"""Vazao em paralelo (IMERG/ERA5) e periodo disponivel do ERA5 no Planetary Computer."""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import time
from concurrent.futures import ThreadPoolExecutor
import adlfs
import pystac_client
import planetary_computer as pc

sys.stdout.reconfigure(encoding="utf-8")
cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
col = cat.get_collection("gpm-imerg-hhr")
so = col.assets["zarr-abfs"].extra_fields["xarray:storage_options"]
fs = adlfs.AzureBlobFileSystem(**so)
base = "imerg/gpm-imerg-hhr.zarr/precipitationCal"
nomes = [f"{base}/{i}.0.0" for i in range(20000, 20024)]


def pega(n):
    f = adlfs.AzureBlobFileSystem(**so)
    return len(f.cat(n))


for nth in (8, 16):
    t0 = time.time()
    with ThreadPoolExecutor(nth) as ex:
        nb = sum(ex.map(pega, nomes[: nth * 1 + 8]))
    dt = time.time() - t0
    print(f"IMERG {nth} threads: {nb/1e6:.0f} MB em {dt:.1f}s = {nb/1e6/dt:.1f} MB/s", flush=True)

# ERA5 periodo
for ano in (1950, 1979, 1980, 2022, 2023, 2024, 2025, 2026):
    its = list(cat.search(collections=["era5-pds"], datetime=f"{ano}-01-01/{ano}-12-31", limit=50).items())
    print("ERA5", ano, len(its), sorted(i.id for i in its)[-2:], flush=True)
