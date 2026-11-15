# 04 · Lente do júri do NASA Space Apps (Field Shift)

**Em uma frase:** o júri vai ver um globo lindo e, logo depois, um formulário de 11 telas. Numa demo de 2 minutos ele não chega ao plano, ao dinheiro nem ao risco, e não lê a palavra "NASA" em nenhuma tela da jornada. A proposta tem quatro mudanças: "Seu roçado" vira 1 tela, já preenchida com o típico do Censo; cada passo ganha 1 "momento de demo" no alto da tela; o selo passa a dizer de qual satélite veio o número; e uma página "Como o QUADRA sabe" junta a ciência num lugar só.

Material: prints e textos em `E:/campeonato-nasa/tmp/fluxo_atual/` (Quixadá, 390 px), API em `127.0.0.1:8090`, código em `web/js/`.

---

## 1. Diagnóstico: o que o júri vê hoje

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| 1 | O passo 2 tem **11 telas de pergunta + resumo**. O contador reinicia duas vezes ("1 de 3", "1 de 3", "1 de 5"), e o botão do passo 1 promete "5 perguntas". | prints 02–13. `lugar.js:148` ("Responder 5 perguntas"). `perguntas.js:103` e os topos de `hoje_ideal`/`historico` | alta |
| 2 | **Perguntas que não mudam nada** dão uma impressão de personalização falsa, e um jurado que testa percebe. | **Água:** `ef.agua` só é lido em `leve_ao_tecnico.js:67-68` e no resumo; o plano e os R$ ficam iguais. **Garantia-Safra:** troca só um chip, e o próprio código diz "o valor do benefício não entra na conta" (`dinheiro.js:116-118`). **"Deu bem"**, **preparo da terra** (trator/animal/enxada), **palhada** e **esterco** só aparecem no resumo (`historico.js:286-289`). **A tela "E na hora de plantar? Só o que muda a conta"** (`hoje_ideal.js:402`) não muda a conta: 1ª chuva, queima e semente só geram frases (`hoje_ideal.js:178-179, 291-298`). | alta |
| 3 | Perguntas **repetidas e fora de ordem**. | A tela 05 pergunta de novo 2026 ("do seu jeito de hoje"). "Não queimo" aparece em 04 e em 07. "Quanto de cada, no seu roçado de 1,0 ha" (02) e "Milho no baixio" (03) vêm **antes** de perguntar o tamanho (09) e o baixio (10). | média |
| 4 | **Dois botões verdes disputando** a mesma tela. | Tela 02: "Próxima" no quiz e "Como plantar →" na barra fixa (`roca.js:121`). Tocar na barra pula o resto das perguntas sem aviso. O passo 1 tem 3 saídas (CTA, "Pular…", barra "Sua roça →"). | alta |
| 5 | **A palavra NASA não aparece na jornada.** | `grep -i nasa` nos 16 textos dá **0**. A fonte fica no `title` do selo (`comum.js:26`), que não abre no toque, ou dentro dos "ver mais". | alta (júri) |
| 6 | **Páginas longas demais.** | 35.663 px somados a 390 px (≈ 45 telas de celular) e **3.318 palavras** visíveis. Passo 4 tem 6.629 px e passo 5 tem 6.377 px. Há 12 caixas "SEU OLHO" e 45 selos. | alta |
| 7 | **No passo 4 o resultado vem depois dos controles.** | As barras Hoje → Melhor → Ideal começam a y ≈ 1.300 px, depois de 4 controles (o que vale mais, preço da raiz, o que você paga, Garantia-Safra). Ordem em `dinheiro.js:84` (`bolso` antes do `hi-slot`). | alta |
| 8 | **Mesmos números 3 vezes** no passo 4. | R$ 2.480 / R$ 984 aparecem nas barras, no cartão "HOJE" e no bloco "No caso ruim… em 3 anos" (`dinheiro.js:171`). | média |
| 9 | **A ciência boa está enterrada.** | O controle "E se chover…" (ponto 13) é o penúltimo bloco do passo 5 (`seguranca.js:417`, y ≈ 5.000). "Testamos 7 jeitos" (ponto 4) e o acerto no teste com o passado (ponto 6) estão no **último** "ver mais" do passo 5 (`seguranca.js:361, 418`). A harmonização (ponto 7) é o último "ver mais" do passo 1. | alta (júri) |
| 10 | **Números vizinhos que não batem.** | Chuva "normal": 590 mm no painel do globo, 568 mm no passo 1 (jan–abr) e 567 mm em tendências. "11 culturas servem" com 16 cartões. Faixas de 0,11 ha no desenho e 0,23 ha na lista. Mar a +2,46 °C e a +2,5 °C. | média |
| 11 | **Parece um formulário incompleto.** | Nos passos 3–5, duas linhas de chips no topo com "terra: não sei" e "baixio: não sei" (`roca.js:111-113`). O desenho mostra "Baixio? · 0,34 ha · se você tiver baixio" mesmo sem resposta. | média |
| 12 | Rótulos técnicos à vista. | "sem preço aqui" embaixo de Sorgo, Palma e Outra (`hoje_ideal.js:373`). "sem piso" e "quebra em 6 em 10" (passo 5). | baixa |
| 13 | **O quiz não fica na URL.** | `fase`/`q` ficam em variáveis do módulo (`perguntas.js:11-14`). Voltar do navegador sai do passo, e recarregar recomeça do "Como você planta hoje?". Na demo ao vivo, um F5 custa 11 telas. | média |

