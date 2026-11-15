# 10 · Simplicidade radical (advogado do diabo) · rodada de debate

Pergunta usada em tudo: **se tirar, o que se perde?** Li as 10 propostas e conferi no código o que estava em disputa
(`roca.js:16-51`, `perguntas.js:72-129`, `dinheiro.js:77-171`, `cenarios.js:18`, `historico.js:355-437`, `seguranca.js:219`,
`hoje_ideal.js:402`, `comum.js:24-26`).

## Veredito em 4 linhas

1. **O melhor fluxo é o da lente 01 (Agricultor)**, com emendas das lentes 04, 03, 09 e 08. É o mais curto que ainda cumpre os
   três pedidos do José. Também é o mais barato: não renumera rotas nem mexe no núcleo, e já traz um plano B.
2. Há consenso quase total no que importa: **uma tela de perguntas já marcada com o típico daqui**, o resultado logo no começo de
   cada passo, um botão principal por tela e nenhuma pergunta que não muda nada.
3. A disputa real é se o passo 1 fica na frente. **Mantenho que sai do caminho**: o painel do globo já conta o El Niño, e o selo
   "NASA" da lente 04 cobre o júri em todas as telas.
4. Abas, troca de fonte em todo o site, botão "Ouvir" e pergunta da criação são bons, mas **não cabem com segurança em 4–6 h na
   véspera**. Ficam depois do núcleo.

## 1. As melhores ideias dos outros

