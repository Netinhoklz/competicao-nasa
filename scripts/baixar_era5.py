"""ERA5 (ECMWF/Copernicus) via Planetary Computer (colecao era5-pds, Zarr horario 0,25 grau).

Chunking medido: (372 h, 150 lat, 150 lon) por variavel e por mes, ~5,5 MB comprimido.
O Nordeste inteiro cai num unico bloco espacial (lat idx 300-449, lon idx 1200-1349), entao
cada mes x variavel custa 2 blocos (~11 MB). Recortamos o NE e agregamos em DIARIO no horario
local do Ceara (UTC-3), guardando a contagem de horas para fechar dias que cruzam o fim do mes.

Uso: python baixar_era5.py ANO_INI ANO_FIM [n_threads]
Saida: E:/campeonato-nasa/dados/era5/mensal_parcial/AAAA-MM.nc  (parciais por mes)
       E:/campeonato-nasa/dados/era5/era5_ne_diario_AAAA.nc     (apos consolidar)
"""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import planetary_computer as pc
import pystac_client
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
OUT = pasta("era5")
PARC = OUT / "mensal_parcial"
PARC.mkdir(exist_ok=True)
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"

AN = {"t2m": "air_temperature_at_2_metres", "d2m": "dew_point_temperature_at_2_metres",
      "u10": "eastward_wind_at_10_metres", "v10": "northward_wind_at_10_metres"}
FC = {"tp": "precipitation_amount_1hour_Accumulation",
      "tmx": "air_temperature_at_2_metres_1hour_Maximum",
      "tmn": "air_temperature_at_2_metres_1hour_Minimum",
      "ssrd": "integral_wrt_time_of_surface_direct_downwelling_shortwave_flux_in_air_1hour_Accumulation"}
LAT_MIN, LAT_MAX = BBOX_NE[1], BBOX_NE[3]
LON_MIN, LON_MAX = BBOX_NE[0] % 360, BBOX_NE[2] % 360


def abrir(asset):
    kw = dict(asset.extra_fields["xarray:open_kwargs"])
    kw["chunks"] = None
    return xr.open_dataset(asset.href, **kw)


def recorte(ds, var):
    da = ds[var].sel(lat=slice(LAT_MAX, LAT_MIN), lon=slice(LON_MIN, LON_MAX))
    return da.load()


def processar_mes(ano, mes, cat):
    dest = PARC / f"{ano}-{mes:02d}.nc"
    if dest.exists():
        return dest, 0.0, "ja existia"
    t0 = time.time()
    its = list(cat.search(collections=["era5-pds"], datetime=f"{ano}-{mes:02d}", limit=10).items())
    an = [i for i in its if i.id.endswith("-an")]
    fc = [i for i in its if i.id.endswith("-fc")]
    if not an or not fc:
        raise RuntimeError(f"itens ausentes {ano}-{mes}: {[i.id for i in its]}")
    an, fc = pc.sign(an[0]), pc.sign(fc[0])
    h = {}
    for k, v in AN.items():
        h[k] = recorte(abrir(an.assets[v]), v)
    for k, v in FC.items():
        h[k] = recorte(abrir(fc.assets[v]), v)
    # horario local (UTC-3): data local = (tempo UTC - 3 h)
    out = {}
    for k, da in h.items():
        da = da.assign_coords(time=da["time"] - np.timedelta64(3, "h"))
        out[k] = da
    ws = np.sqrt(out["u10"] ** 2 + out["v10"] ** 2)
    g = lambda da: da.groupby(da["time"].dt.floor("D"))  # noqa: E731
    dd = xr.Dataset({
        "t2m_soma": g(out["t2m"] - 273.15).sum("time"),
        "d2m_soma": g(out["d2m"] - 273.15).sum("time"),
        "ws_soma": g(ws).sum("time"),
        "ws_max": g(ws).max("time"),
        "tmax": g(out["tmx"] - 273.15).max("time"),
        "tmin": g(out["tmn"] - 273.15).min("time"),
        "tp_mm": g(out["tp"] * 1000.0).sum("time"),
        "ssrd_mj": g(out["ssrd"] / 1e6).sum("time"),
        "n_horas_an": g(out["t2m"]).count("time").isel(lat=0, lon=0, drop=True),
        "n_horas_fc": g(out["tp"]).count("time").isel(lat=0, lon=0, drop=True),
    }).rename(floor="data")
    enc = {v: {"zlib": True, "complevel": 4} for v in dd.data_vars}
    dd.astype("float32").to_netcdf(dest, encoding=enc)
    return dest, time.time() - t0, "ok"


