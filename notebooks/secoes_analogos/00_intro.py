# %% [markdown]
# # Transferir evidência com dados da NASA: análogos climáticos, aptidão e ciclo de plantio
#
# **Pergunta central:** a literatura de rotação vem de climas diferentes do sertão. **De quais estudos podemos usar os
# números no Ceará, e no mundo, e com que peso?** E, para cada lugar, **o que plantar e quando**?
#
# Este notebook aprofunda as conclusões da seção 18 do estudo principal:
# 1. **Robustez:** a ordem dos análogos depende de quais variáveis climáticas usamos?
# 2. **Mapa de análogos no Ceará:** para cada um dos 184 municípios, o estudo de clima mais parecido e a confiança da transferência.
# 3. **O sertão no mundo:** onde, no planeta, o clima se parece com o do Sertão Central, e onde o produto vale igual.
# 4. **Aptidão das culturas nos análogos:** o GAEZ confirma que as mesmas culturas cabem nos lugares parecidos?
# 5. **Ciclo de plantio:** o início da estação pela chuva (IMERG) e pelo verde (MODIS), por município, de 1998 a 2026,
#    e o efeito do El Niño.
# 6. **Como isso entra no motor da QUADRA.**
#
# **Dados:**
# - NASA POWER (climatologia, API, qualquer ponto do planeta);
# - NASA GPM IMERG V07 (diário, 0,1°);
# - NASA MODIS MOD13Q1 (NDVI, 16 dias);
# - FAO GAEZ v4 (aptidão);
# - IBGE (malha municipal);
# - NOAA (ONI).
#
# Preparação: `scripts/preparar_analogos_aprofundado.py` e `scripts/analogos_climaticos_artigos.py`.

# %%
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from comum import DADOS, ceara_gdf, municipios_ce_gdf, paises_gdf

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False})
D_ART = DADOS / "analogos_artigos"
D_APR = DADOS / "analogos_aprofundado"
VARS = ["chuva_anual_mm", "sazonalidade_walsh", "meses_umidos", "aridez_P_ET0", "tmax_estacao_umida", "tmax_mes_mais_quente"]
ROT = {"chuva_anual_mm": "chuva anual", "sazonalidade_walsh": "sazonalidade", "meses_umidos": "meses úmidos",
       "aridez_P_ET0": "aridez P/ET0", "tmax_estacao_umida": "Tmax estação úmida", "tmax_mes_mais_quente": "Tmax mês mais quente"}
A = pd.read_csv(D_ART / "assinaturas.csv")
SIT = A[A.grupo != "Ceará (alvo)"].reset_index(drop=True)
CE12 = A[A.grupo == "Ceará (alvo)"].reset_index(drop=True)
MU = A[VARS].mean()
SD = A[VARS].std()


def z(df):
    return (df[VARS] - MU) / SD


def dist(alvo_z, fontes_z, pesos=None):
    w = np.ones(len(VARS)) if pesos is None else np.asarray(pesos)
    return np.sqrt((((fontes_z.values - alvo_z.values[None, :]) ** 2) * w).sum(1) * len(VARS) / w.sum())


print(f"{len(SIT)} lugares de artigos; {len(CE12)} pontos de referência do Ceará")
