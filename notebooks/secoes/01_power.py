# %% [markdown]
# # 1. NASA POWER — agroclimatologia diária (porta de entrada do produto)
#
# **Ficha técnica**
#
# | Item | Valor |
# |---|---|
# | Provedor | NASA Langley Research Center — projeto POWER (Prediction Of Worldwide Energy Resources) |
# | Origem dos dados | meteorologia: reanálise **MERRA-2** (NASA GMAO); radiação: **CERES/FLASHFlux**; chuva alternativa: **IMERG** (GPM) |
# | Variáveis baixadas | T2M, T2M_MAX, T2M_MIN, T2MDEW (°C); RH2M (%); PRECTOTCORR e IMERG_PRECTOT (mm/dia); WS2M (m/s); ALLSKY_SFC_SW_DWN (MJ m⁻² dia⁻¹); EVPTRNS (chega como fluxo de energia em MJ m⁻² dia⁻¹; convertido para mm/dia ÷ 2,45); GWETTOP/GWETROOT/GWETPROF (fração 0–1 de saturação do solo: superfície, zona de raízes, perfil) |
# | Resolução espacial | meteorologia 0,5° × 0,625° (~55 × 69 km no Ceará); radiação 1° reamostrada |
# | Resolução temporal | diária (também horária, mensal e climatologia) |
# | Período | 1981 → hoje (radiação desde 1984; IMERG desde jun/2000) |
# | Latência | ~2–4 dias (no download de 13/11/2026 o último dia válido foi 10/11) |
# | Acesso | API REST aberta, **sem login**; regional: 1 parâmetro por pedido, ≤ 366 dias e ≤ 10° de lado |
# | Licença | dados públicos da NASA; citar NASA POWER Project |
#
# **Ponto de atenção descoberto no download:** `IMERG_PRECTOT` só vem preenchido quando se pede
# `time-standard=UTC`; no horário local (padrão) a API devolve −999 em todos os anos. O dia do IMERG (UTC) fica,
# portanto, deslocado 3 h em relação ao "dia local" das outras variáveis no Ceará.

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
P = DADOS / "power"
ds = xr.open_dataset(P / "power_ce_diario.nc").load()
ds = ds.merge(xr.open_dataset(P / "power_ce_diario_et0.nc").load())
# EVPTRNS chega como fluxo de energia (MJ m-2 dia-1); em lâmina d'água: / 2,45 MJ/kg
ds["EVPTRNS"] = (ds["EVPTRNS"] / 2.45).assign_attrs(units="mm/day")
ind = pd.read_parquet(P / "power_ce_indicadores_anuais.parquet")
glob = pd.read_parquet(P / "power_global_amostra.parquet")
nem = xr.open_dataset(P / "power_ne_mensal.nc").load()
cem = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
uf = nordeste_gdf(); ce_uf = ceara_gdf()
VARS = [v for v in ds.data_vars if "time" in ds[v].dims]
print("Grade Ceará:", dict(ds.sizes), "| variáveis:", VARS)
print("Período:", str(ds.time.values[0])[:10], "→", str(ds.time.values[-1])[:10])

# %% [markdown]
# ## 1.1 Validação de cobertura global
# Amostra de 107 pontos (2020, diário): todos os continentes, desertos, ilhas oceânicas, altas latitudes, Antártida,
# Groenlândia e dois pontos em mar aberto. Para cada parâmetro, medimos a fração de dias com valor válido.

# %%
glob["valido"] = glob["valor"] != -999
val = glob.pivot_table(index=["ponto", "lat", "lon"], columns="param", values="valido", aggfunc="mean").reset_index()
val["faixa_lat"] = pd.cut(val["lat"], [-90, -60, -30, 0, 30, 60, 90])
print("Fração válida média por faixa de latitude:")
print(val.groupby("faixa_lat").mean(numeric_only=True).drop(columns=["lat", "lon"]).round(2).T.to_string())
falhos = val.set_index("ponto").drop(columns=["lat", "lon", "faixa_lat"])
print("\nPontos com algum parâmetro incompleto:")
print(falhos[(falhos < 1).any(axis=1)].round(2).to_string())

