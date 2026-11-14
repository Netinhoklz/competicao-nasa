"""Quais culturas os artigos baixados (artigos/*.pdf) cobrem: conta mencoes por cultura em cada PDF e gera tabela.

Criterios: 'cita' = >= 3 mencoes no texto; 'foco' = >= 15 mencoes. Saida: pesquisa/culturas_nos_artigos.md e .csv
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
from pypdf import PdfReader  # noqa: E402

PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
ART = PROJ / "artigos"
CULTURAS = {  # nome em PT: padroes (ingles e portugues), sem diferenciar maiusculas
    "Milho": [r"\bmaize\b", r"\bcorn\b", r"\bmilho\b"],
    "Trigo": [r"\bwheat\b", r"\btrigo\b"],
    "Arroz": [r"\brice\b", r"\barroz\b"],
    "Soja": [r"\bsoybeans?\b", r"\bsoya\b", r"\bsoja\b"],
    "Sorgo": [r"\bsorghum\b", r"\bsorgo\b"],
    "Milheto": [r"\bmillets?\b", r"\bmilheto\b"],
    "Cevada": [r"\bbarley\b", r"\bcevada\b"],
    "Aveia": [r"\boats?\b", r"\baveia\b"],
    "Centeio": [r"\brye\b", r"\bcenteio\b"],
    "Canola/colza": [r"\brapeseed\b", r"\bcanola\b", r"\bcolza\b"],
    "Girassol": [r"\bsunflowers?\b", r"\bgirassol\b"],
    "Algodão": [r"\bcotton\b", r"\balgod[aã]o\b"],
    "Cana-de-açúcar": [r"\bsugar ?cane\b", r"\bcana-de-a[çc][uú]car\b"],
    "Mandioca": [r"\bcassava\b", r"\bmanioc\b", r"\bmandioca\b"],
    "Batata": [r"(?<!sweet )\bpotato(es)?\b", r"\bbatata\b(?!-doce)"],
    "Batata-doce": [r"\bsweet potato(es)?\b", r"\bbatata-doce\b"],
    "Feijão comum": [r"\bcommon beans?\b", r"\bphaseolus\b", r"\bdry beans?\b", r"\bfeij[aã]o\b(?!-caupi|-de-corda)"],
    "Feijão-caupi": [r"\bcowpeas?\b", r"\bvigna unguiculata\b", r"\bcaupi\b", r"\bfeij[aã]o-de-corda\b"],
    "Amendoim": [r"\bgroundnuts?\b", r"\bpeanuts?\b", r"\bamendoim\b"],
    "Grão-de-bico": [r"\bchickpeas?\b"],
    "Lentilha": [r"\blentils?\b"],
    "Ervilha": [r"\bfield peas?\b", r"\bpeas\b", r"\bervilha\b"],
    "Fava / feijão-fava": [r"\bfaba beans?\b", r"\bbroad beans?\b", r"\bvicia faba\b", r"\blima beans?\b", r"\bfava\b"],
    "Guandu": [r"\bpigeon ?peas?\b", r"\bcajanus\b", r"\bguandu\b"],
    "Alfafa": [r"\balfalfa\b", r"\blucerne\b"],
    "Trevo": [r"\bclovers?\b"],
    "Ervilhaca (vetch)": [r"\bvetch\b"],
    "Gliricídia": [r"\bgliricidia\b"],
    "Leucena": [r"\bleucaena\b"],
    "Mucuna": [r"\bmucuna\b", r"\bvelvet beans?\b"],
    "Crotalária": [r"\bcrotalaria\b", r"\bsunn hemp\b"],
    "Palma forrageira": [r"\bcactus pear\b", r"\bopuntia\b", r"\bnopalea\b", r"\bpalma forrageira\b"],
    "Caju": [r"\bcashews?\b", r"\bcaju\b"],
    "Banana": [r"\bbananas?\b"],
    "Café": [r"\bcoffee\b", r"\bcaf[eé]\b"],
    "Cacau": [r"\bcocoa\b", r"\bcacao\b"],
    "Mamona": [r"\bcastor\b", r"\bmamona\b"],
    "Gergelim": [r"\bsesame\b", r"\bgergelim\b"],
    "Coco": [r"\bcoconuts?\b"],
    "Melão / frutas irrigadas": [r"\bmelons?\b", r"\bmangoe?s?\b"],
    "Tomate / hortaliças": [r"\btomato(es)?\b", r"\bvegetables?\b"],
    "Capins forrageiros (Urochloa, buffel etc.)": [r"\burochloa\b", r"\bbrachiaria\b", r"\bbuffel\b", r"\bcenchrus\b", r"\bforage grass"],
    "Pastagem (genérico)": [r"\bpastures?\b", r"\bgrasslands?\b"],
    "Plantas de cobertura (genérico)": [r"\bcover crops?\b"],
    "Leguminosas (genérico)": [r"\blegumes?\b", r"\bleguminos"],
}
CEARA = ["Milho", "Feijão-caupi", "Feijão comum", "Mandioca", "Sorgo", "Palma forrageira", "Caju", "Algodão",
         "Fava / feijão-fava", "Guandu", "Gliricídia", "Leucena", "Cana-de-açúcar", "Banana", "Coco", "Melão / frutas irrigadas",
         "Capins forrageiros (Urochloa, buffel etc.)", "Gergelim", "Mamona", "Amendoim", "Milheto"]

pdfs = sorted(ART.glob("*.pdf")) + sorted((ART / "documentos_tecnicos").glob("*.pdf"))
cont = defaultdict(dict)
for f in pdfs:
    try:
        texto = " ".join((p.extract_text() or "") for p in PdfReader(str(f)).pages)
    except Exception as e:
        print("falhou", f.name, type(e).__name__)
        continue
    texto = re.sub(r"\s+", " ", texto.lower())
    for c, pads in CULTURAS.items():
        n = sum(len(re.findall(p, texto)) for p in pads)
        if n:
            cont[c][f.name] = n
print(f"{len(pdfs)} PDFs lidos")

linhas = []
for c in CULTURAS:
    d = cont.get(c, {})
    cita = {k: v for k, v in d.items() if v >= 3}
    foco = {k: v for k, v in d.items() if v >= 15}
    top = sorted(cita.items(), key=lambda x: -x[1])[:4]
    linhas.append({"cultura": c, "artigos_que_citam": len(cita), "artigos_com_foco": len(foco),
                   "ceara": "sim" if c in CEARA else "", "principais": "; ".join(f"{k.rsplit('.', 1)[0][:70]} ({v})" for k, v in top)})
linhas.sort(key=lambda x: (-x["artigos_que_citam"], x["cultura"]))
with open(PROJ / "pesquisa" / "culturas_nos_artigos.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
    w.writeheader()
    w.writerows(linhas)
for l in linhas:
    print(f"{l['cultura']:45s} cita={l['artigos_que_citam']:3d} foco={l['artigos_com_foco']:3d} {l['ceara']:3s} | {l['principais'][:150]}")
