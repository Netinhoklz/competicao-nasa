# %% [markdown]
# # 11 · FAO GAEZ v4 — aptidão agrícola, clima agrícola e solo (global)
#
# **Pergunta do produto:** quais culturas *cabem* em cada lugar do mundo, em sequeiro ou irrigado, e com que produtividade possível?
#
# O GAEZ (Global Agro-Ecological Zones, FAO/IIASA) cruza clima (CRU-TS 1981–2010), solo (HWSD), relevo e exigências
# fisiológicas de dezenas de culturas. Ele vira o **filtro de culturas candidatas** do motor de rotação:
# antes de comparar rotações, descartamos o que o clima e o solo do pixel não sustentam.
#
# Camadas baixadas (306 GeoTIFFs globais, grade de 5′ ≈ 9,3 km no equador):
# aptidão e produtividade atingível de 17 culturas (res05), potencial de forrageiras (res02), recursos agroclimáticos
# 1981–2010 (res01) e séries anuais 1960–2010 (período de crescimento e chuva), solos/relevo/cobertura (LR),
# produção real 2010 (res06) e razão de produtividade alcançada (res07).

# %%
import sys, json, warnings
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import rasterio
from rasterio.windows import from_bounds
from rasterio.features import geometry_mask, rasterize
from scipy import stats
import pymannkendall as mk

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)
plt.rcParams.update({"figure.dpi": 90})

G = pasta("gaez")
sel = pd.read_csv(G / "selecao.csv")
LEG = json.loads((G / "legendas_gaez.json").read_text(encoding="utf-8"))
ce = ceara_gdf()
ne = nordeste_gdf()
mun = municipios_ce_gdf()


PIX = 1 / 12  # grade de 5 arc-min


def _snap(bbox):
    return (np.floor(bbox[0] / PIX) * PIX, np.floor(bbox[1] / PIX) * PIX,
            np.ceil(bbox[2] / PIX) * PIX, np.ceil(bbox[3] / PIX) * PIX)


def ler(arquivo, bbox=None):
    """Lê camada (opcionalmente recortada por bbox alinhado à grade de 5') -> (array float com NaN, transform).
    Camadas a 30" são agregadas por média de blocos 10×10 para a grade de 5'."""
    with rasterio.open(G / arquivo) as ds:
        fator = int(round(PIX / ds.res[0]))
        if bbox is not None:
            w = from_bounds(*_snap(bbox), transform=ds.transform).round_offsets().round_lengths()
            a = ds.read(1, window=w).astype("float32")
            tr = ds.window_transform(w)
        else:
            a = ds.read(1).astype("float32")
            tr = ds.transform
        nd = ds.nodata
    if nd is not None and not np.isnan(nd):
        a[a == nd] = np.nan
    if fator > 1:
        h, wd = a.shape[0] // fator, a.shape[1] // fator
        a = np.nanmean(a[:h * fator, :wd * fator].reshape(h, fator, wd, fator), axis=(1, 3))
        tr = rasterio.Affine(tr.a * fator, tr.b, tr.c, tr.d, tr.e * fator, tr.f)
    return a, tr


def arq(**filtro):
    m = sel.copy()
    for k, v in filtro.items():
        m = m[m[k] == v]
    if len(m) == 0:
        raise KeyError(filtro)
    return m.iloc[0]["arquivo"]


def mascara(geoms, shape, tr):
    return geometry_mask(list(geoms), out_shape=shape, transform=tr, invert=True)


def extent(tr, shape):
    return (tr.c, tr.c + tr.a * shape[1], tr.f + tr.e * shape[0], tr.f)


# grades de referência (Ceará e Nordeste)
_a, TR_CE = ler(arq(servico="res05", cultura="Maize", codigo="si_seq_alto"), BBOX_CE)
SH_CE = _a.shape
M_CE = mascara(ce.geometry, SH_CE, TR_CE)
_a, TR_NE = ler(arq(servico="res05", cultura="Maize", codigo="si_seq_alto"), BBOX_NE)
SH_NE = _a.shape
M_NE = mascara(ne[ne.geometry.bounds.minx > -34.0].geometry if False else ne.geometry, SH_NE, TR_NE)
print("Grade Ceará:", SH_CE, "pixels no estado:", int(M_CE.sum()), "| Grade NE:", SH_NE, "pixels na região:", int(M_NE.sum()))

# %% [markdown]
# ## 1. Ficha técnica

# %%
cat = pd.read_csv(G / "catalogo_gaez_completo.csv", usecols=["servico", "sub_theme_name", "year", "model"], low_memory=False)
resumo_cat = cat.groupby("servico").agg(camadas=("servico", "size"), subtemas=("sub_theme_name", "nunique"),
                                         periodos=("year", "nunique"))
print("Catálogo GAEZ v4 consultado (todas as camadas publicadas):")
print(resumo_cat.to_string())
print("\nCamadas baixadas por grupo:")
print(sel.groupby(["servico", "grupo"]).size().to_string())
with rasterio.open(G / sel.iloc[0]["arquivo"]) as ds:
    print(f"\nGrade: {ds.width}×{ds.height} px, pixel {ds.res[0]:.5f}° (~{ds.res[0]*111.32:.1f} km no equador), CRS {ds.crs}, "
          f"limites {tuple(round(b, 2) for b in ds.bounds)}")
print(f"Tamanho em disco: {tamanho_pasta(G)/1e9:.2f} GB (inclui catálogo de {(G/'catalogo_gaez_completo.csv').stat().st_size/1e6:.0f} MB)")

# %% [markdown]
# | Item | Valor |
# |---|---|
# | Provedor | FAO + IIASA (GAEZ v4, 2021) |
# | Clima de referência | CRU-TS 3.2, 1981–2010 (também 1960–2010 ano a ano e cenários CMIP5 até 2100 no catálogo) |
# | Solo | HWSD v1.2; relevo GMTED; cobertura do solo ~2010 |
# | Resolução | 5 arc-min (~9,3 km no equador); algumas camadas a 30″ |
# | Escala do índice de aptidão (SI) | 0–10000 (= SI×100). Classes: >7500 muito alta, >6300 alta, >5000 boa, >3500 média, >2000 moderada, >1000 marginal, >0 muito marginal, 0 inapto |
# | Acesso | ArcGIS ImageServer (catálogo) + GeoTIFF no S3 da FAO, aberto, sem cadastro |
# | Licença | CC BY 4.0 (FAO) |

# %% [markdown]
# ## 2. Validação de cobertura global
#
# Evidência: rasterizamos a máscara de terra do Natural Earth (1:50 m) na grade do GAEZ e medimos
# quantos pixels de terra têm valor válido (≥ 0) no índice de aptidão do milho e na fração de lavoura (LR).

