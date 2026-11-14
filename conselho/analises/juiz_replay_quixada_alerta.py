"""Juiz (banca adversaria): no replay da demo, o alerta "chuva desde 1/jan < 75% do normal" acende em Quixada?
Regra do rascunho (M3/P4): % do normal da chuva acumulada desde 1/jan ate a data do portao, normal = mediana 1998-2025
do proprio municipio (aqui sem deixar o ano de fora: e so um retrato descritivo do replay, nao uma metrica de habilidade).
Tambem: em quantos municipios do CE o alerta acende em cada portao em 1998, 2012 e 2016 (para comparar com a quebra).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from comum import DERIV

A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
cod = str(pam[pam.local.str.startswith("Quixad")].cod_local.iloc[0])
print("Quixada cod:", cod, "| em chuva:", cod in chuva.columns)

PORTOES = {"31/jan": (1, 31), "28/fev": (2, 28), "19/mar": (3, 19), "31/mar": (3, 31), "30/abr": (4, 30)}
anos = range(1998, 2026)
lin = []
for nome, (m, d) in PORTOES.items():
    acum = {}
    for a in anos:
        s = chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"]
        acum[a] = s.sum()
    acum = pd.DataFrame(acum).T  # ano x municipio
    pct = acum / acum.median()
    for a in [1998, 2012, 2016, 2024]:
        lin.append({"portao": nome, "ano": a, "Quixada_pct": round(pct.loc[a, cod], 2),
                    "Quixada_alerta": bool(pct.loc[a, cod] < 0.75),
                    "frac_mun_alerta_CE": round((pct.loc[a] < 0.75).mean(), 2)})
T = pd.DataFrame(lin)
print(T.pivot(index="ano", columns="portao", values="Quixada_pct")[list(PORTOES)].to_string())
print()
print(T.pivot(index="ano", columns="portao", values="frac_mun_alerta_CE")[list(PORTOES)].to_string())
