# 09 · Lente: celular, acessibilidade e pouca leitura

Medido em Quixadá-CE (2311306), Edge headless em modo celular **390 × 780 px** (Android simples, barra do navegador já descontada).
Scripts: `E:/campeonato-nasa/tmp/mobile_lente/medir.py` (altura, palavras, letra, contraste, alvos, bytes),
`corrida.py` (toque duplo), `sonda.py` (rolagem lateral). Resultado bruto: `E:/campeonato-nasa/tmp/mobile_lente/medidas*.json`.

**Resumo em uma linha:** o plano está a **14 toques** do painel do globo e cada passo de resultado tem **8 a 12 rolagens** e **550 a 840 palavras** à vista.
A proposta põe o plano a **5 toques**, com **3 perguntas** e **no máximo 3 rolagens e 150 palavras por passo**. O resto não some: fica em "ver mais" ou em "Afinar".

---

## 1. Diagnóstico (com medida)

Área útil a 390 × 780: o topo fixo ocupa 107 px e a barra de baixo fixa ocupa 123 px. **Sobram 550 px (70 %)**. "Rolagens" = altura ÷ 550.

| Passo | Altura | Rolagens | Palavras à vista (tudo fechado) | Palavras com letra < 14 px | Alvos < 44 px | Onde está o que importa |
|---|---|---|---|---|---|---|
| 1 Lugar | 4.550 px | 8,3 | 546 | 297 (54 %) | 15 de 16 | CTA "Responder 5 perguntas" em y = 4.134 (**rolagem 8**) |
| 2 Sua roça | 12 telas de 900–1.499 px | 1,6–2,7 cada | 629 nas 12 telas | — | — | o plano só depois de **11 telas** |
| 3 Como plantar | 5.625 px | 10,2 | 656 | 338 (52 %) | 30 de 44 | "O que fazer e quando" em y = 3.094 (**rolagem 6**) |
| 4 Quanto rende | 6.629 px | 12,1 | 722 | 341 (47 %) | 13 de 27 | barras Hoje → Melhor → Ideal em y ≈ 1.300 (**rolagem 3**), depois de 4 controles |
| 5 Segurança | 6.377 px | 11,6 | 841 | 346 (41 %) | 24 de 28 | datas de olhar a terra em y = 3.750 (**rolagem 7**); técnico/WhatsApp em y = 4.068 / 4.790 (**rolagens 8–9**) |

Total à vista: **≈ 3.400 palavras**. Lendo 100 palavras por minuto (leitor com pouca prática), são **≈ 34 minutos**.

Problemas, do mais grave ao mais leve:

1. **ALTA. Os passos de resultado são compridos demais.** Veja a tabela acima. São 8 a 12 rolagens por passo e 42 rolagens nos passos 1, 3, 4 e 5.
2. **ALTA. Há 11 telas de pergunta antes do plano, e a tela promete 5.**
   - O botão diz "Responder **5** perguntas" (`passos/lugar.js:148`).
   - Aparecem 3 contadores diferentes: "SEU JEITO DE HOJE · 1 DE 3", "O QUE VOCÊ JÁ FEZ · 1 DE 3" e "PERGUNTA 1 DE 5" (prints 02, 05 e 08).
   - O caminho mais curto, do painel ao plano, tem **14 toques**: Montar, Sua roça, 11 telas e "Ver como plantar".
3. **ALTA. Algumas perguntas não mudam nem a conta nem o plano.**
   - `agua`: a tela diz "muda o que dá para salvar", mas a resposta só vira uma pergunta para o técnico (`extras/leve_ao_tecnico.js:67-68`).
   - `gs`: "o valor do benefício não entra na conta" (`passos/dinheiro.js:116-130`).
   - Preparo da terra (trator, animal ou enxada): só aparece no resumo (`extras/historico.js:289`).
   - Fogo e semente: geram só frases (`extras/hoje_ideal.js:297-298`).
   - A tela do histórico "2026" já vem marcada "do seu jeito de hoje", ou seja, repete a tela 1 (print 05).
