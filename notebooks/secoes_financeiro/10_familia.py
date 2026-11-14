# %% [markdown]
# ## 10. A família de Quixadá: fluxo de caixa 2027–2029
#
# **A família é a da proposta (fictícia e rotulada como tal):** Dona Francisca, Quixadá-CE, 3 ha (1 ha de baixio), 8
# cabras, semente própria de milho e feijão, **sem mandioca no chão hoje**. O plano é o da seção 6.4 da proposta:
#
# | Talhão | 2027 | 2028 | 2029 |
# |---|---|---|---|
# | Faixa 1 | maniva (fev até o fim da janela ZARC da mandioca, em geral março) | mandioca = tampão (colheita) | caupi precoce |
# | Faixa 2 | caupi precoce (metade guardada até ~10/mar) | ano bom: milho depois do caupi · ano seco: sorgo forrageiro | maniva |
# | Faixa 3 | sorgo forrageiro | maniva | mandioca = tampão (colheita) |
# | Baixio (1 ha) | milho + caupi em revezamento | o mesmo | o mesmo |
# | Bordas | palma + gliricídia | ficam | ficam |
#
# **O que é medido e o que é suposição nesta conta:**
#
# | Item | Valor | Tipo |
# |---|---|---|
# | Receita por ha de milho, feijão e mandioca em Quixadá | mediana do próprio município no grupo de anos do cenário, a preço de referência (PAM 1998–2025) | medido |
# | Cenários de ano | normal = anos sem El Niño forte e fora da seca; El Niño forte = 1998, 2010, 2016, 2024; seca = 2012–2015 | medido (o grupo); a escolha do cenário é suposição |
# | Mandioca em ano de seca | Quixadá não tem mandioca ≥ 10 ha em 2012–2015: usamos a razão ao normal mediana da mesorregião (Sertão Cearense) | suposição com dado vizinho |
# | Faixas | três faixas iguais de 2/3 ha; as bordas (palma + gliricídia) não tiram área | **suposição** (a proposta deixa o tamanho para a família e o técnico) |
# | Baixio | milho + caupi = ½ receita do milho + ½ do feijão por ha (a convenção da S0) | suposição de convenção |
# | Bônus da leguminosa no milho de 2028 | 0% (honesto contra a S0), +9% e +24% (contra cereal solteiro) | literatura (D·T3 e B·T1) |
# | Custo | dois níveis da CONAB: só semente, e desembolso; a mão de obra da família não entra | CONAB (Crateús-CE no milho; mediana NE no feijão e na mandioca) |
# | Mandioca: quando conta o custo | todo no ano da maniva; a receita, no ano da colheita | suposição conservadora para o caixa |
# | Sorgo forrageiro, palma, gliricídia | sem receita em dinheiro (valor de uso para as cabras, não medido); o sorgo forrageiro tem o custo suposto de lavoura anual | suposição; qualitativo |
# | Garantia-Safra | não entra (o valor do benefício não está nas fontes lidas) | fora da conta |

# %%
REG = REFM.mesorregiao.to_dict()
meso_q = REG[QUIXADA]


def grupo_ano(a):
    return "El Niño forte" if a in EN_FORTE else ("seca" if a in SECA else "normal")


Mq = M[M.produto.isin(["Milho", "Feijão", "Mandioca"])].copy()
Mq["g"] = Mq.ano.map(grupo_ano)
REC_Q, ORIG = {}, {}
for c in ["Milho", "Feijão", "Mandioca"]:
    sq = Mq[(Mq.cod_mun == QUIXADA) & (Mq.produto == c)]
    base = sq.R.median()
    for gr in ["normal", "El Niño forte", "seca"]:
        s = sq[sq.g == gr].R
        if len(s) >= 2:
            REC_Q[(c, gr)], ORIG[(c, gr)] = s.median(), f"Quixadá, {len(s)} anos"
        else:
            viz = Mq[(Mq.produto == c) & (Mq.cod_mun.map(REG) == meso_q) & (Mq.g == gr)].R_rel.median()
            REC_Q[(c, gr)], ORIG[(c, gr)] = base * viz, f"mesorregião ({meso_q}), razão {viz:.2f}"
