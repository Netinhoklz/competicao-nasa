# %% [markdown]
# ## 5. Análogos climáticos: quanto cada estudo vale em cada lugar
#
# - **Referências** (regeradas em 14/11 com a Tmax média):
#   - `analogos_artigos/assinaturas.csv`: 20 lugares de artigos e 12 pontos do CE. A média e o desvio dos 32 pontos
#     padronizam as variáveis; os 20 lugares de artigos são os candidatos a análogo;
#   - `analogos_aprofundado/catalogo_lugares_assinaturas.csv`: os 31 lugares dos cartões do catálogo com lugar.
# - **Distância:** euclidiana nas 6 variáveis padronizadas. **Peso de transferência:** w = exp(−d²/2) (`motor.analogos`).
# - **Confiança no protótipo** (w do melhor estudo, **arredondado a 2 casas antes de classificar**, revisão M16):
#   - w ≥ 0,6: "estudos de clima muito parecido";
#   - de 0,3 a 0,6: "parecido";
#   - < 0,3: "a evidência vale só como direção".
# - **Evidência perto:** os cartões cujo lugar tem w ≥ 0,3 (até 12 na página).
# - **Franke ponderado pelo clima** (leguminosa → cereal): só aparece quando a soma dos w dos 3 estratos do Franke é ≥ 0,3
#   (revisão M19).

# %%
z_m = (PW[VARS] - M.MU) / M.SD
dist_s = np.sqrt((((z_m.values[:, None, :] - ((SIT[VARS] - M.MU) / M.SD).values[None]) ** 2).sum(2)))
dist_l = np.sqrt((((z_m.values[:, None, :] - ((LA[VARS] - M.MU) / M.SD).values[None]) ** 2).sum(2)))
Ws = pd.DataFrame(np.exp(-dist_s ** 2 / 2), index=PW.index, columns=SIT.ponto)
Wl = pd.DataFrame(np.exp(-dist_l ** 2 / 2), index=PW.index, columns=LA.lugar)
melhor = Ws.max(1).round(2)
# conferência com o motor em 3 municípios
for cod in ["2311306", "2611606", "2903201"]:
    S_, _ = M.analogos({k: float(PW.loc[cod, k]) for k in VARS})
    assert round(float(S_.iloc[0].w), 2) == melhor[cod] and S_.iloc[0].ponto == Ws.loc[cod].idxmax()
print(f"Melhor w entre os {len(SIT)} lugares de artigos, nos {len(PW)} municípios (conferido com motor.analogos):")
display(descreve(melhor.rename("melhor w")))
conf = pd.cut(melhor, [-0.01, 0.295, 0.595, 1.0], labels=["< 0,3 (só direção)", "0,3–0,6 (parecido)", "≥ 0,6 (muito parecido)"])
display(pd.crosstab(PW.uf, conf, margins=True, margins_name="total").reindex(UF_ORDEM + ["total"]))
print("Mediana do melhor w por UF:")
display(por_uf(melhor).round(2).to_frame("mediana").T)

# %%
lug_m = Ws.idxmax(1)
top = lug_m.value_counts()
print("Lugar de artigo mais parecido (nº de municípios):")
display(top.rename("municípios").to_frame().T)
cats = list(top.index[:7])
rot = lambda s: s.split(" (")[0] if "(" in s and not s.startswith(("África", "Cerrado")) else s.replace(", aprox.", "")  # noqa: E731
cores = {rot(c): CAT[i] for i, c in enumerate(cats)} | {"outros": CINZA}
fig, axs = plt.subplots(1, 2, figsize=(15, 7))
mapa_ne(axs[0], melhor, "Melhor w (lugares de artigos)", vmin=0, vmax=1, rotulo="w")
mapa_ne(axs[1], lug_m.map(lambda s: rot(s) if s in cats else "outros"), "Lugar de artigo mais parecido", categorias=cores)
plt.tight_layout()
plt.show()

