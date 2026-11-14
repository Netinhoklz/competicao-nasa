# QUADRA: proposta final (NASA Space Apps 2026, desafio "Field Shift")

- **Versão:** final, sábado 14/11/2026, 09:25 (hora local, pelo `date`). Prazo de submissão: domingo 15/11/2026, 23:59.
- **De onde vem:** o `rascunho_v1.md`, revisado com os três pareceres da banca adversária (juiz da Space Apps, cético científico e engenheiro de viabilidade). A seção 13 registra cada crítica e o que foi feito com ela.
- **Regra de honestidade:** todo número tem arquivo de origem. As referências vêm da revisão `pesquisa/artigos_e_datasets.md`; as que estão fora dela têm a marca "fora da revisão" e precisam ser reconferidas antes de entrar num slide.
- **Números novos desta versão** (rodados pelo arquiteto, só leitura, em `conselho/analises/`):
  - `arquiteto_final_curvas_quixada.py` → `.saida.txt`: curva de habilidade canônica com e sem o oceano, regra única de alerta, curva de possibilidade, replay de Quixadá ano a ano, ET0 × chuva por mês e pontos globais;
  - `arquiteto_final_carteira_ic.py` → `.saida.txt`: IC90 por bootstrap de anos da carteira na definição canônica;
  - `arquiteto_final_zarc_et0_sensibilidade.py` → `.saida.txt`: datas-limite do ZARC sintético com a ET0 do POWER e com a ET0 na escala do ERA5.
- **Checagens da banca usadas aqui:** `juiz_carteira_definicao_canonica.py`, `juiz_replay_quixada_alerta.py`, `cetico_r3_refutacoes.saida.txt`, `cetico_r3_sao_jose_mandioca.saida.txt` e os três scripts `viabilidade_*.py`.

---

## 0. Resumo executivo

- **O que é:** o QUADRA trata a rotação no semiárido como uma **política com cinco portões de decisão ao longo do ano**, e não como uma sequência fixa de culturas. Cada estratégia é planejada em **3 anos (2027–2029)**, incluindo o que fica no solo na entressafra.
- **Onde ficam os portões:** onde três curvas medidas se cruzam (seção 7, inovação 1):
  - **habilidade:** o que os dados já sabem naquela data, medido deixando o ano inteiro de fora;
  - **opções:** o que ainda dá para plantar (datas-limite);
  - **visibilidade:** quando o satélite consegue ver.
- **A imagem central:** a chuva acumulada da NASA (IMERG) diz quase nada em janeiro (AUC 0,57) e chega a 0,80 em 30/abr. O oceano, conhecido desde novembro, diz um pouco (0,67). As duas linhas se cruzam no fim de fevereiro. Em 19 de março, o milho já não cabe em 58% dos municípios, mas o caupi ainda cabe em 98%. Esse é o último portão de troca.
- **Como compara:** a estratégia atual e três alternativas são **reencenadas nas 28 quadras do registro IMERG (eras TRMM e GPM, 1998–2025)** no município do agricultor. O ranking é pelo **pior ano**, não pela média.
- **Quem arbitra:** o rendimento observado do IBGE (PAM). A NASA é o motor; o IBGE é o juiz.
- **O recibo:** cada número traz a missão de origem, a escala, a validação e um grau de evidência de A a D.
- **A escala, dita sem exagero:** o dado acerta o **nível do ano na região**. Entre municípios no mesmo ano, a habilidade é fraca (AUC ≤ 0,57). Por isso a tela diz "seu município / sua região", e a decisão no roçado fecha com a família e o técnico.
- **A SI:** modelos pequenos, guiados pela física, validados por ano e comparados só com linhas de base pareadas. Um LLM **só redige** textos, offline, travado por um verificador de números.
- **Por que agora:** o Pacífico está no **El Niño mais forte já medido para ago–out** (ONI ASO/2026 = +2,46; o recorde anterior era 2,04, em 1997). A demo é o plano de 2027 de uma família fictícia de Quixadá (CE).

---

## 1. Nome e frase de efeito

**Nome:** **QUADRA**. Na primeira menção do deck e do vídeo: *"QUADRA: the sertão's word for the rainy season"* (fevereiro a maio). Subtítulo: *Field Playbook*. Nome reserva: *Field Replay*.

**Por que não "PROFETA":** o próprio estrategista retirou o nome. Ele promete certeza, que é o que os dados negam, e arrisca soar como apropriação dos profetas da chuva. Eles entram no produto com respeito, no "Checkpoint São José".

**Frase de efeito (PT):**
> "Em janeiro, a chuva que já caiu não diz quase nada, e o oceano diz pouco. O QUADRA reencena no seu município todas as quadras que a NASA registrou, mostra como cada rotação aguentaria o pior ano e marca os dias em que o dado já sabe o bastante e ainda dá tempo de mudar."

**Frase de efeito (EN, pitch):**
> "In January, rain-to-date says almost nothing and the ocean says a little. QUADRA replays every rainy season NASA has recorded over your county, ranks rotations by their worst year, and marks the checkpoints where the data know enough and there is still time to switch."

**Tagline (EN):** *Replay every rainy season NASA has recorded over your county. Decide at the right checkpoint.*

**De onde vem cada peça** (placar consolidado do conselho: média dos 9 avaliadores externos; ver `ata_do_conselho.md`):

| Peça | Origem | Por que entra |
|---|---|---|
| Rotação como política com portões | Agrônomo, "Playbook do Roçado" (8,4) | Esqueleto mais votado. Seis propostas chegaram a ele de forma independente. |
| Replay das quadras observadas, ranking pela cauda | Pesquisador de IA, "SeasonReplay" (8,3) | Torna a comparação concreta: "o que teria acontecido em 1998 no seu município". |
| Recibo A–D, auditoria, sentinela de deriva, duas escalas | Cético, "FieldProof" (8,3) | É a espinha do critério Validade. |
| Calendário, São José, 2027 ao vivo | Estrategista, "PROFETA" (8,1) | Leitura do júri e eixo do storytelling. |
| Oceano como camada própria, aviso de caso inédito | Clima, "ShiftCast" (7,9) | Diz o que o mar informa em novembro e o que não informa. |
| Pior ano, correlação entre culturas, carteira | Economista, "CropFolio" (7,9) | É a métrica que importa para a família. |
| Frequências naturais, técnico no circuito, data de plantio | Designer, "Compadre" (7,5) | Resolve a adoção. |
| Dois relógios da água, salvamento contra irrigação na seca | Hidrólogo, "Extrato d'Água" (7,4) | Linha "conta de água" e relógio lento. |
| Selo de visibilidade | Sensoriamento remoto, "FieldMemory" (6,2) | Terceira curva: quando o satélite enxerga. |
| Portão de entressafra (fogo, palhada, ciclo de praga) | Ecólogo, "CycleBreak" (6,1) | Preenche o portão que as outras propostas deixaram vazio. |

---

## 2. O problema

### 2.1 No Ceará, com os nossos dados

1. **Uma janela, uma chance.**
   - 77,5% do Ceará comporta uma única safra de sequeiro (GAEZ; `notebooks/secoes/90_sintese.py`, 90.2).
   - A estação vai de cerca de 2/fev a 28/jul, com pico em abril. O solo fica exposto de setembro a janeiro (MODIS; mesma seção).
   - A evapotranspiração de referência supera a chuva em **10 de 12 meses**, tanto no POWER quanto no ERA5 (`arquiteto_final_curvas_quixada.saida.txt`, bloco D). No ano, a ET0 vai de 1.970 mm (ERA5) a 2.280 mm (POWER), ou 2,5 a 2,8 vezes a chuva da mesma fonte.
2. **O sistema dominante concentra o risco.**
   - Milho e feijão ocupam 91% da área (Rocha et al. 2021).
   - No registro do PAM, as duas culturas quebram juntas. A correlação mediana das anomalias no mesmo município é **0,78** (183 municípios, 1998–2025). Tirando o choque comum do estado no ano, ainda é 0,67 (`cetico_r3_refutacoes.saida.txt`, bloco F).
   - Ressalva: parte do co-movimento pode ser o mesmo relato municipal. Em Quixadá, o feijão de 2005 é cópia exata do de 2003.
3. **A quebra é frequente e sincronizada.**
   - **Definição canônica de quebra:** produção ÷ área plantada abaixo de 50% da mediana do próprio município nos *outros* anos.
   - O milho quebrou em **21,5%** dos 5.106 município-anos de 1998–2025.
   - Fração de municípios em quebra: 75% em 1998 e em 2012, 70% em 2016 e 61% em 2010. O rendimento estadual do milho caiu 69% em 2012 (`arquiteto_numeros_canonicos.txt`, bloco D).
   - Cerca de metade da variância da quebra municipal é choque comum ao estado no ano: 45–53% no milho (`cetico_escala_vazamento.py`).
4. **O El Niño pesa, mas não decide sozinho.**
   - Dos 6 El Niños desde 1998 (ONI de NDJ ≥ 1,0), **3 viraram catástrofe**: 1998, 2010 e 2016, com 61% a 75% dos municípios em quebra. **Três passaram sem quebra**: 2003, 2019 e 2024, com 1% a 8% (`cetico_r3_refutacoes.saida.txt`, bloco A).
   - Dos 4 El Niños fortes desde 1982 (ONI de out–jan ≥ 1,5), 3 trouxeram quadra seca: 1983, 1998 e 2016. Em 2024, com o Atlântico recorde de quente, não (`cetico_memoria_grace_neff.saida.txt`).
   - Com erro-padrão agrupado por ano, o efeito do El Niño "além da chuva" **não é significativo**: OR 1,57, IC95 0,71–3,50 (mesmo arquivo, bloco A). Grau B.
5. **O solo fica nu e queima.**
   - 72% dos focos de fogo caem em out–dez (VIIRS; síntese 90.2).
   - 17% da área do Ceará está em células de ~375 m com ao menos um foco VIIRS em 2012–2025. Isso não é área queimada: um roçado de 1 ha acende uma célula de 14 ha.
   - A medida de área é o MapBiomas Fogo a 30 m: 12,7% da Caatinga queimou entre 1985 e 2023 (Franca Rocha et al. 2024).
6. **Em janeiro, a chuva que já caiu não diz quase nada.**
   - A chuva IMERG acumulada até 31/jan separa a quebra do milho com AUC de apenas 0,57 (IC90 0,43–0,68). Ela pode até enganar: em Quixadá, janeiro de 1998 teve 150% do normal e janeiro de 2016 teve 197%. Os dois anos foram de quebra.
   - O oceano diz um pouco: o ONI de ASO, publicado no início de novembro, tem AUC de 0,67 (IC90 0,53–0,78) para a quebra municipal. Dentro do ano, a AUC é 0,50 por construção, porque o sinal é regional (`arquiteto_final_curvas_quixada.saida.txt`, bloco A).
   - A habilidade da chuva cresce durante a quadra: 0,73 em 19/mar e 0,80 em 30/abr.

### 2.2 Por que as ferramentas atuais não resolvem

- O **ZARC** dá a janela de plantio de uma cultura, mas a janela não muda com o ano.
- O **prognóstico de tercis** não vira decisão de rotação.
- **Painéis de NDVI** mostram o passado e não comparam estratégias.
- Marengo et al. (2021) mostram que a adaptação à seca no Nordeste ainda é quase toda **pós-desastre**.
- Dury et al. (2012) mostram que o plano de cultivo real é dinâmico e adaptativo, mas os modelos o tratam como estático.
- No Ceará, previsões comunicadas como certeza já custaram a confiança dos agricultores (Lemos et al. 2002, fora da revisão; DOI conferido no Crossref na rodada 1).

### 2.3 Por que agora

- O **ONI ASO/2026 é +2,46**, o maior valor para ago–out desde 1950. Os anteriores foram 2,04 (1997) e 2,02 (2015). Não é o recorde absoluto: o maior ONI de qualquer trimestre foi 2,59, em NDJ 2015 (`arquiteto_numeros_canonicos.txt`, bloco A).
- **O ano de 2027 está fora da distribuição.** Nenhum dos anos de treino teve o mar tão quente nesta época.
- O banco regional de água está **normal**. O GRACE do Ceará, dessazonalizado, tem média de jul–set/2026 no percentil 57. A queda de agosto para setembro (−5,79 cm) está dentro do ruído mês a mês (z = −1,2) e já houve queda maior, de −7,30 cm em 2022 (`cetico_r3_refutacoes.saida.txt`, bloco E).

### 2.4 Por que importa no mundo

- O problema "uma janela de chuva, falso início e data-limite" é o mesmo no Sahel, no Chifre da África, na Índia de sequeiro e no semiárido do Texas. No Texas, o CDL mostra 67% de algodão contínuo (síntese 90.2, item 11).
- Na amostra global do POWER (2020), **40 dos 47 pontos terrestres tropicais amostrados** não têm nenhum mês em que o frio interrompa o ciclo da lagarta-do-cartucho, contra 7 meses em Iowa (`arquiteto_final_curvas_quixada.saida.txt`, bloco E). Onde não há inverno, só a rotação e a entressafra quebram o ciclo.
- O núcleo de dados do QUADRA é global: IMERG, POWER, SMAP, GRACE, HLS, VIIRS, SRTM e NEX-GDDP (síntese 90.1).

---

## 3. A solução: o que o técnico e a família veem e fazem

### 3.1 Dois usuários, um motor

- **Extensionista (técnico de ATER, cooperativa, ONG):** é o usuário principal do MVP. Usa um painel web estático que funciona offline depois de carregado. Escolhe o município da família, lê os portões, compara as estratégias e vê a evidência completa.
- **Família agricultora:** recebe do técnico um **cartão em imagem** com no máximo 3 números, em frequências naturais ("de cada 10 anos parecidos, 4 quebraram o milho"). A família informa a data de plantio e as prioridades, e pode vetar uma sugestão.
- O cartão com áudio e o envio pelo WhatsApp ficam no roteiro. No MVP, o cartão é uma imagem que o técnico mostra.

