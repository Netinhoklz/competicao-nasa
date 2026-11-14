# QUADRA: proposta final v2 (NASA Space Apps 2026, desafio "Field Shift")

- **Versão:** v2, sábado 14/11/2026, a partir das 10:30 (hora local, pelo `date`). Prazo de submissão: domingo 15/11/2026, 23:59.
- **De onde vem:** a `PROPOSTA_FINAL.md` (rodada 1), refeita com as 10 reanálises da rodada 2, que usaram os dados novos já em disco (SMAP L4 diário, SMAP L3, VIIRS VNP13A3, GLDAS-2.2 CLSM diário, GLDAS-2.1 Noah, NLDAS-2, IMERG V07 Late/Early recente) e o artigo-âncora Kluger, Di Tommaso & Lobell (2025).
- **Arbitragem do arquiteto (nova):** `conselho/analises/v2_arquiteto_arbitragem_smap.py` → `.saida.txt`. Resolve as divergências entre especialistas sobre o SMAP nos portões (seção R2.2).
- **Regra de honestidade (mantida):** todo número tem arquivo de origem. Os scripts da rodada 2 ficam em `conselho/analises/v2_<persona>_<tema>.py`, cada um com seu `.saida.txt`. As referências vêm da revisão `pesquisa/artigos_e_datasets.md` ou de `pesquisa/artigo_ancora_objetivo.md` (Crossref conferido em 14/11/2026); as que estão fora das duas têm a marca "fora da revisão".
- **Regra nova, fixada antes da arbitragem:** quando duas leituras igualmente razoáveis do mesmo dado dão números diferentes, **o slide usa a menos favorável** e o recibo mostra a outra.

---

## R2. O que mudou na rodada 2

### R2.1 Em quatro frases

1. A regra de alerta da rodada 1 (chuva IMERG desde 1/jan < 75% do normal) **funcionou em 1998–2015 e falhou em 2016–2025**. Janeiros chuvosos (2016 e 2025) encheram a soma, e a quadra fraca passou sem alerta.
2. O **estado da água no solo** viu esses anos em 30 de abril. Em 2016, a regra de chuva acendeu em 9 dos 127 municípios que perderam o milho; o SMAP L4 acendeu em 64 (90 lendo só o dia). O SMAP sai de "pipeline pronto" e entra no núcleo como **segunda luz** dos portões, com grau B e o alarme falso de 2021 ao lado.
3. O que os dados novos **não** fazem também é resultado: o SMAP não ajuda em novembro (o percentil nem existe de agosto a janeiro no sertão), não decide em 19 de março, não ordena municípios dentro do ano e não explica as quebras de Quixadá em 2023–2024.
4. O "+6,6 p.p. da diversidade" **sai do pitch como bônus de diversidade**. A associação existe nas secas, mas é sobretudo composição (menos milho e feijão) e culturas fora do sequeiro; só com sequeiro, cai para +1,4 p.p. (não significativo). Isso conversa com o artigo-âncora, que também acha pouco ganho em diversificar além de uma rotação simples.

### R2.2 Arbitragem das divergências entre especialistas

Conferi cada divergência nos scripts e, quando foi preciso, nos dados (`v2_arquiteto_arbitragem_smap.saida.txt`, blocos A–F). Nada foi escolhido olhando qual opção favorece o QUADRA.

| # | Divergência | Quem diz o quê | O que conferi | Decisão |
|---|---|---|---|---|
| 1 | AUC do SMAP em 19/mar (milho, 2016–2025) | 0,68: pesquisador de IA, SR, designer e hidrólogo. 0,59: estrategista, cético e agrônomo | Os dois estão certos. A diferença é só a leitura: média dos 7 dias até o portão (0,682, IC90 0,45–0,81) contra o valor do dia (0,593, IC90 0,39–0,71). Contra a chuva (0,547): +0,135 (IC90 por ano −0,014 a +0,223) e +0,046 (−0,054 a +0,109). Sem 2016, 0,495 e 0,444, os dois abaixo do acaso | **19/mar não tem ganho robusto do SMAP.** O deck usa 0,59 (menos favorável) e diz "o solo começa a falar em março e fala alto em abril" |
| 2 | Quebras de 2016 pegas pelo SMAP < 20 em 30/abr | 90 de 127: estrategista e cético (dia). 64 de 127: hidrólogo (média de 7 dias) | Confirmado: 90 (dia) e 64 (7 dias). A AUC é a mesma nas duas (0,772); só a contagem no limiar muda. Diferença contra a chuva: +0,110 com IC90 por ano de −0,023 a +0,171 (dia) e de +0,002 a +0,165 (7 dias) | **O produto lê a média de 7 dias**, que é a do termômetro do designer e é robusta a um dia faltando. **O slide usa 64**; o recibo mostra 90 |
| 3 | Limiar do alerta SMAP | < 25: agrônomo. < 20: seção 05 do notebook, hidrólogo, estrategista, cético e designer | Com < 25 (dia), 2016 dá 114 de 127. O < 20 foi o primeiro escrito (seção 05) | **< 20.** O 25 fica só como sensibilidade na auditoria |
| 4 | Memória da zona da raiz | τ = 13 dias: agrônomo. 46–58 dias: hidrólogo | As duas contas estão certas e medem coisas diferentes. O agrônomo correlaciona dentro de cada ano, o que tira a anomalia média do ano: é a memória intrassazonal. O hidrólogo agrupa entre anos. Na minha conta agrupada: 46 dias na média do CE (ano inteiro), 73 dias só com pares de fev–jun; mediana municipal de 38 e 67 dias | **Nenhum "o solo esquece em X dias" vai ao pitch.** O τ = 13 d continua só como o parâmetro pré-declarado do teste do agrônomo (API) |
| 5 | O "+6,6 p.p." da diversidade | Robusto: estrategista (1998: +10,5; placebo 0,0), agrônomo (controle GLDAS +6,2). Frágil: agrônomo (só sequeiro +1,4; sem séries repetidas +4,1), cético e economista (composição) | "Séries repetidas" tem duas definições: o agrônomo tira a série inteira se houver um ano repetido (37% das séries); o cético conta pares planos (2,1% dos pares). As duas contas estão certas | **A associação é real nas secas, mas não sustenta "diversificar o sequeiro".** Sai do pitch como bônus; entra como linha de honestidade (seção 8.2) |
| 6 | Deslocamento do NDVI desde 2020 | SR: ~3/4 aparece também no VIIRS, não é deriva do Terra. Cético: ~0,013 é próprio do MODIS e o resto depende do produto de chuva | Com a chuva IMERG, VIIRS +0,033 a +0,042 e MODIS +0,047 a +0,053, conforme a janela e o especialista; com a chuva POWER, VIIRS +0,019 (p 0,23) | **Os dois têm razão.** Rótulo: "visto pelos dois sensores com a chuva IMERG; ~0,01 é do MODIS; causa aberta, inclusive o produto de chuva" |
| 7 | Placar de Quixadá com o SMAP | Agrônomo (< 25, dia): 3 alertas e 2 acertos em 30/abr | Com o limiar canônico (< 20): no dia, nenhum alerta (2016 = p20,1; 2025 = p20,3); na média de 7 dias, 1 alerta em 2021, sem quebra | **O placar de Quixadá mostra 0 acerto da luz SMAP.** Os dois anos secos têm os dois menores valores do dia, por décimos acima do limiar. Não mexemos no limiar |
| 8 | Chuva de janeiro de 2016 | 205% do normal no estado (`designer_caso_2016.py`); 216% no município mediano (IA) | Agregações diferentes | **"Cerca do dobro do normal"** |
| 9 | VIIRS NDVI no fim de safra | AUC 0,79 (abr–mai, designer) e 0,81 (mar–mai, estrategista); dentro do ano 0,62–0,63; SR: 0,60 (VIIRS) e 0,62 (MODIS) dentro do ano | Janelas diferentes. A geografia sozinha dá 0,61 dentro do ano no milho (hidrólogo) | **Testemunha do ano, não ordem local:** "AUC ≈ 0,8; dentro do ano ≈ 0,6, igual à geografia" |

### R2.3 Componente → mudança → evidência → arquivo

| Componente | Mudança | Evidência (número conferido) | Arquivo |
|---|---|---|---|
| M3, regra canônica de alerta | **Mantida** para os números históricos, mas sempre mostrada **por era** | 30/abr: 1998–2015, com alerta 5,9 em 10 quebram, sem alerta 1,5 (recall 56%); 2016–2025, 1,1 contra 1,5 (recall 6%; AUC 0,83 → 0,66) | `v2_arquiteto_arbitragem_smap.saida.txt`, E |
| M3, segunda luz nos portões P3 e P4 | **Novo:** percentil da zona da raiz do SMAP L4 < 20, média dos 7 dias até o portão | 30/abr, 2016–2025: AUC 0,77 contra 0,66 da chuva; com a luz, 4 em 10 quebram, sem ela 1 em 10; 2016: 64 de 127 (dia: 90) contra 9; 2025: 21 de 45 (dia: 30) contra 1; 2021: 81 alertas e 3 quebras | idem, A–D; `v2_estrategista_smap_portoes.saida.txt`; `v2_cetico_smap_portoes.saida.txt`; `v2_hidrologo_smap_portoes_quebra.saida.txt` |
| M3, "duas luzes" no replay de 28 quadras | **Novo:** antes de 2015, a segunda luz é o estado da chuva do próprio IMERG (API com τ = 13 d, < 75% do normal) | 1998–2015, anos que o SMAP não viu: em 19/mar, pega 71% das quebras contra 52%, com a mesma precisão (4,7 em 10); em 30/abr, 73% contra 56% (5,1 contra 5,9 em 10) | `v2_agronomo_smap_contraprova.saida.txt`, bloco (e) |
| SMAP L3 (observação do radiômetro) | **Checagem feita**: a observação mostra o mesmo sinal de 30/abr | 30/abr, 2016–2025: L3 0,77 (IC90 0,52–0,88), L4 0,77, chuva IMERG dos últimos 15 dias 0,80, chuva desde 1/jan 0,66 | `v2_cetico_smap_l3_obs_vs_modelo.saida.txt`, bloco C |
| Recibo do SMAP: independência | **Ressalva obrigatória:** o L4 é modelo forçado pela chuva corrigida para o IMERG e corrigido pelo radiômetro. O ganho é do **estado** da água, não exclusivo do satélite | SMAP × estado da chuva IMERG (API30): ρ entre anos de 0,93 a 0,98; o SMAP soma só +0,02 a +0,03 sobre o API em 19/mar (IC tocando zero) | `v2_pesquisador_ia_gldas_portoes_longo.saida.txt`; `v2_cetico_smap_l3_obs_vs_modelo.saida.txt` (fonte da forçante: Reichle et al., EGU23-1419) |
| P3, frase "em 19/mar o que decide é a água no solo" | **Retirada** | SMAP em 19/mar: 0,59 (dia), sem 2016 abaixo de 0,5 | `v2_arquiteto_arbitragem_smap.saida.txt`, A |
| P3/S1, troca em ano de luz acesa | **Corrigida:** num ano como 2016, a área guardada vai para o caupi até ~11/mar; 19/mar fica como último dia de sorgo ou forragem | Caupi semeado em 11/mar com água na floração em 70% (SMAP) e 68% (balde) dos municípios em 2016; em 21/mar, 40% e 33%. Em 2025: 64%/70% contra 52%/50%. n = 2 anos, grau C | `v2_agronomo_smap_janelas.saida.txt`, bloco F |
| P1, portão de novembro | **Fortalecido:** modelo único pré-registrado (logística ONI ASO, ano inteiro fora) no lugar do RPSS com n = 10 | P(quebra municipal \| ONI 2,04) = 0,54 (IC90 0,24–0,75), contra 0,215 num ano qualquer; BSS +0,063 (−0,07 a +0,18); análogos IMERG: 1998 0,75, 2016 0,70, 2024 0,08 | `v2_clima_portao_novembro_2027.saida.txt`, A–C, E |
| P1, painel "hoje": SMAP | **Corrigido:** o percentil do produto vem vazio de ~12/ago a ~12/jan no sertão; entra o percentil próprio, com o termômetro "dormindo" | Vazio em 100% do CE em out–dez; zona da raiz do CE em 0,121 m³/m³ em 10/11/2026, 5º novembro mais seco de 12; anomalia de novembro → fevereiro ρ +0,01 (SMAP, n = 11), +0,00 (Noah, n = 26) | `v2_clima_smap_estado_inicial.saida.txt`; `v2_estrategista_painel_hoje.saida.txt` |
| P1, IMERG da estação seca | **Só contexto**, em mm e posto, nunca em "% do normal" | 01/ago–13/nov/2026: 5,7 mm, 81% da mediana, posto 13 de 29; estação seca × quadra seguinte ρ −0,22 (n.s., n = 28) | `v2_clima_estacao_seca_2026.saida.txt` |
| P2, janeiro | **Fortalecido:** nem o solo sabe em janeiro | 31/jan, 2016–2025: AUC 0,27 (chuva) e 0,26 (SMAP), invertidas pelos janeiros úmidos de 2016 e 2025 | `v2_cetico_smap_portoes.saida.txt`; `v2_pesquisador_ia_smap_escore.saida.txt`, A |
| P2, "o que vigiar" | **Novo, só texto:** o Pacífico dificilmente esfria a tempo; o Atlântico é hipótese exploratória e não entra com probabilidade | 1 de 7 El Niños fortes chegou a FMA ≤ 0,5 (1988); sinal do TSA 2/2 na contraprova, chance de acaso 0,25 | `v2_clima_portao_novembro_2027.saida.txt`, F e G |
| M1, ISNA como "ordem local" | **Rebaixado** a "mapa de risco de base do município" | Dentro do ano (milho, 1999–2025): ISNA 0,613 contra 0,612 só com a geografia | `v2_hidrologo_smap_portoes_quebra.saida.txt` |
| M1, estado da água | **Novo:** balde calibrado contra o SMAP como estimador de estado (novembro, entressafra); sem ganho de alerta | r no ano fora: 0,838 → 0,958 (10 de 10 anos); fora da amostra (1998–2014), calibrado − chuva +0,004 (IC90 −0,049 a +0,065) | `v2_hidrologo_calibra_m1_smap.saida.txt` |
| M1, datas-limite | Caupi confirmado; milho e sorgo com incerteza maior que ±1 decêndio | SMAP e balde: caupi ±1 decêndio em 58%; milho +3 decêndios em 74% dos municípios. O balde ordena a quebra (ρ +0,30 em 2016–2025), o SMAP não (−0,13) | `v2_agronomo_smap_janelas.saida.txt`, B e C |
| M1, "não vê 1998" | **Corrigido:** o ponto cego é da formulação ISNA, não do balanço hídrico | Balde em percentil < 20 em 30/abr/1998: 135 de 135 quebras (chuva: 103). Grau C (o balde começa vazio em 1998) | `v2_hidrologo_calibra_m1_smap.saida.txt` |
| M2, "ordem local dobrada" (ρ 0,155 → 0,307) | **Suspenso do slide** até ser refeito contra uma linha de base só de geografia | O mesmo teste derrubou o ISNA (0,613 contra 0,612) | `v2_hidrologo_smap_portoes_quebra.saida.txt` |
| M2, NDVI | Troca MODIS → VIIRS; a variante "vizinhos de 50 km" sai | VIIRS × MODIS: r 0,986 no estado; VIIRS cobre jul–out/2025, quando o MODIS mensal tem 0% de pixels; vizinhos de 50 km piores em todos os portões (0,561 contra 0,630) | `v2_sr_fundacao_viirs_portoes.saida.txt`, A, C e D |
| Replay: verde do satélite como testemunha | **Novo:** primeira leitura da safra pela NASA, em junho | VIIRS NDVI abr–mai abaixo de 90% do normal: 7,5 em 10 quebraram (n = 309, 12 anos); AUC 0,79 | `v2_designer_verde_viirs.saida.txt`, A |
| M3, NDVI como gatilho de portão | **Nulo; fica fora** | NDVI disponível no portão: +0,015 (19/mar) e −0,008 (30/abr) sobre a chuva | `v2_sr_fundacao_viirs_portoes.saida.txt`, C |
| M4, carteira 1/3 | **Piso declarado** para o ano sem maniva | Se o terço sem mandioca vale zero: CVaR10 0,321 (IC90 0,265–0,401), contra 0,169 do milho, nos 91 municípios de mandioca | `v2_economista_diversidade_carteira.saida.txt`, C |
| M4, ganho por cultura | **Teto, não promessa** | Carteira real: +0,067 por cultura efetiva (IC90 +0,043 a +0,081), cerca de 65% do que a conta da M4 promete (+0,103) | idem, B |
| M4, recibo da cauda | **Corrigido:** "cinco a sete anos ruins desde 1998", não "três episódios" | Cauda da carteira real: 1998, 2012, 2016, 2015, 2010, 2001 e 2013 | idem, B |
| M4, regras R4, R5 e R8 | **Rótulo corrigido:** eram um balde de solo nu, não o SMAP. Passam a "balde, solo ≥ 30/45 mm" | Rótulos "(SMAP)" em `saidas/agronomo_regras_semeadura.txt`; percentil real do SMAP no dia da semeadura: AUC 0,47 | `v2_agronomo_smap_portoes.saida.txt`, P2 |
| S2, faixa de maniva | **Novo calendário (grau C):** a faixa nova vai de fevereiro a abril, nunca na 1ª chuva de janeiro | P(estabelecimento) 0,36 em 21/jan e ≥ 0,7 de 11/fev a 01/mai | `v2_agronomo_smap_janelas.saida.txt`, A e D |
| S2/S3, evidência de diversidade | **O +6,6 p.p. não sustenta "diversificar o sequeiro"** | Só sequeiro: +1,4 p.p. (p 0,51); sequeiro sem séries repetidas: −0,5 (p 0,85); controlando a fração milho + feijão: +2,6 (p 0,32); composição: 30–60% do efeito | `v2_agronomo_diversidade_robustez.saida.txt`; `v2_estrategista_diversidade_reproducao.saida.txt`; `v2_economista_diversidade_carteira.saida.txt`, A; `v2_cetico_diversidade_composicao.saida.txt` |
| S3, leguminosa que fica | **Enfraquecida:** opção de solo, fogo e erosão, não escudo do pior ano | Entressafra (ago–dez): W < 0,1 em 49% dos dias, 0 dia com W ≥ 0,5; Kluger et al. 2025: benefício maior com mais chuva e menor para leguminosa sob calor | `v2_agronomo_smap_janelas.saida.txt`, E; artigo-âncora |
| IA causal sobre rotação no PAM | **Não identificável:** o placebo falha | DML: efeito do feijão anterior −0,056 (IC90 −0,108 a −0,007); placebo do feijão futuro −0,049 (−0,089 a −0,009) | `v2_pesquisador_ia_precrop_dml.saida.txt` |
| P5 e M7, fogo | **P5 vira portão de prática com data fixa** (até o fim de agosto). O "+0,072" sai | Fogo × secagem do SMAP: 0,095 dia por dia (IC95 0,006–0,183); 27% dos focos até 30/set, 72,9% em out–dez; combustível sobre climatologia + tendência: +0,020 (IC90 +0,001 a +0,042), e a tendência sozinha vale +0,098 | `v2_ecologo_calendario_fogo.saida.txt`; `v2_ecologo_indice_combustivel_rz.saida.txt` |
| M7, relógio lento | **Roda na memória de chuva do IMERG**; GWS e GRACE ficam como checagem de segunda missão | 70% da variância do GWS é memória de chuva (R² 0,55 no ano fora); o resíduo do GRACE não acompanha os açudes do Landsat (ρ +0,04) | `v2_hidrologo_relogio_lento_gws.saida.txt` |
| M7, CLSM × GRACE | **Não é validação** (o CLSM assimila o GRACE) | Anomalia sem ciclo no CE: GWS do CLSM 0,85, TWS 0,81, Noah (que não assimila) 0,65 | `v2_cetico_clsm_grace_viirs.saida.txt`, A |
| Pragas | Mapa da "ponte verde" (grau C) para armadilhas; relógio térmico confirmado; nenhum efeito no rendimento | Ponte verde de out/2026 em 5,0% da lavoura (3ª maior de 15); ponte(t−1) → milho(t): +0,001 por dp (IC95 −0,036 a +0,037); 4,29–4,63 gerações da lagarta entre ago e meados de nov | `v2_ecologo_ponte_verde_pragas.saida.txt` |
| M6, sentinela | Bandeiras novas: 4 datas duplicadas no SMAP L4; percentil vazio na seca; NDVI pós-2020 reclassificado; VIIRS de nov/2026 provisório | Duplicatas em 2023-10-09, 2024-04-03, 2024-11-26 e 2025-05-22, com até 0,09 m³/m³ de diferença | `v2_sr_fundacao_smap_l3_l4.saida.txt`; `v2_ecologo_calendario_fogo.saida.txt` |
| Tabela 4.2 | "Resolução nativa" vira **escala útil medida** | NDVI concorda entre sensores a partir de 10–25 km na quadra (0,797 a 10 km; 0,854 a 25 km); SMAP diz ONDE a partir de 36 km; IMERG × SMAP L3 nunca chega a 0,8; o município mediano tem 25 km de lado | `v2_sr_fundacao_escala_real.saida.txt`; `v2_sr_fundacao_smap_l3_l4.saida.txt`, B |
| Selo de visibilidade | **Ganha a linha do micro-ondas** | VIIRS 1 km: só 39–40% dos pixels do CE com NDVI bom ou marginal no mês em jan–mar (95–96% em ago–out); SMAP: cada célula de 9 km vista em 13–15 dias por mês, o ano todo | `v2_sr_fundacao_viirs_portoes.saida.txt`, A; `v2_sr_fundacao_smap_l3_l4.saida.txt`, A |
| Gatilho tipo Garantia-Safra | **Novo componente de auditoria**, não de manchete | Percentil pronto do SMAP em fev–mai: disparou em 1% dos municípios em 2016, com 70% em perda; regra regional de chuva IMERG < 75% (três janelas pré-declaradas): 5 a 6 de 8 anos ruins desde 1998, com 1 a 2 alarmes falsos; risco de base de ~50% no município | `v2_economista_gatilho_smap.saida.txt`; `v2_economista_janela_alerta.saida.txt` |
| Replay | O segundo replay troca **2012 por 2016** (todas as missões) | Ver slide 4 | `v2_designer_termometro_solo.saida.txt` |
| Narrativa e base científica | **Kluger et al. 2025 entra como abertura** | Achados do resumo: diversificar além da rotação simples rende pouco; benefício maior com mais chuva; leguminosa rende menos sob calor | `pesquisa/artigo_ancora_objetivo.md`; `artigos/2025_Kluger_*.pdf` |
| Protocolo (9.1) | Regras novas: leitura menos favorável; resultados por era; sem AUC agregada de probabilidades LOYO com poucos anos | Com 10 anos, a climatologia LOYO sozinha dá AUC 0,154 no milho (artefato) | `v2_pesquisador_ia_smap_portoes.saida.txt` (superado; só o artefato) |
| Orçamento (seção 10) | **~44 h-pessoa** com contingência; o site Flask atual vira página estática | 2 pessoas dão ~51 h (folga de ~7 h); 1 pessoa, ~25,5 h | avaliação do cético (sem script) |

