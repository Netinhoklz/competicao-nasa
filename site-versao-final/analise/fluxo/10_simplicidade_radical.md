# 10 · Simplicidade radical (advogado do diabo)

Pergunta usada em cada tela, pergunta e bloco: **se tirar, o que se perde?** Se a resposta for "nada que o plano, a conta ou um dos
16 pontos usem", sai da frente. Medido em Quixadá-CE (2311306), a 390 px, com os prints de `E:/campeonato-nasa/tmp/fluxo_atual/`
e a API `/api/local` com e sem cada parâmetro.

## 1. Diagnóstico (com evidência)

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| 1 | O caminho até o plano é longo demais: 12 telas de pergunta + 1 resumo, com pelo menos 14 toques depois de "Montar o plano" (12 só pulando tudo); respondendo de verdade, 25 a 30 | prints `02`–`13`; `perguntas.js` (fases hoje → historico → perguntas) | alta |
| 2 | O botão promete "5 perguntas" e entrega 11 telas + resumo. Os contadores recomeçam três vezes ("1 de 3", "1 de 3", "1 de 5") e ninguém sabe quanto falta. É o que mais passa a impressão de amador | `lugar.js:148`; kicker dos prints `02`, `05` e `08` | alta |
| 3 | Metade das perguntas não muda nada no plano nem na conta | água: não vai para a API (`roca.js:44-51`), só aparece em `leve_ao_tecnico.js:67-68`. Garantia-Safra: "o valor do benefício não entra na conta" (`dinheiro.js:129`). "Deu bem", preparo (trator/animal/enxada) e "guardo a semente" só voltam como eco no resumo (`historico.js:270,286,289`). Palhada e esterco não são usados em lugar nenhum | alta |
| 4 | O plano fica atrás de 4.550 px. O passo 1 vem antes das perguntas, e o botão para seguir está no pé da página | print `01` (altura 4.550 px; CTA em ~4.250 px); `lugar.js:148` | alta |
| 5 | Duas barras de navegação ao mesmo tempo no passo 2, com 4 botões. O "Como plantar →" de baixo pula o resto das perguntas sem avisar. Para avançar e voltar há 7 rótulos diferentes: Próxima, Pular, Pronto, Terminar, "Não sei / pular", Anterior, Voltar | prints `02`, `04` e `09`; `roca.html` (`nav-baixo`) + `quiz-nav` | alta |
| 6 | O "voltar" do Android sai do questionário em vez de voltar uma pergunta. "Contar", "Contar o meu ano ruim" e os "mudar" levam de volta à tela 1 de 11 | estado em variáveis do módulo (`perguntas.js:11-13`); respostas gravadas com `location.replace` (`roca.js:144`); `perguntas.js:77` zera a fase ao entrar; `historico.js:362,374` usam `ctx.link(2)` | média |
| 7 | As páginas de resultado são enormes: 5.625 + 6.629 + 6.377 px (mais o passo 1, 23.181 px ≈ 33 telas de celular), com 2.752 palavras e 31 "Ver…" | `wc -w` dos TXT: 541 / 658 / 721 / 832; alturas no cabeçalho de cada TXT | alta |
| 8 | Repetição. O El Niño aparece 5 vezes: painel do globo, passo 1, "Se 2027 for como…" no passo 4, "Hoje" e "E se chover" no passo 5. O R$ 2.760 × R$ 984 aparece 3 vezes no passo 4. As datas de plantar aparecem 5 vezes (cardápio, resumo, calendário, "Melhor", técnico) | TXT `01`, `13`, `14`, `15`, `16`; `dinheiro.js:145-190` (o herói antigo repete o Hoje → Ideal) | média |
| 9 | O passo 4 abre com 4 controles (o "Seu bolso": prioridade, preço da raiz, custo, Garantia-Safra). O primeiro R$ só aparece por volta de 1.300 px | `dinheiro.js:91` (`abertura + bolso + hi-slot`); mosaico do print `15` | média |
| 10 | A tela "Pronto" (13) repete a ficha de respostas que já fica no topo dos passos 3 a 5 | `roca.js:111-113` | baixa |
| 11 | O "seu olho" aparece 12 vezes, além da faixa fixa e da confiança. O ponto 16 vira ruído em vez de aviso | `grep 'SEU OLHO'`: passos 1, 3, 4 e 5 = 2 + 3 + 3 + 2, mais 2 nas perguntas | baixa |