### 3.2 As telas do MVP (três) e o que fica para depois

1. **Relógio da Quadra** (tela principal).
   - Seletor de município (184, mapa GeoJSON sem mapa base, que funciona offline).
   - **As três curvas** sobre o calendário, de novembro a julho: habilidade (chuva IMERG e oceano), opções (datas-limite de milho, sorgo e caupi) e visibilidade.
   - Os 5 portões e o de hoje destacado. Para cada portão:
     - o que o dado já sabe, em frequência natural e com o n;
     - o que ainda não sabe;
     - o que ainda dá para fazer;
     - o placar do alerta **neste município**, com acertos e erros.
   - **Painel "hoje"** (14/nov/2026):
     - ONI (NOAA) com o aviso de caso inédito;
     - contagem de anos análogos;
     - GRACE regional na média de 3 meses (p57, normal);
     - açudes do Sertão Central vistos pelo Landsat (p32 da série 1984–2025; uma AOI, grau C);
     - SMAP L4 (percentil da zona da raiz), **só se o AppEEARS entregar até sáb 20h**.
2. **Cartões de estratégia.**
   - A atual (S0) e três alternativas (S1–S3), lado a lado, cada uma como **sequência 2027–2028–2029**, com a entressafra.
   - Cada cartão traz os 5 campos do desafio: por que foi sugerida, evidência com recibo, benefícios, lacunas e riscos a confirmar com o técnico.
   - Três métricas calculadas: chance de colher menos da metade, "pior ano em 10" e mediana. As demais prioridades (forragem, N, erosão, matéria orgânica, mercado) entram como etiquetas qualitativas com grau.
   - Os pesos da família reordenam os cartões.
3. **Replay.**
   - **1998** (o análogo de El Niño mais próximo de 2027) e **2012** (a seca que só aparece tarde).
   - A chuva IMERG do município anima dia a dia, as barras de ISNA por cultura sobem e descem (grau C) e os portões acendem na data em que teriam acendido.
   - Na colheita, o rendimento observado do IBGE é revelado ao lado da estimativa da NASA (grau A).
   - A S3 aparece hachurada: "sem dado local; faixa da literatura (B·T)".

**Fora das telas do MVP:**
- A **auditoria** vira uma página HTML estática gerada em Python e um slide.
- Ficam no roteiro: código de barras do talhão ao vivo, áudio, simulador de WhatsApp e modo global ao vivo. Do modo global, entram 2 a 3 pontos pré-calculados, com grau C.

### 3.3 Fluxo de uso ao longo do ano

| Quando | O técnico faz | A família recebe ou faz |
|---|---|---|
| Primeira visita | Escolhe o município. Confirma a prática atual (o PAM sugere; 1 pergunta confirma). Faz 4 a 6 **perguntas de troca** que viram os pesos. Registra rebanho, semente guardada, maniva, mão de obra e água guardada. | Cartão de apresentação: "o QUADRA não sabe tudo; aqui está o que ele sabe". |
| **P1, nov–dez** | Lê o oceano e o banco de água. | Ações sem arrependimento: semente de caupi precoce e sorgo até dezembro, maniva guardada, palma, adesão ao Garantia-Safra, não queimar, aceiro. |
| **P2, jan–fev** | Lê a chuva recente. | "Plante uma parte agora e guarde a outra para São José." A família informa a **data de plantio**. |
| **P3, 19/mar ("Checkpoint São José")** | Lê o acumulado desde 1/jan. | Se o alerta acender, a área guardada vai para caupi (até ~21/mar) ou sorgo (até 11–21/mar). |
| **P4, 30/abr** | Lê o alerta de meio da quadra. | Ação graduada: guardar forragem, cortar o milho para os animais se o técnico confirmar, segurar a venda dos animais. |
| **P5, jul–dez** | Lê a água que sobrou e o combustível. | Palhada em vez de fogo, fenação do excedente, aceiro, perene em nível. |
| Fim de safra | Registra o resultado. | A família ordena os caminhos que testou. Isso gera evidência local de rotação, que hoje não existe. |

### 3.4 Glossário em pop-up (exigência do desafio)

- **Evapotranspiração (ET/ET0):** a água que o solo e a planta devolvem ao ar. A ET0 é a de uma grama de referência.
- **Balanço hídrico:** a chuva que entra menos a água que sai, dia a dia.
- **Anomalia de umidade:** quanto o solo está acima ou abaixo do normal daquela época.
- **NDVI:** o quão verde e vigorosa a vegetação está, vista do satélite.
- **Geada:** temperatura mínima ≤ 0 °C. Só aparece fora do Ceará, onde se aplica.
- **ISNA:** a fração da água de que a cultura precisou e que de fato recebeu.
- **"Pior ano em 10":** a média dos 10% piores anos (CVaR10).
- **"% do normal":** a chuva desde 1/jan dividida pela mediana dos outros anos no mesmo município.
- **Percentil.**
- **Grau de evidência A–D.**

### 3.5 Apoiar, não substituir

- Os pesos vêm da família.
- O técnico aprova toda mensagem.
- A família pode vetar ("não quero sorgo"); o app recalcula e mostra o custo da escolha.
- As datas-limite são de uma **janela sintética tipo-ZARC** feita com o IMERG; o cartão diz "confirmar no ZARC oficial com o técnico".
- Todo cartão termina com "o que confirmar no chão com o técnico".
- **Freio de segurança:** sem restrições, o otimizador de renda bruta escolhe "100% mandioca" em todos os municípios (`pesquisador_ia_conformal_carteira.py`). É o exemplo de por que a ferramenta apoia e não decide.

---

## 4. Arquitetura: núcleo global de dados NASA e enriquecimento local

### 4.1 Visão geral

```
        NÚCLEO GLOBAL                                           ENRIQUECIMENTO LOCAL (quando existe)
 [usado] IMERG V07 diário 0,1° (TRMM 1998–2014, GPM 2014→; Late)   Brasil: IBGE PAM (árbitro e calibração), ZARC oficial
 [usado] POWER (1981→; chuva = reanálise MERRA-2 corrigida)                (a conferir), MapBiomas, Garantia-Safra (a conferir)
 [usado] GRACE/GRACE-FO mascons (~300 km) · GLDAS-2.1 Noah          EUA: CDL/CSB, NASS, SSURGO, NLDAS
 [usado] Landsat 1984→ · HLS/S2 30 m · MODIS→VIIRS · VIIRS focos    Resto: FAOSTAT, GDHY, calendários SAGE/GGCMI
 [usado] NASADEM/SRTM 30 m · NEX-GDDP-CMIP6 · ONI/TNA/TSA (NOAA)    Família: data de plantio, água guardada, maniva,
 [pipeline pronto] SMAP L4 via AppEEARS · GLDAS-2.2 CLSM diário             veredito de fim de safra
 [roteiro] ECOSTRESS/ESI · Prithvi-EO-2.0 · NISAR
                  │                                                   │
                  ▼                                                   ▼
   GRADE COMUM + REGRAS DE ESCALA ─► exportador (lê as saídas já validadas) ─► JSON por município
        ─► Relógio (3 curvas, 5 portões) ─► Cartões S0–S3 + recibo ─► Replay (NASA estima, IBGE arbitra)
```

### 4.2 Grade comum e regras de harmonização

| Camada | Resolução nativa | Como entra na grade comum | Regra de uso |
|---|---|---|---|
| IMERG | 0,1° (~11 km), diário | É a **grade de decisão**. Agregada ao polígono do município para calibrar contra o PAM. | Chuva, veranico e % do normal por portão. O recibo marca 1998–2014 como era TRMM. |
| POWER | 0,5°, diário | Célula válida mais próxima de cada célula IMERG. | Sempre como **anomalia ou percentil por fonte**. A Tmax do POWER é cerca de 1,7 °C mais quente que a do ERA5, e a ET0 fica ~15% acima (seção 9.7). |
| SMAP L4 | 9 km, 3 h | Média por célula IMERG, com casamento de CDF contra o balde. | Percentil da zona da raiz, nunca limiar absoluto em mm. Rótulo "pipeline pronto" até chegar. |
| GRACE/GRACE-FO | ~300 km | Mascon regional, **média móvel de 3 meses**. | Só contexto regional. Um mês isolado só aparece com a faixa de ruído. O recibo mostra n_eff ≈ 28. |
| HLS / Landsat / S2 | 30 m (20 m) | Desvio **relativo à vizinhança de 10–20 km na mesma data**. | Cancela a deriva comum dos sensores e o viés de amostragem: o céu limpo coincide com o veranico (`sr_fundacao_r2_ceu_limpo_veranico.py`). |
| MODIS → VIIRS | 250 m – 1 km | Histórico do NDVI relativo (2000→). | A LST diurna do Terra fica fora depois de 2020 por causa da deriva (M6). |
| VIIRS (focos) | 375 m (~14 ha) | Contagem de focos por célula, agregada à paisagem. | Não é área queimada e nunca serve para fiscalizar um talhão. Área queimada: MapBiomas Fogo a 30 m. |
| NASADEM/SRTM | 30 m | Declive e baixio por município. | Erosão, baixio e aleias em nível. |
| NEX-GDDP | 0,25° | Delta de Tmax sobre o replay. | Cenário rotulado; só temperatura (a chuva não é robusta entre modelos; síntese 90.1). |

### 4.3 Que variáveis entram em cada módulo

| Módulo | Variáveis NASA | Variáveis locais | Saída |
|---|---|---|---|
| M1, gêmeo físico | IMERG diário; ET0, Tmax e radiação do POWER; declive NASADEM | Água disponível do solo, data de plantio, Kc e ciclos | ISNA por estágio, sobra de água na colheita, demanda de salvamento, janela sintética tipo-ZARC |
| M2, emulador de replay (fim de safra) | Saídas de M1; dias quentes acima do p90 local (POWER); NDVI relativo (MODIS) | PAM (alvo) | Estimativa da NASA para cada quadra do replay, com intervalo |
| M3, previsor por portão | IMERG acumulado desde 1/jan | ONI | Probabilidade por portão, habilidade, aviso de caso inédito, contagem de análogos |
| M4, carteira e política | Replay de M1–M3 nas 28 quadras | Pesos, restrições, preços | 3 estratégias + a atual, em sequência de 3 anos |
| M5, prática atual | MODIS/HLS (fenologia), focos VIIRS | PAM, 1 pergunta à família | Estratégia atual |
| M6, sentinela de deriva e qualidade | LST e NDVI do MODIS contra POWER, Landsat e HLS | PAM (bandeira de relato repetido) | Rebaixamento automático do grau |
| M7, relógio lento e combustível | GRACE, GLDAS, fração de água do Landsat, NDVI de t e t−1, focos VIIRS | Volume de barreiro ou cisterna | Banco de água azul, área salvável, perspectiva de fogo |
| M8, redator com verificador | JSON de M1–M7 | Trechos conferidos da revisão | Textos dos cartões em PT e EN, congelados |

### 4.4 Frescor dos dados na data da demo (14/11/2026)

- IMERG Late: até 12/11/2026. No MVP, só o **agregado estadual**; a extração de Quixadá dos arquivos já em disco é opcional (~30 min).
- IMERG diário municipal: até 14/09/2026.
- ONI: até ASO/2026. GRACE: até set/2026. GLDAS Noah mensal: até jul/2026.
- MODIS: até nov/2026, com o buraco de jun–nov/2025 no Terra.
- PAM: até 2025. Focos VIIRS no arquivo anual: até dez/2025.
- Pink Sheet: até out/2026.
- SMAP L4 (AppEEARS) e GLDAS diário com água subterrânea ainda estão chegando. **O MVP não depende deles.**
- Nota de unidade: o derivado `imerg_late_ce_mensal` rotula como "mm/day" o que é total mensal. O arquivo não foi alterado; a correção vale para o exportador.

---

## 5. Os módulos de IA (SI)

**Princípio da equipe:** com 28 quadras e cerca de 5 episódios de seca independentes desde 1998, a SI que funciona é **pequena, guiada pela física, validada por ano e comparada só com a mesma linha de base**. Três medidas sustentam isso:

- **A validação aleatória mente:** o boosting tem R² 0,49 com validação aleatória e −0,08 deixando o ano de fora (`cetico_escala_vazamento.py`).
- **A restrição física ajuda pouco e de forma honesta:** com as mesmas entradas, o GBM monotônico dá AUC 0,794 contra 0,762 do GBM livre, no milho (+0,03). No feijão, não ajuda (0,702 contra 0,739) (`saidas/hidrologo_hibrido_log.txt`).
- **A chuva diz o ano; física + satélite dobram a ordem local:** com as mesmas dobras, o ρ dentro do ano vai de 0,155 (só chuva, HGB) para 0,307 (duas escalas) (`saidas/pesquisador_ia_fusao_fisica_satelite.csv`).

### M1. Gêmeo físico do roçado (balde FAO-56)

- **Papel:** simular, para cada cultura e arranjo, a água que a planta recebe em cada estágio.
- **Método:** balde diário FAO-56 (ETc = Kc × ET0) vetorizado em numpy (Allen et al. 1998). A data efetiva de semeadura vem da inversão contra o PAM: o milho se comporta como semeado 0–10 dias após a 1ª chuva, e o feijão cerca de 20 dias depois (`agronomo_calibracao_pratica.py`).
- **Um balde por tipo de número**, declarado no recibo:
  - datas-limite e ISNA de milho, caupi e sorgo vêm do balde do agrônomo (`agronomo_isna_zarc_sintetico.py`);
  - sobra de água na colheita e demanda de salvamento vêm do balde do hidrólogo (`hidrologo_fao56_isna_pam.py`).
