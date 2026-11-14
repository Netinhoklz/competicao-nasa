"""Estrategista - numeros da demo para um municipio (Quixada, AOI sertao_central): replay das carteiras 1998-2025."""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import numpy as np, pandas as pd
from comum import DERIV
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
loc = [l for l in pam.local.unique() if l.startswith("Quixad")]
print("local:", loc)
q = pam[(pam.local == loc[0]) & (pam.ano.between(1998, 2025))]
out = {}
for nome, pref in [("milho", "Milho (em"), ("feijao", "Feij"), ("mandioca", "Mandioca"), ("sorgo", "Sorgo")]:
    s = q[q.produto.str.startswith(pref)].set_index("ano")
    out[nome + "_ha"] = s.area_colhida_ha
    r = s.rendimento_kg_ha.where(s.area_colhida_ha >= 10)
    out[nome] = r / r.median()
T = pd.DataFrame(out)
print(T.loc[[1998, 2012, 2013, 2016, 2024]].round(2).to_string())
B = T[["milho", "feijao", "mandioca"]].dropna()
print("anos com as 3 culturas:", len(B))
for k, s in {"milho": B.milho, "milho+feijao": B[["milho", "feijao"]].mean(1), "1/3 cada": B.mean(1)}.items():
    print(f"  {k:14s} pior ano={s.min():.2f} ({int(s.idxmin())})  P10={s.quantile(.1):.2f}  anos<0.5={int((s < 0.5).sum())}")
