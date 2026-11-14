"""NASA NEX-GDDP-CMIP6 (0,25 grau, diario, downscaling estatistico BCSD) via Planetary Computer - AMOSTRA MINIMA.

Cada arquivo e (ano, variavel) com chunk = 1 dia do globo inteiro (~244 MB tasmax, ~181 MB pr por ano),
entao o recorte exige baixar o arquivo inteiro: baixamos para E:/campeonato-nasa/tmp, recortamos o Nordeste e apagamos.
Uso: python baixar_nex_gddp.py [n_threads]
"""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import planetary_computer as pc
import pystac_client
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
OUT = pasta("nex_gddp")
TMP = RAIZ / "tmp" / "nex"
TMP.mkdir(parents=True, exist_ok=True)
MODELO = "MPI-ESM1-2-HR"
JANELAS = [("historical", range(2010, 2015)), ("ssp245", range(2046, 2051)),
           ("ssp585", range(2046, 2051)), ("ssp585", range(2086, 2091))]
VARS = ["tasmax", "pr"]
LAT = (BBOX_NE[1], BBOX_NE[3])
LON = (BBOX_NE[0] % 360, BBOX_NE[2] % 360)


def uma(cat, cen, ano, var, s):
    dest = OUT / f"nex_{MODELO}_{cen}_{var}_{ano}_ne.nc"
    if dest.exists():
        return dest, "ja existia", 0
    it = next(cat.search(collections=["nasa-nex-gddp-cmip6"], datetime=str(ano),
                         query={"cmip6:model": {"eq": MODELO}, "cmip6:scenario": {"eq": cen}}, limit=1).items())
    it = pc.sign(it)
    tmp = TMP / f"{MODELO}_{cen}_{var}_{ano}.nc"
    t0 = time.time()
    baixar(it.assets[var].href, tmp, s)
    ds = xr.open_dataset(tmp, engine="h5netcdf")
    sub = ds[var].sel(lat=slice(*LAT), lon=slice(*LON)).load()
    ds.close()
    if var == "pr":
        sub = sub * 86400.0
        sub.attrs["units"] = "mm/dia"
    else:
        sub = sub - 273.15
        sub.attrs["units"] = "degC"
    sub = sub.assign_coords(lon=(((sub.lon + 180) % 360) - 180))
    sub.to_dataset(name=var).to_netcdf(dest, encoding={var: {"zlib": True, "complevel": 4}})
    mb = tmp.stat().st_size / 1e6
    tmp.unlink()
    return dest, "ok", mb / (time.time() - t0)


if __name__ == "__main__":
    nth = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    s = sessao_http()
    tarefas = [(cen, ano, v) for cen, anos in JANELAS for ano in anos for v in VARS]
    t0 = time.time()
    with ThreadPoolExecutor(nth) as ex:
        fut = {ex.submit(uma, cat, c, a, v, s): (c, a, v) for c, a, v in tarefas}
        for i, f in enumerate(as_completed(fut), 1):
            c, a, v = fut[f]
            try:
                d, st, vel = f.result()
                print(f"[{i}/{len(tarefas)}] {c} {a} {v} {st} {vel:.1f} MB/s total {time.time()-t0:.0f}s", flush=True)
            except Exception:
                print(f"[{i}/{len(tarefas)}] {c} {a} {v} ERRO {traceback.format_exc()[-500:]}", flush=True)
    registrar_manifesto("nex_gddp", {
        "base": "NASA NEX-GDDP-CMIP6 (NASA Ames), downscaling BCSD 0,25 grau diario",
        "rota": "Microsoft Planetary Computer colecao nasa-nex-gddp-cmip6 (NetCDF por ano/variavel, chunk = 1 dia global)",
        "amostra": {"modelo": MODELO, "janelas": [(c, list(a)) for c, a in JANELAS], "variaveis": VARS},
        "recorte": BBOX_NE, "limitacao": "1 modelo e janelas de 5 anos: sinal de temperatura robusto, chuva ruidosa",
        "tamanho_total_MB": round(tamanho_pasta(OUT) / 1e6, 1),
    })
