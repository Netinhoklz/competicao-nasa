# %% [markdown]
# # 7. Landsat Collection 2 Level-2 (NASA/USGS)
#
# **O que é:** reflectância de superfície (corrigida da atmosfera) dos satélites Landsat 4/5 (TM), 7 (ETM+) e 8/9 (OLI),
# a 30 m, desde 1982. É o **histórico mais longo de imagens de lavoura do planeta**: dá para ver o mesmo talhão desde os anos 80.
#
# **Como baixamos:** Microsoft Planetary Computer (`landsat-c2-l2`), lendo só a janela de cada AOI dentro dos COGs.
# - metadados STAC de **todas** as cenas que tocam o Ceará (1982–hoje);
# - cubos 30 m (vermelho, NIR, SWIR1, NDVI, NDMI) nas 4 AOIs com Landsat 8/9 (2013–hoje);
# - estatísticas por cena nas AOIs com Landsat 4/5/7 (1984–2012), para a série longa das secas.
#
# Máscara de nuvem: bits 0–5 do `QA_PIXEL` (preenchimento, nuvem dilatada, cirro, nuvem, sombra, neve).

# %%
import json
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymannkendall as mk
import xarray as xr
from comum import AOIS, DADOS, paises_gdf
from frente_c_util import mk_sen_vetorizado

pd.set_option("display.width", 200)
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})
D = DADOS / "landsat"
CORES = {"apodi_jaguaribe": "#1f77b4", "cariri": "#d62728", "sertao_central": "#ff7f0e", "ibiapaba": "#2ca02c"}
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

meta = pd.read_parquet(D / "landsat_stac_ceara.parquet")
glob = pd.read_parquet(D / "landsat_stac_global.parquet")
c89 = pd.read_parquet(D / "landsat_aoi_cenas_l89.parquet")
hist = pd.read_parquet(D / "landsat_aoi_cenas_hist.parquet") if (D / "landsat_aoi_cenas_hist.parquet").exists() else pd.DataFrame()
for df in (meta, glob, c89, hist):
    if len(df):
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_localize(None)
man = json.loads((D / "MANIFESTO.json").read_text(encoding="utf-8")) if (D / "MANIFESTO.json").exists() else {}
print(f"cenas no Ceará (STAC): {len(meta):,} | cenas L8/9 nas AOIs: {len(c89):,} | cenas L4/5/7 nas AOIs: {len(hist):,}")

# %% [markdown]
# ## 7.1 Ficha técnica

# %%
ficha = pd.DataFrame([
    ("Provedor", "NASA/USGS; espelho aberto no Microsoft Planetary Computer"),
    ("Produto", "Landsat Collection 2 Level-2 Surface Reflectance (SR) + QA_PIXEL"),
    ("Resolução espacial", "30 m (bandas ópticas); térmica reamostrada para 30 m"),
    ("Revisita nominal", "16 dias por satélite; 8 dias com dois satélites (L8+L9, ou L5+L7)"),
    ("Período", f"{meta.datetime.min():%Y-%m-%d} a {meta.datetime.max():%Y-%m-%d} (cenas que tocam o Ceará)"),
    ("Escala SR", "refl = DN × 0,0000275 − 0,2"),
    ("Acesso", "aberto (USGS EarthExplorer pede login gratuito; o Planetary Computer não pede)"),
    ("Tamanho local", f"{man.get('tamanho_bytes', 0)/1e9:.2f} GB"),
], columns=["item", "valor"])
ficha

# %% [markdown]
# ## 7.2 Validação de cobertura global
# Consultamos o catálogo STAC em **27 caixas de 1°** espalhadas por todos os continentes e faixas de latitude, no ano de 2023.
# - **Revisita efetiva:** mediana do intervalo entre datas distintas de aquisição.
# - **Revisita limpa:** o mesmo intervalo, contando só cenas com menos de 20% de nuvem.

