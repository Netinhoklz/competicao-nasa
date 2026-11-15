# Construtor A: casca e "Sua roça" (15/11/2026)

Ordem de serviço: `analise/fluxo/00_FLUXO_FINAL.md`, seção 7 (dono A). Todas as tarefas de A foram feitas, inclusive as duas opcionais.
Só mexi nos 9 arquivos do dono A (`git diff --stat`: roca.html, roca.js, quadra.css, perguntas.js, perguntas.css, area.js, principal.js,
rocacerta.js, index.html).

## O que fiz

### 1. Entrada direto em "Sua roça"
- `web/js/globo/principal.js:94` e `web/js/globo/rocacerta.js:333`: o botão "Montar o plano do meu roçado" leva a `roca.html#/<cod>/2`
  (os comentários do cabeçalho, `:5` e `:6`, também).
- `web/js/roca.js:243` (exemplos) e `:258` (busca): `#/<cod>/2`. Sem número de passo na URL (`#/<cod>`), o padrão passou a ser 2 (`:46`).

### 2. Tela única (`web/js/passos/perguntas.js`, reescrito)
- Rascunho `{cult, ha, area_un, terra, baixio}` + o conjunto `tocado` + os `<details>` abertos, refeitos quando `ctx.entrou` (`:25-28`, `:162-171`).
  Cada toque só redesenha a tela: não grava, não chama a API e não avança.
- Linha 1 (`:97`): chips de `opcoesCultura(ctx.r)` com `CULT`; a barra `hi-divisao` com ícone + % (o nome só com 2 culturas) fica
  sempre à vista, **dentro** do resumo do "+ quanto de cada", que abre os ± de `mexer` e o "dividir igual" de `igual` (`:93`).
- Linha 2 (`:107`): "Tamanho: 1,0 ha, típico daqui" + selo SUPOSIÇÃO; chips ½·1·2·3·5 ha; "+ outra medida (≈ 3 tarefas)", que roda
  `AREA.render(slot, ctxRascunho, {semTitulo: true})` (`montarArea`, `:149`). O `ctxRascunho` só muda o rascunho (`set` → `tocado.add("ha")`).
- Linha 3 (`:114`): terra com 4 opções (`arenosa`, `mista`, `barro`, `""`), ícone em cima, e `olho(OLHOS.terra)`. Sem "qualquer terra".
- Linha 4 (`:120`): baixio com 4 opções (`nao`, `pouco`, `metade`, `""`) e o `miniRocado`. Quem chega por um link antigo com
  `baixio=terco` vê uma 5ª opção "Um terço" já marcada (`:15`, `:90`).