### R2.4 Os riscos que a banca deixou

| Risco da rodada 1 | Como ficou | Evidência |
|---|---|---|
| "SMAP pode não chegar" | **Resolvido.** O L4 diário (31/03/2015 → 10/11/2026) está em disco, sem dia faltando em 2016–2025; o L3 consolidado apareceu às 10:06 e os recortes diários já foram usados | `v2_agronomo_smap_portoes.saida.txt`; `v2_cetico_smap_l3_obs_vs_modelo.saida.txt` |
| Relevância NASA com SMAP e ECOSTRESS só como roteiro | **SMAP resolvido** (núcleo, com papel medido). ECOSTRESS continua roteiro | seção 4 |
| Números de vitrine que não se reproduzem | **Tratado:** o +6,6 sai do pitch como bônus; o +0,072 do fogo sai; o 0,307 do M2 fica suspenso; o 2016 do slide usa a leitura menos favorável; folha canônica refeita (9.7) | R2.2 e 9.7 |
| Validade local fraca (Quixadá: 8 alertas, 2 acertos) | **Continua.** A luz do SMAP não acerta nenhuma vez em Quixadá com o limiar canônico. O placar continua na tela | R2.2, item 7 |
| Quixadá 2023–25 sem explicação | **Reduzido.** 2025 foi água no fim da quadra (SMAP nos menores valores da década em 30/abr; VIIRS entre os mais secos do estado). 2023: a chuva parou em maio, depois do portão, e os vizinhos também quebraram. 2024: quebra isolada, sem assinatura hídrica nem de vegetação, com a área caindo de 5.000 para 2.800 ha. A causa de 2023–24 fica para conferir com a Ematerce | `v2_hidrologo_smap_portoes_quebra.saida.txt`; `v2_sr_fundacao_escala_real.saida.txt`, D; `v2_estrategista_viirs_quixada.saida.txt` |
| NOVO: a regra canônica falhou na última década | **Mostrado como erro explicado:** a soma desde 1/jan guarda o janeiro chuvoso; o solo não. A curva agregada nunca aparece sem as duas eras | R2.3, primeira linha |

---

## 0. Resumo executivo

- **O que é:** o QUADRA trata a rotação no semiárido como uma **política com cinco portões de decisão ao longo do ano**, e não como uma sequência fixa de culturas. Cada estratégia é planejada em **3 anos (2027–2029)**, incluindo o que fica no solo na entressafra.
- **A pergunta científica:** Kluger, Di Tommaso & Lobell (2025, ERL) mostraram, com satélite, mapas de culturas e florestas causais, que o benefício da rotação **muda com o clima**, mas só em quatro celeiros temperados e sem dados de água. O QUADRA leva a pergunta ao semiárido, onde o que decide é **quando** a água aparece, com os dados de água da NASA no centro.
- **Onde ficam os portões:** onde três curvas medidas se cruzam (seção 7, inovação 1): **habilidade** (o que os dados já sabem, medido deixando o ano inteiro de fora), **opções** (o que ainda dá para plantar) e **visibilidade** (quando o satélite enxerga; agora com a linha do micro-ondas).
- **A imagem central:** a chuva acumulada da NASA (IMERG) quase não diz nada em janeiro (AUC 0,57) e chega a 0,80 em 30/abr, nas 28 quadras de 1998–2025. O oceano, conhecido desde novembro, diz um pouco (0,67). Em 19 de março, o milho já não cabe em 58% dos municípios, mas o caupi ainda cabe em 98%.
- **O achado da rodada 2:** a soma da chuva desde 1/jan **falhou em 2016–2025** (AUC 0,66 em 30/abr; com alerta, 1,1 em 10 quebram, contra 1,5 sem alerta). O **estado da água no solo**, medido pelo SMAP L4, viu os anos que a soma perdeu: em 2016, o análogo de El Niño de 2027, a soma acendeu em 9 dos 127 municípios que perderam o milho, e o SMAP em 64. O portão passa a ter **duas luzes**: chuva desde janeiro **ou** água no solo baixa. Grau B: 10 quadras, uma grande seca, e um alarme falso grande em 2021.
- **Como compara:** a estratégia atual e três alternativas são **reencenadas nas 28 quadras do registro IMERG (eras TRMM e GPM, 1998–2025)** no município do agricultor. O ranking é pelo **pior ano**, não pela média.
- **Quem arbitra:** o rendimento observado do IBGE (PAM). A NASA é o motor; o IBGE é o juiz.
- **O recibo:** cada número traz a missão de origem, a escala, a validação e um grau de evidência de A a D.
- **A escala, dita sem exagero:** os dados acertam **o ano na região**. Entre municípios no mesmo ano, nenhuma camada NASA passa de AUC ~0,60 (IMERG, SMAP, GLDAS, VIIRS no portão), e a vantagem do ISNA é a geografia. Por isso a tela diz "seu município / sua região", e a decisão no roçado fecha com a família e o técnico.
- **A SI:** modelos pequenos, guiados pela física, validados por ano e comparados só com linhas de base pareadas. Um LLM **só redige** textos, offline, travado por um verificador de números.
- **Por que agora:** o Pacífico está no **El Niño mais forte já medido para ago–out** (ONI ASO/2026 = +2,46; o máximo anterior era 2,04, em 1997). Com o mar assim, o modelo deixando o ano de fora dá cerca de **5 em 10 municípios** com quebra do milho, contra 2 em 10 num ano qualquer (faixa honesta de 2 a 8). A demo é o plano de 2027 de uma família fictícia de Quixadá (CE).

---

## 1. Nome e frase de efeito

**Nome:** **QUADRA**. Na primeira menção do deck e do vídeo: *"QUADRA: the sertão's word for the rainy season"* (fevereiro a maio). Subtítulo: *Field Playbook*. Nome reserva: *Field Replay*.

**Por que não "PROFETA":** o próprio estrategista retirou o nome. Ele promete certeza, que é o que os dados negam, e arrisca soar como apropriação dos profetas da chuva. Eles entram no produto com respeito, no "Checkpoint São José".

**Frase de efeito (PT):**
> "Em janeiro, a chuva que já caiu não diz quase nada, e o oceano diz pouco. Em abril, a soma da chuva pode enganar, mas o solo não. O QUADRA reencena no seu município todas as quadras que a NASA registrou, mostra como cada rotação aguentaria o pior ano e marca os dias em que o dado já sabe o bastante e ainda dá tempo de mudar."

**Frase de efeito (EN, pitch):**
> "In January, rain-to-date says almost nothing and the ocean says a little. By April, rain-to-date can fool you; the soil does not. QUADRA replays every rainy season NASA has recorded over your county, ranks rotations by their worst year, and marks the checkpoints where the data know enough and there is still time to switch."

**Tagline (EN):** *Replay every rainy season NASA has recorded over your county. Decide at the right checkpoint.*

**Frase-ponte com o artigo-âncora (EN):** *"Stanford showed which rotation pays depends on climate. In the semi-arid, it depends on when the water shows up."*

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
   - Milho e feijão ocupam 91% da área (Rocha et al. 2021).
   - No registro do PAM, as duas culturas quebram juntas. A correlação mediana das anomalias no mesmo município é **0,78** (183 municípios, 1998–2025). Tirando o choque comum do estado no ano, ainda é 0,67 (`cetico_r3_refutacoes.saida.txt`, bloco F).
   - Ressalva: parte do co-movimento pode ser o mesmo relato municipal. Em Quixadá, o feijão de 2005 é cópia exata do de 2003.
3. **A quebra é frequente e sincronizada.**
   - **Definição canônica de quebra:** produção ÷ área plantada abaixo de 50% da mediana do próprio município nos *outros* anos.
   - O milho quebrou em **21,5%** dos 5.106 município-anos de 1998–2025.
   - Fração de municípios em quebra: 75% em 1998 e em 2012, 70% em 2016 e 61% em 2010. O rendimento estadual do milho caiu 69% em 2012 (`arquiteto_numeros_canonicos.txt`, bloco D).
   - Cerca de metade da variância da quebra municipal é choque comum ao estado no ano: 45–53% no milho (`cetico_escala_vazamento.py`).
4. **O El Niño pesa, mas não decide sozinho.**
   - Dos 6 El Niños desde 1998 (ONI de NDJ ≥ 1,0), **3 viraram catástrofe**: 1998, 2010 e 2016, com 61% a 75% dos municípios em quebra. **Três passaram sem quebra**: 2003, 2019 e 2024, com 1% a 8% (`cetico_r3_refutacoes.saida.txt`, bloco A).
   - **Novo, modelo único pré-registrado:** a logística P(quebra municipal) ~ ONI ASO do ano anterior, validada deixando o ano inteiro de fora, tem BSS de +0,063 no município (IC90 −0,07 a +0,18) e ρ de +0,39 com a fração de municípios em quebra (p = 0,038; n = 28). O sinal é real no nível do ano e pequeno (`v2_clima_portao_novembro_2027.saida.txt`, bloco B).
   - Os El Niños fortes foram "tudo ou nada": o modelo previu cerca de 0,5 para 1998, 2016 e 2024, e o observado foi 0,75, 0,70 e 0,08 (mesmo arquivo).
   - Com erro-padrão agrupado por ano, o efeito do El Niño "além da chuva" **não é significativo**: OR 1,57, IC95 0,71–3,50 (`cetico_memoria_grace_neff.saida.txt`, bloco A). Grau B.
5. **O solo fica nu e queima.**
   - 72,9% dos focos de fogo VIIRS de 2015–2025 caem em out–dez; até 30/set, só 27% (`v2_ecologo_calendario_fogo.saida.txt`).
   - 17% da área do Ceará está em células de ~375 m com ao menos um foco VIIRS em 2012–2025. Isso não é área queimada: um roçado de 1 ha acende uma célula de 14 ha.
   - A medida de área é o MapBiomas Fogo a 30 m: 12,7% da Caatinga queimou entre 1985 e 2023 (Franca Rocha et al. 2024).
6. **Em janeiro, a chuva que já caiu não diz quase nada, e em abril a soma pode enganar.**
   - A chuva IMERG acumulada até 31/jan separa a quebra do milho com AUC de apenas 0,57 (IC90 0,43–0,68). Em Quixadá, janeiro de 1998 teve 150% do normal e janeiro de 2016 teve 197%. Os dois anos foram de quebra.
   - O oceano diz um pouco: o ONI de ASO, publicado no início de novembro, tem AUC de 0,67 (IC90 0,53–0,78) para a quebra municipal (`arquiteto_final_curvas_quixada.saida.txt`, bloco A).
   - A habilidade da chuva cresce durante a quadra: 0,73 em 19/mar e 0,80 em 30/abr, em 1998–2025.
   - **Mas a soma desde 1/jan guarda o janeiro.** Em 1998–2015, a AUC de 30/abr é 0,83; em 2016–2025, cai para 0,66, e o alerta acende menos onde quebra do que onde não quebra (1,1 contra 1,5 em 10). Janeiro foi 34% da chuva de jan–mai em 2016 e 28% em 2025, contra a mediana de 12% (`v2_arquiteto_arbitragem_smap.saida.txt`, bloco E; `v2_economista_janela_alerta.saida.txt`).

### 2.2 Por que as ferramentas atuais não resolvem

- O **ZARC** dá a janela de plantio de uma cultura, mas a janela não muda com o ano.
- O **prognóstico de tercis** não vira decisão de rotação.
- **Painéis de NDVI** mostram o passado e não comparam estratégias. E o óptico fica cego justamente nos portões: só 39–40% dos pixels do Ceará têm NDVI VIIRS bom ou marginal no mês em jan–mar (`v2_sr_fundacao_viirs_portoes.saida.txt`, bloco A).
- O **percentil pronto de umidade do solo** do SMAP L4 não existe no sertão de agosto a meados de janeiro, e com corte fixo de 20 disparou em só 1% dos municípios em fev–mai de 2016 (`v2_economista_gatilho_smap.saida.txt`). Usar o dado da NASA "como vem" não basta: é preciso reancorá-lo no lugar e testá-lo contra o IBGE.
- Marengo et al. (2021) mostram que a adaptação à seca no Nordeste ainda é quase toda **pós-desastre**.
- Dury et al. (2012) mostram que o plano de cultivo real é dinâmico e adaptativo, mas os modelos o tratam como estático.
- No Ceará, previsões comunicadas como certeza já custaram a confiança dos agricultores (Lemos et al. 2002, fora da revisão; DOI conferido no Crossref na rodada 1).
- **A ciência de rotação com satélite** (Kluger et al. 2025; Zhou et al. 2024; Beal Cohen et al. 2019) estuda celeiros temperados com mapa de culturas por pixel e sem dados de água. O semiárido de sequeiro, sem mapa oficial de culturas, fica de fora.

### 2.3 Por que agora

- O **ONI ASO/2026 é +2,46**, o maior valor para ago–out desde 1950. Os anteriores foram 2,04 (1997) e 2,02 (2015). Não é o recorde absoluto: o maior ONI de qualquer trimestre foi 2,59, em NDJ 2015 (`arquiteto_numeros_canonicos.txt`, bloco A).
- **O ano de 2027 está fora da distribuição.** O 2,46 está 0,42 acima do máximo das quadras de 1982 a 2026 (2,04). No máximo já visto, P(quebra municipal) = 0,54 (IC90 0,24–0,75); em 2,46, 0,62 por extrapolação, e o valor muda de 0,53 a 0,72 conforme o análogo retirado (`v2_clima_portao_novembro_2027.saida.txt`, blocos B e E).
- **O Pacífico dificilmente esfria a tempo:** só 1 dos 7 El Niños fortes desde 1951 chegou a FMA ≤ 0,5 (1988; IC90 0,01–0,52) (mesmo arquivo, bloco F).
- **O estado de hoje é normal e não prevê a quadra:**
  - banco regional de água normal: GRACE do Ceará na média de jul–set/2026 no percentil 57 (`cetico_r3_refutacoes.saida.txt`, bloco E); água subterrânea do GLDAS-2.2 CLSM em jun–ago/2026 no p74, com o aviso de que o CLSM assimila o GRACE (`v2_estrategista_painel_hoje.saida.txt`);
  - solo no piso, como todo novembro: zona da raiz do SMAP L4 no CE em 0,121 m³/m³ em 10/11/2026, o 5º mais seco de 12 novembros (`v2_clima_smap_estado_inicial.saida.txt`);
  - estação seca normal: 5,7 mm de 01/ago a 13/nov, 81% da mediana, posto 13 de 29 (`v2_clima_estacao_seca_2026.saida.txt`).
- **A quadra de 2026 foi boa** (698 mm, 120% da mediana, posto 22 de 29), e a caatinga de out/2026 está mais verde que em 12 de 14 outubros (VIIRS, z +1,07). Há combustível no chão (`v2_clima_estacao_seca_2026.saida.txt`; `v2_estrategista_painel_hoje.saida.txt`).

### 2.4 Por que importa no mundo

- O problema "uma janela de chuva, falso início e data-limite" é o mesmo no Sahel, no Chifre da África, na Índia de sequeiro e no semiárido do Texas. No Texas, o CDL mostra 67% de algodão contínuo (síntese 90.2, item 11).
- Na amostra global do POWER (2020), **40 dos 47 pontos terrestres tropicais amostrados** não têm nenhum mês em que o frio interrompa o ciclo da lagarta-do-cartucho, contra 7 meses em Iowa (`arquiteto_final_curvas_quixada.saida.txt`, bloco E). Onde não há inverno, só a rotação e a entressafra quebram o ciclo. No Ceará, o relógio térmico deu 4,3 a 4,6 gerações potenciais da lagarta entre 1/ago e 12/nov em todos os anos de 2012–2025 (`v2_ecologo_ponte_verde_pragas.saida.txt`, bloco 4).
- O núcleo de dados do QUADRA é global. O SMAP L4 cobre 99,6% da terra entre 60°S e 60°N na amostra de 15/04/2025 (`smap_global_amostra_2025-04-15.nc`; seção 05). Atenção: não sabemos se o percentil pronto também some na seca de outras terras áridas; a amostra global não tem percentil.

---

## 3. A solução: o que o técnico e a família veem e fazem

### 3.1 Dois usuários, um motor

- **Extensionista (técnico de ATER, cooperativa, ONG):** é o usuário principal do MVP. Usa um painel web estático que funciona offline depois de carregado. Escolhe o município da família, lê os portões, compara as estratégias e vê a evidência completa.
- **Família agricultora:** recebe do técnico um **cartão em imagem** com no máximo 3 números, em frequências naturais ("de cada 10 municípios, 4 perderam mais da metade do milho"), sempre com "na sua região" e o número de anos ao lado. A família informa a data de plantio e as prioridades, e pode vetar uma sugestão.
- O cartão com áudio e o envio pelo WhatsApp ficam no roteiro. No MVP, o cartão é uma imagem que o técnico mostra.

### 3.2 As telas do MVP (três) e o que fica para depois

1. **Relógio da Quadra** (tela principal).
   - Seletor de município (184, mapa GeoJSON sem mapa base, que funciona offline).
   - **As três curvas** sobre o calendário, de novembro a julho: habilidade (chuva IMERG por era, oceano e a segunda luz do SMAP), opções (datas-limite de milho, sorgo e caupi) e visibilidade (óptico e micro-ondas).
   - Os 5 portões e o de hoje destacado. Para cada portão:
     - o que o dado já sabe, em frequência natural e com o n;
     - o que ainda não sabe;
     - o que ainda dá para fazer;
     - o placar do alerta **neste município**, com acertos e erros, para cada luz.
   - **Faixa "Água agora" com o termômetro do solo** (SMAP L4, proposta do designer), com quatro estados: **dormindo** (cinza, de agosto a meados de janeiro, quando o produto não dá percentil), **verde** (p40 ou mais), **amarelo** (p20 a p39) e **vermelho** (abaixo de p20). A leitura é a média dos 7 dias até a data.
   - **Painel "hoje"** (14/nov/2026):
     - ONI (NOAA) com o aviso de caso inédito e a distribuição dos análogos (1998, 2016, 2024);
     - termômetro do solo DORMINDO, com o nível absoluto e o posto entre os novembros ("5º mais seco de 12; normal para a época");
     - estação seca do IMERG em mm e posto (5,7 mm; posto 13 de 29), com a frase "não prevê a quadra";
     - banco lento regional: GRACE p57 (jul–set), água subterrânea do CLSM p74 (jun–ago);
     - açudes do Sertão Central vistos pelo Landsat (p32 da série 1984–2025; uma AOI, grau C);
     - verde da caatinga em out/2026 (VIIRS, z +1,07): "mais combustível; não queimar".
2. **Cartões de estratégia.**
   - A atual (S0) e três alternativas (S1–S3), lado a lado, cada uma como **sequência 2027–2028–2029**, com a entressafra.
   - Cada cartão traz os 5 campos do desafio: por que foi sugerida, evidência com recibo, benefícios, lacunas e riscos a confirmar com o técnico.
   - Três métricas calculadas: chance de colher menos da metade, "pior ano em 10" e mediana. As demais prioridades (forragem, N, erosão, matéria orgânica, mercado) entram como etiquetas qualitativas com grau.
   - Os pesos da família reordenam os cartões.
3. **Replay.**
   - **1998** (o análogo de El Niño mais próximo de 2027, só com IMERG e IBGE, porque o SMAP e o VIIRS ainda não existiam) e **2016** (o análogo em que a soma da chuva enganou e o solo viu; todas as missões). O 2012 sai do MVP e fica na auditoria como "pego tarde".
   - A chuva IMERG do município anima dia a dia, as barras de ISNA por cultura sobem e descem (grau C) e as luzes acendem na data em que teriam acendido. Em 2016, entram o termômetro do SMAP e, em junho, o verde do VIIRS como testemunha.
   - Na colheita, o rendimento observado do IBGE é revelado ao lado da estimativa da NASA (grau A).
   - A S3 aparece hachurada: "sem dado local; faixa da literatura (B·T)".