# %%
def resumo_amostra(g):
    g = g.dropna(subset=["id"])
    if g.empty:
        return pd.Series({"cenas": 0, "datas": 0, "revisita_d": np.nan, "revisita_limpa_d": np.nan, "nuvem_mediana": np.nan, "plataformas": ""})
    datas = np.sort(g.datetime.dt.normalize().unique())
    lim = np.sort(g[g.cloud_cover < 20].datetime.dt.normalize().unique())
    gap = lambda d: float(np.median(np.diff(d).astype("timedelta64[D]").astype(int))) if len(d) > 1 else np.nan
    return pd.Series({"cenas": len(g), "datas": len(datas), "revisita_d": gap(datas), "revisita_limpa_d": gap(lim),
                      "nuvem_mediana": g.cloud_cover.median(), "plataformas": ",".join(sorted(g.platform.dropna().unique()))})

cob = glob.groupby(["amostra", "lon", "lat"]).apply(resumo_amostra).reset_index().sort_values("lat", ascending=False)
cob

# %%
fig, ax = plt.subplots(figsize=(12, 5.5))
paises_gdf().plot(ax=ax, color="#eeeeee", edgecolor="#999999", lw=0.4)
sc = ax.scatter(cob.lon, cob.lat, s=20 + cob.cenas * 1.5, c=cob.revisita_limpa_d, cmap="viridis_r", edgecolor="k", vmin=0, vmax=60)
for _, r in cob.iterrows():
    ax.annotate(f"{r.amostra.split('_')[0]}\n{int(r.cenas)}", (r.lon, r.lat), fontsize=6, ha="center", va="bottom", xytext=(0, 6), textcoords="offset points")
plt.colorbar(sc, ax=ax, label="revisita limpa (dias, nuvem<20%)")
ax.set_title("Landsat C2 L2 em 2023: cenas por caixa de 1° (tamanho) e revisita limpa (cor)")
ax.set_xlim(-180, 180); ax.set_ylim(-90, 90)
plt.show()

# %%
lat_ok = cob[cob.cenas > 0]
print("Latitude máxima com cenas L2 em 2023:", lat_ok.lat.max(), "| mínima:", lat_ok.lat.min())
print("Amostras sem nenhuma cena:", ", ".join(cob[cob.cenas == 0].amostra) or "nenhuma")
print(f"Revisita efetiva mediana (todas as amostras com dados): {lat_ok.revisita_d.median():.0f} dias;"
      f" revisita limpa mediana: {lat_ok.revisita_limpa_d.median():.0f} dias")
glob["mes"] = glob.datetime.dt.month
meses_amostra = glob.dropna(subset=["id"]).groupby("amostra").agg(
    meses_com_dados=("mes", lambda s: len(set(s.dropna()))), lista=("mes", lambda s: ",".join(str(int(m)) for m in sorted(set(s.dropna())))),
    pct_T1=("categoria", lambda s: round(100 * (s == "T1").mean(), 1)))
meses_amostra.join(cob.set_index("amostra")[["lat"]]).sort_values("lat", ascending=False)

# %% [markdown]
# **Veredito de cobertura (tirado das tabelas acima):** o Landsat C2 L2 é **global sobre terra**. Todas as 27 caixas,
# do Ártico ao interior da Antártida, têm centenas de cenas em 2023, com dois satélites (L8 + L9) e, em várias
# regiões, ainda o L7. Os limites de verdade são outros três:
# 1. **Iluminação:** acima de ~60° de latitude só há cenas nos meses com Sol alto o bastante (Antártida: out–fev;
#    Svalbard/Groenlândia: mar–set). Entre os trópicos e as latitudes médias, onde está a agricultura, há dados nos
#    12 meses.
# 2. **Qualidade geométrica:** nos polos as cenas são *Tier 2* (sem pontos de controle no solo). Nas regiões agrícolas,
#    como o Ceará, ~95% é *Tier 1*, que é o nível adequado para séries temporais por pixel.
# 3. **Revisita limpa:** depende do clima. É curta em desertos e longa nos trópicos úmidos e nas quadras chuvosas.
#
# Para o produto: funciona em qualquer região agrícola do mundo, mas a expectativa de "quantas imagens úteis por mês"
# tem de ser calibrada pelo clima local, como fazemos abaixo para o Ceará.

