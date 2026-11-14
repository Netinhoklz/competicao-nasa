"""Cetico 5: a LST diurna do MODIS Terra tem deriva (orbita do Terra atrasando/adiantando a passagem)?
Sinal de alerta: na previsao pre-registrada (cetico_previsao_preregistrada_2026.py), 2026 aparece com anomalia de
LST de -3,4 C e o modelo errou para cima em 2023-2025. Teste: LST diurna de fev-mai (media CE) x Tmax do POWER
(MERRA-2, independente do satelite) ano a ano; tendencia da diferenca; e o modelo so com NDVI vs NDVI+LST nos anos recentes.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV

import numpy as np
import pandas as pd
import pymannkendall as mk

m = pd.read_parquet(DERIV / "modis_ce_mensal.parquet")
m["data"] = pd.to_datetime(m.data).dt.to_period("M").dt.to_timestamp()
p = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
p["data"] = pd.to_datetime(p.data).dt.to_period("M").dt.to_timestamp()
lst = m[m.variavel == "lst_dia"].set_index("data").valor
lstn = m[m.variavel == "lst_noite"].set_index("data").valor
tmx = p[p.variavel == "T2M_MAX"].set_index("data").valor
tmn = p[p.variavel == "T2M_MIN"].set_index("data").valor
ndvi = m[m.variavel == "ndvi"].set_index("data").valor
if lst.mean() > 200:
    lst, lstn = lst - 273.15, lstn - 273.15
J = pd.concat({"lst_dia": lst, "lst_noite": lstn, "tmax": tmx, "tmin": tmn, "ndvi": ndvi}, axis=1).dropna()
J = J[J.index.month.isin([2, 3, 4, 5])]
A = J.groupby(J.index.year).mean()
A = A[A.index <= 2026]
A["dif_dia"] = A.lst_dia - A.tmax
A["dif_noite"] = A.lst_noite - A.tmin
print(A.round(2).to_string())
for c in ["dif_dia", "dif_noite"]:
    t = mk.original_test(A[c].values)
    print(f"{c}: Mann-Kendall {t.trend} p={t.p:.3f}, Sen {t.slope*10:+.2f} C/decada")
base = A.loc[2000:2019, "dif_dia"]
print(f"dif_dia (LST - Tmax) media 2000-2019 = {base.mean():.2f} C (dp {base.std():.2f}); "
      f"2022 {A.loc[2022,'dif_dia']-base.mean():+.2f}, 2023 {A.loc[2023,'dif_dia']-base.mean():+.2f}, "
      f"2024 {A.loc[2024,'dif_dia']-base.mean():+.2f}, 2025 {A.loc[2025,'dif_dia']-base.mean():+.2f}, "
      f"2026 {A.loc[2026,'dif_dia']-base.mean():+.2f} (em dp: {(A.loc[2026,'dif_dia']-base.mean())/base.std():+.1f})")
# a deriva tambem deveria aparecer na NOITE se fosse clima real; se so o dia cai, e horario de passagem
