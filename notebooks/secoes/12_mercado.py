# %% [markdown]
# # 12 · Mercado: AMS Market News (EUA), FAOSTAT e Banco Mundial (globais)
#
# **Pergunta do produto:** a rotação sugerida tem mercado? Quanto rende por hectare e com que risco?
#
# O desafio indica o **USDA AMS Market News**, mas ele só cobre os EUA e a API exige chave.
# Para um produto que funcione **no mundo todo**, a base de mercado precisa ser global. Este estudo:
# 1. documenta o que foi possível obter do AMS;
# 2. valida a cobertura global do **FAOSTAT** (preço ao produtor e produção por país) e do **Pink Sheet** do Banco Mundial (preços internacionais mensais);
# 3. extrai estatísticas de preço, renda por hectare, volatilidade, sazonalidade e tendência para as culturas candidatas do Ceará/Nordeste.

# %%
import sys, json, warnings
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymannkendall as mk

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
plt.rcParams.update({"figure.dpi": 90, "axes.grid": True, "grid.alpha": 0.3})

M = pasta("mercado")
man = json.loads((M / "MANIFESTO.json").read_text(encoding="utf-8"))
pr = pd.read_parquet(DERIV / "faostat_precos_produtor.parquet")
qcl = pd.read_parquet(DERIV / "faostat_producao_qcl.parquet")
br = pd.read_parquet(DERIV / "faostat_brasil_anual.parquet")
pk = pd.read_parquet(DERIV / "mercado_precos_mensal.parquet")
print("FAOSTAT preços:", pr.shape, "| FAOSTAT produção:", qcl.shape, "| Pink Sheet:", pk.shape)

# %% [markdown]
# ## 1. Ficha técnica
#
# | Base | Provedor | Conteúdo | Resolução | Período | Cobertura | Acesso |
# |---|---|---|---|---|---|---|
# | AMS Market News (MyMarketNews/MARS) | USDA | Relatórios de preço de grãos, gado, hortifrúti nos mercados dos EUA | Mercado/terminal, diário/semanal | contínuo | **Só EUA** | API exige chave; `.txt` legados congelados em 2020 |
# | FAOSTAT Producer Prices | FAO | Preço recebido pelo produtor (USD/t, moeda local, índice) | País, anual (+ mensal em alguns países) | 1991–2025 | **Global** (~177 países) | Bulk aberto |
# | FAOSTAT Crops & Livestock (QCL) | FAO | Área colhida, produção, produtividade | País, anual | 1961–2024 | **Global** (~240 áreas) | Bulk aberto |
# | Pink Sheet (CMO) | Banco Mundial | 71 preços internacionais (grãos, oleaginosas, fertilizantes, energia) | Referência mundial, mensal | 1960–out/2026 | **Global** (preço de bolsa/porto) | xlsx aberto |

# %%
print("Status AMS:", man.get("ams_status"))
print("Status CONAB:", man.get("conab_status"))
print("Arquivos brutos:")
for f in sorted((M / "brutos").iterdir()):
    print(f"  {f.name:32s} {f.stat().st_size/1e6:8.2f} MB")
print(f"Total da pasta mercado: {tamanho_pasta(M)/1e6:.1f} MB")
amostra = (M / "brutos" / "ams_gx_gr110_legado.txt").read_text(encoding="cp1252", errors="replace")
print("\nAmostra AMS (relatório legado):\n", amostra[:700])

# %% [markdown]
# ## 2. Validação de cobertura global
#
# Evidência: número de países com dado por ano e mapa mundial de anos com preço ao produtor.
# O código M49 do FAOSTAT casa com o `ISO_N3` do Natural Earth.

# %%
paises = paises_gdf()
pr["m49"] = pr["Area Code (M49)"].astype(str).str.strip("'").str.zfill(3)
qcl["m49"] = qcl["Area Code (M49)"].astype(str).str.strip("'").str.zfill(3)
paises["m49"] = paises["ISO_N3_EH"].astype(str).str.zfill(3)

usd = pr[(pr["Element"] == "Producer Price (USD/tonne)") & (pr["Months"] == "Annual value")]
anos_pais = usd.groupby("m49")["Year"].nunique().rename("anos_com_preco")
cult_pais = usd.groupby("m49")["Item"].nunique().rename("culturas_com_preco")
g = paises.merge(anos_pais, on="m49", how="left").merge(cult_pais, on="m49", how="left")