- **Validação, pareada:**
  - No milho, o ISNA soma cerca de +0,04 de AUC sobre a chuva com o mesmo modelo: 0,767 contra 0,727.
  - No feijão, piora: 0,637 contra 0,712 (`saidas/hidrologo_hibrido_log.txt`).
  - O ZARC sintético ordena os municípios como a quebra real (ρ de +0,40 a +0,49), mas isso valida a ordem, não as datas. Grau C.
- **Sensibilidade à fonte da ET0 (pedida pela banca):**
  - Com a ET0 na escala do ERA5 (× 0,87), as datas-limite andam no máximo 1 decêndio em 97–99% dos municípios. Andam exatamente 1 decêndio em 53% (milho), 59% (caupi) e 68% (sorgo) (`arquiteto_final_zarc_et0_sensibilidade.saida.txt`).
  - Por isso o cartão mostra a data-limite com **±1 decêndio**.
  - Em Quixadá: o milho fica em 01/mar e o caupi em 21/mar nas duas escalas; o sorgo vai de 11/mar para 21/mar.
- **Onde erra:**
  - Superestima 2010 e 2013 e **não vê 1998**: 4% dos municípios com ISNA < 0,5, contra 67% em quebra real (`pesquisador_ia_checa_simulador_anos.py`). Em Quixadá, o ISNA de floração do milho em 1998 foi 0,53, e o milho colheu zero.
  - Por isso **o risco de 2027 vem do oceano (M3), e não do balde**.
- **Incerteza:** a ordem resiste à água disponível do solo (ρ de 0,46 a 0,48 entre 30 e 90 mm). O nível não resiste: P(ISNA < 0,5) vai de 1,5% a 14,3% (`saidas/hidrologo_calibracao_balde.csv`).

### M2. Emulador de replay em duas escalas (estimativa de fim de safra)

- **Papel:** dar, para cada quadra do replay, a estimativa da NASA para o rendimento relativo do município, ao lado do observado do IBGE.
- **Rótulo obrigatório:** é um **emulador de fim de safra**. Ele usa o NDVI de mar–mai e o ISNA da floração, então **nunca aparece ao lado da curva de habilidade dos portões**.
- **Método:** ridge ou GBM monotônico em duas escalas:
  - nível do ano: ISNA agregado + calor relativo;
  - ordem local: desvio do ISNA + desvio do NDVI relativo aos vizinhos.
- **Validação, só pareada** (mesmas dobras LOYO; `saidas/pesquisador_ia_fusao_fisica_satelite.csv`):

  | Configuração | R² LOYO | ρ dentro do ano | AUC quebra | Viés walk-forward 2020–25 |
  |---|---|---|---|---|
  | Só chuva, HGB | 0,365 | 0,155 | 0,816 | −0,13 |
  | Duas escalas (ISNA ano+local, NDVI só local), ridge | 0,365 | **0,307** | 0,851 | +0,01 |

  - Leitura honesta: o R² empata; o ganho é a **ordem local dobrada** e o viés operacional menor.
  - A faixa das 14 configurações testadas vai de AUC 0,78 a 0,85. A configuração foi escolhida olhando o LOYO; por isso o bloco 0 do MVP refaz a escolha por **seleção aninhada** (dentro de cada dobra). Até lá, o recibo mostra a faixa.
  - O alvo do M2 (anomalia contra tendência) não é o canônico. No replay, o observado mostrado é sempre a razão canônica.
- **Incerteza:** conformal robusto ao ano (o ano é a unidade trocável). Ele cobre 77–86% dos anos no nível de 80%, contra 46–68% do conformal padrão, **mas compra isso com largura**. No portão de pré-safra, a largura passa de 227 para 282 pontos percentuais, onde o modelo é pior que a climatologia (MSSS −0,37). A frase certa é: "em janeiro, a incerteza honesta é do tamanho da climatologia" (`pesquisador_ia_conformal_carteira.py`).

### M3. Previsor por portão, com regra única de alerta

- **Papel:** em cada portão, dizer o que já se sabe e quanto isso vale, e quando não se sabe nada.
- **Regra única de alerta (canônica):** **chuva IMERG acumulada desde 1/jan < 75% do normal do município**, sendo o normal a mediana dos outros anos. Todos os números de alerta desta proposta usam essa regra.
- **Curva de habilidade canônica** (quebra canônica do milho; 5.106 município-anos; IC90 por bootstrap de anos; `arquiteto_final_curvas_quixada.saida.txt`, bloco A):

  | Portão | Chuva NASA (AUC) | Oceano, ONI já publicado | Chuva + oceano (logística, ano fora) | Dentro do ano (chuva) | Com alerta, quebram | Sem alerta, quebram |
  |---|---|---|---|---|---|---|
  | 15/nov | — | 0,67 (0,53–0,78) | — | 0,50 | — | — |
  | 31/jan | 0,57 (0,43–0,68) | 0,67 | 0,62 | 0,53 | 2,8 em 10 | 1,8 em 10 |
  | 28/fev | 0,67 (0,58–0,74) | 0,67 | 0,70 | 0,51 | 3,2 em 10 | 1,8 em 10 |
  | 19/mar | 0,73 (0,66–0,79) | 0,67 | 0,74 | 0,53 | **4,0 em 10** (n = 1.132) | **1,6 em 10** (n = 3.974) |
  | 31/mar | 0,75 (0,66–0,80) | 0,67 | 0,77 | 0,54 | 4,6 em 10 | 1,7 em 10 |
  | 30/abr | **0,80 (0,73–0,85)** | 0,67 | 0,81 | 0,57 | **5,2 em 10** (n = 932) | **1,5 em 10** (n = 4.174) |

  - Taxa-base de quebra: 2,15 em 10.
  - O oceano vale mais que a chuva até o fim de fevereiro (0,67 contra 0,57–0,67). A partir de São José, a chuva NASA passa à frente. Em 30/abr, o oceano já não acrescenta nada (0,81 contra 0,80).
  - A AUC de 30/abr mede uma janela que já é quase a quadra inteira (jan–mai dá 0,83; `cetico_r3_refutacoes.saida.txt`, bloco G). Por isso 30/abr serve para salvar, não para prever.
- **Escala declarada:** dentro do ano, a AUC fica entre 0,51 e 0,57. O alerta é **regional**. Em Quixadá, o alerta de 19/mar acendeu em 8 anos e acertou 2, e o de 30/abr acendeu em 7 e acertou 3 (bloco C). Isso aparece no placar do município.
- **Portão de novembro:** o ONI é o único sinal. A "habilidade em anos de |ONI| ≥ 1" (RPSS +0,13 contra −0,06; `clima_valor_decisao.py`) vem de n = 10 anos, metade de La Niña, sem IC. Por isso entra só como argumento qualitativo.
- **Detector de caso inédito:** o ONI de 2,46 está acima do máximo de ASO usado no treino (2,04).
- **Análogos só como contagem:** o app mostra quantos anos parecidos houve e o que aconteceu em cada um, nunca "de cada 10 anos como este" com n de 4 a 7 (seção 6.3).

### M4. Carteira e política

- **Papel:** gerar e ordenar as estratégias (a atual e mais 3) e a regra de cada portão.
- **Método:** **enumeração exata** de uma biblioteca de jogadas por portão: as regras de plantio R1–R9, a troca de cultura, o revezamento, o salvamento, a palhada e a composição de área. As regras R1–R9 já são a árvore de decisão que o técnico repete; não há destilação à parte.
- **Ranking:** usa os 3 eixos calculados: chance de colher menos da metade, "pior ano em 10" e mediana. Os pesos da família mexem só nesses 3. Forragem, N, carbono, trabalho e ciclos entram como etiquetas com grau.
- **Um motor de carteira só** no JSON: a carteira de áreas iguais, com a definição canônica (`juiz_carteira_definicao_canonica.py`, definição b). A carteira de mínimo CVaR do economista ("melhora em 81% de 131 municípios") vai para a auditoria como "diversificação em geral", porque é dominada por feijão, mandioca e caju e não é a S2.
- **Validação** (`arquiteto_final_carteira_ic.saida.txt`; 2.495 município-anos, 135 municípios, onde as três culturas existem):

  | Composição | Pior ano em 10 (CVaR10) | IC90 por ano | Chance de < 50% |
  |---|---|---|---|
  | 100% milho | 0,15 | 0,09–0,26 | 21% |
  | Milho + feijão | 0,26 | 0,19–0,38 | 15% |
  | 1/3 milho, 1/3 feijão, 1/3 mandioca | **0,36** | 0,28–0,47 | **11%** |

  - O ganho de CVaR10 da carteira 1/3 sobre o milho é de +0,17 a +0,23 (IC90 por ano).
  - Sem os anos de mandioca com rendimento repetido: de 0,14 para 0,34.
  - A cauda vem sobretudo de 1998, 2010, 2012, 2013 e 2016, ou seja, de três episódios de seca. O recibo diz isso.

### M5. Leitor da prática atual

- **No MVP:** a prática atual vem do PAM do município (o que se planta e quanto) e de **1 pergunta** à família ("o senhor queimou o roçado em nov/2025?").
- **Figura estática:** o "código de barras de safras" (fenologia MODIS/HLS + focos VIIRS) da AOI do Sertão Central entra como figura, com o selo de visibilidade.
- **Selo de visibilidade:** fração de AOI-anos com ao menos uma cena útil (≥ 60% da área limpa) nos 30 dias antes do portão, com Sentinel-2 + Landsat: 79% em 28/fev, 71% em 31/mar e 92% em 30/abr. É uma amostra de n = 24 AOI-anos (4 AOIs, 2020–2025). Só com o Landsat 8/9, a chance cai para 50% (28/fev), 29% (31/mar) e 46% (30/abr). As quadras do replay anteriores a 2015–2017 não têm Sentinel-2, então a visibilidade histórica é a do Landsat sozinho (`sr_fundacao_r2_checagens.log`, bloco B).
- **Limite:** a semeadura segue a chuva, quando o óptico está cego. Por isso a data de plantio é **perguntada à família**.
- **Roteiro:** código de barras ao vivo para qualquer talhão, Prithvi-EO-2.0 e Sentinel-1/NISAR para datar o plantio sob nuvem.

### M6. Sentinela de deriva e de qualidade

- **Papel:** rebaixar automaticamente o grau de qualquer camada que derive.
- **Método:** Mann-Kendall/Sen e CUSUM sobre o resíduo de cada sensor contra uma referência independente, mais bandeiras de qualidade do PAM.
- **O que já sinalizou:**
  - **A deriva documentada da órbita do Terra.** A LST diurna do MODIS lê 4,6 °C mais fria em relação à Tmax do ar do que em 2000–2019 (resíduo −6,17 °C em 2026 contra −1,56). A LST noturna não deriva. Usada sem correção, a LST levaria a previsão de 2026 para **+58% de safra**, contra +20% sem ela (`cetico_deriva_lst_terra.saida.txt`; `cetico_previsao_preregistrada_2026_*.saida.txt`). A deriva é documentada pela equipe do MODIS; o sentinela a pegou sozinho, mas não a descobrimos.
  - **Um deslocamento não explicado do NDVI.** Desde 2020, o NDVI de fev–mai está +0,053 mais verde para a mesma chuva. A causa pode ser real, de sensor ou de relato. O cruzamento com o Landsat não confirma a deriva do MODIS: a diferença MODIS − Landsat caiu por volta de 2013, com a entrada do OLI (`cetico_deriva_ndvi_modis_landsat.saida.txt`). Em operação, o modelo só de NDVI superestimou 2020–2025 em ~60 pontos de rendimento relativo, e o modelo só de chuva em ~24 (`cetico_walkforward.saida.txt`). A camada fica com grau rebaixado.
  - **Relato copiado no PAM (achado novo).** 92% dos municípios com 15 ou mais anos de mandioca têm pelo menos um ano com rendimento idêntico ao anterior; a mediana é de 11% dos anos. Mais repetição significa menos variância (ρ −0,37). Em Quixadá, o feijão de 2005 repete o de 2003 (`cetico_r3_sao_jose_mandioca.saida.txt`, bloco C). O sentinela marca esses anos, e a carteira é recalculada sem eles (M4).
  - **"2025, o ano mais verde"** é artefato do buraco do Terra (`ecologo_checagem_ndvi_2025.py`).

### M7. Relógio lento da água e combustível

- **Banco de água azul:**
  - GRACE menos a umidade do solo do GLDAS Noah. O solo esquece em cerca de 3 meses; o residual, em cerca de 48 meses (`hidrologo_grace_residuo_memoria.py`).
  - O n efetivo é ≈ 28; sem 2012–2017, o r cai para 0,31–0,35 (`cetico_memoria_grace_neff.saida.txt`).
  - **Dois sensores e um modelo, numa AOI:** no Sertão Central, a fração de água dos açudes no Landsat (1984–2026) acompanha a chuva de 48 meses (ρ +0,62) e o residual (+0,54). O sinal existe em 1 das 4 AOIs, e a janela de 48 meses foi a melhor entre 6.
  - O GWS do GLDAS-2.2 CLSM tem memória curta: o banco azul do sertão é sobretudo **açude, que evapora** (`hidrologo_r2_banco_azul_checagens.py`).
- **Área salvável:** o salvamento da floração do milho pede 62 mm na mediana (620 m³/ha). Uma cisterna-calçadão de 52 m³ salva cerca de 0,08 ha num ano mediano. **O salvamento só existe com barreiro ou açude**; o app pergunta o volume.
- **Combustível:** a anomalia de NDVI de fev–jun de t e de t−1 prevê os focos de out–dez por célula de 0,25° (skill fora do ano +0,072; `ecologo_r2_checagens.py`). O fogo sai em tercis com faixa larga. Para out–dez/2026, os preditores discordam, e o app mostra a discordância.

