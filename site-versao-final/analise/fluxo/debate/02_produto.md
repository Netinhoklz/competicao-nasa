# 02 · Produto: parecer no debate

Lente: designer de produto sênior. Li as 10 propostas e conferi no código os pontos em disputa. Nada do site foi editado.

**Veredito:** o melhor fluxo é o da **lente 01 (agricultor)**, com 8 emendas. O globo leva direto a uma **tela única "Sua roça"**
com 4 linhas já marcadas, e o plano sai em **2 toques** a partir do painel. Os resultados começam pela resposta. Cada pergunta que
sobra fica no lugar onde o efeito dela aparece. A numeração 1–5 não muda.

---

## 1. Onde mudei de ideia

| Antes (rodada 1) | Agora | Por quê |
|---|---|---|
| A tela 1 era o resumo "Pronto", com 4 fichas que abriam as telas grandes de pergunta que já existem | **Linhas inline**: cada resposta muda ali mesmo, sem entrar e voltar de subtela | Abrir e voltar de subtela traz de volta o estado de módulo (`perguntas.js:11-14`), o "Anterior" quebrado (lente 06) e o toque duplo que pula pergunta (lente 09, confirmado em `perguntas.js:115-120`: `q += 1` roda antes do `ctx.set`, e os botões antigos continuam vivos por ~1 s). Com uma tela só, os 9 links `ctx.link(2)` que já existem (`dinheiro.js:55,88,128`, `plantio.js:71,502`, `seguranca.js:412`, `roca.js:113`) caem no lugar certo sem mudar nada |
| O passo 1 ia para o fim, como "Os dados", com renumeração | **A numeração fica.** Só a entrada muda para `#/<cod>/2` (`principal.js:94`, `rocacerta.js:333`, `roca.js:194,209`). O passo 1 encolhe e continua como pílula 1 | A renumeração quebra cerca de 15 links (era o meu próprio risco nº 1) e custa ~45 min na véspera, sem ganho para quem usa. Trocar a entrada dá o mesmo efeito com 4 linhas |
| Baixio com 3 opções e o tamanho ajustado no desenho | **4 opções**: Não tenho · Pequeno · Grande · Não sei | Ajustar no desenho é UI nova em `plantio.js`. As 4 opções reusam `BAIXIO_FRAC` (`pouco`, `metade`) e a API trata pequeno, ⅓ e metade igual (`ad_baixio=15`) |
| Custo fechado em "Ajustar a conta" | **Custo à vista, numa linha logo abaixo do herói**: "Paga trator ou adubo? Não · Sim" (texto da lente 01) | A lente 03 mediu que esse custo **vira o veredito**: a sobra do plano vai de R$ 4.364 para −R$ 1.743, e o plano ganha em 47 de 100 em vez de 98. Esconder o que vira a resposta é perder precisão |
| A prioridade ficava acima de "Outros jeitos" | **A prioridade vira as próprias abas de "Outros jeitos"** (um seletor só), e o herói mostra sempre o típico grande | Hoje `garantir`, que é o padrão no El Niño, troca o número grande do herói pelo caso ruim (`dinheiro.js:147-149`, `num = garantir ? p10 : p50`). Por isso o agricultor vê R$ 984 no cartão e R$ 2.480 na barra (lente 01). As abas de `cenarios.js:18,436` já são um segundo seletor da mesma coisa |
| 2025 por um link "Contar" no cartão do giro | **Pergunta de 1 toque dentro do cartão**: "Em 2025 também foi milho e feijão? Sim · Não" (lentes 07 e 10) | A frase fica verdadeira sem afirmar o que ele não disse. Detalhe: a lente 04 diz que o padrão "2025 = 2026" já existe, mas `lerHistorico` (`historico.js:102-122`) não infere nada. Só o rascunho do modo pergunta pré-marca 2026 (`:216-221`). Sem `antes`, o cartão mostra "Conte… Contar" (`:365-366`) |

Mantive: tela única com padrões, resultado primeiro, um botão verde por tela, pergunta onde o efeito aparece, cortar o que
não é lido por nenhum código.

---

## 2. Melhores ideias dos outros

