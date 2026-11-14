# %% [markdown]
# ## 7. Diversificação: correlação entre culturas e carteiras em R$/ha
#
# **Correlação.** Para cada par de culturas e cada município com ≥ 10 anos em comum, a correlação de Spearman entre as
# receitas por ha dos dois (a preço de referência, 1998–2025). A tabela é a mediana entre os municípios. Correlação
# baixa ou negativa = uma cultura segura a outra no ano ruim.
#
# **Carteiras** (áreas iguais; receita da carteira = média das receitas por ha):
# - **S0**: ½ milho + ½ feijão (o consórcio de hoje, na convenção da proposta);
# - **1/3**: milho, feijão e mandioca, a mandioca colhida todo ano (a conta da proposta, seção M4);
# - **1/3, mandioca a cada 2 quadras**: o terço de mandioca só colhe um ano sim, outro não (ciclo de 18 meses, como no
#   plano). Por ano, rende metade;
# - **Faixas do plano** (regime permanente da seção 6.4 da proposta): a cada ano, uma faixa colhe mandioca, uma recebe
#   maniva nova (sem receita no ano) e uma tem caupi. Por ha de faixa: (mandioca + caupi + 0) ÷ 3;
# - **Plano da família**: 2/3 da área em faixas e 1/3 em baixio com milho + caupi (como a S0).
#
# Primeiro, a conferência: refazemos a conta da proposta em razão ao normal (CE, área plantada ≥ 50 ha) para ver se
# saem os mesmos 0,26 → 0,36. Depois, a mesma conta em reais.

# %%
W = M.pivot_table(index=["cod_mun", "ano"], columns="produto", values="R")
cults = [c for c in CULT if c in W.columns and W[c].notna().sum() > 500]
COR_M = pd.DataFrame(np.nan, index=cults, columns=cults)
N_M = pd.DataFrame(0, index=cults, columns=cults)
for i, a in enumerate(cults):
    COR_M.loc[a, a] = 1
    for b in cults[i + 1:]:
        sub = W[[a, b]].dropna()
        rh = sub.groupby(level=0).apply(lambda d: d[a].corr(d[b], method="spearman") if len(d) >= 10 else np.nan).dropna()
        if len(rh) >= 20:
            COR_M.loc[a, b] = COR_M.loc[b, a] = rh.median()
            N_M.loc[a, b] = N_M.loc[b, a] = len(rh)
fig, ax = plt.subplots(figsize=(7.5, 6))
im = ax.imshow(COR_M.to_numpy(dtype=float), cmap=DIV.reversed(), vmin=-1, vmax=1)
for i in range(len(cults)):
    for j in range(len(cults)):
        v = COR_M.iloc[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:+.2f}".replace(".", ","), ha="center", va="center", fontsize=8, color="#0b0b0b")
ax.set_xticks(range(len(cults)), cults, rotation=40, ha="right")
ax.set_yticks(range(len(cults)), cults)
ax.grid(False)
plt.colorbar(im, ax=ax, shrink=0.7, label="ρ de Spearman (mediana dos municípios)")
ax.set_title("Correlação das receitas por ha no mesmo município (1998–2025)", fontsize=10)
plt.tight_layout()
plt.show()
print("Correlação (mediana dos municípios) e número de municípios por par:")
display(COR_M.round(2))
display(N_M)

# %%
# conferência com a proposta (definição canônica b: CE, produção ÷ área plantada ≥ 50 ha, razão à mediana dos outros anos)
Q = P[(P.uf == "CE") & (P.area_plantada_ha >= 50) & P.produto.isin(["Milho", "Feijão", "Mandioca"])].copy()
Q["razao"] = Q.rend_plantado_kg_ha / Q.groupby(["cod_mun", "produto"]).rend_plantado_kg_ha.transform(mediana_outros)
YQ = Q.pivot_table(index=["cod_mun", "ano"], columns="produto", values="razao").dropna()


def metr(s):
    s = s.dropna()
    return pd.Series({"CVaR10 (razão)": s[s <= s.quantile(0.1)].mean(), "P(< 0,5) %": (s < 0.5).mean() * 100, "n": len(s)})


conf_c = pd.DataFrame({"100% milho": metr(YQ.Milho), "S0: milho + feijão": metr(YQ[["Milho", "Feijão"]].mean(axis=1)),
                       "1/3 com mandioca": metr(YQ.mean(axis=1))}).T
