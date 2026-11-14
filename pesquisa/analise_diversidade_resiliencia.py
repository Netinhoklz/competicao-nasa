"""Teste com dados do Ceara: diversidade de culturas do municipio x perda de safra na seca de 2012-2016.

Liga o argumento dos artigos-ancora (Bowles 2020; Kluger 2025) aos nossos dados:
- diversidade = Shannon das areas plantadas de lavouras temporarias (media 2004-2011, antes da seca), IBGE PAM;
- perda = 1 - area colhida / area plantada (lavouras temporarias), aumento na seca 2012-2016 vs 2004-2011;
- controle de chuva = anomalia da chuva fev-mai 2012-2016 vs 1998-2011 por municipio (IMERG V07, 0,1 grau).
Saida: pesquisa/analise_diversidade_resiliencia.saida.txt
Observacao: e diversidade de PAISAGEM/portfolio municipal, nao rotacao no talhao.
"""
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402
import statsmodels.api as sm  # noqa: E402
import xarray as xr  # noqa: E402
from scipy import stats  # noqa: E402

from comum import DADOS, DERIV, municipios_ce_gdf  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SAIDA = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\pesquisa\analise_diversidade_resiliencia.saida.txt")
linhas_saida = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    linhas_saida.append(s)


BASE, SECA = range(2004, 2012), range(2012, 2017)

# ---------- PAM: diversidade e perda ----------
p = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
t = p[(p.tipo == "temporaria") & (p.area_plantada_ha > 0)].copy()
t["cod"] = t.cod_local.astype(str)


def shannon(g):
    a = g.area_plantada_ha.values
    s = a / a.sum()
    return -(s * np.log(s)).sum()


div_ano = t[t.ano.isin(BASE)].groupby(["cod", "ano"]).apply(shannon).rename("H")
div = div_ano.groupby("cod").mean().to_frame()
div["n_efetivo_culturas"] = np.exp(div.H)
dom = t[t.ano.isin(BASE)].groupby(["cod", "produto"]).area_plantada_ha.sum().unstack(fill_value=0)
div["frac_milho_feijao"] = (dom.filter(like="Milho").sum(1) + dom.filter(like="Feijão").sum(1)) / dom.sum(1)
div["area_plantada_media_ha"] = t[t.ano.isin(BASE)].groupby(["cod", "ano"]).area_plantada_ha.sum().groupby("cod").mean()


def perda(anos):
    x = t[t.ano.isin(anos)].groupby("cod")[["area_plantada_ha", "area_colhida_ha"]].sum()
    return 1 - x.area_colhida_ha / x.area_plantada_ha


div["perda_base"] = perda(BASE)
div["perda_seca"] = perda(SECA)
div["aumento_perda"] = div.perda_seca - div.perda_base

# ---------- IMERG: chuva fev-mai por municipio ----------
mun = municipios_ce_gdf()
mun["cod"] = mun.codarea.astype(str)
arqs = [DADOS / "imerg" / f"imerg_ce_diario_{a}.nc" for a in range(1998, 2017)]
ds = xr.open_mfdataset([str(a) for a in arqs if a.exists()], combine="by_coords")
var = [v for v in ds.data_vars if ds[v].ndim == 3][0]
fmam = ds[var].where(ds.time.dt.month.isin([2, 3, 4, 5]), drop=True).groupby("time.year").sum("time").load()
latn = "lat" if "lat" in fmam.dims else "latitude"
lonn = "lon" if "lon" in fmam.dims else "longitude"
lo, la = np.meshgrid(fmam[lonn].values, fmam[latn].values)
chuva = {}
for _, m in mun.iterrows():
    mask = shapely.contains_xy(m.geometry, lo, la)
    if mask.sum() == 0:  # municipio menor que o pixel: vizinho mais proximo do centroide
        c = m.geometry.centroid
        sel = fmam.sel({lonn: c.x, latn: c.y}, method="nearest").to_series()
    else:
        sel = fmam.where(xr.DataArray(mask, dims=(latn, lonn), coords={latn: fmam[latn], lonn: fmam[lonn]})).mean((latn, lonn)).to_series()
    chuva[m.cod] = sel
