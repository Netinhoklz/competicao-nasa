# %% [markdown]
# # 10. SRTM / NASADEM: relevo (NASA)
#
# **O que é:** o modelo digital de elevação da missão Shuttle Radar Topography (fevereiro de 2000), reprocessado pela
# NASA como **NASADEM** em 2020 (melhor controle de altura e vazios preenchidos). A resolução é de 1 arcsegundo (~30 m).
# É uma foto única do relevo: não tem série temporal, mas é a base de **declividade, escoamento, erosão e microclima**.
#
# **Como baixamos:** Planetary Computer (`nasadem`, tiles de 1°, COG):
# - mosaico do Ceará a 30 m;
# - derivados a 90 m: declividade, aspecto e TPI (posição topográfica) a 1 e 5 km;
# - hidrologia a 270 m: preenchimento de depressões (*priority-flood*), fluxo D8, área de contribuição, **TWI** e fator
#   **LS da RUSLE**;
# - as mesmas camadas a 30 m em cada AOI;
# - Nordeste a ~1 km.
#
# Validação global por contagem de tiles contra as células de terra (Natural Earth), comparando com o Copernicus
# DEM GLO-30.

# %%
import json
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import xarray as xr
from rasterio.features import rasterize
from comum import AOIS, DADOS, ceara_gdf, nordeste_gdf, paises_gdf

pd.set_option("display.width", 200)
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})
D = DADOS / "srtm"
man = json.loads((D / "MANIFESTO.json").read_text(encoding="utf-8")) if (D / "MANIFESTO.json").exists() else {}

def ler_tif(nome):
    with rasterio.open(D / nome) as src:
        a = src.read(1).astype(np.float32); t = src.transform; nd = src.nodata
    if nd is not None and not np.isnan(nd):
        a[a == nd] = np.nan
    ext = [t.c, t.c + t.a * a.shape[1], t.f + t.e * a.shape[0], t.f]
    return a, t, ext

z90, t90, ext90 = ler_tif("nasadem_ceara_90m.tif")
s90, _, _ = ler_tif("declividade_ceara_90m.tif")
asp90, _, _ = ler_tif("aspecto_ceara_90m.tif")
tpi5, _, _ = ler_tif("tpi5km_ceara_90m.tif")
ce = ceara_gdf()
mask_ce = rasterize([(g, 1) for g in ce.geometry], out_shape=z90.shape, transform=t90, fill=0, dtype="uint8").astype(bool)
print("grade 90 m:", z90.shape, "| pixels dentro do Ceará:", int(mask_ce.sum()))

# %% [markdown]
# ## 10.1 Ficha técnica

# %%
pd.DataFrame([
    ("Provedor", "NASA/JPL (NASADEM_HGT v001, reprocessamento de 2020 do SRTM); espelho no Microsoft Planetary Computer"),
    ("Data da medição", "11–22/02/2000 (interferometria de radar banda C a bordo do ônibus espacial Endeavour)"),
    ("Resolução", "1 arcsegundo (~30 m); erro vertical típico de alguns metros, maior em florestas densas e encostas"),
    ("Cobertura declarada", "56°S a 60°N (limite da órbita do ônibus espacial)"),
    ("Acesso", "aberto (LP DAAC pede login Earthdata; o Planetary Computer não)"),
    ("Tamanho local", f"{man.get('tamanho_bytes', 0)/1e9:.2f} GB"),
], columns=["item", "valor"])

# %% [markdown]
# ## 10.2 Validação de cobertura global

