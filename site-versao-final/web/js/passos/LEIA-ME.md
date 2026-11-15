# Passos da jornada (roca.html)

`roca.js` lê `#/<cod IBGE>/<passo>?respostas`, busca `/api/local?cod=...` (com as respostas que mudam o núcleo) e chama o passo:

```js
// js/passos/<id>.js
export default {
  id: "plantio",              // também a classe .passo-<id> da caixa e o nome do CSS em css/passos/<id>.css
  titulo: "Como plantar",     // nome interno; o da pílula e o do botão verde estão em PASSOS (roca.js)
  render(el, ctx) { el.innerHTML = "..."; /* pode ligar eventos dentro de el; pode ser async */ },
};
```

O passo é redesenhado do zero a cada mudança de resposta ou de passo. Estado de tela que não é resposta (ano escolhido no roçado,
mês do controle deslizante, aba) fica numa variável do módulo.

## O fluxo (analise/fluxo/00_FLUXO_FINAL.md)

- **Ordem da jornada: `ORDEM = [2, 3, 4, 5, 1]`** (Sua roça → O plano → Quanto rende → Se secar → Do espaço). As rotas `#/<cod>/1..5`
  não mudam; o globo entra direto em `#/<cod>/2`; sem número de passo, `#/<cod>` também cai no 2. O passo 1 ("Do espaço") fica fora do
  caminho, a 1 toque pela pílula.
- **Um indicador de progresso:** as pílulas do topo (`curto` no celular: Roça · Plano · Dinheiro · Seca · Espaço), sem número; a atual
  acesa e as anteriores com ✓. Nenhum "n de m" e nenhuma barra de progresso dentro do passo (`quiz-barra`, `hi-barra`, `hs-barra` saíram
  da jornada).