fig, ax = plt.subplots(1, 2, figsize=(16, 4.8))
g.plot(column="anos_com_preco", ax=ax[0], legend=True, cmap="viridis", missing_kwds={"color": "lightgrey"})
ax[0].set_title("FAOSTAT: anos com preço ao produtor (USD/t), 1991–2025")
g.plot(column="culturas_com_preco", ax=ax[1], legend=True, cmap="magma", missing_kwds={"color": "lightgrey"})
ax[1].set_title("FAOSTAT: nº de culturas candidatas com preço")
for a in ax:
    a.set_axis_off()
plt.tight_layout(); plt.show()

paises_por_ano = pd.DataFrame({
    "preço (países)": usd.groupby("Year")["m49"].nunique(),
    "produção (países)": qcl[qcl["Element"] == "Production"].groupby("Year")["m49"].nunique(),
})
paises_por_ano.plot(figsize=(10, 3.2), title="Países com dado por ano (FAOSTAT)")
plt.show()

cobertos = g["anos_com_preco"].notna().sum()
terra_agric = paises[paises["CONTINENT"] != "Antarctica"]
print(f"Países do mapa (Natural Earth 110m, sem Antártida): {len(terra_agric)}")
print(f"Com preço ao produtor FAOSTAT: {cobertos} ({cobertos/len(terra_agric):.0%})")
prod_paises = qcl[qcl['Element']=='Production']['m49'].nunique()
print(f"Áreas com produção FAOSTAT (inclui agregados regionais): {prod_paises}")
print("Pink Sheet: preço de referência internacional único por commodity (não é por país).")
print("AMS: somente mercados dos EUA.")

# %% [markdown]
# **Veredito de cobertura:**
# - **FAOSTAT (preço e produção): GLOBAL.** Quase todos os países agrícolas têm série; as lacunas ficam em países pequenos, em conflito ou com estatística fraca. Escala **nacional** (não serve para município — para o Ceará, complementar com IBGE PAM).
# - **Pink Sheet: GLOBAL como referência** (preço de bolsa/porto). Bom para tendência, choques e fertilizantes; não reflete o preço na porteira do Sertão.
# - **AMS Market News: NÃO É GLOBAL** (só EUA, chave obrigatória). Fica como módulo opcional para usuários dos EUA.

# %% [markdown]
# ## 3. Qualidade dos dados

# %%
flags = pd.DataFrame({
    "preço": pr["Flag"].value_counts(normalize=True),
    "produção": qcl["Flag"].value_counts(normalize=True),
}).fillna(0)
print("Distribuição de flags FAOSTAT (A=oficial, E=estimado, I=imputado, M=faltante, X=fonte internacional):")
print((flags * 100).round(1))

br_usd = usd[usd["Area"] == "Brazil"]
grade = br_usd.pivot_table(index="Item", columns="Year", values="Value", aggfunc="mean")
fig, ax = plt.subplots(figsize=(14, 5.5))
sns.heatmap(grade.notna(), cbar=False, cmap=["#eee", "#2a9d8f"], ax=ax)
ax.set_title("Brasil: anos com preço ao produtor (verde) por cultura — FAOSTAT")
plt.tight_layout(); plt.show()
print("Completude (anos com preço / anos possíveis) no Brasil:")
print((grade.notna().mean(axis=1) * 100).round(0).sort_values().to_string())

pk_largo = pk.pivot_table(index="data", columns="commodity", values="preco")
print("\nPink Sheet: % de meses sem valor por commodity (top 10):")
print((pk_largo.isna().mean() * 100).round(1).sort_values(ascending=False).head(10).to_string())

# %% [markdown]
# ## 4. Estatística descritiva — Brasil e mundo
#
# FAOSTAT é nacional; o Nordeste/Ceará entra como contexto do Brasil. Indicadores para os últimos 5 anos disponíveis.

# %%
def ultimo_quinquenio(df, col="Value"):
    ult = df["Year"].max()
    return df[df["Year"] > ult - 5]

