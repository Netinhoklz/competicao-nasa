# Construtor C: Plano e histórico (15/11/2026, 00:08)

Ordem de serviço: `analise/fluxo/00_FLUXO_FINAL.md`, seção 7, dono C. Só mexi em arquivos do C:

| Arquivo | Linhas |
|---|---|
| `web/js/passos/plantio.js` | +104 / −42 |
| `web/js/passos/plantio/calendario.js` | +38 / −19 |
| `web/css/passos/plantio.css` | +65 / −20 |
| `web/js/extras/historico.js` | +58 / −23 |
| `web/css/extras/area_historico.css` | +17 / −4 |
| `web/css/extras/saude_solo.css` | +11 / −4 |

`desenho.js` e `vulnerabilidade.css` ficaram sem mudança: o título repetido da vulnerabilidade sai por `plantio.css:119`. `node --check` passa nos 3 JS.

**Antes × depois (Quixadá, `#/2311306/3`, 390×844, todo "ver mais" fechado):**

| | antes | depois |
|---|---|---|
| altura | 5.625 px | 2.316 px |
| palavras | 655 | 275 |
| primários à vista | 2 | 1 |
| "seu olho" à vista | 3 | 1 |

## 1. O que fiz

### C1. `plantio.js`: ordem nova
- **Ordem** (`plantio.js:563-565`): `abertura` → `faixaAgora` → `heroi` → `linhaManiva` → `blocoTempo` → giro (`U.extra("historico", {modo:"cartao"})`) → `porQue`.
  - Saiu o CTA verde "Ver quanto rende" (o antigo `:505`), porque o primário agora é o `#avancar` da casca.
  - Saiu o `linkPergunta`.
- **Abertura** (`:66-69`):
  - o kicker "Passo 3 · como plantar" virou "Como plantar";
  - saiu a linha "Seu roçado de 1 ha (padrão daqui)… Mudar", porque a ficha da casca faz isso.
- **Faixa "Agora"** (`:72-75`): `U.faixa("semente","verde","Agora: …")` usa a nova `export function agora(ctx)` (`calendario.js:52-59`). Exemplos:
  - "Agora: junte semente, maniva e mudas; nada de fogo." (Quixadá);
  - "Agora: já dá para plantar mandioca, caupi e palma, até 17/12." (Piritiba, Barreiras).
- **Linha da maniva** (`:318-333`): aparece logo abaixo do desenho, só quando alguma parte tem Mandioca ou quando `ef.maniva === "nao"`.
  - "Mandioca (Parte A):" com 3 botões: Consigo maniva (`""`) · Já tenho no chão (`plantada`) · Não consigo (`nao`).
  - Cada botão chama `ctx.set({maniva})` (`:567-569`).
  - Com `nao`, aparece "Sem maniva: a mandioca saiu do plano." e o botão "voltar".
  - Rótulo "Já tenho no chão": é o do wireframe. O texto longo quebrava em 3 linhas.
- **"Por que este plano"** (`porQue`, `:412-419`): 3 `U.verMais` com a manchete no título:
  - "Onde o seu roçado sofre mais": `vulnerabilidade`, `{painel:false}`;
  - "Por que em faixas: a praga anda menos": `blocoFaixas`, que virou um `div`, com o selo na frase e os anos (`:372-410`);
  - "O que cada planta faz pelo solo": `saude_solo`, `{titulo:false}`.

  Os extras só são montados quando a pessoa abre. O h3 interno da vulnerabilidade fica escondido (`plantio.css:119`).

### C2. `blocoTempo` (`plantio.js:356-369`)
- **Chip "Sua terra: não sei · mudar"**:
  - é `<a href=link(2) data-editar="terra">`: sem o JS do A, ele ainda leva a Sua roça;
  - testado com o A: abre `#/…/2` com `#linha-terra` na tela, e o primário diz "Voltar ao plano →".