- Faixa do El Niño e do solo (`faixa`, `:68`) com `U.selo("medido", fonte)`; a fonte começa pelo solo ("Solo: NASA SMAP L4…; El Niño:
  índice ONI da NOAA…"), então o selo curto do E sai "MEDIDO · NASA SMAP".
- `patch` (`:41`): só as linhas tocadas e só o que mudou de fato (marcar e desmarcar a mesma coisa não grava nada). `hoje` grava **só as
  culturas** e mantém as chaves que a pessoa já tinha (`hojeTxt`, `:35`; `milho:50,feijao:50|cons=0|mbx=1` + mandioca →
  `milho:34,feijao:33,mandioca:33|cons=0|mbx=1`). Maniva: mandioca **acrescentada** com `maniva` vazio → `plantada`; mandioca tirada com
  `plantada` → `""` (só quando a mandioca entra ou sai, para não apagar o que a pessoa escolheu no passo 3).
- Botão (`:173`): `ctx.primario("Ver o meu plano →" | rótulo da volta, fn)`. A `fn` grava `sessionStorage["quadra.antes"]` (`:59`), troca a
  entrada atual do histórico por `#/<cod>/2?<respostas>` (`location.replace`) e faz `location.hash = ctx.link(ctx.volta || 3, patch)`.
  Assim o voltar do Android reabre "Sua roça" como a pessoa deixou, e não no padrão.
- `ctx.foco` (`:179`): rola até `#linha-<k>` (com `scroll-margin-top` para o topo fixo) e acende a linha por 2,6 s. Com foco no tamanho
  e `area_un` gravado, o "+ outra medida" já abre.
- Saíram `fase`, `q`, `telaForcada`, `resumo()`, o contador "pergunta n de 5", as telas de arranjo, manejo, anos, deu-bem, o-que-faz,
  água e maniva e os imports de `historico.js`.

### 3. Casca (`web/js/roca.js`, `web/roca.html`)
- `PASSOS` com `titulo`/`curto`/`primario`/`volta` e `ORDEM = [2, 3, 4, 5, 1]` (`roca.js:10-17`). Pílulas sem número, na ORDEM, a atual
  acesa (`aria-current="step"`) e as anteriores com ✓; "Sua roça · O plano · Quanto rende · Se secar · Do espaço" no computador e
  "Roça · Plano · Dinheiro · Seca · Espaço" no celular (`:138`). As pílulas agora ficam **dentro** do topo fixo (`roca.html`, `<header>`).
- `ctx.primario(rotulo, fn)` (`:187`), refeito a cada `desenhar()` com o padrão do passo (`primarioPadrao`, `:117`): Sua roça "Ver o meu
  plano →" ou "Voltar a <passo> →"; Plano "Quanto rende →"; Dinheiro "E se secar? →"; Se secar "Mandar no WhatsApp" (`import(leve_ao_tecnico)
  .then(m => m.compartilhar(ctx))`, com `rolarAoTecnico` se o export faltar); Do espaço "Ver o meu plano →" (vai ao 3). Sem rótulo, fica o
  padrão do passo.
- Um toque só (`:328`): o primário se desliga no clique e só religa quando a tela muda; se a tela não muda (WhatsApp), religa 0,8 s depois.
- Voltar (`:322`): "←" vai ao anterior na ORDEM; em Sua roça vira "← Mapa" (`index.html`).
- `[data-editar]` (`:303`): guarda `volta = passo` e `foco = k` e faz `location.hash = link(2)`; em Sua roça só rola até a linha.
  `ctx.volta` e `ctx.foco` estão no ctx (`:182`) e somem quando a pessoa sai de Sua roça (`:165`).
- Ficha em 1 linha nos passos 3–5 (`:144`): "1,0 ha (típico) · milho e feijão · Mudar"; o tamanho tem `data-editar="ha"`, as culturas e o
  "Mudar" têm `data-editar="hoje"`.
- Rodapé do ponto 16: `<footer class="passo-fim">` logo depois do `<main>` em `roca.html`, com o `#decide-fim` (mesma lógica do
  `#moldura`, `roca.js:314`) e, só no passo 5, o link pequeno "Outro lugar →" (`:155`). No celular a frase sai da barra e fica no rodapé;
  no computador continua na barra.
- Selo (`:267-300`): toque (ou Enter) em `.selo` abre um balão fixo com a fonte (`data-fonte`, ou o `title` se o E ainda não tiver posto)
  por 5 s; some ao rolar ou tocar fora; dentro de um `<summary>`, o toque mostra a fonte e não abre o "ver mais".
- Robustez (`:18-26`, `:197`): o glossário virou import dinâmico opcional, e o módulo do passo, `hoje_ideal.js` e o glossário têm 1 nova
  tentativa (como os extras de `comum.js`). Motivo: nos testes, o servidor recusou `glossario.js` num pico e o import estático derrubava a
  casca inteira (tela vazia em Arapiraca).
- `ROT` (só servia à ficha antiga de 5 fichas) saiu.

### 4. `web/css/quadra.css`
- `--ink-3` novo (`:9`, ≈ 5,2:1 sobre `--bg`) e `.eco` das manchetes com ele (`:94`, `:97`).
- `summary { min-height: 44px }` e o `summary` do ver-mais com 44 px (`:154`, `:162`); `.selo` 11 px, `nowrap`, `tabindex` com foco visível (`:172`).
- Topo fixo (`:48`) com marca + lugar numa linha e as pílulas embaixo: 88 px a 390 (meta ≤ 96). Barra de baixo em 1 linha: 63 px (meta ≤ 64),
  com a moldura escondida ≤ 760 px.
- `.ficha` em 1 linha, `.passo-fim`/`.decide-fim`/`.outro-lugar`, `.selo-balao` e `.botao.primario:disabled` (`:149`, `:176`, `:202-216`).

### 5. `web/js/extras/area.js`
- `:25` e `:190`: o selo do típico passou de MEDIDO para SUPOSIÇÃO ("típico do município no Censo Agropecuário 2017 (IBGE: área de lavoura
  do estabelecimento familiar), aplicado ao seu roçado").

