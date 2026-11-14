"""Baixa os artigos citados no estudo (versoes legais de acesso aberto) para a pasta artigos/ e gera o indice.

Fontes do PDF, em ordem: OpenAlex (best_oa_location e demais locations), Semantic Scholar (openAccessPdf),
Europe PMC e arXiv. Artigo sem versao aberta fica no indice como "acesso fechado" com o DOI.
Nada de fontes piratas. Os PDFs nao vao para o git (.gitignore); so o indice.
"""
import csv
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
DEST = PROJ / "artigos"
DEST.mkdir(exist_ok=True)
FONTES_TEXTO = sorted((PROJ / "pesquisa").glob("*.md")) + sorted((PROJ / "proposta").glob("*.md"))
EXTRAS_DOI = ["10.1088/1748-9326/ae0f45"]  # Kluger et al. 2025 (ERL); arXiv 2506.02384 como alternativa
EXTRAS_TITULO = ["Continuous Corn and Soybean Yield Penalties across Hundreds of Thousands of Fields"]  # Seifert et al. 2017
DOCS_TECNICOS = {  # documentos tecnicos citados (PDF direto)
    "IMERG_V07_ATBD": "https://gpm.nasa.gov/sites/default/files/2023-07/IMERG_V07_ATBD_final_230712.pdf",
    "MCD64_User_Guide_V61": "https://lpdaac.usgs.gov/documents/1006/MCD64_User_Guide_V61.pdf",
    "ATBD_MapBiomas_Fogo_C5": "https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2026/07/ATBD-MapBiomas-Fogo-Colecao-5.pdf",
    "ZARC_Embrapa_2021": "https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1136438/1/PL-ZARC-2021.pdf",
    "Seifert_2017_AgronJ_continuous_corn_soy": "https://mssoy.org/sites/default/files/documents/seifert-et-al-agron-j-109-2017.pdf",
}
ALT_PDF = {"10.1088/1748-9326/ae0f45": ["https://arxiv.org/pdf/2506.02384"]}

s = sessao_http(retries=2)
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
s.headers["Accept"] = "application/pdf,text/html;q=0.9,*/*;q=0.8"


def limpar_doi(d):
    d = d.strip().rstrip(".:,;)]*`'\"")
    d = re.sub(r"(\*\*|\]|\)).*$", "", d)
    return d.lower()


def onde_citado():
    mapa = {}
    for f in FONTES_TEXTO:
        for d in re.findall(r"10\.\d{4,9}/[^\s\]\)>\"'|,;]+", f.read_text(encoding="utf-8", errors="ignore")):
            mapa.setdefault(limpar_doi(d), set()).add(f.name)
    for d in EXTRAS_DOI:
        mapa.setdefault(d, set()).add("artigo_ancora_objetivo.md")
    return mapa


def nome_arquivo(meta, doi):
    ano = meta.get("publication_year") or "s-d"
    aut = (meta.get("authorships") or [{}])[0].get("author", {}).get("display_name", "") if meta.get("authorships") else ""
    sobrenome = aut.split()[-1] if aut else "autor"
    tit = meta.get("title") or doi
    base = f"{ano}_{sobrenome}_{' '.join(tit.split()[:7])}"
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9_-]+", "_", base).strip("_")[:110] + ".pdf"


def eh_pdf(conteudo):
    return conteudo[:5] == b"%PDF-" and len(conteudo) > 20_000


def tentar(url):
    try:
        r = s.get(url, timeout=90, allow_redirects=True)
        if r.status_code == 200 and eh_pdf(r.content):
            return r.content
    except Exception:
        pass
    return None


def openalex(doi):
    r = s.get(f"https://api.openalex.org/works/https://doi.org/{doi}", timeout=60)
    return r.json() if r.ok else None


def openalex_titulo(titulo):
    r = s.get("https://api.openalex.org/works", params={"search": titulo, "per-page": 1}, timeout=60)
    res = r.json().get("results", []) if r.ok else []
    return res[0] if res else None


def candidatos(meta, doi):
    urls = list(ALT_PDF.get(doi, []))
    if meta:
        bo = meta.get("best_oa_location") or {}
        urls += [bo.get("pdf_url")]
        for loc in meta.get("locations") or []:
            urls.append(loc.get("pdf_url"))
        ids = meta.get("ids") or {}
        if ids.get("pmcid"):
            pmc = ids["pmcid"].rsplit("/", 1)[-1]
            urls.append(f"https://europepmc.org/articles/{pmc}?pdf=render")
        for loc in meta.get("locations") or []:
            lp = loc.get("landing_page_url") or ""
            m = re.search(r"arxiv\.org/abs/([\w.]+)", lp)
            if m:
                urls.append(f"https://arxiv.org/pdf/{m.group(1)}")
    try:
        ss = s.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}", params={"fields": "openAccessPdf"}, timeout=40)
        if ss.ok and (ss.json().get("openAccessPdf") or {}).get("url"):
            urls.append(ss.json()["openAccessPdf"]["url"])
    except Exception:
        pass
    vistos, out = set(), []
    for u in urls:
        if u and u not in vistos:
            vistos.add(u)
            out.append(u)
    return out


