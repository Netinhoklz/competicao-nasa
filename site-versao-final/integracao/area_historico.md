# Módulos "área" e "histórico" (pedidos do José, 14/11)

> "Acrescentar opção por hectare ou tamanho do terreno."
> "Saber o que ele já plantou anteriormente no solo, entender melhor o que ele já faz e entender as suas experiências."

## Arquivos (só estes; nada nos passos, roca.js, roca.html, comum.js ou quadra.css)

| Arquivo | O que é |
|---|---|
| `web/js/extras/area.js` | `export default { id: "area", render(el, ctx, opcoes) }` e `haDe`, `lerArea`, `escreverArea`, `tarefaPadrao`, `TAREFAS`, `PASSO_M` |
| `web/js/extras/historico.js` | `export default { id: "historico", render(el, ctx, opcoes) }` (modos `pergunta`, `cartao`, `memoria`) e `lerHistorico`, `recomendacoes`, `memorias`, `resumoHistorico`, `icHist`, `lerAntes`/`escreverAntes`, `lerExp`/`escreverExp` |
| `web/css/extras/area_historico.css` | estilo dos dois, todo dentro de `.ar` e `.hs` (só tokens de `quadra.css`) |
| `web/teste/area.html` | `http://127.0.0.1:8090/teste/area.html?cod=2311306` (`&area_un=tarefa:4`, `&area_un=medida:100x50`, `&ha=2`) |
| `web/teste/historico.html` | `http://127.0.0.1:8090/teste/historico.html?cod=2311306` (`&modo=pergunta\|cartao\|memoria`, `&antes=`, `&exp=`, `&hoje=`, `&tela=0..3`, `&maniva=`) |

Importam, sem editar: `extras/hoje_ideal.js` (`lerHoje`) e `extras/voce_decide.js` (`olho`). Usam `ctx.util` (comum.js) para o resto.

## O que o integrador faz

1. **`roca.js`: `PADRAO` ganha `area_un: "", antes: "", exp: ""`.** Sem isso o `lerHash` descarta as chaves (ele só lê o que está no
   `PADRAO`). Nenhuma das três vai para a API (`paramsApi` não precisa mudar). O `efetivas()` continua lendo só `resp.ha`.
2. **`roca.html`: `<link rel="stylesheet" href="css/extras/area_historico.css">`** (o `cssExtra` do comum.js só carrega CSS com o nome
   do extra; aqui um arquivo serve aos dois). Os dois módulos também funcionam por `extra("historico", { modo: "cartao" })` +
   `montarExtras`, porque o contrato é o mesmo `render(div, ctx, opcoes)`.
3. **Passo 2, tamanho do roçado** (`perguntas.js`): trocar o corpo da pergunta `ha` (`telaArea`) pelo módulo. O título do quiz fica.
   ```js
   import AREA from "../extras/area.js";
   // no lugar de ${telaArea(ctx, U)}: <div class="area-slot"></div>, e depois do innerHTML:
   AREA.render(el.querySelector(".area-slot"), ctx, { semTitulo: true });
   ```
   Os ouvintes `.area-rapido .chip` e `.area-mais` do `perguntas.js` deixam de existir (o módulo liga os dele). O `olho(OLHOS.tarefa)`
   já sai de dentro do módulo, só na aba "Tarefas" (texto: "A tarefa muda de lugar para lugar: confirme com o técnico.").
4. **Passo 2, histórico: 3 telas logo depois do "Como você planta hoje?"** (mesmo padrão do `hoje_ideal.md`, item 3):
   ```js
   import HIST from "../extras/historico.js";
   let fase = "hoje"; // "hoje" → "historico" → perguntas 0..4; ao chegar (ctx.entrou && !ctx.zerou): fase = "hoje"
   if (fase === "hoje") return HI.render(el, ctx, { modo: "pergunta", aoTerminar: () => { fase = "historico"; this.render(el, ctx); } });
   if (fase === "historico") return HIST.render(el, ctx, { modo: "pergunta",
     aoVoltar: () => { fase = "hoje"; this.render(el, ctx); },               // "Anterior" da 1ª tela volta ao jeito de hoje
     aoTerminar: () => { fase = "perguntas"; q = 0; this.render(el, ctx); } });
   ```
   O módulo zera a tela quando `ctx.entrou` é true (uma vez por ctx) e grava com `ctx.set({ antes, exp })` ao sair de cada tela
   ("Próxima", "Anterior", "Não sei / pular"), não a cada toque. `opcoes.tela` força a tela inicial. Sem `aoTerminar`, mostra
   "Anotado." com fichas que voltam à tela de cada uma (e `opcoes.linkSeguir`, se vier). O resumo do passo 2 pode ganhar as fichas
   com `resumoHistorico(lerHistorico(ctx.resp, ctx.r.padroes), U)` (`[ícone, texto, tela]`; desenhe o ícone com `icHist(U, nome)`,
   porque alguns não estão no comum.js).
