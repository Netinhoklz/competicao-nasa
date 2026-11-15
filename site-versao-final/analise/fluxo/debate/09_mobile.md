# 09 · Debate · Lente: celular, acessibilidade e pouca leitura

Base das medidas: Quixadá-CE (2311306) a **390 × 780 px**. Com o topo fixo (107 px) e a barra de baixo (123 px), sobram **550 px úteis**.
As medidas brutas estão em `E:/campeonato-nasa/tmp/mobile_lente/medidas*.json`. Antes de afirmar, conferi no código os pontos novos deste parecer.

**Minha posição em uma linha:** o melhor fluxo é o do **01 (Agricultor)**, com emendas de quatro lentes:
- **06:** navegação.
- **08:** "não sei" honesto.
- **04:** o nome NASA no selo.
- **09 (a minha):** limites medidos de altura, toque e rede.

Abandonei as minhas "3 telas, uma por pergunta" e passei a defender **uma tela única**. Mas ela só vale se couber sem rolar e se guardar as respostas localmente (ver §6).

---

## 1. As melhores ideias dos outros

| De | Ideia | Por que é boa para o celular |
|---|---|---|
| **01 Agricultor** | O globo leva direto a `#/<cod>/2`. O passo 1 vira "Do espaço", fora do caminho, e a numeração das rotas fica igual | Custa 2 linhas (`globo/principal.js:94`, `globo/rocacerta.js:333`) e tira da frente 4.550 px (8 rolagens) que repetem o painel (`rocacerta.js:167-177`). Não quebra os links `ctx.link(n)`, ao contrário da renumeração do 02 |
| **01 Agricultor** | O tamanho padrão perde o selo MEDIDO. "Paga trator ou adubo? Não / Sim" no lugar de "o que você paga" | Hoje a tela diz "Usando o típico daqui: 1,03 ha **MEDIDO**" (print 09) e parece que o satélite mediu o roçado dele. A outra pergunta usa as palavras dele |
| **01 Agricultor** | Plano B: se faltar tempo, ficam as telas de hoje, mas com entrada direta e as 4 perguntas obrigatórias primeiro | É uma rede de segurança real para a véspera |
| **06 Arquitetura** | Um avançar e um voltar só, na barra de baixo. O voltar do Android volta uma tela. `ctx.editar(k)` abre a pergunta tocada e devolve a pessoa ao passo de onde veio | No celular, o botão físico de voltar é o mais usado. Hoje o chip "1,0 ha" leva a "Como você planta hoje?" (`roca.js:111-113` usa `data-ir="2"` e `perguntas.js:77` zera tudo) |
| **06 Arquitetura** | "Próxima" grava o padrão como se fosse resposta | Conferido: `hoje_ideal.js:442` chama `gravar()` ao avançar. A URL do print 09 já traz `hoje=milho:50,feijao:50\|cons=1\|1chuva=1\|sem=1` sem nenhum toque. Assim, "típico daqui" não se distingue de "você disse" |
| **08 Precisão** | Terra "não sei" = interseção dos solos zoneados. Em 421 municípios o milho não tem janela na arenosa e nada avisa | Num formulário de celular, o padrão vira a resposta de quase todos, e o erro silencioso vira a regra. O aviso precisa aparecer no plano |
| **08 Precisão** | Corrigir textos errados ("acima do recorde", +R$ 909 "do baixio", "milho: nenhum dia") e usar um rótulo só para o El Niño | São 15 minutos e evitam o "vai secar ou não?" de quem lê pouco |
| **03 Valor da informação** | Medir o efeito de cada resposta: maniva "não" leva o plano de 98 para 0 em 100; custo "máquina" leva a sobra de R$ 4.364 para −R$ 1.743; arranjo, manejo, água e Garantia-Safra dão Δ R$ 0 | É a régua objetiva para decidir o que fica na tela pequena |
| **04 Júri** | Selo "MEDIDO · NASA SMAP" | "NASA" aparece 0 vezes nas 16 telas. Com essa troca, o nome aparece em todas sem mexer em cada passo. Condição: ≤ 10 caracteres depois do ponto e selo de 11 px |
| **04 / 06** | "E se chover…" no alto do passo 5 | Mudei de ideia (§7). O controle já serve ao dedo: trilho de 48 px (`cenario_chuva.css:24`) e atalhos em chip (`cenario_chuva.js:113-115`) |
| **05 Extensionista** | O botão principal do fim é "Copiar para o WhatsApp", e "Imprimir" fica em segundo | `window.print()` num Android simples confunde. O WhatsApp é o canal real até o técnico |
| **07 Visual** | `.eco` em `--muted`, selo de 11 px, nenhum cartão dentro de cartão, carrosséis viram grade | Coincide com as minhas medidas: o eco tem contraste de 2,8 : 1, os selos têm 9,5 px e os carrosséis `tend-grade`, `ss-cartoes` e `seg-cols` cortam o conteúdo |
| **02 / 03** | "Ajustar a conta" fechado, com raiz e custo | É a forma certa de esconder o que tem padrão bom. Emenda minha: a linha do resumo mostra a suposição ("Conta com raiz a R$ 0,84/kg, sem trator nem adubo · mudar"), para que o padrão não se esconda |

