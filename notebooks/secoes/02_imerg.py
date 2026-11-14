# %% [markdown]
# # 2. GPM IMERG — precipitação por satélite (NASA/JAXA)
#
# **Ficha técnica**
#
# | Item | Valor |
# |---|---|
# | Missão / produto | GPM (Global Precipitation Measurement), algoritmo IMERG — fusão de micro-ondas passivas de ~10 satélites + infravermelho geoestacionário, calibrada pelo radar DPR e por pluviômetros (GPCC) na versão Final |
# | Variável | precipitação total (mm/dia; mm/h na meia-hora) |
# | Resolução | 0,1° (~11 km no Ceará); meia-hora (nativo) e diário (agregado) |
# | Período baixado | **diário V07: 01/01/1998 a 14/09/2026** (inclui a era TRMM; o POWER tem ~2 meses de latência); **meia-hora V06: amostra de 12 dias, 10–21/03/2009** (auge da quadra de um ano muito chuvoso) |
# | Rotas usadas (sem login) | diário: NASA POWER `IMERG_PRECTOT` com `time-standard=UTC` (o POWER entrega o IMERG na grade nativa 0,1°); meia-hora: Microsoft Planetary Computer `gpm-imerg-hhr` (Zarr V06, 2000-06 a 2021-05) |
# | Rota oficial | GES DISC (GPM_3IMERGDF/DL/DE V07) — exige Earthdata Login; Final V07 só até set/2025, Early/Late até ontem |
# | Recorte | Ceará (−41,5 a −37,0 lon; −8,0 a −2,5 lat; 45×55 pixels) e Nordeste (−48,8 a −34,7; −18,4 a −1,0; 141×174 pixels) |
#
# **Por que o meia-hora é só uma amostra:** no Planetary Computer cada bloco Zarr tem 12 meias-horas do
# **globo inteiro** (~52 MB comprimidos). Para recortar o Ceará é preciso baixar o planeta: o registro completo
# daria ~1,6 TB. Com a conexão medida (5–6 MB/s) isso é inviável; ficamos com uma amostra para ciclo diurno,
# intensidade de 30 min (erosividade) e validação global.

# %%
import sys, warnings
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import shapely
import pymannkendall as mk
from scipy import stats

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
plt.rcParams.update({"figure.dpi": 90, "axes.grid": True, "grid.alpha": 0.3})
DIR = DADOS / "imerg"
ce_gdf, ne_gdf, terra = ceara_gdf(), nordeste_gdf(), terra_gdf()
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def mascara(geom, lon, lat):
    lo, la = np.meshgrid(lon, lat)
    return shapely.contains_xy(geom, lo, la)


def mapa(ax, da, titulo, cmap="viridis", gdf=None, **kw):
    m = ax.pcolormesh(da.lon, da.lat, da, cmap=cmap, shading="auto", **kw)
    (gdf if gdf is not None else ce_gdf).boundary.plot(ax=ax, color="k", lw=0.6)
    ax.set_title(titulo, fontsize=10)
    ax.set_aspect("equal")
    plt.colorbar(m, ax=ax, shrink=0.8)
    return m


ce = xr.open_mfdataset(sorted(DIR.glob("imerg_ce_diario_*.nc")), combine="by_coords")["precip"].load()
M_CE = xr.DataArray(mascara(ce_gdf.geometry.union_all(), ce.lon.values, ce.lat.values), dims=("lat", "lon"))
ce_m = ce.where(M_CE)
serie_ce = ce_m.mean(("lat", "lon")).to_series()  # media diaria na area do Ceara
print("Ceará diário:", ce.sizes, "| período", str(ce.time.values[0])[:10], "→", str(ce.time.values[-1])[:10])
print("pixels dentro do Ceará:", int(M_CE.sum()), "de", M_CE.size)

# %% [markdown]
# ## 2.1 Validação de cobertura global
# Duas evidências independentes:
# 1. **POWER/IMERG V07:** grade regular de 216 pontos (18 latitudes de 85°S a 85°N × 12 longitudes, terra e oceano), 10 dias de mar/2019.
# 2. **Planetary Computer/IMERG V06:** cada bloco baixado é o campo global completo; guardamos o total diário em 0,5° e o número de meias-horas válidas por célula.

# %%
val = pd.read_csv(DIR / "validacao_global_power_imerg.csv")
print("POWER/IMERG V07 — pontos com 10/10 dias válidos:", f"{(val.n_validos == val.n_dias).mean():.0%}",
      "| latitudes testadas:", val.lat.min(), "a", val.lat.max())
