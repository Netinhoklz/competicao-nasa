# Passos da jornada (roca.html)

`roca.js` lê `#/<cod IBGE>/<passo>?respostas`, busca `/api/local?cod=...` (com as respostas que mudam o núcleo) e chama o passo:

```js
// js/passos/<id>.js
export default {
  id: "plantio",              // também a classe .passo-<id> da caixa e o nome do CSS em css/passos/<id>.css
  titulo: "Como plantar",     // nome interno; o da pílula e o do botão verde estão em PASSOS (roca.js)
  css: true,                  // opcional: a casca carrega css/passos/<id>.css antes do 1º desenho (para um passo novo cujo CSS
                              // não está no roca.html; os de Sua roça, Plano e Dinheiro já estão)
  render(el, ctx) { el.innerHTML = "..."; /* pode ligar eventos dentro de el; pode ser async */ },
};
```

O passo é redesenhado do zero a cada mudança de resposta ou de passo. Estado de tela que não é resposta (ano escolhido no roçado,
mês do controle deslizante, aba) fica numa variável do módulo.

## O fluxo (rodada 2: analise/fluxo2/BRIEFING.md, D1–D8)

- **Ordem da jornada: `ORDEM = [2, 3, 4, 5]`**: Sua roça (`#/<cod>/2`) → O plano (`/3`) → Quanto rende (`/4`) → Relatório (`/5`).
  O globo e o painel entram direto em `#/<cod>/2`; sem número de passo, `#/<cod>` também cai no 2.
- **Saíram da jornada:** "Se secar" (`seguranca.js` fica no disco, sem rota; o CSS dele saiu do roca.html) e "Do espaço" (`lugar.js`,
  foi para o painel e o mapa, D6). **Links antigos:** `#/<cod>/1?…` vira `#/<cod>/2?…` com as mesmas respostas (a mesma entrada do
  histórico, sem passo a mais); `#/<cod>/5?…` abre o Relatório. Não há mais `data-ir="1"`, `ctx.link(1)` nem `data-acerto`.
- **Um indicador de progresso:** as pílulas do topo (computador: Sua roça · O plano · Quanto rende · Relatório; celular, `curto`:
  Roça · Plano · Dinheiro · Relatório), sem número; a atual acesa e as anteriores com ✓. Nenhum "n de m" e nenhuma barra de progresso
  dentro do passo.
- **Um botão primário (verde) por tela: sempre o `#avancar` da barra de baixo**, com o nome do destino: Sua roça "Ver o meu plano →"
  (ou "Voltar a <passo> →" para quem veio de um "mudar": "Voltar ao plano →", "Voltar a Quanto rende →", "Voltar ao relatório →");
  Plano "Quanto rende →"; Dinheiro "Ver o relatório →"; Relatório "Mandar no WhatsApp". Dentro do passo tudo é `.botao.secundario`,
  chip ou link. O verde se desliga no 1º toque até a tela mudar (se a tela não muda, como no WhatsApp, volta a ligar em 0,8 s), e um
  2º toque até 700 ms depois do 1º é ignorado. Se a API falha, `roca.js` tenta de novo sozinho uma vez (1,5 s); depois mostra "Sem
  sinal para carregar agora…" e o verde vira "Tentar de novo".
- **O verde do Relatório:** `relatorio.js` chama `ctx.primario("Mandar no WhatsApp", fn)` no `render` (pode ser `async`; a casca liga o
  botão depois do desenho, e um `ctx.primario` chamado mais tarde, depois de um `await`, também vale). Sem isso, o padrão da casca é
  `compartilhar(ctx)` de `extras/leve_ao_tecnico.js`. O "Imprimir / salvar PDF" é um `.botao.secundario` do passo com `window.print()`.
- **Nada avança sozinho.** Um toque numa resposta só redesenha (Sua roça: só o rascunho da tela, sem URL e sem API). O rascunho é
  gravado pelo verde e também quando a pessoa sai de Sua roça por uma pílula ou pelo rodapé (`ctx.pendente`, de `perguntas.js`).
