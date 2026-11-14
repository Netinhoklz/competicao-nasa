# %% [markdown]
# # 13. Bases de ligação: teleconexões (ENSO e Atlântico) e produção agrícola do Ceará (IBGE PAM)
#
# Estas bases não estão na lista do desafio, mas são as que **ligam o clima observado pela NASA à safra real**.
#
# **Ficha técnica — índices climáticos**
#
# | Índice | Provedor | O que mede | Período | Acesso |
# |---|---|---|---|---|
# | ONI | NOAA CPC (ERSSTv5) | anomalia de TSM no Niño 3.4, média de 3 meses (El Niño ≥ +0,5; La Niña ≤ −0,5) | 1950 → set/2026 | aberto |
# | TNA | NOAA PSL (HadISST1.1) | anomalia de TSM do Atlântico tropical norte (5,5°N–23,5°N) | 1948 → set/2026 | aberto |
# | TSA | NOAA PSL (HadISST1.1) | anomalia de TSM do Atlântico tropical sul (0–20°S) | 1948 → set/2026 | aberto |
# | Dipolo | calculado | TNA − TSA: positivo empurra a Zona de Convergência Intertropical para o norte → **quadra seca no Ceará** | 1948 → set/2026 | — |
#
# **Ficha técnica — IBGE PAM (Produção Agrícola Municipal)**
#
# | Item | Valor |
# |---|---|
# | Provedor | IBGE, API SIDRA, tabelas 1612 (lavouras temporárias, 45 produtos) e 1613 (permanentes, 42 produtos) |
# | Recorte | 184 municípios do Ceará + 9 UFs do Nordeste |
# | Variáveis | área plantada / destinada à colheita (ha, desde 1988), área colhida (ha), quantidade (t), rendimento (kg/ha), valor (mil R$; moedas antigas antes de 1994) |
# | Resolução | município, anual; 1974 → 2025 |
# | Acesso | aberto, sem login; licença de dados públicos do IBGE |
# | Cobertura | **somente Brasil** (equivalentes globais: FAOSTAT por país, GDHY em grade, estatísticas nacionais como USDA NASS) |

# %%
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymannkendall as mk
from scipy import stats

warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams.update({"figure.dpi": 90, "axes.grid": True, "grid.alpha": 0.3})
idx = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
pam = pd.read_parquet(DADOS / "ibge_pam" / "pam_ce_municipios.parquet")
pam_ne = pd.read_parquet(DADOS / "ibge_pam" / "pam_ne_estados.parquet")
prod = pam[pam.cod_produto != "0"]
print("Índices:", idx.columns.tolist(), idx.index.min().date(), "→", idx.index.max().date())
print("PAM Ceará:", len(pam), "linhas |", prod.produto.nunique(), "produtos |", pam.cod_local.nunique(), "municípios |", pam.ano.min(), "–", pam.ano.max())

# %% [markdown]
# ## 13.1 Cobertura e qualidade
# Os índices são séries únicas de teleconexão; "cobertura global" não se aplica. O que importa é que eles são
# **calculados para o mundo todo** e servem de preditor em qualquer região onde ENSO/Atlântico pesam. O PAM é só
# brasileiro: para o produto mundial, a camada equivalente é o FAOSTAT (país) ou o GDHY (grade de 0,5°).

# %%
print("Códigos do SIDRA no PAM do Ceará (fração das linhas):")
print((pam.valor_txt.where(pam.valor_txt.isin(["-", "...", "..", "X"]), "número").value_counts(normalize=True)).round(3).to_string())
cob = prod[prod.valor > 0].groupby("variavel").ano.agg(["min", "max"])
print("\nAnos com valores positivos por variável:\n", cob.to_string())
print("\nMunicípios por ano (mín/máx):", prod.groupby("ano").cod_local.nunique().agg(["min", "max"]).to_dict())
r = prod[prod.variavel == "Rendimento médio da produção"]
print("Rendimentos ≤ 0 ou ausentes com área colhida > 0:",
      int(prod.pivot_table(index=["cod_local", "ano", "produto"], columns="variavel", values="valor")
          .pipe(lambda d: ((d["Área colhida"] > 0) & ~(d["Rendimento médio da produção"] > 0)).sum())))
