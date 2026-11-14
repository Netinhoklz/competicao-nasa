# %% [markdown]
# ## 5. Custo, margem bruta e ponto de equilíbrio
#
# **Fonte do custo.** A CONAB publica séries históricas de custo de produção estimado, por cultura e município
# (www.gov.br/conab → Planilhas de custos de produção → Agrícolas; baixadas em 14/11/2026 com TLS verificado). O script
# extraiu só as folhas do Nordeste. Cada planilha traz o local, a safra, o sistema (agricultura familiar ou empresarial),
# a produtividade esperada, o mês dos preços e as linhas de custo em R$/ha. Deflacionamos pelo IPCA do mês dos preços.
#
# **Três níveis de custo, todos da mesma planilha (nenhum número novo):**
# 1. **Semente** (ou maniva): o mínimo que sai do bolso se a família comprar a semente e fizer todo o resto sozinha;
# 2. **Desembolso** = custo operacional − mão de obra (inclui a "gestão da propriedade familiar" e o administrador):
#    o que a planilha manda pagar em dinheiro (aluguel de máquina ou animal, defensivo, juros, manutenção);
# 3. **Custo operacional** (CONAB): o desembolso mais a mão de obra paga à diária. É o custo de quem contrata tudo, ou a
#    régua de quanto a lavoura remunera o dia de trabalho da família.
#
# **Quais planilhas valem para o sertão.** Só as de agricultura familiar e sequeiro do NE: feijão (9 locais, BA, CE, PI,
# SE), mandioca (12 locais, MA, PI, BA, AL), mamona (Irecê-BA e São Raimundo Nonato-PI) e milho (Carira-SE, média
# tecnologia, 6 t/ha). Para o milho do sertão usamos também a de **Crateús-CE** (milho "2ª safra", agricultura
# empresarial de média tecnologia, 1,8 t/ha), que é a mais próxima do roçado cearense. Para cada local, a mediana das
# últimas 5 planilhas. **Central** = mediana dos locais com planilha de 2019 em diante (no milho, o central é Crateús-CE
# e Carira-SE fica como teto); **faixa** = do menor ao maior local.
#
# **Sem planilha da CONAB no NE:** sorgo (só Barreiras-BA, alta tecnologia), algodão (só Barreiras-BA, empresarial),
# amendoim (só SP) e girassol (só MT e RS). Para eles o custo é **suposição**: o de uma lavoura anual manual do NE pela
# CONAB (mediana dos locais de feijão, mamona e milho de Crateús), com a faixa do menor ao maior local. O ponto de
# equilíbrio (seção 5.3) não depende dessa suposição.

# %%
C = pd.read_csv(F / "conab_custos_ne.csv", parse_dates=["mes_precos"])
C["lugar"] = C.folha.str.rsplit("-", n=1).str[0].str.replace("Giral do Ponciano", "Girau do Ponciano")
C["produto"] = C.cultura_arquivo.map({"Feijão 1ª safra": "Feijão", "Mandioca": "Mandioca", "Mamona": "Mamona", "Milho 1ª safra": "Milho"})
crateus = (C.cultura_arquivo == "Milho 2ª safra") & C.lugar.str.startswith("Crateús")
C.loc[crateus, "produto"] = "Milho"
usa = C.produto.notna() & ~C.irrigado & (C.familiar | crateus)
U = C[usa].sort_values("ano_folha").groupby(["produto", "lugar"]).tail(5)
loc = U.groupby(["produto", "lugar", "uf"]).agg(
    planilhas=("folha", "size"), de=("ano_folha", "min"), ate=("ano_folha", "max"), sistema=("sistema", "first"),
    produtividade_conab_kg_ha=("produtividade_kg_ha", "median"), semente=("sementes_r_ha_r2025", "median"),
    mao_de_obra=("mao_de_obra_r_ha_r2025", "median"), desembolso=("desembolso_r_ha_r2025", "median"),
    custo_operacional=("custo_operacional_r_ha_r2025", "median")).reset_index()
print("Planilhas da CONAB usadas (R$ de 2025 por ha; mediana das últimas 5 de cada local)")
display(loc.round(0))


def custo_central(g):
    rec = g[g.ate >= 2019]
    base = rec if len(rec) else g
    return pd.Series({"semente": base.semente.median(), "desembolso": base.desembolso.median(), "custo_operacional": base.custo_operacional.median(),
                      "op_min": g.custo_operacional.min(), "op_max": g.custo_operacional.max(), "des_min": g.desembolso.min(), "des_max": g.desembolso.max(),
                      "produtividade_conab": base.produtividade_conab_kg_ha.median(), "locais": len(g), "locais_recentes": len(rec)})


