"""Confere metadados (Crossref + OpenAlex) e o resumo oficial de uma lista de DOIs; salva em pesquisa/verificacao_meta_analises.json."""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
DOIS = {
    "Mudare 2025 Nat Commun": "10.1038/s41467-025-64567-9",
    "Raveloaritiana 2026 Nat Commun": "10.1038/s41467-025-67757-7",
    "Zhao 2022 Nat Commun": "10.1038/s41467-022-32464-0",
    "Beillouin 2021 GCB": "10.1111/gcb.15747",
    "Rasmussen 2024 Science": "10.1126/science.adj1914",
    "MacLaren 2022 Nat Sustain": "10.1038/s41893-022-00911-x",
    "Smith 2023 Commun Earth Environ": "10.1038/s43247-023-00746-0",
}
s = sessao_http(retries=2)
saida = {}
for rot, doi in DOIS.items():
    cr = s.get(f"https://api.crossref.org/works/{doi}", timeout=60)
    m = cr.json()["message"] if cr.ok else {}
    oa = s.get(f"https://api.openalex.org/works/https://doi.org/{doi}", timeout=60)
    o = oa.json() if oa.ok else {}
    inv = o.get("abstract_inverted_index") or {}
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    resumo = " ".join(w for _, w in pos)
    aut = m.get("author", [])
    saida[rot] = {
        "doi": doi, "crossref_ok": cr.ok, "titulo": (m.get("title") or [""])[0],
        "autores": ", ".join(f"{a.get('given', '')} {a.get('family', '')}".strip() for a in aut[:6]) + (" et al." if len(aut) > 6 else ""),
        "n_autores": len(aut), "revista": (m.get("container-title") or [""])[0],
        "volume": m.get("volume"), "artigo": m.get("article-number") or m.get("page"),
        "data": m.get("published", {}).get("date-parts", [[None]])[0], "citacoes_crossref": m.get("is-referenced-by-count"),
        "acesso_aberto": (o.get("open_access") or {}).get("oa_status"), "pdf_aberto": (o.get("best_oa_location") or {}).get("pdf_url"),
        "pmcid": (o.get("ids") or {}).get("pmcid"), "resumo": resumo,
    }
    print(f"== {rot}: crossref={cr.ok} | {saida[rot]['titulo'][:90]} | {saida[rot]['revista']} {saida[rot]['volume']}:{saida[rot]['artigo']} | "
          f"{saida[rot]['data']} | {saida[rot]['n_autores']} autores | cit {saida[rot]['citacoes_crossref']} | OA {saida[rot]['acesso_aberto']}")
    print("   autores:", saida[rot]["autores"])
    print("   RESUMO:", resumo[:1800] if resumo else "(sem resumo no OpenAlex)")
Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\pesquisa\verificacao_meta_analises.json").write_text(
    json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