### Os 16 pontos numa demo de 2 min

- **Hoje:** aparecem 1 (parcial), 5, 6, 11 (globo), 14 e 16. Ficam escondidos (abaixo de 3.000 px ou atrás de "ver mais") 2, 3, 4, 7, 8, 9, 10, 12 e 13. O 15 aparece, mas como um formulário longo.
- **Com a proposta:** aparecem na demo 1, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15 e 16. Os pontos 2, 3, 4 e 7 ficam na página "Como o QUADRA sabe", aberta com 1 toque.

---

## 2. Decisão por pergunta

Efeito medido pela API (`/api/local?cod=2311306`, com e sem o parâmetro) e pelo código:
- **terra:** muda as datas. Ex.: milho de 21/02–28/02 para 11/02–10/03 em terra misturada ou barro, e o feijão comum deixa de ser zoneado em areia. As partes A, B e C não mudam.
- **baixio:** "não" tira a parte Baixio do plano. O tamanho (`ad_baixio=15`) não muda o plano; só muda área e R$.
- **maniva:** "não" troca toda a mandioca por sorgo forrageiro. "Já plantada" não muda o plano.
- **Censo 2017 de Quixadá:** só 2,8% irrigam e 73,5% guardam semente de milho.

| Item | Decisão | Para onde | Motivo |
|---|---|---|---|
| hoje.culturas | **manter** | tela única "Seu roçado", 1ª linha (chips; milho e feijão já marcados). A divisão em % fica em "ajustar quanto de cada", fechado (padrão: igual) | alimenta Hoje → Melhor → Ideal, o melhor momento do passo 4; pedido do José; ponto 15 |
| hoje.arranjo | **mover** | passo 4, chip do cartão Hoje ("tudo junto · mudar", que já existe) | só mexe no milho fora do baixio e numa frase; depende do baixio, então precisa vir depois dele |
| hoje.manejo | **inferir** | padrão: 1ª chuva; semente pelo Censo (73,5%); queima "não sei". Os conselhos (espere a janela, sem fogo, garanta semente) vão para todos no calendário do passo 3 | a tela diz "Só o que muda a conta" e não muda nenhum R$ |
| hist.anos | **inferir** | 2026 = jeito de hoje e 2025 = igual. Fica no cartão "Por onde começar o seu giro" do passo 3: "Se em 2025 foi igual: comece com o caupi onde estava o milho. Foi diferente? Contar" | hoje repete a 1ª tela; o padrão "igual" já existe no código |
| hist.deu | **mover** | passo 5, "A sua memória e os dados" (o botão "Contar o meu ano ruim" já existe). Fica só "quebrou"; "deu bem" sai | "deu bem" não muda nada (`historico.js:286`); "quebrou" só aparece no confronto com o IBGE |
| hist.faz | **cortar** | não há | práticas e preparo só entram no resumo; o equipamento do ponto 15 já está em "o que você paga: máquina e insumos" |
| terra | **mover** | passo 3, ao lado de "Suas datas": [areia] [misturada] [barro] [não sei], e as datas mudam na hora; a dica do torrão vem junto | é a única resposta que mexe no zoneamento; no contexto das datas ela é entendida e rende uma boa demo |
| ha | **manter** | tela única, 2ª linha: ½ · 1 · 2 · 3 · 5 ha, com "típico daqui: 1,03 ha" marcado e o seletor de tarefas (`area.js`) | muda o desenho e o R$ de forma linear; pedido do José |
| baixio | **manter** | tela única, 3ª linha: Não tenho · Tenho · Não sei (com o mini-roçado). O tamanho fica em ⅓ e se ajusta no desenho do passo 3 | "não" tira o Baixio do plano; o tamanho não muda o plano |
| agua | **mover** | passo 5, "Leve para o técnico", como pergunta fixa: "Que água além da chuva posso usar no milho?" | o plano e os R$ são idênticos com qualquer resposta; 97% não irrigam (Censo) |
| maniva | **mover** | passo 3, na linha da mandioca: "Não consegue maniva? Trocar", e o plano se redesenha com sorgo | só "não consigo" muda o plano; é exceção, então vale 1 toque onde a mandioca aparece |
| bolso.prioridade | **mover** | passo 4, no topo de "Outros jeitos de girar" (logo abaixo das barras), com o sugerido pelo El Niño marcado | ela não muda o plano, só acende o jeito e reordena blocos; tem que ficar onde age (pontos 8 e 9) |
| bolso.raiz | **mover** | passo 4, "Ajustar a conta" (fechado) | muda o R$, mas é ajuste fino; o padrão já tem selo |
| bolso.custo | **opcional** | passo 4, "Ajustar a conta" (fechado) | "A colheita paga o gasto?" já mostra os dois níveis lado a lado |
| bolso.gs | **cortar** | vira um chip fixo no passo 5: "Garantia-Safra: com até 5 ha você cabe; paga se perder 40% ou mais" | a resposta não entra em nenhuma conta |

