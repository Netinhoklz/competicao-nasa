"""Estrategista, RODADA 2 (dados novos), analise 2: o painel "hoje" (14/11/2026) com as missoes novas, e o relogio lento.

Para o slide 7 ("Today") precisamos de numeros de HOJE que se reproduzam, cada um com missao, data e comparacao:
  a) SMAP L4 zona da raiz (percentil) no ultimo granulo (10/11/2026): Ceara e Quixada, contra a mesma data em 2015-2025
     (2015 = o ano do El Nino 2015-16, antes da quebra de 2016).
  b) Isso preve a quadra? Correlacao ENTRE ANOS (n = 10) do SMAP de 10/nov (ano-1) com a fracao de municipios em quebra.
  c) GLDAS-2.2 CLSM (agua subterranea GWS e TWS; assimila GRACE -> concordancia circular): anomalia sazonal de jun-ago/2026
     (media de 3 meses, regra do hidrologo) em percentil contra 2003-2025; e o relogio lento: anomalia de GWS em dez (ano-1)
     contra a fracao de municipios em quebra do milho (2004-2025, n = 22 anos).
  d) VIIRS NDVI do Ceara em out/2026 contra out de 2012-2025.
  e) IMERG V07 Late 01/08-12/11/2026 no Ceara contra a mesma janela de 1998-2025 (IMERG diario historico). So contexto:
     a chuva de ago-out nao preve a quadra (rho -0,06, cetico_r3).
So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, municipios_ce_gdf, ceara_gdf

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import xarray as xr
from scipy.stats import spearmanr

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
QUIX = "2311306"

# ---------------- quebra canonica do milho -> fracao de municipios em quebra por ano
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha
p["ref"] = p.groupby("cod_local", group_keys=False).apply(
    lambda g: pd.Series([np.median(np.delete(g.r.values, i)) if len(g) > 5 else np.nan for i in range(len(g))],
                        index=g.index))
p = p.dropna(subset=["ref"])
p["quebra"] = (p.r / p.ref < 0.5).astype(int)
fq = p.groupby("ano").quebra.mean()

# ---------------- a) SMAP L4 no ultimo granulo
mun = municipios_ce_gdf().to_crs("EPSG:4326")
mun["cod"] = mun.codarea.astype(str).str[:7]
ds = xr.open_dataset(DADOS / "smap/smap_l4_diario_ne.nc")
_, iu = np.unique(ds.time.values, return_index=True)
ds = ds.isel(time=np.sort(iu))
pc = ds["sm_rootzone_pctl"].sel(lat=slice(-2.3, -8.2), lon=slice(-41.7, -36.8))
LA, LO = np.meshgrid(pc.lat.values, pc.lon.values, indexing="ij")
pts = gpd.GeoDataFrame({"i": np.arange(LA.size)}, geometry=gpd.points_from_xy(LO.ravel(), LA.ravel()), crs="EPSG:4326")
mapa = gpd.sjoin(pts, mun[["cod", "geometry"]], predicate="within").groupby("cod")["i"].apply(list).to_dict()
ultimo = pd.Timestamp(pc.time.values.max())
rz = ds["sm_rootzone"].sel(lat=slice(-2.3, -8.2), lon=slice(-41.7, -36.8))
ce_idx = sorted(set(i for v in mapa.values() for i in v))
# a0) quando o percentil existe no Ceara? fracao de pixels do CE com percentil valido, por mes (mesma em todo ano?)
t_all = pd.DatetimeIndex(pc.time.values)
dia15 = [i for i, x in enumerate(t_all) if x.day == 15]
a15 = pc.isel(time=dia15).values.reshape(len(dia15), -1)[:, ce_idx]
fv = pd.Series(np.isfinite(a15).mean(axis=1), index=t_all[dia15])
tab = fv.groupby(fv.index.month).agg(["mean", "min", "max"])
print("=" * 20, "a0) SMAP L4 sm_rootzone_pctl: fracao dos pixels do Ceara com percentil VALIDO (dia 15 de cada mes, 2015-2026)",
      "=" * 20)
print("  mes: " + " | ".join(f"{m:02d}: {r['mean']:.0%} ({r['min']:.0%}-{r['max']:.0%})" for m, r in tab.iterrows()))
print("  -> o percentil some na estacao seca (solo no piso todo ano); em nov o SMAP nao da percentil no Ceara.")
print("=" * 20, f"a) SMAP L4 umidade ABSOLUTA da zona da raiz (m3/m3), granulo de {ultimo:%d/%m/%Y}, mesma data 2015-2026",
      "=" * 20)
datas = [pd.Timestamp(a, ultimo.month, ultimo.day) for a in range(2015, 2027)]
sub = rz.sel(time=datas).values
res = []
for k, dt in enumerate(datas):
    flat = sub[k].ravel()
    v = pd.Series({c: np.nanmean(flat[idx]) for c, idx in mapa.items()})
    res.append({"data": f"{dt:%d/%m/%Y}", "quadra_seguinte": dt.year + 1, "media_mun": v.mean(), "quixada": v[QUIX],
                "fq_quadra_seguinte": fq.get(dt.year + 1, np.nan)})
R = pd.DataFrame(res)
print(R.round(4).to_string(index=False))
hoje = R.iloc[-1]
h = R.iloc[:-1]
print(f"  Hoje: media dos municipios = {hoje.media_mun:.4f} m3/m3 (faixa 2015-2025 na mesma data {h.media_mun.min():.4f}-"
      f"{h.media_mun.max():.4f}); acima de {(h.media_mun < hoje.media_mun).sum()} de {len(h)} anos. "
      f"Quixada = {hoje.quixada:.4f} (acima de {(h.quixada < hoje.quixada).sum()} de {len(h)}).")
ok = R.dropna(subset=["fq_quadra_seguinte"])
r, pv = spearmanr(ok.media_mun, ok.fq_quadra_seguinte)
print(f"  b) ENTRE anos: Spearman(SMAP raiz em {ultimo:%d/%m} do ano-1, fracao em quebra da quadra) = {r:+.2f} "
      f"(p {pv:.2f}, n = {len(ok)} anos)")
# a2) os portoes de 2026 (para o replay "a quadra que acabou de passar", sem arbitro do IBGE ainda)
for (m, d) in [(3, 19), (4, 30)]:
    fl = pc.sel(time=pd.Timestamp(2026, m, d)).values.ravel()
    v = pd.Series({c: np.nanmean(fl[idx]) for c, idx in mapa.items()})
    print(f"  Quadra 2026, portao {d:02d}/{m:02d}: {(v < 20).mean():.0%} dos municipios com percentil < 20 "
          f"(media {v.mean():.1f}; Quixada {v[QUIX]:.1f})")
ds.close()

# ---------------- c) GLDAS-2.2 CLSM (Ceara, mensal ja derivado)
print("\n" + "=" * 20, "c) GLDAS-2.2 CLSM, Ceara (assimila GRACE: concordancia com GRACE e parcialmente circular)", "=" * 20)
G = pd.read_parquet(D + "gldas_clsm_ce_mensal.parquet")
G["data"] = pd.to_datetime(G.data)
print("  variaveis:", sorted(G.variavel.unique()), "| fim:", G.data.max().date())
for var in ["GWS_tavg", "TWS_tavg", "SoilMoist_RZ_tavg"]:
    s = G[G.variavel == var].set_index("data")["valor"].sort_index()
    clim = s[s.index.year <= 2025].groupby(s[s.index.year <= 2025].index.month).mean()
    an = s - s.index.month.map(clim).values
    m3 = an.rolling(3).mean()
    jja = m3[m3.index.month == 8]
    v26 = jja.get(pd.Timestamp("2026-08-01"), np.nan)
    hist = jja[jja.index.year <= 2025]
    pct = (hist < v26).mean() * 100
    tend = np.polyfit(np.arange(len(s)) / 12, s.values, 1)[0]
    print(f"  {var:18s}: anomalia jun-ago/2026 = {v26:+.1f} mm -> percentil {pct:.0f} entre os jun-ago de "
          f"{hist.index.year.min()}-{hist.index.year.max()} (n = {len(hist)}); tendencia bruta {tend:+.1f} mm/ano")
    if var == "GWS_tavg":
        dez = an[an.index.month == 12]
        x = pd.Series(dez.values, index=dez.index.year + 1)
        j = pd.concat([x.rename("gws_dez"), fq.rename("fq")], axis=1).dropna()
        r, pv = spearmanr(j.gws_dez, j.fq)
        jj = j[j.index != 2012]
        r2, pv2 = spearmanr(jj.gws_dez, jj.fq)
        print(f"    relogio lento: Spearman(GWS dez ano-1, fracao em quebra) = {r:+.2f} (p {pv:.2f}, n = {len(j)} anos "
              f"{j.index.min()}-{j.index.max()}); sem 2012: {r2:+.2f} (p {pv2:.2f})")
        sm3 = G[G.variavel == "SoilMoist_RZ_tavg"].set_index("data")["valor"].sort_index()
        # fracao da variancia sazonal de GWS: memoria lenta (autocorrelacao lag 12 da anomalia)
        ac12 = an.autocorr(12)
        print(f"    autocorrelacao da anomalia de GWS a 12 meses = {ac12:+.2f} (memoria de um ano para o outro)")

# GRACE para comparar a mesma regra
Gr = pd.read_parquet(D + "grace_ce_mensal.parquet")
Gr["data"] = pd.to_datetime(Gr.data)
print("  GRACE CE variaveis:", Gr.variavel.unique()[:5], "| fim:", Gr.data.max().date())

# ---------------- d) VIIRS NDVI
print("\n" + "=" * 20, "d) VIIRS VNP13A3 NDVI, media do Ceara", "=" * 20)
V = pd.read_parquet(D + "viirs_ndvi_ce_mensal.parquet")
V["data"] = pd.to_datetime(V.data)
v = V.set_index("data")["valor"].sort_index()
vi = xr.open_dataset(DADOS / "viirs/vnp13a3_ndvi_evi_ceara_001deg.nc")
nv = vi["n_pixels_validos"].sel(time=["2026-09-01", "2026-10-01", "2026-11-01"]).astype("float32")
print("  pixels validos (media da grade) set/out/nov-2026:", [round(float(x), 2) for x in nv.mean(("lat", "lon")).values],
      " <- nov/2026 nao pode ser composicao mensal completa em 14/11; usar out/2026 como ultimo mes fechado")
vi.close()
for mes in (9, 10):
    x = v[v.index.month == mes]
    h = x[x.index.year <= 2025]
    v26 = x.get(pd.Timestamp(2026, mes, 1), np.nan)
    print(f"  NDVI {mes:02d}/2026 = {v26:.3f}; media {mes:02d}/2012-2025 = {h.mean():.3f} (dp {h.std():.3f}); "
          f"z = {(v26 - h.mean()) / h.std():+.2f}; acima de {(h < v26).sum()} de {len(h)} anos")

# ---------------- e) IMERG Late 2026 vs mesma janela 1998-2025
print("\n" + "=" * 20, "e) IMERG V07 Late 01/08-12/11/2026, Ceara (so contexto; nao preve a quadra)", "=" * 20)
ce = ceara_gdf().to_crs("EPSG:4326").geometry.union_all()
L = xr.open_dataset(DADOS / "imerg/imerg_v07_late_diario_ne_recente.nc")["precipitation"]
la, lo = np.meshgrid(L.lat.values, L.lon.values, indexing="ij")
mk = shapely.contains_xy(ce, lo, la)
tot26 = float(L.values[:, mk].mean(axis=1).sum())
fim = pd.Timestamp(L.time.values.max())
hist = {}
for a in range(1998, 2026):
    f = DADOS / f"imerg/imerg_ce_diario_{a}.nc"
    if not f.exists():
        continue
    h = xr.open_dataset(f)
    vn = [k for k in h.data_vars if h[k].ndim == 3][0]
    x = h[vn].sel(time=slice(f"{a}-08-01", f"{a}-{fim.month:02d}-{fim.day:02d}"))
    latn = "lat" if "lat" in x.dims else "latitude"
    lonn = "lon" if "lon" in x.dims else "longitude"
    la2, lo2 = np.meshgrid(x[latn].values, x[lonn].values, indexing="ij")
    mk2 = shapely.contains_xy(ce, lo2, la2)
    arr = x.transpose("time", latn, lonn).values
    hist[a] = float(arr[:, mk2].mean(axis=1).sum())
    h.close()
H = pd.Series(hist)
print(f"  2026 (Late): {tot26:.0f} mm de 01/08 a {fim:%d/%m}; 1998-2025 (diario historico): mediana {H.median():.0f} mm, "
      f"faixa {H.min():.0f}-{H.max():.0f}; 2026 = {tot26 / H.median():.0%} da mediana; acima de {(H < tot26).sum()} de {len(H)} anos")
print("  (Late x Final: produtos diferentes; leitura so de ordem de grandeza)")
