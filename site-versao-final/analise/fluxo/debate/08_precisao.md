# 08 · Debate · Lente: precisão e rigor

14/11/2026 23:11. Só leitura e medida; nada do site foi editado. Conferi no código, na API (`127.0.0.1:8090`) e em duas fontes
externas o que vou afirmar abaixo (seção "Conferido nesta rodada").

## Em uma frase

O melhor fluxo é o da **lente 03 (valor da informação)**: uma tela já preenchida, que pergunta só o que muda o plano, as datas ou o R$,
e põe cada outra pergunta onde a resposta é lida. Sete emendas de rigor vão junto; sem elas, a tela única fica mais rápida e menos precisa.

## 1. As melhores ideias dos outros

| Lente | Ideia | Por que é boa para a precisão |
|---|---|---|
| 03 Valor da informação | Medir o Δ de cada resposta e perguntar só as 5 que mudam algo (hoje, tamanho, terra, baixio, maniva) | É o critério certo, e foi medido: maniva "não" leva o plano de 98 para 0 de 100 combinações e tira R$ 2.851; custo leva a sobra de R$ 4.364 a −R$ 1.743. |
| 03 Valor da informação | O ajuste do Melhor passa a dizer "milho só no baixio, **se ainda não faz**" | Conferi `areasHoje` e `itensCen`: o lugar do milho não muda o R$ do Hoje, só o tamanho do ajuste. Basta a frase condicional; a pergunta do arranjo sai. |
| 06 Arquitetura | "Próxima" grava o padrão como se fosse resposta (`hoje_ideal.js:442`) | Conferido. Sem separar padrão de resposta, o plano e o técnico não sabem o que ele disse e o que nós supusemos. |
| 06 Arquitetura | `ctx.editar(k)`: cada "mudar" abre a pergunta certa e volta | Hoje todo "mudar" cai na 1ª de 11 telas; quem quer corrigir a terra desiste e fica com o "não sei". |
| 09 Celular | O toque duplo pula uma pergunta | Conferido em `perguntas.js:117-119`: `q += 1` antes da tela nova, com os botões antigos ativos por ~1 s. A pergunta do tamanho fica com o padrão sem ele saber. |
| 09 Celular | O "Hoje" fica rotulado "padrão do lugar" até ele mudar | Sem isso, o Hoje → Melhor → Ideal compara o plano com um agricultor médio e diz "o seu jeito". |
| 01 Agricultor | Tirar o selo MEDIDO do tamanho padrão | 1,03 ha é medido **para o município** (Censo 2017). Aplicado ao roçado dele, é SUPOSIÇÃO. Vale para todo padrão. |
| 01 Agricultor | "Não vende" vira "comida da criação (fora do R$)" | Diz a verdade da conta: a forragem está fora do R$, não vale zero. |
| 04 Júri | Selo com a missão ("MEDIDO · NASA SMAP") e um só número de chuva normal (hoje 590, 568 e 567 mm) | Rastreabilidade. Números vizinhos que não batem derrubam a confiança. Se o período for outro, o selo diz qual é. |
| 05 Extensionista | O sorgo forrageiro e a palma ocupam 2 de 9 parte-ano (6 de 9 sem maniva) sem preço, e ninguém pergunta se há criação | É um problema real do plano. Sem criação, forragem não serve. Cabe como pergunta ao técnico e como rótulo (ver objeção). |
| 05 Extensionista | "Cisterna de beber" não é água de roça | Pelo Censo de Quixadá, 83,2% têm cisterna e 2,8% irrigam. A opção induz uma resposta sem efeito. |
| 10 Simplicidade | Baixio pequeno, ⅓ e metade dão o mesmo JSON | Conferido em `roca.js:20` (só `BAIXIO_FRAC`). O tamanho é área do R$, não dado agronômico: vai para o desenho. |

## 2. Objeções concretas