---

## 2. Objeções concretas

| De | Ideia | Objeção |
|---|---|---|
| **06 Arquitetura** | Tela única com 5 blocos de "botões grandes com ícone", meta ≤ 1.800 px | **1.800 px são 3,3 rolagens de formulário.** Com o botão "Ver o meu plano" fixo embaixo, quem lê pouco toca nele sem descer, e terra e maniva ficam no padrão sem que ele as veja. Os cartões de opção de hoje têm 140–176 px (`perguntas.css:13,61`; `hoje_ideal.css:31`): reaproveitados, os 4 ou 5 blocos dão ≈ 1.400 px. A tela única só funciona com **chips compactos de 48–56 px** e ≤ 640 px de altura |
| **06 / 07 / 10** | Resultado em abas novas (Plantar · Rende · Seca, ou Plano · Dinheiro · Segurança · Lugar) | Somam ~1 h de componente novo na véspera. As pílulas do topo já levam a qualquer passo (`roca.js:107-109`). Basta pôr o nome em cada pílula (hoje os passos 3–5 aparecem só como número no celular) e deixar um "próximo" linear na barra, que guia quem lê pouco. As abas ficam para depois da entrega |
| **02 Produto** | Renumerar os passos para [perguntas, plantio, dinheiro, segurança, lugar] | Quebra ~15 links (o próprio 02 admite) e o roteiro `percorrer_fluxo.py`. A entrada direta do 01 tem o mesmo efeito com 2 linhas |
| **02 Produto** | A 1ª tela são 4 fichas de resumo que abrem a pergunta grande e voltam | Cada resposta custa 2 toques e uma ida e volta. Quem lê pouco não percebe que a ficha é tocável. E a ficha mostra "Terra: não sei", justamente o que o 02 aponta como "parece produto incompleto" no topo dos passos 3–5 |
| **05 Extensionista** | 5 perguntas, mais "criação", mais a mandioca condicional: 6–7 telas e 8 toques | Vai contra o pedido do José ("perguntas desnecessárias"). Na v1, "criação" só muda texto, o que o próprio 05 admite, e esse é o critério que todos usaram para cortar a água. "Terra rasa / piçarra" (AD1) tira o milho do zoneamento e põe uma 5ª opção na pergunta mais difícil, sem teste nos 7 municípios. As duas devem virar perguntas no "Leve ao técnico" |
| **08 Precisão** | Corrigir o "não sei" da terra no `motor.py` | **O servidor importa o motor uma vez só** (`servidor.py:22`, `import motor`, sem `reload`), e o briefing proíbe reiniciá-lo. Sem reinício, a correção não chega à tela. Dá para fazer só no front: o plano diz "datas para terra que segura água; se a sua é de areia, confira com o técnico" quando terra = "" |
| **08 Precisão** | Terra como a 1ª pergunta | É a pergunta mais abstrata. Começar pelo que é familiar e já vem marcado ("o que você planta") dá confiança a quem lê pouco. A terra vem em 2º lugar, ainda acima da dobra |
| **08 Precisão** | "E se chover…" no "ver mais", aberto na chuva normal | Concordo com "aberto na chuva normal" e discordo do "ver mais". As duas medianas do milho (3,2 contra 3,9 sacos/ha) só brigam porque os cartões por cultura e o controle aparecem juntos. Com os cartões no "ver mais", o controle vira a única fonte de número visível no passo 5 |
| **04 Júri** | Página nova "Como o QUADRA sabe" (`ciencia.js`) | É mais 1 h de módulo novo. O passo 1, transformado em "Do espaço", já pode ser essa página: harmonização, satélite × pluviômetro e confiança já moram lá. Os 7 métodos e o acerto entram como um "ver mais" a mais |
| **04 Júri** | "E se chover…" como 1º bloco, antes de tudo | A 1ª dobra precisa dizer primeiro "2027 tende a ser apertado" e "olhe de novo em 19/mar e 30/abr". O controle vem logo depois, ainda dentro de 2 rolagens |
| **07 Visual** | Trocar o mono pelo Inter em todo o CSS (1 h) | Vale, mas mexe nas 16 telas de uma vez e pode desalinhar a linha do tempo e as tabelas, o que o 07 admite. Fica depois do fluxo e só se sobrar tempo. O contraste e o tamanho mínimo, sim, entram antes |
| **01 / 10** | Tela única de "cerca de 750 px" (01) e "~760 px" (10) | Passa da área útil: 780 − 60 do topo compacto − 64 da barra de baixo = **656 px**. Com o topo de hoje (107 px), sobram 550 px. A tela cabe se: topo em 1 linha, baixio com 3 chips (sem os 5 mini-desenhos de 58 px), terra 2×2 em chips, "seu olho" em 1 linha e sem faixa de El Niño. Num Android de 360 × 640 vai rolar: por isso o que tem padrão confiável fica embaixo (§5) |
| **03 Valor** | Bloco da maniva que aparece e some conforme as culturas | No celular, um bloco que surge no meio da tela empurra o botão e causa toque errado. Inferir a maniva das culturas e pôr o chip "Sem maniva? trocar" na parte A do plano |
| **03 Valor** | "O que vale mais" como 1º controle do passo 4 | O controle continua antes do resultado. Deve ficar logo abaixo das barras Hoje → Melhor → Ideal |
| **09 (eu)** | 3 telas com avanço no toque | **Retiro.** Cada resposta de terra, baixio ou mandioca grava no hash (`ctx.set` faz `location.replace`, `roca.js:144`), dispara `desenhar()` e uma chamada nova à API (62 KB sem gzip, ~1 s; medi 998 ms até a tela seguinte). São 3 esperas no 3G. A tela única com estado local faz 1 chamada |
| **09 (eu)** | Botão "Ouvir" (speechSynthesis) | Mantenho como ideia, mas rebaixo para "depois da entrega". São 45 min de código novo sem teste em Android real, e nenhuma outra lente pediu |

