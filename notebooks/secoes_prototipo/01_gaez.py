# %% [markdown]
# ## 1. FAO GAEZ v4: o que cabe no lugar
#
# **Ficha técnica**
# - **O que é:** modelo de zonas agroecológicas da FAO e do IIASA (Fischer et al. 2021, `10.4060/cb4744en`).
# - **Variável usada:** índice de aptidão (0–10000, aqui dividido por 100, com **uma casa decimal**), "toda a terra da
#   célula", em sequeiro, com insumo baixo e insumo alto.
# - **Clima de base:** 1981–2010 (CRU-TS 3.2).
# - **Grade:** 5' (~9,3 km no equador).
# - **Culturas na seleção (15, em 30 camadas):** milho, caupi, feijão comum, mandioca, amendoim, sorgo, guandu, milheto,
#   algodão, girassol, soja, arroz irrigado, banana, cana e trigo. O cardápio usa 10 delas.
# - **Classes oficiais da v4** (camada de classes siLr, conferida pela revisão A3): > 85 muito alta; > 70 alta; > 55 boa;
#   > 40 média; > 25 moderada; > 10 marginal; > 0 muito marginal. **Corte "apta": > 40** (média ou melhor), decisão do
#   projeto (`gaez_zarc_municipio.APTA`).
# - **Amostragem:** no ponto interno de cada um dos 1.794 municípios, com a mesma função do motor (`gaez_zarc_municipio.aptidao`).
#
# **No protótipo:**
# - rótulo de aptidão no cardápio (com insumo baixo; o insumo alto é só rótulo, revisão M2);
# - **decide sozinho só quando a cultura não tem ZARC no município** (> 40 = "só aptidão");
# - a única camada de "o que cabe" fora do NE.

# %%
import rasterio
from rasterio.enums import Resampling

