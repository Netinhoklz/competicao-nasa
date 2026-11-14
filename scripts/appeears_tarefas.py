"""AppEEARS: submete recortes (SMAP L3/L4, VIIRS NDVI) e baixa os resultados quando prontos.

Uso:
  python -I appeears_tarefas.py --submeter     # cria as tarefas (uma vez; ids em dados/appeears/tarefas.json)
  python -I appeears_tarefas.py --acompanhar   # consulta a cada 3 min e baixa o que terminar (ate 10 h)
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import AOIS, BBOX_CE, bbox_aoi, pasta, registrar_manifesto, sessao_http  # noqa: E402
from edl import credenciais  # noqa: E402

API = "https://appeears.earthdatacloud.nasa.gov/api"
BASE = pasta("appeears")
ARQ_TAREFAS = BASE / "tarefas.json"
HOJE = datetime.now().strftime("%m-%d-%Y")

# pontos globais de terra para validar cobertura (lon, lat)
PONTOS_GLOBAIS = [(-60.0, -3.1), (-47.9, -15.8), (-38.5, -3.7), (-58.4, -34.6), (-70.6, -33.4), (-77.0, -12.0),
                  (-99.1, 19.4), (-97.5, 35.5), (-93.6, 42.0), (-119.8, 36.4), (-114.0, 51.0), (-147.7, 64.8),
                  (-3.7, 40.4), (2.3, 48.9), (13.4, 52.5), (37.6, 55.8), (24.9, 60.2), (18.9, 69.6),
                  (-15.9, 14.7), (3.4, 6.5), (36.8, -1.3), (31.2, 30.0), (28.0, -26.2), (47.5, -18.9),
                  (39.2, 21.5), (51.4, 35.7), (69.2, 34.5), (77.2, 28.6), (88.4, 22.6), (100.5, 13.8),
                  (106.8, -6.2), (116.4, 39.9), (126.9, 37.6), (139.7, 35.7), (151.2, -33.9), (133.9, -23.7),
                  (115.9, -31.9), (174.8, -41.3), (-68.3, -54.8), (-21.9, 64.1)]


def poligono(b):
    x0, y0, x1, y1 = b
    return [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]


def fc_retangulos(caixas: dict):
    return {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"nome": n}, "geometry": {"type": "Polygon", "coordinates": poligono(b)}}
        for n, b in caixas.items()]}


def camadas(s, produto, padroes):
    todas = list(s.get(f"{API}/product/{produto}", timeout=60).json().keys())
    escolhidas = [c for c in todas if any(re.search(p, c) for p in padroes)]
    return [{"product": produto, "layer": c} for c in escolhidas]


def login(s):
    u, p = credenciais()
    tok = s.post(f"{API}/login", auth=(u, p), timeout=60).json()["token"]
    s.headers["Authorization"] = f"Bearer {tok}"
    return s


def submeter():
    s = login(sessao_http())
    feitas = json.loads(ARQ_TAREFAS.read_text()) if ARQ_TAREFAS.exists() else {}
    ce = fc_retangulos({"ceara": BBOX_CE})
    aois = fc_retangulos({n: bbox_aoi(n) for n in AOIS})
    l3 = camadas(s, "SPL3SMP_E.006", [r"_AM_soil_moisture$", r"_PM_soil_moisture_pm$", r"_AM_retrieval_qual_flag$", r"_PM_retrieval_qual_flag_pm$"])
    l4 = camadas(s, "SPL4SMGP.008", [r"_sm_surface$", r"_sm_rootzone$", r"_sm_rootzone_pctl$"])
    vi3 = camadas(s, "VNP13A3.002", [r"NDVI$", r"_EVI$", r"pixel_reliability$"])
    vi1 = camadas(s, "VNP13A1.002", [r"_NDVI$", r"_EVI$", r"pixel_reliability$"])
    print("camadas:", [c["layer"] for c in l3 + l4 + vi3 + vi1])
    tarefas = {
        # limite de arquivos por pedido: L3 em 3 periodos
        "smap_l3_ceara_2015_2018": ("area", l3, "03-31-2015", "12-31-2018", ce),
        "smap_l3_ceara_2019_2022": ("area", l3, "01-01-2019", "12-31-2022", ce),
        "smap_l3_ceara_2023_2026": ("area", l3, "01-01-2023", HOJE, ce),
        "smap_l4_ceara_2015_2020": ("area", l4, "03-31-2015", "12-31-2020", ce),
        "smap_l4_ceara_2021_2026": ("area", l4, "01-01-2021", HOJE, ce),
        "viirs_vnp13a3_ceara": ("area", vi3, "01-01-2012", HOJE, ce),
        "viirs_vnp13a1_aois": ("area", vi1, "01-17-2012", HOJE, aois),
        "smap_global_pontos_2020": ("point", camadas(s, "SPL3SMP_E.006", [r"_AM_soil_moisture$"]) +
                                    camadas(s, "SPL4SMGP.008", [r"_sm_rootzone$"]), "01-01-2020", "12-31-2020", None),
    }
    for nome, (tipo, lays, d0, d1, geo) in tarefas.items():
        if nome in feitas:
            print("ja submetida:", nome, feitas[nome])
            continue
        params = {"dates": [{"startDate": d0, "endDate": d1}], "layers": lays}
        if tipo == "area":
            params["geo"] = geo
            params["output"] = {"format": {"type": "netcdf4"}, "projection": "geographic"}
        else:
            params["coordinates"] = [{"id": f"p{i}", "longitude": lo, "latitude": la} for i, (lo, la) in enumerate(PONTOS_GLOBAIS)]
        r = s.post(f"{API}/task", json={"task_type": tipo, "task_name": nome, "params": params}, timeout=120)
        print(nome, r.status_code, r.text[:200])
        if r.ok:
            feitas[nome] = r.json()["task_id"]
            ARQ_TAREFAS.write_text(json.dumps(feitas, indent=2))
    registrar_manifesto("appeears", {"fonte": "NASA AppEEARS (LP DAAC/NSIDC) via Earthdata", "tarefas": feitas,
                                     "recorte": {"ceara_bbox": BBOX_CE, "aois": list(AOIS)}})


def acompanhar(horas=10):
    s = login(sessao_http())
    feitas = json.loads(ARQ_TAREFAS.read_text())
    fim = time.time() + horas * 3600
    pendentes = {n: t for n, t in feitas.items() if not (BASE / n / "_OK").exists()}
    while pendentes and time.time() < fim:
        for nome, tid in list(pendentes.items()):
            st = s.get(f"{API}/task/{tid}", timeout=60).json()
            status = st.get("status")
            print(datetime.now().strftime("%H:%M"), nome, status, st.get("progress", {}).get("summary", ""), flush=True)
            if status == "done":
                dest = BASE / nome
                dest.mkdir(exist_ok=True)
                arqs = s.get(f"{API}/bundle/{tid}", timeout=60).json()["files"]
                for a in arqs:
                    alvo = dest / a["file_name"].replace("/", "_")
                    if alvo.exists() and alvo.stat().st_size == a.get("file_size", -1):
                        continue
                    with s.get(f"{API}/bundle/{tid}/{a['file_id']}", stream=True, timeout=600, allow_redirects=True) as r:
                        r.raise_for_status()
                        with open(alvo, "wb") as f:
                            for b in r.iter_content(1 << 20):
                                f.write(b)
                tot = sum(a.get("file_size", 0) for a in arqs)
                (dest / "_OK").write_text(f"{len(arqs)} arquivos, {tot/1e6:.1f} MB")
                print("   baixado:", nome, len(arqs), f"arquivos, {tot/1e6:.1f} MB", flush=True)
                pendentes.pop(nome)
            elif status in ("error", "failed"):
                print("   ERRO:", nome, json.dumps(st)[:400], flush=True)
                pendentes.pop(nome)
        if pendentes:
            time.sleep(180)
    print("pendentes ao sair:", list(pendentes))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--submeter", action="store_true")
    ap.add_argument("--acompanhar", action="store_true")
    a = ap.parse_args()
    if a.submeter:
        submeter()
    if a.acompanhar:
        acompanhar()
