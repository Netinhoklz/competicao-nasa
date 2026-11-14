"""Pesquisador de IA, rodada 2: o ensaio de downscaling do SMAP (sr_fundacao) sobrevive a deriva da LST do MODIS Terra?

O cetico mostrou que a LST diurna do Terra deriva cerca de -4,6 C em 2024-2026 (horario de passagem). O ensaio do
especialista em sensoriamento remoto usa a anomalia de LST diurna como preditor (R2 0,44 fora do ano). Teste:
(1) R2 do modelo linear de 4 anomalias por periodo (2000-2019 x 2020-2026), (2) sem a LST diurna,
(3) com anomalias ESPACIAIS (cada variavel menos a media das celulas no mesmo mes), que cancelam deriva comum.
Alvo: anomalia de umidade 0-10 cm do GLDAS (provisorio, ate o SMAP L4 chegar). Validacao: ano inteiro fora.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

AQUI = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
D = pd.read_parquet(AQUI + "sr_fundacao_painel_celula_mes.parquet")
D = D.dropna(subset=["a_sm0_10", "a_lst_dia", "a_ndvi", "a_lst_noite", "a_amp_termica"]).reset_index(drop=True)
print(f"painel: {len(D)} celula-mes, {D.ano.min()}-{D.ano.max()}")
# deriva comum: media mensal da anomalia de LST diurna por ano
print("media da anomalia de LST diurna (fev-mai) por ano, ultimos anos:")
print(D[D.mes.isin([2, 3, 4, 5])].groupby("ano").a_lst_dia.mean().loc[2016:].round(2).to_string())

y = D.a_sm0_10.values
anos = D.ano.values
for v in ["a_lst_dia", "a_ndvi", "a_lst_noite", "a_amp_termica", "a_sm0_10"]:
    D[v + "_esp"] = D[v] - D.groupby("data")[v].transform("mean")
conj = {"4 anomalias": ["a_lst_dia", "a_ndvi", "a_lst_noite", "a_amp_termica"],
        "sem LST diurna": ["a_ndvi", "a_lst_noite"],
        "4 anomalias espaciais (alvo espacial)": ["a_lst_dia_esp", "a_ndvi_esp", "a_lst_noite_esp", "a_amp_termica_esp"]}
for nome, cols in conj.items():
    X = D[cols].values
    alvo = D.a_sm0_10_esp.values if "espaciais" in nome else y
    pred = np.zeros(len(D))
    for a in np.unique(anos):
        te = anos == a
        pred[te] = LinearRegression().fit(X[~te], alvo[~te]).predict(X[te])
    r = {"todos": r2_score(alvo, pred)}
    for lo, hi in [(2000, 2019), (2020, 2026), (2022, 2026)]:
        m = (anos >= lo) & (anos <= hi)
        r[f"{lo}-{hi}"] = r2_score(alvo[m], pred[m])
    mq = D.mes.isin([2, 3, 4, 5]).values
    r["fev-mai"] = r2_score(alvo[mq], pred[mq])
    print(f"{nome:42s} " + "  ".join(f"{k}={v:.3f}" for k, v in r.items()))
