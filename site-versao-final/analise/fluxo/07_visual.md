# 07 · Lente: design visual / UI

Material: os 16 prints e textos de Quixadá a 390 px (`E:/campeonato-nasa/tmp/fluxo_atual/`), prints novos do globo e do painel
(`E:/campeonato-nasa/tmp/visual_ui/globo/`), `web/css/quadra.css`, `css/globo/*.css`, `css/passos/*.css`, `css/extras/*.css`,
`js/passos/LEIA-ME.md`, `roca.js`, `perguntas.js`, `hoje_ideal.js`, `historico.js`, `dinheiro.js` e o `/api/local` com e sem cada resposta.

## Resumo em 3 linhas

1. A jornada mistura 3 linguagens visuais: a do globo (Inter fina, sóbria, uma cor), a do painel Roça Certa (Fraunces negrito, verde)
   e uma terceira, só dela (rótulos em mono espaçado e selos). O resultado parece remendo. **Proposta: uma linguagem só, a do globo.**
2. As 11 telas de pergunta usam **3 componentes diferentes** (3 barras de progresso, 3 contadores, 3 tamanhos de botão de opção e duas
   barras de navegação ao mesmo tempo). **Proposta: 4 perguntas num componente só, com toque que já avança, e de 14 para 5 toques.**
3. Cada passo de resultado tem de 5,4 a 7,9 telas de altura e repete números. **Proposta: 3 abas fixas (Plano · Dinheiro · Segurança,
   e Lugar em 4º), cada uma com um herói, até 3 blocos e uma lista "Ver mais" no fim.**

---

