# 04 · Júri do NASA Space Apps: parecer no debate

**Em uma frase:** as 10 lentes concordam no essencial: uma tela "Sua roça" já preenchida, o resultado antes dos controles e o corte das perguntas que não mudam nada. Como jurado, escolho o fluxo do **01 (Agricultor)** como base. Ele leva o painel direto à "Sua roça", e o passo 1 sai da frente. Acrescento quatro emendas: a NASA visível nos selos, uma página "Os dados" com a ciência toda junto, os números errados corrigidos e o controle "E se chover…" fora do "ver mais".

Conferi antes de afirmar:
- `grep -i nasa` nos 16 textos de `E:/campeonato-nasa/tmp/fluxo_atual/` dá **0**. No globo (`index.html:37`) e no painel (`painel.html:66`, "NASA GPM IMERG") a palavra aparece.
- `seguranca.js:219` diz "mar quente, **acima do recorde**". A API diz "+2,46; o recorde de qualquer trimestre é +2,59".
- `motor.py:674-678`: o "não sei" da terra é a interseção **só dos solos zoneados**.
- Diferenças no JSON da API, contra o padrão:

  | Resposta | Campos que mudam | Onde |
  |---|---|---|
  | `textura=3` | 77 | 73 na agenda |
  | `textura=1` | 53 | agenda |
  | `maniva=nao` | 30 | 22 no plano |
  | `maniva=plantada` | 9 | faixas e notas do plano |
  | `baixio=0` | 4 | some a faixa do Baixio |

- O passo 4 tem dois seletores da mesma coisa: "O QUE VALE MAIS" no topo e "COMPARE Água/Renda/Solo/Plano" no fim (`15_passo4_dinheiro.txt`; `cenarios.js:18`, `DA_PRIORIDADE`).
- Toque duplo: em `perguntas.js:115-120`, o `q += 1` vem antes de a tela trocar.
- As pílulas da barra já são botões com `data-ir` (`roca.js:107-109`).

---

## 1. Melhores ideias dos outros

