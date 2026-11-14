"""Descobre rotas atuais: links dos granulos (CMR) e produtos do AppEEARS. Nao imprime senha."""
import json
import netrc
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
u, _, p = netrc.netrc(str(Path.home() / "_netrc")).authenticators("urs.earthdata.nasa.gov")
s = sessao_http(retries=2)
CMR = "https://cmr.earthdata.nasa.gov/search/"

for sn, ver in [("GLDAS_NOAH025_M", "2.1"), ("GLDAS_CLSM025_DA1_D", "2.2"), ("NLDAS_NOAH0125_M", "2.0"), ("GPM_3IMERGDL", "07")]:
    c = s.get(CMR + "collections.json", params={"short_name": sn, "version": ver}, timeout=60).json()["feed"]["entry"][0]
    print(f"\n== {sn} {ver} | concept {c['id']} | cloud={c.get('cloud_hosted')}")
    g = s.get(CMR + "granules.json", params={"collection_concept_id": c["id"], "sort_key": "-start_date", "page_size": 1}, timeout=60).json()["feed"]["entry"][0]
    for l in g.get("links", []):
        h = l.get("href", "")
        if h.startswith("http") and not h.endswith((".xml", ".png", ".jpg")):
            print("   ", l.get("rel", "").split("/")[-1][:12], h[:160])

# AppEEARS: produtos SMAP e VIIRS
tok = s.post("https://appeears.earthdatacloud.nasa.gov/api/login", auth=(u, p), timeout=60).json()["token"]
prods = s.get("https://appeears.earthdatacloud.nasa.gov/api/product", timeout=60).json()
print("\n== AppEEARS: produtos SMAP / VIIRS VI / GLDAS?")
for pr in prods:
    pid = pr["ProductAndVersion"]
    if pid.startswith(("SPL3SMP", "SPL4SM", "VNP13", "VJ113", "GLDAS", "NLDAS", "GPM")):
        print("   ", pid, "|", pr.get("Description", "")[:70], "|", pr.get("Resolution"), "|", pr.get("TemporalExtentStart"), "->", pr.get("TemporalExtentEnd"))
for pid in ["SPL3SMP_E.006", "SPL4SMGP.008", "VNP13A1.002"]:
    try:
        lay = s.get(f"https://appeears.earthdatacloud.nasa.gov/api/product/{pid}", timeout=60).json()
        print(f"\n   camadas {pid}:", list(lay.keys())[:25])
    except Exception as e:
        print("   ", pid, "erro", e)
Path("E:/campeonato-nasa/tmp/appeears_token.txt").write_text(tok)
