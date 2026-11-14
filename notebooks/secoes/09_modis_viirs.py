# %% [markdown]
# # 9. MODIS e VIIRS — vegetação, temperatura da superfície, evapotranspiração e fogo
#
# Esta seção estuda os produtos MODIS (Terra/Aqua) e VIIRS (S-NPP) baixados para o Ceará e o Nordeste:
#
# | Produto | O que mede | Resolução nativa | Frequência | Período baixado | Recorte salvo |
# |---|---|---|---|---|---|
# | MOD13Q1 v061 (Terra) | NDVI e EVI (índices de vegetação) + confiabilidade do pixel | 250 m | composto de 16 dias | fev/2000 → 2026 | Ceará em grade 0,01° (~1,1 km) + 4 AOIs a 250 m |
# | MOD13A1 v061 (Terra) | NDVI | 500 m | 16 dias | 2000 → 2026 | Nordeste em grade 0,05° (~5,5 km) |
# | MOD11A2 v061 (Terra) | Temperatura da superfície (LST) dia (~10h30) e noite (~22h30) | 1 km | composto de 8 dias | 2000 → 2026 | Ceará 0,01° |
# | MOD16A3GF v061 (Terra) | Evapotranspiração real (ET) e potencial (PET) anual | 500 m | anual | 2000 → 2025 | Ceará 0,005° |
# | MCD64A1 v061 (Terra+Aqua) | Área queimada (data da queima) | 500 m | mensal | nov/2000 → 2026 | Nordeste: fração 0,05° mensal, mapas anuais 0,005°, km² por UF |
# | FIRMS VIIRS S-NPP | Focos de fogo ativo (375 m) | ponto | por passagem | 2012 → 2025 | Nordeste, por UF |
# | FIRMS MODIS (MCD14) | Focos de fogo ativo (1 km) | ponto | por passagem | 2000 → 2025 | Nordeste, por UF |
# | VIIRS VNP13 (NDVI) | NDVI do VIIRS (continuidade do MODIS) | 500 m / 1 km | 16 dias | **não baixado** (exige Earthdata Login) | — |
# | ESA CCI Land Cover 2020 (auxiliar) | Classe de cobertura do solo (lavoura, arbustiva, floresta…) | 300 m | anual | 2020 | Nordeste |
#
# **Fontes de acesso:** Microsoft Planetary Computer (STAC + COG, aberto, sem login) para os MODIS e o ESA CCI;
# NASA FIRMS (arquivos anuais por país, abertos) para os focos de fogo.
#
# **Decisão de processamento importante:** os *overviews* dos COGs do Planetary Computer foram gerados por
# **média**, o que corrompe camadas categóricas de qualidade (aparecem códigos de confiabilidade 4–10 que não
# existem no produto). Por isso tudo foi lido em resolução cheia, a máscara de qualidade foi aplicada no pixel
# nativo (`pixel_reliability ≤ 1` no NDVI; QC mandatório e erro ≤ 2 K na LST) e só depois os dados foram agregados
# por média para a grade lat/lon.

# %%
import json
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymannkendall as mk
import xarray as xr
from rasterio.features import rasterize
from rasterio.transform import from_origin
from scipy import stats