**O que de fato mexe no resultado (medido na API):**
- **terra:** 95 a 136 campos da agenda e até 3 do plano. Com "areia", o milho perde o zoneamento em Quixadá.
- **baixio = não:** 23 campos do plano (o cereal sai).
- **maniva = não:** 22 campos do plano (o plano gira sem mandioca).
- **baixio = tem:** só a janela do baixio. Pequeno, um terço e metade dão **o mesmo JSON** (`ad_baixio=15`); a diferença fica só na área, calculada no navegador.
- **água:** nada.
- **jeito de hoje:** é a base do "Hoje" no dinheiro (`hoje_ideal.js:146-230`).
- **arranjo:** só a opção "milho no baixio" muda a conta (`areasHoje`); as outras só trocam o texto de um alerta.

## 2. Decisão por pergunta

Regra: **só pergunta antes do plano o que muda o plano ou a conta.** O resto entra no lugar onde o efeito aparece, ou no "Afinar (opcional)".

| Item | Decisão | Para onde | Motivo |
|---|---|---|---|
| hoje.culturas | manter | tela única, pergunta 1, já marcada com milho + feijão ("o mais comum daqui") | É a base do Hoje → Melhor → Ideal (pedido do José). Com a marcação pronta, custa 0 toque |
| hoje.arranjo | opcional | Afinar ("Como fica: junto / em pedaços / milho no baixio") | Só "milho no baixio" muda a conta; o padrão "tudo junto" é o comum |
| hoje.manejo | inferir | padrões: 1ª chuva = comum; semente pelo Censo (73,5% guardam); fogo: o plano já diz "sem fogo" | Só gera alertas de texto; o alerta vira frase condicional ("Se planta na 1ª chuva…") |
| hist.anos | mover | cartão "Por onde começar o seu giro" (aba Plano), 1 toque: "Em 2025 também foi [milho e feijão]? Sim / Não" | 2026 = o jeito de hoje (já está na URL). Só "repetiu milho" vira conselho (`historico.js:128-135`) |
| hist.deu | mover | "Quebrou" → cartão "A sua memória e os dados" (Segurança), em linha, com os anos ruins do IBGE em chips. "Deu bem" sai | "Deu bem" não é usado; "quebrou" só serve à comparação com o IBGE |
| hist.faz | fundir | preparo (trator/animal/enxada) → bolso.custo. Palhada, faixas e esterco saem | Única parte com efeito possível é o equipamento (ponto 15), e hoje nem ele é usado |
| terra | manter | tela única, pergunta 3, com o "aperte um torrão" em uma linha | Muda as datas do ZARC e pode tirar uma cultura (milho em areia) |
| ha | inferir | linha pronta "Roçado: 1,03 ha, o típico daqui (Censo 2017) · mudar" (abre `area.js`: ha, tarefas, medida) | O padrão é MEDIDO; quem quiser muda em 1 toque. Não precisa ser uma tela |
| baixio | manter | tela única, pergunta 2: Tenho / Não tenho / Não sei. Tamanho (pequeno, ⅓, ½) no Afinar | "Não tenho" refaz o plano; o tamanho só mexe na área |
| agua | mover | Afinar e "Leve para o técnico" | Não muda o plano nem a conta; continua como restrição (ponto 15) |
| maniva | mover | na linha da mandioca (Parte A) da aba Plano: "Maniva em fev: consigo / já plantada / não consigo", e no Afinar | Muda o plano, mas o padrão "consigo" vale para a maioria; perguntar onde o efeito se vê |
| bolso.prioridade | mover | cabeçalho do bloco "Outros jeitos de girar" (aba Dinheiro): "O que vale mais pra você?" | É o que acende o jeito recomendado (pontos 9 e 15); o padrão é "garantir" no El Niño |
| bolso.raiz | opcional | "Afinar a conta", no fim da aba Dinheiro (o "seu olho" da casa de farinha fica) | O padrão é a mediana da UF (MEDIDO) |
| bolso.custo | fundir | "Como prepara a terra? Enxada ou animal (só semente) / Trator alugado (máquina e insumos)", no Afinar | Dá efeito real ao equipamento (ponto 15) e tira uma pergunta abstrata |
| bolso.gs | cortar | sai o controle; um chip deduzido da área ("Garantia-Safra: você cabe, até 5 ha"); a agenda já diz "Adesão ao Garantia-Safra" | Não entra na conta (`dinheiro.js:129`) |

