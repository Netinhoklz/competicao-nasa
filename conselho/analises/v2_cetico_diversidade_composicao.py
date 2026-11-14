"""Cetico, rodada 2: o efeito de diversidade (+6,6 p.p. de rendimento do portfolio na seca 2012-16) e causal, ou e
composicao (municipios diversos tem menos milho/feijao, que sao as culturas que mais caem)?

Receita do portfolio copiada de pesquisa/analise_diversidade_resiliencia.py (R1 = media, ponderada pela area-base, da
razao de rendimento 2012-16 / 2004-11 de cada lavoura temporaria, cortada em [0, 3]).
Testes:
1. Contrafactual de COMPOSICAO: R1_comp = mesma ponderacao de area do municipio, mas com a razao MEDIANA DO ESTADO de
   cada cultura (logo, so a mistura de culturas, sem nada local). Quanto do efeito some ao controlar R1_comp?
2. Efeito DENTRO da cultura: painel municipio x cultura, razao ~ diversidade + EF de cultura + chuva + relevo + EF de
   mesorregiao, erro agrupado por municipio. Se a diversidade ajuda "por si", cada cultura cai menos no municipio diverso.
3. Relato copiado: peso do portfolio em series planas (rendimento identico em >= 50% dos anos 2004-16) e R1 sem elas.
4. Autocorrelacao espacial do residuo (I de Moran, 6 vizinhos, permutacao): o n efetivo e menor que 184.
So le arquivos; nao escreve nada.
"""
import json
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
import statsmodels.api as sm

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
rng = np.random.default_rng(0)
P = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/pesquisa/"
div = pd.read_csv(P + "analise_diversidade_resiliencia.saida.csv", dtype={"cod": str}).set_index("cod")
BASE, SECA = range(2004, 2012), range(2012, 2017)

p = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
tp = p[(p.area_colhida_ha > 0) & (p.rendimento_kg_ha > 0)].copy()
tp["cod"] = tp.cod_local.astype(str)
rb = tp[tp.ano.isin(BASE)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
rs = tp[tp.ano.isin(SECA)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
ab = tp[tp.ano.isin(BASE) & (tp.tipo == "temporaria")].groupby(["cod", "produto"]).area_plantada_ha.mean()
razao = (rs / rb).dropna().clip(0, 3)
j = pd.concat([razao.rename("r"), ab.rename("a")], axis=1).dropna().reset_index()
R1 = j.groupby("cod").apply(lambda g: np.average(g.r, weights=g.a))
print(f"R1 recalculado bate com o arquivo: max |dif| = {(R1.reindex(div.index) - div.R1_rend_rel_portfolio).abs().max():.5f}")

# composicao: razao mediana do estado por cultura
med_est = j.groupby("produto").r.median()
j["r_est"] = j.produto.map(med_est)
R1c = j.groupby("cod").apply(lambda g: np.average(g.r_est, weights=g.a))
peso = j.assign(w=j.a / j.groupby("cod").a.transform("sum"))
top = peso.groupby("produto").w.mean().sort_values(ascending=False).head(8)
print("\nRazao mediana do estado (seca/base) das culturas de maior peso medio no portfolio:")
print(pd.DataFrame({"peso_medio": top, "razao_mediana_estado": med_est[top.index]}).round(3).to_string())

nomes = json.loads((DADOS / "referencia" / "ceara_municipios_nomes.json").read_text(encoding="utf-8"))
d = div.copy()
d["R1"] = R1
d["R1_comp"] = R1c
d["log_area"] = np.log(d.area_plantada_media_ha)
d = d.dropna(subset=["R1", "R1_comp", "elev_media"])


def ols(y, cols, dd, fe=True, rotulo=""):
    X = dd[cols].copy()
    Xz = (X - X.mean()) / X.std()
    parts = [Xz]
    if fe:
        parts.append(pd.get_dummies(dd.meso, drop_first=True, dtype=float))
    m = sm.OLS(dd[y], sm.add_constant(pd.concat(parts, axis=1))).fit(cov_type="HC3")
    q1, q3 = dd.n_efetivo_culturas.quantile([0.25, 0.75])
    ef = m.params["n_efetivo_culturas"] / X.n_efetivo_culturas.std() * (q3 - q1) if "n_efetivo_culturas" in cols else np.nan
    print(f"   {rotulo:58s} Q1->Q3 diversidade = {ef * 100:+5.1f} p.p. (p = {m.pvalues.get('n_efetivo_culturas', np.nan):.3f}); "
          f"R2 = {m.rsquared:.3f}" + (f"; beta_pad R1_comp = {m.params['R1_comp']:+.3f} (p = {m.pvalues['R1_comp']:.3f})" if "R1_comp" in cols else ""))
    return m


ctrl = ["anom_chuva_seca", "chuva_clim_mm", "elev_media", "decl_media_graus", "log_area"]
print(f"\n1. Composicao. corr(diversidade, R1_comp) = {d.n_efetivo_culturas.corr(d.R1_comp):+.2f}; "
      f"corr(R1, R1_comp) = {d.R1.corr(d.R1_comp):+.2f}; corr(frac milho+feijao, R1_comp) = {d.frac_milho_feijao.corr(d.R1_comp):+.2f}")
m0 = ols("R1", ["n_efetivo_culturas"] + ctrl, d, rotulo="R1 ~ div + controles + EF meso (reproduz +6,6)")
m1 = ols("R1", ["n_efetivo_culturas", "R1_comp"] + ctrl, d, rotulo="R1 ~ div + R1_comp + controles + EF meso")
m2 = ols("R1_comp", ["n_efetivo_culturas"] + ctrl, d, rotulo="R1_comp ~ div + controles + EF meso (so mistura)")
d["R1_local"] = d.R1 - d.R1_comp
m3 = ols("R1_local", ["n_efetivo_culturas"] + ctrl, d, rotulo="(R1 - R1_comp) ~ div + controles + EF meso")

# 2. dentro da cultura
print("\n2. Dentro da cultura (painel municipio x cultura, culturas com >= 30 municipios; erro agrupado por municipio)")
jj = j.merge(d[["n_efetivo_culturas", "meso"] + ctrl], left_on="cod", right_index=True)
cont = jj.produto.value_counts()
jj = jj[jj.produto.isin(cont[cont >= 30].index)]
X = jj[["n_efetivo_culturas"] + ctrl]
Xz = (X - X.mean()) / X.std()
XX = sm.add_constant(pd.concat([Xz, pd.get_dummies(jj.produto, drop_first=True, dtype=float),
                                pd.get_dummies(jj.meso, drop_first=True, dtype=float)], axis=1))
for rot, w in [("sem peso", None), ("ponderado pela area-base", jj.a.values)]:
    mod = (sm.WLS(jj.r.values, XX, weights=w) if w is not None else sm.OLS(jj.r.values, XX)).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(jj.cod)[0]})
    q1, q3 = d.n_efetivo_culturas.quantile([0.25, 0.75])
    ef = mod.params["n_efetivo_culturas"] / X.n_efetivo_culturas.std() * (q3 - q1)
    print(f"   {rot:26s}: Q1->Q3 diversidade = {ef * 100:+.1f} p.p. na razao de CADA cultura (p = {mod.pvalues['n_efetivo_culturas']:.3f}); "
          f"n = {len(jj)} pares, {jj.cod.nunique()} municipios, {jj.produto.nunique()} culturas")
