# 01 · Lente do agricultor do sertão

Quem lê: Seu Antônio, 47 anos, Quixadá-CE, estudou até o 5º ano. Tem um Android simples e 3 ha de milho, feijão e um pouco de mandioca, cisterna de beber e umas cabras.
Material: `E:/campeonato-nasa/tmp/fluxo_atual/` (TXT e PNG a 390 px). A API `/api/local?cod=2311306` foi chamada com e sem cada resposta para medir o efeito dela.

> "Eu queria saber o que planto, quando planto e se vai chover. Me perguntaram onze coisas, e três delas eu já tinha respondido."

---

## 1. Onde ele trava (diagnóstico)

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| 1 | **A tela promete 5 perguntas, mas são 11 telas e um resumo.** Há 3 contadores diferentes ("1 de 3", "1 de 3", "1 de 5"). Ele se sente enganado e desiste por volta da 6ª tela. | `01_passo1_lugar.txt:168` "Responder 5 perguntas"; `02…txt:4` "1 DE 3"; `05…txt:4` "1 DE 3"; `08…txt:4` "PERGUNTA 1 DE 5" | alta |
| 2 | **Cada pergunta tem dois botões de seguir.** "Próxima" fica no meio da tela, e o botão do rodapé, "Como plantar →", é maior e pula todo o resto. Ele aperta o maior. | PNG `02…png` (os dois botões verdes); `roca.js:121,225-228` | alta |
| 3 | **Ele precisa rolar 4.550 px antes de poder dizer qualquer coisa.** O botão de começar fica a cerca de 4.000 px, depois de El Niño, tendências e 18 culturas. "Pular" é um link pequeno sublinhado. | `01_passo1_lugar.txt:2` (altura 4550); recorte de 3.600–4.550 px | alta |
| 4 | **Metade das perguntas não muda o plano nem a conta.** Água: não vai para a API, e "cisterna de beber" não muda nada. Manejo (1ª chuva, fogo, semente) só gera frases, embora a tela diga "Só o que muda a conta". "Deu bem", "o que já faz" e o preparo da terra só viram rótulo. O valor do Garantia-Safra não entra na conta. | `roca.js:44-51`; `hoje_ideal.js:402` contra `:178-179,291-298`; `historico.js:288-289`; `dinheiro.js:129` | alta |
| 5 | **O passo 4 pede mais 4 escolhas antes de mostrar o dinheiro:** o que vale mais, o preço da raiz em R$/kg, o custo e o Garantia-Safra. O gráfico Hoje → Melhor → Ideal só aparece a cerca de 1.250 px. Ele vende a raiz por carga na casa de farinha e não sabe o preço por quilo. | `15_passo4_dinheiro.txt:11-36`; recorte de 1.250 px | alta |
| 6 | **O resultado é comprido demais.** Os passos 3, 4 e 5 somam 18.631 px, com 29 "Ver…" e 36 selos. "O que fazer e quando", o que ele mais quer, só aparece a cerca de 3.100 px do passo 3. | alturas 5.625 + 6.629 + 6.377; contagem nos TXT; `14…txt:103` | alta |
| 7 | **"Pronto" aparece no meio do caminho.** As telas 3 e 6 fecham com "Pronto ✓", e depois vêm mais 8 e 5 telas. O botão muda de nome a cada tela: Próxima, Pular, Pronto, Terminar. | `04…txt:24`, `07…txt:22`, `03…txt:18`, `12…txt:16` | média |
| 8 | **As perguntas vêm fora de ordem.** O "quanto de cada no seu roçado de 1,0 ha" vem antes de perguntar o tamanho. "Milho no baixio" vem antes de perguntar se ele tem baixio. | `02…txt:18` contra `09` (pergunta 2 de 5); `03…txt:12` contra `10` | média |
| 9 | **Repete o que ele já disse.** O 2026 é o jeito de hoje. Semente e fogo aparecem nas telas 3 e 6 ("Já anotado"). O baixio volta nos passos 3 e 4 com "?". | `05…txt:11-12`; `07…txt:13-14`; `14…txt:9`; `15…txt:30` | média |
| 10 | **Os números se contradizem para ele.** Sobre El Niño o site diz, em lugares diferentes: "chuva fraca em 7 de 10", "os anos de El Niño discordam", "aqui houve seca e ano bom" e "2 de 3 trouxeram seca". No passo 4, o número grande do cartão é o do caso ruim (R$ 984) e o da barra é o típico (R$ 2.480). | `01…txt:9,14,165`; `16…txt:13`; `15…txt:39-58` | média |
| 11 | **Fala de estatística e de técnico:** "pelo acaso seriam 3 em 10", "à frente de hoje em 98 de 100", "caso ruim (1 em 10)", "portões", "evidência B", "tampão", "leguminosa", "insumos". | `01…txt:11`; `15…txt:100`; `16…txt:183`; `14…txt:162` | média |
| 12 | **Diz que o plano rende menos em 2027 porque o sorgo "não vende".** Para quem cria cabra, sorgo e palma são comida da criação. A resposta `criacao` existe em `PADRAO`, mas nunca é perguntada nem usada. | `15…txt:136`; `roca.js:17,87` (sem uso fora daí) | média |
| 13 | **O plano tem "?" no desenho** ("Baixio? · milho + caupi · 0,34 ha, se você tiver baixio"), e a área vem em ha com decimais (0,11 ha), que ele não entende. | `14…txt:15-22,40-41` | baixa |
| 14 | **O tamanho padrão leva o selo MEDIDO** ("Usando o típico daqui: 1,03 ha MEDIDO"). Parece que o satélite mediu o roçado dele. | `09…txt:24-25` | baixa |
| 15 | **"Por onde começar o seu giro" manda ele voltar às perguntas** ("Conte o que você plantou… Contar"). | `14…txt:73-77` | baixa |

