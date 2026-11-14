# %% [markdown]
# ## 18. De quais artigos podemos transferir resultados? Análogos climáticos com dados da NASA
#
# **O problema:** os efeitos de rotação medidos na literatura vêm de climas muito diferentes (Iowa, França, Ontário,
# África, China). Para usar um número no Ceará, é preciso saber **o quanto o lugar do artigo se parece com o nosso**.
#
# **O método** funciona para qualquer ponto do planeta, então serve para o produto global:
# - **Climatologia mensal do NASA POWER** (API, comunidade AG) de cada lugar estudado nos artigos e de 12 pontos do Ceará.
# - **Assinatura climática de cada lugar:**
#   - chuva anual;
#   - sazonalidade da chuva (índice de Walsh);
#   - meses úmidos (chuva ≥ ET0/2, aproximação do período de crescimento);
#   - aridez (P/ET0, com ET0 FAO-56);
#   - Tmax da estação úmida e Tmax do mês mais quente, com a Tmax média das diárias de 2001–2024. **Corrigido em
#     14/11:** a climatologia do POWER traz o recorde do mês, e era ele que entrava antes (revisão C2 de
#     `protótipo/REVISAO_10_AGENTES.md`). Os números desta seção já são os novos.
# - **Semelhança:** distância nas variáveis padronizadas (z). Quanto menor, mais parecido.
#
# Script: `scripts/analogos_climaticos_artigos.py`. Saídas em `E:/campeonato-nasa/dados/analogos_artigos/`.
#
# **Ressalvas:**
# - As coordenadas dos sítios dos artigos são **aproximadas** (cidade, estação experimental ou zona agroecológica citada).
# - O POWER tem ~50 km de resolução.
# - O solo não entra na assinatura.
# - Pesos iguais nas 6 variáveis.

# %%
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from comum import DADOS

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})
A = pd.read_csv(DADOS / "analogos_artigos" / "assinaturas.csv")
D = pd.read_csv(DADOS / "analogos_artigos" / "distancias.csv", index_col=0)
display(A[["ponto", "grupo", "chuva_anual_mm", "et0_anual_mm", "aridez_P_ET0", "meses_umidos", "sazonalidade_walsh", "tmax_estacao_umida", "artigos"]])

# %% [markdown]
# ### 18.1 Onde cada lugar cai no espaço do clima

# %%
fig, ax = plt.subplots(figsize=(11, 6.5))
cores = {"Ceará (alvo)": "k", "Nordeste (artigos)": "tab:orange", "África (Franke 2018)": "tab:green", "Ásia": "tab:purple",
         "EUA/Canadá/Europa/China (Kluger, Bowles)": "tab:blue"}
for g, d in A.groupby("grupo"):
    ax.scatter(d.aridez_P_ET0, d.sazonalidade_walsh, s=30 + 6 * d.meses_umidos, c=cores.get(g, "gray"), label=g, alpha=0.8,
               marker="s" if g == "Ceará (alvo)" else "o")
    for _, r in d.iterrows():
        ax.annotate(r.ponto.replace("CE: ", "").split(" (")[0], (r.aridez_P_ET0, r.sazonalidade_walsh), fontsize=6.5, xytext=(3, 2), textcoords="offset points")
ax.set_xlabel("aridez (chuva ÷ ET0) — mais à esquerda = mais seco")
ax.set_ylabel("sazonalidade da chuva (Walsh) — mais alto = chuva mais concentrada")
ax.set_title("Assinatura climática (NASA POWER). Tamanho do ponto = meses úmidos")
ax.legend(fontsize=7, loc="upper right")
plt.show()

# %% [markdown]
# ### 18.2 Quem é parecido com quem (distância; menor = mais parecido)

# %%
cols = [c for c in D.columns]
fig, ax = plt.subplots(figsize=(13, 7))
Dv = D.loc[D[cols[0]].sort_values().index]
im = ax.imshow(Dv.values, cmap="viridis_r", aspect="auto", vmin=0, vmax=5)
ax.set_xticks(range(len(cols)))
ax.set_xticklabels([c.replace("CE: ", "") for c in cols], rotation=60, ha="right", fontsize=7)
ax.set_yticks(range(len(Dv)))
ax.set_yticklabels(Dv.index, fontsize=7)
for i in range(Dv.shape[0]):
    for j in range(Dv.shape[1]):
        ax.text(j, i, f"{Dv.values[i, j]:.1f}", ha="center", va="center", fontsize=5.5, color="w" if Dv.values[i, j] > 2.5 else "k")
