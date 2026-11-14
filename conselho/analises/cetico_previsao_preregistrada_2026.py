"""Cetico 4 (v2: atributos por argumento; padrao = so NDVI, porque a LST do Terra tem deriva -> cetico_deriva_lst_terra.py): previsao PRE-REGISTRADA da safra 2026 no Ceara (milho e feijao) a partir do MODIS fev-mai 2026,
com intervalo conformal por ANO (jackknife+ agrupado). O IBGE PAM 2026 ainda nao saiu: e uma afirmacao falsificavel.

Modelo: ridge(anomalia NDVI, anomalia LST de fev-mai) -> anomalia do rendimento por area plantada (tendencia linear
por municipio), treino 2000-2025. Intervalo: residuos das previsoes deixando-o-ano-de-fora, agregados por ano no nivel
estado (media ponderada pela area plantada) -> quantis 10% e 90% (n = 26 anos).
Tambem a cobertura empirica do intervalo de 80% por ano (deve ficar perto de 80%).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, REF, DERIV

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from rasterio import features
from rasterio.transform import from_origin
from sklearn.linear_model import RidgeCV
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
for ano in range(2000, 2027):
    ts = [pd.Timestamp(ano, m, 1) for m in (2, 3, 4, 5)]
    a = nd.sel(time=[t for t in ts if t in nd.time.values]).mean("time").values
    b = ls.sel(time=[t for t in ts if t in ls.time.values]).mean("time").values
    if np.nanmax(a) > 2:
        a = a / 10000.0
    ma, mt = media_mun(a), media_mun(b)
    for k in range(1, len(codes)):
        reg.append({"cod": codes[k], "ano": ano, "ndvi": ma[k], "lst": mt[k]})
S = pd.DataFrame(reg)
g = S[S.ano <= 2025].groupby("cod")[["ndvi", "lst"]]
# anomalia contra a climatologia 2000-2025 do municipio (para 2026 nao ha vazamento: 2026 nao entra na media)
clim = g.mean().add_suffix("_c")
S = S.merge(clim, on="cod")
S["ndvi_a"], S["lst_a"] = S.ndvi - S.ndvi_c, S.lst - S.lst_c

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
COLS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["ndvi_a"]
print("atributos:", COLS)
for cult in ["milho", "feijao"]:
    base = pd.read_parquet(AQUI + f"cetico_painel_{cult}.parquet")
    P = base.merge(S, on=["cod", "ano"]).dropna(subset=["an_lin", "ndvi_a", "lst_a"])
    y = P.an_lin.clip(-1, 2).values
    X = P[COLS].values
    pred = np.zeros(len(P))
    for tr_, te_ in GroupKFold(n_splits=P.ano.nunique()).split(X, y, P.ano.values):
        pred[te_] = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13))).fit(X[tr_], y[tr_]).predict(X[te_])
    P["pred"] = pred
    w = P.area_plantada_ha
    est = P.assign(wy=y * w, wp=pred * w).groupby("ano")[["wy", "wp", "area_plantada_ha"]].sum()
    est["obs"], est["prev"] = est.wy / est.area_plantada_ha, est.wp / est.area_plantada_ha
    r = est.obs - est.prev
    lo, hi = np.quantile(r, [0.10, 0.90])
    cobertura = np.mean((est.obs >= est.prev + lo) & (est.obs <= est.prev + hi))
    corr = np.corrcoef(est.obs, est.prev)[0, 1]
    # modelo final (todos os anos) -> 2026
    m = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13))).fit(X, y)
    N = S[S.ano == 2026].dropna(subset=["ndvi_a", "lst_a"]).copy()
    N["prev"] = m.predict(N[COLS].values)
    # peso 2026 = area plantada media 2021-2025 do municipio
    a5 = base[base.ano.between(2021, 2025)].groupby("cod").area_plantada_ha.mean()
    N = N.merge(a5.rename("w"), on="cod")
    prev_est = np.average(N.prev, weights=N.w)
    print(f"\n==== {cult}: estado, deixa-ano-fora: r(prev, obs) = {corr:.2f} (n={len(est)} anos); "
          f"intervalo 80% = prev [{lo:+.2f}, {hi:+.2f}]; cobertura empirica in-sample dos residuos = {cobertura:.0%}")
    print(f"  ANO 2026 (MODIS fev-mai 2026): anomalia prevista do rendimento no estado = {prev_est:+.1%} "
          f"(80%: {prev_est+lo:+.1%} a {prev_est+hi:+.1%}) | NDVI anom. medio {N.ndvi_a.mean():+.3f}, LST anom. {N.lst_a.mean():+.2f} C")
    piores = N.sort_values("prev").head(8)
    nomes = pam.drop_duplicates("cod_local").set_index(pam.drop_duplicates("cod_local").cod_local.astype(int)).local
    print("  municipios com maior quebra prevista:", ", ".join(f"{nomes.get(c, c)} {p:+.0%}" for c, p in zip(piores.cod, piores.prev)))
    N[["cod", "prev", "ndvi_a", "lst_a", "w"]].to_csv(AQUI + f"cetico_prereg_2026_{cult}_{"_".join(COLS)}.csv", index=False)
    # para contexto: observado nos ultimos anos
    print("  obs x prev (deixa-ano-fora) 2019-2025:", ", ".join(f"{a}: {o:+.0%}/{p:+.0%}" for a, o, p in zip(est.index[-7:], est.obs[-7:], est.prev[-7:])))
