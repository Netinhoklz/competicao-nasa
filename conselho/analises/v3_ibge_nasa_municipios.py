"""v3 - Analista IBGE/Nordeste: leva o dado NASA para a malha municipal do IBGE (1794 municipios do NE).

Cada celula da grade (IMERG 0,1 grau; SMAP L4 9 km) vai para o municipio que contem o seu centro; municipio sem
nenhum centro (os pequenos do litoral e do agreste) recebe a celula mais proxima do seu ponto interior.
Saidas (E:/campeonato-nasa/dados/derivados):
  ibge_ne_mun_imerg_mensal.parquet  cod_mun, data, precip_mm (soma mensal, media das celulas), n_celulas
  ibge_ne_mun_smap_mensal.parquet   cod_mun, data, sm_rootzone (media), dias, dias_rz_lt010, dias_rz_lt015, pctl_media
"""
import glob
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
IB = DADOS / "ibge_nordeste"


def mapa_celulas(lats, lons, mun):
    """Devolve (indice_municipio por celula achatada [-1 = fora], n_celulas por municipio)."""
    LON, LAT = np.meshgrid(lons, lats)
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(LON.ravel(), LAT.ravel()), crs=4326)
    j = gpd.sjoin(pts, mun[["geometry"]].reset_index(names="im"), predicate="within", how="left")
    j = j[~j.index.duplicated()]
    idx = j["im"].fillna(-1).astype(int).to_numpy()
    sem = sorted(set(range(len(mun))) - set(idx[idx >= 0]))
    extra = {}
    for im in sem:  # celula mais proxima do ponto interior
        p = mun.geometry.iloc[im].representative_point()
        i = int(np.abs(lats - p.y).argmin())
        k = int(np.abs(lons - p.x).argmin())
        extra[im] = i * len(lons) + k
    return idx, extra


def agregar(arr, idx, extra, n_mun):
    """arr (tempo, celulas) -> (tempo, municipios) media ignorando NaN."""
    T = arr.shape[0]
    soma = np.zeros((T, n_mun))
    cont = np.zeros((T, n_mun))
    ok = idx >= 0
    v = np.where(np.isnan(arr[:, ok]), 0, arr[:, ok])
    c = (~np.isnan(arr[:, ok])).astype(float)
    for t in range(T):
        np.add.at(soma[t], idx[ok], v[t])
        np.add.at(cont[t], idx[ok], c[t])
    for im, cel in extra.items():
        x = arr[:, cel]
        soma[:, im] = np.nan_to_num(x)
        cont[:, im] = (~np.isnan(x)).astype(float)
    with np.errstate(invalid="ignore"):
        return soma / np.where(cont > 0, cont, np.nan)


if __name__ == "__main__":
    mun = gpd.read_file(IB / "malha_ne_municipio.geojson").rename(columns={"codarea": "cod_mun"})
    mun["geometry"] = mun.geometry.make_valid()
    cods = mun["cod_mun"].astype(str).to_numpy()
    n = len(mun)

    # ---- IMERG diario 0,1 grau -> soma mensal por municipio
    arqs = sorted(glob.glob(str(DADOS / "imerg" / "imerg_ne_diario_*.nc")))
    d0 = xr.open_dataset(arqs[0])
    idx, extra = mapa_celulas(d0.lat.values, d0.lon.values, mun)
    print("IMERG: celulas dentro", int((idx >= 0).sum()), "municipios sem celula", len(extra), flush=True)
    partes = []
    for a in arqs:
        ds = xr.open_dataset(a)
        m = ds["precip"].resample(time="MS").sum(min_count=20)  # mm/dia somado = mm/mes
        arr = m.values.reshape(m.shape[0], -1)
        ag = agregar(arr, idx, extra, n)
        df = pd.DataFrame(ag, columns=cods)
        df["data"] = m.time.values
        partes.append(df.melt(id_vars="data", var_name="cod_mun", value_name="precip_mm"))
        ultimo = str(ds.time.values[-1])[:10]
    im = pd.concat(partes, ignore_index=True)
    nc = pd.Series(np.bincount(idx[idx >= 0], minlength=n), index=cods)
    im["n_celulas"] = im["cod_mun"].map(nc).replace(0, 1)
    im["fonte"] = "GPM IMERG V07 (NASA POWER IMERG_PRECTOT 0,1 grau) agregado na malha municipal IBGE"
    im.to_parquet(DERIV / "ibge_ne_mun_imerg_mensal.parquet")
    print("IMERG ok", im.shape, "ultimo dia", ultimo, flush=True)

    # ---- SMAP L4 diario 9 km -> mensal por municipio
    s = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
    idx, extra = mapa_celulas(s.lat.values, s.lon.values, mun)
    print("SMAP: celulas dentro", int((idx >= 0).sum()), "municipios sem celula", len(extra), flush=True)
    rz = s["sm_rootzone"].values.reshape(s.sizes["time"], -1)
    rz_m = agregar(rz, idx, extra, n)
    del rz
    pc = s["sm_rootzone_pctl"].values.reshape(s.sizes["time"], -1)
    pc_m = agregar(pc, idx, extra, n)
    del pc
    tempo = pd.to_datetime(s.time.values)
    dd = pd.DataFrame(rz_m, columns=cods, index=tempo)
    pp = pd.DataFrame(pc_m, columns=cods, index=tempo)
    # diario por municipio (para a analise do semiarido)
    dd.to_parquet(IB / "smap_l4_rootzone_diario_municipio.parquet")
    mes = dd.index.to_period("M").to_timestamp()
    out = pd.DataFrame({
        "sm_rootzone": dd.groupby(mes).mean().stack(),
        "dias": dd.notna().groupby(mes).sum().stack(),
        "dias_rz_lt010": (dd < 0.10).groupby(mes).sum().stack(),
        "dias_rz_lt015": (dd < 0.15).groupby(mes).sum().stack(),
        "pctl_media": pp.groupby(mes).mean().stack(),
    }).reset_index()
    out.columns = ["data", "cod_mun", "sm_rootzone", "dias", "dias_rz_lt010", "dias_rz_lt015", "pctl_media"]
    out["fonte"] = "NASA SMAP L4 SPL4SMGP v008 13:30 UTC agregado na malha municipal IBGE (m3/m3)"
    out.to_parquet(DERIV / "ibge_ne_mun_smap_mensal.parquet")
    print("SMAP ok", out.shape, str(tempo.min())[:10], str(tempo.max())[:10], flush=True)
