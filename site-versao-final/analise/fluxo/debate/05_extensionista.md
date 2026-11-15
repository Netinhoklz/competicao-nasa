# 05 · Técnico de ATER: parecer da rodada de debate

Leitura de quem faz 80 visitas por ano no semiárido. Nada do site foi editado. Conferi na API (`/api/local?cod=2311306`, Quixadá, JSONs em `E:/campeonato-nasa/tmp/ext_debate/`) e no código antes de afirmar.

**Em uma frase:** fico com o fluxo da lente **01 Agricultor**: uma tela "Sua roça" já marcada com o típico daqui, entrando direto do globo. Somo a ele quatro emendas de campo: a terra e o baixio vêm antes do plano, o trator não vira "máquina e insumos", o ganho em R$ não vira manchete e a jornada termina na ficha para o técnico.

## 1. O que conferi (e muda o debate)

| Checagem | Resultado medido | Consequência |
|---|---|---|
| Terra "rasa/piçarra" (AD1), a minha proposta | Em Quixadá, AD1 dá as **mesmas janelas** que AD2 nas Partes A, B, C e nas bordas. A única diferença é o milho do baixio, que fica **"não zoneada no solo escolhido (AD1)"** quando o baixio está em "não sei": sem `ad_baixio`, o núcleo usa a AD da terra no baixio | Retiro a opção "rasa" da v1. Ela custa um botão, não muda nada em cima e quebra o milho do baixio. Vira pergunta na ficha do técnico |
| "Com areia, o milho perde o zoneamento em Quixadá" (lente 10) | **Falso.** Arenosa = AD2 (`TERRA.arenosa`, roca.js:20), e o milho do baixio fica em 21/02–28/02. Só a AD1 tira o zoneamento | O argumento da terra continua de pé: na misturada, o milho do baixio vai para 11/02–10/03 e a mandioca para 01/02–10/03 |
| Baixio "Tenho" × "Não sei" | "Tenho" (pouco/⅓/metade) manda `ad_baixio=15`, e o milho do baixio vai para 11/02–10/03. "Não sei" fica na interseção, 21/02–28/02. Os três tamanhos dão o mesmo JSON | Na tela única, "Tenho" precisa gravar um dos três valores (pouco/terco/metade), senão perde a janela larga. O tamanho só mexe em área e R$ |
| Baixio "Não tenho" | **Nenhum milho no plano** dos 3 anos. Fica a nota "Sem baixio: o cereal sai do roçado" | Quem planta milho hoje vai estranhar. O plano precisa mostrar essa frase à vista, não só em nota |
| maniva=nao / plantada | "nao" troca a mandioca por sorgo forrageiro em 6 de 9 parte-ano. "plantada" mantém o desenho e a Parte A passa a dizer "já está no chão" | Inferir pela mandioca de hoje é seguro, e o "trocar" fica na linha da Parte A |
| O "Hoje" no consórcio | `calculo.js:151` e `hoje_ideal.js:57` contam milho e feijão com **T/2 cada**. O próprio núcleo diz: "contra o consórcio de hoje, o ganho da rotação não foi medido" | Concordo com a lente 08. Até conferir a área de consórcio da PAM, o "+R$ X" não vira manchete |
| Custo "máquina e insumos" | É o desembolso CONAB (`dinheiro.js:47`): máquina, adubo, defensivo, serviço. Na medida da lente 03, a sobra vai de R$ 4.364 para −R$ 1.743 | Não dá para ligar "preparo com trator" a esse nível (ver objeção 3) |
| Assistência técnica | `padroes.pct_orientacao_tecnica = 7,3` em Quixadá | Só 7 em 100 recebem visita. "Leve para o técnico" precisa valer também para sindicato, secretaria e vizinho, e o módulo já lista esses três em "ver mais" |

## 2. Melhores ideias dos outros

