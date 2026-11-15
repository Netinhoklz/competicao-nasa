# 05 · Lente do técnico de ATER (extensionista)

Leitura de quem visita 80 famílias por ano no semiárido. Base: prints e textos de `E:/campeonato-nasa/tmp/fluxo_atual/` (Quixadá, 390 px), o código de `web/js/` e a API medida com e sem cada resposta (`E:/campeonato-nasa/tmp/ext_api/`). Nada do site foi editado.

## 1. Diagnóstico (o que o técnico vê)

**A conversa está ao contrário.** Numa visita, eu pergunto o que muda a recomendação e deixo o resto para o café. Hoje o QUADRA faz 12 telas de perguntas antes do plano. Metade delas não muda nada. E a pergunta que mais muda o sentido do plano, a criação, ninguém faz.

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| 1 | A tela promete "5 perguntas" e entrega 12 telas | `01_passo1_lugar.txt`: "Responder 5 perguntas sobre a sua roça" (lugar.js:148). Depois vêm as telas 02–13 | alta |
| 2 | Três contadores diferentes na mesma etapa: parece um questionário sem fim | "Seu jeito de hoje · 1 de 3" (02), "O que você já fez · 1 de 3" (05), "Pergunta 1 de 5" (08) | alta |
| 3 | Perguntas que não mudam nada: o agricultor responde à toa | **manejo** (1ª chuva, queima, semente) só gera frase de alerta e não mexe no R$ (hoje_ideal.js:178–181 e 291–298), embora a tela diga "Só o que muda a conta" (04). **água** não vai à API (roca.js:44–51) e só vira pergunta para o técnico (leve_ao_tecnico.js:67–68), embora a tela diga "muda o que dá para salvar" (11). **deu bem**, **preparo** (trator/animal/enxada), **palhada/esterco** só aparecem nas fichas do resumo (historico.js:286–289). **Garantia-Safra**: "o valor do benefício não entra na conta" (dinheiro.js:129) | alta |
| 4 | Falta a pergunta da criação. Quem cria bode ou gado usa sorgo forrageiro e palma; quem não cria não tira nada deles | `PADRAO.criacao` existe (roca.js:17), mas nenhuma tela pergunta e nenhum passo usa. Em Quixadá o plano põe sorgo forrageiro em 2 de 9 parte-ano. Sem maniva, são **6 de 9** (API `maniva=nao`), mais palma + gliricídia nas bordas nos 3 anos. Tudo isso aparece como "sem preço aqui" | alta |
| 5 | Passos compridos demais e o botão das perguntas fica escondido | Altura a 390 px: passo 1 = 4.550 px, passo 3 = 5.625, passo 4 = 6.629, passo 5 = 6.377. O botão do passo 1 está no fim dos 4.550 px (≈ 5 telas de rolagem) | alta |
| 6 | Pergunta repetida | O ano de 2026 do histórico é o "jeito de hoje" já marcado ("2026 · do seu jeito de hoje", 05). Queima e semente são perguntadas no hoje e reaparecem no histórico ("Já anotado…", 07) | média |
| 7 | Pedir % de cada cultura no consórcio não tem sentido agronômico (no "tudo junto", milho e feijão ocupam a área toda) e custa toques de +/− | 02. Na conta, "tudo junto" e "em pedaços" dão o mesmo R$: só "milho no baixio" muda (`areasHoje`, hoje_ideal.js:56–60) | média |
| 8 | Na água, "cisterna de beber" não serve ao roçado: a cisterna de placa é para beber. Censo: 83,2% têm cisterna, 2,8% irrigam, então a maioria vai marcar uma opção que não muda nada | `padroes.pct_cisterna = 83,2`, `pct_irrig = 2,8` (API Quixadá) | média |
| 9 | Falta "terra rasa / piçarra", que é comum no sertão cristalino | Medido: `ad=11` (AD1) põe o milho como "não zoneado". Com "seca rápido" (AD2) o milho vai de 21/02 a 28/02; com "misturada" (AD3), de 11/02 a 10/03 | média |
| 10 | Duas navegações na mesma tela | Barra de baixo "← Voltar · Como plantar →" junto com "Anterior/Próxima" do quiz (02, 07, 08). Na 07 são 5 botões | média |
| 11 | "Contar o meu ano ruim" (passo 5) volta ao começo do quiz | `linkPergunta: ctx.link(2)` (historico.js:361/377) e o passo 2 zera em "Como você planta hoje?" (perguntas.js:77). São 4 telas até chegar ao "quebrou" | média |
| 12 | A tela "Pronto" (13) é redundante | A casca já mostra as fichas com "mudar" do passo 3 em diante (roca.js:111–113), e as datas repetem as do passo 3 | baixa |
| 13 | Limitação interna aparece para o agricultor | "Sorgo / Palma / Outra · sem preço aqui" na 1ª pergunta (02) | baixa |
| 14 | Listas de culturas diferentes entre as telas | O hoje tem milho, feijão, mandioca, sorgo, palma e outra. O histórico tem também algodão e "nada (pousio)". Caju, banana e cana faltam (pendência já conhecida) | baixa |

