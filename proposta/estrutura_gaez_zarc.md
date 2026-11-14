# QUADRA sobre GAEZ v4 + ZARC: estrutura da solução

*Rascunho de estrutura, 14/11/2026. Base: estudo das bases (notebooks), catálogo de rotações, análogos climáticos e
viabilidade dos artigos do Nordeste.*

*Atualizado em 14/11/2026 (tarde) com a revisão de 10 agentes do protótipo (`protótipo/REVISAO_10_AGENTES.md`): classes
oficiais do GAEZ v4 e corte "apta" > 40; no ZARC, só os ciclos com cultivar indicada, janela até o fim do decêndio e
duas datas no aviso; números recontados. **O protótipo agora cobre os 1.794 municípios do Nordeste**, com a mesma regra
(`scripts/preparar_prototipo_nordeste.py`; tábua em `E:/campeonato-nasa/dados/gaez_zarc/nordeste_2026-2027.csv`). Os
exemplos e as contagens abaixo continuam sendo do CE.*

## 1. A ideia em uma frase

O **GAEZ** diz *o que cabe* no lugar. O **ZARC** diz *quando plantar e com que risco*. Os **dados da NASA** dizem *se
este ano está seguindo o normal* e escolhem a *ordem das culturas* (rotação) com evidência de clima parecido.

## 2. As quatro perguntas do agricultor e quem responde

| Pergunta | Quem responde | Escala | Onde vale |
|---|---|---|---|
| 1. **O que cabe aqui?** | FAO **GAEZ v4**: índice de aptidão de 0 a 100 por cultura | pixel de ~9 km; clima de 1981–2010 | mundo |
| 2. **Quando plantar e com que risco?** | **ZARC** do MAPA no Brasil; fora dele, um **ZARC sintético** feito com IMERG + POWER | município × decêndio | Brasil (oficial); mundo (sintético) |
| 3. **Este ano está normal?** | **Portões da NASA:** chuva IMERG desde 1/fev, SMAP L4 e VIIRS, mais o ONI da NOAA | município, por data | mundo |
| 4. **Em que ordem plantar?** | **Catálogo de rotações** (147 cartões) ponderado pela semelhança de clima do POWER | município | mundo |

As perguntas 1 e 2 são de **clima médio**: valem para qualquer ano. As perguntas 3 e 4 mudam a decisão **dentro** da
janela que o ZARC permite.

## 3. Camada 1: GAEZ v4, o que cabe

- **O que é:** o modelo de zonas agroecológicas da FAO e do IIASA. Calcula a aptidão de dezenas de culturas por clima,
  solo e relevo, em sequeiro ou irrigado, com insumo baixo ou alto.
