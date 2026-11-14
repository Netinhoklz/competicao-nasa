# %% [markdown]
# ## 30. Ideias de modelos de Machine Learning e Deep Learning
#
# Ideias organizadas pelo bloco do produto que cada uma alimenta. Para cada ideia: entrada (bases deste estudo),
# rótulo/alvo, modelo de partida (baseline), modelo avançado, como validar e o que mostra ao agricultor.
# A regra de ouro: **os números saem dos modelos e das bases; o modelo de linguagem só explica.**
#
# ### Mapa rápido
#
# | # | Bloco do produto | Pergunta que o modelo responde | Bases | Baseline | Avançado |
# |---|---|---|---|---|---|
# | 1 | O que está plantado | Qual cultura/uso em cada pixel? | Sentinel-2/HLS/Landsat (NDVI, bandas), SRTM; rótulos CDL (EUA), MapBiomas/IBGE (BR) | Random Forest / LightGBM em atributos fenológicos | TempCNN, Transformer temporal; **Prithvi-EO-2.0 (NASA/IBM, treinado em HLS)** ou Presto como base pré-treinada |
# | 2 | Rotação atual e próxima cultura | Qual a sequência típica e o que vem depois? | CDL 2008–2025 (transições), solo, clima | Cadeia de Markov de 1ª/2ª ordem por região | LSTM/Transformer de sequência com contexto (clima, solo) |
# | 3 | Calendário do talhão | Quando o campo fica nu? quando planta e colhe? | NDVI MODIS/HLS/S2, chuva IMERG/POWER | Suavização Savitzky–Golay + logística dupla (estilo TIMESAT) | Segmentação temporal (1D U-Net) ou detecção de mudança bayesiana (BEAST) |
# | 4 | Água no solo do talhão | Quanta água a raiz tem hoje e nas próximas semanas? | SMAP L4, GLDAS, POWER ET0/chuva, NDVI, LST, SRTM, solo | Balanço hídrico FAO-56 (balde) | Híbrido: balde físico + correção por XGBoost; downscaling do SMAP 9 km para 30–200 m (validar com NISAR 200 m) |
# | 5 | A quadra chuvosa que vem | O próximo fev–mai será seco, normal ou chuvoso? | ONI (ENSO), TNA/TSA (Atlântico), chuva POWER/IMERG | Regressão logística multinomial de tercis | Gradient boosting/ensembles; avaliação deixando 1 ano de fora |
# | 6 | Quanto cada cultura rende aqui | Rendimento esperado e risco de quebra por cultura | IBGE PAM (municípios), POWER, IMERG, NDVI, GAEZ | Regressão com efeitos fixos de município + clima | LightGBM com SHAP; emulador de modelo de cultura (AquaCrop/DSSAT rodado com POWER) |
# | 7 | Risco de fogo | Probabilidade de queimada no mês, por célula | FIRMS VIIRS, MCD64A1, NDVI, LST, chuva acumulada, uso do solo | LightGBM por célula-mês | ConvLSTM / U-Net espaço-temporal |
# | 8 | Pragas | Quantas gerações da praga cabem no ciclo? a paisagem favorece a dispersão? | POWER (graus-dia), mapa de culturas (CDL/MapBiomas), distâncias | Graus-dia + **percolação** (maior aglomerado conectado de hospedeiros) | Rede neural de grafos (GNN) se houver rótulos de ocorrência |
# | 9 | Motor de rotação | Quais 3+ rotações maximizam as prioridades do agricultor? | Tudo acima + GAEZ/EcoCrop + preços FAOSTAT | Regras agronômicas + pontuação ponderada (pesos do agricultor) | Otimização multiobjetivo (NSGA-II) ou programação inteira; RL (PPO) num simulador de talhão |
# | 10 | Explicação | Por que esta rotação? com que evidência? | Saídas do motor + fichas técnicas + literatura | Modelos de texto com campos preenchidos | LLM com RAG (citando a base e o número), sem inventar números |
#
# ### Detalhe das ideias mais promissoras para 48 h
#
# **(5) Previsão de tercil da quadra chuvosa no Ceará — alto impacto, baixo custo.**
# - A chuva de fev–mai no Ceará responde ao Pacífico (El Niño seca, La Niña chove) e ao gradiente do Atlântico tropical
#   (TNA quente/TSA fria = seca).
# - **Previsão:** com índices de out–dez, prever o tercil antes do plantio (jan).
# - **No produto:** "este ano tende a ser seco → priorize rotação com sorgo/feijão-caupi/palma; adie o milho".
# - **Validação:** deixar 1 ano de fora em 1981–2025; métrica RPSS ou acurácia de tercil contra a climatologia.
#
# **(4) Balanço hídrico híbrido — o coração do motor.**
# - **Modelo físico:** `S(t+1) = S(t) + P − ETc − D`, com `ETc = Kc(cultura, estágio) × ET0(POWER)` e capacidade de
#   água do solo (SSURGO/SoilGrids/GAEZ).
# - **Correção por ML:** um modelo aprende o erro do balde contra SMAP L4/GLDAS.
# - **Saída:** déficit hídrico por estágio de cada cultura candidata, ou seja, o "custo de água" de cada rotação.
#
# **(3) Fenologia + janelas de solo nu.**
# - **Método:** a curva de NDVI (MODIS 250 m para o histórico, HLS/S2 para o talhão) é suavizada e ajustada.
#   Início, pico, fim e os meses com NDVI abaixo de um limiar marcam as **janelas para plantas de cobertura**.
#
# **(1)+(2) Do pixel à rotação.**
# - **Nos EUA:** o CDL dá rótulos anuais por pixel. Uma cadeia de Markov das transições (ex.: milho→soja) é o
#   "prior" de rotação.
# - **No Brasil:** MapBiomas e IBGE dão a supervisão. Com o IBGE PAM, que só informa proporções por município, dá para
#   treinar classificadores por **aprendizado a partir de proporções** (*learning from label proportions*).
#
# **(8) Percolação de pragas.**
# - **Grafo:** talhões com a mesma família hospedeira são nós; arestas ligam talhões a menos de X km.
# - **Métrica:** quando a fração de hospedeiros passa do **limiar de percolação**, forma-se um aglomerado gigante e a
#   praga atravessa a paisagem.
# - **No produto:** a rotação que **quebra a conectividade** reduz o risco regional, o que dá um argumento coletivo,
#   não só individual.
# - **Exemplo histórico:** o bicudo-do-algodoeiro no Nordeste nos anos 1980.
#
# ### Validação e incerteza (critério "Validade")
# - Validação **espacial e temporal em blocos**: deixar município/ano de fora para não vazar a autocorrelação.
# - **Predição conformal** para intervalos de confiança honestos.
# - **Ensembles** para a incerteza do modelo.
# - Em cada mapa, mostrar a **escala real da camada**: região (≥ 9 km) × talhão (10–30 m).
# - Revisão humana: cada estratégia termina com "o que confirmar com o técnico de campo".
#
# ### Roteiro sugerido
# 1. **MVP (48 h):** calendário de riscos (estatística), balanço hídrico FAO-56, filtro GAEZ, pontuação de 3 rotações,
#    previsão de tercil (5) e explicação.
# 2. **Pós-hackathon:** classificação de culturas com Prithvi/Presto, downscaling do SMAP, modelo de fogo e grafo de pragas.
# 3. **Visão:** simulador de talhão + aprendizado por reforço para rotações robustas sob cenários NEX-GDDP-CMIP6.

# %%
print("Seção de ideias (texto).")
