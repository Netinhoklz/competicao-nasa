"""Cientista do clima - Rodada 2: checagens rapidas de afirmacoes do conselho e relacoes nao exploradas.

B. GRACE: o "banco acima do normal (percentil 72, jul/2026)" do hidrologo ainda vale em set/2026?
C. Falso inicio de janeiro x ENSO: o oceano conhecido em dez (ONI OND) muda a chance de falso inicio (achado nº 1 do agronomo)?
D. ONI explica a quebra do milho ALEM da chuva total? E alem de chuva + veranico + calor (mecanismo do risco composto)?
E. Rota de fuga 1: com ONI ASO = 2,46, qual a chance de o ENSO decair a ~0 em FMA (como em 1973 e 1988)?
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV

import numpy as np
import pandas as pd
from scipy import stats

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
S = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas"

I = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
ONI = I["ONI"]  # mes central (preparar_indices.py)
DIP = I["DIPOLO_TNA_menos_TSA"]


def idx(serie, ano, mes):
    try:
        return float(serie.loc[pd.Timestamp(ano, mes, 1)])
    except KeyError:
        return np.nan


# ---------------------------------------------------------------- B. GRACE
print("=" * 30, "B. GRACE dessazonalizado", "=" * 30)
G = pd.read_parquet(DERIV / "grace_ce_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")["TWS_anomalia"]
G = G[G.index >= "2002-04-01"]
clim = G[(G.index.year >= 2003) & (G.index.year <= 2025)].groupby(G[(G.index.year >= 2003) & (G.index.year <= 2025)].index.month).mean()
Gd = G - G.index.month.map(clim).values
for d in ["2026-05-01", "2026-06-01", "2026-07-01", "2026-08-01", "2026-09-01"]:
    v = Gd.loc[d]
    pct = (Gd.dropna() < v).mean() * 100
    print(f"{d[:7]}: bruto {G.loc[d]:+.2f} cm | dessazonalizado {v:+.2f} cm | percentil {pct:.0f}")
setem = G[G.index.month == 9].dropna()
print(f"setembros: n={len(setem)}, mediana {setem.median():.2f}, posicao de 2026 = {int((setem < setem.iloc[-1]).sum()) + 1}o menor")

# ---------------------------------------------------------------- C. falso inicio x ENSO
print("\n" + "=" * 30, "C. falso inicio de janeiro x ENSO (IMERG municipal)", "=" * 30)
ch = pd.read_parquet(S + "/chuva_mun_diaria.parquet")
ch.index = pd.DatetimeIndex(ch.index)
linhas = []
for ano in range(1998, 2026):
    sub = ch[(ch.index >= f"{ano}-01-01") & (ch.index <= f"{ano}-06-30")]
    A = sub.values  # dias x mun
    nd = A.shape[0]
    ac3 = np.full_like(A, np.nan)
    ac3[2:] = A[2:] + A[1:-1] + A[:-2]
    for j in range(A.shape[1]):
        ok = np.where(ac3[:, j] >= 20)[0]
        if len(ok) == 0:
            linhas.append((ano, ch.columns[j], np.nan, np.nan, np.nan)); continue
        d = ok[0]
        jan = sub.index[d].month == 1
        jan_dez = sub.index[d].day <= 31 and jan
        seg = A[d + 1:d + 31, j] < 1.0
        # maior sequencia de dias secos (< 1 mm) nos 30 dias apos a 1a chuva de plantio
        m = c = 0
        for b in seg:
            c = c + 1 if b else 0
            m = max(m, c)
        linhas.append((ano, ch.columns[j], d + 1, int(jan_dez), int(m >= 10)))
F = pd.DataFrame(linhas, columns=["ano", "cod", "doy_inicio", "inicio_jan", "falso"])
F["jan_e_falso"] = F.inicio_jan * F.falso
anual = F.groupby("ano").agg(frac_inicio_jan=("inicio_jan", "mean"), frac_jan_falso=("jan_e_falso", "mean"),
                             doy_mediano=("doy_inicio", "median"))
anual["p_falso_dado_jan"] = F[F.inicio_jan == 1].groupby("ano").falso.mean()
anual["ONI_ASO_ant"] = [idx(ONI, a - 1, 9) for a in anual.index]
anual["ONI_OND_ant"] = [idx(ONI, a - 1, 11) for a in anual.index]
anual["DIP_OND_ant"] = [np.nanmean([idx(DIP, a - 1, m) for m in (10, 11, 12)]) for a in anual.index]
print(anual.round(2).to_string())
for alvo in ["frac_inicio_jan", "frac_jan_falso", "p_falso_dado_jan", "doy_mediano"]:
    for pred in ["ONI_ASO_ant", "ONI_OND_ant", "DIP_OND_ant"]:
        r, p = stats.spearmanr(anual[pred], anual[alvo], nan_policy="omit")
        print(f"  rho({pred:12s}, {alvo:16s}) = {r:+.2f} (p={p:.3f})")
en = anual.ONI_OND_ant >= 1.0
ln = anual.ONI_OND_ant <= -0.5
print(f"\nAnos El Nino (ONI OND ano anterior >= 1,0): {list(anual.index[en])}")
print(f"Anos La Nina (<= -0,5): {list(anual.index[ln])}")
for nome, msk in [("El Nino", en), ("neutro", ~en & ~ln), ("La Nina", ln)]:
    sel = F[F.ano.isin(anual.index[msk])]
    pj = sel.inicio_jan.mean(); pf = sel[sel.inicio_jan == 1].falso.mean(); pjf = sel.jan_e_falso.mean()
    print(f"  {nome:8s}: anos={msk.sum():2d} | P(inicio em jan)={pj:.2f} | P(falso | inicio jan)={pf:.2f} | P(jan e falso)={pjf:.2f}")
u = stats.mannwhitneyu(anual.loc[en, "p_falso_dado_jan"].dropna(), anual.loc[~en, "p_falso_dado_jan"].dropna())
print(f"  Mann-Whitney P(falso|jan), El Nino x demais (nivel ano): p={u.pvalue:.3f}")
anual.to_parquet(S + "/clima_r2_falso_inicio_anual.parquet")

# ---------------------------------------------------------------- D. ONI alem da chuva (estado, 1982-2025)
print("\n" + "=" * 30, "D. ONI explica a quebra do milho alem da chuva?", "=" * 30)
c = pd.read_parquet(S + "/clima_risco_composto_anual.parquet")
pam = pd.read_parquet(DERIV / "ibge_pam_ce_anual.parquet")
pam["ano"] = pam.data.dt.year
rend = pam[pam.variavel == "rendimento_kg_ha"].pivot_table(index="ano", columns="produto", values="valor")
print("produtos:", list(rend.columns)[:12])


def col(nome):
    for k in rend.columns:
        if nome.lower() in str(k).lower():
            return k
    return None


import statsmodels.api as sm

for cult in ["Milho", "Feij"]:
    k = col(cult)
    an = np.log(rend[k] / rend[k].rolling(9, center=True, min_periods=5).median())
    df = c.join(an.rename("anom"), how="inner").dropna(subset=["anom", "chuva_fmam", "ONI_NDJ"])
    df = df[(df.index >= 1982) & (df.index <= 2025)]
    z = lambda s: (s - s.mean()) / s.std()
    X = pd.DataFrame({"chuva": z(df.chuva_fmam), "ONI_NDJ": df.ONI_NDJ})
    m1 = sm.OLS(df.anom, sm.add_constant(X)).fit(cov_type="HC1")
    X2 = X.assign(veranico=z(df.maior_veranico), tmax=z(df.anom_tmax_fmam))
    m2 = sm.OLS(df.anom, sm.add_constant(X2)).fit(cov_type="HC1")
    X3 = pd.DataFrame({"chuva": z(df.chuva_fmam), "ONI_ASO_ant": df.ONI_ASO})
    m3 = sm.OLS(df.anom, sm.add_constant(X3)).fit(cov_type="HC1")
    print(f"\n{k}: n={len(df)} anos ({df.index.min()}-{df.index.max()})")
    print(f"  so chuva+ONI_NDJ : coef ONI={m1.params['ONI_NDJ']:+.3f} (p={m1.pvalues['ONI_NDJ']:.3f}); chuva={m1.params['chuva']:+.3f} (p={m1.pvalues['chuva']:.3f}); R2={m1.rsquared:.2f}")
    print(f"  + veranico + Tmax: coef ONI={m2.params['ONI_NDJ']:+.3f} (p={m2.pvalues['ONI_NDJ']:.3f}); veranico={m2.params['veranico']:+.3f} (p={m2.pvalues['veranico']:.3f}); tmax={m2.params['tmax']:+.3f} (p={m2.pvalues['tmax']:.3f}); R2={m2.rsquared:.2f}")
    print(f"  chuva+ONI_ASO(ano ant., conhecido em nov): coef={m3.params['ONI_ASO_ant']:+.3f} (p={m3.pvalues['ONI_ASO_ant']:.3f}); R2={m3.rsquared:.2f}")
    # parcial de postos
    rr = lambda a, b: stats.spearmanr(a, b)[0]
    res_y = stats.rankdata(df.anom) - np.poly1d(np.polyfit(stats.rankdata(df.chuva_fmam), stats.rankdata(df.anom), 1))(stats.rankdata(df.chuva_fmam))
    res_x = stats.rankdata(df.ONI_NDJ) - np.poly1d(np.polyfit(stats.rankdata(df.chuva_fmam), stats.rankdata(df.ONI_NDJ), 1))(stats.rankdata(df.chuva_fmam))
    rp, pp = stats.pearsonr(res_x, res_y)
    print(f"  rho bruto(ONI_NDJ, anom)={rr(df.ONI_NDJ, df.anom):+.2f}; parcial dado chuva={rp:+.2f} (p={pp:.3f})")
    # municipal: na mesma chuva, El Nino quebra mais?
pn = pd.read_parquet(S + "/painel_mun_ce.parquet").drop_duplicates(["cod", "ano"])
pn = pn[pn.aplant_milho > 50].copy()
pn["prod_plant"] = pn.rend_milho * pn.acolh_milho / pn.aplant_milho
med = pn.groupby("cod").prod_plant.transform("median")
pn["quebra"] = (pn.prod_plant < 0.5 * med).astype(int)
pn["pct_normal"] = pn.P_fmam / pn.groupby("cod").P_fmam.transform("median")
pn["ONI_OND_ant"] = pn.ano.map(lambda a: idx(ONI, a - 1, 11))
pn["faixa"] = pd.cut(pn.pct_normal, [0, 0.7, 0.9, 1.1, 10], labels=["<70%", "70-90%", "90-110%", ">110%"])
pn["fase"] = np.where(pn.ONI_OND_ant >= 1.0, "El Nino", np.where(pn.ONI_OND_ant <= -0.5, "La Nina", "neutro"))
tab = pn.pivot_table(index="faixa", columns="fase", values="quebra", aggfunc=["mean", "count"])
print("\nMunicipal (IMERG 1998-2025): P(quebra milho <50% da mediana) por faixa de chuva fev-mai (% do normal) e fase do ENSO")
print(tab.round(2).to_string())

# ---------------------------------------------------------------- E. decaimento do ENSO
print("\n" + "=" * 30, "E. ONI ASO(y-1) -> ONI FMA(y)", "=" * 30)
anos = range(1951, 2026)
d = pd.DataFrame({"ASO": [idx(ONI, a - 1, 9) for a in anos], "FMA": [idx(ONI, a, 3) for a in anos],
                  "DIP_FMAM": [np.nanmean([idx(DIP, a, m) for m in (2, 3, 4, 5)]) for a in anos]}, index=list(anos)).dropna()
fort = d[d.ASO >= 1.3]
print(fort.round(2).to_string())
b = np.polyfit(d.ASO, d.FMA, 1); res = d.FMA - np.polyval(b, d.ASO)
print(f"todos os anos: FMA = {b[0]:.2f}*ASO {b[1]:+.2f}; dp resid {res.std():.2f}; previsto p/ ASO 2,46: {np.polyval(b, 2.46):.2f}")
bf = np.polyfit(fort.ASO, fort.FMA, 1)
print(f"so ASO>=1,3 (n={len(fort)}): FMA medio {fort.FMA.mean():.2f}; FMA<=0,5 em {(fort.FMA <= 0.5).sum()} de {len(fort)}")
pr = stats.norm.cdf((0.5 - np.polyval(b, 2.46)) / res.std())
print(f"P(FMA 2027 <= 0,5 | ASO 2,46) pela regressao de todos os anos (normal): {pr:.2f}  [extrapolacao]")
