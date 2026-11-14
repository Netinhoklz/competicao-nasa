"""Conselho - Especialista em sensoriamento remoto e modelos de fundacao.

Pergunta: o TVDI a 1 km (MODIS LST x NDVI) carrega informacao sobre a umidade do solo de um modelo NASA
(GLDAS-2.1 Noah 0,25 grau)? E quanto da variabilidade de secura a 1 km fica ESCONDIDA dentro de um pixel de
9 km (SMAP) ou 25 km (GLDAS)? Isso decide se vale a pena fazer downscaling do SMAP com termal+optico.

Metodo:
1. TVDI mensal (2000-2026) na caixa do Ceara com bordas quente/fria por mes (mesma funcao da secao 9.8.5).
2. Agregacao para a grade GLDAS 0,25 grau (celulas com >= 40% de pixels validos).
3. Por mes: Spearman espacial entre TVDI medio da celula e umidade GLDAS 0-10 cm / zona da raiz;
   o mesmo para NDVI e LST sozinhos (controle: o TVDI acrescenta algo?).
4. Decomposicao da variancia do TVDI a 1 km: fracao dentro de blocos de 9 km (9x9 pixels) e de 25 km.
5. Serie temporal: anomalia do TVDI medio x anomalia GLDAS e x POWER GWETROOT.
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

nd = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi
ls = xr.open_dataset(DADOS / "modis/mod11a2_lst_mensal_001deg.nc").lst_dia
nd, ls = xr.align(nd, ls, join="inner")
gl = xr.open_dataset(DADOS / "gldas/gldas_noah025_mensal_ne.nc")
print("MODIS meses comuns:", nd.time.size, str(nd.time.values[0])[:7], "a", str(nd.time.values[-1])[:7])

lat = nd.lat.values
lon = nd.lon.values
# indice da celula GLDAS (centros -18.375.., -48.625..; bordas a cada 0,25 grau)
gi = np.floor((lat + 18.5) / 0.25).astype(int)
gj = np.floor((lon + 48.75) / 0.25).astype(int)
GI, GJ = np.meshgrid(gi, gj, indexing="ij")
glat = -18.375 + 0.25 * np.arange(70)
glon = -48.625 + 0.25 * np.arange(56)
cel = GI * 1000 + GJ
# blocos de 9x9 pixels (~9-10 km, escala SMAP)
bi = (np.arange(lat.size) // 9)[:, None] * 1000 + (np.arange(lon.size) // 9)[None, :]


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
    t = (l - (af * n + bf)) / np.where(den > 0.5, den, np.nan)
    return np.clip(t, 0, 1)


def media_por_grupo(chave, val, minimo):
    ok = np.isfinite(val)
    s = pd.DataFrame({"k": chave[ok], "v": val[ok]}).groupby("k")["v"].agg(["mean", "var", "count"])
    return s[s["count"] >= minimo]


linhas, serie = [], []
NDV, LSV = nd.values, ls.values
for t in range(nd.time.size):
    data = pd.Timestamp(nd.time.values[t])
    n, l = NDV[t], LSV[t]
    tv = tvdi(n, l)
    if tv is None:
        continue
    g = media_por_grupo(cel, tv, 250)
    if len(g) < 30:
        continue
    gn = media_por_grupo(cel, n, 250)["mean"]
    glst = media_por_grupo(cel, l, 250)["mean"]
    ii, jj = (g.index.values // 1000), (g.index.values % 1000)
    try:
        gsel = gl.sel(time=data, method="nearest", tolerance=np.timedelta64(20, "D"))
    except KeyError:
        continue
    sm = gsel.SoilMoi0_10cm_inst.values[ii, jj]
    rz = gsel.RootMoist_inst.values[ii, jj]
    ok = np.isfinite(sm) & np.isfinite(rz)
    if ok.sum() < 30:
        continue
    r_tv_sm = stats.spearmanr(g["mean"].values[ok], sm[ok])[0]
    r_tv_rz = stats.spearmanr(g["mean"].values[ok], rz[ok])[0]
    r_nd_sm = stats.spearmanr(gn.reindex(g.index).values[ok], sm[ok], nan_policy="omit")[0]
    r_ls_sm = stats.spearmanr(glst.reindex(g.index).values[ok], sm[ok], nan_policy="omit")[0]
    # decomposicao de variancia do TVDI 1 km
    v_tot = np.nanvar(tv)
    b9 = media_por_grupo(bi, tv, 20)
    b25 = g
    w9 = np.average(b9["var"], weights=b9["count"]) / v_tot
    w25 = np.average(b25["var"], weights=b25["count"]) / v_tot
    linhas.append({"data": data, "n_cel": int(ok.sum()), "rho_TVDI_sm0_10": r_tv_sm, "rho_TVDI_raiz": r_tv_rz,
                   "rho_NDVI_sm0_10": r_nd_sm, "rho_LST_sm0_10": r_ls_sm,
                   "frac_var_dentro_9km": w9, "frac_var_dentro_25km": w25})
    serie.append({"data": data, "tvdi": float(np.nanmean(tv)), "sm0_10": float(np.nanmean(sm[ok])), "raiz": float(np.nanmean(rz[ok]))})

R = pd.DataFrame(linhas).set_index("data")
S = pd.DataFrame(serie).set_index("data")
print(f"\nMeses analisados: {len(R)}  (celulas GLDAS por mes: mediana {int(R.n_cel.median())})")
print("\n== Correlacao ESPACIAL (Spearman, celulas 0,25 grau) - mediana e fracao de meses com rho < -0,3 ==")
for c in ["rho_TVDI_sm0_10", "rho_TVDI_raiz", "rho_NDVI_sm0_10", "rho_LST_sm0_10"]:
    print(f"  {c:18s} mediana {R[c].median():+.2f}   IQR [{R[c].quantile(.25):+.2f}, {R[c].quantile(.75):+.2f}]   "
          f"meses rho<-0,3: {(R[c] < -0.3).mean():.0%}   rho>+0,3: {(R[c] > 0.3).mean():.0%}")
print("\nPor mes do ano (mediana):")
tab = R.groupby(R.index.month)[["rho_TVDI_sm0_10", "rho_NDVI_sm0_10", "rho_LST_sm0_10", "frac_var_dentro_9km", "frac_var_dentro_25km"]].median().round(2)
print(tab.to_string())
print("\n== Decomposicao da variancia do TVDI a 1 km ==")
print(f"  fracao da variancia DENTRO de blocos de ~9 km (pixel SMAP): mediana {R.frac_var_dentro_9km.median():.0%} "
      f"(IQR {R.frac_var_dentro_9km.quantile(.25):.0%}-{R.frac_var_dentro_9km.quantile(.75):.0%})")
print(f"  fracao da variancia DENTRO de celulas de 25 km (GLDAS):    mediana {R.frac_var_dentro_25km.median():.0%}")

# serie temporal: anomalias
def anom(s):
    return s - s.groupby(s.index.month).transform("mean")

pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw["data"] = pd.to_datetime(pw["data"]).dt.to_period("M").dt.to_timestamp()
gwr = pw[pw.variavel == "GWETROOT"].set_index("data")["valor"]
gwt = pw[pw.variavel == "GWETTOP"].set_index("data")["valor"]
im = pd.read_parquet(DERIV / "imerg_ce_mensal.parquet")
im["data"] = pd.to_datetime(im["data"]).dt.to_period("M").dt.to_timestamp()
ch = im[im.variavel == "precip_total"].set_index("data")["valor"]
S.index = S.index.to_period("M").to_timestamp()
A = pd.DataFrame({"tvdi": anom(S.tvdi), "gldas_sm0_10": anom(S.sm0_10), "gldas_raiz": anom(S.raiz),
                  "power_gwetroot": anom(gwr), "power_gwettop": anom(gwt), "imerg_chuva": anom(ch),
                  "imerg_chuva_3m": anom(ch.rolling(3).sum())}).dropna()
print(f"\n== Correlacao TEMPORAL das anomalias (media da caixa, {len(A)} meses) ==")
for c in ["gldas_sm0_10", "gldas_raiz", "power_gwettop", "power_gwetroot", "imerg_chuva", "imerg_chuva_3m"]:
    r, p = stats.pearsonr(A.tvdi, A[c])
    print(f"  TVDI x {c:15s} r = {r:+.2f} (p = {p:.1e})")
# seca 2012-2017 vs resto
seca = (S.index.year >= 2012) & (S.index.year <= 2017)
print(f"\nTVDI medio: seca 2012-2017 = {S.tvdi[seca].mean():.3f}  vs  demais anos = {S.tvdi[~seca].mean():.3f}")
R.to_csv(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/sr_fundacao_tvdi_gldas_mensal.csv")