| Lente | Ideia | Objeção |
|---|---|---|
| 01 Agricultor | Manchete "Com 3 ajustes, o seu jeito rende R$ X a mais" | Põe na manchete o número mais frágil. (a) Parte do ganho vem do ajuste "milho só no baixio", que na conta é só a troca de milho por feijão em cima (`hoje_ideal.js:103-106`; o próprio módulo diz que o ganho do baixio não está medido). (b) No Hoje, o consórcio conta 50% da área para cada cultura (`hoje_ideal.js:57`). O Censo conta a área cheia (milho 1,03 ha e caupi 0,95 ha num roçado de 1,03 ha). A nota técnica da PAM 2024 não diz como trata o consórcio (busquei "associad" e "consorci"): continua em aberto. (c) Sem toque, "o seu jeito" é o padrão. A manchete pode dar o R$, mas dizendo "o jeito comum daqui" até ele confirmar e com o ano ruim ao lado. |
| 01 Agricultor | Tirar o "pelo acaso seriam 3 em 10" | A frase de estatística sai, a taxa de base fica. Sem ela, "7 em 10" não diz nada. Em palavras simples: "Nos anos de mar assim, a chuva veio fraca em 7 de 10 municípios do CE. Num ano qualquer, são 3 de 10." |
| 02, 06, 07, 10 | Fundir o preparo da terra com o custo (trator = "máquina e insumos") | O nível "desembolso" é o custo CONAB de máquina, **insumos e serviços**, "de lavoura acima da média" (`seguranca.js:265`). Quem só aluga a hora de trator para gradear (é comum no CE) cairia num custo de adubo e veneno que não paga, e a sobra vira negativa: R$ 4.364 → −R$ 1.743 (medida da 03). O "Paga trator **ou** adubo?" (01, 09) tem o mesmo defeito. Ficam os dois níveis com rótulo honesto: "Só a semente" ou "Semente, máquina e adubo". |
| 03 Valor, 05 Extensionista, mim (antes) | Deixar o custo fechado em "Ajustar a conta" | É a única suposição que inverte o sinal do resultado, e não pode ficar enterrada. Basta uma linha sob as barras: "A conta supõe que você só compra a semente. Paga máquina e adubo? Mudar". |
| 02, 04, 06, 10 | Levar a prioridade para "Outros jeitos de girar", abaixo do resultado | Concordo com o lugar, mas hoje ela troca o número grande do cartão: com "garantir" (o padrão no El Niño), o cartão mostra o caso ruim e as barras mostram o típico (`dinheiro.js:147`, `hoje_ideal.js:524`). Se a prioridade descer sem desacoplar, um controle lá embaixo muda o número lá em cima. Antes de mover: a mesma estatística em barra e cartão (típico grande, ano ruim pequeno). |
| 04 Júri | Levar a terra para o passo 3, ao lado das datas | Quase ninguém vai responder, e o "não sei" vira a resposta da maioria. Hoje o "não sei" diz "uso as datas que servem em **qualquer terra**" (`perguntas.js:25`, `lugar.js:116`), e isso é falso: o motor faz a interseção só dos solos **zoneados** (`motor.py:672-678`). O milho 1ª safra não tem zoneamento em AD2 (terra arenosa) em 421 de 1.524 municípios. A terra fica na tela única. O "mudar" com "antes: …" no passo 3 é um bônus. |
| 05 Extensionista | Opção "Terra rasa, de piçarra" = AD1 | Medi em Quixadá: com AD1, só o milho e o feijão comum mudam ("não zoneada"). Caupi, mandioca e sorgo usam a textura e ficam iguais ao AD2. As faixas do plano não mudam, porque o milho já vai no baixio. O efeito é pequeno, e "rasa = AD1" é uma suposição sem base: AD1 é pouca água disponível, não profundidade, e o ZARC antigo tirava solo com menos de 50 cm. Não entra agora. |
| 05 Extensionista | Pergunta nova "Tem criação?" | Na v1, ela não muda número nenhum, e esse é justamente o motivo da queixa do José. O problema é real: vira pergunta do "Leve ao técnico" ("Sem criação, troco o sorgo forrageiro por sorgo de grão?"). O sorgo granífero tem ZARC em Quixadá, de 11/02 a 20/03. O rótulo é o da lente 01. A troca no motor fica para depois da entrega. |
| 09 Celular | Maniva "opcional" (no Afinar) | O padrão "consigo" calado erra o plano inteiro de quem não tem maniva: de 98 para 0 de 100. Fica uma linha condicional na própria tela, que só aparece quando o plano tem mandioca e ele não marcou mandioca hoje (03, 05). |
| 09, 10 | Tamanho só inferido (fora da tela) | O R$ é linear na área. Com 3 ha e um plano de 1,03 ha, o número que ele lê é um terço do dele. Numa linha já preenchida ("1 ha · o comum daqui · mudar") custa 0 toque e é pedido do José. Fica à vista. |
| 07 Visual | Um selo por cartão, no rodapé | Vale (é a regra 6 do LEIA-ME) só para blocos de um tipo. O cartão de cultura do passo 5 mistura PROJEÇÃO (2027, "quebra em X de 10") e MEDIDO (as 4 barras dos El Niños): leva os dois. |
| 01, 02, 03, 04 | Inferir que 2025 foi igual a 2026 | Pode, mas a frase "a terra repetiu milho" fica condicional ("Se em 2025 também foi milho…"), com o selo SUPOSIÇÃO e 1 toque para "foi diferente". Sem isso, afirmamos o que ele não disse. |
| 04, 09 | "Garantia-Safra: paga se perder 40% ou mais" e "você cabe (até 5 ha)" | Os 40% estão certos: Lei 15.236/2025 e Decreto 12.889/2026 (a página da Caixa ainda diz 50%). Mas "você cabe" promete demais: também contam a renda da família e a adesão do município. Texto: "Com até 5 ha, o tamanho cabe. Renda e adesão do município: confira no sindicato." |
| 09 Celular | Botão "Ouvir" (speechSynthesis) | É bom para pouca leitura, mas a voz lê datas como "11/03" de forma errada, e é trabalho novo. Fica fora das 4–6 h. Se entrar, o texto vai com as datas por extenso. |
| 03 Valor | "Culturas sem preço derrubam o Hoje" (milho + sorgo: Hoje R$ 269, plano à frente em 100 de 100) | Concordo, e é linha vermelha: com cultura sem preço no Hoje, a comparação diz "Hoje sem o sorgo (sem preço)" e não mostra "plano à frente". |