- **Aviso do "não sei"** (`avisoTerra`, `:342-352`): uma linha por cultura cujo `cardapio[].por_solo` não tem janela no cód. 1 nem no 12 (um `risco` diferente de "nenhum"). O texto é "Em terra de areia, o milho não tem data do ZARC aqui.", com "a" para mandioca e palma.
  - **Interpretação:** entram as culturas do plano **e as do jeito de hoje** (milho → Milho, feijão → Feijão comum, mandioca).
  - Sem isso, o exemplo da ordem ("feijão comum em Quixadá") não aparecia: o feijão comum não está no plano de Quixadá, só no jeito de hoje padrão (milho + feijão).
- **Linha fixa** (`:365`): "Datas para roça de chuva. Molha a roça? Fale com o técnico."

### C3. `historico.js`, cartão do giro (`historico.js:358-385`)
- **Sem `resp.antes`:** supõe 2026 e 2025 iguais ao jeito de hoje (`lerHoje`). Mostra "Se em 2025 também foi assim (milho e feijão):" e as recomendações, com 1 selo SUPOSIÇÃO; a fonte do selo diz que o ano é suposto.
- **Botões** (`:372-374`, `:381-383`):
  - "Foi no mesmo lugar" grava `antes=2026:milho,feijao|2025:milho,feijao`;
  - "Mudei de lugar" grava `antes=2026:milho,feijao`, que dá "Nada repetiu: siga a ordem A, B, C do plano.";
  - o botão escolhido fica verde, com ✓.
- **Saiu o "Contar"** e o `link` dele.
- **Nova opção `olho`:** o plano passa `olho:false` quando o "seu olho" da metade guardada já está à vista (`plantio.js:354, 564`). Fica 1 "seu olho" à vista, e o passo nunca fica sem nenhum.

### C4. `historico.js`, memória (`historico.js:387-473`)
- **Sem quebra contada:** "Lembra de um ano que quebrou?" e, por cultura (milho, feijão), os 3 piores anos do IBGE (`piores()`) mais o `<select>` "outro ano" (1998–2025).
- **O toque** chama `ctx.set({exp: escreverExp({...e, quebras:[...e.quebras,{c,ano}]})})` (`:458`).
- **Saiu** "Contar o meu ano ruim".
- **O `<select>` só ganha os 28 anos no toque** (`pointerdown`/`focus`, `:460-466`). Antes, o `innerText` contava 56 "palavras" a mais no passo 5 (passo do D).
- **Fora do pedido, pequeno:**
  - cada memória ganhou um "desfazer" (`:405`, `:467-471`), porque um toque errado não tinha volta;
  - a cultura que ainda não foi contada continua com os chips ("Lembra de outro ano ruim?").

### C5. CSS
- **`saude_solo.css:46-57`:** os 4 cartões viraram uma grade 2×2 a ≤ 560 px. Saiu o carrossel de `plantio.css`.
- **"Seu olho":** no máximo 2 à vista. Na prática fica 1:
  - o das faixas foi para o "ver mais" da rotação;
  - o dos vizinhos ficou dentro da sanfona das faixas;
  - o do giro só aparece quando falta o da metade.
- **`plantio.css`:**
  - novos blocos: `.plantio-agora`, `.plantio-maniva`, `.terra-chip`, `.aviso-terra`, `.sequeiro`, `.plantio-porque` (summary com 44 px e manchete em `--ink`);
  - "ver mais" mais baixos no passo (`:109-111`);
  - linha do tempo com bolas de 40 px.
- **`area_historico.css`:** `.hs-se`, `.hs-giro-chips`, `.hs-tirar`, `.hs-mem-anos`, `.hs-mem-linha` (alvos de 44 px), e o rótulo do cartão em 1 linha a ≤ 420 px. Saiu `.hs-piores`, que ficou órfão.

### C6 (opcional). "antes:" nas datas, feito
- `calendario.js:45-48` e `:87-99` leem `sessionStorage["quadra.antes"]`, que o A grava (`perguntas.js:59-65`), com `try/catch`.
- O cartão de plantar mostra "FEV 01/02 ANTES ~~11/02~~" quando a janela da cultura que dá a data mudou. As duas pontas vêm de `agenda.culturas`, para não comparar fontes diferentes.
- Testado de ponta a ponta: em Sua roça, Encharca → Ver o meu plano.

## 2. O que mudei além do texto da ordem (para caber no teto de 2.400 px)

