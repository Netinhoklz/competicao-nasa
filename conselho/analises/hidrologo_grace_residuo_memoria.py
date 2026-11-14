"""Hidrólogo — análise 2: o que o GRACE vê além do solo (água subterrânea + açudes) e quanto tempo dura a memória.

Perguntas:
  (a) Residual = GRACE TWS − umidade do solo 0–200 cm do GLDAS Noah (anomalias, cm). No Ceará, esse residual é
      dominado por água subterrânea e AÇUDES (Noah não tem aquífero nem reservatório). Quanto da variância do GRACE ele é?
  (b) Memória como reservatório linear: S(t) = a·Σ_k P'(t−k)·exp(−k/τ). Qual τ (meses) explica melhor o solo, o
      GRACE e o residual? (seção 20 testou janelas retangulares; aqui o τ tem sentido físico: tempo de esvaziamento.)
  (c) Persistência: correlação do residual dessazonalizado com ele mesmo 3, 6 e 12 meses depois (previsibilidade do
      estoque para decidir irrigação).
  (d) Panorama 2027: com o estado de set/2026 e τ estimado, quanto do déficit/excesso sobra em mai/2027 sob chuva normal
      e sob quadra seca (fev–mai −30%)?
  Contraponto: o mesmo para o Oeste da Bahia (aquífero Urucuia, caixa do MANIFESTO do GRACE).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import pymannkendall as mk
import shapely
import xarray as xr
from scipy import stats

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 200)
SAIDA = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
URU = (-46.6, -14.6, -44.0, -10.4)

gm = xr.open_dataset(DADOS / "gldas" / "gldas_noah025_mensal_ne.nc")
sm = (gm.SoilMoi0_10cm_inst + gm.SoilMoi10_40cm_inst + gm.SoilMoi40_100cm_inst + gm.SoilMoi100_200cm_inst)  # mm
gr = xr.open_dataset(DADOS / "grace" / "grace_ne_mensal.nc").lwe_thickness  # cm
pw = xr.open_dataset(DADOS / "power" / "power_ne_mensal.nc").PRECTOTCORR  # mm/dia (média mensal)
CE = ceara_gdf().union_all()


def media_regiao(da, regiao):
    lo, la = np.meshgrid(da.lon.values, da.lat.values)
    if isinstance(regiao, tuple):
        m = (lo >= regiao[0]) & (lo <= regiao[2]) & (la >= regiao[1]) & (la <= regiao[3])
    else:
        m = shapely.contains_xy(regiao, lo, la)
    s = da.where(xr.DataArray(m, dims=("lat", "lon"), coords={"lat": da.lat, "lon": da.lon})).mean(("lat", "lon")).to_series()
    s.index = pd.to_datetime(s.index).to_period("M").to_timestamp()
    return s.groupby(level=0).mean()


def dessaz(s):
    return s - s.groupby(s.index.month).transform("mean")


def kernel(p_anom, tau, nmax=180):
    w = np.exp(-np.arange(nmax) / tau)
    x = np.convolve(np.nan_to_num(p_anom.values), w)[: len(p_anom)]
    return pd.Series(x, index=p_anom.index)


resultados = {}
for nome, reg in [("Ceará", CE), ("Oeste BA (Urucuia)", URU)]:
    g = media_regiao(gr, reg)
    s = media_regiao(sm, reg) / 10.0  # mm -> cm
    p = media_regiao(pw, reg)
    p = p * p.index.days_in_month  # mm/mês
    base = (g.index >= "2004-01-01") & (g.index < "2010-01-01")
    s_an = s - s[(s.index >= "2004-01-01") & (s.index < "2010-01-01")].mean()
    j = pd.concat({"grace": g, "solo": s_an}, axis=1).dropna()
    j["residual"] = j.grace - j.solo
    print(f"\n================ {nome}: {len(j)} meses ({j.index.min():%Y-%m} a {j.index.max():%Y-%m}) ================")
    print("desvio-padrão (cm):", j.std().round(2).to_dict())
    print("r(GRACE, solo GLDAS) =", round(j.grace.corr(j.solo), 3), "| r(GRACE, residual) =", round(j.grace.corr(j.residual), 3))
    vd = dessaz(j)
    print("fração da variância do GRACE dessazonalizado explicada pelo residual (cov/var):",
          round(np.cov(vd.grace, vd.residual)[0, 1] / vd.grace.var(), 2), "| pelo solo:", round(np.cov(vd.grace, vd.solo)[0, 1] / vd.grace.var(), 2))
    for c in ["grace", "solo", "residual"]:
        a = j[c].resample("YE").mean(); a = a[(a.index.year >= 2003) & (a.index.year <= 2025)]
        r = mk.original_test(a.values)
        print(f"  tendência anual 2003–2025 {c:9s}: Sen {r.slope:+.2f} cm/ano, p = {r.p:.3f}")
    # seca 2012–2017
    d = vd["residual"]
    print("  residual dessaz.: mínimo", round(d.min(), 1), "cm em", f"{d.idxmin():%Y-%m}", "| meses < 0 em 2012–2017:",
          int((d["2012":"2017"] < 0).sum()), "de", int(d["2012":"2017"].notna().sum()))
    # (b) memória: tau ótimo
    pa = dessaz(p)
    linhas = []
    for alvo in ["solo", "grace", "residual"]:
        y = vd[alvo].dropna()
        melhor = None
        for tau in [1, 2, 3, 4, 6, 9, 12, 18, 24, 30, 36, 48, 60, 72]:
            x = kernel(pa, tau).reindex(y.index)
            ok = x.notna() & y.notna()
            r = np.corrcoef(x[ok], y[ok])[0, 1]
            linhas.append({"alvo": alvo, "tau_meses": tau, "r": r})
    M = pd.DataFrame(linhas)
    piv = M.pivot(index="tau_meses", columns="alvo", values="r").round(3)
    print("  correlação com a chuva filtrada por reservatório linear exp(−k/τ):\n", piv.to_string())
    taus = piv.idxmax().to_dict(); print("  τ ótimo (meses):", taus, "| r máx:", piv.max().round(3).to_dict())
    # atribuição: quanto da tendência do residual a chuva (filtrada com o τ ótimo) explica?
    tau_r = int(piv["residual"].idxmax())
    xk = kernel(pa, tau_r).reindex(vd.index)
    ok = xk.notna() & vd.residual.notna()
    a1, b1 = np.polyfit(xk[ok], vd.residual[ok], 1)
    ajust = a1 * xk + b1
    nao_expl = vd.residual - ajust
    anos = lambda s: s.resample("YE").mean().loc["2003":"2025"]
    tr_aj = mk.original_test(anos(ajust).values); tr_ne = mk.original_test(anos(nao_expl).values)
    pr_an = p.resample("YE").sum(); pr_an = pr_an[pr_an.index.year <= 2025]
    tp1 = mk.original_test(pr_an.loc["1981":].values); tp2 = mk.original_test(pr_an.loc["2002":].values)
    print(f"  chuva anual POWER: Sen 1981–2025 {tp1.slope:+.1f} mm/ano (p={tp1.p:.3f}); 2002–2025 {tp2.slope:+.1f} mm/ano (p={tp2.p:.3f})")
    print(f"  tendência do residual explicada pela chuva (τ={tau_r}): {tr_aj.slope:+.2f} cm/ano (p={tr_aj.p:.3f}) | "
          f"NÃO explicada pela chuva: {tr_ne.slope:+.2f} cm/ano (p={tr_ne.p:.3f})")
    # (c) persistência
    pers ={lag: round(vd.residual.autocorr(lag), 2) for lag in (1, 3, 6, 12, 24)}
    pers_s = {lag: round(vd.solo.autocorr(lag), 2) for lag in (1, 3, 6, 12, 24)}
    print("  autocorrelação do residual dessaz.:", pers, "| do solo:", pers_s)
    resultados[nome] = dict(j=j, vd=vd, taus=taus, p=p)

    # (d) panorama 2027 (só o Ceará): decaimento do estado atual
    if nome == "Ceará":
        ultimo = vd.index.max()
        tau = taus["residual"]
        x_now = vd.residual.loc[ultimo]
        meses = (pd.Timestamp("2027-05-01").to_period("M") - ultimo.to_period("M")).n
        # regressão y = a·kernel(P') para converter mm de chuva em cm de estoque
        xk = kernel(pa, tau).reindex(vd.index); ok = xk.notna()
        a_coef = np.polyfit(xk[ok], vd.residual[ok], 1)[0]
        clim_fmam = p.groupby(p.index.month).mean().loc[[2, 3, 4, 5]].sum()
        seca = -0.3 * clim_fmam
        # contribuição da quadra seca em mai/2027: chuva negativa distribuída fev–mai, decaindo até mai
        contrib = a_coef * sum((seca / 4) * np.exp(-k / tau) for k in range(4))
        print(f"  estado em {ultimo:%Y-%m}: residual dessaz. {x_now:+.1f} cm (GRACE dessaz. {vd.grace.loc[ultimo]:+.1f} cm; "
              f"percentil do GRACE dessaz.: {stats.percentileofscore(vd.grace.dropna(), vd.grace.loc[ultimo]):.0f})")
        print(f"  τ = {tau} meses → em mai/2027, chuva normal: {x_now * np.exp(-meses / tau):+.1f} cm; "
              f"quadra −30% ({seca:.0f} mm): {x_now * np.exp(-meses / tau) + contrib:+.1f} cm  (a = {a_coef:.4f} cm por mm filtrado)")
        # quantos meses o residual levou para voltar a >= 0 depois do mínimo da seca
        dmin = vd.residual["2012":"2018"].idxmin()
        volta = vd.residual[dmin:][vd.residual[dmin:] >= 0]
        print(f"  recuperação: mínimo em {dmin:%Y-%m}; primeiro mês >= 0 depois: {volta.index.min():%Y-%m}" if len(volta) else "  sem recuperação")
        j.to_csv(SAIDA / "hidrologo_grace_residuo_ce.csv")
