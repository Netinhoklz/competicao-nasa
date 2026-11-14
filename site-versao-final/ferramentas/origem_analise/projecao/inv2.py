import pandas as pd, numpy as np, importlib
for m in ["statsmodels", "sklearn", "scipy"]:
    try:
        importlib.import_module(m); print(m, "ok")
    except Exception as e:
        print(m, "FALTA", e)
P = pd.read_parquet("E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet")
print(P.produto.value_counts().to_string())
v = P[P.area_plantada_ha > 0]
g = v.groupby("produto").agg(munis=("cod_mun", "nunique"), linhas=("ano", "size"), a0=("ano", "min"), a1=("ano", "max"),
                             perda_med=("perda_area", "median"), rend=("rend_plantado_kg_ha", "median"), preco=("preco_r2025_kg", "median"))
print(g.sort_values("linhas", ascending=False).to_string())
# anos por municipio-cultura
n = v.groupby(["produto", "cod_mun"]).size()
print((n >= 20).groupby("produto").sum().sort_values().to_string())
print(P[P.produto == "Milho"].head(3).T)
print(P.columns.tolist())
import json
print(open("E:/campeonato-nasa/dados/financeiro/MANIFESTO.json", encoding="utf8").read()[:2500])
L = pd.read_parquet("c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados/ibge_ne_lspa_uf_mensal.parquet")
print(L.variavel.unique(), L.produto.unique())
print(L[(L.uf == "CE") & (L.produto.str.startswith("Milho")) & (L.variavel == "rendimento_medio")].tail(14).to_string())
Q = pd.read_parquet("c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados/ibge_ne_pam_mun_anual.parquet")
print(Q.produto.unique()[:80])