pc_arqs = sorted((DIR / "pc_nativo").glob("imerg_v06_*.nc"))
print("dias da amostra nativa V06:", len(pc_arqs))
if pc_arqs:
    g = xr.open_mfdataset(pc_arqs, combine="nested", concat_dim="dia")[["global_dia_05", "global_nvalidos_05"]].load()
    frac_lat = (g.global_nvalidos_05 / 48).mean(("dia", "lon05"))
    fig, ax = plt.subplots(1, 2, figsize=(14, 4), gridspec_kw={"width_ratios": [2.3, 1]})
    m = ax[0].pcolormesh(g.lon05, g.lat05, g.global_dia_05.mean("dia").T, cmap="Blues", vmax=20, shading="auto")
    terra.boundary.plot(ax=ax[0], color="k", lw=0.3)
    ax[0].set_title(f"IMERG V06 — chuva média diária global, {len(pc_arqs)} dia(s) de mar/2009 (mm/dia)")
    plt.colorbar(m, ax=ax[0], shrink=0.8)
    ax[1].plot(frac_lat, g.lat05)
    ax[1].scatter(val.groupby("lat").n_validos.mean() / 10, val.groupby("lat").n_validos.mean().index, c="r", s=12,
                  label="POWER V07 (pontos)")
    ax[1].set_xlabel("fração de dados válidos")
    ax[1].set_ylabel("latitude")
    ax[1].set_title("Cobertura por latitude")
    ax[1].legend()
    plt.tight_layout()
    plt.show()
    print("V06 — fração válida entre 60°S e 60°N:", float(frac_lat.sel(lat05=slice(-60, 60)).mean().round(3)),
          "| acima de 60°:", float(frac_lat.where(abs(frac_lat.lat05) > 60).mean().round(3)))

# %% [markdown]
# **Veredito de cobertura.** O IMERG é **global de fato** para o uso agrícola. A V07 (via POWER) tem valores
# em todas as latitudes testadas, de 85°S a 85°N, terra e oceano. Na V06, a fração válida cai acima de ~60°,
# onde só há micro-ondas esparsas e neve/gelo; isso não afeta nenhuma região agrícola relevante.
# Toda a faixa 60°S–60°N, onde está praticamente toda a agricultura do planeta, tem cobertura completa a 0,1° e
# 30 min. **Pode ser a camada de chuva do produto mundial.**

# %% [markdown]
# ## 2.2 Qualidade: ausentes, buracos, faixas e outliers

# %%
dias_esperados = pd.date_range(ce.time.values[0], ce.time.values[-1], freq="D")
nan_frac = float(ce_m.isnull().where(M_CE).mean())
print(f"dias esperados {len(dias_esperados)} | dias presentes {ce.sizes['time']} | buracos {len(dias_esperados) - ce.sizes['time']}")
print(f"fração de ausentes (pixels do Ceará): {nan_frac:.4%}")
print("dias com algum pixel ausente:", int(ce_m.isnull().where(M_CE, False).any(("lat", "lon")).sum()))
v = ce_m.values[np.isfinite(ce_m.values)]
print(f"mín {v.min():.2f} | máx {v.max():.1f} mm/dia | negativos: {(v < 0).sum()}")
print("percentis dos dias de chuva (≥1 mm):", np.percentile(v[v >= 1], [50, 90, 95, 99, 99.9]).round(1))
top = ce_m.where(ce_m > 150, drop=True)
print("pixel-dias > 150 mm:", int(np.isfinite(top.values).sum()), "| > 250 mm:", int((ce_m > 250).sum()))
idx = np.unravel_index(np.nanargmax(ce_m.values), ce_m.shape)
print("máximo absoluto:", float(ce_m.values[idx]), "mm em", str(ce.time.values[idx[0]])[:10],
      "lat", float(ce.lat[idx[1]]), "lon", float(ce.lon[idx[2]]))
# outliers espaciais: pixel muito acima dos vizinhos no mesmo dia (robustez)
viz = ce.rolling(lat=3, lon=3, center=True).median()
iso = ((ce > 100) & (ce > 5 * (viz + 1))).where(M_CE, False)
print("pixel-dias isolados (>100 mm e >5x a mediana 3x3):", int(iso.sum()), "— candidatos a artefato a revisar")

# %% [markdown]
# ### 2.2b Viés no litoral leste do Nordeste (chuva "quente")
# Total anual médio do IMERG em pixels de capitais contra as normais climatológicas aproximadas (INMET 1991–2020,
# valores de referência arredondados, a conferir com a tabela oficial). Satélites de micro-ondas e infravermelho
# enxergam mal a chuva de nuvens rasas e quentes trazida pelos alísios e pelos distúrbios de leste na costa
# oriental. A calibração mensal do GPCC, em 1°, não resolve o gradiente costeiro.

