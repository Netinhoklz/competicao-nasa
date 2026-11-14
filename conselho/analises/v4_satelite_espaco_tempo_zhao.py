"""v4 (rodada 2) - Cientista de satelite e inferencia causal: o contraste ENTRE climas da base de Zhao 2022
sobrevive a efeitos fixos de geografia? (conferencia do conflito Kluger x Zhao sobre temperatura e chuva)

Kluger 2025 (Tab. S9): DENTRO de cada regiao, estacao mais quente -> menor beneficio da leguminosa antecessora
(6 de 9 bT negativos) e mais chuva -> maior beneficio. O metodologo achou na base aberta de Zhao o contrario
ENTRE climas: sitios com MAT >= 20 C tem efeito MAIOR (b = +0,064 lnRR).
Pergunta: esse contraste entre climas e clima ou e sistema/regiao (Africa, pouco N, rendimento baixo)?
Teste: WLS (peso = wgt da base) de lnRR em MAT e AI, com N e diversidade (CD2) e cultura seguinte; erro-padrao
agrupado por sitio (lat/lon a 0,01 grau). Tres versoes: sem efeito fixo, com efeito fixo de continente,
com efeito fixo de pais. Se o coeficiente de MAT encolhe ou troca de sinal com EF de pais, o contraste entre
climas e confundido com sistema e NAO serve como resposta ao clima (regra R7 do catalogo).
A base nao tem clima do ano: nao da para medir a resposta no tempo aqui; isso so existe em Kluger.

Rodar: E:/campeonato-nasa/venv/Scripts/python.exe -I conselho/analises/v4_satelite_espaco_tempo_zhao.py
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: E402,F401

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.stdout.reconfigure(encoding="utf-8")
ARQ = DADOS / "meta_analises" / "zhao2022_figshare" / "data.csv"


def pct(b):
    return (np.exp(b) - 1) * 100


df = pd.read_csv(ARQ)
df = df.dropna(subset=["yi", "wgt", "MAT", "AI", "NFR", "CD2"]).copy()
df["sitio"] = df["Lat"].round(2).astype(str) + "_" + df["Lon"].round(2).astype(str)
df["MAT5"] = df["MAT"] / 5.0          # por +5 C
df["AI01"] = df["AI"] / 0.1           # por +0,1 de indice de aridez (mais umido)
df["N50"] = df["NFR"] / 50.0
df["milho"] = (df["SubEff"] == "Maize").astype(float)
df["sorgo_milheto"] = df["SubEff"].isin(["Sorghum", "Millet"]).astype(float)
df["trigo"] = df["SubEff"].isin(["Wheat"]).astype(float)
print(f"linhas {len(df)}; sitios {df['sitio'].nunique()}; paises {df['Country'].nunique()}")

base_cols = ["MAT5", "AI01", "N50", "CD2", "milho", "sorgo_milheto", "trigo"]


def ajusta(dd, fe=None, rotulo=""):
    X = dd[base_cols].astype(float)
    if fe is not None:
        X = pd.concat([X, pd.get_dummies(dd[fe], prefix=fe, drop_first=True, dtype=float)], axis=1)
    X = sm.add_constant(X)
    grupos = pd.factorize(dd["sitio"])[0]
    m = sm.WLS(dd["yi"].astype(float), X, weights=dd["wgt"].astype(float)).fit(
        cov_type="cluster", cov_kwds={"groups": grupos})
    print(f"\n[{rotulo}] n={len(dd)} sitios={dd['sitio'].nunique()} R2={m.rsquared:.3f}")
    for c in ["MAT5", "AI01", "N50", "CD2"]:
        b, se, p = m.params[c], m.bse[c], m.pvalues[c]
        lo, hi = b - 1.96 * se, b + 1.96 * se
        print(f"   {c:6s} b={b:+.4f} lnRR (IC95 {lo:+.4f} a {hi:+.4f}) p={p:.3f}  ~ {pct(b):+.1f}%")
    return m


print("\n===== S1. MAT e AI com e sem efeito fixo de geografia (toda a base) =====")
ajusta(df, None, "sem EF")
ajusta(df, "Continent", "EF continente")
ajusta(df, "Country", "EF pais")

print("\n===== S2. So sitios de sequeiro com N <= 50 (o caso do sertao) =====")
d2 = df[(df["IG"] == "no") & (df["NFR"] <= 50)].copy()
ajusta(d2, None, "sequeiro, N<=50, sem EF")
ajusta(d2, "Country", "sequeiro, N<=50, EF pais")

print("\n===== S3. Quanto do 'quente' e Africa? efeito medio por MAT dentro e fora da Africa =====")
for cont in ["Africa", "fora da Africa"]:
    dd = df[df["Continent"] == "Africa"] if cont == "Africa" else df[df["Continent"] != "Africa"]
    for nome, msk in [("MAT < 20", dd["MAT"] < 20), ("MAT >= 20", dd["MAT"] >= 20)]:
        s = dd[msk]
        if len(s) == 0:
            continue
        mp = np.sum(s["yi"] * s["wgt"]) / np.sum(s["wgt"])
        print(f"   {cont:15s} {nome:9s} n={len(s):5d} sitios={s['sitio'].nunique():4d} "
              f"media ponderada {pct(mp):+.1f}%  N mediano {s['NFR'].median():.0f}")
