# 06 · Arquitetura de informação e navegação

Lente: estrutura de passos, progresso, botões, voltar, hash e onde cada conteúdo mora.
Base: prints e textos de `E:/campeonato-nasa/tmp/fluxo_atual/` (Quixadá, 390 px), leitura de `roca.js`, `roca.html`, `comum.js`,
`passos/*.js`, `extras/hoje_ideal.js`, `extras/historico.js`, `extras/area.js` e a API com e sem cada resposta
(`/api/local?cod=2311306` com `textura`, `baixio`, `ad_baixio` e `maniva`).

## Resumo em 3 linhas

1. Hoje o plano aparece depois de **14 toques e 11 telas de pergunta**. Proposta: **3 toques** a partir do globo, com só 2 telas antes do plano.
2. Hoje o passo 2 tem **3 contadores diferentes** ("1 de 3", "1 de 3", "pergunta 1 de 5"). A tela tem 2 botões verdes de avançar e 2 de voltar, e o voltar do Android sai do passo.
   Proposta: **uma ação por tela, na barra de baixo**, e cada tela vira uma entrada no histórico.
3. Hoje cada "mudar" leva de volta à 1ª das 11 telas. Proposta: **"mudar" abre a pergunta certa e volta à tela de onde a pessoa saiu**.
   E **cada dado mora num só lugar**: o El Niño aparece nos passos 1, 4 e 5, e o Hoje/Melhor/Ideal aparece 2 vezes no passo 4.

---

