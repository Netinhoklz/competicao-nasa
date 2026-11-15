# 03 · Valor da informação: parecer no debate

Lente: medir. Li as 10 propostas e conferi na API e no código as afirmações que mudam o voto. Medidas novas desta
rodada estão em `E:/campeonato-nasa/tmp/vi2_*.json` (Quixadá 2311306 e Piritiba 2924801). Nada do site foi editado.

**Em uma linha:** as 10 lentes concordam em 80% do que importa. Só 4 itens ficam na entrada: culturas de hoje, tamanho
(já preenchido), terra e baixio. Os outros vão para onde a resposta é lida. Onde há divergência, a medida decide:
maniva no plano, custo com rótulo honesto, a divisão em % visível quando há mandioca e o "não sei" da terra com aviso.

---

## 1. O que medi de novo para decidir

| Afirmação | Quem | Conferido | Resultado |
|---|---|---|---|
| O "não sei" da terra mostra janela que não vale em todo solo | 08 | **sim** | Piritiba: o "não sei" dá milho de 01/04 a 30/04, mas o milho só é zoneado em AD5 e AD6. Com areia ou terra misturada, o resultado é "não zoneada". Quixadá: o "não sei" dá feijão comum de 01/02 a 10/03, e com areia (AD2) ele também fica "não zoneada". |
| A terra muda o plano A/B/C | 02, 10 | **não** | O plano fica igual com areia, misturada, barro e rasa, tanto em Quixadá quanto em Piritiba. A terra muda as **datas** e a lista "agora". Na areia, o preparo do caupi passa de 22/12–20/01 para 22/01–20/02; no barro, o caupi vai de 11/03–20/03 para 11/03–20/04 e o milho de 21/02–28/02 para 11/02–10/03. |
| Terra "rasa/piçarra" (AD1) tira o milho | 05 | **em parte** | O plano de Quixadá fica igual, porque o milho está só no baixio. Só o milho e o feijão comum da agenda viram "não zoneada (AD1)". |
| "Não tenho baixio" e "sem maniva" mudam o plano | todos | **sim** | Com baixio=0 some a linha Baixio. Com maniva=nao, a mandioca sai das Partes A, B e C e entra o sorgo forrageiro. |
| Trator = "máquina e insumos" | 02, 06, 07, 10 | **não bate** | O custo de desembolso da CONAB é de R$ 1.136/ha no milho, R$ 1.992/ha no feijão e R$ 4.387/ha na mandioca, contra a semente de R$ 284, R$ 142 e R$ 0. Esse custo é de uma lavoura acima da média (`seguranca.js:265`), não de uma diária de trator. Em Quixadá ele vira o resultado de R$ 4.364 para −R$ 1.743, e o plano passa de ganhar em 98 de 100 combinações para 47. |
| A prioridade só acende um jeito | 02, 04, 06, 10 | **não** | `dinheiro.js:147-149`: com "garantir" (o padrão no El Niño), o número grande do herói é o **caso ruim** (P10). Com as outras prioridades, é o típico (P50). É essa a origem do "número grande do cartão ≠ número da barra" que a lente 01 apontou. |
| "Próxima" grava o padrão como se fosse resposta | 06 | **sim** | `hoje_ideal.js:442` chama `gravar()` ao avançar. Numa tela já preenchida isso apagaria o "(típico daqui)", e o "não sei" da terra deixaria de virar pergunta ao técnico (`leve_ao_tecnico.js:11`). |
| O roçado do Censo conta a área inteira para cada cultura | 08 | **sim** | O Censo de Quixadá dá roçado de 1,03 ha, milho 1,03 ha e caupi 0,95 ha. O "Hoje" divide 50/50 (`hoje_ideal.js:57`). Não conferi a PAM, então o risco continua aberto. |
| O aviso honesto do "não sei" exige mexer no `motor.py` | 08 | **não precisa** | O cardápio já traz `por_solo` para cada cultura (Piritiba, milho: só AD5 e AD6). O navegador consegue escrever "só em terra de barro ou no baixio" sem tocar no núcleo. |

