# %% [markdown]
# # 3. ERA5 — reanálise climática (ECMWF / Copernicus, parceiro ESA)
#
# **Ficha técnica**
#
# | Item | Valor |
# |---|---|
# | Produto | ERA5, 5ª reanálise do ECMWF: modelo IFS + assimilação 4D-Var de satélites, radiossondas, estações e boias |
# | Resolução | 0,25° (~28 km), horária, 1940→presente (latência ~5 dias no CDS) |
# | Período baixado | **1979–2020** (o que o espelho aberto `era5-pds` do Planetary Computer oferece; 2021+ só pelo CDS, que exige chave) |
# | Variáveis baixadas (horárias → diárias, dia local UTC−3) | T2m média; Tmax/Tmin (máx/mín horárias da previsão); ponto de orvalho; precipitação; radiação solar descendente (ssrd); vento a 10 m (u, v) |
# | Derivadas (calculadas aqui) | ET0 FAO-56 Penman-Monteith, VPD, umidade relativa, graus-dia base 10 °C, dias com Tmax ≥ 35 °C, déficit P − ET0 |
# | Recorte | Nordeste (−48,8 a −34,7 lon; −18,4 a −1,0 lat; 70×57 pixels). O Nordeste inteiro cai num único bloco Zarr (372 h × 150 × 150), então o custo é ~11 MB por mês por variável |
# | Licença | Copernicus (uso livre com atribuição) |

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
DIR = DADOS / "era5"
ce_gdf, ne_gdf, terra = ceara_gdf(), nordeste_gdf(), terra_gdf()
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def mascara(geom, lon, lat):
    lo, la = np.meshgrid(lon, lat)
    return xr.DataArray(shapely.contains_xy(geom, lo, la), dims=("lat", "lon"))


def mapa(ax, da, titulo, cmap="viridis", gdf=None, **kw):
    m = ax.pcolormesh(da.lon, da.lat, da, cmap=cmap, shading="auto", **kw)
    (gdf if gdf is not None else ne_gdf).boundary.plot(ax=ax, color="k", lw=0.5)
    ax.set_title(titulo, fontsize=10)
    ax.set_aspect("equal")
    plt.colorbar(m, ax=ax, shrink=0.8)


grade = xr.open_dataset(DIR / "era5_ne_mensal_grade.nc").load().sortby("lat")
M_NE = mascara(ne_gdf.geometry.union_all(), grade.lon.values, grade.lat.values)
M_CEg = mascara(ce_gdf.geometry.union_all(), grade.lon.values, grade.lat.values)
# diario so do Ceara (com folga) para estatisticas diarias
arqs = sorted(DIR.glob("era5_ne_diario_*.nc"))
d_ce = xr.open_mfdataset(arqs, combine="by_coords")[["t2m", "tmax", "tmin", "d2m", "tp", "ssrd", "ws10", "ws10_max"]] \
    .sel(lon=slice(BBOX_CE[0], BBOX_CE[2]), lat=slice(BBOX_CE[3], BBOX_CE[1])).load().sortby("lat")
der = xr.open_dataset(DIR / "era5_ne_derivados_diario.nc").sel(lon=slice(BBOX_CE[0], BBOX_CE[2]),
                                                                lat=slice(BBOX_CE[1], BBOX_CE[3])).load()
d_ce = xr.merge([d_ce, der])
M_CE = mascara(ce_gdf.geometry.union_all(), d_ce.lon.values, d_ce.lat.values)
s_ce = d_ce.where(M_CE).mean(("lat", "lon")).to_dataframe().drop(columns=["n_horas_an", "n_horas_fc"], errors="ignore")
print("diário Ceará:", dict(d_ce.sizes), "| pixels no Ceará:", int(M_CE.sum()), "| período",
      str(d_ce.data.values[0])[:10], "→", str(d_ce.data.values[-1])[:10])

# %% [markdown]
# ## 3.1 Validação de cobertura global
# Evidência: um mês inteiro (jan/2020) do planeta, t2m médio e precipitação total, lido do mesmo espelho.

