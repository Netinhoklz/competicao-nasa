# %% [markdown]
# ## 3. Cruzamento GAEZ × ZARC: a situação de cada cultura em cada município
#
# É a tabela que o motor consulta (`E:/campeonato-nasa/dados/gaez_zarc/nordeste_2026-2027.csv`, gerada por
# `scripts/preparar_prototipo_nordeste.py gaez_zarc` com as funções de `gaez_zarc_municipio.py`). A regra foi decidida em
# 14/11, **no nível do município**:
# - se a cultura tem ZARC no município, **o ZARC decide** ("indicada" = risco de 20% em alguma combinação solo × ciclo;
#   "com risco" = o melhor é 30% ou 40%; "fora" = não zoneada). O GAEZ vira rótulo;
# - se não tem ZARC no município, **o GAEZ decide**: aptidão > 40 com insumo baixo = "só aptidão"; senão, "fora". A mamona
#   não tem camada no GAEZ: sem ZARC, fica fora.
# - Mandioca, guandu e milheto não estão na tábua aberta do ZARC. **No CE, a mandioca e o milheto seguem a portaria
#   plurianual** quando o município está nela (`motor.zarc_plurianual`, seção 2); a palma também, mas ela não tem camada
#   no GAEZ e fica fora das 12 culturas desta tabela.
# - Esta seção junta a tábua com a regra das plurianuais do CE e confere o resultado com o próprio `motor.cardapio`.
#
# A pergunta estatística é: **o GAEZ e o ZARC concordam?** Onde o GAEZ dá aptidão maior, a janela do ZARC é mais longa?

# %%
X = M.GZT.copy()  # a mesma tabela que o motor carregou
menu = ["Feijão Caupi", "Milho 1ª Safra", "Feijão 2ª Safra", "mandioca", "Amendoim", "Sorgo Granífero", "guandu",
        "Sorgo Forrageiro", "milheto", "Algodão Herbáceo", "Mamona", "Girassol"]
X = X[X.cultura.isin(menu)].copy()
X["fonte"] = np.where(X.zarc_no_municipio, "ZARC (tábua aberta)", "GAEZ")
for nome_m, cult in [("Mandioca", "mandioca"), ("Milheto", "milheto")]:  # no CE, a portaria plurianual decide (seção 2)
    s_ = SIT_PLUR[nome_m][SIT_PLUR[nome_m] != "fora da portaria"]
    sel_ = (X.cultura == cult) & X.geocodigo.isin(s_.index)
    X.loc[sel_, "situacao"] = X.loc[sel_, "geocodigo"].map(s_)
    X.loc[sel_, "fonte"] = "ZARC plurianual (CE)"
# conferência: a mesma situação que a página mostra (motor.cardapio no ponto interno), em 60 municípios do CE (onde entram
# as plurianuais) e em 30 por UF nas outras 8. A janela por solo não entra na situação; ela fica desligada durante a
# conferência, e a consulta às plurianuais fica em cache, só para o laço ser rápido.
nome_x = {nome: (z or g) for nome, _, g, z, _ in M.CARDAPIO if (z or g) in menu}
sx = X.set_index(["geocodigo", "cultura"]).situacao
amostra = list(MUN.cod[MUN.uf == "CE"].sample(60, random_state=0)) + list(MUN[MUN.uf != "CE"].groupby("uf").cod.apply(lambda s: s.sample(30, random_state=0)).explode())
iguais = total = 0
_jps = M.janelas_por_solo
_zp = M.zarc_plurianual
M.janelas_por_solo = lambda cod, cultura: []
M.zarc_plurianual = __import__("functools").lru_cache(maxsize=None)(_zp)
try:
    for cod in amostra:
        si_ = {(c, "Low"): GB.at[cod, c] for c in GB.columns} | {(c, "High"): GA.at[cod, c] for c in GA.columns}
        for it in M.cardapio({"cod": cod, "uf": UFMUN[cod]}, si_):
            if it["cultura"] in nome_x:
                total += 1
                iguais += it["situacao"] == sx[(cod, nome_x[it["cultura"]])]
finally:
    M.janelas_por_solo, M.zarc_plurianual = _jps, _zp