# %%
g = pd.read_parquet(D / "srtm_cobertura_global.parquet")
g["faixa"] = (g.lat // 10) * 10
fx = g[g.terra].groupby("faixa").agg(celulas_terra=("terra", "size"), nasadem=("nasadem", "sum"), copdem=("copdem", "sum"))
fx["%NASADEM"] = (100 * fx.nasadem / fx.celulas_terra).round(1); fx["%CopDEM"] = (100 * fx.copdem / fx.celulas_terra).round(1)
fx.index = [f"{int(i)}° a {int(i)+10}°" for i in fx.index]
print(f"Tiles NASADEM: {int(g.nasadem.sum()):,} | tiles Copernicus GLO-30: {int(g.copdem.sum()):,} | células de 1° com terra: {int(g.terra.sum()):,}")
fx

# %%
fig, ax = plt.subplots(figsize=(13, 6))
paises_gdf().plot(ax=ax, color="#f2f2f2", edgecolor="#bbbbbb", lw=0.3)
so_cop = g[g.copdem & ~g.nasadem]; ambos = g[g.nasadem]
ax.scatter(ambos.lon + 0.5, ambos.lat + 0.5, s=0.6, c="tab:green", label="NASADEM (e CopDEM)")
ax.scatter(so_cop.lon + 0.5, so_cop.lat + 0.5, s=0.6, c="tab:purple", label="só Copernicus DEM")
ax.axhline(60, color="k", ls="--", lw=0.8); ax.axhline(-56, color="k", ls="--", lw=0.8)
ax.set_xlim(-180, 180); ax.set_ylim(-90, 90); ax.legend(markerscale=12, loc="lower left")
ax.set_title("Tiles de 1° disponíveis: NASADEM (verde) termina em 60°N/56°S; Copernicus DEM (roxo) cobre os polos"); plt.show()

# %% [markdown]
# **Veredito de cobertura:**
# - O NASADEM/SRTM é **quase global**: cobre todas as terras entre 56°S e 60°N, onde está a imensa maioria da
#   agricultura do mundo, inclusive todo o Brasil, a África, a Índia, a China, os EUA e o sul do Canadá.
# - Fica fora o norte do Canadá, da Escandinávia, da Rússia e do Alasca, além da Groenlândia e da Antártida.
# - Para o produto ser 100% global, a solução é usar **Copernicus DEM GLO-30 como reserva** acima de 60°N, ou como
#   base única. Ele também é aberto e cobre os polos.

# %%
dentro = z90[mask_ce]
print(f"Vazios (NaN) dentro do Ceará a 90 m: {np.isnan(dentro).mean()*100:.4f}%  (o NASADEM já vem com vazios preenchidos)")
print(f"Pixels com elevação < 0 m dentro do Ceará: {(dentro < 0).mean()*100:.3f}% (litoral/estuários e ruído do radar)")

# %% [markdown]
# ## 10.3 Estatística descritiva do relevo do Ceará

# %%
zc = dentro[np.isfinite(dentro)]; sc = s90[mask_ce]; sc = sc[np.isfinite(sc)]
desc = pd.Series({"elev_media_m": zc.mean(), "elev_dp_m": zc.std(), "elev_p05": np.percentile(zc, 5), "elev_p50": np.median(zc),
                  "elev_p95": np.percentile(zc, 95), "elev_max": zc.max(), "assimetria": pd.Series(zc).skew(),
                  "% abaixo de 200 m": (zc < 200).mean() * 100, "% acima de 600 m": (zc > 600).mean() * 100,
                  "declividade_media_graus": sc.mean(), "declividade_p90_graus": np.percentile(sc, 90)}).round(2)
desc

# %%
tg = np.tan(np.deg2rad(sc)) * 100
classes = pd.cut(tg, [-1, 3, 8, 20, 45, 75, 1e9], labels=["plano 0–3%", "suave ondulado 3–8%", "ondulado 8–20%", "forte ondulado 20–45%", "montanhoso 45–75%", "escarpado >75%"])
cl = pd.Series(classes).value_counts(normalize=True).sort_index() * 100
fig, axs = plt.subplots(1, 3, figsize=(17, 4))
axs[0].hist(zc, bins=120, color="tab:brown"); axs[0].set_title("Hipsometria do Ceará (90 m)"); axs[0].set_xlabel("m")
axs[1].barh(cl.index.astype(str), cl.values, color="tab:olive"); axs[1].set_title("Classes de declive Embrapa (% da área)")
for i, v in enumerate(cl.values): axs[1].text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=8)
a = asp90[mask_ce & (s90 > 2)]; a = a[np.isfinite(a)]
h, b = np.histogram(a, bins=16, range=(0, 360))
ax = plt.subplot(1, 3, 3, projection="polar"); ax.bar(np.deg2rad(b[:-1] + 11.25), h, width=np.deg2rad(22.5), color="tab:cyan", edgecolor="k")
ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_title("Aspecto das encostas (>2°)")
plt.tight_layout(); plt.show()
print(cl.round(2).to_string())

# %% [markdown]
# ## 10.4 Mapas: relevo, declividade, posição topográfica, umidade (TWI) e erosão (LS)

# %%
h270 = xr.open_dataset(D / "ceara_270m_hidrologia.nc")
ext270 = [float(h270.lon.min()), float(h270.lon.max()), float(h270.lat.min()), float(h270.lat.max())]
locais = {"Ibiapaba": (-40.95, -3.9), "Meruoca": (-40.45, -3.55), "Uruburetama": (-39.55, -3.62), "Baturité": (-38.92, -4.28),
          "Chapada do Araripe": (-39.6, -7.35), "Chapada do Apodi": (-37.95, -5.2), "Fortaleza": (-38.52, -3.73), "Sertão Central": (-39.0, -5.0)}
