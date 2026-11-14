# PercolaCampo do Vicente (vicente)

## Resumo
O PercolaCampo do Vicente (pesquisa_vicente/, protótipos v2 e v3) é uma simulação visual de um sítio fictício. O motor é de 5 etapas e calcula um R_eff e um "% de plantas protegidas", mas quase todas as constantes que decidem o resultado não têm fonte (d0, T0, 2,35, 108−34·R, fator da semente crioula, degrau de 40% de mata). Nenhum dado da NASA é lido, apesar do rótulo "Dados NASA". Vários números do dossiê não batem com os PDFs da própria pasta:
- o With 2002 dá um limiar abaixo de 20% de habitat, não 40%;
- os ganhos de 18–40% e os χc de 0,78–0,92 não aparecem no artigo da Entropy;
- o Poggi 2013 mede espaçamento em mm, em bandeja de muda, e virou d0 em cm no campo;
- o q-exponencial do Ramírez 2020 ajusta o limiar contra o inóculo, não a eficiência de barreira.

Por isso o R_eff e o "% protegido" têm grau D e não devem ir para a tela, nem para o agricultor nem para o júri. Duas coisas se aproveitam com força real. A primeira é a ciência de base: os limiares de percolação (0,593 com 4 vizinhos, 0,407 com 8, 0,5 por ligação) e duas fórmulas publicadas (Entropy 2025, Eq. 11; Ramírez 2020, barreiras mínimas). A segunda é a ideia, que o artigo sustenta e minha simulação confirma: o mesmo hospedeiro em um bloco contínuo fica 100% ligado, e em faixas intercaladas um foco fica preso em 1/k da cultura, desde que o vão de não-hospedeiro seja maior que o alcance da praga. Isso encaixa direto no plano do José: as Partes A/B/C deixam de ser três blocos e viram faixas intercaladas (A-B-C-A-B-C), o baixio fica com o cereal (e a mandioca fica fora dele, por causa da podridão de raiz), e as bordas de palma + gliricídia ficam no lado de onde vem o vento. A rotação no tempo (José, ponte verde) e a distribuição no espaço (Vicente) cabem num único croqui que troca as culturas de faixa a cada ano. Ser honesto aqui fortalece a proposta: faixas protegem contra doença de solo e praga que anda, mas não contra lagarta-do-cartucho, bicudo ou mosca-branca, que voam quilômetros (a seção 16 do José já mostra isso). Cabe até amanhã: portar uma função determinística desenho_rocado (~60 linhas) e uma tela SVG com controle deslizante de faixas e botão de ano, em cerca de 6–8 h.

