"""v4 - Entomologo: o bicudo e a continuidade do hospedeiro no tempo e no espaco (IBGE PAM Ceara 1974-2025).

Pergunta: na chegada do bicudo (NE em 1983, Azambuja & Degrande 2014, p. 378), os municipios do Ceara em que o algodao
era (a) mais PERENE (arboreo/moco = hospedeiro o ano todo, sem vazio possivel) e (b) mais DENSO na paisagem (proprio e
vizinhos, modelo de gravidade como Xing et al. 2020) perderam mais rendimento de algodao herbaceo, descontada a chuva
(rendimento do feijao do mesmo municipio como controle)?

Desenho (ecologico, municipio = unidade):
  pre  = 1974-1982 (antes do bicudo no NE)
  pos  = 1986-1992 (bicudo estabelecido; arboreo ja caiu 48% em 1985, Azambuja p. 379)
  Y    = dlog(rend. herbaceo) - dlog(rend. feijao)   [dif-em-dif dentro do municipio]
  X1   = fracao perene = arboreo / (arboreo + herbaceo), area colhida media do pre
  X2   = densidade propria = area de algodao (arb + herb) / area do municipio
  X3   = densidade dos vizinhos, sum_j dens_j * exp(-d_ij / L), L = 10, 25, 75 km (escala de dispersao)
Tambem: (B) continuidade do hospedeiro da lagarta (milho + sorgo) no PAM, 1990-2025.
Limites: correlacao ecologica; precos, credito e ATER mudaram juntos; o PAM do moco e estimativa municipal.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403
from comum import DERIV, municipios_ce_gdf

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod_local"] = pam["cod_local"].astype(str)


def serie(prefixo, col):
    d = pam[pam["produto"].str.startswith(prefixo)]
    return d.pivot_table(index="cod_local", columns="ano", values=col, aggfunc="sum")


arb_a = serie("Algodão arbóreo", "area_colhida_ha")
her_a = serie("Algodão herbáceo", "area_colhida_ha")
her_r = serie("Algodão herbáceo", "rendimento_kg_ha")
arb_r = serie("Algodão arbóreo", "rendimento_kg_ha")
fei_r = serie("Feijão", "rendimento_kg_ha")
mil_r = serie("Milho", "rendimento_kg_ha")

PRE = list(range(1974, 1983))
POS = list(range(1986, 1993))


def media(df, anos, minimo):
    sub = df.reindex(columns=anos)
    sub = sub.where(sub > 0)
    n = sub.notna().sum(axis=1)
    return sub.mean(axis=1).where(n >= minimo)


# geometria: area e centroide em projecao metrica (SIRGAS 2000 / Brazil Polyconic, EPSG:5880)
g = municipios_ce_gdf().to_crs(5880)
g["cod_local"] = g["codarea"].astype(str)
g["area_km2"] = g.geometry.area / 1e6
cen = g.geometry.centroid
g["x"], g["y"] = cen.x / 1000, cen.y / 1000
g = g.set_index("cod_local")[["area_km2", "x", "y"]]

df = pd.DataFrame(index=g.index)
df["arb_pre"] = arb_a.reindex(columns=PRE).fillna(0).mean(axis=1).reindex(df.index)
df["her_pre"] = her_a.reindex(columns=PRE).fillna(0).mean(axis=1).reindex(df.index)
df["alg_pre"] = df["arb_pre"] + df["her_pre"]
df["perene"] = df["arb_pre"] / df["alg_pre"].replace(0, np.nan)
df["dens"] = df["alg_pre"] / (g["area_km2"] * 100)  # fracao da area do municipio (ha / ha)
df["rh_pre"], df["rh_pos"] = media(her_r, PRE, 4), media(her_r, POS, 3)
df["ra_pre"], df["ra_pos"] = media(arb_r, PRE, 4), media(arb_r, POS, 3)
df["rf_pre"], df["rf_pos"] = media(fei_r, PRE, 4), media(fei_r, POS, 3)
df["rm_pre"], df["rm_pos"] = media(mil_r, PRE, 4), media(mil_r, POS, 3)
df["Y_her"] = np.log(df.rh_pos / df.rh_pre) - np.log(df.rf_pos / df.rf_pre)
df["Y_her_milho"] = np.log(df.rh_pos / df.rh_pre) - np.log(df.rm_pos / df.rm_pre)
df["Y_arb"] = np.log(df.ra_pos / df.ra_pre) - np.log(df.rf_pos / df.rf_pre)
df["dlog_area"] = np.log((arb_a.reindex(columns=POS).fillna(0).mean(axis=1) + her_a.reindex(columns=POS).fillna(0)
                          .mean(axis=1)).reindex(df.index) + 1) - np.log(df["alg_pre"] + 1)

# densidade dos vizinhos (gravidade com nucleo exponencial; exclui o proprio municipio)
xy = g[["x", "y"]].to_numpy()
D = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
dens = df["dens"].fillna(0).to_numpy()
for L in (10, 25, 75):
    W = np.exp(-D / L)
    np.fill_diagonal(W, 0)
    df[f"viz_{L}km"] = (W @ dens) / W.sum(1)

print("== A. Chegada do bicudo x continuidade do hospedeiro (CE, municipios) ==")
print(f"  pre = {PRE[0]}-{PRE[-1]}, pos = {POS[0]}-{POS[-1]}; Y = dlog(rend. algodao herbaceo) - dlog(rend. feijao)")
ok = df.dropna(subset=["Y_her", "perene", "dens"])
print(f"  municipios com rendimento de herbaceo e feijao nos dois periodos: {len(ok)} de {len(df)}")
print(f"  mediana dos rendimentos: herbaceo pre {ok.rh_pre.median():.0f} -> pos {ok.rh_pos.median():.0f} kg/ha; "
      f"feijao pre {ok.rf_pre.median():.0f} -> pos {ok.rf_pos.median():.0f} kg/ha")
print(f"  Y mediano = {ok.Y_her.median():+.3f} (exp = {np.exp(ok.Y_her.median()):.2f}x do feijao)")
print(f"  fracao perene (arboreo) pre: mediana {ok.perene.median():.2f} (p10 {ok.perene.quantile(.1):.2f}, "
      f"p90 {ok.perene.quantile(.9):.2f}); densidade propria mediana {ok.dens.median()*100:.1f}% da area")

print("\n  Spearman (n, rho, p):")
for y in ["Y_her", "Y_her_milho", "Y_arb", "dlog_area"]:
    for x in ["perene", "dens", "viz_10km", "viz_25km", "viz_75km"]:
        s = df[[x, y]].dropna()
        if len(s) < 20:
            continue
        r, p = stats.spearmanr(s[x], s[y])
        print(f"    {y:12s} x {x:9s}: n={len(s):3d} rho={r:+.3f} p={p:.3f}")

print("\n  OLS Y_her ~ z(perene) + z(dens) + z(viz_L) + z(rend. herbaceo pre) [EP HC3]:")
for L in (10, 25, 75):
    s = df.dropna(subset=["Y_her", "perene", "dens", f"viz_{L}km", "rh_pre"]).copy()
    X = s[["perene", "dens", f"viz_{L}km"]].copy()
    X["log_rh_pre"] = np.log(s["rh_pre"])
    X = (X - X.mean()) / X.std()
    m = sm.OLS(s["Y_her"], sm.add_constant(X)).fit(cov_type="HC3")
    linhas = "; ".join(f"{k} {m.params[k]:+.3f} (IC95 {m.conf_int().loc[k, 0]:+.3f} a {m.conf_int().loc[k, 1]:+.3f})"
                       for k in X.columns)
    print(f"    L={L:2d} km, n={int(m.nobs)}, R2={m.rsquared:.2f}: {linhas}")

# area: so municipios que ja existiam no PAM de 1974 e tinham >= 50 ha de algodao no pre
# (municipios criados depois tem pre = 0 por construcao e dariam correlacao artificial)
exist74 = set(pam.loc[(pam.ano == 1974) & pam.area_colhida_ha.notna(), "cod_local"])
sa = df[df.index.isin(exist74) & (df.alg_pre >= 50)].dropna(subset=["dlog_area"]).copy()
print(f"\n  Area (so municipios existentes em 1974 com >= 50 ha de algodao no pre): n={len(sa)}; "
      f"area pos/pre mediana {np.exp(sa.dlog_area.median()):.2f}")
rk = sa[["dlog_area", "perene", "dens", "viz_10km", "viz_25km", "viz_75km"]].rank()
for x in ["perene", "dens", "viz_10km", "viz_25km", "viz_75km"]:
    r, p = stats.spearmanr(sa[x], sa["dlog_area"])
    print(f"    dlog_area x {x:9s}: rho={r:+.3f} p={p:.3f}")
for x in ["viz_10km", "viz_25km", "viz_75km", "perene"]:
    # correlacao parcial de postos controlando a densidade propria
    ctrl = sm.add_constant(rk[["dens"]])
    e1 = sm.OLS(rk["dlog_area"], ctrl).fit().resid
    e2 = sm.OLS(rk[x], ctrl).fit().resid
    r, p = stats.pearsonr(e1, e2)
    print(f"    parcial (controle: densidade propria) dlog_area x {x:9s}: rho={r:+.3f} p={p:.3f}")

# placebo de regressao a media: a mesma conta para culturas sem bicudo (feijao, mandioca, milho)
for nome in ["Feijão", "Mandioca", "Milho"]:
    a = serie(nome, "area_colhida_ha")
    pre_c = a.reindex(columns=PRE).fillna(0).mean(axis=1).reindex(df.index)
    pos_c = a.reindex(columns=POS).fillna(0).mean(axis=1).reindex(df.index)
    sp = pd.DataFrame({"d": np.log(pos_c + 1) - np.log(pre_c + 1), "dens": pre_c / (g["area_km2"] * 100)})
    sp = sp[sp.index.isin(exist74) & (pre_c >= 50)].dropna()
    r, p = stats.spearmanr(sp["dens"], sp["d"])
    print(f"    placebo {nome:8s}: n={len(sp)} area pos/pre mediana {np.exp(sp.d.median()):.2f}; "
          f"dlog_area x densidade propria rho={r:+.3f} p={p:.3f}")

# tercis de perene: efeito em escala natural
ok = ok.copy()
ok["terc"] = pd.qcut(ok.perene, 3, labels=["perene baixo", "perene medio", "perene alto"])
t = ok.groupby("terc", observed=True).agg(n=("Y_her", "size"), perene=("perene", "median"), Y=("Y_her", "median"),
                                         rh_pre=("rh_pre", "median"), rh_pos=("rh_pos", "median"))
t["razao_vs_feijao"] = np.exp(t["Y"])
print("\n  Por tercil da fracao perene (medianas):")
print(t.round(3).to_string())

# sensibilidade: outro pos
POS2 = list(range(1987, 1996))
df["Y_her2"] = (np.log(media(her_r, POS2, 3) / df.rh_pre) - np.log(media(fei_r, POS2, 3) / df.rf_pre))
s = df[["perene", "Y_her2"]].dropna()
r, p = stats.spearmanr(s.perene, s.Y_her2)
print(f"\n  Sensibilidade pos = 1987-1995: Y_her2 x perene: n={len(s)} rho={r:+.3f} p={p:.3f}")
# placebo: antes do bicudo (1974-1977 vs 1979-1982)
PA, PB = list(range(1974, 1978)), list(range(1979, 1983))
df["Y_plac"] = (np.log(media(her_r, PB, 2) / media(her_r, PA, 2)) - np.log(media(fei_r, PB, 2) / media(fei_r, PA, 2)))
s = df[["perene", "Y_plac"]].dropna()
r, p = stats.spearmanr(s.perene, s.Y_plac)
print(f"  Placebo sem bicudo (1979-82 vs 1974-77): Y x perene: n={len(s)} rho={r:+.3f} p={p:.3f}")

print("\n== B. Hospedeiro da lagarta-do-cartucho (milho + sorgo) no PAM do CE ==")
mil_a = serie("Milho", "area_colhida_ha")
sor_a = serie("Sorgo", "area_colhida_ha")
fei_a = serie("Feijão", "area_colhida_ha")
man_a = serie("Mandioca", "area_colhida_ha")
anos = list(range(1990, 2026))
gram = mil_a.reindex(columns=anos).fillna(0).add(sor_a.reindex(columns=anos).fillna(0), fill_value=0)
naog = fei_a.reindex(columns=anos).fillna(0).add(man_a.reindex(columns=anos).fillna(0), fill_value=0)
gram = gram.reindex(df.index).fillna(0)
naog = naog.reindex(df.index).fillna(0)
pres = (gram > 0)
print(f"  municipio-anos 1990-2025 com milho ou sorgo colhido > 0: {pres.values.mean()*100:.1f}% "
      f"({pres.values.sum()} de {pres.size})")
anos_todos = (pres.sum(axis=1) == len(anos)).sum()
print(f"  municipios com gramínea hospedeira em TODOS os {len(anos)} anos: {anos_todos} de {len(df)}")
frac = (gram / (gram + naog).replace(0, np.nan))
print(f"  fracao gramínea / (gramínea + feijao + mandioca), mediana por ano 1990-2025: "
      f"{frac.median(axis=0).median():.2f} (min {frac.median(axis=0).min():.2f}, max {frac.median(axis=0).max():.2f})")
print(f"  municipio-anos com fracao gramínea > 0,407 (limiar de percolacao, 8 vizinhos, secao 16): "
      f"{(frac > 0.407).values.sum() / frac.notna().values.sum() * 100:.1f}%")
dens_g = gram.div(g["area_km2"] * 100, axis=0)
print(f"  milho+sorgo como fracao da AREA do municipio, mediana 2015-2025: "
      f"{dens_g.reindex(columns=range(2015, 2026)).median(axis=1).median()*100:.1f}% "
      f"(p90 {dens_g.reindex(columns=range(2015, 2026)).median(axis=1).quantile(.9)*100:.1f}%)")
