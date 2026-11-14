"""Culturas citadas nos RESUMOS (OpenAlex) de todos os artigos do indice (artigos/indice.csv), baixados ou nao."""
import csv
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402
from culturas_nos_artigos import CULTURAS  # noqa: E402  (reusa o dicionario)

sys.stdout.reconfigure(encoding="utf-8")
PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
s = sessao_http(retries=2)
with open(PROJ / "artigos" / "indice.csv", encoding="utf-8-sig") as f:
    itens = [l for l in csv.DictReader(f) if l["doi"] and not l["status"].startswith("dataset")]
por_cultura = {c: [] for c in CULTURAS}
lidos = 0
for l in itens:
    time.sleep(0.15)
    r = s.get(f"https://api.openalex.org/works/https://doi.org/{l['doi']}", timeout=60)
    if not r.ok:
        continue
    o = r.json()
    inv = o.get("abstract_inverted_index") or {}
    resumo = " ".join(w for _, w in sorted((p, w) for w, ps in inv.items() for p in ps))
    texto = ((o.get("title") or "") + " " + resumo).lower()
    if not resumo:
        continue
    lidos += 1
    rot = f"{(o.get('authorships') or [{}])[0].get('author', {}).get('display_name', '?').split()[-1]} {o.get('publication_year')}"
    for c, pads in CULTURAS.items():
        if any(re.search(p, texto) for p in pads):
            por_cultura[c].append(rot)
print(f"{len(itens)} artigos no índice; {lidos} com resumo no OpenAlex")
linhas = sorted(((c, len(v), ", ".join(v[:8])) for c, v in por_cultura.items()), key=lambda x: -x[1])
with open(PROJ / "pesquisa" / "culturas_nos_resumos.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["cultura", "artigos_com_a_cultura_no_titulo_ou_resumo", "exemplos"])
    w.writerows(linhas)
for c, n, ex in linhas:
    print(f"{c:45s} {n:3d} | {ex[:140]}")
