# %% [markdown]
# # 15. NASA NEX-GDDP-CMIP6 — projeções climáticas para os controles deslizantes de cenário
#
# **Ficha técnica**
#
# | Item | Valor |
# |---|---|
# | Produto | NEX-GDDP-CMIP6 (NASA Earth Exchange, NASA Ames): 35 modelos CMIP6 com downscaling estatístico BCSD (bias-correction spatial disaggregation) para 0,25°, diário |
# | Variáveis | pr, tas, tasmax, tasmin, hurs, huss, rlds, rsds, sfcWind |
# | Cenários | historical (1950–2014), SSP2-4.5 e SSP5-8.5 (2015–2100) |
# | Rota usada | Microsoft Planetary Computer `nasa-nex-gddp-cmip6` (aberto). Cada arquivo = 1 ano × 1 variável com bloco de **1 dia do globo inteiro** (tasmax ≈ 244 MB/ano, pr ≈ 181 MB/ano) → baixa-se o arquivo e recorta-se o Nordeste |
# | **Amostra baixada (mínima)** | 1 modelo (**MPI-ESM1-2-HR**), tasmax + pr, janelas de 5 anos: histórico 2010–14; SSP2-4.5 2046–50; SSP5-8.5 2046–50 e 2086–90 |
# | Limitação | um único modelo e janelas curtas: o sinal de temperatura é robusto; o de chuva é ruidoso (o produto final deve usar o ensemble de 10–35 modelos e janelas de 20–30 anos) |

# %%
import sys, warnings
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import shapely

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
plt.rcParams.update({"figure.dpi": 90, "axes.grid": True, "grid.alpha": 0.3})
DIR = DADOS / "nex_gddp"
ce_gdf, ne_gdf = ceara_gdf(), nordeste_gdf()
JAN = {"hist 2010–14": ("historical", range(2010, 2015)), "SSP2-4.5 2046–50": ("ssp245", range(2046, 2051)),
       "SSP5-8.5 2046–50": ("ssp585", range(2046, 2051)), "SSP5-8.5 2086–90": ("ssp585", range(2086, 2091))}


def carregar(var, cen, anos):
    arqs = [DIR / f"nex_MPI-ESM1-2-HR_{cen}_{var}_{a}_ne.nc" for a in anos]
    arqs = [a for a in arqs if a.exists()]
    if not arqs:
        return None
    return xr.open_mfdataset(arqs, combine="by_coords")[var].load()


def mascara(geom, lon, lat):
    lo, la = np.meshgrid(lon, lat)
    return xr.DataArray(shapely.contains_xy(geom, lo, la), dims=("lat", "lon"))


dados = {k: {v: carregar(v, c, a) for v in ["tasmax", "pr"]} for k, (c, a) in JAN.items()}
for k, d in dados.items():
    print(k, {v: (None if x is None else f"{x.sizes['time']} dias") for v, x in d.items()})
ref = dados["hist 2010–14"]["tasmax"]
M_CE = mascara(ce_gdf.geometry.union_all(), ref.lon.values, ref.lat.values)
M_NE = mascara(ne_gdf.geometry.union_all(), ref.lon.values, ref.lat.values)

# %% [markdown]
# ## 15.1 Cobertura global e qualidade
# Pelos metadados STAC de cada item: grade de 600 × 1440 (0,25°), latitude de **59,875°S a 89,875°N** e
# longitude completa. A Antártida fica fora; o resto do planeta está coberto. O BCSD usa a referência
# observacional GMFD, que só existe em terra, então os pixels de oceano vêm vazios.

# %%
print(f"fração de pixels sem dado no recorte NE (oceano): {float(ref.isel(time=0).isnull().mean()):.0%}; "
      f"dentro do NE: {float(ref.isel(time=0).where(M_NE).isnull().where(M_NE).mean()):.1%}")
for k, d in dados.items():
    for v, x in d.items():
        if x is None:
            continue
        vv = x.where(M_NE).values
        vv = vv[np.isfinite(vv)]
        print(f"{k:18s} {v:6s} mín {vv.min():7.2f} máx {vv.max():7.2f} média {vv.mean():7.2f}  ausentes(NE) "
              f"{float(x.where(M_NE).isnull().where(M_NE).mean()):.2%}")

# %% [markdown]
# **Veredito:** é global para áreas agrícolas (60°S–90°N, só terra) e uniforme no planeta. Os mesmos indicadores
# (dias ≥ 35 °C, chuva da quadra, ET0) podem ser calculados para qualquer fazenda do mundo em qualquer cenário.

# %% [markdown]
# ## 15.2 Mudanças projetadas no Ceará e no Nordeste (relativas ao histórico 2010–14 do próprio modelo)

