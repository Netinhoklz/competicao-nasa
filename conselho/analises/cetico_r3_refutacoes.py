"""Cetico cientifico - Rodada 3 (banca adversaria do rascunho_v1): checagens rapidas para tentar REFUTAR numeros.

A. "El Nino dobra a quebra alem da chuva" (OR 2,30; IC 1,83-2,89): EP agrupado por ANO, chuva flexivel, jackknife de anos.
B. "Em janeiro ninguem sabe" (AUC 0,52): qual a AUC do ONI (ja conhecido em nov e em jan) para a quebra municipal?
C. "ONI ASO reduz a anomalia estadual em -0,208 alem da chuva": robustez a chuva nao linear, chuva mensal, IMERG, jackknife.
D. Analogos: intervalos de Clopper-Pearson para 4/7, 3/4, 3/6 e sensibilidade ao limiar de ONI ASO.
E. GRACE: a queda ago->set/2026 (-5,8 cm) e incomum frente ao ruido mes a mes?
F. Milho x feijao: correlacao depois de tirar o choque comum do ano.
G. Habilidade em 30/abr e "previsao" ou ja e o proprio resultado? AUC da chuva fev-mai inteira (fim da quadra).
H. 2012 era mesmo "invisivel ate abril"? % do normal acumulado desde 1/jan no estado em 2012, 2016, 1998.
Regras: so le derivados; nao escreve nada fora deste script.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
S = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas/"
rng = np.random.default_rng(0)

ind = pd.read_parquet(D + "indices_clima_mensal.parquet")
oni = ind[ind.variavel == "ONI"].set_index("data")["valor"]


def oni_em(ano, mes):
    return float(oni.get(pd.Timestamp(ano, mes, 1), np.nan))


# ---------------- quebra canonica (mesma receita do arquiteto) ----------------
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")


def serie(prefixo):
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        out = np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])
        return pd.Series(out, index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref
    p["quebra"] = (p.razao < 0.5).astype(int)
    return p.dropna(subset=["razao"])


mi = serie("Milho (em gr")
fe = serie("Feij")
pn = pd.read_parquet(S + "painel_mun_ce.parquet").drop_duplicates(["cod", "ano"])
pn["cod"] = pn.cod.astype(str)
mi["cod"] = mi.cod_local.astype(str).str[:7]
M = mi.merge(pn[["cod", "ano", "P_jan", "P_fev", "P_mar", "P_abr", "P_mai", "P_fmam", "veranico_max_fmam"]], on=["cod", "ano"], how="inner")
M["norm"] = M.groupby("cod").P_fmam.transform("median")
M["pct"] = M.P_fmam / M.norm
M["P100"] = M.P_fmam / 100
M["oni_ndj"] = M.ano.map(lambda a: oni_em(a - 1, 12))
M["oni_aso"] = M.ano.map(lambda a: oni_em(a - 1, 9))
M["oni_ond"] = M.ano.map(lambda a: oni_em(a - 1, 11))
M["elnino"] = (M.oni_ndj >= 1.0).astype(int)
print(f"painel milho canonico x chuva IMERG: n={len(M)} municipio-anos, {M.cod.nunique()} municipios, {M.ano.nunique()} anos; "
      f"taxa de quebra {M.quebra.mean():.3f}; anos El Nino (NDJ>=1): {sorted(M[M.elnino == 1].ano.unique())}")

# ================================================================ A
print("\n" + "=" * 25, "A. OR do El Nino 'alem da chuva' com inferencia por ANO", "=" * 25)
f0 = "quebra ~ P100 + elnino + C(cod)"
m_iid = smf.logit(f0, data=M).fit(disp=0, maxiter=300)
m_cl = smf.logit(f0, data=M).fit(disp=0, maxiter=300, cov_type="cluster", cov_kwds={"groups": M.ano.values})
for nome, m in [("EP iid (como no rascunho)", m_iid), ("EP agrupado por ano", m_cl)]:
    lo, hi = np.exp(m.conf_int().loc["elnino"])
    print(f"  {nome:28s}: OR={np.exp(m.params['elnino']):.2f} IC95 {lo:.2f}-{hi:.2f} p={m.pvalues['elnino']:.3f}")
# chuva flexivel: faixas de % do normal + chuva por mes + veranico
M["faixa"] = pd.cut(M.pct, [0, 0.5, 0.7, 0.85, 1.0, 1.15, 1.3, 10], labels=False)
f1 = "quebra ~ C(faixa) + P_fev + P_mar + P_abr + P_mai + veranico_max_fmam + elnino + C(cod)"
m_fx = smf.logit(f1, data=M.dropna(subset=["faixa"])).fit(disp=0, maxiter=500, cov_type="cluster",
                                                          cov_kwds={"groups": M.dropna(subset=["faixa"]).ano.values})
lo, hi = np.exp(m_fx.conf_int().loc["elnino"])
print(f"  chuva flexivel (faixas + meses + veranico), EP por ano: OR={np.exp(m_fx.params['elnino']):.2f} IC95 {lo:.2f}-{hi:.2f} p={m_fx.pvalues['elnino']:.3f}")
print("  jackknife: tira 1 ano El Nino por vez (chuva linear, EP por ano)")
for a in sorted(M[M.elnino == 1].ano.unique()):
    sub = M[M.ano != a]
    m = smf.logit(f0, data=sub).fit(disp=0, maxiter=300, cov_type="cluster", cov_kwds={"groups": sub.ano.values})
    lo, hi = np.exp(m.conf_int().loc["elnino"])
    print(f"    sem {a}: OR={np.exp(m.params['elnino']):.2f} IC95 {lo:.2f}-{hi:.2f}")
fr = M.groupby("ano").agg(q=("quebra", "mean"), en=("elnino", "first"))
print("  fracao de municipios em quebra nos anos El Nino:", fr[fr.en == 1].q.round(2).to_dict())
# bootstrap por ano da diferenca de taxas
anos_en = fr[fr.en == 1].index.values; anos_ou = fr[fr.en == 0].index.values
difs = []
for _ in range(4000):
    a1 = rng.choice(anos_en, len(anos_en)); a0 = rng.choice(anos_ou, len(anos_ou))
    difs.append(M[M.ano.isin(a1)].quebra.mean() - M[M.ano.isin(a0)].quebra.mean())
# (isin com reposicao conta 1 vez cada ano; aproxima por taxa media por ano)
d_ano = []
for _ in range(4000):
    a1 = rng.choice(anos_en, len(anos_en)); a0 = rng.choice(anos_ou, len(anos_ou))
    d_ano.append(fr.loc[a1, "q"].mean() - fr.loc[a0, "q"].mean())
print(f"  diferenca de taxa El Nino - demais (media por ano): {fr[fr.en == 1].q.mean() - fr[fr.en == 0].q.mean():+.3f}; "
      f"IC90 bootstrap por ano [{np.percentile(d_ano, 5):+.3f}, {np.percentile(d_ano, 95):+.3f}]")

# ================================================================ B
print("\n" + "=" * 25, "B. AUC do ONI para a quebra municipal (o que se sabe ANTES do plantio)", "=" * 25)
for col, quando in [("oni_aso", "ASO, conhecido em ~5/nov"), ("oni_ond", "OND, conhecido em ~5/jan"), ("oni_ndj", "NDJ, conhecido em ~5/fev")]:
    sub = M.dropna(subset=[col])
    auc = roc_auc_score(sub.quebra, sub[col])
    bs = []
    anos = sub.ano.unique()
    for _ in range(2000):
        aa = rng.choice(anos, len(anos))
        bb = pd.concat([sub[sub.ano == a] for a in aa])
        if bb.quebra.nunique() == 2:
            bs.append(roc_auc_score(bb.quebra, bb[col]))
    print(f"  ONI {quando:26s}: AUC={auc:.3f} IC90 por ano [{np.percentile(bs, 5):.2f}, {np.percentile(bs, 95):.2f}]")
sub = M.dropna(subset=["oni_ond"])
jan_pct = sub.P_jan / sub.groupby("cod").P_jan.transform("median")
print(f"  chuva de janeiro (% do normal, so dado de chuva, 31/jan): AUC={roc_auc_score(sub.quebra, -jan_pct):.3f}")
z = lambda s: (s - s.mean()) / s.std()
comb = z(sub.oni_ond) - z(jan_pct.clip(upper=3))
print(f"  ONI OND + chuva de janeiro (soma de z, sem ajuste): AUC={roc_auc_score(sub.quebra, comb):.3f}")

# ================================================================ C
print("\n" + "=" * 25, "C. ONI ASO alem da chuva no ESTADO (robustez do -0,208)", "=" * 25)
c = pd.read_parquet(S + "clima_risco_composto_anual.parquet")
pe = pd.read_parquet(D + "ibge_pam_ce_anual.parquet"); pe["ano"] = pe.data.dt.year
rend = pe[pe.variavel == "rendimento_kg_ha"].pivot_table(index="ano", columns="produto", values="valor")
k = [x for x in rend.columns if str(x).startswith("Milho")][0]
an9 = np.log(rend[k] / rend[k].rolling(9, center=True, min_periods=5).median())
v = rend[k].dropna()
an_out = pd.Series([np.log(v.iloc[i] / np.median(np.delete(v.values, i))) for i in range(len(v))], index=v.index)
pw = pd.read_parquet(D + "power_ce_mensal.parquet")
pr = pw[pw.variavel == "PRECTOTCORR"].set_index("data")["valor"]
pr = pr * pr.index.days_in_month  # mm/dia -> mm/mes
mens = pd.DataFrame({f"m{m}": pr[pr.index.month == m].groupby(pr[pr.index.month == m].index.year).sum() for m in (1, 2, 3, 4, 5)})
df = c.join(an9.rename("an9")).join(an_out.rename("an_out")).join(mens)
df = df[(df.index >= 1982) & (df.index <= 2025)].dropna(subset=["an9", "chuva_fmam", "ONI_ASO"])
zc = z(df.chuva_fmam)


def ajusta(y, X, nome):
    m = sm.OLS(y, sm.add_constant(X)).fit(cov_type="HC1")
    print(f"  {nome:58s}: coef ONI_ASO={m.params['ONI_ASO']:+.3f} (p={m.pvalues['ONI_ASO']:.3f}) R2={m.rsquared:.2f} n={int(m.nobs)}")
    return m


ajusta(df.an9, pd.DataFrame({"chuva": zc, "ONI_ASO": df.ONI_ASO}), "replica: chuva linear (alvo mediana movel 9a)")
ajusta(df.an_out, pd.DataFrame({"chuva": zc, "ONI_ASO": df.ONI_ASO}), "alvo canonico (mediana dos outros anos)")
ajusta(df.an9, pd.DataFrame({"chuva": zc, "chuva2": zc ** 2, "ONI_ASO": df.ONI_ASO}), "chuva + chuva^2")
ajusta(df.an9, pd.DataFrame({"lchuva": np.log(df.chuva_fmam), "ONI_ASO": df.ONI_ASO}), "log(chuva)")
ajusta(df.an9, pd.DataFrame({**{f"m{m}": z(df[f"m{m}"]) for m in (2, 3, 4, 5)}, "ONI_ASO": df.ONI_ASO}), "chuva por mes (fev, mar, abr, mai)")
ajusta(df.an9, pd.DataFrame({**{f"m{m}": z(df[f"m{m}"]) for m in (2, 3, 4, 5)}, "ver": z(df.maior_veranico),
                             "tmax": z(df.anom_tmax_fmam), "ONI_ASO": df.ONI_ASO}), "chuva por mes + veranico + Tmax")
# chuva de IMERG (1998-2025), media dos municipios
ch = pd.read_parquet(S + "chuva_mun_diaria.parquet"); ch.index = pd.DatetimeIndex(ch.index)
st = ch.mean(axis=1)
im = st[st.index.month.isin([2, 3, 4, 5])].groupby(st[st.index.month.isin([2, 3, 4, 5])].index.year).sum()
dI = df.join(im.rename("imerg")).dropna(subset=["imerg"])
ajusta(dI.an9, pd.DataFrame({"chuva": z(dI.imerg), "ONI_ASO": dI.ONI_ASO}), "chuva IMERG 1998-2025 (linear)")
ajusta(dI.an9, pd.DataFrame({"chuva": z(dI.imerg), "c2": z(dI.imerg) ** 2, "ONI_ASO": dI.ONI_ASO}), "chuva IMERG + quadrado")
for tira in [[1983], [1998], [2016], [1983, 1998, 2016]]:
    s2 = df.drop([a for a in tira if a in df.index])
    ajusta(s2.an9, pd.DataFrame({"chuva": z(s2.chuva_fmam), "ONI_ASO": s2.ONI_ASO}), f"sem {tira}")
print(f"  corr(chuva POWER fmam, ONI ASO) = {df.chuva_fmam.corr(df.ONI_ASO):+.2f}; corr(POWER, IMERG) 1998+ = {dI.chuva_fmam.corr(dI.imerg):+.2f}")

# ================================================================ D
print("\n" + "=" * 25, "D. Analogos: incerteza amostral (Clopper-Pearson 90%)", "=" * 25)
for x, n, rot in [(4, 7, "ASO>=1,3 (rascunho: 4 secos em 7)"), (3, 4, "El Nino que nao decai (3 em 4)"),
                  (3, 6, "ASO>=1,49 (inclui 1973 e 1988, sem 1983/1966?)"), (2, 2, "so os 2 maiores (1998, 2016)")]:
    lo = stats.beta.ppf(0.05, x, n - x + 1) if x > 0 else 0.0
    hi = stats.beta.ppf(0.95, x + 1, n - x) if x < n else 1.0
    print(f"  {rot:48s}: {x}/{n} = {x / n:.2f}  IC90 [{lo:.2f}, {hi:.2f}]  (taxa-base de tercil seco = 0,33)")
aso = oni[oni.index.month == 9]
for lim in [1.0, 1.3, 1.45, 1.49, 1.5, 2.0]:
    anos = sorted((aso[(aso >= lim) & (aso.index.year < 2026)].index.year + 1).tolist())
    print(f"  limiar ASO >= {lim:.2f}: {len(anos)} anos -> {anos}")

# ================================================================ E
print("\n" + "=" * 25, "E. GRACE CE: a queda de ago->set/2026 e incomum?", "=" * 25)
gr = pd.read_parquet(D + "grace_ce_mensal.parquet").sort_values("data")
gr = gr[gr.variavel == "TWS_anomalia"].set_index("data")["valor"]
des = gr - gr.groupby(gr.index.month).transform("mean")
idx = des.index
dm = des.diff()
consec = (idx.to_series().diff().dt.days.between(27, 32)).values
dm1 = dm[consec]
v26 = dm1.get(pd.Timestamp("2026-09-01"), np.nan)
print(f"  variacao mes a mes dessazonalizada: dp={dm1.std():.2f} cm, n={dm1.notna().sum()}; ago->set/2026 = {v26:+.2f} cm "
      f"(z={v26 / dm1.std():+.1f}; percentil {100 * (dm1 < v26).mean():.0f})")
setembros = dm1[dm1.index.month == 9]
print(f"  so ago->set de todos os anos: media {setembros.mean():+.2f}, dp {setembros.std():.2f}, min {setembros.min():+.2f} ({setembros.idxmin().year})")
print(f"  ultimos meses (cm): {des.tail(6).round(2).to_dict()}")

# ================================================================ F
print("\n" + "=" * 25, "F. Milho x feijao: quanto da correlacao e o choque comum do ano?", "=" * 25)
fe["cod"] = fe.cod_local.astype(str).str[:7]
J = mi[["cod", "ano", "razao"]].merge(fe[["cod", "ano", "razao"]], on=["cod", "ano"], suffixes=("_m", "_f"))
J = J[(J.razao_m > 0) & (J.razao_f > 0)]
J["lm"], J["lf"] = np.log(J.razao_m), np.log(J.razao_f)
J["lm_r"] = J.lm - J.groupby("ano").lm.transform("mean")
J["lf_r"] = J.lf - J.groupby("ano").lf.transform("mean")
r_raw = J.groupby("cod").apply(lambda g: g.lm.corr(g.lf) if len(g) >= 10 else np.nan).median()
r_res = J.groupby("cod").apply(lambda g: g.lm_r.corr(g.lf_r) if len(g) >= 10 else np.nan).median()
print(f"  correlacao mediana por municipio: bruta {r_raw:.2f} | depois de tirar a media do estado no ano {r_res:.2f}")

# ================================================================ G
print("\n" + "=" * 25, "G. 30/abr e previsao ou quase o resultado? AUC por janela de chuva (municipal, % do normal)", "=" * 25)
for cols, rot in [(["P_jan"], "jan"), (["P_jan", "P_fev"], "jan-fev"), (["P_jan", "P_fev", "P_mar"], "jan-mar"),
                  (["P_jan", "P_fev", "P_mar", "P_abr"], "jan-abr (= portao 30/abr)"),
                  (["P_jan", "P_fev", "P_mar", "P_abr", "P_mai"], "jan-mai (quadra inteira, a posteriori)")]:
    s = M[cols].sum(axis=1); pct = s / s.groupby(M.cod).transform("median")
    print(f"  chuva {rot:40s}: AUC={roc_auc_score(M.quebra, -pct):.3f}")

# ================================================================ H
print("\n" + "=" * 25, "H. 2012/2016/1998: % do normal acumulado desde 1/jan (media do estado, IMERG)", "=" * 25)
cum = {}
for a in range(1998, 2026):
    s = st[f"{a}-01-01":f"{a}-06-30"]
    cum[a] = {d: s[:f"{a}-{d}"].sum() for d in ["01-31", "02-28", "03-31", "04-30"]}
C = pd.DataFrame(cum).T
N = C.median()
for a in [1998, 2012, 2016, 2024]:
    print(f"  {a}: " + " | ".join(f"ate {d}: {100 * C.loc[a, d] / N[d]:.0f}%" for d in C.columns))