# %%
gl_arq = sorted(DIR.glob("era5_global_*.nc"))
if gl_arq:
    gl = xr.open_dataset(gl_arq[0]).load()
    fig, ax = plt.subplots(1, 2, figsize=(16, 4.2))
    m = ax[0].pcolormesh(gl.lon, gl.lat, gl.t2m_media, cmap="RdYlBu_r", shading="auto")
    plt.colorbar(m, ax=ax[0], shrink=0.8)
    ax[0].set_title(f"ERA5 t2m média {gl.attrs.get('mes')} (°C)")
    m = ax[1].pcolormesh(gl.lon, gl.lat, gl.tp_total_mm, cmap="Blues", vmax=400, shading="auto")
    plt.colorbar(m, ax=ax[1], shrink=0.8)
    ax[1].set_title("precipitação total do mês (mm)")
    for a in ax:
        terra.boundary.plot(ax=a, color="k", lw=0.3)
    plt.tight_layout()
    plt.show()
    print("fração de valores ausentes no globo (t2m horário):", float(gl.t2m_nan_frac.mean()),
          "| grade:", dict(gl.sizes), "| lat", float(gl.lat.min()), "a", float(gl.lat.max()))
else:
    print("arquivo global ainda não baixado")

# %% [markdown]
# **Veredito de cobertura.** O ERA5 é **global e sem lacunas por construção**: é um modelo físico com
# assimilação de dados, com valor em toda célula de 0,25° de 90°S a 90°N, terra e oceano, a cada hora desde 1940.
# Ele preenche os lugares sem estação meteorológica, o que é exatamente o caso de grande parte do sertão. O preço é
# a resolução (~28 km): não enxerga microclima de baixada ou serra (ver Ibiapaba) e herda vieses do modelo na
# frequência e intensidade da chuva (ver 3.7). **Serve de camada climática mundial de base**, com correção de viés
# local quando houver estação ou IMERG.

# %% [markdown]
# ## 3.2 Qualidade: ausentes, consistência física e outliers

# %%
dias = pd.date_range(s_ce.index.min(), s_ce.index.max(), freq="D")
print(f"dias esperados {len(dias)} | presentes {len(s_ce)} | buracos {len(dias.difference(s_ce.index))}")
vals = d_ce.where(M_CE)
print("ausentes por variável (%):", {v: round(float(vals[v].isnull().where(M_CE).mean() * 100), 3)
                                     for v in ["t2m", "tmax", "tmin", "d2m", "tp", "ssrd", "ws10"]})
chk = {
    "tmax < tmin": int((vals.tmax < vals.tmin).sum()),
    "t2m fora de [tmin, tmax] (>0,5 °C)": int(((vals.t2m < vals.tmin - 0.5) | (vals.t2m > vals.tmax + 0.5)).sum()),
    "orvalho > t2m": int((vals.d2m > vals.t2m + 0.1).sum()),
    "precipitação negativa": int((vals.tp < 0).sum()),
    "ssrd > 35 MJ/m²/dia": int((vals.ssrd > 35).sum()),
    "Tmax > 45 °C": int((vals.tmax > 45).sum()),
    "Tmin < 10 °C": int((vals.tmin < 10).sum()),
}
print("verificações físicas (pixel-dias):", chk)
print(s_ce[["t2m", "tmax", "tmin", "d2m", "tp", "ssrd", "ws10", "et0", "vpd", "ur"]].describe(
    percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).round(2).to_string())
z = (s_ce[["tmax", "tmin", "ssrd", "ws10"]] - s_ce[["tmax", "tmin", "ssrd", "ws10"]].groupby(s_ce.index.month).transform("mean")) \
    / s_ce[["tmax", "tmin", "ssrd", "ws10"]].groupby(s_ce.index.month).transform("std")
print("dias com |z| > 4 (anomalia extrema vs mês):", (z.abs() > 4).sum().to_dict())

# %% [markdown]
# ## 3.3 Estatística descritiva espacial — Nordeste e Ceará

# %%
anual = grade.resample(data="YS")
tmax_a = anual.mean()["tmax"].mean("data")
et0_a = anual.sum(min_count=12)["et0"].mean("data")
tp_a = anual.sum(min_count=12)["tp"].mean("data")
ia = (tp_a / et0_a)
fig, ax = plt.subplots(2, 2, figsize=(14, 11))
mapa(ax[0, 0], tmax_a.where(M_NE), "Tmax média 1979–2020 (°C)", "inferno")
mapa(ax[0, 1], grade["tmin"].mean("data").where(M_NE), "Tmin média (°C)", "viridis")
mapa(ax[1, 0], et0_a.where(M_NE), "ET0 Penman-Monteith (mm/ano)", "YlOrRd")
cl = xr.where(ia < 0.2, 1, xr.where(ia < 0.5, 2, xr.where(ia < 0.65, 3, 4))).where(M_NE)
mapa(ax[1, 1], cl, "Índice de aridez P/ET0 (1 árido, 2 semiárido, 3 subúmido seco, 4 úmido)", "RdYlGn", vmin=1, vmax=4)
plt.tight_layout()
plt.show()
for nome, M in [("Ceará", M_CEg), ("Nordeste", M_NE)]:
    frac = {k: float(((cl == v) & M).sum() / M.sum()) for k, v in
            [("árido", 1), ("semiárido", 2), ("subúmido seco", 3), ("úmido", 4)]}
    print(nome, "— fração da área por classe de aridez (UNEP):", {k: f"{x:.0%}" for k, x in frac.items()})
