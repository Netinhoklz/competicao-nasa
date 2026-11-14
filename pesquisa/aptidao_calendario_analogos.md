# O que plantar, quando plantar e de onde transferir: artigos globais + análogos climáticos

Conferido no Crossref em 14/11/2026 (`scripts/verificar_aptidao_calendario.py`). 📄 = PDF em `artigos/`; 🔗 = abrir pelo DOI.

## 1. O que plantar onde (aptidão)

| Artigo | O que é | Como cruza com os nossos dados | |
|---|---|---|---|
| Fischer et al. 2021, *GAEZ v4 Model documentation* (FAO), [10.4060/cb4744en](https://doi.org/10.4060/cb4744en) | Aptidão global de dezenas de culturas por clima, solo e relevo | Já temos 306 camadas (seção 11). Serve de filtro de culturas candidatas | 📄 |
| Zabel et al. 2014, *PLOS ONE*, [10.1371/journal.pone.0107522](https://doi.org/10.1371/journal.pone.0107522) (371 citações) | Aptidão global de alta resolução por clima, solo e relevo, com perspectivas até 2100 | Segunda opinião ao GAEZ; o cenário futuro conversa com o NEX-GDDP | 📄 |
| Ramirez-Villegas et al. 2013, *Agric. For. Meteorol.*, [10.1016/j.agrformet.2011.09.005](https://doi.org/10.1016/j.agrformet.2011.09.005) | Modelo EcoCrop: aptidão por faixas de temperatura e chuva (caso do sorgo) | Roda com a climatologia mensal do POWER ou do IMERG, em qualquer lugar | 📄 |
| Chevuru et al. 2026, *Scientific Data*, [10.1038/s41597-026-07164-9](https://doi.org/10.1038/s41597-026-07164-9) | **Grade global (0,5°, 1961–2100) de rendimento e uso de água simulados para várias variedades e datas de semeadura** de milho, soja, trigo e arroz (modelo WOFOST, 5 modelos climáticos, 3 cenários) | Para o milho, diz qual variedade e qual data mantêm o rendimento e economizam água no presente e no futuro | 📄 |

## 2. Quando plantar (calendários de cultivo)

| Artigo | O que é | Como cruza | |
|---|---|---|---|
| Waha et al. 2012, *Global Ecol. Biogeogr.*, [10.1111/j.1466-8238.2011.00678.x](https://doi.org/10.1111/j.1466-8238.2011.00678.x) | **Regras climáticas de semeadura** para 11 culturas: início da estação chuvosa ou limiar de temperatura. Validadas contra o MIRCA2000, com erro < 1 mês em ≥ 50% das células para todas as culturas, exceto colza e mandioca | A regra do início da chuva roda com o IMERG diário. O nosso início médio no Ceará é ~17/jan (seção 2) | 🔗 |
| Sacks et al. 2010, *Global Ecol. Biogeogr.*, [10.1111/j.1466-8238.2010.00551.x](https://doi.org/10.1111/j.1466-8238.2010.00551.x) (837 citações) | Calendário global de plantio e colheita | Referência para checar o calendário do Ceará | 🔗 (pago) |
| Portmann et al. 2010, *Global Biogeochem. Cycles*, [10.1029/2008gb003435](https://doi.org/10.1029/2008gb003435) | MIRCA2000: área mensal irrigada e de sequeiro por cultura | Calendário e sequeiro/irrigado por cultura | 🔗 |
| Jägermeyr et al. 2021, *Nature Food*, [10.1038/s43016-021-00400-y](https://doi.org/10.1038/s43016-021-00400-y) | Impactos climáticos com a nova geração de modelos (GGCMI fase 3), com calendário de cultivo harmonizado | Projeções de rendimento para milho, soja, trigo e arroz | 📄 |
| Franch et al. 2022, *GIScience & Remote Sensing*, [10.1080/15481603.2022.2079273](https://doi.org/10.1080/15481603.2022.2079273) | **Calendários globais de milho e trigo derivados de satélite** (WorldCereal) | Compara com a nossa fenologia MODIS e VIIRS (início ~2/fev, pico ~23/abr) | 🔗 |
| Whitcraft et al. 2015, *Remote Sens. Environ.*, [10.1016/j.rse.2014.10.009](https://doi.org/10.1016/j.rse.2014.10.009) | Cobertura de nuvens na estação de cultivo e o limite do satélite óptico | Explica o nosso achado (7–25% de cenas limpas em fev–mai) e justifica o micro-ondas (SMAP e NISAR) | 🔗 (pago) |

Também temos os dados de "onde se planta e quanto rende" globais: Yu et al. 2020 (SPAM 2010) 📄 e Iizumi & Sakai 2020
(GDHY, rendimento histórico 1981–2016) 📄.

## 3. De onde transferir resultados: análogos climáticos (seção 18)

Com a **climatologia do NASA POWER**, comparamos a assinatura climática de 20 lugares onde os artigos foram feitos com
12 pontos do Ceará. A assinatura usa:
- chuva anual;
- sazonalidade;
- meses úmidos;
- aridez P/ET0;
- Tmax da estação úmida e Tmax do mês mais quente. **Corrigido em 14/11 (tarde):** a Tmax e a Tmin agora são a média
  das diárias de 2001–2024; antes, eram o recorde do mês da climatologia do POWER (`protótipo/REVISAO_10_AGENTES.md`,
  C2).

Script: `scripts/analogos_climaticos_artigos.py`. Dados: `E:/campeonato-nasa/dados/analogos_artigos/distancias.csv`.

**Sertão Central (Quixadá), análogos mais próximos (distância z; antes da correção entre parênteses):**
- **Cerrado piauiense, 0,32 (0,63):** Pacheco;
- **Semiárido da Índia (Patancheru), 0,75 (1,58):** referência de semiárido tropical (sorgo, milheto, caupi);
- **Serra Talhada-PE, 1,09 (1,05):** palma-sorgo;
- **Sobral-CE, 1,12 (1,18):** Sacramento 2013 (carbono do solo medido);
- Savana da Guiné (Tamale), 1,67 (1,84): Franke 2018.
- **A África Austral (Harare) deixou de ser análogo:** 2,15 (1,34), em 10º lugar.

**Os mais distantes:**
- Iowa (4,87), França (5,89) e Ontário (5,97): os climas de Kluger, Bowles e Renwick;
- Texas e Kansas (2,80 e 3,98): semiárido temperado.

**Regra para o motor:** peso de transferência w = exp(−d²/2). Os números dos celeiros temperados entram como mecanismo,
com peso ~0. Os do Nordeste entram como valor. Os do Franke (África) chegam a Quixadá com w ≤ 0,25 e ficam só como
sensibilidade.

## 4. O que fazer com isso no produto

1. **Onde:** GAEZ (+ Zabel) filtra as culturas aptas no talhão.
2. **Quando:** regra de Waha com o IMERG para o início da chuva; conferir contra os calendários (Sacks, MIRCA, WorldCereal)
   e a nossa fenologia.
3. **O quê e de que jeito:** para o milho, Chevuru 2026 indica variedade e data no clima de hoje e de 2050. Para as
   demais culturas, o catálogo de rotações comprovadas (em produção pelos 10 agentes), **ponderado pela semelhança
   climática** do lugar de cada artigo.
