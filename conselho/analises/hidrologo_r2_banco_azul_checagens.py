"""Hidrólogo — rodada 2 (debate): checagens rápidas do 'banco de água azul' com dados que chegaram depois da rodada 1.

(A) Estado do GRACE em ago/set-2026: reconcilia 'percentil 72 em jul/2026' (hidrólogo) com '−9,7 cm, 7º menor de 21
    setembros' (estrategista). São leituras diferentes (dessazonalizado contra bruto por mês)?
(B) GLDAS-2.2 CLSM (GWS, chegou agora, mensal CE): o residual GRACE − solo Noah se parece com a água subterrânea do CLSM?
    Estado do GWS em ago/2026. Ressalva: o CLSM-2.2 assimila o GRACE, então não é independente.
(C) Açudes vistos do espaço: fração de água (Landsat 1985–2026, por cena) na estação seca de cada AOI. Que memória (τ) a
    superfície d'água tem? Ela acompanha o residual do GRACE? Ela explica o 'verde na seca' (irrigação) do SR?
(D) ET0 anual do POWER (média CE) para conferir 2.226 mm (rodada 1, célula municipal) contra ~1.960 mm (síntese).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220)
AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")


def serie(arq, var, aoi=None):
    d = pd.read_parquet(DERIV / f"{arq}.parquet")
    d = d[d.variavel == var]
    if aoi is not None:
        d = d[d.aoi == aoi]
    s = d.set_index(pd.to_datetime(d.data))["valor"].sort_index()
    s.index = s.index.to_period("M").to_timestamp()
    return s.groupby(level=0).mean()


def dessaz(s, base=("2003", "2025")):
    clim = s[base[0]:base[1]].groupby(s[base[0]:base[1]].index.month).mean()
    return s - clim.reindex(s.index.month).values


def filtro_tau(p_anom, tau, kmax=120):
    k = np.arange(kmax)
    w = np.exp(-k / tau)
    x = p_anom.fillna(0).values
    y = np.convolve(x, w)[: len(x)]
    return pd.Series(y, index=p_anom.index)


# ---------------------------------------------------------------- (A)
print("=" * 30, "(A) GRACE CE: estado recente", "=" * 30)
g = serie("grace_ce_mensal", "TWS_anomalia")
gd = dessaz(g)
print("últimos meses (bruto | dessaz. | percentil do dessaz. na série toda):")
for t in g.index[-6:]:
    pct = stats.percentileofscore(gd.dropna(), gd[t])
    print(f"  {t:%Y-%m}: {g[t]:+6.2f} | {gd[t]:+6.2f} | p{pct:4.0f}")
setembros = g[g.index.month == 9]
rk = setembros.rank().iloc[-1]
print(f"setembros: n={len(setembros)}, set/2026 bruto = {setembros.iloc[-1]:+.2f}, posição {rk:.0f}º menor; mediana {setembros.median():+.2f}")
for m in (7, 8, 9):
    sm_ = gd[gd.index.month == m]
    print(f"  mês {m}: dessaz. 2026 = {sm_.iloc[-1]:+.2f} ; percentil entre os mesmos meses = {stats.percentileofscore(sm_.dropna(), sm_.iloc[-1]):.0f}")
# tendência que um 'bruto por mês' não remove: média 2003–2010 vs 2018–2025
print(f"média do dessaz.: 2003–2010 {gd['2003':'2010'].mean():+.2f} | 2011–2017 {gd['2011':'2017'].mean():+.2f} | 2018–2025 {gd['2018':'2025'].mean():+.2f}")

# ---------------------------------------------------------------- (B)
print("\n" + "=" * 30, "(B) GLDAS-2.2 CLSM GWS × residual GRACE − Noah", "=" * 30)
res = pd.read_csv(AN / "saidas" / "hidrologo_grace_residuo_ce.csv", parse_dates=["time"]).set_index("time")
res.index = res.index.to_period("M").to_timestamp()
resd = dessaz(res["residual"])
gws = serie("gldas_clsm_ce_mensal", "GWS_tavg") / 10.0  # mm -> cm
rzc = serie("gldas_clsm_ce_mensal", "SoilMoist_RZ_tavg") / 10.0
twc = serie("gldas_clsm_ce_mensal", "TWS_tavg") / 10.0
gwsd, rzcd, twcd = dessaz(gws), dessaz(rzc), dessaz(twc)
df = pd.concat({"res": resd, "gws": gwsd, "grace": gd, "clsm_tws": twcd, "clsm_rz": rzcd}, axis=1).dropna()
print(f"meses em comum: {len(df)} ({df.index.min():%Y-%m} a {df.index.max():%Y-%m})")
print("correlações (anomalias dessazonalizadas):")
print(df.corr().round(3).to_string())
print(f"dp (cm): {df.std().round(2).to_dict()}")
for lag in (0, 3, 6):
    print(f"  r(residual(t), GWS(t+{lag})) = {df.res.corr(df.gws.shift(-lag)):.3f}")
# fração do GRACE dessaz. que vem do GWS do CLSM (cov/var)
print(f"fração da variância do GRACE dessaz. 'explicada' pelo GWS CLSM (cov/var): {np.cov(df.grace, df.gws)[0,1]/df.grace.var():.2f}")
# autocorrelação do GWS
ac = {L: round(gwsd.dropna().autocorr(L), 2) for L in (1, 3, 6, 12, 24)}
print(f"autocorrelação do GWS dessaz.: {ac}")
print("GWS CLSM recente (bruto cm | dessaz. | percentil):")
for t in gws.index[-6:]:
    print(f"  {t:%Y-%m}: {gws[t]:7.2f} | {gwsd[t]:+6.2f} | p{stats.percentileofscore(gwsd.dropna(), gwsd[t]):.0f}")
mn = gwsd.idxmin()
rec = gwsd[mn:][gwsd[mn:] >= 0]
print(f"mínimo GWS dessaz.: {gwsd.min():+.2f} cm em {mn:%Y-%m}; primeiro mês >= 0 depois: {rec.index[0]:%Y-%m}" if len(rec) else "sem recuperação")
# memória do GWS por reservatório linear forçado pela chuva POWER (média CE)
p = serie("power_ce_mensal", "PRECTOTCORR")
pu = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
print("unidade PRECTOTCORR / ET0:", pu[pu.variavel == "PRECTOTCORR"].unidade.iloc[0], "/", pu[pu.variavel == "ET0"].unidade.iloc[0])
pa = dessaz(p, base=("1991", "2020"))
out = {}
for tau in (3, 6, 12, 18, 24, 36, 48, 60):
    f = filtro_tau(pa, tau)
    out[tau] = {"gws": round(gwsd.corr(f), 3), "residual": round(resd.corr(f), 3)}
print("r com a chuva filtrada exp(−k/τ):", out)

# ---------------------------------------------------------------- (C)
print("\n" + "=" * 30, "(C) Açudes do espaço: fração de água Landsat na seca", "=" * 30)
cen = pd.concat([pd.read_parquet(DADOS / "landsat" / "landsat_aoi_cenas_hist.parquet"),
                 pd.read_parquet(DADOS / "landsat" / "landsat_aoi_cenas_l89.parquet")], ignore_index=True)
cen["dt"] = pd.to_datetime(cen.datetime, utc=True).dt.tz_localize(None)
cen = cen[(cen.frac_valida >= 0.6) & cen.frac_agua.notna()]
cen = cen[cen.dt.dt.month.isin([8, 9, 10, 11, 12])]
cen["ano"] = cen.dt.dt.year
fa = cen.groupby(["aoi", "ano"]).agg(agua=("frac_agua", "median"), n=("frac_agua", "size")).reset_index()
fa = fa[fa.n >= 2]
print("fração de água (% da AOI) na seca, resumo por AOI:")
print(fa.groupby("aoi").agua.describe(percentiles=[.1, .5, .9]).mul(100).round(3).to_string())
irr = pd.read_csv(AN / "sr_fundacao_irrigacao_anual.csv")
rows = []
for aoi, sub in fa.groupby("aoi"):
    s = sub.set_index("ano").agua * 100
    if s.max() < 0.2:  # AOI sem espelho d'água relevante
        print(f"  {aoi}: água máxima {s.max():.3f}% — sem açude relevante na AOI, pulado")
        continue
    # memória: chuva POWER (CE) filtrada, média ago–dez de cada ano
    best = []
    for tau in (3, 6, 12, 18, 24, 36, 48, 60, 72):
        f = filtro_tau(pa, tau)
        fy = f[f.index.month >= 8].groupby(f[f.index.month >= 8].index.year).mean()
        j = pd.concat([s, fy], axis=1, keys=["a", "f"]).dropna()
        best.append((tau, stats.spearmanr(j.a, j.f)[0], len(j)))
    print(f"  {aoi}: n anos={len(s)} ({s.index.min()}–{s.index.max()}); ρ(água seca, chuva filtrada τ): "
          + ", ".join(f"τ{t}={r:+.2f}" for t, r, _ in best))
    # chuva fev–mai do mesmo ano (sem memória)
    pfm = p[p.index.month.isin([2, 3, 4, 5])]
    pfm = pfm.groupby(pfm.index.year).mean()
    j = pd.concat([s, pfm], axis=1, keys=["a", "p"]).dropna()
    print(f"     ρ com a chuva fev–mai do mesmo ano: {stats.spearmanr(j.a, j.p)[0]:+.2f} (n={len(j)})")
    # GRACE da AOI e residual CE (ago–dez)
    ga = dessaz(serie("grace_aoi_mensal", "TWS_anomalia", aoi))
    gy = ga[ga.index.month >= 8].groupby(ga[ga.index.month >= 8].index.year).mean()
    ry = resd[resd.index.month >= 8].groupby(resd[resd.index.month >= 8].index.year).mean()
    j = pd.concat([s, gy, ry], axis=1, keys=["a", "g", "r"]).dropna()
    print(f"     2002+: ρ(água, GRACE AOI ago–dez) = {stats.spearmanr(j.a, j.g)[0]:+.2f}; ρ(água, residual CE) = {stats.spearmanr(j.a, j.r)[0]:+.2f} (n={len(j)})")
    # água superficial explica o 'verde na seca' (SR)?
    ir = irr[irr.aoi == aoi].set_index("ano")
    if len(ir):
        j = pd.concat([s, ir.pct_irrig_ativa, gy], axis=1, keys=["a", "v", "g"]).dropna()
        ra = stats.spearmanr(j.a, j.v)
        rg = stats.spearmanr(j.g, j.v)
        # parcial: verde ~ água | GRACE (postos)
        rk_ = j.rank()
        e1 = rk_.v - np.polyval(np.polyfit(rk_.g, rk_.v, 1), rk_.g)
        e2 = rk_.a - np.polyval(np.polyfit(rk_.g, rk_.a, 1), rk_.g)
        print(f"     verde na seca (SR, n={len(j)}): ρ com água = {ra[0]:+.2f} (p={ra[1]:.3f}); com GRACE = {rg[0]:+.2f} (p={rg[1]:.3f}); parcial água|GRACE = {np.corrcoef(e1, e2)[0,1]:+.2f}")
    lst = s.loc[2010:]
    print("     água seca por ano (% AOI): " + " ".join(f"{a}:{v:.2f}" for a, v in lst.items()))
    rows.append(sub.assign(aoi=aoi))

# ---------------------------------------------------------------- (D)
print("\n" + "=" * 30, "(D) ET0 POWER média CE", "=" * 30)
et = serie("power_ce_mensal", "ET0")
pr = serie("power_ce_mensal", "PRECTOTCORR")
pi = serie("power_ce_mensal", "IMERG_PRECTOT")
dias = et.index.days_in_month
eta = (et * dias).groupby(et.index.year).sum()
pra = (pr * dias).groupby(pr.index.year).sum()
pia = (pi * dias).groupby(pi.index.year).sum()
print(f"ET0 anual 1991–2020 (média CE, supondo mm/dia): {eta.loc[1991:2020].mean():.0f} mm | chuva POWER {pra.loc[1991:2020].mean():.0f} | IMERG {pia.loc[1998:2020].mean():.0f}")
print(f"ET0 anual 1999–2025: {eta.loc[1999:2025].mean():.0f} mm")
