# 08 · Lente: precisão e rigor

14/11/2026, noite. Só leitura e medida, nada do site foi editado. Medidas feitas pela API em `http://127.0.0.1:8090`
e pela tábua do ZARC. Os scripts estão em `E:/campeonato-nasa/tmp/precisao/`: `medir.py` (efeito de cada resposta em Quixadá),
`amostra.py` (terra × janela em 24 municípios sorteados, semente 7) e `zarc_solos.py` (solos zoneados nos 1.794 municípios).

## Resumo

Das 15 entradas que o agricultor responde hoje, só 4 mudam o plano ou as datas:
- **terra**
- **baixio**, com "milho no baixio"
- **mandioca/maniva**
- **o que planta hoje**

Outras 4 mudam só o R$, ou o número que aparece em destaque, e cabem no passo 4: prioridade, preço da raiz, custo e área.
As outras 7 não entram em conta nenhuma: arranjo "junto/pedaços", manejo, 2025, deu bem, o que já faz, água e Garantia-Safra.

Proposta:
- **3 perguntas**, em ordem de ganho de precisão, todas com "não sei", e o plano logo depois.
- O que é restrição (água, custo, mercado; ponto 15) fica num bloco do passo 4.
- A memória de quebra vai para o passo 5.
- Do toque no município até o plano: **6 toques** em vez de 15.

O rigor fica, e há 7 números a corrigir. Um deles está no núcleo: o "não sei" do solo esconde que o milho não tem janela em
terra arenosa em 421 municípios.

## 1. Diagnóstico (com evidência)