# sanidade climática: médias anuais por ponto
clim = glob[glob.valido].pivot_table(index="ponto", columns="param", values="valor", aggfunc="mean")
clim["chuva_anual_mm"] = clim["PRECTOTCORR"] * 366
print("\nSanidade (média 2020): mais secos, mais chuvosos, mais frios e mais quentes")
cols = ["T2M", "chuva_anual_mm", "ALLSKY_SFC_SW_DWN", "RH2M"]
print(pd.concat([clim.nsmallest(4, "chuva_anual_mm")[cols], clim.nlargest(4, "chuva_anual_mm")[cols],
                 clim.nsmallest(3, "T2M")[cols], clim.nlargest(3, "T2M")[cols]]).round(1).to_string())

fig, ax = plt.subplots(figsize=(13, 5.5))
paises_gdf().plot(ax=ax, color="0.9", edgecolor="0.6", lw=0.4)
v = val.copy(); v["n_param_ok"] = (falhos == 1).sum(axis=1).values
sc = ax.scatter(v.lon, v.lat, c=v.n_param_ok, cmap="RdYlGn", vmin=7, vmax=11, s=40, edgecolor="k")
plt.colorbar(sc, label="nº de parâmetros 100% válidos (de 11)")
ax.set_title("NASA POWER — validação global (107 pontos, 2020)"); ax.set_ylim(-90, 90); plt.show()

# %% [markdown]
# **Veredito de cobertura:** a meteorologia (temperatura, umidade, vento, chuva MERRA-2 e radiação) é **global de
# verdade**: 100% dos dias válidos em todos os pontos, da Antártida a Svalbard e em mar aberto. As variáveis do
# modelo de superfície (`EVPTRNS`, `GWETROOT`) faltam sobre mantos de gelo e oceano, o que é o esperado e não afeta
# área agrícola. O `IMERG_PRECTOT` segue a cobertura do IMERG (ver a tabela acima, em UTC). Ou seja, o POWER sozinho
# já garante o "funciona em qualquer fazenda do mundo" para clima, só que a ~50 km.

# %% [markdown]
# ## 1.2 Qualidade no Ceará

# %%
anos = ds.time.dt.year
falta = pd.DataFrame({v: ds[v].isnull().groupby(anos).mean(("time", "lat", "lon")).to_series() for v in VARS})
fig, ax = plt.subplots(figsize=(14, 4.5))
im = ax.imshow(falta.T.values, aspect="auto", cmap="Reds", vmin=0, vmax=1)
ax.set_yticks(range(len(VARS))); ax.set_yticklabels(VARS)
ax.set_xticks(range(0, len(falta), 5)); ax.set_xticklabels(falta.index[::5])
plt.colorbar(im, label="fração ausente"); ax.set_title("Dados ausentes por ano e variável (grade do Ceará)"); plt.show()
ultimo = {v: str(ds[v].dropna("time", how="all").time.values[-1])[:10] for v in VARS}
print("Último dia válido por variável:", ultimo)

faixas = {"T2M": (5, 45), "T2M_MAX": (10, 48), "T2M_MIN": (0, 35), "RH2M": (0, 100), "PRECTOTCORR": (0, 400),
          "WS2M": (0, 25), "ALLSKY_SFC_SW_DWN": (0, 40), "GWETTOP": (0, 1), "GWETROOT": (0, 1), "GWETPROF": (0, 1),
          "EVPTRNS": (0, 15), "ET0": (0, 15)}
fora = {v: float(((ds[v] < a) | (ds[v] > b)).sum()) for v, (a, b) in faixas.items() if v in ds}
print("Valores fora da faixa física:", fora)
print("T2M_MIN > T2M_MAX (inconsistências):", int((ds.T2M_MIN > ds.T2M_MAX).sum()))

# %% [markdown]
# ## 1.3 Estatística descritiva — Ceará (diário, pontos dentro do estado)

# %%
from shapely.geometry import Point
import geopandas as gpd
lo, la = np.meshgrid(ds.lon.values, ds.lat.values)
dentro = gpd.GeoSeries([Point(x, y) for x, y in zip(lo.ravel(), la.ravel())], crs=4326).within(ce_uf.union_all()).values.reshape(lo.shape)
mce = xr.DataArray(dentro, coords={"lat": ds.lat, "lon": ds.lon}, dims=("lat", "lon"))
print("Pontos da grade POWER dentro do Ceará:", int(mce.sum()), "de", mce.size)