5. **Passo 3, perto do roçado visto de cima** (`plantio.js`): o cartão "Por onde começar o seu giro".
   ```js
   HIST.render(div, ctx, { modo: "cartao", linkPergunta: ctx.link(2) });   // síncrono; div só para ele
   ```
   Sem histórico, ele mostra "Conte o que você plantou em 2025 e 2026" com o botão "Contar" (`linkPergunta`).
6. **Passo 5 (ou 1), memória** (`seguranca.js`): "A sua memória e os dados", perto do `olho(OLHOS.memoria)` (pode substituí-lo: o
   módulo desenha o próprio olho).
   ```js
   HIST.render(div, ctx, { modo: "memoria", linkPergunta: ctx.link(2) });
   ```

## Formatos (texto compacto na URL, como o `hoje`)

Testado no node: `URLSearchParams` codifica `: , | = x .`, o `decodeURIComponent` do hash devolve, e a leitura corta só no 1º `=`.
Os textos não usam `+`, `&`, `%`, `#` nem espaço (o `+` viraria espaço na leitura do roca.js).

### `ctx.resp.ha` e `ctx.resp.area_un`

- `ha`: hectares com ponto e até 2 casas (`"1.21"`), o que o `efetivas()` já lê. Mínimo `0.01`.
- `area_un`: o que a pessoa digitou, para reabrir na mesma unidade. Só serve à tela; a conta usa `ha`.

| `area_un` | Quer dizer | ha |
|---|---|---|
| `""` | hectares (padrão; também quando ela usa os botões de ha) | o próprio `ha` |
| `tarefa:4` | 4 tarefas do tamanho padrão do estado | 4 × 3.025 m² = 1,21 (BA: 4 × 4.356 m² = 1,74) |
| `tarefa:4:4356` | 4 tarefas de 4.356 m² (ela escolheu o outro tamanho) | 1,74 |
| `medida:100x50` | comprimento × largura em metros | 0,5 |
| `medida:125x60:passos` | em passos (1 passo ≈ 0,8 m) | 125 × 60 × 0,64 = 0,48 |

`haDe(area_un, uf)` devolve os hectares (ou `null` para hectares e texto inválido). Se o `area_un` não bate com o `ha` (diferença
> 2%, por exemplo porque o `ha` mudou por outro caminho), o módulo reabre em hectares.

