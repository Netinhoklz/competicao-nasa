# %% [markdown]
# # 6. GRACE / GRACE-FO — armazenamento total de água (TWS)
#
# **Ficha técnica**
#
# | Item | Valor |
# |---|---|
# | Provedor | NASA/DLR (GRACE, 2002–2017) e NASA/GFZ (GRACE-FO, 2018–); solução de *mascons* do CSR/Universidade do Texas (RL06.3) |
# | Variável | `lwe_thickness`: anomalia do armazenamento total de água (solo + subsolo + aquífero + superfície + neve), em **cm de água equivalente**, relativa à média 2004–2009 |
# | Resolução espacial | grade de 0,25° (amostragem); mascons de ~1° (~120 km); **resolução efetiva ~300 km** |
# | Resolução temporal | mensal |
# | Período | abr/2002 → set/2026 (261 meses), com a lacuna GRACE→GRACE-FO (jul/2017–mai/2018) |
# | Latência | ~2–3 meses |
# | Acesso | aberto, sem login (download.csr.utexas.edu); a versão JPL fica no PO.DAAC e exige Earthdata |
# | Licença / citação | dados abertos; citar Save, Bettadpur & Tapley (2016), DOI 10.15781/cgq9-nh24 |
#
# Para que serve no produto: é o único dado que "enxerga" **água subterrânea/aquífero**. Mostra se a região está
# esgotando ou recarregando água ano a ano. Não serve para um talhão: é um sinal **regional**.

# %%
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymannkendall as mk
import xarray as xr
from scipy import stats

warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams.update({"figure.dpi": 90, "axes.grid": True, "grid.alpha": 0.3})
G = DADOS / "grace"
resumo = xr.open_dataset(G / "grace_global_resumo.nc")
cob = pd.read_parquet(G / "grace_cobertura_mensal.parquet")
ne = xr.open_dataset(G / "grace_ne_mensal.nc")["lwe_thickness"]
ce = pd.read_parquet(DERIV / "grace_ce_mensal.parquet").set_index("data")["valor"]
nem = pd.read_parquet(DERIV / "grace_ne_mensal.parquet").set_index("data")["valor"]
aoi = pd.read_parquet(DERIV / "grace_aoi_mensal.parquet")
uru = aoi[aoi.aoi == "oeste_bahia_urucuia"].set_index("data")["valor"]
print("NE:", dict(ne.sizes), "| Ceará:", ce.index.min().date(), "->", ce.index.max().date(), len(ce), "meses")

# %% [markdown]
# ## 6.1 Validação de cobertura global
# Testes: (a) fração de células com valor em cada mês, separando terra e oceano; (b) extensão em latitude;
# (c) mapa global de tendência e de amplitude sazonal; (d) meses faltantes na série.

# %%
print("Latitude:", float(resumo.lat.min()), "a", float(resumo.lat.max()), "| Longitude:", float(resumo.lon.min()), "a", float(resumo.lon.max()))
print("Fração de meses válidos por pixel (mín/médio):", float(resumo.fracao_meses_validos.min()), float(resumo.fracao_meses_validos.mean()))
print("Fração de pixels com valor por mês — terra: mín", cob.frac_terra.min(), "| oceano: mín", cob.frac_oceano.min())
faixas = pd.cut(resumo.lat.values, [-90, -60, -30, 0, 30, 60, 90])
terra = resumo.terra.values > 0.5
tab = []
for f in faixas.categories:
    sel = (faixas == f)
    m = resumo.tendencia_cm_ano.values[sel][terra[sel]]
    tab.append((str(f), int(terra[sel].sum()), float(np.isfinite(m).mean()), float(np.nanmean(np.abs(m)))))
print(pd.DataFrame(tab, columns=["faixa_lat", "celulas_terra", "frac_com_valor", "|tendência| média cm/ano"]).to_string(index=False))

fig, ax = plt.subplots(1, 2, figsize=(15, 4.2))
r = resumo.tendencia_cm_ano.where(resumo.terra > 0.5)
r.plot(ax=ax[0], cmap="RdBu", vmin=-3, vmax=3, cbar_kwargs={"label": "cm/ano"})
ax[0].set_title("Tendência TWS 2002–2026 (terra) — global")
resumo.amplitude_sazonal_cm.where(resumo.terra > 0.5).plot(ax=ax[1], cmap="viridis", vmax=30, cbar_kwargs={"label": "cm"})
ax[1].set_title("Amplitude do ciclo anual (terra)")
for a in ax:
    a.plot([-41.4, -37.25, -37.25, -41.4, -41.4], [-7.85, -7.85, -2.78, -2.78, -7.85], "k-", lw=1.5)
