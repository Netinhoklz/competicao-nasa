# Field Shift: revisão de artigos e datasets

NASA Space Apps Challenge 2026, desafio "Field Shift: Adapting Farms with NASA Data". Demonstração no Ceará e no Nordeste do Brasil.

Levantamento feito em 13/11/2026. São 73 artigos detalhados e 40 datasets detalhados. Cada seção termina com uma lista curta de leituras e datasets complementares, também verificados.

**Como ler a verificação** (aparece entre colchetes no fim de cada referência):

| Marca | Significado |
|---|---|
| `DOI✓` | DOI conferido no Crossref ou no OpenAlex: autor, título, revista e ano batem |
| `pág.` | achado lido na página ou no PDF do artigo |
| `resumo` | achado lido no resumo oficial (Crossref, OpenAlex ou Semantic Scholar) |
| `snippet` | achado visto só no trecho do resultado de busca; conferir no texto antes de citar números em público |
| `DOI não confirmado` | o DOI não foi conferido; nesse caso vai a URL que foi vista |

---

## Sumário executivo

1. **Rotação diversa:** +28% no milho e perdas 14–90% menores em ano seco (Bowles 2020); leguminosa antecessora dá +20%, ou +32% em baixa produtividade, e o efeito zera acima de cerca de 236 kg N/ha (Zhao 2022). O sequeiro de baixo insumo é onde mais se ganha.
2. **Consórcio:** +23% na África (Himmelstein 2016); milho + caupi foi economicamente melhor em Petrolina (Souza 2011); palma + sorgo foi mais estável (Diniz 2017). Uma das três estratégias deve ser "consórcio + leguminosa".
3. **Corte e queima sem pousio:** −50% de carbono do solo em 10 anos e cerca de 50 anos para recuperar, contra cerca de 10 anos na agrofloresta (Primo 2023, Sobral-CE). Justifica penalizar o fogo.
4. **Fogo na Caatinga:** pico de agosto a novembro; o SPI antecede o fogo em cerca de 4 meses; ano chuvoso seguido de ano seco gera grandes queimadas (Bezerra 2025; Argibay 2020). O MapBiomas Fogo tem 40 anos a 30 m.
5. **Chuva no Ceará:** veranicos (3 ou mais dias com até 2 mm, de fevereiro a maio) explicam a perda de milho e feijão, que somam 91% da área (Rocha 2021). O ENSO sozinho acerta só 36% (Kayano & Andreoli 2006); o Atlântico também entra.
6. **ZARC:** tábua aberta (CC BY) por município × cultura × solo × decêndio. É a restrição de janela que também condiciona crédito e seguro.
7. **Pragas:** Margosian 2009 **não usa o CDL** (correção). Há graus-dia publicados para a lagarta-do-cartucho (base de cerca de 12,6 °C) e para o bicudo (ótimo de 25–28 °C). A rotação pode ser quebrada por adaptação da praga (Levine 2002).
8. **NASA no Brasil:** o IMERG supera o TMPA, mas subestima a chuva no litoral do Nordeste; o ESI antecipa o efeito na produtividade em 10–25 dias; o GRACE mostra −31 km³ no Urucuia; o NISAR a 200 m ainda é provisório.
9. **Adequação global:** o GAEZ v5 (abril de 2025) inclui caju, com camada de adequação NC. Também servem ECOCROP (Recocrop, 1.710 táxons), MIRCA-OS, SPAM 2020 e CROPGRIDS (173 culturas). A API do SoilGrids está pausada.
10. **Kaggle "Crop Recommendation":** tem cara de sintético (100 linhas por classe, valores uniformes, RF com 99,45%). Não usar como evidência.
11. **CDL e CSB só cobrem os EUA.** No Ceará, usar MapBiomas, PAM e fenologia de NDVI, porque a classe "outras lavouras temporárias" mistura as culturas do sertão.

---

## 1. Rotação de culturas e saúde do solo

### Artigos

**1.1 Bowles, T.M. et al. (2020).** *Long-Term Evidence Shows that Crop-Rotation Diversification Increases Agricultural Resilience to Adverse Growing Conditions in North America.* One Earth 2(3):284–293. https://doi.org/10.1016/j.oneear.2020.02.007 [DOI✓ · snippet]
- Achado: 347 sítio-anos de 11 experimentos de longa duração. Rotações diversas aumentaram a produtividade do milho em 28,1% em média e reduziram as perdas em anos de seca em 14,0% a 89,9%.
- Uso: é a principal evidência para o indicador de resiliência. O motor reduz a perda esperada em ano seco conforme a diversidade da rotação.

**1.2 Renwick, L.L.R. et al. (2021).** *Long-term crop rotation diversification enhances maize drought resistance through soil organic matter.* Environmental Research Letters 16:084067. https://doi.org/10.1088/1748-9326/ac1468 [DOI✓ · snippet]
- Achado: com abrigos de exclusão de chuva num ensaio de 36 anos, incluir cereais de inverno e plantas de cobertura cortou a perda do milho na seca em 17,1 ± 6,1%. O mecanismo passa pela matéria orgânica do solo.
- Uso: liga carbono do solo e tolerância à seca. A resiliência pode ser modelada via COS, que vem do SoilGrids e do MapBiomas Solo.

**1.3 MacLaren, C. et al. (2022).** *Long-term evidence for ecological intensification as a pathway to sustainable agriculture.* Nature Sustainability 5:770–779. https://doi.org/10.1038/s41893-022-00911-x [DOI✓ · snippet]
- Achado: 30 experimentos de longa duração na Europa e na África (25.565 registros). Diversidade, culturas de fertilidade e matéria orgânica elevam a produtividade. O ganho some quando somadas a muito fertilizante.
- Uso: confirma que o benefício da rotação é maior com pouco insumo, como no sequeiro do sertão. O motor deve condicionar o ganho ao nível de adubação informado pelo agricultor.

**1.4 Zhao, J. et al. (2022).** *Global systematic review with meta-analysis reveals yield advantage of legume-based rotations and its drivers.* Nature Communications 13:4926. https://doi.org/10.1038/s41467-022-32464-0 [DOI✓ · pág.]
- Achado: 11.768 observações de 462 experimentos em 53 países. A leguminosa antecessora dá +20% na cultura seguinte: +32% em ambientes de baixa produtividade contra +7% nos de alta. O efeito cai cerca de 7% a cada 50 kg N/ha e zera acima de 236 kg N/ha.
- Uso: fornece o coeficiente quantitativo para o "efeito da cultura antecessora" no motor, por exemplo feijão-caupi antes de milho ou sorgo.

**1.5 Yang, X. et al. (2024).** *Diversifying crop rotation increases food production, reduces net greenhouse gas emissions and improves soil health.* Nature Communications 15:198. https://doi.org/10.1038/s41467-023-44464-9 [DOI✓ · snippet]
- Achado: **é experimento de campo de 6 anos, não meta-análise**, feito na Planície do Norte da China. Rotações com batata-doce, amendoim e soja deram:
  - até +38% de produção equivalente;
  - −39% de N₂O;
  - +8% de carbono do solo;
  - +45% no índice de saúde do solo.
- Uso: é exemplo de métrica composta de "saúde do solo" e de comparação multiobjetivo entre rotações, com produção, emissões e solo lado a lado.

**1.6 McDaniel, M.D.; Tiemann, L.K.; Grandy, A.S. (2014).** *Does agricultural crop diversity enhance soil microbial biomass and organic matter dynamics? A meta-analysis.* Ecological Applications 24:560–570. https://doi.org/10.1890/13-0616.1 [DOI✓ · snippet]
- Achado: 122 estudos. A rotação elevou o C da biomassa microbiana em 20,7% e o N em 26,1%. O C total subiu 3,6%, ou 8,5% com planta de cobertura. A AGRIS registra uma errata de 2022, que não foi conferida.
- Uso: dá a ordem de grandeza do ganho de C e N por rotação e cobertura. Serve como prior do indicador de solo.

**1.7 Jian, J. et al. (2020).** *A meta-analysis of global cropland soil carbon changes due to cover cropping.* Soil Biology and Biochemistry 143:107735. https://doi.org/10.1016/j.soilbio.2020.107735 [DOI✓ · snippet]
- Achado: plantas de cobertura elevam o carbono do solo em 15,5% (IC 13,8–17,3%), cerca de 0,56 Mg C/ha/ano, só nos primeiros 30 cm. Misturas e leguminosas são as melhores.
- Uso: é a taxa padrão de sequestro para a estratégia "com cobertura/adubo verde" no simulador de COS.

**1.8 Abdalla, M. et al. (2019).** *A critical review of the impacts of cover crops on nitrogen leaching, net greenhouse gas balance and crop productivity.* Global Change Biology 25:2530–2543. https://doi.org/10.1111/gcb.14644 [DOI✓ · snippet]
- Achado: 106 estudos. A cobertura reduz a lixiviação de N e mitiga 2,06 ± 2,10 Mg CO₂-eq/ha/ano. Penaliza a cultura principal em cerca de 4%, mas a mistura de leguminosa com não leguminosa dá cerca de +13%.
- Uso: entra na coluna de **riscos/trade-offs**. A cobertura pode custar produtividade e, no semiárido, também água.

**1.9 Beillouin, D. et al. (2021).** *Positive but variable effects of crop diversification on biodiversity and ecosystem services.* Global Change Biology 27:4697–4710. https://doi.org/10.1111/gcb.15747 [DOI✓ · snippet]
- Achado: síntese de 95 meta-análises (5.156 experimentos). Diversificar dá +14% de produção (mediana), +63% de controle de pragas e doenças e +11% de qualidade do solo, com grande variabilidade.
- Uso: fornece priors para vários indicadores ao mesmo tempo. A variabilidade alta justifica mostrar intervalos e não só médias.

**1.10 Franke, A.C. et al. (2018).** *Sustainable intensification through rotations with grain legumes in Sub-Saharan Africa: A review.* Agriculture, Ecosystems & Environment 261:172–185. https://doi.org/10.1016/j.agee.2017.09.029 [DOI✓ · snippet]
- Achado: leguminosas de grão trazem benefícios por N e "não N". Os efeitos são mais fracos na zona sudano-saheliana, a mais seca.
- Uso: é um análogo semiárido tropical. Mostra que o ganho da leguminosa encolhe com a aridez, então o motor deve modular o efeito pelo índice de aridez.

**1.11 Rusinamhodzi, L. et al. (2011).** *A meta-analysis of long-term effects of conservation agriculture on maize grain yield under rain-fed conditions.* Agronomy for Sustainable Development 31:657–673. https://doi.org/10.1007/s13593-011-0040-2 [DOI✓ · snippet]
- Achado: em sequeiro de baixa chuva, a agricultura de conservação com rotação e insumos aumenta o milho com o tempo; a rotação elevou a produtividade em 63% dos dados. O preparo reduzido sem cobertura reduziu a produtividade no semiárido.
- Uso: é uma regra de risco. "Plantio direto sem palha" não deve receber bônus no sertão.

**1.12 Himmelstein, J. et al. (2016; vol. 15).** *A meta-analysis of intercropping in Africa: impacts on crop yield, farmer income, and integrated pest management effects.* International Journal of Agricultural Sustainability 15:1–10. https://doi.org/10.1080/14735903.2016.1242332 [DOI✓ · resumo]
- Achado: o consórcio aumenta a produtividade em 23% e a renda bruta em US$ 172/ha em média, com grande variação por manejo e agroecologia.
- Uso: dá suporte quantitativo à estratégia "consórcio", que é a prática tradicional de milho + feijão no Ceará.

### Datasets

**D1. MapBiomas Solo** (MapBiomas)
- Contém:
  - Coleção 3 (2026): carbono do solo de 0–30 cm, anual, de 1985 a 2024; areia, silte e argila em camadas de 10 cm até 100 cm; textura; profundidade até a pedregosidade.
  - Versão beta (2023): carbono do solo de 0–30 cm, de 1985 a 2021, com 9.650 amostras.
- Resolução: 30 m (na Coleção 3, só por snippet); anual.
- Cobertura: Brasil.
- Acesso: gratuito. Os documentos são CC BY 4.0; a licença dos mapas não foi confirmada.
- URL: https://data.mapbiomas.org (mapas beta em doi:10.58053/MapBiomas/DHAYLZ; documento técnico da Coleção 3 em doi:10.58053/MapBiomas/OUQCLO).
- Uso: linha de base de carbono do solo por pixel no Ceará, para projetar ganho ou perda de carbono em cada estratégia (cobertura, consórcio, queima).

SoilGrids, HWSD e WoSIS estão na seção 5.

**Leituras complementares (verificadas):**
- Gaudin et al. 2015, PLOS ONE, 10.1371/journal.pone.0113261: em anos quentes e secos, a rotação diversa deu +7% no milho e +22% na soja.
- Marini et al. 2020, ERL, 10.1088/1748-9326/abc651.
- Smith, M.E. et al. 2023, **Communications Earth & Environment** 4:89, 10.1038/s43247-023-00746-0. Não é da Nature Sustainability.
- King & Blesh 2018, Ecological Applications 28:249–261, 10.1002/eap.1648: leguminosa de grão em rotação de cereais reduziu o carbono do solo em cerca de 5%. É um alerta útil.
- Tiemann et al. 2015, Ecology Letters, 10.1111/ele.12453.
- Liu et al. 2022, AGEE 335:108017, 10.1016/j.agee.2022.108017: síntese de carbono do solo.
- Poeplau & Don 2015, AGEE 200:33–41, 10.1016/j.agee.2014.10.024.
- Tamburini et al. 2020, Science Advances, 10.1126/sciadv.aba1715.
- Boddey et al. 2010, Global Change Biology, 10.1111/j.1365-2486.2009.02020.x: no Sul do Brasil, plantio direto com leguminosa acumulou 5–8 Mg C/ha a mais.
- Mudare et al. 2022, Agronomy for Sustainable Development 42, 10.1007/s13593-022-00816-1: meta-análise de consórcio milho/leguminosa na China e na África. A razão de área equivalente (LER) e as razões de equivalência de N e P ficam acima de 1; ganho de 0,90 t/ha na África.