Com tudo o que a ordem pede, a 1ª versão deu 3.437 px. Para caber, mudei 3 coisas:

1. **A linha do tempo ficou com 3 cartões** (`calendario.js:79-84`): os 2 primeiros plantios do roçado e a 1ª colheita.
   - O preparo e a cerca ficam no calendário completo.
   - **Saiu o cartão "Agora"**, porque a faixa sob o título diz a mesma frase; ficava repetido a 600 px de distância.
   - O wireframe mostrava "agora → fev → mar → mai"; agora é "fev → mar → mai", com o agora no topo.
2. **No celular, a lista das partes, o mês a mês e a rotação foram para um "ver mais" só:** "Ver mês a mês e a rotação 2027–2029" (`plantio.js:181-187`).
   - Ele usa `est.compacto`, ou seja, janela < 486 px.
   - A rotação é um "ver mais" dentro dele.
   - Ele fica aberto quando o mês a mês está ligado: testei um redesenho por maniva no meio do mês a mês e o controle continua à vista.
   - O desenho já traz o nome e a área de cada faixa.
   - **No desktop nada muda:** a lista continua ao lado do desenho e os meses embaixo.
3. **Saiu o botão "Ano todo"**, porque o botão do ano já volta ao ano todo. O play ficou à esquerda das 2 fileiras de meses. As linhas "Cerca viva…" e "Tracejado…" viraram 1 linha ("Cerca viva: palma e gliricídia") mais o "se tiver (tracejado)" na linha do baixio.

## 3. Critérios da seção 8 que tocam o C

Medição a 390×844, com o script da seção 8 mais as posições (`E:/campeonato-nasa/tmp/fluxo_novo/C/medir.py`):

| Município | altura | palavras | primários | olhos | lateral | "Agora" | desenho | erros |
|---|---|---|---|---|---|---|---|---|
| Quixadá 2311306 | 2.316 | 275 | 1 | 1 | não | 325 | 385 | 0 |
| Crateús 2304103 | 2.316 | 270 | 1 | 1 | não | 325 | 385 | 0 |
| Picos 2208007 | 2.198 | 237 | 1 | 1 | não | 325 | 385 | 0 |
| Caicó 2402006 | 2.363 | 285 | 1 | 1 | não | 325 | 385 | 0 |
| Petrolina 2611101 | 2.273 | 263 | 1 | 1 | não | 325 | 385 | 0 |
| Arapiraca 2700300 | 2.146 | 235 | 1 | 1 | não | 325 | 385 | 0 |
| Barreiras 2903201 | 2.340 | 267 | 1 | 1 | não | 325 | 407 | 0 |
| Piritiba 2924801 | 2.385 | 276 | 1 | 1 | não | 325 | 407 | 0 |

Em todos: `proibidas = []`, `selosPequenos = 0`, `summaryBaixo = []`, `contadores = 0`, `nDeM = false`.

- **6, 7, 9 do Plano:** passam. Altura ≤ 2.400, palavras ≤ 300 (teto), "Agora" ≤ 400 e desenho ≤ 550. A **meta** de 200 palavras **não** foi atingida (235–285).
- **13:** passa.
  - Quixadá: "Em terra de areia, o feijão comum não tem data do ZARC aqui."
  - Piritiba: milho e feijão comum.
  - Caicó: milho e feijão comum.
  - Picos: feijão comum.
  - Com `terra=barro`, as linhas somem (Quixadá e Piritiba). Com `arenosa` ou `mista` também não aparecem, porque o aviso só vale para "não sei".
- **14:** passa. "Não consigo" grava `#/2311306/3?maniva=nao`. O desenho fica com A sorgo, B caupi, C sorgo e o baixio com milho, sem mandioca.
- **15:** passa. "Se em 2025 também foi assim (milho e feijão):" com selo SUPOSIÇÃO; "Foi no mesmo lugar" grava `antes=2026:milho,feijao|2025:milho,feijao`.
- **16** (no passo 5 do D): passa. Tocar "1998" no milho grava `exp=quebra=milho:1998` e aparece "O IBGE anotou 0,0 sacos/ha em Quixadá (normal 8,2) · Bate: o município todo quebrou nesse ano." O "outro ano" (2016) e o "desfazer" também foram testados.
- **20:** passa. Com todos os `details` abertos 3 vezes, a montagem dos extras dá `scrollWidth = 390`, em Quixadá e Arapiraca.
- **21:** passa. `#/2311306/3?terra=mista&baixio=terco` abre com 2.313 px e sem erro.
- **12** (a parte do C): o chip da terra tem `data-editar="terra"` e funciona com o tratamento do A.
- **Console:** `erros_console.py` sem erro em `#/2311306/3`, `#/2311306/5` e `teste/historico.html?modo=todos`.