## 1. Diagnóstico (com evidência)

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| D1 | O botão promete **5 perguntas**, mas são **11 telas** e mais o resumo. | `passos/lugar.js:148` "Responder 5 perguntas sobre a sua roça". O passo 2 junta 3 (hoje) + 3 (histórico) + 5 perguntas + o resumo (`perguntas.js:11`, fases hoje → historico → perguntas). Prints `02`–`13`. | alta |
| D2 | Há **três barras de progresso dentro do passo 2**, e todas recomeçam do 1. A pessoa vê "1 de 3", "1 de 3" e depois "pergunta 1 de 5" na **7ª tela**. Por cima de tudo fica a barra 1–5. | `hoje_ideal.js:365` ("Seu jeito de hoje · n de 3"), `historico.js:226` ("O que você já fez · n de 3"), `perguntas.js:103-104` ("Passo 2 · sua roça · pergunta n de 5"), `roca.js:107-109` (pílulas 1–5). Print `08`. | alta |
| D3 | Há **2 botões verdes de avançar na mesma tela**, com rótulos e destinos diferentes. "Próxima →" vai para a tela seguinte do quiz. "Como plantar →" pula todas as perguntas que faltam. | Print `02`: "Próxima" e, logo embaixo, "Como plantar →". Print `13`: "Ver como plantar" e "Como plantar →". O CSS esconde a barra só no `.quiz` (`css/passos/perguntas.css:73`), e não nas 6 telas do hoje e do histórico. Duplicatas também em `lugar.js:148` e `plantio.js:505`. | alta |
| D4 | **Os botões de voltar levam a lugares diferentes.** "Anterior" volta uma tela. "← Voltar" vai ao passo 1. O voltar do Android também vai ao passo 1, e ao avançar de novo o quiz recomeça na 1ª tela. | O estado do quiz fica só em variáveis do módulo (`perguntas.js:11-13`, `hoje_ideal.js:331`, `historico.js:193`), nunca no hash. As respostas usam `location.replace` (`roca.js:144`), então a única entrada no histórico é o passo. Ao entrar no passo, tudo é zerado (`perguntas.js:77`). | alta |
| D5 | **"Mudar" leva ao início do questionário.** O toque em "Terra: não sei" na ficha (passos 3–5), o "Mudar" do passo 3, o "Contar" do giro e o "Contar o meu ano ruim" do passo 5 abrem "Como você planta hoje? 1 de 3". Para chegar à terra são mais 6 telas, e depois não há caminho de volta ao passo de onde a pessoa saiu. | `roca.js:113` (`data-ir="2"`), `plantio.js:71`, `historico.js:361` e `:377/420` (`ctx.link(2)`), `dinheiro.js:128`. Todos caem no zeramento de `perguntas.js:77`. | alta |
| D6 | **Há perguntas que não mudam nada.** "Que água você tem?" diz "muda o que dá para salvar", mas não vai para o núcleo nem para a conta: só vira uma linha do "Leve para o técnico". "E na hora de plantar? Só o que muda a conta" não muda nenhum R$, só frases. "Deu bem" e "Como você prepara a terra" só viram ficha no resumo. | `perguntas.js:30`. `roca.js:44-51` (`paramsApi` não tem `agua`). `leve_ao_tecnico.js:67-68` é o único uso. `hoje_ideal.js:402`, com uso só em alertas e textos (`:178-179`, `:291-298`). `historico.js:286` (`bem`) e `:289` (`roca`) só aparecem no resumo. A Garantia-Safra não entra na conta (`dinheiro.js:129`, title). | alta |
| D7 | **A ordem das perguntas vai contra as dependências.** A 1ª tela fala "no seu roçado de 1,0 ha", mas o tamanho só é perguntado na 9ª. "Milho no baixio" vem na 2ª tela, mas o baixio só é perguntado na 10ª. | Prints `02` e `03` contra `09` e `10`. `hoje_ideal.js:383` e `:387`. | média |
| D8 | **Há perguntas repetidas entre módulos.** "Queimo / Não queimo" e "Guardo semente" estão no "jeito de hoje" e de novo no "o que você já faz". O código tenta esconder isso e escreve "Já anotado no seu jeito de hoje". O tamanho e o baixio voltam a ser perguntados no passo 3 ("Mudar") e no passo 4 (chip "1,0 ha · 0,3 ha de baixio? · mudar"). | `historico.js:269-271`. Print `07`. `plantio.js:71`, `dinheiro.js:128`. | média |
| D9 | **El Niño em 4 lugares, com números diferentes.** O painel do globo mostra o ONI. O passo 1 diz "7 de cada 10 municípios do Ceará". O passo 4 mostra "Se 2027 for como… 1998/2010/2016/2024". O passo 5 diz "2 de 3 anos de mar assim trouxeram estação seca" e mostra de novo as barras dos 4 anos em cada cultura. | Contagem nos TXT: El Niño ou "mar assim" aparece 6× no passo 1, 8× no 4 e 8× no 5. `rocacerta.js:169-176`. | média |
| D10 | **O passo 4 mostra o mesmo resultado 2 vezes.** O bloco Hoje/Melhor/Ideal (R$ 2.480 / 984, R$ 4.360 / 2.760) é repetido logo abaixo no herói "No caso ruim… O plano R$ 2.760 / Jeito de hoje R$ 984". Antes do resultado ainda vêm 4 controles ("Seu bolso"). | Print `15`, linhas 39–47 contra 95–97 do TXT. `dinheiro.js:84` (bolso + hi-slot + heroi). | média |
| D11 | **As páginas de resultado são enormes.** Passo 1: 4.550 px. Passo 3: 5.625. Passo 4: 6.629. Passo 5: 6.377. Somam cerca de 23.000 px, perto de 29 telas de celular. O passo 5 tem 11 "Ver …" e 15 selos. A régua da chuva repete os indicadores "A chuva chega" e "Meses de chuva" (18/01, jan–abr). | Cabeçalho dos TXT. Print `01`. | média |
| D12 | **O fim da jornada não leva a uma ação.** No passo 5, o botão principal é "Outro lugar →", que volta ao globo. O que o ponto 16 pede é levar o plano ao técnico. | `roca.js:121` e `:227`. | média |
| D13 | **Um padrão vira resposta sem a pessoa tocar.** Basta apertar "Próxima" na 1ª tela para o hash gravar `hoje=milho:50,feijao:50\|cons=1\|1chuva=1\|sem=1`. A partir daí o passo 4 trata como informado o que é só o padrão. | URL do print `03`. `hoje_ideal.js:442` (`gravar()` ao avançar). | baixa |
| D14 | **Os nomes dos passos 3–5 não aparecem no celular.** A fileira mostra "✓ — 2 Sua roça — 3 — 4 — 5" e rola de lado. | `roca.js:114-116`. Print `02` (topo). | baixa |