---

## 2. Otimização e recomendação de rotação com dados e ML

### Artigos

**2.1 Dury, J. et al. (2012; online 2011).** *Models to support cropping plan and crop rotation decisions. A review.* Agronomy for Sustainable Development 32:567–580. https://doi.org/10.1007/s13593-011-0037-x [DOI✓ · snippet]
- Achado: revisão de mais de 120 referências. O plano de cultivo costuma ser modelado como decisão estática, quando na prática é um processo dinâmico e adaptativo.
- Uso: é o mapa de métodos (programação linear, regras, simulação). Justifica que o motor replaneje a cada safra conforme a previsão da quadra chuvosa.

**2.2 Detlefsen, N.K.; Jensen, A.L. (2007).** *Modelling optimal crop sequences using network flows.* Agricultural Systems 94:566–572. https://doi.org/10.1016/j.agsy.2007.02.002 [DOI✓ · snippet]
- Achado: formula a rotação ótima como fluxo em rede (nó = cultura/ano), o que permite algoritmos rápidos dentro de modelos de fazenda inteira.
- Uso: é a forma mais simples de implementar o otimizador. O grafo de sucessões tem arestas pesadas pelo efeito antecessor (Zhao 2022) e por risco.

**2.3 Schönhart, M.; Schmid, E.; Schneider, U.A. (2011).** *CropRota – A crop rotation model to support integrated land use assessments.* European Journal of Agronomy 34:263–277. https://doi.org/10.1016/j.eja.2011.02.004 [DOI✓ · snippet]
- Achado: gera rotações típicas a partir do uso do solo observado mais regras agronômicas. Foi validado com 7 anos de dados de 579 fazendas austríacas, segundo o working paper.
- Uso: é a receita para derivar a "estratégia atual" a partir do histórico (MapBiomas/PAM) e das regras de sucessão.

**2.4 Bachinger, J.; Zander, P. (2007).** *ROTOR, a tool for generating and evaluating crop rotations for organic farming systems.* European Journal of Agronomy 26:130–143. https://doi.org/10.1016/j.eja.2006.09.002 [DOI✓ · snippet]
- Achado: gerador de rotações de 3 a 8 anos baseado em regras, avaliando balanço de N, fitossanidade e plantas daninhas.
- Uso: é o modelo mais parecido com o nosso motor explicável: regras de intervalo mínimo entre hospedeiros, balanço de N e pontuação por critério.

**2.5 Sadok, W. et al. (2008).** *Ex ante assessment of the sustainability of alternative cropping systems: implications for using multi-criteria decision-aid methods. A review.* Agronomy for Sustainable Development 28:163–174. https://doi.org/10.1051/agro:2007043 [DOI✓ · só título e metadados; resumo não obtido]
- Achado: revisão de métodos de apoio à decisão multicritério para comparar sistemas de cultivo alternativos antes de adotá-los.
- Uso: fundamenta a pontuação ponderada pelas prioridades do agricultor (renda, risco, solo, trabalho) na comparação das 3 ou mais estratégias.

**2.6 Kallenberg, M.G.J. et al. (2023).** *Nitrogen management with reinforcement learning and crop growth models.* Environmental Data Science 2. https://doi.org/10.1017/eds.2023.28 [DOI✓ · resumo]
- Achado: CropGym, ambiente Gymnasium sobre modelos de cultura. O agente de aprendizado por reforço aprende doses semanais de N quase ótimas, competitivas com as de especialistas, e se mantém perto do ótimo sob mudança de clima quando a chuva é suficiente.
- Uso: mostra como acoplar aprendizado por reforço a um simulador. Fica como extensão futura; para o hackathon, o fluxo em rede ou a enumeração é mais auditável.

**2.7 Fenz, S. et al. (2023).** *AI- and data-driven crop rotation planning.* Computers and Electronics in Agriculture 212:108160. https://doi.org/10.1016/j.compag.2023.108160 [DOI✓ · snippet]
- Achado: um agente de aprendizado por reforço (DQN) gera sequências a partir de matrizes de aptidão de sucessão (da literatura e de NDVI), margem de contribuição e demanda de N. Especialistas julgaram a maioria das sequências realista.
- Uso: é o caso mais próximo do nosso produto. A ideia de usar NDVI para estimar a "aptidão de sucessão" é reaproveitável com MODIS/HLS no Ceará.

**2.8 Osman, J.; Inglada, J.; Dejoux, J.-F. (2015).** *Assessment of a Markov logic model of crop rotations for early crop mapping.* Computers and Electronics in Agriculture 113:234–243. https://doi.org/10.1016/j.compag.2015.02.015 [DOI✓ · snippet]
- Achado: com 3 a 5 anos de histórico de parcelas (LPIS, França), prevê a cultura do ano com acurácia de até cerca de 60%, antes de haver imagens.
- Uso: é a linha de base de "próxima cultura" por cadeia de Markov sobre o histórico.

**2.9 Zhang, C. et al. (2019).** *Machine-learned prediction of annual crop planting in the U.S. Corn Belt based on historical crop planting maps.* Computers and Electronics in Agriculture 166:104989. https://doi.org/10.1016/j.compag.2019.104989 [DOI✓ · snippet]
- Achado: uma rede neural sobre séries do CDL teve concordância esperada de 88% com o CDL futuro e R² acima de 0,9 com as estatísticas do NASS.
- Uso: é o modelo de referência para a parte global da demonstração (EUA/CDL) e para testar a portabilidade ao MapBiomas.

**2.10 Yaramasu, R.; Bandaru, V.; Pnvr, K. (2020).** *Pre-season crop type mapping using deep neural networks.* Computers and Electronics in Agriculture 176:105664. https://doi.org/10.1016/j.compag.2020.105664 [DOI✓ · snippet]
- Achado: um codificador Bi-ConvLSTM sobre o CDL de Nebraska chegou a OA 0,77 e kappa 0,57, contra 0,67 e 0,44 da cadeia de Markov (2018–2019).
- Uso: quantifica quanto o aprendizado profundo ganha sobre Markov, cerca de 10 pontos. Para o hackathon, Markov basta como baseline explicável.

**2.11 Dupuis, A.; Dadouchi, C.; Agard, B. (2023).** *Methodology for multi-temporal prediction of crop rotations using recurrent neural networks.* Smart Agricultural Technology 4:100152. https://doi.org/10.1016/j.atech.2022.100152 [DOI✓ · snippet]
- Achado: um Seq2Seq-LSTM com 6 anos de histórico prevê as 3 próximas culturas com mais de 81% (Recall@10) em Québec. Contexto econômico e meteorológico melhora a previsão. Há um artigo companheiro na mesma revista (4:100180, doi 10.1016/j.atech.2023.100180; DOI não conferido por nós).
- Uso: mostra como prever sequências inteiras, não só o próximo ano. Isso ajuda a projetar a "estratégia atual" para os próximos 3 anos.

**2.12 Arvor, D. et al. (2011).** *Classification of MODIS EVI time series for crop mapping in the state of Mato Grosso, Brazil.* International Journal of Remote Sensing 32(22):7847–7871. https://doi.org/10.1080/01431161.2010.531783 [DOI✓ · snippet]
- Achado: séries de EVI MODIS detectaram 95% da área agrícola e separaram soja, milho, algodão, soja-milho e soja-algodão, com OA de 74%. Cerca de 30% da área era de dupla safra.
- Uso: é o método para detectar número de ciclos e sucessão com NDVI/EVI no Brasil. Adaptar ao sequeiro do Ceará, com ciclo único em fevereiro–maio.

### Datasets

**D2. USDA Cropland Data Layer (CDL)** (USDA NASS)
- Contém: mais de 100 classes de cultura e cobertura.
- Resolução: 30 m de 2008 a 2023 e **10 m desde 2024**, com versão reamostrada para 30 m; anual. O CDL 2025 saiu em 27/02/2026.
- Acurácia das culturas em 2025: 75,4%, kappa 0,712.
- Cobertura: **só EUA** (nacional desde 2008; parcial de 1997 a 2007).
- Acesso: domínio público. Também no Google Earth Engine ("USDA/NASS/CDL").
- URL: https://www.nass.usda.gov/Research_and_Science/Cropland/SARS1a.php e https://nassgeodata.gmu.edu/CropScape/
- Referência: Boryan et al. 2011, Geocarto International 26(5):341–358, doi 10.1080/10106049.2011.562309.
- Uso: treinar e validar o preditor de próxima cultura na parte global da demonstração. O mesmo código roda depois sobre o MapBiomas.

**D3. USDA NASS Crop Sequence Boundaries (CSB)** (NASS + ERS)
- Contém: polígonos de talhão "totalmente sintéticos", gerados por algoritmo a partir do CDL. Cada polígono traz a cultura de cada um de 8 anos (CROP18…CROP25) e a área. Não são parcelas fundiárias.
- Resolução: vetor; janelas de 8 anos, de 2008–2015 até **2018–2025** (lançada em 27/03/2026).
- Cobertura: só EUA contíguos.
- Acesso: domínio público, em ZIP. Código em github.com/USDA-REE-NASS/crop-sequence-boundaries; também no GEE community catalog.
- URL: https://www.nass.usda.gov/Research_and_Science/Crop-Sequence-Boundaries/index.php
- Referências:
  - Hunt et al. 2024, Statistical Journal of the IAOS 40(2):237–246, doi 10.3233/SJI-230078;
  - Abernethy et al. 2023, Computers and Electronics in Agriculture 208:107768, doi 10.1016/j.compag.2023.107768, que usa o CSB na previsão pré-safra.
- Uso: fonte de sequências reais por talhão para estimar matrizes de transição de culturas e testar o recomendador fora do Brasil.

**D4. GCI30, intensidade de cultivo global a 30 m** (Zhang, M. et al.; Harvard Dataverse)
- Contém: número de ciclos por ano (1x, 2x), feito com Landsat, Sentinel-2 e MODIS.
- Resolução: 30 m; média de 2016 a 2018.
- Cobertura: global.
- Acesso: Dataverse, doi 10.7910/DVN/86M4PO; licença não confirmada.
- Referência: Zhang et al. 2021, ESSD 13:4799–4817, doi 10.5194/essd-13-4799-2021. A média global é 1,05 ciclo por ano, e 81,6% da área tem ciclo único. Há uma errata.
- Uso: classificar o pixel do Ceará como 1 ou 2 ciclos por ano, o que dá a estratégia atual e o potencial de safrinha irrigada.

**Leituras complementares (verificadas):**
- Klein Haneveld & Stegeman 2005, EJOR 166:406–429, 10.1016/j.ejor.2004.03.009: as sucessões proibidas entram como restrições lineares.
- Alfandari et al. 2015, EJOR 241:872–879, 10.1016/j.ejor.2014.09.066: o problema é fortemente NP-difícil; usa branch-price-and-cut.
- dos Santos et al. 2010, EJOR 204:639–647, 10.1016/j.ejor.2009.11.026; e Santos et al. 2015, EJOR 245:581–590, 10.1016/j.ejor.2015.03.035: geração de colunas para rotação de hortaliças.
- Sarker & Ray 2009, Computers and Electronics in Agriculture 68:191–199, 10.1016/j.compag.2009.06.002: algoritmo evolutivo multiobjetivo (NSGA-II) para o mix de culturas.
- Overweg et al. 2021, CropGym (arXiv:2104.04326).
- Gautron et al. 2022, gym-DSSAT (arXiv:2207.03270).
- Goldenits et al. 2024, preprint, 10.20944/preprints202410.2391.v1: Q-learning tabular explicável para rotação; não revisado por pares.
- Zhang, C. et al. **2022** (não 2019), Agricultural Systems 201:103462, 10.1016/j.agsy.2022.103462: "trusted pixels" do histórico do CDL.
- Quinton & Landrieu 2021, Remote Sensing 13:4599, 10.3390/rs13224599: modelar a rotação dá +6,6 mIoU.
- Wardlow, Egbert & Kastens 2007, RSE, 10.1016/j.rse.2006.11.021.
- Chen, Y. et al. 2018, JAG 69:133–147, 10.1016/j.jag.2018.03.005: padrões de cultivo no Mato Grosso com NDVI MODIS, OA de 73% para o padrão.
- Song et al. 2021, Nature Sustainability 4:784–792, 10.1038/s41893-021-00729-z: expansão da soja na América do Sul.

---

## 3. Queimadas e agricultura

### Artigos

**3.1 Aragão, L.E.O.C. et al. (2018).** *21st Century drought-related fires counteract the decline of Amazon deforestation carbon emissions.* Nature Communications 9:536. https://doi.org/10.1038/s41467-017-02771-y [DOI✓ · snippet]
- Achado: em anos de seca, os incêndios emitem 989 ± 504 Tg CO₂/ano, mais da metade das emissões do desmatamento. Em 2015 o fogo subiu 36% mesmo com o desmatamento 76% menor.
- Uso: fundamenta o acoplamento seca → fogo no módulo de risco. A seca é a variável-chave, não só o uso do fogo.