| # | Problema | Evidência | Gravidade |
|---|---|---|---|
| D1 | São 11 telas de pergunta e 3 contadores diferentes ("1 de 3", "1 de 3", "1 de 5"). O botão do passo 1 promete 5 perguntas. | `passos/lugar.js:148` diz "Responder 5 perguntas", mas as telas 02 a 13 são 11 perguntas e um resumo. Mínimo de 15 toques do globo ao plano. | alta |
| D2 | Metade das perguntas não muda número nenhum. | Água: só ficha, olho e técnico (`grep ef.agua`), não vai à API (`roca.js:44-51`). Manejo (1ª chuva, queima, semente): só texto (`hoje_ideal.js:178-179, 291-298`). Garantia-Safra: "o benefício não entra na conta" (`dinheiro.js:129`). Esterco, palhada e preparo (trator/animal/enxada) não são lidos por módulo nenhum. "Deu bem" só aparece no resumo (`historico.js:286`). | alta |
| D3 | O "não sei" da terra vale "em todos os solos **zoneados**". Quando a cultura não é zoneada num solo, esse solo sai da interseção e a janela mostrada não vale nele. | `motor.py:676-678`. Na tábua 2026/27, o milho 1ª safra é zoneado em 1.524 municípios: falta o AD2 (o que o site chama de "arenosa") em **421** e faltam AD2 e AD3 em **233**. Caupi sem solo arenoso: 135 de 1.728. Ex.: Piritiba-BA, o "não sei" dá milho de 01/04 a 30/04, mas o milho só é zoneado em AD5 e AD6. | alta |
| D4 | O subtítulo "Só o que muda a conta" é falso. | `hoje_ideal.js:402`. Nenhuma das 3 chaves (1ª chuva, queima, semente) entra em `itensCen` ou `totais`. O próprio módulo diz que "não têm R$" (`hoje_ideal.js:647-648`). | média |
| D5 | O passo 5 diz "mar quente, **acima do recorde**", e isso está errado. | Texto fixo em `seguranca.js:219`. O motor diz "+2,46 ... o maior ago–out desde 1950 (**o recorde de qualquer trimestre é +2,59**)". Além disso, o mesmo mar tem 3 rótulos: "forte" (passo 1, manchete), "muito forte" (passo 1, mar agora; passo 4) e "acima do recorde" (passo 5). | média |
| D6 | O ganho de +R$ 909 do ajuste "Milho só no baixio" vem da troca de milho por feijão em cima, não do baixio. | `hoje_ideal.js:103-106` troca área de milho por feijão. `hoje_ideal.js:647` diz que "o ganho do baixio úmido não está medido". O rótulo atribui o R$ ao lugar errado. | média |
| D7 | O milho de 2027 tem 4 frequências diferentes no passo 5, e duas medianas diferentes para o mesmo cenário. | Tela 16: "quebra em 6 em 10" (projeção), "em 5 de 10 não paga a semente", "5 em 10 roças da região quebram" (chuva de 60%) e "quebrou em 2 de 4" (medido). O típico é **3,2** sacos/ha na projeção e **3,9** no controle de chuva aberto "como nos anos de El Niño". | média |
| D8 | Números repetidos na mesma tela. | Passo 1: "568 mm nesses meses" e "normal 567 mm" na mesma tela. "A chuva chega 18/01 (31/12–14/02)" aparece 2 vezes (indicador e "O ano da chuva"). Passo 4: o herói "No caso ruim... O plano R$ 2.760 / Jeito de hoje R$ 984" repete o gráfico Hoje/Melhor/Ideal logo acima (tela 15). | média |
| D9 | Perguntas fora de ordem. | O arranjo pergunta "milho no baixio" antes de perguntar se há baixio (tela 03 antes da 10). A divisão em % usa "seu roçado de 1,0 ha" antes de perguntar o tamanho (tela 02 antes da 09). O ano de 2026 é perguntado de novo depois do jeito de hoje (tela 05). | média |
| D10 | Mesma raiz, nomes trocados. | O passo 4 mostra "R$ 1,33 **daqui** · R$ 0,84 comum CE". O técnico (passo 5) pergunta "A raiz vale R$ **0,84**/kg na casa de farinha **daqui**?" (`leve_ao_tecnico.js:66`). | baixa |
| D11 | "Metade guardada" tem 2 datas. | Plano e passo 4: "guarde metade até **~10/mar**". Passo 5 e técnico: "em **19/mar** e 30/abr decidimos". E a janela boa do caupi em Quixadá começa em 11/03. | baixa |
| D12 | O passo 3 diz "O milho: nenhum dia" e o passo 2 diz "Milho 21/02 a 28/02". | `saude_solo.js:59`: conta só o risco de 20%. A janela do resumo é de até 40%. | baixa |
| D13 | Consórcio = 50% da área para cada cultura no "Hoje". Precisa conferir. | `calculo.js:151` e `hoje_ideal.js:57`. O Censo do próprio município dá milho 1,03 ha e caupi 0,95 ha por família, num roçado de 1,03 ha: no Censo, a área do consórcio conta cheia para cada cultura. Se a PAM fizer o mesmo, o "Hoje" sai pela metade. | média (a confirmar) |
| D14 | O passo 3 tem mais uma pergunta escondida ("O seu é: mais plano / típico / mais inclinado"), que só muda o desenho da erosão. | Tela 14, `vulnerabilidade.js:218-232`. | baixa |
| D15 | Passos longos demais para o celular. | Passo 1 com 4.550 px, passo 3 com 5.625, passo 4 com 6.629 e passo 5 com 6.377 (BRIEFING). | média |

### O que cada resposta muda de fato (Quixadá, 2311306)

**Terra:** muda **13 de 13 janelas**.
- Caupi (risco 20%):
  - não sei e arenosa: 11/03–20/03 (10 dias)
  - mista: 11/03–31/03 (21 dias)
  - barro: 11/03–20/04 (41 dias)
- Milho:
  - não sei: 21/02–28/02, com até 40% de risco
  - mista ou barro: 11/02–10/03, com até 30% de risco
- Feijão comum em areia: "não zoneada (AD2)".
- Na amostra de 24 municípios, a janela da leguminosa e a do milho mudam com a terra em **23 de 24**.

**Baixio = sim** (`ad_baixio=15`): o milho do baixio passa de 21/02–28/02 (8 dias, até 40%) para 11/02–10/03 (28 dias, até 30%).

