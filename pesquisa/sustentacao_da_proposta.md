# Sustentação da proposta: o que afirmamos, quem já mostrou e o que medimos

Complemento de `artigos_e_datasets.md` (73 artigos). Aqui cada afirmação da apresentação aponta para a literatura
e para o número que nós mesmos medimos. Referências "x.y" são as daquela revisão.

Marcação das referências novas:
- **[busca]** título e veículo confirmados em busca na web em 14/11/2026;
- **[memória]** citada de memória, sem conferência nesta rodada: **conferir DOI, ano e páginas antes de usar em slide**.

## 1. Mapa afirmação → evidência

| # | O que afirmamos | Literatura | O que medimos |
|---|---|---|---|
| 1 | A planta sofre antes de perder o verde: o sinal térmico e de evapotranspiração antecede o NDVI | Otkin et al. 2013 [busca]; Otkin et al. 2018 [busca]; Anderson et al. 2016 (7.4); Fisher et al. 2020 (7.8) | Dentro do mesmo ano, NDVI + temperatura de superfície ordenam os municípios do Ceará por rendimento (ρ 0,23–0,31; positivo em 25 de 26 anos); a chuva não ordena (ρ ≈ 0) |
| 2 | Temperatura × verde dá um índice de secura sem precisar de estação | Sandholt et al. 2002 [memória] | LST × NDVI com r de −0,56 a −0,77 em todos os meses; TVDI do Ceará vai de 0,54 (abr/2009) a 0,75 (out/2012) |
| 3 | A chuva do norte do Nordeste depende do Atlântico e do Pacífico | Hastenrath & Heller 1977 [memória]; Moura & Shukla 1981 [memória]; Nobre & Shukla 1996 (6.1); Kayano & Andreoli 2006 (6.2) | Dipolo × chuva da estação: RN −0,49, MA −0,46, CE −0,45; nada em PE, SE, AL, BA (seção 2) |
| 4 | A previsão sazonal existe, mas é modesta: falar em probabilidade | Rocha Júnior et al. 2021 (6.3); Lemos et al. 2002 [busca] | Tercil da quadra: 41% de acerto contra 33% do acaso (Ceará) |
| 5 | O início da estação antecipa a estação | Liebmann & Marengo 2001 [memória] (método usado no notebook) | Dia de início × total da estação: ρ = −0,67 (Ceará) |
| 6 | Seca derruba milho e feijão; veranico importa | Rocha et al. 2021 (6.6); Marengo et al. 2018 (6.4); Rossato et al. 2017 (7.5) | +100 mm na estação: milho +11%, feijão +8% no Ceará; ver os outros estados na seção 2 |
| 7 | Rotação diversa e leguminosa protegem o rendimento em ano ruim | Bowles et al. 2020 (1.1); Zhao et al. 2022 (1.4); Renwick et al. 2021 (1.2) | Não medimos: entra como premissa declarada no simulador |
| 8 | Queima sem pousio degrada o solo do semiárido | Primo et al. 2023 (3.9); Salcedo et al. 1997 (3.8) | 72% dos focos em out–dez; 62% na Caatinga |
| 9 | Monocultura em paisagem conectada favorece praga | Margosian et al. 2009 (4.1); Azambuja & Degrande 2014 (4.10) | Algodão no Ceará: 306 mil ha (1985) → ~2 mil ha |
| 10 | Validação aleatória superestima o modelo; é preciso deixar ano/região de fora | Roberts et al. 2017 [busca]; Ploton et al. 2020 [busca] | Mesmo modelo: R² 0,40 (aleatória) → −0,09 (deixando o ano de fora) |
| 11 | O agricultor julga a previsão pela chuva do seu município; a mensagem tem de ser local e simples | Lemos et al. 2002 [busca]; Zeri et al. 2018 (7.3) | Desenho: semáforo por talhão, tercis, anos parecidos |
| 12 | O satélite de chuva precisa de conferência com pluviômetro | Rozante et al. 2018 (7.12) | IMERG em 41–60% das normais no litoral leste, 82–94% no sertão |

## 2. Expansão para o Nordeste (análise nova, por estado)