### O que cada resposta muda de verdade (Quixadá, medido na API)

| Resposta | Muda o plano (faixas) | Muda datas | Muda R$ | Onde é usada |
|---|---|---|---|---|
| `maniva=nao` | **sim**: as Partes A e C trocam mandioca por sorgo | não | sim | núcleo e passos 3, 4 e 5 |
| `baixio=0` | **sim**: some a parte Baixio | não | sim | núcleo e passos 3, 4 e 5 |
| `ha` | não (muda a escala) | não | **sim** | passos 3 e 4 |
| `terra` (textura) | não | **sim**: milho de 21/02–28/02 para 11/02–10/03 (terra misturada); arenosa tira o feijão comum | pouco | agenda e "Suas datas" |
| `hoje.culturas` | não | não | **sim** (coluna Hoje) | passo 4 e giro |
| `hoje.arranjo` | não | não | sim ("milho só no baixio") | passo 4 |
| `hoje.manejo` | não | não | **não** | só frases |
| `hist.anos` | não | não | não | cartão do giro (passo 3) |
| `hist.deu` | não | não | não | memória (passo 5); "bem" não é usado |
| `hist.faz` + preparo | não | não | não | só a ficha |
| `agua` | não | não | não | 1 linha do técnico |
| `bolso.*` | não | não | sim (`raiz`, `custo`) | passo 4 |

---

## 2. Decisão por item perguntado