# %% [markdown]
# ## 7.3 Qualidade e disponibilidade no Ceará
# ### Quantas cenas existem por ano e por satélite (todas as que tocam o Ceará)

# %%
meta["ano"] = meta.datetime.dt.year
meta["mes"] = meta.datetime.dt.month
tab = meta.pivot_table(index="ano", columns="platform", values="id", aggfunc="count").fillna(0)
ax = tab.plot(kind="bar", stacked=True, figsize=(13, 4), width=0.85, colormap="tab10")
ax.set_title("Cenas Landsat C2 L2 que tocam o Ceará, por ano e satélite"); ax.set_ylabel("cenas"); ax.set_xlabel("")
plt.show()
print("Categoria (T1 = qualidade geométrica para série temporal):")
print(meta.categoria.value_counts(normalize=True).round(3).to_string())
print(f"Pares path/row distintos: {meta.groupby(['path','row']).ngroups}")

# %% [markdown]
# ### Nuvem por mês: quando dá para enxergar o campo

# %%
fig, axs = plt.subplots(1, 2, figsize=(14, 4))
dados_mes = [meta.loc[meta.mes == m, "cloud_cover"].dropna() for m in range(1, 13)]
axs[0].boxplot(dados_mes, tick_labels=MESES, showfliers=False)
axs[0].axvspan(1.5, 5.5, color="tab:blue", alpha=0.08, label="quadra chuvosa (fev–mai)")
axs[0].set_title("Cobertura de nuvem por cena (Ceará, 1982–hoje)"); axs[0].set_ylabel("% nuvem"); axs[0].legend()
p20 = meta.groupby("mes").cloud_cover.apply(lambda s: (s < 20).mean() * 100)
axs[1].bar(MESES, p20.values, color=["tab:blue" if 2 <= m <= 5 else "tab:gray" for m in range(1, 13)])
axs[1].set_title("% das cenas com menos de 20% de nuvem"); axs[1].set_ylabel("%")
plt.tight_layout(); plt.show()
print(p20.round(1).rename(lambda m: MESES[m - 1]).to_string())

# %% [markdown]
# ### Fração de pixels limpos nas AOIs (máscara QA, Landsat 8/9)

# %%
c89["mes"] = c89.datetime.dt.month
c89["ano"] = c89.datetime.dt.year
fv = c89.pivot_table(index="mes", columns="aoi", values="frac_valida", aggfunc="mean")
prob80 = c89.assign(ok=c89.frac_valida >= 0.8).pivot_table(index="mes", columns="aoi", values="ok", aggfunc="mean")
fig, axs = plt.subplots(1, 2, figsize=(14, 4))
for a in fv.columns:
    axs[0].plot(range(1, 13), fv[a], "-o", color=CORES[a], label=a)
    axs[1].plot(range(1, 13), prob80[a] * 100, "-o", color=CORES[a], label=a)
for ax, t in zip(axs, ["fração média de pixels limpos por cena", "% das passagens com ≥80% da AOI limpa"]):
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(MESES); ax.axvspan(1.5, 5.5, color="tab:blue", alpha=0.08); ax.set_title(t)
axs[0].legend(); plt.tight_layout(); plt.show()
n_limpas = c89[c89.frac_valida >= 0.8].groupby(["aoi", "ano"]).size().unstack(0)
print("Passagens úteis (≥80% limpas) por ano e AOI:")
print(n_limpas.fillna(0).astype(int).to_string())

# %% [markdown]
# ## 7.4 Estatística descritiva nas AOIs (pixels, Landsat 8/9, 2013–hoje)

# %%
def abrir_cubo(nome, var="ndvi"):
    ds = xr.open_dataset(D / f"landsat_aoi_{nome}.nc", decode_cf=False)
    a = ds[var].values.astype(np.float32)
    a[a == -32768] = np.nan
    a *= 1e-4
    t = pd.to_datetime(xr.decode_cf(ds[["time"]]).time.values)
    return a, t, ds.x.values, ds.y.values

