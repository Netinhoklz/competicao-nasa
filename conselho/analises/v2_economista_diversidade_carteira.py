"""Economista, rodada 2, analise 1: o +6,6 p.p. da diversidade recalibra a carteira M4 e o "pior ano"?

Perguntas (pre-registradas antes de rodar):
 A) O efeito da diversidade na seca 2012-16 (+6,6 p.p., pesquisa/analise_diversidade_resiliencia.saida.txt) e
    COMPOSICAO (o municipio diverso planta culturas que sofrem menos; e exatamente o que a carteira M4 ja calcula)
    ou TRANSBORDAMENTO (cada cultura rende mais quando ha diversidade; seria um ganho EXTRA que a M4 nao ve)?
    Decomposicao: R1 = R1_comp + R1_resid, onde R1_comp usa, para cada cultura, a razao media dos OUTROS municipios
    (deixa o municipio de fora). Mesma regressao robusta (chuva, relevo, log da area, EF de mesorregiao, HC3) e
    tambem com erro agrupado por microrregiao.
 B) "Pior ano" da carteira REAL de cada municipio, 1998-2025: CVaR10 (media dos 10% piores anos) da razao anual do
    portfolio de temporarias (producao/area plantada sobre a mediana dos outros anos, ponderada pela area do ano).
    Inclinacao do CVaR10 por cultura efetiva, com IC90 por bootstrap de ANOS (a unidade independente e o ano).
    Comparacao com o que a M4 promete: 100% milho (1 cultura efetiva) -> 1/3 cada (3 culturas efetivas) = +0,21.
 C) Vies de sobrevivencia da carteira 1/3: a M4 so conta municipio-anos em que a mandioca existe (>= 50 ha).
    Em seca a mandioca some (Quixada 0 ha em 2012). Limite inferior "intencao de tratar": nos municipios de
    mandioca (mandioca canonica em >= 14 dos 28 anos), ano sem mandioca conta como mandioca = 0.
Somente le arquivos. Saida: v2_economista_diversidade_carteira.saida.txt
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa")
SAIDA = AQUI / "conselho/analises/v2_economista_diversidade_carteira.saida.txt"
LINHAS = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LINHAS.append(s)


rng = np.random.default_rng(7)
p = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
p["cod"] = p.cod_local.astype(str)
div = pd.read_csv(AQUI / "pesquisa/analise_diversidade_resiliencia.saida.csv", dtype={"cod": str}).set_index("cod")
nomes = json.loads((DADOS / "referencia" / "ceara_municipios_nomes.json").read_text(encoding="utf-8"))
micro = pd.Series({str(m["id"]): m["microrregiao"]["nome"] for m in nomes}, name="micro")
div = div.join(micro)

# ======================= A) composicao x transbordamento =======================
BASE, SECA = range(2004, 2012), range(2012, 2017)
tp = p[(p.area_colhida_ha > 0) & (p.rendimento_kg_ha > 0)]
rb = tp[tp.ano.isin(BASE)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
rs = tp[tp.ano.isin(SECA)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
ab = tp[tp.ano.isin(BASE) & (tp.tipo == "temporaria")].groupby(["cod", "produto"]).area_plantada_ha.mean()
J = pd.concat([(rs / rb).dropna().clip(0, 3).rename("r"), ab.rename("a")], axis=1).dropna().reset_index()
# razao media da cultura nos OUTROS municipios (estado) e na mesma mesorregiao (sem o proprio)
J = J.join(div.meso, on="cod")
soma = J.groupby("produto").r.transform("sum"); cont = J.groupby("produto").r.transform("count")
J["m_estado"] = (soma - J.r) / (cont - 1)
sm_ = J.groupby(["meso", "produto"]).r.transform("sum"); cm_ = J.groupby(["meso", "produto"]).r.transform("count")
J["m_meso"] = np.where(cm_ > 1, (sm_ - J.r) / (cm_ - 1).clip(lower=1), J.m_estado)
J = J.dropna(subset=["m_estado"])
wavg = lambda g, c: np.average(g[c], weights=g.a)  # noqa: E731
R = pd.DataFrame({"R1": J.groupby("cod").apply(wavg, "r"),
                  "R1_comp": J.groupby("cod").apply(wavg, "m_estado"),
                  "R1_comp_meso": J.groupby("cod").apply(wavg, "m_meso")})
R["R1_resid"] = R.R1 - R.R1_comp
R["R1_resid_meso"] = R.R1 - R.R1_comp_meso
d = div.join(R, how="inner").dropna(subset=["R1", "elev_media"])
out(f"A) replicacao: R1 recalculado x R1 do arquivo: r = {np.corrcoef(d.R1, d.R1_rend_rel_portfolio)[0, 1]:.4f}; n = {len(d)}")


def regride(dd, alvo, dv="n_efetivo_culturas", cluster=False):
    X = dd[[dv, "anom_chuva_seca", "chuva_clim_mm", "elev_media", "decl_media_graus"]].copy()
    X["log_area"] = np.log(dd.area_plantada_media_ha)
    sd = X[dv].std()
    Xz = (X - X.mean()) / X.std()
    fe = pd.get_dummies(dd.meso, drop_first=True, dtype=float)
    Xm = sm.add_constant(pd.concat([Xz, fe], axis=1))
    if cluster:
        g = pd.factorize(dd.micro)[0]
        m = sm.OLS(dd[alvo], Xm).fit(cov_type="cluster", cov_kwds={"groups": g})
    else:
        m = sm.OLS(dd[alvo], Xm).fit(cov_type="HC3")
    q1, q3 = dd[dv].quantile([0.25, 0.75])
    k = (q3 - q1) / sd
    return m.params[dv] * k, m.bse[dv] * k, m.pvalues[dv]


out("   Efeito Q1->Q3 de diversidade (2,34 -> 3,30 culturas efetivas), p.p. de rendimento relativo do portfolio na seca 2012-16:")
for alvo, rot in [("R1", "total (o +6,6 do teste)"), ("R1_comp", "composicao (razao da cultura nos outros municipios)"),
                  ("R1_resid", "transbordamento (resto)"), ("R1_comp_meso", "composicao, referencia da mesorregiao"),
                  ("R1_resid_meso", "transbordamento, referencia da mesorregiao")]:
    e, se, pv = regride(d, alvo)
    e2, se2, pv2 = regride(d, alvo, cluster=True)
    out(f"   {rot:52s} {100 * e:+5.1f} p.p. (EP {100 * se:.1f}; p HC3 {pv:.3f} | p agrupado por microrregiao {pv2:.3f})")
out("   razao media na seca por cultura (todos os municipios, nao ponderada): " +
    ", ".join(f"{k[:12]} {v:.2f}" for k, v in J.groupby("produto").r.mean().sort_values().items() if J.produto.eq(k).sum() >= 60))

# ======================= B) pior ano da carteira real, 1998-2025 =======================
t = p[(p.tipo == "temporaria") & p.ano.between(1998, 2025) & (p.area_plantada_ha >= 50)].copy()
t = t.groupby(["cod", "produto", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
t["r"] = t.producao_t / t.area_plantada_ha
t = t.sort_values(["cod", "produto", "ano"])


def med_outros(v):
    return np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])


t["ref"] = t.groupby(["cod", "produto"]).r.transform(lambda s: pd.Series(med_outros(s.values), index=s.index))
t["razao"] = (t.r / t.ref).clip(0, 3)
t = t.dropna(subset=["razao"])
port = t.groupby(["cod", "ano"]).apply(lambda g: np.average(g.razao, weights=g.area_plantada_ha)).unstack()  # mun x ano
mil = t[t.produto.str.startswith("Milho")].set_index(["cod", "ano"]).razao.unstack()
anos = port.columns.values
out(f"\nB) carteira real: {port.shape[0]} municipios x {len(anos)} anos; municipio-anos validos = {int(port.notna().sum().sum())}")


def cvar_linhas(M, q=0.10):
    M = np.asarray(M, float)
    res = np.full(M.shape[0], np.nan)
    for i, row in enumerate(M):
        v = np.sort(row[~np.isnan(row)])
        if len(v) >= 15:
            k = max(1, int(np.ceil(q * len(v))))
            res[i] = v[:k].mean()
    return res


def inclinacao(y, dd):
    """OLS de y em diversidade (culturas efetivas, nao padronizada) + chuva climatologica + relevo + log area + EF meso."""
    X = dd[["n_efetivo_culturas", "chuva_clim_mm", "elev_media", "decl_media_graus"]].copy()
    X["log_area"] = np.log(dd.area_plantada_media_ha)
    X = (X - X.mean())
    X["n_efetivo_culturas"] = dd.n_efetivo_culturas - dd.n_efetivo_culturas.mean()
    fe = pd.get_dummies(dd.meso, drop_first=True, dtype=float)
    A = np.column_stack([np.ones(len(dd)), X.values, fe.values])
    ok = ~np.isnan(y)
    b = np.linalg.lstsq(A[ok], y[ok], rcond=None)[0]
    return b[1]


dd = div.loc[div.index.intersection(port.index)].dropna(subset=["elev_media"])
P = port.loc[dd.index]
Mm = mil.reindex(dd.index)
# composicao anual: razao media da cultura no ano nos OUTROS municipios, ponderada pela area do proprio municipio
s_ = t.groupby(["produto", "ano"]).razao.transform("sum"); c_ = t.groupby(["produto", "ano"]).razao.transform("count")
t["m_out"] = np.where(c_ > 1, (s_ - t.razao) / (c_ - 1).clip(lower=1), np.nan)
tc = t.dropna(subset=["m_out"])
portc = tc.groupby(["cod", "ano"]).apply(lambda g: np.average(g.m_out, weights=g.area_plantada_ha)).unstack().reindex(index=dd.index, columns=anos)
cv = cvar_linhas(P.values)
cvc = cvar_linhas(portc.values)
cvm = cvar_linhas(Mm.reindex(columns=anos).values)
b_tot, b_comp, b_mil = inclinacao(cv, dd), inclinacao(cvc, dd), inclinacao(cvm, dd)
boot = {"tot": [], "comp": [], "mil": []}
for _ in range(500):
    cols = rng.integers(0, len(anos), len(anos))
    boot["tot"].append(inclinacao(cvar_linhas(P.values[:, cols]), dd))
    boot["comp"].append(inclinacao(cvar_linhas(portc.values[:, cols]), dd))
    boot["mil"].append(inclinacao(cvar_linhas(Mm.reindex(columns=anos).values[:, cols]), dd))
ic = {k: np.percentile(v, [5, 95]) for k, v in boot.items()}
out(f"   CVaR10 medio da carteira real: {np.nanmean(cv):.3f}; do milho sozinho no mesmo municipio: {np.nanmean(cvm):.3f}")
out(f"   inclinacao do CVaR10 por +1 cultura efetiva (controles + EF meso), IC90 bootstrap de anos (500):")
out(f"     carteira real                 {b_tot:+.3f}  [{ic['tot'][0]:+.3f}, {ic['tot'][1]:+.3f}]")
out(f"     so composicao (outros munic.) {b_comp:+.3f}  [{ic['comp'][0]:+.3f}, {ic['comp'][1]:+.3f}]")
out(f"     milho sozinho (placebo/transb.) {b_mil:+.3f}  [{ic['mil'][0]:+.3f}, {ic['mil'][1]:+.3f}]")
q1, q3 = dd.n_efetivo_culturas.quantile([0.25, 0.75])
out(f"   Q1->Q3 ({q1:.2f}->{q3:.2f}) no CVaR10 da carteira real: {b_tot * (q3 - q1):+.3f}; promessa da M4 por cultura efetiva: "
    f"(0,356-0,151)/2 = +0,103 (1 -> 3 culturas efetivas)")
# quais anos formam a cauda da carteira real
cauda = []
for i, row in enumerate(P.values):
    v = row[~np.isnan(row)]
    if len(v) >= 15:
        k = max(1, int(np.ceil(0.1 * len(v))))
        idx = np.argsort(np.where(np.isnan(row), np.inf, row))[:k]
        cauda += list(anos[idx])
out("   anos que formam a cauda de 10% da carteira real (contagem de municipio-anos): " +
    str(pd.Series(cauda).value_counts().head(8).to_dict()))

# ======================= C) vies de sobrevivencia da carteira 1/3 =======================
pam = p[p.ano.between(1998, 2025)]


def canonica(pref):
    q = pam[pam.produto.str.startswith(pref) & (pam.area_plantada_ha >= 50)]
    q = q.groupby(["cod", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    q["r"] = q.producao_t / q.area_plantada_ha
    q = q.sort_values(["cod", "ano"])
    o = []
    for c, g in q.groupby("cod"):
        r = g.r.values
        med = np.array([np.median(np.delete(r, i)) if len(r) > 1 else np.nan for i in range(len(r))])
        o.append(pd.DataFrame({"cod": c, "ano": g.ano.values, "razao": r / med}))
    return pd.concat(o).set_index(["cod", "ano"]).razao


Y = pd.DataFrame({"milho": canonica("Milho (em"), "feijao": canonica("Feij"), "mandioca": canonica("Mandioca")})
nmand = Y.mandioca.notna().groupby(level="cod").sum()
mun_mand = nmand[nmand >= 14].index
U = Y[Y.milho.notna() & Y.feijao.notna()]
U = U[U.index.get_level_values("cod").isin(mun_mand)].reset_index()
falta = U.mandioca.isna()
out(f"\nC) municipios de mandioca (>= 14 de 28 anos): {len(mun_mand)}; municipio-anos com milho e feijao: {len(U)}; sem mandioca no ano: {falta.sum()} ({100 * falta.mean():.1f}%)")
out(f"   milho medio quando a mandioca SOME: {U.milho[falta].mean():.3f} (mediana {U.milho[falta].median():.3f}) x quando existe: "
    f"{U.milho[~falta].mean():.3f} (mediana {U.milho[~falta].median():.3f})")
out("   fracao do ano sem mandioca nos anos de cauda: " +
    ", ".join(f"{a}: {100 * falta[U.ano == a].mean():.0f}%" for a in [1998, 2010, 2012, 2013, 2016] if (U.ano == a).any()))


def met(s):
    return s[s <= s.quantile(0.10)].mean(), (s < 0.5).mean()


U["mf"] = U[["milho", "feijao"]].mean(axis=1)
U["c13_excl"] = U[["milho", "feijao", "mandioca"]].mean(axis=1).where(~falta)
U["c13_itt0"] = (U.milho + U.feijao + U.mandioca.fillna(0)) / 3
U["c13_itt_mf"] = U[["milho", "feijao", "mandioca"]].mean(axis=1)  # ano sem mandioca: o terco vira milho+feijao
G = {a: U[U.ano == a] for a in U.ano.unique()}
bs = {k: [] for k in ["milho", "excl", "itt0", "ittmf", "g_excl", "g_itt0"]}
for _ in range(2000):
    B = pd.concat([G[a] for a in rng.choice(list(G), len(G))])
    cm = met(B.milho)[0]
    ce = met(B.c13_excl.dropna())[0]
    ci = met(B.c13_itt0)[0]
    bs["milho"].append(cm); bs["excl"].append(ce); bs["itt0"].append(ci); bs["ittmf"].append(met(B.c13_itt_mf)[0])
    bs["g_excl"].append(ce - met(B.milho[B.c13_excl.notna()])[0]); bs["g_itt0"].append(ci - cm)
for k, s, rot in [("milho", U.milho, "100% milho (todos os anos)"),
                  ("excl", U.c13_excl.dropna(), "1/3 cada, como a M4 (exclui ano sem mandioca)"),
                  ("ittmf", U.c13_itt_mf, "1/3, ano sem mandioca vira milho+feijao"),
                  ("itt0", U.c13_itt0, "1/3, ano sem mandioca = 0 (limite inferior)")]:
    c, pr = met(s)
    lo, hi = np.percentile(bs[k], [5, 95])
    out(f"   {rot:48s} CVaR10 = {c:.3f} IC90 ano [{lo:.3f}, {hi:.3f}]  P(<0,5) = {pr:.3f}  n = {len(s)}")
out(f"   ganho 1/3 - milho, como a M4: IC90 [{np.percentile(bs['g_excl'], 5):+.3f}, {np.percentile(bs['g_excl'], 95):+.3f}] | "
    f"limite inferior (sem mandioca = 0): IC90 [{np.percentile(bs['g_itt0'], 5):+.3f}, {np.percentile(bs['g_itt0'], 95):+.3f}]")

SAIDA.write_text("\n".join(LINHAS), encoding="utf-8")
