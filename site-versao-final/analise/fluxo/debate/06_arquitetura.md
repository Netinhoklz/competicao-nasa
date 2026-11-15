# 06 · Arquitetura de informação e navegação: parecer do debate

Lente: número de passos, progresso, botões, voltar, hash e onde cada resposta e cada dado mora.
Conferi no código e na API antes de afirmar. As referências estão em cada item.

## Resumo em 4 linhas

1. **Fluxo preferido: o da 10 (Simplicidade radical), com 8 emendas.** O globo leva direto a "Sua roça" (`#/cod/2`), que é **1 tela com 4 blocos**. Depois vêm **4 abas**: Plano · Rende · Seca · Do espaço. Os números das rotas ficam como estão.
2. **Mudei de ideia na entrada.** Eu mantinha o passo 1 curto antes das perguntas. Conferi que o painel do globo já mostra o El Niño, a chuva típica e "previsão firma em fev" (`rocacerta.js:166-178`). Por isso o passo 1 vira a última aba.
3. **Achado novo.** Com prioridade "garantir", que é o padrão em ano de El Niño, o número grande do Hoje/Melhor/Ideal passa a ser o **caso ruim**. O gráfico logo acima mostra o **típico** (`hoje_ideal.js:521-525`, `dinheiro.js:147-149`). Daí vem o "R$ 984 × R$ 2.480" (lente 01). Antes de mover a prioridade para baixo, é preciso fixar o número grande no típico. Senão um toque embaixo muda os números de cima.
4. **Linha vermelha da navegação:** um só avançar por tela, na barra de baixo. Cada tela é uma entrada no histórico. Todo "mudar" abre a pergunta certa e volta para a tela de onde a pessoa saiu.

---

## 1. Consenso (9 ou 10 lentes)

- As 11 telas e o resumo viram 1 tela, ou poucas, com o padrão do lugar já marcado. Sai o resumo "Pronto".
- Deixam de ser perguntas: água, Garantia-Safra, "deu bem", "o que já faz" (palhada, esterco, faixas) e o manejo (1ª chuva, fogo, semente).
- Passo 4: o Hoje → Melhor → Ideal vai para o topo. Sai o herói duplicado "No caso ruim…". Raiz e custo vão para "Ajustar a conta", que fica fechado.
- Passos 3–5: no máximo 2.000–2.500 px cada, e o resto em "ver mais".
- Um botão de avançar por tela. Sai a promessa falsa das "5 perguntas".

## 2. As melhores ideias dos outros

