"""Conselho - sensoriamento remoto. Robustez de sr_fundacao_irrigacao_grace.py.

Risco: o numero de cenas por ano dobra a partir de 2022 (entra o Landsat 9), e o p90 do NDVI cresce com mais
cenas mesmo sem mudanca no campo. Teste: repetir so com Landsat 8 (frequencia estavel desde 2013) e com
sorteio de no maximo 6 cenas por ano (200 repeticoes), metricas p90 >= 0,65 e mediana >= 0,55.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

from comum import DADOS, DERIV

warnings.filterwarnings("ignore")
rng = np.random.default_rng(0)
gr = pd.read_parquet(DERIV / "grace_aoi_mensal.parquet")
gr["data"] = pd.to_datetime(gr["data"])
for aoi in ["apodi_jaguaribe", "sertao_central"]:
    ds = xr.open_dataset(DADOS / f"landsat/landsat_aoi_{aoi}.nc")
    t = pd.to_datetime(ds.time.values)
    plat = ds.platform.values.astype(str)
    nd = ds.ndvi.values.astype("float32")[:, ::3, ::3]  # 1 em cada 3 pixels (90 m) para caber em < 5 min
    linhas = []
    for ano in range(2013, 2027):
        sel = np.where((t >= pd.Timestamp(ano, 8, 1)) & (t <= pd.Timestamp(ano, 12, 31)) & (plat == "landsat-8"))[0]
        if len(sel) < 3:
            continue
        cubo = nd[sel]
        ok = np.isfinite(cubo).sum(0) >= 3
        p90 = np.nanpercentile(cubo, 90, axis=0)
        med = np.nanmedian(cubo, 0)
        sub_p90, sub_med = [], []
        for _ in range(200):
            k = rng.choice(len(sel), size=min(4, len(sel)), replace=False)
            c = cubo[k]
            okk = np.isfinite(c).sum(0) >= 2
            sub_p90.append(100 * np.mean(np.nanmax(c, 0)[okk] >= 0.65))
            sub_med.append(100 * np.mean(np.nanmedian(c, 0)[okk] >= 0.55))
        linhas.append({"ano": ano, "cenas_L8": len(sel), "p90_L8": 100 * np.mean(p90[ok] >= 0.65), "med_L8": 100 * np.mean(med[ok] >= 0.55),
                       "max_4cenas_sorteio": np.mean(sub_p90), "med_4cenas_sorteio": np.mean(sub_med)})
    ds.close()
    R = pd.DataFrame(linhas).set_index("ano")
    g = gr[(gr.aoi == aoi) & gr.data.dt.month.isin([8, 9, 10, 11, 12])].groupby(gr.data.dt.year)["valor"].mean().rename("GRACE")
    J = R.join(g)
    print(f"== {aoi} (so Landsat 8) ==")
    print(J.round(1).to_string())
    for c in ["p90_L8", "med_L8", "max_4cenas_sorteio", "med_4cenas_sorteio"]:
        jj = J[[c, "GRACE"]].dropna()
        rho, p = stats.spearmanr(jj[c], jj.GRACE)
        sl = stats.theilslopes(J[c], J.index)[0]
        print(f"  {c:20s} Sen {sl:+.2f} pp/ano | rho com GRACE {rho:+.2f} (p={p:.3f}, n={len(jj)}) | "
              f"media 2013-19 {J.loc[2013:2019, c].mean():.1f}% vs 2022-26 {J.loc[2022:2026, c].mean():.1f}%")
