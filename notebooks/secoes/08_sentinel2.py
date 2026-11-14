# %% [markdown]
# # 8. Sentinel-2 L2A (ESA Copernicus) e HLS (NASA)
#
# **O que é:** imagens multiespectrais de 10–20 m dos satélites Sentinel-2A/B/C da ESA, com bandas de vermelho, NIR,
# *red-edge* e SWIR. A revisita é de 5 dias com dois satélites; onde duas órbitas se sobrepõem (caso da AOI do Apodi), cai
# para ~2,5 dias.
# O **HLS** (Harmonized Landsat Sentinel-2, da NASA) junta Landsat 8/9 e Sentinel-2 numa grade única de 30 m, com
# correções para os dois sensores ficarem comparáveis.
#
# **Como baixamos:**
# - Sentinel-2: Planetary Computer (`sentinel-2-l2a`). O Earth Search (`sentinel-2-c1-l2a`) foi testado e descartado
#   por ter o arquivo incompleto (numa AOI: 2017 com 1 cena, 2018 com 42, 2022 com 13, contra ~140 no Planetary
#   Computer).
# - Offset das *baselines* ≥ 04.00 (desde 25/01/2022): o DN ganhou +1000, então refl = (DN − 1000)/10000. Conferimos
#   que o valor bate exatamente com o Earth Search em datas comuns.
# - Cubos de 20 m (NDVI, NDMI) nas 4 AOIs, de 2017 até hoje, só com cenas de nuvem ≤ 90%. Máscara SCL ∈ {4 vegetação,
#   5 solo, 6 água}.
# - HLS L30/S30 (2020–hoje), com estatísticas por cena nas AOIs (nuvem ≤ 80%; máscara Fmask bits 1–3).

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

pd.set_option("display.width", 200)
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})
D = DADOS / "sentinel2"
CORES = {"apodi_jaguaribe": "#1f77b4", "cariri": "#d62728", "sertao_central": "#ff7f0e", "ibiapaba": "#2ca02c"}
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

def ler(nome):
    p = D / nome
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p)
    if "datetime" in df:
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True).dt.tz_localize(None)
    return df

meta, glob, cen, hls = ler("s2_stac_ceara.parquet"), ler("s2_stac_global.parquet"), ler("s2_aoi_cenas.parquet"), ler("hls_aoi_cenas.parquet")
man = json.loads((D / "MANIFESTO.json").read_text(encoding="utf-8")) if (D / "MANIFESTO.json").exists() else {}
print(f"S2 no Ceará (STAC): {len(meta):,} itens | cenas nas AOIs: {len(cen):,} | HLS nas AOIs: {len(hls):,}")

# %% [markdown]
# ## 8.1 Ficha técnica

# %%
pd.DataFrame([
    ("Provedor", "ESA/Copernicus (Sentinel-2) e NASA (HLS v2.0); espelho aberto no Microsoft Planetary Computer"),
    ("Produto", "Sentinel-2 L2A (Sen2Cor): reflectância de superfície + SCL (classificação de cena)"),
    ("Resolução", "10 m (B02/B03/B04/B08), 20 m (red-edge, B11/B12, SCL), 60 m (atmosféricas); usamos 20 m"),
    ("Revisita", "5 dias com 2 satélites (S2A+S2B; S2C entrou em 2025); ~2,5 dias onde duas órbitas se sobrepõem (AOI Apodi: 1.421 datas em ~10 anos; demais AOIs: ~710)"),
    ("Período no Ceará", f"{meta.datetime.min():%Y-%m-%d} a {meta.datetime.max():%Y-%m-%d}" if len(meta) else "-"),
    ("HLS", "30 m, Landsat 8/9 (L30) + Sentinel-2 (S30) harmonizados; Planetary Computer a partir de 2020"),
    ("Acesso", "aberto (Copernicus Data Space pede cadastro gratuito; Planetary Computer não)"),
    ("Tamanho local", f"{man.get('tamanho_bytes', 0)/1e9:.2f} GB"),
], columns=["item", "valor"])

# %% [markdown]
# ## 8.2 Validação de cobertura global (amostras de 1° em 2023)

