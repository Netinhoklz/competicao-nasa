"""Engenheiro de viabilidade: o 'momento uau' (replay 2012) é calculável com o PAM? E o modo global offline?
Só leitura."""
import sys, os
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import pandas as pd
import numpy as np

D = "E:/campeonato-nasa/dados"
p = pd.read_parquet(os.path.join(D, "derivados", "ibge_pam_mun_anual.parquet"))
prods = {"Milho (em grão)": "milho", "Feijão (em grão)": "feijao", "Mandioca": "mandioca"}
p = p[p["produto"].isin(prods) & (p["ano"].between(1998, 2025))].copy()
p["c"] = p["produto"].map(prods)
p["cod"] = p["cod_local"].astype(str)

A = p.pivot_table(index=["cod", "ano"], columns="c", values="area_plantada_ha", aggfunc="sum")
nomes = p.drop_duplicates("cod").set_index("cod")["local"]

print("## 1. Municípios com área plantada > 0 nas 3 culturas, por ano crítico")
for ano in [1998, 2012, 2016]:
    a = A.xs(ano, level="ano")
    ok = (a[["milho", "feijao", "mandioca"]] > 0).all(axis=1)
    print(f" {ano}: {int(ok.sum())} de {len(a)} municípios")

print("\n## 2. Cidades de demo citadas (área plantada ha: milho/feijão/mandioca)")
for nome in ["Quixadá", "Tauá", "Iguatu"]:
    cods = [c for c, n in nomes.items() if n.startswith(nome + " ")]
    for c in cods:
        sub = A.xs(c, level="cod")
        print(f" {nomes[c]} ({c}):")
        for ano in [1998, 2012, 2016]:
            if ano in sub.index:
                r = sub.loc[ano]
                print(f"   {ano}: milho {r.get('milho', np.nan):.0f} | feijão {r.get('feijao', np.nan):.0f} | mandioca {r.get('mandioca', np.nan):.0f}")

print("\n## 3. Mandioca: fração de anos com rendimento idêntico ao ano anterior (Quixadá, Tauá, Iguatu)")
R = p.pivot_table(index=["cod", "ano"], columns="c", values="rendimento_kg_ha", aggfunc="mean")
for nome in ["Quixadá", "Tauá", "Iguatu"]:
    for c in [c for c, n in nomes.items() if n.startswith(nome + " ")]:
        s = R.xs(c, level="cod")["mandioca"].dropna()
        s = s[s > 0]
        rep = (s.diff() == 0).sum()
        print(f" {nomes[c]}: {rep} repetições em {len(s)} anos; valores únicos {s.nunique()}")

print("\n## 4. POWER global offline")
g = pd.read_parquet(os.path.join(D, "power", "power_global_amostra.parquet"))
print(" forma:", g.shape, "| colunas:", list(g.columns)[:15])
for c in g.columns:
    if "data" in c.lower() or "date" in c.lower() or c.lower() in ("ano", "mes"):
        print(f"  {c}: {g[c].min()} -> {g[c].max()}")
    if c.lower() in ("ponto", "nome", "local", "id", "parametro", "variavel"):
        u = g[c].unique()
        print(f"  {c}: {len(u)} únicos; ex.: {list(u[:10])}")