## 1. Diagnóstico (com evidência)

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| 1 | **3 componentes de pergunta diferentes** no mesmo passo | Botão de opção: `.opcao` 176/140 px (`perguntas.css:13,61`), `.hi-opcao` 150 px (`hoje_ideal.css:31`), `.hs-op` 96/84 px (`area_historico.css:107,205`). 3 barras de progresso (`perguntas.css:6`, `hoje_ideal.css:23`, `area_historico.css:82`). 3 contadores: "SEU JEITO DE HOJE · 1 DE 3", "O QUE VOCÊ JÁ FEZ · 1 DE 3", "PASSO 2 · PERGUNTA 1 DE 5": a pessoa nunca sabe quantas faltam (são 11). O passo 1 promete "Responder **5** perguntas" (`lugar.js:148`). | alta |
| 2 | **Duas barras de navegação ao mesmo tempo** | Telas 02–07 e 13: "Anterior / Próxima" no conteúdo **e** a barra fixa "← Voltar / Como plantar →". O verde de baixo é maior que o "Próxima" e pula o questionário inteiro. As telas 08–12 escondem a barra, porque a regra só vale para `.quiz` (`perguntas.css:73`). Há 5 rótulos para avançar: "Próxima" (verde, Fraunces), "Próxima" (cinza, Inter), "Pular", "Pronto ✓" e "Terminar". O voltar aparece como "← Anterior", "←" (só o ícone, `area_historico.css:211`) e "← Voltar". | alta |
| 3 | **Entradas misturadas ao resultado** | O passo 4 abre com 4 controles ("O que vale mais", "Preço da raiz", "O que você paga", "Garantia-Safra") **antes** do número. São 5 componentes de escolha na jornada: botão de opção, botão segmentado, pílula, aba com ícone e controle deslizante. | alta |
| 4 | **Páginas longas que se repetem** | 4.550 / 5.625 / 6.629 / 6.377 px = 5,4 / 6,7 / 7,9 / 7,6 telas de 844 px. No passo 4, o par R$ 2.760 × R$ 984 aparece em 3 blocos (barras, cartões Hoje/Ideal e "No caso ruim"). "El Niño" aparece 16 vezes nos textos (8 no passo 4). A janela do caupi "11/03 a 20/03" aparece em 4 telas. A manchete do El Niño no passo 1 é a mesma do painel do globo ("7 de cada 10 municípios do Ceará"). | alta |
| 5 | **4 estilos de letra; mono demais** | Na mesma tela: Inter 300 (título), Inter 600, IBM Plex Mono em caixa-alta com espaço .2em e Fraunces 700 (números, manchetes de cartão e **botão**). São 74 usos de `var(--mono)` no CSS; só o passo 3 tem 32 rótulos em caixa-alta. O globo usa Inter no sobretítulo (`style.css` `.sobretitulo`) e mono só nas coordenadas, e diz no próprio cabeçalho: "Visual sóbrio: preto, branco e cinzas; uma só cor de destaque" (`style.css:2–3`). | alta |
| 6 | **Selos repetidos, pequenos e mudos no toque** | 9 / 11 / 10 / 15 selos nos passos 1/3/4/5, com 9,5 px (`quadra.css:162`). No passo 3 há selo até em data solta da linha do tempo ("DEZ 22/12 SUPOSIÇÃO", "MAI 10/05 SUPOSIÇÃO"), contra a regra 6 do LEIA-ME. A fonte só aparece no `title=` (`comum.js:24–27`): no Android, tocar não mostra nada. | média |
| 7 | **Cartão dentro de cartão** | Passo 4: "HOJE" › "O QUE PESA" › 3 subcartões. "MELHOR" tem uma caixa tracejada "SEU OLHO" dentro. Passo 1: El Niño com "SEU OLHO" dentro. São 3 níveis de superfície (`--surface`, `--surface-2`, `--surface-3`). | média |
| 8 | **Rolagem lateral que corta conteúdo** | Passo 1, tendências (o cartão "−6" fica cortado na borda). Passo 3, "O que cada planta faz". Passo 5, colunas 2028/2029 cortadas ("pelo mei", "2,5"). A fileira de passos corta o "5" a 390 px (tela 02) e o "1" no passo 4. | média |
| 9 | **Topo pesado** | Nos passos 3–5, logo + município + 5 bolinhas + fileira de fichas ocupam cerca de 300 px antes do título (36 % da 1ª tela). As fichas mostram "terra: não sei" e "baixio: não sei" no topo de toda tela. | média |
| 10 | **2ª linha do título quase apagada** | `.eco` usa `--ink-4` (0,34): contraste ≈ 2,7:1 (`quadra.css:87,90`; `perguntas.css:10`). O globo usa `--ink-3` (0,5), ≈ 4,8:1. Essa 2ª linha costuma ser a instrução ("Toque no que vai no roçado.", "A parte baixa que fica úmida."). | média |
| 11 | **Cores sobrecarregadas** | Verde = botão, seleção, MEDIDO, "Recomendado", leguminosa e "plano à frente". Azul = PROJEÇÃO, forragem, barra "Ideal", "Seu olho" e série "plano". Âmbar = SUPOSIÇÃO, cereal, barra "Melhor", El Niño e alerta. O globo tem 1 cor de destaque. | média |
| 12 | **CTA duplicado no fim de cada passo** | Tela 13: "Ver como plantar" + "Como plantar →". Passo 3: "Ver quanto rende" + "Quanto rende →". Passo 1: "Responder 5 perguntas" + "Pular e ver o plano" + "Sua roça →". | média |
| 13 | **Perguntas duplicadas** | "Queimo / Não queimo" (tela 04) e "Não queimo" (tela 07). "Guardo a minha semente" (04) volta como "Já anotado: Guarda semente" (07). | média |
| 14 | **Escala sem sistema** | 36 tamanhos de fonte diferentes no CSS (49 declarações abaixo de 12 px) e 14 raios diferentes (de 2 a 20 px). | baixa |
| 15 | **Ícones ambíguos** | O sorgo usa o ícone do milho (`hoje_ideal.js:16`). "Faixas" serve para Hoje, hectares, "Planto em faixas" e "Por onde começar". A gota serve para baixio, barreiro e "Segura a umidade". | baixa |

O que está bom e fica: o título em dois tons, uma pergunta por tela, botões de opção grandes com ícone, o desenho do roçado visto
de cima, a grade de 10 roças, o "Hoje → Melhor → Ideal" e a linha do tempo "O que fazer e quando".

---

## 2. Decisão por item perguntado

Medido no `/api/local` (Quixadá):
- **Terra:** barro muda o plano e as datas (milho de 21/02–28/02 para 11/02–10/03); areia tira o feijão comum.
- **Baixio:** `baixio=0` tira a faixa Baixio do plano.
- **Maniva:** `maniva=nao` troca a mandioca por sorgo nas 3 partes.
- **Água:** não muda nada no núcleo.

