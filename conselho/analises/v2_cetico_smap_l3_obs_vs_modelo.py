"""Cetico, rodada 2: quanto do SMAP L4 e OBSERVACAO e quanto e MODELO, medido com o SMAP L3 (retrieval do radiometro).

O consolidado do L3 (smap_l3_diario_ne.nc) ainda nao existe; leio SO-LEITURA os recortes diarios ja baixados em
E:/campeonato-nasa/dados/smap/l3_diario/ (o download continua; arquivos ilegiveis sao pulados).
- L3 diario = media de AM e PM com qualidade recomendada (bit 0 = 0) e 0 < sm < 1; municipio = media dos pixels 9 km.
- A. cobertura do L3 por municipio-dia; r(L3, L4 superficie) nas anomalias (serie do estado e dentro do dia).
- B. a anomalia da superficie do L4 e explicada pela chuva IMERG (janelas 1-30 d) e, alem dela, pelo L3?
     R2 deixando o ano de fora; Delta R2 = informacao que o L4 compartilha com a observacao alem da chuva.
- C. portoes 19/mar e 30/abr: L3 (media dos 7 dias ate o portao, % da mediana dos outros anos) x L4 zona da raiz
     (pctl) x chuva IMERG, pareados nos mesmos municipio-anos, quebra canonica do milho.
So le arquivos; nao escreve nada.
"""
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import h5py
import numpy as np
import pandas as pd
import shapely
import xarray as xr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
t0 = time.time()
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
L3D = Path("E:/campeonato-nasa/dados/smap/l3_diario")
rng = np.random.default_rng(0)

lat = np.load(L3D / "lat_linhas.npy")
lon = np.load(L3D / "lon_colunas.npy")
ri = np.flatnonzero((lat <= -2.5) & (lat >= -8.1))
ci = np.flatnonzero((lon >= -41.6) & (lon <= -37.0))
lo, la = np.meshgrid(lon[ci], lat[ri])
mun = municipios_ce_gdf()
mun["cod"] = mun.codarea.astype(str)
W = np.zeros((len(mun), lo.size))
for i, g in enumerate(mun.geometry):
    m = shapely.contains_xy(g, lo, la).ravel()
    if m.sum() == 0:
        c = g.centroid
        m = np.zeros(lo.size, bool)
        m[np.argmin((lo.ravel() - c.x) ** 2 + (la.ravel() - c.y) ** 2)] = True
    W[i, m] = 1.0 / m.sum()


def agrega_mat(v):
    """v (t, ncel) -> (t, nmun) media com renormalizacao dos NaN."""
    ok = np.isfinite(v)
    num = np.where(ok, v, 0) @ W.T
    den = ok.astype(float) @ W.T
    return num / np.where(den > 0, den, np.nan), den


arqs = sorted(L3D.glob("SMAP_L3_SM_P_E_*_recorte.nc4"))
datas, mats, pulados = [], [], 0
for f in arqs:
    try:
        with h5py.File(f, "r") as h:
            am = h["Soil_Moisture_Retrieval_Data_AM/soil_moisture"][ri.min():ri.max() + 1, ci.min():ci.max() + 1]
            qa = h["Soil_Moisture_Retrieval_Data_AM/retrieval_qual_flag"][ri.min():ri.max() + 1, ci.min():ci.max() + 1]
            pm = h["Soil_Moisture_Retrieval_Data_PM/soil_moisture_pm"][ri.min():ri.max() + 1, ci.min():ci.max() + 1]
            qp = h["Soil_Moisture_Retrieval_Data_PM/retrieval_qual_flag_pm"][ri.min():ri.max() + 1, ci.min():ci.max() + 1]
    except Exception:
        pulados += 1
        continue
    am = np.where((am > 0) & (am < 1) & ((qa & 1) == 0), am, np.nan)
    pm = np.where((pm > 0) & (pm < 1) & ((qp & 1) == 0), pm, np.nan)
    v = np.nanmean(np.stack([am, pm]), axis=0)
    datas.append(pd.Timestamp(f.name.split("_")[5]))
    mats.append(v.ravel())
