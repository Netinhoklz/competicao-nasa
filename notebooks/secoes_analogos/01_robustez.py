# %% [markdown]
# ## 1. A ordem dos análogos é robusta?
# Três testes, para o Sertão Central (Quixadá):
# - **(a) Tirar uma variável de cada vez:** a ordem muda?
# - **(b) Distância de Mahalanobis:** desconta a correlação entre as variáveis (chuva e aridez andam juntas).
# - **(c) 2.000 sorteios de pesos aleatórios** (Dirichlet): com que frequência cada lugar aparece entre os 3 mais parecidos?

# %%
alvo = "CE: Quixadá (Sertão Central)"
za = z(A[A.ponto == alvo]).iloc[0]
zs = z(SIT)
base = pd.Series(dist(za, zs), index=SIT.ponto).sort_values()
linhas = {"todas": base.rank()}
for v in VARS:
    w = [0 if x == v else 1 for x in VARS]
    linhas[f"sem {ROT[v]}"] = pd.Series(dist(za, zs, w), index=SIT.ponto).rank()
# Mahalanobis
X = A[VARS].values
cov = np.cov(((X - X.mean(0)) / X.std(0)).T)
icov = np.linalg.pinv(cov)
dz = zs.values - za.values[None, :]
mah = np.sqrt(np.einsum("ij,jk,ik->i", dz, icov, dz))
linhas["Mahalanobis"] = pd.Series(mah, index=SIT.ponto).rank()
R = pd.DataFrame(linhas).loc[base.index].astype(int)
fig, ax = plt.subplots(figsize=(12, 6.5))
im = ax.imshow(R.values, cmap="viridis_r", aspect="auto")
ax.set_yticks(range(len(R)))
ax.set_yticklabels(R.index, fontsize=7)
ax.set_xticks(range(R.shape[1]))
ax.set_xticklabels(R.columns, rotation=45, ha="right", fontsize=8)
for i in range(R.shape[0]):
    for j in range(R.shape[1]):
        ax.text(j, i, R.values[i, j], ha="center", va="center", fontsize=6.5, color="w" if R.values[i, j] > 10 else "k")
plt.colorbar(im, label="posição (1 = mais parecido)")
ax.set_title(f"Posição de cada lugar como análogo de {alvo.replace('CE: ', '')} sob diferentes definições de distância")
plt.tight_layout()
plt.show()

# (c) pesos aleatórios
rng = np.random.default_rng(42)
top3 = pd.Series(0, index=SIT.ponto, dtype=float)
for _ in range(2000):
    w = rng.dirichlet(np.ones(len(VARS)))
    d = pd.Series(dist(za, zs, w), index=SIT.ponto)
    top3[d.nsmallest(3).index] += 1
top3 = (top3 / 2000 * 100).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 4.5))
top3.head(10)[::-1].plot.barh(ax=ax, color="tab:green")
ax.set_xlabel("% dos 2.000 sorteios de pesos em que o lugar ficou entre os 3 mais parecidos")
ax.set_title(f"Estabilidade dos análogos de {alvo.replace('CE: ', '')}")
plt.tight_layout()
plt.show()
display(top3.head(8).round(1).to_frame("% no top-3"))
from scipy.stats import kendalltau
tau = {c: round(kendalltau(R["todas"], R[c])[0], 2) for c in R.columns if c != "todas"}
print("Concordância da ordem com a distância completa (tau de Kendall):", tau)

# %% [markdown]
# **Leitura:** um análogo só entra no motor com peso alto se ficar entre os primeiros em quase todos os cenários. Lugares
# que só aparecem bem numa definição de distância entram com cautela no recibo.
