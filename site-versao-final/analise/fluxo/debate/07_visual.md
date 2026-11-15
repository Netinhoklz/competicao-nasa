# 07 · Design visual / UI · rodada de debate

Material: as 10 propostas, os prints de `E:/campeonato-nasa/tmp/fluxo_atual/` (folhas de contato em
`E:/campeonato-nasa/tmp/debate_visual/folha1.png` e `folha2.png`), `perguntas.js`, `hoje_ideal.js`, `roca.js`, `comum.js`,
`rocacerta.js`, `cenarios.js`, `perguntas.css`, `hoje_ideal.css` e `quadra.css`.

## Resumo

- **Fluxo preferido: o do 09 (Celular), com 8 emendas.** São 3 perguntas, uma por tela, com botão grande e toque que já avança. A
  emenda principal: o botão do globo entra direto na 1ª pergunta, e o tamanho do roçado vira uma linha dessa 1ª pergunta. Do painel ao
  plano são **4 toques**.
- **Sou contra a "tela única"** (01, 03, 04, 06, 10). Com os componentes de hoje ela mede cerca de 1.700 px. Para caber nos 750–800 px
  prometidos, os botões de 140–176 px teriam de virar chips de ~56 px, e a tela vira formulário, justo a cara de "não profissional"
  que o José criticou. Além disso, deixar "Não sei" já marcado na terra transforma a resposta que mais mexe nas datas num padrão que
  ninguém escolheu.
- A **linguagem visual única** (a minha 1ª ideia) continua sendo o que mais tira a cara de amador por hora de trabalho: cerca de 1 h
  em `quadra.css`, e as 16 telas mudam juntas.
- Mudei de ideia em 7 pontos (seção 6).

---

## 1. As melhores ideias dos outros

| Lente | Ideia | Por que é boa |
|---|---|---|
| 04 Júri | O selo traz a missão: "MEDIDO · NASA GPM" | Hoje a palavra NASA aparece 0 vezes na jornada. A fonte já vai como 2º argumento de `selo()` (`comum.js:24-27`; ex.: "GPM IMERG via NASA POWER"), e uma regra curta tira dali a sigla. Junto com o meu selo no rodapé do cartão, fica discreto e conta de onde veio o número sem abrir nada. |
| 06 Arquitetura | Cada "mudar" abre **a** pergunta certa e volta à tela de onde veio; o voltar do Android passa a funcionar | Hoje todo chip leva à 1ª das 11 telas (`perguntas.js:77` zera tudo). Botão que leva ao lugar errado é a sensação mais "amadora" que existe. |
| 09 Celular | Travar o toque duplo | O bug está confirmado: 2 toques em 120 ms pulam a pergunta do tamanho. O motivo está em `perguntas.js:115-120`, que soma `q += 1` antes de redesenhar. Com toque que já avança, essa trava é obrigatória (1 linha). |
| 09 Celular | Teto medido por passo: ≤ 1.900 px e ≤ 150 palavras à vista; alvo ≥ 44 px; `summary` com 22 px de altura vira 44 px; topo de 107 px vira ~60 px | Transforma "enxuto" em critério que dá para conferir no print. |
| 03 Valor da informação | Medir o efeito de cada resposta no `/api/local` e no R$ | Com "máquina e insumos", a sobra vai de R$ 4.364 para −R$ 1.743. Sem maniva, o plano passa a ganhar em 0 de 100. Isso decide o que tem de ficar **visível** junto do número, mesmo não sendo pergunta. |
| 08 Precisão | Corrigir os textos falsos: "Só o que muda a conta" (`hoje_ideal.js:402`), "acima do recorde", "+R$ 909" atribuído ao baixio, raiz "daqui". E mostrar no plano a data que a resposta mudou ("antes: …") | São correções de texto, baratas, e um jurado que testa encontra cada uma. |
| 01 Agricultor | Um número grande por cartão (o típico) e o "ano ruim" pequeno; "não vende" vira "vira comida da criação (fora do R$)"; áreas em "⅓ do roçado ≈ N tarefas" em vez de "0,11 ha"; tirar o selo MEDIDO do tamanho padrão | Deixa uma hierarquia clara (1 herói) e acaba com o "o satélite mediu o meu roçado?". |
| 01 / 02 / 06 / 10 | A prioridade junta-se às abas de "Outros jeitos": um seletor só | Hoje são dois seletores da mesma escolha: "O que vale mais" no topo e as abas Água · Renda · Solo · Plano lá embaixo, ligados por `DA_PRIORIDADE` (`cenarios.js:18`). Dois controles para uma escolha é ruído visual. |
| 10 Simplicidade | Baixio pequeno, ⅓ e metade mandam o mesmo pedido à API | Conferido em `roca.js:47`: todos viram `ad_baixio=15`; o tamanho só muda a área no navegador. Com isso dá para tirar uma opção sem perder nada. |
| 02 Produto | Um indicador de progresso só, e o cabeçalho sem "terra: não sei" | No topo de hoje cabem duas fileiras de fichas com "não sei" (`folha2.png`): parece produto inacabado. |
| 04 Júri | Números vizinhos que não batem: 590 / 568 / 567 mm, mar +2,46 / +2,5 °C | Para o júri, inconsistência pesa mais que falta. Um rótulo e um número por fato. |
| 05 / 09 | "Mandar no WhatsApp" é o verde final; "Imprimir" vira secundário | No Android simples, `window.print()` confunde. E o fim natural da jornada é o técnico (ponto 16). |

