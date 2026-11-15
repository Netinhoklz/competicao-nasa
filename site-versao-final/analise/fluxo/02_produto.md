# 02 · Produto: o fluxo profissional do QUADRA

Lente: designer de produto sênior (onboarding e recomendação: Aegro, FieldView, xarvio, Plantix, Plantio Certo; Duolingo,
Typeform, Nubank). Base: prints e textos de `E:/campeonato-nasa/tmp/fluxo_atual/` (Quixadá, 390 px), o código de `web/js/` e a API
medida com e sem cada resposta (`/api/local?cod=2311306`). Nada do site foi editado.

**Em uma frase:** hoje o QUADRA cobra 15 toques e 4.550 px de rolagem antes de mostrar o plano. O fluxo profissional mostra o
plano em 3 toques, com os padrões do Censo já marcados, e pergunta o resto só onde a resposta muda alguma coisa na tela.

---

## 1. Por que parece amador (com evidência)

| # | Problema | Evidência | Grav. |
|---|---|---|---|
| 1 | **Promessa quebrada no número de perguntas.** O botão diz 5 e entrega 11 telas mais o resumo. | `lugar.js:148` "Responder 5 perguntas"; `perguntas.js:84-89` fases hoje (3) + histórico (3) + `PERG` (5) + resumo; prints 02–13 | alta |
| 2 | **4 indicadores de progresso diferentes.** O contador recomeça 3 vezes: depois de 6 telas respondidas, a tela diz "pergunta 1 de 5". | pílulas do topo + "SEU JEITO DE HOJE · 1 DE 3" (02) + "O QUE VOCÊ JÁ FEZ · 1 DE 3" (05) + "PERGUNTA 1 DE 5" (08) | alta |
| 3 | **Esforço antes do valor.** O plano (passo 3) só aparece depois de ~15 toques. O "Hoje → Melhor → Ideal", que é o que o José pediu, fica no passo 4, depois de mais 5.625 px. | contagem na seção 5; alturas no BRIEFING | alta |
| 4 | **Perguntas que não mudam nenhum número.** A tela promete "muda o que dá para salvar", mas a água não entra no plano nem no dinheiro. "Deu bem", "como prepara a terra" e Garantia-Safra só aparecem no resumo. | `perguntas.js:30`; `ef.agua` só em `leve_ao_tecnico.js:67-68` e no próprio quiz; `historico.js:286,289` (bem, roca só no resumo); `dinheiro.js:128` "o valor do benefício não entra na conta" | alta |
| 5 | **Perguntas repetidas.** 2026 já vem do "jeito de hoje"; semente e fogo são perguntados de novo; o histórico é pedido de novo no passo 3 ("Contar") e no passo 5 ("Contar o meu ano ruim"). | print 05 "2026 · do seu jeito de hoje"; print 07 "Já anotado no seu jeito de hoje: Guarda semente"; 14_passo3 "Contar"; 16_passo5 "Contar o meu ano ruim" | média |
| 6 | **Dois botões verdes disputando e navegação sem padrão.** No passo 2, o "Próxima" fica ao lado do "Como plantar →" da barra, e o da barra pula o questionário inteiro. Os rótulos mudam a cada tela. | prints 02, 04, 13; `roca.js:225-226`; rótulos: "Não sei / pular + Próxima", "Anterior + Pular", "Anterior + Pronto", "← + Não sei + Pronto", "Terminar" | alta |
| 7 | **Páginas longas e densas.** Os passos 1, 3, 4 e 5 somam 23.181 px (~27 telas de celular), com 541–832 palavras, 9–15 selos e 4–11 links "Ver…" por passo. | alturas e contagem nos `.txt` 01, 14, 15, 16 | alta |
| 8 | **No passo 4, os controles vêm antes do resultado.** O "Seu bolso" (4 controles, Garantia-Safra e 2 chips) ocupa a 1ª tela; o gráfico Hoje/Melhor/Ideal só começa a ~1.250 px. | print 15 (topo); `dinheiro.js:84` (`abertura + bolso + hi-slot`) | média |
| 9 | **O passo 1 repete o painel do globo** (El Niño e chuva) logo depois de a pessoa ter visto o painel. | `rocacerta.js:3-5` (aba Inverno 2027); `lugar.js:50-74` | média |
| 10 | **"Não sei" no cabeçalho de todo passo.** A ficha do topo mostra "terra: não sei" e "baixio: não sei", e o produto parece incompleto. | `roca.js:111-113`; print 15 (topo) | baixa |
| 11 | **Jargão onde se responde.** "sem preço aqui" sob sorgo, palma e outra; "Só o que muda a conta". | prints 02 e 04 | baixa |
| 12 | **Dois nomes para o mesmo produto:** QUADRA na jornada e Roça Certa no painel. | `roca.html:24`; `painel.html:10,23` | baixa |