- **01 Agricultor.** Entrar direto em `#/cod/2` sem renumerar os passos: são 4 pontos de código (principal.js:94, rocacerta.js:333, roca.js:194/209). É o menor risco para o mesmo ganho. Somo dois detalhes dele: "não vende" vira **"comida da criação (fora do R$)"**, e o padrão de área sai com selo de suposição, não MEDIDO.
- **01 Agricultor e 02 Produto.** Um seletor só de prioridade, dentro de "Outros jeitos" e **depois** do número. Hoje há dois seletores para a mesma coisa.
- **03 Valor da informação.** A medição de cada resposta (Δ R$, Δ datas, Δ plano). É a régua certa para cortar sem achismo, e confirmou o que eu vi: manejo, água, "deu bem", práticas e GS dão Δ 0.
- **04 Júri.** Selo com o nome da missão ("MEDIDO · NASA SMAP"), mudando só `comum.js`. A palavra NASA aparece em todas as telas sem mexer em cada passo. Também o "E se chover…" alto no passo 5.
- **06 Arquitetura.** O "mudar" abre a pergunta certa e **volta ao passo de origem**, e o voltar do Android funciona. Na visita, corrigir uma resposta não pode me mandar ao começo.
- **08 Precisão.** A terra pelo torrão (esfarela / faz bolo e quebra / gruda), com as palavras de hoje embaixo. O "encharca" engana no planossolo do sertão (encharca por cima e guarda pouca água), e o torrão separa melhor. Também as correções de texto: "acima do recorde", "Só o que muda a conta", "+R$ 909 do baixio" e a raiz "daqui".
- **09 Mobile.** O bug do toque duplo, que pula a pergunta do tamanho (perguntas.js:115-120). É mais um motivo para a **tela única**, que não tem `q += 1` para pular. Também o summary com 44 px e o eco com contraste de 4,9:1.
- **10 Simplicidade.** "2025 foi igual?" com 1 toque dentro do cartão do giro, onde o conselho aparece. Também o Garantia-Safra deduzido da área.
- **02 Produto.** Uma faixa de 1 linha com o El Niño em cima da "Sua roça": o porquê fica sem o passo 1 na frente.

## 3. Objeções concretas

1. **Lente 04 (terra no passo 3, ao lado das datas).** O plano abriria com as datas do "não sei" (interseção), e a maioria não volta para corrigir. Pela lente 08, essa interseção ainda ignora solos onde a cultura não é zoneada (milho fora de AD2 em 421 municípios). Na visita, a terra é a primeira coisa que pergunto. Ela fica na tela única, antes do plano.
2. **Lentes 08, 09 e 10 (inferir a área, sem linha).** O José pediu a área com todas as letras. A área também dá a quantidade de semente e de maniva que a família precisa juntar, que é o que o técnico confere. Pré-preenchida na tela única, ela custa 0 toque. Tirar a linha não economiza nada e esconde o pedido.
3. **Lentes 02, 06, 07 e 10 (preparo com trator → custo "máquina e insumos").** A família que usa o trator da prefeitura (patrulha mecanizada, por hora ou de graça) não compra adubo nem defensivo. Ligar trator ao desembolso CONAB faz o plano "dar prejuízo" (de +R$ 4.364 para −R$ 1.743) para quem não paga isso. O custo fica opcional, com rótulo concreto: "Só a semente" / "Pago máquina, adubo e diarista".
4. **Lentes 01 e 02 (manchete "Com 3 ajustes, o seu jeito rende R$ X a mais" e linha-ponte "+R$ 1.680 em 3 anos").** O Hoje usa T/2 no consórcio, e o núcleo diz que o ganho contra o consórcio não foi medido. Um técnico que fizer a conta de cabeça desmonta o número na banca. O número fica nas barras com PROJEÇÃO e "não medido contra o consórcio", sem manchete de ganho.
5. **Lente 02 (reordenar PASSOS, com o lugar no fim).** São cerca de 15 links numéricos (`ctx.link(n)`, `data-ir`, atalho do técnico) na véspera. A entrada direta em `#/cod/2` (lente 01) dá o mesmo efeito sem renumerar.
6. **Lente 07 (4 telas que avançam no toque, e o CSS global de mono para Inter).** O avanço automático com a API de cerca de 1 s é exatamente o que gera o pulo do toque duplo (lente 09). A troca de fonte em 74 usos de `var(--mono)` desalinha a linha do tempo e as tabelas. Se entrar, é o último item, depois de conferir a 390 px.
7. **Lente 08 (opção "Tenho baixio, e o milho já vai lá").** Junta dois fatos num toque e complica a pergunta que decide se há milho no plano. O certo é o que a própria lente 08 propõe depois: o ajuste do Melhor passa a dizer "Em cima, feijão no lugar do milho".
8. **Lente 08 (mexer no `motor.py` do "não sei").** O problema é real, mas mudar o núcleo na véspera exige rodar os 7 municípios. Na v1, só texto: o cartão diz "a data vale para a terra que segura água; na areia, confira".
9. **Lente 09 ("Ouvir" com speechSynthesis).** É boa ideia, mas não cabe no núcleo de 4–6 h, e Android simples muitas vezes não tem voz pt-BR. Fica para depois.
10. **Lente 04 (página nova "Como o QUADRA sabe").** É um módulo novo. O mesmo conteúdo cabe no passo 1 ("O lugar visto do espaço"), que continua na pílula 1. Só entra se sobrar tempo.
11. **Todas as lentes que tiram o "Por onde começar" da P1 sem frase condicional.** Inferir 2025 = 2026 acende "a terra repetiu milho" para quem já roda. O cartão diz "Se em 2025 também foi milho…" e leva o selo de suposição.

