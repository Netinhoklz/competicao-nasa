# Integração do "o que é?" (ponto 2)

Arquivos: `web/js/extras/glossario.js`, `web/css/extras/glossario.css`, `web/dados/glossario_mun.json` (91 KB, gerado por
`ferramentas/preparar_glossario.py`), teste em `web/teste/glossario.html?cod=2311306&abrir=veranico&lista=1`.

## Ligar (3 linhas)

1. `roca.html`: `<link rel="stylesheet" href="css/extras/glossario.css">` depois de `css/quadra.css`.
2. `roca.js`: `import { instalar } from "./extras/glossario.js";` e, logo depois de montar o `ctx` em `desenhar()`, `instalar(ctx);`
   Isso põe o município atual nos exemplos. Os ouvintes são instalados uma vez só e o balão fecha sozinho quando o passo muda.
3. Em cada passo que usa uma palavra: `import { termo } from "../extras/glossario.js";` e troque o texto por `${termo("chave", "texto")}`.

Não ponha `termo()` dentro de `<button>`, `<a>`, `<summary>` ou de elemento com `data-ir`, porque o toque ia disparar os dois.
`ind({ rot })` escapa o rótulo, então use o `sub` ou o `val`, que aceitam HTML. Com uma chave desconhecida, `termo()` devolve só o texto.

## Chaves

`el_nino` · `em_dez` · `zarc` · `umidade_solo` · `evapotranspiracao` · `balanco_hidrico` · `veranico` · `ndvi` · `geada`

## Onde ligar (só a 1ª aparição em cada passo)

| Chave | Passo | Arquivo:linha | Trecho de hoje | Trocar por |
|---|---|---|---|---|
| `el_nino` | 1 | `passos/lugar.js:59` | `` `2027 é ano de El Niño forte. Nos anos…` `` | `` `2027 é ano de ${termo("el_nino", "El Niño forte")}. …` `` |
| `em_dez` | 1 | `passos/lugar.js:59` (mesma frase) | `` `…a chuva veio fraca em ${n} de cada 10 municípios…` `` | `` `…em ${termo("em_dez", `${n} de cada 10`)} municípios…` `` |
| `umidade_solo` | 1 | `passos/lugar.js:78` (`ind` "O solo hoje", `sub`) | `"umidade da raiz vista do satélite"` | `` `${termo("umidade_solo", "umidade da raiz")} vista do satélite` `` |
| `zarc` | 1 | `passos/lugar.js:97` (legenda) | `<span class="chip">● Dá, sem zoneamento</span>` | `` `<span class="chip">● Dá, sem ${termo("zarc", "zoneamento")}</span>` `` |
| `em_dez` | 4 | `passos/dinheiro.js:159` (`rotulo`, aceita HTML) | `"No caso ruim (1 em cada 10)"` | `` `No caso ruim (${termo("em_dez", "1 em cada 10")})` `` |
| `em_dez` | 5 | `passos/seguranca.js:234` | `<span class="seg-piso-sub">em 8 de 10 anos parecidos</span>` | `` `…">${termo("em_dez", "em 8 de 10")} anos parecidos</span>` `` (aparece uma vez por cultura; se quiser, só na 1ª) |

Estas palavras ainda não aparecem na frente de nenhum passo: `veranico`, `evapotranspiracao`, `balanco_hidrico`, `ndvi` e `geada`.
Elas ficam na lista. Os extras dos outros pontos devem chamar `termo()` quando as mostrarem: o verde do satélite (pontos 1 e 11)
usa `ndvi`, a evaporação e a água usam `evapotranspiracao` e `balanco_hidrico`, e os momentos de estresse (pontos 5 e 12) usam
`veranico`. "Geada" não precisa entrar na frente, porque no Nordeste o risco é calor e veranico, e o balão já diz isso.

## A lista inteira (1 bloco, fechado)

No fim do passo 1, depois de `${evidencia(r, U)}` em `passos/lugar.js:131`:

```js
// no HTML do passo:  <div class="extra-glossario"></div>
import G from "../extras/glossario.js";
await G.render(el.querySelector(".extra-glossario"), ctx);           // opcoes: { titulo, termos: [chaves] }
```

Isso desenha um único `verMais` ("O que quer dizer cada palavra?"), fechado, com os 9 termos em duas colunas (uma no celular).
Cada termo tem a definição (até 2 frases) e um exemplo com o número do município e um selo. Não é preciso repetir a lista em
outros passos, porque os balões resolvem na hora.

## O que cada exemplo usa (Quixadá)

| Chave | Fonte do número | Quixadá |
|---|---|---|
| `el_nino` | `r.este_ano.oni` e `perspectiva` (ou `r.el_nino_uf`) | ONI +2,5 °C, acima de +1,5 (forte); 2 dos 3 El Niños fortes com dado trouxeram estação das mais secas |
| `em_dez` | `r.este_ano.inicio` (IMERG) | a chuva chega entre 31/12 e 14/02 em 8 de cada 10 anos |
| `zarc` | `r.este_ano.zarc_primeiro` | 1ª data 21/01 (risco até 4 em 10); menos risco (2 em 10) a partir de 11/02 |
| `umidade_solo` | `r.este_ano.smap` | 8º de 12 anos até 10/11 (1º = o mais seco): normal para a época |
| `evapotranspiracao` | JSON `et0_mm` (POWER, FAO-56) e `r.clima.chuva_anual_mm` | o ar puxaria ~2.210 mm/ano, chove 779 mm: quase 3 vezes |
| `balanco_hidrico` | `r.clima.meses_umidos` (POWER: chuva ≥ ½ ET0) | só em 5 meses a chuva cobre metade do que o ar puxa |
| `veranico` | JSON (IMERG diário, dias < 2 mm, do início da chuva ao fim dos 4 meses) | 7 em 10 anos com 10+ dias sem chuva; o mais longo, 22 dias, em 1999 |
| `ndvi` | JSON (MODIS MOD13A1, 2001–2025, ~15 km em volta do centro) | 0,75 em abril, 0,35 em outubro |
| `geada` | JSON (ERA5, mínima 1979–2020) e `r.clima.tmax_mes_mais_quente` | noite mais fria 19 °C (2008); tarde do mês mais quente 38 °C |

Limites ditos na tela: no leste (estação de mar–jun ou abr–jul e litoral leste), o veranico não mostra número, porque o IMERG
capta só 39–72% da chuva na costa e a conta de dias secos sai falsa (Recife daria 52 dias). Onde a noite mais fria fica abaixo de
10 °C (37 municípios das serras da BA), o balão diz para perguntar a quem mora aí. Sem o JSON, cada termo mostra só a definição e
os exemplos que vêm do `ctx`.