| Item | Decisão | Para onde | Motivo |
|---|---|---|---|
| `hoje.culturas` | **manter** (e fundir) | Tela única "Sua roça", 1º bloco: só os chips de cultura, com milho + feijão já marcados. A divisão em % vai para o passo 4. | É o pedido do José e alimenta a coluna Hoje. Sem a %, não depende do tamanho, que ainda não foi perguntado (D7). |
| `hoje.arranjo` | **mover** | Passo 4, chip do cartão "Hoje" ("tudo junto · mudar"), que abre as 3 opções ali mesmo. Padrão: tudo junto. | Só pesa na conta do Hoje, e "milho no baixio" depende da resposta do baixio, que já foi dada antes do passo 4. |
| `hoje.manejo` | **inferir** | 1ª chuva = o mais comum. Semente pelo Censo (`pct_semente_milho` 73,5% guarda). A queima não é perguntada, porque o plano já diz "sem fogo" a todos (`agenda.agora`). | Não muda R$ (D6), e a tela promete "Só o que muda a conta". |
| `hist.anos` | **inferir** | 2026 = jeito de hoje; 2025 = igual (o padrão que o módulo já usa). O cartão "Por onde começar o seu giro" (passo 3) diz "Se você repetiu milho…" e tem 1 toque para "Em 2025 foi diferente". | Só serve ao cartão do giro, e o caso comum no semiárido é repetir milho + feijão. |
| `hist.deu` | **mover** | Passo 5, "A sua memória e os dados". O "Contar o meu ano ruim" abre as culturas e o ano **ali mesmo**, sem ir ao passo 2. O "deu bem" sai. | A quebra é a âncora da memória (ponto 16). O "deu bem" não é lido por ninguém (`historico.js:286`). |
| `hist.faz` | **cortar** | "Não queimo" e "Semente" já são inferidos. "Planto em faixas", "palhada" e "esterco" não mudam nada. O preparo (trator, animal, enxada) vai para `bolso.custo`. | Só vira ficha no resumo (D6). Repete o manejo (D8). |
| `terra` | **manter** | Tela única, 5º bloco, com "Não sei" marcado e o "seu olho" do torrão. | É a única resposta que muda as datas (ZARC por solo). Num toque, com padrão. |
| `ha` | **manter** | Tela única, 2º bloco. Chips ½, 1, 2, 3 e 5 ha com o do Censo marcado ("1 ha · comum daqui"). Tarefas ou medida do terreno abrem o `area.js` num "outra medida". | Muda a escala do desenho e todo o R$. |
| `baixio` | **manter** | Tela única, 3º bloco, com "Não sei" marcado (tracejado). | Muda o plano: a parte Baixio aparece ou some. |
| `agua` | **inferir** | Padrão "só a chuva" (Censo: 2,8% irrigam). Quem tem poço ou barreiro marca num chip opcional do "Leve para o técnico" (passo 5), onde a resposta vira pergunta ao técnico. | Promete "muda o que dá para salvar" e não muda (D6). O ponto 15 (água) fica coberto pelo chip e pelo jeito "Guardar água" dos cenários. |
| `maniva` | **manter** | Tela única, 4º bloco, com "Consigo maniva" marcado. | É a resposta que mais mexe no plano: sem maniva, a rotação inteira muda. |
| `bolso.prioridade` | **mover** | Passo 4: vira o seletor do bloco "Outros jeitos de girar o roçado" ("O que vale mais para você?"). Padrão: garantir, em ano de El Niño. | Ali ele acende o jeito escolhido (ponto 9). No topo do passo 4 é mais uma pergunta antes do resultado. |
| `bolso.raiz` | **opcional** | Passo 4, "Ajustar a conta" (fechado), junto com o "seu olho" da casa de farinha. Padrão: a mediana do estado. | Só vale com mandioca no plano e mexe pouco. |
| `bolso.custo` | **fundir** | Com o preparo da terra: "Como você prepara a terra? Enxada / Animal / Trator". Trator = máquina e insumos; os outros = só a semente. Fica em "Ajustar a conta". | Uma pergunta concreta no lugar de uma abstrata. O preparo, que hoje não serve para nada, passa a mudar a conta (ponto 15: equipamento). |
| `bolso.gs` | **cortar** | Vira chip informativo no passo 5: "Garantia-Safra: você cabe (até 5 ha)", calculado pelo `ha`, junto ao "Leve para o técnico". | O valor não entra na conta (`dinheiro.js:129`). |

Ficam 5 perguntas no funil, todas com padrão marcado, e mais 4 opcionais nos lugares onde agem.

---

## 3. Fluxo proposto, tela a tela

```
Globo → [1 O lugar] → [2 Sua roça] → PLANO: [Plantar | Rende | Seca]
         funil com 3 pontos              abas, sem contador
```

