# Crítico de viabilidade e honestidade (critico)

## Resumo
Dá para entregar até amanhã 23:59, mas só com estas condições. A base do sistema é o protótipo do José (motor.py mais o servidor stdlib): ele aguentou 40 de 40 municípios sorteados, com 0,54 s de mediana. Não fundimos os três "site-nasa": usamos um globo só, que se pula com um botão, e copiamos peças do JP e do Vicente para dentro do fluxo do José. Há três problemas de honestidade a resolver antes de mostrar qualquer número. (1) Cada parte usa um conjunto diferente de "anos de El Niño": 3, 4 ou 6 anos, conforme a parte. (2) As constantes e os "% de ganho" do PercolaCampo não estão nos artigos que o Vicente juntou, e o "Vento Hoje (Satélite)" é um texto fixo. (3) Uma projeção da série do PAM por município não acerta fora da amostra: treinando em 1998–2017, 33% dos milhos de 2018–2025 passaram do P90, e uma tendência ou uma janela mais recente não corrigem isso. Por isso, a "segurança" deve aparecer como "a faixa do passado conforme o tipo de ano", e não como previsão. O ano de 2027 tem um sinal medido (ONI +2,46), que vale para o estado e não para o município; para 2028 e 2029 não existe previsão do clima, só a faixa do passado. As perguntas entram logo depois da escolha do município, antes do plano. São no máximo 4 (solo, água, área, baixio), sempre com a opção "não sei", e cada resposta muda algo que a pessoa vê. O mínimo viável tem cerca de 19 h de trabalho para 1 pessoa mais IA. Se atrasar, os cortes já estão em ordem: o globo vira uma imagem, a grade do Vicente vira uma figura e as perguntas viram só solo e área. Nunca cortamos os selos medido/suposição/projeção nem o quadro dos 28 anos.

