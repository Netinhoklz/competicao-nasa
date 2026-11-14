"""Inspeciona formato/chunking do NEX-GDDP-CMIP6 no Planetary Computer (so metadados)."""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import json
import pystac_client
import planetary_computer as pc
import xarray as xr
import fsspec

sys.stdout.reconfigure(encoding="utf-8")
cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
col = cat.get_collection("nasa-nex-gddp-cmip6")
print("assets da colecao (primeiros):", list(col.assets.keys())[:12], "... total", len(col.assets))
print("summaries:", {k: (v if len(str(v)) < 300 else str(v)[:300]) for k, v in (col.summaries.to_dict() if col.summaries else {}).items()})
its = list(cat.search(collections=["nasa-nex-gddp-cmip6"], query={"cmip6:model": {"eq": "ACCESS-CM2"}, "cmip6:scenario": {"eq": "ssp585"}},
                      datetime="2050", limit=3).items())
for it in its:
    print(it.id, it.properties)
    for k, a in it.assets.items():
        print("  ", k, a.href[:120], a.media_type)
it = its[0]
a = it.assets["tasmax"]
ds = xr.open_dataset(fsspec.open(a.href).open(), engine="h5netcdf")
print(ds)
print("chunks:", ds["tasmax"].encoding.get("chunksizes"), ds["tasmax"].encoding)
