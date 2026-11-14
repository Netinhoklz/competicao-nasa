# %% [markdown]
# ## 8. Rotação em reais: o bônus da leguminosa e o cenário honesto
#
# Dois cartões do catálogo de rotações (`pesquisa/catalogo_rotacoes_comprovadas.md`) viram dinheiro aqui:
# - **`ne_lg_cereal_sequeiro_quente`**: caupi (ou outra leguminosa de grão) antes de milho ou sorgo **solteiro**, em
#   sequeiro quente e sem adubo: **+24% no rendimento do cereal, faixa +2% a +49%, só no ano colhido** (B·T1). No ano
#   de quebra (rendimento < 0,5 do normal), o bônus é ~0;
# - **`ne_s0_para_rotacao_tempo`**: contra o consórcio milho + feijão de hoje (S0), a troca para rotação no tempo **nunca
#   foi medida**: central 0, sensibilidade **0 a +9%** no milho seguinte (D·T3).
#
# Conta: bônus (R$/ha) = efeito × receita do milho no ano, só nos anos sem quebra. A receita é a preço de referência
# (1998–2025), por município. O plano do protótipo tem uma só passagem leguminosa → cereal em 2027–2029: a faixa 2
# (caupi em 2027 → milho em 2028, se o ano for bom). No baixio, o caupi entra em revezamento no milho em pé, e o catálogo
# não dá bônus de grão para isso (Melo et al. 2013).

# %%
EFEITOS = {"honesto contra a S0: 0%": 0.0, "honesto contra a S0: +9%": 0.09, "leguminosa → cereal solteiro: +2%": 0.02,
           "leguminosa → cereal solteiro: +24%": 0.24, "leguminosa → cereal solteiro: +49%": 0.49}
Mi = M[M.produto == "Milho"].copy()
Mi["colhe"] = ~Mi.quebra
bon = []
for nome, e in EFEITOS.items():
    v = (e * Mi.R * Mi.colhe)
    por_mun = v.groupby(Mi.cod_mun).mean()
    por_mun_en = v[Mi.ano.isin(EN_FORTE)].groupby(Mi.cod_mun[Mi.ano.isin(EN_FORTE)]).mean()
    bon.append({"cenário": nome, "bônus médio (R$/ha·ano)": por_mun.median(), "P10 entre municípios": por_mun.quantile(0.1),
                "P90 entre municípios": por_mun.quantile(0.9), "bônus médio em El Niño forte": por_mun_en.median(),
                "Quixadá": por_mun.get(QUIXADA, np.nan), "Quixadá, El Niño forte": por_mun_en.get(QUIXADA, np.nan)})
BON = pd.DataFrame(bon).set_index("cenário")
print(f"Valor do bônus no milho do ano seguinte (R$ de 2025 por ha de milho; {Mi.cod_mun.nunique()} municípios). "
      f"Anos sem quebra: {Mi.colhe.mean() * 100:.1f}% (El Niño forte: {Mi[Mi.ano.isin(EN_FORTE)].colhe.mean() * 100:.1f}%)")
display(BON.round(0))
mi_q = Mi[Mi.cod_mun == QUIXADA]
print(f"Quixadá: receita mediana do milho {brl(mi_q.R.median())}/ha; quebra em {mi_q.quebra.mean() * 100:.0f}% dos anos "
      f"({int(mi_q.quebra.sum())} de {len(mi_q)}); desembolso do milho (Crateús) {brl(CUSTO.loc['Milho', 'desembolso'])}/ha")

fig, ax = plt.subplots(figsize=(10, 4.2))
nomes = list(EFEITOS)
y = np.arange(len(nomes))
ax.barh(y + 0.18, BON["bônus médio (R$/ha·ano)"], height=0.34, color="#3987e5", label="todos os anos")
ax.barh(y - 0.18, BON["bônus médio em El Niño forte"], height=0.34, color="#0d366b", label="anos de El Niño forte")
for k in range(len(nomes)):
    ax.text(BON.iloc[k, 0] + 2, k + 0.18, brl(BON.iloc[k, 0]), va="center", fontsize=8, color="#52514e")
    ax.text(BON.iloc[k, 3] + 2, k - 0.18, brl(BON.iloc[k, 3]), va="center", fontsize=8, color="#52514e")
ax.set_yticks(y, nomes)
ax.set_xlabel("R$ de 2025 por ha de milho, por ano (mediana dos municípios)")
ax.legend(frameon=False, fontsize=8, loc="lower right")
ax.set_title("Quanto vale, em reais, o efeito da leguminosa no milho seguinte", fontsize=10)
plt.tight_layout()
plt.show()