| Tela (hash) | Objetivo | Conteúdo (visível) | Ação (barra de baixo, a única) |
|---|---|---|---|
| **0 · Globo** (`index.html`) | Achar o município e ver o "da órbita ao campo" | Sem mudança: mergulho, mapa com camadas, painel Roça Certa | "Montar o plano do meu roçado" → `#/<cod>/1` |
| **1 · O lugar** (`#/cod/1`), meta ≤ 1.600 px | Em 10 s: por que 2027 pede cuidado e de onde vêm os dados | Kicker "Visto do espaço". h1 "Quixadá, CE. **2027 é ano de El Niño forte.**". Os 4 indicadores (mar, chuva chega, meses de chuva, solo hoje), com selo. Uma linha "**11 culturas** servem aqui" com os 6 ícones recomendados. Chip "Confiança dos dados: alta · por quê". **Fechados:** "Como o lugar está mudando" (tendências), "O ano da chuva" (régua + satélite × pluviômetro), "Os anos de El Niño" (barras), "Todas as culturas" (cardápio + tabela), "De onde vêm os dados", glossário | ← Mapa · **Montar o meu plano →** |
| **2 · Sua roça** (`#/cod/2`), meta ≤ 1.800 px | Personalizar numa tela só, tudo opcional | h1 "Conte da sua roça.", eco "Já marcamos o comum daqui. Mude o que for diferente." Cinco blocos com rótulo e uma fileira de botões grandes com ícone; o padrão marcado com a etiqueta "comum daqui": (1) **O que planta hoje** (vários), (2) **Tamanho** (½, 1, 2, 3, 5 ha + "outra medida"), (3) **Baixio**, (4) **Maniva**, (5) **Terra na chuva forte** + seu olho. Cada toque grava (`replace`) e não avança sozinho. **Sem resumo "Pronto."** | ← O lugar · **Ver o meu plano →** (ou "Voltar a Rende →", quando a pessoa veio de um "mudar") |
| **3 · Plantar** (`#/cod/3`), meta ≤ 2.500 px | O quê, onde e quando | Abas no topo. **Ficha** (chips das respostas; o toque edita). h1 "Plante em faixas.". Roçado visto de cima (herói). **O que fazer agora** (os 3 próximos marcos; o calendário completo fica fechado). "Por onde começar o seu giro" (se houver recomendação). **"Por que este plano"**: 3 sanfonas fechadas, cada uma com manchete de 1 linha: Onde o roçado sofre (vulnerabilidade), Faixas seguram praga, O que cada planta faz pelo solo | Ajustar · **Quanto rende →** |
| **4 · Rende** (`#/cod/4`), meta ≤ 2.500 px | Vale a pena? | h1 + **Hoje → Melhor → Ideal como herói**, com o chip "Hoje: milho + feijão, tudo junto · mudar" (abre % e arranjo ali). "O que vale mais para você?" + Outros jeitos (cenários). **Fechados:** Quando o dinheiro entra, Se 2027 for como os El Niños, A colheita paga o gasto?, Ajustar a conta (raiz, preparo), Como calculamos. **Sai** o herói "No caso ruim…" (duplicado) | ← Plantar · **Se der seca →** |
| **5 · Seca** (`#/cod/5`), meta ≤ 2.500 px | O que pode dar errado e quando decidir | h1 "2027 tende a ser apertado.". **E se chover…** (controle, aberto na chuva dos El Niños daqui). **O que vamos olhar: 19/mar e 30/abr** (portões). Cada cultura: **só 2027** ("quebra em 6 de 10", "pelo menos 3 sacos"); 2028–29 ficam fechados. "A sua memória e os dados" + "Contar o meu ano ruim" (ali mesmo). **Leve para o técnico**, com os chips opcionais de água e Garantia-Safra | ← Rende · **Mandar para o técnico** (copia para o WhatsApp; "Imprimir" e "Outro lugar" ficam como links) |

### Regras de navegação