4. **ALTA. Um toque duplo pula uma pergunta (erro confirmado).**
   - Teste: 2 toques em "Seca rápido" com 120 ms entre eles. A tela foi de "pergunta 1 de 5" direto para "3 de 5" e pulou o tamanho (`corrida.py`).
   - A tela nova leva **998 ms** no próprio PC. A API leva 0,9–1,5 s e manda 62 KB sem gzip. Nesse tempo não aparece nenhum sinal de que o toque valeu.
   - Causa: `q += 1` roda antes de a tela mudar, e os botões antigos continuam ativos (`passos/perguntas.js:115-120`).
5. **ALTA. A ação de cada passo fica enterrada.** Veja a última coluna da tabela. O passo 1 repete o El Niño, que o painel do globo já mostrou (`globo/rocacerta.js:167-177`).
6. **MÉDIA. Dois botões verdes disputam o toque.**
   - Em todas as telas do passo 2 aparecem "Próxima" (da pergunta) e "Como plantar →" (da barra de baixo). O segundo pula o resto das perguntas sem avisar.
   - No resumo aparecem "Ver como plantar" e "Como plantar →" (prints 02, 05 e 13).
7. **MÉDIA. As barras fixas comem 29 % da tela.**
   - São 107 + 123 px em 780 px.
   - Na pergunta da terra, a 2ª fileira de opções vai até y ≈ 722, mas a barra de baixo começa em 657. "Anterior/Pular" está em y ≈ 885 e exige rolar (print 08).
   - A frase da moldura ocupa 2 linhas dentro da barra fixa.
8. **MÉDIA. Os chips "1,0 ha", "terra: não sei" etc. dos passos 3–5 levam ao lugar errado.** Eles abrem a 1ª tela do passo 2 ("Como você planta hoje?") e não a pergunta tocada (`roca.js:111-113` usa `data-ir="2"` e `perguntas.js:77` zera `fase` e `q` ao entrar).
9. **MÉDIA. O contraste da 2ª linha das manchetes é fraco.**
   - A 2ª linha de toda manchete (`.eco`, `--ink-4` = 0,34) fica em **2,8 : 1**. Reprova até no limite de letra grande (3 : 1).
   - No passo 2, essa linha é justamente a instrução "Toque no que vai no roçado." (`css/quadra.css:8, 89-90`).
10. **MÉDIA. A letra é pequena.**
    - 41–54 % das palavras dos passos 1, 3, 4 e 5 estão abaixo de 14 px.
    - Os selos têm 9,5 px (`quadra.css:162`). Os rótulos do desenho do roçado têm 9,5–11,9 px.
11. **MÉDIA. Muitos alvos de toque são pequenos.**
    - Todos os "Ver …" (summary) têm 22 px de altura (`quadra.css:146`).
    - "SEU OLHO" tem 65×16 px e "Mudar" tem 52×20 px.
    - Garantia-Safra (sim/não/não sei) tem 40 px de altura e os checkboxes do técnico têm 22×22 px.
12. **MÉDIA. A página é pesada para internet fraca.**
    - O globo tem **7,8 MB em 119 pedidos**: maplibre 1,0 MB, three 655 KB, texturas 1,7 MB e relevo vindo do S3. A 1 Mbps, são cerca de 60 s.
    - Cada passo, aberto do zero, tem 0,55–0,94 MB.
    - `glossario_mun.json` (92 KB) baixa em todo passo, mesmo sem ninguém tocar num termo (`extras/glossario.js:236`).
    - `confianca_mun.json` (132 KB), `tendencias/CE.json` (96 KB) e `declive_mun.json` (96 KB) baixam inteiros para mostrar 1 município.
    - O servidor não usa gzip e manda `Cache-Control: no-cache`.