### M8. Redator com verificador

- **Papel:** redigir os textos dos cartões em PT e EN a partir do JSON.
- **Método:**
  - Os textos são redigidos **offline**, nesta sessão de trabalho, por um LLM (uso de inferência), com os números como marcadores `{var}` preenchidos pelo JSON. Depois são **congelados como estáticos**.
  - **Nenhuma API é chamada em tempo de execução.** O saldo da API da equipe acabou em 12/11, e a demo não pode depender de serviço externo.
- **Verificador determinístico** (cerca de 30 linhas):
  - todo número do texto precisa existir no JSON, com a mesma unidade, a mesma entidade e o mesmo grau;
  - léxico proibido: "garante", "vai chover", "certeza";
  - teste com cerca de 30 casos adversariais (número inventado, atribuição trocada, verbo de certeza), todos bloqueados.
- **Regra:** nenhum modelo é treinado com saídas de LLM.

### Os 5 usos de SI que vão para o slide

1. Emulador físico-ML monotônico em duas escalas, com conformal robusto ao ano (M1 + M2).
2. Curva de habilidade por portão medida sem olhar o futuro, com detector de caso inédito (M3).
3. Busca exata de estratégias pela cauda (CVaR), com freio de segurança (M4).
4. Sentinela de deriva e de qualidade de dado (M6).
5. Redator LLM aterrado, com verificador numérico e sem chamada em tempo de execução (M8).

### O que deliberadamente não usamos, e por quê

| Fica fora | Motivo, com dado |
|---|---|
| ML livre para prever rendimento no plantio | MSSS −0,37 no pré-safra: pior que a climatologia. |
| "Modelo grande" | Nenhum foi testado. Não afirmamos que modelos pequenos vencem modelos grandes; afirmamos que a validação aleatória infla (0,49 contra −0,08). |
| Aprendizado por reforço, NSGA-II, Pareto em 8 eixos | O espaço de jogadas é pequeno: a enumeração é exata e auditável. Só 3 eixos são calculados por estratégia. |
| Downscaling do SMAP a 1 km/70 m | Habilidade espacial R² 0,083 (`sr_fundacao_r2_checagens.py`). |
| TVDI | R² 0,077 deixando o ano de fora (`sr_fundacao_downscaling_aprendido.py`). |
| NDVI absoluto e LST do Terra pós-2020 | Deriva e deslocamento não explicado (M6). |
| Dataset "Crop Recommendation" do Kaggle | Padrão de dado sintético (síntese 90.3). |
| Replay com as 44 temporadas do POWER | A chuva do POWER é reanálise. O replay usa só as 28 quadras do IMERG; o POWER entra como contexto climatológico. |
| ECOSTRESS/ESI, Prithvi, SAR, EnKF, GNN de pragas, bot de WhatsApp | Sem dado em disco ou inviável em 36 h. Ficam no slide de próximos passos. |

---

## 6. O motor de rotação

### 6.1 Como gera as estratégias

1. **Biblioteca de componentes:**
   - anuais: milho, feijão/caupi, sorgo;
   - semiperene: mandioca;
   - perenes e forrageiras: palma, guandu, gliricídia;
   - arranjos: consórcio, revezamento, faixas;
   - manejo: palhada, aceiro, fogo ou não fogo.
2. **Regras de sucessão que vêm dos dados:**
   - **No sertão não existe safrinha.** O caupi em revezamento cerca de 50 dias após o milho tem P(ISNA floração ≥ 0,5) de 0,89 na mediana estadual. Em sucessão após a colheita, 0,14, sem nenhum município viável (`agronomo_isna_zarc_sintetico.py`, bloco A4; grau C, limite superior).
   - **Na entressafra não cabe cultura anual sem água.** A ET0 de ago–dez (POWER) é de 1.224 mm, contra 59 mm de chuva. A sobra de água na colheita é de 85 mm depois do sorgo e de 4 mm depois da mandioca (`hidrologo_fao56_isna_pam.py`). Depois da mandioca, só palhada.
   - **Escape hídrico não é quebra de ciclo.** Trocar milho por sorgo mantém a gramínea hospedeira da lagarta-do-cartucho. A quebra de ciclo exige uma não-gramínea (caupi, mandioca, palma), com o status confirmado pelo técnico.
3. **Restrições:**
   - janela sintética tipo-ZARC (±1 decêndio), a confirmar no ZARC oficial;
   - semente e maniva disponíveis antes da data-limite;
   - água azul declarada;
   - mão de obra e consumo da família;
   - regras do Garantia-Safra (limiar, cesta e área mínima), **só se conferidas na lei até sáb 14h**; senão, saem dos cartões.
4. **Avaliação:** cada estratégia é reencenada nas 28 quadras do IMERG. As sequências de 3 anos são **planos**: cada ano é avaliado na quadra do replay, e o efeito do antecessor (leguminosa, palhada) entra como prior da literatura com grau. O estado do solo entre anos não é simulado no MVP.
5. **Escolha:** a atual sempre entra. As outras 3 cobrem perfis distintos: calendário (S1), cauda (S2) e solo (S3). Os pesos da família reordenam a lista.
6. **A frase do slide 3:** *"In a one-window climate, rotation happens inside the season (relay, strips) and across years (legume, cassava, perennials, fallow without fire)."*

**Métricas de cada cartão:**
- **Calculadas (3):** chance de colher menos da metade; "pior ano em 10"; mediana.
- **Etiquetas com grau:**
  - uso de água: água verde, água azul e sobra para a entressafra;
  - forragem: kg MS, literatura, grau C;
  - fixação de N: como ganho de rendimento no cereal seguinte, grau B·T;
  - erosão: meses de solo nu × erosividade (I30 do IMERG, até 80 mm/h) × declive (NASADEM);
  - matéria orgânica: grau C;
  - mercado: teto de participação, PNAE/PAA;
  - ciclos: meses sem gramínea hospedeira, sem queima.

### 6.2 Exemplo concreto: Quixadá (Sertão Central), novembro de 2026

**Graus:**
- **A:** validado com dado local observado, por ano.
- **B:** meta-análise ou síntese multi-sítio.
- **C:** modelo, simulação, ensaio único ou ordem validada sem nível validado.
- **D:** suposição ou resumo de congresso.
- **·T:** transferido de outro clima; rebaixa meio grau.

**Família de demonstração, fictícia e rotulada como tal:** Dona Francisca, Quixadá, 3 ha (1 ha de baixio pelo SRTM), 8 cabras, cisterna de 16 m³ (água de beber), sem barreiro, semente própria de milho e feijão, **sem mandioca no chão hoje**. Prioridades: forragem > comida da família > renda.

**Contexto do município** (`arquiteto_final_curvas_quixada.saida.txt`, bloco C; definição canônica):
- **Milho:** 8 quebras em 28 anos: 1998 (0,00), 2001, 2012 (0,17), 2015, 2016 (0,12), 2023, 2024 e 2025. Grau A.
- **Feijão:** 5 quebras em 28 anos; 0,15 do normal em 2012. Grau A.
- **Mandioca:** só 10 anos têm as três culturas. A área foi 0 ha em 2012–2013 e 40 ha em 2016, então **não há mandioca observada nos piores anos depois de 1998**.
- **Datas-limite da janela sintética** (risco ≤ 30%; ±1 decêndio pela fonte da ET0): milho até 01/mar; sorgo até 11–21/mar; caupi até 21/mar. Grau C.
- **Placar do alerta em Quixadá** (o que o técnico vê):
  - 19/mar: 8 alertas e 2 acertos;
  - 30/abr: 7 alertas e 3 acertos;
  - perdidas em 30/abr: 2001, 2016, 2023, 2024 e 2025. As três últimas tiveram chuva normal (93% a 105% do normal em 30/abr), e o motor não as explica.
  - Isso é grau A e é mostrado assim mesmo: o alerta é regional.

#### S0. Atual: "roçado da 1ª chuva" (igual em 2027, 2028 e 2029)

- **Prática:** milho + feijão consorciados plantados na 1ª chuva de 20 mm ou mais em 3 dias. Broca e queima em out–dez; solo nu de setembro a janeiro.
- **Por que aparece:** é a linha de base. O PAM do município mostra que é a prática dominante, e a família confirma.
- **Evidência:**
  - Em Quixadá, o milho quebra em 8 de 28 anos (grau A).
  - Milho e feijão quebram juntos no PAM (0,78; grau A, com a ressalva do relato).
  - No estado, 100% milho tem "pior ano em 10" de 0,15 e 21% de chance de colher menos da metade (grau A).
- **Benefícios:** custo zero, semente própria, mercado conhecido.
- **Lacunas:** a água disponível do solo do roçado e a data real de plantio.
- **Riscos a confirmar:**
  - solo nu sob chuva erosiva;
  - perda de carbono com a queima (Primo et al. 2023: −50% em 10 anos numa simulação Century de um sítio; grau C);
  - fuga do fogo para os vizinhos;
  - nenhum mês sem gramínea hospedeira.

#### S1. "Escalonar, guardar a decisão e revezar em faixas" (custo zero)

- **2027:**
  - Metade da área na 1ª chuva firme (milho + feijão).
  - **A outra metade fica guardada para São José:** milho, se a chuva firmar antes de 01/mar; caupi (até ~21/mar) ou sorgo (até 11–21/mar), se o alerta acender em 19/mar.
  - Caupi em revezamento cerca de 50 dias após o milho.
  - Entressafra com palhada roçada, sem queima.
- **2028:** as faixas trocam de lugar: onde houve milho entra caupi/feijão, e vice-versa (gramínea ↔ leguminosa).
- **2029:** as faixas trocam de novo. A palhada e a ausência de fogo continuam.
- **Por que aparece:** janeiro engana (Quixadá teve 150% do normal em jan/1998 e 197% em jan/2016, e os dois anos quebraram). Escalonar mantém uma opção aberta até o último portão de troca.
- **Evidência:**
  - No estado, com o alerta aceso em 19/mar, 4 em 10 municípios quebram o milho; sem alerta, 1,6 em 10 (n = 1.132 e 3.974; grau A).
  - Em 19/mar, o caupi ainda cabe em 98% dos municípios e o milho em 42% (grau C).
  - Caupi em revezamento em Quixadá: P 0,75, contra 0,14 em sucessão (grau C, limite superior, porque o balde não modela competição).
- **O que o cartão diz com honestidade:**
  - Em Quixadá, o alerta de 19/mar é fraco: 2 acertos em 8 alertas.
  - O efeito do falso início no PAM não é significativo com erro-padrão agrupado por ano (`cetico_r2_checagens.py`, bloco B).
  - O valor da opção guardada não foi medido no PAM; é grau C.
- **Benefícios:** custo zero; parte da área decide com mais informação; o caupi dá N e proteína.
- **Lacunas:** o replantio não está modelado; a semente de caupi precisa chegar antes de 21/mar.
- **Riscos a confirmar:** arrependimento num ano bom, quando quem plantou tudo colhe mais; ficar fora da janela do ZARC oficial. A mensagem é "plante escalonado", nunca "não plante".

#### S2. "Tampão e forragem em faixas que giram" (escudo do ano ruim)

- **Desenho:** três faixas que trocam de lugar a cada ano:
  - **mandioca:** uma faixa nova recebe maniva a cada quadra, e a mandioca do ano anterior é o tampão do ano, colhida conforme a necessidade;
  - **sorgo forrageiro** com rebrota, como primeira cultura, mais palma adensada no cercado;
  - **caupi precoce** de 60–70 dias.
  - O milho fica só no baixio.
- **Giro das faixas:** a faixa que sai da mandioca recebe caupi, e a do caupi recebe sorgo. Assim sempre há mandioca de um ano no chão. Nenhuma faixa queima.
- **2027, dito com honestidade:** a mandioca precisa ser plantada **no ano anterior** para proteger o ano seco. Sem mandioca no chão hoje, o tampão de Dona Francisca começa em 2028. Em 2027, a proteção vem do sorgo, da palma, do caupi e das ações do P1.
- **Por que aparece:** a prioridade da família é forragem, e o risco do sistema atual está na cauda.
- **Evidência:**
  - Carteira 1/3 milho, 1/3 feijão, 1/3 mandioca no estado: "pior ano em 10" sobe de 0,15 para 0,36 (ganho com IC90 de +0,17 a +0,23), e a chance de colher menos da metade cai de 21% para 11%. São 2.495 município-anos, só onde a mandioca existe. Sem os anos de relato repetido, de 0,14 para 0,34. Grau A no estado.
  - **Replay de 1998 em Quixadá, observado pelo IBGE:** milho 0,00, feijão 0,16, mandioca 0,50. A carteira 1/3 ficou com 0,22, contra 0,08 de milho + feijão. É um ano só (grau A, n = 1).
  - O sorgo tem P(ISNA floração < 0,5) de 6,5%, contra 10,1% do milho (grau C). O PAM do sorgo não serve de evidência: são 21 municípios tecnificados.
  - Palma + sorgo: 6.279 contra 4.627 kg MS/ha (Diniz et al. 2017; ensaio único com irrigação em PE; grau C).
- **Benefícios:** forragem para as cabras no ano seco; comida da família na mandioca; solo coberto mais tempo.
- **Lacunas e riscos, nesta ordem:**
  1. **Maniva-semente guardada / banco de manivas.** Na seca, a mandioca some: Quixadá teve 0 ha em 2012 e 40 ha em 2016. A carteira estadual existe em 116 de 181 municípios em 1998, 104 em 2012 e 69 em 2016.
  2. Casa de farinha e mercado da mandioca. O hedge de preço (−0,80) é estadual; no município, a elasticidade é cerca de zero.
  3. Semente e mercado do sorgo: a área de sorgo em grão do Ceará caiu de 2.900 ha em 2021 para 15 ha em 2025 (`economista_debate_checagens.py`).
  4. Palma resistente à cochonilha (pergunta obrigatória ao técnico).
  5. O sorgo hospeda a lagarta: é escape hídrico, não quebra de ciclo.

