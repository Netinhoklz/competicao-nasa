# Ata do conselho, rodada 2: dados novos, banca R2 e fechamento

- **Data:** sábado, 14/11/2026. Os horários vêm do `date` da máquina e dos carimbos dos arquivos `.saida.txt`.
- **Produto:** `proposta/PROPOSTA_FINAL_v2.md`, corrigida depois da banca da rodada 2 (1.398 linhas). A ata da rodada 1 continua em `proposta/ata_do_conselho.md`.
- **O que esta ata registra:** o que cada especialista reanalisou com os dados novos, as divergências e como foram resolvidas, as notas da banca nas duas rodadas e a folha de números canônicos com a receita de reprodução.

## 1. Cronologia

| Etapa | Quando | O que saiu |
|---|---|---|
| Reanálises dos especialistas com os dados novos (SMAP L4/L3, VIIRS, GLDAS-2.2 CLSM, GLDAS-2.1 Noah, IMERG recente) e com o artigo-âncora | 09:52–10:18 | 39 análises `conselho/analises/v2_<persona>_<tema>.py`, com 41 saídas `.saida.txt` (o índice de combustível do ecólogo tem três) |
| Arbitragem do arquiteto | 10:27 | `v2_arquiteto_arbitragem_smap.py` (9 divergências; regra da leitura menos favorável; corte por era) |
| Proposta v2 | 10:45 | `PROPOSTA_FINAL_v2.md` (1.285 linhas) |
| Banca adversária da rodada 2 | 10:51–11:03 | Engenheiro (`v2_engenheiro_viabilidade_mvp`, 10:51), juiz (`v2_juiz_numero_uau`, 10:52) e cético (`v2_cetico_r2b_gatilho_carteira`, 10:58; `v2_cetico_r2b_smap_contra_imerg_justo`, 11:03) |
| Fechamento do arquiteto | 11:07–11:38 | `v2_arquiteto_r2_fechamento.py` (rc 0; 36 s), a proposta corrigida e esta ata |

## 2. Reanálises de cada especialista

**Agrônomo** (`v2_agronomo_smap_portoes`, `_smap_contraprova`, `_smap_janelas`, `_diversidade_robustez`)
- O percentil do SMAP no dia da semeadura não separa a quebra (AUC 0,47). As regras R4, R5 e R8 estavam rotuladas "(SMAP)", mas eram um balde de solo nu.
- A contraprova fora da era SMAP (1998–2015), com o API do IMERG (τ = 13 d) no lugar do SMAP, pegou 71% das quebras em 19/mar contra 52%, com a mesma precisão.
- A troca do caupi: semeado em 11/mar/2016, teve água na floração em 70% dos municípios (SMAP) e 68% (balde); em 21/mar, 40% e 33%. A faixa de maniva vai de fevereiro a abril. Só com culturas de sequeiro, a diversidade dá +1,4 p.p. (p 0,51).

**Clima** (`v2_clima_estacao_seca_2026`, `_portao_novembro_2027`, `_smap_estado_inicial`)
- O modelo único de novembro (logística ONI ASO, ano fora) dá P(quebra) = 0,54 (IC90 0,24–0,75) no ONI 2,04, com BSS +0,063 (IC cruza zero). Em 2,46, o valor de 0,62 é extrapolação.
- A estação seca de 2026 é normal (5,7 mm; posto 13 de 29) e não prevê a quadra (ρ −0,22, n.s.). O SMAP de novembro também não prevê fevereiro (ρ +0,01). A zona da raiz do CE estava em 0,121 m³/m³ em 10/11, o 5º novembro mais seco de 12.

**Hidrólogo** (`v2_hidrologo_cinco_fontes_umidade`, `_smap_portoes_quebra`, `_calibra_m1_smap`, `_relogio_lento_gws`)
- Gerou o SMAP municipal diário deduplicado, que todos usaram. Cinco estimativas NASA da água na raiz diferem até 0,10 m³/m³ no nível.
- Em 30/abr/2016, o SMAP (média de 7 dias) pegou 64 das 127 quebras. O ISNA dentro do ano é geografia (0,613 contra 0,612).
- O balde calibrado pelo SMAP sobe de r 0,838 para 0,958 no ano fora, sem ganho de alerta (+0,004). A memória de chuva explica 70% do GWS (55% no ano fora), e o GRACE acompanha os açudes do Landsat (ρ +0,57).

