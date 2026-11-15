# Rodada 2 do fluxo (15/11/2026, manhã): o jeito de hoje × o ideal, o terreno em metros e o relatório

Entrega: **hoje, 15/11/2026, 23:59**. 15 agentes, em fases, cada arquivo com um dono por fase.
Base: commit 1eb1f14 (fluxo da rodada 1: `analise/fluxo/00_FLUXO_FINAL.md`) + o preparo do orquestrador (abaixo).

## 1. O pedido do José (dono do projeto), na íntegra

> Precisamos aumentar a questão de dar suporte ao agricultor, precisamos aumentar a lista de o que ele faz hoje e fazer o
> planejamento com base no que ele faz hoje mas também mostrar qual seria o ideal! Montar um exemplo com base no que ele faz hoje
> e mostrar o ideal e colocar em que ele vai se beneficiar, tentar mensurar os benefícios que ele vai ter! Coloque mais opções em
> "O que planta hoje?" acrescente uma barra que vai mostrar todas as opções que temos hoje! Também quero que em "Tamanho: 0,4 ha,
> típico daqui" você coloque para ele colocar o tamanho do terreno de plantio em metros e na apresentação vamos mostrar o terreno
> dele e mostrar os metros que deve ser plantado e distanciamento ideal, ser mais didático nesse quesito. Explique melhor o que é
> "Tem baixio? A parte úmida.". Em "Plante em faixas. Cada ano, cada cultura muda de lugar." quero que você mostre o melhor sistema
> que tem para o que ele faz hoje, acrescente um botão intuitivo que ele irá clicar e ver o que seria o ideal dado todas as
> configurações da terra dele e dados que nós temos! Não entendi a parte "Mandioca (Parte A): tem maniva?" e "A terra repetiu
> milho: comece com o feijão nesse lugar." está meio solto ali no meio, parece ser algo para ser perguntado antes na aba anterior.
> Eu gostei muito da parte "O que vale mais para você?", porém tem de ser algo que temos de colocar na parte de "melhor
> configuração", para ele clicar e ver o que vai mudando, porque isso influencia na configuração do melhor! Essa parte "Se secar"
> está esquisita, temos que validar que já estamos dando o melhor para a pessoa, então vamos remover essa parte. A parte "Do
> espaço" está meio fora de local, ele deveria aparecer na parte de quando damos zoom na parte do mapa e também na parte do painel
> em "http://localhost:8090/painel.html". Vamos colocar no local de "Do espaço" um gerador de relatório que irá mostrar o plano
> detalhado com as datas exatas de quando fazer o que e como fazer.

Pedidos anteriores que continuam valendo: intuitivo, pouco texto, estilo da tela inicial (tema escuro do globo), enxuto, nada
transbordando; os 16 pontos do desafio (lista em `analise/fluxo/BRIEFING.md`, seção final), sobretudo o 16 (a ferramenta apoia, não
substitui o saber local); todo número com selo MEDIDO / SUPOSIÇÃO / PROJEÇÃO e a fonte (`U.selo`); um botão verde por tela.

## 2. Decisões do orquestrador (a leitura do pedido; não reabrir)

**D1. Jornada nova:** Sua roça (`#/<cod>/2`) → O plano (`/3`) → Quanto rende (`/4`) → **Relatório (`/5`)**.
Pílulas: Roça · Plano · Dinheiro · Relatório (`ORDEM = [2,3,4,5]`). "Se secar" sai da jornada (o `seguranca.js` fica no disco,
sem rota). `#/<cod>/1` (o antigo "Do espaço") redireciona para `#/<cod>/2`. O conteúdo do "Do espaço" vai para o painel e o mapa (D6).