| Lente | Ideia | Por que entra |
|---|---|---|
| 01 Agricultor | A entrada pelo globo vai direto à "Sua roça", e o passo 1 sai do caminho | O painel do globo já contou o El Niño e a chuva. É o único jeito de pôr o plano em 2 toques |
| 01 Agricultor | "Paga trator ou adubo? Não · Sim" no lugar de "Só a semente / Máquina e insumos" | São as palavras dele, e cobre o equipamento do ponto 15 |
| 01 Agricultor | Sorgo e palma "viram comida da criação (fora do R$)" em vez de "não vendem" | Conserta o porquê do plano perder em R$ sem criar uma pergunta nova |
| 01 Agricultor | A área padrão perde o selo MEDIDO e passa a dizer "o típico daqui (Censo 2017)" | É medido para o município, não para o roçado dele |
| 03 Valor da informação | Medir o efeito de cada resposta (Δ R$, Δ datas, Δ plano) antes de decidir onde ela mora | É o critério que encerra a discussão. Mostrou que custo e maniva viram o veredito e que água, manejo, "deu bem" e GS dão Δ 0 |
| 04 Júri | Selo com o nome da missão: "MEDIDO · NASA SMAP" (`comum.js:24-27`) | Hoje a palavra NASA aparece 0 vezes na jornada. Com 1 função, ela passa a aparecer em todas as telas |
| 04 Júri | Juntar harmonização, satélite × chão, 7 métodos e o acerto, confiança e glossário num lugar só, para o júri | Entra como o "ver mais" do passo 1 encolhido, sem rota nova |
| 06 Arquitetura | Quem chega por um "mudar" volta ao passo de onde veio ("Voltar a Quanto rende →") | Fecha o ciclo editar → ver o efeito. É uma variável em `roca.js` e não entra no hash |
| 06 / 07 / 10 | Hoje → Melhor → Ideal uma vez só, como herói do passo 4. Sai o `heroiHtml` duplicado ("No caso ruim…") | O mesmo par R$ 2.760 × R$ 984 aparece 3 vezes |
| 08 Precisão | Tirar as frases falsas: "5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde" (+2,46 < +2,59), "+R$ 909 do baixio" (vem da troca de milho por feijão, `hoje_ideal.js:103-106`), raiz "daqui" no técnico | Um jurado que testa acha essas frases em 1 minuto. Cada uma se conserta em ~5 min |
| 08 Precisão | O "não sei" da terra é a interseção só dos solos zoneados (`motor.py:672-677`). Se o milho não é zoneado em areia, a janela mostrada não vale na areia, e a tela não avisa | É o único erro de precisão de verdade que achei confirmado no código. Justifica deixar a terra na 1ª tela |
| 08 Precisão | Mostrar "antes: …" na data quando a resposta da terra a mudou | A pessoa vê que responder valeu. O `resumo()` já faz isso (`perguntas.js:44,61`), e o trecho pode ir para o plano |
| 09 Mobile | Limite medido por passo: ≤ 1.900–2.500 px e ≤ 150 palavras à vista | Dá para conferir com `print_url.py`. "Enxuto" deixa de ser opinião |
| 09 Mobile / 07 | `.eco` de `--ink-4` (2,7–2,8:1) para `--ink-3` (~4,8:1); `summary` com 44 px de altura | A 2ª linha do título é a instrução, e hoje não passa nem em 3:1. É 1 linha de CSS |
| 05 Extensionista | O fim da jornada é "Mandar para o técnico" (WhatsApp), com Imprimir em 2º | O `window.print()` confunde no Android simples, e o ponto 16 vira ação |

---

## 3. Objeções