## Recomendações
- **P0** (0.5 h) Não mostrar R_eff, '% de plantas protegidas', 'proteção de X% para Y%', '8,2% de economia de área', '40% de mata para joaninhas', o d0 por cultura nem o fator da semente crioula. Tirar o rótulo 'Dados NASA' do PercolaCampo. — São constantes sem fonte ou números que contradizem os próprios PDFs. Um avaliador que abrir o With 2002 ou o Entropy 2025 derruba a credibilidade de toda a QUADRA.
- **P0** (2 h) Portar para protótipo/motor.py a função determinística desenho_rocado(plano, area_ha, f_baixio, vento_de, tracao, k) e expô-la em /api/local como plano.desenho: faixas intercaladas A-B-C×k por ano, largura da faixa, maior bloco contínuo, vão entre faixas da mesma família, fração atingida por um foco por grupo de praga, e avisos de adjacência (gramínea com gramínea, mandioca no baixio). — É a parte do Vicente que tem evidência (percolação: bloco contra faixa) e responde a 'como deve ser a plantação e a distribuição' usando o plano que já existe, sem inventar números.
- **P0** (3 h) Tela 'Como plantar o roçado': croqui SVG visto de cima, com bordas no lado do vento, baixio no lado baixo e faixas coloridas por família. Botões 2027/2028/2029 mostram as culturas trocando de faixa. Controle deslizante 'faixas por parte' (1 = blocos de hoje, até 4), três cartões por tipo de praga e selos medido/suposição em cada número. — Junta rotação no tempo (José) e distribuição no espaço (Vicente) numa única imagem. É o 'bem visual e fácil de entender' que o José pediu.
- **P1** (1 h) Pôr as perguntas do croqui logo antes desta tela, não no começo: tamanho do roçado, se tem baixio e quanto, de que lado vem o vento forte, como trabalha a terra (enxada, animal ou trator, que define a largura mínima da faixa) e de que lado fica a caatinga. — Essas respostas só mudam a geometria. Perguntar no início atrasa a primeira resposta útil, e o agricultor sabe responder isso melhor do que qualquer dado global.
- **P1** (1.5 h) Animação determinística do foco no croqui, adaptando o dia 1–15 do v3: o foco se espalha só dentro das faixas da mesma família e só cruza um vão se o alcance da praga for maior que o vão. Trocar o Math.random por essa regra. — Mostra de forma intuitiva por que a faixa protege e por que não protege contra praga que voa, sem fingir uma previsão.
- **P1** (1 h) Gaveta 'Base científica' com os limiares exatos (0,593, 0,407 e 0,5), a Eq. 11 da Entropy 2025, a fórmula de barreiras mínimas do Ramírez 2020, o resultado da paisagem do José (seção 16) e a bibliografia corrigida (o que cada artigo mede, em que escala e com que organismo), com grau A–D em cada item. — O júri valoriza fundamentação física. Citações corretas, com o domínio de validade explícito, transformam um ponto fraco em ponto forte.
- **P2** (0.5 h) Combinar com o Vicente: verificar o DOI do González-Martínez 2026 (Chaos 36(9) 093144) e pegar o PDF de Kun 2019 e With & Crist 1995. Só citar se o PDF estiver na pasta. — Os α = 4,8/2,6, o q = 1,35 e os 8,2% dependem de um artigo que não está na pasta e que não consegui verificar.
- **P2** (4 h) Depois da entrega: puxar a direção do vento (WD10M) do NASA POWER por região, com cuidado para não pegar 429, e calibrar o alcance por grupo de praga com literatura de campo do NE (Macrophomina e Phytophthora em caupi e mandioca, ácaro-verde da mandioca). — Troca as duas suposições principais do croqui (lado do vento e alcance da praga) por dado medido.

## Achados
- **O que o motor calcula (v3) e com que entradas**: Passo a passo do cálculo:
- Entradas: terreno (3 sítios fictícios com vento, declive e fator de chuva digitados), cultura (4 opções com d0 e T0 fixos), solo (3 opções com 'smapFactor' digitado), espaçamento de 40 a 100 cm, semente crioula ou comercial, padrão (monocultura, faixas ou xadrez), borda contra o vento (liga/desliga), % de mata (de 15 a 80) e pb, a fração de plantas-barreira contada no mapa.
- Fórmulas: T_bond = clamp(T0·exp(−d/d0)·fRain·fWind; 0,06; 0,95), com fWind = 1+(v−14)·0,015+declive·0,008.
- Limiar: χc = min(0,98; 0,5927 + k·pb), com k = 0 (monocultura), 0,56 (faixas) ou 0,72 (xadrez).
- Barreiras: E_q = [1+0,35·α·fb]^(−2,857), com α = 4,8 ou 2,6.
- p_site = max(0,2; (1−pb)·semente·aliados) e T_eff = T_bond·(0,45+0,55·E_q)·2,35.
- R_eff = p_site·T_eff/χc, e protegido = clamp(108−34·R_eff; 28; 98).
- Fase da paisagem (1 a 5) pela % de mata.
- O surto de 15 dias é sorteado com Math.random, num alcance em pixels.

