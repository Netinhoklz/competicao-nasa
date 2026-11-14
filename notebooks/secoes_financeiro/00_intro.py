# %% [markdown]
# # QUADRA em reais: rentabilidade, risco e retorno das culturas do protótipo no Nordeste
#
# **A pergunta.** O protótipo QUADRA monta, para cada lugar, um cardápio de 15 culturas e um plano de faixas para
# 2027–2029. Este notebook pergunta **quanto isso vale em dinheiro**: quanto cada cultura rende por hectare, quanto
# custa, com que chance não paga o custo, como se comporta num El Niño forte, quanto a carteira e a rotação protegem
# a renda e o que sobra para uma família de 3 ha em Quixadá-CE.
#
# **Unidades.** Tudo em **R$ de 2025** (IPCA do Banco Central, média anual). A receita aparece **por hectare plantado**
# (inclui a área perdida: é o que a família arrisca) e **por hectare colhido** (é o que o PAM costuma mostrar). Quando
# as culturas têm ciclos diferentes, a receita aparece também **por hectare-mês** de ocupação da terra.
#
# | Seção | Pergunta | Base principal |
# |---|---|---|
# | 1 | O painel: o que entra e como foi limpo | IBGE PAM (SIDRA 1612), IPCA (BCB SGS 433) |
# | 2 | Quanto cada cultura produz por hectare, e com que chance de perda | PAM municipal, 1998–2025 |
# | 3 | Que preço a família recebe, e quanto ele varia | preço implícito do PAM; FAOSTAT; Pink Sheet |
# | 4 | Quanto entra por hectare (plantado, colhido e por mês de terra) | PAM, 2010–2025 |
# | 5 | Quanto custa, quanto sobra e onde fica o ponto de equilíbrio | CONAB, custos de produção (NE) |
# | 6 | Risco e retorno: pior ano em 10, El Niño forte, seca de 2012–2016 | PAM a preço de referência |
# | 7 | Diversificação: correlação e carteiras em R$/ha | PAM; a carteira da proposta, refeita em reais |
# | 8 | Rotação em reais: o bônus da leguminosa e o cenário honesto | catálogo de rotações |
# | 9 | Cardápio do protótipo × dinheiro, município a município | ZARC + GAEZ do NE (motor) |
# | 10 | A família de Quixadá: fluxo de caixa 2027–2029 | tudo acima |
# | 11 | Síntese: o que paga, o que protege, o que falta medir | — |
#
# **O que é medido e o que é suposição.**
# - **Medido:** área, produção e valor da produção por município e ano (IBGE PAM); inflação (IPCA); custo de produção
#   estimado pela CONAB em municípios do Nordeste (planilhas oficiais); preços ao produtor do Brasil (FAOSTAT) e
#   preços mundiais (Banco Mundial).
# - **Do motor do protótipo:** a situação de cada cultura em cada município (ZARC 2026/27 e GAEZ v4; onde a cultura
#   tem ZARC no município, o ZARC decide; senão, aptidão GAEZ > 40 com insumo baixo, classe "média" ou melhor).
# - **Da literatura, com grau:** o bônus da leguminosa antes do cereal (+24%, faixa +2% a +49%, B·T1) e o ganho contra
#   o consórcio de hoje (0 a +9%, D·T3), do catálogo de rotações.
# - **Suposição (sempre marcada e com faixa):** os ciclos das culturas sem fonte, o custo das culturas sem planilha da
#   CONAB no Nordeste, o tamanho das faixas da família e o valor de uso da forragem. Onde o custo é suposição, o
#   notebook mostra o **ponto de equilíbrio**, que não depende de saber o custo.
#
# **Três avisos que valem para tudo.**
# 1. O PAM é **municipal**: mistura sequeiro e irrigado, roça e empresa, consórcio e solteiro.
# 2. O PAM **não separa feijão-caupi de feijão comum**: "Feijão" aqui é "Feijão (em grão)".
# 3. O preço é **implícito** (valor ÷ quantidade). É o preço médio que o IBGE atribui à produção do município, não o
#    preço de uma venda.
#
# Paleta: culturas em ordem e cor fixas; magnitude em um só tom (azul, do claro ao escuro); sinal (lucro ou prejuízo,
# acima ou abaixo) em azul ↔ vermelho com o meio cinza. Nenhum gráfico tem dois eixos y.

# %%
import json
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.patches import Patch

