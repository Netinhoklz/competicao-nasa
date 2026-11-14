"""Rodada 2 (debate) - Engenheiro do motor.

Pergunta: a regra "contra base diversificada o bonus da leguminosa cai para ~0 a +4%"
(extrapolacao da reta de Zhao 2022, Fig. 3b: +50% em D=1 sem N, -6,6% por unidade)
se sustenta nos DADOS ABERTOS do proprio Zhao? E o sorgo responde menos que o milho
no estrato quente e seco?

Base: Zhao et al. 2022 (Nat Commun 13:4926), Figshare data.csv (CC BY 4.0), ja baixada
pelo metodologo em E:/campeonato-nasa/dados/meta_analises/zhao2022_figshare/data.csv.
Colunas usadas: yi (lnRR), wgt (peso por replicas, Eq. 3 do artigo), CD2 (diversidade do
CONTROLE nao leguminoso, Eq. 1, p.6), NFR (kg N/ha na cultura principal), AI, MAT, SubEff,
NumCroPerYr, Lat, Lon, IG (irrigacao, sim/nao/vazio).

Limite: o controle do Zhao NUNCA contem leguminosa (p.6: "Crop diversity was calculated for
each non-legume cropping system (i.e., the control)"). Logo nenhum recorte aqui mede a base
do Ceara (consorcio milho+feijao). Mede so se "base diversa sem leguminosa" derruba o bonus.

Metodo: media ponderada de lnRR (peso wgt), IC95 por bootstrap de sitios (lat/lon a 0,01 grau),
2.000 reamostragens. Nao e o modelo misto do artigo.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
ARQ = "E:/campeonato-nasa/dados/meta_analises/zhao2022_figshare/data.csv"
d = pd.read_csv(ARQ, encoding="latin1")
d["sitio"] = d.Lat.round(2).astype(str) + "_" + d.Lon.round(2).astype(str)
rng = np.random.default_rng(20261114)


def resumo(sub, rotulo, nboot=2000):
    sub = sub.dropna(subset=["yi", "wgt"])
    if len(sub) == 0:
        print(f"{rotulo:<62s} sem dados")
        return
    g = sub.groupby("sitio")
    sw = g.apply(lambda x: (x.yi * x.wgt).sum(), include_groups=False).values
    w = g.wgt.sum().values
    est = sw.sum() / w.sum()
    k = len(w)
    bs = []
    for _ in range(nboot):
        idx = rng.integers(0, k, k)
        bs.append(sw[idx].sum() / w[idx].sum())
    lo, hi = np.percentile(bs, [2.5, 97.5])
    pct = lambda v: 100 * (np.exp(v) - 1)
    print(f"{rotulo:<62s} n={len(sub):5d} sitios={k:4d}  {pct(est):+6.1f}%  IC95 [{pct(lo):+6.1f}; {pct(hi):+6.1f}]")


print("Bloco 1. Bonus da leguminosa por diversidade do CONTROLE (CD2), base inteira")
for nome, cond in [("CD2 = 1 (monocultura)", d.CD2 == 1), ("CD2 2-4", d.CD2.between(1.5, 4)),
                   ("CD2 6-9", d.CD2.between(6, 9)), ("CD2 >= 12", d.CD2 >= 12)]:
    resumo(d[cond], "  todos N, " + nome)
for nome, cond in [("CD2 = 1", d.CD2 == 1), ("CD2 2-4", d.CD2.between(1.5, 4)), ("CD2 6-9", d.CD2.between(6, 9))]:
    resumo(d[cond & (d.NFR <= 50)], "  N <= 50, " + nome)

print("\nReferencia do artigo (Fig. 3b, p.3, sem N): +50% em D=1, -6,6% por unidade.")
print("  Reta extrapolada: D=8 -> 50 - 6,6*7 = +3,8%;  D=6 -> +17,0%;  D=4 -> +30,2%.")

print("\nBloco 2. Estrato quente e seco (AI 0,2-0,5 e MAT >= 20 C), cereal tropical")
qs = d.AI.between(0.2, 0.5) & (d.MAT >= 20)
cer = d.SubEff.isin(["Maize", "Sorghum", "Millet"])
resumo(d[qs & cer], "  milho+sorgo+milheto, todos CD2")
resumo(d[qs & cer & (d.CD2 == 1)], "  milho+sorgo+milheto, CD2 = 1")
resumo(d[qs & cer & (d.CD2 > 1)], "  milho+sorgo+milheto, CD2 > 1")
resumo(d[qs & cer & (d.CD2 >= 4)], "  milho+sorgo+milheto, CD2 >= 4")
print("  distribuicao de CD2 no estrato:", d[qs & cer].CD2.value_counts().sort_index().to_dict())

print("\nBloco 3. Sorgo x milho (conflito Franke x Zhao), mesmo estrato e global")
for cult in ["Maize", "Sorghum", "Millet"]:
    resumo(d[qs & (d.SubEff == cult)], f"  quente-seco, {cult}")
for cult in ["Maize", "Sorghum", "Millet"]:
    resumo(d[qs & (d.SubEff == cult) & (d.NFR <= 50)], f"  quente-seco, N<=50, {cult}")
for cult in ["Maize", "Sorghum"]:
    resumo(d[(d.SubEff == cult) & (d.AI < 0.65)], f"  AI < 0,65 (qualquer MAT), {cult}")

print("\nBloco 4. Controle com mais de uma cultura por ano (NumCroPerYr >= 2)")
resumo(d[d.NumCroPerYr >= 2], "  todos")
resumo(d[(d.NumCroPerYr >= 2) & (d.NFR <= 50)], "  N <= 50")
resumo(d[(d.NumCroPerYr >= 2) & (d.Lat.abs() < 23.5)], "  tropicos")
print("  (Nyear na Eq. 1 = especies por ano do CONTROLE; o artigo nao diz se e consorcio ou duas safras)")

print("\nBloco 5. Robustez: estrato quente-seco cereal sem o sitio de maior peso")
s = d[qs & cer]
top = s.groupby("sitio").wgt.sum().idxmax()
print("  sitio de maior peso:", top, "obs:", int((s.sitio == top).sum()), "pais:", s[s.sitio == top].Country.iloc[0])
resumo(s[s.sitio != top], "  sem o sitio de maior peso")