def consolidar():
    # ignora parciais gravados ha menos de 2 min (podem estar em escrita)
    arqs = [a for a in sorted(PARC.glob("*.nc")) if time.time() - a.stat().st_mtime > 120]
    ds = xr.open_mfdataset(arqs, combine="nested", concat_dim="data", engine="netcdf4")
    ds = ds.load()
    # dias que cruzam meses aparecem 2x: combinar
    soma = ds[["t2m_soma", "d2m_soma", "ws_soma", "tp_mm", "ssrd_mj", "n_horas_an", "n_horas_fc"]].groupby("data").sum()
    mx = ds[["tmax", "ws_max"]].groupby("data").max()
    mn = ds[["tmin"]].groupby("data").min()
    fin = xr.Dataset({
        "t2m": soma["t2m_soma"] / soma["n_horas_an"],
        "tmax": mx["tmax"], "tmin": mn["tmin"],
        "d2m": soma["d2m_soma"] / soma["n_horas_an"],
        "tp": soma["tp_mm"], "ssrd": soma["ssrd_mj"],
        "ws10": soma["ws_soma"] / soma["n_horas_an"], "ws10_max": mx["ws_max"],
        "n_horas_an": soma["n_horas_an"], "n_horas_fc": soma["n_horas_fc"],
    })
    # descarta dias incompletos nas pontas do periodo
    ok = (fin["n_horas_an"] == 24) & (fin["n_horas_fc"] == 24)
    fin = fin.sel(data=ok)
    fin = fin.assign_coords(lon=(((fin.lon + 180) % 360) - 180))
    attrs = {"t2m": "degC media diaria", "tmax": "degC max horaria", "tmin": "degC min horaria",
             "d2m": "degC ponto de orvalho medio", "tp": "mm/dia", "ssrd": "MJ m-2 dia-1 (radiacao solar descendente)",
             "ws10": "m/s velocidade media do vento a 10 m", "ws10_max": "m/s maxima horaria"}
    for k, u in attrs.items():
        fin[k].attrs["units"] = u
    fin.attrs.update({"fonte": "ERA5 via Microsoft Planetary Computer (era5-pds)", "dia": "horario local UTC-3",
                      "recorte": str(BBOX_NE)})
    enc = {v: {"zlib": True, "complevel": 4} for v in fin.data_vars}
    for ano, sub in fin.groupby("data.year"):
        sub.astype("float32").to_netcdf(OUT / f"era5_ne_diario_{ano}.nc", encoding=enc)
    return fin


def modo_global(ano, mes):
    """Um mes global (t2m medio e precipitacao total) como evidencia de cobertura (~1,1 GB de transferencia)."""
    cat = pystac_client.Client.open(STAC)
    its = list(cat.search(collections=["era5-pds"], datetime=f"{ano}-{mes:02d}", limit=10).items())
    an = pc.sign([i for i in its if i.id.endswith("-an")][0])
    fc = pc.sign([i for i in its if i.id.endswith("-fc")][0])
    import dask
    dask.config.set(scheduler="threads", num_workers=8)
    kw = dict(an.assets[AN["t2m"]].extra_fields["xarray:open_kwargs"])
    t = xr.open_dataset(an.assets[AN["t2m"]].href, **kw)[AN["t2m"]]
    kw = dict(fc.assets[FC["tp"]].extra_fields["xarray:open_kwargs"])
    p = xr.open_dataset(fc.assets[FC["tp"]].href, **kw)[FC["tp"]]
    ds = xr.Dataset({"t2m_media": (t.mean("time") - 273.15).astype("float32"),
                     "tp_total_mm": (p.sum("time") * 1000.0).astype("float32"),
                     "t2m_nan_frac": t.isnull().mean("time").astype("float32")}).compute()
    ds = ds.assign_coords(lon=(((ds.lon + 180) % 360) - 180)).sortby("lon")
    ds.attrs = {"fonte": "ERA5 via Planetary Computer era5-pds", "mes": f"{ano}-{mes:02d}"}
    dest = OUT / f"era5_global_{ano}{mes:02d}.nc"
    ds.to_netcdf(dest, encoding={v: {"zlib": True, "complevel": 4} for v in ds.data_vars})
    print("global salvo", dest, ds.sizes)


if __name__ == "__main__":
    if sys.argv[1] == "global":
        modo_global(int(sys.argv[2]), int(sys.argv[3]))
        sys.exit(0)
    a0, a1 = int(sys.argv[1]), int(sys.argv[2])
    nth = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    if a0 == 0:
        fin = consolidar()
        print("consolidado", fin.sizes)
        sys.exit(0)
    cat = pystac_client.Client.open(STAC)
    meses = [(a, m) for a in range(a0, a1 + 1) for m in range(1, 13)]
    t0 = time.time()
    feitos = 0
    with ThreadPoolExecutor(nth) as ex:
        fut = {ex.submit(processar_mes, a, m, cat): (a, m) for a, m in meses}
        for f in as_completed(fut):
            a, m = fut[f]
            try:
                d, dt, st = f.result()
                feitos += 1
                print(f"{a}-{m:02d} {st} {dt:.0f}s  [{feitos}/{len(meses)}] total {time.time()-t0:.0f}s", flush=True)
            except Exception:
                print(f"{a}-{m:02d} ERRO", traceback.format_exc()[-800:], flush=True)
