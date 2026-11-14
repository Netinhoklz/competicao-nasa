# %% [markdown]
# ## 17. O El Niño de 2026–27 e o Nordeste
#
# **O que está acontecendo agora (NOAA, dados baixados em 14/11/2026):**
# - O índice oficial do El Niño (**ONI**) de **ago–set–out/2026 está em +2,46 °C**. No Pacífico equatorial, a semana de
#   04/11/2026 marcou **Niño 3.4 em +3,3 °C** e **Niño 1+2 em +5,6 °C** (`wksst9120.for`).
# - Boletim do CPC de **12/11/2026: "El Niño Advisory"**:
#   - chance **maior que 79%** de El Niño forte a muito forte até **jan–mar/2027**;
#   - chance de **~60%** de ser um evento **histórico** (+2,5 °C ou mais desde 1950) em out–dez e nov–jan.
#
# **Por que importa para o Nordeste:** El Niño desloca a circulação e inibe a descida da Zona de Convergência
# Intertropical em fev–mai, a quadra chuvosa do norte do Nordeste. O Atlântico tropical modula esse efeito: Atlântico
# Norte mais quente que o Sul agrava a seca (Moura & Shukla 1981; Nobre & Shukla 1996; Kayano & Andreoli 2006).
# Alves et al. 2009 ligam esses índices à safra de milho e feijão do Ceará de 1952 a 2000.
#
# **Como lemos:**
# - **Análogos:** os El Niños fortes (ONI de out–dez/nov–jan ≥ 1,5) com dados NASA na quadra seguinte.
# - **Condição de entrada:** chuva (IMERG), umidade da raiz (SMAP), água armazenada (GRACE) e vegetação (VIIRS) agora,
#   comparadas com a mesma época de 2015 e de 2023 (as entradas dos dois últimos El Niños fortes).
# - **Perspectiva:** probabilidade por análogos, com n pequeno e a incerteza explícita.
#
# Script: `scripts/el_nino_2026.py`. Saídas em `E:/campeonato-nasa/dados/el_nino_2026/`.

# %%
import json
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from IPython.display import display
from comum import DADOS, DERIV, nordeste_gdf, ceara_gdf

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})
D = DADOS / "el_nino_2026"
idx = pd.read_csv(D / "indices.csv", index_col=0, parse_dates=True)
ev = pd.read_csv(D / "eventos.csv", index_col=0)
anal = pd.read_csv(D / "analogos_chuva_uf.csv")
rend = pd.read_csv(D / "analogos_rendimento_ce.csv", index_col=0)
atual = pd.read_csv(D / "estado_atual_uf.csv")
smc = pd.read_csv(D / "smap_pctl_comparado.csv")
persp = pd.read_csv(D / "perspectiva_uf.csv")
res = json.loads((D / "resumo.json").read_text(encoding="utf-8"))
print("ONI mais recente:", res["ONI_ultimo"], "| TNA:", res["TNA_ultimo"], "| TSA:", res["TSA_ultimo"])

# %% [markdown]
# ### 17.1 O tamanho deste El Niño na história

# %%
oni = idx.ONI.dropna()
fig, axs = plt.subplots(2, 1, figsize=(13, 6.5))
cores = np.where(oni >= 0.5, "tab:red", np.where(oni <= -0.5, "tab:blue", "lightgray"))
axs[0].bar(oni.index, oni.values, width=25, color=cores)
for y in (1.5, 2.0):
    axs[0].axhline(y, color="k", ls="--", lw=0.6)
fortes = ev[ev.ONI_OND_NDJ >= 1.5]
for ano, e in fortes.iterrows():
    axs[0].annotate(f"{ano}/{str(int(e.quadra_afetada))[2:]}", (pd.Timestamp(int(ano), 12, 1), e.ONI_OND_NDJ), fontsize=7, ha="center", va="bottom")
axs[0].annotate(f"ago–out/2026: +{oni.iloc[-1]:.2f}", (oni.index[-1], oni.iloc[-1]), xytext=(-90, 5), textcoords="offset points",
                fontsize=9, color="darkred", weight="bold")
