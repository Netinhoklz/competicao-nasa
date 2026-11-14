"""Cetico 5b: o NDVI do MODIS Terra tambem deriva nos anos recentes? (o modelo so-NDVI errou para cima em 2023-2025)
Comparacao nas 4 AOIs: NDVI MODIS (MOD13Q1 250 m) x NDVI Landsat (mediana, 30 m) e HLS no mesmo mes; diferenca
anual (meses com os dois) e tendencia. Tambem: chuva fev-mai IMERG/POWER e NDVI MODIS do estado em 2019-2026.
Landsat nao tem a deriva orbital do Terra (Landsat 8/9 mantem horario); se a diferenca MODIS-Landsat cresce, e deriva.
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


def ler(f, var, rot):
    d = pd.read_parquet(DERIV / f)
    d = d[d.variavel == var].copy()
    d["data"] = pd.to_datetime(d.data).dt.to_period("M").dt.to_timestamp()
    return d.groupby(["aoi", "data"]).valor.mean().rename(rot)


J = pd.concat([ler("modis_aoi_mensal.parquet", "ndvi", "modis"), ler("landsat_aoi_mensal.parquet", "ndvi_mediana", "landsat"),
               ler("hls_aoi_mensal.parquet", "ndvi_mediana", "hls")], axis=1).reset_index()
if J.modis.max() > 2:
    J["modis"] = J.modis / 10000
J["ano"] = J.data.dt.year
for ref in ["landsat", "hls"]:
    K = J.dropna(subset=["modis", ref]).copy()
    K["dif"] = K.modis - K[ref]
    A = K.groupby("ano").agg(dif=("dif", "mean"), n=("dif", "size"))
    A = A[A.n >= 6]
    print(f"\nMODIS - {ref.upper()} (media das 4 AOIs, todos os meses com os dois):")
    print(A.round(3).T.to_string())
    if len(A) >= 8:
        t = mk.original_test(A.dif.values)
        print(f"  tendencia: {t.trend} p={t.p:.3f}, Sen {t.slope*10:+.3f} NDVI/decada")
    if ref == "landsat":
        b = A.loc[2000:2019, "dif"]
        print(f"  dif media 2000-2019 = {b.mean():+.3f} (dp {b.std():.3f}); "
              + ", ".join(f"{a}: {A.loc[a,'dif']-b.mean():+.3f}" for a in range(2020, 2027) if a in A.index))

# contexto estadual
m = pd.read_parquet(DERIV / "modis_ce_mensal.parquet")
m["data"] = pd.to_datetime(m.data)
nd = m[m.variavel == "ndvi"].set_index("data").valor
nd = nd[nd.index.month.isin([2, 3, 4, 5])]
ndA = nd.groupby(nd.index.year).mean()
i = pd.read_parquet(DERIV / "imerg_ce_mensal.parquet")
i["data"] = pd.to_datetime(i.data)
pr = i[i.variavel == "precip_total"].set_index("data").valor
pr = pr[pr.index.month.isin([2, 3, 4, 5])]
prA = pr.groupby(pr.index.year).sum()
T = pd.DataFrame({"ndvi_fmam_modis": ndA, "chuva_fmam_imerg": prA}).dropna()
T["ndvi_pred_pela_chuva"] = np.poly1d(np.polyfit(T.loc[:2019, "chuva_fmam_imerg"], T.loc[:2019, "ndvi_fmam_modis"], 1))(T.chuva_fmam_imerg)
T["residuo"] = T.ndvi_fmam_modis - T.ndvi_pred_pela_chuva
print("\nEstado: NDVI MODIS fev-mai x chuva IMERG fev-mai (reta ajustada em 2000-2019):")
print(T.loc[2010:].round(3).to_string())
print(f"residuo medio 2000-2019 {T.loc[:2019,'residuo'].mean():+.3f} (dp {T.loc[:2019,'residuo'].std():.3f}); "
      f"2020-2026 {T.loc[2020:,'residuo'].mean():+.3f}")
