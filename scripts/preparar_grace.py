"""Prepara derivados do GRACE/GRACE-FO (CSR RL06.3 mascons).

Entradas: dados/grace/CSR_GRACE_GRACE-FO_RL0603_Mascons_all-corrections.nc (+ LandMask)
Saidas:
  dados/grace/grace_ne_mensal.nc              recorte Nordeste (lon -180..180)
  dados/grace/grace_global_resumo.nc          tendencia OLS, amplitude sazonal, desvio, cobertura por pixel
  dados/grace/grace_cobertura_mensal.parquet  fracao de pixels validos por mes (terra/oceano)
  derivados/grace_ce_mensal.parquet, grace_ne_mensal.parquet, grace_aoi_mensal.parquet
"""
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import Point

sys.stdout.reconfigure(encoding="utf-8")
G = pasta("grace")
ARQ = G / "CSR_GRACE_GRACE-FO_RL0603_Mascons_all-corrections.nc"
DERIV.mkdir(parents=True, exist_ok=True)

# Oeste da Bahia / aquifero Urucuia (aprox.) e as AOIs do Ceara
REGIOES_EXTRA = {"oeste_bahia_urucuia": (-46.6, -14.6, -44.0, -10.4)}


def abrir():
    ds = xr.open_dataset(ARQ, decode_times=False)
    t0 = pd.Timestamp("2002-01-01")
    meio = t0 + pd.to_timedelta(ds["time"].values.astype(float), unit="D")
    ds = ds.assign_coords(time=meio)
    ds = ds.assign_coords(lon=(((ds.lon + 180) % 360) - 180)).sortby("lon")
    lm = xr.open_dataset(G / "CSR_GRACE_GRACE-FO_RL06_Mascons_v02_LandMask.nc")
    lm = lm.assign_coords(lon=(((lm.lon + 180) % 360) - 180)).sortby("lon")
    return ds, lm["LO_val"]


def mascara_poligono(da, gdf):
    """Mascara booleana (lat, lon) de centros de celula dentro do poligono."""
    lo, la = np.meshgrid(da.lon.values, da.lat.values)
    pts = gpd.GeoDataFrame(geometry=[Point(x, y) for x, y in zip(lo.ravel(), la.ravel())], crs=4326)
    dentro = pts.within(gdf.union_all()).values.reshape(lo.shape)
    return xr.DataArray(dentro, coords={"lat": da.lat, "lon": da.lon}, dims=("lat", "lon"))


def media_ponderada(da, mask):
    w = np.cos(np.deg2rad(da.lat)) * mask
    return (da * w).sum(("lat", "lon")) / w.where(da.notnull()).sum(("lat", "lon"))


def longo(serie, variavel, unidade, extra=None):
    df = serie.to_dataframe(name="valor").reset_index()
    df["data"] = df["time"].dt.to_period("M").dt.to_timestamp()
    df = df.groupby("data", as_index=False)["valor"].mean()
    df["variavel"], df["unidade"], df["fonte"] = variavel, unidade, "GRACE/GRACE-FO CSR RL06.3 mascons"
    if extra:
        for k, v in extra.items():
            df[k] = v
    return df