axs[0].set_title("ONI (anomalia de TSM no Niño 3.4, média móvel de 3 meses) — NOAA CPC")
# Niño semanais 2025-2026
lin = [l for l in (DADOS / "indices_clima" / "atualizado_2026-11-14" / "wksst9120.for").read_text().splitlines() if l[:3].strip().isdigit()]
w = pd.DataFrame([(pd.to_datetime(l[:10].strip(), format="%d%b%Y"), float(l[19:23]), float(l[32:36]), float(l[45:49]), float(l[58:62])) for l in lin],
                 columns=["data", "Niño 1+2", "Niño 3", "Niño 3.4", "Niño 4"]).set_index("data")
w["2025-01-01":].plot(ax=axs[1])
axs[1].axhline(0, color="k", lw=0.6)
axs[1].set_title("Anomalias semanais de TSM (°C) — 2025 a 04/11/2026")
plt.tight_layout()
plt.show()
print("Última semana:", w.index[-1].date(), w.iloc[-1].to_dict())

# %% [markdown]
# ### 17.2 O que os El Niños fortes fizeram na quadra seguinte (chuva de fev–mai, % do normal)
# - **IMERG por estado:** 1998, 2010, 2016 e 2024.
# - **POWER no Ceará:** desde 1983.
# - "abaixo" = tercil inferior da climatologia 1998–2025.

# %%
cols_pct = [c for c in anal.columns if c.endswith("%normal") and not c.startswith("CE_POWER")]
tab = anal.set_index("evento")[["ONI_OND_NDJ", "dipolo_FMA", "CE_POWER_%normal"] + cols_pct].dropna(how="all", subset=cols_pct + ["CE_POWER_%normal"])
display(tab)
M = tab[cols_pct].dropna()
fig, ax = plt.subplots(figsize=(11, 2.8))
im = ax.imshow(M.values, cmap="RdBu", vmin=20, vmax=180, aspect="auto")
ax.set_xticks(range(len(cols_pct)))
ax.set_xticklabels([c.split("_")[0] for c in cols_pct])
ax.set_yticks(range(len(M)))
ax.set_yticklabels(M.index)
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        ax.text(j, i, f"{M.values[i, j]:.0f}", ha="center", va="center", fontsize=8)
plt.colorbar(im, label="% do normal")
ax.set_title("Chuva de fev–mai após El Niño forte, por estado (IMERG)")
plt.show()

# %% [markdown]
# ### 17.3 E a safra do Ceará? (desvio do rendimento em relação à mediana móvel de 7 anos, IBGE PAM)

# %%
r = rend.drop(columns=[c for c in rend.columns if "verde" in c]).dropna(subset=["Milho (em grão)"])
display(r)
fig, ax = plt.subplots(figsize=(9, 3.6))
r.drop(columns="ONI").plot.bar(ax=ax)
ax.axhline(0, color="k", lw=0.6)
ax.set_ylabel("% em relação à tendência")
ax.set_title("Rendimento no Ceará na quadra após El Niño forte")
plt.show()

# %% [markdown]
# ### 17.4 Como o Nordeste está entrando em 2027 (dados NASA)

# %%
display(atual)
display(smc)
fig, axs = plt.subplots(1, 2, figsize=(14, 4))
atual.set_index("UF")["%normal"].plot.bar(ax=axs[0], color=np.where(atual["%normal"] < 80, "tab:red", "tab:blue"))
axs[0].axhline(100, color="k", lw=0.6)
axs[0].set_title(f"Chuva de 01/08 a {res['imerg_data_final'][8:10]}/11/2026 (IMERG), % do normal")
smc.set_index("UF").plot.bar(ax=axs[1])
axs[1].axhline(50, color="k", lw=0.6, ls="--")
axs[1].set_title(f"SMAP L4: percentil da zona da raiz (30 dias até {res['smap_data_final'][8:10]}/11)")
axs[1].set_ylabel("percentil (50 = normal)")
plt.tight_layout()
plt.show()