Script: `conselho/analises/jp_expansao_nordeste.py`. Dados: IMERG e NDVI MODIS por estado (derivados do repositório),
rendimento estadual do IBGE PAM (API SIDRA), 1998–2024. Spearman; com ~27 anos, |ρ| < 0,38 não é significativo a 5%.

| Estado | Início da estação | Chuva × milho | Chuva × feijão | Dipolo × chuva | Milho por +100 mm |
|---|---|---|---|---|---|
| CE | jan | **0,59** | **0,51** | **−0,45** | +11,4% |
| RN | fev | 0,34 | **0,51** | **−0,49** | +5,3% |
| PB | jan | **0,42** | 0,32 | −0,33 | +8,7% |
| PI | jan | 0,16 | **0,56** | −0,30 | +5,4% |
| MA | jan | 0,28 | 0,37 | **−0,46** | +3,2% |
| SE | fev | 0,31 | 0,27 | −0,09 | +6,9% |
| PE | jan | 0,17 | 0,06 | −0,12 | +0,3% |
| AL | mar | 0,21 | 0,20 | 0,03 | +5,1% |
| BA | nov | 0,17 | 0,21 | 0,00 | +2,1% |

Leitura:
- **A cadeia oceano → chuva → safra do Ceará se repete no bloco norte** (CE, RN, PB e, para feijão, PI). É o recorte
  que se sustenta com dado: "Semiárido setentrional".
- **Não se repete em PE, AL, SE e BA.** A Bahia tem estação de novembro a fevereiro e nenhuma ligação com o dipolo.
- **O ONI sozinho ficou fraco em todos os estados** neste período (−0,05 a −0,28). O número mais forte do notebook
  (−0,39 a −0,46) vem de uma série mais longa (1981–2025) e só do Ceará.
- **NDVI médio do estado é um instrumento grosso**: só CE e RN mostram relação com rendimento. No Ceará o sinal
  aparece de verdade na escala de município.

Limites desta análise:
- média estadual mistura regimes (sertão, agreste e litoral em PE e BA) e sistemas (grão de alta tecnologia no
  cerrado de MA, PI e BA pesa no rendimento estadual e depende menos da chuva);
- o IMERG subestima a chuva do litoral leste, o que enfraquece AL e SE;
- 27 anos por estado é pouco; o teste por município está na seção 2b.

## 2b. O mesmo teste por município (1.794 municípios)

Script: `conselho/analises/jp_nordeste_municipios.py`. Dados do José (`dados_resumo/derivados/ibge_ne_*`): IMERG V07 e
SMAP L4 agregados na malha municipal, PAM municipal 1995–2024. "Firme" = Spearman ≥ 0,38; o acaso daria ~2,5% dos
municípios.

| Estado | Municípios | Chuva × milho firme | Chuva × feijão firme | Dipolo × chuva firme | Chuva depois de El Niño forte (mediana) |
|---|---|---|---|---|---|
| CE | 184 | **65%** | 38% | **64%** | 78% do normal |
| PI | 224 | **55%** | 32% | 35% | 89% |
| PB | 223 | **54%** | 36% | 15% | 94% |
| PE | 185 | 40% | 31% | 1% | 94% |
| RN | 167 | 38% | 31% | 44% | 84% |
| MA | 217 | 13% | 6% | **68%** | 81% |
| BA | 417 | 6% | 9% | 0% | 106% |
| AL | 102 | 6% | 2% | 0% | 93% |
| SE | 75 | 1% | 4% | 0% | 84% |

Leitura:
- **Na escala do município o sinal é bem mais forte que na média estadual.** Piauí e Pernambuco, fracos por estado,
  têm 55% e 40% dos municípios com ligação firme: a média estadual escondia o sertão atrás do cerrado e do litoral.
- **O recorte que se sustenta é o Semiárido**: 39% dos municípios do Semiárido (delimitação de 2022) com ligação
  firme para milho, contra 10% fora dele. Elasticidade mediana: +12,7% de milho por +100 mm, contra +1,9%.
