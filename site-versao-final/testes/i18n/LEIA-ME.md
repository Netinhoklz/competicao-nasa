# O site em inglês (e em português)

O site é escrito em português. O inglês, que é a língua padrão, vem de uma camada de tradução no DOM: `web/js/i18n.js`, o 1º
script do `<head>` das 3 páginas. Ele troca o texto mostrado pelo de `web/i18n/en.json`, sem mexer na lógica dos passos.

- **Língua:** `?lang=en|pt` na URL (na busca ou no hash: `roca.html#/2311306/3?lang=pt`) grava e vence; depois vale a da
  página de fora (o painel no iframe do globo), depois o `localStorage` `quadra-lingua`, e por fim o inglês.
- **Seletor:** "English | Português" no topo da página inicial; "EN/PT" no cabeçalho da jornada e do painel. Os dois chamam
  `QUADRA_I18N.mudar(l)`, que grava e recarrega mantendo o hash.
- **Testes:** as ferramentas que abrem o Edge (`aceite_fluxo.py`, `percorrer_fluxo.py`, `teste_pdf.py`, `teste_painel.py`…)
  gravam `quadra-lingua = pt` antes de cada página. O aceite roda em português. Para ver uma tela em inglês, ponha
  `?lang=en` na URL.

## O en.json

```json
{
  "textos":  { "Voltar ao espaço": "Back to space", "Ver o meu plano →": "See my plan →" },
  "modelos": { "Sobra R$ {0} por ano": "R$ {0} left per year", "{0} ha (típico)": "{0} ha (typical)" }
}
```

- **A chave** é o texto de um nó (ou de um atributo `aria-label`, `title`, `placeholder` ou `alt`). As pontas levam `trim` e os
  espaços de dentro viram um só (quebra de linha e espaço duro também). Os espaços das pontas do nó continuam no lugar.
  Cada `<b>`, `<span>` ou `<a>` no meio da frase corta o texto em pedaços: `O QUADRA ajuda. <b>Quem decide…</b>` são 2 chaves.
- **Com " · ":** quando o texto inteiro não está no dicionário, cada pedaço é traduzido sozinho. Assim
  `QUADRA · Quixadá (CE)` e `medido · de onde vem` funcionam com `textos` de um pedaço só.
- **Modelos:** se o texto não está em `textos`, cada número vira `{0}`, `{1}`… e o modelo é procurado.
  - Um número é `2.480`, `0,5`, `-33`, `−R$`, `1.234,56` ou uma data `15/11/2026` (a data inteira vale um só número).
    `40 × 100 m` tem dois números: `{0} × {1} m`. Um número colado numa letra não conta (`SMAP L4`, `MOD13Q1`).
  - Na hora de escrever o inglês, o número muda de formato: `2.480` vira `2,480`, `0,5` vira `0.5` e `1.234,5` vira `1,234.5`.
    Datas e frações (com `/`) ficam como estão. `R$` fica.
  - A ordem pode mudar: `"{0} de {1}": "{1}'s {0}"`.
- **Neutro (já vale em inglês):** é o texto que, além de número, só tem unidade (`R$`, `m`, `ha`, `km`, `kg`, `mm`, `°C`…),
  sigla (até 5 maiúsculas sem acento: `NASA`, `SMAP`, `ZARC`, `IBGE`, `CE`) ou letra solta (as partes `A B C`, os meses
  `J F M`). Exemplos: `R$ 1.390`, `11,3 m`, `NASA GPM`. Sem entrada no dicionário, ele fica como está e só o número muda para
  o formato do inglês. Também não entra na cobertura. Uma palavra em maiúsculas não é neutra (`MEDIDO`, `SUPOSIÇÃO`), nem uma sigla
  maior (`QUADRA`, `NASADEM`). Essas vão no dicionário, igual ao português quando não mudam: `"QUADRA": "QUADRA"`.
  - Atenção ao `O` (Oeste) das coordenadas: é neutro, então precisa de modelo (`"{0}° O": "{0}° W"`, já no en.json).
- **Nomes de lugar nunca se traduzem** (regra do José). Isso vale para município, estado e UF. A lista é
  `web/i18n/lugares.json`, gerada por `ferramentas/preparar_i18n_lugares.py` a partir de `web/dados/busca_municipios.json`.
  - **Quando um nome conta como lugar:** se é estado ou UF; se é o município da página (`roca.html#/<cod>`,
    `painel.html?cod=<cod>`, o cartão e o `?lugar=` do globo); se vem colado numa UF (`Serra Talhada-PE`,
    `Oeiras (INMET/PI)`, `Quixadá, CE`); ou se é o texto inteiro (`Sobral`).
  - **Texto só de lugar** (com número, sigla e unidade, ex.: `Quixadá (CE)`, `Ceará · IBGE 2311306`): fica como está, só o
    número muda de formato. Também não entra na coleta nem na cobertura. Nunca ponha um texto assim no en.json.
  - **Dentro da frase,** o lugar vira marcador, igual ao número, e volta intacto. `Em Quixadá, o milho quebra 3 em 10 anos`
    vira `Em {0}, o milho quebra {1} em {2} anos`, e o modelo serve para todos os municípios. Na coleta, a frase com lugar
    só vem na forma de modelo.
  - **Palavra do site que é nome de município:** `Barro`, `Areia`, `Baixio`, `Capim`, `Saúde`, `Lagoa`… (o `vocab` do
    lugares.json) só conta como lugar nos três primeiros casos. Sozinha, é palavra: vai no en.json (`"Barro": "Clay"`).
    Toda chave do en.json também é tratada como palavra. Se uma palavra do site aparecer como `{0}` num modelo da
    coleta, ponha a palavra no en.json ou em `EXTRA` no gerador, e rode o gerador de novo.
  - **O texto exato do en.json (`textos`) sempre vence.** Ele é traduzido mesmo que seja nome de município. Por isso, onde a
    tela mostra o município de verdade, o elemento tem `translate="no"`: a lista da busca e os atalhos do globo, o nome no
    cartão do mapa, o lugar no topo da jornada, o lugar na faixa do painel e o balão do mapa do painel.
  - **Duas formas de chave valem.** A nova (lugar e número como marcador: `raiz a R$ {0}/kg (comum no {1}) ·`) é procurada
    primeiro. A antiga (só número: `raiz a R$ {0}/kg (comum no CE) ·`) também vale, para as chaves feitas antes de 15/11.
    `testes/ferramentas/i18n_converter_chaves.py` acrescenta ao `modelos` a forma nova de cada chave antiga, sem retraduzir e
    sem apagar nada.