| Lente | Ideia | Por que entra |
|---|---|---|
| 01 Agricultor | Entrar direto em `#/<cod>/2` e mudar só a entrada, sem renumerar os passos. O passo 1 vira "Do espaço", opcional | Corta 4.550 px e cerca de 8 rolagens antes da 1ª pergunta. `principal.js` e `rocacerta.js` só trocam o link. As rotas e os links antigos continuam iguais |
| 01 Agricultor | Plano B: se faltar tempo, manter as telas de hoje com a entrada direta, as 4 perguntas obrigatórias primeiro e o resto atrás de "Afinar" | É a única proposta com saída para o prazo de 15/11, 23:59 |
| 01 Agricultor | "Paga trator ou adubo? Não / Sim" no lugar de "O que você paga" | É a pergunta de custo dita com as palavras dele e mapeia exatamente nos 2 níveis de `dinheiro.js:47`. Melhor que o meu "preparo → custo" (ver §6) |
| 01 Agricultor | "Não vende" vira "vira comida da criação (fora do R$)" | Resolve o problema do sorgo e da palma que a lente 05 viu, sem pergunta nova |
| 01 Agricultor | Tirar o selo MEDIDO da área padrão | "1,03 ha MEDIDO" dá a entender que o satélite mediu o roçado dele. O certo é "típico daqui (Censo 2017)" |
| 01 / 09 | Um número grande por cartão: o típico. O caso ruim fica em letra menor | Hoje, com "garantir", o número grande vira o p10 (`dinheiro.js:147-149`) e a barra mostra o p50: os números brigam entre si |
| 01 + `cenarios.js:18` | A prioridade e as abas de "Outros jeitos" são **a mesma escolha** (`DA_PRIORIDADE = {garantir:"agua", vender:"renda", equilibrar:"plano", solo:"solo"}`) | Conferido no código. Fundir apaga um dos dois seletores do passo 4 |
| 02 Produto | "É assim o seu roçado?": o padrão do Censo já marcado e 0 toques para confirmar | É o princípio certo, que eu aplico como linhas na própria tela, não como fichas que abrem outras telas |
| 02 Produto | Tirar a fileira de fichas "terra: não sei · baixio: não sei" do topo dos passos 3–5 e deixar 1 chip ("1 ha · milho + feijão · Ajustar") | Hoje o topo mostra "não sei" em toda tela (`roca.js:111-113`) e parece formulário incompleto |
| 03 Valor da informação | Medir o efeito de cada resposta antes de decidir. A maniva "não" muda o veredito (98 → 0 de 100) e o custo vira a sobra (R$ 4.364 → −R$ 1.743) | É a base mais firme do debate. Mostra que maniva e custo não podem sumir, só ficar no lugar certo |
| 03 Valor da informação | Pedir a maniva só quando o plano tem mandioca; se a mandioca foi marcada no jeito de hoje, vale "plantada" | Torna a pergunta condicional sem tela nova |
| 04 Júri | Selo "MEDIDO · NASA SMAP" a partir do texto da fonte (`comum.js:24-26`) | A palavra NASA aparece 0 vezes nos 16 textos da jornada (`grep`). Uma função muda todas as telas, e o passo 1 não precisa ficar na frente para o júri |
| 04 Júri | "E se chover…" (ponto 13) visível no alto do passo 5 | É a interação mais forte para a demo, e hoje fica em y ≈ 5.000 px. Eu tinha posto num "ver mais": mudei (§6) |
| 04 Júri | Juntar harmonização, satélite × pluviômetro, os 7 métodos e a confiança num lugar só | Entra dentro do "Do espaço" da lente 01, sem página nova |
| 04 / 08 | Igualar os números vizinhos (590/568/567 mm; "forte", "muito forte", "acima do recorde") | Conferido: `seguranca.js:219` diz "acima do recorde" com +2,46 contra o recorde de +2,59. Um jurado que repara perde a confiança no resto |
| 06 Arquitetura | Cada "mudar" volta à pergunta certa e de lá ao passo de origem, nunca à 1ª de 11 telas | Na tela única isso fica de graça: "mudar" leva a `#/cod/2` e rola até a linha certa |
| 06 Arquitetura | A jornada termina em "Mandar para o técnico", não em "Outro lugar" (`roca.js:121,227`) | Ponto 16 como última ação |
| 08 Precisão | Corrigir o rótulo do "+R$ 909 milho só no baixio": o ganho vem do feijão posto no lugar do milho (`hoje_ideal.js:103-106`) | Um número mal atribuído no herói do passo 4 é o tipo de coisa que derruba a credibilidade |
| 09 Mobile | O toque duplo pula a pergunta do tamanho (`perguntas.js:115-120`, `q += 1` antes de a tela mudar) | Erro medido. Some com a tela única. Se ficar o plano B, precisa travar os botões |
| 09 Mobile | Limite medido por passo: até 3 rolagens (≤ 1.900 px a 390 px) e até 150 palavras à vista; `.eco` com contraste 4,9:1; `summary` com 44 px | É um critério de "pronto" que dá para conferir com `percorrer_fluxo.py`, e não opinião |

## 2. Objeções concretas