CUSTO = loc.groupby("produto").apply(custo_central)
CUSTO["origem"] = "CONAB, NE"
# milho: o central é Crateús-CE (1,8 t/ha, o mais perto do roçado do sertão); Carira-SE (6 t/ha, OGM, adubado) fica como teto
cr = loc[(loc.produto == "Milho") & loc.lugar.str.startswith("Crateús")].iloc[0]
CUSTO.loc["Milho", ["semente", "desembolso", "custo_operacional", "produtividade_conab"]] = [cr.semente, cr.desembolso, cr.custo_operacional, cr.produtividade_conab_kg_ha]
CUSTO.loc["Milho", "origem"] = "CONAB, Crateús-CE (teto: Carira-SE)"
anual = loc[loc.produto.isin(["Feijão", "Mamona"]) | loc.lugar.str.startswith("Crateús")]
sup = custo_central(anual)
for c in ["Sorgo", "Amendoim", "Algodão herbáceo", "Girassol"]:
    CUSTO.loc[c] = sup
    CUSTO.loc[c, "origem"] = "suposição: lavoura anual manual do NE (CONAB)"
    CUSTO.loc[c, "produtividade_conab"] = np.nan
CUSTO = CUSTO.reindex(CULT)
display(CUSTO.round(0))

# %% [markdown]
# ### 5.1 Margem bruta e chance de não pagar o custo
#
# Margem = receita a preço de referência (rendimento do ano × preço de referência do município) − custo. A receita
# varia de ano para ano; o custo fica fixo no valor central (a faixa entra na seção 5.4). A chance de não pagar é a
# fração dos anos (1998–2025) em que a receita ficou abaixo do custo.

# %%
NIV = ["semente", "desembolso", "custo_operacional"]
NOME_NIV = {"semente": "semente", "desembolso": "desembolso", "custo_operacional": "custo operacional"}
M = B[B.n_anos >= ANOS_MIN].copy()
for n in NIV:
    M[f"marg_{n}"] = M.R - M.produto.map(CUSTO[n])
    M[f"falha_{n}"] = M.R < M.produto.map(CUSTO[n])
mm = M.groupby(["produto", "cod_mun"]).agg(R=("R", "median"), **{f"marg_{n}": (f"marg_{n}", "median") for n in NIV},
                                         **{f"falha_{n}": (f"falha_{n}", "mean") for n in NIV}, rend=("rend_plantado_kg_ha", "median"),
                                         preco=("preco_ref", "first")).reset_index()
res = mm.groupby("produto").agg(municipios=("cod_mun", "size"), receita_mediana=("R", "median"),
                                **{f"margem ({NOME_NIV[n]})": (f"marg_{n}", "median") for n in NIV},
                                **{f"não paga {NOME_NIV[n]} (% dos anos)": (f"falha_{n}", lambda s: s.median() * 100) for n in NIV},
                                **{f"municípios com margem > 0 ({NOME_NIV[n]}, %)": (f"marg_{n}", lambda s: (s > 0).mean() * 100) for n in NIV}).reindex(CULT).dropna(how="all")
res["municipios"] = res.municipios.astype(int)
display(res.round(1))

fig, axs = plt.subplots(1, 3, figsize=(15, 5))
for ax, c in zip(axs, ["Milho", "Feijão", "Mandioca"]):
    m = mm[mm.produto == c].set_index("cod_mun").marg_desembolso
    lim = np.nanpercentile(np.abs(m), 95)
    mapa_ne(ax, m, f"{c}: margem mediana sobre o desembolso", cmap=DIV, vmin=-lim, vmax=lim, rotulo="R$ de 2025/ha (vermelho = prejuízo)")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 5.2 A curva que não depende do custo
#
# Para cada cultura, a curva mostra a fração dos município-anos (1998–2025) com receita abaixo de cada valor de custo.
# Qualquer custo que a família tenha, a chance de não pagá-lo se lê na curva. As marcas são os três níveis da CONAB.