def descr(x):
    x = x[np.isfinite(x)]
    return pd.Series({"n": len(x), "média": x.mean(), "desvio": x.std(), "mín": x.min(), "p01": np.percentile(x, 1),
                      "p10": np.percentile(x, 10), "p50": np.percentile(x, 50), "p90": np.percentile(x, 90),
                      "p99": np.percentile(x, 99), "máx": x.max(), "assimetria": stats.skew(x), "curtose": stats.kurtosis(x)})
tab = pd.DataFrame({v: descr(ds[v].where(mce).values.ravel()) for v in VARS}).T
print(tab.round(2).to_string())

fig, axs = plt.subplots(2, 4, figsize=(16, 6.5))
for a, v in zip(axs.ravel(), ["T2M_MAX", "T2M_MIN", "RH2M", "PRECTOTCORR", "ET0", "WS2M", "ALLSKY_SFC_SW_DWN", "GWETROOT"]):
    x = ds[v].where(mce).values.ravel(); x = x[np.isfinite(x)]
    if v == "PRECTOTCORR":
        x = x[x >= 1]; a.set_yscale("log"); a.set_title("PRECTOTCORR (dias ≥ 1 mm)")
    else:
        a.set_title(v)
    a.hist(x, bins=60, color="tab:blue", alpha=0.8)
plt.tight_layout(); plt.show()

# %%
ia = ind[ind.ano.between(1984, 2025)].groupby(["lat", "lon"]).mean(numeric_only=True).to_xarray()
fig, axs = plt.subplots(2, 3, figsize=(16, 9))
for a, (v, cm, t) in zip(axs.ravel(), [("chuva_anual_mm", "YlGnBu", "Chuva anual média (mm)"), ("ET0_anual_mm", "OrRd", "ET0 anual média (mm)"),
                                        ("indice_aridez_P_ET0", "BrBG", "Índice de aridez P/ET0"), ("dias_tmax_gt35", "Reds", "Dias/ano com Tmax > 35 °C"),
                                        ("maior_veranico_fev_mai_d", "YlOrBr", "Maior veranico fev–mai (dias)"), ("GWETROOT_medio", "Greens", "Umidade da zona de raízes (0–1)")]):
    ia[v].plot(ax=a, cmap=cm); ce_uf.boundary.plot(ax=a, color="k", lw=1); a.set_title(t)
plt.tight_layout(); plt.show()
print("Classes de aridez (UNEP) nos pontos do Ceará:",
      pd.cut(ia["indice_aridez_P_ET0"].where(mce).values.ravel(), [0, .05, .2, .5, .65, 10],
             labels=["hiperárido", "árido", "semiárido", "subúmido seco", "úmido"]).value_counts().to_dict())

# %%
# Nordeste (mensal): mapas de chuva e temperatura máxima médias
fig, axs = plt.subplots(1, 3, figsize=(17, 5))
(nem.PRECTOTCORR.groupby("time.year").sum(min_count=12).mean("year") * 30.4).plot(ax=axs[0], cmap="YlGnBu", cbar_kwargs={"label": "mm/ano"})
axs[0].set_title("Nordeste: chuva anual média (MERRA-2)")
nem.T2M_MAX.mean("time").plot(ax=axs[1], cmap="Reds", cbar_kwargs={"label": "°C"}); axs[1].set_title("Tmax média")
nem.GWETROOT.mean("time").plot(ax=axs[2], cmap="Greens", cbar_kwargs={"label": "0–1"}); axs[2].set_title("Umidade da zona de raízes")
for a in axs:
    uf.boundary.plot(ax=a, color="k", lw=0.5); a.set_xlim(BBOX_NE[0], BBOX_NE[2]); a.set_ylim(BBOX_NE[1], BBOX_NE[3])
plt.tight_layout(); plt.show()
print("Unidade de PRECTOTCORR no mensal:", nem.PRECTOTCORR.attrs.get("units", "mm/dia (média do mês)"))

# %% [markdown]
# ## 1.4 Sazonalidade e balanço hídrico