| Item | Decisão | Para onde | Por quê |
|---|---|---|---|
| hoje.culturas | **manter** | Pergunta 1 "O que você planta hoje?" (vários botões; milho + feijão já marcados) | É o pedido do José e o "Hoje" do passo 4. Sai a divisão em %: fica dividido igual, e o % vai para "Afinar". |
| hoje.arranjo | **mover** | "Afinar a conta" (Dinheiro, cartão "Seu jeito de hoje") | Muda só a conta do "Hoje"; o padrão "tudo junto" é o mais comum. |
| hoje.manejo | **fundir** | Com hist.faz, numa lista "O que você já faz" dentro de "Afinar" | Repete pergunta (queima e semente). Só mexe em alertas e no "Melhor". |
| hist.anos | **inferir** | 2026 = pergunta 1; 2025 = igual. 1 pergunta de 1 toque na própria aba Plano: "Plantou milho no mesmo chão em 2025 e 2026? Sim / Não" | Só serve para "por onde começar o giro". Perguntar onde a resposta aparece. |
| hist.deu | **mover** | Segurança › "A sua memória e os dados" ("Lembra de um ano que quebrou?") | O "quebrou" alimenta a memória × IBGE e o milho no baixio. O "deu bem" não muda nada no plano: sai. |
| hist.faz | **fundir** | As práticas vão para "O que você já faz" (com o manejo). O preparo (enxada / animal / trator) responde o **custo** | "Palhada" e "esterco" não mudam nada. O preparo só aparecia no resumo; como custo, ganha uso. |
| terra | **manter** | Pergunta 2 (3 botões + "Não sei" largo) | Muda o plano e as datas (medido acima). |
| ha | **manter** | Pergunta 4, como confirmação: "Seu roçado tem uns 1 ha?" com atalhos ½ · 1 · 2 · 3 · 5 e "outra medida" (tarefas, metros: `area.js`) | Muda o desenho e o dinheiro. Com o típico do Censo marcado, basta 1 toque. |
| baixio | **manter** | Pergunta 3, com 3 botões: Não / Sim, tenho / Não sei | Tira ou põe a faixa Baixio. O tamanho do baixio (pequeno, ⅓, ½) se ajusta no desenho do roçado. |
| agua | **opcional** | "Afinar" (Plano) | Não muda o núcleo; só o aviso de irrigação e o volume do barreiro. |
| maniva | **inferir** | Mandioca marcada na pergunta 1 → "já plantada"; senão, "consigo". Na parte A do Plano: "Não consegue maniva? Trocar" | Quando falta maniva, o plano todo muda; a pessoa reage melhor vendo a mandioca no desenho do que a uma pergunta solta antes. |
| bolso.prioridade | **mover** | Fileira de 4 botões no topo do Dinheiro: Garantir comida · Equilibrar · Vender mais · Cuidar da terra (em ano de El Niño, já vem em "garantir") | É filtro da visão, não pré-requisito. Continua cobrindo os pontos 9 e 15. |
| bolso.raiz | **mover** | "Afinar a conta" (Dinheiro) | Detalhe do preço; o padrão é o comum do estado. |
| bolso.custo | **fundir** | Com o preparo da terra (enxada/animal → só a semente; trator → máquina e insumos), em "Afinar" | Palavra da roça no lugar de um termo de planilha. |
| bolso.gs | **cortar** | Vira 1 linha informativa em Segurança / "Leve para o técnico": "Até 5 ha, você cabe no Garantia-Safra" | Não entra na conta (`dinheiro.js:129`: "o valor do benefício não entra na conta"). |

---

## 3. Fluxo proposto, tela a tela

```
Globo → Painel do município → [Montar o plano] → P1 → P2 → P3 → P4 → PLANO (abas: Plano · Dinheiro · Segurança · Lugar)
```