sel = pd.read_csv(DADOS / "gaez" / "selecao.csv")
sel = sel[(sel.servico == "res05") & sel.variavel.str.startswith("Suitability index") & sel.variavel.str.contains("all land")]
print(f"{len(sel)} camadas de aptidão (culturas × insumo), {sel.cultura_pt.nunique()} culturas:", ", ".join(sorted(sel.cultura_pt.unique())))
print("classes do motor (limite inferior exclusivo):", GZ.CLASSES, "| corte apta: >", GZ.APTA)
# cobertura global: milho, insumo baixo, lido em resolução reduzida (1/4)
with rasterio.open(DADOS / "gaez" / sel[(sel.cultura_pt == "milho") & (sel.input_level == "Low")].arquivo.iloc[0]) as src:
    g = src.read(1, out_shape=(src.height // 4, src.width // 4), resampling=Resampling.nearest).astype(float)
    print("grade original:", src.width, "×", src.height, "| resolução", round(src.res[0] * 60, 2), "arc-min | nodata", src.nodata)
terra = g >= 0
print(f"Cobertura: {terra.mean():.1%} das células com valor (terra); entre elas, {(g[terra] > GZ.APTA * 100).mean():.1%} com milho apto "
      f"(> {GZ.APTA}) no insumo baixo; {(g[terra] == 0).mean():.1%} com aptidão zero")
fig, ax = plt.subplots(figsize=(13, 5.5))
im = ax.imshow(np.where(terra, g / 100, np.nan), extent=[-180, 180, -90, 90], cmap=SEQ, vmin=0, vmax=100)
plt.colorbar(im, ax=ax, label="aptidão (0–100)", shrink=0.75)
ax.set_ylim(-58, 75)
ax.set_title("GAEZ v4: aptidão do milho em sequeiro, insumo baixo (clima 1981–2010)")
ax.grid(False)
plt.show()

# %%
si = GZ.aptidao(list(zip(RP.x, RP.y)))  # a mesma função (e o mesmo arredondamento) do motor e da tábua do NE
GB = pd.DataFrame({c: v for (c, i), v in si.items() if i == "Low"}, index=MUN.cod.values).astype(float)
GA = pd.DataFrame({c: v for (c, i), v in si.items() if i == "High"}, index=MUN.cod.values).astype(float)
ordem = GB.median().sort_values(ascending=False).index
# conferência: é o mesmo valor que está na tábua que o motor consulta?
GZT0 = pd.read_csv(DADOS / "gaez_zarc" / "nordeste_2026-2027.csv", dtype={"geocodigo": str})
conf = GZT0.dropna(subset=["SI baixo"]).drop_duplicates(["geocodigo", "GAEZ"])
igual = np.isclose(conf["SI baixo"].values, [GB.at[c, g_] for c, g_ in zip(conf.geocodigo, conf.GAEZ)])
print(f"Conferência com gaez_zarc/nordeste_2026-2027.csv: {igual.sum()} de {len(igual)} pares município × cultura iguais")
print(f"Aptidão no insumo baixo nos {len(GB)} municípios do NE (ponto interno de cada município):")
display(descreve(GB[ordem]))
CLS = ["não apta", "muito marginal", "marginal", "moderada", "média", "boa", "alta", "muito alta"]
classes = GB[ordem].stack().map(GZ.classe_gaez)
print("Municípios por classe oficial da v4 (insumo baixo):")
display(pd.crosstab(classes.index.get_level_values(1), classes).reindex(index=ordem, columns=CLS, fill_value=0))

# %%
apta_uf = (GB[ordem] > GZ.APTA).groupby(MUN.uf.values).mean().reindex(UF_ORDEM).T * 100
fig, ax = plt.subplots(figsize=(10, 6.5))
im = ax.imshow(apta_uf.values, cmap=SEQ, vmin=0, vmax=100, aspect="auto")
ax.set_xticks(range(len(UF_ORDEM)))
ax.set_xticklabels(UF_ORDEM)
ax.set_yticks(range(len(ordem)))
ax.set_yticklabels(ordem, fontsize=8)
for i in range(apta_uf.shape[0]):
    for j in range(apta_uf.shape[1]):
        v = apta_uf.values[i, j]
        ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7, color="#fcfcfb" if v > 60 else "#0b0b0b")
ax.grid(False)
plt.colorbar(im, ax=ax, label="% dos municípios com aptidão > 40", shrink=0.8)
ax.set_title("GAEZ v4, insumo baixo: % dos municípios aptos (> 40), por cultura e UF")
plt.show()
print("Mediana da aptidão (insumo baixo) por UF, culturas do cardápio:")
cardapio_g = ["feijão-caupi", "milho", "feijão (Phaseolus)", "mandioca", "amendoim", "sorgo", "guandu", "milheto", "algodão", "girassol"]
display(GB[cardapio_g].groupby(MUN.uf.values).median().reindex(UF_ORDEM).round(1))

# %%
fig, axs = plt.subplots(1, 4, figsize=(20, 6.2))
for ax, c in zip(axs, ["feijão-caupi", "milho", "mandioca", "sorgo"]):
    mapa_ne(ax, GB[c], f"{c} (insumo baixo)", vmin=0, vmax=80, rotulo="aptidão")
plt.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(1, 2, figsize=(16, 5.5))
ganho = (GA[ordem] - GB[ordem]).median().sort_values()
axs[0].barh(ganho.index, ganho.values, color=CAT[0], height=0.6)
axs[0].axvline(0, color="#52514e", lw=0.8)
axs[0].set_xlabel("insumo alto − insumo baixo (mediana dos municípios, pontos de aptidão)")
axs[0].set_title("Quanto o insumo alto muda a aptidão no NE")
print("Insumo alto − insumo baixo (mediana dos municípios):", "; ".join(f"{k} {v:+.1f}" for k, v in ganho.items()))
cor = GB[ordem].corr("spearman")
im = axs[1].imshow(cor.values, cmap=DIV, vmin=-1, vmax=1)
axs[1].set_xticks(range(len(ordem)))
axs[1].set_xticklabels(ordem, rotation=60, ha="right", fontsize=8)
axs[1].set_yticks(range(len(ordem)))
axs[1].set_yticklabels(ordem, fontsize=8)
axs[1].grid(False)
plt.colorbar(im, ax=axs[1], label="Spearman entre municípios", shrink=0.8)
axs[1].set_title("As culturas variam juntas no espaço? (insumo baixo)")
plt.tight_layout()
plt.show()
pares_cor = cor.where(np.triu(np.ones(cor.shape, bool), 1)).stack()
print(f"Spearman entre pares de culturas: mediana {pares_cor.median():+.2f}; faixa {pares_cor.min():+.2f} a {pares_cor.max():+.2f}")
baixos = MUN.set_index("cod").loc[GB.index[(GB[["milho", "feijão-caupi", "sorgo"]] <= GZ.APTA).all(1)]]
print(f"Municípios onde milho, caupi e sorgo ficam todos ≤ {GZ.APTA} no insumo baixo: {len(baixos)} de {len(GB)}")
display(baixos.uf.value_counts().reindex(UF_ORDEM, fill_value=0).rename("municípios").to_frame().T)

# %% [markdown]
# **Leitura:**
# - **Cobertura global confirmada:** 24,4% das células da grade têm valor (a terra do planeta). Entre elas, o milho com
#   pouco insumo é apto (> 40) em 12,7% e tem aptidão zero em 60,0%. A camada responde "o que cabe" em qualquer lugar.
# - **A amostra é a mesma do motor:** os 19.734 pares município × cultura batem com a tábua `nordeste_2026-2027.csv`.
# - **No NE, com pouco insumo, a mais apta é a mandioca** (mediana de 48,8). Depois vêm guandu (37,5) e sorgo (36,2).
#   Feijão comum, caupi e milho ficam perto de 33; amendoim e algodão, perto de 30. O girassol tem aptidão zero em 743
#   municípios.
# - **Pelas classes oficiais da v4, a classe mais comum é "moderada" (> 25 a 40)** em 11 das 15 culturas. Passam do corte
#   (> 40): mandioca em 1.203 municípios, guandu em 833, sorgo em 812, feijão comum em 665, caupi em 575, milho em 547 e
#   milheto em 535.
# - **A UF muda tudo.**
#   - CE, RN e PB têm as maiores medianas de sorgo (49,8 a 53,7), milho (38,4 a 48,5) e feijão comum (44,8 a 48,6).
#   - O MA tem as menores: milho 25,0, sorgo 16,7 e girassol 0.
#   - A mandioca é a mais apta em 6 das 9 UFs; no CE, no RN e na PB, é o sorgo.
# - **Em 953 municípios (53%), milho, caupi e sorgo ficam todos ≤ 40:** os 217 do MA, 188 da BA, 179 do PI, 107 de PE e
#   86 de AL. No CE são 56.
# - **As culturas sobem e descem juntas no espaço** (Spearman mediano de +0,43 entre pares; de −0,48 a +0,94). Quem
#   manda é o solo e o relevo da célula, não a cultura.
# - **O insumo alto muda pouco a maioria** (milho +6,2; sorgo +6,4; caupi +13,0), mas muda o **girassol (+22,9)** e o
#   **algodão (+14,8)**. A cana (−17,9), a banana (−10,0) e a mandioca (−2,6) pioram. O protótipo mostra o insumo alto só
#   como rótulo (revisão M2).
# - **No produto:** o GAEZ responde "o que cabe" no mundo, mas é grosseiro no município. No NE, ele só decide onde a
#   cultura não tem ZARC (seção 3).