---

## 3. Fluxo proposto, tela a tela

| Tela | Objetivo | Conteúdo (acima da dobra a 390 px) | Ação |
|---|---|---|---|
| **0 · Globo** (`index.html`) | Impacto visual; "do espaço ao campo" | Globo com atalhos, mergulho, mapa e painel Roça Certa (El Niño 7 em 10, chuva IMERG ano a ano). Sem mudanças | "Montar o plano do meu roçado" (1 toque) |
| **1 · O seu lugar** | Mostrar por que 2027 importa, com dados da NASA à vista | El Niño em 1 linha com as 4 barras. 4 cartões com selo de fonte: mar `NOAA`, chuva chega `NASA GPM`, solo hoje `NASA SMAP`, calor `NASA POWER`. Tendências como estão (carrossel). Embaixo, chip "Confiança dos dados: alta · por quê". Régua, cardápio de 16 culturas e "SEU OLHO" extra vão para 1 "ver mais". **≤ 1.800 px** | barra fixa: "Montar o meu roçado →" |
| **2 · Seu roçado** (1 tela) | Pegar o jeito de hoje sem formulário | "O típico daqui já vem marcado. Mude o que for diferente." 3 linhas: **O que vai no roçado hoje?** (chips), **Tamanho** (chips + tarefas), **Tem baixio?** (3 opções). Sem barra fixa concorrente | "Ver o meu plano →" (1 toque) |
| **3 · O plano** | O momento visual: o roçado girando | Roçado visto de cima, tocando 2027 → 2029 sozinho uma vez, e 1 linha "Comece agora: junte semente e maniva; nada de fogo". Depois: "Por onde começar o giro" (com o histórico inferido), "Suas datas" com a escolha da terra, "Onde o seu roçado sofre mais" (ponto 12) e os 4 cartões "O que cada planta faz pelo solo" (ponto 10). Praga e "parte por parte" vão para "ver mais" | "Quanto rende →" |
| **4 · Quanto rende** | O dinheiro em 3 barras | Manchete + **barras Hoje → Melhor → Ideal no alto**, com o chip "milho + feijão · tudo junto · mudar" e o cartão Melhor (3 ajustes com +R$). Depois "O que vale mais para você?" + Outros jeitos de girar (pontos 8 e 9). Caixa e "paga o gasto?" ficam em "ver mais"; "Ajustar a conta" (raiz e custo) fica fechado | "E se a chuva falhar? →" |
| **5 · E se a chuva falhar?** | O risco, com algo para mexer | Manchete "2027 tende a ser apertado" + **controle "E se chover…" no alto** (ponto 13). Cada cultura em 1 linha com a grade de 10 roças (os 3 anos em "ver mais"). "Vamos olhar de novo em 19/mar e 30/abr". **Leve para o técnico** (Imprimir / WhatsApp). Memória (opcional). Chip da Garantia-Safra | "Levar ao técnico" (compartilhar) |
| **6 · Como o QUADRA sabe** (fora da numeração; botão fixo no topo e link no fim do passo 5) | Os pontos 2, 3, 4, 6 e 7 para o júri num lugar só | Grade comum dos satélites (harmonização), satélite × pluviômetro, **7 métodos testados e o acerto em 100**, confiança, glossário e "o que não dá para projetar". Tudo já existe nos extras | voltar |

