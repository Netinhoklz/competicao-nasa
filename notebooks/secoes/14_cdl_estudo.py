# %% [markdown]
# ## 14. USDA Cropland Data Layer (CDL) — estudo de rotação real (somente EUA)
#
# **Ficha técnica**
#
# | Item | Valor |
# |---|---|
# | Provedor | USDA NASS (Serviço Nacional de Estatística Agrícola dos EUA) |
# | Conteúdo | **Qual cultura está em cada pixel, a cada ano** (~130 classes) |
# | Resolução | 30 m (2008–2025); 10 m também a partir de 2024 |
# | Período | Nacional desde 2008 (alguns estados desde 1997) |
# | Cobertura | **EUA contíguos (CONUS)**; o Havaí vem num arquivo à parte |
# | Acesso | Download direto do NASS (zip por ano, ~1,7–2 GB); o CropScape agora pede cadastro |
# | Arquivos baixados | 2023, 2024 e 2025 (30 m) + camada de **frequência de culturas 2008–2025** |
#
# Ficou numa pasta separada (`E:/campeonato-nasa/estudo_cdl`) porque **não é global**. O valor dele para nós é
# **aprender como rotações reais se comportam** (ex.: milho→soja), para construir o "prior" do motor de rotação e testar
# o método num lugar com rótulos de verdade.
#
# Para ler os rasters nacionais sem descompactar 2,6 GB por ano, foram recortadas 6 janelas de 40 × 40 km
# (`scripts/recortar_cdl.py`), mais uma visão nacional reduzida a 960 m.

# %%
import re
import sys
import warnings
import zipfile
from collections import Counter

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from comum import ESTUDO_CDL, paises_gdf

REC = ESTUDO_CDL / "recortes"
REGIOES = {
    "iowa_story": "Corn Belt: milho-soja",
    "kansas_ogallala": "Ogallala: milho irrigado, trigo, sorgo",
    "california_fresno": "Vale Central: perenes, algodão, tomate",
    "mississippi_delta": "Delta: soja, algodão, arroz",
    "north_dakota_cass": "Planícies do norte: trigo, soja, milho, girassol",
    "texas_lubbock": "Semiárido: algodão de sequeiro (análogo ao sertão)",
}
ANOS = [a for a in (2023, 2024, 2025) if (REC / f"iowa_story_{a}.tif").exists()]
print("anos recortados disponíveis:", ANOS)

# Legenda: culturas (do metadado oficial) + classes não agrícolas padrão do CDL
NAO_AGRI = {0: "Sem dado", 61: "Pousio/ocioso", 63: "Floresta", 64: "Arbustos", 65: "Barren", 81: "Nuvem", 82: "Urbano",
            83: "Água", 87: "Áreas úmidas", 88: "Não agrícola", 92: "Aquicultura", 111: "Água aberta", 112: "Gelo/neve",
            121: "Urbano aberto", 122: "Urbano baixa", 123: "Urbano média", 124: "Urbano alta", 131: "Solo exposto",
            141: "Floresta decídua", 142: "Floresta perene", 143: "Floresta mista", 152: "Arbustos", 176: "Pastagem/campo",
            190: "Áreas úmidas lenhosas", 195: "Áreas úmidas herbáceas"}

# %% [markdown]
# ### 14.1 Qualidade: acurácia por cultura (tabela oficial do NASS, CDL 2024)
# - **Acurácia do produtor:** fração dos pixels que realmente são da cultura e foram classificados como ela
#   (1 − omissão).
# - **Acurácia do usuário:** fração dos pixels classificados como a cultura que são mesmo dela (1 − comissão).
#
# Culturas grandes (milho, soja) passam de 90%; culturas pequenas ficam bem abaixo. **Rótulo do CDL não é verdade
# absoluta**, e isso importa se ele for usado para treinar modelos.