# %%
ne_all = xr.open_mfdataset(sorted(DIR.glob("imerg_ne_diario_*.nc")), combine="by_coords")["precip"].sel(time=slice("1998", "2025"))
pts = {"Recife": (-34.95, -8.05, 2400), "Maceió": (-35.75, -9.65, 2100), "Aracaju": (-37.05, -10.95, 1600),
       "João Pessoa": (-34.85, -7.15, 2000), "Salvador": (-38.50, -12.95, 2100), "Natal": (-35.20, -5.80, 1700),
       "Fortaleza": (-38.55, -3.75, 1600), "São Luís": (-44.25, -2.55, 2300),
       "Petrolina (sertão)": (-40.50, -9.40, 550), "Quixadá (sertão)": (-39.00, -4.95, 800),
       "Crato (Cariri)": (-39.40, -7.25, 1100)}
lin = []
for k, (lo, la, normal) in pts.items():
    s = ne_all.sel(lon=lo, lat=la, method="nearest").load()
    im = float(s.resample(time="YS").sum().mean())
    lin.append({"local": k, "IMERG_mm_ano": round(im), "normal_aprox_mm": normal, "razão": round(im / normal, 2)})
tab_costa = pd.DataFrame(lin).set_index("local")
print(tab_costa.to_string())
print("\n→ litoral leste (Natal a Salvador): IMERG ≈", f"{tab_costa.loc[['Recife','Maceió','Aracaju','João Pessoa','Salvador','Natal'],'razão'].mean():.0%}",
      "da normal; sertão ≈", f"{tab_costa.loc[['Petrolina (sertão)','Quixadá (sertão)'],'razão'].mean():.0%}")

# %% [markdown]
# **Consequência para o produto:** no sertão do Ceará (o foco da demo) o IMERG é confiável. No litoral leste ele
# fica em ~40–60 % das normais aproximadas. Parte disso pode vir de o pixel de 0,1° misturar terra e mar, e o ERA5
# também subestima Recife (ver seção 3.7), mas a ordem de grandeza indica um viés real. Qualquer balanço hídrico
# ali precisa de **correção de viés com pluviômetros** (INMET, ANA, FUNCEME/APAC ou CHIRPS, que já incorpora
# estações). A ferramenta deve mostrar um selo de confiança por pixel, calculado onde houver estação.

# %% [markdown]
# ## 2.3 Estatística descritiva — Ceará e Nordeste

# %%
anos_completos = [a for a in range(1998, 2026)]
anual_ce = ce.sel(time=ce.time.dt.year.isin(anos_completos)).resample(time="YS").sum()
anual_ce["time"] = anual_ce.time.dt.year
serie_anual = serie_ce[serie_ce.index.year.isin(anos_completos)].resample("YS").sum()
serie_anual.index = serie_anual.index.year
desc = serie_anual.describe()
print("Total anual médio na área do Ceará (1998–2025):")
print(desc.round(1).to_string())
print(f"assimetria {stats.skew(serie_anual):.2f} | curtose {stats.kurtosis(serie_anual):.2f} | CV {serie_anual.std()/serie_anual.mean():.1%}")
chuva = v[v >= 1]
print(f"dias de chuva (≥1 mm) por ano, média por pixel: {(ce_m >= 1).sum('time').where(M_CE).mean().item() / len(np.unique(ce.time.dt.year)):.0f}")
print(f"intensidade média nos dias de chuva (SDII): {chuva.mean():.1f} mm/dia")

fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
mapa(ax[0], anual_ce.mean("time").where(M_CE), "Chuva média anual 1998–2025 (mm)", "YlGnBu")
cv = (anual_ce.std("time") / anual_ce.mean("time")).where(M_CE)
mapa(ax[1], cv, "Coeficiente de variação interanual", "magma_r")
ax[2].hist(chuva, bins=np.logspace(0, 2.6, 60), color="steelblue")
ax[2].set_xscale("log")
ax[2].set_yscale("log")
ax[2].set_title("Distribuição dos dias de chuva (pixel-dia, mm)")
plt.tight_layout()
plt.show()

# %%
# Nordeste: agregados anuais ano a ano (sem carregar tudo de uma vez)
ne_arqs = sorted(DIR.glob("imerg_ne_diario_*.nc"))
print("arquivos NE:", len(ne_arqs))
anual_ne, quadra_ne, clim_ne = [], [], []
if not ne_arqs:
    raise SystemExit("dados do Nordeste ainda não consolidados")
for a in ne_arqs:
    d = xr.open_dataset(a)["precip"].load()
    ano = int(d.time.dt.year[0])
    if ano in anos_completos:
        anual_ne.append(d.sum("time").expand_dims(ano=[ano]))
    quadra_ne.append(d.sel(time=d.time.dt.month.isin([2, 3, 4, 5])).sum("time").expand_dims(ano=[ano]))
    clim_ne.append(d.resample(time="MS").sum())
