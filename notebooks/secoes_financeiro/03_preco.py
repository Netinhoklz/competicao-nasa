# %% [markdown]
# ## 3. Preço: o que a família recebe, quanto varia e como se compara ao mercado
#
# O preço implícito do PAM é o valor da produção ÷ a quantidade, em R$ de 2025 por kg (mandioca: kg de raiz). É uma
# média municipal: não diz o preço de cada venda, nem separa o que foi vendido do que ficou para a família.
#
# Medidas de volatilidade (2010–2025):
# - **CV da série do NE**: desvio-padrão ÷ média da mediana anual do NE;
# - **dp da variação anual**: desvio-padrão de ln(preço do ano ÷ preço do ano anterior);
# - **CV dentro do município**: a mesma conta na série de cada município (mediana entre os municípios);
# - **dispersão entre municípios**: no mesmo ano, (P75 − P25) ÷ mediana.

# %%
PR = B[B.ano.between(2010, 2025) & B.preco.notna()]
serie = PR.groupby(["produto", "ano"]).preco.median().unstack(0).reindex(columns=CULT)
fig, axs = plt.subplots(2, 4, figsize=(16, 6.5), sharex=True)
for ax, c in zip(axs.flat, CULT):
    s = serie[c].dropna()
    q = PR[PR.produto == c].groupby("ano").preco.quantile([0.25, 0.75]).unstack()
    ax.fill_between(q.index, q[0.25], q[0.75], color=COR[c], alpha=0.18, lw=0)
    ax.plot(s.index, s, color=COR[c], marker="o", ms=3)
    for a in EN_FORTE:
        ax.axvspan(a - 0.5, a + 0.5, color="#f0efec", zorder=0)
    ax.set_title(f"{c} (R$/kg de 2025)", fontsize=10)
    ax.set_ylim(0, None)
fig.suptitle("Preço implícito real: mediana do NE (linha) e faixa P25–P75 entre municípios; faixas claras = El Niño forte", fontsize=11)
plt.tight_layout()
plt.show()

vol = pd.DataFrame({
    "preço mediano 2016–25 (R$/kg)": PR[PR.ano.isin(PRECO_REF)].groupby("produto").preco.median(),
    "CV da série do NE (%)": serie.std() / serie.mean() * 100,
    "dp da variação anual (ln)": np.log(serie).diff().std(),
    "CV dentro do município (%)": PR.groupby(["produto", "cod_mun"]).preco.agg(lambda s: s.std() / s.mean() * 100 if len(s) >= 8 else np.nan).groupby("produto").median(),
    "dispersão entre municípios": PR.groupby(["produto", "ano"]).preco.agg(lambda s: (s.quantile(0.75) - s.quantile(0.25)) / s.median()).groupby("produto").median(),
    "tendência real (%/ano)": serie.apply(lambda s: np.polyfit(s.dropna().index, np.log(s.dropna()), 1)[0] * 100 if s.notna().sum() >= 5 else np.nan),
}).reindex(CULT)
display(vol.round(2))
puf = PR[PR.ano.isin(PRECO_REF)].pivot_table(index="uf", columns="produto", values="preco", aggfunc="median").reindex(index=UFS, columns=CULT)
print("Preço mediano 2016–2025 por UF (R$ de 2025/kg)")
display(puf.round(2))

# %% [markdown]
# **O preço sobe quando a safra cai?** Se sobe, o preço protege parte da renda no ano ruim (um "seguro natural").
# Testamos em duas escalas: no NE inteiro (preço mediano do ano contra a produção total do NE) e dentro do município
# (preço relativo à UF no ano contra a razão ao normal do rendimento do próprio município).

# %%
prod_ne = P[P.ano.between(2010, 2025)].groupby(["produto", "ano"]).producao_t.sum().unstack(0)
hedge = {}
for c in CULT:
    a = pd.concat([serie[c], prod_ne.get(c)], axis=1).dropna()
    rho_ne = a.corr(method="spearman").iloc[0, 1] if len(a) >= 8 else np.nan
    m = PR[PR.produto == c].copy()
    m["p_rel"] = np.log(m.preco / m.groupby(["uf", "ano"]).preco.transform("median"))
    m = m[m.razao.between(0.01, 5)]
    rho_mun = m[["p_rel", "razao"]].corr(method="spearman").iloc[0, 1] if len(m) > 50 else np.nan
    hedge[c] = {"ρ preço × produção do NE (anos)": rho_ne, "ρ preço relativo × razão do município": rho_mun, "n município-anos": len(m)}
display(pd.DataFrame(hedge).T.round(2))

# razão feijão ÷ milho por kg, semiárido do NE, 2010–2024 (o catálogo diz ≈ 3,61×, grau D)
fm = PR[PR.semiarido & PR.ano.between(2010, 2024) & PR.produto.isin(["Feijão", "Milho"])].pivot_table(index=["cod_mun", "ano"], columns="produto", values="preco")
fm = fm.dropna()
print(f"Preço do feijão ÷ milho no semiárido (2010–2024): mediana dos município-anos {num(np.median(fm.Feijão / fm.Milho))}× "
      f"(P25 {num((fm.Feijão / fm.Milho).quantile(.25))}, P75 {num((fm.Feijão / fm.Milho).quantile(.75))}); "
      f"razão das medianas {num(fm.Feijão.median() / fm.Milho.median())}×; n = {len(fm)}")

