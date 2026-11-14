"""v4 (rodada 2, debate) - Agronomo de plantas de cobertura no Nordeste.

Pergunta do debate: os numeros de ADUBO VERDE antes do milho (mucuna -> milho +78%, Zhao 2022 Fig. 5;
crotalaria -> milho +83%, Mudare 2025 Supl. Tab. 5) foram medidos em que clima, com que agua e com que N?
Eles valem para o sequeiro do semiarido?

Fonte: base aberta de Zhao et al. 2022 (Nat Commun 13:4926; Figshare 10.6084/m9.figshare.20290923, CC BY 4.0),
ja baixada pelo metodologo em E:/campeonato-nasa/dados/meta_analises/zhao2022_figshare/data.csv.
Colunas usadas: PreEff (leguminosa), PreLegPur (Seed / GRM = adubo verde / Forage), SubEff (cultura seguinte),
AI (indice de aridez), MAT, MAP, IG (irrigado), NFR (kg N/ha), Country, Lat/Lon, wgt, yi (lnRR).

Blocos:
 A. Finalidade da leguminosa (grao, adubo verde, forragem) -> cereal tropical (milho, sorgo, milheto, arroz):
    efeito com IC por bootstrap de SITIO, no geral e por estrato de aridez/temperatura.
 B. Especie de cobertura tropical -> milho: n, sitios, paises, AI, MAP, irrigacao, N, efeito.
 C. No analogo quente e seco (AI 0,2-0,5 e MAT >= 20 C): adubo verde contra grao, por cultura seguinte.
 D. Adubo verde: o efeito cai com o N (como na leguminosa de grao)?

Nao e o modelo misto do artigo: media ponderada (wgt) de lnRR com bootstrap de sitios (0,01 grau).

Rodar: E:/campeonato-nasa/venv/Scripts/python.exe -I conselho/analises/v4_agronomo_cobertura_debate_adubo_verde_zhao.py
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: E402,F401

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ARQ = r"E:/campeonato-nasa/dados/meta_analises/zhao2022_figshare/data.csv"
RNG = np.random.default_rng(20261114)
NBOOT = 2000

d = pd.read_csv(ARQ, encoding_errors="replace", low_memory=False)
d["PreEff"] = d["PreEff"].replace({"Pigeonpea": "Pigeon pea", "Sunn hemp": "Crotalaria (sunn hemp)",
                                    "Crotalaria": "Crotalaria (sunn hemp)"})
d["sitio"] = d["Lat"].round(2).astype(str) + "_" + d["Lon"].round(2).astype(str)
d = d.dropna(subset=["yi", "wgt"])


def pct(x):
    return 100 * (np.exp(x) - 1)


def efeito(sub):
    """Media ponderada de lnRR e IC95 por bootstrap de sitios."""
    if len(sub) == 0:
        return None
    g = sub.groupby("sitio").apply(lambda s: pd.Series({"sw": s["wgt"].sum(), "swy": (s["wgt"] * s["yi"]).sum()}),
                                   include_groups=False)
    sw, swy = g["sw"].to_numpy(), g["swy"].to_numpy()
    m = swy.sum() / sw.sum()
    k = len(g)
    if k >= 3:
        idx = RNG.integers(0, k, size=(NBOOT, k))
        bm = swy[idx].sum(1) / sw[idx].sum(1)
        lo, hi = np.percentile(bm, [2.5, 97.5])
    else:
        lo = hi = np.nan
    return dict(n=len(sub), sitios=k, m=pct(m), lo=pct(lo), hi=pct(hi),
                pos=100 * (sub["yi"] > 0).mean())


def linha(rot, sub):
    e = efeito(sub)
    if e is None:
        print(f"  {rot:<48} sem dados")
        return
    ic = "IC n/d (< 3 sitios)" if np.isnan(e["lo"]) else f"IC95 sitio {e['lo']:+.1f} a {e['hi']:+.1f}%"
    print(f"  {rot:<48} {e['m']:+6.1f}%  {ic:<28} n={e['n']:>5}  sitios={e['sitios']:>3}  obs>0 {e['pos']:.0f}%")


CEREAL_TROP = ["Maize", "Sorghum", "Millet", "Rice"]
cer = d[d["SubEff"].isin(CEREAL_TROP)]

print("=" * 110)
print("A. Finalidade da leguminosa antecessora -> cereal tropical (milho, sorgo, milheto, arroz)")
print("=" * 110)
for fin in ["Seed", "GRM", "Forage"]:
    linha(f"{fin} (todos os climas)", cer[cer["PreLegPur"] == fin])
print(" Por estrato de clima:")
estratos = {
    "AI < 0,5 (arido + semiarido)": cer["AI"] < 0.5,
    "AI 0,2-0,5 e MAT >= 20 C (analogo do CE)": (cer["AI"].between(0.2, 0.5)) & (cer["MAT"] >= 20),
    "AI 0,5-0,65": cer["AI"].between(0.5, 0.65, inclusive="left"),
    "AI >= 0,65 (umido)": cer["AI"] >= 0.65,
}
for nome, msk in estratos.items():
    for fin in ["Seed", "GRM"]:
        linha(f"{fin} | {nome}", cer[msk & (cer["PreLegPur"] == fin)])
print(" Adubo verde (GRM) -> cereal tropical, por irrigacao:")
for ig in ["no", "yes"]:
    linha(f"GRM | irrigado = {ig}", cer[(cer["PreLegPur"] == "GRM") & (cer["IG"] == ig)])
linha("GRM | irrigado = nao informado", cer[(cer["PreLegPur"] == "GRM") & (cer["IG"].isna())])

print()
print("=" * 110)
print("B. Especies de cobertura tropical -> milho (todas as finalidades; a finalidade dominante entre parenteses)")
print("=" * 110)
ESP = ["Mucuna", "Crotalaria (sunn hemp)", "Lablab", "Pigeon pea", "Jackbean", "Sesbania", "Cowpea"]
mil = d[d["SubEff"] == "Maize"]
for esp in ESP:
    s = mil[mil["PreEff"] == esp]
    if len(s) == 0:
        print(f"  {esp}: sem pares com milho")
        continue
    linha(f"{esp} -> milho", s)
    fin = s["PreLegPur"].value_counts().to_dict()
    paises = s.groupby("Country")["sitio"].nunique().sort_values(ascending=False).to_dict()
    print(f"      finalidade {fin}; paises (sitios) {paises}")
    print(f"      AI mediana {s['AI'].median():.2f} (min {s['AI'].min():.2f}, max {s['AI'].max():.2f}); "
          f"MAP mediana {s['MAP'].median():.0f} mm (min {s['MAP'].min():.0f}); MAT mediana {s['MAT'].median():.1f} C; "
          f"irrigado {s['IG'].value_counts(dropna=False).to_dict()}; N mediana {s['NFR'].median():.0f} kg/ha")
    seco = s[s["AI"] < 0.5]
    print(f"      com AI < 0,5: {len(seco)} obs em {seco['sitio'].nunique()} sitios "
          f"{sorted(seco['Country'].unique().tolist())}")

print()
print("=" * 110)
print("C. Analogo quente e seco (AI 0,2-0,5 e MAT >= 20 C): finalidade x cultura seguinte")
print("=" * 110)
an = d[d["AI"].between(0.2, 0.5) & (d["MAT"] >= 20)]
for sub in ["Maize", "Sorghum", "Millet"]:
    for fin in ["Seed", "GRM", "Forage"]:
        s = an[(an["SubEff"] == sub) & (an["PreLegPur"] == fin)]
        if len(s):
            linha(f"{fin} -> {sub}", s)
            print(f"      especies {s['PreEff'].value_counts().to_dict()}; paises {sorted(s['Country'].unique().tolist())}; "
                  f"irrigado {s['IG'].value_counts(dropna=False).to_dict()}")

print()
print("=" * 110)
print("D. Adubo verde (GRM) -> cereal tropical: o efeito cai com o N do cereal?")
print("=" * 110)
g = cer[(cer["PreLegPur"] == "GRM")].dropna(subset=["NFR"])
for lo_, hi_, rot in [(0, 0, "0 kg N"), (1, 60, "1-60 kg N"), (61, 120, "61-120 kg N"), (121, 1000, "> 120 kg N")]:
    linha(f"GRM | {rot}", g[g["NFR"].between(lo_, hi_)])
s = cer[(cer["PreLegPur"] == "Seed")].dropna(subset=["NFR"])
for lo_, hi_, rot in [(0, 0, "0 kg N"), (1, 60, "1-60 kg N"), (61, 120, "61-120 kg N"), (121, 1000, "> 120 kg N")]:
    linha(f"Seed | {rot}", s[s["NFR"].between(lo_, hi_)])
# inclinacao WLS simples lnRR ~ N, por finalidade
for fin, sub in [("GRM", g), ("Seed", s)]:
    w = sub["wgt"].to_numpy()
    X = np.c_[np.ones(len(sub)), sub["NFR"].to_numpy() / 50.0]
    y = sub["yi"].to_numpy()
    b = np.linalg.solve(X.T @ (X * w[:, None]), X.T @ (w * y))
    print(f"  WLS {fin}: lnRR = {b[0]:.3f} {b[1]:+.3f} x (N/50)  -> {pct(b[0]):+.1f}% sem N; "
          f"{100*b[1]:+.1f} p.p. de lnRR a cada 50 kg N (sem EP agrupado; descritivo)")

print()
print("Brasil na base (qualquer finalidade -> cereal):")
br = cer[cer["Country"] == "Brazil"]
print(f"  {len(br)} obs, {br['sitio'].nunique()} sitios, AI {br['AI'].min():.2f}-{br['AI'].max():.2f}, "
      f"especies {br['PreEff'].value_counts().to_dict()}, finalidade {br['PreLegPur'].value_counts().to_dict()}")
linha("Brasil -> cereal", br)