# %%
si_g, tr_g = ler(arq(servico="res05", cultura="Maize", codigo="si_seq_alto"))
lav_g, _ = ler(arq(servico="LR", codigo="Cropland"))
terra = terra_gdf()
m_terra = rasterize(((g, 1) for g in terra.geometry), out_shape=si_g.shape, transform=tr_g, fill=0, dtype="uint8").astype(bool)
lat = tr_g.f + tr_g.e * (np.arange(si_g.shape[0]) + 0.5)
m_terra &= (lat > -60)[:, None]  # sem Antártida

val_si = ~np.isnan(si_g)
val_lav = ~np.isnan(lav_g)
print(f"Pixels de terra (Natural Earth): {m_terra.sum():,}")
print(f"  com SI do milho válido: {(val_si & m_terra).sum()/m_terra.sum():.1%}")
print(f"  com fração de lavoura válida: {(val_lav & m_terra).sum()/m_terra.sum():.1%}")
print(f"Pixels de oceano com valor (deveria ser ~0): {(val_si & ~m_terra).sum()/(~m_terra).sum():.2%}")
print(f"Latitudes com dado válido: {lat[val_si.any(axis=1)].min():.1f}° a {lat[val_si.any(axis=1)].max():.1f}°")
print(f"Pixels de terra com SI > 0 (alguma aptidão para milho): {((si_g > 0) & m_terra).sum()/m_terra.sum():.1%}")
# onde está a terra sem SI? (por faixa de latitude e por país)
sem = m_terra & ~val_si
print(f"Terra sem SI: {sem.sum():,} px; desses, {100*sem[lat > 60].sum()/max(sem.sum(),1):.0f}% acima de 60°N "
      f"(gelo/permafrost/água interior)")
paises_g = paises_gdf()
r_pais = rasterize(((g, i + 1) for i, g in enumerate(paises_g.geometry)), out_shape=si_g.shape, transform=tr_g, fill=0, dtype="int32")
cont = pd.Series(r_pais[sem]).value_counts().head(8)
print("Países com mais pixels de terra sem SI:", {paises_g.iloc[i - 1]["NAME"] if i > 0 else "fora de país": int(n) for i, n in cont.items()})

frac_lat = pd.DataFrame({"lat": lat, "terra": m_terra.sum(1), "valido": (val_si & m_terra).sum(1)})
frac_lat["cobertura"] = frac_lat["valido"] / frac_lat["terra"].replace(0, np.nan)

fig, ax = plt.subplots(1, 3, figsize=(18, 4.5), gridspec_kw={"width_ratios": [3, 3, 1]})
si_plot = np.where(m_terra, si_g, np.nan)[::3, ::3]
ax[0].imshow(si_plot / 100, extent=extent(tr_g, si_g.shape), cmap="YlGn", vmin=0, vmax=100)
ax[0].set_title("Aptidão do milho, sequeiro, insumo alto (SI 0–100)")
ax[1].imshow(lav_g[::3, ::3], extent=extent(tr_g, lav_g.shape), cmap="OrRd", vmin=0, vmax=100)
ax[1].set_title("Fração da célula com lavoura (%)")
ax[2].plot(frac_lat["cobertura"], frac_lat["lat"])
ax[2].set_xlim(0, 1.05); ax[2].set_title("Cobertura por latitude"); ax[2].set_xlabel("terra com dado")
for a in ax[:2]:
    a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()

# %% [markdown]
# **Veredito: GAEZ é GLOBAL de fato.** Todo pixel de terra fora da Antártida tem valor; o oceano fica sem dado.
# A limitação é a **resolução (~9 km)**: serve para dizer "que culturas cabem na região do talhão", não para o talhão em si.
# O refinamento intra-talhão vem de Landsat/Sentinel-2/SRTM (outras seções).

# %% [markdown]
# ## 3. Qualidade
#
# Faixa de valores, fração de "sem dado" e consistência interna no Nordeste (aptidão zero ⇒ produtividade atingível zero).

# %%
linhas = []
for _, r in sel[sel["servico"].isin(["res05", "res02"])].iterrows():
    a, _ = ler(r["arquivo"], BBOX_NE)
    v = a[M_NE]
    linhas.append({"cultura": r["cultura"], "codigo": r["codigo"], "unidade": r["unidade"],
                   "% sem dado NE": round(100 * np.isnan(v).mean(), 2), "min": np.nanmin(v), "max": np.nanmax(v),
                   "média NE": round(float(np.nanmean(v)), 1)})
q = pd.DataFrame(linhas)
print(q.pivot_table(index="cultura", columns="codigo", values="% sem dado NE").round(2).to_string())

inconsist = []
for crop in sel.loc[sel["servico"] == "res05", "cultura"].unique():
    si, _ = ler(arq(servico="res05", cultura=crop, codigo="si_seq_alto"), BBOX_NE)
    y, _ = ler(arq(servico="res05", cultura=crop, codigo="yld_seq_alto"), BBOX_NE)
    ok = M_NE & ~np.isnan(si) & ~np.isnan(y)
    inconsist.append({"cultura": crop, "SI=0 e produtividade>0 (%)": round(100 * ((si == 0) & (y > 0) & ok).sum() / ok.sum(), 2),
                      "SI>0 e produtividade=0 (%)": round(100 * ((si > 0) & (y == 0) & ok).sum() / ok.sum(), 2)})
print("\nConsistência SI × produtividade atingível (sequeiro, insumo alto, Nordeste):")
print(pd.DataFrame(inconsist).to_string(index=False))

# %% [markdown]
# ## 4. Ceará e Nordeste — ranking de culturas aptas
#
# Para cada cultura: SI médio, % da área com aptidão **boa ou melhor** (SI > 5000), e produtividade atingível média
# onde a cultura é ao menos moderadamente apta (SI > 2000).

# %%
CLASSES = [(7500, "muito alta"), (6300, "alta"), (5000, "boa"), (3500, "média"), (2000, "moderada"),
           (1000, "marginal"), (0, "muito marginal")]


def classe_si(v):
    out = np.full(v.shape, "inapta", dtype=object)
    for lim, nome in reversed(CLASSES):
        out[v > lim] = nome
    return out


