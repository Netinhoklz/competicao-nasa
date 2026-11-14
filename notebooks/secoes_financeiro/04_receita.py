# %% [markdown]
# ## 4. Receita bruta por hectare: plantado, colhido e por mês de terra
#
# **Receita observada** = valor da produção (R$ de 2025) ÷ área, 2010–2025. Por **ha plantado**, o ano de perda total
# entra como receita zero; por **ha colhido**, ele some (a área colhida é zero). A diferença entre as duas mede o
# quanto a perda de área esconde.
#
# **Receita por hectare-mês** = receita por ha plantado ÷ meses de ocupação da terra (tabela `CICLO`, seção 1). Ela
# responde a outra pergunta: com a mesma terra e o mesmo tempo, qual cultura gera mais dinheiro. Os ciclos são
# parâmetros (só a mandioca tem a duração escrita numa fonte oficial lida, a planilha da CONAB), então a figura mostra a
# faixa de cada um.

# %%
RO = B[B.ano.between(2010, 2025) & (B.n_anos >= ANOS_MIN)]
rm = RO.groupby(["produto", "cod_mun"]).agg(plantado=("R_obs", "median"), colhido=("R_obs_col", "median"),
                                            p10=("R_obs", lambda s: s.quantile(0.1)), p90=("R_obs", lambda s: s.quantile(0.9)),
                                            zero=("R_obs", lambda s: (s <= 0).mean())).reset_index()
rec = rm.groupby("produto").agg(municipios=("cod_mun", "size"), plantado=("plantado", "median"), colhido=("colhido", "median"),
                                p10=("p10", "median"), p90=("p90", "median"), anos_receita_zero_pct=("zero", lambda s: s.mean() * 100)).reindex(CULT).dropna(how="all")
rec["municipios"] = rec.municipios.astype(int)
rec["colhido ÷ plantado"] = rec.colhido / rec.plantado
rec["meses de ciclo"] = CICLO.dias.reindex(rec.index) / 30.4
rec["por ha-mês"] = rec.plantado / rec["meses de ciclo"]
rec["por ha-mês (faixa do ciclo)"] = [f"{brl(rec.plantado[c] / (CICLO.dias_max[c] / 30.4))} a {brl(rec.plantado[c] / (CICLO.dias_min[c] / 30.4))}" for c in rec.index]
print("Receita observada, R$ de 2025 por ha (mediana entre os municípios da mediana 2010–2025 de cada um)")
display(rec.round(2))

fig, axs = plt.subplots(1, 2, figsize=(15, 4.8))
ordem = list(rec.index)
for k, c in enumerate(ordem):
    s = RO[RO.produto == c]
    q = s.R_obs.quantile([0.1, 0.5, 0.9])
    qc = s.R_obs_col.quantile([0.1, 0.5, 0.9])
    axs[0].plot([max(q[0.1], 10), q[0.9]], [k - 0.12, k - 0.12], color=COR[c], lw=5, solid_capstyle="butt")
    axs[0].plot(q[0.5], k - 0.12, "o", color="#fcfcfb", mec=COR[c], ms=6)
    axs[0].plot([max(qc[0.1], 10), qc[0.9]], [k + 0.18, k + 0.18], color=COR[c], lw=2, alpha=0.6)
    axs[0].plot(qc[0.5], k + 0.18, "|", color=COR[c], ms=10)
axs[0].set_xscale("log")
axs[0].set_yticks(range(len(ordem)), ordem)
axs[0].invert_yaxis()
axs[0].set_xlabel("R$ de 2025 por ha (escala log; P10–P90 dos município-anos)")
axs[0].set_title("Por ha plantado (barra grossa) e por ha colhido (linha fina)", fontsize=10)
hm = rec["por ha-mês"].sort_values()
lo = [rec.plantado[c] / (CICLO.dias_max[c] / 30.4) for c in hm.index]
hi = [rec.plantado[c] / (CICLO.dias_min[c] / 30.4) for c in hm.index]
axs[1].barh(range(len(hm)), hm.values, color=[COR[c] for c in hm.index], height=0.6)
axs[1].errorbar(hm.values, range(len(hm)), xerr=[hm.values - lo, np.array(hi) - hm.values], fmt="none", ecolor="#52514e", capsize=3, lw=1)
for k, (c, v) in enumerate(hm.items()):
    axs[1].text(hi[k] + 8, k, brl(v), va="center", fontsize=8, color="#52514e")
