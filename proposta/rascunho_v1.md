# QUADRA: rascunho v1 da proposta (NASA Space Apps 2026, desafio "Field Shift")

- **Versão:** rascunho v1, sábado 14/11/2026, 08:46 (hora local). Prazo de submissão: domingo 15/11/2026, 23:59.
- **De onde vem:** fusão das 10 propostas da rodada 1, dos 10 pareceres do debate (rodada 2) e do placar médio do conselho.
- **Regra de honestidade:** todo número tem arquivo de origem. As referências vêm da revisão `pesquisa/artigos_e_datasets.md`. As poucas que estão fora dela trazem a marca "fora da revisão" e precisam ser conferidas antes de entrar num slide.
- **Números canônicos novos desta versão:** `conselho/analises/arquiteto_numeros_canonicos.py`, com saída em `conselho/analises/saidas/arquiteto_numeros_canonicos.txt`.

---

## 0. Resumo executivo

- **O que é:** o QUADRA trata a rotação no semiárido como uma **política com cinco portões de decisão ao longo do ano**, e não como uma sequência fixa de culturas.
- **Por que portões:** cada portão abre quando três condições valem ao mesmo tempo:
  - os dados NASA já sabem algo naquela data (habilidade medida sem vazamento);
  - a jogada ainda é agronomicamente possível (data-limite de cada cultura);
  - o satélite consegue ver o talhão.
- **Como compara:** a estratégia atual e pelo menos três alternativas são **reencenadas nas 28 quadras observadas pelo GPM/IMERG** (44 com o POWER) no município do agricultor. O ranking é pelo **pior ano**, não pela média.
- **O recibo:** cada número carrega a missão NASA de origem, a escala, o tipo de validação e um grau de evidência de A a D.
- **Quem usa:** o extensionista (painel web) e a família (cartão com áudio, em frequências naturais).
- **A IA:**
  - modelos pequenos, guiados pela física, validados por ano e com incerteza calibrada;
  - um LLM que **só explica**, travado por um verificador de números.
- **Por que agora:** hoje o Pacífico está no **El Niño mais forte já medido para ago–out** (ONI ASO/2026 = +2,46; o recorde anterior era 2,04, em 1997). A demo é o plano de 2027 de uma família de Quixadá, ao vivo.

---

## 1. Nome e frase de efeito

**Nome:** **QUADRA**, que é a palavra do sertão para a estação chuvosa de fevereiro a maio. Subtítulo: *Field Playbook*. Nome reserva: *Field Replay*.

**Por que não "PROFETA":** o próprio estrategista retirou o nome. Ele promete certeza, que é justamente o que os dados negam em janeiro. Também arrisca soar como apropriação dos profetas da chuva. Eles entram no produto como parceiros, no "Checkpoint São José" e no registro "Meus sinais".

**Frase de efeito (PT):**
> "Em janeiro, ninguém sabe como vai ser a quadra, nem o satélite. O QUADRA reencena no seu chão todas as quadras que a NASA já viu, mostra como cada rotação aguentaria o pior ano e avisa quando é hora de mudar o plano."

**Frase de efeito (EN, pitch):**
> "In January, nobody knows the rainy season, not even satellites. QUADRA replays every season NASA has observed on your land, ranks rotations by their worst year, and tells you when to shift."

**Tagline curta (EN):** *Replay every rainy season NASA has seen. Shift at the right checkpoint.*

**Por que este conceito venceu (decisão do arquiteto):**

| Peça | Origem | Por que entra |
|---|---|---|
| Rotação como política com portões | Agrônomo, "Playbook do Roçado" (8,4; 9 votos) | Esqueleto mais votado. Seis propostas chegaram a ele de forma independente: agrônomo, clima, IA, designer, estrategista e cético. |
| Replay das quadras observadas, conformal robusto ao ano, Pareto pela cauda | Pesquisador de IA, "SeasonReplay" (8,3) | Torna a comparação concreta ("o que teria acontecido em 2012 no seu chão") e dá a incerteza honesta. |
| Recibo A–D, auditoria, sentinela de deriva, duas escalas | Cético, "FieldProof" (8,3) | É a espinha do critério Validade. |
| Risco no ano ruim, correlação entre culturas, pilha de risco | Economista, "CropFolio" (8,3) | É a métrica que importa para a família. |
| Calendário, curva de antecedência, São José, 2027 ao vivo | Estrategista (8,1) | Leitura do júri e eixo do storytelling. |
| Portão de habilidade, aviso de caso inédito, valor de decisão | Clima, "ShiftCast" (7,9) | Diz quando o oceano informa e quando não. |
| Entrega por voz, frequências naturais, técnico no circuito, data de plantio | Designer, "Compadre" | Resolve a adoção. |
| Dois relógios da água, salvamento contra irrigação na seca | Hidrólogo, "Extrato d'Água" | Vira a linha "conta de água" de cada cartão e o relógio lento. |
| Código de barras do talhão (versão leve), selo de visibilidade, açude a 30 m | Sensoriamento remoto, "FieldMemory" (6,2) | Detecta a estratégia atual e diz quando o satélite enxerga. |
| Portão de entressafra (combustível, fogo, pousio, ciclo de praga) | Ecólogo, "CycleBreak" (6,1) | Preenche o portão que todas as outras propostas deixaram vazio. |

---

## 2. O problema

### 2.1 No Ceará, com os nossos dados

1. **Uma janela, uma chance.**
   - 77,5% do Ceará comporta uma única safra de sequeiro (GAEZ; `notebooks/secoes/90_sintese.py`, 90.2).
   - A estação vai de cerca de 2/fev a 28/jul, com pico em abril, e o solo fica exposto de setembro a janeiro (MODIS; mesma seção).
   - A chuva média é de 809 mm/ano e a ET0 de 2.279 mm/ano (POWER, média do CE, 1991–2020; `arquiteto_numeros_canonicos.txt`, bloco B).
   - Observação: a síntese cita ET0 de cerca de 1.960 mm/ano. O valor correto, calculado direto do `power_ce_mensal`, é 2.279. Ver a errata no item 9.7.
2. **O sistema dominante concentra o risco.**
   - Milho e feijão ocupam 91% da área (Rocha et al. 2021).
   - As duas culturas quebram juntas. A correlação mediana das anomalias de rendimento no mesmo município é **0,78** (183 municípios, 1998–2025; `arquiteto_numeros_canonicos.txt`). Três especialistas acharam o mesmo por outros caminhos: 0,74, 0,75 e 0,76.
   - **O consórcio tradicional não diversifica contra a seca.**
3. **A quebra é frequente e sincronizada.**
   - Definição canônica de quebra: rendimento por área plantada abaixo de 50% da mediana do próprio município nos *outros* anos, sem vazamento.
   - O milho quebrou em **21,5%** dos 5.106 município-anos de 1998–2025.
   - Fração de municípios em quebra: **75%** em 1998 e em 2012, 70% em 2016, 61% em 2010.
   - O rendimento estadual do milho caiu **−69%** em 2012 (`arquiteto_numeros_canonicos.txt`, bloco D).
   - Cerca de metade da variância da quebra municipal é choque comum ao estado no mesmo ano: 45–53% no milho (`conselho/analises/cetico_escala_vazamento.py`).
4. **O El Niño pesa além da chuva.**
   - Nos anos com ONI de NDJ ≥ 1,0, o milho quebrou em 36,5% dos município-anos, contra 17,5% nos demais (`arquiteto_numeros_canonicos.txt`).
   - Mesmo controlando a chuva de fev–mai e o município, o El Niño ainda **dobra a chance de quebra do milho**: OR 2,30, IC 1,83–2,89 (`conselho/analises/agronomo_debate_checagens.py`).
   - O ONI de ASO, já conhecido em novembro, reduz a anomalia log do milho em −0,208 por unidade, controlando a chuva (p = 0,003; n = 44; `conselho/analises/clima_r2_checagens.py`, bloco D).
5. **O solo fica nu e queima.**
   - 72% dos focos de fogo caem em out–dez (VIIRS; síntese 90.2).
   - 17,4% do Ceará queimou ao menos uma vez em 2012–2025.
   - Onde o fogo volta, volta num intervalo mediano de **3 anos** (`conselho/analises/ecologo_fogo_pousio_combustivel.py`).
   - O corte e queima sem pousio perde cerca de 50% do carbono do solo em 10 anos (Primo et al. 2023, Sobral-CE).
6. **Em janeiro, ninguém sabe o ano.**
   - A habilidade para prever a quebra do milho no município é praticamente nula no plantio: AUC de 0,52 em 31/jan (`conselho/analises/designer_curva_pct_normal.py`).
   - O tercil de chuva em novembro não tem habilidade: RPSS de −0,01 (`conselho/analises/clima_previsao_progressiva.py`).
   - A habilidade só cresce durante a quadra: AUC de 0,77 em 30/abr.

### 2.2 Por que as ferramentas atuais não resolvem

- O **ZARC** dá a janela de plantio de uma cultura, mas a janela não muda com o ano.
- O **prognóstico de tercis** não vira decisão de rotação.
- **Painéis de NDVI** mostram o passado e não comparam estratégias.
- Marengo et al. (2021) mostram que a adaptação à seca no Nordeste ainda é quase toda **pós-desastre**.
- Dury et al. (2012) mostram que o plano de cultivo real é dinâmico e adaptativo, mas os modelos o tratam como estático.
- No Ceará, previsões comunicadas como certeza já custaram a confiança dos agricultores (Lemos et al. 2002, fora da revisão; DOI conferido no Crossref pelo designer na rodada 1).

### 2.3 Por que agora

- O **ONI ASO/2026 é +2,46**, o maior valor para ago–out desde 1950. Os anteriores foram 2,04 (1997) e 2,02 (2015).
- Não é o recorde absoluto: o maior ONI de qualquer trimestre foi 2,59, em NDJ 2015 (`arquiteto_numeros_canonicos.txt`, bloco A).
- **A reserva de água está caindo.** O GRACE do Ceará, dessazonalizado, foi de +3,76 cm (p72) em julho para +2,49 cm (p68) em agosto e **−3,30 cm (p35)** em setembro de 2026 (mesmo arquivo, bloco C).
- A estação seca de 2026 ficou cerca de −0,5 desvio-padrão em agosto e outubro no IMERG Late (seção 05).

### 2.4 Por que importa no mundo

- O problema "uma janela de chuva, falso início e data-limite" é o mesmo no Sahel, no Chifre da África, na Índia de sequeiro e no semiárido do Texas. No Texas, o CDL mostra 67% de algodão contínuo (síntese 90.2, item 11).
- Na amostra global do POWER, **86% dos pontos tropicais não têm nenhum mês em que o frio interrompa o ciclo da lagarta-do-cartucho**, contra 7 meses em Iowa (`conselho/analises/ecologo_grausdia_global_2020.csv`). Onde não há inverno, só a rotação e a entressafra quebram o ciclo.
- Todo o núcleo de dados do QUADRA é global: IMERG, POWER, SMAP, GRACE, HLS, VIIRS, SRTM e NEX-GDDP (síntese 90.1).

