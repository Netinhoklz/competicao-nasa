# X (Correção: Sua roça, casca, mapa e painel): rodada 2, fase 5 (15/11/2026)

Corrigi os 7 achados do meu grupo: 3 médios, 3 baixos baratos e o achado 5, que cruza Sua roça, a casca e o Relatório.
O 6 (o peso do `municipios_ne.json` no painel embutido) ficou de fora, e o motivo está no item 6.

Editei só os meus arquivos. O `comum.js` (`U.ha`) não está na minha lista. Por isso a regra nova de área ficou local em
`perguntas.js` e `roca.js`, e a troca no `U.ha` vai como pedido ao integrador.

Não reiniciei o servidor, não fiz commit e não matei processo nenhum. Usei um Edge por vez, com perfis e prints em
`E:/campeonato-nasa/tmp/fluxo2/X/`.

## 1. Achado por achado

| # | Achado | Situação | O que mudou |
|---|---|---|---|
| 1 | 20 × 20 m aparecia como "0 ha" e 30 × 50 m como "0,2 ha" em Sua roça | **corrigido** em Sua roça e na ficha; o cabeçalho do Relatório é do Y (pedido 1) | `areaTxt` em `perguntas.js` e `roca.js`, com a regra do `haTxt` de `terreno.js`: abaixo de 0,1 ha, a área sai em m²; abaixo de 1 ha, com 2 casas; de 1 ha para cima, o `U.ha` de sempre. Exemplos: 20 × 20 m → "= 400 m² · ≈ 0,1 tarefa"; 30 × 50 m → "= 0,15 ha · ≈ 0,5 tarefa"; 5 × 5 m → "= 25 m² · menos de 0,1 tarefa". |
| 2 | Não dava para saber qual lado é a largura e qual é o comprimento, e o placeholder parecia um valor | **corrigido** | O 1º campo diz "largura", com uma seta de lado (âmbar). O 2º diz "comprimento, morro abaixo", com uma seta para baixo (azul, como "A ÁGUA DESCE ↓" no Plano). Cada campo tem `title` e `aria-label` com a frase inteira ("do alto até embaixo, para onde a água da chuva desce"). O placeholder virou "ex.: 101" em itálico de 14 px. Na aba "Passos" de "em tarefas ou passos" (`area.js`), a ordem também ficou largura × "Comprimento, morro abaixo", e o retângulo põe o comprimento na vertical, como no Plano. |
| 3 | A pergunta da maniva aparecia sem dizer por quê para quem não planta mandioca | **corrigido** | Quem não planta mandioca vê "Se for plantar mandioca, tem maniva? O plano daqui usa mandioca.", com Tenho · Não tenho · Não sei. "Já está plantada" só aparece se ele planta mandioca ou se já tinha marcado. Quem planta mandioca vê "Tem maniva para plantar mais? A rama da mandioca.", com as 4 respostas. |
| 4 | O painel tinha dois verdes cheios, e o "Milho quebra 6 em 10" do cartão não dizia em que anos | **corrigido** no painel e no cartão; o rótulo do Plano é do Y (pedido 2) | A aba acesa do painel ficou verde translúcido com borda verde (`rocacerta.css`). No cartão do mapa: "Milho em 2027 · quebra 6 em 10" (`camadas.js`). O rótulo e o valor quebram a linha no celular (`.cn.longo` em `painel.css`), em vez de cortar em "Milho em 20…". |
| 5 | Um roçado pequeno quebrava o tamanho em todas as telas | **corrigido** na casca e em Sua roça; ainda falta o motor (pedido 3) | (a) `txtHa` grava com 4 casas: 5 × 5 m → `ha=0.0025` (antes, 0.01). (b) Em `medidas()` (`roca.js`), as chaves `larg` e `comp` valem sempre e o `ha` sai delas. A tolerância de ± 5% fica só para a medida de `area_un` de link antigo. (c) `efetivas()` guarda `ha` com 4 casas. `baixio_ha` só passa a 4 casas abaixo de 0,1 ha, para que as contas de R$ do padrão não mudem. (d) A ficha mostra "5 × 5 m" e, sem medidas, a área com `areaTxt`. (e) Em "em tarefas ou passos", uma medida em passos grava o `ha` tirado dos metros. |
| 6 | O painel embutido baixa os 430 KB do `municipios_ne.json` | **não corrigido** | O `rocacerta.js` usa a lista inteira: a datalist da busca e a comparação com os outros municípios (`cods`, `D.m[c]`). O globo não tem esse arquivo para emprestar. Um JSON por UF seria um arquivo novo em `web/dados/`, que não é meu. Além disso, o servidor manda `Last-Modified`, então do 2º município em diante o navegador recebe um 304, sem os 430 KB. O achado não bloqueia a entrega. |
| 7 | "Banana: não é indicado aqui." | **corrigido** | O aviso agora diz "Fora do indicado aqui: banana." e "Fora do indicado aqui: mandioca.". Com mais de uma cultura: "Fora do indicado aqui: milho e banana.". O selo e a fonte não mudaram. |

