# Debate · 01 · Lente do agricultor do sertão

Quem lê: Seu Antônio, 47 anos, Quixadá-CE, 5º ano, Android simples, 3 ha de milho, feijão e um pouco de mandioca, cisterna de beber e umas cabras.

> "Quero dizer o que eu planto, apertar um botão e ver o que fazer. Se o celular me perguntar de novo o que já falei, eu fecho."

**Em resumo:** 6 das 10 lentes chegaram à mesma coisa: **uma tela só, já marcada com o típico daqui**. O desacordo está em três pontos: (1) onde entra o lugar, (2) a maniva e o custo, que mudam o veredito, e (3) quantas perguntas a tela tem. Abaixo, o que eu aceito, o que eu recuso e por quê.

---

## 0. O que eu conferi antes de afirmar (API em 127.0.0.1:8090, Quixadá 2311306)

| Conferência | Resultado |
|---|---|
| `maniva=plantada` | **O plano A/B/C fica igual.** Só a Parte A da agenda passa a "já está no chão (resposta sua)", e o R$ sobe (lente 03: +R$ 1.145). Para quem tem "um pouco de mandioca", supor que a Parte A inteira já está plantada exagera. |
| `maniva=nao` | As Partes A e C viram sorgo forrageiro. A lente 03 mediu o plano à frente em 98 de 100 → 0 de 100. |
| Terra "rasa" (`textura=1&ad=11`), sugestão da lente 05 | Baixio com milho: **"não zoneada no solo escolhido (AD1)"**. Com o baixio respondido (`ad_baixio=15`), o milho volta a ter data (11/02–10/03). Ou seja: "rasa" com "baixio: não sei" deixa uma linha quebrada no plano. |
| Terra "não sei" | O milho do baixio aparece com 21/02–28/02, que é a janela da AD2, e sem aviso. Em terra rasa, essa janela não existe (confirma a lente 08). |
| Área (`ha`) | `plantio.js:67` só muda o rótulo "(padrão daqui)" e os números em ha. **A forma do desenho e as datas não mudam.** Corrijo o que eu tinha escrito ("muda o desenho"): muda os rótulos e todo o R$. |
| Prioridade | Em `dinheiro.js:147-149`, troca o número grande do herói (p10 ou p50), a ordem dos blocos (`:77`) e o jeito aceso em "Outros jeitos" (`cenarios.js:18`). Se o herói duplicado sair (lentes 06, 07, 08 e 10), sobra acender o jeito nos cenários. |
| Consórcio no "Hoje" | O comentário de `calculo.js:145` diz "milho + feijão em toda a área", mas a linha 151 usa `area: T / 2`. **O próprio código se contradiz** (risco D13 da lente 08). |
| "NASA" nas telas | `grep -ic nasa` nos 16 TXT: zero em todos (confirma a lente 04). |
| Passo 4 hoje | O "O que vale mais", o preço da raiz, o "O que você paga" e o Garantia-Safra vêm antes do primeiro R$ (`15_passo4_dinheiro.txt:10-36`). |

---

## 1. As melhores ideias dos outros

