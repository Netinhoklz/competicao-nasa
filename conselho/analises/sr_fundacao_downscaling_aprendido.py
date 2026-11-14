"""Conselho - sensoriamento remoto. Ensaio do downscaling do SMAP com GLDAS (enquanto o SMAP L4 chega).

Pergunta: um indice APRENDIDO (ML sobre LST dia/noite, NDVI e anomalias) preve a anomalia de umidade do solo
(GLDAS-2.1 Noah 0-10 cm, 0,25 grau) num ANO NUNCA VISTO melhor que o indice classico TVDI?
Se sim, o downscaling do produto deve usar o modelo aprendido (treinado na escala grossa e aplicado a 1 km,
hipotese de invariancia de escala usada em DISPATCH/downscaling por ML), nao o TVDI de bordas por cena.

Validacao: deixar o ano inteiro de fora (GroupKFold por ano, 2000-2026), R2 da anomalia por celula-mes.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings

import numpy as np
import pandas as pd
import xarray as xr
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import GroupKFold

from comum import DADOS

warnings.filterwarnings("ignore")
OUT = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/sr_fundacao_painel_celula_mes.parquet"

nd = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi
lsd = xr.open_dataset(DADOS / "modis/mod11a2_lst_mensal_001deg.nc")
nd, ld, ln = xr.align(nd, lsd.lst_dia, lsd.lst_noite, join="inner")
gl = xr.open_dataset(DADOS / "gldas/gldas_noah025_mensal_ne.nc")
gt = set(pd.to_datetime(gl.time.values))
lat, lon = nd.lat.values, nd.lon.values
GI, GJ = np.meshgrid(np.floor((lat + 18.5) / 0.25).astype(int), np.floor((lon + 48.75) / 0.25).astype(int), indexing="ij")
cel = (GI * 1000 + GJ).ravel()
ucel = np.unique(cel)
idx = np.searchsorted(ucel, cel)
ii, jj = ucel // 1000, ucel % 1000


def tvdi(n, l, nb=30):
    ok = np.isfinite(n) & np.isfinite(l)
    bins = np.linspace(0.1, 0.9, nb + 1)
    c, lmax, lmin = [], [], []
    for k in range(nb):
        s = ok & (n >= bins[k]) & (n < bins[k + 1])
        if s.sum() > 50:
            c.append((bins[k] + bins[k + 1]) / 2)
            lmax.append(np.percentile(l[s], 99))
            lmin.append(np.percentile(l[s], 1))
    if len(c) < 5:
        return None
    aq, bq = np.polyfit(c, lmax, 1)
    af, bf = np.polyfit(c, lmin, 1)
    den = (aq * n + bq) - (af * n + bf)
    return np.clip((l - (af * n + bf)) / np.where(den > 0.5, den, np.nan), 0, 1)


def agrega(v):
    v = v.ravel()
    ok = np.isfinite(v)
    s = np.bincount(idx[ok], weights=v[ok], minlength=ucel.size)
    c = np.bincount(idx[ok], minlength=ucel.size)
    return np.where(c >= 250, s / np.maximum(c, 1), np.nan)


partes = []
for t in range(nd.time.size):
    d = pd.Timestamp(nd.time.values[t])
    if d not in gt:
        continue
    n, l, lnn = nd.values[t], ld.values[t], ln.values[t]
    tv = tvdi(n, l)
    if tv is None:
        continue
    g = gl.sel(time=d)
    partes.append(pd.DataFrame({"data": d, "cel": ucel, "tvdi": agrega(tv), "ndvi": agrega(n), "lst_dia": agrega(l),
                                "lst_noite": agrega(lnn), "sm0_10": g.SoilMoi0_10cm_inst.values[ii, jj],
                                "lat": -18.375 + 0.25 * ii, "lon": -48.625 + 0.25 * jj}))
P = pd.concat(partes).dropna()
P["mes"] = P.data.dt.month
P["ano"] = P.data.dt.year
P["amp_termica"] = P.lst_dia - P.lst_noite
for c in ["tvdi", "ndvi", "lst_dia", "lst_noite", "amp_termica", "sm0_10"]:
    P["a_" + c] = P[c] - P.groupby(["cel", "mes"])[c].transform("mean")
P.to_parquet(OUT)
print(f"painel: {len(P)} celula-meses, {P.cel.nunique()} celulas, {P.ano.min()}-{P.ano.max()}")

y = P.a_sm0_10.values
gkf = GroupKFold(n_splits=9)
modelos = {
    "TVDI (anomalia), linear": (["a_tvdi"], LinearRegression()),
    "LST dia (anomalia), linear": (["a_lst_dia"], LinearRegression()),
    "NDVI (anomalia), linear": (["a_ndvi"], LinearRegression()),
    "LST+NDVI+noite+amplitude, linear": (["a_lst_dia", "a_ndvi", "a_lst_noite", "a_amp_termica"], LinearRegression()),
    "Gradient boosting (anomalias + estado + mes + lat/lon)": (
        ["a_lst_dia", "a_ndvi", "a_lst_noite", "a_amp_termica", "a_tvdi", "ndvi", "lst_dia", "mes", "lat", "lon"],
        HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, random_state=0)),
}
print("\n== R2 da anomalia de umidade 0-10 cm em ANOS DEIXADOS DE FORA (GroupKFold por ano) ==")
for nome, (cols, mdl) in modelos.items():
    pred = np.zeros_like(y)
    for tr, te in gkf.split(P, y, groups=P.ano):
        mdl.fit(P.iloc[tr][cols], y[tr])
        pred[te] = mdl.predict(P.iloc[te][cols])
    r2 = r2_score(y, pred)
    # habilidade por estacao
    s_ch = P.mes.isin([2, 3, 4, 5]).values
    print(f"  {nome:55s} R2 = {r2:.3f}   (fev-mai {r2_score(y[s_ch], pred[s_ch]):.3f} | demais {r2_score(y[~s_ch], pred[~s_ch]):.3f})")
