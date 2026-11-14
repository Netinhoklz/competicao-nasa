# Retorno financeiro intuitivo (financeiro)

## Resumo
O retorno financeiro consegue ser mostrado por município com números medidos, mas só para milho, feijão e mandioca. Milho e feijão têm série de 10 anos ou mais em 94% dos 1.794 municípios, a mandioca em 85% e as três juntas em 1.420. As outras culturas têm série curta ou antiga (mamona até 2016, sorgo em 95 municípios, girassol em nenhum). O motor ainda não tem nada de dinheiro, e nenhum colega fez parte financeira. A tela tem de ser montada a partir do notebook do José. Em vez de tentar prever o ano, o método certo de projeção é refazer o plano em cima dos anos que já aconteceram no próprio município, usando o mesmo ano para todas as culturas. Para 2027, o sorteio fica entre os 4 El Niños fortes; para 2028 e 2029, entre os 28 anos da série. São 3.136 sequências, contadas no navegador. Os motivos: a autocorrelação ano a ano é baixa (mediana de 0,21 a 0,24 no milho e no feijão), não há tendência firme, e um teste fora da amostra mostrou que a faixa P10–P90 do passado cobre só 53% a 64% dos anos seguintes. Por isso as faixas precisam ser largas e dizer isso na tela. Em Quixadá (3 ha, contando só a semente), o plano soma R$ 11,5 mil a R$ 24,2 mil em 2027–2029, contra R$ 2,9 mil a R$ 12,3 mil do milho + feijão de hoje. O plano fica à frente em 100% das sequências com o preço da raiz de Quixadá e em 90% com o preço baixo do CE (R$ 0,59/kg). Porém 2027 é o ano caro: o plano fica atrás do jeito de hoje em 3 dos 4 El Niños fortes. O número que mais pesa no resultado é o preço da raiz, então ele precisa ser um seletor visível, e não um valor escondido.

## Recomendações
- **P0** (2.5 h) Criar scripts/preparar_financeiro_site.py que porta a limpeza do 00_intro.py (B, preco_ref, R, quebra, n_anos) e o custo_central do 05_custo.py, e grava E:/campeonato-nasa/dados/financeiro/site_financeiro_mun.json (ou .parquet) com o contrato da proposta para os 1.794 municípios. Mandioca sem série no município: mediana da mesorregião, com o rótulo 'vizinhos'. — O motor não tem dinheiro e a lógica já existe e foi conferida no notebook. Pré-calcular deixa o site rápido e reproduzível.
- **P0** (0.5 h) Adicionar a chave 'financeiro' ao /api/local do motor: uma leitura do JSON por código IBGE, sem cálculo no servidor. — Um único ponto de dados para o front, que já consome o /api/local.
- **P0** (1.5 h) No front, enumerar as 3.136 sequências (4 El Niños × 28 × 28) seguindo exatamente o plano do motor (Partes A/B/C, baixio, bordas sem área), para o plano e para o S0, com custo semente ou desembolso, e tirar P10/P50/P90 por ano, por mês acumulado e de plano − S0. — Enumerar é exato e reproduzível, é instantâneo em JS, se ajusta a qualquer área e preço sem novo cálculo, e preserva a correlação entre culturas no mesmo ano.
- **P0** (2.5 h) Tela 'Dinheiro' com 3 cartões (plano em 3 anos como faixa, o jeito de hoje como faixa, 'em 100 sequências o plano termina à frente em N'), barras por ano com faixa e o seletor do preço da raiz (Quixadá / mediana da UF / preço baixo da UF). — É o pedido do José: retorno de forma intuitiva, sempre com faixa. O preço da raiz é o que mais muda o resultado (ganho de R$ 10,7 mil a R$ 2,7 mil), então não pode ficar escondido.
- **P0** (1.5 h) Gráfico de caixa acumulado mês a mês, de nov/2026 a dez/2029: linha do plano e do S0 com faixa P10–P90, linha 'hoje', marcas de saída no plantio e de entrada na colheita, com as datas tiradas da agenda do motor (2028–29 repetem o mês do ZARC 2026/27). — Responde 'quando entra e quando sai' e mostra que 2027 é o ano caro, com volta a partir de fev/2028.
- **P1** (1 h) Termômetro de segurança por ano, com 3 cores: a fração das sequências em que a colheita paga a semente e em que paga o desembolso. Para 2027, 4 mini-cartões 'se for como 1998 / 2010 / 2016 / 2024'. — Dá a perspectiva de segurança pedida sem prometer número. O teste mostrou que 4 El Niños não fazem uma previsão.
- **P1** (1 h) Faixa de 28 barras 'se o plano estivesse no chão desde 1998' (regime permanente, plano contra S0, mesmo ano). — É o visual mais fácil de entender para segurança, e vem 100% de dado medido (com o aviso do preço da raiz).
- **P1** (1 h) No cartão de cada cultura do cardápio: valor por ha (pior ano já visto, ano típico, melhor ano), R$ por ha-mês e '2025: R$ X' como ponto do dado mais recente. Sem número para forrageiras e perenes. — A seção 90 do notebook pede isso, e o caupi e a mandioca trocam de lugar quando a conta é por mês de terra.
- **P2** (8 h) Depois da entrega: calibrar as faixas para cobrirem 80% fora da amostra (quantis alargados ou mistura com a mesorregião), usar o LSPA 2026 por UF como 'safra corrente', buscar o preço da raiz e da farinha por casa de farinha, e estimar o valor da forragem e do Garantia-Safra. — Hoje a faixa P10–P90 cobre só 53% a 64%. Esses são os buracos que a própria síntese do notebook lista.