crops = sel.loc[sel["servico"] == "res05", ["cultura", "cultura_pt"]].drop_duplicates().set_index("cultura")["cultura_pt"]
linhas, classes_ce = [], {}
for crop, pt in crops.items():
    for regiao, bbox, M in [("Ceará", BBOX_CE, M_CE), ("Nordeste", BBOX_NE, M_NE)]:
        for nivel, cod_si, cod_y in [("alto", "si_seq_alto", "yld_seq_alto"), ("baixo", "si_seq_baixo", "yld_seq_baixo")]:
            si, _ = ler(arq(servico="res05", cultura=crop, codigo=cod_si), bbox)
            y, _ = ler(arq(servico="res05", cultura=crop, codigo=cod_y), bbox)
            v, yv = si[M], y[M]
            apto = v > 2000
            linhas.append({"cultura": pt, "região": regiao, "insumo": nivel, "SI médio": np.nanmean(v) / 100,
                           "% área SI>50 (boa+)": 100 * np.nanmean(v > 5000), "% área SI>20": 100 * np.nanmean(apto),
                           "produtiv. atingível (kg/ha) onde SI>20": np.nanmean(yv[apto]) if apto.any() else np.nan})
            if regiao == "Ceará" and nivel == "alto":
                classes_ce[pt] = pd.Series(classe_si(v[~np.isnan(v)])).value_counts(normalize=True) * 100
rank = pd.DataFrame(linhas)
r_ce = rank[(rank["região"] == "Ceará") & (rank["insumo"] == "alto")].sort_values("SI médio", ascending=False)
print("Ranking no CEARÁ — sequeiro, insumo alto:")
print(r_ce.drop(columns=["região", "insumo"]).round(1).to_string(index=False))
print("\nRanking no CEARÁ — sequeiro, insumo baixo (agricultura familiar):")
print(rank[(rank["região"] == "Ceará") & (rank["insumo"] == "baixo")].sort_values("SI médio", ascending=False)
      .drop(columns=["região", "insumo"]).round(1).to_string(index=False))
print("\nRanking no NORDESTE — sequeiro, insumo baixo (agricultura familiar):")
print(rank[(rank["região"] == "Nordeste") & (rank["insumo"] == "baixo")].sort_values("SI médio", ascending=False)
      .drop(columns=["região", "insumo"]).round(1).to_string(index=False))
DERIV.mkdir(exist_ok=True, parents=True)
rank.to_parquet(DERIV / "gaez_ranking_culturas_ce_ne.parquet", index=False)

# %%
ordem = ["muito alta", "alta", "boa", "média", "moderada", "marginal", "muito marginal", "inapta"]
cores = ["#1a9641", "#73c378", "#c7e9a0", "#ffffbf", "#fdd17f", "#f99e59", "#e85b3a", "#bdbdbd"]
dfc = pd.DataFrame(classes_ce).T.reindex(columns=ordem).fillna(0).loc[r_ce["cultura"]]
ax = dfc.plot.barh(stacked=True, color=cores, figsize=(12, 7), width=0.85)
ax.invert_yaxis(); ax.set_xlabel("% da área do Ceará")
ax.set_title("Ceará: distribuição das classes de aptidão em sequeiro (insumo alto) — GAEZ v4, 1981–2010")
ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left")
plt.tight_layout(); plt.show()

# %%
top = r_ce["cultura"].head(8).tolist()
inv = {v: k for k, v in crops.items()}
fig, axs = plt.subplots(2, 4, figsize=(18, 8.5))
for ax, pt in zip(axs.ravel(), top):
    si, tr = ler(arq(servico="res05", cultura=inv[pt], codigo="si_seq_alto"), BBOX_NE)
    im = ax.imshow(np.where(M_NE, si / 100, np.nan), extent=extent(tr, si.shape), cmap="YlGn", vmin=0, vmax=100)
    ne.boundary.plot(ax=ax, color="grey", lw=0.4)
    ce.boundary.plot(ax=ax, color="k", lw=1.2)
    ax.set_title(f"{pt} (sequeiro, insumo alto)", fontsize=10)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
fig.colorbar(im, ax=axs, shrink=0.6, label="SI (0–100)")
fig.suptitle("Nordeste: índice de aptidão das 8 culturas mais aptas no Ceará (contorno preto = Ceará)")
plt.show()

# %% [markdown]
# ### Por mesorregião do Ceará (matriz cultura × região)

# %%
nomes = pd.DataFrame(json.loads((REF / "ceara_municipios_nomes.json").read_text(encoding="utf-8")))
nomes["meso"] = nomes["microrregiao"].apply(lambda m: m["mesorregiao"]["nome"])
mun["id"] = mun["codarea"].astype(int)
mm = mun.merge(nomes[["id", "nome", "meso"]], on="id")
mm["geometry"] = mm.geometry.make_valid().buffer(0)
meso = mm.dissolve(by="meso").reset_index()
meso["cod"] = np.arange(1, len(meso) + 1)
R_MESO = rasterize(((g, c) for g, c in zip(meso.geometry, meso["cod"])), out_shape=SH_CE, transform=TR_CE, fill=0, dtype="uint8")
print("pixels por mesorregião:", dict(zip(meso["meso"], [int((R_MESO == c).sum()) for c in meso["cod"]])))

mat = {}
for crop, pt in crops.items():
    si, _ = ler(arq(servico="res05", cultura=crop, codigo="si_seq_alto"), BBOX_CE)
    mat[pt] = {n: np.nanmean(si[R_MESO == c]) / 100 for n, c in zip(meso["meso"], meso["cod"])}
mat = pd.DataFrame(mat).T
mat = mat.loc[mat.mean(axis=1).sort_values(ascending=False).index]
fig, ax = plt.subplots(figsize=(11, 8))
sns.heatmap(mat, annot=True, fmt=".0f", cmap="YlGn", vmin=0, vmax=80, ax=ax, cbar_kws={"label": "SI médio (0–100)"})
ax.set_title("Ceará: aptidão média em sequeiro (insumo alto) por mesorregião")
plt.tight_layout(); plt.show()
mat.to_parquet(DERIV / "gaez_si_mesorregiao_ce.parquet")
print("Melhor cultura por mesorregião:", mat.idxmax().to_dict())

# %% [markdown]
# ## 5. Sequeiro × irrigado (lavoura atual, insumo alto)
#
# Mesma base de comparação: "lavoura atual na célula" com sequeiro × irrigação por gravidade.
# Ganho = quanto a irrigação eleva o SI e a produtividade atingível no Ceará. A mandioca não tem cenário irrigado no GAEZ.