# %%
fig, axs = plt.subplots(2, 4, figsize=(16, 7), sharey=True)
for ax, c in zip(axs.flat, CULT):
    r = np.sort(M[M.produto == c].R.dropna().to_numpy())
    if len(r) < 30:
        ax.text(0.5, 0.5, f"{c}: série curta\n({len(r)} município-anos)", ha="center", va="center", transform=ax.transAxes, fontsize=9)
        ax.set_title(c, fontsize=10)
        continue
    x = np.linspace(0, np.quantile(r, 0.97), 300)
    ax.plot(x, np.searchsorted(r, x) / len(r) * 100, color=COR[c])
    for n, ls in zip(NIV, [":", "--", "-"]):
        v = CUSTO.loc[c, n]
        p = np.searchsorted(r, v) / len(r) * 100
        ax.axvline(v, color="#52514e", ls=ls, lw=1)
        ax.text(v, 3 + 14 * NIV.index(n), f" {NOME_NIV[n]}: {p:.0f}%", fontsize=7, color="#52514e")
    ax.axvspan(CUSTO.loc[c, "op_min"], CUSTO.loc[c, "op_max"], color="#f0efec", zorder=0)
    ax.set_title(c + (" (custo suposto)" if CUSTO.loc[c, "origem"].startswith("suposição") else ""), fontsize=10)
    ax.set_xlabel("custo por ha (R$ de 2025)")
axs[0, 0].set_ylabel("% dos anos que não pagam")
axs[1, 0].set_ylabel("% dos anos que não pagam")
fig.suptitle("Chance de a receita não pagar o custo, para qualquer custo (faixa clara = custo operacional do menor ao maior local da CONAB)", fontsize=11)
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 5.3 Ponto de equilíbrio
#
# - **Rendimento de equilíbrio** = custo ÷ preço de referência do município. Comparado com o rendimento mediano do
#   próprio município, diz quantas vezes a lavoura teria de render mais para pagar o custo.
# - **Preço de equilíbrio** = custo ÷ rendimento mediano do município. Comparado com o preço de referência, diz quanto o
#   preço teria de subir.
# - **Produtividade da planilha**: a CONAB calcula o custo para uma produtividade esperada. Se ela for muito maior que a
#   do PAM, o custo da planilha é de uma lavoura mais tecnificada que a média.

# %%
eq = []
for c in CULT:
    m = mm[(mm.produto == c) & (mm.rend > 0)]
    if not len(m):
        continue
    linha = {"cultura": c, "municípios": len(m), "rendimento mediano (kg/ha)": m.rend.median(), "preço de ref. (R$/kg)": m.preco.median(),
             "produtividade da planilha CONAB (kg/ha)": CUSTO.loc[c, "produtividade_conab"]}
    for n in ["desembolso", "custo_operacional"]:
        k = CUSTO.loc[c, n]
        linha[f"rend. de equilíbrio, {NOME_NIV[n]} (kg/ha)"] = (k / m.preco).median()
        linha[f"× o rendimento mediano ({NOME_NIV[n]})"] = (k / m.preco / m.rend).median()
        linha[f"preço de equilíbrio, {NOME_NIV[n]} (R$/kg)"] = (k / m.rend).median()
    eq.append(linha)
EQ = pd.DataFrame(eq).set_index("cultura")
EQ["planilha ÷ PAM"] = EQ["produtividade da planilha CONAB (kg/ha)"] / EQ["rendimento mediano (kg/ha)"]
display(EQ.round(2))

# %% [markdown]
# ### 5.4 Sensibilidade ao custo
#
# O custo central é um ponto. A figura mostra a fração dos municípios em que a margem mediana fica positiva quando o
# custo vai de 0 a 2 vezes o desembolso central (o eixo é o multiplicador). Para as culturas de custo suposto, é a única
# leitura honesta.

# %%
mult = np.linspace(0, 2, 41)
fig, ax = plt.subplots(figsize=(9, 4.6))
for c in CULT:
    m = mm[mm.produto == c]
    if len(m) < 20:
        continue
    k = CUSTO.loc[c, "desembolso"]
    y = [(m.R > k * f).mean() * 100 for f in mult]
    ax.plot(mult, y, color=COR[c], label=c + (" (suposto)" if CUSTO.loc[c, "origem"].startswith("suposição") else ""))
