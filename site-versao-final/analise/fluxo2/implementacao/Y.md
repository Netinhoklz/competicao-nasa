# Y: correção do plano, terreno, ideal, dinheiro e relatório (rodada 2, fase 5, 15/11/2026)

Achados dos revisores R1, R2 e R3 para o meu grupo (39). Corrigi todos os de gravidade alta e média e os baixos baratos. Não reiniciei
o servidor, não fiz commit e usei um Edge sem janela por vez (perfis e prints em `E:/campeonato-nasa/tmp/fluxo2/Y/`).

**Aviso de máquina (11:36):** o C: chegou a 1 MB livre (pagefile de 22,9 GB, memória comprometida quase cheia) e os comandos do Claude
Code falhavam. Nada foi apagado: movi para `E:\c_movido_2026-11-15\` o cache DX da NVIDIA (3,0 GB) e os rastros `.etl` da Área de
Trabalho Remota em `%TEMP%\DiagOutputDir` (2,7 GB), com `robocopy /MOVE`, a receita da memória. Como devolver: `LEIA-ME.txt` na pasta.

## 1. Mudanças de definição (mudam números à vista; explicadas aqui)

1. **Prioridade padrão do "O ideal" pelos números** (`ideal.escolhaPadrao`). Antes: "Guardar água" sempre em ano de alerta. Agora o lado
   ideal nunca abre numa prioridade que perde para outra nos 3 números (ano normal, 2027 e quebra). Em ano de alerta vale a que mais
   sobra em 2027 (até R$ 50 = empate, decide o ano normal). Fora do alerta, "Um pouco de cada", se ninguém a vence. Sem R$ aqui, a regra
   antiga. A resposta da pessoa sempre manda. `ef.prioridade` só vale quando é resposta (o `roca.js` põe "garantir" sem resposta).
   O selo diz "(a que mais sobra em 2027 aqui)".
   - Quixadá padrão abre em **Mais renda**: R$ 3.080 por ano / R$ 266 em 2027 / 1 em 10. Antes, Guardar água: R$ 1.950 / −R$ 33.
   - Os 3 anos do passo 4 com a prioridade padrão: Hoje R$ 2.480 · Melhorado R$ 2.550 · Ideal Mais renda R$ 6.640.
     Com `prioridade=garantir`, continua R$ 3.980. Com `equilibrar`, continua R$ 4.360. O `teste_dinheiro.mjs` passa com esses números.
2. **"Sobra num ano normal" = a média de 2028 e 2029**, com o plano já rodando. Antes era só 2029. A mandioca fica 2 anos no chão:
   num ano colhe uma parte, no outro outra. Só 2029 dava "R$ 0" na mandioca sozinha.
   A quebra usa o mesmo ano normal. O "8 em 10" e os 28 anos continuam na configuração de 2029, como `calculo.replay`;
   o `teste_dinheiro.mjs` confere isso.
3. **"Sobra em 2027, ano de El Niño" = o que sobrou em pelo menos 3 dos 4 El Niños fortes** (o 2º pior). Antes era a mediana dos 4. Em
   Caicó, a mediana (R$ 921) passava a do ano normal (R$ 558). Hoje em Caicó, 2027 dá R$ 7. Os 4 anos e a mediana ficam no `detalhe`;
   a faixa vai do pior ao melhor.
4. **Comida em dois números:** `comida_kg` passa a ser só grão (milho e feijão). Entra um item novo, `raiz_kg` (raiz de mandioca fresca).
   São 9 itens. Antes, 56 kg de grão + 1.285 kg de raiz viravam "1.342 kg de comida".
5. **A mandioca marcada em "O que planta hoje?" já está no chão**, qualquer que seja a resposta da maniva. Nas colunas Melhorado e Ideal,
   ela colhe em 2027 como na coluna Hoje (o "plantada" de `calculo.js`, sem mudar o arquivo).
   - "Tenho" e "Não sei": a rama replanta (a reserva segue).
   - "Não tenho": não planta mandioca nova. A do chão colhe em 2027 numa parte (`velha`) e a parte entra no giro em 2028.
6. **As perenes que ele já tem ficam num pedaço próprio do desenho, em escala**, no alto: "Já plantado · palma · 50 m". Não viram cerca.
   O giro, o material e o R$ usam só o resto (`ha_giro`), a mesma área da conta.
7. **Palma forrageira com número de forragem:** 10 t de matéria seca por ha por ano. É o valor de referência da Tab. 1 em Embrapa/MilkPoint
   2013, a mesma fonte que o A1 já citava para o sorgo. O selo é SUPOSIÇÃO. Conta do 2º ano em diante.

## 2. Achado por achado

| # | grav. | situação | o que mudou |
|---|---|---|---|
| 1 | alta | corrigido | prioridade padrão pelos números (seção 1.1). Nos 8 municípios × 30 respostas, a padrão nunca perde para outra nos 3 números (conferido no `teste_ideal.mjs`) |
| 2 | alta | corrigido | o P2 antes do 1º plantio vira "A chuva está voltando: ainda não plante". Quixadá: "O milho é de 21/02/2027 a 28/02/2027: espere essa data e confira com o técnico a data do zoneamento". "Plante uma parte e guarde a outra" vai para a 1ª tarefa de plantio. O WhatsApp leva o título novo |
| 3 | alta | corrigido no motor | seção 1.5. Seu Antônio "Tenho" em 2027: Hoje R$ 2.500 / Melhorado R$ 3.740 / Ideal R$ 3.750 (antes 2.590 / 666 / −114). Petrolina "Não tenho" em 2027: 723 / 1.600 (antes 30). A pergunta na tela é do X (pedido 1) |
| 4 | média | corrigido | baixio "não sei": tarefas "Parte B e baixio (se tiver)"; o material do baixio vem à parte, "se tiver baixio". Cultura sem data aqui (milho de Petrolina) sai do material: "Só se o técnico der a data de plantar: milho (Parte B)" |
| 5 | média | corrigido | `ideal.falaTexto`, usado só na hora de mostrar: legenda, rotação, notas, 2028/2029 do Relatório e manchete. Troca tampão, leguminosa, cereal, solteiro, precoce, → e "kg de N". "Só cabe salvar" → "Salvar o que der: forragem e animais". O P5 e o P2 vêm sem jargão. Os textos de máquina não mudam: o desenho, a agenda e o material leem "revezamento" e "solteiro" |
| 6 | média | corrigido | rótulo de cada faixa com os metros, também no celular ("A · caupi · 11,3 m", "Baixio · milho + caupi · 33,8 m"). Sob o desenho: "Carreira × cova: A e C caupi 80 × 50 cm · B e baixio milho 100 × 50 cm", com selo. "Seu terreno: metros e distância das covas" abre sozinho com larg e comp (até a pessoa fechar) |
| 7, 24, 36 | média/baixa | em parte | sem peso de semente do milho em fonte lida, não converto para kg. Agora: "≈ 33 mil sementes (menos de 1 saco de 60 mil)". O saco de 60 mil vem da Embrapa Milho e Sorgo, 500 Perguntas, p. 104, e está no agronomia.json (`saco_sementes`). Falta: o peso de 1.000 sementes (A1) |
| 8 | média | corrigido | o material e o terreno levam SUPOSIÇÃO, com a fonte do espaçamento no balão. O selo da linha segue a coluna escolhida, e o "medido" do Hoje vai no balão. Ano normal sem nenhuma colheita com R$ vira "não medido", não R$ 0 |
| 9 | média | corrigido | as perenes dele não viram mais cerca: entram no pedaço "Já plantado" (seção 1.6). A cerca nomeia cada quantidade: "≈ 1.160 raquetes de palma e ≈ 69 estacas de gliricídia" |
| 10 | média | corrigido | ano escolhido com fundo `--green-soft`, borda verde e texto claro (plantio.css) |
| 11 | baixa | corrigido | WhatsApp com "2027: A e C caupi · B milho · baixio (se tiver) milho + caupi (faixas de 11 m)" e a linha do material. "só a chuva" virou "roça de chuva" |
| 12, 30 | alta | corrigido | só mandioca: as partes desencontram (A e C plantam, B colhe em 2027 a do chão). Quixadá, ano normal: Hoje R$ 3.637 / Melhorado R$ 3.637 (antes R$ 0); 3 anos 9.488 / 10.356. Só mandioca e "Não tenho": giro com milho e feijão, com a nota; o terreno nunca escreve cultura vazia |
| 13 | alta | corrigido | seção 1.4. "Em 8 de 10 anos" diz "X kg de grão e Y kg de raiz de mandioca". `ganhosDe` compara grão com grão |
| 14 | alta | corrigido | uma regra só, `terreno.nadaDe` (com as fases da mandioca, `fasesMandioca`). O Plano e o Relatório dizem "já está no chão" / "mandioca segue no chão" nas mesmas partes |
| 15 | alta | corrigido | `desenho.montar` reserva `fora_do_giro` (seção 1.6). Mandioca e palma em 40 × 100 m: 650 manivas por parte de 0,067 ha (antes 3.900 para 0,4 ha) |
| 16, 28 | alta | corrigido | a fonte de R$ e o texto da perda dizem o que fica fora do R$ (palma, sorgo de grão, forragem). Com "Guardar água", a "Comida do gado" entra nas 4 linhas à vista, no lugar do adubo. Se o ideal perde para o melhorado em 2027: "R$ X a menos que o seu jeito melhorado em 2027, com +Y t de comida do gado por ano" |
| 17 | média | corrigido | "Quase igual a hoje" só sem ganho nem perda, com a diferença abaixo de R$ 50. "O ganho maior vem com o ideal" só quando o ideal passa Hoje e Melhorado num número de R$ ou de quebra |
| 18 | média | corrigido | revezamento e data estimada levam SUPOSIÇÃO (`/^ZARC/`). O "como" da colheita só leva selo quando a frase é da cultura, com a fonte dela. Quantidades: SUPOSIÇÃO |
| 19 | média | corrigido | `ideal.textoItem(U, item)` é o formatador único do Plano e do "Ver como calculamos" |
| 20 | média | corrigido | caupi no milho em pé conta pelo `consorcio` do agronomia.json (500 Perguntas, cap. 12): covas a 25 cm com 2 sementes (8 por metro) e 17 a 20 g por 100 sementes. Quixadá, baixio: ≈ 4,8 kg (antes 7,3) |
| 21 | média | corrigido | o feijão comum ganhou `fonte_fraca` ("ensaio irrigado em Goiás") e uma linha no "como": confirmar com o técnico. Os números do terreno já são SUPOSIÇÃO. Falta: uma fonte de sequeiro (A1) |
| 22 | média | corrigido | quando a decisão da metade cai antes da janela: "Ano de alerta: plante conforme a decisão de 10/03/2027 (veja a tarefa do dia)" |
| 23 | baixa | corrigido | preparo a mais de 7 dias do plantio: sai "Plante logo depois…" e entra "O plantio destas partes é de …". O plantio mostra, à vista, "Dá para plantar desde 21/01/2027, com mais risco" |
| 25 | baixa | corrigido | gliricídia: `material_unidade` "estacas" |
| 26, 39 | baixa | corrigido | sem ponto duplo no "como" |
| 27 | baixa | corrigido | "2027, cada cultura" só com o que o plano colhe em 2027 (sem a mandioca nova). Sem nenhuma: "Em 2027 este plano não colhe milho, feijão nem mandioca" |
| 29 | alta | corrigido | a conta parcial com uma série faltando (Caicó, sem a mandioca) aparece "sem a mandioca", em vez de 3 "não medido". Quando o ideal perde em R$: "O ideal daqui não dá mais dinheiro que hoje", com o que ele ganha. Entra, à vista, a linha "Aqui o IBGE mistura lavoura grande" |
| 31 | média | corrigido | seção 1.3 |
| 32 | média | corrigido | 1 linha de ganho dentro de cada lado do controle. Quixadá: "O ideal · +R$ 2.170 por ano". A linha tem uma linha só, para o desenho ficar a ≤ 550 px |
| 33 | média | corrigido | o melhorado lê o risco do ZARC no solo respondido (`cardapio[].por_solo`). Sem janela de 20% nem de 30%, o milho fica só no baixio, quando a terra alta continua girando. Aviso: "Na areia, o milho só tem plantio de 11/01–20/01, com mais risco aqui: ele fica só no baixio." Sem outro papel na terra alta, o milho fica e o aviso diz "plante o milho no baixio" |
| 34 | média | corrigido | roçado todo perene: "Sem R$: o seu roçado inteiro já é palma: não sobra chão para girar". Não diz mais "Quase igual" |
| 35 | média | corrigido | "Um pouco de cada" ganha o "por quê" do motor em `plano.por_que_de`. As faixas do núcleo não mudam, e `agendaDe` continua devolvendo `r.agenda.linhas` |
| 37 | baixa | corrigido | (= 8) |
| 38 | baixa | corrigido | a barra e a nota usam um número só (79). O arquivo vai para o balão do selo |

Outros ajustes feitos no caminho:
- `chaveDe` ganhou `ef.terra`, porque a memória misturava respostas de terra no mesmo `r`.
- `pareado.js` usa `baseComum` e `itensPlano`, que o `ideal.js` agora exporta, em vez das cópias.
- `cenarios.js` (Os 4 jeitos) acende a prioridade que o Plano usa (`opcoes.prioridade`).

## 3. Arquivos

- `web/js/extras/ideal.js`: motor (maniva, só mandioca, milho no solo, prioridade padrão, ano normal, El Niño 3 de 4, grão/raiz,
  conta parcial, `ha_giro` = 0, `textoItem`, `falaTexto`, `baseComum`, `itensPlano` exportados, `por_que_de`, textos sem jargão).
- `web/js/passos/plantio/desenho.js`: o pedaço das perenes em escala (`reserva`, `haGiro`, `profPer`) e a grade com ele.
- `web/js/extras/terreno.js`: `nadaDe`, `fasesMandioca`, o pedaço das perenes, o caupi no milho, as sementes em mil e o saco, o nome
  de cada quantidade, o selo.
- `web/js/passos/plantio.js` e `web/css/passos/plantio.css`: o controle com o ganho, os metros no desenho, a distância das covas,
  o terreno que abre sozinho, "O que você ganha" (9 itens, comida do gado no Água, franqueza, selo, quase igual), `falaTexto`, a cor do ano.
- `web/js/passos/relatorio.js`: o P2, a metade, o preparo, os selos, o baixio "se tiver", a cultura sem data, o material (regra única),
  2028/2029 sem jargão, o resumo para o WhatsApp.
- `web/js/extras/leve_ao_tecnico.js`: as partes e o material no WhatsApp; "roça de chuva".
- `web/js/passos/dinheiro.js`, `web/js/passos/dinheiro/pareado.js`: o formatador único, grão e raiz no "8 em 10", o "2027, cada
  cultura", o 79, os 4 jeitos com a prioridade do Plano; o pareado sobre a base do ideal.
- `web/js/extras/cenarios.js`: só `opcoes.prioridade` no render.
- `web/js/extras/hoje_ideal.js`: o rótulo da prioridade sugerida diz a origem nova ("sugerido: a que mais sobra em 2027").
- `web/dados/agronomia.json`: palma 10 t de MS (referência), `consorcio` do caupi, `saco_sementes` do milho, a gliricídia em
  estacas, `fonte_fraca` do feijão comum.
- `testes/ferramentas/teste_ideal.mjs`: 9 itens e 6 casos novos (só mandioca, só mandioca sem rama, mandioca no chão "Tenho", só palma,
  mandioca + palma em metros, areia). Conferências novas:
  - a mandioca do chão colhe em 2027 no melhorado;
  - todo ano tem colheita quando o hoje colhe;
  - nenhuma parte repete outra quando o giro tem 3 papéis;
  - só mandioca não deixa as 3 partes iguais;
  - o melhorado tem sobra num ano normal quando o hoje tem;
  - a prioridade padrão nunca perde nos 3 números;
  - grão e raiz não se somam.

## 4. Como testei (números)

- `node --check` em todos os JS mexidos.
- `teste_ideal.mjs`: 190.208 conferências, 0 falha; 51 de 51 linhas do núcleo refeitas iguais. Quixadá padrão no `comparar()` do
  passo 4: hoje 2.476 / ideal 4.364 (arredondados 2.480 / 4.360).
- `teste_dinheiro.mjs` (do C3, sem mudar): 22.445 conferências, 0 falha. Quixadá padrão, 3 anos: hoje R$ 2.480, melhor R$ 2.550,
  garantir R$ 3.980, equilibrar R$ 4.360.
- `teste_relatorio.mjs` (do C4, sem mudar): 168 casos, 19.552 conferências, 0 falha. Toda data do relatório existe na agenda.
- `teste_calculo.mjs`: o `calculo.js` não mudou; a saída é a mesma de antes.
- `aceite_fluxo.py --so-telas --so-toques` nos 7 municípios, a 390 px (E:/campeonato-nasa/tmp/fluxo2/Y/aceite_final.txt):
  - **telas:** 0 falhas em 35, com zero erro no console. Plano, lado "seu jeito": 357 a 391 palavras, desenho a 548 px. Lado ideal: 392 a
    426 palavras (teto 430; antes, Picos 457 e Barreiras 456). Relatório de Quixadá: 16 tarefas, 30 datas.
  - **toques:** 11 de 13 ok. C2 e C8 falham pela mudança de definição (pedidos 2 e 3 abaixo). C10 ok: 54 datas, 0 fora da agenda,
    WhatsApp com 1.105 letras.
- No node, com `E:/campeonato-nasa/tmp/fluxo2/Y/conf_terreno.mjs`: os casos de reprodução dos revisores, comparando o terreno, o
  material e as tarefas. Exemplos:
  - mandioca + palma em 40 × 100 m: pedaço "Já plantado" de 0,2 ha; A e B "já está no chão", C ≈ 650 manivas.
  - 2028: B ≈ 650 manivas (a parte que colheu em 2027 replanta) e A e C "mandioca segue no chão".

## 5. O que ficou faltando

- **kg de semente do milho, mucuna, feijão comum e girassol:** falta o peso de 1.000 sementes com fonte (A1). Por enquanto mostro "mil
  sementes" e, no milho, a fração do saco de 60 mil.
- **Fonte de sequeiro do Nordeste para o feijão comum** (A1).
- "Mais renda" em Picos e outros: as 3 partes iguais nos 3 anos (caupi, sorgo de grão, caupi). É o desenho das rotações de
  `cenarios.js`. Não mexi no gerador das rotações nesta fase, e só o melhorado ganhou a conferência de partes desencontradas.
- O "Não tenho" com a mandioca no chão segue a regra do revisor: não planta mandioca nova, e a parte dela entra no giro em 2028. Por isso o
  ano normal do melhorado cai (Petrolina: R$ 615 hoje × R$ 46), e a tela diz "Sobra menos que hoje num ano normal". Se o X mudar a pergunta
  para "Tem rama para plantar **mais** mandioca?", vale pensar se o "Não tenho" deve manter a área de hoje com a rama da própria colheita.
- O ideal desenhado sobre um roçado todo perene (`ha_giro` = 0) ainda mostra as faixas do ideal. A tela diz que não sobra chão para
  girar, mas o desenho e o material do ideal não somem.

## 6. Pedidos ao integrador

1. **Ao X (Sua roça, `perguntas.js`):** com a mandioca marcada em "O que planta hoje?", perguntar "Tem rama para plantar mais
   mandioca?" e tirar "Já está plantada", que o motor já supõe.
2. **`aceite_fluxo.py`, C2:** os R$ de Quixadá na URL padrão do passo 4 agora são Hoje 2.480 · Melhorado 2.550 · Ideal **Mais renda
   6.640** (seção 1.1). Guardar água 3.980 continua com `prioridade=garantir`. Trocar o esperado, ou abrir a URL com `prioridade=garantir`.
   **C8:** com a mandioca no jeito de hoje e "Não tenho", a mandioca do chão continua no desenho de 2027 (colhe) e sai de 2028 e 2029
   (sem mandioca nova; seção 1.5). O C8 espera que ela suma do desenho de 2027. Conferir no desenho de 2028 (ou no texto
   "Sem maniva para plantar mais", que está à vista).
3. **`aceite_fluxo.py`:** pôr a lista de palavras proibidas à vista do R1 (tampão, leguminosa, cereal, solteiro, precoce, →). Contar
   como "verde" todo elemento ≥ 60 × 28 px com o fundo do primário (o ano escolhido já não é verde cheio).
4. **`teste_relatorio.mjs` (C4):**
   - nenhuma tarefa com "Plantar" antes da 1ª janela do plano;
   - nenhum material de cultura sem tarefa de plantio;
   - `frases().leve` do Plano igual ao material do Relatório em cada parte (as duas telas já usam `terreno.contas` com `l.nada`).
5. **`teste_dinheiro.mjs` (C3):** se quiserem o "8 em 10" e os 28 anos também no ano normal (média de 2028 e 2029), trocar a conferência
   do `C.replay(m)`. Hoje os dois seguem 2029 e passam.
