"""Testa HTTPS e OPeNDAP (nuvem) do GES DISC com token EDL: IMERG Late e GLDAS mensal."""
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from edl import sessao_edl  # noqa: E402

s = sessao_edl()
CMR = "https://cmr.earthdata.nasa.gov/search/"
for sn, ver in [("GPM_3IMERGDL", "07"), ("GLDAS_NOAH025_M", "2.1"), ("GLDAS_CLSM025_DA1_D", "2.2"), ("NLDAS_NOAH0125_M", "2.0")]:
    c = s.get(CMR + "collections.json", params={"short_name": sn, "version": ver}, timeout=60).json()["feed"]["entry"][0]
    g = s.get(CMR + "granules.json", params={"collection_concept_id": c["id"], "sort_key": "-start_date", "page_size": 1}, timeout=60).json()["feed"]["entry"][0]
    https = next((l["href"] for l in g["links"] if l["href"].startswith("https://data.gesdisc") or l["href"].startswith("https://hydro1")), None)
    dap = next((l["href"] for l in g["links"] if "opendap.earthdata.nasa.gov" in l["href"]), None)
    print(f"\n== {sn}: {g['title']}")
    if https:
        r = s.get(https, stream=True, timeout=90)
        print("   HTTPS:", r.status_code, r.headers.get("Content-Type"), r.headers.get("Content-Length"), r.url[:80])
        r.close()
    if dap:
        r = s.get(dap + ".dmr.xml", timeout=90)
        print("   OPeNDAP dmr:", r.status_code, len(r.content), "bytes")
        if r.ok:
            import re
            dims = re.findall(r'<Dimension name="([^"]+)" size="(\d+)"', r.text)
            vars_ = re.findall(r'<(?:Float32|Float64|Int16|Int32|Byte) name="([^"]+)"', r.text)
            print("   dims:", dims[:6], "| vars:", vars_[:14])