| Lente | Ideia | Por que serve ao agricultor |
|---|---|---|
| **06 Arquitetura** | Cada "mudar" abre **a pergunta certa** e devolve ele à tela de onde veio (`ctx.editar(k)`). O voltar do Android funciona. Há um único avançar, na barra de baixo. | Hoje, todo "mudar" leva à 1ª de 11 telas, e o voltar do celular sai do passo. Seu Antônio usa o voltar do aparelho, não o "← Anterior". |
| **09 Celular** | **O toque duplo pula a pergunta do tamanho** (erro medido). O eco passa de 2,8:1 para 4,9:1, os alvos ficam com ≥ 44 px e entra o link "Internet fraca? Entrar sem o globo". | Dedo grosso e 3G no sítio: o globo tem 7,8 MB (cerca de 60 s a 1 Mbps). A tela única sem auto-avanço acaba com o erro do toque duplo. |
| **03 Valor da informação** | A medição mostra que **custo e maniva não são ajuste fino**: com máquina e insumos, o plano fica à frente em 98 → 47 de 100; sem maniva, em 98 → 0. | Isso muda onde esses dois ficam: não podem ir para um "ver mais" fechado (ver o voto). |
| **08 Precisão** | Um "não sei" honesto. Corrigir "acima do recorde", o "+R$ 909" atribuído ao baixio, a raiz "daqui" que é o comum do CE, um só rótulo de El Niño e "O milho: nenhum dia". | Se ele pega o site mentindo uma vez, não acredita em mais nada. |
| **04 Júri** | Selo **"MEDIDO · NASA SMAP"**, com o nome da missão no próprio selo. O controle "E se chover…" fica no alto do passo 5. | A NASA aparece com uma troca em `comum.js`, sem tela nova. O controle de chuva é o que ele entende sem ler: "e se chover pouco?". |
| **10 Simplicidade** | Barra de baixo com a frase do ponto 16 e "Ajustar o roçado". Pílulas sem número (Plano · Dinheiro · Segurança · O lugar). Sai o herói duplicado "No caso ruim…". | Não tem número para ele achar que falta etapa, e o ajuste fica sempre à mão. |
| **05 Extensionista** | Opção de terra **"Rasa, de piçarra (a enxada bate na pedra)"**. "Copiar para o WhatsApp" como botão principal, no lugar de Imprimir. Ficha para o técnico. | Quixadá é sertão cristalino, com muita terra rasa. Ele não tem impressora, mas tem WhatsApp. |
| **04, 07, 10 e 02** | A **maniva vai para a linha da mandioca no plano** ("Não consegue maniva? Trocar"). | Ele entende "maniva" quando vê a mandioca no desenho, não numa pergunta solta. |
| **04, 06, 07 e 10** | **2025 em uma linha**, no cartão "Por onde começar o seu giro" ("Em 2025 foi igual? Sim / Não"). | A resposta só muda aquele cartão, então é ali que ela deve ser perguntada. |
| **07 Visual** | Os carrosséis que rolam de lado viram grade (hoje cortam "−6", "pelo mei", "2,5"). Fica uma letra só (Inter). | Número cortado é número errado para quem lê devagar. |
| **02 Produto** | As fichas do topo viram um chip só, sem "não sei" ("1 ha · milho + feijão · Ajustar"). Não mexer no núcleo na véspera. | "terra: não sei" em toda tela parece que ele errou alguma coisa. |

---

## 2. Objeções concretas