| De | Ideia | Por que o júri ganha |
|---|---|---|
| **01 Agricultor** | O painel leva direto a `#/<cod>/2`. A numeração das rotas fica igual, e o passo 1 vira "Do espaço", fora do caminho. | O globo e o painel já contam o "do espaço", com NASA escrita. Na demo de 2 min, repetir o El Niño no passo 1 custa 15 s. São só 4 links a mudar (`principal.js:94`, `rocacerta.js:333`, `roca.js:194, 209`), o menor risco possível. |
| **01 Agricultor** | Juntar os dois seletores de prioridade do passo 4 num só, logo abaixo das barras. | Um seletor que acende o jeito é o ponto 9 em 1 toque, sem a confusão de dois controles iguais. |
| **01 Agricultor** | A área padrão perde o selo MEDIDO e vira "típico daqui · Censo 2017". "Não vende" vira "vira comida da criação (fora do R$)". | O jurado lê "1,03 ha MEDIDO" e pensa que o satélite mediu o roçado. Isso parece exagero, e jurado pune exagero. |
| **03 Valor da informação** | A tabela medida de quais respostas mudam o plano, as datas ou o R$. | Dá à equipe a resposta para a pergunta "por que só 4 perguntas?": "medimos, e só essas mudam o plano". Isso vira ciência, não gosto. |
| **08 Precisão** | Corrigir os números errados ou mal atribuídos: "acima do recorde", "Só o que muda a conta", o "+R$ 909" do "milho no baixio" (o ganho vem da troca por feijão), as 4 frequências do milho em 2027 e o "milho: nenhum dia". | Basta um jurado conferir um número e achar erro para a nota de validade cair inteira. Isto é o que mais importa depois do fluxo. |
| **08 Precisão** | O "não sei" honesto: avisar quando a cultura não é zoneada em todas as terras. | Em 421 municípios, o "não sei" mostra janela de milho que não vale em terra arenosa. Um jurado agrônomo pega isso. |
| **02, 06, 10 e 01** | O preparo da terra entra no custo: "Paga trator ou adubo? Não / Sim". | Cobre os equipamentos do ponto 15 com as palavras do agricultor, e a resposta muda o R$ (03 mediu: a sobra vai de R$ 4.364 para −R$ 1.743). |
| **06 Arquitetura** | Todo "mudar" abre a pergunta certa e devolve a pessoa ao passo de onde veio. | Hoje tocar em "1,0 ha" leva a "Como você planta hoje? 1 de 3". Numa demo ao vivo, isso é constrangedor. |
| **07 Visual e 10 Radical** | "Em 2025 também foi milho e feijão? Sim / Não", à vista no cartão do giro. | Mantém o histórico pedido pelo José visível e de 1 toque, no lugar onde a resposta muda a frase. |
| **01 e 08** | Memória no passo 5: "O IBGE anotou 1998, 2012 e 2016 como os piores. Bate com a sua roça?", com toque no ano. | Junta o ponto 16 (o saber local) e o ponto 6 (validar o modelo) numa frase. É a melhor fala da demo para o júri. |
| **09 Mobile** | Critério medido para aceitar cada passo de resultado: até 1.900 px e até 150 palavras à vista. Alvos de 44 px e contraste do `.eco` de 2,8 para 4,9:1. | Dá um alvo verificável para o fim da noite: ou passou, ou não passou. |
| **09 Mobile** | Link "Internet fraca? Entrar sem o globo". | O globo pesa 7,8 MB. Mostra ao júri que pensamos no Android simples (ponto 14), e custa 10 min. |
| **09 Mobile** | O erro do toque duplo, que pula a pergunta do tamanho. | Com a tela única, o erro some do caminho principal. É mais um motivo para não fazer perguntas em sequência que avançam sozinhas. |
| **07 Visual** | O selo vira "● Medido · ver de onde vem", e a fonte abre no toque. | Hoje a fonte só aparece no `title=`, que não existe no celular. Junto com a minha ideia, fica "● Medido · NASA SMAP". |

## 2. Objeções concretas

| De | Ideia | Objeção |
|---|---|---|
| 05 Extensionista | 5 perguntas em sequência mais 1 condicional (8 toques) | A demo continua com cara de questionário. "Criação" não muda nenhum número, porque o motor não usa a resposta: é o mesmo erro da água. "Terra rasa/piçarra" (AD1) mexe no ZARC na véspera sem teste nos 7 municípios. E o passo 1 continua na frente. |
| 07 Visual | Uma pergunta por tela, com o toque avançando sozinho | Com a API levando cerca de 1 s, isso reproduz o pulo do toque duplo (`perguntas.js:115-120`). Trocar todo o mono por Inter em 1 h é otimista: são 74 usos, além da linha do tempo e das tabelas. A barra de abas nova reescreve a casca. E o "E se chover…" vai para o "ver mais". |
| 08 Precisão | "Seu jeito de trabalhar" (prioridade, água, máquina, raiz) no topo do passo 4 | Repete o erro de hoje: controles antes do resultado. O jurado precisa ver o R$ na 1ª tela. Mexer no `motor.py` na véspera, só se for um campo novo que não muda o plano. O "E se chover…" no "ver mais" esconde o ponto 13. |
| 09 Mobile | Os cartões das culturas e o "E se chover…" no "ver mais" do passo 5 | O passo 5 fica sem o risco à vista. A grade de 10 roças de 2027 é o melhor visual da incerteza (ponto 6). O botão "Ouvir" leva 45 min e o Android pode não ter voz pt-BR: só se sobrar tempo. |
| 03 Valor da informação | Maniva na tela única "só quando o plano tem mandioca"; prioridade como 1º controle do passo 4 | A tela precisaria do plano antes de se desenhar (mais uma chamada à API e mais estado). A prioridade no topo põe de novo um controle antes do resultado. |
| 02 Produto | Renumerar as rotas, e cada ficha abre a tela de pergunta que já existe | Renumerar quebra uns 15 links, e eles mesmos admitem. Basta mudar a entrada e a ordem das pílulas. A ficha "Planta hoje" reabre o sub-questionário de 3 telas do `hoje_ideal`, e mudar custa 2 ou 3 toques em vez de 1. |
| 06 Arquitetura | Uma entrada no histórico por tela, `ctx.editar(k)` com foco, funil de 3 pontos e abas | É escopo demais para a véspera. Com a tela única, quase tudo isso deixa de ser preciso. O passo 1 (até 1.600 px) continua antes da roça. |
| 10 Radical | Botão "Montar o meu plano · 3 toques" e barra com a faixa, "Ajustar o roçado" e abas | Pôr número no botão foi o que deu errado com "5 perguntas", e eles repetem a promessa. A barra de baixo fica lotada a 390 px. O "E se chover…" também vai para o "ver mais". |
| 01 Agricultor | Tela "Afinar o plano" separada | É mais uma rota para fazer e testar. Os ajustes já cabem nos cartões, onde mudam algo. |
| 04 Júri (a minha) | Rota nova `ciencia.js`; terra no passo 3 | Retiro as duas (ver a seção 5). |