**Contagem de hoje:** são cerca de **30 toques** até o plano. Três no globo, cerca de 4.000 px de rolagem e 1 toque no passo 1, 25 nas 11 telas e 1 em "Ver como plantar".

---

## 2. Decisão por pergunta

Para medir, chamei a API com e sem cada parâmetro (Quixadá, 2311306).

| Item | Decisão | Para onde | Por quê (medido) |
|---|---|---|---|
| hoje.culturas | **manter** | Tela "Sua roça", linha 1: Milho e Feijão já marcados; barra colorida com a divisão; "ajustar quanto de cada" fechado | É o que faz o "Hoje" ser dele, e ele responde sem pensar. Os botões de − e + em % cansam: a divisão igual fica como padrão. |
| hoje.arranjo | **inferir** | "Tudo junto" como padrão (já é o de `lerHoje`); "mudar" no cartão Hoje do passo 4 e em "Afinar" | Só muda onde fica o milho e um alerta. Hoje pergunta "milho no baixio" antes de saber se há baixio. |
| hoje.manejo | **opcional** | "Afinar o plano" | Não muda R$, só frases (`hoje_ideal.js:178-179,291-298`), e a tela promete "Só o que muda a conta". |
| hist.anos | **fundir** | "Afinar": um botão "Em 2025 plantou igual? Sim/Não" (2026 = hoje) | Só aciona "a terra repetiu milho". Sem resposta, a frase fica condicional: "Se o milho repete no mesmo lugar, comece ali pelo feijão-caupi". |
| hist.deu | **mover** | Passo 5, "A sua memória": "O IBGE anotou 2012, 1998 e 2016 como os piores aqui. Bate com a sua roça? [Sim] [Foi outro ano]" | "Deu bem" não muda nada. "Quebrou" só serve para comparar com o IBGE, e isso já mora no passo 5 ("Contar o meu ano ruim"). |
| hist.faz | **cortar** | Nenhum lugar. O fogo e a semente ficam no manejo (opcional). | Palhada, esterco, faixas e preparo só viram rótulo (`historico.js:288-289`). |
| terra | **manter** | "Sua roça", linha 3: Areia (seca rápido) · Misturada · Barro (gruda no pé) · Não sei | É a única resposta que mexe nas datas: caupi 11/03–20/03 → 11/03–20/04 no barro; milho 21/02–28/02 → 11/02–10/03 na misturada. |
| ha | **manter** | "Sua roça", linha 2: chips ½ · 1 · 2 · 3 · 5 ha, "≈ N tarefas", "outra medida" abre `extras/area.js` | Muda o desenho e a conta. Com um plano "de 1 ha" e 3 ha na roça, ele desconfia. Tirar o selo MEDIDO do padrão e escrever "típico daqui (Censo)". |
| baixio | **manter** | "Sua roça", linha 4: Não tenho · Pequeno · Grande · Não sei (com os mini-desenhos atuais) | Sem baixio, o plano muda (o milho sai e entram as bordas: 23 valores no plano). O ad do baixio muda as datas do milho. As frações ⅓ e ½ viram "pequeno" e "grande". |
| agua | **opcional** | "Afinar" e a lista "Leve ao técnico" | Não vai para a API (`roca.js:44-51`). "Cisterna de beber" não muda nada; barreiro (volume) e poço só mudam texto. |
| maniva | **inferir** | Mandioca marcada → "tem". Na linha da mandioca do plano: "Já está plantada?" e "Não consigo maniva" | Muda o plano (sem maniva, a mandioca vira sorgo ou caupi: 22 valores), mas quem planta mandioca tem maniva. |
| bolso.prioridade | **fundir** | É a mesma coisa que as abas de "Outros jeitos" (Água/Renda/Solo/Plano); fica um seletor só, depois do número | `cenarios.js:18` liga uma à outra; o passo 4 mostra dois seletores da mesma coisa (`15…txt:11-15` e `192-196`). No El Niño, o padrão segue "garantir". |
| bolso.raiz | **mover** | "Mudar a conta", fechado, no passo 4 | Ele não sabe R$/kg (vende por carga). O padrão continua a mediana do CE. |
| bolso.custo | **mover** | "Mudar a conta", com as palavras dele: "Paga trator ou adubo? Não / Sim" | Cobre o "equipamentos" do ponto 15 sem tela nova. |
| bolso.gs | **cortar** | Uma linha informativa: "Até 5 ha, você pode entrar no Garantia-Safra" (passo 5, técnico) | O valor não entra na conta (`dinheiro.js:129`). |