print(f"Conferência com motor.cardapio: {iguais} de {total} pares município × cultura com a mesma situação ({len(amostra)} municípios)")
print("De onde vem a decisão (pares município × cultura):")
display(pd.crosstab(X.cultura, X.fonte).reindex(menu))
print(f"{X.geocodigo.nunique()} municípios × {X.cultura.nunique()} culturas com dado = {len(X)} linhas; "
      f"ciclos conferidos (só CE): {int(X.ciclos_conferidos.sum())} linhas")
sit_ordem = ["indicada", "com risco", "só aptidão", "fora"]
T = pd.crosstab(X.cultura, X.situacao).reindex(index=menu, columns=sit_ordem, fill_value=0)
fig, ax = plt.subplots(figsize=(11, 5.2))
esq = np.zeros(len(T))
for i, s in enumerate(sit_ordem):
    ax.barh(T.index, T[s], left=esq, color=[CAT[2], CAT[3], CAT[0], CINZA][i], label=s, height=0.65, edgecolor="#fcfcfb", linewidth=1.5)
    esq += T[s].values
ax.invert_yaxis()
ax.set_xlabel(f"municípios (de {X.geocodigo.nunique()})")
ax.legend(ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False)
ax.set_title("Situação de cada cultura do cardápio no NE (ZARC 2026/27 + GAEZ v4)", pad=28)
plt.show()
display(T.assign(total=T.sum(1)))

# %%
X["disponivel"] = X.situacao.isin(["indicada", "só aptidão"])
P = X.pivot_table(index="cultura", columns="uf", values="disponivel", aggfunc="mean").reindex(index=menu, columns=UF_ORDEM) * 100
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(P.values, cmap=SEQ, vmin=0, vmax=100, aspect="auto")
ax.set_xticks(range(9))
ax.set_xticklabels(UF_ORDEM)
ax.set_yticks(range(len(menu)))
ax.set_yticklabels(menu, fontsize=8)
for i in range(P.shape[0]):
    for j in range(P.shape[1]):
        ax.text(j, i, f"{P.values[i, j]:.0f}", ha="center", va="center", fontsize=7, color="#fcfcfb" if P.values[i, j] > 60 else "#0b0b0b")
ax.grid(False)
plt.colorbar(im, ax=ax, label="% dos municípios", shrink=0.8)
ax.set_title("% dos municípios onde a cultura está disponível (indicada ou só aptidão), por UF")
plt.show()
print("De onde vem a decisão: % dos municípios em que a cultura tem ZARC (o ZARC decide), por UF:")
display((X[X.cultura.isin(MENU_Z)].pivot_table(index="cultura", columns="uf", values="zarc_no_municipio", aggfunc="mean")
         .reindex(index=MENU_Z, columns=UF_ORDEM) * 100).round(0))
disp = X[X.disponivel].groupby("geocodigo").cultura.nunique().reindex(MUN.cod, fill_value=0)
print(f"Culturas disponíveis por município (de 12 com dado): nenhuma em {int((disp == 0).sum())} municípios, até 3 em {int((disp <= 3).sum())}. Por UF:")
display(disp.groupby(UFMUN.reindex(disp.index).values).describe()[["min", "25%", "50%", "75%", "max"]].reindex(UF_ORDEM).T)
ex = MUN[(MUN.municipio.isin(["Quixadá", "Barreiras", "Arapiraca", "Balsas"]))].set_index("cod")
print("Exemplos (situação de cada cultura):")
display(X[X.geocodigo.isin(ex.index)].pivot_table(index="cultura", columns="municipio", values="situacao", aggfunc="first").reindex(menu))

# %%
# o GAEZ concorda com o ZARC? aptidão (insumo baixo) × nº de decêndios com risco de 20% (união de solos e ciclos)
pares = {"Feijão Caupi": "feijão-caupi", "Milho 1ª Safra": "milho", "Feijão 2ª Safra": "feijão (Phaseolus)", "Sorgo Granífero": "sorgo",
         "Sorgo Forrageiro": "sorgo", "Amendoim": "amendoim", "Algodão Herbáceo": "algodão", "Girassol": "girassol"}