prod = qcl[qcl["Element"] == "Production"]
mundo = prod[prod["Area"] == "World"].groupby("Item").apply(lambda d: ultimo_quinquenio(d)["Value"].mean())
brasil = prod[prod["Area"] == "Brazil"].groupby("Item").apply(lambda d: ultimo_quinquenio(d)["Value"].mean())
rend = qcl[qcl["Element"] == "Yield"]
rend_br = rend[rend["Area"] == "Brazil"].groupby("Item").apply(lambda d: ultimo_quinquenio(d)["Value"].mean() / 1000)
rend_mu = rend[rend["Area"] == "World"].groupby("Item").apply(lambda d: ultimo_quinquenio(d)["Value"].mean() / 1000)
preco_br = br_usd.groupby("Item").apply(lambda d: ultimo_quinquenio(d)["Value"].mean())
preco_cv = br_usd.groupby("Item").apply(lambda d: ultimo_quinquenio(d)["Value"].std() / ultimo_quinquenio(d)["Value"].mean())
med_mundo = usd.groupby(["Item", "Year"])["Value"].median().reset_index()
preco_mundo = med_mundo.groupby("Item").apply(lambda d: ultimo_quinquenio(d)["Value"].mean())

tab = pd.DataFrame({
    "produção BR (Mt)": brasil / 1e6,
    "% do mundo": 100 * brasil / mundo,
    "produtiv. BR (t/ha)": rend_br,
    "produtiv. mundo (t/ha)": rend_mu,
    "preço BR (USD/t)": preco_br,
    "preço mediano mundo (USD/t)": preco_mundo,
    "CV preço BR 5a": preco_cv,
}).round(2)
tab["receita BR (USD/ha)"] = (tab["produtiv. BR (t/ha)"] * tab["preço BR (USD/t)"]).round(0)
tab = tab.sort_values("receita BR (USD/ha)", ascending=False)
print(tab.to_string())

# %%
fig, ax = plt.subplots(1, 2, figsize=(15, 5))
t2 = tab.dropna(subset=["produtiv. BR (t/ha)", "produtiv. mundo (t/ha)"])
ax[0].scatter(t2["produtiv. mundo (t/ha)"], t2["produtiv. BR (t/ha)"])
for n, r in t2.iterrows():
    ax[0].annotate(n.split(",")[0][:14], (r["produtiv. mundo (t/ha)"], r["produtiv. BR (t/ha)"]), fontsize=7)
lim = max(t2[["produtiv. mundo (t/ha)", "produtiv. BR (t/ha)"]].max()) * 1.1
ax[0].plot([0.1, lim], [0.1, lim], "k--", lw=0.8)
ax[0].set_xscale("log"); ax[0].set_yscale("log")
ax[0].set_xlabel("produtividade mundial (t/ha)"); ax[0].set_ylabel("produtividade Brasil (t/ha)")
ax[0].set_title("Brasil × mundo (acima da diagonal = Brasil mais produtivo)")
t3 = tab.dropna(subset=["receita BR (USD/ha)", "CV preço BR 5a"])
ax[1].scatter(t3["CV preço BR 5a"], t3["receita BR (USD/ha)"], s=40, c="tab:green")
for n, r in t3.iterrows():
    ax[1].annotate(n.split(",")[0][:14], (r["CV preço BR 5a"], r["receita BR (USD/ha)"]), fontsize=7)
ax[1].set_yscale("log"); ax[1].set_xlabel("CV do preço ao produtor (5 anos)")
ax[1].set_ylabel("receita bruta média (USD/ha, escala log)")
ax[1].set_title("Brasil: renda por hectare × risco de preço")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 5. Sazonalidade de preço
#
# (a) Preço ao produtor **mensal no Brasil** (FAOSTAT, moeda local, 2015–2025): índice sazonal = média do mês ÷ média anual.
# (b) Pink Sheet (internacional): índice sazonal de 1990–2025 calculado sobre os preços sem tendência (razão à média móvel de 12 meses).

# %%
meses = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
         "October", "November", "December"]
bm = pr[(pr["Area"] == "Brazil") & (pr["Element"] == "Producer Price (LCU/tonne)") & (pr["Months"].isin(meses))].copy()
bm["mes"] = bm["Months"].map({m: i + 1 for i, m in enumerate(meses)})
bm["rel"] = bm["Value"] / bm.groupby(["Item", "Year"])["Value"].transform("mean")
ind_br = bm.groupby(["Item", "mes"])["rel"].mean().unstack()
ind_br = ind_br[ind_br.notna().sum(axis=1) >= 10]
fig, ax = plt.subplots(figsize=(13, 0.35 * len(ind_br) + 2))
sns.heatmap(ind_br, cmap="RdBu_r", center=1, annot=True, fmt=".2f", ax=ax, cbar_kws={"label": "preço do mês / média do ano"})
ax.set_title("Brasil: sazonalidade do preço ao produtor (FAOSTAT mensal, 2015–2025)")
ax.set_xlabel("mês")
plt.tight_layout(); plt.show()
amp = (ind_br.max(axis=1) - ind_br.min(axis=1)).sort_values(ascending=False)
print("Amplitude sazonal (máx − mín do índice):\n", amp.round(2).to_string())

