"""Agronomo (rodada 2) - o +6,6 p.p. de diversidade (pesquisa/analise_diversidade_resiliencia.py) sustenta qual estrategia?

Medidas contrarias pre-declaradas (mesma especificacao do teste publicado: OLS HC3, chuva IMERG, relevo, log da area,
efeito fixo de mesorregiao; efeito = Q1 -> Q3 de diversidade em pontos percentuais do rendimento relativo 2012-16/2004-11):
 V0 reproducao do publicado (portfolio de temporarias ponderado pela area-base);
 V1 portfolio SEM mandioca (se o efeito some, a diversidade protege porque inclui o tampao = S2);
 V2 portfolio sem as series municipio-cultura com rendimento repetido (relato copiado) em 2004-2016;
 V3 diversidade calculada SEM a mandioca;
 V4 controle de agua da NASA: anomalia da umidade da zona da raiz do GLDAS-2.1 Noah (fev-mai 2012-16 vs 2000-11);
 V5 o efeito varia com a severidade da seca? (interacao diversidade x anomalia de chuva; Kluger et al. 2025 acham
    beneficio da rotacao que varia com o clima).
Unidade: municipio (n = 184), um unico episodio de seca: e associacao de paisagem, nao rotacao no talhao.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import warnings

import numpy as np
import pandas as pd
import shapely
import statsmodels.api as sm
import xarray as xr
from scipy import stats

warnings.filterwarnings("ignore")
BASE, SECA = range(2004, 2012), range(2012, 2017)
div = pd.read_csv(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/pesquisa/analise_diversidade_resiliencia.saida.csv",
                  dtype={"cod": str}).set_index("cod")
p = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
p["cod"] = p.cod_local.astype(str)
p = p[p.cod.isin(div.index)]
MAND = p.produto.str.startswith("Mandioca")

# ------------------------------------------------------------------ rendimento relativo por cultura (como no publicado)
tp = p[(p.area_colhida_ha > 0) & (p.rendimento_kg_ha > 0)]
rb = tp[tp.ano.isin(BASE)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
rs = tp[tp.ano.isin(SECA)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
ab = tp[tp.ano.isin(BASE) & (tp.tipo == "temporaria")].groupby(["cod", "produto"]).area_plantada_ha.mean()
razao = (rs / rb).dropna().clip(0, 3)
J = pd.concat([razao.rename("r"), ab.rename("a")], axis=1).dropna()
# relato copiado: algum ano 2004-2016 com rendimento identico ao do ano anterior
s = p[p.ano.between(2003, 2016) & (p.rendimento_kg_ha > 0)].sort_values("ano")
rep = s.groupby(["cod", "produto"]).apply(lambda g: bool((g.rendimento_kg_ha.diff() == 0)[g.ano >= 2004].any()))
J["repetido"] = rep.reindex(J.index).fillna(False).values
J["mandioca"] = J.index.get_level_values("produto").str.startswith("Mandioca")
print(f"series municipio-cultura no portfolio: {len(J)}; com rendimento repetido em 2004-2016: {J.repetido.mean():.0%} "
      f"(mandioca {J[J.mandioca].repetido.mean():.0%}, demais {J[~J.mandioca].repetido.mean():.0%})")


def port(m):
    jj = J[m]
    return jj.groupby(level="cod").apply(lambda g: np.average(g.r, weights=g.a))


div["R_V0"] = port(np.ones(len(J), bool))
div["R_V1_sem_mandioca"] = port(~J.mandioca.values)
div["R_V2_sem_repetidos"] = port(~J.repetido.values)
print(f"conferencia: R_V0 igual ao publicado? max |dif| = {(div.R_V0 - div.R1_rend_rel_portfolio).abs().max():.4f}")
# rendimento relativo da propria mandioca e participacao dela
mand_r = J[J.mandioca].r.droplevel("produto")
div["rr_mandioca"] = mand_r.reindex(div.index)
t = p[(p.tipo == "temporaria") & (p.area_plantada_ha > 0) & p.ano.isin(BASE)]
area = t.groupby(["cod", "produto"]).area_plantada_ha.sum().unstack(fill_value=0)
div["frac_mandioca"] = (area.filter(like="Mandioca").sum(1) / area.sum(1)).reindex(div.index)


def shannon(g):
    a = g.area_plantada_ha.values; a = a[a > 0]; s_ = a / a.sum()
    return -(s_ * np.log(s_)).sum()


tsm = t[~t.produto.str.startswith("Mandioca")]
div["n_efetivo_sem_mandioca"] = np.exp(tsm.groupby(["cod", "ano"]).apply(shannon).groupby("cod").mean()).reindex(div.index)
print(f"mandioca na area-base: mediana {div.frac_mandioca.median():.1%}; rendimento relativo da mandioca na seca "
      f"{div.rr_mandioca.median():.2f} contra milho {div.R2_rend_rel_milho.median():.2f} e feijao {div.R3_rend_rel_feijao.median():.2f}; "
      f"Spearman diversidade x fracao de mandioca {stats.spearmanr(div.n_efetivo_culturas, div.frac_mandioca, nan_policy='omit')[0]:+.2f}")

# ------------------------------------------------------------------ GLDAS Noah: anomalia da zona da raiz na seca
g = xr.open_dataset(DADOS / "gldas" / "gldas_noah025_mensal_ne.nc")["RootMoist_inst"].sel(
    lat=slice(-8.2, -2.5), lon=slice(-41.7, -37.0)).load()
fm = g.where(g.time.dt.month.isin([2, 3, 4, 5]), drop=True).groupby("time.year").mean("time")
mun = municipios_ce_gdf(); mun["cod"] = mun.codarea.astype(str)
lo, la = np.meshgrid(fm.lon.values, fm.lat.values)
val = np.isfinite(fm.isel(year=0).values)
an = {}
for _, m in mun.iterrows():
    mk = shapely.contains_xy(m.geometry, lo, la) & val
    if mk.sum() == 0:
        pt = m.geometry.representative_point()
        d = np.where(val, (lo - pt.x) ** 2 + (la - pt.y) ** 2, np.inf)
        mk = d == d.min()
    x = fm.values[:, mk].mean(1)
    yrs = fm.year.values
    an[m.cod] = x[np.isin(yrs, list(SECA))].mean() / x[(yrs >= 2000) & (yrs <= 2011)].mean() - 1
div["anom_rootmoist_gldas"] = pd.Series(an).reindex(div.index)
print(f"GLDAS Noah RootMoist fev-mai 2012-16 vs 2000-11: anomalia mediana {div.anom_rootmoist_gldas.median():+.1%}; "
      f"Spearman com a anomalia de chuva IMERG {stats.spearmanr(div.anom_rootmoist_gldas, div.anom_chuva_seca)[0]:+.2f}")


# ------------------------------------------------------------------ regressoes
def efeito(alvo, dv, agua=("anom_chuva_seca",), inter=None, d=None):
    d = (div if d is None else d).dropna(subset=[alvo, dv, "elev_media", *agua])
    X = d[[dv, *agua, "chuva_clim_mm", "elev_media", "decl_media_graus"]].copy()
    X["log_area"] = np.log(d.area_plantada_media_ha)
    Xz = (X - X.mean()) / X.std()
    if inter:
        Xz["inter"] = Xz[dv] * Xz[inter]
    fe = pd.get_dummies(d.meso, drop_first=True, dtype=float)
    m = sm.OLS(d[alvo], sm.add_constant(pd.concat([Xz, fe], axis=1))).fit(cov_type="HC3")
    q1, q3 = d[dv].quantile([0.25, 0.75])
    ef = m.params[dv] / X[dv].std() * (q3 - q1) * 100
    lo_, hi_ = (m.conf_int(0.10).loc[dv] / X[dv].std() * (q3 - q1) * 100).values
    out = f"Q1->Q3 {ef:+.1f} p.p. (IC90 {lo_:+.1f} a {hi_:+.1f}; p {m.pvalues[dv]:.3f}; n {int(m.nobs)})"
    if inter:
        out += f" | interacao com {inter}: {m.params['inter']:+.4f} (p {m.pvalues['inter']:.3f})"
    return out


print("\n=== Efeito da diversidade (n efetivo de temporarias) no rendimento relativo da seca, com EF de mesorregiao ===")
print(f"  V0 publicado, portfolio:                 {efeito('R_V0', 'n_efetivo_culturas')}")
print(f"  V1 portfolio SEM mandioca:               {efeito('R_V1_sem_mandioca', 'n_efetivo_culturas')}")
print(f"  V2 portfolio sem series repetidas:       {efeito('R_V2_sem_repetidos', 'n_efetivo_culturas')}")
print(f"  V3 diversidade SEM mandioca, portfolio:  {efeito('R_V0', 'n_efetivo_sem_mandioca')}")
print(f"  V3b diversidade e portfolio sem mandioca:{efeito('R_V1_sem_mandioca', 'n_efetivo_sem_mandioca')}")
print(f"  fracao de mandioca no lugar da diversidade (Q1->Q3 da fracao): {efeito('R_V0', 'frac_mandioca')}")
print(f"  V4 controle GLDAS (no lugar do IMERG):   {efeito('R_V0', 'n_efetivo_culturas', agua=('anom_rootmoist_gldas',))}")
print(f"  V4b IMERG + GLDAS:                       {efeito('R_V0', 'n_efetivo_culturas', agua=('anom_chuva_seca', 'anom_rootmoist_gldas'))}")
print(f"  V5 interacao com a seca (IMERG):         {efeito('R_V0', 'n_efetivo_culturas', inter='anom_chuva_seca')}")
print(f"  V5b interacao com a seca (GLDAS):        {efeito('R_V0', 'n_efetivo_culturas', agua=('anom_rootmoist_gldas',), inter='anom_rootmoist_gldas')}")
print("  (interacao negativa = a diversidade ajuda MAIS onde a anomalia foi mais negativa, isto e, onde a seca foi pior)")
print("\n  Culturas sozinhas, com controle IMERG + GLDAS:")
for alvo in ["R2_rend_rel_milho", "R3_rend_rel_feijao", "rr_mandioca"]:
    print(f"   {alvo:20s}: {efeito(alvo, 'n_efetivo_culturas', agua=('anom_chuva_seca', 'anom_rootmoist_gldas'))}")
# metades pela severidade da seca (descritivo)
med = div.anom_chuva_seca.median()
for nome, m in [("seca pior (anomalia abaixo da mediana)", div.anom_chuva_seca <= med), ("seca menor", div.anom_chuva_seca > med)]:
    print(f"  {nome}: {efeito('R_V0', 'n_efetivo_culturas', d=div[m])}")

# ------------------------------------------------------------------ V6: so culturas de sequeiro (lista fixada antes de rodar)
SEQ = ("Milho (em gr", "Feij", "Fava", "Mandioca", "Mamona", "Sorgo", "Algodão herbáceo", "Amendoim", "Gergelim", "Girassol")
prod = J.index.get_level_values("produto")
eh_seq = np.array([any(x.startswith(s_) for s_ in SEQ) for x in prod])
div["R_V6_sequeiro"] = port(eh_seq)
area_seq = area[[c for c in area.columns if any(c.startswith(s_) for s_ in SEQ)]]
div["frac_area_sequeiro"] = (area_seq.sum(1) / area.sum(1)).reindex(div.index)
tseq = t[t.produto.apply(lambda x: any(x.startswith(s_) for s_ in SEQ))]
div["n_efetivo_sequeiro"] = np.exp(tseq.groupby(["cod", "ano"]).apply(shannon).groupby("cod").mean()).reindex(div.index)
print("\n=== V6. So culturas de sequeiro (sem cana, arroz, hortalicas e frutas de ciclo curto) ===")
print(f"  area-base que e sequeiro: mediana {div.frac_area_sequeiro.median():.1%} (p10 {div.frac_area_sequeiro.quantile(.1):.1%}); "
      f"Spearman diversidade x fracao NAO sequeiro {stats.spearmanr(div.n_efetivo_culturas, 1 - div.frac_area_sequeiro)[0]:+.2f}")
print(f"  portfolio de sequeiro, diversidade de todas:      {efeito('R_V6_sequeiro', 'n_efetivo_culturas')}")
print(f"  portfolio de sequeiro, diversidade de sequeiro:   {efeito('R_V6_sequeiro', 'n_efetivo_sequeiro')}")
print(f"  portfolio total, controlando a fracao nao sequeiro: {efeito('R_V0', 'n_efetivo_culturas', agua=('anom_chuva_seca', 'frac_area_sequeiro'))}")
print(f"  portfolio de sequeiro sem series repetidas:       "
      f"{efeito('R_V6b', 'n_efetivo_sequeiro', d=div.assign(R_V6b=port(eh_seq & ~J.repetido.values)))}")