# %%
w = np.cos(np.deg2rad(ds.lat)) * mce
med = ds[["PRECTOTCORR", "ET0", "T2M_MAX", "T2M_MIN", "RH2M", "GWETROOT", "ALLSKY_SFC_SW_DWN", "IMERG_PRECTOT"]].where(mce).weighted(w).mean(("lat", "lon"))
mens = med.resample(time="MS").mean()
clim_m = mens.groupby("time.month").mean().to_dataframe()
dias = pd.Series([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], index=range(1, 13))
clim_m["chuva_mm_mes"] = clim_m["PRECTOTCORR"] * dias
clim_m["ET0_mm_mes"] = clim_m["ET0"] * dias
clim_m["P_menos_ET0"] = clim_m["chuva_mm_mes"] - clim_m["ET0_mm_mes"]
print(clim_m[["chuva_mm_mes", "ET0_mm_mes", "P_menos_ET0", "T2M_MAX", "T2M_MIN", "RH2M", "GWETROOT"]].round(1).T.to_string())
fig, ax = plt.subplots(1, 2, figsize=(15, 4.2))
ax[0].bar(clim_m.index, clim_m.chuva_mm_mes, label="chuva", color="tab:blue")
ax[0].plot(clim_m.index, clim_m.ET0_mm_mes, "r-o", label="ET0 (demanda)")
ax[0].axvspan(1.5, 5.5, color="tab:blue", alpha=0.08); ax[0].set_xticks(range(1, 13)); ax[0].legend()
ax[0].set_title("Ceará: chuva × ET0 (climatologia mensal)")
ax2 = ax[1].twinx()
ax[1].plot(clim_m.index, clim_m.T2M_MAX, "r-", label="Tmax"); ax[1].plot(clim_m.index, clim_m.T2M_MIN, "b-", label="Tmin")
ax2.plot(clim_m.index, clim_m.GWETROOT, "g--", label="GWETROOT"); ax[1].legend(loc="upper left"); ax2.legend(loc="upper right")
ax[1].set_xticks(range(1, 13)); ax[1].set_title("Temperaturas e umidade do solo (MERRA-2)")
plt.tight_layout(); plt.show()
meses_def = clim_m.index[clim_m.P_menos_ET0 < 0].tolist()
print("Meses com chuva < ET0 (déficit climático):", meses_def, "→", len(meses_def), "de 12")

# %%
ic = ind[ind.no_ceara].groupby("ano").mean(numeric_only=True)
fig, ax = plt.subplots(1, 2, figsize=(14, 4))
for v, c in [("inicio_chuvas_doy", "tab:green"), ("fim_chuvas_doy", "tab:brown")]:
    ax[0].plot(ic.index, ic[v], "-o", color=c, label=v)
ax[0].set_ylabel("dia do ano"); ax[0].legend(); ax[0].set_title("Início e fim da estação chuvosa (média dos pontos do CE)")
ax[1].scatter(ic.inicio_chuvas_doy, ic.chuva_fev_mai_mm); ax[1].set_xlabel("início (dia do ano)"); ax[1].set_ylabel("chuva fev–mai (mm)")
r = stats.spearmanr(ic.inicio_chuvas_doy, ic.chuva_fev_mai_mm, nan_policy="omit")
ax[1].set_title(f"Início tardio → quadra mais seca? Spearman ρ={r.correlation:.2f} (p={r.pvalue:.3f})")
plt.tight_layout(); plt.show()
print(ic[["inicio_chuvas_doy", "fim_chuvas_doy"]].describe().round(1).T.to_string())

# %% [markdown]
# ## 1.5 Tendências 1984–2025 (Mann-Kendall + Sen)

# %%
cols = ["chuva_anual_mm", "chuva_fev_mai_mm", "ET0_anual_mm", "indice_aridez_P_ET0", "dias_tmax_gt35", "dias_tmax_gt38",
        "dias_chuva_gt50", "maior_veranico_fev_mai_d", "n_veranicos_10d_fev_mai", "inicio_chuvas_doy", "fim_chuvas_doy", "GWETROOT_medio"]
anual_t = med[["T2M_MAX", "T2M_MIN"]].groupby("time.year").mean().to_dataframe()
icx = ic.loc[1984:2025, cols].join(anual_t.loc[1984:2025])
res = []
for c in icx.columns:
    x = icx[c].dropna()
    r = mk.original_test(x.values)
    res.append((c, r.trend, round(r.p, 4), r.slope, r.slope * 10))
print(pd.DataFrame(res, columns=["indicador", "tendência", "p", "Sen/ano", "Sen/década"]).round(3).to_string(index=False))