V3 = np.vstack(mats)
L3, den3 = agrega_mat(V3)
L3 = pd.DataFrame(L3, index=pd.DatetimeIndex(datas), columns=mun.cod.values)
L3 = L3[~L3.index.duplicated()]
print(f"[{time.time() - t0:.0f}s] L3 lido: {len(L3)} dias ({L3.index.min():%Y-%m-%d} -> {L3.index.max():%Y-%m-%d}); arquivos pulados {pulados}")
print(f"  A. cobertura: municipio-dias com L3 valido = {np.isfinite(L3.values).mean():.1%}")

# L4 superficie e zona da raiz nas mesmas datas
l4 = xr.open_dataset("E:/campeonato-nasa/dados/smap/smap_l4_diario_ne.nc")
_t = pd.to_datetime(l4.time.values)
l4 = l4.isel(time=np.flatnonzero(~_t.duplicated()))
l4 = l4.sel(lat=slice(-2.5, -8.1), lon=slice(-41.6, -37.0))
assert np.allclose(l4.lat.values, lat[ri], atol=1e-3) and np.allclose(l4.lon.values, lon[ci], atol=1e-3), "grades L3/L4 diferentes"
sel = l4.sel(time=L3.index)
S4 = pd.DataFrame(agrega_mat(sel.sm_surface.values.reshape(len(L3), -1))[0], index=L3.index, columns=L3.columns)
PC4 = pd.DataFrame(agrega_mat(sel.sm_rootzone_pctl.values.reshape(len(L3), -1))[0], index=L3.index, columns=L3.columns)
print(f"[{time.time() - t0:.0f}s] L4 nas mesmas datas")


def anom(df):
    mes = df.index.month
    return df - df.groupby(mes).transform("mean")


a3, a4 = anom(L3), anom(S4)
e3, e4 = a3.mean(axis=1), a4.mean(axis=1)
ok = e3.notna() & e4.notna()
print(f"  r(L3, L4 superficie), anomalia da media do estado, diaria: {np.corrcoef(e3[ok], e4[ok])[0, 1]:.3f} (n = {ok.sum()} dias)")
d3 = a3.sub(a3.mean(axis=1), axis=0)
d4 = a4.sub(a4.mean(axis=1), axis=0)
mk = np.isfinite(d3.values) & np.isfinite(d4.values)
print(f"  r(L3, L4 superficie) dentro do dia (ordem entre municipios): {np.corrcoef(d3.values[mk], d4.values[mk])[0, 1]:.3f} (n = {mk.sum()})")
print(f"  vies medio L3 - L4 superficie: {np.nanmean(L3.values - S4.values):+.3f} m3/m3")

# B. L4 superficie ~ chuva IMERG (+ L3)
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
cs = chuva.cumsum()
JAN = [1, 3, 7, 15, 30]
idx = L3.index[L3.index <= chuva.index.max()]
Xr = [(cs - cs.shift(k)).reindex(idx)[L3.columns] for k in JAN]
Xr = [x - x.groupby(x.index.month).transform("mean") for x in Xr]
y = a4.loc[idx].values.ravel()
x3 = a3.loc[idx].values.ravel()
XR = np.column_stack([x.values.ravel() for x in Xr])
anos = np.repeat(idx.year.values, L3.shape[1])
dia = np.repeat(np.arange(len(idx)), L3.shape[1])
okb = np.isfinite(y) & np.isfinite(x3) & np.isfinite(XR).all(1)
y, x3, XR, anos, dia = y[okb], x3[okb], XR[okb], anos[okb], dia[okb]


def r2_loyo(yy, XX, aa):
    pred = np.full(len(yy), np.nan)
    for a in np.unique(aa):
        tr, te = aa != a, aa == a
        pred[te] = LinearRegression().fit(XX[tr], yy[tr]).predict(XX[te])
    return 1 - np.sum((yy - pred) ** 2) / np.sum((yy - yy.mean()) ** 2)


r_ch = r2_loyo(y, XR, anos)
r_ch3 = r2_loyo(y, np.column_stack([XR, x3]), anos)
r_3 = r2_loyo(y, x3[:, None], anos)
dm = lambda v: v - pd.Series(v).groupby(dia).transform("mean").values
yd, x3d = dm(y), dm(x3)
XRd = np.column_stack([dm(XR[:, k]) for k in range(XR.shape[1])])
rd_ch, rd_ch3 = r2_loyo(yd, XRd, anos), r2_loyo(yd, np.column_stack([XRd, x3d]), anos)
print(f"\n  B. anomalia da superficie do L4 (municipio-dia com L3 valido, n = {len(y)}), R2 ano fora:")
print(f"     so chuva IMERG (1-30 d): {r_ch:.3f} | so L3: {r_3:.3f} | chuva + L3: {r_ch3:.3f} (Delta pela observacao = {r_ch3 - r_ch:+.3f})")
print(f"     dentro do dia: so chuva {rd_ch:.3f} | chuva + L3 {rd_ch3:.3f} (Delta = {rd_ch3 - rd_ch:+.3f})")