# %%
z = zipfile.ZipFile(ESTUDO_CDL / "2024_30m_cdls.zip")
txt = z.read([n for n in z.namelist() if n.endswith(".htm")][0]).decode("latin-1")
padrao = re.compile(r"^([A-Za-z][A-Za-z/&\.,' \-]+?)\s{2,}(\d{1,3})\s+([\d,]+)\s+([\d.]+)%\s+([\d.]+)%\s+([\d.]+)\s+([\d.]+)%\s+([\d.]+)%\s+([\d.]+)\s*$", re.M)
acc = pd.DataFrame(padrao.findall(txt), columns=["classe", "codigo", "pixels_ref", "prod_acc", "omissao", "kappa_p", "user_acc", "comissao", "kappa_u"])
for c in ["codigo"]:
    acc[c] = acc[c].astype(int)
acc["pixels_ref"] = acc.pixels_ref.str.replace(",", "").astype(int)
for c in ["prod_acc", "user_acc", "omissao", "comissao", "kappa_p", "kappa_u"]:
    acc[c] = acc[c].astype(float)
acc = acc.drop_duplicates("codigo").sort_values("pixels_ref", ascending=False)
NOMES = {**NAO_AGRI, **dict(zip(acc.codigo, acc.classe))}
print(f"{len(acc)} classes com acurácia publicada")
top = acc.head(25)
fig, ax = plt.subplots(figsize=(12, 5))
x = np.arange(len(top))
ax.bar(x - 0.2, top.prod_acc, 0.4, label="produtor")
ax.bar(x + 0.2, top.user_acc, 0.4, label="usuário")
ax.set_xticks(x)
ax.set_xticklabels(top.classe, rotation=75, fontsize=8)
ax.set_ylabel("%")
ax.set_title("CDL 2024 — acurácia por cultura (25 maiores amostras de referência)")
ax.legend()
plt.tight_layout()
plt.show()
print("Correlação de Spearman entre tamanho da amostra e acurácia do produtor:",
      round(acc[["pixels_ref", "prod_acc"]].corr("spearman").iloc[0, 1], 3))
acc.head(15)

# %% [markdown]
# ### 14.2 Validação de cobertura: é global?
# **Não.** A extensão do raster nacional cobre só os EUA contíguos.
#
# Para levar a mesma ideia ao mundo, os análogos são:
# - **ESA WorldCereal:** mapas globais de cereais/cultivos e irrigação, 10 m, 2021+.
# - **MapBiomas:** Brasil, uso do solo anual a 30 m desde 1985, com classes de soja, cana, café, algodão e outras.
# - **IBGE PAM:** proporções de cada cultura por município, que servem de rótulo fraco.

# %%
with rasterio.open(REC / f"nacional_{ANOS[0]}_960m.tif") as r:
    nac = r.read(1)
    from rasterio.warp import transform_bounds
    b = transform_bounds(r.crs, "EPSG:4326", *r.bounds)
print("Extensão em graus (lon_min, lat_min, lon_max, lat_max):", np.round(b, 2))
fig, ax = plt.subplots(figsize=(11, 4.5))
paises_gdf().boundary.plot(ax=ax, color="gray", lw=0.4)
ax.add_patch(plt.Rectangle((b[0], b[1]), b[2] - b[0], b[3] - b[1], fill=False, ec="red", lw=2, label="CDL"))
ax.set_xlim(-180, 180)
ax.set_ylim(-60, 85)
ax.legend()
ax.set_title("Cobertura do CDL — só EUA contíguos")
plt.show()
area_terra = (nac != 0).mean()
print(f"Fração da caixa com dado: {area_terra:.1%}")

# %% [markdown]
# ### 14.3 O que se planta nos EUA (visão nacional a 960 m)
# A amostragem pelo vizinho mais próximo preserva as proporções de área em média (é uma amostra sistemática de 1 a cada
# 32 × 32 pixels).

# %%
cont = Counter(nac[nac != 0].ravel().tolist())
tot = sum(cont.values())
shares = pd.DataFrame([(k, NOMES.get(k, f"classe {k}"), v / tot * 100) for k, v in cont.items()],
                      columns=["codigo", "classe", "pct_area"]).sort_values("pct_area", ascending=False)
