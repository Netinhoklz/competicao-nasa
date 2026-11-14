"""Economista agrícola — Rodada 2 (debate): checagens rápidas de afirmações dos outros especialistas.

A) Gatilho tipo Garantia-Safra: o ISNA do balanço FAO-56 (agronomo_isna_mun_ano.parquet) reduz o risco de base
   em relação à chuva de fev–mai? (o agrônomo propôs isso como ideia solta; ninguém testou contra a perda da cesta)
B) Quanto vale em R$/ha a previsão sazonal do cientista do clima (V da regra fixa, modelo custo–perda)?
C) Falácia de composição: o preço implícito municipal da mandioca cai quando a produção do município sobe?
   (teto de participação para a carteira do pesquisador de IA, que manda 56% para mandioca)
D) Sorgo: preço relativo ao milho e renda por ha nos município-anos com as duas culturas (várias propostas empurram sorgo)
E) Números divergentes entre as propostas: ONI de 2026 (2,46 / 2,31 / 2,14) e ureia/milho (4,0 contra o último mês)
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
SAI = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas/"

m = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
m["cod"] = m.cod_local.astype(str)

# ============ A) gatilho por ISNA x chuva
CESTA = ["Milho (em grão)", "Feijão (em grão)", "Mandioca", "Arroz (em casca)", "Algodão herbáceo (em caroço)"]
d = m[m.produto.isin(CESTA) & m.ano.between(1998, 2025)]
rec = d[d.ano.between(2019, 2025)]
preco = rec.groupby("produto").valor_mil_moeda.sum() / rec.groupby("produto").producao_t.sum()
d = d.assign(v=d.producao_t * d.produto.map(preco))
V = d.groupby(["cod", "ano"]).v.sum().rename("valor").reset_index()
perdas = []
for c, g in V.groupby("cod"):
    g = g[g.valor > 0]
    if len(g) < 20:
        continue
    t = g.ano.values - 1998
    sl, ic, _, _ = stats.theilslopes(np.log(g.valor.values), t)
    perdas.append(pd.DataFrame({"cod": c, "ano": g.ano.values, "razao": g.valor.values / np.exp(ic + sl * t)}))
L = pd.concat(perdas)
I = pd.read_parquet(SAI + "agronomo_isna_mun_ano.parquet")
I["cod"] = I.cod.astype(str)
D = I.merge(L, on=["cod", "ano"]).dropna(subset=["isna_flor_milho", "P_fmam", "razao"])
D["P_rel"] = D.P_fmam / D.groupby("cod").P_fmam.transform("mean")
D["isna_min"] = D[["isna_flor_milho", "isna_flor_caupi"]].min(axis=1)
anos = D.ano.values
print(f"A) Painel gatilho: {len(D)} município-anos, {D.cod.nunique()} municípios")

for lim, rot in [(0.5, "perda >= 50%"), (0.6, "perda >= 40% (Lei 15.236/2025)")]:
    y = (D.razao <= lim).astype(int).values
    taxa = y.mean()
    sc = {
        "chuva fev–mai relativa (municipal)": -D.P_rel.values,
        "ISNA floração milho": -D.isna_flor_milho.values,
        "ISNA ciclo milho": -D.isna_ciclo_milho.values,
        "mín(ISNA flor milho, caupi)": -D.isna_min.values,
    }
    for nome, cols in [("logística chuva + veranico", ["P_rel", "dias_veranico", "veranico_max"]),
                       ("logística ISNA + chuva + veranico", ["P_rel", "dias_veranico", "veranico_max", "isna_flor_milho", "isna_ciclo_milho", "isna_flor_caupi"])]:
        s = np.zeros(len(D))
        for a in np.unique(anos):
            tr, te = anos != a, anos == a
            lg = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(D.loc[tr, cols], y[tr])
            s[te] = lg.predict_proba(D.loc[te, cols])[:, 1]
        sc[nome] = s
    ruins = [a for a in np.unique(anos) if 0.1 <= y[anos == a].mean() <= 0.9]
    linhas = []
    for nome, s in sc.items():
        g = s >= np.quantile(s, 1 - taxa)
        linhas.append({"gatilho": nome, "AUC": round(roc_auc_score(y, s), 3),
                       "AUC dentro do ano": round(np.mean([roc_auc_score(y[anos == a], s[anos == a]) for a in ruins]), 3),
                       "perdas pagas": round(g[y == 1].mean(), 3), "perda sem pagamento": round((~g & (y == 1)).mean(), 3),
                       "pagamento sem perda": round((g & (y == 0)).mean(), 3)})
    print(f"\n  Alvo {rot}: frequência {taxa:.3f} (gatilho calibrado para pagar na mesma frequência; LOYO nas logísticas)")
    print(pd.DataFrame(linhas).to_string(index=False))
# índice anual estadual
fr = D.groupby("ano").agg(perda=("razao", lambda r: (r <= 0.5).mean()), frac_isna=("isna_flor_milho", lambda r: (r < 0.5).mean()),
                          chuva=("P_rel", "mean"))
print("\n  Estado, por ano: Spearman fração em perda × fração ISNA<0,5 =",
      round(stats.spearmanr(fr.perda, fr.frac_isna).correlation, 2), "| × chuva média relativa =",
      round(stats.spearmanr(fr.perda, -fr.chuva).correlation, 2))

# ============ B) valor da previsão em R$/ha (cientista do clima, V regra fixa em 01/fev, quebra do milho)
ce = pd.read_parquet(DERIV / "ibge_pam_ce_anual.parquet")
ce["ano"] = pd.to_datetime(ce.data).dt.year
W = ce.pivot_table(index=["produto", "ano"], columns="variavel", values="valor")
mz = W.loc["Milho (em grão)"].loc[1975:2025]
rend = mz.producao_t * 1000 / mz.area_plantada_ha.where(mz.area_plantada_ha > 0, mz.area_colhida_ha)
ref = rend.rolling(9, center=True, min_periods=5).median()
raz = rend / ref
queb = raz[raz <= 0.70]
p_mz = float((mz.valor_mil_moeda * 1000 / mz.producao_t).loc[2019:2025].median())  # R$/t
rend_med = float(rend.loc[2015:2025].median())
receita = rend_med * p_mz / 1000
falta = float((1 - queb).mean())
Lha = falta * receita
s = 0.30
print(f"\nB) Milho CE: rendimento mediano 2015–25 (área plantada) {rend_med:.0f} kg/ha × R$ {p_mz:.0f}/t = receita R$ {receita:.0f}/ha;"
      f" anos de quebra (≤ 70% da mediana móvel de 9 anos): {len(queb)} de {raz.notna().sum()}, perda média {falta:.0%}"
      f" → L ≈ R$ {Lha:.0f}/ha")
for alfa, Vfix in [(0.2, 0.23), (0.33, 0.39), (0.5, 0.38)]:
    C = alfa * Lha
    Ecl = min(C, s * Lha)
    Epf = s * C
    ganho = Vfix * (Ecl - Epf)
    print(f"  α = {alfa}: C = R$ {C:.0f}/ha, ganho esperado com a previsão = V·(E_clim − E_perfeito) = R$ {ganho:.0f}/ha/ano "
          f"(V = {Vfix}); 3 ha → R$ {3 * ganho:.0f}/família/ano")

# ============ C) falácia de composição: preço implícito municipal × produção municipal
print("\nC) Preço implícito municipal (valor/produção) relativo ao estado no ano × produção municipal relativa (efeito fixo de município)")
for prod in ["Mandioca", "Feijão (em grão)", "Milho (em grão)"]:
    g = m[(m.produto == prod) & m.ano.between(1998, 2025) & (m.producao_t > 0) & (m.valor_mil_moeda > 0)].copy()
    g["p"] = g.valor_mil_moeda / g.producao_t
    g["p_rel"] = np.log(g.p / g.groupby("ano").p.transform("median"))
    g["q_rel"] = np.log(g.producao_t / g.groupby("cod").producao_t.transform("median"))
    g["y_rel"] = np.log(g.rendimento_kg_ha.clip(lower=1) / g.groupby("cod").rendimento_kg_ha.transform("median"))
    for v in ["p_rel", "q_rel", "y_rel"]:
        g[v + "_w"] = g[v] - g.groupby("cod")[v].transform("mean")
    g = g.replace([np.inf, -np.inf], np.nan).dropna(subset=["p_rel_w", "q_rel_w"])
    b = stats.linregress(g.q_rel_w, g.p_rel_w)
    sd_p = g.groupby("cod").p_rel.std().median()
    # choque local de produção (fora do choque do ano): desconta a média do estado no ano
    g["q_loc"] = g.q_rel_w - g.groupby("ano").q_rel_w.transform("mean")
    b2 = stats.linregress(g.q_loc, g.p_rel_w)
    print(f"  {prod:18s} n={len(g):5d} | elasticidade preço/produção (dentro do município) {b.slope:+.3f} (r {b.rvalue:+.2f}) | "
          f"só choque local (fora do ano) {b2.slope:+.3f} (r {b2.rvalue:+.2f}) | dp mediano do log-preço relativo {sd_p:.3f}")

# ============ D) sorgo × milho
so = m[(m.produto == "Sorgo (em grão)") & m.ano.between(1998, 2025) & (m.area_colhida_ha >= 50)]
mi = m[(m.produto == "Milho (em grão)") & m.ano.between(1998, 2025) & (m.area_colhida_ha >= 50)]
j = so.merge(mi, on=["cod", "ano"], suffixes=("_s", "_m"))
j = j[(j.producao_t_s > 0) & (j.producao_t_m > 0)]
j["preco_rel"] = (j.valor_mil_moeda_s / j.producao_t_s) / (j.valor_mil_moeda_m / j.producao_t_m)
j["rec_s"] = j.valor_mil_moeda_s * 1000 / j.area_colhida_ha_s
j["rec_m"] = j.valor_mil_moeda_m * 1000 / j.area_colhida_ha_m
print(f"\nD) Sorgo × milho nos mesmos município-anos (área colhida ≥ 50 ha): n = {len(j)}, municípios = {j.cod.nunique()}")
print(f"  preço sorgo/milho: mediana {j.preco_rel.median():.2f} (p25 {j.preco_rel.quantile(.25):.2f}, p75 {j.preco_rel.quantile(.75):.2f})")
print(f"  rendimento sorgo/milho: mediana {(j.rendimento_kg_ha_s / j.rendimento_kg_ha_m).median():.2f}")
print(f"  receita bruta/ha (R$ correntes) sorgo/milho: mediana {(j.rec_s / j.rec_m).median():.2f}")
cs = m[(m.produto == "Sorgo (em grão)") & m.ano.between(2015, 2025)].groupby("ano").area_colhida_ha.sum()
print("  área colhida de sorgo no CE (ha):", cs.round(0).astype(int).to_dict())

# ============ E) números divergentes
idx = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
oni = idx["ONI"].loc["2026-06-01":]
print("\nE) ONI (série mensal da NOAA CPC no arquivo; cada valor já é média móvel de 3 meses):", oni.round(2).to_dict())
print(f"  último valor (rotulado set/2026) = {oni.iloc[-1]:.2f} | média ago–set = {oni.loc['2026-08-01':].mean():.2f}"
      f" | média jul–set = {oni.loc['2026-07-01':'2026-09-01'].mean():.2f}  → três números para o mesmo fato")
pk = pd.read_parquet(DERIV / "mercado_precos_mensal.parquet").pivot_table(index="data", columns="commodity", values="preco")
r = (pk["Urea"] / pk["Maize"]).dropna()
print(f"  ureia/milho: 2026 por mês {r.loc['2026'].round(2).to_dict()} | média 2000–2020 {r.loc['2000':'2020'].mean():.2f}")
