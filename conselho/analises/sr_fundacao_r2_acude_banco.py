"""Conselho - sensoriamento remoto, RODADA 2. Complemento do bloco C.

1) A area de acude a 30 m (Sertao Central, Landsat QA, 1984-2026) acompanha o 'banco azul' do hidrologo
   (residual GRACE - solo GLDAS, CE)?
2) Em que percentil esta a agua do acude em 2026, comparada ao 'banco' do GRACE (hidrologo: percentil 72 em
   jul/2026 dessazonalizado; estrategista: set/2026 = 7o menor de 21 setembros)? Escala importa?
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from comum import DADOS

BASE = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
lh = pd.read_parquet(DADOS / "landsat/landsat_aoi_cenas_hist.parquet")
ls = pd.read_parquet(DADOS / "landsat/landsat_aoi_cenas_l89.parquet")
L = pd.concat([lh, ls.drop(columns=["erro"], errors="ignore")], ignore_index=True)
L["datetime"] = pd.to_datetime(L["datetime"], utc=True).dt.tz_localize(None)
L = L[(L.aoi == "sertao_central") & (L.frac_valida >= 0.5) & L.frac_agua.notna()]
L["agua"] = 100 * L.frac_agua / L.frac_valida
L = L[L.datetime.dt.month.isin([8, 9, 10, 11, 12])]
A = L.groupby(L.datetime.dt.year).agua.agg(["median", "size"])
A = A[A["size"] >= 2]["median"]

r = pd.read_csv(BASE + "saidas/hidrologo_grace_residuo_ce.csv", parse_dates=["time"]).set_index("time")
for col in ["grace", "residual", "solo"]:
    s = pd.Series({a: r[col][(r.index.year == a) & r.index.month.isin([8, 9, 10, 11, 12])].mean() for a in A.index}).dropna()
    rho, p = spearmanr(A.loc[s.index], s)
    print(f"acude Sertao Central x {col:8s} CE (ago-dez): rho {rho:+.2f} p {p:.3f} n {len(s)}")

print(f"\nacude 2026 = {A.loc[2026]:.2f}% ; percentil na serie 1984-2025 = {(A.drop(2026) < A.loc[2026]).mean():.0%}"
      f" ; mediana {A.drop(2026).median():.2f}%")
print(f"acude 2025 = {A.loc[2025]:.2f}% ; percentil = {(A.drop([2025, 2026]) < A.loc[2025]).mean():.0%}")

# GRACE da AOI do Sertao Central: cru em setembro e dessazonalizado
g = pd.read_parquet(DADOS / "derivados/grace_aoi_mensal.parquet")
g = g[g.aoi == "sertao_central"].set_index("data").valor.sort_index()
clim = g.groupby(g.index.month).transform("mean")
gd = g - clim
ult = g.index.max()
print(f"\nGRACE AOI Sertao Central ultimo mes {ult.date()}: cru {g.iloc[-1]:+.1f} cm; dessaz {gd.iloc[-1]:+.1f} cm; "
      f"percentil dessaz {(gd.iloc[:-1] < gd.iloc[-1]).mean():.0%}")
set_ = g[g.index.month == 9]
print(f"setembros: 2026 = {set_.iloc[-1]:+.1f} cm, posicao {int((set_ < set_.iloc[-1]).sum()) + 1} de {len(set_)}")
# tendencia do GRACE (explica cru x dessazonalizado divergirem?)
t = (g.index - g.index[0]).days / 365.25
print(f"tendencia linear GRACE AOI: {np.polyfit(t, g.values, 1)[0]:+.2f} cm/ano")

# lag: acude responde ao GRACE com defasagem?
for lag in (0, 1, 2):
    s = pd.Series({a: g[(g.index.year == a - lag) & g.index.month.isin([8, 9, 10, 11, 12])].mean() for a in A.index}).dropna()
    rho, p = spearmanr(A.loc[s.index], s)
    print(f"acude(t) x GRACE AOI ago-dez(t-{lag}): rho {rho:+.2f} p {p:.3f} n {len(s)}")