---

## 3. A solução: o que o agricultor e o extensionista veem e fazem

### 3.1 Dois usuários, um motor

- **Extensionista (técnico de ATER, cooperativa, ONG):** é o usuário principal do MVP. Usa um painel web estático que funciona offline depois de carregado. Atende uma lista de famílias, aprova ou edita cada mensagem e vê a evidência completa.
- **Família agricultora:** recebe um **cartão em imagem** (ícones fixos para água, forragem, nitrogênio, solo, matéria orgânica e mercado), um **áudio de até 45 s** e um texto curto.
  - Os números saem em frequências naturais: "de cada 10 anos como este, 4 quebraram o milho".
  - O cartão traz no máximo 3 números.
  - A família informa a data de plantio e as prioridades, e pode vetar uma sugestão.

### 3.2 As telas do painel

1. **Meu chão.**
   - Mapa com município ou ponto lat/lon (qualquer lugar do mundo).
   - A **estratégia atual é inferida** por um código de barras de safras: fenologia MODIS/HLS (ciclos e meses de solo nu), focos VIIRS (queima pré-plantio) e verde na seca (irrigação ou perene).
   - O app faz **uma pergunta de confirmação** ("o senhor queimou este roçado em nov/2025?"), e a resposta corrige o código de barras.
2. **Relógio da Quadra.** Uma linha do tempo de novembro de um ano a dezembro do ano seguinte, com os 5 portões e o de hoje destacado. Para cada portão:
   - **o que a NASA já sabe**: habilidade medida, em frequência natural;
   - **o que ainda não sabe**;
   - **o que ainda dá para fazer**: datas-limite;
   - **selo de visibilidade**: quantas vezes o satélite viu a área nos últimos 30 dias.
3. **Cartões de estratégia.** A atual e mais 3, lado a lado. Cada uma traz os 5 campos pedidos pelo desafio: por que foi sugerida, evidência (com recibo), benefícios, lacunas de informação e riscos a confirmar com o técnico. Há também as linhas "conta de água", "quem cobre seu risco" e "ciclos" (fogo e praga).
4. **Replay.** As quadras de 1998, 2012 e 2016 animadas dia a dia com a chuva IMERG do município. Os cartões divergem e os portões acendem na data em que acenderiam.
5. **2027 ao vivo.** Mostra:
   - ONI e Atlântico;
   - anos análogos reais (1983, 1998 e 2016 secos; 2024 normal; 1973 e 1988 chuvosos);
   - banco de água (GRACE, açudes vistos pelo Landsat);
   - IMERG Late da estação seca;
   - razão de preço ureia/milho atual.
6. **Auditoria** (para o técnico e o júri):
   - validação aleatória contra validação por ano;
   - curva de habilidade por portão;
   - sentinela de deriva dos sensores;
   - "onde erramos";
   - "o que não fizemos".

### 3.3 Fluxo de uso ao longo do ano

| Quando | O técnico faz | A família recebe ou faz |
|---|---|---|
| Primeira visita (qualquer data) | Marca o roçado. Confirma a prática atual com 1 pergunta. Faz 4 a 6 **perguntas de troca** ("prefere pasto garantido para os bichos ou arriscar mais milho para vender?") que viram os pesos. Registra o rebanho, a semente guardada, a mão de obra e o volume de água guardada (cisterna de beber, cisterna de produção, barreiro). | Cartão de apresentação: "o QUADRA não sabe tudo; aqui está o que ele sabe". |
| P1, novembro e dezembro | Lê o portão do oceano e o banco de água. | Ações sem arrependimento: semente de caupi precoce e sorgo, palma, adesão ao Garantia-Safra, não queimar, aceiro. |
| P2, janeiro e início de fevereiro | Lê a chuva recente e o solo. | "Plante uma parte agora e o resto quando firmar." A família informa a **data de plantio**. |
| P3, de 28/fev a 19/mar ("Checkpoint São José") | Lê o acumulado desde o plantio. | Troca possível só para caupi ou sorgo, antes da data-limite. |
| P4, 30 de abril | Lê o alerta de meio da quadra, a vegetação relativa aos vizinhos e o ESI. | Ação graduada: guardar forragem, cortar o milho para as cabras se o alerta se repetir e o técnico confirmar, plantar caupi na umidade que resta. |
| P5, julho a dezembro | Lê o combustível visto do espaço e a água que sobrou. | Palhada em vez de fogo, fenação do excedente, aceiro, perene em nível. |
| Fim de safra | Registra o resultado. | Veredito: a família ordena os caminhos que testou. É evidência local de rotação, que hoje não existe. |

### 3.4 Glossário em pop-up (exigência do desafio)

- **Evapotranspiração (ET/ET0):** a água que o solo e a planta devolvem ao ar.
- **Balanço hídrico:** chuva que entra menos água que sai, dia a dia.
- **Anomalia de umidade:** quanto o solo está acima ou abaixo do normal daquela época.
- **NDVI:** o quão verde e vigorosa a vegetação está, visto do satélite.
- **Geada:** temperatura mínima ≤ 0 °C. Só aparece onde se aplica, ou seja, fora do Ceará.
- **ISNA:** fração da água que a cultura precisou e recebeu.
- **"Pior ano em 10":** substitui o CVaR10 na tela da família.
- **Percentil.**
- **Grau de evidência A–D.**

### 3.5 Apoiar, não substituir

- Os pesos vêm da família.
- O técnico aprova ou edita toda mensagem.
- A família pode vetar ("não quero sorgo"), e o app recalcula e mostra o custo da escolha.
- Toda recomendação respeita a janela do ZARC.
- Todo cartão termina com "o que confirmar no chão com o técnico".

---

## 4. Arquitetura: núcleo global de dados NASA e enriquecimento local

### 4.1 Visão geral

```
            NÚCLEO GLOBAL (qualquer ponto da Terra)                       ENRIQUECIMENTO LOCAL (quando existe)
 IMERG V07 diário 0,1° (1998→; Late p/ ano corrente)        Brasil: IBGE PAM (calibração), ZARC (restrição dura),
 POWER (1981→: Tmax/Tmin, radiação, ET0, GWETROOT)                  MapBiomas, regras do Garantia-Safra/PNAE/PAA
 SMAP L4 zona da raiz (9 km)  · GLDAS-2.1/2.2               EUA: CDL/CSB, NASS, SSURGO, NLDAS
 GRACE/GRACE-FO mascons (~300 km)                            Resto: FAOSTAT, GDHY, calendários SAGE/GGCMI
 HLS 30 m · Landsat 1984→ · MODIS→VIIRS · ECOSTRESS 70 m     Agricultor: data de plantio, pluviômetro, água guardada,
 VIIRS/FIRMS 375 m · NASADEM/SRTM (+Copernicus DEM)                     veredito de fim de safra
 NEX-GDDP-CMIP6 · GAEZ/ECOCROP · ONI/TNA/TSA (NOAA)
                  │                                                         │
                  ▼                                                         ▼
       GRADE COMUM + REGRAS DE ESCALA  ──►  MOTOR (M1–M7)  ──►  PORTÕES P1–P5  ──►  CARTÕES + RECIBO  ──►  EXPLICADOR (M8)
```

### 4.2 Grade comum e regras de harmonização

| Camada | Resolução nativa | Como entra na grade comum | Regra de uso |
|---|---|---|---|
| IMERG | 0,1° (~11 km), diário | É a **grade de decisão**. Agregada também ao polígono do município para calibrar contra o PAM. | Chuva, veranico e acumulado por portão. |
| POWER | 0,5°, diário | Célula válida mais próxima de cada célula IMERG. | Sempre como **anomalia ou percentil por fonte**. A Tmax do POWER é cerca de 1,7 °C mais quente que a do ERA5 (síntese 90.2). |
| SMAP L4 | 9 km, 3 h | Média por célula IMERG, com **casamento de CDF** contra o balde. | Percentil da zona da raiz, nunca limiar absoluto em mm. Há dados só desde 2015, então os gatilhos são testados com o balde (Rossato 2017: a planta responde à camada rasa). |
| GRACE/GRACE-FO | ~300 km | Mascon regional, **média móvel de 3 meses**. | Só contexto regional, nunca o talhão. O recibo mostra n_eff ≈ 28 (`cetico_memoria_grace_neff.py`). |
| HLS / Landsat / S2 | 30 m (20 m) | Desvio **relativo à vizinhança de 10–20 km na mesma data**. | Cancela a deriva comum dos sensores e o viés de amostragem: o céu limpo coincide com o veranico (`sr_fundacao_r2_ceu_limpo_veranico.py`). |
| MODIS → VIIRS | 250 m – 1 km | Histórico do NDVI relativo (2000→) e fenologia. | A LST diurna do Terra fica fora depois de 2020 por causa da deriva (ver M6). |
| ECOSTRESS | 70 m, revisita irregular | Camada experimental de estresse no portão P4. | Grau C enquanto não for validado localmente. |
| VIIRS/FIRMS | 375 m (~14 ha) | Recorrência de fogo por pixel, agregada à paisagem. | É maior que o roçado de 1–3 ha: nunca serve para fiscalizar um talhão. |
| NASADEM/SRTM | 30 m | Declive e baixio por talhão ou município. | Erosão, baixio e aleias em nível. |
| NEX-GDDP | 0,25° | Delta de Tmax aplicado sobre o replay. | Cenário rotulado. Usar vários modelos para chuva (síntese 90.1). |

### 4.3 Que variáveis entram em cada módulo

| Módulo | Variáveis NASA | Variáveis locais | Saída |
|---|---|---|---|
| M1, gêmeo físico | IMERG diário; ET0, Tmax e radiação do POWER; estado inicial SMAP L4 (GWETROOT ou GLDAS como reserva); declive NASADEM | Água disponível do solo (HWSD/SoilGrids/ZARC AD), data de plantio, Kc e ciclos | ISNA por estágio, sobra de água na colheita, escoamento, demanda de salvamento |
| M2, emulador de risco | Saídas de M1; dias quentes acima do p90 local (POWER); NDVI relativo (MODIS/HLS) | ONI; PAM (alvo) | P(quebra), mediana, P10, intervalo conformal |
| M3, previsor por portão | IMERG acumulado e veranico desde o plantio; SMAP; GRACE | ONI, TNA, TSA | Probabilidade por portão, habilidade, aviso de caso inédito, análogos |
| M4, política e carteira | Replay de M1 e M2 em 28 ou 44 quadras | Pesos, restrições (ZARC, cesta do Garantia-Safra, semente, água, mão de obra), preços FAOSTAT | Fronteira de Pareto, 3 estratégias + a atual, árvore de regras |
| M5, prática atual | MODIS/HLS (fenologia), VIIRS (queima), Landsat (verde na seca) | MapBiomas, CDL, resposta do agricultor | Código de barras de safras, estratégia atual |
| M6, sentinela de deriva e qualidade | LST e NDVI do MODIS contra POWER e HLS | PAM (bandeira de relato repetido) | Rebaixamento automático do grau de evidência |
| M7, relógio lento e combustível | GRACE, GLDAS Noah/CLSM, fração de água do Landsat (açudes), NDVI de fev–jun em t e t−1, focos VIIRS | Volume do barreiro ou da cisterna | Banco de água azul, área salvável, perspectiva de fogo de out–dez |
| M8, explicador | JSON de todos os módulos | Revisão de 73 artigos | Texto dos cartões em PT e EN, áudio, glossário |