Atualizei o `LEIA-ME.md`: o `ctx.ef` (a regra de `larg`, `comp` e `ha` com 4 casas), a linha do tamanho e a da maniva em Sua roça,
o aviso e o cartão do mapa.

## 2. Arquivos

- `web/js/passos/perguntas.js`: `txtHa` com 4 casas; `areaTxt` e `tarefasTxt`; os rótulos e as setas dos metros; o placeholder
  "ex.: N"; a maniva em 2 versões; o aviso "Fora do indicado aqui"; o `ha` de uma medida em passos tirado dos metros.
- `web/css/passos/perguntas.css`: as setas (`.sr-m-seta`), o rótulo em flex e o placeholder em itálico de 14 px. O arquivo é de Sua
  roça (B1). Ele não está escrito na minha lista desta fase, mas Sua roça é minha, e o Y não mexe nele.
- `web/js/extras/area.js`: na aba Passos, a ordem largura × "Comprimento, morro abaixo" e o retângulo com o comprimento na vertical.
- `web/js/roca.js`: `medidas()` (as chaves valem e o `ha` sai delas), `efetivas()` (`ha` com 4 casas, `baixio_ha` com 4 casas
  abaixo de 0,1 ha) e a ficha com `areaTxt`.
- `web/js/globo/camadas.js`: "Milho em 2027" / "quebra N em 10" (`longo: true`).
- `web/js/globo/principal.js`: a classe `longo` no botão do cartão.
- `web/css/globo/painel.css`: `.cn.longo` quebra a linha.
- `web/css/globo/rocacerta.css`: a aba acesa.
- `web/js/passos/LEIA-ME.md`.

## 3. Como testei

**Node** (`node --check` nos 5 JS: ok). Rodei duas vezes, porque o Y mexeu no `ideal.js` e no `pareado.js` às 11:29–11:32:

| Teste | 11:23, com as minhas mudanças | 11:40, com as do Y também |
|---|---|---|
| `teste_calculo.mjs` | 16 linhas; `git diff calculo.js` vazio | igual ao HEAD |
| `teste_ideal.mjs` | 143.084 conferências, 0 falha | 189.825, 0 falha |
| `teste_dinheiro.mjs` | 21.413, 0 falha | 22.445, 0 falha |
| `teste_relatorio.mjs` | 168 casos, 19.258 conferências, 0 falha | 18.700, 0 falha |

Nas duas rodadas, o `teste_dinheiro` deu para Quixadá padrão Hoje R$ 2.480 · Melhorado 2.550 · Garantir 3.980 · Equilibrar 4.360.

No meio, às 11:29 (com o `ideal.js` novo e o `pareado.js` ainda velho), o aceite pegou N2 com 1.199 falhas e N3 com 2.171. As duas
sumiram quando o Y fechou o `pareado.js`.

**`efetivas()`** (`E:/campeonato-nasa/tmp/fluxo2/X/ef.mjs`):
- padrão de Quixadá: `ha` 1,03 e `baixio_ha` 0,34, como antes;
- 5 × 5 m, com `ha=0.01` (link velho), com `ha=0.0025` ou sem `ha`: `ha` 0,0025, `larg` 5, `comp` 5;
- 20 × 20 m: 0,04 ha; 30 × 50 m: 0,15 ha; Seu Antônio, 40 × 100 m: 0,4 ha, `baixio_ha` 0,13 (antes, 0,13);
- link antigo `medida:100x40` com `ha=2`, que não bate: vale o `ha` 2, como antes.

**No navegador** (Edge sem janela, 390 × 844, `E:/campeonato-nasa/tmp/fluxo2/X/ver.py`).

Sua roça nos 7 municípios, sem erro no console e sem rolagem de lado:

| Município | Palavras | Altura |
|---|---|---|
| Petrolina | 186 | 1.673 px |
| Quixadá, Crateús, Caicó e Barreiras | 178 | 1.644 px |
| Picos e Arapiraca | 162 | 1.534 px |

O teto é de 190 palavras e 1.800 px. O pior caso antes das correções era Petrolina, com 184 palavras e 1.661 px.

