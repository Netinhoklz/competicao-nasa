"""Pesquisador de IA - analise 1: o "inicio da estacao" prevê a quadra SEM olhar o futuro?

A secao 02 usa o inicio de Liebmann & Marengo (minimo do acumulado de anomalias ate 30/abr). Esse inicio so e
conhecido depois de abril (olha o futuro), e o total "da estacao" comeca nele (efeito mecanico).
Aqui comparo com um inicio CAUSAL (1o dia desde 1/jan com >= 20 mm em 3 dias) e com a informacao disponivel
em datas reais de decisao (1/jan, 15/fev, 1/mar), sempre contra a chuva FUTURA (depois da data de decisao).
Unidades: 184 municipios x 28 anos (1998-2025) e media estadual (28 anos).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
P = pd.read_parquet(OUT / "painel_mun_ce.parquet")
ch = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
ind["data"] = pd.to_datetime(ind["data"])
piv = ind.pivot_table(index="data", columns="variavel", values="valor")


def ond(col, ano):
    s = piv[col]
    return s[(s.index >= f"{ano-1}-10-01") & (s.index <= f"{ano-1}-12-31")].mean()


rows = []
for ano in range(1998, 2026):
    for cod in ch.columns:
        s = ch[cod]
        r = {"cod": cod, "ano": ano}
        for nome, d in [("15fev", f"{ano}-02-15"), ("01mar", f"{ano}-03-01")]:
            r[f"Pate_{nome}"] = s[f"{ano}-01-01":d].sum()
            fut_ini = (pd.Timestamp(d) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            r[f"Pfut_{nome}"] = s[fut_ini:f"{ano}-05-31"].sum()
        rows.append(r)
F = pd.DataFrame(rows).merge(P[["cod", "ano", "inicio_LM_doy", "inicio_causal_doy", "P_fmam"]], on=["cod", "ano"])
F["ONI_ond"] = F.ano.map(lambda a: ond("ONI", a))
F["DIP_ond"] = F.ano.map(lambda a: ond("DIPOLO_TNA_menos_TSA", a))
F["inicio_causal_ate15fev"] = F.inicio_causal_doy.clip(upper=47)  # censurado: em 15/fev so sei "ainda nao"
F["inicio_causal_ate01mar"] = F.inicio_causal_doy.clip(upper=61)


def rho(a, b, df):
    x = df[[a, b]].dropna()
    return stats.spearmanr(x[a], x[b]).statistic


def tabela(df, nivel):
    lin = []
    lin.append(("inicio LM (retrospectivo) x P_fmam", rho("inicio_LM_doy", "P_fmam", df)))
    lin.append(("inicio causal x P_fmam", rho("inicio_causal_doy", "P_fmam", df)))
    lin.append(("[15/fev] inicio causal censurado x chuva 16/fev-31/mai", rho("inicio_causal_ate15fev", "Pfut_15fev", df)))
    lin.append(("[15/fev] chuva 1/jan-15/fev x chuva 16/fev-31/mai", rho("Pate_15fev", "Pfut_15fev", df)))
    lin.append(("[01/mar] chuva 1/jan-1/mar x chuva 2/mar-31/mai", rho("Pate_01mar", "Pfut_01mar", df)))
    lin.append(("[01/jan] ONI out-dez x chuva fev-mai", rho("ONI_ond", "P_fmam", df)))
    lin.append(("[01/jan] Dipolo TNA-TSA out-dez x chuva fev-mai", rho("DIP_ond", "P_fmam", df)))
    lin.append(("[01/jan] ONI out-dez x chuva 2/mar-31/mai", rho("ONI_ond", "Pfut_01mar", df)))
    print(f"\n== {nivel} (n={len(df)})")
    for a, b in lin:
        print(f"  {a:60s} rho = {b:+.2f}")
    return dict(lin)


r_mun = tabela(F, "municipio-ano")
E = F.groupby("ano").mean(numeric_only=True)
r_est = tabela(E, "media estadual por ano")

# Modelo combinado na data real de decisao (1/mar): ONI + dipolo + chuva ate a data -> chuva futura,
# avaliado deixando um ANO inteiro de fora (todos os municipios daquele ano), R2 fora da amostra.
from sklearn.linear_model import LinearRegression
for nome, X in [("so oceanos (1/jan)", ["ONI_ond", "DIP_ond"]),
                ("so chuva ate 1/mar", ["Pate_01mar"]),
                ("oceanos + chuva ate 1/mar", ["ONI_ond", "DIP_ond", "Pate_01mar"])]:
    pred = pd.Series(index=F.index, dtype=float)
    for a in F.ano.unique():
        tr, te = F.ano != a, F.ano == a
        m = LinearRegression().fit(F.loc[tr, X], F.loc[tr, "Pfut_01mar"])
        pred[te] = m.predict(F.loc[te, X])
    y = F.Pfut_01mar
    clim = F.groupby("cod").Pfut_01mar.transform("mean")
    r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    # habilidade contra a climatologia do proprio municipio (MSE skill score)
    pred_c = clim + (pred - pred.groupby(F.cod).transform("mean"))
    msss = 1 - ((y - pred_c) ** 2).mean() / ((y - clim) ** 2).mean()
    print(f"  LOYO chuva 2/mar-31/mai ~ {nome:28s}: MSSS vs climatologia municipal = {msss:+.2f}")

# Versao correta para anomalias: tudo relativo a climatologia do municipio (tira a variacao entre municipios)
print("\n== LOYO com anomalias municipais (alvo = anomalia da chuva 2/mar-31/mai)")
for c in ["Pate_01mar", "Pfut_01mar", "Pate_15fev", "Pfut_15fev"]:
    F[c + "_a"] = F[c] - F.groupby("cod")[c].transform("mean")
for nome, X in [("so oceanos (1/jan)", ["ONI_ond", "DIP_ond"]),
                ("so anomalia chuva ate 1/mar", ["Pate_01mar_a"]),
                ("oceanos + anomalia chuva ate 1/mar", ["ONI_ond", "DIP_ond", "Pate_01mar_a"])]:
    pred = pd.Series(index=F.index, dtype=float)
    for a in F.ano.unique():
        tr, te = F.ano != a, F.ano == a
        m = LinearRegression().fit(F.loc[tr, X], F.loc[tr, "Pfut_01mar_a"])
        pred[te] = m.predict(F.loc[te, X])
    y = F.Pfut_01mar_a
    msss = 1 - ((y - pred) ** 2).mean() / (y ** 2).mean()
    print(f"  {nome:36s}: MSSS = {msss:+.3f}   r = {np.corrcoef(y, pred)[0,1]:+.2f}")
