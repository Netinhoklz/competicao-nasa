"""Agronomo do semiarido - rodada 2 (debate): checagens rapidas de afirmacoes cruzadas.

A. Valor ONI de 2026 (as propostas citam 2,14 / 2,31 / 2,46: qual trimestre e qual valor?).
B. Falso inicio x ENSO: o El Nino aumenta o falso inicio e o plantio em janeiro? A quebra do milho
   com FI + plantio em janeiro e pior em El Nino? (decide o portao G2 de jan/2027)
C. Mandioca como "amortecedor": quanto do amortecimento vem da flexibilidade de colheita
   (area colhida < plantada; rendimento sobre area colhida) e nao da tolerancia da planta?
   Compara anomalia da producao/area plantada, do rendimento oficial (area colhida) e da producao total.
D. Sorgo como amortecedor hidrico (hidrologo) x sorgo no PAM (estrategista: n pequeno, irrigacao?).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")
OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
ANOS = np.arange(1998, 2026)

# ---------------------------------------------------------------- A. ONI 2026
ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
oni = ind[ind.variavel == "ONI"].set_index("data").valor
oni.index = pd.to_datetime(oni.index)
print("=== A. ONI recente (cada mes = trimestre centrado; ex.: ago = JAS, set = ASO) ===")
print(oni["2026-01-01":].round(2).to_string())
print("Maximos historicos por mes-centro (ate 2025):")
for m, lab in [(8, "JAS"), (9, "ASO"), (10, "SON")]:
    s = oni[(oni.index.month == m) & (oni.index.year <= 2025)]
    print(f"  {lab}: max {s.max():.2f} em {s.idxmax().year}")

# ONI out-jan (OND..DJF medio) que antecede a quadra do ano a: meses 11,12 de a-1 e 1 de a (centros NDJ)
def oni_quadra(a):
    v = oni[f"{a-1}-10-01":f"{a}-01-01"]
    return v.mean()

enso = pd.DataFrame({"ano": ANOS, "oni_ondj": [oni_quadra(a) for a in ANOS]})
enso["fase"] = np.where(enso.oni_ondj >= 1.0, "ElNino", np.where(enso.oni_ondj <= -0.5, "LaNina", "neutro"))
print("\nAnos El Nino (ONI out-jan >= 1,0):", enso[enso.fase == "ElNino"].ano.tolist())

# ---------------------------------------------------------------- B. falso inicio x ENSO
chuva = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
cods = list(chuva.columns)
rows = []
for a in ANOS:
    blk = chuva.loc[f"{a}-01-01":f"{a}-10-31"].values
    c3 = np.zeros_like(blk); c3[2:] = blk[2:] + blk[1:-1] + blk[:-2]
    for i, cod in enumerate(cods):
        okd = np.where(c3[2:120, i] >= 20)[0]
        s = int(okd[0] + 2) if len(okd) else 119
        jan = blk[s + 1:s + 31, i] < 1.0
        run = mx = 0
        for x in jan:
            run = run + 1 if x else 0; mx = max(mx, run)
        rows.append({"cod": cod, "ano": a, "sow": s + 1, "seco_max_30d": mx, "P_fmam": blk[31:151, i].sum(),
                     "P_jan": blk[0:31, i].sum()})
F = pd.DataFrame(rows).merge(enso, on="ano")
F["FI"] = (F.seco_max_30d >= 10).astype(int)
F["plantio_jan"] = (F.sow <= 31).astype(int)
F["FI_jan"] = F.FI * F.plantio_jan
print("\n=== B. Falso inicio (>=10 d < 1 mm nos 30 d apos a 1a chuva de 20 mm/3 d) por fase do ENSO ===")
print(F.groupby("fase")[["FI", "plantio_jan", "FI_jan"]].mean().round(3).to_string())
print("Por ano (fracao de municipios):")
tab = F.groupby("ano")[["FI", "plantio_jan", "FI_jan"]].mean().join(enso.set_index("ano"))
print(tab.round(2).to_string())
r = stats.spearmanr(tab.oni_ondj, tab.FI_jan)
print(f"Spearman ONI out-jan x fracao de municipios com FI apos plantio em janeiro: rho={r.statistic:+.2f} p={r.pvalue:.3f} (n={len(tab)})")
r2 = stats.spearmanr(tab.oni_ondj, tab.FI)
print(f"Spearman ONI out-jan x fracao com FI (qualquer mes): rho={r2.statistic:+.2f} p={r2.pvalue:.3f}")

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.cod_local.str.startswith("23")]


def anomalias(prod, anos=(1998, 2025), min_area=300, col="rp"):
    s = pam[(pam.produto == prod) & pam.ano.between(*anos)].copy()
    s["rp"] = np.where(s.area_plantada_ha > 0, s.producao_t * 1000 / s.area_plantada_ha, np.nan)
    s["rc"] = np.where(s.area_colhida_ha > 0, s.producao_t * 1000 / s.area_colhida_ha, np.nan)
    s["prod"] = s.producao_t
    s["fcol"] = np.where(s.area_plantada_ha > 0, s.area_colhida_ha / s.area_plantada_ha, np.nan)
    Y = []
    for cod, g in s.groupby("cod_local"):
        if g.area_plantada_ha.mean() < min_area:
            continue
        g = g.set_index("ano").sort_index()
        out = {}
        for c in ["rp", "rc", "prod"]:
            yy = g[c].where(g[c] > 0).dropna()
            if len(yy) < 15:
                out = None; break
            sl, ic, _, _ = stats.theilslopes(np.log(yy.values), yy.index.values)
            out[c] = g[c] / np.exp(ic + sl * g.index.values) - 1
        if out is None:
            continue
        for a in g.index:
            Y.append({"cod": cod, "ano": a, "an_rp": out["rp"].get(a, np.nan), "an_rc": out["rc"].get(a, np.nan),
                      "an_prod": out["prod"].get(a, np.nan), "fcol": g.fcol.get(a, np.nan)})
    return pd.DataFrame(Y)


M = anomalias("Milho (em grão)").merge(F, on=["cod", "ano"])
M["quebra"] = (M.an_rp <= -0.5).astype(int)
print("\nMilho: P(quebra >= 50%) por fase x (falso inicio apos plantio em janeiro)")
print(M.groupby(["fase", "FI_jan"]).quebra.agg(["mean", "size"]).round(3).to_string())
M["P100"] = M.P_fmam / 100
M["elnino"] = (M.fase == "ElNino").astype(int)
try:
    m = smf.logit("quebra ~ P100 + FI_jan + elnino + FI_jan:elnino + C(cod)", data=M).fit(disp=0, maxiter=300)
    for k in ["FI_jan", "elnino", "FI_jan:elnino"]:
        print(f"  OR({k})={np.exp(m.params[k]):.2f} [IC95 {np.exp(m.conf_int().loc[k, 0]):.2f}-{np.exp(m.conf_int().loc[k, 1]):.2f}] p={m.pvalues[k]:.3f}")
except Exception as e:  # noqa
    print("  logit falhou:", e)
# chuva de janeiro alta e falso inicio (o 'janeiro enganador' de 2016)
F["jan_rel"] = F.P_jan / F.groupby("cod").P_jan.transform("median")
F["jan_alto"] = (F.jan_rel >= 1.5).astype(int)
print("\nJaneiro >= 150% do normal do municipio: P(FI apos plantio em jan) e P(chuva fev-mai no tercil seco)")
F["terc_seco"] = (F.P_fmam <= F.groupby("cod").P_fmam.transform(lambda x: x.quantile(1 / 3))).astype(int)
print(F.groupby("jan_alto")[["FI_jan", "terc_seco"]].mean().round(3).to_string())

# ---------------------------------------------------------------- C. mandioca: tolerancia ou flexibilidade de colheita?
print("\n=== C. Mandioca x milho x feijao nos 20% anos mais secos de cada municipio (fev-mai IMERG) ===")
res = []
for prod, nome in [("Mandioca", "mandioca"), ("Milho (em grão)", "milho"), ("Feijão (em grão)", "feijao")]:
    A = anomalias(prod, min_area=100 if nome == "mandioca" else 300).merge(F[["cod", "ano", "P_fmam"]], on=["cod", "ano"])
    A["q20"] = A.groupby("cod").P_fmam.transform(lambda x: x <= x.quantile(0.2))
    sec = A[A.q20]; nor = A[~A.q20]
    res.append({"cultura": nome, "n_mun": A.cod.nunique(),
                "anom_prod/area_plant (seco)": sec.an_rp.median(), "anom_rend_oficial/area_colh (seco)": sec.an_rc.median(),
                "anom_producao_total (seco)": sec.an_prod.median(),
                "frac_colhida/plantada (seco)": sec.fcol.median(), "frac_colhida/plantada (demais)": nor.fcol.median(),
                "rho_rp_chuva_t": stats.spearmanr(A.an_rp, A.P_fmam, nan_policy="omit").statistic})
    # chuva de t-1 e de t+1 (colheita adiada aparece no ano seguinte?)
    Pm = F.pivot(index="ano", columns="cod", values="P_fmam")
    lag = []
    for d in (-1, 1):
        A[f"P_t{d:+d}"] = [Pm.at[a + d, c] if (a + d) in Pm.index else np.nan for c, a in zip(A.cod, A.ano)]
        lag.append(stats.spearmanr(A.an_rp, A[f"P_t{d:+d}"], nan_policy="omit").statistic)
    res[-1]["rho_rp_chuva_t-1"] = lag[0]; res[-1]["rho_rp_chuva_t+1"] = lag[1]
print(pd.DataFrame(res).set_index("cultura").T.round(3).to_string())

# ---------------------------------------------------------------- D. sorgo no balde x no PAM
print("\n=== D. Sorgo: balde (ISNA floracao) x PAM ===")
I = pd.read_parquet(OUT / "agronomo_isna_mun_ano.parquet")
byy = I.groupby("ano")[["isna_flor_milho", "isna_flor_caupi", "isna_flor_sorgo"]].median()
print("Piores anos (mediana estadual do ISNA na floracao, regra de 20 mm/3 d):")
print(byy.sort_values("isna_flor_milho").head(6).round(2).to_string())
for c in ["milho", "caupi", "sorgo"]:
    print(f"  P(ISNA flor < 0,5) {c}: {(I[f'isna_flor_{c}'] < 0.5).mean():.1%}")
S = pam[(pam.produto.str.startswith("Sorgo")) & pam.ano.between(1998, 2025)]
print("Produtos de sorgo no PAM-CE:", S.produto.unique().tolist())
g = S.groupby("ano")[["area_plantada_ha", "producao_t"]].sum()
g["rend"] = g.producao_t * 1000 / g.area_plantada_ha
print(g.round(0).to_string())
print("Municipios com sorgo >= 50 ha em algum ano:", S[S.area_plantada_ha >= 50].cod_local.nunique())
