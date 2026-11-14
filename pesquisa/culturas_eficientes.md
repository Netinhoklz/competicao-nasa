# Culturas que os nossos artigos sustentam com eficiência

Critério: uma cultura é "eficiente" para o produto quando reúne quatro coisas:
- (a) **efeito de rotação medido** em artigo, de preferência em meta-análise, com número e intervalo;
- (b) **contexto parecido** com o semiárido: baixo insumo, sequeiro ou trópico;
- (c) **dados nossos** para calibrar: IBGE PAM, GAEZ, FAOSTAT;
- (d) **peso no Ceará:** área colhida média de 2019–2024 no IBGE PAM.

Fontes: `pesquisa/evidencia_por_cultura.json`, `pesquisa/culturas_nos_artigos.md`, `pesquisa/meta_analises_globais.md`.
Os resumos e textos foram conferidos no OpenAlex e nas editoras.

## Nível A — evidência forte e aplicável: o núcleo do motor

| Cultura | Papel na rotação | O que os artigos medem | Dados nossos | Área no CE |
|---|---|---|---|---|
| **Milho** | cultura principal, a que se beneficia | Após leguminosa: **+20%**, +32% em ambiente de baixa produtividade (Zhao 2022). Na África Subsaariana, **+41% (+0,49 t/ha)** após leguminosa, com resposta maior que a de sorgo e milheto (Franke 2017). Diversidade: +28% e menos perda em seca (Bowles 2020); −17% de perda na seca (Renwick 2021). Benefício varia com o clima (Kluger 2025; Zhou 2024) | PAM (rendimento +10% por +100 mm), GAEZ (insumo baixo: SI 49), FAOSTAT | **39,7%** |
| **Feijão comum, feijão-caupi e amendoim** | **leguminosa antecessora** ou em consórcio | Todas as leguminosas de grão elevaram o cereal seguinte na África; **amendoim e soja deram efeito maior que o caupi** (Franke 2017). Consórcio milho/leguminosa na África com LER > 1 e +0,90 t/ha, e **milho/feijão comum foi o melhor consórcio na África** (Mudare 2022). Leguminosa como cultura anterior: +23% na cultura seguinte (Mudare 2025) | PAM (feijão), GAEZ (feijão SI 50; caupi SI 45 no insumo baixo), FAOSTAT | **25,9%** (feijão) |

**Ressalva para o semiárido (Franke 2017):** o efeito da leguminosa foi **menor na zona sudano-saheliana**, o análogo
semiárido africano. O produto deve usar a faixa baixa desses ganhos no Ceará.

## Nível B — evidência moderada: entra com cautela

| Cultura | Papel | Evidência | Dados | Área no CE |
|---|---|---|---|---|
| **Sorgo** | cereal tolerante à seca e forragem | Responde menos à leguminosa que o milho (Franke 2017). **Sorgo → milho-sorgo perdeu 32% de rendimento e 31% de receita** (Mudare 2025). Consórcio palma-sorgo irrigado no semiárido: 6.279 contra 4.627 kg MS/ha da palma solteira (Diniz 2017). Híbridos tolerantes à seca (Menezes 2021) | GAEZ: **melhor aptidão no insumo baixo (SI 53)**; PAM | pequena |
| **Algodão** | cultura de renda; quebra de ciclo do bicudo | Exigências térmicas e zoneamento do bicudo (Pereira 2023; Jin 2022); 30 anos de bicudo no Brasil (Azambuja 2014); percolação no CDL do Texas (seção 16) | GAEZ (SI 71 no insumo alto, **35 no baixo**); PAM (queda de 1,25 Mha a ~0) | 0,2% |
| **Milheto** | cereal tolerante | Só Franke 2017 (resposta menor que a do milho) | GAEZ | — |
| **Soja, trigo, arroz** | (produto global) | Muita evidência (Kluger, Zhao, Mudare, Smith, Yang 2024), mas pouca relevância para o Ceará | CDL, FAOSTAT | ~0 / 0,4% |

## Nível C — só fisiologia ou seca: sem efeito de rotação medido

| Cultura | Evidência que temos | Como usar |
|---|---|---|
| **Mandioca** | Tolerância à seca (Carvalho 2016); umidade do solo × rendimento no semiárido (Rossato 2017); mosca-branca (Kriticos 2020) | **Cultura-tampão** pelos nossos dados: só +3% de rendimento por +100 mm (PAM). Sem efeito de rotação da literatura |
| **Palma forrageira** | Consórcio com sorgo (Diniz 2017) | Forragem de entressafra; consórcio em vez de rotação |
| **Caju** | Fisiologia sob estresse (Bezerra 2007) | Perene (19,4% da área): contexto da propriedade, não rotação |
| **Batata-doce** | Rotação na China: até +38% de rendimento equivalente e +45% de saúde do solo (Yang 2024) | Analogia distante (clima temperado) |

## Nível D — sem artigo na nossa base

Guandu, gliricídia, leucena, buffel, Urochloa, crotalária, mucuna, gergelim e mamona. Para estes o motor usa só
**exigências da cultura** (ECOCROP, GAEZ, ZARC) e mostra "sem evidência de rotação". **Próxima busca:** Embrapa
Semiárido / Caprinos e Ovinos (aleias de leucena e gliricídia, palma, buffel e integração lavoura-pecuária).

## Recomendação para o MVP

O conjunto que dá para sustentar com artigos **e** dados é:
- **milho** como cultura principal;
- **feijão comum, feijão-caupi e amendoim** como leguminosa antecessora ou em consórcio, com a faixa baixa de ganho no
  semiárido;
- **sorgo** como cereal tolerante, com o alerta de Mudare 2025;
- **mandioca** como tampão, pelos nossos dados;
- **palma** em consórcio para forragem.

Só milho, feijão e mandioca já somam **70% da área colhida total do Ceará** (temporárias + permanentes, PAM 2019–2024:
39,7% + 25,9% + 4,5%). O conjunto permite comparar as 3+ estratégias do desafio com recibo de evidência A–C por cultura.
