"""Estrategista, RODADA 2, analise 3: o "+6,6 p.p." da diversidade se reproduz e aguenta um juiz atento?

O numero candidato a gancho cientifico vem de pesquisa/analise_diversidade_resiliencia.py (nao e importado nem rodado
aqui, porque ele reescreve as proprias saidas). Copiamos SO o bloco de rendimento R1 (portfolio de temporarias) e
testamos, com a MESMA especificacao, quatro perguntas de juiz:
  1. Reproducao: R1 ~ diversidade + chuva IMERG + relevo + log area + EF de mesorregiao (HC3) -> sai +6,6 p.p.?
  2. Dependencia espacial: mesmo modelo com erro agrupado por MICRORREGIAO (33 grupos). O protocolo do conselho diz que
     residuos se correlacionam por centenas de km; HC3 trata 184 municipios como independentes.
  3. Composicao: o efeito e "diversidade" ou so "menos milho+feijao"? Mesmo modelo + fracao milho+feijao.
  4. Fora do episodio: mesma especificacao na seca de 1998 (base 1990-1997; chuva IMERG fev-mai 1998 contra 1999-2011)
     e placebo sem seca (2008-11 contra 2004-07). Pre-declarado: nao trocamos a especificacao depois de ver.
So le arquivos.
"""
import json
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, DERIV, municipios_ce_gdf

import numpy as np
import pandas as pd
import shapely
import statsmodels.api as sm
import xarray as xr

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

p = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
p["cod"] = p.cod_local.astype(str)
t = p[(p.tipo == "temporaria") & (p.area_plantada_ha > 0)].copy()


def shannon(g):
    a = g.area_plantada_ha.values
    s = a / a.sum()
    return -(s * np.log(s)).sum()