Ficam 4 perguntas obrigatórias, todas já marcadas com o típico daqui. Com um toque ele já vê o plano.

---

## 3. O fluxo proposto, tela a tela

1. **Globo** (`index.html`, sem mudança visual): ele busca "Quixadá", acompanha o mergulho e vê o painel Roça Certa com o inverno de 2027. O botão vira **"Montar o meu plano (1 minuto)"** e leva a `#/<cod>/2`.
2. **Sua roça** (passo 2, uma tela só, cerca de 750 px, sem contador):
   - Título: "O seu roçado". Linha de apoio: "Já marcamos o comum de Quixadá. Mude o que for diferente."
   - Linha 1: O que vai no roçado? Chips com ícone (Milho ✓, Feijão ✓, Mandioca, Sorgo, Palma, Outra) e a barra colorida da divisão.
   - Linha 2: Tamanho (½ · **1 típico** · 2 · 3 · 5 ha), com "≈ 10 tarefas".
   - Linha 3: Terra (Areia · Misturada · Barro · **Não sei**).
   - Linha 4: Baixio (Não tenho · Pequeno · Grande · **Não sei**).
   - Botão fixo embaixo: **"Ver o meu plano →"**. O botão do rodapé some neste passo.
3. **Seu plano** (passo 3, "Como plantar" → **"Seu plano"**):
   - Manchete: "2027: chuva fraca (El Niño). Plante metade e guarde metade."
   - Fichas para mudar: 3 ha · terra misturada · baixio pequeno.
   - **O que fazer e quando** (AGORA → MAI), que sobe para o topo.
   - O roçado visto de cima, com as abas 2027/28/29. As áreas vêm como "⅓ do roçado ≈ 3 tarefas", sem "0,11 ha".
   - Uma frase de "por onde começar" e um "Seu olho".
   - "Ver mais": por que em faixas, onde sofre mais, o que cada planta faz pelo solo, parte a parte.
   - Botão: "Quanto rende →".
