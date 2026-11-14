"""Pesquisador de IA, rodada 2: o ganho da regra R6 (agronomo) se concentra em anos em que o simulador concorda com o PAM?
Compara, por ano, a fracao de municipios com quebra observada do milho (PAM, rendimento por area plantada <= -50% da
mediana movel; cetico_painel_milho.an_y_plant) com a fracao simulada com ISNA na floracao do milho < 0,5 (regra R1,
agronomo_isna_mun_ano.parquet) e com a fracao 'perde tudo' por regra (saidas/agronomo_regras_semeadura.txt, copiada)."""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np, pandas as pd
from scipy import stats
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
P = pd.read_parquet(A + "cetico_painel_milho.parquet"); P["cod"] = P.cod.astype(int); P["ano"] = P.ano.astype(int)
I = pd.read_parquet(A + "saidas/agronomo_isna_mun_ano.parquet"); I["cod"] = I.cod.astype(int); I["ano"] = I.ano.astype(int)
M = P.merge(I, on=["cod", "ano"])
g = M.groupby("ano").agg(obs_quebra=("an_y_plant", lambda s: (s <= -0.5).mean()),
                         sim_isna_lt05=("isna_flor_milho", lambda s: (s < 0.5).mean()),
                         sim_isna_med=("isna_flor_milho", "median"))
# fracao 'perde tudo' por regra, transcrita da saida do agronomo (anos de seca)
pt = pd.DataFrame({"R1_perde_tudo": {2010: .89, 2012: .16, 2013: .39, 2016: .56},
                   "R6_perde_tudo": {2010: .11, 2012: .21, 2013: .04, 2016: .22}})
print(g.join(pt).round(2).to_string())
print("Pearson anual obs x sim(ISNA<0,5):", round(stats.pearsonr(g.obs_quebra, g.sim_isna_lt05).statistic, 2),
      "| Spearman:", round(stats.spearmanr(g.obs_quebra, g.sim_isna_lt05).statistic, 2))