for cult in ["Milho", "Feijão", "Mandioca"]:
    g = jj[jj.produto.str.startswith(cult)]
    Xg = g[["n_efetivo_culturas"] + ctrl]
    Xgz = (Xg - Xg.mean()) / Xg.std()
    mg = sm.OLS(g.r.values, sm.add_constant(pd.concat([Xgz, pd.get_dummies(g.meso, drop_first=True, dtype=float)], axis=1))).fit(cov_type="HC3")
    ef = mg.params["n_efetivo_culturas"] / Xg.n_efetivo_culturas.std() * (q3 - q1)
    print(f"      so {cult:9s}: Q1->Q3 = {ef * 100:+.1f} p.p. (p = {mg.pvalues['n_efetivo_culturas']:.3f}, n = {len(g)})")

# 3. relato copiado
print("\n3. Series planas (relato copiado) no portfolio")
tt = tp[tp.ano.isin(list(BASE) + list(SECA))]
plana = tt.groupby(["cod", "produto"]).rendimento_kg_ha.agg(lambda s: s.value_counts().iloc[0] / len(s) if len(s) >= 6 else np.nan)
j["plana"] = j.set_index(["cod", "produto"]).index.map(plana.to_dict()).values
j["plana"] = j.plana >= 0.5
pw = j.groupby("cod").apply(lambda g: g.a[g.plana].sum() / g.a.sum())
print(f"   pares municipio-cultura com rendimento identico em >= 50% dos anos 2004-16: {j.plana.mean():.1%}; "
      f"peso medio dessas series no portfolio: {pw.mean():.1%} (mediana {pw.median():.1%}); "
      f"corr(peso plano, diversidade) = {pw.reindex(d.index).corr(d.n_efetivo_culturas):+.2f}")
print("   culturas com mais series planas:", j[j.plana].produto.value_counts().head(6).to_dict())
jn = j[~j.plana]
d["R1_sem_planas"] = jn.groupby("cod").apply(lambda g: np.average(g.r, weights=g.a))
d["R1c_sem_planas"] = jn.assign(r_est=jn.produto.map(jn.groupby("produto").r.median())).groupby("cod").apply(
    lambda g: np.average(g.r_est, weights=g.a))
dd = d.dropna(subset=["R1_sem_planas"]).copy()
ols("R1_sem_planas", ["n_efetivo_culturas"] + ctrl, dd, rotulo="R1 sem series planas ~ div + controles + EF meso")
dd["R1_comp"] = dd.R1c_sem_planas
ols("R1_sem_planas", ["n_efetivo_culturas", "R1_comp"] + ctrl, dd, rotulo="R1 sem planas ~ div + R1_comp + controles + EF")

# 4. Moran do residuo do modelo principal
mun = municipios_ce_gdf()
mun["cod"] = mun.codarea.astype(str)
c = mun.set_index("cod").geometry.centroid.reindex(d.index)
xy = np.column_stack([c.x.values, c.y.values])
dist = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
np.fill_diagonal(dist, np.inf)
Wn = np.zeros_like(dist)
for i, row in enumerate(np.argsort(dist, axis=1)[:, :6]):
    Wn[i, row] = 1 / 6


def moran(e):
    z = e - e.mean()
    return len(z) / Wn.sum() * (z @ Wn @ z) / (z @ z)


e = m0.resid.values
I0 = moran(e)
perm = np.array([moran(rng.permutation(e)) for _ in range(999)])
print(f"\n4. I de Moran do residuo (modelo com EF de mesorregiao, 6 vizinhos): I = {I0:+.3f}, p perm = {(perm >= I0).mean():.3f}")
I1 = moran(d.R1.values - d.R1.mean())
print(f"   I de Moran do proprio R1: {I1:+.3f} | a seca 2012-16 e UM episodio: o n de 'eventos' e 1, nao 184")
