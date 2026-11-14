"""Pesquisador de IA - complemento: o que o ONI de out-dez diz sobre o RENDIMENTO (nao so a chuva) por cultura?
Anos com ONI out-dez >= +1 (El Nino moderado/forte antes da quadra) x demais. Rendimento efetivo (area plantada),
anomalia vs mediana municipal de +-14 anos (saidas/anom_*_j14.parquet) e indice de valor (y / mediana) p/ mandioca e caju.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
ind["data"] = pd.to_datetime(ind["data"])
oni = ind[ind.variavel == "ONI"].set_index("data").valor
ond = {a: oni[f"{a-1}-10-01":f"{a-1}-12-31"].mean() for a in range(1998, 2026)}
nino = [a for a, v in ond.items() if v >= 1.0]
nina = [a for a, v in ond.items() if v <= -1.0]
print("anos com ONI out-dez >= +1:", nino, "| <= -1:", nina)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.cod_local.str.startswith("23") & pam.ano.between(1998, 2025)]
for nome, pref in [("milho", "Milho (em gr"), ("feijao", "Feij"), ("mandioca", "Mandioca"), ("caju", "Castanha de caju")]:
    x = pam[pam.produto.str.startswith(pref)].copy()
    x = x[x.groupby("cod_local").area_plantada_ha.transform("median") >= 100]
    x["y"] = np.where(x.area_plantada_ha > 0, x.producao_t * 1000 / x.area_plantada_ha, np.nan)
    x["idx"] = x.y / x.groupby("cod_local").y.transform("median")
    e = x.groupby("ano").idx.median()
    a, b = e[e.index.isin(nino)], e[~e.index.isin(nino) & ~e.index.isin(nina)]
    c = e[e.index.isin(nina)]
    r = stats.spearmanr([ond[k] for k in e.index], e.values)
    print(f"  {nome:9s} indice mediano (1 = ano mediano): El Nino {a.median():.2f} | neutro {b.median():.2f} | "
          f"La Nina {c.median():.2f} | rho(ONI, indice estadual) = {r.statistic:+.2f} (p={r.pvalue:.2f}, n={len(e)}) | "
          f"P(indice<0,5) El Nino {np.mean(a < 0.5):.0%} vs outros {np.mean(e[~e.index.isin(nino)] < 0.5):.0%}")