| De | Ideia | Por que é boa (pela minha lente) |
|---|---|---|
| **10 Simplicidade** | Entrada direta em `#/cod/2`. As abas aparecem na ordem [3, 4, 5, 1], **sem renumerar as rotas**. | É o corte mais barato e o mais limpo: mudam 4 links (`principal.js:94`, `rocacerta.js:333`, `roca.js:194` e `:209`). `ctx.link(n)`, `PADRAO` e os links antigos continuam valendo. |
| **10 Simplicidade** | O tamanho vira 1 linha já preenchida ("Roçado: 1,03 ha, típico daqui · mudar"). | Atende ao pedido do José sem ocupar um bloco inteiro e custa 0 toque. |
| **02 Produto** | Faixa de 1 linha do El Niño no topo de "Sua roça". A ficha do topo vira 1 linha, sem "não sei". | Sem o passo 1, quem chega por `roca.html` (sem passar pelo globo) também vê o contexto. Os "terra: não sei" do topo parecem erro. |
| **04 Júri** | Selo com o nome da missão ("MEDIDO · NASA SMAP"). | Conferi: a palavra "NASA" aparece **0 vezes** nos 16 textos, e SMAP, IMERG, GPM e POWER também 0. É uma mudança só em `comum.js:24-27` (mapear `fonte` → missão) e vale para todas as telas. |
| **04 Júri** | "E se chover…" visível no passo 5. "Como o QUADRA sabe" junta harmonização, satélite × chão, os 7 métodos e a confiança. | O ponto 13 é a melhor interação da demo. A página de ciência deve **virar a aba "Do espaço"** (o passo 1), e não uma rota 6 nova. |
| **01 Agricultor / 09 Mobile** | Um número grande por cartão (o típico), com o caso ruim pequeno embaixo. | Corrige a dupla leitura que achei (resumo, linha 3). Com isso a prioridade só acende os "Outros jeitos" e pode morar ali sem efeito à distância. |
| **01 / 09** | "Paga trator ou adubo? Não / Sim" no lugar de "O que você paga". | É mais preciso que a fusão com o preparo, que eu tinha proposto (ver seção 6). |
| **01 Agricultor** | "Não vende" vira "vira comida da criação (fora do R$)". O selo MEDIDO sai do tamanho padrão. | Resolve a falta da pergunta da criação só com texto. O tamanho padrão é o típico do município, não o roçado dele. |
| **03 Valor da informação** | Efeitos medidos: maniva "não" leva o plano de 98 para 0 em 100, e "plantada" soma R$ 1.145. Custo com máquina leva a sobra de R$ 4.364 para −R$ 1.743. | Separa o que precisa de controle visível do que pode ficar fechado. A maniva não pode ser só suposta. |
| **09 Mobile** | Bug do toque duplo. | Confirmado no código: `perguntas.js:118-119` soma `q += 1` antes de `ctx.set` redesenhar, e os botões antigos continuam ativos. É mais um motivo para uma tela **sem avanço automático**. |
| **09 Mobile** | Contraste do `.eco` de 2,8 para 4,9:1, `summary` com 44 px e passos com até 1.900 px. | São metas que dá para medir na verificação. |
| **08 Precisão** | Corrigir os textos errados: "acima do recorde", "Só o que muda a conta", "+R$ 909" do baixio, a raiz "daqui". Mostrar "antes:" quando a resposta mudou uma data. | É barato e evita que um jurado pegue uma contradição. |
| **05 Extensionista** | Terra "rasa, de piçarra" (AD1). | Testei na API (Quixadá, `textura=1&ad=11`): funciona. Milho e feijão comum ficam "não zoneada no solo escolhido (AD1)", e as faixas do plano não mudam. Custa 1 linha em `TERRA`. |
| **07 Visual** | Inter no lugar do mono, sem cartão dentro de cartão, carrosséis viram grade. | Cerca de 1 h de CSS, sem tocar na navegação, e aproxima as telas do estilo do globo, como o José pediu. |

## 3. Objeções concretas

