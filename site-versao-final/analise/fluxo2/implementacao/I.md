# I (Integrador): rodada 2, fase 3 (15/11/2026, 09:49–10:40)

Colei as peças das fases 1 e 2, atendi os pedidos ao integrador, reescrevi o aceite e o percurso, e rodei tudo nos 7 municípios, em
série, com um Edge por vez. O fluxo colado, as decisões, os 16 pontos e o aceite estão em `analise/fluxo2/00_FLUXO_V2.md`. Não reiniciei
o servidor, não fiz commit e não matei processo nenhum.

## 1. O que fiz

### Correções no site (pedidos ao integrador e o que achei colando)

| Arquivo | O que mudou | Pedido |
|---|---|---|
| `web/js/extras/ideal.js` (`fazerAgenda`) | Um baixio "solteiro" ou "sem revezamento" no texto da célula (o sorgo granífero do "Guardar água") não ganha mais a linha "Feijão-caupi no milho em pé". Conferido nos 7 municípios × 4 prioridades: o revezamento só aparece onde a célula fala em revezamento ou em mucuna. As 51 de 51 linhas do núcleo continuam iguais. | C4 nº 1 |
| `web/js/extras/terreno.js` | (1) `carregarAgronomia()` tenta de novo uma vez em 400 ms. (2) A gliricídia da cerca (`entre_linhas_m` null) agora é contada: perímetro ÷ 5 m. (3) Sem kg na fonte (milho, mucuna), sai o número de sementes (covas × por cova, `unidade: "sementes"`). (4) O caupi do revezamento vai a 25 cm, distância lida do "como" do A1. (5) A 2ª planta segue a mesma leitura do `segundaBaixio` do Plano: "+ feijão em revezamento" (o seu jeito) passa a contar o feijão. Antes, só contava quando o texto dizia "caupi". (6) Algodão (`por_cova` null): "1 planta a cada 15 cm". (7) `svgTerreno` aceita `plano`, para saber a leguminosa. | C2 nº 4, C4 nº 2, A1 nº 1 |
| `web/js/passos/relatorio.js` | Passa o `plano` ao desenho pequeno. "Seu olho" das faixas no bloco do material: o Relatório não tinha nenhum à vista. Os comentários apontam para `testes/ferramentas/teste_relatorio.mjs`. | LEIA-ME (1 "seu olho" por passo) |
| `web/js/passos/dinheiro.js` + `web/css/passos/dinheiro.css` | **Ponto 4 sem casa:** "Testamos 7 jeitos de ler o passado" (as barras de acerto em 100) só existia no `seguranca.js`, que saiu da jornada. Foi para o fim do "Ver como calculamos", com o CSS das barras, que veio do `seguranca.css` (B2 nº 2). | os 16 pontos |
| `web/js/extras/leve_ao_tecnico.js` | "Ver as 5 perguntas" virou "Ver as perguntas (5)": "5 perguntas" é frase banida, e o técnico de Crateús tem 5. | aceite |
| `web/js/roca.js` + `web/css/quadra.css` | `sem-entrada` na caixa do passo quando `ctx.entrou` é falso, em todos os passos: a tela não pula 10 px a cada resposta. | C2 nº 5 |
| `web/js/extras/vulnerabilidade.js:338` | "Do espaço mostra quanto" virou "o painel do município, no mapa (aba Solo e clima), mostra quanto". | B2 nº 3, B3 nº 2 |
| `web/js/extras/historico.js` | Os comentários do modo "cartao" e "memoria" já não dizem passo 3 e 5. | B2 nº 5 |
| `web/js/passos/LEIA-ME.md` | As 6 linhas de Sua roça, "em tarefas ou passos" (`area` com `abas`), o terreno em "ver mais", "Mais 4", `prioridade` + `plano=ideal`, `cenarios` `{ leitura: true }`, o modo "comparacao" novo de `hoje_ideal`, `compartilhar(ctx, { plano, tarefas })`, o `@page` do relatório, `agendaDoPlano`, as contas novas do terreno, `sem-entrada`, os números do cartão do mapa e as abas do painel, os testes do node e os JSON em `testes/exemplos/api/`. | B1 nº 2, B3 nº 1, C2 nº 6, C3 nº 3, C4 nº 4 |

