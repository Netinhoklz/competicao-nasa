"""(1) Como o leque do rendimento estreita nos portões (chuva IMERG desde fev, meses inteiros: fev–mar ~ 31/mar; fev–abr ~ 30/abr).
(2) Persistência: chance de ≥ 1 quebra em 3 anos, independente contra blocos de 3 anos reais.
(3) Preço deflacionado: dispersão e relação com o rendimento (o preço protege?)."""
import numpy as np, pandas as pd
D = "c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados/"
P = pd.read_parquet("E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet")
REF = pd.read_parquet(D + "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
IM = pd.read_parquet(D + "ibge_ne_mun_imerg_mensal.parquet")
IM["ano"] = IM.data.dt.year; IM["mes"] = IM.data.dt.month
IM = IM[IM.ano <= 2025]
quadra_norte = None
fm = IM[IM.mes.isin([2, 3])].groupby(["cod_mun", "ano"]).precip_mm.sum().rename("fm")
fa = IM[IM.mes.isin([2, 3, 4])].groupby(["cod_mun", "ano"]).precip_mm.sum().rename("fa")
C = pd.concat([fm, fa], axis=1).reset_index()
for c in ["fm", "fa"]:
    C[c + "_rel"] = C[c] / C.groupby("cod_mun")[c].transform("median")
v = P[(P.area_plantada_ha > 0) & P.produto.isin(["Milho", "Feijão"])].copy()
v["med"] = v.groupby(["produto", "cod_mun"]).rend_plantado_kg_ha.transform("median")
v = v[v.groupby(["produto", "cod_mun"]).ano.transform("size") >= 20]
v["R"] = v.rend_plantado_kg_ha / v.med
v = v.merge(C, on=["cod_mun", "ano"], how="inner")
# só municípios de quadra do norte (fev–mai): proxy = semiárido e UF no norte do NE
v["semi"] = REF.loc[v.cod_mun, "semiarido_2022"].values
v = v[v.semi & v.uf.isin(["CE", "RN", "PB", "PI", "PE"])]
print("n município-anos (milho+feijão, semiárido CE/RN/PB/PI/PE):", len(v))
for prod in ["Milho", "Feijão"]:
    s = v[v.produto == prod]
    print(f"\n== {prod}: quantis da razão ao normal (R) e P(quebra = R<0,5), por informação disponível")
    lin = [("novembro (clima)", s.R)]
    lin += [("nov + ONI ASO>=1 (98,16,24)", s[s.ano.isin([1998, 2016, 2024])].R)]
    for g, lab in [("fm_rel", "fev-mar"), ("fa_rel", "fev-abr")]:
        lin += [(f"{lab} chuva < 75%", s[s[g] < 0.75].R), (f"{lab} chuva 75-100%", s[(s[g] >= 0.75) & (s[g] < 1)].R),
                (f"{lab} chuva >= 100%", s[s[g] >= 1].R)]
    for lab, x in lin:
        q = x.quantile([0.1, 0.2, 0.5, 0.8, 0.9]).values
        print(f"{lab:32s} n={len(x):6d} anos={s.loc[x.index].ano.nunique():2d} P10={q[0]:.2f} P20={q[1]:.2f} P50={q[2]:.2f} P80={q[3]:.2f} "
              f"P90={q[4]:.2f} P(quebra)={(x < 0.5).mean():.2f}")

# (2) persistência: milho, por município, 1998–2025
s = P[(P.produto == "Milho") & (P.area_plantada_ha > 0)].copy()
s["med"] = s.groupby("cod_mun").rend_plantado_kg_ha.transform("median")
s = s[s.groupby("cod_mun").ano.transform("size") >= 25]
s["qb"] = (s.rend_plantado_kg_ha < 0.5 * s.med).astype(float)
Q = s.pivot(index="cod_mun", columns="ano", values="qb")
p1 = Q.mean(1)
indep = 1 - (1 - p1) ** 3
win = [Q[[a, a + 1, a + 2]].max(1) for a in range(1998, 2024) if {a, a + 1, a + 2} <= set(Q.columns)]
blocos = pd.concat(win, axis=1).mean(1)
print("\nMilho: P(>=1 quebra em 3 anos seguidos), mediana dos municípios: independente", round(indep.median(), 3),
      "| blocos reais de 3 anos", round(blocos.median(), 3))
cond = []
for a in [1998, 2016]:
    cond.append(Q[[a, a + 1, a + 2]].max(1))
print("depois de 1998 (98-00) e 2016 (16-18): fração de municípios com >=1 quebra:", [round(c.mean(), 2) for c in cond])
for a in [1998, 2010, 2016, 2024]:
    nxt = [b for b in [a + 1, a + 2] if b in Q.columns]
    print(f"quebra em {a}: {Q[a].mean():.2f}; anos seguintes", {b: round(Q[b].mean(), 2) for b in nxt})
print("taxa média de quebra num ano qualquer:", round(Q.mean().mean(), 3))
# (3) preço deflacionado (R$ de 2025/kg) por UF: dispersão recente e relação com o rendimento do estado
for prod in ["Milho", "Feijão", "Mandioca"]:
    x = P[(P.produto == prod) & (P.area_plantada_ha > 0)].dropna(subset=["preco_r2025_kg"])
    x = x[x.ano >= 2006]
    g = x.groupby("ano").agg(preco=("preco_r2025_kg", "median"), rend=("rend_plantado_kg_ha", "median"))
    rho = g.preco.corr(g.rend, method="spearman")
    rec = x[x.ano >= 2016].preco_r2025_kg
    print(f"{prod}: preço mediano NE 2016-25 P10/P50/P90 = {rec.quantile(.1):.2f}/{rec.median():.2f}/{rec.quantile(.9):.2f} R$/kg; "
          f"Spearman preço×rend (mediana NE, 2006-25) = {rho:+.2f}; preço em 2016 / mediana = {g.preco.get(2016, np.nan)/g.preco.median():.2f}")
