# Integração do fluxo novo (15/11/2026, 00:35)

Ordem de serviço: `analise/fluxo/00_FLUXO_FINAL.md`, seção 7 (integrador, I1 a I6) e seção 8 (critérios). Relatórios dos construtores:
`A.md` a `E.md` nesta pasta. Não mexi em `nucleo/`, `servidor.py`, `calculo.js` nem `graficos.js`, e não reiniciei o servidor.

## Resumo

- **Os 21 critérios passam** nos 7 municípios (tabela no fim). Na 1ª rodada do aceite (antes de eu mexer) só o critério 6 falhava,
  em 8 de 35 telas: Se secar nos 7 municípios (3.075–3.366 px e 330–362 palavras, tetos 2.400 / 300) e Quanto rende de Barreiras (2.282 px, teto 2.200).
  Os outros 20 já passavam (`E:/campeonato-nasa/tmp/fluxo_novo/integ/aceite_v0.txt`).
- **Do painel ao plano: 2 toques** (era 14). **1 tela** antes do plano (eram 13). Seu Antônio: **6 toques**.
- **Altura da jornada a 390 px (Quixadá): 35.663 → 10.296 px** (caminho principal Sua roça → Se secar: 7.608 px, meta ≤ 8.000).
  **Palavras à vista: 3.332 → 1.105.**
- `teste_calculo.mjs`: saída **idêntica** à da base (`diff` vazio). R$ de Quixadá iguais aos de antes (2.480 / 4.190 / 4.360; ruim 984 / 2.490 / 2.760).
- **Zero erro de console** nos 35 passos (7 municípios × 5 passos), pelo `erros_console.py` e pelo aceite.

## Antes × depois (Quixadá 2311306, 390 px, todo "ver mais" fechado)

O "antes" é `E:/campeonato-nasa/tmp/fluxo_atual/*.txt` (altura da 2ª linha; palavras = texto da tela). O "depois" é o script da seção 8.

| Tela | Antes: telas | Antes: altura | Antes: palavras | Depois: telas | Depois: altura | Depois: palavras | Teto (seção 5) |
|---|---|---|---|---|---|---|---|
| Sua roça (passo 2) | 12 (11 perguntas + resumo) | 12.482 | 593 | 1 | 989 | 93 | 1.000 / 100 |
| O plano (3) | 1 | 5.625 | 655 | 1 | 2.306 | 275 | 2.400 / 300 |
| Quanto rende (4) | 1 | 6.629 | 718 | 1 | 2.000 | 204 | 2.200 / 260 |
| Se secar (5) | 1 | 6.377 | 828 | 1 | 2.313 | 245 | 2.400 / 300 |
| Do espaço (1) | 1 (na frente) | 4.550 | 538 | 1 (fora do caminho) | 2.688 | 288 | 2.800 / 320 |
| **Total** | **16** | **35.663** | **3.332** | **5** | **10.296** | **1.105** | |

| Toques | Antes | Depois |
|---|---|---|
| Do painel ao plano, aceitando o padrão | 14 | **2** (`#planoBotao`/`#plano` do painel → "Ver o meu plano →"; medido no `percorrer_fluxo.py`) |
| Respondendo tudo (Seu Antônio: mandioca, 3 ha, Encharca, Pequeno) | 25 a 30 | **6** |
| Telas antes do plano | 13 | **1** |
| Telas na jornada | 18 | **6** (globo + 5; Do espaço é opcional) |

Prints das 6 telas a 390 px: `E:/campeonato-nasa/tmp/fluxo_novo/final/` (`01_globo_painel`, `02_sua_roca`, `03_plano`, `04_dinheiro`,
`05_se_secar`, `06_do_espaco`, mais `07_seu_antonio_marcado` e `08_seu_antonio_plano`; cada PNG tem um TXT com o texto da tela).
Prints de cada passo nos 7 municípios: `E:/campeonato-nasa/tmp/fluxo_novo/<cod>/` (`aceite_fluxo.py --prints`).

## I1. `git diff --stat` contra os donos

Os 34 arquivos que os construtores mudaram estão todos na lista do dono (A 9, B 6, C 6, D 7, E 6). `calculo.js`, `graficos.js`, `nucleo/` e
`servidor.py` sem mudança. Fora de `web/`: `dados/financeiro_mun.json.bak` (não rastreado, de antes desta rodada; não é de nenhum dono, não mexi).

Depois da integração entram, mudados por mim: `web/js/extras/confianca.js` e `vulnerabilidade.js` (sem dono; só texto "passo N"),
`web/js/passos/LEIA-ME.md`, `testes/ferramentas/percorrer_fluxo.py` (reescrito) e `testes/ferramentas/aceite_fluxo.py` (novo).

## O que o integrador mudou (e por quê)