fig, ax = plt.subplots(figsize=(13, 3.6))
for v in ["ONI", "DIPOLO_TNA_menos_TSA"]:
    idx[v].loc["1980":].plot(ax=ax, label=v)
ax.axhline(0, color="k", lw=0.6); ax.legend(); ax.set_title("ONI e dipolo do Atlântico (TNA − TSA)"); plt.show()
print("Últimos valores (set/2026):", idx.iloc[-1].round(2).to_dict())

# %% [markdown]
# ## 13.2 O que o Ceará planta (estatística descritiva, 2019–2025)

# %%
area_v = ["Área plantada", "Área destinada à colheita"]
rec = prod[prod.ano.between(2019, 2025)]
area = rec[rec.variavel.isin(area_v)].groupby("produto").valor.sum() / 7
valor = rec[rec.variavel == "Valor da produção"].groupby("produto").valor.sum() / 7
top = pd.DataFrame({"área média ha": area, "% da área": 100 * area / area.sum(), "valor médio mil R$": valor,
                    "R$/ha": 1000 * valor / area}).sort_values("área média ha", ascending=False)
print(top.head(15).round(1).to_string())
print(f"\nMilho + feijão + caju = {top['% da área'].iloc[:3].sum():.0f}% da área cultivada")

rend = prod[(prod.variavel == "Rendimento médio da produção") & (prod.valor > 0)]
fig, axs = plt.subplots(1, 3, figsize=(16, 4))
for a, c in zip(axs, ["Milho (em grão)", "Feijão (em grão)", "Mandioca"]):
    x = rend[(rend.produto == c) & rend.ano.between(2000, 2025)].valor
    a.hist(x, bins=50, color="tab:green", alpha=0.8)
    a.set_title(f"{c}: rendimento municipal 2000–2025\nmediana {x.median():.0f} kg/ha | assim. {stats.skew(x):.2f} | curt. {stats.kurtosis(x):.1f}")
plt.tight_layout(); plt.show()

# %%
mun = municipios_ce_gdf()
mun["cod_local"] = mun["codarea"].astype(str)
a_mun = rec[rec.variavel.isin(area_v)].groupby(["cod_local", "produto"]).valor.sum().reset_index()
princ = a_mun.sort_values("valor").groupby("cod_local").tail(1).set_index("cod_local")["produto"]
rm = rend[(rend.produto == "Milho (em grão)") & rend.ano.between(2015, 2025)].groupby("cod_local").valor.median()
g = mun.merge(princ.rename("principal"), left_on="cod_local", right_index=True, how="left") \
       .merge(rm.rename("rend_milho"), left_on="cod_local", right_index=True, how="left")
fig, axs = plt.subplots(1, 2, figsize=(15, 6))
g.plot(column="principal", categorical=True, legend=True, ax=axs[0], cmap="tab10",
       legend_kwds={"loc": "lower left", "fontsize": 7})
axs[0].set_title("Cultura com maior área por município (2019–2025)")
g.plot(column="rend_milho", cmap="YlGn", legend=True, ax=axs[1], missing_kwds={"color": "0.85"})
axs[1].set_title("Rendimento mediano do milho 2015–2025 (kg/ha)")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 13.3 Tendências de longo prazo e o colapso do algodão

# %%
ce = prod.groupby(["ano", "produto", "variavel"]).valor.sum().unstack("variavel")
culturas = ["Milho (em grão)", "Feijão (em grão)", "Mandioca", "Castanha de caju", "Arroz (em casca)",
            "Algodão arbóreo (em caroço)", "Algodão herbáceo (em caroço)", "Cana-de-açúcar", "Banana (cacho)", "Coco-da-baía*"]