# %%
sel = ["Maize", "Sorghum", "Soybeans", "Groundnuts", "Cotton, A Index", "Sugar, world", "Banana, US",
       "Rice, Thai 5%", "Wheat, US HRW", "Urea", "DAP", "Potassium chloride **"]
sel = [s for s in sel if s in pk_largo.columns]
base = pk_largo.loc["1990":, sel]
razao = base / base.rolling(12, center=True).mean()
ind_pk = razao.groupby(razao.index.month).mean().T
fig, ax = plt.subplots(figsize=(13, 5))
sns.heatmap(ind_pk, cmap="RdBu_r", center=1, annot=True, fmt=".2f", ax=ax)
ax.set_title("Pink Sheet: índice sazonal internacional (1990–2025, sem tendência)")
ax.set_xlabel("mês")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6. Tendências (Mann-Kendall + inclinação de Sen)
#
# (a) Produtividade do Brasil 1961–2024 por cultura. (b) Preços internacionais 1990–2026 (nominais, USD).

# %%
linhas = []
for item, d in rend[rend["Area"] == "Brazil"].groupby("Item"):
    s = d.sort_values("Year").set_index("Year")["Value"].dropna() / 1000
    if len(s) < 15:
        continue
    t = mk.original_test(s.values)
    linhas.append({"cultura": item, "anos": len(s), "tendência": t.trend, "p": t.p,
                   "Sen (t/ha/ano)": t.slope, "Sen % ao ano": 100 * t.slope / s.mean(),
                   "produtiv. 1º quinquênio": s.iloc[:5].mean(), "produtiv. último quinquênio": s.iloc[-5:].mean()})
mk_br = pd.DataFrame(linhas).sort_values("Sen % ao ano", ascending=False)
print(mk_br.round(4).to_string(index=False))

# %%
linhas = []
for c in sel:
    s = pk_largo.loc["1990":, c].dropna()
    anual = s.resample("YE").mean()
    t = mk.original_test(anual.values)
    linhas.append({"commodity": c, "tendência": t.trend, "p": round(t.p, 4),
                   "Sen (USD/ano)": round(t.slope, 2), "Sen % ao ano": round(100 * t.slope / anual.mean(), 2)})
print(pd.DataFrame(linhas).to_string(index=False))

fig, ax = plt.subplots(figsize=(13, 4.5))
norm = pk_largo.loc["2000":, sel] / pk_largo.loc["2014":"2016", sel].mean()
norm.plot(ax=ax, lw=1)
ax.set_title("Pink Sheet: preços normalizados (média 2014–2016 = 1)")
ax.legend(ncol=4, fontsize=7)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 7. Variabilidade, extremos e correlação entre mercados
#
# - Volatilidade anualizada = desvio-padrão dos retornos log mensais × √12.
# - Pior queda (drawdown) e maior alta em 12 meses.
# - Correlação de retornos: culturas pouco correlacionadas diversificam a renda da rotação.
# - Fertilizantes (ureia, DAP, KCl) × grãos: os choques de 2021–2022 e de mar–mai/2026 mostram o valor econômico das leguminosas, que fixam nitrogênio.

# %%
ret = np.log(pk_largo.loc["1990":, sel]).diff()
vol = (ret.std() * np.sqrt(12)).rename("volatilidade anual")
dd = (pk_largo.loc["1990":, sel] / pk_largo.loc["1990":, sel].cummax() - 1).min().rename("pior drawdown")
alta12 = (pk_largo.loc["1990":, sel].pct_change(12)).max().rename("maior alta 12m")
print(pd.concat([vol, dd, alta12], axis=1).round(2).sort_values("volatilidade anual", ascending=False).to_string())

