"""Hidrólogo, rodada 2 do conselho, análise A1: cinco fontes de "água na zona da raiz" no Ceará.

Fontes (média do Ceará, máscara IBGE nos centros de cada grade):
  1. SMAP L4 SPL4SMGP v008, sm_rootzone (0-100 cm, m3/m3), diário 13:30 UTC, 2015-03-31 -> 2026-11-10.
  2. M1 em modo contínuo: o mesmo balde FAO-56 do hidrólogo (CN 75, AWC 100 mm/m, p 0,55), com Zr = 1,0 m para casar
     com os 0-100 cm do SMAP e Kc = 1,0 fixo (pré-registrado, sem ajuste). Chuva IMERG municipal (cache do estrategista,
     até 14/09/2026), ET0 FAO-56 do POWER (célula válida mais próxima). Saída: fração de água disponível (0-1).
  3. GLDAS-2.1 Noah, RootMoist_inst (mm), mensal até 2026-07.
  4. GLDAS-2.2 CLSM, SoilMoist_RZ_tavg (mm, 0-100 cm), diário até 2026-08-31.
  5. POWER GWETROOT (umidade relativa da zona da raiz, 0-1; vem do MERRA-2), diário.

Medidas: r bruto (com ciclo sazonal), r das anomalias (ciclo por dia do ano removido), defasagem pela correlação
cruzada das anomalias, memória (lag de e-folding da autocorrelação), viés volumétrico onde há m3/m3, pico climatológico,
e concordância ENTRE ANOS nos portões 19/mar e 30/abr (unidade = ano; n = 11-12).
Também grava a série municipal diária do SMAP L4 (zona da raiz e percentil) para as análises A2 e A3.
Ressalva de independência: SMAP L4, CLSM e o MERRA-2 (fonte do GWETROOT) usam o modelo Catchment da NASA; o Noah e
o balde M1 são físicas diferentes. Concordância entre os três primeiros é em parte física compartilhada.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import shapely
import xarray as xr
from scipy import stats

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220)
AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
SAI = AN / "saidas"

mun = municipios_ce_gdf()
cod_col = next(c for c in mun.columns if "cod" in c.lower() or c.lower() in ("id", "codarea"))
mun["cod"] = mun[cod_col].astype(str).str[:7]
CEU = ceara_gdf().union_all()


def mascara_ce(lat, lon):
    lo, la = np.meshgrid(lon, lat)
    return shapely.contains_xy(CEU, lo, la)


def media_ce(da, lat="lat", lon="lon"):
    m = xr.DataArray(mascara_ce(da[lat].values, da[lon].values), coords={lat: da[lat], lon: da[lon]}, dims=(lat, lon))
    s = da.where(m).mean((lat, lon)).to_series()
    s.index = pd.to_datetime(s.index).normalize()
    return s.groupby(level=0).mean()


# ------------------------------------------------------------------ 1. SMAP L4 (só o recorte do Ceará)
with Cronometro("SMAP L4"):
    l4 = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")[["sm_rootzone", "sm_rootzone_pctl", "sm_surface"]]
    l4 = l4.sel(lat=slice(-2.4, -8.1), lon=slice(-41.6, -36.9)).load()
    l4["time"] = pd.DatetimeIndex(l4.time.values).normalize()
    l4 = l4.groupby("time").mean()  # há 4 datas repetidas no arquivo
    smap_rz = media_ce(l4.sm_rootzone)
    smap_pc = media_ce(l4.sm_rootzone_pctl)
    # série municipal (centros SMAP dentro do município; senão, o mais próximo do centróide)
    LO, LA = np.meshgrid(l4.lon.values, l4.lat.values)
    rz = l4.sm_rootzone.values.reshape(l4.sizes["time"], -1)
    pc = l4.sm_rootzone_pctl.values.reshape(l4.sizes["time"], -1)
    mun_rz, mun_pc, ncel = {}, {}, []
    for cod, g in zip(mun.cod, mun.geometry):
        m = shapely.contains_xy(g, LO.ravel(), LA.ravel())
        if m.sum() == 0:
            c = g.centroid
            m = np.zeros(LO.size, bool)
            m[np.argmin((LO.ravel() - c.x) ** 2 + (LA.ravel() - c.y) ** 2)] = True
        ncel.append(int(m.sum()))
        mun_rz[cod] = np.nanmean(rz[:, m], 1)
        mun_pc[cod] = np.nanmean(pc[:, m], 1)
    tS = pd.DatetimeIndex(l4.time.values)
    pd.DataFrame(mun_rz, index=tS).to_parquet(SAI / "v2_hidrologo_smap_rz_mun_diario.parquet")
    pd.DataFrame(mun_pc, index=tS).to_parquet(SAI / "v2_hidrologo_smap_pctl_mun_diario.parquet")
print(f"SMAP L4: {len(tS)} dias únicos {tS.min():%Y-%m-%d} -> {tS.max():%Y-%m-%d}; células por município: "
      f"mediana {np.median(ncel):.0f}, mín {min(ncel)}, municípios só com a célula mais próxima: {sum(1 for n in ncel if n == 1)}")

# ------------------------------------------------------------------ 2. M1 em modo contínuo
chuva = pd.read_parquet(AN / "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
chuva = chuva[mun.cod.tolist()]
et0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"]
valida = np.isfinite(et0.values).mean(0) > 0.9
ELO, ELA = np.meshgrid(et0.lon.values, et0.lat.values)
iv = np.flatnonzero(valida.ravel())
E0 = et0.values.reshape(et0.sizes["time"], -1)
cx = np.array([g.centroid.x for g in mun.geometry]); cy = np.array([g.centroid.y for g in mun.geometry])
idx_e = [iv[np.argmin((ELO.ravel()[iv] - x) ** 2 + (ELA.ravel()[iv] - y) ** 2)] for x, y in zip(cx, cy)]
E = pd.DataFrame(E0[:, idx_e], index=pd.DatetimeIndex(et0.time.values), columns=mun.cod.tolist())
E = E.fillna(E.groupby(E.index.dayofyear).transform("mean"))
T = chuva.index.intersection(E.index)
T = T[T >= "2014-06-01"]
P = chuva.loc[T].fillna(0).values
EE = E.loc[T].values


def balde(P, E, taw=100.0, p=0.55, kc=1.0, cn=75.0):
    s = 25400.0 / cn - 254.0
    raw = p * taw
    Dr = np.full(P.shape[1], taw)
    out = np.empty_like(P, dtype=float)
    for j in range(P.shape[0]):
        pj = P[j]
        q = np.where(pj > 0.2 * s, (pj - 0.2 * s) ** 2 / (pj + 0.8 * s), 0.0)
        ks = np.where(Dr > raw, np.clip((taw - Dr) / ((1 - p) * taw), 0, 1), 1.0)
        Dr = np.clip(Dr - (pj - q) + ks * kc * E[j], 0, taw)
        out[j] = (taw - Dr) / taw
    return out


with Cronometro("balde M1 contínuo"):
    W = balde(P, EE)
balde_mun = pd.DataFrame(W, index=T, columns=mun.cod.tolist())
balde_ce = balde_mun.mean(1)
chuva_ce = chuva.mean(1)
print(f"balde: {T.min():%Y-%m-%d} -> {T.max():%Y-%m-%d}; chuva média anual CE 2016-2025 = "
      f"{chuva_ce['2016':'2025'].sum() / 10:.0f} mm; ET0 média anual = {E.loc['2016':'2025'].mean(1).sum() / 10:.0f} mm")

# ------------------------------------------------------------------ 3-5. GLDAS Noah, CLSM e POWER GWETROOT
noah = xr.open_dataset(DADOS / "gldas" / "gldas_noah025_mensal_ne.nc")["RootMoist_inst"].sel(lat=slice(-8.1, -2.4), lon=slice(-41.6, -36.9))
noah_ce = media_ce(noah)
with Cronometro("CLSM"):
    cl = xr.open_dataset(DADOS / "gldas" / "gldas_clsm025_diario_ne.nc")[["SoilMoist_RZ_tavg", "GWS_tavg"]]
    cl = cl.sel(lat=slice(-8.1, -2.4), lon=slice(-41.6, -36.9), time=slice("2014-01-01", None)).load()
    clsm_rz = media_ce(cl.SoilMoist_RZ_tavg)
    clsm_gws = media_ce(cl.GWS_tavg)
pw = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")["GWETROOT"].sel(time=slice("2014-01-01", None))
gwet = media_ce(pw)
print(f"Noah até {noah_ce.index.max():%Y-%m}; CLSM até {clsm_rz.index.max():%Y-%m-%d}; GWETROOT até {gwet.dropna().index.max():%Y-%m-%d}")

D = pd.DataFrame({"SMAP_L4": smap_rz, "M1_balde": balde_ce, "CLSM_RZ": clsm_rz, "POWER_GWETROOT": gwet})
D = D["2015-03-31":"2026-11-10"]
D["Noah_RZ"] = np.nan  # mensal, tratado à parte


def anomalia_diaria(s, base=("2015-04-01", "2025-12-31")):
    b = s[base[0]:base[1]]
    clim = b.groupby(b.index.dayofyear).mean().reindex(range(1, 367)).interpolate(limit_direction="both")
    sd = b.groupby(b.index.dayofyear).std().reindex(range(1, 367)).interpolate(limit_direction="both")
    k = 31
    ext = lambda c: pd.concat([c.iloc[-k:], c, c.iloc[:k]]).rolling(k, center=True).mean().iloc[k:-k]
    clim, sd = ext(clim), ext(sd)
    clim.index = sd.index = range(1, 367)
    a = s - clim.reindex(s.index.dayofyear).values
    z = a / sd.reindex(s.index.dayofyear).values
    return a, z, clim


print("\n" + "=" * 25, "(1) Concordância com o SMAP L4 (média do Ceará)", "=" * 25)
A, Z, CL = {}, {}, {}
for c in ["SMAP_L4", "M1_balde", "CLSM_RZ", "POWER_GWETROOT"]:
    A[c], Z[c], CL[c] = anomalia_diaria(D[c].dropna())
A = pd.DataFrame(A); Z = pd.DataFrame(Z)
lin = []
for c in ["M1_balde", "CLSM_RZ", "POWER_GWETROOT"]:
    j = D[["SMAP_L4", c]].dropna()
    ja = A[["SMAP_L4", c]].dropna()
    mj = j.resample("MS").mean().dropna()
    ma = ja.resample("MS").mean().dropna()
    # defasagem: r(anom SMAP(t), anom X(t+k)); k > 0 => X atrasa em relação ao SMAP
    lags = range(-60, 61)
    cc = [ja.SMAP_L4.corr(ja[c].shift(-k)) for k in lags]
    kbest = list(lags)[int(np.nanargmax(cc))]
    lin.append({"fonte": c, "dias": len(j), "r bruto diário": round(j.corr().iloc[0, 1], 3),
                "r bruto mensal": round(mj.corr().iloc[0, 1], 3), "r anomalia diária": round(ja.corr().iloc[0, 1], 3),
                "r anomalia mensal": round(ma.corr().iloc[0, 1], 3), "defasagem (dias, + = atrasa o SMAP)": kbest,
                "r na defasagem": round(np.nanmax(cc), 3)})
# Noah mensal
nm = noah_ce["2015-04":"2026-07"]
sm_m = D.SMAP_L4.resample("MS").mean()["2015-04":"2026-07"]
jn = pd.concat([sm_m, nm], axis=1, keys=["s", "n"]).dropna()
an = jn - jn.groupby(jn.index.month).transform("mean")
ccn = {k: an.s.corr(an.n.shift(-k)) for k in (-2, -1, 0, 1, 2)}
lin.append({"fonte": "Noah_RZ (mensal)", "dias": f"{len(jn)} meses", "r bruto diário": np.nan,
            "r bruto mensal": round(jn.corr().iloc[0, 1], 3), "r anomalia diária": np.nan,
            "r anomalia mensal": round(an.corr().iloc[0, 1], 3), "defasagem (dias, + = atrasa o SMAP)": f"{max(ccn, key=ccn.get)} mês",
            "r na defasagem": round(max(ccn.values()), 3)})
print(pd.DataFrame(lin).to_string(index=False))
print("matriz de r das anomalias mensais (todas as fontes):")
AM = A.resample("MS").mean()
AM["Noah_RZ"] = (noah_ce - noah_ce["2015-04":"2025-12"].groupby(noah_ce["2015-04":"2025-12"].index.month).mean().reindex(noah_ce.index.month).values)
print(AM["2015-04":"2026-07"].corr().round(2).to_string())

print("\n" + "=" * 25, "(2) Viés e amplitude (volumétricos; 2015-04 a 2026-07)", "=" * 25)
vol = pd.DataFrame({"SMAP_L4 (m3/m3)": D.SMAP_L4, "CLSM_RZ (mm/1000)": D.CLSM_RZ / 1000.0})
volm = vol.resample("MS").mean()
volm["Noah_RZ (mm/1000, supõe 1 m)"] = noah_ce / 1000.0
volm = volm["2015-04":"2026-07"].dropna()
desc = volm.describe(percentiles=[0.05, 0.5, 0.95]).T[["mean", "5%", "50%", "95%"]]
desc["amplitude p95-p5"] = desc["95%"] - desc["5%"]
print(desc.round(3).to_string())
for c in volm.columns[1:]:
    print(f"  viés {c} − SMAP = {(volm[c] - volm.iloc[:, 0]).mean():+.3f} m3/m3; razão de amplitude = "
          f"{desc.loc[c, 'amplitude p95-p5'] / desc.iloc[0]['amplitude p95-p5']:.2f}")
print("  M1 e GWETROOT são relativos (0-1): sem viés volumétrico. Amplitude p95-p5 em unidades próprias:",
      {c: round(float(D[c].quantile(.95) - D[c].quantile(.05)), 2) for c in ["M1_balde", "POWER_GWETROOT"]})

print("\n" + "=" * 25, "(3) Ciclo sazonal: dia do pico e do vale (climatologia 2015-2025)", "=" * 25)
for c in CL:
    cl_ = CL[c]
    print(f"  {c:15s} pico no dia {int(cl_.idxmax()):3d} ({(pd.Timestamp('2021-01-01') + pd.Timedelta(days=int(cl_.idxmax()) - 1)):%d/%m}) | "
          f"vale no dia {int(cl_.idxmin()):3d} ({(pd.Timestamp('2021-01-01') + pd.Timedelta(days=int(cl_.idxmin()) - 1)):%d/%m})")
nc = noah_ce["2015-04":"2025-12"].groupby(noah_ce["2015-04":"2025-12"].index.month).mean()
print(f"  Noah_RZ mensal: mês do pico {nc.idxmax()}, mês do vale {nc.idxmin()}")
pc_ = chuva_ce["2016":"2025"].groupby(chuva_ce["2016":"2025"].index.month).sum() / 10
print(f"  chuva IMERG CE: mês mais chuvoso {pc_.idxmax()} ({pc_.max():.0f} mm)")

print("\n" + "=" * 25, "(4) Memória: lag em que a autocorrelação da anomalia cai abaixo de 1/e", "=" * 25)
gws_a, _, _ = anomalia_diaria(clsm_gws["2015-04-01":])
mem = {}
for nome, s in list(A.items()) + [("CLSM_GWS (água subterrânea)", gws_a)]:
    s = s.dropna()
    ac = [s.autocorr(k) for k in range(0, 400, 2)]
    k = next((2 * i for i, v in enumerate(ac) if v < np.exp(-1)), None)
    mem[nome] = k
    print(f"  {nome:28s} e-folding ≈ {k} dias | acf 30 d = {s.autocorr(30):.2f}, 90 d = {s.autocorr(90):.2f}, 180 d = {s.autocorr(180):.2f}")

print("\n" + "=" * 25, "(5) Portões: concordância ENTRE ANOS (z da anomalia no dia do portão; Spearman)", "=" * 25)
# alvo de referência: fração de municípios em quebra canônica do milho no ano (PAM, 1998-2025)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha
p["ref"] = p.groupby("cod_local").r.transform(lambda v: pd.Series([np.median(np.delete(v.values, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=v.index))
p["quebra"] = (p.r / p.ref < 0.5).astype(float)
fq = p.dropna(subset=["ref"]).groupby("ano").quebra.mean()
anos_ch = list(range(1998, 2026))
for nome, (m, d) in {"19/mar": (3, 19), "30/abr": (4, 30)}.items():
    rows = {}
    for a in range(2015, 2027):
        t = pd.Timestamp(a, m, d)
        if t < pd.Timestamp("2015-03-31"):
            continue
        r = {c: Z[c].get(t, np.nan) for c in Z.columns}
        r["SMAP_pctl_produto"] = smap_pc.get(t, np.nan)
        mm = m - 1  # Noah: último mês completo antes do portão
        r["Noah_RZ (mês anterior)"] = AM["Noah_RZ"].get(pd.Timestamp(a, mm, 1), np.nan)
        ac = chuva_ce[f"{a}-01-01":t].sum() if t <= chuva_ce.index.max() else np.nan
        norm = np.median([chuva_ce[f"{b}-01-01":pd.Timestamp(b, m, d)].sum() for b in anos_ch if b != a])
        r["IMERG % do normal"] = ac / norm
        r["fração mun. em quebra (milho)"] = fq.get(a, np.nan)
        rows[a] = r
    G = pd.DataFrame(rows).T
    print(f"--- portão {nome} (n anos = {len(G)})")
    print(G.round(2).to_string())
    rho = G.corr(method="spearman")
    print("Spearman entre anos (colunas-chave):")
    print(rho.loc[["SMAP_L4", "SMAP_pctl_produto", "M1_balde", "IMERG % do normal", "fração mun. em quebra (milho)"]].round(2).to_string())