### Testes

- **`testes/ferramentas/aceite_fluxo.py`** (reescrito), com 5 partes:
  - parte 0, node: o diff do `teste_calculo` contra o `calculo.js` do HEAD e os 3 testes do motor, do dinheiro e do relatório;
  - parte 1, telas: as 5 telas (o Plano nos 2 lados) × 7 municípios;
  - parte 2, toques: C1–C13;
  - parte 3, painel: P1 e P2;
  - parte 4, o percurso e o PDF: F1–F7.

  Os critérios estão na seção 6 do `00_FLUXO_V2.md`. O script sai com 1 se algo falhar, e `--so-<parte>` roda uma parte só.
- **`testes/ferramentas/percorrer_fluxo.py`** (reescrito) faz 5 verificações, cada uma numa linha "rótulo: … ok": globo → plano,
  percurso 2 → 3 → 4 → 5, Seu Antônio, 40 × 100 m (do campo de metros ao desenho, ao terreno e ao Relatório) e o ideal com Água.
- **Para o repositório:**
  - `teste_dinheiro.mjs` (C3), `teste_relatorio.mjs`, `teste_pdf.py` (C4) e `teste_painel.py` (B3), com caminhos relativos;
  - os JSON da API em `testes/exemplos/api/` (8) e `api_respostas/` (4);
  - o `teste_ideal.mjs` passou a ler de lá.

  Os testes do node já não dependem do `E:/…/tmp`.
- `erros_console.py`: o exemplo de uso aponta para `/2`.

### Documentos

- `analise/fluxo2/00_FLUXO_V2.md`, novo: o fluxo em uma página, as decisões, os 16 pontos e o aceite.
- `PLANO_INTEGRACAO.md`: seção "Rodada de 15/11 (manhã)".

## 2. Como testei (números)

- **Node, a partir do repositório, todos com 0 falha:**

  | Teste | Conferências |
  |---|---|
  | `teste_ideal.mjs` | 143.084 |
  | `teste_ideal.mjs` com `API=testes/exemplos/api_respostas/` | 70.574 |
  | `teste_dinheiro.mjs` | 21.413 |
  | `teste_relatorio.mjs` (168 casos) | 19.258 |

  `teste_calculo.mjs` dá saída idêntica à do `calculo.js` do HEAD (16 linhas), e `git diff calculo.js` vem vazio. O `teste_ideal`
  caiu de 144.407 para 143.084 conferências porque saíram as linhas de revezamento penduradas em sorgo solteiro.
- **`teste_terreno.mjs` do C1, com o `agronomia.json` real:**
  - a regressão do quadrado continua com 0 diferenças em 120 layouts;
  - as diferenças de saída são só as esperadas: a gliricídia agora tem "≈ 56 mudas", o milho "≈ 7.920 sementes" e o caupi do
    revezamento vai a 25 cm.
- **Aceite, 1ª rodada completa (10:05–10:23):** 34 de 35 telas ok, C1–C13 ok, P1–P2 ok e F1–F7 ok.
  - A falha foi "5 perguntas" no Relatório de Crateús, já corrigida.
  - Os PDFs têm 4 páginas: Seu Antônio com Água e Quixadá "Um pouco de cada".
- **Rodada final:** os números estão na seção 4.

## 3. O que ficou faltando (para R1–R3 e X/Y)

1. **Feijão × caupi na frente (decidido, não feito):**
   - O nome passa a ser "feijão" para o Feijão-caupi e "feijão comum" para o outro.
   - A troca mexe nos nomes curtos de `plantio.js` (CURTO), `plantio/calendario.js` (NOME), `terreno.js` (CURTO), `relatorio.js`
     (FALA) e `leve_ao_tecnico.js` (NOME), e em cerca de 30 textos fixos com "caupi".
   - Atenção: `plantio.js` e `calendario.js` hoje chamam o Feijão comum de "feijão". Esses dois têm de virar "feijão comum" junto.
   - Fica para o Y, com o aceite rodando depois.
2. **"Só palma"** (C3 nº 5, A2/Y): com `ha_giro = 0`, a frase deveria dizer que não sobra chão para girar.
3. **`medidaIni` × `efetivas`** (B2 nº 6): os dois aceitam medidas de jeitos um pouco diferentes (2% × 5% + 0,005 ha, e o limite
   de 5.000 m). A diferença só aparece num link feito à mão. Deixei como está.