ch = pd.DataFrame(chuva).T
div = div.join(pd.DataFrame({
    "chuva_clim_mm": ch[[a for a in ch.columns if a <= 2011]].mean(1),
    "anom_chuva_seca": ch[[a for a in ch.columns if 2012 <= a <= 2016]].mean(1) / ch[[a for a in ch.columns if a <= 2011]].mean(1) - 1,
}), how="inner").dropna()

out(f"Municípios analisados: {len(div)} (de 184)")
out(div[["n_efetivo_culturas", "frac_milho_feijao", "perda_base", "perda_seca", "aumento_perda", "anom_chuva_seca"]].describe().round(3).to_string())

# ---------- testes ----------
rs, ps = stats.spearmanr(div.n_efetivo_culturas, div.aumento_perda)
out(f"\nSpearman (nº efetivo de culturas × aumento da perda na seca): rho = {rs:+.3f}, p = {ps:.4f}")
rs2, ps2 = stats.spearmanr(div.frac_milho_feijao, div.aumento_perda)
out(f"Spearman (fração milho+feijão × aumento da perda na seca): rho = {rs2:+.3f}, p = {ps2:.4f}")

out("\n>>> A perda por ÁREA (plantada - colhida) é ~0 na maioria dos municípios: após 2000 o IBGE registra a seca como queda de"
    " RENDIMENTO, não de área. A métrica de área é inadequada; os testes válidos estão no bloco de RENDIMENTO abaixo.")
X = div[["n_efetivo_culturas", "anom_chuva_seca", "chuva_clim_mm", "perda_base"]].copy()
X["log_area"] = np.log(div.area_plantada_media_ha)
Xz = (X - X.mean()) / X.std()
mod = sm.OLS(div.aumento_perda, sm.add_constant(Xz)).fit(cov_type="HC3")
out("\nRegressão (variáveis padronizadas, erro robusto HC3): aumento da perda na seca ~ diversidade + chuva + controles")
out(mod.summary2().tables[1].round(4).to_string())
out(f"R² = {mod.rsquared:.3f}, n = {int(mod.nobs)}")

# efeito em unidades: do quartil 1 ao quartil 3 de diversidade
q1, q3 = div.n_efetivo_culturas.quantile([0.25, 0.75])
coef = mod.params["n_efetivo_culturas"] / X.n_efetivo_culturas.std()
out(f"\nEfeito estimado de ir do 1º ao 3º quartil de diversidade ({q1:.2f} → {q3:.2f} culturas efetivas): "
    f"{coef * (q3 - q1) * 100:+.1f} pontos percentuais no aumento da perda de área na seca "
    f"(aumento médio = {div.aumento_perda.mean() * 100:.1f} p.p.)")

# placebo: mesma relação num periodo normal (2004-2007 x 2008-2011)
pl = (perda(range(2008, 2012)) - perda(range(2004, 2008))).reindex(div.index)
rpl, ppl = stats.spearmanr(div.n_efetivo_culturas, pl, nan_policy="omit")
out(f"Placebo (sem seca: 2008–11 vs 2004–07): rho = {rpl:+.3f}, p = {ppl:.4f}")