**Saldo:** de 15 itens perguntados antes ou no meio do resultado, ficam **3 antes do plano** (1 deles já marcado). Os outros 12 viram padrão, ficam no lugar onde o efeito aparece ou somem.

## 3. O fluxo proposto, tela a tela

```
Globo → município → painel Roça Certa → [Montar o meu plano]
   → "Seu roçado" (1 tela, 3 perguntas) → [Ver o meu plano]
   → abas: Plano · Dinheiro · Segurança · O lugar
   → "Leve para o técnico" (WhatsApp / Imprimir)
```

1. **Globo** (`index.html`): o globo gira, a pessoa busca ou toca no município e acontece o mergulho. Sem mudança.
2. **Mapa + painel Roça Certa:** o "Inverno 2027" é o único lugar do El Niño em destaque antes do plano. Um CTA só, grande: **"Montar o meu plano · 3 toques"** → `roca.html#/<cod>/2`.
3. **"Seu roçado"** (`#/<cod>/2`, uma tela de ~760 px, sem rolar):
   ```
   Quixadá, CE · Seu roçado
   3 toques e o plano é seu.
   1  O que vai no roçado hoje?   (marcamos o mais comum daqui)
      [✓ Milho] [✓ Feijão] [Mandioca] [Sorgo] [Palma] [Outra]
   2  Tem baixio? A parte baixa que fica úmida.
      [Tenho] [Não tenho] [Não sei]          (mini-desenho em cada um)
   3  Quando chove forte, a sua terra…
      [Seca rápido] [Segura] [Encharca] [Não sei]
      Na dúvida, aperte um torrão úmido: areia esfarela, barro gruda.
   Roçado: 1,03 ha, o típico daqui (Censo 2017) · mudar
   [ Ver o meu plano → ]
   + Afinar (opcional): quanto de cada · como fica · tamanho do baixio · maniva · 2025 ·
     preparo da terra · água · o que vale mais · preço da raiz
   ```
   Nesta tela não há barra de baixo nem contador; os botões são "Ver o meu plano" e, no topo, "Trocar o lugar".
4. **Aba Plano** (`#/<cod>/3`, meta ≤ 2.000 px):
   - uma linha de ação do El Niño ("2027: El Niño forte. Plante metade, guarde metade.");
   - o roçado visto de cima (2027, 2028, 2029) e a lista de 2027, com a maniva em linha na Parte A;
   - "Por onde começar o seu giro", com a pergunta de 2025 em 1 toque;
   - "O que fazer agora": os 3 próximos itens.
   - Num grupo "Por que este plano funciona", 4 "ver mais" com uma linha de chamada cada: água e erosão (ponto 12), faixas × praga (8), o que cada planta faz (10), 3 anos parte por parte (8).
5. **Aba Dinheiro** (`#/<cod>/4`, meta ≤ 2.000 px):
   - abre direto no Hoje → Melhor → Ideal (barras e 3 cartões; o Melhor com os ajustes é o "otimizar o que ele já faz");
   - "Outros jeitos de girar", com "O que vale mais pra você?" no cabeçalho (pontos 9 e 15);
   - "Ver ano a ano": El Niño nos 4 anos, quando o dinheiro entra, se a colheita paga o gasto;
   - "Afinar a conta": preço da raiz e preparo/custo.
6. **Aba Segurança** (`#/<cod>/5`, meta ≤ 2.000 px):
   - a manchete de 2027;
   - 2027 por cultura, em 3 linhas ("pelo menos X em 8 de 10; quebra em N de 10"), com 2028 e 2029 a um toque;
   - "Vamos olhar de novo em 19/mar e 30/abr";
   - **"Leve para o técnico"** (7 perguntas, WhatsApp, Imprimir);
   - "Lembra de um ano que quebrou?" em linha;
   - "E se chover…" (ponto 13) num "ver mais" com uma linha de chamada.
