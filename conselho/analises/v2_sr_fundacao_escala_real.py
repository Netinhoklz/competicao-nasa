"""Sensoriamento remoto, rodada 2 (dados novos): a ESCALA REAL de cada camada e a triangulacao de Quixada 2023-2025.

Grade nominal nao e escala real. Medimos a escala em que DOIS SENSORES INDEPENDENTES concordam sobre o padrao
espacial das anomalias (cada pixel menos a sua climatologia do mes; cada mes menos a media do dominio), agregando em
blocos cada vez maiores. Regra pre-declarada: escala util = menor bloco com r espacial mediano >= 0,8.
 A. Unidade de decisao: area dos 184 municipios e quantas celulas de cada camada cabem num municipio mediano.
 B. NDVI: VIIRS VNP13A3 (1 km) x MODIS MOD13Q1 (250 m), ambos em 0,01 grau, 2012-2026, blocos de 1 a 50 km.
 C. Agua: IMERG (0,1 grau) x SMAP L3 AM recomendado (radiometro banda L, 9 km), meses fev-mai 2016-2023 (L3 ainda
    baixando). Sensores independentes; a relacao e fisica (mais chuva no mes -> solo mais umido), nao identidade.
    (L3 x L4 ja esta em v2_sr_fundacao_smap_l3_l4.saida.txt: 0,75 a 9 km, 0,82 a 36 km em fev-mai; L4 assimila o SMAP.)
 D. Quixada 2023-2025 (quebra no PAM com chuva, ISNA e SMAP normais): o NDVI de mar-mai viu alguma coisa? E os
    vizinhos de 50 km quebraram no mesmo ano?
So le arquivos.
"""
import glob
import os
import sys
import time
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, REF

import geopandas as gpd
import h5py
import numpy as np
import pandas as pd
import shapely
import xarray as xr
from rasterio import features
from rasterio.transform import from_origin
from scipy import stats

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
D = "E:/campeonato-nasa/dados/derivados/"
t0 = time.time()
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["codarea"] = mun["codarea"].astype(str)
CE = gpd.read_file(REF / "ceara_uf.geojson").union_all()

# ---------------- A. unidade de decisao
print("=" * 25, "A. Municipio x tamanho da celula de cada camada", "=" * 25)
area = mun.to_crs(5880).area / 1e6
print(f"area dos 184 municipios (km2): p10 {area.quantile(.1):.0f} | mediana {area.median():.0f} | p90 {area.quantile(.9):.0f} | "
      f"lado equivalente mediano {np.sqrt(area.median()):.0f} km")
camadas = {"GRACE mascon (~300 km)": 300 ** 2, "POWER 0,5 grau": 55.3 * 55.0, "IMERG 0,1 grau": 11.06 * 11.0,
           "SMAP L3/L4 9 km (EASE2)": 81.0, "NISAR SME2 200 m (roteiro)": 0.04, "VIIRS NDVI 1 km": 1.0,
           "MODIS NDVI 250 m": 0.0625, "HLS/Landsat 30 m": 0.0009}
for k, a in camadas.items():
    print(f"  {k:28s} celula ~{a:>10.4f} km2 -> {area.median() / a:>10.1f} celulas num municipio mediano")

# ---------------- B. NDVI VIIRS x MODIS por tamanho de bloco
print("\n" + "=" * 25, "B. NDVI: VIIRS x MODIS, r espacial das anomalias por bloco", "=" * 25)
mo = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi.sel(time=slice("2012-01-01", None))
vi = xr.open_dataset(DADOS / "viirs/vnp13a3_ndvi_evi_ceara_001deg.nc").ndvi.isel(lat=slice(None, None, -1))
lat, lon = mo.lat.values, mo.lon.values
LO, LA = np.meshgrid(lon, lat)
mce = shapely.contains_xy(CE, LO, LA)
tc = pd.DatetimeIndex(mo.time.values).intersection(pd.DatetimeIndex(vi.time.values))
X = mo.sel(time=tc).values.astype("float32"); Y = vi.sel(time=tc).values.astype("float32")
if np.nanmax(X) > 2:
    X = X / 10000.0
X[(X < -0.2) | (X > 1)] = np.nan; Y[(Y < -0.2) | (Y > 1)] = np.nan
X[:, ~mce] = np.nan; Y[:, ~mce] = np.nan
mes = tc.month.values; base = tc.year.values <= 2024
for k in range(1, 13):
    s = mes == k
    X[s] -= np.nanmean(X[s & base], axis=0); Y[s] -= np.nanmean(Y[s & base], axis=0)
ok = np.isfinite(X) & np.isfinite(Y)
X[~ok] = np.nan; Y[~ok] = np.nan
print(f"meses comuns {len(tc)} ({tc.min():%Y-%m}..{tc.max():%Y-%m}); ({time.time() - t0:.0f} s)")