- **Histórico:** ir de um passo a outro (`ctx.ir`, `ctx.link`, pílulas, verde) entra no histórico (`location.hash =`); responder
  (`ctx.set`) troca no lugar (`location.replace`). O voltar do Android recua um passo; no passo 2, "← Mapa" volta ao globo, e quem
  chegou por um "mudar" vê "←", que volta ao passo de onde saiu sem gravar o rascunho (`history.back()`).
- **Padrão ≠ resposta:** só o que a pessoa tocou vai para a URL. O resto aparece como "típico daqui", "o comum daqui" ou "não sei"
  (selo SUPOSIÇÃO) e vira pergunta ao técnico.
- **Sem nova chamada à API:** só `terra`, `baixio` e `maniva` vão para `/api/local` (`paramsApi` de `roca.js`). Trocar `prioridade` ou
  `plano` com `ctx.set` redesenha o passo com o JSON que já está em cache (dezenas de ms).
- **"Mudar":** qualquer elemento com `data-editar="<linha>"` (de preferência um `<a href="${ctx.link(2)}">`, que funciona sem JS) abre
  Sua roça com a linha `#linha-<linha>` em foco e o verde "Voltar a <passo> →". Linhas de Sua roça: `hoje`, `ha`, `terra`, `baixio` e,
  nesta rodada, `maniva` e `antes` (que saíram do Plano, D2). Recarregar a página esquece a volta (aceito).
- **Da casca (`roca.js`), não do passo:** as pílulas, a ficha em 1 linha dos passos 3–5 ("1 ha (típico) · milho e feijão · Mudar"; com
  as medidas, "40 × 100 m · milho e feijão · Mudar"), o rodapé do ponto 16 (`.passo-fim`: no celular, embaixo de cada passo; no
  computador, na barra) e o balão da fonte do selo (toque ou Enter num `.selo[data-fonte]` mostra a fonte por 5 s). A frase do ponto 16
  leva ao topo do Relatório (o "Leve para o técnico" saiu do Relatório em 15/11; o `compartilhar` dele segue no "Mandar no WhatsApp").
- **Impressão:** `css/quadra.css` tem o `@media print` da casca (folha clara A4, tokens claros, sem topo, ficha, barra de baixo, rodapé
  e balões). O conteúdo do Relatório cuida do dele em `css/passos/relatorio.css` (abrir os "ver mais", quebras de página, ≤ 4 páginas).
- **No node:** `import { PADRAO, efetivas } from "web/js/roca.js"` funciona (sem `document`, o arquivo não liga nada na página).

**Frases banidas na frente** (o script de aceite procura): "5 perguntas", "Só o que muda a conta", "muda o que dá para salvar",
"acima do recorde", "qualquer terra" ("uso as datas que servem em qualquer terra", "As datas valem para qualquer terra"), "sem preço
aqui", "ainda não vende(m)" (forragem: "vira comida da criação, fora do R$"), "à frente de hoje em" (e "à frente em N de 100"),
"você cabe" sem ressalva. Cultura sem série de R$ no município: diga que o IBGE não tem a série dela aqui, com essas palavras.
Na frente, o El Niño tem um rótulo só, "El Niño forte"; o fato do mar é "o mar mais quente de ago–out desde 1950".

## Respostas (chaves de `PADRAO` em roca.js; valores em texto na URL)

| Chave | Valores | Quem grava | Vai para a API? |
|---|---|---|---|
| `hoje` | `milho:50,feijao:50` (+ `\|...`); chaves de `CULT` em `extras/culturas.js` (as antigas `milho, feijao, mandioca, sorgo, palma, outra` não mudam) | Sua roça | não |
| `ha`, `area_un` | hectares com ponto (`"0.4"`); `area_un` = `""`, `tarefa:4`, `medida:<comp>x<larg>[:passos]` (`extras/area.js`) | Sua roça | não |
| `larg`, `comp` | **novas:** largura e comprimento do roçado, metros inteiros (`"40"`, `"100"`) | Sua roça (B1) | não |
| `terra` | `arenosa` \| `mista` \| `barro` | Sua roça | sim |
| `baixio` | `nao` \| `pouco` \| `terco` \| `metade` | Sua roça | sim |
| `maniva` | `tem` \| `plantada` \| `nao` (agora em Sua roça) | Sua roça | sim |
| `antes` | o que plantou no ano passado nesse chão (formato de `extras/historico.js`; agora em Sua roça) | Sua roça | não |
| `prioridade` | `garantir` (Água) \| `vender` (Renda) \| `solo` \| `equilibrar` (Um pouco de cada = `r.plano`); mapa `INV` de `extras/cenarios.js` | O plano, lado "O ideal" | não |
| `plano` | **nova:** `""` (Seu jeito, melhorado; o padrão) \| `"ideal"` | O plano, controle de 2 lados | não |
| `agua`, `vol`, `criacao`, `gs`, `raiz`, `custo`, `exp` | como na rodada 1 | Dinheiro, Leve para o técnico | não |

