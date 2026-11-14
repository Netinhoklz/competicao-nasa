"""Amostra global do SMAP (1 dia, a cada 8 celulas da grade EASE2 9 km) para validar cobertura: L4 e L3 AM/PM."""
import io
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import xarray as xr  # noqa: E402

from baixar_smap_opendap import CMR, dap4  # noqa: E402
from comum import pasta, registrar_manifesto  # noqa: E402
from edl import sessao_edl  # noqa: E402

s = sessao_edl()
DIA = "2025-04-15"  # quadra chuvosa no Ceara; primavera no hemisferio norte
saida = {}
for sn, ver, filtro, vars_, grp in [
    ("SPL4SMGP", "008", "T133000", ["/Geophysical_Data/sm_rootzone", "/cell_lat", "/cell_lon"], "Geophysical_Data"),
    ("SPL3SMP_E", "006", None, ["/Soil_Moisture_Retrieval_Data_AM/soil_moisture", "/Soil_Moisture_Retrieval_Data_PM/soil_moisture_pm"], None),
]:
    cid = s.get(CMR + "collections.json", params={"short_name": sn, "version": ver}, timeout=60).json()["feed"]["entry"][0]["id"]
    gs = s.get(CMR + "granules.json", params={"collection_concept_id": cid, "temporal": f"{DIA}T00:00:00Z,{DIA}T23:59:59Z", "page_size": 20},
               timeout=60).json()["feed"]["entry"]
    g = next(g for g in gs if not filtro or filtro in g["title"])
    dap = next(l["href"] for l in g["links"] if "opendap.earthdata" in l["href"])
    ce = ";".join(f"{v}[0:8:1623][0:8:3855]" for v in vars_)
    b = dap4(s, dap, ce, timeout=600)
    if sn == "SPL4SMGP":
        with xr.open_dataset(io.BytesIO(b), engine="h5netcdf", phony_dims="sort") as d:
            lat, lon = d["cell_lat"].values, d["cell_lon"].values
        with xr.open_dataset(io.BytesIO(b), engine="h5netcdf", group=grp, phony_dims="sort") as d:
            saida["l4_sm_rootzone"] = d["sm_rootzone"].values
        saida["lat"], saida["lon"] = lat, lon
    else:
        for gname, v, k in [("Soil_Moisture_Retrieval_Data_AM", "soil_moisture", "l3_am"), ("Soil_Moisture_Retrieval_Data_PM", "soil_moisture_pm", "l3_pm")]:
            with xr.open_dataset(io.BytesIO(b), engine="h5netcdf", group=gname, phony_dims="sort", mask_and_scale=False) as d:
                saida[k] = d[v].values.astype("float32")
    print(sn, "ok", flush=True)
ds = xr.Dataset({k: (("y", "x"), v) for k, v in saida.items() if k not in ("lat", "lon")},
                coords={"lat": (("y", "x"), saida["lat"]), "lon": (("y", "x"), saida["lon"])})
for k in ds.data_vars:
    ds[k] = ds[k].where((ds[k] >= 0) & (ds[k] <= 1))
ds.attrs["dia"] = DIA
p = pasta("smap") / "smap_global_amostra_2025-04-15.nc"
ds.to_netcdf(p)
registrar_manifesto("smap", {"amostra_global": {"arquivo": str(p), "dia": DIA, "passo_celulas": 8}})
print("gravado", p, {k: float(np.isfinite(ds[k]).mean()) for k in ds.data_vars})