**Se secar (critério 6: era 3.075–3.366 px e 330–362 palavras; ficou 2.172–2.392 px e 233–261 palavras).** Nada que a seção 3.1 pede à
vista saiu da frente; saíram repetições e o detalhe foi para "ver mais":
- `seguranca.js`: o bloco "O que vamos olhar" repetia a frase da abertura ("Olhe a terra em 19/mar e 30/abr e decida com o técnico.").
  O método e o "seu olho" dos portões foram para o ver mais do fim, "Ver como medimos e quanto já acertou", junto com "o que não dá para
  projetar" e o teste com o passado. "O que já se sabe hoje" e os 28 anos foram para "Cada cultura, 2027 a 2029". "Ver cada ano: chuva,
  solo e colheita" desceu para o fim. O fim ficou com 2 ver mais (eram 4, mais 1 sob o "E se chover…").
- `seguranca.js`: o 2º tom do título cabe em 1 linha ("2028 e 2029: normal." / "2028 e 2029 também."). Sem série do IBGE (Caicó), o
  título deixou de dizer "Segurança" (nome velho do passo): "Aqui o IBGE não tem série. / Vale o que você vê na roça."
- `leve_ao_tecnico.js`: o número de perguntas é o próprio "ver mais" ("7 perguntas para a próxima conversa", um toque abre a lista);
  "Onde achar quem confira" entrou nele. Água, Garantia-Safra, Imprimir e Copiar continuam à vista. A linha do Garantia-Safra ficou
  mais curta, com as 3 partes ("paga com perda de 40% ou mais; até 5 ha cabe; renda e adesão do município: confira no sindicato").
- `cenario_chuva.css` (só ≤ 760 px): saem os pontos de cada ano (a linha "Aqui, de N anos com chuva assim…" diz o mesmo e "Ver cada ano"
  mostra os anos) e as 3 culturas ficam lado a lado, como no desenho ("milho … · caupi … · mand. …"). No computador nada muda.
- `seguranca.css`: blocos com 20 px entre si no celular e linhas de 2027 um pouco mais baixas; saiu `.seg-h2`, que ficou órfão.
- `historico.js`: o "seu olho" da memória ficou curto ("Vale a sua memória: o IBGE só vê a média.") e cabe ao lado do rótulo.

**Quanto rende em Barreiras (critério 6: 2.282 → 2.185 px).** `hoje_ideal.js`: no aviso de lavoura grande, o kg/ha foi para a fonte do
selo (o toque mostra) e o selo foi para a linha da etiqueta "seu olho". `cenarios.css`: no celular o rótulo "O que vale mais para você?"
e o selo cabem em 1 linha. `dinheiro.css`/`hoje_ideal.css`: espaços menores (summary com 44 px, que é o mínimo).

**Pedidos dos construtores atendidos:**
- E1 (`quadra.css`): `details.ver-mais > summary { margin: 0 }` para todos. E2: `.ind .ind-rot` quebra a linha (selo comprido).
- C3 (`voce_decide.css`): o texto do "seu olho" fica ao lado do rótulo num painel estreito (`flex-basis` 200 → 160 px).
- C2/B3: os seletores deles estão no `aceite_fluxo.py` (`.cen-aba[data-jeito=renda]`, `[data-maniva="nao"]`, `[data-antes]`,
  `.aviso-terra`, `[data-quebrou="milho"][data-quebrou-ano="1998"]`, `.ficha-mudar`, `#avancar`).
- A3: todos os "mudar" já usam `data-editar` (`grep`: ficha, chip Hoje, "Mudar o que planta", chip da terra); `ctx.link(2)` fica só como `href` de reserva.
- A1/B4/C4/D6/E5 (servidor recusando pedidos): o aceite roda em série, num Edge só, e repete a tela quando aparece `ERR_CONNECTION_REFUSED`.
  Aconteceu 1 vez (Crateús, passo 1, quando rodei um print em paralelo); a repetição passou limpa.
- D2: o `<select>` "outro ano" já só ganha os anos no toque (feito pelo C); não conta mais palavras.
- D3: a barra de baixo mede 63 px nos 35 passos (o aceite confere ≤ 64), com "Mandar no WhatsApp" em 1 linha.
- A5: Plano do Seu Antônio = 2.378 px (teto 2.400).
- Textos com "passo N" (as pílulas não têm mais número): `hoje_ideal.js`, `cenarios.js`, `historico.js`, `confianca.js`,
  `vulnerabilidade.js` passaram a dizer o nome da tela ("Quanto rende", "Do espaço", "o plano").
- I5: `web/js/passos/LEIA-ME.md` atualizado: o fluxo (ORDEM `[2,3,4,5,1]`, um primário por tela, histórico, padrão ≠ resposta,
  `data-editar`), `ctx.primario`, `ctx.volta`, `ctx.foco`, a regra do selo com a fonte, os limites medíveis, a lista de frases proibidas
  e a tabela de extras por passo.