## 4. Votos

| Item | Voto | Para onde |
|---|---|---|
| hoje.culturas | manter | Tela única, linha 1, com milho e feijão marcados. Sem %. O caju entra como chip se der 15 min (pendência anterior) |
| hoje.arranjo | inferir | "Tudo junto"; o "mudar" fica no cartão Hoje do passo 4 |
| hoje.manejo | cortar | Vira conselho para todos em "O que fazer agora": esperar a janela, sem fogo, juntar a semente |
| hist.anos | inferir | 2026 = hoje e 2025 = igual, com frase condicional e 1 toque "Foi diferente?" no cartão do giro (passo 3) |
| hist.deu | mover | Passo 5, "A sua memória", respondido ali mesmo sem `ctx.link(2)`. "Deu bem" sai |
| hist.faz | cortar | Preparo, palhada e esterco viram pergunta na ficha do técnico. Não ligar ao custo |
| terra | manter | Tela única, linha 3: palavras do agricultor + torrão + "Não sei". Sem "rasa" na v1 |
| ha | manter | Tela única, linha 2, já preenchida ("típico daqui", selo de suposição), em ha e tarefas, com area.js em "outra medida" |
| baixio | manter | Tela única, linha 4: Não tenho / Pequeno / Grande / Não sei. "Tenho" grava pouco/metade, para mandar `ad_baixio=15` |
| agua | mover | Chip "Molho a roça / tenho barreiro ou poço" no "Leve ao técnico"; quem irriga vê "as datas são de sequeiro". Sai a "cisterna de beber" |
| maniva | inferir | Mandioca marcada = plantada; sem ela, "consigo". Na Parte A do plano: "Sem maniva? trocar" |
| bolso.prioridade | mover | Cabeçalho de "Outros jeitos de girar", depois do número. Padrão "garantir" no El Niño |
| bolso.raiz | mover | "Ajustar a conta" (fechado), com o "seu olho" da casa de farinha |
| bolso.custo | opcional | "Ajustar a conta": "Só a semente" / "Pago máquina, adubo e diarista" |
| bolso.gs | cortar | Chip deduzido da área ("até 5 ha: você cabe") no passo 5 e na ficha; o lembrete de adesão fica na agenda |

## 5. Fluxo preferido: o da lente 01 (Agricultor), com emendas