print("Conferência (CE, 1998–2025). Proposta: 0,15 / 0,26 / 0,36 e 21% / 15% / 11% (2.495 município-anos)")
conf_c["n"] = conf_c.n.astype(int)
display(conf_c.round(3))

# %%
# carteiras em R$ nos municípios com as três culturas (seção 6), anos em que as três existem
T3 = W.loc[W.index.get_level_values(0).isin(TRES), ["Milho", "Feijão", "Mandioca"]].dropna()
CART = pd.DataFrame({
    "100% milho": T3.Milho, "100% feijão": T3.Feijão, "100% mandioca": T3.Mandioca,
    "S0: ½ milho + ½ feijão": (T3.Milho + T3.Feijão) / 2,
    "1/3 (mandioca todo ano)": T3.mean(axis=1),
    "1/3 (mandioca a cada 2 quadras)": (T3.Milho + T3.Feijão + T3.Mandioca / 2) / 3,
    "Faixas do plano": (T3.Mandioca + T3.Feijão) / 3,
    "Plano da família (2/3 faixas + 1/3 baixio)": 2 / 3 * (T3.Mandioca + T3.Feijão) / 3 + 1 / 3 * (T3.Milho + T3.Feijão) / 2,
})
K = CUSTO.desembolso
K_CART = {"100% milho": K.Milho, "100% feijão": K.Feijão, "100% mandioca": K.Mandioca, "S0: ½ milho + ½ feijão": (K.Milho + K.Feijão) / 2,
          "1/3 (mandioca todo ano)": (K.Milho + K.Feijão + K.Mandioca) / 3, "1/3 (mandioca a cada 2 quadras)": (K.Milho + K.Feijão + K.Mandioca / 2) / 3,
          "Faixas do plano": (K.Mandioca + K.Feijão) / 3, "Plano da família (2/3 faixas + 1/3 baixio)": 2 / 3 * (K.Mandioca + K.Feijão) / 3 + 1 / 3 * (K.Milho + K.Feijão) / 2}
KS = CUSTO.semente
KS_CART = {k: v for k, v in zip(K_CART, [KS.Milho, KS.Feijão, KS.Mandioca, (KS.Milho + KS.Feijão) / 2, (KS.Milho + KS.Feijão + KS.Mandioca) / 3,
                                         (KS.Milho + KS.Feijão + KS.Mandioca / 2) / 3, (KS.Mandioca + KS.Feijão) / 3,
                                         2 / 3 * (KS.Mandioca + KS.Feijão) / 3 + 1 / 3 * (KS.Milho + KS.Feijão) / 2])}


def resumo_cart(X, kc=K_CART, ks=KS_CART):
    out = {}
    en = X.index.get_level_values(1).isin(EN_FORTE)
    for c in X.columns:
        s = X[c]
        rel = s / s.groupby(level=0).transform(mediana_outros)
        por_mun = s.groupby(level=0).agg(["mean", cvar10])
        out[c] = {"receita média (R$/ha)": por_mun["mean"].median(), "CVaR10 (R$/ha)": por_mun["cvar10"].median(),
                  "CVaR10 (razão)": rel[rel <= rel.quantile(0.1)].mean(), "P(< 0,5 do normal) %": (rel < 0.5).mean() * 100,
                  "razão mediana, El Niño forte": rel[en].median(), "não paga a semente %": (s < ks[c]).mean() * 100,
                  "não paga o desembolso %": (s < kc[c]).mean() * 100,
                  "não paga o desembolso %, El Niño forte": (s[en] < kc[c]).mean() * 100}
    return pd.DataFrame(out).T


RC = resumo_cart(CART)
print(f"Carteiras em R$ de 2025 (preço de referência), {T3.index.get_level_values(0).nunique()} municípios, {len(T3)} município-anos")
display(RC.round(2))

# %% [markdown]
# **Placebo e piso, em reais.** O placebo da proposta troca o terço de mandioca pelo **feijão de um dos 5 municípios
# vizinhos mais próximos**, no mesmo ano: é só "mais uma série com ruído independente". Se o placebo já dá quase o mesmo
# ganho, a parte própria da mandioca é pequena. O piso conta como perda total (receita 0) os anos em que a mandioca
# sumiu do município (menos de 10 ha), justo os anos secos em que a maniva falta.