# %%
linhas = []
base_tx = dados["hist 2010–14"]["tasmax"]
base_pr = dados["hist 2010–14"]["pr"]
for k, d in dados.items():
    tx, pr = d["tasmax"], d["pr"]
    if tx is None or pr is None:
        continue
    n_anos = tx.sizes["time"] / 365.25
    for nome, M in [("Ceará", M_CE), ("Nordeste", M_NE)]:
        linhas.append({
            "janela": k, "região": nome,
            "Tmax média (°C)": float(tx.where(M).mean()),
            "dias/ano Tmax≥35 °C (média dos pixels)": float((tx >= 35).where(M).sum("time").where(M).mean() / n_anos),
            "dias/ano Tmax≥38 °C": float((tx >= 38).where(M).sum("time").where(M).mean() / n_anos),
            "chuva anual (mm)": float(pr.where(M).sum("time").where(M).mean() / n_anos),
            "chuva fev–mai (mm)": float(pr.sel(time=pr.time.dt.month.isin([2, 3, 4, 5])).where(M).sum("time").where(M).mean() / n_anos),
        })
tab = pd.DataFrame(linhas).set_index(["região", "janela"]).round(1)
print(tab.to_string())
for reg in ["Ceará", "Nordeste"]:
    b = tab.loc[(reg, "hist 2010–14")]
    print(f"\n{reg} — variação contra 2010–14:")
    for k in list(JAN)[1:]:
        if (reg, k) in tab.index:
            r = tab.loc[(reg, k)]
            print(f"  {k}: ΔTmax {r['Tmax média (°C)'] - b['Tmax média (°C)']:+.1f} °C | dias≥35 °C "
                  f"{b['dias/ano Tmax≥35 °C (média dos pixels)']:.0f}→{r['dias/ano Tmax≥35 °C (média dos pixels)']:.0f} | "
                  f"chuva anual {r['chuva anual (mm)'] / b['chuva anual (mm)'] - 1:+.0%} | quadra {r['chuva fev–mai (mm)'] / b['chuva fev–mai (mm)'] - 1:+.0%}")

# %%
def nanos(x):
    return x.sizes["time"] / 365.25


fig, ax = plt.subplots(2, 3, figsize=(17, 10))
for j, k in enumerate(list(JAN)[1:]):
    tx, pr = dados[k]["tasmax"], dados[k]["pr"]
    if tx is None:
        continue
    dT = (tx.mean("time") - base_tx.mean("time")).where(M_NE)
    m = ax[0, j].pcolormesh(dT.lon, dT.lat, dT, cmap="Reds", vmin=0, vmax=5, shading="auto")
    plt.colorbar(m, ax=ax[0, j], shrink=0.8)
    ax[0, j].set_title(f"ΔTmax média (°C) — {k}", fontsize=10)
    dP = ((pr.sum("time") / nanos(pr)) / (base_pr.sum("time") / nanos(base_pr)) - 1).where(M_NE) * 100
    m = ax[1, j].pcolormesh(dP.lon, dP.lat, dP, cmap="BrBG", vmin=-40, vmax=40, shading="auto")
    plt.colorbar(m, ax=ax[1, j], shrink=0.8)
    ax[1, j].set_title(f"Δ chuva anual (%) — {k}", fontsize=10)
for a in ax.ravel():
    ne_gdf.boundary.plot(ax=a, color="k", lw=0.4)
    a.set_aspect("equal")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 15.3 Tendência entre janelas e variabilidade interanual (comparação com a seca de 2012)

# %%
serie = []
for k, (cen, anos) in JAN.items():
    tx, pr = dados[k]["tasmax"], dados[k]["pr"]
    if tx is None:
        continue
    for a in anos:
        t = tx.sel(time=str(a)).where(M_CE).mean().item()
        q = pr.sel(time=(pr.time.dt.year == a) & pr.time.dt.month.isin([2, 3, 4, 5])).where(M_CE).sum("time").where(M_CE).mean().item()
        d35 = (tx.sel(time=str(a)) >= 35).where(M_CE).sum("time").where(M_CE).mean().item()
        serie.append({"janela": k, "ano": a, "Tmax_media": t, "quadra_mm": q, "dias35": d35})