# %%
LUG = pd.read_csv(D_APR / "catalogo_cartao_lugar.csv").dropna()
cartoes_w = pd.Series((Wl[LUG.lugar].values >= 0.3).sum(1), index=PW.index)
fr = ["franke_sahel", "franke_guine", "franke_austral"]
soma_fr = Wl[[M.LUG[c] for c in fr]].sum(1)
print(f"Cartões com lugar: {len(LUG)}; lugares distintos: {LUG.lugar.nunique()}")
print("Cartões do catálogo com w ≥ 0,3 por município (a 'evidência perto' que a página mostra, até 12):")
display(cartoes_w.groupby(PW.uf).describe()[["min", "25%", "50%", "75%", "max"]].reindex(UF_ORDEM).T)
print(f"Franke ponderado pelo clima aparece (soma dos w ≥ 0,3) em {int((soma_fr >= 0.3).sum())} de {len(PW)} municípios; por UF (%):")
display(((soma_fr >= 0.3).groupby(PW.uf).mean() * 100).reindex(UF_ORDEM).round(0).to_frame("%").T)
fig, axs = plt.subplots(1, 2, figsize=(15, 6.5))
mapa_ne(axs[0], cartoes_w, f"Cartões com w ≥ 0,3 (de {len(LUG)} com lugar)", vmin=0, vmax=int(cartoes_w.max()), rotulo="cartões")
mapa_ne(axs[1], soma_fr, "Soma dos w dos 3 estratos do Franke", vmin=0, vmax=1.5, rotulo="soma dos w")
plt.tight_layout()
plt.show()

# %%
# CE: antes e depois da correção da Tmax (mesma regra de classificação)
oldA = pd.read_csv(DADOS / "analogos_artigos" / "assinaturas_tmax_recorde.csv")
SITo = oldA[oldA.grupo != "Ceará (alvo)"].reset_index(drop=True)
MUo, SDo = oldA[VARS].mean(), oldA[VARS].std()
do = np.sqrt(((((old[VARS] - MUo) / SDo).values[:, None, :] - ((SITo[VARS] - MUo) / SDo).values[None]) ** 2).sum(2))
Wo = pd.DataFrame(np.exp(-do ** 2 / 2), index=old.index, columns=SITo.ponto)
bo = Wo.max(1).round(2)
ce = melhor[PW.uf == "CE"]
classe = lambda w: pd.cut(w, [-0.01, 0.295, 0.595, 1.0], labels=["< 0,3", "0,3–0,6", "≥ 0,6"]).value_counts().sort_index()  # noqa: E731
print("CE, 184 municípios — confiança com a Tmax recorde (antes) e com a Tmax média (agora):")
display(pd.DataFrame({"antes": classe(bo), "agora": classe(ce)}).T)
display(pd.DataFrame({"antes": Wo.idxmax(1).value_counts().head(5), "agora": Ws.loc[ce.index].idxmax(1).value_counts().head(5)}).fillna(0).astype(int))

# %% [markdown]
# **Leitura:**
# - **1.080 dos 1.794 municípios (60%) têm um estudo de clima muito parecido** (w ≥ 0,6); 416 têm um parecido (0,3–0,6) e
#   298 só direção (< 0,3). A mediana do melhor w é 0,67.
# - **A confiança cai a oeste e ao sul:**
#   - na PB, no CE, no PI e no RN, a mediana do melhor w fica entre 0,76 e 0,92. O CE tem 182 de 184 municípios com w ≥ 0,6;
#   - no MA (mediana 0,35) e na BA (0,46), 90 e 150 municípios ficam abaixo de 0,3;
#   - em AL, 73 de 102 ficam em "parecido".
# - **De onde vem a evidência:** Bom Jesus-PI (Cerrado piauiense) é o lugar mais parecido para 422 municípios;
#   Esperança-PB, para 412; Serra Talhada-PE, 277; Embu (planalto da África Oriental), 223; Teresina, 159. Harare fica com
#   24.
# - **Densidade de evidência:** mediana de 22 cartões com w ≥ 0,3 no CE, no RN e na PB, contra 9 na BA e 4 no MA (mínimo
#   de 0 no MA, em SE e na BA). A página mostra até 12.
# - **O Franke ponderado pelo clima aparece em 1.017 municípios** (soma dos w ≥ 0,3): 99% no CE e 95% no PI, mas 18% na BA
#   e 39% no MA.
# - **A correção da Tmax mudou os análogos do CE:**
#   - w ≥ 0,6 passou de 158 para 182 municípios, e < 0,3, de 7 para 0. (O notebook antigo dava 154 porque classificava sem
#     arredondar; com a regra do motor, a Tmax recorde dá 158.)
#   - Harare deixou de ser o mais parecido em 53 municípios (agora, 11); Sobral caiu de 78 para 40; Bom Jesus subiu de 42
#     para 102.
# - **No produto:** onde o melhor w fica abaixo de 0,3 (298 municípios, quase todos no MA e na BA), a evidência vale só
#   como direção.