| Lente | Ideia | Objeção |
|---|---|---|
| 05, 07, 08, 09 | Uma pergunta por tela, com o toque que já avança (3 a 6 telas) | Leva junto os 3 defeitos de hoje: o toque duplo pula pergunta (confirmado), o estado fica fora do hash e o voltar do Android sai do passo. Além disso, todo "mudar" posterior precisa de link direto para a pergunta certa (`ctx.editar(k)`), que é trabalho novo. A tela única não tem nada disso, porque o estado inteiro já está no hash |
| 05 | Pergunta nova "Tem criação?" | O José reclamou de perguntas demais, e na v1 ela só muda texto (a própria lente admite isso). Basta trocar "não vende" por "comida da criação". Pergunta que não muda número é a personalização falsa que o júri pega |
| 05 | Terra "Rasa, de piçarra" (AD1) | Faz sentido agronômico, mas tira o milho do zoneamento e precisa de teste nos 7 municípios. Fica para depois do fluxo, se sobrar tempo |
| 04 | Levar a terra para o passo 3, ao lado das datas | Quem não rola até "Suas datas" fica com o "não sei", que é a interseção (lente 08) e dá janela errada para areia em 421 municípios. Na 1ª tela, com "Não sei" marcado, ela custa 0 toque |
| 04 | Rota nova "Como o QUADRA sabe" (`ciencia.js`) | Rota e módulo novos na véspera. O passo 1 encolhido já é esse lugar: basta pôr os extras no "ver mais" dele |
| 03 | A prioridade como 1º controle do passo 4 | Põe a configuração antes do resultado de novo, e hoje ela troca o número do herói. A prioridade vai para as abas de "Outros jeitos" |
| 03, 06 | Maniva sempre visível na tela única | Alonga a tela para todo mundo por causa de uma minoria. Vale a inferência visível no plano ("mandioca já no chão · mudar" e "Sem maniva? trocar" na Parte A), que é onde ele vê a mandioca |
| 08 | Mexer no `motor.py` para o "não sei" honesto | O diagnóstico está certo, mas mexer no núcleo na véspera é risco. Só depois do fluxo, só como sinal ou texto (sem mudar a janela), e com o JSON comparado nos 7 municípios. Se não der tempo, a tela diz "data que vale em terra que segura água" quando a cultura não tem todos os solos |
| 08 | Antes do "plano à frente em 98 de 100" | O "Hoje" conta o consórcio como metade da área para cada cultura (`calculo.js:148-151`, `area: T/2`). Se a PAM medir o rendimento na área cheia do consórcio, o Hoje sai pela metade. Isso precisa ser conferido antes de pôr o Hoje → Melhor → Ideal como herói. Não é do fluxo, mas é o número que o fluxo destaca |
| 01, 09 | Uma tela "Afinar" separada, reusando as telas de pergunta de `hoje_ideal`/`historico` | Mantém vivo o estado de módulo que estamos tirando. "Deu bem", palhada e esterco não têm destino nenhum: nem o técnico os lê (`leve_ao_tecnico.js:51-69` não lê `exp`). O afinar é a própria tela única (`#/<cod>/2`), com "ajustar quanto de cada" fechado dentro dela |
| 07, 10 | Abas embaixo (Plano · Dinheiro · Segurança · Lugar) e troca de fontes no CSS inteiro | É bom, mas mexe na casca e em 74 usos de `--mono` ao mesmo tempo que a tela única mexe em `roca.js`. Fica no fim da fila. Nesta rodada entram o contraste do `.eco` e um botão verde por tela |
| 09 | Botão "Ouvir" (speechSynthesis) | É feature nova de ~45 min, e a voz pt-BR do Android é instável. Último da fila |
| 10 | Tirar a barra de baixo do passo 2 | Prefiro a barra com o único botão "Ver o meu plano →", fixa e sempre no mesmo lugar. Num Android de 640 px, a tela de 4 linhas rola, e o botão não pode sumir |

---

## 4. Votos

| Item | Voto | Para onde |
|---|---|---|
| hoje.culturas | manter | Tela única, linha 1: "O que vai no roçado hoje?", com milho e feijão marcados (`lerHoje`, `hoje_ideal.js:35`). A % e o arranjo ficam em "ajustar quanto de cada" fechado na mesma linha (reusa `telaCulturas`/`telaArranjo`, `hoje_ideal.js:370-399`, que já devolvem HTML) |
| hoje.arranjo | inferir | Padrão "tudo junto" (`cons:1`). Muda no "ajustar" fechado da linha 1. "Milho no baixio" só aparece se ele marcou que tem baixio |
| hoje.manejo | inferir | Padrões de `lerHoje` (1ª chuva, semente pelo Censo, queima não sei). Os conselhos ficam fixos na agenda e as frases que dependem deles ficam condicionais. A tela sai |
| hist.anos | mover | Cartão "Por onde começar o seu giro" (passo 3): "Em 2025 também foi milho e feijão? Sim · Não", em 1 toque. 2026 vem do jeito de hoje |
| hist.deu | mover | Passo 5, "A sua memória": "Lembra de um ano que quebrou?", com chips dos piores anos do IBGE ali mesmo. "Deu bem" sai |
| hist.faz | fundir | O preparo (trator) vira o custo. Palhada, esterco e faixas saem: nenhum código os lê |
| terra | manter | Tela única, linha 3, com "Não sei" marcado e a dica do torrão em 1 linha. No plano: chip "terra: não sei · mudar" ao lado das datas e "antes: …" quando a data muda |
| ha | manter | Tela única, linha 2: chips ½ · 1 · 2 · 3 · 5 ha com o típico daqui marcado ("Censo 2017", sem MEDIDO) e "outra medida" que abre o `area.js` (tarefas e metros) |
| baixio | manter | Tela única, linha 4: Não tenho · Pequeno · Grande · Não sei, com os mini-desenhos |
| agua | mover | "Leve para o técnico" (passo 5): chip opcional "Tenho barreiro ou poço perto do roçado". "Cisterna de beber" sai, e a água sai da ficha do topo |
| maniva | inferir | Mandioca marcada hoje vale "plantada", com o chip "mandioca já no chão · mudar". Sem mandioca, vale "consigo". "Sem maniva? trocar" fica na linha da Parte A do plano |
| bolso.prioridade | fundir | Vira as abas de "Outros jeitos de girar" (um seletor), logo abaixo do herói. Padrão "garantir" no El Niño. O herói fica sempre com o típico grande |
| bolso.raiz | mover | Passo 4, "Ajustar a conta" (fechado), com os rótulos daqui · comum · baixo. Corrigir o "daqui" da pergunta do técnico |
| bolso.custo | fundir | Com o preparo: "Paga trator ou adubo? Não · Sim", à vista numa linha logo abaixo do herói (vira o veredito) |
| bolso.gs | inferir | Chip calculado pela área ("Garantia-Safra: você cabe, até 5 ha") no técnico. Sai o controle de 3 botões (`dinheiro.js:129`) |