**Tarefa** (selo SUPOSIÇÃO + "confirme com o técnico"): fonte IBGE (1948), *Unidades agrárias não decimais em uso no Brasil*
(inquérito nas prefeituras, 2ª tiragem; https://biblioteca.ibge.gov.br/visualizacao/livros/liv82398.pdf). A tarefa de 25 × 25
braças (0,3025 ha; braça = 2,20 m; 55 × 55 m) é usada em todos os estados do Nordeste (no RN "mil-covas", no MA "linha"). Na Bahia
predomina a "tarefa baiana" de 30 × 30 braças (0,4356 ha; 66 × 66 m), que também aparece no Sertão de PE, em municípios da PB e, no
CE, com o nome de "cem-passos". Por isso o padrão é 3.025 m² (BA: 4.356 m²) e a outra fica a um toque. O documento é antigo: o selo
continua SUPOSIÇÃO.

### `ctx.resp.antes` (o que plantou)

```
2026:milho,feijao|2025:milho
```
Anos separados por `|`, culturas por `,`: `milho, feijao, mandioca, sorgo, palma, algodao, pousio, outra` (`pousio` = "nada", sozinho).
Ano sem resposta = ausente. `""` = não respondeu. Os anos perguntados são o 1º ano do plano − 1 e − 2 (2026 e 2025).

### `ctx.resp.exp` (experiência)

```
bem=feijao|quebra=milho:2024:seca,feijao::praga|faz=naoqueima,palha,faixas,semente,esterco|roca=enxada
```

| Parte | Valores | Sem a parte |
|---|---|---|
| `bem` | culturas que deram bem | não disse |
| `quebra` | `cultura:ano:motivo`, ano e motivo opcionais (`milho`, `milho:2024`, `feijao::praga`); motivos `seca, chuva` (chuva demais), `praga, preco, outro` | não disse |
| `faz` | práticas: `naoqueima, palha` (deixa a palhada), `faixas, semente` (guarda), `esterco` | não marcou (não quer dizer "não faz") |
| `roca` | como prepara a terra: `trator, animal, enxada` | não disse |

### Sem conflito com o `ctx.resp.hoje` (sem perguntar duas vezes)

- O histórico **nunca escreve** em `hoje`.
- Tela 1: se `antes` está vazio e o `hoje` foi informado, 2026 já vem marcado com as culturas do jeito de hoje (chip "do seu jeito de
  hoje"); ela confirma ou muda.
- Tela 3: "Não queimo" e "Guardo semente" só aparecem se o texto do `hoje` **não tem** `queima=` / `sem=`; se tem, viram a linha
  "Já anotado no seu jeito de hoje: …". Quando a pergunta sai no histórico, vai para `exp` como `naoqueima` / `semente`.
- `lerHistorico(resp)` junta os dois: `queima` e `sem` vêm do `hoje` quando ele respondeu, senão do `exp` (`origem` diz de onde).

## `lerHistorico(ctx.resp, ctx.r.padroes)` → objeto (para o hoje_ideal e o plano)

```js
{ anos: {2026: ["milho"], 2025: ["milho"]}, bem: [], quebras: [{c: "milho", ano: 2024, mot: "seca"}], faz: [], roca: null,
  queima: null, sem: null, origem: {queima: null, sem: null}, ultimo: 2026, penultimo: 2025,
  repetiu: ["milho"], capimRepetiu: true, mandioca: false, informado: true }
```
`capimRepetiu` = milho ou sorgo nos dois anos (o sorgo não quebra a lagarta: nota do plano). `mandioca` = mandioca no último ano ou
no jeito de hoje.

**Como o hoje_ideal pode usar (sugestão, sem editar agora):** em `comparar()`, `if (h.queima == null) h.queima = H.queima` (o alerta
do fogo passa a valer quando a resposta veio do histórico); alerta "milho repetido" quando `H.capimRepetiu`; o ajuste "reserva de
mandioca" pode dizer "você já tem" quando `H.mandioca`.
**Como o plano pode usar:** `recomendacoes(r, ef, H)` (sem DOM) já devolve as frases do cartão; quando `H.mandioca` e
`ef.maniva !== "plantada"`, o cartão oferece "Já está plantada: avisar o plano" (`ctx.set({ maniva: "plantada" })`, que muda o núcleo).
O desenho do roçado (passo 3) pode pôr a Parte B onde estava o milho repetido; hoje o núcleo não recebe o histórico.

## O que aparece em Quixadá (3 ha, 1 de baixio; exemplo `antes=2026:milho|2025:milho`, `exp=quebra=milho:2024:seca`)

- **Área**: abre em hectares com o típico daqui (1,03 ha, Censo 2017; "≈ 3,4 tarefas · 1½ campos de futebol"). Tarefas: 4 tarefas de
  55 × 55 m = 1,21 ha (a baiana, 66 × 66 m, a um toque). Medida: 100 × 50 m = 0,5 ha, com o retângulo; em passos, 125 × 60 = 0,48 ha.
  Arapiraca abre em 0,44 ha; Barreiras (BA) abre a tarefa em 66 × 66 m (2,62 ha = 6 tarefas).
- **Cartão**: "A terra repetiu milho: comece com o feijão-caupi nesse lugar." (Parte B do plano; "Milho atrás de milho junta lagarta
  e cansa a terra.") e "O milho quebrou na seca: no plano ele fica no baixio.", com o olho "Você conhece a sua terra: se não bater,
  vale a sua experiência." Com mandioca em 2026 entra "A Parte A já começa com a sua mandioca." (Arapiraca: "O plano daqui não usa
  mandioca."); com `queima=1`, "Deixe a palhada: nada de fogo." Até 3, nesta ordem: repetiu, mandioca, fogo, baixio, faixas.
- **Memória**: "Você lembra: milho quebrou em 2024 (seca). O IBGE anotou 3,8 sacos/ha em Quixadá (normal 8,2). 46% do normal. Bate:
  o município todo quebrou nesse ano." Em Arapiraca o mesmo ano deu 161% do normal: "Aqui o dado não mostra quebra: a sua roça pode
  ser diferente da média. Vale a sua experiência." Em Barreiras, além disso, "Aqui o IBGE mistura lavoura grande" (mediana > 2× a
  familiar da CONAB, o critério do passo 4). Sem ano: os 3 piores anos daqui viram botões "foi em 2012". 2026: "o IBGE ainda não
  publicou". Sorgo, palma, algodão e outra: "o IBGE daqui não tem a série".

## Pendências

- Não testado dentro do `roca.html` (só nas páginas de teste, com o ctx mínimo do LEIA-ME): conferir depois de integrar, em especial o
  `fase` do passo 2 e o "Anterior" voltando ao jeito de hoje.
- O tamanho da tarefa vem de um inquérito de 1948; não achei tabela recente por estado. O passo (0,8 m) é suposição.
- O histórico ainda não muda o núcleo: a ordem A/B/C do plano não troca de lugar com o milho repetido, e a quebra que ele lembra não
  entra na projeção. Só a mandioca já plantada (pelo botão do cartão) muda a API.
- Memória: a régua (quebra < 50% do normal, caiu 50–80%) é a do passo 4, não do IBGE; "preço ruim" não tem dado (o R$/ha da série usa
  preço fixo), então o módulo só diz se a colheita do município foi normal.