| # | Tela | Objetivo | Conteúdo | Ação |
|---|---|---|---|---|
| 0 | Globo (`index.html`) | Escolher o lugar | Não muda: busca, mergulho, mapa e camadas | Buscar ou tocar no mapa |
| 0b | Painel Roça Certa | Dar o porquê (El Niño 2027) | Não muda: manchete do El Niño, mapa por estado e chuva ano a ano | "Montar o plano do meu roçado" → **`#/<cod>/2`** (hoje vai para `/1`) |
| 1 | Pergunta 1 de 4 | O jeito de hoje | "O que você planta hoje? / Toque no que vai no roçado." 6 botões (milho e feijão já marcados) | "Seguir" (fixo embaixo). Link discreto: "Ver o plano sem responder" |
| 2 | Pergunta 2 de 4 | Terra | "Quando chove forte, / como fica a sua terra?" 3 botões + "Não sei" largo + 1 linha de olho ("Aperte um torrão…") | O toque já avança |
| 3 | Pergunta 3 de 4 | Baixio | "Tem uma parte baixa / que fica úmida?" Não / Sim / Não sei, com o mini-roçado | O toque já avança |
| 4 | Pergunta 4 de 4 | Tamanho | "Seu roçado tem uns / 1 ha?" Número grande, atalhos ½ · 1 · 2 · 3 · 5, "Outra medida" (tarefas, metros) | O toque no atalho, ou "É isso", abre o plano |
| 5 | Aba **Plano** (ex-passo 3) | O que fazer na terra | Linha "1 ha · terra misturada · baixio · mudar". Herói: o roçado de cima + 2027/2028/2029 + legenda em lista. "Comece por aqui": as 3 próximas ações. 1 pergunta de 1 toque ("Plantou milho no mesmo chão…?") que mostra "por onde começar" | Abas embaixo |
| 6 | Aba **Dinheiro** (ex-passo 4) | Quanto rende | Botões de prioridade no topo. Herói único: Hoje → Melhor → Ideal. "Melhor = 3 ajustes" em linhas. Cartão "Seu jeito de hoje · Afinar" | "Afinar" abre a folha |
| 6b | Folha **Afinar** | Ajustar sem atrapalhar | Divisão em % · junto ou separado · "o que você já faz" · como prepara a terra (= custo) · preço da raiz · água | "Pronto" fecha e refaz a conta |
| 7 | Aba **Segurança** (ex-passo 5) | Risco e técnico | Herói "2027 tende a ser apertado". 1 linha por cultura (ícone, "quebra em 5 de 10", 10 quadradinhos, "pelo menos…") com 2027/28/29. "Vamos olhar em 19/mar e 30/abr". "Leve para o técnico" | **"Mandar pelo WhatsApp"** (o único verde da aba) |
| 8 | Aba **Lugar** (ex-passo 1) | O lugar visto do espaço (júri) | Tendências em grade 2×3 · régua da chuva · o que dá para plantar (lista compacta) · confiança dos dados | Ver mais: satélite × pluviômetro, de onde vêm os dados, glossário |

As 4 perguntas usam **um componente só** (o `.opcao` de `perguntas.css`). Cada uma tem barra de 4 segmentos e "Sua roça · N de 4",
o voltar no topo à esquerda e **nenhuma** barra embaixo, exceto o "Seguir" da pergunta 1 (é a única com vários botões).
Saem: a tela "Pronto" (o resumo vira a linha "1 ha · terra … · mudar" no topo do Plano), as telas 2 e 3 do jeito de hoje e as 3 telas do histórico.

---

## 4. O que muda em cada passo

**Globo / painel**
- O link do plano vai para `#/<cod>/2` (`globo/principal.js:94`, `globo/rocacerta.js:333`).
- Fora isso, nada muda: é o modelo.

**Passo 1 "O lugar" → vira a 4ª aba, "Lugar"**
- Sai da frente: o El Niño já está no painel.
- Cortar: a manchete do El Niño e "O mar agora" (repetem o painel), "Responder 5 perguntas", "Pular…" e "Sua roça →".
- Tendências: a fileira que rola de lado vira grade 2×3.
- Cardápio: os 16 cartões (≈ 1.400 px) viram lista de 1 linha por cultura (ícone · nome · bolinha · data), ≈ 800 px.
- Confiança dos dados fica, à vista.

**Passo 2 "Sua roça"**
- Passa de 11 telas + resumo para 4 telas.
- O resumo "Pronto" sai.
- `hoje_ideal.js` e `historico.js` deixam de rodar no modo "pergunta" e passam a servir a folha "Afinar" e os cartões.

**Passo 3 "Como plantar" → aba Plano**
- Fica à vista: o roçado com a legenda em lista, "Comece por aqui" (3 próximas ações) e a pergunta de 1 toque do giro.
- Cortar: os rótulos dentro das faixas ("B · caupi · 0,11 ha" duas vezes, enquanto a legenda diz 0,23 ha) e a grade de meses NOV…DEZ.
- Vai para "Ver mais": calendário completo, onde o roçado sofre mais (vulnerabilidade), por que em faixas (praga), o que cada planta faz (grade 2×2, sem carrossel), 3 anos parte por parte.

