# QUADRA: fluxo final (14/11/2026, noite)

Fechamento do moderador sobre as 10 propostas e o debate (`analise/fluxo/01..10_*.md` e `debate/`). Nesta rodada ninguém edita o site:
este arquivo é a ordem de serviço dos construtores. Código conferido em `roca.js`, `perguntas.js`, `hoje_ideal.js`, `historico.js`,
`area.js`, `dinheiro.js`, `cenarios.js`, `plantio.js`, `seguranca.js`, `lugar.js`, `leve_ao_tecnico.js`, `cenario_chuva.js`, `comum.js`
e na API (`/api/local?cod=2311306`).

---

## 1. Resumo (5 linhas)

1. O globo leva direto a **uma tela só, "Sua roça"** (`#/<cod>/2`), com 4 linhas já marcadas com o comum daqui: o que planta, tamanho, terra e baixio. Com **2 toques** depois do painel o agricultor vê o plano. Hoje são 14 toques e 13 telas.
2. **Saem do caminho** as perguntas que não mudam número nenhum (água, manejo, "deu bem", "o que já faz", Garantia-Safra) e as promessas falsas ("5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde").
3. O que muda o resultado **depois** do plano é perguntado **onde age**: maniva na linha da mandioca, 2025 no cartão do giro, o ano que quebrou na memória do passo 5, arranjo, custo e raiz em "Ajustar a conta", prioridade nas abas de "Outros jeitos".
4. **Um indicador** (as pílulas do topo, sem número) e **um botão verde** (na barra de baixo). "Mudar" abre a linha certa e volta, e o voltar do Android funciona. Cada passo abre com a resposta, e o resto vai para "ver mais".
5. O passo 1 vira **"Do espaço"**, fora do caminho e a 1 toque. O selo passa a dizer a fonte ("MEDIDO · NASA SMAP"). Não mudam as rotas `#/<cod>/1..5`, as chaves do `PADRAO`, `motor.py` e `servidor.py`.

---

## 2. As perguntas: decisão final

Votos = votos finais do debate (2ª rodada, 10 lentes). "Mover" e "fundir" que apontam para o mesmo lugar estão somados na decisão.

| Item | Decisão final | Votos | Para onde vai | Padrão quando não perguntado |
|---|---|---|---|---|
| `hoje.culturas` | **manter** | manter 10 | Sua roça, linha 1: chips com milho e feijão marcados. A barra colorida da divisão fica sempre à vista, e "quanto de cada" fica fechado na mesma linha (reusa `mexer`/`igual` de `hoje_ideal.js`). Sai o "sem preço aqui" dos chips. | milho 50 + feijão 50, "o comum daqui" (`lerHoje`, `informado=false`) |
| divisão em % | fechada na linha 1 | linha 1: 5 (01, 02, 03, 04, 10) · passo 4: 4 (06, 07, 08, 09) · sem %: 1 (05) | "+ quanto de cada" na linha 1; a barra fica visível (03: com mandioca marcada, ⅓ igual muda o veredito de 98 para 14 em 100) | divisão igual |
| `hoje.arranjo` | **inferir** | inferir 7 · mover 3 (04, 06, 07) | Ninguém pergunta. "Mudar" no chip Hoje do passo 4 abre "Ajustar a conta" na linha "Como fica no roçado". O rótulo do ajuste "Milho só no baixio" vira "Em cima, feijão no lugar do milho" (o R$ vem da troca de cultura, `hoje_ideal.js:103-106`). | tudo junto (`cons=1`) |
| `hoje.manejo` | **inferir** (sem tela) | inferir 5 · cortar 3 (03, 05, 08) · opcional 2 (01, 07) | Nenhuma tela. Os conselhos (esperar a janela, sem fogo, juntar a semente) já estão para todos em "O que fazer e quando". | 1ª chuva = sim; semente pelo Censo (`pct_semente_milho`); queima = não sei |
| `hist.anos` | **inferir + 1 toque** | inferir 8 · mover 2 (01, 02) | Cartão "Por onde começar o seu giro" (passo 3): frase condicional com selo SUPOSIÇÃO e 2 chips, "Foi no mesmo lugar" e "Mudei de lugar", gravados ali mesmo. | 2026 = jeito de hoje; 2025 = igual (SUPOSIÇÃO) |
| `hist.deu` | **mover** ("deu bem" sai) | mover 10 | Passo 5, "A sua memória e os dados": chips com os 3 piores anos do IBGE por cultura e "outro ano", gravados ali (sem `ctx.link(2)`). | nenhuma quebra; a memória mostra os piores anos do IBGE |
| `hist.faz` | **cortar** | cortar 8 · fundir 2 (02, 04) | Nenhum lugar. O preparo **não** vira custo (ver `bolso.custo`). | nada |
| `terra` | **manter** | manter 10 | Sua roça, linha 3: Seca rápido (areia) · Segura a umidade (misturada) · Encharca (barro) · Não sei, com o torrão em 1 linha. No plano: chip "Sua terra: … · mudar" junto das datas e aviso honesto quando for "não sei". | não sei: interseção dos solos zoneados (`motor.py:672-678`), com aviso por cultura tirado de `cardapio[].por_solo` |
| `ha` | **manter** | manter 9 · fundir 1 (07, também antes do plano) | Sua roça, linha 2: "1 ha · típico daqui" (SUPOSIÇÃO), chips ½·1·2·3·5 ha, "≈ N tarefas" e "+ outra medida" (abre `area.js`: tarefas, metros, passos). | Censo 2017 do município (ou da mesorregião), selo **SUPOSIÇÃO**, nunca MEDIDO |
| `baixio` | **manter, 4 opções** | manter 10 · 4 opções 5 (01, 02, 05, 06, 07) × 3 opções 5 (03, 04, 08, 09, 10) | Sua roça, linha 4: Não tenho · Pequeno · Grande · Não sei, com os mini-desenhos. | não sei (⅓ tracejado; o núcleo usa o padrão dele) |
| `agua` | **mover** | mover 8 · inferir 1 · opcional 1 | "Leve para o técnico": chips opcionais "Barreiro ou açude" e "Poço ou irrigo". Em "O que fazer e quando", linha fixa: "Datas para roça de chuva. Molha a roça? Fale com o técnico." Sai da ficha do topo e a "cisterna de beber" sai. | só a chuva (sequeiro) |
| `maniva` | **inferir + 1 toque visível** | inferir 8 · mover 2 (01, 03) | Linha da mandioca no plano (passo 3, à vista, sob o desenho): Consigo maniva · Já tenho mandioca no chão · Não consigo. | mandioca marcada na linha 1 → `plantada`; sem mandioca → `tem` (consigo) |
| `bolso.prioridade` | **fundir** com as abas de "Outros jeitos" | fundir 5 · mover 5 (mesmo lugar) | Passo 4, logo abaixo do herói: "O que vale mais para você?" = as abas de `cenarios.js`, que passam a gravar `prioridade`. **Condição:** o número grande do herói fica sempre no típico (p50). | garantir em ano de alerta; senão equilibrar |
| `bolso.raiz` | **ajuste fechado + suposição à vista** | mover 5 · opcional 5 (mesmo lugar) | "Ajustar a conta" (fechado). A linha sob o título diz "raiz a R$ 0,84/kg (comum no CE)". | `uf_mediana` (comum do estado) |
| `bolso.custo` | **ajuste fechado + suposição à vista, rótulo honesto** | opcional 6 · fundir 4 (01, 02, 04, 07) | "Ajustar a conta": "Só a semente" / "Semente, trator, adubo e diária (CONAB)". Linha à vista sob o título: "Conta com: só a semente · …". | só a semente |
| `bolso.gs` | **cortar** | cortar 9 · inferir 1 (02) | Uma linha no "Leve para o técnico": paga com perda de 40% ou mais; até 5 ha o tamanho cabe; renda e adesão do município se conferem no sindicato. | não perguntado |
| `criacao` (nova, do 05) | **não entra** | a favor 0 · contra 10 (o 05 mudou) | Texto fixo: forragem "vira comida da criação (fora do R$)" no lugar de "não vende". | não perguntada |
| terra "rasa/piçarra" | **não entra na v1** | contra 9 · a favor 1, se testada (06) | Fica para depois da entrega, com teste nos 7 municípios. | — |

