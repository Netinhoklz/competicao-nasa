# Ata do conselho: como nasceu a proposta QUADRA

- **Data:** sábado, 14/11/2026. Os horários vêm do `date` da máquina e dos carimbos dos arquivos.
- **Pedido do José:** 10 agentes analisam os dados do estudo estatístico e debatem entre si para chegar a uma proposta inovadora, baseada em artigos e em dados, com IA em vários métodos, para o desafio "Field Shift" da NASA Space Apps 2026.
- **Produto final:** `proposta/PROPOSTA_FINAL.md`. Esta ata registra o processo.

## 1. Cronologia

| Etapa | Quando | O que saiu |
|---|---|---|
| Rodada 1: propostas individuais | ~08:05–08:30 | 10 propostas, cada uma com scripts de análise em `conselho/analises/` |
| Rodada 2: debate, checagens cruzadas, votos e notas | ~08:30–08:45 | Pareceres, checagens `*_r2_*` e `*_debate_*`, placar e votos de conceito |
| Rascunho v1 (arquiteto-chefe) | 08:46 | `proposta/rascunho_v1.md` e `arquiteto_numeros_canonicos.py` |
| Rodada 3: banca adversária | ~08:55–09:10 | Pareceres do juiz, do cético e do engenheiro, com checagens novas (`juiz_*`, `cetico_r3_*`, `viabilidade_*`) |
| Versão final (arquiteto-chefe) | 09:15–09:40 | `PROPOSTA_FINAL.md`, esta ata e três checagens novas (`arquiteto_final_*`) |

## 2. Quem era cada especialista

| # | Especialista | Ótica |
|---|---|---|
| 1 | Agrônomo do semiárido | Calendário agrícola, balde FAO-56, ZARC, regras de semeadura, consórcio e revezamento |
| 2 | Cientista do clima e previsão sazonal | ENSO e Atlântico, habilidade progressiva, valor da decisão |
| 3 | Hidrólogo e especialista em balanço hídrico | Água verde e azul, GRACE, GLDAS, açudes, salvamento |
| 4 | Especialista em sensoriamento remoto e modelos de fundação | HLS, SAR, fenologia, irrigação, Prithvi/Presto, downscaling do SMAP, TVDI |
| 5 | Pesquisador de IA e aprendizado de máquina | Emuladores, validação por ano, conformal, busca de política |
| 6 | Ecólogo de pragas, paisagem e fogo | Graus-dia, hospedeiros, focos VIIRS, pousio, carbono |
| 7 | Economista agrícola e de risco | Carteira, CVaR, hedge natural, Garantia-Safra, valor da informação |
| 8 | Designer de produto centrado no agricultor | Voz, WhatsApp, offline, frequências naturais, técnico no circuito |
| 9 | Estrategista de competição (ex-juiz do Space Apps) | Critérios, prêmios, narrativa, momento uau |
| 10 | Cético científico e engenheiro de viabilidade | Vazamento, deriva de sensores, unidade de inferência, escopo |
| — | Arquiteto-chefe | Fusão das propostas, folha de números canônicos, rascunho e versão final |
| — | Banca adversária (3) | Juiz da NASA Space Apps; cético científico; engenheiro de viabilidade |

## 3. As propostas da rodada 1

