"""Busca dirigida no OpenAlex por artigos com base no Nordeste/semiarido brasileiro, para as lacunas do estudo.

So guarda resultados cujo titulo ou resumo cita o Nordeste/semiarido/Caatinga/estado do NE. Saida: pesquisa/busca_nordeste.csv
"""
import csv
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from artigos_nordeste import NE  # noqa: E402  (mesma expressao de marcadores)
from comum import sessao_http  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
TEMAS = {
    "rotação/sucessão": ["crop rotation semiarid Brazil", "crop succession Brazilian semiarid yield", "rotação de culturas semiárido"],
    "consórcio": ["intercropping maize cowpea semiarid Brazil", "maize bean intercropping Brazilian semiarid", "consórcio milho feijão-caupi semiárido"],
    "leguminosas arbóreas/aleias": ["gliricidia alley cropping semiarid Brazil", "leucaena semiarid Brazil maize", "Gliricidia sepium Brazilian semiarid soil"],
    "adubação verde/cobertura": ["green manure Brazilian semiarid", "cover crops Brazilian semiarid soil", "adubação verde semiárido"],
    "palma/forrageiras": ["forage cactus Opuntia intercropping semiarid", "buffel grass Cenchrus ciliaris Brazilian semiarid", "integrated crop livestock semiarid Brazil"],
    "solo/carbono": ["soil organic carbon land use Caatinga agriculture", "slash and burn agriculture Caatinga soil carbon fallow", "soil quality agroforestry Caatinga"],
    "milho/caupi/mandioca e seca": ["maize yield drought Northeast Brazil", "cowpea yield rainfed Brazilian semiarid", "cassava yield semiarid Brazil water"],
    "pragas": ["fall armyworm Spodoptera frugiperda Northeast Brazil maize", "boll weevil Anthonomus grandis semiarid Brazil cotton", "whitefly Bemisia cassava Northeast Brazil"],
    "clima/decisão": ["rainy season onset Ceará", "seasonal rainfall forecast Ceará agriculture", "agricultural risk zoning Brazil sowing dates"],
    "agricultura familiar/políticas": ["family farming drought adaptation semiarid Brazil", "Garantia Safra drought insurance Northeast Brazil", "rainwater cisterns semiarid Brazil agriculture"],
    "satélite": ["SMAP soil moisture Brazilian semiarid", "NDVI Caatinga rainfall response", "remote sensing crop mapping Brazilian semiarid"],
}
s = sessao_http(retries=2)
with open(PROJ / "artigos" / "indice.csv", encoding="utf-8-sig") as f:
    ja = {l["doi"] for l in csv.DictReader(f)}
achados = {}
for tema, qs in TEMAS.items():
    for q in qs:
        time.sleep(0.25)
        r = s.get("https://api.openalex.org/works", params={"search": q, "per-page": 25,
                                                             "filter": "publication_year:>1990,type:article|review"}, timeout=60)
        if not r.ok:
            continue
        for o in r.json().get("results", []):
            doi = (o.get("doi") or "").replace("https://doi.org/", "").lower()
            if not doi:
                continue
            inv = o.get("abstract_inverted_index") or {}
            resumo = " ".join(w for _, w in sorted((p, w) for w, ps in inv.items() for p in ps))
            tr = f"{o.get('title') or ''} {resumo}".lower()
            if not re.search(NE, tr):
                continue
            a = achados.setdefault(doi, {"doi": doi, "titulo": o.get("title"), "ano": o.get("publication_year"),
                                         "autor": ((o.get("authorships") or [{}])[0].get("author", {}).get("display_name") or "?"),
                                         "revista": ((o.get("primary_location") or {}).get("source") or {}).get("display_name"),
                                         "citacoes": o.get("cited_by_count"), "oa": (o.get("open_access") or {}).get("oa_status"),
                                         "ja_no_indice": doi in ja, "temas": set(), "resumo": resumo[:700]})
            a["temas"].add(tema)
lista = sorted(achados.values(), key=lambda x: (-(len(x["temas"])), -(x["citacoes"] or 0)))
with open(PROJ / "pesquisa" / "busca_nordeste.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(lista[0].keys()))
    w.writeheader()
    for a in lista:
        w.writerow({**a, "temas": "; ".join(sorted(a["temas"]))})
print(f"{len(lista)} artigos com base no Nordeste encontrados ({sum(not a['ja_no_indice'] for a in lista)} novos)")
for tema in TEMAS:
    sel = sorted([a for a in lista if tema in a["temas"] and not a["ja_no_indice"]], key=lambda x: -(x["citacoes"] or 0))[:8]
    print(f"\n### {tema}")
    for a in sel:
        print(f"  {a['ano']} {a['autor'].split()[-1]:12s} cit {a['citacoes']:4d} {a['oa'] or '-':7s} | {a['titulo'][:105]} | {(a['revista'] or '')[:30]} | {a['doi']}")
