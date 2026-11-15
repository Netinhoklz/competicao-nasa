# Construtor E: "Do espaço" e selo NASA (14/11/2026, 23:58)

Arquivos mexidos (só os meus): `web/js/comum.js`, `web/js/passos/lugar.js`, `web/css/passos/lugar.css`, `web/js/extras/tendencias.js`,
`web/css/extras/tendencias.css` e `web/js/extras/glossario.js`. Cópias de antes em `E:/campeonato-nasa/tmp/fluxo_novo/E/*.orig`.

## Resultado em números (390×844, todo "ver mais" fechado, script da seção 8)

| | Antes (Quixadá) | Depois |
|---|---|---|
| Altura | 4.550 px | 2.697 (Quixadá, Picos) · 2.736 (Caicó) · 2.744 (Arapiraca, Barreiras) · 2.754 (Petrolina, Piritiba) · 2.767 (Crateús). Teto: 2.800 |
| Palavras | 538 | 288 a 303. Teto: 320 (meta 250, ver o pedido 3) |
| Botões verdes à vista | 2 | 1 (o da barra: "Ver o meu plano →", do roca.js do A) |
| Frases proibidas | "5 perguntas", "muito forte" | nenhuma |
| "NASA" no texto | não | sim, nos 8 municípios |
| Selo < 11 px / summary < 44 px | 19 / 0 | 0 / 0 (o 11 px é do quadra.css do A) |
| Rolagem de lado | não | não, com os "ver mais" fechados e com todos abertos (390 = 390) |
| "Seu olho" à vista | 2 | 1 |
| Erros no console | — | nenhum nos 8 municípios |

## O que fiz

### 1. Selo com a fonte (`comum.js:23-41`)
- `fonteCurta(fonte)` (`comum.js:29`), exportada: tira a fonte curta do próprio texto da fonte, com as tabelas `CURTA_NASA` (`:25`) e
  `CURTA_OUTRAS` (`:27`), e devolve `NASA SMAP`, `NASA GPM` (GPM ou IMERG), `NASA POWER`, `NASA GRACE`, `NASA MODIS`, `NASA VIIRS`,
  `ECOSTRESS`, `NOAA` (ONI ou NOAA), `ZARC`, `CONAB`, `IBGE` (PAM, IBGE ou Censo) e `FAO` (GAEZ). Todas têm até 10 letras.
- `selo()` (`:36`): MEDIDO e PROJEÇÃO viram `MEDIDO · <curta>`, e SUPOSIÇÃO fica sem fonte curta. A assinatura é a mesma, `title`
  continua, e entram `data-fonte="<fonte>"` e `tabindex="0"`. O toque é do A, e foi conferido: tocar no selo do solo abre o balão
  "NASA SMAP L4, 30 dias até…".
- **Desvios da letra da ordem de serviço (decidi assim; o integrador pode mudar):**
  - As missões da NASA têm prioridade sobre as outras fontes. Ao pé da letra ("a 1ª que aparecer no texto"), a fonte que o A usa na
    faixa de Sua roça (`"ONI NOAA; solo NASA SMAP L4"`) daria `NOAA`, e o desenho da seção 3.1 pede `NASA SMAP`. Entre as fontes que
    não são da NASA vale a 1ª do texto, e por isso o herói do passo 4 sai `PROJEÇÃO · IBGE`, como no desenho, e não `CONAB`.
  - Quando o texto cita 3 ou mais missões, o rótulo fica só `NASA`. É o caso das tendências: "NASA (IMERG, SMAP, MODIS, POWER, GRACE)"
    daria `NASA GPM`, o que esconde as outras quatro.
  - Entrou `NASADEM`, que é da NASA e aparece no selo do declive (`vulnerabilidade.js:216`). ERA5 e FUNCEME não têm fonte curta e
    ficam só `MEDIDO`.
  - `data-fonte` e `tabindex` só entram quando a fonte não está vazia. Assim um selo sem fonte não abre um balão vazio.
- Conferido com 20 fontes reais do código (script em `E:/campeonato-nasa/tmp/fluxo_novo/E/teste_selo.mjs`).

### 2. Passo "Do espaço" (`lugar.js`)
- `titulo: "Do espaço"`, `curto: "Espaço"` (`:140-141`). O kicker é "Do espaço" (`:144`).
- Saíram o CTA "Responder 5 perguntas…" e o "Pular…" (as antigas `:148-149`). Também saíram as regras `.cta` e `.pular` de
  `lugar.css`, que ficaram sem uso.