agri = shares[~shares.codigo.isin(NAO_AGRI.keys())]
print(f"Área agrícola (classes de cultura) = {agri.pct_area.sum():.1f}% do território com dado")
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
shares.head(15).plot.barh(x="classe", y="pct_area", ax=ax[0], legend=False)
ax[0].invert_yaxis()
ax[0].set_title("15 maiores classes (todas)")
agri.head(15).plot.barh(x="classe", y="pct_area", ax=ax[1], legend=False, color="tab:green")
ax[1].invert_yaxis()
ax[1].set_title("15 maiores culturas")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 14.4 Janelas regionais: composição e rotação observada
# Para cada uma das 6 janelas de 40 × 40 km, olhamos a composição do último ano e, pixel a pixel, a **sequência de
# culturas nos anos disponíveis**. A pergunta é quanto da área repete a mesma cultura (monocultura) e quanto alterna.

# %%
def ler(reg, ano):
    with rasterio.open(REC / f"{reg}_{ano}.tif") as r:
        return r.read(1)


resumo, seqs_top = [], {}
for reg in REGIOES:
    pilha = np.stack([ler(reg, a) for a in ANOS])
    ultimo = pilha[-1]
    cult = ~np.isin(ultimo, list(NAO_AGRI.keys()))
    c = Counter(ultimo[cult].ravel().tolist())
    top3 = ", ".join(f"{NOMES.get(k, k)} {v / max(cult.sum(), 1):.0%}" for k, v in c.most_common(3))
    linha = {"regiao": reg, "descricao": REGIOES[reg], "% cultivado": round(cult.mean() * 100, 1), "top3 (último ano)": top3}
    if len(ANOS) >= 2:
        ag = np.all(~np.isin(pilha, list(NAO_AGRI.keys())), axis=0)  # cultivado em todos os anos
        mesma = np.all(pilha == pilha[0], axis=0) & ag
        linha["% repete a mesma cultura"] = round(mesma.sum() / max(ag.sum(), 1) * 100, 1)
        seq = Counter(map(tuple, pilha[:, ag].T.tolist()))
        seqs_top[reg] = [(" → ".join(NOMES.get(x, str(x)) for x in s), n / ag.sum()) for s, n in seq.most_common(5)]
    resumo.append(linha)
pd.DataFrame(resumo)

# %%
for reg, lst in seqs_top.items():
    print(f"\n{reg} — 5 sequências mais comuns ({ANOS[0]}–{ANOS[-1]}):")
    for s, f in lst:
        print(f"   {f:6.1%}  {s}")

# %% [markdown]
# ### 14.5 Matriz de transição (prior de rotação)
# Probabilidade de a cultura do ano seguinte ser *j*, dado que no ano anterior foi *i*, nas 6 janelas juntas, entre as
# culturas mais comuns. **É exatamente o modelo de partida (cadeia de Markov) da ideia 2 da seção 30.**

# %%
if len(ANOS) >= 2:
    pares = Counter()
    for reg in REGIOES:
        pilha = np.stack([ler(reg, a) for a in ANOS])
        for t in range(len(ANOS) - 1):
            a, b2 = pilha[t].ravel(), pilha[t + 1].ravel()
            ok = ~np.isin(a, list(NAO_AGRI.keys())) & ~np.isin(b2, list(NAO_AGRI.keys()))
            pares.update(zip(a[ok].tolist(), b2[ok].tolist()))
    origem = Counter()
    for (i, j), n in pares.items():
        origem[i] += n
    principais = [k for k, _ in origem.most_common(10)]
    M = pd.DataFrame(0.0, index=[NOMES.get(k, k) for k in principais], columns=[NOMES.get(k, k) for k in principais])
    for i in principais:
        for j in principais:
            M.loc[NOMES.get(i, i), NOMES.get(j, j)] = pares[(i, j)] / origem[i]
    fig, ax = plt.subplots(figsize=(8, 6.5))
    im = ax.imshow(M.values, cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(M)))
    ax.set_xticklabels(M.columns, rotation=70, fontsize=8)
    ax.set_yticks(range(len(M)))
    ax.set_yticklabels(M.index, fontsize=8)
    for i in range(len(M)):
        for j in range(len(M)):
            ax.text(j, i, f"{M.values[i, j]:.2f}", ha="center", va="center", fontsize=6.5, color="w" if M.values[i, j] < 0.6 else "k")
    plt.colorbar(im, ax=ax, label="P(próxima | atual)")
    ax.set_title(f"Transições ano a ano {ANOS[0]}–{ANOS[-1]} (6 janelas)")
    plt.tight_layout()
    plt.show()
    M.round(2)