Resultado: **4 perguntas no caminho** (todas já marcadas), **5 ajustes de 1 toque onde agem** (2025, maniva, ano que quebrou, água no técnico, prioridade), **3 ajustes fechados** em "Ajustar a conta" (custo, raiz, arranjo). Saem 6 itens.

---

## 3. O fluxo final, tela a tela

### 3.0 Decisões de fluxo (votos)

| Decisão | Votos | Escolha |
|---|---|---|
| Entrar direto em `#/<cod>/2` pelo globo | a favor 9 · indiferente 1 (08) | **sim** |
| Tela única × uma pergunta por tela | tela única 9 · uma por tela 1 (07) | **tela única, sem avanço automático** |
| Renumerar as rotas | 0 (o 02 retirou) | **não**: muda só a ordem das pílulas |
| Passo 1 na frente (curto) × fora do caminho | fora 9 · indiferente 1 (08) | **fora: "Do espaço", a 1 toque** |
| Tela "Afinar" separada | contra 6 (02, 03, 04, 05, 06, 08) · a favor 4 (01, 07, 09, 10) | **não**: "Sua roça" é o afinar |
| Abas fixas embaixo | contra na v1 8 · a favor 2 (06 no topo, 10 se der) | **as pílulas do topo fazem o papel de abas** |
| Número grande do passo 4 sempre no típico | a favor 8 · sem voto 2 | **sim** |
| "E se chover…" à vista no passo 5 | à vista 7 · ver mais 2 (05, 08) · neutro 1 | **à vista, aberto em 100%** |
| Selo com o nome da fonte (NASA) | a favor 10 | **sim** (`comum.js`) |
| Mexer em `motor.py` para o "não sei" | contra 9 · a favor 1 (08) | **não**: aviso no navegador com `por_solo` |
| Botão "Ouvir", troca de fonte global, página de ciência nova | depois da entrega (todos no debate) | **fora da v1** |

### 3.1 As telas

Medidas a 390 px. Topo fixo ≤ 96 px (marca + lugar ≤ 52, pílulas ≤ 40) e barra de baixo ≤ 64 px. Na tela de 390×844, a área útil fica em cerca de 690 px.
Pílulas no celular: **Roça · Plano · Dinheiro · Seca · Espaço** (no desktop: Sua roça · O plano · Quanto rende · Se secar · Do espaço).
A ordem das pílulas é `[2, 3, 4, 5, 1]`, sem número: o passo atual fica aceso e os anteriores com ✓.

**Tela 0: Globo e painel** (`index.html`). Sem mudança visual. Só o link muda.

```
┌──────────────────────────────────────┐
│ QUADRA              [buscar…]        │
│      (globo 3D → mergulho → mapa)    │
│ ┌──────────────────────────────────┐ │
│ │ Quixadá · Ceará                  │ │
│ │ Inverno 2027: El Niño …          │ │
│ │ [chuva] [estação] [solo]         │ │
│ │ [Montar o plano do meu roçado →] │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```
Botão primário: **"Montar o plano do meu roçado →"**, que leva a `roca.html#/<cod>/2`.

**Tela 1: Sua roça** (`#/<cod>/2`). Uma tela e um botão. Conteúdo ≤ 1.000 px.

```
┌──────────────────────────────────────┐
│ ◉ QUADRA   Quixadá · CE     Trocar   │
│ [Roça] Plano  Dinheiro  Seca  Espaço │
├──────────────────────────────────────┤
│ SUA ROÇA                             │
│ É assim o seu roçado?                │
│ Já marcamos o comum daqui.           │
│ (!) 2027: El Niño forte · solo hoje  │
│     normal   MEDIDO · NASA SMAP      │
│ O que você planta hoje?              │
│ [x Milho ] [x Feijão] [ Mandioca]    │
│ [  Sorgo ] [  Palma ] [ Outra   ]    │
│ ███████████░░░░░░░░░ milho ½ feij. ½ │
│ + quanto de cada                     │
│ Tamanho: 1 ha · típico daqui  SUPOS. │
│ [½] [1] [2] [3] [5 ha]  ≈ 3 tarefas  │
│ + outra medida (tarefas, metros)     │
│ Quando chove forte, a sua terra…     │
│ [Seca rápido ] [Segura a umidade]    │
├──────────── dobra 390×844 ───────────┤
│ [Encharca    ] [x Não sei       ]    │
│ olho: aperte um torrão molhado…      │
│ Tem baixio? A parte baixa e úmida.   │
│ [Não tenho][Pequeno][Grande][x N.sei]│
│ O QUADRA ajuda. Quem decide é você,  │
│ com o técnico.                       │
├──────────────────────────────────────┤
│ [← Mapa]      [ Ver o meu plano → ]  │
└──────────────────────────────────────┘
```
- Cada toque só muda o rascunho da tela: não grava, não chama a API e não avança. **"Ver o meu plano →"** grava uma vez só, e só as linhas tocadas (`location.hash = ctx.link(3, patch)`, que entra no histórico). Depois disso o botão fica desligado até a tela mudar.
- Quem chegou por um "mudar" (`data-editar`) vê a linha dele em foco, e o botão muda para **"Voltar a <passo> →"**.
- Botão primário: **"Ver o meu plano →"**.

**Tela 2: Plano** (`#/<cod>/3`). Conteúdo ≤ 2.400 px.

```
┌──────────────────────────────────────┐
│ ◉ QUADRA   Quixadá · CE     Trocar   │
│  Roça [Plano] Dinheiro  Seca  Espaço │
│ 1 ha (típico) · milho e feijão ·Mudar│
├──────────────────────────────────────┤
│ COMO PLANTAR                         │
│ Plante em faixas.                    │
│ Cada ano, cada cultura muda de lugar.│
│ (v) Agora: junte semente de caupi e  │
│     maniva; nada de fogo.            │
│ SEU ROÇADO VISTO DE CIMA [27][28][29]│
│ ┌──────────────────────────────┐     │
│ │ A  mandioca                  │     │
│ │ B  caupi                     │     │
│ │ C  sorgo forrageiro          │     │
│ │ ·· baixio: milho, se tiver ··│     │
│ └──────────────────────────────┘     │
├──────────── dobra ───────────────────┤
│ Mandioca (Parte A):                  │
│ [x Consigo maniva] [Já tenho no chão]│
│ [Não consigo]                        │
│ O QUE FAZER E QUANDO   MEDIDO · ZARC │
│ Sua terra: não sei · mudar           │
│ [cartões: agora → fev → mar → mai]   │
│ Datas para roça de chuva. Molha a    │
│ roça? Fale com o técnico.            │
│ POR ONDE COMEÇAR O SEU GIRO  SUPOS.  │
│ Se o milho repetiu no mesmo chão:    │
│ comece com o caupi ali.              │
│ [Foi no mesmo lugar] [Mudei de lugar]│
│ POR QUE ESTE PLANO                   │
│ + Onde o seu roçado sofre mais       │
│ + Por que em faixas: a praga anda    │
│   menos                              │
│ + O que cada planta faz pelo solo    │
├──────────────────────────────────────┤
│ [←]             [ Quanto rende → ]   │
└──────────────────────────────────────┘
```
Botão primário: **"Quanto rende →"**.

**Tela 3: Dinheiro** (`#/<cod>/4`). Conteúdo ≤ 2.200 px. Nenhum controle antes do número.