res = []
for c in culturas:
    s = ce.xs(c, level="produto")
    for v in ["Área colhida", "Quantidade produzida"]:
        x = s[v].loc[1974:2025].dropna()
        rr = mk.original_test(x.values)
        res.append((c, v, rr.trend, round(rr.p, 4), rr.slope))
    y = (s["Quantidade produzida"] * 1000 / s["Área colhida"]).replace([np.inf], np.nan).loc[1974:2025].dropna()
    rr = mk.original_test(y.values)
    res.append((c, "rendimento kg/ha", rr.trend, round(rr.p, 4), rr.slope))
print(pd.DataFrame(res, columns=["cultura", "variável", "tendência MK", "p", "Sen por ano"]).round(2).to_string(index=False))

fig, axs = plt.subplots(1, 2, figsize=(15, 4.2))
for c in culturas[:7]:
    (ce.xs(c, level="produto")["Área colhida"] / 1e3).plot(ax=axs[0], label=c)
axs[0].set_title("Área colhida no Ceará (mil ha)"); axs[0].legend(fontsize=7)
axs[0].axvline(1983, color="r", ls="--"); axs[0].text(1984, axs[0].get_ylim()[1] * 0.9, "chegada do bicudo (1983)", color="r", fontsize=8)
for c in ["Milho (em grão)", "Feijão (em grão)"]:
    s = ce.xs(c, level="produto"); (s["Quantidade produzida"] * 1000 / s["Área colhida"]).plot(ax=axs[1], marker=".", label=c)
axs[1].set_title("Rendimento estadual (kg/ha)"); axs[1].legend(); plt.tight_layout(); plt.show()
alg = ce.xs("Algodão arbóreo (em caroço)", level="produto")["Área colhida"]
print(f"Algodão arbóreo: {alg.loc[1974:1982].max()/1e3:.0f} mil ha (pico até 1982) → {alg.loc[1995]/1e3:.0f} mil ha (1995) → {alg.loc[2016]:.0f} ha (2016)")

# %% [markdown]
# ## 13.4 Quebra de safra: perda de área e rendimento nas secas

# %%
mz = ce.xs("Milho (em grão)", level="produto"); fj = ce.xs("Feijão (em grão)", level="produto")
perda = pd.DataFrame({"milho": 1 - mz["Área colhida"] / mz["Área plantada"], "feijão": 1 - fj["Área colhida"] / fj["Área plantada"]}).loc[1988:]
rend_ce = pd.DataFrame({"milho": mz["Quantidade produzida"] * 1000 / mz["Área colhida"],
                        "feijão": fj["Quantidade produzida"] * 1000 / fj["Área colhida"]}).loc[1974:]
# anomalia de rendimento relativa à tendência (LOWESS-like via mediana móvel de 9 anos)
tend = rend_ce.rolling(9, center=True, min_periods=5).median()
anom_r = rend_ce / tend - 1
fig, axs = plt.subplots(2, 1, figsize=(14, 7))
perda.plot.bar(ax=axs[0], width=0.85); axs[0].set_title("Fração da área plantada perdida (1 − colhida/plantada)")
anom_r.plot.bar(ax=axs[1], width=0.85); axs[1].set_title("Anomalia de rendimento relativa à tendência de 9 anos")
plt.tight_layout(); plt.show()
print("Piores anos (anomalia de rendimento do milho):", anom_r.milho.nsmallest(8).round(2).to_dict())
print("Perda de área ≥ 20% (milho):", perda.milho[perda.milho >= 0.2].round(2).to_dict())
print("Perda média de área do milho 1988–1999:", round(perda.milho.loc[1988:1999].mean(), 3),
      "| 2000–2025:", round(perda.milho.loc[2000:2025].mean(), 3),
      "→ a partir de ~2000 a perda deixa de aparecer na área e aparece só no rendimento (mudança de método/registro).")

# %% [markdown]
# ## 13.5 Clima × chuva × safra: a cadeia de teleconexão
# Hipótese física conhecida: El Niño (ONI > 0) e dipolo positivo (Atlântico norte mais quente) deslocam a ZCIT para
# o norte e secam a quadra chuvosa do Ceará. Testamos a cadeia **índice (dez–mar) → chuva fev–mai (POWER) →
# rendimento do milho/feijão (PAM)**.