fig, axs = plt.subplots(2, 3, figsize=(18, 11))
paineis = [(z90, ext90, "terrain", (0, 950), "Elevação (m)"), (s90, ext90, "magma_r", (0, 15), "Declividade (graus)"),
           (tpi5, ext90, "RdBu", (-80, 80), "TPI 5 km (m): <0 baixada, >0 topo"),
           (h270.twi.values, ext270, "Blues", (4, 14), "TWI (270 m): umidade topográfica"),
           (np.log10(h270.ls_rusle.values + 1e-3), ext270, "YlOrRd", (-1.5, 1.2), "log10 LS-RUSLE (270 m)"),
           (np.log10(h270.area_contribuicao_m2.values), ext270, "viridis", (4.8, 9), "log10 área de contribuição (m²)")]
for ax, (img, ext, cm, lim, tit) in zip(axs.ravel(), paineis):
    im = ax.imshow(img, extent=ext, cmap=cm, vmin=lim[0], vmax=lim[1]); ce.boundary.plot(ax=ax, color="k", lw=0.8)
    plt.colorbar(im, ax=ax, fraction=0.04); ax.set_title(tit)
    for nome, (x, y) in locais.items():
        ax.plot(x, y, "k^", ms=4); ax.annotate(nome, (x, y), fontsize=7, xytext=(3, 3), textcoords="offset points")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 10.5–10.7 Sazonalidade, tendência e extremos
# O DEM é uma **medição única (fev/2000)**, então não existe sazonalidade nem tendência temporal para estimar.
# No lugar disso, analisamos os **extremos espaciais** e os gradientes que importam para a lavoura:
# - a declividade, ligada ao risco de erosão e à mecanização;
# - as baixadas, que acumulam água e ar frio;
# - os municípios mais e menos acidentados.

# %%
mun = pd.read_parquet(D / "srtm_municipios_ce.parquet")
cols = ["municipio", "elev_media", "elev_max", "amplitude", "decl_media_graus", "frac_ondulado_8a20", "frac_forte_20a45"]
print("10 municípios mais acidentados (declividade média):")
print(mun.sort_values("decl_media_graus", ascending=False)[cols].head(10).round(3).to_string(index=False))
print("\n10 municípios mais planos:")
print(mun.sort_values("decl_media_graus")[cols].head(10).round(3).to_string(index=False))
ls = h270.ls_rusle.values; twi = h270.twi.values; sl270 = h270.declividade.values
ok = np.isfinite(ls)
print(f"\nÁrea com LS > 3 (potencial de erosão alto em lavoura sem cobertura): {(ls[ok] > 3).mean()*100:.1f}% da grade")
tw = twi[np.isfinite(twi)]
print(f"TWI a 270 m: p10={np.percentile(tw,10):.1f} p50={np.percentile(tw,50):.1f} p90={np.percentile(tw,90):.1f} "
      f"(o TWI depende da resolução: a 270 m a área específica mínima já é ~270 m, então só faz sentido comparar dentro da mesma grade;"
      f" nas AOIs a 30 m a mediana é ~7–8). Baixadas úmidas = decil superior (TWI ≥ {np.percentile(tw,90):.1f}).")
baixada = (tpi5 < -30) & (s90 < 2) & mask_ce
print(f"Baixadas planas encaixadas (TPI5km < −30 m e declive < 2°), candidatas a acumular ar frio à noite: {baixada.sum()/mask_ce.sum()*100:.2f}% do Ceará")

# %%
fig, axs = plt.subplots(1, 2, figsize=(14, 4))
v = ok & np.isfinite(sl270)
axs[0].hexbin(h270.elev.values[v], sl270[v], gridsize=70, bins="log", cmap="viridis"); axs[0].set_xlabel("elevação (m)"); axs[0].set_ylabel("declividade (°)")
axs[0].set_title("Quanto mais alto, mais íngreme: serras × sertão")
lat_idx = np.argmin(np.abs(np.arange(z90.shape[0]) * t90.e + t90.f - (-4.3)))
lons = t90.c + t90.a * (np.arange(z90.shape[1]) + 0.5)
axs[1].plot(lons, z90[lat_idx], color="tab:brown"); axs[1].set_title("Perfil W→E em 4,3°S (Ibiapaba → sertão → Baturité → litoral)")
axs[1].set_xlabel("longitude"); axs[1].set_ylabel("m"); plt.tight_layout(); plt.show()

# %% [markdown]
# ## 10.8 Nordeste a ~1 km