#### S3. "Leguminosa que fica, sem fogo" (rotação no sentido estrito)

- **2027:** caupi com faixas de guandu ou gliricídia em nível (declive pelo NASADEM). Roçagem, palhada e aceiro, sem queima.
- **2028:** milho ou sorgo sobre a palhada da leguminosa, com caupi em revezamento.
- **2029:** mandioca, ou milho + caupi. As faixas perenes ficam.
- **Entressafra:** só palhada e perene de raiz funda.
- **Por que aparece:** é a única estratégia de rotação no sentido estrito e ataca nitrogênio, erosão, matéria orgânica e ciclo da lagarta ao mesmo tempo.
- **Evidência:**
  - Leguminosa antecessora: +20% no cereal seguinte, +32% em baixa produtividade (Zhao et al. 2022), com efeito menor na zona árida (Franke et al. 2018). Grau B·T.
  - Rotação diversa: perdas 14–90% menores em ano seco, em clima temperado (Bowles et al. 2020). Grau B·T.
  - Carbono: a agrofloresta recupera o carbono do solo em cerca de 10 anos, contra −50% com a queima (Primo et al. 2023, Sobral-CE; simulação de um sítio; grau C). O +0,56 Mg C/ha/ano de Jian et al. (2020) é de planta de cobertura e não se aplica a esta estratégia perene.
  - Chuva erosiva de fevereiro com I30 de até 80 mm/h (síntese 90.2; grau A).
- **No replay:** aparece hachurada, como faixa da literatura, sem número observado.
- **Benefícios:** milho de 2028 em diante sobre solo melhor; banco de proteína para as cabras; menos fogo e menos erosão; meses sem gramínea hospedeira.
- **Lacunas:** não existe ensaio revisado de rotação no semiárido do Ceará (revisão, seção de lacunas). O efeito real da leguminosa é a lacuna que mais muda o ranking.
- **Riscos a confirmar:**
  - competição por água: cerca de −4% de rendimento com cobertura (Abdalla et al. 2019; grau B·T);
  - mão de obra para implantar e 1–2 anos para estabelecer;
  - se o caupi local é hospedeiro secundário da lagarta.

### 6.3 O plano vivo de 2027 para Dona Francisca

| Portão | O que o QUADRA diz | Evidência |
|---|---|---|
| **P1, hoje (14/nov)** | "Dos 7 anos desde 1966 em que o mar de ago–out estava parecido, **4 tiveram quadra seca**, inclusive os dois mais quentes, 1998 e 2016. Num ano qualquer, é **1 em 3**. Com tão poucos anos, a chance real pode estar entre 2 e 9 em 10. E este ano é inédito: o mar nunca esteve tão quente nesta época." Ações sem arrependimento: semente de caupi precoce e sorgo até dezembro, procurar maniva, garantir a palma, manter a adesão ao Garantia-Safra, aceiro e palhada em vez de queima. | Análogos com ONI ASO ≥ 1,3: 1966, 1973, 1983, 1988, 1998, 2016 e 2024; 4/7, Clopper-Pearson 90% 0,23–0,87 (`cetico_r3_refutacoes.saida.txt`, bloco D). O resultado depende do limiar: com ≥ 1,5, são 3 em 4. O ano de 1966 entra pela chuva anual do CRU/GAEZ (proxy). O ONI de ASO separa a quebra municipal com AUC 0,67. Dos 6 El Niños desde 1998, 3 viraram catástrofe. Os anos do replay IMERG são **reponderados pela semelhança do oceano**: a NASA dá o ano, o mar dá o peso. O balde sozinho não vê 1998. O banco regional está normal (GRACE p57). |
| **P2, janeiro** | "Plante uma parte agora e guarde a outra para São José. Chuva boa em janeiro não garante a quadra." | A chuva de janeiro separa a quebra com AUC 0,57 e já enganou (Quixadá: 150% em 1998, 197% em 2016). |
| **P3, 19/mar** | "Em 19 de março, o que decide é a água que já está no solo. Se a chuva desde janeiro estiver abaixo de 3/4 do normal, a área guardada vai para caupi (até 21/mar) ou sorgo." | No estado, com o alerta, 4 em 10 quebram; sem ele, 1,6 em 10. Em Quixadá, o alerta é fraco (2 acertos em 8). O teste da tradição está na seção 7, inovação 4. |
| **P4, 30/abr** | Ação graduada: guardar forragem; segurar a venda dos animais; cortar o milho para as cabras só se o alerta se repetir e o técnico confirmar. Sem salvamento com água: a cisterna de 16 m³ é de beber. | Com o alerta, 5 em 10 quebram; sem ele, 1,5 em 10. Mas em 2016, o análogo de 2027, o portão de abril pegou só 7% das quebras. **Por isso, em 2027, a proteção vem de P1 e P2.** |
| **P5, jul–dez/2027** | Se a quadra for seca, haverá pouco combustível; se vier verde, fenar o excedente. Palhada e perene em nível. Nova faixa de maniva na quadra de 2028. | Combustível de t e t−1 visto pelo NDVI (M7), em tercis com faixa larga. |

---

## 7. O que é inovador

1. **O calendário de decisão é derivado de três curvas medidas: habilidade, opções e visibilidade.** É a imagem do slide 3 e do vídeo.
   - Habilidade: a chuva NASA sobe de AUC 0,57 (31/jan) a 0,80 (30/abr); o oceano fica em 0,67 desde novembro. As curvas se cruzam no fim de fevereiro.
   - Opções: o milho cabe em 93% dos municípios em 28/fev, 42% em 19/mar e 0% em 31/mar. O caupi cabe em 98% em 19/mar e 41% em 31/mar. Em 30/abr, nada mais cabe (`arquiteto_final_curvas_quixada.saida.txt`, bloco B).
   - Visibilidade: 79% em 28/fev, 71% em 31/mar e 92% em 30/abr (n = 24 AOI-anos).
   - **19 de março é o último portão em que a habilidade já passou a do oceano e a troca ainda cabe.** 30/abr é onde a habilidade e a visibilidade são máximas, mas só cabe salvar.
2. **Teste de estresse de rotações no registro da NASA, com o IBGE como árbitro.**
   - Cada estratégia é reencenada nas 28 quadras do IMERG e ordenada pelo pior ano.
   - O replay põe lado a lado a estimativa da NASA e o observado do IBGE.
   - O replay de 1998 mostra a decisão mudando: o oceano avisa em novembro, janeiro engana, São José abre a janela de troca dois dias antes da data-limite do caupi, e o IBGE revela o resultado.
3. **Honestidade como funcionalidade.**
   - Recibo A–D com a marca de evidência transferida (·T).
   - Placar do alerta por município, com erros (2016 perdido).
   - Auditoria com a inflação da validação aleatória (R² 0,49 contra −0,08).
   - O sentinela, que sinalizou a deriva do Terra e o relato copiado no PAM, uma camada de qualidade de dado que outras ferramentas não têm.
4. **Saber local testado com respeito: o "Checkpoint São José".**
   - A tradição diz que chuva no dia de São José (19/mar) garante o inverno. O teste justo compara com o **resto** da quadra (20/mar–31/mai): a chuva do dia e todo o acumulado até ali dizem a mesma coisa, de forma fraca (ρ estadual +0,32 nos dois; n = 28; p ≈ 0,1; `cetico_r3_sao_jose_mandioca.saida.txt`, bloco A).
   - A tradição é fraca, não errada. O que muda a decisão em 19/mar é a água que já está no solo: o acumulado separa a quebra do milho com AUC 0,73, como **estado do roçado**, não como profecia.
5. **Dois relógios da água e um portão de entressafra.**
   - O solo esquece em cerca de 3 meses; o açude, visto pelo Landsat, lembra por cerca de 4 anos (dois sensores e um modelo, numa AOI).
   - A entressafra, onde no sertão de fato se decide a rotação, vira um portão com ação: palhada em vez de fogo, nova faixa de maniva e perene em nível.

**O que isso exige e que é raro numa equipe de hackathon:** o painel de 184 municípios × 28 anos de rendimento observado cruzado com IMERG diário, POWER, GRACE, MODIS e VIIRS, e os resultados negativos que dizem o que não prometer.

---

## 8. Base científica (revisão `pesquisa/artigos_e_datasets.md`; grau entre colchetes)

| Componente | Referência | Achado que sustenta |
|---|---|---|
| Rotação como política, portões | Dury et al. 2012, Agron. Sustain. Dev. 32:567–580 | O plano de cultivo real é dinâmico e adaptativo. [B] |
| Pesos do agricultor, multicritério | Sadok et al. 2008, Agron. Sustain. Dev. 28:163–174 | Avaliação ex ante com apoio multicritério. [B] |
| Grafo de sucessões, enumeração | Detlefsen & Jensen 2007, Agric. Syst. 94:566 | Rotação como fluxo em rede, otimizável de forma exata. [B] |
| IA de rotação (trabalho mais próximo) | Fenz et al. 2023, Comput. Electron. Agric. 212:108160 (lido só no nível do resumo) | Planejamento de rotação com IA e dados. Nós acrescentamos o tempo da decisão e o risco de cauda. |
| RL acoplado a simulador | Kallenberg et al. 2023, Environ. Data Sci. 2 | RL com modelo de cultura para **adubação nitrogenada**, não rotação. Citado só como exemplo do porquê não usamos RL. |
| Balde FAO-56 | Allen, Pereira, Raes & Smith 1998, FAO-56 | ETc = Kc × ET0; Kc, p e estágios por cultura. [B] |
| ZARC | MAPA/Embrapa (revisão 6.7) | O ISNA e a tábua de risco condicionam crédito e seguro. Nossa janela é sintética [C]. |
| Veranico e perda | Rocha et al. 2021, RBMet 36:579–589 | Veranico explica a perda; milho + feijão = 91% da área. [B, Nordeste] |
| Oceano como probabilidade | Kayano & Andreoli 2006, JGR 111:D13101; Nobre & Shukla 1996, J. Climate 9:2464 | O ENSO sozinho acerta 36%; o Atlântico condiciona a ZCIT. [B] |
| Previsão empírica de referência | Rocha Júnior et al. 2021, Water 13:1613 | Modelo empírico simples é competitivo no Nordeste. [B] |
| Seca e adaptação | Marengo et al. 2018, An. Acad. Bras. Ciênc. 90:1973; Marengo et al. 2021 | A seca de 2010–2016; adaptação ainda pós-desastre. [B] |
| Leguminosa antecessora | Zhao et al. 2022, Nat. Commun. 13:4926; Franke et al. 2018, AGEE 261:172 | +20% (+32% em baixa produtividade); menor no árido. [B·T] |
| Resiliência pela diversidade | Bowles et al. 2020, One Earth 2:284; Renwick et al. 2021, ERL 16:084067; Beillouin et al. 2021, GCB 27:4697 | Perdas menores em ano seco, efeitos variáveis. [B·T] |
| Consórcio e forragem | Himmelstein et al. 2016; Mudare et al. 2022 [B]; Souza et al. 2011, Bragantia 70:715 [C, ensaio único]; Diniz et al. 2017, PAB [C, ensaio irrigado único] | Consórcio +23% na África; LER > 1; milho + caupi em Petrolina; palma + sorgo. |
| Cobertura: custo | Abdalla et al. 2019, GCB 25:2530 | Cerca de −4% na cultura principal e custo de água. [B·T] |
| Fogo, pousio e carbono | Primo et al. 2023, J. Environ. Manage. 336:117594 [C, simulação de um sítio]; Salcedo et al. 1997; Cano-Crespo et al. 2015 [B] | −50% de C em 10 anos sem pousio; fuga do fogo para vizinhos. |
| Área queimada a 30 m | Franca Rocha et al. 2024, Fire 7:437 | 12,7% da Caatinga queimou em 1985–2023 (MapBiomas Fogo). [A, regional] |
| Combustível da quadra anterior | Argibay et al. 2020, Ecol. Indic. 113:106151; Bezerra et al. 2025, Atmosphere 17:46 | Ano úmido seguido de ano seco gera grandes queimadas. [B] |
| Quebra de ciclo de praga | Ratnadass et al. 2011; du Plessis et al. 2020, Insects 11:228; Azambuja & Degrande 2014 | Ruptura temporal de hospedeiro; graus-dia da lagarta; vazio sanitário do algodão. [B] |
| Satélite térmico e solo raso | Anderson et al. 2016, RSE 174:82; Rossato et al. 2017; Fisher et al. 2020, WRR 56 | ESI e ECOSTRESS: base do item de roteiro. |
| SMAP L4 | Reichle et al. 2019, JAMES 11:3106 | Erro sem viés de 0,026 m³/m³ na zona da raiz. |
| GRACE e reservatórios | Gonçalves et al. 2020, STOTEN 705:135845; Lima et al. 2020; Melati et al. 2019 | GRACE com r = 0,78 contra o volume dos açudes do Nordeste. [B] |
| POWER e IMERG no mundo | Van Wart et al. 2015, AFM 209–210:49; White et al. 2008, AFM 148:1574; Rozante et al. 2018, Remote Sens. 10:882 | Clima de satélite alimenta modelos de cultura; viés da Tmax do POWER; o IMERG subestima o litoral do Nordeste. |
| HLS | Claverie et al. 2018, RSE 219:145 | Landsat e Sentinel-2 harmonizados a 30 m. |
| Fenologia | Arvor et al. 2011, IJRS 32:7847 | Séries de EVI/NDVI detectam ciclos no Brasil. |

