"""Gera tabelas derivadas (mensais) de MODIS/VIIRS para cruzar com as outras bases.

Saidas em E:/campeonato-nasa/dados/derivados/:
  modis_ce_mensal.parquet, modis_ne_mensal.parquet, modis_aoi_mensal.parquet,
  viirs_ce_mensal.parquet, viirs_ne_mensal.parquet
Colunas: data (1o dia do mes), variavel, valor, unidade, fonte [, aoi | uf]
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa: E402,F401

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import xarray as xr  # noqa: E402
from rasterio.features import rasterize  # noqa: E402
from rasterio.transform import from_origin  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
M = DADOS / "modis"
V = DADOS / "viirs"
DERIV.mkdir(parents=True, exist_ok=True)
CE_COD = 23


def mascara_ce(lats, lons):
    res = abs(float(lats[0] - lats[1]))
    T = from_origin(float(lons[0]) - res / 2, float(lats[0]) + res / 2, res, res)
    g = ceara_gdf()
    return rasterize([(geom, 1) for geom in g.geometry], out_shape=(len(lats), len(lons)), transform=T,
                     fill=0, dtype="uint8").astype(bool)


def mensal_regional(da, mask, nome, unidade, fonte):
    v = da.where(xr.DataArray(mask, dims=("lat", "lon"), coords={"lat": da.lat, "lon": da.lon}))
    serie = v.mean(("lat", "lon")).to_series()
    s = serie.groupby(serie.index.to_period("M")).mean()
    return pd.DataFrame({"data": s.index.to_timestamp(), "variavel": nome, "valor": s.values,
                         "unidade": unidade, "fonte": fonte})


def main():
    linhas_ce, linhas_ne, linhas_aoi = [], [], []
    # NDVI/EVI
    p = M / "mod13q1_ndvi_evi_ceara_001deg.nc"
    if p.exists():
        ds = xr.open_dataset(p)
        mk = mascara_ce(ds.lat.values, ds.lon.values)
        for v in ("ndvi", "evi"):
            linhas_ce.append(mensal_regional(ds[v], mk, v, "1", "MOD13Q1"))
        fb = ds["frac_boa"].where(ds["frac_boa"] <= 100)
        linhas_ce.append(mensal_regional(fb, mk, "pct_pixels_boa_qualidade_ndvi", "%", "MOD13Q1"))
    # AOIs 250 m
    for nm in AOIS:
        pa = M / f"mod13q1_aoi_{nm}_250m.nc"
        if not pa.exists():
            continue
        a = xr.open_dataset(pa)
        ok = (a.pixel_reliability <= 1) & (a.ndvi_raw > -3000)
        for v, raw in (("ndvi", "ndvi_raw"), ("evi", "evi_raw")):
            s = (a[raw].where(ok) / 1e4).mean(("lat", "lon")).to_series()
            s = s.groupby(s.index.to_period("M")).mean()
            linhas_aoi.append(pd.DataFrame({"data": s.index.to_timestamp(), "variavel": v, "valor": s.values,
                                            "unidade": "1", "fonte": "MOD13Q1 250m", "aoi": nm}))
        s = (a.ndvi_raw.where(ok) / 1e4 < 0.25).where(ok).mean(("lat", "lon")).to_series()
        s = s.groupby(s.index.to_period("M")).mean()
        linhas_aoi.append(pd.DataFrame({"data": s.index.to_timestamp(), "variavel": "frac_solo_nu_ndvi_lt_025",
                                        "valor": s.values, "unidade": "fracao", "fonte": "MOD13Q1 250m", "aoi": nm}))
    # LST
    p = M / "mod11a2_lst_ceara_001deg.nc"
    if p.exists():
        ds = xr.open_dataset(p)
        mk = mascara_ce(ds.lat.values, ds.lon.values)
        for v in ("lst_dia", "lst_noite"):
            linhas_ce.append(mensal_regional(ds[v], mk, v, "degC", "MOD11A2"))
            for nm in AOIS:
                lon0, lat0, lon1, lat1 = bbox_aoi(nm)
                s = ds[v].sel(lat=slice(lat1, lat0), lon=slice(lon0, lon1)).mean(("lat", "lon")).to_series()
                s = s.groupby(s.index.to_period("M")).mean()
                linhas_aoi.append(pd.DataFrame({"data": s.index.to_timestamp(), "variavel": v, "valor": s.values,
                                                "unidade": "degC", "fonte": "MOD11A2 1km", "aoi": nm}))
    # ET anual (fica no mes de janeiro do ano)
    p = M / "mod16a3gf_et_ceara_0005deg.nc"
    if p.exists():
        ds = xr.open_dataset(p)
        mk = mascara_ce(ds.lat.values, ds.lon.values)
        for v in ("et", "pet"):
            d = mensal_regional(ds[v], mk, v + "_anual", "mm/ano", "MOD16A3GF")
            linhas_ce.append(d)
    # NDVI do Nordeste por UF (MOD13A1 0.05 grau)
    p = M / "mod13a1_ndvi_nordeste_005deg.nc"
    if p.exists():
        ds = xr.open_dataset(p).load()
        res = abs(float(ds.lat[0] - ds.lat[1]))
        T = from_origin(float(ds.lon[0]) - res / 2, float(ds.lat[0]) + res / 2, res, res)
        g = nordeste_gdf()
        cod = rasterize([(geom, int(c)) for geom, c in zip(g.geometry, g["codarea"])],
                        out_shape=(ds.sizes["lat"], ds.sizes["lon"]), transform=T, fill=0, dtype="int32")
        for c in np.unique(cod[cod > 0]):
            s = ds.ndvi.where(xr.DataArray(cod == c, dims=("lat", "lon"))).mean(("lat", "lon")).to_series()
            s = s.groupby(s.index.to_period("M")).mean()
            linhas_ne.append(pd.DataFrame({"data": s.index.to_timestamp(), "variavel": "ndvi", "valor": s.values,
                                           "unidade": "1", "fonte": "MOD13A1 0.05deg", "uf": int(c)}))
    # Fogo MCD64A1 por UF
    p = M / "mcd64a1_area_queimada_mensal_uf.parquet"
    if p.exists():
        f = pd.read_parquet(p)
        f["data"] = pd.to_datetime(f["data"]).dt.to_period("M").dt.to_timestamp()
        ce = f[f.uf == CE_COD].groupby("data").area_queimada_km2.sum()
        linhas_ce.append(pd.DataFrame({"data": ce.index, "variavel": "area_queimada_km2", "valor": ce.values,
                                       "unidade": "km2", "fonte": "MCD64A1"}))
        g = f.groupby(["data", "uf"]).area_queimada_km2.sum().reset_index()
        linhas_ne.append(pd.DataFrame({"data": g.data, "variavel": "area_queimada_km2", "valor": g.area_queimada_km2,
                                       "unidade": "km2", "fonte": "MCD64A1", "uf": g.uf}))
    # FIRMS
    for arq, fonte, alvo in (("firms_modis_nordeste.parquet", "FIRMS MODIS", M),
                             ("firms_viirs_snpp_nordeste.parquet", "FIRMS VIIRS S-NPP", V)):
        p = alvo / arq
        if not p.exists():
            continue
        f = pd.read_parquet(p)
        f = f[f["type"] == 0] if "type" in f else f
        f["data"] = f.acq_date.dt.to_period("M").dt.to_timestamp()
        g = f.groupby(["data", "uf"]).agg(focos=("frp", "size"), frp=("frp", "sum")).reset_index()
        dest_ce = linhas_ce if alvo is M else []
        dest_ne = linhas_ne if alvo is M else []
        ce = g[g.uf == CE_COD]
        tab_ce = pd.concat([
            pd.DataFrame({"data": ce.data, "variavel": "focos_fogo", "valor": ce.focos, "unidade": "n", "fonte": fonte}),
            pd.DataFrame({"data": ce.data, "variavel": "frp_soma", "valor": ce.frp, "unidade": "MW", "fonte": fonte})])
        tab_ne = pd.concat([
            pd.DataFrame({"data": g.data, "variavel": "focos_fogo", "valor": g.focos, "unidade": "n", "fonte": fonte, "uf": g.uf}),
            pd.DataFrame({"data": g.data, "variavel": "frp_soma", "valor": g.frp, "unidade": "MW", "fonte": fonte, "uf": g.uf})])
        if alvo is M:
            dest_ce.append(tab_ce)
            dest_ne.append(tab_ne)
        else:
            tab_ce.to_parquet(DERIV / "viirs_ce_mensal.parquet", index=False)
            tab_ne.to_parquet(DERIV / "viirs_ne_mensal.parquet", index=False)
            print("viirs derivados", len(tab_ce), len(tab_ne))
    for nome, lst in (("modis_ce_mensal", linhas_ce), ("modis_ne_mensal", linhas_ne), ("modis_aoi_mensal", linhas_aoi)):
        if lst:
            d = pd.concat(lst, ignore_index=True).dropna(subset=["valor"])
            d.to_parquet(DERIV / f"{nome}.parquet", index=False)
            print(nome, len(d), sorted(d.variavel.unique()))


def grades():
    """Grades pre-agregadas para a secao do notebook (rodar em < 4 min)."""
    p = M / "mod13q1_ndvi_evi_ceara_001deg.nc"
    if p.exists():
        ds = xr.open_dataset(p)
        ndvi = ds.ndvi.astype("float32").load()
        evi = ds.evi.astype("float32").load()
        mens = xr.Dataset({"ndvi": ndvi.resample(time="MS").mean(), "evi": evi.resample(time="MS").mean()})
        mens.attrs = {"fonte": "MOD13Q1 (Terra) 0.01 grau; media mensal dos compostos de 16 dias que iniciam no mes"}
        mens.to_netcdf(M / "mod13q1_ndvi_mensal_001deg.nc", encoding={v: {"zlib": True, "complevel": 4} for v in mens.data_vars})
        anos = ndvi.time.dt.year
        sel = (anos >= 2001) & (anos <= 2025)
        anu = xr.Dataset({"ndvi": ndvi.sel(time=sel).groupby("time.year").mean(),
                          "evi": evi.sel(time=sel).groupby("time.year").mean(),
                          "ndvi_max": ndvi.sel(time=sel).groupby("time.year").max(),
                          "ndvi_min": ndvi.sel(time=sel).groupby("time.year").min()})
        anu.to_netcdf(M / "mod13q1_ndvi_anual_001deg.nc", encoding={v: {"zlib": True, "complevel": 4} for v in anu.data_vars})
        doy = ndvi.time.dt.dayofyear
        slot = ((doy - 1) // 16).rename("slot")
        n = ndvi.sel(time=sel)
        s = slot.sel(time=sel)
        clim = xr.Dataset({"media": n.groupby(s).mean(), "desvio": n.groupby(s).std(),
                           "n_validos": n.notnull().groupby(s).sum()})
        clim = clim.assign_coords(doy=("slot", clim.slot.values * 16 + 1))
        clim.to_netcdf(M / "mod13q1_ndvi_climatologia_001deg.nc", encoding={v: {"zlib": True, "complevel": 4} for v in clim.data_vars})
        print("grades ndvi ok", mens.sizes, anu.sizes, clim.sizes)
        del ndvi, evi
    p = M / "mod11a2_lst_ceara_001deg.nc"
    if p.exists():
        ds = xr.open_dataset(p)
        out = {}
        for v in ("lst_dia", "lst_noite"):
            a = ds[v].astype("float32").load()
            out[v] = a.resample(time="MS").mean()
            out[v + "_nobs"] = a.notnull().resample(time="MS").sum().astype("int16")
            del a
        mens = xr.Dataset(out)
        mens.attrs = {"fonte": "MOD11A2 (Terra) 0.01 grau; media mensal dos compostos de 8 dias"}
        mens.to_netcdf(M / "mod11a2_lst_mensal_001deg.nc", encoding={v: {"zlib": True, "complevel": 4} for v in mens.data_vars})
        print("grades lst ok", mens.sizes)


if __name__ == "__main__":
    if "--grades" in sys.argv:
        grades()
    main()
