"""Consolida os recortes OPeNDAP do SMAP (L4/L3) e do VIIRS VNP13A3 em NetCDF (tempo x lat x lon).

SMAP: grade EASE-Grid 2.0 9 km e retilinea (linha -> lat, coluna -> lon), salva em lat_linhas.npy/lon_colunas.npy.
VIIRS: tiles sinusoidais h13v09/h14v09 projetados para grade regular de 0,01 grau no Ceara (media dos pixels validos).
Uso: python -I consolidar_smap_viirs.py [l4] [l3] [viirs]
"""
import re
import sys
from datetime import datetime

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import xarray as xr  # noqa: E402

from comum import BBOX_CE, DADOS, registrar_manifesto  # noqa: E402


def data_do_nome(nome, padrao):
    m = re.search(padrao, nome)
    return pd.Timestamp(m.group(1))


def smap(chave):
    sub = DADOS / "smap" / ("l4_diario" if chave == "l4" else "l3_diario")
    lat, lon = np.load(sub / "lat_linhas.npy"), np.load(sub / "lon_colunas.npy")
    pecas = sorted(sub.glob("*_recorte.nc4"))
    print(chave, len(pecas), "pecas", flush=True)
    tempos, blocos = [], {}
    for p in pecas:
        try:
            if chave == "l4":
                t = data_do_nome(p.name, r"_(\d{8})T")
                with xr.open_dataset(p, engine="h5netcdf", group="Geophysical_Data", phony_dims="sort") as d:
                    vals = {v: d[v].values for v in ("sm_surface", "sm_rootzone", "sm_rootzone_pctl")}
            else:
                t = data_do_nome(p.name, r"_E_(\d{8})_")
                vals = {}
                for grp, sm, qf, suf in [("Soil_Moisture_Retrieval_Data_AM", "soil_moisture", "retrieval_qual_flag", "am"),
                                         ("Soil_Moisture_Retrieval_Data_PM", "soil_moisture_pm", "retrieval_qual_flag_pm", "pm")]:
                    with xr.open_dataset(p, engine="h5netcdf", group=grp, phony_dims="sort", mask_and_scale=False) as d:
                        vals[f"sm_{suf}"] = d[sm].values.astype("float32")
                        vals[f"qual_{suf}"] = d[qf].values.astype("uint16")
        except Exception as e:  # arquivo corrompido: registra e segue
            print("   erro", p.name, type(e).__name__, flush=True)
            continue
        tempos.append(t)
        for k, v in vals.items():
            blocos.setdefault(k, []).append(v)
    ordem = np.argsort(tempos)
    ds = xr.Dataset({k: (("time", "lat", "lon"), np.stack(v)[ordem]) for k, v in blocos.items()},
                    coords={"time": np.array(tempos)[ordem], "lat": lat, "lon": lon})
    for v in ds.data_vars:
        if v.startswith("sm_") and v != "sm_rootzone_pctl":
            ds[v] = ds[v].where((ds[v] >= 0) & (ds[v] <= 1))
        if v == "sm_rootzone_pctl":
            ds[v] = ds[v].where((ds[v] >= 0) & (ds[v] <= 100))
    ds.attrs["fonte"] = "NASA SMAP " + ("L4 SPL4SMGP v008 (13:30 UTC)" if chave == "l4" else "L3 SPL3SMP_E v006 (AM/PM)")
    destino = DADOS / "smap" / f"smap_{chave}_diario_ne.nc"
    ds.to_netcdf(destino, encoding={v: {"zlib": True, "complevel": 4} for v in ds.data_vars})
    print("   gravado", destino, f"{destino.stat().st_size/1e6:.1f} MB", ds.sizes, flush=True)
    registrar_manifesto("smap", {f"consolidado_{chave}": {"arquivo": str(destino), "tempos": int(ds.sizes["time"]),
                                                           "inicio": str(ds.time.values.min())[:10], "fim": str(ds.time.values.max())[:10],
                                                           "variaveis": list(ds.data_vars)}})