Medida anterior, que continua valendo (`../03_valor_informacao.md`): só 5 itens mudam o plano, as datas ou o R$. São eles
culturas de hoje, tamanho, terra, baixio e maniva. Ainda **culturas de hoje com mandioca em ⅓** derrubam o número de
combinações em que o plano ganha de 98 para 14.

---

## 2. Placar das 10 lentes (onde já há acordo)

| Item | Votos | Acordo |
|---|---|---|
| hoje.culturas | manter 9, fundir 1 (sem a %) | **10/10 na entrada** |
| hoje.arranjo | inferir 3, mover 3, fundir 2, cortar 1, opcional 1 | **10/10 fora da entrada** |
| hoje.manejo | inferir 4, cortar 3, opcional, mover e fundir 1 cada | **10/10 fora do caminho** |
| hist.anos | inferir 6, fundir 2, mover 2 | 9/10 fora da entrada |
| hist.deu | mover 10 (passo 5) | **10/10** |
| hist.faz | cortar 7, fundir o preparo no custo 3 | **10/10 como pergunta sai** |
| terra | manter 9, mover para o passo 3 1 | 9/10 na entrada |
| ha | manter 7, mover ou inferir para uma ficha 3 | **10/10 já preenchido** |
| baixio | manter 10 | **10/10 na entrada** |
| agua | mover 5, opcional 4, inferir 1 | **10/10 fora do caminho** |
| maniva | inferir 4, manter 3, mover 2, opcional 1 | **dividido** |
| bolso.prioridade | mover 5, manter 3, fundir 1, inferir 1 | dividido (topo do passo 4 ou "Outros jeitos") |
| bolso.raiz | opcional 6, mover 4 | **10/10 em "Ajustar a conta"** |
| bolso.custo | opcional 5, fundir com o preparo 4, mover 1 | dividido no **rótulo** |
| bolso.gs | cortar 9, inferir 1 | **10/10: o controle sai** |

---

## 3. As melhores ideias dos outros

1. **06 Arquitetura: `ctx.editar(k)` com volta.** Cada "mudar" abre a pergunta certa e devolve a pessoa ao passo de onde
   veio; cada tela vira uma entrada no histórico, então o voltar do Android funciona. É o que torna **inferir** seguro:
   corrigir um padrão custa 1 toque, não 11 telas.
2. **08 Precisão: o "não sei" honesto.** Medi e está certo (Piritiba, milho; Quixadá, feijão comum). Na minha
   proposta eu tratei a terra como "só datas". Não é só isso: ela é a **única resposta que pode tirar uma cultura do
   zoneamento**. Isso torna a terra mais valiosa e impede que ela seja inferida.
3. **04, 07 e 10: maniva na linha da mandioca do plano** ("Não consegue maniva? Trocar"). A pergunta aparece só onde a
   mandioca aparece e resolve a dependência circular da minha proposta (ver §7).
4. **01 e 10: o globo vai direto para a "Sua roça"** (`#/<cod>/2`), e o passo 1 sai do caminho, a 1 toque nas
   pílulas. O passo 1 não pergunta nada e repete o painel do globo (El Niño, chuva).
5. **06: os padrões não são gravados como resposta.** Sem isso, a tela única perde o "(típico daqui)" e a lista do
   técnico.
6. **09 Celular: travar o toque duplo.** É um erro medido: dois toques em 120 ms pulam a pergunta do tamanho. É
   obrigatório em qualquer tela que avança com o toque.
7. **04 Júri: selo com o nome da missão** ("MEDIDO · NASA SMAP"). Custa uma linha em `comum.js` e faz a palavra NASA
   aparecer nas telas, onde hoje ela aparece 0 vezes.
8. **01 Agricultor: "não vende" vira "vira comida da criação (fora do R$)"** para todos. Cobre a criação sem pergunta
   nova.
9. **08: corrigir números mal atribuídos.** O "+R$ 909 milho só no baixio" vem da troca de milho por feijão em cima,
   e o "acima do recorde" é falso (+2,46 contra +2,59).
10. **02, 06 e 10: prioridade no cabeçalho de "Outros jeitos"**, onde ela age. Vale só com a condição do §5.

---

## 4. Objeções concretas

