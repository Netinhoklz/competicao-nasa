import sys, json, ssl, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context(cafile="C:/Program Files/Git/mingw64/etc/ssl/certs/ca-bundle.crt")
UA = {"User-Agent": "Mozilla/5.0 (dataset-check)"}
B = "https://cmr.earthdata.nasa.gov/search/"

def j(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read())

def colls(**q):
    q.setdefault("page_size", 20)
    return j(B + "collections.json?" + urllib.parse.urlencode(q))["feed"]["entry"]

def last_gran(cid, n=1):
    return j(B + "granules.json?" + urllib.parse.urlencode(
        {"collection_concept_id": cid, "sort_key": "-start_date", "page_size": n}))["feed"]["entry"]

print("== IMERG (todas as versoes/short names com IMERG diario) ==")
for e in colls(keyword="IMERG daily", page_size=30):
    if "IMERG" in e.get("short_name", ""):
        g = last_gran(e["id"])
        print(e["short_name"], e.get("version_id"), e.get("time_start", "")[:10], "->",
              (e.get("time_end") or "em curso")[:10], "| ultimo:", g[0]["time_start"][:10] if g else "-")

print("\n== GRACE mascons: granulos ==")
for sn in ["TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4", "TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4"]:
    for e in colls(short_name=sn):
        gs = last_gran(e["id"], 3)
        for g in gs:
            print(sn, "|", g.get("title", "")[:90], "|", g.get("time_start", "")[:10], "->", g.get("time_end", "")[:10])

print("\n== NISAR soil moisture: ultimo granulo e resumo ==")
for sn in ["NISAR_L3_SME2_PROVISIONAL_V1", "NISAR_L3_SME2_BETA_V1"]:
    for e in colls(short_name=sn):
        g = last_gran(e["id"])
        print(sn, "| ultimo:", g[0]["time_start"][:10] if g else "-")
        print("   resumo:", (e.get("summary") or "")[:600].replace("\n", " "))

print("\n== GEDI L4A: versoes ==")
for e in colls(keyword="GEDI L4A aboveground biomass footprint", page_size=20):
    sn = e.get("short_name", "")
    if "L4A" in sn and "AGB" in sn:
        g = last_gran(e["id"])
        print(sn, e.get("version_id"), "| ultimo:", g[0]["time_start"][:10] if g else "-")

print("\n== OPERA DSWx/DIST e HLS-VI (produtos derivados prontos) ==")
for sn in ["OPERA_L3_DIST-ALERT-HLS_V1", "HLSL30_VI", "HLSS30_VI"]:
    try:
        for e in colls(short_name=sn):
            g = last_gran(e["id"])
            print(sn, e.get("version_id"), e.get("time_start", "")[:10], "| ultimo:", g[0]["time_start"][:10] if g else "-")
    except Exception as ex:
        print(sn, "erro", ex)
