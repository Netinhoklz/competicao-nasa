"""Designer - Analise 1b: curva de habilidade com a medida "% do normal do PROPRIO municipio" (sem ajuste de modelo).

Pergunta: a habilidade baixa antes de abril (designer_calendario_decisao.py, mm brutos) vem da medida? Com o acumulado
desde 1/jan dividido pela mediana do mesmo municipio e da mesma data nos OUTROS anos, qual a AUC por data de decisao?
Inclui o recorte "anos comuns" (sem 1998 e sem 2012-2016) para ver se a habilidade e so das grandes secas.
Dados: saidas/designer_chuva_mun_diaria.parquet (IMERG V07 diario), ibge_pam_mun_anual.parquet.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import warnings

warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
chuva = pd.read_parquet(OUT / "designer_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(str)


def alvo(prefixo):
    s = pam[pam.produto.str.startswith(prefixo) & (pam.ano >= 1990)].copy()
    s["rp"] = np.where(s.area_plantada_ha >= 100, s.producao_t * 1000 / s.area_plantada_ha.replace(0, np.nan), np.nan)
    s = s.sort_values(["cod", "ano"])
    s["tend"] = s.groupby("cod")["rp"].transform(lambda v: v.rolling(7, center=True, min_periods=4).median())
    s["quebra"] = (s.rp / s.tend < 0.5).astype(float).where((s.rp / s.tend).notna())
    return s.set_index(["cod", "ano"]).quebra


anos = list(range(1998, 2026))
cube = np.stack([chuva.loc[pd.Timestamp(a, 1, 1):].iloc[:151].values for a in anos])  # jan-mai (151 dias)
datas = {"31/jan": 31, "15/fev": 46, "28/fev": 59, "15/mar": 74, "31/mar": 90, "15/abr": 105, "30/abr": 120, "31/mai": 151}
linhas = []
for cult, pref in [("milho", "Milho (em gr"), ("feijao", "Feij")]:
    q = alvo(pref)
    for nome, nd in datas.items():
        acc = cube[:, :nd, :].sum(1)  # (anos, mun)
        pct = np.empty_like(acc)
        for k in range(len(anos)):
            pct[k] = acc[k] / np.median(np.delete(acc, k, axis=0), axis=0)
        F = pd.DataFrame(pct, index=anos, columns=chuva.columns).stack().rename("pct").reset_index()
        F.columns = ["ano", "cod", "pct"]
        F = F.join(q, on=["cod", "ano"]).dropna()
        comuns = ~F.ano.isin([1998, 2012, 2013, 2014, 2015, 2016])
        linhas.append({"cultura": cult, "data": nome, "AUC todos os anos": roc_auc_score(F.quebra, -F.pct),
                       "AUC anos comuns": roc_auc_score(F[comuns].quebra, -F[comuns].pct),
                       "P(quebra) se < 75% do normal": F.quebra[F.pct < 0.75].mean(),
                       "P(quebra) se >= 75%": F.quebra[F.pct >= 0.75].mean(),
                       "fracao alertada": (F.pct < 0.75).mean()})
T = pd.DataFrame(linhas)
print(T.round(3).to_string(index=False))
T.to_csv(OUT / "designer_curva_pct_normal.csv", index=False)
