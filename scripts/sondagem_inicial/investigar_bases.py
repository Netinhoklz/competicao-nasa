"""Checa links do desafio e metadados das colecoes NASA no CMR (sem baixar dados)."""
import sys, json, ssl, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
CTX = ssl.create_default_context(cafile="C:/Program Files/Git/mingw64/etc/ssl/certs/ca-bundle.crt")
UA = {"User-Agent": "Mozilla/5.0 (dataset-check)"}

LINKS = {
    "SMAP": "https://www.earthdata.nasa.gov/data/platforms/space-based-platforms/smap",
    "GPM/IMERG": "https://gpm.nasa.gov/data",
    "Landsat (EarthExplorer)": "https://earthexplorer.usgs.gov/",
    "MODIS (LP DAAC)": "https://lpdaac.usgs.gov/products/",
    "VIIRS (Earthdata Search)": "https://search.earthdata.nasa.gov/search?q=VIIRS",
    "NASA POWER": "https://power.larc.nasa.gov/",
    "SRTM": "https://www.earthdata.nasa.gov/data/instruments/srtm",
    "ECOSTRESS": "https://ecostress.jpl.nasa.gov/data",
    "USDA Ag Data Commons": "https://www.nal.usda.gov/services/agdatacommons",
    "Web Soil Survey": "https://websoilsurvey.nrcs.usda.gov/app/",
    "CDL CropScape": "https://nassgeodata.gmu.edu/CropScape/",
    "PRISM": "https://prism.oregonstate.edu",
    "SSURGO/STATSGO2": "https://www.nrcs.usda.gov/resources/data-and-reports/soils",
    "NAIP": "https://naip-usdaonline.hub.arcgis.com/",
    "NLCD": "https://www.usgs.gov/centers/eros/science/national-land-cover-database",
    "NLDAS/GLDAS (Earthdata)": "https://www.earthdata.nasa.gov/",
    "FAO GAEZ": "https://gaez.fao.org",
    "CoCoRaHS": "https://www.cocorahs.org/Maps",
    "USGS NWIS": "https://waterdata.usgs.gov/nwis",
    "USDA AMS Market News": "https://www.ams.usda.gov/market-news",
    "NASS QuickStats": "https://quickstats.nass.usda.gov",
    "OpenET": "https://openetdata.org",
    "LANDFIRE": "https://www.landfire.gov",
    "GEDI": "https://gedi.umd.edu/data",
    "Sentinel-2 (CDSE)": "https://dataspace.copernicus.eu",
    "ERA5 (CDS)": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview",
}

# colecoes NASA representativas (short_name) para ver versao, periodo e ultimo granulo
CMR = [
    ("SMAP L3 9 km diario", "SPL3SMP_E"),
    ("SMAP L4 zona radicular 9 km 3h", "SPL4SMGP"),
    ("SMAP L3 36 km", "SPL3SMP"),
    ("IMERG Final diario", "GPM_3IMERGDF"),
    ("IMERG Late diario", "GPM_3IMERGDL"),
    ("HLS Landsat 30 m", "HLSL30"),
    ("HLS Sentinel-2 30 m", "HLSS30"),
    ("MODIS NDVI 250 m 16d", "MOD13Q1"),
    ("MODIS ET 500 m 8d", "MOD16A2GF"),
    ("MODIS LST 1 km 8d", "MOD11A2"),
    ("VIIRS NDVI 500 m 16d", "VNP13A1"),
    ("ECOSTRESS LST 70 m (C2)", "ECO_L2T_LSTE"),
    ("ECOSTRESS ET JET 70 m (C2)", "ECO_L3T_JET"),
    ("SRTM 30 m", "SRTMGL1"),
    ("NASADEM 30 m", "NASADEM_HGT"),
    ("GLDAS Noah 0.25 3h", "GLDAS_NOAH025_3H"),
    ("GLDAS CLSM diario (agua subterranea)", "GLDAS_CLSM025_DA1_D"),
    ("NLDAS-2 Noah 0.125 horario", "NLDAS_NOAH0125_H"),
    ("GRACE/GRACE-FO mascons JPL", "TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4"),
    ("GEDI L4A biomassa footprint", "GEDI_L4A_AGB_Density_V2_1_2056"),
    ("GEDI L4B biomassa grade 1 km", "GEDI_L4B_Gridded_Biomass_V2_1_2299"),
]


def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        return r.status, r.geturl(), r.read()


def checa_link(item):
    nome, url = item
    try:
        st, final, body = get(url)
        return nome, st, final if final != url else "", len(body)
    except Exception as e:
        return nome, "ERRO", str(e)[:120], 0


def cmr(item):
    rotulo, sn = item
    base = "https://cmr.earthdata.nasa.gov/search/"
    try:
        _, _, b = get(base + "collections.json?" + urllib.parse.urlencode({"short_name": sn, "page_size": 20}))
        ents = json.loads(b)["feed"]["entry"]
        if not ents:
            return rotulo, sn, "nao encontrado no CMR", "", "", ""
        e = sorted(ents, key=lambda x: x.get("version_id", ""))[-1]
        cid = e["id"]
        _, _, g = get(base + "granules.json?" + urllib.parse.urlencode(
            {"collection_concept_id": cid, "sort_key": "-start_date", "page_size": 1}))
        gr = json.loads(g)["feed"]["entry"]
        ult = gr[0].get("time_start", "?")[:10] if gr else "sem granulos"
        return (rotulo, sn, e.get("version_id", ""), e.get("time_start", "")[:10],
                (e.get("time_end") or "em curso")[:10], ult)
    except Exception as ex:
        return rotulo, sn, "ERRO " + str(ex)[:80], "", "", ""


with ThreadPoolExecutor(8) as ex:
    links = list(ex.map(checa_link, LINKS.items()))
    cols = list(ex.map(cmr, CMR))

print("== LINKS ==")
for n, st, red, sz in links:
    print(f"{n:28s} {st}  {sz:>8}  {red}")

print("\n== CMR (versao | inicio | fim declarado | granulo mais recente) ==")
for r in cols:
    print(" | ".join(str(x) for x in r))

# NISAR (lancado 2025): ver se ha produtos de umidade do solo no CMR
try:
    _, _, b = get("https://cmr.earthdata.nasa.gov/search/collections.json?" +
                  urllib.parse.urlencode({"keyword": "NISAR soil moisture", "page_size": 10}))
    print("\n== NISAR soil moisture (busca por palavra-chave) ==")
    for e in json.loads(b)["feed"]["entry"]:
        print(e.get("short_name"), "|", e.get("version_id"), "|", e.get("title")[:100], "|", e.get("time_start", "")[:10])
except Exception as ex:
    print("NISAR erro", ex)

# NASA POWER: parametros da comunidade AG (so metadados)
try:
    _, _, b = get("https://power.larc.nasa.gov/api/system/manager/parameters?community=AG&temporal=daily")
    d = json.loads(b)
    print("\n== NASA POWER: n parametros diarios comunidade AG ==", len(d))
    print(", ".join(sorted(d.keys())[:200]))
except Exception as ex:
    print("POWER erro", str(ex)[:200])