def viirs():
    sub = DADOS / "viirs" / "vnp13a3_tiles"
    R, T, X0, Y0 = 6371007.181, 1111950.5197665233, -20015109.355798, 10007554.677899
    ps = T / 1200
    passo = 0.01
    lats = np.arange(BBOX_CE[1] + passo / 2, BBOX_CE[3], passo)
    lons = np.arange(BBOX_CE[0] + passo / 2, BBOX_CE[2], passo)
    geo = {}
    for tile in ("h13v09", "h14v09"):
        h, v = int(tile[1:3]), int(tile[4:6])
        cc, rr = np.meshgrid(np.arange(1200), np.arange(1200))
        x = X0 + h * T + (cc + 0.5) * ps
        y = Y0 - v * T - (rr + 0.5) * ps
        la = np.degrees(y / R)
        lo = np.degrees(x / (R * np.cos(np.radians(la))))
        dentro = (la >= BBOX_CE[1]) & (la <= BBOX_CE[3]) & (lo >= BBOX_CE[0]) & (lo <= BBOX_CE[2])
        iy = ((la - BBOX_CE[1]) / passo).astype(int)
        ix = ((lo - BBOX_CE[0]) / passo).astype(int)
        geo[tile] = (dentro, iy[dentro], ix[dentro])
    pecas = sorted(sub.glob("VNP13A3.A*.nc4"))
    por_mes = {}
    for p in pecas:
        m = re.search(r"A(\d{4})(\d{3})\.(h\d{2}v\d{2})", p.name)
        t = pd.Timestamp(datetime.strptime(m.group(1) + m.group(2), "%Y%j"))
        por_mes.setdefault(t, []).append((m.group(3), p))
    tempos, nd_l, ev_l, nv_l = [], [], [], []
    for t in sorted(por_mes):
        soma_n = np.zeros((lats.size, lons.size))
        soma_e = np.zeros_like(soma_n)
        cont = np.zeros_like(soma_n)
        for tile, p in por_mes[t]:
            dentro, iy, ix = geo[tile]
            with xr.open_dataset(p, engine="h5netcdf", mask_and_scale=False, phony_dims="sort",
                                 group="HDFEOS/GRIDS/VIIRS_Grid_monthly_VI_1km/Data_Fields") as d:
                ndvi = d["_1_km_monthly_NDVI"].values.astype(float)
                evi = d["_1_km_monthly_EVI"].values.astype(float)
                rel = d["_1_km_monthly_pixel_reliability"].values.astype(int)
            ok = dentro & (rel >= 0) & (rel <= 1) & (ndvi > -10000) & (ndvi <= 10000)
            sel = ok[dentro]
            np.add.at(soma_n, (iy[sel], ix[sel]), ndvi[dentro][sel] / 10000)
            np.add.at(soma_e, (iy[sel], ix[sel]), evi[dentro][sel] / 10000)
            np.add.at(cont, (iy[sel], ix[sel]), 1)
        with np.errstate(invalid="ignore"):
            nd_l.append((soma_n / cont).astype("float32"))
            ev_l.append((soma_e / cont).astype("float32"))
        nv_l.append(cont.astype("uint8"))
        tempos.append(t)
    ds = xr.Dataset({"ndvi": (("time", "lat", "lon"), np.stack(nd_l)), "evi": (("time", "lat", "lon"), np.stack(ev_l)),
                     "n_pixels_validos": (("time", "lat", "lon"), np.stack(nv_l))},
                    coords={"time": tempos, "lat": lats, "lon": lons})
    ds.attrs["fonte"] = "NASA VIIRS VNP13A3 v002 (1 km mensal), pixel_reliability 0-1, projetado para 0,01 grau"
    destino = DADOS / "viirs" / "vnp13a3_ndvi_evi_ceara_001deg.nc"
    ds.to_netcdf(destino, encoding={v: {"zlib": True, "complevel": 4} for v in ds.data_vars})
    print("   gravado", destino, f"{destino.stat().st_size/1e6:.1f} MB", ds.sizes, flush=True)
    registrar_manifesto("viirs", {"consolidado_vnp13a3": {"arquivo": str(destino), "meses": int(ds.sizes["time"]),
                                                          "inicio": str(ds.time.values.min())[:10], "fim": str(ds.time.values.max())[:10]}})


if __name__ == "__main__":
    for k in sys.argv[1:]:
        viirs() if k == "viirs" else smap(k)