```
┌──────────────────────────────────────┐
│  Roça  Plano [Dinheiro] Seca  Espaço │
│ 1 ha (típico) · milho e feijão ·Mudar│
├──────────────────────────────────────┤
│ QUANTO RENDE                         │
│ Hoje, melhor e ideal.                │
│ Do seu jeito ao plano completo.      │
│ Conta com: só a semente · raiz       │
│ R$ 0,84/kg (comum no CE) · ajustar   │
│ EM 3 ANOS · SOBRA     PROJEÇÃO · IBGE│
│  R$ 2.480   R$ 4.190   R$ 4.360      │
│   ██         ████       █████        │
│  Hoje   →  Melhor  →  Ideal          │
│  ruim 984  ruim 2.490 ruim 2.760     │
│ Hoje: milho + feijão, tudo junto     │
│ (o comum daqui) · mudar              │
├──────────── dobra ───────────────────┤
│ MELHOR: o seu jeito com ajustes      │
│ 1 Plante na janela          +R$ …    │
│ 2 Em cima, feijão no lugar          │
│   do milho                  +R$ …    │
│ 3 Um pedaço de mandioca     +R$ …    │
│ IDEAL: o plano completo · R$ 4.360   │
│ O QUE VALE MAIS PARA VOCÊ?           │
│ [Água] [Renda] [Solo] [x Plano]      │
│ (faixa do jeito aceso + comparação)  │
│ + Ajustar a conta                    │
│ + Se 2027 for como os El Niños fortes│
│ + Quando o dinheiro entra            │
│ + A colheita paga o gasto?           │
│ + Ver como calculamos                │
├──────────────────────────────────────┤
│ [←]             [ E se secar? → ]    │
└──────────────────────────────────────┘
```
"Ajustar a conta" (fechado) tem três linhas: "O que entra na conta: Só a semente / Semente, trator, adubo e diária (CONAB)", "Preço da raiz: daqui · comum no CE · baixo" (só com mandioca) e "Como fica no roçado: Tudo junto · Em pedaços · Milho no baixio". Tem também o link "Mudar o que planta ou quanto de cada", que abre Sua roça na linha 1.
Botão primário: **"E se secar? →"**.

**Tela 4: Se secar** (`#/<cod>/5`). Conteúdo ≤ 2.400 px.

```
┌──────────────────────────────────────┐
│  Roça  Plano  Dinheiro [Seca] Espaço │
│ 1 ha (típico) · milho e feijão ·Mudar│
├──────────────────────────────────────┤
│ SE SECAR                             │
│ 2027 tende a ser apertado.           │
│ 2028 e 2029 voltam ao normal daqui.  │
│ Olhe a terra em 19/mar e 30/abr e    │
│ decida com o técnico.                │
│ 2027, CADA CULTURA   PROJEÇÃO · IBGE │
│ milho    quebra em 6 de 10 ■■■■■■□□□□│
│ caupi    quebra em 3 de 10 ■■■□□□□□□□│
│ mandioca quebra em 1 de 10 ■□□□□□□□□□│
│ + Cada cultura, 2027 a 2029          │
│ E SE CHOVER…      MEDIDO · NASA GPM  │
│ 100% da chuva normal                 │
├──────────── dobra ───────────────────┤
│ ────────────●─────────               │
│ [seca forte][El Niño][normal][boa]   │
│ milho … sacos/ha · caupi … · mand. … │
│ O QUE VAMOS OLHAR: 19/mar e 30/abr   │
│ A SUA MEMÓRIA E OS DADOS             │
│ Lembra de um ano que quebrou?        │
│ Milho:  [1998] [2016] [2012] [outro] │
│ Feijão: [2012] [1998] [2025] [outro] │
│ LEVE PARA O TÉCNICO                  │
│ 6 perguntas  [ ] [ ] [ ] …           │
│ Além da chuva: [barreiro] [poço]     │
│ Garantia-Safra: paga com perda de    │
│ 40% ou mais · confira no sindicato   │
│ [Imprimir]  [Copiar o texto]         │
│ + Ver quanto este cálculo já acertou │
├──────────────────────────────────────┤
│ [←]          [ Mandar no WhatsApp ]  │
└──────────────────────────────────────┘
```
Botão primário: **"Mandar no WhatsApp"**, que chama `compartilhar(ctx)` de `leve_ao_tecnico.js`: `navigator.share`; se não houver, `https://wa.me/?text=…`; se não houver, copia o texto. "Outro lugar" vira link pequeno no fim.

**Tela 5: Do espaço** (`#/<cod>/1`, opcional, pela pílula "Espaço"). Conteúdo ≤ 2.800 px (hoje 4.550).

```
┌──────────────────────────────────────┐
│  Roça  Plano  Dinheiro  Seca [Espaço]│
├──────────────────────────────────────┤
│ DO ESPAÇO                            │
│ Quixadá, CE.                         │
│ Veja o que a terra daqui aceita.     │
│ (!) El Niño forte: chuva fraca em    │
│     7 de 10 municípios do CE         │
│ [mar +2,5 °C ] [chuva chega 18/01]   │
│ [chove jan–abr] [solo hoje normal]   │
│ TENDÊNCIAS (grade 2 colunas)         │
├──────────── dobra ───────────────────┤
│ 11 culturas servem aqui (6 ícones)   │
│ + Ver todas                          │
│ Confiança dos dados: alta · por quê  │
│ + O ano da chuva aqui                │
│ + De onde vêm os dados (satélites)   │
│ Quanto o cálculo já acertou → Seca   │
├──────────────────────────────────────┤
│ [←]          [ Ver o meu plano → ]   │
└──────────────────────────────────────┘
```
Botão primário: **"Ver o meu plano →"**, que leva ao passo 3.

**Contagem:** antes eram 14 toques no mínimo do painel ao plano (25 a 30 respondendo), 13 telas antes do plano e 18 na jornada. Agora são **2 toques** com o padrão, **6** respondendo tudo (Montar + mandioca + 3 ha + Encharca + Pequeno + Ver), **1 tela** antes do plano e **6 telas** na jornada (+1 opcional). Altura do caminho principal: de 35.663 px para ≤ 8.000 px.

---

## 4. O que muda em cada passo existente

| Onde | Sai | Vai para "ver mais" | Junta / entra |
|---|---|---|---|
| **Globo e painel** (`principal.js:94`, `rocacerta.js:333`) | nada | — | link `#/<cod>/1` → `#/<cod>/2`. Texto do botão igual, sem número de toques. Opcional: em `index.html`, link "Internet fraca? Entrar sem o globo" → `roca.html` |
| **Casca** (`roca.js`, `roca.html`, `quadra.css`) | a fileira de 5 fichas com "não sei" e água (`roca.js:111-113`); a moldura em 2 linhas na barra do celular; os números das pílulas | — | pílulas na ordem `[2,3,4,5,1]`; ficha em 1 linha ("1 ha (típico) · milho e feijão · Mudar"); 1 primário na barra com o rótulo do destino; delegação `[data-editar]`; rodapé "O QUADRA ajuda. Quem decide é você, com o técnico." no fim de cada passo; toque no selo mostra a fonte; exemplos e busca levam a `/2` (`roca.js:194, 209`) |
| **Passo 2 "Sua roça"** (`perguntas.js`) | 11 telas, resumo "Pronto", 3 contadores, "Anterior/Pular/Pronto/Terminar", estado `fase/q/telaForcada`, telas de arranjo, manejo, anos, deu-bem, o-que-faz, água e maniva | "quanto de cada" e "outra medida" (fechados na própria tela) | 1 tela com 4 linhas, rascunho local e 1 gravação; faixa de 1 linha do El Niño. Os modos "pergunta" de `hoje_ideal.js` e `historico.js` continuam no código (páginas de teste e Plano B), mas saem da jornada |
| **Passo 3 "Plano"** (`plantio.js`) | o "Mudar" da abertura (a ficha da casca faz isso); o CTA "Ver quanto rende" (`plantio.js:505`) | vulnerabilidade, "Por que em faixas" (`blocoFaixas`) e `saude_solo` em 3 sanfonas com título-manchete; o calendário completo continua no "ver mais" | faixa "Agora: …" sob o título; linha da maniva sob o desenho; chip "Sua terra · mudar" e aviso honesto do "não sei" em "O que fazer e quando"; linha fixa de sequeiro; cartão do giro com 2 chips |
| **Passo 4 "Dinheiro"** (`dinheiro.js`, `hoje_ideal.js`, `cenarios.js`) | "Seu bolso" no topo; o 2º herói "No caso ruim… O plano × Jeito de hoje" (`heroiHtml`); o controle do Garantia-Safra; o chip de área; os chips "à frente de hoje em N de 100" na frente; a troca do número grande por p10 em "garantir" | El Niño ("Se 2027 for como…"), caixa, "paga o gasto?", "Como calculamos" (com os 28 anos e a tabela "à frente") | linha de suposições sob o título; herói H/M/I com o típico em destaque; Melhor aberto (≤ 3 ajustes) e Hoje e Ideal em 1 linha cada; "O que vale mais para você?" = abas de cenários gravando `prioridade`; "Ajustar a conta" com custo, raiz e arranjo; h1 neutro "Hoje, melhor e ideal." |
| **Passo 5 "Se secar"** (`seguranca.js`, `leve_ao_tecnico.js`, `cenario_chuva.js`) | "Contar o meu ano ruim" (ia ao passo 2); "acima do recorde"; o verde "Copiar para o WhatsApp" dentro do bloco | `blocoHoje` inteiro ("Ver os detalhes de hoje"); régua dos anos e cartões completos por cultura ("Cada cultura, 2027 a 2029"); limites e métodos (como hoje) | 1 linha por cultura (2027, grade de 10); "E se chover…" aberto em 100%; memória respondida ali; chips de água e linha do Garantia-Safra no técnico; `compartilhar(ctx)` |
| **Passo 1 "Do espaço"** (`lugar.js`) | "Responder 5 perguntas" e "Pular…" (`lugar.js:148-149`); "muito forte" (`lugar.js:86`) | régua "O ano da chuva aqui"; cardápio além das 6 primeiras ("Ver todas") | kicker "Do espaço"; linha "Quanto o cálculo já acertou → Se secar"; tendências em grade; texto "qualquer terra" (`lugar.js:116`) corrigido |
| **Selo** (`comum.js:24-27`) | — | — | "MEDIDO · NASA SMAP", "PROJEÇÃO · IBGE" (fonte curta ≤ 10 caracteres, tirada da própria fonte); `data-fonte` + `tabindex=0` para o toque |