**3.2 Korontzi, S. et al. (2006).** *Global distribution of agricultural fires in croplands from 3 years of Moderate Resolution Imaging Spectroradiometer (MODIS) data.* Global Biogeochemical Cycles. https://doi.org/10.1029/2005GB002529 [DOI✓ · resumo]
- Achado: o fogo agrícola é 8–11% da atividade de fogo global (MODIS, 2001–2003), mas pesa muito mais em certas regiões. A sazonalidade é marcada.
- Uso: é a metodologia de base para separar focos em lavoura (máscara agrícola × FIRMS) e medir a dependência do fogo por estratégia.

**3.3 Franca Rocha, W.J.S. et al. (2024).** *Mapping Burned Area in the Caatinga Biome: Employing Deep Learning Techniques.* Fire 7(12):437. https://doi.org/10.3390/fire7120437 [DOI✓ · pág.]
- Achado: de 1985 a 2023 queimaram 10,9 Mha, ou 12,7% da Caatinga, cerca de 0,5 Mha/ano. O pico foi 2021, com 0,89 Mha. A maior parte foi em savana.
- Uso: é o artigo do mapeamento da Caatinga no MapBiomas Fogo; define a base de 30 m que usaremos.

**3.4 Argibay, D.S. et al. (2020).** *A long-term assessment of fire regimes in a Brazilian ecotone between seasonally dry tropical forests and savannah.* Ecological Indicators 113:106151. https://doi.org/10.1016/j.ecolind.2020.106151 [DOI✓ · pág.]
- Achado: na região de Capivara–Confusões (PI), 1999–2017, 48% da área queimou. Um ano chuvoso seguido de um ano seco gera grandes queimadas. A recorrência chega a 10 e é maior perto de estradas e assentamentos.
- Uso: dá duas variáveis prontas para o risco de fogo: "chuva do ano anterior menos chuva do ano atual" e distância a estradas e assentamentos.

**3.5 Silva, J.L. da et al. (2023).** *Spatio-temporal variability of fire occurrence and recurrence in the Caatinga Biome using MODIS sensor data* (título em português no Crossref). Ciência Florestal 33(1):e70195. https://doi.org/10.5902/1980509870195 [DOI✓ · snippet]
- Achado: com o MCD64A1 (2001–2018), o Piauí tem a maior ocorrência e a maior área queimada da Caatinga. Os picos são em setembro, agosto e outubro.
- Uso: é a validação regional do uso do MCD64A1 (produto NASA) na Caatinga. Confirma a janela de risco de fogo de agosto a outubro, logo após a colheita.

**3.6 de Oliveira, … et al. (2021).** *Environmental risk in Northeast Brazil: estimation of burning areas in Coreaú River Basin, Ceará, Brazil.* Environmental Monitoring and Assessment 193:444. https://doi.org/10.1007/s10661-021-09190-z [DOI✓ · pág.]
- Achado: na bacia do Coreaú (CE), de 2010 a 2017, houve 1.786 focos e 1.187,66 km² queimados (11,17% da bacia). Em Mucambo, a área queimada equivale a 40% do município.
- Uso: é um caso **cearense** que serve para validar o módulo de queimadas e escolher municípios da demonstração.

**3.7 Bezerra, K.F.S. et al. (2025).** *Fire and the Vulnerability of the Caatinga Biome to Droughts and Heatwaves.* Atmosphere 17(1):46. https://doi.org/10.3390/atmos17010046 [DOI✓ · resumo]
- Achado: estudo de 2012 a 2023 com a potência radiativa do fogo (FRP) do VIIRS, mais déficit de pressão de vapor (VPD) e temperatura do ERA5, SPI e ondas de calor.
  - O pico vai de agosto a novembro, sobretudo outubro.
  - O SPI antecede o pico de FRP em cerca de 4 meses.
  - O FRP se correlaciona com a frequência de ondas de calor (r = 0,62) e, negativamente, com o SPI (r = −0,69).
- Uso: entrega a especificação de um índice de risco de fogo com dados NASA (VIIRS) e de reanálise, com defasagem de 4 meses. Dá para alertar em junho sobre o risco de outubro.

**3.8 Salcedo, I.H. et al. (1997).** *Nutrient availability in soil samples from shifting cultivation sites in the semi-arid Caatinga of NE Brazil.* Agriculture, Ecosystems & Environment 65(2):177–186. https://doi.org/10.1016/S0167-8809(97)00073-X [DOI✓ · snippet]
- Achado: a queima libera nutrientes, mas após 5 anos de mandioca e abandono o P disponível e as bases caem. O P é o limitante principal.
- Uso: o "ganho" de fertilidade da roça queimada é temporário. Modelar decaimento da produtividade ao longo de ciclos sem pousio.

**3.9 Primo, A.A. et al. (2023).** *Slash and burn management and permanent or rotation agroforestry systems: A comparative study for C sequestration by century model simulation.* Journal of Environmental Management 336:117594. https://doi.org/10.1016/j.jenvman.2023.117594 [DOI✓ · resumo]
- Achado: experimento de longa duração no semiárido, em Sobral-CE segundo a notícia da Embrapa, simulado com o modelo Century.
  - O corte e queima sem pousio reduz o carbono do solo em cerca de 50% (cerca de 20 Mg/ha) em 10 anos.
  - A recuperação exige cerca de 50 anos de pousio.
  - Sistemas agroflorestais, permanentes ou em rotação, recuperam o estoque original em cerca de 10 anos.
- Uso: é **o** número para penalizar a estratégia "roça com queima" e valorizar a agrofloresta e o consórcio no simulador de carbono do solo.

**3.10 Cano-Crespo, A. et al. (2015).** *Forest edge burning in the Brazilian Amazon promoted by escaping fires from managed pastures.* JGR Biogeosciences 120:2095–2107. https://doi.org/10.1002/2015JG002914 [DOI✓ · snippet]
- Achado: o fogo que escapa de pastagens manejadas responde por até 52% das bordas florestais queimadas junto a pastagens, e por 22% junto a lavouras.
- Uso: justifica o risco de fuga do fogo para vizinhos e reservas. A queima tem custo de vizinhança, e o motor deve exibir esse risco.

**3.11 da Silva Arruda, V.L. et al. (2024).** *Assessing four decades of fire behavior dynamics in the Cerrado biome (1985 to 2022).* Fire Ecology 20. https://doi.org/10.1186/s42408-024-00298-4 [DOI✓ · resumo]
- Achado: 40% do Cerrado queimou entre 1985 e 2022, e 63% dessa área queimou mais de uma vez. O pico de fogo está ficando mais tardio e as manchas maiores. No MATOPIBA, a área queimada cresce com a expansão agrícola.
- Uso: mostra a relação entre expansão agrícola e fogo no MATOPIBA, onde entram o oeste baiano e o sul do Piauí e do Maranhão. Útil para generalizar a ferramenta além do Ceará.

### Datasets

**D5. MODIS MCD64A1 v6.1, área queimada** (NASA LP DAAC)
- Contém: área queimada, dia da queima e qualidade.
- Resolução: 500 m; mensal; de novembro de 2000 até hoje.
- Cobertura: global.
- Acesso: sem restrição de uso; doi 10.5067/MODIS/MCD64A1.061; no Earth Engine como `MODIS/061/MCD64A1`.
- URL: https://lpdaac.usgs.gov/documents/1006/MCD64_User_Guide_V61.pdf
- Referência: Giglio et al. 2018, RSE 217:72–85, doi 10.1016/j.rse.2018.08.005. A Coleção 6 detecta 26% mais área que a C5.1 e capta melhor queimadas pequenas.
- Uso: fração queimada por município e ano desde 2000, comparável no mundo todo. É a camada de fogo da versão global.

**D6. NASA FIRMS, focos ativos MODIS/VIIRS/Landsat** (NASA LANCE)
- Contém:
  - MODIS C6.1 a 1 km, desde 11/2000;
  - VIIRS S-NPP a 375 m, desde 20/01/2012; a página lida lista a série S-NPP até 02/11/2026;
  - VIIRS NOAA-20 desde 01/04/2018 e NOAA-21 desde 01/03/2023;
  - Landsat a 30 m, desde 20/06/2022.
- Resolução temporal: quase tempo real, com cerca de 3 h de latência.
- Cobertura: global.
- Acesso: Earthdata Login ou chave por e-mail; formatos SHP, CSV e JSON.
- URL: https://firms.modaps.eosdis.nasa.gov/download/
- Referência: Schroeder et al. 2014, RSE 143:85–96, doi 10.1016/j.rse.2013.12.008. Há artefatos ligados à Anomalia Magnética do Atlântico Sul, que fica sobre o Brasil.
- Uso: alerta de focos a menos de X km da propriedade e contagem de focos em área agrícola por estratégia.

**D7. INPE Programa Queimadas / BDQueimadas** (INPE)
- Contém: focos de calor de vários satélites. O "satélite de referência" (AQUA, passagem da tarde) mantém a série comparável entre anos.
- Resolução: cerca de 1 km; diário. O início é 1998 ou 2000, conforme a fonte.
- Cobertura: Brasil.
- Acesso: aberto (WFS, CSV e shapefile segundo snippet).
- URL: https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas/
- Uso: série oficial brasileira para relatórios. Serve para cruzar com o FIRMS e comunicar com órgãos locais.

**D8. MapBiomas Fogo, Coleção 5** (MapBiomas; IPAM; Geodatin na Caatinga)
- Contém: cicatrizes mensais e anuais, frequência, área acumulada, **ano do último fogo**, tamanho da cicatriz, área queimada por classe de uso e severidade (beta).
- Resolução: 30 m (Landsat); mensal e anual; de 1985 a 2025.
- Cobertura: Brasil.
- Acesso: gratuito; código aberto em https://github.com/mapbiomas-brazil/fire
- URL do documento técnico: https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2026/07/ATBD-MapBiomas-Fogo-Colecao-5.pdf
- Referência: Alencar et al. 2022, Remote Sensing 14:2510, doi 10.3390/rs14112510. Entre 1985 e 2020 queimaram 19,6% do Brasil, 83% entre julho e outubro.
- Uso: recorrência e "anos desde o último fogo" por pixel como variáveis de risco, mais o histórico de queima da própria fazenda.

**Leituras complementares (verificadas):**
- Sampaio et al. 1998, PAB 33(5):621–632: rebrota da Caatinga após corte e queima, de 94% sem queima a 10% com queima intensa. O DOI informado não resolve, então DOI não confirmado.
- Mamede & Araújo 2008, Journal of Arid Environments 72:458–470, 10.1016/j.jaridenv.2007.07.014: o corte e queima reduz o banco de sementes.
- Pivello 2011, Fire Ecology 7(1):24–39, 10.4996/fireecology.0701024.
- Valente & Laurini 2021, Cleaner Engineering and Technology 4:100255, 10.1016/j.clet.2021.100255: a lei paulista de fim da queima da cana reduziu os focos (processo de Cox).
- **Aguiar** et al. 2011 (não Rudorff como primeiro autor), Remote Sensing 3:2682–2703, 10.3390/rs3122682: monitoramento da colheita de cana sem queima.

---

## 4. Dispersão de pragas, percolação e conectividade

### Artigos

**4.1 Margosian, M.L. et al. (2009).** *Connectivity of the American Agricultural Landscape: Assessing the National Risk of Crop Pest and Disease Spread.* BioScience 59(2):141–151. https://doi.org/10.1525/bio.2009.59.2.7 [DOI✓ · pág. (PDF)]
- Achado: grafo com condados como nós e uma "resistência à transmissão" que depende da densidade do hospedeiro. Milho e soja são altamente conectados em escala nacional; trigo e algodão formam regiões discretas.
- **Correção:** o estudo usa a área plantada por condado do USDA NASS (2006), **não o CDL**. O termo "percolation" não aparece; o método é de limiares de conectividade.
- Uso: é o modelo-base do nosso módulo de "percolação de pragas", com o município do Ceará como nó, a área da PAM ou o MapBiomas como densidade do hospedeiro e o limiar de conectividade.

**4.2 Xing, Y. et al. (2020).** *Global Cropland Connectivity: A Risk Factor for Invasion and Saturation by Emerging Pathogens and Pests.* BioScience 70:744–758. https://doi.org/10.1093/biosci/biaa067 [DOI✓ · snippet]
- Achado: índice de risco por conectividade, com modelo gravitacional, para banana, mandioca, batata, batata-doce e inhame. Os nós "hub" e "ponte" são prioridades de vigilância.
- Uso: é a versão **global** (inclui mandioca) do índice de conectividade. Dá para rodar com CROPGRIDS ou SPAM no mundo todo.

**4.3 Bailey, D.J.; Otten, W.; Gilligan, C.A. (2000).** *Saprotrophic invasion by the soil-borne fungal plant pathogen Rhizoctonia solani and percolation thresholds.* New Phytologist 146(3):535–544. https://doi.org/10.1046/j.1469-8137.2000.00660.x [DOI✓ · snippet]
- Achado: a invasão do patógeno depende de distâncias previstas por um **limiar de percolação**, e não do alcance máximo do fungo.
- Uso: é a base teórica explícita de percolação. Justifica modelar a dispersão como transição de fase: acima de certa fração de hospedeiro conectado, a praga atravessa a paisagem.