## ctx

| Campo | O que é |
|---|---|
| `ctx.r` | resposta de `/api/local` (exemplos completos em `site-versao-final/testes/exemplos/local_<cod>.json`; sem respostas, os 7 municípios + Piritiba em `site-versao-final/testes/exemplos/api/<cod>.json`) |
| `ctx.r.local` | `{cod, municipio, uf, mesorregiao, lat, lon}` |
| `ctx.r.cardapio[]` | 18 culturas: `{cultura, grupo, papel, aptidao, classe, risco20, risco30, risco40, solo_ciclo, situacao, base, por_solo}` |
| `ctx.r.este_ano` | ONI, `nivel_alerta` (alerta / sinal fraco / sem alerta), `perspectiva` do município, `chuva_recente`, `smap`, `regime`, `inicio`, `zarc_primeiro` |
| `ctx.r.plano` | `{anos: [2027, 2028, 2029], faixas: [{parte: "Parte A"…"Bordas", por_que, anos: [{cultura, tipo, texto}×3]}], principios, interruptor, notas, leguminosa}` |
| `ctx.r.agenda` | calendário de hoje até dez/2027: `linhas[]` (`parte, cultura, tipo, estacao, barras[{de, ate, tipo: preparo/risco/plantio/estimado/roca/colheita/pousio, pista: 1 plantar / 2 na roça e colher, rotulo, segue}], marcos[], plantar, colher, fonte`), `marcos[]` (`data, dia, rotulo, texto`), `agora[]`, `culturas[]` (`{cultura, plantar, colher, fonte, situacao}`; 12–13 das 18 do cardápio, as que têm janela aqui), `solo`, `portoes`, `nota_portoes` |
| `ctx.r.financeiro` | por município: contrato da seção 3 de `analise/financeiro.md` (Milho, Feijão, Mandioca com série 1998–2025 em R$/ha de 2025 e kg/ha, preços, custos CONAB, preços da raiz). Pode ser `null` (dado ainda não gerado ou município sem série): mostre isso com clareza |
| `ctx.r.projecao` | por município: contrato da seção 7 de `analise/projecao.md` (quantis por cultura e ano 2027/2028/2029, chance de quebra, anos parecidos medidos). Pode ser `null` |
| `ctx.r.padroes` | padrões do Censo 2017 (`rocado_ha`, `pct_irrig`, …). Pode ser `null` |
| `ctx.r.el_nino_uf` | manchete do estado: `{definicao, anos, acaso_pct, uf, pct_terco_seco: {ano: %}, media, n_mun}`. Pode ser `null` |
| `ctx.ef` | respostas com os padrões aplicados (`efetivas()` de `roca.js`): `larg`, `comp` (metros inteiros, os dois ou nenhum; sem resposta, `null`: o desenho usa o quadrado do `ha` e diz SUPOSIÇÃO; as chaves `larg` e `comp` valem sempre e o `ha` sai delas (5 × 5 m = 0,0025 ha); um link antigo só com `area_un=medida:…` também preenche, e essa medida, se não bater com o `ha` respondido (± 5%), vira `null` e vale o `ha`), `plano` (`"melhor"` \| `"ideal"`), `terra` (nao_sei/arenosa/mista/barro), `ha` (4 casas; com as medidas, larg × comp; senão a resposta; senão o típico do Censo. Para escrever, abaixo de 0,1 ha use m², como o `haTxt` de `terreno.js`: `U.ha` dá "0 ha"), `ha_origem`, `baixio` (nao_sei/nao/pouco/terco/metade), `tem_baixio` (true/false/null), `baixio_frac`, `baixio_ha`, `agua` (chuva/cisterna/barreiro/irriga), `vol_m3`, `maniva` (tem/nao/plantada), `criacao`, `prioridade` (garantir/equilibrar/vender/solo; sem resposta, garantir em ano de alerta de El Niño, senão equilibrar), `prioridade_origem`, `gs`, `raiz` (municipio/uf_mediana/uf_p25), `custo` (semente/desembolso) |
| `ctx.entrou` | true quando a pessoa acabou de chegar a este passo (ou mudou de município); false quando só mudou uma resposta |
| `ctx.set(patch)` | muda respostas (chaves de `PADRAO`; valores em texto) e redesenha, trocando a entrada do histórico no lugar (`location.replace`); se a resposta muda o núcleo, busca de novo |
| `ctx.ir(n)` / `ctx.link(n, patch)` | vai ao passo n (2–5; entra no histórico) / devolve o href do passo n |
| `ctx.primario(rotulo?, fn?)` | troca o rótulo e/ou a ação do botão verde da barra (`#avancar`) desta tela; sem rótulo, fica o padrão do passo (`PASSOS[].primario`). É refeito a cada desenho |
| `ctx.volta` | número do passo de onde a pessoa veio por um "mudar" (`data-editar`), ou `null`. Só vale em Sua roça |
| `ctx.foco` | a linha de Sua roça que o "mudar" pediu (`"hoje"`, `"ha"`, `"terra"`, `"baixio"`, `"maniva"`, `"antes"`) ou `null` |
| `ctx.pendente()` | (posto por `perguntas.js`) o rascunho de Sua roça ainda não gravado; a casca leva junto ao sair por pílula ou rodapé |
| `ctx.util` | `js/comum.js`: `esc, num, brl, brlMil, pct, emDez, selo(tipo, fonte), fonteCurta, dataBR, mesAno, MESES, tipoCss, ha`, `extra`, `montarExtras` (seção "Extras") |