### 4.4 Frescor dos dados na data da demo (14/11/2026)

- IMERG Late: até 12/11/2026.
- IMERG V07 diário via POWER: até set/2026.
- ONI: até ASO/2026.
- GRACE: até set/2026.
- GLDAS Noah mensal: até jul/2026.
- MODIS: até nov/2026, com o buraco de jun–nov/2025 no Terra.
- PAM: até 2025.
- Focos VIIRS no arquivo anual: até dez/2025. O NRT exige chave.
- Pink Sheet: até out/2026.
- SMAP L4 (AppEEARS) e GLDAS diário com água subterrânea ainda estão chegando. **O MVP não depende deles**: o estado do solo usa o GWETROOT do POWER e o GLDAS mensal como reserva.

---

## 5. Os módulos de IA (SI)

Princípio da equipe, medido nos dados: **com 28 quadras, o modelo pequeno, guiado pela física e validado por ano vence o modelo grande.** Exemplos:

- O ML livre sobreajusta: o GBM pré-safra tem MSSS de −0,37 (`pesquisador_ia_conformal_carteira.py`).
- A validação aleatória mente: R² 0,49 contra −0,08 deixando o ano de fora (`cetico_escala_vazamento.py`).
- A restrição física generaliza: AUC 0,794 contra 0,727 (`hidrologo_hibrido_fisica_ml.py`).

### M1. Gêmeo físico do roçado com calibração inversa

- **Papel:** simular, para cada cultura, consórcio e revezamento, a água que a planta recebe em cada estágio, em qualquer ponto do mundo.
- **Método:**
  - balde diário FAO-56 (ETc = Kc × ET0) vetorizado em numpy;
  - **calibração inversa por grade**: a data efetiva de semeadura, a água disponível do solo e o Kc que melhor explicam o rendimento observado da região. É isso que adapta o motor a outro país.
- **Entrada:** IMERG, ET0 do POWER, estado inicial do solo, água disponível do solo, Kc e ciclos (FAO-56, Allen et al. 1998).
- **Saída:** ISNA por estágio, sobra de água na colheita, escoamento, demanda de salvamento.
- **Validação:**
  - O ISNA do milho separa a quebra melhor que a chuva total: AUC 0,810 contra 0,775 (`hidrologo_fao56_isna_pam.py`). Dois baldes independentes, do agrônomo e do hidrólogo, chegam a AUC de 0,81–0,84.
  - O ZARC sintético ordena os municípios como a quebra real: ρ de +0,40 a +0,49; r anual +0,68 (`agronomo_isna_zarc_sintetico.py`).
  - A inversão revelou a prática real: o milho se comporta como semeado 0–10 dias após a 1ª chuva, e o feijão cerca de 20 dias depois (`agronomo_calibracao_pratica.py`).
- **Incerteza:**
  - A ordem de risco resiste à água disponível do solo (ρ de 0,46 a 0,48 entre 30 e 90 mm).
  - O **nível** não resiste: P(ISNA < 0,5) vai de 1,5% a 14,3% conforme os parâmetros do solo (`saidas/hidrologo_calibracao_balde.csv`).
  - Por isso o nível é calibrado em M2, e a água disponível do solo é a primeira lacuna que o app pergunta.

### M2. Emulador de risco em duas escalas, monotônico

- **Papel:** converter o estado físico em probabilidade de quebra, mediana e P10 de cada estratégia em cada quadra do replay. Corrige o otimismo do balde.
- **Método:** gradient boosting com restrição monotônica (mais água nunca reduz o rendimento), ou ridge, em duas escalas:
  - **nível do ano:** ISNA agregado + calor relativo na floração (percentil local do POWER) + ONI;
  - **ordem local:** desvio do ISNA do município + desvio do NDVI relativo aos vizinhos na mesma data.
- **Entrada:** M1, POWER, MODIS/HLS, ONI. O alvo é o PAM municipal (no Brasil), NASS (EUA) ou FAOSTAT/GDHY (resto).
- **Saída:** P(quebra < 50%), mediana, P10 e intervalo.
- **Validação deixando o ano de fora:**
  - **R² 0,365, AUC 0,851, ρ dentro do ano 0,307, viés walk-forward de 2020–2025 de +0,01** (`pesquisador_ia_fusao_fisica_satelite.py`). Para comparar: só chuva dá R² 0,102; a versão "chuva + NDVI" dá 0,053.
  - O GBM monotônico vence o livre: AUC 0,794 contra 0,727 (`hidrologo_hibrido_fisica_ml.py`).
  - O híbrido ISNA + calor ganha da chuva sozinha: AUC 0,841 contra 0,808 (`agronomo_calibracao_pratica.py`).
- **Por que é obrigatório:** o balde puro erra justo nos anos que decidem.
  - Superestima 2010 (96% dos municípios com ISNA < 0,5 contra 45% em quebra real) e 2013 (46% contra 20%).
  - Não vê 1998 nem 2001 (4% e 1% contra 67% e 49%) (`pesquisador_ia_checa_simulador_anos.py`).
- **Incerteza:** **conformal robusto ao ano**, que trata o ano como unidade trocável. Cobre 77–86% dos anos no nível prometido, contra 46–68% do conformal padrão (`pesquisador_ia_conformal_carteira.py`).

### M3. Previsor por portão, com portão de habilidade

- **Papel:** em cada portão, dizer o que já se sabe, com a habilidade medida, e quando não se sabe nada.
- **Método:**
  - regressão logística regularizada e calibrada, treinada só com o que se conhece em cada data;
  - **portão de habilidade:** a previsão só aparece no regime em que tem histórico. Em novembro, isso exige |ONI| ≥ 1: RPSS +0,13 nesses anos contra −0,06 nos demais (`clima_valor_decisao.py`);
  - **detector de caso inédito:** o ONI de 2,46 está acima do máximo de ASO usado no treino (2,04);
  - **análogos k-NN** só para a narrativa ("este ano parece 1998 e 2016"). Medimos que os análogos sozinhos são mal calibrados como probabilidade (`designer_calendario_decisao.py`).
- **Validação, curva de habilidade sem vazamento** (milho, quebra municipal):

  | Data | AUC | Fonte |
  |---|---|---|
  | 31/jan | 0,52 | designer |
  | 28/fev | 0,65 | designer |
  | 31/mar | 0,70–0,72 | estrategista (refeita) e designer |
  | 30/abr | **0,77** (IC90 0,69–0,82, bootstrap por ano) | `cetico_r2_checagens.py` |

  - Em 30/abr: "chuva < 75% do normal desde 1/jan" separa 3,8 contra 1,1 quebras em 10 (3,5×; IC90 2,1–5,8).
  - Valor econômico em 01/fev pelo modelo custo–perda com regra fixa: V de 0,23 a 0,39 (`saidas/clima_valor_relativo.csv`).
- **Incerteza e escala declaradas:**
  - O alerta é **regional**. A média estadual do "% do normal" dá a mesma AUC que a municipal (0,77).
  - Entre municípios no mesmo ano, a AUC cai para 0,55–0,57, e para 0,59 com o NDVI (`cetico_r2_fusao_duas_escalas.py`).
  - Para 2027 a tela mostra uma **faixa** e o **n de análogos**, nunca um número único.

### M4. Otimizador de política e de carteira

- **Papel:** gerar e ordenar as estratégias, a atual mais pelo menos 3, e a regra de cada portão.
- **Método:**
  - **enumeração exata** de uma biblioteca de jogadas por portão (regras de plantio R1–R9, troca de cultura, revezamento, salvamento, cobertura, carteira);
  - **fronteira de Pareto** em P(colher menos da metade), CVaR10 ("pior ano em 10"), mediana, água azul, meses de solo coberto, N, trabalho e ciclos;
  - **mínimo CVaR por programação linear** (Rockafellar–Uryasev, fora da revisão; DOI conferido pelo economista) para a composição;
  - **seleção aninhada por episódio de seca** (2012–2017 como um bloco) para não escolher ruído;
  - **destilação numa árvore rasa** com a fidelidade reportada. É a frase que o técnico repete.
- **Validação:**
  - A carteira de mínimo CVaR, fora da amostra, melhora a cauda em **81% de 131 municípios**: CVaR10/média de 0,327 para 0,406 e P(< 50%) de 0,143 para 0,087 (`economista_portfolio_culturas.py`).
  - A regra única vence a política fina por município: 3,0% contra 6,1% (`agronomo_regras_semeadura.py`).
- **Incerteza:** análise de sensibilidade do ranking (tornado) à água disponível do solo, ao Kc/Ky, ao efeito da leguminosa e ao preço. É o "o que medir primeiro" viável em 36 h; o EVPPI fica para depois.
- **Freio de segurança:** sem restrições, o otimizador de renda bruta dá "100% mandioca" em todos os municípios (`pesquisador_ia_conformal_carteira.py`). É o melhor exemplo, no pitch, de por que a ferramenta apoia e não decide.

### M5. Leitor da prática atual (código de barras leve)

- **Papel:** preencher a estratégia atual, que o desafio exige, sem formulário e fora dos EUA.
- **Método:** suavização de Whittaker e fenométricas (início do verde, pico, colheita, meses com NDVI < 0,25) em MODIS (2000→) e Landsat/HLS; cruzamento com os focos VIIRS e com a queda de NBR; **uma pergunta de aprendizado ativo** ao agricultor.
- **Validação:** onde houver tempo, teste contra o CDL em Iowa ou no Texas e contra o MapBiomas no Ceará.
- **Selo de visibilidade:** fração de anos com ao menos uma cena útil (≥ 60% da área limpa) nos 30 dias antes do portão (`sr_fundacao_r2_checagens.py`, bloco B):

  | Portão | Só HLS | S2 nativo + Landsat |
  |---|---|---|
  | 31/mar | 38% | 71% |
  | 30/abr | 50% | **92%** |
  | Seca | 100% | 100% |

- **Limites:**
  - A data de plantio não é visível, porque a semeadura segue a chuva, quando o óptico está cego. Por isso é **perguntada à família**. Isso quase dobra a fração de quebras que o alerta de veranico pega, de 23% para 43% (`designer_relogio_veranico.py`).
  - O consórcio não se separa a 30 m.
  - Prithvi-EO-2.0, o modelo de fundação NASA/IBM treinado em HLS, é o próximo passo, não o MVP.