| Lente | Ideia | Objeção |
|---|---|---|
| 02 Produto | `PASSOS = [perguntas, plantio, dinheiro, seguranca, lugar]`, com renumeração | Quebra uns 15 links (`ctx.link(n)`, `data-ir`, o atalho do técnico) e o `percorrer_fluxo.py` na véspera. Mudar só a entrada (lente 01) tem o mesmo efeito sem esse risco |
| 02 Produto | O resumo como 1ª tela, com fichas que abrem as telas de pergunta que já existem | Cada mudança custa 3 toques (abrir, escolher, voltar) e depende de `fase/q/telaForcada`, que a própria lente 02 aponta como risco do "Anterior". Linhas na própria tela custam 1 toque |
| 03 / 08 | A prioridade como 1º controle do passo 4, antes do herói | Volta o problema de controle antes do resultado (o herói hoje está na rolagem 3, medida da lente 09). Ela só decide o número grande porque `dinheiro.js:147` troca p50 por p10; com um número fixo, ela passa a só acender um jeito |
| 05 Extensionista | Pergunta nova "Tem criação?" | Na v1 ela só muda texto (a própria lente admite), e o pedido do José é **menos** pergunta. O texto "vira comida da criação" resolve o mesmo problema sem perguntar |
| 05 Extensionista | Opção "Rasa, de piçarra" (AD1) | Tira o milho do zoneamento da terra alta e não foi testada nos 7 municípios. Mudar o plano de quem marca essa opção na véspera é arriscado. Fica para depois |
| 05 / 07 / 08 / 09 | Assistente de 3 a 6 telas, com o toque que já avança | Funciona, mas cada tela é uma chance a mais do toque duplo (09), de contador e de voltar quebrado. A tela única chega ao plano com 1 toque. Se o time preferir assistente, usar o de 3 telas da lente 09 com botão travado |
| 05 / 08 / 09 / 03 / 04 / 06 | Deixar um passo 1 curto na frente | É mais uma tela entre o painel e o plano repetindo o El Niño (`rocacerta.js:3-5` contra `lugar.js:50-74`). O selo NASA da lente 04 e o "Do espaço" a 1 toque cobrem o júri. **Aceitável como recuo**: no máximo 1 tela e botão visível sem rolar |
| 06 Arquitetura | `ctx.editar(k)`, cada tela como entrada no histórico, funil de 3 pontos e abas | É engenharia de navegação de 2 h ou mais. Com a tela única, o voltar do Android só precisa funcionar entre passos, o que já acontece |
| 07 Visual | Trocar o mono pela Inter em todo o CSS (74 usos de `var(--mono)`), raios e tamanhos | Mexe nas 16 telas na véspera; a lente 07 estima 1 h, mas desalinha linhas do tempo e tabelas. Agora só `.eco` (contraste) e a fonte do botão. O resto depois |
| 07 / 08 / 09 / eu (antes) | "E se chover…" num "ver mais" | Esconde o ponto 13, que é o melhor momento da demo (04). Fica visível |
| 08 Precisão | Corrigir no `motor.py` o "não sei" da terra (interseção que ignora solo não zoneado) | O achado é verdadeiro e importante, mas mexer no núcleo na véspera quebra a regra do briefing. Agora: frase na tela ("vale para terra que segura água; na areia, confira"). O motor fica para depois da entrega |
| 08 Precisão | Água, custo e prioridade num bloco "Seu jeito de trabalhar" **antes** do herói | Mesmo problema da prioridade: 4 controles antes do número. Vão para depois do resultado |
| 09 Mobile | Botão "Ouvir" (speechSynthesis), módulo novo | Bom para pouca leitura, mas são 45 min fora do núcleo e falham num Android sem voz pt-BR. Entra só se sobrar tempo |
| 09 Mobile | Baixio com 5 desenhos (Não · Pequeno · ⅓ · Metade · Não sei) | Pequeno, ⅓ e metade mandam o mesmo `ad_baixio=15` para a API (`roca.js:49`). Bastam 3 opções; o tamanho vai para "Afinar" |
| 01 / 02 / 07 / eu (antes) | Fundir o preparo da terra com o custo (trator = "máquina e insumos") | É um mapeamento aproximado: quem aluga trator para gradear não paga necessariamente o adubo. Como o custo vira a sobra de +R$ 4.364 para −R$ 1.743 (03), um palpite errado inverte o veredito. A pergunta direta da lente 01 é exata |

## 3. Votos