**Passo 4 "Quanto rende" → aba Dinheiro**
- No topo: os botões de prioridade.
- Herói único: Hoje → Melhor → Ideal.
- Cortar o 2º herói "No caso ruim… O plano × Jeito de hoje": repete os mesmos números.
- O bloco "Seu bolso" sai do topo e vai para "Afinar".
- Vai para "Ver mais": quando o dinheiro entra, a colheita paga o gasto?, se 2027 for como 1998/2010/2016/2024, outros jeitos de girar o roçado (cenários), como calculamos.

**Passo 5 "Segurança" → aba Segurança**
- Os 3 cartões de cultura que rolam de lado viram 1 linha por cultura, com o mesmo botão de ano do Plano.
- "HOJE · 2 de 3 anos de mar assim" e "Ainda não sabemos" vão para "Ver mais", porque o El Niño já foi dito.
- O "Leve para o técnico" sobe e termina no verde "Mandar pelo WhatsApp".
- Vai para "Ver mais": E se chover (controle deslizante), a sua memória e os dados (com o "quebrou"), os 28 anos, o que não dá para projetar, quanto já acertou.

**Moldura (`roca.html`)**
- Sai a fileira de 5 bolinhas e a fileira de fichas.
- Sai a barra fixa "Voltar / Próximo".
- Entra a barra de abas embaixo, só nos resultados.
- A frase do ponto 16 vira a última linha de cada aba e continua no cartão do globo.

---

## 5. Os 3 modelos de tela

### A. Pergunta (igual à tela inicial do globo: uma pergunta, nada em volta)

```
+--------------------------------------+
| <-        [====][====][----][----]   |  56 px; voltar à esquerda; barra de 4
|                                      |
| SUA ROÇA · 2 DE 4                    |  Inter 12/500, caixa-alta .12em, --ink-3
| Quando chove forte,                  |  Inter 300 30 px
| como fica a sua terra?               |  2º tom: --muted (contraste >= 4,5:1)
|                                      |
| +---------------+ +---------------+  |  botões 2 colunas, 112 px, raio 12
| |      ≈        | |      ◊        |  |  ícone 40 px
| |  Seca rápido  | | Segura a água |  |  17/600, no máx. 1 linha de apoio 13 px
| +---------------+ +---------------+  |
| +---------------+                    |
| |   Encharca    |                    |
| +---------------+                    |
| [             Não sei              ] |  contorno, 48 px, largura toda
|  (olho) Aperte um torrão: areia      |  1 linha, sem caixa
|         esfarela, barro gruda.       |
+--------------------------------------+
```
- O toque já avança.
- Só a pergunta de vários botões tem "Seguir", verde, 56 px, fixo embaixo.
- Nenhuma outra barra.

### B. Resultado (uma aba)

```
+--------------------------------------+
| (o) QUADRA     Quixadá, CE   Trocar  |  56 px, igual ao topo do globo
| 1 ha · terra misturada · baixio  mudar |  13 px, 1 linha
| PLANO                                |  rótulo
| Plante em faixas.                    |  Inter 300 30 px
| Cada ano, cada cultura muda.         |  2º tom
| +----------------------------------+ |
| | [ 2027 ][ 2028 ][ 2029 ]         | |  segmentado (o mesmo em toda a jornada)
| |      (desenho do roçado)         | |  1 herói: desenho OU número Fraunces 44
| | A  Mandioca            0,23 ha   | |  legenda = lista com divisórias
| | B  Feijão-caupi        0,23 ha   | |
| | ● Suposição · ver como           | |  selo NO RODAPÉ, junto do "ver como"
| +----------------------------------+ |
| Comece por aqui                      |  bloco 2 (máx. 3 blocos à vista)
| ...                                  |
| VER MAIS                             |
| > Calendário completo                |  linhas de 56 px com seta
| > Onde o roçado sofre mais           |
| > Por que em faixas                  |
| O QUADRA ajuda. Quem decide é você.  |  ponto 16, fim da aba
+--------------------------------------+
| Plano | Dinheiro | Segurança | Lugar |  abas 64 px, ícone + 13 px
+--------------------------------------+
```