7. **Aba O lugar** (`#/<cod>/1`, meta ≤ 2.500 px): o passo 1 de hoje, mais curto (El Niño, 4 indicadores, régua, tendências, cardápio em uma fileira com "ver todas", confiança, fontes e glossário). O CTA passa a ser "Voltar ao meu plano".
8. **Fim:** "Leve para o técnico" → WhatsApp ou Imprimir; ou "Outro lugar".

Barra de baixo, nas abas: a faixa do ponto 16 ("Quem decide é você, com o técnico") + o botão **"Ajustar o roçado"**, que abre a tela 3 com o Afinar aberto. Saem o "← Voltar / Próximo →", porque as abas já navegam. As pílulas ficam sem número e sem ✓: são abas, não um passo a passo. Cada aba termina com o CTA da próxima ("Ver quanto rende →").

## 4. O que muda em cada passo

- **Globo/painel:** `js/globo/principal.js:94` e `js/globo/rocacerta.js:333` passam a apontar para `#/<cod>/2`, com o texto "Montar o meu plano · 3 toques". O painel continua o mesmo.
- **Passo 1 → aba "O lugar", a última** (`lugar.js`):
  - saem "Responder 5 perguntas" e "Pular…" (`:148-149`), e entra "Voltar ao meu plano" (`ctx.link(3)`);
  - o cardápio de 16 cartões vira uma fileira de ícones com "Ver todas" (`U.verMais`);
  - ficam a régua, as tendências (pontos 1 e 11) e a confiança (ponto 6).
- **Passo 3 → aba "Plano"** (`plantio.js:501-505`):
  - a ordem passa a ser: herói → cartão do giro (pergunta 2025 em linha) → "O que fazer agora" (3 itens);
  - a grade de 12 meses ("Ano todo") vai para dentro de "Ver o calendário completo";
  - `vulnerabilidade`, `blocoFaixas` e `saude_solo` vão para dentro de `U.verMais`, que já monta o extra só na abertura;
  - a maniva entra em linha na Parte A.
- **Passo 4 → aba "Dinheiro"** (`dinheiro.js:91`):
  - nova ordem: `abertura + hi-slot + jeitos + verMais(elnino, caixa, termo) + verMais(bolso, "Afinar a conta")`;
  - o `heroiHtml` sai da tela, porque repete o Hoje → Ideal; o "Ver os 28 anos" vai para "Ver ano a ano";
  - o seletor de Garantia-Safra é trocado por um chip.
- **Passo 5 → aba "Segurança"** (`seguranca.js:406-418`):
  - `blocoHoje` vai para o "ver mais" (repete o El Niño);
  - os cartões de cultura mostram só 2027, com 2028 e 2029 a um toque;
  - `blocoPortoes` e `leve_ao_tecnico` sobem;
  - a memória fica com a pergunta em linha (`historico.js:376-420`, que já tem os chips de ano);
  - `blocoCenario` e `blocoLimites` viram um "ver mais" cada.
- **"Seu olho":** um por aba, o que mais pesa na decisão (Plano: metade guardada; Dinheiro: preço na casa de farinha; Segurança: 19/mar e 30/abr; Lugar: os anos de El Niño discordam). Com a faixa fixa e o "Leve para o técnico", o ponto 16 fica mais forte do que com 12 avisos espalhados.

## 5. Toques até ver o plano

| | Hoje | Proposta |
|---|---|---|
| Depois de "Montar o plano", mínimo | 14 (12 só pulando tudo) + rolar ~4.000 px | **2** (Montar → Ver o meu plano) |
| Respondendo de verdade | 25–30 | **4** (Montar, baixio, terra, Ver) |
| Telas antes do plano | passo 1 + 12 | **1** |
| Altura das páginas de resultado | 23.181 px | meta ~8.500 px (−63%) |

## 6. Riscos

- O José pode achar que o jeito de hoje, o histórico e a área sumiram. Mitigação:
  - o jeito de hoje é a pergunta 1, já marcada;
  - a área fica à vista com "mudar";
  - o histórico aparece em linha e visível no Plano (2025) e na Segurança (ano que quebrou).
