# Construtor B (Dinheiro): relatório

Ordem de serviço: `analise/fluxo/00_FLUXO_FINAL.md`, seção 7 (B0 a B4). Só mexi nos 6 arquivos do B:
`web/js/passos/dinheiro.js`, `web/css/passos/dinheiro.css`, `web/js/extras/hoje_ideal.js`, `web/css/extras/hoje_ideal.css`,
`web/js/extras/cenarios.js` e `web/css/extras/cenarios.css`. Não mexi em `calculo.js`, `graficos.js`, `nucleo/` nem `servidor.py`,
e não reiniciei o servidor.

## O que fiz

### B0. Export (já estava pronto)
- `hoje_ideal.js:663`: `export { CULT, igual, mexer, opcoesCultura };`.

### B1. dinheiro.js: a ordem nova
A ordem agora é: título → linha do que a conta supõe → Hoje/Melhor/Ideal → "O que vale mais para você?" → painel com "Ajustar a conta",
El Niño, caixa, "paga o gasto?" e "Ver como calculamos". Não há nenhum controle antes do gráfico.
- `dinheiro.js:93`: `abertura()` com o kicker "Quanto rende" (saiu o "Passo 4 ·"). O título é sempre "Hoje, melhor e ideal." com o eco
  "Do seu jeito ao plano completo." (`:66` e `:85`).
- `dinheiro.js:52-55`: linha de suposições usada como apoio do título:
  "Conta com: só a semente · raiz a R$ 0,84/kg (comum no CE) · ajustar", com o selo SUPOSIÇÃO.
  - O "ajustar" é um `<button data-abrir="ajustar-conta">`, e não um `<a href="#…">`, porque o hash é a rota.
  - O clique abre o `<details id="ajustar-conta">` e rola até ele (`ligar`, `:107-120`; `scroll-margin-top` em `dinheiro.css:37`).
  - O trecho da raiz só aparece quando o plano tem mandioca com série.
- `dinheiro.js:56` e `:135-154`: "Ajustar a conta" (fechado) tem três linhas e um link:
  - custo: "Só a semente" e "Semente, trator, adubo e diária" (CONAB);
  - preço da raiz, só com mandioca: daqui, comum no UF e baixo no UF, com `OLHOS.preco_raiz`;
  - "Como fica no roçado": "Tudo junto", "Em pedaços" e "Milho no baixio". A última só aparece se há milho e o baixio não é "não";
  - o link "Mudar o que planta ou quanto de cada", com `data-editar="hoje"` e o href de `ctx.link(2)` como reserva.
- `dinheiro.js:126-133` `comArranjo()`: o arranjo grava `hoje` com `escreverHoje`, mas só com as culturas, `cons`/`mbx` e as chaves que
  a pessoa já tinha. Não repete o defeito de `escreverHoje(lerHoje(""))`. Exemplo: o padrão + "Milho no baixio" grava
  `hoje=milho:50,feijao:50|cons=0|mbx=1`.
- `dinheiro.js:79-84`: os blocos de El Niño, caixa e termo foram para `U.verMais` com títulos de roça:
  "Se 2027 for como os El Niños fortes", "Quando o dinheiro entra" e "A colheita paga o gasto?".
  - Os "Ver mais" de dentro deles viraram texto direto, para não ter `<details>` dentro de `<details>`.
  - O selo foi para a legenda de cada bloco.
- `dinheiro.js:83`: "Ver como calculamos" junta três coisas:
  - o detalhe do Hoje/Melhor/Ideal (`<div class="hi-detalhes hoje-ideal">`, preenchido pelo `hoje_ideal.js` via `opcoes.detalhesEm`);
  - os 28 anos (`replayHtml`, título h4 "Os 28 anos…", `:273`);
  - o detalhe do plano (`detalhesHtml`).
- Saíram `bolsoHtml` (o seg de prioridade, o chip de área e o seg do Garantia-Safra), `heroiHtml`, `ganhaOuMotivo` e `kg`.
  - Também saíram as regras de CSS órfãs: `.bolso*`, `.gs`, `.heroi*`, `.hn*`, `.graf-h`, `.chip.grande`, `.rot-mini`, `.seg-vazio` e `.como`.