# %%
def resumo(g):
    g = g.dropna(subset=["id"])
    if g.empty:
        return pd.Series({"itens": 0, "datas": 0, "revisita_d": np.nan, "revisita_limpa_d": np.nan, "nuvem_mediana": np.nan})
    d = np.sort(g.datetime.dt.normalize().unique()); l = np.sort(g[g.cloud_cover < 20].datetime.dt.normalize().unique())
    gap = lambda x: float(np.median(np.diff(x).astype("timedelta64[D]").astype(int))) if len(x) > 1 else np.nan
    return pd.Series({"itens": len(g), "datas": len(d), "revisita_d": gap(d), "revisita_limpa_d": gap(l), "nuvem_mediana": g.cloud_cover.median()})

cob = glob.groupby(["amostra", "lon", "lat"]).apply(resumo).reset_index().sort_values("lat", ascending=False)
cob

# %%
fig, ax = plt.subplots(figsize=(12, 5.5))
paises_gdf().plot(ax=ax, color="#eeeeee", edgecolor="#999999", lw=0.4)
sc = ax.scatter(cob.lon, cob.lat, s=15 + cob.datas * 0.8, c=cob.revisita_limpa_d, cmap="viridis_r", edgecolor="k", vmin=0, vmax=40)
for _, r in cob.iterrows():
    ax.annotate(f"{r.amostra.split('_')[0]}\n{int(r.datas)}", (r.lon, r.lat), fontsize=6, ha="center", xytext=(0, 6), textcoords="offset points")
plt.colorbar(sc, ax=ax, label="revisita limpa (dias)")
ax.set_title("Sentinel-2 L2A em 2023: datas distintas por caixa de 1° (tamanho) e revisita limpa (cor)")
ax.set_xlim(-180, 180); ax.set_ylim(-90, 90); plt.show()
ok = cob[cob.itens > 0]
print("Latitude máx/mín com dados:", ok.lat.max(), ok.lat.min(), "| sem dados:", ", ".join(cob[cob.itens == 0].amostra) or "nenhuma")
print(f"Revisita mediana: {ok.revisita_d.median():.0f} dias; revisita limpa mediana: {ok.revisita_limpa_d.median():.0f} dias")
glob["mes"] = glob.datetime.dt.month
glob.dropna(subset=["id"]).groupby("amostra").agg(lat=("lat", "first"), meses=("mes", lambda s: len(set(s.dropna()))),
    lista=("mes", lambda s: ",".join(str(int(m)) for m in sorted(set(s.dropna()))))).sort_values("lat", ascending=False)

# %% [markdown]
# **Veredito de cobertura (tirado das tabelas acima):** o Sentinel-2 L2A é **global sobre terra**. As 27 caixas têm
# dados em 2023, do norte da Groenlândia (81°N) ao interior da Antártida (80°S). Os limites:
# 1. **Iluminação:** acima de ~60° só há imagens nos meses com Sol. Entre os trópicos e as latitudes médias há os
#    12 meses.
# 2. **Número de órbitas:** caixas cobertas por uma órbita têm ~73 datas/ano (5 dias). Onde duas órbitas se sobrepõem,
#    são ~145 datas/ano (2–3 dias). No Ceará, as AOIs ficam nessas faixas de sobreposição.
# 3. **Histórico curto:** os dados úteis começam em 2015–2017, então para tendências longas e secas antigas o Landsat
#    é a base.
#
# Para lavoura em **qualquer país**, o Sentinel-2 é a camada de alta frequência do produto.

# %% [markdown]
# ## 8.3 Qualidade e disponibilidade no Ceará

# %%
meta["ano"] = meta.datetime.dt.year; meta["mes"] = meta.datetime.dt.month
fig, axs = plt.subplots(1, 3, figsize=(17, 4))
meta.pivot_table(index="ano", columns="platform", values="id", aggfunc="count").fillna(0).plot(kind="bar", stacked=True, ax=axs[0], width=0.85)
axs[0].set_title("Itens S2 que tocam o Ceará por ano"); axs[0].set_xlabel("")
axs[1].boxplot([meta.loc[meta.mes == m, "cloud_cover"].dropna() for m in range(1, 13)], tick_labels=MESES, showfliers=False)
axs[1].axvspan(1.5, 5.5, color="tab:blue", alpha=0.08); axs[1].set_title("Nuvem por cena (%)")
p20 = meta.groupby("mes").cloud_cover.apply(lambda s: (s < 20).mean() * 100)
axs[2].bar(MESES, p20.values, color=["tab:blue" if 2 <= m <= 5 else "tab:gray" for m in range(1, 13)]); axs[2].set_title("% cenas com nuvem < 20%")
plt.tight_layout(); plt.show()
print("Baselines de processamento (mistura de versões ao longo do tempo):")
print(meta.baseline.value_counts().head(10).to_string())
print(f"Tiles MGRS distintos: {meta.mgrs.nunique()}")