**Baixio = não:** a linha do baixio sai, e o milho sai do plano.

**Maniva = não:** as partes A, B e C giram sem mandioca (sorgo no lugar).

**Maniva = plantada:** a Parte A "já está no chão" e colhe em 2027.

**Tamanho do baixio** (pequeno, ⅓, ½): não vai à API. Muda só o desenho e a área do R$, sem ganho medido.

**Área:** nenhuma janela muda. Só a escala e o R$ total, que é linear.

**Água:** nada no plano nem no R$. Só o chip "salva ~X ha" (barreiro com volume) e as perguntas do técnico.

## 2. Decisão para cada item

| Item | Decisão | Por quê | Para onde |
|---|---|---|---|
| hoje.culturas | manter | Única entrada do "Hoje" (o R$ e os alertas do passo 4). | Pergunta 2 "O que vai no roçado hoje?", **sem %**. Milho e feijão já vêm marcados, então 1 toque. A divisão em % vai para o chip "ajustar" no passo 4. |
| hoje.arranjo | fundir | "Tudo junto" e "em pedaços" dão o mesmo R$ (`hoje_ideal.js:59`; o próprio texto: "dá o mesmo R$ por ha"). Só "milho no baixio" muda a conta. | Na pergunta 3, opção "Tenho baixio, e o milho já vai lá". |
| hoje.manejo | cortar | 1ª chuva, queima e semente não entram em conta. São conselhos que valem para todos e já estão no calendário: "Junte semente... e nada de fogo", "Prepare a terra, sem fogo". | Ficam no "O que fazer agora" do passo 3. |
| hist.anos | inferir | 2026 = jeito de hoje (o código já pré-marca: `historico.js:218-221`). 2025 só serve para "capim repetiu". O efeito que o plano usa (leguminosa antes do cereal, +24%) é de 1 ano. | "Por onde começar o giro" do passo 3, calculado do hoje. Ex.: "Onde foi milho em 2026, comece com o caupi". |
| hist.deu | mover | "Deu bem" não é usado. "Quebrou + ano" só serve à memória contra o IBGE (validação; pontos 6 e 16). | Passo 5: "Lembra de um ano que quebrou?", com toque num dos piores anos do IBGE. |
| hist.faz | cortar | Esterco, palhada e preparo não são lidos. "Não queimo" e "guardo semente" repetem o manejo. "Faixas" só gera uma frase de reforço. | Nenhum. |
| terra | manter | É a resposta que mais muda o plano (ver acima). Vira a pergunta 1. Opções pelo **torrão**, porque a textura do ZARC é granulometria: "Esfarela (areia)", "Faz bolo e quebra (misturada)", "Gruda (barro)". As palavras do Vicente ficam embaixo ("seca rápido / segura / encharca"). "Encharca" sozinho confunde planossolo (topo de areia, pouca água guardada) com barro. | Pergunta 1. Ao tocar, mostra 1 linha com a data que mudou. |
| ha | mover | Nenhuma data depende dela. Só a escala, o R$ total e o limite de 5 ha do Garantia-Safra. O padrão do Censo (1,03 ha) serve. | Chip "1 ha (típico daqui) · mudar" no topo dos passos 3 e 4, que abre o `area.js` (hectare, tarefa ou medida). |
| baixio | manter | Muda o plano (o milho sai ou fica) e a janela do milho (de 40% para 30% de risco). Num toque: "Não tenho / Tenho, e o milho vai lá / Tenho / Não sei". | Pergunta 3. O tamanho (pequeno, ⅓, ½) fica no padrão ⅓ e se ajusta no desenho do passo 3. |
| agua | mover | Não entra no plano nem no R$. Mas é o ponto 15 e serve de guarda: com poço ou irrigação, as janelas do ZARC (sequeiro) não valem. | Bloco "Seu jeito de trabalhar" no passo 4 (água, custo, mercado), com o aviso de irrigado e o "salva ~X ha" do barreiro. |
| maniva | inferir | Muda muito (gira com ou sem mandioca; "já plantada" protege 2027). Sai do hoje: mandioca marcada → "já plantada" (ciclo de 12–18 meses: a de 2026 está no chão em 2027). | Pergunta 2. Sem mandioca marcada, aparece uma linha: "Consegue maniva? Sim · Não". No plano, chip "mandioca já no chão · mudar". |
| bolso.prioridade | manter | Decide o número em destaque (caso ruim ou típico) e o jeito recomendado (ponto 9). Padrão: "garantir" no El Niño. | Passo 4, "Seu jeito de trabalhar". |
| bolso.raiz | opcional | É o número que mais pesa no R$ (`hoje_ideal.js:653`). O padrão (mediana da UF) é conservador. | Passo 4, 3 chips. Corrigir "daqui" na pergunta do técnico. |
| bolso.custo | opcional | Muda a base da "sobra": "paga o gasto" em 2027 vai de 3 de 4 para 0 de 4. | Passo 4, 2 chips, junto da água (equipamento, ponto 15). |
| bolso.gs | cortar | Nenhum número depende do sim/não. | Uma linha fixa "Garantia-Safra: você cabe (até 5 ha)" no "O que fazer agora" (a adesão já está na agenda do motor). |