# %% [markdown]
# **Comparação com o mercado.** A FAOSTAT publica o preço ao produtor do Brasil inteiro (moeda local por tonelada); o
# Banco Mundial (Pink Sheet) publica o preço mundial em dólar. Usamos os dois só para comparar o nível (FAOSTAT,
# deflacionado pelo mesmo IPCA) e a volatilidade (variação anual em ln, sem unidade), não como preço local.

# %%
FAO_ITEM = {"Maize (corn)": "Milho", "Beans, dry": "Feijão", "Cassava, fresh": "Mandioca", "Sorghum": "Sorgo",
            "Groundnuts, excluding shelled": "Amendoim", "Seed cotton, unginned": "Algodão herbáceo",
            "Castor oil seeds": "Mamona", "Sunflower seed": "Girassol"}
fao = pd.read_parquet(DERIV / "faostat_precos_produtor.parquet")
fao = fao[(fao.Area == "Brazil") & (fao.Element == "Producer Price (LCU/tonne)") & (fao.Months == "Annual value") & fao.Item.isin(FAO_ITEM)]
ipa = pd.read_csv(F / "ipca_anual.csv").set_index("ano").fator_r2025
fao = fao.assign(produto=fao.Item.map(FAO_ITEM), preco=fao.Value / 1000 * fao.Year.map(ipa))
fao = fao[fao.Year.between(2010, 2025)].pivot_table(index="Year", columns="produto", values="preco")
comp = pd.DataFrame({"PAM NE 2016–25 (R$/kg)": serie.loc[2016:2025].median(),
                     "FAOSTAT Brasil 2016–25 (R$/kg)": fao.loc[2016:2025].median(),
                     "anos FAOSTAT": fao.loc[2010:2025].notna().sum()}).reindex(CULT)
comp["NE ÷ Brasil"] = comp.iloc[:, 0] / comp.iloc[:, 1]
comp["ρ das variações anuais"] = [np.log(serie[c]).diff().corr(np.log(fao[c]).diff()) if c in fao and fao[c].notna().sum() >= 8 else np.nan for c in CULT]
display(comp.round(2))

pk = pd.read_parquet(DERIV / "mercado_precos_mensal.parquet")
PINK = {"Maize": "Milho", "Sorghum": "Sorgo", "Groundnuts": "Amendoim", "Cotton, A Index": "Algodão herbáceo (pluma)", "Sunflower oil": "Girassol (óleo)"}
pk = pk[pk.commodity.isin(PINK)]
pa = pk.assign(ano=pk.data.dt.year).groupby(["commodity", "ano"]).preco.mean().unstack(0)
pa = pa.loc[2010:2025]
vm = pd.DataFrame({"dp da variação anual (ln), mundo US$": np.log(pa).diff().std(), "anos": pa.notna().sum()})
vm.index = vm.index.map(PINK)
display(vm.round(2))

# %% [markdown]
# **Leitura.**
# - **Preço mediano 2016–2025** (R$ de 2025/kg): feijão 4,43; amendoim 3,89; mamona 3,49; algodão 3,36; milho 1,18;
#   mandioca 0,75; sorgo 0,71.
# - **Feijão ÷ milho = 3,61×** no semiárido (2010–2024; P25 3,00, P75 4,51; n = 16.672). Confirma o 3,61 do catálogo.
# - **Volatilidade:** a mediana do NE varia pouco de um ano para o outro (dp do ln de 0,12 a 0,23; a maior é a do
#   feijão). O preço mundial em dólar varia mais (0,20–0,24 no milho, sorgo, amendoim e algodão). Dentro do município, o
#   CV vai de 23% (milho) a 36% (mandioca). No mesmo ano, a mandioca tem a maior dispersão entre municípios (0,69): é
#   mercado local.
# - **Tendência real:** amendoim +6,4%/ano, mamona +5,3%, mandioca +4,0%, algodão +2,8%, milho +1,4%, feijão +0,9%.
# - **"Seguro natural" só regional:** no NE inteiro, o preço do feijão sobe quando a produção cai (ρ −0,79), e o da
#   mandioca também (ρ −0,60); o do milho, não (+0,36). Dentro do município, o preço relativo não acompanha a quebra
#   local (ρ de −0,08 a +0,11). A família só ganha preço alto quando a região toda quebra.
# - **FAOSTAT:** o feijão do NE vale o mesmo que o do Brasil (1,00×); o milho vale 1,36× (o NE compra milho de fora); a
#   mandioca, 0,88×. As variações anuais do milho e do feijão andam com as do Brasil (ρ 0,83 e 0,79); as da mandioca,
#   não (0,15).
