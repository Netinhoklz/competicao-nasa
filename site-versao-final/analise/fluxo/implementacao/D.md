# Construtor D: Se secar e técnico (14/11/2026, 23:56)

Ordem de serviço: `analise/fluxo/00_FLUXO_FINAL.md`, seção 7, dono D. Mexi só nos 7 arquivos do D:

| Arquivo | Linhas |
|---|---|
| `web/js/passos/seguranca.js` | +51 / −31 |
| `web/css/passos/seguranca.css` | +24 / −2 |
| `web/js/extras/leve_ao_tecnico.js` | +50 / −9 |
| `web/js/extras/voce_decide.js` | +1 / −1 |
| `web/css/extras/voce_decide.css` | +17 / −7 |
| `web/js/extras/cenario_chuva.js` | +7 / −7 |
| `web/css/extras/cenario_chuva.css` | +24 / −2 |

`node --check` passa nos 4 JS.

## 1. O que fiz

### D1. `seguranca.js`: ordem nova
- **Ordem** (`seguranca.js:430-438`): abertura → "2027, cada cultura" → `blocoCenario` ("E se chover…") → `blocoPortoes` → `U.extra("historico", {modo: "memoria"})` (sem `linkPergunta`, então não vai ao passo 2) → `U.extra("leve_ao_tecnico")` → `blocoLimites`.
- **Abertura** (`:177-191`): o kicker passa a ser "Se secar" e a frase de apoio é "Olhe a terra em 19/mar e 30/abr e decida com o técnico.". Onde os portões não valem (`agenda.portoes === false`: Petrolina, Arapiraca, Barreiras, Piritiba), a frase é "Olhe a terra antes de plantar e decida com o técnico.". O h1 e o `.eco` não mudaram.
- **"2027, cada cultura"** (`bloco2027`, `:193-214`):
  - 1 linha por cultura do plano com série: ícone, nome ("Feijão (caupi)" quando o plano usa caupi), "quebra em **X de 10**" e `dezRocas(d.anos["2027"].quebra)`. Com 0 ou 10, a linha diz "quase nunca quebra" ou "quase sempre quebra".
  - 1 selo PROJEÇÃO no rótulo (com o selo do E, aparece "PROJEÇÃO · IBGE").
  - O 1º "X de 10" leva o `termo("em_dez")` ("o que é?"), que antes ficava no cartão.
  - Embaixo vem a nota "Quebrar = colher menos da metade do normal daqui." e `U.verMais(…, "Cada cultura, 2027 a 2029")`, com:
    - "Não é previsão…" (a frase que saiu da abertura);
    - o aviso de lavoura grande com o "seu olho" (ele saiu da frente: com ele, Barreiras teria 3 olhos à vista);
    - `reguaAnos`, os cartões completos e as fichas "sem série" (sorgo, palma).
- **`blocoHoje`** (`:216-235`): o bloco inteiro foi para `U.verMais(…, "Ver os detalhes de hoje")`, sem `<details>` dentro de `<details>`. Ele fica no grupo final, antes dos 28 anos (`blocoLimites`, `:397-399`).
- **Mar** (`:246`): "mar quente, acima do recorde" virou "o mar mais quente de ago–out desde 1950".
- **Textos e selos menores:**
  - `:269`: "quebra em 6 em 10" virou "quebra em 6 de 10" nos cartões do ver mais.
  - `:36`: a fonte dos portões passou a citar "chuva GPM IMERG (NASA) × colheita IBGE PAM". Com o `selo()` do E, o rótulo fica "MEDIDO · NASA GPM". É fiel ao método, que usa a chuva IMERG desde 1/fev.
  - A frase "A chuva que cair desde 1º de fevereiro…" passou para o "Ver como medimos os portões".
  - `:382`: o ver mais da sobreposição se chama "Ver cada ano: chuva, solo e colheita".
  - `:420`: `titulo: "Se secar"`.
- **CSS** (`seguranca.css:9-28`):
  - estilo das linhas de 2027 (grade de 10 com 12 px a ≤ 400 px);
  - os "ver mais" do passo ficam com menos respiro, mas a linha de cima e o alvo de 44 px continuam;
  - `.seg-bloco` com 26 px de margem no celular;
  - saiu `.seg-apoio`, que ficou órfão.

### D2. `cenario_chuva.js`
- **Abertura em 100%** (`:306`): `tela.x ??= 100`. O chip "anos de El Niño" continua a 1 toque (`:114`). O comentário do topo foi atualizado (`:9`).
- **Frase** (`:155`): o teste de `x === 100` vem antes. Assim a frase diz "Com a chuva normal" mesmo num município cujos anos de El Niño deram 100% (critério 17).
- **Linha "Aqui…"** (`:161-162`): ficou mais curta ("Aqui, de N anos com chuva assim, o milho quebrou em K"). O selo passou a citar "chuva GPM IMERG…", e por isso aparece "MEDIDO · NASA GPM" à vista dentro do "E se chover…".
- **Legenda dos pontos** (`:116`): ficou mais curta ("milho quebrou · não quebrou · El Niño forte").
- **CSS do celular** (`cenario_chuva.css:117-140`, ≤ 760 px):
  - o número fica ao lado do rótulo;
  - **1 linha por cultura**: nome · colheita · "X em 10 quebram", como no wireframe ("milho … sacos/ha · caupi … · mand. …");
  - no celular saem o "normal X" e a grade de 10 por cultura, porque as grades já estão à vista em "2027, cada cultura";
  - chips com 44 px.

  No desktop nada mudou.