Medido na API (Quixadá, comparando o JSON com e sem a resposta):
- **terra:** muda 13 janelas de plantio (misturada ou barro); com areia, o feijão comum sai do zoneamento. O desenho do plano é o mesmo.
- **baixio = não:** o plano perde a faixa do baixio (5 → 4 faixas).
- **ad_baixio:** muda só `agenda.linhas`.
- **maniva = não:** troca a rotação das partes A, B e C (a mandioca sai).
- **maniva = plantada:** muda só a agenda.
- **água, deu bem, preparo, práticas e GS:** não chegam à API nem ao cálculo.

---

## 2. Decisão para cada pergunta

| Item | Decisão | Para onde | Motivo |
|---|---|---|---|
| hoje.culturas | **manter** | Tela única "Sua roça", ficha 1, já marcada com milho + feijão (padrão do Censo). A % sai da frente: divide igual | Faz a conta do "Hoje" (o pedido do José). O padrão serve à maioria: confirmar custa 0 toque |
| hoje.arranjo | **inferir** | Padrão "tudo junto" (o mais comum). Para mudar: a ficha 1 abre as 3 telas do jeito de hoje, que já existem | Só muda o R$ do Hoje quando o milho fica no baixio. Não deve estar no caminho principal |
| hoje.manejo | **mover** | Atrás da ficha 1 (tela 3 do jeito de hoje), opcional | 1ª chuva, fogo e semente só geram avisos de texto (`hoje_ideal.js:178-179, 291-298`) |
| hist.anos | **mover** | Cartão "Por onde começar o seu giro" no Plano (o botão "Contar" já existe) | Pergunta na hora em que a resposta aparece. 2026 já sai do jeito de hoje |
| hist.deu | **mover** | "Quebrou" vai para "Contar o meu ano ruim" no passo Seca (já existe). "Deu bem" sai | "Deu bem" não é lido por nada (`historico.js:286`). "Quebrou" alimenta a memória contra o IBGE |
| hist.faz | **fundir** | "Como prepara a terra" vira a escolha de custo: trator = máquina e insumos; animal ou enxada = só a semente. As práticas saem | `roca` e `faz` só aparecem no resumo. O equipamento (ponto 15) passa a mudar a conta |
| terra | **manter** | Tela única, ficha 3 (4 opções com ícone; padrão "não sei") | Muda 13 janelas de plantio: é a pergunta de maior efeito no calendário |
| ha | **manter** | Tela única, ficha 2, já preenchida com o típico daqui (1,03 ha, MEDIDO). Abre o `area.js` (ha, tarefas, medida) | Muda o desenho e todos os R$. Com o padrão, confirmar custa 0 toque |
| baixio | **manter** | Tela única, ficha 4, com 3 opções: Tenho / Não tenho / Não sei. O tamanho (pequeno, ⅓, ½) vai para o "Mudar" do desenho no Plano | "Não tenho" tira uma faixa do plano. O tamanho é detalhe e se acerta melhor olhando o desenho |
| agua | **opcional** | Fileira de chips dentro de "Leve ao técnico" (passo Seca) e no "Ajustar a conta" | Não muda plano nem R$. Fica pelo ponto 15 e pelas perguntas ao técnico, sem prometer "muda o que dá para salvar" |
| maniva | **inferir** | Se "Planta hoje" tem mandioca, vale "já plantada"; senão, "consigo". Quem não consegue maniva troca no cartão da Parte A do Plano | Afeta a rotação, mas é a minoria. O padrão cobre a maioria e a troca fica onde a mandioca aparece |
| bolso.prioridade | **mover** | Passo Rende, logo acima de "Outros jeitos de girar" (é o que ela acende). Padrão: "garantir" em ano de El Niño | Ponto 9: fica ao lado do efeito dela, não antes do resultado |
| bolso.raiz | **mover** | "Ajustar a conta" (fechado) no passo Rende | Muda o R$ da mandioca, mas é ajuste fino. O padrão MEDIDO serve |
| bolso.custo | **fundir** | Junta com "como prepara a terra" (hist.faz) em "Ajustar a conta": "Só a semente / Trator e insumos" | Uma pergunta só, com efeito real (`dinheiro.js:47`) |
| bolso.gs | **inferir** | Vira chip informativo: "Garantia-Safra: você cabe (até 5 ha)", calculado pelo tamanho. Sai o controle de 3 botões | O controle não muda nada na conta (`dinheiro.js:128`) |