warnings.filterwarnings("ignore")
pd.set_option("display.width", 180)
pd.set_option("display.max_columns", 30)
plt.rcParams.update({"figure.dpi": 90, "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9})

M = DADOS / "modis"
V = DADOS / "viirs"
CE = ceara_gdf()
NE = nordeste_gdf()
UF_NOME = {21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA"}
NE["sigla"] = NE["codarea"].astype(int).map(UF_NOME)
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
CHUVOSA = [2, 3, 4, 5]          # quadra chuvosa do Ceará (fev–mai)
SECA = [8, 9, 10, 11]           # auge da estação seca
SECA_GRANDE = list(range(2012, 2018))


def mascara(lats, lons, gdf):
    res = abs(float(lats[0] - lats[1]))
    T = from_origin(float(lons[0]) - res / 2, float(lats[0]) + res / 2, res, res)
    return rasterize([(g, 1) for g in gdf.geometry], out_shape=(len(lats), len(lons)), transform=T,
                     fill=0, dtype="uint8").astype(bool)


def extent(da):
    r = abs(float(da.lon[1] - da.lon[0]))
    return [float(da.lon.min()) - r / 2, float(da.lon.max()) + r / 2, float(da.lat.min()) - r / 2, float(da.lat.max()) + r / 2]


def mapa(da, titulo, ax, cmap="viridis", vmin=None, vmax=None, contorno=CE, rotulo=""):
    im = ax.imshow(np.asarray(da), extent=extent(da), origin="upper", cmap=cmap, vmin=vmin, vmax=vmax,
                   interpolation="nearest")
    contorno.boundary.plot(ax=ax, color="k", lw=0.6)
    ax.set_title(titulo)
    ax.set_xlabel("lon")
    ax.set_ylabel("lat")
    ax.grid(False)
    plt.colorbar(im, ax=ax, shrink=0.8, label=rotulo)
    return im


def descr(x, nome):
    x = np.asarray(x, dtype="float64").ravel()
    x = x[np.isfinite(x)]
    if x.size == 0:
        return {"variavel": nome, "n": 0}
    p = np.percentile(x, [5, 25, 50, 75, 95])
    return {"variavel": nome, "n": x.size, "media": x.mean(), "desvio": x.std(), "p05": p[0], "p25": p[1],
            "mediana": p[2], "p75": p[3], "p95": p[4], "assimetria": stats.skew(x), "curtose": stats.kurtosis(x)}


def mk_vetorizado(Y):
    """Mann-Kendall (sem correção de empates) + inclinação de Sen, vetorizado. Y: (T, N) com NaN."""
    Y = np.asarray(Y, dtype="float32")
    Tn = Y.shape[0]
    i, j = np.triu_indices(Tn, 1)
    D = Y[j] - Y[i]
    S = np.nansum(np.sign(D), axis=0)
    n = np.sum(np.isfinite(Y), axis=0).astype("float64")
    var = n * (n - 1) * (2 * n + 5) / 18.0
    with np.errstate(all="ignore"):
        z = np.where(S > 0, (S - 1) / np.sqrt(var), np.where(S < 0, (S + 1) / np.sqrt(var), 0.0))
        p = 2 * (1 - stats.norm.cdf(np.abs(z)))
        sen = np.nanmedian(D / (j - i)[:, None].astype("float32"), axis=0)
    p[n < 8] = np.nan
    sen[n < 8] = np.nan
    return sen, z, p


def mk_tabela(series: dict, unidade: dict):
    linhas = []
    for nome, s in series.items():
        s = s.dropna()
        if len(s) < 8:
            continue
        r = mk.original_test(s.values)
        linhas.append({"serie": nome, "n_anos": len(s), "inicio": int(s.index.min()), "fim": int(s.index.max()),
                       "tendencia": r.trend, "p_valor": round(r.p, 4), "tau": round(r.Tau, 3),
                       "sen_por_ano": r.slope, "sen_por_decada": r.slope * 10, "unidade": unidade.get(nome, ""),
                       "media": s.mean(), "mudanca_%_por_decada": 100 * r.slope * 10 / s.mean() if s.mean() else np.nan})
    return pd.DataFrame(linhas)


def carregar(p):
    p = M / p if not str(p).startswith(("E:", "e:")) else p
    if not Path(p).exists():
        print("AUSENTE:", p)
        return None
    return xr.open_dataset(p)


# %% [markdown]
# ## 9.1 Inventário do que foi baixado

# %%
inv = []
for pasta_ in (M, V):
    for f in sorted(pasta_.glob("*")):
        if f.is_file():
            inv.append({"pasta": pasta_.name, "arquivo": f.name, "MB": round(f.stat().st_size / 1e6, 1)})
inv = pd.DataFrame(inv)
print(inv.to_string(index=False))
print(f"\nTotal: {inv.MB.sum():.0f} MB")
man = json.loads((M / "MANIFESTO.json").read_text(encoding="utf-8"))
for k, v in man.items():
    if isinstance(v, dict):
        print(f"- {k}: período {v.get('periodo', v.get('anos', ''))} | datas {v.get('n_datas', v.get('n_meses', v.get('n_anos', '')))}"
              f" | erros {len(v.get('erros', []))}")

# %% [markdown]
# ## 9.2 Validação de cobertura global — "é realmente do mundo todo?"
#
# Evidências usadas:
# 1. **Inventário de tiles** num único período de cada produto, consultado no catálogo STAC do Planetary Computer.
#    A grade sinusoidal do MODIS tem 36 × 18 = 460 tiles; só os que contêm terra são produzidos.
# 2. **Amostra de 14 pontos agrícolas e de controle em todos os continentes** (inclusive deserto e alta latitude),
#    lendo o valor do pixel diretamente no arquivo.
# 3. **FIRMS:** existência do arquivo anual por país para vários países de todos os continentes.

# %%
val = json.loads((M / "validacao_global.json").read_text(encoding="utf-8"))
tab = []
for col, info in val["colecoes"].items():
    tab.append({"colecao": col, "tiles_num_periodo": info["n_tiles"], "lat_min": info["lat_min"], "lat_max": info["lat_max"],
                "lon_min": info["lon_min"], "lon_max": info["lon_max"]})
print(pd.DataFrame(tab).to_string(index=False))
tpp = pd.DataFrame({col: {dt: v["n_tiles"] for dt, v in d.items()} for col, d in val.get("tiles_por_periodo", {}).items()})
print("\nTiles disponíveis por período (estabilidade do catálogo):")
print(tpp.to_string())
print("Lacunas conhecidas do MCD64A1 no Nordeste:", val.get("lacunas_nordeste_mcd64a1"))

fig, ax = plt.subplots(figsize=(11, 5))
terra = terra_gdf()
terra.plot(ax=ax, color="#ddd", edgecolor="#999", lw=0.3)
cores = {"modis-13Q1-061": "tab:green", "modis-11A2-061": "tab:red", "modis-64A1-061": "tab:orange", "modis-16A3GF-061": "tab:blue"}
for k, (col, info) in enumerate(val["colecoes"].items()):
    hv = np.array(info["tiles"]) if info["tiles"] else np.zeros((0, 2))
    if len(hv) == 0:
        continue
    lat_c = 90 - (hv[:, 1] + 0.5) * 10
    lon_c = ((hv[:, 0] + 0.5) * 10 - 180) / np.cos(np.radians(lat_c))
    ok = np.abs(lon_c) <= 180
    ax.scatter(lon_c[ok] + 1.5 * k, lat_c[ok], s=9, color=cores.get(col, "k"), label=f"{col} ({len(hv)} tiles)")
ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_title("Centros dos tiles MODIS produzidos num único período (deslocados para não sobrepor)")
ax.legend(loc="lower left", fontsize=7)
plt.show()


def decodifica(col, v):
    if v is None or isinstance(v, str):
        return v
    if col == "modis-13Q1-061":
        return None if v <= -3000 else round(v / 1e4, 3)
    if col == "modis-11A2-061":
        return None if v == 0 else round(v * 0.02 - 273.15, 1)
    if col == "modis-16A3GF-061":
        return None if v >= 65500 else round(v * 0.1, 0)
    if col == "modis-64A1-061":
        return {-2: "água", -1: "não mapeado", 0: "não queimado"}.get(int(v), f"queimado dia {int(v)}")
    return v


pts = []
for nome, info in val["pontos"].items():
    lin = {"ponto": nome, "lon": info["lon"], "lat": info["lat"]}
    for col in val["colecoes"]:
        r = info.get(col, {})
        lin[col.replace("modis-", "").replace("-061", "")] = decodifica(col, r.get("valor_bruto")) if r.get("item") else "sem tile"
    pts.append(lin)
pts = pd.DataFrame(pts)
print("\nValores lidos no pixel (NDVI jul/2024 | LST dia °C jul/2024 | ET 2023 mm/ano | MCD64A1 jul/2023):")
print(pts.to_string(index=False))

fv = json.loads((V / "validacao_global_firms.json").read_text(encoding="utf-8"))["head_2023"]
firms = pd.DataFrame([{"arquivo": k, "status": v.get("status"), "MB": round(v.get("bytes", 0) / 1e6, 1)} for k, v in fv.items()])
print("\nFIRMS – arquivo anual 2023 por país (HTTP 200 = existe):")
print(firms.to_string(index=False))

# %% [markdown]
# **Veredito de cobertura (lido das evidências acima):**
#
# - **MOD13Q1/MOD13A1 (NDVI), MOD11A2 (LST), MCD64A1 (área queimada): globais sobre terra.** Num único período existem
#   tiles de todos os continentes, de ~85° N a ~60° S. A LST inclui até a Antártida e a área queimada vai de 60° S a
#   75° N. Os limites de longitude acima de ±180° são artefato do retângulo envolvente dos tiles sinusoidais. O mar
#   não faz parte do produto terrestre.
#   Os pontos de teste em Iowa, Pampa, França, Ucrânia, Punjab, Henan, Quênia, Java, NSW (Austrália), Mato Grosso e
#   Ceará devolveram valores válidos. Os poucos "sem dado" são esperados: deserto sem vegetação, nuvem no
#   composto ou inverno boreal.
# - **MOD16A3GF (ET/PET): global, mas com buracos por desenho.** O algoritmo não calcula ET em áreas urbanas, água,
#   neve/gelo e solo nu (códigos ≥ 65 500). No Sahara o pixel vem como classe especial, não como ET.
# - **FIRMS (VIIRS e MODIS): global.** Há arquivos por país em todos os continentes; a Rússia aparece sob outro
#   nome no índice. O arquivo anual só existe para anos fechados (2026 não tem). O ano corrente exige a API NRT
#   com chave (MAP_KEY gratuita).
# - **Atenção para o produto mundial:** o Terra (MOD) e o Aqua (MYD) estão em fim de vida, com deriva orbital
#   desde ~2022, o que muda o horário de passagem e afeta a LST. A continuidade é o **VIIRS (VNP13/VNP21/VNP64)**,
#   que exige Earthdata Login. O desenho do sistema deve ser *agnóstico ao sensor*: MODIS até ~2025, VIIRS depois.

# %% [markdown]
# ## 9.3 Qualidade dos dados (nuvens, máscaras, buracos)

# %%
ce_m = pd.read_parquet(DERIV / "modis_ce_mensal.parquet")
ce_m["mes"] = ce_m.data.dt.month
boa = ce_m[ce_m.variavel == "pct_pixels_boa_qualidade_ndvi"]
fig, axs = plt.subplots(1, 3, figsize=(15, 3.6))
g = boa.groupby("mes").valor.agg(["mean", "min", "max"])
axs[0].bar(range(1, 13), g["mean"], color=["tab:blue" if m in CHUVOSA else "tab:gray" for m in range(1, 13)])
axs[0].errorbar(range(1, 13), g["mean"], yerr=[g["mean"] - g["min"], g["max"] - g["mean"]], fmt="none", color="k", lw=0.8)
axs[0].set_xticks(range(1, 13), MESES)
axs[0].set_title("NDVI MOD13Q1: % de pixels 250 m com boa qualidade\n(média mensal no Ceará; azul = quadra chuvosa)")
axs[0].set_ylim(0, 100)

ndvi16 = carregar("mod13q1_ndvi_evi_ceara_001deg.nc")
t = pd.to_datetime(ndvi16.time.values)
por_ano = pd.Series(1, index=t).groupby(t.year).sum()
axs[1].bar(por_ano.index, por_ano.values, color="tab:green")
axs[1].axhline(23, color="k", ls="--", lw=0.8)
axs[1].set_title("Compostos MOD13Q1 por ano (esperado 23)")
dif = np.diff(t.values).astype("timedelta64[D]").astype(int)
print("Intervalos entre compostos MOD13Q1 (dias):", pd.Series(dif).value_counts().to_dict())
print("Datas com falha de leitura:", int((~ndvi16.feito.values.astype(bool)).sum()))
for i in np.where(dif > 16)[0]:
    print(f"  lacuna NDVI: {t[i]:%Y-%m-%d} → {t[i + 1]:%Y-%m-%d} ({dif[i]} dias)")
lst8 = xr.open_dataset(M / "mod11a2_lst_ceara_001deg.nc")
t8 = pd.to_datetime(lst8.time.values)
d8 = np.diff(t8.values).astype("timedelta64[D]").astype(int)
print("Intervalos entre compostos MOD11A2 (dias):", pd.Series(d8).value_counts().to_dict())
for i in np.where(d8 > 9)[0]:
    print(f"  lacuna LST: {t8[i]:%Y-%m-%d} → {t8[i + 1]:%Y-%m-%d} ({d8[i]} dias)")

lstm = carregar("mod11a2_lst_mensal_001deg.nc").load()
mk_ce = mascara(lstm.lat.values, lstm.lon.values, CE)
frac_lst = lstm.lst_dia.where(mk_ce).notnull().sum(("lat", "lon")) / mk_ce.sum()
fl = frac_lst.to_series()
axs[2].bar(range(1, 13), fl.groupby(fl.index.month).mean() * 100,
           color=["tab:blue" if m in CHUVOSA else "tab:gray" for m in range(1, 13)])
axs[2].set_xticks(range(1, 13), MESES)
axs[2].set_title("LST dia MOD11A2: % do Ceará com valor válido no mês")
plt.tight_layout()
plt.show()

fogo_uf = pd.read_parquet(M / "mcd64a1_area_queimada_mensal_uf.parquet")
fogo_uf["data"] = pd.to_datetime(fogo_uf["data"])
q = fogo_uf.groupby("data")[["area_terra_km2", "area_sem_mapeamento_km2"]].sum()
q["pct_sem_mapeamento"] = 100 * q.area_sem_mapeamento_km2 / (q.area_terra_km2 + q.area_sem_mapeamento_km2)
print("\nMCD64A1 – % do Nordeste sem mapeamento por mês (mediana por mês do ano):")
print(q.groupby(q.index.month).pct_sem_mapeamento.median().round(2).rename(index=dict(enumerate(MESES, 1))).to_string())
print("Meses com > 5% sem mapeamento:", q[q.pct_sem_mapeamento > 5].index.strftime("%Y-%m").tolist()[:20])

# %% [markdown]
# **Leitura:** na quadra chuvosa a nuvem derruba a fração de pixels "bons" do NDVI e da LST justamente quando a
# lavoura de sequeiro está no campo. Consequência para o produto:
# - suavizar e preencher a série temporal (Savitzky–Golay, Whittaker ou harmônicos) antes de extrair fenologia;
# - combinar sensores ópticos (MODIS/VIIRS, HLS, Sentinel-2) com radar (Sentinel-1, NISAR), que atravessa nuvem;
# - mostrar ao usuário um **indicador de confiança** por mês.

# %% [markdown]
# ## 9.4 Estatística descritiva — Ceará e Nordeste

# %%
ndm = carregar("mod13q1_ndvi_mensal_001deg.nc").load()
mk_ce01 = mascara(ndm.lat.values, ndm.lon.values, CE)
etd = carregar("mod16a3gf_et_ceara_0005deg.nc").load()
mk_ce005 = mascara(etd.lat.values, etd.lon.values, CE)
rng = np.random.default_rng(0)


def amostra(da, mk_, n=2_000_000):
    a = np.asarray(da.values)[:, mk_]
    a = a[np.isfinite(a)]
    return rng.choice(a, size=min(n, a.size), replace=False) if a.size else a


linhas = [descr(amostra(ndm.ndvi, mk_ce01), "NDVI mensal (CE)"),
          descr(amostra(ndm.evi, mk_ce01), "EVI mensal (CE)"),
          descr(amostra(lstm.lst_dia, mk_ce01), "LST dia mensal °C (CE)"),
          descr(amostra(lstm.lst_noite, mk_ce01), "LST noite mensal °C (CE)"),
          descr(amostra(etd.et, mk_ce005), "ET anual mm (CE)"),
          descr(amostra(etd.pet, mk_ce005), "PET anual mm (CE)"),
          descr(amostra(etd.pet - etd.et, mk_ce005), "Déficit PET−ET anual mm (CE)")]
ndne = carregar("mod13a1_ndvi_nordeste_005deg.nc")
ndne = ndne.load() if ndne is not None else None
if ndne is not None:
    mk_ne05 = mascara(ndne.lat.values, ndne.lon.values, NE)
    linhas.append(descr(amostra(ndne.ndvi, mk_ne05), "NDVI 16 dias (NE, 0,05°)"))
fq = carregar("mcd64a1_frac_queimada_nordeste_005deg.nc").load()
mk_ne05b = mascara(fq.lat.values, fq.lon.values, NE)
linhas.append(descr(amostra(fq.frac_queimada * 100, mk_ne05b), "% queimado no mês por célula 0,05° (NE)"))
tabd = pd.DataFrame(linhas)
print(tabd.round(3).to_string(index=False))

# %%
fig, axs = plt.subplots(1, 3, figsize=(15, 3.6))
mm = ndm.time.dt.month
for meses, cor, rot in ((CHUVOSA, "tab:green", "quadra chuvosa (fev–mai)"), (SECA, "tab:brown", "seca (ago–nov)")):
    x = amostra(ndm.ndvi.sel(time=mm.isin(meses)), mk_ce01, 500_000)
    axs[0].hist(x, bins=80, alpha=0.55, density=True, color=cor, label=f"{rot}: média {x.mean():.2f}")
axs[0].set_title("Distribuição do NDVI no Ceará")
axs[0].legend()
for meses, cor, rot in ((CHUVOSA, "tab:green", "chuvosa"), (SECA, "tab:red", "seca")):
    x = amostra(lstm.lst_dia.sel(time=lstm.time.dt.month.isin(meses)), mk_ce01, 500_000)
    axs[1].hist(x, bins=80, alpha=0.55, density=True, color=cor, label=f"{rot}: média {x.mean():.1f} °C")
axs[1].set_title("LST dia (~10h30) no Ceará")
axs[1].legend()
x = amostra(etd.et, mk_ce005, 500_000)
y = amostra(etd.pet, mk_ce005, 500_000)
axs[2].hist(x, bins=80, alpha=0.6, density=True, label=f"ET real: média {x.mean():.0f} mm")
axs[2].hist(y, bins=80, alpha=0.6, density=True, label=f"ET potencial: média {y.mean():.0f} mm")
axs[2].set_title("MOD16A3GF anual no Ceará")
axs[2].legend()
plt.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(2, 3, figsize=(16, 9))
nd_media = ndm.ndvi.mean("time").where(mk_ce01)
nd_cv = (ndm.ndvi.std("time") / ndm.ndvi.mean("time")).where(mk_ce01)
mapa(nd_media, "NDVI médio 2000–2026", axs[0, 0], "YlGn", 0.2, 0.8)
mapa(nd_cv, "Coef. de variação temporal do NDVI", axs[0, 1], "magma_r", 0.1, 0.6)
mapa(lstm.lst_dia.mean("time").where(mk_ce01), "LST dia média (°C)", axs[0, 2], "inferno", 28, 42)
mapa(etd.et.mean("time").where(mk_ce005), "ET real média (mm/ano)", axs[1, 0], "Blues", 300, 1300)
mapa((etd.pet - etd.et).mean("time").where(mk_ce005), "Déficit hídrico PET−ET (mm/ano)", axs[1, 1], "Reds", 1000, 2400)
mapa((lstm.lst_dia - lstm.lst_noite).mean("time").where(mk_ce01), "Amplitude térmica dia−noite (°C)", axs[1, 2], "coolwarm", 8, 22)
plt.tight_layout()
plt.show()

# %%
fig, axs = plt.subplots(1, 3, figsize=(17, 5))
qa = carregar("mcd64a1_queimado_anual_nordeste_0005deg.nc").load()
anos_q = qa.ano.values
freq = qa.queimado.sum("ano")
mk_nef = mascara(qa.lat.values, qa.lon.values, NE)
mapa(freq.where(mk_nef & (freq > 0)), f"Nº de anos com queima ({anos_q.min()}–{anos_q.max()})", axs[0], "hot_r", 1, 12, NE)
if ndne is not None:
    mapa(ndne.ndvi.mean("time").where(mk_ne05), "NDVI médio Nordeste (MOD13A1)", axs[1], "YlGn", 0.2, 0.85, NE)
fogo_uf["ano"] = fogo_uf.data.dt.year
anual_uf = fogo_uf[(fogo_uf.ano >= 2001) & (fogo_uf.ano <= 2025)].groupby(["ano", "uf"]).area_queimada_km2.sum().unstack()
anual_uf.columns = [UF_NOME[c] for c in anual_uf.columns]
area_uf = NE.to_crs(5880).area / 1e6
area_uf.index = NE.sigla
pct = (anual_uf.mean() / area_uf[anual_uf.columns] * 100).sort_values()
axs[2].barh(pct.index, pct.values, color=["tab:red" if k == "CE" else "tab:gray" for k in pct.index])
axs[2].set_title("Área queimada média anual (% da UF), 2001–2025")
plt.tight_layout()
plt.show()
print("Área queimada anual média por UF (km²):")
print(anual_uf.mean().round(0).sort_values(ascending=False).to_string())

viirs = pd.read_parquet(V / "firms_viirs_snpp_nordeste.parquet", columns=["latitude", "longitude", "acq_date", "frp", "type", "uf", "confidence"])
viirs = viirs[viirs["type"] == 0]
viirs["ano"] = viirs.acq_date.dt.year
viirs["mes"] = viirs.acq_date.dt.month
print("\nFIRMS VIIRS (vegetação, type=0) – focos por ano e UF:")
print(viirs.groupby(["ano", "uf"]).size().unstack().rename(columns=UF_NOME).to_string())
print("\nFRP (MW) – estatística descritiva no Nordeste:")
print(descr(viirs.frp, "FRP VIIRS (MW)"))

# %% [markdown]
# ## 9.5 Sazonalidade — o calendário do campo no Ceará

# %%
fig, axs = plt.subplots(1, 3, figsize=(16, 4))
for v, cor in (("ndvi", "tab:green"), ("evi", "tab:olive")):
    s = ce_m[ce_m.variavel == v].groupby("mes").valor
    axs[0].plot(range(1, 13), s.mean(), "-o", color=cor, label=v.upper())
    axs[0].fill_between(range(1, 13), s.quantile(0.1), s.quantile(0.9), color=cor, alpha=0.15)
axs[0].axvspan(1.5, 5.5, color="tab:blue", alpha=0.08, label="quadra chuvosa")
axs[0].set_xticks(range(1, 13), MESES)
axs[0].set_title("Vegetação no Ceará (média e faixa 10–90%)")
axs[0].legend()
for v, cor in (("lst_dia", "tab:red"), ("lst_noite", "tab:purple")):
    s = ce_m[ce_m.variavel == v].groupby("mes").valor
    axs[1].plot(range(1, 13), s.mean(), "-o", color=cor, label=v)
    axs[1].fill_between(range(1, 13), s.quantile(0.1), s.quantile(0.9), color=cor, alpha=0.15)
axs[1].axvspan(1.5, 5.5, color="tab:blue", alpha=0.08)
axs[1].set_xticks(range(1, 13), MESES)
axs[1].set_title("Temperatura da superfície no Ceará (°C)")
axs[1].legend()
aoi_m = pd.read_parquet(DERIV / "modis_aoi_mensal.parquet")
aoi_m["mes"] = aoi_m.data.dt.month
for nm in AOIS:
    s = aoi_m[(aoi_m.aoi == nm) & (aoi_m.variavel == "ndvi")].groupby("mes").valor.mean()
    axs[2].plot(s.index, s.values, "-o", label=nm)
axs[2].axvspan(1.5, 5.5, color="tab:blue", alpha=0.08)
axs[2].set_xticks(range(1, 13), MESES)
axs[2].set_title("NDVI 250 m nas áreas agrícolas (AOIs)")
axs[2].legend(fontsize=7)
plt.tight_layout()
plt.show()

clim_ce = ce_m[ce_m.variavel.isin(["ndvi", "lst_dia"])].pivot_table(index="mes", columns="variavel", values="valor")
print("Climatologia mensal no Ceará:")
print(clim_ce.round(3).rename(index=dict(enumerate(MESES, 1))).to_string())

# %%
fig, axs = plt.subplots(1, 3, figsize=(16, 4))
fm = fogo_uf.copy()
fm["mes"] = fm.data.dt.month
ne_mes = fm[(fm.ano >= 2001) & (fm.ano <= 2025)].groupby(["ano", "mes"]).area_queimada_km2.sum().groupby("mes").mean()
ce_mes = fm[(fm.uf == 23) & (fm.ano >= 2001) & (fm.ano <= 2025)].groupby(["ano", "mes"]).area_queimada_km2.sum().groupby("mes").mean()
axs[0].bar(range(1, 13), ne_mes.reindex(range(1, 13)).values, color="tab:orange")
axs[0].set_xticks(range(1, 13), MESES)
axs[0].set_title("Área queimada média por mês – Nordeste (km², MCD64A1)")
axs[1].bar(range(1, 13), ce_mes.reindex(range(1, 13)).values, color="tab:red")
axs[1].set_xticks(range(1, 13), MESES)
axs[1].set_title("Área queimada média por mês – Ceará (km²)")
fv_mes = viirs.groupby(["ano", "mes", "uf"]).size().groupby(["mes", "uf"]).mean().unstack().rename(columns=UF_NOME)
fv_mes.plot(ax=axs[2], marker=".")
axs[2].set_xticks(range(1, 13), MESES)
axs[2].set_title("Focos VIIRS médios por mês e UF")
axs[2].legend(fontsize=7, ncol=3)
plt.tight_layout()
plt.show()
print("Pico de área queimada no Ceará:", MESES[int(ce_mes.idxmax()) - 1], "| no Nordeste:", MESES[int(ne_mes.idxmax()) - 1])
print("Fração da área queimada anual do Ceará que ocorre em set–dez:", round(ce_mes.loc[9:12].sum() / ce_mes.sum(), 3))

# %%
fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
mapa(ndm.ndvi.sel(time=ndm.time.dt.month == 4).mean("time").where(mk_ce01), "NDVI médio de abril (auge chuvoso)", axs[0], "YlGn", 0.2, 0.85)
mapa(ndm.ndvi.sel(time=ndm.time.dt.month == 10).mean("time").where(mk_ce01), "NDVI médio de outubro (auge seco)", axs[1], "YlGn", 0.2, 0.85)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 9.6 Tendências — Mann-Kendall + inclinação de Sen
#
# Usamos o teste de Mann-Kendall original (`pymannkendall.original_test`) nas séries anuais regionais e uma versão
# vetorizada (mesma estatística S, sem correção de empates, aceitável para dados contínuos) pixel a pixel.

# %%
anu = carregar("mod13q1_ndvi_anual_001deg.nc").load()
ser = {}
ser["NDVI médio anual CE"] = anu.ndvi.where(mk_ce01).mean(("lat", "lon")).to_series()
ser["NDVI mínimo anual CE"] = anu.ndvi_min.where(mk_ce01).mean(("lat", "lon")).to_series()
ser["EVI médio anual CE"] = anu.evi.where(mk_ce01).mean(("lat", "lon")).to_series()
lsta = lstm.lst_dia.where(mk_ce01).mean(("lat", "lon")).to_series()
lsta = lsta[(lsta.index.year >= 2001) & (lsta.index.year <= 2025)]
ser["LST dia média anual CE"] = lsta.groupby(lsta.index.year).mean()
lstn = lstm.lst_noite.where(mk_ce01).mean(("lat", "lon")).to_series()
lstn = lstn[(lstn.index.year >= 2001) & (lstn.index.year <= 2025)]
ser["LST noite média anual CE"] = lstn.groupby(lstn.index.year).mean()
ets = etd.et.where(mk_ce005).mean(("lat", "lon")).to_series()
ser["ET anual CE"] = ets.groupby(ets.index.year).mean()
pts_ = etd.pet.where(mk_ce005).mean(("lat", "lon")).to_series()
ser["PET anual CE"] = pts_.groupby(pts_.index.year).mean()
ser["Área queimada CE km²"] = fogo_uf[(fogo_uf.uf == 23) & (fogo_uf.ano.between(2001, 2025))].groupby("ano").area_queimada_km2.sum()
ser["Área queimada NE km²"] = fogo_uf[fogo_uf.ano.between(2001, 2025)].groupby("ano").area_queimada_km2.sum()
ser["Focos VIIRS CE"] = viirs[viirs.uf == 23].groupby("ano").size()
ser["Focos VIIRS NE"] = viirs.groupby("ano").size()
fmod = pd.read_parquet(M / "firms_modis_nordeste.parquet", columns=["acq_date", "type", "uf", "frp"])
fmod = fmod[fmod["type"] == 0]
fmod["ano"] = fmod.acq_date.dt.year
ser["Focos MODIS CE (2001–2025)"] = fmod[(fmod.uf == 23) & fmod.ano.between(2001, 2025)].groupby("ano").size()
if ndne is not None:
    nn = ndne.ndvi.where(mk_ne05).mean(("lat", "lon")).to_series()
    nn = nn[(nn.index.year >= 2001) & (nn.index.year <= 2025)]
    ser["NDVI médio anual NE"] = nn.groupby(nn.index.year).mean()
uni = {"LST dia média anual CE": "°C", "LST noite média anual CE": "°C", "ET anual CE": "mm", "PET anual CE": "mm",
       "Área queimada CE km²": "km²", "Área queimada NE km²": "km²"}
tend = mk_tabela(ser, uni)
print(tend.round(4).to_string(index=False))

# %%
cube = anu.ndvi.values.reshape(anu.sizes["year"], -1)[:, mk_ce01.ravel()]
sen, z, p = mk_vetorizado(cube)
mapa_sen = np.full(mk_ce01.size, np.nan, "float32")
mapa_sen[mk_ce01.ravel()] = sen
mapa_p = np.full(mk_ce01.size, np.nan, "float32")
mapa_p[mk_ce01.ravel()] = p
mapa_sen = mapa_sen.reshape(mk_ce01.shape)
mapa_p = mapa_p.reshape(mk_ce01.shape)
lstan = lstm.lst_dia.sel(time=lstm.time.dt.year.isin(range(2001, 2026))).groupby("time.year").mean()
cube2 = lstan.values.reshape(lstan.sizes["year"], -1)[:, mk_ce01.ravel()]
sen2, z2, p2 = mk_vetorizado(cube2)
m2 = np.full(mk_ce01.size, np.nan, "float32")
m2[mk_ce01.ravel()] = sen2
m2 = m2.reshape(mk_ce01.shape)
p2m = np.full(mk_ce01.size, np.nan, "float32")
p2m[mk_ce01.ravel()] = p2
p2m = p2m.reshape(mk_ce01.shape)

fig, axs = plt.subplots(1, 3, figsize=(17, 5))
da_sen = xr.DataArray(mapa_sen * 10, coords={"lat": anu.lat, "lon": anu.lon}, dims=("lat", "lon"))
mapa(da_sen, "Tendência do NDVI anual (Sen, por década)", axs[0], "BrBG", -0.08, 0.08)
yy, xx = np.where(mapa_p < 0.05)
axs[0].scatter(anu.lon.values[xx[::23]], anu.lat.values[yy[::23]], s=0.3, c="k", alpha=0.4)
da2 = xr.DataArray(m2 * 10, coords={"lat": anu.lat, "lon": anu.lon}, dims=("lat", "lon"))
mapa(da2, "Tendência da LST dia anual (°C por década)", axs[1], "RdBu_r", -1.5, 1.5)
for nome, pp, ss in (("NDVI", mapa_p, mapa_sen), ("LST", p2m, m2)):
    v = np.isfinite(pp)
    print(f"{nome}: % pixels com tendência significativa (p<0,05): {100 * np.mean(pp[v] < 0.05):.1f}% | "
          f"positiva {100 * np.mean((pp[v] < 0.05) & (ss[v] > 0)):.1f}% | negativa {100 * np.mean((pp[v] < 0.05) & (ss[v] < 0)):.1f}%")
fa = fq.frac_queimada.sel(time=fq.time.dt.year.isin(range(2001, 2026))).groupby("time.year").sum()
cube3 = fa.values.reshape(fa.sizes["year"], -1)[:, mk_ne05b.ravel()]
sen3, _, p3 = mk_vetorizado(cube3)
m3 = np.full(mk_ne05b.size, np.nan, "float32")
m3[mk_ne05b.ravel()] = sen3 * 10 * 100
mapa(xr.DataArray(m3.reshape(mk_ne05b.shape), coords={"lat": fq.lat, "lon": fq.lon}, dims=("lat", "lon")),
     "Tendência da fração queimada anual (p.p. por década)", axs[2], "PuOr_r", -5, 5, NE)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 9.7 Variabilidade interanual e extremos — a grande seca de 2012–2017

# %%
base = anu.ndvi.sel(year=slice(2001, 2011))
anom = (anu.ndvi - base.mean("year")) / base.std("year")
anom_ce = (ser["NDVI médio anual CE"] - ser["NDVI médio anual CE"].loc[2001:2011].mean()) / ser["NDVI médio anual CE"].loc[2001:2011].std()
fig, axs = plt.subplots(1, 2, figsize=(15, 3.8), gridspec_kw={"width_ratios": [2, 1]})
axs[0].bar(anom_ce.index, anom_ce.values, color=["tab:red" if y in SECA_GRANDE else ("tab:green" if v > 0 else "tab:orange") for y, v in anom_ce.items()])
axs[0].set_title("Anomalia padronizada do NDVI anual do Ceará (base 2001–2011); vermelho = 2012–2017")
axs[0].axhline(0, color="k", lw=0.7)
rank = anom_ce.sort_values()
print("Anos mais secos pelo NDVI (z):", rank.head(6).round(2).to_dict())
print("Anos mais verdes pelo NDVI (z):", rank.tail(4).round(2).to_dict())
q_ce = ser["Área queimada CE km²"]
axs[1].boxplot([q_ce[q_ce.index.isin(SECA_GRANDE)], q_ce[~q_ce.index.isin(SECA_GRANDE)]], tick_labels=["2012–2017", "outros anos"])
axs[1].set_title("Área queimada anual no Ceará (km²)")
plt.tight_layout()
plt.show()
print("Área queimada CE – média 2012–2017:", round(q_ce[q_ce.index.isin(SECA_GRANDE)].mean()), "km² | outros anos:",
      round(q_ce[~q_ce.index.isin(SECA_GRANDE)].mean()), "km²; Mann-Whitney p =",
      round(stats.mannwhitneyu(q_ce[q_ce.index.isin(SECA_GRANDE)], q_ce[~q_ce.index.isin(SECA_GRANDE)]).pvalue, 4))
e_ce = ser["ET anual CE"]
print("ET real CE – média 2012–2017:", round(e_ce[e_ce.index.isin(SECA_GRANDE)].mean()), "mm | outros anos:",
      round(e_ce[~e_ce.index.isin(SECA_GRANDE)].mean()), "mm")

fig, axs = plt.subplots(1, 6, figsize=(20, 3.6))
for ax, y in zip(axs, SECA_GRANDE):
    mapa(anom.sel(year=y).where(mk_ce01), f"z do NDVI {y}", ax, "RdYlGn", -3, 3)
plt.tight_layout()
plt.show()
ano_min = anu.ndvi.where(mk_ce01).idxmin("year")
vc = pd.Series(ano_min.values[mk_ce01]).value_counts(normalize=True).head(6)
print("Ano do menor NDVI anual de cada pixel (fração do estado):", (vc * 100).round(1).to_dict())

# %% [markdown]
# ## 9.8 Análises específicas
# ### 9.8.1 Fenologia por pixel (início, pico, fim e amplitude da estação)
#
# Método: curva climatológica de 23 compostos (2001–2025) por pixel; limiar = mínimo + 50% da amplitude.
# - **Início (SOS):** primeiro composto, a partir do vale, acima do limiar.
# - **Pico (POS):** composto de NDVI máximo.
# - **Fim (EOS):** primeiro composto após o pico abaixo do limiar.

# %%
clim = carregar("mod13q1_ndvi_climatologia_001deg.nc")
C = clim.media.values  # (23, lat, lon)
nslot = C.shape[0]
flat = C.reshape(nslot, -1)
valido = np.isfinite(flat).sum(0) >= 18
flat = np.where(np.isfinite(flat), flat, np.nanmean(flat, axis=0, keepdims=True))
vmin_i = np.nanargmin(np.where(np.isfinite(flat), flat, np.inf), axis=0)
idx = (vmin_i[None, :] + np.arange(nslot)[:, None]) % nslot
rol = np.take_along_axis(flat, idx, axis=0)
amp = rol.max(0) - rol.min(0)
thr = rol.min(0) + 0.5 * amp
pos_r = rol.argmax(0)
acima = rol > thr[None, :]
sos_r = acima.argmax(0)
apos = (np.arange(nslot)[:, None] > pos_r[None, :]) & ~acima
eos_r = np.where(apos.any(0), apos.argmax(0), nslot - 1)
doy = lambda r: ((vmin_i + r) % nslot) * 16 + 1  # noqa: E731
SOS, POS, EOS = doy(sos_r), doy(pos_r), doy(eos_r)
dur = ((eos_r - sos_r) * 16).astype(float)
shape2 = C.shape[1:]
fen = {}
for nome, arr in (("SOS", SOS), ("POS", POS), ("EOS", EOS), ("duracao", dur), ("amplitude", amp)):
    a = np.where(valido & mk_ce01.ravel(), arr, np.nan).astype("float32").reshape(shape2)
    fen[nome] = xr.DataArray(a, coords={"lat": clim.lat, "lon": clim.lon}, dims=("lat", "lon"))
fig, axs = plt.subplots(1, 4, figsize=(19, 4.5))
mapa(fen["SOS"], "Início da estação (dia do ano)", axs[0], "twilight", 1, 365)
mapa(fen["POS"], "Pico (dia do ano)", axs[1], "twilight", 1, 365)
mapa(fen["duracao"], "Duração (dias)", axs[2], "viridis", 30, 250)
mapa(fen["amplitude"], "Amplitude sazonal do NDVI", axs[3], "YlGn", 0.05, 0.5)
plt.tight_layout()
plt.show()
for nome in ("SOS", "POS", "EOS", "duracao", "amplitude"):
    v = fen[nome].values[np.isfinite(fen[nome].values)]
    print(f"{nome}: mediana {np.median(v):.0f} | p10 {np.percentile(v, 10):.0f} | p90 {np.percentile(v, 90):.0f}" if nome != "amplitude"
          else f"{nome}: mediana {np.median(v):.3f} | p10 {np.percentile(v, 10):.3f} | p90 {np.percentile(v, 90):.3f}")
med_pos = int(np.nanmedian(fen["POS"].values))
print("Mês típico do pico:", MESES[(pd.Timestamp("2021-01-01") + pd.Timedelta(days=med_pos - 1)).month - 1])

# %% [markdown]
# ### 9.8.2 Janelas de solo nu / vegetação rala nas AOIs (NDVI < 0,25 a 250 m)

# %%
fig, axs = plt.subplots(1, len(AOIS), figsize=(19, 4))
for ax, nm in zip(axs, AOIS):
    a = aoi_m[(aoi_m.aoi == nm) & (aoi_m.variavel == "frac_solo_nu_ndvi_lt_025")].copy()
    a["ano"] = a.data.dt.year
    hm = a.pivot_table(index="ano", columns="mes", values="valor")
    im = ax.imshow(hm.values * 100, aspect="auto", cmap="YlOrBr", vmin=0, vmax=60)
    ax.set_xticks(range(12), [m[0] for m in MESES])
    ax.set_yticks(range(0, len(hm.index), 4), hm.index[::4])
    ax.set_title(f"{nm}\n% da AOI com NDVI<0,25")
    ax.grid(False)
plt.colorbar(im, ax=axs, shrink=0.8)
plt.show()
sn = aoi_m[aoi_m.variavel == "frac_solo_nu_ndvi_lt_025"].groupby(["aoi", "mes"]).valor.mean().unstack() * 100
sn.columns = MESES
print("% médio da AOI com NDVI < 0,25 por mês:")
print(sn.round(1).to_string())

# %% [markdown]
# ### 9.8.3 Resposta do NDVI à chuva e à umidade do solo, com defasagem
# Usa as séries mensais do Ceará produzidas pelas outras frentes em `dados/derivados/`. Ordem de preferência para a
# chuva: IMERG (`precip_total`), depois POWER (`PRECTOTCORR`), depois ERA5 (`tp`). Fica a que tiver mais meses em comum
# com o NDVI. A umidade do solo da zona da raiz vem do POWER (`GWETROOT`, MERRA-2). As correlações são calculadas
# sobre **anomalias** (cada mês menos a média daquele mês do ano), para não confundir a resposta com o ciclo sazonal.

# %%
nd_ce = ce_m[ce_m.variavel == "ndvi"].set_index("data").valor.sort_index()


def serie_derivada(arquivo, variavel):
    p = DERIV / arquivo
    if not p.exists():
        return None
    d = pd.read_parquet(p).dropna(subset=["valor"])
    d = d[d.variavel == variavel]
    if d.empty:
        return None
    s = d.groupby(pd.to_datetime(d.data).dt.to_period("M").dt.to_timestamp()).valor.mean().sort_index()
    return s


candidatas = [("imerg_ce_mensal.parquet", "precip_total"), ("power_ce_mensal.parquet", "PRECTOTCORR"),
              ("era5_ce_mensal.parquet", "tp")]
melhor = None
for arq, var in candidatas:
    s = serie_derivada(arq, var)
    if s is None:
        continue
    n_comum = len(pd.concat([nd_ce, s], axis=1).dropna())
    print(f"candidata {arq}/{var}: {s.index.min():%Y-%m}–{s.index.max():%Y-%m}, {n_comum} meses em comum com o NDVI")
    if melhor is None or n_comum > melhor[2] + 24:
        melhor = (f"{arq}/{var}", s, n_comum)


def anomalia(s):
    return s.groupby(s.index.month).transform(lambda x: x - x.mean())


if melhor is None:
    print("Nenhuma série de precipitação em derivados/ — rode de novo depois das frentes POWER/IMERG.")
else:
    nome_p, prec, _ = melhor
    print("Precipitação usada:", nome_p)
    j = pd.concat({"ndvi": nd_ce, "prec": prec}, axis=1).dropna()
    an = j.apply(anomalia)
    res = pd.DataFrame([{"defasagem_meses": lag, "r_bruto": j.ndvi.corr(j.prec.shift(lag)),
                         "r_anomalias": an.ndvi.corr(an.prec.shift(lag))} for lag in range(0, 5)])
    print(res.round(3).to_string(index=False))
    acum = {k: an.ndvi.corr(anomalia(j.prec.rolling(k).sum()).reindex(an.index)) for k in (1, 2, 3, 4, 6)}
    print("r(anomalia NDVI, anomalia da chuva acumulada nos k meses anteriores):", {k: round(v, 3) for k, v in acum.items()})
    sm = serie_derivada("power_ce_mensal.parquet", "GWETROOT")
    res_sm = None
    if sm is not None:
        js = pd.concat({"ndvi": nd_ce, "sm": sm}, axis=1).dropna().apply(anomalia)
        res_sm = pd.DataFrame([{"defasagem_meses": lag, "r_anomalias": js.ndvi.corr(js.sm.shift(lag))} for lag in range(0, 5)])
        print("NDVI × umidade da zona da raiz (POWER GWETROOT), anomalias:")
        print(res_sm.round(3).to_string(index=False))
    fig, axs = plt.subplots(1, 2, figsize=(13, 3.4))
    axs[0].bar(res.defasagem_meses - 0.2, res.r_anomalias, 0.4, label="chuva (" + nome_p.split(".")[0] + ")")
    if res_sm is not None:
        axs[0].bar(res_sm.defasagem_meses + 0.2, res_sm.r_anomalias, 0.4, label="umidade raiz (POWER)")
    axs[0].set_title("r entre anomalias: NDVI(t) × fator(t − defasagem), Ceará")
    axs[0].set_xlabel("defasagem (meses)")
    axs[0].legend()
    anual = j.groupby(j.index.year).agg(ndvi=("ndvi", "mean"), prec=("prec", "sum"))
    anual = anual[(anual.index >= 2001) & (anual.index <= 2025)]
    axs[1].scatter(anual.prec, anual.ndvi, c=["tab:red" if y in SECA_GRANDE else "tab:green" for y in anual.index])
    for y, r_ in anual.iterrows():
        axs[1].annotate(str(y)[2:], (r_.prec, r_.ndvi), fontsize=7)
    rr_ = np.corrcoef(anual.prec, anual.ndvi)[0, 1]
    axs[1].set_title(f"Ano a ano: chuva anual × NDVI médio (r = {rr_:.2f}); vermelho = 2012–2017")
    axs[1].set_xlabel("chuva anual (mm)")
    axs[1].set_ylabel("NDVI médio")
    plt.tight_layout()
    plt.show()
    print(f"r anual chuva × NDVI = {rr_:.3f} (n = {len(anual)})")

# %% [markdown]
# ### 9.8.4 Fogo × cobertura do solo — lavoura ou Caatinga?

# %%
lc = carregar("esa_cci_lc_2020_nordeste_300m.nc")
# No semiárido, o ESA CCI chama a Caatinga arbórea de "floresta decídua" (classes 60–62): separamos.
GR = {"Lavoura": [10, 11, 12, 20, 30], "Mosaico veg.+lavoura": [40], "Floresta perene/mista": [50, 70, 71, 72, 80, 81, 82, 90],
      "Floresta decídua (Caatinga arbórea/Cerrado)": [60, 61, 62],
      "Arbustiva/Caatinga": [100, 110, 120, 121, 122], "Campo/herbácea": [130, 140, 150, 151, 152, 153],
      "Alagado": [160, 170, 180], "Urbano": [190], "Solo exposto": [200, 201, 202], "Água": [210]}
mapa_gr = {c: g for g, cs in GR.items() for c in cs}
lcv = lc.lccs_class.values
la0, lo0 = float(lc.lat[0]), float(lc.lon[0])
rlc = abs(float(lc.lat[1] - lc.lat[0]))


def classe_em(lat, lon):
    i = np.clip(np.round((la0 - lat) / rlc).astype(int), 0, lcv.shape[0] - 1)
    j = np.clip(np.round((lon - lo0) / rlc).astype(int), 0, lcv.shape[1] - 1)
    return lcv[i, j]


vz = viirs.copy()
vz["lc"] = classe_em(vz.latitude.values, vz.longitude.values)
vz["grupo"] = vz.lc.map(mapa_gr).fillna("outros")
dist_focos = vz.groupby("grupo").size() / len(vz) * 100
mk_lc = mascara(lc.lat.values, lc.lon.values, NE)
cls_area = pd.Series(lcv[mk_lc]).map(mapa_gr).fillna("outros").value_counts(normalize=True) * 100
LAT2, LON2 = np.meshgrid(qa.lat.values, qa.lon.values, indexing="ij")
cl_q = classe_em(LAT2[mk_nef], LON2[mk_nef])
gq = pd.Series(cl_q).map(mapa_gr).fillna("outros")
queim_media = qa.queimado.mean("ano").values[mk_nef]
taxa = pd.DataFrame({"grupo": gq.values, "q": queim_media}).groupby("grupo").q.mean() * 100
comp = pd.DataFrame({"% da área do NE": cls_area, "% dos focos VIIRS": dist_focos,
                     "% da classe queimada por ano (MCD64A1)": taxa}).round(2).sort_values("% da área do NE", ascending=False)
print(comp.to_string())
vce = vz[vz.uf == 23]
area_foco = pd.DataFrame({"area_queimada_km2_2012_2025": fogo_uf[fogo_uf.ano.between(2012, 2025)].groupby("uf").area_queimada_km2.sum(),
                          "focos_viirs_2012_2025": viirs[viirs.ano.between(2012, 2025)].groupby("uf").size()})
area_foco["km2_por_foco"] = area_foco.area_queimada_km2_2012_2025 / area_foco.focos_viirs_2012_2025
area_foco.index = area_foco.index.map(UF_NOME)
print("Área queimada (MCD64A1, 500 m) por foco ativo (VIIRS, 375 m) – quanto menor, menores as queimadas:")
print(area_foco.round(3).sort_values("km2_por_foco").to_string())
print("\nCeará – % dos focos VIIRS por classe:", (vce.groupby("grupo").size() / len(vce) * 100).round(1).sort_values(ascending=False).to_dict())
fig, ax = plt.subplots(figsize=(9, 3.5))
comp[["% da área do NE", "% dos focos VIIRS"]].plot.bar(ax=ax)
ax.set_title("Onde o fogo acontece no Nordeste (ESA CCI LC 2020 × focos VIIRS 2012–2025)")
plt.xticks(rotation=30, ha="right")
plt.show()

# %% [markdown]
# ### 9.8.5 Temperatura da superfície × NDVI — estresse térmico e índice TVDI
#
# No espaço LST × NDVI, pixels secos ficam na "borda quente" e pixels bem supridos de água na "borda fria". O
# **TVDI** (*Temperature–Vegetation Dryness Index*) = (LST − LST_fria(NDVI)) / (LST_quente(NDVI) − LST_fria(NDVI))
# é um indicador de umidade do solo a 1 km que só usa NDVI e LST (MODIS/VIIRS), portanto **global**.

# %%
nd_al, ls_al = xr.align(ndm.ndvi, lstm.lst_dia, join="inner")
corr_mes = []
for m in range(1, 13):
    sel = nd_al.time.dt.month == m
    a = nd_al.sel(time=sel).values[:, mk_ce01].ravel()
    b = ls_al.sel(time=sel).values[:, mk_ce01].ravel()
    ok = np.isfinite(a) & np.isfinite(b)
    corr_mes.append(np.corrcoef(a[ok], b[ok])[0, 1] if ok.sum() > 100 else np.nan)
print("Correlação de Pearson NDVI × LST dia por mês (pixels do Ceará):", dict(zip(MESES, np.round(corr_mes, 2))))


def tvdi(nd, ls, nb=30):
    ok = np.isfinite(nd) & np.isfinite(ls)
    bins = np.linspace(0.1, 0.9, nb + 1)
    c, lmax, lmin = [], [], []
    for k in range(nb):
        s = ok & (nd >= bins[k]) & (nd < bins[k + 1])
        if s.sum() > 50:
            c.append((bins[k] + bins[k + 1]) / 2)
            lmax.append(np.percentile(ls[s], 99))
            lmin.append(np.percentile(ls[s], 1))
    c, lmax, lmin = map(np.array, (c, lmax, lmin))
    aq, bq = np.polyfit(c, lmax, 1)
    af, bf = np.polyfit(c, lmin, 1)
    t = (ls - (af * nd + bf)) / ((aq * nd + bq) - (af * nd + bf))
    return np.clip(t, 0, 1), (aq, bq, af, bf), (c, lmax, lmin)


fig, axs = plt.subplots(1, 4, figsize=(20, 4.3))
casos = [("2009-04", "abril/2009 (ano chuvoso)"), ("2012-10", "outubro/2012 (seca)")]
for k, (mes, rot) in enumerate(casos):
    nd2 = nd_al.sel(time=mes).squeeze().values
    ls2 = ls_al.sel(time=mes).squeeze().values
    nd2 = np.where(mk_ce01, nd2, np.nan)
    ls2 = np.where(mk_ce01, ls2, np.nan)
    tv, coef, pts_e = tvdi(nd2, ls2)
    ok = np.isfinite(nd2) & np.isfinite(ls2)
    axs[2 * k].hexbin(nd2[ok], ls2[ok], gridsize=60, bins="log", cmap="viridis")
    xs = np.linspace(0.1, 0.9, 10)
    axs[2 * k].plot(xs, coef[0] * xs + coef[1], "r-", label="borda quente")
    axs[2 * k].plot(xs, coef[2] * xs + coef[3], "b-", label="borda fria")
    axs[2 * k].set_xlabel("NDVI")
    axs[2 * k].set_ylabel("LST dia (°C)")
    axs[2 * k].set_title(f"Espaço LST×NDVI – {rot}")
    axs[2 * k].legend(fontsize=7)
    mapa(xr.DataArray(tv, coords={"lat": ndm.lat, "lon": ndm.lon}, dims=("lat", "lon")), f"TVDI – {rot}", axs[2 * k + 1], "RdYlBu_r", 0, 1)
    print(f"{rot}: TVDI médio no Ceará = {np.nanmean(tv):.3f}; inclinação da borda quente = {coef[0]:.1f} °C por unidade de NDVI")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 9.9 Insights e ideias para o produto
#
# Os números abaixo saíram das células acima, executadas em 13/11/2026 sobre os dados baixados.
#
# **Cobertura global (veredito):** NDVI/EVI (MOD13), LST (MOD11), área queimada (MCD64A1) e focos FIRMS são
# **globais sobre terra**: 294, 317 e 268 tiles por período, com valores válidos em 14 pontos de 6 continentes. O ET
# (MOD16) é global, mas deixa urbano, água e solo nu sem valor por desenho. Riscos para o produto mundial:
# - Terra e Aqua estão em fim de vida. Há buraco de **26/06 a 17/11/2025** no NDVI e na LST do Terra no catálogo, e a
#   deriva orbital contamina tendências da LST diurna.
# - O catálogo do Planetary Computer tem lacunas pontuais: MCD64A1 de jul/2024 com 46 tiles e de nov/2024 com 48% do NE.
# - A continuidade está no **VIIRS**: o NDVI VNP13 exige Earthdata Login; os focos FIRMS são abertos.
#
# ### Insights mais fortes
# 1. **O calendário agrícola do Ceará é curto e bem definido.** Início da estação no dia 33 (~2 fev); pico no
#    dia 113 (~23 abr); fim no dia 209 (~28 jul); duração mediana de 176 dias. O NDVI estadual vai de 0,37 (out) a
#    0,76 (abr). No auge seco, o Sertão Central cai a 0,34 e o Apodi a 0,39; a Ibiapaba segura 0,55. A janela de
#    **solo exposto** vai de set a jan: Apodi chega a 10% da área com NDVI < 0,25 em dezembro; Sertão Central a 6,5%.
#    *Uso no produto:* é a janela para plantas de cobertura ou forrageiras nas áreas irrigadas e para manter palhada
#    no sequeiro.
# 2. **A vegetação responde à chuva com 1 mês de atraso e tem "memória" de 3–4 meses.**
#    - NDVI(t) × chuva IMERG(t−1): r = 0,84 nos dados brutos e 0,49 nas anomalias.
#    - Com a chuva acumulada em 4 meses, r = 0,60.
#    - Com a umidade da zona da raiz (POWER/MERRA-2) no mesmo mês, r = 0,51.
#    - Ano a ano, chuva × NDVI: r = 0,65.
#    *Uso:* prever vigor e estresse com 1–2 meses de antecedência a partir de IMERG + SMAP + índices de ENSO e do Atlântico.
# 3. **A seca de 2012–2017 é o maior sinal da série de 25 anos.** 2012 foi o pior ano (z = −2,57 no NDVI anual) e é o
#    ano de menor NDVI em 37,6% do estado. A ET real caiu de 959 para 748 mm/ano (−22%). Os anos mais verdes foram 2025
#    (z = +2,39), 2022, 2011 e 2009. *Uso:* mostrar ao agricultor o "ano típico" e o "ano de seca" de cada rotação
#    proposta, com o histórico real do pixel.
# 4. **No Ceará o fogo é pequeno, frequente e anterior ao plantio.**
#    - São ~22 mil focos VIIRS por ano (15–30 mil); 72% caem em out–dez e 88% da área queimada fica em set–dez.
#    - Cada foco VIIRS corresponde a só 0,016 km² de área queimada no MCD64A1, 7–8× menos que no MA, PI e BA.
#      O produto de 500 m **não enxerga** as queimadas do Ceará; o sensor certo é o VIIRS de 375 m, mais
#      Sentinel-2/HLS para as cicatrizes.
#    - 62% dos focos caem em Caatinga (arbórea 42% + arbustiva 20%), 14% em lavoura e 8% em mosaico. É a assinatura
#      do **roçado com queima** (agricultura itinerante) e da limpeza de pasto.
#    - A tendência dos focos no Ceará é +29%/década, mas com p = 0,08 (sinal fraco).
#    *Uso:* alerta de "risco de queima pré-plantio" e recomendação de alternativas (palhada, plantio direto,
#    leguminosa de cobertura), que conversam diretamente com saúde do solo e rotação.
# 5. **LST × NDVI dá um índice de secura a 1 km que funciona no mundo todo.** A correlação é negativa em todos os
#    meses (r de −0,56 a −0,77), mais fraca em abril, quando a água não limita. O TVDI médio do Ceará vai de 0,54
#    (abr/2009, chuvoso) a 0,75 (out/2012, seca), e a borda quente fica 5× mais íngreme na seca. *Uso:* camada de
#    estresse hídrico mais fina que o SMAP (9 km), calculável só com MODIS/VIIRS.
#
# ### Outros achados
# - **O déficit hídrico é o fator dominante:** ET potencial de 2.563 mm/ano contra ET real de 910 mm/ano, ou seja,
#   déficit de ~1.650 mm. Rotação e consórcio precisam ser escolhidos pelo balanço hídrico; irrigação só onde há água
#   (cruzar com GRACE e outorgas).
# - **Tendências:** 23,8% dos pixels têm tendência positiva significativa do NDVI (esverdeamento), contra 1% negativa,
#   mas a média estadual não é significativa (+3,7%/década, p = 0,18). A LST **noturna** sobe +0,33 °C/década
#   (p = 0,016). A LST **diurna** "cai" em 23,8% dos pixels, o que provavelmente é artefato da deriva orbital do
#   Terra; não usar a LST diurna do Terra para tendência. No Nordeste inteiro (MOD13A1, 0,05°), o NDVI médio é 0,59,
#   também sem tendência significativa (+1,8%/década, p = 0,27).
# - **Nuvem:** só 60–67% dos pixels de NDVI são de boa qualidade em jan–mar, contra 96–99% em jun–out. O produto
#   precisa de suavização temporal, fusão com radar (Sentinel-1/NISAR) e um indicador de confiança por mês.
# - **Fogo no Nordeste:** MA, PI e BA, no Cerrado, concentram 95% da área queimada (média de 17,5, 10,9 e 10,6 mil
#   km²/ano). O pico regional é em setembro; o do Ceará, em outubro–novembro. A seca de 2012–2017 **não** aumentou a
#   área queimada no Ceará (244 contra 407 km²/ano; p = 0,18). Hipótese: em seca há menos biomassa e menos roçado
#   plantado.
#
# ### Ideias de modelos para implementar
# - **Fenologia por talhão:** suavização Whittaker ou Savitzky–Golay, e depois detecção de início, pico e fim. Usar
#   HLS a 30 m para o talhão e MODIS para o histórico desde 2000. Fora dos EUA, isso substitui o CDL para descobrir
#   a "rotação atual" e as janelas de solo nu.
# - **Previsão de NDVI/estresse 1–3 meses à frente:**
#   - entradas: chuva acumulada (IMERG), umidade (SMAP, POWER GWETROOT), LST, TVDI e índices climáticos;
#   - modelos: gradient boosting com defasagens, LSTM ou Temporal Fusion Transformer por pixel, ConvLSTM para mapas;
#   - validação: por ano, deixando 2012–2017 fora do treino como teste de estresse.
# - **Classificador "queima agrícola × vegetação nativa":** foco VIIRS + NDVI antes e depois + cobertura do solo.
#   Saída: alerta e recomendação de manejo de palhada.
# - **Camada global de estresse hídrico (TVDI/ESI) a 1 km**, harmonizando MODIS (2000–2025) e VIIRS (2012–) no
#   período comum (regressão ou mapeamento de quantis), para que o sistema seja agnóstico ao sensor.