**Fora das telas do MVP:**
- A **auditoria** vira uma página HTML estática gerada em Python e um slide. Ela inclui o gatilho tipo Garantia-Safra (seção 9.3), o placar das duas eras e a arbitragem R2.2.
- Ficam no roteiro: código de barras do talhão ao vivo, áudio, simulador de WhatsApp, modo global ao vivo e SMAP ao vivo. Do modo global, entram 2 a 3 pontos pré-calculados, com grau C.

### 3.3 Fluxo de uso ao longo do ano

| Quando | O técnico faz | A família recebe ou faz |
|---|---|---|
| Primeira visita | Escolhe o município. Confirma a prática atual (o PAM sugere; 1 pergunta confirma). Faz 4 a 6 **perguntas de troca** que viram os pesos. Registra rebanho, semente guardada, maniva, mão de obra e água guardada. | Cartão de apresentação: "o QUADRA não sabe tudo; aqui está o que ele sabe". |
| **P1, nov–dez** | Lê o oceano e o banco de água. O termômetro do solo está dormindo, e isso é dito. | Ações sem arrependimento: semente de caupi precoce e sorgo até dezembro, maniva guardada, palma, adesão ao Garantia-Safra, não queimar, aceiro. |
| **P2, jan–fev** | Lê a chuva recente; o termômetro acorda em meados de janeiro (~12/jan). Em 28/fev: "ainda é cedo". | "Plante uma parte agora e guarde a outra." A família informa a **data de plantio**. |
| **Início de março (só em ano de El Niño forte)** | Lê as duas luzes e o oceano. | Em ano como 2016, a área guardada vai para o caupi até ~11/mar, a menos que as duas luzes estejam verdes. |
| **P3, 19/mar ("Checkpoint São José")** | Lê as duas luzes: chuva desde 1/jan e termômetro do solo. | Se uma luz acender, a área guardada vai para sorgo ou forragem (até 11–21/mar); o caupi, até ~21/mar só em ano normal. |
| **P4, 30/abr** | Lê as duas luzes. É o portão em que o solo fala alto. | Ação graduada: guardar forragem, cortar o milho para os animais se o técnico confirmar, segurar a venda dos animais. |
| **Junho** | Lê o verde do satélite (VIIRS) como primeira leitura da safra. | "O IBGE confirma no ano que vem." |
| **P5, até 31/ago (data fixa)** | Mensagem de prática: o fogo segue o calendário da broca, não a secura do solo. Mapa da "ponte verde" para armadilhas. | Palhada em vez de fogo, fenação do excedente, aceiro, perene em nível. |
| Fim de safra | Registra o resultado. | A família ordena os caminhos que testou. Isso gera evidência local de rotação, que hoje não existe. |

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
- **"% do normal":** a chuva desde 1/jan dividida pela mediana dos outros anos no mesmo município. Na estação seca, a tela usa mm e posto, nunca "% do normal" (398% sobre 1 mm engana).
- **"Seu município / sua região":** "seu município" é onde o número foi medido; "sua região" é onde contamos quantas vezes ele acertou, ano a ano, porque a seca atinge a região inteira de uma vez.
- **Percentil.**
- **Grau de evidência A–D.**

### 3.5 Apoiar, não substituir

- Os pesos vêm da família.
- O técnico aprova toda mensagem.
- A família pode vetar ("não quero sorgo"); o app recalcula e mostra o custo da escolha.
- As datas-limite são de uma **janela sintética tipo-ZARC** feita com o IMERG; o cartão diz "confirmar no ZARC oficial com o técnico".
- Quando as duas luzes discordam (chuva baixa, solo não vermelho), o cartão diz "os dois instrumentos discordam; o técnico decide", sem número.
- Todo cartão termina com "o que confirmar no chão com o técnico".
- **Freio de segurança:** sem restrições, o otimizador de renda bruta escolhe "100% mandioca" em todos os municípios (`pesquisador_ia_conformal_carteira.py`). É o exemplo de por que a ferramenta apoia e não decide.

---

## 4. Arquitetura: núcleo global de dados NASA e enriquecimento local

### 4.1 Visão geral

```
        NÚCLEO GLOBAL                                               ENRIQUECIMENTO LOCAL (quando existe)
 [usado] IMERG V07 diário 0,1° (TRMM 1998–2014, GPM 2014→; Late/Early)  Brasil: IBGE PAM (árbitro e calibração), ZARC oficial
 [usado] SMAP L4 v008 zona da raiz 9 km (2015→): 2ª luz dos portões     (a conferir), MapBiomas, Garantia-Safra (a conferir)
 [checagem] SMAP L3 v006 (observação do radiômetro)                     EUA: CDL/CSB, NASS, SSURGO, NLDAS-2 (em disco)
 [usado] POWER (1981→; chuva = reanálise MERRA-2 corrigida)             Resto: FAOSTAT, GDHY, calendários SAGE/GGCMI
 [usado] GRACE/GRACE-FO mascons (~300 km) · GLDAS-2.1 Noah · GLDAS-2.2 CLSM   Família: data de plantio, água guardada, maniva,
 [usado] Landsat 1984→ · HLS/S2 30 m · MODIS→VIIRS VNP13A3 · VIIRS focos      veredito de fim de safra
 [usado] NASADEM/SRTM 30 m · NEX-GDDP-CMIP6 · ONI/TNA/TSA (NOAA)
 [roteiro] ECOSTRESS/ESI · Prithvi-EO-2.0 · NISAR (com regra de validação pré-declarada)
                  │                                                   │
                  ▼                                                   ▼
   GRADE COMUM + ESCALA ÚTIL MEDIDA ─► exportador (lê as saídas já validadas) ─► JSON por município
        ─► Relógio (3 curvas, 5 portões, 2 luzes) ─► Cartões S0–S3 + recibo ─► Replay 1998 e 2016 (NASA estima, IBGE arbitra)
```

### 4.2 Grade comum, escala útil e regras de harmonização

A coluna nova, "escala útil medida", é a menor escala em que dois sensores independentes concordam nas anomalias com r ≥ 0,8 (regra pré-declarada pelo especialista em sensoriamento remoto; `v2_sr_fundacao_escala_real.saida.txt` e `v2_sr_fundacao_smap_l3_l4.saida.txt`, bloco B). O município mediano do Ceará tem 632 km², ou 25 km de lado.

| Camada | Resolução nativa | Escala útil medida | Como entra na grade comum | Regra de uso |
|---|---|---|---|---|
| IMERG | 0,1° (~11 km), diário | Nunca chega a r 0,8 contra o SMAP L3 (0,57 a 11 km; 0,63 a 88 km): vale para o **ano e a região** | É a **grade de decisão**. Agregada ao polígono do município para calibrar contra o PAM. | Chuva desde 1/jan por portão, **sempre por era** (1998–2015 e 2016–2025). Na estação seca, mm e posto. O Late e o IMERG via POWER são o mesmo dado na sobreposição de 01/ago a 14/set/2026 (razão 1,00; r 1,00; `v2_clima_estacao_seca_2026.saida.txt`). |
| SMAP L4 (SPL4SMGP v008) | 9 km, granulo diário das 13:30 UTC | Diz **quando** a 9 km (r temporal com o L3 de 0,89 por célula) e **onde** a partir de 36 km (r das anomalias 0,824) | Média das células de 9 km com centro no município (mediana de 8 células; Quixadá tem 25). | **Percentil da zona da raiz, média dos 7 dias até o portão; < 20 acende a luz.** De ~12/ago a ~12/jan o percentil do produto vem vazio no sertão: aí entra o **percentil próprio** (posto entre os anos desde 2015, com o n) e o nível absoluto. Nunca limiar absoluto em m³/m³: cinco estimativas NASA da água na raiz diferem até 0,10 m³/m³ no nível (CLSM 0,256 contra SMAP 0,161; `v2_hidrologo_cinco_fontes_umidade.saida.txt`). Deduplicar as 4 datas repetidas. |
| SMAP L3 (SPL3SMP_E v006) | 9 km, AM e PM | Igual ao L4 (concorda em r 0,89 na anomalia diária do estado) | Só checagem | Qualidade recomendada (bit0 = 0). Cada célula é vista em 13–15 dias por mês, na quadra e na seca. |
| POWER | 0,5°, diário | — | Célula válida mais próxima de cada célula IMERG. | Sempre como **anomalia ou percentil por fonte**. A Tmax do POWER é cerca de 1,7 °C mais quente que a do ERA5, e a ET0 fica ~15% acima (seção 9.7). |
| GRACE/GRACE-FO | ~300 km | Regional | Mascon regional, **média móvel de 3 meses**. | Só contexto regional. Um mês isolado só aparece com a faixa de ruído. O recibo mostra n_eff ≈ 28. |
| GLDAS-2.2 CLSM (diário) | 0,25° | Regional: a célula de Quixadá anda junto com o CE (r 0,98; `v2_designer_banco_lento.saida.txt`) | Água subterrânea (GWS) por mês | **Assimila o GRACE**: é o GRACE redistribuído, não uma segunda opinião. A concordância com o GRACE (r 0,88 no CE) não vale como validação. |
| GLDAS-2.1 Noah (mensal) | 0,25° | Regional | Umidade em 4 camadas | É a referência **não circular** contra o GRACE (r da anomalia 0,65 no CE). |
| HLS / Landsat / S2 | 30 m (20 m) | Talhão, mas visível em só 29–71% dos portões | Desvio **relativo à vizinhança na mesma data**. | Cancela a deriva comum dos sensores e o viés de amostragem: o céu limpo coincide com o veranico (`sr_fundacao_r2_ceu_limpo_veranico.py`). |
| MODIS → VIIRS (VNP13A3) | 250 m – 1 km | **25 km na quadra** (r 0,854; 0,42 a 1 km) e 2 km na seca | NDVI **relativo ao estado no mesmo ano**, agregado ao município. O VIIRS é a fonte a partir de 2012. | Continuidade: r 0,986 com o MODIS na média do estado e cobertura de jul–out/2025. O composto de nov/2026 é provisório (produzido em 13/11). O NDVI absoluto pós-2020 está deslocado (M6). |
| VIIRS (focos) | 375 m (~14 ha) | — | Contagem de focos por célula, agregada à paisagem. | Não é área queimada e nunca serve para fiscalizar um talhão: 51% dos focos de out–dez caem em pixel arbóreo e só 4,7% em lavoura (`v2_ecologo_calendario_fogo.saida.txt`). Área queimada: MapBiomas Fogo a 30 m. |
| NASADEM/SRTM | 30 m | — | Declive e baixio por município. | Erosão, baixio e aleias em nível. |
| NEX-GDDP | 0,25° | — | Delta de Tmax sobre o replay. | Cenário rotulado; só temperatura (a chuva não é robusta entre modelos; síntese 90.1). |
| NISAR (roteiro) | 200 m | Não medida | — | Antes de qualquer uso: agregar a 9 km e exigir r ≥ 0,8 nas anomalias contra o SMAP L3 a 36 km. Provisório e não validado (revisão, D40). Nenhum dado do NISAR na demo. |

### 4.3 Que variáveis entram em cada módulo

| Módulo | Variáveis NASA | Variáveis locais | Saída |
|---|---|---|---|
| M1, gêmeo físico | IMERG diário; ET0, Tmax e radiação do POWER; declive NASADEM; **SMAP L4 como alvo de calibração do estado** | Água disponível do solo, data de plantio, Kc e ciclos | ISNA por estágio, sobra de água na colheita, demanda de salvamento, janela sintética tipo-ZARC, **estado da água calibrado** (novembro e entressafra) |
| M2, emulador de replay (fim de safra) | Saídas de M1; dias quentes acima do p90 local (POWER); NDVI relativo (**VIIRS**, MODIS antes de 2012) | PAM (alvo) | Estimativa da NASA para cada quadra do replay, com intervalo |
| M3, previsor por portão | IMERG acumulado desde 1/jan; **SMAP L4 percentil da zona da raiz (2015→)**; **API do IMERG (τ = 13 d) como segunda luz antes de 2015** | ONI | Duas luzes por portão, habilidade por era, aviso de caso inédito, contagem de análogos, probabilidade do P1 |
| M4, carteira e política | Replay de M1–M3 nas 28 quadras | Pesos, restrições, preços | 3 estratégias + a atual, em sequência de 3 anos |
| M5, prática atual | MODIS/HLS (fenologia), focos VIIRS | PAM, 1 pergunta à família | Estratégia atual |
| M6, sentinela de deriva e qualidade | LST e NDVI do MODIS contra POWER, Landsat, HLS e **VIIRS**; **disponibilidade e duplicatas do SMAP** | PAM (bandeira de relato repetido) | Rebaixamento automático do grau |
| M7, relógio lento e combustível | **Memória de chuva do IMERG (12–48 meses)**; GRACE e GLDAS como checagem; fração de água do Landsat; NDVI VIIRS de t e t−1; focos VIIRS | Volume de barreiro ou cisterna | Banco de água azul, área salvável, **mapa** de combustível e da ponte verde |
| M8, redator com verificador | JSON de M1–M7 | Trechos conferidos da revisão | Textos dos cartões em PT e EN, congelados |

### 4.4 Frescor dos dados na data da demo (14/11/2026)

- IMERG V07 Late: até 12/11/2026; Early: até 13/11/2026 (Nordeste, diário). IMERG diário municipal: até 14/09/2026.
- **SMAP L4 diário: 31/03/2015 → 10/11/2026**, sem dia faltando em 2016–2025; 4 datas com dois granulos, a deduplicar no exportador.
- **SMAP L3:** o consolidado chegou às 10:06 de sábado; as checagens usaram os recortes diários (até 04/06/2025 no teste do cético; até 08/05/2024 no do especialista em SR). Os números L3 podem mudar um pouco e devem ser refeitos antes do deck.
- **VIIRS VNP13A3:** até out/2026 (nov/2026 é provisório e fica fora de painel).
- **GLDAS-2.2 CLSM diário:** até 31/08/2026. GLDAS-2.1 Noah mensal: até jul/2026. NLDAS-2: até out/2026.
- ONI: até ASO/2026. GRACE: até set/2026.
- MODIS: até set/2026 no arquivo mensal, com o buraco de jul–out/2025 no Terra.
- PAM: até 2025. Focos VIIRS no arquivo anual: até dez/2025 (o FIRMS de 2026 exige o NRT com chave).
- Pink Sheet: até out/2026.
- Nota de unidade: o derivado `imerg_late_ce_mensal` rotula como "mm/day" o que é total mensal. O arquivo não foi alterado; a correção vale para o exportador.

---

## 5. Os módulos de IA (SI)

**Princípio da equipe:** com 28 quadras e um punhado de episódios de seca desde 1998, a SI que funciona é **pequena, guiada pela física, validada por ano e comparada só com a mesma linha de base**. Quatro medidas sustentam isso:

- **A validação aleatória mente:** o boosting tem R² 0,49 com validação aleatória e −0,08 deixando o ano de fora (`cetico_escala_vazamento.py`).
- **A restrição física ajuda pouco e de forma honesta:** com as mesmas entradas, o GBM monotônico dá AUC 0,794 contra 0,762 do GBM livre, no milho (+0,03). No feijão, não ajuda (0,702 contra 0,739) (`saidas/hidrologo_hibrido_log.txt`).
- **O estado vence a soma, e isso não é exclusivo do satélite:** em 30/abr (2016–2025), o percentil da zona da raiz do SMAP dá AUC 0,77 contra 0,66 da chuva desde 1/jan; o estado da chuva do próprio IMERG (API de 30 dias) reproduz quase tudo, e o SMAP soma no máximo +0,02 a +0,03 sobre ele em São José (`v2_pesquisador_ia_gldas_portoes_longo.saida.txt`).
- **Dentro do ano, nada bate a geografia:** nenhum sinal NASA que muda de ano para ano passa de AUC ~0,60 entre municípios no mesmo ano, e o mapa de risco de base do município sozinho dá de 0,61 a 0,69 no milho, conforme o portão (`v2_hidrologo_smap_portoes_quebra.saida.txt`).

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
- **Sensibilidade das datas-limite:**
  - À fonte da ET0: com a ET0 na escala do ERA5 (× 0,87), as datas andam no máximo 1 decêndio em 97–99% dos municípios (`arquiteto_final_zarc_et0_sensibilidade.saida.txt`). Em Quixadá, o milho fica em 01/mar e o caupi em 21/mar nas duas escalas; o sorgo vai de 11/mar para 21/mar.
  - **Ao modelo de solo (novo):** com a zona da raiz do SMAP no lugar do balde, o caupi concorda (±1 decêndio em 58% dos municípios), mas o milho fica 3 decêndios mais tarde na mediana (em Quixadá, 21/abr contra 01/mar) e o sorgo 2. O SMAP não ordena a quebra entre municípios (ρ −0,13), e o balde ordena. **As datas ficam com o balde.** O cartão do caupi mostra ±1 decêndio; o do milho e do sorgo diz "a incerteza passa de ±1 decêndio: outro modelo de solo da NASA dá mais tarde, sem validação" (`v2_agronomo_smap_janelas.saida.txt`, blocos B e C).
- **Onde erra:**
  - Superestima 2010 e 2013. O **ISNA de cultura semeada na 1ª chuva** não vê 1998: 4% dos municípios com ISNA < 0,5, contra 67% em quebra real (`pesquisador_ia_checa_simulador_anos.py`).
  - **Correção da rodada 2:** o ponto cego é dessa formulação, não do balanço hídrico. O estado da água do balde, em percentil, acende para 1998: abaixo de 20 em 30/abr em 135 das 135 quebras (a chuva pegou 103). Grau C, porque o balde começa vazio em 1/jan/1998 (`v2_hidrologo_calibra_m1_smap.saida.txt`).
  - O risco de 2027 continua vindo do oceano (M3, P1), e não do balde.
- **Incerteza:** a ordem resiste à água disponível do solo (ρ de 0,46 a 0,48 entre 30 e 90 mm). O nível não resiste: P(ISNA < 0,5) vai de 1,5% a 14,3% (`saidas/hidrologo_calibracao_balde.csv`).

### M2. Emulador de replay em duas escalas (estimativa de fim de safra)

- **Papel:** dar, para cada quadra do replay, a estimativa da NASA para o rendimento relativo do município, ao lado do observado do IBGE.
- **Rótulo obrigatório:** é um **emulador de fim de safra**. Ele usa o NDVI de mar–mai e o ISNA da floração, então **nunca aparece ao lado da curva de habilidade dos portões**.
- **Método:** ridge ou GBM monotônico em duas escalas:
  - nível do ano: ISNA agregado + calor relativo;
  - ordem local: desvio do ISNA + desvio do NDVI **relativo ao estado no mesmo ano** (a variante "relativo aos vizinhos de 50 km" é pior em todos os portões: 0,561 contra 0,630 no fim de safra; `v2_sr_fundacao_viirs_portoes.saida.txt`, bloco C).
- **Validação, só pareada** (mesmas dobras LOYO; `saidas/pesquisador_ia_fusao_fisica_satelite.csv`):

  | Configuração | R² LOYO | ρ dentro do ano | AUC quebra | Viés walk-forward 2020–25 |
  |---|---|---|---|---|
  | Só chuva, HGB | 0,365 | 0,155 | 0,816 | −0,13 |
  | Duas escalas (ISNA ano+local, NDVI só local), ridge | 0,365 | 0,307 | 0,851 | +0,01 |

  - **Suspenso do slide na rodada 2:** o ganho de ordem local (0,155 → 0,307) ainda não foi comparado com uma linha de base **só de geografia**. O mesmo teste mostrou que a vantagem do ISNA dentro do ano era geografia. Até o bloco 0 refazer essa comparação, o número fica na auditoria.
  - A faixa das 14 configurações testadas vai de AUC 0,78 a 0,85. A configuração foi escolhida olhando o LOYO; por isso o bloco 0 do MVP refaz a escolha por **seleção aninhada**. Até lá, o recibo mostra a faixa.
  - O alvo do M2 (anomalia contra tendência) não é o canônico. No replay, o observado mostrado é sempre a razão canônica.
  - **Regra anti-artefato (nova):** a AUC 0,851 vem de previsões LOYO agregadas. Com poucos anos, essa métrica é enviesada (com 10 anos, a climatologia LOYO sozinha dá AUC 0,154; `v2_pesquisador_ia_smap_portoes.saida.txt`, superado). Com 28 anos o viés é menor, mas o bloco 0 confere com escore sem intercepto e AUC dentro do ano.
- **Continuidade do NDVI:** o VIIRS substitui o MODIS sem retreinar o M2 antes do júri. No fim de safra, o VIIRS perde cerca de 0,02 de AUC dentro do ano contra o MODIS (0,599 contra 0,621, IC −0,05 a +0,00) (`v2_sr_fundacao_viirs_portoes.saida.txt`, bloco C).
- **Testemunha de junho (novo):** o NDVI VIIRS de abr–mai, em % do normal do município, é a primeira leitura da safra pela NASA, um ano antes do PAM. Abaixo de 90% do normal, 7,5 em 10 municípios quebraram o milho (n = 309 município-anos, 12 de 14 anos); acima, 1,9 em 10; AUC 0,79 (IC90 por ano 0,73–0,83) (`v2_designer_verde_viirs.saida.txt`, bloco A). Dentro do ano, ~0,62, igual à geografia: é **testemunha do ano**, não ordem local. Grau A como testemunha; não é alarme.
- **Incerteza:** conformal robusto ao ano (o ano é a unidade trocável). Ele cobre 77–86% dos anos no nível de 80%, contra 46–68% do conformal padrão, **mas compra isso com largura**. No portão de pré-safra, a largura passa de 227 para 282 pontos percentuais, onde o modelo é pior que a climatologia (MSSS −0,37). A frase certa é: "em janeiro, a incerteza honesta é do tamanho da climatologia" (`pesquisador_ia_conformal_carteira.py`).