13. **MÉDIA. Há informação repetida.**
    - A régua do ano repete "18/01" e "jan–abr" dos indicadores.
    - A lista "2027 · o ano todo" repete o desenho com números que parecem diferentes: "A · mandioca 0,11 ha" duas vezes no desenho e "A Mandioca 0,23 ha" na lista.
    - No passo 4 há dois números por opção: R$ 2.480 nas barras e R$ 984 em destaque no cartão "Hoje".
14. **BAIXA. Ninguém consegue ouvir a tela.**
    - Não há botão de ouvir (nenhum `speechSynthesis` no código).
    - `lang="pt-BR"` e os SVG com nome estão certos.
    - O "·" aparece 23 vezes como separador nos passos 3 e 5, além de "≈", "⅓" e "↓", que atrapalham o leitor de tela.
15. **BAIXA. Há carrosséis laterais que ninguém percebe.** "Como o seu lugar está mudando" corta o 2º cartão na borda (print 01). Também `ss-cartoes` no passo 3 e `seg-cols` ×3 no passo 5.

---

## 2. Limites medíveis (o que a proposta tem que cumprir)

| # | Limite | Hoje | Como medir |
|---|---|---|---|
| L1 | **≤ 5 toques** do painel do globo até ver o desenho do plano; **≤ 2** pelo atalho "ver com o típico daqui" | 14 | contar no `percorrer_fluxo.py` |
| L2 | **≤ 3 perguntas** antes do plano, **1 toque cada**, mais "É isso" | 11 telas | — |
| L3 | Tela de pergunta **cabe sem rolar** (≤ 640 px entre as barras) e tem **≤ 25 palavras** | 900–1.499 px; 40–64 palavras | `medir.py` (H ≤ 780) |
| L4 | Passo de resultado **≤ 1.900 px** (≤ 3 rolagens) com tudo fechado e **≤ 150 palavras** à vista | 4.550–6.629 px; 546–841 | `medir.py` |
| L5 | A **resposta do passo na 1ª dobra** (y < 700 px) | rolagens 3–8 | `medir.py` (mapa) |
| L6 | **1 botão verde por tela** | 2 | olho |
| L7 | Contraste ≥ 4,5 : 1 no texto e ≥ 3 : 1 nas manchetes; **0** palavras de leitura com letra < 14 px (selos e eixos ≥ 11 px) | eco 2,8 : 1; 41–54 % < 14 px | `medir.py` |
| L8 | Alvos ≥ 44 × 44 px, exceto termos dentro do texto | 13–30 por passo | `medir.py` |
| L9 | ≤ 300 KB por passo depois da 1ª carga; nada de JSON baixado "por garantia" | glossário 92 KB sempre | aba Rede |

---

## 3. Decisão por pergunta