- `dinheiro.js:180`: o chip do El Niño diz "El Niño forte" (antes, "muito forte").
- `dinheiro.js:189-197` `semVendaEm`: a frase diz "a maniva ainda não colhe; o sorgo vira comida da criação (fora do R$)".
- `dinheiro.js:161`: "sem preço aqui" virou "comida da criação, fora do R$".
- `dinheiro.js:97-105` `abertosAntes`/`reabrir`: num redesenho por resposta nova (custo, raiz, arranjo, prioridade), os "ver mais" que
  estavam abertos continuam abertos. O "Ajustar a conta" não fecha embaixo do dedo e a rolagem não pula (medido: scroll 1565 → 1565).
- `dinheiro.js:65-74`: sem série para o plano (Caicó, por exemplo), o título continua "Hoje, melhor e ideal." quando há IBGE.
  - O alerta duplicado do passo saiu; fica o aviso do `hoje_ideal`.
  - O que falta e a tabela por cultura foram para "Ver como calculamos" (`semConta`, `:344`).
  - Sem nenhum dado do IBGE, fica o título antigo, "Ainda não dá para fazer a conta aqui."
- `dinheiro.js:57`: `termo("em_dez", "1 em 10")` vai para a legenda do gráfico, e assim o glossário do passo 4 continua ligado.
- O "seu olho" da lavoura grande (`OLHOS.agro`) passou a ir no aviso do gráfico. Sem mandioca, ele fica no "Ajustar a conta".

### B2. hoje_ideal.js: modo "comparacao"
- `hoje_ideal.js:523` `numeros(f)`: o típico (p50) fica sempre em destaque e o "ruim" pequeno. Saiu a troca por p10 em "garantir".
- `hoje_ideal.js:595-614`: Hoje, Melhor e Ideal ficam num painel só (`.hi-tres`), cada um com a barra da cor do gráfico.
  - Hoje e Ideal ocupam 1 linha cada: descrição + típico + ruim. O Ideal leva o `planoMini` numa fileira embaixo.
  - O Melhor fica aberto com até 3 ajustes (`frente3`) e o resto vai para "Mais N ajustes".
  - Os ajustes são linhas, não cartões dentro do cartão.
- Saíram da frente:
  - os chips "à frente de hoje em N de 100" (`frente()` foi removida);
  - o "quebra em N de 10" (`quebraHtml`), que fica na tabela;
  - o "o que pesa", que foi para o detalhe como "O que pesa no jeito de hoje" (`:638`);
  - o destaque "garantir/vender" do Ideal.
  - A coluna "à frente de hoje" continua na tabela de `detalhes()`.
- `hoje_ideal.js:529` `textoHoje()` e `:572` `chipHoje`: "milho + feijão, tudo junto (o comum daqui) · mudar", com `data-editar="hoje"`.
  - A % só aparece quando a divisão não é igual.
  - Fiz uma função nova para não mudar `descHoje`, que é contrato com o A.
- `hoje_ideal.js:313`: `TXT_BAIXIO` = "Em cima, feijão no lugar do milho (o milho fica no baixio)." Vale para `TXT_AJ.baixio` e para o
  caso sem série (antigo `:300`).
- "sem preço aqui" virou "comida da criação, fora do R$" no chip do Hoje e na nota do Ideal (antigos `:567` e `:616`). Com "outra"
  marcada, o chip diz só "fora do R$".
- `hoje_ideal.js:579-596`: os avisos de dado (falta série ou lavoura grande) agora aparecem numa linha logo abaixo do gráfico, no mesmo
  painel. Antes ficavam num painel acima dele. Assim o gráfico começa em ≤ 450 px também em Caicó e Barreiras.
- `opcoes.detalhesEm` (`:620`): no passo 4, o "como calculamos" vai para o "Ver como calculamos" do passo. Sem ele, o módulo mantém o
  fecho antigo (página `web/teste/hoje_ideal.html`).
