"""FAO GAEZ v4: baixa o catalogo completo (todos os ImageServers) e os GeoTIFFs globais selecionados.

Uso:
  python -I baixar_gaez.py catalogo     -> dados/gaez/catalogo_gaez_<servico>.csv + catalogo_gaez_completo.csv
  python -I baixar_gaez.py selecionar   -> dados/gaez/selecao.csv (lista de camadas escolhidas)
  python -I baixar_gaez.py baixar       -> dados/gaez/tif/<servico>/<nome>.tif
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
SERVICOS = ["LR", "res01", "res02", "res05", "res06", "res07"]
BASE = "https://gaez-services.fao.org/server/rest/services/{}/ImageServer/query"
P = pasta("gaez")


def catalogo():
    s = sessao_http()
    todos = []
    for sv in SERVICOS:
        linhas, off = [], 0
        while True:
            r = s.get(BASE.format(sv), params={
                "where": "1=1", "outFields": "*", "returnGeometry": "false", "f": "json",
                "resultOffset": off, "resultRecordCount": 1000, "orderByFields": "objectid"}, timeout=120)
            r.raise_for_status()
            d = r.json()
            feats = d.get("features", [])
            linhas += [f["attributes"] for f in feats]
            print(sv, "offset", off, "->", len(feats), flush=True)
            if not feats or not d.get("exceededTransferLimit", len(feats) == 1000):
                break
            off += len(feats)
        df = pd.DataFrame(linhas)
        df["servico"] = sv
        df.to_csv(P / f"catalogo_gaez_{sv}.csv", index=False, encoding="utf-8")
        todos.append(df)
        print(sv, "total", len(df), flush=True)
    full = pd.concat(todos, ignore_index=True)
    full.to_csv(P / "catalogo_gaez_completo.csv", index=False, encoding="utf-8")
    print("catalogo completo:", len(full))


# Culturas (nomes GAEZ) -> nome em pt-BR
CULTURAS = {
    "Maize": "milho", "Sorghum": "sorgo", "Phaseolus bean": "feijão (Phaseolus)", "Cowpea": "feijão-caupi",
    "Cassava": "mandioca", "Cotton": "algodão", "Soybean": "soja", "Wetland rice": "arroz irrigado",
    "Wheat": "trigo", "Pearl millet": "milheto", "Groundnut": "amendoim", "Sugarcane": "cana",
    "Banana": "banana", "Sunflower": "girassol", "Pigeonpea": "guandu", "Grass": "pastagem (gramínea)",
    "Pasture legumes": "leguminosa forrageira",
}
# res05: (variavel, water_supply, input_level, codigo curto)
RES05 = [
    ("Suitability index  range (0 – 10000); all land in grid cell", "Rainfed", "High", "si_seq_alto"),
    ("Suitability index  range (0 – 10000); all land in grid cell", "Rainfed", "Low", "si_seq_baixo"),
    ("Average attainable yield of best occurring suitability class in grid cell", "Rainfed", "High", "yld_seq_alto"),
    ("Average attainable yield of best occurring suitability class in grid cell", "Rainfed", "Low", "yld_seq_baixo"),
    ("Suitability index  range (0 – 10000); current cropland in grid cell", "Rainfed", "High", "si_lav_seq_alto"),
    ("Suitability index  range (0 – 10000); current cropland in grid cell", "Gravity Irrigation", "High", "si_lav_irr_alto"),
    ("Average attainable yield of current cropland", "Gravity Irrigation", "High", "yld_lav_irr_alto"),
    ("Average attainable yield of current cropland", "Rainfed", "High", "yld_lav_seq_alto"),
]
# res06 (2010) e res07 (2010): culturas equivalentes
RES06_CROPS = ["Maize", "Sorghum", "Pulses", "Cassava", "Cotton", "Soybean", "Wetland rice", "Wheat", "Millet",
               "Groundnut", "Sugarcane", "Banana", "Sunflower", "Fodder crops"]
# res01 historico (1981-2010, CRU-TS): variaveis agroclimaticas
RES01_VARS = [
    "Koeppen-Geiger (3-character) classification",
    "Reference potential evapotranspiration (using AWC=100 mm/m)",
    "Reference actual evapotranspiration (using AWC=100 mm/m)",
    "Reference evapotranspiration deficit (mm; AWC=100)",
    "Total number of growing period days",
    "Beginning date of longest component LGP (day-of-year)",
    "Length of longest component LGP (days)",
    "Multi-cropping class (rain-fed)",
    "Multi-cropping class (with irrigation)",
    "Thermal Zones",
    "Annual precipitation (mm)",
    "Annual P/PET ratio (*100)",
    "Modified Fournier Index (mm)",
    "Mean annual temperature (°C)",
    "Annual temperature sum for days with Ta>10 °C (degree-days)",
    "Number of days with Tmax > 35 °C",
    "Number of days with Tmax > 40 °C",
    "Total number of rain days (days with P > 1 mm)",
    "Longest period of consecutive dry days in temperature growing period LGPt=5(days)",
    "Net primary production (rain-fed)",
]
# LR: solos, terreno, cobertura, zonas
LR_VARS = [
    "Dominant AEZ class (33 classes) at 5 arc-minutes", "Moisture regime class", "Thermal regime class",
    "Dominant soil (5 arc-minute)", "Most limiting soil quality, high inputs", "Most limiting soil quality, low inputs",
    "Nutrient availability, low inputs", "Nutrient retention capacity, high inputs", "Rooting conditions, low inputs",
    "Oxygen availability to roots, low inputs", "Presence of salinity and sodicity, low inputs",
    "Workability, low inputs", "Soil suitability, rain-fed, high inputs", "Soil suitability, rain-fed, low inputs",
    "Soil and terrain suitability, rain-fed, low inputs", "Median altitude (5 arc-minute)",
    "Median terrain slope class (5 arc-minute)", "Dominant land cover/use", "Cropland", "Grassland",
    "Cropland, equipped for full control irrigation", "Ruminant livestock density (year 2010)",
]


def _ler(sv):
    d = pd.read_csv(P / f"catalogo_gaez_{sv}.csv", low_memory=False)
    d.columns = [c.lower() for c in d.columns]
    for c in d.columns:
        if d[c].dtype == object:
            d[c] = d[c].astype(str).str.strip()
    return d


def selecionar():
    sel = []
    # res05
    d = _ler("res05")
    h = d[(d["year"] == "1981-2010") & (d["model"] == "CRUTS32")]
    for crop, pt in CULTURAS.items():
        for var, ws, il, cod in RES05:
            m = h[(h["crop"] == crop) & (h["variable"] == var.strip()) & (h["water_supply"] == ws) & (h["input_level"] == il)]
            if len(m):
                r = m.iloc[0]
                sel.append({"servico": "res05", "grupo": "aptidao", "cultura": crop, "cultura_pt": pt, "codigo": cod,
                            "variavel": var, "water_supply": ws, "input_level": il, "unidade": r.get("units"),
                            "nome": r["name"], "url": r["download_url"]})
            else:
                print("res05 sem camada:", crop, cod, flush=True)
    # res02: forrageiras (nao existem no res05) -> potencial agroclimatico, sequeiro, insumo alto
    d2 = _ler("res02")
    h2 = d2[(d2["year"] == "1981-2010") & (d2["model"] == "CRUTS32") & (d2["variable"] == "Agro-climatic potential yield")
            & d2["water_supply"].str.contains("rain-fed") & (d2["input_level"] == "High")]
    for crop in ["Grass", "Pasture legumes", "Alfalfa"]:
        m = h2[h2["crop"] == crop]
        if len(m):
            r = m.iloc[0]
            sel.append({"servico": "res02", "grupo": "forrageira_potencial", "cultura": crop, "codigo": "pot_seq_alto",
                        "variavel": "Agro-climatic potential yield", "water_supply": "rain-fed", "input_level": "High",
                        "unidade": r.get("units"), "nome": r["name"], "url": r["download_url"]})
    # res06 / res07 (2010, total)
    for sv, vars_ in [("res06", ["Yield", "Production"]), ("res07", ["Cropwise Yield Achievement Ratio"])]:
        d = _ler(sv)
        m = d[(d["year"].astype(str).str.startswith("2010")) & (d["water_supply"] == "Total") & d["crop"].isin(RES06_CROPS)
              & d["variable"].isin(vars_)]
        for _, r in m.iterrows():
            sel.append({"servico": sv, "grupo": "producao_real_2010" if sv == "res06" else "lacuna_2010",
                        "cultura": r["crop"], "codigo": r["variable"], "variavel": r["variable"], "unidade": r.get("units"),
                        "nome": r["name"], "url": r["download_url"]})
    # res01 historico
    d = _ler("res01")
    h = d[(d["year"] == "1981-2010") & (d["model"] == "CRUTS32")]
    for v in RES01_VARS:
        m = h[h["variable"] == v]
        if len(m):
            r = m.iloc[0]
            sel.append({"servico": "res01", "grupo": "agroclima", "codigo": v, "variavel": v, "unidade": r.get("units"),
                        "nome": r["name"], "url": r["download_url"]})
        else:
            print("res01 sem camada:", v, flush=True)
    # res01 series anuais 1960-2010 (CRU-TS) para tendencia
    an = d[(d["model"] == "CRUTS32") & d["year"].str.fullmatch(r"\d{4}")]
    for v, cod in [("Total number of growing period days", "lgp_anual"), ("Annual precipitation (mm)", "prec_anual")]:
        m = an[an["variable"] == v].drop_duplicates("year").sort_values("year")
        for _, r in m.iterrows():
            sel.append({"servico": "res01_anual", "grupo": cod, "codigo": cod, "variavel": v, "ano": int(r["year"]),
                        "unidade": r.get("units"), "nome": r["name"], "url": r["download_url"]})
    # LR (nao-climaticas ou historico)
    d = _ler("LR")
    for v in LR_VARS:
        m = d[(d["variable"] == v) & d["year"].isin(["n.a.", "1981-2010"])]
        if len(m):
            r = m.iloc[0]
            sel.append({"servico": "LR", "grupo": "terra_solo", "codigo": v, "variavel": v, "unidade": r.get("units"),
                        "nome": r["name"], "url": r["download_url"]})
        else:
            print("LR sem camada:", v, flush=True)
    s = pd.DataFrame(sel)
    s["arquivo"] = s.apply(lambda r: f"tif/{r['servico']}/{Path(str(r['url'])).name}", axis=1)
    s.to_csv(P / "selecao.csv", index=False, encoding="utf-8")
    print(s.groupby(["servico", "grupo"]).size(), "\nTOTAL", len(s), flush=True)


def baixar_selecao():
    from concurrent.futures import ThreadPoolExecutor
    s = pd.read_csv(P / "selecao.csv")
    ses = sessao_http()

    def um(r):
        dst = P / r["arquivo"]
        try:
            if dst.exists() and dst.stat().st_size > 0:
                return r["arquivo"], "ja", dst.stat().st_size
            baixar(r["url"], dst, ses)
            return r["arquivo"], "ok", dst.stat().st_size
        except Exception as e:
            return r["arquivo"], f"ERRO {e}", 0

    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(um, [r for _, r in s.iterrows()]))
    ok = sum(1 for _, st, _ in res if st in ("ok", "ja"))
    for a, st, sz in res:
        if st not in ("ok", "ja"):
            print(a, st, flush=True)
    print("baixados", ok, "de", len(res), flush=True)
    registrar_manifesto("gaez", {
        "fonte": "FAO GAEZ v4 (gaez-services.fao.org ImageServer + S3 data.gaezdev.aws.fao.org)",
        "cobertura": "global, grade 5 arc-min (~9,3 km no equador), lat 90N-90S",
        "periodo": "clima historico 1981-2010 (CRU-TS 3.2); producao real 2010",
        "n_arquivos": ok, "tamanho_bytes": tamanho_pasta(P / "tif"),
        "selecao": str(P / "selecao.csv"), "catalogo": str(P / "catalogo_gaez_completo.csv"),
    })


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "catalogo"
    if modo == "catalogo":
        catalogo()
    elif modo == "selecionar":
        selecionar()
    elif modo == "baixar":
        baixar_selecao()