| Item | Decisão | Para onde | Por quê |
|---|---|---|---|
| hoje.culturas | **manter** (P1) | 1ª pergunta, com milho + feijão já marcados ("o mais comum daqui") e o botão "É isso →" | É o pedido do José e alimenta a coluna "Hoje" do passo 4. As % ficam num link "quanto de cada?" (padrão: dividir igual) |
| hoje.arranjo | **fundir** | 1 fileira de 3 chips na própria P1: Tudo junto (padrão) · Em pedaços · Milho no baixio | Muda onde fica o milho na conta (`hoje_ideal.js:59`). Não justifica uma tela inteira |
| hoje.manejo | **inferir** | "Afinar" (opcional). Padrão: 1ª chuva = sim; semente pelo Censo; fogo = não sei | Só a "1ª chuva" mexe no "Melhor"; fogo e semente viram só frases (`hoje_ideal.js:291-298`) |
| hist.anos | **inferir** | 2026 = 2025 = o jeito de hoje, com SUPOSIÇÃO. No passo 3: "Se em 2025 também foi milho… · Foi diferente? Contar" | A tela "2026" já vem preenchida pelo hoje. O cartão "por onde começar" funciona com o inferido |
| hist.deu | **mover** | Passo 5, "A sua memória e os dados" (o botão "Contar o meu ano ruim" já existe) | Só é usado no passo 5 (`seguranca.js:412`). Lá a pergunta faz sentido, ao lado do IBGE |
| hist.faz | **cortar** | — (as funções ficam, para links antigos com `exp=`) | Práticas e preparo só geram frases e um chip. "Fogo" e "semente" repetem o manejo. O equipamento já está em bolso.custo |
| terra | **manter** (P2) | 2ª pergunta, 4 opções 2×2, avança no toque | Muda as datas do ZARC. Ex.: barro, caupi 11/03–20/04 em vez de 11/03–20/03; arenosa tira o feijão comum do zoneamento |
| ha | **inferir** | Chip "1 ha · típico daqui ✎" no topo do plano e do dinheiro. "Afinar" abre `area.js` sem mudança (ha, tarefas ou medida) | O padrão do Censo (1,03 ha) só muda a escala; o desenho e as datas ficam iguais. O pedido do José continua atendido, a 1 toque |
| baixio | **manter** (P3) | 3ª pergunta, 5 desenhos, avança no toque **direto para o plano** | `baixio=0` tira a faixa do milho do plano. É a resposta que mais muda o desenho |
| agua | **opcional** | "Afinar" e "Leve ao técnico" | Não entra na conta nem no plano; só vira pergunta ao técnico. Cobre o ponto 15 (água) sem travar o caminho |
| maniva | **opcional** | "Afinar", com padrão "consigo maniva". No plano, um chip "Sem maniva? trocar" junto da faixa da mandioca | `maniva=nao` troca A/B/C por sorgo (mudança grande, mas rara). Quem não tem maniva vê o chip junto da mandioca |
| bolso.prioridade | **manter** | Passo 4, **logo abaixo das barras**: 1 fileira de 4 chips de 48 px. Padrão inferido "garantir" no El Niño | Ponto 9. Muda a ordem e o jeito recomendado |
| bolso.raiz | **opcional** | Passo 4, "Ajustar a conta" (ver mais). Padrão: comum do estado | Afina o R$; tem padrão MEDIDO |
| bolso.custo | **opcional** | Passo 4, "Ajustar a conta": "Você paga trator ou adubo? Não / Sim" | É o "equipamento" do ponto 15, numa pergunta que muda a conta |
| bolso.gs | **cortar** (pergunta) | Vira 1 frase em "Leve ao técnico": "Garantia-Safra: até 5 ha; paga se perder 40 % ou mais" | Não entra na conta (`dinheiro.js:129`) |

---

## 4. O fluxo proposto, tela a tela

```
Globo ─► Painel ─► Passo 1 (1 tela) ─► P1 Hoje ─► P2 Terra ─► P3 Baixio ─► Passo 3 PLANO ─► Passo 4 ─► Passo 5
  │                     └──── "ver com o típico daqui" ─────────────────────────┘     ▲
  └─ "Internet fraca? Entrar sem o globo" ─► roca.html (busca)            Afinar ─┘ (chips no topo: abre 1 pergunta e volta)
```