| Item | Voto | Para onde |
|---|---|---|
| hoje.culturas | **manter** | Tela única "Seu roçado", linha 1. Milho e feijão já marcados ("o mais comum daqui"). Sem os botões de %: divide igual e a barra colorida fica visível. "Quanto de cada" vai para Afinar |
| hoje.arranjo | **inferir** | "Tudo junto" como padrão. Muda no chip "Hoje: milho + feijão, tudo junto · mudar" do cartão Hoje (passo 4) e no Afinar |
| hoje.manejo | **inferir** | Padrões: 1ª chuva = comum; semente pelo Censo (`hoje_ideal.js:35`); fogo = o plano já diz "sem fogo". Frases condicionais. Afinar opcional. Sai o "Só o que muda a conta" (`hoje_ideal.js:402`, falso) |
| hist.anos | **inferir** | 2026 = jeito de hoje; 2025 = igual, com o selo SUPOSIÇÃO. O cartão "Por onde começar o seu giro" usa frase condicional ("Se em 2025 também foi milho…") com "Foi diferente? Sim / Não" na própria linha. Sai o "Contar", que manda ao passo 2 |
| hist.deu | **mover** | Passo 5, "A sua memória e os dados". Os chips dos piores anos do IBGE ("milho quebrou em 2012?") gravam o `exp` ali mesmo (`historico.js` já tem `escreverExp`), sem `ctx.link(2)`. "Deu bem" sai |
| hist.faz | **cortar** | Palhada, esterco e faixas não são lidos por nenhum código; fogo e semente repetem o manejo. O preparo não vira custo (§2) |
| terra | **manter** | Tela única, linha 4: Seca rápido · Segura · Encharca · Não sei (já marcado), com o torrão em 1 linha. É a única entrada que muda as datas e que não dá para inferir sem mapa de solo (03) |
| ha | **manter** | Tela única, linha 2: chips ½ · 1 · 2 · 3 · 5 ha, com o típico do Censo marcado, "≈ N tarefas" e "outra medida" (`area.js`). Rótulo "típico daqui (Censo 2017)", sem MEDIDO |
| baixio | **manter** | Tela única, linha 3: Tenho · Não tenho · Não sei, com o mini-desenho. O tamanho vai para Afinar (mesmo `ad_baixio`) |
| agua | **mover** | Chip em "Leve para o técnico" ("tenho barreiro ou poço perto"), que vira uma pergunta na ficha. Também no Afinar. Sai a frase falsa "muda o que dá para salvar" (`perguntas.js:30`) |
| maniva | **inferir** | Mandioca marcada na linha 1 → "plantada"; sem mandioca → "consigo". Na linha da mandioca (Parte A) do plano: "Já está no chão · Não consigo maniva? trocar", e o plano se refaz. Aparece só quando o plano tem mandioca |
| bolso.prioridade | **fundir** | Com as abas de "Outros jeitos de girar" (mesmas 4 escolhas, `cenarios.js:18`), logo abaixo do herói. No El Niño, vem "garantir". O número grande fica sempre o típico |
| bolso.raiz | **opcional** | "Afinar a conta" (fechado), no passo 4. O padrão é a mediana do estado (MEDIDO), com o "seu olho" da casa de farinha |
| bolso.custo | **opcional** | "Afinar a conta": "Paga trator ou adubo? Não / Sim" |
| bolso.gs | **cortar** | Sai o controle de 3 botões (não entra na conta, `dinheiro.js:129`). Fica o chip deduzido da área: "Garantia-Safra: com até 5 ha você cabe", no técnico |

**Saldo:** antes do plano, 4 linhas numa tela, todas já marcadas. A tela não é uma pergunta por vez. A personalização que muda o
plano continua inteira: culturas, tamanho, baixio e terra antes; maniva na própria linha da mandioca.

## 4. O fluxo que defendo: o da lente 01, com emendas

```
Globo → município → painel Roça Certa → [Montar o meu plano]          (toque 1)
  → #/<cod>/2  "Seu roçado"  (1 tela, 4 linhas já marcadas)  → [Ver o meu plano]   (toque 2)
  → 3 Seu plano → 4 Quanto rende → 5 Se secar → [Mandar para o técnico]
  "Do espaço" (o passo 1) a 1 toque, fora do caminho
```

1. **Painel do globo** (sem mudança visual): o link passa a `#/<cod>/2` (`principal.js:94`, `rocacerta.js:333`) e o texto vira
   "Montar o meu plano". Nada de "3 toques" ou "5 perguntas" no botão: número prometido é número cobrado.