- **Referências:**
  - Fischer et al. 2021, *GAEZ v4 Model documentation*, [10.4060/cb4744en](https://doi.org/10.4060/cb4744en);
  - Zabel et al. 2014, *PLOS ONE*, [10.1371/journal.pone.0107522](https://doi.org/10.1371/journal.pone.0107522), como segunda
    opinião revisada por pares.
  - Os dois PDFs estão em `artigos/`.
- **O que temos:** 306 camadas em `E:/campeonato-nasa/dados/gaez/`, com índice de aptidão e rendimento atingível. O
  clima de base é 1981–2010 (CRU-TS 3.2), em grade de 5' (~9 km).
- **Classes de aptidão** (camada oficial de classes do GAEZ v4, siLr; Fischer et al. 2021, fig. 7-3): > 85 muito alta;
  > 70 alta; > 55 boa; > 40 média; > 25 moderada; > 10 marginal; > 0 muito marginal.
  - **Corrigido em 14/11 (revisão A3):** os limiares 75/63/50/35/20 que usávamos são do texto da legenda do portal, não
    da camada de classes da v4.
  - A aptidão tem 1 casa decimal e só é arredondada na tela (revisão M1).
- **Como usamos:** é o filtro de culturas candidatas, por padrão em **sequeiro com insumo baixo**, que é a realidade da
  agricultura familiar do semiárido. **Corte "apta": > 40** (classe média ou melhor), decisão do projeto em 14/11;
  antes era > 35.
- **Limites:**
  - Não vê o ano: é clima médio.
  - O pixel de 9 km mistura serra, baixio e tabuleiro.
  - Não tem palma forrageira nem gergelim; mamona não está na nossa seleção. Para essas, usar o EcoCrop com o POWER
    (Ramírez-Villegas et al. 2013, em `artigos/`).
  - **Clima parecido não garante culturas parecidas**, e por isso o motor exige as duas coisas. Com a Tmax média
    (correção de 14/11), os 5 lugares mais parecidos no clima têm perfil de aptidão parecido (de 0,79 a 0,98), e
    Harare, de perfil diferente (−0,08), deixou de ser análogo (d 2,15; notebook de análogos, seção 4).

## 4. Camada 2: ZARC, quando plantar e com que risco

- **O que é:** o Zoneamento Agrícola de Risco Climático do MAPA, publicado por portaria a cada safra.
- **Granularidade:** para cada município, cultura, solo e ciclo, diz o risco de perda (20, 30 ou 40%) em cada
  decêndio (período de 10 dias), ou que a cultura não é indicada.
  - Solo: arenoso, médio ou argiloso; para o milho, as classes de água disponível AD1 a AD6.
  - Ciclo: Grupos I a IV.
- **Critério:** a cultura tem água suficiente na fase crítica em pelo menos 80% dos anos. É a linha de Campos et al. 2010
  ([10.1590/s1415-43662010000400008](https://doi.org/10.1590/s1415-43662010000400008), em `artigos/`).
- **O que temos:**
  - a tábua de risco oficial do Ceará de 2025/26 (22.231 linhas) e de 2026/27 (23.967 linhas), com o dicionário de
    dados, em `E:/campeonato-nasa/dados/complementares/zarc/`;
  - o arquivo de 2016/17 não tem nenhuma linha do Ceará;
  - **novo:** a tábua 2026/27 dos 9 estados do Nordeste (240.949 linhas, 1.794 municípios, 17 culturas, 113 portarias),
    em `E:/campeonato-nasa/dados/complementares/zarc_ne/`.
- **Portarias do CE em 2026/27:** 11, uma por cultura. A Portaria 245 vale só para o milho consorciado com braquiária;
  o milho 1ª safra é a 218.
- **Culturas de sequeiro com ZARC no Ceará:** milho (também consorciado com braquiária), feijão-caupi, feijão de 2ª
  safra, sorgo granífero e forrageiro, algodão herbáceo, amendoim, mamona e girassol. O girassol cobre só 104 dos 184
  municípios.
- **Regras de leitura (revisão de 14/11):**
  - **só os grupos de ciclo com cultivar indicada na portaria:** no CE, caupi (Port. 121/2026) e sorgo forrageiro
    (Port. 297/2026) só no Grupo I; mamona (Port. 143/2026) nos Grupos II–IV. Fora do CE, isso não foi conferido, e o
    cartão avisa;
  - **a mamona do cardápio é a tradicional;** a de "Clima Semiárido", indicada para baixa produtividade, fica fora;
  - **a janela vai do 1º dia do 1º decêndio ao último dia do último** (antes, terminava no 1º dia do último decêndio:
    o caupi "21/02–11/04" ia, na verdade, até 20/04);
  - **o aviso tem duas datas:** a 1ª com alguma cultura zoneada (risco até 40%) e a 1ª com risco de 20%;
  - **a janela é dada por solo**, além da união dos solos.
- **Fora da tábua aberta no Ceará:** mandioca, palma, guandu, milheto e gergelim. Para elas, a janela vem do ZARC
  sintético ou da janela de umidade do SMAP.
  - *Resolvido (revisão A1, 14/11 à noite):* a mandioca (Port. 11/2020), o milheto (330/2020) e a palma (284/2019) têm
    ZARC do CE em portaria plurianual. A tábua foi extraída e conferida (`scripts/zarc_plurianual_ce.py`), e o protótipo
    a usa no CE. As três constam como vigentes na página do MAPA (05/11/2026); SISZARC não conferido. O gergelim
    (198/2023) ficou de fora (não está no cardápio).
  - *Resolvido (revisão C5):* na Port. 11/2020, a janela da mandioca termina em março na maior parte do CE; abril fica
    fora em 160 de 184 municípios (com risco ≤ 30%, em todos). Em Quixadá, risco de 20% de 01/02 a 10/03. O plano diz
    "maniva na janela ZARC da mandioca".
- **Limites:**
  - Também é clima médio.
  - **A resposta depende do solo e do ciclo**, então o produto precisa perguntar o solo ao técnico ou estimar pelo
    SoilGrids.
  - Só existe no Brasil.

## 5. Exemplo: Quixadá, safra 2026/27

Saída de `scripts/gaez_zarc_municipio.py 2311306` (regerada em 14/11, à tarde):
- GAEZ no ponto interno do município (−4,911; −39,028), com 1 casa decimal e as classes oficiais da v4;
- ZARC de sequeiro 2026/27, com 9 portarias em Quixadá, uma por cultura: caupi 121, mamona 143, algodão 169, milho 218,
  milho com braquiária 245, sorgo granífero 270, sorgo forrageiro 297, feijão de 2ª safra 354 e amendoim 73 (o CE tem
  11: mais o girassol, 97, e o feijão irrigado, 27);
- só os ciclos com cultivar indicada no caupi e no sorgo forrageiro (Grupo I) e na mamona (Grupos II–IV, a tradicional);
  nas outras culturas, todos os grupos da tábua;
- as janelas são a **união** dos solos e desses ciclos, ou seja, a leitura mais permissiva. Cada janela vai do 1º dia
  do 1º decêndio ao último dia do último. A janela por solo está na leitura abaixo.

| Cultura (GAEZ) | Aptidão, insumo baixo | Aptidão, insumo alto | Cultura no ZARC | Risco 20% | Risco ≤ 30% | Risco ≤ 40% | Solo × ciclo com 20% |
|---|---|---|---|---|---|---|---|
| mandioca | 66,1 (boa) | 54,0 | fora da tábua aberta | — | — | — | — |
| sorgo | 65,7 (boa) | 73,8 | Sorgo Forrageiro (Grupo I) | 21/02–30/04 | 11/02–10/05 | 01/02–20/05 | 3 de 3 |
| sorgo | 65,7 (boa) | 73,8 | Sorgo Granífero | 11/02–20/04 | 01/02–30/04 | 21/01–10/05 | 9 de 9 |
| guandu | 62,0 (boa) | 72,5 | fora da tábua aberta | — | — | — | — |
| milheto | 60,1 (boa) | 73,5 | fora da tábua aberta | — | — | — | — |
| soja (fora do cardápio) | 60,1 (boa) | 72,3 | fora da tábua aberta | — | — | — | — |
| feijão (*Phaseolus*) | 58,4 (boa) | 70,4 | Feijão 2ª Safra | nenhum | 11/02–20/03 | 01/02–20/04 | 0 de 8 |
| milho | 55,7 (boa) | 72,5 | Milho 1ª Safra (igual com braquiária) | nenhum | 11/02–10/03 | 11/02–31/03 | 0 de 11 |
| feijão-caupi | 54,0 (média) | 72,3 | Feijão Caupi (Grupo I) | 11/03–20/04 | 01/03–20/04 | 21/01–20/04 | 3 de 3 |
| amendoim | 46,2 (média) | 61,9 | Amendoim | 11/02–20/03 | 01/02–10/04 | 21/01–20/04 | 8 de 9 |
| algodão | 41,3 (média) | 88,5 | Algodão Herbáceo | 11/02–20/03 | 01/02–31/03 | 21/01–20/04 | 6 de 9 |
| girassol | 0,0 | 50,7 | Girassol | — | — | — | sem linha |
| — | — | — | Mamona (tradicional, Grupos II–IV) | 21/02–31/03 | 21/02–10/04 | 21/02–20/04 | 6 de 8 |

**O que a combinação mostra:**
- **Núcleo seguro: caupi e sorgo.** Têm aptidão média (caupi, 54,0) ou boa (sorgo, 65,7) e risco de 20% em todos os
  solos com cultivar indicada (3 de 3 no Grupo I; no sorgo granífero, 9 de 9). São a base da estratégia de cauda (S2) e
  da troca de março (S1).
  - **Mas o caupi só chega a 20% a partir de 11/03.** Por solo: arenoso de 11 a 20/03; médio de 11 a 31/03; argiloso
    de 11/03 a 20/04. Antes disso, fica com 30% (desde 01/03) ou 40% (desde 21/01). A metade guardada até ~10/mar da
    S1 cai no começo da janela de 20%.
  - O sorgo forrageiro tem 20% de 21/02 a 20/03 no arenoso, até 20/04 no médio e até 30/04 no argiloso.
- **O milho cabe (aptidão 55,7), mas nunca chega ao risco de 20%.** O melhor é 30%, de 11/02 a 10/03, e só em AD5–AD6
  do Grupo I, os solos que guardam mais água. No AD4 do Grupo I, 30% só de 21 a 28/02; no AD2 e no AD3, só 40%; o AD1
  não é zoneado. No Grupo II, 30% só no AD5 (11–20/02) e no AD6 (11–28/02); no Grupo III, só no AD6 (11–20/02). Isso
  confirma a data-limite de 01/mar da proposta v2 (o decêndio de 01 a 10/03).
- **A mandioca é a mais apta no insumo baixo (66,1, logo acima do sorgo, 65,7), mas não está na tábua aberta do ZARC.**
  A janela dela vem da NASA (SMAP), e ela é o tampão do ano ruim. A portaria plurianual (Port. 11/2020) ainda não entrou
  (seção 4; A1 e C5 resolvidos no CE com a tábua plurianual).
- **O algodão só se justifica com insumo alto** (88,5 contra 41,3) e com vazio sanitário regional contra o bicudo.
- **Duas datas, nada em janeiro:** em Quixadá, o ZARC 2026/27 só zoneia alguma cultura a partir de 21/jan, e a 40%
  (algodão, amendoim, caupi e sorgo granífero). O risco de 30% começa em 01/fev, e o de 20% em 11/fev (algodão,
  amendoim e sorgo granífero). O milho só entra em 11/fev. A prática atual de plantar milho + feijão na 1ª chuva de
  janeiro (S0) fica **fora do zoneamento**.
  - *A conferir:* a portaria e as regras do Proagro e do Garantia-Safra sobre plantio fora do ZARC.

## 5.1 Cardápio do MVP: 15 culturas

Números de `scripts/gaez_zarc_municipio.py --ceara` com a regra decidida, ZARC 2026/27, recontados em 14/11 (tarde) em
`E:/campeonato-nasa/dados/gaez_zarc/ceara_2026-2027.csv`: classes da v4, corte "apta" > 40 e só os ciclos com cultivar.
"Indicada" = risco de 20% em alguma combinação solo × ciclo. "Com risco" = o melhor do ZARC é 30% ou 40%. "Apta" = sem
ZARC na tábua e aptidão > 40.

| Grupo | Cultura | Papel no sistema | Municípios do CE (de 184) | Base |
|---|---|---|---|---|
| **Alimento** | Feijão-caupi | leguminosa principal | 184 indicada (Grupo I) | ZARC + GAEZ |
| | Milho | cereal principal | 154 indicada, 30 com risco | ZARC + GAEZ |
| | Feijão comum | leguminosa | 136 indicada, 48 com risco | ZARC (feijão 2ª safra) + GAEZ |
| | Mandioca | tampão do ano seco | 155 apta (antes 164) | CE: ZARC plurianual (Port. 11/2020); outros estados: GAEZ |
| | Amendoim | leguminosa; quebra de nematoide | 183 indicada, 1 com risco | ZARC + GAEZ |
| | Sorgo granífero | cereal tolerante | 184 indicada | ZARC + GAEZ (mercado quase sumiu) |
| | Guandu | grão e forragem | 123 apta (antes 135) | GAEZ |
| **Forragem e cobertura** | Sorgo forrageiro | forragem | 184 indicada (Grupo I) | ZARC + GAEZ |
| | Milheto | forragem e cobertura | 102 apta (antes 121) | GAEZ |
| | Palma forrageira | forragem perene | sem camada | Diniz 2017, Lima 2018a (grau C); EcoCrop pendente |
| | Gliricídia | banco de proteína em faixa | sem camada | Martins 2015, Pérez-Marin 2006 |
| | Mucuna-preta | cobertura em revezamento no milho | sem camada | Melo 2013 |
| **Renda** | Algodão herbáceo | renda; só com vazio contra o bicudo | 183 indicada, 1 com risco | ZARC + GAEZ |
| | Mamona | renda | 184 indicada (tradicional, Grupos II–IV) | ZARC |
| | Girassol | renda | 70 indicada, 34 com risco | ZARC + GAEZ |

- **Por município:** das 12 culturas com dado, a mediana é 10 disponíveis (mínimo 6, máximo 12; antes, mediana 11).
  Por mesorregião: Centro-Sul, Noroeste e Sul 11; Norte e Sertões 10; Região Metropolitana 9; Jaguaribe 7.
- **Quixadá continua com 9:** caupi, sorgo granífero e forrageiro, amendoim, algodão, mamona, mandioca, guandu e
  milheto. O milho e o feijão comum ficam "com risco", porque ali o ZARC nunca passa de 30%.
- **Fora do cardápio do CE:** soja (só no recorte do MATOPIBA), arroz, cana, banana e trigo. A tábua GAEZ × ZARC traz a
  soja com aptidão > 40 em 97 municípios do CE, mas ela fica fora do cardápio.
- **Com o GAEZ como corte, o ZARC perderia mais:** com > 40, 632 pares município × cultura que o ZARC indica com 20%
  de risco cairiam, em 152 municípios (com o corte antigo, > 35: 494 em 127). É a razão da regra da seção 6.

## 6. Como as camadas se combinam no motor

1. **Quais culturas** (regra decidida em 14/11):
   - **onde há ZARC, o ZARC decide**, e a aptidão do GAEZ aparece como rótulo;
   - **o GAEZ filtra sozinho só as culturas sem ZARC** (aptidão > 40): mandioca, guandu e milheto;
   - **nos perímetros irrigados**, o GAEZ entra com insumo alto.
2. **Janela ZARC:** o período de semeadura e o risco de cada cultura, para o solo e o ciclo do usuário. Se o solo for
   desconhecido, o cartão mostra a faixa entre o solo mais restritivo e o mais permissivo. O protótipo já calcula a
   janela de cada solo e mostra as duas datas do aviso (zoneada até 40% e risco de 20%); o seletor de solo ainda falta
   (revisão A7).
3. **Portões NASA do ano:** escolhem o ponto *dentro* da janela. A janela do ZARC é sempre o limite.
   - **P1, novembro:** ONI e o que esperar da quadra.
   - **P2, jan–fev:** "plante uma parte e guarde a outra".
   - **~10/mar:** caupi precoce na metade guardada, se a chuva desde 1/fev estiver abaixo de 75%.
   - **19/mar e 30/abr:** a chuva desde 1/fev confirma; o SMAP é a segunda confirmação.
   - **Essas datas são da quadra do norte.** No Nordeste, o regime muda
     (`E:/campeonato-nasa/dados/analogos_aprofundado/regime_chuva_ne_mun.csv`, os 4 meses mais chuvosos do IMERG): a
     quadra do norte (jan–abr ou fev–mai) cobre 1.056 municípios, inclusive os 184 do CE; o litoral leste (mar–jun ou
     abr–jul), 312; o Cerrado e o sul da BA (out–jan, nov–fev ou dez–mar), 426. No litoral leste, o IMERG capta só
     39–72% da chuva das automáticas do INMET, e as datas vêm do ZARC.
4. **Rotação:** o catálogo ponderado pelo clima ordena as sequências de 2027 a 2029:
   - faixas milho | caupi que trocam de lugar a cada ano;
   - caupi ou mucuna em revezamento tardio no milho;
   - interruptor por ano: leguminosa em ano bom, pousio ou sorgo forrageiro em ano seco;
   - tampão de mandioca que gira entre as faixas;
   - palma e gliricídia em nível, sem fogo.
5. **Cartão com recibo:**
   - aptidão GAEZ;
   - risco ZARC;
   - luz do ano;
   - efeito da rotação, com o grau (A–D) e o peso de clima w;
   - a lacuna dita com honestidade: a passagem do consórcio atual (S0) para a rotação nunca foi medida.

## 7. Fora do Brasil: GAEZ + ZARC sintético da NASA

- **Mesmo critério do ZARC, só com dados globais.** Balanço hídrico FAO-56 com chuva IMERG e clima POWER; a cultura é
  indicada num decêndio se tiver água suficiente na fase crítica em pelo menos 80% dos anos.
- **Validação no Ceará contra o ZARC oficial:**
  - Contra o solo mais permissivo, o milho sintético acerta a ordem (Spearman 0,86) e cai a ±1 decêndio em 89% dos
    municípios.
  - Contra a mediana dos solos e ciclos, caupi e sorgo acertam ±1 decêndio em 84%, e o milho sai 2 decêndios mais tarde.
  - **O veredito depende do solo escolhido** (`conselho/analises/v3_verificador_zarc_solo.saida.txt`).
- **Cuidado com a ET0 do POWER:** sai 1,27 vez a das estações automáticas do INMET no Ceará, mas 0,97–1,01 vez as
  normais. Ela entra como sensibilidade, não como correção fixa.
- **Onde a lógica vale igual** (notebook de análogos, seção 3, com a Tmax média): Chaco argentino, Oeste da Bahia,
  norte da Austrália, Burkina Faso, sudoeste de Madagascar e o Deccan. Logo depois vêm o Benim, o Zimbábue, o México,
  o Sudão do Sul, a Namíbia, Moçambique, o norte da Nigéria, o Pantanal e Angola. São 19 de 387 pontos de terra a
  distância < 1,5 do Sertão Central; o norte de Minas (1,59) e a China saíram.

## 8. Onde entra cada dado da NASA

| Dado | Papel nesta estrutura |
|---|---|
| **POWER** | clima para o ZARC sintético e o EcoCrop; assinatura climática dos análogos (peso w do catálogo) |
| **GPM IMERG V07** | chuva diária do ZARC sintético; início da estação; regime de chuva; luz principal dos portões (chuva desde 1/fev). O Final vai até 30/09/2025; depois, o diário via POWER é o Late, preliminar |
| **SMAP L4** | segunda confirmação nos portões (r 0,72 contra 303 estações do CEMADEN); janela da maniva |
| **MODIS / VIIRS** | o verde confirma o início e a resposta da lavoura; testemunha de junho |
| **NASADEM** | declive para as faixas em nível e as aleias (10–25%) |
| **GRACE / GLDAS** | relógio lento da água (açude, poço) |

## 9. Decisões em aberto (equipe)

1. ~~Limiar do GAEZ~~ **Decidido em 14/11:** o ZARC decide onde existe; o GAEZ (> 40, insumo baixo) filtra só as
   culturas sem ZARC; nos perímetros irrigados, insumo alto. Motivo: com o GAEZ como corte, pares município × cultura
   que o ZARC indica com 20% de risco cairiam: 494 em 127 municípios com o corte antigo (> 35) e 632 em 152 com o
   atual (> 40). São serras, litoral e várzeas do Jaguaribe, onde o pixel de 9 km mistura encosta, duna e cidade.
   - **Corte "apta" > 40 (decidido em 14/11, à tarde; revisão A3):** é a classe "média" ou melhor da camada oficial
     da v4. O > 35 vinha dos limiares do texto do portal.
2. **Solo para o ZARC:** perguntar ao técnico, estimar pelo SoilGrids ou mostrar sempre a faixa? O protótipo já calcula
   a janela de cada solo; falta o seletor (revisão A7).
3. **Culturas fora da tábua aberta do ZARC no CE** (mandioca, palma, guandu, milheto, gergelim): EcoCrop com POWER mais
   a janela do SMAP, com grau C? A mandioca, o milheto, a palma e o gergelim têm portaria plurianual (revisão A1): a
   tábua complementar, ainda pendente, cobriria essas quatro.
4. **Datas do ZARC em Quixadá:** o protótipo mostra as duas datas (zoneada a 40% desde 21/jan; risco de 20% desde
   11/fev). Falta confirmar na portaria e decidir como o cartão fala de quem planta antes ("sua data de plantio está
   fora do ZARC").
5. **Mamona e girassol:** estão no ZARC, mas não na nossa seleção do GAEZ (o girassol tem aptidão 0 no insumo baixo).
   Entram? A mamona já entra no cardápio pelo ZARC, na versão tradicional (Grupos II–IV).
6. **Grupos de ciclo fora do CE:** no CE, só entram os grupos com cultivar indicada (caupi e sorgo forrageiro no Grupo
   I; mamona nos Grupos II–IV). Nos outros 8 estados, isso não foi conferido nas portarias; hoje o protótipo usa todos
   os grupos e avisa.

## 10. Próximos passos

1. Rodar `scripts/gaez_zarc_municipio.py` para os 184 municípios e fazer o mapa do "núcleo seguro" (aptidão > 40 e
   risco de 20%) por cultura. Feito para o NE inteiro na tábua do protótipo (`nordeste_2026-2027.csv`); falta o mapa.
2. Gerar o ZARC sintético global com IMERG + POWER, reaproveitando o balanço do agrônomo, e publicar o mapa de
   validação contra o oficial.
3. Levar as duas camadas para o site (globo → mapa): clicar no município abre o cartão.
4. Rodar o EcoCrop para a palma e o gergelim.

## Fontes no repositório

- `scripts/gaez_zarc_municipio.py`: a tabela da seção 5, para qualquer município do CE.
- `scripts/preparar_prototipo_nordeste.py`: a mesma regra para os 1.794 municípios do NE (ZARC do NE, assinaturas do
  POWER, regime e início da chuva).
- `protótipo/REVISAO_10_AGENTES.md`: a revisão de 14/11 que motivou as correções desta versão.
- `notebooks/estudo_estatistico_bases.ipynb`, seção 11 (GAEZ), e `notebooks/analogos_transferencia.ipynb`, seções 3, 4 e 6.
- `pesquisa/aptidao_calendario_analogos.md`, `pesquisa/catalogo_rotacoes_comprovadas.md` e
  `pesquisa/viabilidade_artigos_nordeste.md`.
- `proposta/PROPOSTA_FINAL_v2.md`, seção 6 (motor de rotação e portões).
