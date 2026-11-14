# %% [markdown]
# ## 9. O cardápio do protótipo em reais, município a município
#
# O motor do protótipo decide, para cada município, a situação de cada cultura (`E:/campeonato-nasa/dados/gaez_zarc/
# nordeste_2026-2027.csv`, versão regerada em 14/11): onde a cultura tem ZARC no município, o ZARC decide ("indicada" =
# risco de 20% em algum solo e ciclo; "com risco" = só 30% ou 40%); sem ZARC, o GAEZ v4 com insumo baixo filtra
# (aptidão > 40 = "só aptidão"; classes oficiais do GAEZ v4: > 85 muito alta, > 70 alta, > 55 boa, > 40 média,
# > 25 moderada, > 10 marginal). Aqui cruzamos essa situação com o dinheiro das seções 4 a 6.
#
# **A mandioca e o ZARC.** A tábua aberta do ZARC 2026/27 não traz a mandioca, então o motor a filtra pelo GAEZ. No CE,
# a mandioca tem ZARC em portaria plurianual (Port. 11/2020; em Quixadá, a janela vai até 31/03), fora da tábua.
#
# - **Disponível** = "indicada" ou "só aptidão". O feijão do PAM vale para o caupi e para o feijão comum: conta a melhor
#   situação dos dois.
# - **Com série** = o município tem ≥ 10 anos válidos da cultura no PAM. Sem série, a cultura fica no cardápio, mas sem
#   número de dinheiro (o produto mostra "sem histórico de produção no município").
# - **Maior margem esperada** = maior margem mediana sobre o desembolso (seção 5; custo suposto onde não há CONAB).
# - **Menor risco** = maior receita no pior decil (CVaR10 em R$/ha): a cultura que mais deixa dinheiro no ano ruim.
# - **Melhor por mês de terra** = maior receita mediana por ha-mês (ciclo central da seção 1).

# %%
GZN = pd.read_csv(DADOS / "gaez_zarc" / "nordeste_2026-2027.csv", dtype={"geocodigo": str})
MAPA_C = {"Milho 1ª Safra": "Milho", "Feijão Caupi": "Feijão", "Feijão 2ª Safra": "Feijão", "Sorgo Granífero": "Sorgo",
          "Algodão Herbáceo": "Algodão herbáceo", "Amendoim": "Amendoim", "Girassol": "Girassol", "Mamona": "Mamona", "mandioca": "Mandioca"}
ORD_SIT = {"indicada": 0, "só aptidão": 1, "com risco": 2, "fora": 3}
g = GZN.assign(produto=GZN.cultura.map(MAPA_C)).dropna(subset=["produto"])
g["o"] = g.situacao.map(ORD_SIT)
SIT = g.sort_values("o").groupby(["geocodigo", "produto"]).situacao.first().unstack()
CARD = ["Feijão Caupi", "Milho 1ª Safra", "Feijão 2ª Safra", "mandioca", "Amendoim", "Sorgo Granífero", "guandu", "Sorgo Forrageiro",
        "milheto", "Algodão Herbáceo", "Mamona", "Girassol"]
n_card = GZN[GZN.cultura.isin(CARD) & GZN.situacao.isin(["indicada", "só aptidão"])].groupby("geocodigo").cultura.nunique()
print(f"Culturas do cardápio com camada (12 de 15) disponíveis por município: mediana {n_card.median():.0f} (P10 {n_card.quantile(.1):.0f}, "
      f"P90 {n_card.quantile(.9):.0f}); {GZN.geocodigo.nunique()} municípios")
display(pd.crosstab(g.produto, g.situacao).reindex(index=CULT, columns=list(ORD_SIT)).fillna(0).astype(int))

met = mm.merge(RR[["produto", "cod_mun", "cvar10", "cvar10_rel"]], on=["produto", "cod_mun"], how="left")
met["por_ha_mes"] = met.R / met.produto.map(CICLO.dias / 30.4)
met["situacao"] = [SIT.at[c, p] if c in SIT.index and p in SIT.columns else np.nan for c, p in zip(met.cod_mun, met.produto)]
cand = met[met.situacao.isin(["indicada", "só aptidão"])]
print(f"Pares município × cultura com série: {len(met)}; disponíveis no cardápio: {len(cand)} ({len(cand) / len(met) * 100:.0f}%)")
fora = met[~met.situacao.isin(["indicada", "só aptidão"])]
print("Com série no PAM, mas fora do cardápio (o produtor planta onde o motor não indica):")
display(fora.groupby(["produto", "situacao"]).size().unstack(fill_value=0).reindex(CULT).dropna(how="all").astype(int))

# %%
best_m = cand.loc[cand.groupby("cod_mun").marg_desembolso.idxmax()].set_index("cod_mun")
best_r = cand.loc[cand.groupby("cod_mun").cvar10.idxmax()].set_index("cod_mun")
best_h = cand.loc[cand.groupby("cod_mun").por_ha_mes.idxmax()].set_index("cod_mun")
fig, axs = plt.subplots(1, 3, figsize=(16, 6.2))
mapa_ne(axs[0], best_m.produto, "Cultura de maior margem esperada (sobre o desembolso)", cores=COR, ordem=CULT)
mapa_ne(axs[1], best_r.produto, "Cultura de menor risco (maior receita no pior decil)", cores=COR, ordem=CULT)
mapa_ne(axs[2], best_h.produto, "Cultura de maior receita por ha-mês", cores=COR, ordem=CULT)
plt.tight_layout()
plt.show()
venc = pd.DataFrame({"maior margem": best_m.produto.value_counts(), "menor risco": best_r.produto.value_counts(),
                     "por ha-mês": best_h.produto.value_counts()}).reindex(CULT).fillna(0).astype(int)