**Saem:** Silva et al. 2009 (algodão agroecológico) é resumo de congresso [D]. Por isso a S4 opcional de algodão sai da proposta e fica nas ideias futuras.

**Fora da revisão** (DOI conferido no Crossref ou no arXiv por um agente na rodada 1; reconferir antes do slide):
- Rockafellar & Uryasev 2000, Journal of Risk 2(3), doi 10.21314/JOR.2000.038: CVaR.
- Barber et al. 2021, Ann. Statist. 49:486, doi 10.1214/20-AOS1965: base dos intervalos conformais.
- Roberts et al. 2017, Ecography 40:913, doi 10.1111/ecog.02881: validação cruzada em blocos.
- Lemos et al. 2002, Climatic Change 55:479, doi 10.1023/A:1020785826029: previsão sazonal no Ceará.
- Gigerenzer & Hoffrage 1995, Psychol. Rev. 102:684, doi 10.1037/0033-295X.102.4.684: frequências naturais.
- van Etten et al. 2019, PNAS 116:4194, doi 10.1073/pnas.1813720116: ciência cidadã tricot.
- Szwarcman et al. 2024, arXiv:2412.02732: Prithvi-EO-2.0, só como próximo passo.

---

## 9. Validação honesta e limitações

### 9.1 Protocolo, igual para toda a equipe

- **A unidade independente é o ano**, não o município-ano. Os resíduos se correlacionam por centenas de km (`pesquisador_ia_hierarquico.py`).
- **Toda variável de nível anual** (ONI, dipolo, GRACE regional) tem erro-padrão agrupado por ano. Município-anos não são réplicas.
- **Validação:** toda métrica sai de uma destas três: deixando o ano inteiro de fora (LOYO); walk-forward, só com o passado; deixando o episódio de seca de fora, com 2012–2017 como um bloco.
- **Seleção aninhada:** toda escolha de regra, limiar, análogo ou configuração é aninhada. Escolher pelo resultado do teste é proibido (correção do M2 no bloco 0).
- **Toda AUC** é decomposta em entre anos e dentro do ano.
- **Os intervalos** vêm de bootstrap por ano. O recibo mostra o n efetivo: são cerca de 5 episódios de seca desde 1998.
- **Comparação:** toda comparação de modelos é **pareada**, com as mesmas entradas e as mesmas dobras.
- **Toda estratégia** é avaliada contra o **rendimento observado do PAM**, nunca contra o ISNA do próprio balde.

### 9.2 Números de cabeçalho, os únicos que vão para os slides

| # | Afirmação | Valor | Validação | Fonte | Grau |
|---|---|---|---|---|---|
| 1 | No registro do PAM, milho e feijão quebram juntos | ρ mediano 0,78 (0,67 sem o choque do ano) | Descritivo, 183 municípios | `arquiteto_numeros_canonicos.txt`; `cetico_r3_refutacoes.saida.txt` F | A |
| 2 | A chuva NASA aprende durante a quadra; o oceano sabe pouco desde novembro | AUC 0,57 (31/jan) → 0,73 (19/mar) → 0,80 (30/abr; IC90 0,73–0,85); oceano 0,67 (0,53–0,78); dentro do ano ≤ 0,57 | LOYO + bootstrap por ano | `arquiteto_final_curvas_quixada.saida.txt` A | A |
| 3 | As opções fecham | Milho cabe em 93% (28/fev) → 42% (19/mar) → 0% (31/mar) dos municípios; caupi em 98% (19/mar) | Simulação, ±1 decêndio | idem B; `arquiteto_final_zarc_et0_sensibilidade.saida.txt` | C |
| 4 | Alerta único em 30/abr | Com alerta, 5 em 10 quebram; sem alerta, 1,5 em 10 (n = 932 e 4.174). 2012 pego (91%); 2016 perdido (7%) | LOYO do normal; IC por ano a anexar no bloco 0 | idem A | A |
| 5 | A validação aleatória infla | R² 0,49 contra −0,08 | Aleatório contra LOYO | `cetico_escala_vazamento.py` | A |
| 6 | A chuva diz o ano; física + satélite dobram a ordem local | ρ dentro do ano 0,155 → 0,307; AUC 0,816 → 0,851 (fim de safra; faixa das 14 configurações 0,78–0,85) | Mesmas dobras LOYO; seleção aninhada no bloco 0 | `saidas/pesquisador_ia_fusao_fisica_satelite.csv` | A |
| 7 | Um terço em mandioca protege a cauda | "Pior ano em 10" 0,15 → 0,36 (ganho com IC90 +0,17 a +0,23); chance de < 50%: 21% → 11% | 2.495 município-anos onde a mandioca existe; robusto sem os anos repetidos | `arquiteto_final_carteira_ic.saida.txt` | A |
| 8 | El Niño: mais chance, não certeza | 3 dos 6 El Niños desde 1998 viraram catástrofe; 3 passaram | Contagem por ano | `cetico_r3_refutacoes.saida.txt` A | B |

**Proibido no deck:** qualquer número que use outra definição de quebra, outra regra de alerta ou comparação não pareada.

### 9.3 Onde erramos, e mostramos (uma regra só)

- **2012:** pego tarde. Em 19/mar, o alerta pegou 40% das quebras; em 30/abr, 91% (123 de 135). Quando acende, já só cabe salvar.
- **2016, o análogo de 2027:** perdido. Em 30/abr, o alerta pegou 7% (9 de 127). Janeiro teve 205% do normal no estado (`designer_caso_2016.py`). Só o oceano avisou.
- **2024:** El Niño forte sem quebra estadual (8%), com o Atlântico recorde de quente. Em Quixadá, porém, o milho quebrou (0,46) com chuva normal.
- **Quixadá 2023–2025:** três quebras do PAM com chuva normal. O motor não explica (praga, relato ou área). Fica na auditoria.
- **O balde** superestima 2010 e 2013 e não vê 1998 nem 2001.
- **Alarmes falsos:**
  - em 30/abr, 48% dos alertas caem em municípios sem quebra;
  - em 28/fev, 68%, e por isso fevereiro não tem alarme;
  - em 3 anos de uso, 60% das famílias não recebem nenhum alerta (`designer_confianca_alertas.txt`). Por isso o calendário fixo de 5 conversas tem conteúdo mesmo em ano quieto.
- **Anos de excesso** (2009, 2024): o balde não modela encharcamento.

### 9.4 Grau de evidência por tipo de afirmação

| Grau | O que é | Exemplos |
|---|---|---|
| A | Validado com dado local observado, por ano | Correlação entre culturas no PAM, curva de habilidade, alerta, carteira estadual |
| B | Meta-análise ou síntese multi-sítio; contagem de poucos anos | El Niño × quebra (contagem), fuga do fogo para vizinhos (Cano-Crespo 2015) |
| B·T | B transferido de outro clima (meio grau abaixo) | Leguminosa antecessora, rotação diversa, custo da cobertura |
| C | Modelo, simulação, ensaio único, ordem validada sem nível | Datas-limite sintéticas, revezamento, sorgo no balde, palma + sorgo, carbono de Primo, açude numa AOI |
| D | Suposição ou resumo de congresso | Volume de cisterna suposto, preço de forragem, algodão agroecológico |

### 9.5 Limitações

1. **Nenhum efeito de rotação foi observado no Ceará.** O PAM valida o efeito do clima sobre cada cultura, não o do antecessor.
2. **A habilidade é regional.** Tudo foi calibrado no município (o PAM é estimado pelo IBGE e pela Ematerce), e a decisão é do roçado de 1–5 ha. Dentro do ano, a AUC é ≤ 0,57.
3. **2027 está fora da distribuição** (ONI ASO 2,46 contra o máximo de 2,04). Toda probabilidade é extrapolação, com 4 a 7 análogos.
4. **Poucos episódios.** Há cerca de 5 episódios de seca desde 1998, e a cauda da carteira vem de três. Todo IC é largo.
5. **A área plantada se adapta** ao ano: ρ com o ONI de NDJ de −0,43 no milho (`cetico_r2_checagens.py`, bloco C).
6. **Qualidade do PAM por cultura.** A mandioca tem relato repetido e ciclo longo; o feijão mistura Phaseolus e caupi; o sorgo é tecnificado e tem n pequeno.
7. **Escala da água azul.** A família típica de sequeiro não tem água para salvar o roçado.
8. **Sem custo de produção.** A renda é normalizada e bruta.
9. **Regras institucionais não conferidas:** o limiar do Garantia-Safra (40% ou 50%), a cesta, a área mínima e a janela do ZARC oficial de Quixadá. Sem conferência, não entram em slide.
10. **Muitos testes sobre os mesmos 28–44 anos.** O dipolo × início, o fogo × NDVI e o "ONI além da chuva" são exploratórios e não vão para o pitch.

### 9.6 Testes que dão para fazer antes do júri

- **Conversa com um técnico de ATER ou um agricultor** (José; seção 10). Vale mais para o Impacto do que qualquer teste novo.
- **Seleção aninhada do M2** e IC por ano do alerta de 30/abr (bloco 0).
- **SMAP L4**, se chegar: percentil da zona da raiz contra o GWETROOT na AOI do Sertão Central.
- **Pré-registro com hash** da contagem de análogos de 2027: **só com o OK explícito do José**, porque é voz pública.
- Cortados por custo ou dependência: FIRMS NRT (exige chave), LSPA, código de barras contra o CDL do Texas.

### 9.7 Folha de números canônicos e erratas (obrigatória antes do deck)

**Números canônicos:**

| Item | Valor canônico | Não usar |
|---|---|---|
| ONI | ASO/2026 = +2,46; recorde para ago–out (antes 2,04, em 1997); recorde absoluto 2,59 (NDJ 2015) | "o El Niño mais forte da história"; "2,14"; "2,31" |
| GRACE CE | Média de jul–set/2026 no p57: banco regional normal | "caiu para p35"; "reserva caindo" |
| ET0 do CE | 1.970 (ERA5) a 2.280 (POWER) mm/ano; 2,5 a 2,8 vezes a chuva da mesma fonte; supera a chuva em 10 de 12 meses nas duas | Um valor único chamado de "correto" |
| Ureia/milho | 1,85 em out/2026; pico de 4,00 em abr/2026; média de 2000–2020 = 1,51 (`cetico_r2_ureia.py`) | "4,0 agora" |
| Quebra | Produção ÷ área plantada < 50% da mediana do município nos outros anos; milho 21,5% e feijão 14,6% (1998–2025) | Mediana móvel; área colhida; limiar de 60% |
| Alerta | Chuva IMERG desde 1/jan < 75% do normal (mediana dos outros anos) | "3,8 contra 1,1"; "33 alertas, 31 acertos"; padrão "011" |
| Milho 2012 | −69% no estado; 75% dos municípios em quebra | "71%", "50%" |
| Registro de chuva | IMERG (eras TRMM e GPM), 28 quadras 1998–2025; POWER 1981–2026 é reanálise (MERRA-2 corrigida) | "28 years of GPM"; "44 quadras observadas" |
| Fogo | 17% da área do CE em células de ~375 m com ≥ 1 foco (2012–2025); área queimada pelo MapBiomas | "17,4% do Ceará queimou"; "o fogo volta a cada 3 anos" como fato de talhão |
| Pontos globais | 40 de 47 pontos terrestres tropicais sem mês de quebra térmica | "86% dos trópicos" |

**Erratas da síntese e do rascunho:**
- **ET0 (corrige a errata do rascunho):** o ~1.960 mm/ano da síntese é a ET0 do ERA5, e os 2.279 mm/ano do rascunho são a do POWER. Os dois estão certos; a diferença de 15% vem do viés quente da Tmax do POWER.
- **OR 2,30 do El Niño:** era o termo de uma interação e tinha erro-padrão iid. Sai.
- **Início da estação (ρ −0,67):** é retrospectivo e mecânico. O início causal tem ρ ≈ 0 com a chuva restante. Sai a regra de fevereiro.
- **"2025, o ano mais verde"** é artefato do MODIS Terra.
- **"Fogo cerca de 6 meses depois de anos verdes":** o sinal forte é a quadra do ano anterior.
- **"O combustível explica metade da tendência do fogo":** duas séries com tendência em 14 anos não sustentam atribuição. Sai.
- **"IMERG Late da estação seca −0,5 dp" como motivo de alarme:** a chuva de ago–out não prevê a quadra (ρ −0,06, n = 28). Sai de "por que agora".
- As elasticidades com mediana móvel curta estão subestimadas: o milho é +13,8%/100 mm (`pesquisador_ia_hierarquico.py`).

---

## 10. Plano de MVP para as próximas ~38 h

**Orçamento:** cerca de 27 horas-pessoa (estimativa do engenheiro de viabilidade), que cabem em 2 pessoas mais agentes.

| Tarefa | Horas |
|---|---|
| Exportador | 3 |
| Trajetórias diárias | 1,5 |
| App | 8–10 |
| Textos e verificador | 2 |
| Auditoria | 2 |
| Slides | 4 |
| Vídeo | 3 |
| Checagem cruzada | 2 |

**Decisões até as 10h de sábado:** tamanho da equipe e papéis, nome e esta folha canônica.

**Papéis:**
- **P1, Motor:** exportador e JSON.
- **P2, App:** página estática HTML + JS + Plotly, com GeoJSON dos 184 municípios e sem mapa base.
- **P3, Ciência e recibo:** bloco 0, recibos, auditoria e texto de SI.
- **P4, Narrativa:** slides e vídeo.

Com 2 pessoas: P1+P3 e P2+P4.