**4.4 Rusch, A. et al. (2016).** *Agricultural landscape simplification reduces natural pest control: A quantitative synthesis.* Agriculture, Ecosystems & Environment 221:198–204. https://doi.org/10.1016/j.agee.2016.01.039 [DOI✓ · snippet]
- Achado: o controle biológico de pulgões foi 46% menor em paisagens homogêneas dominadas por lavoura.
- Uso: fornece o efeito da simplificação da paisagem: a fração de vegetação nativa (Caatinga) ao redor entra como fator protetor.

**4.5 Karp, D.S. et al. (2018).** *Crop pests and predators exhibit inconsistent responses to surrounding landscape composition.* PNAS 115(33):E7863–E7870. https://doi.org/10.1073/pnas.1800042115 [DOI✓ · snippet]
- Achado: 132 estudos e 6.759 sítios. Pragas e inimigos naturais respondem de forma inconsistente ao habitat não cultivado; a paisagem explica pouco.
- Uso: é o contraponto a Rusch. O fator "paisagem" entra com **peso pequeno e incerteza explícita**, para não vender certeza que a literatura não sustenta.

**4.6 Ratnadass, A. et al. (2011).** *Plant species diversity for sustainable management of crop pests and diseases in agroecosystems: a review.* Agronomy for Sustainable Development. https://doi.org/10.1007/s13593-011-0022-4 [DOI✓ · resumo]
- Achado: lista oito mecanismos pelos quais a diversidade vegetal reduz pragas e doenças, entre eles diluição de recurso, **ruptura do ciclo espacial** e **ruptura do ciclo temporal** (rotação), supressividade do solo e conservação de inimigos naturais.
- Uso: é a fundamentação formal de "rotação como quebra de ciclo". No motor, isso vira a contagem de meses consecutivos com hospedeiro da mesma praga.

**4.7 Sutherst, R.W.; Maywald, G.F. (1985).** *A computerised system for matching climates in ecology.* Agriculture, Ecosystems & Environment 13:281–299. https://doi.org/10.1016/0167-8809(85)90016-7 [DOI✓ · snippet]
- Achado: é o artigo de origem do CLIMEX. Combina índices de crescimento e de estresse num Índice Ecoclimático (EI).
- Uso: dá a estrutura do índice clima-praga (crescimento × estresses de frio, calor e seca), implementável com o POWER sem depender do software CLIMEX, cuja licença não foi confirmada.

**4.8 Early, R. et al. (2018).** *Forecasting the global extent of invasion of the cereal pest Spodoptera frugiperda, the fall armyworm.* NeoBiota 40:25–50. https://doi.org/10.3897/neobiota.40.28165 [DOI✓ · snippet]
- Achado: a temperatura mínima anual e a chuva da estação úmida limitam a lagarta-do-cartucho. Boa parte dos trópicos permite populações o ano todo.
- Uso: no semiárido sem inverno, a praga persiste o ano todo. A rotação com não hospedeiro (algodão, feijão, mandioca) ganha valor relativo.

**4.9 du Plessis, H. et al. (2020).** *The Effect of Temperature on the Development of Spodoptera frugiperda (Lepidoptera: Noctuidae).* Insects 11(4):228. https://doi.org/10.3390/insects11040228 [DOI✓ · resumo]
- Achado:
  - O ótimo de desenvolvimento fica entre 26 e 30 °C.
  - O limiar inferior é 13,01 °C para o ovo, 12,12 °C para a larva e 12,57 °C do ovo ao adulto.
  - São necessários 35,68 °D para o ovo, 204,60 °D para a larva e 150,54 °D para a pupa.
- Uso: são os parâmetros prontos para o modelo de graus-dia (gerações por ciclo de milho ou sorgo) com Tmax e Tmin do NASA POWER.

**4.10 Azambuja, R.; Degrande, P.E. (2014).** *Trinta anos do bicudo-do-algodoeiro no Brasil.* Arquivos do Instituto Biológico 81(4):377–410. https://doi.org/10.1590/1808-1657000012013 [DOI✓ · pág.]
- Achado:
  - O primeiro registro foi em fevereiro de 1983, em Campinas-SP. No Nordeste, julho de 1983 em Campina Grande/Ingá-PB, provavelmente uma segunda introdução.
  - Mesmo com controle, as perdas vão de 3% a 75%.
  - O controle cultural se apoia na destruição de soqueiras e no plantio uniforme.
  - O artigo não traz números de área do Nordeste.
- Uso: é a base histórica do caso "bicudo" e da regra de **vazio sanitário** e destruição de restos no motor quando a estratégia inclui algodão.

**4.11 Pereira, F.P.; Diniz, A.J.F.; Parra, J.R.P. (2023).** *Fertility Life Table, Thermal Requirements, and Ecological Zoning of Anthonomus grandis grandis Boheman (Coleoptera: Curculionidae) in Brazil.* Insects 14:582. https://doi.org/10.3390/insects14070582 [DOI✓ · snippet]
- Achado: o ciclo dura 16,1 dias a 32 °C e 46,2 dias a 18 °C. A reprodução (R0) é máxima entre 25 e 28 °C. O zoneamento inclui parte do Nordeste.
- Uso: parâmetros térmicos do bicudo para estimar gerações por safra no Ceará, que é quente o ano todo e por isso de alto risco, e comparar estratégias com e sem algodão.

**4.12 Levine, E. et al. (2002).** *Adaptation of the Western Corn Rootworm to Crop Rotation: Evolution of a New Strain in Response to a Management Practice.* American Entomologist 48:94–107. https://doi.org/10.1093/ae/48.2.94 [DOI✓ · snippet]
- Achado: surgiu uma variante da larva-alfinete que põe ovos na soja, o que tornou ineficaz a rotação milho-soja de dois anos.
- Uso: é o exemplo-chave de **risco** na seção de lacunas e riscos. Rotações curtas e repetitivas podem selecionar pragas adaptadas, então o motor deve preferir sequências variadas.

### Datasets

**D9. EPPO Global Database** (EPPO)
- Contém: pragas, distribuição por país, hospedeiros e categorização regulatória; atualização contínua.
- Cobertura: global.
- Acesso: web gratuita; API REST e download em SQLite via data.eppo.int, com registro gratuito e "Open Data Licence".
- URL: https://gd.eppo.int
- Uso: tabela praga → hospedeiros, que define quais culturas "conectam" a mesma praga no grafo de percolação e na regra de quebra de ciclo.

**D10. GBIF** (Global Biodiversity Information Facility)
- Contém: registros de ocorrência georreferenciados, inclusive de pragas como *S. frugiperda* e *A. grandis*.
- Resolução: pontos com data.
- Cobertura: global.
- Acesso: API e downloads com DOI. A licença varia por dataset: CC0, CC BY 4.0 ou CC BY-NC 4.0.
- URL: https://www.gbif.org
- Uso: pontos de presença para calibrar ou validar o índice clima-praga (tipo CLIMEX ou MaxEnt) no mundo todo.

**D11. FAO FAMEWS, monitoramento da lagarta-do-cartucho** (FAO)
- Contém: app e plataforma com vistorias de campo e armadilhas de feromônio validadas por pontos focais nacionais. Mapas quase em tempo real alimentam o FAWRisk (admin-2, África).
- Cobertura: começou na África em 2018 e se expandiu; não confirmamos se cobre o Brasil.
- Acesso: livre pelo mapa da FAO.
- URL: https://www.fao.org/fall-armyworm/monitoring-tools/en (a página da plataforma deu 404 no momento da consulta).
- Uso: modelo de protocolo de monitoramento participativo. A ferramenta pode imitá-lo deixando o agricultor reportar pragas.

**Leituras e datasets complementares (verificados):**
- Sutrave et al. 2012, PLoS ONE, 10.1371/journal.pone.0037793: rede de condados da ferrugem asiática da soja.
- Plantegenest et al. 2007, J. R. Soc. Interface 4:963–972, 10.1098/rsif.2007.1114: epidemiologia de paisagem.
- Gilligan & van den Bosch 2008, Annual Review of Phytopathology 46:385–418, 10.1146/annurev.phyto.45.062806.094357.
- Skelsey et al. 2010, Phytopathology 100:1146–1161, 10.1094/PHYTO-06-09-0148, *Invasion of Phytophthora infestans at the Landscape Level…*: agrupar lavouras aumentou a doença.
- Mundt 2002, Annual Review of Phytopathology 40:381–410, 10.1146/annurev.phyto.40.011402.113723.
- Meehan et al. 2011, PNAS 108:11500–11505, 10.1073/pnas.1100751108.
- Jaworski et al. 2023, Agriculture Communications, 10.1016/j.agrcom.2023.100004.
- Kenis et al. 2022, Entomologia Generalis, 10.1127/entomologia/2022/1659: revisão da lagarta-do-cartucho.
- Zacarias 2020, Climatic Change 161:555–566, 10.1007/s10584-020-02722-5.
- Jin et al. 2022, Agriculture 12:1759, 10.3390/agriculture12111759: MaxEnt do bicudo.
- Gray et al. 2009, Annual Review of Entomology 54:303–321, 10.1146/annurev.ento.54.110807.090434.
- Kriticos et al. 2015, manual do CLIMEX v4 (CSIRO, sem DOI).
- Kriticos et al. 2020, Scientific Reports 10:22049, 10.1038/s41598-020-79149-6: *Bemisia* e mandioca na África Oriental.
- Akrivou et al. 2021, PLOS ONE, 10.1371/journal.pone.0261626, e da Silva, N.R. et al. 2024, Plants 13:535, 10.3390/plants13040535: mosca-negra-dos-citros.
- Datasets: CABI Compendium (cerca de 2.500 fichas; URL oficial não confirmada); AGROFIT/MAPA (via Embrapa AgroAPI); PlantVillage (54.306 imagens de laboratório; Mohanty et al. 2016, 10.3389/fpls.2016.01419).

---

## 5. Datasets de referência: qual cultura combina com qual solo e clima

### Artigos

**5.1 Ramírez-Villegas, J. et al. (2013; online 2011).** *Empirical approaches for assessing impacts of climate change on agriculture: The EcoCrop model and a case study with grain sorghum.* Agricultural and Forest Meteorology 170:67–78. https://doi.org/10.1016/j.agrformet.2011.09.005 [DOI✓ · resumo]
- Achado: integra os parâmetros do FAO-ECOCROP a um modelo mecanístico simples, com calibração e avaliação. Para sorgo, teve taxa de verdadeiro positivo de pelo menos 0,967 e falso negativo de no máximo 0,026 contra estatísticas nacionais e subnacionais.
- Uso: é o método validado para transformar as faixas do ECOCROP (Tmin, Tótima, chuva etc.) numa nota de aptidão de 0 a 1, aplicável no mundo todo. O sorgo é uma cultura do semiárido.

Os artigos de referência de cada dataset vêm dentro de cada item.

### Datasets

**D12. FAO ECOCROP** (FAO, Divisão de Terras e Águas)
- Contém, por espécie: temperatura e chuva ótimas e absolutas; pH; luz; zona de Köppen; fotoperíodo; latitude e altitude; profundidade, textura, fertilidade, salinidade e drenagem do solo; ciclo em dias; usos.
- Número de espécies: a página fala em "mais de 2.568".
- Resolução: não espacial; estático. Descontinuado por volta de 2015; segundo a FAO, o acesso agora é "pelo GAEZ".
- Cobertura: global.
- Acesso: CC BY 4.0 pelo catálogo da FAO. O formulário oficial ainda está no ar, mas não há download em arquivo.
- URLs: https://ecocrop.apps.fao.org/ecocrop/srv/en/cropSearchForm e https://data.apps.fao.org/catalog/dataset/ecocrop
- Cópias:
  - pacote R **Recocrop** (CRAN v0.4-2, 2025, GPL≥3), com 1.710 táxons derivados do antigo site;
  - **OpenCLIM/ecocrop** no GitHub, com o `EcoCrop_DB.csv` completo (Open Government Licence v3; Zenodo 10.5281/zenodo.10843625).
- Referência: Hackett 1991, Agroforestry Systems 14:131–143, 10.1007/BF00045728.
- Uso: **a tabela central** de exigências por cultura do motor global. Para o Ceará, inclui feijão-caupi, sorgo, mandioca, palma e caju.

**D13. FAO GAEZ v4 e v5** (FAO + IIASA)
- Contém:
  - **v4 (2021):** 51 culturas, sequeiro e irrigado, dois níveis de manejo; adequação, rendimento atingível, rendimento real e gaps. Resolução de 5 arc-min (cerca de 9 km). Série histórica de 1961 a 2010 e 4 cenários RCP.
  - **v5 (lançado em 14/04/2025):** adequação, rendimento atingível e potencial, rendimento real em 2020 e gaps. Inclui **caju**, gergelim, manga e melancia, entre outras. Bases de 1981–2000 e 2001–2020 (AgERA5). Cenários futuros CMIP6 (SSP1-2.6, SSP3-7.0, SSP5-8.5).
- Resolução: na v5, as fontes divergem: a página fala em 30 arc-seg (cerca de 1 km) e o wiki em 5 arc-min.
- Cobertura: global.
- Acesso: licença por camada. Adequação e rendimento atingível são **CC BY-NC-SA 4.0**; gaps, rendimentos reais e potencial são CC BY 4.0 (v5).
- URLs: https://www.fao.org/gaez/gaezv4/en, https://data.apps.fao.org/gaez/?lang=en e documentação em https://github.com/un-fao/gaezv5/wiki
- Referência: Fischer et al. 2021, doi 10.4060/cb4744en.
- Uso: rendimento atingível por pixel, para checar o resultado do ECOCROP e projetar mudança climática. Atenção à licença NC se o produto for comercial.