### C. Detalhe (o "ver mais" aberto)
- É o mesmo `<details>` de hoje, com outra cara.
- Abre como linha da lista: título 17/600, o gráfico ou a tabela, 1 frase, e a fonte escrita por extenso com o selo.
- Tudo o que é técnico mora aqui: ZARC, IMERG, P10/P90, 28 anos, harmonização, métodos.

---

## 6. Regras visuais (para tudo parecer um produto só)

1. **2 estilos de letra.**
   - Inter em tudo: título 300, texto 400, rótulo e botão 600.
   - Fraunces 700 **só** no número-herói, no máximo 1 por cartão.
   - IBM Plex Mono sai: os rótulos viram Inter 12/500 em caixa-alta .12em, como o `.sobretitulo` do globo. Números alinhados com `tabular-nums`.
2. **Escala:** 13 · 15 · 17 · 22 · 30, mais 44 no número. Nada abaixo de 12 px; o selo fica com 11 px.
3. **Uma cor de ação.**
   - Verde = botão, seleção e "o plano".
   - Âmbar = atenção. Terra = quebra ou perda. Cinza = jeito de hoje.
   - Nos gráficos: Hoje cinza, Melhor verde-claro, Ideal verde.
   - As cores de tipo de cultura ficam só no desenho do roçado e na legenda dele.
4. **Selo: 1 por cartão, no rodapé.**
   - Fica junto do "ver como", no formato "● Medido · ver de onde vem" (bolinha colorida, palavra em caixa normal).
   - Nunca no título nem em linha de lista. A fonte vai por extenso dentro do "ver como" (no toque, o `title=` não abre).
5. **Um nível de superfície.**
   - Cartão = `--surface` + borda 1 px + raio 16.
   - Dentro do cartão só há divisórias, nunca outro cartão.
   - "Seu olho" = 1 linha com o ícone de olho, sem caixa tracejada, no máximo 1 por tela.
6. **1 botão verde por tela.**
   - O verde tem 56 px, largura toda e fica fixo embaixo, ou é o último bloco da aba.
   - O secundário é contorno de 48 px. O terciário é link. Voltar = seta no topo.
   - A mesma ação tem sempre o mesmo nome: "Seguir".
7. **Um componente por tipo de escolha.**
   - Botões grandes com ícone, em 2 colunas, para perguntas.
   - Botão segmentado (2 a 4 opções curtas) para trocar a visão: ano, prioridade.
   - Pílula só para leitura.
8. **Nada rola de lado.** Use grade de 2 colunas ou lista; o ano se troca no botão segmentado.
9. **Densidade:** por aba, 1 herói + até 3 blocos à vista; o resto numa lista "Ver mais" única, no fim. Alvo: até 2.000 px por aba a 390 px.
10. **Espaço e raio:** espaços de 8 / 16 / 24 / 32; raio 12 em botões, 16 em cartões, 999 só em pílula.
11. **Contraste:** o 2º tom do título é `--muted` (0,58), nunca `--ink-4`, em texto que precisa ser lido.
12. **Topo:** 56 px (marca, município, "Trocar"). Sem bolinhas de passo e sem fileira de fichas.

---

## 7. Toques até ver o plano

| | Hoje | Proposta |
|---|---|---|
| Do botão "Montar o plano" até o plano | **14 toques** + 4.550 px de rolagem no passo 1 (Montar, Responder, 3 do jeito de hoje, 3 do histórico, 5 perguntas, "Ver como plantar") | **5 toques** (Montar, Seguir, terra, baixio, tamanho) |
| Atalho "ver sem responder" | 2 toques + 4.550 px de rolagem | 2 toques (Montar, "Ver o plano sem responder") |
| Telas até o plano | 1 + 11 + resumo = 13 | 4 |

---

## 8. Como implementar em 4–6 h (por ordem de efeito por hora)