from comum import DADOS, DERIV

PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
F = DADOS / "financeiro"
# paleta (referência das orientações de visualização; validada: 8 cores passam CVD e visão normal)
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEQ = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])
DIV = LinearSegmentedColormap.from_list("div", ["#d03b3b", "#ec8a7d", "#f0efec", "#6da7ec", "#184f95"])  # vermelho = prejuízo
CINZA = "#8a8984"
plt.rcParams.update({"figure.dpi": 110, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.edgecolor": "#c3c2b7", "axes.spines.top": False,
                     "axes.spines.right": False, "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
                     "text.color": "#0b0b0b", "axes.prop_cycle": plt.cycler(color=CAT), "lines.linewidth": 2})
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# culturas do PAM em ordem fixa (a cor segue a cultura em todo o notebook)
CULT = ["Milho", "Feijão", "Mandioca", "Sorgo", "Amendoim", "Algodão herbáceo", "Mamona", "Girassol"]
COR = dict(zip(CULT, CAT))
NO_CARDAPIO = {"Milho": "Milho", "Feijão": "Feijão-caupi e feijão comum (juntos no PAM)", "Mandioca": "Mandioca",
               "Sorgo": "Sorgo granífero (o PAM é só sorgo em grão)", "Amendoim": "Amendoim", "Algodão herbáceo": "Algodão herbáceo",
               "Mamona": "Mamona", "Girassol": "Girassol"}
SEM_PAM = ["Guandu", "Sorgo forrageiro", "Milheto", "Palma forrageira", "Gliricídia", "Mucuna-preta"]
UFS = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
AREA_MIN = 10          # ha plantados: abaixo disso, o município-ano não entra (ruído de arredondamento)
ANOS_MIN = 10          # anos válidos para um município ter "série" de uma cultura
PRECO_REF = range(2016, 2026)  # janela do preço de referência
QUIXADA = "2311306"

EVT = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
EN_FORTE = sorted(int(a) for a in EVT[(EVT.ONI_OND_NDJ >= 1.5) & EVT.quadra_afetada.between(1998, 2025)].quadra_afetada)
SECA = list(range(2012, 2017))

# ciclo de cada cultura em dias (central, mínimo, máximo) para a receita por hectare-mês
CICLO = pd.DataFrame([
    ("Feijão", 70, 60, 75, "parâmetro: caupi precoce 60–70 d (proposta v3, S2) e ~70–75 d (pedido); feijão comum é mais longo"),
    ("Milho", 110, 100, 120, "parâmetro: ~110 d (pedido); faixa suposta"),
    ("Sorgo", 110, 100, 120, "suposição (parâmetro), sem fonte lida"),
    ("Amendoim", 100, 90, 120, "suposição (parâmetro), sem fonte lida"),
    ("Algodão herbáceo", 140, 120, 160, "suposição (parâmetro), sem fonte lida"),
    ("Mamona", 180, 150, 240, "suposição (parâmetro), sem fonte lida"),
    ("Girassol", 100, 90, 120, "suposição (parâmetro), sem fonte lida"),
    ("Mandioca", 456, 365, 548, "12–18 meses (pedido); a CONAB usa '2º ciclo (18 meses)' na planilha da mandioca"),
], columns=["cultura", "dias", "dias_min", "dias_max", "fonte"]).set_index("cultura")


def descreve(df):
    """Estatística descritiva com ausentes, percentis e assimetria."""
    df = df.to_frame() if isinstance(df, pd.Series) else df
    d = df.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
    d.insert(1, "ausentes_%", (df.isna().mean() * 100).round(1))
    d["assimetria"] = df.skew(numeric_only=True)
    return d.rename(columns={"count": "n", "mean": "média", "std": "dp", "50%": "mediana"}).round(2)