plt.tight_layout(); plt.show()

# %%
todos = pd.period_range("2002-04", "2026-09", freq="M")
presentes = pd.PeriodIndex(pd.to_datetime(ne.time.values).to_period("M"))
faltam = todos.difference(presentes)
print(f"Meses esperados {len(todos)} | presentes (únicos) {presentes.nunique()} | faltantes {len(faltam)}")
grupos = pd.Series(faltam.to_timestamp()).diff().dt.days.gt(40).cumsum()
for _, g in pd.Series(faltam.astype(str)).groupby(grupos.values):
    print("  lacuna:", g.iloc[0], "→", g.iloc[-1], f"({len(g)} meses)")

# %% [markdown]
# **Veredito de cobertura:** é **global de verdade**, inclusive oceanos e polos (de −89,9° a +89,9°), com 100% das
# células preenchidas em todos os meses. O que limita não é a cobertura, é a **resolução**: ~300 km efetivos. O
# Ceará inteiro equivale a poucos "pixels independentes". Há ~35 meses faltantes, a maioria na lacuna de 11 meses
# entre as missões (2017–2018) e em falhas pontuais de bateria do GRACE (2011–2017).

# %% [markdown]
# ## 6.2 Qualidade da série regional

# %%
def resumo_estat(s, nome):
    s = s.dropna()
    return pd.Series({"n": len(s), "média": s.mean(), "desvio": s.std(), "mín": s.min(), "p05": s.quantile(.05),
                      "p25": s.quantile(.25), "mediana": s.median(), "p75": s.quantile(.75), "p95": s.quantile(.95),
                      "máx": s.max(), "assimetria": stats.skew(s), "curtose": stats.kurtosis(s)}, name=nome)

tabela = pd.concat([resumo_estat(ce, "Ceará"), resumo_estat(nem, "Nordeste"), resumo_estat(uru, "Oeste BA/Urucuia")]
                   + [resumo_estat(aoi[aoi.aoi == a].set_index("data")["valor"], a) for a in AOIS], axis=1).T
print(tabela.round(2).to_string())
z = (ce - ce.mean()) / ce.std()
print("\nOutliers |z|>2,5 no Ceará:", z[abs(z) > 2.5].round(2).to_dict())
print("Duplicatas de mês no arquivo original:", int(presentes.duplicated().sum()), "(meses com duas soluções; foram promediadas)")

# %% [markdown]
# ## 6.3 Distribuição e mapas no Nordeste

# %%
fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
for s, n in [(ce, "Ceará"), (nem, "Nordeste"), (uru, "Oeste BA")]:
    ax[0].hist(s.dropna(), bins=30, alpha=0.5, label=n)
ax[0].set_title("Histograma da anomalia TWS (cm)"); ax[0].legend()
ne.mean("time").plot(ax=ax[1], cmap="BrBG", center=0, cbar_kwargs={"label": "cm"})
ax[1].set_title("Média 2002–2026 (rel. 2004–09)")
ne.std("time").plot(ax=ax[2], cmap="magma", cbar_kwargs={"label": "cm"})
ax[2].set_title("Desvio padrão mensal")
uf = nordeste_gdf()
for a in ax[1:]:
    uf.boundary.plot(ax=a, color="k", lw=0.5)
    a.set_xlim(BBOX_NE[0], BBOX_NE[2]); a.set_ylim(BBOX_NE[1], BBOX_NE[3])
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6.4 Sazonalidade (climatologia mensal)
# No Ceará a chuva cai em fevereiro–maio. O armazenamento total responde com atraso: o pico de água vem no fim
# da quadra chuvosa e o mínimo no fim da estação seca (nov–dez).

# %%
clim = pd.DataFrame({"Ceará": ce.groupby(ce.index.month).mean(), "Nordeste": nem.groupby(nem.index.month).mean(),
                     "Oeste BA": uru.groupby(uru.index.month).mean()})