| Especialista | Proposta | Em duas linhas |
|---|---|---|
| Agrônomo | **Playbook do Roçado** (Field Playbook) | Em vez de uma sequência fixa, entrega 5 momentos de decisão no ano. Cada um tem um gatilho medido pela NASA e uma jogada testada contra 28 anos de safras reais dos 184 municípios do Ceará. |
| Clima | **ShiftCast** (Adaptive Rotation Pathways) | Diz quando decidir, além do que plantar. Junta o oceano, o IMERG e o SMAP num mapa de caminhos com gatilhos, mostrando quantas quebras teria evitado e quantos alarmes falsos teria dado. |
| Hidrólogo | **Extrato d'Água** (WaterLedger) | Toda rotação tem uma conta de água. Mostra quem a paga (chuva, solo ou o banco lento de aquíferos e açudes) e quanto risco sobra. |
| Sensoriamento remoto | **FieldMemory** (Memória do Talhão) | Reconstrói o "código de barras" do talhão (plantio, solo nu, fogo, irrigação) com HLS, radar, SMAP e GRACE, mesmo sob nuvem. Com essa memória, compara 3 ou mais rotações. |
| Pesquisador de IA | **SeasonReplay** | Prever a quadra quase não funciona. Reencena as 28 quadras do IMERG e as de 2050 (NEX-GDDP) no talhão e mostra qual rotação aguenta o pior ano, com incerteza honesta. |
| Ecólogo | **CycleBreak** (Quebra-Ciclo) | Onde não há inverno, só a rotação quebra os ciclos. Mostra quantas gerações de praga cada estratégia alimenta, quanto conecta a paisagem de hospedeiros e quanto carbono queima. |
| Economista | **CropFolio** | Trata cada rotação como uma carteira de investimentos e a testa contra 28 anos de chuva, o El Niño e o preço do adubo de hoje. Entrega um "prospecto" com a renda do ano ruim e quem cobre o risco. |
| Designer | **Compadre** | Um conselheiro de roçado por voz no WhatsApp, junto com o técnico de campo. Fala nos momentos em que o dado sabe algo e aprende com o pluviômetro e o veredito de cada família. |
| Estrategista | **PROFETA** (reservas: QUADRA, Field Replay) | Transforma 28 anos de satélite num calendário vivo de decisões (novembro, janeiro, São José, abril). Em cada ponto, compara 3 ou mais rotações pelo risco de perder a safra. |
| Cético e viabilidade | **FieldProof** ("Roçado com Recibo") | Compara pelo menos 3 rotações com dados NASA. Cada número tem recibo: de qual missão saiu, em que escala vale, como foi validado sem olhar o futuro e o que conferir no chão. |

## 4. Placar da rodada 2

Cada especialista deu nota de 0 a 10 às outras nove propostas e à própria.

- **Consolidação:** no placar bruto, a mesma proposta aparece com rótulos diferentes (por exemplo, "Designer de produto (Compadre)" e "Designer centrado no agricultor (Compadre)"). Juntamos os rótulos e tiramos a média ponderada pelos votos. Cada proposta recebeu exatamente 9 votos externos.
- **Correção:** o rascunho v1 atribuía 8,3 ao CropFolio. Esse valor era só de uma linha com 2 votos; a média dos 9 votos é 7,9.

| Posição | Proposta (especialista) | Média externa (9 votos) | Autoavaliação |
|---|---|---|---|
| 1 | Playbook do Roçado (agrônomo) | **8,4** | 8,0 |
| 2 | SeasonReplay (pesquisador de IA) | 8,3 | 7,0 |
| 2 | FieldProof (cético) | 8,3 (8 × 8,3 + 1 × 8,5) | 7,0 |
| 4 | PROFETA (estrategista) | 8,1 | 7,0 |
| 5 | CropFolio (economista) | 7,9 (2 × 8,3 + 7 × 7,8) | 7,0 |
| 5 | ShiftCast (clima) | 7,9 | 7,0 |
| 7 | Compadre (designer) | 7,5 (1 × 8,0 + 2 × 7,8 + 6 × 7,3) | 7,0 |
| 8 | Extrato d'Água (hidrólogo) | 7,4 (1 × 8,0 + 2 × 7,8 + 6 × 7,2) | 7,0 |
| 9 | FieldMemory (sensoriamento remoto) | 6,2 | 6,0 |
| 10 | CycleBreak (ecólogo) | 6,1 | 6,0 |

**Leitura:** as quatro primeiras ficaram empatadas na prática (8,1 a 8,4). O que derrubou FieldMemory e CycleBreak foi a viabilidade em 36 h (Prithvi, SAR, GNN de pragas), não a ideia. As duas viraram peças da proposta final: o selo de visibilidade e o portão de entressafra.

## 5. Votos de conceito central (rodada 2)

**Unanimidade (10 de 10):** a rotação deixa de ser uma sequência fixa e vira uma política com portões ao longo da quadra. Cada estratégia é reencenada nas quadras do registro NASA, ordenada pelo pior ano e entregue com recibo de evidência.

Cada voto trouxe uma ênfase própria:

