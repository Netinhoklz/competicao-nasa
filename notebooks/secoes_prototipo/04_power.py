# %% [markdown]
# ## 4. NASA POWER: a assinatura climática do lugar
#
# **Ficha técnica**
# - **O que é:** a API do NASA POWER (comunidade AG), numa célula de 0,5° × 0,625°.
#   - Climatologia (`/api/temporal/climatology/point`): médias mensais de chuva (`PRECTOTCORR`), temperatura média,
#     umidade, vento e radiação.
#   - **Tmax e Tmin: médias das máximas e mínimas diárias de 2001–2024** (`/api/temporal/daily/point`). Até 14/11, a
#     assinatura usava `T2M_MAX` e `T2M_MIN` da climatologia, que **são o extremo do mês (o recorde), não a média**: em
#     Quixadá, janeiro dava 39,3 °C contra 34,9 °C de média diária (revisão C2). Todas as tabelas foram regeradas.
# - **Assinatura (6 variáveis):**
#   - chuva anual;
#   - sazonalidade de Walsh;
#   - meses úmidos (P ≥ ET0/2);
#   - aridez P/ET0 (ET0 FAO-56 Penman-Monteith, que usa a Tmax e a Tmin);
#   - Tmax da estação úmida;
#   - Tmax do mês mais quente.
# - **Arquivo:** `analogos_aprofundado/ne_mun_assinaturas.csv`, uma assinatura no ponto interno de cada um dos 1.794
#   municípios.
#
# **No protótipo:**
# - no NE, a assinatura pré-calculada do município (a célula do ponto interno);
# - fora do NE, a API é consultada ao vivo e guardada em cache pela célula nativa do POWER (revisão M13);
# - a assinatura alimenta os análogos (seção 5).

# %%
VARS = M.VARS
PW = M.MUNA.copy()  # ne_mun_assinaturas.csv, indexado pelo código IBGE
PW["uf"] = UFMUN.reindex(PW.index)
celulas = PW[VARS].drop_duplicates()
n_cel = len({M._chave_power(la, lo) for la, lo in zip(PW.lat, PW.lon)})
print(f"{len(PW)} municípios, sem assinatura: {int(PW.chuva_anual_mm.isna().sum())}; {n_cel} células do POWER e {len(celulas)} "
      "assinaturas diferentes: a célula (~55 × 70 km) cobre vários municípios. Para estatística, a amostra efetiva é de células.")
display(descreve(PW[VARS + ["et0_anual_mm", "altitude_m"]]))
print("Mediana por UF:")
display(PW.groupby("uf")[VARS + ["et0_anual_mm"]].median().reindex(UF_ORDEM).round(2))
cel_uf = PW.assign(cel=[M._chave_power(la, lo) for la, lo in zip(PW.lat, PW.lon)]).groupby("uf").cel.nunique().reindex(UF_ORDEM)
display(pd.DataFrame({"municípios": PW.uf.value_counts().reindex(UF_ORDEM), "células do POWER": cel_uf}).T)

# %%
fig, axs = plt.subplots(1, 4, figsize=(20, 6.2))
for ax, (v, rot, vmin, vmax) in zip(axs, [("chuva_anual_mm", "mm/ano", 400, 2000), ("aridez_P_ET0", "P/ET0", 0.2, 1.2),
                                          ("meses_umidos", "meses", 0, 9), ("tmax_estacao_umida", "°C", 27, 35)]):
    mapa_ne(ax, PW[v], v.replace("_", " "), vmin=vmin, vmax=vmax, rotulo=rot)
plt.tight_layout()
plt.show()

# %%
# por que a assinatura mudou: Tmax/Tmin recorde (climatologia) × médias diárias (2001–2024), no CE e nos lugares dos artigos
old = pd.read_csv(D_APR / "ceara_mun_assinaturas_tmax_recorde.csv", dtype={"cod": str}).set_index("cod")
dif = pd.DataFrame({v: PW.loc[old.index, v] - old[v] for v in ["tmax_estacao_umida", "tmax_mes_mais_quente", "et0_anual_mm",
                                                                 "aridez_P_ET0", "meses_umidos", "chuva_anual_mm"]})
print("CE, 184 municípios: assinatura nova (médias diárias) − antiga (recorde do mês):")
display(dif.describe().T[["mean", "min", "50%", "max"]].round(2).rename(columns={"mean": "média", "50%": "mediana"}))
A_ = pd.read_csv(DADOS / "analogos_artigos" / "assinaturas.csv")
A_old = pd.read_csv(DADOS / "analogos_artigos" / "assinaturas_tmax_recorde.csv")
lug = A_[["ponto", "tmax_estacao_umida", "tmax_mes_mais_quente", "et0_anual_mm"]].merge(
    A_old[["ponto", "tmax_estacao_umida", "tmax_mes_mais_quente", "et0_anual_mm"]], on="ponto", suffixes=("", " (recorde)"))
lug["Δ Tmax úmida"] = lug.tmax_estacao_umida - lug["tmax_estacao_umida (recorde)"]
lug = lug.merge(A_[["ponto", "meses_umidos"]], on="ponto").merge(A_old[["ponto", "meses_umidos"]], on="ponto", suffixes=("", " (recorde)"))
print(f"Lugares de referência (n = {len(lug)}): Δ Tmax da estação úmida de {lug['Δ Tmax úmida'].min():+.1f} a {lug['Δ Tmax úmida'].max():+.1f} °C")
display(lug[lug.ponto.str.contains("Quixadá|Harare|Niamey|Iowa|Bom Jesus|Sobral-CE|Embu") | (lug["Δ Tmax úmida"] == lug["Δ Tmax úmida"].min())].set_index("ponto").round(1))