## 3. Votos

| Item | Voto | Para onde |
|---|---|---|
| hoje.culturas | **manter** | "Sua roça", linha 1. Chips com milho e feijão marcados; a % fica em "ajustar quanto de cada", fechado (padrão: igual) |
| hoje.arranjo | **mover** | Passo 4, chip do cartão Hoje: "tudo junto · mudar" |
| hoje.manejo | **inferir** | Padrões: 1ª chuva; semente pelo Censo (73,5%); queima "não sei". Os conselhos vão para todos em "O que fazer agora". Sai o "Só o que muda a conta" |
| hist.anos | **inferir** | 2026 vem do jeito de hoje; 2025 fica igual, com selo SUPOSIÇÃO. No cartão do giro, à vista: "Em 2025 também foi milho e feijão? Sim / Não", com frase condicional |
| hist.deu | **mover** | Passo 5, "A sua memória": "O IBGE anotou os piores anos. Bate com a sua roça?", com toque no ano. "Deu bem" sai |
| hist.faz | **fundir** | O preparo vai para o custo ("Paga trator ou adubo?"). Palhada, esterco e faixas saem. Fogo e semente já estão no manejo |
| terra | **manter** | "Sua roça", linha 3: Areia · Misturada · Barro · Não sei, com a dica do torrão. No passo 3, o chip "terra" fica ao lado de "Suas datas" e as datas mudam na hora |
| ha | **manter** | "Sua roça", linha 2, já preenchida: "1 ha · típico daqui (Censo 2017)", chips ½ · 1 · 2 · 3 · 5 e "outra medida" (`area.js`, com tarefas) |
| baixio | **manter** | "Sua roça", linha 4: Não tenho · Tenho · Não sei, com o mini-roçado. O tamanho fica em ⅓ e se ajusta no desenho |
| agua | **mover** | "Leve para o técnico", chip opcional (barreiro, poço, irrigo; sem "cisterna de beber"). Quem irriga lê "estas datas são para roça de sequeiro". Sai da ficha |
| maniva | **inferir** | Mandioca marcada vale "já plantada"; sem mandioca, vale "consigo". Na Parte A do plano: "Sem maniva? Trocar" |
| bolso.prioridade | **fundir** | Um seletor só, logo abaixo das barras, abrindo "Outros jeitos de girar". No El Niño, o padrão é "garantir" |
| bolso.raiz | **mover** | Passo 4, "Ajustar a conta" (fechado) |
| bolso.custo | **fundir** | Junto com o preparo: "Paga trator ou adubo? Não / Sim", em "Ajustar a conta" |
| bolso.gs | **cortar** | Vira um chip calculado pela área no passo 5 e no técnico: "Garantia-Safra: até 5 ha, você cabe" |

## 4. Fluxo preferido: o 01, com emendas

