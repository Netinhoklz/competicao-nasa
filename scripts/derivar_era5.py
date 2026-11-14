"""Derivados do ERA5 diario do Nordeste (0,25 grau, 1979-2020, dia local UTC-3).

- ET0 FAO-56 Penman-Monteith diaria (Allen et al. 1998), VPD, UR media, GDD base 10, dias Tmax>=35.
- Salva E:/campeonato-nasa/dados/era5/era5_ne_derivados_diario.nc (et0, vpd, ur, gdd10)
- Tabelas: derivados/era5_ce_mensal.parquet, era5_ne_mensal.parquet (coluna uf), era5_aoi_mensal.parquet (coluna aoi)
"""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import shapely
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
DIR = DADOS / "era5"
FONTE = "ERA5 (ECMWF) via Planetary Computer era5-pds, 0,25 grau"
SIGLA = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}


def es(t):
    return 0.6108 * np.exp(17.27 * t / (t + 237.3))


def et0_pm(tmax, tmin, td, rs, u10, lat_deg, doy, z=0.0):
    """FAO-56 Penman-Monteith diario (mm/dia). rs em MJ m-2 dia-1, u10 em m/s, temperaturas em degC."""
    tmean = (tmax + tmin) / 2
    e_s = (es(tmax) + es(tmin)) / 2
    e_a = es(td)
    delta = 4098 * es(tmean) / (tmean + 237.3) ** 2
    P = 101.3 * ((293 - 0.0065 * z) / 293) ** 5.26
    gamma = 0.665e-3 * P
    u2 = u10 * 4.87 / np.log(67.8 * 10 - 5.42)
    phi = np.deg2rad(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(dec), -1, 1))
    ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(phi) * np.sin(dec) + np.cos(phi) * np.cos(dec) * np.sin(ws))
    rso = (0.75 + 2e-5 * z) * ra
    rns = 0.77 * rs
    sigma = 4.903e-9
    rnl = sigma * ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2 * (0.34 - 0.14 * np.sqrt(e_a)) * \
        (1.35 * np.clip(rs / rso, 0.25, 1.0) - 0.35)
    rn = rns - rnl
    et0 = (0.408 * delta * rn + gamma * 900 / (tmean + 273) * u2 * (e_s - e_a)) / (delta + gamma * (1 + 0.34 * u2))
    return et0.clip(min=0), (e_s - e_a).clip(min=0), (100 * e_a / e_s).clip(max=100)


def mascara(geom, lon, lat):
    lo, la = np.meshgrid(lon, lat)
    return shapely.contains_xy(geom, lo, la)


UNID = {"t2m": "degC", "tmax": "degC", "tmin": "degC", "d2m": "degC", "tp": "mm/mes", "ssrd": "MJ m-2 dia-1",
        "ws10": "m/s", "et0": "mm/mes", "vpd": "kPa", "ur": "%", "gdd10": "degC-dia/mes", "dias_tmax35": "dias",
        "deficit_p_menos_et0": "mm/mes"}


def mensal(ds):
    g = ds.resample(data="MS")
    return xr.Dataset({
        "t2m": g.mean()["t2m"], "tmax": g.mean()["tmax"], "tmin": g.mean()["tmin"], "d2m": g.mean()["d2m"],
        "tp": g.sum(min_count=1)["tp"], "ssrd": g.mean()["ssrd"], "ws10": g.mean()["ws10"],
        "et0": g.sum(min_count=1)["et0"], "vpd": g.mean()["vpd"], "ur": g.mean()["ur"],
        "gdd10": g.sum(min_count=1)["gdd10"],
        "dias_tmax35": (ds["tmax"] >= 35).where(ds["tmax"].notnull()).resample(data="MS").sum(min_count=1),
        "deficit_p_menos_et0": g.sum(min_count=1)["tp"] - g.sum(min_count=1)["et0"],
    })


def longo(ds_media, extra=None):
    out = []
    for v in ds_media.data_vars:
        s = ds_media[v].to_series()
        df = pd.DataFrame({"data": s.index, "variavel": v, "valor": s.values.astype(float), "unidade": UNID[v], "fonte": FONTE})
        for k, val in (extra or {}).items():
            df[k] = val
        out.append(df)
    return pd.concat(out, ignore_index=True)


def main():
    arqs = sorted(DIR.glob("era5_ne_diario_*.nc"))
    ds = xr.open_mfdataset(arqs, combine="by_coords").load().sortby("lat")
    doy = ds["data"].dt.dayofyear
    lat2 = ds["lat"] * xr.ones_like(ds["lon"])
    et0, vpd, ur = et0_pm(ds.tmax, ds.tmin, ds.d2m, ds.ssrd, ds.ws10, lat2, doy)
    ds["et0"], ds["vpd"], ds["ur"] = et0, vpd, ur
    ds["gdd10"] = ((ds.tmax + ds.tmin) / 2 - 10).clip(min=0)
    der = ds[["et0", "vpd", "ur", "gdd10"]].astype("float32")
    der["et0"].attrs["units"] = "mm/dia (FAO-56 Penman-Monteith, z=0)"
    der["vpd"].attrs["units"] = "kPa"
    der["ur"].attrs["units"] = "% (media diaria aproximada)"
    der["gdd10"].attrs["units"] = "degC-dia (base 10)"
    der.to_netcdf(DIR / "era5_ne_derivados_diario.nc", encoding={v: {"zlib": True, "complevel": 4} for v in der.data_vars})
    mm = mensal(ds)
    mm.astype("float32").to_netcdf(DIR / "era5_ne_mensal_grade.nc",
                                   encoding={v: {"zlib": True, "complevel": 4} for v in mm.data_vars})
    lon, lat = ds.lon.values, ds.lat.values
    m_ce = xr.DataArray(mascara(ceara_gdf().geometry.union_all(), lon, lat), dims=("lat", "lon"))
    longo(mm.where(m_ce).mean(("lat", "lon"))).to_parquet(DERIV / "era5_ce_mensal.parquet", index=False)
    ne = nordeste_gdf()
    tabs = [longo(mm.where(xr.DataArray(mascara(ne.geometry.union_all(), lon, lat), dims=("lat", "lon"))).mean(("lat", "lon")), {"uf": "NE"})]
    for _, r in ne.iterrows():
        m = xr.DataArray(mascara(r.geometry, lon, lat), dims=("lat", "lon"))
        tabs.append(longo(mm.where(m).mean(("lat", "lon")), {"uf": SIGLA[str(r.codarea)]}))
    pd.concat(tabs, ignore_index=True).to_parquet(DERIV / "era5_ne_mensal.parquet", index=False)
    aois = []
    for nome in AOIS:
        lo, la, _ = AOIS[nome]
        sub = mm.sel(lon=lo, lat=la, method="nearest")  # 0,25 grau > AOI: pixel mais proximo
        aois.append(longo(sub.drop_vars(["lat", "lon"]), {"aoi": nome}))
    pd.concat(aois, ignore_index=True).to_parquet(DERIV / "era5_aoi_mensal.parquet", index=False)
    print("ok", ds.sizes, "ET0 media CE mm/ano:",
          float(mm["et0"].where(m_ce).mean(("lat", "lon")).resample(data="YS").sum().mean()))


if __name__ == "__main__":
    main()