def main():
    ds, land = abrir()
    tws = ds["lwe_thickness"]  # cm de agua equivalente, anomalia em relacao a media 2004-2009
    print("periodo", str(tws.time.values[0])[:10], "->", str(tws.time.values[-1])[:10], "n meses", tws.sizes["time"])

    # recorte NE
    ne = tws.sel(lon=slice(BBOX_NE[0] - 1, BBOX_NE[2] + 1), lat=slice(BBOX_NE[1] - 1, BBOX_NE[3] + 1))
    ne.to_dataset(name="lwe_thickness").to_netcdf(G / "grace_ne_mensal.nc", encoding={"lwe_thickness": {"zlib": True}})

    m_ce = mascara_poligono(ne, ceara_gdf())
    m_ne = mascara_poligono(ne, nordeste_gdf().cx[-49:-34.5, :])
    ce = media_ponderada(ne, m_ce)
    nem = media_ponderada(ne, m_ne)
    longo(ce, "TWS_anomalia", "cm").to_parquet(DERIV / "grace_ce_mensal.parquet")
    longo(nem, "TWS_anomalia", "cm").to_parquet(DERIV / "grace_ne_mensal.parquet")

    aois = []
    for nome, b in REGIOES_EXTRA.items():
        sub = tws.sel(lon=slice(b[0], b[2]), lat=slice(b[1], b[3]))
        w = np.cos(np.deg2rad(sub.lat))
        s = sub.weighted(w).mean(("lat", "lon"))
        aois.append(longo(s, "TWS_anomalia", "cm", {"aoi": nome}))
    for nome, (lo, la, _) in AOIS.items():
        s = tws.sel(lon=lo, lat=la, method="nearest")
        aois.append(longo(s, "TWS_anomalia", "cm", {"aoi": nome}))
    pd.concat(aois, ignore_index=True).to_parquet(DERIV / "grace_aoi_mensal.parquet")

    # resumo global por pixel: tendencia OLS (cm/ano), amplitude sazonal, desvio, cobertura
    print("calculando resumo global...", flush=True)
    t_anos = (tws.time - tws.time[0]).dt.days.values / 365.25
    X = np.column_stack([np.ones_like(t_anos), t_anos,
                         np.sin(2 * np.pi * t_anos), np.cos(2 * np.pi * t_anos)])
    Y = tws.values.reshape(tws.sizes["time"], -1).astype("float64")
    valido = np.isfinite(Y)
    frac = valido.mean(0)
    Yf = np.where(valido, Y, 0.0)
    # minimos quadrados com mascara: resolve pixel a pixel via normal equations vetorizadas
    coef = np.full((4, Y.shape[1]), np.nan)
    tudo = valido.all(0)
    if tudo.any():
        c, *_ = np.linalg.lstsq(X, Yf[:, tudo], rcond=None)
        coef[:, tudo] = c
    shape = (tws.sizes["lat"], tws.sizes["lon"])
    resumo = xr.Dataset({
        "tendencia_cm_ano": (("lat", "lon"), coef[1].reshape(shape)),
        "amplitude_sazonal_cm": (("lat", "lon"), np.hypot(coef[2], coef[3]).reshape(shape)),
        "desvio_cm": (("lat", "lon"), np.nanstd(Y, 0).reshape(shape)),
        "fracao_meses_validos": (("lat", "lon"), frac.reshape(shape)),
        "terra": (("lat", "lon"), land.values),
    }, coords={"lat": tws.lat, "lon": tws.lon})
    resumo.to_netcdf(G / "grace_global_resumo.nc")

    # cobertura mensal: fracao de pixels de terra e oceano com valor
    lmask = land.values > 0.5
    cob = []
    for i, t in enumerate(tws.time.values):
        v = np.isfinite(Y[i].reshape(shape))
        cob.append((pd.Timestamp(t), v[lmask].mean(), v[~lmask].mean()))
    pd.DataFrame(cob, columns=["data", "frac_terra", "frac_oceano"]).to_parquet(G / "grace_cobertura_mensal.parquet")

    registrar_manifesto("grace", {
        "fonte": "CSR/UT Austin GRACE & GRACE-FO RL06.3 mascons (all corrections)",
        "url": "https://download.csr.utexas.edu/outgoing/grace/RL0603_mascons/",
        "doi_mascons": "10.15781/cgq9-nh24 (Save et al. 2016)",
        "variavel": "lwe_thickness: anomalia de armazenamento total de agua (cm de agua equivalente)",
        "grade": "0,25 grau (amostragem); mascons de ~1 grau; resolucao efetiva ~300 km",
        "periodo": f"{str(tws.time.values[0])[:10]} a {str(tws.time.values[-1])[:10]}",
        "n_meses": int(tws.sizes["time"]),
        "recortes_derivados": {"ce": "poligono IBGE", "ne": "poligonos IBGE", **{k: str(v) for k, v in REGIOES_EXTRA.items()}},
        "arquivos": {f.name: f.stat().st_size for f in G.glob("*.*") if f.is_file()},
    })
    print("FIM grace", flush=True)


if __name__ == "__main__":
    main()
