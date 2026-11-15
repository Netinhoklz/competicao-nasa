# 03 · Valor da informação: o que cada pergunta muda de verdade

Lente: medir. Para cada item perguntado, comparei a saída **com e sem a resposta**: o JSON da API (`/api/local`, 10
municípios + amostra de 36) e as contas do navegador rodadas no node (`calculo.js`, `hoje_ideal.js`, `historico.js`,
7 municípios). Medidas brutas: `E:/campeonato-nasa/tmp/vi_diff_out.txt`, `vi_medir_out.txt`, `vi_resumo.txt`.
Nada do site foi editado.

**Resumo em uma linha:** das 11 telas do passo 2, **só 5 itens mudam o plano, as datas ou o R$** (culturas de hoje,
tamanho, terra, baixio e maniva). Os outros 7 mudam **zero** em datas, plano e R$; mudam só uma frase, ou nada.

---

## 1. Diagnóstico do fluxo atual (com evidência)

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| 1 | 13 telas e **14 toques no mínimo** entre o globo e o plano; respondendo de verdade, uns 30 | passo 1 + 11 perguntas + resumo (`perguntas.js:77-97`, prints 02–13) | alta |
| 2 | O botão promete "**5 perguntas**", mas são 11 telas | `lugar.js:148` × prints 02–12 | alta |
| 3 | A tela "E na hora de plantar?" diz "**Só o que muda a conta**", mas nada muda o R$ (Δ R$ 0 nos 6 municípios com conta; Caicó não tem série do IBGE) | `hoje_ideal.js:402`; plantio na 1ª chuva, queima e semente só trocam frases (`:178-179`, `:291-298`) | alta |
| 4 | A pergunta da água diz "**muda o que dá para salvar**", mas não muda nada: não vai para a API nem para a conta | `perguntas.js:30`; `roca.js:44-51` (não envia `agua`); só aparece em texto (`leve_ao_tecnico.js:67-68`, `perguntas.js:68`) | alta |
| 5 | Respostas que **nenhum código lê**: "deu bem", "como prepara a terra" (trator/animal/enxada), "palhada", "esterco" e o volume do barreiro | `historico.js:72,76` são lidos, mas só `resumoHistorico` (`:282-291`) os usa; `vol` só gera um chip (`perguntas.js:101`) | alta |
| 6 | O histórico repete o jeito de hoje: 2026 vem preenchido pelo "hoje", e queima e semente são perguntadas duas vezes (no hoje e no "já faz") | `historico.js:216-222`, `:265-272` | média |
| 7 | Ordem trocada: pede a % de cada cultura "no seu roçado de 1,0 ha" **antes** de perguntar o tamanho | print 02 × pergunta 2 de 5 (print 09) | média |
| 8 | O resumo "Pronto" é uma 12ª tela que repete as respostas, com **dois botões iguais** ("Ver como plantar" e "Como plantar →") | print 13; `perguntas.js:69` × barra de `roca.html` | média |
| 9 | No passo 4, o Garantia-Safra (sim/não/não sei) não muda nada; o chip "você cabe" sai do tamanho | `dinheiro.js:116-118`; Δ R$ 0 | média |
| 10 | Chave morta `criacao` no PADRAO e em efetivas(), sem pergunta nem uso | `roca.js:17,87` | baixa |
| 11 | Passos longos a 390 px: 4.550 / 5.625 / 6.629 / 6.377 px (de 6 a 9 telas de rolagem cada) | BRIEFING, prints 01, 14, 15 e 16 | média |

### Quanto cada item muda (medido)

R$ = sobra em 3 anos depois da semente (P50), Quixadá 1,03 ha, preço da raiz "comum CE". "Frente" = em quantas de 100
combinações o plano ganha do jeito de hoje (base: plano R$ 4.364, hoje R$ 2.476, frente 98).

