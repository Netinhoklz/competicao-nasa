"""GES DISC (Earthdata Cloud) via OPeNDAP DAP4: recorta no servidor e baixa so a caixa pedida.

Colecoes: GLDAS Noah mensal, GLDAS CLSM diario (agua subterranea), NLDAS mensal (EUA) e IMERG V07 Late/Early recentes.
Exige _netrc + EULA "NASA GESDISC DATA ARCHIVE" aprovado no perfil Earthdata.
Uso: python -I baixar_gesdisc.py [gldas_m gldas_clsm nldas_m imerg_recente]
"""
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
# caixa dos EUA para o NLDAS: cobre as janelas do CDL de Kansas, Iowa e Texas (Lubbock)
BBOX_EUA_PLANICIES = (-102.5, 32.5, -92.5, 43.0)

COLECOES = {
    "gldas_m": dict(sn="GLDAS_NOAH025_M", ver="2.1", bbox=BBOX_NE, pasta="gldas/noah_mensal", t0="2000-01-01", t1="2026-12-31",
                    vars=["SoilMoi0_10cm_inst", "SoilMoi10_40cm_inst", "SoilMoi40_100cm_inst", "SoilMoi100_200cm_inst",
                          "RootMoist_inst", "Evap_tavg", "PotEvap_tavg", "Rainf_f_tavg", "Qs_acc", "Qsb_acc", "Tair_f_inst"]),
    "gldas_clsm": dict(sn="GLDAS_CLSM025_DA1_D", ver="2.2", bbox=BBOX_NE, pasta="gldas/clsm_diario", t0="2003-02-01", t1="2026-12-31",
                       vars=["GWS_tavg", "TWS_tavg", "SoilMoist_RZ_tavg", "SoilMoist_S_tavg", "Evap_tavg"]),
    "nldas_m": dict(sn="NLDAS_NOAH0125_M", ver="2.0", bbox=BBOX_EUA_PLANICIES, pasta="nldas/noah_mensal", t0="1979-01-01", t1="2026-12-31",
                    vars=["SoilM_0_10cm", "SoilM_10_40cm", "SoilM_40_100cm", "SoilM_0_100cm", "Evap", "PotEvap", "Rainf", "Qs", "Qsb"]),
    "imerg_recente": dict(sn="GPM_3IMERGDL", ver="07", bbox=BBOX_NE, pasta="imerg/v07_late_recente", t0="2026-08-01", t1="2026-12-31",
                          vars=["precipitation"]),
    "imerg_early": dict(sn="GPM_3IMERGDE", ver="07", bbox=BBOX_NE, pasta="imerg/v07_early_recente", t0="2026-11-01", t1="2026-12-31",
                        vars=["precipitation"]),
}


def granulos(s, sn, ver, t0, t1, bbox):
    cid = s.get(CMR + "collections.json", params={"short_name": sn, "version": ver}, timeout=60).json()["feed"]["entry"][0]["id"]
    out, pagina = [], 1
    while True:
        r = s.get(CMR + "granules.json", params={"collection_concept_id": cid, "temporal": f"{t0}T00:00:00Z,{t1}T23:59:59Z",
                                                  "bounding_box": ",".join(map(str, bbox)), "page_size": 2000, "page_num": pagina,
                                                  "sort_key": "start_date"}, timeout=120).json()["feed"]["entry"]
        if not r:
            break
        for g in r:
            dap = next((l["href"] for l in g["links"] if "opendap.earthdata.nasa.gov" in l["href"]), None)
            if dap:
                out.append((g["time_start"][:10], g["title"], dap))
        pagina += 1
        if len(r) < 2000:
            break
    return cid, out


def eixo(s, dap, nome):
    r = s.get(f"{dap}.dap.nc4", params={"dap4.ce": f"/{nome}"}, timeout=120)
    r.raise_for_status()
    import io
    with xr.open_dataset(io.BytesIO(r.content), engine="h5netcdf") as d:
        return d[nome].values.astype(float)


def indices(valores, vmin, vmax):
    i = np.where((valores >= vmin) & (valores <= vmax))[0]
    return int(i.min()), int(i.max())


def ordem_dims(s, dap, var):
    import re
    r = s.get(f"{dap}.dmr.xml", timeout=120)
    r.raise_for_status()
    m = re.search(rf'<(?:Float32|Float64|Int16|Int32)\s+name="{var}">(.*?)</', r.text, re.S)
    return re.findall(r'<Dim name="/?([^"]+)"', m.group(1) if m else "")


def baixar(chave, threads=6):
    cfg = COLECOES[chave]
    s = sessao_edl()
    destino = pasta(cfg["pasta"])
    cid, lista = granulos(s, cfg["sn"], cfg["ver"], cfg["t0"], cfg["t1"], cfg["bbox"])
    print(f"{chave}: {len(lista)} granulos ({lista[0][0] if lista else '-'} a {lista[-1][0] if lista else '-'})", flush=True)
    if not lista:
        return
    d0 = lista[0][2]
    lat, lon = eixo(s, d0, "lat"), eixo(s, d0, "lon")
    x0, x1, y0, y1 = cfg["bbox"][0], cfg["bbox"][2], cfg["bbox"][1], cfg["bbox"][3]
    j0, j1 = indices(lat, y0, y1)
    i0, i1 = indices(lon, x0, x1)
    dims = ordem_dims(s, d0, cfg["vars"][0])
    fat = {"time": "[0:0]", "lat": f"[{j0}:{j1}]", "lon": f"[{i0}:{i1}]"}
    sel = "".join(fat.get(d, "") for d in dims)
    ce = ";".join([f"/{v}{sel}" for v in cfg["vars"]] + [f"/lat[{j0}:{j1}]", f"/lon[{i0}:{i1}]", "/time"])
    print(f"   dims={dims} lat[{j0}:{j1}] lon[{i0}:{i1}]", flush=True)

    def um(item):
        data, titulo, dap = item
        alvo = destino / (titulo.split(":")[-1].replace(".nc4", "").replace(".nc", "") + "_recorte.nc4")
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

    t0 = time.time()
    cont = {}
    with ThreadPoolExecutor(threads) as ex:
        fut = [ex.submit(um, it) for it in lista]
        for k, f in enumerate(as_completed(fut), 1):
            st = f.result()
            cont[st] = cont.get(st, 0) + 1
            if k % 200 == 0 or k == len(lista):
                print(f"   {k}/{len(lista)} {cont} {time.time()-t0:.0f}s", flush=True)
    tam = sum(f.stat().st_size for f in destino.glob("*.nc4"))
    registrar_manifesto(cfg["pasta"].split("/")[0], {chave: {
        "fonte": f"NASA GES DISC {cfg['sn']} v{cfg['ver']} (OPeNDAP DAP4, Earthdata Cloud)", "concept_id": cid,
        "recorte_bbox": cfg["bbox"], "variaveis": cfg["vars"], "periodo": [lista[0][0], lista[-1][0]],
        "granulos": len(lista), "status": cont, "bytes": tam, "pasta": str(destino),
        "baixado_em": datetime.now().isoformat(timespec="seconds")}})


if __name__ == "__main__":
    for k in sys.argv[1:] or list(COLECOES):
        baixar(k)