sm = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
fim = pd.Timestamp(sm.time.values.max())
mapa = sm.sm_rootzone_pctl.sel(time=slice(fim - pd.Timedelta(days=29), fim)).mean("time")
fig, ax = plt.subplots(figsize=(7, 7))
mapa.plot(ax=ax, cmap="RdYlBu", vmin=0, vmax=100, cbar_kwargs={"label": "percentil da umidade da zona da raiz"})
nordeste_gdf().boundary.plot(ax=ax, color="k", lw=0.5)
ceara_gdf().boundary.plot(ax=ax, color="k", lw=1.5)
ax.set_title(f"SMAP L4 — umidade da zona da raiz, 30 dias até {fim:%d/%m/%Y}")
plt.show()
print("GRACE (set/AAAA, cm):", res["grace"])
print("NDVI VIIRS (nov/AAAA):", res["ndvi"])

# %% [markdown]
# ### 17.5 Perspectiva para a quadra de 2027 (por análogos)

# %%
display(persp)

# %% [markdown]
# ### 17.6 Leitura e impacto no produto
# **O que os dados dizem:**
# - **Nos 5 El Niños fortes com dado desde 1982** (1982/83, 1997/98, 2009/10, 2015/16, 2023/24), a quadra do Ceará
#   teve 53%, 44%, 64%, 58% e 93% do normal (POWER). Ficou no tercil inferior em **4 de 5**.
# - **Pelo IMERG,** o norte do Nordeste (MA, PI, CE, RN, PB) ficou abaixo do normal em **3 de 4** eventos. O leste e o
#   sul (PE, AL, SE, BA) dividem-se em 2 de 4, como esperado pela geografia da quadra.
# - **Safra do Ceará:** o **milho caiu 40% a 64% abaixo da tendência em 4 de 5 eventos** (nos outros anos, +7,5% em média)
#   e o feijão caiu de 19% a 51%. A **mandioca perdeu só de 14% a 33%**: é o amortecedor, como já vimos na seção 20.
# - **A exceção é 2023/24:** quadra normal e safra normal, mesmo com ONI de +2,0. O índice do Atlântico em fev–abr foi
#   parecido com o de 2016, então o dipolo sozinho não explica a diferença. **El Niño forte aumenta muito a chance de
#   seca, mas não a garante.**
# - **A condição de entrada é pior que nas últimas vezes.** Em novembro de 2026, o percentil da umidade da zona da raiz
#   do SMAP está em **18 no Ceará** (25 em 2015 e 28 em 2023), e entre 12 e 19 em MA, PE, AL, SE e PB. A chuva de
#   ago–nov ficou entre 57% e 68% do normal no MA, PI, RN e PB. O GRACE do Ceará está em −9,7 cm, entre 2023 (−3,5) e
#   2015 (−16,7).
#
# **O que a QUADRA faz com isso no portão de novembro (alerta, não sentença):**
# 1. Mostra a **probabilidade**: nos análogos, de 3 a 4 em cada 5 quadras abaixo do normal no norte do Nordeste. Diz que
#    a amostra é pequena e que 2024 foi a exceção.
# 2. Reordena as estratégias pela **pior quadra**: mais mandioca e palma (amortecedores e forragem), caupi de ciclo curto,
#    sorgo no lugar de parte do milho. O plantio do milho fica condicionado ao portão de 19/mar (chuva acumulada e SMAP).
# 3. Recomenda **guardar forragem e água** (relógio lento: GRACE e água subterrânea do GLDAS).
# 4. **Reavalia a cada portão** com o IMERG e o SMAP: se a quadra começar bem (como em 2024), o plano volta para o padrão.
#
# **Ressalvas:**
# - n = 5 eventos e uma quadra por evento.
# - O ONI de out–jan de 2026/27 ainda não foi observado (o CPC prevê forte a muito forte).
# - O Atlântico de fev–abr/2027 ainda é desconhecido.
# - Com ONI perto de +2,5, 2027 pode ficar **fora da faixa histórica** (o maior análogo é 2015/16, +2,59).
