"""Cetico 6: deixar-o-ano-de-fora (LOYO) x validacao para a frente (walk-forward: treina so com anos < t).
O modelo so-NDVI teve r = 0,67 no estado com LOYO, mas errou para cima em 2023-2025. O walk-forward mostra o que
aconteceria em operacao. Compara: so-chuva IMERG (fmam, veranicos, maior seca) x so-NDVI MODIS fev-mai x ambos.
Anomalias dos atributos contra a media dos anos ANTERIORES do municipio (sem olhar o futuro).
Alvo: anomalia do rendimento por area plantada; tendencia por municipio estimada so com anos anteriores (reta em t-12..t-1;
o alvo do ano t e y_t / tendencia_extrapolada - 1) -> nada do futuro entra.
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
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

AQUI = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
nd = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi
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
reg = []
for ano in range(2000, 2026):
    ts = [pd.Timestamp(ano, m, 1) for m in (2, 3, 4, 5)]
    a = nd.sel(time=[t for t in ts if t in nd.time.values]).mean("time").values
    if np.nanmax(a) > 2:
        a = a / 10000.0
    ok = np.isfinite(a) & (lab > 0)
    s = np.bincount(lab[ok], weights=a[ok], minlength=len(codes))
    n = np.bincount(lab[ok], minlength=len(codes))
    for k in range(1, len(codes)):
        reg.append({"cod": codes[k], "ano": ano, "ndvi": s[k] / n[k] if n[k] else np.nan})
S = pd.DataFrame(reg)

for cult in ["milho", "feijao"]:
    P = pd.read_parquet(AQUI + f"cetico_painel_{cult}.parquet").merge(S, on=["cod", "ano"]).sort_values(["cod", "ano"])
    # tendencia so com o passado: reta nos 12 anos anteriores, extrapolada para t
    P["an_wf"] = np.nan
    for c, g in P.groupby("cod"):
        anos, yy = g.ano.values, g.y_plant.values
        for i in range(len(g)):
            m = (anos < anos[i]) & (anos >= anos[i] - 12)
            if m.sum() >= 6:
                b = np.polyfit(anos[m], yy[m], 1)
                t = max(np.polyval(b, anos[i]), 0.25 * np.nanmedian(yy[m]))
                P.loc[g.index[i], "an_wf"] = yy[i] / t - 1
    # atributos como anomalia contra a media dos anos anteriores do municipio
    for v in ["fmam", "nver", "cdd", "ndvi"]:
        P[v + "_p"] = P[v] - P.groupby("cod")[v].transform(lambda x: x.shift(1).expanding().mean())
    P = P.dropna(subset=["an_wf", "fmam_p", "ndvi_p"])
    P["y"] = P.an_wf.clip(-1, 2)
    conj = {"so chuva IMERG": ["fmam_p", "nver_p", "cdd_p"], "so NDVI MODIS": ["ndvi_p"], "chuva + NDVI": ["fmam_p", "nver_p", "cdd_p", "ndvi_p"]}
    lin = []
    for nome, cols in conj.items():
        prev = []
        for t in range(2010, 2026):
            trn, tst = P[P.ano < t], P[P.ano == t]
            if len(tst) == 0:
                continue
            mdl = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13))).fit(trn[cols], trn.y)
            w = tst.area_plantada_ha
            pt = mdl.predict(tst[cols])
            from scipy.stats import spearmanr
            prev.append({"ano": t, "obs": np.average(tst.y, weights=w), "prev": np.average(pt, weights=w),
                         "rho_dentro": spearmanr(pt, tst.y).statistic})
        E = pd.DataFrame(prev).set_index("ano")
        rec = E.loc[2020:]
        lin.append({"modelo": nome, "r estado 2010-2025": round(E.obs.corr(E.prev), 2),
                    "rho dentro do ano": f"{E.rho_dentro.mean():+.2f} ({(E.rho_dentro > 0).sum()}/{len(E)})",
                    "MAE 2010-2019": round((E.loc[:2019].obs - E.loc[:2019].prev).abs().mean(), 3),
                    "MAE 2020-2025": round((rec.obs - rec.prev).abs().mean(), 3),
                    "vies 2020-2025 (prev-obs)": round((rec.prev - rec.obs).mean(), 3),
                    "2023/2024/2025 prev vs obs": " | ".join(f"{E.loc[a,'prev']:+.0%}/{E.loc[a,'obs']:+.0%}" for a in [2023, 2024, 2025] if a in E.index)})
    print(f"\n==== {cult} (walk-forward, alvo e atributos sem futuro; n municipio-anos = {len(P)})")
    print(pd.DataFrame(lin).to_string(index=False))