| De | Ideia | Objeção |
|---|---|---|
| 07, 08, 09, 05 | Perguntas em telas seguidas, com avanço no toque | Cada tela é mais um estado a guardar, mais um contador "n de 4" e mais um voltar a acertar. O toque duplo (confirmado) volta a pular perguntas. Numa tela só, "mudar" é só rolar até o bloco com `foco`. Com 4 blocos curtos, a tela única cabe em cerca de 1.000 px, com o botão fixo. |
| 02 Produto | Renumerar `PASSOS` para [perguntas, plantio, dinheiro, segurança, lugar] | Há cerca de 15 números fixos no código (8 `link(2)`, `link(3)`, `link(4)`, `data-ir`, `passo: 5`, o `rolarTecnico`). Quebra os links antigos e o `percorrer_fluxo.py`. A ordem das abas resolve o mesmo sem renumerar. |
| 04 Júri | Rota 6 nova "Como o QUADRA sabe" | Seria um 6º lugar fora da numeração, com mais um botão fixo no topo. É melhor juntar com a aba "Do espaço" (passo 1), que já guarda harmonização, satélite × chão, confiança e glossário. |
| 04 Júri | Terra no passo 3, ao lado de "Suas datas" | A pessoa precisaria achar o controle no meio do plano. As datas não são o herói do passo 3. A terra é um fato da roça que ele sabe dizer, então o lugar dela é "Sua roça". Mostrar "antes: …" na data que mudou (08) dá o mesmo efeito visível. |
| 07 Visual | Abas fixas **embaixo**, junto com a barra de ação | Ficariam duas barras embaixo, e num 360×640 isso come cerca de 120 px. As abas devem ficar no topo, no lugar das pílulas (`#passos-nav`). Embaixo fica só a ação. |
| 07, 09, 01 | Folha ou tela "Afinar" com %, arranjo, manejo, preparo, raiz e água | A mesma resposta passaria a ter **dois lugares** ("Afinar" e o passo 4). Cada controle opcional mora onde age: a % e o arranjo no cartão Hoje, raiz e custo em "Ajustar a conta", a água no técnico. "Ajustar o roçado" reabre só "Sua roça". A tela "Afinar" da 01, com o HI e o HIST em modo pergunta, traz de volta as 3 + 3 telas. |
| 10 Simplicidade | Tirar a barra "← Voltar / Próximo →" e pôr o CTA no fim de cada aba | Volta o botão dentro do conteúdo, que hoje duplica a barra (prints 13 e 14). A barra de baixo continua com **uma** ação primária, que é a próxima aba: "Quanto rende →", "Se faltar chuva →" e, na última, "Mandar para o técnico". |
| 03, 08, 09 | Prioridade no topo do passo 4 "porque escolhe o número em destaque" | É verdade: `garantir` troca `p50` por `p10` (`hoje_ideal.js:521-525`). Mas isso é o defeito, não um motivo para manter. O número grande deve ser sempre o típico, porque o gráfico diz "Típico em 3 anos" (`hoje_ideal.js:518`). Aí a prioridade só acende os cenários e fica junto deles. |
| 03 | Maniva como bloco condicional da tela única | O bloco aparece ou some quando ele marca ou desmarca mandioca nas culturas, e a tela pula embaixo do dedo. Fica melhor na linha da Parte A do plano, onde a mandioca aparece. |
| 05 Extensionista | Pergunta nova "Tem criação?" | Na v1 a resposta só muda texto, e foi por isso que cortamos água e manejo. Basta trocar "não vende" por "comida da criação" (01), sem perguntar. Trocar o forrageiro no motor fica para depois da entrega. |
| 05 Extensionista | Manter o passo 1 e 5 perguntas em telas seguidas (8 toques) | O painel do globo já fez a abertura. São 6 toques a mais que a tela única, sem ganho de precisão. |
| 08 Precisão | Mudar o "não sei" da terra em `motor.py` | Mexe no núcleo na véspera, e o servidor não pode ser reiniciado. Só entra se for uma marca de texto (`so_em`), sem mudar janela nem plano, feita pelo dono do núcleo, conferida nos 7 municípios e com o servidor recarregado sem parar. Senão fica para depois. |
| 08 Precisão | "E se chover" num "ver mais", por causa das 2 medianas (3,2 × 3,9) | É melhor corrigir a contradição do que esconder o ponto 13. O controle abre no mesmo cenário do cartão, ou com o rótulo "como nos 4 El Niños fortes", e fica visível. |
| 09 Mobile | Tamanho só como chip no plano | O José pediu essa opção. Visível em "Sua roça", ela custa 0 toque e tira a desconfiança do "plano de 1 ha". |
| 09 Mobile | Botão "Ouvir" (speechSynthesis) | É uma função nova (cerca de 45 min) que não resolve nenhum dos defeitos de fluxo. Fica por último, se sobrar tempo. |
| 01, 02, 07, 08 | Inferir "mandioca já plantada" a partir da mandioca marcada hoje | A inferência mexe no R$ (+R$ 1.145, lente 03), então não pode ficar escondida. Entra o chip "a sua mandioca vira a Parte A · mudar" na própria linha. |

## 4. Votos

| Item | Voto | Para onde |
|---|---|---|
| `hoje.culturas` | **manter** | "Sua roça", bloco 1: chips com milho + feijão marcados como "comum daqui". A % vai para o cartão Hoje do passo 4 (padrão: divisão igual). |
| `hoje.arranjo` | **mover** | Cartão Hoje do passo 4, no chip "tudo junto · mudar", que abre as 3 opções ali mesmo. Padrão: tudo junto. |
| `hoje.manejo` | **inferir** | 1ª chuva = sim; semente pelo Censo; fogo = não sei. Os conselhos (esperar a janela, sem fogo, juntar a semente) ficam fixos em "O que fazer agora". |
| `hist.anos` | **inferir** | 2026 = jeito de hoje; 2025 = igual, com o selo SUPOSIÇÃO. O cartão do giro diz "Se em 2025 também foi…" e tem 1 toque para "Foi diferente". |
| `hist.deu` | **mover** | Passo 5, "A sua memória e os dados": "Lembra de um ano que quebrou?" abre ali mesmo, em `HIST.render` tela 1 dentro de um `details`. Sai o "deu bem". |
| `hist.faz` | **cortar** | Nenhum lugar. O preparo também sai, porque o custo ganha a pergunta própria. |
| `terra` | **manter** | "Sua roça", bloco 4: Areia · Misturada · Barro · Não sei, com o torrão em 1 linha. "Rasa, de piçarra" (AD1) só se for testada nos 7 municípios. |
| `ha` | **manter** | "Sua roça", bloco 2: linha "1,03 ha · comum daqui (Censo)" + chips ½·1·2·3·5. "Outra medida" abre o `area.js`. Sem o selo MEDIDO no padrão. |
| `baixio` | **manter** | "Sua roça", bloco 3: Não tenho · Tenho, pequeno · Tenho, grande · Não sei, nas chaves que já existem (`nao`/`pouco`/`metade`/`""`). Pequeno, ⅓ e metade mandam o mesmo `ad_baixio=15` (`roca.js:47`); o tamanho só muda a área. |
| `agua` | **inferir** | "Só a chuva". Chip opcional "Tenho barreiro ou poço" no "Leve para o técnico" (passo 5). Sai da ficha do topo. |
| `maniva` | **inferir** | Mandioca marcada hoje vira "já plantada", senão "consigo". Na linha da Parte A do plano: "Não consegue maniva? Trocar" e o chip "a sua mandioca vira a Parte A · mudar". |
| `bolso.prioridade` | **mover** | No cabeçalho de "Outros jeitos de girar", no passo 4. **Condição:** o número grande do Hoje/Melhor/Ideal fica sempre no típico. |
| `bolso.raiz` | **opcional** | Passo 4, "Ajustar a conta" (fechado), com o "seu olho" da casa de farinha. |
| `bolso.custo` | **opcional** | Passo 4, "Ajustar a conta": "Paga trator ou adubo? Não / Sim" (Sim = máquina e insumos). |
| `bolso.gs` | **cortar** | Chip calculado pelo `ha` no passo 5: "Garantia-Safra: você cabe (até 5 ha)". |

