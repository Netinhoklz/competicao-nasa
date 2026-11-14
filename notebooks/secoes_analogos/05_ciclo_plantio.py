# %% [markdown]
# ## 5. Ciclo de plantio: quando a estação começa, pela chuva e pelo verde (1998–2026)
# Para cada município e ano:
# - **Início pela chuva (IMERG V07):** regra agronômica no espírito das regras climáticas de semeadura de Waha et al. 2012.
#   A partir de 1/dez, é o 1º dia com ≥ 20 mm em 3 dias **sem** veranico de ≥ 10 dias secos (< 1 mm) nos 30 dias seguintes.
#   Isso evita o falso início.
# - **Início do verde (MODIS NDVI):** a partir de 1/dez, o 1º composto de 16 dias acima de mínimo + 50% da amplitude da estação.
#
# Perguntas:
# - Qual é a data típica de cada região?
# - O quanto ela varia de um ano para outro?
# - **O El Niño atrasa o início?**
# - Quanto tempo o verde leva para responder à chuva?

# %%
O = pd.read_csv(D_APR / "onset_sos_mun.csv", dtype={"cod": str}, parse_dates=["inicio_chuva", "inicio_verde"])
# dia do ano; dezembro vira negativo (ex.: 15/dez = -16) para a estação ficar contínua
O["doy_chuva"] = np.where(O.inicio_chuva.dt.month == 12, O.inicio_chuva.dt.dayofyear - 365, O.inicio_chuva.dt.dayofyear)
O["doy_verde"] = np.where(O.inicio_verde.dt.month == 12, O.inicio_verde.dt.dayofyear - 365, O.inicio_verde.dt.dayofyear)
O["defasagem_dias"] = O.doy_verde - O.doy_chuva
idx = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
fortes = set(idx[idx.ONI_OND_NDJ >= 1.5].quadra_afetada.astype(int))
lanina = set(idx[idx.ONI_OND_NDJ <= -0.8].quadra_afetada.astype(int))
O["fase"] = np.where(O.ano.isin(fortes), "El Niño forte", np.where(O.ano.isin(lanina), "La Niña", "outros"))
print(f"{O.cod.nunique()} municípios × {O.ano.nunique()} anos; início pela chuva não ocorreu até 31/mai em {O.inicio_chuva.isna().mean():.0%} dos município-anos")

med = O.groupby("cod")[["doy_chuva", "doy_verde", "defasagem_dias"]].median()
var = O.groupby("cod").doy_chuva.agg(lambda s: s.quantile(0.9) - s.quantile(0.1)).rename("amplitude_p10_p90")
geo = municipios_ce_gdf().assign(cod=lambda g: g.codarea.astype(str)).merge(med.join(var), on="cod")
fig, axs = plt.subplots(1, 3, figsize=(18, 6))
geo.plot(column="doy_chuva", ax=axs[0], cmap="viridis", legend=True, legend_kwds={"label": "dia do ano (0 = 1/jan)"})
axs[0].set_title("Início da estação pela chuva (IMERG), mediana 1999–2026")
geo.plot(column="amplitude_p10_p90", ax=axs[1], cmap="magma_r", legend=True, legend_kwds={"label": "dias (p90 − p10)"})
axs[1].set_title("Variação do início entre anos")
geo.plot(column="defasagem_dias", ax=axs[2], cmap="coolwarm", legend=True, legend_kwds={"label": "dias"})
axs[2].set_title("Defasagem chuva → verde (MODIS), mediana")
for a in axs:
    ceara_gdf().boundary.plot(ax=a, color="k", lw=0.8)
    a.set_axis_off()
plt.tight_layout()
plt.show()

# %%
est = O.groupby("ano").agg(inicio_chuva=("doy_chuva", "median"), sem_inicio=("inicio_chuva", lambda s: s.isna().mean() * 100),
                            inicio_verde=("doy_verde", "median"), chuva_fev_mai=("chuva_fev_mai_mm", "median"))