## Ferramentas (I2, I3)

- `testes/ferramentas/percorrer_fluxo.py pasta [largura] [cod] [nome]`: globo (`index.html?lugar=Quixadá`) → verde do painel →
  "Ver o meu plano" (critério 2); percurso padrão 2 → 3 → 4 → 5 → 1 pelo verde e pela pílula, com print + texto de cada tela; Seu Antônio
  (critério 3, confere que o hash tem só as 5 chaves). Se o globo não abrir no Edge sem janela, usa `painel.html`.
- `testes/ferramentas/aceite_fluxo.py [cods] [--so-telas|--so-toques] [--prints]`: parte 1 = o script da seção 8 sem mudança + posições
  (critérios 1, 5, 6, 7, 9, 17, 19, 20) em cada passo dos 7 municípios, com tabela; parte 2 = os toques em Quixadá e Piritiba
  (critérios 4, 8, 10–19, 21). Grava `E:/campeonato-nasa/tmp/fluxo_novo/final/aceite.json`. Leva uns 20 min (em série).

## Resultado de cada critério

| # | Critério | Resultado | Como foi conferido |
|---|---|---|---|
| 1 | Sua roça é 1 tela, com as 4 linhas | passa | aceite: 0 `#q-prox/#hi-prox/#hs-prox` e 4 `#linha-*` nos 7 municípios |
| 2 | Do painel ao plano em 2 toques | passa | `percorrer_fluxo.py`: `index.html?lugar=Quixadá` → verde do painel → verde de Sua roça = `#/2311306/3` (o `#planoBotao` do cartão cede o lugar ao `#plano` do painel quando ele desenha; o script toca o que está à vista) |
| 3 | Seu Antônio grava só as 5 chaves | passa | `#/2311306/3?terra=barro&ha=3&baixio=pouco&maniva=plantada&hoje=milho:34,feijao:33,mandioca:33`, nada mais; o toque não muda a URL antes do verde |
| 4 | Só "Ver o meu plano" = hash sem parâmetros; "(típico)" e "(o comum daqui)" | passa | `#/2311306/3`; ficha "1,0 ha (típico) · milho e feijão · Mudar"; passo 4 "(o comum daqui)" |
| 5 | 1 verde e 0 barras de progresso | passa | 35 telas: `primarios` = 1, `contadores` = 0, `nDeM` = false |
| 6 | Alturas e palavras nos tetos | passa | Sua roça 989 px / 93; Plano 2.137–2.354 / 235–285; Dinheiro 1.939–2.185 / 188–254; Se secar 2.172–2.392 / 233–261; Do espaço 2.688–2.758 / 288–303 |
| 7 | Zero erro no console | passa | aceite (35 telas + toques) e `erros_console.py` nos 35 passos: nenhuma linha de erro |
| 8 | R$ de Quixadá e `teste_calculo.mjs` | passa | Hoje R$ 2.480 (ruim 984), Melhor R$ 4.190 (2.490), Ideal R$ 4.360 (2.760); `diff` com `base_calculo.txt` vazio |
| 9 | Gráfico ≤ 450 px, sem controle antes | passa | topo do gráfico 407–432 px; 0 `.seg`/`[data-set]` antes dele nos 7 |
| 10 | "Renda" grava `prioridade=vender` e o número não muda | passa | `#/2311306/4?prioridade=vender`; 2.480 / 4.190 / 4.360 antes e depois |
| 11 | Voltar do navegador 4 → 3 → 2 → globo | passa | `#/…/4` → `#/…/3` → `#/…/2` → `index.html` (entrando pelo globo) |
| 12 | "Mudar" da ficha no passo 4 | passa | abre `#/2311306/2` com `#linha-hoje` à vista e "Voltar a Quanto rende →"; o verde volta a `#/2311306/4` |
| 13 | Aviso da terra "não sei" | passa | Piritiba: milho e feijão comum; Quixadá: feijão comum; com `terra=barro` some |
| 14 | Linha da maniva; "Não consigo" | passa | linha à vista; `maniva=nao` e a mandioca sai do desenho |
| 15 | Cartão do giro sem `antes` | passa | "Se em 2025 também foi assim…" com SUPOSIÇÃO; "Foi no mesmo lugar" grava `antes=2026:milho,feijao\|2025:milho,feijao` |
| 16 | Memória no passo 5 | passa | "1998" no milho grava `exp=quebra=milho:1998` e mostra "O IBGE anotou…", sem sair do passo |
| 17 | "E se chover…" em 100% e 2027 acima de 900 px | passa | "Com a chuva normal…"; linhas de 2027 até 480–642 px, título do "E se chover…" 600–763 px. Caicó não tem linha de 2027: o plano de lá (mandioca, sorgo, palma) não tem cultura com série no IBGE, e o passo diz isso |
| 18 | "Mandar no WhatsApp" | passa | chama `navigator.share` (texto de 585 letras); sem ele, abre `https://wa.me/?text=…`; 0 verde no bloco do técnico. A cópia (sem share e com a janela bloqueada) foi testada pelo D |
| 19 | "MEDIDO · NASA …" à vista; o toque mostra a fonte | passa | Sua roça "MEDIDO · NASA SMAP", Se secar "MEDIDO · NASA GPM", Do espaço 5 selos NASA; o toque abre o balão com a fonte |
| 20 | Nada rola de lado, nem com tudo aberto | passa | 35 telas, com os `details` abertos 3 vezes (para os extras montarem): `scrollWidth` = 390 |
| 21 | Links antigos | passa | `#/2311306/1` abre "Do espaço"; `#/2311306/3?terra=mista&baixio=terco` abre o plano com ⅓, sem erro |