# %%
cen["mes"] = cen.datetime.dt.month; cen["ano"] = cen.datetime.dt.year
cv = cen[~cen.get("pulada_nuvem", pd.Series(False, index=cen.index)).fillna(False).astype(bool)]
fig, axs = plt.subplots(1, 2, figsize=(14, 4))
for n in AOIS:
    g = cen[cen.aoi == n]
    axs[0].plot(range(1, 13), g.groupby("mes").frac_valida.mean().reindex(range(1, 13)), "-o", color=CORES[n], label=n)
    axs[1].plot(range(1, 13), (g.assign(ok=g.frac_valida >= 0.8).groupby("mes").ok.mean().reindex(range(1, 13))) * 100, "-o", color=CORES[n])
for ax, t in zip(axs, ["fração média da AOI limpa (SCL) por passagem", "% de passagens com ≥80% limpa"]):
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(MESES); ax.axvspan(1.5, 5.5, color="tab:blue", alpha=0.08); ax.set_title(t)
axs[0].legend(); plt.tight_layout(); plt.show()
uteis = cen[cen.frac_valida >= 0.8].groupby(["aoi", "ano"]).size().unstack(0).fillna(0).astype(int)
print("Passagens úteis (≥80% limpas) por ano:"); print(uteis.to_string())

# %% [markdown]
# ## 8.4 Estatística descritiva nas AOIs (20 m)

# %%
MAX_CENAS = 300  # amostra de cenas por AOI (os cubos têm 600–1200 datas; limita memória e tempo)
rng = np.random.default_rng(1)
linhas, mapas = [], {}
for n in AOIS:
    arq = D / f"s2_aoi_{n}.nc"
    if not arq.exists():
        continue
    ds = xr.open_dataset(arq, decode_cf=False)
    sid = pd.Series(ds.scene_id.values)
    fv = sid.map(cen.drop_duplicates("id").set_index("id").frac_valida).fillna(0).values
    idx = np.flatnonzero(fv >= 0.5)
    if len(idx) > MAX_CENAS:
        idx = np.sort(rng.choice(idx, MAX_CENAS, replace=False))
    a = ds["ndvi"].isel(time=idx).values.astype(np.float32); a[a == -32768] = np.nan; a *= 1e-4
    v = a[np.isfinite(a)]; s = pd.Series(rng.choice(v, size=min(400_000, v.size), replace=False))
    linhas.append({"aoi": n, "datas_no_cubo": ds.sizes["time"], "cenas_usadas(≥50% limpas)": len(idx), "media": s.mean(), "dp": s.std(),
                   "p05": s.quantile(.05), "mediana": s.median(), "p95": s.quantile(.95), "assimetria": s.skew(), "curtose": s.kurt(),
                   "frac_solo_exposto": (s < 0.2).mean(), "frac_veg_densa": (s > 0.6).mean()})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p90 = np.nanpercentile(a, 90, axis=0); p10 = np.nanpercentile(a, 10, axis=0)
    mapas[n] = (p90, p10, [ds.x.values.min() / 1e3, ds.x.values.max() / 1e3, ds.y.values.min() / 1e3, ds.y.values.max() / 1e3])
    del a, v
    ds.close()
pd.DataFrame(linhas).set_index("aoi").round(3)

# %%
fig, axs = plt.subplots(2, len(mapas), figsize=(4.2 * len(mapas), 8))
for j, (n, (p90, p10, ext)) in enumerate(mapas.items()):
    for i, (img, tit, cm, lim) in enumerate([(p90, "NDVI p90 (máximo típico)", "YlGn", (0, 0.9)), (p90 - p10, "amplitude p90−p10", "magma", (0, 0.7))]):
        im = axs[i, j].imshow(img, extent=ext, cmap=cm, vmin=lim[0], vmax=lim[1]); axs[i, j].set_title(f"{n}\n{tit}", fontsize=9)
        axs[i, j].set_xticks([]); axs[i, j].set_yticks([]); plt.colorbar(im, ax=axs[i, j], fraction=0.046)
