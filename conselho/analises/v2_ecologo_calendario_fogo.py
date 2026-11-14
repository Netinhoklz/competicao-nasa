"""Ecologo (rodada 2, dados novos) - Analise 2: o fogo da entressafra segue a SECURA ou o CALENDARIO?
(reavaliacao do portao de entressafra: quando o tecnico deve falar de aceiro e de palhada em vez de fogo)

Pergunta pre-especificada: num municipio, nos anos em que o solo seca mais cedo (SMAP L4) ou a chuva acaba mais cedo
(IMERG), o fogo tambem chega mais cedo? Se sim, o portao pode ser disparado pelo SMAP; se nao, o fogo e de pratica
(broca e queima antes do plantio) e o portao deve ter data fixa.
Definicoes (municipio-ano, 2015-2025; janela do fogo 1/jul-31/dez; >= 20 focos FIRMS type 0 n/h na janela):
  fogo_p10, fogo_p50 = dia do ano em que o acumulado de focos de jul-dez chega a 10% e 50%;
  seca_smap = 1o dia >= 1/mai em que a media de 7 dias de sm_rootzone (SMAP L4) fica <= mediana de set-nov
              daquele municipio em 2015-2025 ("chegou ao nivel tipico da seca");
  fim_chuva = dia em que a chuva IMERG acumulada desde 1/jan atinge 95% do total de jan-jul.
Teste: anomalias dentro do municipio (menos a media do municipio); inclinacao por MQO com EP agrupado por ano;
rho de Spearman entre anos com as medias estaduais (n = 11). Unidade independente = ano.
Extra descritivo: classe de cobertura ESA CCI 2020 (300 m) sob os focos de out-dez.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.api as sm
import xarray as xr
from scipy import stats

AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
mun = gpd.read_file(REF / "ceara_municipios.geojson").to_crs(4326)
mun["codarea"] = mun.codarea.astype(str)
cods = mun.codarea.values
idx_cod = {c: i for i, c in enumerate(cods)}

# ---------- FIRMS diario por municipio ----------
v = pd.read_parquet(DADOS / "viirs" / "firms_viirs_snpp_nordeste.parquet",
                    columns=["latitude", "longitude", "acq_date", "type", "uf", "confidence"])
v = v[(v.uf == 23) & (v["type"] == 0) & (v.confidence.astype(str).str.lower().isin(["n", "h"]))].copy()
pts = gpd.sjoin(gpd.GeoDataFrame(v, geometry=gpd.points_from_xy(v.longitude, v.latitude), crs=4326),
                mun[["codarea", "geometry"]], predicate="within")
pts["data"] = pd.to_datetime(pts.acq_date)
pts["ano"] = pts.data.dt.year
pts["doy"] = pts.data.dt.dayofyear

# ---------- SMAP L4 diario por municipio (zona da raiz) ----------
sd = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc").sel(lat=slice(-2.4, -8.1), lon=slice(-41.6, -36.9))
LA, LO = np.meshgrid(sd.lat.values, sd.lon.values, indexing="ij")
g = gpd.sjoin(gpd.GeoDataFrame(geometry=gpd.points_from_xy(LO.ravel(), LA.ravel()), crs=4326),
              mun[["codarea", "geometry"]], predicate="within")
lab = np.full(LA.size, -1)
lab[g.index.values] = g.codarea.map(idx_cod).values
rz = sd.sm_rootzone.values.reshape(sd.sizes["time"], -1)
m = lab >= 0
L = lab[m]
cnt = np.bincount(L, minlength=len(cods))
daily = np.vstack([np.bincount(L, weights=np.nan_to_num(r[m]), minlength=len(cods)) / np.maximum(cnt, 1) for r in rz])
rzm = pd.DataFrame(daily, index=pd.to_datetime(sd.time.values), columns=cods)
dup = rzm.index[rzm.index.duplicated()]
print(f"SMAP L4: {len(dup)} datas duplicadas no arquivo consolidado ({', '.join(d.strftime('%Y-%m-%d') for d in dup)}); media por data")
rzm = rzm.groupby(level=0).mean().asfreq("D")  # dias sem granulo ficam NaN
rz7 = rzm.rolling(7, min_periods=4).mean()
nivel = rzm[(rzm.index.month.isin([9, 10, 11])) & (rzm.index.year <= 2025)].median()

# ---------- IMERG municipal ----------
ch = pd.read_parquet(AN / "saidas" / "chuva_mun_diaria.parquet")
ch.index = pd.to_datetime(ch.index)

lin = []
for y in range(2015, 2026):
    py = pts[(pts.ano == y) & (pts.data.dt.month >= 7)]
    r7 = rz7.loc[f"{y}-05-01":f"{y}-12-31"]
    cy = ch.loc[f"{y}-01-01":f"{y}-07-31"]
    cum = cy.cumsum() / cy.sum()
    for c in cods:
        d = np.sort(py.doy[py.codarea == c].values)
        if len(d) < 20:
            continue
        abaixo = r7[c] <= nivel[c]
        seca = abaixo.idxmax().dayofyear if abaixo.any() else np.nan
        fim = cum[c].ge(0.95).idxmax().dayofyear
        lin.append({"codarea": c, "ano": y, "n": len(d), "p10": np.percentile(d, 10), "p50": np.percentile(d, 50),
                    "seca_smap": seca, "fim_chuva": fim})
T = pd.DataFrame(lin).dropna()
print(f"Municipio-anos com >= 20 focos em jul-dez e as tres datas: {len(T)} ({T.codarea.nunique()} municipios, 2015-2025)")
fmt = lambda x: (pd.Timestamp("2021-01-01") + pd.Timedelta(days=float(x) - 1)).strftime("%d/%m")
for c in ("p10", "p50", "seca_smap", "fim_chuva"):
    q = T[c].quantile([0.25, 0.5, 0.75]).values
    an = T[c] - T.groupby("codarea")[c].transform("mean")
    print(f"  {c:9s}: mediana {fmt(q[1])} (IQR {fmt(q[0])}-{fmt(q[2])}); dp entre anos dentro do municipio = {an.std():.1f} dias")

for c in ("p10", "p50", "seca_smap", "fim_chuva"):
    T[c + "_a"] = T[c] - T.groupby("codarea")[c].transform("mean")
print("\nO fogo anda junto com a secura? (anomalias dentro do municipio; EP agrupado por ano, 11 grupos)")
for alvo in ("p10_a", "p50_a"):
    for X in (["seca_smap_a"], ["fim_chuva_a"], ["seca_smap_a", "fim_chuva_a"]):
        mm = sm.OLS(T[alvo], sm.add_constant(T[X])).fit(cov_type="cluster", cov_kwds={"groups": T.ano})
        rho = stats.spearmanr(T[alvo], T[X[0]])[0]
        print(f"  {alvo} ~ {' + '.join(X):26s}: " + " | ".join(f"{x} {mm.params[x]:+.3f} dia/dia (IC95 {mm.conf_int().loc[x, 0]:+.3f} a {mm.conf_int().loc[x, 1]:+.3f})" for x in X)
              + f" | rho pooled com {X[0]} {rho:+.3f}")
ea = T.groupby("ano")[["p10", "p50", "seca_smap", "fim_chuva", "n"]].mean()
print("\nMedias estaduais por ano (dia do ano):")
print(ea.assign(p10=ea.p10.map(fmt), p50=ea.p50.map(fmt), seca_smap=ea.seca_smap.map(fmt), fim_chuva=ea.fim_chuva.map(fmt)).to_string())
for c in ("seca_smap", "fim_chuva"):
    for a in ("p10", "p50"):
        r, p = stats.spearmanr(ea[a], ea[c])
        print(f"  entre anos (n=11): rho({a}, {c}) = {r:+.2f} (p={p:.2f})")

# ---------- quando o fogo acontece: fracao mensal ----------
fm = pts[pts.ano.between(2015, 2025)].groupby(pts.data.dt.month).size()
print("\nFracao dos focos do ano por mes (2015-2025):", ", ".join(f"{k}: {v / fm.sum() * 100:.1f}%" for k, v in fm.items()))
cum = (fm.cumsum() / fm.sum())
print("  acumulado ate 31/ago: %.0f%%; ate 30/set: %.0f%%" % (cum.loc[8] * 100, cum.loc[9] * 100))

# ---------- cobertura sob os focos de out-dez (ESA CCI 2020 300 m) ----------
lc = xr.open_dataset(DADOS / "modis" / "esa_cci_lc_2020_nordeste_300m.nc")
lat, lon = lc.lat.values, lc.lon.values
od = pts[pts.data.dt.month.isin([10, 11, 12]) & pts.ano.between(2015, 2025)]
ii = np.clip(np.round((lat[0] - od.latitude.values) / abs(lat[1] - lat[0])).astype(int), 0, len(lat) - 1)
jj = np.clip(np.round((od.longitude.values - lon[0]) / abs(lon[1] - lon[0])).astype(int), 0, len(lon) - 1)
cls = lc.lccs_class.values[ii, jj]
grupo = pd.Series(np.select([np.isin(cls, [10, 11, 12, 20]), np.isin(cls, [30, 40]), np.isin(cls, [120, 121, 122, 130]),
                             np.isin(cls, [50, 60, 61, 62, 70, 80, 90, 100])],
                            ["lavoura", "mosaico lavoura/natural", "arbustiva/campo", "floresta/arborea"], "outra"))
# cobertura do estado inteiro, para comparar (pixels 300 m no CE)
uf = gpd.read_file(REF / "ceara_uf.geojson").to_crs(4326).union_all()
from shapely import contains_xy
sl = (lat >= -8) & (lat <= -2.5)
sc = (lon >= -41.5) & (lon <= -37)
LA2, LO2 = np.meshgrid(lat[sl][::3], lon[sc][::3], indexing="ij")
dentro = contains_xy(uf, LO2.ravel(), LA2.ravel())
cl_ce = lc.lccs_class.values[np.ix_(np.where(sl)[0][::3], np.where(sc)[0][::3])].ravel()[dentro]
g_ce = pd.Series(np.select([np.isin(cl_ce, [10, 11, 12, 20]), np.isin(cl_ce, [30, 40]), np.isin(cl_ce, [120, 121, 122, 130]),
                            np.isin(cl_ce, [50, 60, 61, 62, 70, 80, 90, 100])],
                           ["lavoura", "mosaico lavoura/natural", "arbustiva/campo", "floresta/arborea"], "outra"))
tab = pd.DataFrame({"focos_out_dez_%": grupo.value_counts(normalize=True) * 100,
                    "area_CE_%": g_ce.value_counts(normalize=True) * 100}).round(1)
tab["razao"] = (tab["focos_out_dez_%"] / tab["area_CE_%"]).round(2)
print(f"\nCobertura ESA CCI 2020 sob {len(od)} focos de out-dez (2015-2025) x area do Ceara (amostra 1 em 9 pixels):")
print(tab.to_string())
