"""Localiza (OpenAlex + Crossref) os artigos de cobertura/sucessao do Nordeste citados no texto recebido e salva os DOIs."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
TITULOS = {
    "da Luz 2023 Sustainability": "Short-Term Agronomic and Economic Responses to the Adoption of Cover Crops for Corn Rotation in the Brazilian Semiarid Region",
    "Souza 2024 Stresses": "Maize Morphophysiological Changes Modulated by Cover Crops Rotation in Northeast Brazil",
    "Barbosa 2026 Geoderma Regional": "Cover crops modulate soil phosphorus dynamics under P fertilizer sources in dryland maize production on tropical soil",
    "Melo 2013": "Sistemas de culturas com milho sob semeadura direta na região Nordeste do Brasil",
    "Xavier 2006 RBCS": "Nodulação e produção do caupi sob efeito de plantas de cobertura e inoculação",
    "Pimentel 2011 Rev Cienc Agron": "Sazonalidade de resposta de bioindicadores edáficos utilizando adubação verde em condições semiáridas",
    "Pacheco 2017 Rev Caatinga": "Biomass and nutrient cycling by cover crops in Brazilian Cerrado in the State of Piauí",
    "Pacheco 2013 Bragantia": "Produção de fitomassa e acúmulo de nutrientes por plantas de cobertura no cerrado piauiense",
    "Pacheco 2011 RBCS": "Produção e ciclagem de nutrientes por plantas de cobertura nas culturas de arroz de terras altas e de soja",
    "Embrapa ILP SPD Agreste 2016": "Integração lavoura-pecuária e sistema plantio direto Agreste Nordeste Embrapa Algodão",
    "Embrapa gergelim rotação": "Cultivo do gergelim rotação de culturas Embrapa",
}
s = sessao_http(retries=2)
saida = {}
for rot, tit in TITULOS.items():
    time.sleep(0.3)
    r = s.get("https://api.openalex.org/works", params={"search": tit, "per-page": 3}, timeout=60)
    res = r.json().get("results", []) if r.ok else []
    cand = []
    for o in res:
        cand.append({"doi": (o.get("doi") or "").replace("https://doi.org/", "").lower(), "titulo": o.get("title"), "ano": o.get("publication_year"),
                     "autor": ((o.get("authorships") or [{}])[0].get("author", {}).get("display_name")),
                     "revista": ((o.get("primary_location") or {}).get("source") or {}).get("display_name"),
                     "oa": (o.get("open_access") or {}).get("oa_status"), "tipo": o.get("type")})
    saida[rot] = cand
    print(f"\n== {rot}")
    for c in cand:
        print(f"   {c['ano']} | {c['autor']} | {c['titulo'][:110] if c['titulo'] else ''} | {c['revista']} | {c['doi']} | {c['oa']} | {c['tipo']}")
Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\pesquisa\localizacao_texto2.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