# %% [markdown]
# ### 14.6 Frequência de culturas 2008–2025 (camada oficial do NASS)
# Em cada pixel, a camada de frequência conta em quantos dos 18 anos ele recebeu uma dada cultura.
# Isso mostra a **intensidade** de cada sistema: milho quase todo ano = monocultura; metade dos anos = rotação bienal.

# %%
freqs = sorted(REC.glob("*_freq*.tif")) + sorted(REC.glob("*Frequency*.tif"))
freqs = sorted(set(freqs))
if not freqs:
    print("Recortes da camada de frequência ainda não gerados.")
else:
    reg_freq = {}
    for f in freqs:
        reg = next((r for r in REGIOES if f.name.startswith(r)), None)
        if reg is None:
            continue
        with rasterio.open(f) as r:
            a = r.read(1)
        m = re.search(r"crop_frequency_([a-z]+)_", f.stem)
        reg_freq.setdefault(reg, {})[m.group(1) if m else f.stem.replace(reg + "_", "")] = a
    camadas = sorted({k for d in reg_freq.values() for k in d})
    fig, axs = plt.subplots(len(camadas), 1, figsize=(11, 2.6 * len(camadas)), squeeze=False)
    for ci, cam in enumerate(camadas):
        ax = axs[ci, 0]
        for reg, d in reg_freq.items():
            if cam in d:
                v = d[cam]
                v = v[(v > 0) & (v < 50)]
                if v.size:
                    h = np.bincount(v.astype(int), minlength=19)[1:19]
                    ax.plot(range(1, 19), h / h.sum(), marker="o", ms=3, label=reg)
        ax.set_title(f"{cam}: distribuição do nº de anos (2008–2025) com a cultura, entre pixels que a tiveram ao menos 1 vez")
        ax.set_xlabel("anos com a cultura")
        ax.legend(fontsize=7, ncol=3)
    plt.tight_layout()
    plt.show()

# %% [markdown]
# ### 14.7 Insights do CDL para o produto
# - **A rotação real é detectável por satélite e é muito estruturada.** No Corn Belt a alternância milho↔soja domina; em
#   regiões semiáridas aparecem **pousio** e culturas tolerantes à seca (algodão, sorgo, trigo). A matriz de transição é
#   um *prior* pronto para o motor: dada a cultura atual, quais sucessões são habituais e quais seriam novidade (e exigem
#   mais justificativa).
# - **Pousio e "ocioso" são parte da rotação no semiárido.** No Texas de sequeiro, o pousio é estratégia de guardar água.
#   É o mesmo dilema do sertão: o produto deve oferecer "pousio com cobertura" como estratégia comparável.
# - **Qualidade desigual dos rótulos.** Culturas pequenas têm acurácia bem menor. Se treinarmos modelos com o CDL, temos
#   de ponderar por acurácia ou focar nas classes confiáveis.
# - **Generalizar para o mundo:** a mesma análise roda com o WorldCereal (global), o MapBiomas (Brasil) ou com rótulos
#   gerados pelo nosso classificador de culturas (ideia 1 da seção 30), treinado onde o CDL existe e transferido para
#   outras regiões com cautela.
# - **Ligação com pragas (percolação):** a fração de área com a mesma cultura hospedeira em janelas de 40 km (ex.: milho
#   + soja > 80% no Iowa) indica paisagens acima do limiar de percolação, onde pragas especialistas se espalham com
#   facilidade. A rotação e a diversidade de culturas quebram essa conectividade.