**Base do 01:**
- O painel leva direto a `#/<cod>/2`.
- "Sua roça" é uma tela só, com 4 linhas pré-marcadas: o que planta, tamanho, terra e baixio.
- Os números das rotas ficam iguais.
- O passo 1 sai do caminho principal.

**Emendas:**
- **(a) Do 02 (um fio só).** Um único botão verde por tela, na barra de baixo. As pílulas ficam sem número, na ordem **Sua roça · Plano · Rende · Se secar · Os dados**. Saem os CTAs repetidos, o "Pular" e o "Pronto". A ficha do topo fica numa linha só ("1 ha · milho + feijão · baixio · mudar"), sem "não sei".
- **(b) Minha.** "Os dados" (a rota 1, hoje `lugar.js`) recebe o que eu queria numa página nova:
  - os 7 jeitos testados, com o acerto em 100 (`metodos`, exportado de `seguranca.js`);
  - a grade comum dos satélites (harmonização);
  - satélite × pluviômetro, confiança e glossário.

  Os pontos 2, 3, 4, 6 e 7 ficam num lugar só, sem rota nova.
- **(c) Minha.** O selo passa a nomear a missão: "● Medido · NASA SMAP", "● Projeção · NOAA" (`comum.js:24-27`, até 10 caracteres). Em "Sua roça" entra uma faixa de 1 linha: "2027: El Niño forte (NOAA) · solo hoje (NASA SMAP)". Assim, quem entra por um link direto, sem o globo, também vê o porquê e a NASA.
- **(d) Do 08.** Entram as correções de números da seção 1, antes de gravar o vídeo.
- **(e) Do 06.** Todo "mudar" leva à "Sua roça" com a linha certa em destaque, e o botão vira "Voltar ao <passo>".
- **(f) Minha.** No passo 5, a ordem fica assim:
  1. a manchete;
  2. o controle "E se chover…", à vista;
  3. a cultura de 2027 numa linha, com a grade de 10 roças (2028 e 2029 a 1 toque);
  4. os portões de 19/mar e 30/abr;
  5. "Leve para o técnico" (WhatsApp);
  6. a memória.
- **(g) Contra o 01.** Não haverá tela "Afinar". Cada ajuste fica no cartão onde age:
  - arranjo no Hoje;
  - maniva na Parte A;
  - 2025 no giro;
  - quebra na memória;
  - raiz e custo em "Ajustar a conta";
  - água no técnico.
- **(h) Do 09.** Cada passo de resultado tem no máximo 1.900 px e 150 palavras à vista, e entra o link "Internet fraca?".

**Toques:** do painel ao plano são 2 ("Montar o plano" e "Ver o meu plano"). Do globo são 3. Hoje são 15.

**Roteiro de demo (2 min):**

| Tempo | Tela | O que mostrar |
|---|---|---|
| 20 s | Globo e painel | Mergulho até Quixadá e a frase "El Niño: chuva fraca em 7 de 10 municípios do CE" (NASA GPM IMERG) |
| 10 s | Sua roça | "O típico do Censo já vem marcado", 1 toque |
| 25 s | Plano | O roçado gira 2027 → 2029. Toco em "barro" e as datas mudam |
| 20 s | Rende | Hoje → Melhor → Ideal. Toco em "Garantir comida" e o jeito muda |
| 25 s | Se secar | Arrasto a chuva para 60%: "5 em 10 roças de milho quebram". "Bate com a sua roça?" e "Leve para o técnico" |
| 20 s | Os dados | Os 7 métodos com o acerto, a grade dos satélites e o satélite × pluviômetro |

**Vídeo (30 s):** globo → Quixadá → "2027: El Niño" → 1 toque → roçado girando → barras de R$ → controle da chuva.

**Divisão em 4–6 h, um dono por arquivo:**