# %% [markdown]
# **A sequência inteira.** O catálogo (item 12, grau D) já comparou, no semiárido de 2010–2024, feijão → milho contra
# milho → milho: a sequência com feijão dá 0,80–0,94 da massa, mas 1,55–1,69 vez a receita. Refazemos em R$ de 2025
# (receita observada, os dois anos somados), com e sem o bônus. A conta mostra de onde vem o dinheiro: do preço do
# feijão (≈ 3,6 vezes o do milho por kg, seção 3), não do nitrogênio.

# %%
base_sa = M[M.semiarido & M.ano.between(2010, 2025) & M.produto.isin(["Milho", "Feijão"])].pivot_table(index=["cod_mun", "ano"], columns="produto", values="R_obs")
nxt = base_sa.reindex([(c, a + 1) for c, a in base_sa.index])
nxt.index = base_sa.index
SA = base_sa.join(nxt.add_suffix("_t1")).dropna()
SA = SA[SA.index.get_level_values(1) <= 2024]
qm = M[M.produto == "Milho"].set_index(["cod_mun", "ano"]).quebra
SA["colhe_t1"] = ~qm.reindex([(c, a + 1) for c, a in SA.index]).fillna(False).astype(bool).to_numpy()
seq = {}
for nome, e in [("sem bônus", 0.0), ("bônus +24%", 0.24)]:
    fm_ = SA.Feijão + SA.Milho_t1 * (1 + e * SA.colhe_t1)
    mm_ = SA.Milho + SA.Milho_t1
    r = fm_ / mm_
    seq[nome] = {"receita de 2 anos, feijão → milho (R$/ha)": fm_.median(), "receita de 2 anos, milho → milho (R$/ha)": mm_.median(),
                 "razão mediana": r.median(), "acima do milho → milho (%)": (r > 1).mean() * 100}
print(f"Sequência de 2 anos no semiárido, 2010–2024 ({len(SA)} pares município-ano)")
display(pd.DataFrame(seq).T.round(2))

# %% [markdown]
# **Em três anos (2027–2029), para a faixa 2 do plano.** O caupi de 2027 só paga o bônus em 2028, e só se 2028 não for
# ano de quebra. A tabela usa a distribuição do próprio município: o bônus esperado em 2028 é o efeito × a receita média
# do milho nos anos sem quebra × a chance de não quebrar. Em Quixadá, por ha e para a faixa de 2/3 ha da família (a
# largura da faixa é suposição da seção 10).

# %%
q = Mi[Mi.cod_mun == QUIXADA]
p_colhe = q.colhe.mean()
p_colhe_en = q[q.ano.isin(EN_FORTE)].colhe.mean()
r_colhe = q[q.colhe].R.mean()
lin = []
for nome, e in EFEITOS.items():
    lin.append({"cenário": nome, "2028 normal: R$/ha": e * r_colhe * p_colhe, "2028 normal: faixa de 2/3 ha": e * r_colhe * p_colhe * 2 / 3,
                "2028 como El Niño forte: R$/ha": e * r_colhe * p_colhe_en, "2028 como El Niño forte: faixa de 2/3 ha": e * r_colhe * p_colhe_en * 2 / 3})
ROT3 = pd.DataFrame(lin).set_index("cenário")
print(f"Quixadá: chance de o milho não quebrar {p_colhe * 100:.0f}% (em El Niño forte {p_colhe_en * 100:.0f}%); receita média do milho nos anos colhidos {brl(r_colhe)}/ha")
display(ROT3.round(0))

# %% [markdown]
# **Leitura.**
# - O milho **não quebra em 76,8%** dos município-anos (61,0% em El Niño forte); só nesses anos o bônus vale.
# - **Bônus de +24%** (leguminosa → cereal solteiro): **R$ 153 por ha de milho por ano** na mediana dos municípios (P10
#   R$ 72; P90 R$ 421); R$ 105 em El Niño forte. Na faixa de +2% a +49%: de R$ 13 a R$ 313.
# - **Cenário honesto contra a S0:** central 0; com +9%, R$ 58/ha por ano (R$ 39 em El Niño forte).
# - O bônus de +24% é cerca de 1/4 da receita mediana do milho e **não chega ao desembolso** do milho (R$ 1.136/ha): a
#   rotação não faz o milho pagar a planilha.
# - **Sequência de 2 anos:** feijão → milho rende 1,44 vez a receita de milho → milho sem bônus (acima em 81% dos pares)
#   e 1,56 vez com +24% (87%). Reproduz o catálogo (1,55–1,69 vez; 82–90%). O dinheiro vem do preço do feijão.
# - **Quixadá, faixa 2 (2/3 ha), 2028:** o milho não quebra em 71% dos anos (25% em El Niño forte). Bônus esperado de
#   R$ 131 com +24%, R$ 49 com +9% e R$ 0 no central honesto; se 2028 for como um El Niño forte, R$ 46 com +24%. **Em 3
#   anos, a rotação em si vale menos de R$ 300 para a família.** O valor do plano está em outro lugar (seções 7 e 10).