serie = pd.DataFrame(serie)
print(serie.groupby("janela")[["Tmax_media", "quadra_mm", "dias35"]].agg(["mean", "std", "min", "max"]).round(1).to_string())
imerg = DERIV / "imerg_ce_mensal.parquet"
if imerg.exists():
    i = pd.read_parquet(imerg)
    i = i[i.variavel == "precip_total"].set_index("data")["valor"]
    q_obs = i[i.index.month.isin([2, 3, 4, 5])].groupby(i[i.index.month.isin([2, 3, 4, 5])].index.year).sum()
    q_2012 = q_obs.loc[2012]
    hist_mod = serie[serie.janela == "hist 2010–14"].quadra_mm.mean()
    obs_2010_14 = q_obs.loc[2010:2014].mean()
    q_clim = q_obs.loc[1998:2025].mean()
    print(f"\nquadra observada (IMERG): climatologia 1998–2025 {q_clim:.0f} mm; 2010–14 {obs_2010_14:.0f} mm (inclui a seca); "
          f"2012 {q_2012:.0f} mm | modelo 'histórico 2010–14': {hist_mod:.0f} mm "
          f"({hist_mod/q_clim-1:+.0%} contra a climatologia observada).")
    print("  Atenção: os anos de um modelo climático NÃO correspondem aos anos reais (o modelo não 'sabe' que 2012 foi seco);"
          " só climatologias longas são comparáveis. Com 5 anos, essa diferença mistura viés e acaso.")
    lim = q_2012 / obs_2010_14  # 2012 como fração da média 2010-14
    for k in JAN:
        s = serie[serie.janela == k]
        frac = (s.quadra_mm / hist_mod < lim).mean()
        print(f"  {k}: anos com quadra relativa abaixo do nível de 2012: {frac:.0%} (n={len(s)})")
era5 = DERIV / "era5_ce_mensal.parquet"
if era5.exists():
    e = pd.read_parquet(era5)
    e = e[e.variavel == "tmax"].set_index("data")["valor"]
    print(f"Tmax média ERA5 2010–14 no Ceará: {e.loc['2010':'2014'].mean():.1f} °C vs NEX hist "
          f"{serie[serie.janela=='hist 2010–14'].Tmax_media.mean():.1f} °C")
fig, ax = plt.subplots(1, 2, figsize=(14, 4))
for k, g in serie.groupby("janela", sort=False):
    ax[0].plot(g.ano, g.Tmax_media, "o-", label=k)
    ax[1].plot(g.ano, g.dias35, "o-", label=k)
ax[0].set_title("Tmax média anual no Ceará (°C)")
ax[1].set_title("Dias com Tmax ≥ 35 °C por ano (média dos pixels do Ceará)")
ax[0].legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 15.4 Insights e desenho dos controles deslizantes
#
# 1. **O calor é o sinal robusto.** No Ceará (MPI-ESM1-2-HR, contra o próprio histórico 2010–14), a Tmax média sobe
#    +0,6 °C (SSP2-4.5, 2046–50), +0,9 °C (SSP5-8.5, 2046–50) e +1,9 °C (SSP5-8.5, 2086–90). Os **dias com Tmax ≥ 35 °C
#    passam de ~56/ano para ~78, ~98 e ~142/ano**, e os dias ≥ 38 °C de ~5 para ~10, ~14 e ~29/ano. Para culturas com
#    floração sensível a calor (feijão-comum, milho), a janela de plantio "segura" encolhe.
# 2. **A chuva é incerta.** O mesmo modelo dá −9 %, −6 % e +12 % na chuva anual nas três janelas. Esse sinal de
#    5 anos de um único modelo é dominado pela variabilidade interanual, na mesma escala da seca de 2012. O produto
#    deve mostrar a chuva futura como **faixa do ensemble** (p10–p90 entre modelos), nunca como um número.
# 3. **Desenho sugerido dos controles:** (a) "Aquecimento: +1 / +2 / +3 °C", que desloca a distribuição diária de
#    Tmax/Tmin observada (ERA5/POWER) e recalcula dias ≥ 35 °C, ET0 e graus-dia; (b) "Chuva da quadra: −30 % a
#    +20 %", que escala os dias de chuva do IMERG e recalcula veranicos e o balanço hídrico; (c) botão "usar
#    projeção SSP2-4.5/SSP5-8.5 2050", que aplica os deltas do ensemble NEX-GDDP. O método (a)+(b) é transparente
#    e explicável ao agricultor; o (c) dá a âncora científica.
# 4. **Combinação com a rotação:** cada estratégia candidata recebe uma nota de robustez, ou seja, a fração de
#    cenários em que ainda atinge a produtividade mínima. Isso favorece rotações com culturas de ciclo curto e
#    tolerantes ao calor.
#
# **Ideias de ML/DL:** emulador neural (MLP/gradient boosting) do modelo de cultivo, que recebe os deltas de cenário
# e responde em milissegundos no controle deslizante; seleção de subconjunto de modelos CMIP6 por desempenho
# histórico no NE (skill-weighting) antes de montar o ensemble.