cubos = {n: abrir_cubo(n) for n in AOIS}
linhas = []
rng = np.random.default_rng(0)
amostras_pix = {}
for n, (a, t, x, y) in cubos.items():
    v = a[np.isfinite(a)]
    amostras_pix[n] = rng.choice(v, size=min(400_000, v.size), replace=False)
    s = pd.Series(amostras_pix[n])
    linhas.append({"aoi": n, "cenas_no_cubo": a.shape[0], "pixels_validos_M": v.size / 1e6,
                   "media": s.mean(), "dp": s.std(), "p05": s.quantile(.05), "p25": s.quantile(.25), "mediana": s.median(),
                   "p75": s.quantile(.75), "p95": s.quantile(.95), "assimetria": s.skew(), "curtose": s.kurt(),
                   "frac_NDVI<0.2 (solo exposto)": (s < 0.2).mean(), "frac_NDVI>0.6 (veg. densa)": (s > 0.6).mean()})
desc = pd.DataFrame(linhas).set_index("aoi").round(3)
desc

# %%
fig, ax = plt.subplots(figsize=(11, 4))
for n, v in amostras_pix.items():
    ax.hist(v, bins=120, range=(-0.2, 1.0), histtype="step", lw=1.6, density=True, color=CORES[n], label=n)
ax.axvline(0.2, color="k", ls=":", lw=1); ax.axvline(0.6, color="k", ls=":", lw=1)
ax.set_title("Distribuição do NDVI por pixel (todas as datas limpas, Landsat 8/9)"); ax.set_xlabel("NDVI"); ax.legend()
plt.show()

# %%
fig, axs = plt.subplots(3, 4, figsize=(16, 11))
for j, (n, (a, t, x, y)) in enumerate(cubos.items()):
    ext = [x.min() / 1e3, x.max() / 1e3, y.min() / 1e3, y.max() / 1e3]
    chuva = np.isin(t.month, [3, 4, 5]); seca = np.isin(t.month, [9, 10, 11])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m_ch = np.nanmedian(a[chuva], axis=0); m_se = np.nanmedian(a[seca], axis=0); dp = np.nanstd(a, axis=0)
    for i, (img, tit, cm, vmin, vmax) in enumerate([(m_ch, "NDVI mediano mar–mai", "YlGn", 0, 0.9),
                                                     (m_se, "NDVI mediano set–nov", "YlGn", 0, 0.9),
                                                     (dp, "desvio-padrão temporal", "magma", 0, 0.3)]):
        im = axs[i, j].imshow(img, extent=ext, cmap=cm, vmin=vmin, vmax=vmax)
        axs[i, j].set_title(f"{n}\n{tit}", fontsize=9); axs[i, j].set_xticks([]); axs[i, j].set_yticks([])
        plt.colorbar(im, ax=axs[i, j], fraction=0.046)
plt.suptitle("Mapas de NDVI por AOI (30 m): chuva × seca × variabilidade", y=1.0); plt.tight_layout(); plt.show()

# %% [markdown]
# **Como ler os mapas:**
# - Na **Chapada do Apodi**, os talhões irrigados aparecem como blocos verdes mesmo na seca (set–nov). O contraste com
#   a Caatinga ao redor é o sinal de irrigação.
# - No **Sertão Central** e no **Cariri**, quase tudo fica marrom na seca. O desvio-padrão alto marca áreas de lavoura e
#   pasto de sequeiro, que respondem forte à chuva.
# - A **Ibiapaba** mantém NDVI mais alto o ano todo, por ser serra úmida, com chuva orográfica e nuvem.

# %% [markdown]
# ## 7.5 Sazonalidade: o calendário do verde

