"""Cientista do clima - Rodada 2, analise 2: o estado inicial do solo em nov/2026 (SMAP L4) e se ele tem memoria ate a quadra.

A. SMAP L4 (SPL4SMGP v008, 13:30 UTC), Ceara (centros de celula dentro do limite IBGE) e Quixada (2311306):
   percentil da zona da raiz do produto (sm_rootzone_pctl) em 10/11/2026 e media de 01-10/nov; o mesmo recorte de
   01-10/nov em 2015-2025 (posto proprio de 2026 entre 12 novembros); distribuicao espacial do percentil em 10/11/2026.
B. Quanto vale "percentil" num balde vazio: dispersao entre anos da umidade da zona da raiz (m3/m3) em 01-10/nov
   contra a de abril e contra a amplitude sazonal.
C. Memoria: a anomalia de 01-10/nov (ano t-1) persiste ate 01/fev e 19/mar (ano t)? Informa a chuva fev-mai(t) e a
   fracao de municipios em quebra canonica do milho(t)? SMAP: 11 pares (2016-2026) / 10 (2016-2025).
   Prova longa com o GLDAS-2.1 Noah (RootMoist, nov, 2000-2025) e o GLDAS-2.2 CLSM (SoilMoist_RZ, nov, 2003-2025),
   depois de checar se o GLDAS de novembro concorda com o SMAP de novembro. Unidade = ano; Spearman.
Nota: o SMAP L3 ainda esta sendo consolidado (arquivo nao existe agora); aqui so o L4.
So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, DERIV, REF

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import shapely
from scipy import stats

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
rng = np.random.default_rng(1)
QX = "2311306"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"

uf = gpd.read_file(REF / "ceara_uf.geojson").geometry.union_all()
mun = gpd.read_file(REF / "ceara_municipios.geojson")
qx_geom = mun[mun.codarea.astype(str) == QX].geometry.iloc[0]

print("SMAP L3 consolidado existe?", (DADOS / "smap" / "smap_l3_diario_ne.nc").exists())
ds = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
sub = ds[["sm_rootzone", "sm_rootzone_pctl", "sm_surface"]].sel(lat=slice(-2.5, -8.0), lon=slice(-41.5, -37.0)).load()
lat, lon = sub.lat.values, sub.lon.values
LO, LA = np.meshgrid(lon, lat)
m_ce = shapely.contains_xy(uf, LO, LA)
m_qx = shapely.contains_xy(qx_geom, LO, LA)
tempo = pd.DatetimeIndex(sub.time.values)
print(f"SMAP L4: {tempo.min():%Y-%m-%d} -> {tempo.max():%Y-%m-%d}; {len(tempo)} dias; celulas no Ceara {m_ce.sum()}, em Quixada {m_qx.sum()}")


def media(var, msk):
    v = sub[var].values[:, msk]
    return pd.Series(np.nanmean(v, axis=1), index=tempo)


S = {(v, r): media(v, m) for v in ["sm_rootzone", "sm_rootzone_pctl", "sm_surface"] for r, m in [("CE", m_ce), ("QX", m_qx)]}
ult = tempo.max()

print("\n" + "=" * 25, "A. Estado do solo hoje (SMAP L4)", "=" * 25)
for r in ["CE", "QX"]:
    print(f"  {r}: {ult:%d/%m/%Y}: pctl zona da raiz {S[('sm_rootzone_pctl', r)][ult]:.0f} | zona da raiz {S[('sm_rootzone', r)][ult]:.4f} m3/m3 | superficie {S[('sm_surface', r)][ult]:.4f} m3/m3")
nov = {}
for r in ["CE", "QX"]:
    t = pd.DataFrame({a: {v: S[(v, r)].loc[f"{a}-11-01":f"{a}-11-10"].mean() for v in ["sm_rootzone", "sm_rootzone_pctl", "sm_surface"]}
                      for a in range(2015, 2027)}).T
    nov[r] = t
    pos = int((t.sm_rootzone.loc[:2025] < t.sm_rootzone[2026]).sum()) + 1
    print(f"\n  {r}: media de 01-10/nov por ano (posto de 2026 na zona da raiz: {pos} de 12; 1 = mais seco)")
    print(t.round(4).to_string())
# o percentil do produto existe no Ceara nesta epoca?
P = sub["sm_rootzone_pctl"].values[:, m_ce]
nf = pd.Series(np.isnan(P).mean(axis=1), index=tempo)
print("\n  fracao das celulas do Ceara com sm_rootzone_pctl VAZIO (fill), por mes (2015-2026):")
print("   ", {k: round(v, 2) for k, v in nf.groupby(tempo.month).mean().items()})
for a in [2016, 2020, 2025]:
    x = nf[(tempo >= f"{a}-05-01") & (tempo <= f"{a + 1}-04-30")]
    on = x[x > 0.5]
    print(f"    {a}/{a + 1}: vazio em > 50% das celulas de {on.index.min():%d/%m/%Y} a {on.index.max():%d/%m/%Y}")
k = (tempo >= "2026-03-01") & (tempo <= "2026-03-10")
pm, rm = P[k], sub["sm_rootzone"].values[:, m_ce][k]
print(f"    01-10/mar/2026: zona da raiz mediana onde o pctl esta vazio {np.nanmedian(rm[np.isnan(pm)]):.3f} contra {np.nanmedian(rm[~np.isnan(pm)]):.3f} onde existe")
ne = ds[["sm_rootzone", "sm_rootzone_pctl"]].sel(time=ult).load()
terra = ~np.isnan(ne.sm_rootzone.values)
print(f"    Nordeste inteiro em {ult:%d/%m/%Y}: pctl vazio em {np.isnan(ne.sm_rootzone_pctl.values[terra]).mean():.0%} das celulas de terra")
# percentil proprio: posto de 2026 entre os 12 novembros (01-10/nov), celula a celula
R3 = sub["sm_rootzone"].values
mnov = np.stack([np.nanmean(R3[(tempo >= f"{a}-11-01") & (tempo <= f"{a}-11-10")], axis=0) for a in range(2015, 2027)])
posto = (mnov[:-1] < mnov[-1]).sum(axis=0) + 1  # 1..12
pc = posto[m_ce]
print(f"\n  percentil PROPRIO (posto de 01-10/nov/2026 entre 12 novembros 2015-2026), celulas do Ceara: "
      f"tercil seco (posto 1-4) {np.mean(pc <= 4):.0%} | meio (5-8) {np.mean((pc >= 5) & (pc <= 8)):.0%} | umido (9-12) {np.mean(pc >= 9):.0%}")
anom = (mnov[-1] - np.nanmedian(mnov[:-1], axis=0))[m_ce] * 1000
print(f"  anomalia de 2026 contra a mediana 2015-2025 (mm por metro de solo): mediana espacial {np.nanmedian(anom):+.1f}, p10 {np.nanpercentile(anom, 10):+.1f}, p90 {np.nanpercentile(anom, 90):+.1f}")

print("\n" + "=" * 25, "B. Quanto vale o percentil num balde vazio (CE, zona da raiz, m3/m3)", "=" * 25)
rz = S[("sm_rootzone", "CE")]
mens = rz.groupby([rz.index.year, rz.index.month]).mean().unstack()
mens = mens.loc[2016:2025]
print("  media mensal (2016-2025) e dp entre anos, por mes:")
print(pd.DataFrame({"media": mens.mean(), "dp_entre_anos": mens.std(), "min": mens.min(), "max": mens.max()}).round(4).T.to_string())
dn = nov["CE"].sm_rootzone
amp = mens.mean().max() - mens.mean().min()
print(f"  dp entre anos em 01-10/nov: {dn.std():.4f} m3/m3 | dp em abril: {mens[4].std():.4f} | amplitude sazonal media: {amp:.4f}")
print(f"  faixa de 2015-2026 em 01-10/nov: {dn.min():.4f} a {dn.max():.4f} m3/m3 ({(dn.max() - dn.min()) * 1000:.1f} mm por metro de solo)")
print(f"  2026: {dn[2026]:.4f}; diferenca para a mediana dos outros novembros: {(dn[2026] - dn.drop(2026).median()) * 1000:+.1f} mm/m")

print("\n" + "=" * 25, "C. Memoria: novembro(t-1) -> quadra(t)", "=" * 25)


def sp(x, y, nb=2000):
    d = pd.concat([pd.Series(x).rename("x"), pd.Series(y).rename("y")], axis=1).dropna()
    r, pv = stats.spearmanr(d.x, d.y)
    bs = []
    for _ in range(nb):
        i = rng.integers(0, len(d), len(d))
        bs.append(stats.spearmanr(d.x.values[i], d.y.values[i])[0])
    return f"rho={r:+.2f} IC90 [{np.nanpercentile(bs, 5):+.2f},{np.nanpercentile(bs, 95):+.2f}] p={pv:.2f} n={len(d)}"


# persistencia dentro do proprio SMAP (anomalia = valor - media dos outros anos no mesmo dia)
def em(serie, a, md):
    return serie.loc[f"{a}-{md}":f"{a}-{md}"].mean()


xs = {t: em(rz, t - 1, "11-10") for t in range(2016, 2027)}
for nome, md in [("10/dez", None), ("01/fev", "02-01"), ("19/mar", "03-19"), ("30/abr", "04-30")]:
    if md is None:
        ys = {t: em(rz, t - 1, "12-10") for t in range(2016, 2027)}
    else:
        ys = {t: em(rz, t, md) for t in range(2016, 2027)}
    print(f"  SMAP zona da raiz CE: 10/nov(t-1) x {nome}: {sp(xs, ys)}")

# chuva fev-mai do IMERG (media dos 184 municipios) e quebra canonica
ch = pd.read_parquet(A + "saidas/chuva_mun_diaria.parquet")
ch.index = pd.DatetimeIndex(ch.index)
chm = ch.mean(axis=1)
fmam = pd.Series({a: chm.loc[f"{a}-02-01":f"{a}-05-31"].sum() for a in range(1998, 2027)})
fmam_pct = fmam / fmam.loc[:2025].median()
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pp = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
pp = pp[(pp.ano >= 1998) & (pp.ano <= 2025) & (pp.area_plantada_ha >= 50)]
pp = pp.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
pp["r"] = pp.producao_t / pp.area_plantada_ha


def med_outros(g):
    v = g["r"].values
    return pd.Series([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=g.index)


pp["ref"] = pp.groupby("cod_local", group_keys=False).apply(med_outros)
pp = pp.dropna(subset=["ref"])
pp["quebra"] = ((pp.r / pp.ref) < 0.5).astype(int)
frac = pp.groupby("ano").quebra.mean()

smap_nov = {t: nov["CE"].sm_rootzone[t - 1] for t in range(2016, 2027)}
print(f"  SMAP 01-10/nov(t-1) x chuva fev-mai(t): {sp(smap_nov, fmam_pct)}")
print(f"  SMAP 01-10/nov(t-1) x fracao em quebra(t): {sp(smap_nov, frac)}")
pct_nov = {t: nov["CE"].sm_rootzone_pctl[t - 1] for t in range(2016, 2027)}
print(f"  SMAP pctl 01-10/nov(t-1) x fracao em quebra(t): {sp(pct_nov, frac)}")

g1 = pd.read_parquet(DERIV / "gldas_ce_mensal.parquet")
g1 = g1[g1.variavel == "RootMoist_inst"].set_index("data")["valor"]
g2 = pd.read_parquet(DERIV / "gldas_clsm_ce_mensal.parquet")
g2 = g2[g2.variavel == "SoilMoist_RZ_tavg"].set_index("data")["valor"]
for nome, g, a0 in [("GLDAS-2.1 Noah RootMoist", g1, 2000), ("GLDAS-2.2 CLSM SoilMoist_RZ", g2, 2003)]:
    g.index = pd.DatetimeIndex(g.index)
    gn = {a: float(g.get(pd.Timestamp(a, 11, 1), np.nan)) for a in range(a0, 2026)}
    conc = sp({a: gn[a] for a in range(2015, 2026)}, {a: nov["CE"].sm_rootzone[a] for a in range(2015, 2026)})
    print(f"\n  {nome}: novembro concorda com o SMAP de novembro (2015-2025)? {conc}")
    x = {a + 1: gn[a] for a in gn}
    print(f"    nov(t-1) x chuva fev-mai(t): {sp(x, fmam_pct)}")
    print(f"    nov(t-1) x fracao em quebra(t): {sp(x, frac)}")
    gf = {a: float(g.get(pd.Timestamp(a, 2, 1), np.nan)) for a in range(a0 + 1, 2027)}
    print(f"    nov(t-1) x fevereiro(t) do proprio modelo (persistencia): {sp(x, gf)}")
