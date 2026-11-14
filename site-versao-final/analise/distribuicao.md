# Plantação e distribuição no roçado (distribuicao)

## Resumo
A tela "como plantar e distribuir" deve sair do plano() e da agenda() do José, sem motor novo no servidor. Ela vira um desenho SVG do roçado visto de cima: as partes A/B/C vão em faixas em nível (A B C A B C), o baixio fica embaixo, a borda de palma + gliricídia contorna o roçado e o tamanho vem da resposta "área do roçado". Do PercolaCampo do Vicente vale aproveitar a linguagem visual e uma única regra que tem fonte: o limiar χc≈0,593 do monocultivo em malha quadrada (Alonso-Tlali 2025, que também estuda faixas alternadas e xadrez). Os coeficientes do motor dele não aparecem nos PDFs da pasta artigos, nem no artigo de 2026, que não está lá. São eles k_faixas 0,56, k_xadrez 0,72, χc 0,88–0,92, q 1,35, α 4,8, d0 em cm e "% protegida = 108 − 34·R_eff". Por isso não devem ir para a tela como número. No lugar deles proponho calcular a conectividade de verdade sobre o desenho, com as mesmas definições do MANIFESTO de percolação do José (p, S = fração no maior aglomerado, "atravessa"). Rodei essa prova para Quixadá (3 ha, 1/3 de baixio). Em blocos lado a lado, a gramínea forma um só aglomerado que desce do alto até o baixio em 2027 e 2028. Em faixas em nível na ordem B, C, A (a A encosta no baixio), ela fica em 3 blocos separados, sem nenhum contato gramínea com gramínea nos 3 anos. A mesma prova achou um ponto fraco do plano onde não há mandioca apta (Arapiraca): 77–80% do roçado fica com gramínea todo ano, e há ponte verde temporal nas partes B e C. Até amanhã cabem o desenho, a troca de ano 2027/28/29, o controle mês a mês sobre as barras da agenda e o selo de conectividade. Ficam para depois o polígono desenhado no mapa, a orientação pelo NASADEM, o vento e o espaçamento com fonte.