## 3. Votos

| Item | Voto | Para onde |
|---|---|---|
| hoje.culturas | manter | Tela única, linha 1. Milho e feijão vêm marcados, sem %, divisão igual. Até ele tocar, fica "o comum daqui" (SUPOSIÇÃO). A % fica no "mudar" do cartão Hoje (passo 4). |
| hoje.arranjo | inferir | "Tudo junto". O ajuste do Melhor diz "Se o milho ainda vai na terra alta: feijão lá em cima, milho só no baixio". Não muda o R$ do Hoje. |
| hoje.manejo | cortar | Sai como pergunta. "Sem fogo", "espere a janela" e "junte a semente" ficam como conselho fixo em "O que fazer agora" (passo 3). |
| hist.anos | inferir | 2026 vem do jeito de hoje; 2025 = igual (SUPOSIÇÃO). No cartão "Por onde começar o seu giro", a frase é condicional e há 1 toque "Em 2025 foi diferente". |
| hist.deu | mover | Passo 5, "A sua memória e os dados": "Lembra de um ano que quebrou?", com os piores anos do IBGE em chips, respondido ali (sem ir ao passo 2). "Deu bem" sai. |
| hist.faz | cortar | Ninguém lê esterco, palhada, faixas e preparo. Fogo e semente repetem o manejo. |
| terra | manter | Tela única, linha 2, à vista na 1ª dobra. Opções pelo torrão (esfarela, faz bolo e quebra, gruda), com "seca rápido / segura / encharca" embaixo, e "Não sei" com texto honesto. |
| ha | manter | Linha pronta na tela única: "1 ha · o comum daqui (Censo 2017) · mudar", que abre `area.js` (ha, tarefa, medida). Custa 0 toque. |
| baixio | manter | Tela única, linha 3: Não tenho, Tenho, Não sei. O tamanho (⅓ como padrão) se ajusta no desenho do passo 3. Com "não sei", o passo 4 diz "conta com ⅓ de baixio". |
| agua | mover | Chip opcional no "Leve ao técnico" (poço ou barreiro), sem "cisterna de beber". Em "Suas datas", uma linha fixa: "Datas para roça só de chuva. Irriga? Elas mudam: fale com o técnico." |
| maniva | inferir | Mandioca marcada hoje → "já plantada". Sem mandioca marcada e com mandioca no plano, aparece 1 linha condicional na tela única: "Consegue maniva? Sim · Não". No plano, chip "mandioca já no chão · mudar". |
| bolso.prioridade | mover | Cabeçalho de "Outros jeitos de girar" (passo 4), **depois** de fixar barra e cartão no típico (ano ruim pequeno). O padrão "garantir" no El Niño continua. |
| bolso.raiz | opcional | "Ajustar a conta" no passo 4, com 2–3 chips (daqui R$ 1,33 · comum no CE R$ 0,84). O padrão continua a mediana da UF, que é conservadora. Na pergunta do técnico, usar o mesmo nome do preço. |
| bolso.custo | opcional | Linha **à vista** sob as barras: "A conta supõe só a semente. Paga máquina e adubo? Mudar". Rótulos honestos, sem fundir com o preparo da terra. |
| bolso.gs | cortar | Uma linha fixa no "O que fazer agora" ou no técnico: "Garantia-Safra paga com perda de 40% ou mais. Com até 5 ha, o tamanho cabe; renda e adesão, confira no sindicato." |