| Lente | Ideia | Objeção |
|---|---|---|
| **07 Visual** | 4 telas, com toque que já avança | O toque que avança sozinho é a causa do erro do toque duplo que a lente 09 mediu (pula o tamanho). As 4 telas também têm 4 contadores e 4 carregamentos de cerca de 1 s com internet fraca. Uma tela, sem avanço automático, resolve. |
| **05 Extensionista** | 5 a 6 telas com contador, mais a pergunta nova "Tem criação?" | Na v1, a criação **só muda texto**, e é o mesmo erro que estamos cortando (perguntar sem efeito). Melhor: uma frase fixa "Se tem bode ou gado, o sorgo e a palma viram comida da criação (fora do R$)", sem pergunta. E o passo 1 antes das perguntas atrasa o plano. |
| **03, 05 e 08** | Mandioca marcada no "hoje" → maniva = "plantada" em silêncio | Soma +R$ 1.145 sem ele ter dito nada, e "um pouco de mandioca" não é a Parte A inteira (⅓ de 3 ha = 1 ha). Mostrar a escolha na linha da mandioca e não inferir. |
| **03 e 06** | Maniva como 5º bloco da tela única | São 5 blocos, de 1.300 a 1.800 px. Num Android 360×640, isso passa de 2 telas. A pergunta só faz sentido quando a mandioca aparece no plano. |
| **04 Júri** | Terra no passo 3, ao lado das datas | O plano abriria com as datas do "não sei", e em terra rasa a janela do milho não existe (conferido). Ele responde a terra sem pensar ("é piçarra", "é barro"), em 1 toque. A terra fica antes do plano. |
| **02, 04, 08 e 10** | Baixio "Tenho / Não tenho / Não sei" e o tamanho ajustado "no desenho" | Ajustar no desenho é **interface nova no plano**, na véspera da entrega. "Não tenho · Pequeno · Grande · Não sei" na mesma linha custa zero toque a mais e acerta o R$ (fração de 0,2 ou 0,5, `roca.js:21`). |
| **08, 09 e 10** | Tirar o tamanho da tela única e deixar só "1,03 ha · mudar" | Com o plano de 1 ha e uma roça de 3 ha, todo R$ sai 3 vezes menor, e ele desconfia do resto. O tamanho foi pedido do José. Uma linha de chips (½ · 1 · 2 · 3 · 5) custa 1 toque e cabe na mesma tela. |
| **03 e 08** | Prioridade como 1º controle do passo 4, antes do número | Repete o erro de hoje (controles antes do resultado). O número que ela troca (p10/p50) é o do herói duplicado, que vai sair. Ela fica no cabeçalho de "Outros jeitos", depois das barras. |
| **02 Produto** | Renumerar os passos e mandar o lugar para o fim | Quebra cerca de 15 links (`ctx.link(n)`, `data-ir`) na véspera. O mesmo efeito sai sem renumerar: o globo leva a `#/cod/2`, e o passo 1 vira a aba "O lugar". |
| **08 Precisão** | Mudar `motor.py` (`so_em`) no "não sei" | O núcleo não deve mudar na véspera (lente 02). Uma frase na tela basta: "Sem saber a terra, mostramos a data que vale na terra arenosa. Em terra rasa, de pedra, o milho só vai no baixio." |
| **05 Extensionista** | Terra "rasa" (AD1) direto | Conferido: "rasa" com "baixio: não sei" dá "Milho não zoneada (AD1)" na linha do baixio. Só entra com teste nos 7 municípios e com a frase do baixio tratada. |
| **09 Celular** | Botão "Ouvir" (speechSynthesis) | É bom para quem lê pouco, mas leva cerca de 45 min, e a voz pt-BR do Android simples lê mal datas e "ha". Fica para depois, se sobrar tempo. |
| **04 Júri** | Página nova "Como o QUADRA sabe" (`ciencia.js`) | É uma rota nova. A aba "O lugar" com os extras já existentes cobre os pontos 2, 3, 6 e 7. Só entra se sobrar tempo. |
| **10 Simplicidade** | "E se chover…" dentro de "ver mais" | É o ponto 13, e é o que ele entende sem ler. Fica aberto no passo 5 (lentes 04 e 06). |
| **01 (a minha)** | Manchete "Com 3 ajustes, o seu jeito rende R$ X a mais" | Retiro. Se o "Hoje" estiver pela metade por causa do consórcio (`calculo.js:145` contra `:151`), a manchete promete dinheiro que não existe. Até conferir, ficam as barras com o selo, sem o "a mais" em letra grande. |

---

## 3. Votos