| Agente | Arquivos | O que faz | Tempo |
|---|---|---|---|
| A | `roca.js`, `roca.html`, `comum.js`, links do globo | Entrada, pílulas, botão único, ficha, "mudar" com volta, selo com a missão | ≈ 1,5 h |
| B | `perguntas.js` e css | Tela única, reaproveitando `opcao()`, `AREA.render`, o mini-roçado e a grade de culturas do `hoje_ideal` | ≈ 1,5–2 h |
| C | `plantio.js`, `lugar.js` | Agenda no alto, "ver mais", giro com "2025 igual?", maniva na Parte A; "Os dados" com `metodos` | ≈ 1,5 h |
| D | `dinheiro.js`, `seguranca.js` | Barras primeiro, um seletor, "Ajustar a conta", sem o `heroiHtml` repetido, chip da GS; nova ordem do passo 5 e correções de texto | ≈ 1,5 h |

**Conferência (≈ 0,5 h):**
- `percorrer_fluxo.py` nos 7 municípios;
- os mesmos R$ com a mesma URL;
- nada rola de lado a 390 px.

## 5. Onde mudei de ideia

1. **O passo 1 sai da frente.** Antes eu o mantinha encurtado. Mudei porque o globo e o painel já fazem a abertura "do espaço" com NASA escrita, e o passo 1 repete o El Niño, o que custa 15 s numa demo de 2 min. A minha página "Como o QUADRA sabe" se funde com ele em "Os dados", e isso dá **menos** trabalho, porque não precisa de rota nem de `ciencia.js`. Para o júri não perder a NASA, entram o selo com a missão e a faixa de 1 linha.
2. **A terra volta para "Sua roça".** Antes eu a levava ao passo 3. O 08 mostrou que o "não sei" é a interseção dos solos zoneados (`motor.py:674-678`), e a terra é a resposta que mais mexe no JSON (`textura=3`: 77 campos). Deixá-la em "não sei" por padrão piora a precisão justamente para quem não rola a tela. O momento de demo continua: o chip da terra ao lado de "Suas datas".
3. **Maniva "já plantada" muda o plano.** Eu tinha escrito que não mudava. A API mostra que muda as faixas e as notas (9 campos). O voto continua "inferir", agora sabendo que a inferência tem efeito e por isso precisa do "mudar" à vista.
4. **A prioridade passa de "mover" para "fundir".** O 01 mostrou que existem dois seletores da mesma coisa no passo 4.

## 6. Linhas vermelhas

1. **Os três pedidos do José ficam à vista no caminho principal.** O jeito de hoje é a linha 1 de "Sua roça" e o Hoje das barras. A área é a linha 2. O histórico tem 1 toque visível no Plano (2025) e em Se secar (a quebra). Nada disso pode ficar só atrás de "Afinar".
2. **Terra e baixio são perguntados antes do plano.** São as respostas que mudam datas e faixas.
3. **Hoje → Melhor → Ideal fica na 1ª tela de Rende**, sem nenhum controle antes.
4. **Todo número leva selo MEDIDO, SUPOSIÇÃO ou PROJEÇÃO, com a fonte legível no toque.** A palavra NASA aparece dentro da jornada.
5. **Nenhuma promessa falsa na tela.** Saem "5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde" e o "+R$ 909 do baixio". Nenhum botão leva número de toques ou de perguntas. Pergunta que não muda nada só existe se disser que é "para o técnico".
6. **Os 16 pontos continuam a 1 toque.** "Os dados" fica sempre visível na barra (pontos 2, 3, 4, 6 e 7). Em Se secar, o "E se chover…" e a grade de 10 roças de 2027 ficam à vista, fora do "ver mais".
7. **Ponto 16 na 1ª tela de Se secar:** a frase "quem decide é você, com o técnico" e "Leve para o técnico" (WhatsApp).
8. **Um botão verde por tela, e "mudar" volta ao passo de origem.**
9. **Segurança da entrega:**
   - não mexer em `servidor.py`;
   - `motor.py` só com campo novo, testado;
   - as chaves do `PADRAO` e os números de rota ficam iguais;
   - o `percorrer_fluxo.py` passa nos 7 municípios, com os mesmos R$ para a mesma URL, antes de gravar o vídeo.