ax.axvline(1, color=CINZA, ls="--", lw=1)
ax.set_xlabel("custo = multiplicador × desembolso central da CONAB")
ax.set_ylabel("% dos municípios com margem mediana > 0")
ax.legend(frameon=False, fontsize=8, ncol=2)
ax.set_title("Quanto o custo pode subir antes de a margem virar prejuízo", fontsize=10)
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 5.5 Culturas sem preço de mercado na base
#
# Guandu, sorgo forrageiro, milheto, palma forrageira, gliricídia e mucuna-preta não têm série de preço nem de produção no
# PAM. O valor delas é **de uso**: forragem que substitui ração ou volumoso comprado, nitrogênio, cobertura do solo.
# Não achamos fonte de preço de forragem no NE com série; por isso **o notebook não põe número de receita nelas**. A
# única referência lida com custo é Lima et al. (2018a, Rev. Caatinga 31(1):191), em Serra Talhada-PE, irrigado (a lâmina
# "0%" recebeu 583 mm): consórcio palma + sorgo de R$ 12.422–12.564/ha contra R$ 11.893–12.034/ha da palma solteira,
# com B/C > 1,5 a partir do 2º ano, em reais correntes de 2012–2013 (`pesquisa/viabilidade_artigos_nordeste.md`, grau C).
# Não usamos esse número no cálculo: é ensaio único e irrigado.
#
# O que dá para dizer em reais é o **custo de oportunidade**: a forragem numa faixa precisa valer, por hectare, pelo menos
# a margem que o caupi ou o milho dariam na mesma faixa. A tabela mostra esse piso.

# %%
op = mm[mm.produto.isin(["Feijão", "Milho"])].groupby("produto").agg(
    receita_mediana=("R", "median"), margem_semente_mediana=("marg_semente", "median"),
    margem_desembolso_mediana=("marg_desembolso", "median"))
op["a forragem empata se valer (R$/ha), família que só compra semente"] = op.margem_semente_mediana.clip(lower=0)
op["a forragem empata se valer (R$/ha), desembolso da CONAB"] = op.margem_desembolso_mediana.clip(lower=0)
display(op.round(0))
q_op = mm[(mm.cod_mun == QUIXADA) & mm.produto.isin(["Feijão", "Milho"])].set_index("produto")[["R", "marg_semente", "marg_desembolso"]]
print("Quixadá (mediana 1998–2025):")
display(q_op.round(0))

# %% [markdown]
# **Leitura.**
# - **Custo da CONAB (R$ de 2025/ha):** feijão familiar de sequeiro, custo operacional central R$ 3.847 (faixa R$ 2.134
#   a 4.701), desembolso R$ 1.992 e semente R$ 142. Milho de Crateús-CE: R$ 1.845, R$ 1.136 e R$ 284. Mandioca:
#   R$ 8.678, R$ 4.387 e maniva sem custo na maioria das planilhas. Mamona de Irecê-BA: R$ 4.089 e R$ 2.656.
# - **A planilha é de uma lavoura melhor que a média:** ela supõe 3,4 vezes o rendimento mediano do PAM no milho, 2,3 no
#   feijão, 2,2 na mamona e 1,7 na mandioca.
# - **Margem mediana sobre o desembolso:** mandioca +R$ 3.261/ha; amendoim +R$ 1.765 e algodão +R$ 331 (custo
#   suposto); milho −R$ 519; feijão −R$ 584; mamona −R$ 683; sorgo −R$ 1.167 (suposto). **Sobre a semente, todas ficam
#   positivas:** feijão +R$ 1.267, milho +R$ 333.
# - **Chance de não pagar o desembolso** (mediana dos municípios): milho 86% dos anos, mamona 81%, feijão 75%, mandioca
#   11%. O custo operacional completo (com a diária) não é pago no ano mediano de milho, feijão, sorgo e mamona; a
#   mandioca o paga em 32% dos anos.
# - **Ponto de equilíbrio sobre o desembolso:** o feijão precisaria de 440 kg/ha (1,41 vez o mediano) ou de R$ 6,45/kg
#   (contra R$ 4,53); o milho, de 935 kg/ha (1,84 vez) ou R$ 2,13/kg (contra R$ 1,21). A mandioca paga o desembolso com
#   57% do rendimento mediano.
# - **O que isso quer dizer:** o roçado de milho e feijão do sertão **não paga a planilha da CONAB; paga a semente**. Ele
#   se sustenta porque a família não paga a própria diária (a CONAB a valoriza em ~R$ 1.855/ha no feijão), não aluga
#   máquina e consome boa parte da colheita como comida e forragem.
# - **Forragem:** numa faixa, a forragem empata com o caupi se valer pelo menos R$ 1.267/ha para a família que só compra
#   semente (R$ 333/ha contra o milho). Sobre o desembolso, qualquer valor positivo já empata, porque caupi e milho dão
#   prejuízo na mediana.