## 3. Fluxo proposto, tela a tela

0. **Globo** (`index.html`, sem mudança): escolhe o município, o painel "Roça Certa" mostra o El Niño do estado e a estação.
   Toque: "Montar o plano do meu roçado".
1. **O seu lugar** (passo 1, uma tela e meia):
   - Manchete do El Niño, com uma definição: "o mar já está em El Niño forte; nos anos assim, a chuva veio fraca em 7 de 10 municípios do CE (o acaso daria 3)".
   - 3 indicadores: a chuva chega por volta de 18/01; chove de jan a abr (568 mm); o solo hoje.
   - As culturas recomendadas, com a data "em qualquer terra".
   - A confiança em 1 linha.
   - Toques: "3 perguntas e o plano fica seu" ou "ver o plano com o típico daqui".
2. **Pergunta 1 · Sua terra:** 3 torrões e "não sei", mais o "seu olho" do torrão. Um toque avança. A tela seguinte mostra, no topo,
   "terra de barro: caupi de 11/03 a 20/04".
3. **Pergunta 2 · O que vai no roçado hoje?**
   - Grade: milho, feijão, mandioca, sorgo, palma, caju, outra. Milho e feijão já marcados.
   - Sem mandioca marcada, uma linha: "Consegue maniva? Sim · Não".
   - Toque: "Seguir".
4. **Pergunta 3 · Tem baixio?** 4 cartões com mini-roçado: "Não tenho / Tenho, e o milho vai lá / Tenho / Não sei", mais o "seu olho" de depois
   da chuva. Um toque leva ao plano.
5. **Seu plano** (passo 3):
   - Fila de chips das respostas, cada um com "mudar": terra, 1 ha típico, baixio, mandioca.
   - **Suas datas**: 3 culturas, com "antes: …" quando a resposta mudou a data. O código já faz isso em `perguntas.js:48`.
   - Roçado visto de cima em 2027, com ⅓ ou ½ do baixio ajustável ali.
   - "Por onde começar", tirado do hoje.
   - "O que fazer agora": 3 próximos itens, com sem fogo, semente, maniva e Garantia-Safra.
   - 4 linhas "o que cada planta faz pelo solo".
   - Em "ver mais": a rotação de 3 anos, "por que faixas" (simulador), erosão e ladeira, calor, parte por parte.
6. **Quanto rende** (passo 4):
   - "Seu jeito de trabalhar": o que vale mais, água, paga máquina?, preço da raiz. Tudo já preenchido.
   - Um herói só: Hoje → Melhor → Ideal, com os ajustes.
   - 1 linha: "2027 é o ano mais apertado: −R$ 138 em abr/27".
   - Em "ver mais": "se 2027 for como 1998/2010/2016/2024", o caixa mês a mês, "paga o gasto?", outros jeitos de girar, como calculamos.