rq = pd.DataFrame({"R$/ha": pd.Series(REC_Q), "origem": pd.Series(ORIG)})
print("Receita por ha plantado em Quixadá, por cenário (R$ de 2025, preço de referência)")
display(rq)

A_F, A_B = 2 / 3, 1.0  # área de cada faixa e do baixio (ha) — suposição
MULT_MAND = 1.0  # preço da raiz = preço de referência de Quixadá (a seção final testa outros)
KS_, KD_ = CUSTO.semente, CUSTO.desembolso


def ano_plano(ano, cen, bonus, ano_seco_f2=False):
    """Receita e custos (semente, desembolso) do plano no ano, por talhão."""
    r = lambda c: REC_Q[(c, cen)]
    t = []
    s0b = ((r("Milho") + r("Feijão")) / 2 * A_B, (KS_.Milho + KS_.Feijão) / 2 * A_B, (KD_.Milho + KD_.Feijão) / 2 * A_B)
    if ano == 2027:
        t += [("Faixa 1: maniva", 0, KS_.Mandioca * A_F, KD_.Mandioca * A_F), ("Faixa 2: caupi", r("Feijão") * A_F, KS_.Feijão * A_F, KD_.Feijão * A_F),
              ("Faixa 3: sorgo forrageiro", 0, KS_.Sorgo * A_F, KD_.Sorgo * A_F)]
    elif ano == 2028:
        f2 = (("Faixa 2: sorgo forrageiro (ano seco)", 0, KS_.Sorgo * A_F, KD_.Sorgo * A_F) if ano_seco_f2 else
              ("Faixa 2: milho depois do caupi", r("Milho") * (1 + bonus) * A_F, KS_.Milho * A_F, KD_.Milho * A_F))
        t += [("Faixa 1: mandioca (colheita)", r("Mandioca") * MULT_MAND * A_F, 0, 0), f2, ("Faixa 3: maniva", 0, KS_.Mandioca * A_F, KD_.Mandioca * A_F)]
    else:
        t += [("Faixa 1: caupi", r("Feijão") * A_F, KS_.Feijão * A_F, KD_.Feijão * A_F), ("Faixa 2: maniva", 0, KS_.Mandioca * A_F, KD_.Mandioca * A_F),
              ("Faixa 3: mandioca (colheita)", r("Mandioca") * MULT_MAND * A_F, 0, 0)]
    t.append(("Baixio: milho + caupi", *s0b))
    return pd.DataFrame(t, columns=["talhão", "receita", "custo_semente", "custo_desembolso"])


def ano_s0(cen):
    r = lambda c: REC_Q[(c, cen)]
    return pd.DataFrame([("S0: 3 ha de milho + feijão", (r("Milho") + r("Feijão")) / 2 * 3, (KS_.Milho + KS_.Feijão) / 2 * 3,
                          (KD_.Milho + KD_.Feijão) / 2 * 3)], columns=["talhão", "receita", "custo_semente", "custo_desembolso"])


CENARIOS = {"A. três anos normais": ["normal", "normal", "normal"],
            "B. El Niño forte em 2027, depois normal": ["El Niño forte", "normal", "normal"],
            "C. El Niño forte em 2027 e seca em 2028": ["El Niño forte", "seca", "normal"]}
linhas, detalhe = [], {}
for nome, cens in CENARIOS.items():
    for bonus in [0.0, 0.24]:
        for ano, cen in zip([2027, 2028, 2029], cens):
            seco = cen == "seca" and ano == 2028
            pl = ano_plano(ano, cen, bonus, ano_seco_f2=seco)
            s0 = ano_s0(cen)
            detalhe[(nome, bonus, ano)] = pl
            for rot, d in [("Plano", pl), ("S0", s0)]:
                linhas.append({"cenário": nome, "bônus": bonus, "ano": ano, "quadra": cen, "sistema": rot, "receita": d.receita.sum(),
                               "custo semente": d.custo_semente.sum(), "custo desembolso": d.custo_desembolso.sum()})