plt.suptitle("Sentinel-2 20 m: onde a vegetação fica mais verde e onde ela mais varia"); plt.tight_layout(); plt.show()

# %% [markdown]
# A **amplitude** (p90 − p10) a 20 m separa bem:
# - lavoura de sequeiro e pasto, com amplitude alta: verde na chuva e solo na seca;
# - mata/serra, com amplitude baixa e verde sempre;
# - talhões irrigados, que aparecem como retângulos de geometria regular e pivôs circulares, com NDVI alto e amplitude
#   que muda por talhão conforme o calendário de plantio.
#
# Os limites de talhão aparecem nítidos a 20 m: dá para segmentar parcelas.

# %% [markdown]
# ## 8.5 Sazonalidade

# %%
cl = cen[cen.frac_valida >= 0.3].groupby(["aoi", "mes"]).ndvi_mediana.agg(["median", lambda s: s.quantile(.25), lambda s: s.quantile(.75)])
cl.columns = ["med", "q25", "q75"]
fig, axs = plt.subplots(1, 2, figsize=(15, 4.3))
for n in AOIS:
    if n in cl.index.get_level_values(0):
        c = cl.loc[n]; axs[0].plot(c.index, c.med, "-o", color=CORES[n], label=n); axs[0].fill_between(c.index, c.q25, c.q75, color=CORES[n], alpha=0.12)
        m = cen[(cen.aoi == n) & (cen.frac_valida >= 0.3)].groupby("mes").ndmi_mediana.median(); axs[1].plot(m.index, m, "-o", color=CORES[n])
for ax, t in zip(axs, ["NDVI mediano por mês (S2)", "NDMI mediano por mês (umidade da vegetação, NIR−SWIR1)"]):
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(MESES); ax.axvspan(1.5, 5.5, color="tab:blue", alpha=0.08); ax.set_title(t)
axs[0].legend(); plt.tight_layout(); plt.show()

# %% [markdown]
# ## 8.6 Tendências (Mann-Kendall + Sen) e 8.7 variabilidade interanual
# A série de 2017–hoje é curta: as tendências servem de **sinal**, não de conclusão. O Landsat (seção 7) é a base para
# tendências longas.

# %%
cc = cen[(cen.frac_valida >= 0.3) & cen.ndvi_mediana.notna()].copy()
cc["mes_ini"] = cc.datetime.dt.to_period("M").dt.to_timestamp()
mensal = cc.groupby(["aoi", "mes_ini"]).ndvi_mediana.median().unstack(0)
linhas = []
for n in mensal.columns:
    s = mensal[n].dropna()
    anom = s - s.groupby(s.index.month).transform("mean")
    r = mk.original_test(anom.values); rs = mk.seasonal_test(s.asfreq("MS").interpolate(limit=2).dropna().values, period=12)
    linhas.append({"aoi": n, "meses": len(s), "MK anomalia: tendência": r.trend, "p": round(r.p, 4), "Sen/ano (anomalia)": round(r.slope * 12, 4),
                   "MK sazonal: tendência": rs.trend, "p sazonal": round(rs.p, 4)})
display(pd.DataFrame(linhas)) if "display" in dir() else print(pd.DataFrame(linhas).to_string())

an = cc.groupby(["aoi", "ano"]).ndvi_mediana.median().unstack(0)
pico = cc[cc.mes.isin([3, 4, 5, 6])].groupby(["aoi", "ano"]).ndvi_p90.max().unstack(0)
fig, axs = plt.subplots(1, 2, figsize=(15, 4))
for n in an.columns:
    axs[0].plot(an.index, an[n], "-o", color=CORES[n], label=n); axs[1].plot(pico.index, pico[n], "-o", color=CORES[n])
axs[0].set_title("NDVI anual (mediana)"); axs[1].set_title("pico da quadra chuvosa (p90 mar–jun)"); axs[0].legend(); plt.tight_layout(); plt.show()

