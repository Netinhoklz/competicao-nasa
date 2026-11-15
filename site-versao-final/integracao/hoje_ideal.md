# Módulo "Hoje → melhor → ideal" (pedido do José, 14/11)

> "Quero que o usuário tenha a oportunidade de chegar e colocar as configurações que ele trabalha hoje para tentar otimizar e
> melhorar ainda mais o que ele já faz hoje e também o que seria o ideal máximo para ele!"

## Arquivos (só estes; nada nos passos, roca.js, comum.js, quadra.css, calculo.js, nucleo/ ou servidor.py)

| Arquivo | O que é |
|---|---|
| `web/js/extras/hoje_ideal.js` | o módulo: `export default { id: "hoje-ideal", titulo, async render(el, ctx, opcoes) }` e as funções puras abaixo |
| `web/css/extras/hoje_ideal.css` | estilo, todo dentro de `.hoje-ideal` (só tokens de `quadra.css`) |
| `web/teste/hoje_ideal.html` | página de teste: `http://127.0.0.1:8090/teste/hoje_ideal.html?cod=2311306&modo=ambos` |

Parâmetros da página de teste: `cod`, `modo=ambos|pergunta|comparacao`, `hoje=<texto>`, `tela=0..3`, `ha`, `baixio_ha`, `baixio=0`,
`maniva`, `prioridade`, `custo`, `raiz`, `semfin=1` (simula município sem série). A API demora alguns segundos com o servidor ocupado.

## Os dois modos

```js
import HI from "../extras/hoje_ideal.js";          // de dentro de js/passos/
await HI.render(div, ctx, { modo: "pergunta", aoTerminar: (h) => {...}, linkComparacao: ctx.link(4), tela: 0 });
HI.render(div, ctx, { modo: "comparacao", linkMudar: ctx.link(2), semTitulo: true });
```

- `render` escreve em `div.innerHTML`: passe uma `div` só para o módulo. Os eventos ficam no filho, e redesenhar não acumula ouvintes.
- **pergunta** ("Como você planta hoje?", 3 telas, no estilo do passo 2): (1) culturas em botões grandes (milho, feijão, mandioca,
  sorgo e palma só se o cardápio não diz "fora", e "outra") e quanto de cada (barra do roçado + −/+ de 10%, "dividir igual");
  (2) arranjo: tudo junto / em pedaços / milho no baixio (só com baixio) / não sei (1 toque escolhe e avança); (3) três pares sim/não:
  1ª chuva ou espera firmar, queima ou não, guarda semente ou compra. Com o padrão já marcado, são 3 toques (Próxima, arranjo, Pronto);
  "Não sei / pular" grava `""` (vale o padrão) em 1 toque. Grava com `ctx.set({ hoje })` ao sair das telas 1, 2 e 3 (não a cada toque
  da tela 1). No fim chama `opcoes.aoTerminar(h)`; sem ele, mostra um resumo com "mudar" em cada ficha. `opcoes.tela` força a tela inicial.
  A tela atual fica numa variável do módulo; ela volta a 0 quando `ctx.entrou` é true (uma vez por ctx).
- **comparacao**: título, chip com o jeito de hoje ("· mudar" → `opcoes.linkMudar`, senão `ctx.link(2)`), aviso de dado, um gráfico
  (3 colunas: o típico em 3 anos com o traço do caso ruim), as colunas HOJE, MELHOR e IDEAL, e o fecho "Quem decide é você, com o
  técnico", com o ajuste que mais depende do olho. Método, áreas e tabela P10/P50/P90 ficam no "Ver como calculamos". `semTitulo: true`
  tira o título (use no topo do passo 4, que já tem o dele).

## Formato de `ctx.resp.hoje`

```
milho:50,feijao:50|cons=1|1chuva=1|queima=1|sem=1
```

