"""Designer, rodada 2. O "banco lento": agua subterranea do GLDAS-2.2 CLSM (que ASSIMILA o GRACE) para a tela do tecnico.

Perguntas (pre-registradas):
  A. Hoje: em que percentil esta a agua subterranea (GWS) e o armazenamento total (TWS) em jun-ago/2026, dessazonalizados,
     contra jun-ago de 2003-2025, em Quixada (celula 0,25 graus) e no CE? Bate com a mensagem "banco regional normal" (GRACE p57)?
  B. O banco lento de jun-ago do ano t-1 diz algo sobre a quadra do ano t (fracao de municipios em quebra do milho,
     chuva IMERG jan-mai do CE, razao do milho em Quixada)? Unidade = ano (2004-2025, n = 22). Se nao diz, ele nao entra
     no cartao da familia como sinal de safra.
  C. Quanto tempo o banco levou para voltar depois de 2012-2016 (Quixada e CE)? E a frase de "memoria" para a tela.
So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import json
import time

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy.stats import spearmanr

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
t0 = time.time()
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"

gc = xr.open_dataset(DADOS / "gldas" / "gldas_clsm025_diario_ne.nc")
gc = gc.sel(lat=slice(-8.0, -2.5), lon=slice(-41.5, -37.0))[["GWS_tavg", "TWS_tavg"]].load()
gc = gc.where(gc > -9000)
mens = gc.resample(time="MS").mean()
print(f"GLDAS CLSM CE: {dict(gc.sizes)}; {str(gc.time.values[0])[:10]} -> {str(gc.time.values[-1])[:10]}; {time.time()-t0:.0f}s")

ce = ceara_gdf()
LON, LAT = np.meshgrid(mens.lon.values, mens.lat.values)
pts = gpd.GeoDataFrame({"i": np.arange(LON.size)}, geometry=gpd.points_from_xy(LON.ravel(), LAT.ravel()), crs=ce.crs)
dentro = gpd.sjoin(pts, ce[["geometry"]], predicate="within", how="inner").i.values
lo_q, la_q = AOIS["sertao_central"][0], AOIS["sertao_central"][1]
iq = int(np.argmin((LON.ravel() - lo_q) ** 2 + (LAT.ravel() - la_q) ** 2))
print(f"celulas no CE: {len(dentro)}; celula de Quixada: lon {LON.ravel()[iq]:.3f}, lat {LAT.ravel()[iq]:.3f}")


def serie(var, ix):
    v = mens[var].values.reshape(mens.sizes["time"], -1)[:, ix]
    s = pd.Series(np.nanmean(v, axis=1) if v.ndim > 1 else v, index=pd.to_datetime(mens.time.values)) / 10.0  # mm -> cm
    return s


S = {"GWS_Quixada": serie("GWS_tavg", np.array([iq])), "GWS_CE": serie("GWS_tavg", dentro),
     "TWS_Quixada": serie("TWS_tavg", np.array([iq])), "TWS_CE": serie("TWS_tavg", dentro)}
S = pd.DataFrame(S)
dz = S - S.groupby(S.index.month).transform(lambda x: x.loc[:"2025"].mean() if False else x.mean())
print("ultimo mes:", S.index.max().date())

print("\n" + "=" * 20, "A. Hoje: jun-ago/2026, dessazonalizado, contra jun-ago 2003-2025", "=" * 20)
jja = dz[dz.index.month.isin([6, 7, 8])]
jja = jja.groupby(jja.index.year).mean()
for c in S.columns:
    h = jja[c].loc[2003:2025].dropna()
    v = jja[c].loc[2026]
    print(f"  {c:12s}: anomalia jun-ago/2026 = {v:+.2f} cm; percentil entre {len(h)} anos = p{100*np.mean(h < v):.0f}; "
          f"faixa {h.min():+.1f} a {h.max():+.1f} cm")
gr = pd.read_parquet(D + "grace_ce_mensal.parquet").set_index("data")["valor"]
gr.index = pd.to_datetime(gr.index)
grz = gr - gr.groupby(gr.index.month).transform("mean")
gj = grz[grz.index.month.isin([6, 7, 8])]
gj = gj.groupby(gj.index.year).mean()
print(f"  GRACE CE (mesma conta, jun-ago): {gj.loc[2026]:+.2f} cm, p{100*np.mean(gj.loc[2003:2025].dropna() < gj.loc[2026]):.0f} "
      f"(a proposta usa jul-set = p57; aqui e jun-ago para casar com o GLDAS, que vai ate ago)")
print("  r mensal das anomalias, 2003-2026: TWS_CE x GRACE = "
      f"{pd.concat([dz.TWS_CE, grz], axis=1).dropna().corr().iloc[0,1]:.2f}; GWS_Quixada x GWS_CE = {dz[['GWS_Quixada','GWS_CE']].corr().iloc[0,1]:.2f}")

print("\n" + "=" * 20, "B. O banco de jun-ago(t-1) diz algo sobre a quadra de t? (n = anos)", "=" * 20)
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha


def med_outros(g):
    v = g["r"].values
    return pd.Series([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=g.index)


p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
p["razao"] = p.r / p.ref
p = p.dropna(subset=["razao"])
p["cod"] = p.cod_local.astype(str).str[:7]
fq = p.groupby("ano").apply(lambda g: (g.razao < 0.5).mean())
nomes = json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))
cq = str(next(m["id"] for m in nomes if m["nome"].startswith("Quixad")))
rq = p[p.cod == cq].set_index("ano").razao
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chm = chuva.mean(axis=1)
cjm = pd.Series({a: chm.loc[f"{a}-01-01":f"{a}-05-31"].sum() for a in range(1998, 2026)})
B = pd.DataFrame({"gws_ce_t1": jja.GWS_CE.shift(1, freq=None), "gws_qxd_t1": jja.GWS_Quixada}).copy()
B = pd.DataFrame({"gws_ce_t1": jja.GWS_CE, "gws_qxd_t1": jja.GWS_Quixada})
B.index = B.index + 1  # banco de jun-ago do ano anterior
B = B.join(pd.DataFrame({"frac_quebra": fq, "chuva_jan_mai": cjm, "razao_qxd": rq}), how="inner").loc[2004:2025]
print(f"  n = {len(B)} anos ({B.index.min()}-{B.index.max()})")
for x in ["gws_ce_t1", "gws_qxd_t1"]:
    for y in ["frac_quebra", "chuva_jan_mai", "razao_qxd"]:
        d = B[[x, y]].dropna()
        r = spearmanr(d[x], d[y]).correlation
        print(f"    Spearman {x} x {y}: {r:+.2f} (n={len(d)})")
# sem o bloco 2012-2017 (o episodio domina)
d = B.drop(index=range(2012, 2018), errors="ignore")
print(f"    sem 2012-2017: Spearman gws_ce_t1 x frac_quebra = {spearmanr(d.gws_ce_t1, d.frac_quebra).correlation:+.2f}; "
      f"x chuva_jan_mai = {spearmanr(d.gws_ce_t1, d.chuva_jan_mai).correlation:+.2f} (n={len(d)})")
print("    tercis do banco (CE) e a quebra do ano seguinte, em frequencia natural:")
B["terc"] = pd.qcut(B.gws_ce_t1, 3, labels=["baixo", "medio", "alto"])
for t, g in B.groupby("terc"):
    print(f"      banco {t:5s} (n={len(g)} anos: {list(g.index)}): fracao media de municipios em quebra = {g.frac_quebra.mean():.2f}; "
          f"anos com >= 50% em quebra: {int((g.frac_quebra >= 0.5).sum())}")

print("\n" + "=" * 20, "C. Memoria: recuperacao depois de 2012-2016", "=" * 20)
for c in ["GWS_Quixada", "GWS_CE"]:
    s3 = dz[c].rolling(3).mean()
    imin = s3.loc["2012":"2018"].idxmin()
    rec = s3.loc[imin:]
    volta = rec[rec >= 0].index.min()
    print(f"  {c}: minimo (media movel 3 meses) {s3[imin]:+.1f} cm em {imin:%Y-%m}; volta ao normal (>= 0) em {volta:%Y-%m} "
          f"-> {(volta.year - imin.year) * 12 + volta.month - imin.month} meses")
    ac = {k: round(float(dz[c].autocorr(k)), 2) for k in (1, 3, 6, 12, 24)}
    print(f"    autocorrelacao da anomalia mensal: {ac}")
print("  ultimos 6 meses (anomalia dessazonalizada, cm):")
print(dz.tail(6).round(2).to_string())
print(f"\ntempo total {time.time()-t0:.0f}s")