**Sensoriamento remoto** (`v2_sr_fundacao_viirs_portoes`, `_smap_l3_l4`, `_escala_real`)
- O VIIRS continua o MODIS (r 0,986) e cobre a lacuna do Terra. Em jan–mar, só 39–40% dos pixels têm NDVI bom. O NDVI no portão não soma à chuva.
- O SMAP L3 e o L4 concordam em r 0,89 por célula. O SMAP diz "onde" só a partir de 36 km. A célula mediana é vista em 13–15 dias por mês.
- O NDVI concorda entre sensores a partir de 10–25 km. Quixadá 2023 teve vizinhos em quebra.

**Pesquisador de IA** (`v2_pesquisador_ia_smap_portoes`, `_smap_escore`, `_gldas_portoes_longo`, `_regra_estado`, `_precrop_dml`)
- Achou o artefato da AUC agregada de probabilidades LOYO com poucos anos (a climatologia sozinha dá 0,154). 2016 responde por 47% das quebras da década.
- O GLDAS não soma nada ao estado da chuva do IMERG. O SMAP soma só +0,02 a +0,03 sobre o API em São José. A floresta causal à maneira de Kluger no PAM falha no placebo (antecessor −0,056; placebo do sucessor −0,049).

**Ecólogo** (`v2_ecologo_calendario_fogo`, `_indice_combustivel`, `_ndvi_deslocamento_viirs`, `_painel_combustivel`, `_ponte_verde_pragas`)
- 72,9% dos focos caem em out–dez: o fogo segue o calendário da broca, e por isso o P5 virou portão de data fixa.
- O "+0,072" do combustível era tendência; sobre ela, sobra +0,020. A ponte verde de out/2026 está em 5,0% da lavoura (3ª maior de 15), sem efeito no milho seguinte (+0,001 por dp). O deslocamento do NDVI aparece também no VIIRS.

**Economista** (`v2_economista_diversidade_carteira`, `_gatilho_smap`, `_janela_alerta`, `_smap_calibracao`)
- De 30% a 60% do "+6,6 p.p." é composição. A carteira real entrega ~65% do ganho por cultura (+0,067). O piso sem maniva é de 0,321.
- Declarou as janelas de alerta (entre elas, 1/fev → portão) e mostrou que janeiro foi 34% da chuva de jan–mai em 2016. O "1% do SMAP" do gatilho veio da média sazonal de percentis; o cético mostrou na banca que isso é artefato.

**Designer** (`v2_designer_banco_lento`, `_termometro_solo`, `_verde_viirs`)
- Desenhou o termômetro do solo em 4 estados, com o "dormindo" de agosto a meados de janeiro. Só 13,2% dos município-dias ficam abaixo de p20, e a climatologia do percentil não foi conferida.
- O VIIRS de abr–mai abaixo de 90% do normal marca 7,5 quebras em 10 (AUC 0,79): é a testemunha de junho. O banco lento esquece em ~8 meses.

**Estrategista** (`v2_estrategista_diversidade_reproducao`, `_painel_hoje`, `_smap_portoes`, `_viirs_quixada`)
- Reproduziu o +6,6 p.p. (1998: +10,5; placebo 0,0), que cai para +2,6 controlando a fração milho + feijão. No SMAP, leu 90 de 127 em 30/abr/2016, na leitura do dia.
- Painel "hoje": GRACE p57, CLSM p74, caatinga com z +1,07. Em Quixadá, o NDVI de 2025 ficou em 0,93 do normal (seca de fim de quadra), e o de 2026 em 1,031.

**Cético, como especialista** (`v2_cetico_smap_portoes`, `_smap_l3_obs_vs_modelo`, `_clsm_grace_viirs`, `_diversidade_composicao`)
- O L3 do radiômetro dá o mesmo que o L4 em 30/abr (0,774), e a chuva dos últimos 15 dias também (0,80): o ganho é do estado da água.
- O CLSM × GRACE é em parte circular (GWS 0,85 contra 0,65 do Noah). A diversidade é quase aritmética: melão, soja e sorgo tecnificados ficaram em ~1,03–1,08 na seca.