Também conferido em todas as 35 telas: topo fixo 88 px (≤ 96), barra de baixo 63 px (≤ 64), "seu olho" à vista 1 ou 2, nenhuma frase
proibida, nenhum selo < 11 px, nenhum `summary` < 44 px, a linha da terra a 598 px (acima da dobra de 844), "Agora" a 325 px e o desenho
a 501–522 px no Plano.

## Tabela do aceite (parte 1)

```
município  tela       altura palav prim olho NASA pos              erro  resultado
----------------------------------------------------------------------------------
Quixadá    Sua roça      989    93    1    1    1 terra 598           0  ok
Quixadá    Plano        2306   275    1    1    0 agora 325 des 501    0  ok
Quixadá    Dinheiro     2000   204    1    1    0 gráfico 432         0  ok
Quixadá    Se secar     2313   245    1    1    2 2027 620 ch 741     0  ok
Quixadá    Do espaço    2688   288    1    1    5                     0  ok
Crateús    Sua roça      989    93    1    1    1 terra 598           0  ok
Crateús    Plano        2306   270    1    1    0 agora 325 des 501    0  ok
Crateús    Dinheiro     2000   204    1    1    0 gráfico 432         0  ok
Crateús    Se secar     2313   245    1    1    2 2027 620 ch 741     0  ok
  (de novo 2304103/1: pronto=False erros=['LOG Failed to load resource: net::ERR_CONNECTION_REFUSED /css/passos/plantio.css', 'LOG Failed to load resource: net::ERR_CONNECTION_REFUSED /css/passos/dinheiro.css'])
Crateús    Do espaço    2758   300    1    1    5                     0  ok
Picos      Sua roça      989    93    1    1    1 terra 598           0  ok
Picos      Plano        2189   237    1    1    0 agora 325 des 501    0  ok
Picos      Dinheiro     1996   193    1    1    0 gráfico 407         0  ok
Picos      Se secar     2243   239    1    1    2 2027 550 ch 671     0  ok
Picos      Do espaço    2688   288    1    1    5                     0  ok
Caicó      Sua roça      989    93    1    1    1 terra 598           0  ok
Caicó      Plano        2354   285    1    1    0 agora 325 des 501    0  ok
Caicó      Dinheiro     1939   188    1    1    0 gráfico 407         0  ok
Caicó      Se secar     2286   247    1    1    2 2027 None ch 729    0  ok
Caicó      Do espaço    2727   297    1    1    5                     0  ok
Petrolina  Sua roça      989    93    1    1    1 terra 598           0  ok
Petrolina  Plano        2264   263    1    1    0 agora 325 des 501    0  ok
Petrolina  Dinheiro     2042   208    1    1    0 gráfico 432         0  ok
Petrolina  Se secar     2172   233    1    1    2 2027 480 ch 600     0  ok
Petrolina  Do espaço    2745   300    1    1    5                     0  ok
Arapiraca  Sua roça      989    93    1    1    1 terra 598           0  ok
Arapiraca  Plano        2137   235    1    1    0 agora 325 des 501    0  ok
Arapiraca  Dinheiro     2023   203    1    1    0 gráfico 407         0  ok
Arapiraca  Se secar     2225   235    1    1    2 2027 516 ch 637     0  ok
Arapiraca  Do espaço    2734   298    1    1    5                     0  ok
Barreiras  Sua roça      989    93    1    1    1 terra 598           0  ok
Barreiras  Plano        2331   267    1    1    0 agora 325 des 522    0  ok
Barreiras  Dinheiro     2185   254    1    2    0 gráfico 432         0  ok
Barreiras  Se secar     2392   261    1    1    2 2027 642 ch 763     0  ok
Barreiras  Do espaço    2734   303    1    1    5                     0  ok
telas com falha: 0 de 35
```

## Pendências

- **Metas de palavras** (não são teto): Sua roça 93 (meta 70), Plano 235–285 (200), Dinheiro 188–254 (180), Se secar 233–261 (200),
  Do espaço 288–300 (250). Todas abaixo do teto.