| Especialista | Nome votado | Ênfase que trouxe ao conceito |
|---|---|---|
| Agrônomo | Plano Vivo do Roçado / Field Playbook | Os portões têm de respeitar o calendário agronômico: depois da data-limite, só salvamento. |
| Clima | (sem nome) "NASA diz quando há sinal" | O portão só abre onde há habilidade comprovada; o alvo do oceano é a quebra, não o tercil. |
| Hidrólogo | Field Playbook | Dois relógios da água: o rápido decide o quê plantar; o lento decide quanta água azul gastar. |
| Sensoriamento remoto | (frase de pitch) | Selo de visibilidade por portão; o satélite só entra quando de fato vê. |
| Pesquisador de IA | Field Playbook / Playbook do Roçado | Física + ML monotônico, conformal por ano, seleção aninhada; RL e GNN ficam como roteiro. |
| Ecólogo | Field Playbook / Roçado com Recibo | O portão de entressafra: combustível, fogo, pousio e janela sem hospedeiro. |
| Economista | "Plano vivo ranqueado pela cauda" | Perde-se no ano ruim, não na média; a previsão vale pouco em R$, a composição mexe na cauda. |
| Designer | **QUADRA** | Técnico no circuito, frequências naturais, a família dá os pesos e pode vetar. |
| Estrategista | **QUADRA** (reserva Field Replay) | Retirou o próprio PROFETA: promete certeza e arrisca apropriar os profetas da chuva. |
| Cético e viabilidade | **QUADRA** | Escala declarada: o dado acerta o nível do ano; o talhão fecha com o agricultor. |

**Nome:**
- QUADRA teve 3 votos explícitos; Field Playbook, 4 (como nome de trabalho); 3 votos não indicaram nome.
- O arquiteto escolheu **QUADRA** como nome, com **Field Playbook** como subtítulo. A palavra é local, curta, pronunciável em inglês e não promete certeza.
- A banca pediu a glosa *"the sertão's word for the rainy season"* na primeira menção.

## 6. Notas da banca adversária ao rascunho v1 (1 a 5)

| Revisor | Impacto | Criatividade | Validade | Relevância NASA | Apresentação | Média |
|---|---|---|---|---|---|---|
| Juiz da NASA Space Apps | 3,5 | 4 | 3,5 | 4 | 3 | 3,6 |
| Cético científico | 4 | 4 | 2,5 | 3,5 | 3 | 3,4 |
| Engenheiro de viabilidade | 4 | 4 | 3 | 4 | 3 | 3,6 |

**Veredito comum:** o conceito é forte e raro, mas cerca de 10 números de vitrine não sobreviviam a um juiz atento, e o escopo não cabia no relógio. A versão final responde a todas as 35 críticas de gravidade alta e média (seção 13 da proposta).

## 7. Principais divergências e como foram resolvidas

