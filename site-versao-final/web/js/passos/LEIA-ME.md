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
| `ctx.ef` | respostas com os padrões aplicados: `terra` (nao_sei/arenosa/mista/barro), `ha`, `ha_origem`, `baixio` (nao_sei/nao/pouco/terco/metade), `tem_baixio` (true/false/null), `baixio_frac`, `baixio_ha`, `agua` (chuva/cisterna/barreiro/irriga), `vol_m3`, `maniva` (tem/nao/plantada), `criacao`, `prioridade` (garantir/equilibrar/vender), `prioridade_origem`, `gs`, `raiz` (municipio/uf_mediana/uf_p25), `custo` (semente/desembolso) |
| `ctx.set(patch)` | muda respostas (chaves de `PADRAO` em roca.js; valores em texto) e redesenha; se a resposta muda o núcleo, busca de novo |
| `ctx.ir(n)` / `ctx.link(n, patch)` | vai ao passo n / devolve o href do passo n |
| `ctx.util` | `js/comum.js`: `esc, num, brl, brlMil, pct, emDez, selo(tipo, fonte), dataBR, mesAno, MESES, tipoCss, ha` |

## Regras

- Cada passo só escreve nos próprios arquivos: `js/passos/<id>.js`, `css/passos/<id>.css` e, se precisar, `js/passos/<id>/*.js`.
- Cores e fontes só pelos tokens de `css/quadra.css` (`var(--green)`, `var(--surface)`…). As classes `.t-leguminosa`, `.t-cereal`,
  `.t-tampao`, `.t-forragem`, `.t-perene`, `.t-pousio` definem `--cor` (forte) e `--fundo` (claro) do tipo de cultura. Modo escuro sai dos tokens.
- Gráficos em SVG à mão, sem biblioteca. Um eixo só; legenda quando houver 2 séries ou mais; texto na cor da tinta, não da série.
- Todo número leva `ctx.util.selo("medido" | "suposicao" | "projecao", fonte)`.
- Linguagem do agricultor (frases curtas, "em 7 de 10 anos"), com o detalhe técnico em `<details>`.
- Funciona a 390 px de largura (rolagem horizontal só dentro de um gráfico, nunca da página).