plt.colorbar(im, label="distância climática (z)")
ax.set_title("Lugares dos artigos (linhas) × pontos do Ceará (colunas)")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 18.3 Peso de transferência
# Um efeito medido num artigo entra no motor com peso w = exp(−d²/2), em que d é a distância climática. Assim, d = 1
# pesa 0,61, d = 2 pesa 0,14 e d = 3 pesa 0,01. A tabela mostra os pesos para o Sertão Central (Quixadá).

# %%
q = D["CE: Quixadá (Sertão Central)"].sort_values()
W = pd.DataFrame({"distância": q, "peso_transferência": np.exp(-q ** 2 / 2).round(2)})
W["artigos"] = A.set_index("ponto").artigos.reindex(W.index)
display(W)

# %% [markdown]
# ### 18.4 Leitura
# - **Os análogos mais próximos do Sertão Central** são:
#   - o **Cerrado piauiense** (d 0,32; peso 0,95; Pacheco 2011/2013/2017);
#   - o **semiárido da Índia (Patancheru)** (0,75; peso 0,75), referência de semiárido tropical;
#   - **Serra Talhada-PE** (1,09; palma-sorgo de Diniz 2017 e Lima 2018);
#   - **Sobral-CE** (1,12; Sacramento 2013, carbono do solo medido).
#   - **Os estudos do próprio Nordeste são a melhor base para o Ceará**, como esperado. Nos 12 pontos do Ceará, o lugar
#     de artigo mais parecido é o Cerrado piauiense em 7, Sobral em 2 (Sobral e Itapipoca) e Teresina em 1 (Tianguá);
#     em Juazeiro do Norte, Sobral e o Cerrado empatam (d 0,60). Só em Fortaleza ele vem de fora do Nordeste: a África
#     Austral (Harare e Chitedze empatam, d 1,40; peso 0,38).
# - **Nos artigos africanos, o análogo mais parecido é a Savana da Guiné (Tamale, d 1,67; peso 0,25).** O Sahel (Niamey,
#   2,09) e a África Austral (Harare, 2,15) ficam longe: Harare caiu do 4º para o 10º lugar com a Tmax média. No Franke
#   2018, a leguminosa antes do cereal deu o mesmo efeito relativo no Sahel e na Guiné (+24%; zona × resposta, p = 0,351),
#   então a aridez não reduz o efeito relativo. Mas nenhum estrato africano chega a Quixadá com peso ≥ 0,3: o número
#   africano fica só como sensibilidade.
# - **Os celeiros onde se mediu a rotação por satélite estão entre os lugares MENOS parecidos com o Ceará:** Iowa (d
#   4,87), França (5,89), Ontário (5,97) e o NE da China (4,57). Por isso **os números de Kluger, Bowles e Renwick entram
#   como mecanismo e direção, com peso ~0, e não como valor**. O próprio Kluger mostra que o efeito varia com o clima.
# - **Texas e Kansas são semiáridos, mas de outro tipo:** frios no inverno e sem estação úmida definida. Por isso ficam
#   longe (d 2,80 e 3,98). A lição da monocultura de algodão no Texas vale para a percolação de pragas, não para o
#   rendimento. No Kansas, o único mês úmido cai no inverno, e a "Tmax da estação úmida" fica em 8,5 °C: é efeito da
#   definição de mês úmido em clima temperado.
# - **Petrolina, onde foi medido o Kc de Souza 2011/2015, é bem mais seca que o Ceará** (429 mm, nenhum mês úmido). O
#   Kc é uma propriedade da cultura e da fase, e se transfere com a ET0 local. O que não se transfere é o rendimento de
#   sequeiro.
# - **Para o produto global,** o mesmo cálculo responde, para qualquer talhão do mundo, "quais estudos foram feitos num
#   clima parecido com o meu?", e dá o peso de cada evidência no recibo.