print(f"Ceará: P médio {float(tp_a.where(M_CEg).mean()):.0f} mm/ano vs ET0 {float(et0_a.where(M_CEg).mean()):.0f} mm/ano "
      f"→ déficit climático {float((tp_a - et0_a).where(M_CEg).mean()):.0f} mm/ano")
fig, ax = plt.subplots(1, 4, figsize=(17, 3.2))
for a, v, u in zip(ax, ["tmax", "tmin", "et0", "vpd"], ["°C", "°C", "mm/dia", "kPa"]):
    a.hist(d_ce[v].where(M_CE).values.ravel(), bins=60, color="indianred" if v == "tmax" else "steelblue")
    a.set_title(f"{v} diário no Ceará ({u})")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 3.4 Sazonalidade: calor, demanda hídrica e o balanço P − ET0

# %%
SOMA = lambda x: x.sum(min_count=1)  # noqa: E731
mm = s_ce.resample("MS").agg({"t2m": "mean", "tmax": "mean", "tmin": "mean", "tp": SOMA, "et0": SOMA, "vpd": "mean",
                               "ssrd": "mean", "ws10": "mean", "ur": "mean"})
clim = mm.groupby(mm.index.month).mean()
clim.index = MESES
print(clim.round(2).to_string())
fig, ax = plt.subplots(1, 2, figsize=(15, 4))
ax[0].bar(MESES, clim.tp, color="steelblue", label="chuva ERA5")
ax[0].plot(MESES, clim.et0, "o-", c="darkorange", label="ET0")
ax[0].plot(MESES, 0.5 * clim.et0, "--", c="darkorange", alpha=0.6, label="0,5·ET0 (limiar de crescimento FAO)")
ax[0].set_title("Balanço climático mensal no Ceará (mm/mês)")
ax[0].legend()
ax2 = ax[1].twinx()
ax[1].plot(MESES, clim.tmax, "r-o", label="Tmax")
ax[1].plot(MESES, clim.tmin, "b-o", label="Tmin")
ax2.plot(MESES, clim.vpd, "k--", label="VPD (eixo dir.)")
ax[1].set_title("Temperatura e déficit de pressão de vapor")
ax[1].legend(loc="upper left")
ax2.legend(loc="upper right")
plt.tight_layout()
plt.show()
# comprimento do periodo de crescimento (proxy mensal): meses com P >= 0,5 ET0
lgp = ((grade.tp >= 0.5 * grade.et0).where(grade.et0.notnull()).groupby("data.year").sum(min_count=12)).mean("year")
fig, ax = plt.subplots(figsize=(7, 6))
mapa(ax, lgp.where(M_NE), "Meses/ano com P ≥ 0,5·ET0 (proxy do período de crescimento)", "YlGn", vmin=0, vmax=12)
plt.show()
print(f"período de crescimento médio no Ceará: {float(lgp.where(M_CEg).mean()):.1f} meses/ano")

# %% [markdown]
# ## 3.5 Tendências 1979–2020 (Mann-Kendall + Sen)

# %%
an = s_ce.resample("YS").agg({"t2m": "mean", "tmax": "mean", "tmin": "mean", "tp": SOMA, "et0": SOMA, "vpd": "mean",
                               "ssrd": "mean", "ws10": "mean"})
an["dias_tmax35"] = (s_ce.tmax >= 35).resample("YS").sum()
an = an[s_ce.tmax.resample("YS").count() >= 360]  # so anos completos
an.index = an.index.year
res = []
for v in an.columns:
    t = mk.original_test(an[v].values)
    res.append({"variável": v, "tendência": t.trend, "p": round(t.p, 4), "Sen/década": round(t.slope * 10, 3),
                "média": round(an[v].mean(), 2)})
