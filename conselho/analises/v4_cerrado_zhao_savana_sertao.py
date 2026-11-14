"""v4 Cerrado/MATOPIBA - rodada 2 (debate).
Pergunta: na base aberta do Zhao 2022 (Figshare), o efeito da leguminosa antecessora
no cereal muda entre o analogo da savana umida (Cerrado/MATOPIBA: MAT >= 20, MAP 1000-1800)
e o analogo quente e semiarido (sertao: AI 0,2-0,5, MAT >= 20)? E os pares do Brasil?
Media ponderada de lnRR (peso wgt) e IC por bootstrap de sitios (Lat/Lon a 0,01 grau).
Nao e o modelo misto do artigo.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
CSV = r"E:/campeonato-nasa/dados/meta_analises/zhao2022_figshare/data.csv"
d = pd.read_csv(CSV, index_col=0)
d["sitio"] = d["Lat"].round(2).astype(str) + "_" + d["Lon"].round(2).astype(str)
rng = np.random.default_rng(42)


def resumo(sub, rotulo, B=2000):
    sub = sub.dropna(subset=["yi", "wgt"])
    if len(sub) == 0:
        print(f"{rotulo}: vazio")
        return
    sitios = sub["sitio"].unique()
    est = np.average(sub["yi"], weights=sub["wgt"])
    grupos = {s: g for s, g in sub.groupby("sitio")}
    boots = []
    if len(sitios) >= 3:
        for _ in range(B):
            amostra = rng.choice(sitios, size=len(sitios), replace=True)
            g = pd.concat([grupos[s] for s in amostra])
            boots.append(np.average(g["yi"], weights=g["wgt"]))
        lo, hi = np.percentile(boots, [2.5, 97.5])
        ic = f"IC sitio {100*(np.exp(lo)-1):+.1f} a {100*(np.exp(hi)-1):+.1f}%"
    else:
        ic = "IC n/d (< 3 sitios)"
    paises = ", ".join(sorted(sub["Country"].unique())[:8])
    print(f"{rotulo}: {100*(np.exp(est)-1):+.1f}% ({ic}); n obs={len(sub)}, sitios={len(sitios)}; "
          f"frac neg={np.mean(sub['yi']<0):.2f}; paises: {paises}")


cereal = d["SubEff"].isin(["Maize", "Rice", "Sorghum", "Millet", "Wheat"])
savana = (d["MAT"] >= 20) & (d["MAP"].between(1000, 1800))
sertao = (d["MAT"] >= 20) & (d["AI"].between(0.2, 0.5))
brasil = d["Country"] == "Brazil"

print("== Colunas de antecessora mais comuns:", d["PreEff"].value_counts().head(12).to_dict())
print("== Culturas seguintes mais comuns:", d["SubEff"].value_counts().head(10).to_dict())
print()
print("== A. Leguminosa -> cereal por analogo")
resumo(d[cereal & savana], "Savana umida (MAT>=20, MAP 1000-1800) -> cereal")
resumo(d[cereal & sertao], "Semiarido quente (AI 0,2-0,5, MAT>=20) -> cereal")
resumo(d[cereal & savana & (d["NFR"] <= 50)], "Savana umida, N<=50")
resumo(d[cereal & savana & (d["NFR"] > 50)], "Savana umida, N>50")
print()
print("== B. Pares do foco MATOPIBA (soja/caupi -> milho/arroz) por analogo")
for pre in ["Soybean", "Cowpea", "Groundnut", "Mucuna", "Pigeon pea"]:
    for sub_c in ["Maize", "Rice"]:
        m = (d["PreEff"] == pre) & (d["SubEff"] == sub_c)
        if m.sum() == 0:
            continue
        resumo(d[m & savana], f"{pre}->{sub_c} savana umida")
        resumo(d[m & sertao], f"{pre}->{sub_c} semiarido quente")
print()
print("== C. Brasil")
resumo(d[brasil], "Brasil, todas as culturas")
print(d.loc[brasil, ["PreEff", "SubEff", "AI", "MAP", "MAT", "Lat", "Lon"]]
      .groupby(["PreEff", "SubEff"]).agg(n=("AI", "size"), AI=("AI", "median"),
                                          MAP=("MAP", "median"), MAT=("MAT", "median"),
                                          lat=("Lat", "median")).to_string())
resumo(d[brasil & cereal], "Brasil -> cereal")