print(clim.round(1).T.to_string())
ax = clim.plot(marker="o", figsize=(9, 3.8)); ax.axvspan(2, 5, color="tab:blue", alpha=0.08, label="quadra chuvosa CE")
ax.set_xticks(range(1, 13)); ax.set_ylabel("cm"); ax.set_title("Climatologia mensal da anomalia TWS"); ax.legend(); plt.show()
print("Mês de pico no Ceará:", int(clim["Ceará"].idxmax()), "| mês de mínimo:", int(clim["Ceará"].idxmin()),
      "| amplitude:", round(clim["Ceará"].max() - clim["Ceará"].min(), 1), "cm")

# %% [markdown]
# ## 6.5 Tendências (Mann-Kendall com correção de autocorrelação + inclinação de Sen)

# %%
def dessaz(s):
    return s - s.groupby(s.index.month).transform("mean")

linhas = []
for nome, s in [("Ceará", ce), ("Nordeste", nem), ("Oeste BA/Urucuia", uru)] + [(a, aoi[aoi.aoi == a].set_index("data")["valor"]) for a in AOIS]:
    d = dessaz(s).dropna()
    r1 = mk.hamed_rao_modification_test(d.values)
    anual = s.resample("YE").mean().dropna()
    r2 = mk.original_test(anual.values)
    linhas.append((nome, r1.trend, r1.p, r1.slope * 12, r2.trend, r2.p, r2.slope))
print(pd.DataFrame(linhas, columns=["região", "MK mensal (Hamed-Rao)", "p", "Sen cm/ano", "MK anual", "p anual", "Sen anual cm/ano"]).round(3).to_string(index=False))

# tendência por pixel no NE (médias anuais, 2003-2025 completos)
anual = ne.groupby("time.year").mean().sel(year=slice(2003, 2025))
sl = np.full((ne.sizes["lat"], ne.sizes["lon"]), np.nan); pv = sl.copy()
for i in range(ne.sizes["lat"]):
    for j in range(ne.sizes["lon"]):
        v = anual[:, i, j].values
        if np.isfinite(v).sum() > 15:
            r = mk.original_test(v[np.isfinite(v)]); sl[i, j], pv[i, j] = r.slope, r.p
fig, ax = plt.subplots(figsize=(7.5, 6))
im = ax.pcolormesh(ne.lon, ne.lat, sl, cmap="RdBu", vmin=-1.5, vmax=1.5, shading="auto")
ax.contourf(ne.lon, ne.lat, (pv < 0.05).astype(float), levels=[0.5, 1.5], hatches=["..."], colors="none")
uf.boundary.plot(ax=ax, color="k", lw=0.6); plt.colorbar(im, label="Sen (cm/ano)")
ax.set_xlim(BBOX_NE[0], BBOX_NE[2]); ax.set_ylim(BBOX_NE[1], BBOX_NE[3])
ax.set_title("Tendência TWS 2003–2025 por pixel (pontilhado: p<0,05)"); plt.show()

# %% [markdown]
# ## 6.6 Variabilidade interanual e a seca de 2012–2017

# %%
an = pd.DataFrame({"Ceará": ce.resample("YE").mean(), "Nordeste": nem.resample("YE").mean(), "Oeste BA": uru.resample("YE").mean()})
an.index = an.index.year
fig, ax = plt.subplots(2, 1, figsize=(13, 7))
an.plot.bar(ax=ax[0], width=0.85); ax[0].axvspan(9.5, 15.5, color="orange", alpha=0.15)
ax[0].set_title("Média anual da anomalia TWS (faixa laranja = seca 2012–2017)"); ax[0].set_ylabel("cm")
d = dessaz(ce)
ax[1].fill_between(d.index, d, 0, where=d < 0, color="tab:red", alpha=0.6)
ax[1].fill_between(d.index, d, 0, where=d >= 0, color="tab:blue", alpha=0.6)
ax[1].set_title("Ceará: anomalia dessazonalizada"); plt.tight_layout(); plt.show()

