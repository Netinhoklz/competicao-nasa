# %% [markdown]
# ## 2. Produtividade esperada: quanto cada cultura produz por hectare, e com que chance de perda
#
# Para cada município com série (≥ 10 anos válidos entre 1998 e 2025) e cada cultura:
# - **mediana, P10 e P90** do rendimento por **ha plantado** (o P10 é o "pior ano em 10" do próprio município);
# - **chance de quebra** = fração dos anos com rendimento < 0,5 do normal (mediana dos outros anos);
# - **perda de área** = 1 − área colhida ÷ área plantada (a parte do roçado que nem foi colhida).
#
# A tabela do NE é a mediana entre os municípios. A conferência com o catálogo de rotações vem primeiro: lá, a quebra do
# milho é de ~20% dos município-anos no CE e ~21% no NE (2000–2024, mediana da mesma janela).

# %%
# conferência com o catálogo (mesma janela e mesma mediana, área plantada ≥ 10 ha)
J = B[B.ano.between(2000, 2024)].copy()
J["med_janela"] = J.groupby(["cod_mun", "produto"]).rend_plantado_kg_ha.transform("median")
J["q_janela"] = J.rend_plantado_kg_ha < 0.5 * J.med_janela
conf = pd.DataFrame({"NE": J.groupby("produto").q_janela.mean() * 100,
                     "CE": J[J.uf == "CE"].groupby("produto").q_janela.mean() * 100}).reindex(["Milho", "Feijão", "Mandioca"])
print("Quebra (% dos município-anos), 2000–2024, mediana da mesma janela — catálogo: milho CE 20,2%, NE 21,0%")
display(conf.round(1))

S2 = B[B.n_anos >= ANOS_MIN]
mun = S2.groupby(["produto", "cod_mun"]).agg(
    mediana=("rend_plantado_kg_ha", "median"), p10=("rend_plantado_kg_ha", lambda s: s.quantile(0.1)),
    p90=("rend_plantado_kg_ha", lambda s: s.quantile(0.9)), colhido=("rend_colhido_kg_ha", "median"),
    p_quebra=("quebra", "mean"), perda_area=("perda_area", "mean"), anos=("ano", "size")).reset_index()
mun["uf"] = mun.cod_mun.str[:2].map(dict(zip(["21", "22", "23", "24", "25", "26", "27", "28", "29"], UFS)))
tab = mun.groupby("produto").agg(municipios=("cod_mun", "size"), mediana_kg_ha=("mediana", "median"), p10_kg_ha=("p10", "median"),
                                 p90_kg_ha=("p90", "median"), colhido_kg_ha=("colhido", "median"),
                                 quebra_pct=("p_quebra", lambda s: s.median() * 100), perda_area_pct=("perda_area", lambda s: s.median() * 100)
                                 ).reindex(CULT).dropna(how="all")
tab["P10/mediana"] = tab.p10_kg_ha / tab.mediana_kg_ha
# qualidade do relato: rendimento idêntico ao do ano anterior (número repetido, não medido de novo)
rep = S2.sort_values("ano").groupby(["cod_mun", "produto"]).rend_colhido_kg_ha.diff().abs() < 1e-6
consec = S2.sort_values("ano").groupby(["cod_mun", "produto"]).ano.diff() == 1
tab["rendimento repetido do ano anterior (%)"] = (rep & consec).groupby(S2.produto).sum() / consec.groupby(S2.produto).sum() * 100
tab["valor redondo (múltiplo de 100 kg/ha, %)"] = S2.groupby("produto").rend_colhido_kg_ha.apply(lambda s: (s.round(6) % 100 == 0).mean() * 100)
tab["municipios"] = tab.municipios.astype(int)
print("Rendimento por ha plantado (kg/ha; mandioca em kg de raiz): mediana entre os municípios com série")
display(tab.round(2))
mq = S2[S2.produto == "Milho"].set_index(["cod_mun", "ano"]).quebra
sel = (S2.produto == "Mandioca") & consec
rep_m = rep[sel]
cm = S2.loc[rep_m.index, ["cod_mun", "ano"]]
na_cauda = mq.reindex(pd.MultiIndex.from_frame(cm)).fillna(False).to_numpy().astype(bool)
print(f"Mandioca (anos seguidos): rendimento repetido do ano anterior em {rep_m.mean() * 100:.0f}% dos município-anos e em "
      f"{rep_m[na_cauda].mean() * 100:.0f}% dos município-anos em que o milho quebrou (n = {na_cauda.sum()})")

# %%
uf_tab = mun.pivot_table(index="uf", columns="produto", values="mediana", aggfunc="median").reindex(index=UFS, columns=CULT).dropna(axis=1, how="all")
uf_q = mun.pivot_table(index="uf", columns="produto", values="p_quebra", aggfunc="median").reindex(index=UFS, columns=uf_tab.columns) * 100
print("Rendimento mediano por ha plantado (kg/ha), por UF")
display(uf_tab.round(0))
print("Chance de quebra (% dos anos com < 0,5 do normal), mediana dos municípios, por UF")
display(uf_q.round(1))
sa = S2.assign(semiarido=S2.cod_mun.map(REFM.semiarido_2022)).groupby(["produto", "semiarido"]).agg(
    rend=("rend_plantado_kg_ha", "median"), quebra=("quebra", "mean")).unstack()