- **Folgas pequenas:** Sua roça 989/1.000 px (A: uma fileira a mais de culturas passa do teto); Se secar de Barreiras 2.392/2.400;
  Plano do Seu Antônio 2.378/2.400; Quanto rende de Barreiras 2.185/2.200.
- **"Quanto o cálculo já acertou → Se secar"** (Do espaço) leva ao topo do passo 5, não ao ver mais "Ver como medimos e quanto já acertou"
  (precisaria de uma âncora e de abrir o details ao chegar).
- **Servidor:** `servidor.py` (fila padrão de 5) recusa pedidos com vários navegadores ao mesmo tempo, e os CSS fixos do `roca.html`
  não têm nova tentativa. Com 1 pessoa não acontece; não mexi (fora do escopo).
- Da seção 9: conferir na PAM como o consórcio entra na área; limpar os modos "pergunta" órfãos depois da entrega; terra "rasa/piçarra".
- O Hoje → "mudar" vai para Sua roça (seção 7), e não para o "Ajustar a conta" na linha do arranjo (seção 2); o arranjo está a 1 toque
  pelo "ajustar" da linha "Conta com" (decisão do B, mantida).

## Código órfão (não apaguei)

- `hoje_ideal.js`, modo "pergunta": `desenharPergunta`, `telaCulturas`, `telaArranjo`, `telaManejo`, `topo` ("n de 3"), `resumoHoje`,
  `PARES`, `miniRocado`, estado `tela/rascunho/visto/zerados`; CSS `hi-quiz-*`, `hi-opcao*`, `hi-fichas`, `hi-nav`, `.hi-fecho`, `.hi-olho`.
  Só `web/teste/hoje_ideal.html` usa (e o Plano B).
- `historico.js`, modo "pergunta": `desenharPergunta`, `telaAnos`, `telaDeu`, `telaFaz`, `topo`, `botaoCult`, `novoRascunho`, estado
  `tela/rasc/visto/deHoje/zerados`, exports `resumoHistorico` e `icHist`; CSS `.hs-pergunta`, `.hs-topo`, `.hs-barra`, `.hs-titulo`,
  `.hs-op(s)`, `.hs-bloco`, `.hs-quebra`, `.hs-mot*`, `.hs-nav`, `.hs-pronto`, `.hs-fichas`, `.hs-ficha`, `.hs-ja`, `.hs-pular-txt`.
  Só `web/teste/historico.html` usa. `recomendacoes()` "Já está plantada: avisar o plano" repete a linha da maniva.
- `graficos.js`: `G.barrasH` não é mais usado pelo passo 4. `calculo.js`: `C.comida2027`, `C.precoEmpate` e `C.totais` só são usados
  por `teste_calculo.mjs`.
- `leve_ao_tecnico.js`: `FICHA.agua.cisterna` fica só para links antigos com `agua=cisterna`.
- `web/teste/cenario_chuva.html`: o comentário ainda diz que abre no El Niño (abre em 100%).
- `testes/ferramentas/print_cdp_seguranca.mjs`: ferramenta antiga do passo 5, sem uso no fluxo novo.

## Revisão e correção (15/11/2026, concluída às 01:55)

Dois revisores conferiram o fluxo: um com o olhar do agricultor (A, 21 achados, prints em `E:/campeonato-nasa/tmp/rev_agri/`) e outro
técnico (T, 9 achados, scripts em `E:/campeonato-nasa/tmp/revisor/`). Reproduzi cada achado antes de mexer
(`E:/campeonato-nasa/tmp/correcao/repro.py` → `antes.json`; créditos do mapa em `creditos.py`) e conferi de novo depois (`depois.json`,
`extra.py`). Os 30 se confirmaram (A8 e T4 são o mesmo defeito e ficaram numa linha). Corrigi todos; em 3 recusei um detalhe da correção proposta e fiz de outro jeito, com o motivo na tabela.
Não mexi em `nucleo/`, `servidor.py`, `calculo.js` nem `graficos.js`, e não reiniciei o servidor.