## Recomendações
- **P0** (3 h) Trocar rocado() por rocadoSvg(plano, agenda, respostas): o roçado em escala (quadrado com a área da resposta), o baixio embaixo, as partes A/B/C em 6 faixas em nível (A B C A B C, 3 faixas se cada uma ficar com menos de 10 m), a borda no perímetro, a área de cada faixa no rótulo e as cores de estilo.css. — É a tela que o José pediu, e todos os dados já vêm de /api/local. Não muda o motor nem o estudo financeiro (mesmas áreas de 10_familia.py).
- **P0** (1 h) Escolher a ordem das faixas por força bruta (as 6 permutações de A, B e C), minimizando os contatos gramínea com gramínea entre faixas vizinhas e com o baixio nos 3 anos. Mostrar a ordem escolhida e o porquê numa frase. — É a regra do PercolaCampo que tem fonte (barreira entre suscetíveis, Alonso-Tlali 2025; Ramírez 2018). Em Quixadá e Barreiras ela zera os contatos e corta o caminho morro abaixo. São 20 linhas de JS.
- **P0** (1 h) Botões 2027 | 2028 | 2029 com transição de cor por faixa (a letra fica, a cultura muda), uma seta 'o que entrou aqui no ano passado' e o selo 'mandioca do ano anterior ainda no chão = tampão'. — A rotação só se entende vendo a cultura trocar de faixa. Hoje são 3 quadradinhos lado a lado.
- **P0** (2 h) Controle mês a mês (nov/2026–dez/2027) que lê agenda.linhas[].barras e pinta cada faixa pelo estado do mês (preparo, plantio, crescendo, colheita, descanso/palhada), com os marcos (P1–P5, 19/mar, 30/abr) no trilho. Em 2028 e 2029, só a vista por ano. — Liga o desenho ao calendário que já existe, com uma fonte só para as datas. A agenda só vai até dez/2027 (motor.py:555), por isso o mês a mês para aí.
- **P1** (1.5 h) Selo de conectividade por ano, calculado no navegador (union-find numa grade de 5 m): a gramínea ocupa p% do roçado em N blocos; ela 'desce até o baixio' sim ou não. Ao lado, a frase fixa 'não segura a lagarta-do-cartucho (a mariposa voa longe); ajuda contra o que anda pelo chão e pela água'. — Usa as definições do MANIFESTO do José (p, S, atravessa) no lugar dos coeficientes sem fonte do Vicente, e é honesto sobre o alcance.
- **P1** (1 h) Aviso quando a gramínea passar de 59% do roçado num ano ou repetir na mesma faixa em anos seguidos (Arapiraca), com a sugestão de o técnico trocar um sorgo forrageiro por pousio pastejado, leguminosa ou palma. Mudar o plano() fica a critério do José. — Achado concreto: sem mandioca apta, o giro tem 2 fases de sorgo forrageiro (motor.py:684-687). O PercolaCampo agrega exatamente aí.
- **P1** (1 h) No baixio, desenhar linhas alternadas milho/caupi (1:1, suposição), que trocam de paridade a cada ano ('as linhas trocam de lugar'). As linhas de caupi ficam vazias até a data do revezamento (50–85 dias depois do milho). — É o 'consórcio em linhas alternadas' do PercolaCampo dentro do que o plano já manda (motor.py:688 e 921-936).
- **P2** (2 h) Reaproveitar a animação 'Dia 1 a 15' do PercolaCampo sobre o nosso desenho (um foco num ponto do alto, espalhando só por vizinho do mesmo grupo e morro abaixo), com o rótulo 'ilustra o mecanismo; não prevê perda'. — É visual e fácil de entender, mas sem dado de praga medido. Só depois do essencial.
- **P2** (8 h) Depois da entrega: o polígono do roçado desenhado no mapa do João, a orientação das faixas pelo aspecto do NASADEM (CE) ou pela declividade de 1 km (NE), a direção do vento (POWER WD2M, uma chamada por município, com cache), o espaçamento e a densidade com fonte (Embrapa/CONAB). — Mais fidelidade, mas cada item pede dado ou leitura nova.