anual_ne = xr.concat(anual_ne, "ano")
quadra_ne = xr.concat(quadra_ne, "ano")
mens_ne = xr.concat(clim_ne, "time")
M_NE = xr.DataArray(mascara(ne_gdf.geometry.union_all(), anual_ne.lon.values, anual_ne.lat.values), dims=("lat", "lon"))
fig, ax = plt.subplots(1, 2, figsize=(14, 6))
mapa(ax[0], anual_ne.mean("ano").where(M_NE), "Nordeste — chuva média anual 1998–2025 (mm)", "YlGnBu", gdf=ne_gdf)
mapa(ax[1], (quadra_ne.mean("ano") / anual_ne.mean("ano")).where(M_NE), "Fração do ano que cai em fev–mai", "PuOr",
     gdf=ne_gdf, vmin=0, vmax=1)
plt.tight_layout()
plt.show()
siglas = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
tab = []
for _, r in ne_gdf.iterrows():
    m = xr.DataArray(mascara(r.geometry, anual_ne.lon.values, anual_ne.lat.values), dims=("lat", "lon"))
    s = anual_ne.where(m).mean(("lat", "lon")).to_series()
    q = quadra_ne.where(m).mean(("lat", "lon")).to_series()
    tab.append({"UF": siglas[str(r.codarea)], "anual_media_mm": s.mean(), "anual_dp_mm": s.std(), "CV": s.std() / s.mean(),
                "min_ano": s.idxmin(), "min_mm": s.min(), "fração_fev_mai": (q.reindex(s.index) / s).mean()})
print(pd.DataFrame(tab).set_index("UF").round(2).sort_values("anual_media_mm").to_string())

# %% [markdown]
# ## 2.4 Sazonalidade e a quadra chuvosa (fev–mai)

# %%
mens_ce = serie_ce.resample("MS").sum()
mens_ce = mens_ce[mens_ce.index < "2026-09-01"]
clim = mens_ce.groupby(mens_ce.index.month).agg(["mean", "std", lambda x: x.quantile(0.1), lambda x: x.quantile(0.9)])
clim.columns = ["media", "dp", "p10", "p90"]
clim.index = MESES
print(clim.round(1).to_string())
print(f"fração do total anual em fev–mai: {clim.loc[['fev','mar','abr','mai'],'media'].sum()/clim['media'].sum():.1%}")
fig, ax = plt.subplots(1, 2, figsize=(14, 4))
ax[0].bar(MESES, clim.media, yerr=clim.dp, color=["#1f77b4" if m in ("fev", "mar", "abr", "mai") else "#bbb" for m in MESES])
ax[0].fill_between(range(12), clim.p10, clim.p90, alpha=0.2, color="orange", label="p10–p90")
ax[0].set_title("Climatologia mensal — área do Ceará (mm/mês)")
ax[0].legend()
mapa(ax[1], ce.sel(time=ce.time.dt.month.isin([2, 3, 4, 5])).groupby("time.year").sum().mean("year").where(M_CE)
     / anual_ce.mean("time").where(M_CE), "Fração do total anual em fev–mai", "PuOr", vmin=0.4, vmax=1)
plt.tight_layout()
plt.show()

# %%
# Início/fim da estação chuvosa (Liebmann & Marengo 2001: acumulado de anomalias no ano hidrológico ago–jul)
media_diaria = serie_ce.mean()
reg = []
for ano in range(1998, 2026):
    s = serie_ce[f"{ano}-08-01":f"{ano+1}-07-31"]
    if len(s) < 360:
        continue
    A = (s - media_diaria).cumsum()
    ini = A[: f"{ano+1}-04-30"].idxmin()        # inicio: minimo do acumulado ate o fim de abril
    fim = A[ini:].idxmax()                      # fim: maximo do acumulado depois do inicio
    if fim <= ini:
        continue
    reg.append({"ano_hidro": f"{ano}/{ano+1}", "inicio": ini, "fim": fim, "duracao_dias": (fim - ini).days,
                "total_estacao_mm": s[ini:fim].sum()})
est = pd.DataFrame(reg)
est["inicio_doy"] = est.inicio.dt.dayofyear.where(est.inicio.dt.month < 8, est.inicio.dt.dayofyear - 365)
print(est[["ano_hidro", "inicio", "fim", "duracao_dias", "total_estacao_mm"]].to_string(index=False))
print(f"\ninício médio: dia {est.inicio_doy.mean():.0f} do ano (dp {est.inicio_doy.std():.0f} dias) | duração média {est.duracao_dias.mean():.0f} dias")
r = stats.spearmanr(est.inicio_doy, est.total_estacao_mm)
print(f"correlação (Spearman) início × total da estação: {r.statistic:.2f} (p={r.pvalue:.3f})")

# %% [markdown]
# ## 2.5 Tendências (Mann-Kendall + declive de Sen)

