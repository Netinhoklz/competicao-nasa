# Quais culturas os nossos artigos cobrem

Duas leituras, geradas em 14/11/2026:
- **Textos completos dos 67 PDFs** baixados em `artigos/` (`scripts/culturas_nos_artigos.py`):
  - "cita" = a cultura aparece 3 ou mais vezes no texto;
  - "foco" = 15 ou mais vezes, ou seja, a cultura é objeto do estudo.
- **Títulos e resumos de todos os artigos do índice** (`scripts/culturas_nos_resumos.py`): 168 artigos, dos quais 126 têm
  resumo no OpenAlex. Inclui os que não pudemos baixar.

Os nomes foram buscados em inglês e português, com sinônimos (ex.: *cowpea* / *Vigna unguiculata* / caupi /
feijão-de-corda). Contagem automática: serve para ver a cobertura, não substitui a leitura.

| Cultura | PDFs que citam | PDFs com foco | Resumos que citam | Cultura do Ceará? |
|---|---|---|---|---|
| Milho | 35 | 23 | 28 | **sim** |
| Trigo | 27 | 10 | 10 |  |
| Soja | 25 | 12 | 16 |  |
| Arroz | 15 | 7 | 6 |  |
| Pastagem (genérico) | 13 | 3 | 5 |  |
| Leguminosas (genérico) | 11 | 8 | 10 |  |
| Sorgo | 11 | 5 | 3 | **sim** |
| Cevada | 11 | 3 | 0 |  |
| Algodão | 9 | 4 | 5 | **sim** |
| Mandioca | 7 | 5 | 4 | **sim** |
| Alfafa | 7 | 2 | 1 |  |
| Aveia | 7 | 1 | 0 |  |
| Canola/colza | 7 | 2 | 0 |  |
| Plantas de cobertura (genérico) | 6 | 0 | 6 |  |
| Feijão-caupi | 6 | 3 | 4 | **sim** |
| Batata | 6 | 1 | 2 |  |
| Cana-de-açúcar | 5 | 1 | 3 | **sim** |
| Centeio | 5 | 1 | 0 |  |
| Amendoim | 4 | 2 | 3 | **sim** |
| Feijão comum | 4 | 2 | 3 | **sim** |
| Milheto | 4 | 1 | 1 | **sim** |
| Girassol | 4 | 2 | 0 |  |
| Tomate / hortaliças | 4 | 2 | 0 |  |
| Batata-doce | 3 | 2 | 2 |  |
| Trevo | 3 | 1 | 1 |  |
| Cacau | 3 | 1 | 0 |  |
| Café | 3 | 2 | 0 |  |
| Banana | 2 | 2 | 1 | **sim** |
| Palma forrageira | 2 | 1 | 0 | **sim** |
| Caju | 1 | 1 | 1 | **sim** |
| Fava / feijão-fava | 1 | 0 | 1 | **sim** |
| Coco | 1 | 1 | 0 | **sim** |
| Gliricídia | 1 | 0 | 0 | **sim** |
| Guandu | 1 | 1 | 0 | **sim** |
| Ervilha, grão-de-bico, lentilha | 1 cada | 0–1 | 0 |  |
| Melão / frutas irrigadas | 1 | 0 | 0 | **sim** |
| Capins forrageiros (Urochloa, buffel), gergelim, leucena, mamona | 0 | 0 | 0 | **sim** |
| Crotalária, mucuna, ervilhaca | 0 | 0 | 0 |  |

## Leitura

1. **A literatura de rotação é dos celeiros temperados.**
   - Milho, trigo e soja dominam: 35, 27 e 25 PDFs.
   - Kluger 2025, Bowles 2020, Renwick 2021, Smith 2023 e Zhou 2024 são todos sobre milho, soja e trigo.
   - Zhao 2022 e Mudare 2025 cobrem mais culturas, mas com ~90% dos dados em cereais (Zhao: 91% das culturas
     principais após leguminosa são cereais).
2. **As culturas do sertão estão sub-representadas:**
   - **feijão-caupi:** 6 PDFs, 3 com foco;
   - **mandioca:** 7 PDFs, 5 com foco, quase todos sobre seca ou mosca-branca, não sobre rotação;
   - **sorgo:** 11 PDFs, 5 com foco;
   - **palma forrageira:** 2;
   - **caju:** 1;
   - **guandu e gliricídia:** 1 cada.
   - **Nenhum artigo de rotação usa caupi → milho ou mandioca → caupi com dado medido no semiárido.** A revisão já
     registrava essa lacuna.
3. **O que existe sobre as culturas locais** é principalmente fisiologia, seca ou consórcio:
   - Souza 2011 e Santos 2026: caupi e água;
   - Carvalho 2016: mandioca e seca;
   - Diniz 2017: palma × sorgo irrigado;
   - Bezerra 2007: fisiologia do caju;
   - Azambuja 2014: bicudo.
4. **Forrageiras do semiárido e adubação verde não aparecem nos artigos baixados:** buffel e Urochloa, leucena,
   crotalária, mucuna, gergelim e mamona. São exatamente as opções de **cobertura e forragem na entressafra** que a
   QUADRA quer comparar.

## Consequência para o produto

- **Para milho, feijão, sorgo, amendoim e algodão**, o motor de rotação pode usar os efeitos das meta-análises
  (Zhao 2022, Mudare 2025) com a ressalva de que vêm de outros climas. Funciona como **prior**, com evidência de grau B ou C.
- **Para caupi, mandioca, palma, caju, gliricídia, leucena e buffel**, o motor deve usar **exigências da cultura**
  (FAO ECOCROP, GAEZ, ZARC) e **dados locais** (IBGE PAM, nosso teste de diversidade), mostrando "evidência fraca" no
  recibo. Fingir um efeito de rotação medido seria desonesto.
- **Lacunas para pesquisar** (próxima rodada da revisão): leucena e gliricídia em aleias no semiárido (Embrapa), palma
  forrageira em consórcio ou rotação, buffel e Urochloa em integração lavoura-pecuária no Nordeste, e plantas de
  cobertura do semiárido (crotalária, mucuna, feijão-de-porco).