### M3. Previsor por portão, com duas luzes

- **Papel:** em cada portão, dizer o que já se sabe e quanto isso vale, e quando não se sabe nada.
- **Luz 1, regra canônica (mantida):** **chuva IMERG acumulada desde 1/jan < 75% do normal do município**, sendo o normal a mediana dos outros anos.
- **Luz 2, nova (pré-registrada para 2027):** **percentil da zona da raiz do SMAP L4 < 20, na média dos 7 dias até o portão**. Antes de 2015, no replay, a luz 2 é o estado da chuva do IMERG (API com τ = 13 d medido no próprio SMAP, < 75% do normal), como no teste fora da amostra do agrônomo.
- **Regra "duas luzes":** o portão acende se a luz 1 **ou** a luz 2 acender. A tela mostra as duas luzes separadas, o recibo das duas eras e a mensagem própria quando elas discordam.
- **Curva de habilidade por era** (quebra canônica do milho; IC90 por bootstrap de anos; `arquiteto_final_curvas_quixada.saida.txt`, bloco A; `v2_arquiteto_arbitragem_smap.saida.txt`, blocos A–E; `v2_cetico_smap_portoes.saida.txt`):

  | Portão | Chuva NASA, 28 quadras 1998–2025 (AUC) | Chuva, 1998–2015 | Chuva, 2016–2025 | SMAP L4, 2016–2025 (7 dias / dia) | Oceano, ONI já publicado | Dentro do ano |
  |---|---|---|---|---|---|---|
  | 15/nov | — | — | — | — (percentil vazio) | 0,67 (0,53–0,78) | 0,50 |
  | 31/jan | 0,57 (0,43–0,68) | — | 0,27 | — / 0,26 | 0,67 | 0,53 (chuva) |
  | 28/fev | 0,67 (0,58–0,74) | — | 0,46 | 0,62 / 0,61 | 0,67 | ~0,50 (chuva e SMAP) |
  | 19/mar | 0,73 (0,66–0,79) | 0,77 | 0,55 | 0,68 / **0,59** | 0,67 | 0,53 (chuva, 28 anos); 0,53–0,57 (SMAP) |
  | 31/mar | 0,75 (0,66–0,80) | — | 0,55 | — / 0,58 | 0,67 | 0,54 (chuva) |
  | 30/abr | **0,80 (0,73–0,85)** | 0,83 | **0,66** | **0,77 / 0,77** | 0,67 | 0,57 (chuva, 28 anos); 0,55–0,56 (SMAP) |

  - Taxa-base de quebra: 2,15 em 10 (1998–2025); 2,5 em 10 em 1998–2015 e 1,5 em 10 em 2016–2025.
  - Em 19/mar, as duas leituras do SMAP divergem (0,68 e 0,59), e sem 2016 as duas ficam abaixo de 0,5. **Vale a menos favorável: o solo ainda não decide em São José.**
  - Em 30/abr, as duas leituras dão 0,77, e a diferença contra a chuva é de +0,11 (IC90 por ano de −0,02 a +0,17 no dia; de +0,00 a +0,17 na média de 7 dias). É o único portão em que o solo fala alto.
  - A AUC de 30/abr mede uma janela que já é quase a quadra inteira (jan–mai dá 0,83 em 28 anos; `cetico_r3_refutacoes.saida.txt`, bloco G). Por isso 30/abr serve para salvar, não para prever.
  - A coluna "chuva + oceano (logística, ano fora)" da rodada 1 (0,62 a 0,81) usa AUC agregada de probabilidades LOYO e será reconferida no bloco 0 com a regra anti-artefato. Até lá, sai do slide.
- **Placar dos alertas na era SMAP (2016–2025, milho; 1.820 município-anos, 268 quebras; `v2_arquiteto_arbitragem_smap.saida.txt`, blocos A–D):**

  | Portão e luz | Acende em | Com a luz, quebram | Sem a luz, quebram | Pega das quebras | 2016 (127 quebras) | 2021 (7 quebras) | 2025 (45 quebras) |
  |---|---|---|---|---|---|---|---|
  | 19/mar, só chuva | 12% | 1,0 em 10 | 1,5 em 10 | 8% | 6 (7 alertas) | 7 (100 alertas) | 0 |
  | 19/mar, SMAP (7 dias) | 7% | 5,0 em 10 | 1,2 em 10 | 23% | 47 (56) | 1 (26) | 5 (12) |
  | 19/mar, SMAP (dia) | 7% | 3,5 em 10 | 1,3 em 10 | 17% | 32 (38) | 1 (24) | 2 (5) |
  | 19/mar, duas luzes (7 dias) | 16% | 2,5 em 10 | 1,3 em 10 | 27% | 48 (57) | 7 (102) | 5 (12) |
  | 30/abr, só chuva | 8% | 1,1 em 10 | 1,5 em 10 | 6% | 9 (14) | 6 (107) | 1 (7) |
  | **30/abr, SMAP (7 dias)** | 13% | **4,0 em 10** | **1,1 em 10** | 36% | **64 (91)** | 3 (81) | 21 (46) |
  | 30/abr, SMAP (dia) | 17% | 4,3 em 10 | 0,9 em 10 | 50% | 90 (128) | 3 (86) | 30 (65) |
  | 30/abr, duas luzes (7 dias) | 16% | 3,6 em 10 | 1,1 em 10 | 39% | 67 (94) | 6 (112) | 22 (49) |

  - **Fora da era SMAP, com o API como luz 2 (1998–2015):** em 19/mar, as duas luzes pegam 71% das quebras contra 52% da chuva sozinha, com a mesma precisão (4,7 em 10); sem luz, 1,2 em 10 contra 1,7. Em 30/abr, 73% contra 56%, com precisão de 5,1 contra 5,9 em 10. As duas luzes acendem mais: 38% contra 28% dos município-anos em 19/mar (`v2_agronomo_smap_contraprova.saida.txt`, bloco e).
  - **O custo, dito junto:** o alerta é regional. Em 2016, a luz do SMAP (7 dias) também acendeu em 27 dos 55 municípios que não quebraram; em 2021, acendeu em 81 municípios e só 3 quebraram. Mostrar 2021 sempre que 2016 aparecer.
  - **O que o recibo diz:** o SMAP L4 é um modelo da NASA forçado pela chuva (corrigida para os totais do IMERG desde a versão 6 do L4_SM; a v008 não foi conferida) e corrigido pelo radiômetro do SMAP. A observação pura do radiômetro (L3) dá o mesmo em 30/abr (AUC 0,77, IC90 0,52–0,88), e a chuva IMERG dos últimos 15 dias também (0,80). **O que funciona é o estado da água, não a soma.** O SMAP é a segunda missão que confirma e a camada global ao vivo (`v2_cetico_smap_l3_obs_vs_modelo.saida.txt`).
  - **Ressalva de processo:** a regra de duas luzes foi formulada depois de ver 2016–2025. O limiar 20 foi escrito antes (seção 05); o teste em 1998–2015 é fora da amostra, mas com o substituto (API). Grau B até a quadra de 2027.
- **Escala declarada:** dentro do ano, a AUC fica entre 0,50 e 0,60 para todas as luzes. O alerta é **regional**. Em Quixadá:
  - luz 1 (28 anos): 19/mar, 8 alertas e 2 acertos; 30/abr, 7 alertas e 3 acertos (`arquiteto_final_curvas_quixada.saida.txt`, bloco C);
  - luz 2 (2016–2025, limiar 20): **nenhum acerto.** Em 30/abr, os dois anos secos têm os dois menores valores do dia (2016 = p20,1; 2025 = p20,3), por décimos acima do limiar; na média de 7 dias, a luz acende só em 2021 (p15,9), ano sem quebra. Em 19/mar, só em 2018 (dia, p15,4), sem quebra. Não reajustamos o limiar; o placar mostra isso.
- **Portão de novembro (P1), modelo único pré-registrado** (`v2_clima_portao_novembro_2027.saida.txt`): logística P(quebra municipal) ~ ONI ASO do ano anterior, validada deixando o ano inteiro de fora.
  - BSS municipal +0,063 (IC90 −0,07 a +0,18): habilidade pequena, com IC que inclui zero. No nível do ano, ρ +0,39 (p = 0,038; n = 28).
  - No máximo já visto (ONI 2,04): **0,54 (IC90 0,24–0,75)**, contra 0,20 com ONI 0 e 0,215 de taxa-base. Em 2,46 (o de hoje): 0,62 (0,25–0,83), **por extrapolação**; o valor vai de 0,53 a 0,72 conforme o análogo retirado.
  - Na tela: "num ano qualquer, 2 em 10 municípios perdem metade do milho; com o mar assim, cerca de 5 em 10 (faixa honesta de 2 a 8)". Logo abaixo, a distribuição dos análogos: 1998, 7,5 em 10; 2016, 7 em 10; 2024, menos de 1 em 10. É uma moeda viciada, não uma média tranquila.
- **Detector de caso inédito:** o ONI de 2,46 está 0,42 acima do máximo de ASO das quadras de 1982 a 2026 (2,04). A tela mostra o valor em 2,04 como "dentro do que já vimos" e o de 2,46 com selo de extrapolação.
- **Análogos só como contagem:** o app mostra quantos anos parecidos houve e o que aconteceu em cada um (seção 6.3). Três contagens dizem o mesmo, risco alto e longe de certeza: 4 de 7 quadras secas desde 1966 (1966 por proxy); 3 de 5 pela reanálise POWER desde 1982 (IC90 0,19–0,92); 2 de 3 catástrofes na era IMERG (IC90 0,14–0,98).
- **O que vigiar em P2 (só texto, sem probabilidade):** o Pacífico dificilmente esfria a tempo (1 de 7 El Niños fortes). O Atlântico Sul (TSA de jul–set) separou os análogos que escaparam, mas a hipótese nasceu ao olhar 5 deles e a contraprova (2 de 2) tem chance de acaso de 0,25. Hoje o TSA está do lado de 2024 (+0,37). A tela diz "em jan–fev vamos olhar o Atlântico". Fica fora do pitch.

### M4. Carteira e política

- **Papel:** gerar e ordenar as estratégias (a atual e mais 3) e a regra de cada portão.
- **Método:** **enumeração exata** de uma biblioteca de jogadas por portão: as regras de plantio R1–R9, a troca de cultura, o revezamento, o salvamento, a palhada e a composição de área. As regras R1–R9 já são a árvore de decisão que o técnico repete; não há destilação à parte.
  - **Correção de rótulo:** as regras R4, R5 e R8 apareciam como "(SMAP)" em `saidas/agronomo_regras_semeadura.txt`, mas eram um balde de solo nu. Passam a "R4/R5: balde, solo ≥ 30/45 mm" e "R8: fevereiro ou balde ≥ 45 mm em janeiro". Com o SMAP de verdade, "esperar o solo encher" não separa a quebra: o percentil da zona da raiz no dia de semeadura tem AUC 0,47, e o tercil úmido quebrou até um pouco mais (15,5% contra 11,4% no seco) (`v2_agronomo_smap_portoes.saida.txt`, P2).
- **Ranking:** usa os 3 eixos calculados: chance de colher menos da metade, "pior ano em 10" e mediana. Os pesos da família mexem só nesses 3. Forragem, N, carbono, trabalho e ciclos entram como etiquetas com grau.
- **Um motor de carteira só** no JSON: a carteira de áreas iguais, com a definição canônica (`juiz_carteira_definicao_canonica.py`, definição b). A carteira de mínimo CVaR do economista ("melhora em 81% de 131 municípios") vai para a auditoria como "diversificação em geral".
- **Validação** (`arquiteto_final_carteira_ic.saida.txt`; 2.495 município-anos, 135 municípios, onde as três culturas existem):

  | Composição | Pior ano em 10 (CVaR10) | IC90 por ano | Chance de < 50% |
  |---|---|---|---|
  | 100% milho | 0,15 | 0,09–0,26 | 21% |
  | Milho + feijão | 0,26 | 0,19–0,38 | 15% |
  | 1/3 milho, 1/3 feijão, 1/3 mandioca | **0,36** | 0,28–0,47 | **11%** |

  - O ganho de CVaR10 da carteira 1/3 sobre o milho é de +0,17 a +0,23 (IC90 por ano). Sem os anos de mandioca com rendimento repetido: de 0,14 para 0,34.
  - **Piso declarado (novo):** a M4 só conta os anos em que a mandioca existe, e ela some na seca (25% dos município-anos de 2016 sem mandioca). Contando o ano sem mandioca como perda total, nos 91 municípios de mandioca, o CVaR10 fica em **0,321 (IC90 0,265–0,401)**, contra 0,169 do milho; o ganho mínimo é de +0,12 a +0,17. Se o terço sem maniva vira milho + feijão, 0,356 (`v2_economista_diversidade_carteira.saida.txt`, bloco C).
  - **Teto, não promessa (novo):** na carteira real dos municípios, cada cultura efetiva a mais vale +0,067 no CVaR10 (IC90 +0,043 a +0,081), cerca de 65% do que a conta da M4 promete por cultura (+0,103). Acrescentar uma cultura que quebra junto com o milho (feijão) rende menos (mesmo arquivo, bloco B).
  - **A cauda (corrigida):** a cauda da carteira real vem de **cinco a sete anos ruins desde 1998** (em ordem de peso: 1998, 2012, 2016, 2015, 2010, 2001 e 2013), não de "três episódios".

### M5. Leitor da prática atual

- **No MVP:** a prática atual vem do PAM do município (o que se planta e quanto) e de **1 pergunta** à família ("o senhor queimou o roçado em nov/2025?"). O satélite não responde isso: a 375 m, o FIRMS não separa a broca do roçado do incêndio na capoeira (51% dos focos de out–dez caem em pixel arbóreo).
- **Figura estática:** o "código de barras de safras" (fenologia MODIS/HLS + focos VIIRS) da AOI do Sertão Central entra como figura, com o selo de visibilidade.
- **Selo de visibilidade (atualizado):**
  - Óptico a 30 m: fração de AOI-anos com ao menos uma cena útil (≥ 60% da área limpa) nos 30 dias antes do portão, com Sentinel-2 + Landsat: 79% em 28/fev, 71% em 31/mar e 92% em 30/abr (n = 24 AOI-anos). Só com o Landsat 8/9: 50%, 29% e 46% (`sr_fundacao_r2_checagens.log`, bloco B).
  - Óptico a 1 km: só 39–40% dos pixels do CE têm NDVI VIIRS bom no mês em jan–mar, contra 95–96% em ago–out.
  - **Micro-ondas (novo):** o SMAP vê cada célula de 9 km em 13 a 15 dias por mês, na quadra e na seca; 93,5% das células têm vista nos 16 dias antes de cada portão (`v2_sr_fundacao_smap_l3_l4.saida.txt`, bloco A). "O satélite óptico fica cego nas datas de decisão; o micro-ondas não."
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
  - **Novo, SMAP L4:** 4 datas com dois granulos no consolidado (2023-10-09, 2024-04-03, 2024-11-26, 2025-05-22), com até 0,09 m³/m³ de diferença na zona da raiz; o exportador deduplica (aviso ao dono de `consolidar_smap_viirs.py`). O percentil do produto vem vazio de ~12/ago a ~12/jan no sertão. E a base da climatologia do percentil não foi conferida: só 13,2% dos município-dias de 2015–2026 ficaram abaixo de p20, quando se esperaria 20% (`v2_designer_termometro_solo.saida.txt`). Até conferir na documentação, nenhum texto diz "mais seco que 8 de cada 10 anos".
  - **Novo, VIIRS:** o composto de nov/2026 foi produzido em 13/11, antes do fim do mês, e fica fora de qualquer painel.
  - **Novo, discordância SMAP × chuva:** em 2026, o SMAP marcou p39 em 19/mar e p35 em 30/abr, com a chuva a 110% e 105% do normal (`v2_hidrologo_cinco_fontes_umidade.saida.txt`). Só o PAM de 2026 arbitra. A sentinela registra o caso.

### M7. Relógio lento da água e combustível

- **Banco de água azul (refeito):**
  - O relógio lento passa a rodar na **memória de chuva do próprio IMERG** (filtros de 12 a 48 meses): é global, fresco (Late até 12/11) e não depende do GRACE. Cerca de 70% da variância da água subterrânea do GLDAS-2.2 CLSM é só memória de chuva (R² 0,70; 0,55 deixando o ano de fora), e a parte que vem do GRACE não acompanha os açudes do Landsat (ρ +0,04, contra +0,50 da parte da chuva; n = 23) (`v2_hidrologo_relogio_lento_gws.saida.txt`).
  - **GRACE e GLDAS viram a checagem de segunda missão.** A concordância CLSM × GRACE é em parte circular: a água subterrânea do CLSM acompanha o GRACE (r da anomalia 0,85) mais de perto que o próprio TWS do modelo (0,81), e o Noah, que não assimila, dá 0,65 (`v2_cetico_clsm_grace_viirs.saida.txt`).
  - Memória: a água subterrânea esquece em cerca de 8 meses na série mensal de 2003–2026 (e-folding; 392 dias na série diária de 2015–2026). O recibo diz "8 a 13 meses". Depois de 2016, o banco só voltou ao normal em abr–mai/2018 (`v2_designer_banco_lento.saida.txt`).
  - **Não prevê a quadra:** o banco de jun–ago (t−1) contra a fração de municípios em quebra no ano t dá ρ +0,14 (n = 22); o GWS de dezembro, +0,05 (n = 22). O banco lento serve para poço, cacimba e água dos animais, não para escolher a cultura; fica na tela do técnico, sempre como "sua região".
  - No Sertão Central, a fração de água dos açudes no Landsat (1984–2026) acompanha a chuva de 48 meses (ρ +0,62), num sinal que existe em 1 das 4 AOIs (rodada 1; grau C).
- **Área salvável:** o salvamento da floração do milho pede 62 mm na mediana (620 m³/ha). Uma cisterna-calçadão de 52 m³ salva cerca de 0,08 ha num ano mediano. **O salvamento só existe com barreiro ou açude**; o app pergunta o volume.
- **Combustível (corrigido):** o "+0,072 fora do ano" da rodada 1 era quase todo tendência. Contra climatologia + tendência, o combustível do VIIRS (NDVI de fev–jun de t e t−1) acrescenta +0,020 (IC90 +0,001 a +0,042); a tendência sozinha vale +0,098. No portão de 30/set, o índice de combustível e secura com o SMAP dá +0,002 (IC90 −0,041 a +0,044) e ρ −0,03 entre anos: **sem habilidade no total do ano**. Dentro do ano, a ordem entre municípios tem ρ ~+0,2 (`v2_ecologo_indice_combustivel_rz.saida.txt`). O app mostra o combustível **em tercis, como mapa**, com a frase "sem habilidade comprovada no nível do ano", e nenhum número de focos previstos.
- **Ponte verde (novo, grau C):** os pixels de lavoura ou mosaico ainda verdes em outubro (NDVI VIIRS ≥ 0,55) são onde a lagarta atravessa a seca. Em out/2026, 5,0% da lavoura (3ª maior de 15 outubros; mediana 3,4%). A geografia é fixa (90% da variância), então o mapa serve para posicionar armadilhas e a visita do técnico. A ponte de um ano não muda o milho do ano seguinte no PAM (+0,001 por dp; IC95 −0,036 a +0,037) (`v2_ecologo_ponte_verde_pragas.saida.txt`).

### M8. Redator com verificador

- **Papel:** redigir os textos dos cartões em PT e EN a partir do JSON.
- **Método:**
  - Os textos são redigidos **offline**, nesta sessão de trabalho, por um LLM (uso de inferência), com os números como marcadores `{var}` preenchidos pelo JSON. Depois são **congelados como estáticos**.
  - **Nenhuma API é chamada em tempo de execução.** O saldo da API da equipe acabou em 12/11, e a demo não pode depender de serviço externo.
- **Verificador determinístico** (cerca de 30 linhas):
  - todo número do texto precisa existir no JSON, com a mesma unidade, a mesma entidade e o mesmo grau;
  - léxico proibido: "garante", "vai chover", "certeza", "vai quebrar", "o solo do seu roçado";
  - **regras novas:** bloqueia frequência do termômetro do solo entre agosto e meados de janeiro; exige "na sua região" em toda frequência; bloqueia "mais seco que 8 de cada 10 anos" até a climatologia do percentil ser conferida;
  - teste com cerca de 30 casos adversariais (número inventado, atribuição trocada, verbo de certeza), todos bloqueados.
- **Regra:** nenhum modelo é treinado com saídas de LLM.

### Os 5 usos de SI que vão para o slide

1. Gêmeo físico FAO-56 calibrado contra o SMAP (estado da água) e emulador monotônico de fim de safra, com conformal robusto ao ano (M1 + M2).
2. Curva de habilidade por portão e **por era**, medida sem olhar o futuro, com **duas luzes pré-registradas** e detector de caso inédito (M3).
3. Busca exata de estratégias pela cauda (CVaR), com piso declarado e freio de segurança (M4).
4. Sentinela de deriva e de qualidade de dado: deriva do Terra, NDVI deslocado nos dois sensores, relato copiado no PAM, percentil e duplicatas do SMAP (M6).
5. Redator LLM aterrado, com verificador numérico e sem chamada em tempo de execução (M8).

### O que deliberadamente não usamos, e por quê

