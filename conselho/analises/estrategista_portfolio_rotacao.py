"""Estrategista - Analise 3: a rotacao como carteira de risco. Milho e feijao quebram juntos?

Pergunta: as culturas do sertao quebram no mesmo ano (correlacao alta = rotacao milho<->feijao nao protege)?
Qual o "pior decil" (P10) e a perda em ano seco de cada cultura e de misturas simples?

Dados: derivados/ibge_pam_mun_anual.parquet (184 municipios, 1998-2025), derivados/imerg_ce_mensal.parquet
(tercil seco da quadra fev-mai do Ceara).
Metrica: razao do rendimento para a mediana do proprio municipio (tira solo, tecnologia media e unidade).
Mistura com pesos iguais em razao = renda relativa se o preco ficasse constante (simplificacao declarada).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from comum import DERIV

pd.set_option("display.width", 220)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[(pam.ano >= 1998) & (pam.ano <= 2025)]
CULT = {"milho": "Milho (em", "feijao": "Feij", "mandioca": "Mandioca", "sorgo": "Sorgo", "algodao_herb": "Algod\u00e3o herb",
        "castanha_caju": "Castanha de caju", "cana": "Cana-de-a", "arroz": "Arroz", "amendoim": "Amendoim", "melancia": "Melancia",
        "banana": "Banana"}
alvos = {}
for nome, pref in CULT.items():
    q = pam[pam.produto.str.startswith(pref) & (pam.area_colhida_ha >= 50) & (pam.rendimento_kg_ha > 0)][["cod_local", "ano", "rendimento_kg_ha"]]
    if len(q) < 100:
        print("pouco dado:", nome, len(q))
        continue
    q["razao"] = q.rendimento_kg_ha / q.groupby("cod_local").rendimento_kg_ha.transform("median")
    alvos[nome] = q.set_index(["cod_local", "ano"]).razao
Y = pd.DataFrame(alvos)

im = pd.read_parquet(DERIV / "imerg_ce_mensal.parquet")
im["data"] = pd.to_datetime(im.data)
ip = im[im.variavel == "precip_total"].set_index("data")["valor"]
f = ip[ip.index.month.isin([2, 3, 4, 5])]
fmam = f.groupby(f.index.year).sum()[f.groupby(f.index.year).count() == 4].loc[1998:2025]
seco = set(fmam[fmam <= fmam.quantile(1 / 3)].index)
print("Anos do tercil seco (IMERG FMAM CE):", sorted(seco))
anoY = Y.index.get_level_values("ano")

linhas = []
for c in Y.columns:
    s = Y[c].dropna()
    a = s.index.get_level_values("ano")
    par = Y[["milho", c]].dropna()
    linhas.append({"cultura": c, "municipio_ano": len(s), "P10": s.quantile(0.10), "P(quebra<0.5)": (s < 0.5).mean(),
                   "mediana_ano_seco": s[np.isin(a, list(seco))].median(), "mediana_ano_nao_seco": s[~np.isin(a, list(seco))].median(),
                   "spearman_com_milho": par.milho.corr(par[c], method="spearman") if c != "milho" else 1.0, "n_par_milho": len(par)})
T = pd.DataFrame(linhas).sort_values("P10", ascending=False)
print("\n=== Risco por cultura (razao do rendimento / mediana municipal, 1998-2025) ===")
print(T.round(2).to_string(index=False))

# carteiras simples nos municipio-ano onde as 3 culturas principais existem
B = Y[["milho", "feijao", "mandioca"]].dropna()
cart = {
    "100% milho": B.milho,
    "100% feijao": B.feijao,
    "milho+feijao (50/50)": B[["milho", "feijao"]].mean(axis=1),
    "milho+mandioca (50/50)": B[["milho", "mandioca"]].mean(axis=1),
    "milho+feijao+mandioca (1/3)": B.mean(axis=1),
}
a = B.index.get_level_values("ano")
L = []
for k, s in cart.items():
    cvar = s[s <= s.quantile(0.10)].mean()
    L.append({"carteira": k, "n": len(s), "P10": s.quantile(0.10), "CVaR10 (media do pior decil)": cvar,
              "P(<0.5)": (s < 0.5).mean(), "mediana_ano_seco": s[np.isin(a, list(seco))].median()})
print("\n=== Carteiras (mesmos municipio-ano, n comum) ===")
print(pd.DataFrame(L).round(3).to_string(index=False))

# com sorgo onde existir
B2 = Y[["milho", "feijao", "sorgo"]].dropna()
if len(B2) > 50:
    print(f"\nCom sorgo (n={len(B2)} municipio-ano):")
    for k, s in {"100% milho": B2.milho, "milho+feijao": B2[["milho", "feijao"]].mean(axis=1), "milho+sorgo": B2[["milho", "sorgo"]].mean(axis=1),
                 "sorgo": B2.sorgo}.items():
        print(f"  {k:14s} P10={s.quantile(0.1):.2f}  P(<0.5)={(s < 0.5).mean():.1%}")
    print("  Spearman milho x sorgo:", round(B2.milho.corr(B2.sorgo, method="spearman"), 2))

# ano 2012 e 2016: fracao de municipios com quebra por cultura
for ano in (2012, 2016):
    s = Y[anoY == ano]
    print(f"\n{ano}: fracao de municipios com rendimento < 50% da mediana:",
          {c: round((s[c].dropna() < 0.5).mean(), 2) for c in ["milho", "feijao", "mandioca", "sorgo", "castanha_caju", "cana"] if c in s and s[c].notna().sum() >= 5},
          "| n:", {c: int(s[c].notna().sum()) for c in ["milho", "feijao", "mandioca", "sorgo", "castanha_caju", "cana"] if c in s})
