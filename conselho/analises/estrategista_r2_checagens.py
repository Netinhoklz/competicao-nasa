"""Rodada 2 do estrategista: checagem de números conflitantes entre propostas.
(1) Qual é o ONI de 2026 (2,14 / 2,31 / 2,46?) e em que trimestre é recorde.
(2) GRACE do CE em 2026: hidrólogo diz +3,8 cm dessazonalizado (p72, jul/2026);
    estrategista disse -9,7 cm em set/2026 (7º menor de 21 setembros). Quem está certo?
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import pandas as pd, numpy as np

D = r"E:/campeonato-nasa/dados/derivados/"
ind = pd.read_parquet(D + "indices_clima_mensal.parquet")
print(ind.variavel.unique())
print(ind.data.min(), ind.data.max())
oni = ind[ind.variavel.str.lower().str.contains("oni")].copy()
print(oni.variavel.unique(), oni.unidade.unique()[:3], oni.fonte.unique()[:3])
oni = oni.pivot_table(index="data", columns="variavel", values="valor").sort_index()
print(oni.tail(8))
col = oni.columns[0]
s = oni[col]
s.index = pd.to_datetime(s.index)
print("\nmaiores valores por mes-calendario (rotulo do arquivo):")
for m in [7, 8, 9, 10]:
    sm = s[s.index.month == m].sort_values(ascending=False)
    print(m, [(d.year, round(v, 2)) for d, v in sm.head(5).items()])
print("\nmedia jul-set por ano, top 5:")
js = s[s.index.month.isin([7, 8, 9])].groupby(s[s.index.month.isin([7, 8, 9])].index.year).mean().sort_values(ascending=False)
print(js.head(5).round(2))
print("max global:", s.idxmax(), round(s.max(), 2))

# --- GRACE
g = pd.read_parquet(D + "grace_ce_mensal.parquet")
print("\nGRACE variaveis:", g.variavel.unique(), g.fonte.unique())
for v in g.variavel.unique():
    gv = g[g.variavel == v].copy()
    gv["data"] = pd.to_datetime(gv.data)
    gv = gv.set_index("data").valor.sort_index()
    print("\n==", v, gv.index.min().date(), gv.index.max().date(), "n=", len(gv))
    print(gv.tail(6).round(2))
    # percentil bruto do ultimo valor entre todos os meses
    last_d, last_v = gv.index[-1], gv.iloc[-1]
    print("ultimo", last_d.date(), round(last_v, 2), "percentil bruto (todos meses):", round((gv < last_v).mean() * 100, 1))
    same = gv[gv.index.month == last_d.month]
    print("rank no mesmo mes:", int((same < last_v).sum()) + 1, "de", len(same), "mediana mesmo mes:", round(same.median(), 2))
    # dessazonalizado: anomalia vs climatologia mensal
    clim = gv.groupby(gv.index.month).transform("mean")
    ds = gv - clim
    print("dessaz ultimo:", round(ds.iloc[-1], 2), "percentil dessaz:", round((ds < ds.iloc[-1]).mean() * 100, 1))
    # tendencia
    yrs = (gv.index - gv.index[0]).days / 365.25
    b = np.polyfit(yrs, gv.values, 1)[0]
    print("tendencia linear bruta cm/ano:", round(b, 3))
