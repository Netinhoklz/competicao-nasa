"""Economista agrícola — Análise A2: hedge natural de preço por cultura + valor do nitrogênio em kg de milho.

Pergunta 1: quando a safra do Ceará quebra, o preço local sobe e compensa (hedge natural)? Para quais culturas?
- Preço implícito no Ceará = valor da produção / quantidade (IBGE PAM estadual, ibge_pam_ce_anual), 1995–2025 (pós-Real).
- Dividido pelo preço ao produtor do Brasil no mesmo ano (FAOSTAT, LCU/t): a razão elimina a inflação e o ciclo nacional,
  e mede o "prêmio local".
- Anomalia de rendimento = rend / tendência de Theil-Sen em log.
- Elasticidade: log(prêmio local) ~ log(anomalia de rendimento). beta < 0 = preço sobe quando a safra quebra.
- Compara o risco da renda (rendimento × prêmio local) com o risco do rendimento puro.

Pergunta 2: quanto milho o agricultor precisa vender para comprar nitrogênio, ao longo do tempo?
- Pink Sheet (Banco Mundial): ureia (46% N) e milho, USD/t. kg de milho por kg de N = (ureia/0,46)/milho.
- Compara com o rendimento mediano do milho no Ceará (PAM) e com o prêmio da leguminosa antecessora de Zhao et al. 2022.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)

ce = pd.read_parquet(DERIV / "ibge_pam_ce_anual.parquet")
ce["ano"] = pd.to_datetime(ce.data).dt.year
W = ce.pivot_table(index=["produto", "ano"], columns="variavel", values="valor")
fao = pd.read_parquet(DERIV / "faostat_precos_produtor.parquet")
br = fao[(fao.Area == "Brazil") & (fao.Months == "Annual value") & (fao.Element == "Producer Price (LCU/tonne)")]
br = br.pivot_table(index="Year", columns="Item", values="Value")
PAR = {
    "Milho (em grão)": "Maize (corn)", "Feijão (em grão)": "Beans, dry", "Mandioca": "Cassava, fresh",
    "Castanha de caju": "Cashew nuts, in shell", "Arroz (em casca)": "Rice", "Algodão herbáceo (em caroço)": "Seed cotton, unginned",
    "Mamona (baga)": "Castor oil seeds", "Cana-de-açúcar": "Sugar cane", "Banana (cacho)": "Bananas",
}
linhas = []
series = {}
for pt, en in PAR.items():
    if en not in br.columns or pt not in W.index.get_level_values(0):
        continue
    s = W.loc[pt].loc[1995:2025]
    s = s[(s.producao_t > 0) & (s.area_colhida_ha > 0)]
    p_ce = s.valor_mil_moeda * 1000 / s.producao_t  # R$/t
    rend = s.producao_t / s.area_colhida_ha
    j = pd.concat([p_ce.rename("p_ce"), br[en].rename("p_br"), rend.rename("rend")], axis=1).dropna()
    if len(j) < 15:
        continue
    t = j.index.values - 1995
    sl, ic, _, _ = stats.theilslopes(np.log(j.rend.values), t)
    j["anom"] = j.rend / np.exp(ic + sl * t)
    j["premio"] = j.p_ce / j.p_br
    j["premio_rel"] = j.premio / j.premio.median()
    b, a, r, p, se = stats.linregress(np.log(j.anom), np.log(j.premio_rel))
    renda = j.anom * j.premio_rel
    k = max(1, int(round(0.1 * len(j))))
    linhas.append({
        "cultura": pt, "anos": len(j), "elasticidade preço local/rend.": round(b, 2), "p": round(p, 3), "r": round(r, 2),
        "CV rendimento": round(j.anom.std() / j.anom.mean(), 2), "CV renda (c/ preço local)": round(renda.std() / renda.mean(), 2),
        "CVaR10 rend./média": round(np.sort(j.anom)[:k].mean() / j.anom.mean(), 2),
        "CVaR10 renda/média": round(np.sort(renda)[:k].mean() / renda.mean(), 2),
        "prêmio no pior ano de rend.": round(float(j.premio_rel.loc[j.anom.idxmin()]), 2), "pior ano": int(j.anom.idxmin()),
    })
    series[pt] = j
T = pd.DataFrame(linhas).sort_values("elasticidade preço local/rend.")
print("Hedge natural (Ceará / Brasil, 1995–2025):")
print(T.to_string(index=False))

for pt in ["Milho (em grão)", "Feijão (em grão)", "Mandioca"]:
    if pt in series:
        j = series[pt]
        print(f"\n{pt}: anos de seca 2012–2016 — anomalia de rendimento e prêmio local relativo")
        print(j.loc[2010:2018, ["anom", "premio_rel"]].round(2).T.to_string())

# ---- Pergunta 2: nitrogênio em kg de milho
pk = pd.read_parquet(DERIV / "mercado_precos_mensal.parquet").pivot_table(index="data", columns="commodity", values="preco")
kgN = (pk["Urea"] / 0.46) / pk["Maize"]
kgN = kgN.dropna()
print("\nkg de milho para comprar 1 kg de N (via ureia, preço internacional):")
print(f"  média 2000–2020 = {kgN.loc['2000':'2020'].mean():.2f}; 2021–22 = {kgN.loc['2021':'2022'].mean():.2f}; "
      f"máximo = {kgN.max():.2f} em {kgN.idxmax():%Y-%m}; último = {kgN.iloc[-1]:.2f} em {kgN.index[-1]:%Y-%m}")
print("  2026 por mês:", kgN.loc["2026"].round(2).to_dict())
razao = (pk["Urea"] / pk["Maize"]).dropna()
print(f"  razão ureia/milho: último = {razao.iloc[-1]:.2f} ({razao.index[-1]:%Y-%m}); 2026 máx = {razao.loc['2026'].max():.2f}")

mz = W.loc["Milho (em grão)"]
rend_mz = (mz.producao_t * 1000 / mz.area_colhida_ha).loc[2015:2025]
med = float(rend_mz.median())
print(f"\nRendimento do milho no Ceará (PAM estadual) 2015–2025: mediana {med:.0f} kg/ha; faixa {rend_mz.min():.0f}–{rend_mz.max():.0f}")
for dose in (30, 60):
    for nome, v in (("média 2000–2020", kgN.loc['2000':'2020'].mean()), ("último", kgN.iloc[-1]), ("pico 2026", kgN.loc['2026'].max())):
        print(f"  dose ilustrativa {dose} kg N/ha a preço {nome}: {dose * v:.0f} kg de milho = {dose * v / med:.0%} da colheita mediana")

# prêmio da leguminosa antecessora (Zhao et al. 2022: +32% em ambientes de baixa produtividade; +20% média)
p_mz = float((mz.valor_mil_moeda * 1000 / mz.producao_t).loc[2019:2025].median())
for b in (0.20, 0.32):
    print(f"  Zhao 2022 b={b:.2f}: +{b * med:.0f} kg/ha de milho = R$ {b * med * p_mz / 1000:.0f}/ha (preço implícito CE 2019–25 R$ {p_mz:.0f}/t)")