**Arquiteto-chefe** (`v2_arquiteto_arbitragem_smap`, `v2_arquiteto_r2_fechamento`)
- A arbitragem fixou a leitura menos favorável e o corte por era, que revelou a falha da soma desde 1/jan em 2016–2025 (0,83 → 0,66).
- O fechamento (blocos A–I) calculou as curvas por era nos 5 portões (o oceano dá 0,66 e 0,72), aplicou o critério pré-declarado da luz de 2027 (venceu a chuva desde 1/fev, com 0,709) e congelou a regra com sha256.
- Também mediu o nível do ano em 2016, 2021, 2022 e 2025, o placar de Quixadá, o contrafactual do caupi em 1998 (1 em 10 municípios), a carteira nos anos de luz NASA (0,13 → 0,21), a S0 de Quixadá e o L3 consolidado (sem mudança).

**Banca da rodada 2**
- **Juiz** (`v2_juiz_numero_uau`): reproduziu o número-uau a partir do `.nc` cru, com agregação municipal própria (9, 64 e 90 de 127). Mostrou que, dentro de 2016, as 91 luzes do SMAP acertaram o mesmo que o acaso (64 contra 63,5; AUC 0,525).
- **Cético** (`v2_cetico_r2b_*`): comparou o SMAP com 5 leituras da chuva IMERG (a desde 1/fev pegou 113 das 127 quebras em 30/abr/2016). Mostrou que o "1%" é artefato e rodou o placebo do vizinho na carteira (0,335).
- **Engenheiro** (`v2_engenheiro_viabilidade_mvp`): montou o exportador em 0,4 s e mediu 29 h úteis contra 32–34 h de tarefas. Contou 83 números nos 7 slides e 85 palavras no vídeo. Viu que nada do MVP existia às 10:53.

## 3. Divergências e como foram resolvidas

A tabela completa, com o que foi conferido, está na seção R2.2 da proposta.

| # | Divergência | Resolução |
|---|---|---|
| 1 | SMAP em 19/mar: 0,68 (7 dias) × 0,59 (dia) | As duas estão certas. Sem 2016, as duas ficam abaixo de 0,5. O SMAP não decide em São José; vale o 0,59 quando ele aparece sozinho |
| 2 | 2016 em 30/abr: 90 × 64 de 127 | O produto lê a média de 7 dias. No slide, o SMAP aparece no nível do ano (metade do estado) |
| 3 | Limiar 25 × 20 | 20, que está no commit `48a3608` antes dos testes |
| 4 | Memória do solo: 13 × 46–58 dias | Medem coisas diferentes; nenhum número vai ao pitch |
| 5 | +6,6 p.p.: robusto × frágil | Composição, não diversidade; vai para o slide de honestidade |
| 6 | Deslocamento do NDVI: VIIRS × MODIS | Visto pelos dois sensores; causa aberta |
| 7 | Placar de Quixadá | SMAP com 0 acerto. Chuva desde 1/fev: 3 de 9 em 19/mar e 5 de 9 em 30/abr |
| 8 | Janeiro de 2016: 205% × 216% | "Cerca do dobro do normal" |
| 9 | VIIRS: AUC 0,79–0,81 × dentro do ano 0,60–0,63 | Testemunha do ano, não ordem local |
| 10 | **Luz principal de 2027:** v2 (soma desde 1/jan OU SMAP) × juiz (API + SMAP) × cético (chuva desde 1/fev; SMAP confirma) | Critério pré-declarado no fechamento: maior AUC mínima entre {19/mar, 30/abr} × {1998–2015, 2016–2025}. Venceu a chuva desde 1/fev (0,709), à frente dos últimos 30 dias (0,672), do API (0,607), dos últimos 15 dias (0,576) e da soma desde 1/jan (0,547). O SMAP vira a segunda missão (vermelho/amarelo). Ressalva: as AUCs já tinham sido vistas, e no nível do ano, em São José, a última década não se ordena bem |
| 11 | "1% do SMAP" × "64 de 127" | Artefato da média sazonal de percentis. Sai do slide 6 |
| 12 | Métricas da S1: juiz (calcular, grau C) × engenheiro ("não medido") | Contrafactual da metade guardada nos três El Niños fortes. As 3 métricas da S1 ficam "sem número", porque o balde não vê 1998 |
| 13 | Números por slide: 3 (juiz) × 6 (engenheiro) | 3 no corpo, mais 1 linha de recibo |
| 14 | S0 no cartão: estado × município | Município, com o rótulo "seu município". A S2 fica com o estado |
| 15 | Portão do número-uau: 30/abr (juiz) × leituras alternativas (cético) | 19/mar, o último dia de troca. O 30/abr entra como confirmação do SMAP |