sa_m = REFM.semiarido_2022
venc_sa = pd.DataFrame({"maior margem": best_m[best_m.index.map(sa_m) == True].produto.value_counts(),
                        "menor risco": best_r[best_r.index.map(sa_m) == True].produto.value_counts(),
                        "por ha-mês": best_h[best_h.index.map(sa_m) == True].produto.value_counts()}).reindex(CULT).fillna(0).astype(int)
print("Número de municípios em que cada cultura vence: NE inteiro | só o semiárido (delimitação 2022)")
display(pd.concat({"NE": venc, "semiárido": venc_sa}, axis=1))
print("Aviso: no cerrado (oeste da BA, sul do MA e do PI), milho e algodão são lavoura empresarial (CONAB Barreiras-BA: algodão "
      f"{brl(C[C.cultura_arquivo.eq('Algodão')].custo_operacional_r_ha_r2025.median())}/ha de custo operacional); o custo de lavoura "
      "familiar usado aqui não vale lá, e a vitória do algodão e do milho nesses municípios é otimista.")
print(f"Municípios com ≥ 1 cultura disponível e com série: {cand.cod_mun.nunique()} de {GZN.geocodigo.nunique()}; "
      f"a de maior margem é 'indicada' pelo ZARC em {(best_m.situacao == 'indicada').mean() * 100:.0f}% deles")
print(f"Margem mediana da melhor cultura > 0 (sobre o desembolso) em {(best_m.marg_desembolso > 0).mean() * 100:.0f}% dos municípios; "
      f"sobre a semente em {(best_m.marg_semente > 0).mean() * 100:.0f}%")
sem_mand = cand[cand.produto != "Mandioca"]
best_sm = sem_mand.loc[sem_mand.groupby("cod_mun").marg_desembolso.idxmax()].set_index("cod_mun")
print("Sem a mandioca, a cultura de maior margem seria:")
display(best_sm.produto.value_counts().reindex(CULT).dropna().astype(int))
uf_w = best_m.assign(uf=best_m.index.str[:2].map(dict(zip(["21", "22", "23", "24", "25", "26", "27", "28", "29"], UFS))))
display(pd.crosstab(uf_w.uf, uf_w.produto).reindex(index=UFS, columns=[c for c in CULT if c in uf_w.produto.unique()]).fillna(0).astype(int))

# %%
qx = met[met.cod_mun == QUIXADA].set_index("produto")[["situacao", "R", "marg_semente", "marg_desembolso", "falha_desembolso", "cvar10", "cvar10_rel", "por_ha_mes"]]
qx.columns = ["situação no cardápio", "receita mediana", "margem (semente)", "margem (desembolso)", "não paga desembolso (frac.)", "CVaR10 (R$/ha)",
              "CVaR10 ÷ mediana", "R$ por ha-mês"]
print("Quixadá: culturas com série no PAM, situação no cardápio e dinheiro (R$ de 2025/ha plantado)")
display(qx.reindex([c for c in CULT if c in qx.index]).round(2))
print("Cardápio de Quixadá no motor:", ", ".join(f"{r.cultura} ({r.situacao})" for r in GZN[GZN.geocodigo == QUIXADA].itertuples()))

# %% [markdown]
# **Leitura.**
# - O motor deixa **9 culturas** com camada disponíveis no município mediano (P10 5, P90 11), de 12.
# - **75%** dos pares município × cultura com 10 anos ou mais de produção no PAM estão disponíveis no cardápio.
# - **O cardápio corta a mandioca onde ela é plantada:** 480 municípios com 10 anos ou mais de mandioca no PAM ficam
#   "fora" (GAEZ ≤ 40 e sem ZARC na tábua). No milho, 369 ficam "com risco" e 124 "fora"; no feijão, 232 "com risco".
# - **Cultura de maior margem esperada** (sobre o desembolso): mandioca em 918 municípios, milho em 349, feijão em 268,
#   algodão em 95, amendoim em 35, mamona em 20, sorgo em 6. No semiárido: mandioca 602, milho 227, feijão 215,
#   algodão 91. Sem a mandioca, o milho venceria em 597 e o feijão em 587.
# - **Cultura de menor risco** (mais receita no pior decil): mandioca em 1.007 municípios, feijão em 477.
# - **Por ha-mês, o feijão/caupi vence em 1.077 municípios** (727 no semiárido); a mandioca em 376; o amendoim em 93.
# - 1.691 de 1.794 municípios têm ao menos uma cultura disponível e com série. A margem mediana da melhor delas é
#   positiva sobre o desembolso em 67% dos municípios e sobre a semente em 97%. A melhor é "indicada" pelo ZARC em só
#   43%: a mandioca, que mais vence, não está na tábua aberta do ZARC.
# - **Quixadá:** mandioca ("só aptidão") rende R$ 12.896/ha na mediana, com margem de +R$ 8.509 sobre o desembolso e
#   R$ 5.896 no pior decil (com o preço de pouco volume da seção 10); feijão ("indicada") R$ 1.506 e −R$ 486; milho
#   ("com risco") R$ 651 e −R$ 485; algodão ("indicada") R$ 2.035 e +R$ 42; mamona ("indicada") −R$ 2.066.
# - No cerrado (oeste da BA, sul do MA e do PI), a vitória do milho e do algodão é otimista: o custo usado é o de lavoura
#   familiar, e a CONAB de Barreiras-BA dá R$ 10.517/ha no algodão.