**D14. FAO-56, Kc e duração de estágios** (FAO)
- Contém:
  - ETo de Penman-Monteith;
  - Tabela 11, com a duração dos estágios por cultura, época e região;
  - Tabela 12, com Kc inicial, médio e final e altura máxima;
  - Kc dual no capítulo 7.
- Ressalva: os Kc tabelados valem para umidade relativa mínima de cerca de 45% e vento de 2 m/s. **No semiárido, ajustar o Kc médio e final** pelas equações 62 e 65.
- Cobertura: global.
- Acesso: livre; licença não confirmada.
- URL: https://www.fao.org/3/X0490E/x0490e00.htm
- Referência: Allen, Pereira, Raes & Smith 1998, FAO Irrigation and Drainage Paper 56, ISBN 92-5-104219-5.
- Uso: balanço hídrico por cultura (ETc = Kc × ETo, com ETo do POWER) para estimar estresse hídrico e o índice de satisfação de necessidade de água (ISNA), no estilo do ZARC.

**D15. SAGE Crop Calendar** (Sacks et al., UW-Madison)
- Contém: datas de plantio e colheita e duração de 19 culturas.
- Resolução: 5 arc-min e 0,5°; climatologia estática.
- Cobertura: global.
- Acesso: download livre, sem licença formal.
- URL: https://sage.nelson.wisc.edu/data-and-models/datasets/crop-calendar-dataset
- Referência: Sacks et al. 2010, Global Ecology and Biogeography 19(5):607–620, 10.1111/j.1466-8238.2010.00551.x.
- Uso: calendário padrão fora do Brasil (no Brasil, usar ZARC e CONAB).

**D16. MIRCA2000 e MIRCA-OS** (Goethe-Univ. Frankfurt; Kebede et al.)
- Contém:
  - **MIRCA2000:** áreas mensais irrigadas e de sequeiro de 26 classes, por volta de 2000.
  - **MIRCA-OS:** 23 classes, irrigado e sequeiro, com calendário de plantio e maturidade e áreas mensais para 2000, 2005, 2010 e 2015. A v2, de março de 2026, inclui 2020.
- Resolução: 5 arc-min.
- Cobertura: global.
- Acesso: dados em CC BY 4.0.
- URLs: https://zenodo.org/record/7422506 (MIRCA2000) e https://www.hydroshare.org/resource/e4582ca0042148338bb5e0148b749ed6/ (MIRCA-OS)
- Referências: Portmann et al. 2010, GBC, 10.1029/2008GB003435; Kebede et al. 2025, Scientific Data 12:208, 10.1038/s41597-024-04313-w.
- Uso: saber quando cada cultura ocupa o solo, para montar sucessões viáveis no ano (safra e safrinha) no mundo todo.

**D17. GGCMI Phase 3, calendário de culturas** (Jägermeyr et al.)
- Contém: dias de plantio e maturidade de 18 culturas, sequeiro e irrigado separados.
- Resolução: 0,5°; estático.
- Cobertura: global.
- Acesso: CC BY 4.0.
- URL: https://zenodo.org/record/5062513
- Referência: Jägermeyr et al. 2021, Nature Food 2:873–885, 10.1038/s43016-021-00400-y.
- Uso: calendário harmonizado com os modelos de cultura globais. Útil se usarmos DSSAT ou APSIM com o POWER.

**D18. MapSPAM (SPAM 2020 v2.0)** (IFPRI; Land & Carbon Lab)
- Contém: área física e colhida, rendimento e produção de 46 culturas ou grupos, sequeiro e irrigado.
- Resolução: 5 arc-min (cerca de 10 km); média de 2019 a 2021. Há versões de 2000, 2005 e 2010.
- Cobertura: global.
- Acesso: Dataverse, CC BY 4.0 (termos do IFPRI). DOI do SPAM 2020: 10.7910/DVN/SWPENT.
- Referência do SPAM2010: Yu et al. 2020, ESSD 12:3545–3572, 10.5194/essd-12-3545-2020.
- Uso: "o que já se planta aqui" em qualquer lugar do mundo e densidade de hospedeiro para o módulo de pragas.

**D19. CROPGRIDS** (Tang et al.; Univ. Sydney e FAO)
- Contém: área colhida e física de **173 culturas**, com camada de qualidade.
- Resolução: 0,05° (cerca de 5,6 km); por volta de 2020.
- Cobertura: global.
- Acesso: CC BY 4.0, doi 10.6084/m9.figshare.22491997.
- Referência: Tang et al. 2024, Scientific Data 11:413, 10.1038/s41597-024-03247-7.
- Uso: cobre culturas menores que o SPAM não tem, como palma e caju. É a melhor fonte global de densidade de hospedeiro.

**D20. GDHY, produtividade histórica global** (Iizumi, NARO)
- Contém: rendimento anual de milho, arroz, trigo e soja; milho e arroz com safra principal e secundária.
- Resolução: 0,5°; anual de 1981 a 2016.
- Cobertura: global.
- Acesso: CC BY 4.0.
- URL: https://doi.pangaea.de/10.1594/PANGAEA.909132
- Referência: Iizumi & Sakai 2020, Scientific Data 7:97, 10.1038/s41597-020-0433-7.
- Uso: anomalias de produtividade × índices de seca (SMAP, IMERG, ESI) fora do Brasil. Não cobre feijão nem mandioca.

**D21. SoilGrids 2.0** (ISRIC)
- Contém: pH, carbono orgânico, densidade, fração grossa, areia, silte, argila, CTC, N total e estoque de carbono, em 6 intervalos de profundidade.
- Resolução: 250 m; estático.
- Cobertura: global.
- Acesso: CC BY 4.0. **A API REST está pausada, sem prazo**; usar WCS ou download de arquivos.
- URL: https://www.isric.org/explore/soilgrids
- Referências: Poggio et al. 2021, SOIL 7:217–240, 10.5194/soil-7-217-2021; Hengl et al. 2017, PLOS ONE, 10.1371/journal.pone.0169748.
- Uso: pH, textura e carbono do solo por pixel para a aptidão (ECOCROP) e a linha de base de carbono fora do Brasil.

**D22. HWSD v2 (v2.0, v2.01 e v2.2)** (FAO + IIASA)
- Contém: classes WRB/FAO-90 em 7 camadas até 200 cm, com CTC, N, C/N, saturação por Al, textura, densidade, **profundidade enraizável** e **água disponível**.
- Resolução: 30 arc-seg (cerca de 1 km).
- Cobertura: global.
- Acesso: v2.0 e v2.01 são CC BY-NC-SA; **a v2.2 é CC BY 4.0**.
- URL: https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/harmonized-world-soil-database-v20/en/
- Referência: FAO & IIASA 2023, 10.4060/cc3823en.
- Uso: água disponível e profundidade de raiz para o balanço hídrico FAO-56. É o dado que falta no SoilGrids para o risco de veranico.

**D23. Crop Recommendation Dataset (Kaggle, usuário atharvaingle)**
- Contém: 2.200 linhas por 8 colunas (N, P, K, temperatura, umidade, pH, chuva e rótulo), com 22 culturas.
- Origem declarada, na íntegra: "build by augmenting datasets of rainfall, climate and fertilizer data available for India". Não cita fonte nem método.
- Resolução e cobertura: sem coordenadas, sem data e sem local.
- Acesso: Apache-2.0; criado em 19/12/2020.
- URL: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
- **Avaliação crítica** (o CSV foi baixado e analisado):
  - exatamente 100 linhas por classe;
  - N, P e K inteiros, sem unidade, em faixas fechadas e redondas por cultura; maçã e uva têm faixas idênticas;
  - distribuição quase uniforme dentro de cada classe (o teste KS não rejeita a uniforme), o que é a assinatura de sorteio dentro de faixas de especialista, não de medição;
  - chuva de 20 a 299 mm **sem período**;
  - umidade de 14–20% para grão-de-bico;
  - um Random Forest em validação cruzada acerta **99,45%**, o que mostra separação trivial.
  - Não encontramos crítica publicada.
- Uso: **não usar como evidência.** No máximo serve como dado de brinquedo para demonstrar a interface, sempre com aviso explícito.

**D24. ESA WorldCereal** (ESA/VITO)
- Contém: culturas temporárias, milho (1ª e 2ª safra), cereais de inverno e de primavera, lavoura ativa e irrigação ativa, com confiança.
- Resolução: 10 m; ano de 2021 (v100).
- Cobertura: global.
- Acesso: CC BY 4.0, doi 10.5281/zenodo.7875105.
- Referência: Van Tricht et al. 2023, ESSD 15:5491–5515, 10.5194/essd-15-5491-2023.
- Uso: máscara global de lavoura e milho a 10 m, que substitui o CDL fora dos EUA na versão mundial.