---

## 5. Regras de navegação e visuais

**Navegação**
- **Um indicador de progresso:** as pílulas do topo, sem número. Nenhum "n de m" em lugar nenhum: saem `quiz-barra`, `hi-barra` e `hs-barra` da jornada.
- **Um botão primário (verde) por tela**, sempre o `#avancar` da barra de baixo, com o nome do destino:
  - Sua roça: "Ver o meu plano →", ou "Voltar a <passo> →" quem veio de um "mudar"
  - Plano: "Quanto rende →"
  - Dinheiro: "E se secar? →"
  - Se secar: "Mandar no WhatsApp"
  - Do espaço: "Ver o meu plano →"

  Dentro do conteúdo tudo é `.botao.secundario`, chip ou link.
- **Voltar:** "←" na barra vai ao anterior na ordem `[2,3,4,5,1]`; em Sua roça vira "← Mapa" (`index.html`). Cada passo é uma entrada no histórico (`location.hash =`), e as respostas usam `location.replace`, então o voltar do Android recua um passo.
- **"Mudar"** = qualquer elemento com `data-editar="hoje|ha|terra|baixio"`. Ele abre Sua roça com a linha em foco e guarda a volta (`ctx.volta`, `ctx.foco`). Se a página for recarregada, cai no padrão "Ver o meu plano" (aceito).
- **Nada avança sozinho.** O primário se desliga no 1º toque até a tela mudar (o bug do toque duplo, `perguntas.js:115-120`, some com o avanço automático).
- **Padrão ≠ resposta:** só o que foi tocado vai para a URL. O resto aparece como "típico daqui", "o comum daqui" ou "não sei" e vira pergunta ao técnico.

**Visual (mínimo nesta rodada; a troca de fonte global fica para depois)**
- `.eco` com `--ink-3` (contraste ≥ 4,5:1); `summary` com `min-height: 44px`; alvos do caminho principal ≥ 44 px; selo com 11 px e `white-space: nowrap`.
- Topo fixo ≤ 96 px e barra de baixo ≤ 64 px a 390 px. No celular, a frase do ponto 16 sai da barra e vira o rodapé de cada passo; no desktop continua na barra.
- Nada rola de lado na página (`scrollWidth ≤ innerWidth`). Os carrosséis que ficam à vista viram grade: tendências; e saúde do solo, que vai para um "ver mais".
- No máximo 2 "SEU OLHO" à vista por tela.
- Na frente, o El Niño tem um rótulo só: "El Niño forte". O fato do mar é "o mar mais quente de ago–out desde 1950". O texto técnico do motor (`texto_oni`) fica só no "ver mais".
- Frases proibidas na frente: "5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde", "uso as datas que servem em qualquer terra", "As datas valem para qualquer terra", "sem preço aqui", "ainda não vende(m)" (forragem), "você cabe" sem ressalva, "à frente em N de 100".

**Limites medíveis (a 390 px, com todo "ver mais" fechado)**

| Tela | Altura máx. (scrollHeight) | Palavras à vista (meta / teto) | Outro |
|---|---|---|---|
| Sua roça | 1.000 px | 70 / 100 | a linha da terra começa acima da dobra a 390×844 |
| Plano | 2.400 px | 200 / 300 | "Agora" ≤ 400 px do topo; o desenho começa ≤ 550 px |
| Dinheiro | 2.200 px | 180 / 260 | o gráfico H/M/I começa ≤ 450 px, sem controle antes |
| Se secar | 2.400 px | 200 / 300 | as linhas de 2027 e o título de "E se chover…" ≤ 900 px |
| Do espaço | 2.800 px | 250 / 320 | sem CTA de perguntas |
| Toques do painel até o plano | 2 com o padrão; ≤ 6 respondendo tudo | — | 1 tela antes do plano |

---

## 6. Onde fica cada um dos 16 pontos

| Ponto | Onde fica depois da mudança |
|---|---|
| 1. Temperatura, umidade, chuva, evaporação × vulnerabilidade e solo | Globo (camadas Solo, Calor, Água guardada); Do espaço (indicadores, tendências); Plano › "Onde o seu roçado sofre mais" (manchete à vista) |
| 2. Termos científicos | Balão "o que é?" do glossário em todos os passos; glossário em Do espaço |
| 3. Satélite × medida no chão | Do espaço › "De onde vêm os dados" (`satelite_chao`, `harmonizacao`); o selo agora diz o satélite |
| 4. Comparar abordagens | Se secar › "Ver quanto este cálculo já acertou" (7 jeitos, acerto em 100); link a partir de Do espaço |
| 5. Transições sazonais, campo despido, estresse | Plano (roçado mês a mês com "descanso", "O que fazer e quando"); Do espaço › "O ano da chuva aqui" |
| 6. Incerteza e saber local | Selos em todo número; grade de 10 roças (Se secar); "E se chover…"; confiança (Do espaço); memória × IBGE; "SEU OLHO" |
| 7. Harmonização numa grade comum | Do espaço › "De onde vêm os dados" (`harmonizacao`) |
| 8. Comparar cenários de rotação | Dinheiro › "O que vale mais para você?" (cenários, à vista) e H/M/I; Plano › "Por que em faixas: a praga anda menos" |
| 9. Ideias × prioridades | Dinheiro › abas de cenários = `prioridade` (Água · Renda · Solo · Plano) |
| 10. Fixadoras, cobertura, raízes | Plano › "O que cada planta faz pelo solo" (manchete à vista) |
| 11. Mapas no tempo | Globo (camadas com controle de tempo); Do espaço (tendências) |
| 12. Vulnerabilidade no campo | Plano › "Onde o seu roçado sofre mais" (desenho do roçado com erosão e água) |
| 13. Controles de cenário | Se secar › "E se chover…" (aberto); Plano mês a mês |
| 14. Fácil para quem lê pouco | Uma tela de perguntas, um botão, ícones e palavras da roça; limites da seção 5 |
| 15. Prioridades e restrições (água, equipamento, mercado) | Mercado: prioridade "Renda" e preço da raiz. Equipamento: "Semente, trator, adubo e diária", com a suposição à vista. Água: chips no técnico + linha de sequeiro nas datas. Tamanho e baixio: em Sua roça |
| 16. Apoia e não substitui | Rodapé fixo em cada tela; 1ª dobra de Se secar ("decida com o técnico"); "Leve para o técnico" + WhatsApp como fim; memória ("vale a sua"); "SEU OLHO" |

