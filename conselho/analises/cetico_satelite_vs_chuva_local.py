"""Cetico 2: o satelite de vegetacao (MODIS 1 km) ve a quebra LOCAL que a chuva do IMERG nao ve?

Contexto (cetico_escala_vazamento.py): ~half da variancia do rendimento municipal e choque comum do ano; a outra
metade e espacialmente coerente (r ~ 0,5 com os 5 vizinhos) mas a chuva municipal do IMERG quase nao a explica
(rho ~ 0,03-0,07). Aqui testamos NDVI e LST de mar-mai do MODIS, em todos os pixels e so nos pixels de lavoura
(ESA CCI 2020, classes 10-30), contra o residuo local do rendimento.

Atencao: NDVI de mar-mai e informacao DENTRO da safra (nowcast), nao previsao antes do plantio.
Dados: E:/campeonato-nasa/dados/modis/mod13q1_ndvi_mensal_001deg.nc, mod11a2_lst_mensal_001deg.nc,
       esa_cci_lc_2020_nordeste_300m.nc; paineis cetico_painel_{milho,feijao}.parquet (script 1).
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
from sklearn.metrics import r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

AQUI = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
nd = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi
ls = xr.open_dataset(DADOS / "modis/mod11a2_lst_mensal_001deg.nc").lst_dia
lat, lon = nd.lat.values, nd.lon.values
res = abs(lon[1] - lon[0])
# rotulos de municipio no grid 0,01 grau
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["codarea"] = mun["codarea"].astype(int)
tr = from_origin(lon.min() - res / 2, lat.max() + res / 2, res, res)
lab = features.rasterize(((g, i + 1) for i, g in enumerate(mun.geometry)), out_shape=(len(lat), len(lon)), transform=tr,
                         fill=0, dtype="int32")
if lat[0] < lat[-1]:  # grade crescente em latitude: inverter o raster
    lab = lab[::-1]
codes = np.r_[0, mun.codarea.values]
# mascara de lavoura (ESA CCI 2020) amostrada no grid 0,01
cci = xr.open_dataset(DADOS / "modis/esa_cci_lc_2020_nordeste_300m.nc").lccs_class
cl = cci.sel(lat=xr.DataArray(lat, dims="lat"), lon=xr.DataArray(lon, dims="lon"), method="nearest").values
lav = (cl >= 10) & (cl <= 30)
print(f"pixels 0,01 grau no CE: {(lab>0).sum()} | fracao de lavoura (CCI 10-30): {lav[lab>0].mean():.1%}")


def media_mun(campo, mascara=None):
    ok = np.isfinite(campo) & (lab > 0)
    if mascara is not None:
        ok &= mascara
    s = np.bincount(lab[ok], weights=campo[ok], minlength=len(codes))
    n = np.bincount(lab[ok], minlength=len(codes))
    with np.errstate(invalid="ignore", divide="ignore"):
        return s / n, n


reg = []
for ano in range(2000, 2026):
    sel = [pd.Timestamp(ano, m, 1) for m in (3, 4, 5)]
    a = nd.sel(time=[t for t in sel if t in nd.time.values]).mean("time").values
    b = ls.sel(time=[t for t in sel if t in ls.time.values]).mean("time").values
    if np.nanmax(a) > 2:  # escala inteira -> NDVI
        a = a / 10000.0
    ma, _ = media_mun(a)
    ml, nl = media_mun(a, lav)
    mt, _ = media_mun(b)
    for k in range(1, len(codes)):
        reg.append({"cod": codes[k], "ano": ano, "ndvi": ma[k], "ndvi_lav": ml[k] if nl[k] >= 20 else np.nan, "lst": mt[k]})
S = pd.DataFrame(reg)
print(S.describe().round(3).to_string())

for cult in ["milho", "feijao"]:
    P = pd.read_parquet(AQUI + f"cetico_painel_{cult}.parquet").merge(S, on=["cod", "ano"]).dropna(subset=["an_lin", "ndvi", "lst"])
    # anomalias no municipio: valor menos a media dos OUTROS anos (sem usar o proprio ano)
    for v in ["ndvi", "ndvi_lav", "lst", "fmam", "nver", "cdd"]:
        g = P.groupby("cod")[v]
        P[v + "_a"] = P[v] - (g.transform("sum") - P[v]) / (g.transform("count") - 1)
    y = P.an_lin.clip(-1, 2)
    P["res"] = y - P.assign(y=y).groupby("ano").y.transform("mean")
    print(f"\n==== {cult}: {len(P)} municipio-anos 2000-2025 (tendencia linear por municipio)")
    # nivel estado
    E = P.assign(y=y).groupby("ano")[["y", "ndvi_a", "lst_a", "fmam_a"]].mean()
    for v in ["ndvi_a", "lst_a", "fmam_a"]:
        r = stats.pearsonr(E[v], E.y)
        print(f"  estado (n={len(E)}): r(anomalia {v[:-2]}, anomalia rendimento) = {r.statistic:+.2f} (p={r.pvalue:.3f})")
    # dentro do ano: desvio em relacao ao estado
    lin = []
    for v in ["fmam_a", "nver_a", "cdd_a", "ndvi_a", "ndvi_lav_a", "lst_a"]:
        dv = P[v] - P.groupby("ano")[v].transform("mean")
        ok = dv.notna()
        rr = [stats.spearmanr(dv[ok & (P.ano == a)], P.res[ok & (P.ano == a)]).statistic for a in sorted(P.ano.unique())]
        lin.append({"variavel (desvio local no ano)": v[:-2], "rho medio dentro do ano": round(np.nanmean(rr), 3),
                    "anos com rho>0": f"{np.sum(np.array(rr) > 0)}/{len(rr)}"})
    print(pd.DataFrame(lin).to_string(index=False))
    # modelos, deixando o ano de fora
    conj = {"chuva IMERG": ["fmam_a", "nver_a", "cdd_a"], "MODIS NDVI+LST": ["ndvi_a", "lst_a"],
            "chuva + MODIS": ["fmam_a", "nver_a", "cdd_a", "ndvi_a", "lst_a"]}
    tab = []
    gk = GroupKFold(n_splits=P.ano.nunique())
    for nome, cols in conj.items():
        X = P[cols].values
        pred = np.zeros(len(P))
        for tr_, te_ in gk.split(X, y, P.ano.values):
            m = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13))).fit(X[tr_], y.values[tr_])
            pred[te_] = m.predict(X[te_])
        rho = [stats.spearmanr(pred[P.ano.values == a], y.values[P.ano.values == a]).statistic for a in sorted(P.ano.unique())]
        # acerto de quebra severa (<= -50%)
        q = y.values <= -0.5
        from sklearn.metrics import roc_auc_score
        tab.append({"atributos": nome, "R2 deixa-ano-fora": round(r2_score(y, pred), 3),
                    "rho dentro do ano": round(np.nanmean(rho), 3), "AUC quebra<=-50%": round(roc_auc_score(q, -pred), 3)})
    print(pd.DataFrame(tab).to_string(index=False))