---

## 2. Objeções

| Lente | Ideia | Objeção concreta |
|---|---|---|
| 01, 03, 04, 06, 10 | **Tela única "Sua roça"** com 3 a 5 blocos | **Conta da altura com os componentes atuais**, a 390 px: título ~176 px. Culturas: 6 botões `.hi-opcao` de 150 px (`hoje_ideal.css:31`) em 2 colunas, que dão 474 px. Terra e baixio: 4 botões `.opcao` de 140 px (`perguntas.css:61`) em 2×2, que dão ~292 px cada. Área ~200 px (print 09). Rótulos e espaços ~250 px. **Total ≈ 1.700 px**, ou 2,2 telas: o próprio 06 aceita ≤ 1.800 px. Para caber em ~750 px (01) ou ~760 px (10), seria preciso um chip novo de ~56 px, que é **formulário**: mata o botão grande com ícone, que é o elemento mais parecido com a tela inicial (o pedido do José) e o melhor para quem lê pouco. O 03 já admite ~1.300 px para 5 blocos. |
| 01, 06, 10 | Terra e baixio **pré-marcados em "Não sei"** na tela única | A terra é a resposta que mais muda as datas: 13 de 13 janelas em Quixadá (08) e 33 de 36 municípios (03). Com "Não sei" já marcado e um botão verde fixo, a maioria segue sem responder. O plano cai então na interseção dos solos, que o 08 mostrou ser enganosa (o milho fica sem janela em terra arenosa em 421 municípios, e o "não sei" não avisa). Uma pergunta por tela **obriga a escolher**, e "Não sei" continua sendo uma escolha honesta. |
| 02 Produto | O resumo vira a 1ª tela, com 4 fichas | A 1ª tela mostraria "Terra: não sei" e "Baixio: não sei", o mesmo ar de incompleto que o 02 aponta no cabeçalho. Quem lê pouco não vê uma ficha como pergunta: confirma sem ler. É a opção mais barata, mas é a que menos personaliza a terra. Reordenar os passos (lugar para a posição 5) também quebra ~15 links, como o próprio 02 admite. |
| 03 Valor da informação | Bloco da maniva "só quando o plano tem mandioca", na mesma tela | Só se sabe se o plano tem mandioca **depois** da terra e do baixio. O bloco apareceria ou sumiria enquanto a pessoa responde, e a tela pula. Melhor pôr a maniva na linha da mandioca do plano. |
| 03, 08 | Prioridade / "Seu jeito de trabalhar" **antes** do número no passo 4 | Repete o erro de hoje: controles antes do resultado (o herói está em y ≈ 1.300 px). As suposições vão para **uma linha embaixo do número**, com "mudar", não para controles acima dele. |
| 04 Júri | A terra vai para o passo 3, ao lado das datas | É ótimo para a demo (a data muda na frente do júri), mas a terra fica opcional e quase ninguém vai achar. Fico com a terra na pergunta e o "antes: …" ao lado da data (08). |
| 04, 08, 09, 03, 05, 06 | O passo 1 continua na frente (≤ 1.100 a 1.800 px) | A manchete do El Niño do passo 1 é **a mesma frase** do painel do globo: "Em 7 de cada 10 municípios do Ceará…" (`rocacerta.js:169` e `01_passo1_lugar.txt:9`). Ver a mesma tela duas vezes antes da 1ª pergunta é o que dá a sensação de "isso não acaba". O júri já tem o globo, as camadas e o painel. Proposta: o passo 1 vira a última aba, "Do espaço", juntando a página "Como o QUADRA sabe" do 04 (sem rota nova). |
| 05 Extensionista | Nova pergunta "Tem criação?" | Na v1 ela só muda texto: é exatamente a "pergunta desnecessária" de que o José reclamou. O problema de verdade ("sorgo/palma sem preço") se resolve com a frase do 01: "vira comida da criação (fora do R$)". |
| 05 Extensionista | "Terra rasa, de piçarra" (AD1) | Tira o milho da terra alta do zoneamento e não foi testada em 7 municípios. Na véspera, só com teste. Visualmente, 5 opções deixam um botão órfão na grade 2×2. |
| 08 Precisão | Opção "Tenho baixio, e o milho já vai lá" | São duas perguntas num botão só (tem baixio? onde vai o milho?), e o texto não cabe num botão de 140 px a 390 px. O arranjo fica no cartão Hoje do Dinheiro. |
| 08 Precisão | "E se chover…" no "ver mais" | Esconde o ponto 13 e o controle mais visual do produto. Fica à vista na Segurança (04, 06). |
| 08 Precisão | Mexer em `motor.py` para o "não sei" honesto | Na véspera, só o texto no front ("só em terra que segura água"), sem mudar o núcleo. |
| 09 Celular | Botão "Ouvir" em toda pergunta e manchete | Um controle a mais em cada tela, e muito Android simples não tem voz pt-BR. Fica para depois da entrega. |
| 09 Celular | Arranjo (junto / pedaços / milho no baixio) na P1 | "Milho no baixio" aparece antes de perguntar o baixio: é a ordem errada que 01, 06 e 08 apontaram. Vai para o cartão Hoje. |
| 09 Celular | Tamanho só como chip no topo do plano | O pedido do José ("opção por hectare") sai do caminho. Fica como **linha da P1**: "Seu roçado: uns 1 ha · mudar". |
| 10 Simplicidade | Barra de baixo com a frase do ponto 16, "Ajustar o roçado" e pílulas | São três coisas numa barra fixa, que já come 29 % da tela (09). A frase do ponto 16 vai para o fim de cada aba. |
| 06 / 10 / 07 (eu) | Barra de abas embaixo | Cabe, mas disputa as 4–6 h com o que mais importa. Abro mão: as pílulas de cima ganham rótulo e a barra de baixo fica com 1 botão verde. |