# %%
def media_meses(s, meses):
    s = s.copy()
    df = s.to_frame("v"); df["ano"] = df.index.year; df["m"] = df.index.month
    return df[df.m.isin(meses)].groupby("ano").v.mean()

# ONI de dez–mar: desloca 1 mês para que dezembro conte no ano da quadra seguinte
o = idx["ONI"].copy(); o.index = o.index + pd.DateOffset(months=1)
oni_djf = media_meses(o, [1, 2, 3, 4]).rename("ONI_dez_mar")
dip_fmam = media_meses(idx["DIPOLO_TNA_menos_TSA"], [2, 3, 4, 5]).rename("dipolo_fev_mai")
dip_jan = media_meses(idx["DIPOLO_TNA_menos_TSA"], [1]).rename("dipolo_jan")
tab = pd.concat([oni_djf, dip_fmam, dip_jan, anom_r.milho.rename("anom_rend_milho"), anom_r["feijão"].rename("anom_rend_feijao")], axis=1)

p = DERIV / "power_ce_mensal.parquet"
if p.exists():
    pw = pd.read_parquet(p)
    pr = pw[pw.variavel == "PRECTOTCORR"].set_index("data")["valor"]
    q = pr[pr.index.month.isin([2, 3, 4, 5])]  # já em mm/mês (soma mensal)
    chuva = q.groupby(q.index.year).sum(min_count=4)
    tab["chuva_fev_mai_mm"] = chuva
tab = tab.loc[1981:2025]
cor = tab.corr(method="spearman")
print("Correlação de Spearman (1981–2025):\n", cor.round(2).to_string())
n = tab.dropna().shape[0]
print("anos com todos os dados:", n)

if "chuva_fev_mai_mm" in tab:
    fig, axs = plt.subplots(1, 3, figsize=(17, 4.5))
    for a, (x, y) in zip(axs, [("ONI_dez_mar", "chuva_fev_mai_mm"), ("dipolo_fev_mai", "chuva_fev_mai_mm"), ("chuva_fev_mai_mm", "anom_rend_milho")]):
        d = tab[[x, y]].dropna(); rr = stats.spearmanr(d[x], d[y])
        a.scatter(d[x], d[y]);
        for ano, row in d.iterrows():
            if ano in (1983, 1993, 1998, 2012, 2015, 2016, 1985, 2009, 2024):
                a.annotate(str(ano), (row[x], row[y]), fontsize=7)
        a.set_xlabel(x); a.set_ylabel(y); a.set_title(f"ρ = {rr.correlation:.2f} (p = {rr.pvalue:.3f})")
    plt.tight_layout(); plt.show()

    # modelo simples de previsão da quadra: chuva ~ ONI + dipolo (validação deixando um ano de fora)
    d = tab[["ONI_dez_mar", "dipolo_fev_mai", "dipolo_jan", "chuva_fev_mai_mm"]].dropna()
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import LeaveOneOut, cross_val_predict
    for cols in (["ONI_dez_mar"], ["dipolo_fev_mai"], ["ONI_dez_mar", "dipolo_fev_mai"], ["ONI_dez_mar", "dipolo_jan"]):
        pred = cross_val_predict(LinearRegression(), d[cols], d.chuva_fev_mai_mm, cv=LeaveOneOut())
        r2 = 1 - ((d.chuva_fev_mai_mm - pred) ** 2).sum() / ((d.chuva_fev_mai_mm - d.chuva_fev_mai_mm.mean()) ** 2).sum()
        tercil = pd.qcut(d.chuva_fev_mai_mm, 3, labels=False); tp = pd.qcut(pred, 3, labels=False)
        print(f"preditores {cols}: R² fora da amostra = {r2:.2f} | acerto de tercil = {(tercil.values == tp).mean():.2f} (acaso = 0,33)")
    print("Obs.: 'dipolo_fev_mai' é concomitante à quadra (não é previsão); 'dipolo_jan' e ONI dez–mar são conhecidos antes/no início.")

