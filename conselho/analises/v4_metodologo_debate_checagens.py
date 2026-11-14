"""v4 (rodada 2, debate) - Metodologo da generalizacao: checagens dos pontos em conflito entre especialistas.

A. Zhao 2022, PDF: definicao do indice de diversidade do controle (Eq. 1) e o que o texto diz do controle.
B. Zhao 2022, base aberta (Figshare data.csv): o efeito da leguminosa quando o CONTROLE ja e diverso (CD2 >= 6),
   medido, e nao extrapolado da reta (o "+4% contra o consorcio" do engenheiro e do especialista 1).
C. Zhao 2022, base aberta: caupi -> milho e caupi -> sorgo/milheto no analogo quente e seco (AI 0,2-0,5, MAT >= 20 C),
   com IC por bootstrap de sitio. Fecha a lacuna do especialista 1 (a base bloqueou o download dele).
D. Zhao 2022, base aberta: efeito por classe de chuva (MAP < 500, 500-700, 700-1000) com AI e N baixos - confronta
   a regra "abaixo de ~600 mm nao prometer ganho" (ecologo, Bowles) com a base global.
E. Mudare 2025, Source Data: nao leguminosa na Africa (aba Figure 1e) e classes de MAP (aba S5-S6), para arbitrar
   16% (texto) contra +2,3% (Source Data).

Rodar: E:/campeonato-nasa/venv/Scripts/python.exe -I conselho/analises/v4_metodologo_debate_checagens.py
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: E402,F401

import re
from pathlib import Path as _P

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RNG = np.random.default_rng(20261114)
PROJ = _P(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa")
ZHAO_CSV = _P(r"E:/campeonato-nasa/dados/meta_analises/zhao2022_figshare/data.csv")
MUDARE_SD = _P(r"E:/campeonato-nasa/dados/suplementos_artigos/2025_Mudare_source_data.xlsx")
ZHAO_PDF = PROJ / "artigos" / "2022_Zhao_Global_systematic_review_with_meta-analysis_reveals_yield.pdf"


def titulo(t):
    print("\n" + "=" * 20 + " " + t + " " + "=" * 20)


def pct(x):
    return (np.exp(x) - 1) * 100


def boot_sitio(df, nboot=1000):
    cod, inv = np.unique(df["sitio"].values, return_inverse=True)
    y, w = df["yi"].values, df["wgt"].values
    sy = np.bincount(inv, weights=y * w, minlength=len(cod))
    sw = np.bincount(inv, weights=w, minlength=len(cod))
    est = sy.sum() / sw.sum()
    bs = []
    for _ in range(nboot):
        k = RNG.integers(0, len(cod), len(cod))
        bs.append(sy[k].sum() / sw[k].sum())
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return est, lo, hi, len(cod), len(df)


def linha(rot, df):
    if len(df) == 0:
        print(f"{rot:60s} sem dados")
        return
    e, lo, hi, ns, no = boot_sitio(df)
    print(f"{rot:60s} {pct(e):+6.1f}% (IC sitio {pct(lo):+6.1f} a {pct(hi):+6.1f}) | {ns} sitios, {no} obs")


# ---------------- A ----------------
titulo("A. Zhao 2022 PDF: indice de diversidade do controle")
try:
    from pypdf import PdfReader
    r = PdfReader(str(ZHAO_PDF))
    for i, p in enumerate(r.pages):
        t = (p.extract_text() or "").replace("\n", " ")
        for m in re.finditer(r"[^.]{0,250}(Eq\. ?1|equation 1|\(1\)|crop diversity of the control|diversity index)[^.]{0,350}\.", t):
            print(f"p.{i+1}: {m.group(0)[:700]}")
            print("---")
except Exception as ex:  # noqa: BLE001
    print("falha ao ler PDF:", ex)

# ---------------- base aberta ----------------
z = pd.read_csv(ZHAO_CSV)
z["sitio"] = z["Lat"].round(2).astype(str) + "_" + z["Lon"].round(2).astype(str)
print("\ncolunas:", list(z.columns))
print("CD2 (diversidade do controle) - distribuicao:", z["CD2"].describe().round(2).to_dict())
print("PreEff top 15:", z["PreEff"].value_counts().head(15).to_dict())
print("SubEff top 12:", z["SubEff"].value_counts().head(12).to_dict())
print("NFR describe:", z["NFR"].describe().round(1).to_dict())

# ---------------- B ----------------
titulo("B. Efeito medido com controle ja diverso (CD2), N baixo")
nb = z["NFR"] <= 50
for lo_, hi_ in [(1, 1), (2, 3), (4, 5), (6, 9), (10, 99)]:
    m = (z["CD2"] >= lo_) & (z["CD2"] <= hi_)
    linha(f"CD2 {lo_}-{hi_}, todos os N", z[m])
    linha(f"CD2 {lo_}-{hi_}, N <= 50", z[m & nb])
print("Leitura: se CD2 >= 6 com N <= 50 der efeito >> +4%, a extrapolacao linear da Fig. 3b nao descreve os dados.")
print("Atencao: o controle de Zhao e sempre NAO leguminoso, mesmo com CD2 alto. Um consorcio milho+feijao nao e"
      " controle valido; o numero abaixo nao mede 'separar o consorcio no tempo'.")

# ---------------- C ----------------
titulo("C. Caupi e outras leguminosas -> cereal no analogo quente e seco")
an = (z["AI"] >= 0.2) & (z["AI"] < 0.5) & (z["MAT"] >= 20)
an_amplo = (z["AI"] < 0.65) & (z["MAT"] >= 20)
cer = z["SubEff"].isin(["Maize", "Sorghum", "Millet", "Pearl millet", "Pearl Millet"])
for esp in ["Cowpea", "Groundnut", "Peanut", "Pigeon pea", "Pigeonpea", "Common bean", "Bean", "Soybean", "Mungbean", "Mucuna"]:
    m = z["PreEff"].astype(str).str.lower() == esp.lower()
    if m.sum() == 0:
        continue
    linha(f"{esp} -> milho (global)", z[m & (z["SubEff"] == "Maize")])
    linha(f"{esp} -> milho (analogo AI 0,2-0,5, MAT>=20)", z[m & an & (z["SubEff"] == "Maize")])
    linha(f"{esp} -> milho/sorgo/milheto (analogo amplo AI<0,65, MAT>=20)", z[m & an_amplo & cer])
    paises = z[m & an_amplo & cer]["Country"].value_counts().to_dict()
    if paises:
        print("   paises:", paises)

# ---------------- D ----------------
titulo("D. Classe de chuva x efeito (leguminosa -> cereal, N <= 50, sequeiro quando informado)")
seq = z["IG"].astype(str).str.lower() != "yes"
for a, b in [(0, 500), (500, 600), (600, 700), (700, 1000), (1000, 5000)]:
    m = (z["MAP"] >= a) & (z["MAP"] < b)
    linha(f"MAP {a}-{b}, cereal, N<=50, nao irrigado", z[m & cer & nb & seq])
    linha(f"MAP {a}-{b}, qualquer cultura", z[m])

# ---------------- E ----------------
titulo("E. Mudare 2025 Source Data")
try:
    xl = pd.ExcelFile(MUDARE_SD)
    print("abas:", xl.sheet_names)
    for aba in xl.sheet_names:
        if aba.lower().replace(" ", "") in ("figure1e", "supplementaryfigures5-s6"):
            d = xl.parse(aba)
            print(f"\n-- aba {aba}: {d.shape}")
            print(d.head(40).to_string(max_colwidth=40))
except Exception as ex:  # noqa: BLE001
    print("falha ao ler Source Data:", ex)
