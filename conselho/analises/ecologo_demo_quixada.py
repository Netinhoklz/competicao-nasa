"""Ecologo - numeros para a demo (AOI Sertao Central / Quixada): recorrencia de fogo VIIRS na AOI de ~11 km,
graus-dia locais (celula POWER mais proxima) e posicao do municipio no aglomerado de milho+sorgo.
Reusa as definicoes de ecologo_fogo_pousio_combustivel.py e ecologo_percolacao_algodao.py.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
import xarray as xr

lon0, lat0, _ = AOIS["sertao_central"]
v = pd.read_parquet(DADOS / "viirs" / "firms_viirs_snpp_nordeste.parquet", columns=["latitude", "longitude", "acq_date", "type", "uf", "confidence"])
v = v[(v["type"] == 0) & v.confidence.isin(["n", "h"])]
v = v[v.latitude.between(lat0 - 0.05, lat0 + 0.05) & v.longitude.between(lon0 - 0.05, lon0 + 0.05)].copy()
v["ano"] = pd.to_datetime(v.acq_date).dt.year
v["mes"] = pd.to_datetime(v.acq_date).dt.month
v = v[v.ano.between(2012, 2025)]
RES = 0.0034
v["ci"] = np.floor(v.latitude / RES).astype(int)
v["cj"] = np.floor(v.longitude / RES).astype(int)
cel = v.groupby(["ci", "cj"]).ano.agg(lambda s: sorted(set(s)))
n_anos = cel.str.len()
area_aoi = (0.1 * 111) * (0.1 * 111 * np.cos(np.radians(lat0)))
print(f"AOI Sertao Central ({area_aoi:.0f} km2): {len(v)} focos 2012-2025; {len(cel)} pixels ~375 m queimados "
      f"(~{len(cel) * 0.1406:.0f} km2 = {len(cel) * 0.1406 / area_aoi * 100:.0f}% da AOI); >= 2 anos: {(n_anos >= 2).mean() * 100:.0f}%")
gaps = np.concatenate([np.diff(t) for t in cel if len(t) > 1]) if (n_anos > 1).any() else np.array([])
if len(gaps):
    print(f"  intervalo mediano entre queimas no mesmo pixel: {np.median(gaps):.0f} anos (n = {len(gaps)})")
print("  focos por mes (soma 2012-2025):", v.groupby("mes").size().to_dict())
print("  focos por ano:", v.groupby("ano").size().to_dict())

ds = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")[["T2M_MAX", "T2M_MIN"]].sel(lat=lat0, lon=lon0, method="nearest").load()
tm = ((ds.T2M_MAX + ds.T2M_MIN) / 2).to_series()
dd = (tm - 12.57).clip(lower=0)
ger = dd.groupby(dd.index.year).sum().loc[1991:2020].mean() / 390.82
mil = np.mean([dd.loc[f"{y}-02-01":pd.Timestamp(f"{y}-02-01") + pd.Timedelta(days=119)].sum() / 390.82 for y in range(1991, 2021)])
mil_irr = np.mean([dd.loc[f"{y}-08-01":pd.Timestamp(f"{y}-08-01") + pd.Timedelta(days=119)].sum() / 390.82 for y in range(1991, 2021)])
print(f"Celula POWER ({float(ds.lat):.2f}, {float(ds.lon):.2f}): lagarta {ger:.1f} geracoes/ano (1991-2020); "
      f"milho de sequeiro 120 d (1/fev) = {mil:.2f} geracoes; milho irrigado 120 d (1/ago) = {mil_irr:.2f} geracoes")