O v2 é igual, com mais o padrão 'aleatório' (k = 0,42) e uma 'economia de área' fixa de 8,2%. _[colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_motor_calibrado_por_metan_lise_cient_fica.html:915-985 (motor), :813-888 (terrenos, culturas e solos digitados), :1079-1123 (surto com Math.random); v2 .html:896-897 e :914]_
- **Nenhum dado da NASA entra no motor**: Não há fetch nem leitura de arquivo. Tudo o que é 'SMAP', 'vento NASA POWER' ou 'declive SRTM' é constante digitada para sítios inventados (Sítio Boa Esperança, Chácara Águas Claras, Sítio Serra Verde). O rótulo 'Dados NASA' aparece só no cabeçalho e no comentário do código. _[grep 'NASA|SMAP|POWER|fetch(' no v3: só .html:139 (texto do cabeçalho), :670 (fórmula exibida) e :812 (comentário)]_
- **Constantes sem fonte dominam o resultado (grau D)**: Constantes que não aparecem em nenhum dos 6 PDFs:
- d0 (32/44/52/65 cm) e T0 (0,76–0,92);
- 2,35, 0,45/0,55, e 108 e 34 no '% protegido';
- semente crioula 0,76 contra comercial 1,05;
- degrau de aliados 0,85/1,08 em 40%;
- α = 4,8/2,6 e o mapeamento de fb.

Portei o motor para Python e varri as 18.144 combinações de entrada do app:
- 81% saem 'Protegida' e 36% batem no teto de 98%;
- até monocultura, semente comercial, sem borda e com 30% de mata dá 71% de 'plantas protegidas';
- só trocar a semente muda o R_eff em ×1,38, e mata de 45% para 39% muda em ×1,27, ambos sem fonte.

No estado inicial do app, o botão 'Aplicar melhor desenho' não muda nenhuma entrada efetiva (faixas e borda já ligadas, 70 cm ≥ d0+18, mata de 45 para 50 não cruza o degrau de 40). Ele mostra 'de X% para X%'. _[Porte e varredura: C:/Users/NETINH~1/AppData/Local/Temp/claude/88b277d27b184113/73cd62bd-b6e9-4872-9e4a-a06e5ca404a0/scratchpad/analise10/vicente/motor_vicente.py (saída: varredura n=18144, Protegida 0,81, teto 98 = 0,36, monocultura 71%); v3 .html:1685-1700]_
- **Números do dossiê que não batem com os PDFs da pasta**: - With 2002: o limiar de estrutura da paisagem é abaixo de 20% de habitat (lacunaridade), em parcelas experimentais de trevo com pulgão e joaninha em Ohio. O dossiê diz cerca de 40%.
- Entropy 2025 (Alonso-Tlali): o texto não tem nenhum número em %. Os χc 'aleatório 0,78–0,85', 'faixas 0,88–0,92', 'redução de 65%' e 'ganho de 18–32%' ou '25–40%' não estão no artigo. O resultado real são curvas críticas no plano (σA, σB) e a Eq. 11 para mistura ao acaso. A conclusão é que o xadrez (diagonais) tem a maior região sem percolação.
- Poggi 2013: espaçamentos de 22 a 54 mm entre mudas de couve-flor em bandeja, com Rhizoctonia. A 26 mm, as manchas tiveram de 1 a 22 plantas (média 10,5). No motor isso virou d0 = 32–65 cm para milho, feijão e mandioca no campo, um salto de escala de cerca de 10× sem base.
- Cunniffe 2014: a dispersão média de 2a ≈ 5 m está correta, mas para uma doença de citros na Bahia (BBSC). As 200–300 plantas/ha são densidades ótimas de produção, não um limiar que se 'cruza'.
- Ramírez 2020: o q-exponencial (Tsallis) ajusta σc_plant contra o inóculo I (a = 0,91, n = 2,0 na grade quadrada, ou seja q ≈ 1,5), não a eficiência de barreira com q = 1,35. As 'barreiras' do artigo são membranas físicas no solo entre plantas, em estufa.
- González-Martínez 2026 (Chaos), Kun 2019 e With & Crist 1995 não estão na pasta. Os α = 4,8/2,6 e os 8,2% dependem só do primeiro e não pude verificar.