# %%
linhas = []
for crop, pt in crops.items():
    try:
        s_r, _ = ler(arq(servico="res05", cultura=crop, codigo="si_lav_seq_alto"), BBOX_CE)
        s_i, _ = ler(arq(servico="res05", cultura=crop, codigo="si_lav_irr_alto"), BBOX_CE)
        y_r, _ = ler(arq(servico="res05", cultura=crop, codigo="yld_lav_seq_alto"), BBOX_CE)
        y_i, _ = ler(arq(servico="res05", cultura=crop, codigo="yld_lav_irr_alto"), BBOX_CE)
    except KeyError:
        continue
    # o SI irrigado só existe nas células com lavoura equipada para irrigação (fora delas vale 0):
    # compara nas MESMAS células (s_i > 0) para não confundir "sem irrigação instalada" com "inapto"
    ok = M_CE & ~np.isnan(s_r) & ~np.isnan(s_i) & (s_i > 0)
    linhas.append({"cultura": pt, "células comparadas": int(ok.sum()), "SI sequeiro": np.nanmean(s_r[ok]) / 100, "SI irrigado": np.nanmean(s_i[ok]) / 100,
                   "% área boa+ sequeiro": 100 * np.mean(s_r[ok] > 5000), "% área boa+ irrigado": 100 * np.mean(s_i[ok] > 5000),
                   "produtiv. sequeiro (kg/ha)": np.nanmean(y_r[ok & (y_r > 0)]) if (ok & (y_r > 0)).any() else 0,
                   "produtiv. irrigado (kg/ha)": np.nanmean(y_i[ok & (y_i > 0)]) if (ok & (y_i > 0)).any() else 0})
irr = pd.DataFrame(linhas)
irr["ganho SI (pontos)"] = irr["SI irrigado"] - irr["SI sequeiro"]
irr["fator produtiv."] = irr["produtiv. irrigado (kg/ha)"] / irr["produtiv. sequeiro (kg/ha)"].replace(0, np.nan)
irr = irr.sort_values("ganho SI (pontos)", ascending=False)
print(irr.round(1).to_string(index=False))

fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(irr))
ax.bar(x - 0.2, irr["SI sequeiro"], 0.4, label="sequeiro")
ax.bar(x + 0.2, irr["SI irrigado"], 0.4, label="irrigado (gravidade)")
ax.set_xticks(x); ax.set_xticklabels(irr["cultura"], rotation=45, ha="right")
ax.set_ylabel("SI médio no Ceará (0–100)"); ax.legend()
ax.set_title("Ceará: quanto a irrigação muda a aptidão (lavoura atual, insumo alto)")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6. Clima agrícola (res01, 1981–2010)
#
# Período de crescimento (LGP: dias em que chuva + reserva do solo ≥ metade da evapotranspiração), início do LGP,
# dias de calor extremo, déficit hídrico, erosividade (índice de Fournier) e quantas safras por ano o clima permite.

# %%
def r01(trecho):
    m = sel[(sel["servico"] == "res01") & sel["variavel"].str.contains(trecho, regex=False)]
    return m.iloc[0]["arquivo"]


VARS = {
    "LGP total (dias)": "Total number of growing period days",
    "Início do LGP mais longo (dia do ano)": "Beginning date of longest component LGP",
    "LGP mais longo (dias)": "Length of longest component LGP",
    "Dias com Tmax > 35 °C": "Number of days with Tmax > 35",
    "Dias com Tmax > 40 °C": "Number of days with Tmax > 40",
    "Chuva anual (mm)": "Annual precipitation (mm)",
    "ETP de referência (mm)": "Reference potential evapotranspiration",
    "Déficit de ET (mm)": "Reference evapotranspiration deficit",
    "Dias de chuva (P > 1 mm)": "Total number of rain days",
    "Maior veranico no período de crescimento (dias)": "Longest period of consecutive dry days",
    "Temperatura média anual (°C)": "Mean annual temperature",
    "Graus-dia (Ta > 10 °C)": "Annual temperature sum for days with Ta>10",
}
linhas, campos = [], {}
for rot, trecho in VARS.items():
    a, tr = ler(r01(trecho), BBOX_NE)
    campos[rot] = (a, tr)
    for regiao, M in [("Ceará", None), ("Nordeste", M_NE)]:
        if regiao == "Ceará":
            b, _ = ler(r01(trecho), BBOX_CE)
            v = b[M_CE]
        else:
            v = a[M]
        if "dia do ano" in rot:  # variável circular: média circular e percentis não fazem sentido direto
            ang = 2 * np.pi * v[~np.isnan(v)] / 365
            media_c = (np.degrees(np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())) % 360) / 360 * 365
            linhas.append({"variável": rot + " [média circular]", "região": regiao, "média": media_c, "p10": np.nan,
                           "mediana": np.nan, "p90": np.nan, "desvio": np.nan})
            continue
        linhas.append({"variável": rot, "região": regiao, "média": np.nanmean(v), "p10": np.nanpercentile(v, 10),
                       "mediana": np.nanmedian(v), "p90": np.nanpercentile(v, 90), "desvio": np.nanstd(v)})
agro = pd.DataFrame(linhas)
print(agro.pivot_table(index="variável", columns="região", values=["média", "p10", "p90"]).round(1).to_string())

# %%
mostrar = ["LGP total (dias)", "Início do LGP mais longo (dia do ano)", "Dias com Tmax > 35 °C", "Déficit de ET (mm)",
           "Chuva anual (mm)", "Maior veranico no período de crescimento (dias)"]
cmaps = ["YlGn", "twilight", "OrRd", "Reds", "Blues", "Purples"]
fig, axs = plt.subplots(2, 3, figsize=(18, 10))
for ax, rot, cm in zip(axs.ravel(), mostrar, cmaps):
    a, tr = campos[rot]
    im = ax.imshow(np.where(M_NE, a, np.nan), extent=extent(tr, a.shape), cmap=cm)
    ne.boundary.plot(ax=ax, color="grey", lw=0.4)
    ce.boundary.plot(ax=ax, color="k", lw=1.2)
    ax.set_title(rot); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    fig.colorbar(im, ax=ax, shrink=0.7)
plt.suptitle("Nordeste — recursos agroclimáticos GAEZ (1981–2010)")
plt.tight_layout(); plt.show()

ini, _ = ler(r01("Beginning date of longest component LGP"), BBOX_CE)
mes_ini = pd.to_datetime(ini[M_CE][~np.isnan(ini[M_CE])].astype(int).clip(1, 365) - 1, unit="D", origin="2001-01-01").month
print("Ceará — mês de início do período de crescimento (% da área):")
print((pd.Series(mes_ini).value_counts(normalize=True).sort_index() * 100).round(1).to_string())

# %% [markdown]
# ### Quantas safras por ano? (classe de multicultivo, sequeiro × irrigado)