print(pd.DataFrame(res).to_string(index=False))


def sen_grade(cubo):
    sl = np.full(cubo.shape[1:], np.nan)
    pv = np.full(cubo.shape[1:], np.nan)
    for i in range(cubo.shape[1]):
        for j in range(cubo.shape[2]):
            y = cubo.values[:, i, j]
            if np.isfinite(y).all():
                t = mk.original_test(y)
                sl[i, j], pv[i, j] = t.slope, t.p
    return (xr.DataArray(sl, coords={"lat": cubo.lat, "lon": cubo.lon}, dims=("lat", "lon")),
            xr.DataArray(pv, coords={"lat": cubo.lat, "lon": cubo.lon}, dims=("lat", "lon")))


s_tx, p_tx = sen_grade(grade.tmax.resample(data="YS").mean())
s_et, p_et = sen_grade(grade.et0.resample(data="YS").sum(min_count=12))
fig, ax = plt.subplots(1, 2, figsize=(15, 6))
mapa(ax[0], (s_tx * 10).where(M_NE), "Tendência da Tmax média (°C/década)", "RdBu_r", vmin=-0.6, vmax=0.6)
yy, xx = np.where((p_tx < 0.05).values & M_NE.values)
ax[0].scatter(grade.lon.values[xx], grade.lat.values[yy], s=2, c="k")
mapa(ax[1], (s_et * 10).where(M_NE), "Tendência da ET0 anual (mm/década)", "PuOr_r", vmin=-60, vmax=60)
yy, xx = np.where((p_et < 0.05).values & M_NE.values)
ax[1].scatter(grade.lon.values[xx], grade.lat.values[yy], s=2, c="k")
plt.tight_layout()
plt.show()
print(f"pixels do NE com aquecimento significativo de Tmax (p<0,05): {float(((p_tx < 0.05) & (s_tx > 0) & M_NE).sum() / M_NE.sum()):.0%}")

# %% [markdown]
# ## 3.6 Variabilidade interanual, seca 2012–2017 (dentro da janela até 2020) e extremos de calor

# %%
z = (an - an.mean()) / an.std()
fig, ax = plt.subplots(figsize=(14, 4))
ax.plot(z.index, z.tmax, "r-o", ms=3, label="Tmax")
ax.plot(z.index, z.et0, "-o", c="darkorange", ms=3, label="ET0")
ax.bar(z.index, z.tp, color="steelblue", alpha=0.5, label="chuva")
ax.axvspan(2011.5, 2017.5, color="k", alpha=0.08, label="seca 2012–2017")
ax.set_title("Anomalias padronizadas anuais no Ceará (ERA5)")
ax.legend(ncol=4)
plt.show()
sec, fora = an.loc[2012:2017], an.drop(range(2012, 2018))
print("seca 2012–2017 vs demais anos:", {v: f"{sec[v].mean() - fora[v].mean():+.2f}" for v in ["tp", "tmax", "et0", "vpd", "dias_tmax35"]})
r = stats.spearmanr(an.tp, an.tmax)
print(f"Spearman chuva × Tmax anual: {r.statistic:.2f} (p={r.pvalue:.3f}) — anos secos são também mais quentes (seca composta)")
print("anos com mais dias Tmax≥35 °C:", an.dias_tmax35.nlargest(5).to_dict())
q = s_ce[s_ce.index.month.isin([2, 3, 4, 5])]
print(f"na quadra chuvosa: dias com Tmax≥35 °C por ano = {(q.tmax >= 35).groupby(q.index.year).sum().mean():.1f}; "
      f"na estação seca (ago–dez) = {(s_ce.tmax[s_ce.index.month.isin([8,9,10,11,12])] >= 35).groupby(s_ce.index.year[s_ce.index.month.isin([8,9,10,11,12])]).sum().mean():.1f}")

# %% [markdown]
# ## 3.7 Comparação com outras bases (IMERG e POWER, se presentes)

