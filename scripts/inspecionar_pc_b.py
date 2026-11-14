"""Inspeciona chunking/custo dos assets Zarr do Planetary Computer (IMERG, ERA5)."""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import time
import json
import adlfs
import pystac_client
import planetary_computer as pc
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)

# ---------- IMERG: tamanho comprimido dos chunks e velocidade
col = cat.get_collection("gpm-imerg-hhr")
a = col.assets["zarr-abfs"]
so = a.extra_fields["xarray:storage_options"]
fs = adlfs.AzureBlobFileSystem(**so)
base = "imerg/gpm-imerg-hhr.zarr/precipitationCal"
zarray = json.loads(fs.cat(base + "/.zarray"))
print("IMERG .zarray:", zarray)
lst = fs.ls(base, detail=True)[:40]
tam = [x["size"] for x in lst if not x["name"].endswith((".zarray", ".zattrs"))]
print("n amostras", len(tam), "tamanho medio MB", sum(tam) / len(tam) / 1e6, "min", min(tam) / 1e6, "max", max(tam) / 1e6)
t0 = time.time()
nb = 0
for x in lst[5:13]:
    nb += len(fs.cat(x["name"]))
dt = time.time() - t0
print(f"download serial 8 chunks: {nb/1e6:.1f} MB em {dt:.1f}s = {nb/1e6/dt:.1f} MB/s")

# ---------- ERA5
items = list(cat.search(collections=["era5-pds"], datetime="2020-01", limit=5).items())
for it in items:
    for k, asset in it.assets.items():
        if k in ("air_temperature_at_2_metres_1hour_Maximum", "air_temperature_at_2_metres"):
            kw = dict(asset.extra_fields["xarray:open_kwargs"])
            d2 = xr.open_dataset(asset.href, **kw)
            print(k, asset.href)
            print(d2)
            for v in d2.data_vars:
                print(" ", v, "chunks:", d2[v].encoding.get("chunks"), "preferred:", d2[v].encoding.get("preferred_chunks"), d2[v].dtype)
            so2 = kw["storage_options"]
            fs2 = adlfs.AzureBlobFileSystem(**so2)
            path = asset.href.replace("abfs://", "")
            var = list(d2.data_vars)[0]
            l2 = fs2.ls(path + "/" + var, detail=True)
            tt = [x["size"] for x in l2 if not x["name"].endswith((".zarray", ".zattrs"))]
            print("  n chunks", len(tt), "MB medio", sum(tt) / len(tt) / 1e6, "total MB", sum(tt) / 1e6)
            print("  exemplo nomes", [x["name"].split("/")[-1] for x in l2[:6]])
    # demais assets so nomes
print("== range temporal ERA5: buscar ultimo item")
last = list(cat.search(collections=["era5-pds"], datetime="2024-01/2026-12", limit=100).items())
print(sorted(set(i.properties.get("start_datetime", i.datetime and i.datetime.isoformat())[:7] for i in last))[-6:])