**O que está certo e fica:** perguntar a terra pelo que se vê ("quando chove forte"). É a pergunta que mais mexe nas datas: com "não sei", a janela do milho é de 8 dias (21/02–28/02); com "misturada", é de 28 dias (11/02–10/03); e na terra de areia o feijão comum sai do zoneamento. Ficam também o baixio ("não tenho" tira a faixa do milho; "tenho" abre a janela do milho do baixio para 11/02–10/03), a maniva ("não consigo" troca a mandioca por sorgo forrageiro), o tamanho (desenho e R$), o "SEU OLHO" e o "não sei" com padrão.

## 2. O que fica de cada pergunta

| Item | Decisão | Para onde | Por quê |
|---|---|---|---|
| hoje.culturas | **manter** | P1 "O que tem no seu roçado?" | É o ponto de partida da rotação e do Hoje→Melhor→Ideal. Vira um toque só, sem % |
| hoje.arranjo | **inferir** ("tudo junto") | "mudar" no cartão Hoje (passo 4) | Só "milho no baixio" muda o R$, e o consórcio junto é o comum |
| hoje.manejo | **cortar** | o plano já diz "sem fogo", "espere a janela" e "garanta a semente" para todos | Não muda o R$. A semente já vem do Censo (`pct_semente_milho = 73,5`) |
| hist.anos | **fundir** com hoje.culturas | linha "Todo ano no mesmo lugar? Sim / Não" na P1 (vem marcado "Sim") | 2026 = hoje. Para a rotação só importa saber se repetiu no mesmo lugar |
| hist.deu | **mover** | passo 5, "A sua memória e os dados", formulário dentro da própria tela | "Quebrou + ano + motivo" é ótimo para a conversa (ponto 16), mas não muda o plano. "Deu bem" não tem efeito: sai |
| hist.faz | **cortar** | o preparo vira pergunta para o técnico | Palhada, faixas e esterco não mudam nada. A queima já está no plano para todos |
| terra | **manter** | P2, com nome + sinal: Areia / Misturada / Barro / **Rasa, de piçarra** / Não sei | É a resposta que mais muda as datas (medido) |
| ha | **manter** | P4, já preenchido com o típico do Censo (1,03 ha ≈ 3 tarefas). Um toque em "É isso" | Muda o desenho e o R$. Fica o pedido do José (ha/tarefas/medida, area.js) |
| baixio | **manter** | P3: Não / Sim, pequeno / Sim, grande / Não sei | Sim/não muda o plano. O tamanho só muda o desenho e o R$: "um terço" e "metade" viram "pequeno/grande" |
| agua | **mover** + inferir "só a chuva" | passo 5, chip opcional "Tenho barreiro ou poço perto do roçado" | Não muda a conta. 97% não irrigam |
| maniva | **manter** como condicional | P6, só se a P1 não marcou mandioca e o plano usa mandioca. Quem marcou mandioca fica com `maniva=plantada` | Muda o plano todo |
| bolso.prioridade | **inferir** (garantir em ano de El Niño, já é assim) | fica no topo do passo 4, numa linha | Ponto 9/15. É escolha, não fato: melhor depois de ver o R$ |
| bolso.raiz | **opcional** | passo 4, "Ajustar a conta" (fechado) | O padrão é o preço do município (MEDIDO) |
| bolso.custo | **opcional** | passo 4, "Ajustar a conta" (fechado) | A tabela "a colheita paga o gasto?" já mostra os dois níveis |
| bolso.gs | **cortar** o seletor | fica o lembrete que já está em "O que fazer agora" ("Adesão ao Garantia-Safra") | Não entra na conta |
| criacao (nova) | **manter** (nova P5) | "Tem criação?": Gado, bode ou ovelha / Só galinha ou porco / Não tenho | Decide se o sorgo forrageiro e a palma fazem sentido (pontos 8 e 15) |

## 3. Fluxo proposto, tela a tela

Ordem da visita de ATER: o que tem no roçado e se repete, a terra, o baixio, o tamanho, a criação e a maniva. Uma pergunta por tela, um toque e avança. Um contador só ("1 de 5"). Sem tela de resumo. Durante as perguntas, a barra de baixo fica escondida.