Resultado: **15 respostas → 4 confirmações na frente** (todas pré-marcadas). O resto fica atrás de um toque, no lugar onde aparece o efeito.
Os três pedidos do José continuam: o jeito de hoje (ficha 1 e o Hoje → Melhor → Ideal), a área (ficha 2, com tarefas) e o histórico
(no giro e na memória).

---

## 3. O fluxo proposto, tela a tela

Ordem nova das pílulas (o único indicador de progresso): **1 Sua roça · 2 Plano · 3 Rende · 4 Se secar · 5 Os dados**.
Regra da casca: **um só botão verde por tela**, o da barra de baixo; os CTAs repetidos no fim dos passos saem.

| Tela | Objetivo | O que tem | Ação (botão verde) |
|---|---|---|---|
| **0 Globo + painel** (`index.html`, sem mudança) | Encantar e localizar com dados da NASA | Globo, mergulho, mapa com camadas no tempo; painel com chuva e El Niño | Toque no município → **"Montar o plano do meu roçado"** (vai para `#/cod/1`, que agora é "Sua roça") |
| **1 Sua roça** (o resumo "Pronto" de hoje, que passa a ser a 1ª tela) | Confirmar em 1 toque; mostrar que o plano é dele | Kicker "Quixadá · CE". Título: "É assim o seu roçado?", com o eco "Marcamos o mais comum daqui." Faixa âmbar de 1 linha: "2027: El Niño forte. Chuva fraca em 7 de 10 municípios do CE" (MEDIDO). 4 fichas 2×2, cada uma com "mudar": **Planta hoje** (milho + feijão) · **Tamanho** (1,03 ha, típico daqui) · **Terra** (não sei) · **Baixio** (não sei). Embaixo, uma linha pequena: "Dá para mudar depois." | **"Ver o meu plano →"**. Tocar numa ficha abre a pergunta grande que já existe e volta para esta tela |
| **2 Plano** (passo 3 enxuto) | Mostrar o que fazer | Manchete "Plante em 3 faixas. Cada ano, cada uma muda." Roçado visto de cima (2027/28/29). "Agora": os 3 próximos marcos (ex.: "14/11 junte semente e maniva"). Cartão "Por onde começar o seu giro", com o "Contar 2025 e 2026" opcional. Linha-ponte: "Rende +R$ 1.680 em 3 anos". Fechados: "Onde o roçado sofre mais", "Por que em faixas", "O que cada planta faz pelo solo", "Parte por parte em 3 anos", "O calendário completo" | **"Quanto rende →"** |
| **3 Rende** (passo 4 enxuto) | Provar o ganho: Hoje → Melhor → Ideal | O gráfico Hoje/Melhor/Ideal primeiro, com a linha "Hoje: milho + feijão, tudo junto · mudar". Os ajustes do "Melhor". "O que vale mais para você?" + "Outros jeitos de girar". Fechados: "Ajustar a conta" (raiz, "Só a semente / Trator e insumos", chip da Garantia-Safra), "Se 2027 for como…", "Quando o dinheiro entra", "A colheita paga o gasto?" | **"E se 2027 secar? →"** |
| **4 Se secar** (passo 5 enxuto) | Mostrar o risco e devolver a decisão (ponto 16) | Manchete "2027 tende a ser apertado." Uma linha por cultura só para 2027, com a grade de 10 roças (2028 e 2029 no "ver mais"). "E se chover…" (o controle, ponto 13). "Contar o meu ano ruim" (memória). "Vamos olhar de novo em 19/mar e 30/abr". **"Leve para o técnico"** por último, com os chips de água (opcional) | **"Mandar para o WhatsApp"** (Imprimir fica como botão secundário) |
| **5 Os dados** (o passo 1 de hoje, movido para o fim) | Explicar de onde vem cada número (pontos 1, 2, 3, 6, 7, 11) | Tudo o que o passo 1 tem hoje: El Niño, indicadores, régua da chuva, tendências, as 18 culturas, confiança, satélite × pluviômetro, glossário. O plano liga para cá ("Por que este plano? Ver os dados") | **"Outro lugar →"** |

