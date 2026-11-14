# %% [markdown]
# ## 6. Risco e retorno
#
# Medidas por município e cultura, na receita a preço de referência (R$ de 2025 por ha plantado, 1998–2025):
# - **média** e **CV** (desvio-padrão ÷ média);
# - **pior ano em 10** = P10 da série do município; **CVaR10** = média dos anos abaixo do P10 (os ~3 piores de 28);
# - **chance de não pagar o desembolso** (seção 5).
#
# Depois, a mesma receita em dois grupos de anos que importam para 2027: os **El Niños fortes** (ONI de OND–NDJ ≥ 1,5:
# quadras de 1998, 2010, 2016 e 2024) e a **seca longa de 2012–2016**. Por fim, a "fronteira": a média contra o pior
# decil, cultura a cultura.

# %%
def cvar10(s):
    s = s.dropna()
    return s[s <= s.quantile(0.1)].mean()


RR = M.groupby(["produto", "cod_mun"]).agg(
    media=("R", "mean"), mediana=("R", "median"), dp=("R", "std"), p10=("R", lambda s: s.quantile(0.1)), cvar10=("R", cvar10),
    falha_des=("falha_desembolso", "mean"), anos=("R", "size")).reset_index()
RR["cv"] = RR.dp / RR.media
RR["p10_rel"] = RR.p10 / RR.mediana
RR["cvar10_rel"] = RR.cvar10 / RR.mediana
risco = RR.groupby("produto").agg(municipios=("cod_mun", "size"), media=("media", "median"), mediana=("mediana", "median"),
                                  cv=("cv", "median"), p10=("p10", "median"), cvar10=("cvar10", "median"),
                                  p10_rel=("p10_rel", "median"), cvar10_rel=("cvar10_rel", "median"),
                                  nao_paga_desembolso_pct=("falha_des", lambda s: s.median() * 100)).reindex(CULT).dropna(how="all")
risco["municipios"] = risco.municipios.astype(int)
print("Risco e retorno por cultura (mediana entre os municípios com série; R$ de 2025 por ha plantado)")
display(risco.round(2))

# o preço protege? CV da receita observada (com o preço do ano) contra a receita a preço fixo, mesmos anos 2010–2025
pp = M[M.ano.between(2010, 2025)].dropna(subset=["R_obs"]).groupby(["produto", "cod_mun"]).filter(lambda g: len(g) >= 10)
cvp = pp.groupby(["produto", "cod_mun"]).agg(cv_fixo=("R", lambda s: s.std() / s.mean()), cv_obs=("R_obs", lambda s: s.std() / s.mean())).groupby("produto").median().reindex(CULT).dropna()
cvp["o preço do ano muda o CV em"] = cvp.cv_obs - cvp.cv_fixo
print("CV da receita, 2010–2025: a preço fixo (só clima) e observada (clima + preço do ano)")
display(cvp.round(3))

# %%
def grupo(a):
    return "El Niño forte" if a in EN_FORTE else ("seca 2012–16" if a in SECA else "demais anos")


M["grupo"] = M.ano.map(grupo)
M["R_rel"] = M.R / M.groupby(["produto", "cod_mun"]).R.transform("median")
eg = M.groupby(["produto", "grupo"]).agg(R=("R", "median"), R_rel=("R_rel", "median"), quebra=("quebra", "mean"),
                                         nao_paga=("falha_desembolso", "mean")).unstack()
lin = {}
for c in CULT:
    if c not in eg.index:
        continue
    e = eg.loc[c]
    lin[c] = {"receita, demais anos": e[("R", "demais anos")], "receita, El Niño forte": e[("R", "El Niño forte")],
              "receita, seca 2012–16": e[("R", "seca 2012–16")],
              "razão ao normal, El Niño forte": e[("R_rel", "El Niño forte")], "razão ao normal, seca": e[("R_rel", "seca 2012–16")],
              "quebra %, demais": e[("quebra", "demais anos")] * 100, "quebra %, El Niño forte": e[("quebra", "El Niño forte")] * 100,
              "quebra %, seca": e[("quebra", "seca 2012–16")] * 100,
              "não paga desembolso %, demais": e[("nao_paga", "demais anos")] * 100,
              "não paga desembolso %, El Niño forte": e[("nao_paga", "El Niño forte")] * 100}
EN = pd.DataFrame(lin).T
print("Receita (R$ de 2025/ha plantado, mediana dos município-anos) e risco por grupo de anos")
display(EN.round(2))
pa = M[M.produto.isin(["Milho", "Feijão", "Mandioca"]) & M.ano.isin(EN_FORTE)].groupby(["ano", "produto"]).R_rel.median().unstack()
print("Razão ao normal da receita, mediana dos municípios, em cada El Niño forte")
display(pa.round(2))

fig, ax = plt.subplots(figsize=(12, 4.4))
ix = M[M.produto.isin(["Milho", "Feijão", "Mandioca"])].groupby(["ano", "produto"]).R_rel.median().unstack()
for c in ["Milho", "Feijão", "Mandioca"]:
    ax.plot(ix.index, ix[c], color=COR[c], marker="o", ms=3, label=c)