# %%
fig, axs = plt.subplots(1, 2, figsize=(16, 6))
cor = celulas.corr("spearman")
im = axs[0].imshow(cor.values, cmap=DIV, vmin=-1, vmax=1)
axs[0].set_xticks(range(len(VARS)))
axs[0].set_xticklabels([v.replace("_", " ") for v in VARS], rotation=40, ha="right", fontsize=8)
axs[0].set_yticks(range(len(VARS)))
axs[0].set_yticklabels([v.replace("_", " ") for v in VARS], fontsize=8)
for i in range(len(VARS)):
    for j in range(len(VARS)):
        axs[0].text(j, i, f"{cor.values[i, j]:.2f}", ha="center", va="center", fontsize=7, color="#0b0b0b")
axs[0].grid(False)
plt.colorbar(im, ax=axs[0], shrink=0.8, label="Spearman (assinaturas únicas)")
axs[0].set_title("As 6 variáveis da assinatura andam juntas? (NE)")
pc = cor.where(np.triu(np.ones(cor.shape, bool), 1)).stack().dropna().sort_values()
print("Pares mais negativos:", "; ".join(f"{a} × {b} {v:+.2f}" for (a, b), v in pc.head(3).items()))
print("Pares mais positivos:", "; ".join(f"{a} × {b} {v:+.2f}" for (a, b), v in pc.tail(3).items()))
SIT = M.SIT
LA = M.LA
GL = pd.read_csv(D_APR / "global_assinaturas.csv")
axs[1].scatter(GL.chuva_anual_mm, GL.aridez_P_ET0, s=10, color=CINZA, label=f"grade global de 6° ({len(GL)} pontos de terra)")
axs[1].scatter(celulas.chuva_anual_mm, celulas.aridez_P_ET0, s=12, color=CAT[0], label=f"NE ({len(celulas)} assinaturas únicas)")
axs[1].scatter(LA.chuva_anual_mm, LA.aridez_P_ET0, s=40, color=CAT[1], marker="D", edgecolor="#fcfcfb", label="lugares do catálogo de rotações")
for _, r in LA[LA.lugar.str.contains("Corn Belt|Sahel|Harare|Bom Jesus|Serra Talhada|Europa|Akron")].iterrows():
    axs[1].annotate(r.lugar.split(" (")[0], (r.chuva_anual_mm, r.aridez_P_ET0), fontsize=7, xytext=(4, 3), textcoords="offset points", color="#52514e")
axs[1].set_xlim(0, 2600)
axs[1].set_ylim(0, 2)
axs[1].set_xlabel("chuva anual (mm, POWER)")
axs[1].set_ylabel("aridez P/ET0")
axs[1].legend(fontsize=8, loc="upper left")
axs[1].set_title("Onde o Nordeste fica entre os climas do mundo e dos estudos")
plt.tight_layout()
plt.show()
print("Meses úmidos: municípios por UF")
display(pd.crosstab(PW.uf, PW.meses_umidos.astype(int)).reindex(UF_ORDEM))

# %% [markdown]
# **Leitura:**
# - **Os 1.794 municípios caem em 396 células do POWER**, com 396 assinaturas diferentes. A BA tem 134 células; AL, 13; SE,
#   12. Para estatística, a amostra efetiva é de células, não de municípios.
# - **O clima do NE pelo POWER** (mediana dos municípios): chuva de 898 mm (426 a 2.194), aridez 0,48 (0,18 a 1,68), 5
#   meses úmidos (0 a 12), Tmax da estação úmida de 30,7 °C (27,0 a 36,8) e ET0 de 1.867 mm.
#   - O MA é o mais úmido: 1.394 mm, aridez 0,95 e 7 meses úmidos. RN, BA, PB e PI ficam entre 761 e 826 mm.
#   - A Tmax da estação úmida é maior no RN (32,0 °C) e no PI (31,7) e menor em AL (28,8), SE (29,0) e PE (29,2).
#   - Na BA, 104 municípios têm 11 ou 12 meses úmidos, e 17 não têm nenhum.
# - **A correção da Tmax mudou a assinatura** (CE, 184 municípios):
#   - Tmax da estação úmida −6,0 °C em média (−2,2 a −7,2); Tmax do mês mais quente −2,2 °C; ET0 −98 mm (−19 a −177);
#     aridez +0,02. A chuva não mudou;
#   - em Quixadá, a Tmax da estação úmida foi de 39,2 para 32,6 °C; em Harare, de 35,2 para 27,9 °C;
#   - nos lugares temperados, a ET0 menor muda até os meses úmidos. No Kansas sudoeste, um mês frio passou a contar como
#     úmido, e a Tmax da estação úmida foi de 45,0 para 8,5 °C. É efeito da definição da variável, não do clima.
# - **As variáveis andam juntas** (assinaturas únicas): chuva × aridez +0,94; meses úmidos × aridez +0,88; chuva × meses
#   úmidos +0,82. A Tmax da estação úmida cai onde chove mais (−0,57) e onde a aridez é menor (−0,63). Na prática, a
#   assinatura tem dois eixos: água e calor.
# - **No gráfico de dispersão, o NE ocupa uma faixa larga e estreita ao mesmo tempo:** de 426 a 2.194 mm de chuva, sempre
#   na mesma reta de aridez. Os lugares do catálogo caem quase todos dentro da nuvem do NE; Corn Belt e Europa temperada
#   ficam acima dela, com mais água para a mesma chuva.