0. **Globo / painel Roça Certa**: igual a hoje. "Montar o plano do meu roçado" leva a `#/cod/1`.
1. **O seu lugar** (uma tela): manchete do El Niño 2027 + 4 blocos (mar, chuva chega, meses de chuva, solo hoje). O botão "Montar o meu plano · 5 perguntas" aparece **sem rolar**, com "Pular: plano com o típico daqui" embaixo. O resto vai para "Ver mais sobre o seu lugar".
2. **P1 · O que tem no seu roçado?** Ícones de seleção múltipla (milho, feijão, mandioca, sorgo, palma, caju, outra), com milho + feijão já marcados ("o mais comum aqui"). Embaixo, a linha "Todo ano no mesmo lugar? [Sim] [Não]", com Sim marcado. Botão "É isso". Grava `hoje` (divisão igual), `antes` (2026 = 2025 se Sim) e `maniva=plantada` se tiver mandioca.
3. **P2 · Como é a sua terra?** Areia (seca logo) / Misturada (segura a umidade) / Barro (encharca, gruda no pé) / Rasa, de piçarra (a enxada bate na pedra) / Não sei. Com o "SEU OLHO" do torrão.
4. **P3 · Tem baixio?** "A parte baixa onde a água para." Não / Sim, pequeno / Sim, grande / Não sei.
5. **P4 · Tamanho do roçado**: o típico daqui já vem preenchido, com os chips ½·1·2·3·5 ha e as unidades ha/tarefas/medida. Botão "É isso".
6. **P5 · Tem criação?** Gado, bode ou ovelha / Só galinha ou porco / Não tenho.
7. **P6 · Consegue rama de mandioca (maniva) para fevereiro?** Aparece só se a P1 não marcou mandioca e o plano usa mandioca. Consigo / Não consigo. Daqui vai direto ao plano.
8. **Passo 3 · Seu plano**: no topo, as fichas das respostas (um toque = mudar). Depois o roçado visto de cima, A-B-C de 2027 a 2029; "Por onde começar o seu giro", que agora sempre tem dado; "O que fazer e quando"; e o botão **"Levar para o técnico"** (imprimir ou WhatsApp). Num "Por que este plano" fechado ficam erosão, praga em faixas, o que cada planta faz pelo solo e os 3 anos parte por parte.
9. **Passo 4 · Quanto rende**: Hoje → Melhor → Ideal primeiro, com uma linha "O que vale mais" (padrão sugerido). Fechados: "Ajustar a conta" (preço da raiz, custo, divisão e arranjo do jeito de hoje) e "Ver mais" (os 4 El Niños, quando o dinheiro entra, se a colheita paga o gasto, outros jeitos de girar).
10. **Passo 5 · Segurança**: a manchete de 2027, "O que vamos olhar" (19/mar e 30/abr) e "Leve para o técnico". Fechados: o leque de cada cultura, "A sua memória e os dados" (com "Contar o meu ano ruim" na própria tela), "E se chover…", os 28 anos e o chip opcional de barreiro ou poço.

**Toques do globo até ver o plano:** 8 em Quixadá com o padrão (globo 1 + passo 1 1 + P1–P5 5 + maniva 1), 7 para quem já tem mandioca e 2 para quem pula. **Hoje são 14 toques e 13 telas** (globo, passo 1, 11 perguntas, resumo e "Ver como plantar").

## 4. O que muda nos passos 1, 3, 4, 5 e no globo