7. **Segurança** (passo 5):
   - Manchete.
   - Um cartão por cultura: 2027 "quebra em X de 10" (PROJEÇÃO) com as 4 barras dos anos de El Niño (MEDIDO); 2028–2029 numa linha.
   - "Lembra de um ano que quebrou?", com chips dos piores anos e a resposta "bate / não bate".
   - "Vamos olhar de novo em 19/mar e 30/abr".
   - **Leve ao técnico**: cada "não sei" vira uma pergunta. Imprimir e WhatsApp.
   - Em "ver mais": e se chover (controle), os 28 anos, o que não dá para projetar, quanto já acertou.

## 4. O que muda nos passos

**Passo 1**
- **Cortar** "O ano da chuva aqui": repete "a chuva chega" e "meses de chuva".
- **Cortar** a "Chuva da estação, normal 567 mm": é o mesmo número de "568 mm".
- **Mover para "ver mais"**:
  - as 6 tendências (o mapa do globo já tem calor e água guardada no tempo, ponto 11);
  - "o mar agora +2,5 °C";
  - satélite × pluviômetro;
  - a tabela técnica.
- **Mostrar** só as culturas recomendadas, mais o milho com o aviso.
- **Mudar** o botão de "5 perguntas" para "3 perguntas".

**Passo 2:** são as 3 perguntas acima. Some a tela "Pronto": as datas e as fichas vão para o topo do passo 3.

**Passo 3**
- **Juntar** o resumo no topo.
- **Mover o tamanho do baixio** para o desenho.
- **Mover para "ver mais"**:
  - "Onde o roçado sofre mais", com a pergunta da ladeira;
  - "Por que em faixas" (deixar 1 frase à vista);
  - os números dos 4 cartões de solo;
  - "Em 3 anos, parte por parte".
- **Corrigir** "o milho: nenhum dia" para "nenhum dia com risco baixo (20%)".

**Passo 4**
- **Cortar** o herói repetido: "No caso ruim... O plano / Jeito de hoje" repete o Hoje/Ideal.
- **Juntar** o bolso e a água em "Seu jeito de trabalhar". O Garantia-Safra vira uma linha.
- **Mover para "ver mais"**: "Se 2027 for como…", "Quando o dinheiro entra", "A colheita paga o gasto?", "Outros jeitos de girar".
- **Corrigir** o rótulo do ajuste para "Em cima, feijão no lugar do milho: +R$ 909", com a nota "o ganho do baixio não está medido".
- **Mover** "à frente de hoje em 100 de 100" para "ver mais", com a ressalva de que a conta não inclui o erro do próprio modelo.

**Passo 5**
- **Corrigir** "acima do recorde" (`seguranca.js:219`) para "o mar mais quente para ago–out desde 1950".
- **Uma frequência por cultura** em 2027. As outras vão para "ver mais".
- **2028 e 2029** numa linha.
- **"E se chover…"** vai para "ver mais", aberto na chuva normal (aberto no El Niño, o típico diverge da projeção: 3,9 × 3,2).
- **Memória**: um toque no ano.
- **Leve ao técnico**: manter, e corrigir "daqui" na pergunta da raiz.

**Núcleo (`motor.py`, ~45 min)**
- Em `_decs` e `janela`, com "não sei", marcar `so_em` quando a cultura não for zoneada em todas as classes (textura 1–3, ou AD2/AD3/AD5 do mapa do site).
- Na tela, aparece "milho: só em terra que segura água ou no baixio".
- O plano não muda: o milho já fica no baixio.

**Rótulos:** um só para o mar, "El Niño forte" (a classe que escolhe os anos parecidos), com o valor no detalhe. Uma frase única em "ver mais":
"El Niño forte = ONI de out–jan ≥ 1,5: 1998, 2010, 2016 e 2024. A chuva por satélite começa em 1998, por isso a chuva conta 3 anos
e a colheita conta 4".

## 5. Toques até ver o plano

Hoje são **15**: município, montar, "5 perguntas", culturas, arranjo, manejo, anos, deu, faz, terra, tamanho, baixio, água, maniva e "Ver como plantar".