## Contratos novos da rodada 2 (detalhe em analise/fluxo2/BRIEFING.md, seções 4–6)

| Arquivo | Dono | O que dá |
|---|---|---|
| `js/extras/culturas.js` | B1 | `CULT` (`{ nome, serie?, icone, t, semRs?, motor }`, `motor` = nome no cardápio do núcleo, `"outra"` → `null`) e `opcoesCultura(r)`; `hoje_ideal.js` reexporta os dois |
| `js/extras/ideal.js` | A2 | sem DOM (roda no node): `planoMelhor(r, resp, ef)`, `planoIdeal(r, resp, ef, prioridade)` (formato de `r.plano`), `beneficios(r, resp, ef, plano, tipo)` (`itens[{id, rotulo, valor, unidade, selo, fonte}]`, `valor: null` = não medido), `comparar3(r, resp, ef, prioridade)`, `agendaDe(r, plano, ef)` (formato de `r.agenda.linhas`), `agendaLonga(r, plano)` (o mesmo formato até dez/2029, para o mês a mês do Plano: 2028 e 2029 repetem as datas do ZARC 2026/27), `escolhido(r, resp, ef)` (`{tipo, prioridade, plano, linhas}`: o que Plano, Dinheiro e Relatório mostram, pela chave `plano` e `prioridade`) |
| `js/extras/terreno.js` (+ `css/extras/terreno.css`) | C1 | `export default { render(el, ctx, { plano, ano }) }`: o terreno larg × comp em escala, os metros de cada faixa, o espaçamento e o zoom de 5 m × 5 m |
| `dados/agronomia.json` | A1 | espaçamento de sequeiro das 18 culturas (`entre_linhas_m, entre_covas_m, por_cova, plantas_ha, semente_kg_ha, material, material_unidade, profundidade_cm, ciclo_dias, como[], fonte`), `operacoes` (preparo sem fogo, capina, cobertura, colheita, guardar semente, adubação verde) e `beneficios` (N, palhada, forragem), tudo com fonte |
| `js/passos/relatorio.js` (+ `css/passos/relatorio.css`, com `css: true`) | C4 | o passo 5 (D7) |

## Visual e texto (versão 2: para o agricultor, no estilo da tela inicial)

