"""Ecologo (rodada 2 do conselho, dados novos) - passo 0: painel municipio x mes para o indice de combustivel/secura.

Monta, para os 184 municipios do Ceara e cada mes de 2012-01 a 2026-10:
  - focos FIRMS VIIRS S-NPP (type 0 = vegetacao, confianca n/h), 2012-2025 (o ano corrente nao tem arquivo anual);
  - NDVI VIIRS VNP13A3 v002 mensal 1 km (grade 0,01 grau), media dos pixels validos do municipio
    (nov/2026 fica fora: o granulo A2026305 foi produzido em 13/11/2026, antes do fim do mes);
  - SMAP L4 SPL4SMGP v008 (13:30 UTC, 9 km): media mensal de sm_surface, sm_rootzone e sm_rootzone_pctl
    das celulas cujo centro cai no municipio (se nenhuma, a celula mais proxima do ponto representativo); 2015-04 em diante;
  - IMERG (via POWER, ja agregado por municipio em saidas/chuva_mun_diaria.parquet, ate 14/09/2026): chuva do mes,
    chuva dos 60 dias que terminam no fim do mes e dias desde o ultimo dia >= 5 mm (no fim do mes).
Saida: saidas/v2_ecologo_painel_mun_mes.parquet (arquivo novo, so deste ecologo).
O SMAP L3 ainda nao foi consolidado (smap_l3_diario_ne.nc nao existe as 10h de 14/11); so o L4 entra.
"""
import sys
import time

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy.spatial import cKDTree

t0 = time.time()
AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
mun = gpd.read_file(REF / "ceara_municipios.geojson").to_crs(4326)
mun["codarea"] = mun.codarea.astype(str)
cods = mun.codarea.values
idx_cod = {c: i for i, c in enumerate(cods)}
rep = mun.geometry.representative_point()
rep_xy = np.c_[rep.y.values, rep.x.values]


def rotular(lat, lon):
    """Rotula pontos de uma grade (lat, lon 1-D) com o indice do municipio (-1 fora)."""
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(LO.ravel(), LA.ravel()), crs=4326)
    j = gpd.sjoin(pts, mun[["codarea", "geometry"]], predicate="within")
    lab = np.full(LA.size, -1, dtype=int)
    lab[j.index.values] = j.codarea.map(idx_cod).values
    return lab.reshape(LA.shape), LA, LO


def media_por_rotulo(arr3, lab, n):
    """arr3 (t, y, x) -> (t, n) media ignorando NaN por rotulo."""
    m = lab.ravel() >= 0
    L = lab.ravel()[m]
    out = np.full((arr3.shape[0], n), np.nan)
    for k in range(arr3.shape[0]):
        v = arr3[k].ravel()[m]
        ok = np.isfinite(v)
        s = np.bincount(L[ok], weights=v[ok], minlength=n)
        c = np.bincount(L[ok], minlength=n)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[k] = np.where(c > 0, s / c, np.nan)
    return out


# ---------------- FIRMS ----------------
v = pd.read_parquet(DADOS / "viirs" / "firms_viirs_snpp_nordeste.parquet",
                    columns=["latitude", "longitude", "acq_date", "type", "uf", "confidence"])
v = v[(v.uf == 23) & (v["type"] == 0) & (v.confidence.astype(str).str.lower().isin(["n", "h"]))].copy()
pts = gpd.GeoDataFrame(v, geometry=gpd.points_from_xy(v.longitude, v.latitude), crs=4326)
pts = gpd.sjoin(pts, mun[["codarea", "geometry"]], predicate="within")
pts["mes"] = pd.to_datetime(pts.acq_date).dt.to_period("M").dt.to_timestamp()
focos = pts.groupby(["codarea", "mes"]).size().rename("focos")
print(f"FIRMS CE type0 n/h: {len(v)} focos; dentro de municipio: {len(pts)} ({time.time() - t0:.0f}s)")

meses = pd.date_range("2012-01-01", "2026-10-01", freq="MS")
P = pd.MultiIndex.from_product([cods, meses], names=["codarea", "mes"]).to_frame(index=False)
P = P.merge(focos.reset_index(), on=["codarea", "mes"], how="left")
P.loc[P.mes.dt.year <= 2025, "focos"] = P.loc[P.mes.dt.year <= 2025, "focos"].fillna(0)