# %%
nomes_mc = [i["rotulo"] for i in LEG["res01"]["Multi-cropping Class"]]
mc = {}
for rot, trecho in [("sequeiro", "Multi-cropping class (rain-fed)"), ("irrigado", "Multi-cropping class (with irrigation)")]:
    for regiao, bbox, M in [("Ceará", BBOX_CE, M_CE), ("Nordeste", BBOX_NE, M_NE)]:
        a, _ = ler(r01(trecho), bbox)
        v = a[M]; v = v[~np.isnan(v)].astype(int)
        cont = pd.Series(v).value_counts(normalize=True) * 100
        cont.index = [nomes_mc[i - 1] if 1 <= i <= len(nomes_mc) else f"código {i}" for i in cont.index]
        mc[(regiao, rot)] = cont
mc = pd.DataFrame(mc).fillna(0).round(1)
print("Classe de multicultivo (% da área) — rótulos na ordem da legenda oficial do serviço res01:")
print(mc.to_string())

# %% [markdown]
# ## 7. Solo, relevo e uso da terra (LR)

# %%
def lr(trecho):
    m = sel[(sel["servico"] == "LR") & (sel["variavel"] == trecho)]
    return m.iloc[0]["arquivo"]


def dist_classes(trecho, legenda, bbox=BBOX_CE, M=None, deslocamento=0):
    M = M_CE if M is None else M
    a, _ = ler(lr(trecho), bbox)
    v = a[M]; v = v[~np.isnan(v)].astype(int)
    s = pd.Series(v).value_counts(normalize=True) * 100
    s.index = [legenda[i - deslocamento] if 0 <= i - deslocamento < len(legenda) else f"código {i}" for i in s.index]
    return s.round(1)


leg_solo = [i["rotulo"] for i in LEG["LR"]["Dominant Soil"]]
leg_sq = [i["rotulo"] for i in LEG["LR"]["Limiting Soil Quality"]]
leg_mr = [i["rotulo"] for i in LEG["LR"]["Moisture Regime Class"]]
leg_lc = [i["rotulo"] for i in LEG["LR"]["Dominant Land Cover"]]
leg_aez = [i["rotulo"] for i in LEG["LR"]["AEZ Classification (33 Classes)"]]
print("Solo dominante no Ceará (% da área; rótulos HWSD na ordem da legenda, 'NA'=0):")
print(dist_classes("Dominant soil (5 arc-minute)", leg_solo).head(12).to_string())
print("\nQualidade de solo mais limitante (insumo baixo):")
print(dist_classes("Most limiting soil quality, low inputs", leg_sq).to_string())
print("\nRegime de umidade (LGP):")
print(dist_classes("Moisture regime class", leg_mr).to_string())
print("\nZona agroecológica dominante (33 classes):")
print(dist_classes("Dominant AEZ class (33 classes) at 5 arc-minutes", leg_aez).head(8).to_string())
print("\nCobertura dominante (rótulos na ordem da legenda, início em 1):")
print(dist_classes("Dominant land cover/use", leg_lc, deslocamento=1).to_string())

fr = {}
for rot, trecho in [("lavoura %", "Cropland"), ("pastagem/campo %", "Grassland"),
                    ("lavoura irrigável %", "Cropland, equipped for full control irrigation"),
                    ("ruminantes (UA/km²)", "Ruminant livestock density (year 2010)"), ("altitude mediana (m)", "Median altitude (5 arc-minute)")]:
    for regiao, bbox, M in [("Ceará", BBOX_CE, M_CE), ("Nordeste", BBOX_NE, M_NE)]:
        a, _ = ler(lr(trecho), bbox)
        fr[(rot, regiao)] = np.nanmean(a[M])
print("\nMédias de uso da terra e relevo:")
print(pd.Series(fr).unstack().round(2).to_string())

# %% [markdown]
# ## 8. Tendências 1960–2010 (séries anuais CRU-TS do GAEZ)
#
# Período de crescimento (LGP) e chuva anual: média do Ceará por ano, Mann-Kendall + Sen, e mapa de tendência por pixel no Nordeste
# (Mann-Kendall vetorizado; significância a 5 %).

# %%
anuais = sel[sel["servico"] == "res01_anual"].copy()
anuais["ano"] = anuais["ano"].astype(int)
series, cubos = {}, {}
for cod in ["lgp_anual", "prec_anual"]:
    sub = anuais[anuais["codigo"] == cod].sort_values("ano")
    pilha = []
    for _, r in sub.iterrows():
        a, tr_ne = ler(r["arquivo"], BBOX_NE)
        pilha.append(a)
    cubo = np.stack(pilha)  # (anos, y, x)
    cubos[cod] = (cubo, sub["ano"].values)
    a_ce = []
    for _, r in sub.iterrows():
        b, _ = ler(r["arquivo"], BBOX_CE)
        a_ce.append(np.nanmean(b[M_CE]))
    series[cod] = pd.Series(a_ce, index=sub["ano"].values)
ser = pd.DataFrame(series)
ser.columns = ["LGP (dias)", "chuva (mm)"]
ser.index.name = "ano"
ser.to_parquet(DERIV / "gaez_ce_lgp_chuva_anual_1960_2010.parquet")

for c in ser.columns:
    t = mk.original_test(ser[c].values)
    print(f"{c}: tendência={t.trend}, p={t.p:.3f}, Sen={t.slope:.2f}/ano ({100*t.slope/ser[c].mean():.2f} %/ano), média={ser[c].mean():.0f}")
print("Correlação de Pearson LGP × chuva (Ceará, anual):", round(ser.corr().iloc[0, 1], 3))

fig, ax = plt.subplots(figsize=(13, 4))
ax.bar(ser.index, ser["chuva (mm)"], color="tab:blue", alpha=0.5, label="chuva anual (mm)")
ax2 = ax.twinx()
ax2.plot(ser.index, ser["LGP (dias)"], "g-o", ms=3, label="LGP (dias)")
ax.set_title("Ceará — chuva anual e período de crescimento (GAEZ/CRU-TS, média estadual)")
ax.legend(loc="upper left"); ax2.legend(loc="upper right")
plt.tight_layout(); plt.show()


