# Meta-análises globais que complementam Kluger et al. (2025) — verificação

Conferido em 14/11/2026:
- **Metadados** pelo Crossref e pelo OpenAlex.
- **Números** contra o resumo oficial e o **texto completo** de cada artigo (PDF ou HTML das editoras).
- **Material de apoio:** `scripts/verificar_artigos_texto.py`, `scripts/conferir_trechos.py` e
  `pesquisa/verificacao_meta_analises.json`.
- **PDFs:** em `artigos/`, exceto o Beillouin 2021 (ver abaixo).

**Veredito geral:**
- **Os 7 artigos existem**, com título, autores, revista e ano corretos.
- A maioria dos números confere com o texto completo, mas **há erros e omissões que mudam a leitura**, sobretudo no
  Beillouin 2021 e no Mudare 2025 (tabela 2).
- Dois artigos já estavam na nossa revisão: Zhao 2022 e Smith 2023.

## 1. Os artigos

| # | Referência | Revista / DOI | Citações (Crossref) | Acesso / PDF local |
|---|---|---|---|---|
| 1 | Mudare, S. et al. (2025). *Crop rotations synergize yield, nutrition, and revenue: a meta-analysis* | Nature Communications 16:9552 · [10.1038/s41467-025-64567-9](https://doi.org/10.1038/s41467-025-64567-9) | 61 | aberto · baixado |
| 2 | Raveloaritiana, E.; Wanger, T. C. (2026). *Long-term agricultural diversification increases financial profitability, biodiversity, and ecosystem services: a second-order meta-analysis* | Nature Communications 17:1016 · [10.1038/s41467-025-67757-7](https://doi.org/10.1038/s41467-025-67757-7) | 25 | aberto · baixado |
| 3 | Zhao, J. et al. (2022). *Global systematic review with meta-analysis reveals yield advantage of legume-based rotations and its drivers* | Nature Communications 13:4926 · [10.1038/s41467-022-32464-0](https://doi.org/10.1038/s41467-022-32464-0) | 322 | aberto · baixado |
| 4 | Beillouin, D. et al. (2021). *Positive but variable effects of crop diversification on biodiversity and ecosystem services* | Global Change Biology 27:4697–4710 · [10.1111/gcb.15747](https://doi.org/10.1111/gcb.15747) | 600 | cópia aberta no [HAL](https://hal.science/hal-03289109), mas o site bloqueia download automático (anti-robô): baixar pelo navegador |
| 5 | Rasmussen, L. V. et al. (2024). *Joint environmental and social benefits from diversified agriculture* | Science 384:87–93 · [10.1126/science.adj1914](https://doi.org/10.1126/science.adj1914) | 153 | versão aberta (green) · baixado |
| 6a | MacLaren, C. et al. (2022). *Long-term evidence for ecological intensification as a pathway to sustainable agriculture* | Nature Sustainability 5:770–779 · [10.1038/s41893-022-00911-x](https://doi.org/10.1038/s41893-022-00911-x) | 195 | aberto · baixado |
| 6b | Smith, M. E. et al. (2023). *Increasing crop rotational diversity can enhance cereal yields* | Communications Earth & Environment 4:89 · [10.1038/s43247-023-00746-0](https://doi.org/10.1038/s43247-023-00746-0) | 113 | aberto · baixado |

## 2. O que o texto recebido dizia × o que os artigos dizem

| Artigo | Afirmação do texto | Verificação | Situação |
|---|---|---|---|
| Mudare 2025 | 3.663 observações pareadas de 738 experimentos (1980–2024) | Resumo e texto: 3.663 observações, 738 experimentos, 1980–2024 | ✅ confere |
| Mudare 2025 | "aumenta a produtividade total (+23%)" | No **resumo**, 23% é o ganho **só da cultura seguinte** quando a anterior é leguminosa (16% sem leguminosa). Para a **sequência inteira**, o texto dá rendimento total +23% (IC 16–31%) | ⚠️ certo para o total, mas o resumo usa 23% para outra coisa; citar com o IC |
| Mudare 2025 | calorias +24%, proteína +14%, ferro, zinco e magnésio | Energia +24% (IC 16–32%), proteína +14% (IC 8–21%), Fe +27%, Mg +17%, Zn +17% | ✅ confere |
| Mudare 2025 | receita do produtor +20% | +20% (IC 12–29%) | ✅ confere |
| Mudare 2025 | reduz o N entre 41% e 46% | Vale **especificamente** para milho ou trigo em rotação com leguminosa, comparado à monocultura desses cereais, mantendo o rendimento | ⚠️ confere, mas o recorte precisa ser dito |
| Mudare 2025 | (omitido) | **Nem toda rotação ganha:** sorgo → milho-sorgo **perdeu 32% de rendimento e 31% de receita**; milho/sorgo → soja-milho/soja-sorgo também perdeu. Os maiores ganhos (> 80%) estão em regiões de monocultura, **sobretudo África Ocidental e Austral e América do Sul**, e o ganho foi maior na África, onde se usa pouco N | ❗ omissão importante para o Ceará |
| Raveloaritiana 2026 | 120 anos, 184 meta-análises, 6.741 tamanhos de efeito | Confere | ✅ |
| Raveloaritiana 2026 | lucratividade, solo, biodiversidade e carbono +37% a +189% em 20 anos | Confere: lucratividade, biodiversidade, polinização, qualidade do solo e sequestro de carbono | ✅ |
| Raveloaritiana 2026 | (omitido) | **Sem efeito significativo no rendimento, no controle de pragas e na regulação do clima.** É sobre diversificação em geral (consórcio, orgânico, inoculação), não só rotação. Ganha-ganha com rendimento em > 75% de probabilidade nos primeiros ~40–50 anos | ❗ omissão importante |
| Zhao 2022 | 11.768 observações, 462 experimentos, 53 países, 1959–2020 | Confere | ✅ |
| Zhao 2022 | Meta-Forest (random forest em meta-análise) | Confere: pacote R `metaforest`, 21 moderadores | ✅ |
| Zhao 2022 | +20% em média; +32% em baixo uso de insumos | +20% confere. O +32% é para **ambientes de baixa produtividade** (contra 7% nos de alta), e os autores interpretam como baixo insumo (ex.: África, orgânicos) | ✅ com a nuance |
| Zhao 2022 | o ganho cai 7% a cada 50 kg N/ha | Confere; o efeito zera acima de **236 kg N/ha** | ✅ |
| Beillouin 2021 | 99 meta-análises, > 3.700 estudos, 85 a 114 países, 50+ espécies | **95 meta-análises, 5.156 experimentos, > 54.500 observações pareadas, 120 espécies, 85 países** | ❌ números errados no texto |
| Beillouin 2021 | produção +14%, pragas e doenças +63%, água +51%, biodiversidade +24%, solo +11% | Confere, mas são **medianas de todas as estratégias** (agrofloresta, consórcio, cobertura, rotação, mistura de cultivares). O resultado varia muito por estratégia; a agrofloresta é a mais eficaz | ⚠️ não atribuir esses números à rotação em si |
| Rasmussen 2024 | 2.655 propriedades em 11 países | Confere (24 estudos). Os países são **Brasil (5 conjuntos de dados)**, Malawi, Costa Rica, Etiópia, Alemanha, Bolívia, Canadá, Colômbia, EUA, Gana e Indonésia | ✅ e o Brasil está dentro |
| Rasmussen 2024 | (omitido) | Achado central: **combinar várias estratégias** (gado, culturas, solo, plantas não cultivadas, água) dá mais resultados positivos que uma estratégia sozinha | ➕ útil para nós |
| MacLaren 2022 | 25.565 registros, 30 experimentos de longo prazo, Europa e África | Confere | ✅ |
| MacLaren 2022 | lista de países (Quênia, Malawi, Moçambique etc.) | Não confirmei a lista de experimentos no texto baixado; só "Europa e África" | ⚠️ não citar países |
| MacLaren 2022 | diversidade substitui o N | Confere: interação **substitutiva**, com efeito forte em dose baixa de N e quase nulo em dose alta | ✅ |
| Smith 2023 | 32 experimentos de 10 a 63 anos | Confere (Europa e América do Norte) | ✅ |
| Smith 2023 | ganho por grupos funcionais, crescendo com o tempo | Confere: **riqueza funcional** mais que número de espécies; ganho crescente com os anos e maior com pouco N, sobretudo no milho | ✅ |
| Kluger 2025 | "sem dado de fertilizante por talhão, o efeito soja → milho parece menor que nos experimentos" | Confere. Os próprios autores dizem que os efeitos negativos no milho podem ser em parte explicados pelo **menor uso de fertilizante nas rotações**, e que estudo anterior sem dado de fertilizante **subestimou** o efeito soja → milho | ✅ |
| Kluger 2025 | avalia só a cultura seguinte | Confere: o efeito é medido no rendimento da cultura seguinte. Eles comparam o ganho mediano deles (4,5%) com os 16% de uma meta-análise de meta-análises | ✅ |

## 3. Por que estes artigos fortalecem a nossa proposta (Ceará / semiárido)

1. **O ganho da rotação é maior justamente onde se usa pouco insumo.**
   - Zhao: +32% em ambientes de baixa produtividade contra 7% nos de alta.
   - MacLaren e Smith: diversidade substitui o N.
   - Mudare: maior ganho na África e na América do Sul.
   - Isso bate com os nossos dados: GAEZ "insumo baixo" no Ceará e a razão de preço ureia/milho de 4,0 em 2026.
   - **No sertão, a rotação vale mais do que nos celeiros que Kluger estudou.**
2. **Kluger mede pouco ganho (4,5%) num lugar de muito adubo.** As meta-análises explicam o porquê: o N sintético mascara
   o efeito. A nossa ferramenta mostra o caso oposto, de pouco N, onde a literatura prevê ganho grande.
3. **Renda e nutrição, não só rendimento.** Mudare (+20% de receita, +24% de calorias, +14% de proteína) dá base para
   pontuarmos as rotações por renda e nutrição da família, e não só por toneladas.
4. **Cuidados que viram funcionalidade do motor:**
   - **Nem toda sequência ganha.** No Mudare, milho-sorgo no lugar de sorgo perdeu 31% de receita. O motor deve
     penalizar sequências sabidamente ruins.
   - **Os efeitos de longo prazo são lentos.** Em Raveloaritiana não há efeito de rendimento; os benefícios estão em
     solo, carbono e lucratividade ao longo de décadas. A ferramenta deve separar o ganho deste ano do ganho em 10–20 anos.
   - **Combinar estratégias rende mais** (Rasmussen). Rotação + cobertura + manejo de água é melhor que rotação sozinha.
5. **O nosso teste no Ceará** (`analise_diversidade_resiliencia.py`): os municípios mais diversos preservaram +6,6 p.p.
   de rendimento do portfólio na seca de 2012–2016. A rodada 2 do conselho mostrou que isso é sobretudo **composição**
   (mais culturas tolerantes ou irrigadas). **Só com sequeiro, cai para +1,4 p.p., não significativo** (ver
   `artigo_ancora_objetivo.md`). Coerente com a literatura: o que importa é **qual** cultura entra (leguminosa,
   tolerante à seca), não o número de culturas.

## 4. Como citar no pitch sem exagero

- "Meta-análises com milhares de experimentos em dezenas de países mostram que a rotação aumenta rendimento total,
  calorias e renda (Mudare et al. 2025, Nature Communications: +20% de receita). O ganho é maior onde se usa pouco
  fertilizante (Zhao et al. 2022; MacLaren et al. 2022), que é exatamente o caso do semiárido."
- **Não usar:** os números do Beillouin como efeito da rotação (são de todas as diversificações); "−41% a 46% de N" sem
  dizer que vale para milho ou trigo com leguminosa; Raveloaritiana como prova de ganho de rendimento (não há).