### D3. `leve_ao_tecnico.js`
- **`export async function compartilhar(ctx)`** (`:137-150`):
  - monta o mesmo `texto()` do "Copiar o texto";
  - tenta `navigator.share({text})`;
  - se a pessoa fechar a janela (`AbortError`), para ali;
  - senão abre `window.open("https://wa.me/?text=…")`;
  - se o navegador bloquear a janela, chama `copiar()` e escreve o aviso no bloco (`avisar`, `:130-135`, que também rola até o aviso).
  - Devolve `"share" | "cancelou" | "wa.me" | "copiou" | "falhou"`.

  O A já chama `compartilhar` pelo botão verde, e eu conferi o caminho completo.
- **Botões** (`:181`): "Copiar para o WhatsApp" (verde) virou `.botao.secundario` "Copiar o texto". No bloco não sobrou nenhum botão verde.
- **Água** (`:153, :175-176, :193`): chips "Barreiro ou açude" e "Poço ou irrigo", com `ctx.set({agua})`. Tocar de novo no chip aceso volta para `""` (só a chuva). A cisterna saiu dos chips, mas `FICHA.agua.cisterna` ficou para links antigos.
- **Garantia-Safra** (`:177-178`): "paga com perda de 40% ou mais; até 5 ha o tamanho cabe; renda da família e adesão do município: confira no sindicato." Com `ef.ha > 5`, o meio vira "acima de 5 ha o tamanho não cabe", para não dizer "cabe" sem ressalva.
- **Preço da raiz** (`:65-70`): a pergunta usa o rótulo da opção escolhida, por exemplo "A raiz vale R$ 0,84/kg (comum no CE) na casa de farinha?". Os rótulos são "daqui", "comum no UF" e "baixo no UF". O município com `origem_municipio: "UF"` (Caicó) recebe "comum no RN".
- **Para caber na tela** (decisão minha, ver seção 2):
  - ficam à vista as **3 primeiras perguntas** e o resto vai para "Ver as outras N perguntas" (`:166-174`; imprimir, copiar e WhatsApp levam todas);
  - "Aqui, só 7 de 100 roças de família recebem orientação técnica" foi para o "Onde achar quem confira" (`:185`).
- **CSS** (`voce_decide.css:46, 56-79`):
  - chips de água lado a lado (2 colunas no celular);
  - linha do Garantia-Safra com o ícone de escudo;
  - Imprimir e Copiar lado a lado, sem quebrar;
  - saiu `.lt-sub`, que ficou órfão.

### D4. `voce_decide.js`
- **`OLHOS.terra`** (`:26`): "Na dúvida, aperte um torrão molhado: areia esfarela, barro gruda." São 10 palavras. Já tinha ≤ 12; troquei "úmido" por "molhado", como no wireframe.
- **`voce_decide.css`, celular** (`:78-79`): saíram as regras que punham a frase da moldura como 1ª linha da barra de baixo (2 linhas). Entrou `.nav-baixo .moldura-decide { display: none; }` a ≤ 760 px, que é a regra da seção 5. Sem isso o meu CSS, carregado depois do `quadra.css`, poderia vencer o "moldura escondida" do A. Fora da `.nav-baixo` a classe não é afetada (o rodapé do A continua aparecendo).

## 2. O que não fiz ou não alcancei

- **Critério 6 (Se secar ≤ 2.400 px e ≤ 300 palavras): não passa.** Medido a 390×844 com todo "ver mais" fechado:

  | Município | Altura (px) | Palavras |
  |---|---|---|
  | Quixadá | 3.280 | 404 |
  | Crateús | 3.280 | 403 |
  | Picos | 3.206 | 397 |
  | Caicó | 3.070 | 386 |
  | Petrolina | 3.132 | 390 |
  | Arapiraca | 3.172 | 392 |
  | Barreiras | 3.370 | 418 |
  | Piritiba | 3.247 | 399 |

  No começo eram 4.411 px e 468 palavras.
  - Altura por bloco em Quixadá: abertura 220, 2027 328, "E se chover…" 709, portões 211, memória (C) 404, técnico 687, ver mais do fim 205. Somam 2.764, mais margens, o topo e o rodapé/barra do A.
  - Só com o que a seção 7 manda deixar à vista ("E se chover…" aberto, portões, memória, técnico com chips e Garantia-Safra, rodapé), o piso fica perto de 2.900 px.
  - Cerca de **56 das palavras são as opções do `<select>` "outro ano" da memória (C)**, porque `innerText` conta os 28 anos de cada select. Sem elas, Quixadá fica em cerca de 348.