---

## 3. Votos

| Item | Voto | Para onde |
|---|---|---|
| hoje.culturas | **manter** | P1 "O que você planta hoje?": 6 botões com milho e feijão já marcados, sem a divisão em % (fica dividido igual; o % vai para "Ajustar a conta") e sem o "sem preço aqui" embaixo do botão |
| hoje.arranjo | **mover** | Chip "tudo junto · mudar" no cartão Hoje do Dinheiro (depende do baixio, que já foi respondido) |
| hoje.manejo | **opcional** | Link "Afinar o meu jeito" no cartão Hoje, que reabre a tela que já existe (`telaManejo`), com o subtítulo falso trocado |
| hist.anos | **inferir** | 2026 = jeito de hoje; 2025 = igual. Frase condicional no cartão "Por onde começar o giro" com 1 toque: "Em 2025 foi diferente?" |
| hist.deu | **mover** | Segurança, "A sua memória e os dados": "Lembra de um ano que quebrou?", com os anos do IBGE em chips, ali mesmo. "Deu bem" sai |
| hist.faz | **cortar** | Palhada, esterco e faixas saem. A palavra "como prepara a terra" é reaproveitada no custo |
| terra | **manter** | P2, uma tela, 4 botões 2×2 (Seca rápido · Segura · Encharca · Não sei), sem nada pré-marcado; o toque avança. No plano, a data mostra "antes: …" |
| ha | **fundir** | Linha da P1: "Seu roçado: uns 1 ha (típico daqui) · mudar", que abre `area.js` ali mesmo; sem selo MEDIDO no padrão |
| baixio | **manter** | P3, 4 mini-desenhos 2×2 (Não tenho · Pequeno · Grande · Não sei); o toque leva ao plano |
| agua | **mover** | Chip opcional "Tenho barreiro ou poço" no "Leve para o técnico"; sai da ficha do topo |
| maniva | **inferir** | Mandioca na P1 → "já plantada"; senão, "consigo". Linha visível (não link miúdo) na Parte A do plano: "Sem maniva? Trocar" |
| bolso.prioridade | **fundir** | Um seletor só: as abas de "Outros jeitos de girar", logo abaixo do herói, com "garantir" já aceso no El Niño |
| bolso.raiz | **mover** | "Ajustar a conta" (fechado). A hipótese fica escrita embaixo do herói: "raiz a R$ 0,84/kg · mudar" |
| bolso.custo | **fundir** | "Paga trator ou adubo? Não / Sim" em "Ajustar a conta", com a hipótese escrita embaixo do herói ("só a semente · mudar") |
| bolso.gs | **cortar** | 1 linha no "Leve para o técnico": "Até 5 ha você cabe no Garantia-Safra" |

