"""v3 - Especialista sensoriamento/hidrologia - Teste 3 (GRACE e conferencias rapidas dos grupos 2 e 3).

 a) Lima et al. 2020 (Bol Cienc Geod 26(3) e2020013): Spearman TWS (GRACE CSR RL06 mascon) x SPI-12/24/36 = 0,57/0,73/0,72;
    TWS x NDVI (MODIS) = 0,77; "377 GRACE RL06 Mascon grids, from April 2002 to June 2017". Regiao NAEHR (PI a AL).
    Proxy aqui: media do CE (o CE tem 64,93% da capacidade dos reservatorios da NAEHR, Tab. 2 do proprio artigo).
 b) Goncalves et al. 2020 (STOTEN; o guia diz 2019): depleção de TWS no Sistema Aquifero Urucuia 6,5 +- 2,6 mm/ano (2002-2014).
    CAIXA APROXIMADA (nao e o poligono do aquifero): lon -46,5 a -44,5, lat -15,5 a -10,5.
 c) Melati et al. 2019 (Hydrogeol J 27:2789): Sistema Aquifero Medio do Araripe, afloramento de 1.394 km2, ~84 milhoes m3/ano
    bombeados; 7 de 12 pocos (58%) com NS > 0,50. Sem pocos aqui: so o sinal GRACE - GLDAS e a escala detectavel.
 d) Alvala et al. 2019 (o guia diz 2017): ano hidrologico 2015-16 foi o 2o mais seco depois de 2012-13 (ultimos 6 anos).
 e) Medeiros et al. 2022: sitio SD (Estacao Ecologica do Serido) "Serra Negra do Norte, Paraiba", 6 34'42"S 37 15'05"W.
"""
import sys
import time

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import json
import warnings

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from shapely.geometry import shape, Point

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
T0 = time.time()


def secao(t):
    print("\n" + "=" * 100 + f"\n{t}  [{time.time()-T0:.0f}s]\n" + "=" * 100)


def tendencia(s):
    s = s.dropna()
    x = (s.index - s.index[0]).days.values / 365.25
    r = stats.linregress(x, s.values)
    return r.slope, r.stderr, len(s)


# ---------------------------------------------------------------- (a) Lima 2020
secao("(a) Lima 2020 - GRACE CSR (media CE) x SPI-12/24/36 (IMERG CE) e NDVI (MODIS CE)")
gr = pd.read_parquet(DERIV / "grace_ce_mensal.parquet").set_index("data")["valor"]
gr.index = pd.to_datetime(gr.index).to_period("M").to_timestamp()
print(f"   meses GRACE/GRACE-FO no arquivo entre 2002-04 e 2017-06: {len(gr.loc['2002-04-01':'2017-06-01'])} "
      "(o artigo diz 377 grades nesse periodo, que so tem 183 meses de calendario)")
im = pd.read_parquet(DERIV / "imerg_ce_mensal.parquet")
p = im[im.variavel == "precip_total"].set_index("data")["valor"]
p.index = pd.to_datetime(p.index)


def spi(s, k):
    a = s.rolling(k).sum()
    out = pd.Series(index=a.index, dtype=float)
    for m in range(1, 13):
        x = a[(a.index.month == m)].dropna()
        sh, loc, sc = stats.gamma.fit(x, floc=0)
        out[x.index] = stats.norm.ppf(np.clip(stats.gamma.cdf(x, sh, loc=0, scale=sc), 1e-3, 1 - 1e-3))
    return out


for per in [("2002-04-01", "2017-06-01"), ("2002-04-01", "2026-08-01")]:
    linha = []
    for k in [12, 24, 36]:
        j = pd.concat([gr, spi(p, k)], axis=1).dropna().loc[per[0]:per[1]]
        linha.append(f"SPI-{k}: rho={stats.spearmanr(j.iloc[:,0], j.iloc[:,1]).statistic:+.2f} (n={len(j)})")
    print(f"   {per[0][:7]}..{per[1][:7]}  " + "  ".join(linha) + ("   | artigo: 0,57 / 0,73 / 0,72" if per[1] < "2018" else ""))
