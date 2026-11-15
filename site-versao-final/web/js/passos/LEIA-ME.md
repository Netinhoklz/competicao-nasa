# Passos da jornada (roca.html)

`roca.js` lê `#/<cod IBGE>/<passo>?respostas`, busca `/api/local?cod=...` (com as respostas que mudam o núcleo) e chama o passo:

```js
// js/passos/<id>.js
export default {
  id: "plantio",              // também a classe .passo-<id> da caixa e o nome do CSS em css/passos/<id>.css
  titulo: "Como plantar",     // aparece no passo a passo e no botão "Próximo"
  render(el, ctx) { el.innerHTML = "..."; /* pode ligar eventos dentro de el; pode ser async */ },
};
```

O passo é redesenhado do zero a cada mudança de resposta ou de passo. Estado de tela que não é resposta (ano escolhido no roçado,
mês do controle deslizante, aba) fica numa variável do módulo.

## ctx

| Campo | O que é |
|---|---|
| `ctx.r` | resposta de `/api/local` (exemplos completos em `site-versao-final/testes/exemplos/local_<cod>.json`) |
| `ctx.r.local` | `{cod, municipio, uf, mesorregiao, lat, lon}` |
| `ctx.r.cardapio[]` | 15 culturas: `{cultura, grupo, papel, aptidao, classe, risco20, risco30, risco40, solo_ciclo, situacao, base, por_solo}` |
| `ctx.r.este_ano` | ONI, `nivel_alerta` (alerta / sinal fraco / sem alerta), `perspectiva` do município, `chuva_recente`, `smap`, `regime`, `inicio`, `zarc_primeiro` |
| `ctx.r.plano` | `{anos: [2027, 2028, 2029], faixas: [{parte: "Parte A"…"Bordas", por_que, anos: [{cultura, tipo, texto}×3]}], principios, interruptor, notas, leguminosa}` |
| `ctx.r.agenda` | calendário de hoje até dez/2027: `linhas[]` (`parte, cultura, tipo, estacao, barras[{de, ate, tipo: preparo/risco/plantio/estimado/roca/colheita/pousio, pista: 1 plantar / 2 na roça e colher, rotulo, segue}], marcos[], plantar, colher, fonte`), `marcos[]` (`data, dia, rotulo, texto`), `agora[]`, `culturas[]`, `solo`, `portoes`, `nota_portoes` |
| `ctx.r.financeiro` | por município: contrato da seção 3 de `analise/financeiro.md` (Milho, Feijão, Mandioca com série 1998–2025 em R$/ha de 2025 e kg/ha, preços, custos CONAB, preços da raiz). Pode ser `null` (dado ainda não gerado ou município sem série): mostre isso com clareza |
| `ctx.r.projecao` | por município: contrato da seção 7 de `analise/projecao.md` (quantis por cultura e ano 2027/2028/2029, chance de quebra, anos parecidos medidos). Pode ser `null` |
| `ctx.r.padroes` | padrões do Censo 2017 (`rocado_ha`, `pct_irrig`, …). Pode ser `null` |
| `ctx.r.el_nino_uf` | manchete do estado: `{definicao, anos, acaso_pct, uf, pct_terco_seco: {ano: %}, media, n_mun}`. Pode ser `null` |
| `ctx.ef` | respostas com os padrões aplicados: `terra` (nao_sei/arenosa/mista/barro), `ha`, `ha_origem`, `baixio` (nao_sei/nao/pouco/terco/metade), `tem_baixio` (true/false/null), `baixio_frac`, `baixio_ha`, `agua` (chuva/cisterna/barreiro/irriga), `vol_m3`, `maniva` (tem/nao/plantada), `criacao`, `prioridade` (garantir/equilibrar/vender/solo), `prioridade_origem`, `gs`, `raiz` (municipio/uf_mediana/uf_p25), `custo` (semente/desembolso) |
| `ctx.entrou` | true quando a pessoa acabou de chegar a este passo (ou mudou de município); false quando só mudou uma resposta |
| `ctx.set(patch)` | muda respostas (chaves de `PADRAO` em roca.js; valores em texto) e redesenha; se a resposta muda o núcleo, busca de novo |
| `ctx.ir(n)` / `ctx.link(n, patch)` | vai ao passo n / devolve o href do passo n |
| `ctx.util` | `js/comum.js`: `esc, num, brl, brlMil, pct, emDez, selo(tipo, fonte), dataBR, mesAno, MESES, tipoCss, ha`, `extra`, `montarExtras` (seção "Extras") |

## Visual e texto (versão 2: para o agricultor, no estilo da tela inicial)

Quem vai usar é o agricultor. O visual segue a tela inicial (o globo do João Pedro): fundo de espaço escuro, manchete fina em dois tons,
rótulos em mono espaçado, painéis escuros com ícone e número grande, e o verde do botão "Montar o plano". Só existe tema escuro.