Por que não abrir direto no plano, sem a tela 1: o plano sairia com "baixio?" tracejado e "terra: não sei" para todos, e quem lê
pouco não acha o "ajustar". A tela 1 custa 1 toque e é a prova visual do ponto 15 para o júri.

---

## 4. O que muda nos passos

| Onde | O que | Decisão |
|---|---|---|
| Casca (`roca.js`, `roca.html`) | Nova ordem `PASSOS = [perguntas, plantio, dinheiro, seguranca, lugar]`, com títulos curtos (Sua roça, Plano, Rende, Se secar, Os dados). Os links numéricos passam a usar o número novo (`ctx.link(2..4)` em `lugar.js:148-149`, `perguntas.js:69`, `plantio.js:71,502,505`, `dinheiro.js:55,88,128`, `seguranca.js:412`, `hoje_ideal.js:296` `passo: 3`, `roca.js:113,118,220-222`) | mudar ordem (~45 min) |
| Casca | Um só verde: a barra de baixo é o botão primário. Na tela 1, o rótulo é "Ver o meu plano →". Saem os `.cta` do fim de `lugar.js:148`, `perguntas.js:69` e `plantio.js:505`, e o "Pular e ver o plano" | cortar |
| Casca | A ficha do topo (`roca.js:111-113`) vira **um** chip: "1 ha · milho + feijão · Ajustar". Sem os "não sei" | juntar |
| Casca | Frase do ponto 16 em 1 linha: "Quem decide é você, com o técnico." (continua link para o técnico) | encurtar |
| Passo 1 → "Os dados" (`lugar.js`) | Vai para a posição 5. Saem o CTA "Responder 5 perguntas" e o "Pular". A manchete de El Niño vira uma faixa de 1 linha na tela 1 | mover |
| Passo 2 → "Sua roça" (`perguntas.js`) | Abre em `q = PERG.length` (o resumo). O resumo passa de 7 fichas para 4 (planta hoje, tamanho, terra, baixio), sem "datas de plantar". Responder uma ficha volta ao resumo (`q = PERG.length`, não `q + 1`). A ficha 1 abre o `hoje_ideal` (3 telas) e volta no fim. O baixio fica com 3 opções. A água e a maniva saem da fila. As fases hoje e histórico saem do caminho de chegada | juntar e cortar |
| Passo 3 → "Plano" (`plantio.js`) | À vista ficam abertura, roçado, "Agora" (3 marcos), cartão do giro e linha-ponte do R$. `vulnerabilidade`, `blocoTempo` (completo), `blocoFaixas` e `saude_solo` vão para 4 `U.verMais` com títulos curtos. "Contar" abre o histórico com `#/cod/1?abrir=hist`. O cartão da Parte A ganha "Sem maniva? trocar". **Alvo: ≤ 2.000 px** (hoje 5.625) | "ver mais" |
| Passo 4 → "Rende" (`dinheiro.js`) | Ordem nova: `abertura + hi-slot (herói) + ajustes + prioridade + cenarios + verMais("Ajustar a conta": raiz, custo, chip GS) + verMais(elnino, caixa, termo)`. Sai o controle de 3 botões da GS. **Alvo: ≤ 2.500 px** (hoje 6.629) | mover e "ver mais" |
| Passo 5 → "Se secar" (`seguranca.js`) | Cartões por cultura só com 2027 à vista. "E se chover…" à vista. A memória vira um botão. "Leve ao técnico" por último, com WhatsApp em verde e chips de água. Dos 11 "Ver…", ficam 3. **Alvo: ≤ 2.500 px** (hoje 6.377) | "ver mais" |
| Globo / painel | Sem mudança de tela. O botão continua para `#/cod/1`, que agora é "Sua roça". Sugestão de 5 min: o título do `painel.html` passar a "QUADRA" | manter |