def processar(doi, citado_em):
    time.sleep(0.3)
    meta = openalex(doi)
    linha = {"doi": doi, "citado_em": "; ".join(sorted(citado_em)), "titulo": "", "primeiro_autor": "", "ano": "",
             "revista": "", "tipo": "", "acesso_aberto": "", "licenca": "", "status": "", "arquivo": "", "fonte_pdf": ""}
    if meta:
        aut = meta.get("authorships") or []
        pl = meta.get("primary_location") or {}
        linha.update({"titulo": meta.get("title") or "", "ano": meta.get("publication_year") or "",
                      "primeiro_autor": (aut[0]["author"]["display_name"] + (" et al." if len(aut) > 1 else "")) if aut else "",
                      "revista": ((pl.get("source") or {}).get("display_name")) or "", "tipo": meta.get("type") or "",
                      "acesso_aberto": (meta.get("open_access") or {}).get("oa_status", ""),
                      "licenca": ((meta.get("best_oa_location") or {}).get("license")) or ""})
    if linha["tipo"] in ("dataset",):
        linha["status"] = "dataset (não é artigo)"
        return linha
    nome = nome_arquivo(meta or {}, doi)
    alvo = DEST / nome
    if alvo.exists() and alvo.stat().st_size > 20_000:
        linha.update(status="baixado", arquivo=nome, fonte_pdf="(já existia)")
        return linha
    for u in candidatos(meta, doi):
        c = tentar(u)
        if c:
            alvo.write_bytes(c)
            linha.update(status="baixado", arquivo=nome, fonte_pdf=u)
            return linha
    linha["status"] = "acesso fechado / sem PDF aberto" if linha["acesso_aberto"] in ("closed", "") else "PDF aberto bloqueado pelo site (abrir pelo DOI)"
    return linha


def main():
    mapa = onde_citado()
    dois = sorted(d for d in mapa if re.match(r"^10\.\d{4,9}/\S+$", d))
    print(f"{len(dois)} DOIs para processar", flush=True)
    with ThreadPoolExecutor(4) as ex:
        linhas = list(ex.map(lambda d: processar(d, mapa[d]), dois))
    for t in EXTRAS_TITULO:
        meta = openalex_titulo(t)
        if meta and meta.get("doi"):
            d = meta["doi"].replace("https://doi.org/", "").lower()
            if d not in dois:
                linhas.append(processar(d, {"artigo_ancora_objetivo.md (busca por título)"}))
    tec = DEST / "documentos_tecnicos"
    tec.mkdir(exist_ok=True)
    for nome, url in DOCS_TECNICOS.items():
        c = tentar(url)
        ok = bool(c)
        if ok:
            (tec / f"{nome}.pdf").write_bytes(c)
        linhas.append({"doi": "", "citado_em": "artigos_e_datasets.md / artigo_ancora_objetivo.md", "titulo": nome, "primeiro_autor": "",
                       "ano": "", "revista": "documento técnico", "tipo": "documento técnico", "acesso_aberto": "aberto",
                       "licenca": "", "status": "baixado" if ok else "falhou", "arquivo": f"documentos_tecnicos/{nome}.pdf" if ok else "",
                       "fonte_pdf": url})
    escrever_indice(linhas)


def escrever_indice(linhas):
    campos = list(linhas[0].keys())
    with open(DEST / "indice.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    cont = {}
    for l in linhas:
        cont[l["status"]] = cont.get(l["status"], 0) + 1
    md = ["# Artigos do estudo", "",
          "PDFs das versões **legais de acesso aberto** dos artigos citados no estudo (revisão de literatura, artigo-âncora e"
          " proposta). Artigos de acesso fechado ficam listados com o DOI. Os PDFs não vão para o GitHub; só este índice e o `indice.csv`.",
          "", "| Situação | Quantidade |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(cont.items(), key=lambda x: -x[1])] + [
          "", "| Ano | Primeiro autor | Título | Revista | DOI | Situação | Arquivo |", "|---|---|---|---|---|---|---|"]
    for l in sorted(linhas, key=lambda x: (str(x["ano"]), x["primeiro_autor"])):
        tit = (l["titulo"] or "").replace("|", "/")[:120]
        doi = f"[{l['doi']}](https://doi.org/{l['doi']})" if l["doi"] else ""
        arq = f"[{l['arquivo']}]({l['arquivo']})" if l["arquivo"] else ""
        md.append(f"| {l['ano']} | {l['primeiro_autor']} | {tit} | {l['revista']} | {doi} | {l['status']} | {arq} |")
    (DEST / "INDICE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(cont)


if __name__ == "__main__":
    main()