| # | Achado | Feito / recusado | Por quê (e o que mudou) |
|---|---|---|---|
| T1 | Toque duplo no verde pula o plano e dispara o WhatsApp (o verde religa em 22–55 ms) | **feito** | `roca.js`: um 2º toque até 700 ms depois do 1º é ignorado. Antes: 2 toques (60, 150, 400 ms) em Sua roça → `#/…/4`; agora → `#/…/3`. Em Quanto rende → `/5` e 0 share (era 1); no WhatsApp, 1 share |
| A2 | "← Mapa" depois de um "Mudar" joga no globo e perde as respostas | **feito** | `roca.js`: com `volta`, o botão é "←" e faz `history.back()` (volta ao passo de onde saiu, sem gravar o rascunho e sem entrada nova no histórico). Antes `/index.html`; agora `#/…/4` |
| A1 | Se secar: "E se chover…" em 100% diz "1 em 10" logo abaixo do "6 de 10" de 2027, sem dizer que não é 2027 | **feito em parte** | `cenario_chuva.js`: em 100% a frase passa a ser "Com a chuva normal. Em 2027 tende a chover menos: toque em “anos de El Niño”." (onde o El Niño não seca, "Com a chuva normal: não é a previsão de 2027."). **Recusado** trocar o chip para "como 2027": ele leva a 60% e mostra milho 5, feijão 4, mandioca 4 em 10, e a linha de 2027 diz 6, 5, 4 (são duas contas, a curva chuva → quebra e a projeção dos anos de El Niño); com esse nome, o chip criaria outra contradição. A frase continua começando por "Com a chuva normal" (critério 17) |
| A13 | Se secar repete o "1 em 10" 3 vezes e tem 2 "Ver como calculamos" | **feito** | A frase em 100% não repete o número (os cartões já dizem). Os títulos agora são "O que o IBGE chama de quebra" (`historico.js`) e "De onde vem esta conta" (`cenario_chuva.js`) |
| T2 | O rascunho de Sua roça se perde ao sair pela pílula ou pelo rodapé | **feito** | `perguntas.js` expõe `ctx.pendente()` (o mesmo patch do verde, com o "antes"); `roca.js` (`irCom`) grava ao sair por uma pílula ou por "Quem decide é você". Antes `#/…/3` com "Sua terra: não sei"; agora `#/…/3?terra=barro`, "Sua terra: de barro". O "←" continua sendo cancelar |
| T3 | O "antes dd/mm" vaza para outros municípios | **feito** | `sessionStorage["quadra.antes"] = {cod, jan}` (`perguntas.js`); `calendario.js` só compara no mesmo município. Picos e Barreiras: 0 data riscada falsa (antes 1 e 2) |
| A6 | "ANTES 21/02" se lê como prazo | **feito** | `calendario.js`: "FEV 01/02 · ERA 11/02", sem risco |
| A8 + T4 | Falha da API: texto de programador ("Failed to fetch… python servidor.py") e verde desligado para sempre | **feito, um detalhe recusado** | `roca.js`: tenta de novo sozinho uma vez depois de 1,5 s; se falhar de novo, "Sem sinal para carregar agora. Confira a internet e toque em Tentar de novo." e o verde da barra vira "Tentar de novo" (ligado; o toque busca de novo). Com a API falhando só 1 vez, a tela abre sozinha. **Recusado** o botão secundário com `location.reload()` dentro do erro: seria um 2º botão para a mesma coisa, e recarregar esquece a volta do "mudar" |
| T5 | O arranjo grava o padrão das culturas como resposta e tira o "(o comum daqui)" | **feito** | `dinheiro.js` `comArranjo` só troca `cons`/`mbx`; `hoje_ideal.js` `lerHoje`: `informado` só com culturas respondidas. "Em pedaços" → `hoje=|cons=0` e "(o comum daqui)" fica; "Tudo junto" → URL limpa. `escreverHoje` saiu do import de `dinheiro.js` (ficou sem uso) |
| A3 | "+ outra medida" repete ½·1·2·3·5 ha e mostra um 2º típico (1,03 ha) | **feito** | `area.js`: com `semTitulo` (só Sua roça usa) não desenha os atalhos nem a linha do típico |
| A4 | Dinheiro repete os 6 R$ do gráfico nos cartões | **feito** | `hoje_ideal.js`: com gráfico, os cartões Hoje, Melhor e Ideal ficam sem os R$ (os ajustes continuam com o +R$ de cada um). Sem gráfico, igual a antes. O critério 8 lê o gráfico: 2.480 / 4.190 / 4.360, ruim 984 / 2.490 / 2.760 |
| A5 | Chips do giro e linha da maniva sem pergunta | **feito** | `historico.js`: "Em 2025, plantou no mesmo chão de 2026?" com "Sim, no mesmo chão" / "Não, mudei"; `plantio.js`: "Mandioca (Parte A): tem maniva?" |
| A7 | O ajuste do baixio promete R$ sem a pessoa ter baixio | **feito** | `hoje_ideal.js`: com baixio "não sei", "Se tiver baixio: o milho lá embaixo e feijão em cima." (também no ajuste sem série) |
| A9 | Créditos do mapa cobrem a barra "Ver no mapa" a 1280 | **feito** | `mapa.js`: recolhidos ao "i" no `load`. Medido: antes ficavam abertos de 14 a 22 s, por cima das camadas (caixa 34–698 × 690–754 px; barra 36–376 × 638–764); agora já estão no "i" quando o mapa aparece (durante o globo o mapa não está à vista) |
| A10 | Painel do globo abre com estatística e jargão | **feito** | `rocacerta.js`: "Nos anos de El Niño forte, a chuva veio fraca em 7 de 10 municípios do Ceará." (o acaso fica no indicador); sub "o mar de ago–out 2026 · forte a partir de +1,5" (sem "ONI"); título do gráfico sem "IMERG" |
| A11 | "não tem data do ZARC aqui" na frente | **feito** | `plantio.js`: "Em terra de areia, o feijão comum não tem data segura aqui: pergunte ao técnico." (o ZARC fica no selo do bloco). Mudei o critério 13 do `aceite_fluxo.py` para o texto novo |
| A12 | "Metade guardada…" e "até ~10/mar" | **feito** | `voce_decide.js`: "Guarde metade da semente; plante quando a terra molhar a mão."; `hoje_ideal.js`: "até por volta de 10/mar" |
| A14 | "+ 7 perguntas…" parece número, "Poço ou irrigo", "Outro lugar →" | **feito** | `leve_ao_tecnico.js`: o "ver mais" tem cara de botão (borda, 52 px) e diz "Ver as 7 perguntas" (o rótulo do bloco já diz "Leve para o técnico"; "…para o técnico" quebrava em 2 linhas); "Poço ou irrigação". "Outro lugar →" saiu (`roca.html`, `roca.js`, `quadra.css`): o "Trocar" do topo faz o mesmo. A seção 3.1 pedia esse link; tirei porque repete o "Trocar" e, colado no WhatsApp, se lê como "mandar para outro lugar" |
| A15 | "11 culturas servem" × "Ver todas as 16"; "Recomendado" 6 vezes | **feito, com outro texto** | `lugar.js`: "Ver todas: mais 3 com risco e 2 só nos estudos". **Recusado** o texto proposto ("16 (5 com mais risco)"): 2 das 5 são "só nos estudos", não de risco. O "Recomendado" sai só dos cartões recomendados à vista (a bolinha verde já diz); os outros mantêm o rótulo (em Petrolina nenhuma é recomendada e as 6 à vista são "Com mais risco") |
| A16 | Tamanho sem nada aceso; "1,0 ha" × "3 ha" | **feito** | `perguntas.js`: sem resposta, o chip mais perto do típico fica tracejado (`.sr-op.sugerida`, só a cara). `comum.js` `U.ha`: sem casa decimal quando o valor está a menos de 0,05 de um inteiro (1,03 → "1 ha", também na ficha "1 ha (típico)", como no desenho da seção 3.1) |
| A17 | O giro repete a linha da maniva | **feito** | `historico.js`: com `maniva=plantada`, o cartão não repete "A Parte A já começa com a sua mandioca". Plano do Seu Antônio: 2.378 → 2.308 px |
| A18 | "Contra o plano: …" lista 5 coisas; aba "Plano" | **feito** | `cenarios.js`: "Comparado ao plano: …", "perde em" com até 2; a aba virou "Um pouco de cada" (em 2 linhas, letra 13,5 px). A grade e a tabela de "Ver a comparação" continuam "Plano" (são colunas da comparação) |
| A19 | 5 selos na 1ª dobra de Do espaço; "Os anos de El Niño discordam" | **feito** | `lugar.js`: 1 selo no rótulo "O tempo daqui" ("MEDIDO · NASA GPM", e o toque mostra a fonte dos 4 números) no lugar de 1 por cartão; "Nem todo El Niño seca igual: olhe a chuva de fevereiro." (`lugar.js` e `voce_decide.js`) |
| A20 | "O zoneamento não conferiu o ciclo da semente." | **feito** | `confianca.js`: "As datas de plantio não olham o ciclo da sua semente: confira com o técnico." (o JSON fica igual; vale na frente, no ver mais e no texto do técnico) |
| A21 | Botão de passar os meses é um 2º verde cheio | **feito** | `plantio.js` + `comum.js` (ícone novo `tocar`, um triângulo); `plantio.css`: fundo `--surface-3`, ícone verde, âmbar quando toca |
| T6 | "%" solto no hash trava a página (URIError) | **feito** | `roca.js` `lerHash`: `decodeURIComponent` com try/catch. `#/…/3?ha=50%` abre sem erro. A decodificação dupla ficou: nenhum valor das respostas usa "+" ou "&" |
| T7 | `satelite_chao` num ver mais dentro de outro | **feito** | `lugar.js`: foi para "De onde vêm os dados (satélites)", com `harmonizacao` (como a seção 6 diz). Tudo fechado: sem mudança de altura |
| T8 | "Quanto o cálculo já acertou" cai no topo do passo 5 | **feito** | `lugar.js` (`data-acerto`), `seguranca.js` (`id="seg-acerto"`), `roca.js` (`abrirAcerto`): chega com "Ver como medimos e quanto já acertou" aberto e no topo da tela (94 px, logo abaixo do topo fixo) |
| T9 | Critério 11 falhou 1 vez no aceite completo | **feito** | `aceite_fluxo.py`: repete o critério 11 quando o servidor recusou um pedido ou o 1º verde não andou, e imprime a pilha e os erros quando falha |