- Gráfico (`:497`): 210 → 196 px de altura. Os números não mudaram.
- Removida a propriedade `hojeDesc` de `comHoje()`, que só o herói usava.
- Frases proibidas no modo "pergunta" (órfão, mas é o Plano B): `:373` "sem preço aqui" virou "fora do R$" e `:403`
  "Só o que muda a conta." virou "Toque no que você faz.".

### B3. cenarios.js
- `cenarios.js:429`: o rótulo agora é "O que vale mais para você?".
- `cenarios.js:435-437`: abas grandes com ícone (Água · Renda · Solo · Plano) logo abaixo do rótulo.
  - Quando a prioridade é o padrão, a aba acesa diz "sugerido" (`:419`). O chip "Sugerido no El Niño: …" saiu.
- `cenarios.js:18` e `:448-451`: o clique em `[data-jeito]` faz `ctx.set({prioridade: INV[jeito]})`. Saiu o `est.escolha`, e o jeito
  aceso agora vem sempre de `ef.prioridade`.
- `cenarios.js:441-445`: a ≤ 760 px, a grade e o giro, junto com "como pontuamos", ficam num "ver mais" só, "Ver a comparação". A
  faixa, a frase da troca e as abas ficam à vista. No computador a grade continua à vista.

### B4. CSS
- `dinheiro.css:24-41`: linha "Conta com", botão "ajustar" (com alvo de 44 px) e painel `.mais-conta` com os summary de 46 px.
- `hoje_ideal.css:89-95` e `:116-150`:
  - linhas Hoje/Melhor/Ideal (`.hi-bloco`, `.hi-linha`, `a.hi-mudar`);
  - ajustes sem fundo de cartão;
  - aviso dentro do painel do gráfico;
  - `.hi-tres.agro .hi-l-num` apagado;
  - `@media (max-width: 420px)` para os números.
- `cenarios.css:5-15`: as abas `.cen-aba` e `.cen-sug`.

## O que não fiz e por quê
- **Barreiras (2903201) passa do teto de altura: 2.282 px > 2.200.** É o único dos 7 com o aviso de lavoura grande à vista, e os
  números são largos ("R$ 58,8 mil"). Já compactei o aviso (de painel para linha) e o "seu olho" dele (de caixa para etiqueta).
  - O que ainda daria para cortar é texto honesto: o aviso, ou a frase "Contra o plano".
  - Os outros 6 ficam entre 2.008 e 2.110 px.
  - As palavras de Barreiras ficam em 257, dentro do teto de 260.
- Barreiras também passa da meta de 180 palavras (o teto é 260). A meta também não fecha nos outros: dá 188 a 208 palavras.
  O que sobra é a frase "Contra o plano: …" (ponto 8, as trocas entre os jeitos), que preferi deixar à vista.
- O "Mudar" do chip Hoje vai para "Sua roça" (`data-editar="hoje"`, como pede a seção 7). A seção 2 dizia que ele abriria o
  "Ajustar a conta" na linha do arranjo. O arranjo continua a 1 toque pelo "ajustar" da linha de suposições.
- O texto de apoio antigo ("O seu roçado de 1 ha refeito nos anos…") saiu da frente. Sem isso o gráfico passaria de 450 px.
  O mesmo texto está no título do selo PROJEÇÃO e no "Ver como calculamos".

## Pedidos ao integrador
1. **Código órfão (não apaguei):**
   - O modo "pergunta" do `hoje_ideal.js` (`desenharPergunta`, `telaCulturas`, `telaArranjo`, `telaManejo`, `resumoHoje`, `topo`, `PARES`,
     `miniRocado`, `tela/rascunho/visto/zerados`) e o CSS dele. Ainda é usado em `web/teste/hoje_ideal.html` e no Plano B.
   - `.hi-fecho` e `.hi-olho`, que só aparecem fora da jornada.
   - Fora dos meus arquivos: `G.barrasH` (`graficos.js`) não é mais usado pelo passo 4. `C.comida2027`, `C.precoEmpate` e `C.totais`
     agora só são usados por `teste_calculo.mjs`.