Resultado: 15 respostas → **4 linhas na frente, todas pré-marcadas**, mais 3 perguntas de 1 toque no lugar do efeito (2025,
ano que quebrou, custo) e 3 ajustes fechados (%/arranjo, raiz, água).

---

## 5. Fluxo preferido: o da lente 01, com emendas

| Tela | O que tem | Ação |
|---|---|---|
| 0 Globo e painel (sem mudança visual) | Mergulho, mapa e painel com El Niño e chuva | "Montar o meu plano" → `#/<cod>/2` (**toque 1**) |
| 2 Sua roça (1 tela, ≤ 1.000 px, sem contador) | "Já marcamos o comum de Quixadá. Mude o que for diferente." 4 linhas: o que planta · tamanho · terra · baixio | Barra fixa: "Ver o meu plano →" (**toque 2**). Quem veio de um "mudar": "Voltar a <passo> →" |
| 3 Plano (≤ 2.000 px) | Manchete com 1 frase de El Niño ("plante metade, guarde metade"). Roçado de cima 2027/28/29. "O que fazer agora" (3 marcos) logo abaixo. Cartão do giro com 2025 em 1 toque. Datas com chip da terra e "antes:". "Sem maniva? trocar" na Parte A. "Por que este plano": 3–4 sanfonas com manchete de 1 linha visível (onde sofre, faixas e praga, o que cada planta faz pelo solo, parte por parte) | "Quanto rende →" |
| 4 Rende (≤ 2.500 px) | Barras Hoje → Melhor → Ideal no alto, com o típico grande e o ano ruim pequeno. Ajustes do Melhor com +R$ (rótulo corrigido). "Paga trator ou adubo? Não · Sim". "Outros jeitos" com as abas = prioridade. Fechados: "Ajustar a conta" (raiz, %, arranjo), El Niño, caixa, "paga o gasto?", como calculamos | "Se secar →" |
| 5 Se secar (≤ 2.500 px) | "2027 tende a ser apertado." 1 linha por cultura para 2027 (2028–29 fechados). "E se chover…" à vista, aberto na chuva normal (some a mediana dupla 3,2 × 3,9 da lente 08). "Lembra de um ano que quebrou?" inline. "Olhamos de novo em 19/mar e 30/abr". "Leve para o técnico" com o chip de água e o de GS | "Mandar para o técnico" (WhatsApp); "Imprimir" e "Outro lugar" como links |
| 1 O lugar e os dados (pílula 1, ≤ 1.600 px) | El Niño em 1 linha, 4 indicadores com "NASA <missão>" no selo, "11 culturas servem aqui" e a confiança em 1 linha. "Ver mais": tendências, régua, cardápio, harmonização, satélite × chão, 7 métodos e o acerto, de onde vêm os dados, glossário. Sem "Responder 5 perguntas" e sem "Pular" | "Montar o meu plano →" |

Emendas ao fluxo da lente 01:
1. Sem a tela "Afinar" separada: o afinar é a própria tela única (lente 06: "mudar" leva até ela e volta ao passo de origem).
2. A numeração 1–5 e as chaves do `PADRAO` não mudam. Muda só a entrada. Os links antigos continuam valendo.
3. O passo 1 encolhe para ≤ 1.600 px e guarda tudo o que é para o júri (lente 04). O selo ganha o nome da missão.
4. O custo fica à vista no passo 4, e o herói mostra sempre o típico (lente 03 e o código de `dinheiro.js`).
5. 2025 e o ano que quebrou viram perguntas de 1 toque, onde a resposta age (lentes 07, 08 e 10).
6. Saem as frases falsas e fica um rótulo só para o El Niño (lente 08).
7. Na casca: um botão verde (o da barra), a ficha do topo numa linha ("1 ha · milho + feijão · mudar", sem "não sei"), `.eco` com contraste ≥ 4,5:1.
8. A pergunta da criação não entra; o texto passa a dizer "comida da criação".

