"""Hidrólogo, rodada 2, análise A4: a água subterrânea do GLDAS-2.2 CLSM (GWS) como "relógio lento", sem a
circularidade com o GRACE.

O problema: o CLSM-2.2 ASSIMILA o GRACE, então "GWS concorda com o GRACE" não prova nada. O desenho:
  1. Parte da chuva: regressão (OLS) da anomalia mensal do GWS em filtros exponenciais da anomalia de chuva IMERG
     (memória tau = 3, 6, 12, 24, 48 meses; chuva municipal média do Ceará, sem GRACE). R2 = quanto do GWS é só
     memória de chuva. O resíduo = o que a chuva não explica (inclui os incrementos da assimilação do GRACE).
  2. Diagnóstico da assimilação: no buraco GRACE -> GRACE-FO (jul/2017 a mai/2018) não há GRACE para assimilar.
     O resíduo muda de comportamento nesses meses?
  3. Teste com sensor independente (Landsat, açudes do Sertão Central, fração de água ago-dez, 2003-2025): qual parte do
     GWS acompanha a água azul de verdade, a da chuva ou o resíduo? Também o VIIRS NDVI de set-nov (2012-2025).
  4. Os dois relógios hoje: SMAP L4 (percentil da zona da raiz, até 10/11/2026) e GWS (até ago/2026).
Unidade de inferência: o ano (n de 14 a 23); sem seleção de tau no teste (os 5 filtros entram juntos na regressão).
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
CEU = ceara_gdf().union_all()


def serie(arq, var, aoi=None):
    d = pd.read_parquet(DERIV / f"{arq}.parquet")
    d = d[d.variavel == var]
    if aoi is not None:
        d = d[d.aoi == aoi]
    s = d.set_index(pd.to_datetime(d.data))["valor"].sort_index()
    s.index = s.index.to_period("M").to_timestamp()
    return s.groupby(level=0).mean()


def dessaz(s, base=("2003", "2025")):
    b = s[base[0]:base[1]]
    return s - b.groupby(b.index.month).mean().reindex(s.index.month).values


def filtro_tau(x, tau, kmax=180):
    w = np.exp(-np.arange(kmax) / tau)
    return pd.Series(np.convolve(x.fillna(0).values, w)[: len(x)], index=x.index)


def rho_parcial(y, x, z):
    """Spearman parcial de y com x controlando z (postos, resíduos de OLS)."""
    ry, rx, rz = stats.rankdata(y), stats.rankdata(x), stats.rankdata(z)
    Z = np.c_[np.ones(len(rz)), rz]
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    r = np.corrcoef(ey, ex)[0, 1]
    n = len(y)
    t = r * np.sqrt((n - 3) / (1 - r ** 2))
    return r, 2 * stats.t.sf(abs(t), n - 3)


# ------------------------------------------------------------------ dados
cl = xr.open_dataset(DADOS / "gldas" / "gldas_clsm025_diario_ne.nc")["GWS_tavg"].sel(lat=slice(-8.1, -2.4), lon=slice(-41.6, -36.9)).load()
lo, la = np.meshgrid(cl.lon.values, cl.lat.values)
m_ce = xr.DataArray(shapely.contains_xy(CEU, lo, la), coords={"lat": cl.lat, "lon": cl.lon}, dims=("lat", "lon"))
gws_ce = cl.where(m_ce).mean(("lat", "lon")).to_series()
lon_q, lat_q, _ = AOIS["sertao_central"]
gws_sc = cl.sel(lat=slice(lat_q - 0.25, lat_q + 0.25), lon=slice(lon_q - 0.25, lon_q + 0.25)).mean(("lat", "lon")).to_series()
gm = {}
for nome, s in [("CE", gws_ce), ("Sertão Central", gws_sc)]:
    s.index = pd.to_datetime(s.index)
    gm[nome] = s.resample("MS").mean() / 10.0  # mm -> cm
chuva = pd.read_parquet(AN / "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
p_ce = chuva.mean(1).resample("MS").sum()
p_ce = p_ce[: "2026-08-01"]
pa = dessaz(p_ce, base=("1998", "2025"))
grace = dessaz(serie("grace_ce_mensal", "TWS_anomalia"))
print(f"GWS CLSM: {gm['CE'].index.min():%Y-%m} -> {gm['CE'].index.max():%Y-%m} | chuva IMERG CE mensal: {p_ce.index.min():%Y-%m} -> {p_ce.index.max():%Y-%m}")

# ------------------------------------------------------------------ 1. quanto do GWS é memória de chuva
print("\n" + "=" * 25, "(1) GWS = memória de chuva + resíduo", "=" * 25)
TAUS = [3, 6, 12, 24, 48]
F = pd.DataFrame({f"tau{t}": filtro_tau(pa, t) for t in TAUS})
dec = {}
for nome in gm:
    g = dessaz(gm[nome])
    X = F.loc[g.index.intersection(F.index)]
    X = X[X.index >= "2003-02-01"]
    y = g.reindex(X.index)
    ok = y.notna()
    A = np.c_[np.ones(ok.sum()), X[ok].values]
    beta = np.linalg.lstsq(A, y[ok].values, rcond=None)[0]
    yhat = pd.Series(A @ beta, index=X[ok].index)
    res = y[ok] - yhat
    r2 = 1 - res.var() / y[ok].var()
    # mesmo ajuste, deixando o ANO de fora (para não inflar o R2)
    yh_lo = pd.Series(np.nan, index=X[ok].index)
    for a in sorted(set(X[ok].index.year)):
        tr = X[ok].index.year != a
        b = np.linalg.lstsq(A[tr], y[ok].values[tr], rcond=None)[0]
        yh_lo[~tr] = A[~tr] @ b
    r2_lo = 1 - ((y[ok] - yh_lo) ** 2).sum() / ((y[ok] - y[ok].mean()) ** 2).sum()
    dec[nome] = pd.DataFrame({"gws": y[ok], "chuva": yhat, "residuo": res})
    ac = {L: round(g.dropna().autocorr(L), 2) for L in (1, 3, 6, 12, 24)}
    efold = next((L for L in range(1, 60) if g.dropna().autocorr(L) < np.exp(-1)), None)
    print(f"  {nome:15s} n={ok.sum()} meses | R2 da chuva (5 filtros) {r2:.2f} | R2 deixando o ano de fora {r2_lo:.2f} | dp GWS {y[ok].std():.2f} cm, "
          f"dp resíduo {res.std():.2f} cm | autocorr {ac} | e-folding {efold} meses")
D = dec["CE"].join(grace.rename("grace"), how="left")
j = D.dropna()
print(f"  CE: r(GWS, GRACE) = {j.gws.corr(j.grace):.2f} | r(parte da chuva, GRACE) = {j.chuva.corr(j.grace):.2f} | r(resíduo, GRACE) = {j.residuo.corr(j.grace):.2f} (n={len(j)})")
print(f"  CE: r(chuva IMERG filtrada tau 12, GRACE) = {F.tau12.reindex(j.index).corr(j.grace):.2f} -> GRACE sem passar pelo CLSM")

# ------------------------------------------------------------------ 2. o buraco do GRACE
print("\n" + "=" * 25, "(2) Buraco GRACE -> GRACE-FO (jul/2017 a mai/2018): o resíduo do CLSM muda?", "=" * 25)
rr = dec["CE"].residuo
dr = rr.diff().abs()
gap = (dr.index >= "2017-07-01") & (dr.index <= "2018-05-01")
viz = ((dr.index >= "2015-07-01") & (dr.index < "2017-07-01")) | ((dr.index > "2018-05-01") & (dr.index <= "2020-05-01"))
print(f"  |variação mensal do resíduo| (cm): no buraco {dr[gap].mean():.2f} (n={gap.sum()}) | 2 anos antes e depois {dr[viz].mean():.2f} (n={viz.sum()}) | série toda {dr.mean():.2f}")
dg = dessaz(gm["CE"]).diff().abs()
print(f"  |variação mensal do GWS| (cm): no buraco {dg[gap].mean():.2f} | vizinhança {dg[viz].mean():.2f}")
print(f"  meses com GRACE no buraco (deveria ser 0): {grace.reindex(dr.index[gap]).notna().sum()}")
print("  resíduo e GRACE mês a mês em 2017-2018:")
print(pd.DataFrame({"resíduo": rr, "GRACE": grace})["2017-03":"2018-09"].round(2).T.to_string())

# ------------------------------------------------------------------ 3. sensor independente: açudes do Landsat e NDVI do VIIRS
print("\n" + "=" * 25, "(3) Teste independente: fração de água dos açudes (Landsat, Sertão Central, ago-dez)", "=" * 25)
cen = pd.concat([pd.read_parquet(DADOS / "landsat" / "landsat_aoi_cenas_hist.parquet"),
                 pd.read_parquet(DADOS / "landsat" / "landsat_aoi_cenas_l89.parquet")], ignore_index=True)
cen["dt"] = pd.to_datetime(cen.datetime, utc=True).dt.tz_localize(None)
cen = cen[(cen.aoi == "sertao_central") & (cen.frac_valida >= 0.6) & cen.frac_agua.notna() & cen.dt.dt.month.isin([8, 9, 10, 11, 12])]
cen["ano"] = cen.dt.dt.year
fa = cen.groupby("ano").agg(agua=("frac_agua", "median"), n=("frac_agua", "size"))
fa = fa[fa.n >= 2].agua * 100
ago_dez = lambda s: s[s.index.month >= 8].groupby(s[s.index.month >= 8].index.year).mean()
ds = dec["Sertão Central"]
Y = pd.DataFrame({"agua": fa, "gws_sc": ago_dez(ds.gws), "chuva_sc": ago_dez(ds.chuva), "residuo_sc": ago_dez(ds.residuo),
                  "gws_ce": ago_dez(dec["CE"].gws), "residuo_ce": ago_dez(dec["CE"].residuo),
                  "grace_ce": ago_dez(grace), "tau12": ago_dez(F.tau12), "tau48": ago_dez(F.tau48)}).dropna()
print(f"  anos: {Y.index.min()}-{Y.index.max()} (n={len(Y)})")
for c in ["gws_sc", "chuva_sc", "residuo_sc", "gws_ce", "residuo_ce", "grace_ce", "tau12", "tau48"]:
    r, pv = stats.spearmanr(Y.agua, Y[c])
    print(f"   rho(água dos açudes, {c:10s}) = {r:+.2f} (p={pv:.3f})")
for x, z in [("gws_sc", "chuva_sc"), ("residuo_sc", "chuva_sc"), ("grace_ce", "tau48"), ("gws_sc", "tau48")]:
    r, pv = rho_parcial(Y.agua.values, Y[x].values, Y[z].values)
    print(f"   rho parcial(água, {x} | {z}) = {r:+.2f} (p={pv:.3f})")
# variação de um ano para o outro (tira tendências comuns)
dY = Y.diff().dropna()
for c in ["gws_sc", "chuva_sc", "residuo_sc", "grace_ce"]:
    r, pv = stats.spearmanr(dY.agua, dY[c])
    print(f"   em diferenças anuais: rho(Δágua, Δ{c}) = {r:+.2f} (p={pv:.3f}, n={len(dY)})")

print("\n  VIIRS NDVI set-nov (Ceará, 2012-2025) contra o GWS de jul-ago e a chuva filtrada:")
vi = serie("viirs_ndvi_ce_mensal", "ndvi")
vi_son = vi[vi.index.month.isin([9, 10, 11])]
vi_son = vi_son.groupby(vi_son.index.year).mean()
ja = lambda s: s[s.index.month.isin([7, 8])].groupby(s[s.index.month.isin([7, 8])].index.year).mean()
V = pd.DataFrame({"ndvi_son": vi_son, "gws_ja": ja(dec["CE"].gws), "chuva_ja": ja(dec["CE"].chuva), "residuo_ja": ja(dec["CE"].residuo),
                  "chuva_fmam": p_ce[p_ce.index.month.isin([2, 3, 4, 5])].groupby(p_ce[p_ce.index.month.isin([2, 3, 4, 5])].index.year).sum()}).dropna()
V = V[V.index <= 2025]
for c in ["gws_ja", "chuva_ja", "residuo_ja", "chuva_fmam"]:
    r, pv = stats.spearmanr(V.ndvi_son, V[c])
    print(f"   rho(NDVI set-nov, {c:10s}) = {r:+.2f} (p={pv:.3f}, n={len(V)})")
r, pv = rho_parcial(V.ndvi_son.values, V.gws_ja.values, V.chuva_fmam.values)
print(f"   rho parcial(NDVI set-nov, GWS jul-ago | chuva fev-mai) = {r:+.2f} (p={pv:.3f})")
r, pv = rho_parcial(V.ndvi_son.values, V.gws_ja.values, V.chuva_ja.values)
print(f"   rho parcial(NDVI set-nov, GWS jul-ago | parte da chuva do GWS) = {r:+.2f} (p={pv:.3f})")
dV = V.diff().dropna()
for c in ["gws_ja", "chuva_ja", "residuo_ja", "chuva_fmam"]:
    r, pv = stats.spearmanr(dV.ndvi_son, dV[c])
    print(f"   em diferenças anuais: rho(ΔNDVI set-nov, Δ{c}) = {r:+.2f} (p={pv:.3f}, n={len(dV)})")

# ------------------------------------------------------------------ 4. os dois relógios hoje
print("\n" + "=" * 25, "(4) Os dois relógios hoje (Ceará)", "=" * 25)
pct = pd.read_parquet(SAI / "v2_hidrologo_smap_pctl_mun_diario.parquet")
rz = pd.read_parquet(SAI / "v2_hidrologo_smap_rz_mun_diario.parquet")
falta = pct.isna().groupby(pct.index.month).mean().mean(1)
print("   o percentil PRONTO do SMAP L4 (sm_rootzone_pctl) vem vazio em que fração dos município-dias, por mês (2015-2026):")
print("   " + " | ".join(f"{m}: {v:.0%}" for m, v in falta.items()))
print(f"   sm_rootzone (m3/m3) vazio: {rz.isna().mean().mean():.1%} dos município-dias")
# percentil PRÓPRIO: posição do sm_rootzone da janela de 7 dias contra a mesma janela dos outros anos (2015-2025), por município
for t in ["2026-08-31", "2026-09-30", "2026-10-31", "2026-11-10"]:
    t = pd.Timestamp(t)
    w = lambda a: rz.loc[pd.Timestamp(a, t.month, t.day) - pd.Timedelta(days=6):pd.Timestamp(a, t.month, t.day)].mean()
    hoje = w(2026)
    outros = pd.DataFrame({a: w(a) for a in range(2015, 2026)}).T
    proprio = (outros < hoje).mean() * 100
    pp = pct.loc[t - pd.Timedelta(days=6):t].mean()
    print(f"   {t:%d/%m/%Y}: percentil pronto (média CE) {pp.mean():.0f} ({pp.notna().mean():.0%} dos municípios com valor) | percentil próprio do sm_rootzone "
          f"contra 2015-2025: média {proprio.mean():.0f}, municípios abaixo de 20: {(proprio < 20).mean():.0%}, posto do CE {int((outros.mean(1) < hoje.mean()).sum()) + 1}º de 12")
g = dessaz(gm["CE"])
for t in g.index[-4:]:
    print(f"   GWS CLSM {t:%Y-%m}: anomalia {g[t]:+.2f} cm | percentil na série 2003-2026 {stats.percentileofscore(g.dropna(), g[t]):.0f} | "
          f"parte da chuva {dec['CE'].chuva.get(t, np.nan):+.2f} | resíduo {dec['CE'].residuo.get(t, np.nan):+.2f}")
print(f"   chuva IMERG CE dos últimos 12 meses até ago/2026: {p_ce['2025-09':'2026-08'].sum():.0f} mm | mediana 1998-2025 de set-ago: "
      f"{np.median([p_ce[f'{a - 1}-09':f'{a}-08'].sum() for a in range(1999, 2026)]):.0f} mm")
