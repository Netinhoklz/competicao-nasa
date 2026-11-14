"""SMAP L3 (SPL3SMP_E) e L4 (SPL4SMGP) via OPeNDAP na nuvem da NSIDC, recortando o Nordeste no servidor.

L4: um granulo por dia (13:30 UTC ~ 10:30 no Ceara): sm_surface, sm_rootzone, sm_rootzone_pctl.
L3: diario, passagens AM e PM, umidade 0-5 cm + flag de qualidade.
Grade EASE-Grid 2.0 de 9 km (1624 x 3856): latitude so depende da linha, longitude so da coluna.
Uso: python -I baixar_smap_opendap.py [l4] [l3]
"""
import io
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import xarray as xr  # noqa: E402

from comum import BBOX_NE, pasta, registrar_manifesto  # noqa: E402
from edl import sessao_edl  # noqa: E402

CMR = "https://cmr.earthdata.nasa.gov/search/"
CFG = {
    "l4": dict(sn="SPL4SMGP", ver="008", sub="smap/l4_diario", filtro="T133000",
               vars=["/Geophysical_Data/sm_surface", "/Geophysical_Data/sm_rootzone", "/Geophysical_Data/sm_rootzone_pctl"]),
    "l3": dict(sn="SPL3SMP_E", ver="006", sub="smap/l3_diario", filtro=None,
               vars=["/Soil_Moisture_Retrieval_Data_AM/soil_moisture", "/Soil_Moisture_Retrieval_Data_AM/retrieval_qual_flag",
                     "/Soil_Moisture_Retrieval_Data_PM/soil_moisture_pm", "/Soil_Moisture_Retrieval_Data_PM/retrieval_qual_flag_pm"]),
}


def dap4(s, url, ce, timeout=300):
    r = s.get(f"{url}.dap.nc4", params={"dap4.ce": ce}, timeout=timeout)
    r.raise_for_status()
    return r.content


def granulos(s, sn, ver, filtro):
    cid = s.get(CMR + "collections.json", params={"short_name": sn, "version": ver}, timeout=60).json()["feed"]["entry"][0]["id"]
    out, pag = [], 1
    while True:
        r = s.get(CMR + "granules.json", params={"collection_concept_id": cid, "page_size": 2000, "page_num": pag,
                                                  "sort_key": "start_date", "bounding_box": ",".join(map(str, BBOX_NE))},
                  timeout=180).json()["feed"]["entry"]
        for g in r:
            if filtro and filtro not in g["title"]:
                continue
            dap = next((l["href"] for l in g["links"] if "opendap.earthdata.nasa.gov" in l["href"]), None)
            if dap:
                out.append((g["time_start"][:10], g["title"], dap))
        if len(r) < 2000:
            break
        pag += 1
    return cid, out


def grade_ease2(s, dap_l4):
    """Linha -> latitude e coluna -> longitude a partir do cell_lat/cell_lon do L4."""
    with xr.open_dataset(io.BytesIO(dap4(s, dap_l4, "/cell_lat[0:1623][1928]")), engine="h5netcdf") as d:
        lat = np.asarray(d["cell_lat"].values).ravel().astype(float)
    with xr.open_dataset(io.BytesIO(dap4(s, dap_l4, "/cell_lon[812][0:3855]")), engine="h5netcdf") as d:
        lon = np.asarray(d["cell_lon"].values).ravel().astype(float)
    return lat, lon


def baixar(chave, s, lat, lon, threads=6):
    cfg = CFG[chave]
    destino = pasta(cfg["sub"])
    cid, lista = granulos(s, cfg["sn"], cfg["ver"], cfg["filtro"])
    x0, y0, x1, y1 = BBOX_NE
    rows = np.where((lat >= y0) & (lat <= y1))[0]
    cols = np.where((lon >= x0) & (lon <= x1))[0]
    r0, r1, c0, c1 = int(rows.min()), int(rows.max()), int(cols.min()), int(cols.max())
    ce = ";".join(f"{v}[{r0}:{r1}][{c0}:{c1}]" for v in cfg["vars"])
    np.save(destino / "lat_linhas.npy", lat[r0:r1 + 1])
    np.save(destino / "lon_colunas.npy", lon[c0:c1 + 1])
    print(f"{chave}: {len(lista)} granulos ({lista[0][0]} a {lista[-1][0]}); linhas {r0}:{r1}, colunas {c0}:{c1}", flush=True)

    def um(item):
        data, titulo, dap = item
        alvo = destino / f"{titulo.split(':')[-1].replace('.h5', '')}_recorte.nc4"
        if alvo.exists() and alvo.stat().st_size > 0:
            return "pulado"
        for t in range(5):
            try:
                r = s.get(f"{dap}.dap.nc4", params={"dap4.ce": ce}, timeout=300)
                if r.status_code == 200:
                    alvo.write_bytes(r.content)
                    return "ok"
                if r.status_code in (403, 404):
                    return f"http {r.status_code}"
            except Exception:
                pass
            time.sleep(5 * (t + 1))
        return "falhou"

    t0, cont = time.time(), {}
    with ThreadPoolExecutor(threads) as ex:
        for k, f in enumerate(as_completed([ex.submit(um, it) for it in lista]), 1):
            st = f.result()
            cont[st] = cont.get(st, 0) + 1
            if k % 250 == 0 or k == len(lista):
                print(f"   {k}/{len(lista)} {cont} {time.time()-t0:.0f}s", flush=True)
    registrar_manifesto("smap", {chave: {
        "fonte": f"NASA NSIDC {cfg['sn']} v{cfg['ver']} via OPeNDAP (Earthdata Cloud)", "concept_id": cid,
        "grade": "EASE-Grid 2.0 9 km; linhas/colunas do recorte salvas em lat_linhas.npy/lon_colunas.npy",
        "recorte_bbox": BBOX_NE, "linhas": [r0, r1], "colunas": [c0, c1], "variaveis": cfg["vars"],
        "filtro_granulo": cfg["filtro"], "granulos": len(lista), "status": cont,
        "baixado_em": datetime.now().isoformat(timespec="seconds")}})


if __name__ == "__main__":
    s = sessao_edl()
    cid4 = s.get(CMR + "collections.json", params={"short_name": "SPL4SMGP", "version": "008"}, timeout=60).json()["feed"]["entry"][0]["id"]
    g = s.get(CMR + "granules.json", params={"collection_concept_id": cid4, "page_size": 1, "sort_key": "-start_date"}, timeout=60).json()["feed"]["entry"][0]
    lat, lon = grade_ease2(s, next(l["href"] for l in g["links"] if "opendap.earthdata" in l["href"]))
    print(f"grade EASE2: {lat.size} linhas ({lat.min():.2f}..{lat.max():.2f}), {lon.size} colunas ({lon.min():.2f}..{lon.max():.2f})", flush=True)
    for k in sys.argv[1:] or ["l4", "l3"]:
        baixar(k, s, lat, lon)