**D2. Sua roça (uma tela, tudo com padrão; o caminho de 1 toque continua valendo):**
- "O que planta hoje?": as opções à vista (as mais comuns daqui) + **uma barra "Ver todas as culturas (N)"** que abre a lista completa:
  as 18 do cardápio do núcleo (`r.cardapio[].cultura`: Feijão-caupi, Milho, Feijão comum, Mandioca, Amendoim, Sorgo granífero,
  Guandu, Sorgo forrageiro, Milheto, Palma forrageira, Gliricídia, Mucuna-preta, Algodão herbáceo, Mamona, Girassol, Caju, Banana,
  Cana-de-açúcar) + "Outra". Escolha múltipla. Cultura fora do zoneamento daqui pode ser marcada (ele planta hoje), com um aviso curto.
  A lista mora em `web/js/extras/culturas.js` (CULT + opcoesCultura; ver seção 4). **Chaves que já existem não mudam**
  (`milho, feijao, mandioca, sorgo, palma, outra`): links antigos e o cenário "Seu Antônio" continuam iguais.
- Tamanho: os chips de ha continuam, e **"em metros" vira caminho de primeira classe**: Largura (m) × Comprimento (m) à vista (não
  escondido), com a conversão em ha e tarefas ao lado. Grava `ha`, `area_un` (formato que `area.js` já usa) e os novos `larg` e
  `comp` (metros, inteiros). Sem resposta: o típico do Censo, como hoje.
- Terra: como está.
- **Baixio explicado:** "Tem baixio?" com uma frase clara (a parte mais baixa do roçado, para onde a água da chuva escorre e a
  terra fica úmida por mais tempo: beira de riacho, grota, açude) e um desenho pequeno de perfil (alto → baixio).
- **Maniva e o ano passado vêm para cá** (saem do Plano): "Tem maniva (rama de mandioca) para plantar?" (Tenho · Já está plantada ·
  Não tenho · Não sei; chave `maniva`, valores que já existem: tem | plantada | nao) e "No ano passado, o que plantou nesse chão?"
  (chips das culturas dele + "Descansou" + "Não sei"; chave `antes`, formato que `historico.js` já usa).
- "O que vale mais para você?" **não** entra aqui (vai para o Plano, D3).
- Limites a 390 px: altura ≤ 1.800 px, ≤ 190 palavras à vista (`#jornada.innerText`, com os "ver mais" fechados).

**D3. O plano (`/3`): o jeito dele melhorado, e um botão para o ideal.**
- Abre em **"Seu jeito, melhorado"**: só as culturas que ele marcou, no melhor sistema para elas (faixas A/B/C que giram, cereal no
  baixio quando houver, as datas do ZARC, o espaçamento). Um **controle grande de 2 lados [Seu jeito melhorado | O ideal]**; o lado
  "O ideal" mostra o plano com tudo o que sabemos (terra, baixio, maniva, ano passado, prioridade, cardápio do lugar).
- **"O que vale mais para você?" (Água · Renda · Solo · Um pouco de cada) fica dentro do lado "O ideal"**; cada toque redesenha o
  roçado e os benefícios na hora (sem nova chamada à API) e grava `prioridade` (mapa `INV` de `cenarios.js`: agua→garantir,
  renda→vender, solo→solo, plano→equilibrar). "Um pouco de cada" = o plano do núcleo (`r.plano`).
- O lado escolhido grava a nova chave `plano` ("" = melhorado, o padrão; "ideal"). Dinheiro e Relatório seguem essa escolha.
- **"O que você ganha"**: Hoje → Melhorado → Ideal, com números medidos e selados (seção 5): R$ no ano típico, R$ no ano de El Niño
  (2027), anos de quebra em 10, comida colhida (kg), forragem, nitrogênio que a leguminosa deixa (kg N), meses de chão coberto,
  a "ponte" da lagarta quebrada pelas faixas. Onde não dá para medir, diz que não mede (nunca inventa).
- **"Seu terreno em metros"** (D4): o terreno dele em escala com as medidas, os metros de cada faixa e o espaçamento.
- **Saem do meio da tela:** a linha "Mandioca (Parte A): tem maniva?" e o cartão do giro ("A terra repetiu milho…"). O efeito das
  respostas de Sua roça aparece dentro do plano, como um "por quê" curto da faixa (ex.: "A: começa com feijão; ali teve milho").