# %%
im = DERIV / "imerg_ce_mensal.parquet"
if im.exists():
    i = pd.read_parquet(im)
    i = i[i.variavel == "precip_total"].set_index("data")["valor"]
    e = mm.tp
    comum_idx = e.index.intersection(i.index)
    x, y = e.loc[comum_idx], i.loc[comum_idx]
    print(f"Chuva mensal no Ceará, {comum_idx.min():%Y-%m}→{comum_idx.max():%Y-%m}: r={np.corrcoef(x, y)[0,1]:.3f} | "
          f"ERA5/IMERG = {x.sum()/y.sum():.2f}")
    dce = xr.open_mfdataset(sorted((DADOS / "imerg").glob("imerg_ce_diario_*.nc")), combine="by_coords")["precip"]
    dce = dce.sel(time=slice("1998-01-01", "2020-12-31")).coarsen(lat=2, lon=2, boundary="trim").mean().load()
    fe1 = (d_ce.tp.sel(data=slice('1998', '2020')).where(M_CE) >= 1).where(M_CE).mean().item()
    M_im = mascara(ce_gdf.geometry.union_all(), dce.lon.values, dce.lat.values)
    dce = dce.where(M_im)
    fi1 = (dce >= 1).where(M_im).mean().item()
    fe01 = (d_ce.tp.sel(data=slice('1998', '2020')).where(M_CE) >= 0.1).where(M_CE).mean().item()
    fi01 = (dce >= 0.1).where(M_im).mean().item()
    print(f"frequência de dias com chuva ≥1 mm: ERA5 {fe1:.1%} vs IMERG {fi1:.1%};  ≥0,1 mm: ERA5 {fe01:.1%} vs IMERG {fi01:.1%}"
          f"  → ERA5 tem {'MENOS' if fe1 < fi1 else 'MAIS'} dias de chuva que o IMERG no Ceará")
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(y, x, s=8)
    ax.plot([0, y.max()], [0, y.max()], "k--")
    ax.set_xlabel("IMERG (mm/mês)")
    ax.set_ylabel("ERA5 (mm/mês)")
    ax.set_title("Chuva mensal na área do Ceará")
    plt.show()
# litoral leste: ERA5 x IMERG x normais aproximadas (mesmos pontos da secao do IMERG)
pts = {"Recife": (-34.95, -8.05, 2400), "Maceió": (-35.75, -9.65, 2100), "Aracaju": (-37.05, -10.95, 1600),
       "Salvador": (-38.50, -12.95, 2100), "Fortaleza": (-38.55, -3.75, 1600), "São Luís": (-44.25, -2.55, 2300),
       "Petrolina (sertão)": (-40.50, -9.40, 550), "Quixadá (sertão)": (-39.00, -4.95, 800)}
an_tp = grade.tp.sel(data=slice("1998", "2020")).resample(data="YS").sum(min_count=12).mean("data")
ne_im = sorted((DADOS / "imerg").glob("imerg_ne_diario_*.nc"))
if ne_im:
    im_all = xr.open_mfdataset(ne_im, combine="by_coords")["precip"].sel(time=slice("1998", "2020"))
lin = []
for k, (lo, la, normal) in pts.items():
    e5 = float(an_tp.sel(lon=lo, lat=la, method="nearest"))
    im_v = float(im_all.sel(lon=lo, lat=la, method="nearest").resample(time="YS").sum().mean()) if ne_im else np.nan
    lin.append({"local": k, "ERA5_mm": round(e5), "IMERG_mm": round(im_v), "normal_aprox_mm": normal,
                "ERA5/normal": round(e5 / normal, 2), "IMERG/normal": round(im_v / normal, 2)})
print("\nChuva anual média 1998–2020 em pontos de referência (normais aproximadas, a conferir):")
print(pd.DataFrame(lin).set_index("local").to_string())
pw = DERIV / "power_ce_mensal.parquet"
if pw.exists():
    p = pd.read_parquet(pw)
    print("POWER — variáveis disponíveis:", sorted(p.variavel.unique())[:30])
    mapa_v = {"T2M_MAX": "tmax", "T2M_MIN": "tmin", "T2M": "t2m", "PRECTOTCORR": "tp"}
    for vp, ve in mapa_v.items():
        s = p[p.variavel == vp].set_index("data")["valor"]
        if len(s):
            ref = mm[ve] if ve != "tp" else mm.tp
            c = ref.index.intersection(s.index)
            if len(c) > 12:
                extra = (f", razão POWER/ERA5 {s.loc[c].sum()/ref.loc[c].sum():.2f}" if ve == "tp"
                         else f", viés POWER−ERA5 {np.mean(s.loc[c]-ref.loc[c]):+.2f} °C")
                print(f"  {vp} × ERA5 {ve} ({c.min():%Y}–{c.max():%Y}): r={np.corrcoef(ref.loc[c], s.loc[c])[0,1]:.3f}{extra}")