2. **Seu roçado** (`perguntas.js`, cerca de 800 px):
   - título "Quixadá, CE · Seu roçado" e o eco "Já marcamos o comum daqui. Mude o que for diferente.";
   - linhas: 1) o que vai no roçado; 2) tamanho; 3) baixio; 4) terra;
   - "+ Afinar (opcional)" fechado no fim;
   - **um** botão fixo embaixo, "Ver o meu plano →". Sem contador, sem resumo "Pronto", sem a barra "Como plantar →";
   - tocar numa opção grava com `ctx.set` e não muda de tela, então o toque duplo não pula nada;
   - reaproveita `opcao()`, `AREA.render` e a grade de culturas de `hoje_ideal.js`;
   - as chaves do `PADRAO` ficam iguais.
3. **Seu plano** (passo 3, meta ≤ 1.900 px):
   - 1 chip no topo: "1 ha · milho + feijão · Ajustar", que volta a `#/cod/2`;
   - manchete e uma frase de El Niño ("plante metade, guarde metade");
   - o roçado visto de cima, depois "O que fazer agora" (3 itens) e o cartão do giro com a frase condicional;
   - a maniva fica em linha na Parte A;
   - "Por que este plano": 3 sanfonas, cada uma com 1 linha à vista (onde sofre, faixas × praga, o que cada planta faz);
   - sem "?" no desenho;
   - áreas em "⅓ do roçado ≈ N tarefas".
4. **Quanto rende** (passo 4, meta ≤ 1.900 px):
   - o herói Hoje → Melhor → Ideal no alto, com um número grande (o típico) e o caso ruim pequeno;
   - logo abaixo, "Outros jeitos", com a prioridade dentro;
   - fechados: "Afinar a conta" (raiz, trator ou adubo) e "Ver ano a ano" (El Niños, caixa, paga o gasto);
   - **sai o `heroiHtml`** (`dinheiro.js:145-190`), que repete o herói;
   - corrigir o rótulo do +R$ 909.
5. **Se secar** (passo 5, meta ≤ 1.900 px):
   - manchete "2027 tende a ser apertado; 2028 e 2029, normais";
   - **"E se chover…" aberto** e 2027 em 1 linha por cultura (2028 e 2029 a 1 toque);
   - "Olhamos de novo em 19/mar e 30/abr", depois a memória com os chips dos anos do IBGE;
   - por último, **"Leve para o técnico"**, com o chip da água, o da Garantia-Safra e o botão verde "Mandar no WhatsApp";
   - corrigir "acima do recorde" (`seguranca.js:219`).
6. **Do espaço** (o passo 1 sem o CTA de perguntas): fica tudo o que tem hoje, mais os 7 métodos e "quanto já acertou"
   (`seguranca.js:361,387`). Entra pelo link "Como sabemos (dados da NASA)" no topo e no fim do passo 5.
7. **Em todas as telas:** o selo com a missão ("MEDIDO · NASA SMAP", até 10 caracteres depois do ponto), um botão verde por tela,
   a faixa do ponto 16 em 1 linha e `.eco` com contraste 4,9:1.

**Toques até o plano:** 2 depois do painel com os padrões, de 4 a 6 respondendo de verdade (hoje são 14, ou de 25 a 30
respondendo).

## 5. Ordem para as 4–6 h (o que corta primeiro se faltar tempo)

| # | O quê | Tempo | Se faltar tempo |
|---|---|---|---|
| 1 | Entrada em `#/cod/2`; a tela única "Seu roçado"; sai a barra "Como plantar →" no passo 2 | 2 h | **Plano B da lente 01:** manter as telas de hoje, entrar direto, as 4 perguntas que mudam o plano primeiro, o resto atrás de "Afinar", contador único e botão travado no 1º toque |
| 2 | Passo 4: herói primeiro, sai `heroiHtml`, prioridade nos "Outros jeitos", número típico fixo, "Afinar a conta" | 1 h | não pode faltar: é o pedido do Hoje → Ideal |
| 3 | Passo 5: "E se chover" e o técnico visíveis, memória em linha, Garantia-Safra como chip, "recorde" corrigido | 45 min | manter a ordem e só subir o técnico |
| 4 | Passo 3: ação primeiro, sanfonas com manchete, maniva em linha, giro condicional | 45 min | só subir "O que fazer agora" |
| 5 | Selo NASA, "Do espaço" fora do caminho, `.eco`, números vizinhos iguais | 45 min | o selo é 1 função: fica |
| 6 | Abas, troca de fonte, "Ouvir", criação, AD1, correção do motor | — | depois da entrega |