| Fica fora | Motivo, com dado |
|---|---|
| ML livre para prever rendimento no plantio | MSSS −0,37 no pré-safra: pior que a climatologia. |
| "Modelo grande" | Nenhum foi testado. Afirmamos só que a validação aleatória infla (0,49 contra −0,08). |
| **Floresta causal / DML sobre o PAM para "efeito da rotação"** | O protótipo à maneira de Kluger dá um efeito do feijão anterior de −0,056, e o **placebo do feijão futuro dá o mesmo** (−0,049): o PAM municipal não identifica o antecessor (`v2_pesquisador_ia_precrop_dml.saida.txt`). A floresta causal vai para o roteiro, na escala do talhão. |
| **Percentil pronto do SMAP com corte fixo (≤ 20 em fev–mai)** | Disparou em 1% dos municípios em 2016, com 70% em perda; sem valor de setembro a janeiro (`v2_economista_gatilho_smap.saida.txt`). |
| **GLDAS nos portões** | GLDAS − chuva de −0,041 a +0,013 em 22 quadras; nada sobre o estado do IMERG (`v2_pesquisador_ia_gldas_portoes_longo.saida.txt`). |
| **NDVI como gatilho de portão** | O NDVI disponível no portão não soma à chuva (+0,015 e −0,008). Só no fim de safra. |
| **SMAP de novembro como preditor** | Anomalia de 10/nov → 01/fev: ρ +0,01 (SMAP, n = 11), +0,00 (Noah, n = 26). |
| **Atlântico Sul (TSA) como probabilidade** | Hipótese exploratória com n = 7 e contraprova de acaso 0,25. |
| **SMAP ao vivo ou global no app** | Custaria 3–4 h a mais, fora do orçamento (avaliação do cético). |
| Aprendizado por reforço, NSGA-II, Pareto em 8 eixos | O espaço de jogadas é pequeno: a enumeração é exata e auditável. |
| Downscaling do SMAP a 1 km/70 m | Habilidade espacial R² 0,083 (`sr_fundacao_r2_checagens.py`). |
| TVDI | R² 0,077 deixando o ano de fora (`sr_fundacao_downscaling_aprendido.py`). |
| NDVI absoluto e LST do Terra pós-2020 | Deriva e deslocamento (M6). |
| Dataset "Crop Recommendation" do Kaggle | Padrão de dado sintético (síntese 90.3). |
| Replay com as 44 temporadas do POWER | A chuva do POWER é reanálise. O replay usa só as 28 quadras do IMERG. |
| ECOSTRESS/ESI, Prithvi, SAR, EnKF, GNN de pragas, bot de WhatsApp | Sem dado em disco ou inviável em 36 h. Ficam no slide de próximos passos. |

---

## 6. O motor de rotação

### 6.1 Como gera as estratégias

1. **Biblioteca de componentes:**
   - anuais: milho, feijão/caupi, sorgo;
   - semiperene: mandioca;
   - perenes e forrageiras: palma, guandu, gliricídia;
   - arranjos: consórcio, revezamento, faixas;
   - manejo: palhada, aceiro, fogo ou não fogo.
2. **Regras de sucessão que vêm dos dados:**
   - **No sertão não existe safrinha.** O caupi em revezamento cerca de 50 dias após o milho tem P(ISNA floração ≥ 0,5) de 0,89 na mediana estadual. Em sucessão após a colheita, 0,14, sem nenhum município viável (`agronomo_isna_zarc_sintetico.py`, bloco A4; grau C, limite superior). Pelo SMAP, a maior corrida úmida da quadra tem mediana de 95 dias: cobre o caupi de 75 dias em 69% dos município-anos e o milho de 110 dias em 43% (`v2_agronomo_smap_janelas.saida.txt`, bloco D).
   - **Na entressafra não cabe cultura anual sem água.** A ET0 de ago–dez (POWER) é de 1.224 mm, contra 59 mm de chuva. A sobra de água na colheita é de 85 mm depois do sorgo e de 4 mm depois da mandioca (`hidrologo_fao56_isna_pam.py`). O SMAP confirma: de agosto a dezembro, o primeiro metro fica perto do piso em 49% dos dias. Depois da mandioca, só palhada.
   - **Escape hídrico não é quebra de ciclo.** Trocar milho por sorgo mantém a gramínea hospedeira da lagarta-do-cartucho. A quebra de ciclo exige uma não-gramínea (caupi, mandioca, palma), com o status confirmado pelo técnico. O relógio térmico nunca para (cerca de 23 dias por geração em 2026).
   - **Maniva com a quadra estabelecida (novo, grau C):** a faixa nova de mandioca é plantada de fevereiro a abril, nunca na 1ª chuva de janeiro: P(estabelecimento em 60 dias) de 0,36 em 21/jan e ≥ 0,7 de 11/fev a 01/mai na mediana estadual (`v2_agronomo_smap_janelas.saida.txt`, blocos A e D). A janela do SMAP corre tarde no milho, então pode ser 1–2 decêndios mais cedo.
   - **Troca de São José em ano de luz acesa (novo, grau C):** num ano como 2016, a área guardada precisa ir para o caupi até cerca de 11/mar (água na floração em 70% dos municípios pelo SMAP e 68% pelo balde) e não até 21/mar (40% e 33%). Em 2025: 64%/70% contra 52%/50%. Em anos normais, 21/mar continua valendo (~98–100%). Os dois métodos concordam e são independentes, mas são 2 anos (`v2_agronomo_smap_janelas.saida.txt`, bloco F).
3. **Restrições:**
   - janela sintética tipo-ZARC (±1 decêndio no caupi; incerteza maior no milho e no sorgo), a confirmar no ZARC oficial;
   - semente e maniva disponíveis antes da data-limite;
   - água azul declarada;
   - mão de obra e consumo da família;
   - regras do Garantia-Safra (limiar, cesta e área mínima), **só se conferidas na lei**; senão, saem dos cartões.
4. **Avaliação:** cada estratégia é reencenada nas 28 quadras do IMERG. As sequências de 3 anos são **planos**: cada ano é avaliado na quadra do replay, e o efeito do antecessor (leguminosa, palhada) entra como prior da literatura com grau. O estado do solo entre anos não é simulado no MVP; a memória de novembro até fevereiro é nula (ρ +0,01), então essa simplificação custa pouco na água.
5. **Escolha:** a atual sempre entra. As outras 3 cobrem perfis distintos: calendário (S1), cauda (S2) e solo (S3). Os pesos da família reordenam a lista.
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

**Família de demonstração, fictícia e rotulada como tal:** Dona Francisca, Quixadá, 3 ha (1 ha de baixio pelo SRTM), 8 cabras, cisterna de 16 m³ (água de beber), sem barreiro, semente própria de milho e feijão, **sem mandioca no chão hoje**. Prioridades: forragem > comida da família > renda.

**Contexto do município** (`arquiteto_final_curvas_quixada.saida.txt`, bloco C; `v2_arquiteto_arbitragem_smap.saida.txt`, blocos A–D; definição canônica):
- **Milho:** 8 quebras em 28 anos: 1998 (0,00), 2001, 2012 (0,17), 2015, 2016 (0,12), 2023 (0,36), 2024 (0,46) e 2025 (0,30). Grau A.
- **Feijão:** 5 quebras em 28 anos; 0,15 do normal em 2012. Grau A.
- **Mandioca:** só 10 anos têm as três culturas. A área foi 0 ha em 2012–2013 e 40 ha em 2016, então **não há mandioca observada nos piores anos depois de 1998**.
- **Datas-limite da janela sintética** (risco ≤ 30%): milho até 01/mar (incerteza maior que ±1 decêndio: o SMAP dá 21/abr, sem validação); sorgo até 11–21/mar; caupi até 21/mar (±1 decêndio), ou até ~11/mar em ano de luz acesa. Grau C.
- **Placar das luzes em Quixadá** (o que o técnico vê):
  - luz 1, chuva (28 anos): 19/mar, 8 alertas e 2 acertos; 30/abr, 7 alertas e 3 acertos; perdidas em 30/abr: 2001, 2016, 2023, 2024 e 2025;
  - luz 2, solo (2016–2025): **nenhum acerto**. Em 30/abr, 2016 e 2025 tiveram os dois menores valores do dia na década (p20,1 e p20,3), logo acima do limiar 20; a média de 7 dias acendeu só em 2021 (p15,9), sem quebra;
  - isso é grau A e é mostrado assim mesmo: o alerta é regional.
- **O que a NASA viu nas quebras de 2023–2025** (auditoria):
  - **2025:** chuva a 93% do normal em 30/abr, mas o solo no fundo da década (p20,3) e o NDVI VIIRS de mar–mai entre os 3% mais baixos do estado (0,93 do normal). Seca de fim de quadra, vista tarde (`v2_estrategista_viirs_quixada.saida.txt`).
  - **2023:** chuva a 104% e solo p66 em 30/abr; maio teve 22 mm, e os vizinhos também quebraram (35% dos 20 vizinhos a menos de 0,3°; 5 de 5 a menos de 50 km). Possível fim de chuva depois do portão; NDVI verde (`v2_hidrologo_smap_portoes_quebra.saida.txt`; `v2_sr_fundacao_escala_real.saida.txt`, D).
  - **2024:** chuva a 105%, solo p70, NDVI verde (1,05), **nenhum vizinho quebrou** e a área plantada caiu de 5.000 para 2.800 ha. Sem assinatura hídrica nem de vegetação: "o satélite discorda do árbitro; confirmar praga, relato ou área com o técnico".

#### S0. Atual: "roçado da 1ª chuva" (igual em 2027, 2028 e 2029)

- **Prática:** milho + feijão consorciados plantados na 1ª chuva de 20 mm ou mais em 3 dias. Broca e queima em out–dez; solo nu de setembro a janeiro.
- **Por que aparece:** é a linha de base. O PAM do município mostra que é a prática dominante, e a família confirma.
- **Evidência:**
  - Em Quixadá, o milho quebra em 8 de 28 anos (grau A).
  - Milho e feijão quebram juntos no PAM (0,78; grau A, com a ressalva do relato).
  - No estado, 100% milho tem "pior ano em 10" de 0,15 e 21% de chance de colher menos da metade (grau A).
  - Plantar com o perfil úmido não protege: no dia de semeadura da regra do agricultor, o tercil úmido do SMAP quebrou o milho em 15,5% dos casos, contra 11,4% no seco (`v2_agronomo_smap_portoes.saida.txt`, P2).
- **Benefícios:** custo zero, semente própria, mercado conhecido.
- **Lacunas:** a água disponível do solo do roçado e a data real de plantio.
- **Riscos a confirmar:**
  - solo nu sob chuva erosiva;
  - perda de carbono com a queima (Primo et al. 2023: −50% em 10 anos numa simulação Century de um sítio; grau C);
  - fuga do fogo para os vizinhos;
  - nenhum mês sem gramínea hospedeira.

#### S1. "Escalonar, guardar a decisão e revezar em faixas" (custo zero)

- **2027:**
  - Metade da área na 1ª chuva firme (milho + feijão).
  - **A outra metade fica guardada:**
    - **em ano de mar como o de 2027:** decisão no início de março (~10/mar): caupi até ~11/mar, a menos que as duas luzes estejam verdes; sorgo ou forragem até 19/mar;
    - em ano normal: milho, se a chuva firmar antes de 01/mar; caupi (até ~21/mar) ou sorgo (até 11–21/mar), se uma luz acender em 19/mar.
  - Caupi em revezamento cerca de 50 dias após o milho.
  - Entressafra com palhada roçada, sem queima.
- **2028:** as faixas trocam de lugar: onde houve milho entra caupi/feijão, e vice-versa (gramínea ↔ leguminosa).
- **2029:** as faixas trocam de novo. A palhada e a ausência de fogo continuam.
- **Por que aparece:** janeiro engana (Quixadá teve 150% do normal em jan/1998 e 197% em jan/2016, e os dois anos quebraram; em 31/jan, nem o solo separa a quebra em 2016–2025, AUC 0,26). Escalonar mantém uma opção aberta até o último portão de troca.
- **Evidência:**
  - Em 28 anos, com a luz 1 acesa em 19/mar, 4 em 10 municípios quebram o milho; sem ela, 1,6 em 10 (grau A). **Mas em 2016–2025, 1,0 contra 1,5**: a soma falhou na década.
  - Duas luzes em 19/mar, fora da era SMAP (1998–2015): pegam 71% das quebras contra 52%, com a mesma precisão (grau B).
  - Em 19/mar, o caupi ainda cabe em 98% dos municípios e o milho em 42% (grau C).
  - Caupi semeado em 11/mar em 2016: água na floração em 7 de 10 municípios; em 21/mar, em 4 de 10 (grau C, n = 2 anos).
  - Caupi em revezamento em Quixadá: P 0,75, contra 0,14 em sucessão (grau C, limite superior, porque o balde não modela competição).
- **O que o cartão diz com honestidade:**
  - Em Quixadá, as luzes de 19/mar são fracas: 2 acertos em 8 alertas da chuva e nenhum do solo.
  - O efeito do falso início no PAM não é significativo com erro-padrão agrupado por ano (`cetico_r2_checagens.py`, bloco B).
  - O valor da opção guardada não foi medido no PAM; é grau C.
- **Benefícios:** custo zero; parte da área decide com mais informação; o caupi dá N e proteína.
- **Lacunas:** o replantio não está modelado; a semente de caupi precisa chegar **antes de ~10/mar** em 2027.
- **Riscos a confirmar:** arrependimento num ano bom, quando quem plantou tudo colhe mais; ficar fora da janela do ZARC oficial. A mensagem é "plante escalonado", nunca "não plante".

#### S2. "Tampão e forragem em faixas que giram" (escudo do ano ruim)

- **Desenho:** três faixas que trocam de lugar a cada ano:
  - **mandioca:** uma faixa nova recebe maniva a cada quadra, **de fevereiro a abril** (nunca na 1ª chuva de janeiro), e a mandioca do ano anterior é o tampão do ano, colhida conforme a necessidade;
  - **sorgo forrageiro** com rebrota, como primeira cultura, mais palma adensada no cercado;
  - **caupi precoce** de 60–70 dias.
  - O milho fica só no baixio.
- **Giro das faixas:** a faixa que sai da mandioca recebe caupi, e a do caupi recebe sorgo. Assim sempre há mandioca de um ano no chão. Nenhuma faixa queima.
- **2027, dito com honestidade:** a mandioca precisa ser plantada **no ano anterior** para proteger o ano seco. Sem mandioca no chão hoje, o tampão de Dona Francisca começa em 2028. Em 2027, a proteção vem do sorgo, da palma, do caupi e das ações do P1.
- **Por que aparece:** a prioridade da família é forragem, e o risco do sistema atual está na cauda.
- **Evidência:**
  - Carteira 1/3 milho, 1/3 feijão, 1/3 mandioca no estado: "pior ano em 10" sobe de 0,15 para 0,36 (ganho com IC90 de +0,17 a +0,23), e a chance de colher menos da metade cai de 21% para 11%. São 2.495 município-anos, só onde a mandioca existe. Sem os anos de relato repetido, de 0,14 para 0,34. Grau A no estado.
  - **Piso, contando o ano sem maniva como perda total:** 0,32 (IC90 0,27–0,40), contra 0,17 do milho nos mesmos municípios (grau A no estado).
  - **Na vida real, o ganho é menor que a conta:** cada cultura efetiva a mais na carteira real de um município vale cerca de 65% do que a carteira de áreas iguais promete. O cartão mostra 0,36 como teto.
  - **Replay de 1998 em Quixadá, observado pelo IBGE:** milho 0,00, feijão 0,16, mandioca 0,50. A carteira 1/3 ficou com 0,22, contra 0,08 de milho + feijão. É um ano só (grau A, n = 1).
  - O sorgo tem P(ISNA floração < 0,5) de 6,5%, contra 10,1% do milho (grau C). O PAM do sorgo não serve de evidência: são 21 municípios tecnificados.
  - Palma + sorgo: 6.279 contra 4.627 kg MS/ha (Diniz et al. 2017; ensaio único com irrigação em PE; grau C).
  - **O que não usamos como evidência:** o "+6,6 p.p. dos municípios mais diversos" (seção 8.2). Ele vem sobretudo de menos milho + feijão e de culturas fora do sequeiro; só com sequeiro, +1,4 p.p. (n.s.). A S2 se apoia na carteira observada, não nele.
- **Benefícios:** forragem para as cabras no ano seco; comida da família na mandioca; solo coberto mais tempo.
- **Lacunas e riscos, nesta ordem:**
  1. **Maniva-semente guardada / banco de manivas.** Na seca, a mandioca some: Quixadá teve 0 ha em 2012 e 40 ha em 2016. A carteira estadual existe em 116 de 181 municípios em 1998, 104 em 2012 e 69 em 2016.
  2. Casa de farinha e mercado da mandioca. O hedge de preço (−0,80) é estadual; no município, a elasticidade é cerca de zero.
  3. Semente e mercado do sorgo: a área de sorgo em grão do Ceará caiu de 2.900 ha em 2021 para 15 ha em 2025 (`economista_debate_checagens.py`).
  4. Palma resistente à cochonilha (pergunta obrigatória ao técnico).
  5. O sorgo hospeda a lagarta: é escape hídrico, não quebra de ciclo.

#### S3. "Leguminosa que fica, sem fogo" (rotação no sentido estrito)

- **2027:** caupi com faixas de guandu ou gliricídia em nível (declive pelo NASADEM). Roçagem, palhada e aceiro, sem queima.
- **2028:** milho ou sorgo sobre a palhada da leguminosa, com caupi em revezamento.
- **2029:** mandioca, ou milho + caupi. As faixas perenes ficam.
- **Entressafra:** só palhada e perene de raiz funda.
- **Por que aparece:** é a única estratégia de rotação no sentido estrito e ataca nitrogênio, erosão, matéria orgânica e ciclo da lagarta ao mesmo tempo. **Não é o escudo do pior ano** (rodada 2).
- **Evidência:**
  - Leguminosa antecessora: +20% no cereal seguinte, +32% em baixa produtividade (Zhao et al. 2022), com efeito menor na zona árida (Franke et al. 2018). Grau B·T.
  - Rotação diversa: perdas 14–90% menores em ano seco, em clima temperado (Bowles et al. 2020). Grau B·T.
  - **O artigo-âncora puxa para baixo no semiárido:** em Kluger et al. (2025), o benefício do antecessor foi maior sob mais chuva, e a leguminosa antecessora rendeu menos sob calor. O sertão é seco e quente. Grau B·T.
  - Carbono: a agrofloresta recupera o carbono do solo em cerca de 10 anos, contra −50% com a queima (Primo et al. 2023, Sobral-CE; simulação de um sítio; grau C).
  - Chuva erosiva de fevereiro com I30 de até 80 mm/h (síntese 90.2; grau A).
- **No replay:** aparece hachurada, como faixa da literatura, sem número observado.
- **Benefícios:** milho de 2028 em diante sobre solo melhor; banco de proteína para as cabras; menos fogo e menos erosão; meses sem gramínea hospedeira.
- **Lacunas:** não existe ensaio revisado de rotação no semiárido do Ceará, e o PAM não identifica o efeito do antecessor (o placebo falha; seção 5). O efeito real da leguminosa é a lacuna que mais muda o ranking.
- **Riscos a confirmar:**
  - **competição por água, agora com dado:** na entressafra o primeiro metro de solo está seco (W < 0,1 em 49% dos dias), então a perene vive de água abaixo de 1 m, que o SMAP não vê. Pelo GLDAS Noah, a camada de 1–2 m tem ciclo de só 36 mm e acompanha o abril do mesmo ano (ρ +0,90): recarrega menos justamente no ano seco (`v2_agronomo_smap_janelas.saida.txt`, bloco E). A literatura dá cerca de −4% de rendimento com cobertura (Abdalla et al. 2019; grau B·T);
  - mão de obra para implantar e 1–2 anos para estabelecer;
  - se o caupi local é hospedeiro secundário da lagarta.

### 6.3 O plano vivo de 2027 para Dona Francisca