### 6. Opcionais
- `web/index.html:139-143`: "Internet fraca? Entrar sem o globo →" na tela de carga do globo (leva a `roca.html`, que abre a busca de
  município). O `aria-hidden` passou do contêiner para a marca e a barrinha, para o link poder ser focado.
- `sessionStorage["quadra.antes"]` = `{cultura: "dd/mm a dd/mm"}` (as janelas de antes da gravação), com try/catch; é apagado quando
  "Ver o meu plano" não muda nada (para o C não mostrar "antes" velho).

## O que mudei em relação ao desenho da seção 3, e por quê

Tudo para caber no teto de 1.000 px e 100 palavras a 390 px. Sem esses ajustes, a primeira versão tinha 1.239 px.
- h1: "É assim o seu roçado? / Marcamos o comum daqui." ("Já" saiu para o 2º tom caber em 1 linha).
- Terra em 4 colunas (ícone em cima) no lugar de 2×2. "≈ N tarefas" foi para o resumo "+ outra medida (≈ 3 tarefas)".
- A barra da divisão é o próprio resumo do "+ quanto de cada" (continua sempre à vista).
- A ficha usa só os nomes ("milho e feijão", como no desenho) e não o `descHoje` inteiro ("milho 50% + feijão 50% · tudo junto"), que não
  cabe em 1 linha a 390 px.
- O rodapé do ponto 16 fica fora do `#jornada` (irmão do `<main>`), como antes, quando estava na barra. Por isso as 10 palavras dele não
  entram no "palavras" do script.
- A faixa do El Niño ocupa 2 linhas a 390 px (texto + selo "MEDIDO · NASA SMAP"), 44 px no total. No computador fica em 1 linha.

## O que não fiz
- Nada da lista de A ficou de fora.
- Não mexi em `hoje_ideal.js`, `historico.js` nem nos CSS deles. Os modos "pergunta" ficaram órfãos na jornada (ver abaixo).

## Código órfão (não apaguei)
- `hoje_ideal.js`: `desenharPergunta`, `telaCulturas`, `telaArranjo`, `telaManejo`, `topo` ("n de 3"), o export `resumoHoje` e o estado
  `tela`/`rascunho`. Só a página `web/teste/hoje_ideal.html` usa.
- `historico.js`: o modo "pergunta" e os exports `resumoHistorico`/`icHist`. Só a página `web/teste/historico.html` usa.
- CSS desses modos: `hi-quiz-*`, `hi-opcao*`, `hi-fichas`, `hi-nav` (`hoje_ideal.css`) e `hs-*` de pergunta (`area_historico.css`).
- As classes antigas do quiz (`.quiz*`, `.opcao*`, `.fichas`, `.datas`, `.campo`) saíram de `perguntas.css`; nenhum outro módulo usava.

## Pedidos ao integrador
1. **Servidor sob carga.** `servidor.py` usa `ThreadingHTTPServer` com a fila padrão (5). Com os 5 construtores testando ao mesmo tempo,
   o Edge recebeu `ERR_CONNECTION_REFUSED` em CSS e JS. Os CSS fixos do `roca.html` não têm nova tentativa, e a página fica sem estilo.
   Rode o aceite em série. Com 1 pessoa usando, não acontece. Não mexi no servidor.
2. **LEIA-ME (I5):** `ctx.primario(rotulo?, fn?)` (sem rótulo fica o padrão do passo; um primário por tela, sempre `#avancar`); `ctx.volta`
   (número do passo ou `null`) e `ctx.foco` (`"hoje"|"ha"|"terra"|"baixio"|null`); `data-editar` em qualquer "mudar"; ORDEM `[2,3,4,5,1]`;
   a ficha e o rodapé são da casca.
3. **B, C e D:** troquem os "mudar" que ainda usam `ctx.link(2)` por `data-editar="…"`. O link continua funcionando, mas sem foco e sem
   "Voltar a …". Na última leitura, a frase do Hoje no passo 4 já trazia "mudar".
4. **Folga de Sua roça:** 989 px, para um teto de 1.000. Se entrar mais uma fileira de chips na linha 1 (a pendência de caju, banana e
   cana), ou se `OLHOS.terra` passar de 2 linhas, a tela passa de 1.000. Nesse caso, ponha as culturas extras em "Outra" ou num "+ mais".
