# %% [markdown]
# ## 4. SMAP, GLDAS, NLDAS, IMERG V07 recente e VIIRS NDVI — bases que exigem Earthdata Login
#
# Essas coleções **só são entregues com conta NASA Earthdata** (gratuita).
# Exceção já resolvida: o **IMERG V07 diário a 0,1° (1998 → set/2026)** veio aberto pela API do NASA POWER (seção 2).
# Só os últimos ~2 meses (Early/Late) dependem do Earthdata.
# - **Enquanto a credencial não existir:** a análise abaixo usa os **metadados abertos do catálogo CMR** da NASA
#   (extensão espacial, período e número de arquivos por ano) para validar a cobertura global e planejar os recortes.
# - **Quando o arquivo `_netrc` existir:** `scripts/baixar_earthdata.py --dados` baixa os recortes do Ceará.
#
# **Ficha técnica (resumo)**
#
# | Base | Variável-chave para o produto | Resolução | Período |
# |---|---|---|---|
# | SMAP L3 (SPL3SMP_E) | umidade do solo 0–5 cm | 9 km, ~2–3 dias | 2015– |
# | SMAP L4 (SPL4SMGP) | umidade da superfície e da **zona da raiz** (0–100 cm) | 9 km, 3 h | 2015– |
# | GLDAS-2.1 Noah | umidade por camada, ET, escoamento | 0,25°, mensal/3 h | 2000– |
# | GLDAS-2.2 CLSM | idem + **água subterrânea** (assimila GRACE) | 0,25°, diário | 2003– |
# | NLDAS-2 | idem, alta frequência | 0,125°, hora/mês | 1979– |
# | IMERG V07 Late/Final | chuva | 0,1°, 30 min/dia | 1998– |
# | VIIRS VNP13 | NDVI/EVI (continuidade do MODIS) | 500 m / 0,05° | 2012– |

# %%
import json
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import pandas as pd
from comum import DADOS, paises_gdf

meta = json.loads((DADOS / "earthdata_metadados" / "cmr_colecoes.json").read_text(encoding="utf-8"))
linhas = []
for rot, m in meta.items():
    s, w, n, e = map(float, m["caixa_espacial (S W N E)"][0].split())
    linhas.append({
        "coleção": rot, "short_name": m["short_name"], "versão": m["versao"],
        "lat_min": s, "lat_max": n, "lon_min": w, "lon_max": e,
        "início": m["primeiro_granulo"][:10] if m["primeiro_granulo"] else None,
        "último granulo": m["ultimo_granulo"][:10] if m["ultimo_granulo"] else None,
        "granulos que tocam o Ceará": m["granulos_ceara"], "na nuvem": m["nuvem"],
    })
tab = pd.DataFrame(linhas)
tab["global?"] = tab.apply(lambda r: "sim" if (r.lon_max - r.lon_min) >= 359 and r.lat_min <= -55 and r.lat_max >= 60 else
                           ("quase (sem Antártida)" if (r.lon_max - r.lon_min) >= 359 else "NÃO (regional)"), axis=1)
tab

# %% [markdown]
# ### 4.1 Validação de cobertura global (pelo catálogo)
# O mapa mostra a caixa espacial declarada de cada coleção. Note que **NLDAS cobre só os EUA contíguos**: para um produto
# mundial, o equivalente global é o **GLDAS**.

# %%
paises = paises_gdf()
fig, ax = plt.subplots(figsize=(12, 5.5))
paises.boundary.plot(ax=ax, color="gray", lw=0.4)
cores = plt.cm.tab10.colors
for i, r in tab.iterrows():
    ax.add_patch(plt.Rectangle((r.lon_min, r.lat_min), r.lon_max - r.lon_min, r.lat_max - r.lat_min,
                               fill=False, ec=cores[i % 10], lw=1.5 + 0.3 * i, label=r.short_name))
ax.set_xlim(-182, 182)
ax.set_ylim(-92, 92)
ax.legend(fontsize=7, loc="lower left", ncol=2)
ax.set_title("Caixa espacial declarada no CMR")
plt.show()

# %% [markdown]
# ### 4.2 Continuidade temporal — granulos por ano
# Ano com número de arquivos abaixo do esperado indica lacuna (ou ano corrente incompleto).
# O **IMERG Final** para em set/2025: para 2025–2026 só existem as versões Early/Late, que não têm correção por pluviômetros.

# %%
por_ano = pd.DataFrame({m["short_name"]: pd.Series(m["granulos_por_ano"]) for m in meta.values()}).fillna(0).astype(int)
por_ano.index = por_ano.index.astype(int)
fig, ax = plt.subplots(figsize=(12, 4.5))
(por_ano.div(por_ano.max()).T).pipe(lambda d: ax.imshow(d.values, aspect="auto", cmap="viridis"))
ax.set_yticks(range(len(por_ano.columns)))
ax.set_yticklabels(por_ano.columns)
ax.set_xticks(range(len(por_ano.index)))
ax.set_xticklabels(por_ano.index, rotation=90)
ax.set_title("Granulos por ano (normalizado pelo máximo da coleção) — escuro = lacuna/ausência")
plt.show()
por_ano.T

# %% [markdown]
# ### 4.3 Volume do recorte do Ceará (planejamento)
# O número de granulos que tocam o Ceará dá a escala do download quando houver login.
#
# **Estratégia de download**
# - **SMAP e VIIRS:** via **AppEEARS**, que recorta no servidor pelo polígono do Ceará e evita baixar arquivos globais.
# - **GLDAS e IMERG V07:** via **OPeNDAP**, fatiando lat/lon.
#
# **Insights para o produto**
# - **SMAP L4 (zona da raiz)** é a variável de umidade certa para lavoura. O L3 mede só os 5 cm de cima e, a 9 km,
#   descreve a região, não o talhão.
# - **GLDAS-2.2 CLSM** assimila o GRACE e entrega **água subterrânea a 0,25°**: é a ponte entre o GRACE (~300 km) e o talhão.
# - **NLDAS** fica fora do núcleo global; só serve para enriquecer quando o usuário estiver nos EUA.
# - **Alternativas abertas enquanto não há login** (seção 01): o POWER traz umidade do solo do MERRA-2
#   (`GWETTOP`, `GWETROOT`, `GWETPROF`), um substituto global grosseiro (~50 km) do SMAP/GLDAS.

# %%
pend = [p for p in ["smap", "gldas", "nldas", "imerg_v07", "viirs_vnp13"] if (DADOS / p).exists()]
print("Pastas de dados Earthdata já presentes:", pend or "nenhuma (aguardando credencial)")