sa.columns = [f"{a}_{'semiárido' if b else 'fora'}" for a, b in sa.columns]
sa = sa.reindex(CULT).dropna(how="all")
sa[["quebra_fora", "quebra_semiárido"]] *= 100
print("Semiárido (delimitação 2022) contra o resto do NE: rendimento por ha plantado (kg/ha) e quebra (% dos município-anos)")
display(sa.round(1))

# %%
fig, axs = plt.subplots(2, 3, figsize=(15, 9.5))
for j, c in enumerate(["Milho", "Feijão", "Mandioca"]):
    m = mun[mun.produto == c].set_index("cod_mun")
    mapa_ne(axs[0, j], m.mediana, f"{c}: rendimento mediano (kg/ha plantado)", vmin=0, vmax=m.mediana.quantile(0.95), rotulo="kg/ha")
    mapa_ne(axs[1, j], m.p_quebra * 100, f"{c}: chance de quebra (% dos anos)", vmin=0, vmax=40, rotulo="% dos anos")
fig.suptitle("Produtividade e risco físico por município (1998–2025; só municípios com ≥ 10 anos de série)", fontsize=12)
plt.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(1, 2, figsize=(14, 4.6))
ordem = [c for c in CULT if c in tab.index]
for k, c in enumerate(ordem):
    r = S2[S2.produto == c].razao.clip(0, 2.5)
    q = r.quantile([0.1, 0.25, 0.5, 0.75, 0.9])
    axs[0].plot([q[0.1], q[0.9]], [k, k], color=COR[c], lw=2)
    axs[0].plot([q[0.25], q[0.75]], [k, k], color=COR[c], lw=7, solid_capstyle="butt")
    axs[0].plot(q[0.5], k, "o", color="#fcfcfb", ms=5, mec=COR[c])
axs[0].axvline(0.5, color=CINZA, ls="--", lw=1)
axs[0].text(0.52, len(ordem) - 0.6, "quebra (< 0,5)", fontsize=8, color="#52514e")
axs[0].set_yticks(range(len(ordem)), ordem)
axs[0].invert_yaxis()
axs[0].set_xlabel("rendimento do ano ÷ normal do município (P10–P90; barra = P25–P75; ponto = mediana)")
axs[0].set_title("Quanto o ano se afasta do normal", fontsize=10)
ano_q = S2[S2.produto.isin(["Milho", "Feijão", "Mandioca"])].groupby(["ano", "produto"]).quebra.mean().unstack() * 100
for c in ["Milho", "Feijão", "Mandioca"]:
    axs[1].plot(ano_q.index, ano_q[c], color=COR[c], label=c, marker="o", ms=3)
for a in EN_FORTE:
    axs[1].axvspan(a - 0.5, a + 0.5, color="#f0efec", zorder=0)
axs[1].axvspan(SECA[0] - 0.5, SECA[-1] + 0.5, color="#e1e0d9", alpha=0.5, zorder=0)
axs[1].text(EN_FORTE[0], 92, "faixas claras: El Niño forte; cinza: seca 2012–16", fontsize=8, color="#52514e")
axs[1].set_ylim(0, 100)
axs[1].set_ylabel("% dos municípios em quebra")
axs[1].legend(frameon=False, fontsize=8, loc="upper right")
axs[1].set_title("Quebra por ano no NE", fontsize=10)
plt.tight_layout()
plt.show()
anos_q = ano_q.round(0)
print("Quebra (% dos municípios) nos anos de El Niño forte e na seca:")
display(anos_q.loc[[a for a in EN_FORTE + SECA if a in anos_q.index]].T)

# %% [markdown]
# **Leitura.**
# - **Conferência:** a quebra do milho em 2000–2024 dá **21,2% no NE e 20,2% no CE**, igual ao catálogo (21,0% e 20,2%).
# - **Rendimento mediano por ha plantado:** milho 533 kg/ha, feijão 309, mandioca 9.289 kg de raiz, sorgo 1.061,
#   amendoim 1.000, algodão 600, mamona 545.
# - **Pior ano em 10 ÷ mediana:** 0,28 no milho, no algodão e na mamona; 0,35 no sorgo; 0,37 no feijão; **0,61 na
#   mandioca**; 0,80 no amendoim.
# - **Chance de quebra** (mediana dos municípios): milho 25% dos anos, algodão 23%, mamona 21%, feijão 18%, sorgo 17%,
#   mandioca 6%, amendoim 0%.
# - **O semiárido é outro mundo:** milho 421 contra 833 kg/ha fora dele, com quebra em 28% contra 8,5% dos anos;
#   feijão 270 contra 500 kg/ha, quebra 23% contra 4%. A mandioca quase não muda (9.000 contra 9.500 kg/ha).
# - **Por UF:** o RN tem a maior quebra de milho (36%) e de feijão (32%); MA, AL e SE, as menores (~7%).
# - **Os anos ruins:** em 1998, 59% dos municípios quebraram o milho, 44% o feijão e 13% a mandioca. Em 2012: 62%, 51% e
#   21%. Em 2016: 53%, 47% e 20%. Em 2024, El Niño forte, só 11%, 13% e 11%.
# - **Qualidade do relato:** a mandioca repete o rendimento do ano anterior em 33% dos anos seguidos (25% nos anos em
#   que o milho quebrou) e 73% dos valores são múltiplos de 100 kg/ha; o amendoim repete em 30%. Parte da estabilidade
#   da mandioca e do amendoim é do relato, não da roça. As seções 6 e 7 herdam esse viés.