| # | Divergência | Lados | Como foi resolvida |
|---|---|---|---|
| 1 | Prever ou decidir em portões? | Clima: há sinal no oceano em novembro. IA e estrategista: "em janeiro ninguém sabe". Cético (banca): o ONI tem AUC 0,67 já em novembro. | A curva mostra as duas linhas. A chuva NASA vai de 0,57 a 0,80; o oceano fica em 0,67 desde novembro; elas se cruzam no fim de fevereiro. A frase virou "rain-to-date says almost nothing; the ocean says a little". |
| 2 | O El Niño "dobra a quebra além da chuva"? | Agrônomo e clima: OR 2,30. Cético: com EP agrupado por ano, OR 1,57 e p = 0,27. | Sai o OR. Entra a contagem honesta: 3 dos 6 El Niños desde 1998 viraram catástrofe. Grau B. |
| 3 | O banco de água está caindo? | Hidrólogo e estrategista: GRACE p72 → p35. Cético: a queda de um mês está dentro do ruído; a média de jul–set está no p57. | Vale a regra do próprio hidrólogo (média de 3 meses): "banco regional normal". |
| 4 | Qual ano no replay? | Estrategista: 2012. Engenheiro: 2016 em Quixadá ou 2012 em Tauá. Juiz: 1998. | 1998 em Quixadá: é o análogo de El Niño, é calculável (havia mandioca) e mostra a decisão mudando em São José. 2012 fica como "pego tarde"; 2016 vai para a auditoria. |
| 5 | São José | Estrategista: o dia vale AUC 0,53 e o acumulado 0,72. Cético: o teste justo é contra o resto da quadra, e aí empatam (ρ +0,32). | O teste justo vai para o slide 1: "a tradição é fraca, não errada; o que decide é a água no solo". |
| 6 | Qual carteira? | Economista: mínimo CVaR (81% de 131). IA: outra métrica (62% de 58). Estrategista: 1/3 de cada. Juiz: o "3×" de Quixadá exclui as perdas totais. | Um motor só: a carteira 1/3 com a definição canônica (0,15 → 0,36, com IC por ano). O mínimo CVaR vai para a auditoria. O "3×" sai. |
| 7 | Mandioca como amortecedor | Economista e IA: sim, grau A. Cético: relato copiado, grau B/C. | Refeito sem os anos repetidos e o ganho resiste (0,14 → 0,34). Grau A no estado, B no município. Maniva vira risco nº 1; a mandioca precisa ser plantada no ano anterior. |
| 8 | "Física vence ML livre" | Hidrólogo: 0,794 contra 0,727. Cético e engenheiro: comparação com entradas diferentes. | Só comparações pareadas: +0,03 da restrição monotônica no milho e nada no feijão. "Small beats big" sai. |
| 9 | Dois baldes | Agrônomo (milho, caupi, sorgo) e hidrólogo (milho, feijão, sorgo, mandioca). | Um balde por tipo de número, declarado no recibo. "Independentes" sai, porque usam os mesmos dados. |
| 10 | Escala: talhão ou município? | Designer e sensoriamento remoto: "seu chão". Cético e juiz: dentro do ano, a AUC é ≤ 0,57. | Tagline "over your county". A tela mostra o placar do alerta no município, com os erros. |
| 11 | O que é "rotação" | Júri pode ler como diversificação (juiz). | Cada estratégia vira uma sequência 2027–2029 com entressafra; a S2 vira faixas que giram. |
| 12 | Escopo | Designer: voz, WhatsApp, painel PWA. Sensoriamento remoto: código de barras ao vivo. Engenheiro: ~85 h-pessoa não cabem. | MVP de 3 telas e ~27 h-pessoa. Voz, WhatsApp, código de barras ao vivo e modo global ao vivo vão para o roteiro. |
| 13 | LLM em tempo de execução | Todos: explicador com RAG. Engenheiro: o saldo da API acabou em 12/11. | Textos redigidos offline e congelados, com verificador regex. Nenhuma API em execução. |
| 14 | 28 ou 44 quadras | Clima: 44 com o POWER, para incluir 1983. Cético: a chuva do POWER antes do IMERG é reanálise. | O replay usa as 28 do IMERG (eras TRMM e GPM). O POWER fica como contexto climatológico. |
| 15 | Fogo | Ecólogo: "17,4% queimou; volta a cada 3 anos". Cético: área de pixel não é área queimada. | "17% da área em células com ≥ 1 foco"; área pelo MapBiomas Fogo. O intervalo de retorno vira grau C. |

## 8. Ideias soltas que ficaram para o futuro

**Agrônomo**
- Gatilho do Garantia-Safra pelo ISNA: a fração de municípios com ISNA < 0,5 tem r = +0,68 com a fração em quebra.
- Planejamento das casas de sementes: prever em dezembro quantos municípios vão trocar milho por caupi ou sorgo.
- Previsão da castanha de caju pela quadra (ρ +0,50).
- Balde dual FAO-56 para o consórcio, com competição por água.
- Mapa público de datas-limite para a Ematerce.

**Clima**
- Mapa-múndi de habilidade sazonal por pixel ("onde a previsão vale a pena").
- NASA GEOS-S2S como preditor (acesso a confirmar).
- Veranico subsazonal com MJO.
- Modelo de sobrevivência para a duração do veranico.
- A exceção de 2024 (Atlântico inteiro recorde de quente) como interação ONI × TSA.

**Hidrólogo**
- "Açude virtual" do barreiro, com área de contribuição do NASADEM, escoamento do IMERG e evaporação da ET0.
- Mapa global da memória hídrica (τ) por mascon do GRACE.
- Separador clima × uso nos hotspots do GRACE.
- ESI do ECOSTRESS como gatilho de salvamento.
- EnKF com o NISAR.