def montar(base, seca):
    tb = t[t.ano.isin(base)]
    div = np.exp(tb.groupby(["cod", "ano"]).apply(shannon).groupby("cod").mean()).rename("n_efetivo_culturas").to_frame()
    dom = tb.groupby(["cod", "produto"]).area_plantada_ha.sum().unstack(fill_value=0)
    div["frac_milho_feijao"] = (dom.filter(like="Milho").sum(1) + dom.filter(like="Feijão").sum(1)) / dom.sum(1)
    div["area_plantada_media_ha"] = tb.groupby(["cod", "ano"]).area_plantada_ha.sum().groupby("cod").mean()
    tp = p[(p.area_colhida_ha > 0) & (p.rendimento_kg_ha > 0)]
    rb = tp[tp.ano.isin(base)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
    rs = tp[tp.ano.isin(seca)].groupby(["cod", "produto"]).rendimento_kg_ha.mean()
    ab = tp[tp.ano.isin(base) & (tp.tipo == "temporaria")].groupby(["cod", "produto"]).area_plantada_ha.mean()
    j = pd.concat([(rs / rb).dropna().clip(0, 3).rename("r"), ab.rename("a")], axis=1).dropna()
    div["R1"] = j.groupby("cod").apply(lambda g: np.average(g.r, weights=g.a))
    return div


# ---------- chuva IMERG fev-mai por municipio (mesma receita do script original)
mun = municipios_ce_gdf()
mun["cod"] = mun.codarea.astype(str)
arqs = [str(DADOS / "imerg" / f"imerg_ce_diario_{a}.nc") for a in range(1998, 2017)]
ds = xr.open_mfdataset(arqs, combine="by_coords")
var = [v for v in ds.data_vars if ds[v].ndim == 3][0]
fmam = ds[var].where(ds.time.dt.month.isin([2, 3, 4, 5]), drop=True).groupby("time.year").sum("time").load()
latn = "lat" if "lat" in fmam.dims else "latitude"
lonn = "lon" if "lon" in fmam.dims else "longitude"
lo, la = np.meshgrid(fmam[lonn].values, fmam[latn].values)
ch = {}
for _, m in mun.iterrows():
    mask = shapely.contains_xy(m.geometry, lo, la)
    if mask.sum() == 0:
        c = m.geometry.centroid
        ch[m.cod] = fmam.sel({lonn: c.x, latn: c.y}, method="nearest").to_series()
    else:
        ch[m.cod] = fmam.where(xr.DataArray(mask, dims=(latn, lonn), coords={latn: fmam[latn], lonn: fmam[lonn]})).mean(
            (latn, lonn)).to_series()
ch = pd.DataFrame(ch).T

nomes = json.loads((DADOS / "referencia" / "ceara_municipios_nomes.json").read_text(encoding="utf-8"))
meso = pd.Series({str(m["id"]): m["microrregiao"]["mesorregiao"]["nome"] for m in nomes}, name="meso")
micro = pd.Series({str(m["id"]): m["microrregiao"]["nome"] for m in nomes}, name="micro")
srtm = pd.read_parquet(DERIV / "srtm_municipios_ce.parquet").assign(cod=lambda d: d.codarea.astype(str)).set_index("cod")


def ajustar(div, extra=(), cluster=False, rotulo=""):
    d = div.join(meso).join(micro).join(srtm[["elev_media", "decl_media_graus"]]).dropna(subset=["R1", "elev_media"])
    cols = ["n_efetivo_culturas", "anom_chuva_seca", "chuva_clim_mm", "elev_media", "decl_media_graus", *extra]
    X = d[cols].copy()
    X["log_area"] = np.log(d.area_plantada_media_ha)
    Xz = (X - X.mean()) / X.std()
    fe = pd.get_dummies(d.meso, drop_first=True, dtype=float)
    Z = sm.add_constant(pd.concat([Xz, fe], axis=1))
    if cluster:
        g = pd.factorize(d.micro)[0]
        m = sm.OLS(d.R1, Z).fit(cov_type="cluster", cov_kwds={"groups": g})
    else:
        m = sm.OLS(d.R1, Z).fit(cov_type="HC3")
    q1, q3 = d.n_efetivo_culturas.quantile([0.25, 0.75])
    ef = m.params["n_efetivo_culturas"] / X.n_efetivo_culturas.std() * (q3 - q1)
    lo_, hi_ = m.conf_int(alpha=0.10).loc["n_efetivo_culturas"] / X.n_efetivo_culturas.std() * (q3 - q1)
    txt = f"   {rotulo:58s}: Q1->Q3 = {ef * 100:+.1f} p.p. (IC90 {lo_ * 100:+.1f} a {hi_ * 100:+.1f}); p = " \
          f"{m.pvalues['n_efetivo_culturas']:.4f}; n = {int(m.nobs)}"
    if extra:
        txt += f"; coef padronizado de {extra[0]} = {m.params[extra[0]]:+.4f} (p {m.pvalues[extra[0]]:.3f})"
    print(txt)
    return ef


print("=" * 20, "1-3. Seca 2012-2016 (base 2004-2011), mesma especificacao do original", "=" * 20)
div = montar(range(2004, 2012), range(2012, 2017))
div = div.join(pd.DataFrame({"chuva_clim_mm": ch[[a for a in ch.columns if a <= 2011]].mean(1),
                             "anom_chuva_seca": ch[[a for a in ch.columns if 2012 <= a <= 2016]].mean(1)
                             / ch[[a for a in ch.columns if a <= 2011]].mean(1) - 1}), how="inner")
print(f"   R1 medio = {div.R1.mean():.3f}; correlacao diversidade x fracao milho+feijao = "
      f"{div.n_efetivo_culturas.corr(div.frac_milho_feijao):+.2f}")
ajustar(div, rotulo="1. reproducao (HC3)")
ajustar(div, cluster=True, rotulo="2. erro agrupado por microrregiao (33 grupos)")
ajustar(div, extra=("frac_milho_feijao",), rotulo="3. + fracao milho+feijao (HC3)")
ajustar(div, extra=("frac_milho_feijao",), cluster=True, rotulo="3b. + fracao milho+feijao, agrupado por microrregiao")

print("\n" + "=" * 20, "4. Fora do episodio e placebo (mesma especificacao)", "=" * 20)
d98 = montar(range(1990, 1998), [1998])
d98 = d98.join(pd.DataFrame({"chuva_clim_mm": ch[[a for a in ch.columns if 1999 <= a <= 2011]].mean(1),
                             "anom_chuva_seca": ch[1998] / ch[[a for a in ch.columns if 1999 <= a <= 2011]].mean(1) - 1}),
               how="inner")
print(f"   seca de 1998: R1 medio = {d98.R1.mean():.3f}")
ajustar(d98, rotulo="4a. seca de 1998, base 1990-1997 (HC3)")
ajustar(d98, cluster=True, rotulo="4a'. seca de 1998, agrupado por microrregiao")
dpl = montar(range(2004, 2008), range(2008, 2012))
dpl = dpl.join(pd.DataFrame({"chuva_clim_mm": ch[[a for a in ch.columns if a <= 2011]].mean(1),
                             "anom_chuva_seca": ch[[a for a in ch.columns if 2008 <= a <= 2011]].mean(1)
                             / ch[[a for a in ch.columns if 2004 <= a <= 2007]].mean(1) - 1}), how="inner")
print(f"   placebo 2008-11 x 2004-07: R1 medio = {dpl.R1.mean():.3f}")
ajustar(dpl, rotulo="4b. placebo sem seca (HC3)")
ajustar(dpl, cluster=True, rotulo="4b'. placebo sem seca, agrupado por microrregiao")