| Lente | Ideia | Objeção |
|---|---|---|
| 02, 06, 07, 10 | Preparo da terra = custo ("Trator → máquina e insumos") | O desembolso da CONAB é de R$ 1.136 a R$ 4.387/ha, muito mais que uma diária de trator. Com esse rótulo, quem aluga trator um dia vê o plano passar de ganhar em 98 de 100 para 47, e o resultado de R$ 4.364 para −R$ 1.743. **Um erro de rótulo vira erro de resultado.** O rótulo tem de dizer o que a conta soma: "Semente, máquina, adubo e diária (custo da CONAB)". |
| 05 | Pergunta nova "Tem criação?" | Nenhum código lê a resposta (`criacao` está parada em `roca.js:17,87`), então o efeito é 0 por construção. É o mesmo tipo de pergunta que o José reclamou. A frase fixa da lente 01 cobre o assunto sem tela. |
| 05 | Uma pergunta por tela (5 + 1) | Com padrão marcado, a tela única custa 1 toque; 6 telas custam 6. O ganho de informação é o mesmo. |
| 05 | Terra "rasa/piçarra" | O plano de Quixadá fica igual, e o mapa rasa → AD1 é suposição. É barato, mas não é prioridade nas 4–6 h. |
| 08, 09 | Tamanho fora da entrada (só ficha) | O R$ é linear na área (0,5 ha dá R$ 2.105; 3 ha, R$ 12.684), e o tamanho é pedido explícito do José. Uma linha já preenchida custa **0 toque**, então não há ganho em esconder. |
| 01 (e o atual) | Selo MEDIDO no tamanho padrão | O MEDIDO vale para o município, não para o roçado dele. O certo é "típico daqui (Censo 2017)", que é uma SUPOSIÇÃO para ele. |
| 01, 02, 04, 10 | Divisão igual como padrão escondido | Com mandioca marcada, a divisão igual dá ⅓ a ela, e o plano passa de ganhar em 98 para 14 (medido). É **o padrão que mais pesa no produto**. A barra da divisão tem de ficar visível quando a mandioca está marcada. |
| 02 | Fichas 2×2 que abrem a pergunta grande | Mudar custa 2 toques, e as opções ficam escondidas. A terra, que muda as datas, seria respondida menos. Botões na própria tela custam 1 toque. Renumerar os passos quebra cerca de 15 links: melhor manter `#/cod/1..5` (como propõem 07 e 10). |
| 04 | Terra só no passo 3 | Seria aceitável **como segundo lugar** para mudar, ao lado de "Suas datas". Sozinha, deixa o "não sei" valendo para a maioria, e o "não sei" de hoje mostra janelas que não valem em areia. Se for, tem de ir junto com o aviso do `por_solo`. |
| 07, 09 | Toque que já avança, com 3 ou 4 telas | Precisa travar o toque duplo, que é um erro medido. São 3 ou 4 telas contra 1, para a mesma informação. |
| 07 | Abas + CSS global + perguntas na mesma janela de 4–6 h | É risco de prazo. A própria lente diz que as abas podem esperar. |
| 09 | Botão "Ouvir" | É escopo novo (45 min) e não tira nenhuma pergunta do caminho. Fica para depois do essencial. |
| 08 | Mudar o `motor.py` na véspera | O `por_solo` já chega ao navegador, então o aviso sai em JS sem mexer no núcleo. |
| 06 e 03 (minha) | Maniva como bloco na entrada | Não serve em 5 de 10 municípios (planos sem mandioca). Só mostrá-la "quando o plano tem mandioca" exige o plano antes da tela que o define. |
| 01, 02, 04, 09 | "A colheita paga o gasto?" e o custo, ambos fechados | Some da vista a maior sensibilidade de R$ depois das culturas de hoje. Pelo menos uma linha com a base do custo fica visível sob o herói ("sobra depois da semente; sem diária nem máquina"). |
| 02, 04, 06, 10 | Prioridade só em "Outros jeitos" | Hoje ela escolhe o número grande do herói (P10 ou P50). Se sair do topo sem fixar o herói, o número grande muda sem a pessoa saber por quê. |

---

## 5. Votos por item