est["fase"] = ["El Niño forte" if a in fortes else ("La Niña" if a in lanina else "outros") for a in est.index]
fig, axs = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
cores = {"El Niño forte": "tab:red", "La Niña": "tab:blue", "outros": "gray"}
axs[0].bar(est.index, est.inicio_chuva, color=[cores[f] for f in est.fase])
axs[0].set_ylabel("início pela chuva (dia do ano, mediana dos municípios)")
axs[0].set_title("Início da estação no Ceará por ano (vermelho = quadra após El Niño forte; azul = La Niña)")
axs[1].bar(est.index, est.sem_inicio, color=[cores[f] for f in est.fase])
axs[1].set_ylabel("% de municípios sem início até 31/mai")
plt.tight_layout()
plt.show()
comp = O.groupby("fase").agg(inicio_chuva_mediana=("doy_chuva", "median"), sem_inicio_pct=("inicio_chuva", lambda s: round(s.isna().mean() * 100, 1)),
                              inicio_verde_mediana=("doy_verde", "median"), defasagem_mediana=("defasagem_dias", "median"), n=("cod", "count"))
display(comp)
from scipy.stats import mannwhitneyu
a = O[O.fase == "El Niño forte"].doy_chuva.dropna()
b = O[O.fase == "outros"].doy_chuva.dropna()
print(f"Mann-Whitney (início pela chuva, El Niño forte × outros, município-anos): p = {mannwhitneyu(a, b).pvalue:.3g}"
      " (atenção: município-anos do mesmo ano não são independentes; a unidade honesta é o ano)")
ea = est[est.fase == "El Niño forte"].inicio_chuva
eo = est[est.fase == "outros"].inicio_chuva
print(f"Por ano: mediana do início em El Niño forte = dia {ea.median():.0f} (n = {len(ea)}); outros = dia {eo.median():.0f} (n = {len(eo)})")

# %%
r = O.dropna(subset=["doy_chuva", "doy_verde"])
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(r.doy_chuva, r.doy_verde, s=4, alpha=0.3)
ax.plot([-30, 150], [-30, 150], "k--", lw=0.8)
ax.set_xlabel("início pela chuva (IMERG), dia do ano")
ax.set_ylabel("início do verde (MODIS), dia do ano")
ax.set_title(f"Chuva × verde por município-ano (r = {r.doy_chuva.corr(r.doy_verde):.2f})")
plt.show()

# %% [markdown]
# **Leitura e uso no produto:**
# - **O portão de janeiro e fevereiro ganha uma data local:** o início pela chuva, por município, com a faixa de
#   variação entre anos. Plantar antes do "início verdadeiro" (sem veranico logo depois) é o falso início que
#   queima semente.
# - **O verde do MODIS confirma o início pela chuva com uma defasagem medida** (mapa à direita). No produto, o NDVI do
#   VIIRS/HLS faz essa confirmação no talhão, quando a nuvem deixar.
# - **O El Niño forte NÃO atrasou o início.** Nos 3 anos de El Niño forte da série (2010, 2016 e 2024), o início pela
#   chuva veio **antes**: mediana no dia 6 contra o dia 18 nos anos neutros (sem La Niña); contra todos os demais anos, dia 15.
#   - São **janeiros chuvosos seguidos de quadra fraca**, o falso início em escala de estação. É o mesmo "janeiro engana"
#     da rodada 2 do conselho.
#   - **O início da chuva sozinho não protege em ano de El Niño.** Por isso a QUADRA decide nos portões de 19/mar e
#     30/abr (chuva desde 1/fev e SMAP), e não só no início.
#   - A comparação honesta é por **ano** (n = 3 contra 18). Os municípios de um mesmo ano não são independentes, então o
#     p do Mann-Whitney por município-ano é otimista.
# - Ficam de fora 8 municípios pequenos, que não contêm o centro de nenhuma célula de 0,1° do IMERG.
# - **Global:** a regra usa só a chuva diária do IMERG, que existe para todo o planeta. Ela conversa com os calendários
#   globais (Sacks 2010, MIRCA2000, WorldCereal) para checagem.