## Achados
- **O plano do José já tem tudo o que o desenho precisa, menos a geometria**: O plano() devolve 5 'faixas' (Parte A/B/C, Baixio, Bordas), cada uma com cultura e tipo por ano de 2027 a 2029. A agenda() devolve, por parte e estação, as barras de/até com o tipo (preparo, plantio, risco, roça, colheita, pousio) de nov/2026 a dez/2027. Nada diz o tamanho nem a posição das partes: a proposta deixa esse tamanho 'para a família com o técnico', e o estudo financeiro supõe 3 faixas de 2/3 ha, 1 ha de baixio e bordas que não tiram área. _[protótipo/motor.py:646-736 (plano), 863-918 (agenda), 555 (VIS_INI/VIS_FIM); proposta/PROPOSTA_FINAL_v3.md:939 e 946; notebooks/secoes_financeiro/10_familia.py:22-23 e 56]_
- **O desenho atual (rocado()) é um esquema de 3 colunas sem escala**: O rocado() desenha uma grade CSS de 3 colunas A/B/C, mais uma tarja de baixio e a legenda 'borda verde'. Não tem área, ordem espacial, linhas de plantio nem estado do mês. É o ponto de partida natural, e as cores por tipo já existem e podem ser reaproveitadas. _[protótipo/static/app.js:262-272; protótipo/static/estilo.css:62-87 (cores t-/f- por tipo)]_
- **PercolaCampo: o limiar e as configurações têm fonte; os coeficientes do motor não**: Confirmado no PDF: χc = 0,59274621 para monocultivo em malha quadrada com vizinhos próximos, e as configurações 'colunas intercaladas' e 'xadrez' (diagonais), em Alonso-Tlali 2025. Ramírez 2018 compara 'alternate rows'. Não aparecem nos PDFs: k_faixas 0,56 (o '0,56' só aparece como eixo de figura), k_xadrez 0,72, χc 0,88–0,92, '65%' e '25–40%' de ganho. O artigo González-Martínez 2026 (q = 1,35, α = 4,8) não está em artigos/. O motor v3 tem fatores ad hoc: T_eff×2,35, crioula 0,76, '% protegida = 108 − 34·R_eff', d0 = 52 cm para o milho. Os terrenos e o vento são fictícios (FARM_TERRAINS). _[Texto extraído com pypdf em scratchpad/analise10/distribuicao/pdfs.py e ctx.py; contagem de '0.88', '0.92', '65%', '0.78' = 0 em entropy-27-00386, PhysRevE 98 e PhysRevE 101; colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_...html:878-881 e 925-959; dossiê:95-108]_
- **Poggi 2013 e With 2002 foram esticados além do que medem**: Poggi 2013 mediu espaçamentos de 22 a 54 mm em bandejas de mudas (Rhizoctonia em couve-flor). Levar isso para 'd0 = 52 cm no milho' é extrapolação. With 2002 trabalha com parcelas de 16×16 m de trevo. O limiar claro é o de lacunaridade abaixo de 20% de habitat; para a C. maculata, a resposta 'pode ocorrer' perto de 40% e só em paisagem fragmentada. A 'regra dos 40%' é uma leitura frouxa. _[PHYTO-02-13-0033-R.pdf ('inter-plant spacings of 22, 26, 34, 44, and 54 mm', 'propagation trays'); with2002.pdf ('threshold in lacunarity below 20% habitat'; 'higher levels of habitat (<40%)')]_
- **Prova: faixas em nível na ordem certa separam a gramínea; blocos lado a lado a ligam do alto ao baixio**: Quixadá, 3 ha, baixio 1/3, células de 5 m, vizinhança 4. Com os blocos A|B|C, 2027 e 2028 têm gramínea em p = 0,56 da área, num só aglomerado (S = 1,0) que atravessa de cima até o baixio. Com faixas em nível B C A B C A (a A, que nunca é gramínea em Quixadá, encosta no baixio), a gramínea fica em 3 blocos (S = 0,60–0,63; o maior é o próprio baixio), sem caminho morro abaixo, com 0 contatos gramínea com gramínea em 3 anos. Barreiras tem o mesmo plano e dá o mesmo resultado. O 'atravessa' horizontal é trivial (a faixa ocupa toda a largura): o que importa é o atravessar morro abaixo, por onde corre a água. _[E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 scratchpad/analise10/distribuicao/layout_sim2.py (planos de /api/local salvos em quixada.json, barreiras.json, arapiraca.json)]_
- **Onde não há mandioca apta, o plano fica com 2/3 de gramínea todo ano e tem ponte verde**: Arapiraca: A = sorgo forrageiro/caupi/sorgo forrageiro, B = caupi/sorgo forrageiro/sorgo forrageiro, C = sorgo forrageiro/sorgo forrageiro/caupi, e milho no baixio todo ano. A gramínea fica em 0,67 da área sem baixio e em 0,77–0,80 com baixio de 1/3, acima de 0,593 todo ano. Nenhuma ordem de faixas evita contato (7 contatos em 3 anos). Há ponte verde temporal (gramínea no mesmo lugar em t e t+1) em B (2028→29) e C (2027→28). A causa: sem mandioca, o giro é forragem → leguminosa → pos_leg, e pos_leg = cel(seco) = sorgo forrageiro. Duas das três fases são gramínea. _[protótipo/motor.py:672-687; saída de scratchpad/analise10/distribuicao/plano.py ('fracao graminea por ano [0.67, 0.67, 0.67]'; 'ponte verde temporal em Parte B / Parte C / Baixio')]_
- **Separar gramíneas não segura a lagarta-do-cartucho; o ganho é contra o que anda pelo chão e pela água**: A própria proposta diz que a mariposa voa de ~100 a 250 km e que milho ou sorgo existem em 98,3% dos município-anos do CE. Dentro de um roçado de 3 ha (cerca de 173 m de lado), qualquer raio a partir de 300 m liga tudo, e os dados do José mostram S(300 m) alto até nas AOIs do CE. A regra de percolação dentro do roçado só faz sentido para quem se espalha por contato, solo ou água: Phytophthora (os zoósporos de Ramírez 2020 vão pela água do solo), nematoide, fungo de raiz. A tela precisa dizer isso. _[proposta/PROPOSTA_FINAL_v3.md:962; E:/campeonato-nasa/dados/percolacao/MANIFESTO.json; metricas.csv (sertao_central, ponte verde, 300 m: S = 0,313; apodi 0,565); PhysRevE.101.032301 (título: Phytophthora zoospores)]_
- **Os dados de percolação do José são de paisagem (40 km, 30 m), não do roçado**: cenarios.csv mostra que girar uma fração f dos talhões da ponte verde reduz o maior aglomerado: em Apodi, de 0,577 (f = 0) para 0,251 (f = 0,5). A curva é ruidosa (0,511 em f = 0,3). O dado só existe para 4 AOIs do CE e 6 dos EUA. Serve como cartão 'o seu roçado na paisagem' (contexto), não como regra de desenho por município. _[E:/campeonato-nasa/dados/percolacao/cenarios.csv (pivot em scratchpad/analise10/distribuicao/perc.py); metricas.csv: p da lavoura no sertão central = 0,005, Cariri 0,042, Apodi 0,158]_
- **Não há no repositório fonte de espaçamento ou densidade para as culturas do plano**: A única densidade com fonte é a de Souza et al. 2011 (Petrolina, irrigado): caupi solteiro com 80 mil plantas/ha e consorciado 1:1 com o milho com 40 mil. Para milho, mandioca, sorgo e palma no sequeiro não há fonte lida. Nos CSVs da CONAB pode haver quantidade de semente por ha (não conferi). As linhas do desenho têm que ser ilustrativas e trazer o rótulo 'espaçamento com o técnico'. _[grep 'plantas/ha|espaçamento|entre linhas' em pesquisa/*.md, proposta/*.md e catalogo_rotacoes.json: só pesquisa/catalogo_rotacoes_comprovadas.md:158 (Souza 2011)]_
- **O relevo e o vento existem só em parte**: Há relevo SRTM por município só no CE (srtm_municipios_ce.parquet: frac_plano_0a3, frac_suave_3a8, frac_ondulado_8a20 etc.; Quixadá 41,8% / 43,8% / 7,9%). Há NASADEM e aspecto de 30–90 m do CE e declividade do NE a 1 km. Isso não define o baixio de um roçado: o baixio tem que ser pergunta. No cache do POWER há velocidade do vento (WS2M), mas não a direção, e a 'borda contra o vento' do PercolaCampo depende dela. _[dados_resumo/derivados/srtm_municipios_ce.parquet; E:/campeonato-nasa/dados/srtm/ (aspecto_ceara_90m.tif, declividade_nordeste_1km.tif); E:/campeonato-nasa/dados/power/power_ne_mensal.nc (variáveis: ... WS2M, sem WD)]_

## Reaproveitar
- protótipo/static/app.js:262-272 (rocado) e estilo.css:62-87 (cores t-/f- por tipo) → site-versao-final/static/js/distribuicao.js: Trocar a grade CSS por um SVG em escala, mantendo as mesmas classes de cor e a legenda TIPOS (app.js:258).
- protótipo/motor.py:646-736 (plano) e 863-936 (agenda, _revezamento) → API /api/local do site-versao-final: Consumir sem mudar no P0. As faixas dão a cultura por ano, e as barras dão o estado do mês e o revezamento do baixio.
- colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_...html:1194-1290 (renderFarmSvg) e 1064-1123 (onda Dia 1–15) → site-versao-final/static/js/distribuicao.js (P2): Aproveitar o estilo visual: plantas como pontos, faixa protetora em quadradinhos, curvas de nível e a animação do foco. Trocar o motor de coeficientes (linhas 915-985) pelo cálculo de aglomerado sobre o nosso layout, com o rótulo 'ilustra o mecanismo'.
- colegas/vicente/pesquisa_vicente/dossi_completo_projeto_percolacampo_hackathon_nasa.md (seção 1.1 e tabela 1) e os PDFs de artigos/ → texto da tela e aba de fontes: Citar só o que foi conferido (χc = 0,5927; faixas e xadrez em Alonso-Tlali 2025; linhas alternadas em Ramírez 2018; zoósporos pela água em Ramírez 2020) num 'por que em faixas' de 2 frases.
- E:/campeonato-nasa/dados/percolacao/MANIFESTO.json, metricas.csv e cenarios.csv → selo de conectividade; cartão de contexto (P2): Mesmas definições (p, S, atravessa, ponte verde) no selo do roçado. Na Ceará, um cartão opcional 'o seu roçado na paisagem' com a curva S2 vs f das 4 AOIs.
- notebooks/secoes_financeiro/10_familia.py:22-23 e 56 → contrato entre distribuição e financeiro: Usar as mesmas áreas (faixas iguais, baixio informado, bordas sem tirar área), para que a tela financeira some as mesmas faixas que o desenho mostra.
- scratchpad/analise10/distribuicao/layout_sim2.py → testes do site-versao-final: Portar para JS a lógica da ordem ótima (6 permutações) e do aglomerado (ndimage.label ≈ union-find). Os números de Quixadá e Arapiraca servem de teste.
- dados_resumo/derivados/srtm_municipios_ce.parquet e E:/campeonato-nasa/dados/srtm/aspecto_ceara_90m.tif → P2, pós-entrega: Depois: sugerir a ladeira padrão (fração 8–20% do município) e orientar as faixas pelo aspecto no CE.

## Proposta detalhada
## 1. Onde a tela entra no fluxo e as perguntas dela
Fluxo: escolher o lugar (globo/mapa do João) → opções e configurações (cardápio e plano do José) → **[3 perguntas do desenho]** → "como plantar e distribuir" (esta tela) → retorno financeiro.
As perguntas ficam logo acima do desenho, porque cada resposta redesenha na hora. Tudo vem preenchido com o exemplo rotulado "Dona Francisca (fictícia): 3 ha, 1 ha de baixio".
1. **Tamanho do roçado:** ha ou tarefas. A tarefa cearense de 3.025 m² é suposição a conferir. Use 0,5–5 ha, porque o Garantia-Safra limita a área plantada a 5 ha (proposta:44).
2. **Tem baixio, a parte que fica úmida depois da chuva?** Não / pouco (1/5) / um terço / metade / "não sei". "Não sei" desenha o baixio de 1/3 tracejado, com "confirme". Pergunta extra: **de que lado ele fica** (em cima, embaixo, esquerda, direita; o padrão é embaixo).
3. **O terreno tem ladeira?** Plano / pouca / muita (10–25%). Com ladeira, as divisas das faixas viram aleias de palma em nível (Pinheiro & Nair 2018, C, proposta:947).
Mais adiante (já no motor): solo (textura/AD) e "tem mandioca no chão hoje?".

## 2. Algoritmo (entradas → layout), tudo no navegador
Entradas: `r.plano.faixas` (motor.py:690-704), `r.agenda.linhas[].barras` (motor.py:763-804), respostas {area_ha, baixio_frac, lado_baixio, ladeira}.
```
lado = sqrt(area_ha*1e4)                     # quadrado (suposição até haver polígono)
b = area_ha*baixio_frac                      # ha do baixio (resposta)
up = area_ha - b ; parte_ha = up/3           # A=B=C, igual ao 10_familia.py:56
prof_up = up*1e4/lado                        # profundidade da parte alta (m)
nfx = 6 if prof_up/6 >= 10 else 3            # faixas de >= 10 m (suposição de manejo)
# ordem: 6 permutações de [A,B,C]; seq = perm*2 (de cima para baixo); a última faixa encosta no baixio
custo(perm) = Σ_anos Σ_vizinhos [gram(c_i) e gram(c_i+1)]  # gram = {Milho, Sorgo gran., Sorgo forr., Milheto}
perm* = argmin custo (empate: a de menos gramínea encostando no baixio)
faixas = [{id:'B1', parte:'Parte B', y0, y1, ha: parte_ha/2}, ...]
bordas = linha no perímetro (não tira área, como no estudo financeiro); a gliricídia fica do lado de fora,
         longe do grão (Martins 2015, proposta:947); a palma fica do lado de dentro.
ladeira = 'muita' -> as divisas das faixas viram linha de palma (aleia em nível)
baixio  = linhas alternadas cereal/caupi 1:1 (suposição); a paridade troca a cada ano (motor.py:688)
```
Conectividade por ano (P1): uma grade de células de 5 m recebe a cultura de cada célula; depois `label` com vizinhança 4 (union-find de ~30 linhas em JS) dá, para a gramínea:
- p = fração da área;
- n_blocos;
- S = maior bloco / total;
- `desce` = o maior bloco toca a 1ª linha do alto e a linha do baixio.

Selo: verde se desce = não; âmbar se desce = sim; vermelho se, além disso, p > 0,593 ou houver ponte verde temporal (gramínea na mesma faixa em t e t+1). O 0,593 é só régua de referência, porque vale para mistura ao acaso (Alonso-Tlali 2025); o que manda é o aglomerado calculado.
Resultado medido (layout_sim2.py):
- Quixadá: blocos lado a lado dão p = 0,56 e desce = sim (2027, 2028); faixas B C A B C A dão 3 blocos e desce = não.
- Arapiraca: p = 0,77–0,80, 7 contatos, aviso vermelho.

Estado do mês m (P0): para a faixa da Parte P na estação e, pegar as barras de `agenda.linhas` com parte == P e estacao == e, cujo intervalo contém m. Prioridade: colheita > roca > plantio > risco > preparo. Sem barra: "descanso/palhada". Mandioca e palma seguem com a barra 'roca' até 2028. A linha "caupi no milho em pé" do baixio acende as linhas pares do baixio.

## 3. Contrato de dados (gerado no cliente; o motor não muda no P0)
```json
{"area_ha":3,"lado_m":173,"baixio":{"ha":1,"lado":"baixo","fonte":"resposta"},
 "ordem":["Parte B","Parte C","Parte A"],"por_que_ordem":"a Parte A nunca tem gramínea aqui: encosta no baixio",
 "faixas":[{"id":"B1","parte":"Parte B","y0_m":0,"y1_m":19,"ha":0.33}],
 "anos":{"2027":{"cel":{"B1":{"cultura":"Feijão-caupi","tipo":"leguminosa"}},
                 "conect":{"graminea":{"p":0.57,"blocos":3,"S":0.6,"desce":false}}}},
 "rotulos":{"linhas":"ilustrativas: espaçamento com o técnico","bordas":"não tiram área (suposição do estudo financeiro)"}}
```

## 4. Esboço (2027, Quixadá, 3 ha, 1 ha de baixio, faixas em nível)
```
 N ↑   gliricídia (fora) · palma (dentro) = borda em nível ··················
 ┌──────────────────────────────────────────────────────────┐
 │ B1  caupi precoce · 0,33 ha  · · · · · · · · · · · · · · · │ ← metade guardada até ~10/mar
 │ C1  sorgo forrageiro · 0,33 ha ||||||||||||||||||||||||||| │
 │ A1  mandioca (maniva 01/02–10/03) · 0,33 ha ♣ ♣ ♣ ♣ ♣ ♣ ♣ │
 │ B2  caupi precoce · · · · · · · · · · · · · · · · · · · · ·│
 │ C2  sorgo forrageiro ||||||||||||||||||||||||||||||||||||| │
 │ A2  mandioca ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ ♣ │ ← sem gramínea encostando no baixio
 │≈≈ BAIXIO 1 ha: milho ║ caupi ║ milho ║ caupi (linhas alternadas) ≈│
 └──────────────────────────────────────────────────────────┘ água corre ↓
 [2027] 2028 2029     mês: nov ─ dez ─ jan ─ FEV ●─ mar ─ abr ─ … ─ dez/27
 Selo: gramínea em 57% do roçado, em 3 blocos separados; não desce até o baixio.
```
SVG mínimo, com viewBox no tamanho do lado em metros (escala real):
```html
<svg viewBox="0 0 173 173" role="img" aria-label="Roçado 2027 visto de cima">
 <rect width="173" height="173" fill="none" stroke="var(--perene)" stroke-width="4"/>
 <g id="faixas"><rect y="0" width="173" height="19.2" class="f-leguminosa" data-id="B1"/> …</g>
 <rect y="115.3" width="173" height="57.7" class="f-cereal"/>
 <g id="linhas"><!-- uma <line> a cada ~2 m de desenho, cor do tipo; caupi tracejado até o revezamento --></g>
 <text x="4" y="12">B · caupi · 0,33 ha</text>
</svg>
```
Animação:
- Ano: um clique troca a classe de cor de cada faixa, com `transition: fill .6s`. A letra fica, e uma seta pequena mostra "veio de C".
- Mês: um slider reescreve a classe de estado de cada faixa. O desenho das linhas muda assim: solo nu no preparo, pontos pequenos no plantio, traço cheio crescendo, ícone de colheita.
- "Play": avança 1 mês a cada 0,8 s até dez/2027.

## 5. O que é dado, suposição ou projeção
- **Dado/fonte:**
  - culturas por parte e ano (plano, proposta 6.4);
  - janelas e colheitas (ZARC 2026/27 + CICLO, com os ciclos sem fonte marcados como suposição no motor);
  - gliricídia longe do grão (Martins 2015);
  - aleias em 10–25% de declive (Pinheiro & Nair 2018);
  - χc 0,593 e as configurações faixas/xadrez (Alonso-Tlali 2025);
  - definições p, S e atravessa (MANIFESTO do José).
- **Suposição:**
  - roçado quadrado, A = B = C e bordas fora da área (como no estudo financeiro);
  - largura mínima de 10 m por faixa;
  - linhas 1:1 no baixio;
  - células de 5 m;
  - espaçamento das linhas (ilustrativo);
  - "não sei" = baixio de 1/3.
- **Projeção:** o desenho de 2028–2029 (datas de 2028 repetem o ZARC 2026/27). Não há previsão de praga nem de perda: o selo é geometria, não risco medido.

## Riscos
- Mostrar os números do motor do PercolaCampo (ex.: 'proteção de 61% para 94%') como se fossem medidos: não estão nos PDFs, e um avaliador que abrir o artigo acha a diferença. Na tela vai só o aglomerado calculado e o χc com fonte.
- Dar a entender que as faixas seguram a lagarta-do-cartucho: a própria proposta diz que a mariposa voa de 100 a 250 km. A frase de limite precisa ficar colada no selo.
- O desenho quadrado com faixas iguais pode ser lido como receita: rotular 'o tamanho de cada faixa e o solo do baixio se confirmam com o técnico' (proposta:939 e 1650).
- As linhas de plantio sem fonte de espaçamento podem ser tomadas como densidade recomendada: manter o rótulo 'ilustrativas'.
- A agenda só vai até dez/2027: o mês a mês de 2028–2029 não existe. Não inventar datas para 2029.
- Mudar o plano() por causa do achado de Arapiraca na véspera mexe no estudo financeiro e nos números canônicos: é melhor um aviso na tela do que mudar o motor sem o José decidir.
- Sobrecarga visual no celular: o SVG precisa caber em 360 px, com os rótulos das faixas abreviados (B · caupi) e o detalhe num toque.

## Perguntas abertas
- O José aceita que as bordas fiquem fora da área cultivada (como no 10_familia.py) ou quer que tirem área? Isso muda a soma do financeiro.
- Para lugares sem mandioca apta (Arapiraca), o plano deve trocar um dos sorgos forrageiros por pousio pastejado ou leguminosa? Hoje dá 2/3 de gramínea todo ano.
- O Vicente tem o PDF do González-Martínez et al. 2026 (Chaos 36:093144) e a fonte dos coeficientes k_faixas/k_xadrez e d0? Sem isso, eles ficam fora da tela.
- As faixas em nível ficam na horizontal do desenho (baixio embaixo) ou o agricultor desenha o polígono no mapa do João já nesta versão?
- A unidade preferida na pergunta de área é ha, tarefa ou as duas? E qual tamanho de tarefa vale em cada estado do NE?