- Com banana marcada em Quixadá: 187 palavras e 1.727 px.
- Digitando nos metros: 20 × 20 → "= 400 m² · ≈ 0,1 tarefa"; 30 × 50 → "= 0,15 ha · ≈ 0,5 tarefa"; 5 × 5 → "= 25 m² · menos de 0,1 tarefa". O
  verde grava `#/2311306/3?ha=0.0025&area_un=medida:5x5&larg=5&comp=5`, e a ficha diz "5 × 5 m · milho e feijão · Mudar".
- `#/2311306/5?ha=0.01&area_un=medida:5x5&larg=5&comp=5`: a ficha diz "5 × 5 m". O cabeçalho do Relatório ainda diz
  "5 × 5 m · 0 ha" (é o `U.ha` do `relatorio.js`; pedido 1).
- `#/2311306/4?larg=5&comp=5`: antes saía "falta a série" e "−R$ 0". Agora Hoje dá R$ 6 e Melhorado e Ideal dão "sem conta" (pedido 3).
- Maniva com `hoje=milho:50,mandioca:50`: "Tem maniva para plantar mais? A rama da mandioca. Tenho · Já está plantada · Não tenho ·
  Não sei".
- O aviso aparece com `hoje=milho:50,banana:50` e em Picos com `hoje=mandioca:100`: "Fora do indicado aqui: banana." / "…: mandioca.".
- Cartão do mapa (`index.html?lugar=Quixadá`, 390 px): "Milho em 2027 / quebra 6 em 10 / PROJEÇÃO". O rótulo cabe (74 de 74 px),
  e os 3 cartões têm 99 px de altura (antes, 85).
- Painel `painel.html?cod=2311306`: a aba "Inverno 2027" acesa em verde translúcido com borda, sem erro no console.

Prints em `E:/campeonato-nasa/tmp/fluxo2/X/`:
- `quixada_2_tam.png`, `quixada_2_30x50_tam.png`: a linha do tamanho;
- `passos_crop.png`: a aba Passos;
- `globo_crop_b.png`: o cartão e o painel embutido;
- `painel_crop.png`.

**Aceite** (`aceite_fluxo.py 2311306,2208007`, 11:28–11:40). Prints e `aceite.json` em `E:/campeonato-nasa/tmp/fluxo2/X/aceite/`;
a 2ª rodada de node e toques (11:41) está em `aceite2/`.

- **Telas: 10 de 10 ok.** 1 verde em todas, 0 erro no console, nada rolando de lado.

  | Município | Tela | Altura | Palavras | Outros |
  |---|---|---|---|---|
  | Quixadá | Sua roça | 1.644 px | 178 | |
  | Quixadá | Plano | 2.734 px | 329 | |
  | Quixadá | Plano ideal | 2.941 px | 347 | |
  | Quixadá | Dinheiro | 1.976 px | 223 | |
  | Quixadá | Relatório | 5.627 px | | 16 tarefas, 26 datas |
  | Picos | Sua roça | 1.534 px | 162 | |
  | Picos | Plano | 2.710 px | 323 | |
  | Picos | Plano ideal | 3.014 px | 380 | |
  | Picos | Dinheiro | 2.003 px | 231 | |
  | Picos | Relatório | 5.099 px | | 14 tarefas, 22 datas |