| Portão | O que o QUADRA diz | Evidência |
|---|---|---|
| **P1, hoje (14/nov)** | "O mar está mais quente do que em qualquer ago–out já medido. Num ano qualquer, 2 de cada 10 municípios da região perdem metade do milho; com o mar assim, cerca de 5 de cada 10 (faixa honesta de 2 a 8). Nos anos mais parecidos: 1998, 7 em 10; 2016, 7 em 10; 2024, menos de 1 em 10. O solo está seco como em todo novembro, e isso não diz nada sobre a quadra." Ações sem arrependimento: semente de caupi precoce e sorgo **até dezembro**, procurar maniva para fevereiro, garantir a palma, manter a adesão ao Garantia-Safra, aceiro e palhada em vez de queima. | Modelo único, ano fora: P(2,04) = 0,54 (IC90 0,24–0,75); em 2,46, 0,62 por extrapolação (`v2_clima_portao_novembro_2027.saida.txt`). Contagens: 4 de 7 quadras secas desde 1966 (proxy em 1966); 3 de 5 pelo POWER desde 1982; 2 de 3 catástrofes na era IMERG. O Pacífico esfriou a tempo em 1 de 7 El Niños fortes. Os anos do replay IMERG são **reponderados pela semelhança do oceano**: a NASA dá o ano, o mar dá o peso. SMAP de novembro → fevereiro: ρ +0,01. Banco regional normal (GRACE p57; CLSM p74). Quadra de 2026 úmida: há combustível. |
| **P2, janeiro–fevereiro** | "Plante uma parte agora e guarde a outra. Chuva boa em janeiro não garante a quadra: em 2016, janeiro teve cerca do dobro do normal e 7 de cada 10 municípios perderam o milho. Em jan–fev, vamos olhar o Atlântico." No fim de fevereiro: "ainda é cedo; nem a chuva nem o solo separaram os anos". | 31/jan: AUC 0,57 (28 anos); 0,27 (chuva) e 0,26 (SMAP) em 2016–2025. 28/fev: dentro do ano ~0,50 nas duas. Atlântico: exploratório, sem número. |
| **Início de março (~10/mar)** | "Com o mar deste ano, a metade guardada vai para o caupi até ~11 de março, a menos que as duas luzes estejam verdes. Confirmar com o técnico: a semente chegou?" | Caupi em 11/mar num ano como 2016: água na floração em 7 de 10 municípios; em 21/mar, 4 de 10 (SMAP e balde concordam; n = 2 anos; grau C). Na última década, a chuva de 19/mar teve AUC de só 0,55, abaixo do 0,67 que o oceano tem nos 28 anos (o oceano não foi medido só nessa década). |
| **P3, 19/mar** | Duas luzes: "chuva desde janeiro: {luz 1}; termômetro do solo: {luz 2}". Se uma acender: sorgo ou forragem na área que sobrou; caupi só se ainda couber. Se discordarem: "os dois instrumentos discordam; o técnico decide". | 28 anos: com a luz 1, 4 em 10 quebram; sem ela, 1,6 em 10. 2016–2025: luz 1, 1,0 contra 1,5; luz 2 (7 dias), 5,0 contra 1,2 (n = 124 alertas; quase metade de 2016); a leitura do dia dá 3,5 contra 1,3. Em Quixadá, as duas são fracas. O teste da tradição está na seção 7, inovação 4. |
| **P4, 30/abr** | "É aqui que o solo fala alto." Ação graduada: guardar forragem; segurar a venda dos animais; cortar o milho para as cabras se uma luz se repetir e o técnico confirmar. Sem salvamento com água: a cisterna de 16 m³ é de beber. | 2016–2025: com a luz do solo, 4 em 10 quebram; sem ela, 1 em 10. Em 2016, a soma pegou 9 das 127 quebras e o solo, 64. Em 2021, o solo acendeu em 81 municípios e 3 quebraram. **Em 30/abr só cabe salvar; por isso, em 2027, a proteção vem de P1, P2 e do início de março.** |
| **Junho** | "Verde do satélite em abril–maio: {x}% do normal do seu município. Quando ficou abaixo de 90%, 7 a 8 de cada 10 municípios perderam mais da metade do milho. O IBGE confirma no ano que vem." | VIIRS NDVI abr–mai, testemunha, grau A como testemunha (`v2_designer_verde_viirs.saida.txt`). |
| **P5, até 31/ago/2027 (data fixa)** | "O fogo vem pelo calendário; a decisão é antes de setembro." Palhada, aceiro, fenação do excedente se a quadra vier verde, perene em nível. Nova faixa de maniva na quadra de 2028 (fevereiro a abril). | 27% dos focos até 30/set e 72,9% em out–dez; o meio da temporada de fogo anda ~1 dia a cada 10 dias de secagem do SMAP (`v2_ecologo_calendario_fogo.saida.txt`). Combustível como mapa em tercis, sem previsão de focos. |

**Cartão da família no P1 (imagem; no máximo 3 números):** "Quixadá, 14 de novembro de 2026. O solo está seco como em todo novembro: isso é normal e não diz nada sobre a quadra. O mar está mais quente do que em qualquer agosto–outubro já medido. Num ano qualquer, 2 de cada 10 municípios da região perdem metade do milho; com o mar assim, cerca de 5 de cada 10. Agora: guardar semente de feijão-de-corda precoce e de sorgo, procurar maniva para fevereiro, não queimar. Confirmar com o técnico: a semente chega antes de 10 de março?" Rodapé: "Medido no seu município · Acertos contados na sua região · Grau B".

---

## 7. O que é inovador

1. **O calendário de decisão é derivado de três curvas medidas: habilidade, opções e visibilidade.** É a imagem do slide 3.
   - Habilidade: a chuva NASA sobe de AUC 0,57 (31/jan) a 0,80 (30/abr) em 28 quadras; o oceano fica em 0,67 desde novembro. **Na última década, a soma caiu para 0,55 e 0,66 nesses portões, e a segunda luz (o solo) fica em 0,59–0,68 em 19/mar e 0,77 em 30/abr.** Em 28 anos, a chuva passa o oceano no fim de fevereiro; em 2016–2025, a soma só chega a 0,66 em abril, e o solo, a 0,77 (o 0,67 do oceano é dos 28 anos; ele não foi medido só nessa década).
   - Opções: o milho cabe em 93% dos municípios em 28/fev, 42% em 19/mar e 0% em 31/mar. O caupi cabe em 98% em 19/mar e 41% em 31/mar. Em 30/abr, nada mais cabe (`arquiteto_final_curvas_quixada.saida.txt`, bloco B).
   - Visibilidade: o óptico a 30 m vê 79% em 28/fev, 71% em 31/mar e 92% em 30/abr (n = 24 AOI-anos); a 1 km, 39–40% dos pixels em jan–mar; **o micro-ondas do SMAP vê 13–15 dias por mês o ano todo.**
   - **19 de março é o último portão de troca; 30 de abril é onde habilidade e visibilidade são máximas, mas só cabe salvar.** Em ano de mar como o de 2027, a troca do caupi antecipa para o início de março, e a decisão se apoia no oceano.
2. **A soma engana; o estado, não (novo).** A regra de chuva desde 1/jan carrega o janeiro chuvoso até abril. A segunda luz (água na zona da raiz, SMAP L4) pegou, em 30/abr de 2016, 64 das 127 quebras que a soma perdeu (pegou 9). O teste fora da amostra, com o estado da chuva do IMERG no lugar do SMAP, mostra que a ideia vale também em 1998–2015 (71% contra 52% em 19/mar, mesma precisão). O recibo diz que o ganho é do **estado** da água, que o SMAP L4 é modelo + radiômetro e que a chuva recente do IMERG faz quase o mesmo.
3. **Teste de estresse de rotações no registro da NASA, com o IBGE como árbitro.**
   - Cada estratégia é reencenada nas 28 quadras do IMERG e ordenada pelo pior ano.
   - O replay põe lado a lado a estimativa da NASA e o observado do IBGE.
   - O replay de 1998 mostra a decisão mudando: o oceano avisa em novembro, janeiro engana, São José abre a janela de troca dois dias antes da data-limite do caupi, e o IBGE revela o resultado. **O replay de 2016 (novo)** mostra a soma dizendo "tudo bem", o solo dizendo "não", o verde do VIIRS testemunhando em junho e o IBGE julgando.
4. **Honestidade como funcionalidade.**
   - Recibo A–D com a marca de evidência transferida (·T).
   - Placar do alerta por município, com erros, **para cada luz** (em Quixadá, a luz do solo nunca acertou).
   - **Toda curva por era**: a regra que funcionou em 1998–2015 e falhou em 2016–2025 aparece assim.
   - **Leitura menos favorável no slide** quando duas leituras divergem (64, não 90).
   - Auditoria com a inflação da validação aleatória (R² 0,49 contra −0,08) e com os resultados nulos: SMAP de novembro, combustível no total do ano, NDVI no portão, IA causal no PAM.
   - O sentinela, que sinalizou a deriva do Terra, o relato copiado no PAM, o NDVI deslocado nos dois sensores e o percentil do SMAP que some na seca.
5. **Saber local testado com respeito: o "Checkpoint São José".**
   - A tradição diz que chuva no dia de São José (19/mar) garante o inverno. O teste justo compara com o **resto** da quadra (20/mar–31/mai): a chuva do dia e todo o acumulado até ali dizem a mesma coisa, de forma fraca (ρ estadual +0,32 nos dois; n = 28; p ≈ 0,1; `cetico_r3_sao_jose_mandioca.saida.txt`, bloco A).
   - A tradição é fraca, não errada. **E em 19/mar nem o solo decide ainda** (rodada 2): o SMAP no dia de São José empata com a chuva e, sem 2016, fica abaixo do acaso. São José marca a última janela de troca; quem fala alto é o solo de 30 de abril.
6. **Dois relógios da água e um portão de entressafra.**
   - O solo responde em semanas a poucos meses (a anomalia da zona da raiz cai a 1/e em 38–46 dias, agrupando os anos; dentro de uma mesma quadra, em cerca de 2 semanas). A água subterrânea lembra por 8 a 13 meses. O relógio lento roda na memória de chuva do IMERG, com GRACE e GLDAS como segunda missão.
   - A entressafra, onde no sertão de fato se decide a rotação, vira um portão **de prática com data fixa** (até 31/ago): palhada em vez de fogo, aceiro, nova faixa de maniva na quadra seguinte e perene em nível.