# %%
zne, tne, extne = ler_tif("nasadem_nordeste_1km.tif"); sne, _, _ = ler_tif("declividade_nordeste_1km.tif")
ne = nordeste_gdf()
lab = rasterize([(gg, i + 1) for i, gg in enumerate(ne.geometry)], out_shape=zne.shape, transform=tne, fill=0, dtype="int32")
UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
lin = []
for i, cod in enumerate(ne.codarea.astype(str)):
    m = (lab == i + 1) & np.isfinite(zne)
    lin.append({"UF": UF.get(cod, cod), "elev_media": zne[m].mean(), "elev_p95": np.percentile(zne[m], 95), "decl_media_graus_1km": sne[m].mean(),
                "% > 500 m": (zne[m] > 500).mean() * 100})
fig, ax = plt.subplots(figsize=(9, 9))
im = ax.imshow(zne, extent=extne, cmap="terrain", vmin=0, vmax=1200); ne.boundary.plot(ax=ax, color="k", lw=0.6)
plt.colorbar(im, ax=ax, fraction=0.04, label="m"); ax.set_title("Relevo do Nordeste (NASADEM ~1 km)"); plt.show()
pd.DataFrame(lin).round(1).sort_values("elev_media")

# %% [markdown]
# ## 10.9 AOIs a 30 m

# %%
aoi_tab = pd.read_parquet(D / "srtm_aoi_estatico.parquet").set_index("aoi")
fig, axs = plt.subplots(4, 4, figsize=(15, 15))
for i, n in enumerate(AOIS):
    ds = xr.open_dataset(D / f"srtm_aoi_{n}.nc")
    ext = [float(ds.lon.min()), float(ds.lon.max()), float(ds.lat.min()), float(ds.lat.max())]
    for j, (v, cm, lim) in enumerate([("elev", "terrain", None), ("declividade", "magma_r", (0, 15)), ("twi", "Blues", (4, 14)), ("ls_rusle", "YlOrRd", (0, 6))]):
        arr = ds[v].values
        lo, hi = lim if lim else (np.nanpercentile(arr, 1), np.nanpercentile(arr, 99))
        im = axs[i, j].imshow(arr, extent=ext, cmap=cm, vmin=lo, vmax=hi); plt.colorbar(im, ax=axs[i, j], fraction=0.046)
        axs[i, j].set_title(f"{n} — {v}", fontsize=8); axs[i, j].set_xticks([]); axs[i, j].set_yticks([])
plt.tight_layout(); plt.show()
aoi_tab.round(3).T

# %% [markdown]
# ## 10.10 Insights e ideias para o produto
# 1. **O relevo do Ceará é dominado pelo sertão baixo e plano.** A maior parte da área fica abaixo de 400 m e nas
#    classes plano/suave ondulado (≤ 8%), ótimo para mecanização. Ilhas de relevo concentram declividade, umidade
#    e nuvem: Ibiapaba, Araripe, Baturité, Meruoca e Uruburetama.
# 2. **Erosão é questão de lugar.** O LS alto se concentra nas encostas das serras e nos vales encaixados. Nesses
#    talhões, rotações com cobertura permanente (palhada, perenes, consórcios) rendem mais do que no sertão plano.
#    O produto pode priorizar "cobertura do solo" pelo LS do talhão.
# 3. **O TWI acha as baixadas úmidas.** Várzeas e fundos de vale (TWI alto) acumulam água e são onde culturas mais
#    exigentes, como milho e arroz de várzea, têm chance na seca. Nas áreas de TWI baixo, a escolha vai para culturas
#    tolerantes: sorgo, feijão-caupi, palma.
# 4. **Microclima.** Baixadas encaixadas (TPI negativo e plano) acumulam ar frio à noite. No Ceará isso quase não
#    gera geada, mas a camada é crucial no produto global (Sul do Brasil, Argentina, EUA). Junto com a altitude, ela
#    ajusta a temperatura do POWER/ERA5 (~−6,5 °C/km) para o talhão.
# 5. **A cobertura é quase global.** O NASADEM cobre 56°S–60°N; para fechar os polos, entra o Copernicus DEM. A camada
#    é estática, então basta baixar uma vez por região: é barata e pode ser pré-calculada no servidor.
#
# **Ideias de modelo:**
# - Usar o relevo (declividade, TWI, TPI, aspecto) como **features estáticas** em todos os modelos de estresse e
#   produtividade.
# - **RUSLE completa:**
#   - R a partir da intensidade de chuva do IMERG;
#   - K a partir do solo (SoilGrids/GAEZ);
#   - LS a partir daqui;
#   - C a partir do NDVI do Landsat/S2;
#   - e assim estimar a **perda de solo em t/ha/ano para cada rotação proposta**, comparando cobertura e manejo.
# - **Downscaling** de temperatura e chuva com o relevo (regressão ou CNN do tipo super-resolução).