def mk_vetorizado(cubo):
    """Mann-Kendall por pixel (sem correção de empates) + inclinação de Sen. cubo: (n, y, x)."""
    n = cubo.shape[0]
    X = cubo.reshape(n, -1)
    S = np.zeros(X.shape[1], dtype="float64")
    pares = []
    for i in range(n - 1):
        d = X[i + 1:] - X[i]
        S += np.nansum(np.sign(d), axis=0)
        pares.append(d / np.arange(1, n - i)[:, None])
    var = n * (n - 1) * (2 * n + 5) / 18
    Z = np.where(S > 0, (S - 1) / np.sqrt(var), np.where(S < 0, (S + 1) / np.sqrt(var), 0))
    p = 2 * (1 - stats.norm.cdf(np.abs(Z)))
    sen = np.nanmedian(np.concatenate(pares, axis=0), axis=0)
    shp = cubo.shape[1:]
    return sen.reshape(shp), p.reshape(shp)


fig, axs = plt.subplots(1, 2, figsize=(15, 6))
for ax, (cod, rot, un) in zip(axs, [("lgp_anual", "LGP", "dias/década"), ("prec_anual", "chuva anual", "mm/década")]):
    cubo, anos = cubos[cod]
    sen, p = mk_vetorizado(cubo)
    sen10 = np.where(M_NE, sen * 10, np.nan)
    lim = np.nanpercentile(np.abs(sen10), 98)
    im = ax.imshow(sen10, extent=extent(tr_ne, sen.shape), cmap="RdBu", vmin=-lim, vmax=lim)
    yy, xx = np.where(M_NE & (p < 0.05))
    xs = tr_ne.c + (xx + 0.5) * tr_ne.a
    ys = tr_ne.f + (yy + 0.5) * tr_ne.e
    ax.scatter(xs[::3], ys[::3], s=0.3, c="k", alpha=0.5)
    ne.boundary.plot(ax=ax, color="grey", lw=0.4); ce.boundary.plot(ax=ax, color="k", lw=1.2)
    ax.set_title(f"Tendência de {rot} 1960–2010 (Sen, {un}); pontos = p<0,05")
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    fig.colorbar(im, ax=ax, shrink=0.7)
    print(f"{rot}: % da área do NE com tendência significativa: {100*np.mean(p[M_NE] < 0.05):.1f}% "
          f"(queda: {100*np.mean((p[M_NE] < 0.05) & (sen[M_NE] < 0)):.1f}%, alta: {100*np.mean((p[M_NE] < 0.05) & (sen[M_NE] > 0)):.1f}%)")
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 9. Variabilidade e extremos (1960–2010)
#
# - Anos mais secos do Ceará (anomalia de chuva e LGP).
# - **Risco de "ano sem safra"**: fração dos anos em que o LGP do pixel ficou abaixo de 60 dias (regime árido) — um mapa direto
#   de risco climático para culturas de sequeiro.
# - Coeficiente de variação interanual do LGP.

# %%
anom = (ser - ser.mean()) / ser.std()
print("Anos mais secos no Ceará (z-score da chuva e do LGP):")
print(anom.sort_values("chuva (mm)").head(10).round(2).to_string())
print("\nAnos mais chuvosos:")
print(anom.sort_values("chuva (mm)", ascending=False).head(5).round(2).to_string())

cubo_lgp, anos = cubos["lgp_anual"]
risco = np.nanmean(cubo_lgp < 60, axis=0)
cv = np.nanstd(cubo_lgp, axis=0) / np.nanmean(cubo_lgp, axis=0)
fig, axs = plt.subplots(1, 2, figsize=(15, 6))
for ax, campo, rot, cm in [(axs[0], risco, "fração dos anos com LGP < 60 dias", "Reds"),
                           (axs[1], cv, "CV interanual do LGP", "magma_r")]:
    im = ax.imshow(np.where(M_NE, campo, np.nan), extent=extent(tr_ne, campo.shape), cmap=cm)
    ne.boundary.plot(ax=ax, color="grey", lw=0.4); ce.boundary.plot(ax=ax, color="k", lw=1.2)
    ax.set_title(rot); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    fig.colorbar(im, ax=ax, shrink=0.7)
plt.tight_layout(); plt.show()
cubo_ce = np.stack([ler(r["arquivo"], BBOX_CE)[0] for _, r in anuais[anuais["codigo"] == "lgp_anual"].sort_values("ano").iterrows()])
risco_ce = np.nanmean(cubo_ce < 60, axis=0)[M_CE]
print(f"Ceará: fração média de anos com LGP < 60 dias = {np.nanmean(risco_ce):.1%}; "
      f"pixels com risco ≥ 20 %: {np.mean(risco_ce >= 0.2):.1%}")
print("Anos em que mais de 30 % do Ceará teve LGP < 60 dias:",
      [int(a) for a, f in zip(sorted(anuais.loc[anuais['codigo'] == 'lgp_anual', 'ano']), [np.mean(c[M_CE] < 60) for c in cubo_ce]) if f > 0.3])

# %% [markdown]
# ## 10. Aptidão potencial × produção real (2010)
#
# Se o GAEZ é um bom filtro, onde a aptidão é maior a produtividade real (res06, 2010) deveria ser maior.
# Correlação de Spearman pixel a pixel (só pixels com cultivo em 2010), em quatro escalas.

# %%
PARES = {"Maize": "Maize", "Sorghum": "Sorghum", "Cassava": "Cassava", "Cotton": "Cotton", "Soybean": "Soybean",
         "Wetland rice": "Wetland rice", "Wheat": "Wheat", "Pearl millet": "Millet", "Groundnut": "Groundnut",
         "Sugarcane": "Sugarcane", "Banana": "Banana", "Sunflower": "Sunflower", "Cowpea": "Pulses"}
BBOX_BR = (-74.0, -34.0, -34.7, 5.5)
escalas = {"Ceará": (BBOX_CE, M_CE), "Nordeste": (BBOX_NE, M_NE), "Brasil (bbox)": (BBOX_BR, None), "Mundo": (None, None)}
rng = np.random.default_rng(0)
linhas = []
for crop_si, crop_real in PARES.items():
    f_si = arq(servico="res05", cultura=crop_si, codigo="si_seq_alto")
    f_y = sel[(sel["servico"] == "res06") & (sel["cultura"] == crop_real) & (sel["variavel"] == "Yield")]
    if f_y.empty:
        continue
    f_y = f_y.iloc[0]["arquivo"]
    lin = {"cultura GAEZ": crops.get(crop_si, crop_si), "produção real (classe)": crop_real}
    for nome, (bbox, M) in escalas.items():
        si, _ = ler(f_si, bbox)
        y, _ = ler(f_y, bbox)
        ok = ~np.isnan(si) & (y > 0) & ~np.isnan(y)
        if M is not None:
            ok &= M
        x1, x2 = si[ok], y[ok]
        if len(x1) > 200000:
            idx = rng.choice(len(x1), 200000, replace=False)
            x1, x2 = x1[idx], x2[idx]
        lin[f"ρ {nome}"] = stats.spearmanr(x1, x2).correlation if len(x1) > 30 else np.nan
        lin[f"n {nome}"] = int(ok.sum())
    linhas.append(lin)