| Item | Datas | Plano A/B/C | Desenho | R$ (Quixadá) | Outros municípios | Classe |
|---|---|---|---|---|---|---|
| **hoje.culturas** | — | — | — | Hoje: só milho −R$ 1.500; só feijão +R$ 1.440; com mandioca ⅓ +R$ 2.324 → **frente 98 → 14** | só milho: frente 12→67 (Picos); com mandioca: Petrolina 97→0 | **muda muito** (a régua do passo 4) |
| hoje.arranjo | — | — | — | Hoje Δ 0; "milho no baixio" tira o ajuste do Melhor (−R$ 471); muda 1 frase | igual nos 6 com conta | **só texto** |
| hoje.manejo (1ª chuva, queima, semente) | — | — | — | Δ 0 em Hoje, Melhor e Ideal; liga/desliga 1 frase de alerta e 1 de ajuste | igual nos 6 com conta | **só texto** |
| hist.anos (2026/2025) | — | — | — | Δ 0; acende 1 cartão: "A terra repetiu milho: comece com o caupi" ou "a Parte A já começa com a sua mandioca" | igual | **só texto** (1 frase útil) |
| hist.deu | — | — | — | "Deu bem": **nada** (sem leitor). "Quebrou + ano": passo 5 compara com o IBGE (milho 2024 = 0,46 do normal) e 1 cartão do baixio | igual | **só texto** (a memória é ponto 16) |
| hist.faz | — | — | — | Δ 0. Faixas → 1 frase; palhada, esterco e trator/animal/enxada → **nada** | igual | **nada / só texto** |
| **terra** | **sim**: janela principal +10 dias (mediana) na mista e no barro; arenosa ≈ "não sei" | — | — | Δ 0 | amostra de 36: alarga em 71/132 linhas (mista) e 85/136 (barro); arenosa iguala em 107/128; datas mudam em 33/36 municípios | **muda pouco a médio** (só as datas) |
| **ha** | — | — | escala (m², ha por faixa) | linear: 0,5 ha → R$ 2.105; 3 ha → R$ 12.684; **frente igual (98)** | linear nos 6 com conta; quem ganha nunca muda | **muda o número, não o veredito**; Censo dá padrão municipal em 1.642/1.794 |
| **baixio** | "tenho": a janela do milho no baixio vai de 8 para 28 dias | "não tenho": **some a linha do Baixio** (milho sai do roçado) | sim (fração 0,2/⅓/½) | não: +R$ 937; metade: −R$ 495 | Barreiras −R$ 10.272 (−27%); Petrolina +R$ 3.713 (+55%); muda o plano em 10/10 | **muda muito** |
| agua | — | — | — | Δ 0 (não vai para a API) | igual | **só texto** (pergunta ao técnico) |
| **maniva** | "plantada": "já está no chão" | "não": **plano sem mandioca** | — | não: −R$ 2.851 e **frente 98 → 0**; plantada: +R$ 1.145 | 0 efeito em 5/10 (plano sem mandioca); amostra: 24/36 planos têm mandioca | **muda muito, mas só quando o plano tem mandioca** |
| bolso.prioridade | — | — | — | Δ 0; troca o número do destaque (P50 R$ 4.364 → caso ruim R$ 2.761), a ordem dos blocos e o jeito aceso em "Outros jeitos" | igual | **muda o destaque** (ponto 9); padrão inferido do El Niño |
| bolso.raiz | — | — | — | município R$ 1,33: +R$ 1.814; baixo: −R$ 921 | Crateús: frente 99 → 67; 0 efeito sem mandioca | **muda médio** (só com mandioca) |
| bolso.custo | — | — | — | máquina e insumos: plano **R$ 4.364 → −R$ 1.743**, frente 98 → 47 | Petrolina −R$ 8.003; Crateús frente 99 → 53 | **muda muito** (o bloco "a colheita paga?" já mostra os dois) |
| bolso.gs | — | — | — | Δ 0; troca 1 chip | igual | **nada** |

---

## 2. Decisão por item