mod = pd.read_parquet(DERIV / "modis_ce_mensal.parquet")
nd = mod[mod.variavel == "ndvi"].set_index("data")["valor"]
nd.index = pd.to_datetime(nd.index)
ga = gr.groupby(gr.index.year).mean(); na = nd.groupby(nd.index.year).mean()
j = pd.concat([ga, na], axis=1).dropna().loc[2003:2017]
print(f"   TWS anual x NDVI anual 2003-2017: rho={stats.spearmanr(j.iloc[:,0], j.iloc[:,1]).statistic:+.2f} (n={len(j)}) | artigo 0,77")
j = pd.concat([ga, na], axis=1).dropna().loc[2003:2025]
print(f"   TWS anual x NDVI anual 2003-2025: rho={stats.spearmanr(j.iloc[:,0], j.iloc[:,1]).statistic:+.2f} (n={len(j)})")
for per in [("2002-04-01", "2017-06-01"), ("2011-01-01", "2017-12-01"), ("2018-01-01", "2026-09-01"), ("2002-04-01", "2026-09-01")]:
    b, e, n = tendencia(gr.loc[per[0]:per[1]])
    print(f"   tendencia TWS CE {per[0][:7]}..{per[1][:7]}: {10*b:+.1f} +- {10*e:.1f} mm/ano (n={n})")

# ---------------------------------------------------------------- (b) Goncalves Urucuia
secao("(b) Goncalves 2020 - tendencia de TWS no Urucuia (caixa aproximada) - artigo: -6,5 +- 2,6 mm/ano 2002-2014")
g = xr.open_dataset(DADOS / "grace" / "grace_ne_mensal.nc")["lwe_thickness"]
cx = g.sel(lon=slice(-46.5, -44.5), lat=slice(-15.5, -10.5))
w = np.cos(np.radians(cx.lat))
s = (cx.weighted(w).mean(("lat", "lon")) * 10).to_series()
s.index = pd.to_datetime(s.index)
for per in [("2002-04-01", "2014-12-31"), ("2002-04-01", "2017-06-30"), ("2018-06-01", "2026-09-30"), ("2002-04-01", "2026-09-30")]:
    b, e, n = tendencia(s.loc[per[0]:per[1]])
    print(f"   {per[0][:7]}..{per[1][:7]}: {b:+.1f} +- {e:.1f} mm/ano (n={n}, erro padrao OLS sem autocorrelacao)")

# ---------------------------------------------------------------- (c) Melati Araripe
secao("(c) Melati 2019 - Araripe: GRACE - GLDAS Noah (proxy de agua subterranea) e escala detectavel")
lon0, lat0 = -39.6, -7.4  # centro aproximado da Chapada do Araripe
tws = (g.sel(lon=lon0, lat=lat0, method="nearest") * 10).to_series()
tws.index = pd.to_datetime(tws.index).to_period("M").to_timestamp()
gl = xr.open_dataset(DADOS / "gldas" / "gldas_noah025_mensal_ne.nc").sel(lon=lon0, lat=lat0, method="nearest")
sm = (gl["SoilMoi0_10cm_inst"] + gl["SoilMoi10_40cm_inst"] + gl["SoilMoi40_100cm_inst"] + gl["SoilMoi100_200cm_inst"]).to_series()
sm.index = pd.to_datetime(sm.index)
base = slice("2004-01-01", "2009-12-31")
gws = (tws - tws.loc[base].mean()) - (sm - sm.loc[base].mean())
cl = xr.open_dataset(DADOS / "gldas" / "gldas_clsm025_diario_ne.nc")["GWS_tavg"].sel(lon=lon0, lat=lat0, method="nearest").to_series()
cl = cl.resample("MS").mean()
for nome, ser in [("TWS GRACE", tws), ("solo 0-200 cm Noah", sm), ("GWS = TWS - solo (Noah)", gws), ("GWS CLSM 2.2 (assimila GRACE)", cl)]:
    b, e, n = tendencia(ser.loc["2010-01-01":"2017-12-31"])
    print(f"   {nome:32s} 2010-2017: {b:+.1f} +- {e:.1f} mm/ano (n={n})")