# por pixel: Tmax e chuva anual
fig, axs = plt.subplots(1, 2, figsize=(13, 5))
for a, v, cm, un in [(axs[0], "T2M_MAX", "Reds", "°C/década"), (axs[1], "PRECTOTCORR", "BrBG", "mm/ano por década")]:
    agg = ds[v].sel(time=slice("1984", "2025")).groupby("time.year")
    arr = (agg.mean() if v == "T2M_MAX" else agg.sum(min_count=360))
    sl = np.full(mce.shape, np.nan); pv = sl.copy()
    for i in range(mce.shape[0]):
        for j in range(mce.shape[1]):
            y = arr[:, i, j].values; y = y[np.isfinite(y)]
            if len(y) > 20:
                rr = mk.original_test(y); sl[i, j] = rr.slope * 10; pv[i, j] = rr.p
    im = a.pcolormesh(ds.lon, ds.lat, sl, cmap=cm if v == "PRECTOTCORR" else "Reds", shading="auto")
    a.contourf(ds.lon, ds.lat, (pv < 0.05).astype(float), levels=[0.5, 1.5], hatches=["..."], colors="none")
    ce_uf.boundary.plot(ax=a, color="k"); plt.colorbar(im, ax=a, label=un); a.set_title(f"Tendência {v} (pontilhado p<0,05)")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 1.6 Variabilidade interanual, seca de 2012–2017 e extremos

# %%
ch = ic.loc[1984:2025, "chuva_anual_mm"]
anom = (ch - ch.mean()) / ch.std()
fig, ax = plt.subplots(figsize=(14, 4))
ax.bar(anom.index, anom, color=np.where(anom < 0, "tab:red", "tab:blue"))
ax.axvspan(2011.5, 2017.5, color="orange", alpha=0.15); ax.set_title("Ceará: anomalia padronizada da chuva anual (MERRA-2 corrigido)")
plt.show()
print("Anos mais secos:", anom.nsmallest(6).round(2).to_dict())
print("Anos mais chuvosos:", anom.nlargest(6).round(2).to_dict())
print("Seca 2012–2017: chuva média", round(ch.loc[2012:2017].mean()), "mm vs climatologia", round(ch.mean()), "mm",
      f"({100 * (ch.loc[2012:2017].mean() / ch.mean() - 1):.0f}%)")

pr = ds.PRECTOTCORR.where(mce).values
pr = pr[np.isfinite(pr)]
umidos = pr[pr >= 1]
print("\nPercentis de chuva em dias úmidos (≥1 mm):", {p: round(float(np.percentile(umidos, p)), 1) for p in (50, 90, 95, 99, 99.9)})
tx = ds.T2M_MAX.where(mce).values; tx = tx[np.isfinite(tx)]
print("Percentis de Tmax:", {p: round(float(np.percentile(tx, p)), 1) for p in (50, 90, 95, 99)})
print("Fração de dias com Tmax > 35 °C (limiar de estresse térmico para milho/feijão na floração):", round(float((tx > 35).mean()), 3))

# %% [markdown]
# ## 1.7 Duas chuvas no mesmo produto: MERRA-2 corrigido × IMERG
# O POWER entrega duas estimativas de chuva. Se elas divergem, o app precisa escolher e explicar a incerteza.

# %%
mm = med[["PRECTOTCORR", "IMERG_PRECTOT"]].resample(time="MS").mean().to_dataframe().dropna()
if len(mm) > 24:
    r = np.corrcoef(mm.PRECTOTCORR, mm.IMERG_PRECTOT)[0, 1]
    vies = 100 * (mm.PRECTOTCORR.mean() / mm.IMERG_PRECTOT.mean() - 1)
    print(f"Meses comparados: {len(mm)} | correlação mensal r={r:.3f} | viés MERRA-2 vs IMERG: {vies:+.1f}%")
    d = ds[["PRECTOTCORR", "IMERG_PRECTOT"]].where(mce).weighted(w).mean(("lat", "lon")).to_dataframe().dropna()
    print("Diário: r =", round(np.corrcoef(d.PRECTOTCORR, d.IMERG_PRECTOT)[0, 1], 3),
          "| dias ≥ 1 mm MERRA-2:", round((d.PRECTOTCORR >= 1).mean(), 3), "IMERG:", round((d.IMERG_PRECTOT >= 1).mean(), 3))
    fig, ax = plt.subplots(1, 2, figsize=(13, 4))
    ax[0].scatter(mm.IMERG_PRECTOT * 30.4, mm.PRECTOTCORR * 30.4, s=8); ax[0].plot([0, 400], [0, 400], "k--")
    ax[0].set_xlabel("IMERG (mm/mês)"); ax[0].set_ylabel("MERRA-2 corrigido (mm/mês)"); ax[0].set_title("Chuva mensal no Ceará")
    c2 = mm.groupby(mm.index.month).mean() * 30.4
    c2.plot(ax=ax[1], marker="o"); ax[1].set_title("Climatologia mensal das duas fontes"); plt.tight_layout(); plt.show()