7. **A pergunta de Stanford no semiárido (novo).** Kluger et al. (2025) mediram, com satélite e florestas causais, como o benefício da rotação muda com o clima em celeiros temperados. O QUADRA leva a pergunta para onde ela não foi feita (sequeiro tropical, sem mapa oficial de culturas) e acrescenta o que eles não têm: os dados de água da NASA e o **momento** da decisão.

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
| Veranico e perda | Rocha et al. 2021, RBMet 36:579–589 | Veranico explica a perda; milho + feijão = 91% da área. [B, Nordeste] |
| Oceano como probabilidade | Kayano & Andreoli 2006, JGR 111:D13101; Nobre & Shukla 1996, J. Climate 9:2464 | O ENSO sozinho acerta 36%; o Atlântico condiciona a ZCIT. [B] |
| Previsão empírica de referência | Rocha Júnior et al. 2021, Water 13:1613 | Modelo empírico simples é competitivo no Nordeste. [B] |
| Seca e adaptação | Marengo et al. 2018, An. Acad. Bras. Ciênc. 90:1973; Marengo et al. 2021 | A seca de 2010–2016; adaptação ainda pós-desastre. [B] |
| Leguminosa antecessora | Zhao et al. 2022, Nat. Commun. 13:4926; Franke et al. 2018, AGEE 261:172 | +20% (+32% em baixa produtividade); menor no árido. [B·T] |
| Resiliência pela diversidade | Bowles et al. 2020, One Earth 2:284; Renwick et al. 2021, ERL 16:084067; Beillouin et al. 2021, GCB 27:4697 | Perdas menores em ano seco (Bowles: 14% a 90%; Renwick: ~17% menos perda do milho na seca, ligada à matéria orgânica), efeitos variáveis. [B·T] |
| Consórcio e forragem | Himmelstein et al. 2016; Mudare et al. 2022 [B]; Souza et al. 2011, Bragantia 70:715 [C, ensaio único]; Diniz et al. 2017, PAB [C, ensaio irrigado único] | Consórcio +23% na África; LER > 1; milho + caupi em Petrolina; palma + sorgo. |
| Cobertura: custo | Abdalla et al. 2019, GCB 25:2530 | Cerca de −4% na cultura principal e custo de água. [B·T] |
| Fogo, pousio e carbono | Primo et al. 2023, J. Environ. Manage. 336:117594 [C, simulação de um sítio]; Salcedo et al. 1997; Cano-Crespo et al. 2015 [B] | −50% de C em 10 anos sem pousio; fuga do fogo para vizinhos. |
| Área queimada a 30 m | Franca Rocha et al. 2024, Fire 7:437 | 12,7% da Caatinga queimou em 1985–2023 (MapBiomas Fogo). [A, regional] |
| Combustível da quadra anterior | Argibay et al. 2020, Ecol. Indic. 113:106151; Bezerra et al. 2025, Atmosphere 17:46 | Ano úmido seguido de ano seco gera grandes queimadas. [B] |
| Quebra de ciclo de praga | Ratnadass et al. 2011; du Plessis et al. 2020, Insects 11:228; Azambuja & Degrande 2014 | Ruptura temporal de hospedeiro; graus-dia da lagarta (Tb 12,57 °C; K 390,8 GD); vazio sanitário do algodão. [B] |
| Satélite térmico e solo raso | Anderson et al. 2016, RSE 174:82; Rossato et al. 2017; Fisher et al. 2020, WRR 56 | ESI e ECOSTRESS: base do item de roteiro. |
| SMAP L4 | Reichle et al. 2019, JAMES 11:3106; produto SPL4SMGP v8 (Reichle et al. 2025, doi 10.5067/T5RUATAQREF8) | Erro sem viés de 0,026 m³/m³ na zona da raiz (avaliação da v4). |
| SMAP L4: forçante de chuva | Reichle et al., EGU23-1419 (resumo de congresso; https://meetingorganizer.copernicus.org/EGU23/EGU23-1419.html) | Desde a v6 do L4_SM, fora da América do Norte, a chuva da forçante é corrigida para os totais diários do IMERG. Usado só para descrever a dependência no recibo; a v008 não foi conferida. [D como fonte] |
| SMAP L3 | O'Neill et al. 2023, SPL3SMP_E v6, doi 10.5067/M20OXIZHY3RJ | Observação do radiômetro em banda L a 9 km. |
| GRACE e reservatórios | Gonçalves et al. 2020, STOTEN 705:135845; Lima et al. 2020; Melati et al. 2019 | GRACE com r = 0,78 contra o volume dos açudes do Nordeste. [B] |
| POWER e IMERG no mundo | Van Wart et al. 2015, AFM 209–210:49; White et al. 2008, AFM 148:1574; Rozante et al. 2018, Remote Sens. 10:882 | Clima de satélite alimenta modelos de cultura; viés da Tmax do POWER; o IMERG subestima o litoral do Nordeste. |
| HLS | Claverie et al. 2018, RSE 219:145 | Landsat e Sentinel-2 harmonizados a 30 m. |
| Fenologia | Arvor et al. 2011, IJRS 32:7847 | Séries de EVI/NDVI detectam ciclos no Brasil. |

**Os números do artigo-âncora** (ganho mediano de ~4,5% de uma rotação de 2 culturas; ganho ~3,7 vezes maior que o de diversificar ainda mais) **constam no texto do arXiv v2 em disco**, mas não foram conferidos na versão publicada da ERL. Ficam fora dos slides até essa conferência. No slide entram só os achados qualitativos do resumo.

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

**Leitura que vai para o deck:** o padrão "mais diverso perdeu menos" aparece nas duas grandes secas do Ceará e some em anos normais. Mas ele é sobretudo **menos dependência de milho + feijão** e de culturas fora do sequeiro (melão, soja e sorgo tecnificados, segundo o cético); entre as culturas de sequeiro, o efeito desaparece. Isso é coerente com o achado (ii) do artigo-âncora (diversificar além da rotação simples rende pouco) e com o (iii) (benefício menor com pouca chuva). **Por isso o QUADRA não promete bônus de diversidade: ordena cada rotação pelo pior ano observado.** É associação municipal num episódio, não efeito de rotação no talhão. Grau B.

### 8.3 Como o método do artigo-âncora entra no roteiro

O protótipo municipal mostrou por que a escala tem de ser o talhão: no PAM, o efeito do feijão anterior e o do feijão futuro (placebo) têm o mesmo tamanho (`v2_pesquisador_ia_precrop_dml.saida.txt`). O desenho do próximo passo, à maneira de Kluger:
1. **Unidade:** pixel ou talhão de 30 m, não o município.
2. **Tratamento:** a sequência em t−1 (roçado após pousio, roçado repetido, após leguminosa), tirada do MapBiomas anual (classes a conferir: o roçado do semiárido tende a cair em "mosaico de usos") ou de uma classificação HLS calibrada nas proporções do PAM.
3. **Desfecho:** pico de NDVI ou EVI (HLS/Landsat/VIIRS) calibrado contra o rendimento do PAM por município, como Kluger fez com condados.
4. **Modificadores:** o estado da água nos portões (SMAP L4, API do IMERG), ET0 do POWER, relevo do SRTM e ONI. É aqui que entra o que o artigo não tem.
5. **Validação:** floresta causal honesta com cross-fitting por bloco de anos, teste de calibração, placebo do antecessor futuro e IC por ano.

---

## 9. Validação honesta e limitações

### 9.1 Protocolo, igual para toda a equipe

- **A unidade independente é o ano**, não o município-ano. Os resíduos se correlacionam por centenas de km (`pesquisador_ia_hierarquico.py`).
- **Toda variável de nível anual** (ONI, dipolo, GRACE regional) tem erro-padrão agrupado por ano. Município-anos não são réplicas.
- **Validação:** toda métrica sai de uma destas três: deixando o ano inteiro de fora (LOYO); walk-forward, só com o passado; deixando o episódio de seca de fora, com 2012–2017 como um bloco.
- **Seleção aninhada:** toda escolha de regra, limiar, análogo ou configuração é aninhada. Escolher pelo resultado do teste é proibido (correção do M2 no bloco 0).
- **Toda AUC** é decomposta em entre anos e dentro do ano.
- **Os intervalos** vêm de bootstrap por ano. O recibo mostra o n efetivo.
- **Comparação:** toda comparação de modelos é **pareada**, com as mesmas entradas e as mesmas dobras.
- **Toda estratégia** é avaliada contra o **rendimento observado do PAM**, nunca contra o ISNA do próprio balde.
- **Regras novas da rodada 2:**
  - **Por era:** toda curva e todo alerta aparecem também em 1998–2015 e 2016–2025. A curva agregada sozinha esconde que a regra de chuva falhou na última década.
  - **Leitura menos favorável:** quando duas leituras igualmente razoáveis do mesmo dado divergem (ex.: SMAP no dia × média de 7 dias), o slide usa a menos favorável, e o recibo mostra a outra.
  - **Contra a geografia:** toda vantagem "dentro do ano" é comparada com uma linha de base só de geografia (o mapa de risco de base do município). Foi esse teste que rebaixou o ISNA e suspendeu o 0,307 do M2.
  - **Sem AUC agregada de probabilidades LOYO com poucos anos:** com 10 anos, a climatologia LOYO sozinha dá AUC 0,154 (o intercepto cai quando o ano de teste é seco). Usar escore sem intercepto, a variável crua ou a AUC dentro do ano.
  - **Limiar de dado novo fixado antes:** o 20 do SMAP veio da seção 05 do notebook, escrito antes dos testes; o τ = 13 d do API veio da autocorrelação do SMAP, medida sem olhar a quebra.
  - **Diagnóstico sem 2016:** todo ganho da era SMAP é mostrado também sem 2016, que responde por 47% das quebras de milho da década (`v2_pesquisador_ia_smap_escore.saida.txt`).

### 9.2 Números de cabeçalho, os únicos que vão para os slides

| # | Afirmação | Valor | Validação | Fonte | Grau |
|---|---|---|---|---|---|
| 1 | No registro do PAM, milho e feijão quebram juntos | ρ mediano 0,78 (0,67 sem o choque do ano) | Descritivo, 183 municípios | `arquiteto_numeros_canonicos.txt`; `cetico_r3_refutacoes.saida.txt` F | A |
| 2 | A chuva NASA aprende durante a quadra; o oceano sabe pouco desde novembro | AUC 0,57 (31/jan) → 0,73 (19/mar) → 0,80 (30/abr; IC90 0,73–0,85) em 28 quadras; oceano 0,67 (0,53–0,78); dentro do ano ≤ 0,57 | LOYO do normal + bootstrap por ano | `arquiteto_final_curvas_quixada.saida.txt` A | A |
| 3 | **Mas a soma desde 1/jan falhou na última década** | 30/abr: AUC 0,83 (1998–2015) → 0,66 (2016–2025); com alerta, 5,9 → 1,1 em 10 quebram; sem alerta, 1,5 nas duas eras | Por era, mesma regra | `v2_arquiteto_arbitragem_smap.saida.txt` E | A |
| 4 | **A segunda luz, o solo, viu o que a soma perdeu** | 30/abr, 2016–2025: AUC 0,77 contra 0,66 (dif. +0,11; IC90 por ano −0,02 a +0,17); com a luz, 4 em 10 quebram, sem ela 1 em 10; 2016: **64 de 127** contra 9 (90 na leitura do dia); 2021: 81 alertas e 3 quebras | Pareado, bootstrap por ano, leitura menos favorável; reproduzido por 4 scripts | `v2_arquiteto_arbitragem_smap.saida.txt` A–D; `v2_hidrologo_smap_portoes_quebra.saida.txt`; `v2_estrategista_smap_portoes.saida.txt`; `v2_cetico_smap_portoes.saida.txt` | B |
| 5 | A ideia das duas luzes vale fora da era SMAP | 1998–2015 (API do IMERG como luz 2): em 19/mar, pega 71% das quebras contra 52%, com a mesma precisão (4,7 em 10) | Fora da amostra, com substituto | `v2_agronomo_smap_contraprova.saida.txt` (e) | B |
| 6 | As opções fecham | Milho cabe em 93% (28/fev) → 42% (19/mar) → 0% (31/mar) dos municípios; caupi em 98% (19/mar) | Simulação, ±1 decêndio | `arquiteto_final_curvas_quixada.saida.txt` B; `arquiteto_final_zarc_et0_sensibilidade.saida.txt` | C |
| 7 | A validação aleatória infla | R² 0,49 contra −0,08 | Aleatório contra LOYO | `cetico_escala_vazamento.py` | A |
| 8 | Um terço em mandioca protege a cauda | "Pior ano em 10" 0,15 → 0,36 (ganho com IC90 +0,17 a +0,23); chance de < 50%: 21% → 11%; piso de 0,32 se a maniva faltar | 2.495 município-anos onde a mandioca existe; intenção de tratar nos 91 municípios de mandioca | `arquiteto_final_carteira_ic.saida.txt`; `v2_economista_diversidade_carteira.saida.txt` C | A |
| 9 | O mar de 2027: mais chance, não certeza | Cerca de 5 em 10 municípios com quebra do milho, contra 2 em 10 num ano qualquer (P(2,04) = 0,54; IC90 0,24–0,75); análogos: 1998 7,5 em 10, 2016 7 em 10, 2024 menos de 1 em 10 | Modelo único, ano inteiro fora; contagem | `v2_clima_portao_novembro_2027.saida.txt` A–C | B |
| 10 | Os satélites sabem o ano, não o município | Dentro do ano, IMERG, SMAP e GLDAS ficam entre 0,47 e 0,60; a vantagem do ISNA é geografia (0,613 contra 0,612) | Dentro do ano, contra só geografia | `v2_hidrologo_smap_portoes_quebra.saida.txt`; `v2_economista_gatilho_smap.saida.txt` | A |
| 11 | O óptico fica cego nas datas de decisão; o micro-ondas não | NDVI VIIRS bom em 39–40% dos pixels em jan–mar (95–96% em ago–out); SMAP vê cada célula 13–15 dias por mês | Descritivo | `v2_sr_fundacao_viirs_portoes.saida.txt` A; `v2_sr_fundacao_smap_l3_l4.saida.txt` A | A |

**Proibido no deck:** qualquer número que use outra definição de quebra, outra regra de alerta, outro limiar do SMAP, a leitura mais favorável quando há duas, ou comparação não pareada. **Saíram dos slides na rodada 2:** o "ρ 0,155 → 0,307" do M2 (suspenso), o "+6,6 p.p." como bônus de diversidade, o "+0,072" do fogo e a frase "em 19/mar o que decide é a água no solo".

### 9.3 Onde erramos, e mostramos

- **2012:** pego tarde. Em 19/mar, o alerta pegou 40% das quebras; em 30/abr, 91% (123 de 135). Quando acende, já só cabe salvar.
- **2016, o análogo de 2027: perdido pela soma, pego pelo solo em abril.** Em 30/abr, a soma pegou 9 de 127; o solo, 64 (90 na leitura do dia). Em 19/mar, 6 contra 47 (32 no dia). Janeiro teve cerca do dobro do normal. Mesmo pego, em 30/abr só cabe salvar.
- **2021, o alarme falso das duas luzes:** em 30/abr, o solo acendeu em 81 municípios e a chuva em 107; só 7 quebraram.
- **2025:** a soma pegou 1 de 45; o solo, 21.
- **2024:** El Niño forte sem quebra estadual (8%), com o Atlântico recorde de quente. Em Quixadá, o milho quebrou (0,46) com chuva normal, solo úmido, verde normal e nenhum vizinho em quebra.
- **Quixadá 2023–2025:** 2025 foi água no fim da quadra; 2023, provavelmente chuva que parou em maio (com vizinhos em quebra); 2024 não tem assinatura NASA (seção 6.2). Na auditoria, como "o satélite discorda do árbitro".
- **Quixadá, luz do solo:** nenhum acerto em 2016–2025 com o limiar canônico (seção 6.2).
- **O balde:** superestima 2010 e 2013; o ISNA de cultura não vê 1998 nem 2001 (o estado em percentil vê 1998, grau C).
- **Alarmes falsos:**
  - em 30/abr (28 anos), 48% dos alertas de chuva caem em municípios sem quebra; com a luz do solo (2016–2025), 60%;
  - em 28/fev, 68%, e por isso fevereiro não tem alarme;
  - o "60% das famílias sem alerta em 3 anos" (`designer_confianca_alertas.txt`) foi medido com uma luz só e será refeito, porque as duas luzes acendem mais.
- **Anos de excesso** (2009, 2024): o balde não modela encharcamento.
- **2026, discordância aberta:** o SMAP marcou p39 em 19/mar e p35 em 30/abr, com a chuva a 110% e 105% do normal. Só o PAM de 2026 (que sai em 2027) arbitra; o VIIRS de mar–mai indica safra perto do normal (mediana 1,031 do normal; `v2_estrategista_viirs_quixada.saida.txt`).
- **Gatilho tipo Garantia-Safra (auditoria):** com o IMERG em fev–mai, o risco de base no município fica perto de 50% nos dois sentidos: metade das perdas não é paga e metade dos pagamentos vai para quem não perdeu (`v2_economista_gatilho_smap.saida.txt`).

### 9.4 Grau de evidência por tipo de afirmação

| Grau | O que é | Exemplos |
|---|---|---|
| A | Validado com dado local observado, por ano | Correlação entre culturas no PAM, curva de habilidade por era, regra de chuva, carteira estadual e seu piso, continuidade VIIRS × MODIS |
| B | Meta-análise ou síntese multi-sítio; poucos anos ou poucos episódios com dado local | Segunda luz do SMAP (10 quadras, 1 grande seca), duas luzes fora da amostra (com substituto), P1 do oceano, El Niño × quebra (contagem), associação diversidade × resiliência |
| B·T | B transferido de outro clima (meio grau abaixo) | Leguminosa antecessora, rotação diversa, achados de Kluger et al. 2025, custo da cobertura |
| C | Modelo, simulação, ensaio único, ordem validada sem nível | Datas-limite sintéticas, troca do caupi até 11/mar em ano de luz acesa, janela da maniva, balde em percentil em 1998, ponte verde, palma + sorgo, carbono de Primo, açude numa AOI |
| D | Suposição ou resumo de congresso | Volume de cisterna suposto, preço de forragem, forçante do SMAP L4 v008 (só por resumo do EGU) |

### 9.5 Limitações

1. **Nenhum efeito de rotação foi observado no Ceará.** O PAM valida o efeito do clima sobre cada cultura, não o do antecessor. O protótipo de IA causal confirma: o placebo do antecessor futuro dá o mesmo efeito.
2. **A habilidade é regional.** Tudo foi calibrado no município (o PAM é estimado pelo IBGE e pela Ematerce), e a decisão é do roçado de 1–5 ha. Dentro do ano, a AUC fica em ~0,60 ou menos para todas as camadas.
3. **2027 está fora da distribuição** (ONI ASO 2,46 contra o máximo de 2,04). Toda probabilidade é extrapolação, com 3 a 7 análogos.
4. **Poucos episódios.** A era SMAP tem 10 quadras, e 2016 responde por 47% das quebras de milho da década (2016 + 2025 = 64%). Sem 2016, o SMAP em 19/mar fica abaixo do acaso. A cauda da carteira vem de cinco a sete anos ruins desde 1998. Todo IC é largo.
5. **O SMAP L4 não é independente do IMERG.** É um modelo forçado pela chuva corrigida para o IMERG e corrigido pelo radiômetro. A chuva IMERG dos últimos 15 dias iguala o SMAP em 30/abr (0,80 contra 0,77; linha de base criada depois, num teste só). Dizemos "o estado da água", nunca "dois satélites independentes concordam".
6. **A climatologia do percentil do SMAP não foi conferida** (só 13,2% dos município-dias abaixo de p20). Os valores de 2016 vêm do reprocessamento v008 de hoje, não do que existia em 2016: o slide diz "would have flagged with today's product".
7. **"Dados de água da NASA" não são uma verdade única no município:** GLDAS Noah e IMERG mal concordam sobre onde a seca de 2012–16 foi pior (ρ +0,09; `v2_agronomo_diversidade_robustez.saida.txt`); os níveis de umidade diferem até 0,10 m³/m³ entre produtos.
8. **A área plantada se adapta** ao ano: ρ com o ONI de NDJ de −0,43 no milho (`cetico_r2_checagens.py`, bloco C).
9. **Qualidade do PAM por cultura.** A mandioca tem relato repetido e ciclo longo; o feijão mistura Phaseolus e caupi; o sorgo é tecnificado e tem n pequeno.
10. **Escala da água azul.** A família típica de sequeiro não tem água para salvar o roçado.
11. **Sem custo de produção.** A renda é normalizada e bruta.
12. **Regras institucionais não conferidas:** o limiar do Garantia-Safra (40% ou 50%), a cesta, a área mínima e a janela do ZARC oficial de Quixadá. Sem conferência, não entram em slide.
13. **Muitos testes sobre os mesmos anos.** A rodada 2 somou dezenas de comparações às da rodada 1. Só os números da tabela 9.2 vão ao pitch; o resto (TSA do Atlântico, dipolo × início, combustível × fogo, "ONI além da chuva", regra de 15 dias de chuva) é exploratório.

### 9.6 Testes que dão para fazer antes do júri

- **Conversa com um técnico de ATER ou um agricultor** (José; seção 10). Vale mais para o Impacto do que qualquer teste novo.
- **Bloco 0:** seleção aninhada do M2; o ρ dentro do ano do M2 contra a linha de base só de geografia; a coluna "chuva + oceano (logística)" com a regra anti-artefato; IC por ano do alerta de 30/abr por era.
- **SMAP L3 consolidado** (chegou às 10:06): refazer a checagem do cético com o arquivo completo, inclusive a contagem de 2016 em 30/abr na observação.
- **Documento do SMAP L4 v008:** conferir a base da climatologia do percentil e a forçante de chuva da versão 8.
- **Kluger et al. 2025:** conferir na versão publicada da ERL os números do arXiv (4,5% e 3,7×) antes de qualquer slide numérico.
- **Pré-registro interno** da regra de duas luzes para 2027 (limiar 20, média de 7 dias, P3 e P4). O hash público **só com o OK explícito do José**, porque é voz pública; o mesmo vale para a leitura VIIRS da safra de 2026 ("perto do normal").
- Refazer `designer_confianca_alertas` com as duas luzes.
- Cortados por custo ou dependência: FIRMS NRT (exige chave), LSPA, código de barras contra o CDL do Texas, SMAP ao vivo.

### 9.7 Folha de números canônicos e erratas (obrigatória antes do deck)

**Números canônicos:**

| Item | Valor canônico | Não usar |
|---|---|---|
| ONI | ASO/2026 = +2,46; recorde para ago–out (antes 2,04, em 1997); recorde absoluto 2,59 (NDJ 2015) | "o El Niño mais forte da história"; "2,14"; "2,31" |
| Risco de 2027 (P1) | ~5 em 10 municípios com quebra do milho (P(2,04) = 0,54; IC90 0,24–0,75), contra 2 em 10; em 2,46, 0,62 só com selo de extrapolação; análogos 1998 0,75, 2016 0,70, 2024 0,08 | "62% de chance" sem o selo; uma média sem os três anos |
| Análogos | 4 de 7 desde 1966 (proxy em 1966); 3 de 5 pelo POWER desde 1982; 2 de 3 catástrofes na era IMERG | "de cada 10 anos como este" |
| GRACE e banco lento | GRACE CE jul–set/2026 no p57 (jun–ago: p70); GWS do CLSM jun–ago/2026 no p74 (assimila o GRACE) | "caiu para p35"; "reserva caindo"; o r 0,88/0,95 do CLSM × GRACE como validação |
| SMAP hoje | Zona da raiz do CE 0,121 m³/m³ em 10/11/2026, 5º novembro mais seco de 12; Quixadá 0,087; percentil do produto vazio | qualquer percentil do produto entre ~12/ago e ~12/jan |
| Luz 2 (SMAP) | Percentil da zona da raiz do SMAP L4 < 20, média dos 7 dias até o portão | limiar 25; leitura do dia como número principal; "mais seco que 8 de cada 10 anos" |
| 2016, 30/abr | Chuva 9 de 127; SMAP 64 de 127 (90 na leitura do dia); 2021: 81 alertas, 3 quebras | "90" sem "on the day itself"; 2016 sem 2021 |
| Regra de chuva por era | 30/abr: AUC 0,83 (1998–2015) e 0,66 (2016–2025); com alerta 5,9 e 1,1 em 10; sem alerta 1,5 nas duas | a curva agregada sozinha |
| SMAP em 19/mar | 0,59 (dia) a 0,68 (7 dias), contra 0,55 da chuva; sem 2016, abaixo de 0,5 | "o solo decide em São José" |
| Memória do solo | Anomalia da zona da raiz cai a 1/e em 38–46 dias, agrupando os anos; ~2 semanas dentro de uma quadra | "o solo esquece em 13 dias" ou "em 6–8 semanas" sem a definição |
| ET0 do CE | 1.970 (ERA5) a 2.280 (POWER) mm/ano; 2,5 a 2,8 vezes a chuva da mesma fonte; supera a chuva em 10 de 12 meses nas duas | Um valor único chamado de "correto" |
| Ureia/milho | 1,85 em out/2026; pico de 4,00 em abr/2026; média de 2000–2020 = 1,51 (`cetico_r2_ureia.py`) | "4,0 agora" |
| Quebra | Produção ÷ área plantada < 50% da mediana do município nos outros anos; milho 21,5% e feijão 14,6% (1998–2025) | Mediana móvel; área colhida; limiar de 60% |
| Alerta de chuva | IMERG desde 1/jan < 75% do normal (mediana dos outros anos) | "3,8 contra 1,1"; "33 alertas, 31 acertos"; padrão "011"; janela fev–mai como regra principal (seria escolha pós-teste) |
| Milho 2012 | −69% no estado; 75% dos municípios em quebra | "71%", "50%" |
| Registro de chuva | IMERG (eras TRMM e GPM), 28 quadras 1998–2025; POWER 1981–2026 é reanálise (MERRA-2 corrigida) | "28 years of GPM"; "44 quadras observadas" |
| Carteira | CVaR10 0,15 → 0,36 (teto); piso 0,32 nos municípios de mandioca; mundo real ~65% do ganho por cultura; cauda de 5 a 7 anos ruins | "três episódios"; somar o +6,6 ao CVaR |
| Diversidade | +6,6 p.p. nas secas (+10,5 em 1998; 0,0 no placebo), sobretudo composição; só sequeiro +1,4 (n.s.) | "more diverse crops kept 6.6 points more yield" sem a ressalva; "diversificar o sequeiro protege" |
| Fogo | 72,9% dos focos em out–dez e 27% até 30/set (2015–2025); 17% da área do CE em células de ~375 m com ≥ 1 foco (2012–2025); combustível +0,02 sobre a tendência, sem habilidade no total do ano | "17,4% do Ceará queimou"; "+0,072"; número de focos previstos para 2026 |
| VIIRS NDVI | Continuidade do MODIS (r 0,986 no estado); testemunha de fim de safra (AUC ~0,8; abaixo de 90% do normal, 7,5 em 10 quebram); nov/2026 provisório | "o NDVI decide no portão"; "seu talhão contra os vizinhos" com 1 km |
| Deslocamento do NDVI | +0,03 a +0,05 desde 2020 nos dois sensores com a chuva IMERG; ~0,01 próprio do MODIS; causa aberta | "deriva do Terra" como causa principal |
| Kluger et al. 2025 | Achados qualitativos do resumo | "4,5%" e "3,7×" até conferir na versão publicada |
| Pontos globais | 40 de 47 pontos terrestres tropicais sem mês de quebra térmica | "86% dos trópicos" |

**Erratas da rodada 2 (sobre a v1):**
- **"Em 19/mar, o que decide é a água que já está no solo"** (slide 1, seção 7.4 e P3 da v1): o teste direto não sustenta. Sai.
- **"2016 perdido; só o oceano avisou":** vira "perdido pela soma; o solo viu em 30/abr".
- **Regras R4, R5 e R8 "(SMAP)":** eram balde de solo nu. Renomeadas.
- **"No milho, o ISNA soma +0,04":** dentro do ano, é geografia. O ISNA vira mapa de risco de base.
- **"M1 não vê 1998":** é a formulação do ISNA de cultura; o estado em percentil vê (grau C).
- **"+0,072" do combustível:** era tendência. Vira +0,02 sobre a tendência.
- **"SMAP: percentil da zona da raiz, sempre":** o percentil do produto não existe de ~12/ago a ~12/jan no sertão; percentil próprio nesse período.
- **"Pipeline pronto: SMAP L4"** (slide 5 da v1): o SMAP é usado.
- **"A cauda vem de três episódios":** são cinco a sete anos ruins.
- **"Deslocamento não explicado do NDVI", com suspeita de deriva do MODIS:** aparece também no VIIRS; a causa principal não é o Terra.
- **"MODIS até nov/2026, buraco de jun–nov/2025":** no arquivo mensal, o MODIS vai até set/2026, e a lacuna real é jul–out/2025.
- **Frase de pitch "+6,6 points" de `pesquisa/artigo_ancora_objetivo.md`:** só com a ressalva da seção 8.2.

**Erratas da rodada 1 (mantidas):**
- **ET0:** o ~1.960 mm/ano da síntese é a ET0 do ERA5, e os 2.279 mm/ano do rascunho são a do POWER. Os dois estão certos; a diferença de 15% vem do viés quente da Tmax do POWER.
- **OR 2,30 do El Niño:** era o termo de uma interação e tinha erro-padrão iid. Sai.
- **Início da estação (ρ −0,67):** é retrospectivo e mecânico. O início causal tem ρ ≈ 0 com a chuva restante. Sai a regra de fevereiro.
- **"2025, o ano mais verde"** é artefato do MODIS Terra.
- **"Fogo cerca de 6 meses depois de anos verdes":** o sinal forte é a quadra do ano anterior.
- **"O combustível explica metade da tendência do fogo":** duas séries com tendência em 14 anos não sustentam atribuição. Sai.
- **"IMERG Late da estação seca −0,5 dp" como motivo de alarme:** a chuva da estação seca não prevê a quadra (ρ −0,06 na rodada 1; ρ −0,22, n.s., na janela de 01/ago–13/nov da rodada 2). Sai de "por que agora".
- As elasticidades com mediana móvel curta estão subestimadas: o milho é +13,8%/100 mm (`pesquisador_ia_hierarquico.py`).

---

## 10. Plano de MVP para as ~37 h restantes

**Orçamento (recalculado pelo cético na rodada 2):** a demanda é de cerca de **44 horas-pessoa** com 25% de contingência: a tabela da v1 (25,5–27,5 h), o bloco 0 fora dela (+3 h), o mínimo dos dados novos (+3,5 h: export do SMAP por portão e 1 gráfico com recibo, 1,5 h; VIIRS como continuidade, 0,5 h; diversidade + Kluger com ressalvas, 0,75 h; folha canônica, 0,75 h) e a conversão do site atual para estático (+2 h). **Com 2 pessoas, a oferta é de ~51 h (folga de ~7 h). Com 1 pessoa e agentes, ~25,5 h: faltam ~18 h e o corte é imediato** (ver abaixo). Qualquer dado novo além do mínimo estoura.

| Tarefa | Horas |
|---|---|
| Exportador (inclui o SMAP por portão, a deduplicação e o percentil próprio de novembro) | 4,5 |
| Trajetórias diárias | 1,5 |
| App (inclui converter o `site-nasa` atual para página estática) | 10–12 |
| Textos e verificador | 2 |
| Auditoria | 2 |
| Slides | 4 |
| Vídeo | 3 |
| Checagem cruzada | 2 |
| Bloco 0 | 3 |

**Decisões atrasadas (eram até as 10h de sábado):** tamanho da equipe e papéis, nome e esta folha canônica. Sem a decisão do tamanho da equipe, vale o plano de 1 pessoa.

**Papéis:**
- **P1, Motor:** exportador e JSON.
- **P2, App:** página estática HTML + JS + Plotly, com GeoJSON dos 184 municípios e sem mapa base.
- **P3, Ciência e recibo:** bloco 0, recibos, auditoria e texto de SI.
- **P4, Narrativa:** slides e vídeo.

Com 2 pessoas: P1+P3 e P2+P4.

**Arquitetura:**
- **Não empacotar nem importar os scripts do conselho.** Importar executa o script e sobrescreve `conselho/analises/saidas/`.
- Um único `motor/exportar.py` **lê as saídas já salvas**:
  - `agronomo_zarc_sintetico_prob.parquet`;
  - `agronomo_isna_mun_ano.parquet`;
  - `hidrologo_fao56_mun_ano.parquet`;
  - **`v2_hidrologo_smap_pctl_mun_diario.parquet` e `v2_hidrologo_smap_rz_mun_diario.parquet`** (SMAP municipal diário, já deduplicado), para a média de 7 dias por portão e o percentil próprio de novembro;
  - o cache de chuva diária e o PAM.
- Ele **copia** (não importa) só a função `simular()` para gerar as trajetórias diárias de 3 municípios × 3 anos.
- Sai um JSON por município (184) e por ponto global (2 a 3). **A página é estática e não chama nenhuma API ao vivo.** O `site-nasa/` atual (Flask, geocodificação ao vivo no Nominatim e globo 3D, ~1.800 linhas) contraria isso e não roda no GitHub Pages: a geocodificação vira uma lista local dos 184 municípios, e o globo sai ou vira imagem.

| Bloco | Quando | Quem | Tarefa | Pronto quando |
|---|---|---|---|---|
| 0 | Sáb 11–14h | P3 (+ todos às 11h) | Congelar a folha 9.7. Seleção aninhada do M2 e o M2 contra só geografia. Coluna logística do M3 com a regra anti-artefato. IC por ano do alerta por era. Esquema do JSON (portões, duas luzes, estratégias, recibos). | Ninguém usa número fora da folha. |
| 1 | Sáb 11–15h | P1 | `motor/exportar.py`: duas luzes por portão e município (2015–2025, média de 7 dias, com o dia na auditoria), percentil próprio de novembro, trajetórias diárias (Quixadá, Tauá, Iguatu × 1998, 2012, 2016), JSON dos 184. | O JSON de Quixadá e o 64/127 de 2016 batem com `v2_arquiteto_arbitragem_smap.saida.txt`. |
| 2 | Sáb 13h – Dom 02h | P2 | Converter o site para estático. As 3 telas: Relógio (3 curvas, duas luzes, termômetro com "dormindo", placar do município, painel "hoje"); Cartões S0–S3 em 3 anos; Replay de 1998 e 2016 (frames do Plotly, IBGE revelado na colheita). Glossário em pop-up. | Quixadá carrega em < 2 s no celular. |
| 3 | Sáb 15–21h | P3 | Página de auditoria estática gerada em Python (eras, arbitragem R2.2, nulos, gatilho tipo Garantia-Safra). Textos dos cartões redigidos offline e congelados; verificador regex com 30 casos adversariais e as regras novas. | Zero números fora do JSON; os 30 casos bloqueados. |
| 4 | Sáb 20h | P3 | Refazer a checagem do SMAP L3 com o consolidado; conferir a documentação do L4 v008. | Números do L3 atualizados na folha. |
| — | **Sáb 22h** | Todos | **Números congelados.** | — |
| — | **Dom 02–08h** | Todos | **Sono obrigatório.** | — |
| 5 | Dom 08h | P2 | **App congelado**; ele vira a fonte das telas do vídeo. | — |
| 6 | Dom 08–13h | P4 (+P3) | 7 slides em inglês. | — |
| 7 | Dom 12–17h | P4 | Vídeo de 30 s (roteiro 11.2). | Vídeo gravado até 17h. |
| 8 | Dom 17–20h | Todos | Checagem cruzada (slides × folha × app) e ensaio. | Nenhuma divergência. |
| 9 | Dom 20–22h | Todos | Publicar no GitHub Pages; vídeo e PDF como reserva. Submeter. | Submetido antes das 22h; folga até 23:59. |

**Tarefas do José (pessoa, não agente):**
- ler o regulamento sobre trabalho anterior ao evento e o formato da declaração de uso de IA (atrasado);
- decidir o tamanho da equipe (atrasado);
- conferir o limiar e a cesta do Garantia-Safra e a janela do ZARC de Quixadá;
- até sáb 18h, falar com 1 técnico de ATER ou 1 agricultor e mostrar o cartão de Dona Francisca (P1 e o termômetro "dormindo");
- decidir sobre o pré-registro público (duas luzes para 2027; leitura VIIRS da safra de 2026).

**Se a equipe for de 1 pessoa, cortar já:**
1. App em ~5 h: Relógio + 1 cartão + replay estático.
2. Vídeo em 2 h.
3. Sem pontos globais, sem globo, sem trajetórias animadas.

**O que cortar se faltar tempo, nesta ordem (2 pessoas):**
1. Pontos globais: fica 1 ponto.
2. Painel de fogo: vira uma linha no cartão S0.
3. Trajetórias diárias animadas: o replay mostra só os portões e a revelação do IBGE.
4. O replay de 2016 animado: vira a figura estática do slide 4.

**Nunca cortar:**
- o Relógio com as 3 curvas e as duas luzes;
- os 4 cartões com recibo;
- o replay de 1998 com o observado do IBGE (estático, se preciso);
- a figura de 2016 (9 contra 64 de 127, com 2021 ao lado);
- a folha canônica.

**Cortados de saída do MVP:**
- código de barras ao vivo (fica a figura estática);
- áudio e TTS (ficam como roteiro, a menos que haja voz humana gravada até sáb 18h);
- modo global ao vivo e SMAP ao vivo;
- ECOSTRESS e GNN/Prithvi;
- simulador de WhatsApp;
- FIRMS NRT, LSPA e CDL;
- Pareto em 8 eixos e árvore destilada;
- replay com as temporadas do POWER;
- explicador LLM em tempo de execução;
- retreinar o M2 com o VIIRS.

**Próximos passos (slide):** floresta causal no talhão à maneira de Kluger (MapBiomas/HLS + pico de NDVI calibrado no PAM + estado da água como modificador), Prithvi-EO-2.0, Sentinel-1/NISAR para datar o plantio (com a regra de validação contra o SMAP L3), assimilação do SMAP L4 no balde, ECOSTRESS/ESI como gatilho, bot de WhatsApp com áudio, rede de pluviômetros, veredito tricot, EVPPI e GEOS-S2S.

---

## 11. Roteiro da demo

### 11.1 Os 7 slides (em inglês)

1. **"Stanford asked which rotation pays where. We asked when the water decides."**
   - Kluger, Di Tommaso & Lobell (ERL 2025): satellites, crop maps and causal forests in four temperate breadbaskets. Rotation benefits are real and change with climate: larger in rainier seasons, smaller for legume precrops in the heat, and diversifying beyond a simple rotation adds little. No semi-arid, no water data.
   - *QUADRA: the sertão's word for the rainy season.* We take the question to Brazil's semi-arid, one rainy window, with NASA water data at the core.
   - Our own check, in one line: "In Ceará's droughts, counties less locked into corn and beans kept more yield, but among rain-fed crops the diversity link vanishes (+1.4 points, not significant). So QUADRA promises no rotation bonus: it ranks every plan by its worst year."
2. **"One window, one chance."**
   - Mapa do Ceará em 1998 e 2012: 3 em 4 municípios perderam mais da metade do milho.
   - No registro, milho e feijão quebram juntos (0,78).
   - A ET0 supera a chuva em 10 de 12 meses.
   - O mesmo problema no Sahel, na Índia de sequeiro e no Texas.
3. **"Three curves decide when to decide."** É a imagem principal.
   - Habilidade: chuva NASA (0,57 → 0,80 em 28 quadras), oceano (0,67) e a segunda luz, o solo (0,77 em 30/abr na era SMAP).
   - Opções fechando (milho 93% → 42% → 0%; caupi 98% em São José).
   - Visibilidade: "Optical satellites go blind at decision time (39–40% usable pixels in Jan–Mar); SMAP's microwave sees every 9 km cell 13–15 days a month."
   - Caixa de São José: "Tradition is weak, not wrong (ρ ≈ +0.3). On that day, neither rain nor soil says much yet. By April 30, the soil does."
   - Os 5 portões e a frase "In a one-window climate, rotation happens inside the season and across years."
4. **Momento uau: "2016: rain-to-date said fine. The soil said no."**
   - Mapa dos 182 municípios em 30/abr/2016. Janeiro teve cerca do dobro do normal.
   - "Rain-to-date flagged 9 of the 127 counties that lost more than half their corn. NASA SMAP root-zone soil moisture flagged 64." Rodapé: "weekly reading; 90 if read on the day itself; would have flagged with today's reprocessed product."
   - "Same in 2025: 1 vs 21 of 45."
   - "Where it fails: 2021, 81 counties flagged, 3 failed. Ten seasons, one big drought: grade B."
   - "Rain-to-date remembers January. The soil doesn't." Recibo em um clique: SMAP L4 é modelo da NASA alimentado pela chuva IMERG e corrigido pelo radiômetro SMAP; o radiômetro sozinho (L3) e a chuva recente do IMERG contam a mesma história.
5. **"Your county, every season replayed."**
   - Quixadá: S0 contra S1–S3 como sequências 2027–2029. O replay de 1998 (São José a 70% do normal, janela do caupi aberta). Um terço em mandioca: o "pior ano em 10" vai de 0,15 a 0,36 (nos municípios de mandioca, 0,32 mesmo se a maniva faltar).
   - Placar honesto: "Our soil light never hit in Quixadá (2016 and 2025 were its two lowest readings, just above the line). Skill is regional."
   - Caixa "When the referee and the satellites disagree": 2024, chuva a 105%, solo p70, VIIRS verde, nenhum vizinho em quebra, e o IBGE registrou quebra. "Check pests, reporting or area with the extension agent."
6. **"NASA is the engine, IBGE is the referee. How we used SI, honestly."**
   - *used in this demo:* IMERG, SMAP L4, GRACE/GRACE-FO, GLDAS-2.1/2.2, VIIRS (NDVI and fire), MODIS, Landsat/HLS, POWER, SRTM, NEX-GDDP; *check:* SMAP L3; *roadmap:* ECOSTRESS, NISAR, Prithvi.
   - "Every curve shown by era: the rain rule that worked in 1998–2015 failed in 2016–2025, and we show it."
   - "Satellites know the bad year, not the bad county (within-year AUC ≤ 0.60 for every layer)."
   - "Random validation lies (0.49 vs −0.08)."
   - "Our drift sentinel flagged Terra's documented orbit drift and a post-2020 greening seen by two sensors."
   - "NASA's off-the-shelf SMAP drought percentile flagged 1% of counties in 2016; we re-anchor every layer against IBGE before trusting it."
7. **"Today: strongest Aug–Oct El Niño on record (ONI +2.46)."**
   - "In a typical year, 2 in 10 counties lose half their corn. With this ocean, about 5 in 10 (honest range 2–8). Closest years: 1998 and 2016, 7 in 10; 2024, fewer than 1 in 10."
   - "Soil thermometer: asleep, as every November. Water bank: normal. The caatinga is greener than in 12 of 14 Octobers: more fuel, don't burn."
   - Ações sem arrependimento para Dona Francisca (fictícia): semente de caupi e sorgo até dezembro, maniva para fevereiro, troca para o caupi no início de março, as duas luzes em São José e em 30 de abril.
   - Frase do técnico de ATER, se obtida com permissão.
   - "NASA evidence. The farmer decides."

### 11.2 Vídeo de 30 s (em inglês, com legenda; no máximo 3 números: 9, 127, 64)

| Tempo | Imagem | Locução |
|---|---|---|
| 0–6 s | Mapa do Ceará em 30/abr/2016, quase todo "chuva ok"; legenda "QUADRA: the sertão's word for the rainy season" | "April 30, 2016. Rain-to-date looked fine in almost every county of Ceará." |
| 6–14 s | O mapa fica vermelho onde o SMAP acendeu; contador 9 → 64 de 127 | "Rain alone flagged 9 of the 127 counties that went on to lose their corn. NASA's SMAP soil moisture flagged 64." |
| 14–21 s | As 3 curvas se cruzando sobre o calendário | "Stanford showed rotation benefits change with climate. QUADRA brings that to the semi-arid, with NASA water data, and finds the checkpoints where the data know enough and you can still switch." |
| 21–27 s | Mostrador do ONI; o Relógio com P1 aceso e o termômetro dormindo | "Today the Pacific shows a record El Niño. Buy cowpea seed now, don't burn, switch early." |
| 27–30 s | O técnico e a família olhando o cartão | "NASA evidence. The farmer decides." |

**Como reproduzir o número-uau (9, 64, 127):**
1. `E:/campeonato-nasa/venv/Scripts/python.exe -I "c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/v2_hidrologo_cinco_fontes_umidade.py"` (gera `saidas/v2_hidrologo_smap_pctl_mun_diario.parquet`, o SMAP municipal diário deduplicado).
2. `E:/campeonato-nasa/venv/Scripts/python.exe -I "c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/v2_arquiteto_arbitragem_smap.py"` → bloco [30/abr], linha "chuva < 75% (canonica)" (2016: 9/127) e linha "SMAP 7d < 20" (2016: 64/127; 2021: 3/7 com 81 alertas). A linha "SMAP dia < 20" dá 90/127.
3. Reproduções independentes: `v2_hidrologo_smap_portoes_quebra.py` (64 na média de 7 dias); `v2_estrategista_smap_portoes.py` e `v2_cetico_smap_portoes.py` (90 no dia, lendo o `.nc` direto).
- Quebra canônica: produção ÷ área plantada < 50% da mediana dos outros anos (milho, PAM, área ≥ 50 ha). Luz de chuva: IMERG desde 1/jan < 75% do normal. Luz do solo: percentil da zona da raiz do SMAP L4 < 20, média de 24 a 30/abr.

**Cuidados:**
- A família é fictícia e rotulada.
- Não usar logomarca da FUNCEME, da Ematerce ou da NASA que sugira endosso. Os selos dizem "data from".
- "QUADRA: the sertão's word for the rainy season" aparece na legenda do primeiro segundo.
- O rodapé do vídeo diz "grade B; false alarm in 2021; today's reprocessed product". O vídeo não diz que o SMAP decide em 19/mar nem que ajuda em novembro.
- Nenhum número do Kluger no vídeo nem nos slides até a conferência na versão publicada.

---

## 12. Mapa de prêmios-alvo e critérios de julgamento

### 12.1 Prêmios

| Prêmio | Prioridade | O que o sustenta |
|---|---|---|
| **Best Use of Science** | 1ª | As três curvas validadas por ano e por era; duas luzes com teste fora da amostra; comparações só pareadas; IBGE como árbitro; arbitragem pela leitura menos favorável; resultados negativos declarados (soma em 2016–2025, Quixadá, SMAP de novembro, IA causal no PAM); recibo A–D com marca ·T; ponte com Kluger et al. 2025. |
| **Best Storytelling** | 2ª | 2016, "a chuva disse que estava tudo bem, o solo disse que não"; São José testado com respeito; replay de 1998 com a decisão mudando; 2027 ao vivo; Dona Francisca. |
| **Local Impact** | 3ª | Ceará, 184 municípios, técnico no circuito, ações baratas em novembro, troca para o caupi no início de março, maniva e semente; validação com um técnico de ATER (se feita). |
| **Best Use of Data** | 4ª | Mais de dez bases NASA, cada uma numa decisão; SMAP L4 testado contra o IBGE e reancorado; L3 como checagem; VIIRS como continuidade do MODIS; escala útil medida entre sensores; o sentinela de deriva; o relato copiado no PAM. |
| **Galactic Impact** | Indicação | Motor global (SMAP cobre 99,6% da terra entre 60°S e 60°N); janela sintética em qualquer ponto; "40 de 47 pontos terrestres tropicais sem mês de quebra térmica". |
| Best Use of Technology | Não é alvo | O app estático é simples de propósito. Se for avaliado, o argumento é o verificador e a ausência de API em tempo de execução. |

### 12.2 Critérios (notas de 1 a 5)

| Critério | Como atendemos | Risco e mitigação |
|---|---|---|
| **Impacto** | Decisão real de uma família numa data real (2027); métrica do ano ruim; ações baratas já em novembro e no início de março; canal pelo extensionista. | Família fictícia. Mitigação: 1 conversa real com ATER e 1 mudança feita por causa dela, no slide 7. |
| **Criatividade** | Calendário derivado de três curvas; duas luzes (soma e estado); rotação como política em 3 anos; São José; entressafra como portão; honestidade como funcionalidade; a pergunta de Stanford no semiárido. | O júri pode ler como diversificação. Mitigação: cada estratégia como sequência 2027–2029, a frase do slide 3 e o "não prometemos bônus de rotação". |
| **Validade** | Definição canônica única; curvas por era; comparações pareadas; validação por ano; leitura menos favorável; recibo; auditoria; onde erramos. | Habilidade regional e poucos episódios (a era SMAP tem 10 quadras). Mitigação: grau B na segunda luz, 2021 ao lado de 2016, o placar de Quixadá com 0 acerto da luz do solo e "seu município / sua região". |
| **Relevância (NASA no núcleo)** | Portões e replay são IMERG; a segunda luz é o SMAP L4 (checado pelo L3); o balde é IMERG + POWER calibrado contra o SMAP; a memória é IMERG + GRACE + GLDAS + Landsat; o verde é VIIRS; o fogo é VIIRS; o relevo é SRTM; o futuro é NEX-GDDP. | O ONI é da NOAA e o árbitro é o IBGE. Mitigação: "NASA tells the state, the ocean tells the odds"; o ONI só repondera os anos do replay NASA; o IBGE só confere. |
| **Apresentação** | Uma imagem (as três curvas), um número-uau (9 contra 64 de 127), três telas; no máximo 3 números no vídeo. | Excesso de instrumentos. Mitigação: no cartão da família, no máximo 3 números e um instrumento por portão; a auditoria fica fora das telas, como link. |

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
- FIRMS NRT, LSPA, CDL e o simulador de WhatsApp foram cortados; o pré-registro só sai com o OK do José; o mapa usa o GeoJSON sem tiles (E).

**Onde não seguimos a banca, e por quê:**
- **Replay de 2016 ou de Tauá (E):** preferimos 1998. Ver o item 2.
- **IMERG Late com "−0,5 dp" no painel "hoje" (J):** entra como contexto de frescor dos dados, com a frase "isso não prevê a quadra (ρ −0,06)". O dado do cético mostra que a chuva da estação seca não informa a quadra.
- **Grau B/C para toda a mandioca (C):** mantivemos o grau A para o resultado estadual, porque ele resiste à retirada dos anos repetidos, com IC por ano. O nível do município fica em B.

### 13.2 Rodada 2 (riscos que a banca deixou e o que os dados novos fizeram)

Ver a seção R2.4 no início do documento. Em resumo: o risco "SMAP pode não chegar" está resolvido; a Relevância NASA ganhou o SMAP no núcleo; os números de vitrine que não se reproduzem saíram ou foram rebaixados (+6,6 p.p., +0,072, 0,307); a validade local de Quixadá continua fraca e é mostrada assim; e apareceu um risco novo, a falha da regra de chuva na última década, que agora é o centro da narrativa como erro explicado.

---

## Anexo A. Decisões em aberto para a equipe (exigem pessoa, não agente)

1. Tamanho da equipe e divisão dos papéis P1–P4 (**atrasado; era até as 10h de sábado**). Sem decisão, vale o plano de 1 pessoa (seção 10).
2. Nome final: QUADRA (recomendado) ou a reserva Field Replay.
3. Ler o regulamento sobre trabalho anterior ao evento e o formato da declaração de uso de IA (atrasado).
4. Conferir na lei o limiar, a cesta e a área mínima do Garantia-Safra, e a janela do ZARC oficial de Quixadá.
5. **Uma conversa com um técnico de ATER** (Ematerce, sindicato rural ou ONG da ASA) **ou com um agricultor**, até sáb 18h, com permissão para citar 1 frase. Perguntar também sobre Quixadá 2023–2024 (praga, relato ou área?).
6. Publicar ou não o hash do pré-registro das duas luzes para 2027 e a leitura VIIRS da safra de 2026 (voz pública).
7. Gravar ou não 45 s de voz humana em português para o cartão (até sáb 18h).
8. Confirmar se fatos do "Encontro dos Profetas da Chuva" de Quixadá podem ser citados (agora no slide 3).

---

## Project summary (English)

QUADRA (the sertão's word for the rainy season) is a decision-support tool that lets farmers and extension agents stress-test rotation plans against NASA's record before committing. Kluger, Di Tommaso and Lobell (ERL 2025) showed with satellites and causal machine learning that rotation benefits change with climate, but only in temperate breadbaskets and without water data. QUADRA takes the question to the semi-arid tropics, where a rotation is not a fixed crop sequence but a policy with checkpoints, and where what decides is when the water shows up.

QUADRA places the checkpoints where three measured curves cross. The first is what the data already know, validated by leaving whole years out: over 28 rainy seasons (1998–2025), IMERG rain-to-date rises from AUC 0.57 in January to 0.80 by April 30, and the ocean gives 0.67 from November. In the last decade, however, rain-to-date fell to 0.66, because wet Januaries masked dry seasons. NASA's SMAP root-zone soil moisture restores the signal on April 30 (0.77): in 2016, the closest analog to today's record El Niño, rain-to-date flagged 9 of the 127 counties that lost their corn, and SMAP flagged 64. QUADRA therefore uses two lights, rain-to-date or soil water, and shows its false alarms (2021) next to its hits. The second curve is what is still possible: planting deadlines from an FAO-56 water balance driven by IMERG and NASA POWER. The third is when satellites can see: optical sensors go blind at decision time, while SMAP's microwave radiometer sees the ground 13–15 days a month.

For each county, QUADRA compares the current practice with three alternative three-year strategies, replays them over every season in the IMERG record, and ranks them by their worst years. Observed yields from Brazil's IBGE act as referee. Every number carries a receipt (NASA source, scale, validation, A–D grade), every curve is shown by era, and an audit page shows where the tool fails, including counties where the soil light never hit. In Ceará, a third of the area in cassava raised the worst-decile harvest from 15% to 36% of normal (in cassava counties, still 32% even when cuttings run out). GRACE, GLDAS, VIIRS, Landsat, SRTM and NEX-GDDP add water memory, greenness, fire, terrain and 2050 heat. The engine is global; the demo is Ceará. NASA evidence. The farmer decides.

## Use of SI (AI) tools

Inside the product, SI appears in five places:
1. A physics-guided crop-water twin (FAO-56 water balance) whose soil-water state is calibrated against NASA SMAP L4, plus a monotonic end-of-season emulator. Both are validated by leaving whole years out, and the emulator's year-robust conformal intervals report their width.
2. Checkpoint forecasts whose skill is measured without look-ahead and shown separately for 1998–2015 and 2016–2025, with two pre-registered lights (rain-to-date and SMAP root-zone soil moisture), an out-of-sample test of the second light before SMAP existed, and an out-of-distribution warning for this year's record El Niño.
3. An exact search over rotation strategies that ranks them by tail risk (CVaR) instead of average yield, with a declared floor for years when cassava cuttings are missing.
4. A drift and data-quality sentinel that downgrades evidence automatically. It flagged Terra's documented orbit drift in land surface temperature, a post-2020 greening seen by two sensors, copied year-to-year yield reports, and SMAP's dry-season gaps and duplicated dates.
5. A large language model that only drafts the text on each card. It works offline from the engine's numbers, and a deterministic checker blocks any number, attribution or certainty word that the engine did not produce.

We also report what did not work: causal machine learning on county statistics could not identify a rotation effect (a placebo test failed), and November soil moisture does not predict the rainy season.

To build QUADRA, the team used Anthropic's Claude (Claude Code) as a coding and analysis assistant. This included a council of AI agents that proposed, debated, re-analysed new NASA data and adversarially reviewed designs over two rounds. Every reported number comes from a script in the project repository that a person can rerun. No model was trained on LLM outputs, and no LLM is called at run time.