| Item | Decisão | Por quê (medida) | Para onde |
|---|---|---|---|
| hoje.culturas | **manter** | Única resposta que vira o veredito do passo 4 (frente 98 → 14 com mandioca). Padrão milho + feijão 50/50 já é o mais comum | Tela única "Sua roça", bloco 1, já marcado; a % fica em "ajustar %" (padrão: dividir igual) |
| hoje.arranjo | **cortar** | R$ 0; muda 1 frase | Inferir "tudo junto". O ajuste do Melhor passa a dizer "Milho só no baixio, se ainda não faz" |
| hoje.manejo | **cortar** | R$ 0 nos 6 municípios com conta; os conselhos ("espere a janela", "sem fogo", "junte a semente") já estão no "O que fazer e quando" do passo 3 | Semente pelo Censo (`pct_semente_milho`, já é o padrão: `hoje_ideal.js:35`); 1ª chuva e queima ficam como conselho fixo |
| hist.anos | **inferir** | Só acende 1 cartão. 2026 = jeito de hoje (já é assim); 2025 = igual (repetir no mesmo lugar é a regra) | `lerHistorico`: sem `antes`, usar hoje para 2026 e 2025. O cartão diz "**Se** o milho repete no mesmo lugar…". Link "no ano passado foi diferente" no cartão |
| hist.deu | **mover** | "Deu bem" não tem leitor; "quebrou + ano" só serve à memória do passo 5 | Passo 5, bloco "A sua memória e os dados": os chips "quebrou: milho/feijão/mandioca" + ano ficam ali, sem voltar ao passo 2 |
| hist.faz | **cortar** | Palhada, esterco e trator/animal/enxada: nenhum leitor; "faixas" só gera 1 frase | O "como prepara a terra" vira o rótulo do custo no passo 4 (ver bolso.custo) |
| terra | **manter** | Muda as datas em 33/36 municípios (+10 dias de mediana na mista e no barro). Sem mapa de solo, não dá para inferir | Tela única, bloco 3: 3 ícones + "não sei" (= datas de qualquer terra) |
| ha | **manter** (só confirmar) | O R$ escala com a área; quem ganha não muda; o Censo dá o padrão municipal em 1.642 de 1.794 | Tela única, bloco 2: "1,03 ha (o típico daqui)" já preenchido; hectares, tarefas e medida em "mudar" |
| baixio | **manter** | Muda o plano em 10/10, o desenho e o R$ (−27% a +55%) | Tela única, bloco 4 (5 opções com o mini-desenho) |
| agua | **mover** | R$ 0, datas 0, plano 0. O plano é de sequeiro | Passo 5, "Leve ao técnico": pergunta fixa "Tenho poço ou irrigação: que datas mudam?". A ficha do topo perde o chip "só a chuva" |
| maniva | **manter** (condicional) | Vira o plano e o veredito (98 → 0), mas só quando o plano tem mandioca (24/36) | Tela única, bloco 5, **só se o plano tem mandioca**. Mandioca marcada no bloco 1 → "plantada" inferido (pergunta some). Senão: "Consegue maniva? Sim / Não" |
| bolso.prioridade | **manter** | R$ 0, mas escolhe o número que importa (típico ou caso ruim) e o jeito aceso: é o ponto 9. Padrão "garantir" em alerta já é bom | Passo 4, primeiro controle (como hoje) |
| bolso.raiz | **opcional** | Muda o R$ do plano em −21% a +53%, só com mandioca | Passo 4, "Ajustar a conta" (ver mais), com o "seu olho: pergunte na casa de farinha" |
| bolso.custo | **opcional** | Muda muito, mas o bloco "A colheita paga o gasto do ano?" já mostra os dois níveis | Passo 4, "Ajustar a conta", com rótulo concreto: "Como prepara a terra? Enxada / Animal = só a semente · Trator = máquina e insumos" |
| bolso.gs | **cortar** | R$ 0; o "você cabe" sai do tamanho (≤ 5 ha) | Passo 5: chip automático "Garantia-Safra: você cabe (até 5 ha)" |

---

## 3. Fluxo proposto, tela a tela

1. **Globo → painel "Roça Certa"** (sem mudança). Botão "Montar o plano do meu roçado" → passo 1.
2. **Passo 1 · O seu lugar (1 tela, ~1.000 px)**. Ficam o título, a frase do El Niño 2027, 4 números (a chuva chega, os
   meses de chuva, o solo hoje, o mar) e uma linha: "11 culturas servem aqui". O botão principal fica no alto e no fim:
   "Montar o meu plano · 1 tela". Tendências, ano da chuva, cardápio de 18 e confiança vão para "ver mais".
3. **Passo 2 · Sua roça (1 tela só, tudo já preenchido)**: "Toque só no que for diferente".
   - Bloco 1, "O que vai no roçado": chips multisseleção (milho e feijão já marcados), mais "ajustar %".
   - Bloco 2, "Tamanho": "1,03 ha · o típico daqui", com o "mudar" que abre o `area.js` (ha, tarefas ou medida).
   - Bloco 3, "Quando chove forte, a terra…": seca rápido / segura / encharca / não sei. Tag: "muda as datas".
   - Bloco 4, "Tem baixio?": não / pequeno / ⅓ / metade / não sei (mini-desenho). Tag: "muda onde vai o milho".
   - Bloco 5, só se o plano tem mandioca e ela não foi marcada no bloco 1: "Consegue maniva?" Sim / Não.
   - Botão: "Ver o meu plano". Sem a tela de resumo: as respostas aparecem como fichas no topo dos passos 3 a 5
     (`roca.js:111`), e cada ficha volta a esta tela.
