# %% [markdown]
# ## 3. O sertão no mundo: onde o clima se parece com o do Sertão Central?
# Assinatura climática do NASA POWER numa grade global de 6° (pontos de terra) e a distância até Quixadá. Mostra:
# - **onde mais o produto se aplica do mesmo jeito** (mercado global da ferramenta);
# - **onde procurar mais literatura de rotação** que se transfira para o sertão.

# %%
G = pd.read_csv(D_APR / "global_assinaturas.csv")
zg = (G[VARS] - MU) / SD
G["dist_sertao"] = dist(za, zg)
G["similaridade"] = np.exp(-G.dist_sertao ** 2 / 2)
print(f"{len(G)} pontos de terra; {int((G.dist_sertao < 1.0).sum())} com distância < 1 do Sertão Central")
fig, ax = plt.subplots(figsize=(15, 7))
paises_gdf().boundary.plot(ax=ax, color="lightgray", lw=0.4)
sc = ax.scatter(G.lon, G.lat, c=G.similaridade, cmap="YlOrBr", s=60, marker="s", vmin=0, vmax=1, edgecolors="none")
plt.colorbar(sc, ax=ax, label="semelhança com o clima do Sertão Central (exp(−d²/2))", shrink=0.7)
for _, s in SIT.iterrows():
    ax.scatter(s.lon, s.lat, marker="*", s=90, c="tab:blue", edgecolors="k", lw=0.4)
q = A[A.ponto == alvo].iloc[0]
ax.scatter(q.lon, q.lat, marker="*", s=250, c="red", edgecolors="k")
ax.set_xlim(-180, 180)
ax.set_ylim(-55, 70)
ax.set_title("Onde no mundo o clima se parece com o do sertão (★ azul = lugares dos artigos; ★ vermelho = Quixadá)")
plt.show()
top = G.nsmallest(20, "dist_sertao")[["lat", "lon", "chuva_anual_mm", "aridez_P_ET0", "meses_umidos", "sazonalidade_walsh", "dist_sertao"]]
display(top.round(2))

# %% [markdown]
# **Leitura:**
# - **Só 2 dos 387 pontos de terra têm distância < 1 do Sertão Central, e 19 têm distância < 1,5.** O clima do sertão
#   é raro no planeta. Os mais parecidos são:
#   - o próprio Ceará (−6, −39; d 0,22);
#   - o **Chaco argentino** (−24, −63; d 0,77), o único outro ponto com d < 1;
#   - o **Oeste da Bahia** (−12, −45; 1,01) e o **norte da Austrália** (−18, 129; 1,01);
#   - **Burkina Faso** (12, −3; 1,04) e o **sudoeste de Madagascar** (−24, 45; 1,05);
#   - o **Deccan na Índia** (18, 75; 1,15).
#   - Logo depois vêm o norte do Benim, o Zimbábue, o Chaco argentino mais ao sul (−30, −63), o México, o Sudão do Sul,
#     a Namíbia, Moçambique, o norte da Nigéria, o Pantanal (−18, −57) e Angola. O norte de Minas (−18, −45) fica logo
#     acima, com d 1,59.
#   - **É nessas savanas tropicais de estação chuvosa curta que vale procurar experimentos de rotação** para o catálogo.
# - **Ressalva:** o **norte da China** (36–42°N) tem chuva de monção concentrada no verão, que imita a sazonalidade do
#   sertão. Com a Tmax média (e não o recorde do mês), ele fica fora dos 20 mais parecidos: todos os 20 estão entre 30°S
#   e 24°N. **Próxima melhoria:** incluir a Tmin do mês mais frio (geada), para separar de vez as monções temperadas das
#   tropicais.
# - **Para a ferramenta,** essas regiões são onde a QUADRA funciona com a mesma lógica (portões, análogos e IMERG + SMAP)
#   sem nenhuma mudança: uma prova concreta do "produto global".
# - Grade de 6°: o mapa é indicativo. Para cada usuário, o produto calcula a assinatura do próprio talhão.