**Pouco texto:**
1. Cada passo abre com `titulo-passo`: um `kicker` (2–5 palavras, mono) e um `h1` de 1 linha com o `.eco` cinza na 2ª linha
   (ex.: `<h1>Plante em faixas.<span class="eco">A praga anda menos.</span></h1>`). No máximo 1 frase de apoio.
2. Cada bloco tem: rótulo curto + 1 número grande ou 1 desenho + no máximo 1 frase de até ~15 palavras.
3. Fonte, método, tabela, nota e ressalva longa vão para `ctx.util.verMais(html)` ("Ver como calculamos"), fechado.
4. O sentido vem de ícone, cor e forma, não de parágrafo: semáforo (verde/âmbar/terra), grade de 10 roças (`dezRocas`), barras.
5. Frequência natural ("6 em 10"), nunca "0,6" nem "60% de probabilidade". Datas curtas ("11/03 a 20/03").
6. Um selo por bloco (no rótulo), não um por número. Os selos são pequenos e não podem roubar a cena.
7. Nada de jargão na frente: ZARC, GAEZ, IMERG, SMAP, P10/P90, percentil, conforme e R_eff ficam no `verMais`. Na frente, palavras da roça.
8. Ações em botões grandes (≥ 48 px de altura), com ícone.

**Componentes prontos** (`css/quadra.css` + `js/comum.js`):

| Classe ou função | Para quê |
|---|---|
| `.titulo-passo` com `.kicker` e `h1 .eco` | abertura do passo, igual à tela inicial |
| `.painel`, `.painel.destaque` (âmbar), `.painel.verde`, `.painel.alerta` | painéis; os coloridos são para a manchete do bloco |
| `ind({icone, rot, val, un, sub, selo})` e `.grade-2/3/4` | cartão indicador com número grande (igual ao painel do JP) |
| `faixa(icone, "verde" \| "ambar" \| "terra" \| "azul", frase)` | bola colorida + frase forte (manchete) |
| `ic(nome, "" \| "g" \| "gg")`, `icCultura(cultura)` | ícones de traço: milho, feijao, mandioca, palma, vaca, gota, chuva, sol, onda, termo, dinheiro, calendario, escudo, pino, enxada, poco, cisterna, semente, broto, faixas, areia, barro, alerta, ok, relogio, seta… |
| `dezRocas(p, cor)` | grade de 10 quadradinhos pintados |
| `verMais(html, titulo)` | o detalhe técnico escondido |
| `.chip`, `.chip.verde/.ambar/.terra` | pílulas curtas |
| `.botao.primario` (verde), `.botao.secundario`, `.cta` | botões; `.cta` = botão largo de chamada |
| `.numero-grande` | número solto em destaque (Fraunces) |

Tokens: `--bg --surface --surface-2 --surface-3 --ink --ink-2 --muted --ink-4 --border --border-2 --green --green-forte --amber --terra
--blue` (e os `-soft`), `--font` (Inter, manchetes), `--mono` (rótulos), `--display` (Fraunces, números), `--t-<tipo>` e `--f-<tipo>`.

## Regras

- Cada passo só escreve nos próprios arquivos: `js/passos/<id>.js`, `css/passos/<id>.css` e, se precisar, `js/passos/<id>/*.js`.
- Cores e fontes só pelos tokens de `css/quadra.css` (`var(--green)`, `var(--surface)`…). As classes `.t-leguminosa`, `.t-cereal`,
  `.t-tampao`, `.t-forragem`, `.t-perene`, `.t-pousio` definem `--cor` (forte) e `--fundo` (claro) do tipo de cultura. Modo escuro sai dos tokens.
- Gráficos em SVG à mão, sem biblioteca. Um eixo só; legenda quando houver 2 séries ou mais; texto na cor da tinta, não da série.
- Todo número leva `ctx.util.selo("medido" | "suposicao" | "projecao", fonte)`.
- Linguagem do agricultor (frases curtas, "em 7 de 10 anos"), com o detalhe técnico em `<details>`.
- Funciona a 390 px de largura (rolagem horizontal só dentro de um gráfico, nunca da página).

## Extras (js/extras/): blocos prontos dentro dos passos

Cada extra é um módulo `js/extras/<id>.js` com `export default { id, async render(el, ctx, opcoes) }`, que desenha dentro do próprio `<div>`.
O passo põe o div com `U.extra(id, opcoes)` no HTML e, no fim do `render` (que vira `async`), chama `await U.montarExtras(el, ctx)`.

- `montarExtras` importa cada extra uma vez só e pede o CSS dele (`css/extras/<id>.css`) só quando ele aparece; o extra desenha depois que o
  CSS chegou. `voce_decide.css` e `glossario.css` valem na jornada toda e já vêm no `roca.html`.