**Arquitetura:**
- **Não empacotar nem importar os scripts do conselho.** Importar executa o script e sobrescreve `conselho/analises/saidas/`.
- Um único `motor/exportar.py` **lê as saídas já salvas**:
  - `agronomo_zarc_sintetico_prob.parquet`;
  - `agronomo_isna_mun_ano.parquet`;
  - `hidrologo_fao56_mun_ano.parquet`;
  - o cache de chuva diária e o PAM.
- Ele **copia** (não importa) só a função `simular()` para gerar as trajetórias diárias de 3 municípios × 3 anos.
- Sai um JSON por município (184) e por ponto global (2 a 3). A página é estática e não chama nenhuma API ao vivo.

| Bloco | Quando | Quem | Tarefa | Pronto quando |
|---|---|---|---|---|
| 0 | Sáb 10–13h | P3 (+ todos às 10h) | Congelar a folha 9.7. Seleção aninhada do M2. IC por ano do alerta de 30/abr. Esquema do JSON (portões, estratégias, recibos). | Ninguém usa número fora da folha. |
| 1 | Sáb 10–14h | P1 | `motor/exportar.py`, trajetórias diárias (Quixadá, Tauá, Iguatu × 1998, 2012, 2016), JSON dos 184. Baixar em segundo plano o IMERG_PRECTOT + ET0 do POWER de 2 pontos globais (1998–2025). | O JSON de Quixadá bate com os `.saida.txt` desta proposta. |
| 2 | Sáb 13h – Dom 02h | P2 | As 3 telas: Relógio (3 curvas, portões, placar do município, painel "hoje"); Cartões S0–S3 em 3 anos; Replay de 1998 e 2012 (frames do Plotly, IBGE revelado na colheita). Glossário em pop-up. | Quixadá carrega em < 2 s no celular. |
| 3 | Sáb 14–20h | P3 | Página de auditoria estática gerada em Python. Textos dos cartões redigidos offline e congelados; verificador regex com 30 casos adversariais. | Zero números fora do JSON; os 30 casos bloqueados. |
| 4 | Sáb 20h | P1 | Ponto de corte do SMAP: chegou, entra 1 gráfico com recibo; não chegou, fica "pipeline pronto". | Decisão registrada. |
| — | **Sáb 22h** | Todos | **Números congelados.** | — |
| — | **Dom 02–08h** | Todos | **Sono obrigatório.** | — |
| 5 | Dom 08h | P2 | **App congelado**; ele vira a fonte das telas do vídeo. | — |
| 6 | Dom 08–13h | P4 (+P3) | 7 slides em inglês. | — |
| 7 | Dom 12–17h | P4 | Vídeo de 30 s (roteiro 11.2). | Vídeo gravado até 17h. |
| 8 | Dom 17–20h | Todos | Checagem cruzada (slides × folha × app) e ensaio. | Nenhuma divergência. |
| 9 | Dom 20–22h | Todos | Publicar no GitHub Pages; vídeo e PDF como reserva. Submeter. | Submetido antes das 22h; folga até 23:59. |

**Tarefas do José (pessoa, não agente):**
- ler hoje de manhã o regulamento sobre trabalho anterior ao evento e o formato da declaração de uso de IA;
- conferir até sáb 14h o limiar e a cesta do Garantia-Safra e a janela do ZARC de Quixadá;
- até sáb 18h, falar com 1 técnico de ATER ou 1 agricultor e mostrar o cartão de Dona Francisca;
- decidir sobre o pré-registro.

**O que cortar se faltar tempo, nesta ordem:**
1. Pontos globais: fica 1 ponto.
2. Painel de fogo: vira uma linha no cartão S0.
3. Trajetórias diárias animadas: o replay mostra só os portões e a revelação do IBGE.
4. O replay de 2012: fica só o de 1998.

**Nunca cortar:**
- o Relógio com as 3 curvas;
- os 4 cartões com recibo;
- o replay de 1998 com o observado do IBGE;
- a folha canônica.

**Cortados de saída do MVP:**
- código de barras ao vivo (fica a figura estática);
- áudio e TTS (ficam como roteiro, a menos que haja voz humana gravada até sáb 18h);
- modo global ao vivo;
- ECOSTRESS e GNN/Prithvi;
- simulador de WhatsApp;
- FIRMS NRT, LSPA e CDL;
- Pareto em 8 eixos e árvore destilada;
- replay com as temporadas do POWER;
- explicador LLM em tempo de execução.

**Próximos passos (slide):** Prithvi-EO-2.0, Sentinel-1/NISAR para datar o plantio, assimilação do SMAP L4, ECOSTRESS/ESI como gatilho, bot de WhatsApp com áudio, rede de pluviômetros, veredito tricot, EVPPI e GEOS-S2S.

---

## 11. Roteiro da demo

### 11.1 Os 7 slides (em inglês)

1. **"Will it rain on São José's day?"**
   - *QUADRA: the sertão's word for the rainy season.* A tradição diz que chuva em 19 de março garante o inverno.
   - Testamos contra o resto da quadra, nas 28 quadras do registro IMERG (TRMM + GPM): a chuva do dia e todo o acumulado dizem o mesmo, de forma fraca (ρ ≈ +0,3).
   - O que muda a decisão em 19/mar é a água que já está no solo. "Tradition is weak, not wrong. So we built the checkpoint on that day."
2. **"One window, one chance."**
   - Mapa do Ceará em 1998 e 2012: 3 em 4 municípios perderam mais da metade do milho.
   - No registro, milho e feijão quebram juntos (0,78).
   - O mesmo problema no Sahel, na Índia de sequeiro e no Texas.
3. **"Three curves decide when to decide."** É a imagem principal.
   - Habilidade da chuva NASA (0,57 → 0,80) e do oceano (0,67).
   - Opções fechando (milho 93% → 42% → 0%).
   - Visibilidade (até 92% em 30/abr).
   - Os 5 portões e a frase "In a one-window climate, rotation happens inside the season and across years."
4. **Momento uau: "Replay 1998 over Quixadá."**
   - Nov/1997: o oceano avisa. Jan/1998: 150% do normal, e janeiro engana. 19/mar: 70% do normal, com a janela do caupi aberta até 21/mar. 30/abr: 62%, só salvar.
   - Na colheita, o IBGE revela: milho 0, feijão 0,16, mandioca 0,50. O plano com 1/3 em mandioca guardou cerca de 1/5 de uma colheita normal, contra menos de 1/10.
   - No estado, o "pior ano em 10" vai de 0,15 para 0,36.
   - Clique num recibo.
5. **"NASA is the engine, IBGE is the referee."** Diagrama missão → decisão, com três rótulos:
   - *used in this demo:* IMERG, POWER, GRACE, Landsat/HLS, MODIS, VIIRS, SRTM, GLDAS, NEX-GDDP;
   - *pipeline ready:* SMAP L4;
   - *roadmap:* ECOSTRESS, Prithvi, NISAR.
6. **"How we used SI, honestly."**
   - "Rain tells the year; physics + satellite doubles the local ranking (0.155 → 0.307)."
   - "Random validation lies (0.49 vs −0.08)."
   - "Our drift sentinel automatically flagged Terra's documented orbit drift: daytime LST reads 4.6 °C cooler relative to air temperature than in 2000–2019; used raw, it would fake a crop boom."
   - Uma linha: "Where we fail: 2016 missed in April; skill is regional, not field-level" + link para a auditoria.
7. **"Today: strongest Aug–Oct El Niño on record."**
   - "Of 7 years with a similar ocean, 4 had a dry season; in a normal year it is 1 in 3."
   - Ações sem arrependimento para Dona Francisca (fictícia).
   - Frase do técnico de ATER, se obtida com permissão.
   - Mesmo motor em 2–3 pontos globais pré-calculados (grau C).
   - "NASA evidence. The farmer decides."

### 11.2 Vídeo de 30 s (em inglês, com legenda; no máximo 3 números)

| Tempo | Imagem | Locução |
|---|---|---|
| 0–5 s | Calendário de Quixadá em 19/mar/1998; a barra de chuva IMERG em 70% | "March 19, 1998. NASA's rain record over this county already shows 70% of normal." |
| 5–12 s | As 3 curvas se cruzando sobre o calendário | "In January, nobody can tell the season. QUADRA finds the checkpoints where NASA data already know, and you can still switch." |
| 12–20 s | Os 4 cartões de rotação em 1998; o IBGE revela o observado; selos IMERG, POWER, GRACE | "That year, corn gave zero. A plan with a third in cassava kept about a fifth of a normal harvest." |
| 20–27 s | Mostrador do ONI; o Relógio com P1 aceso | "Today the Pacific is warmer than before 1998, the strongest August–October El Niño on record. Buy cowpea seed now, don't burn, decide on São José." |
| 27–30 s | O técnico e a família olhando o cartão | "NASA evidence. The farmer decides." |

**Cuidados:**
- A família é fictícia e rotulada.
- Não usar logomarca da FUNCEME, da Ematerce ou da NASA que sugira endosso. Os selos dizem "data from".
- "QUADRA: the sertão's word for the rainy season" aparece na legenda do primeiro segundo.

---

## 12. Mapa de prêmios-alvo e critérios de julgamento

### 12.1 Prêmios

| Prêmio | Prioridade | O que o sustenta |
|---|---|---|
| **Best Use of Science** | 1ª | As três curvas validadas por ano; comparações só pareadas; IBGE como árbitro; resultados negativos declarados (2016, Quixadá 2023–2025); recibo A–D com marca ·T. |
| **Best Storytelling** | 2ª | São José testado com respeito; replay de 1998 com a decisão mudando; 2027 ao vivo; Dona Francisca. |
| **Local Impact** | 3ª | Ceará, 184 municípios, técnico no circuito, ações baratas em novembro, maniva e semente de caupi; validação com um técnico de ATER (se feita). |
| **Best Use of Data** | 4ª | Mais de dez bases NASA, cada uma numa decisão; o sentinela de deriva; o relato copiado no PAM como camada de qualidade; 42 anos de açudes no Landsat. |
| **Galactic Impact** | Indicação | Motor global; janela sintética em qualquer ponto; "40 de 47 pontos terrestres tropicais sem mês de quebra térmica". |
| Best Use of Technology | Não é alvo | O app estático é simples de propósito. Se for avaliado, o argumento é o verificador e a ausência de API em tempo de execução. |

### 12.2 Critérios (notas de 1 a 5)

| Critério | Como atendemos | Risco e mitigação |
|---|---|---|
| **Impacto** | Decisão real de uma família numa data real (2027); métrica do ano ruim; ações baratas já em novembro; canal pelo extensionista. | Família fictícia. Mitigação: 1 conversa real com ATER e 1 mudança feita por causa dela, no slide 7. |
| **Criatividade** | Calendário derivado de três curvas; rotação como política em 3 anos; São José; entressafra como portão; honestidade como funcionalidade. | O júri pode ler como diversificação. Mitigação: cada estratégia como sequência 2027–2029 e a frase do slide 3. |
| **Validade** | Definição canônica única; comparações pareadas; validação por ano; recibo; auditoria; onde erramos. | Habilidade regional e poucos episódios. Mitigação: a tela diz "seu município / sua região" e mostra o placar local com os erros. |
| **Relevância (NASA no núcleo)** | Portões e replay são IMERG; o balde é IMERG + POWER; a memória é GRACE + Landsat; o fogo é VIIRS; o relevo é SRTM; o futuro é NEX-GDDP. | O ONI é da NOAA e o árbitro é o IBGE. Mitigação: o ONI só repondera os anos do replay NASA; o IBGE só confere. SMAP entra se chegar. |
| **Apresentação** | Uma imagem (as três curvas), uma decisão (1998), três telas; no máximo 3 números no vídeo. | Excesso de conteúdo. Mitigação: a auditoria fica fora das telas, como link. |

### 12.3 Texto curto "How we used SI" (para a submissão)

Ver "Use of SI (AI) tools", no fim deste documento.

---

## 13. O que a banca questionou e como respondemos

Notas da banca ao rascunho v1, de 1 a 5:

| Revisor | Impacto | Criatividade | Validade | Relevância NASA | Apresentação |
|---|---|---|---|---|---|
| Juiz da Space Apps | 3,5 | 4 | 3,5 | 4 | 3 |
| Cético científico | 4 | 4 | 2,5 | 3,5 | 3 |
| Engenheiro de viabilidade | 4 | 4 | 3 | 4 | 3 |

Todos os problemas de gravidade alta e média estão abaixo, agrupados quando dois revisores apontaram o mesmo. "J" é o juiz, "C" o cético e "E" o engenheiro.