## 4. O fluxo preferido e as emendas

O fluxo da **lente 03**:
- Globo e painel, sem mudança.
- Passo 1 curto: 1 tela, com o botão no alto e no fim.
- **Uma tela "Sua roça" já preenchida.**
- O plano, o rende e a segurança, cada um com a resposta na 1ª dobra.

Ele pergunta exatamente o que a medida mostrou que muda alguma coisa, e manda o resto para onde a resposta é lida. Mudei do meu fluxo de 3 telas para a tela única porque ela tem a mesma informação, em menos toques, e o bug do toque duplo some junto com o avanço automático. Do município ao plano são 4–5 toques, contando a terra.

Emendas:
1. **Ordem e 1ª dobra.** A ordem das linhas é: o que planta hoje → terra → baixio → tamanho (linha pronta) → maniva (só quando cabe). A terra é a resposta de maior efeito nas datas (13 de 13 janelas em Quixadá; 23 de 24 municípios na amostra) e não dá para inferir: precisa estar à vista num Android de 360×640.
2. **Padrão ≠ resposta.** Cada linha guarda se ele tocou ou não, e "Ver o meu plano" não grava o padrão como resposta (corrige `hoje_ideal.js:442`). Tudo que ele não tocou aparece como "o comum daqui" (SUPOSIÇÃO) na ficha, no cartão Hoje e como pergunta no "Leve ao técnico".
3. **"Não sei" honesto.**
   - Versão mínima, só texto (10 min): sai "qualquer terra" de `perguntas.js:25` e `lugar.js:116`, e entra "uso as datas das terras em que o ZARC tem a cultura aqui; confira a sua com o técnico".
   - Versão certa (30–45 min, só acrescenta): o motor devolve os solos zoneados da janela, e a tela diz "milho: só em terra que segura água ou no baixio" quando falta AD2. O plano não muda; testar nos 7 municípios.
4. **Um número por pergunta.** A mesma estatística na barra e no cartão (típico grande, ano ruim pequeno). Antes disso, a prioridade não desce. Sai o herói repetido "No caso ruim… O plano / Jeito de hoje". O "à frente em 98 de 100" vai para "ver mais" com a ressalva: não conta o erro do modelo, e o consórcio a 50% (D13) não foi conferido.
5. **Suposições que invertem o resultado ficam à vista.** Uma linha sob as barras para o custo, com rótulos honestos. Com cultura sem preço no Hoje, aparece "Hoje sem o sorgo (sem preço)" e não aparece "plano à frente".
6. **Corrigir os textos falsos ou mal atribuídos** (≈30 min no total):
   - "5 perguntas" (`lugar.js:148`)
   - "Só o que muda a conta" (`hoje_ideal.js:402`, que sai com a tela)
   - "muda o que dá para salvar" (`perguntas.js:30`, que sai com a pergunta)
   - "acima do recorde" (`seguranca.js:219`; o certo é "o mar mais quente para ago–out desde 1950")
   - "+R$ 909 milho só no baixio" (o certo é "feijão no lugar do milho em cima")
   - um rótulo só para o mar, "El Niño forte", com a taxa de base em palavras simples
   - uma frequência por cultura em 2027 no passo 5
7. **Do resto, ficam da 06 e da 09:** `ctx.editar(k)` com volta ao passo de origem, a memória de quebra respondida no passo 5, botões desligados até a tela mudar, e o selo com a missão e o período (04).

Sobre o passo 1, não brigo: tanto o curto (03, 04, 06) quanto a entrada direta pelo globo (01, 07, 10) servem à precisão. A condição é que a frase do El Niño seja uma só em todo o site.

## 5. Linhas vermelhas