# %%
quadra_ce = serie_ce[serie_ce.index.month.isin([2, 3, 4, 5])].resample("YS").sum()
quadra_ce.index = quadra_ce.index.year
dias_chuva = (ce_m >= 1).where(M_CE).sum("time")
res = []
for nome, s in [("total anual (1998–2025)", serie_anual), ("quadra fev–mai (1998–2026)", quadra_ce),
                ("duração da estação", est.set_index("ano_hidro").duracao_dias),
                ("início da estação (dia)", est.set_index("ano_hidro").inicio_doy)]:
    t = mk.original_test(s.values)
    res.append({"série": nome, "tendência": t.trend, "p": round(t.p, 3), "Sen/ano": round(t.slope, 2),
                "Sen/década_%média": round(10 * t.slope / s.mean() * 100, 1)})
print(pd.DataFrame(res).to_string(index=False))


def sen_mk_grade(cubo):
    """cubo (ano, lat, lon) -> declive de Sen e p-valor por pixel."""
    sl = np.full(cubo.shape[1:], np.nan)
    pv = np.full(cubo.shape[1:], np.nan)
    arr = cubo.values
    for i in range(arr.shape[1]):
        for j in range(arr.shape[2]):
            y = arr[:, i, j]
            if np.isfinite(y).sum() > 10:
                t = mk.original_test(y)
                sl[i, j], pv[i, j] = t.slope, t.p
    return (xr.DataArray(sl, coords={"lat": cubo.lat, "lon": cubo.lon}, dims=("lat", "lon")),
            xr.DataArray(pv, coords={"lat": cubo.lat, "lon": cubo.lon}, dims=("lat", "lon")))


sl_ce, p_ce = sen_mk_grade(anual_ce.where(M_CE))
ne_c = anual_ne.coarsen(lat=2, lon=2, boundary="trim").mean()
sl_ne, p_ne = sen_mk_grade(ne_c)
fig, ax = plt.subplots(1, 2, figsize=(15, 5.5))
mapa(ax[0], (sl_ce * 10).where(M_CE), "Ceará — tendência do total anual (mm/década)", "BrBG", vmin=-150, vmax=150)
yy, xx = np.where((p_ce < 0.1).values & M_CE.values)
ax[0].scatter(ce.lon.values[xx], ce.lat.values[yy], s=1, c="k", label="p<0,1")
ax[0].legend(loc="lower right")
mapa(ax[1], sl_ne * 10, "Nordeste (0,2°) — tendência do total anual (mm/década)", "BrBG", gdf=ne_gdf, vmin=-150, vmax=150)
yy, xx = np.where((p_ne < 0.1).values)
ax[1].scatter(ne_c.lon.values[xx], ne_c.lat.values[yy], s=1, c="k")
plt.tight_layout()
plt.show()
print(f"pixels do Ceará com tendência significativa (p<0,1): {float(((p_ce < 0.1) & M_CE).sum() / M_CE.sum()):.1%}")
print(f"células do NE com tendência significativa (p<0,1): {float((p_ne < 0.1).sum() / np.isfinite(p_ne).sum()):.1%}")

# %% [markdown]
# ## 2.6 Variabilidade interanual, seca 2012–2017 e extremos

# %%
anom = (serie_anual - serie_anual.mean()) / serie_anual.std()
fig, ax = plt.subplots(figsize=(14, 4))
cores = ["#b2182b" if 2012 <= a <= 2017 else ("#d6604d" if z < 0 else "#2166ac") for a, z in anom.items()]
ax.bar(anom.index, serie_anual - serie_anual.mean(), color=cores)
ax.set_title("Anomalia do total anual no Ceará (mm) — vermelho escuro = seca 2012–2017")
plt.show()
seca = serie_anual.loc[2012:2017]
print(f"seca 2012–2017: média {seca.mean():.0f} mm vs normal {serie_anual.drop(range(2012, 2018)).mean():.0f} mm "
      f"({seca.mean()/serie_anual.drop(range(2012, 2018)).mean()-1:+.0%}); 6 anos seguidos abaixo da média: "
      f"{(seca < serie_anual.mean()).all()}")
print("anos mais secos:", serie_anual.nsmallest(4).round(0).to_dict())
print("anos mais chuvosos:", serie_anual.nlargest(4).round(0).to_dict())

# %%
# Índices de extremos por pixel (ETCCDI simplificados) e veranicos na quadra
def maior_seq(b):
    m = c = 0
    for x in b:
        c = c + 1 if x else 0
        m = max(m, c)
    return m


def veranicos(serie_quadra, limiar=1.0, minimo=10):
    seca = serie_quadra < limiar
    n = c = 0
    for x in seca:
        if x:
            c += 1
        else:
            if c >= minimo:
                n += 1
            c = 0
    return n + (1 if c >= minimo else 0)


