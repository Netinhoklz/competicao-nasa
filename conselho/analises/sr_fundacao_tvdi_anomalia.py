"""Conselho - sensoriamento remoto. Continuacao de sr_fundacao_tvdi_gldas.py.

Achado anterior: no espaco BRUTO o TVDI quase nao se correlaciona com a umidade GLDAS (rho ~ +0,1), mas no tempo
(media da caixa) r = -0,62. Hipotese: o campo estatico (textura e profundidade do solo no GLDAS, altitude e brisa
no LST) mascara a relacao. Teste: remover a climatologia de CADA celula (anomalia celula-mes) e repetir.

Saidas:
- Spearman espacial mensal entre anomalias de TVDI e de umidade GLDAS 0-10 cm (por celula 0,25 grau);
- correlacao temporal por celula (mapa de onde o TVDI acompanha a umidade): mediana e fracao de celulas r < -0,3;
- comparacao com NDVI e LST isolados (o TVDI soma informacao?).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

from comum import DADOS

warnings.filterwarnings("ignore")

nd = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi
ls = xr.open_dataset(DADOS / "modis/mod11a2_lst_mensal_001deg.nc").lst_dia
nd, ls = xr.align(nd, ls, join="inner")
gl = xr.open_dataset(DADOS / "gldas/gldas_noah025_mensal_ne.nc")
gtimes = pd.to_datetime(gl.time.values)
lat, lon = nd.lat.values, nd.lon.values
gi = np.floor((lat + 18.5) / 0.25).astype(int)
gj = np.floor((lon + 48.75) / 0.25).astype(int)
GI, GJ = np.meshgrid(gi, gj, indexing="ij")
cel = (GI * 1000 + GJ).ravel()
ucel = np.unique(cel)
pos = {c: k for k, c in enumerate(ucel)}
idx = np.array([pos[c] for c in cel])


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


datas, TV, NDc, LSc, SM = [], [], [], [], []
ii, jj = ucel // 1000, ucel % 1000
for t in range(nd.time.size):
    d = pd.Timestamp(nd.time.values[t])
    if d not in set(gtimes):
        continue
    n, l = nd.values[t], ls.values[t]
    tv = tvdi(n, l)
    if tv is None:
        continue
    datas.append(d)
    TV.append(agrega(tv))
    NDc.append(agrega(n))
    LSc.append(agrega(l))
    SM.append(gl.SoilMoi0_10cm_inst.sel(time=d).values[ii, jj])
D = pd.DatetimeIndex(datas)
TV, NDc, LSc, SM = map(np.array, (TV, NDc, LSc, SM))
print(f"{len(D)} meses x {TV.shape[1]} celulas")


def anom(M):
    out = M.copy()
    for m in range(1, 13):
        s = D.month == m
        out[s] = M[s] - np.nanmean(M[s], axis=0)
    return out


aTV, aND, aLS, aSM = map(anom, (TV, NDc, LSc, SM))
rows = []
for k in range(len(D)):
    ok = np.isfinite(aTV[k]) & np.isfinite(aSM[k]) & np.isfinite(aND[k]) & np.isfinite(aLS[k])
    if ok.sum() < 30:
        continue
    rows.append({"data": D[k], "rho_aTVDI_aSM": stats.spearmanr(aTV[k][ok], aSM[k][ok])[0],
                 "rho_aNDVI_aSM": stats.spearmanr(aND[k][ok], aSM[k][ok])[0],
                 "rho_aLST_aSM": stats.spearmanr(aLS[k][ok], aSM[k][ok])[0], "n": int(ok.sum())})
R = pd.DataFrame(rows).set_index("data")
print("\n== Spearman ESPACIAL das ANOMALIAS (celula-mes), 0,25 grau ==")
for c in ["rho_aTVDI_aSM", "rho_aNDVI_aSM", "rho_aLST_aSM"]:
    print(f"  {c:15s} mediana {R[c].median():+.2f}  IQR [{R[c].quantile(.25):+.2f}, {R[c].quantile(.75):+.2f}]  "
          f"meses rho<-0,3: {(R[c] < -0.3).mean():.0%}  rho>+0,3: {(R[c] > 0.3).mean():.0%}")
print("Por estacao (mediana rho_aTVDI_aSM): chuvosa fev-mai = "
      f"{R[R.index.month.isin([2, 3, 4, 5])].rho_aTVDI_aSM.median():+.2f}; transicao jun-jul = "
      f"{R[R.index.month.isin([6, 7])].rho_aTVDI_aSM.median():+.2f}; seca ago-jan = "
      f"{R[R.index.month.isin([8, 9, 10, 11, 12, 1])].rho_aTVDI_aSM.median():+.2f}")

# correlacao temporal por celula
rt, rn, rl = [], [], []
for j in range(TV.shape[1]):
    for arr, lst in ((aTV, rt), (aND, rn), (aLS, rl)):
        ok = np.isfinite(arr[:, j]) & np.isfinite(aSM[:, j])
        lst.append(np.corrcoef(arr[ok, j], aSM[ok, j])[0, 1] if ok.sum() >= 60 else np.nan)
rt, rn, rl = map(np.array, (rt, rn, rl))
v = np.isfinite(rt)
print(f"\n== Correlacao TEMPORAL por celula (anomalias, {v.sum()} celulas) ==")
for nome, r in (("TVDI", rt), ("NDVI", rn), ("LST", rl)):
    r = r[np.isfinite(r)]
    print(f"  {nome}: mediana r = {np.median(r):+.2f};  celulas com r < -0,3: {np.mean(r < -0.3):.0%};  r > +0,3: {np.mean(r > 0.3):.0%}")
# |r| do TVDI maior que o do NDVI e o do LST?
both = np.isfinite(rt) & np.isfinite(rn) & np.isfinite(rl)
print(f"  celulas onde |r_TVDI| > max(|r_NDVI|, |r_LST|): {np.mean(np.abs(rt[both]) > np.maximum(np.abs(rn[both]), np.abs(rl[both]))):.0%}")
pd.DataFrame({"cel_lat": -18.375 + 0.25 * ii, "cel_lon": -48.625 + 0.25 * jj, "r_tvdi": rt, "r_ndvi": rn, "r_lst": rl}).to_csv(
    r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/sr_fundacao_tvdi_r_por_celula.csv", index=False)