4. **Quanto rende** (passo 4):
   - Manchete: "Com 3 ajustes, o seu jeito rende R$ X a mais em 3 anos."
   - **Barras Hoje → Melhor → Ideal** no topo.
   - Cartão **Melhor** aberto, com os 3 ajustes e o R$ de cada.
   - Hoje e Ideal em uma linha cada. Um número grande por cartão (o típico), com "ano ruim: R$ 984" pequeno.
   - "Mudar a conta" fechado (raiz e custo).
   - "Outros jeitos", com as abas Comida/Renda/Solo/Plano: é ali que ele escolhe a prioridade.
   - "Ver mais": se 2027 for como 1998…, o caixa mês a mês, se a colheita paga o gasto.
   - Botão: "Se secar →".
5. **Se secar** (passo 5, "Segurança" → **"Se secar"**):
   - Manchete: "2027 tende a ser apertado. 2028 e 2029, normais."
   - O controle "E se chover…" aparece aberto.
   - "A sua memória", com os anos ruins do IBGE e a pergunta "Bate com a sua roça?".
   - "Vamos olhar de novo em 19/mar e 30/abr."
   - **Leve para o técnico**, com WhatsApp e Imprimir, fecha o passo.
   - As 3 culturas ficam em uma linha cada; o resto vai para "Ver os cálculos".
6. **Afinar o plano** (opcional; vem do link "Contar mais do seu jeito (30 s)" no fim dos passos 4 e 5 e dos "mudar"):
   - Versão mínima: as telas de arranjo e manejo de `hoje_ideal.js` e a de anos de `historico.js`, como já existem.
   - Se sobrar tempo: uma tela só de chips, com arranjo, 1ª chuva, fogo, semente, 2025 igual, mandioca plantada e água.
   - Botão: "Refazer o plano".
7. **Do espaço** (passo 1, "O lugar" → **"Do espaço"**, opcional): todo o `lugar.js` (tendências, cardápio, confiança, de onde vêm os dados, glossário), com o botão "Voltar ao meu plano". O júri chega por aqui, ou pelo globo.

---

## 4. O que muda em cada passo

| Onde | O quê | Decisão |
|---|---|---|
| Globo e painel | O link do plano passa a `#/<cod>/2` (`principal.js:94`, `rocacerta.js:333`, `roca.js:194,209`) | mover a entrada |
| Passo 1 | Passa a se chamar "Do espaço". Sai "Responder 5 perguntas" e "Pular" (`lugar.js:148-149`), e entra "Voltar ao meu plano". O El Niño vira uma linha no topo do passo 3. | opcional |
| Passo 2 | As 11 telas e o resumo viram 1 tela com 4 linhas. Os módulos HI e HIST, em modo pergunta, só abrem por "Afinar". O `#avancar` some neste passo. | juntar |
| Passo 3 | Fica na ordem manchete → agenda → desenho → 1 olho → "Ver mais" (faixas e praga, vulnerabilidade, saúde do solo, parte a parte). "Por onde começar" vira uma frase condicional, sem o botão "Contar". | cortar a ordem atual e mover para "Ver mais" |
| Passo 4 | As barras e o cartão Melhor sobem para o topo. Os controles de raiz e custo vão para "Mudar a conta". O Garantia-Safra vira texto. A prioridade fica nas abas de "Outros jeitos". Os blocos El Niño, caixa e "paga o gasto" vão para "Ver mais". | mover e juntar |
| Passo 5 | Ficam visíveis a manchete, a chuva, a memória, os portões e o técnico. Os leques das 3 culturas ficam com uma linha cada e "Ver mais". Os 4 "Ver…" finais viram um só. | mover para "Ver mais" |
| Texto | Uma frase de El Niño igual em todos os passos. "Não vende" vira "vira comida da criação (fora do R$)". "MEDIDO" sai da área padrão. Na manchete, R$ por ano ao lado dos 3 anos. | cortar a contradição |

