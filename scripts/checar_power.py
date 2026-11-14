"""Conferencia rapida das saidas do POWER (tamanhos, periodos, faixas, ET0 de referencia)."""
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
P = DADOS / "power"
ds = xr.open_dataset(P / "power_ce_diario.nc")
print(dict(ds.sizes), list(ds.data_vars))
for v in ds.data_vars:
    if "time" in ds[v].dims:
        x = ds[v]
        ok = x.notnull().any(("lat", "lon"))
        t = x.time.values[ok.values]
        print(f"{v:18s} {str(t[0])[:10] if len(t) else '-'} -> {str(t[-1])[:10] if len(t) else '-'} "
              f"nulos={float(x.isnull().mean()):.3f} min={float(x.min()):.2f} max={float(x.max()):.2f} un={x.attrs.get('units','?')}")
f = P / "power_ce_diario_et0.nc"
if f.exists():
    e = xr.open_dataset(f)
    fort = e.ET0.sel(lat=-3.5, lon=-38.75, method="nearest")
    print("ET0 Fortaleza media mm/dia:", round(float(fort.mean()), 2), "| por mes:",
          fort.groupby("time.month").mean().round(1).values.tolist())
for n in ["power_ne_mensal.nc"]:
    if (P / n).exists():
        print(n, dict(xr.open_dataset(P / n).sizes))
g = pd.read_parquet(P / "power_global_amostra.parquet")
g["ok"] = g.valor != -999
print("global IMERG valido por faixa lat:", g[g.param == "IMERG_PRECTOT"].assign(f=pd.cut(g.lat, [-90, -60, 0, 60, 90])).groupby("f").ok.mean().round(2).to_dict())
