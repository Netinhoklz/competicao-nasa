# %% [markdown]
# ## 2. Mapa de análogos no Ceará: qual literatura vale em cada município?
# Para cada um dos 184 municípios, calculamos a assinatura climática do NASA POWER (pelo ponto interno do município) e o
# lugar de artigo mais parecido. A **confiança da transferência** é o peso w = exp(−d²/2) do melhor análogo: perto de 1,
# o estudo foi feito num clima muito parecido; perto de 0, não há estudo parecido.

# %%
M = pd.read_csv(D_APR / "ceara_mun_assinaturas.csv", dtype={"cod": str})
zm = z(M)
dm = np.array([dist(zm.iloc[i], zs) for i in range(len(M))])
M["melhor_analogo"] = SIT.ponto.values[dm.argmin(1)]
M["grupo_analogo"] = SIT.grupo.values[dm.argmin(1)]
M["dist_melhor"] = dm.min(1)
M["confianca"] = np.exp(-M.dist_melhor ** 2 / 2)
# melhor análogo FORA do Nordeste (para ver de que literatura global cada região puxa)
fora = ~SIT.grupo.str.startswith("Nordeste")
M["melhor_global"] = SIT.ponto.values[fora][dm[:, fora.values].argmin(1)]
M["dist_global"] = dm[:, fora.values].min(1)
geo = municipios_ce_gdf().assign(cod=lambda g: g.codarea.astype(str)).merge(M, on="cod")
fig, axs = plt.subplots(1, 3, figsize=(19, 6.5))
geo.plot(column="melhor_analogo", ax=axs[0], legend=True, categorical=True, cmap="tab10",
         legend_kwds={"fontsize": 6.5, "loc": "lower left", "bbox_to_anchor": (0, -0.55)})
axs[0].set_title("Estudo de clima mais parecido (qualquer região)")
geo.plot(column="confianca", ax=axs[1], cmap="YlGn", vmin=0, vmax=1, legend=True, legend_kwds={"label": "confiança da transferência w"})
axs[1].set_title("Confiança da transferência")
geo.plot(column="melhor_global", ax=axs[2], legend=True, categorical=True, cmap="Set2",
         legend_kwds={"fontsize": 6.5, "loc": "lower left", "bbox_to_anchor": (0, -0.45)})
axs[2].set_title("Análogo mais parecido FORA do Nordeste")
for a in axs:
    ceara_gdf().boundary.plot(ax=a, color="k", lw=0.8)
    a.set_axis_off()
plt.tight_layout()
plt.show()
resumo = M.groupby("mesorregiao").agg(municipios=("cod", "count"), confianca_media=("confianca", "mean"),
                                       analogo_mais_comum=("melhor_analogo", lambda s: s.value_counts().index[0]),
                                       global_mais_comum=("melhor_global", lambda s: s.value_counts().index[0]),
                                       dist_global_media=("dist_global", "mean")).round(2)
display(resumo)
print("Distribuição do melhor análogo (nº de municípios):")
display(M.melhor_analogo.value_counts().to_frame("municípios"))

# %% [markdown]
# **Leitura:**
# - **As regiões do Ceará não puxam a mesma literatura.**
#   - O **Cerrado piauiense** é o melhor análogo em 102 municípios (Centro-Sul, Jaguaribe, Sertões e Sul).
#   - **Sobral**, em 40 (Noroeste e Norte).
#   - A **Savana da Guiné (Tamale)**, em 13 (Região Metropolitana de Fortaleza).
#   - A **África Austral (Harare)** fica só com 11.
#   - Fora do Nordeste, o análogo mais comum é o **semiárido da Índia (Patancheru)** em 5 das 7 mesorregiões. Na
#     Metropolitana e no Norte, é a Savana da Guiné.
# - **A confiança é alta em todas as mesorregiões** (w médio de 0,73 no Norte a 0,90 no Centro-Sul). A Região
#   Metropolitana de Fortaleza (0,75) não é mais o ponto fraco.
# - **No produto,** o recibo de cada estratégia mostra o estudo análogo **do município do usuário**, não um número único
#   para o estado.