else:
    print("derivado do POWER ainda não disponível (outra frente)")

# %% [markdown]
# ## 3.8 Insights e ideias para o produto
#
# (números medidos nas células acima; ERA5 diário 1979–2020, área do Ceará)
#
# 1. **A demanda supera a oferta de água quase o ano todo.** A ET0 Penman-Monteith do Ceará é ~1.960 mm/ano, contra
#    ~810 mm de chuva: déficit climático de ~−1.150 mm/ano. Só fev–abr têm chuva > ET0. O período de crescimento
#    (meses com P ≥ 0,5·ET0, critério FAO) é de **~3,9 meses**. Culturas de ciclo longo só funcionam com irrigação
#    ou nas serras.
# 2. **O índice de aridez separa o mapa em zonas de manejo.** P/ET0 (UNEP) põe 80 % do Ceará no semiárido, 15 % no
#    subúmido seco e 4 % no úmido (serras/litoral). No Nordeste: 45 % semiárido, 35 % úmido. É uma classificação
#    mundial e barata (P/ET0 em qualquer pixel ERA5) que o produto pode usar para pré-filtrar culturas antes do GAEZ.
# 3. **Aquecimento.** A T2m média sobe +0,18 °C/década (p = 0,01) e a Tmin +0,11 °C/década (p = 0,01). A Tmax média
#    estadual não é significativa (+0,11, p = 0,22), mas **73 % dos pixels do Nordeste** têm aumento significativo de
#    Tmax. Os dias com Tmax ≥ 35 °C crescem +2/década (p = 0,001), com recordes em 2019 (28 dias), 2005 e 1998.
#    Quase todos caem em ago–dez (5,2/ano contra 0,3 na quadra).
# 4. **Seca composta.** Correlação de Spearman entre chuva anual e Tmax anual = **−0,88**. Em 2012–2017 houve
#    −261 mm de chuva, +0,58 °C de Tmax e +96 mm de ET0 por ano em relação aos demais anos. O estresse hídrico do
#    agricultor é o produto dos dois, então o motor de risco precisa combinar chuva (IMERG) e demanda (ERA5/POWER).
# 5. **Chuva: ERA5 × IMERG (viés de chuvisco confirmado).** Os totais mensais batem (r = 0,985; ERA5 ≈ 93 % do IMERG),
#    mas o ERA5 tem **mais** dias com chuva: 31 % contra 23,5 % para ≥ 1 mm, e 55 % contra 37 % para ≥ 0,1 mm. Ele
#    distribui chuva fraca demais e encurta os veranicos. Para contar veranicos e dias de chuva, use o IMERG;
#    para temperatura, radiação, vento e umidade, o ERA5/POWER.
# 6. **POWER × ERA5:** as séries mensais concordam (r 0,93–0,97), mas a Tmax do POWER é ~1,7 °C mais quente que a do
#    ERA5. Limiares absolutos (dias ≥ 35 °C, graus-dia) mudam conforme a fonte. O produto deve fixar uma fonte por
#    indicador e calibrar os limiares nela.
# 7. **Litoral leste:** o ERA5 também fica abaixo das normais aproximadas (Recife 0,42; Salvador 0,61; Maceió 0,64),
#    mas menos que o IMERG em Maceió e Aracaju. Parte do déficit costeiro pode vir de pixel misto terra/mar. Validar
#    com estações antes de usar no litoral.
#
# **Ideias de ML/DL**
# - **Correção de viés + downscaling** (quantile mapping → gradient boosting/U-Net) do ERA5 para 1 km usando
#   SRTM (altitude, face de encosta) e distância ao mar; alvo = estações INMET/FUNCEME.
# - **Gerador estocástico de tempo** (Markov para ocorrência de chuva + cópulas para T/radiação), condicionado a
#   ENSO/dipolo, para simular centenas de safras e estimar a probabilidade de sucesso de cada rotação.
# - **Modelo de cultivo simplificado** (FAO AquaCrop-like: balanço hídrico diário com Kc por fase × ET0) acoplado ao
#   motor de rotação: produtividade relativa = f(Σ ETc real / Σ ETc potencial).
# - **Seleção de cenários futuros**: os mesmos indicadores (dias ≥ 35 °C, ET0, período de crescimento) calculados com
#   o NEX-GDDP-CMIP6 alimentam os controles deslizantes de "clima 2050".