- Ficam: "Agora", calendário, "seu olho" (ponto 16), "Por que este plano" (vulnerabilidade, faixas, saúde do solo, nos "ver mais").
- Limites a 390 px: ≤ 3.600 px, ≤ 430 palavras à vista.

**D4. Terreno em metros e espaçamento (didático):** retângulo larg × comp em escala (sem resposta: quadrado do ha típico, dito como
SUPOSIÇÃO); cada faixa com largura em metros e comprimento; por faixa: nº de linhas, distância entre linhas e entre covas/plantas,
sementes por cova, quantidade de semente/maniva/muda para aquela área; e um **zoom de um pedaço de 5 m × 5 m** desenhando as linhas e
as covas no espaçamento certo. Números de `web/dados/agronomia.json` (seção 6), com a fonte.

**D5. Quanto rende (`/4`):** Hoje → Melhorado → Ideal com os mesmos números do "O que você ganha" (uma fonte só: `extras/ideal.js`);
as abas de prioridade saem daqui (o ideal mostrado é o da prioridade escolhida no Plano; uma linha diz qual e leva para mudar).
O que o ponto 6 (incerteza) precisava do "Se secar" vem em forma compacta: "em 8 de 10 anos parecidos você colhe pelo menos X" e,
num "ver mais", a grade de 10 roças. Culturas novas sem série de R$: dizer que o IBGE não tem a série no município (frases banidas
abaixo). Primário: "Ver o relatório →". Limites: ≤ 2.600 px, ≤ 300 palavras.

**D6. "Do espaço" vai para o mapa e o painel:** `web/painel.html` (painel "Roça Certa", que o globo mostra num iframe com
`?embutido=1`, e sozinho em `painel.html?cod=`) ganha o que o passo 1 mostrava: El Niño 2027, chuva e meses de chuva, solo hoje
(SMAP), tendências, satélite × pluviômetro, grades de cada satélite (harmonização), confiança dos dados, glossário, e o "E se
chover…" (ponto 13, vinha do "Se secar"). No zoom do mapa (`js/globo/camadas.js`/`mapa.js`), o cartão do município mostra os
números-chave dessas camadas. O embutido fica leve: o pesado em "ver mais" ou abas. O verde "Montar o plano do meu roçado" segue
para `roca.html#/<cod>/2`.

**D7. Relatório (`/5`, `passos/relatorio.js`):** "O plano do seu roçado": cabeçalho (município, data de hoje, tamanho larg × comp,
terra, baixio, plano escolhido e prioridade); **"O que fazer e quando"**: lista em ordem de data, com **datas exatas (dd/mm/aaaa)**,
de agora até dez/2027 (2028 e 2029 resumidos por ano): onde (Parte A/B/C, baixio, bordas), o quê, **como** (passo a passo curto:
preparo sem fogo, plantio com espaçamento, covas, sementes, profundidade, capina, cobertura, colheita, guardar semente), e a condição
quando houver (ex.: plantar só depois que a chuva firmar, os portões da agenda). Datas tiradas de `r.agenda` (barras de/ate, marcos,
janelas do ZARC em decêndios) — nunca inventadas. Depois: o desenho pequeno do roçado, a lista de materiais (sementes kg, manivas,
mudas), "Leve para o técnico" (de `leve_ao_tecnico.js`) e a frase do ponto 16. Primário: **"Mandar no WhatsApp"**
(`compartilhar(ctx)`); secundário: "Imprimir / salvar PDF" (`window.print()` com `@media print` claro, A4, ≤ 4 páginas).
Sem teto de palavras (é o detalhe), mas escaneável: datas à esquerda, uma linha de "o quê" e o "como" curto.