1. **Uma ação primária por tela, sempre na barra de baixo.** Nenhum "avançar" dentro do conteúdo: saem `lugar.js:148-149`, o CTA do resumo e `plantio.js:505`. A frase do ponto 16 continua na barra.
2. **Voltar = a tela anterior**, igual ao voltar do Android. Cada tela é uma entrada no histórico (`location.hash =`), e as respostas usam `location.replace`, como já fazem. Sem estado de navegação em variável de módulo: recarregar a página abre a mesma tela.
3. **Progresso só no funil:** "1 O lugar · 2 Sua roça · 3 Plano" (3 pontos, com rótulos). No plano, **abas** "Plantar · Rende · Seca", sem ✓ e sem números. Sem "n de 3" nem "pergunta n de 5".
4. **Toda pergunta tem padrão marcado e é opcional.** Só um toque explícito vai para o hash; apertar "avançar" não grava o padrão (corrige D13). Os selos continuam dizendo "padrão daqui (Censo 2017)".
5. **"Mudar" leva à pergunta certa e volta à tela de origem.** Um novo `ctx.editar(chave)` em `roca.js` guarda `volta = passo atual` e `foco = chave` e vai ao `#/cod/2`. Lá a tela rola até o bloco, destaca a pergunta, e o botão de baixo vira "Voltar a <passo>". As respostas ficam todas num lugar só, a ficha do topo das abas. Saem os "Mudar" soltos (`plantio.js:71`, `dinheiro.js:128`).
6. **Um fato, um lugar.** El Niño: a manchete no passo 1 e o detalhe no passo 5 ("E se chover"). No passo 4, "Se 2027 for como…" fica fechado. Sai o "Hoje: 2 de 3 anos de mar assim" do passo 5 (é o mesmo fato com outro número). Hoje/Melhor/Ideal só no 4. Datas só no 3. Garantia-Safra só no 5.
7. **No máximo 3 blocos visíveis por tela e 1 "seu olho" por bloco.** Método, fonte, tabela e "por quê" vão para `verMais`, fechado.

---

## 4. O que muda nos passos 1, 3, 4, 5 e no globo

| Onde | O quê | Decisão | Motivo |
|---|---|---|---|
| Globo / painel | Botão "Montar o plano do meu roçado" | Sem mudança (continua indo ao `#/cod/1`) | O painel já mostra El Niño e chuva, e o passo 1 curto completa sem repetir. |
| Passo 1 | Gráfico de barras do El Niño (4 anos) + detalhes | Mover para "ver mais" ("Os anos de El Niño") | Os mesmos 4 anos voltam nos passos 4 e 5 (D9). |
| Passo 1 | Régua "O ano da chuva" + satélite × pluviômetro | Mover para "ver mais" | Repete os indicadores "A chuva chega" e "Meses de chuva" (D11). |
| Passo 1 | Tendências (6 cartões) | Mover para "ver mais" ("Como o lugar está mudando") | Pontos 1 e 11 ficam cobertos, e também nas camadas do globo (calor e água com controle de tempo). |
| Passo 1 | Cardápio de 18 culturas | Juntar numa linha "11 culturas servem aqui" com os 6 ícones recomendados; o resto vai para "ver mais" | O plano do passo 3 já escolhe por ele. |
| Passo 1 | Confiança dos dados | Juntar num chip "Confiança: alta · por quê" | Ponto 6 com 1 linha visível. |
| Passo 1 | "Responder 5 perguntas" e "Pular…" | Cortar | Duplicam a barra de baixo, e o "5" é falso (D1, D3). |
| Passo 2 | Hoje (3 telas) + histórico (3) + 5 perguntas + resumo | Juntar numa tela só, com 5 blocos (ver seção 2) | D1, D2, D4, D7, D8. |
| Passo 3 | "Seu roçado de 1 ha… Mudar" | Cortar (a ficha faz isso) | D8. |
| Passo 3 | Ordem: herói → giro → vulnerabilidade → o que fazer → faixas → solo | Nova ordem: herói → **o que fazer agora** → giro → "Por que este plano" (vulnerabilidade, faixas e solo em 3 sanfonas) | O agricultor quer "o que faço agora". Os pontos 8, 10 e 12 ficam com manchete visível. |
| Passo 3 | Pergunta do declive ("mais plano / típico / mais inclinado") dentro da vulnerabilidade | Manter, dentro da sanfona | Só faz sentido ao lado do desenho da erosão. |
| Passo 3 | "Ver quanto rende" (CTA no conteúdo) | Cortar | Duplica a barra (D3). |
| Passo 4 | "Seu bolso" no topo (4 controles) | Mover: prioridade → seletor dos cenários; raiz e custo (+ preparo) → "Ajustar a conta" (fechado); Garantia-Safra → passo 5 | Resultado primeiro (D10). |
| Passo 4 | Hoje → Melhor → Ideal | Vira o **herói**; o chip "Hoje · mudar" abre % e arranjo ali mesmo (telas 0 e 1 do `hoje_ideal` num `details`) | É o pedido do José e a resposta a "vale a pena?". |
| Passo 4 | Herói "No caso ruim… plano × hoje" | Cortar; "Ver os 28 anos" passa para "Como calculamos" | São os mesmos números do Hoje/Melhor/Ideal (D10). |
| Passo 4 | "Se 2027 for como…", "Quando o dinheiro entra", "A colheita paga o gasto?" | Mover para "ver mais" (3 sanfonas) | Detalhe. O herói já diz "2027 é o mais apertado". |
| Passo 5 | "Hoje: 2 de 3 anos de mar assim…" + "Ainda não sabemos" | Cortar o número. "Ainda não sabemos: o Atlântico, a chuva, o preço" vira 1 linha sob o h1 | D9. O ponto 6 continua visível. |
| Passo 5 | "E se chover…" | Subir para logo depois do h1 | É o bloco mais intuitivo (ponto 13) e responde à pergunta do passo. |
| Passo 5 | Cartões por cultura (3 culturas × 3 anos) | Mostrar só 2027; 2028 e 2029 ficam em "ver mais" | Corta cerca de 2/3 da altura sem perder a projeção. |
| Passo 5 | "Contar o meu ano ruim" | Abrir as culturas e o ano ali mesmo (sem ir ao passo 2) | D5. |
| Passo 5 | Botão final "Outro lugar →" | Trocar por "Mandar para o técnico" (WhatsApp); "Outro lugar" vira link | D12, ponto 16. |
| Casca (`roca.js`) | Pílulas 1–5 | Funil com 3 pontos (passos 1–2) e abas Plantar · Rende · Seca (3–5) | D2, D14. |