ind = []
for ano in range(1998, 2027):
    s = serie_ce[str(ano)]
    q = s[s.index.month.isin([2, 3, 4, 5])]
    ind.append({"ano": ano, "Rx1day": s.max(), "Rx5day": s.rolling(5).sum().max(),
                "dias>20mm": int((s >= 20).sum()), "dias>50mm": int((s >= 50).sum()),
                "CDD_quadra": maior_seq(q < 1), "veranicos≥10d": veranicos(q, 1, 10), "veranicos≥5d": veranicos(q, 1, 5)})
ind = pd.DataFrame(ind).set_index("ano")
print("Índices na MÉDIA do Ceará (a média espacial suaviza extremos; ver mapas por pixel abaixo):")
print(ind.round(1).to_string())

# por pixel: maior veranico da quadra (média dos anos) e frequência de dias > 20/50 mm
qd = ce.sel(time=ce.time.dt.month.isin([2, 3, 4, 5]))
cdd = []
for ano in range(1998, 2027):
    b = (qd.sel(time=str(ano)) < 1).values
    run = np.zeros(b.shape[1:])
    mx = np.zeros(b.shape[1:])
    for t in range(b.shape[0]):
        run = np.where(b[t], run + 1, 0)
        mx = np.maximum(mx, run)
    cdd.append(mx)
cdd = xr.DataArray(np.array(cdd), dims=("ano", "lat", "lon"), coords={"ano": range(1998, 2027), "lat": ce.lat, "lon": ce.lon})
fig, ax = plt.subplots(1, 3, figsize=(17, 4.5))
mapa(ax[0], cdd.mean("ano").where(M_CE), "Maior veranico na quadra (dias, média)", "OrRd")
mapa(ax[1], ((ce >= 20).sum("time") / len(np.unique(ce.time.dt.year))).where(M_CE), "Dias/ano com ≥20 mm", "Blues")
mapa(ax[2], ((ce >= 50).sum("time") / len(np.unique(ce.time.dt.year))).where(M_CE), "Dias/ano com ≥50 mm", "Purples")
plt.tight_layout()
plt.show()
print(f"maior veranico médio na quadra (pixel): {float(cdd.mean('ano').where(M_CE).mean()):.1f} dias; "
      f"na seca 2012: {float(cdd.sel(ano=2012).where(M_CE).mean()):.1f}; no chuvoso 2009: {float(cdd.sel(ano=2009).where(M_CE).mean()):.1f}")

# %%
# Período de retorno do máximo diário (Gumbel) — média dos pixels do Ceará e mapa do evento de 10 anos
amax = ce.sel(time=ce.time.dt.year.isin(range(1998, 2026))).groupby("time.year").max()
loc, esc = stats.gumbel_r.fit(amax.where(M_CE).stack(p=("lat", "lon")).dropna("p").median("p").values)
print("Rx1day mediano entre pixels — níveis de retorno (mm):",
      {T: round(stats.gumbel_r.ppf(1 - 1 / T, loc, esc), 1) for T in (2, 5, 10, 25)})
a = amax.values
mu = np.nanmean(a, 0)
sd = np.nanstd(a, 0)
# método dos momentos (rápido por pixel)
beta = sd * np.sqrt(6) / np.pi
mu_g = mu - 0.5772 * beta
r10 = mu_g - beta * np.log(-np.log(1 - 1 / 10))
fig, ax = plt.subplots(figsize=(6, 5))
mapa(ax, xr.DataArray(r10, coords={"lat": ce.lat, "lon": ce.lon}, dims=("lat", "lon")).where(M_CE),
     "Chuva diária de 10 anos de retorno (mm, Gumbel)", "plasma")
plt.show()

# %% [markdown]
# ## 2.7 Erosividade da chuva (fator R da USLE/RUSLE)
# Duas estimativas:
# 1. **Mensal (toda a série):** equação de Lombardi Neto & Moldenhauer (1992),
#    $EI_{30} = 67{,}355\,(r^2/P)^{0,85}$, com $r$ = chuva do mês e $P$ = chuva anual
#    (MJ·mm·ha⁻¹·h⁻¹; equação de Campinas/SP, que precisa de validação no semiárido).
# 2. **Por evento (amostra meia-hora V06):** energia cinética de Brown & Foster (1987),
#    $e = 0{,}29[1-0{,}72e^{-0{,}05i}]$, vezes a intensidade máxima em 30 min ($I_{30}$).

# %%
mens_px = ce.resample(time="MS").sum()
anual_px = mens_px.groupby("time.year").sum()
eir = []
for ano in range(1998, 2026):
    r = mens_px.sel(time=str(ano))
    P = anual_px.sel(year=ano)
    eir.append((67.355 * (r ** 2 / P) ** 0.85).sum("time"))