### M6. Sentinela de deriva e de qualidade

- **Papel:** rebaixar automaticamente o grau de evidência de qualquer camada que derive.
- **Método:** Mann-Kendall/Sen e CUSUM sobre o resíduo de cada sensor contra uma referência independente, mais bandeiras de qualidade do PAM.
- **O que já pegou:**
  - A **LST diurna do MODIS Terra caiu −4,6 °C** em 2026 contra 2000–2019 por deriva de órbita. A LST noturna não caiu. Usada sem correção, fabricava +58% de safra (`cetico_deriva_lst_terra.py`).
  - O **NDVI está mais verde para a mesma chuva desde 2020** (+0,053), e o NDVI absoluto erra para cima em operação, com viés de +0,60 (`cetico_walkforward.py`).
  - A **mandioca no PAM tem 8% dos anos com rendimento idêntico ao do ano anterior** (relato repetido; `cetico_r2_checagens.py`, bloco D).
  - Uma **anomalia artificial em "2025, ano mais verde"**: o buraco do Terra tirou os meses secos (`ecologo_checagem_ndvi_2025.py`).

### M7. Relógio lento da água e combustível visto do espaço (portões P1 e P5)

- **Banco de água azul.**
  - Método: GRACE menos a umidade do solo do GLDAS Noah, com um reservatório linear de tempo de memória τ ajustado no local.
  - Memória medida no Ceará: cerca de 3 meses no solo e cerca de 48 meses no residual (`hidrologo_grace_residuo_memoria.py`).
  - **Confirmação por outro sensor e outra escala:** a fração de água dos açudes no Landsat a 30 m, de 1984 a 2026, no Sertão Central, tem ρ +0,62 com a chuva de 48 meses, +0,57 com o GRACE da área e +0,54 com o residual. Com a quadra do mesmo ano, só +0,17 (`sr_fundacao_r2_acude_banco.py`).
  - O GWS do GLDAS-2.2 CLSM, que não tem açude, tem memória curta. **O banco azul do sertão é sobretudo açude, que evapora**, e pouco aquífero (`hidrologo_r2_banco_azul_checagens.py`).
- **Área salvável.**
  - O salvamento da floração do milho pede 62 mm na mediana (p90 de 167 mm), ou 620 m³/ha.
  - Uma cisterna-calçadão de 52 m³ salva cerca de 0,08 ha num ano mediano e cerca de 0,03 ha num ano como 2012 (`agronomo_debate_checagens.py`; `hidrologo_fao56_isna_pam.py`).
  - **O salvamento do roçado só existe com barreiro ou açude.** O app pergunta o volume.
- **Índice de combustível.**
  - A anomalia de NDVI de fev–jun do ano t (+0,075 por dp) e do ano t−1 (+0,091 por dp) prevê os focos de out–dez por célula de 0,25° (p < 0,001).
  - Skill fora do ano: +0,072, contra +0,033 da umidade do solo.
  - O combustível explica cerca de **metade da tendência de alta do fogo**: de +3,1%/ano para +1,5%/ano depois de controlado (`ecologo_r2_checagens.py`, bloco D).
- **Incerteza:** o fogo sai em tercis com faixa larga. Para out–dez/2026 os preditores discordam: a chuva diz abaixo da média, e o NDVI diz perto ou acima (`ecologo_r2_fogo_ndvi_2026.py`). O app mostra a discordância.

### M8. Explicador SI com verificador numérico

- **Papel:** redigir os cartões em PT e EN, o áudio e o glossário, e transformar as respostas às perguntas de troca em pesos.
- **Método:** LLM com RAG restrito à revisão de 73 artigos e ao JSON do motor. Um **verificador determinístico** extrai cada número do texto e exige que ele exista no JSON (com tolerância). Se não existir, o texto é bloqueado e cai num modelo de texto fixo.
- **Validação:** teste em que um número inventado é bloqueado, mais checagem de nível de leitura.
- **Incerteza:** o texto carrega o grau A–D e muda o registro de voz. Dado local: "aqui, de cada 10 anos...". Meta-análise global: "a pesquisa de fora diz...".
- **Regra:** o LLM é usado só na inferência. Nenhum modelo é treinado com saídas do Claude.

### Os 5 usos de SI que vão para o slide

1. Emulador físico-ML monotônico em duas escalas (M1 + M2).
2. Conformal robusto ao ano.
3. Busca de política com Pareto pela cauda, destilada em árvore (M4).
4. Previsão por portão com portão de habilidade e valor de decisão (M3).
5. Explicador LLM aterrado com verificador (M8).

M5–M7 aparecem no diagrama de dados.

### O que deliberadamente não usamos, e por quê

| Fica fora | Motivo, com dado |
|---|---|
| Deep learning para prever rendimento no plantio | MSSS de −0,37: sobreajusta com 28 anos. |
| Aprendizado por reforço, NSGA-II | O espaço de jogadas é pequeno; a enumeração é exata e auditável. |
| Downscaling do SMAP a 1 km/70 m | O ganho é temporal; a habilidade espacial é R² 0,083 (`sr_fundacao_r2_checagens.py`). |
| TVDI | R² 0,077 deixando o ano de fora (`sr_fundacao_downscaling_aprendido.py`). |
| NDVI absoluto e LST do Terra pós-2020 | Deriva (M6). |
| Dataset "Crop Recommendation" do Kaggle | Padrão de dado sintético (síntese 90.3). |
| Ajuste fino do Prithvi, SAR→NDVI, EnKF, GNN de pragas, bot real de WhatsApp | Inviáveis em 36 h. Ficam no slide de próximos passos. |

---

## 6. O motor de rotação

### 6.1 Como gera as estratégias

1. **Biblioteca de componentes:**
   - culturas anuais: milho, feijão/caupi, sorgo;
   - semiperenes: mandioca;
   - perenes e forrageiras: palma, guandu, gliricídia;
   - arranjos: consórcio e revezamento;
   - manejo: cobertura e palhada, fogo ou não fogo.
2. **Regras de sucessão que vêm dos dados:**
   - **No sertão não existe safrinha.** O caupi em revezamento cerca de 50 dias após o milho tem P(ISNA floração ≥ 0,5) de 0,89. Semeado junto, 0,75. Em sucessão após a colheita, **0,14**, sem nenhum município viável (`agronomo_isna_zarc_sintetico.py`, bloco A4). A segunda cultura é sempre revezamento ou perene.
   - **Na entressafra não cabe cultura anual sem água.** A ET0 de ago–dez é de 1.224 mm contra 59 mm de chuva (`hidrologo_r2_banco_azul_checagens.py`). A sobra de água na colheita é de 85 mm depois do sorgo, 64 depois do milho, 59 depois do feijão e 4 depois da mandioca (`hidrologo_fao56_isna_pam.py`). Depois da mandioca, só palhada.
   - **Escape hídrico não é quebra de ciclo.** Trocar milho por sorgo mantém a gramínea hospedeira da lagarta-do-cartucho. A quebra exige uma não-gramínea (caupi, mandioca, palma), com o status confirmado pelo técnico (tabela EPPO/CABI).
   - **Algodão** só com destruição de soqueira e vazio sanitário pactuados no município (Azambuja & Degrande 2014).
3. **Restrições duras:**
   - janela do ZARC oficial no Brasil, que condiciona crédito e Proagro;
   - área mínima de cultura da cesta do Garantia-Safra (feijão, milho, arroz, mandioca, algodão). Sorgo e palma não estão nela, e a regra exata ainda precisa ser conferida;
   - semente disponível antes da data-limite;
   - água azul declarada;
   - mão de obra;
   - consumo da família;
   - teto de participação por mercado.
4. **Avaliação:**
   - cada estratégia é reencenada nas 28 quadras do IMERG (1998–2025) e nas 44 do POWER (1981+, para incluir 1983);
   - as rotações de 3 anos são reencenadas em **blocos de anos contíguos** (por exemplo, 2012–2014), carregando o estado da água e do solo. Sortear quadras independentes apagaria a memória de 48 meses.
5. **Escolha:** a atual sempre entra. As outras 3 são pontos distintos da fronteira de Pareto (a mais robusta na cauda, a equilibrada, a construtora de solo), ordenadas pelos pesos da família. Mudar os pesos reordena a lista na hora.
6. **Explicação:** cada cartão traz os 5 campos do desafio, o recibo e as linhas "conta de água", "quem cobre seu risco" e "ciclos".

**Métricas de cada cartão, que cobrem as prioridades do desafio:**
- **Uso de água:** água verde usada, água azul necessária e sobra para a entressafra.
- **Forragem:** kg MS. Literatura, grau B/C.
- **Fixação de N:** como **ganho de rendimento** no cereal seguinte, não como ureia evitada, porque a família típica de sequeiro não aduba (a confirmar no Censo Agro). A razão ureia/milho ao vivo só vale para quem aduba.
- **Erosão:** meses de solo nu × erosividade (I30 do IMERG, até 80 mm/h) × declive (NASADEM).
- **Matéria orgânica:** trajetória de carbono em 10 anos, grau B/C.
- **Mercado:** renda normalizada, teto de participação, PNAE/PAA.
- **Risco:** "pior ano em 10" e "chance de colher menos da metade".
- Também: trabalho e ciclos (meses sem hospedeiro, intervalo entre queimas).

### 6.2 Exemplo concreto: Quixadá (Sertão Central), novembro de 2026

> **Aviso de método:** os números abaixo vêm de análises do conselho com definições de quebra diferentes, indicadas em cada linha. O **bloco 0 do MVP recalcula todos com a definição canônica** (seção 9.7). Os graus seguem o recibo: **A** = validado com dado local observado; **B** = meta-análise global; **C** = modelo ou simulação; **D** = suposição.

**Família de demonstração, fictícia e rotulada como tal na demo:** Dona Francisca, Quixadá, 3 ha (1 ha de baixio pelo SRTM), 8 cabras, cisterna de 16 m³ (água de beber), sem barreiro, semente própria de milho e feijão. Prioridades pelas perguntas de troca: forragem > comida da família > renda.

**Contexto do município (grau A):**
- Milho: 8 quebras em 28 anos; em 2012 colheu 0,17 do normal; em 1998, perda total.
- Feijão: 5 quebras em 28 anos; em 2012, 0,15 do normal (`arquiteto_numeros_canonicos.txt`).
- Datas-limite do ZARC sintético (risco ≤ 30%): **milho até 01/mar, sorgo até 11/mar, caupi até 21/mar** (`agronomo_isna_zarc_sintetico.py`; grau B, porque a ordem foi validada contra o PAM).
- Fogo na área de demonstração de 123 km²: 23% queimou ao menos uma vez desde 2012, e onde houve requeima o intervalo mediano foi de 3 anos (`ecologo_demo_quixada.py`; grau A na escala da paisagem).