# %%
pts = MUN_NE.set_index("cod").geometry.representative_point()
xy = np.c_[pts.x, pts.y]
cods = pts.index.to_numpy()
d2 = ((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1)
np.fill_diagonal(d2, np.inf)
VIZ = {c: cods[np.argsort(d2[i])[:5]] for i, c in enumerate(cods)}
Wf = W["Feijão"].dropna()
Wfr = (Wf / Wf.groupby(level=0).transform(mediana_outros))
rng = np.random.default_rng(14)


def placebo(T, base, sorteios=50):
    """CVaR10 da carteira 1/3 com o feijão de um vizinho (sorteado entre os 5 mais próximos, mesmo ano) no lugar da mandioca."""
    fv = base.to_dict()
    opcoes = [[o for o in (fv.get((v, a)) for v in VIZ.get(c, [])) if o is not None and not np.isnan(o)] for (c, a) in T.index]
    tem = np.array([len(o) > 0 for o in opcoes])
    resto = T.drop(columns="Mandioca").to_numpy()[tem]
    opcoes = [o for o in opcoes if o]
    res = []
    for _ in range(sorteios):
        viz = np.array([o[rng.integers(len(o))] for o in opcoes])
        s = np.c_[resto, viz].mean(axis=1)
        s = s[~np.isnan(s)]
        res.append(s[s <= np.quantile(s, 0.1)].mean())
    return np.mean(res), np.quantile(res, 0.05), np.quantile(res, 0.95)


TR = T3 / T3.groupby(level=0).transform(mediana_outros)
pl_r = placebo(TR, Wfr)
s13 = TR.mean(axis=1)
s0 = TR[["Milho", "Feijão"]].mean(axis=1)
print(f"Razão ao normal (NE, {len(TR)} município-anos): S0 {num(s0[s0 <= s0.quantile(.1)].mean(), 3)} | 1/3 {num(s13[s13 <= s13.quantile(.1)].mean(), 3)} | "
      f"placebo do vizinho {num(pl_r[0], 3)} (90% dos sorteios: {num(pl_r[1], 3)}–{num(pl_r[2], 3)})")
YR = YQ.copy()
Qf = Q[Q.produto == "Feijão"].set_index(["cod_mun", "ano"]).razao
pl_ce = placebo(YR, Qf)
print(f"Conferência no CE (proposta: placebo 0,335, faixa 0,323–0,347): {num(pl_ce[0], 3)} ({num(pl_ce[1], 3)}–{num(pl_ce[2], 3)})")

# piso: anos sem mandioca contam como perda total
Wall = W.loc[W.index.get_level_values(0).isin(TRES), ["Milho", "Feijão", "Mandioca"]].dropna(subset=["Milho", "Feijão"])
falta = Wall.Mandioca.isna()
def razao_piso(s):
    """Razão ao normal; o normal é a mediana dos outros anos COM mandioca; ano sem mandioca = 0."""
    v = s.to_numpy()
    tem = ~np.isnan(v)
    out = []
    for i in range(len(v)):
        outros = v[tem & (np.arange(len(v)) != i)]
        out.append(0.0 if not tem[i] else (v[i] / np.median(outros) if len(outros) else np.nan))
    return pd.Series(out, index=s.index)


rel_p = pd.DataFrame({"Milho": Wall.Milho / Wall.Milho.groupby(level=0).transform(mediana_outros),
                      "Feijão": Wall.Feijão / Wall.Feijão.groupby(level=0).transform(mediana_outros),
                      "Mandioca": Wall.Mandioca.groupby(level=0).transform(razao_piso)})
s_piso = rel_p.mean(axis=1)
print(f"Piso: {num(falta.mean() * 100, 1)}% dos município-anos sem mandioca; CVaR10 (razão) da 1/3 contando esses anos como zero = "
      f"{num(s_piso[s_piso <= s_piso.quantile(.1)].mean(), 3)}")
pl_rs = placebo(T3, Wf)
s13r = T3.mean(axis=1)
s0r = ((T3.Milho + T3.Feijão) / 2)
print(f"Em R$ por ha (CVaR10 agrupado dos município-anos): S0 {brl(s0r[s0r <= s0r.quantile(.1)].mean())} | 1/3 {brl(s13r[s13r <= s13r.quantile(.1)].mean())} | "
      f"placebo {brl(pl_rs[0])} ({brl(pl_rs[1])}–{brl(pl_rs[2])})")

# %%
fig, ax = plt.subplots(figsize=(10, 5.5))
for c in ["Milho", "Feijão", "Mandioca"]:
    r = RC.loc[f"100% {c.lower()}"]
    ax.scatter(r["receita média (R$/ha)"], r["CVaR10 (R$/ha)"], s=80, color=COR[c], edgecolor="#fcfcfb", lw=2, zorder=3)
    ax.annotate(f"100% {c.lower()}", (r["receita média (R$/ha)"], r["CVaR10 (R$/ha)"]), xytext=(6, 4), textcoords="offset points", fontsize=8, color="#52514e")
for k, mk in zip([c for c in RC.index if not c.startswith("100%")], ["s", "D", "^", "P", "X"]):
    r = RC.loc[k]
    ax.scatter(r["receita média (R$/ha)"], r["CVaR10 (R$/ha)"], s=70, marker=mk, color="#52514e", edgecolor="#fcfcfb", lw=1.5, zorder=3)
    ax.annotate(k, (r["receita média (R$/ha)"], r["CVaR10 (R$/ha)"]), xytext=(6, -10), textcoords="offset points", fontsize=8, color="#52514e")
ax.set_xscale("log")
ax.set_xlabel("receita média (R$ de 2025/ha por ano, log)")
ax.set_ylabel("CVaR10: média dos piores anos (R$/ha)")
ax.set_title(f"Fronteira média × pior decil: culturas e carteiras nos {len(TRES)} municípios com milho, feijão e mandioca", fontsize=10)
plt.tight_layout()
plt.show()

# %%
# a mesma comparação com a receita observada (preço do ano), 2010–2025
Wo = M[M.ano.between(2010, 2025)].pivot_table(index=["cod_mun", "ano"], columns="produto", values="R_obs")
T3o = Wo.loc[Wo.index.get_level_values(0).isin(TRES), ["Milho", "Feijão", "Mandioca"]].dropna()
CO = pd.DataFrame({"S0: ½ milho + ½ feijão": (T3o.Milho + T3o.Feijão) / 2, "1/3 (mandioca todo ano)": T3o.mean(axis=1),
                   "Faixas do plano": (T3o.Mandioca + T3o.Feijão) / 3})
print(f"Receita observada (com o preço do ano), 2010–2025, {len(T3o)} município-anos")
display(resumo_cart(CO).round(2))

# %% [markdown]
# **Leitura.**
# - **Correlação mediana no mesmo município:** milho × feijão **+0,70** (quebram juntos); milho × mandioca e feijão ×
#   mandioca +0,31; mandioca × amendoim +0,01. Todas são positivas: nenhuma cultura do PAM é seguro natural de outra, mas
#   a mandioca e o amendoim são as menos ligadas ao roçado.
# - **Conferência:** a conta da proposta sai igual: pior ano em 10 de **0,15 / 0,26 / 0,36** e P(< 0,5) de 21% / 15% /
#   11%, nos mesmos 2.495 município-anos do CE.
# - **Placebo:** no CE, o feijão do vizinho no lugar da mandioca dá 0,325 (0,318–0,331), perto dos 0,335 da proposta; a
#   parte própria da mandioca fica em ~+0,035. No NE (34.895 município-anos): S0 0,165, carteira 1/3 0,321, placebo
#   0,229; parte própria ~+0,09. **Piso** (ano sem mandioca = perda total; 6,8% dos município-anos): 0,260, ainda acima
#   da S0.
# - **Em reais, o ganho é de nível, não só de diversificação.** A carteira 1/3 rende R$ 3.307/ha por ano, contra R$ 1.159
#   da S0, e o pior decil sobe de R$ 351 para R$ 1.584/ha. No pior decil agrupado, a S0 fica em R$ 127/ha; a carteira
#   com o feijão do vizinho no lugar da mandioca, em R$ 198; com a mandioca, em R$ 956. Quase todo o ganho vem da
#   receita alta da mandioca (R$ 7.241/ha).
# - **Ciclo:** se o terço de mandioca só colhe a cada 2 quadras, a carteira rende R$ 2.030/ha e o pior decil cai para
#   R$ 964/ha; ainda 2,7 vezes a S0.
# - **Faixas do plano:** R$ 2.962/ha por ano, pior decil R$ 1.431. **Plano da família** (com o baixio): R$ 2.405 e
#   R$ 1.155. Chance de não pagar o desembolso: 39% dos município-anos, contra 68% da S0; em El Niño forte, 48% contra 75%.
# - **Com o preço do ano** (2010–2025), a vantagem continua: pior ano em 10 de 0,16 (S0) para 0,32 (1/3); chance de não
#   pagar o desembolso de 70% para 47%.
