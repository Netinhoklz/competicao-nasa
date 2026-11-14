# %% [markdown]
# # Field Shift — Estudo estatístico das bases de dados (NASA Space Apps 2026)
#
# **Objetivo do produto:** uma ferramenta de apoio à decisão de **rotação de culturas** que funcione em
# **qualquer lugar do mundo**, demonstrada no **Ceará / Nordeste do Brasil**.
#
# **Este notebook:** para cada base de dados baixada, mostra:
# 1. ficha técnica;
# 2. **validação de cobertura global** (é global de verdade?);
# 3. qualidade dos dados;
# 4. estatística descritiva no Ceará e no Nordeste;
# 5. sazonalidade;
# 6. tendências (Mann-Kendall + Sen);
# 7. variabilidade e extremos;
# 8. insights para o produto.
#
# Depois vêm as **relações entre bases** (seção 20), as **ideias de ML/DL** (seção 30) e a **síntese** (seção 90).
#
# **Regiões usadas em todo o estudo**
# - Ceará: caixa −41,5 a −37,0 de longitude, −8,0 a −2,5 de latitude (limite do IBGE recortado por dentro).
# - Nordeste: −48,8 a −34,7 de longitude, −18,4 a −1,0 de latitude (sem Fernando de Noronha).
# - 4 áreas agrícolas de interesse (AOIs, ~11 km de lado) para dados de alta resolução: Chapada do Apodi/Jaguaribe
#   (irrigada), Cariri, Sertão Central e Serra da Ibiapaba.
#
# Todos os dados estão em `E:/campeonato-nasa/dados/<base>/`, cada um com seu `MANIFESTO.json`.

# %%
import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import pandas as pd
from comum import AOIS, BBOX_CE, BBOX_NE, DADOS, ESTUDO_CDL, ceara_gdf, municipios_ce_gdf, nordeste_gdf, tamanho_pasta

pd.set_option("display.max_colwidth", 120)
plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})

# %% [markdown]
# ## 0.1 Inventário do que foi baixado
# A tabela é calculada na hora a partir do disco: pasta, tamanho, número de arquivos e o resumo do `MANIFESTO.json`.

# %%
linhas = []
for p in sorted([d for d in DADOS.iterdir() if d.is_dir()] + [ESTUDO_CDL]):
    arqs = [f for f in p.rglob("*") if f.is_file()]
    man = p / "MANIFESTO.json"
    info = json.loads(man.read_text(encoding="utf-8")) if man.exists() else {}
    linhas.append({
        "pasta": p.name,
        "tamanho_GB": round(sum(f.stat().st_size for f in arqs) / 1e9, 3),
        "arquivos": len(arqs),
        "fonte": str(info.get("fonte", ""))[:90],
        "cobertura/recorte": str(info.get("cobertura", info.get("recorte", "")))[:90],
    })
inventario = pd.DataFrame(linhas).sort_values("tamanho_GB", ascending=False)
print(f"Total em disco: {inventario.tamanho_GB.sum():.2f} GB")
inventario

# %% [markdown]
# ## 0.2 Área de estudo

# %%
ce, ne, mun = ceara_gdf(), nordeste_gdf(), municipios_ce_gdf()
fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
ne.boundary.plot(ax=ax[0], color="gray", lw=0.7)
ce.plot(ax=ax[0], color="#f4a261", alpha=0.6)
ax[0].set_title("Nordeste (9 UFs) e Ceará")
mun.boundary.plot(ax=ax[1], color="lightgray", lw=0.4)
ce.boundary.plot(ax=ax[1], color="k", lw=1)
for nome, (lon, lat, desc) in AOIS.items():
    ax[1].add_patch(plt.Rectangle((lon - 0.05, lat - 0.05), 0.1, 0.1, fill=False, ec="red", lw=2))
    ax[1].annotate(nome, (lon, lat), xytext=(5, 5), textcoords="offset points", color="darkred", fontsize=9)
ax[1].set_title("Ceará: 184 municípios e as 4 AOIs")
for a in ax:
    a.set_xlabel("lon")
    a.set_ylabel("lat")
plt.tight_layout()
plt.show()
pd.DataFrame([(k, v[0], v[1], v[2]) for k, v in AOIS.items()], columns=["aoi", "lon", "lat", "descrição"])