---

## 3. Votos

| Item | Voto | Para onde |
|---|---|---|
| hoje.culturas | **manter** | Tela única, linha 1: chips de 56 px com milho e feijão marcados ("o comum daqui"), sem a divisão em %. A % vai para "Ajustar a conta" no passo 4 (padrão: dividir igual) |
| hoje.arranjo | **inferir** | Padrão "tudo junto". "Mudar" fica no cartão Hoje do passo 4. Depende do baixio, e "junto" ou "em pedaços" dão o mesmo R$ (`hoje_ideal.js:59`) |
| hoje.manejo | **inferir** | 1ª chuva = comum, semente pelo Censo, fogo = não sei. Os conselhos ficam para todos em "O que fazer agora". Δ R$ 0 (03) |
| hist.anos | **inferir** | 2026 = 2025 = jeito de hoje, com selo SUPOSIÇÃO. No passo 3: "Se em 2025 também foi milho… · Foi diferente? 1 toque" |
| hist.deu | **mover** | Passo 5, "A sua memória": o "quebrou + ano" se responde ali mesmo, sem `ctx.link(2)`. "Deu bem" sai |
| hist.faz | **cortar** | Nenhuma tela. O equipamento fica coberto por "Paga trator ou adubo?" (bolso.custo) |
| terra | **manter** | Tela única, linha 2, acima da dobra: 4 chips 2×2 (Seca rápido · Segura · Encharca · Não sei) e 1 linha do torrão. Com "não sei", o plano avisa que a data pode não valer na areia |
| ha | **manter** | Tela única, última linha: chips ½ · 1 · 2 · 3 · 5 ha, com o típico marcado e sem selo MEDIDO; "outra medida" abre `area.js` sem mudança. Custa 0 toque |
| baixio | **manter** | Tela única, linha 3: 3 chips (Não tenho · Tenho · Não sei). Pouco, ⅓ e metade dão a mesma chamada (`ad_baixio=15`, `roca.js:49`) e só mudam a área, então o tamanho vai para o desenho do plano |
| agua | **mover** | Chip opcional em "Leve ao técnico": "Tenho barreiro ou poço perto". Não vai para a API (`roca.js:44-51`) |
| maniva | **inferir** | Mandioca marcada = "plantada"; sem ela = "consigo". O chip "Sem maniva? trocar" fica na parte A do desenho |
| bolso.prioridade | **mover** | Passo 4, logo abaixo das barras: 4 chips de 48 px que acendem o jeito em "Outros jeitos". Padrão "garantir" no El Niño |
| bolso.raiz | **opcional** | "Ajustar a conta" (fechado), com a suposição escrita na linha do resumo |
| bolso.custo | **opcional** | "Ajustar a conta": "Paga trator ou adubo? Não / Sim". A linha do resumo diz "sem trator nem adubo", porque essa resposta vira o sinal do R$ (03) |
| bolso.gs | **cortar** | 1 frase no técnico, tirada da área: "Até 5 ha você cabe no Garantia-Safra" |