Quem vai usar é o agricultor. O visual segue a tela inicial (o globo do João Pedro): fundo de espaço escuro, manchete fina em dois tons,
rótulos em mono espaçado, painéis escuros com ícone e número grande, e o verde do botão "Montar o plano". Só existe tema escuro (a
impressão é clara).

**Pouco texto:**
1. Cada passo abre com `titulo-passo`: um `kicker` (2–5 palavras, mono) e um `h1` de 1 linha com o `.eco` cinza na 2ª linha
   (ex.: `<h1>Plante em faixas.<span class="eco">A praga anda menos.</span></h1>`). No máximo 1 frase de apoio.
2. Cada bloco tem: rótulo curto + 1 número grande ou 1 desenho + no máximo 1 frase de até ~15 palavras.
3. Fonte, método, tabela, nota e ressalva longa vão para `ctx.util.verMais(html)` ("Ver como calculamos"), fechado.
4. O sentido vem de ícone, cor e forma, não de parágrafo: semáforo (verde/âmbar/terra), grade de 10 roças (`dezRocas`), barras.
5. Frequência natural ("6 em 10"), nunca "0,6" nem "60% de probabilidade". Datas curtas ("11/03 a 20/03"); no Relatório, datas exatas
   (dd/mm/aaaa) à esquerda.
6. Um selo por bloco (no rótulo), não um por número. Os selos são pequenos (11 px, sem quebrar) e não podem roubar a cena.
   O rótulo diz a fonte: `selo("medido", fonte)` vira "MEDIDO · NASA SMAP" pela 1ª missão da NASA que aparece no texto da fonte
   (SMAP, GPM/IMERG, POWER, GRACE, MODIS, VIIRS, ECOSTRESS, NASADEM; 3 ou mais = "NASA"); sem NASA, a 1ª entre NOAA (ONI), ZARC,
   CONAB, IBGE (PAM, Censo) e FAO (GAEZ). SUPOSIÇÃO fica sem fonte curta. Com fonte, o selo ganha `data-fonte` e `tabindex="0"`.
7. Nada de jargão na frente: ZARC, GAEZ, IMERG, SMAP, P10/P90, percentil, conforme e R_eff ficam no `verMais`. Na frente, palavras da
   roça (roçado, baixio, maniva, tarefa, cova, carreira), número com unidade.
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
Na impressão os mesmos tokens viram claros (`@media print` de `quadra.css`): use os tokens e a folha sai legível sem CSS extra.

## Regras

- Cada passo só escreve nos próprios arquivos: `js/passos/<id>.js`, `css/passos/<id>.css` e, se precisar, `js/passos/<id>/*.js`.
- Cores e fontes só pelos tokens de `css/quadra.css` (`var(--green)`, `var(--surface)`…). As classes `.t-leguminosa`, `.t-cereal`,
  `.t-tampao`, `.t-forragem`, `.t-perene`, `.t-pousio` definem `--cor` (forte) e `--fundo` (claro) do tipo de cultura. Modo escuro sai dos tokens.
- Gráficos em SVG à mão, sem biblioteca. Um eixo só; legenda quando houver 2 séries ou mais; texto na cor da tinta, não da série.
- Todo número leva `ctx.util.selo("medido" | "suposicao" | "projecao", fonte)`.
- Linguagem do agricultor (frases curtas, "em 7 de 10 anos"), com o detalhe técnico em `<details>`.
- Funciona a 390 px de largura (rolagem horizontal só dentro de um gráfico, nunca da página), também com todo "ver mais" aberto.
- Alvos de toque ≥ 44 px (todo `summary` também); o `.eco` usa `--ink-3` (contraste ≥ 4,5:1).

**Limites a 390 px, com todo "ver mais" fechado** (rodada 2; `testes/ferramentas/aceite_fluxo.py` confere nos 7 municípios; palavras =
`#jornada.innerText` à vista):

| Tela | Altura máx. | Palavras (teto) | Outro |
|---|---|---|---|
| Sua roça (2) | 1.800 px | 190 | o caminho de 1 toque continua valendo (tudo tem padrão); "em metros" à vista, não escondido (D2) |
| O plano (3) | 3.600 px | 430 | abre em "Seu jeito, melhorado"; o controle [Seu jeito melhorado \| O ideal] grande; "O que vale mais para você?" dentro do lado "O ideal" (D3) |
| Quanto rende (4) | 2.600 px | 300 | Hoje → Melhorado → Ideal com os números de `extras/ideal.js`; sem as abas de prioridade (D5) |
| Relatório (5) | sem teto | sem teto | escaneável: datas exatas à esquerda, 1 linha de "o quê" e o "como" curto; impressão A4 em ≤ 4 páginas (D7) |