**D8. Fora desta rodada:** a dica do satélite para terra e baixio (proposta anterior, sem resposta do José), mudanças no núcleo
(`nucleo/motor.py`) e no servidor. Tudo no navegador, a partir do JSON de `/api/local`.

## 3. Regras de trabalho

- **Não reinicie nem pare o servidor** (`http://127.0.0.1:8090`, processo do orquestrador). Ele serve `web/` do disco: editou, recarregou.
  Ele recusa pedidos em paralelo sob carga: **use o JSON salvo** em `E:/campeonato-nasa/tmp/fluxo2/api/<cod>.json` (sem respostas)
  para testes no node; para respostas diferentes, um `curl --retry 3` por vez. No máximo **um Edge sem janela por agente** por vez.
- Ferramentas: `testes/ferramentas/print_url.py`, `percorrer_fluxo.py`, `erros_console.py`, `aceite_fluxo.py`, `teste_calculo.mjs`.
  Python: `MSYS_NO_PATHCONV=1 E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 ...`. Perfis do Edge e prints em
  `E:/campeonato-nasa/tmp/fluxo2/<seu-id>/` (o C: está quase cheio). Nunca mate python.exe nem msedge.exe em massa (só por PID).
- Para arquivo .py ou .mjs de teste, escreva com a ferramenta Write (heredoc no Bash estraga barras invertidas).
- **Edite só os arquivos que são seus nesta fase** (seção 7). Precisa de algo no arquivo de outro? Escreva no seu relatório
  (seção "pedidos ao integrador"); não edite.
- **Não faça commit.** Não mexa em `site-nasa-v2/` nem em `dados/financeiro_mun.json.bak`.
- `node --check` em todo JS que tocar. Sem erro no console nas telas que tocar (7 municípios: Quixadá 2311306, Crateús 2304103,
  Picos 2208007, Caicó 2402006, Petrolina 2611101, Arapiraca 2700300, Barreiras 2903201).
- `testes/ferramentas/teste_calculo.mjs`: `web/js/passos/dinheiro/calculo.js` **não muda**; Quixadá padrão segue Hoje R$ 2.480 /
  Melhor 4.190 / Ideal 4.360 no passo 4, salvo mudança de definição explicada no relatório.
- Frases banidas: "5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde", "qualquer terra",
  "sem preço aqui", "ainda não vende", "à frente de hoje em".
- Texto para agricultor de pouca leitura: frases curtas, palavras do lugar (roçado, baixio, maniva, tarefa, cova, carreira),
  número com unidade, nada de jargão na frente (o jargão vai no "o que é?" do glossário ou no balão do selo).
- Contrato do `ctx`, regras visuais e componentes: `web/js/passos/LEIA-ME.md`; casca: `web/js/roca.js`.
- Escreva o relatório em `analise/fluxo2/implementacao/<ID>.md`: o que fez, arquivos, como testou (com números), o que ficou
  faltando, pedidos ao integrador.

## 4. Preparo já feito pelo orquestrador

- `web/js/extras/culturas.js` (novo): `CULT` e `opcoesCultura` saíram de `hoje_ideal.js`, que agora importa e reexporta os dois
  (`export { CULT, igual, mexer, opcoesCultura }` continua). Cada entrada: `{ nome, serie?, icone, t, semRs?, motor }`, com
  `motor` = o nome no cardápio do núcleo (`"feijao"` → `"Feijão-caupi"`, `"sorgo"` → `"Sorgo forrageiro"`, `"palma"` → `"Palma
  forrageira"`, `"outra"` → `null`). Chaves novas que o B1 acrescentar seguem esse formato.