| Item | Voto | Para onde |
|---|---|---|
| hoje.culturas | **manter** | Tela única, linha 1: chips com Milho e Feijão já marcados. A divisão igual é o padrão, com a barra colorida à vista e "quanto de cada" fechado. |
| hoje.arranjo | **inferir** | "Tudo junto" (`lerHoje`), com "mudar" no cartão Hoje do passo 4. |
| hoje.manejo | **opcional** | "Afinar": as telas atuais por link, sem o subtítulo "Só o que muda a conta". Os conselhos (sem fogo, espere a janela, junte a semente) valem para todos e ficam no plano. |
| hist.anos | **mover** | Cartão "Por onde começar o seu giro" (passo 3): uma frase condicional e "Em 2025 foi igual? Sim / Não" ali mesmo. O 2026 vem do jeito de hoje. |
| hist.deu | **mover** | Passo 5, "A sua memória": os anos ruins do IBGE em chips e "Bate com a sua roça? / Foi outro ano", respondido ali, sem voltar ao passo 2. "Deu bem" sai. |
| hist.faz | **cortar** | Palhada, esterco e faixas saem. O preparo (enxada, animal ou trator) vira o rótulo do custo. |
| terra | **manter** | Tela única, linha 3: Areia · Misturada · Barro · Não sei, mais "Rasa, de pedra" se passar no teste. |
| ha | **manter** | Tela única, linha 2: chips ½ · 1 · 2 · 3 · 5 ha, "≈ N tarefas" e "outra medida" (`area.js`). O padrão diz "típico daqui (Censo 2017)", sem o selo MEDIDO. |
| baixio | **manter** | Tela única, linha 4: Não tenho · Pequeno · Grande · Não sei, com os mini-desenhos atuais. |
| agua | **opcional** | "Afinar" e "Leve ao técnico". No plano, uma frase fixa: "Datas para roçado que depende da chuva. Molha com poço? Fale com o técnico." |
| maniva | **mover** | Linha da mandioca (Parte A), **visível**: "Consigo maniva · Não consigo · Já tenho mandioca no chão". O padrão é "consigo", sem inferir "plantada". |
| bolso.prioridade | **fundir** | Cabeçalho de "Outros jeitos de girar" ("O que vale mais para você?"), depois das barras. No El Niño, o padrão é "garantir". |
| bolso.raiz | **mover** | "Mudar a conta", fechado, com o padrão "preço comum do CE" e o "daqui" corrigido. |
| bolso.custo | **fundir** | Com o preparo da terra, em **uma linha visível** logo abaixo das barras: "Conta para quem prepara na enxada ou com animal. Usa trator alugado? mudar". |
| bolso.gs | **cortar** | Chip calculado pela área ("até 5 ha, você cabe no Garantia-Safra") no passo 5 e no técnico. |

Ficam 4 perguntas antes do plano, todas já marcadas: o que planta, tamanho, terra e baixio. O resto vai para onde a resposta muda algo.

---

## 4. O fluxo que eu prefiro

**A base é o 10 (Simplicidade radical).** É quase o meu: o globo leva direto à tela única, o resultado fica em abas sem número e o lugar vira a última aba. Eu o escolho porque ele junta a barra de baixo com o ponto 16 e o "Ajustar o roçado". Emendas:

1. **Tela única com 4 linhas, não 3** (fica o tamanho em chips) e baixio com Pequeno/Grande. Sem auto-avanço, sem contador e um botão fixo só: "Ver o meu plano →" (lente 09: acaba com o toque duplo).
2. **Navegação da lente 06**: cada chip do topo e cada "mudar" abrem a pergunta certa e voltam. O voltar do Android funciona, e nada manda para o começo.
3. **No alto de cada aba, o que fazer**: no Plano, "O que fazer e quando", o desenho e a maniva na linha da mandioca. No Dinheiro, as barras Hoje → Melhor → Ideal (um número típico, com o ano ruim pequeno), a linha do trator visível e a prioridade nos "Outros jeitos". Na Segurança, a manchete, "E se chover…" **aberto**, os portões de 19/mar e 30/abr, a memória em linha e "Copiar para o WhatsApp".
4. **NASA à vista sem tela nova** (lente 04): o selo "MEDIDO · NASA SMAP" e a aba "O lugar" no roteiro da demo.
5. **Correções de texto da lente 08**: recorde, +R$ 909, raiz "daqui", um rótulo de El Niño, o "não sei" honesto e, até conferir o consórcio, nenhuma manchete de "R$ a mais".
6. **Celular (lente 09)**: eco a 4,9:1, alvos ≥ 44 px, o link "Entrar sem o globo" e nada rolando de lado.
7. **Fora desta rodada**: o "Ouvir", a página "Como o QUADRA sabe", a pergunta da criação, o CSS global da lente 07 e o `so_em` no motor.