5. **Plano (C):** no cenário do Seu Antônio, o passo 3 deu 2.446 px (teto 2.400) na minha medida das 23 h. Pode ter mudado depois.

## Como testei
- `node --check` em roca.js, perguntas.js, area.js, principal.js e rocacerta.js: ok.
- Script CDP próprio (`E:/campeonato-nasa/tmp/fluxo_novo/A/cdp_a.py` + roteiros `r1`–`r9.json`), Edge sem janela a 390×844, com o
  script da seção 8:
  - **Sua roça nos 7 municípios + Piritiba** (`todos.py`): altura 989 px, 93 palavras, 1 primário, 0 contadores, sem rolagem lateral
    (nem com todos os `<details>` abertos), 1 "seu olho", NASA à vista, nenhuma frase proibida, 0 selo < 11 px, 0 summary < 44 px,
    topo 88 px, barra 63 px, linha da terra em 598 px (acima da dobra) e zero erro de console. As 2 falhas de passagem (Caicó e
    Arapiraca, por `ERR_CONNECTION_REFUSED` do servidor) passaram ao repetir; depois da nova tentativa no `roca.js`, Arapiraca passou de primeira.
  - **Critério 1:** sem `#q-prox`/`#hi-prox`/`#hs-prox`, e com as 4 `#linha-*`.
  - **Critério 3 (Seu Antônio):** mandioca + 3 ha + Encharca + Pequeno + Ver deu
    `#/2311306/3?terra=barro&ha=3&baixio=pouco&maniva=plantada&hoje=milho:34,feijao:33,mandioca:33`, e nada mais.
    Com 3 cliques seguidos no verde, houve 1 navegação só.
  - **Critério 4:** só "Ver" deu `#/2311306/3`, sem parâmetros. A ficha mostrou "1,0 ha (típico) · milho e feijão · Mudar" e o passo 4,
    "(o comum daqui)".
  - **Critério 11:** 2 → 3 → 4 pelo verde; `history.back()` foi 4 → 3 → 2, e de 2 saiu da página.
  - **Critério 12:** "Mudar" da ficha no passo 4 abriu Sua roça com `#linha-hoje` na tela (top 133 px) e o verde "Voltar a Quanto rende →".
    Tocar Sorgo e o verde deu `#/2311306/4?hoje=milho:34,feijao:33,sorgo:33`.
  - **Critério 19:** o toque no selo da faixa abriu o balão com a fonte e o fechou em 5 s.
  - **Critério 18:** no passo 5, "Mandar no WhatsApp" chamou o `navigator.share` simulado (texto de 585 caracteres) e o botão voltou a ligar.
  - **Critério 21:** `#/2311306/1` e `#/2311306/3?terra=mista&baixio=terco` abrem; em Sua roça, esse link mostra "Segura a umidade" e
    "Um terço" marcados.
  - **Outras regras do patch:** um `hoje` com `|cons=0|mbx=1` mantém as chaves; `maniva=nao` fica; tirar a mandioca com `maniva=plantada`
    apaga a maniva; marcar e desmarcar não grava nada.
  - **Outras checagens:** "outra medida" → Tarefas → 4 gravou `ha=1.21&area_un=tarefa:4`; o "usar típico" limpou; "seu olho" →
    "o que é?" abre o glossário; passo 1: "←" vai ao 5 e "Ver o meu plano →" vai ao 3; `painel.html?cod=2311306` deu `#plano` =
    `roca.html#/2311306/2`.
- `testes/ferramentas/erros_console.py` em `#/2311306/{2,3,4,5,1}`: nenhum erro.
- Prints em `E:/campeonato-nasa/tmp/fluxo_novo/A/`:
  - Sua roça: `01_suaroca_dobra`, `02_suaroca_inteira`, `03_seu_antonio_marcado`
  - passo 3 e voltar: `04_seu_antonio_passo3_topo`, `05_voltar_para_suaroca`
  - Mudar, selo e links: `06_mudar_do_passo4`, `07_balao_selo`, `08_link_antigo_terco`, `09_abertos_tarefas`
  - computador: `10_desktop_suaroca`, `11_desktop_passo4`, `12_desktop_sem_lugar`
  - outros: `13_index_carga`, `14_passo5_fim`, `15_passo1_topo`, e `m_<cod>_p2` por município