- JSON da API sem respostas dos 7 municípios + Piritiba (2924801) em `E:/campeonato-nasa/tmp/fluxo2/api/`.
  Campos úteis: `plano.faixas[]` ({parte, por_que, anos[3]: {cultura, tipo, texto}}), `plano.anos`, `agenda.linhas[]` ({parte,
  cultura, tipo, estacao, barras[]: {de, ate, tipo (preparo|risco|plantio|estimado|roca|colheita|pousio), rotulo}}),
  `agenda.culturas[]` ({cultura, plantar, colher, fonte, situacao} para as 18 culturas), `agenda.marcos`, `agenda.portoes`,
  `cardapio[]` ({cultura, situacao, risco20/30/40, aptidao...}), `financeiro`, `projecao`, `padroes` (Censo 2017).

## 5. Contrato do motor do ideal: `web/js/extras/ideal.js` (dono: A2; sem DOM, roda no node)

```js
// h = lerHoje(resp.hoje, r.padroes); ef = ctx.ef (área, baixio, etc., como roca.js monta); prioridade ∈ garantir|vender|solo|equilibrar
export function planoMelhor(r, resp, ef)            // → plano no formato de r.plano ({anos, faixas[{parte, por_que, anos[3]}], notas})
                                                     //   só com as culturas dele (CULT[k].motor), no melhor giro A/B/C (+ Baixio)
export function planoIdeal(r, resp, ef, prioridade)  // → idem; equilibrar = r.plano; garantir/vender/solo = as rotações de cenarios.js
export function beneficios(r, resp, ef, plano, tipo) // tipo ∈ hoje|melhor|ideal → { itens: [{ id, rotulo, valor, unidade, selo,
                                                     //   fonte }], rs: {...} }  (id: rs_tipico, rs_el_nino, quebra_10, comida_kg,
                                                     //   forragem_t, n_kg, meses_coberto, ponte_lagarta); valor null = não medido
export function comparar3(r, resp, ef, prioridade)  // → { hoje, melhor, ideal } cada um { plano, beneficios }
export function agendaDe(r, plano, ef)               // → linhas no formato de r.agenda.linhas ({parte, cultura, tipo, estacao,
                                                     //   barras[{de, ate, tipo, rotulo}]}) para o plano dado; para r.plano devolve
                                                     //   r.agenda.linhas sem mudar. Datas só de r.agenda.culturas[].plantar/colher
                                                     //   (ZARC) e das regras de preparo que a agenda do núcleo já usa.
export function escolhido(r, resp, ef)               // → { tipo: "melhor"|"ideal", prioridade, plano, linhas } (o que o Plano,
                                                     //   o Dinheiro e o Relatório mostram, pela chave `plano` e `prioridade`)
```
- `ef` é o que `efetivas()` de `roca.js` devolve (`ctx.ef`); a prioridade padrão é "garantir" em ano de alerta de El Niño (2027
  é) e "equilibrar" fora dele: o lado "O ideal" abre nessa prioridade e diz qual é.
- R$ e quebra: a conta de `passos/dinheiro/calculo.js` (sem mudar) e a de `hoje_ideal.js` (`comparar`), que já faz Hoje/Melhor/Ideal.
- Ponte da lagarta: `plantio/desenho.js` (`grade`, `espalhar`, `ehGram`, `LIMIAR_SITIO`).
- Coeficientes de benefício (N da leguminosa, palhada, forragem): `web/dados/agronomia.json` (seção 6, do A1), com fonte; se faltar,
  `valor: null`.
- O plano devolvido precisa desenhar em `plantio/desenho.js` (`montar`) e no `svgRocado` do `plantio.js` sem mudança de formato.

## 6. Contrato dos dados de agronomia: `web/dados/agronomia.json` (dono: A1)

