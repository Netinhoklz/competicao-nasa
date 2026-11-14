"""Tabelas derivadas do IMERG (via POWER, 0,1 grau, diario UTC) para cruzar com outras bases.

Saidas em E:/campeonato-nasa/dados/derivados/:
  imerg_ce_mensal.parquet   (data, variavel, valor, unidade, fonte)          media na area do Ceara (mascara IBGE)
  imerg_ne_mensal.parquet   (data, variavel, valor, unidade, fonte, uf)      uf = 'NE' (regiao) ou sigla da UF
  imerg_aoi_mensal.parquet  (data, variavel, valor, unidade, fonte, aoi)     media na caixa de cada AOI
"""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import shapely
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
DIR = DADOS / "imerg"
FONTE = "GPM IMERG V07 via NASA POWER (0,1 grau)"
SIGLA = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}


def mascara(geom, lon, lat):
    lo, la = np.meshgrid(lon, lat)
    return shapely.contains_xy(geom, lo, la)


def mensal_de_diario(da):
    """da (time, lat, lon) mm/dia -> Dataset mensal com total, dias>=1mm, rx1day, dias>=20, dias>=50."""
    g = da.resample(time="MS")
    return xr.Dataset({
        "precip_total": g.sum(min_count=1),
        "dias_chuva_1mm": (da >= 1).resample(time="MS").sum(),
        "dias_20mm": (da >= 20).resample(time="MS").sum(),
        "dias_50mm": (da >= 50).resample(time="MS").sum(),
        "rx1day": g.max(),
    })


UNID = {"precip_total": "mm/mes", "dias_chuva_1mm": "dias", "dias_20mm": "dias", "dias_50mm": "dias", "rx1day": "mm/dia"}


def para_longo(ds_media, extra=None):
    linhas = []
    for v in ds_media.data_vars:
        s = ds_media[v].to_series()
        df = pd.DataFrame({"data": s.index, "variavel": v, "valor": s.values.astype(float),
                           "unidade": UNID[v], "fonte": FONTE})
        if extra:
            for k, val in extra.items():
                df[k] = val
        linhas.append(df)
    return pd.concat(linhas, ignore_index=True)


def main():
    DERIV.mkdir(parents=True, exist_ok=True)
    # ---------------- Ceara
    ce = xr.open_mfdataset(sorted(DIR.glob("imerg_ce_diario_*.nc")), combine="by_coords")["precip"].load()
    m_ce = mascara(ceara_gdf().geometry.union_all(), ce.lon.values, ce.lat.values)
    mens = mensal_de_diario(ce)
    media = mens.where(xr.DataArray(m_ce, dims=("lat", "lon"))).mean(("lat", "lon"))
    df = para_longo(media)
    df.to_parquet(DERIV / "imerg_ce_mensal.parquet", index=False)
    print("CE", df.shape, df["data"].min(), df["data"].max())
    # ---------------- AOIs
    aois = []
    for nome in AOIS:
        x0, y0, x1, y1 = bbox_aoi(nome)
        sub = mens.sel(lon=slice(x0, x1), lat=slice(y0, y1)).mean(("lat", "lon"))
        aois.append(para_longo(sub, {"aoi": nome}))
    pd.concat(aois, ignore_index=True).to_parquet(DERIV / "imerg_aoi_mensal.parquet", index=False)
    # ---------------- Nordeste por UF
    arqs = sorted(DIR.glob("imerg_ne_diario_*.nc"))
    if not arqs:
        print("sem NE ainda")
        return
    ne_gdf = nordeste_gdf()
    partes = []
    for a in arqs:
        da = xr.open_dataset(a)["precip"].load()
        mm = mensal_de_diario(da)
        partes.append(mm)
    mens_ne = xr.concat(partes, dim="time")
    lon, lat = mens_ne.lon.values, mens_ne.lat.values
    tabelas = []
    m_ne = mascara(ne_gdf.geometry.union_all(), lon, lat)
    tabelas.append(para_longo(mens_ne.where(xr.DataArray(m_ne, dims=("lat", "lon"))).mean(("lat", "lon")), {"uf": "NE"}))
    for _, row in ne_gdf.iterrows():
        m = mascara(row.geometry, lon, lat)
        tabelas.append(para_longo(mens_ne.where(xr.DataArray(m, dims=("lat", "lon"))).mean(("lat", "lon")),
                                  {"uf": SIGLA.get(str(row["codarea"]), str(row["codarea"]))}))
    out = pd.concat(tabelas, ignore_index=True)
    out.to_parquet(DERIV / "imerg_ne_mensal.parquet", index=False)
    print("NE", out.shape, out["uf"].unique())


if __name__ == "__main__":
    main()