# classificação por percentis (estilo monitor de seca com GRACE)
pct = d.rank(pct=True)
classe = pd.cut(pct, [0, .02, .05, .10, .20, .30, 1.0], labels=["D4 excepcional", "D3 extrema", "D2 severa", "D1 moderada", "D0 anormal", "normal/úmido"])
print("Meses por classe de seca (Ceará, dessazonalizado):\n", classe.value_counts().sort_index().to_string())
print("\nMínimo da série:", d.idxmin().date(), round(d.min(), 1), "cm")
seca = d["2012":"2017"]
print("Seca 2012–2017: média", round(seca.mean(), 1), "cm | meses abaixo de 0:", int((seca < 0).sum()), "de", len(seca))
print("Déficit acumulado (soma das anomalias negativas, cm·mês):", round(seca[seca < 0].sum(), 0))

# %%
# Relação com a chuva do POWER (se o derivado existir): correlação com defasagem
p = DERIV / "power_ce_mensal.parquet"
if p.exists():
    pw = pd.read_parquet(p)
    chuva = pw[pw.variavel == "PRECTOTCORR"].set_index("data")["valor"]
    chuva_anom = dessaz(chuva)
    acum = chuva_anom.rolling(12).sum()
    base = dessaz(ce).dropna()
    res = []
    for lag in range(0, 13):
        x = acum.shift(lag).reindex(base.index)
        ok = x.notna()
        res.append((lag, np.corrcoef(base[ok], x[ok])[0, 1]))
    res = pd.DataFrame(res, columns=["defasagem_meses", "r"])
    print("Correlação TWS × chuva acumulada 12 meses (anomalias):\n", res.round(2).to_string(index=False))
else:
    print("Derivado do POWER ainda não existe; correlação será feita na seção de relações.")

# %% [markdown]
# ## 6.7 Insights e uso no produto
#
# - **Global de verdade, mas regional**: serve a qualquer fazenda do mundo como "termômetro" da água da bacia ou do
#   aquífero, nunca como dado do talhão. No app, entra como um **semáforo regional de água** ("a água da sua região
#   está X cm abaixo do normal; tendência de Y cm/ano").
# - **A seca 2012–2017 aparece com clareza** no Ceará: 45 de 50 meses abaixo do normal, mínimo de −24,6 cm em
#   jul/2016 e −17 cm na média anual de 2016. A recuperação só se completa em 2022–2024. Isso mostra a **memória longa**
#   do sistema: um ano de chuva boa não repõe o aquífero. O motor de rotação deve penalizar culturas de alta demanda
#   hídrica (irrigadas) quando o TWS está em déficit persistente.
# - **Ceará e Nordeste não têm tendência de longo prazo** (Mann-Kendall com correção de autocorrelação, p ≈ 0,7–0,8):
#   o sinal é dominado por ciclos de seca e recuperação, não por esgotamento contínuo.
# - **Oeste da Bahia (Urucuia) perde água de forma significativa**: −1,4 a −1,7 cm/ano (p < 0,001) e anomalia média de
#   −15 cm, coerente com a expansão da irrigação por pivô. É o caso de "rotação que economiza água" para a
#   apresentação e um contraponto ao Ceará.
# - **Validade científica**: as AOIs do Ceará (11 km) caem dentro de um ou dois mascons, então os valores por AOI são
#   quase iguais ao regional. Isso precisa ser dito no app, para não sugerir uma precisão que o dado não tem.
# - **Sazonalidade com atraso**: o TWS do Ceará chega ao pico em maio (fim da quadra) e ao mínimo em dezembro, com
#   amplitude de ~20 cm. Isso permite uma regra simples de "água guardada" para decidir a safrinha ou a cultura de
#   segunda época.
# - **Ligação com a chuva do POWER**: a anomalia de TWS correlaciona com a chuva acumulada de 12 meses (r ≈ 0,47 com
#   1 mês de defasagem) e a correlação decai devagar (r ≈ 0,3 com 12 meses), outra evidência da memória plurianual.
# - **Ideias de ML**:
#   1. *downscaling* do GRACE (300 km → 5–10 km) com floresta aleatória ou gradient boosting, usando chuva (IMERG/POWER),
#      ET (MODIS/ECOSTRESS), NDVI e relevo (SRTM) como preditores; é técnica publicada para aquíferos.
#   2. Preencher a lacuna 2017–2018 com um modelo de séries (LSTM/SARIMAX) dirigido pela chuva.
#   3. Previsão de TWS 3–6 meses à frente a partir de ENSO/dipolo do Atlântico (seção 13) e da chuva acumulada,
#      para alertas de risco hídrico na rotação.