# %% [markdown]
# ## 8.8 Comparação Landsat × Sentinel-2 nas mesmas datas (±1 dia)
# Comparamos o NDVI mediano da AOI nas passagens em que os dois sensores viram a AOI com ≥ 80% limpa e com até 1 dia
# de diferença.

# %%
L = pd.read_parquet(DADOS / "landsat" / "landsat_aoi_cenas_l89.parquet")
L["datetime"] = pd.to_datetime(L["datetime"], utc=True).dt.tz_localize(None)
pares = []
for n in AOIS:
    a = L[(L.aoi == n) & (L.frac_valida >= 0.8)].sort_values("datetime"); b = cen[(cen.aoi == n) & (cen.frac_valida >= 0.8)].sort_values("datetime")
    if a.empty or b.empty:
        continue
    m = pd.merge_asof(a[["datetime", "ndvi_mediana", "ndmi_mediana"]], b[["datetime", "ndvi_mediana", "ndmi_mediana"]].rename(columns={"datetime": "dt_s2"}),
                      left_on="datetime", right_on="dt_s2", direction="nearest", tolerance=pd.Timedelta("1D"), suffixes=("_L", "_S2")).dropna()
    m["aoi"] = n; pares.append(m)
pares = pd.concat(pares) if pares else pd.DataFrame()
if len(pares):
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    for n, g in pares.groupby("aoi"):
        axs[0].scatter(g.ndvi_mediana_L, g.ndvi_mediana_S2, s=14, color=CORES[n], label=n, alpha=0.7)
        axs[1].scatter(g.ndmi_mediana_L, g.ndmi_mediana_S2, s=14, color=CORES[n], alpha=0.7)
    for ax, t in zip(axs, ["NDVI", "NDMI"]):
        lo, hi = ax.get_xlim(); ax.plot([lo, hi], [lo, hi], "k--", lw=1); ax.set_xlabel(f"Landsat 8/9 {t}"); ax.set_ylabel(f"Sentinel-2 {t}"); ax.set_title(t)
    axs[0].legend(); plt.tight_layout(); plt.show()
    d = pares.ndvi_mediana_S2 - pares.ndvi_mediana_L
    from scipy.stats import pearsonr
    r = pearsonr(pares.ndvi_mediana_L, pares.ndvi_mediana_S2)[0]
    print(f"pares: {len(pares)} | viés S2−L (NDVI): {d.mean():+.4f} | RMSD: {np.sqrt((d**2).mean()):.4f} | r = {r:.3f}")
    print(pares.groupby("aoi").apply(lambda g: pd.Series({"n": len(g), "vies": (g.ndvi_mediana_S2 - g.ndvi_mediana_L).mean()})).round(4).to_string())

# %% [markdown]
# ## 8.9 HLS: a série harmonizada (L30 + S30)

# %%
if len(hls):
    hls["mes"] = hls.datetime.dt.month
    h = hls[(hls.frac_valida >= 0.3) & hls.ndvi_mediana.notna()]
    print("Cenas HLS por coleção:", hls.colecao.value_counts().to_dict())
    print("Passagens úteis (≥80% limpas) por ano/AOI:")
    print(hls[hls.frac_valida >= 0.8].groupby([hls.datetime.dt.year, "aoi"]).size().unstack().fillna(0).astype(int).to_string())
    fig, ax = plt.subplots(figsize=(15, 4))
    for n, g in h.groupby("aoi"):
        for col, mk_ in (("hls2-l30", "o"), ("hls2-s30", ".")):
            gg = g[g.colecao == col]; ax.plot(gg.datetime, gg.ndvi_mediana, mk_, ms=3, color=CORES[n], alpha=0.6, label=f"{n} {col[-3:]}")
    ax.set_title("HLS: NDVI mediano por passagem (L30 = círculos, S30 = pontos)"); ax.legend(ncol=4, fontsize=7); plt.show()
    gap = h[h.frac_valida >= 0.8].groupby("aoi").datetime.apply(lambda s: np.median(np.diff(np.sort(s.dt.normalize().unique())).astype("timedelta64[D]").astype(int)))
    print("Intervalo mediano entre passagens úteis (dias), HLS:", gap.to_dict())

# %% [markdown]
# ### O HLS remove o viés entre sensores?
# Repetimos a comparação da 8.8 dentro do HLS: pares L30 × S30 com até 1 dia de diferença e ≥ 80% da AOI limpa.

