# Ponto 16, "Você decide": onde cada peça entra

O QUADRA apoia e não substitui quem planta. A camada tem 4 peças. Todas são leves: o CSS tem ~5 KB, os módulos ~13 KB e o JSON tem
132 KB, buscado uma vez só no passo 1 e reaproveitado do cache no passo 5.

| Peça | Arquivo | Onde |
|---|---|---|
| Frase fixa da moldura | `voce_decide.js` (`FRASE`, `moldura()`) | barra de baixo de `roca.html`, em todos os passos |
| "Seu olho" (1 linha) | `voce_decide.js` (`olho(texto)`, `OLHOS`) | 13 momentos da jornada (lista abaixo), no máximo 1 por bloco |
| Confiança dos dados aqui | `confianca.js` + `web/dados/confianca_mun.json` | passo 1, entre "O que dá para plantar aqui" e o botão das 5 perguntas |
| Leve para o técnico | `leve_ao_tecnico.js` | passo 5, entre "O que vamos olhar" (portões) e "Ver o que não dá para projetar" |

O CSS de tudo está em `web/css/extras/voce_decide.css`, junto com a folha de impressão.

## 0. roca.html

1. No `<head>`, depois de `css/passos/seguranca.css`, entra `<link rel="stylesheet" href="css/extras/voce_decide.css">`.
2. Na `<nav class="nav-baixo">`, entre `#voltar` e `#avancar`, entra a frase fixa. Ela vai em HTML estático para aparecer antes do JS:

```html
<p class="moldura-decide"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="2.8"/></svg><span>O QUADRA ajuda. <b>Quem decide é você, com o técnico.</b></span></p>
```

**Por que no rodapé, e não no topo.** A barra de baixo é fixa: a frase fica à vista em todos os passos e ao lado do botão "Próximo",
que é onde a pessoa decide. O topo já tem a marca, o lugar e "Trocar o lugar". No computador, a frase fica centrada entre "Voltar" e
"Próximo", sem aumentar a barra. No celular, até 760 px, ela vira uma linha de 12 px acima dos dois botões
(`.nav-baixo:has(.moldura-decide)` passa a quebrar linha). A barra cresce ~20 px e cabe no `padding-bottom` de 110 px do `main`.

## 1. "Seu olho": a lista exata

Uso: `import { olho, OLHOS } from "../extras/voce_decide.js"` (dentro de `js/passos/`), e no HTML do bloco `${olho(OLHOS.<chave>)}`.
Cada texto tem até 12 palavras. Prioridade 1 = entra. Prioridade 2 = só se o bloco não ficar cheio.

| # | Passo · bloco (função, arquivo) | Onde exatamente | Condição | Chave · texto | Prio. |
|---|---|---|---|---|---|
| 1 | 1 · painel do El Niño (`elNino`, `lugar.js`) | depois de `<p class="sub enso-sub">`, dentro do mesmo `<div>` | sempre que o painel aparece | `el_nino` · "Os anos de El Niño discordam: olhe a chuva de fevereiro." | 1 |
| 2 | 1 · "O ano da chuva aqui" (`regua`, `lugar.js`) | depois de `.regua-legenda` | `/litoral leste/.test(r.este_ano.regime?.texto \|\| "")` | `leste` · "Perto do mar, o pluviômetro da comunidade vale mais que o satélite." | 1 |
| 3 | 1 · "O que dá para plantar aqui" (`culturas`, `lugar.js`) | depois de `<div class="culturas">` | `servem.some((i) => SIT[i.situacao][0] === "apto")` (há "Dá, sem zoneamento") | `sem_zarc` · "Sem zoneamento, a data é estimada: confirme com quem já planta." | 1 |
| 4 | 2 · pergunta da terra (`render`, `perguntas.js`) | depois de `.opcoes` (e de `extraAgua`), antes de `.quiz-muda` | `p.k === "terra"` | `terra` · "Na dúvida, aperte um torrão úmido: areia esfarela, barro gruda." | 1 |
| 5 | 2 · pergunta do baixio (idem) | mesmo lugar | `p.k === "baixio"` | `baixio` · "Ande no roçado depois de uma chuva: onde a água para?" | 1 |
| 6 | 2 · "Pronto." (`resumo`, `perguntas.js`) | **troca** o `<p class="aviso">Com irrigação, combine as datas…</p>` | `ef.agua === "irriga"` | `irrigacao` · "Com irrigação, as datas mudam: combine com o técnico." | 1 |
| 7 | 2 · tamanho do roçado (`telaArea`, `perguntas.js`) | depois do `<p class="sub centro">` da tarefa | sempre | `tarefa` · "A tarefa muda de lugar para lugar: confira a medida daqui." | 2 |
| 8 | 3 · "Seu roçado visto de cima" (`heroi`, `plantio.js`) | depois de `.mes-controle`, antes do 1º `verMais` | sempre | `faixas` · "Faixas e espaçamento se acertam no chão, em curva de nível." | 1 |
| 9 | 3 · "O que fazer e quando" (`blocoTempo`, `plantio.js`) | depois de `linhaDoTempo(ctx)` | `/metade/i.test(ctx.r.plano?.interruptor \|\| "")` (alerta, quadra e leguminosa) | `metade` · "Metade guardada: só plante se a terra estiver molhada na mão." | 1 |
| 10 | 3 · "Por que em faixas" (`blocoFaixas`, `plantio.js`) | depois de `.rodape-faixas` | sempre | `vizinhos` · "Contra praga que voa, combine o plantio com os vizinhos." | 2 |
| 11 | 4 · "Seu bolso" (`bolsoHtml`, `dinheiro.js`) | depois de `.bolso-linha`, antes de `.bolso-chips` | `temMand` | `preco_raiz` · "Pergunte o preço da raiz na casa de farinha daqui." | 1 |
| 12 | 4 · aviso de lavoura grande (`render`, `dinheiro.js`, `const aviso`) | dentro do `painel alerta`, depois do `<p class="pequeno sub">` | `agro` (`m.agro.length > 0`) | `agro` · "Faça a conta com o que a sua família colhe." | 1 |
| 13 | 5 · "Cada cultura do plano" (`render`, `seguranca.js`) | depois de `reguaAnos(U, r, dados)`, antes de `cartoes` | há cartões | `memoria` · "Lembra de 2010 e 2016? Compare com a colheita da sua roça." | 1 |
| 14 | 5 · "Vamos olhar de novo em 19/mar e 30/abr" (`blocoPortoes`, `seguranca.js`) | depois de `<p class="sub seg-apoio">`, antes de `.grade-3` | `vale` (= `ag.portoes !== false`) | `portoes` · "19/mar e 30/abr: confira a umidade na mão e com o técnico." | 1 |
| 15 | 5 · idem | mesmo lugar | `!vale` | `portoes_fora` · "Aqui as datas de troca são outras: decida com o técnico." | 1 |

