"""Cetico - Rodada 3, parte 2.

A. Teste JUSTO de Sao Jose: a profecia fala do RESTO da quadra. Chuva no dia 19/mar (e em 18-20/mar) e chuva acumulada
   ate 19/mar preveem a chuva de 20/mar a 31/mai? (municipal e estadual). O acumulado "diz" porque preve o resto ou
   porque ja e parte do total?
B. 2012 no portao de 30/abr: quantas quebras canonicas o alerta "< 75% do normal desde 1/jan" pega (recall)?
C. Mandioca: municipios com rendimento repetido (relato copiado) tem variancia menor? (o "amortecedor" e dado?)
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
D = "E:/campeonato-nasa/dados/derivados/"
S = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas/"

ch = pd.read_parquet(S + "chuva_mun_diaria.parquet"); ch.index = pd.DatetimeIndex(ch.index)
L = []
for a in range(1998, 2026):
    dia = ch.loc[f"{a}-03-19"]
    jan = ch.loc[f"{a}-03-18":f"{a}-03-20"].sum()
    ate = ch.loc[f"{a}-01-01":f"{a}-03-19"].sum()
    resto = ch.loc[f"{a}-03-20":f"{a}-05-31"].sum()
    tot = ch.loc[f"{a}-02-01":f"{a}-05-31"].sum()
    L.append(pd.DataFrame({"ano": a, "cod": ch.columns.astype(str), "dia19": dia.values, "j3": jan.values,
                           "ate19": ate.values, "resto": resto.values, "fmam": tot.values}))
X = pd.concat(L, ignore_index=True)
for c in ["ate19", "resto", "fmam"]:
    X[c + "_pct"] = X[c] / X.groupby("cod")[c].transform("median")
print("=" * 20, "A. Sao Jose: preve o RESTO da quadra (20/mar-31/mai)?", "=" * 20)
for pred in ["dia19", "j3", "ate19"]:
    r_m = stats.spearmanr(X[pred], X.resto_pct).statistic
    E = X.groupby("ano")[[pred, "resto"]].mean()
    r_e, p_e = stats.spearmanr(E[pred], E.resto)
    print(f"  {pred:6s} x chuva restante: rho municipal (pooled) {r_m:+.2f} | rho estadual {r_e:+.2f} (p={p_e:.2f}, n={len(E)})")
E = X.groupby("ano")[["ate19", "resto", "fmam"]].sum()
print(f"  fracao da chuva fev-mai que ja caiu ate 19/mar (mediana dos anos): {(X.groupby('ano').apply(lambda g: (g.ate19.clip(upper=None) - 0).sum()) / E.fmam).median():.2f} (inclui jan no numerador)")
# quebra canonica do milho
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
p = pam[pam.produto.str.startswith("Milho (em gr") & pam.ano.between(1998, 2025) & (pam.area_plantada_ha >= 50)].copy()
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha
p["ref"] = p.groupby("cod_local").r.transform(lambda v: pd.Series([np.median(np.delete(v.values, i)) for i in range(len(v))], index=v.index))
p["quebra"] = (p.r < 0.5 * p.ref).astype(int)
p["cod"] = p.cod_local.astype(str).str[:7]
Q = X.merge(p[["cod", "ano", "quebra"]], on=["cod", "ano"])
for pred, sinal in [("dia19", -1), ("j3", -1), ("ate19_pct", -1), ("resto_pct", -1)]:
    print(f"  AUC quebra milho com {pred:10s}: {roc_auc_score(Q.quebra, sinal * Q[pred]):.3f}")

print("\n" + "=" * 20, "B. 2012 e 2016 no portao de 30/abr (alerta: jan-abr < 75% do normal do municipio)", "=" * 20)
A = []
for a in range(1998, 2026):
    s = ch.loc[f"{a}-01-01":f"{a}-04-30"].sum()
    A.append(pd.DataFrame({"ano": a, "cod": ch.columns.astype(str), "ja": s.values}))
A = pd.concat(A, ignore_index=True)
A["pct"] = A.ja / A.groupby("cod").ja.transform("median")
A["alerta"] = (A.pct < 0.75).astype(int)
B = A.merge(p[["cod", "ano", "quebra"]], on=["cod", "ano"])
for a in [1998, 2012, 2016, 2024]:
    b = B[B.ano == a]
    q = b.quebra.sum(); al = b.alerta.sum(); hit = (b.alerta & b.quebra).sum()
    print(f"  {a}: quebras={q}, alertas={al}, acertos={hit}, recall={hit / max(q, 1):.0%}, precisao={hit / max(al, 1):.0%}")
tot_q = B.quebra.sum(); tot_hit = (B.alerta & B.quebra).sum()
print(f"  todos os anos: recall {tot_hit / tot_q:.0%}; precisao {tot_hit / B.alerta.sum():.0%}; taxa-base {B.quebra.mean():.1%}")

print("\n" + "=" * 20, "C. Mandioca: relato repetido x variancia", "=" * 20)
m = pam[pam.produto.str.startswith("Mandioca") & pam.ano.between(1998, 2025) & (pam.area_plantada_ha >= 50)].copy()
m = m.sort_values(["cod_local", "ano"])
m["r"] = m.producao_t / m.area_plantada_ha
m["rend_of"] = m.producao_t / m.area_colhida_ha.replace(0, np.nan) if "area_colhida_ha" in m.columns else m.r
m["rep"] = m.groupby("cod_local").rend_of.diff().abs() < 1e-9
g = m.groupby("cod_local").agg(n=("r", "size"), frac_rep=("rep", "mean"),
                               cv=("r", lambda v: np.std(np.log(v[v > 0])) if (v > 0).sum() > 5 else np.nan))
g = g[g.n >= 15].dropna()
r, pv = stats.spearmanr(g.frac_rep, g.cv)
print(f"  municipios com >= 15 anos: {len(g)}; fracao mediana de anos repetidos {g.frac_rep.median():.2f}; "
      f"com >= 1 repeticao: {(g.frac_rep > 0).mean():.0%}")
print(f"  rho(fracao repetida, dp do log-rendimento) = {r:+.2f} (p={pv:.3f})")
print(f"  dp mediano do log-rendimento: sem repeticao {g[g.frac_rep == 0].cv.median():.2f} (n={(g.frac_rep == 0).sum()}) | "
      f"com >= 10% repetido {g[g.frac_rep >= 0.10].cv.median():.2f} (n={(g.frac_rep >= 0.10).sum()})")
mi = pam[pam.produto.str.startswith("Milho (em gr") & pam.ano.between(1998, 2025) & (pam.area_plantada_ha >= 50)].copy()
mi["r"] = mi.producao_t / mi.area_plantada_ha
gm = mi.groupby("cod_local").r.apply(lambda v: np.std(np.log(v[v > 0])) if (v > 0).sum() > 5 else np.nan)
print(f"  referencia: dp mediano do log-rendimento do milho {gm.median():.2f}")