R = xr.concat(eir, "ano").assign_coords(ano=range(1998, 2026))
fig, ax = plt.subplots(1, 2, figsize=(14, 4.5))
mapa(ax[0], R.mean("ano").where(M_CE), "Fator R médio (MJ·mm·ha⁻¹·h⁻¹·ano⁻¹)", "inferno_r")
Rs = R.where(M_CE).mean(("lat", "lon")).to_series()
ax[1].plot(Rs.index, Rs.values, "o-")
ax[1].set_title("Fator R na média do Ceará por ano")
plt.tight_layout()
plt.show()
print(f"R médio no Ceará: {Rs.mean():.0f} (faixa entre anos {Rs.min():.0f}–{Rs.max():.0f}); "
      f"correlação com o total anual: {np.corrcoef(Rs.values, serie_anual.loc[1998:2025].values)[0,1]:.2f}")

# %% [markdown]
# ## 2.8 Ciclo diurno e intensidade de 30 min (amostra nativa V06, horário local UTC−3)

# %%
if pc_arqs:
    hh = xr.open_mfdataset(pc_arqs, combine="by_coords")["precip_ne"].load()  # (time, lon, lat) mm/h
    hh = hh.transpose("time", "lat", "lon").sel(lon=slice(BBOX_CE[0], BBOX_CE[2]), lat=slice(BBOX_CE[1], BBOX_CE[3]))
    hh = hh.assign_coords(time=hh.time - np.timedelta64(3, "h"))
    Mh = xr.DataArray(mascara(ce_gdf.geometry.union_all(), hh.lon.values, hh.lat.values), dims=("lat", "lon"))
    hora = hh.time.dt.hour + hh.time.dt.minute / 60
    ciclo = hh.where(Mh).groupby(hora).mean().mean(("lat", "lon"))
    costa = hh.where(Mh & (hh.lat > -3.6)).groupby(hora).mean().mean(("lat", "lon"))
    interior = hh.where(Mh & (hh.lat < -5.5)).groupby(hora).mean().mean(("lat", "lon"))
    pico = hh.groupby(hh.time.dt.hour).mean().idxmax("hour")
    fig, ax = plt.subplots(1, 2, figsize=(14, 4.5))
    ax[0].plot(ciclo.group, ciclo, label="Ceará")
    ax[0].plot(costa.group, costa, label="faixa litorânea (lat > −3,6)")
    ax[0].plot(interior.group, interior, label="sul/sertão (lat < −5,5)")
    ax[0].set_xlabel("hora local")
    ax[0].set_ylabel("mm/h médio")
    ax[0].set_title(f"Ciclo diurno da chuva — {len(pc_arqs)} dia(s) de mar/2009")
    ax[0].legend()
    mapa(ax[1], pico.where(Mh), "Hora local do pico médio de chuva", "twilight")
    plt.tight_layout()
    plt.show()
    for nome, c in [("Ceará", ciclo), ("litoral", costa), ("sul/sertão", interior)]:
        print(f"{nome}: pico às {float(c.idxmax()):.1f} h local, mínimo às {float(c.idxmin()):.1f} h; "
              f"razão pico/média {float(c.max() / c.mean()):.1f}")
    # erosividade por evento diário (I30 = maior intensidade em 30 min; energia Brown & Foster)
    e_unit = 0.29 * (1 - 0.72 * np.exp(-0.05 * hh))  # MJ/ha/mm
    energia = (e_unit * hh * 0.5).resample(time="D").sum()  # MJ/ha
    i30 = hh.resample(time="D").max()
    ei30 = (energia * i30).where(Mh)
    tot = (hh * 0.5).resample(time="D").sum().where(Mh)
    print(f"I30 máximo na amostra: {float(i30.where(Mh).max()):.0f} mm/h | EI30 diário máx: {float(ei30.max()):.0f} MJ·mm·ha⁻¹·h⁻¹")
    print(f"fração da chuva caída com intensidade > 25 mm/h: "
          f"{float((hh.where(hh > 25) * 0.5).where(Mh).sum() / (hh * 0.5).where(Mh).sum()):.1%}")
else:
    print("amostra meia-hora ainda não baixada")

# %% [markdown]
# ## 2.9 Coerência entre versões: V07 diário (POWER) × V06 meia-hora (Planetary Computer)

# %%
if pc_arqs:
    v06 = (hh.assign_coords(time=hh.time + np.timedelta64(3, "h")) * 0.5).resample(time="D").sum()
    comum_t = np.intersect1d(v06.time.values, ce.time.values)
    a6 = v06.sel(time=comum_t).interp(lat=ce.lat, lon=ce.lon, method="nearest").where(M_CE)
    a7 = ce.sel(time=comum_t).where(M_CE)
    x, y = a6.values.ravel(), a7.values.ravel()
    ok = np.isfinite(x) & np.isfinite(y)
    print(f"dias comparados: {len(comum_t)} | pixel-dias: {ok.sum()} | r de Pearson {np.corrcoef(x[ok], y[ok])[0,1]:.2f} | "
          f"viés V07−V06: {np.mean(y[ok]-x[ok]):+.2f} mm/dia ({np.mean(y[ok])/np.mean(x[ok])-1:+.0%})")