Topo fixo ≤ 96 px e barra de baixo ≤ 64 px. No máximo 2 "seu olho" à vista por tela. Para conferir depois de mexer:
`testes/ferramentas/aceite_fluxo.py` (parte 0: os testes do node; parte 1: a tabela por tela e município; parte 2: os toques; parte 3:
o painel; parte 4: `percorrer_fluxo.py`, com o globo, o "Seu Antônio", 40 × 100 m e o ideal com Água, e o PDF do Relatório). Os testes
do node rodam sozinhos também: `node testes/ferramentas/teste_ideal.mjs`, `teste_dinheiro.mjs`, `teste_relatorio.mjs` e
`teste_calculo.mjs` (os JSON da API sem respostas estão em `testes/exemplos/api/`; 4 respostas reais de Quixadá em
`testes/exemplos/api_respostas/`).

## Extras (js/extras/): blocos prontos dentro dos passos

Cada extra é um módulo `js/extras/<id>.js` com `export default { id, async render(el, ctx, opcoes) }`, que desenha dentro do próprio `<div>`.
O passo põe o div com `U.extra(id, opcoes)` no HTML e, no fim do `render` (que vira `async`), chama `await U.montarExtras(el, ctx)`.

- `montarExtras` importa cada extra uma vez só e pede o CSS dele (`css/extras/<id>.css`) só quando ele aparece (lista `CSS_PROPRIO` de
  `comum.js`); o extra desenha depois que o CSS chegou. `voce_decide.css`, `glossario.css`, `hoje_ideal.css` e `area_historico.css`
  valem na jornada toda e já vêm no `roca.html`. Um extra novo com CSS entra no `CSS_PROPRIO` ou pede o próprio CSS no `render` (`terreno.js` faz assim com `css/extras/terreno.css`).
- Um extra dentro de um `verMais` fechado só é montado quando a pessoa abre (nada é baixado antes).
- Espera no máximo 700 ms: com os dados em cache (redesenho por resposta nova) tudo entra antes de o passo ir para a tela, sem a página pular.
- Se um extra falha, o div some e o passo segue. Pedido recusado pelo servidor (JS ou CSS): tenta de novo uma vez.

**Regra do enxuto:** no máximo 2 blocos visíveis novos por passo; o resto vai para `verMais` ou para um toque. Um "seu olho" por bloco e
2 por tela, no máximo.

O que cada tela mostra nesta rodada (alvo; o detalhe está nas decisões D2–D7 do briefing):