# %%
c89v = c89[c89.frac_valida >= 0.3].copy()
clim = c89v.groupby(["aoi", "mes"]).ndvi_mediana.agg(["median", lambda s: s.quantile(.25), lambda s: s.quantile(.75), "count"])
clim.columns = ["mediana", "q25", "q75", "n"]
fig, axs = plt.subplots(1, 2, figsize=(15, 4.5))
for n in AOIS:
    c = clim.loc[n]
    axs[0].plot(c.index, c.mediana, "-o", color=CORES[n], label=n)
    axs[0].fill_between(c.index, c.q25, c.q75, color=CORES[n], alpha=0.12)
    s = c89v[c89v.aoi == n].groupby("mes").frac_solo_exposto.mean()
    axs[1].plot(s.index, s * 100, "-o", color=CORES[n], label=n)
for ax, t in zip(axs, ["NDVI mediano da AOI por mês (faixa = IQR entre anos/cenas)", "% da AOI com solo exposto (NDVI<0,2)"]):
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(MESES); ax.axvspan(1.5, 5.5, color="tab:blue", alpha=0.08); ax.set_title(t)
axs[0].legend(); plt.tight_layout(); plt.show()
pico = clim.mediana.groupby(level=0).idxmax().apply(lambda x: MESES[x[1] - 1])
vale = clim.mediana.groupby(level=0).idxmin().apply(lambda x: MESES[x[1] - 1])
amp = clim.mediana.groupby(level=0).agg(lambda s: s.max() - s.min())
print(pd.DataFrame({"mes_pico": pico, "mes_vale": vale, "amplitude_NDVI": amp.round(3)}).to_string())

# %% [markdown]
# **Leitura agronômica:**
# - O pico do NDVI vem **depois** do pico da chuva (abr–mai). Isso indica uma defasagem de ~1–2 meses entre a chuva e
#   o verde.
# - O **solo exposto** cresce de agosto a dezembro. É a **janela de campo nu**, exatamente onde o desafio pede para
#   pensar em cobertura do solo e rotação: palhada, consórcio, forrageiras perenes como palma ou capim, ou culturas
#   de ciclo curto no início das chuvas.

# %% [markdown]
# ## 7.6 Tendências (Mann-Kendall + Sen)
# ### Série longa por AOI (1984–hoje; TM/ETM+ e OLI juntos)
# Atenção: o NDVI do OLI é ligeiramente maior que o do TM/ETM+ (Roy et al. 2016). Por isso testamos a tendência na série
# completa e também só na era OLI (2013+).

# %%
todas = pd.concat([hist.assign(sensor="TM/ETM+"), c89.assign(sensor="OLI")], ignore_index=True) if len(hist) else c89.assign(sensor="OLI")
todas = todas[(todas.frac_valida >= 0.3) & todas.ndvi_mediana.notna()].copy()
todas["ano"] = todas.datetime.dt.year
anual = todas.groupby(["aoi", "ano"]).ndvi_mediana.median().unstack(0)
seca_anual = todas[todas.datetime.dt.month.isin([8, 9, 10, 11])].groupby(["aoi", "ano"]).ndvi_mediana.median().unstack(0)
linhas = []
for n in AOIS:
    for rot, serie in (("anual", anual), ("seca ago–nov", seca_anual)):
        if n not in serie:
            continue
        for per, s in (("série completa", serie[n].dropna()), ("só OLI 2013+", serie[n].dropna().loc[2013:])):
            if len(s) >= 6:
                r = mk.original_test(s.values)
                linhas.append({"aoi": n, "estatística": rot, "período": per, "anos": len(s), "início": s.index.min(),
                               "tendência": r.trend, "p": round(r.p, 4), "Sen_NDVI_por_década": round(r.slope * 10, 4)})
pd.DataFrame(linhas)

# %%
fig, ax = plt.subplots(figsize=(14, 4.5))
for n in AOIS:
    if n in anual:
        ax.plot(anual.index, anual[n], "-o", ms=3, color=CORES[n], label=n)
