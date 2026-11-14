"""Ecologo de pragas - Analise 4 (rapida): "pontes verdes" da entressafra no Ceara.

Pergunta: onde a paisagem continua verde no auge seco (out), mantendo hospedeiro para a lagarta-do-cartucho e outras
pragas entre uma quadra e a seguinte? (No CE o relogio termico nao para; ver ecologo_grausdia_geracoes.py.)
Metodo: NDVI MODIS mensal a 0,01 grau (dados/modis/mod13q1_ndvi_mensal_001deg.nc), mediana de outubro 2001-2024 por
pixel; classe ESA CCI 2020 do pixel; "ponte verde" = NDVI de outubro >= 0,55 em pixel de lavoura/mosaico (o NDVI
estadual de outubro e ~0,37, secao 09). Agregado por municipio (malha IBGE).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

nd = xr.open_dataset(DADOS / "modis" / "mod13q1_ndvi_mensal_001deg.nc")
var = [k for k in nd.data_vars][0]
x = nd[var]
out = x.sel(time=(x.time.dt.month == 10) & (x.time.dt.year <= 2024)).median("time").load()
abr = x.sel(time=(x.time.dt.month == 4) & (x.time.dt.year <= 2024)).median("time").load()
LA, LO = np.meshgrid(out.lat.values, out.lon.values, indexing="ij")
lc = xr.open_dataset(DADOS / "modis" / "esa_cci_lc_2020_nordeste_300m.nc")
lcv = lc.lccs_class.values
la0, lo0 = float(lc.lat[0]), float(lc.lon[0])
r = abs(float(lc.lat[1] - lc.lat[0]))
ii = np.clip(np.round((la0 - LA) / r).astype(int), 0, lcv.shape[0] - 1)
jj = np.clip(np.round((LO - lo0) / r).astype(int), 0, lcv.shape[1] - 1)
cls = lcv[ii, jj]
df = pd.DataFrame({"lat": LA.ravel(), "lon": LO.ravel(), "ndvi_out": out.values.ravel(), "ndvi_abr": abr.values.ravel(),
                   "cls": cls.ravel()}).dropna()
mun = gpd.read_file(DADOS / "referencia" / "ceara_municipios.geojson")
import json
nomes = {str(d["id"]): d["nome"] for d in json.loads((DADOS / "referencia" / "ceara_municipios_nomes.json").read_text(encoding="utf-8"))}
pts = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326)
pts = gpd.sjoin(pts, mun[["codarea", "geometry"]], predicate="within").drop(columns="index_right")
agri = pts.cls.isin([10, 11, 12, 20, 30, 40])
pts["ponte"] = agri & (pts.ndvi_out >= 0.55)
print(f"Pixels 1 km no CE: {len(pts):,}; de lavoura/mosaico (ESA CCI): {agri.sum():,} ({agri.mean() * 100:.1f}%)")
print(f"NDVI mediano de outubro: lavoura {pts[agri].ndvi_out.median():.2f}; todo o CE {pts.ndvi_out.median():.2f}")
print(f"'Pontes verdes' (lavoura/mosaico com NDVI de out >= 0,55): {pts.ponte.sum():,} pixels = "
      f"{pts.ponte.sum() / agri.sum() * 100:.1f}% da lavoura")
m = pts.groupby("codarea").agg(pixels=("ponte", "size"), pontes=("ponte", "sum"))
m["frac"] = m.pontes / m.pixels * 100
m["nome"] = m.index.astype(str).map(nomes)
print("Municipios com mais 'ponte verde' (% da area do municipio):")
print(m.sort_values("pontes", ascending=False).head(12).round(1).to_string())
# distancia de cada pixel de lavoura de sequeiro (NDVI out < 0,45) a ponte verde mais proxima
from scipy.spatial import cKDTree

pv = pts[pts.ponte]
seq = pts[agri & (pts.ndvi_out < 0.45)]
t = cKDTree(np.c_[pv.lat.values * 111, pv.lon.values * 111 * np.cos(np.radians(5))])
dd, _ = t.query(np.c_[seq.lat.values * 111, seq.lon.values * 111 * np.cos(np.radians(5))])
print(f"Lavoura de sequeiro (NDVI out < 0,45): {len(seq):,} pixels; distancia a ponte verde mais proxima: "
      f"mediana {np.median(dd):.0f} km; {np.mean(dd <= 10) * 100:.0f}% a <= 10 km; {np.mean(dd <= 25) * 100:.0f}% a <= 25 km")
