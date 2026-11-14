"""Classifica os artigos do indice pelo grau de ligacao com o Nordeste brasileiro (titulo/resumo OpenAlex + texto do PDF local).

Niveis: 1 = estudo feito no Nordeste/semiarido brasileiro (local no titulo/resumo); 2 = Brasil incluindo o Nordeste ou
o Nordeste aparece bastante no texto completo; 3 = cita o Nordeste de passagem. Saida: pesquisa/artigos_nordeste.csv
"""
import csv
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
NE = (r"northeast(ern)? brazil|nordeste|brazilian semi-?arid|semi-?arid (region of )?brazil|semi-?árido|caatinga|"
      r"\bceará\b|\bceara\b|pernambuco|paraíba|paraiba|rio grande do norte|piauí|piaui|\bbahia\b|sergipe|alagoas|maranhão|maranhao|"
      r"petrolina|juazeiro|sobral|serra talhada|quixadá|quixada|fortaleza|teresina|mossoró|mossoro|funceme|embrapa semi|matopiba|sudene|"
      r"são francisco river|sao francisco river|rio são francisco|polígono das secas")
BR = r"\bbrazil|brasil|brazilian"


def main():
    s = sessao_http(retries=2)
    with open(PROJ / "artigos" / "indice.csv", encoding="utf-8-sig") as f:
        itens = [l for l in csv.DictReader(f) if l["doi"] and not l["status"].startswith("dataset")]
    textos = {}
    try:
        from pypdf import PdfReader
        for l in itens:
            if l["arquivo"]:
                try:
                    textos[l["doi"]] = " ".join((p.extract_text() or "") for p in PdfReader(str(PROJ / "artigos" / l["arquivo"])).pages[:40]).lower()
                except Exception:
                    pass
    except ImportError:
        pass
    linhas = []
    for l in itens:
        time.sleep(0.12)
        r = s.get(f"https://api.openalex.org/works/https://doi.org/{l['doi']}", timeout=60)
        o = r.json() if r.ok else {}
        inv = o.get("abstract_inverted_index") or {}
        resumo = " ".join(w for _, w in sorted((p, w) for w, ps in inv.items() for p in ps))
        tr = f"{o.get('title') or l['titulo']} {resumo}".lower()
        ne_tr = sorted(set(m.group(0) for m in re.finditer(NE, tr)))
        full = textos.get(l["doi"], "")
        n_full = len(re.findall(NE, full))
        br = bool(re.search(BR, tr))
        if ne_tr:
            nivel = 1
        elif (br and n_full >= 3) or n_full >= 10:
            nivel = 2
        elif n_full >= 1 or br:
            nivel = 3
        else:
            continue
        aut = (o.get("authorships") or [{}])[0].get("author", {}).get("display_name", l["primeiro_autor"] or "?")
        linhas.append({"nivel": nivel, "ano": o.get("publication_year") or l["ano"], "primeiro_autor": aut.split()[-1] if aut else "",
                       "titulo": o.get("title") or l["titulo"], "revista": ((o.get("primary_location") or {}).get("source") or {}).get("display_name") or l["revista"],
                       "doi": l["doi"], "marcadores_titulo_resumo": "; ".join(ne_tr), "mencoes_NE_texto_completo": n_full,
                       "pdf_local": l["arquivo"], "status": l["status"], "citacoes": o.get("cited_by_count")})
    linhas.sort(key=lambda x: (x["nivel"], -(x["citacoes"] or 0)))
    with open(PROJ / "pesquisa" / "artigos_nordeste.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    for n in (1, 2, 3):
        sel = [x for x in linhas if x["nivel"] == n]
        print(f"\n===== NÍVEL {n}: {len(sel)} artigos")
        for x in sel:
            print(f"  {x['ano']} {x['primeiro_autor']:14s} | {x['titulo'][:95]} | {x['revista'][:35] if x['revista'] else ''} | cit {x['citacoes']} | "
                  f"{'PDF' if x['pdf_local'] else '-'} | {x['marcadores_titulo_resumo'][:50]} | txt:{x['mencoes_NE_texto_completo']}")


if __name__ == "__main__":
    main()
