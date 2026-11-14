"""Integrador (v4, catalogo de rotacoes): confere no texto dos artigos os numeros em que os
especialistas divergiram ou que vao para o bloco PARA VERIFICAR.
(A) Source Data do Mudare 2025: Fig. 1e (regiao x leguminosa), Fig. 2b (pares), Supl. S5-S6.
(B) Trechos do texto dos PDFs (pypdf) em torno de cada numero.
(C) Tabela 3 do Franke 2018 (XML do Europe PMC).
Somente le arquivos.
"""
import re
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import math
import pandas as pd
from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")
ART = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/artigos")
SUP = Path(r"E:/campeonato-nasa/dados/suplementos_artigos")
META = Path(r"E:/campeonato-nasa/dados/meta_analises")


def pct(x):
    try:
        return f"{(math.exp(float(x)) - 1) * 100:+.1f}%"
    except Exception:
        return "?"


print("=== A. Source Data Mudare 2025 ===")
xl = pd.ExcelFile(SUP / "2025_Mudare_source_data.xlsx")
print("abas:", xl.sheet_names)
for aba in xl.sheet_names:
    if not re.search(r"1e|2b|S5|2a", aba, re.I):
        continue
    df = xl.parse(aba, header=None)
    print(f"\n--- aba {aba!r}: {df.shape} ---")
    # localizar a linha de cabecalho
    for i in range(min(6, len(df))):
        print("  cab", i, [str(v)[:22] for v in df.iloc[i].tolist()[:12]])
    alvo = r"Africa|North America|South America|Sun hemp|Crotalaria|Mixture|Alfalfa|Clover|Cowpea|Fallow|Sorghum|Pigeon|Mucuna|Velvet|Groundnut|Peanut|Soybean|<\s*500|500|1000|Irrig|Rainfed|Sand|Legume|Non"
    for i in range(len(df)):
        lin = " ".join(str(v) for v in df.iloc[i].tolist())
        if re.search(alvo, lin, re.I):
            vals = df.iloc[i].tolist()
            txt = " | ".join(str(v)[:14] for v in vals[:12])
            print(f"  r{i}: {txt}")

print("\n--- Fig. 2b completa (pares antecessora -> principal; efeito em %, IC em %) ---")
f2b = xl.parse("Figure 2b", header=2)
print(f2b.iloc[:, [0, 1, 2, 5, 6, 7]].to_string())

print("\n=== B. Trechos dos PDFs ===")
BUSCA = {
    "2022_Zhao": [r"excluded", r"236", r"28\.9", r"32\.4", r"14\.5", r"78%", r"1\.3%", r"32%", r"7%"],
    "2025_Mudare": [r"lnCV", r"83%", r"16%", r"29%", r"stable", r"transgressive"],
    "2020_Bowles": [r"88\.9", r"89\.9", r"28\.1", r"22\.6"],
    "2021_Renwick": [r"17\.1", r"53\s?%", r"36\s?%"],
    "2017_Diniz": [r"1\.51", r"12[.,]130|12130", r"14[.,]073|14073", r"4[.,]627|4627"],
    "2026_Raveloaritiana": [r"0\.1259", r"0\.3633", r"189"],
    "2013_Melo": [r"3[.,]728", r"3[.,]447", r"22[.,]1", r"49[.,]3"],
    "2025_Kluger": [r"4\.5%", r"3\.7"],
    "2011_Rusinamhodzi": [r"mean\s*=\s*0\.1", r"20 years", r"63"],
    "2015_Martins": [r"410", r"36[,.]"],
    "2011_Souza": [r"13%|13 %", r"66"],
}
for pref, pads in BUSCA.items():
    arqs = sorted(ART.glob(pref + "*.pdf"))
    if not arqs:
        print(f"\n[{pref}] PDF nao encontrado")
        continue
    r = PdfReader(str(arqs[0]))
    print(f"\n[{arqs[0].name}] {len(r.pages)} p.")
    paginas = []
    for k, pg in enumerate(r.pages):
        try:
            paginas.append(pg.extract_text() or "")
        except Exception:
            paginas.append("")
    for pad in pads:
        n = 0
        for k, t in enumerate(paginas):
            t2 = re.sub(r"\s+", " ", t)
            for m in re.finditer(pad, t2):
                ini = max(0, m.start() - 110)
                print(f"  [{pad}] p.{k + 1}: ...{t2[ini:m.end() + 110]}...")
                n += 1
                if n >= 3:
                    break
            if n >= 3:
                break
        if n == 0:
            print(f"  [{pad}] sem ocorrencia")

print("\n=== C. Franke 2018, Tabela 3 (XML) ===")
xml = (META / "franke2018_pmc" / "franke2018.xml").read_text(encoding="utf-8", errors="ignore")
m = re.search(r"<table-wrap[^>]*>.*?Table 3.*?</table-wrap>", xml, re.S)
if m:
    tab = m.group(0)
    linhas = re.findall(r"<tr>(.*?)</tr>", tab, re.S)
    for l in linhas:
        cel = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", l, re.S)]
        print("  ", " | ".join(cel))
else:
    print("  tabela 3 nao encontrada")
for pad in [r"crop failure", r"Sudano-Sahelian zone[^.]{0,200}", r"intercrop[^.]{0,120}excluded|excluded[^.]{0,120}intercrop"]:
    for mm in list(re.finditer(pad, xml, re.I))[:2]:
        s = re.sub(r"<[^>]+>", "", xml[max(0, mm.start() - 150): mm.end() + 150])
        print(f"  [{pad[:25]}] ...{re.sub(chr(10), ' ', s)}...")