| Item | Voto | Para onde |
|---|---|---|
| hoje.culturas | **manter** | Tela única, linha 1: milho e feijão já marcados. A barra da divisão fica visível quando a mandioca está marcada ou há 3 culturas ou mais. "Ajustar %" a 1 toque. |
| hoje.arranjo | **inferir** | "Tudo junto". O ajuste do Melhor diz "se ainda não faz", e o rótulo dos +R$ 909 é corrigido (vem da troca de cultura). |
| hoje.manejo | **cortar** | A semente vem do Censo (73,5%). 1ª chuva e fogo viram conselho fixo em "O que fazer agora". |
| hist.anos | **inferir** | 2026 e 2025 iguais ao jeito de hoje, com selo SUPOSIÇÃO e frase "Se…". No cartão do giro, 1 toque: "Em 2025 foi diferente?". |
| hist.deu | **mover** | Passo 5, "A sua memória", respondido ali mesmo (sem `ctx.link(2)`). "Deu bem" sai. |
| hist.faz | **cortar** | Nenhum código lê. O preparo **não** vira custo (ver §4). |
| terra | **manter** | Tela única, 4 opções, com "Não sei" explícito (vira pergunta ao técnico) e o aviso do `por_solo`. Também dá para mudar ao lado de "Suas datas". |
| ha | **manter** | Tela única, linha já preenchida "1,03 ha · típico daqui (Censo 2017) · mudar", que abre o `area.js`. Sem MEDIDO no roçado dele. |
| baixio | **manter** | Tela única: Tenho / Não tenho / Não sei. O tamanho (pequeno, ⅓, metade) vai para o desenho, porque dá o mesmo JSON (`ad_baixio=15`) e no máximo −R$ 495 contra o ⅓. |
| agua | **mover** | "Leve ao técnico", com a linha fixa "Plano de sequeiro (só chuva). Se você irriga, as datas mudam: pergunte ao técnico". |
| maniva | **mover** | Na Parte A do plano: "Não consegue maniva? Trocar". Se a mandioca foi marcada no jeito de hoje, vale "já plantada", com chip "mudar". |
| bolso.prioridade | **mover** | Para o cabeçalho de "Outros jeitos", **só se** o herói passar a mostrar sempre o típico grande e o caso ruim pequeno. Senão fica no topo do passo 4. |
| bolso.raiz | **opcional** | "Ajustar a conta" (fechado), com o "seu olho" da casa de farinha. |
| bolso.custo | **opcional** | "Ajustar a conta", com o rótulo honesto "Só a semente / Semente, máquina, adubo e diária (CONAB)". A base do custo fica visível sob o herói. |
| bolso.gs | **cortar** | O controle sai. Vira chip automático pelo tamanho ("até 5 ha: você cabe") no passo 5 e no técnico. |

---

## 6. Melhor fluxo: o da lente 10 (Simplicidade radical), com 6 emendas

**Por que a 10.** É o fluxo com menos toques e sem perguntas mortas na entrada. O globo e o painel levam direto à
"Sua roça", que é uma tela só. O resultado vem em Plano · Dinheiro · Segurança · O lugar, e os números de rota
`#/cod/1..5` ficam iguais. As lentes 01 e 06 chegam quase ao mesmo desenho; a 06 traz a navegação que falta à 10.

1. **Entrada (tela única "Seu roçado")**:
   - Culturas de hoje, com a barra da divisão visível quando há mandioca.
   - Tamanho já preenchido ("típico daqui", sem MEDIDO).
   - Terra (4 opções, "Não sei" explícito).
   - Baixio (Tenho / Não tenho / Não sei).
   - Nada é gravado até o toque.
2. **Navegação da lente 06**:
   - `ctx.editar(k)` com volta ao passo de origem.
   - Cada tela como entrada no histórico.
   - Um único botão primário, na barra de baixo.
   - Trava do toque duplo (lente 09).
3. **Maniva no plano** (Parte A: "Não consegue maniva? Trocar"), com "já plantada" inferido da mandioca de hoje.
4. **Custo honesto**:
   - Nada de "trator = máquina e insumos".
   - O rótulo diz o que a conta soma.
   - Sob o herói, uma linha visível com a base do custo.