Os três pedidos do José continuam no caminho e à vista:
- **jeito de hoje:** Sua roça linha 1 e o herói H/M/I;
- **área em ha, tarefa ou medida:** Sua roça linha 2 e "outra medida";
- **histórico:** 2025 no cartão do giro e o ano que quebrou na memória, os dois respondidos com 1 toque.

---

## 7. Plano de implementação (5 construtores, arquivos sem sobreposição)

**Regra:** cada dono só toca os arquivos da sua linha. Os contratos entre donos estão no fim da seção. Nenhum dono toca `nucleo/`,
`servidor.py`, `calculo.js` e `graficos.js`. Os modos "pergunta" de `hoje_ideal.js` e `historico.js` ficam no código (páginas `web/teste/` e Plano B):
não apagar, só listar como órfãos no relatório.

### Ordem

- **0:00–0:10:** o Integrador tira a linha de base (I0) e B faz o B0 (export).
- **0:10–2:30:** A, B, C, D e E trabalham em paralelo, cada um na ordem das suas tarefas.
- **2:30–3:30:** o Integrador junta e confere.
- **Folga até 4 h 30.**
- **Plano B, se às 1:45 a tela única de A não estiver de pé:** `perguntas.js` começa em `fase = "perguntas"` e pula hoje e histórico; abre com a tela de culturas de `HI` e depois terra, tamanho e baixio; tira água e maniva; a última resposta chama `ctx.ir(3)`, sem resumo; trava o toque duplo. Leva uns 30 min.

### A: casca e "Sua roça" (≈ 2 h 30)

Arquivos: `web/roca.html`, `web/js/roca.js`, `web/css/quadra.css`, `web/js/passos/perguntas.js`, `web/css/passos/perguntas.css`,
`web/js/extras/area.js`, `web/js/globo/principal.js`, `web/js/globo/rocacerta.js`, `web/index.html` (só o link opcional).

1. **Entrada (15 min).** `principal.js:94` e `rocacerta.js:333` passam a usar `/${cod}/2`; `roca.js:194` (exemplos) e `:209` (busca), `/2`.
2. **Tela única (75 min).** Reescrever `perguntas.js`:
   - Estado: rascunho `{hoje, ha, area_un, terra, baixio, maniva}` e o conjunto `tocado`, refeitos quando `ctx.entrou`.
   - Linha 1: chips de `opcoesCultura(ctx.r)` com `CULT`, barra `hi-divisao` e "+ quanto de cada" (`mexer`/`igual`), tudo de `hoje_ideal.js`.
   - Linha 2: valor típico com selo SUPOSIÇÃO, chips ½·1·2·3·5, "≈ N tarefas" (`tarefaPadrao`) e `<details>` "+ outra medida", que roda `AREA.render(slot, ctxRascunho, {semTitulo: true})`. `ctxRascunho` = `{...ctx, resp: {...ctx.resp, ...rasc}, entrou: false, set: (p) => {Object.assign(rasc, p); tocado.add("ha"); redesenhar();}}`.
   - Linha 3: terra com 4 opções (`arenosa`, `mista`, `barro`, `""`) e `OLHOS.terra` em 1 linha. O "Não sei" sem "qualquer terra" (`perguntas.js:25`).
   - Linha 4: baixio com 4 opções (`nao`, `pouco`, `metade`, `""`) e `miniRocado`.
   - Faixa de 1 linha do El Niño e do solo, com `U.selo("medido", "<ONI NOAA; solo NASA SMAP L4>")`.
   - `hoje` grava **só as culturas** (`"milho:34,feijao:33,mandioca:33"`). Não usar `escreverHoje` sobre um `lerHoje("")`: ele escreveria `|cons=1|1chuva=1|sem=1`, o padrão posto como resposta (o defeito de `hoje_ideal.js:442`). Quem já tinha chaves no `hoje` mantém as chaves dele.
   - Maniva: se a mandioca foi marcada e `resp.maniva === ""`, o patch leva `maniva: "plantada"`; se foi desmarcada e era `"plantada"`, leva `maniva: ""`.
   - Botão: `ctx.primario("Ver o meu plano →", () => location.hash = ctx.link(ctx.volta || 3, patch))`, com `patch` só das linhas tocadas.
   - `ctx.foco`: rola até `#linha-<k>` e destaca a linha.
   - Saem `fase`, `q`, `telaForcada`, `resumo()` e o contador.
3. **roca.js (40 min).**
   - `ORDEM = [2,3,4,5,1]` e `curto` nas pílulas, que perdem o número.
   - `ctx.primario(rotulo, fn)`, zerado a cada `desenhar()`, e o rótulo padrão por passo (seção 5).
   - No passo 5, o primário faz `import("./extras/leve_ao_tecnico.js").then(m => m.compartilhar(ctx))`.
   - Voltar pela ORDEM, com "← Mapa" no passo 2.
   - Clique em `[data-editar]`: guarda `volta = estado.passo` e `foco = k`, e faz `location.hash = link(2)`.
   - `ctx.volta` e `ctx.foco` passam a existir no ctx.
   - Ficha em 1 linha, com `descHoje(lerHoje(...))` de `hoje_ideal.js`, o ha com "(típico)" e "Mudar" (`data-editar="hoje"`).
   - Rodapé `.decide-fim` depois do `caixa`, com o link ao técnico (a lógica do `#moldura` que já existe).
   - Clique em `.selo[data-fonte]`: balão fixo com a fonte por 5 s.
4. **quadra.css (20 min).**
   - `.eco` → `var(--ink-3)`, `summary` ≥ 44 px, `.selo` 11 px e `nowrap`.
   - Topo e pílulas ≤ 96 px a 390; `.nav-baixo` em 1 linha ≤ 64 px, com a moldura escondida ≤ 760 px.
   - `.ficha` em 1 linha, `.decide-fim`, balão do selo e estado desligado do primário.
5. **area.js (10 min).** O selo do típico (`area.js:131`) passa de MEDIDO para SUPOSIÇÃO ("típico do município no Censo 2017, aplicado ao seu roçado").
6. **Opcional.**
   - `index.html`: "Internet fraca? Entrar sem o globo".
   - Gravar `sessionStorage["quadra.antes"]` = janelas atuais ao tocar "Ver o meu plano", com try/catch, para o "antes:" do C.

### B: Dinheiro (≈ 2 h)

Arquivos: `web/js/passos/dinheiro.js`, `web/css/passos/dinheiro.css`, `web/js/extras/hoje_ideal.js`, `web/css/extras/hoje_ideal.css`,
`web/js/extras/cenarios.js`, `web/css/extras/cenarios.css`.

0. **Primeiro, 5 min.** No fim de `hoje_ideal.js`: `export { CULT, igual, mexer, opcoesCultura };`. A depende disso.
1. **dinheiro.js, ordem nova (50 min).**
   - Ordem: `abertura("Hoje, melhor e ideal.", "Do seu jeito ao plano completo.", apoio)` → linha de suposições ("Conta com: só a semente · raiz R$ x/kg (comum no UF) · ajustar", em que "ajustar" abre e rola até `#ajustar-conta`) → `hi-slot` → `jeitos` (cenários) → `<details id="ajustar-conta">` "Ajustar a conta" → verMais de El Niño, caixa e termo → "Ver como calculamos".
   - "Ajustar a conta" tem: custo "Só a semente / Semente, trator, adubo e diária (CONAB)"; raiz, só com mandioca, com `OLHOS.preco_raiz`; arranjo "Tudo junto / Em pedaços / Milho no baixio", gravando `hoje` com `escreverHoje`; e o link `data-editar="hoje"`.
   - Remover `bolsoHtml` (seg de prioridade, chip de área e seg do Garantia-Safra) e `heroiHtml`. O `replayHtml` ("os 28 anos") vai para "Ver como calculamos".
   - `dinheiro.js:210`: "El Niño muito forte" → "El Niño forte".
   - `semVendaEm`, frase `:205-206`: "ainda não vende(m)" → "a maniva ainda não colhe; o sorgo vira comida da criação (fora do R$)".
   - `dinheiro.js:140`: "sem preço aqui" → "comida da criação, fora do R$".