As linhas 14 e 15 são o mesmo bloco: sai uma ou a outra. Em Quixadá, com as respostas padrão, aparecem 2 no passo 1, 1 por pergunta
no passo 2, 2 no passo 3, 1 no passo 4 e 2 no passo 5.

## 2. Confiança dos dados aqui (passo 1)

Em `lugar.js`, o `render` vira `async`. O `roca.js` já espera o `render`. No HTML, entre `${culturas(r, U)}` e o
`<a class="botao primario cta">`, entra `<div data-extra="confianca"></div>`. Depois do `innerHTML`:

```js
import CF from "../extras/confianca.js";
await CF.render(el.querySelector('[data-extra="confianca"]'), ctx);
```

O bloco é um painel com três partes:
- um medidor de 3 barras, como o sinal do celular: verde/alta, âmbar/média ou terra/baixa;
- uma frase curta e até 3 motivos de até 10 palavras;
- o "Ver por quê", que mostra todos os motivos com fonte, onde o técnico pesa mais e como o nível é calculado.

O bloco leva um selo SUPOSIÇÃO: os critérios são medidos, mas os pesos são escolha nossa. Se o JSON faltar, o bloco some.

`confiancaDe(dados, cod, ctx.r)` devolve o contrato: `{nivel, motivos: [{chave, texto, peso, tecnico}], tecnico: [...]}`. A
agenda da resposta acerta dois critérios. "estimada" passa a nomear a cultura ("Data de plantar da mandioca estimada pela chuva.").
"portoes" passa a usar o `agenda.portoes` do motor. Exemplo: em Arapiraca a 1ª janela abre em 11/04, então os portões não valem.

**Formato do JSON:** `{"_sobre", "_textos": {chave: {texto, tecnico, peso}}, "<cod>": {"nivel", "motivos": [chaves]}}`. Os textos
ficam uma vez só em `_textos`. Repetidos em cada município, o arquivo passaria de 500 KB; assim fica com 132 KB. O nível por
município também serve ao globo ou ao painel do JP, se quiserem pintar o mapa.

## 3. Leve para o técnico (passo 5)

Em `seguranca.js`, o `render` vira `async`. Entre `${blocoPortoes(U, r, dados)}` e `${blocoLimites(U)}` entra
`<div data-extra="leve_ao_tecnico"></div>`, e depois:

```js
import LT from "../extras/leve_ao_tecnico.js";
await LT.render(el.querySelector('[data-extra="leve_ao_tecnico"]'), ctx);
```

O bloco tem um número grande, a lista e dois botões de 48 px:
- **Lista:** 5 a 7 perguntas tiradas do ctx: terra, baixio, faixas e espaçamento, a data da leguminosa, metade guardada e portões
  (ou "que datas valem na minha estação"), preço da raiz, água e maniva. Entram também os pedidos dos motivos de confiança daqui.
- **Linha medida:** "Aqui, só 7 de 100 roças de família recebem orientação técnica" (Censo 2017, selo MEDIDO).
- **Imprimir:** sai só uma folha clara, com caixinhas, o resumo da roça, a confiança, um espaço para anotações e a frase.
- **Copiar para o WhatsApp:** copia o mesmo texto puro.
- **"Onde achar quem confira":** o órgão de assistência rural do estado (Ematerce, IPA, Bahiater…), o sindicato, a secretaria do
  município, a casa de farinha e o vizinho.

## 4. Teste

`http://127.0.0.1:8090/teste/voce_decide.html?cod=2311306` (opções: `terra=`, `agua=irriga|barreiro`, `vol=`, `maniva=nao`,
`tem_baixio=0|?`). Conferido a 1300 e 390 px, sem rolagem lateral nem erro de JS, em Quixadá, Arapiraca (sem baixio, barreiro) e
Barreiras (terra arenosa, irrigação). A folha de impressão foi conferida com a mídia de impressão emulada.

Para regerar o JSON (~20 s): `E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_confianca.py`.