**Nomes dos passos na barra:** O lugar · Seu roçado · O plano · Quanto rende · Se faltar chuva. "Segurança" é vago, e "Como plantar" e "O plano" são a mesma coisa.

---

## 4. O que muda em cada passo

- **Barra fixa e casca (`roca.js`, `roca.html`)**
  - A barra fixa vira **o único botão principal**, com o rótulo do passo seguinte. Saem os CTAs repetidos dentro dos passos ("Responder 5 perguntas", "Pular…", "Ver como plantar", "Ver quanto rende").
  - As fichas do topo (2 linhas de chips, `roca.js:111-113`) viram 1 linha: "1 ha · baixio ⅓? · milho + feijão · mudar".
  - Entra o botão "Como sabemos" no topo e a rota 6 (`ciencia`).
- **Passo 1 (`lugar.js:141-150`)**
  - **Ficam:** El Niño, os 4 indicadores e tendências.
  - **Vão para 1 "ver mais":** régua, cardápio e confiança (esta deixa só o chip).
  - **Saem:** o CTA e o "Pular" (linhas 148-149).
- **Selo com a fonte (`comum.js:24-27`)**
  - Tira a missão do texto de `fonte` (SMAP, GPM/IMERG, POWER, GRACE, MODIS, ECOSTRESS, NOAA, IBGE, ZARC) e escreve "MEDIDO · NASA SMAP", com no máximo 10 caracteres depois do ponto.
  - Muda todas as telas de uma vez, sem mexer nos passos.
- **Passo 2 (`perguntas.js`)**
  - A máquina `hoje → historico → perguntas` dá lugar a **1 tela**. Ela reusa os chips de culturas de `hoje_ideal`, `AREA.render` e o mini-roçado do baixio.
  - Grava `hoje`, `ha` e `baixio` com `ctx.set`. As chaves de `PADRAO` ficam como estão, então links antigos continuam valendo.
  - Os modos "pergunta" de `historico.js` e as telas 2 e 3 de `hoje_ideal` param de ser chamados, mas o código não é apagado.
- **Passo 3 (`plantio.js:500-504`)**
  - Ordem nova: herói → cartão do giro → vulnerabilidade → calendário (com a terra) → saúde do solo. `blocoFaixas` (praga) e "parte por parte" vão para "ver mais".
  - A linha da mandioca ganha "sem maniva? trocar" (`ctx.set({maniva:"nao"})`).
  - Fica no máximo 1 "SEU OLHO".
- **Passo 4 (`dinheiro.js:84`)**
  - Ordem nova: abertura → `hi-slot` (barras) → `jeitos`, com a prioridade dentro → `verMais("Ajustar a conta", bolso sem GS)` → `verMais(caixa + termo)`.
  - Saem o bloco "No caso ruim… em 3 anos" (`heroiHtml`, repete as barras) e o `elNinoHtml`, que vai para o passo 5.
- **Passo 5 (`seguranca.js:405-418`)**
  - Ordem nova: abertura → `blocoCenario` → cartões em 1 linha → portões → `leve_ao_tecnico` → memória → chip GS.
  - `blocoLimites` e `metodos` vão para a página 6.
- **Globo e painel:** sem mudanças. Ficam só como pendência os textos dos 590/568/567 mm: usar a mesma definição de "chuva normal" nas duas telas, ou rotular com o período ("jan–abr").

---

## 5. Toques até ver o plano

- **Hoje:** 15 toques do globo até o plano (atalho, "Montar o plano", CTA do passo 1, 11 telas e o resumo), ou 1 toque escondido em "Pular…" a y ≈ 4.300 px.
- **Proposta:** **4 toques** do globo (atalho → "Montar o plano do meu roçado" → "Montar o meu roçado" → "Ver o meu plano"). Dentro do `roca.html` são 2 toques. Responder de verdade as 3 linhas acrescenta de 2 a 4 toques.

---

## 6. Roteiro de demo (2 min) e vídeo (30 s)

