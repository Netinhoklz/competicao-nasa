"""IBGE PAM (Producao Agricola Municipal) via API SIDRA.

Tabela 1612 (lavouras temporarias) e 1613 (permanentes): municipios do Ceara, ano a ano, 1974->ultimo;
e estados do Nordeste. Saida: dados/ibge_pam/pam_ce_municipios.parquet, pam_ne_estados.parquet
Codigos SIDRA: "-" = zero absoluto; ".." = nao se aplica; "..." = nao disponivel; "X" = sigilo.
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
OUT = pasta("ibge_pam")
CACHE = OUT / "cache_json"
CACHE.mkdir(exist_ok=True)
S = sessao_http(retries=6)
TAB = {1612: ("109,216,214,112,215", "c81"), 1613: ("2313,216,214,112,215", "c82")}
ANOS = range(1974, 2026)


def pedir(url, arq):
    if arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    erro = None
    for t in range(8):
        try:
            r = S.get(url, timeout=300)
            if r.status_code == 200:
                js = r.json()
                arq.write_text(r.text, encoding="utf-8")
                return js
            erro = f"HTTP {r.status_code} {r.text[:200]}"
        except Exception as e:  # conexao interrompida (ChunkedEncodingError etc.)
            erro = repr(e)[:200]
        time.sleep(5 * (t + 1))
    raise RuntimeError(f"{url} -> {erro}")


def para_df(js, tabela):
    cab, linhas = js[0], js[1:]
    df = pd.DataFrame(linhas).rename(columns=cab)
    df["tabela"] = tabela
    return df


def municipios(tabela):
    vars_, cls = TAB[tabela]
    dfs = []

    def ano(a):
        url = (f"https://apisidra.ibge.gov.br/values/t/{tabela}/n6/in%20n3%2023/v/{vars_}/p/{a}/{cls}/all"
               "?formato=json")
        return para_df(pedir(url, CACHE / f"mun_{tabela}_{a}.json"), tabela)

    with ThreadPoolExecutor(3) as ex:
        for df in ex.map(ano, ANOS):
            dfs.append(df)
    print("municipios", tabela, "ok", flush=True)
    return pd.concat(dfs, ignore_index=True)


def estados_ne(tabela):
    vars_, cls = TAB[tabela]
    dfs = []
    for v in vars_.split(","):
        url = (f"https://apisidra.ibge.gov.br/values/t/{tabela}/n3/in%20n2%202/v/{v}/p/all/{cls}/all?formato=json")
        dfs.append(para_df(pedir(url, CACHE / f"ne_{tabela}_{v}.json"), tabela))
    print("estados NE", tabela, "ok", flush=True)
    return pd.concat(dfs, ignore_index=True)


def arrumar(df):
    ren = {}
    for c in df.columns:
        if "Município (Código)" in c or "Unidade da Federação (Código)" in c:
            ren[c] = "cod_local"
        elif c in ("Município", "Unidade da Federação"):
            ren[c] = "local"
        elif c == "Ano":
            ren[c] = "ano"
        elif c == "Variável":
            ren[c] = "variavel"
        elif c == "Unidade de Medida":
            ren[c] = "unidade"
        elif c == "Valor":
            ren[c] = "valor_txt"
        elif c.startswith("Produto das lavouras") and "(Código)" not in c:
            ren[c] = "produto"
        elif c.startswith("Produto das lavouras") and "(Código)" in c:
            ren[c] = "cod_produto"
    df = df.rename(columns=ren)
    manter = ["tabela", "cod_local", "local", "ano", "variavel", "unidade", "produto", "cod_produto", "valor_txt"]
    df = df[[c for c in manter if c in df.columns]].copy()
    df["valor"] = pd.to_numeric(df["valor_txt"].where(~df["valor_txt"].isin(["-"]), "0"), errors="coerce")
    df["ano"] = df["ano"].astype(int)
    df["tipo"] = df["tabela"].map({1612: "temporaria", 1613: "permanente"})
    return df


if __name__ == "__main__":
    t0 = time.time()
    mun = pd.concat([arrumar(municipios(1612)), arrumar(municipios(1613))], ignore_index=True)
    mun.to_parquet(OUT / "pam_ce_municipios.parquet")
    ne = pd.concat([arrumar(estados_ne(1612)), arrumar(estados_ne(1613))], ignore_index=True)
    ne.to_parquet(OUT / "pam_ne_estados.parquet")
    registrar_manifesto("ibge_pam", {
        "fonte": "IBGE - Producao Agricola Municipal (PAM), API SIDRA",
        "url": "https://apisidra.ibge.gov.br/values/t/{1612,1613}/...",
        "recorte": "184 municipios do Ceara (n6 in n3 23) e 9 UFs do Nordeste (n3 in n2 2)",
        "periodo": f"{mun.ano.min()}-{mun.ano.max()}",
        "variaveis": sorted(mun.variavel.unique().tolist()),
        "n_produtos": int(mun.produto.nunique()),
        "linhas": {"municipios": len(mun), "estados_ne": len(ne)},
        "arquivos": {f.name: f.stat().st_size for f in OUT.glob("*.parquet")},
        "minutos": round((time.time() - t0) / 60, 1),
    })
    # o JSON do SIDRA e muito verboso (~1 GB); o parquet guarda tudo
    import shutil
    shutil.rmtree(CACHE, ignore_errors=True)
    print("FIM", len(mun), len(ne), round((time.time() - t0) / 60, 1), "min", flush=True)
