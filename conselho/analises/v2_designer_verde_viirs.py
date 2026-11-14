"""Designer, rodada 2. O "verde do satelite": VIIRS VNP13A3 NDVI mensal 1 km por municipio.

Perguntas (pre-registradas; sem ajuste de limiar):
  A. O NDVI de fev-mar (publicado ate meados de abril, entao disponivel no portao de 30/abr) e o de abr-mai (fim de safra,
     papel de "testemunha" no replay) separam a quebra canonica do milho? Anomalia = NDVI / mediana dos OUTROS anos do
     mesmo municipio (igual a regra do % do normal). PAREADO com o IMERG % do normal em 30/abr nos MESMOS municipio-anos.
     Unidade independente = ANO (2012-2025, 14 quadras). AUC total, dentro do ano, Spearman entre anos.
  B. Quixada 2012-2025: o satelite "ve" as quebras de 2023-2025 que a chuva nao explica?
  C. Sentinela (M6): o "mais verde para a mesma chuva desde 2020", visto no MODIS Terra, aparece no VIIRS (outro satelite)?
     NDVI mar-mai do CE ~ chuva IMERG jan-mai do CE; ajuste em 2012-2019, residuo medio em 2020-2025.
  D. Frescor: o ultimo mes do arquivo e um composto completo?
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
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
t0 = time.time()
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
rng = np.random.default_rng(0)

pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")


def serie(prefixo):
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        out = np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])
        return pd.Series(out, index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref
    p["quebra"] = (p.razao < 0.5).astype(int)
    p["cod"] = p.cod_local.astype(str).str[:7]
    return p.dropna(subset=["razao"])


mi = serie("Milho (em gr")
nomes = json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))
COD_QXD = str(next(m["id"] for m in nomes if m["nome"].startswith("Quixad")))

vi = xr.open_dataset(DADOS / "viirs" / "vnp13a3_ndvi_evi_ceara_001deg.nc")
print("VIIRS:", dict(vi.sizes), str(vi.time.values[0])[:7], "->", str(vi.time.values[-1])[:7])
print("\n" + "=" * 20, "D. Frescor do ultimo mes", "=" * 20)
for t in vi.time.values[-3:]:
    nv = vi.n_pixels_validos.sel(time=t)
    print(f"  {str(t)[:7]}: fracao de celulas com NDVI valido = {float(vi.ndvi.sel(time=t).notnull().mean()):.3f}; n_pixels_validos medio = {float(nv.where(nv > 0).mean()):.2f}")
tiles = sorted((DADOS / "viirs" / "vnp13a3_tiles").glob("VNP13A3.A2026305*"))
print("  granulos de nov/2026 (A2026305 = 01/11):", [t.name for t in tiles])
print("  o carimbo de producao (2026317 = 13/11) e anterior ao fim de novembro: tratar nov/2026 como provisorio e NAO usar.")

meses = [m for m in pd.to_datetime(vi.time.values) if m.month in (2, 3, 4, 5) and m.year <= 2026]
nd = vi.ndvi.sel(time=meses).load()
nd = nd.where((nd > -0.2) & (nd <= 1))
gm = municipios_ce_gdf()
gm["cod"] = gm.codarea.astype(str)
LON, LAT = np.meshgrid(vi.lon.values, vi.lat.values)
pts = gpd.GeoDataFrame({"i": np.arange(LON.size)}, geometry=gpd.points_from_xy(LON.ravel(), LAT.ravel()), crs=gm.crs)
sj = gpd.sjoin(pts, gm[["cod", "geometry"]], predicate="within", how="inner")
codes = sj.cod.values
idx = sj.i.values
V = nd.values.reshape(len(meses), -1)[:, idx]
dfc = pd.DataFrame(V.T)
dfc["cod"] = codes
mun = dfc.groupby("cod").mean().T  # mes x municipio
mun.index = pd.DatetimeIndex(meses)
print(f"municipios com celulas VIIRS: {mun.shape[1]}; carregado em {time.time()-t0:.0f}s")


def janela(ms):
    s = mun[mun.index.month.isin(ms)]
    return s.groupby(s.index.year).mean()  # ano x mun


def anom(tab):
    out = tab.copy() * np.nan
    for a in tab.index:
        out.loc[a] = tab.loc[a] / tab.drop(index=a).loc[:2025].median()
    return out


FM = anom(janela([2, 3]))
AM = anom(janela([4, 5]))

chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
anos_all = list(range(1998, 2026))
ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-04-30"].sum() for a in anos_all}).T
I30 = ac.copy() * np.nan
for a in anos_all:
    I30.loc[a] = ac.loc[a] / ac.drop(index=a).median()


def longo(t, nome):
    return t.stack().rename(nome).reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})


df = (mi[["cod", "ano", "quebra", "razao"]].merge(longo(FM, "ndvi_fm"), on=["cod", "ano"]).merge(longo(AM, "ndvi_am"), on=["cod", "ano"])
      .merge(longo(I30, "imerg30"), on=["cod", "ano"]).dropna())
df = df[(df.ano >= 2012) & (df.ano <= 2025)]


def auc_dentro(d, col):
    num = den = 0.0
    for a, g in d.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, g[col]); den += w
    return num / den if den else np.nan


def ic(d, col, nboot=400):
    yrs = d.ano.unique()
    g = {a: d[d.ano == a] for a in yrs}
    bs = [roc_auc_score(bb.quebra, bb[col]) for bb in (pd.concat([g[a] for a in rng.choice(yrs, len(yrs))]) for _ in range(nboot)) if bb.quebra.nunique() == 2]
    return np.percentile(bs, 5), np.percentile(bs, 95)


print("\n" + "=" * 20, "A. VIIRS x IMERG, pareado (milho, quebra canonica, 2012-2025)", "=" * 20)
print(f"n = {len(df)} municipio-anos, {df.ano.nunique()} anos; taxa de quebra {df.quebra.mean():.3f}")
an = df.groupby("ano").agg(q=("quebra", "mean"), fm=("ndvi_fm", "mean"), am=("ndvi_am", "mean"), im=("imerg30", "mean"))
for col, rot in [("imerg30", "IMERG % normal ate 30/abr"), ("ndvi_fm", "VIIRS NDVI fev-mar (disponivel em 30/abr)"),
                 ("ndvi_am", "VIIRS NDVI abr-mai (fim de safra, testemunha)")]:
    s = -df[col].clip(upper=3)
    d2 = df.assign(s=s)
    lo, hi = ic(d2, "s")
    print(f"  {rot:45s}: AUC {roc_auc_score(df.quebra, s):.3f} [IC90 ano {lo:.2f}-{hi:.2f}] | dentro do ano {auc_dentro(d2, 's'):.3f} | "
          f"entre anos Spearman {spearmanr(-an[{'imerg30':'im','ndvi_fm':'fm','ndvi_am':'am'}[col]], an.q).correlation:+.2f} (n={len(an)})")
print(f"  r(NDVI fev-mar, IMERG) = {np.corrcoef(df.ndvi_fm, df.imerg30.clip(upper=3))[0,1]:+.2f}; r(NDVI abr-mai, IMERG) = {np.corrcoef(df.ndvi_am, df.imerg30.clip(upper=3))[0,1]:+.2f}")
# frequencias naturais com faixa fixada a priori: NDVI abaixo de 90% do normal do municipio
for col in ["ndvi_fm", "ndvi_am"]:
    b = df[col] < 0.90
    print(f"  {col} < 90% do normal: {10*df.quebra[b].mean():.1f} em 10 quebraram (n={b.sum()}, anos {df.ano[b].nunique()}); "
          f">= 90%: {10*df.quebra[~b].mean():.1f} em 10 (n={(~b).sum()})")
print("  ano a ano (estado):")
print(an.round(2).to_string())

print("\n" + "=" * 20, "B. Quixada: o satelite ve 2023-2025?", "=" * 20)
q = df[df.cod == COD_QXD].set_index("ano")[["razao", "quebra", "imerg30", "ndvi_fm", "ndvi_am"]].round(2)
print(q.to_string())
print("  (NDVI em fracao do normal do municipio; < 0,90 = mais seco que o normal)")

print("\n" + "=" * 20, "C. Sentinela: mais verde para a mesma chuva desde 2020? (CE, VIIRS)", "=" * 20)
mm = mun.mean(axis=1)
nd_mam = mm[mm.index.month.isin([3, 4, 5])].groupby(mm[mm.index.month.isin([3, 4, 5])].index.year).mean()
ch = chuva.mean(axis=1)
r_jm = pd.Series({a: ch.loc[f"{a}-01-01":f"{a}-05-31"].sum() for a in range(2012, 2026)})
J = pd.DataFrame({"ndvi": nd_mam.loc[2012:2025], "chuva": r_jm}).dropna()
tr = J.loc[:2019]
b1, b0 = np.polyfit(tr.chuva, tr.ndvi, 1)
J["residuo"] = J.ndvi - (b0 + b1 * J.chuva)
print(J.round(3).to_string())
print(f"  ajuste 2012-2019: NDVI = {b0:.3f} + {b1*100:.4f} x chuva/100 mm; residuo medio 2020-2025 = {J.residuo.loc[2020:].mean():+.3f} "
      f"(dp dos residuos 2012-2019 = {J.residuo.loc[:2019].std():.3f}; n = 8 e 6 anos)")
mod = pd.read_parquet(D + "modis_ce_mensal.parquet")
mod = mod[mod.variavel == "ndvi"].set_index("data")["valor"]
mod.index = pd.to_datetime(mod.index)
mo = mod[mod.index.month.isin([3, 4, 5])]
mo = mo.groupby(mo.index.year).mean().reindex(J.index)
if mo.notna().sum() >= 10:
    trm = pd.DataFrame({"n": mo, "c": J.chuva}).dropna()
    c1, c0 = np.polyfit(trm.loc[:2019].c, trm.loc[:2019].n, 1)
    resm = trm.n - (c0 + c1 * trm.c)
    print(f"  mesmo teste com MODIS (mesma janela 2012-2025): residuo medio 2020-2025 = {resm.loc[2020:].mean():+.3f} (dp 2012-2019 = {resm.loc[:2019].std():.3f})")
print(f"\ntempo total {time.time()-t0:.0f}s")