FC = pd.DataFrame(linhas)
FC["margem sobre a semente"] = FC.receita - FC["custo semente"]
FC["margem sobre o desembolso"] = FC.receita - FC["custo desembolso"]
print("Talhões do plano no cenário B (bônus 0), ano a ano (R$ de 2025)")
for ano in [2027, 2028, 2029]:
    print(f"— {ano}")
    display(detalhe[("B. El Niño forte em 2027, depois normal", 0.0, ano)].round(0))
print("Fluxo de caixa da família, 3 ha (R$ de 2025; bônus 0 = cenário honesto contra a S0)")
display(FC[FC.bônus == 0].pivot_table(index=["cenário", "ano", "quadra"], columns="sistema",
                                      values=["receita", "margem sobre a semente", "margem sobre o desembolso"]).round(0))

# %%
TOT = FC.groupby(["cenário", "bônus", "sistema"])[["receita", "custo semente", "custo desembolso", "margem sobre a semente", "margem sobre o desembolso"]].sum()
dif = (TOT.xs("Plano", level="sistema") - TOT.xs("S0", level="sistema"))
print("Totais de 2027–2029 (R$ de 2025, 3 ha)")
display(TOT.round(0))
print("Plano − S0, em 3 anos (R$ de 2025)")
display(dif.round(0))

fig, axs = plt.subplots(1, 2, figsize=(15, 4.8))
cn = list(CENARIOS)
x = np.arange(len(cn))
for k, (rot, cor) in enumerate([("S0", "#a3a29b"), ("Plano", "#184f95")]):
    v = [TOT.loc[(c, 0.0, rot), "receita"] for c in cn]
    axs[0].bar(x + (k - 0.5) * 0.36, v, width=0.34, color=cor, label=rot + (" (3 ha de milho + feijão)" if rot == "S0" else " por faixas"))
    for xi, vi in zip(x, v):
        axs[0].text(xi + (k - 0.5) * 0.36, vi + 80, brl(vi), ha="center", fontsize=8, color="#52514e")
ROT_CEN = ["A. três anos\nnormais", "B. El Niño forte em 2027,\ndepois normal", "C. El Niño forte em 2027\ne seca em 2028"]
axs[0].set_xticks(x, ROT_CEN, fontsize=8)
axs[0].set_ylabel("receita de 2027–2029 (R$ de 2025)")
axs[0].legend(frameon=False, fontsize=8)
axs[0].set_title("Receita bruta em 3 anos, bônus 0 (cenário honesto)", fontsize=10)
d0 = [dif.loc[(c, 0.0), "margem sobre a semente"] for c in cn]
d24 = [dif.loc[(c, 0.24), "margem sobre a semente"] for c in cn]
dd = [dif.loc[(c, 0.0), "margem sobre o desembolso"] for c in cn]
todos = np.array(d0 + d24 + dd)
lim = np.abs(todos).max() * 1.2
alc = []
for k, (v, rot) in enumerate([(d0, "margem sobre a semente, bônus 0"), (d24, "margem sobre a semente, bônus +24%"), (dd, "margem sobre o desembolso, bônus 0")]):
    cores = ["#184f95" if vi >= 0 else "#d03b3b" for vi in v]
    axs[1].bar(x + (k - 1) * 0.26, v, width=0.24, color=cores, alpha=[1, 0.6, 0.35][k])
    alc.append(Patch(color="#184f95", alpha=[1, 0.6, 0.35][k], label=rot))
    for xi, vi in zip(x, v):
        axs[1].text(xi + (k - 1) * 0.26, vi + (lim * 0.02 if vi >= 0 else -lim * 0.06), brl(vi), ha="center", fontsize=7, color="#52514e")
