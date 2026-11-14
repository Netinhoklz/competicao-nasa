"""VIIRS VNP13A3 (NDVI/EVI mensal 1 km) via OPeNDAP na nuvem do LP DAAC, tiles sinusoidais do Ceara (h13v09, h14v09).

Baixa as 3 variaveis do tile inteiro (1200 x 1200) e depois projeta para lat/lon na consolidacao.
Uso: python -I baixar_viirs_opendap.py [--sondar]
"""
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import BBOX_CE, pasta, registrar_manifesto  # noqa: E402
from edl import sessao_edl  # noqa: E402

CMR = "https://cmr.earthdata.nasa.gov/search/"
TILES = ("h13v09", "h14v09")
NOMES = ("_1_km_monthly_NDVI", "_1_km_monthly_EVI", "_1_km_monthly_pixel_reliability")


def granulos(s):
    cid = s.get(CMR + "collections.json", params={"short_name": "VNP13A3", "version": "002"}, timeout=60).json()["feed"]["entry"][0]["id"]
    out, pag = [], 1
    while True:
        r = s.get(CMR + "granules.json", params={"collection_concept_id": cid, "page_size": 2000, "page_num": pag,
                                                  "sort_key": "start_date", "bounding_box": ",".join(map(str, BBOX_CE))},
                  timeout=180).json()["feed"]["entry"]
        for g in r:
            if any(t in g["title"] for t in TILES):
                dap = next((l["href"] for l in g["links"] if "opendap.earthdata.nasa.gov" in l["href"]), None)
                if dap:
                    out.append((g["time_start"][:10], g["title"], dap))
        if len(r) < 2000:
            break
        pag += 1
    return cid, out


def caminhos(s, dap):
    t = s.get(dap + ".dmr.xml", timeout=120).text
    pilha, achados = [], {}
    for m in re.finditer(r"<(/?)(Group|Int16|UInt8|Int8|UInt16|Float32)([^>]*?)(/?)>", t):
        fecha, tag, attrs, auto = m.groups()
        nome = re.search(r'name="([^"]+)"', attrs)
        if tag == "Group":
            if fecha:
                pilha.pop()
            elif not auto:
                pilha.append(nome.group(1))
            continue
        if not fecha and nome and nome.group(1) in NOMES:
            achados[nome.group(1)] = "/" + "/".join(pilha + [nome.group(1)])
    return achados


def main(sondar=False):
    s = sessao_edl()
    cid, lista = granulos(s)
    cam = caminhos(s, lista[-1][2])
    print(f"{len(lista)} granulos ({lista[0][0]} a {lista[-1][0]}); caminhos: {cam}", flush=True)
    if sondar:
        return
    ce = ";".join(cam[n] for n in NOMES if n in cam)
    destino = pasta("viirs/vnp13a3_tiles")

    def um(item):
        data, titulo, dap = item
        alvo = destino / f"{titulo.split(':')[-1]}.nc4"
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
    with ThreadPoolExecutor(6) as ex:
        for k, f in enumerate(as_completed([ex.submit(um, it) for it in lista]), 1):
            st = f.result()
            cont[st] = cont.get(st, 0) + 1
            if k % 50 == 0 or k == len(lista):
                print(f"   {k}/{len(lista)} {cont} {time.time()-t0:.0f}s", flush=True)
    registrar_manifesto("viirs", {"vnp13a3_opendap": {
        "fonte": "NASA LP DAAC VNP13A3 v002 via OPeNDAP (Earthdata Cloud)", "concept_id": cid, "tiles": TILES,
        "variaveis": cam, "granulos": len(lista), "status": cont, "baixado_em": datetime.now().isoformat(timespec="seconds")}})


if __name__ == "__main__":
    main(sondar="--sondar" in sys.argv)