| Parte | Valores | Sem a chave (padrão) |
|---|---|---|
| culturas `chave:%` separadas por vírgula | `milho`, `feijao`, `mandioca`, `sorgo`, `palma`, `outra`; inteiros que somam 100 (o leitor renormaliza) | `milho:50,feijao:50` |
| `cons` | 1 = tudo junto (consórcio); 0 = em pedaços | 1 |
| `mbx` | 1 = milho no baixio (só com `cons=0`) | não |
| `1chuva` | 1 = planta na 1ª chuva; 0 = espera a chuva firmar | 1 |
| `queima` | 1 = queima o roçado; 0 = não queima | não sei (sem alerta) |
| `sem` | 1 = guarda a semente; 0 = compra ou recebe | Censo 2017: 1 se `padroes.pct_semente_milho` ≥ 50 |

`""` = não respondeu = todos os padrões (milho + feijão juntos, na 1ª chuva: o mais comum no semiárido). Funções: `lerHoje(txt, r.padroes)`
e `escreverHoje(h)`. O texto passa intacto pelo `roca.js` (testado: `URLSearchParams` codifica `: , | =`, o `decodeURIComponent` do hash
devolve, e o `URLSearchParams` da leitura corta só no primeiro `=`).

## O que o integrador faz

1. `roca.js`: `PADRAO` ganha `hoje: ""`. **Não** mande `resp.hoje` para a API: `/api/local` tem um parâmetro `hoje` que é uma DATA
   (AAAA-MM-DD). O `paramsApi` atual não manda; só cuidado ao mexer nele (ou renomeie a chave para `pratica` nos dois lados).
2. `roca.html`: `<link rel="stylesheet" href="css/extras/hoje_ideal.css">`.
3. **Passo 2 (sugestão: a pergunta é a 1ª tela, "Como você planta hoje?")** em `perguntas.js`:
   ```js
   import HI from "../extras/hoje_ideal.js";
   let q = -1;                                   // -1 = "Como você planta hoje?"; depois 0..4 como hoje
   // no render, ao chegar: if (ctx.entrou && !ctx.zerou) { q = -1; ... }
   if (q < 0) return HI.render(el, ctx, { modo: "pergunta", aoTerminar: () => { q = 0; this.render(el, ctx); } });
   ```
   O resumo do passo 2 pode ganhar a ficha do jeito de hoje com `resumoHoje(lerHoje(ctx.resp.hoje, ctx.r.padroes), U)`
   (`[ícone, texto, tela]`) ou só `descHoje(h)`.
4. **Passo 4 (sugestão: a comparação no topo, antes dos números do plano)** em `dinheiro.js`, depois do `el.innerHTML = ...`:
   ```js
   el.insertAdjacentHTML("afterbegin", `<div class="hi-slot"></div>`);   // ou logo depois da .titulo-passo
   HI.render(el.querySelector(".hi-slot"), ctx, { modo: "comparacao", linkMudar: ctx.link(2), semTitulo: true });
   ```
   O modo comparação é síncrono (o `render` é async só por causa do contrato).
5. **O `calculo.js` usando o "hoje" informado no lugar do milho + feijão fixo** (sem editar o `calculo.js`): em `dinheiro.js`, troque
   `const m = C.montar(r, ef);` por
   ```js
   import { comHoje } from "../extras/hoje_ideal.js";
   const m = comHoje(C.montar(r, ef), r, ef, ctx.resp.hoje);
   ```
   `comHoje` devolve o mesmo `m` com `m.s0` refeito pelas áreas informadas, com os meses de plantio e colheita da agenda que o próprio
   `montar` já tirou (o caixa mês a mês continua certo), e com as séries e os anos estendidos se o jeito de hoje tiver mandioca. Sem
   resposta (`""`) devolve o `m` intacto. Se o informado não tem conta aqui (só sorgo/palma, ou cultura sem série), mantém o S0 fixo e
   marca `m.hojeFixo` com o motivo (mostre como chip). Para o rótulo, troque o `<small>milho + feijão</small>` do herói por
   `m.hojeDesc || "milho + feijão"`. Conferido no node: com `""` ou `milho:50,feijao:50` o S0 sai idêntico ao de hoje (Quixadá
   2.865 / 7.212 / 12.275); com `milho:40,feijao:30,mandioca:30` o S0 do passo 4 (8.421 / 13.000 / 17.835) bate com o HOJE do módulo.