| Passo | Visível | Num toque ou no "ver mais" |
|---|---|---|
| 2 Sua roça | as 6 linhas `#linha-hoje`, `#linha-ha`, `#linha-terra`, `#linha-baixio`, `#linha-maniva` (só quando a mandioca está no jeito dele, no plano daqui ou já respondida) e `#linha-antes`, cada uma num cartão numerado (número, ícone e pergunta curta numa linha, no mesmo eixo; a ajuda curta embaixo da pergunta, no mesmo recuo; as opções de uma fileira com a mesma largura e altura, e a última fileira incompleta enche a largura; na borda de cima a etiqueta "comum daqui" enquanto é o padrão, ou ✓ quando respondida; a resposta marcada ganha ✓ no canto): 1 "O que você planta?" (as comuns daqui + a barra "Ver todas as culturas (19)": as 18 do cardápio + "Outra", por grupos, escolha múltipla; cultura fora do zoneamento ganha 1 linha de aviso com selo, "Fora do indicado aqui: banana."), 2 "Qual o tamanho?" ("= X ≈ N tarefas" embaixo da pergunta, em `.sr-m-conv` (m² abaixo de 0,1 ha; 2 casas abaixo de 1 ha), com o selo SUPOSIÇÃO e a etiqueta "típico daqui" sem resposta; chips de ha + "ou em metros" com o desenho do terreno, largura (seta de lado) × "comprimento, morro abaixo" (seta para baixo: o lado do alto até embaixo, como no desenho do Plano)), 3 "Como é a terra?" (Areia / Misturada / Barro com o desenho da textura e as palavras do Vicente embaixo: seca rápido, segura água, encharca; o "?" abre o "seu olho" do torrão), 4 "Tem baixio?" ("A parte mais baixa do roçado, onde a água para." à vista, embaixo da pergunta; cada resposta com o roçado de lado; o "?" abre o desenho de perfil e o "seu olho"), 5 "Tem maniva?" (quem planta mandioca: "A rama, para plantar mais."; quem não planta: "O plano daqui usa mandioca.", sem "Já plantada"; respostas com o desenho da rama), 6 "E no ano passado?" ("Em 2025, nesse chão."), a faixa de 1 linha do El Niño e do solo | "+ quanto de cada"; "em tarefas ou passos" = `area` com `{ semTitulo: true, abas: ["tarefa", "passos"] }` (passos também gravam `larg` e `comp` em metros) |
| 3 O plano | controle [Seu jeito melhorado \| O ideal] (grava `plano`), "Agora", o roçado larg × comp com o "por quê" curto de cada parte (o efeito da maniva e do ano passado) e os avisos do plano, "O que você ganha" (Hoje → Melhorado → Ideal, de `comparar3`: até 3 ganhos, o que fica pior e 4 dos 8 números); no lado "O ideal", "O que vale mais para você?" (Água · Renda · Solo · Um pouco de cada: o toque grava `prioridade` e também `plano=ideal`) | "Seu terreno em metros" (`terreno`, num "ver mais"), o mês a mês; "Mais 4: comida, gado, chão coberto e lagarta"; "Ver como calculamos"; o calendário completo; "Por que este plano" (`vulnerabilidade`, as faixas, `saude_solo`, que recebem uma cópia do `ctx` com `r.plano` e `r.agenda` do plano à vista) |
| 4 Quanto rende | Hoje → Melhorado → Ideal (`hoje_ideal` modo "comparacao" com `{ c3, escolhido, linkMudar, linkIdeal, ruim, olhoAgro }`; o `comHoje` saiu): o gráfico de 3 anos, uma linha por caminho (a do Ideal diz a prioridade e leva ao Plano com `plano=ideal`), as 3 linhas de R$ do "O que você ganha" (mesmo rótulo, valor, selo e fonte), "Em 8 de 10 anos já vistos aqui…" (`rs.oito_em_dez`) | a grade de 10 roças (`rs.replay`); "Ajustar a conta"; El Niño, "Quando o dinheiro entra", "A colheita paga o gasto?"; "Os 4 jeitos, lado a lado" (`cenarios` com `{ leitura: true }`: só mostra, sem abas e sem gravar; sem opções, o modo antigo com abas ainda grava `prioridade`); "Ver como calculamos" (os 8 números nos 3 caminhos) |
| 5 Relatório | "O plano do seu roçado": cabeçalho (município, data de hoje, larg × comp, terra, baixio, plano e prioridade, cada um com "Mudar"), "O que fazer e quando" (`.rl-tarefa`, datas exatas dd/mm/aaaa de `escolhido().linhas` e `r.agenda.marcos`, de agora a dez/2027; 2028 e 2029 por ano), o desenho pequeno do roçado (`svgTerreno`), "O que juntar para 2027", o fim com "Imprimir / salvar PDF" (`.rl-fim`) e a frase do ponto 16 (só no papel) | o passo a passo de cada tarefa; "Como fazer, cultura por cultura" (seção própria); "Imprimir / salvar PDF" |

**Detalhes de contrato desta rodada:**
- `compartilhar(ctx, { plano, tarefas })` (`extras/leve_ao_tecnico.js`): com o resumo do Relatório, o texto do WhatsApp leva "Plano: …" e
  "Próximas tarefas:" (5 linhas com datas) antes das perguntas; sem `opcoes`, fica como era (o padrão da casca e o "Copiar o texto").
- `css/passos/relatorio.css` põe `@page { margin: 10mm }`: depois que o Relatório abre, essa margem vale também para as outras folhas
  impressas da mesma visita (a do técnico); só a margem muda.