5. **Herói fixo no passo 4**:
   - Típico grande e caso ruim pequeno, os dois sempre.
   - A prioridade passa para "Outros jeitos".
   - Sai o bloco repetido "No caso ruim…".
6. **"Não sei" da terra com aviso**, tirado do `por_solo` no navegador ("só em terra de barro ou no baixio"), sem
   mexer no `motor.py`.

**Toques do globo ao plano:**
- Com os padrões: 3 (município · "Montar o meu plano" · "Ver o meu plano").
- Respondendo terra e baixio: 5.
- Mudando também as culturas: 6 a 7.

Hoje são 14 no mínimo e uns 30 respondendo de verdade.

---

## 7. Linhas vermelhas (não podem ser cortadas)

1. **Culturas de hoje na entrada.** São a régua do Hoje → Melhor → Ideal, mudam o resultado (98 → 14 com mandioca) e
   foram pedidas pelo José.
2. **Baixio na entrada.** Muda o plano em 10 de 10 municípios.
3. **Terra perguntada, nunca inferida**, com "Não sei" explícito. É a única resposta que pode tirar uma cultura do
   zoneamento (Piritiba, milho; Quixadá, feijão comum na areia).
4. **Maniva a 1 toque onde a mandioca aparece.** "Sem maniva" vira o plano e tira a mandioca de A, B e C.
5. **Tamanho visível com "mudar"** (pedido do José; o R$ é linear na área).
6. **Padrão ≠ resposta.** O que não foi tocado continua marcado "(típico daqui)" ou "SUPOSIÇÃO" e vira pergunta ao
   técnico.
7. **Nenhuma tela promete efeito que não tem**: "5 perguntas", "Só o que muda a conta", "muda o que dá para salvar".
8. **Nenhuma pergunta cuja resposta não tem leitor** (água, Garantia-Safra, "deu bem", palhada, esterco, criação), a
   não ser como pergunta ao técnico.
9. **O rótulo do custo diz o que a conta soma.** Sem isso, o resultado vira por causa de uma palavra.
10. **O ponto 15 continua coberto**: equipamento no custo, mercado na prioridade e no preço da raiz, água no técnico.
    **O ponto 16 também**: a memória do ano ruim fica no passo 5, respondida ali mesmo, com o IBGE ao lado.
11. **Inferências com selo e "mudar"**: 2025 igual a 2026, mandioca já plantada, divisão igual.

---

## 8. Onde mudei de ideia e por quê

- **Maniva: de "manter (condicional) na entrada" para "mover para o plano".** A minha condição ("só se o plano tem
  mandioca") era circular: o plano depende da terra e do baixio, que estão na mesma tela. Na linha da mandioca, a
  pergunta aparece só quando importa e onde o efeito se vê (lentes 04, 07 e 10).
- **Baixio: de 5 opções para 3.** O tamanho dá o mesmo JSON (`ad_baixio=15`), e a diferença é de no máximo
  −R$ 495 (cerca de 11%) contra o ⅓. No desenho ele se ajusta melhor (lentes 02, 04 e 10).
- **Passo 1: de "1 tela na frente" para "fora do caminho, a 1 toque".** Ele não pergunta nada e repete o El Niño e a
  chuva do painel. A lente 04 tem razão no medo de esconder a NASA, e o selo com o nome da missão resolve isso melhor
  que 1.000 px antes da 1ª pergunta.
- **Prioridade: de "1º controle do passo 4" para "Outros jeitos", com condição.** Só vale se o herói ficar fixo. Ao
  medir, vi que é a prioridade que troca o número grande (P10 ou P50), e isso explica a contradição que a lente 01 viu.
- **Terra: vale mais do que eu tinha escrito.** Não é só "+10 dias de janela". O "não sei" esconde culturas não
  zoneadas (achado da lente 08, que conferi). Por isso a terra fica obrigatória e com "Não sei" explícito.
- **Não mudei** no custo. Juntar custo e preparo é boa ideia para a linguagem, mas o mapa "trator = desembolso da
  CONAB" é errado em número: a medida mostra que ele vira o resultado.