---

## 4. O fluxo que defendo: o 01, com emendas

```
Globo ─► Painel ─► SUA ROÇA (1 tela, ≤ 640 px) ─► PLANO ─► RENDE ─► SE SECAR ─► WhatsApp ao técnico
   └─ "Internet fraca? Entrar sem o globo" ─► roca.html (busca)
   Pílula "Do espaço" (ex-passo 1) sempre a 1 toque, fora do caminho.
   Chips do topo do plano ─► abrem 1 pergunta (Afinar) ─► voltam ao passo de origem.
```

**Toques do painel até o plano: 2** com os padrões ("Montar" e "Ver o meu plano"), **5** respondendo terra, baixio e uma cultura. Hoje são 14.

| Tela | Na 1ª dobra (≤ 640 px) | No "ver mais" (cada um com 1 linha-resumo visível) |
|---|---|---|
| **Sua roça** | "Já marcamos o comum de Quixadá. Mude o que for diferente." · culturas · terra · baixio · tamanho · barra: **"Ver o meu plano →"** | nada |
| **Plano** (≤ 1.900 px) | ficha em 1 linha com ✎ · manchete · desenho visto de cima com o botão de ano (já existe) · **"O que fazer agora"** com 3 ações e datas | o calendário de 14 meses, a lista "2027 · o ano todo" (que sai da dobra), onde sofre (ponto 12), faixas e praga (8), o que cada planta faz (10) e parte por parte |
| **Rende** (≤ 1.900 px) | **barras Hoje → Melhor → Ideal**, com 1 número por coluna (o típico) · os ajustes do Melhor com +R$ · "O que vale mais" (4 chips) | "Ajustar a conta" (com a suposição escrita), caso ruim, El Niño, caixa, "paga o gasto?", outros jeitos. **Sai o herói repetido** "No caso ruim…" |
| **Se secar** (≤ 1.900 px) | "2027 tende a ser apertado" · **"Olhe a terra de novo em 19/mar e 30/abr"** · **"E se chover…"** aberto em 100 %, com atalhos · **Leve ao técnico** com **Copiar para o WhatsApp** | cartões por cultura com 2027/28/29, 28 anos, a memória ("Lembra de um ano que quebrou?"), o que não dá para projetar, quanto acertou |
| **Do espaço** (ex-passo 1, ≤ 1.100 px à vista) | El Niño em 1 linha · 3 números com selo NASA · "11 culturas servem aqui" com 6 ícones · confiança em 1 linha | tendências (ponto 11, só baixa ao abrir), régua, satélite × pluviômetro (3), harmonização (7), métodos (4/6), glossário (2) |

