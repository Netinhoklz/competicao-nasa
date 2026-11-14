# %% [markdown]
# # Dados do protótipo QUADRA no Nordeste: estudo descritivo e estatístico de cada base
#
# O protótipo (`protótipo/`) recebe um lugar e responde quatro perguntas: o que cabe, quando plantar e com que risco,
# como está este ano e em que ordem plantar. Desde 14/11/2026 ele cobre os **1.794 municípios dos 9 estados do Nordeste**
# e já traz as correções da revisão de 10 agentes (`protótipo/REVISAO_10_AGENTES.md`). Este notebook descreve, base por
# base, **exatamente os dados e as regras que o motor (`protótipo/motor.py`) usa hoje**: o que é cada base, a cobertura, a
# qualidade, a estatística descritiva, os mapas e o que isso muda no produto.
#
# | Seção | Base | Onde entra no protótipo | Cobertura no protótipo |
# |---|---|---|---|
# | 1 | **FAO GAEZ v4**: aptidão por cultura | cardápio: rótulo de aptidão; decide as culturas sem ZARC no município | mundo |
# | 2 | **ZARC 2026/27 (MAPA)**: risco por decêndio | cardápio: janela e risco; 1º decêndio zoneado e 1º com risco de 20% | 1.794 municípios do NE |
# | 3 | **Cruzamento GAEZ × ZARC** | situação de cada cultura em cada município | NE |
# | 4 | **NASA POWER**: climatologia + Tmax/Tmin médias | assinatura climática do lugar | mundo |
# | 5 | **Análogos climáticos** (POWER × lugares dos artigos) | peso w de cada estudo; confiança do recibo | mundo |
# | 6 | **Catálogo de rotações** (147 cartões) | regras do motor e evidência | — |
# | 7 | **NASA GPM IMERG**: regime de chuva | estação típica do município; avisos fora da quadra e no litoral leste | NE |
# | 8 | **NASA GPM IMERG**: início da estação e El Niño | quando a chuva começa; El Niño no próprio município | NE |
# | 9 | **NOAA ONI** e chuva recente | "este ano" | mundo (perspectiva só no NE) |
# | 10 | **NASA SMAP L4**: solo agora | posição do solo nos últimos 30 dias entre 12 anos | NE |
# | 11 | **Síntese** | o que cada base sustenta e o limite de cada uma | — |
#
# O notebook importa o próprio motor (`motor.py`) para usar as mesmas tabelas e funções que a página usa: a malha, o
# regime, o início da estação, as primeiras datas do ZARC e a perspectiva do El Niño.
#
# Paleta: categorias em ordem fixa; magnitude em uma só cor (azul, do claro ao escuro); sinal (antes/depois, acima/abaixo)
# em azul ↔ vermelho com o meio cinza.

# %%
import json
import math
import re
import sys
import warnings

sys.dont_write_bytecode = True  # importar o motor não grava nada em protótipo/__pycache__
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\protótipo")
warnings.filterwarnings("ignore")
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from scipy import stats

import gaez_zarc_municipio as GZ
import motor as M
from comum import DADOS, nordeste_gdf

PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
D_APR = DADOS / "analogos_aprofundado"
# paleta (referência das orientações de visualização)
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEQ = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])
DIV = LinearSegmentedColormap.from_list("div", ["#184f95", "#6da7ec", "#f0efec", "#ec8a7d", "#d03b3b"])
CINZA = "#c3c2b7"
plt.rcParams.update({"figure.dpi": 100, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.edgecolor": "#c3c2b7", "axes.spines.top": False,
                     "axes.spines.right": False, "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "text.color": "#0b0b0b", "axes.prop_cycle": plt.cycler(color=CAT), "lines.linewidth": 2})
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)

UF_ORDEM = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]  # pela ordem do código IBGE (21 a 29)
MUN = M.MUN[["cod", "municipio", "uf", "mesorregiao", "geometry"]].copy()  # a mesma malha e os mesmos nomes do motor
RP = MUN.geometry.representative_point()  # ponto interno: onde o GAEZ e o POWER são lidos
MUN["lat"], MUN["lon"] = RP.y.values, RP.x.values
UFMUN = MUN.set_index("cod").uf
MUN_PLOT = MUN[["cod", "geometry"]].copy()
MUN_PLOT["geometry"] = MUN_PLOT.geometry.simplify(0.01)  # só para desenhar mais rápido
NE = nordeste_gdf()
XLIM, YLIM = (-48.9, -34.6), (-18.5, -0.9)  # Fernando de Noronha (−32,4°) fica fora do quadro dos mapas


def descreve(df):
    """Estatística descritiva com ausentes, percentis e assimetria."""
    df = df.to_frame() if isinstance(df, pd.Series) else df
    d = df.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
    d.insert(1, "ausentes_%", (df.isna().mean() * 100).round(1))
    d["assimetria"] = df.skew(numeric_only=True)
    return d.rename(columns={"count": "n", "mean": "média", "std": "dp", "50%": "mediana"}).round(2)


def mapa_ne(ax, valores, titulo, cmap=SEQ, vmin=None, vmax=None, rotulo="", categorias=None, ticks=None, rotulos_ticks=None):
    """Mapa dos 1.794 municípios do NE; valores = Series indexada pelo código IBGE (texto).
    categorias = {rótulo: cor}, em ordem fixa, para mapas categóricos."""
    g = MUN_PLOT.assign(v=MUN_PLOT.cod.map(valores))
    if categorias:
        cor = g.v.map(categorias).fillna("#eeebe3")
        g.plot(ax=ax, color=cor, edgecolor="none", linewidth=0)
        presentes = [k for k in categorias if (g.v == k).any()]
        ax.legend(handles=[Patch(color=categorias[k], label=f"{k} ({int((g.v == k).sum())})") for k in presentes],
                  fontsize=7, loc="lower left", frameon=False)
    else:
        g.plot(column="v", ax=ax, cmap=cmap, vmin=vmin, vmax=vmax, edgecolor="none", linewidth=0,
               missing_kwds={"color": "#eeebe3"}, legend=True, legend_kwds={"label": rotulo, "shrink": 0.6})
        if ticks is not None:
            cb = ax.get_figure().axes[-1]
            cb.set_yticks(ticks)
            cb.set_yticklabels(rotulos_ticks or ticks, fontsize=7)
    NE.boundary.plot(ax=ax, color="#52514e", lw=0.6)
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_aspect("equal")
    ax.set_title(titulo, fontsize=10)
    ax.set_axis_off()


def por_uf(s, func="median"):
    """Agrega uma Series indexada pelo código IBGE por UF, na ordem do IBGE."""
    return s.groupby(UFMUN.reindex(s.index).values).agg(func).reindex(UF_ORDEM)


print(f"{len(MUN)} municípios do NE (malha do IBGE, a mesma do motor); por UF:")
display(MUN.uf.value_counts().reindex(UF_ORDEM).rename("municípios").to_frame().T)
print("Datas e períodos de cada base, como o motor mostra (revisão M29):")
display(pd.Series(M.FONTES).rename("fonte").to_frame())