## 4. Notas da banca adversária (1 a 5)

| Revisor | Rodada | Impacto | Criatividade | Validade | Relevância NASA | Apresentação | Média |
|---|---|---|---|---|---|---|---|
| Juiz da NASA Space Apps | R1 (rascunho v1) | 3,5 | 4 | 3,5 | 4 | 3 | 3,6 |
| Juiz da NASA Space Apps | R2 (v2) | 3,5 | 4 | 3,5 | 4,5 | 3 | 3,7 |
| Cético científico | R1 | 4 | 4 | 2,5 | 3,5 | 3 | 3,4 |
| Cético científico | R2 | 4 | 4 | 3 | 4 | 3 | 3,6 |
| Engenheiro de viabilidade | R1 | 4 | 4 | 3 | 4 | 3 | 3,6 |
| Engenheiro de viabilidade | R2 | 3,5 | 4 | 4 | 4 | 2,5 | 3,6 |
| **Média dos três** | R1 | 3,83 | 4,00 | 3,00 | 3,83 | 3,00 | 3,53 |
| **Média dos três** | R2 | 3,67 | 4,00 | 3,50 | 4,17 | 2,83 | 3,63 |

**Veredito comum da R2:** a v2 é mais honesta que a v1 e ganhou em Relevância (o SMAP saiu do roteiro e foi para o núcleo) e em Validade (o corte por era, a leitura menos favorável, a linha de base só de geografia). Mas três pontos derrubariam a demo diante de um juiz atento:
- o número-uau media volume de alarme, contra a pior leitura da chuva;
- o vídeo se contradizia e não cabia em 30 s;
- o MVP não existia e o plano não cabia para 1 pessoa.

Os três foram consertados na versão corrigida (seção 13.2 da proposta). As notas acima são da v2 antes do conserto; a banca não reavaliou a versão corrigida.

## 5. Números canônicos e receita de reprodução

**Comando padrão** (rodar da pasta `conselho/analises/`, com `MPLBACKEND=Agg`): `E:/campeonato-nasa/venv/Scripts/python.exe -I "<script>.py"`. Os scripts só leem arquivos e gravam apenas o próprio `.saida.txt`.

**Dependências do fechamento** (`v2_arquiteto_r2_fechamento.py`, 36 s):
- `saidas/v2_hidrologo_smap_pctl_mun_diario.parquet` (gerado por `v2_hidrologo_cinco_fontes_umidade.py`);
- `estrategista_cache_chuva_mun_diaria.parquet` e `saidas/chuva_mun_diaria.parquet` (idênticos de 1998-01-01 a 2026-09-14);
- `saidas/agronomo_isna_mun_ano.parquet`;
- `E:/campeonato-nasa/dados/derivados/ibge_pam_mun_anual.parquet`;
- POWER ET0 (`E:/campeonato-nasa/dados/power/power_ce_diario_et0.nc`);
- SMAP L3 consolidado (`E:/campeonato-nasa/dados/smap/smap_l3_diario_ne.nc`);
- ONI (`E:/campeonato-nasa/dados/indices_clima/oni.ascii.txt`).