### Emendas ao 01

1. **A tela única cabe sem rolar a 390 × 780.** Isso pede chips de 48–56 px (não os cartões de 140–176 px), topo em 1 linha (107 → ~60 px) e baixio com 3 opções. Se `medir.py` der mais de 640 px, a tela se divide em 2 ("O que planta" / "Terra e baixio"), com 1 toque a mais, como prevê o risco do 03.
2. **Ordem pela confiança do padrão.** O que não tem padrão confiável fica no alto (culturas para começar, depois terra e baixio). O que tem padrão bom fica embaixo (tamanho do Censo). Num Android de 360 × 640, o que cair abaixo da dobra é o que menos erra se ficar no padrão.
3. **Estado local na tela única.** O toque não grava no hash. Quando ele toca "Ver o meu plano", o código grava tudo de uma vez e faz **1** chamada à API (hoje terra, baixio e mandioca fazem uma chamada cada, de ~1 s e 62 KB). Só o que ele tocou vai para a URL; o resto fica `""`, e o plano diz "típico daqui". Isso corrige o `gravar()` de `hoje_ideal.js:442` apontado pelo 06.
4. **Toque seguro.**
   - "Ver o meu plano" se desliga no 1º toque e mostra "Montando…".
   - O toque duplo em chip de várias escolhas não pode desmarcar sem mostrar.
   - Nas telas do Afinar que avançam no toque, os botões ficam travados até a tela mudar. É o erro que confirmei: dois toques em 120 ms pulam a pergunta do tamanho (`perguntas.js:115-120`).
5. **Navegação do 06.** O único botão principal fica na barra de baixo, com o nome do destino. O voltar do Android volta uma tela. Cada chip da ficha abre a sua pergunta e volta ao passo de origem. As pílulas ganham nome no celular.
6. **Teto medido por passo de resultado:** ≤ 1.900 px e ≤ 150 palavras com tudo fechado, e a ação na 1ª dobra (y < 700). O passo 3 é o caso crítico: hoje o bloco "Seu roçado visto de cima" vai de y = 531 a y = 2.121 (1.590 px). Ficam o desenho e o botão de ano; a lista e a grade de meses saem da dobra.
7. **"Não sei" honesto (08) feito só no front:** uma linha no plano quando terra = "". Não mexer em `motor.py` nem em `servidor.py`.
8. **Selo com missão (04)**, ≤ 10 caracteres e 11 px. Junto vão os mínimos de leitura: `.eco` a 0,5 (4,9 : 1), `summary` com 44 px de altura, letra de leitura ≥ 14 px.
9. **Rede:** tirar o `carregar()` antecipado do glossário (`glossario.js:236`, −92 KB por passo) e o link "Internet fraca? Entrar sem o globo" no globo (7,8 MB em 119 pedidos). São ~10 min.
10. **Ficam para depois da entrega:** abas, troca de fonte, a página "Como sabemos" separada, "criação", "terra rasa", "Ouvir", gzip no servidor.