## 4. Pedidos ao integrador

1. **LEIA-ME.md (I5), passo 3:**
   - Os extras do passo 3 agora ficam em "ver mais" ("Por que este plano"), não à vista.
   - `historico` `{modo:"cartao", olho}`: o cartão não usa mais `linkPergunta`.
   - `agora(ctx)` vem de `plantio/calendario.js`.
   - A linha do tempo tem 3 cartões.
2. **`percorrer_fluxo.py` (I2), seletores do C:**
   - `[data-maniva="nao"]`;
   - `[data-antes]`: o 1º é "Foi no mesmo lugar";
   - `.terra-chip[data-editar="terra"]`;
   - `.aviso-terra`;
   - `[data-quebrou="milho"][data-quebrou-ano="1998"]`;
   - `select[data-quebrou]`, que só ganha os anos no `focus`.
3. **Para o D (`voce_decide.css`):** a 390 px, o texto do "seu olho" desce para baixo do rótulo e a caixa fica com cerca de 90 px. Com o texto na mesma linha, todo passo ganha uns 20 px.
4. **Servidor:** com os 5 construtores testando ao mesmo tempo, o `servidor.py` recusou conexões várias vezes (`ERR_CONNECTION_REFUSED` em CSS e JS). Por isso medi com repetição (`rodar.sh`). Se aparecer um passo sem estilo no aceite, repita antes de culpar o código.

## 5. Código órfão (não apaguei)

- **`historico.js`, modo "pergunta":** `desenharPergunta`, `telaAnos`, `telaDeu`, `telaFaz`, `topo`, `botaoCult`, `novoRascunho`, o estado `tela/rasc/visto/deHoje/zerados` e os exports `resumoHistorico`, `icHist` e `lerHistorico`.
  - O `perguntas.js` novo do A não importa mais o `historico.js`.
  - Quem usa é só `teste/historico.html`.
- **`area_historico.css`, CSS desse modo:** `.hs-pergunta`, `.hs-topo`, `.hs-barra`, `.hs-titulo`, `.hs-op(s)`, `.hs-bloco`, `.hs-quebra`, `.hs-mot*`, `.hs-nav`, `.hs-pronto`, `.hs-fichas`, `.hs-ficha`, `.hs-ja` e `.hs-pular-txt`.
- **`recomendacoes()`, ação "Já está plantada: avisar o plano":** continua funcionando, mas agora repete a linha da maniva (com mandioca marcada, o A já grava `maniva=plantada`, e a ação quase não aparece).

## 6. Como testei

- **Prints a 390 px** em `E:/campeonato-nasa/tmp/fluxo_novo/C/`:
  - os 8 municípios: `p3_<cod>.png`;
  - antes × depois: `antes_2311306_3.png` e `p3_2311306_lado.png`;
  - as 3 sanfonas abertas: `p3_porque_aberto.png` (recortes em `p3_porque_1/2.png`);
  - maniva: `c14_maniva_nao.png`;
  - giro: `c15_giro_mesmo.png`, `c15_giro_mudei.png`, `c15_giro_lado.png`;
  - memória: `c16_memoria*.png`, `c16_passo5.png`;
  - "antes:": `c6_antes*.png`, `c6_fluxo_real.png`;
  - "mudar" da terra: `c12_terra_mudar.png`;
  - mês a mês: `c_mes.png`;
  - desktop a 1280 px: `p3_desktop.png`.
- **Ferramentas:**
  - `medir.py`: CDP, critérios da seção 8, posição dos blocos e erros de console;
  - `rodar.sh`: repete quando o servidor recusa.
