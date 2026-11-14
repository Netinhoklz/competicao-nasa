# %% [markdown]
# ## 90. Síntese
#
# ### 90.1 Veredito de cobertura global (o produto pode atender o mundo?)
#
# | Base | Global? | Evidência deste estudo | Ressalva para o produto |
# |---|---|---|---|
# | NASA POWER | **Sim** | 107 pontos em todos os continentes, inclusive Antártida, Svalbard e oceano: meteorologia 100% válida (seção 1) | ~50 km: clima regional, não microclima |
# | GPM IMERG | **Sim** | V07 com dados nos 216 pontos testados, de 85°S a 85°N (seção 2) | V07 diária a 0,1° vem aberta pelo POWER (~2 meses de atraso); V06 completa só entre 60°S e 60°N |
# | ERA5 | **Sim** | 90°S–90°N, sem ausentes (seção 3) | modelo, não observação; ~31 km; aberto só até 2020 (Planetary Computer) |
# | NEX-GDDP-CMIP6 | **Quase** | 60°S–90°N, só terra (seção 15) | projeções; usar vários modelos para chuva |
# | NLDAS | **Não** | caixa 25–53°N, 125–67°W (seção 4) | usar só como enriquecimento nos EUA |
# | GLDAS | **Quase** | 60°S–90°N (seção 4) | sem Antártida; exige Earthdata |
# | SMAP | **Sim** | 85°S–90°N (seção 4) | exige Earthdata; 9 km; L3 só 0–5 cm → usar L4 (zona da raiz) |
# | GRACE/GRACE-FO | **Sim** | 100% das células de terra e oceano (seção 6) | resolução efetiva ~300 km; 35 meses faltantes (lacuna 2017–18) |
# | Landsat | **Sim** | dados nas 27 caixas de teste de 81°N a 80°S (seção 7) | revisita de 8–16 dias; nuvem na estação chuvosa |
# | Sentinel-2 | **Sim** | idem (seção 8) | NDVI tem viés contra o Landsat → usar **HLS** |
# | MODIS | **Sim (terra)** | ~300 tiles por período, 14 pontos em 6 continentes (seção 9) | Terra no fim da vida (lacuna de jun–nov/2025) → migrar para VIIRS |
# | VIIRS (fogo FIRMS) | **Sim** | arquivos anuais por país (seção 9) | NDVI do VIIRS exige Earthdata |
# | SRTM/NASADEM | **Quase** | 56°S–60°N (seção 10) | completar com o Copernicus DEM (global) |
# | FAO GAEZ | **Sim** | 99,8% dos pixels de terra, 56°S–84°N (seção 11) | ~9 km; clima de 1981–2010; produção real "2010" não confere com o IBGE |
# | AMS Market News | **Não** | só EUA, API com chave (seção 12) | trocar por FAOSTAT (por país) + Banco Mundial (referência) |
# | CDL | **Não** | só EUA contíguos (seção 14) | serve de laboratório e de "prior" de rotação; globais: WorldCereal, MapBiomas (BR) |
#
# **Conclusão de arquitetura: núcleo global + enriquecimento local.**
# - **Núcleo (funciona em qualquer lugar):**
#   - chuva: IMERG, com o POWER de reserva;
#   - temperatura, radiação e ET0: POWER (ERA5 como alternativa);
#   - umidade do solo: SMAP L4, com o POWER GWETROOT enquanto não houver login;
#   - vegetação: HLS a 30 m, a cada 2–4 dias;
#   - relevo: NASADEM + Copernicus DEM;
#   - água regional: GRACE;
#   - fogo: VIIRS/FIRMS;
#   - aptidão: GAEZ (+ ECOCROP);
#   - mercado: FAOSTAT + Banco Mundial;
#   - futuro: NEX-GDDP-CMIP6.
# - **Enriquecimento local quando existir:**
#   - Brasil: IBGE PAM, ZARC e MapBiomas;
#   - EUA: CDL, SSURGO e NLDAS.
#
# ### 90.2 O que os dados dizem sobre o Ceará (o roteiro do pitch)
# 1. **Uma janela, uma chance.**
#    - 77,5% do Ceará só comporta uma safra de sequeiro (GAEZ).
#    - A estação vai de ~2/fev a ~28/jul, com pico em abril (MODIS).
#    - O solo fica exposto de setembro a janeiro (MODIS/Landsat).
#    - **A rotação no sertão é, antes de tudo, decidir o que fica no solo na entressafra** (cobertura, forrageira,
#      leguminosa perene) e qual cultura arrisca na quadra.
# 2. **A chuva decide o rendimento, cultura a cultura** (IBGE PAM × POWER, seção 20).
#    - Cada +100 mm em fev–mai: milho +10%, fava +9%, feijão +8%; mandioca +3%, cana +1,4%.
#    - Mandioca, cana e culturas irrigadas são os **amortecedores** da rotação.
# 3. **O oceano avisa, mas pouco.**
#    - O ONI de out–jan correlaciona com a chuva de fev–mai (r ≈ −0,39).
#    - Um modelo de tercil acerta 41% contra 33% do acaso (RPSS +0,10).
#    - O produto deve falar em **probabilidades**.
#    - O ONI de set/2026 em +2,46 (El Niño forte) é **alerta para a quadra de 2027**.
# 4. **O aquecimento está na temperatura, não na chuva.**
#    - Tendência de temperatura: Tmax do POWER +0,37 °C/década; T2m do ERA5 +0,18 °C/década. 73% dos pixels do
#      Nordeste têm aumento significativo de Tmax. A chuva anual não tem tendência.
#    - **Cuidado com limiares absolutos:** a Tmax do POWER é ~1,7 °C mais quente que a do ERA5. Os dias acima de 35 °C
#      crescem +10/década no POWER e +2/década no ERA5. O produto deve usar **anomalias ou percentis por fonte**, ou
#      calibrar com estação do INMET.
#    - ET0 ~1.960 mm/ano contra ~810 mm de chuva; a ET0 supera a chuva em 10 de 12 meses.
#    - **Futuro (NEX-GDDP, 1 modelo):** dias ≥ 35 °C passam de 56/ano para 98/ano em 2046–50 (SSP5-8.5) e 142/ano em
#      2086–90. O sinal de temperatura é robusto; o de chuva, não.
# 4b. **O início da estação prevê a estação** (IMERG, seção 2).
#    - Início médio ~17/jan; o dia de início correlaciona ρ = −0,67 com o total da estação.
#    - Isso dá uma **regra de decisão em fevereiro**: início tardio → trocar para a rotação tolerante à seca.
#    - Seca composta: chuva e Tmax anuais com ρ = −0,88; em 2012–17, −29% de chuva, +0,58 °C de Tmax e +96 mm/ano de ET0.
#    - Chuva concentrada e erosiva: 73% em fev–mai; I30 de até 80 mm/h; maior veranico médio da quadra de 12,7 dias
#      (22,6 em 2012).
# 5. **A água tem memória de anos.**
#    - O GRACE no Ceará acompanha a chuva acumulada de 36–48 meses (r ≈ 0,47–0,49).
#    - Na seca de 2012–2017, 45 de 50 meses ficaram abaixo do normal (mínimo de −24,6 cm em jul/2016).
#    - Contraponto: o aquífero Urucuia (Oeste da Bahia) perde 1,4–1,7 cm/ano.
# 6. **A vegetação responde rápido à água e o calor a denuncia.**
#    - NDVI × chuva: pico com 1 mês de defasagem.
#    - Umidade da raiz × NDVI: r ≈ 0,51.
#    - LST × NDVI: r ≈ −0,85 → índice de secura (TVDI) a 1 km, global.
# 7. **Fogo: antes do plantio e na Caatinga.**
#    - 72% dos focos caem em out–dez; 62% na Caatinga, 14% em lavoura.
#    - Anos verdes antecedem mais fogo ~6 meses depois (combustível).
#    - O produto de área queimada a 500 m não vê o roçado; o VIIRS a 375 m vê.
# 8. **A nuvem cega o satélite óptico justo na estação.**
#    - Só 7–25% das cenas Landsat de fev–mai têm menos de 20% de nuvem.
#    - **HLS** (Landsat + Sentinel-2) é obrigatório, e o radar (Sentinel-1/NISAR) é o próximo passo.
# 9. **O que cabe no Ceará depende do insumo** (GAEZ).
#    - Com insumo baixo, típico da agricultura familiar: sorgo, mandioca, guandu, feijão.
#    - **O algodão tem aptidão alta e área ~zero:** caiu de 306 mil ha (1985) para ~2 mil ha, e o algodão arbóreo de
#      1,25 Mha para zero. Pragas (bicudo) e mercado explicam o que o clima não explica.
# 10. **A conta do adubo favorece a leguminosa.** A razão de preço ureia/milho chegou a 4,0 (abr/2026), contra uma
#     média de 1,5 em 2000–2020 (Banco Mundial).
# 11. **A rotação real é mensurável.** No CDL (EUA), 73% do Iowa alterna milho↔soja, mas o semiárido do Texas tem
#     67% de algodão contínuo. A monocultura no semiárido é o mesmo risco que o bicudo explorou no Nordeste.
#
# ### 90.3 O que a literatura acrescenta (ver `pesquisa/artigos_e_datasets.md`)
# - **Leguminosa antes da cultura:** +20% no rendimento seguinte, chegando a +32% em ambientes de baixa produtividade;
#   o efeito some com muito N mineral (Zhao et al. 2022, Nat. Commun.).
# - **Rotação diversa:** +28% no milho e perdas 14–90% menores em ano seco (Bowles et al. 2020, One Earth).
# - **Corte e queima sem pousio no semiárido (Sobral-CE):** ~50% do carbono do solo perdido em ~10 anos (Primo et al. 2023).
# - **Veranico** (≥ 3 dias com ≤ 2 mm) liga-se à perda de milho e feijão no Ceará (Rocha et al. 2021, FUNCEME).
# - **ZARC (MAPA):** tábua de risco aberta por município × cultura × solo × decêndio. É a restrição de janela de
#   plantio pronta para o Brasil.
# - **Alerta:** o "Crop Recommendation Dataset" do Kaggle tem padrão de dado sintético e não deve ser usado como evidência.
#
# ### 90.4 Pendências e riscos
# - **Earthdata Login:** SMAP, GLDAS, NLDAS, VIIRS VNP13 e os últimos ~2 meses do IMERG (Early/Late) aguardam a
#   credencial. O IMERG V07 diário a 0,1° de 1998 a set/2026 já veio pelo POWER, sem login. Os scripts estão prontos
#   (`scripts/baixar_earthdata.py`).
# - **Chuva no litoral leste:** o IMERG ficou em ~40–60% de normais aproximadas em Recife, Maceió, Aracaju e Salvador,
#   contra 82–94% no sertão. As normais usadas eram aproximadas: **conferir com as Normais do INMET** antes de afirmar
#   viés. Pode haver efeito de pixel misto terra/mar.
# - **ERA5 aberto só até 2020** (espelho do Planetary Computer); para 2021+, CDS com chave. O ERA5 tem viés de
#   chuvisco (mais dias ≥ 1 mm que o IMERG).
# - **Calibração do POWER:** o IMERG do POWER só vem preenchido no horário UTC; a radiação começa em 1984.
# - **MODIS:** os arquivos reprocessados mudaram o tipo do campo de qualidade (já tratado); a tendência da LST diurna é
#   contaminada pela deriva orbital do Terra.
# - **AOIs:** as coordenadas são aproximadas; para a demo, escolher talhões reais com o usuário.

# %%
print("Síntese (texto). Números detalhados nas seções 1–20.")
