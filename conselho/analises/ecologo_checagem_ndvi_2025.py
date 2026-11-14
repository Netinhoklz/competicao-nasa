"""Ecologo - checagem: 2025 foi mesmo o 'ano mais verde' (secao 09, z = +2,39)? E as fontes de chuva concordam em 2025-26?
Hipotese: o buraco do MODIS Terra (26/06 a 17/11/2025) tira os meses secos da media anual de 2025 e infla o NDVI anual.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import pandas as pd

m = pd.read_parquet(DERIV / "modis_ce_mensal.parquet")
m["data"] = pd.to_datetime(m.data)
n = m[m.variavel == "ndvi"].set_index("data").valor
print("Meses de NDVI presentes em 2025:", [d.month for d in n["2025"].index])
clim = n["2001":"2024"].groupby(n["2001":"2024"].index.month).mean()
a = n["2001":"2025"]
an = a - clim.loc[a.index.month].values
jm = an[an.index.month <= 5]
print("Anomalia media de NDVI jan-mai (meses presentes em todos os anos):", jm.groupby(jm.index.year).mean().round(3).loc[2018:].to_dict())
for f, var in (("power_ce_mensal", "PRECTOTCORR"), ("imerg_ce_mensal", "precip_total")):
    d = pd.read_parquet(DERIV / f"{f}.parquet")
    d["data"] = pd.to_datetime(d.data)
    s = d[d.variavel == var].set_index("data").valor
    q = s[s.index.month.isin([2, 3, 4, 5, 6])]
    q = q.groupby(q.index.year).sum()
    base = q.loc[max(1991, q.index.min()):2020].mean()
    print(f"{f}:{var} chuva fev-jun (mm): {q.loc[2018:2026].round(0).to_dict()} | media base {base:.0f}")