2. **hoje_ideal.js, modo comparação (40 min).**
   - `numeros()` sempre com p50 em destaque e "caso ruim" pequeno (sem `garantir`).
   - Melhor aberto com até 3 ajustes; o resto em "Mais N ajustes".
   - Hoje e Ideal em 1 linha cada (descrição + típico + caso ruim), com o `planoMini` do Ideal.
   - `frente()` sai da frente; a coluna "à frente de hoje" continua na tabela de `detalhes()`.
   - `chipHoje`: "milho + feijão, tudo junto (o comum daqui) · mudar", com `data-editar="hoje"`.
   - `TXT_AJ.baixio` e `:300`: "Em cima, feijão no lugar do milho (o milho fica no baixio)."
   - `:567` e `:616`: "sem preço aqui" → "comida da criação, fora do R$".
3. **cenarios.js (20 min).**
   - Rótulo "O que vale mais para você?".
   - O clique em `[data-jeito]` faz `ctx.set({prioridade: INV[jeito]})`, com `INV = {agua: "garantir", renda: "vender", solo: "solo", plano: "equilibrar"}`, no lugar de `est.escolha`.
   - Se o bloco passar de ~700 px a 390, `grade` e `giro` vão para `U.verMais(..., "Ver a comparação")`, e a faixa e as abas ficam à vista.
4. **CSS (10 min).** Cartões Hoje e Ideal em linha; nada de cartão dentro de cartão no Melhor.

### C: Plano e histórico (≈ 2 h)

Arquivos: `web/js/passos/plantio.js`, `web/js/passos/plantio/calendario.js`, `web/js/passos/plantio/desenho.js` (só se precisar),
`web/css/passos/plantio.css`, `web/js/extras/historico.js`, `web/css/extras/area_historico.css`, `web/css/extras/saude_solo.css`,
`web/css/extras/vulnerabilidade.css`.

1. **plantio.js, ordem (45 min).**
   - Ordem: `abertura` (sem o link "Mudar", `plantio.js:71`) → faixa "Agora: …" (nova `export function agora(ctx)` em `calendario.js`, a mesma frase do 1º cartão de `linhaDoTempo`) → `heroi` → linha da maniva → `blocoTempo` → cartão do giro → seção "Por que este plano" com 3 `U.verMais`.
   - Linha da maniva: só se alguma parte tem Mandioca ou se `ef.maniva === "nao"`. São 3 chips, `ctx.set({maniva: "" | "plantada" | "nao"})`; com "nao", mostra "Sem maniva: a mandioca saiu do plano · voltar".
   - As 3 sanfonas: "Onde o seu roçado sofre mais" (vulnerabilidade), "Por que em faixas: a praga anda menos" (`blocoFaixas`) e "O que cada planta faz pelo solo" (`saude_solo`).
   - Sai o CTA `plantio.js:505`.
2. **blocoTempo (25 min).**
   - Chip "Sua terra: <rótulo> · mudar" com `data-editar="terra"`.
   - Se `ef.terra === "nao_sei"`: para cada cultura do plano cujo `cardapio[].por_solo` não tenha solo arenoso (cod 1 ou 12), uma linha "Em terra de areia, o <cultura> não tem data do ZARC aqui." Ex.: feijão comum em Quixadá; milho em Piritiba (2924801).
   - Linha fixa de sequeiro.
3. **historico.js, cartão (25 min).**
   - Sem `resp.antes`, usar `anos = {2026: ks, 2025: ks}` do jeito de hoje e mostrar as recomendações com o prefixo "Se em 2025 também foi assim:" e `U.selo("suposicao", …)`.
   - Chips: "Foi no mesmo lugar" → `ctx.set({antes: "2026:ks|2025:ks"})`; "Mudei de lugar" → `ctx.set({antes: "2026:ks"})`, que dá "Nada repetiu: siga a ordem A, B, C".
   - Sai o "Contar" (`historico.js:366`).
4. **historico.js, memória (20 min).**
   - Sem quebra contada: por cultura (milho, feijão), chips dos 3 piores anos (`piores()`) e "outro ano" (`<select>` 1998–2025). O toque faz `ctx.set({exp: escreverExp({...e, quebras: [...e.quebras, {c, ano}]})})`.
   - Sai "Contar o meu ano ruim" (`historico.js:420`).
5. **CSS (10 min).** O carrossel `ss-cartoes` vira grade de 2 colunas. No máximo 2 "SEU OLHO" à vista.
6. **Opcional.** "antes: …" ao lado da data que mudou, lendo `sessionStorage["quadra.antes"]` com try/catch.

### D: Se secar e técnico (≈ 1 h 45)

Arquivos: `web/js/passos/seguranca.js`, `web/css/passos/seguranca.css`, `web/js/extras/leve_ao_tecnico.js`, `web/js/extras/voce_decide.js`,
`web/css/extras/voce_decide.css`, `web/js/extras/cenario_chuva.js`, `web/css/extras/cenario_chuva.css`.

1. **seguranca.js, ordem (50 min).**
   - Ordem: `abertura` + linha "Olhe a terra em 19/mar e 30/abr e decida com o técnico." → bloco "2027, cada cultura" → `blocoCenario` → `blocoPortoes` → `U.extra("historico", {modo: "memoria"})` → `U.extra("leve_ao_tecnico")` → `blocoLimites`.
   - O bloco "2027, cada cultura" tem uma linha por cultura: ícone, "quebra em X de 10" e `dezRocas(d.anos["2027"].quebra)`, com 1 selo PROJEÇÃO. Embaixo, `U.verMais(reguaAnos + cartões completos, "Cada cultura, 2027 a 2029")`.
   - `blocoHoje` inteiro vai para `U.verMais(…, "Ver os detalhes de hoje")`.
   - `seguranca.js:219`: "mar quente, acima do recorde" → "o mar mais quente de ago–out desde 1950".
2. **cenario_chuva.js (5 min).** `:306`: `tela.x ??= 100`. O chip "anos de El Niño" continua a 1 toque.
3. **leve_ao_tecnico.js (40 min).**
   - `export async function compartilhar(ctx)`: monta `texto()` como no render, tenta `navigator.share({text})`, depois `window.open("https://wa.me/?text=" + encodeURIComponent(t))`, e por último `copiar(t)` com o aviso.
   - O botão "Copiar para o WhatsApp" vira `.botao.secundario` "Copiar o texto".
   - Chips de água: `ctx.set({agua: "barreiro" | "irriga" | ""})`, sem a cisterna.
   - Linha do Garantia-Safra: "paga com perda de 40% ou mais; até 5 ha o tamanho cabe; renda da família e adesão do município: confira no sindicato".
   - `:66`: "na casa de farinha daqui" passa a usar o rótulo da opção escolhida ("comum no CE" por padrão).
4. **voce_decide.js (10 min).** `OLHOS.terra` em ≤ 12 palavras (o torrão), porque vai na tela única.

### E: Do espaço e selo NASA (≈ 1 h 30)

Arquivos: `web/js/passos/lugar.js`, `web/css/passos/lugar.css`, `web/js/comum.js`, `web/js/extras/tendencias.js`,
`web/css/extras/tendencias.css`, `web/js/extras/glossario.js`.

1. **comum.js `selo()` (25 min).**
   - Fonte curta, pela 1ª que aparecer no texto da fonte: SMAP → "NASA SMAP"; GPM ou IMERG → "NASA GPM"; POWER → "NASA POWER"; GRACE → "NASA GRACE"; MODIS → "NASA MODIS"; VIIRS → "NASA VIIRS"; ECOSTRESS; ONI ou NOAA → "NOAA"; ZARC → "ZARC"; CONAB; PAM, IBGE ou Censo → "IBGE"; GAEZ → "FAO". Para MEDIDO e PROJEÇÃO, o rótulo vira `MEDIDO · <curta>`; SUPOSIÇÃO fica sem fonte curta.
   - A assinatura não muda. Acrescentar `data-fonte="<fonte>"` e `tabindex="0"`.
2. **lugar.js (40 min).**
   - Kicker "Do espaço"; saem as linhas `148-149`.
   - `:86`: "El Niño muito forte" → "El Niño forte".
   - `regua()` vai para `U.verMais(…, "O ano da chuva aqui")`.
   - `culturas()`: as 6 primeiras à vista e o resto em "Ver todas as N".
   - `:116`: "As datas valem para qualquer terra; no passo 2 elas se ajustam à sua." → "Sem saber a sua terra, as datas são as que servem nos solos onde a cultura tem zoneamento; em Sua roça elas se ajustam à sua."
   - Linha "Quanto o cálculo já acertou" com `ctx.link(5)`.
   - Ordem: El Niño → indicadores → tendências → culturas → confiança → origem.