**Sensoriamento remoto**
- Código de barras do talhão como certificado de prática (sem queima, com cobertura) para crédito ou pagamento por serviço ambiental.
- Classe própria para a palma forrageira.
- Índice de exposição à erosão (dias de solo nu × I30 × declive).
- Monitor global de visibilidade por sensor.
- Prithvi-EO-2.0 ajustado no HLS da Caatinga.

**Pesquisador de IA**
- Efeito causal da rotação nos EUA (CDL × HLS, diferenças em diferenças) como prior empírico para o Brasil.
- Aprendizado a partir de proporções do PAM para classificar culturas no HLS.
- Valor de opção real da mandioca como "estoque vivo".
- Carteiras cooperativas entre regiões pouco correlacionadas.
- Modo do técnico: ranquear onde a visita de campo vale mais.

**Ecólogo**
- Validação do fogo de out–dez/2026 com o FIRMS NRT (exige chave).
- MapBiomas Fogo no relógio do pousio.
- Hubs do grafo de hospedeiros para posicionar armadilhas.
- Animação do aglomerado de algodão de 1974–1995 como abertura ("the landscape was a bridge").

**Economista**
- Valor da informação NASA em R$/ha, que exige custos de produção.
- Microsseguro cooperativo para a faixa de perdas de 25–40%.
- Escore de resiliência da rotação para o crédito do PRONAF ou do BNB.
- Teto de participação pelo PNAE/FNDE.
- Algodão agroecológico como opção de alto risco, saída da proposta porque a única fonte é resumo de congresso.

**Designer**
- Boletim de rádio comunitária por microrregião.
- Placar público de confiança por município.
- Pluviômetro de garrafa PET com leitura por foto.
- Balanço da cisterna (água de beber × água de produção).
- Personas globais do mesmo motor (por exemplo, "Jirani").
- Leilão de forragem entre comunidades em anos sincronizados.

**Estrategista**
- Módulo "Meus sinais": o agricultor registra indícios e a ferramenta os pontua contra o IMERG.
- Cartão-postal Landsat do talhão em 1998, 2012 e 2016.
- O que a perda das casas de farinha fez com a resiliência de Quixadá.
- Calendário de portões gerado automaticamente para qualquer pixel.

**Cético e viabilidade**
- Validação deixando o episódio de seca de fora como padrão.
- Pré-registro com hash da faixa de 2027 (decisão do José).
- Troca da "verdade de campo" MODIS pelo VIIRS VNP13.
- Tabela de frescor dos dados.
- O grau A–D como camada do mapa global.
- O relato copiado no PAM como produto de qualidade de dado.

## 9. Checagens novas da versão final (arquiteto-chefe)

Todas são só leitura e ficam em `conselho/analises/`.

**`arquiteto_final_curvas_quixada.py` → `.saida.txt`**
- Curva de habilidade canônica: chuva 0,57 → 0,80; oceano 0,67; dentro do ano ≤ 0,57.
- Regra única de alerta: em 30/abr, 5,2 contra 1,5 quebras em 10.
- Curva de possibilidade: milho 93% → 42% → 0%; caupi 98% em 19/mar.
- Replay de Quixadá ano a ano:
  - 1998: 70% do normal em 19/mar;
  - 2012: 75%, só acima do gatilho;
  - 2016: o alerta nunca acende;
  - placar local fraco: 2 acertos em 8 alertas em 19/mar.
- ET0 supera a chuva em 10 de 12 meses, no POWER e no ERA5.
- 40 de 47 pontos terrestres tropicais sem mês de quebra térmica.

**`arquiteto_final_carteira_ic.py` → `.saida.txt`**
- Carteira 1/3: CVaR10 0,15 → 0,36, com ganho de +0,17 a +0,23 (IC90 por ano).
- A cauda vem de 1998, 2010, 2012, 2013 e 2016.

**`arquiteto_final_zarc_et0_sensibilidade.py` → `.saida.txt`**
- Com a ET0 na escala do ERA5, as datas-limite andam no máximo 1 decêndio em 97–99% dos municípios.
- Em Quixadá: milho 01/mar e caupi 21/mar não mudam; sorgo vai de 11/mar para 21/mar.