4. **Passo 3 · Como plantar**: o desenho A/B/C, o cartão "Por onde começar" (inferido do jeito de hoje) e "O que fazer
   agora" (3 itens). Em "ver mais": a rotação de 3 anos, o calendário completo, por que em faixas, o que cada planta
   faz e onde o roçado sofre mais.
5. **Passo 4 · Quanto rende**: Hoje → Melhor → Ideal no topo, mais "O que vale mais" (prioridade). Em "Ajustar a conta"
   (ver mais) ficam o preço da raiz e "Como prepara a terra" (custo). El Niño, caixa, "a colheita paga?" e os outros
   jeitos vão para "ver mais".
6. **Passo 5 · Segurança**: os cartões por cultura (compactos), mais "A sua memória": "Lembra de um ano que quebrou?
   [milho] [feijão] [mandioca] + ano", com a resposta do IBGE na hora. Ficam também os portões de 19/mar e 30/abr, o
   "Leve ao técnico" (com a pergunta da água) e o chip do Garantia-Safra.

---

## 4. O que muda nos passos 1, 3, 4 e 5 (e no globo e no painel)

| Onde | O quê | Decisão | Motivo |
|---|---|---|---|
| Globo/painel | Botão "Montar o plano do meu roçado" | manter | 1 toque, já é claro |
| Passo 1 | Botão "Responder 5 perguntas…" (`lugar.js:148`) | trocar por "Montar o meu plano · 1 tela", no alto e no fim | Promete 5 e entrega 11; fica no fim de 4.550 px |
| Passo 1 | "Pular e ver o plano com os padrões" | cortar | A tela única já está preenchida: pular = 1 toque igual |
| Passo 1 | Tendências, ano da chuva, cardápio de 18, confiança | mover para "ver mais" | Nenhum desses muda o plano; o cardápio repete as datas do passo 3 |
| Passo 3 | "Por onde começar o seu giro · Contar" | trocar por cartão inferido + link "foi diferente" | Hoje aparece vazio para quem pulou e manda de volta ao passo 2 |
| Passo 3 | Seletor "O seu é: mais plano / típico / inclinado" | manter dentro de "Onde sofre mais" (ver mais) | Muda só o desenho de erosão (ponto 12); não é pergunta do fluxo |
| Passo 4 | Controle Garantia-Safra sim/não/não sei | cortar; o chip vai para o passo 5 | Δ R$ 0 |
| Passo 4 | Preço da raiz + "O que você paga" | juntar em "Ajustar a conta" (ver mais) | Mudam muito o R$, mas o padrão é bom e o bloco "paga?" já mostra os dois níveis |
| Passo 4 | "Hoje: milho 50% + feijão 50% · tudo junto · mudar" | manter, sem "tudo junto" | O arranjo foi cortado |
| Passo 5 | "Contar o meu ano ruim" (volta ao passo 2) | juntar: o "quebrou + ano" passa a ser respondido ali | Único leitor da resposta é este bloco (`historico.js:172-190`) |
| Passo 5 | Leve ao técnico | acrescentar a pergunta fixa da água/irrigação | A água sai do fluxo, mas o ponto 15 continua coberto |
| Topo (ficha) | Chips terra · ha · baixio · água · maniva | tirar a água; pôr "Hoje: milho + feijão" | A água não muda nada |

---

## 5. Toques até ver o plano

| | Mínimo | Respondendo de verdade | Telas entre o globo e o plano |
|---|---|---|---|
| Hoje | **14** (ou 2 pulando tudo, sem personalizar nada) | ~30 | 13 |
| Proposta | **3** (globo · "Montar o meu plano" · "Ver o meu plano") | **5 a 7** (terra 1, baixio 1, culturas 0–2, tamanho 0–2, maniva 0–1) | 2 |

---

## 6. Riscos

- **Tudo numa tela fica longo a 390 px** (5 blocos ≈ 1.300 px). Mitigação: blocos compactos de 1 linha de botões.
  Se passar de 1,5 tela, dividir em 2 (Roçado: culturas e tamanho · Terra: terra, baixio e maniva), com 1 toque a mais.