- **Um botão primário (verde) por tela: sempre o `#avancar` da barra de baixo**, com o nome do destino (Sua roça "Ver o meu plano →"
  ou "Voltar a <passo> →"; Plano "Quanto rende →"; Dinheiro "E se secar? →"; Se secar "Mandar no WhatsApp"; Do espaço "Ver o meu
  plano →"). Dentro do passo tudo é `.botao.secundario`, chip ou link. O verde se desliga no 1º toque até a tela mudar, e um 2º toque
  até 700 ms depois do 1º é ignorado (com a API em cache a tela nova chega em ~50 ms: sem isso o toque duplo pulava o plano).
  Se a API falha, `roca.js` tenta de novo sozinho uma vez (1,5 s); depois mostra "Sem sinal para carregar agora…" e o verde vira
  "Tentar de novo".
- **Nada avança sozinho.** Um toque numa resposta só redesenha (Sua roça: só o rascunho da tela, sem URL e sem API). O rascunho é
  gravado pelo verde e também quando a pessoa sai de Sua roça por uma pílula ou pelo rodapé (`ctx.pendente`, de `perguntas.js`).
- **Histórico:** ir de um passo a outro (`ctx.ir`, `ctx.link`, pílulas, verde) entra no histórico (`location.hash =`); responder
  (`ctx.set`) troca no lugar (`location.replace`). O voltar do Android recua um passo; no passo 2, "← Mapa" volta ao globo, e quem
  chegou por um "mudar" vê "←", que volta ao passo de onde saiu sem gravar o rascunho (`history.back()`).
- **Padrão ≠ resposta:** só o que a pessoa tocou vai para a URL. O resto aparece como "típico daqui", "o comum daqui" ou "não sei"
  (selo SUPOSIÇÃO) e vira pergunta ao técnico.
- **"Mudar":** qualquer elemento com `data-editar="hoje|ha|terra|baixio"` (de preferência um `<a href="${ctx.link(2)}">`, que funciona
  sem JS) abre Sua roça com a linha `#linha-<k>` em foco e o verde "Voltar a <passo> →". Recarregar a página esquece a volta (aceito).
- **Da casca (`roca.js`), não do passo:** as pílulas, a ficha em 1 linha dos passos 3–5 ("1 ha (típico) · milho e feijão · Mudar"),
  o rodapé do ponto 16 (`.passo-fim`: no celular, embaixo de cada passo; no computador, na barra) e o balão da fonte do selo (toque ou
  Enter num `.selo[data-fonte]` mostra a fonte por 5 s).

**Frases proibidas na frente** (o script de aceite procura): "5 perguntas", "Só o que muda a conta", "muda o que dá para salvar",
"acima do recorde", "qualquer terra" ("uso as datas que servem em qualquer terra", "As datas valem para qualquer terra"), "sem preço
aqui", "ainda não vende(m)" (forragem: "vira comida da criação, fora do R$"), "você cabe" sem ressalva, "à frente (de hoje) em N de 100".
Na frente, o El Niño tem um rótulo só, "El Niño forte"; o fato do mar é "o mar mais quente de ago–out desde 1950".

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
| `ctx.set(patch)` | muda respostas (chaves de `PADRAO` em roca.js; valores em texto) e redesenha, trocando a entrada do histórico no lugar (`location.replace`); se a resposta muda o núcleo, busca de novo |
| `ctx.ir(n)` / `ctx.link(n, patch)` | vai ao passo n (entra no histórico) / devolve o href do passo n |
| `ctx.primario(rotulo?, fn?)` | troca o rótulo e/ou a ação do botão verde da barra (`#avancar`) desta tela; sem rótulo, fica o padrão do passo (`PASSOS[].primario`). É refeito a cada desenho |
| `ctx.volta` | número do passo de onde a pessoa veio por um "mudar" (`data-editar`), ou `null`. Só vale em Sua roça |
| `ctx.foco` | a linha de Sua roça que o "mudar" pediu: `"hoje"`, `"ha"`, `"terra"`, `"baixio"` ou `null` |
| `ctx.util` | `js/comum.js`: `esc, num, brl, brlMil, pct, emDez, selo(tipo, fonte), fonteCurta, dataBR, mesAno, MESES, tipoCss, ha`, `extra`, `montarExtras` (seção "Extras") |

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
6. Um selo por bloco (no rótulo), não um por número. Os selos são pequenos (11 px, sem quebrar) e não podem roubar a cena.
   O rótulo diz a fonte: `selo("medido", fonte)` vira "MEDIDO · NASA SMAP" pela 1ª missão da NASA que aparece no texto da fonte
   (SMAP, GPM/IMERG, POWER, GRACE, MODIS, VIIRS, ECOSTRESS, NASADEM; 3 ou mais = "NASA"); sem NASA, a 1ª entre NOAA (ONI), ZARC,
   CONAB, IBGE (PAM, Censo) e FAO (GAEZ). SUPOSIÇÃO fica sem fonte curta. Com fonte, o selo ganha `data-fonte` e `tabindex="0"`.
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
- Funciona a 390 px de largura (rolagem horizontal só dentro de um gráfico, nunca da página), também com todo "ver mais" aberto.
- Alvos de toque ≥ 44 px (todo `summary` também); o `.eco` usa `--ink-3` (contraste ≥ 4,5:1).

**Limites a 390 px, com todo "ver mais" fechado** (seção 5 do fluxo; `testes/ferramentas/aceite_fluxo.py` confere nos 7 municípios):

| Tela | Altura máx. | Palavras (meta / teto) | Outro |
|---|---|---|---|
| Sua roça (2) | 1.000 px | 70 / 100 | a linha da terra começa acima da dobra de 390×844 |
| O plano (3) | 2.400 px | 200 / 300 | "Agora" ≤ 400 px do topo; o desenho começa ≤ 550 px |
| Quanto rende (4) | 2.200 px | 180 / 260 | o gráfico Hoje/Melhor/Ideal começa ≤ 450 px, sem controle antes |
| Se secar (5) | 2.400 px | 200 / 300 | as linhas de 2027 e o título de "E se chover…" ≤ 900 px |
| Do espaço (1) | 2.800 px | 250 / 320 | — |

Topo fixo ≤ 96 px e barra de baixo ≤ 64 px. No máximo 2 "seu olho" à vista por tela. Para conferir depois de mexer:
`testes/ferramentas/aceite_fluxo.py` (tabela por tela e município + os toques) e `percorrer_fluxo.py` (prints do percurso e o "Seu Antônio").

## Extras (js/extras/): blocos prontos dentro dos passos

Cada extra é um módulo `js/extras/<id>.js` com `export default { id, async render(el, ctx, opcoes) }`, que desenha dentro do próprio `<div>`.
O passo põe o div com `U.extra(id, opcoes)` no HTML e, no fim do `render` (que vira `async`), chama `await U.montarExtras(el, ctx)`.

- `montarExtras` importa cada extra uma vez só e pede o CSS dele (`css/extras/<id>.css`) só quando ele aparece; o extra desenha depois que o
  CSS chegou. `voce_decide.css` e `glossario.css` valem na jornada toda e já vêm no `roca.html`.
- Um extra dentro de um `verMais` fechado só é montado quando a pessoa abre (nada é baixado antes).
- Espera no máximo 700 ms: com os dados em cache (redesenho por resposta nova) tudo entra antes de o passo ir para a tela, sem a página pular.
- Se um extra falha, o div some e o passo segue. Pedido recusado pelo servidor (JS ou CSS): tenta de novo uma vez.

**Regra do enxuto:** no máximo 2 blocos visíveis novos por passo; o resto vai para `verMais` ou para um toque. Um "seu olho" por bloco e
2 por tela, no máximo.

| Passo | Visível | No "ver mais" (montado ao abrir) |
|---|---|---|
| 2 Sua roça | uma tela com 4 linhas (`#linha-hoje`, `#linha-ha`, `#linha-terra`, `#linha-baixio`) e a faixa de 1 linha do El Niño e do solo; usa `CULT`, `igual`, `mexer` e `opcoesCultura` de `hoje_ideal.js` | `area` (`{semTitulo:true}`, "+ outra medida", num ctx de rascunho que não grava); "+ quanto de cada" |
| 3 O plano | faixa "Agora: …" (`agora(ctx)` de `plantio/calendario.js`), o roçado, a linha da maniva (só com mandioca no plano), "O que fazer e quando" (3 cartões, chip "Sua terra · mudar", aviso do "não sei" por `cardapio[].por_solo`, linha de sequeiro), `historico` `{modo:"cartao", olho}` ("Por onde começar o seu giro": supõe 2025 = jeito de hoje, 2 chips que gravam `antes`) | "Ver mês a mês e a rotação 2027–2029" (celular); "Por que este plano": `vulnerabilidade` `{painel:false}` ("Onde o seu roçado sofre mais"), as faixas ("Por que em faixas: a praga anda menos") e `saude_solo` `{titulo:false}` ("O que cada planta faz pelo solo") |
| 4 Quanto rende | linha "Conta com: …" (o que a conta supõe, com "ajustar"), `hoje_ideal` `{modo:"comparacao"}` (gráfico Hoje → Melhor → Ideal, sempre no típico; Melhor com até 3 ajustes), `cenarios` ("O que vale mais para você?": as abas Água · Renda · Solo · Um pouco de cada (o plano) gravam `prioridade` e não mudam o número grande) | "Ver a comparação" (grade e giro dos jeitos, no celular); "Ajustar a conta" (custo, preço da raiz, arranjo, "Mudar o que planta"); El Niño; "Quando o dinheiro entra"; "A colheita paga o gasto?"; "Ver como calculamos" (detalhe do Hoje/Melhor/Ideal e os 28 anos) |
| 5 Se secar | "2027, cada cultura" (1 linha por cultura, grade de 10), `cenario_chuva` `{partes:["cenario"], agro}` ("E se chover…", abre em 100%; no celular, sem os pontos de cada ano e com as culturas lado a lado), `historico` `{modo:"memoria"}` (chips dos 3 piores anos do IBGE + "outro ano", gravam `exp` ali mesmo), `leve_ao_tecnico` (número de perguntas, água além da chuva, Garantia-Safra, imprimir e copiar; `compartilhar(ctx)` é o verde "Mandar no WhatsApp") | "Cada cultura, 2027 a 2029" (o que já se sabe hoje, régua dos anos, cartões, 28 anos); as perguntas e quem confere (no número de perguntas); "Ver cada ano: chuva, solo e colheita" (`cenario_chuva` `{partes:["sobreposicao"]}`); "Ver como medimos e quanto já acertou" (o 19/mar e o 30/abr com o "seu olho" dos portões, o que não dá para projetar, os 7 jeitos testados) |
| 1 Do espaço | El Niño em 1 manchete, indicadores 2×2, `tendencias` (grade de 2 colunas no celular, 1 frase por bloco), 6 culturas, `confianca`, linha "Quanto o cálculo já acertou → Se secar" | "Ver cada El Niño forte", "Ver todas as N" (culturas com datas), "O ano da chuva aqui" (régua), "De onde vêm os dados" (`satelite_chao` + `harmonizacao`, ponto 3 e 7), `glossario` (a lista) |

**Ponto 16 em toda a jornada** (`js/extras/voce_decide.js`, lista e condições em `integracao/voce_decide.md`):
- a frase fixa "O QUADRA ajuda. Quem decide é você, com o técnico." é um link ao "Leve para o técnico" do passo 5 (`roca.js`): no
  computador fica na barra de baixo (`#moldura`); no celular sai da barra e vira o rodapé de cada passo (`.passo-fim`, `#decide-fim`);
  a mesma frase está no cartão do lugar do globo (`index.html`) e embaixo do botão do plano no painel (`painel.html`);
- o 1º "seu olho" à vista de cada passo vira "o que é?" (termo `seu_olho` do glossário; `roca.js`, `explicarOlho`): no toque não há title;
- `olho(OLHOS.<chave>)` ("seu olho") entra no texto do passo: El Niño (com o mês em que a estação daqui começa), litoral leste, cultura sem
  zoneamento, terra, baixio, tarefa, irrigação, faixas, metade guardada, vizinhos, preço da raiz, lavoura grande (no passo 4, no
  aviso do gráfico quando o IBGE daqui passa de 2× a roça de família da CONAB, e no "Ajustar a conta" sem mandioca; no passo 5, no ver mais "Cada cultura"), anos de El Niño e portões (no ver mais do fim do passo 5; onde os portões
  não valem, a abertura não dá data e o selo é SUPOSIÇÃO). Todo passo tem pelo menos 1 à vista e no máximo 2;
- `confianca` no passo 1 e `leve_ao_tecnico` no passo 5.

**Glossário** (`js/extras/glossario.js`): `roca.js` chama `instalar(ctx)` a cada passo (o JSON do município só baixa no 1º balão aberto); o texto usa `termo(chave, "palavra")` só na 1ª
aparição de cada passo, nunca dentro de `<button>`, `<a>`, `<summary>` ou de `ind({rot})`. Ligados hoje: `el_nino`, `em_dez`, `umidade_solo`,
`zarc` (passo 1), `em_dez` (passos 4 e 5), `evapotranspiracao` e `ndvi` (cartões das tendências), `geada`, `veranico` e
`balanco_hidrico` (vulnerabilidade) e `seu_olho` (o 1º "seu olho" de cada passo).

O mapa do globo tem as próprias camadas (`js/globo/camadas.js`, ligado em `js/globo/mapa.js`), fora da jornada: Foto, Milho, Chuva,
Solo (mês a mês desde 2015), Calor (2000–2025, NASA POWER) e Água guardada (2002–2026, GRACE por mesorregião), as três com controle de
tempo e "tocar", e Confiança. Calor e Água vêm de `dados/camadas_tempo.json` (`ferramentas/preparar_camadas_tempo.py`, ~90 KB, baixado só
quando uma das duas abas abre).
