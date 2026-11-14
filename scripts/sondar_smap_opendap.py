"""Sonda caminhos e dimensoes das variaveis do SMAP L3/L4 no OPeNDAP da nuvem (DMR)."""
import re
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from edl import sessao_edl  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
s = sessao_edl()
CMR = "https://cmr.earthdata.nasa.gov/search/"
ALVOS = {"SPL3SMP_E": ["soil_moisture", "soil_moisture_pm", "retrieval_qual_flag", "retrieval_qual_flag_pm"],
         "SPL4SMGP": ["sm_surface", "sm_rootzone", "sm_rootzone_pctl", "cell_lat", "cell_lon"]}
for sn, ver in [("SPL3SMP_E", "006"), ("SPL4SMGP", "008")]:
    c = s.get(CMR + "collections.json", params={"short_name": sn, "version": ver}, timeout=60).json()["feed"]["entry"][0]
    g = s.get(CMR + "granules.json", params={"collection_concept_id": c["id"], "sort_key": "-start_date", "page_size": 1}, timeout=60).json()["feed"]["entry"][0]
    dap = next(l["href"] for l in g["links"] if "opendap.earthdata" in l["href"])
    t = s.get(dap + ".dmr.xml", timeout=120).text
    print("==", sn, dap[:110])
    # percorre a arvore guardando o caminho de grupos
    pilha = []
    for m in re.finditer(r"<(/?)(Group|Float32|Float64|Int16|UInt16|Int32|UInt8|Byte|Int8)([^>]*?)(/?)>", t):
        fecha, tag, attrs, auto = m.groups()
        nome = re.search(r'name="([^"]+)"', attrs)
        if tag == "Group":
            if fecha:
                pilha.pop()
            elif not auto:
                pilha.append(nome.group(1))
            continue
        if fecha or not nome:
            continue
        if nome.group(1) in ALVOS[sn]:
            fim = t.find(f"</{tag}>", m.end())
            dims = re.findall(r'<Dim name="([^"]+)"', t[m.end():fim])
            print("  ", tag, "/" + "/".join(pilha + [nome.group(1)]), dims)
    print("   dimensoes declaradas:", re.findall(r'<Dimension name="([^"]+)" size="(\d+)"', t)[:10])
