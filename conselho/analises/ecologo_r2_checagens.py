"""Ecologo (rodada 2): checagens rapidas de afirmacoes de outros especialistas e relacoes nao exploradas.

(A) GRACE: o hidrologo diz 'banco em +3,8 cm, percentil 72 (jul/2026)'; o estrategista diz 'set/2026 = -9,7 cm,
    7o menor de 21 setembros'. Sao compativeis?
(B) ONI de 2026: 2,14 (estrategista, jul-set), 2,31 (economista, ago-set), 2,46 (clima, 'ASO'/set). Qual e qual?
(C) Fogo de out-dez: o El Nino do proprio ano (ONI de set) acrescenta algo ao efeito da chuva de t-1?
(D) Combustivel visto do espaco: a anomalia de NDVI (MODIS) de fev-jun de t e t-1 preve o fogo de out-dez melhor
    que a chuva? (celulas 0,25 grau do painel sr_fundacao)
(E) Pragas x regra de semeadura do agronomo: a regra 'so depois de 1/fev' (R6) sincroniza o plantio na paisagem?
    Espalhamento das datas de semeadura entre municipios vizinhos (<= 50 km) contra 1 geracao da lagarta (~26 d).
(F) Fogo pre-plantio (out-dez do ano y) x rendimento do milho no ano y+1, dentro do ano (exploratorio).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from scipy.spatial import cKDTree
from shapely.geometry import Point
import statsmodels.api as sm

AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")

# ---------------- (A) GRACE ----------------
g = pd.read_parquet(DERIV / "grace_ce_mensal.parquet").set_index("data").valor.sort_index()
g.index = pd.to_datetime(g.index)
clim = g.groupby(g.index.month).transform("mean")
gd = g - clim
print("(A) GRACE CE (TWS_anomalia, cm)")
for d in ["2026-06-01", "2026-07-01", "2026-08-01", "2026-09-01"]:
    if pd.Timestamp(d) in g.index:
        x = g.loc[d]
        xd = gd.loc[d]
        print(f"  {d[:7]}: bruto {x:+.1f} cm | dessazonalizado {xd:+.1f} cm, percentil {stats.percentileofscore(gd.values, xd):.0f} "
              f"da serie dessazonalizada | rank entre os mesmos meses: {(g[g.index.month == pd.Timestamp(d).month] < x).sum() + 1}o "
              f"de {(g.index.month == pd.Timestamp(d).month).sum()} | mediana desse mes {g[g.index.month == pd.Timestamp(d).month].median():+.1f}")
# tendencia de longo prazo afeta o percentil? (Sen)
t_ = (g.index.year + (g.index.month - 0.5) / 12).values
sl = stats.theilslopes(gd.values, t_)[0]
print(f"  Sen da serie dessazonalizada: {sl:+.2f} cm/ano")
print(f"  Ultimos 12 meses dessazonalizados: " + ", ".join(f"{i.strftime('%Y-%m')} {v:+.1f}" for i, v in gd.iloc[-12:].items()))

# ---------------- (B) ONI ----------------
ix = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
oni = ix[ix.variavel == "ONI"].set_index("data").valor.sort_index()
oni.index = pd.to_datetime(oni.index)
print("\n(B) ONI (valor por mes no arquivo):", ", ".join(f"{i.strftime('%Y-%m')} {v:+.2f}" for i, v in oni.loc["2026-05":].items()))
for y in (1997, 2015, 2023, 2026):
    s = oni.loc[f"{y}-07":f"{y}-09"]
    print(f"  {y}: jul {s.iloc[0]:+.2f} ago {s.iloc[1]:+.2f} set {s.iloc[2]:+.2f} | media jul-set {s.mean():+.2f} | media ago-set {s.iloc[1:].mean():+.2f}")
print("  Fonte:", ix[ix.variavel == "ONI"].fonte.iloc[0])

# ---------------- (C) fogo out-dez: chuva t-1 + ONI de set do ano t ----------------
v = pd.read_parquet(DADOS / "viirs" / "firms_viirs_snpp_nordeste.parquet",
                    columns=["latitude", "longitude", "acq_date", "type", "uf", "confidence"])
v = v[(v.uf == 23) & (v["type"] == 0) & (v.confidence.astype(str).str.lower().isin(["n", "h", "nominal", "high"]))].copy()
v["acq_date"] = pd.to_datetime(v.acq_date)
v["ano"] = v.acq_date.dt.year
v["mes"] = v.acq_date.dt.month
v = v[v.ano.between(2012, 2025)]
vod = v[v.mes.isin([10, 11, 12])].copy()

ds = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")["IMERG_PRECTOT"].load()
uf = gpd.read_file(REF / "ceara_uf.geojson").to_crs(4326).union_all()
lats, lons = ds.lat.values, ds.lon.values
cells = [(la, lo) for la in lats for lo in lons if uf.contains(Point(lo, la))]
quadra = ds.where(ds.time.dt.month.isin([2, 3, 4, 5, 6]), drop=True).groupby("time.year").sum()
vod["la_c"] = lats[np.abs(vod.latitude.values[:, None] - lats[None, :]).argmin(1)]
vod["lo_c"] = lons[np.abs(vod.longitude.values[:, None] - lons[None, :]).argmin(1)]
fd = vod.groupby(["la_c", "lo_c", "ano"]).size()
oni_set = {y: oni.get(pd.Timestamp(f"{y}-09-01"), np.nan) for y in range(2010, 2027)}
lin = []
for la, lo in cells:
    q = quadra.sel(lat=la, lon=lo).to_series()
    z = (q - q.loc[1991:2020].mean()) / q.loc[1991:2020].std()
    for y in range(2012, 2026):
        lin.append({"cel": f"{la}_{lo}", "ano": y, "pz": z.get(y), "pz1": z.get(y - 1), "oni": oni_set[y],
                    "focos": fd.get((la, lo, y), 0)})
P = pd.DataFrame(lin)
P["lf"] = np.log1p(P.focos)
P["t"] = P.ano - 2018.5
for c in ("lf", "pz", "pz1", "oni", "t"):
    P[c + "_d"] = P[c] - P.groupby("cel")[c].transform("mean")
print("\n(C) Painel 38 celulas x 14 anos (IMERG via POWER), log(1+focos out-dez), EF de celula, EP agrupado por ano")
for X in (["pz_d", "pz1_d"], ["pz_d", "pz1_d", "oni_d"], ["pz_d", "pz1_d", "oni_d", "t_d"]):
    m = sm.OLS(P.lf_d, P[X]).fit(cov_type="cluster", cov_kwds={"groups": P.ano})
    print("  " + " | ".join(f"{c} {m.params[c]:+.3f} (p={m.pvalues[c]:.3f})" for c in X) + f" | R2 dentro {m.rsquared:.3f}")
est = P.groupby("ano").agg(focos=("focos", "sum"), pz1=("pz1", "mean"), oni=("oni", "first"))
print("  Estado: rho(focos, ONI set) = %+.2f (p=%.3f); anos e ONI:" % stats.spearmanr(est.focos, est.oni),
      {int(k): (int(r.focos), round(r.oni, 2)) for k, r in est.iterrows()})

# ---------------- (D) combustivel por NDVI (celulas 0,25) ----------------
sp = pd.read_parquet(AN / "sr_fundacao_painel_celula_mes.parquet")
q5 = sp[sp.mes.between(2, 6)].groupby(["cel", "ano"]).agg(nd=("a_ndvi", "mean"), sm=("a_sm0_10", "mean"),
                                                        lat=("lat", "first"), lon=("lon", "first")).reset_index()
cc = q5.groupby("cel")[["lat", "lon"]].first()
tree = cKDTree(cc[["lat", "lon"]].values)
dist, idx = tree.query(vod[["latitude", "longitude"]].values)
vod["cel25"] = np.where(dist <= 0.18, cc.index.values[idx], -1)
f25 = vod[vod.cel25 >= 0].groupby(["cel25", "ano"]).size()
q5 = q5.set_index(["cel", "ano"])
lin = []
for c in cc.index:
    for y in range(2012, 2026):
        if (c, y) in q5.index and (c, y - 1) in q5.index:
            lin.append({"cel": c, "ano": y, "nd": q5.loc[(c, y), "nd"], "nd1": q5.loc[(c, y - 1), "nd"],
                        "sm": q5.loc[(c, y), "sm"], "sm1": q5.loc[(c, y - 1), "sm"], "focos": f25.get((c, y), 0)})
Q = pd.DataFrame(lin).dropna()
Q["lf"] = np.log1p(Q.focos)
Q["t"] = Q.ano - 2018.5
for c in ("nd", "nd1", "sm", "sm1"):
    Q[c] = (Q[c] - Q[c].mean()) / Q[c].std()
for c in ("lf", "nd", "nd1", "sm", "sm1", "t"):
    Q[c + "_d"] = Q[c] - Q.groupby("cel")[c].transform("mean")
print(f"\n(D) Painel {Q.cel.nunique()} celulas 0,25 x {Q.ano.nunique()} anos; regressores em dp; EF de celula; EP agrupado por ano")
for X in (["sm_d", "sm1_d"], ["nd_d", "nd1_d"], ["nd_d", "nd1_d", "sm_d", "sm1_d"], ["nd_d", "nd1_d", "sm_d", "sm1_d", "t_d"], ["t_d"], ["sm_d", "sm1_d", "t_d"]):
    m = sm.OLS(Q.lf_d, Q[X]).fit(cov_type="cluster", cov_kwds={"groups": Q.ano})
    print("  " + " | ".join(f"{c} {m.params[c]:+.3f} (p={m.pvalues[c]:.3f})" for c in X) + f" | R2 dentro {m.rsquared:.3f}")
# LOYO skill: NDVI t-1 vs umidade t-1
for X in (["sm1"], ["nd1"], ["nd1", "sm1"]):
    sse = ssc = 0.0
    for y in sorted(Q.ano.unique()):
        a, b = Q[Q.ano != y], Q[Q.ano == y]
        mc = a.groupby("cel").lf.mean()
        mx = a.groupby("cel")[X].mean()
        beta = np.linalg.lstsq((a[X] - mx.loc[a.cel].values).values, (a.lf - mc.loc[a.cel].values).values, rcond=None)[0]
        ok = b.cel.isin(mc.index)
        b = b[ok]
        hat = mc.loc[b.cel].values + (b[X] - mx.loc[b.cel].values).values @ beta
        sse += ((b.lf - hat) ** 2).sum()
        ssc += ((b.lf - mc.loc[b.cel].values) ** 2).sum()
    print(f"  LOYO skill (MSE vs climatologia da celula) com {X}: {1 - sse / ssc:+.3f}")

# ---------------- (E) sincronia do plantio: R1 x R6 ----------------
ch = pd.read_parquet(AN / "saidas" / "chuva_mun_diaria.parquet")
mun = gpd.read_file(REF / "ceara_municipios.geojson").to_crs(5880)
cod_col = [c for c in mun.columns if c.lower() in ("codarea", "cd_mun", "codigo", "cod", "id", "cd_geocmu", "geocodigo")]
mun["cod"] = mun[cod_col[0]].astype(str).str[:7]
cent = mun.set_index("cod").geometry.centroid
cent = cent.loc[[c for c in ch.columns if c in cent.index]]
xy = np.c_[cent.x.values, cent.y.values]
viz = cKDTree(xy).query_ball_point(xy, r=50_000)
cods = list(cent.index)


def semeadura(serie_ano, inicio_doy):
    s3 = serie_ano.rolling(3).sum()
    ok = (s3 >= 20) & (serie_ano.index.dayofyear >= inicio_doy + 2)
    return serie_ano.index[ok.values][0].dayofyear if ok.any() else np.nan


GER = 390.8 / 15.0  # dias por geracao da lagarta a ~15 graus-dia/dia (CE, fev-mai)
res = []
for y in range(1998, 2026):
    sa = ch.loc[f"{y}-01-01":f"{y}-06-30", cods]
    for regra, ini in (("R1", 1), ("R6", 32)):
        d = np.array([semeadura(sa[c], ini) for c in cods])
        spread = np.array([np.nanmax(d[nb]) - np.nanmin(d[nb]) if np.isfinite(d[nb]).sum() > 1 else np.nan for nb in viz])
        precoce = np.array([d[i] <= np.nanmedian(d[nb]) - GER if np.isfinite(d[i]) else False for i, nb in enumerate(viz)])
        res.append({"ano": y, "regra": regra, "iqr_estado": np.nanpercentile(d, 75) - np.nanpercentile(d, 25),
                    "spread50_med": np.nanmedian(spread), "frac_spread_gt_ger": np.nanmean(spread > GER),
                    "frac_precoce_1ger": precoce.mean(), "frac_jan": np.nanmean(d <= 31)})
R = pd.DataFrame(res)
print(f"\n(E) Sincronia do plantio (IMERG municipal 1998-2025; 1 geracao da lagarta ~{GER:.0f} d)")
print(R.groupby("regra")[["iqr_estado", "spread50_med", "frac_spread_gt_ger", "frac_precoce_1ger", "frac_jan"]].median().round(3).to_string())
print("  Media entre anos:")
print(R.groupby("regra")[["iqr_estado", "spread50_med", "frac_spread_gt_ger", "frac_precoce_1ger", "frac_jan"]].mean().round(3).to_string())
w = R.pivot(index="ano", columns="regra", values="spread50_med")
print(f"  Anos em que R6 reduz o espalhamento mediano na vizinhanca de 50 km: {(w.R6 < w.R1).sum()} de {len(w)}; "
      f"Wilcoxon p = {stats.wilcoxon(w.R1, w.R6).pvalue:.4f}")

# ---------------- (F) fogo out-dez (y) x milho (y+1) ----------------
am = pd.read_parquet(AN / "saidas" / "anom_milho_j14.parquet")
am["cod"] = am.cod.astype(str)
mun4 = mun.to_crs(4326)[["cod", "geometry"]]
pts = gpd.GeoDataFrame(vod[["ano"]].copy(), geometry=gpd.points_from_xy(vod.longitude, vod.latitude), crs=4326)
jn = gpd.sjoin(pts, mun4, predicate="within")
fm = jn.groupby(["cod", "ano"]).size().rename("focos").reset_index()
area = mun.set_index("cod").geometry.area / 1e6
full = pd.MultiIndex.from_product([mun.cod.unique(), range(2012, 2025)], names=["cod", "ano"])
fm = fm.set_index(["cod", "ano"]).reindex(full, fill_value=0).reset_index()
fm["dens"] = np.log1p(fm.focos / area.loc[fm.cod].values * 100)  # focos por 100 km2
fm["dens_a"] = fm.dens - fm.groupby("cod").dens.transform("mean")
fm["ano_safra"] = fm.ano + 1
M = am.merge(fm[["cod", "ano_safra", "dens_a", "dens"]], left_on=["cod", "ano"], right_on=["cod", "ano_safra"])
rs = []
for y, b in M.groupby("ano"):
    if len(b) > 30:
        r1 = stats.spearmanr(b.dens_a, b.anom)[0]
        # parcial: residualiza posto da anomalia e do fogo na chuva fev-mai do ano da safra
        rk = b[["dens_a", "anom", "P_fmam_z"]].rank()
        ra = sm.OLS(rk.dens_a, sm.add_constant(rk.P_fmam_z)).fit().resid
        rb = sm.OLS(rk.anom, sm.add_constant(rk.P_fmam_z)).fit().resid
        rs.append({"ano": y, "rho": r1, "rho_parc": np.corrcoef(ra, rb)[0, 1], "n": len(b)})
RS = pd.DataFrame(rs)
print(f"\n(F) Fogo out-dez (y, anomalia do proprio municipio) x anomalia do milho (y+1), dentro do ano, {len(RS)} safras")
print(f"  rho mediano {RS.rho.median():+.3f} (positivo em {(RS.rho > 0).sum()} de {len(RS)}); "
      f"parcial (controle chuva fev-mai) mediano {RS.rho_parc.median():+.3f} (positivo em {(RS.rho_parc > 0).sum()}); "
      f"sinal: Wilcoxon p = {stats.wilcoxon(RS.rho_parc).pvalue:.3f}")
# entre municipios: densidade media de fogo x nivel de rendimento / tendencia
lvl = M.groupby("cod").agg(dens=("dens", "mean"), anom_sd=("anom", "std"))
print("  Entre municipios: rho(densidade media de fogo, desvio-padrao da anomalia do milho) = %+.2f (p=%.3f)"
      % stats.spearmanr(lvl.dens, lvl.anom_sd))
