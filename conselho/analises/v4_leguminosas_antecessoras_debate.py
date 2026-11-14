"""v4 - Especialista em leguminosas antecessoras, RODADA 2 (debate): checagens de conflitos entre especialistas.

Usa a base aberta de Zhao et al. 2022 (Figshare 10.6084/m9.figshare.20290923, baixada pelo metodologo em
E:/campeonato-nasa/dados/meta_analises/zhao2022_figshare/data.csv) e o PAM do Ceara.

C1. Ranking de especies (conflito R6 do leguminosas x R6 do metodologo "amendoim > caupi"): por par
    antecessora -> cereal, no analogo quente e seco (AI 0,2-0,5 e MAT >= 20 C) e no amplo (AI < 0,65, MAT >= 20 C).
C2. O sorgo responde menos? (conflito R7 x metodologo "nao prometer ganho no sorgo"): sorgo x milho no analogo.
C3. Controle ja diverso (conflito "contra a S0 ~ +4%" do engenheiro): efeito observado com CD2 >= 8 e N baixo,
    em vez de extrapolar a reta da Fig. 3b.
C4. Quebra no PAM-CE: tres definicoes que circularam (4,8% / 15,1% / 22,7%) na mesma base.

Rodar: E:/campeonato-nasa/venv/Scripts/python.exe -I conselho/analises/v4_leguminosas_antecessoras_debate.py
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: E402,F401

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RNG = np.random.default_rng(20261114)
NBOOT = 1000


def pct(x):
    return (np.exp(x) - 1) * 100


def linha(rot, df):
    if len(df) == 0:
        print(f"  {rot:<52s} n=0")
        return
    g = df["sitio"].values
    cod, inv = np.unique(g, return_inverse=True)
    sy = np.bincount(inv, weights=df.yi.values * df.wgt.values)
    sw = np.bincount(inv, weights=df.wgt.values)
    k = len(cod)
    est = sy.sum() / sw.sum()
    idx = RNG.integers(0, k, size=(NBOOT, k))
    bs = sy[idx].sum(1) / sw[idx].sum(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    # mediana entre sitios (cada sitio = media ponderada propria)
    med_sit = np.median(sy / sw)
    paises = ",".join(sorted(df.Country.unique()))[:60]
    print(f"  {rot:<52s} n={len(df):4d} sitios={k:3d} efeito {pct(est):+6.1f}% IC sitio [{pct(lo):+6.1f}; {pct(hi):+6.1f}] "
          f"mediana sitios {pct(med_sit):+6.1f}% | {paises}")


z = pd.read_csv(r"E:/campeonato-nasa/dados/meta_analises/zhao2022_figshare/data.csv")
z["sitio"] = z["Lat"].round(2).astype(str) + "_" + z["Lon"].round(2).astype(str)
quente = z.MAT >= 20
estrito = quente & (z.AI >= 0.2) & (z.AI < 0.5)
amplo = quente & (z.AI < 0.65)
print(f"Zhao data.csv: {len(z)} linhas; analogo estrito {estrito.sum()} obs; amplo {amplo.sum()} obs")

print("\n===== C1/C2. Pares antecessora -> cereal =====")
pares = [("Cowpea", "Maize"), ("Peanut", "Maize"), ("Soybean", "Maize"), ("Common bean", "Maize"), ("Pigeon pea", "Maize"),
         ("Mucuna", "Maize"), ("Cowpea", "Sorghum"), ("Peanut", "Sorghum"), ("Cowpea", "Millet"), ("Peanut", "Millet")]
for nome, msk in [("GLOBAL", np.ones(len(z), bool)), ("AMPLO quente AI<0,65", amplo), ("ESTRITO quente AI 0,2-0,5", estrito)]:
    print(f" -- {nome}")
    for a, b in pares:
        linha(f"{a} -> {b}", z[msk & (z.PreEff == a) & (z.SubEff == b)])
print(" -- por especie antecessora, cereal qualquer (milho, sorgo, milheto), AMPLO e N <= 50")
cer = z.SubEff.isin(["Maize", "Sorghum", "Millet"])
for a in ["Cowpea", "Peanut", "Soybean", "Pigeon pea", "Common bean", "Mucuna", "Lablab"]:
    linha(f"{a} -> cereal tropical, N<=50", z[amplo & cer & (z.PreEff == a) & (z.NFR <= 50)])
print(" -- cereal seguinte (qualquer leguminosa), AMPLO")
for b in ["Maize", "Sorghum", "Millet"]:
    linha(f"leguminosa -> {b}", z[amplo & (z.SubEff == b)])
    linha(f"leguminosa -> {b}, N<=50", z[amplo & (z.SubEff == b) & (z.NFR <= 50)])

print("\n===== C3. Controle ja diverso (CD2 >= 8) =====")
for d in [1, 2, 4, 6, 8, 9, 12]:
    linha(f"CD2 == {d}, N <= 50", z[(z.CD2 == d) & (z.NFR <= 50)])
linha("CD2 >= 8, qualquer N", z[z.CD2 >= 8])
linha("CD2 >= 8, N <= 50", z[(z.CD2 >= 8) & (z.NFR <= 50)])
linha("CD2 >= 8, N <= 50, cereal", z[(z.CD2 >= 8) & (z.NFR <= 50) & z.SubEff.isin(["Maize", "Sorghum", "Millet", "Wheat", "Rice", "Barley"])])
sub = z[z.CD2 >= 8]
print("  CD2>=8: NumCroPerYr", sub.NumCroPerYr.value_counts().to_dict(), "| paises", sub.Country.value_counts().head(8).to_dict())
print("  CD2>=8: culturas seguintes", sub.SubEff.value_counts().head(6).to_dict(), "| antecessoras", sub.PreEff.value_counts().head(6).to_dict())

print("\n===== C4. Quebra do milho no PAM-CE, tres definicoes =====")
pam = pd.read_parquet(r"E:/campeonato-nasa/dados/derivados/ibge_pam_mun_anual.parquet")
m = pam[pam["produto"].astype(str).str.lower().str.contains("milho")].copy()
m = m[(m.area_plantada_ha > 0)]
m["yp"] = m.producao_t * 1000 / m.area_plantada_ha
m["med"] = m.groupby("cod_local").yp.transform("median")
for per in [(1988, 2025), (2000, 2024)]:
    s = m[(m.ano >= per[0]) & (m.ano <= per[1])]
    d1 = ((s.area_colhida_ha / s.area_plantada_ha) < 0.5).mean()
    d2 = (((s.area_colhida_ha / s.area_plantada_ha) < 0.5) | (s.producao_t <= 0)).mean()
    d3 = (s.yp < 0.5 * s.med).mean()
    d4 = (s.yp < 0.25 * s.med).mean()
    print(f"  {per}: n={len(s)} | colhida/plantada<0,5: {d1*100:.1f}% | idem ou producao 0: {d2*100:.1f}% | "
          f"rend/plantada < 0,5 mediana mun.: {d3*100:.1f}% | < 0,25 mediana: {d4*100:.1f}%")

print("\n===== C5. A 'perda' do PAM-NE (colhida/plantada < 0,5) depende da UF que informa? milho, 2000-2024 =====")
ne = pd.read_parquet(DERIV / "ibge_ne_pam_mun_anual.parquet")
ne = ne[(ne.ano >= 2000) & (ne.ano <= 2024) & ne.produto.astype(str).str.startswith("Milho") & (ne.area_plantada_ha > 0)].copy()
ne["uf"] = ne.cod_mun.astype(str).str[:2]
ne["perda_area"] = (ne.area_colhida_ha.fillna(0) / ne.area_plantada_ha < 0.5) | (ne.producao_t.fillna(0) <= 0)
ne["yp"] = ne.producao_t.fillna(0) * 1000 / ne.area_plantada_ha
ne["med"] = ne.groupby("cod_mun").yp.transform("median")
ne["perda_rend"] = ne.yp < 0.5 * ne.med
print(ne.groupby("uf").agg(n=("yp", "size"), perda_area=("perda_area", "mean"), perda_rend=("perda_rend", "mean")).round(3).to_string())
print(f"  NE: perda_area {ne.perda_area.mean()*100:.1f}% | perda_rend {ne.perda_rend.mean()*100:.1f}%")