Não é uma metanálise: não há agregação estatística de efeitos. _[Texto extraído com pdftotext em scratchpad/analise10/vicente/*.txt. with2002.txt L23 ('threshold in lacunarity below 20% habitat'); grep '%' em entropy-27-00386.txt sem resultado; PHYTO-02-13-0033-R.txt L133-134 e L295-300; file.txt L322 (2a ≈ 5 m) e L405-412 (200/300 plantas/ha como ótimos); 10.1103@PhysRevE.101.032301.txt L168 e L318. Dossiê: dossi_completo...md:28-31, :37-38, :97, :101-103]_
- **O que tem evidência sólida e pode ser portado**: - Grau A (matemática ou simulação exata): o limiar de sítio na grade quadrada é pc = 0,5927 com 4 vizinhos e 0,4073 com 8; o de ligação é 0,5. Num bloco contínuo, o hospedeiro é 100% conectado por definição.
- Grau B (modelo publicado, válido no seu domínio): a Eq. 11 da Entropy 2025, Mix·σA + (1−Mix)·σB < (pc−I)/(1−I), para mistura ao acaso; e o Ramírez 2020, barreiras mínimas = 1 − B/(ps+A), com A = (pcb−pcs)/(1−pcb) e B = pcb(1−pcs)/(1−pcb). Valores: ps = 0,7 exige 21% das ligações com barreira; 0,9 exige 43%; 1,0 exige 50%.
- Grau C: a transferência para mandioca, caupi e milho no semiárido, que é direção e não número.

Minha simulação de um roçado de 120×120 covas com 1/3 de hospedeiro:
- em bloco, S = 1,00 (um foco alcança tudo) para qualquer alcance;
- em faixas de 4 linhas de hospedeiro e 8 de não-hospedeiro, S = 0,10 enquanto o alcance é de até 6 covas, e S = 1,00 com alcance de 10 covas, maior que o vão de 8;
- ao acaso com 33%, fica isolado com alcance de até 1,5 cova e atravessa a partir de 3. _[motor_vicente.py (mesma pasta do scratchpad): funções sigma_b_critico_mistura, barreiras_minimas_solo e atravessa; saída 'faixas de 4 linhas alternadas ... r=6: S=0.10 | r=10: S=1.00']_
- **O José já tem percolação, na escala da paisagem**: - A seção 16 do José trabalha com janelas de 40 km a 30 m (CDL dos EUA e Esri LULC do CE). Resultados:
  - no Texas, o algodão contínuo deixa 65% da ponte verde num único aglomerado, e rotacionar 30% dos talhões derruba isso para cerca de 22%;
  - com raio de 5 km, tudo fica conectado, inclusive no CE;
  - no Sertão Central, só 28–64% da lavoura volta ao mesmo pixel.
- O v4_entomologo mostra que 69,7% dos município-anos do CE têm fração de gramínea acima de 0,407.

O Vicente trabalha na escala da cova e da faixa dentro do roçado. As duas escalas se completam, não se repetem. 'Percolação' hídrica (termo D do FAO-56) é outra coisa e não deve ser misturada na tela. _[notebooks/secoes/16_percolacao.py:170-190; E:/campeonato-nasa/dados/percolacao/MANIFESTO.json; conselho/analises/v4_entomologo_bicudo_conectividade.saida.txt (bloco B)]_
- **Onde encaixa no plano do José**: - O plano tem Parte A/B/C 'de tamanho parecido', que trocam de cultura a cada ano: mandioca → leguminosa → forragem/cereal. Tem também o baixio com cereal e leguminosa em revezamento, e as bordas com palma + gliricídia em nível. Mas não diz a geometria.
- A contribuição do Vicente é a geometria: as Partes entram como k faixas intercaladas (A-B-C repetido k vezes), em nível ou atravessadas ao vento. Assim, cada faixa de uma família tem dos dois lados faixas de outras famílias (Euphorbiaceae, Fabaceae, Poaceae).
- Com isso, o maior pedaço contínuo da mesma cultura cai de U/3 para U/(3k), e um foco de praga de solo fica em no máximo 1/k da cultura.
- Conflitos que a função precisa avisar:
  - sorgo forrageiro (Parte C) encostado no baixio de milho, porque são duas gramíneas e a lagarta-do-cartucho passa; a nota em motor.py:713 já reconhece que sorgo não quebra o ciclo;
  - mandioca não vai no baixio, pela podridão de raiz em solo encharcado. Isso é recomendação agronômica comum e eu não verifiquei no repositório. _[protótipo/motor.py:646-736 (função plano; faixas, baixio e bordas em :690-704; nota do cartucho em :713); /api/local de Quixadá: plano.faixas[0] = Parte A, Mandioca, 'maniva de 01/02 a 10/03 (ZARC, Port. 11/2020)']_
- **O que já existe para as perguntas do croqui**: - A /api/local não traz vento, e os derivados têm WS2M (velocidade), mas não direção. Então 'de que lado vem o vento forte?' deve ser pergunta ao agricultor, com padrão 'leste/sudeste (alísios)' marcado como suposição.
- O Censo 2017 (ibge_ne_censo2017_praticas_mun) dá 22,6 ha por estabelecimento em Quixadá (mediana do NE 22,7 ha). Mas estabelecimento não é roçado: o tamanho do roçado tem que ser pergunta.
- O Censo também dá a linha de base da prática: rotação em 6,1% dos estabelecimentos de Quixadá (mediana do NE 6,7%) e plantio em nível em 2,2% (mediana 0,4%). É um bom número de contexto para o júri. _[curl /api/local?lat=-4.97&lon=-39.01 (chaves: local, terra, fontes, clima, analogos, confianca, cardapio, este_ano, plano, agenda, evidencia; sem vento); power_ne_mensal.parquet: variáveis sem WD; consulta ao parquet do Censo 2017]_
- **interface-inicial-vicente (Roça Certa CE) repete o que já existe**: É uma página única para os 184 municípios do CE, com 1,7 MB de JSON embutido: chuva diária IMERG por município de 1998 a set/2026, ONI, PAM e SRTM. Os cartões são Inverno 2027, Quando plantar, Seu ano na roça, O que aguenta seca, Entressafra e Como foi o inverno. Isso se sobrepõe ao protótipo do José (1.794 municípios) e ao painel do JP. A regra de 'Quando plantar' vem do conselho/analises/agronomo_regras_semeadura, que é trabalho compartilhado do commit 48a3608 do José, e o protótipo do José já usa 'lê a chuva desde 1/fev'. Vale aproveitar o padrão 'Como eu funciono' e a malha do IBGE do CE, mas não como tela própria. _[colegas/vicente/interface-inicial-vicente/README.md; dados/dados_pagina.json (chaves: anos, nomes, relevo, rain, oni_jas, oni_ultimo, culturas, anual, geo; 184 municípios); conselho/analises/saidas/agronomo_regras_semeadura.txt; protótipo/motor.py:831]_

## Reaproveitar
- colegas/vicente/pesquisa_vicente/prototipo/percolacampo_v3_motor_calibrado_por_metan_lise_cient_fica.html:1194-1322 (renderFarmSvg) → site-versao-final/ tela 'Como plantar o roçado' (componente croqui): Base do desenho SVG do croqui: trocar o polígono fictício e as covas por um retângulo com faixas coloridas por família, manter as setas de vento e o anel de mata, que vira 'lado da caatinga'.
- v3 .html:1079-1180 (startOutbreakAt, setTimelineDay e reprodução do dia 1 ao 15) → site-versao-final/ animação 'ver um foco se espalhar': Manter a linha do tempo e o controle deslizante dos dias, e trocar o Math.random pela regra determinística 'espalha na família e só cruza o vão se o alcance for maior que o vão'.
- v3 .html:1539 e seguintes (setWizardStep, assistente de 4 passos com cartões grandes) e o fluxo do dossiê :125 → site-versao-final/ passo de perguntas antes do croqui: Padrão visual das perguntas (cartões tocáveis com ícone). Trocar o conteúdo por tamanho do roçado, baixio, vento, tipo de trabalho da terra e lado da caatinga.
- v2 e v3, aba 'Base Científica (Metanálise)' → site-versao-final/ gaveta da tela do croqui: Reaproveitar o layout da aba como gaveta 'Base científica', com o conteúdo corrigido: limiares, Eq. 11 da Entropy, fórmula de barreiras do Ramírez 2020, o que cada artigo mede e grau A–D. Renomear para não dizer 'metanálise'.
- colegas/vicente/pesquisa_vicente/artigos/*.pdf (6 PDFs) e dossi_completo...md:133-143 → site-versao-final/referencias/: Copiar os PDFs para a pasta de referências da versão final e usar a bibliografia com as correções (With 2002 = 20%; Poggi em mm em bandeja; Cunniffe 2a ≈ 5 m para BBSC; Ramírez 2020 com Tsallis contra o inóculo).
- notebooks/secoes/16_percolacao.py:170-190 e E:/campeonato-nasa/dados/percolacao/cenarios.csv → site-versao-final/ cartão lateral da tela do croqui: Cartão 'na paisagem' ao lado do croqui: curva do aglomerado gigante da ponte verde contra a fração de talhões rotacionados (Texas, de 65% para cerca de 22% com 30%).
- protótipo/motor.py:646-736 (plano) e :713 (nota do cartucho) → protótipo/motor.py (nova função logo depois de plano) e /api/local → plano.desenho: desenho_rocado consome plano['faixas'] sem mudar a lógica de rotação. As notas já existentes viram os avisos de adjacência.
- dados_resumo/derivados/ibge_ne_censo2017_praticas_mun.parquet (pct_rotacao, pct_plantio_nivel) → site-versao-final/ rodapé do croqui e slide do júri: Número de contexto no croqui e na apresentação: 'em Quixadá, 6% dos estabelecimentos fazem rotação e 2% plantam em nível'. É a linha de base medida.
- colegas/vicente/interface-inicial-vicente/fonte/pagina.html (página 'Como eu funciono') → site-versao-final/ página de método: Só o padrão de explicar cada número com fonte e limite. Os cartões (Inverno 2027, Quando plantar etc.) já estão cobertos pelo protótipo do José e pelo painel do JP.

## Proposta detalhada
FUNÇÃO A PORTAR: desenho_rocado (Python, em protótipo/motor.py, logo depois de plano(); determinística, sem sorteio)

ENTRADAS
- plano: o dict que plano() já devolve (faixas Parte A/B/C, Baixio e Bordas por ano 2027–2029). É medido no sentido de vir do ZARC/GAEZ e do catálogo.
- area_ha: pergunta ao agricultor. Sem resposta, o croqui sai em % e sem hectares. Não usar os 22,6 ha por estabelecimento do Censo como se fossem o roçado.
- f_baixio: pergunta ("tem baixio? pouco/médio/muito" = 0,10/0,20/0,30). Esses valores são suposição. Com "não", o baixio é 0.
- vento_de: pergunta (8 direções). O padrão é "L/SE (alísios)", marcado como suposição.
- tracao: enxada/animal/trator, que dá a largura mínima da faixa w_min = 3/6/12 m (suposição, ajustável).
- k: faixas por Parte, escolhido no controle deslizante (1 a 4). O padrão é o maior k com w ≥ w_min.

CONSTANTES
- FAMILIA = {Mandioca: Euphorbiaceae; Feijão-caupi, Feijão comum, Amendoim, Gliricídia: Fabaceae; Milho, Sorgo, Milheto: Poaceae; Palma: Cactaceae; Pousio: nenhuma}.
- ALCANCE por grupo de praga, como ordem de grandeza (suposição, com fonte só para a direção):
  - solo/raiz (fungos de solo, Phytophthora, nematoides): ~5 m. Exemplo medido: BBSC em citros na Bahia, 2a ≈ 5 m (Cunniffe 2014). Direção: Poggi 2013 e Ramírez 2020.
  - anda ou vento curto (ácaros, cochonilha): ~30 m (suposição).
  - voa longe (lagarta-do-cartucho, bicudo, mosca-branca): mais de 1 km. Vem da seção 16 do José: com 5 km, tudo fica conectado.

CÁLCULO
1. Área útil: U = A·(1 − f_baixio) − área das bordas (1 linha de palma + gliricídia de ~3 m no perímetro do lado do vento; suposição).
2. Lado: L = √(U·10⁴) m. O roçado é aproximado por um quadrado, com faixas atravessadas ao vento ou em nível.
3. Largura da faixa: w = L/(3k). Se w < w_min, k = max(1, ⌊L/(3·w_min)⌋).
4. Ordem das faixas: [A,B,C]×k. Para cada ano t e cada faixa i, cultura = plano[Parte][t] e fam = FAMILIA[cultura].
5. Para cada família F no ano t:
   - vao_F = a menor soma contínua de larguras de faixas vizinhas de outra família entre duas faixas de F. É 2w quando A, B e C são de famílias diferentes e 0 se duas Partes vizinhas são da mesma família.
   - O baixio conta como uma faixa extra no lado baixo.
6. Maior bloco contínuo da mesma cultura: U/(3k), ou a soma das faixas adjacentes da mesma família.
7. Fração da cultura F que um foco alcança, para cada grupo g: S_F,g = 1/k_F se vao_F > ALCANCE[g], senão 1. Aqui k_F é o número de faixas de F. Com k = 1 (blocos), S = 1 sempre.
8. Avisos:
   - (a) vao_F = 0 (duas Partes vizinhas da mesma família);
   - (b) baixio de Poaceae encostado em faixa de Poaceae (sorgo da Parte C com milho do baixio): "ponha caupi ou mandioca entre os dois";
   - (c) mandioca na faixa encostada no baixio: "a mandioca vai no alto; baixio encharca e dá podridão de raiz";
   - (d) grupo 'voa longe' sempre com S = 1: "faixa não segura essa praga; o que segura é a rotação de família no tempo e o calendário comum da comunidade (vazio do bicudo)".
9. Bordas: palma + gliricídia no lado vento_de, em nível (já está no plano do José). Tem efeito de quebra-vento. Não prometer contenção de praga.

SAÍDA (JSON em plano.desenho)
{ "k": 3, "largura_faixa_m": 19, "ordem": ["A","B","C","A","B","C","A","B","C"],
  "anos": { "2027": [{"faixa":1,"parte":"A","cultura":"Mandioca","familia":"Euphorbiaceae"}, ...] },
  "metricas": { "2027": { "Feijão-caupi": {"maior_bloco_ha":0.37, "vao_m":38, "foco": {"solo":"1/3","anda":"1/3","voa":"tudo"}} } },
  "avisos": ["..."], "bordas": {"lado":"L","texto":"palma + gliricídia em nível, do lado de onde vem o vento"},
  "selos": {"culturas":"medido (ZARC/GAEZ)", "faixas":"proposta", "alcance":"suposição", "limiar":"teoria (grau A)"} }

FÓRMULAS DA GAVETA 'BASE CIENTÍFICA' (sem mudar a tela principal)
- limiar_mistura(σA, mix, I=0): σB_c = [(pc−I)/(1−I) − mix·σA]/(1−mix), com pc = 0,5927 (Entropy 2025, Eq. 11). Num consórcio ao acaso de hospedeiro (σ = 1) com não-hospedeiro (σ = 0), o hospedeiro precisa ficar abaixo de 59% das covas (4 vizinhos) ou de 41% (8 vizinhos).
- barreiras_min(ps) = 1 − 0,4073/(ps − 0,1854) para ps > 0,5927 (Ramírez 2020, grade quadrada; caso solo).

WIREFRAME DA TELA (passo 4 de 5: depois de "Opções e plano" e das perguntas, antes de "Retorno financeiro")

+--------------------------------------------------------------+
| COMO PLANTAR O ROÇADO - Quixadá (CE)        [2027][2028][2029]|
+--------------------------------------------------------------+
|  vento forte vem daqui  >>>                                  |
|  ######## bordas: palma + gliricídia (em nível) ########     |
|  |MAN|CAU|SOR|MAN|CAU|SOR|MAN|CAU|SOR|   <- faixas de ~19 m  |
|  |   |   |   |   |   |   |   |   |   |                       |
|  ~~~~~~~~~~~ baixio: milho + caupi em revezamento ~~~~~~~~~~ |
|  [!] sorgo encostado no milho do baixio: ponha caupi entre   |
+--------------------------------------------------------------+
| Faixas por parte:  1 --o-- 2 --- 3 --- 4   (1 = como é hoje) |
| Maior pedaço da mesma cultura: 0,37 ha (era 1,1 ha)          |
+--------------------------------------------------------------+
| [Doença de solo]   foco fica em 1 faixa: perde no máx. 1/3   |
| [Ácaro/cochonilha] foco fica em 1 faixa, se o vão > 30 m      |
| [Voa longe]        faixa não segura: vale a troca de cultura  |
|                    no ano e o calendário da comunidade        |
+--------------------------------------------------------------+
| [> ver um foco se espalhar]          [Base científica  v]    |
| selos: ZARC/GAEZ = medido | faixas = proposta | alcance = suposição |
+--------------------------------------------------------------+

- Os botões de ano trocam as cores das faixas (A→B→C) e o croqui continua no lugar: é a rotação acontecendo.
- O botão "ver um foco" anima as faixas da mesma família ficando vermelhas, dia após dia, parando no vão.
- Para o júri, com a frase "percolação em duas escalas", um cartão lateral mostra a paisagem do José: Texas, 65% → 22% com 30% dos talhões rotacionados (CDL).

O QUE MOSTRAR E O QUE NÃO MOSTRAR
- Para o agricultor, é defensável: faixa intercalada em vez de bloco; mandioca no alto e cereal no baixio; bordas no lado do vento; "faixa não segura praga que voa".
- Para o júri, é defensável: os limiares exatos, as duas fórmulas publicadas com seu domínio (grade, vizinhos próximos, pimenta com Phytophthora), o resultado da paisagem do José e o grau C da transferência.
- Não mostrar: R_eff, % protegido, ganho de produção por desenho, d0 por cultura, regra dos 40% de mata e simulação sorteada apresentada como previsão.

## Riscos
- Credibilidade diante do júri: apresentar o PercolaCampo como 'motor calibrado por metanálise com dados NASA' é fácil de derrubar. Não há dado NASA, as constantes não têm fonte e a regra dos 40% contradiz o With 2002 da própria pasta. Pode contaminar a confiança no resto da QUADRA.
- Faixas intercaladas têm custo agronômico que não foi medido: competição e sombra (sorgo sobre caupi), manejo mais trabalhoso e incompatibilidade com tração. O próprio motor do José diz que o ganho da rotação contra o consórcio milho + feijão de hoje não foi medido. O croqui precisa dizer 'proposta', não 'comprovado'.
- As pragas que mais pesam no sequeiro do NE (lagarta-do-cartucho, bicudo, mosca-branca, pulgão do caupi) voam: o desenho no roçado quase não as contém. Se a tela vender faixa como proteção geral, ela engana o agricultor.
- Os alcances por grupo de praga (5 m, 30 m, mais de 1 km) e as larguras mínimas por tipo de trabalho da terra são suposições de ordem de grandeza. Os resultados do croqui dependem deles, e precisam do selo 'suposição' e de um controle visível.
- Os parâmetros α = 4,8/2,6, q = 1,35 e os 8,2% vêm de um artigo (González-Martínez 2026, Chaos) que não está na pasta e não pude verificar. Citá-lo sem o PDF é um risco.
- Questão de equipe: cortar o R_eff e o '% protegido' pode soar como descartar o trabalho do Vicente. Convém apresentar como 'promovido para o croqui, com a parte que se sustenta', com o nome dele na tela.
- Prazo: P0 (função, endpoint e tela) soma cerca de 5,5 h para uma pessoa com IA. Se apertar, entrega o croqui estático com botões de ano e controle de faixas, e deixa a animação e a gaveta científica para o P1.

## Perguntas abertas
- O Vicente tem o PDF ou o DOI do González-Martínez et al. 2026 (Chaos 36(9) 093144), e de onde saíram d0, T0 e o fator da semente crioula? Se houver uma fonte que eu não vi, o grau de algumas constantes muda.
- O José aceita que as Partes A/B/C sejam desenhadas como faixas intercaladas (A-B-C repetido) em vez de três blocos? A lógica de rotação não muda, só a geometria.
- 'Distribuição' no pedido do José é o croqui dentro do roçado (minha leitura) ou também a distribuição entre roçados vizinhos e na comunidade (calendário comum, vazio do bicudo)? A segunda escala já existe na seção 16 do José.
- Que largura mínima de faixa é aceitável para quem trabalha com enxada, com animal ou com trator? Hoje usei 3, 6 e 12 m como suposição.
- A interface-inicial-vicente (Roça Certa CE) sai da versão final, absorvida pelo protótipo do José e pelo painel do JP, ou o Vicente quer manter algum cartão dela?