corr = pd.DataFrame(linhas)
print(corr.round(2).to_string(index=False))

# %% [markdown]
# ### Validação externa: GAEZ × IBGE (PAM) no Ceará
#
# Consulta pontual ao IBGE/SIDRA (tabela 1612, Ceará, 1974–2024) só para validar. Compara:
# (a) a "produção real 2010" do GAEZ (res06) agregada no estado com o IBGE 2010;
# (b) a produtividade atingível do GAEZ (sequeiro, insumo baixo e alto) com a produtividade observada 1981–2010.

# %%
ibge = pd.read_csv(G / "validacao_ibge_pam_ce_1974_2024.csv")
rend_ibge = ibge[ibge["variavel"] == "Rendimento médio da produção"].pivot_table(index="ano", columns="produto", values="valor")
area_ibge = ibge[ibge["variavel"] == "Área colhida"].pivot_table(index="ano", columns="produto", values="valor")
MAP_IBGE = {"Maize": "Milho (em grão)", "Cotton": "Algodão herbáceo (em caroço)", "Cassava": "Mandioca",
            "Soybean": "Soja (em grão)"}
linhas = []
for crop, prod_ibge in MAP_IBGE.items():
    fy = sel[(sel["servico"] == "res06") & (sel["cultura"] == crop) & (sel["variavel"] == "Yield")].iloc[0]["arquivo"]
    fp = sel[(sel["servico"] == "res06") & (sel["cultura"] == crop) & (sel["variavel"] == "Production")].iloc[0]["arquivo"]
    y6, _ = ler(fy, BBOX_CE); p6, _ = ler(fp, BBOX_CE)
    ok = M_CE & (y6 > 0) & (p6 > 0)
    area_g = (p6[ok] * 1000 / y6[ok]).sum()
    lin = {"cultura": crop, "GAEZ 2010: produtiv. (kg/ha)": 1e6 * p6[ok].sum() / area_g if area_g else np.nan,
           "IBGE 2010: produtiv. (kg/ha)": rend_ibge.loc[2010, prod_ibge],
           "GAEZ 2010: área (mil ha)": area_g / 1e3, "IBGE 2010: área (mil ha)": area_ibge.loc[2010, prod_ibge] / 1e3}
    gaez_crop = {"Maize": "Maize", "Cotton": "Cotton", "Cassava": "Cassava", "Soybean": "Soybean"}[crop]
    for cod, rot in [("yld_seq_baixo", "GAEZ atingível insumo baixo"), ("yld_seq_alto", "GAEZ atingível insumo alto")]:
        ya, _ = ler(arq(servico="res05", cultura=gaez_crop, codigo=cod), BBOX_CE)
        lin[rot + " (kg/ha)"] = np.nanmean(ya[M_CE & (ya > 0)])
    # conversão aproximada IBGE -> base do GAEZ (matéria seca; algodão em pluma)
    conv = {"Maize": 0.87, "Soybean": 0.87, "Cassava": 0.35, "Cotton": 0.38}[crop]
    obs = rend_ibge.loc[1981:2010, prod_ibge] * conv
    lin["fator IBGE→GAEZ (aprox.)"] = conv
    lin["IBGE média 1981–2010 convertida (kg/ha)"] = obs.mean()
    lin["IBGE máx. 1981–2010 convertida (kg/ha)"] = obs.max()
    lin["IBGE / atingível insumo baixo"] = obs.mean() / lin["GAEZ atingível insumo baixo (kg/ha)"]
    lin["IBGE / atingível insumo alto"] = obs.mean() / lin["GAEZ atingível insumo alto (kg/ha)"]
    linhas.append(lin)
val = pd.DataFrame(linhas).set_index("cultura").T
print(val.round(2).to_string())
print("\nConversões aproximadas: grão a 13 % de umidade → matéria seca ×0,87; mandioca fresca → seca ×0,35; "
      "algodão em caroço → pluma ×0,38. A produção 'real 2010' do GAEZ fica 19× acima do IBGE no milho e com área 4× menor.")

# %% [markdown]
# ### Clima anual do GAEZ × produtividade real (IBGE), Ceará 1974–2010
#
# Anomalias de produtividade (razão à mediana móvel de 7 anos, para tirar a tendência tecnológica) contra chuva anual e LGP.

# %%
ser_v = ser.loc[1974:2010]
an_rend = rend_ibge.loc[1974:2010, ["Milho (em grão)", "Feijão (em grão)", "Mandioca", "Algodão herbáceo (em caroço)"]]
an_rend = an_rend / an_rend.rolling(7, center=True, min_periods=3).median() - 1
linhas = []
for c in an_rend.columns:
    for v in ser_v.columns:
        x = pd.concat([an_rend[c], ser_v[v]], axis=1).dropna()
        rho, p = stats.spearmanr(x.iloc[:, 0], x.iloc[:, 1])
        linhas.append({"cultura": c, "variável GAEZ": v, "ρ Spearman": round(rho, 2), "p": round(p, 4), "n": len(x)})
print(pd.DataFrame(linhas).to_string(index=False))
fig, axs = plt.subplots(1, 2, figsize=(14, 4.5))
for ax, c in zip(axs, ["Milho (em grão)", "Feijão (em grão)"]):
    x = pd.concat([an_rend[c], ser_v["chuva (mm)"]], axis=1).dropna()
    ax.scatter(x["chuva (mm)"], 100 * x[c])
    for ano, r in x.iterrows():
        if abs(r[c]) > 0.5:
            ax.annotate(str(ano), (r["chuva (mm)"], 100 * r[c]), fontsize=7)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel("chuva anual GAEZ/CRU-TS no Ceará (mm)"); ax.set_ylabel("anomalia de produtividade IBGE (%)")
    ax.set_title(f"{c}: produtividade × chuva anual (1974–2010)")
plt.tight_layout(); plt.show()
print("Produtividade do milho no Ceará (IBGE), anos recentes (kg/ha):", rend_ibge.loc[2010:2024, "Milho (em grão)"].astype(int).to_dict())
alg = area_ibge["Algodão herbáceo (em caroço)"] / 1000
print("Área colhida de algodão herbáceo no Ceará (mil ha):", alg.loc[[1974, 1980, 1985, 1990, 2000, 2005, 2010, 2015, 2024]].round(1).to_dict())
fig, ax = plt.subplots(figsize=(12, 3.5))
(area_ibge[["Milho (em grão)", "Feijão (em grão)", "Mandioca", "Algodão herbáceo (em caroço)"]] / 1000).plot(ax=ax)
ax.set_ylabel("mil ha"); ax.set_title("Ceará — área colhida (IBGE PAM): o algodão herbáceo sumiu apesar da alta aptidão climática no GAEZ")
plt.tight_layout(); plt.show()