# %% [markdown]
# ## 2.10 Insights e ideias para o produto
# (números medidos nas células acima; IMERG V07 diário 1998–2026 e amostra V06 meia-hora de mar/2009)
#
# 1. **Chuva concentrada = risco concentrado.** 73 % da chuva anual do Ceará cai em fev–mai, com média de
#    812 mm/ano (1998–2025) e CV interanual de 27 % na média estadual (maior no sertão, ver mapa). O calendário do
#    produto deve trabalhar com probabilidades (p10/p90 por mês), não com médias.
# 2. **O dia de início da estação prevê a estação.** Pelo acumulado de anomalias (Liebmann & Marengo), o início
#    médio é ~17/jan (dp 22 dias) e tem correlação de Spearman **−0,67** com o total da estação. Inícios tardios
#    (mar/2010, fev/2012) vieram com estações de 48–72 dias e ~330 mm. Regra de decisão para o produto: se até
#    meados de fevereiro a estação não "abriu", trocar para a rotação de ciclo curto / tolerante à seca.
# 3. **Seca 2012–2017: seis anos seguidos abaixo da média**, com média de 612 mm contra 867 mm nos demais anos (−29 %).
#    2012 (432 mm) foi o pior ano da série. Justifica um módulo de "rotação de emergência" (sorgo, palma
#    forrageira, caupi precoce, milheto).
# 4. **Veranicos.** O maior período seco dentro da quadra tem em média 12,7 dias por pixel; foram 22,6 dias em 2012
#    contra 6,9 em 2009. Culturas com fase crítica (floração/enchimento) de mais de 2 semanas sem chuva correm
#    risco alto em boa parte do sertão.
# 5. **Sem tendência robusta de chuva em 28 anos** (−3,7 %/década, p = 0,42; só 13 % dos pixels com p < 0,1). A
#    variabilidade interanual domina a tendência; o risco vem da variabilidade, não de um secamento linear.
# 6. **Erosividade alta e concentrada.** O fator R médio é ~6.350 MJ·mm·ha⁻¹·h⁻¹·ano⁻¹ (4.000–9.900 entre anos),
#    com correlação 0,92 com o total anual. Na amostra de 30 min há I30 de até 80 mm/h, e 5,7 % da chuva cai acima
#    de 25 mm/h. A chuva de 10 anos de retorno é ~70 mm/dia (mediana dos pixels). Solo descoberto no início da
#    quadra é o pior cenário, o que dá argumento para cobertura morta e plantas de cobertura (cruzar com NDVI de
#    solo exposto e declividade do SRTM).
# 7. **Ciclo diurno muda entre litoral e interior:** pico às 16 h no litoral (convecção de brisa) e às 22h30 no sul
#    do estado (sistemas noturnos). Isso orienta a janela de pulverização, de fenação e de colheita.
# 8. **Limitação crítica: o IMERG fica muito abaixo das normais no litoral leste do NE** (Recife, Maceió, Aracaju,
#    Salvador ≈ 41–60 % das normais aproximadas; parte pode ser efeito de pixel misto terra/mar), mas é bom no
#    sertão (82–94 %). Para a demo no sertão do Ceará ele serve. No produto mundial, cada pixel precisa de um selo
#    de confiança e de correção por pluviômetros onde houver.
# 9. **Coerência entre versões:** V07 (POWER) × V06 (Planetary Computer) nos mesmos dias: r = 0,80; a V07 tem +10 %.
#
# **Ideias de ML/DL a partir desta base**
# - **Previsão sazonal da quadra** com índices oceânicos (Niño 3.4, gradiente do Atlântico tropical) + o próprio
#   início da estação: gradient boosting / regressão quantílica → probabilidade de ano seco, normal ou chuvoso por município.
# - **Modelo de sobrevivência para veranicos** (Weibull / Cox, covariáveis: ENSO, altitude, mês) → risco de
#   veranico ≥ 15 dias na floração de cada cultura candidata. Entra direto na pontuação das rotações.
# - **Correção de viés costeiro**: regressão espacial (GWR / random forest com distância ao mar, altitude e vento)
#   treinada com pluviômetros INMET/ANA/FUNCEME → IMERG corrigido; avaliar com validação cruzada espacial.
# - **Nowcasting 0–6 h** (ConvLSTM / U-Net temporal) com o IMERG de meia hora (Early, latência ~4 h) para alertas de
#   chuva forte em colheita e aplicação de defensivos.
# - **Downscaling 0,1° → 1 km** com SRTM e NDVI como covariáveis (U-Net/SRCNN), para chegar à escala do talhão.