- **Não juntei os 4 "ver mais" do fim** (detalhes de hoje, 28 anos, o que não dá para projetar, quanto acertou). A seção 7 diz "limites e métodos (como hoje)". Juntar daria cerca de −100 px.
- **Não mostrei 0 perguntas** no técnico (só o número e os botões). O wireframe mostra caixas à vista. Daria cerca de −200 px.
- **Caicó** (Mandioca sem `anos` na projeção) continua com o h1 antigo "Segurança de cada colheita. / Sem série do IBGE aqui para projetar." e a linha "O IBGE não tem série suficiente…". A lógica é a de antes; só o nome "Segurança" ficou velho.
- **Código órfão:** nenhum novo. `chuvaElNino` continua em uso (chip). `freq` e `perspectiva` continuam em uso. A página `web/teste/cenario_chuva.html` ainda diz no comentário que abre no El Niño (arquivo de teste, não é meu).

## 3. Pedidos ao integrador

1. **Critério 6 do Se secar:** decidir se o teto sobe para cerca de 3.000 px e 350 palavras ou o que mais vai para o ver mais. Candidatos, por ganho:
   - perguntas do técnico só no ver mais (−200 px);
   - régua de pontos do "E se chover…" no ver mais (−90);
   - juntar os 4 ver mais do fim em 2 (−100);
   - um "outro ano" só na memória (C, −80);
   - h1 menor no celular (A, −40).
2. **C (memória):** o `<select>` "outro ano" infla a contagem de palavras do script de aceite em cerca de 56. Duas saídas: preencher as `<option>` só ao focar, ou o script descontar `select`.
3. **A (barra):** a 390 px, "Mandar no WhatsApp" quebrou em 2 linhas numa das medições (fonte Fraunces 18 px), e a barra passou de 64 px. Na última medição já estava em 1 linha; vale conferir.
4. **A:** o "Outro lugar" pequeno do fim já está no rodapé do A, por isso **não** pus outro no passo 5 (tirei o meu para não repetir).
5. **E:** com o `selo()` novo, a régua de 2027 (no ver mais) mostra "PROJEÇÃO · NOAA" e os cartões "PROJEÇÃO · IBGE". Está correto, só aviso.
6. **Servidor:** com os 5 construtores ao mesmo tempo, o `servidor.py` recusou conexões algumas vezes (`ERR_CONNECTION_REFUSED` em CSS e API) e depois voltou sozinho. No I3, repetir a medição antes de culpar o código.

## 4. Como testei

- **Script próprio** `E:/campeonato-nasa/tmp/fluxo_novo/D/medir.py`. Ele abre o Edge sem janela a 390×844, roda o script da seção 8 (mais o fundo das linhas de 2027, o topo do "E se chover…", `ccPct`, o verde no bloco do técnico e a altura por bloco), coleta os erros do console e tira um print fechado e outro com todos os `details` abertos (`lateral`).
- **Resultado nos 8 municípios** (7 + Piritiba):
  - zero erro no console;
  - `primarios` = 1 e nenhum verde no bloco do técnico;
  - `contadores` = 0, `nDeM` = false;
  - `lateral` = false, também com tudo aberto;
  - `olhos` = 2;
  - `nasa` = true, com "MEDIDO · NASA GPM" à vista;
  - `proibidas` = [], `selosPequenos` = 0, `summaryBaixo` = 0;
  - "E se chover…" em 100% com "Com a chuva normal…";
  - fundo das linhas de 2027 ≤ 688 px e título do "E se chover…" ≤ 815 px (critério 17: ≤ 900).
- **Critério 18:**
  - O espião em `navigator.share` registrou a chamada pelo `#avancar` do A, com o texto de 585 caracteres.
  - Sem share e com `window.open` bloqueado, o botão copiou e o aviso disse "Copiado. Cole no WhatsApp.".
  - `AbortError` para sem abrir janela. `NotAllowedError` abre `wa.me` (`teste_compartilhar.js` e `teste_botao.js` na mesma pasta).
- **Água:**
  - "Barreiro ou açude" gravou `agua=barreiro`, acendeu o chip e trouxe a pergunta "O barreiro salva o milho na floração?".
  - "Poço ou irrigo" gravou `agua=irriga`. Tocar de novo limpou o `agua`.
  - `history.length` não cresceu, porque o `location.replace` faz a troca no lugar.
- **Páginas de teste:** `web/teste/cenario_chuva.html` e `web/teste/voce_decide.html` passaram no `erros_console.py` sem erro.
- **Desktop:** a 1280 px, conferido no print (`desk_q5.png`).
- **Prints** em `E:/campeonato-nasa/tmp/fluxo_novo/D/`:
  - `m<cod>_fechado.png` e `m<cod>_aberto.png` dos 8 municípios;
  - `q5_parte0..2.png` (Quixadá em 3 partes);
  - `m2903201_cc.png` (Barreiras, colheita em % sem sobrepor o nome; o defeito apareceu e foi corrigido);
  - `desk_q5.png`.