Um dono por arquivo (A: `roca.js` + globo + `perguntas.js`; B: `plantio.js` + `historico.js`; C: `dinheiro.js` + `cenarios.js`;
D: `seguranca.js` + `lugar.js` + `comum.js`). Fim: `percorrer_fluxo.py` nos 7 municípios, com o mesmo JSON e o mesmo R$ para as
mesmas respostas.

## 6. Onde mudei de ideia, e por quê

- **Tamanho (ha): de "inferir" para "manter" na tela.** O José pediu essa opção de forma explícita. Como linha de chips já marcada,
  custa 0 toque e fica à vista. A lente 01 também mostrou que o selo MEDIDO no padrão engana.
- **Preparo → custo: abandonei.** Os números da lente 03 (custo inverte a sobra) mostram que um palpite pelo preparo é caro. A
  pergunta direta da lente 01 ("Paga trator ou adubo?") é exata, e o `hist.faz` passa a ser só corte.
- **Prioridade: de "mover" para "fundir".** No código, a prioridade e os "Outros jeitos" são a mesma escolha (`cenarios.js:18`), e
  ela só decide o número grande porque `dinheiro.js:147` troca o típico pelo caso ruim. Com o número fixo, um seletor basta.
- **"E se chover…": de "ver mais" para visível.** A lente 04 tem razão: é o ponto 13 e a melhor interação da demo.
- **Abas: de núcleo para "se sobrar tempo".** Elas não tiram nenhuma pergunta. O ganho vem da tela única e do resultado primeiro.
- **Passo 1: de aba numerada no fim para "Do espaço" fora do caminho, sem renumerar** (lente 01). Dá o mesmo efeito sem quebrar
  links. Continuo contra deixá-lo na frente; o recuo aceitável é no máximo 1 tela, com o botão sem rolar.
- **Maniva: de "mover" para "inferir"** (mandioca de hoje → plantada), com a troca em linha na Parte A. A lente 03 mediu que a
  resposta mexe no veredito, então o padrão precisa vir das respostas dele e ser visível onde age.

## 7. Linhas vermelhas (não podem ser cortadas)

1. **O jeito de hoje** na 1ª tela e o **Hoje → Melhor → Ideal** como herói do passo 4 (pedido do José).
2. **A área à vista** na 1ª tela, com ha, tarefas e medida (pedido do José).
3. **O histórico continua no produto e visível:** 2025 no cartão do giro e o ano que quebrou na memória do passo 5, respondidos
   ali mesmo. Nenhum "Contar" ou "mudar" pode mandar à 1ª tela de perguntas.
4. **As 4 entradas que mudam o plano** (terra, baixio, maniva, culturas) continuam editáveis, a 1 toque de onde aparecem.
5. **O ponto 16:** "Leve para o técnico" visível e como última ação; a faixa "quem decide é você" em todo passo.
6. **O selo em todo número.** Padrão inferido leva "típico daqui" ou SUPOSIÇÃO, nunca MEDIDO para o roçado dele.
7. **Os 16 pontos a 1 toque:** "E se chover…" visível (13); 8, 10 e 12 com manchete à vista; "Do espaço" (1, 2, 3, 6, 7, 11) a 1
   toque e no roteiro da demo.
8. **Nenhuma promessa falsa na tela:** "5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde".
9. **Nada no `motor.py` nem no `servidor.py` na véspera.** As chaves do `PADRAO` e da URL ficam iguais, e o mesmo JSON sai para as
   mesmas respostas.
10. **Um botão principal por tela**, sempre no mesmo lugar.