# %%
# ENSO de 2026: o que esperar para a quadra de 2027?
on = idx["ONI"].loc["2025":]
print("ONI recente:", on.round(2).to_dict())
if "chuva_fev_mai_mm" in tab:
    forte = tab[tab.ONI_dez_mar >= 1.0]
    print("\nQuadras após El Niño forte (ONI dez–mar ≥ 1,0):")
    print(forte[["ONI_dez_mar", "chuva_fev_mai_mm", "anom_rend_milho", "anom_rend_feijao"]].round(2).to_string())
    print("Chuva fev–mai média nesses anos:", round(forte.chuva_fev_mai_mm.mean()), "mm vs climatologia", round(tab.chuva_fev_mai_mm.mean()), "mm")

# %% [markdown]
# ## 13.6 Insights e uso no produto
#
# - **O Ceará planta três coisas**: milho (40%), feijão (26%) e caju (19%) somam **85% da área** em 2019–2025; milho e
#   feijão são de sequeiro e, em geral, consorciados.
#   Na prática, a "rotação atual" típica é **milho+feijão todo ano na mesma área**, um ótimo caso para o desafio: a
#   ferramenta compara essa base com alternativas (sorgo, feijão-caupi solteiro, palma forrageira, gergelim, adubos
#   verdes, pousio melhorado).
# - **O colapso do algodão arbóreo** (de ~1,2 milhão de ha antes de 1983 a zero em 2016) é o caso histórico mais forte do
#   Nordeste de praga (bicudo) combinada com seca destruindo um sistema produtivo. É argumento direto para a parte
#   de "quebrar ciclos de pragas" com rotação e diversificação.
# - **Quebra de safra é climática e previsível em parte**. A cadeia fecha com números (Spearman, 1981–2025):
#   chuva fev–mai × anomalia de rendimento do milho **ρ = 0,75** (feijão 0,62); ONI dez–mar × chuva **ρ = −0,46**;
#   dipolo fev–mai × chuva **ρ = −0,58**. Nas **7 quadras após El Niño forte** (ONI ≥ 1,0: 1983, 1987, 1992, 1998, 2010,
#   2016, 2024) a chuva fev–mai média foi **402 mm contra 593 mm** da climatologia (−32%), e o milho rendeu de 43% a
#   64% abaixo da tendência em 6 delas (2024 foi a exceção).
# - **O ONI de set/2026 está em +2,46** (El Niño forte e subindo), o que pede **alerta para a quadra de 2027**. Uma
#   rotação com culturas tolerantes à seca (sorgo, caupi precoce, palma forrageira) deve subir no ranking do app quando
#   o índice estiver assim. É o gancho perfeito para a apresentação: "o app já diria hoje o que plantar em 2027".
# - **Previsibilidade real, mas modesta**: só com o ONI de dez–mar, o tercil da quadra acerta 44% (acaso 33%;
#   R² fora da amostra 0,15). Com o dipolo concomitante chega a R² 0,33, mas esse dado só existe durante a quadra.
#   O produto deve falar em **probabilidades por tercil**, nunca em certeza.
# - **Mudança de registro no PAM**: até 1999 a seca aparece como perda de área (até 71% do milho em 1993); depois de
#   2000 a área colhida ≈ plantada e a perda aparece só no rendimento. Qualquer modelo treinado com o PAM deve usar
#   **rendimento** como alvo e tratar essa quebra de série.
# - **Ideias de ML**:
#   1. *Previsão de tercil da quadra chuvosa* com ONI/dipolo (regressão logística ordinal ou gradient boosting);
#      validação deixando um ano de fora, como acima.
#   2. *Modelo de rendimento municipal* (painel 184 municípios × 50 anos) com chuva, ET0, veranicos e Tmax do POWER,
#      NDVI MODIS e solo: gradient boosting com efeitos fixos do município, ou rede com *embedding* de município.
#      Esse modelo vira o **"simulador de rotação"**: prevê o rendimento de cada cultura sob o clima de cada cenário.
#   3. *Recomendador* que transforma a previsão de quadra em ranking de rotação, sempre mostrando a incerteza
#      (intervalo de previsão) e os anos análogos ("esta quadra se parece com 1998 e 2016").