---

## 4. Fluxo preferido: o do 09, com emendas

```
Globo → Painel → [Montar o meu plano · 3 perguntas] → P1 → P2 → P3 → Plano · Rende · Seca · Do espaço
         toque 1                                       2     3     4
```

| # | Tela | Na tela | Ação |
|---|---|---|---|
| 0 | Globo + painel | Sem mudança | "Montar o meu plano · 3 perguntas" → `#/<cod>/2` (`principal.js:94`, `rocacerta.js:333`) |
| P1 | "O que você planta hoje?" | 6 botões (milho e feijão marcados), com `.hi-opcao` de 120 px nesta tela para caber em ~800 px; linha "Seu roçado: uns 1 ha · mudar"; contador "Sua roça · 1 de 3" | "Seguir", o único verde, fixo embaixo. A barra "Voltar / Como plantar" some no passo 2 inteiro (hoje a regra `perguntas.css:73` só vale para `.quiz`) |
| P2 | "Quando chove forte, como fica a sua terra?" | 4 botões 2×2 e 1 linha do torrão, sem caixa | O toque avança, com a trava do toque duplo; voltar no topo à esquerda |
| P3 | "Tem uma parte baixa que fica úmida?" | 4 mini-desenhos 2×2 | O toque abre o plano (`ctx.ir(3)`), sem a tela "Pronto" |
| 3 | Plano | Linha de respostas ("terra misturada · 1 ha · baixio pequeno · mudar", em que cada palavra abre a sua pergunta e volta); o roçado de cima 2027/28/29; "O que fazer agora" (3 ações); "Por onde começar" condicional; "Sem maniva? Trocar" na Parte A. O resto vai para uma lista "Ver mais", cada item com manchete de 1 linha visível | "Quanto rende →" |
| 4 | Rende | Herói Hoje → Melhor → Ideal (1 número grande por barra, o típico, e o ano ruim pequeno) e, embaixo, a linha "Conta com: só a semente · raiz R$ 0,84/kg · milho + feijão, tudo junto · mudar". Depois os ajustes do Melhor e "Outros jeitos" (que fazem as vezes da prioridade). "Ajustar a conta" fica fechado. Sai o 2º herói "No caso ruim…" | "Se secar →" |
| 5 | Seca | "2027 tende a ser apertado"; "E se chover…" aberto; 1 linha por cultura em 2027 (2028–29 a 1 toque); "Olhamos de novo em 19/mar e 30/abr"; "Leve para o técnico" | "Mandar no WhatsApp" (verde); "Imprimir" é link |
| 6 | Do espaço (ex-passo 1, última aba) | El Niño, tendências em grade 2×3, régua, cardápio em lista, confiança, satélite × pluviômetro, harmonização, os 7 métodos (página do 04 dentro desta aba) | "Voltar ao meu plano" |

**As 8 emendas ao 09**
1. Entrada direta em `#/<cod>/2`; o passo 1 vira a última aba, "Do espaço" (o painel já disse o El Niño com a mesma frase).
2. O tamanho vira linha da P1 (pedido do José à vista; 1 tela a menos).
3. O arranjo sai da P1 e vai para o cartão Hoje.
4. Baixio com 4 opções em vez de 5: a grade 2×2 fecha sem botão órfão, e ⅓ e metade já davam o mesmo pedido à API.
5. A navegação do 06: "mudar" abre a pergunta certa e volta, e o voltar do Android funciona.
6. O selo do 04 no meu formato: "● Medido · NASA GPM", 11 px, no rodapé do cartão; a fonte por extenso no "ver como", porque no toque o `title=` não abre.
7. A linha de suposições embaixo do herói do Rende, no lugar dos 4 controles em cima.
8. Sem "Ouvir" e sem abas embaixo na v1.