ax.axvspan(2012, 2017.99, color="tab:red", alpha=0.08, label="seca 2012–2017")
ax.axvline(2013, color="k", ls=":", lw=1)
ax.text(2013.2, ax.get_ylim()[1] * 0.97, "início do OLI", fontsize=8)
ax.set_title("NDVI anual (mediana das cenas limpas) por AOI"); ax.legend(ncol=5); plt.show()

# %% [markdown]
# ### Tendência por pixel (Sen da mediana de NDVI da seca, 2013–hoje)

# %%
fig, axs = plt.subplots(1, 4, figsize=(17, 4.3))
resumo_pix = []
for j, (n, (a, t, x, y)) in enumerate(cubos.items()):
    anos = np.arange(2013, t.year.max() + 1)
    comp = []
    for ano in anos:
        m = (t.year == ano) & np.isin(t.month, [8, 9, 10, 11])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            comp.append(np.nanmedian(a[m], axis=0) if m.sum() else np.full(a.shape[1:], np.nan))
    comp = np.stack(comp, axis=-1)
    sen, z, p = mk_sen_vetorizado(comp, anos.astype(float))
    ext = [x.min() / 1e3, x.max() / 1e3, y.min() / 1e3, y.max() / 1e3]
    im = axs[j].imshow(sen * 10, extent=ext, cmap="BrBG", vmin=-0.15, vmax=0.15)
    axs[j].contour(np.flipud(p < 0.05), levels=[0.5], colors="k", linewidths=0.3, extent=ext, origin="lower")
    axs[j].set_title(f"{n}\nSen (ΔNDVI/década); contorno p<0,05", fontsize=9); axs[j].set_xticks([]); axs[j].set_yticks([])
    plt.colorbar(im, ax=axs[j], fraction=0.046)
    ok = np.isfinite(p)
    resumo_pix.append({"aoi": n, "% pixels esverdeando (p<0,05)": 100 * ((p < 0.05) & (sen > 0))[ok].mean(),
                       "% pixels perdendo verde (p<0,05)": 100 * ((p < 0.05) & (sen < 0))[ok].mean(),
                       "Sen mediano/década": float(np.nanmedian(sen) * 10)})
plt.tight_layout(); plt.show()
pd.DataFrame(resumo_pix).round(3)

# %% [markdown]
# ## 7.7 Variabilidade interanual e extremos (secas)

# %%
z_an = (anual - anual.mean()) / anual.std()
fig, ax = plt.subplots(figsize=(14, 3.8))
im = ax.imshow(z_an.T.values, aspect="auto", cmap="RdYlGn", vmin=-2.5, vmax=2.5)
ax.set_yticks(range(len(z_an.columns))); ax.set_yticklabels(z_an.columns)
ax.set_xticks(range(0, len(z_an.index), 2)); ax.set_xticklabels(z_an.index[::2], rotation=90)
plt.colorbar(im, ax=ax, label="anomalia padronizada de NDVI (z)")
ax.set_title("Anos verdes e anos secos por AOI (z-score do NDVI anual)"); ax.grid(False); plt.show()
media_z = z_an.mean(axis=1).sort_values()
print("5 anos mais 'secos' (média dos z das AOIs):", ", ".join(f"{a} ({v:+.2f})" for a, v in media_z.head(5).items()))
print("5 anos mais 'verdes':", ", ".join(f"{a} ({v:+.2f})" for a, v in media_z.tail(5)[::-1].items()))
if len(z_an.loc[2012:2017]):
    print("z médio 2012–2017 por AOI:", z_an.loc[2012:2017].mean().round(2).to_dict())

# %% [markdown]
# **Cuidado com o salto de sensor.** O NDVI médio da era OLI (2013+) é maior que o da era TM/ETM+ em quase todas as
# AOIs (tabela abaixo). Parte disso é diferença de sensor (Roy et al. 2016), não só clima. Por isso a anomalia na
# série completa "esconde" parte da seca de 2012–2017. Para comparar anos, padronizamos **dentro de cada era**.