**Demo**
1. Globo → atalho Quixadá → mergulho → painel "7 em 10 municípios secam no El Niño" (20 s).
2. Passo 1: "estes 4 números vêm de satélites da NASA" (SMAP, GPM, POWER) e tendências (15 s).
3. Seu roçado: 1 toque, "o típico do Censo já vem marcado" (10 s).
4. O plano: o roçado gira 2027 → 2029; toco em "barro" e as datas mudam (20 s).
5. Quanto rende: Hoje R$ 2,5 mil → Ideal R$ 4,4 mil em 3 anos; toco em "Guardar água" e o jeito muda (20 s).
6. E se chover pouco: arrasto para 60% e "5 em 10 roças de milho quebram"; "Leve para o técnico" (20 s).
7. "Como o QUADRA sabe": 7 métodos testados e grade comum dos satélites (15 s).

**Vídeo (30 s):** globo (0–6 s) → Quixadá (6–10) → "2027: El Niño" (10–14) → 1 toque (14–17) → roçado girando (17–22) → barras de R$ (22–26) → controle da chuva (26–30).

---

## 7. Quem faz o quê em 4–6 h (1 dono por arquivo)

1. **Agente A, `perguntas.js` + css (≈ 1,5 h).** Tela única "Seu roçado".
2. **Agente B, `roca.js` + `roca.html` + `comum.js` (≈ 1,5 h).** Barra como único CTA, ficha em 1 linha, selo com a missão e rota `ciencia` + `passos/ciencia.js` (só monta extras que já existem; `metodos` passa a ser exportado de `seguranca.js`).
3. **Agente C, `lugar.js` + `plantio.js` (≈ 1,5 h).** Cortes, ordem nova, terra junto das datas e maniva na mandioca.
4. **Agente D, `dinheiro.js` + `seguranca.js` (≈ 1,5 h).** Ordem nova, sai a repetição, GS vira chip e o El Niño vai para o passo 5.
5. **Conferência (≈ 0,5 h).**
   - Rodar `testes/ferramentas/percorrer_fluxo.py` nos 7 municípios de teste.
   - A 390 px, nenhuma rolagem lateral.
   - Os passos 1, 3, 4 e 5 com no máximo ~2.500 px cada.
   - Os R$ das barras iguais aos de hoje com as mesmas respostas na URL.

---

## 8. Riscos

- **Personalização menos visível (ponto 15).** Cortar perguntas pode dar essa impressão. A compensação são os ajustes no lugar onde fazem efeito (terra nas datas, maniva na mandioca, arranjo no cartão Hoje, prioridade nos jeitos, raiz e custo em "Ajustar a conta") mais a frase "o típico daqui já vem marcado".
- **Inferir 2025 = 2026 pode errar** o "a terra repetiu milho". A frase precisa ser condicional ("se em 2025 foi igual") e manter o botão "Contar".
- **O José pode sentir o histórico rebaixado.** O histórico continua no produto, nos passos 3 e 5, onde ele muda algo; explicar isso na entrega.
- **Mexer em 6 arquivos na véspera** (entrega em 15/11, 23:59) pode quebrar algo. Mitigação: as chaves de `PADRAO` e da URL ficam iguais, cada arquivo tem 1 dono e a conferência fica pronta antes do vídeo.
- **Selo com nome da missão** pode quebrar linha a 390 px. Limitar a 10 caracteres e testar em todos os passos.
- **Controle da chuva no alto do passo 5** pode confundir o agricultor antes de ele ver as culturas. Por isso a manchete do controle diz o que fazer: "Arraste: e se chover menos?".
- **A demo depende do servidor local e do WebGL do globo.** Gravar o vídeo no desktop e ter um link direto `roca.html#/2311306/1` de reserva.

---

## 9. As 3 ideias mais importantes

1. **"Seu roçado" em 1 tela, já marcada com o típico do Censo** (o que planta, tamanho, baixio), com o botão "Ver o meu plano". São 15 toques a menos até o plano. As outras perguntas viram ajustes no lugar onde mudam algo. Água, Garantia-Safra, "deu bem", práticas e preparo saem, porque não mudam nada.
2. **1 momento de demo no alto de cada passo:**
   - passo 1: El Niño + 4 cartões "NASA";
   - passo 3: o roçado girando;
   - passo 4: as barras Hoje → Melhor → Ideal;
   - passo 5: o controle "E se chover…".

   O resto vai para 1 "ver mais" por passo e uma barra fixa só. A altura cai pela metade ou mais.
3. **NASA e ciência visíveis sem jargão.** O selo diz de qual satélite veio o número ("MEDIDO · NASA SMAP"). A página "Como o QUADRA sabe" junta harmonização, satélite × pluviômetro, 7 métodos testados com o acerto, confiança e glossário. O júri vê os pontos 2–7 em 15 s, e o agricultor não precisa abrir.