| # | Tela | Objetivo | Conteúdo (limite) | Ação |
|---|---|---|---|---|
| 0 | **Globo** (index.html) | Achar o município; impressionar o júri | Como hoje, mais um link pequeno no topo: "Internet fraca? Entrar sem o globo", que leva a `roca.html` (a busca de município já existe em `roca.js:185-211`) | Buscar/tocar no município |
| 1 | **Painel Roça Certa** | Mostrar o El Niño e a chuva daqui | Como hoje | "Montar o plano do meu roçado" (toque 1) |
| 2 | **Passo 1 · O seu lugar** (≤ 1.100 px, ≤ 80 palavras) | Dizer o que a terra aceita | Manchete "Quixadá aceita 11 culturas." + eco "2027 é ano de El Niño forte." · 3 números numa linha (chuva chega ~18/01 · chove jan–abr · solo hoje normal), MEDIDO · 6 ícones das recomendadas + "ver todas" · 1 linha "Confiança dos dados: alta · por quê". Ver mais: "Os dados do satélite" (barras de El Niño, régua, tendências, satélite × pluviômetro, de onde vêm, glossário) | Barra de baixo: **"3 perguntas e o plano sai →"** (toque 2) · link "ver o plano com o típico daqui" |
| 3 | **P1 · Como você planta hoje?** (≤ 640 px, ≤ 25 palavras) | Pegar o jeito de hoje | 6 ícones (milho e feijão já marcados), "Como fica?" com 3 chips (Tudo junto marcado), link "quanto de cada?" | **"É isso →"** (toque 3) |
| 4 | **P2 · Quando chove forte, como fica a sua terra?** | Datas do ZARC por solo | 4 opções 2×2 (Seca rápido · Segura · Encharca · Não sei) + 1 linha do "seu olho" (torrão) | Toque na opção avança (toque 4) |
| 5 | **P3 · Tem um baixio?** | Onde vai o milho | 5 desenhos (Não · Pequeno · ⅓ · Metade · Não sei) | Toque leva **direto ao plano** (toque 5) |
| 6 | **Passo 3 · O seu plano** (≤ 1.900 px, ≤ 150 palavras) | Mostrar o plano | Ficha em 1 linha ("1 ha típico ✎ · terra arenosa ✎ · baixio ⅓ ✎ · **+ Afinar**") · manchete "Plante em 3 faixas. Cada ano elas giram." · desenho visto de cima (2027/28/29) · **"O que fazer agora"**: as 3 próximas ações com data · cartão "Por onde começar" (1 frase). Ver mais: mês a mês, onde o roçado sofre, por que em faixas, o que cada planta faz pelo solo, 3 anos parte por parte | Barra: **"Quanto rende →"** |
| 7 | **Afinar** (opcional; reaproveita as telas do passo 2) | Pontos 15 e 16 sem travar o caminho | Abre só a pergunta tocada: tamanho (`area.js`), água, mandioca, 1ª chuva/fogo/semente, "2025 foi diferente?" | Responder **volta ao passo de onde veio** |
| 8 | **Passo 4 · Quanto rende** (≤ 1.900 px, ≤ 150 palavras) | Hoje → Melhor → Ideal | Manchete · **barras Hoje → Melhor → Ideal** (1 número cada, o típico; o caso ruim em letra menor embaixo) · "Do Hoje ao Melhor": os 2 ajustes com +R$ · "O que vale mais" (4 chips). Ver mais: "Ajustar a conta" (preço da raiz, quem paga trator/adubo, área, jeito de hoje) e "Mais contas" (caso ruim, se 2027 for como…, quando o dinheiro entra, a colheita paga o gasto, outros jeitos de girar, como calculamos) | Barra: **"Segurança →"** |
| 9 | **Passo 5 · Segurança e técnico** (≤ 1.900 px, ≤ 150 palavras) | O que olhar e com quem decidir (ponto 16) | Manchete "2027 tende a ser apertado. Plante metade, guarde metade." · **"Olhe a terra de novo em 19/mar e 30/abr"** · **Leve ao técnico**: 3 perguntas + "ver as 7" + **WhatsApp** e Imprimir · "A sua memória": "Lembra de um ano que quebrou? Contar" (abre direto a tela do que quebrou). Ver mais: cada cultura ano a ano (leques), E se chover…, 28 anos, o que não dá para projetar, quanto já acertou | Barra: **"Mandar ao técnico"** (WhatsApp) |

**Toques até o plano:** **5** a partir do painel (Montar, 3 perguntas, É isso, terra, baixio), ou 7 contando a busca no globo. Hoje são **14** (16).
Pelo atalho "ver com o típico daqui" são **2**.

---

## 5. O que muda em cada lugar