---

## 6. Ordem para caber em 4–6 h (um dono por arquivo)

| Prioridade | Dono | Arquivos | O quê | Tempo |
|---|---|---|---|---|
| P1 | A | `perguntas.js`, `hoje_ideal.js` (exportar `telaCulturas`/`telaArranjo`), `roca.js`, `principal.js`, `rocacerta.js` | Tela única. Entrada em `/2`. Barra com 1 botão verde. "Voltar a <passo>". Ficha numa linha. `.eco` com mais contraste | 2 h |
| P1 | B | `dinheiro.js`, `cenarios.js` | Herói no alto com o típico. Sai o `heroiHtml` duplicado. Custo numa linha. Prioridade = abas. Raiz em "Ajustar". GS vira chip. Rótulo do +R$ 909 | 1,5 h |
| P2 | C | `plantio.js`, `historico.js` | Agenda sobe. Giro com 2025 em 1 toque. Memória com o ano que quebrou inline. Maniva "trocar". Sanfonas com manchete | 1,5 h |
| P2 | D | `seguranca.js`, `leve_ao_tecnico.js`, `lugar.js`, `comum.js` | Passo 5 reordenado, com WhatsApp no fim. Passo 1 ≤ 1.600 px. Selo com a missão. Frases falsas (recorde, raiz "daqui") | 1,5 h |
| P3 | quem acabar | `motor.py` (só sinal ou texto) | "Não sei" honesto da terra, com o JSON comparado nos 7 municípios | 30 min |
| P4 | se sobrar | CSS, casca | Abas, Inter no lugar do mono, terra rasa, "Ouvir", link "Internet fraca" | — |

Para conferir: atualizar `testes/ferramentas/percorrer_fluxo.py` para a tela única e refazer os prints a 390 px nos 7
municípios. Com as mesmas respostas, o JSON da API e os R$ das barras têm que sair iguais. Cada "mudar" (passos 3, 4 e 5) tem que
abrir `#/<cod>/2` e voltar ao passo de origem. Cada passo de resultado fica abaixo do limite de px. Os 16 pontos são marcados um a
um na lista de prints.

---

## 7. Linhas vermelhas

1. **Nenhuma frase falsa na tela**: o número de perguntas, "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde", o +R$ do baixio e a raiz "daqui". Para o júri, uma frase falsa custa mais que dez telas feias.
2. **Os 3 pedidos do José ficam no caminho principal, não escondidos**: o jeito de hoje (linha 1 e herói Hoje → Melhor → Ideal), a área (linha 2, com tarefas e medida) e o histórico (2025 no giro e o ano que quebrou na memória, os dois à vista).
3. **O que muda plano, datas ou veredito fica a 1 toque e à vista**: terra, baixio, área, culturas de hoje, maniva (inferida com chip) e custo.
4. **Todo padrão aparece como padrão**: "típico daqui", "não sei", SUPOSIÇÃO. A frase do giro é condicional. A área dele não leva MEDIDO.
5. **O selo MEDIDO/SUPOSIÇÃO/PROJEÇÃO fica em todo número**, com a fonte legível no celular (o `title=` não abre no toque).
6. **Ponto 16 no fim, como ação**: "Leve para o técnico" com WhatsApp, a memória contra o IBGE e a frase da moldura.
7. **Os pontos 8, 10, 12 e 13 não somem**: cada "ver mais" deixa uma manchete de 1 linha à vista, e "E se chover…" fica aberto no passo 5.
8. **Uma ação primária por tela e um indicador de progresso só.**
9. **Rotas `#/<cod>/1..5` e chaves do `PADRAO` iguais**; servidor intocado; núcleo só com o JSON comparado nos 7 municípios.
10. **Antes de o "plano à frente" virar manchete, conferir a área do consórcio no Hoje** (`calculo.js:148-151`).

**Toques até o plano:** 2 a partir do painel ("Montar o meu plano" e "Ver o meu plano"). Quem quer personalizar faz 4 a 8 toques
na mesma tela. Hoje são 14 ou mais.