**A linguagem visual continua a do meu parecer** (`../07_visual.md`, seção 6): Inter em tudo, Fraunces só no número-herói, o mono
sai dos rótulos, 1 verde por tela, nada de cartão dentro de cartão, nada rolando de lado, `.eco` em `--muted` (hoje é `--ink-4` =
0,34, `quadra.css:87,90`), nada abaixo de 12 px. Também tirar a cor âmbar da barra "Melhor": hoje o âmbar é ao mesmo tempo
"Melhor", SUPOSIÇÃO, El Niño e o alerta "sugerido: garantir" (`folha2.png`). A escala passa a ser Hoje cinza, Melhor verde-claro e
Ideal verde.

**Ordem de trabalho (≈ 5,8 h)**: `quadra.css` (1 h) → `perguntas.js` com P1 sem %, PERG = [terra, baixio de 4], sem histórico e sem
resumo, trava do toque duplo e linha do tamanho (1,5 h) → link do globo e rótulos das pílulas (0,5 h) → `dinheiro.js` com herói
primeiro, linha de suposições, prioridade nas abas e herói duplicado cortado (1 h) → `plantio.js` e `seguranca.js` com "ver mais",
maniva, memória e chuva em cima (1 h) → `selo()` (0,3 h) → prints e `percorrer_fluxo.py` nos 7 municípios (0,5 h).

---

## 5. Linhas vermelhas (o que não pode ser cortado)

1. **1 botão primário por tela** e nenhuma tela com duas navegações ao mesmo tempo.
2. **Contador honesto**: o botão diz "3 perguntas", são 3, e há um contador só.
3. **Selo em todo número-chave**: 1 por cartão, no rodapé, ≥ 11 px, com a fonte legível no toque. "Enxuto" não pode tirar a transparência.
4. **Jeito de hoje e tamanho à vista antes do plano** (pedidos do José), e o Hoje → Melhor → Ideal como herói do Rende.
5. **Terra e baixio perguntados de verdade**, sem "Não sei" já marcado; a data que a resposta mudou aparece no plano.
6. **Ponto 16 visível sem abrir nada**: "Leve para o técnico" e "quem decide é você" em toda tela de resultado.
7. **Ponto 13 ("E se chover…") à vista** na Seca. Os pontos 8, 10 e 12 com manchete de 1 linha visível, mesmo dentro de "ver mais".
8. **Nada rola de lado a 390 px**; alvos ≥ 44 px; 2ª linha do título com contraste ≥ 4,5:1.
9. **A hipótese do R$ escrita embaixo do número** (custo, raiz). Sem isso, o número engana quem paga trator: a sobra de R$ 4.364
   vira −R$ 1.743 (medido pelo 03).
10. **Nada no `motor.py` nem no `servidor.py` na véspera**: as correções de precisão entram como texto no front.

---

## 6. Onde mudei de ideia, e por quê

1. **Tamanho**: deixa de ser a 4ª tela e vira linha da P1 (do 09 e do 10). Sai 1 tela, a pessoa chega ao plano em 4 toques, e o
   pedido da área continua à vista.
2. **Baixio**: passa de 3 para 4 opções. Pequeno, ⅓ e metade mandam o mesmo pedido (`roca.js:47`); 4 mini-desenhos fecham a grade 2×2
   e reaproveitam o que existe, sem construir um controle de tamanho no desenho do plano, como eu tinha proposto.
3. **Prioridade**: sai do topo do Dinheiro e vai para as abas de "Outros jeitos" (do 01, 02, 06 e 10). Os dois controles escolhem a
   mesma coisa (`DA_PRIORIDADE`), e com o herói mostrando sempre o típico ela não precisa ficar acima do número.
4. **hist.faz e manejo**: eu tinha proposto juntar os dois numa lista "O que você já faz". Agora as práticas são cortadas e o manejo
   fica opcional, na tela que já existe. Uma lista de práticas que não muda nada (Δ R$ 0, medido pelo 03) seria mais uma tela que o
   José chamaria de desnecessária.
5. **"E se chover…"**: sai do "ver mais" e vai para a 1ª dobra da Seca (do 04 e do 06). É o controle mais visual do produto e cobre o
   ponto 13.
6. **Abas embaixo**: abro mão para caber no prazo. As pílulas de cima ganham rótulo (Plano · Rende · Seca · Do espaço) e a barra de
   baixo fica só com o botão verde.
7. **Selo**: além de ir para o rodapé, passa a dizer a missão (do 04). É a forma mais barata de a NASA aparecer em toda tela.

**Onde não mudei**: o passo 1 fora do caminho e a pergunta por tela em vez da tela única. Os dois motivos estão na seção 2 (a frase
repetida do painel e a conta de ~1.700 px).