6. Ponto 16: o módulo desenha o próprio olho (mesmo traço do `extras/voce_decide.js`). Se quiser uma fonte só, troque o `OLHO` local
   por `icOlho()` de `voce_decide.js`.

## Como a conta é feita (resumo; o detalhe está no "Ver como calculamos")

- A mesma do passo 4: `calculo.totais()` com 2027 entre os 4 El Niños fortes e 2028–29 entre os 28 anos (3.136 combinações), o mesmo
  ano para todas as culturas e para os três caminhos, R$ de 2025, custo e preço da raiz escolhidos no passo 4 (`ef.custo`, `ef.raiz`).
  Só milho, feijão e mandioca têm R$; sorgo, palma e "outra" ocupam área e ficam fora (o sorgo paga a semente, como no passo 4).
- **HOJE**: as áreas informadas. Tudo junto ou em pedaços dá o mesmo R$ por ha (o IBGE não separa); a mandioca fica duas estações no chão
  (por ano, metade colhe e metade planta). Quebra = ano em que a colheita do roçado vale menos da metade do típico dele (a régua do IBGE
  para uma cultura), nos 28 anos. Alertas (até 3): "sem reserva" (medido: a colheita cai à metade ou a um terço no El Niño forte), "milho
  fora do baixio" (medido: quebra do milho daqui, só se ≥ 2 em 10), queimar, 1ª chuva (mediana do início da chuva), arranjo.
- **MELHOR**: ajustes pequenos no que ele já faz. Com conta, só se ganham no típico e ficam à frente de hoje em 6 de 10 combinações ou
  mais: "milho só no baixio; em cima, feijão" e "um pedaço de mandioca de reserva" (⅓ da terra alta, o tamanho de uma parte do plano;
  só onde o cardápio não diz "fora"; em 2027 só metade é plantada e colhe a partir de 2028, salvo maniva já no chão). Sem R$: metade
  guardada até ~10/mar (só quando a agenda ou o interruptor do plano mandam; senão "escalone" em ano de alerta), janela boa do ZARC (se
  planta na 1ª chuva), faixas (passo 3), sem fogo (se queima), garantir a semente (se compra). Mostra 4; o resto vai para "Mais N ajustes".
- **IDEAL**: o plano do motor (`ctx.r.plano`) na conta do passo 4: os números são os mesmos do herói do passo 4 quando o hoje é o padrão.
  `prioridade = garantir` → o número grande é o caso ruim; `vender` → o típico.
- Olho: metade guardada / escalonar > janela > milho no baixio > faixas (o primeiro que aparecer).

## O que aparece (3 ha, 1 ha de baixio, garantir, só a semente, raiz = mediana da UF)

| | HOJE (milho + feijão juntos) | MELHOR | IDEAL |
|---|---|---|---|
| Quixadá | típico R$ 7.210, ruim R$ 2.870, quebra 2 em 10 | R$ 12,2 mil / R$ 7.220, quebra 1 em 10, à frente 100 de 100 | R$ 12,7 mil / R$ 8.020, quebra 1 em 10, à frente 98 de 100 |
| Arapiraca | R$ 16,0 mil / R$ 9.380 | R$ 17,4 mil / R$ 11,5 mil (só milho no baixio; mandioca "fora" no cardápio) | R$ 8.800 / R$ 5.390: atrás em R$ (sorgo = comida da criação) |
| Barreiras | R$ 67,4 mil (IBGE de lavoura grande: aviso, números apagados) | igual a hoje (nenhum ajuste passa no 6 de 10) | R$ 44,0 mil |

## Pendências

- Os ganhos do baixio úmido, das faixas, de não queimar, da janela e da metade guardada não têm R$ (o IBGE não separa quem faz); só a
  troca de cultura e a reserva de mandioca entram na conta. O ganho da rotação contra o consórcio de hoje segue não medido.
- A reserva de mandioca pesa muito pelo preço da raiz (o mesmo seletor do passo 4).
- O módulo não foi testado dentro do `roca.html` (só na página de teste com o ctx mínimo); conferir depois de integrar.