- **Toques: C1, C3–C7 e C9–C13 ok.** Duas falhas, nenhuma das minhas correções:
  - **C2:** "R$ 2.480 | R$ 2.550 | R$ 6.640", e o esperado no ideal é R$ 3.980.
    - No mesmo navegador, `comparar3` com o `ef` padrão dá 2.476 / 2.551 / 3.985, como o node. O `ef` padrão não mudou com as minhas
      correções: `ha` 1,03 e `baixio_ha` 0,34.
    - O gráfico da página mostra 6.640, e a tabela "Sobra num ano normal" mostra R$ 3.080 no ideal.
    - A diferença apareceu depois do `ideal.js` do Y (11:29–11:32) e está no caminho `dinheiro.js`/`hoje_ideal.js`/`ideal.js`
      (pedido 5).
  - **C8:** "mandioca no desenho True → True".
    - A linha da maniva aparece, o "Não tenho" grava `maniva=nao` e o verde leva ao Plano.
    - O `ideal.js` atual deixa 1 faixa de mandioca (Parte C, 2027) com `maniva=nao` e milho e mandioca no jeito dele (`c8.mjs` no
      node: 6 faixas com mandioca sem resposta, 1 com "Não tenho"). É a mandioca que já está no chão, e a pergunta nova ("Tem maniva
      para plantar mais?") combina com ela.
    - O critério do C8 no aceite precisa acompanhar (pedido 6).
- **Painel:** P1 ok (as 3 abas com os extras, 7, 6 e 16 selos, sem erro). P2 ok (o verde vai para `#/2311306/2`; o cartão mostra
  "Milho em 2027 · quebra 6 em 10", "Chuva típica 590 mm" e "Solo agora normal").
- **Percurso e PDF:** F1–F7 ok.
  - F4: "40 × 100 m", com "= 0,4 ha ≈ 1,3 tarefa".
  - F6 e F7: PDFs A4 de 4 páginas.

## 4. O que ficou faltando

- O `U.ha` do `comum.js` continua escrevendo "0 ha" para menos de 0,05 ha, e 1 casa para menos de 1 ha. Isso aparece no Relatório,
  em `leve_ao_tecnico`, `dinheiro`, `cenarios`, `hoje_ideal` e `harmonizacao` (pedido 1).
- O achado 6 (item 6 da tabela).
- O cartão do mapa ficou 14 px mais alto no celular, porque "quebra 6 em 10" ocupa 2 linhas.

## 5. Pedidos ao integrador

1. **`U.ha` em `comum.js`** (a regra para o site todo; o `comum.js` não é meu nem do Y):
   ```js
   export const ha = (v) => (v > 0 && v < 0.1 ? `${num(v * 1e4 >= 100 ? Math.round(v * 1e3) * 10 : Math.round(v * 1e4))} m²`
     : v > 0 && v < 0.995 ? `${num(v, 2).replace(/0$/, "")} ha`
     : `${num(v, v < 10 && Math.abs(v - Math.round(v)) >= 0.05 ? 1 : 0)} ha`);
   ```
   - Com isso, o `areaTxt` local de `perguntas.js` e `roca.js` pode virar `U.ha`.
   - Sem isso, o Y precisa trocar `U.ha(ef.ha)` por `haTxt(U, ef.ha)` em `relatorio.js` (cabeçalho, l. 394; hoje sai "5 × 5 m · 0 ha").
   - Atenção: entre 0,1 e 1 ha, o texto passa de 1 casa para 2 (Arapiraca típico: "0,4 ha" vira "0,44 ha"). Conferir os tetos de
     palavras.
2. **Y, Plano:** chamar a linha "Anos de quebra" de "Anos ruins do roçado" (`ideal.js`/`plantio.js`). O cartão do mapa agora diz
   "Milho em 2027 · quebra 6 em 10", e as duas coisas não podem parecer o mesmo número (achado 4 do R1).
3. **Y, `ideal.js` l. 303 (`ha_giro: … * 100) / 100`):** `ha_giro` é arredondado para 2 casas. Num roçado de 5 × 5 m (0,0025 ha), ele vira 0, e Melhorado e Ideal
   saem "sem conta" em Quanto rende. Com 4 casas (como o `ef.ha` agora), a conta sai. O mesmo vale para a cópia em
   `dinheiro/pareado.js`.
4. **`aceite_fluxo.py`:** acrescentar o caso 5 × 5 (achado 5 do R3):
   - `#/2311306/5?ha=0.0025&area_un=medida:5x5&larg=5&comp=5`;
   - a ficha diz "5 × 5 m", e o "TAMANHO" do Relatório não diz "0 ha".
5. **C2 do aceite (Y):**
   - Em `#/2311306/4`, o gráfico mostra o ideal em R$ 6.640, e o `comparar3` dá 3.985 com o mesmo `ef`.
   - O `teste_dinheiro` passa porque não confere o gráfico (`.hi-graf .hi-g-val`).
   - Conferir a coluna "ideal" do gráfico de `hoje_ideal.js` (modo "comparacao") contra `c3.ideal.beneficios.rs.tres_anos.p50`.
6. **C8 do aceite (integrador):** com o `ideal.js` atual, "Não tenho" maniva deixa a mandioca que já está no chão (1 faixa no 1º ano).
   - Se essa é a regra nova do Y, o C8 passa a conferir que a mandioca cai de 6 faixas para 1, e não que ela some.
   - Se não é, é com o Y.
7. **`teste_ideal.mjs`:** a cópia de `efetivas()` não lê `larg` e `comp` para o `ha`. O caso "em metros" (sem `ha`, 120 × 250 m) usa o
   típico ali, enquanto o site usa 3 ha. Importar `efetivas` de `roca.js`, como fazem `teste_dinheiro` e `teste_relatorio`, tira a
   diferença.
