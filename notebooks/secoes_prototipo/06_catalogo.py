# %% [markdown]
# ## 6. Catálogo de rotações comprovadas: a evidência do motor
#
# **Ficha técnica**
# - **O que é:** `pesquisa/catalogo_rotacoes.json`, com 147 configurações debatidas por 10 especialistas e conferidas por
#   verificação adversária.
# - **Cada cartão traz:**
#   - tipo, efeito (valor central e faixa) e onde o efeito foi medido (cultura seguinte, sequência inteira, consórcio,
#     solo ou praga);
#   - grau A–D;
#   - transferência T0–T3 (T0 medido no semiárido; T1 clima análogo; T2 só direção; T3 não transfere);
#   - lugar e DOI.
#
# **No protótipo (`motor.cartao`, revisões C4 e A8):**
# - **número só para cartões T0/T1**; T2 dá só a direção e T3 "não transfere";
# - as regras negativas e de "sem bônus" saem sem ganho (`mostrar_efeito=False`);
# - 11 cartões fixos aparecem como "regras do motor";
# - os cartões com lugar entram ponderados pelo peso de clima w (seção 5).

# %%
CATJ = json.loads((PROJ / "pesquisa" / "catalogo_rotacoes.json").read_text(encoding="utf-8"))
K = pd.json_normalize(CATJ["configuracoes"])
K["pct"] = K["efeito.pct"].map(lambda p: p[0] if isinstance(p, list) and p and p[0] is not None else np.nan)
K["tem_lugar"] = K.id.isin(LUG.id)
K["doi"] = K.referencias.map(lambda r: next((x for x in r or [] if x.startswith("10.")), None))
print(f"{len(K)} cartões; {K.tem_lugar.sum()} com lugar identificável; {K.doi.nunique()} DOIs distintos; "
      f"{K.pct.notna().sum()} com efeito em %")
display(pd.crosstab(K.tipo, K.grau, margins=True, margins_name="total"))
display(pd.crosstab(K.tipo, K.transferencia, margins=True, margins_name="total"))
print("Unidade do efeito (as 6 mais comuns):")
display(K["efeito.unidade"].value_counts().head(6).to_frame("cartões").T)

# %%
# a regra do motor: que cartões a página mostra com número?
C = pd.DataFrame([M.cartao(c) for c in M.CARDS])
C["mostra_numero"] = C.efeito.notna()
print("Cartões que saem com número na página (motor.cartao), por transferência:")
display(pd.crosstab(C.transferencia, C.mostra_numero.map({True: "com número", False: "sem número"}), margins=True, margins_name="total"))
print(f"Cartões marcados como irrigados ('[irrigado]' na página): {int(C.irrigado.sum())}")
RG = C[C.id.isin(M.REGRAS)].set_index("id")[["tipo", "grau", "transferencia", "efeito"]]
RG["uso no motor"] = [M.REGRAS[i][0] for i in RG.index]
print(f"As {len(RG)} regras fixas do motor ({int(RG.efeito.notna().sum())} com número):")
display(RG)

# %%
P = K.dropna(subset=["pct"])
grupos = [g for g in ["cultura_seguinte", "sequencia_inteira", "sistema_consorciado", "solo_ou_servico"] if (P["efeito.na"] == g).any()]
fig, ax = plt.subplots(figsize=(12, 4.8))
for i, gname in enumerate(grupos):
    y = P[P["efeito.na"] == gname].pct.clip(-100, 200)
    x = np.full(len(y), i) + np.random.default_rng(0).uniform(-0.18, 0.18, len(y))
    mostra = P[P["efeito.na"] == gname].transferencia.isin(["T0", "T1"]).values
    ax.scatter(x[~mostra], y[~mostra], s=18, facecolor="none", edgecolor=CAT[i], alpha=0.8)
    ax.scatter(x[mostra], y[mostra], s=18, color=CAT[i], alpha=0.9)
    ax.hlines(y.median(), i - 0.3, i + 0.3, color="#0b0b0b", lw=2)
    ax.text(i + 0.32, y.median(), f"mediana {y.median():+.0f}% (n = {len(y)}; {mostra.sum()} T0/T1)", va="center", fontsize=8, color="#52514e")
ax.axhline(0, color="#52514e", lw=0.8)
ax.set_xticks(range(len(grupos)))
ax.set_xticklabels([g.replace("_", " ") for g in grupos])
ax.set_ylabel("efeito (% do controle; cortado em −100 e +200)")
ax.set_title("Efeitos do catálogo por onde foram medidos (cheio = T0/T1, que a página mostra; vazio = T2/T3, só direção)")
plt.show()
print("Efeito em % por grau (cartões de cultura seguinte):")
display(P[P["efeito.na"] == "cultura_seguinte"].groupby("grau").pct.describe().round(1))
print("Referências com mais cartões:")
display(K.referencia_texto.str.extract(r"^([^,;(]+?\d{4}[a-z]?)")[0].value_counts().head(10).rename("cartões").to_frame())

# %% [markdown]
# **Leitura:**
# - **147 cartões; 72 com lugar; 48 DOIs distintos; 81 com efeito em %.**
#   - Graus: A 9, B 44, C 76, D 18.
#   - Transferência: T0 36, T1 7, T2 73, T3 31.
# - **Na página, só 29 cartões saem com número** (24 T0 e 5 T1). Os 104 T2/T3 dão só a direção. Outros 14 T0/T1 também
#   ficam sem número (efeito sem valor central em % ou regra que manda esconder o número).
# - **Das 11 regras fixas do motor, só uma tem número:** o +24% (+2 a +49) da leguminosa antes do cereal (T1), "no ano
#   colhido, contra cereal solteiro". As regras negativas e de "sem bônus" (da Luz, Pacheco, Melo) saem sem ganho.
# - **19 cartões vêm de ensaio irrigado** e saem marcados na página.
# - **Nenhum dos 64 cartões de rotação é T0.** Não há rotação no tempo medida no semiárido brasileiro. Os números de
#   rotação que valem no sertão são os 5 T1.
# - **Na cultura seguinte, a mediana dos efeitos é de +13% (grau B) a +27% (grau C)**, e de +20% no grau A (Zhao 2022,
#   global, T2).
# - **Três meta-análises sustentam 46 cartões:** Mudare 2025 (21), Zhao 2022 (14) e Franke 2018 (11).