---

## 5. Toques até ver o plano

- **Hoje:** 14 toques. Montar → Sua roça → Próxima → arranjo → Pronto → Próxima → Próxima → Pronto → terra → Próxima → baixio → água → maniva → Ver como plantar. A outra saída é o link "Pular…", no fim de 4.550 px de rolagem. Antes do plano a pessoa passa por 11 telas de pergunta e mais o resumo.
- **Proposto: 3 toques** ("Montar o plano" no globo → "Montar o meu plano" → "Ver o meu plano"). Antes do plano há só 2 telas, e quem quiser responde tudo na tela 2 sem trocar de tela.

---

## 6. Riscos

1. **Perder a sensação de conversa que o José pediu** ("entender o que ele já faz"). Para reduzir: "O que planta hoje" abre a tela 2. O Hoje/Melhor/Ideal vira o herói do passo 4. A memória das quebras fica no passo 5, com o IBGE ao lado.
2. **A tela única pode parecer formulário.** Para reduzir: botões grandes com ícone (os mesmos de hoje), sem campo de texto, o padrão marcado com a etiqueta "comum daqui" e o botão de baixo sempre visível.
3. **A inferência "2025 = igual a 2026"** dispara "A terra repetiu milho" para quem girou. Para reduzir: frase condicional ("Se você repetiu…") e 1 toque para "Em 2025 foi diferente".
4. **Ver mais demais esconde pontos do desafio do júri** (pontos 1, 8, 10, 11, 12). Para reduzir: cada sanfona tem manchete de 1 linha visível, e o roteiro da demo abre uma por passo.
5. **O ponto 15** (água, equipamento, mercado) precisa continuar editável. Água: chip do técnico. Equipamento: preparo → custo. Mercado: raiz e "Vender mais". Conferir antes de entregar.
6. **O "volta" fica numa variável de `roca.js`.** Se a pessoa recarregar no meio, o botão de baixo cai no padrão "Ver o meu plano" (passo 3). É aceitável.
7. **Quebra o script de teste** `testes/ferramentas/percorrer_fluxo.py`, que clica as 11 telas, e os links antigos com `#/cod/2` no meio do quiz, que passam a abrir a tela única. Os dois precisam ser atualizados e os prints refeitos a 390 px.
8. **Conflito de edição.** `roca.js`, `perguntas.js` e `dinheiro.js` são mexidos por mais de uma ideia. É preciso 1 dono por arquivo.