# %% [markdown]
# **Atenção:** a razão de produtividade alcançada (res07) abaixo é derivada da produção real de 2010 (res06), que a validação acima mostrou
# estar muito distante do IBGE no Ceará. Fica registrada apenas como evidência de que essa camada **não deve** ser usada no produto para o Ceará.

# %%
leg_gap =[i["rotulo"] for i in LEG["res07"]["Yield and Production Gaps Symbology"]]
gap = {}
for _, r in sel[sel["servico"] == "res07"].iterrows():
    a, _ = ler(r["arquivo"], BBOX_CE)
    v = a[M_CE]; v = v[~np.isnan(v) & (v > 0)].astype(int)
    if len(v) < 10:
        continue
    s = pd.Series(v).value_counts(normalize=True) * 100
    s.index = [leg_gap[i] if i < len(leg_gap) else f"código {i}" for i in s.index]
    gap[r["cultura"]] = s
gap = pd.DataFrame(gap).T.reindex(columns=leg_gap[1:]).fillna(0).round(1)
print("Ceará — razão produtividade real / atingível em 2010 (% dos pixels cultivados por classe):")
print(gap.to_string())
if len(gap):
    ax = gap.plot.barh(stacked=True, cmap="RdYlGn", figsize=(11, 5))
    ax.set_xlabel("% dos pixels com a cultura no Ceará"); ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", title="real/atingível")
    ax.set_title("Ceará — quanto da produtividade possível é alcançada (GAEZ res07, 2010)")
    plt.tight_layout(); plt.show()

# %% [markdown]
# ## 11. Insights e ideias para o produto
#
# 1. **GAEZ é global de verdade e serve de filtro de candidatas.** 99,8 % dos pixels de terra (sem Antártida) têm aptidão calculada, de 56°S a 84°N.
#    Para qualquer ponto: `candidatas = {cultura | SI_sequeiro(insumo do agricultor) > 35}` ∪ `{cultura | SI_irrigado > 35 e há água}`.
#    É o primeiro estágio do motor de rotação, antes do clima recente (POWER/IMERG/SMAP) e do talhão (Landsat/Sentinel-2/SRTM).
# 2. **O nível de insumo decide o ranking no Ceará.** Com insumo alto, algodão (71), sorgo (63), milho (60), guandu, milheto, soja e feijões (~58)
#    ficam todos "bons"; com **insumo baixo** (agricultura familiar) lideram **sorgo, mandioca, guandu e feijão** (~50–53) e o algodão despenca (35).
#    O produto precisa perguntar o nível tecnológico — ele muda a recomendação.
# 3. **Irrigação destrava culturas específicas** (mesmas células): banana 0→68, cana 3→53, arroz 30→66; para grãos e leguminosas o ganho de aptidão é ~0
#    (o clima médio já os permite) — no semiárido a irrigação vale mais para fruticultura/cana do que para grãos.
# 4. **Calendário da rotação:** no Ceará o período de crescimento começa entre dez e jan (média circular ≈ 8 de janeiro) e **77,5 % da área só
#    comporta uma safra de sequeiro** (22 % "dupla limitada"). Logo, a decisão-chave da rotação é *o que fica no solo na entressafra*
#    (cobertura, forrageira, leguminosa perene como guandu), não uma segunda safra de grão.
# 5. **Clima explica a produtividade real:** anomalias de produtividade do IBGE (1974–2010) correlacionam com o LGP anual do GAEZ
#    (milho ρ = 0,59; feijão 0,47; p < 0,01) — mas o LGP mensal do GAEZ quase nunca cai abaixo de 60 dias e não "viu" a seca de 2010
#    (produtividade do milho 316 kg/ha). **Veranicos dentro da estação** só aparecem com dados diários (IMERG/POWER/SMAP): o risco do produto
#    deve vir deles, e o GAEZ entra como aptidão média.
# 6. **Lacuna de produtividade enorme:** o milho real do Ceará (IBGE 1981–2010, convertido) fica em ~24 % do atingível com insumo baixo e ~7 % com insumo alto.
#    O ganho vem de manejo (água no solo, cobertura, rotação com leguminosa), não de trocar o clima — argumento central do pitch.
# 7. **A camada de "produção real 2010" do GAEZ (res06/res07) é inútil no Ceará:** milho 19× acima do IBGE e área 4× menor. Além disso, as correlações
#    aptidão × produção real (seção 10) são parcialmente circulares (a desagregação usa a própria aptidão). Para o Brasil, usar IBGE PAM municipal;
#    para o mundo, FAOSTAT nacional + SPAM com cautela.
# 8. **Algodão: aptidão alta, área zero.** O algodão herbáceo caiu de 306 mil ha (1985) para ~2 mil ha (2010–2024) no Ceará. Clima e solo não explicam
#    a saída (com insumo alto ele é a cultura mais apta) — pragas (bicudo-do-algodoeiro, desde os anos 1980), mercado e crédito sim. É o exemplo
#    perfeito de por que o motor precisa de uma camada de **pragas/ciclo de pragas** e de **mercado**, além de clima e solo.
# 9. **Solo do Ceará:** Luvissolos (36 %), Regossolos, Planossolos, Latossolos; a limitação mais comum é **retenção de nutrientes** (39 %) e oxigênio
#    (Planossolos, 12 %) — favorece rotações que aumentam matéria orgânica (leguminosas, palhada) e evita culturas sensíveis a encharcamento nas baixadas.
# 10. **Tendência 1960–2010:** sem tendência significativa no Ceará como um todo; no Nordeste, 11,5 % da área tem queda significativa do LGP e nenhuma área tem alta.
#     **Cenários CMIP5 até 2100 estão no catálogo** com as mesmas variáveis — base pronta para o slider de clima futuro.
#
# **Limitações:** clima-base 1981–2010 e séries só até 2010 (não captura a seca de 2012–2017); resolução de 9 km; dias com Tmax > 35 °C subestimados
# (interpolação de dados mensais); HWSD é grosseiro no semiárido; caju/castanha e palma forrageira não existem no GAEZ; rótulos de classes
# mapeados pela ordem da legenda oficial do serviço (consistentes com os solos conhecidos do Ceará).
