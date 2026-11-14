# Jornada e telas (jornada)

## Resumo
Hoje existem quatro interfaces com três marcas (QUADRA, Roça Certa e PercolaCampo), e cada uma cobre só um pedaço da jornada. A melhor costura é uma página única com um stepper de 6 passos: Lugar, O lugar, Sua roça, Plantio, Retorno e Segurança. O globo do site-nasa-v2 serve de abertura e o conteúdo vem do motor do José (a /api/local responde em 0,4 s com 38 KB, então o stepper pode rodar ao vivo). As perguntas entram num bloco só, no passo 3: depois que a pessoa já viu o que os dados da NASA e do ZARC dizem sem perguntar nada, e antes do plano, do retorno e da segurança, que dependem das respostas. Toda pergunta aceita "não sei" e mostra na hora o que muda. A parte do Vicente entra no passo 4 como a camada "por dentro de cada parte": faixas alternadas, espaçamento e borda contra o vento, encaixada no roçado A/B/C + baixio + bordas do José. Os números de "% da lavoura salva" do PercolaCampo ficam fora da tela do agricultor, porque saem de constantes ad hoc e de dados fixos no código. Na segurança, cada ciclo de colheita do plano ganha uma faixa p10–p50–p90 de renda por ha, tirada da série do próprio município (PAM 1998–2025, deflacionada). O ciclo de 2027 é condicionado ao El Niño medido hoje (só 4 anos, mostrados um a um); 2028 e 2029 usam a história inteira e têm faixa mais larga, a "névoa". Isso é distribuição de anos parecidos, não previsão, e a tela diz isso. O escopo P0 soma cerca de 26 h (contando ~4 h de vídeo e slides) com uma pessoa e IA até 15/11 às 23:59 e só cabe com sono curto: se apertar, o primeiro corte é o passo 6 enxuto, sem a faixa da série temporal. O modo técnico, o glossário completo, o simulador do PercolaCampo e o inglês ficam em P1/P2.