| h | Arquivo | O quê |
|---|---|---|
| 1,0 | `css/quadra.css` (+ ajustes em `css/passos/*`) | Muda as 16 telas de uma vez: `.kicker`, `.cartao h3`, `.olho-rot` e `th` em Inter (ou `--mono: var(--font)` + `tabular-nums`) · `.botao.primario` em Inter 600 · `.eco` em `--muted` · `.selo` sem borda, com bolinha, 11 px, caixa normal (`text-transform: lowercase` + `::first-letter`) · achatar `.painel .painel` / `.aviso` / `.olho` dentro de cartão (sem fundo, sem borda) · tamanhos menores que 12 px sobem para 12 · tendências, saúde do solo e anos do passo 5 viram grade · `#ficha { display:none }` |
| 1,5 | `js/passos/perguntas.js`, `css/passos/perguntas.css` | `PERG` com 4 itens (culturas do tipo "vários", grava `resp.hoje` com `escreverHoje`; terra; baixio com 3 opções; tamanho via `AREA`) · o toque avança · última → `ctx.ir(3)` · sai o resumo · um contador "Sua roça · N de 4" · voltar no topo · `maniva` inferida das culturas |
| 1,0 | `roca.html`, `roca.js`, `css/quadra.css` | `.passos-nav` vira barra de abas fixa embaixo nos passos 3, 4, 5 e 1 (rótulos Plano · Dinheiro · Segurança · Lugar), escondida no 2 · sai a barra "Voltar/Próximo" · a frase do ponto 16 vira a última linha · link do globo para `/2` |
| 1,0 | `js/passos/dinheiro.js` | Prioridade em botão segmentado no topo · `bolsoHtml` + jeito de hoje (arranjo, %, manejo, preparo = custo, água) dentro de `verMais(…, "Afinar a conta")` · sai o 2º herói repetido · os blocos secundários vão para o "Ver mais" do fim |
| 0,5 | `plantio.js`, `seguranca.js`, `lugar.js` | Os blocos secundários entram em `verMais` (lista no fim) · linha "Não consegue maniva? Trocar" na parte A · "Contar o meu ano ruim" recebe o "quebrou" · sem CTA repetido |
| 0,5 | `testes/ferramentas/percorrer_fluxo.py` + prints a 390 px | Conferir as 4 perguntas, as 4 abas, rolagem lateral zero e altura de cada aba |

---

## 9. Riscos

- **Pontos 1, 2, 3, 7 e 11 para o júri.** O passo 1 sair da frente esconde o "lugar visto do espaço". Mitigação: aba "Lugar" à vista, o roteiro da demo passa por ela, e o painel do globo já mostra El Niño e o mapa.
- **Inferências podem errar.** Maniva tirada das culturas, 2025 igual a 2026, custo tirado do preparo. Mitigação: cada inferência tem "mudar" ou "trocar" ao lado do lugar onde aparece.
- **Pedidos do José.** Jeito de hoje e histórico saindo das perguntas podem soar como "sumiu o que eu pedi". Mitigação: o jeito de hoje continua na pergunta 1 e no herói Hoje → Melhor → Ideal; o histórico vira "por onde começar" (1 toque) e "a sua memória"; o detalhe fica em "Afinar".
- **Trocar o mono globalmente.** Pode desalinhar a linha do tempo, os meses e as tabelas. Mitigação: `font-variant-numeric: tabular-nums` e conferência a 390 px.
- **Selo mais discreto.** Pode parecer menos transparência. Mitigação: 1 selo por cartão sempre, a fonte escrita por extenso no "ver como" (hoje ela só aparece no hover) e a legenda dos 3 selos na aba Lugar.
- **Prazo apertado** (entrega amanhã). Fazer na ordem da seção 8: só o CSS da 1ª hora já resolve metade da cara amadora. Se faltar tempo, as abas podem esperar; as 4 perguntas não.
- **Testes e links antigos.** Manter os números de rota (`#/<cod>/1..5`) e mudar só a ordem das abas e o link do globo.

---

## 10. As minhas 3 ideias mais importantes

1. **Uma linguagem só, a do globo.** Inter e uma cor de ação; sai o mono; Fraunces só no número-herói; o selo vira "● Medido" no rodapé do cartão; nada de cartão dentro de cartão. É quase tudo CSS (cerca de 1 h) e muda as 16 telas.
2. **4 perguntas, um componente, toque que avança.** O botão do globo entra direto na pergunta 1 (sem passo 1 e sem resumo): de 14 para 5 toques. Jeito de hoje, histórico e bolso viram "Afinar" ou 1 toque no lugar onde mudam o resultado.
3. **Resultado em abas fixas** (Plano · Dinheiro · Segurança · Lugar), cada uma com herói + até 3 blocos + uma lista "Ver mais" no fim. Um botão verde por tela, nada rola de lado, até cerca de 2.000 px por aba (hoje são de 4.550 a 6.629).
