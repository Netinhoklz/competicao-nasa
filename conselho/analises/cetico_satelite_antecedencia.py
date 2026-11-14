"""Cetico 2b: com quanta antecedencia o MODIS (NDVI/LST mensal, 1 km) ve a quebra local de milho/feijao?
Mesmo desenho de cetico_satelite_vs_chuva_local.py, mas com atributos acumulados ate o fim de cada mes
(fev, fev-mar, fev-abr, fev-mai) e, para comparar, a chuva IMERG ate o mesmo mes nao entra (ja coberta por outros).
Validacao: deixa o ANO inteiro de fora. Metricas: R2, rho medio dentro do ano, AUC de quebra <= -50%.
Tambem: probabilidade de "tercil seco" para 2027 pelos analogos de El Nino forte (n = 4) com prior climatologico.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, REF

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from rasterio import features
from rasterio.transform import from_origin
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

AQUI = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
nd = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi
ls = xr.open_dataset(DADOS / "modis/mod11a2_lst_mensal_001deg.nc").lst_dia
lat, lon = nd.lat.values, nd.lon.values
res = abs(lon[1] - lon[0])
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["codarea"] = mun["codarea"].astype(int)
tr = from_origin(lon.min() - res / 2, lat.max() + res / 2, res, res)
lab = features.rasterize(((g, i + 1) for i, g in enumerate(mun.geometry)), out_shape=(len(lat), len(lon)), transform=tr,
                         fill=0, dtype="int32")
if lat[0] < lat[-1]:
    lab = lab[::-1]
codes = np.r_[0, mun.codarea.values]


def media_mun(campo):
    ok = np.isfinite(campo) & (lab > 0)
    s = np.bincount(lab[ok], weights=campo[ok], minlength=len(codes))
    n = np.bincount(lab[ok], minlength=len(codes))
    with np.errstate(invalid="ignore", divide="ignore"):
        return s / n


reg = []
for ano in range(2000, 2026):
    for m in (1, 2, 3, 4, 5):
        t = pd.Timestamp(ano, m, 1)
        a = nd.sel(time=t).values if t in nd.time.values else np.full((len(lat), len(lon)), np.nan)
        b = ls.sel(time=t).values if t in ls.time.values else np.full((len(lat), len(lon)), np.nan)
        if np.nanmax(a) > 2:
            a = a / 10000.0
        ma, mt = media_mun(a), media_mun(b)
        for k in range(1, len(codes)):
            reg.append({"cod": codes[k], "ano": ano, "mes": m, "ndvi": ma[k], "lst": mt[k]})
S = pd.DataFrame(reg)

for cult in ["milho", "feijao"]:
    base = pd.read_parquet(AQUI + f"cetico_painel_{cult}.parquet")
    tab = []
    for ate, nome in [(2, "ate fev (decisao ~10/mar)"), (3, "ate mar (~10/abr)"), (4, "ate abr (~10/mai)"), (5, "ate mai (~10/jun)")]:
        F = S[S.mes.between(2, ate)].groupby(["cod", "ano"])[["ndvi", "lst"]].mean().reset_index()
        P = base.merge(F, on=["cod", "ano"]).dropna(subset=["an_lin", "ndvi", "lst"])
        for v in ["ndvi", "lst"]:
            g = P.groupby("cod")[v]
            P[v + "_a"] = P[v] - (g.transform("sum") - P[v]) / (g.transform("count") - 1)
        y = P.an_lin.clip(-1, 2).values
        X = P[["ndvi_a", "lst_a"]].values
        pred = np.zeros(len(P))
        for tr_, te_ in GroupKFold(n_splits=P.ano.nunique()).split(X, y, P.ano.values):
            pred[te_] = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13))).fit(X[tr_], y[tr_]).predict(X[te_])
        rho = [stats.spearmanr(pred[P.ano.values == a], y[P.ano.values == a]).statistic for a in sorted(P.ano.unique())]
        tab.append({"janela MODIS": nome, "R2 deixa-ano-fora": round(r2_score(y, pred), 3),
                    "rho dentro do ano": round(np.nanmean(rho), 3), "AUC quebra<=-50%": round(roc_auc_score(y <= -0.5, -pred), 3),
                    "taxa base quebra": round(float(np.mean(y <= -0.5)), 3)})
    print(f"\n==== {cult}")
    print(pd.DataFrame(tab).to_string(index=False))

# analogos de El Nino forte: 3 de 4 secos (cetico_memoria_grace_neff.py). Prior climatologico Beta(2/3, 4/3) (media 1/3)
from scipy.stats import beta
for nome, (a0, b0) in {"prior uniforme Beta(1,1)": (1, 1), "prior climatologico Beta(0.67,1.33)": (2 / 3, 4 / 3)}.items():
    post = beta(a0 + 3, b0 + 1)
    print(f"P(tercil seco | El Nino forte) com {nome}: media {post.mean():.2f}, IC 90% [{post.ppf(0.05):.2f}, {post.ppf(0.95):.2f}]")
