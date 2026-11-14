# Projeção por ciclo e segurança (projecao)

## Resumo
Para os anos seguintes, o melhor método é o mais simples: os quantis do próprio município encolhidos para a mesorregião (método C, peso do município n/(n+10)). Num backtest com 1.783 municípios, ele dá cobertura de 80% de 0,77 a 0,78 deixando o ano de fora (média por ano 0,775) e foi o mais estável no walk-forward. Para 2027, condicionar ao ONI de ago–out (anos 1998, 2016 e 2024; método D) acerta a chance média de quebra nos El Niños fortes (prevista 0,30 contra observada 0,30). O C dá 0,16 nesses anos. Mas o D é estreito demais: cobre só 0,55 (LOYO) e 0,46 (WF), porque os três anos discordam entre si (milho em quebra: 60%, 53% e 11% dos municípios). Por isso o leque de 2027 precisa de um alargamento conforme, calibrado no walk-forward: P10/P90 ± 0,155 × a mediana e piso P20 − 0,079 × a mediana. Com ele, a cobertura volta a 0,78–0,80 e o piso 8 em 10 se sustenta em 0,88 dos casos nos El Niños fortes. Regressão quantílica e remoção de tendência foram reprovadas: no walk-forward do milho, a regressão quantílica cobre 0,26, e a tendência deixa 9 dos 18 anos abaixo de 60%. Para falar de segurança com honestidade, a página mostra três coisas: o que o município colheu de fato em 1998, 2016 e 2024, a chance de quebra em 10 roças e um leque que estreita em 19/mar e 30/abr com a chuva IMERG desde fevereiro. No milho do semiárido, a chance de quebra vai de 0,28 em novembro para 0,60 se a chuva de fev–abr ficar abaixo de 75% do normal, ou para 0,10 se passar de 100%. Em 2028 e 2029 sobra só o clima (sem oceano). Não dá para projetar secas longas como a de 2012–15 (cobertura de 0,60–0,70 nesses anos), a roça de uma família específica (o PAM é a média do município), a mandioca ano a ano, nem o efeito da rotação.

## Recomendações
- **P0** (2 h) Adotar o método 'C + D + conforme' para a projeção: 2027 = D (ONI ASO ≥ 1,0, mesorregião + município, peso n/(n+10)) com P10/P90 ± 0,155·mediana e P20/P80 ∓ 0,079·mediana; 2028 e 2029 = C com ± 0,104 e ∓ 0,056. Gerar uma vez em lote (projecao.py) e servir pré-calculado: como uma chave 'projecao' no /api/local do protótipo, ou como JSON por município. — Foi o único conjunto calibrado no walk-forward (cobertura média por ano 0,783; piso P20 se sustentou em 0,88 nos El Niños fortes). É simples e não depende de modelo ajustado na hora.
- **P0** (0.3 h) Copiar os scripts backtest.py, metricas.py, portoes_precos.py, projecao.py e extra.py do scratchpad para site-versao-final/dados/projecao/ (ou para protótipo/), junto com o projecao_mun.json. — O scratchpad é apagado em cerca de 1,5 dia (memória do projeto). Sem os scripts, os números do backtest não se reproduzem para o júri.
- **P0** (3 h) Tela 'Segurança por ciclo': para cada parte do roçado (A/B/C), um leque por ano (2027, 2028, 2029) em sacos/ha, com uma grade de 10 roças pintadas (quebra) e, embaixo, 'o que o seu município colheu em 1998, 2016 e 2024' (medido). P90 escondido; P80 como 'ano bom'. — É a forma honesta e visual de dizer segurança: frequência natural (já canônica no projeto), anos reais parecidos e o leque inteiro, nunca um número só.
- **P0** (0.5 h) Selos fixos no leque: 2027 com 'oceano acima do recorde (2,46 > 2,04): extrapolação, 3 anos parecidos'; 2028/29 com 'só clima, sem previsão do oceano'; mandioca com 'o PAM repete o valor em 29% dos anos, leque otimista'. — O backtest mostra onde cada número falha. Sem os selos, o leque de 2027 parece certeza.
- **P1** (2 h) Atualização nos portões: tabela pré-calculada por mesorregião e cultura com os quantis de R e a chance de quebra por classe de chuva IMERG desde 1/fev (< 75%, 75–100%, ≥ 100%), para mostrar como o leque de 2027 estreita em 19/mar e 30/abr. — É a informação que mais muda a decisão: no milho, a chance de quebra vai de 0,28 para 0,60 ou 0,10. E conversa com a 'luz principal' canônica.
- **P1** (1.5 h) Retorno financeiro no mesmo leque: receita = kg × preço mediano 2016–25 do município (R$ de 2025), com a linha da semente e a do desembolso da CONAB (05_custo.py:210-212), escrito como 'em X de 10 anos parecidos a colheita não paga a semente'. A área vem da pergunta ao agricultor. — Deixa o retorno intuitivo sem inventar preço futuro. O preço do feijão sobe na seca (ρ −0,52); isso vira uma nota, não uma correção.
- **P2** (2 h) Trocar o nível pela mediana dos últimos 10 anos onde a tendência do log do rendimento for forte (cerrado da BA, do PI e do MA), e validar no mesmo backtest. — Corrige o artefato de Barreiras. Não cabe validar até amanhã com segurança.
- **P2** (6 h) Depois da entrega: conformal por blocos de ano (Mondrian por classe de ENSO), um ensemble com o logístico canônico de P(quebra) e a LSPA da UF a partir de mar/2027 como 'o IBGE já estima'. — Os erros são correlacionados dentro do ano. O conformal agrupado trata município-anos como trocáveis, e isso é otimista.