- O júri perde a "porta do espaço" se o passo 1 for para o fim. Mitigação: o globo e o painel já mostram satélite e El Niño; no vídeo, globo → camadas → 3 toques → plano; na banca, abrir a aba "O lugar".
- Pontos que vão para o "ver mais" (8, 10, 12, 13) podem ficar invisíveis para quem avalia. Mitigação:
  - cada "ver mais" tem uma linha de chamada com um número;
  - checklist dos 16 pontos ao refazer os prints (`testes/ferramentas/percorrer_fluxo.py`).
- Respostas padrão ("não sei") podem passar por respostas dadas. Mitigação: a ficha do topo marca "(típico daqui)" e "não sei" como hoje; o padrão da área continua com o selo MEDIDO.
- Links antigos e URLs com respostas: as chaves do `PADRAO` não mudam, e `#/<cod>/1` continua abrindo "O lugar". Verificar que o JSON é igual com as mesmas respostas nos 7 municípios de teste.
- Prazo de 4–6 h com vários agentes: há conflito se dois mexerem em `roca.js` ou `perguntas.js`. Cada arquivo precisa de um dono (abaixo).
- Abas sem número podem confundir quem espera um passo a passo. Mitigação: CTA para a próxima aba no fim de cada uma.

## 7. As 3 ideias mais importantes

1. **Uma tela só, com 3 perguntas, e só o que muda o plano ou a conta:** jeito de hoje (já marcado), baixio e terra, com o tamanho pré-preenchido pelo Censo. Tudo o mais vai para "Afinar (opcional)". De 12 telas e 14 toques para 1 tela e 2–4 toques.
2. **O globo leva direto às perguntas, e o resultado vira 4 abas (Plano · Dinheiro · Segurança · O lugar).** Cada aba responde na primeira tela, e o resto fica em "ver mais". O passo 1 de 4.550 px sai da frente, porque o globo já contou a história "do espaço".
3. **Perguntar onde o efeito aparece e cortar o que não é usado:**
   - maniva na linha da mandioca;
   - 2025 no cartão do giro;
   - "o que vale mais" nos "Outros jeitos";
   - equipamento fundido no custo;
   - Garantia-Safra deduzido da área;
   - o resumo "Pronto", o herói duplicado do passo 4 e 3 das 5 aparições do El Niño saem.

## Implementação (4–6 h, um dono por arquivo)

| Dono | Arquivos | O quê | Tempo |
|---|---|---|---|
| A | `roca.js`, `roca.html`, `css/quadra.css` (nav), `js/globo/principal.js:94`, `js/globo/rocacerta.js:333` | ordem das abas [3, 4, 5, 1] nas pílulas sem número; passo 2 sem barra de baixo; barra = faixa do ponto 16 + "Ajustar o roçado"; link do globo para `/2`; variável `abrirAfinar` (como `rolarTecnico`) para os "mudar" abrirem o Afinar | 1 h |
| B | `passos/perguntas.js`, `css/passos/perguntas.css` | tela única (reaproveita `PERG` e `opcao()`, `lerHoje/escreverHoje`, `AREA.render` dentro do "mudar"); Afinar com linhas segmentadas gravando as mesmas chaves (`hoje`, `baixio`, `agua`, `maniva`, `antes`, `custo`, `raiz`, `prioridade`); sai o modo pergunta de `hoje_ideal` e `historico` dentro do passo 2 | 2 h |
| C | `passos/plantio.js`, `passos/dinheiro.js`, `extras/historico.js` (cartão e memória em linha) | os cortes e "ver mais" das seções 4/Plano e 4/Dinheiro; pergunta de 2025 no cartão; maniva em linha; bolso para o fim; tirar o `heroiHtml` | 2 h |
| D | `passos/seguranca.js`, `passos/lugar.js` | os "ver mais" da Segurança e do Lugar; CTA "Voltar ao meu plano"; cardápio compacto | 1,5 h |
| todos | `testes/ferramentas/percorrer_fluxo.py` | prints a 390 px; alturas ≤ meta; checklist dos 16 pontos; JSON igual com as mesmas respostas | 0,5 h |
