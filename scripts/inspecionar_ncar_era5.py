"""Inspeciona chunking interno dos NetCDF do ERA5 no espelho NCAR (s3://nsf-ncar-era5, anonimo)."""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import time
import fsspec
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
fs = fsspec.filesystem("s3", anon=True)
for pref in ["nsf-ncar-era5/e5.oper.an.sfc/202401/", "nsf-ncar-era5/e5.oper.fc.sfc.accumu/202401/",
             "nsf-ncar-era5/e5.oper.fc.sfc.minmax/202401/"]:
    try:
        ls = fs.ls(pref, detail=True)
        print(pref, len(ls))
        for x in ls[:40]:
            print("   ", x["name"].split("/")[-1], round(x["size"] / 1e6, 1), "MB")
    except Exception as e:
        print(pref, "erro", e)
# ultimo mes disponivel
meses = sorted(p.split("/")[-1] for p in fs.ls("nsf-ncar-era5/e5.oper.an.sfc/"))
print("an.sfc meses:", meses[:2], "...", meses[-3:])
f = [x for x in fs.ls("nsf-ncar-era5/e5.oper.an.sfc/202401/") if "_2t." in x][0]
t0 = time.time()
ds = xr.open_dataset(fs.open(f), engine="h5netcdf")
v = list(ds.data_vars)[0]
print(f, ds[v].shape, ds[v].encoding.get("chunksizes"), "abrir:", round(time.time() - t0, 1), "s")
print(ds)