## Achados
- **Inventário: o que existe de série (medido) e até quando**: Rendimento por ha plantado vem do PAM, 1998–2025 (painel financeiro, com preço em R$ de 2025). Municípios com 20 anos ou mais de série: milho 1.630, feijão 1.662, mandioca 1.490, amendoim 147, algodão 82, mamona 79, sorgo 41, girassol 0. Caupi, guandu, milheto e palma não têm série municipal própria; o caupi está dentro de 'Feijão'. O PAM por safra (1ª e 2ª) cobre 2003–2025. O IMERG mensal por município vai de 1998-01 a 2026-09 (Final até 30/09/2025; depois, Late preliminar). O SMAP mensal vai de 2015-03 a 2026-11. O ONI vai até ASO/2026 = 2,46. A LSPA por UF vai de 2006-09 a 2026-10, mas só para a safra do ano civil: ainda não há estimativa para 2027. _[scratchpad/analise10/projecao/inv.py e inv2.py; painel_mun_cultura_ano.parquet: 386.543 linhas, 8 produtos; indices_clima_mensal 2026-09 ONI 2,46]_
- **O PAM é estimativa do agente municipal, e a mandioca repete valores**: O rendimento sai idêntico ao do ano anterior em 28,6% dos anos na mandioca, 9,2% no milho e 7,4% no feijão. Por isso o leque da mandioca parece estreito ('seguro') sem ser. Nos anos de El Niño forte, a perda de área (1 − colhida/plantada) sobe de 0,12 para 0,18 no milho e de 0,10 para 0,15 no feijão; na mandioca quase não muda (0,026 contra 0,031). _[oni.py (saída: 'fração de anos com rendimento idêntico ao ano anterior')]_
- **Backtest LOYO (28 anos, ~131 mil município-anos, 3 culturas): o C é o mais bem calibrado**: Cobertura de 80% (P10–P90) no milho: C 0,777, A 0,764, E 0,768, D 0,742, B 0,736, D2 0,701. Média por ano, nas 3 culturas: C 0,775, A 0,771, E 0,772, D 0,748, B 0,731, D2 0,692. O pior ano é 1998, 2012 ou 2024 (de 0,45 a 0,57). A remoção de tendência estreita o intervalo e perde cobertura. O Brier da quebra fica parecido entre os métodos (milho de 0,162 a 0,178). _[backtest.py + metricas.py → metricas.txt, bloco 'LOYO: todos os anos, por cultura' e 'cobertura 80% por ano']_
- **Nos El Niños fortes conhecidos em novembro (ONI ASO ≥ 1,0: 1998, 2016, 2024), nenhum piso se sustenta sem alargar**: Fração de casos com rendimento ≥ P20 (meta 0,80), LOYO. Método C: 0,47 em 1998, 0,57 em 2016 e 0,87 em 2024. Método D: 0,53, 0,67 e 0,90. A chance média de quebra prevista nos três anos fica certa com o D (0,298 contra 0,303 observada) e baixa com o C (0,162). No nível do ano, o D erra o sinal: prevê 0,30, 0,35 e 0,55 contra 0,60, 0,53 e 0,11 observados no milho. Os três anos parecidos discordam entre si, e esse é o limite do dado. _[metricas.txt, 'LOYO: por grupo' e 'Milho LOYO, por ano'; extra.py (piso80 por ano)]_
- **Walk-forward 2008–2025 (só o passado): o alargamento conforme é o único que chega perto de 80%**: Cobertura média por ano: F_conf 0,783 (pior ano 0,565, em 2024; 1 ano abaixo de 0,6), C 0,688, A 0,665, D 0,645, B 0,606 (9 anos abaixo de 0,6), E 0,562 (12 anos). No milho, a regressão quantílica (E) falhou: cobertura 0,26, com ajustes perdidos em 2010 e 2012–15, porque o termo de tendência extrapola. Nos El Niños fortes, o F cobre 0,61 nos dois lados, mas o piso P20 se sustenta em 0,88 (milho 0,95), que é o lado que importa para a segurança. Fatores calibrados (× a mediana do município): D, bilateral 0,155 e piso 0,079; C, 0,104 e 0,056. _[metricas.txt, 'WF: …'; extra.py, linhas 'WF C_hier/D_enso Qhat80']_
- **O leque estreita durante a quadra com a chuva IMERG desde fevereiro (medido, meses inteiros)**: Milho no semiárido de CE, RN, PB, PI e PE (23.704 município-anos), em razão ao normal do município. Em novembro, só com o clima: P20 0,30, P50 1,00, chance de quebra 0,28. Com o ONI ≥ 1: P50 0,47, quebra 0,52 (3 anos). Com chuva de fev–abr abaixo de 75% do normal: P50 0,33, quebra 0,60. Entre 75% e 100%: P50 0,72, quebra 0,37. Acima de 100%: P20 0,81, P50 1,36, quebra 0,10. No feijão, a quebra fica em 0,23 (clima), 0,50 (abaixo de 75%) e 0,08 (acima de 100%). Fev–mar (cerca de 31/mar) já separa: 0,54, 0,33 e 0,13. Os portões de 19/mar e 30/abr são decêndios, e aqui usei meses inteiros, então é uma aproximação. _[portoes_precos.py (bloco '== Milho' e '== Feijão')]_
- **2028–2029: o ano depois do El Niño não é previsível, e a seca longa não vem do oceano**: Fração de municípios com quebra do milho. Depois de 1998: 0,33 em 1999 e 0,07 em 2000. Depois de 2010: 0,07 em 2011 e 0,63 em 2012. Depois de 2016: 0,27 em 2017 e 0,15 em 2018. Depois de 2024: 0,30 em 2025. A taxa de um ano qualquer é 0,229. O pior ano da série (2012, 0,63) veio depois de um La Niña, e nenhum método cobre a seca de 2012–15 (LOYO, de 0,62 a 0,71). Chance de pelo menos 1 quebra em 3 anos (mediana dos municípios): 0,58 supondo anos independentes, 0,50 nos blocos reais de 3 anos. As quebras se agrupam. _[portoes_precos.py, seção (2)]_
- **Preço: o feijão tem proteção natural parcial; o milho, não**: Correlação de Spearman entre o preço deflacionado e o rendimento (medianas do NE, 2006–25): feijão −0,52 (em 2016, preço 1,31 vez a mediana), mandioca −0,49, milho +0,26. Faixa P10/P50/P90 do preço entre os municípios, 2016–25, em R$ de 2025/kg: milho 0,82/1,18/1,71; feijão 2,71/4,41/6,55; mandioca 0,41/0,77/1,71. _[portoes_precos.py, seção (3)]_
- **Conferência com o número canônico**: A mediana da chance de quebra do milho em 2027 nos municípios do CE sai 0,56 no método recomendado, contra P(2,04) = 0,54 (IC90 de 0,24 a 0,75) do modelo logístico da folha 9.7. Medianas de 2027 por UF no milho: RN 0,63, CE 0,56, PB 0,52, PE 0,49, PI 0,47, BA 0,28, AL 0,25, MA 0,21, SE 0,14. Em 2028 (só clima): de 0,06 a 0,34. _[projecao_mun.json, agregado por UF; proposta/PROPOSTA_FINAL_v3.md:1212]_
- **Quixadá (exemplo da demo), projeção com o método recomendado**: Milho: mediana de 492 kg/ha (8,2 sc). Em 2027: P50 151 kg (2,5 sc), P80 450 kg, P20 0. Chance de quebra 0,68. Chance de não pagar a semente 0,56 e o desembolso ≥ 0,95. Medido nos anos parecidos: 0 em 1998, 60 em 2016, 228 em 2024. Em 2028 e 2029 (clima): P20 182, P50 492, P80 992 kg; quebra 0,28. Feijão em 2027: P50 149 kg (normal 297); quebra 0,51; medido 51, 120 e 212. Mandioca em 2027: P50 6,0 t/ha (normal 8,9); quebra 0,25. Pelo menos 1 quebra em 2027–29: milho 0,83, feijão 0,65, mandioca 0,39. _[projecao.py → projecao_exemplos.json; extra.py (rendimentos de 1998, 2016 e 2024)]_
- **Artefato no cerrado (Barreiras): tendência forte e a mesorregião misturada**: Em Barreiras, o P90 de 2027 do milho sai 24,5 t/ha, contra a mediana de 7,5 t. O pool da mesorregião nos anos de El Niño inclui 2024, com rendimentos altos por tendência e não pelo clima. Lá a mediana de 1998–2025 subestima o nível atual (11,3 t em 2024 e 9,5 t em 2025). Fica a recomendação de não mostrar o P90, e de usar como nível a mediana dos últimos 10 anos onde a tendência for forte. Essa troca não entrou no teste. _[projecao.py (saída de Barreiras); extra.py (linhas de 2903201)]_