#### S0. Atual: "roçado da 1ª chuva"

- **Prática:** milho + feijão consorciados plantados na 1ª chuva de 20 mm ou mais em 3 dias; broca e queima em out–dez; solo nu de setembro a janeiro.
- **Por que aparece:** é a linha de base. O PAM, a fenologia MODIS e os focos VIIRS mostram que é a prática dominante. O agricultor confirma.
- **Evidência:**
  - Milho e feijão quebram juntos (0,78; grau A).
  - No Ceará, 21,5% dos município-anos têm quebra do milho, e 36,5% nos anos de El Niño (grau A).
  - No balde, a perda total (milho e caupi com ISNA < 0,5) acontece em 7,8% dos anos e em 33,8% dos anos secos (`agronomo_regras_semeadura.txt`; grau C).
- **Benefícios:** custo zero, semente própria, mercado conhecido, dentro do ZARC e do Garantia-Safra.
- **Lacunas:** a água disponível do solo do roçado e a data real de plantio.
- **Riscos a confirmar:**
  - Solo nu sob chuva erosiva.
  - Perda de carbono com a queima: −50% em 10 anos segundo Primo et al. 2023, que é simulação Century de um sítio (grau C).
  - Fuga do fogo para os vizinhos.
  - Cerca de 4,5 gerações potenciais de lagarta por safra, sem ano livre de hospedeiro (teto térmico, `ecologo_grausdia_geracoes.py`; grau C).

#### S1. "Escalonar e revezar" (custo zero, só muda o calendário)

- **Prática:**
  - Plantar parte da área na 1ª chuva e o resto quando a chuva firmar (≥ 50 mm em 10 dias, ou já em fevereiro: regra R9).
  - Caupi em **revezamento** cerca de 50 dias após o milho.
  - Troca para caupi ou sorgo se a chuva firme não vier até a data-limite do milho.
- **Por que aparece:** o falso início de janeiro (chuva seguida de veranico) é o risco que o calendário consegue reduzir sem custo. E o revezamento é a única segunda cultura com água.
- **Evidência:**
  - Em Quixadá, o caupi em revezamento tem P de 0,75, contra 0,57 semeado junto e 0,14 em sucessão (grau C, limite superior, porque o balde não modela competição).
  - No balde, a R9 reduz a perda total de 7,8% para 4,3%, com rendimento relativo de 1,012 e CVaR10 de 0,405 contra 0,345 (grau C).
- **O que o cartão diz com honestidade:**
  - O ganho vem de 2010 e 2013, anos em que o balde superestima a perda. Em 2016, quando o balde concorda com o PAM, a fração de municípios com perda total cai de 56% para 22%. Em 2012 não há ganho (`pesquisador_ia_checa_simulador_anos.py`).
  - O efeito do falso início no PAM (OR de cerca de 1,7) **não é significativo** com erro-padrão agrupado por ano: +1,7 pp, EP 2,6 (`cetico_r2_checagens.py`, bloco B).
  - **No El Niño, o falso início não acrescenta risco** (0,365 contra 0,421; `agronomo_debate_checagens.py`).
- **Benefícios:** custo zero; menos risco de perder tudo em ano não El Niño; o caupi dá N e proteína.
- **Lacunas:** o replantio, que o agricultor faz de verdade, não está modelado; a semente de caupi precisa chegar antes de 21/mar.
- **Riscos a confirmar:**
  - Arrependimento num janeiro bom, quando o vizinho que plantou tudo colhe.
  - Ficar fora da janela do ZARC ou do Garantia-Safra.
  - Por isso a mensagem é **"plante escalonado"**, nunca "não plante".

#### S2. "Tampão e forragem" (escudo do ano ruim)

- **Prática:**
  - Cerca de 1/3 da área em mandioca, em faixa, com colheita flexível.
  - Sorgo forrageiro **como primeira cultura** (com rebrota; nunca depois do caupi).
  - Palma adensada consorciada com sorgo no cercado.
  - Caupi precoce de 60–70 dias.
  - O milho fica só no baixio.
- **Por que aparece:** a prioridade de Dona Francisca é forragem, e o risco do sistema atual está na cauda.
- **Evidência:**
  - A carteira com 1/3 milho, 1/3 feijão e 1/3 mandioca leva o CVaR10 de 0,18 para 0,39 da mediana e a P(< 0,5) de 19,8% para 9,2% (2.474 município-anos; `estrategista_portfolio_rotacao.py`; grau A, com preço constante).
  - Em Quixadá, o pior ano vai de 0,10 para 0,35 (`estrategista_demo_quixada.py`).
  - A carteira de mínimo CVaR, fora da amostra, melhora a cauda em 81% de 131 municípios (grau A).
  - Nos 20% de anos mais secos, a produção total de mandioca cai 18,5%, contra 64% do milho (`agronomo_debate_checagens.py`; grau A−, por causa da bandeira de relato repetido da mandioca).
  - Palma + sorgo deu 6.279 contra 4.627 kg MS/ha (Diniz et al. 2017; ensaio com lâminas de irrigação; grau B).
  - O sorgo tem P(ISNA floração < 0,5) de 6,5%, contra 10,1% do milho (grau C).
  - O PAM do sorgo **não** serve de evidência: são 21 municípios tecnificados, com área zero em 2016–2018.
- **Benefícios:** forragem garantida para as cabras no ano seco; comida da família na mandioca; solo coberto mais tempo.
- **Lacunas:**
  - Casa de farinha: a área de mandioca em Quixadá caiu para 0–40 ha em 2012–2024.
  - Mercado e semente de sorgo: o sorgo em grão do Ceará caiu de 2.900 ha em 2021 para 15 ha em 2025 (`economista_debate_checagens.py`).
  - O rendimento da palma não está no PAM.
- **Riscos a confirmar:**
  - Variedade de palma resistente à cochonilha (pergunta obrigatória ao técnico).
  - Sorgo e palma fora da cesta do Garantia-Safra: manter a área mínima de cultura coberta.
  - O sorgo é hospedeiro da lagarta (escape hídrico, não quebra de ciclo).
  - O hedge de preço da mandioca (−0,80) é **estadual**; no município, a elasticidade é cerca de zero, então há teto de mercado.

#### S3. "Leguminosa que fica, sem fogo" (rotação de 3 anos)

- **Prática:**
  - Ano 1: caupi com faixas de guandu ou gliricídia em nível (declive pelo NASADEM), roçagem, palhada, aceiro, sem queima.
  - Ano 2: milho ou sorgo sobre a leguminosa, com caupi em revezamento.
  - Ano 3: mandioca, ou milho + caupi.
  - Na entressafra: só palhada ou perene de raiz funda.
- **Por que aparece:** é a única estratégia que é **rotação no sentido estrito** (o júri vai perguntar). Ataca nitrogênio, erosão, matéria orgânica e o ciclo da lagarta ao mesmo tempo.
- **Evidência:**
  - Leguminosa antecessora: +20% no cereal seguinte, +32% em baixa produtividade (Zhao et al. 2022), com efeito menor na zona árida (Franke et al. 2018). Grau B, faixa larga.
  - Rotação diversa: perdas 14–90% menores em ano seco (Bowles et al. 2020; clima temperado; grau B).
  - Cobertura: +0,56 Mg C/ha/ano (Jian et al. 2020; grau B).
  - Agrofloresta recupera o carbono em cerca de 10 anos, contra −50% com a queima (Primo et al. 2023; grau C).
  - Solo coberto nas chuvas de fevereiro, com I30 de até 80 mm/h (síntese 90.2; grau A).
- **Benefícios:** milho de 2028 em diante sobre solo melhor; banco de proteína para as cabras; menos fogo e menos erosão; meses sem gramínea hospedeira.
- **Lacunas:**
  - **Não existe ensaio revisado de rotação no semiárido do Ceará** (revisão, seção de lacunas).
  - O efeito real da leguminosa é a lacuna que mais muda o ranking (análise de sensibilidade).
  - A água disponível do solo.
- **Riscos a confirmar:**
  - A cobertura compete por água e pode custar cerca de 4% de rendimento (Abdalla et al. 2019).
  - Mão de obra para implantar e 1–2 anos para estabelecer.
  - Se o caupi local é hospedeiro secundário da lagarta.

**Opcional, condicional:** S4, algodão agroecológico consorciado com caupi e milho (Silva et al. 2009, Embrapa Algodão; mais de 1.000 kg/ha em sequeiro). Só aparece se o município tiver pacto de vazio sanitário. Riscos: bicudo e falta de hedge de preço.

### 6.3 O plano vivo de 2027 para Dona Francisca (sobreposto à estratégia escolhida)

| Portão | O que o QUADRA diz | Evidência |
|---|---|---|
| **P1, hoje (14/nov)** | "Em anos com o mar tão quente quanto agora, cerca de 6 em 10 tiveram quadra seca (entre 5 e 7 em 10, com base em 4 a 7 anos parecidos). **Caso inédito:** o mar nunca esteve tão quente nesta época." Ações: comprar semente de caupi precoce e sorgo até dezembro, garantir a palma, manter a adesão ao Garantia-Safra, aceiro e palhada em vez de queima. | Análogos 1966–2024: 4 secos em 7. Condicionado a um El Niño que não decai até FMA: 3 secos em 4 (`clima_r2_checagens.py`). A persistência prevê FMA de cerca de 1,7, então a rota de fuga "o El Niño morre rápido" está quase fechada. A saída possível é o Atlântico, com dipolo de fev–mai ≤ −0,3, como em 1973. O El Niño dobra a quebra além da chuva (OR 2,30). A reserva de água caiu para p35 em setembro. |
| **P2, janeiro** | "Plante escalonado. Neste tipo de ano, o perigo não é o falso início: é o ano inteiro." Peso no revezamento e na carteira. O app vigia TSA − TNA. | No El Niño, o falso início não acrescenta risco (0,365 contra 0,421). O dipolo de out–dez prevê o **quando** (ρ +0,49 com o dia de início; p = 0,008, exploratório entre 12 testes). |
| **P3, 19/mar** | "O que vale não é chover no dia de São José; é quanto choveu até ele." Depois de 01/mar, a troca só cabe para caupi (até 21/mar). | O dia de São José vale AUC 0,53; o acumulado até ele, 0,72 (`estrategista_sao_jose.py`). |
| **P4, 30/abr** | Ação graduada. Primeiro, guardar forragem e segurar a venda dos animais. O milho para as cabras só se o alerta se repetir e o técnico confirmar. Sem salvamento com água: a cisterna de 16 m³ é de beber. | 3,8 contra 1,1 em 10. Quando a chuva para depois de um começo normal (padrão "011"), P(quebra) = 0,74. Mas 45% dos alertas caem em ano normal (`designer_confianca_alertas.py`). **Em 2016 o portão de abril pegou só 4 de 124 quebras** (`estrategista_r2_portao_multimissao.py`). Por isso, em 2027, a proteção vem de P1 e P2. |
| **P5, jul–dez/2027** | Se a quadra for seca, haverá pouco combustível; se vier verde, fenar o excedente. Palhada e perene em nível. | Combustível de t e t−1 visto pelo NDVI (M7). |