## Recomendações
- **P0** (0.5 h) Congelar 5 decisões antes de codar: (1) a base é o protótipo stdlib; (2) um globo só, o da v2 (bibliotecas locais, qualidade adaptativa) ou o do JP, decidido num teste de 15 min; (3) uma definição de El Niño (sugiro a do motor: ONI OND–NDJ ≥ 1,5, anos 1998, 2010, 2016 e 2024, que o financeiro já usa); (4) nome único QUADRA, com 'Roça Certa' como nome de tela; (5) o que fica público (repositório e site), por decisão do José — Sem isso, as três partes mostram números e nomes contraditórios na mesma demo
- **P0** (3 h) Montar site-versao-final/ copiando (sem mover) motor.py e app.py do protótipo, servindo uma página com 5 passos por hash (#globo, #lugar, #perguntas, #plano, #retorno). As peças do JP e da v2 entram como arquivos estáticos; nada de Flask nem de Node no produto final — Um servidor, uma pilha, e o motor já validado (40 de 40) segue intocado
- **P0** (1.5 h) Passo 'lugar' sem internet: mapa SVG com malha_ne.json do JP (457 KB) e busca pela lista local de /api/municipios no lugar do Nominatim. Botão 'Pular o globo' sempre visível e imagem de reserva se o WebGL falhar — A demo e a gravação não podem depender de Wi-Fi, do Nominatim nem de GPU
- **P0** (1.5 h) Passo 'perguntas' depois de escolher o município e antes do plano: solo (textura 1–3, o motor já aceita), água guardada (nenhuma, cisterna/barreiro ou poço/irrigação), tamanho do roçado (ha ou tarefas) e se há baixio. Sempre com 'não sei', que usa o padrão com o selo 'padrão' — São os dados que o agricultor sabe melhor que o satélite. Cada resposta muda algo na tela: as janelas, as partes A/B/C, os R$ totais e o baixio
- **P0** (2 h) Escrever exportar_financeiro.py (lê painel_mun_cultura_ano.parquet e conab_custos_ne.csv) → financeiro_mun.json com milho, feijão e mandioca por município: os 28 valores anuais, P10/P50/P90 em R$/ha e kg/ha, número de anos, anos de El Niño forte marcados, e se cada ano pagou a semente e o desembolso (este com selo de suposição). Mais a rota /api/financeiro?cod= — É o único jeito honesto de dar a 'perspectiva de segurança' por município; arquivo de ~300 KB
- **P0** (3 h) Tela 'retorno e segurança': um quadro com os 28 anos reais (um quadrado por ano, verde se pagou o desembolso, âmbar se pagou só a semente, vermelho se nem isso), mais 3 cartões de ciclo: 2027 (El Niño medido, chance do estado, os 4 anos fortes mostrados um a um), 2028 e 2029 (faixa do passado, 'sem previsão do clima'), e a comparação plano × prática atual do notebook com o selo 'simulação' — É visual, cada marca é um ano medido, e não promete previsão. Responde ao 'projeção por ciclo' sem fingir que se sabe o futuro
- **P0** (1.5 h) Selos em todo número (MEDIDO / SUPOSIÇÃO / PROJEÇÃO) com a fonte no tooltip. Trocar 'Neste município, nos 3 El Niños fortes...' por 'o que aconteceu aqui (3 anos, não é previsão)' e pôr a chance do estado como sinal principal — Evita que a projeção pareça previsão garantida e resolve a contradição município × estado
- **P0** (5 h) Vídeo de 30 s com legenda em inglês, gravado do fluxo real (roteiro abaixo), e os 7 slides em inglês a partir da v3 §11.1, com o fluxo novo no slide 5 — O júri vê o vídeo e os slides, não o servidor local
- **P0** (1.5 h) Rodar os testes de aceitação (lista na proposta) em Quixadá, Picos, Petrolina, Arapiraca e Barreiras, inclusive com o Wi-Fi desligado — Pega os números do CE vazando para outros estados, o El Niño inconsistente e a dependência de rede
- **P1** (1.5 h) Contribuição do Vicente no passo 'plano': caixa 'Por que faixas e não blocos' com uma grade de 30×30 em JS (mostra se o foco atravessa a roça em monocultivo × faixas × xadrez, com o limiar 0,5927) desenhada sobre as partes A/B/C e as bordas do José. Sem '% de plantas protegidas', sem 'ganho de colheita' e sem 'vento por satélite' — Aproveita a ideia real (a conectividade da lavoura) e a liga à distribuição espacial, sem números inventados
- **P1** (1.5 h) Contribuição do JP: o gráfico 'Seu estado nos anos de El Niño' do rocacerta.js recalculado com o conjunto canônico, os créditos e licenças, e a ferramenta de captura (captura.py ou captura.mjs) para tirar os quadros do vídeo — Mostra o trabalho do JP sem trazer o Flask e as dependências de CDN
- **P1** (0.5 h) Gerar JSON estático para os 5 municípios da demo (e os 1.794, cerca de 16 min, só se o site for publicado) como reserva do motor — Se o servidor ou o E: falharem na gravação, o fluxo continua
- **P2** (0.5 h) Pedidos aos colegas: JP sobe jp_analogos_atlantico.py e embasamento_painel_nordeste.md; Vicente diz de onde vêm as constantes k_geom, q e α e confere González-Martínez 2026. Até lá, nenhum desses números aparece — Afirmações sem arquivo não entram no deck (regra da v3 §9.7)
- **P2** (0.5 h) Antes de publicar: trocar os PDFs com copyright por DOIs, deixar os créditos visíveis e tirar os easter eggs do produto — Licença e foco
- **P2** (8 h) Depois da entrega: seletor de AD para milho e feijão comum, portarias plurianuais fora do CE (A1), ciclos com cultivar fora do CE, preço na porteira, valor de uso da forragem — Está pendente na REVISAO_10_AGENTES e não cabe até 23:59

## Achados
- **O motor do José aguenta como base: estável, rápido e cobre o NE inteiro**: Sorteei 40 municípios do NE: 40 respostas OK, 0 erros, nenhum campo vazio (cardápio, plano, agenda, este_ano). Cada resposta pesa cerca de 43 KB. Exportar os 1.794 municípios em JSON estático levaria uns 16 min em série (~77 MB). O motor só roda na máquina do José: ele lê dados do E: (GAEZ, SMAP, ZARC, IBGE), usa geopandas e o módulo POWER (ao vivo só fora do NE). Para a demo, use o servidor ao vivo e guarde JSON pré-gerado dos 5 municípios da demo como reserva. _[scratchpad/analise10/critico/amostra_api.py → 'ok=40 erros=0 vazios={} tempo mediano=0.54s max=0.90s'; curl /api/local Quixadá 200, 0,71 s, 42.953 B; motor.py:95-164 (leituras de DADOS no E:)]_
- **Três interfaces duplicadas com pilhas diferentes; a v3 tinha mandado abandonar o globo**: Hoje existem três versões da interface: site-nasa do José (Flask, 8 MB), site-nasa do JP (Flask, 16 MB, com o painel Roça Certa, ovos.js, util.js e malha_ne.json) e site-nasa-v2 (Node estático, bibliotecas copiadas para vendor/, texturas de 1K a 8K, criada hoje entre 12:14 e 12:59 na pasta do José, autor não confirmado). A PROPOSTA v3 §10 dizia: 'A página é estática e não chama nenhuma API ao vivo. O site-nasa antigo (Flask, Nominatim, globo 3D...) é abandonado'. O pedido de hoje do José (globo → Nordeste → protótipo) passa por cima disso. O risco é real: o globo é a peça mais frágil da demo. _[diff -rq site-nasa colegas/joao-pedro/site-nasa (20+ arquivos diferentes); site-nasa-v2/README.md; proposta/PROPOSTA_FINAL_v3.md §10, bloco 'Arquitetura' (linhas ~1360-1375)]_
- **El Niño: três definições e três conjuntos de anos entre as partes**: José (motor): FORTES = ONI OND–NDJ ≥ 1,5; o texto da tela cita 2010, 2016 e 2024, e vale por município. Notebook financeiro: 1998, 2010, 2016 e 2024. JP: ONI jul–set ≥ 0,5, ou seja 1998, 2003, 2005, 2010, 2016 e 2024, por estado. Vicente: '1998, 2016 e 2024'. Na mesma demo, uma tela diria '3 anos', outra '4' e outra '6', e a manchete da v3 (§9.2 #9, '~5 em 10', só CE) é um quarto número. Contradição de fundo: o JP mostra o sinal só por estado porque a contagem municipal não supera o acaso. A v3 §9.2 #10 dá o mesmo recado: 'os satélites sabem o ano, não o município'. Mesmo assim, o protótipo do José escreve 'Neste município, nos 3 El Niños fortes...'. Isso é descritivo e tem n=3, mas parece previsão municipal. _[protótipo/motor.py:109 e :996; notebooks/secoes_financeiro/06_risco.py:119, 10_familia.py:20, 90_sintese.py:73; colegas/joao-pedro/site-nasa/README.md seção 'Painel Roça Certa' e static/js/rocacerta.js:55; colegas/vicente/interface-inicial-vicente/fonte/pagina.html ('Anos parecidos... 1998, 2016 e 2024')]_
- **A prova do JP para 'El Niño por estado' não está na branch**: O README do JP cita conselho/analises/jp_analogos_atlantico.py (o teste deixando um ano de fora, AUC ≈ 0,5), pesquisa/embasamento_painel_nordeste.md, testes/test_analise_nordeste.py e requirements-dev.txt. Nenhum deles existe em origin/estudo-jp (29f81f6), e por isso a afirmação não se reproduz. A conclusão bate com a v3 §9.2 #10, que tem arquivo, e é nela que devemos nos apoiar até o JP subir os arquivos. Outro ponto: rascunhos/decisao_api.py está quebrado, segundo o próprio cabeçalho (todo código IBGE dá 404), e fica de fora. _[git ls-tree -r --name-only origin/estudo-jp | grep -E 'analogos_atlantico|embasamento_painel|test_analise_nordeste|requirements-dev' → rc=1; colegas/joao-pedro/site-nasa/rascunhos/decisao_api.py:1-8]_
- **PercolaCampo (Vicente): os conceitos são reais; as constantes e os ganhos não estão nos artigos**: Os artigos existem: Ramírez 2018 e 2020, Alonso-Tlali 2025, Poggi 2013, Cunniffe 2014 e With 2002. O limiar 0,5927 da malha quadrada também é real. Os artigos mostram que o padrão xadrez/diagonal é o que melhor bloqueia o contágio. Não estão em nenhum deles: as constantes k_aleatório 0,42, k_faixas 0,56 e k_xadrez 0,72, o q = 1,35, o α 4,8/2,6 e a conversão 'plantas protegidas = 108 − 34·R_eff' (presa entre 28 e 98). O texto de Alonso-Tlali 2025 não tem nenhum '%', e mesmo assim a Tabela 1 do dossiê atribui a ele '+18–32%' e '+25–40% de colheita'. González-Martínez 2026 (Chaos 36(9) 093144) não está na pasta de artigos e não tenho como conferir. Os artigos tratam de pimenta e Phytophthora no México, couve-flor, citros e pulgões: nenhum fala de mandioca, caupi ou sorgo no semiárido (só Cunniffe trata de citros na Bahia). E no sertão a perda principal vem da falta de água, não de pragas. Por fim, 'Vento Hoje (Satélite)' é um texto fixo por terreno, sem nenhum fetch. _[percolacampo_v3_*.html:181, 817, 838, 858 (vento fixo), :940-959 (constantes e protectedPct); dossi_completo...md:28-31, 101, 137; pdftotext entropy-27-00386.pdf | grep -c '%' → 0; grep cassava|cowpea|sorghum|semi-arid|Brazil → 0 em 5 dos 6 PDFs (file.pdf = Cunniffe: 21)]_
- **O financeiro por município é viável só para 3 culturas**: painel_mun_cultura_ano.parquet: 386.543 linhas, 1998–2025, 8 produtos, 1.791 municípios. Com 20 anos ou mais de série: feijão em 1.662 municípios, milho em 1.630, mandioca em 1.490. O resto é pouco: amendoim 147, algodão 82, mamona 79, sorgo 41. No PAM, 'Feijão' soma caupi e feijão comum. A planilha de custo da CONAB vem de lavouras com rendimento 1,7 a 3,4 vezes o do PAM, então 'não paga o desembolso' sai pessimista e deve levar o selo 'suposição'. Em Quixadá, a mandioca de 2016 rendeu R$ 8.957/ha, acima da mediana de R$ 5.017, porque o preço subiu na seca: a receita parece segura, mas só é para quem vende. _[scratchpad/analise10/critico/painel.py (Quixadá: milho P10/P50/P90 = 182/622/1.851 R$/ha; feijão 574/1.340/2.386; mandioca 2.401/5.017/11.923; milho 1998 = 0 kg/ha); notebooks/secoes_financeiro/90_sintese.py (custos CONAB 1,7–3,4×)]_
- **Projetar pela série temporal não funciona fora da amostra: o tipo de ano decide**: Testei treinar em 1998–2017 e conferir em 2018–2025, município a município. MILHO: 33% dos municípios têm tendência de alta significativa; nos anos de teste, só 5% ficaram abaixo do P10 e 33% passaram do P90 (o esperado é 10% e 10%). FEIJÃO: 11% e 21%. MANDIOCA: 23% abaixo do P10, com 31% de tendência de queda e 29% dos anos repetindo o rendimento do ano anterior (imputação do PAM, o que faz o risco parecer menor). Usar só a janela de 2006–2017, ou uma tendência Theil–Sen encolhida, não melhorou a calibração. Os 8 anos de teste funcionam como uns 8 sorteios só, porque o choque do ano é o mesmo em toda a região (2018–2024 foi uma sequência úmida). ARIMA, Prophet ou tendência dariam uma previsão com falsa segurança. _[scratchpad/analise10/critico/serie.py e serie2.py (saída: 'Milho A: abaixo P10 5% | acima P90 33% | <=P50 31%'; 'Mandioca A: 23% | 17% | 59%'; métodos B e C iguais dentro de ±3 p.p.)]_
- **Na demo, quase tudo depende de internet, e o repositório está privado**: Protótipo: cdnjs (Leaflet) e ladrilhos do OSM. JP: jsDelivr e Google Fonts nos templates, mais Esri Wayback, EOX s2maps, OpenFreeMap, AWS Terrain e a malha do IBGE baixada na hora. v2: tem as bibliotecas locais, mas busca no Nominatim e usa os mesmos ladrilhos. PercolaCampo: Tailwind pelo CDN 'play', que não serve para produção. O github.com/Netinhoklz/competicao-nasa responde 404 para quem não está logado, ou seja, é privado. O Space Apps pede o link do projeto e uma demo com acesso público. Publicar é decisão do José ('voz pública'). _[grep -o https?://host nas pastas static/templates/js (resultado listado); curl -s -o /dev/null -w '%{http_code}' https://github.com/Netinhoklz/competicao-nasa → 404]_
- **Licenças: dá para usar no desafio, com atribuição visível. PDFs não podem ir para repositório público**: Sentinel-2 cloudless é CC BY-NC-SA 4.0 (uso não comercial, com atribuição). Esri Wayback pede atribuição. Os ladrilhos do OSM e o Nominatim têm política de uso leve, com atribuição. Solar System Scope é CC BY 4.0. Three.js é MIT e MapLibre é BSD. As imagens da NASA são de domínio público, mas o logo da NASA não pode aparecer. A branch do Vicente versiona 6 PDFs: os da PhysRevE (APS), Phytopathology (APS) e Ecol. Appl. (With 2002) têm copyright; Entropy (MDPI) e PLoS CB são CC BY. Se o repositório ficar público, troque esses PDFs por DOIs. _[colegas/joao-pedro/site-nasa/README.md 'Fontes de dados e créditos'; git ls-tree -r --name-only origin/estudo-vicente | grep -c '\.pdf$' → 6]_
- **Regras do Space Apps que afetam o corte**: Pelo guia de 2025: a demo é um vídeo de até 30 s com legenda em inglês OU até 7 slides em inglês contando a capa. Ela fica num site externo com acesso público e precisa mostrar o nome da equipe, os integrantes, o desafio e como os dados abertos das agências espaciais foram usados. A busca não achou uma regra explícita de declarar uso de IA; confira no guia de 2026 e declare de qualquer jeito (o slide 6 da v3 já faz isso). Como o júri vai ver o vídeo e os slides, e não o servidor local, o vídeo vale mais do que o polimento do site. _[WebSearch: spaceappschallenge.org/resources/project-submission-guide/ e o guia de 2025 (demo de 30 s ou 7 slides; hospedada fora)]_
- **Mesmo nome em produtos diferentes e números do CE em telas do NE**: 'Roça Certa' é o nome do painel do JP e também da interface do Vicente; 'PercolaCampo' é um terceiro nome; o produto é QUADRA. As manchetes da v3 (§9.2) são do CE (184 municípios), e o protótipo cobre 1.794. A revisão do José já tinha achado 'o alerta do CE vale para os 9 estados'. Isso precisa de teste de aceitação em Petrolina e Barreiras. _[protótipo/REVISAO_10_AGENTES.md:20-48; proposta/PROPOSTA_FINAL_v3.md §9.2]_

## Reaproveitar
- protótipo/motor.py + protótipo/app.py → site-versao-final/servidor/: Copiar sem mudar a lógica; acrescentar só a rota /api/financeiro?cod= no app.py
- protótipo/static/app.js (Gantt, roçado A/B/C, cardápio) → site-versao-final/static/passos/: Separar em plano.js e opcoes.js, chamados pelos passos 3 e 4
- site-nasa-v2/js/espaco.js, qualidade.js, nordeste.js, vendor/ (three 0.160, maplibre 5.24), texturas 1K–4K, fontes/ → site-versao-final/static/globo/: Passo 0, com botão Pular; sem Nominatim (a busca usa a lista local)
- colegas/joao-pedro/site-nasa/static/data/malha_ne.json → site-versao-final/static/dados/: Mapa SVG offline do passo 1 (1.794 municípios e divisas)
- colegas/joao-pedro/site-nasa/static/js/rocacerta.js (gráfico do estado nos anos de El Niño, escalaOni) e util.js (dentroDoNordeste) → site-versao-final/static/passos/opcoes.js: Gráfico 'Seu estado nos anos de El Niño' recalculado com o conjunto canônico; validação do clique
- colegas/joao-pedro/site-nasa/ferramentas/captura.py ou site-nasa-v2/ferramentas/captura.mjs → site-versao-final/ferramentas/: Capturas automáticas para os testes de aceitação e quadros para o vídeo
- colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_*.html (desenho do terreno, botões de faixa e borda) → site-versao-final/static/passos/faixas.js: Só a interface e a ideia de conectividade: grade 30×30 com monocultivo/faixas/xadrez e o limiar 0,5927; sem k_geom, q, R_eff→% e vento fixo
- colegas/vicente/interface-inicial-vicente (página 'Como eu funciono') → site-versao-final/static/passos/fontes.js: Modelo da aba 'De onde vem cada número', junto com o 'De onde vem cada regra' do protótipo
- notebooks/secoes_financeiro/04_receita.py, 05_custo.py, 06_risco.py, 10_familia.py, 90_sintese.py → site-versao-final/ferramentas/exportar_financeiro.py: Lógica do exportar_financeiro.py (lê o painel parquet e o CSV da CONAB; não executa os notebooks) e os números de plano × atual
- proposta/PROPOSTA_FINAL_v3.md §9.2, §9.7, §11.1, §11.2 → slides/ e vídeo: Folha de números canônicos, 7 slides e cuidados do vídeo (família fictícia rotulada, sem logo da NASA)
- scratchpad/analise10/critico/serie2.py e amostra_api.py → site-versao-final/ferramentas/testes/: Teste de calibração da faixa e teste de aceitação com 40 municípios

## Proposta detalhada
## 1. Arquitetura mínima (uma pilha só)

```
site-versao-final/
  servidor/app.py        <- cópia do protótipo/app.py + rota /api/financeiro?cod=
  servidor/motor.py      <- cópia sem mudança de lógica (DADOS continua no E:)
  ferramentas/exportar_financeiro.py   ferramentas/exportar_demo.py
  static/index.html      <- 5 passos, roteador por hash
  static/globo/          <- da site-nasa-v2 (espaco.js, qualidade.js, nordeste.js, vendor/, texturas 1K–4K)
  static/dados/malha_ne.json (JP)  financeiro_mun.json  demo/<cod>.json
  static/passos/lugar.js perguntas.js plano.js (Gantt+roçado do protótipo) faixas.js (Vicente) retorno.js
  CREDITOS.md  README.md
```
O que fica de fora: Flask, Node, Nominatim, os ladrilhos de satélite como requisito, ovos.js e decisao_api.py.

## 2. Fluxo e onde entram as perguntas

```
[0 Globo] -> "Entrar no Nordeste" / "Pular"     (rotação 5 s; reserva: imagem estática)
[1 Lugar] mapa SVG dos 1.794 + busca local -> clique no município
          faixa de 1 linha: "Quixadá-CE · estação jan–abr (IMERG) · ONI +2,46 (medido)"
[2 Perguntas] (4 cartões grandes, cada um com "não sei")
   Solo na chuva forte?  some rápido | demora | empoça   -> textura 1/2/3 (o motor usa)
   Água guardada?        nenhuma | cisterna/barreiro | poço/irrigação -> texto/escopo*
   Tamanho do roçado?    [ 2 ] ha (ou tarefas)          -> R$ totais e tamanho de A/B/C
   Tem baixio?           sim | não                      -> mostra/oculta a faixa do baixio
   *irrigação: "o plano é de sequeiro; com irrigação as janelas do ZARC não valem"
[3 Opções] cardápio de 15 culturas (semáforo ZARC/GAEZ) + "Este ano":
   sinal = chance do ESTADO (CE: ~5 em 10 contra 2 em 10, v3 §9.2 #9)
   "O que aconteceu aqui" = os 3–4 anos fortes do município, com selo "não é previsão"
[4 Plantação e distribuição] roçado visto de cima (A/B/C + baixio + bordas) por ano,
   Gantt até dez/2027, e a caixa do Vicente "Por que faixas": grade 30×30,
   botões monocultivo/faixas/xadrez, o foco atravessa ou não (ilustração do conceito)
[5 Retorno e segurança] (ver 3)
```
As perguntas entram depois do passo 1: a pessoa já viu que o lugar foi reconhecido e ainda não viu o plano, que depende das respostas. O solo continua editável no passo 4.

## 3. Projeção por ciclo, de forma honesta

- **Medido:** os 28 anos do PAM (1998–2025) do município em kg/ha e em R$/ha de 2025 (preço do PAM deflacionado pelo IPCA).
- **Quadro de segurança:** 28 quadrados, um por ano real.
  - verde: pagou o desembolso (CONAB, selo de suposição);
  - âmbar: pagou só a semente;
  - vermelho: não pagou nem a semente.
  - Os anos de El Niño forte ficam contornados.
  - Texto: "Em 28 anos medidos aqui, a roça de milho pagou a semente em X."
- **Ciclo 2027** (caupi e milho colhidos em mai–jul/2027):
  - O ONI +2,46 é medido. A chance de quebra é a do estado: no CE vem da v3 §9.2 #9; nos outros estados, a contagem do JP com o conjunto canônico, ou "não avaliado".
  - Os 4 anos fortes aparecem um a um, como pontos, sem média. No milho do NE: 0,38, 0,80, 0,47 e 1,27 do normal (06_risco.py:122).
- **Mandioca plantada em fev/2027, colhida em 2028:** faixa P10–P90 alargada, com o aviso "29% dos anos repetem o anterior no PAM".
- **Ciclos 2028 e 2029:** "sem previsão do clima: é o que o passado daqui mostra" (faixa P10–P50–P90).
  - Nota fixa: "2018–2025 vieram acima da faixa em 1 de cada 3 municípios no milho; a faixa não é promessa."
- **Não usar** ARIMA, Prophet nem tendência. O teste fora da amostra (serie2.py) mostrou que nada disso calibra: o ano decide.
- **Plano × prática atual:** números do notebook, com o selo "simulação com o passado (NE)".
  - Não pagar o desembolso: 68% → 34%; em El Niño forte, 75% → 41%.
  - Pior decil: R$ 351 → R$ 1.431/ha.

## 4. Plano hora a hora (sáb 14/11, 18:30 → dom 15/11, 23:59)

| Quando | Tarefa | Pronto quando |
|---|---|---|
| Sáb 18:30–19:00 | As 5 decisões congeladas; esqueleto de site-versao-final/ | README com as decisões |
| 19:00–20:30 | Servidor copiado + index com 5 passos; globo v2 com botão Pular; mapa SVG + busca local | Quixadá abre do globo ao passo 3 sem internet |
| 20:30–21:30 | Passo de perguntas ligado a textura, área e baixio | Mudar o solo muda a janela (01/02–10/03 → 11/02–28/02 em Quixadá arenoso) |
| 21:30–23:00 | exportar_financeiro.py + /api/financeiro | Quixadá: milho P50 ≈ R$ 622, feijão ≈ R$ 1.340, mandioca ≈ R$ 5.017; medianas do NE batem com o 90_sintese (598 / 1.182 / 5.342) |
| 23:00–00:30 | Tela de retorno (28 quadrados + 3 cartões + plano × atual) | Todos os números têm selo |
| 00:30–01:30 | Plano: roçado + Gantt (reuso do protótipo) + caixa de faixas do Vicente | Sem % de ganho na tela |
| 01:30 | **Números congelados** | — |
| 01:30–07:30 | Sono | — |
| Dom 08:00–09:30 | Harmonizar o El Niño, trocar os textos municipais, selos | grep do conjunto de anos dá um só |
| 09:30–10:30 | Testes de aceitação + JSON de reserva dos 5 municípios | Checklist todo verde |
| 10:30–13:30 | 7 slides em inglês (PDF) | ≤ 3 números por slide; capa conta como slide |
| 13:30–15:30 | Gravação e edição do vídeo de 30 s com legenda | ≤ 30 s, legendado |
| 15:30–17:00 | Checagem cruzada (slides × site × folha 9.7), CREDITOS.md, declaração de IA | Nenhuma divergência |
| 17:00–18:30 | Publicação do vídeo e dos slides com link público; formulário do Space Apps (o repositório público só com o OK do José) | Submetido |
| 18:30–23:59 | Folga para imprevistos | — |

## 5. O que cortar se atrasar (nesta ordem)

1. O globo 3D vira imagem estática do NE com o botão "Entrar" (o globo pode aparecer só nos 3 s iniciais do vídeo).
2. A grade interativa do Vicente vira 2 figuras (monocultivo × faixas) com 3 linhas de texto.
3. Os cartões de 2028 e 2029 viram um só: "anos seguintes: faixa do passado".
4. As perguntas viram só solo e área.
5. O gráfico do estado do JP vira uma frase com o número canônico.
6. Os slides caem para 5.

**Nunca cortar:** os selos medido/suposição/projeção; a definição única de El Niño; o quadro dos 28 anos; Quixadá rodando sem internet; o vídeo com legenda.

## 6. Testes de aceitação

1. Fluxo completo em Quixadá, Picos, Petrolina, Arapiraca e Barreiras: 0 erro no console, menos de 3 s por passo.
2. Wi-Fi desligado: o fluxo roda; só os ladrilhos somem, com aviso.
3. Fora do CE, nenhum número que é só do CE: procurar 'CE' e os números da §9.2 no JSON de Petrolina e Barreiras.
4. Um só conjunto de anos de El Niño em todas as telas.
5. Os números financeiros de Quixadá e as medianas do NE batem com o notebook.
6. Zero ocorrências de 'garant', 'certeza' ou 'vai colher' nos textos.
7. A caixa do Vicente não tem % de ganho nem 'Satélite' em dado fixo.
8. Créditos visíveis: Sentinel-2 cloudless, Esri, OSM, Solar System Scope; nenhum logo da NASA.
9. Teste com 40 municípios sorteados: 0 erro (já passa hoje).
10. Vídeo com 30 s ou menos, legenda em inglês, equipe, integrantes, desafio e dados da NASA.
11. No máximo 7 slides, em inglês.
12. Os links do vídeo e dos slides abrem numa janela anônima.

## 7. Vídeo de 30 s (inglês, legendado, cerca de 65 palavras)

| Tempo | Imagem | Locução |
|---|---|---|
| 0–5 s | Globo girando até o Nordeste; legenda "QUADRA: the sertão's word for the rainy season" | "One rainy season. One chance to plant." |
| 5–11 s | Clique em Quixadá; as 3 perguntas | "Pick your town, answer three questions." |
| 11–18 s | Cardápio, Gantt e roçado em faixas A/B/C | "NASA rain, soil moisture and climate data, with Brazil's official zoning, build a three-year rotation, in strips." |
| 18–25 s | Os 28 quadrados e o cartão de 2027 | "Each square is a real past year here. 2027: a record El Niño. More risk, not certainty." |
| 25–30 s | Nomes da equipe; "Data from GPM IMERG, SMAP L4, POWER, GAEZ, ZARC, IBGE" | "NASA evidence. The farmer decides." |

## Riscos
- O globo 3D trava ou fica lento na máquina da gravação (no teste sem GPU, a v1 desenhava 4 quadros por segundo); reduza com o botão Pular e a imagem de reserva
- Juntar três bases de código (Flask do JP, Node da v2, stdlib do José) consome a noite; reduza copiando peças para a pilha do protótipo
- Os números de El Niño se contradizem entre as telas (3, 4 ou 6 anos; município × estado) e o júri percebe
- Os '% de plantas protegidas' e os 'ganhos de 18–40%' do PercolaCampo aparecem como se fossem dados científicos, e as constantes não estão nos artigos
- A faixa P10–P90 parece previsão: em 2018–2025 o milho passou do P90 em 33% dos municípios; precisa da nota fixa e dos anos mostrados um a um
- Na mandioca, 29% dos anos repetem o anterior no PAM: o risco parece menor do que é
- O custo da CONAB não é o custo do sertão (rendimentos 1,7–3,4 vezes o do PAM): 'não paga o desembolso' sai pessimista, e o preço de seca dá receita alta para quem não vende
- O motor depende do E: e do ambiente do José; se a máquina cair, não há demo (reserva: JSON dos 5 municípios)
- O repositório está privado (404 para anônimo); sem o OK do José não há link público do projeto, e PDFs com copyright não podem ir junto
- Ladrilhos do OSM e do Nominatim: limites de uso; o CDN 'play' do Tailwind e o Google Fonts quebram sem rede
- Afirmações sem arquivo na branch (o AUC ≈ 0,5 do JP; González-Martínez 2026) entram no deck e não se defendem numa pergunta do júri
- O cansaço tira o sono da madrugada; sem números congelados à 01:30, os slides e o vídeo divergem do site

## Perguntas abertas
- Qual globo fica: o do JP (Flask) ou o da site-nasa-v2 (JS estático)? Quem é o autor da v2?
- O repositório e o site vão ficar públicos para a submissão? (decisão do José; hoje é privado)
- O JP pode subir jp_analogos_atlantico.py e embasamento_painel_nordeste.md ainda hoje?
- De onde o Vicente tirou k_geom (0,42/0,56/0,72), q = 1,35 e α = 4,8/2,6? O artigo González-Martínez 2026 existe e está acessível?
- A gravação do vídeo vai ser na máquina do José (dados no E:)? O júri vai abrir o site ou só ver o vídeo e os slides?
- O guia de 2026 do Space Apps exige declarar o uso de IA, ou marcar mídia gerada por IA? Conferir na página oficial
- Para a família, o preço que vale é o do PAM (implícito) ou o da porteira? Mostramos kg além de R$?
- A pergunta sobre água deve mudar algum número (só o baixio, por exemplo) ou fica só como aviso de escopo?