- Um extra dentro de um `verMais` fechado só é montado quando a pessoa abre (nada é baixado antes).
- Espera no máximo 700 ms: com os dados em cache (redesenho por resposta nova) tudo entra antes de o passo ir para a tela, sem a página pular.
- Se um extra falha, o div some e o passo segue. Pedido recusado pelo servidor (JS ou CSS): tenta de novo uma vez.

**Regra do enxuto:** no máximo 2 blocos visíveis novos por passo; o resto vai para `verMais` ou para um toque. Um "seu olho" por bloco, no máximo.

| Passo | Visível | No "ver mais" (montado ao abrir) |
|---|---|---|
| 1 O lugar | `tendencias` (depois da régua da chuva; no celular, fileira de deslizar), `confianca` (antes do botão das 5 perguntas) | `satelite_chao` (`{painel:false}`, dentro da régua: "O satélite acerta aqui?"), `harmonizacao` (`{naTela:["ndvi","grace"]}`, "De onde vêm os dados"), `glossario` (a lista, "O que quer dizer cada palavra?") |
| 3 Como plantar | `vulnerabilidade` (`{vista:"agua"}`, logo abaixo do roçado; a aba "Geada e calor" tem o "E se esquentar?" hoje/+1 °C/+2 °C, com `dados/calor_cenario.json` baixado só no toque), `saude_solo` (depois das faixas; no celular, fileira de deslizar) | — |
| 4 Quanto rende | `cenarios` ("Outros jeitos de girar o roçado", depois dos blocos do dinheiro; acende o jeito da prioridade do "Seu bolso": garantir → água, vender → renda, solo → solo, equilibrar → plano) | — |
| 5 Segurança | `leve_ao_tecnico` (logo depois dos portões), `cenario_chuva` `{partes:["cenario"], agro}` ("E se chover…", abre na chuva dos anos de El Niño daqui; com `agro`, só "% do normal") | `cenario_chuva` `{partes:["sobreposicao"]}` ("Ver a chuva, o solo e a colheita de cada ano"); no fim, "Ver os 28 anos", "o que não dá para projetar" e "quanto já acertou" (com os 7 jeitos testados) |

**Ponto 16 em toda a jornada** (`js/extras/voce_decide.js`, lista e condições em `integracao/voce_decide.md`):
- a frase fixa "O QUADRA ajuda. Quem decide é você, com o técnico." está na barra de baixo do `roca.html` e é um link: leva ao
  "Leve para o técnico" do passo 5 (`roca.js`); a mesma frase está no cartão do lugar do globo (`index.html`) e embaixo do botão do
  plano no painel (`painel.html`);
- o 1º "seu olho" à vista de cada passo vira "o que é?" (termo `seu_olho` do glossário; `roca.js`, `explicarOlho`): no toque não há title;
- `olho(OLHOS.<chave>)` ("seu olho") entra no texto do passo: El Niño (com o mês em que a estação daqui começa), litoral leste, cultura sem
  zoneamento, terra, baixio, tarefa, irrigação, faixas, metade guardada, vizinhos, preço da raiz, lavoura grande (no passo 4 sempre, no
  herói; no passo 5, com o aviso de lavoura grande, quando o IBGE daqui passa de 2× a roça de família da CONAB), anos de El Niño e portões
  (onde os portões não valem, a manchete não dá data e o selo é SUPOSIÇÃO). Todo passo tem pelo menos 1;
- `confianca` no passo 1 e `leve_ao_tecnico` no passo 5.

**Glossário** (`js/extras/glossario.js`): `roca.js` chama `instalar(ctx)` a cada passo; o texto usa `termo(chave, "palavra")` só na 1ª
aparição de cada passo, nunca dentro de `<button>`, `<a>`, `<summary>` ou de `ind({rot})`. Ligados hoje: `el_nino`, `em_dez`, `umidade_solo`,
`zarc` (passo 1), `em_dez` (passos 4 e 5), `evapotranspiracao` e `ndvi` (cartões das tendências), `geada`, `veranico` e
`balanco_hidrico` (vulnerabilidade) e `seu_olho` (o 1º "seu olho" de cada passo).

O mapa do globo tem as próprias camadas (`js/globo/camadas.js`, ligado em `js/globo/mapa.js`), fora da jornada: Foto, Milho, Chuva,
Solo (mês a mês desde 2015), Calor (2000–2025, NASA POWER) e Água guardada (2002–2026, GRACE por mesorregião), as três com controle de
tempo e "tocar", e Confiança. Calor e Água vêm de `dados/camadas_tempo.json` (`ferramentas/preparar_camadas_tempo.py`, ~90 KB, baixado só
quando uma das duas abas abre).