# %%
print("NDVI anual médio por era:")
print(pd.DataFrame({"TM/ETM+ 1984–2012": anual.loc[:2012].mean(), "OLI 2013+": anual.loc[2013:].mean(),
                    "salto": anual.loc[2013:].mean() - anual.loc[:2012].mean()}).round(3).to_string())
oli = anual.loc[2013:2025]
z_oli = (oli - oli.mean()) / oli.std()
print("\nAnos mais secos dentro da era OLI (média dos z):", z_oli.mean(axis=1).sort_values().head(5).round(2).to_dict())
pk = todas[todas.datetime.dt.month.isin([3, 4, 5, 6])].groupby(["aoi", "ano"]).ndvi_p90.max().unstack(0).loc[2013:2025]
print("Picos de chuva mais fracos na era OLI (média dos z do p90 mar–jun):", ((pk - pk.mean()) / pk.std()).mean(axis=1).sort_values().head(5).round(2).to_dict())
tm = anual.loc[:2012]
print("Anos mais secos dentro da era TM/ETM+:", ((tm - tm.mean()) / tm.std()).mean(axis=1).sort_values().head(6).round(2).to_dict())

# %%
pico_anual =todas[todas.datetime.dt.month.isin([3, 4, 5, 6])].groupby(["aoi", "ano"]).ndvi_p90.max().unstack(0)
fig, ax = plt.subplots(figsize=(14, 3.8))
for n in AOIS:
    if n in pico_anual:
        ax.plot(pico_anual.index, pico_anual[n], "-o", ms=3, color=CORES[n], label=n)
ax.axvspan(2012, 2017.99, color="tab:red", alpha=0.08)
ax.set_title("Pico de verde da estação chuvosa (p90 do NDVI, mar–jun): o 'tamanho da safra' visto do espaço"); ax.legend(ncol=4)
plt.show()

# %% [markdown]
# ## 7.8 Insights e ideias para o produto
# 1. **Janela de visibilidade.** No Ceará, de fevereiro a maio, poucas cenas Landsat ficam com menos de 20% de nuvem
#    (gráfico 7.3). De julho a dezembro, quase todas as passagens são úteis. Por isso o produto não deve depender de uma
#    imagem óptica na quadra chuvosa: convém combinar com SAR (NISAR/Sentinel-1) ou com o HLS, que é mais frequente.
# 2. **Calendário do verde e janela de campo nu.** O pico de NDVI vem ~1–2 meses depois do pico da chuva, e o solo
#    exposto domina de agosto a dezembro no sequeiro. Esse é o insumo direto para recomendar **cobertura do solo** e
#    **datas de semeadura**.
# 3. **Irrigação aparece como "verde na seca".** NDVI de seca alto e estável identifica perímetros irrigados (Apodi).
#    É um rótulo barato para separar sistemas irrigados de sequeiro em qualquer lugar do mundo, sem cadastro.
# 4. **Secas ficam registradas.** A série 1984–hoje marca, sincronizados entre as AOIs, os anos de seca conhecidos do
#    Nordeste:
#    - 1992–93, 1998–99 e 2003 na era TM/ETM+;
#    - 2015–2017 (fim da grande seca de 2012–2017) dentro da era OLI.
#
#    Daí sai um índice de **risco histórico por talhão**: quantos anos em 40 o verde falhou. Para isso as anomalias
#    precisam ser padronizadas **por sensor**, por causa do salto TM → OLI.
# 5. **Tendência por pixel separa** áreas que estão degradando (perda de verde na seca) de áreas que estão sendo
#    convertidas para irrigação (ganho). Serve como camada "saúde do solo/cobertura" no mapa do agricultor.
#
# **Ideias de modelo:**
# - Classificador de sistema (irrigado × sequeiro × pasto × Caatinga) com features fenológicas: pico, vale, amplitude,
#   integral de NDVI e NDVI de seca.
# - Detecção de mudança (BFAST/CCDC) para datar as conversões.
# - Previsão do NDVI de pico a partir da chuva de fev–mar, usando as seções de clima, para alerta precoce de quebra
#   de safra.