---

## 7. O que é inovador, e por que ninguém mais vai ter

1. **Portões postos onde três curvas se cruzam: habilidade, possibilidade e visibilidade.**
   - Ninguém tinha cruzado a habilidade da previsão com o que ainda é agronomicamente possível em cada data e com o que o satélite consegue ver.
   - Em 19/mar, a data-limite do milho já passou em quase todos os municípios (21/fev–11/mar), então o portão só pode trocar para caupi ou sorgo.
   - 30/abr é o primeiro portão em que a habilidade (AUC 0,77) e a visibilidade (92% dos anos com cena útil em 30 dias) são altas ao mesmo tempo, e ali só cabe salvar.
   - O calendário é **derivado dos dados**, não de um manual.
2. **O oceano prevê a quebra, não a chuva: o Atlântico decide o quando e o Pacífico o quanto se perde.**
   - Em novembro, o tercil de chuva não tem habilidade (RPSS −0,01).
   - Mesmo assim, o ONI de ASO explica a anomalia do milho além da chuva: −0,208 por unidade, p = 0,003, n = 44. Isso continua depois de controlar o veranico e a Tmax: −0,115, p = 0,023.
   - O dipolo do Atlântico, e não o ONI, governa o início da estação (ρ +0,49) (`clima_r2_checagens.py`).
   - O portão de novembro passa a ter o **alvo certo**. Ressalva: 12 testes, então é achado exploratório.
3. **Replay no chão, ranking pelo pior ano e honestidade como funcionalidade.**
   - Cada estratégia é reencenada nas quadras que o GPM viu, com conformal robusto ao ano.
   - Cada número traz recibo A–D.
   - Há uma página de auditoria com a inflação da validação aleatória (R² 0,49 contra −0,08), a deriva que pegamos (−4,6 °C na LST do Terra) e onde erramos (2012 invisível até abril; 2016 invisível em abril).
   - Quase nenhuma equipe mostra os próprios erros. Nós transformamos isso em produto.
4. **Dois relógios da água vistos por três sensores e um portão de entressafra.**
   - O solo esquece em cerca de 3 meses; o açude lembra por cerca de 4 anos. O GRACE, o GLDAS e 42 anos de Landsat sobre os açudes mostram isso juntos.
   - O combustível visto pelo NDVI de t−1 prevê o fogo e explica metade da sua tendência.
   - A entressafra, que no sertão é onde de fato se decide a rotação (síntese 90.2), vira um portão com ação: "combustível vira forragem".
5. **Ciência conversando com o saber local.**
   - A "profecia de São José" testada com satélite: o dia não diz nada (AUC 0,53), o acumulado até ele diz (0,72).
   - O portão recebe o nome cultural e lê o dado certo. Os profetas da chuva são tratados como parceiros, e não como alvo de desmentido.

**Por que ninguém mais vai ter:**
- Exige o painel de 184 municípios × 28 anos de rendimento observado, já cruzado com IMERG diário, POWER, GRACE, MODIS e VIIRS.
- Exige as dez análises de validação deste conselho.
- Exige os resultados negativos que nos dizem o que não prometer.
- A maioria das equipes vai entregar um painel de NDVI, um classificador sobre o dataset sintético do Kaggle ou um otimizador do Corn Belt.

---

## 8. Base científica (referências da revisão e o achado que sustenta cada componente)

| Componente | Referência (revisão `pesquisa/artigos_e_datasets.md`) | Achado que sustenta |
|---|---|---|
| Rotação como política, portões | Dury et al. 2012, Agron. Sustain. Dev. 32:567–580 | O plano de cultivo real é dinâmico e adaptativo, mas os modelos o tratam como estático. |
| Pesos do agricultor, multicritério | Sadok et al. 2008, Agron. Sustain. Dev. 28:163–174 | Avaliação ex ante de sistemas com apoio multicritério. |
| Grafo de sucessões, enumeração | Detlefsen & Jensen 2007, Agric. Syst. 94:566 | Rotação como fluxo em rede, otimizável de forma exata. |
| IA de rotação (trabalho mais próximo) | Fenz et al. 2023, Comput. Electron. Agric. 212:108160; Kallenberg et al. 2023, EDS 2 | Planejamento de rotação com IA e RL acoplado a simulador. Nós acrescentamos o tempo da decisão e o risco de cauda. |
| Balde FAO-56 | Allen, Pereira, Raes & Smith 1998, FAO-56 (revisão D14) | ETc = Kc × ET0; Kc, p e estágios por cultura. |
| ZARC como restrição e validação | MAPA/Embrapa, capítulo ZARC (revisão 6.7) | O ISNA e a tábua de risco condicionam crédito e seguro. |
| Veranico e perda de milho e feijão | Rocha et al. 2021, RBMet 36:579–589 | Veranico (≥ 3 d com ≤ 2 mm) explica a perda; milho + feijão = 91% da área. |
| Oceano como probabilidade | Kayano & Andreoli 2006, JGR 111:D13101; Nobre & Shukla 1996, J. Climate 9:2464 | O ENSO sozinho acerta 36%; o gradiente do Atlântico condiciona a ZCIT. |
| Previsão empírica de referência | Rocha Júnior et al. 2021, Water 13:1613 | Modelo empírico simples é competitivo no Nordeste. |
| Caso de estresse e lacuna ex ante | Marengo et al. 2018, An. Acad. Bras. Ciênc. 90:1973; Marengo et al. 2021, Clim. Resil. Sustain. | A seca de 2010–2016; adaptação ainda pós-desastre. |
| Leguminosa antecessora | Zhao et al. 2022, Nat. Commun. 13:4926; Franke et al. 2018, AGEE 261:172 | +20% (+32% em baixa produtividade); efeito menor na zona árida. |
| Resiliência pela diversidade | Bowles et al. 2020, One Earth 2:284; Renwick et al. 2021, ERL 16:084067; Beillouin et al. 2021, GCB 27:4697 | Perdas 14–90% menores em ano seco; a matéria orgânica protege o milho na seca; efeitos positivos mas variáveis, então é preciso mostrar intervalos. |
| Consórcio e forragem | Himmelstein et al. 2016; Souza et al. 2011, Bragantia 70:715; Mudare et al. 2022, ASD 42; Diniz et al. 2017, PAB | Consórcio +23% na África; milho + caupi melhor em Petrolina; LER > 1; palma + sorgo 6.279 contra 4.627 kg MS/ha. |
| Cobertura: benefício e custo | Jian et al. 2020, SBB 143:107735; Abdalla et al. 2019, GCB 25:2530 | +0,56 Mg C/ha/ano; cerca de −4% na cultura principal e custo de água. |
| Fogo, pousio e carbono | Primo et al. 2023, J. Environ. Manage. 336:117594; Salcedo et al. 1997, AGEE 65:177; Cano-Crespo et al. 2015, JGR-B 120:2095 | −50% de C em 10 anos sem pousio; P cai após a queima; fuga do fogo para vizinhos. |
| Combustível da quadra anterior | Argibay et al. 2020, Ecol. Indic. 113:106151; Bezerra et al. 2025, Atmosphere 17:46 | Ano úmido seguido de ano seco gera grandes queimadas. |
| Quebra de ciclo de praga | Ratnadass et al. 2011, ASD; du Plessis et al. 2020, Insects 11:228; Levine et al. 2002, Am. Entomol. 48:94; Azambuja & Degrande 2014, Arq. Inst. Biol. 81:377 | Ruptura temporal de hospedeiro; graus-dia da lagarta; risco de rotações curtas e repetitivas; vazio sanitário do algodão. |
| Satélite térmico e solo raso | Anderson et al. 2016, RSE 174:82; Rossato et al. 2017, Front. Environ. Sci.; Fisher et al. 2020, WRR 56 | O ESI antecipa a quebra em 10–25 dias; a planta responde à camada rasa; ECOSTRESS a 70 m. |
| SMAP L4 | Reichle et al. 2019, JAMES 11:3106 (citado na revisão) | Erro sem viés de 0,026 m³/m³ na zona da raiz. |
| GRACE e reservatórios | Gonçalves et al. 2020, STOTEN 705:135845; Lima et al. 2020, Bol. Ciênc. Geod. 26; Melati et al. 2019 | Depleção no Urucuia; GRACE com r = 0,78 contra o volume dos açudes do Nordeste; GRACE + GLDAS no Araripe. |
| POWER e IMERG no mundo todo | Van Wart et al. 2015, AFM 209–210:49; White et al. 2008, AFM 148:1574; Rozante et al. 2018, Remote Sens. 10:882 | Clima de satélite alimenta modelos de cultura em qualquer lugar; viés da Tmax do POWER; o IMERG subestima o litoral do Nordeste. |
| HLS | Claverie et al. 2018, RSE 219:145 (citado na revisão) | Landsat e Sentinel-2 harmonizados a 30 m. |
| Fenologia e ciclos | Arvor et al. 2011, IJRS 32:7847 | Séries de EVI/NDVI detectam ciclos e sucessões no Brasil. |
| Seca combinada (vegetação + chuva) | Brito et al. 2018, IJC 38:517 | Frequência, duração e severidade da seca no semiárido. |

**Fora da revisão** (DOI conferido no Crossref ou no arXiv por um agente na rodada 1; reconferir antes do slide):

- Rockafellar & Uryasev 2000, Journal of Risk 2(3), doi 10.21314/JOR.2000.038: formulação linear do mínimo CVaR.
- Barber et al. 2021, Ann. Statist. 49:486, doi 10.1214/20-AOS1965: jackknife+, base dos intervalos conformais.
- Roberts et al. 2017, Ecography 40:913, doi 10.1111/ecog.02881: validação cruzada em blocos.
- Bretherton et al. 1999, J. Climate 12:1990: número efetivo de graus de liberdade.
- Lemos et al. 2002, Climatic Change 55:479, doi 10.1023/A:1020785826029: lições da previsão sazonal no Ceará.
- Gigerenzer & Hoffrage 1995, Psychol. Rev. 102:684, doi 10.1037/0033-295X.102.4.684: frequências naturais.
- van Etten et al. 2019, PNAS 116:4194, doi 10.1073/pnas.1813720116: ciência cidadã tricot.
- Szwarcman et al. 2024, arXiv:2412.02732: Prithvi-EO-2.0, só como próximo passo.

---

## 9. Validação honesta e limitações

### 9.1 Protocolo, igual para toda a equipe

- **A unidade independente é o ano**, não o município-ano. Os resíduos se correlacionam por centenas de km: o do milho vai de 0,69 abaixo de 25 km a 0,35 a 300–600 km (`pesquisador_ia_hierarquico.py`).
- Toda métrica sai de uma destas três validações:
  - **deixando o ano inteiro de fora** (LOYO);
  - **walk-forward**, só com o passado;
  - **deixando o episódio de seca de fora**, com 2012–2017 como um bloco.