## 5. Fluxo preferido: o da 10, com emendas

```
Globo → painel (El Niño) → [Sua roça: 1 tela, 4 blocos] → [Plano | Rende | Seca | Do espaço]
         "Montar o plano"        "Ver o meu plano"          abas no topo, sem números
```

Toques até o plano: **2** depois de escolher o município ("Montar o plano" e "Ver o meu plano").

| Tela (rota) | Visível | Barra de baixo (a única ação) |
|---|---|---|
| Sua roça (`#/cod/2`) | Faixa de 1 linha do El Niño (02). h1 "Conte da sua roça." e eco "Já marcamos o comum daqui". 4 blocos: o que planta hoje, tamanho (1 linha), baixio, terra. Sem contador. | ← Mapa · **Ver o meu plano →**. Se a pessoa veio de um "mudar", o botão vira **Voltar a Rende →**. |
| Plano (`#/cod/3`) | Ficha de 1 linha ("1 ha · milho + feijão · terra e baixio: comum daqui · Ajustar"). Roçado visto de cima. O que fazer agora (3 itens). Cartão do giro. Maniva na Parte A. "Por que este plano" com 3 sanfonas de manchete visível. | ← · **Quanto rende →** |
| Rende (`#/cod/4`) | Hoje → Melhor → Ideal como herói, com 1 número grande (o típico) e o caso ruim pequeno. Cartão Hoje com % e arranjo. "Outros jeitos" com a prioridade. Fechados: "Ajustar a conta" (raiz, trator/adubo), El Niño, caixa, paga o gasto. | ← · **Se faltar chuva →** |
| Seca (`#/cod/5`) | "2027 tende a ser apertado". "E se chover…" visível e coerente com os cartões. Só 2027 por cultura. Datas de olhar a terra (19/mar e 30/abr). Memória com entrada ali mesmo. Leve para o técnico, com os chips de água e Garantia-Safra. | ← · **Mandar para o técnico** (WhatsApp). "Imprimir" e "Outro lugar" viram links. |
| Do espaço (`#/cod/1`) | O passo 1 de hoje, com "Como o QUADRA sabe" (04): harmonização, satélite × chão, 7 métodos, confiança, glossário. Sem o "Responder 5 perguntas" e sem o "Pular". | ← · **Voltar ao meu plano** |

Emendas sobre a 10:
1. **(06)** `ctx.editar(k)`: guarda `volta` e `foco`, vai a `#/cod/2`, rola até o bloco e o botão de baixo vira "Voltar a <aba>". Substitui todos os `link(2)` soltos.
2. **(06)** Cada tela é uma entrada no histórico, e o voltar do Android segue a mesma ordem. Nenhum estado de tela fica em variável de módulo. O padrão só vai para o hash com um toque explícito (corrige `hoje_ideal.js:442`).
3. **(02)** A faixa de El Niño de 1 linha em "Sua roça" e a ficha de 1 linha, sem "não sei".
4. **(04)** O selo com a missão NASA. "E se chover" visível. A ciência entra na aba "Do espaço".
5. **(01/09)** Um número grande (o típico), e a prioridade só nos cenários.
6. **(08)** Os 4 textos corrigidos. "antes: …" na data que a resposta mudou.
7. **(09)** Até 1.900–2.000 px por aba, alvos de 44 px e contraste do eco.
8. **(07)** O CSS global (Inter, sem cartão dentro de cartão, carrosséis em grade), se sobrar 1 h.

