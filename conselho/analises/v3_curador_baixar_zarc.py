"""Curador de bases (v3): baixa a Tabua de Risco oficial do ZARC (MAPA, dados abertos CKAN) em fluxo e guarda so as
linhas do Ceara. Fonte: https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-dc8ff323b96f
Colunas dec1..dec36 = decendios do ano (risco 20, 30 ou 40%; 0 = nao indicado).
Saida: E:/campeonato-nasa/dados/complementares/zarc/tabua_risco_ce_<safra>.csv + MANIFESTO.json
Uso: python -I v3_curador_baixar_zarc.py
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

BASE = DADOS / "complementares" / "zarc"
RAIZ_CKAN = "https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-dc8ff323b96f/resource/"
ARQ = {
    "2025-2026": "f9d597f9-0fee-47eb-9344-8642274ca9da/download/dados-abertos-tabua-de-risco-safra-2025-2026.csv",
    "2026-2027": "139e5a60-1f43-4cc8-aeab-a35dbbf816c0/download/dados-abertos-tabua-de-risco-safra-2026-2027.csv",
    "2016-2017": "0bb6188d-8b6a-4ab6-9d77-2e88dc889313/download/dados-abertos-tabua-de-risco-safra-2016-2017.csv",
}
DIC = "bebb0ebb-bc75-460c-b900-a7a1ebd87bee/download/dicionario-de-dados-tabua-de-risco-2026.pdf"


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    s = sessao_http()
    baixar(RAIZ_CKAN + DIC, BASE / "dicionario-de-dados-tabua-de-risco-2026.pdf", s)
    res = {}
    for safra, rel in ARQ.items():
        t0 = time.time()
        n_tot = n_ce = 0
        mb = 0
        with s.get(RAIZ_CKAN + rel, stream=True, timeout=180) as r, \
                open(BASE / f"tabua_risco_ce_{safra}.csv", "w", encoding="utf-8") as f:
            r.raise_for_status()
            r.encoding = "utf-8-sig"
            cab = None
            for linha in r.iter_lines(decode_unicode=True):
                if linha is None:
                    continue
                mb += len(linha) + 1
                if cab is None:
                    cab = linha.lstrip("\ufeff")
                    f.write(cab + "\n")
                    iuf = cab.split(";").index("UF")
                    continue
                n_tot += 1
                p = linha.split(";")
                if len(p) > iuf and p[iuf] == "CE":
                    f.write(linha + "\n")
                    n_ce += 1
        res[safra] = {"linhas_brasil": n_tot, "linhas_ce": n_ce, "mb_lidos": round(mb / 1e6, 1)}
        print(safra, res[safra], f"{time.time() - t0:.0f}s", flush=True)
    registrar_manifesto("complementares/zarc", {
        "fonte": "MAPA, Zoneamento Agricola de Risco Climatico (Zarc) - Tabua de Risco, dados abertos",
        "url": "https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-dc8ff323b96f",
        "recorte": "so UF = CE (filtro em fluxo; o arquivo nacional nao foi gravado)",
        "safras": res,
        "script": "conselho/analises/v3_curador_baixar_zarc.py",
    }, base=BASE)


if __name__ == "__main__":
    main()