axs[1].axhline(0, color=CINZA, lw=1)
axs[1].set_ylim(min(0, todos.min()) * 1.3 - lim * 0.05, lim)
axs[1].set_xticks(x, ROT_CEN, fontsize=8)
axs[1].set_ylabel("plano − S0, margem em 3 anos (R$)")
axs[1].legend(handles=alc, frameon=False, fontsize=8, loc="upper right")
axs[1].set_title("Quanto o plano ganha da S0 em 3 anos (azul = plano à frente; vermelho = atrás)", fontsize=10)
plt.tight_layout()
plt.show()

# %%
# composição da receita do plano por cultura, cenário B, bônus 0
comp = []
for ano in [2027, 2028, 2029]:
    d = detalhe[("B. El Niño forte em 2027, depois normal", 0.0, ano)]
    cen = CENARIOS["B. El Niño forte em 2027, depois normal"][ano - 2027]
    lin = {"ano": ano, "Milho": 0.0, "Feijão": 0.0, "Mandioca": 0.0}
    for t in d.itertuples():
        if "mandioca (colheita)" in t.talhão:
            lin["Mandioca"] += t.receita
        elif "caupi" in t.talhão and "Baixio" not in t.talhão:
            lin["Feijão"] += t.receita
        elif "milho depois" in t.talhão:
            lin["Milho"] += t.receita
        elif "Baixio" in t.talhão:
            lin["Milho"] += REC_Q[("Milho", cen)] / 2 * A_B
            lin["Feijão"] += REC_Q[("Feijão", cen)] / 2 * A_B
    comp.append(lin)
comp = pd.DataFrame(comp).set_index("ano")
fig, ax = plt.subplots(figsize=(8, 4.2))
base = np.zeros(len(comp))
for c in ["Milho", "Feijão", "Mandioca"]:
    ax.bar(comp.index, comp[c], bottom=base, color=COR[c], width=0.55, edgecolor="#fcfcfb", linewidth=2, label=c)
    base += comp[c].to_numpy()
for a, v in zip(comp.index, base):
    ax.text(a, v + 60, brl(v), ha="center", fontsize=8, color="#52514e")
ax.set_xticks(comp.index)
ax.set_ylabel("receita do ano (R$ de 2025, 3 ha)")
ax.legend(frameon=False, fontsize=8)
ax.set_title("De onde vem a receita do plano (cenário B: El Niño forte em 2027)", fontsize=10)
plt.tight_layout()
plt.show()
display(comp.round(0))

# %% [markdown]
# ### 10.1 O plano depende do preço da raiz
#
# Em Quixadá, a mandioca quase sumiu depois de 2012 (13 a 40 ha por ano) e o preço implícito de 2016–2025 ficou alto
# (R$ 1,00 a 1,96/kg de 2025). Esse preço é de pouco volume. Uma faixa nova de mandioca por família, em muitas famílias,
# pode não achar esse preço. A tabela refaz o cenário B (bônus 0) com o preço da raiz de Quixadá, a mediana e o P25 do CE
# em 2016–2025, e mostra o **preço de equilíbrio da raiz**: o preço em que o plano empata com a S0 em 3 anos.

# %%
pq = B[(B.cod_mun == QUIXADA) & (B.produto == "Mandioca")].preco_ref.iloc[0]
ce_m = B[(B.uf == "CE") & (B.produto == "Mandioca") & B.ano.isin(PRECO_REF)].preco
opcoes = {"preço de referência de Quixadá": pq, "mediana do CE, 2016–2025": ce_m.median(), "P25 do CE, 2016–2025": ce_m.quantile(0.25)}
sens = []
cen_b = CENARIOS["B. El Niño forte em 2027, depois normal"]


def tot_b(mult):
    global MULT_MAND
    MULT_MAND = mult
    pl = pd.concat([ano_plano(a, c, 0.0) for a, c in zip([2027, 2028, 2029], cen_b)])
    s0 = pd.concat([ano_s0(c) for c in cen_b])
    MULT_MAND = 1.0
    return pl, s0


