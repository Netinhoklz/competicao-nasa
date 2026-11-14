# %% [markdown]
# ## 11. Síntese: o que paga mais, o que protege mais e o que falta medir
#
# A tabela junta os números de cada seção, cultura a cultura, na mesma unidade (R$ de 2025 por ha plantado, mediana dos
# municípios com série). "Suposto" marca as culturas cujo custo não tem planilha da CONAB no NE.

# %%
SINT = pd.DataFrame({
    "receita observada (R$/ha plantado)": rec.plantado,
    "R$ por ha-mês": rec["por ha-mês"],
    "chance de quebra (%)": tab.quebra_pct,
    "pior ano em 10 ÷ mediana": risco.p10_rel,
    "razão ao normal em El Niño forte": EN["razão ao normal, El Niño forte"],
    "desembolso (R$/ha)": CUSTO.desembolso,
    "margem sobre o desembolso": res["margem (desembolso)"],
    "margem sobre a semente": res["margem (semente)"],
    "não paga o desembolso (% dos anos)": res["não paga desembolso (% dos anos)"],
    "rend. de equilíbrio ÷ mediano (desembolso)": EQ["× o rendimento mediano (desembolso)"],
    "custo": CUSTO.origem.map(lambda o: "suposto" if str(o).startswith("suposição") else "CONAB"),
}).reindex(CULT).dropna(subset=["receita observada (R$/ha plantado)"])
display(SINT.round(2))
CH = RC.loc[["S0: ½ milho + ½ feijão", "1/3 (mandioca todo ano)", "1/3 (mandioca a cada 2 quadras)", "Faixas do plano",
             "Plano da família (2/3 faixas + 1/3 baixio)"], ["receita média (R$/ha)", "CVaR10 (R$/ha)", "CVaR10 (razão)", "não paga o desembolso %",
                                                              "não paga o desembolso %, El Niño forte"]]
display(CH.round(2))

# %% [markdown]
# **O que paga mais.**
# - **Por hectare:** mandioca (R$ 5.342/ha plantado, receita observada 2010–2025) e amendoim (R$ 3.633/ha, em só 165
#   municípios, 72% da área fora do semiárido). O roçado fica muito atrás: feijão R$ 1.182 e milho R$ 598.
# - **Por mês de terra:** amendoim (R$ 1.104) e feijão/caupi precoce (R$ 513). A mandioca cai para R$ 356 porque prende a
#   terra 12 a 18 meses. O milho fica em R$ 165.
# - **Contra o custo:** sobre o desembolso da CONAB, só a mandioca (+R$ 3.261/ha) fica positiva entre as culturas com
#   planilha no NE; amendoim e algodão também, mas com custo suposto. **O roçado de milho e feijão paga a semente, não a
#   planilha:** não paga o desembolso em 75% (feijão) e 86% (milho) dos anos.
#
# **O que protege mais.**
# - **A mandioca:** pior ano em 10 = 0,62 do normal; 1,00 do normal nos quatro El Niños fortes; quebra em 6% dos anos.
#   Com o aviso do relato: 33% dos rendimentos repetem o ano anterior.
# - **A carteira:** a conta da proposta sai igual (0,26 → 0,36 no CE) e o placebo também (0,325 contra 0,335). Em reais, a
#   carteira 1/3 leva o pior decil de R$ 351 para R$ 1.584/ha; as faixas do plano, para R$ 1.431/ha. A chance de não
#   pagar o desembolso cai de 68% (S0) para 34% (faixas) e, em El Niño forte, de 75% para 41%.
# - **Mas a proteção em reais é, sobretudo, nível de receita:** no pior decil agrupado, o feijão do vizinho no lugar da
#   mandioca leva a carteira a R$ 198/ha (S0: R$ 127); a mandioca leva a R$ 956.
#
# **A rotação em si vale pouco em dinheiro:** +24% no milho depois do caupi = R$ 153 por ha de milho por ano (mediana do
# NE); contra a prática de hoje, de R$ 0 a R$ 58. Na família de Quixadá, menos de R$ 300 em 3 anos. O argumento
# financeiro do plano é a mandioca no chão e a forragem, não o nitrogênio.
#
# **A família de Quixadá (fictícia):** o plano pede caixa e trabalho em 2027 (maniva e sorgo forrageiro sem venda) e paga
# em 2028–2029 com a mandioca. Com El Niño forte em 2027, fica R$ 13.978 acima da S0 em 3 anos (margem sobre a semente)
# com o preço da raiz de Quixadá, R$ 7.333 com a mediana do CE e R$ 4.009 com o P25 do CE. Empata com a raiz a R$ 0,29/kg.
#
# **O que falta medir, nesta ordem:**
# 1. **O custo de verdade da família do sertão** (o que sai do bolso por ha). As planilhas da CONAB são de lavouras com
#    1,7 a 3,4 vezes o rendimento do PAM.
# 2. **O mercado da mandioca para muitas famílias ao mesmo tempo** (casa de farinha, frete, preço da raiz). O ganho do
#    plano vai de R$ 14 mil a R$ 4 mil com o preço.
# 3. **O valor de uso da forragem** (sorgo forrageiro, palma, gliricídia) para as cabras. Hoje entra como zero.
# 4. **O ensaio de faixas contra o consórcio de hoje** (o "0 a +9%").
# 5. **O caupi separado do feijão comum**, e o relato repetido da mandioca (33%) e do amendoim (30%).
# 6. **O Garantia-Safra em reais** (o valor do benefício não está nas fontes lidas).
#
# **Limites.**
# - O PAM é municipal: mistura sequeiro e irrigado, roça e empresa (o algodão e o milho do cerrado entram junto); caupi e
#   feijão comum vêm juntos.
# - O preço é implícito, não de venda. A referência é 2016–2025, e o preço real da mandioca, da mamona e do amendoim subiu
#   4% a 6% ao ano desde 2010.
# - Os custos da CONAB vêm de outros municípios do NE e de lavouras com mais tecnologia; amendoim, algodão, sorgo e
#   girassol não têm planilha no NE (custo suposto, com faixa).
# - Os ciclos são parâmetros (só a mandioca tem duração em fonte oficial lida). O girassol não tem série. A forragem não
#   tem preço.
# - "El Niño forte" são 4 anos (1998, 2010, 2016, 2024), e 2024 foi bom.
#
# **Para o protótipo.**
# - No cartão de cada cultura: receita por ha a preço de referência do município, pior ano em 10, chance de não pagar a
#   semente e o desembolso, e o ponto de equilíbrio (rendimento e preço). Nenhum desses números depende de saber o custo
#   da família.
# - Mostrar R$ por ha-mês ao lado de R$ por ha: o caupi e a mandioca trocam de lugar.
# - Rever o filtro do GAEZ na mandioca: 480 municípios com 10 anos ou mais de mandioca no PAM ficam "fora" do
#   cardápio pelo GAEZ.
# - **Não dizer:** "a rotação paga" (vale de R$ 0 a R$ 153 por ha de milho por ano); "+24% contra a sua prática"; "o
#   plano rende R$ 24 mil" sem o preço da raiz e o caixa de 2027; "a mandioca não quebra" sem o aviso do relato repetido;
#   "0,15 → 0,36" como ganho sobre a prática atual (a base é a S0, 0,26).