- Toda escolha de regra, limiar ou análogo é feita por **seleção aninhada**, porque são cerca de 8 episódios independentes de seca em 1981–2026 (`cetico_memoria_grace_neff.py`).
- Toda AUC é decomposta em **entre anos** e **dentro do ano**.
- Os intervalos de confiança vêm de **bootstrap por ano**, e o recibo mostra o n efetivo.
- Toda estratégia de semeadura é avaliada contra o **rendimento observado do PAM**, e não contra o ISNA do próprio balde, para evitar circularidade.

### 9.2 Números de cabeçalho, os únicos que vão para os slides

| # | Afirmação | Valor | Validação | Fonte |
|---|---|---|---|---|
| 1 | Milho e feijão quebram juntos | ρ mediano 0,78 (183 municípios) | Descritivo, PAM 1998–2025 | `arquiteto_numeros_canonicos.txt` |
| 2 | A habilidade cresce na quadra | AUC 0,52 (31/jan) → 0,77 (30/abr; IC90 0,69–0,82) | LOYO + bootstrap por ano | `designer_curva_pct_normal.py`; `cetico_r2_checagens.py` |
| 3 | O modelo físico pequeno vence o livre | AUC 0,794 contra 0,727 | LOYO | `hidrologo_hibrido_fisica_ml.py` |
| 4 | Emulador em duas escalas | R² 0,365; AUC 0,851; viés walk-forward +0,01 | LOYO + walk-forward | `pesquisador_ia_fusao_fisica_satelite.py` |
| 5 | A validação aleatória infla | R² 0,49 contra −0,08 | Aleatório contra LOYO | `cetico_escala_vazamento.py` |
| 6 | A diversificação protege a cauda | Melhora em 81% de 131 municípios | Fora da amostra por blocos | `economista_portfolio_culturas.py` |
| 7 | O conformal robusto cobre os anos ruins | 77–86% dos anos, contra 46–68% | Por ano | `pesquisador_ia_conformal_carteira.py` |
| 8 | São José | O dia vale AUC 0,53; o acumulado, 0,72 | Por município-ano e estadual | `estrategista_sao_jose.py` |

### 9.3 Onde erramos, e mostramos

- **2012:** invisível até abril. Em 28/fev, nenhum alerta; em 30/abr, 33 alertas com 31 acertos (`estrategista_alerta_municipal.py`).
- **2016:** foi um falso início do tipo "janeiro enganador": janeiro com 205% do normal e fevereiro com 37% (`designer_caso_2016.py`). O portão de abril pegou **4 de 124** quebras.
- **2024:** El Niño sem seca, com o Atlântico inteiro recorde de quente. O alerta de fevereiro foi falso e se corrigiu em abril.
- **O balde** superestima 2010 e 2013 e não vê 1998 nem 2001.
- **Alarmes falsos:**
  - em 30/abr, 45% dos alertas caem em ano normal;
  - em 28/fev, 63%, e por isso **fevereiro não tem alarme de chuva**;
  - em 3 anos de uso, 60% das famílias não recebem nenhum alerta (`designer_confianca_alertas.py`). Por isso o calendário fixo de 5 conversas tem conteúdo mesmo em ano quieto.
- **Anos de excesso** (2009 e 2024): os municípios mais chuvosos quebraram mais. O balde não modela encharcamento.

### 9.4 Grau de evidência por tipo de afirmação

| Grau | O que é | Exemplos |
|---|---|---|
| A | Validado com dado local observado, por ano | Correlação entre culturas, curva de habilidade, carteira fora da amostra, El Niño × quebra |
| B | Meta-análise global ou ordem validada | Efeito da leguminosa, carbono da cobertura, datas-limite do ZARC sintético |
| C | Simulação ou modelo | Perda total no balde, revezamento, sorgo, gerações de praga, carbono de Primo 2023 |
| D | Suposição | Rendimento potencial suposto, volume da cisterna, preço de forragem |

### 9.5 Limitações

1. **Nenhum efeito de rotação foi observado no Ceará.** O PAM valida o efeito do clima sobre cada cultura, não o do antecessor. Nenhum cartão pode dizer "a rotação X rende Y% a mais no seu município".
2. **Falácia ecológica.** Tudo foi calibrado no município (o PAM é estimado pelo IBGE e pela Ematerce), e a decisão é do roçado de 1–5 ha. A camada do talhão é relativa e experimental.
3. **2027 está fora da distribuição** (ONI ASO 2,46 contra o máximo de 2,04). Toda probabilidade é extrapolação, com n de 4 a 7 análogos.
4. **Definições que mudam o tamanho da quebra.** Os resultados variam com o método da tendência: a fração de municípios em quebra em 2012 vai de 50% a 75% conforme o método. Daí a definição canônica única (9.7).
5. **A área plantada se adapta ou é registrada depois da safra.** Seu ρ com o ONI de NDJ é de −0,43 no milho e −0,52 no feijão (`cetico_r2_checagens.py`, bloco C). A linha de base do replay não pode ser congelada.
6. **Qualidade do PAM por cultura.** A mandioca tem relato repetido e ciclo de 12–24 meses. O feijão mistura Phaseolus e caupi. O sorgo é tecnificado e tem n pequeno.
7. **Escala da água azul.** A família típica de sequeiro não tem água para o salvamento do roçado.
8. **Sem custo de produção.** A renda é normalizada e bruta. Os custos são campos editáveis pelo técnico.
9. **Regras institucionais a conferir:** o limiar do Garantia-Safra (40% pela Lei 15.236/2025, segundo o economista; 50% na Lei 10.420/2002, segundo o designer), a cesta e a área mínima, a janela do ZARC de Quixadá e o calendário de distribuição de sementes.
10. **Muitos testes sobre os mesmos 28–44 anos.** Achados como o do dipolo × início e o do fogo × rendimento seguinte são exploratórios. Os 8 números da tabela 9.2 são os únicos de cabeçalho.

### 9.6 Testes que dão para fazer antes do júri

- **Pré-registro com hash** (publicado hoje) da afirmação de novembro para a quadra de 2027: faixa de P(seca) e lista de análogos. É falsificável em maio.
- **LSPA mensal do IBGE (2026):** teste fora da amostra no nível estadual sem esperar o PAM de 2027.
- **FIRMS NRT de out–nov/2026:** desempata a discordância chuva × NDVI no fogo. Exige chave MAP_KEY.
- **Teste global:** o código de barras contra o CDL num condado do Texas.

### 9.7 Folha de números canônicos e erratas (obrigatória antes do deck)

**Números canônicos** (`arquiteto_numeros_canonicos.py`):

| Item | Valor canônico | Não usar |
|---|---|---|
| ONI | **ASO/2026 = +2,46**; recorde para ago–out (antes 2,04 em 1997); recorde absoluto 2,59 em NDJ 2015 | "2,14 (jul–set)" e "2,31 (ago–set)", que são médias de médias móveis; "o El Niño mais forte da história" |
| GRACE CE (dessazonalizado) | jul +3,76 (p72) → ago +2,49 (p68) → **set −3,30 cm (p35)**; média de jul–set +0,99 (p57) | "banco bom, p72" |
| Ureia/milho (Pink Sheet) | **1,85 em out/2026**; pico de 4,00 em abr/2026; média de 2000–2020 = 1,51 (`cetico_r2_ureia.py`) | "4,0 agora" |
| Chuva e ET0 do CE (POWER, 1991–2020) | 809 e **2.279** mm/ano | ET0 "~1.960" (síntese 90.2, a corrigir) |
| Quebra | rendimento por área plantada < 50% da mediana do município nos outros anos; milho 21,5% e feijão 14,6% dos município-anos (1998–2025) | Médias móveis de 7 anos (escondem a seca plurianual) e o limiar de < 60% |
| Milho em 2012 | −69% no estado; 75% dos municípios em quebra | "71%", "50%" (outras definições) |

**Erratas da síntese e das propostas:**
- O ρ −0,67 do "início da estação" é retrospectivo e mecânico. O início causal tem ρ ≈ 0 com a chuva restante. **Sai a regra de fevereiro.**
- "2025, o ano mais verde" é artefato do MODIS Terra.
- "Fogo cerca de 6 meses depois de anos verdes" está errado: o sinal forte é a quadra do ano anterior.
- As elasticidades com mediana móvel curta estão subestimadas: o milho é +13,8%/100 mm, e não +10% (`pesquisador_ia_hierarquico.py`, argumento 14).
- A LST do Terra pós-2020 tem deriva.

---

## 10. Plano de MVP para as próximas ~38 h

**Hipótese de equipe:** 3 a 4 pessoas. A **definir com a equipe**. Com 2 pessoas, juntar P1+P3 e P2+P4.

**Papéis:**
- **P1, Motor:** dados, Python, JSON.
- **P2, App:** página estática HTML + JS + Leaflet + Plotly.
- **P3, Ciência e recibo:** números canônicos, validação, auditoria, texto de SI.
- **P4, Narrativa:** slides, vídeo de 30 s, roteiro e voz.

**Arquitetura do MVP:** tudo **pré-calculado** em um JSON por município (184) e por ponto global (Sahel e Texas). A página é estática, sem servidor, e **não chama APIs ao vivo durante a demo**.