3. **tendências (15 min).** `tend-grade` vira grade de 2 colunas a ≤ 420 px, sem rolagem lateral.
4. **glossario.js (opcional, 10 min).** O JSON do município só baixa na 1ª abertura do balão.

### Contratos entre donos

| De → para | Contrato |
|---|---|
| B → A | `hoje_ideal.js` exporta `CULT`, `igual`, `mexer` e `opcoesCultura`. `lerHoje`, `escreverHoje` e `descHoje` já são exportados |
| D → A | `leve_ao_tecnico.js` exporta `compartilhar(ctx)` |
| E → A | `selo()` põe `data-fonte` e `tabindex="0"`; A trata o toque e o CSS |
| A → B, C, D | `data-editar="hoje\|ha\|terra\|baixio"` em qualquer "mudar". `ctx.link(2)` continua válido: cai na tela única |
| A → C (opcional) | `sessionStorage["quadra.antes"]` = `{cultura: "dd/mm a dd/mm"}` antes da gravação |

### Integrador (≈ 1 h no fim + 10 min no começo)

- **I0 (antes de tudo).** Tirar a linha de base:
  - `node testes/ferramentas/teste_calculo.mjs > E:/campeonato-nasa/tmp/base_calculo.txt`;
  - `curl` do `/api/local` dos 7 municípios para `E:/campeonato-nasa/tmp/base_api_<cod>.json`.
  
  Os 7 municípios: Quixadá 2311306, Crateús 2304103, Picos 2208007, Caicó 2402006, Petrolina 2611101, Arapiraca 2700300, Barreiras 2903201. Piritiba 2924801 entra só no teste da terra "não sei".
- **I1.** `git diff --stat`: cada arquivo mudado tem que estar na lista do seu dono.
- **I2.** Atualizar `testes/ferramentas/percorrer_fluxo.py` para o fluxo novo:
  - percurso: `#/<cod>/2` → print → clicar `#avancar` → passo 3 → `#avancar` → 4 → `#avancar` → 5 → `#/<cod>/1`;
  - mais o cenário "Seu Antônio": mandioca + 3 ha + Encharca + Pequeno + "Ver o meu plano".
- **I3.** Rodar o script de aceite (seção 8) e `erros_console.py` em cada passo dos 7 municípios. Prints em `E:/campeonato-nasa/tmp/fluxo_novo/<cod>/`.
- **I4.** Conferir os R$ de Quixadá na URL padrão e repetir `teste_calculo.mjs` (saída idêntica à da base).
- **I5.** Atualizar `web/js/passos/LEIA-ME.md`: ordem `[2,3,4,5,1]`, `ctx.primario`, `data-editar`, `ctx.volta`/`ctx.foco`, um primário por tela, a lista de frases proibidas.
- **I6.** Relatório: antes × depois (alturas, palavras, toques), prints das 6 telas a 390 px, pendências e código órfão.

---

## 8. Critérios de aceite

**Por script** (rodar no Edge sem janela a 390×844, em cada tela e nos 7 municípios). A tela passa se todos os campos baterem:

```js
(() => {
  const j = document.getElementById("jornada");
  const vis = (e) => (e.offsetWidth || e.offsetHeight) && !e.closest("details:not([open])");
  const txt = j.innerText;
  return {
    hash: location.hash,
    altura: document.documentElement.scrollHeight,
    palavras: txt.trim().split(/\s+/).length,
    primarios: [...document.querySelectorAll(".botao.primario")].filter(vis).length,          // = 1
    contadores: document.querySelectorAll(".quiz-barra,.hi-barra,.hs-barra").length,          // = 0
    nDeM: /\b\d+ de \d+\b/i.test(document.querySelector(".kicker")?.innerText || ""),         // false
    lateral: document.documentElement.scrollWidth > innerWidth,                              // false
    olhos: [...j.querySelectorAll(".olho")].filter(vis).length,                              // <= 2
    nasa: /NASA/.test(txt),                                                                  // true em Sua roça, Se secar e Do espaço
    proibidas: ["5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde",
      "qualquer terra", "sem preço aqui", "ainda não vende", "à frente de hoje em"].filter((f) => txt.includes(f)), // []
    selosPequenos: [...document.querySelectorAll(".selo")].filter((s) => parseFloat(getComputedStyle(s).fontSize) < 11).length, // 0
    summaryBaixo: [...document.querySelectorAll("summary")].filter((s) => vis(s) && s.getBoundingClientRect().height < 44).length, // 0
  };
})()
```

| # | Critério | Como conferir |
|---|---|---|
| 1 | Passo 2 tem **1 tela**: nenhum `#q-prox`, `#hi-prox` ou `#hs-prox`, e as 4 linhas `#linha-hoje`, `#linha-ha`, `#linha-terra` e `#linha-baixio` | script + print |
| 2 | Do painel ao plano: **2 toques** (clicar `#planoBotao` → clicar `#avancar` dá `#/<cod>/3`) | `percorrer_fluxo.py` |
| 3 | Seu Antônio: mandioca + 3 ha + Encharca + Pequeno + Ver → o hash (decodificado) tem `hoje=milho:34,feijao:33,mandioca:33`, `maniva=plantada`, `ha=3`, `terra=barro`, `baixio=pouco`, e **nada mais** | `percorrer_fluxo.py` |
| 4 | Aceitar o padrão (só "Ver o meu plano") deixa o hash **sem parâmetros**; o passo 4 diz "(o comum daqui)" e a ficha diz "(típico)" | script |
| 5 | Nenhuma tela com 2 barras de progresso ou 2 botões verdes à vista (`contadores = 0`, `primarios = 1`) | script |
| 6 | Alturas e palavras dentro dos tetos da seção 5 (Sua roça ≤ 1.000 px e ≤ 100 palavras; Plano ≤ 2.400 / 300; Dinheiro ≤ 2.200 / 260; Se secar ≤ 2.400 / 300; Do espaço ≤ 2.800 / 320) | script |
| 7 | **Zero erro no console** em cada passo dos 7 municípios | `erros_console.py` |
| 8 | Quixadá, URL padrão `#/2311306/4`: típico Hoje **R$ 2.480**, Melhor **R$ 4.190**, Ideal **R$ 4.360**; caso ruim 984 / 2.490 / 2.760 (iguais a `15_passo4_dinheiro.txt`); `teste_calculo.mjs` com saída idêntica à da base | print + `diff` |
| 9 | O gráfico H/M/I começa ≤ 450 px no passo 4; nenhum `.seg` ou `[data-set]` antes dele | `getBoundingClientRect().top` + `scrollY` |
| 10 | Prioridade: tocar "Renda" nas abas grava `prioridade=vender` e o número grande **não muda** | script antes e depois |
| 11 | Voltar do navegador (`history.back()`) no passo 4 leva ao passo 3, no passo 3 ao 2, e no 2 sai para o globo | script |
| 12 | "Mudar" da ficha (passo 4) abre Sua roça com `#linha-hoje` na tela, e o primário diz "Voltar a Quanto rende →"; tocar nele volta ao passo 4 | print + script |
| 13 | Piritiba (2924801) e Quixadá com terra "não sei": aparece "Em terra de areia, o … não tem data do ZARC aqui."; com `terra=barro` a linha some | print |
| 14 | Passo 3: a linha da maniva aparece quando há mandioca no plano; "Não consigo" grava `maniva=nao` e a mandioca some do desenho | print |
| 15 | Cartão do giro sem `antes`: frase com "Se em 2025…" e selo SUPOSIÇÃO; "Foi no mesmo lugar" grava `antes=2026:milho,feijao\|2025:milho,feijao` | script |
| 16 | Memória: tocar "1998" no milho grava `exp=quebra=milho:1998`, e aparece "O IBGE anotou…" sem sair do passo 5 | script |
| 17 | Passo 5: "E se chover…" abre em 100% ("Com a chuva normal") e as 3 linhas de 2027 ficam acima de 900 px | print |
| 18 | Passo 5: o primário "Mandar no WhatsApp" chama `navigator.share`, ou abre `wa.me`, ou copia; dentro do bloco do técnico não há botão verde | clique no Edge (o `wa.me` pode ser interceptado) |
| 19 | Selo: pelo menos um "MEDIDO · NASA …" visível em Sua roça, Se secar e Do espaço; tocar num selo mostra a fonte | script + print |
| 20 | A 390 px nada rola de lado em nenhuma tela (`lateral = false`), com todos os "ver mais" abertos também | script com `details.open = true` |
| 21 | Links antigos continuam abrindo: `#/2311306/1` (Do espaço) e `#/2311306/3?terra=mista&baixio=terco` (plano com ⅓) | navegar |

