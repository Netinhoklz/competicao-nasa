"""Junta os recortes OPeNDAP (um arquivo por granulo) num NetCDF por colecao e gera series mensais (Ceara/NE).

Uso: python -I consolidar_gesdisc.py gldas_m gldas_clsm nldas_m imerg_recente imerg_early
Apaga os recortes individuais so depois de conferir que o consolidado tem todos os tempos.
"""
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402
import xarray as xr  # noqa: E402

from comum import DADOS, DERIV, ceara_gdf, nordeste_gdf, registrar_manifesto  # noqa: E402

CFG = {
    "gldas_m": ("gldas/noah_mensal", "gldas_noah025_mensal_ne.nc", "gldas", "GLDAS-2.1 Noah"),
    "gldas_clsm": ("gldas/clsm_diario", "gldas_clsm025_diario_ne.nc", "gldas_clsm", "GLDAS-2.2 CLSM"),
    "nldas_m": ("nldas/noah_mensal", "nldas_noah0125_mensal_planicies_eua.nc", "nldas", "NLDAS-2 Noah"),
    "imerg_recente": ("imerg/v07_late_recente", "imerg_v07_late_diario_ne_recente.nc", "imerg_late", "IMERG V07 Late"),
    "imerg_early": ("imerg/v07_early_recente", "imerg_v07_early_diario_ne_recente.nc", "imerg_early", "IMERG V07 Early"),
}


def mascara(ds, gdf):
    lon2, lat2 = np.meshgrid(ds.lon.values, ds.lat.values)
    geom = gdf.union_all()
    m = shapely.contains_xy(geom, lon2, lat2)
    return xr.DataArray(m, coords={"lat": ds.lat, "lon": ds.lon}, dims=("lat", "lon"))


def consolidar(chave):
    sub, nome, rotulo, fonte = CFG[chave]
    d = DADOS / sub
    pecas = sorted(d.glob("*_recorte.nc4"))
    destino = d.parent / nome
    if not pecas and destino.exists():
        print(chave, "ja consolidado")
        ds = xr.open_dataset(destino)
    else:
        print(chave, len(pecas), "pecas", flush=True)
        dss = []
        for p in pecas:
            with xr.open_dataset(p, engine="h5netcdf") as x:
                dss.append(x.load())
        ds = xr.concat(dss, dim="time").sortby("time")
        ds = ds.transpose(*[x for x in ("time", "lat", "lon") if x in ds.dims], ...)
        enc = {v: {"zlib": True, "complevel": 4} for v in ds.data_vars if ds[v].ndim >= 2}
        ds.to_netcdf(destino, encoding=enc)
        chk = xr.open_dataset(destino)
        assert chk.sizes["time"] == len(pecas), "consolidado incompleto"
        chk.close()
        for p in pecas:
            p.unlink()
        print("   gravado", destino, f"{destino.stat().st_size/1e6:.1f} MB", flush=True)
    # series mensais
    regioes = {"ce": ceara_gdf(), "ne": nordeste_gdf()} if chave != "nldas_m" else {}
    vars_ = [v for v in ds.data_vars if {"lat", "lon"} <= set(ds[v].dims)]
    for reg, gdf in regioes.items():
        m = mascara(ds, gdf)
        linhas = []
        for v in vars_:
            s = ds[v].where(m).mean(("lat", "lon")).to_series()
            s.index = pd.to_datetime(s.index)
            agg = s.resample("MS").mean() if chave not in ("imerg_recente", "imerg_early") else s.resample("MS").sum(min_count=1)
            un = ds[v].attrs.get("units", "")
            linhas.append(pd.DataFrame({"data": agg.index, "variavel": v, "valor": agg.values, "unidade": un, "fonte": fonte}))
        out = pd.concat(linhas)
        out.to_parquet(DERIV / f"{rotulo}_{reg}_mensal.parquet", index=False)
        print("   derivado", f"{rotulo}_{reg}_mensal.parquet", out.shape, flush=True)
    registrar_manifesto(sub.split("/")[0], {f"consolidado_{chave}": {"arquivo": str(destino), "tempos": int(ds.sizes["time"]),
                                                                     "inicio": str(ds.time.values.min())[:10], "fim": str(ds.time.values.max())[:10],
                                                                     "variaveis": vars_}})


if __name__ == "__main__":
    for k in sys.argv[1:]:
        consolidar(k)