**Plano de 4–6 h (3 agentes, um dono por arquivo):**
1. **A (casca + Sua roça):** `roca.js`, `roca.html`, `perguntas.js`, `quadra.css`. São 2 h. Teste: `testes/ferramentas/percorrer_fluxo.py` + print a 390 px.
2. **B (Plano + Os dados):** `plantio.js`, `lugar.js`, `historico.js` (parâmetro `abrir`). São 1,5 h. Teste: altura ≤ 2.000 px.
3. **C (Rende + Se secar):** `dinheiro.js`, `seguranca.js`, `leve_ao_tecnico.js`. São 2 h. Teste: alturas ≤ 2.500 px; os mesmos R$ de antes nos 7 municípios.
4. Juntos (30 min): percorrer o fluxo em Quixadá, Picos e Petrolina; checar os selos e os 16 pontos.

---

## 5. Toques até ver o plano

- **Hoje: 15 toques no mínimo**, aceitando todos os padrões, e 4.550 px de rolagem: município, "Montar o plano", rolar o passo 1 inteiro,
  "Responder 5 perguntas", 3 telas do jeito de hoje, 3 do histórico, 5 perguntas e "Ver como plantar". Até o Hoje/Melhor/Ideal são 16 toques e mais 5.625 px.
- **Proposta: 3 toques:** município → "Montar o plano do meu roçado" → "Ver o meu plano". Quem ajusta as 4 fichas chega com até 7 toques.
  O Hoje/Melhor/Ideal fica a 4 toques.

---

## 6. Riscos

- **A renumeração quebra links.** São ~15 chamadas `ctx.link(n)`/`data-ir`, mais o atalho do técnico que hoje aponta para o passo 5. Mitigação: um mapa
  `NUM = {roca: 1, plano: 2, rende: 3, seca: 4, dados: 5}`, grep por `link(` e `ir(`, e percorrer o fluxo inteiro antes de entregar.
- **O júri pode ver menos satélite**, porque o passo 1 deixa de abrir a jornada. Mitigação: a demo abre no globo e no painel (que já mostram a NASA), a faixa de El Niño
  fica na tela 1, a pílula "Os dados" fica sempre visível e o plano liga para ela.
- **Padrão errado para quem não ajusta** (área do Censo, milho + feijão). Mitigação: o chip "Ajustar" no topo de cada passo, o "típico daqui" escrito na ficha
  e o selo MEDIDO no tamanho.
- **O José pode sentir que o que ele pediu sumiu** (histórico, jeito de hoje). Mitigação: os três continuam, só que no lugar do efeito. Mostrar a ele a ficha 1, o
  "Contar" do giro e a memória do passo Seca.
- **Estado de `perguntas.js`** (`fase`, `q`, `telaForcada`): o novo caminho "abre a ficha → volta ao resumo" pode quebrar o "Anterior". Mitigação: na
  pergunta aberta por uma ficha, "Anterior" vira "Voltar" e leva ao resumo.
- **Celular pequeno (360×640):** a tela 1 pode rolar um pouco. Mitigação: fichas compactas (~120 px) e a barra de baixo fixa com o botão.
- **Prazo (15/11, 23:59):** nada no núcleo nem no servidor. Só ordem, `verMais` e cortes de tela. O que não couber fica como está.

---

## 7. As 3 ideias que mais importam

1. **Resultado primeiro, com padrões inteligentes.** O resumo "Pronto" vira a 1ª tela, já preenchido com o Censo e o IBGE: 4 fichas e 1 botão. São 15 toques → 3.
2. **Perguntar onde a resposta muda algo, e cortar o que não muda nada.** O histórico vai para o giro e para a memória; a % e o manejo ficam atrás da ficha "Planta hoje";
   preço e custo vão para "Ajustar a conta". Saem "deu bem", o preparo (vira custo), a água como pergunta e a Garantia-Safra como controle.
3. **Um fio só.** Um indicador de progresso (as pílulas Sua roça · Plano · Rende · Se secar · Os dados) e um botão verde por tela.
   Cada passo fica em ≤ 2–3 telas à vista, com o resto em "ver mais". O passo 1 vai para o fim como "Os dados", porque o painel do globo já faz a abertura.