**Por print** (6 telas a 390 px, comparadas com `E:/campeonato-nasa/tmp/fluxo_atual/`): uma tela de perguntas no estilo da tela inicial,
com botões grandes com ícone, título fino em dois tons e o verde só na barra de baixo; em cada passo de resultado a resposta aparece na 1ª dobra.

---

## 9. Divergências que ficaram e por que foram vencidas

| Divergência | Lado vencido | Por que |
|---|---|---|
| Uma pergunta por tela, com toque que avança (07; 09 e 05 na 1ª rodada) | 07 | São 3 ou 4 telas para a mesma informação. O avanço automático é a causa medida do pulo do tamanho (`perguntas.js:115-120`), e cada resposta de terra ou baixio refaz a API (cerca de 1 s, 62 KB). A objeção do 07 era a altura (≈ 1.700 px com os cartões atuais), e por isso a tela única usa chips de 48–56 px e tem teto de 1.000 px |
| Baixio com 3 opções (03, 04, 08, 09, 10) × 4 (01, 02, 05, 06, 07), empate 5 × 5 | 3 opções | O mérito decidiu. 4 opções fecham a grade 2×2, não custam toque a mais, usam chaves que já existem (`pouco` e `metade`) e não exigem o controle novo de tamanho no desenho que o lado das 3 opções pressupunha (não cabe no prazo). A API trata os tamanhos igual (`ad_baixio=15`), mas o R$ e o desenho mudam (0,2 × 0,5) |
| Terra sem "Não sei" marcado (07) | 07 | Uma resposta obrigatória sem padrão quebra a linha vermelha "1 toque até o plano". O risco do "não sei" (interseção que esconde cultura não zoneada, achado do 08) fica tratado com o aviso por cultura no plano, com o chip "mudar" ao lado das datas e com a pergunta ao técnico |
| Custo "Paga trator ou adubo? Não/Sim" (01, 02, 04, 06, 07, 09, 10) × rótulo honesto da CONAB (03, 05, 08) | a pergunta sim/não | Ganhou o mérito sobre a contagem: "Sim" ligaria quem só aluga a hora do trator ao desembolso completo (máquina + insumos + serviço), e a sobra iria de R$ 4.364 para −R$ 1.743. O rótulo escolhido cita trator e adubo juntos ("Semente, trator, adubo e diária"), o que mantém a palavra do equipamento (ponto 15). A suposição fica à vista sob o título, como pediam 01, 02, 07 e 08 |
| Prioridade como 1º controle do passo 4 (03, 08 na 1ª rodada) | 03, 08 | Seria controle antes do resultado de novo. Ela só decidia o número grande por causa de `dinheiro.js:147` e `hoje_ideal.js:524`; com o típico fixo, ela só acende um jeito, e por isso vai para as abas de cenários (os dois mudaram de voto) |
| Maniva sem supor "plantada" (01) e linha condicional na tela única (08) | 01, 08 | A linha condicional depende do plano, que depende da terra e do baixio da mesma tela, e faria a tela pular embaixo do dedo. Supor "plantada" quando ele marca mandioca é o caso comum. O risco do 01 (+R$ 1.145 sem ele dizer) e o do 08 (98 → 0 sem maniva) ficam cobertos pela linha de 3 chips **à vista** sob o desenho |
| Passo 1 curto na frente (03, 05, 06, 08, 09 na 1ª rodada) | todos mudaram | O painel do globo já mostra o El Niño e a chuva (`rocacerta.js:166-178`). O passo 1 repetiria a mesma frase antes da 1ª pergunta. O júri vê NASA no globo, no selo e em "Do espaço" |
| Tela "Afinar" separada (01, 07, 09, 10) | 01, 07, 09, 10 | A mesma resposta ficaria em 2 lugares, e voltariam o estado de módulo e as 3 + 3 telas. Cada ajuste mora onde age, e Sua roça é o afinar |
| Abas fixas embaixo (07, 10; 06 no topo) | barra de abas | Seria uma 2ª barra (cerca de 120 px a menos num 360×640) e componente novo na véspera. As pílulas do topo, na ordem `[2,3,4,5,1]` e sem número, já são as abas |
| "E se chover…" no "ver mais" (05, 08) | 05, 08 | É o ponto 13 e a melhor interação da demo. A briga das medianas (3,2 × 3,9) se resolve abrindo em 100% e mostrando só a frequência nas linhas de 2027 |
| Cartões por cultura no "ver mais" (05, 07, 09) × à vista (02, 04, 06, 10) | os dois em parte | Fica 1 linha por cultura à vista (a grade de 10 roças, ponto 6) e o cartão completo de 3 anos no "ver mais" |
| Manchete "Com 3 ajustes, o seu jeito rende R$ X a mais" (01, 02) | 01, 02 | O Hoje conta o consórcio como metade da área para cada cultura (`calculo.js:151`) e o ganho contra o consórcio não foi medido. O h1 do passo 4 fica neutro ("Hoje, melhor e ideal.") e os R$ ficam no gráfico com PROJEÇÃO. Conferir a PAM fica como pendência |
| Pergunta nova "Tem criação?" (05) | 05 (mudou) | Nenhum código leria a resposta. A frase fixa "vira comida da criação (fora do R$)" resolve |
| Terra "rasa/piçarra" = AD1 (05; 06 se testada) | 05, 06 | Só muda milho e feijão comum para "não zoneada", o mapa rasa → AD1 é suposição, e falta o teste nos 7 municípios. Fica para depois da entrega |
| `motor.py` com o "não sei" honesto (08) | 08 | O servidor não pode ser reiniciado (`servidor.py:22` importa o motor uma vez só). O `por_solo` do cardápio dá o aviso no navegador sem tocar o núcleo |
| Renumerar os passos (02, 1ª rodada) | 02 (mudou) | Quebra cerca de 15 links (`ctx.link(n)`, `data-ir`, atalho do técnico) e o `percorrer_fluxo.py`. Mudar a entrada e a ordem das pílulas dá o mesmo efeito |
| Página nova "Como o QUADRA sabe" (04) | 04 (mudou) | Seria rota e módulo novos. "Do espaço" e os "ver mais" que já existem cobrem os pontos 2, 3, 4, 6 e 7 |
| Tamanho fora da tela, só como chip (08, 09, 10 na 1ª rodada) | todos mudaram | O R$ é linear na área (0,5 ha → R$ 2.105; 3 ha → R$ 12.684), é pedido do José e, já preenchido, custa 0 toque |
| Ordem das linhas: tamanho por último (08, 09) × 2º (os outros 8) | 08, 09 | 8 votos. A terra continua acima da dobra a 390×844, que era o motivo do 08 |
| Faixa do El Niño na tela única (09 contra, pela altura) | 09 | Foi pedida por 02, 04, 05 e 06. Ocupa 1 linha (≤ 44 px) e dá o porquê a quem entra sem o globo |
| Botão "Ouvir" (09), troca de fonte global (07), `ctx.editar` com uma entrada por tela no histórico (06) | todos para depois | Nenhum deles tira pergunta do caminho e todos custam 45–60 min com risco. Do 06 fica a versão simples: `data-editar`, foco e volta numa variável |

**Pendências declaradas:**
- caju, banana e cana como chip na linha 1 (hoje é "Outra");
- conferir na PAM como o consórcio entra na área;
- "antes:" nas datas (opcional);
- link "Internet fraca?" (opcional);
- limpeza dos modos "pergunta" órfãos depois da entrega.
