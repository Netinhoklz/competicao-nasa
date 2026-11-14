"""Ecologo de pragas/fogo - Analise 3: o fogo do Ceara como relogio do pousio e como resposta ao combustivel.

Perguntas:
  (A) Recorrencia: com que frequencia o MESMO pedaco de paisagem (~375 m, pixel VIIRS) volta a queimar em 2012-2025?
      Intervalo de retorno curto = pousio curto = perda de carbono do solo (Primo et al. 2023: corte e queima sem
      pousio -> ~-50% de C do solo em 10 anos; recuperacao ~50 anos).
  (B) Combustivel: a chuva da quadra (fev-jun) do ano t e do ano t-1 preve os focos de out-dez do ano t, por celula?
      Previsao "emitida em julho" com validacao deixando 1 ano de fora, e aplicacao a 2026.
Dados: FIRMS VIIRS S-NPP 375 m (E:/campeonato-nasa/dados/viirs/firms_viirs_snpp_nordeste.parquet, type=0 = fogo de
vegetacao presumido, confianca n/h), ESA CCI LC 2020 300 m (dados/modis/esa_cci_lc_2020_nordeste_300m.nc),
NASA POWER diario 0,5 grau (dados/power/power_ce_diario.nc).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from shapely.geometry import Point
import statsmodels.api as sm

v = pd.read_parquet(DADOS / "viirs" / "firms_viirs_snpp_nordeste.parquet",
                    columns=["latitude", "longitude", "acq_date", "type", "uf", "confidence", "frp"])
v = v[(v.uf == 23) & (v["type"] == 0) & (v.confidence.astype(str).str.lower().isin(["n", "h", "nominal", "high"]))].copy()
v["acq_date"] = pd.to_datetime(v.acq_date)
v["ano"] = v.acq_date.dt.year
v["mes"] = v.acq_date.dt.month
v = v[v.ano.between(2012, 2025)]
print(f"Focos VIIRS no CE (type 0, confianca n/h, 2012-2025): {len(v):,}")

# ---------------- (A) recorrencia por pixel ~375 m ----------------
RES = 0.0034  # ~375 m
v["ci"] = np.floor(v.latitude / RES).astype(int)
v["cj"] = np.floor(v.longitude / RES).astype(int)
cel = v.groupby(["ci", "cj"]).ano.agg(lambda s: tuple(sorted(set(s)))).rename("anos").reset_index()
cel["n_anos"] = cel.anos.str.len()
N = len(cel)
print(f"\n(A) Pixels de ~375 m que queimaram ao menos 1 vez: {N:,} (~{N * 0.375 ** 2 / 1e3:.1f} mil km2 = "
      f"{N * 0.375 ** 2 / 148_894 * 100:.1f}% do CE)")
dist = cel.n_anos.value_counts().sort_index()
print("  Distribuicao do numero de anos com fogo (de 14):", dist.to_dict())
for k in (2, 3, 5):
    print(f"  >= {k} anos com fogo: {(cel.n_anos >= k).mean() * 100:.1f}% dos pixels")


def gaps(t):
    return np.diff(t) if len(t) > 1 else np.array([])


g_all = np.concatenate([gaps(np.array(t)) for t in cel.anos])
print(f"  Intervalo entre queimas sucessivas no mesmo pixel: mediana {np.median(g_all):.0f} ano(s); "
      f"{(g_all <= 2).mean() * 100:.0f}% <= 2 anos; {(g_all <= 4).mean() * 100:.0f}% <= 4 anos (n = {len(g_all):,})")
# focos em pixel que ja tinha queimado nos 3 anos anteriores
pa = v.groupby(["ci", "cj", "ano"]).size().rename("nf").reset_index()
ss = set(zip(pa.ci, pa.cj, pa.ano))
pa["requeima3"] = [any((i, j, y - d) in ss for d in (1, 2, 3)) for i, j, y in zip(pa.ci, pa.cj, pa.ano)]
pa_ = pa[pa.ano >= 2015]
print(f"  2015-2025: {pa_.requeima3.mean() * 100:.1f}% dos pixel-ano queimados ja tinham queimado nos 3 anos anteriores "
      f"({(pa_.nf * pa_.requeima3).sum() / pa_.nf.sum() * 100:.1f}% dos focos)")
# por cobertura do solo (ESA CCI 2020)
lc = xr.open_dataset(DADOS / "modis" / "esa_cci_lc_2020_nordeste_300m.nc")
lcv = lc.lccs_class.values
la0, lo0 = float(lc.lat[0]), float(lc.lon[0])
rlc = abs(float(lc.lat[1] - lc.lat[0]))
GR = {"Lavoura": [10, 11, 12, 20, 30], "Mosaico": [40], "Caatinga arborea": [60, 61, 62],
      "Caatinga arbustiva": [100, 110, 120, 121, 122], "Campo/herbacea": [130, 140, 150, 151, 152, 153]}
mapa_gr = {c: g for g, cs in GR.items() for c in cs}
lat_c = (cel.ci + 0.5) * RES
lon_c = (cel.cj + 0.5) * RES
ii = np.clip(np.round((la0 - lat_c) / rlc).astype(int), 0, lcv.shape[0] - 1)
jj = np.clip(np.round((lon_c - lo0) / rlc).astype(int), 0, lcv.shape[1] - 1)
cel["grupo"] = pd.Series(lcv[ii, jj]).map(mapa_gr).fillna("outros").values
cel["med_gap"] = [np.median(gaps(np.array(t))) if len(t) > 1 else np.nan for t in cel.anos]
tab = cel.groupby("grupo").agg(pixels=("n_anos", "size"), anos_medio=("n_anos", "mean"),
                               frac_3mais=("n_anos", lambda s: (s >= 3).mean() * 100),
                               gap_mediano=("med_gap", "median")).sort_values("pixels", ascending=False)
print("  Recorrencia por classe de cobertura (ESA CCI 2020):")
print(tab.round(2).to_string())

# ---------------- (B) combustivel: chuva fev-jun -> focos out-dez ----------------
for FONTE in ("PRECTOTCORR", "IMERG_PRECTOT"):
    ds = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")[FONTE].load()
    uf = gpd.read_file(DADOS / "referencia" / "ceara_uf.geojson").to_crs(4326).union_all()
    lats, lons = ds.lat.values, ds.lon.values
    dlat, dlon = 0.5, float(lons[1] - lons[0])
    cells = [(la, lo) for la in lats for lo in lons if uf.contains(Point(lo, la))]
    print(f"\n(B) [{FONTE}] Celulas POWER com centro no CE: {len(cells)}")
    quadra = ds.where(ds.time.dt.month.isin([2, 3, 4, 5, 6]), drop=True).groupby("time.year").sum()
    v["la_c"] = lats[np.abs(v.latitude.values[:, None] - lats[None, :]).argmin(1)]
    v["lo_c"] = lons[np.abs(v.longitude.values[:, None] - lons[None, :]).argmin(1)]
    fd = v[v.mes.isin([10, 11, 12])].groupby(["la_c", "lo_c", "ano"]).size()
    linhas = []
    for la, lo in cells:
        q = quadra.sel(lat=la, lon=lo).to_series()
        z = (q - q.loc[1991:2020].mean()) / q.loc[1991:2020].std()
        for y in range(2012, 2027):
            linhas.append({"la": la, "lo": lo, "ano": y, "pz": z.get(y), "pz1": z.get(y - 1), "pz2": z.get(y - 2),
                           "focos": fd.get((la, lo, y), 0) if y <= 2025 else np.nan})
    P = pd.DataFrame(linhas)
    P["cel"] = P.la.astype(str) + "_" + P.lo.astype(str)
    P["lf"] = np.log1p(P.focos)
    tr = P[P.ano <= 2025].copy()
    tr["lf_d"] = tr.lf - tr.groupby("cel").lf.transform("mean")
    for c in ("pz", "pz1", "pz2"):
        tr[c + "_d"] = tr[c] - tr.groupby("cel")[c].transform("mean")
    
    Xc = ["pz_d", "pz1_d", "pz2_d"]
    mod = sm.OLS(tr.lf_d, tr[Xc]).fit(cov_type="cluster", cov_kwds={"groups": tr.ano})
    print("  Painel com efeito fixo de celula, log(1+focos out-dez) ~ z chuva fev-jun (t, t-1, t-2); EP agrupado por ano:")
    for c in Xc:
        print(f"    {c:6s}: {mod.params[c]:+.3f} (EP {mod.bse[c]:.3f}, p = {mod.pvalues[c]:.3f}) -> x{np.exp(mod.params[c]):.2f} focos por +1 dp")
    print(f"    R2 dentro = {mod.rsquared:.3f}, n = {len(tr)}")
    tr["t_d"] = tr.ano - 2018.5
    mod2 = sm.OLS(tr.lf_d, tr[Xc + ["t_d"]]).fit(cov_type="cluster", cov_kwds={"groups": tr.ano})
    print("    Robustez com tendencia linear: " + "; ".join(f"{c} {mod2.params[c]:+.3f} (p={mod2.pvalues[c]:.3f})" for c in Xc + ["t_d"]))

    # serie estadual (14 anos)
    est = tr.groupby("ano").agg(focos=("focos", "sum"), pz=("pz", "mean"), pz1=("pz1", "mean"))
    print("  Estado: Spearman focos out-dez x chuva fev-jun do mesmo ano: rho = %+.2f (p = %.3f); x ano anterior: rho = %+.2f (p = %.3f)"
          % (*stats.spearmanr(est.focos, est.pz), *stats.spearmanr(est.focos, est.pz1)))
    print("  Focos out-dez por ano:", est.focos.astype(int).to_dict())

    # previsao deixando 1 ano de fora (modelo: efeito fixo de celula + pz + pz1)
    prev = []
    for y in range(2012, 2026):
        a = tr[tr.ano != y]
        mcel = a.groupby("cel").lf.mean()
        mpz = a.groupby("cel")[["pz", "pz1"]].mean()
        Xa = (a[["pz", "pz1"]] - mpz.loc[a.cel].values)
        beta = np.linalg.lstsq(Xa.values, (a.lf - mcel.loc[a.cel].values).values, rcond=None)[0]
        b_ = tr[tr.ano == y]
        yhat = mcel.loc[b_.cel].values + ((b_[["pz", "pz1"]] - mpz.loc[b_.cel].values).values @ beta)
        prev.append(pd.DataFrame({"ano": y, "cel": b_.cel.values, "obs": b_.lf.values, "hat": yhat, "clim": mcel.loc[b_.cel].values}))
    pv = pd.concat(prev)
    sse = ((pv.obs - pv.hat) ** 2).sum()
    ssc = ((pv.obs - pv.clim) ** 2).sum()
    print(f"  LOYO por celula-ano: skill vs climatologia da celula = {1 - sse / ssc:+.3f} (MSE)")
    ag = pv.groupby("ano").agg(obs=("obs", lambda s: np.expm1(s).sum()), hat=("hat", lambda s: np.expm1(s).sum()))
    r_ag, p_ag = stats.pearsonr(ag.obs, ag.hat)
    print(f"  LOYO estadual: r(previsto, observado) dos focos out-dez = {r_ag:+.2f} (p = {p_ag:.3f}), n = 14 anos")
    # aplicacao a 2026 com o modelo completo
    mcel = tr.groupby("cel").lf.mean()
    mpz = tr.groupby("cel")[["pz", "pz1"]].mean()
    beta = np.linalg.lstsq((tr[["pz", "pz1"]] - mpz.loc[tr.cel].values).values, (tr.lf - mcel.loc[tr.cel].values).values, rcond=None)[0]
    f26 = P[P.ano == 2026]
    h26 = mcel.loc[f26.cel].values + ((f26[["pz", "pz1"]] - mpz.loc[f26.cel].values).values @ beta)
    med = est.focos.mean()
    print(f"  2026: chuva fev-jun z medio = {f26.pz.mean():+.2f}; 2025 z medio = {f26.pz1.mean():+.2f}")
    print(f"  Previsao (emissao jul/2026) de focos out-dez 2026 no CE: ~{np.expm1(h26).sum():,.0f} "
          f"(media 2012-2025 = {med:,.0f}; max {est.focos.max():,.0f} em {est.focos.idxmax()})")
    print(f"  Proporcao de celulas com previsao acima da propria climatologia: {(h26 > mcel.loc[f26.cel].values).mean() * 100:.0f}%")