res = []
for cz, cg in pares.items():
    q_ = JJ[JJ.Nome_cultura == cz].set_index("cod")
    a_ = GB[cg].reindex(q_.index)
    rho, p = stats.spearmanr(a_, q_.n20_uniao)
    dentro = [stats.spearmanr(a_[q_.uf == u], q_.n20_uniao[q_.uf == u])[0] for u in UF_ORDEM if (q_.uf == u).sum() >= 20]
    res.append({"cultura": cz, "n": len(q_), "Spearman NE": round(rho, 2), "p": float(f"{p:.2g}"),
                "Spearman dentro da UF (mediana)": round(float(np.nanmedian(dentro)), 2),
                "UFs com Spearman < 0": int(np.sum(np.array(dentro) < 0)), "UFs avaliadas": len(dentro),
                "indicada pelo ZARC e GAEZ ≤ 40": int(((a_ <= GZ.APTA) & (q_.n20_uniao > 0)).sum())})
R = pd.DataFrame(res).set_index("cultura")
display(R)
corte = X[(X.situacao == "indicada") & (X["SI baixo"] <= GZ.APTA)].groupby("geocodigo").size().reindex(MUN.cod, fill_value=0)
print(f"Pares município × cultura indicados pelo ZARC que um corte pelo GAEZ (≤ {GZ.APTA}) derrubaria: {int(corte.sum())}, "
      f"em {int((corte > 0).sum())} municípios ({(corte > 0).mean():.0%} do NE)")
fig, axs = plt.subplots(1, 2, figsize=(14, 6.5))
mapa_ne(axs[0], disp, "Culturas disponíveis (regra decidida, de 12)", vmin=0, vmax=12, rotulo="culturas")
mapa_ne(axs[1], corte, f"Culturas indicadas pelo ZARC que o corte pelo GAEZ (≤ {GZ.APTA}) derrubaria", vmin=0, vmax=9, rotulo="culturas")
plt.tight_layout()
plt.show()

# %% [markdown]
# **Leitura:**
# - **A tabela reproduz a página:** a situação bate com `motor.cardapio` em 3.600 de 3.600 pares município × cultura (60
#   municípios do CE, onde entram as plurianuais, e 30 em cada uma das outras 8 UFs).
# - **Com a regra decidida, a mamona é a cultura mais indicada** (1.553 de 1.794 municípios). Depois vêm caupi (1.459),
#   sorgo granífero (1.410), amendoim (1.363), algodão (1.355) e sorgo forrageiro (1.352). O milho é indicado em 1.154 e
#   fica "com risco" em 370; o girassol é indicado em 793.
# - **De onde vem a decisão:**
#   - o GAEZ decide o guandu nos 1.794 municípios e a mandioca e o milheto nos 1.610 de fora do CE ("só aptidão": mandioca
#     em 1.048, guandu em 833, milheto em 433);
#   - **no CE, a mandioca e o milheto seguem a portaria plurianual** e ficam indicados nos 184 municípios;
#   - nas culturas da tábua aberta, o GAEZ decide pouco. As exceções são o girassol (sem ZARC em 631 municípios; ZARC em
#     só 21% do MA e 47% do PI) e o milho (sem ZARC em 270; ZARC em 60% da BA).
# - **Culturas disponíveis por município:** mediana de 11 (de 12) no CE, com as plurianuais; 10 em AL e SE; 9 em RN, PB e
#   PE; 8 na BA; 7 no MA e no PI. **22 municípios não têm nenhuma**, quase todos no centro da BA, e 140 têm até 3.
# - **Exemplos:** em Quixadá, milho e feijão de 2ª safra ficam "com risco", o girassol fica fora, mandioca e milheto são
#   indicados pela portaria plurianual, e o guandu entra pela aptidão. Balsas, Barreiras e Arapiraca têm as 9 culturas da
#   tábua aberta indicadas.
# - **O GAEZ e o ZARC NÃO concordam no NE.** A aptidão e o comprimento da janela de 20% têm correlação negativa em 7 de 8
#   culturas:
#   - amendoim −0,54; milho −0,52; algodão −0,37; feijão de 2ª safra −0,29; caupi −0,25; sorgo forrageiro −0,19; sorgo
#     granífero −0,10;
#   - só o girassol é positivo (+0,29);
#   - dentro de cada UF, a mediana continua negativa (sorgo −0,46 e −0,47; amendoim −0,42; milho −0,33; caupi −0,06).
#     Então não é só efeito de comparar estados.
# - **Se o GAEZ cortasse (≤ 40), cairiam 7.285 pares município × cultura que o ZARC indica (tábua aberta e plurianuais do
#   CE), em 1.351 municípios (75% do NE).** Isso sustenta a regra: onde há ZARC, o ZARC decide.