def brl(v, casas=0):
    """1234.5 -> 'R$ 1.234'."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return "R$ " + f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def num(v, casas=2):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


# malhas do NE (IBGE), simplificadas para desenhar rápido
MUN_NE = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
MUN_NE["cod"] = MUN_NE.codarea.astype(str)
MUN_NE["geometry"] = MUN_NE.geometry.simplify(0.01)
UF_NE = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_UF.geojson")
REFM = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
NOME = REFM.municipio.to_dict()


def mapa_ne(ax, valores, titulo, cmap=SEQ, vmin=None, vmax=None, rotulo="", cores=None, ordem=None):
    """Mapa dos 1.794 municípios do NE. valores = Series indexada pelo código IBGE (texto).
    Com `cores` (dict categoria -> cor), desenha categorias em cor fixa e legenda na ordem `ordem`."""
    g = MUN_NE.assign(v=MUN_NE.cod.map(valores))
    base = g[g.v.isna()]
    base.plot(ax=ax, color="#eeebe3", edgecolor="#fcfcfb", linewidth=0.1)
    if cores:
        alca = []
        for k in (ordem or list(cores)):
            s = g[g.v == k]
            if len(s):
                s.plot(ax=ax, color=cores[k], edgecolor="#fcfcfb", linewidth=0.1)
                alca.append(Patch(color=cores[k], label=f"{k} ({len(s)})"))
        alca.append(Patch(color="#eeebe3", label=f"sem dado ({len(base)})"))
        ax.legend(handles=alca, fontsize=7, loc="lower right", bbox_to_anchor=(1.02, 0.0), ncol=1, frameon=False)
    else:
        g[g.v.notna()].plot(column="v", ax=ax, cmap=cmap, vmin=vmin, vmax=vmax, edgecolor="#fcfcfb", linewidth=0.1,
                            legend=True, legend_kwds={"label": rotulo, "shrink": 0.6})
    UF_NE.boundary.plot(ax=ax, color="#52514e", lw=0.5)
    ax.set_title(titulo, fontsize=10)
    ax.set_axis_off()


print(f"{len(MUN_NE)} municípios do NE; El Niño forte (ONI OND–NDJ ≥ 1,5) nas quadras {EN_FORTE}; seca longa {SECA[0]}–{SECA[-1]}")
display(CICLO)

# %% [markdown]
# ## 1. O painel: o que entra e como foi limpo
#
# O script `scripts/preparar_financeiro.py` junta e deflaciona as bases (saídas em `E:/campeonato-nasa/dados/financeiro/`,
# com `MANIFESTO.json`):
# - **PAM municipal do NE**, 1998–2025: milho, feijão, mandioca, sorgo e algodão herbáceo já estavam em disco; amendoim,
#   mamona e girassol vieram agora do SIDRA (tabela 1612, 135 consultas por cultura × variável × UF);
# - **IPCA** (SGS 433), do Plano Real até o último mês publicado; o fator leva cada ano à média de 2025;
# - **CONAB**: séries de custo de produção (seção 5).
#
# **Regras de limpeza (fixadas antes de olhar os resultados):**
# - um município-ano entra se tem **≥ 10 ha plantados** da cultura;
# - **rendimento por ha plantado** = produção ÷ área plantada (o ano de perda total fica com rendimento 0);
# - **razão ao normal** = rendimento do ano ÷ mediana dos **outros** anos do mesmo município (definição canônica da
#   proposta); **quebra** = razão < 0,5;
# - **preço implícito** = valor ÷ produção, só com produção ≥ 1 t e dentro de 0,25× a 4× da mediana da UF no ano;
# - **preço de referência** de cada município e cultura = mediana do preço real de 2016–2025 (≥ 3 anos); sem isso, a
#   mediana da UF; sem isso, a do NE;
# - **receita a preço de referência** = rendimento do ano × preço de referência. Ela isola o risco de clima e deixa usar
#   1998, o El Niño mais forte da série com dado. A **receita observada** (valor ÷ área, 2010–2025) traz junto o
#   choque de preço e serve de conferência.

# %%
P = pd.read_parquet(F / "painel_mun_cultura_ano.parquet")
P = P[P.produto.isin(CULT)].copy()
P["uf"] = P.cod_mun.str[:2].map({"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"})
P["semiarido"] = P.cod_mun.map(REFM.semiarido_2022).fillna(False)
B = P[P.area_plantada_ha >= AREA_MIN].copy()


def mediana_outros(s):
    v = s.to_numpy()
    if len(v) < 2:
        return pd.Series(np.nan, index=s.index)
    return pd.Series([np.median(np.delete(v, i)) for i in range(len(v))], index=s.index)


B["normal_kg_ha"] = B.groupby(["cod_mun", "produto"]).rend_plantado_kg_ha.transform(mediana_outros)
B["razao"] = B.rend_plantado_kg_ha / B.normal_kg_ha
B["quebra"] = B.razao < 0.5
B["n_anos"] = B.groupby(["cod_mun", "produto"]).ano.transform("size")

# preço implícito limpo
pr = B.preco_r2025_kg.where(B.producao_t >= 1)
med_uf_ano = pr.groupby([B.uf, B.produto, B.ano]).transform("median")
B["preco"] = pr.where((pr / med_uf_ano).between(0.25, 4))
jan = B[B.ano.isin(PRECO_REF)]
p_mun = jan.groupby(["cod_mun", "produto"]).preco.agg(["median", "count"])
p_mun = p_mun[p_mun["count"] >= 3]["median"]
p_uf = jan.groupby(["uf", "produto"]).preco.median()
p_ne = jan.groupby("produto").preco.median()
idx = pd.MultiIndex.from_frame(B[["cod_mun", "produto"]])
B["preco_ref"] = p_mun.reindex(idx).to_numpy()
B["origem_preco"] = np.where(B.preco_ref.notna(), "município", None)
f_uf = p_uf.reindex(pd.MultiIndex.from_frame(B[["uf", "produto"]])).to_numpy()
B["origem_preco"] = np.where(B.preco_ref.isna() & ~np.isnan(f_uf), "UF", B.origem_preco)
B["preco_ref"] = B.preco_ref.fillna(pd.Series(f_uf, index=B.index))
B["origem_preco"] = np.where(B.preco_ref.isna(), "NE", B.origem_preco)
B["preco_ref"] = B.preco_ref.fillna(B.produto.map(p_ne))
B["R"] = B.rend_plantado_kg_ha * B.preco_ref          # R$ de 2025 por ha plantado, a preço de referência
B["R_col"] = B.rend_colhido_kg_ha * B.preco_ref       # por ha colhido
B["R_obs"] = B.receita_plantado_r2025_ha              # observada (valor ÷ área plantada)
B["R_obs_col"] = B.receita_colhido_r2025_ha

cob = pd.DataFrame({
    "municípios com algum ano": B.groupby("produto").cod_mun.nunique(),
    f"municípios com série (≥ {ANOS_MIN} anos)": B[B.n_anos >= ANOS_MIN].groupby("produto").cod_mun.nunique(),
    "município-anos válidos": B.groupby("produto").size(),
    "área plantada/ano 2016–25 (mil ha)": P[P.ano.isin(PRECO_REF)].groupby("produto").area_plantada_ha.sum() / 10 / 1000,
    "valor/ano 2016–25 (R$ mi de 2025)": P[P.ano.isin(PRECO_REF)].groupby("produto").valor_r2025.sum() / 10 / 1e6,
    "preço de ref. do município (%)": B.groupby("produto").origem_preco.apply(lambda s: (s == "município").mean() * 100),
    "área no semiárido 2016–25 (%)": P[P.ano.isin(PRECO_REF) & P.semiarido].groupby("produto").area_plantada_ha.sum()
    / P[P.ano.isin(PRECO_REF)].groupby("produto").area_plantada_ha.sum() * 100,
}).reindex(CULT)
for c in cob.columns[:3]:
    cob[c] = cob[c].astype("Int64")
display(cob.round(1))
print("Município-anos válidos no total:", len(B), "| anos", B.ano.min(), "a", B.ano.max())
print("Quixadá tem série de:", sorted(B[(B.cod_mun == QUIXADA) & (B.n_anos >= ANOS_MIN)].produto.unique()))

# %% [markdown]
# **Leitura.**
# - O painel tem **150.318 município-anos válidos** (≥ 10 ha plantados), de 1998 a 2025, em 8 culturas.
# - Milho e feijão têm série (≥ 10 anos) em ~1.690 municípios; mandioca em 1.528; algodão herbáceo em 324; mamona em
#   207; amendoim em 165; sorgo em 95. **O girassol sumiu:** 308 município-anos no total e área zero em 2016–2025. Ele
#   fica no texto, mas fora das contas de risco.
# - Em 2016–2025, o NE plantou por ano 2,71 milhões de ha de milho e 1,35 milhão de ha de feijão. A mandioca ocupou só
#   419 mil ha, mas gerou **R$ 2,85 bilhões por ano**, mais que o feijão (R$ 1,97 bilhão).
# - O preço de referência é do próprio município em 94–97% dos município-anos de milho, feijão e mandioca; no sorgo, no
#   algodão e na mamona, em só 35–53% (o resto vem da mediana da UF).
# - Quixadá tem série de milho, feijão, mandioca, algodão herbáceo e mamona.