**Casca (roca.html + quadra.css), ~45 min**
- Topo do celular em **1 linha** (marca, município e ícone de trocar): de 107 para ~60 px.
- Barra de baixo em **1 linha**:
  - A moldura passa a dizer só "Quem decide é você, com o técnico.".
  - Fica **um único botão verde**, com a ação do passo.
  - A barra **some durante as perguntas** (`body.em-pergunta .nav-baixo{display:none}`). Área útil: 550 → ~640 px (+16 %).
- Ficha dos passos 3–5 em **1 linha rolável**, com o chip "+ Afinar". Cada chip abre **a pergunta certa**: o `click` de `[data-ir]` grava `data-tela` numa variável, como já faz `rolarTecnico`, e `perguntas.js` abre nela e volta à origem.
- `.eco` com `rgba(242,244,247,.5)` (4,9 : 1). `details.ver-mais > summary { min-height:44px }`. Controles segmentados e opções com ≥ 48 px. Selos com 11 px.
- Glossário: tirar o `carregar()` de `instalar` (`glossario.js:236`). O balão já busca quando abre (linhas 219 e 262). Economia: −92 KB por passo.

**Passo 2 (perguntas.js + modo pergunta de hoje_ideal), ~1,5–2 h**
- Ficam **3 telas**: P1 (culturas + arranjo; as % num link), P2 terra, P3 baixio. Somem as 3 telas do histórico, a do manejo, o tamanho, a água, a mandioca e o resumo "Pronto". O fim da P3 leva a `ctx.link(3)`.
- No 1º toque numa opção: marcar a opção, **desligar todos os botões** e mostrar "…". Isso corrige o toque duplo.
- Uma só barra de progresso, "1 de 3", e o botão do passo 1 diz "3 perguntas".
- Modo "afinar" (uma pergunta e voltar), reaproveitando `PERG`, `area.js`, `historico.js` (tela 1 = o que quebrou) e as chaves do manejo.
- Histórico inferido: `antes` vazio e hoje informado → 2025 = 2026 = hoje, marcado SUPOSIÇÃO (`historico.js`, perto da linha 218).

**Passo 1 (lugar.js), ~30 min**
- **Cortar**: a régua (repete os indicadores) e o painel grande do El Niño (repete o globo). Ambos vão para "Os dados do satélite".
- **Mover para ver mais**: tendências (dentro de `<details>` fechado o `montarExtras` já não baixa nada: −96 KB), a tabela técnica, de onde vêm os dados e o glossário.
- **Juntar**: os 4 indicadores viram uma fileira de 3. As culturas mostram 6 ícones + "ver todas". A confiança vira 1 linha + "por quê".

**Passo 3 (plantio.js), ~30 min**
- **Subir** "O que fazer e quando", só as 3 próximas ações, para logo abaixo do desenho.
- **Cortar** a lista "2027 · o ano todo" (repete o desenho com números que confundem).
- **Mover para ver mais**: a grade de 14 meses, "Onde o seu roçado sofre mais" (−100 KB de `declive_mun.json` até alguém abrir), "Por que em faixas", "O que cada planta faz pelo solo" e "Em 3 anos, parte por parte".
- Rótulos do desenho com ≥ 12 px.

**Passo 4 (dinheiro.js + modo comparação de hoje_ideal), ~45 min**
- **Subir** o `hi-slot` (barras) para antes do `bolso`.
- No modo comparação, mostrar 1 número por opção e só os ajustes do "Melhor". Os cartões completos de Hoje, Melhor e Ideal vão para "ver mais".
- Mantém "O que vale mais" logo abaixo.
- **Mover** preço da raiz e custo para "Ajustar a conta".
- **Cortar** a escolha da Garantia-Safra (vira frase no técnico).
- **Mover** `corpo` (herói, caixa, El Niño, termo) e `jeitos` (cenarios) para "Mais contas".

**Passo 5 (seguranca.js), ~30 min**
- **Subir** `blocoPortoes` e `leve_ao_tecnico` para logo depois da manchete.
- **Juntar** o bloco "Hoje" à manchete: 1 frase, e "Ainda não sabemos" vai para o ver mais.
- **Mover** os cartões por cultura, os leques, "E se chover…" e os 28 anos para "ver mais".
- O "Contar o meu ano ruim" passa a abrir direto a tela do que quebrou.

