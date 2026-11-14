"""Para as culturas do Ceara, lista os artigos do indice cujo titulo/resumo cita a cultura e extrai as frases com numeros.

Saida: pesquisa/evidencia_por_cultura.json (cultura -> artigos -> frases relevantes)
"""
import csv
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
ALVO = {
    "Milho": r"\bmaize\b|\bcorn\b", "Feijão-caupi": r"\bcowpeas?\b|vigna unguiculata", "Feijão comum": r"common beans?|phaseolus|dry beans?",
    "Amendoim": r"groundnuts?|peanuts?", "Sorgo": r"\bsorghum\b", "Milheto": r"\bmillets?\b", "Mandioca": r"\bcassava\b|\bmanioc\b",
    "Algodão": r"\bcotton\b", "Guandu": r"pigeon ?peas?|cajanus", "Soja": r"\bsoybeans?\b", "Cana": r"sugar ?cane",
    "Caju": r"\bcashews?\b", "Palma": r"cactus pear|opuntia|nopalea", "Leguminosas": r"\blegumes?\b",
}
s = sessao_http(retries=2)
with open(PROJ / "artigos" / "indice.csv", encoding="utf-8-sig") as f:
    itens = [l for l in csv.DictReader(f) if l["doi"] and not l["status"].startswith("dataset")]
extra = ["10.1038/s41467-025-64567-9", "10.1038/s41467-025-67757-7", "10.1038/s41893-022-00911-x", "10.1038/s43247-023-00746-0",
         "10.1126/science.adj1914", "10.1111/gcb.15747"]
dois = sorted({l["doi"] for l in itens} | set(extra))
saida = {c: [] for c in ALVO}
for doi in dois:
    time.sleep(0.12)
    r = s.get(f"https://api.openalex.org/works/https://doi.org/{doi}", timeout=60)
    if not r.ok:
        continue
    o = r.json()
    inv = o.get("abstract_inverted_index") or {}
    resumo = " ".join(w for _, w in sorted((p, w) for w, ps in inv.items() for p in ps))
    tit = o.get("title") or ""
    texto = f"{tit}. {resumo}"
    aut = (o.get("authorships") or [{}])[0].get("author", {}).get("display_name", "?").split()[-1]
    frases = re.split(r"(?<=[.;])\s+", texto)
    for c, pad in ALVO.items():
        if re.search(pad, texto, re.I):
            rel = [f for f in frases if re.search(pad, f, re.I) and re.search(r"\d", f)]
            saida[c].append({"ref": f"{aut} {o.get('publication_year')}", "doi": doi, "titulo": tit,
                             "revista": ((o.get("primary_location") or {}).get("source") or {}).get("display_name"),
                             "tipo": o.get("type"), "frases_com_numero": rel[:4]})
(PROJ / "pesquisa" / "evidencia_por_cultura.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
for c, lst in saida.items():
    print(f"\n######## {c}: {len(lst)} artigos")
    for a in lst:
        print(f"  - {a['ref']} | {a['titulo'][:110]} | {a['revista']}")
        for fr in a["frases_com_numero"][:2]:
            print("       >", fr[:260])