| # | Número canônico | Valor | Script | Onde ler na saída |
|---|---|---|---|---|
| 1 | 2016 no nível do ano, 19/mar | Chuva desde 1/jan com luz em 7 de 182 municípios; desde 1/fev em 182 de 182; 127 quebras (70%); SMAP em 56 | `v2_arquiteto_r2_fechamento.py` | Bloco C, [19/mar], linha "2016:" |
| 2 | 2016 no nível do ano, 30/abr | Desde 1/jan 14 (normal em 92%); desde 1/fev 164; SMAP 91 (metade) | idem | Bloco C, [30/abr], linha "2016:" |
| 3 | Alarme falso de 2022, 19/mar | Chuva desde 1/fev em 142; SMAP em 0; 3 quebras | idem | Bloco C, [19/mar], linha "2022:" |
| 4 | Alarme falso de 2021 | 19/mar: chuva desde 1/fev 76, SMAP 26; 30/abr: 97 e 81; 7 quebras | idem | Bloco C, linhas "2021:" |
| 5 | Duas missões (2016–2025) | 19/mar: vermelho 5,3 em 10 (118 município-anos, 5 anos), amarelo 2,1, verde 0,9. 30/abr: 4,1; 3,4; 0,8 | idem | Bloco C, "estados de duas missões" |
| 6 | Qual município? | AUC dentro de 2016: 0,61, 0,65 e 0,65 (19/mar); 0,53, 0,59 e 0,53 (30/abr), para desde 1/jan, desde 1/fev e SMAP | idem | Bloco C, "AUC dentro do ano" |
| 7 | Mesmo número de alarmes | Com a taxa da chuva desde 1/fev, a soma desde 1/jan pegaria 55 de 127 em 2016 e gastaria 142 alertas em 2021 (19/mar) | idem | Bloco C, "mesma taxa de alerta" |
| 8 | Curvas por era nos 5 portões | 19/mar: desde 1/jan 0,77/0,55; desde 1/fev 0,74/0,71; SMAP 0,68. 30/abr: 0,83/0,66; 0,82/0,76; SMAP 0,77. ONI 0,66/0,72 | idem | Bloco A, "AUC agrupada" |
| 9 | Nível do ano (Spearman) | 19/mar, 2016–2025: desde 1/fev +0,19; SMAP +0,32; desde 1/jan −0,30. 30/abr: +0,50; +0,63; +0,41; API +0,87 | idem | Bloco A, "Spearman entre anos" |
| 10 | Escolha da luz e hash | Mínimos: desde 1/fev 0,709; R30 0,672; API 0,607; R15 0,576; desde 1/jan 0,547. sha256 `41b7c820fe6693dd1ac2336075585a36fc6ec03fd9e1133c4537d8cf984fdb41` | idem | Bloco B |
| 11 | Quixadá | Desde 1/fev: 19/mar, 9 alertas e 3 acertos; 30/abr, 9 e 5 (2025 a 0,747). Desde 1/jan: 8/2 e 7/3 | idem | Bloco D |
| 12 | Contrafactual do caupi (grau C) | Caupi de 11/mar com água na floração: 1998 10%, 2016 68%, 2024 100%. Caupi de 21/mar: 15%, 33%, 72%. Sorgo de 11/mar: 1%, 10%. A conferência com o agrônomo bate (68/33/10) | idem | Bloco E |
| 13 | Carteira nos anos de luz NASA | Chuva desde 1/fev < 75% em 30/abr (n = 585, 17 anos): CVaR10 milho 0,049; S0 0,134; 1/3 0,206; ganho sobre a S0 com IC90 de +0,042 a +0,104 | idem | Bloco F |
| 14 | S0 de Quixadá | Milho + feijão: P(< 0,5) 0,214 (6 de 28 anos); pior ano em 10 0,164; mediana 1,052 | idem | Bloco G |
| 15 | SMAP L3 consolidado | 30/abr: 0,774 (n = 1.740); 19/mar: 0,637; 30/abr/2016 abaixo de 75% do normal em 173 de 174 municípios | idem | Bloco H |
| 16 | Vídeo | 70 palavras | idem | Bloco I |
| 17 | Regra antiga por era | 30/abr: AUC 0,831 / 0,662; com alerta, 5,9 / 1,1 em 10 quebram; sem alerta, 1,5 | `v2_arquiteto_arbitragem_smap.py` | Bloco E |
| 18 | SMAP de 30/abr/2016, do `.nc` cru | 64 de 127 com 91 luzes (7 dias); 90 de 127 (dia); 63,5 esperadas ao acaso; AUC dentro de 2016 0,525 | `v2_juiz_numero_uau.py` | Blocos A/B e E, [30/abr] |
| 19 | SMAP contra a melhor chuva | 30/abr: SMAP 0,772; desde 1/fev 0,759 (+0,013; IC90 −0,039 a +0,080); API 0,801; R15 0,805 | `v2_cetico_r2b_smap_contra_imerg_justo.py` | Bloco A |
| 20 | Carteira contra a S0 e placebo | 0,15 / 0,26 / 0,36 (n = 2.495); placebo do feijão do vizinho 0,335 (0,323–0,347) | `arquiteto_final_carteira_ic.py`; `v2_cetico_r2b_gatilho_carteira.py` | Tabela da carteira; bloco 3 |
| 21 | Piso e teto da carteira | Piso 0,321 (IC90 0,265–0,401); +0,067 por cultura (~65%) | `v2_economista_diversidade_carteira.py` | Blocos C e B |
| 22 | Artefato do "1%" | Média fev–abr de percentis: dp 14,7, p10 34, acende 0,7%, 0 de 127 | `v2_cetico_r2b_gatilho_carteira.py` | Bloco 1 |
| 23 | Risco de 2027 | P(ONI 2,04) = 0,54 (IC90 0,24–0,75); em 2,46, 0,62 por extrapolação; BSS +0,063 | `v2_clima_portao_novembro_2027.py` | Blocos A–C, E |
| 24 | ONI de hoje | ASO/2026 = +2,46 | arquivo `oni.ascii.txt` | Última linha |
| 25 | SMAP hoje | CE 0,121 m³/m³ (média das células); Quixadá 0,087; 5º de 12 novembros | `v2_clima_smap_estado_inicial.py`; `v2_engenheiro_viabilidade_mvp.py` | Saída inteira; bloco C |
| 26 | Painel "hoje" | GRACE p57 (jul–set); caatinga out/2026 z +1,07, 3º de 15 | `cetico_r3_refutacoes.py` (E); `v2_engenheiro_viabilidade_mvp.py` (C) | — |
| 27 | Relógio lento | R² da memória de chuva 0,70 (0,55 no ano fora); GRACE × açudes ρ +0,57 | `v2_hidrologo_relogio_lento_gws.py` | Blocos 1 e 3 |
| 28 | Visibilidade | VIIRS 39–40% de pixels bons em jan–mar; SMAP, célula mediana 13–15 dias por mês | `v2_sr_fundacao_viirs_portoes.py` (A); `v2_sr_fundacao_smap_l3_l4.py` (A) | — |
| 29 | Opções | Milho 93% → 42% → 0%; caupi 98% em 19/mar | `arquiteto_final_curvas_quixada.py` | Bloco B |
| 30 | Validação aleatória | R² 0,49 contra −0,08 | `cetico_escala_vazamento.py` | — |
| 31 | Milho × feijão | ρ 0,78 (0,67 sem o choque do ano) | `arquiteto_numeros_canonicos.py`; `cetico_r3_refutacoes.py` (F) | — |
| 32 | Diversidade | +6,6 p.p. no total; só sequeiro +1,4 (p 0,51) | `v2_agronomo_diversidade_robustez.py` | V0 e V6 |
| 33 | Limiar 20 antes dos testes | "abaixo de 20 = seca agrícola" na seção 05 | `git show 48a3608 -- notebooks/secoes/05_earthdata_dados.py` | Commit de 14/11, 08:34:37 |

## 6. O que continua em aberto

**Com pessoa (José), em ordem de retorno:**
1. Conversa com 1 técnico de ATER até sáb 18h.
2. OK para o repositório e a página públicos até sáb 18h.
3. Tamanho da equipe (atrasado; vale o plano de 1 pessoa).
4. Regulamento.
5. Garantia-Safra e ZARC.
6. Hash público.

**Riscos remanescentes (o arquiteto, depois do fechamento):**
1. **No nível do ano, em São José, na última década, nenhuma leitura ordena bem os anos** (chuva desde 1/fev ρ +0,19; SMAP +0,32; n = 10). E a luz principal foi escolhida depois de ver as AUCs. O número-uau de 2016 é real, mas é um ano; 2022 e 2021 têm de aparecer sempre ao lado.
2. **Impacto sem usuário real**, e a S1 e a S3 sem métrica de pior ano. A rotação "no sentido estrito" continua sem evidência local, e o número da carteira é em parte média de ruído (placebo do vizinho).
3. **Execução:** às 11:38 de sábado, nenhuma tela, figura ou exportador existe; o plano de 1 pessoa pede ~19 h contra ~29 h úteis.