1. A **terra** é perguntada antes do plano, à vista, com "não sei", e o "não sei" nunca diz "qualquer terra". No milho, isso é falso em 421 municípios.
2. **Baixio sim/não** antes do plano: tira ou põe o milho, e a janela do milho do baixio passa de 8 para 28 dias.
3. **Maniva:** nunca supor "consigo" em silêncio quando o plano tem mandioca e ele não marcou mandioca. Fica 1 linha condicional, porque o efeito vai de 98 para 0 de 100 e tira R$ 2.851.
4. **Padrão ≠ resposta:** o que não foi tocado é "o comum daqui" (SUPOSIÇÃO), nunca "o seu", e vira pergunta do técnico.
5. **Selo** MEDIDO/SUPOSIÇÃO/PROJEÇÃO em todo número. Bloco que mistura tipos leva os dois. Padrão do município aplicado ao roçado dele é SUPOSIÇÃO.
6. **A mesma estatística** no gráfico e no cartão, e um número para cada pergunta do agricultor.
7. Nenhum texto que promete efeito que não existe ("5 perguntas", "Só o que muda a conta", "muda o que dá para salvar") e nenhum número errado ou mal atribuído ("acima do recorde", "+R$ 909 do baixio").
8. **A suposição que inverte o sinal da sobra** (custo) fica à vista, e trator não vira desembolso CONAB.
9. **Hoje com cultura sem preço:** a tela não diz "plano à frente".
10. **A memória de quebra contra o IBGE** fica no passo 5 (pontos 6 e 16), respondida ali.
11. **Garantia-Safra** sem "você cabe" absoluto: faltam renda e adesão.

## 6. Onde mudei de ideia

- **ha:** de mover para manter. Numa linha pronta, custa 0 toque, e o R$ é linear na área. Um plano de 1 ha para quem tem 3 ha mostra um número que não é dele (lente 01).
- **hoje.arranjo:** de fundir (opção "Tenho, e o milho vai lá") para inferir. Conferi que o lugar do milho não muda o R$ do Hoje (`itensCen` usa só `ha.milho`), só o tamanho do ajuste, que já é uma troca de cultura. A frase condicional da 03 resolve sem a 4ª opção do baixio, que fica com 3.
- **bolso.prioridade:** de manter no topo para mover para os cenários, com a condição de desacoplar o número grande.
- **agua:** de bloco no passo 4 para chip do técnico mais uma frase fixa de sequeiro nas datas. A guarda vem sem pergunta.
- **Fluxo:** de 3 telas em sequência para a tela única da 03. A informação é a mesma, com menos toques e sem o bug do toque duplo, desde que a terra fique na 1ª dobra e o padrão fique separado da resposta.
- **Mantive:** terra pelo torrão, o "não sei" honesto, o corte do manejo, do "o que já faz" e da pergunta do Garantia-Safra, e a memória no passo 5.

## 7. Conferido nesta rodada

- `motor.py:672-678`: o "não sei" faz a interseção dos grupos `Cod_Solo` presentes na tábua, ou seja, só dos solos zoneados. Com um solo zoneado só, ele devolve a janela desse solo como geral.
- `perguntas.js:25` e `lugar.js:116`: os textos "datas que servem em qualquer terra".
- `hoje_ideal.js:56-60` e `:103-106`: "junto" e "pedaços" dão o mesmo resultado; "milho no baixio" só mexe em `milhoAlta`; `soBaixio` troca milho por feijão.
- `dinheiro.js:147` e `hoje_ideal.js:524`: com "garantir", o número grande é o p10; as barras mostram o p50 (`hoje_ideal.js:509`).
- `dinheiro.js:356` e `seguranca.js:265`: o desembolso é "máquina, insumos e serviços", "lavoura acima da média".
- `perguntas.js:117-119`: o toque duplo; `hoje_ideal.js:442`: o padrão gravado ao avançar.
- `roca.js:19-20`: o mapa da terra (arenosa AD2, mista AD3, barro AD5) e `BAIXIO_FRAC` ("" = ⅓).
- API, Quixadá, com AD1: o milho e o feijão comum ficam "não zoneada (AD1)"; caupi, mandioca e sorgo ficam iguais ao AD2; as faixas ficam iguais. Script em `E:/campeonato-nasa/tmp/precisao/rasa.py`.
- Garantia-Safra: perda mínima de 40% (Lei 15.236/2025; Decreto 12.889/2026). O "40%" do site (`dinheiro.js:376`) está certo.
- PAM 2024, notas técnicas: não há regra para culturas associadas (busca por "associad" e "consorci" no texto todo). O D13 continua em aberto.