# %%
if len(hls):
    pp = []
    for n, g in hls[hls.frac_valida >= 0.8].groupby("aoi"):
        a = g[g.colecao == "hls2-l30"].sort_values("datetime"); b = g[g.colecao == "hls2-s30"].sort_values("datetime")
        m = pd.merge_asof(a[["datetime", "ndvi_mediana"]], b[["datetime", "ndvi_mediana"]].rename(columns={"datetime": "d2"}), left_on="datetime",
                          right_on="d2", direction="nearest", tolerance=pd.Timedelta("1D"), suffixes=("_L30", "_S30")).dropna()
        pp.append(m)
    pp = pd.concat(pp)
    dh = pp.ndvi_mediana_S30 - pp.ndvi_mediana_L30
    comp = pd.DataFrame({
        "Landsat C2 × Sentinel-2 L2A (brutos)": [len(pares), (pares.ndvi_mediana_S2 - pares.ndvi_mediana_L).mean(),
                                                  np.sqrt(((pares.ndvi_mediana_S2 - pares.ndvi_mediana_L) ** 2).mean()),
                                                  np.corrcoef(pares.ndvi_mediana_L, pares.ndvi_mediana_S2)[0, 1]] if len(pares) else [np.nan] * 4,
        "HLS L30 × S30 (harmonizados)": [len(pp), dh.mean(), np.sqrt((dh ** 2).mean()), np.corrcoef(pp.ndvi_mediana_L30, pp.ndvi_mediana_S30)[0, 1]]},
        index=["pares", "viés (S2 − Landsat)", "RMSD", "r"]).T.round(4)
    print(comp.to_string())

# %% [markdown]
# ## 8.10 Insights e ideias para o produto
# 1. **Sentinel-2 + HLS resolvem a frequência.** As AOIs são vistas a cada ~5 dias, ou ~2,5 dias no Apodi, onde duas
#    órbitas se sobrepõem. Somando L30 + S30, o HLS dá uma passagem útil (≥ 80% limpa) a cada 4–10 dias medianos.
#    Isso o Landsat sozinho não garante: ele tem 4–19 passagens úteis por ano por AOI.
# 2. **Landsat e Sentinel-2 brutos andam juntos, mas não batem.**
#    - A correlação é quase perfeita (r ≈ 0,995), mas há um **viés sistemático de ~−0,06 no NDVI**: o S2 sai menor.
#    - As causas são a NIR larga B08 contra a NIR estreita do OLI e as cadeias de correção diferentes (Sen2Cor contra
#      LaSRC).
#    - Dentro do **HLS** o viés cai para ~+0,007 e o RMSD para ~0,01, porque o HLS usa a B8A, ajuste de banda e BRDF.
#    - Conclusão: para costurar séries (Landsat 1984–2016 + S2/HLS 2017+), **use o HLS** ou aplique uma correção
#      linear por região. Nunca misture os brutos.
# 3. **20 m mostra o talhão.** A amplitude p90−p10 e o p90 delimitam parcelas e pivôs. Com isso dá para segmentar
#    talhões automaticamente (SAM/U-Net) e calcular a fenologia **por talhão**, não por pixel.
# 4. **O NDMI (NIR−SWIR1) é o "termômetro de água" da planta.** Ele cai antes do NDVI quando falta água, por isso é
#    um bom gatilho de **alerta de estresse hídrico** a cruzar com SMAP/IMERG/POWER.
# 5. **Atenção às baselines.** O offset de 2022 (+1000 no DN) muda os números brutos, e o arquivo mistura 8 baselines.
#    Um produto global precisa normalizar por *baseline*. O HLS já entrega isso, e ainda harmoniza com o Landsat
#    (item 2), por isso é a escolha natural para o motor.
#
# **Ideias de modelo:**
# - Classificação de cultura por série temporal S2/HLS (Transformer temporal, TempCNN, LSTM ou TimesNet) treinada com
#   rótulos do CDL nos EUA e transferida para o Brasil com poucos rótulos (MapBiomas).
# - Previsão de curto prazo do NDVI/NDMI (próximas 2–4 semanas) com chuva e umidade do solo como covariáveis.
# - Detecção do plantio e da colheita (pontos de virada da curva) para montar o **calendário real de rotação** de
#   cada talhão.