**Datasets complementares (verificados):**
- WoSIS: perfis de solo, cerca de 228 mil em 174 países; doi 10.17027/isric-wdcsoils-20231130; licença por perfil.
- EarthStat: Monfreda et al. 2008, 175 culturas por volta de 2000; licença não confirmada.
- FAO Crop Calendar (https://cropcalendar.apps.fao.org/) e GIEWS Crop Calendar.
- GEOGLAM Crop Monitor (https://www.cropmonitor.org/, "todos os direitos reservados").
- GYGA, renomeado YPYGA (https://yieldgap.com, CC BY-NC-SA).
- FAOSTAT QCL (CC BY 4.0).
- CHIRPS (0,05°, 50°S–50°N, domínio público; a **v3 já existe e a v2 encerra após dezembro de 2026**).
- AgERA5 (0,1°, diário desde 1979, CC-BY; é a base do GAEZ v5).
- ERA5-Land (0,1°, horário desde 1950).
- WaPOR (o nível L1 a 300 m é global).
- WorldClim 2.1.
- Global Aridity Index e ET0 **v3.1** (a v3.0 foi descontinuada por erro na radiação de onda longa; doi 10.6084/m9.figshare.7504448).
- ESA CCI Soil Moisture.

---

## 6. Brasil, Nordeste e Ceará

### Artigos

**6.1 Nobre, P.; Shukla, J. (1996).** *Variations of Sea Surface Temperature, Wind Stress, and Rainfall over the Tropical Atlantic and South America.* Journal of Climate 9(10):2464–2479. https://doi.org/10.1175/1520-0442(1996)009<2464:VOSSTW>2.0.CO;2 [DOI✓ · pág.]
- Achado: o modo interanual dominante do Atlântico tropical é um padrão de TSM e vento assimétrico em relação ao equador, o "dipolo" ou gradiente. Ele condiciona a posição da Zona de Convergência Intertropical (ZCIT) e a chuva de março a maio no norte do Nordeste.
- Uso: justifica usar o gradiente de TSM do Atlântico (norte menos sul) como variável do cenário sazonal, junto com o Niño 3.4.

**6.2 Kayano, M.T.; Andreoli, R.V. (2006).** *Relationships between rainfall anomalies over northeastern Brazil and the El Niño–Southern Oscillation.* Journal of Geophysical Research 111:D13101. https://doi.org/10.1029/2005JD006142 [DOI✓ · snippet]
- Achado: uma previsão baseada só no ENSO acertaria o clima do Nordeste em apenas 36% das vezes; o Atlântico também pesa.
- Uso: é a métrica-alerta para a interface. Não comunicar "El Niño = seca" como certeza; mostrar a probabilidade condicionada a ENSO **e** Atlântico.

**6.3 Rocha Júnior, R.L. da et al. (2021).** *An Empirical Seasonal Rainfall Forecasting Model for the Northeast Region of Brazil.* Water 13(12):1613. https://doi.org/10.3390/w13121613 [DOI✓ · resumo]
- Achado: um modelo empírico com funções ortogonais empíricas (EOF) da chuva de fevereiro a abril, comparado ao conjunto norte-americano de modelos (NMME). Os três primeiros modos explicam a maior parte da variabilidade e se ligam a anomalias de TSM do Pacífico e do Atlântico tropical.
- Uso: é uma receita simples de previsão sazonal (EOF mais teleconexões) para gerar cenários de quadra chuvosa no motor, se não houver acesso ao produto da FUNCEME.

**6.4 Marengo, J.A. et al. (2018).** *Climatic characteristics of the 2010-2016 drought in the semiarid Northeast Brazil region.* Anais da Academia Brasileira de Ciências 90(2):1973–1985. https://doi.org/10.1590/0001-3765201720170206 [DOI✓ · pág.]
- Achado: 16 dos 25 anos entre meados da década de 1990 e 2016 tiveram chuva abaixo do normal. Algumas secas vêm do El Niño, outras do Atlântico Norte tropical quente.
- Uso: define 2012–2016 como o caso de estresse para a demonstração ("como cada estratégia teria se saído na seca de 2012–2016").

**6.5 Marengo, J.A. et al. (2021).** *Drought in Northeast Brazil: A review of agricultural and policy adaptation options for food security.* Climate Resilience and Sustainability. https://doi.org/10.1002/cli2.17 [DOI✓ · resumo]
- Achado: revisa as estratégias de adaptação à seca no semiárido (manejo e conservação do solo, gestão da água, previsão sazonal, crédito e transferências). Muitas ações são pós-desastre e geram dependência; experiências como o AdaptaSertão mostram potencial.
- Uso: enquadra o produto como ferramenta de **adaptação ex ante**, que é a lacuna apontada, e não de resposta pós-seca.

**6.6 Rocha, R.L. et al. (2021).** *Indicadores de Veranicos e de Distribuição de Chuva no Ceará e os Impactos na Agricultura de Sequeiro.* Revista Brasileira de Meteorologia 36(3):579–589. https://doi.org/10.1590/0102-77863630041 [DOI✓ · pág.]
- Achado: estudo da FUNCEME com chuva diária de fevereiro a maio (1980–2018) e rendimento de milho e feijão da tabela SIDRA 1612. Mais veranicos significam mais perda; chuva bem distribuída significa menos perda. Milho e feijão ocupam 91% da área cultivada do Ceará. Veranico foi definido como 3 ou mais dias com até 2 mm.
- Uso: dá a **definição operacional de veranico** e a validação local. O IMERG diário vai calcular os veranicos por município e estratégia.

**6.7 MAPA/Embrapa: capítulo "Zoneamento Agrícola de Risco Climático (ZARC)"** (por volta de 2021; ano inferido do arquivo). Em *Estratégias de adaptação às mudanças do clima dos sistemas agropecuários brasileiros*, p. 102–103. https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1136438/1/PL-ZARC-2021.pdf [pág.; sem DOI]
- Achado: o ZARC existe desde 1996, baseia-se no ISNA e na frequência de eventos adversos, e é usado no Proagro, no PSR e no crédito. A economia estimada é de cerca de R$ 1 bilhão por ano.
- Uso: o motor deve **respeitar o ZARC** (janela e risco), porque plantar fora dele custa seguro e crédito ao agricultor. É também a referência metodológica do nosso balanço hídrico.

**6.8 Santos, … et al. (2026).** *Water deficit limits growth and yield of cowpea cultivars.* Revista Caatinga 39. https://doi.org/10.1590/1983-21252026v3914137rc [DOI✓ · pág.]
- Achado: em Teresina (Embrapa Meio-Norte), com lâminas de 133,8 a 357 mm, a produtividade máxima foi de 1.582,55 kg/ha para BRS Inhuma (com 311 mm) e 1.334,49 kg/ha para BRS Olho Negro (com 332 mm). A Olho Negro foi a mais tolerante.
- Uso: dá a curva de resposta à água do feijão-caupi para calibrar o rendimento esperado por cenário de chuva.

**6.9 Souza, L.S.B. et al. (2011).** *Eficiência do uso da água das culturas do milho e do feijão-caupi sob sistemas de plantio exclusivo e consorciado no semiárido brasileiro.* Bragantia 70(3):715–721. https://doi.org/10.1590/S0006-87052011000300030 [DOI✓ · pág.]
- Achado: em Petrolina-PE, o consórcio milho e caupi rendeu menos grãos por cultura que o plantio exclusivo, mas foi economicamente mais vantajoso em todos os tratamentos de irrigação.
- Uso: dá suporte à estratégia "consórcio milho + caupi" com métrica econômica, não só de produtividade.

**6.10 Diniz, W.J.S. et al. (2017).** *Forage cactus-sorghum intercropping at different irrigation water depths in the Brazilian Semiarid Region.* Pesquisa Agropecuária Brasileira. https://doi.org/10.1590/S0100-204X2017000900004 [DOI✓ · resumo]
- Achado: em Serra Talhada-PE, o consórcio palma e sorgo teve índice de produtividade do sistema de 6.279 kg MS/ha, contra 4.627 kg/ha da palma solteira, com mais estabilidade e alta compatibilidade.
- Uso: é a estratégia forrageira (palma + sorgo) para propriedades com pecuária. Entra como uma das alternativas comparadas.

**6.11 Carvalho, L.M. de et al. (2016).** *Productivity and drought tolerance of cassava cultivars in the Coastal Tablelands of Northeastern Brazil.* Ciência Rural. https://doi.org/10.1590/0103-8478cr20151035 [DOI✓ · resumo]
- Achado: 'Irará', 'BRS Tapioqueira', 'BRS Kiriris' e 'BRS Caipira' foram as mais adaptadas. A 'BRS Caipira' recuperou a clorofila mais rápido após a seca.
- Uso: parâmetros de cultivar de mandioca para o Nordeste. A mandioca entra como cultura "tampão" contra seca nas rotações.

**6.12 Bezerra, M.A. et al. (2007).** *Physiology of cashew plants grown under adverse conditions.* Brazilian Journal of Plant Physiology. https://doi.org/10.1590/S1677-04202007000400012 [DOI✓ · resumo]
- Achado: revisão da ecofisiologia do cajueiro, importante no semiárido nordestino, com ênfase em estresse hídrico e salino, nutrição e trocas gasosas.
- Uso: o caju é perene e entra como componente fixo (agrofloresta ou consórcio) e não como cultura de rotação anual. Esta é a referência para as suas exigências.

**6.13 Silva, … et al. (2009).** *Produtividade do algodoeiro BRS Safira em sistemas agroecológicos no semiárido.* Anais do 7º Congresso Brasileiro do Algodão (Embrapa Algodão). https://www.alice.cnptia.embrapa.br/handle/doc/512459 [pág.; sem DOI]
- Achado: em sequeiro em Remígio-PB, os consórcios algodão + feijão-macassar + milho e amendoim + algodão + gergelim não reduziram a produtividade do algodão, que ficou acima de 1.000 kg/ha. O preço orgânico chega a 100% acima do convencional.
- Uso: é a estratégia "algodão agroecológico consorciado". Confronta-se com o risco do bicudo (seção 4) e com o prêmio de preço.

### Datasets

**D25. ZARC: Tábua de Risco (dados abertos) e Painel de Indicação de Riscos** (MAPA)
- Contém: períodos de plantio indicados por **município × cultura × tipo de solo × ciclo × decêndio (1–36)**, com o número da portaria. O painel mostra o menor risco do município, com cores verde (20%), amarelo (30%) e vermelho (40%).
- Resolução: municipal; decendial. CSVs por safra de 2016/17 a 2026/27.
- Cobertura: Brasil.
- Acesso: **CC BY**, com atualização semanal; o painel é público, sem login.
- URLs:
  - https://dados.agricultura.gov.br/dataset/tabua-de-risco-zoneamento-agricola-de-risco-climatico
  - https://mapa-indicadores.agricultura.gov.br/publico/extensions/Zarc/Zarc.html
  - portarias: https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-risco-climatico/portarias
- Ressalva: os níveis 20/30/40%, o modelo de balanço hídrico (SARRA) e as classes de água disponível (AD1–AD6) foram confirmados só por snippet.
- Uso: **restrição dura** de janela de plantio no Ceará e validação do nosso balanço hídrico (o risco calculado por nós deve bater com o do ZARC).

**D26. FUNCEME: Calendário de Chuvas e prognóstico da quadra chuvosa** (FUNCEME)
- Contém:
  - chuva diária por posto e município, com cerca de 527 postos operados por voluntários e série desde 1972 (segundo o jornal O Povo, 2024);
  - prognóstico em tercis (abaixo, em torno e acima da normal), com modelos combinados com INMET e CPTEC desde 2013. A categoria mais provável se confirmou em 11 de 13 anos (Diário do Nordeste, 23/01/2026).
- Cobertura: Ceará.
- Acesso: licença e formato de download não confirmados; o site principal deu erro de certificado no momento da consulta.
- URL: https://chuvas.funceme.br/
- Uso: verdade de campo para corrigir o viés do IMERG no Ceará e cenário sazonal oficial para ponderar os anos simulados.

**D27. IBGE: Produção Agrícola Municipal (PAM/SIDRA)** (IBGE)
- Contém: área plantada e colhida, produção, rendimento e valor de 64 produtos, desde 1974. A tabela 1612 traz as lavouras temporárias e a 5457 as temporárias e permanentes.
- Resolução: municipal; anual.
- Cobertura: Brasil.
- Acesso: aberto pelo SIDRA e pela API.
- URLs: https://sidra.ibge.gov.br/tabela/1612 e https://sidra.ibge.gov.br/tabela/5457
- Uso: rendimento municipal histórico de milho, feijão, mandioca, sorgo, algodão e caju no Ceará, para calibrar o efeito da seca e validar o motor. É também a "densidade de hospedeiro" por município no módulo de pragas, como em Margosian.

**D28. CONAB: Calendário de Plantio e Colheita de Grãos no Brasil** (CONAB)
- Contém: meses de plantio e colheita por cultura e UF; edições de 2020 e 2022.
- Cobertura: Brasil.
- Acesso: reprodução permitida com citação.
- URL: antigo.conab.gov.br/outras-publicacoes/item/download/45710_77f0a5ee35e765e2248999f4c61e70c8 (visto só em snippet; o PDF falhou por erro de certificado).
- Uso: calendário por UF quando a cultura não tem ZARC no município.

**D29. MapBiomas: Cobertura e Uso da Terra, Coleções 10 e 11** (MapBiomas)
- Contém: classes anuais de uso, com códigos:

  | Classe | Código |
  |---|---|
  | Soja | 39 |
  | Cana | 20 |
  | Arroz | 40 |
  | Algodão (beta) | 62 |
  | Outras lavouras temporárias | 41 |
  | Café | 46 |
  | Citrus | 47 |
  | Mosaico de usos | 21 |
  | Pastagem | 15 |

- Resolução: 30 m; anual. A Coleção 10 cobre 1985–2024. A **Coleção 11** saiu em 12/08/2026, cobre 1985–2025 e tem 33 classes.
- Cobertura: Brasil.
- Acesso: CC BY 4.0 no Earth Engine (`projects/mapbiomas-public/assets/brazil/lulc/v1`); o FAQ do MapBiomas fala em CC BY-SA.
- Referência: Souza Jr. et al. 2020, Remote Sensing 12:2735, 10.3390/rs12172735, com exatidão média de 89%.
- Uso: identificar a estratégia atual (lavoura, pastagem, mosaico, vegetação) e a fração de Caatinga ao redor. Limitação: no sertão, quase tudo cai em "outras lavouras temporárias" ou "mosaico", então a cultura específica vem da PAM ou da fenologia.

**D30. Embrapa: Mapa de Solos do Brasil / PronaSolos** (Embrapa Solos; o PronaSolos reúne Embrapa, SGB e IBGE)
- Contém: classes de solo do SiBCS.
- Resolução: escala 1:5.000.000; legenda atualizada em 2011.
- Cobertura: Brasil.
- Acesso: o PDF de 2011 é CC BY-NC-ND 4.0; a licença do vetor de 2020 e do PronaSolos não foi confirmada.
- URL: https://www.infoteca.cnptia.embrapa.br/infoteca/handle/doc/920267
- Referência: Santos et al. 2011, Embrapa Solos, Documentos 130.
- Uso: casar o tipo de solo da fazenda com a classe de solo do ZARC e com a água disponível da HWSD.

**Leituras e fontes complementares (verificadas):**
- Hastenrath & Heller 1977, QJRMS 103:77–92, 10.1002/qj.49710343505.
- Moura & Shukla 1981, J. Atmos. Sci. 38:2653–2675, 10.1175/1520-0469(1981)038<2653:OTDODI>2.0.CO;2 (DOI confirmado no Crossref).
- Hastenrath 2012, Climatic Change 112:243–251, 10.1007/s10584-011-0227-1.
- Andreoli & Kayano 2006, International Journal of Climatology 26:1895–1912, 10.1002/joc.1341.
- Marengo et al. 2017, Theor. Appl. Climatol. 129:1189–1200, 10.1007/s00704-016-1840-8.
- Sun et al. 2005, J. Climate 18:551–567, 10.1175/JCLI-3266.1: downscaling da FUNCEME.
- de Menezes et al. 2021, J. Agronomy and Crop Science, 10.1111/jac.12539: híbridos de sorgo sob seca no semiárido.
- Rossetti 2001, Rev. Bras. Agrometeorologia 9(3):386–399 (ZARC e crédito; PDF no site do MAPA).
- Silva & Oliveira 2017, Rev. Bras. Geografia Física 10(4):1269–1280: áreas suscetíveis à desertificação no Ceará, 81,56% do território no semiárido. DOI não confirmado; https://periodicos.ufpe.br/revistas/rbgfe/article/download/234084/27481
- Fontes institucionais:
  - Embrapa Semiárido (https://www.embrapa.br/semiarido);
  - Embrapa Agroindústria Tropical, para o caju (https://www.embrapa.br/agroindustria-tropical);
  - Embrapa Meio-Norte, para o caupi (https://www.embrapa.br/meio-norte);
  - Embrapa Algodão (https://www.embrapa.br/algodao);
  - Embrapa Mandioca e Fruticultura (https://www.embrapa.br/mandioca-e-fruticultura).
- MapBiomas Água: em 2024, a Caatinga tinha 981.350 ha de água, 17,9% abaixo do máximo; resolução não confirmada.

---

## 7. Uso combinado de dados NASA na agricultura

### Artigos

**7.1 Brito, S.S.B. et al. (2018; online 2017).** *Frequency, duration and severity of drought in the Semiarid Northeast Brazil region.* International Journal of Climatology 38:517–529. https://doi.org/10.1002/joc.5225 [DOI✓ · snippet]
- Achado: com SPI-12 e o índice de saúde da vegetação (VHI) em 1981–2016, a seca mais severa e longa foi a de 2011–2016.
- Uso: combina índice de chuva e índice de vegetação por satélite, o mesmo desenho que faremos com IMERG e NDVI do MODIS.

**7.2 Cunha, A.P.M.A. et al. (2019).** *Extreme Drought Events over Brazil from 2011 to 2019.* Atmosphere 10(11):642. https://doi.org/10.3390/atmos10110642 [DOI✓ · snippet]
- Achado: um Índice Integrado de Seca (meteorológico mais sensoriamento remoto) mostra as secas mais severas e extensas de 2011 a 2017, com destaque para 2014/15.
- Uso: é o modelo de índice combinado do Cemaden para replicar com SMAP, IMERG e NDVI.

**7.3 Zeri, M. et al. (2018).** *Tools for Communicating Agricultural Drought over the Brazilian Semiarid Using the Soil Moisture Index.* Water 10(10):1421. https://doi.org/10.3390/w10101421 [DOI✓ · snippet]
- Achado: com 595 estações de umidade do solo do Cemaden no semiárido, propõe o índice ISA, que identifica estresse hídrico de 3 dias ou mais, para data de plantio e irrigação.
- Uso: a rede do Cemaden serve para validar o SMAP no Nordeste. O ISA é uma forma simples de comunicar estresse ao agricultor.

**7.4 Anderson, M.C. et al. (2016).** *The Evaporative Stress Index as an indicator of agricultural drought in Brazil: An assessment based on crop yield impacts.* Remote Sensing of Environment 174:82–99. https://doi.org/10.1016/j.rse.2015.11.034 [DOI✓ · snippet]
- Achado: no Brasil (2003–2013), o ESI se correlacionou com a produtividade mais que a chuva TRMM e o LAI na maioria das culturas, com pico de 10 a 25 dias de antecedência na soja. Captou secas-relâmpago no milho da Bahia.
- Uso: justifica usar ET térmica (ECOSTRESS, ou ESI) como sinal de estresse antecipado no Nordeste.

**7.5 Rossato, L. et al. (2017).** *Impact of Soil Moisture on Crop Yields over Brazilian Semiarid.* Frontiers in Environmental Science. https://doi.org/10.3389/fenvs.2017.00073 [DOI✓ · resumo]
- Achado: nos municípios do semiárido, a produtividade de arroz, feijão, mandioca e milho se correlaciona mais com a chuva do que com a umidade modelada em 100 cm. A raiz média tem cerca de 40 cm, e a planta responde à água das camadas superiores.
- Uso: **use a umidade da zona radicular rasa** (SMAP L4 de 0–100 cm com cautela; preferir a superfície e o balanço até cerca de 40 cm). Não confiar em camadas profundas como preditor de safra.

**7.6 Gonçalves, R.D. et al. (2020).** *Using GRACE to quantify the depletion of terrestrial water storage in Northeastern Brazil: The Urucuia Aquifer System.* Science of the Total Environment 705:135845. https://doi.org/10.1016/j.scitotenv.2019.135845 [DOI✓ · pág.]
- Achado: no Sistema Aquífero Urucuia (cerca de 125 mil km², oeste baiano), o armazenamento caiu 6,5 ± 2,6 mm/ano entre 2002 e 2014, sem queda significativa da chuva. A causa é atribuída a fatores antrópicos, como a irrigação.
- Uso: é a evidência para o indicador "sustentabilidade da água subterrânea" das estratégias irrigadas, com o GRACE na escala regional.

**7.7 Renna Camacho, C. et al. (2023).** *Large-Scale Groundwater Monitoring in Brazil Assisted With Satellite-Based Artificial Intelligence Techniques.* Water Resources Research 59. https://doi.org/10.1029/2022WR033588 [DOI✓ · resumo]
- Achado: um conjunto de modelos de IA (XGBoost, LightGBM e CatBoost, mais regressão) combina GRACE e poços da rede RIMAS em 12 aquíferos. O erro (RMSE) cai para 2,68 cm, contra 6,76 cm do GLDAS. A variação estimada em duas décadas é de −31 km³ no Urucuia e −6 km³ no Bauru-Caiuá.
- Uso: mostra como passar o GRACE de cerca de 300 km para a escala do aquífero com IA e poços. É uma rota para o alerta de água subterrânea.

**7.8 Fisher, J.B. et al. (2020).** *ECOSTRESS: NASA's Next Generation Mission to Measure Evapotranspiration From the International Space Station.* Water Resources Research 56(4). https://doi.org/10.1029/2019WR026058 [DOI✓ · snippet]
- Achado: a evapotranspiração foi validada em 82 torres de fluxo (r² 0,88, viés de 8%). O pixel de 70 m, comparado ao de 1 km, melhora a correlação em 85% e reduz o erro em 62%.
- Uso: o ECOSTRESS a 70 m resolve o talhão pequeno do sertão; é o sinal de estresse hídrico por talhão.

**7.9 Xue, J. et al. (2022).** *Improving the spatiotemporal resolution of remotely sensed ET information for water management through Landsat, Sentinel-2, ECOSTRESS and VIIRS data fusion.* Irrigation Science 40:609–634. https://doi.org/10.1007/s00271-022-00799-7 [DOI✓ · snippet]
- Achado: funde o térmico do ECOSTRESS e do VIIRS com Landsat e HLS e gera ET diária a 30 m, com menor latência que o Landsat sozinho.
- Uso: é o caminho para cobrir as lacunas da órbita irregular do ECOSTRESS com HLS e VIIRS na série do Ceará.

**7.10 White, J.W. et al. (2008).** *Evaluation of NASA satellite- and assimilation model-derived long-term daily temperature data over the continental US.* Agricultural and Forest Meteorology 148:1574–1584. https://doi.org/10.1016/j.agrformet.2008.05.017 [DOI✓ · pág.]
- Achado: comparação com 855 estações. A Tmax do POWER ficou 2,4 °C mais fria (RMSE de 4,1 °C) e a Tmin 1,1 °C mais quente. A data de antese do trigo simulada teve r² de 0,92.
- Uso: o POWER é adequado para fenologia e graus-dia de pragas, mas **precisa de correção de viés** com estações do INMET ou da FUNCEME.

**7.11 Van Wart, J. et al. (2015).** *Creating long-term weather data from thin air for crop simulation modeling.* Agricultural and Forest Meteorology 209–210:49–58. https://doi.org/10.1016/j.agrformet.2015.02.020 [DOI✓ · snippet]
- Achado: com radiação do POWER, chuva do TRMM e temperatura calibrada com cerca de 3 anos de estação, a produtividade simulada ficou dentro de ±10% em 78% dos locais, contra 44% com o POWER bruto.
- Uso: é a receita de "clima sintético" para rodar modelos de cultura (DSSAT ou APSIM) em qualquer lugar: POWER mais IMERG mais calibração curta.

**7.12 Rozante, J.R. et al. (2018).** *Evaluation of TRMM/GPM Blended Daily Products over Brazil.* Remote Sensing 10(6):882. https://doi.org/10.3390/rs10060882 [DOI✓ · snippet]
- Achado: o IMERG Final superou o TMPA em todas as regiões do Brasil (2014–2017). Na costa do Nordeste, todos os produtos subestimam a chuva diária.
- Uso: o IMERG é a chuva padrão do produto, mas precisa de correção com postos da FUNCEME, sobretudo no litoral cearense.

### Datasets

**D31. SMAP: umidade do solo** (NASA NSIDC DAAC)
- Contém dois produtos:
  - **SPL3SMP_E v006**: umidade superficial, 9 km (EASE-Grid 2.0), diária, global; doi 10.5067/M20OXIZHY3RJ; https://nsidc.org/data/SPL3SMP_E
  - **SPL4SMGP v008** (Level-4): superfície e zona radicular, assimilação no modelo Catchment, 9 km a cada 3 h, de 31/03/2015 até hoje; doi 10.5067/T5RUATAQREF8; https://www.earthdata.nasa.gov/data/catalog/nsidc-cprd-spl4smgp-008-0
- Acesso: gratuito, com Earthdata Login (padrão NASA; não conferido na página).
- Referências: Entekhabi et al. 2010, Proc. IEEE 98:704–716, 10.1109/JPROC.2010.2043918; Reichle et al. 2019, JAMES 11:3106–3130, 10.1029/2019MS001729 (erro sem viés de 0,039 m³/m³ na superfície e 0,026 na zona radicular).
- Uso: estado hídrico do solo para o semáforo de plantio e o balanço FAO-56. O L4 de zona radicular é o mais útil, com a ressalva de Rossato (7.5).

**D32. GPM IMERG Final Daily V07 (GPM_3IMERGDF)** (NASA GES DISC)
- Contém: precipitação diária em mm/dia.
- Resolução: 0,1°; diária; desde junho de 1998, com o registro TRMM-GPM reprocessado na V07.
- Cobertura: global.
- Acesso: Earthdata Login; CC BY 4.0; doi 10.5067/GPM/IMERGDF/DAY/07; também no AWS Open Data.
- URLs: https://registry.opendata.aws/nasa-gpm3imergdf/ e ATBD em https://gpm.nasa.gov/sites/default/files/2023-07/IMERG_V07_ATBD_final_230712.pdf
- Uso: contagem de veranicos (definição FUNCEME), SPI e chuva por decêndio para comparar com o ZARC.

**D33. MODIS MOD13Q1 v061 e VIIRS VNP13A1 v002, índices de vegetação** (NASA LP DAAC)
- Contém: NDVI e EVI (o VIIRS também EVI2), com camadas de qualidade.
- Resolução: MODIS a 250 m e 16 dias, desde 2000; VIIRS a 500 m e 16 dias, desde 2012, como continuidade.
- Cobertura: global.
- Acesso: livre. DOIs: 10.5067/MODIS/MOD13Q1.061 e 10.5067/VIIRS/VNP13A1.002.
- URLs: https://catalog.data.gov/dataset/modis-terra-vegetation-indices-16-day-l3-global-250m-sin-grid-v061 e https://www.earthdata.nasa.gov/es/data/catalog/lpcloud-vnp13a1-002
- Uso: fenologia de 25 anos para detectar ciclos e rotação (método de Arvor) e anomalia de vegetação na seca.

**D34. HLS v2.0 (HLSL30/HLSS30)** (NASA LP DAAC)
- Contém: reflectância harmonizada Landsat 8/9 e Sentinel-2A/B/C; produtos de índice de vegetação desde fevereiro de 2025.
- Resolução: 30 m (tiles MGRS); revisita combinada de cerca de 1,6 a 3 dias.
- Cobertura: terras globais, exceto a Antártida.
- Acesso: livre, em COG. DOIs: 10.5067/HLS/HLSL30.002 e 10.5067/HLS/HLSS30.002.
- URL: https://www.earthdata.nasa.gov/data/projects/hls
- Referência: Claverie et al. 2018, RSE 219:145–161, 10.1016/j.rse.2018.09.002.
- Uso: NDVI a 30 m por talhão, para identificar a cultura atual e acompanhar a safra em lavouras pequenas do sertão.

**D35. Landsat Collection 2 Level-2 (reflectância e temperatura de superfície)** (USGS EROS)
- Contém: reflectância e temperatura da superfície.
- Resolução: 30 m; 16 dias por satélite; desde 22/08/1982.
- Cobertura: global.
- Acesso: livre (EarthExplorer).
- URL: https://www.usgs.gov/landsat-missions/landsat-collection-2
- Uso: histórico longo de 40 anos de uso e temperatura para a fazenda. É a base do MapBiomas e do MapBiomas Fogo.

**D36. ECOSTRESS: ET em tiles a 70 m (ECO_L3T_JET v002)** (NASA LP DAAC)
- Contém: evapotranspiração instantânea e diurna, com produtos L4 de ESI e eficiência do uso da água (código exato não confirmado). A v001 era ECO3ETPTJPL (PT-JPL).
- Resolução: 70 m; temporal irregular, pela órbita da ISS, desde 2018.
- Cobertura: faixa de latitudes da ISS (limites não confirmados; o Ceará, perto de 4°S, está dentro).
- Acesso: livre, em COG; disponível no AppEEARS.
- URL: https://cmr.earthdata.nasa.gov/virtual-directory/collections/C2076106409-LPCLOUD
- Uso: estresse hídrico por talhão, comparando a ET real das estratégias. É a evidência de "uso de água" na comparação.

**D37. GRACE/GRACE-FO: mascons (JPL RL06.3 v4 e CSR RL06.3)** (NASA PO.DAAC; UT Austin CSR)
- Contém: anomalia de armazenamento de água terrestre, em cm de água equivalente.
- Resolução: JPL em grade de 0,5° com mascons nativos de 3°; CSR em 0,25°, cerca de 1° nativo; mensal desde abril de 2002.
- Cobertura: global.
- Acesso: o JPL exige Earthdata Login (netCDF-4; doi 10.5067/TEMSC-3JC634); o CSR tem download direto.
- URLs: https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4 e https://www2.csr.utexas.edu/grace/RL06_mascons.html
- Uso: tendência regional de água subterrânea (Urucuia, Araripe), como alerta para estratégias com irrigação. Não serve para a escala da fazenda.

**D38. NASA POWER (API, comunidade "AG")** (NASA LaRC)
- Contém: Tmax, Tmin, radiação, chuva, umidade e vento para agroclimatologia. Agora também traz IMERG (cerca de 0,1°) e SMAP L4 (cerca de 0,09°).
- Resolução: meteorologia em ½° × ⅝° (MERRA-2/GEOS-IT) e radiação em 1°; horária, diária e climatologia; meteorologia desde 1981.
- Cobertura: global.
- Acesso: gratuito; até 20 parâmetros por ponto. Não confirmamos se exige chave.
- URL: https://power.larc.nasa.gov/docs/methodology/
- Referência do cliente R: Sparks 2018, JOSS 3:1035, 10.21105/joss.01035.
- Uso: ETo para o FAO-56, graus-dia de pragas e clima diário para DSSAT ou APSIM em qualquer ponto do mundo, com correção de viés (White 2008).

**D39. NASADEM (NASADEM_HGT v001)** (NASA LP DAAC)
- Contém: modelo digital de elevação do SRTM reprocessado, sem vazios.
- Resolução: 1 arco-segundo (cerca de 30 m); estático.
- Cobertura: de 60°N a 56°S.
- Acesso: livre; doi 10.5067/MEASURES/NASADEM/NASADEM_HGT.001.
- URL: https://catalog.data.gov/dataset/nasadem-merged-dem-global-1-arc-second-v001
- Uso: declividade e posição no relevo, para risco de erosão, acúmulo de água (baixios) e aptidão mecanizável.

**D40. NISAR L3 Soil Moisture (SME2), provisório** (NASA/ISRO; ASF DAAC)
- Contém: umidade do solo a partir de radar banda L.
- Resolução: **200 m** (EASE-Grid 2.0); cerca de 2 passagens a cada 12 dias; latência de 72 h. A meta é 0,06 m³/m³ com vegetação abaixo de 5 kg/m².
- Cobertura: global. O satélite foi lançado em 30/07/2025 e o beta está disponível desde 01/10/2025.
- Acesso: **provisório, não validado**; ficou fora do release validado de 11/2026.
- URL: https://www.earthdata.nasa.gov/data/catalog/asf-nisar-l3-sme2-provisional-v1-1
- Uso: é o "próximo passo" de resolução, de 9 km para 200 m. Usar na demonstração como camada experimental, rotulada como tal.

**Leituras e datasets complementares (verificados):**
- Melati et al. 2019, Hydrogeology Journal 27:2789–2802, 10.1007/s10040-019-02065-1: GRACE na Bacia do Araripe (CE/PE); GRACE mais GLDAS foi a melhor combinação.
- Lima et al. 2020, Boletim de Ciências Geodésicas 26, 10.1590/s1982-21702020000300013: o armazenamento do GRACE se correlaciona 0,78 com o volume de reservatórios do Nordeste.
- Paredes-Trejo & Barbosa 2017, Water 9:377, 10.3390/w9060377: índice de déficit hídrico do solo (SWDI) com SMOS no Nordeste.
- Anderson et al. 2011, J. Climate 24:2025–2044, 10.1175/2010JCLI3812.1: define o ESI.
- Kogan 1995, Adv. Space Res. 15:91–100, 10.1016/0273-1177(95)00079-T: índices VCI, TCI e VHI.
- White et al. 2011, Agronomy Journal 103:1242–1251, 10.2134/agronj2011.0038: radiação do POWER.
- Rodrigues et al. 2021, Water 13:2714, 10.3390/w13192714: IMERG na bacia do São Francisco, com correlação diária de 0,28 a 0,61.
- dos Santos Araújo et al. 2024, RSASE 33:101111, 10.1016/j.rsase.2023.101111: umidade do solo por satélite para seca no semiárido (resumo não obtido).
- OpenET: Melton et al. 2022, JAWRA 58:971–994, 10.1111/1752-1688.12956; cobre os EUA, e "OpenET Brazil" aparece sem detalhes.
- ESA CCI Soil Moisture (seção 5).

---

## Ideias derivadas da literatura

### A. Motor de rotação

1. **Representação.** Usar um grafo de sucessões com nós "cultura × safra" e arestas permitidas ou proibidas por regra, como em Haneveld & Stegeman 2005, Detlefsen & Jensen 2007 e o ROTOR. Enumerar sequências de 3 a 5 anos e otimizar por fluxo em rede ou busca exaustiva, o que é viável com cerca de 10 culturas. Programação inteira e aprendizado por reforço (Fenz 2023; CropGym) ficam como extensão.
2. **Efeito da cultura antecessora.** Multiplicar o rendimento por `1 + b`. Para leguminosa antecessora, `b` vale 0,20 em média, 0,32 em baixa produtividade e 0,07 em alta. Reduzir `b` em cerca de 7% a cada 50 kg N/ha e zerar acima de 236 kg N/ha (Zhao 2022). Reduzir também conforme a aridez, já que o efeito é mais fraco no Sahel segundo Franke 2018.
3. **Resiliência.** Simular a estratégia sobre todos os anos de 2000 a 2025 (IMERG/POWER) e reportar:
   - a média;
   - o **percentil 10** da produtividade;
   - a **probabilidade de perda acima de X%**;
   - a perda em 2012–2016.
   - Calibrar a redução de perda em ano seco pela diversidade: de 14% a 90% em Bowles 2020 e 17% em Renwick 2021.
4. **Consórcio.** Avaliar pela razão de área equivalente (LER), pela produtividade do sistema e pelo ganho econômico (Mudare 2022; Diniz 2017; Souza 2011), e não pela produtividade de cada cultura isolada.
5. **Carbono e saúde do solo.** O indicador anual de carbono do solo parte do MapBiomas Solo ou do SoilGrids:
   - planta de cobertura ou adubo verde: cerca de +0,56 Mg C/ha/ano (Jian 2020);
   - corte e queima sem pousio: −50% em 10 anos (Primo 2023);
   - leguminosa de grão em rotação de cereais: cerca de −5% (King & Blesh 2018), como alerta.
6. **Multicritério.** Pesos definidos pelo agricultor (renda, risco, solo, água, trabalho) sobre os indicadores normalizados, como em Sadok 2008. Mostrar o ranking e a sensibilidade aos pesos.
7. **Estratégia atual.** Inferir pelo histórico: MapBiomas mais PAM, com cadeia de Markov de transições (Osman 2015; baseline de Yaramasu 2020) e número de ciclos por NDVI ou GCI30 (Arvor 2011). Para os EUA, validar com CDL e CSB.

### B. Água e clima (Ceará)

- **Balanço hídrico.** Calcular ETc = Kc (FAO-56, ajustado para clima seco) × ETo (POWER). A oferta vem do IMERG corrigido com a FUNCEME e da água disponível da HWSD. O índice tipo ISNA é ETr/ETm na floração. Validar contra a tábua do ZARC.
- **Veranicos.** Contar sequências de 3 ou mais dias com até 2 mm entre fevereiro e maio (Rocha 2021) e usá-las como preditor de perda de milho e feijão. Calibrar com a SIDRA 1612.
- **Cenário sazonal.** Ponderar os anos históricos análogos por ENSO (Niño 3.4) **e** pelo gradiente do Atlântico (Nobre & Shukla 1996; Kayano & Andreoli 2006). Alternativa: ponderar pelos tercis da FUNCEME.
- **Sinais de estresse.** Usar SMAP L4 (zona radicular, com a cautela de Rossato 2017), ESI ou ECOSTRESS (antecedência de 10 a 25 dias, Anderson 2016) e anomalia de NDVI (VHI, Brito 2018).
- **Água subterrânea.** Usar a tendência do GRACE como alerta regional para estratégias irrigadas (Gonçalves 2020; Renna Camacho 2023).

### C. Pragas ("percolação")

- **Rede de hospedeiros.** Os nós são células de 5 km (CROPGRIDS/SPAM) ou municípios (PAM). O peso vem da densidade de hospedeiro por praga, definida pela tabela EPPO de hospedeiros. A aresta é a resistência à transmissão, que cai com a densidade (Margosian 2009) e com a distância (modelo gravitacional, Xing 2020).
- **Métrica de percolação.** Medir o tamanho do maior componente conectado acima de um limiar de hospedeiro. O limiar é estimado por simulação na própria grade, no espírito de Bailey et al. 2000. Comparar o tamanho do componente nas estratégias: se a estratégia troca milho por não hospedeiro, quanto o componente encolhe?
- **Quebra de ciclo.** Contar os meses consecutivos com hospedeiro da mesma praga no talhão (Ratnadass 2011) e penalizar sequências curtas e repetitivas (risco de adaptação, Levine 2002).
- **Graus-dia.** Calcular o número de gerações por ciclo com Tmax e Tmin do POWER, corrigidas:
  - lagarta-do-cartucho: base de cerca de 12,6 °C; 35,7 °D para o ovo, 204,6 °D para a larva e 150,5 °D para a pupa (du Plessis 2020);
  - bicudo: R0 máximo a 25–28 °C (Pereira 2023).
  - Ambos são índices relativos entre estratégias, não previsões de infestação.
- **Algodão.** Se a estratégia inclui algodão, aplicar a regra obrigatória de destruição de soqueira e vazio sanitário, com o risco do bicudo exibido (Azambuja & Degrande 2014).
- **Paisagem.** Usar a fração de Caatinga num raio de 1 a 2 km como fator protetor de peso **baixo** e incerto (Rusch 2016 contra Karp 2018).

### D. Queimadas

- **Índice de risco de fogo.** Combinar:
  - SPI-6 com defasagem de cerca de 4 meses, VPD e ondas de calor (Bezerra 2025);
  - a diferença entre a chuva do ano anterior e a do ano atual (Argibay 2020);
  - recorrência e anos desde o último fogo (MapBiomas Fogo);
  - distância a estradas;
  - focos ativos (FIRMS) para alerta.
- **Penalidade por estratégia.** Aplicar a estratégias que usam fogo: perda de carbono do solo (Primo 2023), queda de P após a queima (Salcedo 1997), menor regeneração (Sampaio 1998) e risco de fuga do fogo para vizinhos (Cano-Crespo 2015).
- **Métricas.** Fração queimada por ano (MCD64A1), FRP e anos desde o último fogo.

### E. Validação

- **Rendimento municipal.** Comparar com o IBGE PAM (Ceará, 1974–hoje) contra o que o motor prevê para a estratégia "atual" em cada ano. A métrica é a correlação das anomalias, que pede um teste pareado ano a ano.
- **Janela de plantio.** Medir a concordância com o ZARC (o mesmo decêndio indicado).
- **Parte global.** Prever a próxima cultura com CDL e CSB. A métrica é OA ou kappa contra a baseline de Markov (Yaramasu 2020).

---

## Lacunas: o que procuramos e não encontramos ou não confirmamos

- **Rotação no semiárido do Ceará.** Não achamos artigo revisado por pares com dados de produtividade de **rotação**. Só achamos consórcio (Souza 2011; Silva 2009; Diniz 2017) e uma enquete (Scientia Agraria, 90% não fazem rotação) que não foi detalhada. Esse é o principal buraco de evidência local, e o motor dependerá de priors globais (Zhao, Bowles) moduladas pela aridez.
- **Sistemas de recomendação de culturas com sensoriamento remoto.** Não achamos artigo sólido; os resultados eram anais fracos ou patentes. Também não achamos crítica publicada ao dataset do Kaggle; a análise crítica é nossa.
- **Autores pedidos e não encontrados.** Sahajpal (LSTM sobre o CDL), "Johnson & Mueller" (previsão pré-safra) e Kastens como primeiro autor não apareceram. Smith et al. 2023 **não** é da Nature Sustainability, e não encontramos um "Liu et al. 2022" sobre produtividade; só a síntese de carbono do solo.
- **Algodão no Nordeste.** Números do colapso da área (a cifra "2 milhões para 350 mil ha" só apareceu em veículo de imprensa) não foram confirmados em fonte revisada. Usar a série do IBGE PAM/CONAB.
- **Bemisia no Brasil.** Não achamos modelo climático de escala nacional para a mosca-branca. Nematoides: não achamos uma revisão específica de rotação no semiárido.
- **Caju, palma, mandioca e sorgo.** Achamos poucos estudos de produtividade sob seca. Para caju, só a revisão de Bezerra 2007 e números da imprensa setorial: área de 775 mil ha em 2009 e 595 mil ha em 2016. A cartilha da Embrapa sobre palma (2022) não abriu.
- **ZARC.** Nenhuma portaria do Ceará foi aberta. Os níveis 20/30/40%, o modelo SARRA e as classes AD1–AD6 foram vistos só em snippet. O artigo-base de Cunha & Assad 2001 (Rev. Bras. Agrometeorologia 9(3):377–385) foi visto só como citação.
- **FUNCEME.** Licença, formato de download e API dos postos não foram confirmados; o site apresentou erro de certificado. As perdas de 2012 no Ceará (feijão cerca de −80%, milho cerca de −86%) vieram de um boletim do MAPA, com números inconsistentes entre trechos.
- **Dados.** Não confirmamos:
  - a resolução nativa por camada do GAEZ v5 (30″ ou 5′);
  - a resolução do MapBiomas Água;
  - os limites exatos de profundidade do SoilGrids;
  - a licença do FAO-56, do WorldClim, do EarthStat e do PronaSolos;
  - um artigo revisado do SPAM 2020;
  - se o FAO Crop Calendar e o GYGA cobrem o Brasil;
  - a cobertura do FAMEWS no Brasil;
  - se a API do POWER exige chave;
  - a faixa de latitude e o código dos produtos L4 do ECOSTRESS v002;
  - se o "OpenET Brazil" já opera.
- **Não pesquisados.** GRACE no aquífero Guarani, artigos-base do SRTM (Farr 2007), do VIIRS VI e do NISAR, e a revisão de Akpoti 2019 sobre aptidão agrícola.
- **Limite de buscas.** A cota de buscas na web da sessão (200) acabou durante o levantamento. A parte final foi feita só com páginas oficiais e com consultas diretas aos metadados do Crossref, do OpenAlex e do Semantic Scholar (DOIs e resumos). Itens marcados com `snippet` devem ter os números conferidos no texto completo antes de entrar em slides.