## Recomendações
- **P0** (3 h) Montar um stepper de 6 passos num único endereço, sem iframe, com o estado na URL (#/2311306/4?t=1&ag=chuva&a=3ha…), history.pushState em cada passo e o botão Voltar do navegador funcionando — O iframe do JP quebra a rolagem e o Voltar no celular. A URL com estado permite link direto para o vídeo e para o júri, e o passo 'pular' fica reproduzível.
- **P0** (2.5 h) Passo 1: globo do site-nasa-v2 → ao pousar, abrir a folha do Vicente 'Sua roça fica em QUIXADÁ (CE) · [Mudar] [Ver o que dá para plantar →]'; botão 'Pular animação' que abre o mapa leve dos municípios (malha_ne.json do JP) — O globo é o impacto visual do vídeo. Em celular fraco, ninguém pode ficar preso nele.
- **P0** (3 h) Passo 2 'O que este lugar permite', sem perguntar nada: faixa 'HOJE 14/11 (medido)' com a tríade Sabemos / Ainda não sabemos / Dá para fazer; régua da estação de chuva; cardápio em blocos coloridos pelo risco do ZARC, sem tabela no modo agricultor; 'Janela aberta agora' — Mostra o valor antes de pedir esforço, como no cartão 'o QUADRA não sabe tudo; aqui está o que ele sabe' da proposta. Reaproveita cartaoAno e cartaoCardapio do José.
- **P0** (2.5 h) Passo 3 'Sua roça': um bloco de 6 perguntas em botões grandes, cada uma com 'não sei' e a linha 'muda:'. São elas: prática atual (pré-marcada pelo Censo 2017), terra (areia / mistura / barro), água (só chuva / cisterna ou barreiro / açude ou poço que irriga), tamanho e baixio, criação, o que já tem guardado, e o vento (opcional). O solo vai para a API; as outras mudam a tela no navegador — Este é o melhor momento para perguntar: o plano, o retorno e a segurança dependem das respostas, e a pessoa já viu o que os dados sabem. Com 'não sei', o plano usa o melhor caso e o rótulo 'suposição' aparece no plano.
- **P0** (4 h) Passo 4 'Como plantar e distribuir': roçado visto de cima (rocado() do José) com seletor 2027/2028/2029 e ▶ animar; lupa 'ver por dentro da parte' com o desenho do PercolaCampo (faixas milho|caupi, covas, borda de palma + gliricídia do lado do vento informado); linha do ano simplificada (Gantt do José) e lista 'Agora' para marcar — É onde o José pediu a parte do Vicente. O PercolaCampo entra como o arranjo dentro de cada parte, que é a escala que falta ao plano A/B/C, sem trazer os números de ganho.
- **P0** (3 h) Passo 5 'Quanto rende': barras de entrada e gasto por ano, com a linha do caixa acumulado do plano contra a prática atual; botões 'Como vai ser 2027? normal / El Niño forte / seca' e 'Preço da raiz'; manchete com a faixa (+R$ 4 a 14 mil em 3 anos em Quixadá) e 'chance de não pagar o desembolso 68% → 34%'; nos outros municípios, R$/ha pela mediana do painel, com o selo 'por ha, sem a sua área' quando a área não for informada — A queda em 2027 seguida de alta é a verdade financeira do plano e precisa estar à vista; a faixa evita prometer um número só.
- **P0** (3 h) Passo 6 'Segurança por colheita': uma linha por ciclo do plano (cultura, parte, mês da colheita) com a faixa p10–p50–p90 de R$/ha do município, os anos de El Niño forte como pontos com o ano escrito, o risco do ZARC da janela e uma luz verde/amarela/vermelha por regra rotulada. 2027 condicionado ao El Niño (n = 4, mostrado ano a ano); 2028 e 2029 com a série toda e faixa mais larga. Mais um gráfico da série 1998–2025 com 'hoje' e as faixas projetadas — Responde ao pedido de 'perspectiva de segurança' sem inventar índice. São três leituras honestas (ZARC oficial, história do município, ano de El Niño), separando o medido do projetado.
- **P0** (1.5 h) Pré-calcular um JSON financeiro por município (1.791) a partir de painel_mun_cultura_ano.parquet: n, p10/p50/p90, valores nos anos de El Niño forte e de seca, série anual e custo CONAB (semente e desembolso), com a marca 'misto/irrigado' onde o PAM foge da roça familiar — Os passos 5 e 6 ficam rápidos e funcionam em hospedagem estática. Sem a marca, Barreiras mostraria milho a R$ 5.887/ha como se fosse do sertão.
- **P0** (0.5 h) Decidir uma única mensagem de El Niño: o estado como manchete, em frequência natural, e o município (3 anos) como detalhe; o cartão do Vicente sai — Três números diferentes para a mesma pergunta derrubam a confiança, e o teste do JP mostrou AUC ≈ 0,5 no nível do município.
- **P0** (3 h) Roteiro e gravação do vídeo de 30 s em inglês (só Quixadá, qualidade=alta, legendas na tela) e ≤ 7 slides — É o que o júri vê primeiro. Precisa usar só números da folha 9.7 ou do JSON.
- **P1** (1.5 h) Interruptor 'Modo técnico': mostra a tabela do cardápio com solo × ciclo, o ZARC por solo, a evidência (grau A–D, T0–T3, w), as fontes e o seletor AD1–AD6 — Atende o extensionista e o avaliador sem poluir a tela do agricultor. Reaproveita cartaoEvidencia e cartaoFontes.
- **P1** (1.5 h) Glossário em pop-up nos termos (ZARC, GAEZ, SMAP, IMERG, tampão, baixio, revezamento, percentil, 'pior ano em 10') e o botão '?' do Vicente levando a 'Como funciona' — É exigência do desafio, e o texto já está escrito na proposta (3.4).
- **P1** (1 h) Abrir o simulador completo do PercolaCampo numa aba ou janela, rotulado 'modelo teórico de percolação (literatura fora do semiárido)', com o vento e o espaçamento vindos das respostas — Dá crédito à parte do Vicente e mostra a ciência ao júri sem misturar os números dele com os medidos.
- **P1** (2 h) Acabamento para celular: navegação fixa embaixo, Gantt vertical por parte, anos do roçado trocados com o dedo, alvos ≥ 48 px, letra de 18 px, globo em qualidade baixa ou pulado — O agricultor usa celular. Hoje só o Vicente foi pensado para ele.
- **P2** (8 h) Versão em inglês dos rótulos, perguntas de retorno nos portões ('Plantou? Em que dia?' e o pluviômetro), cartão para WhatsApp, áudio, uso sem internet e pesos da família — Valem a pena, mas não cabem até 15/11 às 23:59. O vídeo legendado cobre o inglês.

## Achados
- **Quatro telas, três marcas, nenhuma cobre a jornada inteira**: site-nasa-v2 = só globo + mapa (sem painel). JP v1 = globo + painel Roça Certa num iframe, com abas Inverno/Plantar/Alerta e 3 abas vazias. Protótipo do José = todo o conteúdo (cardápio, este ano, calendário, rotação, evidência), mas numa página longa de 7 cartões densos. Vicente = linguagem certa para o agricultor (letra de 18 px, semáforo, botão '?' que leva a 'Como eu funciono', folha 'Sua roça fica em… Mudar / Ver'), mas com dados só do CE (184 municípios). PercolaCampo = simulador de arranjo espacial com terrenos fictícios. _[site-nasa-v2/index.html (sem painel); colegas/joao-pedro/site-nasa/static/js/painel.js:26 (iframe /painel/<cod>?embutido=1); colegas/joao-pedro/site-nasa/static/js/rocacerta.js (abas 'veranico', 'preparo' e 'entressafra' com vazia:true); protótipo/static/app.js:67 (nav por âncoras de 7 cartões); colegas/vicente/interface-inicial-vicente/README.md (184 municípios do CE)]_
- **O globo do site-nasa-v2 é o melhor palco do passo 1**: É a mesma experiência da v1 do JP, mas estática, com bibliotecas locais e qualidade adaptativa: 30 contra 4 quadros por segundo e 0,7–0,8 MB contra 4,9 MB baixados na abertura, medidos sem placa de vídeo. Já traz o 'só o Nordeste' com o aviso 'Oxente, aí não!' e 'Me leva pro Nordeste'. Falta o passo seguinte: ao chegar, mostrar a folha de confirmação do município e abrir o stepper. O autor não está confirmado. _[site-nasa-v2/README.md:42-43 (medições) e seção 'Só o Nordeste'; js/qualidade.js; js/nordeste.js]_
- **O motor do José aguenta um stepper ao vivo; a malha de municípios pesa no celular**: /api/local de Picos: 0,41 s e 38 KB. Com textura=1, 0,42 s: trocar o solo pode redesenhar o plano na hora. Já /api/municipios devolve 2,8 MB sem gzip, o que pesa no 3G. A malha simplificada do JP (malha_ne.json em caminhos SVG, servida com gzip) é a melhor escolha para o mapa de escolha. _[curl -w em http://127.0.0.1:8765/api/local?lat=-7.08&lon=-41.47 → tempo=0.406s, tamanho=38095; /api/municipios → 2807372 B; colegas/joao-pedro/site-nasa/README.md (seção Otimizações: gzip, ~870 KB → ~300 KB)]_
- **A API só aceita solo; as outras perguntas têm de mudar algo visível na tela**: O motor recebe textura (1–3) e AD (11–16), e AD1–AD6 não é linguagem de agricultor. A proposta já lista o que perguntar na primeira visita: prática atual (o Censo 2017 sugere e uma pergunta confirma), solo, rebanho, semente guardada, maniva, mão de obra e água guardada. Uma pergunta que não muda nada parece de enfeite. Cada pergunta precisa de uma linha 'muda:' ligada a uma saída. _[protótipo/static/app.js:11 (urlLocal só com textura e ad) e seletoresSolo(); proposta/PROPOSTA_FINAL_v3.md:369 (Primeira visita)]_
- **Três mensagens diferentes sobre o El Niño**: O motor do José fala do município (IMERG, 3 El Niños fortes: '2 de 3 no terço mais seco'). O painel do JP fala de propósito do estado, porque contar anos parecidos do município não passou do acaso no teste deixando um ano de fora (AUC ≈ 0,5). O Vicente usa os anos com ONI ≥ 1 do próprio município. Se as três aparecerem no mesmo site, o usuário vê números que se contradizem. É preciso escolher uma manchete e deixar as outras como detalhe. _[Quixadá na /api/local: este_ano.perspectiva ('nos 3 El Niños fortes da série IMERG… 2 ficaram no terço mais seco'); colegas/joao-pedro/site-nasa/README.md:34 (AUC ≈ 0,5); colegas/vicente/interface-inicial-vicente/fonte/pagina.html:251 (cardInverno)]_
- **PercolaCampo: boa UX, números sem base no semiárido**: Peças muito boas: os 3 passos práticos (distância entre covas, barreira contra o vento, casa das joaninhas com ≥ 40% de mata), a régua de espaçamento, a simulação do foco do dia 1 ao 15 e o 'aplicar melhor desenho' em 1 toque. Problemas: o vento é texto fixo ('Vento vindo do Nordeste (18 km/h)'), os terrenos são fictícios, '% da lavoura salva' = 108 − R_eff·34 e os fatores 0,76/1,05/2,35 não vêm de medição. A página usa o Tailwind pelo CDN (compilação em tempo real) e não chama nenhum dado. Como camada visual do arranjo dentro de cada parte do roçado, encaixa bem. Como número de ganho na tela do agricultor, não. _[colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_motor_calibrado_por_metan_lise_cient_fica.html:7 (cdn.tailwindcss.com), :181 (vento fixo), :952-959 (seedFactor, T_eff·2,35, protectedPct); dossi_completo_projeto_percolacampo_hackathon_nasa.md seção 4.1]_
- **Não há vento por município nos dados**: O motor não tem direção do vento e power_ne_mensal.parquet é regional (6.480 linhas: data, variável, valor). A borda contra o vento do PercolaCampo precisa de outra fonte: perguntar ao agricultor (ele sabe melhor que o satélite) ou usar um padrão regional rotulado como suposição. Baixar o POWER por município não cabe no prazo (dá 429). _[grep 'vento|WD2M|WS2M' protótipo/motor.py: só a linha 40 (texto da fonte); E:/campeonato-nasa/venv/Scripts/python.exe olhar_vento.py → colunas ['data','variavel','valor','unidade','fonte']]_
- **Já há dado financeiro para mostrar a segurança por ciclo em quase todo o NE**: painel_mun_cultura_ano.parquet: 1.791 municípios × 8 culturas × 1998–2025, com receita por ha plantado em R$ de 2025. Em Quixadá a história se conta sozinha. Milho: p10 R$ 182, p50 R$ 622, p90 R$ 1.851, mediana nos 4 El Niños fortes R$ 184. Mandioca: p50 R$ 5.231 e R$ 5.731 nos El Niños. Feijão: p50 R$ 1.340 e R$ 805 nos El Niños. Atenção: o PAM mistura irrigado e lavoura comercial. Em Barreiras o milho tem p50 de R$ 5.887/ha, que é do cerrado e não da roça familiar. _[scratchpad/analise10/jornada/quixada_fin.py → saída em C:/Users/NETINH~1/AppData/Local/Temp/claude/88b277d27b184113/73cd62bd-b6e9-4872-9e4a-a06e5ca404a0/scratchpad/analise10/jornada/quixada_fin.saida.txt]_
- **O caso da família de Quixadá dá a manchete do passo de retorno**: O plano pede caixa e trabalho em 2027 (maniva e sorgo forrageiro sem venda) e paga em 2028–2029 com a mandioca: a curva cai e depois sobe. Com El Niño forte em 2027, fica de +R$ 4.009 a +R$ 13.978 acima da prática atual em 3 anos, conforme o preço da raiz, e empata com a raiz a R$ 0,29/kg. A chance de não pagar o desembolso cai de 68% para 34% (de 75% para 41% em El Niño forte). A família é fictícia, e o cálculo deixa de fora a mão de obra, a forragem e o Garantia-Safra. _[notebooks/secoes_financeiro/90_sintese.py:40-52; notebooks/secoes_financeiro/10_familia.py:1-30 (tabela medido × suposição)]_
- **O que a proposta exige que apareça na tela**: Glossário em pop-up (exigência do desafio); 'apoiar, não substituir': todo cartão termina com 'o que confirmar com o técnico'; o freio de segurança ('100% mandioca' é o que o otimizador escolheria); toda data limitada ao ZARC; nenhum número de Quixadá fora do JSON ou da folha 9.7. _[proposta/PROPOSTA_FINAL_v3.md:379 (3.4 Glossário), 402-410 (3.5), 686 (lista branca de números)]_

## Reaproveitar
- site-nasa-v2/js/espaco.js, qualidade.js, nordeste.js, busca.js, css/estilo.css, vendor/ → site-versao-final/ (camada de abertura): Passo 1 inteiro: globo, mergulho, 'só o Nordeste' com o aviso 'Oxente', qualidade adaptativa. Ao pousar, disparar o evento que abre a folha de confirmação, em vez do cartão 'Você está em'.
- colegas/joao-pedro/site-nasa/static/js/util.js (dentroDoNordeste, acharMunicipio) e static/data/malha_ne.json → site-versao-final/js e dados/: Ligar o lugar ao código IBGE e desenhar um mapa leve em SVG para o 'pular animação' e para o minimapa do cabeçalho.
- colegas/joao-pedro/site-nasa/static/js/rocacerta.js (escalaOni, barraNormal, fila do solo, anosEstado) → passo 2: Minigráficos da faixa 'HOJE' do passo 2: régua do ONI, posição do solo entre os anos e seca por estado nos anos de El Niño, a manchete única de El Niño.
- colegas/joao-pedro/site-nasa/static/js/painel.js → casca do stepper: Só o padrão: o mapa encolhe e o painel abre ao lado, com o stepper no lugar do iframe.
- protótipo/static/app.js (cartaoAno, cartaoCardapio + seletoresSolo, cartaoCalendario, rocado, cartaoPlano, cartaoEvidencia, cartaoFontes) e /api/local → passos 2 e 4, modo técnico: Conteúdo dos passos 2 e 4 e do modo técnico. Reaproveitar as funções e trocar a página longa pelo stepper; o cardápio vira blocos no modo agricultor e tabela no modo técnico.
- protótipo/static/estilo.css (.t-*/.f-* por tipo de cultura e .b-* do Gantt) → css comum: Uma só paleta por papel da cultura (leguminosa, cereal, tampão, forragem, perene) nos passos 4, 5 e 6, para a pessoa seguir a cor da roça até o dinheiro.
- colegas/vicente/interface-inicial-vicente/fonte/pagina.html (tokens :root, .big semáforo, .tiles 'Agora: entressafra', botão '?' para 'Como eu funciono', folha 'Sua roça fica em', cardChuva, cardCulturas) → css comum, passos 1, 4 e 6: Linguagem visual do modo agricultor: letra de 18 px, Atkinson Hyperlegible, semáforo, folha de confirmação do passo 1, lista 'Agora' do passo 4. cardChuva e cardCulturas servem de base visual para o passo 6. Os dados (só do CE) não vão.
- colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_*.html (renderPlantRuler, 'O que fazer na prática' em 3 passos, renderFarmSvg com faixas e borda, linha do tempo do dia 1 ao 15) → passo 4 (lupa) + página separada do simulador: A lupa 'por dentro da parte' no passo 4: desenho estático das faixas e da borda do lado do vento informado, a régua de espaçamento e os 3 passos práticos. O simulador completo abre à parte, rotulado 'modelo teórico'. Não usar protectedPct nem o Tailwind CDN na página final.
- notebooks/secoes_financeiro/10_familia.py e 90_sintese.py → passo 5: Manchete e números do passo 5 em Quixadá (+R$ 4–14 mil, 68% → 34%, empate a R$ 0,29/kg) e a tabela medido × suposição como 'como funciona' do retorno.
- E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet + conab_custos_ne.csv → site-versao-final/dados/fin/: Pré-calcular dados/fin/<cod>.json (quantis, anos de El Niño e de seca, série anual, custo) para os passos 5 e 6 em todo o NE.
- proposta/PROPOSTA_FINAL_v3.md 3.3 (primeira visita), 3.4 (glossário), 3.5 (apoiar, não substituir) → passo 3, pop-ups, rodapés: Lista e ordem das perguntas do passo 3, textos do glossário em pop-up e o rodapé 'confirme com o técnico' em todos os passos.
- colegas/joao-pedro/site-nasa/ferramentas/captura.py e site-nasa-v2/ferramentas/captura.mjs → ferramentas/: Fotografar cada passo para os slides e testar no Chrome sem janela antes de gravar o vídeo.

## Proposta detalhada
## 0. A jornada em uma linha

ABRIR (globo 3D) → 1 LUGAR → 2 O LUGAR PERMITE (só dados) → 3 SUA ROÇA (perguntas) → 4 PLANTIO (rotação do José + desenho do Vicente) → 5 RETORNO (R$) → 6 SEGURANÇA (projeção por colheita)

Regras de UX em todos os passos:
- Cada passo termina com a mesma tríade: **Sabemos (medido) · Ainda não sabemos · Dá para fazer / confirme com o técnico**.
- Todo número leva um selo pequeno: `medido`, `suposição` ou `projeção (anos parecidos)`.

## 1. Quando perguntar (análise)

| Opção | Prós | Contras | Veredito |
|---|---|---|---|
| A. Assistente antes de tudo | o plano já sai personalizado | a pessoa responde antes de ver qualquer valor; mais abandono; vídeo lento | não |
| **B. Bloco único depois do passo 2** | primeiro o valor ("o que a NASA e o ZARC sabem sem perguntar"); as perguntas fazem a ponte do lugar para a sua roça; 1 minuto; fácil de filmar | o passo 2 ainda não é pessoal | **sim** |
| C. Perguntas espalhadas por cada passo | cada pergunta perto do efeito | dispersa; o passo 5 pediria a área tarde demais | só como reforço: o chip "solo: não informado ✎" no passo 4 |

Segundo momento (P2, fica para depois): as **perguntas de retorno nos portões** da proposta.
- P2 jan–fev: "Plantou? Em que dia?" → recalcula a colheita.
- 19/mar: "Quanto deu o pluviômetro?"

É a segunda visita da tabela 3.3 da proposta.

## 2. Cabeçalho comum (passos 2 a 6)

```
 QUADRA · Quixadá (CE) · Sertão Central          [Mudar lugar] [?] [Modo técnico] [Fontes]
 (1)Lugar ── (2)O lugar ── (3)Sua roça ── (4)Plantio ── (5)Retorno ── (6)Segurança
   ✓            ✓            ●             ○              ○             ○
```

No celular:
```
 QUADRA · Quixadá (CE)               [≡]
 Passo 3 de 6 · Sua roça   ▓▓▓░░░
 ...
 [ ← Voltar ]            [ Próximo → ]   ← barra fixa embaixo
```

Navegação:
- Os passos já visitados ficam clicáveis.
- "Pular" existe no passo 3 (usa o melhor caso e marca "suposição").
- "Não sei" existe em toda pergunta.
- O Voltar do navegador volta um passo.
- "Começar de novo" fica no menu.

## 3. Wireframes

### PASSO 1: Lugar (globo do site-nasa-v2 + folha do Vicente)

```
+------------------------------------------------------------------+
| QUADRA                          NASA Space Apps 2026 / Field Shift|
|                                                                  |
|   Escolha um lugar                    .-"""""-.                  |
|   no Nordeste.                      /  TERRA  \   contorno        |
|   [ Quixadá, Ceará          ][ Ir ] |   3D NE   |  dourado do NE  |
|   Experimente: Quixadá · Picos · Petrolina · Arapiraca · Barreiras|
|   [ Pular animação → lista/mapa ]   "Oxente, aí não!" fora do NE  |
+------------------------------------------------------------------+
            (mergulho: globo → mapa com o município aceso)
+---------------------------- folha de baixo ----------------------+
|  Sua roça fica em  QUIXADÁ (CE)  · Sertão Central · 1.794 no NE   |
|  [ Mudar ]                        [ Ver o que dá para plantar → ] |
+------------------------------------------------------------------+
```

### PASSO 2: O que este lugar permite (nenhuma pergunta)

```
┌ HOJE · 14/11/2026 · medido ─────────────────────────────────────┐
│ (●vermelho) ANO DE ALERTA  El Niño +2,46 (ago–out): o mais forte │
│             desde 1950 (NOAA). No seu estado, depois de El Niño, │
│             seca em X de cada 10 municípios.  [ver ano a ano]    │
│ Solo agora (SMAP): 8º de 12 anos · normal p/ a época · "dormindo"│
│ Chuva ago–nov: 6 mm · estação seca, não prevê a quadra           │
│ Ainda não sabemos: o Atlântico de fev–abr.                       │
│ Dá para fazer já: semente de caupi até dez · maniva p/ fev       │
└──────────────────────────────────────────────────────────────────┘
 Estação de chuva  J  F  M  A  M  J  J  A  S  O  N  D
                   ■  ■  ■  ■  ·  ·  ·  ·  ·  ·  ▲hoje
                   jan–abr · 568 mm · 75% do ano · começa ~18/jan (8 em 10: 31/dez–14/fev)
┌ O QUE DÁ PARA PLANTAR AQUI · 11 de 15 ───────────────────────────┐
│ COMIDA   [Caupi ●] [Mandioca ●] [Milho ◐] [Feijão ◐] [Amendoim ●] │
│ GADO     [Sorgo forr. ●] [Palma ●] [Milheto ●] [Guandu ○] [Gliric. ○]│
│ RENDA    [Algodão ●] [Mamona ●] [Girassol ✕]                       │
│ ● risco 20% (ZARC)  ◐ risco 30–40%  ○ apta, sem ZARC  ✕ não cabe   │
│ toque no bloco → janela "11/03–20/04" + de onde vem (ZARC/GAEZ)    │
└────────────────────────────────────────────────────────────────────┘
 Janela aberta agora: Palma (desde 01/12) · Próxima: maniva 01/02
                                       [ Responder 6 perguntas → ]
```

### PASSO 3: Sua roça (6 perguntas, cerca de 1 minuto)

```
 Responda o que souber. Cada resposta muda o plano. "Não sei" também vale.
 0. Hoje você planta milho com feijão na 1ª chuva?  (o Censo 2017 diz que sim aqui)
    [ sim ] [ não, outra coisa ] [ não sei ]        muda: a comparação do passo 5
 1. Como é a terra da roça?
    [areia solta] [mistura] [barro que gruda] [não sei]
    muda: as janelas do ZARC (ex.: maniva 01/02–10/03 → 11/02–28/02 na areia)
 2. Que água a roça tem?
    [só chuva] [cisterna/barreiro] [açude ou poço que irriga] [não sei]
    muda: cisterna de 52 mil L = 5 mm em 1 ha, ou 17 mm em 1 tarefa (0,3 ha)
          → "dá para salvar um pedaço no veranico, não o roçado" (conta física)
          irriga → aviso: "o ZARC é de sequeiro; na parte irrigada as datas mudam"
 3. Tamanho do roçado [ 3 ] (ha | tarefas)   Tem baixio? [sim][não][não sei]
    muda: o tamanho das partes A/B/C e o retorno em R$ (sem área → R$ por ha)
 4. Tem criação?  [cabras/ovelhas] [gado] [nenhuma]
    muda: o destaque da forragem (sorgo, palma, gliricídia)
 5. Já tem guardado:  [✓ semente de caupi] [✓ maniva] [✓ mudas de palma]
    muda: a lista "Agora" do passo 4
 6. (opcional) De onde vem o vento forte?  ( N / L / S / O )  [não sei]
    muda: o lado da borda protetora (passo 4); "não sei" = leste, suposição
 [ Pular perguntas: usar o melhor caso ]                 [ Ver meu plano → ]
```

- AD1–AD6 só aparece no modo técnico; no modo agricultor fica "não sei = melhor caso".
- Água, área, criação, guardado e vento mudam só a tela no navegador; a API hoje só recebe o solo.

### PASSO 4: Como plantar e distribuir (José + Vicente)

```
 [ 2027 ] [ 2028 ] [ 2029 ]   [▶ ver girar]            solo: areia ✎  área: 3 ha ✎
┌──────────── seu roçado visto de cima · 3 ha ─────────────────────────┐
│ ▒▒▒▒ BORDA: palma + gliricídia, em curva de nível · lado do vento: L ▒▒▒│
│ ┌ Parte A · 0,67 ha ┐ ┌ Parte B · 0,67 ha ┐ ┌ Parte C · 0,67 ha ┐    │
│ │ MANDIOCA (tampão) │ │ CAUPI             │ │ SORGO FORRAGEIRO  │    │
│ │                   │ │ metade guardada   │ │                   │    │
│ │                   │ │ até ~10/mar       │ │                   │    │
│ └───────────────────┘ └───────────────────┘ └───────────────────┘    │
│ ~~~~~~~ BAIXIO · 1 ha: MILHO + caupi no milho em pé (50–85 dias) ~~~~~~│
└──────────────────────────────────────────────────────────────────────┘
  Siga a cor: a cultura troca de parte a cada ano (leguminosa → cereal → mandioca).
 [ lupa: ver por dentro da Parte B ]  ← camada PercolaCampo
 ┌ por dentro da parte (desenho) ─────────────────────────────────────┐
 │ vento L →  ▒ ▒ ▒ barreira (2 primeiras linhas)                     │
 │   milho | caupi | milho | caupi | milho …   covas a [70 cm ◄►]      │
 │ 1. Distância entre covas  2. Barreira contra o vento                │
 │ 3. Casa das joaninhas: mata ou faixa florida ≥ 40% no entorno       │
 │ [▶ Por que faixas? ilustração de praga, dia 1 → 15] (modelo teórico)│
 └────────────────────────────────────────────────────────────────────┘
┌ LINHA DO ANO · hoje → dez/2027 ──────────────────────────────────────┐
│            nov dez jan fev mar abr mai jun jul ago set out nov dez   │
│ Marcos      ①   ②    ③      ④ ⑤   ⑥                ⑦        ⑧      │
│ Parte A     .   .   ░░▓▓▓▓▓·····························→ colhe 2028│
│ Parte B     .   .   ░░░░░░░▓▓▓▓▓·····███                            │
│ Parte C     .   .     ░░▓▓▓▓▓▓▓▓▓····████████                       │
│ Baixio      .   .     ▓▓▓▓░░·········████                           │
│ ░ dá com risco (até 40%)  ▓ plantar (ZARC)  · na roça  █ colher  │ hoje│
└──────────────────────────────────────────────────────────────────────┘
 AGORA (14/11): ☐ semente de caupi até dez  ☐ maniva p/ fev  ☐ mudas de palma
                ☐ Garantia-Safra  ☐ aceiro e nada de fogo
```

No celular:
- Os anos trocam com o dedo.
- A linha do ano vira lista vertical por parte: "Parte B · Caupi · plantar 11/03–20/04 · colher 10/05–04/07", com uma barrinha.

### PASSO 5: Quanto rende

```
 Quanto rende o plano em 3 anos · R$ de 2025 · sua roça de 3 ha
 Como vai ser 2027?  [ normal ] [ El Niño forte ● ] [ seca ]
 Preço da raiz:  [ Quixadá ● ] [ mediana CE ] [ baixo (P25) ]
 ┌──────────────────────────────────────────────────────────────┐
 │ R$  +│        ▇▇ entra                ▇▇▇▇        ▇▇▇▇         │
 │     0├────────────────────────────────────────────────────    │
 │     -│  ▇▇ sai (maniva, sorgo)                                │
 │       2027 (o plano investe)       2028 (paga)   2029 (paga)  │
 │  ── caixa acumulado do plano    - - - como é hoje (milho+feijão)│
 └──────────────────────────────────────────────────────────────┘
 ⇒ Em 3 anos: de +R$ 4,0 mil a +R$ 14,0 mil acima de hoje (depende do preço da raiz)
 ⇒ Chance de não pagar o desembolso: hoje 68% → plano 34%  (El Niño: 75% → 41%)
 Por que não tudo mandioca? Renda máxima ≠ roça segura: comida, gado e risco de mercado.
 Fora da conta: mão de obra da família · forragem para as cabras (valor de uso) · Garantia-Safra
```

Fora de Quixadá:
- O valor sai em R$ por ha pela mediana do município, a partir do PAM.
- Onde o PAM é misto ou irrigado, aparece o selo "lavoura comercial misturada".

### PASSO 6: Segurança por colheita (projeção por ciclo)

```
 Cada colheita do plano: o que aconteceu nos anos parecidos (IBGE PAM, Quixadá, 1998–2025)
 2027 · sabemos que é El Niño forte (medido hoje)
 COLHEITA             QUANDO      RENDA POR HA (p10 ─ p50 ─ p90)            LUZ
 Caupi · Parte B      mai–jul/27  ├────────●──────────┤  ◆16 ◆10 ◆98 ◆24      ◐
 Milho · Baixio       mai–jul/27  ├─●──────────────────────┤ ◆◆◆ ~R$ 184    ●vermelho
 Sorgo forr. · C      mai–ago/27  uso no gado · sem preço (só risco ZARC 20%) ◐
 2028 e 2029 · ainda não sabemos o clima: vale a história inteira (faixa mais larga)
 Mandioca · Parte A   fev–set/28  ├──────────●──────────────┤ El Niño ≈ 1,0× ●verde
 …
 ┌ série temporal · R$/ha do milho ───────────────────────────────────┐
 │  ●  ● ◆ ●  ●●   ● ◆  ●  ●  ●●  ● ◆ ●  …  ● ◆ │hoje│▓▓2027▓▓│░░2028░░│░░2029░░│
 │ 1998 …………………………………………………………… 2025      ◆ El Niño forte  ▓░ faixa projetada  │
 └─────────────────────────────────────────────────────────────────┘
 Portões do ano: a luz acende ao longo da estação → 19/mar (último dia de troca) · 30/abr (só salvar)
 Sabemos: ONI, SMAP, ZARC, 28 anos do IBGE. Ainda não sabemos: o Atlântico, o preço de 2028.
 Confirme com o técnico: o solo, o baixio, a semente.
```

Regra da luz por ciclo (suposição rotulada, mostrada em "como funciona"):
- verde = risco 20% no ZARC e pagou a semente em ≥ 8 de cada 10 anos;
- vermelho = risco 40% ou fora do ZARC, ou pagou em < 5 de 10;
- amarelo = o resto.

Com n < 10 (anos de El Niño), a tela mostra os anos um a um e nunca "de cada 10".

## 4. Como projetar dada a série temporal (o lado da UX)

Não usar tendência nem ARIMA com 28 pontos ruidosos. A projeção por ciclo é a **distribuição empírica do próprio município**, a preço de 2025 pelo IPCA:
1. **2027:** distribuição condicionada ao El Niño forte medido hoje (anos 1998, 2010, 2016 e 2024; n = 4, mostrados ano a ano).
2. **2028 e 2029:** todos os 28 anos, porque o ENSO não dá informação a mais de um ano.
3. **A janela vem do ZARC oficial:** risco de 20/30/40% = a chance oficial de perda.

Na tela, "projeção" sempre significa "o que aconteceu em anos parecidos", nunca "o que vai acontecer". A faixa mais estreita e deslocada em 2027 e mais larga em 2028–29 conta, sem palavras, quanto sabemos em cada horizonte.

## 5. Medido × suposição × projeção (o selo de cada número)

| Na tela | Tipo | Fonte |
|---|---|---|
| ONI +2,46, SMAP 8/12, chuva ago–nov 6 mm, ZARC 2026/27, PAM 1998–2025, custos CONAB | medido (a chuva recente é preliminar) | /api/local; painel_mun_cultura_ano.parquet; conab_custos_ne.csv |
| Aptidão GAEZ | modelo (clima médio) | /api/local cardapio |
| Datas de colheita = janela + ciclo; ciclos sem fonte (sorgo, palma…) | suposição onde a API diz "suposição" | agenda.linhas[].colher |
| Faixa de renda por ciclo 2027/28/29 | projeção (anos parecidos) | JSON financeiro novo |
| Partes de tamanho igual, baixio = metade milho e metade feijão, vento leste se "não sei" | suposição | 10_familia.py; resposta 6 |
| "% da lavoura salva", ganho das faixas | modelo teórico (fora da tela do agricultor) | PercolaCampo v3:952-959 |
| Cisterna → mm sobre a área | conta física (1 mm em 1 ha = 10 mil L) | resposta 2 |

## 6. Contrato de estado da página

```js
estado = { cod:'2311306', lat, lon, passo:1..6,
  pratica:'consorcio_1a_chuva|outra|nsei', solo:{textura:''|'1'|'2'|'3', ad:''},
  agua:'chuva|cisterna|irriga|nsei', area:{v:3, un:'ha|tarefa'}, baixio:'sim|nao|nsei',
  criacao:'cabras|gado|nenhuma|nsei', guardado:{caupi:false, maniva:false, palma:false},
  vento:'N|L|S|O|nsei', ano2027:'el_nino|normal|seca', preco:'mun|uf|p25', tecnico:false }
URL: #/2311306/4?t=1&ag=chuva&a=3ha&bx=1&cr=cabras&v=L
```

Fontes de dados por passo:
- Passos 2 e 4: `/api/local?lat&lon&textura&ad` (motor do José).
- Passos 5 e 6: `dados/fin/<cod>.json`, novo:

```json
{"cod": "2311306", "misto": false,
 "culturas": {"Milho": {"n": 28, "p10": 182, "p50": 622, "p90": 1851,
                        "el_nino": {"1998": 0, "2010": 0, "2016": 0, "2024": 0},
                        "serie": {"1998": 0},
                        "custo": {"semente": 0, "desembolso": 0, "fonte": "CONAB Crateús"}}}}
```

(Os zeros só marcam a forma; os valores saem do parquet.)

- Passo 4, lupa: configuração fixa do desenho, com espaçamento por cultura e borda do lado do vento.

## 7. Modo celular (resumo)

- Uma coluna, barra Voltar/Próximo fixa embaixo, alvos ≥ 48 px, letra de 18 px (tokens do Vicente: Atkinson Hyperlegible, semáforo s-ok, s-warn e s-bad).
- O globo entra em qualidade baixa ou é pulado.
- A malha vem do malha_ne.json com gzip, não dos 2,8 MB da /api/municipios.
- As tabelas só aparecem no modo técnico.
- O Gantt vira lista vertical.
- Os anos do roçado trocam com o dedo.

## 8. Vídeo de 30 s (inglês, só Quixadá, legendas na tela)

| Tempo | Tela | Legenda |
|---|---|---|
| 0–4 s | globo girando até o NE, contorno dourado | "1,794 municipalities. What to plant, when, in which order?" |
| 4–8 s | mergulho em Quixadá, faixa HOJE | "El Niño +2.46: strongest Aug–Oct since 1950 (NOAA)" |
| 8–12 s | cardápio acendendo | "NASA POWER · GPM IMERG · SMAP + FAO GAEZ + official ZARC" |
| 12–16 s | 3 toques (areia, só chuva, cabras) e a janela da maniva encolhendo | "Answer what you know. Every answer changes the plan." |
| 16–22 s | roçado girando 2027→2028→2029, faixas e borda contra o vento | "Rotation in 3 parts + strip layout against pests and wind" |
| 22–27 s | curva do caixa caindo e subindo; faixas de segurança | "Costs in 2027, pays in 2028–29. Cassava held normal in all 4 strong El Niños." |
| 27–30 s | marca QUADRA | "NASA data → a plan a farmer can read. Supports the extension agent; doesn't replace them." |

## 9. Slides (≤ 7)

1. O problema (a 1ª chuva engana e o El Niño de 2026).
2. A jornada em 6 passos (este stepper).
3. Que dado da NASA alimenta cada passo.
4. O plano: rotação A/B/C + desenho das faixas.
5. Retorno e segurança por colheita.
6. Honestidade: o que é medido, suposto e projetado, onde erramos.
7. Equipe (José: motor/protótipo; JP: globo/interface; Vicente: desenho da roça/PercolaCampo) e próximos passos.

## 10. Cronograma até 15/11 23:59

| Quando | O quê |
|---|---|
| Hoje 19–23h | decisões (marca, El Niño), cópia das partes para site-versao-final, JSON financeiro |
| Sáb 08–12h | casca do stepper + passos 1 e 2 |
| Sáb 12–16h | passos 3 e 4 (camada PercolaCampo estática) |
| Sáb 16–19h | passos 5 e 6 |
| Sáb 19–21h | celular + gravação do vídeo |
| Sáb 21–23:59 | slides, entrega, folga |

Corte se apertar, nesta ordem:
1. modo técnico;
2. simulador do PercolaCampo (fica só o desenho estático);
3. gráfico da série no passo 6 (ficam só as faixas por ciclo).

## Riscos
- Três mensagens de El Niño (município do José, estado do JP, anos ONI ≥ 1 do Vicente) na mesma página se contradizem diante do júri e do agricultor.
- Os números do PercolaCampo (92% da lavoura salva, ganho de 25–40%) saem de constantes ad hoc e de vento fixo no código, e não foram medidos no semiárido. Se aparecerem como resultado, um avaliador cético derruba a credibilidade do resto. Também convém conferir a referência 'González-Martínez et al. 2026, Chaos 36(9)'.
- O PAM municipal mistura irrigado e lavoura comercial: sem a marca 'misto', o passo 5 mostra em Barreiras um milho de R$ 5.887/ha como se fosse roça de sequeiro.
- Só 4 anos de El Niño forte: transformar isso em 'de cada 10' engana. Mostrar sempre os anos um a um.
- O caso financeiro completo é só de Quixadá, com família fictícia, e deixa de fora a mão de obra, a forragem e o Garantia-Safra. Nos outros municípios o retorno fica mais pobre (por ha).
- Perguntas que não mudam nada visível (criação, guardado) parecem de enfeite: cada uma precisa da linha 'muda:' ligada a uma saída real.
- Falta vento por município; a borda contra o vento depende da resposta do agricultor ou de um padrão rotulado como suposição.
- Celular: o globo pesa em aparelho fraco e /api/municipios tem 2,8 MB sem gzip; sem 'pular animação' e sem a malha leve, a pessoa desiste no passo 1.
- Iframe (padrão do JP) quebra o Voltar e a rolagem no celular; o stepper tem de ficar no mesmo documento.
- Prazo: reescrever as telas do José do zero consome o sábado; o caminho seguro é reaproveitar as funções de cartão e só trocar o layout.
- Datas de colheita de ciclos sem fonte (sorgo, palma, amendoim) aparecem no passo 6 como faixa 'segura'; precisam levar o selo 'suposição' que a API já devolve.
- Marcas misturadas (QUADRA, Roça Certa, PercolaCampo) e três estilos visuais confundem o vídeo de 30 s.

## Perguntas abertas
- Marca: QUADRA para tudo, com 'Roça Certa' como nome do plano do agricultor e o PercolaCampo como módulo 'desenho da roça (Vicente)'? É decisão de voz pública do José.
- Qual mensagem de El Niño fica como manchete: a do estado (validada pelo JP) ou a do município (motor do José)?
- Quem fez o site-nasa-v2? Ele é a base do passo 1 ou fica a v1 do JP? O JP precisa saber antes de amanhã.
- O júri vai abrir um link público (exige site estático e o motor pré-calculado para os 1.794 municípios) ou só ver o vídeo e o servidor local?
- O passo 5 completo fica só para Quixadá (família fictícia) e os outros municípios recebem R$/ha, ou vale gerar a família-modelo para todos com a área informada?
- Unidade de área: aceitar 'tarefa'? O tamanho muda por estado (CE ≈ 0,3 ha; BA ≈ 0,44 ha); é preciso confirmar a tabela antes de converter.
- A página precisa de alternância para o inglês, ou o vídeo legendado e os slides em inglês bastam para o júri?
- O Vicente concorda que o '% da lavoura salva' saia da tela do agricultor e fique só no simulador rotulado como modelo teórico?