```json
{ "meta": { "gerado": "...", "regra": "..." },
  "culturas": { "<nome do cardápio do núcleo>": {
      "entre_linhas_m": 1.0, "entre_covas_m": 0.5, "por_cova": 2, "plantas_ha": 40000, "semente_kg_ha": 20,
      "material": "semente|maniva|muda|raquete|estaca", "material_unidade": "kg|manivas|mudas|raquetes",
      "profundidade_cm": "3–5", "ciclo_dias": "90–110", "como": ["frase curta", "..."], "fonte": "Embrapa ..., ano, url" } },
  "operacoes": { "preparo_sem_fogo": { "como": ["..."], "fonte": "..." }, "capina": {...}, "cobertura": {...},
      "colheita": {...}, "guardar_semente": {...}, "adubacao_verde": {...} },
  "beneficios": { "n_kg_ha": { "Feijão-caupi": [min, max], "...": [..] }, "palhada_t_ha": {...}, "forragem_t_ms_ha": {...},
      "fonte": { "n_kg_ha": "...", "...": "..." } } }
```
As 18 culturas do cardápio (seção 2, D2) com espaçamento **de sequeiro no semiárido** (Embrapa Semiárido, Embrapa Meio-Norte,
Embrapa Mandioca e Fruticultura, IPA, EMPARN, Embrapa Algodão, sistemas de produção). Faixa quando a fonte der faixa; o valor
central no campo numérico. Toda linha com fonte (título, ano, link quando houver). Nada sem fonte.

## 7. Fases e donos de arquivo

| Fase | ID | Agente | Arquivos que são seus |
|---|---|---|---|
| 1 | A1 | Agrônomo (pesquisa) | `web/dados/agronomia.json` (novo) |
| 1 | A2 | Motor do ideal | `web/js/extras/ideal.js` (novo), `web/js/extras/hoje_ideal.js`, `web/js/extras/cenarios.js` (só exportar/reusar os construtores; a interface dele é do C3 na fase 2), `testes/ferramentas/teste_ideal.mjs` (novo) |
| 1 | B1 | Sua roça | `web/js/passos/perguntas.js`, `web/css/passos/perguntas.css`, `web/js/extras/area.js` (+ css dele), `web/js/extras/culturas.js`, `web/js/extras/historico.js` (+ css dele) |
| 1 | B2 | Casca | `web/js/roca.js`, `web/roca.html`, `web/css/quadra.css`, `web/js/passos/LEIA-ME.md`, `web/js/passos/relatorio.js` (só um esqueleto que renderiza um título, para a rota existir; o C4 escreve o conteúdo) |
| 1 | B3 | Mapa e painel | `web/painel.html`, `web/js/globo/*.js`, `web/css/globo/*.css`, `web/index.html`, `web/js/passos/lugar.js` (aposentar ou reaproveitar), `web/js/extras/{tendencias,satelite_chao,harmonizacao,confianca,glossario,cenario_chuva}.js` e os css deles (só o que precisar para rodar fora da jornada) |
| 1 | C1 | Terreno e espaçamento | `web/js/passos/plantio/desenho.js` (retângulo larg × comp, compatível com o formato de hoje), `web/js/extras/terreno.js` (novo, `export default { render(el, ctx, { plano, ano }) }`), `web/css/extras/terreno.css` (novo) |
| 2 | C2 | O plano | `web/js/passos/plantio.js`, `web/js/passos/plantio/calendario.js`, `web/css/passos/plantio.css` |
| 2 | C3 | Quanto rende | `web/js/passos/dinheiro.js`, `web/js/passos/dinheiro/*.js` exceto `calculo.js`, `web/css/passos/dinheiro.css`, `web/js/extras/hoje_ideal.js` (interface), `web/js/extras/cenarios.js` (interface) |
| 2 | C4 | Relatório | `web/js/passos/relatorio.js`, `web/css/passos/relatorio.css` (novo), `web/js/extras/leve_ao_tecnico.js` |
| 3 | I | Integrador | todos (cola, conflitos, `aceite_fluxo.py`, `percorrer_fluxo.py`, `analise/fluxo2/00_FLUXO_V2.md`, `PLANO_INTEGRACAO.md`) |
| 4 | R1–R3 | Revisores | nenhum (só leem, medem e relatam) |
| 5 | X, Y | Correção | X: Sua roça, casca, mapa e painel; Y: plano, terreno, ideal, dinheiro, relatório |