# C. portoes
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha
p["ref"] = p.groupby("cod_local", group_keys=False).apply(
    lambda g: pd.Series([np.median(np.delete(g.r.values, i)) if len(g) > 5 else np.nan for i in range(len(g))], index=g.index))
p["quebra"] = (p.r / p.ref < 0.5).astype(int)
p["cod"] = p.cod_local.astype(str).str[:7]
base = p.dropna(subset=["ref"])[["cod", "ano", "quebra"]]
anos_im = list(range(1998, 2026))
print("\n  C. portoes (pareado; L3 = media dos 7 dias ate o portao em % da mediana dos outros anos):")
for gn, (m, d) in {"19/mar": (3, 19), "30/abr": (4, 30)}.items():
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_im}).T
    pc = pd.DataFrame({a: ac.loc[a] / ac.drop(index=a).median() for a in anos_im}).T
    yrs = [a for a in range(2016, 2026) if pd.Timestamp(a, m, d) <= L3.index.max()]
    l3g = pd.DataFrame({a: L3.loc[pd.Timestamp(a, m, d) - pd.Timedelta(days=6):pd.Timestamp(a, m, d)].mean() for a in yrs}).T
    l3r = pd.DataFrame({a: l3g.loc[a] / l3g.drop(index=a).median() for a in yrs}).T
    pcg = pd.DataFrame({a: PC4.loc[pd.Timestamp(a, m, d)] for a in yrs if pd.Timestamp(a, m, d) in PC4.index}).T
    # linha de base extra (nao e configuracao candidata): chuva dos ultimos 15 dias ate o portao, % do normal
    ac15 = pd.DataFrame({a: chuva.loc[pd.Timestamp(a, m, d) - pd.Timedelta(days=14):pd.Timestamp(a, m, d)].sum() for a in anos_im}).T
    pc15 = pd.DataFrame({a: ac15.loc[a] / ac15.drop(index=a).median().replace(0, np.nan) for a in anos_im}).T
    df = base[base.ano.isin(yrs)].copy()
    df["chuva"] = [pc.loc[a, c] if c in pc.columns else np.nan for a, c in zip(df.ano, df.cod)]
    df["c15"] = [pc15.loc[a, c] if c in pc15.columns else np.nan for a, c in zip(df.ano, df.cod)]
    df["l3"] = [l3r.loc[a, c] if c in l3r.columns else np.nan for a, c in zip(df.ano, df.cod)]
    df["l4pc"] = [pcg.loc[a, c] if (a in pcg.index and c in pcg.columns) else np.nan for a, c in zip(df.ano, df.cod)]
    df = df.dropna()
    cols = {"chuva IMERG": -df.chuva.clip(upper=3), "chuva 15 d": -df.c15.clip(upper=5), "SMAP L3 (observacao, 0-5 cm)": -df.l3, "SMAP L4 zona da raiz pctl": -df.l4pc}
    g = {a: df.index[df.ano == a] for a in df.ano.unique()}
    bs = []
    for _ in range(1000):
        ii = np.concatenate([g[a] for a in rng.choice(list(g), len(g))])
        if df.quebra[ii].nunique() == 2:
            bs.append([roc_auc_score(df.quebra[ii], v[ii]) for v in cols.values()])
    bs = np.array(bs)
    txt = " | ".join(f"{k}: {roc_auc_score(df.quebra, v):.3f} [{np.percentile(bs[:, i], 5):.2f},{np.percentile(bs[:, i], 95):.2f}]"
                     for i, (k, v) in enumerate(cols.items()))
    print(f"     {gn} (anos {yrs[0]}-{yrs[-1]}, n = {len(df)}, quebras {df.quebra.sum()}): {txt}")
print(f"\n[{time.time() - t0:.0f}s] fim")
