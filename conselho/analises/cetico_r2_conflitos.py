"""Cetico rodada 2: checa numeros conflitantes entre especialistas (ONI 2026, GRACE 2026, ureia/milho)."""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
from comum import DERIV
import pandas as pd, numpy as np

ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
ind["data"] = pd.to_datetime(ind["data"])
oni = ind[ind.variavel == "ONI"].set_index("data")["valor"]
# ranking do valor de setembro (ASO centrado) entre todos os setembros
sep = oni[oni.index.month == 9]
print("ONI set (ASO) top5:", sep.sort_values(ascending=False).head(5).round(2).to_dict())
print("media jul-set 2026:", round(oni["2026-07":"2026-09"].mean(), 2), " ago-set:", round(oni["2026-08":"2026-09"].mean(), 2))
js = oni[oni.index.month.isin([7, 8, 9])].groupby(oni[oni.index.month.isin([7, 8, 9])].index.year).mean()
print("media jul-set top5:", js.sort_values(ascending=False).head(5).round(2).to_dict())

g = pd.read_parquet(DERIV / "grace_ce_mensal.parquet")
print(g.fonte.unique(), g.unidade.unique())
g["data"] = pd.to_datetime(g["data"])
s = g.set_index("data")["valor"].sort_index()
clim = s.groupby(s.index.month).transform("mean")
d = s - clim
for mes in ["2026-05-01", "2026-06-01", "2026-07-01", "2026-08-01", "2026-09-01"]:
    t = pd.Timestamp(mes)
    print(mes, "cru", round(s[t], 2), "dessaz", round(d[t], 2), "pct dessaz", round((d < d[t]).mean() * 100, 1))

m = pd.read_parquet(DERIV / "mercado_precos_mensal.parquet")
print(m.columns.tolist()); print(m.head(3))
