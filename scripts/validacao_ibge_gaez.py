"""Consulta pontual ao IBGE/SIDRA (PAM, tabela 1612) para VALIDAR o GAEZ no Ceara.
Nao e o download da base IBGE PAM (municipal) — so a serie estadual do Ceara, 1974-2024.
Saida: dados/gaez/validacao_ibge_pam_ce_1974_2024.csv
"""
import sys
import json

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
G = DADOS / "gaez"
s = sessao_http()
anos = ",".join(str(a) for a in range(1974, 2025))
# 2711 milho, 2702 feijao, 2708 mandioca, 2689 algodao herbaceo, 2713 soja, 2695 arroz, 2716 sorgo
url = (f"https://apisidra.ibge.gov.br/values/t/1612/n3/23/v/112,216,214/p/{anos}"
       f"/c81/2711,2702,2708,2689,2713,2716/f/n")
d = s.get(url, timeout=180).json()
df = pd.DataFrame(d[1:])
df.columns = [d[0][c] for c in df.columns]
df = df.rename(columns={"Produto das lavouras temporárias": "produto", "Variável": "variavel", "Ano": "ano",
                        "Valor": "valor", "Unidade de Medida": "unidade"})
df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
df["ano"] = df["ano"].astype(int)
df = df[["produto", "variavel", "unidade", "ano", "valor"]]
df.to_csv(G / "validacao_ibge_pam_ce_1974_2024.csv", index=False, encoding="utf-8")
print(df.groupby(["produto", "variavel"])["ano"].agg(["min", "max", "count"]))
registrar_manifesto("gaez", {"validacao_externa": {
    "arquivo": str(G / "validacao_ibge_pam_ce_1974_2024.csv"),
    "fonte": "IBGE/SIDRA tabela 1612 (PAM), nivel UF=Ceara, 1974-2024", "url": url}})