- `terreno.js`: `contas(lay, k, agro, plano)` conta a cerca viva pelo perímetro (gliricídia, uma estaca a cada 5 m), o feijão do
  revezamento a 25 cm (o "como" do caupi no `agronomia.json`) e, sem kg na fonte (milho, mucuna), o número de sementes
  (`unidade: "sementes"`); `svgTerreno(U, lay, k, { W, Hmax, zoom, agro, plano })`. `carregarAgronomia()` tenta de novo uma vez em 400 ms.
- `plantio/calendario.js`: `agendaDoPlano(r.agenda, escolhido(r, resp, ef).linhas)` dá a agenda do plano à vista com o "o que fazer
  agora" refeito; `agora`, `linhaDoTempo`, `calendarioCompleto` e `ligarCalendario` aceitam essa agenda no último argumento.
- Casca: um redesenho por resposta nova (`ctx.entrou` falso) põe `sem-entrada` na caixa do passo, sem a animação de entrada (a tela não pula).

**Ponto 16 em toda a jornada** (`js/extras/voce_decide.js`, lista e condições em `integracao/voce_decide.md`):
- a frase fixa "O QUADRA ajuda. Quem decide é você, com o técnico." é um link ao topo do Relatório (passo 5, `roca.js`): no
  computador fica na barra de baixo (`#moldura`); no celular sai da barra e vira o rodapé de cada passo (`.passo-fim`, `#decide-fim`);
  a mesma frase está no cartão do lugar do globo (`index.html`) e embaixo do botão do plano no painel (`painel.html`);
- o 1º "seu olho" à vista de cada passo vira "o que é?" (termo `seu_olho` do glossário; `roca.js`, `explicarOlho`): no toque não há title;
- `olho(OLHOS.<chave>)` ("seu olho") entra no texto do passo: El Niño, litoral leste, cultura sem zoneamento, terra, baixio, tarefa,
  irrigação, faixas, metade guardada, vizinhos, preço da raiz, lavoura grande, anos de El Niño e portões (onde os portões não valem, a
  abertura não dá data e o selo é SUPOSIÇÃO). Todo passo tem pelo menos 1 à vista e no máximo 2;
- `confianca` vai para o painel (D6) e `leve_ao_tecnico` fica no Relatório.

**Glossário** (`js/extras/glossario.js`): `roca.js` chama `instalar(ctx)` a cada passo (o JSON do município só baixa no 1º balão aberto); o texto usa `termo(chave, "palavra")` só na 1ª
aparição de cada passo, nunca dentro de `<button>`, `<a>`, `<summary>` ou de `ind({rot})`. Ligados: `el_nino`, `em_dez`, `umidade_solo`,
`zarc`, `evapotranspiracao` e `ndvi` (cartões das tendências, agora no painel), `geada`, `veranico` e `balanco_hidrico`
(vulnerabilidade) e `seu_olho` (o 1º "seu olho" de cada passo).

O mapa do globo tem as próprias camadas (`js/globo/camadas.js`, ligado em `js/globo/mapa.js`), fora da jornada: Foto, Milho, Chuva,
Solo (mês a mês desde 2015), Calor (2000–2025, NASA POWER) e Água guardada (2002–2026, GRACE por mesorregião), as três com controle de
tempo e "tocar", e Confiança. Calor e Água vêm de `dados/camadas_tempo.json` (`ferramentas/preparar_camadas_tempo.py`, ~90 KB, baixado só
quando uma das duas abas abre). Nesta rodada, o cartão do município no zoom e o painel (`painel.html`) ganham o que o "Do espaço"
mostrava (D6): o cartão mostra 3 números-chave com selo (`numerosChave(cod)` de `camadas.js`: "Milho em 2027 · quebra 6 em 10", chuva típica, solo agora;
o toque liga a camada), e o painel ganha as abas Solo e clima (`tendencias`), E se chover (`cenario_chuva` cenário + sobreposição) e
Os dados (`confianca`, `glossario`, `satelite_chao`, `harmonizacao`), montadas com `montarExtras` fora da jornada. Quem mudar
`comum.js` (`selo`, `extra`, `montarExtras`) ou o formato dos extras deve reabrir `painel.html?cod=2311306` nessas 3 abas.