fig, ax = plt.subplots(1, 2, figsize=(16, 6))
sns.heatmap(ret.corr(), cmap="RdBu_r", center=0, vmin=-1, vmax=1, annot=True, fmt=".2f", ax=ax[0], annot_kws={"size": 7})
ax[0].set_title("Correlação dos retornos mensais (1990–2026)")
fert = pk_largo.loc["2005":, [c for c in ["Urea", "DAP", "Potassium chloride **", "Maize", "Soybeans"] if c in pk_largo]]
(fert / fert.loc["2019"].mean()).plot(ax=ax[1])
ax[1].axvspan("2021-06", "2022-12", color="orange", alpha=0.2, label="choque de fertilizantes 2021–22")
ax[1].axvspan("2026-02", "2026-06", color="red", alpha=0.2, label="choque de fertilizantes 2026")
ax[1].set_title("Fertilizantes × grãos (média 2019 = 1)")
ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

razao_ureia_milho = (pk_largo["Urea"] / pk_largo["Maize"]).loc["2000":]
print(f"Razão ureia/milho (USD/t ÷ USD/t): média 2000–2020 = {razao_ureia_milho.loc[:'2020'].mean():.2f}; "
      f"pico = {razao_ureia_milho.max():.2f} em {razao_ureia_milho.idxmax():%Y-%m}; atual = {razao_ureia_milho.dropna().iloc[-1]:.2f}")

# %% [markdown]
# ### Extremos de produção no Brasil — anos de quebra
# Desvio da produtividade em relação à tendência (LOESS simples por média móvel de 7 anos). Anos com desvio < −15 % são "quebras".

# %%
quebras = []
for item in ["Maize (corn)", "Beans, dry", "Cassava, fresh", "Seed cotton, unginned", "Sorghum", "Rice", "Soya beans"]:
    s = rend[(rend["Area"] == "Brazil") & (rend["Item"] == item)].set_index("Year")["Value"].sort_index()
    tend = s.rolling(7, center=True, min_periods=3).median()
    desvio = s / tend - 1
    for ano, v in desvio[desvio < -0.15].items():
        quebras.append({"cultura": item, "ano": ano, "desvio %": round(100 * v, 1)})
print(pd.DataFrame(quebras).sort_values(["ano", "cultura"]).to_string(index=False))

# %% [markdown]
# ## 8. Insights e ideias para o produto
#
# 1. **O AMS não serve para um produto mundial.** Só EUA, com chave e formato instável. A camada de mercado global deve vir do **FAOSTAT** (preço ao produtor e produtividade por país) com o **Pink Sheet** como sinal internacional mensal, e o AMS como plugin opcional nos EUA.
# 2. **Renda por hectare × risco** (gráfico da seção 4) é diretamente um eixo do motor de rotação: `receita esperada = produtividade atingível (GAEZ, por pixel) × preço ao produtor (FAOSTAT, por país)`, com o CV do preço como penalidade de risco.
# 3. **Diversificação de renda:** a matriz de correlação de retornos mostra pares pouco correlacionados (ex.: banana × grãos; açúcar × fertilizantes). Uma rotação com culturas de baixa correlação reduz a variância da renda — dá para pontuar isso como um "índice de portfólio" da rotação.
# 4. **Choques de fertilizantes:** a razão ureia/milho (média 1,5 em 2000–2020) chegou a 3,6 em nov/2021 e a **4,0 em abr/2026** — ou seja, o choque se repetiu este ano. Leguminosas (feijão-caupi, guandu, amendoim) que fixam N viram **seguro contra preço de insumo** — argumento econômico, além do agronômico, para incluí-las na rotação.
# 5. **Sazonalidade de preço** (FAOSTAT mensal do Brasil) indica janelas de venda: o produtor que colhe fora do pico de oferta ganha mais. O motor pode sugerir **datas de plantio que deslocam a colheita** para meses de preço mais alto, desde que caibam na janela climática (POWER/IMERG/ZARC).
# 6. **Anos de quebra** aparecem nas séries nacionais; para o Ceará, as quebras são muito mais fortes (seca 2012–2017). Ideia: cruzar com IMERG/SMAP para mostrar que a "renda esperada" precisa ser ajustada pelo risco climático local.
#
# **Limitações:** FAOSTAT é anual e nacional (não reflete o preço local no Ceará); Pink Sheet é nominal em USD (deflacionar para comparar décadas); CONAB (preços por UF) ficou inacessível daqui — certificado TLS do portal com nome errado.