- **Padrão aceito sem ler**: quem não toca em nada fica com milho + feijão, ⅓ de baixio "se tiver" e terra "não sei".
  É o mesmo que o "Pular" de hoje, mas o plano precisa continuar marcando "(padrão daqui)" e "baixio?" (já faz isso:
  `plantio.js:67-68`).
- **O cartão do histórico inferido** ("a terra repetiu milho") vira suposição. A frase precisa do "se" e do selo
  SUPOSIÇÃO; senão afirma o que ele não disse.
- **Maniva "plantada" inferida da mandioca no jeito de hoje**: a mandioca de hoje pode ser de outro pedaço. Mostrar o
  chip "a sua mandioca vira a Parte A · mudar".
- **Culturas sem preço** (sorgo, palma, outra) derrubam o "Hoje" (milho + sorgo: Hoje R$ 269, frente 100). Já existe o
  aviso "fica fora da conta", mas o veredito fica viesado: manter o aviso ao lado do número.
- **Ponto 15 (restrições: água, equipamento, mercado)**: com a água fora do fluxo, a cobertura passa a vir da
  prioridade (mercado), do "como prepara a terra" (equipamento) e da pergunta da água no técnico. Dizer isso no roteiro do júri.
- Mudar o passo 2 mexe no estado de `perguntas.js` (fase, q, telaForcada). Reaproveitar `opcao()`, `AREA.render` e
  `telaCulturas`, sem reescrever os módulos.

---

## 7. As 3 ideias mais importantes

1. **Pergunte só o que muda a resposta.** De 15 itens, 5 mudam plano, datas ou R$ (culturas de hoje, tamanho, terra,
   baixio e maniva). Os outros 7 do passo 2 (arranjo, manejo, os 3 do histórico, água e volume) mudam zero ou uma
   frase: corte, infira ou mova para onde a resposta é lida.
2. **Uma tela já preenchida com o típico daqui** (Censo 2017 + jeito mais comum), em que ele "toca só no que é
   diferente". São 3 toques até o plano em vez de 14, e nenhuma promessa falsa ("Só o que muda a conta", "muda o que dá
   para salvar", "5 perguntas").
3. **Cada pergunta vai para onde é lida.** A memória do ano ruim vai para o passo 5 (onde o IBGE responde), a água para
   o "Leve ao técnico", preço e custo para "Ajustar a conta" no passo 4, e a maniva só aparece quando o plano tem mandioca.

### Plano de implementação (4–6 h)

1. `perguntas.js`: tela única com 5 blocos, reaproveitando `opcao()`, `AREA.render(slot, ctx, {semTitulo:true})` e a
   grade de culturas de `hoje_ideal.js` (exportar `telaCulturas` ou uma versão compacta). Sem o resumo. Verificação: o
   print a 390 px tem 1 tela e ≤ 1.500 px; o hash leva `hoje`, `terra`, `ha`, `baixio`, `maniva`. **~2 h**
2. `roca.js paramsApi`: sem `resp.maniva` e com mandioca em `resp.hoje` → `maniva=plantada`. `lerHistorico`: sem
   `antes`, usar hoje para 2026 e 2025, marcado "inferido" (o cartão usa "Se…"). Tirar a água da ficha. Verificação:
   Quixadá com `hoje=milho:50,feijao:50` mostra o cartão do caupi; com mandioca, a Parte A diz "já no chão". **~45 min**
3. `dinheiro.js`: tirar o seg do GS; preço da raiz e custo em `U.verMais(..., "Ajustar a conta")`; rótulo do custo
   "Como prepara a terra". Verificação: R$ igual ao de hoje com o padrão (Quixadá R$ 4.364 / 2.476). **~45 min**
4. `historico.js` modo "memoria": os chips "quebrou + ano" no próprio bloco do passo 5 (reaproveitar o `detalhe` da
   `telaDeu`). `leve_ao_tecnico.js`: a pergunta da água fixa e o chip GS automático. Verificação: milho 2024 mostra
   "0,46 do normal" sem sair do passo 5. **~1 h**
5. `lugar.js`: o botão novo no alto e no fim; tendências, cardápio e confiança em "ver mais". **~30 min**
6. Conferir os 7 municípios (plano e R$ iguais aos de hoje com o padrão) e a ausência de rolagem lateral a 390 px. **~30 min**