Divisão de trabalho, com um dono por arquivo (cerca de 5 h de trabalho, cerca de 2 h de relógio):

| Dono | Arquivos | Tarefa |
|---|---|---|
| A | `roca.js`, `roca.html`, `perguntas.js`, `perguntas.css`, os 2 links do globo | Abas, barra, `editar` e a tela única |
| B | `plantio.js`, `historico.js`, `lugar.js` | Plano enxuto, maniva na Parte A, giro condicional, aba "Do espaço" |
| C | `dinheiro.js`, `hoje_ideal.js` (modo comparação), `seguranca.js`, `leve_ao_tecnico.js` | Número típico fixo, herói único, "Ajustar a conta", memória ali mesmo, técnico |
| D | `comum.js` (selo) e `quadra.css` | Selo NASA, contraste, alvos e regras do 07 |

No fim, refazer `percorrer_fluxo.py` e os prints dos 7 municípios.

## 6. Linhas vermelhas

1. **O jeito de hoje e o Hoje → Melhor → Ideal ficam à vista**: bloco 1 de "Sua roça" e herói do passo 4. Nada disso vai para dentro de um "Afinar".
2. **O tamanho fica visível em "Sua roça"**, com ha, tarefas e medida (`area.js`).
3. **O histórico continua no produto**: o cartão do giro (passo 3) e a memória (passo 5), com entrada ali mesmo. Não pode ser cortado por inteiro.
4. **Terra, baixio e maniva continuam editáveis, num toque visível**, porque mudam o plano ou as datas. A maniva não pode ficar só suposta: o plano vai de 98 para 0 em 100.
5. **Uma ação primária por tela, na barra de baixo.** Nenhuma tela com dois avanços.
6. **"Mudar" abre a pergunta certa e volta à tela de origem.** O voltar do Android segue a ordem das telas.
7. **Nenhuma frase promete efeito que não existe** ("muda X" só aparece onde muda).
8. **O selo MEDIDO/SUPOSIÇÃO/PROJEÇÃO fica em todo número.** Todo padrão inferido aparece como "comum daqui" ou SUPOSIÇÃO, com frase condicional.
9. **O ponto 16 fica visível**: a moldura, o "Leve para o técnico" no passo 5 e um "seu olho" por aba. **O ponto 13 fica visível** ("E se chover"). **O ponto 15 continua alcançável**: prioridade, trator/adubo e água.
10. **Não mexer em `servidor.py`.** As rotas `#/cod/1..5` e as chaves do `PADRAO` ficam iguais. As mesmas respostas dão o mesmo plano e os mesmos R$ nos 7 municípios.

## 7. Onde mudei de ideia

- **Entrada:** antes era o passo 1 curto e depois "Sua roça" (3 toques). Agora é a entrada direta em "Sua roça" (2 toques), e o passo 1 vira a aba "Do espaço". Motivo: o painel já mostra El Niño, chuva típica e "previsão firma em fev" (`rocacerta.js:166-178`), e a faixa de 1 linha (02) cobre quem chega sem o globo.
- **Maniva:** antes era o bloco 4 da tela única. Agora vai para a linha da Parte A do plano, inferida das culturas. Motivo: assim a tela única fica com 4 blocos fixos, e a pergunta aparece onde a mandioca aparece, para todos que têm mandioca no plano.
- **Custo:** antes era fundido com o preparo (trator/animal/enxada). Agora é "Paga trator ou adubo? Não / Sim". Motivo: o nível "Máquina e insumos" inclui adubo, e quem usa enxada e compra adubo sairia com a conta errada.
- **Prioridade:** antes era só "mover para os cenários". Agora é "mover, **desde que** o número grande fique no típico". Motivo: conferi que a prioridade troca o número grande (`hoje_ideal.js:521-525`).
- **Abas:** eram 3 (Plantar · Rende · Seca) depois de um funil com pontos. Agora são 4, com "Do espaço" no fim, e o funil deixa de existir, porque só tem 1 tela.