vol = 84e6
for nome, area in [("afloramento 1.394 km2", 1394e6), ("1 grau x 1 grau a 7,4 S", 110.6e3 * 110.6e3 * np.cos(np.radians(7.4))),
                   ("pegada efetiva GRACE ~300 km x 300 km", 300e3 * 300e3)]:
    print(f"   bombeamento 84 milhoes m3/ano espalhado em {nome}: {1000*vol/area:.1f} mm/ano")

# ---------------------------------------------------------------- (d) Alvala anos hidrologicos
secao("(d) Alvala 2019 - chuva do ano hidrologico out-set (IMERG CE)")
hy = {}
for a in range(1999, 2026):
    jn = p.loc[f"{a-1}-10-01":f"{a}-09-01"]
    if len(jn) == 12:
        hy[f"{a-1}-{a}"] = jn.sum()
hy = pd.Series(hy)
ult6 = hy.loc["2010-2011":"2015-2016"]
print("   ultimos 6 anos hidrologicos do artigo (IMERG CE, mm):", ult6.round(0).to_dict())
print("   ordem do mais seco ao mais umido:", list(ult6.sort_values().index))
print(f"   media 1998/99-2024/25 = {hy.mean():.0f} mm")

# ---------------------------------------------------------------- (e) Medeiros sitio SD
secao("(e) Medeiros 2022 - em que UF cai o sitio SD (6 34'42\"S, 37 15'05\"W)?")
ufs = json.load(open(REF / "nordeste_ufs.geojson", encoding="utf-8"))
NOME = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
for rot, (la, lo) in {"SD Serido": (-(6 + 34 / 60 + 42 / 3600), -(37 + 15 / 60 + 5 / 3600)),
                      "MSD Petrolina": (-(9 + 2 / 60 + 47 / 3600), -(40 + 19 / 60 + 16 / 3600)),
                      "BP Campina Grande": (-(7 + 16 / 60 + 49 / 3600), -(35 + 58 / 60 + 34 / 3600))}.items():
    pt = Point(lo, la)
    ach = [NOME.get(f["properties"]["codarea"], f["properties"]["codarea"]) for f in ufs["features"] if shape(f["geometry"]).contains(pt)]
    print(f"   {rot:18s} ({la:.4f}, {lo:.4f}) -> UF {ach}")

# ---------------------------------------------------------------- (f) Barbosa 2019: NDVI x chuva defasada 3 meses
secao("(f) Barbosa 2019 (SEVIRI NDVI; resumo: R2 = 0,62 com chuva defasada 3 meses) - MODIS NDVI x IMERG, media do CE")
ndm = nd.copy(); ndm.index = ndm.index.to_period("M").to_timestamp()
pmm = p.copy(); pmm.index = pmm.index.to_period("M").to_timestamp()
for rot, x in [("chuva do mes", pmm), ("soma 3 meses (t-2..t)", pmm.rolling(3).sum())]:
    linha = []
    for k in range(0, 4):
        j = pd.concat([ndm, x.shift(k)], axis=1).dropna().loc["2008-01-01":"2016-12-01"]
        linha.append(f"lag {k}: R2={j.corr().iloc[0,1]**2:.2f}")
    print(f"   NDVI bruto x {rot:22s} 2008-2016: " + "  ".join(linha))
za = lambda s: (s - s.groupby(s.index.month).transform("mean")) / s.groupby(s.index.month).transform("std")
for k in range(0, 4):
    j = pd.concat([za(ndm), za(pmm.rolling(3).sum()).shift(k)], axis=1).dropna().loc["2008-01-01":"2016-12-01"]
    print(f"   anomalias (sem ciclo anual) NDVI x soma 3 meses, lag {k}: R2={j.corr().iloc[0,1]**2:.2f} (n={len(j)})")

print(f"\nTempo total: {time.time()-T0:.0f} s")