- "El Niño muito forte" → "acima do normal" no indicador do mar (`:84`). "El Niño forte" já está na manchete logo acima, e foi o
  rótulo único pedido na seção 5. O `texto_oni` do motor, que diz "muito forte", ficou só no "ver mais".
- A régua foi para `U.verMais(…, "O ano da chuva aqui")` (`:42-47`), com o selo na legenda e o "satélite × pluviômetro" dentro dela.
  Ela mora no painel de origem (`:132`).
- Culturas (`:95-123`): à vista ficam as 6 primeiras, só como ícone + nome + situação (o desenho da seção 3.1 pede "6 ícones"). Em
  "Ver todas as N" (`:123`) vão as N culturas com a época de plantar, a legenda (com o "o que é?" do ZARC), o "seu olho" das datas
  estimadas, "Não servem aqui" e a tabela técnica. O texto "qualquer terra" foi trocado pela frase da ordem de serviço (`:111`).
- Linha "Quanto o cálculo já acertou → Se secar" com `ctx.link(5)` (`:135`, estilo em `lugar.css:46-51`, 48 px de alvo).
- Ordem (`:144-153`): El Niño → indicadores → tendências → culturas → confiança → origem (régua, de onde vêm os dados, glossário,
  acertou).
- Feito além da lista para caber nos 2.800 px e 320 palavras:
  - El Niño (`:63-70`): as barras de cada ano e o "Pelo acaso seriam 3 em 10…" foram para "Ver cada El Niño forte". O selo foi para o
    fim da manchete, e a manchete ficou mais curta: "El Niño forte em 2027: nos anos assim, a chuva veio fraca em 7 de 10 municípios do
    Ceará." O `viewBox` das barras cresceu para os rótulos de 10 em 10 caberem (`:56`).
  - Os textos de baixo dos indicadores ficaram mais curtos (`:84-91`).
  - Saiu o painel "Dá para plantar agora", que não está na ordem da seção 7. O "Agora:" do Plano (C) cobre isso, e são 106 px a menos
    em Barreiras.

### 3. `lugar.css`
- `.enso` sem grade, porque as barras foram para o "ver mais" (`:2-3`). O rótulo dos indicadores pode quebrar (`:11`), senão o selo
  maior apertava "A chuva chega" em 3 linhas no desktop. No celular, o selo dos indicadores tem `letter-spacing: .04em` (`:82`) para
  "MEDIDO · NASA SMAP" caber no cartão de 2×2.
- Cartão da cultura no celular em 3 linhas, com o ícone ao lado (`:56-60`).
- "Ver mais" mais juntos neste passo (`:73-74`). O alvo de 44 px continua (ver o pedido 1).
- Confiança no celular: os motivos da frente ficam escondidos (`:84`), mas estão todos no "Ver por quê" do próprio bloco (`confianca.js`
  monta `todos` com os mesmos motivos). O desenho da seção 3.1 pede "Confiança dos dados: alta · por quê".
- Saiu a fileira de deslizar das tendências (antigas `:64-67`).

### 4. Tendências
- `tendencias.css:50-70`: a ≤ 420 px, `tend-grade` vira grade de 2 colunas sem rolagem de lado. No cartão estreito, o número fica em
  cima do gráfico.
- No celular, o bloco tem 1 frase só (`.tend-frase-bloco`, `tendencias.js:157` e `:223-225`): é a da 1ª série que está do lado ruim,
  na ordem da manchete, e ela muda junto com o ano tocado. É a regra "no máximo 1 frase por bloco". No desktop, cada cartão continua
  com a sua frase.
- Ajustes de texto:
  - o chip perde o "desde N:" no celular (`:97`; a data continua no `title`);
  - "em 2026" passou a "2026" (`:137`);
  - "Toque para ver o ano." (`:207`);
  - "O satélite vê a região; a sua roça confirma ou corrige." (`:208`).
- O JSON das séries tenta de novo uma vez e não guarda a falha (`tendencias.js:10-17`). Num teste, o servidor recusou pedidos durante
  uma rajada e o bloco ficou "não carregaram".

### 5. Glossário (`glossario.js`)
- `instalar()` não baixa mais o JSON (`:236`). O balão já pedia o JSON ao abrir e redesenhava com o exemplo, e a lista de "O que quer
  dizer cada palavra?" é montada e baixa o JSON só quando abre (`:262-270`).