2. Para o `LEIA-ME.md` (I5): a linha do passo 4 na tabela dos extras.
   - Ela deve dizer que `cenarios` é "O que vale mais para você?" e que as abas gravam `prioridade`.
   - O "acende o jeito da prioridade do Seu bolso" não vale mais.
3. **`percorrer_fluxo.py` e o script de aceite:** os seletores do passo 4 que eu uso são:
   - `.cen-aba[data-jeito=renda]` (prioridade);
   - `[data-abrir=ajustar-conta]`;
   - `#ajustar-conta`;
   - `[data-set="custo=desembolso"]` e `[data-set="arr=baixio"]`;
   - `.hi-mudar[data-editar=hoje]`.
4. O servidor recusou conexões várias vezes (`ERR_CONNECTION_REFUSED`) com os 5 construtores ao mesmo tempo. Se algum print vier em
   branco ("Olhando o seu lugar lá de cima"), repita.

## Como testei
- `node --check` nos 3 JS, a cada mudança.
- `node testes/ferramentas/teste_calculo.mjs`: saída **idêntica** à base (`diff` com `E:/campeonato-nasa/tmp/base_fluxo/base_calculo.txt`).
- No node (`E:/campeonato-nasa/tmp/fluxo_novo/B/num.mjs`), `comparar()` nos 7 municípios, com prioridade padrão e "vender". Os números são
  iguais com as duas prioridades.
- Edge sem janela a 390×844 (`E:/campeonato-nasa/tmp/fluxo_novo/B/medir.py`, com o script da seção 8 e alguns campos a mais), passo 4
  nos 7 municípios:

| Município | Altura (px) | Palavras | Gráfico (topo, px) |
|---|---|---|---|
| Quixadá | 2.068 | 204 | 432 |
| Crateús | 2.068 | 204 | 432 |
| Picos | 2.063 | 193 | 407 |
| Caicó | 2.008 | 188 | 407 |
| Petrolina | 2.110 | 208 | 432 |
| Arapiraca | 2.090 | 203 | 407 |
| Barreiras | 2.282 | 257 | 432 |

  Nos 7 municípios:
  - `primarios` 1 e `contadores` 0;
  - nenhuma frase proibida;
  - nenhum selo menor que 11 px nem summary menor que 44 px;
  - olhos ≤ 2;
  - nenhum controle antes do gráfico;
  - nada rola de lado, nem com todos os `details` abertos;
  - "(o comum daqui)" à vista;
  - zero erro no console.
- Quixadá `#/2311306/4` (critério 8): Hoje R$ 2.480 (ruim R$ 984), Melhor R$ 4.190 (ruim R$ 2.490), Ideal R$ 4.360 (ruim R$ 2.760).
- Toques em Quixadá (critério 10 e os ajustes):
  - "Renda" grava `prioridade=vender`, a aba acende e os números não mudam;
  - "ajustar" abre o `#ajustar-conta` a 150 px do topo;
  - "Semente, trator, adubo e diária" grava `custo=desembolso`, o bloco continua aberto e a rolagem não pula;
  - "Milho no baixio" grava `hoje=milho:50,feijao:50|cons=0|mbx=1` e o chip passa a dizer "milho + feijão, milho no baixio".
  - Também rodei o cenário do Seu Antônio (`hoje=milho:34,feijao:33,mandioca:33&maniva=plantada&ha=3&terra=barro&baixio=pouco`):
    2.135 px, 220 palavras, sem erro.
- `.hi-mudar` (com o `roca.js` do A): vai a `#/2311306/2`, o primário diz "Voltar a Quanto rende →", e o primário volta a `#/2311306/4`.
- As páginas `web/teste/hoje_ideal.html` e `web/teste/cenarios.html` abrem sem erro.
- Prints a 390 px em `E:/campeonato-nasa/tmp/fluxo_novo/B/`:
  - `final_<cod>.png`, os 7 municípios com os "ver mais" fechados;
  - `q4_aberto.png`, com todos abertos;
  - `q4_1280.png`, no computador;
  - `antonio_4.png`.