---

## 7. As 3 ideias mais importantes

1. **Resultado primeiro.** O funil fica com 2 telas: o lugar curto e "Sua roça" numa tela só, com os padrões do Censo marcados. O plano aparece no 3º toque. Toda outra pergunta mora onde ela muda algo: Hoje e arranjo no passo 4, a quebra no passo 5, raiz e custo em "Ajustar a conta". O que não muda nada sai.
2. **Uma navegação só.** A barra de baixo tem o único avançar e o único voltar, cada tela é uma entrada no histórico (o voltar do Android funciona) e nada de estado de tela fica fora do hash. O funil mostra 3 pontos, o plano mostra 3 abas, e somem as barras "n de 3" aninhadas.
3. **Um fato, um lugar, e "mudar" no lugar.** El Niño com a manchete no 1 e o detalhe no 5. Hoje/Melhor/Ideal uma vez só, como herói do 4. As respostas aparecem só na ficha. Todo "mudar" abre a pergunta certa e devolve a pessoa à tela de onde ela veio.

---

## Plano de implementação (cerca de 5 h de trabalho, 3 donos em paralelo, cerca de 2 h de relógio)

| Dono | Arquivos | Tarefa | Tempo |
|---|---|---|---|
| A | `roca.js`, `roca.html`, `css/quadra.css` | Casca: funil com 3 pontos e abas; ficha só nas abas, com `data-editar`; `ctx.editar(k)` com `volta` e `foco`; rótulos da barra de baixo; passo 5 → "Mandar para o técnico" (chama o copiar do `leve_ao_tecnico`); Voltar = passo anterior | 1 h |
| A | `passos/perguntas.js`, `css/passos/perguntas.css` | Tela única com 5 blocos (reaproveita `PERG`, as culturas de `hoje_ideal` exportadas e `AREA.render` em "outra medida"); sem `fase`, `q` nem resumo; rola até `ctx.foco` | 1 h 30 |
| B | `passos/lugar.js`, `passos/plantio.js`, `extras/historico.js` | Passo 1 em ≤ 1.600 px (blocos para `verMais`); passo 3 na nova ordem com 3 sanfonas, sem CTA nem "Mudar"; inferência do histórico (2026 = hoje, 2025 = igual) + toque "Em 2025 foi diferente"; "Contar o meu ano ruim" ali mesmo | 1 h 30 |
| C | `passos/dinheiro.js`, `passos/seguranca.js`, `extras/leve_ao_tecnico.js` | Passo 4: Hoje/Melhor/Ideal como herói, sai o herói duplicado, bolso para "Ajustar a conta", prioridade nos cenários, preparo → custo. Passo 5: "E se chover" em cima, só 2027 por cultura, sai o "2 de 3", chips de água e Garantia-Safra no técnico | 1 h 30 |
| Todos | `testes/ferramentas/percorrer_fluxo.py` | Novo percurso, prints a 390 px, medir as alturas contra as metas | 30 min |

Como verificar: 3 toques do globo ao passo 3. O voltar do Android, do passo 4 até o globo, passa por 4 → 3 → 2 → 1. Tocar em "Terra" na ficha do passo 4 abre o bloco da terra, e o botão de baixo leva de volta ao passo 4. As alturas a 390 px ficam dentro das metas. O plano e os R$ continuam iguais aos de hoje para as mesmas respostas, nos 7 municípios de teste.