**Estimativa (4–6 h):**

| Tarefa | Tempo |
|---|---|
| Tela "Sua roça", reaproveitando `opcao()`, os ícones de CULT e `AREA` em modo chips | 1,5–2 h |
| Entrada, nomes dos passos e rodapé | 0,3 h |
| Ordem do passo 3 | 0,7 h |
| Ordem do passo 4 | 1 h |
| Ordem do passo 5 | 0,5 h |
| Textos | 0,5 h |
| "Afinar" (link para as telas existentes) | 0,3 h |
| Prints a 390 px nos 7 municípios e `percorrer_fluxo.py` | 0,7 h |

---

## 5. Toques até ver o plano

- **Hoje:** cerca de 30 toques e cerca de 4.000 px de rolagem.
- **Proposta: 8 toques.** São 3 no globo, 4 respostas (Mandioca, 3 ha, Misturada, Pequeno) e "Ver o meu plano".
- Quem aceita o típico daqui chega com 4 toques.

---

## 6. Riscos

- **O júri pode sentir falta da NASA no começo.** O globo e o painel já são "do espaço". O passo 1 continua na barra como "Do espaço" e entra na demo.
- **Os pedidos do José podem parecer rebaixados.** O jeito de hoje e a área ficam na 1ª tela; o histórico vira a memória do passo 5 e o "Afinar". É preciso dizer isso na entrega.
- **Os padrões inferidos erram para quem não é típico** (tudo junto, 2025 igual, maniva). Todo padrão aparece na ficha com "mudar", e as frases que dependem de padrão ficam condicionais.
- **A divisão igual exagera a parte de quem tem "um pouco de mandioca".** A barra colorida fica visível e "ajustar" fica a um toque.
- **Esconder em "Ver mais" pode tirar da vista os pontos 8, 10, 12 e 13.** Cada bloco escondido deixa uma frase-resumo visível, e o controle de chuva fica aberto no passo 5.
- **Entrar pelo passo 2 muda o "Voltar" e o roteiro de `percorrer_fluxo.py`.** A numeração dos passos fica igual, só muda a entrada. Depois, refazer os prints.
- **Prazo de amanhã.** Plano B: deixar as telas de hoje, mas com a entrada direta, as 4 perguntas obrigatórias primeiro e o resto atrás de "Afinar".
- **Num Android pequeno (360×640), a tela de 4 linhas passa de uma tela.** Por isso o botão fica fixo embaixo.

---

## 7. As 3 ideias mais importantes

1. **Uma tela só, "Sua roça", com 4 perguntas já marcadas com o típico daqui** (o que planta, tamanho, terra e baixio). Com um toque ele vê o plano, e o caminho cai de cerca de 30 para 4 a 8 toques.
2. **Primeiro a resposta, depois os dados.** O globo leva direto à "Sua roça", e o passo 1 (4.550 px) vira "Do espaço", opcional. Cada passo abre com o que fazer: a agenda no plano, as barras e os 3 ajustes do Melhor no rende, a chuva e o técnico no "Se secar". O resto vai para "Ver mais".
3. **Tirar o que não muda nada e juntar o que se repete.** Água, manejo, "deu bem", "o que já faz", Garantia-Safra, preço da raiz e custo saem do caminho. A prioridade passa a ser as abas dos "Outros jeitos", o 2026 vem do jeito de hoje e a memória do ano ruim vai para o passo 5 como "bate com a sua roça?".