Também atualizei o `web/js/passos/LEIA-ME.md` (toque duplo, erro da API, rascunho nas pílulas, "←" depois de um "mudar", aba
"Um pouco de cada", `satelite_chao` em "De onde vêm os dados").

Órfãos novos (apaguei os que a minha mudança deixou sem uso): `.outro-lugar` (CSS), `.lt-cab .numero-grande` (CSS) e `escreverHoje` no import
de `dinheiro.js`. A função `escreverHoje` continua exportada por `hoje_ideal.js` (o modo "pergunta" usa).

### Resultado final (depois da correção, 15/11/2026 01:55)

- **`aceite_fluxo.py` nos 7 municípios: 0 falhas em 35 telas**, e os critérios 4, 8 e 10 a 21 passam (saída em
  `E:/campeonato-nasa/tmp/correcao/aceite_final.txt`, JSON em `E:/campeonato-nasa/tmp/fluxo_novo/final/aceite.json`, prints em
  `E:/campeonato-nasa/tmp/fluxo_novo/<cod>/`).
- **`erros_console.py` nos 35 passos: nenhuma linha de erro** (`E:/campeonato-nasa/tmp/correcao/erros_final.txt`).
- **`teste_calculo.mjs`: `diff` com `base_calculo.txt` vazio.** R$ de Quixadá na tela: 2.480 / 4.190 / 4.360, ruim 984 / 2.490 / 2.760.
- **`percorrer_fluxo.py`: nenhuma falha.** Critério 2: 2 toques (`#/2311306/2` → `#/2311306/3`). Critério 3: o Seu Antônio grava só as
  5 chaves. Prints e textos em `E:/campeonato-nasa/tmp/fluxo_novo/final/` (`01_globo_painel` a `08_seu_antonio_plano`).