for a in EN_FORTE:
    ax.axvspan(a - 0.5, a + 0.5, color="#f0efec", zorder=0)
ax.axvspan(SECA[0] - 0.5, SECA[-1] + 0.5, color="#e1e0d9", alpha=0.5, zorder=0)
ax.axhline(1, color=CINZA, lw=1)
ax.set_ylabel("receita do ano ÷ receita normal do município")
ax.set_title("Índice de renda por ha plantado no NE (mediana dos municípios; faixas claras = El Niño forte; cinza = seca 2012–16)", fontsize=10)
ax.legend(frameon=False, fontsize=8)
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 6.1 A fronteira: retorno médio contra o pior decil
#
# Cada ponto é uma cultura (mediana entre os municípios). Mais à direita, mais receita média; mais acima, mais receita no
# pior ano em 10 (CVaR10). Como as culturas existem em municípios diferentes, o painel da direita repete a conta só nos
# municípios que têm as três culturas principais, para comparar o mesmo chão.

# %%
fig, axs = plt.subplots(1, 2, figsize=(14, 5))
for c in risco.index:
    r = risco.loc[c]
    axs[0].scatter(r.media, r.cvar10, s=70, color=COR[c], edgecolor="#fcfcfb", lw=2, zorder=3)
    axs[0].annotate(c, (r.media, r.cvar10), xytext=(6, 4), textcoords="offset points", fontsize=8, color="#52514e")
axs[0].set_xscale("log")
axs[0].set_xlabel("receita média (R$ de 2025/ha plantado, log)")
axs[0].set_ylabel("CVaR10: média dos piores anos (R$/ha)")
axs[0].set_title("Todas as culturas, cada uma nos seus municípios", fontsize=10)
tres = set.intersection(*[set(RR[RR.produto == c].cod_mun) for c in ["Milho", "Feijão", "Mandioca"]])
r3 = RR[RR.cod_mun.isin(tres)].groupby("produto")[["media", "cvar10", "cvar10_rel"]].median()
for c in ["Milho", "Feijão", "Mandioca"]:
    axs[1].scatter(r3.loc[c, "media"], r3.loc[c, "cvar10"], s=70, color=COR[c], edgecolor="#fcfcfb", lw=2, zorder=3)
    axs[1].annotate(f"{c} (CVaR10 = {r3.loc[c, 'cvar10_rel']:.2f} do normal)", (r3.loc[c, "media"], r3.loc[c, "cvar10"]),
                    xytext=(6, 4), textcoords="offset points", fontsize=8, color="#52514e")
axs[1].set_xlabel("receita média (R$ de 2025/ha plantado)")
axs[1].set_ylabel("CVaR10 (R$/ha)")
axs[1].set_title(f"Mesmo chão: os {len(tres)} municípios com as três culturas", fontsize=10)
plt.tight_layout()
plt.show()
TRES = sorted(tres)

# %% [markdown]
# **Leitura.**
# - **CV da receita:** milho 0,73; algodão 0,58; feijão e mamona 0,54; sorgo 0,53; mandioca 0,30; amendoim 0,25.
# - **Pior decil (CVaR10) ÷ mediana:** milho 0,14; algodão 0,16; mamona 0,18; feijão 0,24; sorgo 0,26; **mandioca
#   0,47**; amendoim 0,73 (com o viés do relato da seção 2).
# - **O preço do ano não reduz o risco:** a receita observada tem CV maior que a de preço fixo em todas as culturas
#   (+0,04 no feijão a +0,26 no amendoim).
# - **El Niño forte (1998, 2010, 2016, 2024):** a receita mediana do milho cai de R$ 729 para R$ 425/ha (razão ao normal
#   0,75); a quebra do milho sobe de 17% para 39% dos município-anos; a do feijão, de 13% para 32%; a do algodão, de 16%
#   para 42%. A mandioca fica em 1,00 do normal, com quebra de 7% para 12%.
# - **Ano a ano:** o milho ficou em 0,38 do normal em 1998, 0,47 em 2016, 0,80 em 2010 e **1,27 em 2024**; o feijão em
#   0,61, 0,57, 0,94 e 1,00; a mandioca em 0,84, 0,96, 1,00 e 1,00. O El Niño forte aumenta a chance de perda, mas não é
#   sentença: 2024 foi bom.
# - **Seca de 2012–2015** (2016 conta como El Niño): milho 0,71 do normal, feijão 0,86, mandioca 0,98, sorgo 0,52,
#   algodão 0,53, mamona 0,48.
# - **Chance de não pagar o desembolso em El Niño forte:** milho 82%, mamona 84%, feijão 77%, algodão 60%, mandioca 29%.
# - **Fronteira:** nos 1.420 municípios com as três culturas, a mandioca tem mais receita média e mais receita no pior
#   decil que o milho e o feijão. Não há troca entre retorno e risco: a mandioca ganha nos dois eixos.