**Ouvir (novo, opcional, ~45 min)**: `extras/ouvir.js`, com um botão "🔊 Ouvir" nas 3 perguntas e na manchete de cada passo.
- Usa `speechSynthesis` com voz pt-BR e fica escondido se não houver voz.
- Lê um texto montado a partir dos dados ("Plante o feijão-caupi entre 11 de março e 20 de março"), nunca o `innerText` com "·", "≈" e "⅓".

---

## 6. Riscos

- **Blocos que medem a largura ao desenhar podem sair com largura 0 dentro de `<details>` fechado.** Exemplos: o `W` do plantio, `fundosRotulos`, os carrosséis e o SVG da vulnerabilidade. Os extras já esperam o `toggle`, mas o HTML próprio dos passos não. Abrir cada "ver mais" a 390 px antes de entregar.
- **Esconder perguntas pode parecer "menos personalizado" ao júri.** Mitigação: a ficha com "✎" e "+ Afinar" fica no topo do plano, e os padrões dizem de onde vêm ("1 ha · típico daqui, Censo 2017").
- **"É isso" com o padrão marcado pode ser aceito sem leitura.** O "Hoje" do passo 4 fica rotulado "padrão do lugar" até ele mudar.
- **O histórico inferido gera "A terra repetiu milho" sem ele ter dito.** O texto precisa ser condicional ("Se em 2025 também foi milho…") e levar o selo SUPOSIÇÃO.
- **Afinar quebrar a volta.** Precisa voltar ao passo de origem e manter as respostas no hash. Testar os 5 chips nos passos 3, 4 e 5.
- **Mudança na véspera da entrega.** Rodar `testes/ferramentas/percorrer_fluxo.py` e conferir os 7 municípios de teste antes e depois. Não mexer em `servidor.py`, que não pode ser reiniciado agora.
- **A internet fraca continua lenta na troca de terra e de baixio**: são 2 chamadas de 62 KB sem gzip, cada uma com ~1 s de cálculo. Fora do escopo de 4–6 h. Depois da entrega: gzip no servidor e pré-busca das 3 variantes do baixio.
- **Ouvir:** Android sem voz pt-BR, ou leitura ruim de datas. Por isso o texto é montado e o botão some sem voz.
- Numa das 3 medições, o passo 4 abriu mais largo que a tela (innerHeight 1.306, zoom para fora) e depois não se repetiu. Vale abrir o passo 4 frio no celular de verdade.

---

## 7. As 3 ideias mais importantes

1. **3 perguntas, 1 toque cada, e o plano sai.**
   - As perguntas: "Como planta hoje?" (com o arranjo e o padrão já marcado), terra e baixio.
   - O resto vira "Afinar": chips no topo do plano que abrem a pergunta certa e voltam.
   - Ganho: de 14 para 5 toques, de 12 para 3 telas, de 629 para ≤ 75 palavras.
2. **A resposta na 1ª dobra e o resto no "ver mais", com limite medido.** Cada passo fica em ≤ 3 rolagens (≤ 1.900 px) e ≤ 150 palavras à vista. Sobem para o topo o desenho, "o que fazer agora", as barras Hoje → Melhor → Ideal, as datas de olhar a terra e o técnico. Dentro de `<details>` os extras nem baixam, o que tira 100–230 KB por passo.
3. **Toque seguro e legível.**
   - Um único botão verde por tela, e a barra some nas perguntas.
   - Bloqueio do toque duplo (o erro confirmado que pula a pergunta do tamanho).
   - Contraste do eco de 2,8 para 4,9 : 1, alvos ≥ 44 px, letra ≥ 14 px.
   - Barras fixas menores (+16 % de tela) e o botão "Ouvir" nas perguntas e manchetes.
