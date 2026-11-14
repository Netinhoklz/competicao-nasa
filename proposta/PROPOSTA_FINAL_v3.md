# QUADRA: proposta final v3 (NASA Space Apps 2026, desafio "Field Shift")

- **Versão:** v3, montada sobre a v2 com as correções da rodada 3, sábado 14/11/2026, a partir das 14:00 (hora local, pelo `date`). Prazo de submissão: domingo 15/11/2026, 23:59.
- **De onde vem a v3:** a `PROPOSTA_FINAL_v2.md` inteira, com as correções de seis fontes da rodada 3: a leitura dos artigos do Nordeste (`pesquisa/viabilidade_artigos_nordeste.md`, seção 4.3 e "Verificação adversária"), o catálogo de rotações (`pesquisa/catalogo_rotacoes_comprovadas.md` e `pesquisa/catalogo_rotacoes.json`), o El Niño 2026–27 corrigido (`pesquisa/el_nino_2026_nordeste.md`), o notebook de análogos climáticos (`notebooks/analogos_transferencia.ipynb`, texto em `notebooks/secoes_analogos/`), a estrutura GAEZ + ZARC (`proposta/estrutura_gaez_zarc.md`) e o plano de rotação 2027–2029 da família de demonstração (seção 6.4). O que mudou está na seção R3. Daqui para baixo, o texto da v2 continua valendo onde a R3 não diz outra coisa.
- **Revisão de 14/11 (tarde):** a revisão de 10 agentes do protótipo (`protótipo/REVISAO_10_AGENTES.md`) corrigiu dados de base (Tmax do POWER, classes do GAEZ, ciclos do ZARC, datas do IMERG). Os números novos estão na R3.5 e já entraram no texto, nas seções 2 a 12 e no resumo em inglês.
- **Versão anterior:** v2 corrigida depois da banca da rodada 2, sábado 14/11/2026, a partir das 11:25 (hora local, pelo `date`).
- **De onde vem:** a `PROPOSTA_FINAL.md` (rodada 1), refeita com as reanálises da rodada 2, que usaram os dados novos já em disco (SMAP L4 diário, SMAP L3, VIIRS VNP13A3, GLDAS-2.2 CLSM diário, GLDAS-2.1 Noah, NLDAS-2, IMERG V07 Late/Early recente), com o artigo-âncora Kluger, Di Tommaso & Lobell (2025) e com os três pareceres da banca da rodada 2 (juiz, cético e engenheiro de viabilidade).
- **Análises do arquiteto:** `conselho/analises/v2_arquiteto_arbitragem_smap.py` resolve as divergências entre especialistas (seção R2.2). Depois da banca, `conselho/analises/v2_arquiteto_r2_fechamento.py` → `.saida.txt` traz as curvas por era nos 5 portões, a escolha pré-declarada da luz de 2027 e o hash da regra, o nível do ano em 2016, 2021, 2022 e 2025, o placar de Quixadá, o contrafactual do caupi em 1998, 2016 e 2024, a carteira condicionada à luz NASA e a checagem com o SMAP L3 consolidado.
- **Regra de honestidade (mantida):** todo número tem arquivo de origem. Os scripts da rodada 2 ficam em `conselho/analises/v2_<persona>_<tema>.py`, cada um com seu `.saida.txt`. As referências vêm da revisão `pesquisa/artigos_e_datasets.md` ou de `pesquisa/artigo_ancora_objetivo.md` (Crossref conferido em 14/11/2026); as que estão fora das duas têm a marca "fora da revisão". **Na v3**, valem também o guia `pesquisa/artigos_nordeste.md` (lido e conferido em `pesquisa/viabilidade_artigos_nordeste.md`) e o catálogo de rotações; os scripts da rodada 3 ficam em `conselho/analises/v3_*` e `v4_*`.
- **Regra da leitura menos favorável (mantida):** quando duas leituras igualmente razoáveis do mesmo dado dão números diferentes, **o slide usa a menos favorável** e o recibo mostra a outra.
- **Regra nova, cobrada pela banca R2: linha de base justa.** Todo ganho é medido contra a **melhor** leitura já declarada do mesmo dado, nunca contra a pior. Foi essa regra que trocou a luz principal (R2.1).
- **Regra nova da rodada 3: transferência medida.** Um número de rotação só entra no motor se foi medido no semiárido brasileiro (T0) ou num análogo de aridez e temperatura com pelo menos 5 sítios (T1). Média global ou de continente dá só a direção (T2). O recibo mostra o peso de clima w do estudo, medido com o NASA POWER (`pesquisa/catalogo_rotacoes_comprovadas.md`, "Como ler"; `notebooks/secoes_analogos/06_motor.py`).

---

## R3. O que mudou na rodada 3

### R3.1 Em cinco frases

1. **A rotação ganhou um número que vale no sertão, e um limite.** Para caupi (ou outra leguminosa de grão) antes de milho ou sorgo **solteiro**, em sequeiro quente, o motor usa +24% no ano colhido (faixa de +2% a +49%). É síntese do conselho, grau B·T1, e as âncoras de artigo concordam. Contra a prática de hoje (milho + feijão consorciados), a troca para rotação no tempo **nunca foi medida**: central 0, sensibilidade de 0 a +9% (D·T3).
2. **A NASA mede de onde a evidência pode vir.** Pela assinatura de clima do POWER (com a Tmax e a Tmin médias, corrigidas em 14/11; R3.5), os celeiros temperados onde a rotação foi medida por satélite têm peso w = 0,00 para Quixadá, e nenhum ensaio de rotação no tempo vem de clima de sertão. Nenhum número de rotação T0/T1 vem de clima parecido (w ≥ 0,3): o Franke da África Austral (+42%) caiu para w 0,10. Ponderado pelo clima, Quixadá ficaria em cerca de +28% (soma dos pesos 0,46). O motor fica com os +24% e usa os +28% só como sensibilidade, porque nenhum estrato do Franke tem clima parecido com Quixadá (o maior peso é o da Savana da Guiné, 0,25).
3. **O ZARC oficial vira o limite.** Onde há ZARC, ele decide a cultura e a janela. O GAEZ v4 (aptidão > 40, a classe "média" ou melhor da v4; insumo baixo) só filtra as culturas sem ZARC, e nos perímetros irrigados entra com insumo alto. Em Quixadá, o milho nunca chega ao risco de 20% (o melhor é 30%, de 11/fev a 10/mar, só nos solos que guardam mais água, AD5–AD6). O ZARC 2026/27 só zoneia alguma cultura a partir de 21/jan, e a 40%; o risco de 20% só aparece em 11/fev. O milho entra em 11/fev (a conferir na portaria).
4. **A família da demo ganhou um plano por faixas para 2027–2029** (seção 6.4). Três faixas trocam de lugar a cada ano (mandioca-tampão, caupi precoce e sorgo forrageiro). O baixio leva milho + caupi em revezamento tardio, e as bordas, palma + gliricídia em nível. Sem mandioca no chão hoje, o tampão só protege a partir de 2028; em 2027, a proteção vem do escalonamento e da forragem.
5. **A leitura dos artigos do Nordeste corrigiu 18 trechos da v2** (R3.3). Os que mais pesam são a ET0 do POWER (1,27 vez a das estações automáticas do INMET, mas 0,97–1,01 vez as normais: o fator 0,79 vira só sensibilidade), o Garantia-Safra conferido na lei, o carbono de Sobral ("perde menos", não "recupera"), o palma + sorgo como índice (IPS) e o "ano úmido e depois seco" do fogo, que não se repete no Ceará. O solo do Ceará em novembro de 2026 está normal, em 5º de 12 novembros (na entrada de 2015, foi o 2º; na de 2023, o 7º). Nenhuma frase diz que ele está mais seco que nos El Niños anteriores.

### R3.2 Componente → mudança → evidência → arquivo

| Componente | Mudança | Evidência (número conferido) | Arquivo |
|---|---|---|---|
| Motor, efeito da leguminosa antes do cereal | **Novo: cartão do Nordeste** no lugar das médias globais | +24% no ano colhido (faixa +2% a +49%), só contra cereal solteiro e com N ≈ 0; síntese do conselho, B·T1. Âncoras de artigo: Franke +24% (Sahel e Guiné); Mudare, leguminosa com MAT > 20 °C, +22% (+5 a +40). As médias globais (Zhao +20%) dão só a direção (T2) | `pesquisa/catalogo_rotacoes_comprovadas.md`, "O que o motor usa no Nordeste" e "Verificação adversária" (B2, B3); `pesquisa/catalogo_rotacoes.json` |
| Motor, sair do consórcio S0 | **Novo: "não medido"** | Consórcio milho + feijão → rotação no tempo: central 0, sensibilidade 0 a +9% (D·T3). É o ensaio que falta | catálogo, cartão `ne_s0_para_rotacao_tempo` e lacuna 2 |
| Motor, aridez | **Sai "efeito menor na zona árida"** | A aridez não reduz o efeito relativo: Franke dá +24% no Sahel e +24% na Guiné (zona × resposta, p = 0,351). No ano seco, o intervalo alarga até 0; o que cai é a t/ha e a chance de colher | catálogo, regra G05 e "Regras rejeitadas na R2" |
| Motor, ano colhido | **Novo** | O bônus só vale no ano colhido. O milho quebra em 20,2% dos município-anos do CE e em 21,0% no NE (2000–2024, mediana da mesma janela) | catálogo, G01 e B4 |
| Motor, comparáveis sem leguminosa | **Novo** | Pousio → milho +31% e sorgo → milho +28% (C·T2, só direção); caupi → milho contra milho contínuo +14,7% (B·T2). Milho-sorgo na sequência vira alerta C (n = 10), não veto | catálogo, resumo do Nordeste; "Verificação adversária", itens 8, 10 e 13 |
| Motor, consórcio milho + caupi | **Ressalva nova** | LER 1,37 na África (Mudare 2022). O 1,15 de Souza 2011 foi irrigado até 40 DAS: o LER em sequeiro não foi medido | catálogo, item 18 |
| Recibo, transferência | **Novo: peso de clima w pelo POWER** | Celeiros temperados w = 0,00. Nenhum número de rotação T0/T1 com w ≥ 0,3 (o Franke da África Austral, +42%, caiu para w 0,10); ponderado, cerca de +28% em Quixadá (soma dos pesos 0,46; só sensibilidade). A ordem dos análogos resiste: o Cerrado piauiense fica no top-3 do Sertão Central em 100% de 2.000 sorteios de pesos, e o semiárido da Índia em 98,6%; o tau de Kendall fica entre 0,85 e 0,92 tirando qualquer variável | `notebooks/secoes_analogos/06_motor.py` (seção 6 e conclusões); `01_robustez.py` |
| Recibo, por município | **Novo** | O Cerrado piauiense é o melhor análogo em 102 municípios, Sobral em 40, a Savana da Guiné em 13 e a África Austral (Harare) em 11. A confiança média vai de 0,73 (Norte) a 0,90 (Centro-Sul); a Região Metropolitana de Fortaleza passou de 0,31 para 0,75 | `notebooks/secoes_analogos/02_mapa_ceara.py` |
| Recibo, aptidão | **Novo: o GAEZ confere o análogo** | Spearman −0,76 entre distância de clima e semelhança de aptidão. Os 5 lugares mais parecidos no clima têm perfil de culturas parecido (0,79 a 0,98). Harare (−0,08) deixou de ser análogo (d 2,15, 10º lugar) | `notebooks/secoes_analogos/04_aptidao.py` |
| Portão de jan–fev | **Novo** | Nos 3 anos de El Niño forte da série de início (2010, 2016 e 2024), a chuva começou **antes** no estado: mediana no dia 6, contra o dia 18 nos anos neutros (sem La Niña) e o dia 15 em todos os demais anos (n = 3 anos). No município, o sinal muda: 129 municípios do CE com início mais cedo, 34 mais tarde e 13 iguais. O início da estação não protege | `notebooks/secoes_analogos/05_ciclo_plantio.py`; `notebooks/secoes_prototipo/07_imerg_inicio.py` |
| Produto global | **Novo** | Só 19 de 387 pontos de terra (grade de 6°, contando o próprio Ceará) têm distância < 1,5 do clima do Sertão Central. Os mais parecidos: Chaco argentino (0,77), Oeste da Bahia e norte da Austrália (1,01), Burkina Faso (1,04), sudoeste de Madagascar (1,05) e Deccan (1,15). O norte de Minas (1,59) e a China saíram | `notebooks/secoes_analogos/03_sertao_no_mundo.py` |
| Camadas de clima médio | **Novo: GAEZ v4 + ZARC + portões NASA + catálogo** | Onde há ZARC, o ZARC decide; o GAEZ (> 40, insumo baixo) filtra só as culturas sem ZARC; nos perímetros irrigados, insumo alto. Cardápio do MVP com 15 culturas; Quixadá tem 9 | `proposta/estrutura_gaez_zarc.md`, seções 5, 5.1 e 6 |
| Janela sintética × ZARC oficial | **Conferida; "depende do solo"** | Contra o solo e o ciclo mais permissivos, só o milho confere (Spearman 0,86; ±1 decêndio em 89%). Contra a mediana dos solos e ciclos, caupi e sorgo conferem (±1 em 84%), e o milho sintético fica 2 decêndios mais tarde. Em Quixadá, o caupi de 21/mar fica a ±1 decêndio do oficial em 8 de 9 combinações de solo e ciclo; só com o Grupo I, o único com cultivar indicada (R3.5), em 2 de 3 (no argiloso, o oficial vai até 20/abr). **A frase do caupi na 6.2 fica**, dizendo o solo | `pesquisa/viabilidade_artigos_nordeste.md`, 4.3 e "Verificação adversária"; `v3_verificador_zarc_solo.saida.txt` |
| ET0 do POWER | **Corrigida** | 1,27 vez a das 16 automáticas do INMET no CE (vento +1,6 m/s; radiação +1,4 MJ/m²/dia), mas 0,97 (Fortaleza) e 1,01 (Sobral) vez a ETP normal; Tmax com viés de só +0,14 °C. O fator 0,79 é só sensibilidade | viabilidade, 4.3 e 4.4 (item 9); `v3_curador_valida_inmet.saida.txt`, D e D2 |
| Garantia-Safra | **Conferido na lei** | Perda ≥ 40% (art. 8º, Lei 15.236/2025); área plantada máxima de 5 ha (art. 10, IV, redação da Lei 12.766/2012); renda de até 1,5 salário mínimo (art. 10, III); até 4 módulos fiscais (art. 10, V). Dona Francisca (3 ha) cabe | viabilidade, 4.3 e "Verificação adversária" (Planalto, lido pela ferramenta web em 14/11) |
| El Niño 2026–27 no Nordeste | **Corrigido** | Zona da raiz do SMAP L4, 30 dias até 10/11, posição entre 12 anos: MA e SE 1º (o mais seco), PI e PE 2º, AL e BA 3º, PB e RN 4º, CE 5º (normal). O percentil pronto do SMAP quase não existe nessa época e saiu | `pesquisa/el_nino_2026_nordeste.md` |
| Plano da família | **Novo (seção 6.4)** | Faixas que trocam de lugar em 2027–2029, dentro da janela do ZARC; tampão de mandioca a partir de 2028 | 6.4, com a fonte de cada linha |

### R3.3 Os 18 trechos da v2 corrigidos pela leitura dos artigos

A lista vem de `pesquisa/viabilidade_artigos_nordeste.md`, seção 4.3, já revista pela "Verificação adversária" do mesmo arquivo. A linha é a da v2.

| Linha da v2 | Antes | Agora | Onde na v3 |
|---|---|---|---|
| 155, 826 | "Milho e feijão ocupam 91% da área" | 91% da área das lavouras **temporárias** (PAM 2017); com as permanentes, 66,2% (62,4% em 2025) | 2.1; 8.1 |
| 826 | "Veranico explica a perda" | O veranico acompanha a perda, mas **acrescenta pouco** à chuva total; pesa nos anos de chuva normal | 8.1 |
| 827 | Kayano & Andreoli 2006, "JGR 111:D13101" | JGR 111(D13), localizador 2005JD006142; o D13101 não foi confirmado | 8.1 |
| 838 | Rossato 2017 para "solo raso" | Não sustenta "solo raso, chuva manda": com GLDAS e IMERG, a água no solo prevê melhor que a chuva | 8.1 |
| 842 | "GRACE com r = 0,78 contra os açudes" | ρ de Spearman entre médias anuais (n ≈ 15–16), na região hidrográfica Atlântico Nordeste Oriental (PI a AL) | 8.1 |
| 730 | "Palma + sorgo: 6.279 contra 4.627 kg MS/ha" | O 6.279 é o **IPS** (índice de produtividade do sistema); em matéria seca, o consórcio deu 12.130 kg/ha, igual ao sorgo solteiro (14.073, sem diferença) | S2 |
| 675, 751 | Primo 2023 "Sobral-CE"; "a agrofloresta recupera o carbono" | Primo é simulação Century, local não verificado (D). A medição em Sobral (Sacramento 2013) mostra que a agrofloresta **perde menos** carbono que a broca com queima | S0; S3; 8.1 |
| 834 | Salcedo 1997 para "−50% de C" e "fuga do fogo" | Salcedo trata de nutrientes depois da queima; sai dessa linha | 8.1 |
| 836 | "Ano úmido seguido de ano seco gera grandes queimadas" (Argibay 2020 e Bezerra 2025) | Bezerra é de **2026** e não trata disso. O padrão é só de Argibay, num ecótono do PI, e não aparece no CE | 2.3; M7; 8.1 |
| 171, 835 | "MapBiomas Fogo a 30 m: 12,7% entre 1985 e 2023" | O 12,7% confere; o nome "MapBiomas Fogo" não está no resumo e fica a conferir | 2.1; 8.1 |
| 186 | Perda de confiança por Lemos et al. 2002 | Lemos sustenta distorção e má interpretação; a perda de credibilidade está em Finan & Nelson 2001, p. 105. Citar os dois | 2.2 |
| 184, 829 | "Marengo et al. (2021)" | Marengo et al. 2022, Clim. Resil. Sustain. 1:e17 (aceito em 2021) | 2.2; 8.1 |
| 329, 1059 | "Tmax do POWER ~1,7 °C mais quente"; "a diferença de 15% vem do viés quente da Tmax do POWER" | Contra o INMET, a Tmax do POWER tem viés de só +0,14 °C. A ET0 do POWER sai 1,27 vez a das automáticas, mas 0,97–1,01 vez as normais | 4.2; M1; 9.7 |
| 619, 976, 1371 | Garantia-Safra "40% ou 50%", "área mínima" | Perda ≥ 40%; área **máxima** de 5 ha; renda até 1,5 SM; até 4 módulos fiscais | 6.1; 9.3; 9.5; Anexo A |
| 615, 651 | "Caupi ±1 decêndio" | **A frase da linha 651 fica.** No estado, o veredito contra o ZARC oficial depende do solo; ao citar, dizer contra qual solo | M1; 6.1; 6.2 |
| 262 | "o PAM sugere" a prática atual | Quem sugere é o **Censo 2017**: a diversidade do PAM quase não acompanha a rotação declarada (ρ +0,15 no CE) | 3.3; M5 |
| 988, 1127, 1292 | LSPA cortada "por custo" | A LSPA já está baixada para as 9 UFs, sem custo | 9.6; 10; 13.1 |
| 548, 644, 769 | Cisterna-calçadão de 52 m³; cisterna de 16 m³ | Nenhum dos dois volumes foi confirmado nos textos lidos. Marengo 2022 confirma só que a cisterna é de beber | M7; 6.2; 6.3 |

### R3.4 O que não mudou, e por quê

- **Os números de vitrine da v2 ficam iguais:** a luz principal, a segunda missão, o 2016 no nível do ano, o placar de Quixadá e a carteira. A rodada 3 não refez nenhum deles.
- **A frase do caupi de Quixadá (6.2) fica.** A leitura dos artigos tinha marcado o trecho, e a verificação adversária o confirmou.
- **Os +28% ponderados pelo clima não viram o número central** (eram +36% antes da correção da Tmax; R3.5). Nenhum estrato do Franke tem clima parecido com Quixadá (w de 0,10 a 0,25).
- **As médias globais (Zhao +20%, +32% em baixa produtividade) não viram número do sertão.** São T2: dão só a direção. O +32% está só no resumo do artigo, sem intervalo.
- **Os números do Kluger (4,5% e 3,7×) continuam fora dos slides** até a conferência na versão publicada da ERL.
- **Nenhum número novo vai aos slides.** Os slides 3, 5 e 6 ganham frases sem número novo (seção 11).

### R3.5 Revisão de 14/11 (tarde): dados corrigidos

Dez agentes revisaram o protótipo (`protótipo/REVISAO_10_AGENTES.md`). Dois dados de base estavam errados, e algumas regras estavam mal aplicadas. Os dados foram regerados, e os números abaixo substituem os antigos em todo o documento.

- **A. Análogos climáticos (revisão C2/A2).** A Tmax e a Tmin do POWER eram o recorde do mês da climatologia. Agora são a média das diárias de 2001–2024 (Tmax da estação úmida de Quixadá: 39,2 → 32,6 °C). Números novos (`E:/campeonato-nasa/tmp/analogos_numeros_novos.md`; `notebooks/analogos_transferencia.ipynb`):
  - top-3 do Sertão Central em 2.000 sorteios de pesos: Cerrado piauiense 99,6% → 100%; semiárido da Índia 15,6% → 98,6% (agora o 2º análogo); Harare 22,2% → 3,6%;
  - Harare deixou de ser análogo (4º → 10º; d 1,34 → 2,15). Melhor análogo por município do CE: Cerrado piauiense 42 → 102; Sobral 78 → 40; Harare 53 → 11;
  - confiança da Região Metropolitana de Fortaleza: 0,31 → 0,75. A menor agora é a do Norte (0,73);
  - sertão no mundo, d < 1,5: 8 → 19 pontos de 387. O norte de Minas e a China saíram;
  - GAEZ: Spearman −0,64 → −0,76;
  - pesos w para Quixadá: Bom Jesus-PI 0,82 → 0,95; Harare 0,41 → 0,10;
  - leguminosa → cereal ponderado pelo clima em Quixadá: +36% → +28% (soma dos pesos 0,46). Nenhum número de rotação T0/T1 vem de clima parecido. O motor continua com +24%;
  - os rótulos proibidos saíram dos dados: Sobral cita Sacramento 2013, não Primo; o Franke aparece como "Franke 2018 (zona)", sem "efeito MENOR/MAIOR".
- **B. GAEZ (A3/M1).** Valem as classes da camada oficial da v4: > 85 muito alta; > 70 alta; > 55 boa; > 40 média; > 25 moderada; > 10 marginal; > 0 muito marginal. O corte "apta" passou de > 35 para > 40, e a aptidão tem 1 casa decimal. Os limiares 75/63/50/35 eram do texto do portal, não da v4. No CE, a mandioca fica apta em 155 municípios (antes 164), o guandu em 123 (antes 135) e o milheto em 102 (antes 121).
- **C. ZARC (C3/M4/M5/A6/A7).**
  - No CE, só entram os grupos de ciclo com cultivar indicada: caupi e sorgo forrageiro no Grupo I; mamona nos Grupos II–IV. A mamona do cardápio é a tradicional; a de "Clima Semiárido" fica fora.
  - A janela termina no último dia do decêndio, e não no primeiro.
  - O aviso tem duas datas: zoneada (até 40%) e risco de 20%. Em Quixadá, 21/jan e 11/fev.
  - A janela é mostrada por solo.
  - Quixadá: caupi com 20% de 11/03 a 20/04 (antes 21/02–11/04); milho só até 30%, de 11/02 a 10/03, e só em AD5–AD6; sorgo forrageiro com 20% de 21/02 a 30/04.
  - O ZARC 2026/27 do CE tem 11 portarias, uma por cultura; a Portaria 245 vale só para o milho com braquiária. No NE: 240.949 linhas, 1.794 municípios, 17 culturas e 113 portarias.
- **D. IMERG (A16).** O IMERG Final V07 termina em 30/09/2025. O que vem depois no arquivo diário via POWER (até 14/09/2026) é o Late, preliminar.
- **E. Início da chuva em El Niño (M25/A17).** O "dia 6 contra 18" vale contra os anos neutros (sem La Niña). Contra todos os demais anos, é dia 6 contra 15. No município, o sinal varia: 129 municípios do CE com início mais cedo, 34 mais tarde e 13 iguais. Em Quixadá, os +24 dias têm n = 3 e não se separam do acaso: 14% das triplas de anos sem El Niño forte dão diferença ≥ 24 dias (permutação).
- **F. Regime de chuva do NE** (`regime_chuva_ne_mun.csv`, os 4 meses mais chuvosos do IMERG). Quadra do norte (jan–abr ou fev–mai): 1.056 municípios. Litoral leste (mar–jun ou abr–jul): 312. Cerrado e sul da BA (out–jan, nov–fev ou dez–mar): 426. No litoral leste, o IMERG capta só 39–72% da chuva medida (17 automáticas do INMET a menos de 20 km do mar, do RN à BA, fora o litoral norte do RN; `v3_curador_valida_inmet.saida.txt`, B2). Os portões de 19/mar e 30/abr foram calibrados no CE, que é todo de quadra do norte (184 de 184).
- **G. Protótipo.** Cobre os 1.794 municípios do Nordeste. O El Niño é medido no próprio município, e os números do catálogo só aparecem para cartões T0/T1 (`protótipo/README.md`).
- **A1 e C5 resolvidos (14/11, noite):** a tábua das portarias plurianuais do CE foi extraída e conferida (mandioca Port. 11/2020, milheto Port. 330/2020, palma Port. 284/2019; `scripts/zarc_plurianual_ce.py`; duas leituras independentes, PDF do MAPA e DOU, bateram em todas as células). As três constam como vigentes na página "Safra vigente — Ceará" do MAPA (05/11/2026); o SISZARC não foi conferido. Na mandioca, abril fica fora em 160 de 184 municípios (com risco ≤ 30%, em todos); em Quixadá, risco de 20% de 01/02 a 10/03. O protótipo já usa essa tábua no CE, e o "maniva de fevereiro a abril" deste texto foi trocado pela janela da portaria. As contagens estaduais da janela sintética × ZARC (Spearman 0,86; ±1 decêndio em 89% e 84%) foram feitas com todos os grupos de ciclo e não foram refeitas só com os grupos com cultivar.

---

## R2. O que mudou na rodada 2

### R2.1 Em cinco frases (já com a banca R2)

1. A regra de alerta da rodada 1 (chuva IMERG desde 1/jan < 75% do normal) **funcionou em 1998–2015 e falhou em 2016–2025**. Janeiros chuvosos (2016 e 2025) encheram a soma, e a quadra fraca passou sem alerta.
2. O que recupera a última década é **ler a água como estado e esquecer janeiro**, não o SMAP em si. A mesma chuva IMERG, contada **desde 1/fev**, empata com o SMAP L4 em 30/abr (AUC 0,76 contra 0,77; diferença +0,013, IC90 por ano de −0,04 a +0,08). É também a única leitura que se segura nas duas eras e nos dois portões de decisão (AUC mínima de 0,71) (`v2_cetico_r2b_smap_contra_imerg_justo.saida.txt`, bloco A; `v2_arquiteto_r2_fechamento.saida.txt`, blocos A e B).
3. **A regra de 2027 foi congelada hoje, com hash interno.** A luz principal é a chuva IMERG desde 1/fev < 75% do normal, lida em 19/mar e 30/abr. O SMAP L4 (percentil < 20, média de 7 dias) é a **segunda missão**, que confirma ou não. Em 19/mar (2016–2025), com as duas acesas, 5,3 em 10 municípios quebraram o milho; só com a chuva, 2,1; com nenhuma, 0,9 (taxa-base: 1,5). Grau B: a regra foi escolhida depois de ver 2016–2025; os limiares (75% e 20) foram fixados antes.
4. **O número-uau conta o ano, não o município.** Em 19/mar/2016, último dia de troca, a chuva IMERG contada desde 1/jan acendeu em 7 dos 182 municípios. Contada desde 1/fev, acendeu em todos os 182. E 127 (7 em 10) perderam o milho. Qual município? Nenhuma leitura sabe: a AUC dentro de 2016 fica entre 0,61 e 0,65. O alarme falso vai junto: em 2022, a chuva desde fevereiro acendeu em 142 municípios, o SMAP em nenhum, e 3 quebraram.
5. **A rotação tem número onde dá e "sem número" onde não dá.**
   - Contra a prática atual (milho + feijão), um terço em mandioca leva o "pior ano em 10" de 0,26 a 0,36. É um teto: o placebo do vizinho deixa só +0,02 a +0,08 como parte própria da mandioca.
   - Nos município-anos com a luz NASA acesa em 30/abr, o pior ano vai de 0,13 para 0,21.
   - Na metade guardada da S1, o balde (grau C) dá água na floração ao caupi de 11/mar em 7 de 10 municípios em 2016, mas em só 1 de 10 em 1998.
   - A S1 e a S3 não têm "pior ano" medido, e os cartões dizem isso.

### R2.2 Arbitragem das divergências (especialistas e banca)

Conferi cada divergência nos scripts e, quando foi preciso, nos dados (`v2_arquiteto_arbitragem_smap.saida.txt`, blocos A–F; `v2_arquiteto_r2_fechamento.saida.txt`, blocos A–I). Nada foi escolhido olhando qual opção favorece o QUADRA. A linha 10 usou um critério escrito antes de rodar o fechamento, mas depois de o cético já ter impresso as AUCs por era; isso está dito na própria linha.

| # | Divergência | Quem diz o quê | O que conferi | Decisão |
|---|---|---|---|---|
| 1 | AUC do SMAP em 19/mar (milho, 2016–2025) | 0,68: pesquisador de IA, SR, designer e hidrólogo. 0,59: estrategista, cético e agrônomo | Os dois estão certos; só muda a leitura. Média dos 7 dias até o portão: 0,682 (IC90 0,45–0,81). Valor do dia: 0,593 (0,39–0,71). Sem 2016: 0,495 e 0,444 | **O SMAP não decide em São José.** Quando o SMAP aparece sozinho em 19/mar, o deck usa 0,59. No portão, ele só confirma a luz principal (linha 10) |
| 2 | Quebras de 2016 pegas pelo SMAP < 20 em 30/abr | 90 de 127 (dia): estrategista e cético. 64 de 127 (7 dias): hidrólogo | Confirmado. O juiz refez a conta do `.nc` cru e bateu exatamente. Dentro de 2016, as 91 luzes pegam 64 quebras, contra 63,5 esperadas ao acaso | **O produto lê a média de 7 dias.** No slide, o SMAP aparece no nível do ano ("seco em metade do estado em 30/abr": 91 de 182). O 64 e o 90 ficam no recibo, com "o SMAP não sabe qual município" |
| 3 | Limiar do SMAP | < 25: agrônomo. < 20: seção 05, hidrólogo, estrategista, cético e designer | O < 20 está no commit `48a3608` (14/11, 08:34; "abaixo de 20 = seca agrícola"), antes dos testes | **< 20.** O 25 fica só como sensibilidade |
| 4 | Memória da zona da raiz | 13 dias: agrônomo. 46–58 dias: hidrólogo | Medem coisas diferentes: dentro do ano contra entre anos (38–46 dias na minha conta agrupada) | Nenhum "o solo esquece em X dias" vai ao pitch |
| 5 | O "+6,6 p.p." da diversidade | Robusto: estrategista e agrônomo. Frágil: agrônomo (só sequeiro), cético e economista (composição) | As duas contas de "séries repetidas" estão certas; só sequeiro dá +1,4 (n.s.); composição tem ρ −0,84 com a fração milho + feijão | **É composição, não diversidade.** Sai do slide 1 e vai para o slide de honestidade com o rótulo "composição, não diversidade" |
| 6 | Deslocamento do NDVI desde 2020 | SR: ~3/4 também no VIIRS. Cético: ~0,01 só do MODIS | Os dois têm razão (VIIRS +0,033 a +0,042; MODIS +0,047 a +0,053 com IMERG) | "Visto pelos dois sensores com a chuva IMERG; ~0,01 é do MODIS; causa aberta" |
| 7 | Placar de Quixadá | Agrônomo (< 25, dia): 2 acertos do SMAP. Cético (banca): com a chuva desde 1/fev, 2016 acende | **SMAP < 20: nenhum acerto** (2016 = p20,1; 2025 = p20,3 no dia). **Chuva desde 1/fev**: em 19/mar, 9 alertas e 3 acertos (1998, 2015, 2016); em 30/abr, 9 alertas e 5 acertos (1998, 2012, 2015, 2016, 2025, este último a 0,747, por um fio). A regra antiga dava 8/2 e 7/3 | O placar mostra as duas luzes, com os alarmes falsos (2018 e 2022 em 19/mar; 2005, 2010, 2013 e 2021 em 30/abr) e as quebras perdidas (2001, 2023, 2024) |
| 8 | Chuva de janeiro de 2016 | 205% (estado) e 216% (município mediano) | Agregações diferentes | "Cerca do dobro do normal" |
| 9 | VIIRS no fim de safra | AUC 0,79–0,81; dentro do ano 0,60–0,63 | Janelas diferentes; a geografia sozinha dá 0,61 dentro do ano | Testemunha do ano, não ordem local |
| 10 | **Luz principal de 2027** | v2: soma desde 1/jan OU SMAP. Juiz: "estado da água" = API do IMERG + SMAP. Cético: chuva desde 1/fev, com o SMAP confirmando | Critério pré-declarado R1: maior AUC **mínima** em {19/mar, 30/abr} × {1998–2015, 2016–2025}. Resultado: desde 1/fev 0,709; últimos 30 dias 0,672; API 0,607; últimos 15 dias 0,576; desde 1/jan 0,547. O API é o melhor em 30/abr (0,80; ρ entre anos +0,87), mas cai para 0,61 em 19/mar na última década | **Chuva IMERG desde 1/fev é a luz principal; o SMAP confirma.** O API e as outras leituras ficam no recibo. Ressalva: a escolha veio depois de o cético imprimir essas AUCs. E, no nível do ano, em 19/mar/2016–2025, nenhuma leitura ordena bem os anos (desde 1/fev +0,19; SMAP +0,32; desde 1/jan −0,30; n = 10) |
| 11 | O "1% do SMAP" (economista) contra os 64 de 127 (v2) | Economista: percentil pronto, corte 20, fev–mai. Cético (banca): é artefato da média de percentis | Média de ~89 percentis diários: dp 14,7, p10 34; acende em 0,7% e pega 0 de 127. O mesmo produto lido no portão pega 64; o posto da média sazonal, 84 (`v2_cetico_r2b_gatilho_carteira.saida.txt`, bloco 1) | **O "1%" sai do slide 6.** Era defeito nosso, não da NASA. O gatilho tipo Garantia-Safra fica na auditoria com a marca "escalas diferentes para IMERG e SMAP; refazer antes de qualquer frase" |
| 12 | Métricas da S1 | Juiz: calcular as 3 métricas (grau C). Engenheiro: "não medido" | Não existe S1 observada no PAM. O ISNA do milho semeado na 1ª chuva não vê 1998 (96% dos municípios com água pelo balde, contra 25% sem quebra no IBGE), então uma cauda simulada da S1 seria enviesada justo no ano que importa | **A S1 ganha o contrafactual da metade guardada nos três El Niños fortes (grau C).** As 3 métricas ficam como "sem número" no cartão |
| 13 | Números por slide | Juiz: no máximo 3. Engenheiro: no máximo 6 | Hoje são 12 a 18 tokens numéricos por slide | **No máximo 3 números no corpo, mais 1 linha de recibo no rodapé.** O resto vai para as notas e para o AUDIT.md |
| 14 | Cartão S0: estado ou município | v2: estado (0,15; 21%). Engenheiro: município | Quixadá, milho + feijão, 28 anos: 6 anos abaixo da metade (21%); pior ano em 10 = 0,16 (1998, 2012, 2016); mediana 1,05 | **S0 com o número do município**, rotulado "seu município". A S2 fica com o do estado, rotulado "estado" |
| 15 | Portão do número-uau | Juiz: 30/abr no nível do ano. Cético: chuva desde 1/fev × SMAP | Em 30/abr só cabe salvar (milho 0%, caupi 41% já em 31/mar). Em 19/mar/2016, a chuva desde 1/fev já acendia em 182 de 182 | **O número-uau é 19/mar (troca); o 30/abr é a confirmação do SMAP (metade do estado).** O vídeo deixa de se contradizer |

### R2.3 Componente → mudança → evidência → arquivo

| Componente | Mudança | Evidência (número conferido) | Arquivo |
|---|---|---|---|
| M3, regra de 1998–2025 (chuva desde 1/jan) | **Vira "regra antiga"**: aparece por era e no replay, nunca como luz de 2027 | 30/abr: AUC 0,83 em 1998–2015 e 0,66 em 2016–2025; com alerta, 5,9 e 1,1 em 10 quebram; 19/mar: 0,77 e 0,55 | `v2_arquiteto_arbitragem_smap.saida.txt`, E; `v2_arquiteto_r2_fechamento.saida.txt`, A |
| M3, luz principal de 2027 | **Nova: chuva IMERG desde 1/fev < 75% do normal**, em 19/mar e 30/abr | 19/mar: 0,74 (1998–2015) e 0,71 (2016–2025); 30/abr: 0,82 e 0,76. Em 2016–2025, com luz, quebram 2,8 em 10 (19/mar) e 3,8 em 10 (30/abr); sem luz, 0,9 e 0,8 | `v2_arquiteto_r2_fechamento.saida.txt`, A e B; `v2_cetico_r2b_smap_contra_imerg_justo.saida.txt`, F e H |
| M3, segunda missão | **SMAP L4 confirma**: percentil < 20, média de 7 dias. Vermelho = as duas; amarelo = só a chuva | 19/mar, 2016–2025: vermelho 5,3 em 10 quebram (118 município-anos, 5 anos), amarelo 2,1, verde 0,9. 30/abr: 4,1; 3,4; 0,8. Em 2022, a chuva acendeu em 142 e o SMAP em 0 (amarelo; 3 quebras) | `v2_arquiteto_r2_fechamento.saida.txt`, C |
| Regra congelada para 2027 | **Texto e sha256 interno** no fechamento; hash público só com o OK do José | sha256 `41b7c820…fdb41` (texto completo no bloco B) | `v2_arquiteto_r2_fechamento.saida.txt`, B |
| Oceano por era | **Novo:** o ONI de ASO medido nas duas eras | AUC 0,66 (1998–2015) e 0,72 (2016–2025). Na última década, o oceano conhecido em novembro valeu o mesmo que a melhor chuva de São José (0,71) | `v2_arquiteto_r2_fechamento.saida.txt`, A |
| SMAP L3 (radiômetro) | **Checagem refeita com o consolidado** (até 12/11/2026; 7 datas duplicadas removidas) | 30/abr: L3 0,774 (IC90 0,53–0,88; n = 1.740), igual ao recorte parcial; L4 0,767; chuva desde 1/fev 0,756; desde 1/jan 0,656. 19/mar: L3 0,637. Em 30/abr/2016, o L3 ficou abaixo de 75% do próprio normal em 173 de 174 municípios | `v2_arquiteto_r2_fechamento.saida.txt`, H |
| Recibo do SMAP: independência | **Ressalva mantida e corrigida** | O L4 é forçado por chuva corrigida para o IMERG (segundo a equipe do L4_SM, EGU23-1419; v008 não conferida) e corrigido pelo radiômetro. A checagem mais independente é o L3 | `v2_cetico_smap_l3_obs_vs_modelo.saida.txt`; fechamento, H |
| P3, troca em ano de luz acesa | **Corrigida de novo:** só o caupi até ~11/mar; **o sorgo sai da troca** | Água na floração pelo balde: caupi 11/mar em 68% (2016), 10% (1998) e 100% (2024); caupi 21/mar em 33%, 15% e 72%; sorgo 11/mar em 10% (2016) e 1% (1998) | `v2_arquiteto_r2_fechamento.saida.txt`, E; `v2_agronomo_smap_janelas.saida.txt`, F |
| Leitura de 10/mar (só em El Niño forte) | **Descritiva, sem habilidade medida** | Chuva desde 1/fev < 75% em 10/mar: 94% dos municípios em 1998, 100% em 2016 e 0% em 2024 (quebra: 75%, 70% e 8%). A soma desde 1/jan: 15%, 0% e 0% | fechamento, C |
| P1, portão de novembro | Mantido (modelo único pré-declarado no script do clima); a frase muda | "No El Niño mais forte antes deste (ONI 2,04), cerca de 5 em 10 (faixa de 2 a 8). Este ano está além do recorde" | `v2_clima_portao_novembro_2027.saida.txt` |
| P1, painel "hoje" | **De 6 para 4 itens:** ONI, termômetro dormindo, GRACE e caatinga | Quixadá 0,087 m³/m³ e o CE em 5º de 12 (posto reproduzido); o 0,121 do CE é a média das 1.837 células e só aparece copiado da folha | `v2_clima_smap_estado_inicial.saida.txt`; `v2_engenheiro_viabilidade_mvp.saida.txt`, C |
| M4, carteira | **Comparada com a prática atual (S0), com placebo** | 0,26 (milho + feijão) → 0,36 (1/3 com mandioca). Placebo pré-declarado do cético: o feijão do vizinho no lugar da mandioca já dá 0,335 (0,323–0,347); o milho do vizinho, 0,278. Parte própria da mandioca: +0,02 a +0,08 | `arquiteto_final_carteira_ic.saida.txt`; `v2_cetico_r2b_gatilho_carteira.saida.txt`, 3 |
| M4, carteira nos anos de luz NASA | **Novo:** o número da rotação passa pelo dado da NASA | Município-anos com chuva desde 1/fev < 75% em 30/abr (n = 585, 17 anos): pior ano em 10 de milho 0,05, S0 0,13, 1/3 0,21 (ganho sobre a S0 com IC90 por ano de +0,04 a +0,10) | fechamento, F |
| M4, piso e teto | Mantidos | Piso de 0,32 sem maniva; o mundo real entrega ~65% do ganho por cultura | `v2_economista_diversidade_carteira.saida.txt`, B e C |
| M2 (emulador de fim de safra) | **Sai da demo e do bloco 0** | As previsões por município-ano nunca foram salvas; o 0,307 já estava suspenso | `v2_engenheiro_viabilidade_mvp.saida.txt` |
| M1, datas e estado | Mantidos (balde para datas; calibração pelo SMAP só para o estado) | r no ano fora de 0,838 → 0,958; caupi ±1 decêndio em 58% | `v2_hidrologo_calibra_m1_smap.saida.txt`; `v2_agronomo_smap_janelas.saida.txt` |
| M7, relógio lento | **Números corrigidos** | Memória de chuva explica **55%** da variância do GWS no ano fora (70% dentro da amostra). O ρ +0,04 é do **resíduo do CLSM**, não do GRACE. O GRACE direto acompanha os açudes do Landsat (ρ +0,57; +0,73 em diferenças anuais). A memória IMERG e o GRACE rodam como pares (n = 23 não separa os dois) | `v2_hidrologo_relogio_lento_gws.saida.txt`, 1 e 3 |
| M7, CLSM × GRACE | Não é validação | "Assimila o GRACE por construção; não medimos quanto" | `v2_cetico_clsm_grace_viirs.saida.txt`, A |
| Selo de visibilidade | **Frase corrigida** | "O radiômetro do SMAP (pegada de ~40 km, grade de 9 km) vê a célula mediana em 13–15 dias por mês, através das nuvens; o óptico fica parcialmente cego (39–40% de pixels bons em jan–mar)" | `v2_sr_fundacao_smap_l3_l4.saida.txt`, A; `v2_sr_fundacao_viirs_portoes.saida.txt`, A |
| Escala dentro do ano | **Frase corrigida** | Nenhuma camada passa de ~0,65 dentro do ano (L3 0,645 em 30/abr; VIIRS 0,62–0,63); a geografia sozinha dá 0,61 | fechamento, H; `v2_hidrologo_smap_portoes_quebra.saida.txt` |
| Diversidade | **"Composição, não diversidade"**; sai do slide 1 | Só sequeiro +1,4 p.p. (p 0,51); composição × fração milho + feijão ρ −0,84 | `v2_agronomo_diversidade_robustez.saida.txt`; `v2_cetico_diversidade_composicao.saida.txt` |
| Narrativa | **"Stanford" sai**; o slide 1 vira o problema | Kluger, Di Tommaso & Lobell (ERL 2025); o primeiro autor também é do MIT (IDSS) | PDF em `artigos/` |
| Vídeo | **Reescrito com 70 palavras**, sem contradição com os portões | Contagem no script | fechamento, I |
| MVP (seção 10) | **Plano de 1 pessoa, ~19 h**: página nova, cartões só de Quixadá, replay estático, AUDIT.md | 29 h úteis contra 32–34 h no plano antigo | `v2_engenheiro_viabilidade_mvp.saida.txt`, F |

Continuam valendo, sem mudança, as linhas da v2 sobre o P2 de janeiro (AUC 0,27 e 0,26 em 2016–2025), o "o que vigiar" do Atlântico (só texto), o ISNA rebaixado a mapa de risco de base, a troca MODIS → VIIRS, o VIIRS como testemunha de junho, o NDVI fora dos portões, as regras R4, R5 e R8 renomeadas para "balde", a faixa de maniva de fevereiro a abril, a S3 enfraquecida, a IA causal não identificável no PAM, o P5 com data fixa, as pragas (ponte verde, grau C), a sentinela com as duplicatas do SMAP e a tabela 4.2 com a escala útil medida.

### R2.4 Os riscos que a banca da rodada 1 deixou

| Risco da rodada 1 | Como ficou | Evidência |
|---|---|---|
| "SMAP pode não chegar" | **Resolvido.** L4 diário e L3 consolidado em disco; o L3 já foi usado na checagem final | fechamento, H |
| Relevância NASA com SMAP/ECOSTRESS só como roteiro | **Resolvido para o SMAP**, agora como segunda missão, com papel medido; o IMERG lido como estado é a luz principal. O ECOSTRESS continua no roteiro | R2.2, linha 10 |
| Números de vitrine que não se reproduzem | **Tratado.** O número-uau foi reproduzido pelo juiz a partir do `.nc` cru; os de 2016 no nível do ano saem de um script só, em 36 s | `v2_juiz_numero_uau.saida.txt`; fechamento |
| Validade local fraca (Quixadá) | **Melhorou, sem virar acerto.** Chuva desde 1/fev: 5 acertos em 9 alertas em 30/abr (contra 3 em 7 da regra antiga); o SMAP continua com 0 acerto; 2023 e 2024 continuam sem assinatura | R2.2, linha 7 |
| Quixadá 2023–25 sem explicação | **Reduzido.** 2025 foi água no fim da quadra; 2023 provavelmente a chuva que parou em maio; 2024 sem assinatura NASA (vai para a Ematerce) | seção 6.2 |
| A regra canônica falhou na última década | **Erro explicado e consertado com dado NASA:** a nova leitura passa nas duas eras | R2.1 |

Os riscos e as críticas da banca da rodada 2 estão na seção 13.2.

---

## 0. Resumo executivo

- **O que é:** o QUADRA trata a rotação no semiárido como uma **política com cinco portões de decisão ao longo do ano**, e não como uma sequência fixa de culturas. Cada estratégia é planejada em **3 anos (2027–2029)**, incluindo o que fica no solo na entressafra.
- **A pergunta científica:** Kluger, Di Tommaso & Lobell (2025, ERL) mostraram, com satélite, mapas de culturas e florestas causais, que o benefício da rotação **muda com o clima**, mas só em quatro celeiros temperados e sem dados de água. O QUADRA leva a pergunta ao semiárido, onde o que decide é **quando** a água aparece, com os dados de água da NASA no centro.
- **Onde ficam os portões:** onde três curvas medidas se cruzam (seção 7, inovação 1). São elas a **habilidade** (o que os dados já sabem, medido deixando o ano inteiro de fora e **sempre por era**), as **opções** (o que ainda dá para plantar) e a **visibilidade** (quando o satélite enxerga, agora com o micro-ondas). Dois portões importam para a demo: **19/mar, o último dia de troca**, e **30/abr, quando só cabe salvar**.
- **O achado da rodada 2:** a forma de **ler** a chuva da NASA decide. A soma desde 1/jan guarda o janeiro chuvoso e falhou em 2016–2025 (30/abr: AUC 0,83 → 0,66 entre as eras). A mesma chuva IMERG contada desde 1/fev se segura nas duas eras (19/mar: 0,74 e 0,71; 30/abr: 0,82 e 0,76). Em 19/mar/2016, a soma acendeu em 7 dos 182 municípios, a chuva desde fevereiro em 182, e 7 em 10 perderam o milho. A água no solo do SMAP L4 confirmou em metade do estado até 30/abr.
- **A regra de 2027 (congelada com hash interno, grau B):** a luz principal é a chuva IMERG desde 1/fev < 75% do normal. O SMAP L4 é a segunda missão, que confirma (vermelho) ou não (amarelo). Em 19/mar, na última década, quebraram 5,3 em 10 no vermelho, 2,1 no amarelo e 0,9 no verde. Os alarmes falsos vão sempre ao lado: em 2022, a chuva acendeu em 142 municípios, o SMAP em nenhum, e 3 quebraram.
- **Como compara:** a prática atual e três alternativas são reencenadas nas 28 quadras do registro IMERG (eras TRMM e GPM, 1998–2025). Onde há dado observado, a comparação é pelo **pior ano**; onde não há (S1, S3), o cartão diz "sem número".
- **O que cabe, quando e em que ordem (novo na v3):** o GAEZ v4 diz o que cabe; o ZARC oficial diz quando plantar e com que risco, e é sempre o limite; os portões da NASA escolhem o ponto dentro da janela; o catálogo de rotações, ponderado pela semelhança de clima medida com o POWER, dá a ordem. O número que transfere para o sertão é +24% para leguminosa antes do cereal solteiro, só no ano colhido (B·T1). Contra o consórcio de hoje, a troca nunca foi medida, e o cartão diz isso. A família da demo recebe um plano por faixas para 2027–2029 (seção 6.4).
- **Quem arbitra:** o rendimento observado do IBGE (PAM). A NASA é o motor; o IBGE é o juiz.
- **O recibo:** cada número traz a missão de origem, a escala, a validação e um grau de evidência de A a D.
- **A escala, dita sem exagero:** os dados acertam **o ano na região**. Entre municípios no mesmo ano, nenhuma camada NASA passa de AUC ~0,65 (o L3 dá 0,645 em 30/abr; o VIIRS, 0,62–0,63), perto do que a geografia sozinha dá (0,61). Por isso a tela diz "seu município / sua região", e a decisão no roçado fecha com a família e o técnico.
- **A SI:** modelos pequenos, guiados pela física, validados por ano e comparados só com a melhor linha de base declarada. Um LLM **só redige** textos, offline, travado por uma checagem de números.
- **Por que agora:** o Pacífico está no **El Niño mais forte já medido para ago–out** (ONI ASO/2026 = +2,46; o máximo anterior era 2,04, em 1997). No El Niño mais forte antes deste, o modelo que deixa o ano de fora dá cerca de **5 em 10 municípios** com quebra do milho, contra 2 em 10 num ano qualquer (faixa de 2 a 8). Os análogos: 1998 e 2016, 7 em 10; 2024, menos de 1 em 10. **Este ano está além do recorde.** A demo é o plano de 2027 de uma família fictícia de Quixadá (CE).

---

## 1. Nome e frase de efeito

**Nome:** **QUADRA**. Na primeira menção do deck e do vídeo: *"QUADRA: the sertão's word for the rainy season"* (fevereiro a maio). Subtítulo: *Field Playbook*. Nome reserva: *Field Replay*.

**Por que não "PROFETA":** o próprio estrategista retirou o nome. Ele promete certeza, que é o que os dados negam, e arrisca soar como apropriação dos profetas da chuva. Eles entram no produto com respeito, no "Checkpoint São José".

**Frase de efeito (PT):**
> "Em janeiro, a chuva que já caiu não diz quase nada, e o oceano diz pouco. Até março, um janeiro chuvoso pode esconder uma quadra fraca. A mesma chuva da NASA contada desde fevereiro, e a água no solo do SMAP, não esconderam 2016; e erram também, por isso o alarme falso vai junto. O QUADRA reencena no seu município todas as quadras que a NASA registrou, compara as rotações pelo pior ano onde o registro deixa e marca os dias em que o dado já sabe o bastante e ainda dá tempo de mudar."

**Frase de efeito (EN, pitch):**
> "In January, rain-to-date says almost nothing and the ocean says a little. By March, a wet January can hide a dry season; NASA's water-state readings, rain counted from February and SMAP soil moisture, did not hide 2016. QUADRA replays every rainy season NASA has recorded over your county, compares rotations by their worst years where the record allows, and marks the checkpoints where the data know enough and there is still time to switch."

**Frase de mecanismo (EN, sempre com 2022 ou 2021 ao lado):** *"Rain counted from January remembers a wet January. Rain counted from February doesn't."* **Proibido:** "the soil does not fool you", "o solo não engana" e "rain-to-date remembers January; the soil doesn't". Em 2016, o SMAP só acendeu de verdade na última semana de abril (10 de 127 quebras em 15/abr; 64 em 30/abr).

**Tagline (EN):** *Replay every rainy season NASA has recorded over your county. Decide at the right checkpoint.*

**Frase-ponte com o artigo-âncora (EN):** *"Kluger, Di Tommaso & Lobell (ERL 2025) showed that which rotation pays depends on climate. In the semi-arid, it depends on when the water shows up."*

**De onde vem cada peça** (placar consolidado do conselho: média dos 9 avaliadores externos; ver `ata_do_conselho.md`):

| Peça | Origem | Por que entra |
|---|---|---|
| Rotação como política com portões | Agrônomo, "Playbook do Roçado" (8,4) | Esqueleto mais votado. Seis propostas chegaram a ele de forma independente. |
| Replay das quadras observadas, ranking pela cauda | Pesquisador de IA, "SeasonReplay" (8,3) | Torna a comparação concreta: "o que teria acontecido em 1998 no seu município". |
| Recibo A–D, auditoria, sentinela de deriva, duas escalas | Cético, "FieldProof" (8,3) | É a espinha do critério Validade. |
| Calendário, São José, 2027 ao vivo | Estrategista, "PROFETA" (8,1) | Leitura do júri e eixo do storytelling. |
| Oceano como camada própria, aviso de caso inédito | Clima, "ShiftCast" (7,9) | Diz o que o mar informa em novembro e o que não informa. |
| Pior ano, correlação entre culturas, carteira | Economista, "CropFolio" (7,9) | É a métrica que importa para a família. |
| Frequências naturais, técnico no circuito, termômetro do solo | Designer, "Compadre" (7,5) | Resolve a adoção; na rodada 2, o termômetro com o estado "dormindo". |
| Dois relógios da água, salvamento contra irrigação na seca | Hidrólogo, "Extrato d'Água" (7,4) | Linha "conta de água" e relógio lento; na rodada 2, a segunda régua do SMAP. |
| Selo de visibilidade, escala útil medida | Sensoriamento remoto, "FieldMemory" (6,2) | Terceira curva, agora com o micro-ondas. |
| Portão de entressafra (fogo, palhada, ciclo de praga) | Ecólogo, "CycleBreak" (6,1) | Preenche o portão que as outras propostas deixaram vazio. |

---

## 2. O problema

### 2.1 No Ceará, com os nossos dados

1. **Uma janela, uma chance.**
   - 77,5% do Ceará comporta uma única safra de sequeiro (GAEZ; `notebooks/secoes/90_sintese.py`, 90.2).
   - A estação vai de cerca de 2/fev a 28/jul, com pico em abril. O solo fica exposto de setembro a janeiro (MODIS; mesma seção).
   - A evapotranspiração de referência supera a chuva em **10 de 12 meses**, tanto no POWER quanto no ERA5 (`arquiteto_final_curvas_quixada.saida.txt`, bloco D). No ano, a ET0 vai de 1.970 mm (ERA5) a 2.280 mm (POWER), ou 2,5 a 2,8 vezes a chuva da mesma fonte.
   - **Novo:** na entressafra (ago–dez), o primeiro metro de solo do SMAP fica perto do piso em metade dos dias (W < 0,1 em 49% dos dias, numa escala em que 0 é o p2 e 1 é o p98 do próprio município) e em nenhum dia chega à metade da faixa (`v2_agronomo_smap_janelas.saida.txt`, bloco E).
2. **O sistema dominante concentra o risco.**
   - Milho e feijão ocupam 91% da área das lavouras **temporárias** (PAM 2017; Rocha et al. 2021). Com as lavouras permanentes, 66,2% (62,4% em 2025).
   - No registro do PAM, as duas culturas quebram juntas. A correlação mediana das anomalias no mesmo município é **0,78** (183 municípios, 1998–2025). Tirando o choque comum do estado no ano, ainda é 0,67 (`cetico_r3_refutacoes.saida.txt`, bloco F).
   - Ressalva: parte do co-movimento pode ser o mesmo relato municipal. Em Quixadá, o feijão de 2005 é cópia exata do de 2003.
3. **A quebra é frequente e sincronizada.**
   - **Definição canônica de quebra:** produção ÷ área plantada abaixo de 50% da mediana do próprio município nos *outros* anos.
   - O milho quebrou em **21,5%** dos 5.106 município-anos de 1998–2025.
   - Fração de municípios em quebra: 75% em 1998 e em 2012, 70% em 2016 e 61% em 2010. O rendimento estadual do milho caiu 69% em 2012 (`arquiteto_numeros_canonicos.txt`, bloco D).
   - Cerca de metade da variância da quebra municipal é choque comum ao estado no ano: 45–53% no milho (`cetico_escala_vazamento.py`).
4. **O El Niño pesa, mas não decide sozinho.**
   - Dos 6 El Niños desde 1998 (ONI de NDJ ≥ 1,0), **3 viraram catástrofe**: 1998, 2010 e 2016, com 61% a 75% dos municípios em quebra. **Três passaram sem quebra**: 2003, 2019 e 2024, com 1% a 8% (`cetico_r3_refutacoes.saida.txt`, bloco A).
   - **Modelo único, pré-declarado no script do clima:** a logística P(quebra municipal) ~ ONI ASO do ano anterior, validada deixando o ano inteiro de fora, tem BSS de +0,063 no município (IC90 −0,07 a +0,18) e ρ de +0,39 com a fração de municípios em quebra (p = 0,038; n = 28). O sinal é real no nível do ano e pequeno (`v2_clima_portao_novembro_2027.saida.txt`, bloco B). Por era, a AUC do ONI é 0,66 em 1998–2015 e 0,72 em 2016–2025 (`v2_arquiteto_r2_fechamento.saida.txt`, bloco A).
   - Os El Niños fortes foram "tudo ou nada": o modelo previu cerca de 0,5 para 1998, 2016 e 2024, e o observado foi 0,75, 0,70 e 0,08 (mesmo arquivo).
   - Com erro-padrão agrupado por ano, o efeito do El Niño "além da chuva" **não é significativo**: OR 1,57, IC95 0,71–3,50 (`cetico_memoria_grace_neff.saida.txt`, bloco A). Grau B.
5. **O solo fica nu e queima.**
   - 72,9% dos focos de fogo VIIRS de 2015–2025 caem em out–dez; até 30/set, só 27% (`v2_ecologo_calendario_fogo.saida.txt`).
   - 17% da área do Ceará está em células de ~375 m com ao menos um foco VIIRS em 2012–2025. Isso não é área queimada: um roçado de 1 ha acende uma célula de 14 ha.
   - A medida de área vem do Landsat a 30 m: 12,7% da Caatinga queimou em 1985–2023 (Franca Rocha et al. 2024). O resumo do artigo não cita o nome "MapBiomas Fogo", que fica a conferir no texto completo. O MCD64A1 da NASA vê só 4,9% do CE queimado em 2001–2025: é um piso.
6. **Em janeiro, a chuva que já caiu não diz quase nada; até março, a soma desde janeiro pode enganar.**
   - A chuva IMERG acumulada até 31/jan separa a quebra do milho com AUC de apenas 0,57 (IC90 0,43–0,68). Em Quixadá, janeiro de 1998 teve 150% do normal e janeiro de 2016 teve 197%. Os dois anos foram de quebra.
   - O oceano diz um pouco: o ONI de ASO, publicado no início de novembro, tem AUC de 0,67 (IC90 0,53–0,78) para a quebra municipal (`arquiteto_final_curvas_quixada.saida.txt`, bloco A).
   - **A soma desde 1/jan guarda o janeiro.** Em 30/abr, a AUC dela é 0,83 em 1998–2015 e cai para 0,66 em 2016–2025, quando o alerta acende menos onde quebra do que onde não quebra (1,1 contra 1,5 em 10). Janeiro foi 34% da chuva de jan–mai em 2016 e 28% em 2025, contra a mediana de 12% (`v2_arquiteto_arbitragem_smap.saida.txt`, bloco E; `v2_economista_janela_alerta.saida.txt`).
   - **A mesma chuva contada desde 1/fev** não guarda o janeiro: 0,82 e 0,76 em 30/abr; 0,74 e 0,71 em 19/mar, nas duas eras (`v2_arquiteto_r2_fechamento.saida.txt`, bloco A).
   - **Novo: o início da estação também engana em El Niño forte.** O início pela chuva (IMERG; a partir de 1/dez, o 1º dia com ≥ 20 mm em 3 dias sem veranico de 10 dias secos nos 30 dias seguintes) foi medido por município de 1999 a 2026. Nos 3 anos de El Niño forte da série (2010, 2016 e 2024), a chuva começou **antes**: mediana no dia 6, contra o dia 18 nos anos neutros (sem La Niña) e o dia 15 em todos os demais anos (n = 3 anos; o p por município-ano é otimista). Em 2010 e 2016 a quadra falhou (61% e 70% dos municípios com quebra do milho); em 2024, não (8%). O início sozinho não protege, e por isso a decisão fica nos portões de março e abril (`notebooks/secoes_analogos/05_ciclo_plantio.py`). **O sinal muda de município para município:** 129 municípios do CE tiveram início mais cedo (> 5 dias), 34 mais tarde e 13 igual (`notebooks/secoes_prototipo/07_imerg_inicio.py`). Em Quixadá, nos mesmos 3 anos, o início veio 24 dias depois do típico (2010: 19/03; 2016: 06/01; 2024: 12/02; mediana 12/02, contra 20/01 em 1999–2026). Com n = 3, isso não se separa do acaso: 14% das triplas de anos sem El Niño forte dão diferença ≥ 24 dias (permutação; `protótipo/REVISAO_10_AGENTES.md`, A17). Por isso o cartão mostra os anos do próprio município, sem tirar regra deles (protótipo, `protótipo/motor.py`, função `inicio_estacao`).

### 2.2 Por que as ferramentas atuais não resolvem

- O **ZARC** dá a janela de plantio de uma cultura, mas a janela não muda com o ano. E a prática atual nem sempre cabe nela: em Quixadá, o ZARC 2026/27 só zoneia alguma cultura a partir de 21/jan (a 40%), o risco de 20% só aparece em 11/fev, e o milho só entra em 11/fev, quando a família costuma plantar na 1ª chuva de janeiro (a conferir na portaria; `proposta/estrutura_gaez_zarc.md`, seção 5).
- O **prognóstico de tercis** não vira decisão de rotação.
- **Painéis de NDVI** mostram o passado e não comparam estratégias. E o óptico fica cego justamente nos portões: só 39–40% dos pixels do Ceará têm NDVI VIIRS bom ou marginal no mês em jan–mar (`v2_sr_fundacao_viirs_portoes.saida.txt`, bloco A).
- O **percentil pronto de umidade do solo** do SMAP L4 não existe no sertão de agosto a meados de janeiro. E a **média sazonal** desses percentis (fev–mai) comprime a escala: acende em 0,7% dos municípios e não pega nenhuma das 127 quebras de 2016. O mesmo produto lido no portão (média de 7 dias) pega 64 (`v2_cetico_r2b_gatilho_carteira.saida.txt`, bloco 1). Usar o dado da NASA exige saber **como e quando lê-lo**, e testar a leitura contra o IBGE.
- Marengo et al. (2022) mostram que a adaptação à seca no Nordeste ainda é quase toda **pós-desastre**.
- Dury et al. (2012) mostram que o plano de cultivo real é dinâmico e adaptativo, mas os modelos o tratam como estático.
- No Ceará, previsões comunicadas como certeza já custaram a confiança dos agricultores. Em 1997, a previsão "abaixo da média" foi lida como seca, e a FUNCEME perdeu credibilidade (Finan & Nelson 2001, p. 105). Lemos et al. (2002) mostram a distorção e a má interpretação da previsão (fora da revisão; DOI conferido no Crossref na rodada 1).
- **A ciência de rotação com satélite** (Kluger et al. 2025; Zhou et al. 2024; Beal Cohen et al. 2019) estuda celeiros temperados com mapa de culturas por pixel e sem dados de água. O semiárido de sequeiro, sem mapa oficial de culturas, fica de fora. **Novo:** pela assinatura de clima do POWER, esses celeiros (Corn Belt, Europa, Ontário e Pradarias) têm peso w = 0,00 para Quixadá, e nenhum ensaio de rotação no tempo do catálogo vem de clima de sertão (`notebooks/secoes_analogos/06_motor.py`).

### 2.3 Por que agora

- O **ONI ASO/2026 é +2,46**, o maior valor para ago–out desde 1950. Os anteriores foram 2,04 (1997) e 2,02 (2015). Não é o recorde absoluto: o maior ONI de qualquer trimestre foi 2,59, em NDJ 2015 (`arquiteto_numeros_canonicos.txt`, bloco A).
- **O ano de 2027 está fora da distribuição.** O 2,46 está 0,42 acima do máximo das quadras de 1982 a 2026 (2,04). No máximo já visto, P(quebra municipal) = 0,54 (IC90 0,24–0,75); em 2,46, 0,62 por extrapolação, e o valor muda de 0,53 a 0,72 conforme o análogo retirado (`v2_clima_portao_novembro_2027.saida.txt`, blocos B e E).
- **O Pacífico dificilmente esfria a tempo:** só 1 dos 7 El Niños fortes desde 1951 chegou a FMA ≤ 0,5 (1988; IC90 0,01–0,52) (mesmo arquivo, bloco F). O boletim do CPC de 12/11/2026 ("El Niño Advisory") dá chance maior que 79% de El Niño forte a muito forte até jan–mar/2027 e de ~60% de evento histórico (≥ +2,5 °C) em out–dez e nov–jan (`pesquisa/el_nino_2026_nordeste.md`).
- **O estado de hoje é normal e não prevê a quadra:**
  - banco regional de água normal: GRACE do Ceará na média de jul–set/2026 no percentil 57 (`cetico_r3_refutacoes.saida.txt`, bloco E); água subterrânea do GLDAS-2.2 CLSM em jun–ago/2026 no p74, com o aviso de que o CLSM assimila o GRACE (`v2_estrategista_painel_hoje.saida.txt`);
  - solo no piso, como todo novembro: zona da raiz do SMAP L4 no CE em 0,121 m³/m³ em 10/11/2026, o 5º mais seco de 12 novembros (`v2_clima_smap_estado_inicial.saida.txt`);
  - estação seca normal: 5,7 mm de 01/ago a 13/nov, 81% da mediana, posto 13 de 29 (`v2_clima_estacao_seca_2026.saida.txt`).
- **O Nordeste entra em 2027 com solos diferentes (novo):** na zona da raiz do SMAP L4 (30 dias até 10/11, posição entre 12 anos; 1 = o mais seco), o Maranhão e Sergipe estão em 1º, o novembro mais seco da série; Piauí e Pernambuco em 2º; Alagoas e Bahia em 3º; Paraíba e Rio Grande do Norte em 4º. **O Ceará está em 5º, normal.** Para comparar: na entrada de 2015, o CE ficou em 2º; na de 2023, em 7º. A água no solo de novembro não prevê a quadra; o risco de 2027 vem do oceano (`pesquisa/el_nino_2026_nordeste.md`).
  - **Correção da rodada 3:** a 1ª versão de `pesquisa/el_nino_2026_nordeste.md` dizia "CE 18 contra 25 e 28", pelo percentil pronto do SMAP. Esse campo quase não existe no Nordeste nessa época (menos de 0,5% das células do Ceará de out a jan). Saiu.
- **A quadra de 2026 foi boa** (698 mm, 120% da mediana, posto 22 de 29), e a caatinga de out/2026 está mais verde que em 12 de 14 outubros (VIIRS, z +1,07). Há combustível no chão (`v2_clima_estacao_seca_2026.saida.txt`; `v2_estrategista_painel_hoje.saida.txt`). **Mas isso não vira previsão de fogo:** no CE, os 6 anos "úmido e depois seco" de 25 não queimaram mais (−0,16 no log da área sobre a tendência; p unilateral 0,66). O sinal com a chuva do ano anterior é fraco (focos MODIS de jul–dez, ρ +0,36; p = 0,07) (`pesquisa/viabilidade_artigos_nordeste.md`, 4.3, linha 836).

### 2.4 Por que importa no mundo

- O problema "uma janela de chuva, falso início e data-limite" é o mesmo no Sahel, no Chifre da África, na Índia de sequeiro e no semiárido do Texas. No Texas, o CDL mostra 67% de algodão contínuo (síntese 90.2, item 11).
- **Novo: onde o sertão se repete no planeta.** Pela assinatura de clima do POWER numa grade global de 6°, só 19 de 387 pontos de terra têm distância < 1,5 do Sertão Central, e só 2 ficam abaixo de 1. Os mais parecidos são o próprio Ceará (0,22), o Chaco argentino (0,77), o Oeste da Bahia e o norte da Austrália (1,01), Burkina Faso (1,04), o sudoeste de Madagascar (1,05) e o Deccan (1,15); logo depois vêm o Benim, o Zimbábue, o México, o Sudão do Sul, a Namíbia, Moçambique, o norte da Nigéria, o Pantanal e Angola. É onde a QUADRA funciona com a mesma lógica e onde vale procurar ensaios de rotação. Com a Tmax média, o norte de Minas (1,59) e o norte da China saíram: os 20 mais parecidos ficam entre 30°S e 24°N. A grade é indicativa (`notebooks/secoes_analogos/03_sertao_no_mundo.py`).
- Na amostra global do POWER (2020), **40 dos 47 pontos terrestres tropicais amostrados** não têm nenhum mês em que o frio interrompa o ciclo da lagarta-do-cartucho, contra 7 meses em Iowa (`arquiteto_final_curvas_quixada.saida.txt`, bloco E). Onde não há inverno, só a rotação e a entressafra quebram o ciclo. No Ceará, o relógio térmico deu 4,3 a 4,6 gerações potenciais da lagarta entre 1/ago e 12/nov em todos os anos de 2012–2025 (`v2_ecologo_ponte_verde_pragas.saida.txt`, bloco 4).
- O núcleo de dados do QUADRA é global. O SMAP L4 cobre 99,6% da terra entre 60°S e 60°N na amostra de 15/04/2025 (`smap_global_amostra_2025-04-15.nc`; seção 05). Atenção: não sabemos se o percentil pronto também some na seca de outras terras áridas; a amostra global não tem percentil.

---

## 3. A solução: o que o técnico e a família veem e fazem

### 3.1 Dois usuários, um motor

- **Extensionista (técnico de ATER, cooperativa, ONG):** é o usuário principal do MVP. Usa um painel web estático que funciona offline depois de carregado. Escolhe o município da família, lê os portões, compara as estratégias e vê a evidência completa.
- **Família agricultora:** recebe do técnico um **cartão em imagem** com no máximo 3 números, em frequências naturais ("de cada 10 municípios, 4 perderam mais da metade do milho"), sempre com "na sua região" e o número de anos ao lado. A família informa a data de plantio e as prioridades, e pode vetar uma sugestão.
- O cartão com áudio e o envio pelo WhatsApp ficam no roteiro. No MVP, o cartão é uma imagem que o técnico mostra.

### 3.2 As telas do MVP (três, numa página estática nova) e o que fica para depois

A página é escrita do zero (`index.html` com JS puro e uma biblioteca de gráficos mínima, sem API ao vivo). Do `site-nasa/` antigo aproveita-se no máximo o CSS. Os **cartões completos existem só para Quixadá**; nos outros 183 municípios aparecem o Relógio e o placar.

1. **Relógio da Quadra** (tela principal).
   - Seletor com os 184 nomes (`ceara_municipios_nomes.json`) e um mapa estático do Ceará.
   - **As três curvas** como tabela estadual fixa, **sempre por era**: habilidade (chuva desde 1/fev, regra antiga desde 1/jan, SMAP e oceano), opções (datas-limite de milho e caupi) e visibilidade (óptico e micro-ondas).
   - Dois portões destacados: **19/mar, o último dia de troca**, e **30/abr, só salvar**. Os outros três (nov, jan–fev e entressafra) aparecem como marcos de texto.
   - Para cada portão:
     - o que o dado já sabe, em frequência natural e com o n;
     - o que ainda não sabe;
     - o que ainda dá para fazer;
     - o placar **deste município** para a chuva desde 1/fev e para o SMAP, com acertos, alarmes falsos e quebras perdidas.
   - **Luz em quatro estados**:
     - **vermelho:** chuva desde 1/fev < 75% do normal **e** SMAP < 20;
     - **amarelo:** só a chuva;
     - **cinza-amarelo:** só o SMAP ("os instrumentos discordam; o técnico decide");
     - **verde:** nenhuma das duas.
   - **Termômetro do solo** (SMAP L4, média de 7 dias): dormindo, verde, amarelo ou vermelho, como na v2.
   - **Painel "hoje"** (14/nov/2026), com 4 itens copiados da folha 9.7 num JSON fixo:
     - ONI +2,46, com o selo "além do recorde" e os análogos (1998, 2016, 2024);
     - termômetro DORMINDO, Quixadá a 0,087 m³/m³ e o estado em 5º de 12 novembros ("normal para a época");
     - GRACE no p57 (jul–set): banco regional normal;
     - caatinga em out/2026 (VIIRS z +1,07; 3º outubro mais verde de 15): "mais combustível; não queimar".
2. **Cartões de estratégia (só Quixadá, textos congelados, ordem fixa).**
   - A atual (S0) e três alternativas (S1–S3), cada uma como **sequência 2027–2028–2029**, com a entressafra.
   - Os 5 campos do desafio: por que foi sugerida, evidência com recibo, benefícios, lacunas e riscos a confirmar com o técnico.
   - **Números só onde existem** (seção 6.2):
     - S0 com as 3 métricas do município ("seu município");
     - S2 com as do estado ("estado", teto e piso);
     - S1 com o contrafactual da metade guardada (grau C) e "sem número" no pior ano;
     - S3 "sem número de pior ano"; o efeito do antecessor como "+24% no ano colhido, contra milho solteiro (B·T1); contra a sua prática atual, não medido" (6.2).
   - **Novo:** cada cartão mostra a janela do ZARC oficial 2026/27 de Quixadá (risco por solo e ciclo) e a aptidão GAEZ como rótulo, mais o peso de clima w do estudo citado.
   - **Novo:** o plano da família por faixas, 2027–2029 (seção 6.4), entra como texto congelado no cartão da família, sem tela nova.
   - Os pesos da família reordenando os cartões ficam para a próxima versão.
3. **Replay (estático, com um controle de data).**
   - **1998:** em 10/mar, 19/mar e 30/abr, a chuva desde 1/jan e desde 1/fev. Depois, o balde do caupi (grau C) e o IBGE revelado na colheita.
   - **2016:** as mesmas datas, mais o SMAP e o verde do VIIRS de abr–mai como testemunha, e o IBGE no fim.
   - Sem M2, sem trajetórias animadas e sem barras de ISNA diárias.

**Fora das telas do MVP:**
- A **auditoria** vira um `AUDIT.md` no repositório (o GitHub renderiza), com as tabelas R2.2 e 9.2 e links para os `.saida.txt`. Ela inclui o gatilho tipo Garantia-Safra (marcado "refazer com a mesma escala"), as 5 leituras da chuva lado a lado, o placar das duas eras e os nulos.
- Ficam no roteiro: o código de barras do talhão ao vivo, áudio, simulador de WhatsApp, modo global, SMAP ao vivo, pesos da família e o emulador M2 na tela. Do modo global, fica 1 linha: "o SMAP L4 cobre 99,6% da terra entre 60°S e 60°N".
- **Novo (14/11, tarde): o protótipo "escolha o lugar"** (`protótipo/`) já cobre os 1.794 municípios do Nordeste: cardápio GAEZ + ZARC com janela por solo, regime e início da chuva, El Niño medido no próprio município e plano por faixas. O número do catálogo só aparece em cartões T0/T1 (`protótipo/README.md`; R3.5).

### 3.3 Fluxo de uso ao longo do ano

| Quando | O técnico faz | A família recebe ou faz |
|---|---|---|
| Primeira visita | Escolhe o município. Confirma a prática atual (o Censo Agropecuário 2017 sugere; 1 pergunta confirma). Pergunta o solo do roçado, porque a janela do ZARC depende dele. Registra rebanho, semente guardada, maniva, mão de obra e água guardada. | Cartão de apresentação: "o QUADRA não sabe tudo; aqui está o que ele sabe". |
| **P1, nov–dez** | Lê o oceano e o banco de água. O termômetro do solo está dormindo, e isso é dito. | Ações sem arrependimento: semente de caupi precoce até dezembro, maniva guardada, palma, adesão ao Garantia-Safra, não queimar, aceiro. |
| **P2, jan–fev** | Lê a chuva recente; o termômetro acorda em meados de janeiro (~12/jan). Em 28/fev: "ainda é cedo". Confere a data com o ZARC: em Quixadá, o ZARC 2026/27 só zoneia alguma cultura a partir de 21/jan (a 40%), o risco de 20% só aparece em 11/fev, e o milho só entra em 11/fev (a conferir). | "Plante uma parte agora e guarde a outra." A família informa a **data de plantio**. Se ela cair fora do ZARC, o cartão avisa (texto em aberto; proposta da estrutura: "sua data de plantio está fora do ZARC"). |
| **Início de março (~10/mar), só em ano de El Niño forte** | Lê a chuva desde 1/fev e o SMAP (leitura descritiva, sem habilidade medida). | Se a luz estiver acesa, a metade guardada vai para o caupi até ~11/mar, **se o técnico confirmar que ainda há umidade para a semente**. Num ano como 2016, o caupi de 11/mar teve água na floração em 7 de 10 municípios; num como 1998, em 1 de 10 (balde, grau C). Se estiver verde (como em 2024), a metade guardada segue o plano normal. |
| **P3, 19/mar ("Checkpoint São José")** | Lê a luz em quatro estados. | Vermelho ou amarelo: caupi só se ainda couber (até ~21/mar em ano normal); **sem sorgo de grão na troca**. Cinza-amarelo: "os instrumentos discordam; o técnico decide". |
| **P4, 30/abr** | Lê a luz de novo; é quando o SMAP mais confirma. | Ação graduada: guardar forragem, cortar o milho para os animais se o técnico confirmar, segurar a venda dos animais. |
| **Junho** | Lê o verde do satélite (VIIRS) como primeira leitura da safra. | "O IBGE confirma no ano que vem." |
| **P5, até 31/ago (data fixa)** | Mensagem de prática: o fogo segue o calendário da broca, não a secura do solo. Mapa da "ponte verde" para armadilhas. | Palhada em vez de fogo, fenação do excedente, aceiro, perene em nível. |
| Fim de safra | Registra o resultado, faixa por faixa. | A família ordena os caminhos que testou. Isso gera evidência local de rotação, que hoje não existe. As faixas que trocam de lugar (seção 6.4) são o ensaio que falta no catálogo. |

### 3.4 Glossário em pop-up (exigência do desafio)

- **Evapotranspiração (ET/ET0):** a água que o solo e a planta devolvem ao ar. A ET0 é a de uma grama de referência.
- **Balanço hídrico:** a chuva que entra menos a água que sai, dia a dia.
- **Anomalia de umidade:** quanto o solo está acima ou abaixo do normal daquela época.
- **Zona da raiz:** a camada de 0 a 100 cm do SMAP L4, onde a planta busca água.
- **Termômetro do solo:** o percentil da zona da raiz do SMAP L4 na média dos 7 dias. "Dormindo" quando o produto não calcula o percentil (de agosto a meados de janeiro, no sertão).
- **NDVI:** o quão verde e vigorosa a vegetação está, vista do satélite.
- **Geada:** temperatura mínima ≤ 0 °C. Só aparece fora do Ceará, onde se aplica.
- **ISNA:** a fração da água de que a cultura precisou e que de fato recebeu.
- **"Pior ano em 10":** a média dos 10% piores anos (CVaR10).
- **"% do normal":** a chuva no período dividida pela mediana dos outros anos no mesmo município. Na estação seca, a tela usa mm e posto, nunca "% do normal" (398% sobre 1 mm engana).
- **"Chuva desde 1/fev":** a luz principal do QUADRA. Conta a chuva a partir de 1º de fevereiro, porque um janeiro chuvoso pode esconder uma quadra fraca.
- **"Segunda missão":** o SMAP, que mede a água no solo por micro-ondas e confirma, ou não, o que a chuva diz.
- **"Seu município / sua região":** "seu município" é onde o número foi medido; "sua região" é onde contamos quantas vezes ele acertou, ano a ano, porque a seca atinge a região inteira de uma vez.
- **ZARC (novo):** o Zoneamento Agrícola de Risco Climático do Ministério da Agricultura. Para cada município, cultura, solo e ciclo, diz o risco de perda (20%, 30% ou 40%) em cada decêndio (período de 10 dias).
- **GAEZ (novo):** o mapa de aptidão das culturas da FAO (nota de 0 a 100). Diz o que cabe no lugar, em clima médio.
- **Peso de clima w (novo):** quanto o clima do lugar de um estudo se parece com o do seu município, de 0 a 1, pela assinatura do NASA POWER. Perto de 1, o estudo foi feito num clima muito parecido; abaixo de 0,3, "nenhum estudo de clima parecido".
- **Tampão (novo):** a faixa de mandioca plantada no ano anterior, colhida conforme a necessidade no ano seco.
- **Revezamento (novo):** semear a segunda cultura no meio da primeira, antes da colheita (ex.: caupi 50–85 dias depois do milho).
- **Percentil.**
- **Grau de evidência A–D.**

### 3.5 Apoiar, não substituir

- No MVP, a ordem dos cartões é fixa. Na próxima versão, os pesos vêm da família.
- O técnico aprova toda mensagem.
- A família pode vetar ("não quero caupi"). No MVP, o cartão mostra a alternativa seguinte; recalcular o custo da escolha fica para a próxima versão.
- **As datas-limite vêm do ZARC oficial 2026/27, que é sempre o limite** (regra decidida em 14/11; `proposta/estrutura_gaez_zarc.md`, seção 6). Se o solo for desconhecido, o cartão mostra a faixa entre o solo mais restritivo e o mais permissivo, e o técnico confirma o solo. A **janela sintética tipo-ZARC** (IMERG + POWER) fica como checagem no Brasil e como a camada global fora dele. Os portões da NASA escolhem o ponto **dentro** da janela.
- Quando a chuva e o solo discordam, o cartão diz "os dois instrumentos discordam; o técnico decide", sem número. Foi o que aconteceu em 2022: chuva baixa em 142 municípios, solo normal em todos, e 3 quebras.
- Todo cartão termina com "o que confirmar no chão com o técnico".
- **Freio de segurança:** sem restrições, o otimizador de renda bruta escolhe "100% mandioca" em todos os municípios (`pesquisador_ia_conformal_carteira.py`). É o exemplo de por que a ferramenta apoia e não decide.
- **Freio da transferência (novo):** se o estudo mais parecido com o município tem peso de clima w < 0,3, o recibo diz "nenhum estudo de clima parecido" e rebaixa o grau (`notebooks/secoes_analogos/06_motor.py`). Com a Tmax corrigida (R3.5), nenhum município do CE fica abaixo de 0,3 no melhor análogo (os menores são Paracuru e São Gonçalo do Amarante, 0,38), e a Região Metropolitana de Fortaleza passou de 0,31 para 0,75. O freio continua valendo para os números de rotação: nenhum número T0/T1 tem w ≥ 0,3 em Quixadá. No protótipo, o rebaixamento do grau ainda está só em parte (revisão M15).

---

## 4. Arquitetura: núcleo global de dados NASA e enriquecimento local

### 4.1 Visão geral

```
        NÚCLEO GLOBAL                                               ENRIQUECIMENTO LOCAL (quando existe)
 [luz]     IMERG V07 diário 0,1° (TRMM 1998–2014, GPM 2014→): chuva desde 1/fev    Brasil: IBGE PAM (árbitro), ZARC oficial
 [2ª missão] SMAP L4 v008 zona da raiz 9 km (2015→): confirma a luz                 2026/27 (limite), Garantia-Safra (lei
 [checagem] SMAP L3 v006 (radiômetro; consolidado até 12/11/2026)                   conferida), Censo 2017, LSPA (em disco)
 [na tela]  VIIRS VNP13A3 (testemunha de junho; caatinga), GRACE/GRACE-FO, SRTM     Mundo: FAO GAEZ v4 (o que cabe)
 [repositório] POWER, GLDAS-2.1/2.2, MODIS, Landsat/HLS, NEX-GDDP, focos VIIRS      EUA: CDL/CSB, NASS, NLDAS-2 (em disco)
 [análogos] POWER: assinatura de clima → peso w de cada estudo do catálogo         Família: data de plantio, solo, água
 [roteiro]  ECOSTRESS/ESI · Prithvi-EO-2.0 · NISAR (com regra de validação pré-declarada)   guardada, maniva, veredito de fim de safra
                  │                                                   │
                  ▼                                                   ▼
   GRADE COMUM + ESCALA ÚTIL MEDIDA ─► exportador (lê os parquets já salvos; 0,4 s) ─► JSON por município
        ─► Relógio (3 curvas por era, luz em 4 estados) ─► Cartões de Quixadá + recibo ─► Replay estático 1998 e 2016 (IBGE arbitra)
```

**Novo na v3, as quatro perguntas do agricultor** (`proposta/estrutura_gaez_zarc.md`, seções 2 e 6):

| Pergunta | Quem responde | Regra |
|---|---|---|
| O que cabe aqui? | FAO GAEZ v4 (aptidão de 0 a 100; clima de 1981–2010; pixel de ~9 km) | Onde há ZARC, o GAEZ é só rótulo. Ele filtra sozinho só as culturas sem ZARC na tábua do CE (mandioca, guandu, milheto), com aptidão > 40 (classe "média" ou melhor da camada oficial da v4) em sequeiro e insumo baixo. Nos perímetros irrigados, insumo alto |
| Quando plantar e com que risco? | ZARC oficial no Brasil; fora dele, ZARC sintético com IMERG + POWER | O ZARC decide e é sempre o limite. Com o GAEZ como corte (> 40), 632 pares município × cultura que o ZARC indica com 20% de risco cairiam, em 152 municípios (com o corte antigo, > 35: 494 em 127); são serras, litoral e várzeas do Jaguaribe |
| Este ano está normal? | Portões da NASA (chuva IMERG desde 1/fev, SMAP L4, VIIRS) e ONI | Escolhem o ponto dentro da janela do ZARC |
| Em que ordem plantar? | Catálogo de rotações (147 cartões), ponderado pelo peso de clima w do POWER | Número só com T0 ou T1; T2 só como direção |

### 4.2 Grade comum, escala útil e regras de harmonização

A coluna nova, "escala útil medida", é a menor escala em que dois sensores independentes concordam nas anomalias com r ≥ 0,8 (regra pré-declarada pelo especialista em sensoriamento remoto; `v2_sr_fundacao_escala_real.saida.txt` e `v2_sr_fundacao_smap_l3_l4.saida.txt`, bloco B). O município mediano do Ceará tem 632 km², ou 25 km de lado.

| Camada | Resolução nativa | Escala útil medida | Como entra na grade comum | Regra de uso |
|---|---|---|---|---|
| IMERG | 0,1° (~11 km), diário | Nunca chega a r 0,8 contra o SMAP L3 (0,57 a 11 km; 0,63 a 88 km): vale para o **ano e a região** | É a **grade de decisão**. Agregada ao polígono do município para calibrar contra o PAM. | **Luz principal: chuva desde 1/fev por portão**, sempre mostrada por era (1998–2015 e 2016–2025). A soma desde 1/jan fica como regra antiga, no replay e na auditoria. Na estação seca, mm e posto. O Late e o IMERG via POWER são o mesmo dado na sobreposição de 01/ago a 14/set/2026 (razão 1,00; r 1,00; `v2_clima_estacao_seca_2026.saida.txt`): o Final V07 termina em 30/09/2025, e o que vem depois é Late, preliminar. **No litoral leste**, o IMERG capta só 39–72% da chuva das 17 automáticas do INMET a menos de 20 km do mar (fora o litoral norte do RN); ali, as datas vêm do ZARC. O regime do litoral leste (estação de mar–jun ou abr–jul) cobre 312 municípios (R3.5, F). |
| SMAP L4 (SPL4SMGP v008) | 9 km, granulo diário das 13:30 UTC | Diz **quando** a 9 km (r temporal com o L3 de 0,89 por célula) e **onde** a partir de 36 km (r das anomalias 0,824) | Média das células de 9 km com centro no município (mediana de 8 células; Quixadá tem 25). | **Segunda missão: percentil da zona da raiz, média dos 7 dias até o portão; < 20 confirma a luz.** De ~12/ago a ~12/jan o percentil do produto vem vazio no sertão: aí entra o **percentil próprio** (posto entre os anos desde 2015, com o n) e o nível absoluto. Nunca a **média sazonal** de percentis (comprime a escala) e nunca limiar absoluto em m³/m³ (cinco estimativas NASA da água na raiz diferem até 0,10 m³/m³; `v2_hidrologo_cinco_fontes_umidade.saida.txt`). Deduplicar as 4 datas repetidas. |
| SMAP L3 (SPL3SMP_E v006) | Pegada do radiômetro de ~40 km, postada numa grade de 9 km; AM e PM | Igual ao L4 (r 0,89 na anomalia diária do estado) | Só checagem | Qualidade recomendada (bit0 = 0); deduplicar as 7 datas repetidas do consolidado. A célula mediana é vista em 13–15 dias por mês, na quadra e na seca; 93,5% das células-mês têm ao menos 4 dias vistos. |
| POWER | 0,5°, diário | — | Célula válida mais próxima de cada célula IMERG. | Sempre como **anomalia ou percentil por fonte**. A ET0 do POWER fica ~15% acima da do ERA5 (seção 9.7). **Corrigido na v3:** contra 16 estações automáticas do INMET no CE, a Tmax do POWER tem viés de só +0,14 °C (+0,46 °C com correção de altitude), então o "viés quente da Tmax do POWER" não explica essa diferença; o ERA5 não foi testado contra o INMET. A ET0 do POWER sai 1,27 vez a das automáticas (vento +1,6 m/s; radiação +1,4 MJ/m²/dia), mas 0,97 (Fortaleza) e 1,01 (Sobral) vez a ETP normal do INMET. Não há fator único: o 0,79 (1/1,27) é só sensibilidade (`v3_curador_valida_inmet.saida.txt`, D e D2). |
| GRACE/GRACE-FO | ~300 km | Regional | Mascon regional, **média móvel de 3 meses**. | Só contexto regional. Um mês isolado só aparece com a faixa de ruído. O recibo mostra n_eff ≈ 28. |
| GLDAS-2.2 CLSM (diário) | 0,25° | Regional: a célula de Quixadá anda junto com o CE (r 0,98; `v2_designer_banco_lento.saida.txt`) | Água subterrânea (GWS) por mês | **Assimila o GRACE por construção; não medimos quanto.** A concordância com o GRACE (r 0,88 no CE) não vale como validação. Fica fora da tela. |
| GLDAS-2.1 Noah (mensal) | 0,25° | Regional | Umidade em 4 camadas | É a referência **não circular** contra o GRACE (r da anomalia 0,65 no CE). |
| HLS / Landsat / S2 | 30 m (20 m) | Talhão, mas visível em só 29–71% dos portões | Desvio **relativo à vizinhança na mesma data**. | Cancela a deriva comum dos sensores e o viés de amostragem: o céu limpo coincide com o veranico (`sr_fundacao_r2_ceu_limpo_veranico.py`). |
| MODIS → VIIRS (VNP13A3) | 250 m – 1 km | **25 km na quadra** (r 0,854; 0,42 a 1 km) e 2 km na seca | NDVI **relativo ao estado no mesmo ano**, agregado ao município. O VIIRS é a fonte a partir de 2012. | Continuidade: r 0,986 com o MODIS na média do estado e cobertura de jul–out/2025. O composto de nov/2026 é provisório (produzido em 13/11). O NDVI absoluto pós-2020 está deslocado (M6). |
| VIIRS (focos) | 375 m (~14 ha) | — | Contagem de focos por célula, agregada à paisagem. | Não é área queimada e nunca serve para fiscalizar um talhão: 51% dos focos de out–dez caem em pixel arbóreo e só 4,7% em lavoura (`v2_ecologo_calendario_fogo.saida.txt`). Área queimada: Landsat a 30 m (Franca Rocha et al. 2024; o nome "MapBiomas Fogo" fica a conferir). |
| NASADEM/SRTM | 30 m | — | Declive e baixio por município. | Erosão, baixio e aleias em nível. |
| NEX-GDDP | 0,25° | — | Delta de Tmax sobre o replay. | Cenário rotulado; só temperatura (a chuva não é robusta entre modelos; síntese 90.1). |
| NISAR (roteiro) | 200 m | Não medida | — | Antes de qualquer uso: agregar a 9 km e exigir r ≥ 0,8 nas anomalias contra o SMAP L3 a 36 km. Provisório e não validado (revisão, D40). Nenhum dado do NISAR na demo. |

### 4.3 Que variáveis entram em cada módulo

| Módulo | Variáveis NASA | Variáveis locais | Saída |
|---|---|---|---|
| M1, gêmeo físico | IMERG diário; ET0, Tmax e radiação do POWER; declive NASADEM; **SMAP L4 como alvo de calibração do estado** | Água disponível do solo, data de plantio, Kc e ciclos | ISNA por estágio, sobra de água na colheita, demanda de salvamento, janela sintética tipo-ZARC, **estado da água calibrado** (novembro e entressafra) |
| M2, emulador de replay (fim de safra) | Saídas de M1; dias quentes acima do p90 local (POWER); NDVI relativo (**VIIRS**, MODIS antes de 2012) | PAM (alvo) | Estimativa da NASA para cada quadra. **Fica no repositório, fora da demo:** as previsões por município-ano não foram salvas |
| M3, previsor por portão | **Chuva IMERG desde 1/fev (luz principal)**; **SMAP L4, percentil da zona da raiz (segunda missão, 2015→)**; chuva desde 1/jan como regra antiga | ONI | Luz em 4 estados por portão, habilidade por era, aviso de caso inédito, contagem de análogos, probabilidade do P1 |
| M4, carteira e política | Replay de M1–M3 nas 28 quadras | Pesos, restrições, preços | 3 estratégias + a atual, em sequência de 3 anos |
| M5, prática atual | MODIS/HLS (fenologia), focos VIIRS | PAM, 1 pergunta à família | Estratégia atual |
| M6, sentinela de deriva e qualidade | LST e NDVI do MODIS contra POWER, Landsat, HLS e **VIIRS**; **disponibilidade e duplicatas do SMAP** | PAM (bandeira de relato repetido) | Rebaixamento automático do grau |
| M7, relógio lento e combustível | **Memória de chuva do IMERG (12–48 meses)**; GRACE e GLDAS como checagem; fração de água do Landsat; NDVI VIIRS de t e t−1; focos VIIRS | Volume de barreiro ou cisterna | Banco de água azul, área salvável, **mapa** de combustível e da ponte verde |
| M8, redator com verificador | JSON de M1–M7 | Trechos conferidos da revisão | Textos dos cartões em PT e EN, congelados |

### 4.4 Frescor dos dados na data da demo (14/11/2026)

- IMERG V07 Late: até 12/11/2026; Early: até 13/11/2026 (Nordeste, diário). IMERG diário municipal (via POWER): até 14/09/2026. O Final V07 vai só até 30/09/2025; depois disso, o diário via POWER é o Late, preliminar.
- **SMAP L4 diário: 31/03/2015 → 10/11/2026**, sem dia faltando em 2016–2025; 4 datas com dois granulos, a deduplicar no exportador.
- **SMAP L3:** o consolidado (2015-03-31 → 2026-11-12; 4.167 dias, 7 datas duplicadas) foi usado na checagem final do arquiteto (`v2_arquiteto_r2_fechamento.saida.txt`, bloco H). Os números do L3 nos portões não mudaram em relação aos recortes diários (30/abr: 0,774).
- **VIIRS VNP13A3:** até out/2026 (nov/2026 é provisório e fica fora de painel).
- **GLDAS-2.2 CLSM diário:** até 31/08/2026. GLDAS-2.1 Noah mensal: até jul/2026. NLDAS-2: até out/2026.
- ONI: até ASO/2026. GRACE: até set/2026.
- MODIS: até set/2026 no arquivo mensal, com o buraco de jul–out/2025 no Terra.
- PAM: até 2025. Focos VIIRS no arquivo anual: até dez/2025 (o FIRMS de 2026 exige o NRT com chave).
- Pink Sheet: até out/2026.
- Nota de unidade: o derivado `imerg_late_ce_mensal` rotula como "mm/day" o que é total mensal. O arquivo não foi alterado; a correção vale para o exportador.

---

## 5. Os módulos de IA (SI)

**Princípio da equipe:** com 28 quadras e um punhado de episódios de seca desde 1998, a SI que funciona é **pequena, guiada pela física, validada por ano e comparada só com a melhor linha de base declarada**. Cinco medidas sustentam isso:

- **A validação aleatória mente:** o boosting tem R² 0,49 com validação aleatória e −0,08 deixando o ano de fora (`cetico_escala_vazamento.py`).
- **A restrição física ajuda pouco e de forma honesta:** com as mesmas entradas, o GBM monotônico dá AUC 0,794 contra 0,762 do GBM livre, no milho (+0,03). No feijão, não ajuda (0,702 contra 0,739) (`saidas/hidrologo_hibrido_log.txt`).
- **A leitura decide mais que o sensor:** em 30/abr (2016–2025), a mesma chuva IMERG vai de AUC 0,66 (desde 1/jan) a 0,76 (desde 1/fev), 0,80 (API) e 0,80 (últimos 15 dias). O SMAP fica em 0,77 e o L3 em 0,77. Contra a melhor leitura declarada, o ganho próprio do SMAP é ~0 (`v2_cetico_r2b_smap_contra_imerg_justo.saida.txt`, A; `v2_arquiteto_r2_fechamento.saida.txt`, H).
- **Onde o SMAP soma:** como confirmação em São José (vermelho 5,3 em 10 contra amarelo 2,1), como alvo de calibração do balde (r 0,84 → 0,96 no ano fora), como nível absoluto, através das nuvens e no globo.
- **Dentro do ano, nada bate de longe a geografia:** nenhuma camada NASA passa de AUC ~0,65 entre municípios no mesmo ano (L3 0,645 em 30/abr), e o mapa de risco de base do município sozinho dá de 0,61 a 0,69 no milho, conforme o portão (`v2_hidrologo_smap_portoes_quebra.saida.txt`).

### M1. Gêmeo físico do roçado (balde FAO-56)

- **Papel:** simular, para cada cultura e arranjo, a água que a planta recebe em cada estágio, e estimar o estado da água no solo fora da quadra.
- **Método:** balde diário FAO-56 (ETc = Kc × ET0) vetorizado em numpy (Allen et al. 1998). A data efetiva de semeadura vem da inversão contra o PAM: o milho se comporta como semeado 0–10 dias após a 1ª chuva, e o feijão cerca de 20 dias depois (`agronomo_calibracao_pratica.py`).
- **Um balde por tipo de número**, declarado no recibo:
  - datas-limite e ISNA de milho, caupi e sorgo vêm do balde do agrônomo (`agronomo_isna_zarc_sintetico.py`);
  - sobra de água na colheita e demanda de salvamento vêm do balde do hidrólogo (`hidrologo_fao56_isna_pam.py`);
  - **novo: o estado da água** (portão de novembro, entressafra) vem do balde do hidrólogo **calibrado contra o SMAP L4** município a município, com o SMAP como alvo e nunca a safra. A correlação com o SMAP no ano deixado de fora sobe de 0,838 para 0,958 (10 de 10 anos), a memória vai de 18 para 44 dias e o vale da seca passa de 08/09 para 20/10 (SMAP: 18/11) (`v2_hidrologo_calibra_m1_smap.saida.txt`). A capacidade calibrada cai na borda da grade (300 mm em 97 de 184 municípios): é um parâmetro efetivo de memória, não uma propriedade do solo. Por isso o ISNA de cultura continua no balde padrão.
- **Validação, pareada:**
  - No milho, o ISNA soma cerca de +0,04 de AUC sobre a chuva com o mesmo modelo (0,767 contra 0,727; `saidas/hidrologo_hibrido_log.txt`). **Correção da rodada 2:** dentro do ano, essa vantagem é a geografia (ISNA 0,613 contra 0,612 só com o mapa de risco do município, 1999–2025). O ISNA entra como **mapa de risco de base**, grau C, e não como "sinal NASA do ano".
  - No feijão, piora: 0,637 contra 0,712.
  - Calibrar o balde pelo SMAP **não** melhora o alerta fora da amostra (1998–2014: calibrado − chuva = +0,004, IC90 −0,049 a +0,065). O ganho do SMAP no M1 é hidrológico.
  - O ZARC sintético ordena os municípios como a quebra real (ρ de +0,40 a +0,49 em 28 anos; +0,30 só em 2016–2025). Isso valida a ordem, não as datas. Grau C.
  - **Novo: o sintético contra o ZARC oficial 2026/27.** O veredito depende do solo de referência, porque o sintético usa um solo só. Contra o solo e o ciclo mais permissivos de cada município, só o milho confere (Spearman 0,86; ±1 decêndio em 89%), e caupi e sorgo ficam 2–3 decêndios mais cedo (±1 em 38% e 2%). Contra a mediana dos solos e ciclos, caupi e sorgo conferem (diferença mediana 0; ±1 em 84%), e o milho sintético fica 2 decêndios mais tarde (±1 em 8%). Em Quixadá, o caupi sintético (21/mar) fica a ±1 decêndio do oficial em 8 das 9 combinações de solo e ciclo (exceção: argiloso do Grupo I, até 20/abr). Só o Grupo I tem cultivar indicada na Port. 121/2026 (R3.5, C): com ele, são 2 de 3 combinações. Regra: nunca escrever "confere" sem dizer contra qual solo (`pesquisa/viabilidade_artigos_nordeste.md`, 4.3 e "Verificação adversária"; `v3_verificador_zarc_solo.saida.txt`). No Brasil, a janela que vai ao cartão é a oficial (3.5).
- **Sensibilidade das datas-limite:**
  - À fonte da ET0: com a ET0 na escala do ERA5 (× 0,87), as datas andam no máximo 1 decêndio em 97–99% dos municípios (`arquiteto_final_zarc_et0_sensibilidade.saida.txt`). Em Quixadá, o milho fica em 01/mar e o caupi em 21/mar nas duas escalas; o sorgo vai de 11/mar para 21/mar.
  - **À estação do INMET (novo):** não há fator único (1,27 contra as automáticas; 0,97–1,01 contra as normais). O fator 0,79 entra só como sensibilidade, e a rodada do M1 com ET0 × 0,79, incluindo o milho, ainda falta. A hipótese de que a ET0 inflada explica o caupi e o sorgo sintéticos mais cedo não fecha: a ET0 é a mesma nas três culturas, e o desvio de 2–3 decêndios só aparece contra o solo oficial mais permissivo (`pesquisa/viabilidade_artigos_nordeste.md`, 4.4, item 9). Até calibrar a ET0, o Kc da FAO fica.
  - **Ao modelo de solo (novo):** com a zona da raiz do SMAP no lugar do balde, o caupi concorda (±1 decêndio em 58% dos municípios), mas o milho fica 3 decêndios mais tarde na mediana (em Quixadá, 21/abr contra 01/mar) e o sorgo 2. O SMAP não ordena a quebra entre municípios (ρ −0,13), e o balde ordena. **As datas ficam com o balde.** O cartão do caupi mostra ±1 decêndio; o do milho e do sorgo diz "a incerteza passa de ±1 decêndio: outro modelo de solo da NASA dá mais tarde, sem validação" (`v2_agronomo_smap_janelas.saida.txt`, blocos B e C).
- **Onde erra:**
  - Superestima 2010 e 2013. O **ISNA de cultura semeada na 1ª chuva** não vê 1998: 4% dos municípios com ISNA < 0,5, contra 67% em quebra real (`pesquisador_ia_checa_simulador_anos.py`).
  - **Correção da rodada 2:** o ponto cego é dessa formulação, não do balanço hídrico. O estado da água do balde, em percentil, acende para 1998: abaixo de 20 em 30/abr em 135 das 135 quebras (a chuva pegou 103). Grau C, porque o balde começa vazio em 1/jan/1998 (`v2_hidrologo_calibra_m1_smap.saida.txt`).
  - O risco de 2027 continua vindo do oceano (M3, P1), e não do balde.
- **Incerteza:** a ordem resiste à água disponível do solo (ρ de 0,46 a 0,48 entre 30 e 90 mm). O nível não resiste: P(ISNA < 0,5) vai de 1,5% a 14,3% (`saidas/hidrologo_calibracao_balde.csv`).

### M2. Emulador de replay em duas escalas (estimativa de fim de safra)

- **Papel:** dar, para cada quadra do replay, a estimativa da NASA para o rendimento relativo do município, ao lado do observado do IBGE. **Fica no repositório e fora da demo** (banca R2): as previsões por município-ano nunca foram salvas, e o número de vitrine (0,307) já estava suspenso.
- **Rótulo obrigatório:** é um **emulador de fim de safra**. Ele usa o NDVI de mar–mai e o ISNA da floração, então **nunca aparece ao lado da curva de habilidade dos portões**.
- **Método:** ridge ou GBM monotônico em duas escalas:
  - nível do ano: ISNA agregado + calor relativo;
  - ordem local: desvio do ISNA + desvio do NDVI **relativo ao estado no mesmo ano** (a variante "relativo aos vizinhos de 50 km" é pior em todos os portões: 0,561 contra 0,630 no fim de safra; `v2_sr_fundacao_viirs_portoes.saida.txt`, bloco C).
- **Validação, só pareada** (mesmas dobras LOYO; `saidas/pesquisador_ia_fusao_fisica_satelite.csv`):

  | Configuração | R² LOYO | ρ dentro do ano | AUC quebra | Viés walk-forward 2020–25 |
  |---|---|---|---|---|
  | Só chuva, HGB | 0,365 | 0,155 | 0,816 | −0,13 |
  | Duas escalas (ISNA ano+local, NDVI só local), ridge | 0,365 | 0,307 | 0,851 | +0,01 |

  - **Suspenso:** o ganho de ordem local (0,155 → 0,307) não foi comparado com uma linha de base **só de geografia**, o mesmo teste que derrubou o ISNA. Fica no repositório, sem slide.
  - A faixa das 14 configurações testadas vai de AUC 0,78 a 0,85, e a configuração foi escolhida olhando o LOYO. Seleção aninhada fica para depois do júri; até lá, o repositório mostra a faixa.
  - O alvo do M2 (anomalia contra tendência) não é o canônico. No replay, o observado mostrado é sempre a razão canônica.
  - **Regra anti-artefato (nova):** a AUC 0,851 vem de previsões LOYO agregadas. Com poucos anos, essa métrica é enviesada (com 10 anos, a climatologia LOYO sozinha dá AUC 0,154; `v2_pesquisador_ia_smap_portoes.saida.txt`, superado). Com 28 anos o viés é menor; a conferência com escore sem intercepto e AUC dentro do ano fica para depois do júri, com o M2 fora da demo.
- **Continuidade do NDVI:** o VIIRS substitui o MODIS sem retreinar o M2 antes do júri. No fim de safra, o VIIRS perde cerca de 0,02 de AUC dentro do ano contra o MODIS (0,599 contra 0,621, IC −0,05 a +0,00) (`v2_sr_fundacao_viirs_portoes.saida.txt`, bloco C).
- **Testemunha de junho (novo):** o NDVI VIIRS de abr–mai, em % do normal do município, é a primeira leitura da safra pela NASA, um ano antes do PAM. Abaixo de 90% do normal, 7,5 em 10 municípios quebraram o milho (n = 309 município-anos, 12 de 14 anos); acima, 1,9 em 10; AUC 0,79 (IC90 por ano 0,73–0,83) (`v2_designer_verde_viirs.saida.txt`, bloco A). Dentro do ano, ~0,62, igual à geografia: é **testemunha do ano**, não ordem local. Grau A como testemunha; não é alarme.
- **Incerteza:** conformal robusto ao ano (o ano é a unidade trocável). Ele cobre 77–86% dos anos no nível de 80%, contra 46–68% do conformal padrão, **mas compra isso com largura**. No portão de pré-safra, a largura passa de 227 para 282 pontos percentuais, onde o modelo é pior que a climatologia (MSSS −0,37). A frase certa é: "em janeiro, a incerteza honesta é do tamanho da climatologia" (`pesquisador_ia_conformal_carteira.py`).

### M3. Previsor por portão: uma luz de chuva NASA e a segunda missão

- **Papel:** em cada portão, dizer o que já se sabe e quanto isso vale, e quando não se sabe nada.
- **Luz principal (congelada para 2027):** **chuva IMERG de 1/fev até o portão < 75% do normal do município**, sendo o normal a mediana das outras quadras. A regra da rodada 1 (chuva desde 1/jan) vira a "regra antiga" e só aparece por era, no replay e na auditoria.
- **Segunda missão:** **percentil da zona da raiz do SMAP L4 < 20, na média dos 7 dias até o portão.** Ela confirma ou não a luz principal e nunca acende o vermelho sozinha.
- **Os quatro estados:** vermelho (as duas acesas), amarelo (só a chuva), cinza-amarelo (só o SMAP: "os instrumentos discordam; o técnico decide") e verde.
- **Como a luz principal foi escolhida** (critério R1, escrito no cabeçalho de `v2_arquiteto_r2_fechamento.py` antes de rodar): entre as 5 leituras de chuva já declaradas por outros especialistas, todas com corte fixo de 75%, vence a de maior AUC **mínima** em {19/mar, 30/abr} × {1998–2015, 2016–2025}. As AUCs por era já tinham sido impressas pelo cético (`v2_cetico_r2b_smap_contra_imerg_justo.saida.txt`, bloco F), então a escolha não é cega a esses números.

  | Leitura (quem declarou) | 19/mar 1998–2015 | 19/mar 2016–2025 | 30/abr 1998–2015 | 30/abr 2016–2025 | Mínimo |
  |---|---|---|---|---|---|
  | **Desde 1/fev (economista)** | 0,74 | 0,71 | 0,82 | 0,76 | **0,709** |
  | Últimos 30 dias (cético) | 0,73 | 0,67 | 0,75 | 0,75 | 0,672 |
  | API τ = 13 d (agrônomo) | 0,75 | 0,61 | 0,79 | 0,80 | 0,607 |
  | Últimos 15 dias (cético) | 0,71 | 0,58 | 0,72 | 0,80 | 0,576 |
  | Desde 1/jan (regra antiga) | 0,77 | 0,55 | 0,83 | 0,66 | 0,547 |

- **Regra congelada:** o texto completo e o sha256 interno (`41b7c820fe6693dd1ac2336075585a36fc6ec03fd9e1133c4537d8cf984fdb41`) estão no bloco B do fechamento. O juiz de 2027 é a quebra canônica do milho no PAM de 2027, publicado em 2028. O hash só vira público com o OK do José.
- **Curvas por era nos 5 portões** (AUC agrupada, quebra canônica do milho; `v2_arquiteto_r2_fechamento.saida.txt`, bloco A):

  | Portão | Desde 1/jan, 98–15 | Desde 1/jan, 16–25 | Desde 1/fev, 98–15 | Desde 1/fev, 16–25 | SMAP 7 d, 16–25 | ONI ASO, 98–15 | ONI ASO, 16–25 |
  |---|---|---|---|---|---|---|---|
  | 15/nov | — | — | — | — | (percentil vazio) | 0,66 | 0,72 |
  | 31/jan | 0,63 | 0,27 | — | — | — | 0,66 | 0,72 |
  | 28/fev | 0,71 | 0,46 | 0,65 | 0,66 | 0,62 | 0,66 | 0,72 |
  | **19/mar** | 0,77 | 0,55 | **0,74** | **0,71** | 0,68 (dia: 0,59) | 0,66 | 0,72 |
  | 31/mar | 0,79 | 0,55 | 0,76 | 0,70 | 0,68 (dia: 0,58) | 0,66 | 0,72 |
  | **30/abr** | 0,83 | 0,66 | **0,82** | **0,76** | 0,77 | 0,66 | 0,72 |

  - Nas 28 quadras juntas, a regra antiga dá 0,57 (31/jan), 0,67, 0,73, 0,75 e 0,80 (30/abr). Esses números só aparecem com as duas eras ao lado.
  - Na última década, **o oceano conhecido em novembro (0,72) valeu tanto quanto a melhor chuva de São José (0,71)**. A frase de 2027 segue: "a NASA diz o estado, o oceano diz a chance".
  - A AUC de 30/abr mede uma janela que já é quase a quadra inteira. Por isso 30/abr serve para salvar, não para prever.
- **No nível do ano, a unidade independente**, a habilidade é bem menor. Spearman entre a fração de municípios com luz e a fração em quebra (mesmo bloco):
  - 19/mar: desde 1/fev +0,63 (1998–2015) e +0,19 (2016–2025); regra antiga +0,63 e −0,30; SMAP +0,32 (2016–2025).
  - 30/abr: desde 1/fev +0,78 e +0,50; regra antiga +0,86 e +0,41; API +0,79 e +0,87; SMAP +0,63.
  - **Em São José, na última década, nenhuma leitura ordena bem os anos (n = 10).** A chuva desde 1/fev é a única que não se inverte. Cada leitura erra anos diferentes: a regra antiga perdeu 2016 e 2025; a chuva desde 1/fev perdeu 2012 e 2015 em 19/mar e deu alarme falso em 2022 (78% dos municípios) e 2021 (42%).
- **Placar das duas missões (2016–2025, milho; 1.820 município-anos, 268 quebras; bloco C):**

  | Portão e estado | Município-anos | Quebram | Anos com o estado |
  |---|---|---|---|
  | 19/mar, vermelho (chuva desde 1/fev e SMAP) | 118 | **5,3 em 10** | 5 |
  | 19/mar, amarelo (só a chuva) | 426 | 2,1 em 10 | 7 |
  | 19/mar, só o SMAP | 6 | 0 em 10 | 2 |
  | 19/mar, verde | 1.270 | 0,9 em 10 | 9 |
  | 30/abr, vermelho | 212 | 4,1 em 10 | 3 |
  | 30/abr, amarelo | 194 | 3,4 em 10 | 7 |
  | 30/abr, só o SMAP | 30 | 3,3 em 10 | 5 |
  | 30/abr, verde | 1.384 | 0,8 em 10 | 10 |

  - Taxa-base da década: 1,5 em 10. Em 19/mar, a confirmação do SMAP separa o vermelho do amarelo. Em 30/abr, ela pouco acrescenta.
  - No nível do ano, o vermelho tem ρ +0,32 (19/mar) e +0,46 (30/abr), com n = 10. Não é significativo.
- **2016 e os anos que vão junto** (bloco C):
  - **2016, 19/mar:** 127 de 182 municípios quebraram. Desde 1/jan: luz em 7. Desde 1/fev: em 182. SMAP: em 56.
  - **2016, 30/abr:** desde 1/jan, luz em 14 (o estado parecia normal em 92%); desde 1/fev, em 164; SMAP, em 91 (metade).
  - **Qual município?** Ninguém sabe: dentro de 2016, a AUC é de 0,61 (desde 1/jan), 0,65 (desde 1/fev) e 0,65 (SMAP) em 19/mar, e de 0,53, 0,59 e 0,53 em 30/abr. Com as mesmas 91 luzes do SMAP em 30/abr, os 91 municípios com menos chuva desde 1/jan teriam pego 66 quebras, contra 64 do SMAP (`v2_juiz_numero_uau.saida.txt`).
  - **Mesmo número de alarmes:** com a mesma taxa de alerta da chuva desde 1/fev (29,9% dos município-anos em 19/mar), a regra antiga pegaria 55 das 127 quebras de 2016 e gastaria 142 alertas em 2021. A chuva desde 1/fev pega as 127 e gasta 76 alertas em 2021.
  - **2021:** 7 quebras. Em 19/mar, a chuva desde 1/fev acendeu em 76 municípios e o SMAP em 26; em 30/abr, 97 e 81.
  - **2022:** 3 quebras. Em 19/mar, a chuva desde 1/fev acendeu em 142 municípios e o SMAP em 0. É o melhor exemplo de por que existe a segunda missão.
  - **2025:** 45 quebras. Em 30/abr, o SMAP acendeu em 46 municípios e pegou 21 (11,4 esperadas ao acaso, `v2_juiz_numero_uau.saida.txt`). É o único ano com acerto municipal acima do acaso, e os municípios vizinhos não são independentes.
- **O que o recibo diz:** o SMAP L4 é um modelo da NASA forçado por chuva corrigida para os totais do IMERG (segundo a equipe do L4_SM, EGU23-1419; a v008 não foi conferida) e corrigido pelo radiômetro. A observação pura do radiômetro (L3 consolidado) dá o mesmo em 30/abr (0,774; IC90 0,53–0,88; n = 1.740). Em 30/abr/2016, o L3 esteve abaixo de 75% do próprio normal em 173 de 174 municípios (bloco H). **Duas missões da NASA veem o estado da água; a soma desde janeiro, não.** As duas não são independentes, e o recibo diz isso.
- **Ressalva de processo:** a luz principal e o papel do SMAP foram escolhidos depois de ver 2016–2025. Os limiares foram fixados antes: 75% na rodada 1 e 20 na seção 05 do notebook (commit `48a3608`, 14/11 às 08:34: "abaixo de 20 = seca agrícola"). Grau B até a quadra de 2027.
- **Escala declarada:** dentro do ano, a AUC fica entre 0,50 e ~0,65 para todas as leituras. O alerta é **regional**. Em Quixadá (bloco D):
  - chuva desde 1/fev: em 19/mar, 9 alertas e 3 acertos (1998, 2015, 2016), com alarmes falsos em 2005, 2008, 2010, 2013, 2018 e 2022. Em 30/abr, 9 alertas e 5 acertos (1998, 2012, 2015, 2016 e 2025, este a 0,747 do normal, por um fio), com alarmes falsos em 2005, 2010, 2013 e 2021. Quebras perdidas: 2001, 2023 e 2024;
  - regra antiga: 8 alertas e 2 acertos em 19/mar; 7 e 3 em 30/abr;
  - SMAP (2016–2025, limiar 20): **nenhum acerto.** Em 30/abr, os dois anos secos tiveram os dois menores valores do dia (2016 = p20,1; 2025 = p20,3), por décimos acima do limiar. A média de 7 dias acendeu só em 2021 (p15,9), sem quebra. Por isso, em Quixadá, o único vermelho da década foi falso (2021, 30/abr). Não reajustamos o limiar; o placar mostra isso.
- **Portão de novembro (P1), modelo único pré-declarado no script do clima** (`v2_clima_portao_novembro_2027.saida.txt`): logística P(quebra municipal) ~ ONI ASO do ano anterior, validada deixando o ano inteiro de fora.
  - BSS municipal +0,063 (IC90 −0,07 a +0,18): habilidade pequena, com IC que inclui zero. No nível do ano, ρ +0,39 (p = 0,038; n = 28).
  - No El Niño mais forte antes deste (ONI 2,04): **0,54 (IC90 0,24–0,75)**, contra 0,20 com ONI 0 e 0,215 de taxa-base. Em 2,46 (o de hoje), 0,62 (0,25–0,83), **por extrapolação**; o valor vai de 0,53 a 0,72 conforme o análogo retirado.
  - Na tela: "num ano qualquer, 2 em 10 municípios perdem metade do milho. No El Niño mais forte antes deste, cerca de 5 em 10 (faixa de 2 a 8). Em 1998 e 2016, 7 em 10; em 2024, menos de 1 em 10. Este ano está além do recorde."
- **Detector de caso inédito:** o ONI de 2,46 está 0,42 acima do máximo de ASO das quadras de 1982 a 2026 (2,04). A tela mostra o valor em 2,04 como "dentro do que já vimos" e o de 2,46 com selo de extrapolação.
- **Análogos só como contagem:** 4 de 7 quadras secas desde 1966 (1966 por proxy); 3 de 5 pela reanálise POWER desde 1982 (IC90 0,19–0,92); 2 de 3 catástrofes na era IMERG (IC90 0,14–0,98). Na leitura descritiva de 10/mar, a chuva desde 1/fev estava acesa em 94% dos municípios em 1998, 100% em 2016 e 0% em 2024 (quebras de 75%, 70% e 8%). São n = 3 anos, sem habilidade medida.
- **O que vigiar em P2 (só texto, sem probabilidade):** o Pacífico dificilmente esfria a tempo (1 de 7 El Niños fortes). O Atlântico Sul (TSA de jul–set) separou os análogos que escaparam, mas a hipótese nasceu ao olhar 5 deles, e a contraprova (2 de 2) tem chance de acaso de 0,25. Hoje o TSA está do lado de 2024 (+0,37). Fica fora do pitch.

### M4. Carteira e política

- **Papel:** gerar e ordenar as estratégias (a atual e mais 3) e a regra de cada portão.
- **Método:** **enumeração exata** de uma biblioteca de jogadas por portão: as regras de plantio R1–R9, a troca de cultura, o revezamento, o salvamento, a palhada e a composição de área. As regras R1–R9 já são a árvore de decisão que o técnico repete; não há destilação à parte.
  - **Correção de rótulo:** as regras R4, R5 e R8 apareciam como "(SMAP)" em `saidas/agronomo_regras_semeadura.txt`, mas eram um balde de solo nu. Passam a "R4/R5: balde, solo ≥ 30/45 mm" e "R8: fevereiro ou balde ≥ 45 mm em janeiro". Com o SMAP de verdade, "esperar o solo encher" não separa a quebra: o percentil da zona da raiz no dia de semeadura tem AUC 0,47, e o tercil úmido quebrou até um pouco mais (15,5% contra 11,4% no seco) (`v2_agronomo_smap_portoes.saida.txt`, P2).
- **Ranking:** onde há rendimento observado, usa os 3 eixos calculados (chance de colher menos da metade, "pior ano em 10" e mediana). Onde não há (S1, S3), o cartão diz "sem número". Forragem, N, carbono, trabalho e ciclos entram como etiquetas com grau.
- **Um motor de carteira só** no JSON: a carteira de áreas iguais, com a definição canônica (`juiz_carteira_definicao_canonica.py`, definição b). A carteira de mínimo CVaR do economista ("melhora em 81% de 131 municípios") fica no AUDIT.md como "diversificação em geral".
- **Validação** (`arquiteto_final_carteira_ic.saida.txt`; 2.495 município-anos, 135 municípios, onde as três culturas existem):

  | Composição | Pior ano em 10 (CVaR10) | IC90 por ano | Chance de < 50% |
  |---|---|---|---|
  | 100% milho | 0,15 | 0,09–0,26 | 21% |
  | **Milho + feijão (prática atual, S0)** | **0,26** | 0,19–0,38 | **15%** |
  | 1/3 milho, 1/3 feijão, 1/3 mandioca | **0,36** | 0,28–0,47 | **11%** |

  - **A comparação que vale é contra a S0** (banca R2): 0,26 → 0,36. O 0,15 do milho sozinho só aparece na tabela.
  - **Placebo pré-declarado pelo cético** (`v2_cetico_r2b_gatilho_carteira.saida.txt`, bloco 3; n = 2.438): trocar o terço de mandioca pelo **feijão de um dos 5 vizinhos mais próximos**, no mesmo ano, já dá 0,335 (0,323–0,347 em 200 sorteios); pelo milho do vizinho, 0,278. Parte da conta é só a média de séries com ruído de relato independente. **A parte própria da mandioca fica entre +0,02 e +0,08.** Não derrubam o efeito: o relato copiado (só 5% da mandioca na cauda do milho repete o ano anterior) e o ciclo longo (com a mandioca do ano seguinte, 0,444). Grau A só para o descritivo do estado; o ganho atribuível à mandioca é B.
  - **Nos anos em que a luz NASA acendeu** (bloco F do fechamento; n = 585 município-anos com chuva desde 1/fev < 75% em 30/abr, 17 anos): pior ano em 10 de 0,05 no milho, 0,13 na S0 e 0,21 na 1/3. O ganho sobre a S0 tem IC90 por ano de +0,04 a +0,10. Com a luz apagada, 0,30, 0,40 e 0,51. Com a luz de 19/mar, 0,06, 0,17 e 0,25. É assim que o número da rotação passa pelo dado da NASA: **a luz diz em que anos a cauda chega; a carteira diz quanto dela fica.**
  - **Piso declarado:** contando o ano sem mandioca como perda total, nos 91 municípios de mandioca, o CVaR10 fica em **0,321 (IC90 0,265–0,401)**, contra 0,169 do milho (`v2_economista_diversidade_carteira.saida.txt`, bloco C).
  - **Teto, não promessa:** na carteira real dos municípios, cada cultura efetiva a mais vale +0,067 no CVaR10 (IC90 +0,043 a +0,081), cerca de 65% do que a conta da M4 promete por cultura (+0,103) (mesmo arquivo, bloco B).
  - **A cauda:** vem de **cinco a sete anos ruins desde 1998** (em ordem de peso: 1998, 2012, 2016, 2015, 2010, 2001 e 2013).

### M5. Leitor da prática atual

- **Novo, Censo Agropecuário 2017:** a rotação declarada sai do Censo, não do PAM. A diversidade de culturas do PAM quase não acompanha a rotação declarada (Shannon × rotação, ρ +0,15 no CE). A rotação declarada cobre 7,9% dos estabelecimentos no CE e 6,1% em Quixadá (4.880 estabelecimentos) (`pesquisa/viabilidade_artigos_nordeste.md`, 4.3 e "Confirmado sem mudança").
- **No MVP:** a prática atual vem do PAM do município (o que se planta e quanto), do Censo 2017 (se a rotação é declarada) e de **1 pergunta** à família ("o senhor queimou o roçado em nov/2025?"). O satélite não responde isso: a 375 m, o FIRMS não separa a broca do roçado do incêndio na capoeira (51% dos focos de out–dez caem em pixel arbóreo).
- **Figura estática:** o "código de barras de safras" (fenologia MODIS/HLS + focos VIIRS) da AOI do Sertão Central entra como figura, com o selo de visibilidade.
- **Selo de visibilidade (atualizado):**
  - Óptico a 30 m: fração de AOI-anos com ao menos uma cena útil (≥ 60% da área limpa) nos 30 dias antes do portão, com Sentinel-2 + Landsat: 79% em 28/fev, 71% em 31/mar e 92% em 30/abr (n = 24 AOI-anos). Só com o Landsat 8/9: 50%, 29% e 46% (`sr_fundacao_r2_checagens.log`, bloco B).
  - Óptico a 1 km: só 39–40% dos pixels do CE têm NDVI VIIRS bom no mês em jan–mar, contra 95–96% em ago–out.
  - **Micro-ondas:** o radiômetro do SMAP tem pegada de ~40 km e é postado numa grade de 9 km. A célula mediana é vista em 13 a 15 dias por mês, na quadra e na seca, e 93,5% das células-mês têm ao menos 4 dias vistos (`v2_sr_fundacao_smap_l3_l4.saida.txt`, bloco A). Frase do slide: "o óptico fica parcialmente cego nas datas de decisão; o micro-ondas vê através das nuvens".
- **Limite:** a semeadura segue a chuva, quando o óptico está cego. Por isso a data de plantio é **perguntada à família**.
- **Roteiro:** código de barras ao vivo para qualquer talhão, Prithvi-EO-2.0 e Sentinel-1/NISAR para datar o plantio sob nuvem.

### M6. Sentinela de deriva e de qualidade

- **Papel:** rebaixar automaticamente o grau de qualquer camada que derive ou falhe.
- **Método:** Mann-Kendall/Sen e CUSUM sobre o resíduo de cada sensor contra uma referência independente, mais bandeiras de qualidade do PAM e do SMAP.
- **O que já sinalizou:**
  - **A deriva documentada da órbita do Terra.** A LST diurna do MODIS lê 4,6 °C mais fria em relação à Tmax do ar do que em 2000–2019 (resíduo −6,17 °C em 2026 contra −1,56). A LST noturna não deriva. Usada sem correção, a LST levaria a previsão de 2026 para **+58% de safra**, contra +20% sem ela (`cetico_deriva_lst_terra.saida.txt`; `cetico_previsao_preregistrada_2026_*.saida.txt`). A deriva é documentada pela equipe do MODIS; o sentinela a pegou sozinho, mas não a descobrimos.
  - **Um deslocamento do NDVI desde 2020, agora visto por dois sensores.** O NDVI de fev–mai está mais verde para a mesma chuva: +0,047 a +0,053 no MODIS e +0,033 a +0,042 no VIIRS, com a chuva IMERG. Com a chuva POWER, o VIIRS dá +0,019 (p 0,23). A parte própria do MODIS é cerca de 0,01 (`v2_sr_fundacao_viirs_portoes.saida.txt`, bloco B; `v2_cetico_clsm_grace_viirs.saida.txt`; `v2_ecologo_ndvi_deslocamento_viirs.saida.txt`). **Não é, principalmente, deriva do Terra; a causa continua aberta** (vegetação real, uso do solo, relato ou o próprio produto de chuva). O rendimento não acompanhou. O NDVI absoluto continua rebaixado; o QUADRA só usa NDVI relativo dentro do ano, que é imune ao deslocamento.
  - **Relato copiado no PAM.** 92% dos municípios com 15 ou mais anos de mandioca têm pelo menos um ano com rendimento idêntico ao anterior; a mediana é de 11% dos anos (`cetico_r3_sao_jose_mandioca.saida.txt`, bloco C). O sentinela marca esses anos, e a carteira é recalculada sem eles (M4).
  - **"2025, o ano mais verde"** era artefato do buraco do Terra (`ecologo_checagem_ndvi_2025.py`). O VIIRS cobre a lacuna.
  - **Novo, SMAP L4:** 4 datas com dois granulos no consolidado (2023-10-09, 2024-04-03, 2024-11-26, 2025-05-22), com até 0,09 m³/m³ de diferença na zona da raiz; o exportador deduplica (aviso ao dono de `consolidar_smap_viirs.py`). No **L3 consolidado**, 7 datas duplicadas (fica a primeira). O percentil do produto vem vazio de ~12/ago a ~12/jan no sertão. E a base da climatologia do percentil não foi conferida: só 13,2% dos município-dias de 2015–2026 ficaram abaixo de p20, quando se esperaria 20% (`v2_designer_termometro_solo.saida.txt`). Até conferir na documentação, nenhum texto diz "mais seco que 8 de cada 10 anos".
  - **Novo, VIIRS:** o composto de nov/2026 foi produzido em 13/11, antes do fim do mês, e fica fora de qualquer painel.
  - **Novo, discordância SMAP × chuva:** em 2026, o SMAP marcou p39 em 19/mar e p35 em 30/abr, com a chuva a 110% e 105% do normal (`v2_hidrologo_cinco_fontes_umidade.saida.txt`). Só o PAM de 2026 arbitra. A sentinela registra o caso.

### M7. Relógio lento da água e combustível

- **Banco de água azul (refeito):**
  - O relógio lento roda na **memória de chuva do próprio IMERG** (filtros de 12 a 48 meses), com o **GRACE como par de mesmo peso**: com n = 23 anos, os dois não se separam. A memória de chuva explica 70% da variância da água subterrânea do GLDAS-2.2 CLSM dentro da amostra e **55% deixando o ano de fora**. O ρ +0,04 com os açudes do Landsat é do **resíduo do CLSM** depois da chuva, não do GRACE. **O GRACE direto é a série que mais acompanha os açudes** (ρ +0,57, p 0,005; +0,73 em diferenças anuais); descontada a memória de chuva de 48 meses, ainda dá +0,35 (p 0,11) (`v2_hidrologo_relogio_lento_gws.saida.txt`, blocos 1 e 3).
  - **CLSM × GRACE não é validação.** O CLSM assimila o GRACE por construção, e não medimos quanto. No buraco GRACE → GRACE-FO (jul/2017–mai/2018), o resíduo não mudou de forma clara (variação mensal de 0,95 contra 1,09 cm). A concordância (r da anomalia 0,85 no GWS; 0,65 no Noah, que só vai até 2 m) não serve de prova em nenhum sentido (`v2_cetico_clsm_grace_viirs.saida.txt`, A).
  - Memória: a água subterrânea esquece em cerca de 8 meses na série mensal de 2003–2026 (e-folding; 392 dias na série diária de 2015–2026). O recibo diz "8 a 13 meses". Depois de 2016, o banco só voltou ao normal em abr–mai/2018 (`v2_designer_banco_lento.saida.txt`).
  - **Não prevê a quadra:** o banco de jun–ago (t−1) contra a fração de municípios em quebra no ano t dá ρ +0,14 (n = 22); o GWS de dezembro, +0,05 (n = 22). O banco lento serve para poço, cacimba e água dos animais, não para escolher a cultura; fica na tela do técnico, sempre como "sua região".
  - No Sertão Central, a fração de água dos açudes no Landsat (1984–2026) acompanha a chuva de 48 meses (ρ +0,62), num sinal que existe em 1 das 4 AOIs (rodada 1; grau C).
- **Área salvável:** o salvamento da floração do milho pede 62 mm na mediana (620 m³/ha). Uma cisterna-calçadão de 52 m³ salva cerca de 0,08 ha num ano mediano. **Correção da v3:** o volume de 52 m³ não foi confirmado em nenhum texto lido (de Lindoso, só o resumo); é suposição (grau D). Marengo 2022 confirma só que a cisterna é de beber. **O salvamento só existe com barreiro ou açude**; o app pergunta o volume.
- **Combustível (corrigido):** o "+0,072 fora do ano" da rodada 1 era quase todo tendência. Contra climatologia + tendência, o combustível do VIIRS (NDVI de fev–jun de t e t−1) acrescenta +0,020 (IC90 +0,001 a +0,042); a tendência sozinha vale +0,098. No portão de 30/set, o índice de combustível e secura com o SMAP dá +0,002 (IC90 −0,041 a +0,044) e ρ −0,03 entre anos: **sem habilidade no total do ano**. Dentro do ano, a ordem entre municípios tem ρ ~+0,2 (`v2_ecologo_indice_combustivel_rz.saida.txt`). O app mostra o combustível **em tercis, como mapa**, com a frase "sem habilidade comprovada no nível do ano", e nenhum número de focos previstos.
- **Novo, a leitura dos artigos confirma:** o ar seco do mesmo mês acompanha o fogo também no CE (anomalia de FRP do FIRMS × VPD do POWER, r +0,59), mas não a antecedência de 4 meses de Bezerra et al. (2026), nem o "ano úmido e depois seco" de Argibay et al. (2020), medido num ecótono do PI. No painel MCD64A1 do CE, os 6 anos "úmido e depois seco" de 25 não queimaram mais (−0,16 no log da área; p unilateral 0,66). Por isso ficam a data fixa do P5, o combustível como mapa e nenhuma previsão de focos (`pesquisa/viabilidade_artigos_nordeste.md`, Top 15, item 15).
- **Ponte verde (novo, grau C):** os pixels de lavoura ou mosaico ainda verdes em outubro (NDVI VIIRS ≥ 0,55) são onde a lagarta atravessa a seca. Em out/2026, 5,0% da lavoura (3ª maior de 15 outubros; mediana 3,4%). A geografia é fixa (90% da variância), então o mapa serve para posicionar armadilhas e a visita do técnico. A ponte de um ano não muda o milho do ano seguinte no PAM (+0,001 por dp; IC95 −0,036 a +0,037) (`v2_ecologo_ponte_verde_pragas.saida.txt`).

### M8. Redator com verificador

- **Papel:** redigir os textos dos cartões em PT e EN a partir do JSON.
- **Método:**
  - Os textos são redigidos **offline**, nesta sessão de trabalho, por um LLM (uso de inferência), com os números como marcadores `{var}` preenchidos pelo JSON. Depois são **congelados como estáticos**.
  - **Nenhuma API é chamada em tempo de execução.** O saldo da API da equipe acabou em 12/11, e a demo não pode depender de serviço externo.
- **Checagem de números** (cerca de 20 linhas, banca R2):
  - todo número dos textos de Quixadá precisa estar no JSON ou na folha 9.7 (lista branca);
  - léxico proibido: "garante", "vai chover", "certeza", "vai quebrar", "o solo do seu roçado", "o solo não engana";
  - bloqueia frequência do termômetro do solo entre agosto e meados de janeiro, exige "na sua região" em toda frequência e bloqueia "mais seco que 8 de cada 10 anos".
- **Regra:** nenhum modelo é treinado com saídas de LLM.

### Os 5 usos de SI que vão para o slide

1. Gêmeo físico FAO-56 calibrado contra o SMAP para estimar o estado da água (M1).
2. Curva de habilidade por portão e **por era**, medida sem olhar o futuro, com a luz principal escolhida por critério declarado (a pior era tem de passar), a segunda missão como confirmação, a regra **congelada com hash** para 2027 e o detector de caso inédito (M3).
3. Busca exata de estratégias pela cauda (CVaR), comparada com a prática atual, com placebo, piso declarado e freio de segurança (M4).
4. Sentinela de deriva e de qualidade de dado: deriva do Terra, NDVI deslocado nos dois sensores, relato copiado no PAM, percentil e duplicatas do SMAP (M6).
5. Redator LLM aterrado, com checagem numérica por lista branca e sem chamada em tempo de execução (M8).

### O que deliberadamente não usamos, e por quê

| Fica fora | Motivo, com dado |
|---|---|
| ML livre para prever rendimento no plantio | MSSS −0,37 no pré-safra: pior que a climatologia. |
| "Modelo grande" | Nenhum foi testado. Afirmamos só que a validação aleatória infla (0,49 contra −0,08). |
| **Floresta causal / DML sobre o PAM para "efeito da rotação"** | O protótipo à maneira de Kluger dá um efeito do feijão anterior de −0,056, e o **placebo do feijão futuro dá o mesmo** (−0,049): o PAM municipal não identifica o antecessor (`v2_pesquisador_ia_precrop_dml.saida.txt`). A floresta causal vai para o roteiro, na escala do talhão. |
| **Média sazonal do percentil pronto do SMAP (≤ 20 em fev–mai)** | A média de percentis diários comprime a escala (dp 14,7; p10 34): acende em 0,7% e pega 0 de 127 quebras em 2016. O mesmo produto lido no portão pega 64 (`v2_cetico_r2b_gatilho_carteira.saida.txt`, bloco 1). |
| **Soma desde 1/jan como luz de 2027** | Falhou em 2016–2025 (0,55 em 19/mar; 0,66 em 30/abr). Fica como regra antiga, por era. |
| **SMAP como luz que acende sozinha** | Contra a melhor leitura de chuva declarada, o ganho próprio é ~0 (+0,013 contra a chuva desde 1/fev, IC90 −0,04 a +0,08); em Quixadá, nenhum acerto. Entra só como confirmação. |
| **Emulador M2 na demo** | As previsões por município-ano não foram salvas; o ganho de ordem local não passou pelo teste contra só geografia. |
| **GLDAS nos portões** | GLDAS − chuva de −0,041 a +0,013 em 22 quadras; nada sobre o estado do IMERG (`v2_pesquisador_ia_gldas_portoes_longo.saida.txt`). |
| **NDVI como gatilho de portão** | O NDVI disponível no portão não soma à chuva (+0,015 e −0,008). Só no fim de safra. |
| **SMAP de novembro como preditor** | Anomalia de 10/nov → 01/fev: ρ +0,01 (SMAP, n = 11), +0,00 (Noah, n = 26). |
| **Atlântico Sul (TSA) como probabilidade** | Hipótese exploratória com n = 7 e contraprova de acaso 0,25. |
| **SMAP ao vivo ou global no app** | Fora do orçamento de 1 pessoa (seção 10). Fica 1 linha sobre a cobertura global. |
| Aprendizado por reforço, NSGA-II, Pareto em 8 eixos | O espaço de jogadas é pequeno: a enumeração é exata e auditável. |
| Downscaling do SMAP a 1 km/70 m | Habilidade espacial R² 0,083 (`sr_fundacao_r2_checagens.py`). |
| TVDI | R² 0,077 deixando o ano de fora (`sr_fundacao_downscaling_aprendido.py`). |
| NDVI absoluto e LST do Terra pós-2020 | Deriva e deslocamento (M6). |
| Dataset "Crop Recommendation" do Kaggle | Padrão de dado sintético (síntese 90.3). |
| Replay com as 44 temporadas do POWER | A chuva do POWER é reanálise. O replay usa só as 28 quadras do IMERG. |
| ECOSTRESS/ESI, Prithvi, SAR, EnKF, GNN de pragas, bot de WhatsApp | Sem dado em disco ou inviável em 36 h. Ficam no slide de próximos passos. |
| **Médias globais de meta-análise como número do sertão (novo)** | O Zhao (+20%) e as médias de continente são T2: dão só a direção. O "+32% em baixa produtividade" está só no resumo, sem intervalo. O número vem do cartão do Nordeste (+24%, B·T1) (`pesquisa/catalogo_rotacoes_comprovadas.md`, B3 e item 5). |
| **Os +28% ponderados pelo clima como número central (novo)** | Nenhum estrato do Franke tem clima parecido com Quixadá: a Savana da Guiné pesa 0,25, o Sahel 0,11 e a África Austral (Harare) 0,10. Antes da correção da Tmax, a conta dava +36%, puxada por Harare (w 0,41). Fica como sensibilidade (`notebooks/secoes_analogos/06_motor.py`). |
| **Cobertura de 60 dias antes do milho no sequeiro (novo)** | No balde, empurra a semeadura do milho para 15/03 e derruba P(sucesso) de 0,92 para 0,49 nos 184 municípios. Os ensaios que a sustentam (da Luz et al. 2023; Souza et al. 2024) foram irrigados. No sequeiro cabe só o revezamento tardio (`pesquisa/viabilidade_artigos_nordeste.md`, Top 15, item 9). |
| **Fator fixo de 0,79 na ET0 do POWER (novo)** | Contra as normais do INMET, a ET0 do POWER quase não tem viés (0,97–1,01). Só sensibilidade. |

---

## 6. O motor de rotação

### 6.1 Como gera as estratégias

1. **Biblioteca de componentes:**
   - anuais: milho, feijão/caupi, sorgo;
   - semiperene: mandioca;
   - perenes e forrageiras: palma, guandu, gliricídia;
   - arranjos: consórcio, revezamento, faixas;
   - manejo: palhada, aceiro, fogo ou não fogo.
   - **Novo, cardápio do MVP (15 culturas):** feijão-caupi, milho, feijão comum, mandioca, amendoim, sorgo granífero e guandu (alimento); sorgo forrageiro, milheto, palma forrageira, gliricídia e mucuna-preta (forragem e cobertura); algodão herbáceo, mamona e girassol (renda). **Quixadá tem 9 indicadas ou aptas** (recontado em 14/11 com as classes da v4 e o corte > 40: a lista não mudou): caupi, sorgo granífero e forrageiro, amendoim, algodão, mamona, mandioca, guandu e milheto. O milho e o feijão comum ficam "com risco", porque ali o ZARC nunca passa de 30% (`proposta/estrutura_gaez_zarc.md`, seção 5.1).
2. **Regras de sucessão que vêm dos dados:**
   - **No sertão não existe safrinha.** O caupi em revezamento cerca de 50 dias após o milho tem P(ISNA floração ≥ 0,5) de 0,89 na mediana estadual. Em sucessão após a colheita, 0,14, sem nenhum município viável (`agronomo_isna_zarc_sintetico.py`, bloco A4; grau C, limite superior). Pelo SMAP, a maior corrida úmida da quadra tem mediana de 95 dias: cobre o caupi de 75 dias em 69% dos município-anos e o milho de 110 dias em 43% (`v2_agronomo_smap_janelas.saida.txt`, bloco D).
   - **Na entressafra não cabe cultura anual sem água.** A ET0 de ago–dez (POWER) é de 1.224 mm, contra 59 mm de chuva. A sobra de água na colheita é de 85 mm depois do sorgo e de 4 mm depois da mandioca (`hidrologo_fao56_isna_pam.py`). O SMAP confirma: de agosto a dezembro, o primeiro metro fica perto do piso em 49% dos dias. Depois da mandioca, só palhada.
   - **Escape hídrico não é quebra de ciclo.** Trocar milho por sorgo mantém a gramínea hospedeira da lagarta-do-cartucho. A quebra de ciclo exige uma não-gramínea (caupi, mandioca, palma), com o status confirmado pelo técnico. O relógio térmico nunca para (cerca de 23 dias por geração em 2026).
   - **Maniva com a quadra estabelecida (novo, grau C):** a faixa nova de mandioca é plantada na janela ZARC da mandioca (Port. 11/2020: em Quixadá, risco de 20% de 01/02 a 10/03 e até 40% de 21/01 a 31/03; abril fica fora em 160 de 184 municípios do CE), nunca na 1ª chuva de janeiro: P(estabelecimento em 60 dias) de 0,36 em 21/jan e ≥ 0,7 de 11/fev a 01/mai na mediana estadual (`v2_agronomo_smap_janelas.saida.txt`, blocos A e D). A janela do SMAP corre tarde no milho, então pode ser 1–2 decêndios mais cedo.
   - **Troca em ano de luz acesa (grau C, refeita com 1998 e 2024):** pelo balde da rodada 1, a fração de municípios com água na floração do caupi semeado em 11/mar foi de 68% em 2016, **10% em 1998** e 100% em 2024. Semeado em 21/mar: 33%, 15% e 72%. O sorgo de 11/mar teve água em 10% dos municípios em 2016 e 1% em 1998, e por isso **sai da troca** (`v2_arquiteto_r2_fechamento.saida.txt`, bloco E). Em anos normais, o caupi de 21/mar teve água em 93% dos municípios. Leitura: **o caupi do início de março salva um ano como 2016, não um ano como 1998.** Contra um 1998, a proteção é o que já está no chão: a mandioca do ano anterior (Quixadá, 1998: mandioca 0,50 do normal; milho 0,00) e a forragem guardada.
   - **Cobertura no sequeiro (novo):** cobertura de 60 dias antes do milho não cabe (o milho atrasado perde 40% da chuva do ciclo, de 641 para 387 mm), e a semeadura de cobertura depois da colheita não tem água (63 mm medianos em 60 dias). No sequeiro cabe só o revezamento tardio (~50–85 dias depois do milho) ou a faixa perene, **sem bônus de grão**: em Melo et al. (2013), com mucuna, guandu e fava intercaladas no milho (sem crotalária nem braquiária), o +22% a +49% do resumo soma o efeito do NPK, e só a leguminosa não muda o grão com significância. Todo efeito de cobertura na cultura seguinte medido no Nordeste foi irrigado (da Luz et al. 2023; Souza et al. 2024) (`pesquisa/catalogo_rotacoes_comprovadas.md`, G12 e G17).
   - **Regras do catálogo de rotações (novo; `pesquisa/catalogo_rotacoes_comprovadas.md`, "O que o motor usa no Nordeste" e regras G01–G30):**
     - **Leguminosa antes do cereal solteiro:** +24% no ano colhido (faixa +2% a +49%; síntese do conselho; B·T1). As âncoras de artigo concordam: Franke +24% no Sahel e na Guiné; Mudare, leguminosa com MAT > 20 °C, +22% (+5 a +40). O sorgo usa a metade inferior da faixa, porque no Franke ele responde pouco (+11%, não significativo, n = 25).
     - **Só no ano colhido:** o bônus vale ~0 kg no ano de quebra. O milho quebra em 20,2% dos município-anos do CE e em 21,0% no NE (2000–2024, mediana da mesma janela). As meta-análises excluem o rendimento zero.
     - **A aridez não reduz o efeito relativo:** o centro fica; no ano seco, o intervalo alarga até 0; o que cai é a t/ha e a chance de colher.
     - **Base certa ou nada:** os priors de leguminosa foram medidos contra base **sem** leguminosa. Contra o consórcio milho + feijão (S0), a troca para rotação no tempo não foi medida: central 0, sensibilidade de 0 a +9% (D·T3).
     - **Comparáveis obrigatórios sem leguminosa:** pousio → milho +31% e sorgo → milho +28% (C·T2, só direção); caupi → milho contra milho contínuo, +14,7% (B·T2). Não retirar o pousio sem balanço hídrico.
     - **Sequência inteira:** milho-sorgo no lugar de sorgo contínuo é **alerta C** (−32% na sequência; n = 10), não veto.
     - **Gliricídia longe do grão:** em Taperoá-PB (~600 mm), o N no grão do caupi caiu de 18,04 para 1,58 kg/ha entre fileiras de gliricídia, e o N fixado pelo caupi, de 11,22 para 1,08 (Tab. 2); junto ao milho + caupi, a gliricídia não tirou N do ar (0%), contra ~52% com buffel ou palma (%Ndfa, Tab. 1). O rendimento do caupi (410 contra 36 kg/ha, Tab. 1) não difere pelo teste. A gliricídia vira banco de forragem e proteína, em faixa afastada do grão (Martins et al. 2015; grau C).
3. **Restrições:**
   - **janela do ZARC oficial 2026/27, que é o limite** (por solo e ciclo; se o solo for desconhecido, a faixa entre o mais restritivo e o mais permissivo). A janela sintética tipo-ZARC (±1 decêndio no caupi; incerteza maior no milho e no sorgo) fica como checagem; contra o oficial, o veredito depende do solo (M1);
   - **aptidão GAEZ > 40 (classe "média" ou melhor da v4; sequeiro, insumo baixo)** só para as culturas sem ZARC na tábua do CE (mandioca, guandu, milheto); palma e gliricídia não têm camada no GAEZ;
   - semente e maniva disponíveis antes da data-limite;
   - água azul declarada;
   - mão de obra e consumo da família;
   - **regras do Garantia-Safra, conferidas na Lei 10.420/2002** (página do Planalto, lida pela ferramenta web em 14/11): perda ≥ 40% (art. 8º, redação da Lei 15.236/2025); área plantada **máxima** de 5 ha (art. 10, IV, redação da Lei 12.766/2012); renda de até 1,5 salário mínimo (art. 10, III); até 4 módulos fiscais (art. 10, V). O inciso VI (veto a quem irriga) foi revogado pela Lei 12.806/2013. Dona Francisca (3 ha) cabe. **Não conferidos:** a cesta de culturas e o que acontece com quem planta fora do ZARC (a conferir na portaria e nas regras do Proagro e do Garantia-Safra). O José abre a página do Planalto antes de qualquer slide.
4. **Avaliação:** cada estratégia é reencenada nas 28 quadras do IMERG. As sequências de 3 anos são **planos**: cada ano é avaliado na quadra do replay, e o efeito do antecessor (leguminosa, palhada) entra como prior da literatura com grau. **Novo:** o prior sai do catálogo de rotações (147 cartões), só com transferência T0 ou T1, e o recibo mostra o peso de clima w do estudo (seção 7, inovação 8). O estado do solo entre anos não é simulado no MVP; a memória de novembro até fevereiro é nula (ρ +0,01), então essa simplificação custa pouco na água.
5. **Escolha:** a atual sempre entra. As outras 3 cobrem perfis distintos: calendário (S1, que protege contra um ano como 2016), cauda (S2, que protege contra um ano como 1998) e solo (S3). No MVP a ordem é fixa; os pesos da família ficam para a próxima versão. **Novo:** para a família da demo, as peças das três viram um plano por faixas, 2027–2029 (6.4).
6. **A frase do slide 3:** *"In a one-window climate, rotation happens inside the season (relay, strips) and across years (legume, cassava, perennials, fallow without fire)."*

**Métricas de cada cartão:**
- **Calculadas (3):** chance de colher menos da metade; "pior ano em 10"; mediana.
- **Etiquetas com grau:**
  - uso de água: água verde, água azul e sobra para a entressafra;
  - forragem: kg MS, literatura, grau C;
  - fixação de N: como ganho de rendimento no cereal seguinte, grau B·T;
  - erosão: meses de solo nu × erosividade (I30 do IMERG, até 80 mm/h) × declive (NASADEM);
  - matéria orgânica: grau C;
  - mercado: teto de participação, PNAE/PAA;
  - ciclos: meses sem gramínea hospedeira, sem queima.

### 6.2 Exemplo concreto: Quixadá (Sertão Central), novembro de 2026

**Graus:**
- **A:** validado com dado local observado, por ano.
- **B:** meta-análise ou síntese multi-sítio; ou poucos anos/episódios com dado local.
- **C:** modelo, simulação, ensaio único ou ordem validada sem nível validado.
- **D:** suposição ou resumo de congresso.
- **·T:** transferido de outro clima; rebaixa meio grau.
- **·T0 a ·T3 (novo, no catálogo de rotações):** T0 = medido no semiárido brasileiro; T1 = análogo medido no estrato de aridez 0,2–0,5 e temperatura média ≥ 20 °C, com pelo menos 5 sítios; T2 = só a direção; T3 = não transfere. O motor usa número só com T0 ou T1. No catálogo, o grau mede a força no domínio do estudo, e o T, a transferência; os dois ficam separados, para não penalizar duas vezes (`pesquisa/catalogo_rotacoes_comprovadas.md`, "Como ler").

**Família de demonstração, fictícia e rotulada como tal:** Dona Francisca, Quixadá, 3 ha (1 ha de baixio pelo SRTM), 8 cabras, cisterna de 16 m³ (água de beber; o volume é parte da ficção, grau D: nenhum texto lido confirma volumes de cisterna), sem barreiro, semente própria de milho e feijão, **sem mandioca no chão hoje**. Prioridades: forragem > comida da família > renda.

**Contexto do município** (`arquiteto_final_curvas_quixada.saida.txt`, bloco C; `v2_arquiteto_r2_fechamento.saida.txt`, blocos D, E e G; definição canônica):
- **Milho:** 8 quebras em 28 anos: 1998 (0,00), 2001, 2012 (0,17), 2015, 2016 (0,12), 2023 (0,36), 2024 (0,46) e 2025 (0,30). Grau A.
- **Feijão:** 5 quebras em 28 anos; 0,15 do normal em 2012. Grau A.
- **Milho + feijão (S0):** 6 dos 28 anos abaixo da metade do normal (1998, 2012, 2015, 2016, 2023, 2025); pior ano em 10 = 0,16 (1998, 2012, 2016); mediana 1,05. Grau A, "seu município".
- **Mandioca:** só 10 anos têm as três culturas, todos entre 1998 e 2010. A área foi 0 ha em 2012–2013 e 40 ha em 2016, então **não há mandioca observada nos piores anos depois de 1998** e a carteira do município não é calculável.
- **Datas-limite da janela sintética** (risco ≤ 30%): milho até 01/mar (incerteza maior que ±1 decêndio: o SMAP dá 21/abr, sem validação); caupi até 21/mar (±1 decêndio) em ano normal. Em ano de luz acesa, até ~11/mar, se ainda houver umidade (em 2016, o caupi de 11/mar teve água em Quixadá e o de 21/mar não; em 1998, nenhum dos dois). Grau C.
- **Conferidas com o ZARC oficial 2026/27 (novo; refeito em 14/11 à tarde, R3.5):** o decêndio do milho de 01/mar (01–10/mar) aparece no oficial só em AD5–AD6 do Grupo I (os solos que guardam mais água), com risco de 30%; em nenhum solo ou ciclo o milho chega ao risco de 20%. O caupi de 21/mar fica a ±1 decêndio do oficial (risco ≤ 30%) em 8 das 9 combinações de solo e ciclo, contando todos os grupos. Só o Grupo I tem cultivar indicada (Port. 121/2026), e com ele são 2 de 3: no arenoso e no médio, confere; no argiloso, o oficial vai até 20/abr. **A frase do caupi fica**, dizendo o solo (`pesquisa/viabilidade_artigos_nordeste.md`, 4.3 e seção 5).
- **O que cabe em Quixadá (novo; GAEZ no ponto interno do município, com 1 casa decimal e as classes da v4; ZARC de sequeiro 2026/27, 9 portarias, uma por cultura (caupi 121, milho 218, sorgo granífero 270, sorgo forrageiro 297); só os ciclos com cultivar indicada no caupi e no sorgo forrageiro; união dos solos, a leitura mais permissiva; saída de `scripts/gaez_zarc_municipio.py 2311306`):**

  | Cultura | Aptidão GAEZ, insumo baixo | ZARC, risco 20% | ZARC, risco ≤ 30% |
  |---|---|---|---|
  | Sorgo forrageiro | 65,7 (boa) | 21/02–30/04 (3 de 3 solos, Grupo I) | 11/02–10/05 |
  | Sorgo granífero | 65,7 (boa) | 11/02–20/04 (9 de 9 solos × ciclos) | 01/02–30/04 |
  | Mandioca | 66,1 (boa) | ZARC plurianual (Port. 11/2020), fora da tábua aberta | 01/02–10/03 a 20%; 21/01–31/03 até 40% (abril fora) |
  | Guandu | 62,0 (boa) | fora da tábua aberta do ZARC | — |
  | Feijão-caupi | 54,0 (média) | 11/03–20/04 (3 de 3 solos, Grupo I) | 01/03–20/04 |
  | Milho | 55,7 (boa) | nenhum | 11/02–10/03 (a janela inteira só em AD5–AD6 do Grupo I) |
  | Feijão comum (*Phaseolus*) | 58,4 (boa) | nenhum | 11/02–20/03 (feijão 2ª safra; só AD4–AD6) |

  - **Núcleo seguro: caupi e sorgo**, com aptidão média ou boa e risco de 20% em todos os solos. O caupi só chega a 20% a partir de 11/mar; antes disso, fica em 30% (desde 01/mar) ou 40% (desde 21/jan). A mandioca é a mais apta no insumo baixo (66,1, logo acima do sorgo, 65,7) e tem ZARC só na portaria plurianual (Port. 11/2020).
  - **Duas datas, nada em janeiro:** o ZARC 2026/27 só zoneia alguma cultura a partir de 21/jan, e a 40% (algodão, amendoim, caupi e sorgo granífero). O risco de 30% começa em 01/fev e o de 20% em 11/fev (algodão, amendoim e sorgo granífero). O milho entra em 11/fev, a 30%. A prática de plantar milho + feijão na 1ª chuva de janeiro (S0) fica fora do zoneamento: o milho só entra em 11/fev, e o feijão comum em 01/fev, a 40%. *A conferir:* a portaria e as regras do Proagro e do Garantia-Safra sobre plantio fora do ZARC (`proposta/estrutura_gaez_zarc.md`, seção 5).
- **Placar das luzes em Quixadá** (o que o técnico vê):
  - **luz principal, chuva desde 1/fev (28 anos):** em 19/mar, 9 alertas e 3 acertos (1998, 2015, 2016); em 30/abr, 9 alertas e 5 acertos (1998, 2012, 2015, 2016, 2025). Perdidas em 30/abr: 2001, 2023 e 2024;
  - **regra antiga, desde 1/jan:** 8 alertas e 2 acertos em 19/mar; 7 e 3 em 30/abr;
  - **segunda missão, SMAP (2016–2025): nenhum acerto.** Em 30/abr, 2016 e 2025 tiveram os dois menores valores do dia na década (p20,1 e p20,3), logo acima do limiar 20. O único vermelho da década em Quixadá foi falso (2021, 30/abr);
  - tudo isso é grau A e é mostrado assim mesmo: o alerta é regional.
- **O que a NASA viu nas quebras de 2023–2025** (auditoria):
  - **2025:** chuva a 93% do normal em 30/abr, mas o solo no fundo da década (p20,3) e o NDVI VIIRS de mar–mai entre os 3% mais baixos do estado (0,93 do normal). Seca de fim de quadra, vista tarde (`v2_estrategista_viirs_quixada.saida.txt`).
  - **2023:** chuva a 104% e solo p66 em 30/abr; maio teve 22 mm, e os vizinhos também quebraram (35% dos 20 vizinhos a menos de 0,3°; 5 de 5 a menos de 50 km). Possível fim de chuva depois do portão; NDVI verde (`v2_hidrologo_smap_portoes_quebra.saida.txt`; `v2_sr_fundacao_escala_real.saida.txt`, D).
  - **2024:** chuva a 105%, solo p70, NDVI verde (1,05), **nenhum vizinho quebrou** e a área plantada caiu de 5.000 para 2.800 ha. Sem assinatura hídrica nem de vegetação: "o satélite discorda do árbitro; confirmar praga, relato ou área com o técnico".

#### S0. Atual: "roçado da 1ª chuva" (igual em 2027, 2028 e 2029)

- **Prática:** milho + feijão consorciados plantados na 1ª chuva de 20 mm ou mais em 3 dias. Broca e queima em out–dez; solo nu de setembro a janeiro.
- **Por que aparece:** é a linha de base. O PAM do município mostra que é a prática dominante, e a família confirma.
- **Evidência:**
  - **Seu município (Quixadá, 28 anos, IBGE):** milho + feijão abaixo da metade do normal em 6 anos (2 em 10); pior ano em 10 = 0,16; mediana 1,05. O milho sozinho quebra em 8 de 28 anos (grau A).
  - Milho e feijão quebram juntos no PAM (0,78; grau A, com a ressalva do relato).
  - **Estado:** milho + feijão tem "pior ano em 10" de 0,26 e 15% de chance de colher menos da metade (grau A).
  - Plantar com o perfil úmido não protege: no dia de semeadura da regra do agricultor, o tercil úmido do SMAP quebrou o milho em 15,5% dos casos, contra 11,4% no seco (`v2_agronomo_smap_portoes.saida.txt`, P2).
- **Benefícios:** custo zero, semente própria, mercado conhecido.
- **Lacunas:** a água disponível do solo do roçado e a data real de plantio.
- **Riscos a confirmar:**
  - solo nu sob chuva erosiva;
  - perda de carbono com a queima. **Medido em Sobral (Sacramento et al. 2013; grau C):** de 2002 a 2011, a broca com queima perdeu 58,87 Mg/ha de C no solo (0–40 cm). A base de 2002 vem de outro estudo, e os estoques iniciais dos sistemas diferiam. **Cenário de modelo (Primo et al. 2023; grau D):** −50% em 10 anos sem pousio, numa simulação Century; o local não foi verificado no texto;
  - fuga do fogo para os vizinhos;
  - nenhum mês sem gramínea hospedeira;
  - **plantio fora do ZARC (novo):** em Quixadá, o ZARC 2026/27 só zoneia alguma cultura a partir de 21/jan (a 40%), o risco de 20% só aparece em 11/fev, e o milho só entra em 11/fev; plantar milho + feijão na 1ª chuva de janeiro fica fora do zoneamento (a conferir na portaria e nas regras do Proagro e do Garantia-Safra).

#### S1. "Escalonar, guardar a decisão e revezar em faixas" (custo zero; o escudo de um ano como 2016)

- **2027:**
  - Metade da área na 1ª chuva firme (milho + feijão).
  - **A outra metade fica guardada:**
    - **em ano de mar como o de 2027:** decisão em ~10/mar. Se a chuva desde 1/fev estiver acesa e o técnico confirmar umidade para a semente, caupi até ~11/mar. Se não houver umidade, a metade não recebe grão e fica com palhada, sem custo de semente. Se estiver verde, plano normal;
    - em ano normal: milho, se a chuva firmar antes de 01/mar; caupi até ~21/mar, se a luz acender em 19/mar.
  - Caupi em revezamento cerca de 50 dias após o milho.
  - Entressafra com palhada roçada, sem queima.
- **2028:** as faixas trocam de lugar: onde houve milho entra caupi/feijão, e vice-versa (gramínea ↔ leguminosa).
- **2029:** as faixas trocam de novo. A palhada e a ausência de fogo continuam.
- **Por que aparece:** janeiro engana (Quixadá teve 150% do normal em jan/1998 e 197% em jan/2016, e os dois anos quebraram). Escalonar mantém uma opção aberta até o último portão de troca. **Novo:** o início da estação também engana: nos 3 anos de El Niño forte da série de início (2010, 2016 e 2024), a chuva começou antes do normal no estado (mediana no dia 6, contra 18 nos anos neutros e 15 em todos os demais; n = 3 anos), mas o sinal muda de município para município (2.1, item 6) (`notebooks/secoes_analogos/05_ciclo_plantio.py`).
- **Evidência:**
  - **Pior ano, chance de < 50% e mediana da S1: sem número.** Não existe S1 observada no PAM, e o balde não vê a quebra do milho de 1998 (96% dos municípios com água pela simulação, contra 25% sem quebra no IBGE). Uma cauda simulada seria enviesada justo no ano que importa (R2.2, linha 12).
  - **A metade guardada nos três El Niños fortes da era IMERG** (balde da rodada 1, grau C; `v2_arquiteto_r2_fechamento.saida.txt`, bloco E):

    | Quadra | Milho da 1ª chuva sem quebra (IBGE) | Caupi de 11/mar com água na floração (balde) | Caupi de 21/mar | Chuva desde 1/fev acesa em 10/mar |
    |---|---|---|---|---|
    | 1998 | 2,5 em 10 | **1 em 10** | 1,5 em 10 | 94% dos municípios |
    | 2016 | 3 em 10 | **7 em 10** | 3 em 10 | 100% |
    | 2024 | 9 em 10 | 10 em 10 | 7 em 10 | 0% |

  - Leitura: a troca do início de março teria colhido algo em 7 de 10 municípios em 2016. Em 1998, não havia água nem para o caupi; o que a metade guardada poupa nesse caso é semente e trabalho, não colheita. Em 2024, a luz verde em 10/mar mandaria seguir o plano normal, e o milho foi bem. São 3 anos, e as colunas misturam o observado (IBGE) com a simulação (balde).
  - Em 19/mar, o caupi ainda cabe em 98% dos municípios na janela sintética, e o milho em 42% (grau C).
  - Caupi em revezamento em Quixadá: P 0,75, contra 0,14 em sucessão (grau C, limite superior, porque o balde não modela competição).
- **O que o cartão diz com honestidade:**
  - Em Quixadá, a luz principal acertou 3 de 9 alertas em 19/mar, e o SMAP nunca acertou.
  - O efeito do falso início no PAM não é significativo com erro-padrão agrupado por ano (`cetico_r2_checagens.py`, bloco B).
  - O valor da opção guardada não foi medido no PAM; é grau C.
- **Benefícios:** custo zero; parte da área decide com mais informação; o caupi dá N e proteína.
- **Lacunas:** o replantio não está modelado; a semente de caupi precisa chegar **antes de ~10/mar** em 2027.
- **Riscos a confirmar:** arrependimento num ano bom, quando quem plantou tudo colhe mais; ficar fora da janela do ZARC oficial. **Novo:** em Quixadá, a metade plantada na 1ª chuva só fica dentro do ZARC 2026/27 com risco de até 30% a partir de 11/fev no milho (só em AD5–AD6) e no feijão comum, e a partir de 01/mar no caupi (antes, o caupi tem 40%). A metade guardada para ~10/mar cai no começo da janela de 20% do caupi (11/mar a 20/abr, na união dos solos do Grupo I, o único com cultivar indicada). A mensagem é "plante escalonado", nunca "não plante".

#### S2. "Tampão e forragem em faixas que giram" (escudo do ano ruim)

- **Desenho:** três faixas que trocam de lugar a cada ano:
  - **mandioca:** uma faixa nova recebe maniva a cada quadra, **na janela ZARC da mandioca (Port. 11/2020: em Quixadá, risco de 20% de 01/02 a 10/03 e até 40% de 21/01 a 31/03; abril fica fora em 160 de 184 municípios do CE)** (nunca na 1ª chuva de janeiro), e a mandioca do ano anterior é o tampão do ano, colhida conforme a necessidade;
  - **sorgo forrageiro** com rebrota, como primeira cultura, mais palma adensada no cercado;
  - **caupi precoce** de 60–70 dias.
  - O milho fica só no baixio.
- **Giro das faixas:** a faixa que sai da mandioca recebe caupi, e a do caupi recebe sorgo. Assim sempre há mandioca de um ano no chão. Nenhuma faixa queima.
- **2027, dito com honestidade:** a mandioca precisa ser plantada **no ano anterior** para proteger o ano seco. Sem mandioca no chão hoje, o tampão de Dona Francisca começa em 2028. Em 2027, a proteção vem do sorgo, da palma, do caupi e das ações do P1.
- **Por que aparece:** a prioridade da família é forragem, e o risco do sistema atual está na cauda.
- **Evidência:**
  - **Contra a prática atual:** no estado, a carteira 1/3 milho, 1/3 feijão e 1/3 mandioca leva o "pior ano em 10" de **0,26 (milho + feijão) a 0,36**, e a chance de colher menos da metade de 15% para 11%. São 2.495 município-anos, só onde a mandioca existe. **É um teto:**
    - o placebo do vizinho já dá 0,335, então a parte própria da mandioca fica entre +0,02 e +0,08 (grau B);
    - a carteira real dos municípios entrega cerca de 65% do ganho por cultura;
    - o piso é 0,32 se a maniva faltar.
  - **Nos anos em que a luz NASA acendeu em 30/abr:** pior ano em 10 de 0,13 na S0 e 0,21 na 1/3 (ganho com IC90 por ano de +0,04 a +0,10; n = 585 município-anos, 17 anos).
  - **Replay de 1998 em Quixadá, observado pelo IBGE:** milho 0,00, feijão 0,16, mandioca 0,50. A carteira 1/3 ficou com 0,22, contra 0,08 de milho + feijão. É um ano só (grau A, n = 1). É também o ano em que a S1 não ajudaria (caupi de 11/mar com água em 1 de 10 municípios): a S2 é o escudo de um ano como 1998.
  - O sorgo tem P(ISNA floração < 0,5) de 6,5%, contra 10,1% do milho (grau C). O PAM do sorgo não serve de evidência: são 21 municípios tecnificados.
  - **Palma + sorgo (corrigido na v3):** Diniz et al. (2017), Serra Talhada-PE, média de 5 regimes de água, 4 deles com gotejo de água salina; ensaio único, grau C. O 6.279 é o **IPS** (índice de produtividade do sistema, em kg MS/ha equivalentes de palma), comparado com os 4.627 da palma solteira. Em matéria seca, o consórcio rendeu 12.130 kg/ha (3.573 de palma + 8.557 de sorgo): 2,6 vezes a palma solteira e sem diferença do sorgo solteiro (14.073 kg/ha, mesma letra). O LER de 1,51 é a média dos 5 regimes. O ganho é de terra (duas culturas no mesmo chão), não de superar o melhor solteiro.
  - **O que não usamos como evidência:** o "+6,6 p.p. dos municípios mais diversos" (seção 8.2). É composição (menos milho e feijão) e culturas fora do sequeiro; só com sequeiro, +1,4 p.p. (n.s.).
- **Benefícios:** forragem para as cabras no ano seco; comida da família na mandioca; solo coberto mais tempo.
- **Lacunas e riscos, nesta ordem:**
  1. **Maniva-semente guardada / banco de manivas.** Na seca, a mandioca some: Quixadá teve 0 ha em 2012 e 40 ha em 2016. A carteira estadual existe em 116 de 181 municípios em 1998, 104 em 2012 e 69 em 2016.
  2. Casa de farinha e mercado da mandioca. O hedge de preço (−0,80) é estadual; no município, a elasticidade é cerca de zero.
  3. Semente e mercado do sorgo: a área de sorgo em grão do Ceará caiu de 2.900 ha em 2021 para 15 ha em 2025 (`economista_debate_checagens.py`).
  4. Palma resistente à cochonilha (pergunta obrigatória ao técnico).
  5. O sorgo hospeda a lagarta: é escape hídrico, não quebra de ciclo.

#### S3. "Leguminosa que fica, sem fogo" (rotação no sentido estrito)

- **2027:** caupi, com guandu ou gliricídia em **faixa forrageira em nível, afastada do grão** (declive pelo NASADEM). Roçagem, palhada e aceiro, sem queima. **Corrigido na v3:** a v2 punha o caupi entre faixas de gliricídia; em Taperoá-PB, o N no grão do caupi caiu de 18,04 para 1,58 kg/ha entre as fileiras, e a gliricídia não tirou N do ar junto ao grão (Martins et al. 2015; grau C; seção 6.1).
- **2028:** milho ou sorgo sobre a palhada da leguminosa, com caupi em revezamento.
- **2029:** mandioca, ou milho + caupi. As faixas perenes ficam.
- **Entressafra:** só palhada e perene de raiz funda.
- **Por que aparece:** é a única estratégia de rotação no sentido estrito e ataca nitrogênio, erosão, matéria orgânica e ciclo da lagarta ao mesmo tempo. **Não é o escudo do pior ano** (rodada 2).
- **Evidência:**
  - **Leguminosa antes do cereal (refeito na v3 com o catálogo):** caupi antes de milho ou sorgo **solteiro**, em sequeiro quente e sem adubo nitrogenado, rende +24% no ano colhido (faixa de +2% a +49%). É síntese do conselho, grau B·T1; as âncoras de artigo concordam (Franke et al. 2018: +24% no Sahel e na Guiné; Mudare et al. 2025: +22% com temperatura média > 20 °C). O sorgo fica na metade inferior da faixa. As médias globais (Zhao et al. 2022: +20%) dão só a direção (T2), e o "+32% em baixa produtividade" do Zhao está só no resumo, sem intervalo (`pesquisa/catalogo_rotacoes_comprovadas.md`).
  - **A aridez não reduz o efeito relativo (corrigido na v3).** A v2 dizia "efeito menor na zona árida". No Franke, o Sahel e a Guiné dão o mesmo +24% (zona × resposta, p = 0,351). O que cai no seco é a t/ha e a chance de colher; no ano seco, o intervalo alarga até 0.
  - **Contra a prática atual, não medido.** Os +24% valem contra cereal solteiro. Contra o consórcio milho + feijão (S0), a troca para rotação no tempo nunca foi medida: central 0, sensibilidade de 0 a +9% (D·T3). É a lacuna que mais muda o ranking.
  - **De onde vem a evidência, medido com a NASA (novo; refeito com a Tmax média, R3.5):** pela assinatura de clima do POWER, os celeiros temperados têm peso w = 0,00 para Quixadá, e nenhum ensaio de rotação no tempo do catálogo vem de clima de sertão. O de clima mais parecido é o soja → milho de Bom Jesus-PI, no Cerrado (w 0,95): deu efeito nulo e é T2, só direção. **Nenhum número de rotação T0/T1 vem de clima parecido:** o Franke da África Austral (+42%) caiu de w 0,41 para 0,10. Ponderado pelo clima, Quixadá ficaria em cerca de +28% (soma dos pesos 0,46; +29% a +31% entre as mesorregiões). **O motor fica com os +24% e usa os +28% só como sensibilidade**, porque nenhum estrato do Franke tem w ≥ 0,3 (o maior é a Savana da Guiné, 0,25) (`notebooks/secoes_analogos/06_motor.py` e `04_aptidao.py`).
  - Rotação diversa em ano de seca, em clima temperado: rendimento 14,0% a 88,9% **maior** no ano de seca, em 9 sítios dos EUA (Bowles et al. 2020, corpo do artigo; o resumo fala em perdas 14,0% a 89,9% menores). Grau B·T; o catálogo marca T3: não transfere.
  - **O artigo-âncora (relido na v3):** em Kluger et al. (2025), o benefício do antecessor foi maior sob mais chuva, e a leguminosa antecessora rendeu menos sob calor. O efeito do calor foi medido dentro de cada região, ano a ano; entre climas, o efeito da temperatura some no Zhao quando se controla o país. Por isso o catálogo não desconta o prior pelo calor, e o ano quente de El Niño fica como hipótese, grau C (`pesquisa/catalogo_rotacoes_comprovadas.md`, conflito 8 e regra G13). Grau B·T.
  - **Carbono (corrigido na v3):** medido em Sobral (Sacramento et al. 2013; grau C), a agrofloresta **perde menos** carbono do solo (0–40 cm) que a broca com queima, em relação a 2002: −23,87 Mg/ha no silvipastoril e −8,13 no agrossilvipastoril, contra −58,87 no tradicional. Pela Tab. 5, o agrossilvipastoril dá 5,13, não os 8,13 impressos. Isso não quer dizer que a agrofloresta tem mais carbono: os estoques iniciais diferiam (127 contra 77 Mg/ha), e em 2011 eram 68,2 no tradicional e 71,6 no agrossilvipastoril. A base de 2002 vem de outro estudo, e a vegetação nativa subiu +9,6 no período. O "recupera em cerca de 10 anos" de Primo et al. (2023) é simulação Century, com local não verificado: grau D, só como cenário. Nunca misturar os Mg/ha do campo com os do modelo.
  - Chuva erosiva de fevereiro com I30 de até 80 mm/h (síntese 90.2; grau A).
- **No replay e no cartão:** "sem número de pior ano". O efeito do antecessor aparece como "+24% no ano colhido, contra milho solteiro (B·T1); contra a sua prática atual, não medido".
- **Benefícios:** milho de 2028 em diante sobre solo melhor; banco de proteína para as cabras; menos fogo e menos erosão; meses sem gramínea hospedeira.
- **Lacunas:** não existe ensaio revisado de rotação no semiárido do Ceará, e o PAM não identifica o efeito do antecessor (o placebo falha; seção 5). O painel PAM × IMERG do catálogo confirma: no CE, corrigido pelo placebo do ano seguinte, cada 10 pontos percentuais a mais de leguminosa no ano anterior mudam o milho em +0,18% (IC95 −5,01 a +5,37), abaixo do efeito mínimo detectável (7,1%) (`pesquisa/catalogo_rotacoes_comprovadas.md`, "O que os nossos dados mostraram", 1). O efeito real da leguminosa contra o consórcio de hoje é a lacuna que mais muda o ranking, e o ensaio mais barato que a responde é o de **faixas que trocam de lugar** num município do sertão (seção 6.4).
- **Riscos a confirmar:**
  - **competição por água, agora com dado:** na entressafra o primeiro metro de solo está seco (W < 0,1 em 49% dos dias), então a perene vive de água abaixo de 1 m, que o SMAP não vê. Pelo GLDAS Noah, a camada de 1–2 m tem ciclo de só 36 mm e acompanha o abril do mesmo ano (ρ +0,90): recarrega menos justamente no ano seco (`v2_agronomo_smap_janelas.saida.txt`, bloco E). A literatura dá cerca de −4% de rendimento com cobertura (Abdalla et al. 2019; grau B·T);
  - mão de obra para implantar e 1–2 anos para estabelecer;
  - se o caupi local é hospedeiro secundário da lagarta.

### 6.3 O plano vivo de 2027 para Dona Francisca

| Portão | O que o QUADRA diz | Evidência |
|---|---|---|
| **P1, hoje (14/nov)** | "O mar está mais quente do que em qualquer ago–out já medido. Num ano qualquer, 2 de cada 10 municípios da região perdem metade do milho. No El Niño mais forte antes deste, cerca de 5 de cada 10 (faixa de 2 a 8); em 1998 e 2016, 7 em 10; em 2024, menos de 1 em 10. Este ano está além do recorde. O solo está seco como em todo novembro, e isso não diz nada sobre a quadra." Ações sem arrependimento: semente de caupi precoce **até dezembro**, procurar maniva para fevereiro, garantir a palma, manter a adesão ao Garantia-Safra, aceiro e palhada em vez de queima. | Modelo único, ano fora: P(2,04) = 0,54 (IC90 0,24–0,75); em 2,46, 0,62 por extrapolação (`v2_clima_portao_novembro_2027.saida.txt`). Na última década, o ONI de novembro teve AUC 0,72, igual à melhor chuva de São José (`v2_arquiteto_r2_fechamento.saida.txt`, A). Contagens: 4 de 7 quadras secas desde 1966; 3 de 5 pelo POWER desde 1982; 2 de 3 catástrofes na era IMERG. SMAP de novembro → fevereiro: ρ +0,01. Banco regional normal (GRACE p57). |
| **P2, janeiro–fevereiro** | "Plante uma parte agora e guarde a outra. Chuva boa em janeiro não garante a quadra: em 2016, janeiro teve cerca do dobro do normal e 7 de cada 10 municípios perderam o milho." No fim de fevereiro: "ainda é cedo". **Novo:** "No ZARC deste ano, em Quixadá, o milho só entra a partir de 11 de fevereiro; confirme a data e o solo com o técnico." | 31/jan: AUC da soma 0,63 (1998–2015) e 0,27 (2016–2025). 28/fev: 0,71 e 0,46; chuva desde 1/fev 0,65 e 0,66. Em El Niño forte, o início da chuva veio antes no estado (dia 6 contra 18 nos anos neutros e 15 em todos os demais; n = 3 anos); em Quixadá, veio depois (+24 dias), sem se separar do acaso. ZARC 2026/27: zoneado (a 40%) só a partir de 21/jan; risco de 20% a partir de 11/fev; milho a partir de 11/fev, a 30%, só em AD5–AD6 (a conferir). |
| **Início de março (~10/mar)** | "Com o mar deste ano: se a chuva desde 1º de fevereiro estiver abaixo de 75% do normal e ainda houver umidade, a metade guardada vai para o caupi até ~11 de março. Se não houver umidade, ela fica sem grão. Confirmar com o técnico: a semente chegou?" | Chuva desde 1/fev acesa em 10/mar: 94% dos municípios em 1998, 100% em 2016 e 0% em 2024 (descritivo, n = 3). Caupi de 11/mar com água: 7 em 10 municípios em 2016 e 1 em 10 em 1998 (balde, grau C). |
| **P3, 19/mar** | Luz em quatro estados. "Vermelho: a chuva e o solo dizem seco. Amarelo: só a chuva diz seco. Caupi só se ainda couber; sem sorgo de grão." Cinza-amarelo: "os dois instrumentos discordam; o técnico decide". | 2016–2025: vermelho 5,3 em 10 quebram; amarelo 2,1; verde 0,9. Em 2022, a chuva acendeu em 142 municípios e o SMAP em nenhum (3 quebras). Em Quixadá, 3 acertos em 9 alertas da chuva e nenhum do solo. O teste da tradição está na seção 7, inovação 5. |
| **P4, 30/abr** | "É quando o solo mais confirma." Ação graduada: guardar forragem, segurar a venda dos animais, cortar o milho para as cabras se a luz se repetir e o técnico confirmar. Sem salvamento com água: a cisterna é de beber (o volume de 16 m³ é da família fictícia, grau D). | 2016–2025: vermelho 4,1 em 10; amarelo 3,4; verde 0,8. Em 2016, o SMAP acendeu em metade do estado (91 de 182). **Em 30/abr só cabe salvar; por isso, em 2027, a proteção vem de P1, P2 e do início de março.** |
| **Junho** | "Verde do satélite em abril–maio: {x}% do normal do seu município. Quando ficou abaixo de 90%, 7 a 8 de cada 10 municípios perderam mais da metade do milho. O IBGE confirma no ano que vem." | VIIRS NDVI abr–mai, testemunha, grau A como testemunha (`v2_designer_verde_viirs.saida.txt`). |
| **P5, até 31/ago/2027 (data fixa)** | "O fogo vem pelo calendário; a decisão é antes de setembro." Palhada, aceiro, fenação do excedente se a quadra vier verde, perene em nível. Nova faixa de maniva na quadra de 2028 (fevereiro a abril). | 27% dos focos até 30/set e 72,9% em out–dez (`v2_ecologo_calendario_fogo.saida.txt`). Combustível como mapa em tercis, sem previsão de focos. |

**Cartão da família no P1 (imagem; no máximo 3 números):** "Quixadá, 14 de novembro de 2026. O solo está seco como em todo novembro: isso é normal e não diz nada sobre a quadra. O mar está mais quente do que em qualquer agosto–outubro já medido. Num ano qualquer, 2 de cada 10 municípios da região perdem metade do milho; no El Niño mais forte que já tínhamos visto, cerca de 5 de cada 10. Agora: guardar semente de feijão-de-corda precoce, procurar maniva para fevereiro, não queimar. Confirmar com o técnico: a semente chega antes de 10 de março?" Rodapé: "Medido no seu município · Acertos contados na sua região · Grau B".

### 6.4 O plano de rotação 2027–2029 de Dona Francisca, por faixas (novo na v3)

O plano junta as peças da S1 (escalonar e guardar), da S2 (tampão e forragem em faixas que giram) e da S3 (leguminosa e perene, sem fogo) num desenho só, na ordem das prioridades da família: forragem > comida > renda. Os cartões S0–S3 continuam como estão, para a comparação. As três faixas ficam fora do baixio; o tamanho de cada uma é decisão da família com o técnico. Tudo cabe no cardápio de Quixadá e dentro da janela do ZARC (6.2).

| Talhão | 2027 | 2028 | 2029 | Por que, com o grau |
|---|---|---|---|---|
| **Faixa 1** | Maniva na janela ZARC da mandioca (Quixadá: 01/02–10/03 a 20%) | Mandioca = **tampão**, colhida conforme a necessidade | Caupi precoce | A maniva pega com P(estabelecimento em 60 dias) ≥ 0,7 de 11/fev a 01/mai, contra 0,36 em 21/jan (C). A mandioca é a mais apta no GAEZ em Quixadá (66,1, insumo baixo) e tem ZARC só na portaria plurianual (Port. 11/2020). Em 1998, a mandioca de Quixadá deu 0,50 do normal, e o milho, 0,00 (A, n = 1). A faixa passa os 3 anos sem gramínea |
| **Faixa 2** | Caupi precoce; a metade fica guardada até ~10/mar | Sorgo forrageiro; em ano bom, milho (caupi → milho) | Maniva na janela ZARC da mandioca | A metade guardada teve água na floração em 7 de 10 municípios num ano como 2016 e em 1 de 10 num como 1998 (balde, C). No ZARC, o caupi do Grupo I tem risco de 20% de 11/mar a 20/abr: a metade guardada cai no começo dessa janela. Caupi → milho solteiro: +24% no ano colhido (+2% a +49%; B·T1); o sorgo fica na metade inferior da faixa. Contra o consórcio de hoje, não medido (0 a +9%; D·T3) |
| **Faixa 3** | Sorgo forrageiro | Maniva na janela ZARC da mandioca | Mandioca = tampão | O sorgo forrageiro tem risco ZARC de 20% nos 3 solos do Grupo I, o único com cultivar indicada, em Quixadá (21/fev a 30/abr) e alimenta as cabras no ano seco. Hospeda a lagarta: é escape hídrico, não quebra de ciclo |
| **Baixio (1 ha)** | Milho + caupi em revezamento tardio (caupi 50–85 dias depois do milho), escalonado | O mesmo, trocando de lugar | O mesmo, trocando de lugar | No sequeiro cabe o revezamento tardio, sem bônus de grão (Melo et al. 2013). O caupi em revezamento tem P 0,75 em Quixadá, contra 0,14 em sucessão (C, limite superior). LER de milho + caupi de 1,37 na África (Mudare et al. 2022; B); em sequeiro, não medido. O milho respeita o ZARC (risco de 30%, de 11/fev a 10/mar, só nos solos que guardam mais água, AD5–AD6): o técnico confirma o solo do baixio |
| **Bordas** | Palma + gliricídia em nível, com a gliricídia longe do grão; sem fogo | Ficam | Ficam | A gliricídia é banco de forragem e proteína: junto ao grão, não tira N do ar e derruba o N do caupi (Martins et al. 2015; C). Aleias em 10–25% de declive (Pinheiro & Nair 2018; C); pelo NASADEM, essa faixa de declive cobre 11,9% de Quixadá. Palma resistente à cochonilha: pergunta obrigatória ao técnico |

**O giro:** de 2028 em diante, sempre há uma faixa de mandioca de um ano no chão (a faixa 1 em 2028, a faixa 3 em 2029 e a faixa 2 em 2030), e uma faixa nova recebe maniva a cada quadra. Nenhuma faixa queima.

**O interruptor de cada ano:**
- **Ano bom** (nenhum alerta aceso: nem o oceano no P1, nem a chuva NASA desde 1/fev): leguminosa antes do milho. Em 2028, a faixa 2 vai de caupi para milho.
- **Ano seco** (alerta aceso: o oceano no P1 ou a chuva NASA desde 1/fev): sorgo forrageiro ou pousio no lugar do milho. A escolha é feita no plantio, com o oceano (P1) e a chuva desde 1/fev. Depois de ~10/mar, só cabe o caupi ou deixar a faixa em pousio com palhada: o sorgo saiu da troca, porque o de 11/mar teve água em 1 de 10 municípios em 2016.
- **O pousio não é perda:** no catálogo, pousio → milho dá +31% contra milho contínuo (C·T2: só a direção vale no sertão). Não se tira o pousio sem medir a água.
- **Em 2027, o alerta já está aceso no P1** (ONI +2,46, além do recorde). O desenho de 2027 já é o de ano seco nas faixas (caupi e sorgo forrageiro), e o milho fica só no baixio, escalonado.

**2027, dito com honestidade:** sem mandioca no chão hoje, o tampão só protege a partir de 2028. Em 2027, a proteção vem do escalonamento (a metade do caupi guardada até ~10/mar e o baixio escalonado) e da forragem (sorgo forrageiro e palma), mais as ações do P1: semente de caupi até dezembro, maniva para fevereiro, palma e nada de queima.

**O que o plano tem de número, e o que não tem:**
- **Não tem "pior ano em 10" próprio.** É uma combinação de S1, S2 e S3, e a S1 e a S3 não têm esse número. A referência mais próxima é a carteira 1/3 da S2 (estado, teto: 0,26 → 0,36), mas a composição do plano é outra.
- **O efeito da rotação vale só no ano colhido.** O milho quebra em cerca de 1 de cada 5 município-anos (21,5% pela definição canônica, 1998–2025; 20,2% no CE pela janela do catálogo, 2000–2024), e nesse ano o bônus é ~0.
- **Não quebra a lagarta na região:** milho ou sorgo existem em 98,3% dos município-anos do CE, e a mariposa voa ~100–250 km. A quebra de ciclo vale na faixa sem gramínea, com o status confirmado pelo técnico (`pesquisa/catalogo_rotacoes_comprovadas.md`, "O que os nossos dados mostraram", 11, e G23).
- **A troca do consórcio de hoje por faixas que trocam de lugar nunca foi medida.** Por isso o plano é também o ensaio que falta: o técnico registra o resultado de cada faixa no fim de cada safra (3.3).
- **Riscos, nesta ordem:** maniva-semente para três plantios (2027, 2028 e 2029); mão de obra para implantar as bordas; mercado e casa de farinha para a mandioca; semente de sorgo forrageiro.

---

## 7. O que é inovador

1. **O calendário de decisão é derivado de três curvas medidas: habilidade, opções e visibilidade.** É a imagem do slide 3.
   - **Habilidade, sempre por era:** em 19/mar, a chuva desde 1/fev dá 0,74 (1998–2015) e 0,71 (2016–2025); a soma desde 1/jan, 0,77 e 0,55; o oceano, conhecido desde novembro, 0,66 e 0,72. Em 30/abr: desde 1/fev 0,82 e 0,76; desde 1/jan 0,83 e 0,66; SMAP 0,77 (2016–2025).
   - **Opções:** o milho cabe em 93% dos municípios em 28/fev, 42% em 19/mar e 0% em 31/mar. O caupi cabe em 98% em 19/mar e 41% em 31/mar. Em 30/abr, nada mais cabe (`arquiteto_final_curvas_quixada.saida.txt`, bloco B).
   - **Visibilidade:** o óptico a 30 m vê 79% em 28/fev, 71% em 31/mar e 92% em 30/abr (n = 24 AOI-anos); a 1 km, 39–40% dos pixels em jan–mar. O radiômetro do SMAP vê a célula mediana em 13–15 dias por mês, o ano todo.
   - **19 de março é o último portão de troca; 30 de abril é onde habilidade e visibilidade são máximas, mas só cabe salvar.** Em ano de mar como o de 2027, a decisão do caupi antecipa para o início de março e se apoia no oceano e na chuva desde fevereiro.
2. **A forma de ler a água da NASA decide (novo).** A mesma chuva IMERG, somada desde 1/jan, carrega o janeiro chuvoso até abril e perdeu 2016. Contada desde 1/fev, acendeu nos 182 municípios em 19/mar/2016, o último dia de troca. A água no solo do SMAP confirmou em metade do estado até 30/abr. A segunda missão separa o vermelho (5,3 em 10 quebram em 19/mar) do amarelo (2,1) e segurou o alarme falso de 2022. O recibo diz que o SMAP L4 usa chuva ajustada ao IMERG, que o L3 (só radiômetro) conta a mesma história e que nenhuma leitura sabe qual município.
3. **Teste de estresse de rotações no registro da NASA, com o IBGE como árbitro.**
   - Cada estratégia é reencenada nas 28 quadras do IMERG. Onde há rendimento observado, a ordem é pelo pior ano; onde não há, o cartão diz "sem número".
   - **Duas secas, dois escudos:** num ano como 2016, a metade guardada da S1 vira caupi no início de março (7 em 10 municípios com água na floração); num ano como 1998, não havia água nem para o caupi (1 em 10), e quem protege é a mandioca plantada no ano anterior (S2; Quixadá, 1998: mandioca 0,50, milho 0,00).
   - O replay de 1998 mostra o oceano avisando em novembro, janeiro enganando, a chuva desde fevereiro acesa em 10/mar em 94% dos municípios, o balde dizendo que nem o caupi teria água e o IBGE revelando o resultado. O replay de 2016 mostra a soma dizendo "tudo bem", a chuva desde fevereiro e depois o solo dizendo "não", o verde do VIIRS testemunhando em junho e o IBGE julgando.
4. **Honestidade como funcionalidade.**
   - Recibo A–D com a marca de evidência transferida (·T).
   - Placar do alerta por município, com erros, **para cada luz** (em Quixadá, o SMAP nunca acertou, e o único vermelho foi falso).
   - **Toda curva por era**: a regra que funcionou em 1998–2015 e falhou em 2016–2025 aparece assim.
   - **Linha de base justa:** o SMAP foi comparado com a melhor leitura da chuva, não com a pior, e perdeu o posto de luz principal por isso.
   - **Regra congelada com hash** antes da quadra de 2027.
   - AUDIT.md com a inflação da validação aleatória (R² 0,49 contra −0,08) e com os resultados nulos: SMAP de novembro, combustível no total do ano, NDVI no portão, IA causal no PAM, a média sazonal de percentis.
   - O sentinela, que sinalizou a deriva do Terra, o relato copiado no PAM, o NDVI deslocado nos dois sensores e o percentil do SMAP que some na seca.
5. **Saber local testado com respeito: o "Checkpoint São José".**
   - A tradição diz que chuva no dia de São José (19/mar) garante o inverno. O teste justo compara com o **resto** da quadra (20/mar–31/mai): a chuva do dia e todo o acumulado até ali dizem o mesmo, e pouco (ρ estadual +0,32 nos dois; n = 28; p ≈ 0,1; `cetico_r3_sao_jose_mandioca.saida.txt`, bloco A).
   - **"A chuva de São José diz tanto quanto toda a chuva até ali, que é pouco."** São José marca a última janela de troca; é nesse dia que o QUADRA lê a luz principal.
6. **Dois relógios da água e um portão de entressafra.**
   - O solo responde em semanas a poucos meses (a anomalia da zona da raiz cai a 1/e em 38–46 dias, agrupando os anos; dentro de uma mesma quadra, em cerca de 2 semanas). A água subterrânea lembra por 8 a 13 meses. O relógio lento roda na memória de chuva do IMERG com o GRACE como par.
   - A entressafra, onde no sertão de fato se decide a rotação, vira um portão **de prática com data fixa** (até 31/ago): palhada em vez de fogo, aceiro, nova faixa de maniva na quadra seguinte e perene em nível.
7. **A pergunta de Kluger, Di Tommaso & Lobell no semiárido (novo).** Kluger et al. (2025) mediram, com satélite e florestas causais, como o benefício da rotação muda com o clima em celeiros temperados. O QUADRA leva a pergunta para onde ela não foi feita (sequeiro tropical, sem mapa oficial de culturas) e acrescenta o que eles não têm: os dados de água da NASA e o **momento** da decisão.
8. **A transferência de evidência medida com a NASA (novo na v3).** A literatura de rotação vem de climas diferentes do sertão. O QUADRA mede, com a assinatura de clima do POWER, quanto o lugar de cada estudo se parece com cada município (peso w), e o GAEZ confere se as mesmas culturas cabem nos dois lugares.
   - **Os celeiros temperados**, onde a rotação foi medida por satélite, têm w = 0,00 para Quixadá. Nenhum ensaio de rotação no tempo do catálogo vem de clima de sertão, e nenhum número de rotação T0/T1 vem de clima parecido (w ≥ 0,3). Os números que valem no sertão vêm do próprio Nordeste.
   - **A ordem dos análogos é robusta** (refeita com a Tmax média, R3.5): o Cerrado piauiense fica entre os 3 mais parecidos com o Sertão Central em 100% de 2.000 sorteios de pesos, e o semiárido da Índia em 98,6%. Tirando qualquer variável, o tau de Kendall fica entre 0,85 e 0,92 (`notebooks/secoes_analogos/01_robustez.py` e `06_motor.py`).
   - **Cada município puxa uma literatura:** o Cerrado piauiense é o melhor análogo em 102 municípios, Sobral em 40, a Savana da Guiné em 13 e Harare em 11. A confiança média vai de 0,73 (Norte) a 0,90 (Centro-Sul); a Região Metropolitana de Fortaleza tem 0,75. O recibo é municipal (`02_mapa_ceara.py`).
   - **Clima parecido traz culturas parecidas** (Spearman −0,76 entre distância de clima e semelhança de aptidão). Os 5 lugares mais parecidos no clima têm perfil de culturas parecido (0,79 a 0,98). Harare, de culturas diferentes (−0,08), deixou de ser análogo (d 2,15). O motor continua exigindo as duas coisas e fica com os +24% do cartão do Nordeste; os +28% ponderados pelo clima são só sensibilidade (`04_aptidao.py`).

**O que isso exige e que é raro numa equipe de hackathon:** o painel de 184 municípios × 28 anos de rendimento observado cruzado com IMERG diário, SMAP L4/L3 diário, POWER, GRACE, GLDAS, MODIS e VIIRS, e os resultados negativos que dizem o que não prometer.

---

## 8. Base científica

### 8.1 Referências (revisão `pesquisa/artigos_e_datasets.md` e `pesquisa/artigo_ancora_objetivo.md`; grau entre colchetes)

| Componente | Referência | Achado que sustenta |
|---|---|---|
| **Artigo-âncora: rotação × clima com satélite e IA causal** | **Kluger, Di Tommaso & Lobell 2025, Environ. Res. Lett. 20:114037, doi 10.1088/1748-9326/ae0f45** (arXiv 2506.02384 v2, out/2025, PDF em `artigos/`) | Mapas de culturas + satélite + florestas causais em 4 celeiros (EUA, Canadá, França, NE da China). Do resumo: (i) os antecessores mais usados estão entre os melhores; (ii) passar de uma rotação simples para uma mais diversa rendeu pouco e às vezes foi negativo; (iii) o efeito do antecessor foi maior em condições mais chuvosas; (v) a leguminosa antecessora rendeu menos sob calor. Não estuda semiárido nem dados de água. [B·T] |
| Benefício da rotação muda com o clima | Zhou et al. 2024, Global Change Biology, doi 10.1111/gcb.17556 | Satélite + floresta causal no Corn Belt: o benefício milho-soja é sensível ao clima e muda com o aquecimento. [B·T] |
| Satélite reproduz o efeito de campo | Beal Cohen, Seifert, Azzari & Lobell 2019, Agron. J., doi 10.2134/agronj2019.03.0157 | O satélite reproduziu o efeito da rotação medido em campo. [B·T] |
| Diversidade estabiliza a produção | Renard & Tilman 2019, Nature, doi 10.1038/s41586-019-1316-y | Em escala nacional, mais diversidade de culturas, produção mais estável. [B] |
| Rotação como política, portões | Dury et al. 2012, Agron. Sustain. Dev. 32:567–580 | O plano de cultivo real é dinâmico e adaptativo. [B] |
| Pesos do agricultor, multicritério | Sadok et al. 2008, Agron. Sustain. Dev. 28:163–174 | Avaliação ex ante com apoio multicritério. [B] |
| Grafo de sucessões, enumeração | Detlefsen & Jensen 2007, Agric. Syst. 94:566 | Rotação como fluxo em rede, otimizável de forma exata. [B] |
| IA de rotação (trabalho mais próximo) | Fenz et al. 2023, Comput. Electron. Agric. 212:108160 (lido só no nível do resumo) | Planejamento de rotação com IA e dados. Nós acrescentamos o tempo da decisão e o risco de cauda. |
| RL acoplado a simulador | Kallenberg et al. 2023, Environ. Data Sci. 2 | RL com modelo de cultura para **adubação nitrogenada**, não rotação. Citado só como exemplo do porquê não usamos RL. |
| Balde FAO-56 | Allen, Pereira, Raes & Smith 1998, FAO-56 | ETc = Kc × ET0; Kc, p e estágios por cultura. [B] |
| ZARC | MAPA/Embrapa (revisão 6.7) | O ISNA e a tábua de risco condicionam crédito e seguro. Nossa janela é sintética [C]. |
| Veranico e perda | Rocha et al. 2021, RBMet 36:579–589 | **Corrigido na v3:** o veranico acompanha a perda, mas acrescenta pouco à chuva total. Refeito no IMERG nos 183 municípios: r com a chuva de −0,91 no estado e −0,67 no município; o resíduo dá AUC 0,593; a correlação parcial com o rendimento, dada a chuva, é negativa em 87% dos municípios (mediana −0,22). Pesa nos anos de chuva normal (quebra de 18,0% com veranico alto, contra 7,5%). A definição do veranico é de Menezes et al. 2008. Milho + feijão = 91% da área das lavouras **temporárias** (PAM 2017). [B, Nordeste] |
| Oceano como probabilidade | Kayano & Andreoli 2006, JGR 111(D13), localizador 2005JD006142 (o "D13101" da v2 não foi confirmado no Crossref); Nobre & Shukla 1996, J. Climate 9:2464 | O ENSO sozinho acerta 36%; o Atlântico condiciona a ZCIT. [B] |
| Previsão empírica de referência | Rocha Júnior et al. 2021, Water 13:1613 | Modelo empírico simples é competitivo no Nordeste. [B] |
| Seca e adaptação | Marengo et al. 2018, An. Acad. Bras. Ciênc. 90:1973; Marengo et al. 2022, Clim. Resil. Sustain. 1:e17 (aceito em 2021) | A seca de 2010–2016; adaptação ainda pós-desastre; a cisterna é de beber. [B] |
| Previsão e confiança no Ceará (novo) | Finan & Nelson 2001, Clim. Res. 19:97, doi 10.3354/cr019097; Lemos et al. 2002 (fora da revisão) | Em 1997, a previsão "abaixo da média" foi lida como seca, e a FUNCEME perdeu credibilidade (p. 105). Em 1998, a FUNCEME passou a informar sem dizer quando plantar e treinou a Ematerce (p. 107). A âncora escrita de São José está na nota 1, p. 98. [B] |
| Leguminosa antecessora | Zhao et al. 2022, Nat. Commun. 13:4926; Franke et al. 2018, AGEE 261:172; Mudare et al. 2025, Nat. Commun. 16:9552, doi 10.1038/s41467-025-64567-9 | **Corrigido na v3:** Zhao, +20% como média global (T2: só a direção); o "+32% em baixa produtividade" está só no resumo, sem intervalo. Franke, +24% no Sahel e na Guiné: a aridez não reduz o efeito relativo. Mudare, caupi → milho contra milho contínuo, +14,7%; pousio → milho, +31%. [B·T] |
| **Cartão do Nordeste (novo)** | Catálogo de rotações do conselho, cartão `ne_lg_cereal_sequeiro_quente` (`pesquisa/catalogo_rotacoes_comprovadas.md`) | Leguminosa de grão → cereal solteiro, sequeiro quente, N ≈ 0: +24% no ano colhido (+2% a +49%). Central e limite alto são síntese do conselho, não número de artigo. [B·T1] |
| **S0 → rotação no tempo (novo)** | Catálogo, cartão `ne_s0_para_rotacao_tempo` | Não medido em nenhum artigo do catálogo: central 0, sensibilidade 0 a +9%. [D·T3] |
| Resiliência pela diversidade | Bowles et al. 2020, One Earth 2:284; Renwick et al. 2021, ERL 16:084067; Beillouin et al. 2021, GCB 27:4697 | **Corrigido na v3:** Bowles, rendimento 14,0% a 88,9% **maior** no ano de seca, em 9 sítios dos EUA (corpo do artigo; o resumo fala em perdas 14,0% a 89,9% menores). Renwick, 1 sítio em Ontário: a perda pela seca caiu de 53% para 36%, ou 17,1 pontos percentuais (cerca de um terço a menos), ligada à matéria orgânica. Efeitos variáveis; não transferem (T3). [B·T] |
| Consórcio e forragem | Himmelstein et al. 2016; Mudare et al. 2022 [B]; Souza et al. 2011, Bragantia 70:715 [C, ensaio único]; Diniz et al. 2017, PAB 52:724 [C, ensaio irrigado único] | Consórcio +23% na África; LER milho + caupi de 1,37 (Mudare 2022). **Corrigido na v3:** o ensaio de Petrolina (Souza 2011) foi irrigado (a lâmina mínima recebeu 100% da ETo por gotejo até 40 DAS): o LER em sequeiro não foi medido. Palma + sorgo: o 6.279 é o IPS; em matéria seca, 12.130 kg/ha, sem diferença do sorgo solteiro. |
| Cobertura: custo | Abdalla et al. 2019, GCB 25:2530 | Cerca de −4% na cultura principal e custo de água. [B·T] |
| **Cobertura no Nordeste (novo)** | Melo et al. 2013, Ciênc. Rural 43:1535 [B]; da Luz et al. 2023 e Souza et al. 2024 [C, irrigados] | Melo (Alagoinha-PB, 2000–2008): mucuna, guandu e fava intercaladas no milho (sem crotalária nem braquiária); o +22% a +49% do resumo soma o NPK; só a leguminosa não muda o grão com significância; cobertura > 80% antes do plantio. Da Luz e Souza tiveram irrigação; os autores de da Luz dizem que o resultado não representa o sequeiro. |
| **Aleias e gliricídia (novo)** | Martins et al. 2015, PAB 50:178 [C]; Pinheiro & Nair 2018, Forest Syst. 27:eR01S [C] | Martins (Taperoá-PB): N no grão do caupi de 18,04 para 1,58 kg/ha entre fileiras de gliricídia (Tab. 2); a gliricídia tira ~52% do N do ar com buffel ou palma e 0% junto ao milho + caupi (%Ndfa, Tab. 1). Pinheiro & Nair: aleias em 10–25% de declive. |
| Fogo, pousio e carbono | Primo et al. 2023, J. Environ. Manage. 336:117594 [**D**, simulação Century, local não verificado]; Sacramento et al. 2013, Rev. Bras. Ciênc. Solo 37:784 [C, medição em Sobral]; Cano-Crespo et al. 2015 [B] | Primo: −50% de C em 10 anos sem pousio (cenário). Sacramento: a agrofloresta **perde menos** carbono que a broca com queima (−8,13 e −23,87 contra −58,87 Mg/ha), sem ter mais carbono. Cano-Crespo: fuga do fogo para vizinhos. **Corrigido na v3:** Salcedo et al. 1997 trata de nutrientes depois da queima e não sustenta nenhuma das duas frases; saiu desta linha. |
| Área queimada a 30 m | Franca Rocha et al. 2024, Fire 7:437 | 12,7% da Caatinga queimou em 1985–2023, pelo Landsat. O nome "MapBiomas Fogo" não está no resumo (a conferir no texto completo). [A, regional] |
| Fogo e ar seco | Argibay et al. 2020, Ecol. Indic. 113:106151; Bezerra et al. **2026** (on-line em 29/12/2025), Atmosphere 17:46 | **Corrigido na v3:** Argibay viu "ano úmido seguido de ano seco" com muita queima num ecótono do PI; no CE, isso não se repete (6 anos de 25; −0,16 no log da área; p unilateral 0,66). Bezerra não trata disso: mostra o ar seco (VPD) acompanhando o fogo no mesmo mês, efeito que se replica no CE (r +0,59). [B] |
| Quebra de ciclo de praga | Ratnadass et al. 2011; du Plessis et al. 2020, Insects 11:228; Azambuja & Degrande 2014 | Ruptura temporal de hospedeiro; graus-dia da lagarta (Tb 12,57 °C; K 390,8 GD); vazio sanitário do algodão. [B] |
| Satélite térmico | Anderson et al. 2016, RSE 174:82; Fisher et al. 2020, WRR 56 | ESI e ECOSTRESS: base do item de roteiro. **Corrigido na v3:** Rossato et al. 2017 saiu de "solo raso". Eles concluem que a chuva correlaciona mais que a água no solo, porque a raiz tem 40 cm; com GLDAS e IMERG, a água no solo de 0–40 cm prevê melhor que a chuva (feijão 0,44 contra 0,28; milho 0,55 contra 0,44), e 0–40 ≈ 0–100 cm. |
| SMAP L4 | Reichle et al. 2019, JAMES 11:3106; produto SPL4SMGP v8 (Reichle et al. 2025, doi 10.5067/T5RUATAQREF8) | Erro sem viés de 0,026 m³/m³ na zona da raiz (avaliação da v4). |
| SMAP L4: forçante de chuva | Reichle et al., EGU23-1419 (resumo de congresso; https://meetingorganizer.copernicus.org/EGU23/EGU23-1419.html) | Desde a v6 do L4_SM, fora da América do Norte, a chuva da forçante é corrigida para os totais diários do IMERG. Usado só para descrever a dependência no recibo; a v008 não foi conferida. [D como fonte] |
| SMAP L3 | O'Neill et al. 2023, SPL3SMP_E v6, doi 10.5067/M20OXIZHY3RJ | Observação do radiômetro em banda L a 9 km. |
| GRACE e reservatórios | Gonçalves et al. 2020, STOTEN 705:135845 [B]; Lima et al. 2020, Bol. Ciênc. Geod. 26(3):e2020013 [C]; Melati et al. 2019 | **Corrigido na v3:** Lima et al. dão ρ de Spearman 0,78 entre o GRACE e o volume médio anual dos reservatórios, com médias anuais (n ≈ 15–16), na região hidrográfica Atlântico Nordeste Oriental (PI a AL). Gonçalves et al. tratam da perda de água no aquífero Urucuia (oeste da BA) sem queda de chuva. |
| POWER e IMERG no mundo | Van Wart et al. 2015, AFM 209–210:49; White et al. 2008, AFM 148:1574; Rozante et al. 2018, Remote Sens. 10:882 | Clima de satélite alimenta modelos de cultura; viés da Tmax do POWER; o IMERG subestima o litoral do Nordeste. **Medido por nós (v3):** no litoral leste, o IMERG capta 39–72% da chuva de 17 automáticas do INMET a menos de 20 km do mar (`v3_curador_valida_inmet.saida.txt`, B2). |
| HLS | Claverie et al. 2018, RSE 219:145 | Landsat e Sentinel-2 harmonizados a 30 m. |
| Fenologia | Arvor et al. 2011, IJRS 32:7847 | Séries de EVI/NDVI detectam ciclos no Brasil. |
| **Aptidão das culturas (novo)** | Fischer et al. 2021, *GAEZ v4 Model documentation*, doi 10.4060/cb4744en; Zabel et al. 2014, PLOS ONE, doi 10.1371/journal.pone.0107522 | O que cabe no lugar, por clima, solo e relevo, em sequeiro ou irrigado, com insumo baixo ou alto; clima de 1981–2010, pixel de ~9 km. Não vê o ano. Classes da camada oficial da v4 (Fischer et al. 2021, fig. 7-3): > 85 muito alta; > 70 alta; > 55 boa; > 40 média; > 25 moderada; > 10 marginal; > 0 muito marginal. Corte "apta" do QUADRA: > 40. |
| **ZARC oficial (novo)** | MAPA, Tábua de Risco do Ceará 2025/26 e 2026/27 (11 portarias no CE em 2026/27, uma por cultura, de março a agosto de 2026; a 245 vale só para o milho com braquiária) e do Nordeste 2026/27 (240.949 linhas, 1.794 municípios, 17 culturas, 113 portarias); Campos et al. 2010, doi 10.1590/s1415-43662010000400008 | Risco de 20%, 30% ou 40% por município, cultura, solo, ciclo e decêndio. Critério: água suficiente na fase crítica em pelo menos 80% dos anos. No CE, o QUADRA usa só os grupos de ciclo com cultivar indicada na portaria (caupi e sorgo forrageiro no Grupo I; mamona nos Grupos II–IV). |
| **Garantia-Safra (novo)** | Lei 10.420/2002, com as redações das Leis 12.766/2012 e 15.236/2025 (página do Planalto, lida pela ferramenta web em 14/11) | Perda ≥ 40% (art. 8º); área plantada máxima de 5 ha (art. 10, IV); renda de até 1,5 salário mínimo (art. 10, III); até 4 módulos fiscais (art. 10, V). |

**Os números do artigo-âncora** (ganho mediano de ~4,5% de uma rotação de 2 culturas; ganho ~3,7 vezes maior que o de diversificar ainda mais) **constam no texto do arXiv v2 em disco**, mas não foram conferidos na versão publicada da ERL. Ficam fora dos slides até essa conferência. Na rodada 3, o catálogo conferiu os dois no texto em disco (4,5% na p. 33; 3,67× na p. 13); a Tab. S9 recalculada dá mediana de 4,25% e média de 4,52%. A versão publicada continua sem conferência. No slide entram só os achados qualitativos do resumo.

**Saem:** Silva et al. 2009 (algodão agroecológico) é resumo de congresso [D]. Por isso a S4 opcional de algodão sai da proposta e fica nas ideias futuras.

**Fora da revisão** (DOI conferido no Crossref ou no arXiv por um agente na rodada 1; reconferir antes do slide):
- Rockafellar & Uryasev 2000, Journal of Risk 2(3), doi 10.21314/JOR.2000.038: CVaR.
- Barber et al. 2021, Ann. Statist. 49:486, doi 10.1214/20-AOS1965: base dos intervalos conformais.
- Roberts et al. 2017, Ecography 40:913, doi 10.1111/ecog.02881: validação cruzada em blocos.
- Lemos et al. 2002, Climatic Change 55:479, doi 10.1023/A:1020785826029: previsão sazonal no Ceará.
- Gigerenzer & Hoffrage 1995, Psychol. Rev. 102:684, doi 10.1037/0033-295X.102.4.684: frequências naturais.
- van Etten et al. 2019, PNAS 116:4194, doi 10.1073/pnas.1813720116: ciência cidadã tricot.
- Szwarcman et al. 2024, arXiv:2412.02732: Prithvi-EO-2.0, só como próximo passo.

### 8.2 A mesma pergunta nos dados do Ceará: o que resiste e o que não resiste

Pergunta do `pesquisa/analise_diversidade_resiliencia.py`: os municípios com mais diversidade de lavouras antes da seca (2004–2011) perderam menos rendimento na seca de 2012–2016? Cinco especialistas refizeram o teste com medidas contrárias fixadas antes de rodar.

| Teste | Resultado | Arquivo |
|---|---|---|
| Original (chuva IMERG, relevo, log da área, efeito fixo de mesorregião, HC3) | **+6,6 p.p.** do 1º ao 3º quartil de diversidade (IC90 +3,1 a +10,1; p 0,002); reproduz exatamente | `v2_agronomo_diversidade_robustez.saida.txt`, V0; `v2_estrategista_diversidade_reproducao.saida.txt` |
| Erro agrupado por microrregião | +6,6 (p 0,0007) | estrategista |
| Outra seca (1998, base 1990–1997) | +10,5 (p 0,025 agrupado) | estrategista |
| Placebo sem seca (2008–11 contra 2004–07) | **+0,0** (p 0,99) | estrategista |
| Controle de água pelo GLDAS Noah | +6,2 (p 0,004) | agrônomo, V4 |
| Controlando a fração milho + feijão | **+2,6** (p 0,32); correlação diversidade × fração −0,75 | estrategista |
| Só a composição (razão de cada cultura nos outros municípios) | +2,0 a +4,0: **30% a 60%** do efeito é mistura de culturas | `v2_economista_diversidade_carteira.saida.txt`, A; `v2_cetico_diversidade_composicao.saida.txt` |
| Sem as séries com algum rendimento repetido (37% das séries) | +4,1 (IC90 −0,4 a +8,5; p 0,13) | agrônomo, V2 |
| **Só culturas de sequeiro, com diversidade de sequeiro** | **+1,4** (IC90 −2,2 a +5,1; p 0,51) | agrônomo, V6 |
| Sequeiro sem séries repetidas | −0,5 (p 0,85) | agrônomo, V6 |
| Cada cultura sozinha | milho +6,6 (p 0,28); feijão +1,2 (p 0,57); mandioca −1,5 (p 0,66) | agrônomo |

**Leitura que vai para o deck (só no slide de honestidade, nunca no slide 1):** o padrão "mais diverso perdeu menos" aparece nas duas grandes secas do Ceará e some em anos normais. Mas é **composição, não diversidade**: é sobretudo menos dependência de milho + feijão, as culturas que mais caíram na seca (0,48 e 0,58 da base), e culturas fora do sequeiro (melão, soja e sorgo tecnificados, ~1,03–1,08). Entre as culturas de sequeiro, o efeito desaparece. Isso é coerente com o achado (ii) do artigo-âncora (diversificar além da rotação simples rende pouco) e com o (iii) (benefício menor com pouca chuva). **Por isso o QUADRA não promete bônus de diversidade.** É associação municipal num episódio, não efeito de rotação no talhão. Grau B.

### 8.3 Como o método do artigo-âncora entra no roteiro

O protótipo municipal mostrou por que a escala tem de ser o talhão: no PAM, o efeito do feijão anterior e o do feijão futuro (placebo) têm o mesmo tamanho (`v2_pesquisador_ia_precrop_dml.saida.txt`). O desenho do próximo passo, à maneira de Kluger:
1. **Unidade:** pixel ou talhão de 30 m, não o município.
2. **Tratamento:** a sequência em t−1 (roçado após pousio, roçado repetido, após leguminosa), tirada do MapBiomas anual (classes a conferir: o roçado do semiárido tende a cair em "mosaico de usos") ou de uma classificação HLS calibrada nas proporções do PAM.
3. **Desfecho:** pico de NDVI ou EVI (HLS/Landsat/VIIRS) calibrado contra o rendimento do PAM por município, como Kluger fez com condados.
4. **Modificadores:** o estado da água nos portões (chuva IMERG desde 1/fev, SMAP L4), ET0 do POWER, relevo do SRTM e ONI. É aqui que entra o que o artigo não tem.
5. **Validação:** floresta causal honesta com cross-fitting por bloco de anos, teste de calibração, placebo do antecessor futuro e IC por ano.
6. **Novo, o ensaio de campo que falta:** faixas que trocam de lugar a cada ano (milho | caupi, com o tampão de mandioca), contra o consórcio de hoje, em sequeiro, por pelo menos 3 anos e num município do sertão. É o contraste que nenhum artigo do catálogo mediu (`pesquisa/catalogo_rotacoes_comprovadas.md`, lacuna 2). O painel municipal do IBGE não resolve: o teto da literatura (+1,4% a +2,6% por +10 pontos percentuais de leguminosa) fica abaixo do efeito mínimo detectável (3,7% no NE; 7,1% no CE).

---

## 9. Validação honesta e limitações

### 9.1 Protocolo, igual para toda a equipe

- **A unidade independente é o ano**, não o município-ano. Os resíduos se correlacionam por centenas de km (`pesquisador_ia_hierarquico.py`).
- **Toda variável de nível anual** (ONI, dipolo, GRACE regional) tem erro-padrão agrupado por ano. Município-anos não são réplicas.
- **Validação:** toda métrica sai de uma destas três: deixando o ano inteiro de fora (LOYO); walk-forward, só com o passado; deixando o episódio de seca de fora, com 2012–2017 como um bloco.
- **Seleção aninhada:** toda escolha de regra, limiar, análogo ou configuração é aninhada. Escolher pelo resultado do teste é proibido. Quando uma escolha foi feita depois de ver o teste (a luz de 2027), isso é dito e o grau cai para B.
- **Toda AUC** é decomposta em entre anos e dentro do ano.
- **Os intervalos** vêm de bootstrap por ano. O recibo mostra o n efetivo.
- **Comparação:** toda comparação de modelos é **pareada**, com as mesmas entradas e as mesmas dobras.
- **Toda estratégia** é avaliada contra o **rendimento observado do PAM**, nunca contra o ISNA do próprio balde.
- **Regras novas da rodada 2:**
  - **Por era:** toda curva e todo alerta aparecem também em 1998–2015 e 2016–2025. A curva agregada sozinha esconde que a regra de chuva falhou na última década.
  - **Leitura menos favorável:** quando duas leituras igualmente razoáveis do mesmo dado divergem (ex.: SMAP no dia × média de 7 dias), o slide usa a menos favorável, e o recibo mostra a outra.
  - **Linha de base justa (banca R2):** a regra da leitura menos favorável vale também para a comparação. Todo ganho é medido contra a **melhor** leitura já declarada do mesmo dado, e o recibo mostra todas lado a lado (as 5 leituras da chuva IMERG).
  - **Nível do ano:** todo número-uau é dito no nível do ano (fração de municípios com luz contra a fração em quebra), com o comparador de mesmo número de alarmes e com "qual município? nenhum sabe" quando a AUC dentro do ano for ≤ 0,65.
  - **Contra a geografia:** toda vantagem "dentro do ano" é comparada com uma linha de base só de geografia (o mapa de risco de base do município). Foi esse teste que rebaixou o ISNA e suspendeu o 0,307 do M2.
  - **Sem AUC agregada de probabilidades LOYO com poucos anos:** com 10 anos, a climatologia LOYO sozinha dá AUC 0,154. Usar escore sem intercepto, a variável crua ou a AUC dentro do ano.
  - **Limiares fixados antes:** o 75% veio da rodada 1, e o 20 do SMAP da seção 05 do notebook (commit `48a3608`, 14/11 às 08:34). O τ = 13 d do API veio da autocorrelação do SMAP, sem olhar a quebra.
  - **Escolha declarada:** a luz de 2027 saiu de um critério escrito antes de rodar o fechamento (maior AUC mínima entre eras e portões), dito junto com o fato de que as AUCs já tinham sido vistas. "Pré-registrado" não é usado.
  - **Diagnóstico sem 2016:** todo ganho da era SMAP é mostrado também sem 2016, que responde por 47% das quebras de milho da década (`v2_pesquisador_ia_smap_escore.saida.txt`).

### 9.2 Números de cabeçalho, os únicos que vão para os slides

| # | Afirmação | Valor | Validação | Fonte | Grau |
|---|---|---|---|---|---|
| 1 | No registro do PAM, milho e feijão quebram juntos | ρ mediano 0,78 (0,67 sem o choque do ano) | Descritivo, 183 municípios | `arquiteto_numeros_canonicos.txt`; `cetico_r3_refutacoes.saida.txt` F | A |
| 2 | A soma da chuva desde 1/jan falhou na última década | 30/abr: AUC 0,83 (1998–2015) → 0,66 (2016–2025); 19/mar: 0,77 → 0,55 | Por era, mesma regra | `v2_arquiteto_arbitragem_smap.saida.txt` E; `v2_arquiteto_r2_fechamento.saida.txt` A | A |
| 3 | A mesma chuva NASA contada desde 1/fev passa nas duas eras | 19/mar: 0,74 e 0,71; 30/abr: 0,82 e 0,76. Maior AUC mínima entre as 5 leituras declaradas (0,709) | Por era; critério declarado antes de rodar, depois de ver as AUCs | fechamento A e B; `v2_cetico_r2b_smap_contra_imerg_justo.saida.txt` F | B |
| 4 | **2016 no nível do ano** | Em 19/mar, a chuva desde 1/jan acendeu em 7 de 182 municípios; desde 1/fev, em 182; 127 (7 em 10) quebraram. Qual município? Nenhuma leitura sabe (AUC dentro de 2016 de 0,61 a 0,65). Com o mesmo número de alarmes, a soma pegaria 55 das 127 | Descritivo por ano; comparador de mesmo número de alarmes | fechamento C | A (descritivo) |
| 5 | **Duas missões da NASA** | 19/mar, 2016–2025: vermelho (chuva desde 1/fev e SMAP) 5,3 em 10 quebram; amarelo 2,1; verde 0,9. Em 2022, a chuva acendeu em 142 municípios, o SMAP em 0 e 3 quebraram. Em 30/abr/2016, o SMAP acendeu em metade do estado | Pareado, 1.820 município-anos, 10 anos | fechamento C | B |
| 6 | As opções fecham | Milho cabe em 93% (28/fev) → 42% (19/mar) → 0% (31/mar) dos municípios; caupi em 98% (19/mar) | Simulação, ±1 decêndio | `arquiteto_final_curvas_quixada.saida.txt` B | C |
| 7 | A validação aleatória infla | R² 0,49 contra −0,08 | Aleatório contra LOYO | `cetico_escala_vazamento.py` | A |
| 8 | **A carteira contra a prática atual** | Pior ano em 10: 0,26 (milho + feijão) → 0,36 com um terço em mandioca (teto). Parte própria da mandioca: +0,02 a +0,08 (placebo do vizinho). Piso de 0,32 sem maniva. Nos anos de luz NASA acesa em 30/abr: 0,13 → 0,21 | Intenção de tratar; placebo pré-declarado; IC por ano | `arquiteto_final_carteira_ic.saida.txt`; `v2_cetico_r2b_gatilho_carteira.saida.txt` 3; fechamento F | A no estado (descritivo); B na parte da mandioca |
| 9 | O mar de 2027: mais chance, não certeza | No El Niño mais forte antes deste, cerca de 5 em 10 municípios com quebra (P(2,04) = 0,54; IC90 0,24–0,75), contra 2 em 10; 1998 e 2016, 7 em 10; 2024, menos de 1 em 10; este ano está além do recorde | Modelo único, ano inteiro fora; contagem | `v2_clima_portao_novembro_2027.saida.txt` A–C | B |
| 10 | Os satélites sabem o ano, não o município | Dentro do ano, nenhuma camada passa de ~0,65 (L3 0,645 em 30/abr; VIIRS 0,62–0,63); a geografia sozinha dá 0,61 | Dentro do ano, contra só geografia | fechamento H; `v2_hidrologo_smap_portoes_quebra.saida.txt` | A |
| 11 | O óptico fica parcialmente cego; o micro-ondas, não | NDVI VIIRS bom em 39–40% dos pixels em jan–mar (95–96% em ago–out); o radiômetro do SMAP vê a célula mediana em 13–15 dias por mês | Descritivo | `v2_sr_fundacao_viirs_portoes.saida.txt` A; `v2_sr_fundacao_smap_l3_l4.saida.txt` A | A |

**Proibido no deck:** qualquer número que use outra definição de quebra, outra regra de alerta, outro limiar do SMAP, a leitura mais favorável quando há duas, uma linha de base pior que a melhor declarada, ou comparação não pareada. **Saíram dos slides na rodada 2:** o "ρ 0,155 → 0,307" do M2, o "+6,6 p.p." como bônus de diversidade, o "+0,072" do fogo, a frase "em 19/mar o que decide é a água no solo" e, depois da banca R2, o "9 contra 64 de 127" como contraste SMAP × chuva, o "1% do SMAP", o "0,15 → 0,36" como ganho sobre a prática atual e "the soil does not fool you".

### 9.3 Onde erramos, e mostramos

- **2012:** pego tarde pela regra antiga. Em 19/mar, ela pegou 40% das quebras; em 30/abr, 91% (123 de 135). A chuva desde 1/fev **perdeu 2012 em 19/mar** (luz em 19% dos municípios, com 75% em quebra) e pegou em 30/abr (68%).
- **2015:** a chuva desde 1/fev também perdeu 2015 em 19/mar (17% com luz, 61% em quebra).
- **2016, o análogo de 2027:** a soma desde janeiro perdeu. A chuva desde fevereiro acendeu em 182 de 182 em 19/mar; o SMAP, em 56 em 19/mar e em 91 em 30/abr. Qual município? Ninguém sabe dentro do ano. Mesmo assim, em 19/mar/2016, o caupi semeado em 21/mar teve água na floração em só 3 de 10 municípios (balde): a troca útil era no início de março.
- **1998:** nem o caupi de 11/mar teria tido água (1 em 10 municípios, balde, grau C). A troca do início de março não salva um ano como 1998.
- **2021 e 2022, os alarmes falsos:** em 2021 (7 quebras), a chuva desde 1/fev acendeu em 76 municípios em 19/mar e 97 em 30/abr; o SMAP, em 26 e 81. Em 2022 (3 quebras), a chuva acendeu em 142 em 19/mar, e o SMAP em nenhum.
- **2025:** a soma pegou 1 de 45 em 30/abr; a chuva desde 1/fev, 34 (em 100 alertas); o SMAP, 21 (em 46 alertas, contra 11,4 ao acaso).
- **2024:** El Niño forte sem quebra estadual (8%), com o Atlântico recorde de quente. Em Quixadá, o milho quebrou (0,46) com chuva normal, solo úmido, verde normal e nenhum vizinho em quebra.
- **Quixadá 2023–2025:** 2025 foi água no fim da quadra (a chuva desde 1/fev pegou por um fio: 0,747); 2023, provavelmente chuva que parou em maio (com vizinhos em quebra); 2024 não tem assinatura NASA (seção 6.2). No AUDIT.md, como "o satélite discorda do árbitro".
- **Quixadá, SMAP:** nenhum acerto em 2016–2025 com o limiar canônico, e o único vermelho da década foi falso (2021).
- **No nível do ano, em São José, na última década:** nenhuma leitura ordena bem os anos (chuva desde 1/fev ρ +0,19; SMAP +0,32; soma desde 1/jan −0,30; n = 10).
- **O balde:** superestima 2010 e 2013; o ISNA de cultura não vê 1998 nem 2001 (o estado em percentil vê 1998, grau C).
- **Alarmes falsos:**
  - em 30/abr (2016–2025), 62% dos alertas da chuva desde 1/fev caem em municípios sem quebra; no vermelho, 59%;
  - em 28/fev, 68% (regra antiga), e por isso fevereiro não tem alarme;
  - o "60% das famílias sem alerta em 3 anos" (`designer_confianca_alertas.txt`) foi medido com a regra antiga e precisa ser refeito.
- **Anos de excesso** (2009, 2024): o balde não modela encharcamento.
- **2026, discordância aberta:** o SMAP marcou p39 em 19/mar e p35 em 30/abr, com a chuva desde 1/jan a 110% e 105% do normal. Só o PAM de 2026 (que sai em 2027) arbitra; o VIIRS de mar–mai indica safra perto do normal (mediana 1,031 do normal; `v2_estrategista_viirs_quixada.saida.txt`).
- **Gatilho tipo Garantia-Safra (AUDIT.md):** com o IMERG em fev–mai, o risco de base no município fica perto de 50% nos dois sentidos (`v2_economista_gatilho_smap.saida.txt`). A comparação com o SMAP usou outra escala (média de percentis) e será refeita antes de qualquer frase. **Novo na v3:** a regra da lei é perda ≥ 40% (art. 8º da Lei 10.420/2002, redação da Lei 15.236/2025), então o rótulo da auditoria passa a razão < 0,6. Com ele, dá 26,0% dos município-anos em 1998–2025 (5.144) e 29,8% em 2016–2025 (`pesquisa/viabilidade_artigos_nordeste.md`, "Verificação adversária").

### 9.4 Grau de evidência por tipo de afirmação

| Grau | O que é | Exemplos |
|---|---|---|
| A | Validado com dado local observado, por ano | Correlação entre culturas no PAM, curva de habilidade por era, regra de chuva, carteira estadual e seu piso, continuidade VIIRS × MODIS |
| B | Meta-análise ou síntese multi-sítio; poucos anos ou poucos episódios com dado local | Luz principal de 2027 (escolhida depois de ver 2016–2025), duas missões (10 quadras, 1 grande seca), parte própria da mandioca na carteira, P1 do oceano, El Niño × quebra (contagem), associação diversidade × resiliência |
| B·T | B transferido de outro clima (meio grau abaixo) | Leguminosa antecessora (cartão do Nordeste, +24% no ano colhido, B·T1), rotação diversa, achados de Kluger et al. 2025, custo da cobertura |
| C | Modelo, simulação, ensaio único, ordem validada sem nível | Datas-limite sintéticas, contrafactual do caupi guardado (1998, 2016, 2024), janela da maniva, balde em percentil em 1998, ponte verde, palma + sorgo (IPS), carbono medido em Sobral (Sacramento 2013), gliricídia longe do grão (Martins 2015), açude numa AOI |
| D | Suposição, resumo de congresso ou simulação usada como cenário | Volume de cisterna suposto (52 m³ e 16 m³), preço de forragem, forçante do SMAP L4 v008 (só por resumo do EGU), carbono de Primo 2023 (simulação Century; rebaixado de C na v3), troca do consórcio S0 por rotação no tempo (não medida; 0 a +9%) |

### 9.5 Limitações

1. **Nenhum efeito de rotação foi observado no Ceará.** O PAM valida o efeito do clima sobre cada cultura, não o do antecessor. O protótipo de IA causal confirma: o placebo do antecessor futuro dá o mesmo efeito. **Novo:** nenhum ensaio de rotação no tempo do catálogo vem de clima de sertão, e a troca do consórcio milho + feijão por rotação no tempo nunca foi medida (D·T3). O número de rotação do motor (+24%) é transferido (B·T1) e vale só no ano colhido, contra cereal solteiro.
2. **A habilidade é regional.** Tudo foi calibrado no município (o PAM é estimado pelo IBGE e pela Ematerce), e a decisão é do roçado de 1–5 ha. Dentro do ano, a AUC fica em ~0,65 ou menos para todas as camadas, perto da geografia (0,61). No nível do ano, em São José, na última década, nenhuma leitura ordena bem os anos (n = 10).
3. **2027 está fora da distribuição** (ONI ASO 2,46 contra o máximo de 2,04). Toda probabilidade é extrapolação, com 3 a 7 análogos.
4. **Poucos episódios.** A era SMAP tem 10 quadras, e 2016 responde por 47% das quebras de milho da década (2016 + 2025 = 64%). Sem 2016, o SMAP em 19/mar fica abaixo do acaso. A cauda da carteira vem de cinco a sete anos ruins desde 1998. Todo IC é largo.
5. **O SMAP L4 não é independente do IMERG.** É um modelo forçado por chuva corrigida para o IMERG (segundo a equipe do L4_SM; v008 não conferida) e corrigido pelo radiômetro. Contra a melhor leitura declarada da chuva, o ganho próprio dele é ~0 em 30/abr. As 5 leituras da chuva estão lado a lado no AUDIT.md (desde 1/jan 0,66; desde 1/fev 0,76; últimos 30 dias 0,75; API 0,80; últimos 15 dias 0,80; SMAP 0,77; L3 0,77). Dizemos "duas missões veem o estado da água", nunca "dois satélites independentes concordam".
6. **A climatologia do percentil do SMAP não foi conferida** (só 13,2% dos município-dias abaixo de p20). Os valores de 2016 vêm do reprocessamento v008 de hoje, não do que existia em 2016: o slide diz "would have flagged with today's product".
7. **"Dados de água da NASA" não são uma verdade única no município:** GLDAS Noah e IMERG mal concordam sobre onde a seca de 2012–16 foi pior (ρ +0,09; `v2_agronomo_diversidade_robustez.saida.txt`); os níveis de umidade diferem até 0,10 m³/m³ entre produtos.
8. **A área plantada se adapta** ao ano: ρ com o ONI de NDJ de −0,43 no milho (`cetico_r2_checagens.py`, bloco C).
9. **Qualidade do PAM por cultura.** A mandioca tem relato repetido e ciclo longo; o feijão mistura Phaseolus e caupi; o sorgo é tecnificado e tem n pequeno.
10. **Escala da água azul.** A família típica de sequeiro não tem água para salvar o roçado.
11. **Sem custo de produção.** A renda é normalizada e bruta.
12. **Regras institucionais, em parte conferidas (atualizado na v3):** o Garantia-Safra foi conferido na lei pela ferramenta web (perda ≥ 40%; área plantada máxima de 5 ha; renda de até 1,5 salário mínimo; até 4 módulos fiscais), e a janela do ZARC oficial de Quixadá está em disco (Tábua de Risco 2026/27). Continuam sem conferência a cesta de culturas e o que acontece com quem planta fora do ZARC (em Quixadá, nada zoneado antes de 21/jan, e 20% só a partir de 11/fev). Sem conferência, não entram em slide.
13. **Muitos testes sobre os mesmos anos.** A rodada 2 somou dezenas de comparações às da rodada 1. Só os números da tabela 9.2 vão ao pitch; o resto (TSA do Atlântico, dipolo × início, combustível × fogo, "ONI além da chuva", regra de 15 dias de chuva) é exploratório.
14. **A transferência por clima tem limites (novo).** A assinatura do POWER não tem variável de inverno. Com a Tmax média (R3.5), o norte da China saiu dos parecidos (os 20 mais parecidos ficam entre 30°S e 24°N), mas em clima temperado a "Tmax da estação úmida" pode cair no inverno (Kansas: 8,5 °C). A grade global é de 6°, e o GAEZ é clima médio de 1981–2010 com pixel de ~9 km, que mistura serra, baixio e tabuleiro. O peso w diz quão parecido é o clima, não se o ensaio vale; por isso o grau e a transferência continuam separados. Os números dos análogos mudaram com a correção da Tmax (de recorde do mês para média das diárias): Harare saiu do 4º para o 10º lugar.
15. **A ET0 do POWER não tem um fator único de correção (novo).** Contra as estações automáticas do INMET, ela sai 1,27 vez maior; contra as normais, quase igual (0,97–1,01). A sensibilidade completa do M1 com ET0 × 0,79 ainda falta.
16. **O Nordeste tem três regimes de chuva (novo, 14/11 à tarde).** Pelos 4 meses mais chuvosos do IMERG, a quadra do norte (jan–abr ou fev–mai) cobre 1.056 municípios; o litoral leste (mar–jun ou abr–jul), 312; o Cerrado e o sul da BA (out–jan, nov–fev ou dez–mar), 426 (`regime_chuva_ne_mun.csv`). Os portões de 19/mar e 30/abr e as datas do plano foram calibrados na quadra do CE. No litoral leste, o IMERG capta só 39–72% da chuva medida, e ali as datas vêm do ZARC.
17. **O IMERG Final V07 termina em 30/09/2025 (novo).** Depois disso, o diário via POWER (até 14/09/2026) e a chuva recente são Late ou Early, preliminares. A revisão A15 achou a chuva recente (Late e Early) comparada com uma normal feita de outro produto; o protótipo passou a mostrá-la em percentil e com o rótulo "preliminar".

### 9.6 O que ainda dá para fazer antes do júri

- **Conversa com um técnico de ATER ou um agricultor** (José, até sáb 18h). É a ação de maior retorno para o Impacto: 1 frase com permissão e 1 mudança feita por causa dela.
- **Feito no fechamento:** SMAP L3 consolidado (sem mudança: 0,774 em 30/abr); AUC por era nos 5 portões; congelamento interno da regra de 2027 (sha256 no bloco B); contrafactual do caupi em 1998.
- **Documento do SMAP L4 v008:** conferir a base da climatologia do percentil e a forçante de chuva da versão 8.
- **Kluger et al. 2025:** conferir na versão publicada da ERL os números do arXiv (4,5% e 3,7×) antes de qualquer slide numérico.
- **Hash público** da regra de 2027 e da leitura VIIRS da safra de 2026: **só com o OK explícito do José** (voz pública).
- Refazer `designer_confianca_alertas` com a luz nova.
- Refazer o gatilho tipo Garantia-Safra com a mesma escala para o IMERG e o SMAP (AUDIT.md; não vai a slide), já com o rótulo da lei (razão < 0,6).
- **Novo na v3:**
  - conferir na portaria do ZARC as duas datas de Quixadá (zoneado a 40% desde 21/jan; 20% desde 11/fev) e o que o Proagro e o Garantia-Safra dizem de quem planta fora do ZARC;
  - rodar o M1 com ET0 × 0,79, incluindo o milho (sensibilidade);
  - copiar para `artigos/` os PDFs de da Luz 2023 e Souza 2024, que só existem no scratchpad do agrônomo, apagado em ~1,5 dia (caminhos em `pesquisa/viabilidade_artigos_nordeste.md`, 4.4, item 12);
  - conferir no texto completo de Franca Rocha et al. 2024 o nome "MapBiomas Fogo".
- **A LSPA não foi cortada por custo (corrigido na v3):** já está baixada para as 9 UFs, sem custo. No milho do CE, o IMERG de 30/abr ordena os anos melhor que a LSPA de abril (ρ 0,82 contra 0,23; n = 19). Fica no AUDIT.md como linha de base oficial; não vai à tela do MVP.
- Cortados por custo ou dependência: seleção aninhada do M2, FIRMS NRT (exige chave), código de barras contra o CDL do Texas, SMAP ao vivo.

### 9.7 Folha de números canônicos e erratas (obrigatória antes do deck)

**Números canônicos:**

| Item | Valor canônico | Não usar |
|---|---|---|
| ONI | ASO/2026 = +2,46; recorde para ago–out (antes 2,04, em 1997); recorde absoluto 2,59 (NDJ 2015) | "o El Niño mais forte da história"; "2,14"; "2,31" |
| Risco de 2027 (P1) | No El Niño mais forte antes deste, ~5 em 10 municípios com quebra (P(2,04) = 0,54; IC90 0,24–0,75), contra 2 em 10; em 2,46, 0,62 só com selo de extrapolação; análogos 1998 0,75, 2016 0,70, 2024 0,08; "este ano está além do recorde" | "with this ocean, about 5 in 10"; "62% de chance" sem o selo; uma média sem os três anos |
| Oceano por era | AUC do ONI ASO: 0,66 (1998–2015), 0,72 (2016–2025), 0,67 (28 quadras) | o 0,67 ao lado de números de uma era só |
| Análogos | 4 de 7 desde 1966 (proxy em 1966); 3 de 5 pelo POWER desde 1982; 2 de 3 catástrofes na era IMERG | "de cada 10 anos como este" |
| GRACE e banco lento | GRACE CE jul–set/2026 no p57; GRACE × açudes do Landsat ρ +0,57 (+0,73 em diferenças); memória de chuva = 55% da variância do GWS no ano fora | "caiu para p35"; o r 0,88/0,95 do CLSM × GRACE como validação; "70% da variância"; "a parte do GRACE não acompanha os açudes" |
| SMAP hoje | Painel: Quixadá 0,087 m³/m³ e o CE em 5º novembro mais seco de 12. Se o estado aparecer: 0,121 m³/m³ (média das 1.837 células), copiado da folha | 0,116 (média das médias municipais); qualquer percentil do produto entre ~12/ago e ~12/jan |
| **Luz principal de 2027** | Chuva IMERG de 1/fev até o portão < 75% do normal (mediana das outras quadras), em 19/mar e 30/abr; sha256 interno `41b7c820…fdb41` | "pre-registered"; "duas luzes" (W1 OU SMAP) como regra de 2027; soma desde 1/jan como luz de 2027 |
| **Segunda missão** | SMAP L4 percentil da zona da raiz < 20, média dos 7 dias até o portão; confirma (vermelho) ou não (amarelo) | limiar 25; leitura do dia como número principal; média sazonal de percentis; "mais seco que 8 de cada 10 anos"; SMAP acendendo o vermelho sozinho |
| Curvas por era | 19/mar: desde 1/jan 0,77 / 0,55; desde 1/fev 0,74 / 0,71; SMAP 0,68 (dia 0,59). 30/abr: 0,83 / 0,66; 0,82 / 0,76; SMAP 0,77 | a curva agregada sozinha; 0,80 (28 quadras) ao lado de 0,77 (10 quadras) |
| **2016 no nível do ano** | 19/mar: desde 1/jan 7 de 182; desde 1/fev 182 de 182; quebra 127 de 182 (7 em 10). 30/abr: desde 1/jan 14 (normal em 92%); desde 1/fev 164; SMAP 91 (metade). Dentro de 2016: AUC 0,53–0,65. Mesmo número de alarmes: a soma pegaria 55 de 127 em 19/mar | "NASA SMAP flagged 64" como contraste com a chuva; mapa municipal ficando vermelho como prova de acerto; 2016 sem 2021 ou 2022 |
| Alarmes falsos | 2022: chuva desde 1/fev em 142 municípios, SMAP em 0, 3 quebras (19/mar). 2021: 76 e 26 em 19/mar; 97 e 81 em 30/abr; 7 quebras | 2016 sozinho |
| Duas missões | 19/mar (2016–2025): vermelho 5,3 em 10; amarelo 2,1; verde 0,9 (taxa-base 1,5). 30/abr: 4,1; 3,4; 0,8 | — |
| Quixadá | Chuva desde 1/fev: 19/mar 9 alertas e 3 acertos; 30/abr 9 e 5 (2025 a 0,747). Regra antiga: 8/2 e 7/3. SMAP: 0 acerto; único vermelho falso (2021). S0: 6 de 28 anos abaixo da metade; pior ano em 10 0,16; mediana 1,05 | "Quixadá acerta"; carteira de Quixadá (não calculável) |
| SMAP em 19/mar sozinho | 0,59 (dia) a 0,68 (7 dias); sem 2016, abaixo de 0,5 | "o solo decide em São José" |
| SMAP L3 | Consolidado: 30/abr 0,774 (n 1.740); 19/mar 0,637; 30/abr/2016 abaixo de 75% do normal em 173 de 174 municípios | "independente do IMERG" para o L4 |
| Memória do solo | Anomalia da zona da raiz cai a 1/e em 38–46 dias, agrupando os anos; ~2 semanas dentro de uma quadra | "o solo esquece em 13 dias" sem a definição |
| Visibilidade | Óptico VIIRS: 39–40% de pixels bons em jan–mar. Radiômetro SMAP: pegada de ~40 km, grade de 9 km, célula mediana vista em 13–15 dias por mês | "every 9 km cell 13–15 days"; "optical goes blind" |
| Dentro do ano | Nenhuma camada passa de ~0,65 (L3 0,645; VIIRS 0,62–0,63); geografia 0,61 | "≤ 0.60 for every layer" |
| ET0 do CE | 1.970 (ERA5) a 2.280 (POWER) mm/ano; 2,5 a 2,8 vezes a chuva da mesma fonte; supera a chuva em 10 de 12 meses nas duas. **v3:** a ET0 do POWER é 1,27 vez a das 16 automáticas do INMET no CE, mas 0,97 (Fortaleza) e 1,01 (Sobral) vez a ETP normal; Tmax do POWER com viés de +0,14 °C contra o INMET; o fator 0,79 é só sensibilidade | um valor único chamado de "correto"; "viés quente da Tmax do POWER" como causa dos 15%; "o ERA5 é que é frio"; 0,79 como correção fixa |
| Ureia/milho | 1,85 em out/2026; pico de 4,00 em abr/2026; média de 2000–2020 = 1,51 (`cetico_r2_ureia.py`) | "4,0 agora" |
| Quebra | Produção ÷ área plantada < 50% da mediana do município nos outros anos; milho 21,5% e feijão 14,6% (1998–2025). No catálogo de rotações (outra janela e outra mediana): milho CE 20,2% e NE 21,0% (2000–2024, mediana da mesma janela) | mediana móvel; área colhida; limiar de 60%; o 18,8% antigo do catálogo (mediana de 1988–2025, com o milho verde de 2025 na mesma mediana) |
| Milho 2012 | −69% no estado; 75% dos municípios em quebra | "71%", "50%" |
| Registro de chuva | IMERG (eras TRMM e GPM), 28 quadras 1998–2025; POWER 1981–2026 é reanálise (MERRA-2 corrigida). **v3.5:** IMERG Final V07 até 30/09/2025; o diário via POWER segue até 14/09/2026 com o Late (preliminar); Late até 12/11 e Early até 13/11/2026 | "28 years of GPM"; "44 quadras observadas"; "IMERG Final até 14/09/2026" |
| **Carteira** | Contra a S0: 0,26 → 0,36 (teto); parte própria da mandioca +0,02 a +0,08 (placebo do vizinho 0,335); piso 0,32; mundo real ~65% do ganho; nos anos de luz NASA acesa em 30/abr, 0,13 → 0,21 (IC90 do ganho +0,04 a +0,10); cauda de 5 a 7 anos ruins | "0,15 → 0,36" como ganho sobre a prática; "raised"; "três episódios"; somar o +6,6 ao CVaR |
| Contrafactual do caupi | Caupi de 11/mar com água na floração (balde): 1998 1 em 10; 2016 7 em 10; 2024 10 em 10. Sorgo de 11/mar: 2016 1 em 10; 1998 0 | "sorgo até 19/mar" na troca; "São José abre a janela em 1998" |
| Diversidade | +6,6 p.p. nas secas (+10,5 em 1998; 0,0 no placebo), sobretudo composição; só sequeiro +1,4 (n.s.). Rótulo: "composição, não diversidade" | no slide 1; "diversificar o sequeiro protege" |
| Fogo | 72,9% dos focos em out–dez e 27% até 30/set (2015–2025); 17% da área do CE em células de ~375 m com ≥ 1 foco (2012–2025); combustível +0,02 sobre a tendência, sem habilidade no total do ano. **v3:** área queimada 12,7% da Caatinga em 1985–2023 (Landsat; Franca Rocha et al. 2024); MCD64A1, 4,9% do CE em 2001–2025 (piso); no CE, os anos "úmido e depois seco" não queimam mais (−0,16; p unilateral 0,66) | "17,4% do Ceará queimou"; "+0,072"; número de focos previstos; "MapBiomas Fogo" antes de conferir o nome; "ano úmido seguido de ano seco gera grandes queimadas" no CE; "Bezerra 2025" |
| VIIRS NDVI | Continuidade do MODIS (r 0,986 no estado); testemunha de fim de safra (AUC ~0,8; abaixo de 90% do normal, 7,5 em 10 quebram); caatinga out/2026 z +1,07, 3º de 15; nov/2026 provisório | "o NDVI decide no portão" |
| Deslocamento do NDVI | +0,03 a +0,05 desde 2020 nos dois sensores com a chuva IMERG; ~0,01 próprio do MODIS; causa aberta | "deriva do Terra" como causa principal |
| Kluger et al. 2025 | "Kluger, Di Tommaso & Lobell (ERL 2025)"; achados qualitativos do resumo | "Stanford showed"; "4,5%" e "3,7×" até conferir na versão publicada |
| São José | "A chuva do dia diz tanto quanto toda a chuva até ali, que é pouco (ρ ≈ +0,3; n = 28)" | "tradition is weak, not wrong" |
| Reprodução | "Recomputado em 4 scripts a partir dos mesmos dados"; o juiz reproduziu do `.nc` cru | "reproduzido de forma independente por 4 scripts" |
| Pontos globais | 40 de 47 pontos terrestres tropicais sem mês de quebra térmica; SMAP L4 cobre 99,6% da terra entre 60°S e 60°N | "86% dos trópicos" |
| **Rotação no sertão (v3)** | Leguminosa de grão → cereal solteiro, sequeiro quente, N ≈ 0: +24% no ano colhido (faixa +2% a +49%), síntese do conselho, B·T1; sorgo na metade inferior da faixa | "+20%" ou "+32%" do Zhao como número do sertão; "+24%" sem "no ano colhido" e "contra cereal solteiro"; "a aridez reduz o efeito" |
| **S0 → rotação no tempo (v3)** | Não medido: central 0, sensibilidade 0 a +9% (D·T3) | qualquer ganho da rotação "contra a sua prática atual" |
| **Comparáveis (v3)** | Pousio → milho +31% e sorgo → milho +28% (C·T2, só direção); caupi → milho contra milho contínuo +14,7% (B·T2); milho-sorgo na sequência: alerta C (n = 10) | "pousio é perda"; "milho-sorgo vetado" |
| **Consórcio milho + caupi (v3)** | LER 1,37 na África (Mudare 2022); em sequeiro, não medido | "LER de 1,15 no sequeiro" (Souza 2011 foi irrigado até 40 DAS) |
| **Transferência (v3.5, Tmax média)** | Celeiros temperados w = 0,00; nenhum número de rotação T0/T1 com w ≥ 0,3 (Franke África Austral +42% com w 0,10); ponderado ~+28% em Quixadá (soma dos pesos 0,46; +29% a +31% entre as mesorregiões), só como sensibilidade; top-3 em 2.000 sorteios: Cerrado piauiense 100%, semiárido da Índia 98,6%; tau de Kendall 0,85–0,92; melhor análogo: Cerrado piauiense 102, Sobral 40, Savana da Guiné 13, Harare 11 municípios; confiança média de 0,73 (Norte) a 0,90 (Centro-Sul), RMF 0,75; GAEZ Spearman −0,76; Harare 10º (d 2,15); 19 de 387 pontos de terra a distância < 1,5 do Sertão Central; w para Quixadá: Bom Jesus-PI 0,95, Harare 0,10 | "+36%" ou "+28%" como central; "o clima parecido garante culturas parecidas"; Harare como análogo do sertão; "RMF é o ponto fraco"; "norte de Minas e China parecidos com o sertão"; "Sobral — Primo 2023"; "Franke: efeito MENOR/MAIOR" |
| **Início da estação (v3.5)** | Nos 3 anos de El Niño forte da série de início (2010, 2016, 2024), mediana estadual no dia 6, contra o dia 18 nos anos neutros (sem La Niña) e o dia 15 em todos os demais (n = 3 anos); em 2010 e 2016 a quadra falhou, em 2024 não. Por município: 129 mais cedo, 34 mais tarde, 13 iguais. Quixadá +24 dias, com n = 3: 14% das triplas ao acaso dão ≥ 24 dias | "o El Niño atrasa o início"; o p do Mann-Whitney por município-ano; "dia 6 contra 18" sem dizer "anos neutros"; os +24 dias de Quixadá em negrito ou como regra |
| **ZARC e GAEZ em Quixadá (v3.5)** | Milho: nenhuma janela de risco 20%; risco 30% de 11/fev a 10/mar, só em AD5–AD6 do Grupo I. Caupi (só Grupo I, o único com cultivar indicada): risco 20% de 11/mar a 20/abr em 3 de 3 solos; o sintético de 21/mar fica a ±1 decêndio do oficial em 2 de 3 (8 de 9 com todos os grupos). Sorgo forrageiro (só Grupo I): 20% de 21/fev a 30/abr em 3 de 3. Mandioca: GAEZ 66,1 (boa), fora da tábua aberta do ZARC. Zoneado a 40% só a partir de 21/jan; 20% só a partir de 11/fev (a conferir). 9 portarias em Quixadá. Quixadá tem 9 culturas no cardápio | "confere com o ZARC" sem dizer o solo; "o ZARC indica plantio em janeiro"; "nenhuma cultura antes de 21/jan" sem a segunda data; "caupi 20% em 9 de 9"; a Portaria 245 como portaria do milho |
| **GAEZ (v3.5)** | Classes da camada oficial da v4: > 85 muito alta; > 70 alta; > 55 boa; > 40 média; > 25 moderada; > 10 marginal; > 0 muito marginal; corte "apta" > 40; 1 casa decimal. No CE: mandioca apta em 155 municípios, guandu em 123, milheto em 102 | "legenda oficial" para 75/63/50/35; corte > 35; mandioca apta em 164 |
| **ZARC no CE e no NE (v3.5)** | CE 2026/27: 11 portarias, uma por cultura (a 245 só para o milho com braquiária); só os grupos de ciclo com cultivar (caupi e sorgo forrageiro no Grupo I; mamona nos Grupos II–IV; a mamona tradicional, sem a de "Clima Semiárido"); janela até o último dia do decêndio; aviso com duas datas; janela por solo. NE 2026/27: 240.949 linhas, 1.794 municípios, 17 culturas, 113 portarias | a janela terminando no 1º dia do último decêndio ("21/02–11/04"); somar grupos sem cultivar |
| **Regime de chuva do NE (v3.5)** | Quadra do norte (jan–abr ou fev–mai) 1.056 municípios; litoral leste (mar–jun ou abr–jul) 312; Cerrado e sul da BA (out–jan, nov–fev ou dez–mar) 426. No litoral leste, o IMERG capta 39–72% da chuva das automáticas do INMET | os portões do CE como regra dos 9 estados |
| **Protótipo (v3.5)** | 1.794 municípios do NE; El Niño medido no próprio município; número do catálogo só para cartões T0/T1 | o alerta do CE valendo para os 9 estados |
| **Janela sintética × ZARC no estado (v3)** | Contra o solo mais permissivo: milho Spearman 0,86 e ±1 decêndio em 89%; caupi e sorgo ±1 em 38% e 2%. Contra a mediana dos solos: caupi e sorgo ±1 em 84%; milho ±1 em 8% | um veredito só para o estado |
| **Garantia-Safra (v3)** | Perda ≥ 40% (art. 8º, Lei 15.236/2025); área plantada máxima de 5 ha (art. 10, IV, Lei 12.766/2012); renda até 1,5 salário mínimo (art. 10, III); até 4 módulos fiscais (art. 10, V); rótulo da auditoria razão < 0,6: 26,0% (1998–2025) e 29,8% (2016–2025) | "40% ou 50%"; "área mínima"; a cesta antes de conferir |
| **Área das culturas (v3)** | Milho + feijão = 91% da área das lavouras temporárias (PAM 2017); com as permanentes, 66,2% (62,4% em 2025) | "91% da área" sem "temporárias" |
| **Veranico (v3)** | Acompanha a perda e acrescenta pouco à chuva: r −0,67 no município; resíduo AUC 0,593; parcial negativa em 87% dos municípios (mediana −0,22); quebra de 18,0% com veranico alto contra 7,5% nos anos de chuva normal | "o veranico explica a perda"; "quase redundante" |
| **Carbono (v3)** | Sobral (Sacramento 2013, C): a agrofloresta perde menos C que a broca com queima (−8,13 e −23,87 contra −58,87 Mg/ha); Primo 2023 é cenário de modelo (D) | "a agrofloresta recupera o carbono"; "a agrofloresta tem mais carbono"; Primo "Sobral-CE" |
| **Palma + sorgo (v3)** | IPS 6.279 contra 4.627 kg MS/ha da palma solteira; em MS, 12.130 kg/ha, sem diferença do sorgo solteiro (14.073); LER 1,51 como média de 5 regimes; ensaio irrigado | "6.279 kg MS/ha" sem "IPS"; "o consórcio supera o sorgo" |
| **Gliricídia (v3)** | Longe do grão: entre fileiras, N no grão do caupi de 18,04 para 1,58 kg/ha (Tab. 2); %Ndfa 0% junto ao milho + caupi e ~52% com buffel ou palma (Tab. 1) | "caupi com faixas de gliricídia" no mesmo talhão; o 410 contra 36 kg/ha como diferença |
| **GRACE × açudes (v3)** | ρ de Spearman 0,78 entre médias anuais (n ≈ 15–16), região hidrográfica Atlântico NE Oriental (PI a AL), Lima et al. 2020 | "r = 0,78 contra os açudes do Nordeste" |
| **SMAP no Nordeste hoje (v3)** | 30 dias até 10/11/2026, posição entre 12 anos: MA e SE 1º; PI e PE 2º; AL e BA 3º; PB e RN 4º; CE 5º (normal; na entrada de 2015 foi 2º e na de 2023, 7º) | "CE 18 contra 25 e 28"; "o solo do Ceará está mais seco que nos El Niños anteriores"; qualquer percentil pronto do SMAP de out a jan |
| **Prática atual (v3)** | Rotação declarada no Censo 2017: 7,9% dos estabelecimentos no CE; 6,1% em Quixadá (4.880 estabelecimentos); diversidade do PAM × rotação declarada, ρ +0,15 no CE | "o PAM mostra a rotação" |
| **LSPA (v3)** | Em disco para as 9 UFs, sem custo; IMERG de 30/abr contra a LSPA de abril no milho do CE: ρ 0,82 contra 0,23 (n = 19) | "cortada por custo" |

**Erratas de 14/11, tarde (sobre a v3; R3.5):**
- **"Franke África Austral +42% com w 0,41" e "ponderado ~+36%":** com a Tmax média, a África Austral tem w 0,10, nenhum número de rotação T0/T1 tem w ≥ 0,3, e o ponderado é ~+28%.
- **"Sobral 78, Harare 53 e Cerrado piauiense 42 municípios"; "RMF com confiança 0,31":** são Cerrado piauiense 102, Sobral 40, Savana da Guiné 13 e Harare 11; a RMF tem 0,75.
- **"Harare tem clima parecido e culturas diferentes":** Harare deixou de ser análogo (10º, d 2,15). O semiárido da Índia é o 2º (98,6% no top-3).
- **"Só 8 de 387 pontos: Oeste da Bahia, norte de Minas, Madagascar, Angola e Namíbia":** são 19 pontos; o norte de Minas e a China saíram.
- **"GAEZ Spearman −0,64":** é −0,76.
- **"GAEZ > 35" e as classes 75/63/50/35 como "legenda oficial":** o corte é > 40, e as classes oficiais da v4 são 85/70/55/40/25/10.
- **"Caupi com risco de 20% em 9 de 9, de 21/fev a 11/abr", em Quixadá:** só o Grupo I tem cultivar; o risco de 20% vai de 11/mar a 20/abr. O sorgo forrageiro vai de 21/fev a 30/abr (Grupo I), e o milho com 30% vai até 10/mar.
- **"O ZARC não indica nenhuma cultura antes de 21/jan":** fica, mas com a segunda data: o risco de 20% só começa em 11/fev.
- **"IMERG Final até 14/09/2026":** o Final V07 vai até 30/09/2025; depois, é o Late.
- **"Dia 6 contra o dia 18 nos demais anos":** o 18 é dos anos neutros; contra todos os demais, é 15. O "24 dias depois" de Quixadá sai do negrito: com n = 3, não se separa do acaso (14% das triplas).

**Erratas da rodada 3 (sobre a v2):**
- **"Milho e feijão ocupam 91% da área":** é das lavouras temporárias; com as permanentes, 66,2%.
- **"Veranico explica a perda":** acompanha a perda e acrescenta pouco à chuva total.
- **"Kayano & Andreoli 2006, JGR 111:D13101":** o D13101 não foi confirmado; o localizador é 2005JD006142.
- **Rossato 2017 para "solo raso":** com GLDAS e IMERG, a água no solo prevê melhor que a chuva. Sai dessa linha.
- **"GRACE com r = 0,78 contra os açudes do Nordeste":** é ρ de Spearman entre médias anuais, de Lima et al. 2020, no Atlântico NE Oriental.
- **"Palma + sorgo: 6.279 contra 4.627 kg MS/ha":** o 6.279 é o IPS; em matéria seca, o consórcio empata com o sorgo solteiro.
- **"A agrofloresta recupera o carbono em ~10 anos" (Primo 2023, "Sobral-CE"):** é simulação, com local não verificado (D). Medido em Sobral, a agrofloresta perde menos carbono que a broca com queima.
- **Salcedo 1997 para "−50% de C" e "fuga do fogo":** não sustenta nenhuma das duas. Sai.
- **"Ano úmido seguido de ano seco gera grandes queimadas" (Argibay 2020 e "Bezerra 2025"):** Bezerra é de 2026 e não trata disso; no CE, o padrão não se repete.
- **"MapBiomas Fogo: 12,7%":** o número confere; o nome fica a conferir no texto completo.
- **"Previsões como certeza custaram a confiança (Lemos 2002)":** a perda de credibilidade está em Finan & Nelson 2001, p. 105. Citar os dois.
- **"Marengo et al. (2021)":** é Marengo et al. 2022, Clim. Resil. Sustain. 1:e17.
- **"A Tmax do POWER é ~1,7 °C mais quente" como causa da ET0 maior:** contra o INMET, o viés da Tmax é de só +0,14 °C. A ET0 do POWER é 1,27 vez a das automáticas e 0,97–1,01 vez as normais.
- **Garantia-Safra "40% ou 50%" e "área mínima":** é perda ≥ 40% e área **máxima** de 5 ha.
- **"Caupi ±1 decêndio" (linha 651 da v2):** fica. Contra o ZARC oficial, em Quixadá, confere em 8 de 9 combinações (em 2 de 3 só com o Grupo I, o único com cultivar; R3.5); no estado, depende do solo.
- **"O PAM sugere a prática atual":** quem sugere a rotação declarada é o Censo 2017.
- **"LSPA cortada por custo":** já está em disco, sem custo.
- **Cisterna-calçadão de 52 m³ e cisterna de 16 m³:** volumes não confirmados (D).
- **Do catálogo de rotações:** "efeito menor na zona árida" (a aridez não reduz o efeito relativo); "caupi com faixas de gliricídia" (a gliricídia vai para faixa forrageira afastada do grão); Bowles "perdas 14–90% menores" (no corpo do artigo, rendimento 14,0% a 88,9% maior); Renwick "~17% menos perda" (são 17,1 pontos percentuais); Primo de C para D.

**Erratas da rodada 2, primeira parte (sobre a v1):**
- **"Em 19/mar, o que decide é a água que já está no solo":** o teste direto não sustenta. Sai.
- **Regras R4, R5 e R8 "(SMAP)":** eram balde de solo nu. Renomeadas.
- **"No milho, o ISNA soma +0,04":** dentro do ano, é geografia. O ISNA vira mapa de risco de base.
- **"M1 não vê 1998":** é a formulação do ISNA de cultura; o estado em percentil vê (grau C).
- **"+0,072" do combustível:** era tendência. Vira +0,02 sobre a tendência.
- **"SMAP: percentil da zona da raiz, sempre":** o percentil do produto não existe de ~12/ago a ~12/jan no sertão.
- **"A cauda vem de três episódios":** são cinco a sete anos ruins.
- **"Deslocamento do NDVI" atribuído ao MODIS:** aparece também no VIIRS; a causa principal não é o Terra.
- **"MODIS até nov/2026, buraco de jun–nov/2025":** o MODIS vai até set/2026, e a lacuna real é jul–out/2025.

**Erratas da rodada 2, segunda parte (sobre a v2, apontadas pela banca R2):**
- **"9 contra 64 de 127" como prova do SMAP:** comparava o SMAP com a pior leitura da chuva. Dentro de 2016, as 91 luzes do SMAP pegaram 64 quebras, contra 63,5 ao acaso. Vira o nível do ano em 19/mar, com a chuva desde 1/fev e o SMAP como segunda missão.
- **"Duas luzes" (soma desde 1/jan OU SMAP) como regra de 2027:** perde para a chuva desde 1/fev sozinha nos dois portões. Sai.
- **"By April, rain-to-date can fool you; the soil does not" e "the soil doesn't [remember January]":** em 2021 o solo acendeu em 81 municípios e 3 quebraram; em 2016, o SMAP só acendeu na última semana de abril. Saem.
- **"NASA's off-the-shelf SMAP drought percentile flagged 1%":** artefato da média sazonal de percentis. Sai.
- **"Two pre-registered lights":** não houve pré-registro. Vira "thresholds fixed before testing; 2027 rule chosen after seeing 2016–2025 and frozen on 14/11/2026 (internal hash)".
- **"Within-year AUC ≤ 0.60 for every layer":** o L3 dá 0,645 e o VIIRS 0,62–0,63. Vira "~0,65".
- **"With this ocean, about 5 in 10":** o 0,54 é do ONI 2,04. Vira "at the strongest El Niño before this one".
- **"70% da variância do GWS" e "o resíduo do GRACE não acompanha os açudes":** são 55% no ano fora, e o ρ +0,04 é do resíduo do CLSM; o GRACE acompanha (+0,57).
- **"SMAP sees every 9 km cell 13–15 days a month":** 13–15 é a mediana das células, e a pegada do radiômetro é de ~40 km.
- **"A third in cassava raised the worst-decile harvest from 15% to 36%":** a base certa é a S0 (0,26); "raised" soa causal; é um teto.
- **"São José abre a janela do caupi em 1998":** pelo balde, o caupi de 21/mar/1998 teve água em 15% dos municípios (Quixadá: não). Vira "o oceano mandou guardar; a chuva desde fevereiro confirmou em março; quem protegeu foi a mandioca".
- **"Sorgo até 19/mar" na troca em ano de luz acesa:** 1 em 10 municípios com água em 2016. Sai.
- **"Stanford showed/asked":** vira o nome dos autores.
- **"Reproduzido por 4 scripts" e "fed by IMERG rain":** viram "recomputado em 4 scripts a partir dos mesmos dados" e "forçado por chuva corrigida para o IMERG, segundo a equipe do L4_SM; v008 não conferida".
- **Frase de pitch "+6,6 points" de `pesquisa/artigo_ancora_objetivo.md`:** só com o rótulo "composição, não diversidade".

**Erratas da rodada 1 (mantidas):**
- **ET0:** o ~1.960 mm/ano da síntese é a ET0 do ERA5, e os 2.279 mm/ano do rascunho são a do POWER. Os dois estão certos. **Corrigido na v3:** a diferença de 15% não vem de um "viés quente da Tmax do POWER", que contra o INMET é de só +0,14 °C; dizer que "o ERA5 é que é frio" seria inferência, porque o ERA5 não foi testado contra o INMET.
- **OR 2,30 do El Niño:** era o termo de uma interação e tinha erro-padrão iid. Sai.
- **Início da estação (ρ −0,67):** é retrospectivo e mecânico. O início causal tem ρ ≈ 0 com a chuva restante. Sai a regra de fevereiro.
- **"2025, o ano mais verde"** é artefato do MODIS Terra.
- **"Fogo cerca de 6 meses depois de anos verdes":** o sinal forte é a quadra do ano anterior.
- **"O combustível explica metade da tendência do fogo":** duas séries com tendência em 14 anos não sustentam atribuição. Sai.
- **"IMERG Late da estação seca −0,5 dp" como motivo de alarme:** a chuva da estação seca não prevê a quadra (ρ −0,06 na rodada 1; ρ −0,22, n.s., na janela de 01/ago–13/nov da rodada 2). Sai de "por que agora".
- As elasticidades com mediana móvel curta estão subestimadas: o milho é +13,8%/100 mm (`pesquisador_ia_hierarquico.py`).

---

## 10. Plano de MVP para as ~36 h restantes (plano de 1 pessoa)

**Por que 1 pessoa:** às 11h de sábado o tamanho da equipe continua indefinido (Anexo A, item 3), e nenhuma tela, figura ou exportador existe. Vale o plano de 1 pessoa. O engenheiro mediu 29 h úteis por pessoa até domingo 23:59, já tirando 6 h de sono e 2 h de folga de submissão. O plano abaixo pede ~19 h e deixa cerca de 1/3 de margem (`v2_engenheiro_viabilidade_mvp.saida.txt`, bloco F). Se uma segunda pessoa entrar, ela fica com slides e vídeo, e a folga vira ensaio.

**Formato decidido:** 7 slides em inglês (PDF), vídeo de 30 s (MP4) e uma página estática. O PDF e o MP4 são a entrega que não depende de publicar nada.

| Tarefa | Horas |
|---|---|
| Bloco 0 enxuto: esquema do JSON; a folha 9.7 já está congelada neste documento | 1 |
| Figuras (matplotlib + `ceara_municipios.geojson`): par de mapas de 19/mar/2016 (chuva desde 1/jan × desde 1/fev, 127 quebras contornadas), mapa do SMAP em 30/abr/2016, painel de 2022 ao lado e Relógio estático por era | 2 |
| Exportador: lê os parquets salvos, monta a luz em 4 estados, os placares e o JSON de Quixadá | 1,5 |
| App: `index.html` novo, com JS puro e uma biblioteca de gráficos mínima, e as 3 telas | 6 |
| Textos de Quixadá com checagem por lista branca (~20 linhas) | 1 |
| Slides (7) | 3 |
| Vídeo (30 s, 70 palavras) | 2 |
| Checagem cruzada (slides × folha × app) | 1,5 |
| Publicação e submissão | 1 |
| **Total** | **19** |

**Arquitetura:**
- **Não empacotar nem importar os scripts do conselho.** Importar executa o script e sobrescreve `conselho/analises/saidas/`.
- Um único `motor/exportar.py` **lê as saídas já salvas** e reproduz os números de vitrine em menos de 1 s (o protótipo do engenheiro rodou em 0,4 s):
  - `estrategista_cache_chuva_mun_diaria.parquet` (chuva desde 1/fev e desde 1/jan por portão);
  - `saidas/v2_hidrologo_smap_pctl_mun_diario.parquet` (SMAP municipal diário, já deduplicado; média de 7 dias);
  - `saidas/agronomo_zarc_sintetico_prob.parquet` e `saidas/agronomo_isna_mun_ano.parquet` (datas-limite e ISNA final, estáticos);
  - `saidas/v2_ecologo_painel_mun_mes.parquet` (VIIRS mensal por município, a testemunha de junho);
  - o PAM.
- **Sem** cópia de `simular()`: há 4 versões diferentes no conselho, e as trajetórias animadas saíram. **Sem** M2.
- Sai um JSON por município (184; ~3 kB cada). O painel "hoje" é um JSON fixo copiado da folha 9.7. **A página é estática e não chama nenhuma API ao vivo.** O `site-nasa/` antigo (Flask, Nominatim, globo 3D com 7,6 MB de texturas e ladrilhos Esri online) é abandonado; dele sai no máximo o CSS.

| Bloco | Quando | Tarefa | Pronto quando |
|---|---|---|---|
| 0 | Sáb 12–13h | Esquema do JSON; folha 9.7 como `motor/folha.json` | Ninguém usa número fora da folha |
| 1 | Sáb 13–15h | **As figuras primeiro.** Um mesmo par de mapas alimenta o slide 4, os primeiros 13 s do vídeo e o replay de 2016 | As legendas batem com o bloco C do fechamento (7/182, 182/182, 127; 2022: 142 e 0) |
| 2 | Sáb 15–16:30 | `motor/exportar.py` e o JSON dos 184 | O JSON de Quixadá bate com o bloco D (9 alertas e 3 acertos em 19/mar; 9 e 5 em 30/abr) |
| — | **Sáb até 18h** | **José:** conversa com 1 técnico de ATER; OK (ou não) para repositório e página públicos | — |
| 3 | Sáb 16:30–22h | App: Relógio (luz em 4 estados, termômetro, placar, painel "hoje" com 4 itens), cartões de Quixadá, replay estático de 1998 e 2016, glossário | Quixadá carrega em < 2 s no celular |
| — | **Sáb 22h** | **Números congelados** | — |
| 4 | Sáb 22–23h | Textos de Quixadá e checagem por lista branca | Zero número fora do JSON ou da folha |
| — | **Dom 02–08h** | **Sono obrigatório** | — |
| 5 | Dom 08–11h | 7 slides (seção 11.1) | No máximo 3 números no corpo de cada slide |
| 6 | Dom 11–13h | Vídeo (seção 11.2) | 70 palavras; gravado até 13h |
| 7 | Dom 13–14:30 | Checagem cruzada e ensaio | Nenhuma divergência |
| 8 | Dom 14:30–15:30 | Publicação (só com o OK do José) ou PDF + MP4; submissão | Submetido muito antes das 22h; folga até 23:59 |

**Se faltar tempo, cortar nesta ordem:**
1. O replay de 2016 vira só a figura do slide 4.
2. O seletor dos 184 municípios vira Quixadá e mais 2 vizinhos.
3. O painel "hoje" vira uma imagem.

**Nunca cortar:**
- a figura de 2016 no nível do ano, com 2022 ao lado;
- o placar de Quixadá, com o 0 acerto do SMAP;
- os 4 cartões de Quixadá, com o "sem número" onde não há número;
- o replay de 1998 com o observado do IBGE (estático);
- a folha canônica.

**Cortados de saída do MVP:** M2 e seleção aninhada; trajetórias diárias animadas e barras de ISNA diárias; cartões para 184 municípios e pesos da família; globo, MapLibre, Esri e Nominatim; auditoria gerada em Python (vira `AUDIT.md`); suíte de 30 casos adversariais (vira lista branca); do painel "hoje", a chuva da estação seca, o GWS do CLSM e os açudes do Landsat; pontos globais (vira 1 linha); NLDAS-2, GLDAS Noah e IMERG Early fora do recibo; código de barras ao vivo; áudio e TTS; modo global e SMAP ao vivo; ECOSTRESS, GNN e Prithvi; simulador de WhatsApp; FIRMS NRT e CDL; explicador LLM em tempo de execução. A LSPA sai da tela por escopo, não por custo: já está em disco e vai ao AUDIT.md (9.6).

**Próximos passos (slide):** floresta causal no talhão à maneira de Kluger (MapBiomas/HLS + pico de NDVI calibrado no PAM + estado da água como modificador), Prithvi-EO-2.0, Sentinel-1/NISAR para datar o plantio (com a regra de validação contra o SMAP L3), assimilação do SMAP L4 no balde, ECOSTRESS/ESI como gatilho, bot de WhatsApp com áudio, rede de pluviômetros, veredito tricot, EVPPI e GEOS-S2S.

---

## 11. Roteiro da demo

### 11.1 Os 7 slides (em inglês; no máximo 3 números no corpo e 1 linha de recibo no rodapé)

1. **"One window, one chance."** (o problema)
   - Map of Ceará, 1998 and 2012: **3 in 4 counties** lost more than half their corn.
   - "Corn and beans fail together (**ρ 0.78**). Evaporative demand beats rain in **10 of 12 months**."
   - One line: "Kluger, Di Tommaso & Lobell (ERL 2025) showed that rotation benefits change with climate, in temperate breadbaskets and without water data. In the semi-arid, what decides is *when* the water shows up."
   - "Same problem in the Sahel, rain-fed India and semi-arid Texas."
2. **"QUADRA: rotation as a policy with checkpoints."**
   - *QUADRA: the sertão's word for the rainy season.* Five checkpoints on one calendar; each plan is a 3-year sequence (2027–2029), dry season included.
   - "In a one-window climate, rotation happens inside the season (relay, strips) and across years (legume, cassava, perennials, fallow without fire)."
   - "NASA is the engine, IBGE (Brazil's official crop statistics) is the referee." Rodapé: "28 rainy seasons × 184 counties".
3. **"Three curves decide when to decide."** É a imagem principal. Só dois portões marcados: **Mar 19, last day to switch**, and **Apr 30, salvage only**.
   - Skill, last decade, Mar 19: "NASA rain counted from Feb 1: **0.71**; counted from Jan 1: 0.55" (curva das duas eras ao lado, nunca a agregada sozinha).
   - Options: "On Mar 19, corn still fits in **4 of 10** counties, cowpea in 10 of 10."
   - Visibility: "Optical satellites go partly blind at decision time (**4 in 10** usable pixels in Jan–Mar); SMAP's radiometer sees through clouds."
   - Rodapé (São José): "São José rain says as much as all the rain-to-date, which is not much (ρ ≈ +0.3, n = 28)."
   - Segunda linha do rodapé (nova na v3, sem número novo): "Planting windows: synthetic, checked against Brazil's official ZARC; the verdict depends on the soil."
4. **Momento uau: "2016: the same NASA rain, read two ways."**
   - Par de mapas de 19/mar/2016: "Counted from January 1: **7 of 182** counties flagged. Counted from February 1: **182 of 182**."
   - "**7 in 10** counties went on to lose their corn. By April 30, NASA SMAP soil moisture agreed in half the state."
   - Caixa ao lado: "**2022**: rain light in 142 counties, SMAP in none; 3 lost corn. That is why a second NASA mission confirms."
   - Caixa embaixo: "Which county? Neither reading knows. Skill is regional."
   - Rodapé: "Same alarm count, the Jan-1 reading catches 55 of 127. Five IMERG readings compared in AUDIT.md. Rule chosen after seeing 2016–2025; thresholds fixed before testing (commit 48a3608); frozen for 2027. Today's reprocessed products. Grade B."
5. **"Your county, every season replayed."** (Quixadá)
   - Replay de 1998 e de 2016 em quadros estáticos; os 4 cartões como sequências 2027–2029.
   - "Two droughts, two shields: early-March cowpea had water in **7 of 10** counties in 2016 and 1 of 10 in 1998. In 1998, cassava planted the year before still gave half a harvest in Quixadá."
   - "Against today's corn + beans, a third in cassava lifts the worst-year-in-ten from **0.26 to 0.36** (a ceiling: part of it is just averaging)."
   - Placar honesto: "In Quixadá the soil light never hit; the rain light hit **5 of 9** alerts on Apr 30."
   - Linha nova na v3 (sem número): "Dona Francisca's 2027–2029 plan: three strips that switch places every year (cassava buffer from 2028, early cowpea, forage sorghum); legume before corn only in a good year."
   - Rodapé: "Staggered sowing and legume-that-stays: no worst-year number yet; not in the record. Switching from today's intercrop to rotation over time has never been measured."
6. **"NASA is the engine, IBGE is the referee. How we used SI, honestly."**
   - *On screen:* IMERG, SMAP L4, VIIRS, GRACE/GRACE-FO, SRTM. *In our analysis (repo):* SMAP L3, GLDAS-2.1/2.2, MODIS, Landsat/HLS, POWER, NEX-GDDP, NLDAS-2. *Roadmap:* ECOSTRESS, NISAR, Prithvi.
   - "Every curve by era: the rule that worked in 1998–2015 failed in 2016–2025, and we show it. Fair baselines: SMAP was compared with the best rain reading, and lost the main-light role."
   - "Random validation lies (**0.49 vs −0.08**)."
   - "What did not work: causal ML on county statistics (a placebo failed); the diversity link is composition, not diversity (rain-fed crops only: **+1.4 points**, not significant)."
   - "Satellites know the bad year, not the bad county (within-year AUC up to ~**0.65**; geography alone 0.61)."
   - Linha nova na v3 (sem número no corpo): "Evidence transfer measured with NASA POWER: the temperate breadbaskets where rotation was measured by satellite get zero climate weight for the sertão, and no rotation-over-time trial comes from a sertão-like climate." Nas notas: w = 0,00; nenhum número de rotação T0/T1 com w ≥ 0,3 (Franke África Austral w 0,10); o motor usa +24%, e o ponderado pelo clima (+28%) é só sensibilidade.
7. **"Today: strongest Aug–Oct El Niño on record (ONI +2.46)."**
   - "In a typical year, **2 in 10** counties lose half their corn. At the strongest El Niño before this one, about **5 in 10** (range 2–8). This year is beyond the record."
   - "Soil thermometer: asleep, as every November. Water bank: normal."
   - Ações para Dona Francisca (fictícia): "Buy cowpea seed now. Keep half the field for an early-March decision. Find cassava cuttings for February. Don't burn."
   - Frase do técnico de ATER, se obtida com permissão.
   - "NASA evidence. The farmer decides."

### 11.2 Vídeo de 30 s (em inglês, com legenda; 70 palavras, contadas no bloco I do fechamento)

| Tempo | Imagem | Locução |
|---|---|---|
| 0–6 s | Mapa do Ceará em 19/mar/2016, quase todo verde pela soma desde janeiro; legenda "QUADRA: the sertão's word for the rainy season" | "March 19, 2016, the last day to switch crops. NASA rain counted from January looked normal." |
| 6–13 s | O mesmo mapa pela chuva desde 1/fev, todo aceso; depois o SMAP de 30/abr acendendo metade | "Counted from February, it said dry everywhere. By April, NASA soil moisture agreed in half the state." |
| 13–19 s | As 127 quebras contornadas; legenda "2022: false alarm, the soil did not confirm" | "Seven in ten counties lost their corn. A wet January hid a dry season." |
| 19–26 s | Mostrador do ONI; Relógio com o P1 aceso e o termômetro dormindo | "Today: a record El Niño. Buy cowpea seed, keep half the field for an early-March decision, don't burn." |
| 26–30 s | O técnico e a família olhando o cartão | "NASA evidence. The farmer decides." |

Rodapé fixo: "Same NASA rain, two readings · false alarms in 2021 and 2022 · today's reprocessed products · grade B". O vídeo não fala em Stanford, não diz que o solo decide em São José e não diz que o SMAP ajuda em novembro.

**Como reproduzir o número-uau (19/mar/2016: 7 e 182 de 182; 127 quebras; 2022: 142 e 0):**
1. Se faltar `saidas/v2_hidrologo_smap_pctl_mun_diario.parquet`: `E:/campeonato-nasa/venv/Scripts/python.exe -I "c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/v2_hidrologo_cinco_fontes_umidade.py"`.
2. `E:/campeonato-nasa/venv/Scripts/python.exe -I "c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/v2_arquiteto_r2_fechamento.py"` (36 s). No bloco C, em [19/mar], linha "2016:": "chuva 1/jan: luz em 7/182", "chuva 1/fev: luz em 182/182, pega 127/127", "SMAP 7d: luz em 56/182"; linha "2022:": "chuva 1/fev: luz em 142/182", "SMAP 7d: luz em 0/182". Em [30/abr], "SMAP 7d: luz em 91/182". Também no bloco C: a tabela dos estados de duas missões e o comparador de mesmo número de alarmes (55/127).
3. Reprodução a partir do `.nc` cru, com agregação municipal própria: `v2_juiz_numero_uau.py` (o SMAP de 30/abr/2016 com 91 luzes e 64 quebras; 2021 com 81 luzes).
- Quebra canônica: produção ÷ área plantada < 50% da mediana dos outros anos (milho, PAM, área ≥ 50 ha). Luz principal: IMERG de 1/fev até o portão < 75% do normal. Segunda missão: percentil da zona da raiz do SMAP L4 < 20, média dos 7 dias até o portão.

**Cuidados:**
- A família é fictícia e rotulada.
- Não usar logomarca da FUNCEME, da Ematerce ou da NASA que sugira endosso. Os selos dizem "data from".
- "QUADRA: the sertão's word for the rainy season" aparece na legenda do primeiro segundo.
- Nenhum mapa municipal fica "vermelho de acerto": a legenda diz "flagged", e a caixa "which county? neither reading knows" fica no mesmo quadro.
- Nenhum número do Kluger no vídeo nem nos slides até a conferência na versão publicada.

---

## 12. Mapa de prêmios-alvo e critérios de julgamento

### 12.1 Prêmios

| Prêmio | Prioridade | O que o sustenta |
|---|---|---|
| **Best Use of Science** | 1ª | Curvas validadas por ano e por era; linha de base justa (o SMAP perdeu o posto de luz principal para a melhor leitura da chuva); regra de 2027 congelada com hash; IBGE como árbitro; resultados negativos declarados (soma em 2016–2025, Quixadá, SMAP de novembro, IA causal no PAM, média de percentis); recibo A–D com marca ·T; ponte com Kluger et al. 2025. **v3:** transferência de evidência medida com o POWER (celeiros temperados com peso zero; "não medido" para a troca do consórcio de hoje) e 18 trechos corrigidos contra os artigos do Nordeste. |
| **Best Storytelling** | 2ª | 2016, "a mesma chuva da NASA, lida de dois jeitos"; 2022, o alarme falso que a segunda missão segurou; "duas secas, dois escudos" (1998 e 2016); São José testado com respeito; 2027 ao vivo; Dona Francisca. |
| **Local Impact** | 3ª | Ceará, 184 municípios (o protótipo "escolha o lugar" cobre os 1.794 do Nordeste), técnico no circuito, ações baratas em novembro, decisão do caupi no início de março, maniva e semente; validação com um técnico de ATER (se feita). **v3:** plano por faixas 2027–2029 dentro da janela do ZARC oficial, e as regras do Garantia-Safra conferidas na lei. |
| **Best Use of Data** | 4ª | Duas missões na luz (GPM IMERG e SMAP L4), o L3 como checagem, o VIIRS como continuidade do MODIS e testemunha, a escala útil medida entre sensores, o sentinela de deriva, o relato copiado no PAM. |
| **Galactic Impact** | Indicação | Motor global (o SMAP L4 cobre 99,6% da terra entre 60°S e 60°N; o IMERG é quase global); "40 de 47 pontos terrestres tropicais sem mês de quebra térmica". **v3:** onde o sertão se repete no planeta (só 19 de 387 pontos de terra muito parecidos, todos entre 30°S e 24°N: Chaco argentino, Oeste da Bahia, norte da Austrália, Burkina Faso, sudoeste de Madagascar, Deccan...); GAEZ + ZARC sintético fora do Brasil. |
| Best Use of Technology | Não é alvo | A página estática é simples de propósito. |

### 12.2 Critérios (notas de 1 a 5)

| Critério | Como atendemos | Risco e mitigação |
|---|---|---|
| **Impacto** | Decisão real de uma família numa data real (2027); métrica do ano ruim onde ela existe; ações baratas em novembro e no início de março; canal pelo extensionista; carteira medida nos anos em que a luz NASA acendeu. | Família fictícia e nenhum usuário real ainda. Mitigação: 1 conversa com ATER até sáb 18h, com 1 frase e 1 mudança feita por causa dela, no slide 7. |
| **Criatividade** | Calendário derivado de três curvas; a leitura da água como achado; luz em quatro estados com duas missões; rotação como política em 3 anos; "duas secas, dois escudos"; São José; entressafra como portão; honestidade como funcionalidade. | O júri pode ler como alerta de seca + carteira. Mitigação: o slide 2 (sequências 2027–2029) e o slide 5 ("duas secas, dois escudos"). |
| **Validade** | Definição canônica única; curvas por era; linha de base justa; nível do ano; regra congelada; validação por ano; leitura menos favorável; recibo; AUDIT.md; onde erramos. | Habilidade regional; em São José, na última década, nenhuma leitura ordena bem os anos; a escolha da luz foi feita depois de ver os dados. Mitigação: grau B, 2022 e 2021 ao lado de 2016, o placar de Quixadá e "which county? neither reading knows". |
| **Relevância (NASA no núcleo)** | A luz é o GPM IMERG lido como estado; a confirmação é o SMAP L4 (checado pelo L3); o balde é IMERG + POWER calibrado contra o SMAP; o verde é VIIRS; o relevo é SRTM; o banco lento é IMERG + GRACE. | O ONI é da NOAA, e o árbitro é o IBGE. Mitigação: "NASA tells the state, the ocean tells the odds"; o IBGE só confere. |
| **Apresentação** | Uma imagem (as três curvas), um número-uau no nível do ano, três telas, no máximo 3 números por slide e 70 palavras no vídeo. | A página não existe às 11h de sábado. Mitigação: plano de 1 pessoa, figuras primeiro, PDF e MP4 como entrega independente. |

### 12.3 Texto curto "How we used SI" (para a submissão)

Ver "Use of SI (AI) tools", no fim deste documento.

---

## 13. O que a banca questionou e como respondemos

### 13.1 Rodada 1 (banca adversária sobre o rascunho v1)

Notas da banca ao rascunho v1, de 1 a 5:

| Revisor | Impacto | Criatividade | Validade | Relevância NASA | Apresentação |
|---|---|---|---|---|---|
| Juiz da Space Apps | 3,5 | 4 | 3,5 | 4 | 3 |
| Cético científico | 4 | 4 | 2,5 | 3,5 | 3 |
| Engenheiro de viabilidade | 4 | 4 | 3 | 4 | 3 |

Todos os problemas de gravidade alta e média estão abaixo, agrupados quando dois revisores apontaram o mesmo. "J" é o juiz, "C" o cético e "E" o engenheiro.

| # | Crítica (quem, gravidade) | Resposta |
|---|---|---|
| 1 | O "3×" da demo de Quixadá (0,35 contra 0,10) usa área colhida, exclui as perdas totais e cai em 2016; em 2012 não havia mandioca (J alta, E alta, C alta) | **Cortado.** Entram a carteira estadual canônica (0,15 → 0,36, agora com IC90 por ano) e o observado de Quixadá em 1998 (milho 0,00; feijão 0,16; mandioca 0,50; carteira 0,22). |
| 2 | O replay de 2012 mostra um alerta tarde demais; não mostra decisão mudando (J alta) | **Replay principal trocado para 1998**, o análogo de El Niño. O alerta acende em Quixadá em 19/mar (70%), antes da data-limite do caupi (21/mar). Esta conta foi refeita com o normal sem o próprio ano. 2012 fica como "pego tarde"; 2016 vai para a auditoria como erro. A frase é "switch window opened", não "harvest rescued". O engenheiro sugeriu 2016 em Quixadá ou 2012 em Tauá; preferimos 1998, que é calculável (Quixadá tinha 600 ha de mandioca) e amarra P1, P3 e 2027. |
| 3 | Linhas de base escolhidas a dedo: R² 0,365 contra 0,102; 0,794 contra 0,727; "small beats big" (J alta, C alta, E alta e média) | **Só comparações pareadas:** ρ dentro do ano 0,155 → 0,307 e AUC 0,816 → 0,851 com o HGB só de chuva; monotônico contra livre com as mesmas entradas, +0,03 no milho e nada no feijão; ISNA soma ~+0,04 no milho e piora o feijão. "Small beats big" sai. A AUC 0,851 é rotulada como fim de safra. |
| 4 | "On your land" promete mais do que a habilidade entrega (J alta) | Tagline trocada para "over your county". A tela diz "seu município / sua região" e mostra o placar local. |
| 5 | "Em janeiro ninguém sabe" contradiz o P1, que se apoia no ONI (C alta) | Curva refeita com duas linhas: chuva NASA (0,57 → 0,80) e oceano (0,67 desde novembro). A frase passa a ser "rain-to-date says almost nothing; the ocean says a little". |
| 6 | OR 2,30 do El Niño: era um termo de interação, com EP iid; com EP por ano, OR 1,57 e p = 0,27 (C alta) | **Cortado.** Entra a contagem: 3 dos 6 El Niños desde 1998 viraram catástrofe e 3 passaram. Grau B. Toda variável anual passa a ter EP agrupado por ano. |
| 7 | Oito números de cabeçalho com cinco definições de quebra (C alta) | Tabela 9.2 refeita com a definição canônica e uma regra de alerta. Recalculados por nós: curva, alerta, carteira e possibilidade. Os números de outras definições estão proibidos no deck. |
| 8 | M2: melhor de 14 configurações escolhida no teste; alvo não canônico; fim de safra (C alta) | Faixa das 14 (0,78–0,85) reportada; rótulo de fim de safra; seleção aninhada no bloco 0; o observado do replay usa sempre a razão canônica. |
| 9 | O teste de São José é injusto: compara com a quadra inteira, não com o resto dela (C alta) | Reescrito com o teste justo: a chuva do dia e o acumulado dizem o mesmo sobre o resto (ρ +0,32 nos dois). "A tradição é fraca, não errada." A AUC 0,73 fica só como estado do roçado. |
| 10 | Análogos com falsa precisão: "5 a 7 em 10" (J média, C alta) | Agora é contagem: 4 de 7, contra 1 em 3 normalmente, com a faixa de 2 a 9 em 10. Mostra o limiar, o n e marca 1966 como proxy. |
| 11 | GRACE "caindo para p35" é um mês dentro do ruído (C alta; J média pediu o GRACE no painel) | Sai de "por que agora" e do P1 como alarme. No painel "hoje", entra como "banco regional normal (p57, média de jul–set)". Atende o juiz (GRACE no painel) sem o alarme falso. |
| 12 | Fogo: área de pixel tratada como área queimada; intervalo de 3 anos por célula e censurado (C alta) | Reescrito: "17% da área em células com ≥ 1 foco"; área pelo MapBiomas (12,7% da Caatinga em 39 anos). O intervalo de retorno vira grau C e sai do pitch. A ligação direta com Primo sai. |
| 13 | Mandioca como amortecedor apoiada em relato copiado (C alta; J baixa) | Carteira refeita sem os anos repetidos: 0,14 → 0,34, o ganho resiste. Grau A no estado e B no município. Maniva vira risco nº 1, com "plantar no ano anterior". O relato copiado vira camada do M6. Um motor de carteira só. |
| 14 | O balde M1 não vê 1998; a errata da ET0 estava invertida (J média, C média) | Errata corrigida: os dois valores estão certos, cada um pela sua fonte. ZARC sintético refeito com ET0 × 0,87: as datas andam no máximo 1 decêndio em 97–99% dos municípios, então o cartão mostra ±1 decêndio. Nos slides, "ET0 exceeds rain in 10 of 12 months". O risco de 2027 vem do M3/ONI, não do balde. |
| 15 | Relevância NASA mais fraca do que o slide sugere; SMAP e ECOSTRESS sem dado em disco (J média, E alta) | Rótulos "used / pipeline ready / roadmap". O ECOSTRESS sai do P4. O replay mostra a estimativa NASA contra o IBGE. O SMAP entra com recibo se chegar até sáb 20h. No painel "hoje" ficam o ONI, o GRACE e o açude do Landsat, e o IMERG Late como contexto. |
| 16 | Parece diversificação, não rotação (J média) | Cada estratégia é uma sequência 2027–2029 com a entressafra; a S2 vira faixas que giram; nenhuma alternativa queima. |
| 17 | Escopo grande demais para ~38 h; empacotar scripts é uma armadilha (J média, E alta) | MVP de 3 telas e cerca de 27 horas-pessoa. Exportador que lê as saídas salvas, sem importar scripts. Números congelados no sáb 22h, sono das 02h às 08h, app congelado no dom 08h. O verificador sai da lista "nunca cortar". |
| 18 | "O alerta" tem quatro definições (J média, C média) | Uma regra só (< 75% do normal desde 1/jan), com todos os números refeitos e o n ao lado. O "011" sai do pitch. |
| 19 | Proveniência imprecisa: "28 anos de GPM"; reanálise chamada de observação; deriva da LST "descoberta" (J média, C média e baixa) | "IMERG (TRMM + GPM eras), 1998–2025"; o POWER é marcado como reanálise; a frase da deriva diz que ela é documentada pela NASA. |
| 20 | Falta validação com usuário real (J média) | Tarefa do José até sáb 18h: 1 conversa com ATER ou com um agricultor, 1 frase com permissão e 1 mudança feita, no slide 7. Agentes não fazem esse contato. |
| 21 | Conformal compra cobertura com largura (C média) | A largura é reportada (227 → 282 p.p. no pré-safra), com a frase "em janeiro a incerteza honesta é do tamanho da climatologia". |
| 22 | NDVI "+0,053" listado como deriva pega; "metade da tendência do fogo"; viés sem unidade (C média) | Rotulado como "deslocamento não explicado". A atribuição do fogo sai. O viés ganha unidade (~60 pontos de rendimento relativo). |
| 23 | Oceano "decide o quando e o quanto" exagera (C média) | Sai do pitch. Na auditoria: "o Pacífico informa mais sobre a quebra do que sobre o tercil de chuva (exploratório; depende de 3 anos)". |
| 24 | Portão de habilidade de novembro com n = 10 (C média) | Mostrado com o n e só como argumento qualitativo. |
| 25 | Graus mal atribuídos (C média) | Criada a marca ·T. ZARC sintético passa para C; Diniz e Souza para C (ensaio único); Silva 2009 para D (sai); carbono da S3 por Primo (C), não por Jian; Kallenberg descrito corretamente. |
| 26 | 0,78 milho × feijão: "independentes" e "três especialistas confirmaram" (C média) | "No registro do PAM, quebram juntos", com 0,67 sem o choque do ano e a ressalva do relato. As duas frases saem. |
| 27 | "86% dos trópicos" inclui um ponto no oceano (C média) | "40 de 47 pontos terrestres tropicais amostrados". |
| 28 | Explicador LLM em tempo de execução; saldo da API acabou; TTS depende de serviço (E alta) | Textos redigidos offline e congelados, verificador regex, nenhuma API em execução. Áudio só com voz humana gravada até sáb 18h; senão, sai. |
| 29 | Os 4 cartões "divergem dia a dia" sem estado diário para todas as estratégias (E alta) | Animam a chuva IMERG e as barras de ISNA por cultura (C); o PAM é revelado na colheita (A); a S3 fica hachurada. |
| 30 | "81% de 131" não é a S2 (E média) | A S2 cita só a carteira 1/3; o 81% vai para a auditoria como "diversificação em geral". |
| 31 | Modo global sem dados nem calibração (E média) | 2 pontos baixados hoje em segundo plano, grau C, "pontos pré-calculados; qualquer ponto na próxima versão". A calibração inversa fora do Brasil vai para o roteiro. |
| 32 | "Meu chão" só existe em 4 AOIs (E média) | O código de barras vira figura estática de 1 AOI; nos 184 municípios, PAM + 1 pergunta. O selo de visibilidade mostra o n e o valor antes de 2015. |
| 33 | ZARC oficial e Garantia-Safra usados como restrição dura sem conferência (E média; J baixa) | "Janela sintética tipo-ZARC", com "confirmar no ZARC oficial". O Garantia-Safra só entra se o José conferir na lei até sáb 14h. |
| 34 | Replay em 44 temporadas, blocos plurianuais com estado e Pareto em 8 eixos exigem código novo (E média) | Só as 28 quadras do IMERG; as sequências de 3 anos são planos, com prior da literatura para o antecessor, sem estado simulado; 3 eixos calculados e etiquetas com grau. |
| 35 | Regras da Space Apps sobre trabalho anterior não conferidas (E média) | Tarefa do José hoje de manhã. Se houver restrição, a submissão separa a preparação prévia do que foi construído no fim de semana. |

**Baixa gravidade, também resolvidos:**
- IMERG Late saiu de "por que agora", e a unidade foi anotada (C).
- O selo de 92% agora traz o n (C).
- O açude passou a ser "dois sensores e um modelo, numa AOI" (C).
- O verificador ganhou gabarito, léxico proibido e 30 casos adversariais (C).
- O replay de Quixadá em 2023–2025 foi rodado e vai para a auditoria (C).
- "QUADRA" ganhou glosa na primeira menção (J).
- O IMERG Late municipal foi rotulado como estadual (E).
- FIRMS NRT, LSPA, CDL e o simulador de WhatsApp foram cortados; o pré-registro só sai com o OK do José; o mapa usa o GeoJSON sem tiles (E). (Nota da v3: a LSPA já está em disco para as 9 UFs, sem custo; ver 9.6.)

**Onde não seguimos a banca, e por quê:**
- **Replay de 2016 ou de Tauá (E):** preferimos 1998. Ver o item 2.
- **IMERG Late com "−0,5 dp" no painel "hoje" (J):** entra como contexto de frescor dos dados, com a frase "isso não prevê a quadra (ρ −0,06)". O dado do cético mostra que a chuva da estação seca não informa a quadra.
- **Grau B/C para toda a mandioca (C):** mantivemos o grau A para o resultado estadual, porque ele resiste à retirada dos anos repetidos, com IC por ano. O nível do município fica em B.

### 13.2 O que a banca da rodada 2 questionou e como respondemos

**Notas da banca, de 1 a 5** (rodada 1 sobre o rascunho v1; rodada 2 sobre a v2 antes desta correção):

| Revisor | Rodada | Impacto | Criatividade | Validade | Relevância NASA | Apresentação |
|---|---|---|---|---|---|---|
| Juiz da Space Apps | R1 | 3,5 | 4 | 3,5 | 4 | 3 |
| Juiz da Space Apps | R2 | 3,5 | 4 | 3,5 | **4,5** | 3 |
| Cético científico | R1 | 4 | 4 | 2,5 | 3,5 | 3 |
| Cético científico | R2 | 4 | 4 | **3** | **4** | 3 |
| Engenheiro de viabilidade | R1 | 4 | 4 | 3 | 4 | 3 |
| Engenheiro de viabilidade | R2 | **3,5** | 4 | **4** | 4 | **2,5** |
| **Média** | R1 | 3,83 | 4,00 | 3,00 | 3,83 | 3,00 |
| **Média** | R2 | 3,67 | 4,00 | 3,50 | 4,17 | 2,83 |

**Leitura:** a v2 ganhou Validade (+0,5) e Relevância (+0,33), perdeu um pouco em Impacto e Apresentação (o MVP não existe e o escopo cresceu) e manteve a Criatividade. O juiz disse que, com três consertos baratos, Validade e Apresentação sobem para 4 (contar no nível do ano; "duas missões NASA veem o estado da água"; roteiro de 70 palavras). Os três foram feitos. Para ele, o Impacto só sobe com o técnico de ATER e com números de rotação; os números foram feitos onde dá, e o técnico depende do José.

Todos os problemas de gravidade alta e média estão abaixo, agrupados quando dois revisores apontaram o mesmo ("J" juiz, "C" cético, "E" engenheiro).

| # | Crítica (quem, gravidade) | Resposta | Onde |
|---|---|---|---|
| 1 | O "9 contra 64 de 127" mede quantos alarmes acenderam, não quais municípios: dentro de 2016, 64 acertos contra 63,5 ao acaso (J alta). E compara o SMAP com a **pior** leitura da chuva (C alta) | **Refeito no nível do ano, em 19/mar:** 7 contra 182 de 182, com 127 quebras. Comparador de mesmo número de alarmes: a soma pegaria 55. "Qual município? Nenhuma leitura sabe" (AUC dentro de 2016 de 0,53 a 0,65). Acerto municipal só como exemplo de 2025 (SMAP 21 de 45 contra 11,4 ao acaso; vizinhos não são independentes). As 5 leituras da chuva lado a lado no AUDIT.md. Regra nova "linha de base justa" (9.1) | R2.1; M3; 9.2 nº 4; slide 4 |
| 2 | O que faz a diferença é o estado da água, não o SMAP: o API dá 0,80, e "duas luzes" perde para a chuva desde 1/fev nos dois portões; padrão duplo entre proibir fevereiro e adotar o SMAP (J alta; C alta) | **Luz principal trocada** para a chuva IMERG desde 1/fev, pelo critério pré-declarado R1 (maior AUC mínima entre eras e portões: 0,709). O SMAP vira segunda missão (vermelho 5,3 em 10 contra amarelo 2,1 em 19/mar). O API fica no recibo (é o melhor em 30/abr, mas cai para 0,61 em 19/mar na última década). O padrão duplo acaba: as duas escolhas são pós-teste e são ditas assim. Frase: "Two NASA missions see the water state; rain counted from January doesn't" | R2.2 linha 10; M3 |
| 3 | O vídeo se contradiz (número de 30/abr, quando só cabe salvar, seguido de "you can still switch") e tem 85 palavras (J alta; E alta) | **Reescrito com 70 palavras.** O número é de 19/mar (último dia de troca), o SMAP de 30/abr entra como confirmação, e a ação de 2027 é "early-March decision". Stanford saiu | 11.2; fechamento, bloco I |
| 4 | Rotação e saúde do solo sem número; S1 sem métrica; cartões para 184 municípios sem dados (J alta; E alta) | **S0 de Quixadá calculada** (6 de 28 anos abaixo da metade; pior ano 0,16; mediana 1,05). **Carteira contra a S0** (0,26 → 0,36, teto) e **nos anos de luz NASA acesa** (0,13 → 0,21; IC90 do ganho +0,04 a +0,10). **S1: contrafactual da metade guardada** em 1998, 2016 e 2024 (grau C). As 3 métricas da S1 e da S3 ficam "sem número", com justificativa: não há S1 observada, e o balde não vê a quebra de 1998. Cartões só de Quixadá, ordem fixa | 6.2; M4; R2.2 linhas 12 e 14 |
| 5 | Slide 6, "o percentil pronto do SMAP acendeu em 1% em 2016", contradiz o slide 4, e o "1%" é artefato da média de percentis (J média; C alta) | **Saiu.** O 2.2 e a 9.3 foram reescritos; o gatilho tipo Garantia-Safra fica no AUDIT.md com "escalas diferentes; refazer"; nova linha 11 na arbitragem | R2.2 linha 11; 2.2; 9.3 |
| 6 | "The soil does not fool you" e "rain-to-date remembers January; the soil doesn't" são refutadas pelos dados (2021; o SMAP só acendeu no fim de abril) (J média; C alta) | **Proibidas** (9.7). Fica a frase de mecanismo "rain counted from January remembers a wet January; rain counted from February doesn't", sempre com 2022 ou 2021 ao lado | 1; 9.7 |
| 7 | O replay de 1998 contradiz a regra nova do caupi, e o "sorgo até 19/mar" não se sustenta (J média) | **Balde rodado para 1998:** caupi de 11/mar com água em 10% dos municípios, de 21/mar em 15% (Quixadá: não nos dois). A legenda muda para "o oceano mandou guardar, a chuva desde fevereiro confirmou em março, quem protegeu foi a mandioca". **O sorgo sai da troca** (1 em 10 municípios em 2016). Nasce o "duas secas, dois escudos" | 6.1; S1; S2; 7.3 |
| 8 | "Pre-registered" é exagero (J média; C média) | **Saiu.** Fica "thresholds fixed before testing (75% in round 1; 20 in commit 48a3608, 14/11 08:34); 2027 rule chosen after seeing 2016–2025 and frozen on 14/11/2026 (internal hash)". O congelamento foi feito de fato (sha256 no bloco B). O "teste fora da amostra com substituto" deixou de ser necessário: a luz nova tem as duas eras | M3; 9.1; Use of SI |
| 9 | Apresentação sobrecarregada: 5 a 10 afirmações por slide; slide 1 com o artigo de outros e um nulo; formato e equipe indefinidos (J média; E média) | O slide 1 virou o problema, com Kluger numa linha. O nulo da diversidade foi para o slide 6. No máximo 3 números no corpo. O slide 3 marca só 19/mar e 30/abr. O slide 6 separa "on screen" de "in our analysis". Formato decidido: PDF + MP4 + página estática, com plano de 1 pessoa | 11.1; 10 |
| 10 | Impacto sem usuário real nem valor de decisão medido; o município da demo é onde a luz nova nunca acertou (J média) | O contrafactual foi medido (grau C). Com a luz nova, Quixadá passa a ter 5 acertos em 9 alertas em 30/abr; o SMAP continua com 0, e isso fica na tela. **A conversa com o técnico de ATER continua sendo do José, até as 18h** (agentes não fazem esse contato). Mantivemos Quixadá: o placar honesto é um ativo de Validade | 6.2; Anexo A |
| 11 | O resumo diz que a mandioca "raised the worst-decile harvest from 15% to 36%": soa causal, usa a base errada e não usa a NASA (J média; C média) | **Reescrito:** "against today's corn + beans, an equal-thirds portfolio had a worst-year-in-ten of 0.36 of normal vs 0.26 (a ceiling)", com o número dos anos de luz NASA acesa | Project summary; M4 |
| 12 | Carteira contra a base errada; placebo do vizinho desconta o ganho (C média) | **Feito:** 0,26 → 0,36 contra a S0; parte própria da mandioca de +0,02 a +0,08; grau A só no descritivo, B na parte da mandioca | M4; 9.2 nº 8 |
| 13 | CLSM × GRACE e relógio lento: 70% em vez de 55% no ano fora; rótulo do resíduo errado; circularidade não medida (C média) | **Corrigido:** 55% no ano fora; o ρ +0,04 é do resíduo do CLSM; o GRACE acompanha os açudes (+0,57); memória IMERG e GRACE como pares; "assimila por construção; não medimos quanto" | M7; 4.2; 9.7 |
| 14 | "Within-year AUC ≤ 0.60 for every layer" é falso (C média) | Vira "~0,65 (L3 0,645; VIIRS 0,62–0,63); geografia 0,61" | 0; 5; 9.2 nº 10 |
| 15 | "With this ocean, about 5 in 10" usa o ONI 2,04 (C média) | Vira "at the strongest El Niño before this one, about 5 in 10 (range 2–8)... This year is beyond the record" | 0; M3; 6.3; slide 7 |
| 16 | O slide 3 mistura eras (0,80 de 28 quadras ao lado de 0,77 de 10); só há divisão por era em 2 portões (C média; E média) | **Curvas por era nos 5 portões calculadas** (fechamento, bloco A), incluindo o oceano (0,66 e 0,72). O slide 3 mostra a última década e as duas eras, nunca a agregada sozinha | M3; slide 3 |
| 17 | Nada do MVP existe; o `site-nasa/` é um globo sem dados do QUADRA (E alta) | **O `site-nasa/` foi abandonado.** A página é escrita do zero e contada como construção nova (6 h) | 3.2; 10 |
| 18 | O orçamento não fecha para 1 pessoa (E alta) | **Plano de 1 pessoa com ~19 h** contra 29 h úteis, com as figuras primeiro | 10 |
| 19 | O M2 não tem previsões salvas, e o bloco 0 gastaria horas num número que já saiu do slide (E alta) | **M2 fora da demo e do bloco 0** | M2; 10 |
| 20 | Dois valores para o "SMAP hoje" (0,121 e 0,116) (E média; C baixa) | O painel mostra Quixadá (0,087) e o posto; o 0,121 do CE só aparece copiado da folha, como "média das células" | 9.7; 3.2 |
| 21 | A seção 10 contradiz a si mesma (trajetórias de Tauá e Iguatu, 4 `simular()`, "nunca cortar" contra "1 cartão") (E média) | Trajetórias e `simular()` saíram; o ISNA final é estático; "nunca cortar" = 4 cartões de Quixadá | 10 |
| 22 | Números demais nos slides; o slide 6 lista bases que não aparecem nas telas (E média) | No máximo 3 números no corpo; slide 6 com "on screen" separado de "in our analysis (repo)" | 11.1 |

**Gravidade baixa, também resolvidos:**
- "Stanford" virou o nome dos autores (J).
- "Tradition is weak, not wrong" virou "São José rain says as much as all the rain-to-date, which is not much" (J).
- O micro-ondas ganhou a pegada (~40 km) e a "célula mediana"; o óptico ficou "parcialmente cego" (C).
- A diversidade saiu do slide 1, com o rótulo "composição, não diversidade" (C).
- "Reproduzido por 4 scripts" virou "recomputado em 4 scripts a partir dos mesmos dados"; "fed by IMERG" virou "forçado por chuva corrigida para o IMERG, segundo a equipe do L4_SM" (C).
- O painel "hoje" caiu de 6 para 4 itens (E).
- A auditoria virou `AUDIT.md`, e o verificador virou lista branca (E).
- O SMAP L3 consolidado foi usado já no fechamento, e o resultado não mudou (E).
- A publicação no GitHub Pages entrou na lista do José até sáb 18h, com o PDF e o MP4 como entrega independente (E).

**Onde não seguimos a banca, e por quê:**
- **Juiz: as 3 métricas de S0, S1 e S2 no replay, via ISNA.** Fizemos as da S0 e da S2 com o observado e não fizemos as da S1. O ISNA do milho da 1ª chuva não vê 1998 (96% com água contra 25% sem quebra no IBGE), então a cauda simulada da S1 sairia enviesada justo no ano que importa. No lugar dela, o contrafactual da metade guardada.
- **Juiz: a luz como "API do IMERG + SMAP".** O critério pré-declarado escolheu a chuva desde 1/fev: o API é o melhor em 30/abr, mas fraco em 19/mar na última década (0,61), e 19/mar é o portão de troca.
- **Juiz: 2021 sempre ao lado de 2016.** Para a luz nova, o pior alarme falso de São José é 2022 (142 municípios). O slide mostra 2022; o rodapé do vídeo cita 2021 e 2022.
- **Juiz: o número-uau em 30/abr.** Usamos 19/mar, porque é o dia em que ainda dá para trocar; o 30/abr entra como confirmação do SMAP.
- **Cético: "W2 E SMAP" só como confirmação.** Adotamos, como o vermelho. Mas a chuva sozinha não fica muda: é o amarelo (2,1 em 10, contra 0,9 no verde).
- **Engenheiro: "S1 = não medido".** Acrescentamos o contrafactual (grau C), porque custou minutos e muda a história ("duas secas, dois escudos").
- **Engenheiro: até 6 números por slide.** Ficamos com o limite do juiz (3 no corpo), mais 1 linha de recibo.

---

## Anexo A. Decisões em aberto para a equipe (exigem pessoa, não agente), em ordem de retorno

1. **Uma conversa com um técnico de ATER** (Ematerce, sindicato rural ou ONG da ASA) **ou com um agricultor, até sáb 18h**, com permissão para citar 1 frase e com 1 mudança feita por causa dela. Mostrar o cartão de Dona Francisca e a luz em quatro estados. Perguntar sobre Quixadá 2023–2024 (praga, relato ou área?). É a ação de maior retorno para o Impacto.
2. **Até sáb 18h, aprovar ou não o repositório e a página públicos** (voz pública). Sem OK, a entrega é PDF + MP4.
3. Tamanho da equipe (**atrasado**). Sem decisão, vale o plano de 1 pessoa (seção 10).
4. Ler o regulamento sobre trabalho anterior ao evento e o formato da declaração de uso de IA (atrasado).
5. **Garantia-Safra e ZARC (atualizado na v3):** o limiar (perda ≥ 40%) e a área (máxima de 5 ha) foram conferidos na página do Planalto pela ferramenta web em 14/11; o José abre a página antes de qualquer slide. Faltam a cesta de culturas e a regra para quem planta fora do ZARC. A janela oficial de Quixadá está em disco (Tábua de Risco 2026/27); falta conferir na portaria as duas datas (zoneado a 40% desde 21/jan; 20% desde 11/fev) e decidir como o cartão fala disso.
6. Publicar ou não o hash da regra de 2027 (sha256 `41b7c820fe6693dd1ac2336075585a36fc6ec03fd9e1133c4537d8cf984fdb41`) e a leitura VIIRS da safra de 2026.
7. Nome final: QUADRA (recomendado) ou a reserva Field Replay.
8. Gravar ou não 45 s de voz humana em português para o cartão (até sáb 18h).
9. Confirmar se fatos do "Encontro dos Profetas da Chuva" de Quixadá podem ser citados.
10. **Novo na v3: copiar para `artigos/` os PDFs de da Luz 2023 e Souza 2024** antes que o scratchpad apague (~1,5 dia; caminhos em `pesquisa/viabilidade_artigos_nordeste.md`, 4.4, item 12). A tarefa dos agentes não autorizava mexer em `artigos/`.
11. **Novo na v3: o tamanho de cada faixa do plano da família (6.4)** e o solo do baixio, a confirmar com o técnico de ATER na conversa do item 1.

---

## Project summary (English)

QUADRA (the sertão's word for the rainy season) lets farmers and extension agents stress-test rotation plans against NASA's record before committing. Kluger, Di Tommaso and Lobell (ERL 2025) showed with satellites and causal machine learning that rotation benefits change with climate, but only in temperate breadbaskets and without water data. QUADRA takes the question to the semi-arid tropics, where a rotation is a policy with checkpoints and what decides is when the water shows up.

QUADRA places the checkpoints where three measured curves cross: what the data already know (validated by leaving whole years out, and always shown for 1998–2015 and 2016–2025 separately), what is still possible (Brazil's official ZARC planting windows, checked against an FAO-56 water balance driven by IMERG and NASA POWER that works anywhere), and when satellites can see (optical sensors go partly blind at decision time; SMAP's radiometer sees through clouds). The key finding is about how to read NASA water data. Counting IMERG rain from January 1 worked until 2015 and failed in the last decade, because wet Januaries hid dry seasons. The same IMERG rain counted from February 1 holds up in both periods. On March 19, 2016, the last day to switch crops and the closest analog to today's record El Niño, rain counted from January flagged 7 of Ceará's 182 counties; counted from February, all 182; 7 in 10 counties then lost their corn. NASA's SMAP soil moisture is the second mission that confirms. When both agreed on March 19, 5 in 10 counties lost their corn; with rain alone, 2 in 10; with neither, 1 in 10. In 2022, rain flagged 142 counties and SMAP none, and only 3 failed. The light is regional: it tells the year, not the county, and the screen says so. The 2027 rule is frozen with an internal hash; it was chosen after seeing the data, with thresholds fixed beforehand.

For each county, QUADRA compares the current practice with three alternative three-year strategies over every season in the IMERG record. Observed yields from Brazil's IBGE act as referee, and where the record cannot measure a strategy, the card says so. Against today's corn and beans, an equal-thirds corn–beans–cassava portfolio, computed on county yields, had a worst-year-in-ten of 36% of normal versus 26% (a ceiling: part of it is averaging). In county-years when NASA's April light was on, it was 21% versus 13%. Staggered sowing protects against a 2016-type year (early-March cowpea had water in 7 of 10 counties), while cassava planted the year before protects against a 1998-type year (when not even cowpea had water). Rotation numbers are used only when measured in the Brazilian semi-arid or in a matching aridity-and-temperature stratum, and each receipt shows how similar the study's climate is to the county's, measured with NASA POWER: the temperate breadbaskets get zero weight, no rotation-over-time trial comes from a sertão-like climate, and none of the measured rotation numbers the engine may use comes from a similar climate, so switching from today's corn–bean intercrop to rotation over time is marked "not measured". For the demo family, the strategies become one 2027–2029 plan in strips that switch places every year, with cassava as the dry-year buffer from 2028, early cowpea, forage sorghum, and a legume before corn only in a good year. Every number carries a receipt (NASA source, scale, validation, A–D grade), and an audit file shows where the tool fails, including the county where the soil light never hit. The engine is global; the demo map covers all 1,794 counties of Brazil's Northeast, with El Niño measured in each county and planting windows by soil, and the validation is in Ceará. NASA evidence. The farmer decides.

## Use of SI (AI) tools

Inside the product, SI appears in five places:
1. A physics-guided crop-water twin (FAO-56 water balance) whose soil-water state is calibrated against NASA SMAP L4 and validated by leaving whole years out.
2. Checkpoint alerts whose skill is measured without look-ahead and shown separately for 1998–2015 and 2016–2025. The main light (IMERG rain counted from February) was chosen by a declared criterion (the reading whose worst era-and-checkpoint score is highest) after seeing 2016–2025, with thresholds fixed before testing (75% from round 1; 20 in commit 48a3608). SMAP L4 confirms it as a second mission. The 2027 rule was frozen on 14/11/2026 with an internal hash, and an out-of-distribution warning flags this year's record El Niño.
3. An exact search over rotation strategies that ranks them by tail risk (CVaR) against current practice, with a neighbour placebo, a declared floor for years without cassava cuttings, and "no number" where the record cannot measure a strategy. Rotation effects from the literature enter as numbers only when measured in the Brazilian semi-arid or in a matching aridity-and-temperature stratum, and each receipt shows the study's climate weight, measured with NASA POWER.
4. A drift and data-quality sentinel that downgrades evidence automatically. It flagged Terra's documented orbit drift in land surface temperature, a post-2020 greening seen by two sensors, copied year-to-year yield reports, and SMAP's dry-season gaps and duplicated dates.
5. A large language model that only drafts the text on each card. It works offline from the engine's numbers, and a whitelist check blocks any number the engine did not produce.

We also report what did not work: causal machine learning on county statistics could not identify a rotation effect (a placebo test failed), November soil moisture does not predict the rainy season, and SMAP soil moisture alone adds about nothing over the best reading of IMERG rain.

To build QUADRA, the team used Anthropic's Claude (Claude Code) as a coding and analysis assistant. This included a council of AI agents that proposed, debated, re-analysed new NASA data and adversarially reviewed designs over two rounds. Every reported number comes from a script in the project repository that a person can rerun. No model was trained on LLM outputs, and no LLM is called at run time.