- `node --check` passa nos 18 JS mexidos; `aceite_fluxo.py` compila.

| Tela (7 municípios) | Altura (px) | Palavras | Teto | Antes da correção |
|---|---|---|---|---|
| Sua roça | 989 | 93 | 1.000 / 100 | 989 / 93 |
| O plano | 2.167–2.384 | 242–298 | 2.400 / 300 | 2.137–2.354 / 235–285 |
| Quanto rende | 1.927–2.171 | 178–235 | 2.200 / 260 | 1.939–2.185 / 188–254 |
| Se secar | 2.138–2.357 | 236–268 | 2.400 / 300 | 2.172–2.392 / 233–261 |
| Do espaço | 2.604–2.707 | 281–299 | 2.800 / 320 | 2.688–2.758 / 288–303 |

| # | Critério | Resultado |
|---|---|---|
| 1 | Sua roça = 1 tela com 4 linhas | passa (7 municípios) |
| 2 | Do painel ao plano em 2 toques | passa (`percorrer_fluxo.py`) |
| 3 | Seu Antônio grava só as 5 chaves | passa |
| 4 | Só "Ver o meu plano" = hash limpo; "(típico)" e "(o comum daqui)" | passa (ficha "1 ha (típico)") |
| 5 | 1 verde e 0 barra de progresso | passa (35 telas) |
| 6 | Alturas e palavras nos tetos | passa (tabela acima) |
| 7 | Zero erro no console | passa (aceite e `erros_console.py`, 35 passos) |
| 8 | R$ de Quixadá e `teste_calculo.mjs` | passa |
| 9 | Gráfico ≤ 450 px, sem controle antes | passa (407–432 px) |
| 10 | "Renda" grava `prioridade=vender`, número igual | passa |
| 11 | Voltar 4 → 3 → 2 → globo | passa (de primeira) |
| 12 | "Mudar" da ficha no passo 4 e volta | passa |
| 13 | Aviso da terra "não sei" | passa (texto novo, sem a sigla) |
| 14 | Linha da maniva; "Não consigo" | passa |
| 15 | Cartão do giro sem `antes` | passa |
| 16 | Memória no passo 5 | passa |
| 17 | "E se chover…" em 100%, 2027 acima de 900 px | passa ("Com a chuva normal. Em 2027 tende a chover menos…"; 2027 até 480–642 px) |
| 18 | "Mandar no WhatsApp" | passa (share; sem share, `wa.me`; 0 verde no técnico) |
| 19 | "MEDIDO · NASA …" à vista e o toque mostra a fonte | passa |
| 20 | Nada rola de lado, nem com tudo aberto | passa (35 telas) |
| 21 | Links antigos | passa |

Folgas que ficaram pequenas: **O plano de Caicó com 298 palavras (teto 300)**, por causa da pergunta nova do giro e da da maniva;
Sua roça 989/1.000 px; Se secar de Barreiras 2.357/2.400. Quanto rende de Barreiras ganhou folga (2.185 → 2.171).