0. **Globo e painel**: sem mudança visual. O botão leva a `#/cod/2`.
1. **Sua roça** (1 tela, botão fixo "Ver o meu plano"): uma faixa de 1 linha com o El Niño (emenda da lente 02) e 4 linhas já marcadas: o que planta, tamanho, terra (pelo torrão, emenda da lente 08) e baixio. São 2 toques do painel ao plano com o padrão, e de 4 a 6 respondendo tudo.
2. **Seu plano**: "O que fazer e quando" no topo, depois o desenho e o cartão do giro (com 1 toque em "2025"). "Sem maniva? trocar" fica na Parte A. A forragem aparece como "comida da criação". Sem baixio, a frase "o milho fica de fora" aparece **à vista**.
3. **Quanto rende**: barras Hoje → Melhor → Ideal com PROJEÇÃO e "não medido contra o consórcio". Sem manchete de ganho (emenda minha). A prioridade fica dentro de "Outros jeitos", e raiz e custo em "Ajustar a conta". Sai o herói duplicado "No caso ruim" (lentes 04, 06, 07 e 08).
4. **Se secar**: manchete de 2027, "E se chover…" aberto (lente 04), portões de 19/mar e 30/abr, memória respondida ali, e **"Leve para o técnico" por último, com "Copiar para o WhatsApp" em verde**.
5. **Do espaço** (passo 1, pílula 1): continua inteiro para o júri, com o selo "NASA + missão" (lente 04).

Duas emendas que são minhas:
- **Ficha mais completa.** `texto()` e `papel()` de leve_ao_tecnico.js hoje mandam só a linha do roçado e as perguntas. Entram mais 4 linhas: o plano de 2027 (A, B, C, baixio), as datas de plantar, os portões e "o que juntar agora" (semente e maniva para N ha). São uns 40 min.
- **Quem confere.** O título passa a ser "Leve para o técnico ou o sindicato". Em Quixadá, só 7,3% têm orientação técnica (Censo).

## 6. Linhas vermelhas

1. Terra e baixio vêm **antes** do plano. São as duas respostas que mudam as datas e se há milho no plano. "Tenho baixio" tem que chegar ao núcleo como `ad_baixio=15`.
2. O jeito de hoje fica na 1ª tela, e o Hoje → Melhor → Ideal fica no topo do passo 4 (pedido do José).
3. A área fica à vista na 1ª tela, pré-preenchida, em ha, tarefas ou medida (pedido do José).
4. O histórico continua no produto: o "quebrou" com o ano, no passo 5, respondido no lugar, e o "2025" no cartão do giro.
5. "Leve para o técnico" com WhatsApp e a frase do ponto 16 fica no fim da jornada, à vista e fora de "ver mais".
6. Todo padrão inferido aparece como suposição ("típico daqui"), e toda frase que depende dele é condicional ("Se em 2025…").
7. Nenhuma tela promete efeito que não existe: "5 perguntas", "Só o que muda a conta", "muda o que dá para salvar".
8. O ganho do plano contra o consórcio não vira manchete enquanto o T/2 não for conferido.
9. Sem mexer no `motor.py` nem renumerar rotas na véspera. As chaves do `PADRAO` ficam iguais, e depois se roda `percorrer_fluxo.py` nos 7 municípios.
10. Os pontos 8, 10, 12 e 13 ficam com manchete de 1 linha visível, mesmo com o detalhe em "ver mais".

## 7. Onde mudei de ideia

- **Cinco telas em sequência → tela única pré-marcada.** O bug do toque duplo (lente 09), o estado em variáveis de módulo (lente 06) e o caminho de 1 toque com o padrão (lentes 01, 03 e 10) pesam mais que "uma pergunta por tela". Saio de 8 toques para 2.
- **"Rasa, de piçarra" sai da v1.** Medi: em cima, dá as mesmas janelas da areia em Quixadá, e com o baixio em "não sei" deixa o milho do baixio como "não zoneada". Vira pergunta para o técnico.
- **A criação não vira tela.** Na v1 ela só mudaria texto, e cortei a água pelo mesmo motivo. Fica o texto "comida da criação (fora do R$)" (lente 01) e, na ficha, "Sem criação: troco o sorgo forrageiro por sorgo de grão?".
- **A maniva sai da P6 condicional.** Passa a ser inferida pela mandioca de hoje, com "trocar" na Parte A, onde o efeito aparece.
- **"Todo ano no mesmo lugar?" sai da P1.** Vai com 1 toque para o cartão do giro, onde o conselho mora (lentes 07 e 10).
- **O passo 1 sai da frente.** Eu queria o botão no topo do passo 1. Mas o painel já mostra o El Niño, e a entrada direta em `#/cod/2` com 1 linha de El Niño resolve com menos risco.