Na proposta são **6**: município, montar, "3 perguntas", terra, "Seguir", baixio. Com o atalho "ver com o típico daqui", são **3**.

## 6. Riscos

- **Maniva inferida.** Inferir "já plantada" a partir de "mandioca hoje" erra para quem já arrancou tudo. Mitigação: chip "mandioca já no chão · mudar" no plano.
  O botão "Já está plantada: avisar o plano" já existe.
- **Consórcio no R$ (D13).** Conferir a nota metodológica da PAM sobre culturas associadas antes da demo (30 min). Se a área contar cheia
  para cada cultura, o "Hoje" está pela metade e o "plano à frente em 98 de 100" pode virar. Até conferir, "à frente de hoje" fica só no "ver mais".
- **Terra → AD é suposição.** O mapa é arenosa AD2, mista AD3, barro AD5 e baixio AD5, e precisa do selo SUPOSIÇÃO na tela. O torrão diminui
  o erro do "encharca" no planossolo, mas não substitui o técnico.
- **Histórico e pedido do José.** Cortar o histórico mexe num pedido dele ("saber o que já plantou"). Mitigação: 2026 = jeito de hoje (perguntado),
  e a memória fica no passo 5. Dizer isso a ele com essas palavras.
- **Pontos do desafio escondidos.** Mandar tudo para "ver mais" esconde do júri os pontos 2, 3, 7, 12 e 13. No vídeo de 30 s, abrir 2 ou 3 "ver mais".
- **Motor às vésperas.** A mudança no `motor.py` vem na véspera da entrega. Testar nos 7 municípios e conferir que o plano e as janelas
  com terra respondida não mudam: só o texto do "não sei".
- **Estado global do `perguntas.js`.** As variáveis `fase`, `q` e `telaForcada` são globais. Ao reescrever, o "mudar" das fichas precisa reabrir a pergunta certa:
  rodar `testes/ferramentas/percorrer_fluxo.py`.

## 7. As 3 ideias que mais importam

1. **Perguntar só o que muda o plano, na ordem do ganho:** terra, o que planta hoje (a maniva sai daí) e baixio (com o "milho vai lá").
   O resto vira padrão visível com "mudar" ou vai para o passo 4 como restrição (ponto 15). São 6 toques em vez de 15.
2. **"Não sei" honesto:**
   - Corrigir a interseção que ignora solo não zoneado: o milho não tem janela em terra arenosa em 421 municípios e o "não sei" não avisa.
   - Cada "não sei" aparece como chip no plano e vira pergunta do "Leve ao técnico".
   - Mostrar na hora a data que a resposta mudou.
3. **Um número por pergunta do agricultor:**
   - Um herói por passo: Hoje → Melhor → Ideal no passo 4 e "quebra em X de 10" por cultura no passo 5.
   - Um rótulo para o El Niño.
   - Corrigir os números errados ou mal atribuídos: "acima do recorde", "Só o que muda a conta", +R$ 909 do baixio e a raiz "daqui".

## Implementação (cerca de 5 h)

| Bloco | Arquivo | Tempo |
|---|---|---|
| 3 perguntas, a maniva inferida, o baixio de 4 opções e o fim do resumo | `passos/perguntas.js` e `roca.js` (o `hoje` gravado com `mbx`) | 1,5 h |
| Topo do passo 3 (datas com "antes", chips, baixio no desenho) e os "ver mais" | `passos/plantio.js` | 45 min |
| "Seu jeito de trabalhar", o herói único, os "ver mais" e o rótulo do ajuste | `passos/dinheiro.js` e `extras/hoje_ideal.js` | 1 h |
| "Acima do recorde", uma frequência, o controle de chuva no "ver mais" e a memória com toque | `passos/seguranca.js` e `extras/historico.js` | 45 min |
| "Ver mais" e o botão "3 perguntas" | `passos/lugar.js` | 30 min |
| `so_em` no "não sei" | `nucleo/motor.py` | 45 min |