4. **`pareado.js`** (C3) copia 4 funções internas do `ideal.js`. O teste garante que batem. Exportar `contexto` e `itensPlano` do
   motor tiraria a cópia (A2/Y, opcional).
5. **Os PDFs estão no limite: 4 de 4 páginas.** Qualquer linha a mais no Relatório impresso pode passar para 5. O aceite (F6, F7)
   avisa.
6. **Quanto rende de Barreiras tem 291 palavras, para um teto de 300.**
7. **O texto do P4 do núcleo** ("cortar o milho para os animais") aparece também em plano sem milho (C4). É do núcleo (D8).

## 4. Rodada final do aceite

Rodada de 15/11/2026, 10:24–10:34, com `aceite_fluxo.py --prints`: **tudo ok** (saída 0). Resultado em
`E:/campeonato-nasa/tmp/fluxo2/final/aceite.json` e prints em `E:/campeonato-nasa/tmp/fluxo2/final/`.

| Parte | Resultado |
|---|---|
| Node | N1 ok (16 linhas iguais ao HEAD; `calculo.js` sem mudança) · N2 143.084 conferências, 0 falha · N3 21.413, 0 falha · N4 19.258 em 168 casos, 0 falha |
| Telas (35 = 5 × 7 municípios) | 0 falha. Sua roça 1.522–1.661 px e 160–184 palavras · Plano, seu jeito, 2.699–2.828 px e 323–356 · Plano, ideal, 2.975–3.131 px e 353–415 · Quanto rende 1.925–2.163 px e 213–291 · Relatório 3.789–5.627 px, 5–16 tarefas. 1 verde em todas; "seu olho" 1–2; 0 erro no console; nada rolando de lado |
| Toques | C1–C13 ok. Quixadá padrão: R$ 2.480 · 2.550 · 3.980. Prioridades: 4 desenhos e 4 tabelas diferentes. Seu Antônio com Água: Plano e Quanto rende com os mesmos R$ 703 / 949 / 903 (ano normal), 345 / 511 / 452 (2027) e 1 em 10; Relatório "O ideal · Guardar água" com 44 datas, 0 fora da agenda |
| Painel | P1 ok (as 6 peças do antigo "Do espaço" nas 3 abas, 7–16 selos por aba, 0 erro) · P2 ok (verde → `#/2311306/2`; cartão: milho quebra 6 em 10, chuva 590 mm, solo normal) |
| Percurso e PDF | F1–F5 ok (o globo abriu de verdade e levou ao plano em 2 toques) · F6 e F7: PDF A4 com 4 páginas cada |

Prints a 390 px, em `E:/campeonato-nasa/tmp/fluxo2/final/`:
- cada tela dos 7 municípios: `<cod>/2_sua_roça.png`, `3_plano.png`, `3_plano_ideal.png`, `4_dinheiro.png` e `5_relatório.png`;
- `percurso/`:
  - o globo: `01_globo_painel`;
  - as telas: `02_sua_roca`, `03_plano`, `04_dinheiro` e `05_relatorio`;
  - Seu Antônio: `06`–`07`;
  - 40 × 100 m: `08`–`10`, com o terreno aberto em `09_metros_plano`;
  - o ideal com Água: `11`–`13`;
- o painel aba por aba: `painel/quixada_390_<aba>.png`;
- o ponto 4 no "Ver como calculamos": `ponto4_7jeitos_390.png`;
- os PDFs: `relatorio_F6.pdf` e `relatorio_F7.pdf`.

## 5. Pedidos

- **Y (fase 5):**
  - a troca feijão × caupi (item 1 acima);
  - a frase do "só palma";
  - se mexer no Relatório impresso, rodar `aceite_fluxo.py --so-fim` (PDF ≤ 4 páginas).
- **R1–R3:** o aceite inteiro roda com `MSYS_NO_PATHCONV=1 E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8
  testes/ferramentas/aceite_fluxo.py --prints`. Leva ~40 min e salva em `E:/campeonato-nasa/tmp/fluxo2/final/` (`QUADRA_PRINTS`
  troca a pasta). Só a parte do node: `--so-node` (~15 s).