# ---------------- VIIRS NDVI ----------------
vd = xr.open_dataset(DADOS / "viirs" / "vnp13a3_ndvi_evi_ceara_001deg.nc")
lab_v, _, _ = rotular(vd.lat.values, vd.lon.values)
tv = pd.to_datetime(vd.time.values)
sel = tv <= pd.Timestamp("2026-10-01")
nd = vd.ndvi.isel(time=np.where(sel)[0]).values
ndm = media_por_rotulo(nd, lab_v, len(cods))
del nd
nv = pd.DataFrame(ndm, index=tv[sel], columns=cods).stack().rename("ndvi").reset_index()
nv.columns = ["mes", "codarea", "ndvi"]
P = P.merge(nv, on=["codarea", "mes"], how="left")
print(f"VIIRS NDVI ok; municipio-meses sem NDVI: {P.ndvi.isna().mean() * 100:.1f}% ({time.time() - t0:.0f}s)")

# ---------------- SMAP L4 ----------------
sd = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
sd = sd.sel(lat=slice(-2.4, -8.1), lon=slice(-41.6, -36.9))
lab_s, LA, LO = rotular(sd.lat.values, sd.lon.values)
# municipios sem centro de celula: celula valida mais proxima do ponto representativo
amostra = sd.sm_rootzone.isel(time=10).values
valid = np.isfinite(amostra)
tree = cKDTree(np.c_[LA[valid], LO[valid]])
faltam = sorted(set(range(len(cods))) - set(np.unique(lab_s[lab_s >= 0])))
extra = {}
for k in faltam:
    _, ii = tree.query(rep_xy[k])
    extra[k] = (np.where(valid.ravel())[0][ii])
print(f"SMAP: {(lab_s >= 0).sum()} celulas em municipios; {len(faltam)} municipios pela celula mais proxima")
sm_mes = {}
for var in ("sm_surface", "sm_rootzone", "sm_rootzone_pctl"):
    x = sd[var].load()
    xm = x.resample(time="MS").mean()
    arr = xm.values
    out = media_por_rotulo(arr, lab_s, len(cods))
    for k, fi in extra.items():
        out[:, k] = arr.reshape(arr.shape[0], -1)[:, fi]
    sm_mes[var] = pd.DataFrame(out, index=pd.to_datetime(xm.time.values), columns=cods)
    print(f"  {var} ok ({time.time() - t0:.0f}s)")
for var, df in sm_mes.items():
    s = df.stack().rename(var).reset_index()
    s.columns = ["mes", "codarea", var]
    P = P.merge(s, on=["codarea", "mes"], how="left")
# a ultima granula e 10/11/2026: novembro/2026 fica fora (parcial) pelo corte do painel em 2026-10

# ---------------- IMERG municipal ----------------
ch = pd.read_parquet(AN / "saidas" / "chuva_mun_diaria.parquet")
ch.index = pd.to_datetime(ch.index)
pm = ch.resample("MS").sum()
pm.loc[pd.Timestamp("2026-09-01")] = np.nan  # setembro/2026 incompleto (ate 14/09)
p60 = ch.rolling(60, min_periods=55).sum()
fim = ch.index.to_series().groupby(ch.index.to_period("M")).max()
p60_fim = p60.loc[fim.values]
p60_fim.index = fim.index.to_timestamp()
molhado = (ch >= 5).astype(int)
ult = pd.DataFrame(np.where(molhado.values == 1, np.arange(len(ch))[:, None], np.nan), index=ch.index,
                   columns=ch.columns).ffill()
seco = (np.arange(len(ch))[:, None] - ult)
seco_fim = seco.loc[fim.values]
seco_fim.index = fim.index.to_timestamp()
for nome, df in (("P_mes", pm), ("P_60", p60_fim), ("seco_dias", seco_fim)):
    s = df.stack().rename(nome).reset_index()
    s.columns = ["mes", "codarea", nome]
    P = P.merge(s, on=["codarea", "mes"], how="left")
P.loc[P.mes >= pd.Timestamp("2026-09-01"), ["P_mes", "P_60", "seco_dias"]] = np.nan

P["ano"] = P.mes.dt.year
P["m"] = P.mes.dt.month
out = AN / "saidas" / "v2_ecologo_painel_mun_mes.parquet"
P.to_parquet(out, index=False)
print(f"Painel: {len(P)} linhas, {P.codarea.nunique()} municipios, {P.mes.min():%Y-%m} a {P.mes.max():%Y-%m} -> {out}")
print(P.groupby("ano")[["focos", "ndvi", "sm_rootzone_pctl", "P_mes"]].agg(
    {"focos": "sum", "ndvi": "mean", "sm_rootzone_pctl": "mean", "P_mes": "sum"}).round(3).to_string())
print(f"Tempo total {time.time() - t0:.0f}s")
