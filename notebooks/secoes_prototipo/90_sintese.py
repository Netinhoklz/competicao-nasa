# %% [markdown]
# ## 11. Síntese: o que cada base sustenta no protótipo do Nordeste, e o limite de cada uma
#
# | Base | O que sustenta no protótipo | Números-chave deste notebook | Limite que o cartão precisa dizer |
# |---|---|---|---|
# | **FAO GAEZ v4** | rótulo de aptidão; decide o guandu, a mandioca e o milheto fora do CE e as culturas sem ZARC no município; a única camada fora do Brasil | mandioca é a mais apta no NE (mediana 48,8); milho, caupi e sorgo ≤ 40 em 953 municípios (todos os 217 do MA) | pixel de 9 km; clima de 1981–2010; **discorda do ZARC** (Spearman de −0,54 a +0,29) |
# | **ZARC 2026/27** | janela e risco por cultura e por solo; o 1º decêndio zoneado e o 1º com 20% | 81 portarias (9 culturas × 9 UFs); janela mediana de 3 (feijão de 2ª safra) a 7 decêndios (sorgo); o solo muda a janela em 66% a 87% dos municípios | ciclos com cultivar conferidos só no CE; portarias plurianuais (mandioca, milheto, palma) só no CE, lidas dos PDFs e fora das duas datas da página; a tábua muda a cada safra |
# | **GAEZ × ZARC** | situação de cada cultura | mediana de 7 (MA, PI) a 11 (CE) culturas disponíveis; 22 municípios sem nenhuma; o corte pelo GAEZ derrubaria 7.285 pares indicados; a tabela bate com `motor.cardapio` | — |
# | **NASA POWER** | assinatura climática do lugar | 396 células para 1.794 municípios; com a Tmax média, a Tmax da estação úmida caiu 6,0 °C no CE | célula de ~55 × 70 km; a definição de "mês úmido" depende da ET0 |
# | **Análogos** | peso w e confiança do recibo | 1.080 municípios com w ≥ 0,6; 298 com w < 0,3 (90 no MA e 150 na BA) | lugares dos artigos aproximados; pouca evidência no MA e na BA |
# | **Catálogo** | regras do motor e evidência | 29 de 147 cartões com número (T0/T1); nenhuma rotação é T0 | o ganho contra o consórcio de hoje nunca foi medido |
# | **IMERG (regime)** | estação típica; avisos fora da quadra e no litoral leste | 1.056 municípios na quadra, 312 no litoral leste, 426 no Cerrado e sul da BA | na faixa até ~20 km da costa leste o IMERG capta só 39–72% da chuva; o aviso vai pela distância à costa (182 municípios) |
# | **IMERG (início e El Niño)** | início típico; nível do El Niño no município | início típico de 24/10 a 17/03 (medianas por UF e regime); ZARC × IMERG, Spearman +0,83; alerta em 922 municípios | 3–4 anos de El Niño forte: a diferença no início não se separa do acaso; 2026 é Late (preliminar) e fica fora da série |
# | **ONI** | "este ano" | ASO 2026 = +2,46, o maior ASO desde 1950 (recorde de qualquer trimestre: +2,59, em 2015/16) | 2024 foi El Niño forte e quadra normal; o Atlântico de fev–abr ainda é desconhecido |
# | **SMAP L4** | o solo agora | "seco para a época" em 981 municípios; 2026 é o mais seco dos 12 anos no MA e em SE | em novembro, não prevê a estação |
#
# **O que este estudo muda no protótipo do NE:**
# 1. **Tudo é municipal, e o motor já faz assim:** o regime, o início da chuva, o nível do El Niño e a primeira data do ZARC
#    mudam muito de um estado para outro (o alerta acende em todo o CE e em nenhum município de AL e SE).
# 2. **A regra "onde há ZARC, o ZARC decide" vale no NE inteiro:** o GAEZ e o ZARC discordam em 7 de 8 culturas, também
#    dentro de cada UF.
# 3. **A "janela do milho encolheu" sai do texto:** a mudança de 2025/26 para 2026/27 vem da troca do esquema de solo. As
#    outras 7 culturas são idênticas nas duas safras.
# 4. **A estação de 2026 (IMERG Late, preliminar) fica fora da normal e do El Niño, no motor e aqui.** Com ela, 33
#    municípios mudariam de nível (955 alertas contra 922). Quando o IMERG Final chegar, ela pode voltar.
# 5. **Pendências:**
#    - conferir nas portarias dos outros 8 estados os grupos de ciclo com cultivar (hoje, só no CE);
#    - conferir no SISZARC a vigência das portarias plurianuais do CE (hoje, pela página do MAPA de 05/11/2026);
#    - ZARC sintético fora do Brasil e SMAP global, em vez do recorte do Nordeste.