axs[1].set_yticks(range(len(hm)), hm.index)
axs[1].set_xlabel("R$ de 2025 por ha-mês (mediana; traço = faixa do ciclo)")
axs[1].set_title("Receita por mês de terra ocupada", fontsize=10)
plt.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
for ax, c in zip(axs, ["Milho", "Feijão", "Mandioca"]):
    m = rm[rm.produto == c].set_index("cod_mun").plantado
    mapa_ne(ax, m, f"{c}: receita mediana 2010–2025 (R$/ha plantado)", vmin=0, vmax=m.quantile(0.95), rotulo="R$ de 2025/ha")
plt.tight_layout()
plt.show()
ruf = rm.assign(uf=rm.cod_mun.str[:2].map(dict(zip(["21", "22", "23", "24", "25", "26", "27", "28", "29"], UFS)))).pivot_table(
    index="uf", columns="produto", values="plantado", aggfunc="median").reindex(index=UFS, columns=CULT).dropna(axis=1, how="all")
print("Receita observada mediana por UF (R$ de 2025 por ha plantado)")
display(ruf.round(0))

# %%
# conferência: a receita a preço de referência (usada nas seções 5 a 10) contra a observada, nos mesmos município-anos
cf = RO.dropna(subset=["R", "R_obs"])
c2 = pd.DataFrame({"mediana observada": cf.groupby("produto").R_obs.median(), "mediana a preço de ref.": cf.groupby("produto").R.median(),
                   "ρ de Spearman": cf.groupby("produto").apply(lambda g: g.R.corr(g.R_obs, method="spearman")),
                   "dp ln(observada ÷ ref.)": cf[(cf.R > 0) & (cf.R_obs > 0)].groupby("produto").apply(lambda g: np.log(g.R_obs / g.R).std())}).reindex(CULT)
display(c2.round(2))

# %% [markdown]
# **Leitura.**
# - **Receita observada mediana, 2010–2025, por ha plantado:** mandioca R$ 5.342; amendoim R$ 3.633; algodão R$ 1.567;
#   feijão R$ 1.182; mamona R$ 735; sorgo R$ 688; milho R$ 598.
# - **Por ha colhido**, milho, feijão, algodão e mamona ficam 13% a 21% acima: o PAM por área colhida esconde a perda de
#   área. Na mandioca e no amendoim a diferença é de 2–3%.
# - **Por ha-mês, a ordem muda:** amendoim R$ 1.104; **feijão R$ 513** (R$ 479 a 599 com ciclo de 60 a 75 dias);
#   mandioca R$ 356 (R$ 296 a 445 para 12 a 18 meses); algodão R$ 340; sorgo R$ 190; milho R$ 165; mamona R$ 124. O
#   caupi precoce é o que mais rende por mês de terra entre as culturas do roçado; a mandioca rende muito por hectare,
#   mas prende a terra por mais de um ano.
# - **Por UF:** a mandioca rende R$ 9.248/ha em AL e R$ 9.013 em PE, contra R$ 3.522 no PI; o milho rende R$ 2.426 em SE
#   e R$ 1.153 no MA, contra R$ 303 no RN e R$ 314 em PE.
# - **Conferência:** a receita a preço de referência acompanha a observada (ρ de 0,72 a 0,98). Fica acima na mandioca
#   (+17%), no algodão (+23%) e na mamona (+64%), porque o preço real dessas culturas subiu desde 2010 e a referência é
#   a de 2016–2025.
