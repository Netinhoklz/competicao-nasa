"""v4 - Metodologo da generalizacao (cetico): o efeito medido num lugar transfere para o semiarido?

Testes rapidos (< 8 min) com os DADOS ABERTOS das proprias meta-analises e com os nossos dados:

A. Zhao et al. 2022 (Nat Commun 13:4926), base aberta no Figshare (doi 10.6084/m9.figshare.20290923, CC BY 4.0,
   11.768 pares, colunas AI, MAT, MAP, NFR, CD2, RC, IG, yi = lnRR). Pergunta: o efeito da leguminosa antecessora
   no semiarido quente (AI 0,2-0,5 e MAT >= 20 C) e o que os moderadores globais (N, diversidade, cultura) preveem?
   - A1 reproduz a media global (artigo: +20,4%, IC 17,7-23,1%, p.2)
   - A2 efeito por classe de aridez (UNEP) com IC por bootstrap de SITIO (as observacoes do mesmo sitio nao sao independentes)
   - A3 analogo do Ceara (AI 0,2-0,5, MAT >= 20 C): quantos sitios, que paises, que efeito
   - A4 meta-regressao WLS com erro-padrao agrupado por sitio: N, diversidade, aridez, temperatura
   - A5 teste de transferencia: modelo ajustado FORA do analogo preve a media DENTRO do analogo?
   - A6 irrigacao dentro das zonas secas; A7 ciclo de rotacao (duracao); A8 MAP nao e aridez
B. Kluger et al. 2025 (ERL), Tabela S9 (p.64 do PDF): sinal e significancia da heterogeneidade com chuva e temperatura
C. Franke et al. 2018 (AGEE 261:172), texto completo pelo Europe PMC (PMC5946712): Tabela 3 (zona agroecologica,
   cereal, leguminosa, N, ciclo) e Tabela 2 (estudos da zona sudano-saheliana)
D. Raveloaritiana & Wanger 2026: aritmetica do "+189% de lucratividade" (p.4 do PDF)
E. Nossos dados: (1) aridez P/ET0 do Ceara pelo NASA POWER x cobertura da base de Zhao;
   (2) PAM Ceara: fracao de municipio-anos com perda (colhida/plantada) - Zhao EXCLUIU rendimento zero (p.7)

Rodar: E:/campeonato-nasa/venv/Scripts/python.exe -I conselho/analises/v4_metodologo_transferencia_moderadores.py
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: E402,F401

import hashlib
import re
import time as _time
import xml.etree.ElementTree as ET
from pathlib import Path as _P

import numpy as np
import pandas as pd
import statsmodels.api as sm

T0 = _time.time()
sys.stdout.reconfigure(encoding="utf-8")
RNG = np.random.default_rng(20261114)
NBOOT = 1000
PROJ = _P(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa")
META = DADOS / "meta_analises"


def titulo(t):
    print("\n" + "=" * 20 + " " + t + " " + "=" * 20)


def pct(lnrr):
    return (np.exp(lnrr) - 1) * 100


def media_pond(y, w):
    return float(np.sum(y * w) / np.sum(w))


def boot_sitio(df, col_y="yi", col_w="wgt", col_g="sitio", nboot=NBOOT):
    """Media ponderada de lnRR com IC95 por bootstrap de sitios (reamostra sitios inteiros)."""
    g = df[col_g].values
    cod, inv = np.unique(g, return_inverse=True)
    sy = np.bincount(inv, weights=df[col_y].values * df[col_w].values)
    sw = np.bincount(inv, weights=df[col_w].values)
    k = len(cod)
    est = sy.sum() / sw.sum()
    idx = RNG.integers(0, k, size=(nboot, k))
    bs = sy[idx].sum(1) / sw[idx].sum(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return est, lo, hi, k


def linha(rotulo, df):
    if len(df) == 0:
        print(f"  {rotulo:<58s} n=0")
        return None
    e, lo, hi, k = boot_sitio(df)
    print(f"  {rotulo:<58s} n={len(df):5d} sitios={k:4d}  efeito {pct(e):+6.1f}%  IC95 sitio [{pct(lo):+6.1f}, {pct(hi):+6.1f}]")
    return e, lo, hi, k


# =====================================================================================================
# A. ZHAO 2022 - base aberta
# =====================================================================================================
titulo("A. Zhao et al. 2022 - base aberta do Figshare (11.768 pares)")
zdir = META / "zhao2022_figshare"
zdir.mkdir(parents=True, exist_ok=True)
zcsv = zdir / "data.csv"
if not zcsv.exists():
    import requests
    r = requests.get("https://ndownloader.figshare.com/files/36749424", timeout=120)
    r.raise_for_status()
    zcsv.write_bytes(r.content)
md5 = hashlib.md5(zcsv.read_bytes()).hexdigest()
print(f"  arquivo {zcsv} md5 {md5} (Figshare informa 3b2475164c21d87a5435db67d09fc1ef) -> {'OK' if md5 == '3b2475164c21d87a5435db67d09fc1ef' else 'DIFERENTE'}")
z = pd.read_csv(zcsv)
z["Continent"] = z["Continent"].replace({"Arfica": "Africa"})
z["sitio"] = z["Lat"].round(2).astype(str) + "_" + z["Lon"].round(2).astype(str)
print(f"  linhas {len(z)}; sitios (lat/lon a 0,01 grau) {z.sitio.nunique()}; paises {z.Country.nunique()}")
print(f"  ATENCAO: a base nao tem identificador de estudo nem rendimento do controle; o agrupamento e por sitio")

# A1 reproducao
titulo("A1. Reproducao da media global (artigo p.2: +20,4%, IC95 17,7-23,1%)")
linha("todas as observacoes (media ponderada por replicas)", z)
print(f"  mediana dos lnRR: {pct(np.median(z.yi)):+.1f}% (artigo: mediana 10,2%)")
print(f"  fracao positiva {np.mean(z.yi > 0)*100:.1f}% | nula {np.mean(z.yi == 0)*100:.1f}% | negativa {np.mean(z.yi < 0)*100:.1f}% (artigo: 73,6/0,7/25,7)")

# A2 classes de aridez
titulo("A2. Efeito por classe de aridez (AI = P/PET; UNEP: <0,2 arido; 0,2-0,5 semiarido; 0,5-0,65 subumido seco; >0,65 umido)")
cortes = [0, 0.2, 0.5, 0.65, 1.0, 10]
nomes = ["arido (<0,2)", "semiarido (0,2-0,5)", "subumido seco (0,5-0,65)", "umido (0,65-1,0)", "hiperumido (>1,0)"]
z["classe_ai"] = pd.cut(z.AI, cortes, labels=nomes, right=False)
for c in nomes:
    linha(f"{c}", z[z.classe_ai == c])
print("  -- so cereais (maize, sorghum, millet, wheat, barley, rice)")
cereais = ["Maize", "Sorghum", "Millet", "Wheat", "Barley", "Rice"]
for c in nomes:
    linha(f"{c} | cereais", z[(z.classe_ai == c) & z.SubEff.isin(cereais)])

# A3 analogo do Ceara
titulo("A3. Analogo termo-hidrico do Ceara: AI 0,2-0,5 E temperatura media anual >= 20 C")
an = z[(z.AI >= 0.2) & (z.AI < 0.5) & (z.MAT >= 20)]
linha("analogo (AI 0,2-0,5 e MAT >= 20)", an)
if len(an):
    print("  paises:", an.groupby("Country").agg(n=("yi", "size"), sitios=("sitio", "nunique")).sort_values("n", ascending=False).to_dict("index"))
    print("  cultura seguinte:", an.SubEff.value_counts().to_dict())
    print("  leguminosa antecessora:", an.PreEff.value_counts().head(12).to_dict())
    print("  N aplicado no analogo: mediana", an.NFR.median(), "| p10-p90", an.NFR.quantile([.1, .9]).round(0).tolist())
    print("  irrigacao no analogo:", an.IG.value_counts(dropna=False).to_dict())
an2 = z[(z.AI < 0.65) & (z.MAT >= 20)]
linha("analogo amplo (AI < 0,65 e MAT >= 20)", an2)
an3 = an2[(an2.NFR <= 50) & an2.SubEff.isin(["Maize", "Sorghum", "Millet"]) & (an2.IG != "yes")]
linha("amplo + N <= 50 + milho/sorgo/milheto + nao irrigado", an3)
print("     paises desse recorte:", an3.groupby("Country").agg(n=("yi", "size"), sitios=("sitio", "nunique")).to_dict("index"))
linha("  o mesmo recorte SEM Africa", an3[an3.Continent != "Africa"])
linha("  o mesmo recorte SO Africa", an3[an3.Continent == "Africa"])
linha("  o mesmo recorte sem o sitio unico do Mali (84 obs)", an3[an3.Country != "Mali"])
s_med = an3.groupby("sitio").apply(lambda g: media_pond(g.yi.values, g.wgt.values))
print(f"     mediana entre SITIOS (cada sitio pesa 1): {pct(s_med.median()):+.1f}% | sitios com efeito negativo {int((s_med < 0).sum())} de {len(s_med)}")
for leg in ["Cowpea", "Peanut", "Common bean", "Pigeon pea", "Mucuna", "Lablab"]:
    linha(f"amplo | antecessora = {leg}", an2[an2.PreEff == leg])
for cult in ["Maize", "Sorghum", "Millet", "Wheat", "Cotton"]:
    linha(f"amplo | cultura seguinte = {cult}", an2[an2.SubEff == cult])
print("  -- comparacao: mesmas combinacoes fora das zonas secas quentes (AI >= 0,65 ou MAT < 20)")
fora = z[~z.index.isin(an2.index)]
linha("fora | milho apos qualquer leguminosa, N <= 50", fora[(fora.SubEff == "Maize") & (fora.NFR <= 50)])
linha("dentro (amplo) | milho apos qualquer leguminosa, N <= 50", an2[(an2.SubEff == "Maize") & (an2.NFR <= 50)])
linha("fora | milho, N > 100", fora[(fora.SubEff == "Maize") & (fora.NFR > 100)])

# A4 meta-regressao
titulo("A4. Meta-regressao WLS (peso = replicas), erro-padrao agrupado por sitio")
m = z.copy()
m["N50"] = m.NFR / 50.0
m["seco"] = (m.AI < 0.5).astype(float)
m["subumido"] = ((m.AI >= 0.5) & (m.AI < 0.65)).astype(float)
m["quente"] = (m.MAT >= 20).astype(float)
m["milho"] = (m.SubEff == "Maize").astype(float)
m["sorgo_milheto"] = m.SubEff.isin(["Sorghum", "Millet"]).astype(float)
m["irrig"] = (m.IG == "yes").astype(float)
m["irrig_na"] = m.IG.isna().astype(float)
m["adubo_verde"] = (m.PreLegPur == "GRM").astype(float)
m["forrag"] = (m.PreLegPur == "Forage").astype(float)


def wls(form_cols, dados, rot):
    X = sm.add_constant(dados[form_cols])
    fit = sm.WLS(dados.yi, X, weights=dados.wgt).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(dados.sitio)[0]})
    print(f"  [{rot}] n={len(dados)}, sitios={dados.sitio.nunique()}, R2={fit.rsquared:.3f}")
    for c in fit.params.index:
        b, se = fit.params[c], fit.bse[c]
        print(f"     {c:<16s} b={b:+.4f} (lnRR)  EP={se:.4f}  p={fit.pvalues[c]:.3f}   ~ {pct(b):+.1f}% (multiplicativo)")
    return fit


f1 = wls(["N50", "CD2"], m, "M1 so N e diversidade (os 2 moderadores principais do artigo)")
f2 = wls(["N50", "CD2", "seco", "subumido", "quente", "milho", "sorgo_milheto", "irrig", "irrig_na", "adubo_verde", "forrag"], m,
         "M2 + aridez, calor, cultura, irrigacao, finalidade da leguminosa")
m["seco_x_N50"] = m.seco * m.N50
m["quente_x_seco"] = m.quente * m.seco
f3 = wls(["N50", "CD2", "seco", "subumido", "quente", "quente_x_seco", "seco_x_N50", "milho", "sorgo_milheto", "irrig", "irrig_na",
          "adubo_verde", "forrag"], m, "M3 + interacoes seco x N e seco x quente")

# A5 teste de transferencia
titulo("A5. Teste de transferencia: modelo SEM aridez ajustado fora do analogo preve o analogo?")
cols_t = ["N50", "CD2", "milho", "sorgo_milheto", "adubo_verde", "forrag"]
mask_an = (m.AI < 0.65) & (m.MAT >= 20)
for rotulo, mask in [("analogo amplo (AI<0,65 e MAT>=20)", mask_an),
                     ("analogo estrito (AI 0,2-0,5 e MAT>=20)", (m.AI >= 0.2) & (m.AI < 0.5) & (m.MAT >= 20)),
                     ("semiarido qualquer temperatura (AI 0,2-0,5)", (m.AI >= 0.2) & (m.AI < 0.5)),
                     ("Africa inteira (controle positivo de baixo insumo)", m.Continent == "Africa")]:
    tr, te = m[~mask], m[mask]
    if te.sitio.nunique() < 3:
        print(f"  {rotulo}: poucos sitios ({te.sitio.nunique()})")
        continue
    X = sm.add_constant(tr[cols_t])
    fit = sm.WLS(tr.yi, X, weights=tr.wgt).fit()
    te = te.assign(pred=fit.predict(sm.add_constant(te[cols_t], has_constant="add")))
    te = te.assign(res=te.yi - te.pred)
    e_obs, lo_o, hi_o, k = boot_sitio(te)
    e_pred = media_pond(te.pred.values, te.wgt.values)
    e_res, lo_r, hi_r, _ = boot_sitio(te, col_y="res")
    print(f"  {rotulo}: sitios={k}, n={len(te)} | observado {pct(e_obs):+.1f}% [{pct(lo_o):+.1f}, {pct(hi_o):+.1f}] | "
          f"previsto pelos moderadores globais {pct(e_pred):+.1f}% | residuo (obs - prev) {e_res:+.3f} lnRR "
          f"IC95 [{lo_r:+.3f}, {hi_r:+.3f}] -> {'TRANSFERE (IC do residuo cruza 0)' if lo_r <= 0 <= hi_r else 'NAO transfere (vies sistematico)'}")

# A6 irrigacao
titulo("A6. Irrigacao dentro das zonas secas (AI < 0,5): o ensaio irrigado nao e analogo do sequeiro")
sec = z[z.AI < 0.5]
for ig in ["yes", "no"]:
    linha(f"AI<0,5 | irrigado = {ig}", sec[sec.IG == ig])
linha("AI<0,5 | irrigacao nao informada", sec[sec.IG.isna()])

# A7 duracao
titulo("A7. Duracao: ciclo de rotacao (RC) - o efeito cresce com o tempo?")
for a, b, rot in [(0, 1.5, "1o ciclo"), (1.5, 3.5, "2o-3o ciclo"), (3.5, 10.5, "4o-10o ciclo"), (10.5, 999, ">10 ciclos")]:
    linha(f"RC {rot}", z[(z.RC >= a) & (z.RC < b)])
    linha(f"RC {rot} | AI<0,65", z[(z.RC >= a) & (z.RC < b) & (z.AI < 0.65)])

# A8 MAP nao e aridez
titulo("A8. Chuva anual (MAP) nao e aridez: mesma faixa de chuva, aridez diferente conforme o calor")
faixa = z[(z.MAP >= 700) & (z.MAP <= 1000)].drop_duplicates("sitio")
for t0, t1 in [(-5, 10), (10, 20), (20, 35)]:
    s = faixa[(faixa.MAT >= t0) & (faixa.MAT < t1)]
    if len(s):
        print(f"  MAP 700-1000 mm, MAT {t0}-{t1} C: {len(s)} sitios, AI mediana {s.AI.median():.2f} (p10 {s.AI.quantile(.1):.2f} - p90 {s.AI.quantile(.9):.2f})")

# =====================================================================================================
# B. KLUGER 2025 - Tabela S9
# =====================================================================================================
titulo("B. Kluger et al. 2025 - Tabela S9 (p.64 do PDF): efeito de 2 anos, diversificacao, chuva e temperatura")
from pypdf import PdfReader  # noqa: E402

kpdf = PROJ / "artigos" / "2025_Kluger_Precrop_payoffs_causal_machine_learning_reveals_large.pdf"
txt = PdfReader(str(kpdf)).pages[63].extract_text()
pat = re.compile(r"^(US|Canada|China|France)\s+(\S+)→(\S+)\s+\S+→\S+\s+([\d,]+)\s+([\d,]+)\s+(-?[\d.]+)%(\*?)\s+(NA|-?[\d.]+%\*?)\s+(-?[\d.]+)%(\*?)\s+(-?[\d.]+)%(\*?)\s*$")
rows = []
for ln in txt.splitlines():
    mm = pat.match(ln.strip())
    if mm:
        g = mm.groups()
        ed = None if g[7] == "NA" else float(g[7].rstrip("*").rstrip("%"))
        rows.append(dict(pais=g[0], pre=g[1], cult=g[2], eff2=float(g[5]), eff2_sig=g[6] == "*", effdiv=ed,
                         effdiv_sig=g[7].endswith("*"), bp=float(g[8]), bp_sig=g[9] == "*", bt=float(g[10]), bt_sig=g[11] == "*"))
k9 = pd.DataFrame(rows)
print(f"  linhas lidas da Tabela S9: {len(k9)} (o artigo diz 36 pares precrop-cultura-pais)")
grupo = {"S": "leguminosa", "Pe": "leguminosa", "Le": "leguminosa", "DB": "leguminosa",
         "C": "cereal", "WW": "cereal", "WB": "cereal", "UW": "cereal", "SW": "cereal", "Si": "cereal",
         "R": "folha larga", "Su": "folha larga", "Ch": "folha larga", "P": "pastagem", "F": "pousio"}
k9["grupo"] = k9.pre.map(grupo)
print(f"  efeito de 2 anos: mediana {k9.eff2.median():.2f}% (artigo p.33: 4,5%) | media {k9.eff2.mean():.2f}% | negativos {int((k9.eff2 < 0).sum())}")
print(f"  valores ordenados: {sorted(k9.eff2.tolist())}")
kd = k9.dropna(subset=["effdiv"])
print(f"  diversificar alem de 2 culturas (n={len(kd)}): mediana {kd.effdiv.median():.2f}% | media {kd.effdiv.mean():.2f}% | "
      f"razao media(2 anos)/media(diversificar) = {k9.eff2.mean() / kd.effdiv.mean():.1f} (artigo p.13: 3,7)")
print(f"  diversificar: negativos {int((kd.effdiv < 0).sum())} de {len(kd)}; negativos significativos {int(((kd.effdiv < 0) & kd.effdiv_sig).sum())}")
print("  heterogeneidade com CHUVA (p25->p75): ", f"positivos sig. {int(((k9.bp > 0) & k9.bp_sig).sum())}, "
      f"negativos sig. {int(((k9.bp < 0) & k9.bp_sig).sum())}, nao sig. {int((~k9.bp_sig).sum())}; mediana {k9.bp.median():+.2f} p.p.")
print("  heterogeneidade com TEMPERATURA: ", f"positivos sig. {int(((k9.bt > 0) & k9.bt_sig).sum())}, "
      f"negativos sig. {int(((k9.bt < 0) & k9.bt_sig).sum())}, nao sig. {int((~k9.bt_sig).sum())}")
print(k9.groupby("grupo").agg(n=("eff2", "size"), eff2_med=("eff2", "median"), chuva_med=("bp", "median"),
                              chuva_pos_sig=("bp", lambda s: int(((s > 0) & k9.loc[s.index, "bp_sig"]).sum())),
                              temp_med=("bt", "median"),
                              temp_neg_sig=("bt", lambda s: int(((s < 0) & k9.loc[s.index, "bt_sig"]).sum()))).to_string())
leg = k9[k9.grupo == "leguminosa"]
print("  leguminosas (linha a linha): ", leg[["pais", "pre", "cult", "eff2", "bp", "bp_sig", "bt", "bt_sig"]].to_dict("records"))

# =====================================================================================================
# C. FRANKE 2018 - Tabelas 2 e 3 (PMC)
# =====================================================================================================
titulo("C. Franke et al. 2018 (AGEE 261:172-185; PMC5946712) - Tabelas 2 e 3")
fdir = META / "franke2018_pmc"
fdir.mkdir(parents=True, exist_ok=True)
fxml = fdir / "franke2018.xml"
if not fxml.exists():
    import requests
    r = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5946712/fullTextXML", timeout=120)
    r.raise_for_status()
    fxml.write_bytes(r.content)
root = ET.parse(fxml).getroot()
tabs = {}
for tw in root.iter("table-wrap"):
    lab = tw.find("label")
    lab = lab.text.strip() if lab is not None else tw.get("id")
    linhas = []
    for tr in tw.iter("tr"):
        linhas.append([" ".join("".join(c.itertext()).split()) for c in tr])
    tabs[lab] = linhas
t3 = [r for r in tabs["Table 3"] if len(r) == 8 and re.match(r"^\d+$", r[1] or "")]
d3 = pd.DataFrame(t3, columns=["fator", "n", "cont", "apos_leg", "se_y", "resp", "se_resp", "p"])
for c in ["n", "cont", "apos_leg", "resp", "se_resp"]:
    d3[c] = pd.to_numeric(d3[c])
d3["rel_%"] = (d3.resp / d3.cont * 100).round(1)
d3["IC95_resp"] = d3.apply(lambda r: f"[{r.resp - 1.96 * r.se_resp:+.2f}, {r.resp + 1.96 * r.se_resp:+.2f}]", axis=1)
print(d3[["fator", "n", "cont", "apos_leg", "resp", "se_resp", "IC95_resp", "p", "rel_%"]].to_string(index=False))
inter = [r for r in tabs["Table 3"] if r and "x yield response" in r[0]]
print("  interacoes (p):", [(r[0], r[-1]) for r in inter])

# Tabela 2: blocos por zona
t2 = tabs["Table 2"]
zona, regs = None, []
for r in t2:
    if len(r) >= 1 and r[0] and all(x == "" for x in r[1:]) or (len(r) == 1):
        zona = r[0]
        continue
    if len(r) >= 10 and r[3] and re.match(r"^[\d.]+", r[4] or ""):
        ctrl = float(re.match(r"^[\d.]+", r[4]).group())
        for j, legn in zip(range(5, 10), ["cowpea", "groundnut", "soybean", "pigeonpea", "outra"]):
            for v in re.findall(r"(−?-?\d+)(?:\s*\(([^)]*)\))?", r[j] or ""):
                val = float(v[0].replace("−", "-"))
                regs.append(dict(zona=zona, fonte=r[0], pais=r[1], cereal=r[3], controle=ctrl, leg=legn if not v[1] else v[1], pct=val))
d2 = pd.DataFrame(regs)
print(f"  Tabela 2: {len(d2)} valores (% de aumento do cereal apos leguminosa, por estudo x leguminosa)")
print(d2.groupby("zona").pct.describe()[["count", "min", "25%", "50%", "75%", "max"]].round(0).to_string())
ss = d2[d2.zona.str.contains("Sudano", na=False)]
print(f"  Sudano-saheliana: controle (cereal continuo) mediana {ss.drop_duplicates(['fonte','pais','controle']).controle.median():.2f} t/ha; "
      f"aumento relativo mediana {ss.pct.median():.0f}% (min {ss.pct.min():.0f}, max {ss.pct.max():.0f}); "
      f"negativos {int((ss.pct < 0).sum())} de {len(ss)}")
from scipy.stats import spearmanr  # noqa: E402
rho, pv = spearmanr(d2.controle, d2.pct)
print(f"  Tabela 2 inteira: Spearman(rendimento do controle, % de aumento) = {rho:+.2f} (p={pv:.3g}); o texto diz que o ganho relativo cai com o controle")

# =====================================================================================================
# D. Raveloaritiana 2026 - aritmetica
# =====================================================================================================
titulo("D. Raveloaritiana & Wanger 2026 - o que e o '+189% de lucratividade em 20 anos' (p.4 do PDF)")
l20, l0 = 0.3633, 0.1259
print(f"  lnRR 20 anos = {l20} -> efeito absoluto exp-1 = {pct(l20):+.1f}% | lnRR curto prazo (<3 anos) = {l0} -> {pct(l0):+.1f}%")
print(f"  (lnRR20 / lnRR0 - 1) = {(l20 / l0 - 1) * 100:.0f}%  <- e ISTO que o artigo chama de '189%': aumento relativo do log da razao,")
print(f"  nao '+189% de lucro'. Em 20 anos a diversificacao da +{pct(l20):.0f}% de lucratividade contra +{pct(l0):.0f}% no curto prazo.")

# =====================================================================================================
# E. NOSSOS DADOS
# =====================================================================================================
titulo("E1. Aridez do Ceara pelo NASA POWER (P/ET0 FAO-56, celulas 0,5 x 0,625 grau) x cobertura da base de Zhao")
pw = pd.read_parquet(DADOS / "power" / "power_ce_indicadores_anuais.parquet")
pw = pw[(pw.no_ceara == True) & (pw.ano.between(1991, 2020))]  # noqa: E712
pc = pw.groupby(["lat", "lon"]).agg(P=("chuva_anual_mm", "mean"), ET0=("ET0_anual_mm", "mean")).reset_index()
pc["AI"] = pc.P / pc.ET0
print(f"  celulas no Ceara: {len(pc)} | P media {pc.P.median():.0f} mm | ET0 {pc.ET0.median():.0f} mm | AI mediana {pc.AI.median():.2f} "
      f"(p10 {pc.AI.quantile(.1):.2f}, p90 {pc.AI.quantile(.9):.2f})")
print("  classes de aridez das celulas:", pd.cut(pc.AI, cortes, labels=nomes, right=False).value_counts().to_dict())
ai_lo, ai_hi = pc.AI.quantile(.1), pc.AI.quantile(.9)
cob = z[(z.AI >= ai_lo) & (z.AI <= ai_hi) & (z.MAT >= 24)]
print(f"  Zhao com AI na faixa p10-p90 do Ceara ({ai_lo:.2f}-{ai_hi:.2f}) E MAT >= 24 C (Ceara ~26-27 C): {len(cob)} obs "
      f"({len(cob) / len(z) * 100:.1f}%), {cob.sitio.nunique()} sitios, paises {sorted(cob.Country.unique())}")
if len(cob):
    linha("efeito nessa faixa", cob)
print("  CUIDADO: o AI de Zhao vem do WorldClim/CGIAR e o nosso do POWER; a comparacao e de ordem de grandeza.")

titulo("E2. PAM Ceara: quanto do tempo o rendimento 'colhido' esconde a perda (Zhao excluiu rendimento zero, p.7)")
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.ano.between(1990, 2025)]
for prefixo, rot in [("Milho (em", "milho"), ("Feij", "feijao")]:
    s = pam[pam.produto.str.startswith(prefixo) & (pam.area_plantada_ha > 50)].copy()
    s["sobrev"] = (s.area_colhida_ha / s.area_plantada_ha).clip(0, 1)
    s["rend_plantado"] = s.producao_t * 1000 / s.area_plantada_ha
    s["rend_colhido"] = np.where(s.area_colhida_ha > 0, s.producao_t * 1000 / s.area_colhida_ha.replace(0, np.nan), np.nan)
    perda_total = (s.sobrev < 0.05).mean() * 100
    perda_metade = (s.sobrev < 0.5).mean() * 100
    razao = s.rend_plantado.sum() / s.rend_colhido.fillna(0).sum()
    print(f"  {rot}: {len(s)} municipio-anos (area plantada > 50 ha) | perda quase total (colhida < 5% da plantada) {perda_total:.1f}% | "
          f"perda >= metade {perda_metade:.1f}% | rendimento por ha plantado / por ha colhido = {razao:.2f}")
    print(f"     rendimento colhido mediana {np.nanmedian(s.rend_colhido):.0f} kg/ha; por ha plantado mediana {s.rend_plantado.median():.0f} kg/ha")
    anos = s.groupby("ano").apply(lambda g: (g.sobrev < 0.5).mean() * 100)
    print(f"     anos com >= 40% dos municipios perdendo metade ou mais: {anos[anos >= 40].index.tolist()}")
    # a perda no PAM do Ceara aparece como rendimento baixo, nao como area perdida: medir a quase falha pelo rendimento
    s["rel"] = s.rend_plantado / s.groupby("cod_local").rend_plantado.transform("median")
    quase = (s.rel < 0.25).mean() * 100
    s = s.sort_values("rend_plantado")
    acima = s[s.rel >= 1].rend_plantado.sum() / s.rend_plantado.sum() * 100
    print(f"     quase falha (rendimento por ha plantado < 25% da mediana do municipio): {quase:.1f}% dos municipio-anos | "
          f"anos acima da mediana do municipio somam {acima:.0f}% de todo o rendimento acumulado")
    print(f"     -> um ganho RELATIVO constante (ex. +24%) entrega {acima:.0f}% do seu ganho ABSOLUTO nos anos bons; nos anos de quase falha, ~0 kg/ha")
print("  Leitura: no PAM do Ceara a perda quase nunca aparece como area nao colhida; aparece como rendimento baixo.")
print("  O efeito multiplicativo das meta-analises (Zhao excluiu rendimento zero) entrega pouco kg/ha justamente nos anos secos.")

print(f"\nTempo total: {_time.time() - T0:.1f} s")