for nome, p in opcoes.items():
    pl, s0 = tot_b(p / pq)
    sens.append({"preço da raiz": nome, "R$/kg": p, "receita do plano (3 anos)": pl.receita.sum(), "receita da S0": s0.receita.sum(),
                 "plano − S0, margem sobre a semente": (pl.receita.sum() - pl.custo_semente.sum()) - (s0.receita.sum() - s0.custo_semente.sum()),
                 "plano − S0, margem sobre o desembolso": (pl.receita.sum() - pl.custo_desembolso.sum()) - (s0.receita.sum() - s0.custo_desembolso.sum())})
SENS = pd.DataFrame(sens).set_index("preço da raiz")
display(SENS.round(2))
pl0, s00 = tot_b(0.0)
pl1, _ = tot_b(1.0)
mand_rev = pl1.receita.sum() - pl0.receita.sum()  # receita da mandioca no preço de Quixadá
for nivel, col in [("semente", "custo_semente"), ("desembolso", "custo_desembolso")]:
    falta = (s00.receita.sum() - s00[col].sum()) - (pl0.receita.sum() - pl0[col].sum())
    print(f"Preço de equilíbrio da raiz (plano = S0 em 3 anos, cenário B, margem sobre o {nivel}): "
          f"{brl(max(falta, 0) / mand_rev * pq, 2)}/kg (Quixadá hoje: {brl(pq, 2)}; CE mediana {brl(ce_m.median(), 2)})")

# %% [markdown]
# **Leitura.**
# - **Receita por ha em Quixadá** (normal / El Niño forte / seca): milho R$ 967 / R$ 190 / R$ 455 (−80% no El Niño
#   forte); feijão R$ 2.142 / R$ 831 / R$ 1.201; mandioca R$ 13.340 / R$ 6.937 / R$ 5.430 (a seca pela mesorregião).
# - **2027 é o ano caro.** Com El Niño forte, o plano fatura R$ 1.064 contra R$ 1.532 da S0, porque 2/3 ha viram maniva e
#   2/3 ha viram sorgo forrageiro (sem venda). Sobre a semente, +R$ 663 contra +R$ 894; sobre o desembolso, −R$ 6.080
#   contra −R$ 3.161.
# - **2028 e 2029 pagam o plano:** a colheita da mandioca (R$ 8.894 por faixa) leva a receita a R$ 11.093 e R$ 11.876,
#   contra R$ 4.663 da S0.
# - **Em 3 anos (cenário B, bônus 0):** receita de R$ 24.033 contra R$ 10.858. O plano fica **R$ 13.978 acima da S0** na
#   margem sobre a semente e R$ 9.044 acima sobre o desembolso (plano +R$ 5.825; S0 −R$ 3.218).
# - **Cenário C (seca em 2028):** o plano fica R$ 9.608 (semente) e R$ 4.008 (desembolso) acima da S0; sobre o
#   desembolso, o plano perde R$ 1.390 e a S0, R$ 5.398.
# - **O bônus de +24% acrescenta só R$ 155 em 3 anos.**
# - **Tudo depende do preço da raiz.** Com o preço de Quixadá (R$ 1,33/kg, de pouco volume), o plano ganha R$ 13.978 da
#   S0 (semente); com a mediana do CE (R$ 0,84), R$ 7.333; com o P25 do CE (R$ 0,59), R$ 4.009, e sobre o desembolso
#   passa a perder R$ 925. **O plano empata com a S0 se a raiz valer R$ 0,29/kg** (semente) ou R$ 0,66/kg (desembolso).
# - **Fora da conta:** a forragem do sorgo e da palma para as 8 cabras (valor de uso), o Garantia-Safra, a diária da
#   família, a casa de farinha e o frete. O plano pede caixa e trabalho em 2027 e devolve em 2028–2029.