- **Não se traduz:** `script`, `style`, `code`, `textarea`, `noscript` e o que tiver `translate="no"` ou `data-i18n="nao"`.
  Use `data-i18n="nao"` num trecho que não deve mudar (nome de variedade, código, citação).
- **String que não passa pelo DOM:** use `window.QUADRA_I18N?.t?.(texto) ?? texto`. Ela traduz linha a linha. Hoje só o texto do
  "Mandar no WhatsApp" usa (`compartilhar` em `web/js/extras/leve_ao_tecnico.js`). Ainda **não** usam: o "Copiar o texto" do
  mesmo arquivo, `alert`/`confirm`, texto desenhado em `<canvas>` e os nomes do mapa (MapLibre).

## Coletar, traduzir, medir

1. **Coletar** o que o site mostra (página em português, `?i18n=coletar`):
   `MSYS_NO_PATHCONV=1 E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 testes/ferramentas/i18n_coletar.py [cod,cod,...]`
   O resultado vai para `testes/i18n/pt_textos.json`: uma lista de `{chave, contagem, onde}` (onde = até 5 telas), em ordem
   alfabética. Cada texto com número aparece duas vezes: como veio e na forma de modelo (`{0}`). O texto com nome de lugar
   só aparece como modelo, e o texto só de lugar não aparece. A coleta inclui o que só sai na impressão (`beforeprint`) e o
   texto do WhatsApp. Sem argumento, roda os 7 municípios do aceite: 224 telas, ~40 min. Com um só:
   38 telas, ~9 min. Sua roça (passo 2) não lê o plano nem a prioridade, então roda só com as variantes que mudam a tela.
2. **Traduzir:** ponha cada chave em `textos` ou, se tiver número que muda, a forma com `{0}` em `modelos`. Escolha um dos dois,
   não os dois. Copie a chave do JSON como está (acento, seta `→`, `R$`). Use um inglês simples, para o agricultor e para o
   jurado. A sigla fica como está (NASA, ZARC, IBGE, SMAP). Nome de município ou de estado nunca se traduz: copie como está.
3. **Medir** (mesmo percurso, `?lang=en`):
   `MSYS_NO_PATHCONV=1 E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 testes/ferramentas/i18n_cobertura.py [cod,cod,...]`
   Grava `testes/i18n/faltas.json` (o que ainda aparece em português, `{chave, onde}`) e imprime
   `cobertura: X de Y textos (Z%)`. O texto neutro e os nomes de lugar não contam. A forma contada é a de modelo quando o
   texto tem número. `faltas.json` é a lista de trabalho: em `pt_textos.json` cada texto com número vem também cru.

Uma ferramenta por vez, nunca junto com o aceite: com dois Edge, o servidor recusa pedidos.

## Limites

- **Município que não é o da página, solto na frase:** sem UF colada, ele não vira marcador. Exemplo: as estações
  vizinhas citadas só pelo nome, como a lista `Aratuba, Guaramiranga, Ibiapina…`. Um texto fixo assim vai inteiro no en.json,
  com os nomes copiados como estão. Já um texto que muda de município para município fica uma chave por município. Para
  esse caso, o passo deve pôr o nome num elemento próprio ou com a UF (`Oeiras-PI`).
- **Texto lido de volta do DOM:** se o JavaScript lê um texto já traduzido e o junta com português (`textContent + " · de onde vem"`),
  o resultado mistura as línguas. Os pedaços com " · " resolvem a maior parte desses casos. Em inglês, dois lugares leem o texto
  de volta. O `reabrir` de `web/js/passos/dinheiro.js` compara o `<summary>` velho (já em inglês) com o novo (ainda em
  português): depois de um redesenho, o "ver mais" que estava aberto fecha. O `fundosRotulos` de `web/js/passos/plantio.js` mede
  o rótulo da faixa, e se ele mede antes da tradução, o fundo fica do tamanho do texto em português. O jeito de corrigir é
  comparar por uma chave fixa (`data-*`) em vez do texto.
- **Município com nome de palavra do site:** um município como Barro (CE) que aparece sozinho fora de um elemento com
  `translate="no"` vira "Clay", porque o dicionário vence. A frase com o nome dentro não tem esse problema.
- **Atributos:** `data-*` e `content` de `<meta>` não são traduzidos.