## Achados
- **Cobertura real por município: só milho, feijão e mandioca aguentam um número local**: Série = 10 anos ou mais com pelo menos 10 ha plantados, PAM 1998–2025 (2025 é o último ano medido, com 14.264 linhas). Milho: 1.690 municípios (94%), 1.611 com dado em 2021–25. Feijão: 1.693 (94%), 1.618. Mandioca: 1.528 (85%), 1.394. Algodão herbáceo: 324 (último ano mediano 2017). Mamona: 207 (último ano mediano 2016, série velha). Amendoim: 165. Sorgo: 95. Girassol: 0. Há 1.671 municípios com milho e feijão, 1.420 com as três culturas e 13 sem nenhuma série. Guandu, sorgo forrageiro, milheto, palma, gliricídia e mucuna não têm preço nem produção no PAM, então ficam sem valor em R$ (é valor de uso). _[Comando: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 C:/Users/NETINH~1/AppData/Local/Temp/claude/88b277d27b184113/73cd62bd-b6e9-4872-9e4a-a06e5ca404a0/scratchpad/analise10/financeiro/fin.py (bloco COBERTURA); notebooks/secoes_financeiro/00_intro.py:205-235; 05_custo.py seção 5.5]_
- **O motor e os sites dos colegas não têm nada financeiro**: O /api/local de Quixadá devolve local, terra, fontes, clima, analogos, confianca, cardapio, este_ano, plano, agenda e evidencia, sem nenhuma chave de dinheiro. Busquei 'lucro', 'receita' e 'R$' nas pastas do João Pedro e do Vicente e no site-nasa-v2. Só apareceram o 12_mercado.py, que é a base comum (FAOSTAT/AMS), e um 'não uma receita' em texto no index.html do Vicente. A tela financeira é nova e sai inteira de notebooks/secoes_financeiro. _[curl http://127.0.0.1:8765/api/local?lat=-4.97&lon=-39.02 (chaves listadas); grep -rlI -i 'lucro|receita|R$ [0-9]' em colegas/ e site-nasa-v2/; grep em protótipo/motor.py só acha CICLO (linha 539-553)]_
- **O plano do motor não é o plano da seção 10 do notebook: o R$ 13.978 não pode ser copiado**: No motor, a Parte B de 2028 é sorgo forrageiro: 'em ano bom: milho no baixio depois da leguminosa'. O 10_familia.py:62-66 calcula a Faixa 2 de 2028 como 'milho depois do caupi' com bônus. A conta do site precisa seguir a sequência que o motor mostra (A: maniva → mandioca colhe → caupi; B: caupi → sorgo forrageiro → maniva; C: sorgo forrageiro → maniva → mandioca colhe; baixio: milho + caupi nos 3 anos). Fazendo assim, o bônus de leguminosa sai da conta. Ele valia menos de R$ 300 em 3 anos de qualquer jeito (08_rotacao.py, leitura). _[quixada.json → plano.faixas (Parte B anos[1] = Sorgo forrageiro); notebooks/secoes_financeiro/10_familia.py:55-70]_
- **Números sólidos de Quixadá (medidos, R$ de 2025 por ha plantado, preço de referência do município)**: Milho: 28 anos, 492 kg/ha, R$ 1,32/kg. P10/P50/P90 = R$ 172 / 651 / 1.900; El Niño forte R$ 190; quebra em 29% dos anos; não paga a semente (R$ 284) em 21% e não paga o desembolso (R$ 1.136) em 68%. Feijão: 28 anos, 297 kg/ha, R$ 5,07/kg. P10/P50/P90 = R$ 579 / 1.506 / 3.229; El Niño forte R$ 831; quebra 18%; não paga o desembolso (R$ 1.992) em 57%. Mandioca: 24 anos (2012–15 completados pela mesorregião), 9.667 kg/ha, R$ 1,33/kg. P10/P50/P90 = R$ 6.670 / 12.896 / 15.708; El Niño forte R$ 6.937; quebra 8%; paga o desembolso (R$ 4.439) em todos os anos. Os anos recentes de milho e feijão estão abaixo da mediana longa. Milho em 2021–25: 530, 660, 240, 300, 200. Feijão: 1.280, 1.430, 780, 1.070, 510. É o 'dado de hoje' que precisa aparecer na tela. _[fin.py (bloco QUIXADÁ, JSON dos cartões) e fin2.py ('últimos 5 anos'); bate com 10_familia.py leitura (milho 967/190/455; feijão 2.142/831/1.201 por grupo)]_
- **Prever pela série temporal não funciona: autocorrelação baixa e sem tendência firme**: Autocorrelação lag-1 da razão ao normal, mediana dos municípios: feijão 0,21, milho 0,24, mandioca 0,44. A da mandioca vem inflada pelo relato repetido: 33% dos rendimentos repetem o ano anterior (seção 2). Tendência (Spearman ano × razão), mediana: milho +0,18, feijão +0,01, mandioca −0,09, com P10–P90 de −0,5 a +0,6. ARIMA ou tendência linear em 28 pontos dominados por choques de chuva não acrescentam nada. O que se projeta é a distribuição: o próprio histórico do município, condicionado ao ENSO só onde existe sinal (2027). _[fin.py, blocos AUTOCORRELAÇÃO e TENDÊNCIA]_
- **Teste fora da amostra: a faixa do passado é estreita demais**: Montei as faixas com 1998–2015 e conferi nos anos 2016–2025. P10–P90 (deveria cobrir 80%) cobriu 59% no milho, 64% no feijão e 53% na mandioca. P5–P95 cobriu 68%, 74% e 63%. Do mínimo ao máximo, 76%, 84% e 74%. Usando a razão da mesorregião como faixa, 65%, 72% e 57%. Os desvios têm direção: o milho ficou acima da faixa em 31% dos anos (tendência de alta) e a mandioca abaixo em 29% (queda). Conclusão: no cartão, a faixa deve ser 'do pior ao melhor ano já visto' e trazer o aviso 'o futuro varia mais que o passado'. _[fin.py (FORA DA AMOSTRA) e fin3.py (calibração P5–P95, mín–máx e mesorregião)]_
- **Condicionar 2027 ao El Niño ajuda em 2016 e atrapalha em 2024: 4 anos não bastam**: Comparei o erro absoluto mediano da razão ao normal prevendo pela mediana dos El Niños de 1998 e 2010 contra a climatologia. Em 2016 o condicionamento ganha: milho 0,38 contra 0,76, feijão 0,37 contra 0,58. Em 2024 perde: milho 0,92 contra 0,56, feijão 0,50 contra 0,32. Na mandioca a climatologia ganha nos dois anos. A recomendação é mostrar 2027 como os 4 anos reais ('se 2027 for como 1998 / 2010 / 2016 / 2024'), mais um botão 'e se for um ano qualquer', e não uma mediana condicionada só. _[fin.py (ERRO ABSOLUTO MEDIANO ... 2016 e 2024)]_
- **Quixadá, plano contra o jeito de hoje (S0), 3 ha, contando só a semente: o plano ganha nos 3 anos, mas 2027 é caro**: Enumeração: 2027 entre os 4 El Niños fortes, 2028 e 2029 entre os 28 anos, sempre o mesmo ano para todas as culturas. Margem sobre a semente em 3 anos, P10/P50/P90: plano R$ 11.500 / 18.010 / 24.190; S0 R$ 2.880 / 7.270 / 12.320. Com a raiz a R$ 1,33 (Quixadá), o ganho fica entre R$ 6.000 e 14.560 e o plano vence em 100% das sequências. Com a mediana do CE (R$ 0,84), ganho de R$ 2.110 a 7.980, vence em 98%. Com o P25 do CE (R$ 0,59), ganho de −R$ 60 a 4.920, vence em 90%. Em 2027, ano a ano: em 1998 o plano dá −R$ 101 e o S0 −R$ 252; em 2010, R$ 1.086 contra 1.719; em 2016, R$ 347 contra 392; em 2024, R$ 1.002 contra 1.426. O plano só está à frente em 2027 em 25% dos casos; em 2028 já está em 95%. Contando o desembolso da CONAB, o plano acumulado tem P50 de +R$ 59 (fica negativo em 49% das sequências) e o S0 tem P50 de −R$ 4.930 (negativo em 90%). Em 2027 o plano dá cerca de −R$ 6.430. _[fin.py (SIMULAÇÃO Quixadá ×2) e fin2.py (preço da raiz; 2027 condicionado); fin4.py (2027 por ano de El Niño)]_
- **Caixa mês a mês: o ponto mais baixo é pequeno e vem cedo**: No caminho típico (2027 na mediana dos El Niños fortes, 2028–29 na mediana do município, raiz de Quixadá, só a semente), as saídas são −R$ 142 em fev/27, −R$ 189 em mar/27 e −R$ 71 em abr/27. O ponto mais baixo é −R$ 401 em abr/2027. Depois entram R$ 649 em jun/27 e R$ 415 em jul/27, fechando 2027 em +R$ 663. A mandioca entra aos poucos de fev a set/2028, com R$ 933 a 1.828 por mês, e o acumulado chega a R$ 10.031 em set/2028 e R$ 20.403 em set/2029. Contando o desembolso, o buraco de 2027 passa de R$ 6 mil. A tela precisa mostrar os dois níveis de custo. _[fin2.py (CAIXA MÊS A MÊS); datas das barras plantio/colheita em quixada.json → agenda.linhas]_
- **Replay de 28 anos: 'se o plano estivesse no chão desde 1998'**: Em regime permanente (uma parte colhe mandioca, outra tem caupi, outra recebe maniva, mais o baixio), com a raiz de Quixadá, o valor da colheita do plano fica acima do S0 em 28 de 28 anos. O pior ano é 2012 (R$ 1.881 contra 511), e 1998 dá R$ 4.748 contra 387. É o visual de segurança mais forte e mais fácil de entender: 28 barras pareadas. Mas depende do preço da raiz, que vem de pouco volume (13 a 35 ha/ano em Quixadá desde 2018), e da mandioca relatada, que se repete em 33% dos anos. _[fin.py (REPLAY ano a ano; 'anos em que o plano em regime fica abaixo da S0: 0 de 28'); mandioca Quixadá área 13–35 ha (fin.py)]_
- **Custos: a CONAB serve como régua de dois níveis, não como custo da família**: Custos da CONAB em R$ de 2025/ha (semente / desembolso / operacional). Feijão familiar: 142 / 1.992 / 3.847 (desembolso de 590 a 3.212 em 9 locais). Milho de Crateús-CE: 284 / 1.136 / 1.845 (teto Carira-SE, 4.476). Mandioca: 0 / ≈4.400 / ≈8.700. Na minha conta a mandioca deu 4.439/8.706, contra 4.387/8.678 no notebook, porque não apliquei a correção de nome Giral→Girau. Vale o do notebook. Sorgo, amendoim e algodão têm custo suposto. As planilhas pressupõem 1,7 a 3,4 vezes o rendimento do PAM, então 'só semente' é otimista e 'desembolso' é pessimista para o roçado. Os dois precisam aparecer. _[fin.py (CUSTO); notebooks/secoes_financeiro/05_custo.py:22-26, 61-66 e leitura final]_

## Reaproveitar
- notebooks/secoes_financeiro/00_intro.py:191-235 (limpeza B, preço de referência com fallback município→UF→NE, R = rendimento × preço) → scripts/preparar_financeiro_site.py: Portar quase sem mudança para o script de pré-cálculo. Minha réplica em fin.py reproduziu os números de Quixadá da seção 10.
- notebooks/secoes_financeiro/05_custo.py:29-66 (custo_central, Crateús-CE para o milho, suposição para sorgo, amendoim e algodão) → scripts/preparar_financeiro_site.py → custo_ha no JSON: Copiar com a correção de nome Giral→Girau (a falta dela explica a diferença de 1% na mandioca).
- notebooks/secoes_financeiro/10_familia.py:55-80 (ano_plano, ano_s0) → site-versao-final/static/js/dinheiro.js: Reescrever em JS seguindo a sequência de partes do motor (Parte B 2028 = sorgo forrageiro) e enumerar 4×28×28 sequências.
- protótipo/motor.py:539-553 (CICLO) e a agenda (barras plantio/colheita) do /api/local → dinheiro.js (caixa mês a mês): Tirar daí o mês de saída (início do plantio) e de entrada (meio da colheita) do caixa mensal; repetir o mês do ano em 2028–29.
- notebooks/secoes_financeiro/00_intro.py:58-62 (paleta CAT/SEQ/DIV validada) → site-versao-final/static/css: Usar como tokens CSS: azul de magnitude, azul↔vermelho de sinal, cinza #8a8984 para o S0.
- notebooks/secoes_financeiro/90_sintese.py (lista 'Não dizer') → textos da tela Dinheiro: Virar a regra de redação da tela: nada de 'a rotação paga', '+24% contra a sua prática' ou 'o plano rende R$ 24 mil' sem o preço da raiz e o caixa de 2027.
- C:/Users/NETINH~1/AppData/Local/Temp/claude/88b277d27b184113/73cd62bd-b6e9-4872-9e4a-a06e5ca404a0/scratchpad/analise10/financeiro/fin.py e fin2.py → scripts/ (conferência): Protótipo das contas (cobertura, cartões de Quixadá, simulação plano × S0, caixa mensal, teste fora da amostra) para conferir a implementação. O scratchpad apaga em cerca de 1,5 dia: copiar para o repositório se for usar.

## Proposta detalhada
1. O QUE É MEDIDO, O QUE É SUPOSIÇÃO E O QUE É PROJEÇÃO (vai como rótulo na tela)
- MEDIDO: rendimento por ha plantado (IBGE PAM 1998–2025) × preço de referência (mediana 2016–2025 do preço implícito do município, com pelo menos 3 anos; se não houver, a UF; se não houver, o NE), em R$ de 2025 (IPCA). Custos da CONAB (semente, desembolso, operacional). Os anos de El Niño forte (1998, 2010, 2016, 2024).
- SUPOSIÇÃO: área igual nas Partes A/B/C; bordas não tiram área; baixio = ½ milho + ½ caupi; sorgo forrageiro, palma e gliricídia sem valor em R$; custo do sorgo = lavoura anual manual; custo da maniva todo no ano do plantio; mandioca colhida aos poucos na janela fev–set do ano seguinte; datas de 2028–29 iguais às do ZARC 2026/27.
- PROJEÇÃO: as sequências de anos já vistos aplicadas a 2027–2029. Não é previsão do ano.

2. FÓRMULAS (m = município, c = cultura, y = ano histórico)
- R(m,c,y) = rend_plantado(m,c,y) [kg/ha] × preco_ref(m,c) [R$/kg]. O ano de perda total entra como 0.
- Série válida: 10 anos ou mais com pelo menos 10 ha plantados. Lacuna de ano: R = mediana_mun(c) × razão ao normal mediana da mesorregião no ano y (rótulo 'vizinhos').
- Cartão da cultura: pior ano já visto = mín R; ano típico = mediana; melhor = máx; P10/P90; el_nino_forte = mediana de R nos anos de El Niño forte (se houver 2 ou mais); quebra% = % de anos com rendimento < 0,5 × mediana dos outros anos; nao_paga_X% = % de anos com R < custo_X(c).
- Margem_X = R − custo_X, com X em {semente, desembolso}. Equilíbrio: rend_eq = custo_desembolso / preco_ref; preco_eq = custo_desembolso / rend_mediano.
- Área da família (respostas): T = roçado (ha), b = baixio (ha). Cada parte = (T − b)/3; bordas = 0 ha.
- Ano k do plano no ano histórico y (sequência do motor):
  - 2027: receita = F·a + (Mi+F)/2·b; custo = (K_mand + K_feij + K_sorgo)·a + (K_mi+K_feij)/2·b
  - 2028: receita = Mand·p·a + (Mi+F)/2·b; custo = (K_sorgo + K_mand)·a + baixio
  - 2029: receita = (F + Mand·p)·a + (Mi+F)/2·b; custo = (K_feij + K_mand)·a + baixio
  - onde a = (T−b)/3 e p = preco_raiz_escolhido / preco_ref_mand.
- S0 (o jeito de hoje) = (Mi+F)/2 · T de receita; custo = (K_mi+K_feij)/2 · T.
- Sequências: y27 ∈ {1998, 2010, 2016, 2024} (ou 1998–2025 no botão 'ano qualquer'), y28 e y29 ∈ 1998–2025. Total de 4×28×28 = 3.136, enumeradas, sem sorteio. O mesmo y vale para todas as culturas e para o S0 (comparação pareada).
- Saídas: P10/P50/P90 por ano e do acumulado; P(plano ≥ S0 no fim de 2029); termômetro do ano k = % das sequências com margem_k ≥ 0. Caixa mensal: custo no mês de início da barra 'plantio' da agenda; receita no mês do meio da barra 'colheita'; mandioca = receita ÷ 8 em fev a set; acumulado mês a mês com P10/P50/P90.

3. CONTRATO JSON (por município, chave 'financeiro' no /api/local). Exemplo de Quixadá com valores reais (fin.py e fin2.py). '…' marca campos que o script preenche.
{
 "cod": "2311306", "municipio": "Quixadá", "uf": "CE",
 "moeda": "R$ de 2025 (IPCA)", "base": "IBGE PAM 1998–2025; CONAB custos NE", "ultimo_ano_medido": 2025,
 "anos_el_nino_forte": [1998, 2010, 2016, 2024],
 "culturas": {
  "Milho": {"anos_serie": 28, "preco_kg": 1.32, "origem_preco": "município", "rend_mediano_kg_ha": 492,
     "valor_ha": {"p10": 172, "p50": 651, "p90": 1900, "min": 0, "max": "…"}, "el_nino_forte": 190,
     "ultimos": {"2021": 530, "2022": 660, "2023": 240, "2024": 300, "2025": 200},
     "quebra_pct": 29, "nao_paga_pct": {"semente": 21, "desembolso": 68},
     "custo_ha": {"semente": 284, "desembolso": 1136, "operacional": 1845, "faixa_desembolso": [1136, 4476], "origem": "CONAB Crateús-CE (teto Carira-SE)", "tipo": "medido"},
     "equilibrio": {"rend_kg_ha": 861, "preco_kg": 2.31}, "ha_mes": "…"},
  "Feijão": {"anos_serie": 28, "preco_kg": 5.07, "rend_mediano_kg_ha": 297, "valor_ha": {"p10": 579, "p50": 1506, "p90": 3229}, "el_nino_forte": 831,
     "ultimos": {"2021": 1280, "2022": 1430, "2023": 780, "2024": 1070, "2025": 510}, "quebra_pct": 18, "nao_paga_pct": {"semente": 0, "desembolso": 57},
     "custo_ha": {"semente": 142, "desembolso": 1992, "operacional": 3847, "faixa_desembolso": [590, 3212]}, "equilibrio": {"rend_kg_ha": 393, "preco_kg": 6.71},
     "aviso": "PAM junta caupi e feijão comum"},
  "Mandioca": {"anos_serie": 24, "anos_vizinhos": [2012, 2013, 2014, 2015], "preco_kg": 1.33, "rend_mediano_kg_ha": 9667,
     "valor_ha": {"p10": 6670, "p50": 12896, "p90": 15708}, "el_nino_forte": 6937, "quebra_pct": 8, "nao_paga_pct": {"semente": 0, "desembolso": 0},
     "custo_ha": {"semente": 0, "desembolso": 4387, "operacional": 8678}, "equilibrio": {"rend_kg_ha": 3298},
     "aviso": "preço de pouco volume (13–35 ha/ano desde 2018); 33% dos rendimentos do PAM repetem o ano anterior"},
  "Algodão herbáceo": {"anos_serie": 28, "valor_ha": {"p10": 924, "p50": 2035, "p90": 3154}, "custo_tipo": "suposição"},
  "Sorgo forrageiro": {"valor_ha": null, "texto": "valor de uso (forragem), sem preço na base"}
 },
 "historico_R_ha": {"anos": [1998, "…", 2025], "Milho": ["…28 valores"], "Feijão": ["…"], "Mandioca": ["…"], "origem_Mandioca": ["mun", "…", "meso"]},
 "precos_raiz": {"municipio": 1.33, "uf_mediana": 0.84, "uf_p25": 0.59, "padrao": "uf_mediana"},
 "padrao_familia": {"T_ha": 3, "baixio_ha": 1, "rotulo": "família da proposta (fictícia)"},
 "calibracao": {"faixa_p10_p90_cobriu_fora_da_amostra": {"Milho": 0.59, "Feijão": 0.64, "Mandioca": 0.53}},
 "avisos": ["valor da colheita = vender ou comer, a preço da região; não é lucro", "forragem e Garantia-Safra fora da conta"]
}
Tamanho estimado: cerca de 1,5 KB por município, uns 2,7 MB no total, servidos um município por chamada.
Valores esperados no front para Quixadá (T=3, b=1, só semente), para conferir a implementação:
- raiz a 1,33: plano R$ 11.500 / 18.010 / 24.190 contra S0 R$ 2.880 / 7.270 / 12.320; plano à frente em 100% das sequências.
- raiz a 0,84: ganho R$ 2.110 / 5.350 / 7.980; à frente em 98%.
- raiz a 0,59: ganho −R$ 60 / 2.710 / 4.920; à frente em 90%.
- 2027: 1998 −101 contra −252; 2010 1.086 contra 1.719; 2016 347 contra 392; 2024 1.002 contra 1.426.
- Caixa (caminho típico): fundo −R$ 401 em abr/27; +663 em dez/27; +10.031 em set/28; +20.403 em set/29.

4. TELA 'DINHEIRO' (depois de 'como plantar'; usa a área e o baixio já respondidos)
┌───────────────────────────────────────────────────────────────┐
│ Quixadá-CE · seu roçado de 3 ha (1 ha de baixio)   [mudar área]│
│ Preço da raiz: (●) R$0,84 região  ( ) R$1,33 aqui  ( ) R$0,59   │
│ Custo: (●) só a semente   ( ) pago máquina e insumos (CONAB)    │
├──────────────────┬──────────────────┬─────────────────────────┤
│ PLANO 2027–29    │ DO JEITO DE HOJE │ SEGURANÇA               │
│ R$ 8 a 17 mil    │ R$ 2,9 a 12 mil  │ Em 98 de 100 sequências │
│ típico R$12,7 mil│ típico R$ 7,3 mil│ de anos já vistas, o    │
│ ▁▃▆█▆▃▁ (faixa)   │ ▁▃▆█▆▃▁           │ plano termina à frente  │
├──────────────────┴──────────────────┴─────────────────────────┤
│ CAIXA MÊS A MÊS (acumulado)  — plano ▬ azul   hoje ▬ cinza       │
│ R$ ▲                                        ░░░▓▓▓ plano        │
│    │                         ░░░▓▓▓▓▓▓▓▓▓▓▓▓                     │
│    │            ░░▓▓▓▓▓▓▓▓▓▓▓              ▒▒▒ hoje              │
│  0 ┼─▼▼──▲▲─────▲▲▲▲▲▲▲▲────────▲▲▲▲▲▲▲▲─────────────────      │
│    │ │hoje  2027 (caro)   2028: entra a mandioca   2029          │
│    ▼ saída = semente/maniva   ▲ entrada = colheita               │
├───────────────────────────────────────────────────────────────┤
│ 2027 É EL NIÑO MUITO FORTE. SE FOR COMO…                        │
│ [1998: −R$100 | hoje −R$250] [2010: R$1,1 mil | 1,7 mil]        │
│ [2016: R$350 | 390] [2024: R$1,0 mil | 1,4 mil] [ano qualquer ▸] │
│ "Em 2027 o plano rende menos que o de hoje: maniva e sorgo não  │
│  vendem. Volta a partir de fev/2028."                           │
├───────────────────────────────────────────────────────────────┤
│ TERMÔMETRO POR ANO   paga a semente   paga máquina e insumos    │
│ 2027                 ██████░░ 75%      ░░░░░░░░ 0%               │
│ 2028                 ████████ 100%     █████░░░ 6x%              │
│ 2029                 ████████ 100%     ██████░░ 7x%              │
├───────────────────────────────────────────────────────────────┤
│ SE O PLANO ESTIVESSE NO CHÃO DESDE 1998 (28 anos, mesmo ano)     │
│ ▌▌▐▌▐▌▌▌▐▌▌▌▐▌▌▐▌▌▌▌▌▌▌▌▌▌▌▌  azul = plano, cinza = hoje          │
│ "Ficou acima em 28 de 28 anos (com o preço da raiz daqui)."     │
└───────────────────────────────────────────────────────────────┘
Os valores dos cartões no desenho usam a raiz a 0,84. Os do termômetro são ilustrativos ('x' = o front calcula); o 75% de 2027 é a fração dos 4 El Niños com margem ≥ 0.
Regras visuais (paleta do 00_intro.py): magnitude em azul de um só tom; sinal em azul ↔ vermelho com cinza no meio; o S0 sempre em cinza; nenhum gráfico com dois eixos y. Todo número vem como faixa, com 'típico' em letra menor. Rótulos 'medido', 'suposição' e 'projeção' como selo pequeno em cada bloco. Nunca usar 'lucro'; usar 'sobra depois da semente'.

5. PERGUNTAS E QUANDO FAZER (pelo ângulo do dinheiro)
- Logo depois de escolher o lugar, junto das perguntas de água, porque mudam o plano: quantos ha planta (T); se tem baixio e quantos ha (b); se tem mandioca no chão hoje (se sim, a Parte A já colhe em 2027 e o ano caro some).
- Na própria tela do dinheiro, como seletor com valor padrão, porque só mudam o número: se a semente é guardada ou comprada; se paga máquina ou animal (nível de custo); onde vende a mandioca (raiz na região / aqui / preço baixo / 'não sei' = mediana da UF); quantos animais tem (só texto: 'a forragem vale para X cabras', sem R$).

6. COMO PROJETAR (resposta à pergunta da série temporal)
- Não usar ARIMA nem tendência. A autocorrelação é de 0,21 a 0,24, a tendência é ~0, e a série tem 28 pontos dominados por choques de chuva.
- Usar o 'replay' dos anos do próprio município (distribuição climatológica). Condicionar ao ENSO só em 2027, mostrando os 4 anos reais lado a lado com o 'ano qualquer'. Em 2028 e 2029, nenhum condicionamento, porque o ENSO não tem previsão com mais de cerca de 9 meses.
- Preço: real fixo, a referência de 2016–2025, sem extrapolar a alta da mandioca (+4% a 6% ao ano desde 2010). O risco de preço entra pelo seletor da raiz.
- Mostrar o calibrador honesto: 'esta faixa acertou 6 em 10 anos num teste'. Nos cartões, usar 'pior–melhor ano já visto' (cobriu 74% a 84%).
- Mostrar o dado de hoje (2025 e 2021–25) como pontos sobre a faixa.

## Riscos
- O preço da raiz de Quixadá (R$ 1,33/kg) vem de pouco volume (13 a 35 ha/ano). Muitas famílias plantando mandioca ao mesmo tempo podem não conseguir esse preço. Com R$ 0,59 o ganho mediano cai de R$ 10,7 mil para R$ 2,7 mil, e o P10 fica em −R$ 60. Sugiro que o padrão seja a mediana da UF.
- A mandioca parece segura demais. 33% dos rendimentos do PAM repetem o ano anterior, e fora da amostra a faixa da mandioca cobriu só 53% dos anos, com 29% abaixo. O 'quebra 8%' precisa vir com aviso.
- As faixas tiradas do histórico subestimam a incerteza (cobriram 53% a 64% contra os 80% nominais). Se o texto disser '8 em 10' sem o calibrador, promete mais do que entrega.
- São só 4 El Niños fortes, e 2024 foi bom. Uma 'previsão de 2027' baseada neles é frágil: no teste, o condicionamento errou mais que a climatologia em 2024.
- O valor do PAM inclui o que a família come e dá aos animais. Chamar de 'dinheiro' ou 'lucro' engana; o rótulo tem de ser 'valor da colheita'.
- Os custos da CONAB vêm de lavouras com 1,7 a 3,4 vezes o rendimento do PAM. 'Só semente' é otimista e 'desembolso' é pessimista, por isso a tela precisa mostrar os dois.
- Divergência entre o plano do motor e a seção 10 do notebook (Parte B em 2028). Se o site copiar o R$ 13.978 do notebook, os números não vão bater com o plano que a pessoa vê.
- Forragem com valor zero e sem Garantia-Safra. A conta é conservadora para o plano, mas o S0 também recebe o Garantia-Safra, o que pode confundir a comparação.
- 266 municípios sem série de mandioca e 13 sem nenhuma série. Precisa de mensagem explícita e do fallback pela mesorregião com rótulo, nunca um número inventado.
- Prazo: as P0 somam cerca de 8,5 h. Se a integração das telas atrasar, cortar o termômetro e o replay de 28 anos (P1) antes de cortar o seletor do preço da raiz.

## Perguntas abertas
- Qual deve ser o preço padrão da raiz: o do município (R$ 1,33, pouco volume) ou a mediana da UF (R$ 0,84)? Recomendo a mediana da UF como padrão.
- O custo padrão é 'só semente' ou o desembolso da CONAB? Recomendo 'só semente' com o seletor visível.
- Para 2027, mostrar só os 4 El Niños ou também uma mistura com o 'ano qualquer'? A perspectiva do IMERG em Quixadá diz que 2 de 3 El Niños ficaram no terço mais seco.
- A família padrão continua 3 ha com 1 ha de baixio (fictícia, da proposta)?
- Se a família já tem mandioca no chão, a Parte A colhe em 2027. O motor já trata esse caso na sequência das partes, ou só em nota?
- O site final vai rodar sobre o motor Python (porta 8765) ou como estático JS (site-nasa-v2)? Isso decide se o JSON financeiro vem pelo /api/local ou como arquivo por município.