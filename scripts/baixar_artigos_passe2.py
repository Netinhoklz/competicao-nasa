"""Segundo passe: corrige DOIs com parenteses e tenta o PDF oficial pela pagina do artigo (citation_pdf_url).

Somente links oficiais da editora/repositorio (o que a propria pagina declara). Atualiza indice.csv e INDICE.md.
"""
import csv
import re
import sys
import time

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import baixar_artigos as BA  # noqa: E402

CORRIGIR = {
    "10.1016/0167-8809(85": "10.1016/0167-8809(85)90016-7",
    "10.1016/0273-1177(95": "10.1016/0273-1177(95)00079-t",
    "10.1016/s0167-8809(97": "10.1016/s0167-8809(97)00073-x",
    "10.1175/1520-0442(1996": "10.1175/1520-0442(1996)009<2464:vosstw>2.0.co;2",
    "10.1175/1520-0469(1981": "10.1175/1520-0469(1981)038<2653:otdodi>2.0.co;2",
}
s = BA.s


def pdf_pela_pagina(doi):
    """Abre a pagina do artigo pelo DOI e segue o citation_pdf_url declarado pela editora."""
    try:
        r = s.get(f"https://doi.org/{doi}", timeout=60, allow_redirects=True, headers={"Accept": "text/html"})
    except Exception:
        return None, None
    pagina = r.url
    urls = re.findall(r'<meta[^>]+name="citation_pdf_url"[^>]+content="([^"]+)"', r.text or "")
    urls += re.findall(r'<meta[^>]+content="([^"]+)"[^>]+name="citation_pdf_url"', r.text or "")
    if "link.springer.com" in pagina:
        urls.append(f"https://link.springer.com/content/pdf/{doi}.pdf")
    if "onlinelibrary.wiley.com" in pagina or "wiley.com" in pagina:
        urls.append(f"https://onlinelibrary.wiley.com/doi/pdfdirect/{doi}")
    for u in urls:
        try:
            p = s.get(u, timeout=90, allow_redirects=True, headers={"Referer": pagina, "Accept": "application/pdf"})
            if p.status_code == 200 and BA.eh_pdf(p.content):
                return p.content, u
        except Exception:
            pass
    return None, None


def main():
    with open(BA.DEST / "indice.csv", encoding="utf-8-sig") as f:
        linhas = [l for l in csv.DictReader(f) if l["doi"] not in CORRIGIR]  # tira os DOIs truncados
    for cheio in CORRIGIR.values():  # e processa as versoes completas
        linhas.append(BA.processar(cheio, {"artigos_e_datasets.md"}))
    novos = 0
    for l in linhas:
        if l["status"] == "baixado" or l["status"].startswith("dataset") or not l["doi"]:
            continue
        time.sleep(0.5)
        c, u = pdf_pela_pagina(l["doi"])
        if c:
            meta = BA.openalex(l["doi"]) or {}
            nome = BA.nome_arquivo(meta, l["doi"])
            (BA.DEST / nome).write_bytes(c)
            l.update(status="baixado", arquivo=nome, fonte_pdf=u)
            novos += 1
            print("   +", nome, flush=True)
    BA.escrever_indice(linhas)
    print("novos no passe 2:", novos)


if __name__ == "__main__":
    main()
