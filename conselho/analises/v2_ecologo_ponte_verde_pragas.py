"""Ecologo (rodada 2, dados novos) - Analise 3: leitura de pragas com graus-dia + VIIRS (ponte verde) + SMAP.

Pergunta 1 (VIIRS sem o buraco do Terra): quanto da lavoura/mosaico fica verde em outubro (ponte verde para a
  lagarta-do-cartucho entre uma quadra e a seguinte), ano a ano 2012-2026? Em out/2026, antes da quadra de 2027, a
  ponte esta acima do normal?
Pergunta 2: a ponte depende da agua (chuva IMERG da quadra, SMAP L4 de set-out) ou e fixa (irrigacao, baixios)?
Pergunta 3 (teste falsificavel, exploratorio): mais ponte verde em out do ano y-1 -> pior milho em y no mesmo
  municipio, descontada a chuva fev-mai de y? (anomalia do milho em saidas/anom_milho_j14.parquet; EF de municipio,
  EP agrupado por ano). Se a ponte alimentasse a praga a ponto de pesar no PAM, o sinal seria negativo.
Pergunta 4 (graus-dia): geracoes potenciais da lagarta em ago-dez/2026 (El Nino forte) contra 2012-2025, POWER diario.
Parametros iguais aos da rodada 1 (ecologo_grausdia_geracoes.py): Tb 12,57 C, K 390,8 graus-dia (du Plessis et al.
  2020), corte superior 32 C; ponte = NDVI de outubro >= 0,55 em pixel ESA CCI 2020 de lavoura/mosaico
  (classes 10, 11, 12, 20, 30, 40). Limiar herdado da rodada 1 (MODIS); VIIRS - MODIS = +0,014 no CE (secao 05).
Sem dado de praga observado: a ponte e o relogio termico sao camada de hipotese (grau C/D), e a pergunta 3 e o unico
  teste contra um desfecho medido (e indireto).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.api as sm
import xarray as xr
from scipy import stats

AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
mun = gpd.read_file(REF / "ceara_municipios.geojson").to_crs(4326)
mun["codarea"] = mun.codarea.astype(str)

vd = xr.open_dataset(DADOS / "viirs" / "vnp13a3_ndvi_evi_ceara_001deg.nc")
LA, LO = np.meshgrid(vd.lat.values, vd.lon.values, indexing="ij")
pts = gpd.sjoin(gpd.GeoDataFrame(geometry=gpd.points_from_xy(LO.ravel(), LA.ravel()), crs=4326),
                mun[["codarea", "geometry"]], predicate="within")
flat = pts.index.values
cod_px = pts.codarea.values
lc = xr.open_dataset(DADOS / "modis" / "esa_cci_lc_2020_nordeste_300m.nc")
la_l, lo_l = lc.lat.values, lc.lon.values
ii = np.clip(np.round((la_l[0] - LA.ravel()[flat]) / abs(la_l[1] - la_l[0])).astype(int), 0, len(la_l) - 1)
jj = np.clip(np.round((LO.ravel()[flat] - lo_l[0]) / abs(lo_l[1] - lo_l[0])).astype(int), 0, len(lo_l) - 1)
cls = lc.lccs_class.values[ii, jj]
agri = np.isin(cls, [10, 11, 12, 20, 30, 40])
print(f"Pixels 0,01 grau no CE: {len(flat):,}; lavoura/mosaico ESA CCI: {agri.sum():,} ({agri.mean() * 100:.1f}%)")

tv = pd.to_datetime(vd.time.values)
lin = []
for y in range(2012, 2027):
    k = np.where((tv.year == y) & (tv.month == 10))[0]
    if not len(k):
        continue
    nd = vd.ndvi.isel(time=int(k[0])).values.ravel()[flat]
    ok = np.isfinite(nd) & agri
    df = pd.DataFrame({"codarea": cod_px[ok], "ponte": nd[ok] >= 0.55, "nd": nd[ok]})
    g = df.groupby("codarea").agg(frac=("ponte", "mean"), nd=("nd", "median"), n=("ponte", "size"))
    g["ano"] = y
    lin.append(g.reset_index())
B = pd.concat(lin)
est = B.groupby("ano").apply(lambda d: pd.Series({"ponte_%": np.average(d.frac, weights=d.n) * 100,
                                                  "ndvi_out_lavoura": np.average(d.nd, weights=d.n)}), include_groups=False)
print("\n(1) Ponte verde em outubro (VIIRS), % da lavoura/mosaico do CE com NDVI >= 0,55:")
print(est.round(2).T.to_string())
base = est.loc[2012:2025, "ponte_%"]
print(f"  2012-2025: mediana {base.median():.1f}% (min {base.min():.1f} em {base.idxmin()}, max {base.max():.1f} em {base.idxmax()});"
      f" out/2026 = {est.loc[2026, 'ponte_%']:.1f}% -> posto {int((base < est.loc[2026, 'ponte_%']).sum()) + 1} de {len(base) + 1}")
Bm = B.pivot(index="codarea", columns="ano", values="frac")
acima = (Bm[2026] > Bm.loc[:, 2012:2025].median(axis=1)).mean()
print(f"  Municipios com ponte de out/2026 acima da propria mediana 2012-2025: {acima * 100:.0f}% (n = {Bm[2026].notna().sum()})")
# persistencia espacial: a ponte e sempre nos mesmos lugares?
rr = [stats.spearmanr(Bm[a], Bm[a + 1], nan_policy="omit")[0] for a in range(2012, 2026)]
print(f"  rho entre municipios de um ano para o seguinte: mediana {np.median(rr):+.2f} (min {min(rr):+.2f}) -> geografia fixa")

# (2) a ponte depende da agua?
P = pd.read_parquet(AN / "saidas" / "v2_ecologo_painel_mun_mes.parquet")
q = P[P.m.between(2, 5)].groupby(["codarea", "ano"]).P_mes.sum(min_count=4).rename("P_fmam")
s = P[P.m.isin([9, 10])].groupby(["codarea", "ano"]).sm_rootzone.mean().rename("rz_so")
D = B.merge(q.reset_index(), on=["codarea", "ano"], how="left").merge(s.reset_index(), on=["codarea", "ano"], how="left")
D = D[D.ano <= 2025]
ea = D.groupby("ano")[["frac", "P_fmam", "rz_so"]].mean()
print("\n(2) A ponte depende da agua? (estado, n = anos)")
print(f"  rho(ponte, chuva IMERG fev-mai) = {stats.spearmanr(ea.frac, ea.P_fmam)[0]:+.2f} (n={len(ea)});"
      f" rho(ponte, SMAP zona da raiz set-out) = {stats.spearmanr(ea.loc[2015:].frac, ea.loc[2015:].rz_so)[0]:+.2f} (n={len(ea.loc[2015:])})")
d = D.dropna(subset=["P_fmam", "rz_so"]).copy()
for c in ("frac", "P_fmam", "rz_so"):
    d[c + "_z"] = (d[c] - d.groupby("codarea")[c].transform("mean")) / d[c].std()
mm = sm.OLS(d.frac_z, d[["P_fmam_z", "rz_so_z"]]).fit(cov_type="cluster", cov_kwds={"groups": d.ano})
print("  Painel dentro do municipio (2015-2025, EP por ano): " + " | ".join(
    f"{c} {mm.params[c]:+.3f} (p={mm.pvalues[c]:.3f})" for c in ("P_fmam_z", "rz_so_z")) + f" | R2 {mm.rsquared:.3f}")
# variancia: quanto da variacao da ponte e entre municipios (fixa) x entre anos
tot = d.frac.var()
entre_m = d.groupby("codarea").frac.transform("mean").var()
print(f"  Fracao da variancia da ponte que e geografia fixa (media do municipio): {entre_m / tot * 100:.0f}%")

# (3) ponte de out(y-1) -> anomalia do milho em y
am = pd.read_parquet(AN / "saidas" / "anom_milho_j14.parquet")[["cod", "ano", "anom", "P_fmam_z"]]
am["cod"] = am.cod.astype(str)
b1 = B[["codarea", "ano", "frac"]].copy()
b1["ano"] += 1
X = am.merge(b1.rename(columns={"codarea": "cod", "frac": "ponte1"}), on=["cod", "ano"]).dropna()
X = X[X.ano.between(2013, 2025)]
pz1 = am[["cod", "ano", "P_fmam_z"]].copy()
pz1["ano"] += 1
X = X.merge(pz1.rename(columns={"P_fmam_z": "P_fmam_z1"}), on=["cod", "ano"], how="left").dropna()
for c in ("anom", "ponte1", "P_fmam_z", "P_fmam_z1"):
    X[c + "_d"] = X[c] - X.groupby("cod")[c].transform("mean")
X["ponte1_d"] = X.ponte1_d / X.ponte1_d.std()
print(f"\n(3) Ponte de out(y-1) -> anomalia do milho em y ({len(X)} municipio-anos, {X.cod.nunique()} municipios, "
      f"{X.ano.nunique()} safras 2013-2025; EF de municipio, EP por ano)")
for cols in (["ponte1_d"], ["ponte1_d", "P_fmam_z_d"], ["ponte1_d", "P_fmam_z_d", "P_fmam_z1_d"]):
    mm = sm.OLS(X.anom_d, X[cols]).fit(cov_type="cluster", cov_kwds={"groups": X.ano})
    ci = mm.conf_int().loc["ponte1_d"]
    print(f"  {' + '.join(cols):36s}: ponte1 {mm.params['ponte1_d']:+.3f} por dp (IC95 {ci[0]:+.3f} a {ci[1]:+.3f}, p={mm.pvalues['ponte1_d']:.3f})")
# dentro do ano (entre municipios), descontada a chuva
rs = []
for a, g in X.groupby("ano"):
    e = sm.OLS(g.anom, sm.add_constant(g[["P_fmam_z"]])).fit().resid
    pr = g.ponte1 - g.groupby("cod").ponte1.transform("mean") if False else g.ponte1_d
    rs.append(stats.spearmanr(pr, e)[0])
print(f"  Dentro do ano (ponte desviada da media do municipio x residuo da chuva): rho mediano {np.median(rs):+.3f}; "
      f"negativo em {(np.array(rs) < 0).sum()}/{len(rs)} safras")

# (4) graus-dia da lagarta ago-dez (POWER 0,5 grau, celulas no CE)
pw = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")[["T2M_MAX", "T2M_MIN"]]
uf = gpd.read_file(REF / "ceara_uf.geojson").to_crs(4326).union_all()
from shapely import contains_xy
LA2, LO2 = np.meshgrid(pw.lat.values, pw.lon.values, indexing="ij")
mk = xr.DataArray(contains_xy(uf, LO2, LA2), dims=("lat", "lon"), coords={"lat": pw.lat, "lon": pw.lon})
tx = pw.T2M_MAX.where(pw.T2M_MAX > -90)
tn = pw.T2M_MIN.where(pw.T2M_MIN > -90)
tm = np.minimum((tx + tn) / 2, 32.0)
gdd = (tm - 12.57).clip(min=0).where(mk).mean(("lat", "lon")).to_series()
ult = gdd.dropna().index.max()
print(f"\n(4) Graus-dia da lagarta (POWER ate {ult:%d/%m/%Y}); geracoes = soma / 390,8")
rows = {}
for y in range(2012, 2027):
    s = gdd.loc[f"{y}-08-01":f"{y}-11-12"]
    rows[y] = s.sum() / 390.8
r = pd.Series(rows)
print("  Geracoes potenciais 1/ago-12/nov (mesma janela em todos os anos): " + ", ".join(f"{k}: {v:.2f}" for k, v in r.items()))
print(f"  2026 = {r[2026]:.2f} contra mediana 2012-2025 {r.loc[2012:2025].median():.2f} (max {r.loc[2012:2025].max():.2f} em {r.loc[2012:2025].idxmax()});"
      f" dias por geracao em 2026: {(gdd.loc['2026-08-01':'2026-11-12'].count()) / r[2026]:.0f}")