- Conferido: no passo 1 há 0 pedidos de `glossario_mun.json` antes do toque e 1 depois. O balão do veranico traz "Em Quixadá, em 7 de
  cada 10 anos…".

## O que não fiz e por quê
- **A linha "Quanto o cálculo já acertou" leva ao topo do passo 5, não ao "Ver quanto este cálculo já acertou".** Para levar até lá,
  o passo 5 (D) precisaria de uma âncora.
- **"Do espaço" não ficou abaixo da meta de 250 palavras.** Ficou em 288 a 303, dentro do teto de 320. Os 8 selos à vista somam cerca
  de 30 "palavras" (ver o pedido 3).
- **Não mexi em `confianca.js`, `harmonizacao.js` nem `satelite_chao.js`, que não têm dono.** Só escondi os motivos repetidos da
  confiança no celular, pelo CSS do meu passo.

## Pedidos ao integrador
1. **quadra.css (A):** com `summary { min-height: 44px }`, a margem `details > summary { margin: 8px 0 }` faz cada "ver mais" ocupar uns
   85 px. Sugiro `details.ver-mais > summary { margin: 0 }` para todos. No meu passo isso já está em `lugar.css:73-74`, e foram 7
   "ver mais" × 30 px.
2. **quadra.css (A):** `.ind .ind-rot { flex-wrap: wrap; }` para todos. O selo agora é mais comprido e não quebra, e em outro passo
   que use `ind()` com selo o rótulo fica espremido no desktop. Hoje isso só está em `lugar.css:11`.
3. **Palavras:** o script da seção 8 conta `MEDIDO · NASA GPM` como 4 palavras. Os passos perto do teto ganham cerca de 3 por selo
   à vista. Na minha medição, Se secar está em 403 palavras e 3.276 px (D).
4. **Fontes dos selos:** para sair `· NASA …`, o texto da fonte precisa ter o nome da missão (SMAP, GPM/IMERG, POWER, GRACE, MODIS,
   VIIRS, ECOSTRESS, NASADEM). Conferido em Sua roça (`MEDIDO · NASA SMAP`) e em Se secar (`MEDIDO · NASA GPM`,
   `PROJEÇÃO · NASA GPM`).
5. **Servidor:** com os 5 construtores testando ao mesmo tempo, apareceram `ERR_CONNECTION_REFUSED` em `css/passos/plantio.css`,
   `dinheiro.css` e `glossario.js`. Uma rodada de Quixadá falhou por isso, e a repetição passou limpa. Não é defeito do código, mas
   convém rodar o aceite final sem testes paralelos.
6. **LEIA-ME (I5), linha do passo 1:**
   - tendências em grade de 2 colunas no celular, com 1 frase por bloco;
   - régua em "O ano da chuva aqui" (ver mais);
   - glossário com o JSON baixado sob demanda;
   - regra da fonte curta do selo, com `data-fonte`/`tabindex` só quando há fonte;
   - `fonteCurta` exportada por `comum.js`.
7. Nenhum código órfão novo meu. `teste/tendencias.html` e `teste/glossario.html` continuam funcionando, sem erro no console.

## Como testei
- `node --check` nos 4 JS. `node testes/ferramentas/teste_calculo.mjs` deu saída idêntica a
  `E:/campeonato-nasa/tmp/base_fluxo/base_calculo.txt`.
- `E:/campeonato-nasa/tmp/fluxo_novo/E/medir.py`: Edge sem janela a 390×844 roda o script da seção 8 com os "ver mais" fechados, mais a
  lista dos selos à vista e os elementos além da largura. Depois abre todos os `details` e mede a rolagem de lado, e junta os erros do
  console. Rodou nos 7 municípios + Piritiba, e os números estão na tabela do topo.
- Prints a 390 px:
  - `E:/campeonato-nasa/tmp/fluxo_novo/E/final_<cod>_1.png` (8 municípios);
  - `aberto_2311306_1.png`: tudo aberto, conferidos as barras do El Niño, as culturas com datas, a régua, o glossário e as grades;
  - `antes_2311306_1.png`.
  
  Também a 1.280 px (`desk_1280.png`) e a 600 px (`tab_600.png`).
- Toque no selo: abre o balão do A com a fonte. Link "Se secar" = `#/2311306/5`.