def curva(X, Y, ok, blocos, rotulo_km, sazao, minfrac=0.5, minpts=12):
    out = []
    for b in blocos:
        nl, nc = (X.shape[1] // b) * b, (X.shape[2] // b) * b
        sh = (len(X), nl // b, b, nc // b, b)
        xb = np.nanmean(X[:, :nl, :nc].reshape(sh), axis=(2, 4)); yb = np.nanmean(Y[:, :nl, :nc].reshape(sh), axis=(2, 4))
        cnt = ok[:, :nl, :nc].reshape(sh).sum(axis=(2, 4))
        rq, rr = [], []
        for t in range(len(xb)):
            o = np.isfinite(xb[t]) & np.isfinite(yb[t]) & (cnt[t] >= max(1, minfrac * b * b))
            if o.sum() >= minpts:
                v = stats.pearsonr(xb[t][o] - xb[t][o].mean(), yb[t][o] - yb[t][o].mean()).statistic
                (rq if sazao[t] else rr).append(v)
        out.append({"bloco": f"{rotulo_km(b)}", "r_fev_mai": np.median(rq) if rq else np.nan, "meses_fev_mai": len(rq),
                    "r_outros": np.median(rr) if rr else np.nan, "meses_outros": len(rr)})
    return pd.DataFrame(out)


Tb = curva(X, Y, ok, [1, 2, 5, 10, 25, 50], lambda b: f"{b} km", np.isin(mes, [2, 3, 4, 5]))
print(Tb.round(3).to_string(index=False))
# autocorrelacao com o vizinho imediato (1 km) da anomalia do VIIRS: quanto da grade e informacao propria
ac = [stats.pearsonr(Y[t][:, :-1][ok[t][:, :-1] & ok[t][:, 1:]], Y[t][:, 1:][ok[t][:, :-1] & ok[t][:, 1:]]).statistic
      for t in range(len(Y)) if (ok[t][:, :-1] & ok[t][:, 1:]).sum() > 1000]
print(f"VIIRS: r entre pixels vizinhos (1 km) da anomalia, mediana por mes {np.median(ac):.3f}")
del X, Y

# ---------------- C. IMERG x SMAP L3 (independentes)
print("\n" + "=" * 25, "C. Agua: IMERG 0,1 grau x SMAP L3 (banda L), fev-mai, r espacial das anomalias mensais", "=" * 25)
l3dir = DADOS / "smap/l3_diario"
lat9 = np.load(l3dir / "lat_linhas.npy"); lon9 = np.load(l3dir / "lon_colunas.npy")
arqs = sorted(glob.glob(str(l3dir / "SMAP_L3_SM_P_E_*_recorte.nc4")))
agora = time.time()
arqs = [a for a in arqs if agora - os.path.getmtime(a) > 180]
arqs = {os.path.basename(a).split("_")[5]: a for a in arqs}
# grade IMERG do CE
im0 = xr.open_dataset(DADOS / "imerg/imerg_ce_diario_2016.nc")
latI, lonI = im0.lat.values, im0.lon.values
# cada celula SMAP vai para a celula IMERG mais proxima (media das celulas SMAP dentro de cada 0,1 grau)
LO9, LA9 = np.meshgrid(lon9, lat9)
dentro9 = shapely.contains_xy(CE, LO9, LA9)
iy = np.clip(np.round((LA9 - latI[0]) / (latI[1] - latI[0])).astype(int), 0, len(latI) - 1)
ix = np.clip(np.round((LO9 - lonI[0]) / (lonI[1] - lonI[0])).astype(int), 0, len(lonI) - 1)
caixa = (LA9 >= latI.min() - 0.05) & (LA9 <= latI.max() + 0.05) & (LO9 >= lonI.min() - 0.05) & (LO9 <= lonI.max() + 0.05) & dentro9
flat = (iy * len(lonI) + ix)[caixa]
LOI, LAI = np.meshgrid(lonI, latI)
mceI = shapely.contains_xy(CE, LOI, LAI)
meses = [(y, m) for y in range(2016, 2024) for m in (2, 3, 4, 5)]
chuvaM, smM = [], []
for (y, m) in meses:
    im = xr.open_dataset(DADOS / f"imerg/imerg_ce_diario_{y}.nc").precip.sel(time=f"{y}-{m:02d}")
    chuvaM.append(im.sum("time").values)
    acc = np.zeros(len(latI) * len(lonI)); n = np.zeros(len(latI) * len(lonI))
    dias_m = pd.date_range(f"{y}-{m:02d}-01", periods=pd.Timestamp(y, m, 1).days_in_month)
    for dd in dias_m:
        a = arqs.get(dd.strftime("%Y%m%d"))
        if a is None:
            continue
        with h5py.File(a, "r") as h:
            s = h["Soil_Moisture_Retrieval_Data_AM/soil_moisture"][:]
            q = h["Soil_Moisture_Retrieval_Data_AM/retrieval_qual_flag"][:]
        v = np.where((s >= 0.02) & (s <= 0.5) & (q != 65534) & ((q.astype(np.int64) & 1) == 0), s, np.nan)[caixa]
        o = np.isfinite(v)
        acc += np.bincount(flat[o], weights=v[o], minlength=acc.size); n += np.bincount(flat[o], minlength=acc.size)
    with np.errstate(invalid="ignore", divide="ignore"):
        g = (acc / n).reshape(len(latI), len(lonI))
    g[n.reshape(len(latI), len(lonI)) < 3] = np.nan
    smM.append(g)
CH = np.array(chuvaM, dtype="float64"); SM = np.array(smM)
CH[:, ~mceI] = np.nan; SM[:, ~mceI] = np.nan
mm = np.array([m for _, m in meses])
for k in (2, 3, 4, 5):
    s = mm == k
    CH[s] -= np.nanmean(CH[s], axis=0); SM[s] -= np.nanmean(SM[s], axis=0)
okI = np.isfinite(CH) & np.isfinite(SM)
CH[~okI] = np.nan; SM[~okI] = np.nan
print(f"meses fev-mai: {len(meses)}; celulas IMERG do CE com SMAP: {int(okI.any(0).sum())} ({time.time() - t0:.0f} s)")
Tc = curva(CH, SM, okI, [1, 2, 4, 8], lambda b: f"{b} x 0,1 grau (~{11 * b} km)", np.ones(len(meses), bool), minpts=8)
print(Tc[["bloco", "r_fev_mai", "meses_fev_mai"]].round(3).to_string(index=False))
# a mesma coisa so no nivel da media do CE (temporal): quanto o mes inteiro concorda
cm = np.nanmean(np.where(okI, CH, np.nan), axis=(1, 2)); sm_ = np.nanmean(np.where(okI, SM, np.nan), axis=(1, 2))
print(f"temporal (media do CE, anomalia do mes): r = {stats.pearsonr(cm, sm_).statistic:.3f} (n = {len(meses)} meses)")

# ---------------- D. Quixada 2023-2025
print("\n" + "=" * 25, "D. Quixada (2311306): o satelite viu as quebras de 2023-2025?", "=" * 25)
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha
p["ref"] = p.groupby("cod_local")["r"].transform(
    lambda v: pd.Series([np.median(np.delete(v.values, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=v.index))
p["razao"] = p.r / p.ref
p["cod"] = p.cod_local.astype(str).str[:7]
cent = mun.to_crs(5880).geometry.centroid
xy = np.c_[cent.x.values, cent.y.values]
iq = int(np.where(mun.codarea.values == "2311306")[0][0])
dq = np.sqrt(((xy - xy[iq]) ** 2).sum(1)) / 1000
viz = set(mun.codarea.values[(dq <= 50) & (dq > 0)])
# NDVI mar-mai por municipio (VIIRS e MODIS), anomalia contra os outros anos 2012-2025 e posto dentro do ano
res = abs(lon[1] - lon[0])
tr = from_origin(lon.min() - res / 2, lat.max() + res / 2, res, res)
lab = features.rasterize(((g, i + 1) for i, g in enumerate(mun.geometry)), out_shape=(len(lat), len(lon)), transform=tr,
                         fill=0, dtype="int32")
tab = {}
for nome, da in [("VIIRS", vi), ("MODIS", xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi)]:
    reg = {}
    for y in range(2012, 2026):
        a = da.sel(time=[pd.Timestamp(y, m, 1) for m in (3, 4, 5)]).mean("time").values.astype("float64")
        if np.nanmax(a) > 2:
            a = a / 10000.0
        okk = np.isfinite(a) & (lab > 0)
        s_ = np.bincount(lab[okk], weights=a[okk], minlength=len(mun) + 1); n_ = np.bincount(lab[okk], minlength=len(mun) + 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            reg[y] = (s_ / n_)[1:]
    Mn = pd.DataFrame(reg, index=mun.codarea.values).T
    an = Mn - (Mn.sum() - Mn) / (Mn.count() - 1)
    tab[nome] = an
linhas = []
for y in range(2016, 2026):
    pq = p[(p.ano == y)]
    rq = pq[pq.cod == "2311306"].razao
    lv = pq[pq.cod.isin(viz)]
    lin = {"ano": y, "razao_milho_Quixada": round(float(rq.iloc[0]), 2) if len(rq) else np.nan,
           "vizinhos50km_quebra": f"{(lv.razao < 0.5).mean():.0%} de {len(lv)}", "estado_quebra": f"{(pq.razao < 0.5).mean():.0%}"}
    for nome, an in tab.items():
        lin[f"NDVI_{nome}_anom"] = round(float(an.loc[y, "2311306"]), 3)
        lin[f"NDVI_{nome}_posto(1=mais seco)"] = f"{int(an.loc[y].rank().loc['2311306'])}/{an.loc[y].notna().sum()}"
    linhas.append(lin)
print(pd.DataFrame(linhas).to_string(index=False))
q = p[p.cod == "2311306"].set_index("ano")[["area_plantada_ha", "r", "razao"]].loc[2014:2025]
print("PAM Quixada milho (area plantada ha, rendimento t/ha, razao canonica):")
print(q.round(3).T.to_string())
print(f"tempo total {time.time() - t0:.0f} s")
