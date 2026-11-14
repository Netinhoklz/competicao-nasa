"""Agronomo do semiarido - 5a analise: o "falso inicio" aparece no rendimento REAL (IBGE PAM)?

Falso inicio (FI) = depois da 1a chuva de plantio (>= 20 mm em 3 dias, desde 1/jan), vem uma sequencia de >= 10 dias
com < 1 mm nos 30 dias seguintes. Compara a anomalia de rendimento (Theil-Sen, por area plantada) de milho e feijao
em municipio-anos COM e SEM falso inicio, dentro do mesmo tercil de chuva de fev-mai (controle da chuva total),
e estima a razao de chances de quebra >= 50% por regressao logistica (chuva fev-mai + FI + FI x mes do plantio).
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
chuva = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
cods = list(chuva.columns)
rows = []
for a in ANOS:
    blk = chuva.loc[f"{a}-01-01":f"{a}-10-31"].values  # dias x mun
    c3 = np.zeros_like(blk); c3[2:] = blk[2:] + blk[1:-1] + blk[:-2]
    for i, cod in enumerate(cods):
        okd = np.where(c3[2:120, i] >= 20)[0]
        s = int(okd[0] + 2) if len(okd) else 119
        jan = blk[s + 1:s + 31, i] < 1.0
        run = mx = 0
        for x in jan:
            run = run + 1 if x else 0; mx = max(mx, run)
        rows.append({"cod": cod, "ano": a, "sow": s + 1, "seco_max_30d": mx, "P_fmam": blk[31:151, i].sum()})
F = pd.DataFrame(rows)
F["FI"] = (F.seco_max_30d >= 10).astype(int)
F["plantio_jan"] = (F.sow <= 31).astype(int)

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.cod_local.str.startswith("23") & pam.ano.between(1998, 2025)]
for prod, nome in {"Milho (em grão)": "milho", "Feijão (em grão)": "feijao"}.items():
    s = pam[pam.produto == prod].copy()
    s["rp"] = np.where(s.area_plantada_ha > 0, s.producao_t * 1000 / s.area_plantada_ha, np.nan)
    Y = []
    for cod, g in s.groupby("cod_local"):
        if g.area_plantada_ha.mean() < 300:
            continue
        g = g.set_index("ano").sort_index(); yy = g.rp.where(g.rp > 0).dropna()
        if len(yy) < 15:
            continue
        sl, ic, _, _ = stats.theilslopes(np.log(yy.values), yy.index.values)
        an = g.rp / np.exp(ic + sl * g.index.values) - 1
        Y += [{"cod": cod, "ano": a, "anom": v} for a, v in an.items() if np.isfinite(v)]
    D = pd.DataFrame(Y).merge(F, on=["cod", "ano"])
    D["terc"] = D.groupby("cod").P_fmam.transform(lambda x: pd.qcut(x.rank(method="first"), 3, labels=["seco", "normal", "chuvoso"]))
    D["quebra"] = (D.anom <= -0.5).astype(int)
    print(f"\n=== {nome}: {len(D)} municipio-anos; falso inicio em {D.FI.mean():.0%}; plantio em janeiro em {D.plantio_jan.mean():.0%} ===")
    T = D.groupby(["terc", "FI"]).agg(n=("anom", "size"), anom_mediana=("anom", "median"), p_quebra50=("quebra", "mean")).unstack("FI")
    print(T.round(3).to_string())
    for t in ["seco", "normal", "chuvoso"]:
        a0 = D[(D.terc == t) & (D.FI == 0)].anom; a1 = D[(D.terc == t) & (D.FI == 1)].anom
        print(f"  tercil {t}: Mann-Whitney p={stats.mannwhitneyu(a0, a1).pvalue:.1e}")
    D["P100"] = D.P_fmam / 100
    m = smf.logit("quebra ~ P100 + FI + plantio_jan + FI:plantio_jan + C(cod)", data=D).fit(disp=0, maxiter=200)
    print(f"  logit (efeito fixo de municipio): OR(FI)={np.exp(m.params['FI']):.2f} "
          f"[IC95 {np.exp(m.conf_int().loc['FI', 0]):.2f}-{np.exp(m.conf_int().loc['FI', 1]):.2f}], "
          f"OR(+100 mm fev-mai)={np.exp(m.params['P100']):.2f}, OR(plantio em jan)={np.exp(m.params['plantio_jan']):.2f}, "
          f"OR(FI x jan)={np.exp(m.params['FI:plantio_jan']):.2f} (p={m.pvalues['FI:plantio_jan']:.2f})")
    print(f"  FI conforme o mes do plantio: jan={D[D.plantio_jan == 1].FI.mean():.0%}, fev+={D[D.plantio_jan == 0].FI.mean():.0%}")