else:
    print("IMERG_PRECTOT sem dados suficientes nesta grade.")

# %% [markdown]
# ## 1.8 Insights e uso no produto
#
# - **Cobertura global comprovada**: a meteorologia do POWER foi 100% válida em 107 pontos de todos os continentes.
#   É a camada que garante que o app funcione em qualquer fazenda. Só que é **regional (~50 km)**: sem microclima,
#   sem efeito de serra (Ibiapaba/Araripe ficam suavizadas). O SRTM entra para corrigir isso.
# - **Balanço hídrico climático**: a ET0 calculada por FAO-56 (~6 mm/dia no interior, 5,2 em Fortaleza) supera a
#   chuva em **10 de 12 meses**; só março e abril têm excedente (~+55 mm/mês). A estação útil vai, em média, do dia
#   26 (fim de janeiro) ao dia 184 (início de julho). Isso define a **janela de plantio de sequeiro** e quanto falta
#   para irrigar; é o núcleo do motor de rotação (a cultura cabe na janela? quanto de água ela pede?). 32 dos 38
#   pontos do estado são **semiáridos** (P/ET0 entre 0,2 e 0,5) e 6 são subúmidos secos (litoral e serras).
# - **O sinal de mudança climática está na temperatura, não na chuva**: Tmax +0,37 °C/década e Tmin +0,24 °C/década
#   (p ≤ 0,01); dias acima de 35 °C crescem **+10 por década** e acima de 38 °C, +5 por década. A chuva anual não tem
#   tendência significativa (p = 0,15). Resultado: a mesma chuva com mais calor e mais ET, ou seja, mais estresse.
#   Rotações com culturas tolerantes ao calor na floração (sorgo, caupi, gergelim) ganham peso ao longo do tempo.
# - **Seca 2012–2017** = −31% de chuva (584 mm/ano contra 849 mm da climatologia). Os anos mais secos (1993, 2012,
#   1998) são anos de El Niño e/ou de dipolo positivo, ligação explorada na seção 13.
# - **Indicadores de risco prontos** para o calendário do app: dias com Tmax > 35 °C (estresse na floração; 35% dos
#   dias no Ceará), veranicos na quadra chuvosa, chuvas > 50 mm (erosão), início e fim das chuvas (data de plantio).
# - **Duas chuvas, quase a mesma resposta no mensal**: `PRECTOTCORR` (MERRA-2 corrigido) e `IMERG_PRECTOT` têm
#   r = 0,97 no mensal e viés de −0,3%, mas r = 0,83 no diário e o IMERG tem menos dias de chuva (34% × 40%). Para
#   balanço mensal tanto faz; para veranicos e dias de plantio, a escolha da fonte muda o resultado e o app deve
#   mostrar a faixa entre as duas.
# - **Ideias de ML/DL**:
#   1. *Previsão sazonal da quadra chuvosa* (fev–mai) com ENSO/dipolo (seção 13) + chuva de dezembro e janeiro
#      (gradient boosting ou regressão quantílica) → probabilidade de quadra seca, normal ou chuvosa para escolher a
#      rotação.
#   2. *Detecção do início das chuvas* em tempo real (classificador sobre janelas de 30 dias) para dizer "pode plantar".
#   3. *Gerador de cenários* (bootstrap por blocos de anos ou GAN/difusão sobre séries diárias) para os controles de
#      cenário do app (+2 °C, −20% de chuva).
#   4. *Emulador de produtividade*: modelos de cultura (DSSAT/APSIM aceitam o POWER como entrada) → rede neural
#      substituta para avaliar milhares de rotações em segundos.