- **AL, SE e BA continuam sem sinal**, e o Maranhão tem o oceano mandando na chuva (68%) sem a chuva mandar no milho (13%).
- Depois de El Niño forte (1998, 2010, 2016, 2024) a chuva da estação ficou em 78% do normal no Ceará e acima do
  normal no centro da Bahia. São só quatro eventos.
- O percentil pronto do SMAP (`pctl_media`) vem nulo justamente nos municípios mais secos (1.356 de 1.794 em
  out/2026); a página usa a posição do mês entre os mesmos meses desde 2015.

Página para o agricultor com o mapa: `interface-nordeste-jp/index.html`.

## 3. Podemos usar dados do IBGE?

O IBGE PAM é dado público e aberto. O guia de submissão do Space Apps de 2022 dizia que qualquer dado aberto pode
ser usado, desde que o projeto use também dado da NASA ou de agência parceira para concorrer na etapa global. Não
achamos a frase equivalente no guia de 2026: **conferir no regulamento deste ano**. No nosso caso o IBGE entra só
como verdade de campo para validar; o produto roda com dados da NASA.

## 4. Lacunas

- Não achamos estudo revisado por pares que meça em quantos dias o ECOSTRESS antecipa o estresse em lavoura
  comercial; o que existe são materiais da NASA/JPL e os trabalhos com o ESI (Otkin, Anderson).
- Não medimos o estresse silencioso por talhão no Nordeste: depende de baixar ECOSTRESS (conta Earthdata).
- Não achamos avaliação recente de como o agricultor familiar usa a previsão da FUNCEME.

## 5. Referências novas

- Otkin, J.A. et al. (2013). *Examining Rapid Onset Drought Development Using the Thermal Infrared–Based Evaporative
  Stress Index.* Journal of Hydrometeorology 14. [busca] https://www.ssec.wisc.edu/~jasono/papers/otkin_jhm_aug2013.pdf
- Otkin, J.A. et al. (2018). *Flash Droughts: A Review and Assessment of the Challenges Imposed by Rapid-Onset
  Droughts in the United States.* BAMS 99. [busca] https://www.ssec.wisc.edu/~jasono/papers/otkin_bams_may2018.pdf
- Roberts, D.R. et al. (2017). *Cross-validation strategies for data with temporal, spatial, hierarchical, or
  phylogenetic structure.* Ecography 40(8):913–929. [busca] https://doi.org/10.1111/ecog.02881
- Ploton, P. et al. (2020). *Spatial validation reveals poor predictive performance of large-scale ecological mapping
  models.* Nature Communications 11:4540. [busca] https://hal.inrae.fr/hal-02936567v1/document
- Lemos, M.C.; Finan, T.J.; Fox, R.W.; Nelson, D.R.; Tucker, J. (2002). *The Use of Seasonal Climate Forecasting in
  Policymaking: Lessons from Northeast Brazil.* Climatic Change. [busca: título e autores; ano e veículo de memória]
  https://experts.arizona.edu/en/publications/the-use-of-seasonal-climate-forecasting-in-policymaking-lessons-f/
- NASA Earth Observatory. *Detecting Invisible Plant Stress* (ECOSTRESS). [busca]
  https://science.nasa.gov/earth/earth-observatory/detecting-invisible-plant-stress-145823
- Sandholt, I.; Rasmussen, K.; Andersen, J. (2002). *A simple interpretation of the surface temperature/vegetation
  index space for assessment of surface moisture status.* Remote Sensing of Environment 79. [memória]
- Hastenrath, S.; Heller, L. (1977). *Dynamics of climatic hazards in northeast Brazil.* QJRMS 103. [memória]
- Moura, A.D.; Shukla, J. (1981). *On the dynamics of droughts in northeast Brazil.* J. Atmospheric Sciences 38. [memória]
- Liebmann, B.; Marengo, J.A. (2001). *Interannual variability of the rainy season and rainfall in the Brazilian
  Amazon Basin.* Journal of Climate 14. [memória]
- Regimes de chuva do Nordeste (norte fev–mai × leste): artigo em Frontiers in Environmental Science (2015), a
  identificar. [busca] https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2015.00034/full