**Tempo estimado:**
- 2 linhas de entrada: 5 min.
- Tela única com estado local: 1,5–2 h.
- Casca (barra, chips que voltam, mínimos de leitura): 45 min.
- Passos 3, 4 e 5 reordenados com "ver mais": 1,5 h.
- Textos (08) e selo (04): 30 min.
- `percorrer_fluxo.py`, 7 municípios e `medir.py` a 390 px: 45 min.

O total fica em **~5–5,5 h**, dentro da faixa.

---

## 5. Linhas vermelhas (não pode cortar nem quebrar)

1. **Nenhuma tela de pergunta passa de 640 px a 390 × 780**, e o plano fica a ≤ 5 toques do painel.
2. **Um único botão principal por tela**, sempre no mesmo lugar e com o nome do destino. Nada de dois verdes.
3. **A resposta de cada passo na 1ª dobra:** o desenho e "o que fazer agora"; as barras Hoje → Melhor → Ideal; as datas de olhar a terra e o técnico/WhatsApp.
4. **O padrão nunca se passa por resposta.** O que ele não tocou aparece como "típico daqui". A terra "não sei" avisa que a data pode não valer na areia.
5. **O toque duplo não pula nem desmarca** nenhuma pergunta.
6. **Voltar do Android volta uma tela**, e as respostas ficam no hash. O link mandado pelo WhatsApp reabre o mesmo plano.
7. **Os pedidos do José continuam visíveis:**
   - O jeito de hoje é a linha 1 da tela única e a coluna Hoje do passo 4.
   - A área fica a 0–1 toque (chips, tarefas e medida em `area.js`).
   - O histórico vira o cartão do giro e a memória do passo 5.
8. **Ponto 16 na 1ª dobra do passo 5:** a frase "quem decide é você, com o técnico" e o "Copiar para o WhatsApp".
9. **Os selos MEDIDO / SUPOSIÇÃO / PROJEÇÃO ficam** em todo número, com ≥ 11 px.
10. **Todo "ver mais" tem 1 linha-resumo visível.** Os pontos 8, 10, 12 e 13 não podem sumir sem chamada.
11. **Contraste ≥ 4,5 : 1 nas instruções e alvos ≥ 44 px** nos controles do caminho principal.
12. **Nada de mexer em `servidor.py` ou `motor.py`** enquanto o reinício estiver proibido.

---

## 6. Onde mudei de ideia, e por quê

- **De "3 telas, uma por pergunta" para tela única.** Ao ler o roteador, vi que cada resposta de terra, baixio ou mandioca grava no hash e refaz a chamada à API (`roca.js:144` e `desenhar()`). No 3G isso são 3 esperas de ~1 s ou mais, que eu mesmo medi (998 ms). Com estado local, a tela única faz 1 chamada. Ponho duas condições: caber em ≤ 640 px e ter chips compactos.
- **Do passo 1 antes das perguntas para "Do espaço" fora do caminho.** Eu já tinha apontado que ele repete o painel do globo. A entrada direta do 01 custa 2 linhas e não renumera nada. Ele continua encurtado, porque o júri vai abri-lo.
- **ha: de "inferir" para "manter" numa linha de chips já marcada.** Na tela única ela custa 0 toque, e o José pediu. O 01 mostra que um "plano de 1 ha" para quem tem 3 ha gera desconfiança.
- **Arranjo: de "fundir na P1" para "inferir".** Ele depende do baixio (01, 04, 06, 08), "junto" e "em pedaços" dão o mesmo R$, e o +R$ 909 do "milho no baixio" vem da troca por feijão (08).
- **Baixio: de 5 desenhos para 3 chips.** Pouco, ⅓ e metade dão a mesma chamada (`roca.js:49`), e os mini-desenhos não cabem na tela única.
- **"E se chover…": do "ver mais" para a 1ª dobra do passo 5.** Isso vale com o controle aberto em 100 % e os cartões por cultura no "ver mais", para que não apareçam duas medianas (08). O controle já é bom para o dedo, e é o ponto 13 que o júri vai tocar (04).
- **"Ouvir": de ideia do top 3 para "depois da entrega".** Faltam o tempo e o teste em Android real.