## Reaproveitar
- notebooks/secoes_financeiro/06_risco.py (definição de quebra, grupos de El Niño forte e da seca de 2012–16, CVaR10) → site-versao-final, tela Retorno financeiro: Usar as mesmas definições (quebra = produção ÷ área plantada abaixo de 50% da mediana) para o leque e o painel financeiro falarem a mesma língua.
- notebooks/secoes_financeiro/05_custo.py:210-212 (semente e desembolso da CONAB, em R$ de 2025) → projecao.py (CUSTO) e o componente do leque: Linhas horizontais no leque da receita e 'chance de não pagar a semente/o desembolso'.
- protótipo/motor.py:241-258 (_perspectiva_municipal: chuva IMERG da estação nos El Niños fortes) → resposta /api/local → bloco projecao: Texto ao lado do leque de 2027 ('a chuva da quadra aqui nesses anos foi X% do normal'), junto com o rendimento medido nos mesmos anos.
- proposta/PROPOSTA_FINAL_v3.md:1212 (P(2,04) = 0,54; IC90 de 0,24 a 0,75; análogos 0,75, 0,70 e 0,08) → selo de 2027 no leque: Conferência e texto oficial no nível do estado. A mediana do CE no meu método (0,56) bate com esse número.
- scratchpad/analise10/projecao/*.py e projecao_mun.json → site-versao-final/dados/projecao/: Mover para o repositório antes que o scratchpad seja apagado. O projecao.py regenera o JSON em cerca de 20 s.

## Proposta detalhada
## 1. O que é medido, o que é projeção e o que é suposição

- **Medido (dado):**
  - rendimento por ha plantado do PAM, 1998–2025; é estimativa do IBGE no município, não medida de campo;
  - IMERG mensal por município: Final até 09/2025, Late depois;
  - SMAP L4 de 2015 a 2026;
  - ONI ASO/2026 = 2,46;
  - preço deflacionado do PAM (R$ de 2025);
  - custo da CONAB.
- **Projeção:** os quantis P10/P20/P50/P80/P90 do rendimento e da receita por município, cultura e ano (2027, 2028 e 2029), e a chance de quebra.
- **Suposições:**
  - o futuro se parece com 1998–2025 (estacionariedade, sem tendência);
  - 2027 se parece com os 3 anos de ONI ASO ≥ 1,0;
  - o preço é a mediana de 2016–25;
  - o custo é o da CONAB, de lavoura acima da média.

## 2. Método escolhido ("C + D + conforme")

Notação: y(m,t) é o rendimento por ha plantado; med(m) é a mediana do município em 1998–2025; R = y/med; n(m) é o número de anos do município; K = 10.

- **C (clima, para 2028 e 2029):**
  - q_C(p) = med × [w·Q_mun(R, p) + (1−w)·Q_meso(R, p)], com w = n/(n+K) (média de quantis, à Vincent);
  - P(quebra) = w·freq_mun(R < 0,5) + (1−w)·freq_meso(R < 0,5).
- **D (2027):** a mesma conta, mas só com os anos de ONI ASO(t−1) ≥ 1,0 (1998, 2016 e 2024). Nesse caso n tem no máximo 3, então w ≤ 0,23 e quem domina é a mesorregião.
- **Alargamento conforme, calibrado no walk-forward 2008–2025:**
  - 2027: P10 −0,155·med; P90 +0,155·med; P20 −0,079·med; P80 +0,079·med (corte em 0);
  - 2028 e 2029: 0,104 e 0,056.
- **Quebra** (definição canônica): R < 0,5.
- **Receita:** kg × preço mediano do município em 2016–25. Na falta dele, a mediana da UF.
- **Chance de não pagar:** interpolação do custo nos quantis da receita. Semente e desembolso da CONAB: milho 284 e 1.136; feijão 142 e 1.992; mandioca 0 e 4.387 R$/ha.
- **Pelo menos 1 quebra em 3 anos:** 1 − Π(1 − p_ano). Os blocos reais de 3 anos dão um pouco menos (0,50 contra 0,58), porque as quebras se agrupam.

## 3. Backtest (rodado; 1.783 municípios, milho, feijão e mandioca)

Métodos testados:
- A: quantis do município;
- B: tendência log-OLS removida;
- C: encolhimento para a mesorregião;
- D: condicionado ao ONI;
- D2: D com nível pela tendência;
- E: regressão quantílica pooled com ONI, ONI⁺, semiárido×ONI⁺ e ano;
- F: D + conforme, só no walk-forward.

| Modo / grupo | Métrica | A | B | C | D | D2 | E | F |
|---|---|---|---|---|---|---|---|---|
| LOYO, milho | cobertura 80% | 0,764 | 0,736 | **0,777** | 0,742 | 0,701 | 0,768 | – |
| LOYO, todos | média por ano | 0,771 | 0,731 | **0,775** | 0,748 | 0,692 | 0,772 | – |
| LOYO, El Niño (98/16/24) | cobertura | 0,678 | 0,642 | 0,687 | 0,555 | 0,589 | 0,700 | – |
| LOYO, El Niño | piso P20 (meta 0,80) | 0,639 | 0,607 | 0,637 | 0,701 | 0,751 | 0,756 | – |
| LOYO, El Niño | quebra prevista / observada | 0,16/0,30 | 0,18/0,30 | 0,16/0,30 | **0,30/0,30** | 0,35/0,30 | 0,30/0,30 | – |
| LOYO, seca 2012–15 | cobertura | 0,706 | 0,625 | 0,712 | 0,679 | 0,616 | 0,701 | – |
| WF, todos | média por ano | 0,665 | 0,606 | 0,688 | 0,645 | 0,602 | 0,562 | **0,783** |
| WF, todos | pior ano | 0,42 | 0,33 | 0,45 | 0,39 | 0,38 | 0,29 | **0,565** |
| WF, El Niño | piso P20 | 0,723 | 0,694 | 0,715 | 0,818 | 0,872 | 0,764 | **0,883** |
| WF, milho | cobertura | 0,641 | 0,628 | 0,674 | 0,623 | 0,613 | 0,259 (falhou) | **0,772** |

Brier da quebra, LOYO, milho: de 0,162 (B) a 0,178 (E). O erro está no nível do ano: no milho, a fração de municípios em quebra vai de 0,04 a 0,63 entre os anos, e todo método sem oceano prevê cerca de 0,22 em qualquer ano.

## 4. Como dizer "segurança" (texto e visual)

- **Linha 1 (anos parecidos, medido):** "Nos 3 anos com o mar assim (1998, 2016, 2024), o milho de Quixadá deu 0, 1 e 4 sacos/ha. O normal daqui é 8."
- **Linha 2 (frequência):** uma grade de 10 roças. Em 2027, 7 pintadas: "em 7 de 10 anos parecidos a roça de milho do município quebrou".
- **Linha 3 (piso):** "Em 8 de 10 anos parecidos você colhe pelo menos X sacos/ha". X é o P20 já alargado. Se X = 0, escrever: "não há piso: em 2 de 10 anos parecidos não se colhe nada".
- **Linha 4 (dinheiro):** "Em 9 de 10 anos assim, o milho não paga o desembolso; o feijão também não; a mandioca sim em ~8 de 10" (no JSON: 0,95, 0,95 e 0,23).
- **Leque (fan chart):**
  - eixo x: novembro/2026 → 19/mar → 30/abr (2027) → safra 2028 → safra 2029;
  - faixa P20–P80 escura, P10–P90 clara, linha P50, linha tracejada do normal (mediana), marcas da semente e do desembolso;
  - o leque de 2027 estreita nos portões, com a tabela da chuva desde fevereiro;
  - 2028 e 2029 ficam largos e iguais, com o selo "só clima".

```
sacos/ha (milho, Quixadá)
16 |                                  ░░░░░░░    ░░░░░░░
12 |                                  ▒▒▒▒▒▒▒    ▒▒▒▒▒▒▒
 8 | - - - normal - - - - - - - - - - ●───────── ●──────  ← 2028/29: só clima
 4 |  ░▒▒●▒▒░   (se chover <75%: ▼)  ▒▒▒▒▒▒▒    ▒▒▒▒▒▒▒
 0 |__▒▒▒▒▒▒______(se chover >100%: ▲)_░░░░░░░____░░░░░░░__
     nov/26   19/mar  30/abr      safra 2028  safra 2029
     [selo: mar acima do recorde 2,46 → 3 anos parecidos; extrapolação]
     ■■■■■■■□□□  7 de 10 roças do município quebraram em anos assim
```

- **Mudança na quadra (pré-calculada, R ao normal, milho do semiárido):**

| Chuva fev–abr | P50 | Chance de quebra |
|---|---|---|
| abaixo de 75% | 0,33 | 0,60 |
| 75–100% | 0,72 | 0,37 |
| 100% ou mais | 1,36 | 0,10 |

## 5. O que muda entre 2027, 2028 e 2029

- **2027:**
  - há sinal do oceano, mas o ONI de 2,46 está fora da série (máximo ASO 2,04);
  - os 3 anos parecidos discordam (2024 foi bom);
  - mostrar os três anos separados e a chance média; nunca um único "vai quebrar";
  - a projeção é revista em 19/mar e 30/abr com o IMERG e o SMAP.
- **2028 e 2029:**
  - só clima. O ano depois do El Niño não tem sinal estável (quebra de 0,07 a 0,33 contra 0,23 de base);
  - mostrar o leque climatológico e a chance de pelo menos 1 quebra em 3 anos (milho em Quixadá: 0,83).

## 6. O que NÃO dá para projetar (dizer na tela)

- secas plurianuais como a de 2012–15 (vêm sem aviso do oceano);
- a roça de uma família: o PAM é média municipal, e a roça individual varia mais;
- a mandioca ano a ano (PAM repetido em 29% dos anos);
- sorgo, caupi separado, guandu e palma (sem série municipal);
- o ganho da rotação: o +24% é literatura (T1), não está no PAM;
- preço futuro: só a faixa histórica;
- irrigação ou baixio: o PAM mistura e é quase todo sequeiro;
- o litoral leste: o IMERG capta só 39–72% da chuva do INMET, então os portões valem para a quadra do norte;
- o cerrado com tendência forte: o P90 de Barreiras é um artefato.

## 7. Contrato do JSON (gerado: projecao_mun.json, 1.783 municípios, ~7,4 MB; exemplos em projecao_exemplos.json)

```
{"2311306": {"municipio":"Quixadá","uf":"CE","mesorregiao":"Sertões Cearenses",
  "Milho": {"mediana_1998_2025_kg_ha":492,"n_anos":28,"n_anos_el_nino_forte":3,
    "peso_municipio_2027":0.23,"peso_municipio_clima":0.74,"preco_r2025_kg":1.32,
    "custo_r2025_ha":{"semente":284,"desembolso":1136},
    "medido_anos_parecidos_kg_ha":{"1998":0,"2016":60,"2024":228},
    "anos":{
      "2027":{"kg_ha":{"p10":0,"p20":0,"p50":151,"p80":450,"p90":608},
              "sacos60_ha":{"p10":0.0,"p20":0.0,"p50":2.5,"p80":7.5,"p90":10.1},
              "chance_quebra":0.68,"receita_r2025_ha":{"p10":0,"p20":0,"p50":200,"p80":596,"p90":804},
              "chance_nao_paga_semente":0.56,"chance_nao_paga_desembolso":0.95,
              "base":"ONI ago–out ≥ 1,0 (safras 1998, 2016, 2024); ONI 2026 = 2,46 fora da série (extrapolação)"},
      "2028":{"kg_ha":{"p10":66,"p20":182,"p50":492,"p80":992,"p90":1388},"chance_quebra":0.28,
              "chance_nao_paga_semente":0.23,"chance_nao_paga_desembolso":0.72,"base":"só clima ..."},
      "2029":{...igual a 2028...}},
    "chance_ao_menos_1_quebra_2027_2029":0.83},
  "Feijão": {...2027: p50 149 kg, quebra 0,51; medido 51/120/212...},
  "Mandioca": {...2027: p50 6.036 kg, quebra 0,25...}}}
```

Notas sobre o JSON:
- Valores 0,95 e 0,05 nas chances de não pagar indicam o limite da interpolação: leia "≥ 9 em 10" e "≤ 1 em 10".
- Sugestão: o motor carrega o JSON (ou um parquet) e acrescenta "projecao" na resposta de /api/local. Assim a página continua estática no front.

## 8. Arquivos (scratchpad, copiar para o repositório)

Pasta: C:/Users/NETINH~1/AppData/Local/Temp/claude/88b277d27b184113/73cd62bd-b6e9-4872-9e4a-a06e5ca404a0/scratchpad/analise10/projecao/

- backtest.py → bt_linhas.parquet (1.374.902 linhas)
- metricas.py → metricas.txt
- portoes_precos.py (portões, persistência e preço)
- extra.py (fatores do conforme, mistura C+D, anos parecidos)
- projecao.py → projecao_mun.json e projecao_exemplos.json

## Riscos
- 2027 está fora da série (ONI 2,46 contra o máximo de 2,04), e só há 3 anos parecidos, que discordam entre si: 2024 foi bom. Qualquer número de 2027 precisa do selo de extrapolação e dos três anos mostrados separados.
- Os erros são correlacionados dentro do ano: o conformal agrupado trata município-anos como trocáveis. Mesmo com o alargamento, um ano como 2024 ou 2012 cobre só 0,57–0,60.
- Os fatores do conforme (0,155/0,079 e 0,104/0,056) foram calibrados nos mesmos dados do backtest. A calibração reportada é levemente otimista.
- O PAM é a média do município, e a roça de uma família varia mais. 'Em 8 de 10 anos' vale para as roças do município, não para a roça dele. Escrever assim.
- Mandioca: rendimento repetido em 28,6% dos anos, então o leque estreito engana.
- Cerrado com tendência (Barreiras): o P90 sai absurdo (24,5 t/ha de milho) e a mediana de 1998–2025 subestima o nível atual. Esconder o P90 e revisar o nível depois.
- Litoral leste (312 municípios): o IMERG subestima a chuva (39–72%), e a atualização nos portões não vale lá.
- O custo da CONAB é de lavoura acima da média (milho 3,4 vezes o rendimento do PAM), então 'não paga o desembolso' pode assustar. Mostrar a semente como a primeira linha.
- Os portões usam meses inteiros (fev–mar e fev–abr), não os decêndios de 19/mar e 30/abr. É aproximação a recalcular com o diário se der tempo.
- Os arquivos estão no scratchpad (apagado em ~1,5 dia): copiar para o repositório.

## Perguntas abertas
- Mostrar o P90 ('ano muito bom') ou parar no P80? Recomendo parar no P80, por causa do artefato do cerrado e porque o tema é segurança.
- Qual número de 2027 vai para a tela no nível do estado: o logístico canônico (0,54, IC90 de 0,24 a 0,75) ou a mediana municipal deste método (CE 0,56)? São consistentes, mas a tela deve citar um só.
- Caupi, sorgo e palma do plano de rotação não têm série municipal. Na tela de segurança, o caupi usa o 'Feijão' do PAM, com aviso, ou fica sem leque?
- Para a receita, o site vai perguntar a área plantada (ha) e se ele vende ou come a colheita? O preço só importa se ele vende.
- O JSON de 7,4 MB vai inteiro para o front estático, ou o motor serve por município no /api/local (recomendado)?