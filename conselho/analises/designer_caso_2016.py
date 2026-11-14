"""Designer - Analise 3c: por que o alerta de chuva de 30/abr falhou em 2016 (e acertou em 2012)?

Hipoteses: (1) janeiro muito chuvoso (antes do plantio) mascara o deficit de fev-abr no acumulado desde 1/jan;
(2) calor (Tmax POWER) e (3) memoria hidrica (GRACE TWS) no 5o ano da seca 2012-2017.
Dados: saidas/designer_chuva_mun_diaria.parquet (IMERG), power_ce_mensal, grace_ce_mensal (medias do Ceara).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa: F401,F403
from comum import DERIV

import numpy as np
import pandas as pd

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
ch = pd.read_parquet(OUT / "designer_chuva_mun_diaria.parquet").mean(axis=1)
m = ch.resample("MS").sum()
m = m[(m.index.year >= 1998) & (m.index.year <= 2025)]
clim = m.groupby(m.index.month).median()
print("Chuva media do CE (IMERG), % da mediana 1998-2025 do mes:")
for a in [2012, 2016]:
    print(f"  {a}: " + " ".join(f"{mm:02d}:{m[pd.Timestamp(a, mm, 1)] / clim[mm]:.0%}" for mm in range(1, 6)))
    fa = sum(m[pd.Timestamp(a, mm, 1)] for mm in [2, 3, 4]) / clim[[2, 3, 4]].sum()
    print(f"        fev-abr = {fa:.0%} do normal; jan-abr = {sum(m[pd.Timestamp(a, mm, 1)] for mm in range(1, 5)) / clim[[1, 2, 3, 4]].sum():.0%}")

pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw["data"] = pd.to_datetime(pw.data)
P = pw.pivot_table(index="data", columns="variavel", values="valor")
tx = P["T2M_MAX"]
an = tx - tx.groupby(tx.index.month).transform(lambda s: s[(s.index.year >= 1991) & (s.index.year <= 2020)].mean())
for a in [2012, 2016]:
    print(f"Tmax POWER anomalia vs 1991-2020, fev-mai {a}: " + " ".join(f"{mm:02d}:{an[pd.Timestamp(a, mm, 1)]:+.1f}" for mm in range(2, 6)))
gw = P["GWETROOT"]
ga = gw - gw.groupby(gw.index.month).transform("mean")
for a in [2012, 2016]:
    print(f"GWETROOT POWER anomalia (0-1) fev-mai {a}: " + " ".join(f"{mm:02d}:{ga[pd.Timestamp(a, mm, 1)]:+.3f}" for mm in range(2, 6)))
gr = pd.read_parquet(DERIV / "grace_ce_mensal.parquet")
gr["data"] = pd.to_datetime(gr.data)
print("GRACE variaveis:", gr.variavel.unique().tolist())
g = gr[gr.variavel == gr.variavel.unique()[0]].set_index("data").valor
for a in [2012, 2016]:
    v = g[(g.index.year == a) & (g.index.month.isin([1, 2, 3, 4]))]
    print(f"GRACE ({gr.variavel.unique()[0]}) jan-abr {a}: " + " ".join(f"{d:%m}:{x:+.1f}" for d, x in v.items()))
