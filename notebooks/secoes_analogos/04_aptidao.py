# %% [markdown]
# ## 4. As mesmas culturas cabem nos análogos? (FAO GAEZ v4)
# Índice de aptidão (0–100, sequeiro, insumo baixo e alto) de 15 culturas, amostrado em cada lugar de artigo e nos 12
# pontos do Ceará. **Se o análogo climático também tem o mesmo perfil de aptidão, a transferência da evidência fica mais
# segura.**

# %%
GZ = pd.read_csv(D_APR / "gaez_sitios.csv")
baixo = GZ[GZ.insumo == "Low"].pivot_table(index="ponto", columns="cultura", values="SI")
ordem = [p for p in list(CE12.ponto) + list(base.index) if p in baixo.index]
H = baixo.loc[ordem]
fig, ax = plt.subplots(figsize=(14, 9))
im = ax.imshow(H.values, cmap="YlGn", aspect="auto", vmin=0, vmax=80)
ax.set_xticks(range(H.shape[1]))
ax.set_xticklabels(H.columns, rotation=55, ha="right", fontsize=8)
ax.set_yticks(range(H.shape[0]))
ax.set_yticklabels([p.replace("CE: ", "CE · ") for p in H.index], fontsize=7)
ax.axhline(len(CE12) - 0.5, color="r", lw=1.5)
plt.colorbar(im, label="índice de aptidão GAEZ (sequeiro, insumo baixo)")
ax.set_title("Aptidão das culturas: Ceará (acima da linha) × lugares dos artigos (ordenados pela semelhança com o Sertão Central)")
plt.tight_layout()
plt.show()

# correlação do perfil de aptidão entre Quixadá e cada lugar de artigo, contra a distância climática
q_perfil = H.loc[alvo]
corr = H.loc[[p for p in base.index if p in H.index]].apply(lambda r: r.corr(q_perfil), axis=1)
C = pd.DataFrame({"distância climática": base.reindex(corr.index), "correlação do perfil de aptidão": corr.round(2)})
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(C["distância climática"], C["correlação do perfil de aptidão"])
for p, r in C.iterrows():
    ax.annotate(p.split(" (")[0], (r["distância climática"], r["correlação do perfil de aptidão"]), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
ax.set_xlabel("distância climática ao Sertão Central (POWER)")
ax.set_ylabel("correlação do perfil de aptidão com Quixadá (GAEZ)")
ax.set_title("Clima parecido → culturas parecidas?")
plt.show()
display(C.sort_values("distância climática"))
print("Correlação de Spearman entre distância climática e semelhança de aptidão:",
      round(C.corr("spearman").iloc[0, 1], 2))

# %% [markdown]
# **Leitura:**
# - **O clima é um bom guia:** quanto mais longe no clima, menos parecido o perfil de culturas (Spearman −0,76).
#   - Os análogos do Nordeste têm o perfil de aptidão quase igual ao de Quixadá: Sobral 0,98, Cerrado piauiense 0,82,
#     Serra Talhada 0,79.
#   - Os 5 lugares mais parecidos no clima (d de 0,32 a 1,67) têm todos perfil parecido (de 0,79 a 0,98). Entre eles
#     estão o semiárido da Índia (d 0,75; 0,80) e a Savana da Guiné (d 1,67; 0,93).
#   - Iowa, França, Ontário e o NE da China têm perfis diferentes (correlação ≤ 0,03).
# - **Harare deixou de ser a exceção:** agora ele está longe no clima (d 2,15, 10º lugar) e não conta como análogo. O
#   perfil de culturas continua diferente (correlação −0,08), provavelmente pela altitude, que deixa o lugar mais fresco.
#   - Os desvios ficam a meia distância: a Planície do Norte da China (d 2,12; 0,03) e Harare têm perfil diferente;
#     Niamey (d 2,09; 0,80) e Petrolina (d 2,51; 0,83) têm perfil parecido.
#   - **Transferir de lugares assim exige checar cultura a cultura.**
# - A tabela mostra, cultura a cultura, onde a aptidão do análogo difere da do sertão. **A evidência de uma cultura só
#   se transfere se ela também cabe nos dois lugares.**