# ---------- bloco de RENDIMENTO (métrica válida pós-2000) ----------
out("\n================ RENDIMENTO ================")
tp = p[(p.area_colhida_ha > 0) & (p.rendimento_kg_ha > 0)].copy()
tp["cod"] = tp.cod_local.astype(str)
rb = tp[tp.ano.isin(BASE)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
rsec = tp[tp.ano.isin(SECA)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
ab = tp[tp.ano.isin(BASE) & (tp.tipo == "temporaria")].groupby(["cod", "produto"]).area_plantada_ha.mean()
razao = (rsec / rb).dropna().clip(0, 3)
# R1: rendimento relativo do portfólio de temporárias, ponderado pela área-base
j = pd.concat([razao.rename("r"), ab.rename("a")], axis=1).dropna()
div["R1_rend_rel_portfolio"] = j.groupby("cod").apply(lambda g: np.average(g.r, weights=g.a))
# R2: milho sozinho
mil = razao[razao.index.get_level_values("produto").str.startswith("Milho")]
div["R2_rend_rel_milho"] = mil.droplevel("produto").reindex(div.index)
fej = razao[razao.index.get_level_values("produto").str.startswith("Feijão")]
div["R3_rend_rel_feijao"] = fej.droplevel("produto").reindex(div.index)
# diversidade incluindo permanentes (caju etc.)
tall = p[p.ano.isin(BASE) & (p.area_plantada_ha > 0)].copy()
tall["cod"] = tall.cod_local.astype(str)
div["n_efetivo_c_perm"] = np.exp(tall.groupby(["cod", "ano"]).apply(shannon).groupby("cod").mean())

for alvo in ["R1_rend_rel_portfolio", "R2_rend_rel_milho", "R3_rend_rel_feijao"]:
    d = div.dropna(subset=[alvo])
    out(f"\n--- {alvo}: média {d[alvo].mean():.3f} (1 = sem perda), n = {len(d)}")
    for dv in ["n_efetivo_culturas", "n_efetivo_c_perm", "frac_milho_feijao"]:
        r, pv = stats.spearmanr(d[dv], d[alvo])
        out(f"   Spearman {dv:20s} × {alvo}: rho = {r:+.3f}, p = {pv:.4f}")
    for dv in ["n_efetivo_culturas", "n_efetivo_c_perm"]:
        X = d[[dv, "anom_chuva_seca", "chuva_clim_mm"]].copy()
        X["log_area"] = np.log(d.area_plantada_media_ha)
        Xz = (X - X.mean()) / X.std()
        m2 = sm.OLS(d[alvo], sm.add_constant(Xz)).fit(cov_type="HC3")
        b, se, pz = m2.params[dv], m2.bse[dv], m2.pvalues[dv]
        bc = m2.params["anom_chuva_seca"]
        q1, q3 = d[dv].quantile([0.25, 0.75])
        efeito = b / X[dv].std() * (q3 - q1)
        out(f"   OLS {alvo} ~ {dv} + chuva + controles: beta_pad = {b:+.4f} (EP {se:.4f}, p = {pz:.4f}); "
            f"chuva beta_pad = {bc:+.4f}; R² = {m2.rsquared:.3f}; Q1→Q3 de diversidade = {efeito * 100:+.1f} p.p. de rendimento relativo")

# ---------- robustez: efeito fixo de mesorregião + relevo (SRTM) ----------
import json  # noqa: E402

out("\n================ ROBUSTEZ: mesorregião (efeito fixo) + altitude e declividade ================")
nomes = json.loads((DADOS / "referencia" / "ceara_municipios_nomes.json").read_text(encoding="utf-8"))
meso = pd.Series({str(m["id"]): m["microrregiao"]["mesorregiao"]["nome"] for m in nomes}, name="meso")
srtm = pd.read_parquet(DERIV / "srtm_municipios_ce.parquet").assign(cod=lambda d: d.codarea.astype(str)).set_index("cod")
div = div.join(meso).join(srtm[["elev_media", "decl_media_graus"]])
out("municípios por mesorregião: " + ", ".join(f"{k} {v}" for k, v in div.meso.value_counts().items()))
for alvo in ["R1_rend_rel_portfolio", "R2_rend_rel_milho", "R3_rend_rel_feijao"]:
    for dv in ["n_efetivo_culturas", "n_efetivo_c_perm"]:
        d = div.dropna(subset=[alvo, "elev_media"])
        X = d[[dv, "anom_chuva_seca", "chuva_clim_mm", "elev_media", "decl_media_graus"]].copy()
        X["log_area"] = np.log(d.area_plantada_media_ha)
        Xz = (X - X.mean()) / X.std()
        fe = pd.get_dummies(d.meso, drop_first=True, dtype=float)
        m3 = sm.OLS(d[alvo], sm.add_constant(pd.concat([Xz, fe], axis=1))).fit(cov_type="HC3")
        q1, q3 = d[dv].quantile([0.25, 0.75])
        ef = m3.params[dv] / X[dv].std() * (q3 - q1)
        out(f"   {alvo} ~ {dv} + chuva + relevo + EF mesorregião: beta_pad = {m3.params[dv]:+.4f} (EP {m3.bse[dv]:.4f}, "
            f"p = {m3.pvalues[dv]:.4f}); Q1→Q3 = {ef * 100:+.1f} p.p.; R² = {m3.rsquared:.3f}; n = {int(m3.nobs)}")

div.round(5).to_csv(SAIDA.with_suffix(".csv"))
SAIDA.write_text("\n".join(linhas_saida), encoding="utf-8")