| Bloco | Quando | Quem | Tarefa | Pronto quando |
|---|---|---|---|---|
| 0 | Sáb 09–11h | Todos | Congelar a folha de números (9.7), a definição de quebra, os 5 portões e o esquema do JSON (portões, estratégias, recibos). Escolher o nome. | Esquema escrito; ninguém usa número fora da folha. |
| 1 | Sáb 11–19h | P1 | Empacotar em `motor/` os scripts que já existem: `agronomo_isna_zarc_sintetico.py`, `agronomo_regras_semeadura.py`, `hidrologo_fao56_isna_pam.py`, `hidrologo_hibrido_fisica_ml.py`, `pesquisador_ia_fusao_fisica_satelite.py`, `pesquisador_ia_conformal_carteira.py`, `economista_portfolio_culturas.py`, `designer_curva_pct_normal.py` e `clima_previsao_progressiva.py`. Gerar por município: datas-limite, curva de habilidade por portão, replay de S0–S3 (mediana, P10, P(< 50%), pior ano em 10) e valores de 1998, 2012 e 2016. | JSON de Quixadá bate com as saídas dos scripts; os 184 rodam em menos de 10 min. |
| 2 | Sáb 11–19h | P3 | Recalcular os cartões com a definição canônica. Gerar os recibos (fonte, escala, validação, n, grau). Montar a página de auditoria (aleatório × LOYO, deriva da LST, curva, onde erramos). Escrever o texto "Como usamos SI". | Todo número do JSON tem recibo. |
| 3 | Sáb 13h – Dom 02h | P2 | Telas: Meu chão (mapa + código de barras pré-calculado das 4 AOIs), Relógio da Quadra, Cartões, Replay animado de 2012, 2027 ao vivo, Auditoria. Glossário em pop-up. | Quixadá, Tauá e Iguatu carregam em menos de 2 s no celular. |
| 4 | Sáb 19–24h | P1 | Painel 2027: ONI, análogos, GRACE em 3 meses, açude pelo Landsat, IMERG Late. Índice de combustível de out–dez/2026. | Números iguais aos da folha. |
| 5 | Dom 00–06h | P1 + P3 | Explicador: textos dos cartões gerados a partir do JSON (PT e EN) por LLM, com o verificador numérico, e salvos como estáticos. Áudio TTS de 45 s para o cartão da Dona Francisca. Teste: um número inventado é bloqueado. | Zero números fora do JSON. |
| 6 | Dom 08–12h | P1 | Modo global: rodar offline o ZARC sintético e o replay pela API do POWER (IMERG_PRECTOT + ET0) em 2 pontos (Sahel e Texas). Mapa dos meses sem quebra térmica (`ecologo_grausdia_global_2020.csv`). | 2 pontos globais carregam no app. |
| 7 | Dom 08–18h | P4 (+P3) | 7 slides em inglês, roteiro e gravação do vídeo de 30 s, simulador de conversa no estilo WhatsApp (maquete). | Vídeo gravado até dom 18h. |
| 8 | Dom 18–21h | Todos | Ensaio, checagem cruzada de números (slides contra folha contra app) e publicação do app. | Nenhuma divergência. |
| 9 | Dom 21–23:59 | Todos | Folga e submissão. | Submetido antes das 23h. |

**O que cortar se faltar tempo, nesta ordem:**
1. Modo global ao vivo: fica 1 ponto pré-calculado.
2. Índice de combustível e painel de fogo: viram uma linha no cartão S0.
3. Áudio TTS: fica só o cartão em imagem.
4. S3 simulado em blocos plurianuais: S3 entra só com os priors da literatura (grau B).
5. Código de barras: fica a estratégia atual pela PAM mais uma pergunta.

**Nunca cortar:** replay de 2012, os 4 cartões com recibo, a curva de habilidade, a página "onde erramos" e o verificador numérico.

**Fora do MVP, no slide de próximos passos:** Prithvi-EO-2.0, Sentinel-1/NISAR para datar o plantio sob nuvem, assimilação do SMAP L4 no balde, ECOSTRESS como gatilho, bot real de WhatsApp, rede de pluviômetros, veredito tricot com Plackett–Luce, EVPPI e GEOS-S2S.

---

## 11. Roteiro da demo

### 11.1 Os 7 slides (em inglês)

1. **"Will it rain until São José's day?"**
   - Abertura cultural: no sertão, a tradição diz que, se chover em 19/mar, o inverno está garantido.
   - Testamos com 28 anos de GPM: o dia não diz nada (AUC 0,53); a chuva acumulada até ele diz (0,72).
   - "Science and local knowledge, talking."
2. **"One window, one chance."**
   - Mapa do Ceará em 2012: 75% dos municípios perderam mais da metade do milho; −69% no estado.
   - Milho e feijão quebram juntos (0,78).
   - O mesmo problema no Sahel, na Índia e no Texas.
3. **"In January, nobody knows. So QUADRA decides at checkpoints."**
   - A curva de habilidade (0,52 → 0,77) sobre o calendário, com as datas-limite e o selo de visibilidade.
   - Os 5 portões.
4. **Momento uau: "Replay 2012 on your land."**
   - A chuva IMERG de Quixadá anima dia a dia.
   - Os 4 cartões divergem.
   - O alerta acende em 30/abr.
   - "In the worst year, the buffered plan kept about 3× more of the harvest" (0,35 contra 0,10; `estrategista_demo_quixada.py`; recalcular com a definição canônica antes).
   - Clique no recibo de um número.
5. **"NASA at the core."** Diagrama missão → decisão:
   - IMERG: quando plantar e trocar;
   - POWER: demanda de água e calor;
   - SMAP: solo;
   - GRACE e Landsat: os açudes e a água guardada;
   - MODIS/VIIRS/HLS: prática e fogo;
   - SRTM: baixio e erosão;
   - NEX-GDDP: 2050.
   - Os dois relógios da água.
6. **"How we used SI, and where we fail."**
   - "Small physics-guided models beat big ones" (0,794 contra 0,727).
   - "Random validation lies" (0,49 contra −0,08).
   - "We caught a satellite drifting 4.6 °C."
   - 2012 invisível até abril; 2016 invisível em abril.
   - "What we did not do."
7. **"Today: strongest Aug–Oct El Niño on record. Anywhere on Earth."**
   - O plano de 2027 da Dona Francisca (fictícia).
   - Clique no Sahel ou no Texas.
   - "NASA evidence. The farmer decides."

### 11.2 Vídeo de 30 s (em inglês, com legenda; áudio do cartão em português ao fundo)

| Tempo | Imagem | Locução |
|---|---|---|
| 0–4 s | Mapa do Ceará em 2012 escurecendo | "2012. Three in four municipalities in Ceará lost over half their corn." |
| 4–9 s | Matriz milho × feijão, as duas barras caindo juntas | "Corn and beans fail together. In January, nobody can tell the season." |
| 9–19 s | **Replay 2012:** a chuva IMERG anima, os 4 cartões divergem, o alerta acende em 30/abr | "QUADRA replays every rainy season NASA has seen, on your land, and ranks rotations by their worst year." |
| 19–25 s | Mostrador do ONI em +2,46; o Relógio da Quadra com P1 aceso; o cartão em imagem com áudio em português | "Today the Pacific shows its strongest August–October El Niño on record. QUADRA tells you what to do now, and when to decide." |
| 25–30 s | Selos IMERG, POWER, SMAP, GRACE, Landsat e VIIRS; o técnico aprova | "NASA evidence. The farmer decides." |

**Momento uau:** os quatro cartões se separando no replay de 2012 enquanto a chuva real do satélite cai sobre Quixadá, e o portão de 30/abr acendendo na data em que teria acendido. Em seguida, o corte para "today", com o recorde do El Niño.

**Cuidados:**
- A família é **fictícia** e rotulada.
- Não usar logomarca da FUNCEME, da Ematerce ou da NASA que sugira endosso. Os selos dizem "dados de", não "parceria".
- O simulador de WhatsApp é rotulado como maquete.

---

## 12. Mapa de prêmios-alvo e critérios de julgamento

### 12.1 Prêmios

| Prêmio | Prioridade | O que o sustenta |
|---|---|---|
| **Best Use of Science** | 1ª | Modelos físicos validados por ano contra 5 mil município-anos; o oceano prevê a quebra e não a chuva; o dipolo governa o início; os dois relógios da água confirmados por três sensores; resultados negativos declarados. |
| **Best Storytelling** | 2ª | São José testado; replay de 2012; 2027 ao vivo; Dona Francisca; "where we fail". |
| **Local Impact** | 3ª | Ceará, 184 municípios, ZARC, Garantia-Safra, extensionista no circuito, linguagem e frequências naturais. |
| **Best Use of Data** | 4ª | Mais de dez bases NASA, cada uma numa decisão; o sentinela de deriva que pegou a LST do Terra; 42 anos de açudes no Landsat; o NDVI que arbitra a discordância POWER × IMERG. |
| **Galactic Impact** | Indicação | Núcleo global; ZARC sintético em qualquer ponto; mapa de "onde o inverno não quebra o ciclo" (86% dos trópicos). |
| Best Use of Technology | Não é alvo | O app estático é simples por escolha. Se for avaliado, o argumento é o verificador numérico e o conformal robusto ao ano. |

### 12.2 Critérios (notas de 1 a 5)

| Critério | Como atendemos | Risco e mitigação |
|---|---|---|
| **Impacto** | Decisão real de uma família em data real (2027); métrica do ano ruim; pilha de risco com o Garantia-Safra; canal pelo extensionista; escala global. | Pode parecer ferramenta de técnico. Mitigação: o cartão em áudio e a Dona Francisca no vídeo. |
| **Criatividade** | Rotação como política; portões pelo cruzamento de habilidade, possibilidade e visibilidade; São José; entressafra como portão; honestidade como funcionalidade. | A banca pode não reconhecer "rotação" sem sequência milho–soja. Mitigação: a frase "in a one-window climate, rotation happens inside the season (intercrop, relay) and across years (legume, perennial, fallow without fire)" e a estratégia S3 de 3 anos. |
| **Validade** | Validação por ano, walk-forward e por episódio; 8 números de cabeçalho; recibo A–D; auditoria; onde erramos; folha de números única. | Números divergentes entre slides derrubam a nota. Mitigação: bloco 0 e bloco 8 do MVP. |
| **Relevância (NASA no núcleo)** | O replay é IMERG; o balde é POWER + SMAP; a memória é GRACE + Landsat; a prática é MODIS/HLS + VIIRS; o relevo é SRTM; o futuro é NEX-GDDP. Selos visíveis em cada número. | O oceano (ONI) é NOAA. Mitigação: dizer que ele só inclina os cenários e que a decisão é calculada com dados NASA. |
| **Apresentação** | 7 slides com um gancho por slide; vídeo de 30 s com o momento uau; inglês; no máximo 3 números por cartão. | Excesso de conteúdo. Mitigação: uma espinha (o relógio) e uma tela (o cartão); o resto vai para a página de auditoria. |

### 12.3 Texto curto "How we used SI" (rascunho para a submissão)

> QUADRA uses SI in five places:
>
> 1. A physics-guided, monotonic yield-risk emulator (FAO-56 water balance plus gradient boosting) calibrated on 28 years × 184 municipalities and validated leaving whole years out.
> 2. Year-robust conformal prediction for honest intervals.
> 3. Checkpoint-specific calibrated forecasts that are only shown where they have proven skill.
> 4. An exact multi-objective search that ranks rotation strategies by their worst year and distils them into a short decision tree.
> 5. A large language model that only writes explanations from the engine's numbers, with a deterministic checker that blocks any number not computed by the engine.
>
> No model was trained on LLM outputs. Every number shown carries its NASA source, scale, validation and evidence grade.

---

## Anexo A. Decisões em aberto para a equipe (exigem pessoa, não agente)

1. Nome final: QUADRA, ou a reserva Field Replay.
2. Tamanho da equipe e divisão dos papéis P1–P4.
3. Conferir no Planalto o limiar e a cesta do Garantia-Safra e a regra de área mínima.
4. Conferir a janela do ZARC oficial de Quixadá para milho, caupi e sorgo.
5. Chave do FIRMS NRT, se quiser o slide de validação ao vivo do fogo.
6. Publicar ou não o hash do pré-registro de 2027 hoje.
7. Confirmar se as datas e fatos do "Encontro dos Profetas da Chuva" de Quixadá podem ser citados.
