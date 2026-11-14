"""Economista agrícola — Análise A1: o portfólio de culturas do Ceará diversifica o risco de renda?

Pergunta: com a tecnologia de hoje e o clima de 2001–2025, quanto a renda por hectare do "sistema atual"
(milho + feijão) cai nos piores anos, e quanto um portfólio com culturas menos correlacionadas
(mandioca, castanha de caju, fava, mamona, algodão herbáceo, batata-doce) reduz essa cauda?

Método (simulação histórica, estilo "historical VaR"):
- IBGE PAM municipal (ibge_pam_mun_anual.parquet), 2001–2025 (permanentes mudam de unidade em 2001).
- Rendimento sem tendência tecnológica: tendência de Theil-Sen em log(rendimento) por município × cultura;
  desvio_t = rend_t / tendência_t. Renda simulada_t = rend. de 2025 (pela tendência) × desvio_t × preço.
- Preço constante = preço implícito estadual mediano 2019–2025 (valor / produção, R$/kg) — isola o risco de produção.
- Por município (com as culturas presentes em >= 18 dos 25 anos), métricas de renda/ha:
  média, CV, CVaR10 (média dos 10% piores anos ≈ 2–3 anos) e P(renda < 50% da média).
- Portfólios: "atual" = milho+feijão com os pesos de área 2019–2025; alternativas fixas;
  e o portfólio de mínimo CVaR (otimização linear de Rockafellar–Uryasev) e de máxima média com CVaR >= o atual.
- Correlação dos desvios (pooled dentro do município) entre culturas.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import warnings

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import linprog

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)

m = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
CULT = {
    "Milho (em grão)": "milho", "Feijão (em grão)": "feijao", "Mandioca": "mandioca",
    "Castanha de caju": "caju", "Fava (em grão)": "fava", "Mamona (baga)": "mamona",
    "Algodão herbáceo (em caroço)": "algodao", "Batata-doce": "batata_doce",
}
d = m[m.produto.isin(CULT) & m.ano.between(2001, 2025)].copy()
d["c"] = d.produto.map(CULT)

# preço implícito estadual 2019–2025 (R$/kg)
rec = d[d.ano.between(2019, 2025)]
preco = (rec.groupby("c").valor_mil_moeda.sum() * 1000 / (rec.groupby("c").producao_t.sum() * 1000))
print("Preço implícito estadual 2019–2025 (R$/kg):\n", preco.round(2).to_string())

ok = d[(d.area_colhida_ha >= 20) & (d.rendimento_kg_ha > 0)]

# desvio do rendimento à tendência Theil-Sen em log, por município × cultura
linhas = []
for (mun, c), g in ok.groupby(["cod_local", "c"]):
    if g.ano.nunique() < 18:
        continue
    y = np.log(g.rendimento_kg_ha.values)
    t = g.ano.values - 2001
    sl, ic, _, _ = stats.theilslopes(y, t)
    tend = np.exp(ic + sl * t)
    nivel_2025 = np.exp(ic + sl * (2025 - 2001))
    for ano, ren, td in zip(g.ano.values, g.rendimento_kg_ha.values, tend):
        linhas.append((mun, c, ano, ren / td, nivel_2025))
D = pd.DataFrame(linhas, columns=["mun", "c", "ano", "desvio", "nivel_2025"])
D["renda"] = D.desvio * D.nivel_2025 * D.c.map(preco)  # R$/ha com tecnologia e preço de hoje
print("\nPares município×cultura com >= 18 anos:", D.groupby("c").mun.nunique().to_dict())

# 1) correlação dos desvios entre culturas (dentro do município)
W = D.pivot_table(index=["mun", "ano"], columns="c", values="desvio")
corr = W.apply(np.log).corr(min_periods=200)
print("\nCorrelação dos log-desvios de rendimento (pooled dentro do município, 2001–2025):")
print(corr.round(2).to_string())

# risco por cultura isolada
uni = D.groupby(["c", "mun"]).renda.agg(
    media="mean", cv=lambda s: s.std() / s.mean(),
    cvar10=lambda s: s.nsmallest(max(1, int(round(0.1 * len(s))))).mean(),
    p_meia=lambda s: (s < 0.5 * s.mean()).mean()).reset_index()
uni["cvar_rel"] = uni.cvar10 / uni.media
print("\nRisco por cultura (mediana entre municípios): renda média R$/ha, CV, CVaR10/média, P(renda<50% da média)")
print(uni.groupby("c")[["media", "cv", "cvar_rel", "p_meia"]].median().round(2).sort_values("cv").to_string())


# 2) portfólios por município
def metricas(r):
    k = max(1, int(round(0.1 * len(r))))
    srt = np.sort(r)
    return dict(media=r.mean(), cv=r.std() / r.mean(), cvar_rel=srt[:k].mean() / r.mean(),
                p_meia=(r < 0.5 * r.mean()).mean(), pior=srt[0] / r.mean())


def min_cvar(R, alfa=0.10, media_min=None):
    """Rockafellar–Uryasev: minimiza CVaR da PERDA (−renda) com pesos >= 0 que somam 1."""
    T, n = R.shape
    # variáveis: w (n), z (1), u (T)
    c = np.r_[np.zeros(n), 1.0, np.full(T, 1.0 / (alfa * T))]
    # u_t >= -R_t w - z  ->  -R_t w - z - u_t <= 0
    A = np.hstack([-R, -np.ones((T, 1)), -np.eye(T)])
    b = np.zeros(T)
    if media_min is not None:
        A = np.vstack([A, np.r_[-R.mean(0), 0, np.zeros(T)]])
        b = np.r_[b, -media_min]
    Aeq = np.r_[np.ones(n), 0, np.zeros(T)][None, :]
    bounds = [(0, 1)] * n + [(None, None)] + [(0, None)] * T
    res = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=[1], bounds=bounds, method="highs")
    return res.x[:n] if res.success else None


area_rec = rec.groupby(["cod_local", "c"]).area_colhida_ha.sum().unstack(fill_value=0)
P = D.pivot_table(index=["mun", "ano"], columns="c", values="renda")
CAND = ["milho", "feijao", "mandioca", "caju", "fava", "mamona", "algodao", "batata_doce"]
FIX = {
    "atual milho+feijão (pesos de área)": None,
    "milho+feijão 50/50": {"milho": .5, "feijao": .5},
    "1/3 milho+feijão, 1/3 mandioca, 1/3 caju": {"milho": 1/6, "feijao": 1/6, "mandioca": 1/3, "caju": 1/3},
    "milho+feijão 60% + mandioca 40%": {"milho": .3, "feijao": .3, "mandioca": .4},
}
res = []
pesos_opt = []
for mun, g in P.groupby(level="mun"):
    g = g.droplevel(0)
    base = g[["milho", "feijao"]].dropna()
    if len(base) < 18:
        continue
    am, af = area_rec.loc[mun, "milho"] if mun in area_rec.index else 0, area_rec.loc[mun, "feijao"] if mun in area_rec.index else 0
    wa = am / (am + af) if (am + af) > 0 else 0.5
    for nome, w in FIX.items():
        w = {"milho": wa, "feijao": 1 - wa} if w is None else w
        cols = list(w)
        gg = g[cols].dropna()
        if len(gg) < 18:
            continue
        r = gg.values @ np.array([w[c] for c in cols])
        res.append(dict(mun=mun, portfolio=nome, anos=len(gg), **metricas(r)))
    # otimizados com as culturas que o município já cultiva (>= 18 anos em comum)
    cols = [c for c in CAND if c in g and g[c].notna().sum() >= 18]
    gg = g[cols].dropna()
    if len(cols) >= 3 and len(gg) >= 15:
        R = gg.values
        r_at = gg[["milho", "feijao"]].values @ np.array([wa, 1 - wa])
        w1 = min_cvar(R)
        w2 = min_cvar(R, media_min=r_at.mean())  # mesma renda média do atual, menor cauda
        if w1 is not None:
            res.append(dict(mun=mun, portfolio="ótimo: mínimo CVaR10", anos=len(gg), **metricas(R @ w1)))
        if w2 is not None:
            res.append(dict(mun=mun, portfolio="ótimo: mínimo CVaR10 c/ renda média >= atual", anos=len(gg), **metricas(R @ w2)))
            res.append(dict(mun=mun, portfolio="(atual no mesmo subconjunto de anos)", anos=len(gg), **metricas(r_at)))
            pesos_opt.append(dict(mun=mun, **dict(zip(cols, w2))))
RES = pd.DataFrame(res)
tab = RES.groupby("portfolio").agg(municipios=("mun", "nunique"), renda_media=("media", "median"), cv=("cv", "median"),
                                   cvar10_sobre_media=("cvar_rel", "median"), p_renda_abaixo_50pct=("p_meia", "median"),
                                   pior_ano_sobre_media=("pior", "median"))
print("\nPortfólios — mediana entre municípios (renda R$/ha a preço e tecnologia de hoje, clima 2001–2025):")
print(tab.round(3).to_string())

PW = pd.DataFrame(pesos_opt).set_index("mun").fillna(0)
print("\nPeso médio no portfólio 'mínimo CVaR com renda >= atual' (municípios):", len(PW))
print(PW.mean().round(3).sort_values(ascending=False).to_string())
print("Fração de municípios em que o ótimo põe >= 20% fora de milho+feijão:",
      round(float(((1 - PW.get("milho", 0) - PW.get("feijao", 0)) >= 0.2).mean()), 3))

# 3) os anos ruins: renda do atual nos anos de seca
at = RES[RES.portfolio == "atual milho+feijão (pesos de área)"]
print("\nAtual: CVaR10/média mediano =", round(at.cvar_rel.median(), 3), "| P(renda < 50% média) =", round(at.p_meia.median(), 3))
ano_med = P[["milho", "feijao"]].groupby(level="ano").median()
ano_med["mf"] = ano_med.mean(axis=1)
ano_med = ano_med.join(P.groupby(level="ano")[["mandioca", "caju"]].median())
print("\nRenda mediana por ano (R$/ha), milho, feijão, mandioca, caju:")
print((ano_med).round(0).to_string())

# 4) Diversificação pura: cada cultura normalizada para média 1 no município (equivale a supor margem esperada igual;
#    não temos custo de produção). Quanto a cauda cai só por combinar culturas pouco correlacionadas?
res2, pes2 = [], []
for mun, g in P.groupby(level="mun"):
    g = g.droplevel(0)
    cols = [c for c in CAND if c in g and g[c].notna().sum() >= 18]
    if "milho" not in cols or "feijao" not in cols:
        continue
    gg = g[cols].dropna()
    if len(gg) < 15:
        continue
    N = gg / gg.mean()
    am = area_rec.loc[mun, "milho"] if mun in area_rec.index else 0
    af = area_rec.loc[mun, "feijao"] if mun in area_rec.index else 0
    wa = am / (am + af) if (am + af) > 0 else 0.5
    r_at = N[["milho", "feijao"]].values @ np.array([wa, 1 - wa])
    res2.append(dict(mun=mun, portfolio="atual (milho+feijão)", ncult=len(cols), **metricas(r_at)))
    if len(cols) >= 3:
        w = min_cvar(N.values)
        if w is not None:
            res2.append(dict(mun=mun, portfolio="mínimo CVaR10 (culturas do próprio município)", ncult=len(cols), **metricas(N.values @ w)))
            pes2.append(dict(mun=mun, **dict(zip(cols, w))))
        for extra in ["mandioca", "caju", "fava", "batata_doce"]:
            if extra in cols:
                r = N[["milho", "feijao", extra]].values @ np.array([wa * .7, (1 - wa) * .7, .3])
                res2.append(dict(mun=mun, portfolio=f"70% atual + 30% {extra}", ncult=len(cols), **metricas(r)))
R2 = pd.DataFrame(res2)
print("\n[Normalizado: média 1 por cultura] mediana entre municípios:")
print(R2.groupby("portfolio").agg(municipios=("mun", "nunique"), cv=("cv", "median"), cvar10=("cvar_rel", "median"),
                                  p_abaixo_50=("p_meia", "median"), pior_ano=("pior", "median")).round(3).to_string())
PW2 = pd.DataFrame(pes2).set_index("mun").fillna(0)
print("Peso médio no mínimo CVaR normalizado (", len(PW2), "municípios):")
print(PW2.mean().round(3).sort_values(ascending=False).to_string())
# pareado: ganho de CVaR do ótimo vs atual por município
a = R2[R2.portfolio == "atual (milho+feijão)"].set_index("mun").cvar_rel
o = R2[R2.portfolio == "mínimo CVaR10 (culturas do próprio município)"].set_index("mun").cvar_rel
j = pd.concat([a, o], axis=1, keys=["atual", "otimo"]).dropna()
print(f"Pareado ({len(j)} municípios): CVaR10/média atual {j.atual.median():.3f} -> ótimo {j.otimo.median():.3f}; "
      f"melhora em {(j.otimo > j.atual).mean():.0%} dos municípios; Wilcoxon p = {stats.wilcoxon(j.otimo, j.atual).pvalue:.2g}")

# 5) Honestidade: o ótimo acima é dentro da amostra. Validação em blocos de 5 anos: otimiza nos outros 20 anos,
#    aplica os pesos no bloco deixado de fora e junta as rendas fora da amostra.
fora_at, fora_ot = [], []
for mun, g in P.groupby(level="mun"):
    g = g.droplevel(0)
    cols = [c for c in CAND if c in g and g[c].notna().sum() >= 18]
    if "milho" not in cols or "feijao" not in cols or len(cols) < 3:
        continue
    gg = g[cols].dropna()
    if len(gg) < 15:
        continue
    am = area_rec.loc[mun, "milho"] if mun in area_rec.index else 0
    af = area_rec.loc[mun, "feijao"] if mun in area_rec.index else 0
    wa = am / (am + af) if (am + af) > 0 else 0.5
    r_ot = pd.Series(index=gg.index, dtype=float)
    for b0 in range(2001, 2026, 5):
        te = gg.index[(gg.index >= b0) & (gg.index < b0 + 5)]
        tr = gg.index.difference(te)
        if len(te) == 0 or len(tr) < 12:
            continue
        mu = gg.loc[tr].mean()
        w = min_cvar((gg.loc[tr] / mu).values)
        if w is None:
            continue
        r_ot.loc[te] = (gg.loc[te] / mu).values @ w
    mu_all = gg.mean()
    r_at = (gg[["milho", "feijao"]] / mu_all[["milho", "feijao"]]).values @ np.array([wa, 1 - wa])
    r_ot = r_ot.dropna()
    if len(r_ot) >= 15:
        fora_ot.append(dict(mun=mun, **metricas(r_ot.values)))
        fora_at.append(dict(mun=mun, **metricas(r_at)))
FA, FO = pd.DataFrame(fora_at).set_index("mun"), pd.DataFrame(fora_ot).set_index("mun")
print(f"\nFora da amostra (blocos de 5 anos, {len(FO)} municípios): CVaR10/média atual {FA.cvar_rel.median():.3f} -> "
      f"ótimo {FO.cvar_rel.median():.3f}; P(<50%) {FA.p_meia.median():.3f} -> {FO.p_meia.median():.3f}; "
      f"CV {FA.cv.median():.3f} -> {FO.cv.median():.3f}; melhora em {(FO.cvar_rel > FA.cvar_rel).mean():.0%} dos municípios")

# 6) Prêmio atuarialmente justo de um seguro de renda com cobertura de 70% da média (E[max(0, 0,7·média − R)] / média)
def premio(r, cob=0.7):
    return np.maximum(0, cob * r.mean() - r).mean() / r.mean()


pr_at, pr_mand, pr_caju = [], [], []
for mun, g in P.groupby(level="mun"):
    g = g.droplevel(0)
    if not {"milho", "feijao"} <= set(g.columns):
        continue
    am = area_rec.loc[mun, "milho"] if mun in area_rec.index else 0
    af = area_rec.loc[mun, "feijao"] if mun in area_rec.index else 0
    wa = am / (am + af) if (am + af) > 0 else 0.5
    for extra, lista in (("mandioca", pr_mand), ("caju", pr_caju)):
        if extra not in g or g[extra].notna().sum() < 18:
            continue
        gg = g[["milho", "feijao", extra]].dropna()
        if len(gg) < 15:
            continue
        N = gg / gg.mean()
        r_at = N[["milho", "feijao"]].values @ np.array([wa, 1 - wa])
        r_mx = N.values @ np.array([wa * .7, (1 - wa) * .7, .3])
        lista.append((premio(r_at), premio(r_mx)))
for nome, l in (("mandioca", pr_mand), ("caju", pr_caju)):
    a = np.array(l)
    print(f"Prêmio justo (cobertura 70%), {len(a)} municípios: atual {np.median(a[:, 0]):.3f} da renda média -> "
          f"70% atual + 30% {nome} {np.median(a[:, 1]):.3f} (queda mediana {1 - np.median(a[:, 1] / np.maximum(a[:, 0], 1e-9)):.0%})")