- **Globo/painel**: sem mudança. O painel já conta o El Niño e a estação de chuva, e o passo 1 só confirma.
- **Passo 1** (`lugar.js`): manchete + 4 blocos + botão no topo. "O ano da chuva", tendências, "o que dá para plantar", confiança e fontes vão para **um** `<details>` "Ver mais sobre o seu lugar". O botão passa a dizer "5 perguntas", que agora é verdade. Os pontos 1, 6 e 11 continuam na página.
- **Passo 2** (`perguntas.js`): sai o encadeamento hoje→histórico→perguntas e a tela "Pronto". A nova lista de perguntas reaproveita os ícones de `hoje_ideal.js` (sem a parte de %) e `area.js`. O último toque chama `ctx.ir(3)`.
- **Passo 3** (`plantio.js`): no topo ficam o desenho, o giro, a agenda e "Levar para o técnico". Vulnerabilidade, praga em faixas, saúde do solo e "parte por parte" ficam num "Por que este plano" fechado (pontos 8, 10 e 12 continuam lá).
- **Passo 4** (`dinheiro.js`): primeiro o Hoje→Melhor→Ideal. O "Seu bolso" vira uma linha (prioridade). Raiz, custo, divisão e arranjo vão para "Ajustar a conta". O seletor do Garantia-Safra sai e o chip "você cabe: até 5 ha" fica.
- **Passo 5** (`seguranca.js`): no topo, manchete, portões e técnico. O resto vai para "Ver mais". A memória abre o formulário do "quebrou" na própria tela (`HIST.render` na tela 1, só com a parte do "quebrou"), em vez de `ctx.link(2)`.
- **Ficha do roçado** (`leve_ao_tecnico.js`, `papel()` e `texto()` ampliados), numa página, para imprimir ou copiar para o WhatsApp:
  - município, data e confiança dos dados;
  - o roçado (área em ha e tarefas, terra, baixio, criação, o que planta e se repete);
  - tabela do plano 2027–2029 (A, B, C, baixio, bordas);
  - janelas de plantio de 2027 (ZARC);
  - 3 a 5 linhas de "fazer agora";
  - os portões de 19/mar e 30/abr;
  - Hoje × Plano em R$ (típico e caso ruim, PROJEÇÃO);
  - as 7 perguntas com caixinha ☐ e linhas para o técnico anotar;
  - a frase "o QUADRA apoia; quem decide é você, com o técnico".
- **Perguntas para o técnico**, duas novas:
  - "Sem criação: troco o sorgo forrageiro por sorgo de grão ou milheto?"
  - "A terra é minha? Posso plantar palma e gliricídia na cerca?" (posse da terra: importa para as perenes, mas não precisa virar pergunta no app).

## 5. Riscos

- Cortar telas pode parecer que se perdeu o que o José pediu (jeito de hoje, área, histórico). Os três continuam: jeito de hoje = P1, área = P4, histórico = linha "todo ano no mesmo lugar" + memória no passo 5. Isso precisa ser dito a ele.
- Inferir "todo ano igual" acende "a terra repetiu milho" para quem já roda. O "Não" está na mesma tela.
- "Terra rasa" (AD1) tira o milho da terra alta do zoneamento. O baixio continua com o milho (AD5). Testar nos 7 municípios.
- Na v1, a criação só muda texto e perguntas ao técnico. Trocar o forrageiro por sorgo de grão no motor (`forr` em motor.py:728) mexe no núcleo na véspera: só com o teste dos 7 municípios, senão fica para depois.
- Sem a %, o "Hoje" divide a área por igual. A % continua em "Ajustar a conta".
- `<details>` fechados escondem pontos do desafio na demo. É preciso uma lista "ponto → onde abrir" para quem apresenta.
- `window.print()` em Android simples gera PDF e confunde. O botão principal deve ser "Copiar para o WhatsApp".
- Agronomia do plano (não é do fluxo, mas o técnico vai notar): o baixio fica com milho nos 3 anos (motor.py, `[cel(cereal_baixio…)] * 3`). Há caupi em revezamento, mas não é rotação.
- Os links antigos continuam funcionando: as chaves `hoje`, `antes` e `exp` ficam no `PADRAO`.

## 6. Ordem de implementação (≈ 5–6 h)

1. `perguntas.js`: 5+1 perguntas, um contador, fim direto no passo 3. Esconder a barra de baixo no passo 2. `roca.js`: `TERRA.rasa`, fichas com criação no lugar da água. **2 h**
2. Passo 1: botão no topo + um "Ver mais". **40 min**
3. Passos 3, 4 e 5: subir o essencial e fechar o resto. Tirar o seletor do Garantia-Safra. **1 h 30**
4. Ficha do roçado (imprimir/WhatsApp) + 2 perguntas novas ao técnico. **1 h**
5. Memória com formulário na própria tela no passo 5. **40 min** (se faltar tempo, fica o link atual)

## 7. As 3 ideias mais importantes

1. **Cinco perguntas de verdade, de um toque cada, na ordem da visita.** O que tem no roçado (e se repete), terra, baixio, tamanho e criação, mais a maniva só quando faz falta. O resto vira padrão do Censo/município e ajuste opcional depois do plano. São 8 toques do globo ao plano, contra 14 hoje.
2. **Perguntar a criação.** É o que decide se o sorgo forrageiro e a palma (um terço do roçado em 2027, e dois terços sem maniva) servem para algo. Ligar a resposta ao texto do plano e às perguntas do técnico.
3. **Ficha do roçado numa página** para imprimir ou mandar por WhatsApp: plano A-B-C, datas, fazer agora, portões, R$ hoje × plano, as perguntas com caixinha e espaço para o técnico. É o que o técnico leva na visita, e cumpre o ponto 16.