| # | Crítica (quem, gravidade) | Resposta |
|---|---|---|
| 1 | O "3×" da demo de Quixadá (0,35 contra 0,10) usa área colhida, exclui as perdas totais e cai em 2016; em 2012 não havia mandioca (J alta, E alta, C alta) | **Cortado.** Entram a carteira estadual canônica (0,15 → 0,36, agora com IC90 por ano) e o observado de Quixadá em 1998 (milho 0,00; feijão 0,16; mandioca 0,50; carteira 0,22). |
| 2 | O replay de 2012 mostra um alerta tarde demais; não mostra decisão mudando (J alta) | **Replay principal trocado para 1998**, o análogo de El Niño. O alerta acende em Quixadá em 19/mar (70%), antes da data-limite do caupi (21/mar). Esta conta foi refeita com o normal sem o próprio ano. 2012 fica como "pego tarde"; 2016 vai para a auditoria como erro. A frase é "switch window opened", não "harvest rescued". O engenheiro sugeriu 2016 em Quixadá ou 2012 em Tauá; preferimos 1998, que é calculável (Quixadá tinha 600 ha de mandioca) e amarra P1, P3 e 2027. |
| 3 | Linhas de base escolhidas a dedo: R² 0,365 contra 0,102; 0,794 contra 0,727; "small beats big" (J alta, C alta, E alta e média) | **Só comparações pareadas:** ρ dentro do ano 0,155 → 0,307 e AUC 0,816 → 0,851 com o HGB só de chuva; monotônico contra livre com as mesmas entradas, +0,03 no milho e nada no feijão; ISNA soma ~+0,04 no milho e piora o feijão. "Small beats big" sai. A AUC 0,851 é rotulada como fim de safra. |
| 4 | "On your land" promete mais do que a habilidade entrega (J alta) | Tagline trocada para "over your county". A tela diz "seu município / sua região" e mostra o placar local. |
| 5 | "Em janeiro ninguém sabe" contradiz o P1, que se apoia no ONI (C alta) | Curva refeita com duas linhas: chuva NASA (0,57 → 0,80) e oceano (0,67 desde novembro). A frase passa a ser "rain-to-date says almost nothing; the ocean says a little". |
| 6 | OR 2,30 do El Niño: era um termo de interação, com EP iid; com EP por ano, OR 1,57 e p = 0,27 (C alta) | **Cortado.** Entra a contagem: 3 dos 6 El Niños desde 1998 viraram catástrofe e 3 passaram. Grau B. Toda variável anual passa a ter EP agrupado por ano. |
| 7 | Oito números de cabeçalho com cinco definições de quebra (C alta) | Tabela 9.2 refeita com a definição canônica e uma regra de alerta. Recalculados por nós: curva, alerta, carteira e possibilidade. Os números de outras definições estão proibidos no deck. |
| 8 | M2: melhor de 14 configurações escolhida no teste; alvo não canônico; fim de safra (C alta) | Faixa das 14 (0,78–0,85) reportada; rótulo de fim de safra; seleção aninhada no bloco 0; o observado do replay usa sempre a razão canônica. |
| 9 | O teste de São José é injusto: compara com a quadra inteira, não com o resto dela (C alta) | Reescrito com o teste justo: a chuva do dia e o acumulado dizem o mesmo sobre o resto (ρ +0,32 nos dois). "A tradição é fraca, não errada." A AUC 0,73 fica só como estado do roçado. |
| 10 | Análogos com falsa precisão: "5 a 7 em 10" (J média, C alta) | Agora é contagem: 4 de 7, contra 1 em 3 normalmente, com a faixa de 2 a 9 em 10. Mostra o limiar, o n e marca 1966 como proxy. |
| 11 | GRACE "caindo para p35" é um mês dentro do ruído (C alta; J média pediu o GRACE no painel) | Sai de "por que agora" e do P1 como alarme. No painel "hoje", entra como "banco regional normal (p57, média de jul–set)". Atende o juiz (GRACE no painel) sem o alarme falso. |
| 12 | Fogo: área de pixel tratada como área queimada; intervalo de 3 anos por célula e censurado (C alta) | Reescrito: "17% da área em células com ≥ 1 foco"; área pelo MapBiomas (12,7% da Caatinga em 39 anos). O intervalo de retorno vira grau C e sai do pitch. A ligação direta com Primo sai. |
| 13 | Mandioca como amortecedor apoiada em relato copiado (C alta; J baixa) | Carteira refeita sem os anos repetidos: 0,14 → 0,34, o ganho resiste. Grau A no estado e B no município. Maniva vira risco nº 1, com "plantar no ano anterior". O relato copiado vira camada do M6. Um motor de carteira só. |
| 14 | O balde M1 não vê 1998; a errata da ET0 estava invertida (J média, C média) | Errata corrigida: os dois valores estão certos, cada um pela sua fonte. ZARC sintético refeito com ET0 × 0,87: as datas andam no máximo 1 decêndio em 97–99% dos municípios, então o cartão mostra ±1 decêndio. Nos slides, "ET0 exceeds rain in 10 of 12 months". O risco de 2027 vem do M3/ONI, não do balde. |
| 15 | Relevância NASA mais fraca do que o slide sugere; SMAP e ECOSTRESS sem dado em disco (J média, E alta) | Rótulos "used / pipeline ready / roadmap". O ECOSTRESS sai do P4. O replay mostra a estimativa NASA contra o IBGE. O SMAP entra com recibo se chegar até sáb 20h. No painel "hoje" ficam o ONI, o GRACE e o açude do Landsat, e o IMERG Late como contexto. |
| 16 | Parece diversificação, não rotação (J média) | Cada estratégia é uma sequência 2027–2029 com a entressafra; a S2 vira faixas que giram; nenhuma alternativa queima. |
| 17 | Escopo grande demais para ~38 h; empacotar scripts é uma armadilha (J média, E alta) | MVP de 3 telas e cerca de 27 horas-pessoa. Exportador que lê as saídas salvas, sem importar scripts. Números congelados no sáb 22h, sono das 02h às 08h, app congelado no dom 08h. O verificador sai da lista "nunca cortar". |
| 18 | "O alerta" tem quatro definições (J média, C média) | Uma regra só (< 75% do normal desde 1/jan), com todos os números refeitos e o n ao lado. O "011" sai do pitch. |
| 19 | Proveniência imprecisa: "28 anos de GPM"; reanálise chamada de observação; deriva da LST "descoberta" (J média, C média e baixa) | "IMERG (TRMM + GPM eras), 1998–2025"; o POWER é marcado como reanálise; a frase da deriva diz que ela é documentada pela NASA. |
| 20 | Falta validação com usuário real (J média) | Tarefa do José até sáb 18h: 1 conversa com ATER ou com um agricultor, 1 frase com permissão e 1 mudança feita, no slide 7. Agentes não fazem esse contato. |
| 21 | Conformal compra cobertura com largura (C média) | A largura é reportada (227 → 282 p.p. no pré-safra), com a frase "em janeiro a incerteza honesta é do tamanho da climatologia". |
| 22 | NDVI "+0,053" listado como deriva pega; "metade da tendência do fogo"; viés sem unidade (C média) | Rotulado como "deslocamento não explicado". A atribuição do fogo sai. O viés ganha unidade (~60 pontos de rendimento relativo). |
| 23 | Oceano "decide o quando e o quanto" exagera (C média) | Sai do pitch. Na auditoria: "o Pacífico informa mais sobre a quebra do que sobre o tercil de chuva (exploratório; depende de 3 anos)". |
| 24 | Portão de habilidade de novembro com n = 10 (C média) | Mostrado com o n e só como argumento qualitativo. |
| 25 | Graus mal atribuídos (C média) | Criada a marca ·T. ZARC sintético passa para C; Diniz e Souza para C (ensaio único); Silva 2009 para D (sai); carbono da S3 por Primo (C), não por Jian; Kallenberg descrito corretamente. |
| 26 | 0,78 milho × feijão: "independentes" e "três especialistas confirmaram" (C média) | "No registro do PAM, quebram juntos", com 0,67 sem o choque do ano e a ressalva do relato. As duas frases saem. |
| 27 | "86% dos trópicos" inclui um ponto no oceano (C média) | "40 de 47 pontos terrestres tropicais amostrados". |
| 28 | Explicador LLM em tempo de execução; saldo da API acabou; TTS depende de serviço (E alta) | Textos redigidos offline e congelados, verificador regex, nenhuma API em execução. Áudio só com voz humana gravada até sáb 18h; senão, sai. |
| 29 | Os 4 cartões "divergem dia a dia" sem estado diário para todas as estratégias (E alta) | Animam a chuva IMERG e as barras de ISNA por cultura (C); o PAM é revelado na colheita (A); a S3 fica hachurada. |
| 30 | "81% de 131" não é a S2 (E média) | A S2 cita só a carteira 1/3; o 81% vai para a auditoria como "diversificação em geral". |
| 31 | Modo global sem dados nem calibração (E média) | 2 pontos baixados hoje em segundo plano, grau C, "pontos pré-calculados; qualquer ponto na próxima versão". A calibração inversa fora do Brasil vai para o roteiro. |
| 32 | "Meu chão" só existe em 4 AOIs (E média) | O código de barras vira figura estática de 1 AOI; nos 184 municípios, PAM + 1 pergunta. O selo de visibilidade mostra o n e o valor antes de 2015. |
| 33 | ZARC oficial e Garantia-Safra usados como restrição dura sem conferência (E média; J baixa) | "Janela sintética tipo-ZARC", com "confirmar no ZARC oficial". O Garantia-Safra só entra se o José conferir na lei até sáb 14h. |
| 34 | Replay em 44 temporadas, blocos plurianuais com estado e Pareto em 8 eixos exigem código novo (E média) | Só as 28 quadras do IMERG; as sequências de 3 anos são planos, com prior da literatura para o antecessor, sem estado simulado; 3 eixos calculados e etiquetas com grau. |
| 35 | Regras da Space Apps sobre trabalho anterior não conferidas (E média) | Tarefa do José hoje de manhã. Se houver restrição, a submissão separa a preparação prévia do que foi construído no fim de semana. |

**Baixa gravidade, também resolvidos:**
- IMERG Late saiu de "por que agora", e a unidade foi anotada (C).
- O selo de 92% agora traz o n (C).
- O açude passou a ser "dois sensores e um modelo, numa AOI" (C).
- O verificador ganhou gabarito, léxico proibido e 30 casos adversariais (C).
- O replay de Quixadá em 2023–2025 foi rodado e vai para a auditoria (C).
- "QUADRA" ganhou glosa na primeira menção (J).
- O IMERG Late municipal foi rotulado como estadual (E).
- FIRMS NRT, LSPA, CDL e o simulador de WhatsApp foram cortados; o pré-registro só sai com o OK do José; o mapa usa o GeoJSON sem tiles (E).

**Onde não seguimos a banca, e por quê:**
- **Replay de 2016 ou de Tauá (E):** preferimos 1998. Ver o item 2.
- **IMERG Late com "−0,5 dp" no painel "hoje" (J):** entra como contexto de frescor dos dados, com a frase "isso não prevê a quadra (ρ −0,06)". O dado do cético mostra que a chuva da estação seca não informa a quadra.
- **Grau B/C para toda a mandioca (C):** mantivemos o grau A para o resultado estadual, porque ele resiste à retirada dos anos repetidos, com IC por ano. O nível do município fica em B.

---

## Anexo A. Decisões em aberto para a equipe (exigem pessoa, não agente)

1. Tamanho da equipe e divisão dos papéis P1–P4, **até as 10h de sábado**.
2. Nome final: QUADRA (recomendado) ou a reserva Field Replay.
3. Ler o regulamento sobre trabalho anterior ao evento e o formato da declaração de uso de IA.
4. Conferir na lei o limiar, a cesta e a área mínima do Garantia-Safra, e a janela do ZARC oficial de Quixadá, **até sáb 14h**.
5. **Uma conversa com um técnico de ATER** (Ematerce, sindicato rural ou ONG da ASA) **ou com um agricultor**, até sáb 18h, com permissão para citar 1 frase.
6. Publicar ou não o hash do pré-registro de 2027 (voz pública).
7. Gravar ou não 45 s de voz humana em português para o cartão (até sáb 18h).
8. Confirmar se fatos do "Encontro dos Profetas da Chuva" de Quixadá podem ser citados no slide 1.

---

## Project summary (English)

QUADRA (the sertão's word for the rainy season) is a decision-support tool that lets farmers and extension agents stress-test rotation plans against NASA's record before committing. In semi-arid regions with a single rainy window, a rotation is not a fixed crop sequence but a policy with checkpoints. QUADRA places those checkpoints where three measured curves cross. The first is what the data already know: the skill of IMERG rain-to-date for county-level crop failure, validated by leaving whole years out, rises from AUC 0.57 in January to 0.80 by April 30, while the ocean gives 0.67 from November. The second is what is still possible: planting deadlines from an FAO-56 water balance driven by IMERG and NASA POWER. The third is when Landsat and Sentinel-2 can actually see the ground.

For each county, QUADRA compares the current practice with three alternative three-year strategies, replays them over every rainy season in the IMERG record (TRMM and GPM eras, 1998–2025), and ranks them by their worst years. Observed yields from Brazil's IBGE act as referee. Every number carries a receipt (NASA source, scale, validation, A–D evidence grade), and an audit page shows where the tool fails.

In Ceará, Brazil, corn and beans fail together; across 2,495 county-years, a third of the area in cassava raised the worst-decile harvest from 15% to 36% of normal. Replaying 1998, the closest analog to today's record El Niño, the March 19 checkpoint flagged rain at 70% of normal over Quixadá two days before the cowpea deadline. GRACE, MODIS/VIIRS, SRTM and NEX-GDDP add water memory, fire, terrain and 2050 heat. The engine is global; the demo is Ceará. NASA evidence. The farmer decides.

## Use of SI (AI) tools

Inside the product, SI appears in five places:
1. A physics-guided, monotonic risk emulator (FAO-56 water balance plus gradient boosting). It is trained on 184 municipalities × 28 years and validated by leaving whole years out. Its intervals are year-robust conformal intervals, and their width is reported.
2. Checkpoint forecasts whose skill is measured without look-ahead, with an out-of-distribution warning for this year's record El Niño.
3. An exact search over rotation strategies that ranks them by tail risk (CVaR) instead of average yield.
4. A drift and data-quality sentinel that downgrades evidence automatically. It flagged Terra's documented orbit drift in land surface temperature and copied year-to-year yield reports.
5. A large language model that only drafts the text on each card. It works offline from the engine's numbers, and a deterministic checker blocks any number, attribution or certainty word that the engine did not produce.

To build QUADRA, the team used Anthropic's Claude (Claude Code) as a coding and analysis assistant. This included a council of AI agents that proposed, debated and adversarially reviewed designs. Every reported number comes from a script in the project repository that a person can rerun. No model was trained on LLM outputs, and no LLM is called at run time.
