"""Acrescenta DOIs a artigos/ (PDF aberto legal) e ao indice; tambem salva o texto completo em HTML/PDF->texto para conferencia.

Uso: python -I baixar_artigos_extra.py <rotulo_citacao> doi1 doi2 ...
Texto completo vai para E:/campeonato-nasa/tmp/textos/<doi_seguro>.txt (so para busca local; nao versionado).
"""
import csv
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import baixar_artigos as BA  # noqa: E402
from baixar_artigos_passe2 import pdf_pela_pagina  # noqa: E402

TEXTOS = Path("E:/campeonato-nasa/tmp/textos")
TEXTOS.mkdir(parents=True, exist_ok=True)
FULLTEXT_HTML = {  # paginas oficiais de texto completo aberto
    "nature": "https://www.nature.com/articles/{suf}",
    "pmc": "https://pmc.ncbi.nlm.nih.gov/articles/{pmc}/",
}


def texto_de_html(t):
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t))


def salvar_texto(doi, meta):
    urls = []
    if doi.startswith("10.1038/"):
        urls.append(FULLTEXT_HTML["nature"].format(suf=doi.split("/", 1)[1]))
    pmc = ((meta or {}).get("ids") or {}).get("pmcid")
    if pmc:
        urls.append(FULLTEXT_HTML["pmc"].format(pmc=pmc.rsplit("/", 1)[-1]))
    for u in urls:
        try:
            r = BA.s.get(u, timeout=90, headers={"Accept": "text/html"})
            if r.ok and len(r.text) > 50_000:
                txt = texto_de_html(r.text)
                (TEXTOS / (re.sub(r"[^A-Za-z0-9]+", "_", doi) + ".txt")).write_text(txt, encoding="utf-8")
                return u, len(txt)
        except Exception:
            pass
    return None, 0


def main(rotulo, dois):
    with open(BA.DEST / "indice.csv", encoding="utf-8-sig") as f:
        linhas = list(csv.DictReader(f))
    existentes = {l["doi"]: l for l in linhas}
    for doi in dois:
        doi = doi.lower()
        if doi in existentes:
            l = existentes[doi]
            l["citado_em"] = "; ".join(sorted(set(l["citado_em"].split("; ")) | {rotulo}))
        else:
            l = BA.processar(doi, {rotulo})
            linhas.append(l)
        if l["status"] != "baixado":
            c, u = pdf_pela_pagina(doi)
            if c:
                nome = BA.nome_arquivo(BA.openalex(doi) or {}, doi)
                (BA.DEST / nome).write_bytes(c)
                l.update(status="baixado", arquivo=nome, fonte_pdf=u)
        fonte, n = salvar_texto(doi, BA.openalex(doi))
        print(f"{doi}: {l['status']} | {l.get('arquivo', '')} | texto: {fonte} ({n} chars)", flush=True)
    BA.escrever_indice(linhas)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