**Toques:** 3 no globo e "Ver o meu plano" = **4** para quem aceita o típico. Com as respostas de Seu Antônio (Mandioca, 3 ha, Misturada, Pequeno) = **8**. Hoje são cerca de 30.

**Tempo** (3 donos, um por arquivo):

| Dono | Arquivos | Tarefas | Tempo |
|---|---|---|---|
| A | `perguntas.js`, `roca.js`, globo | Tela única e entrada em `#/cod/2` (2 h), e "mudar" que abre a pergunta certa e as pílulas (0,7 h) | ≈ 2,7 h |
| B | `plantio.js`, `historico.js` | Ordem do passo 3, maniva e 2025 em linha | ≈ 1,2 h |
| C | `dinheiro.js`, `seguranca.js`, `comum.js` | Ordem dos passos 4 e 5 (1,5 h), linha do trator, memória em linha e selo NASA | ≈ 2 h |
| Todos | textos e testes | Textos (0,3 h), mais prints e `percorrer_fluxo.py` nos 7 municípios (0,7 h) | ≈ 1 h |

---

## 5. Linhas vermelhas (não pode ser cortado)

1. **Com 1 toque ele vê o plano.** Nenhuma pergunta obrigatória sem padrão marcado.
2. **Um botão verde por tela, sempre no mesmo lugar.** Nada de "Pronto" no meio, nada de contador que recomeça e nada de promessa falsa ("5 perguntas", "Só o que muda a conta", "muda o que dá para salvar").
3. **O jeito de hoje (o que planta) e o tamanho ficam na 1ª tela.** São pedidos do José e a base do "Hoje".
4. **Terra e baixio ficam antes do plano**, porque mudam as datas e as partes.
5. **"Mudar" e "Contar" nunca levam de volta ao começo.** Abrem a pergunta certa, e o voltar do celular funciona.
6. **O que vira o veredito não fica escondido nem é inferido em silêncio:** a maniva na linha da mandioca e o trator numa linha visível do passo 4.
7. **"O que fazer e quando" na 1ª dobra do plano, e Hoje → Melhor → Ideal no alto do passo 4**, com um número por barra.
8. **Ponto 16 até o fim:** a frase na barra, "Leve para o técnico" com WhatsApp e a memória do ano ruim respondida no passo 5.
9. **Selo em todo número**, e o tamanho padrão sem MEDIDO falso ("típico daqui, Censo 2017").
10. **O "E se chover…" fica aberto no passo 5** (ponto 13), e o lugar continua a um toque (pontos 1, 2, 3, 7 e 11).

---

## 6. Onde eu mudei de ideia

- **Maniva:** de "inferir 'tem' quando marca mandioca" para **"mostrar na linha da mandioca, sem inferir 'plantada'"**. A lente 03 mediu 98 → 0 de 100 sem maniva. A API mostra que "plantada" só muda a agenda e o R$ (+R$ 1.145), e "um pouco de mandioca" não enche a Parte A.
- **2025:** de "Afinar" para **"em linha no cartão do giro"**. A resposta só muda aquele cartão (lentes 04, 06, 07 e 10).
- **Custo:** de "fechado em 'Mudar a conta'" para **uma linha visível debaixo das barras**. Com trator alugado, o plano cai de 98 para 47 de 100 (lente 03). Não é ajuste fino.
- **Manchete de R$ "a mais":** retiro até conferir o consórcio a 50% (`calculo.js:145` diz uma coisa, a `:151` faz outra).
- **Área:** corrigi o motivo. Ela não muda o desenho nem as datas, só os rótulos e o R$. **Continuo mantendo** pela confiança dele e pelo pedido do José.
- **Não mudei** a entrada direta na "Sua roça". O painel do globo já diz o El Niño. Aceito a emenda do júri (selo NASA e a aba "O lugar" na demo) para não perder os pontos 1, 2, 3, 7 e 11.
