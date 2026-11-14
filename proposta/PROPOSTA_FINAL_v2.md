# QUADRA: proposta final v2 (NASA Space Apps 2026, desafio "Field Shift")

- **Versão:** v2 corrigida depois da banca da rodada 2, sábado 14/11/2026, a partir das 11:25 (hora local, pelo `date`). Prazo de submissão: domingo 15/11/2026, 23:59.
- **De onde vem:** a `PROPOSTA_FINAL.md` (rodada 1), refeita com as reanálises da rodada 2, que usaram os dados novos já em disco (SMAP L4 diário, SMAP L3, VIIRS VNP13A3, GLDAS-2.2 CLSM diário, GLDAS-2.1 Noah, NLDAS-2, IMERG V07 Late/Early recente), com o artigo-âncora Kluger, Di Tommaso & Lobell (2025) e com os três pareceres da banca da rodada 2 (juiz, cético e engenheiro de viabilidade).
- **Análises do arquiteto:** `conselho/analises/v2_arquiteto_arbitragem_smap.py` resolve as divergências entre especialistas (seção R2.2). Depois da banca, `conselho/analises/v2_arquiteto_r2_fechamento.py` → `.saida.txt` traz as curvas por era nos 5 portões, a escolha pré-declarada da luz de 2027 e o hash da regra, o nível do ano em 2016, 2021, 2022 e 2025, o placar de Quixadá, o contrafactual do caupi em 1998, 2016 e 2024, a carteira condicionada à luz NASA e a checagem com o SMAP L3 consolidado.
- **Regra de honestidade (mantida):** todo número tem arquivo de origem. Os scripts da rodada 2 ficam em `conselho/analises/v2_<persona>_<tema>.py`, cada um com seu `.saida.txt`. As referências vêm da revisão `pesquisa/artigos_e_datasets.md` ou de `pesquisa/artigo_ancora_objetivo.md` (Crossref conferido em 14/11/2026); as que estão fora das duas têm a marca "fora da revisão".
- **Regra da leitura menos favorável (mantida):** quando duas leituras igualmente razoáveis do mesmo dado dão números diferentes, **o slide usa a menos favorável** e o recibo mostra a outra.
- **Regra nova, cobrada pela banca R2: linha de base justa.** Todo ganho é medido contra a **melhor** leitura já declarada do mesmo dado, nunca contra a pior. Foi essa regra que trocou a luz principal (R2.1).

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
   - **Modelo único, pré-declarado no script do clima:** a logística P(quebra municipal) ~ ONI ASO do ano anterior, validada deixando o ano inteiro de fora, tem BSS de +0,063 no município (IC90 −0,07 a +0,18) e ρ de +0,39 com a fração de municípios em quebra (p = 0,038; n = 28). O sinal é real no nível do ano e pequeno (`v2_clima_portao_novembro_2027.saida.txt`, bloco B). Por era, a AUC do ONI é 0,66 em 1998–2015 e 0,72 em 2016–2025 (`v2_arquiteto_r2_fechamento.saida.txt`, bloco A).
   - Os El Niños fortes foram "tudo ou nada": o modelo previu cerca de 0,5 para 1998, 2016 e 2024, e o observado foi 0,75, 0,70 e 0,08 (mesmo arquivo).
   - Com erro-padrão agrupado por ano, o efeito do El Niño "além da chuva" **não é significativo**: OR 1,57, IC95 0,71–3,50 (`cetico_memoria_grace_neff.saida.txt`, bloco A). Grau B.
5. **O solo fica nu e queima.**
   - 72,9% dos focos de fogo VIIRS de 2015–2025 caem em out–dez; até 30/set, só 27% (`v2_ecologo_calendario_fogo.saida.txt`).
   - 17% da área do Ceará está em células de ~375 m com ao menos um foco VIIRS em 2012–2025. Isso não é área queimada: um roçado de 1 ha acende uma célula de 14 ha.
   - A medida de área é o MapBiomas Fogo a 30 m: 12,7% da Caatinga queimou entre 1985 e 2023 (Franca Rocha et al. 2024).
6. **Em janeiro, a chuva que já caiu não diz quase nada; até março, a soma desde janeiro pode enganar.**
   - A chuva IMERG acumulada até 31/jan separa a quebra do milho com AUC de apenas 0,57 (IC90 0,43–0,68). Em Quixadá, janeiro de 1998 teve 150% do normal e janeiro de 2016 teve 197%. Os dois anos foram de quebra.
   - O oceano diz um pouco: o ONI de ASO, publicado no início de novembro, tem AUC de 0,67 (IC90 0,53–0,78) para a quebra municipal (`arquiteto_final_curvas_quixada.saida.txt`, bloco A).
   - **A soma desde 1/jan guarda o janeiro.** Em 30/abr, a AUC dela é 0,83 em 1998–2015 e cai para 0,66 em 2016–2025, quando o alerta acende menos onde quebra do que onde não quebra (1,1 contra 1,5 em 10). Janeiro foi 34% da chuva de jan–mai em 2016 e 28% em 2025, contra a mediana de 12% (`v2_arquiteto_arbitragem_smap.saida.txt`, bloco E; `v2_economista_janela_alerta.saida.txt`).
   - **A mesma chuva contada desde 1/fev** não guarda o janeiro: 0,82 e 0,76 em 30/abr; 0,74 e 0,71 em 19/mar, nas duas eras (`v2_arquiteto_r2_fechamento.saida.txt`, bloco A).

### 2.2 Por que as ferramentas atuais não resolvem

- O **ZARC** dá a janela de plantio de uma cultura, mas a janela não muda com o ano.
- O **prognóstico de tercis** não vira decisão de rotação.
- **Painéis de NDVI** mostram o passado e não comparam estratégias. E o óptico fica cego justamente nos portões: só 39–40% dos pixels do Ceará têm NDVI VIIRS bom ou marginal no mês em jan–mar (`v2_sr_fundacao_viirs_portoes.saida.txt`, bloco A).
- O **percentil pronto de umidade do solo** do SMAP L4 não existe no sertão de agosto a meados de janeiro. E a **média sazonal** desses percentis (fev–mai) comprime a escala: acende em 0,7% dos municípios e não pega nenhuma das 127 quebras de 2016. O mesmo produto lido no portão (média de 7 dias) pega 64 (`v2_cetico_r2b_gatilho_carteira.saida.txt`, bloco 1). Usar o dado da NASA exige saber **como e quando lê-lo**, e testar a leitura contra o IBGE.
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
     - S3 "sem número; faixa da literatura (B·T)".
   - Os pesos da família reordenando os cartões ficam para a próxima versão.
3. **Replay (estático, com um controle de data).**
   - **1998:** em 10/mar, 19/mar e 30/abr, a chuva desde 1/jan e desde 1/fev. Depois, o balde do caupi (grau C) e o IBGE revelado na colheita.
   - **2016:** as mesmas datas, mais o SMAP e o verde do VIIRS de abr–mai como testemunha, e o IBGE no fim.
   - Sem M2, sem trajetórias animadas e sem barras de ISNA diárias.

**Fora das telas do MVP:**
- A **auditoria** vira um `AUDIT.md` no repositório (o GitHub renderiza), com as tabelas R2.2 e 9.2 e links para os `.saida.txt`. Ela inclui o gatilho tipo Garantia-Safra (marcado "refazer com a mesma escala"), as 5 leituras da chuva lado a lado, o placar das duas eras e os nulos.
- Ficam no roteiro: o código de barras do talhão ao vivo, áudio, simulador de WhatsApp, modo global, SMAP ao vivo, pesos da família e o emulador M2 na tela. Do modo global, fica 1 linha: "o SMAP L4 cobre 99,6% da terra entre 60°S e 60°N".

### 3.3 Fluxo de uso ao longo do ano

| Quando | O técnico faz | A família recebe ou faz |
|---|---|---|
| Primeira visita | Escolhe o município. Confirma a prática atual (o PAM sugere; 1 pergunta confirma). Registra rebanho, semente guardada, maniva, mão de obra e água guardada. | Cartão de apresentação: "o QUADRA não sabe tudo; aqui está o que ele sabe". |
| **P1, nov–dez** | Lê o oceano e o banco de água. O termômetro do solo está dormindo, e isso é dito. | Ações sem arrependimento: semente de caupi precoce até dezembro, maniva guardada, palma, adesão ao Garantia-Safra, não queimar, aceiro. |
| **P2, jan–fev** | Lê a chuva recente; o termômetro acorda em meados de janeiro (~12/jan). Em 28/fev: "ainda é cedo". | "Plante uma parte agora e guarde a outra." A família informa a **data de plantio**. |
| **Início de março (~10/mar), só em ano de El Niño forte** | Lê a chuva desde 1/fev e o SMAP (leitura descritiva, sem habilidade medida). | Se a luz estiver acesa, a metade guardada vai para o caupi até ~11/mar, **se o técnico confirmar que ainda há umidade para a semente**. Num ano como 2016, o caupi de 11/mar teve água na floração em 7 de 10 municípios; num como 1998, em 1 de 10 (balde, grau C). Se estiver verde (como em 2024), a metade guardada segue o plano normal. |
| **P3, 19/mar ("Checkpoint São José")** | Lê a luz em quatro estados. | Vermelho ou amarelo: caupi só se ainda couber (até ~21/mar em ano normal); **sem sorgo de grão na troca**. Cinza-amarelo: "os instrumentos discordam; o técnico decide". |
| **P4, 30/abr** | Lê a luz de novo; é quando o SMAP mais confirma. | Ação graduada: guardar forragem, cortar o milho para os animais se o técnico confirmar, segurar a venda dos animais. |
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
- **"% do normal":** a chuva no período dividida pela mediana dos outros anos no mesmo município. Na estação seca, a tela usa mm e posto, nunca "% do normal" (398% sobre 1 mm engana).
- **"Chuva desde 1/fev":** a luz principal do QUADRA. Conta a chuva a partir de 1º de fevereiro, porque um janeiro chuvoso pode esconder uma quadra fraca.
- **"Segunda missão":** o SMAP, que mede a água no solo por micro-ondas e confirma, ou não, o que a chuva diz.
- **"Seu município / sua região":** "seu município" é onde o número foi medido; "sua região" é onde contamos quantas vezes ele acertou, ano a ano, porque a seca atinge a região inteira de uma vez.
- **Percentil.**
- **Grau de evidência A–D.**

### 3.5 Apoiar, não substituir

- No MVP, a ordem dos cartões é fixa. Na próxima versão, os pesos vêm da família.
- O técnico aprova toda mensagem.
- A família pode vetar ("não quero caupi"). No MVP, o cartão mostra a alternativa seguinte; recalcular o custo da escolha fica para a próxima versão.
- As datas-limite são de uma **janela sintética tipo-ZARC** feita com o IMERG; o cartão diz "confirmar no ZARC oficial com o técnico".
- Quando a chuva e o solo discordam, o cartão diz "os dois instrumentos discordam; o técnico decide", sem número. Foi o que aconteceu em 2022: chuva baixa em 142 municípios, solo normal em todos, e 3 quebras.
- Todo cartão termina com "o que confirmar no chão com o técnico".
- **Freio de segurança:** sem restrições, o otimizador de renda bruta escolhe "100% mandioca" em todos os municípios (`pesquisador_ia_conformal_carteira.py`). É o exemplo de por que a ferramenta apoia e não decide.

---

## 4. Arquitetura: núcleo global de dados NASA e enriquecimento local

### 4.1 Visão geral

```
        NÚCLEO GLOBAL                                               ENRIQUECIMENTO LOCAL (quando existe)
 [luz]     IMERG V07 diário 0,1° (TRMM 1998–2014, GPM 2014→): chuva desde 1/fev    Brasil: IBGE PAM (árbitro), ZARC oficial
 [2ª missão] SMAP L4 v008 zona da raiz 9 km (2015→): confirma a luz                 (a conferir), Garantia-Safra (a conferir)
 [checagem] SMAP L3 v006 (radiômetro; consolidado até 12/11/2026)                   EUA: CDL/CSB, NASS, NLDAS-2 (em disco)
 [na tela]  VIIRS VNP13A3 (testemunha de junho; caatinga), GRACE/GRACE-FO, SRTM     Família: data de plantio, água guardada,
 [repositório] POWER, GLDAS-2.1/2.2, MODIS, Landsat/HLS, NEX-GDDP, focos VIIRS      maniva, veredito de fim de safra
 [roteiro]  ECOSTRESS/ESI · Prithvi-EO-2.0 · NISAR (com regra de validação pré-declarada)
                  │                                                   │
                  ▼                                                   ▼
   GRADE COMUM + ESCALA ÚTIL MEDIDA ─► exportador (lê os parquets já salvos; 0,4 s) ─► JSON por município
        ─► Relógio (3 curvas por era, luz em 4 estados) ─► Cartões de Quixadá + recibo ─► Replay estático 1998 e 2016 (IBGE arbitra)
```

### 4.2 Grade comum, escala útil e regras de harmonização

A coluna nova, "escala útil medida", é a menor escala em que dois sensores independentes concordam nas anomalias com r ≥ 0,8 (regra pré-declarada pelo especialista em sensoriamento remoto; `v2_sr_fundacao_escala_real.saida.txt` e `v2_sr_fundacao_smap_l3_l4.saida.txt`, bloco B). O município mediano do Ceará tem 632 km², ou 25 km de lado.

| Camada | Resolução nativa | Escala útil medida | Como entra na grade comum | Regra de uso |
|---|---|---|---|---|
| IMERG | 0,1° (~11 km), diário | Nunca chega a r 0,8 contra o SMAP L3 (0,57 a 11 km; 0,63 a 88 km): vale para o **ano e a região** | É a **grade de decisão**. Agregada ao polígono do município para calibrar contra o PAM. | **Luz principal: chuva desde 1/fev por portão**, sempre mostrada por era (1998–2015 e 2016–2025). A soma desde 1/jan fica como regra antiga, no replay e na auditoria. Na estação seca, mm e posto. O Late e o IMERG via POWER são o mesmo dado na sobreposição de 01/ago a 14/set/2026 (razão 1,00; r 1,00; `v2_clima_estacao_seca_2026.saida.txt`). |
| SMAP L4 (SPL4SMGP v008) | 9 km, granulo diário das 13:30 UTC | Diz **quando** a 9 km (r temporal com o L3 de 0,89 por célula) e **onde** a partir de 36 km (r das anomalias 0,824) | Média das células de 9 km com centro no município (mediana de 8 células; Quixadá tem 25). | **Segunda missão: percentil da zona da raiz, média dos 7 dias até o portão; < 20 confirma a luz.** De ~12/ago a ~12/jan o percentil do produto vem vazio no sertão: aí entra o **percentil próprio** (posto entre os anos desde 2015, com o n) e o nível absoluto. Nunca a **média sazonal** de percentis (comprime a escala) e nunca limiar absoluto em m³/m³ (cinco estimativas NASA da água na raiz diferem até 0,10 m³/m³; `v2_hidrologo_cinco_fontes_umidade.saida.txt`). Deduplicar as 4 datas repetidas. |
| SMAP L3 (SPL3SMP_E v006) | Pegada do radiômetro de ~40 km, postada numa grade de 9 km; AM e PM | Igual ao L4 (r 0,89 na anomalia diária do estado) | Só checagem | Qualidade recomendada (bit0 = 0); deduplicar as 7 datas repetidas do consolidado. A célula mediana é vista em 13–15 dias por mês, na quadra e na seca; 93,5% das células-mês têm ao menos 4 dias vistos. |
| POWER | 0,5°, diário | — | Célula válida mais próxima de cada célula IMERG. | Sempre como **anomalia ou percentil por fonte**. A Tmax do POWER é cerca de 1,7 °C mais quente que a do ERA5, e a ET0 fica ~15% acima (seção 9.7). |
| GRACE/GRACE-FO | ~300 km | Regional | Mascon regional, **média móvel de 3 meses**. | Só contexto regional. Um mês isolado só aparece com a faixa de ruído. O recibo mostra n_eff ≈ 28. |
| GLDAS-2.2 CLSM (diário) | 0,25° | Regional: a célula de Quixadá anda junto com o CE (r 0,98; `v2_designer_banco_lento.saida.txt`) | Água subterrânea (GWS) por mês | **Assimila o GRACE por construção; não medimos quanto.** A concordância com o GRACE (r 0,88 no CE) não vale como validação. Fica fora da tela. |
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
| M2, emulador de replay (fim de safra) | Saídas de M1; dias quentes acima do p90 local (POWER); NDVI relativo (**VIIRS**, MODIS antes de 2012) | PAM (alvo) | Estimativa da NASA para cada quadra. **Fica no repositório, fora da demo:** as previsões por município-ano não foram salvas |
| M3, previsor por portão | **Chuva IMERG desde 1/fev (luz principal)**; **SMAP L4, percentil da zona da raiz (segunda missão, 2015→)**; chuva desde 1/jan como regra antiga | ONI | Luz em 4 estados por portão, habilidade por era, aviso de caso inédito, contagem de análogos, probabilidade do P1 |
| M4, carteira e política | Replay de M1–M3 nas 28 quadras | Pesos, restrições, preços | 3 estratégias + a atual, em sequência de 3 anos |
| M5, prática atual | MODIS/HLS (fenologia), focos VIIRS | PAM, 1 pergunta à família | Estratégia atual |
| M6, sentinela de deriva e qualidade | LST e NDVI do MODIS contra POWER, Landsat, HLS e **VIIRS**; **disponibilidade e duplicatas do SMAP** | PAM (bandeira de relato repetido) | Rebaixamento automático do grau |
| M7, relógio lento e combustível | **Memória de chuva do IMERG (12–48 meses)**; GRACE e GLDAS como checagem; fração de água do Landsat; NDVI VIIRS de t e t−1; focos VIIRS | Volume de barreiro ou cisterna | Banco de água azul, área salvável, **mapa** de combustível e da ponte verde |
| M8, redator com verificador | JSON de M1–M7 | Trechos conferidos da revisão | Textos dos cartões em PT e EN, congelados |

### 4.4 Frescor dos dados na data da demo (14/11/2026)

- IMERG V07 Late: até 12/11/2026; Early: até 13/11/2026 (Nordeste, diário). IMERG diário municipal: até 14/09/2026.
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
- **Sensibilidade das datas-limite:**
  - À fonte da ET0: com a ET0 na escala do ERA5 (× 0,87), as datas andam no máximo 1 decêndio em 97–99% dos municípios (`arquiteto_final_zarc_et0_sensibilidade.saida.txt`). Em Quixadá, o milho fica em 01/mar e o caupi em 21/mar nas duas escalas; o sorgo vai de 11/mar para 21/mar.
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

- **No MVP:** a prática atual vem do PAM do município (o que se planta e quanto) e de **1 pergunta** à família ("o senhor queimou o roçado em nov/2025?"). O satélite não responde isso: a 375 m, o FIRMS não separa a broca do roçado do incêndio na capoeira (51% dos focos de out–dez caem em pixel arbóreo).
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
- **Área salvável:** o salvamento da floração do milho pede 62 mm na mediana (620 m³/ha). Uma cisterna-calçadão de 52 m³ salva cerca de 0,08 ha num ano mediano. **O salvamento só existe com barreiro ou açude**; o app pergunta o volume.
- **Combustível (corrigido):** o "+0,072 fora do ano" da rodada 1 era quase todo tendência. Contra climatologia + tendência, o combustível do VIIRS (NDVI de fev–jun de t e t−1) acrescenta +0,020 (IC90 +0,001 a +0,042); a tendência sozinha vale +0,098. No portão de 30/set, o índice de combustível e secura com o SMAP dá +0,002 (IC90 −0,041 a +0,044) e ρ −0,03 entre anos: **sem habilidade no total do ano**. Dentro do ano, a ordem entre municípios tem ρ ~+0,2 (`v2_ecologo_indice_combustivel_rz.saida.txt`). O app mostra o combustível **em tercis, como mapa**, com a frase "sem habilidade comprovada no nível do ano", e nenhum número de focos previstos.
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
   - **Troca em ano de luz acesa (grau C, refeita com 1998 e 2024):** pelo balde da rodada 1, a fração de municípios com água na floração do caupi semeado em 11/mar foi de 68% em 2016, **10% em 1998** e 100% em 2024. Semeado em 21/mar: 33%, 15% e 72%. O sorgo de 11/mar teve água em 10% dos municípios em 2016 e 1% em 1998, e por isso **sai da troca** (`v2_arquiteto_r2_fechamento.saida.txt`, bloco E). Em anos normais, o caupi de 21/mar teve água em 93% dos municípios. Leitura: **o caupi do início de março salva um ano como 2016, não um ano como 1998.** Contra um 1998, a proteção é o que já está no chão: a mandioca do ano anterior (Quixadá, 1998: mandioca 0,50 do normal; milho 0,00) e a forragem guardada.
3. **Restrições:**
   - janela sintética tipo-ZARC (±1 decêndio no caupi; incerteza maior no milho e no sorgo), a confirmar no ZARC oficial;
   - semente e maniva disponíveis antes da data-limite;
   - água azul declarada;
   - mão de obra e consumo da família;
   - regras do Garantia-Safra (limiar, cesta e área mínima), **só se conferidas na lei**; senão, saem dos cartões.
4. **Avaliação:** cada estratégia é reencenada nas 28 quadras do IMERG. As sequências de 3 anos são **planos**: cada ano é avaliado na quadra do replay, e o efeito do antecessor (leguminosa, palhada) entra como prior da literatura com grau. O estado do solo entre anos não é simulado no MVP; a memória de novembro até fevereiro é nula (ρ +0,01), então essa simplificação custa pouco na água.
5. **Escolha:** a atual sempre entra. As outras 3 cobrem perfis distintos: calendário (S1, que protege contra um ano como 2016), cauda (S2, que protege contra um ano como 1998) e solo (S3). No MVP a ordem é fixa; os pesos da família ficam para a próxima versão.
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

**Contexto do município** (`arquiteto_final_curvas_quixada.saida.txt`, bloco C; `v2_arquiteto_r2_fechamento.saida.txt`, blocos D, E e G; definição canônica):
- **Milho:** 8 quebras em 28 anos: 1998 (0,00), 2001, 2012 (0,17), 2015, 2016 (0,12), 2023 (0,36), 2024 (0,46) e 2025 (0,30). Grau A.
- **Feijão:** 5 quebras em 28 anos; 0,15 do normal em 2012. Grau A.
- **Milho + feijão (S0):** 6 dos 28 anos abaixo da metade do normal (1998, 2012, 2015, 2016, 2023, 2025); pior ano em 10 = 0,16 (1998, 2012, 2016); mediana 1,05. Grau A, "seu município".
- **Mandioca:** só 10 anos têm as três culturas, todos entre 1998 e 2010. A área foi 0 ha em 2012–2013 e 40 ha em 2016, então **não há mandioca observada nos piores anos depois de 1998** e a carteira do município não é calculável.
- **Datas-limite da janela sintética** (risco ≤ 30%): milho até 01/mar (incerteza maior que ±1 decêndio: o SMAP dá 21/abr, sem validação); caupi até 21/mar (±1 decêndio) em ano normal. Em ano de luz acesa, até ~11/mar, se ainda houver umidade (em 2016, o caupi de 11/mar teve água em Quixadá e o de 21/mar não; em 1998, nenhum dos dois). Grau C.
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
  - perda de carbono com a queima (Primo et al. 2023: −50% em 10 anos numa simulação Century de um sítio; grau C);
  - fuga do fogo para os vizinhos;
  - nenhum mês sem gramínea hospedeira.

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
- **Por que aparece:** janeiro engana (Quixadá teve 150% do normal em jan/1998 e 197% em jan/2016, e os dois anos quebraram). Escalonar mantém uma opção aberta até o último portão de troca.
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
  - **Contra a prática atual:** no estado, a carteira 1/3 milho, 1/3 feijão e 1/3 mandioca leva o "pior ano em 10" de **0,26 (milho + feijão) a 0,36**, e a chance de colher menos da metade de 15% para 11%. São 2.495 município-anos, só onde a mandioca existe. **É um teto:**
    - o placebo do vizinho já dá 0,335, então a parte própria da mandioca fica entre +0,02 e +0,08 (grau B);
    - a carteira real dos municípios entrega cerca de 65% do ganho por cultura;
    - o piso é 0,32 se a maniva faltar.
  - **Nos anos em que a luz NASA acendeu em 30/abr:** pior ano em 10 de 0,13 na S0 e 0,21 na 1/3 (ganho com IC90 por ano de +0,04 a +0,10; n = 585 município-anos, 17 anos).
  - **Replay de 1998 em Quixadá, observado pelo IBGE:** milho 0,00, feijão 0,16, mandioca 0,50. A carteira 1/3 ficou com 0,22, contra 0,08 de milho + feijão. É um ano só (grau A, n = 1). É também o ano em que a S1 não ajudaria (caupi de 11/mar com água em 1 de 10 municípios): a S2 é o escudo de um ano como 1998.
  - O sorgo tem P(ISNA floração < 0,5) de 6,5%, contra 10,1% do milho (grau C). O PAM do sorgo não serve de evidência: são 21 municípios tecnificados.
  - Palma + sorgo: 6.279 contra 4.627 kg MS/ha (Diniz et al. 2017; ensaio único com irrigação em PE; grau C).
  - **O que não usamos como evidência:** o "+6,6 p.p. dos municípios mais diversos" (seção 8.2). É composição (menos milho e feijão) e culturas fora do sequeiro; só com sequeiro, +1,4 p.p. (n.s.).
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
- **No replay e no cartão:** "sem número; faixa da literatura (B·T)". Nenhuma métrica de pior ano.
- **Benefícios:** milho de 2028 em diante sobre solo melhor; banco de proteína para as cabras; menos fogo e menos erosão; meses sem gramínea hospedeira.
- **Lacunas:** não existe ensaio revisado de rotação no semiárido do Ceará, e o PAM não identifica o efeito do antecessor (o placebo falha; seção 5). O efeito real da leguminosa é a lacuna que mais muda o ranking.
- **Riscos a confirmar:**
  - **competição por água, agora com dado:** na entressafra o primeiro metro de solo está seco (W < 0,1 em 49% dos dias), então a perene vive de água abaixo de 1 m, que o SMAP não vê. Pelo GLDAS Noah, a camada de 1–2 m tem ciclo de só 36 mm e acompanha o abril do mesmo ano (ρ +0,90): recarrega menos justamente no ano seco (`v2_agronomo_smap_janelas.saida.txt`, bloco E). A literatura dá cerca de −4% de rendimento com cobertura (Abdalla et al. 2019; grau B·T);
  - mão de obra para implantar e 1–2 anos para estabelecer;
  - se o caupi local é hospedeiro secundário da lagarta.

### 6.3 O plano vivo de 2027 para Dona Francisca

| Portão | O que o QUADRA diz | Evidência |
|---|---|---|
| **P1, hoje (14/nov)** | "O mar está mais quente do que em qualquer ago–out já medido. Num ano qualquer, 2 de cada 10 municípios da região perdem metade do milho. No El Niño mais forte antes deste, cerca de 5 de cada 10 (faixa de 2 a 8); em 1998 e 2016, 7 em 10; em 2024, menos de 1 em 10. Este ano está além do recorde. O solo está seco como em todo novembro, e isso não diz nada sobre a quadra." Ações sem arrependimento: semente de caupi precoce **até dezembro**, procurar maniva para fevereiro, garantir a palma, manter a adesão ao Garantia-Safra, aceiro e palhada em vez de queima. | Modelo único, ano fora: P(2,04) = 0,54 (IC90 0,24–0,75); em 2,46, 0,62 por extrapolação (`v2_clima_portao_novembro_2027.saida.txt`). Na última década, o ONI de novembro teve AUC 0,72, igual à melhor chuva de São José (`v2_arquiteto_r2_fechamento.saida.txt`, A). Contagens: 4 de 7 quadras secas desde 1966; 3 de 5 pelo POWER desde 1982; 2 de 3 catástrofes na era IMERG. SMAP de novembro → fevereiro: ρ +0,01. Banco regional normal (GRACE p57). |
| **P2, janeiro–fevereiro** | "Plante uma parte agora e guarde a outra. Chuva boa em janeiro não garante a quadra: em 2016, janeiro teve cerca do dobro do normal e 7 de cada 10 municípios perderam o milho." No fim de fevereiro: "ainda é cedo". | 31/jan: AUC da soma 0,63 (1998–2015) e 0,27 (2016–2025). 28/fev: 0,71 e 0,46; chuva desde 1/fev 0,65 e 0,66. |
| **Início de março (~10/mar)** | "Com o mar deste ano: se a chuva desde 1º de fevereiro estiver abaixo de 75% do normal e ainda houver umidade, a metade guardada vai para o caupi até ~11 de março. Se não houver umidade, ela fica sem grão. Confirmar com o técnico: a semente chegou?" | Chuva desde 1/fev acesa em 10/mar: 94% dos municípios em 1998, 100% em 2016 e 0% em 2024 (descritivo, n = 3). Caupi de 11/mar com água: 7 em 10 municípios em 2016 e 1 em 10 em 1998 (balde, grau C). |
| **P3, 19/mar** | Luz em quatro estados. "Vermelho: a chuva e o solo dizem seco. Amarelo: só a chuva diz seco. Caupi só se ainda couber; sem sorgo de grão." Cinza-amarelo: "os dois instrumentos discordam; o técnico decide". | 2016–2025: vermelho 5,3 em 10 quebram; amarelo 2,1; verde 0,9. Em 2022, a chuva acendeu em 142 municípios e o SMAP em nenhum (3 quebras). Em Quixadá, 3 acertos em 9 alertas da chuva e nenhum do solo. O teste da tradição está na seção 7, inovação 5. |
| **P4, 30/abr** | "É quando o solo mais confirma." Ação graduada: guardar forragem, segurar a venda dos animais, cortar o milho para as cabras se a luz se repetir e o técnico confirmar. Sem salvamento com água: a cisterna de 16 m³ é de beber. | 2016–2025: vermelho 4,1 em 10; amarelo 3,4; verde 0,8. Em 2016, o SMAP acendeu em metade do estado (91 de 182). **Em 30/abr só cabe salvar; por isso, em 2027, a proteção vem de P1, P2 e do início de março.** |
| **Junho** | "Verde do satélite em abril–maio: {x}% do normal do seu município. Quando ficou abaixo de 90%, 7 a 8 de cada 10 municípios perderam mais da metade do milho. O IBGE confirma no ano que vem." | VIIRS NDVI abr–mai, testemunha, grau A como testemunha (`v2_designer_verde_viirs.saida.txt`). |
| **P5, até 31/ago/2027 (data fixa)** | "O fogo vem pelo calendário; a decisão é antes de setembro." Palhada, aceiro, fenação do excedente se a quadra vier verde, perene em nível. Nova faixa de maniva na quadra de 2028 (fevereiro a abril). | 27% dos focos até 30/set e 72,9% em out–dez (`v2_ecologo_calendario_fogo.saida.txt`). Combustível como mapa em tercis, sem previsão de focos. |

**Cartão da família no P1 (imagem; no máximo 3 números):** "Quixadá, 14 de novembro de 2026. O solo está seco como em todo novembro: isso é normal e não diz nada sobre a quadra. O mar está mais quente do que em qualquer agosto–outubro já medido. Num ano qualquer, 2 de cada 10 municípios da região perdem metade do milho; no El Niño mais forte que já tínhamos visto, cerca de 5 de cada 10. Agora: guardar semente de feijão-de-corda precoce, procurar maniva para fevereiro, não queimar. Confirmar com o técnico: a semente chega antes de 10 de março?" Rodapé: "Medido no seu município · Acertos contados na sua região · Grau B".

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

**Leitura que vai para o deck (só no slide de honestidade, nunca no slide 1):** o padrão "mais diverso perdeu menos" aparece nas duas grandes secas do Ceará e some em anos normais. Mas é **composição, não diversidade**: é sobretudo menos dependência de milho + feijão, as culturas que mais caíram na seca (0,48 e 0,58 da base), e culturas fora do sequeiro (melão, soja e sorgo tecnificados, ~1,03–1,08). Entre as culturas de sequeiro, o efeito desaparece. Isso é coerente com o achado (ii) do artigo-âncora (diversificar além da rotação simples rende pouco) e com o (iii) (benefício menor com pouca chuva). **Por isso o QUADRA não promete bônus de diversidade.** É associação municipal num episódio, não efeito de rotação no talhão. Grau B.

### 8.3 Como o método do artigo-âncora entra no roteiro

O protótipo municipal mostrou por que a escala tem de ser o talhão: no PAM, o efeito do feijão anterior e o do feijão futuro (placebo) têm o mesmo tamanho (`v2_pesquisador_ia_precrop_dml.saida.txt`). O desenho do próximo passo, à maneira de Kluger:
1. **Unidade:** pixel ou talhão de 30 m, não o município.
2. **Tratamento:** a sequência em t−1 (roçado após pousio, roçado repetido, após leguminosa), tirada do MapBiomas anual (classes a conferir: o roçado do semiárido tende a cair em "mosaico de usos") ou de uma classificação HLS calibrada nas proporções do PAM.
3. **Desfecho:** pico de NDVI ou EVI (HLS/Landsat/VIIRS) calibrado contra o rendimento do PAM por município, como Kluger fez com condados.
4. **Modificadores:** o estado da água nos portões (chuva IMERG desde 1/fev, SMAP L4), ET0 do POWER, relevo do SRTM e ONI. É aqui que entra o que o artigo não tem.
5. **Validação:** floresta causal honesta com cross-fitting por bloco de anos, teste de calibração, placebo do antecessor futuro e IC por ano.

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
- **Gatilho tipo Garantia-Safra (AUDIT.md):** com o IMERG em fev–mai, o risco de base no município fica perto de 50% nos dois sentidos (`v2_economista_gatilho_smap.saida.txt`). A comparação com o SMAP usou outra escala (média de percentis) e será refeita antes de qualquer frase.

### 9.4 Grau de evidência por tipo de afirmação

| Grau | O que é | Exemplos |
|---|---|---|
| A | Validado com dado local observado, por ano | Correlação entre culturas no PAM, curva de habilidade por era, regra de chuva, carteira estadual e seu piso, continuidade VIIRS × MODIS |
| B | Meta-análise ou síntese multi-sítio; poucos anos ou poucos episódios com dado local | Luz principal de 2027 (escolhida depois de ver 2016–2025), duas missões (10 quadras, 1 grande seca), parte própria da mandioca na carteira, P1 do oceano, El Niño × quebra (contagem), associação diversidade × resiliência |
| B·T | B transferido de outro clima (meio grau abaixo) | Leguminosa antecessora, rotação diversa, achados de Kluger et al. 2025, custo da cobertura |
| C | Modelo, simulação, ensaio único, ordem validada sem nível | Datas-limite sintéticas, contrafactual do caupi guardado (1998, 2016, 2024), janela da maniva, balde em percentil em 1998, ponte verde, palma + sorgo, carbono de Primo, açude numa AOI |
| D | Suposição ou resumo de congresso | Volume de cisterna suposto, preço de forragem, forçante do SMAP L4 v008 (só por resumo do EGU) |

### 9.5 Limitações

1. **Nenhum efeito de rotação foi observado no Ceará.** O PAM valida o efeito do clima sobre cada cultura, não o do antecessor. O protótipo de IA causal confirma: o placebo do antecessor futuro dá o mesmo efeito.
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
12. **Regras institucionais não conferidas:** o limiar do Garantia-Safra (40% ou 50%), a cesta, a área mínima e a janela do ZARC oficial de Quixadá. Sem conferência, não entram em slide.
13. **Muitos testes sobre os mesmos anos.** A rodada 2 somou dezenas de comparações às da rodada 1. Só os números da tabela 9.2 vão ao pitch; o resto (TSA do Atlântico, dipolo × início, combustível × fogo, "ONI além da chuva", regra de 15 dias de chuva) é exploratório.

### 9.6 O que ainda dá para fazer antes do júri

- **Conversa com um técnico de ATER ou um agricultor** (José, até sáb 18h). É a ação de maior retorno para o Impacto: 1 frase com permissão e 1 mudança feita por causa dela.
- **Feito no fechamento:** SMAP L3 consolidado (sem mudança: 0,774 em 30/abr); AUC por era nos 5 portões; congelamento interno da regra de 2027 (sha256 no bloco B); contrafactual do caupi em 1998.
- **Documento do SMAP L4 v008:** conferir a base da climatologia do percentil e a forçante de chuva da versão 8.
- **Kluger et al. 2025:** conferir na versão publicada da ERL os números do arXiv (4,5% e 3,7×) antes de qualquer slide numérico.
- **Hash público** da regra de 2027 e da leitura VIIRS da safra de 2026: **só com o OK explícito do José** (voz pública).
- Refazer `designer_confianca_alertas` com a luz nova.
- Refazer o gatilho tipo Garantia-Safra com a mesma escala para o IMERG e o SMAP (AUDIT.md; não vai a slide).
- Cortados por custo ou dependência: seleção aninhada do M2, FIRMS NRT (exige chave), LSPA, código de barras contra o CDL do Texas, SMAP ao vivo.

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
| ET0 do CE | 1.970 (ERA5) a 2.280 (POWER) mm/ano; 2,5 a 2,8 vezes a chuva da mesma fonte; supera a chuva em 10 de 12 meses nas duas | um valor único chamado de "correto" |
| Ureia/milho | 1,85 em out/2026; pico de 4,00 em abr/2026; média de 2000–2020 = 1,51 (`cetico_r2_ureia.py`) | "4,0 agora" |
| Quebra | Produção ÷ área plantada < 50% da mediana do município nos outros anos; milho 21,5% e feijão 14,6% (1998–2025) | mediana móvel; área colhida; limiar de 60% |
| Milho 2012 | −69% no estado; 75% dos municípios em quebra | "71%", "50%" |
| Registro de chuva | IMERG (eras TRMM e GPM), 28 quadras 1998–2025; POWER 1981–2026 é reanálise (MERRA-2 corrigida) | "28 years of GPM"; "44 quadras observadas" |
| **Carteira** | Contra a S0: 0,26 → 0,36 (teto); parte própria da mandioca +0,02 a +0,08 (placebo do vizinho 0,335); piso 0,32; mundo real ~65% do ganho; nos anos de luz NASA acesa em 30/abr, 0,13 → 0,21 (IC90 do ganho +0,04 a +0,10); cauda de 5 a 7 anos ruins | "0,15 → 0,36" como ganho sobre a prática; "raised"; "três episódios"; somar o +6,6 ao CVaR |
| Contrafactual do caupi | Caupi de 11/mar com água na floração (balde): 1998 1 em 10; 2016 7 em 10; 2024 10 em 10. Sorgo de 11/mar: 2016 1 em 10; 1998 0 | "sorgo até 19/mar" na troca; "São José abre a janela em 1998" |
| Diversidade | +6,6 p.p. nas secas (+10,5 em 1998; 0,0 no placebo), sobretudo composição; só sequeiro +1,4 (n.s.). Rótulo: "composição, não diversidade" | no slide 1; "diversificar o sequeiro protege" |
| Fogo | 72,9% dos focos em out–dez e 27% até 30/set (2015–2025); 17% da área do CE em células de ~375 m com ≥ 1 foco (2012–2025); combustível +0,02 sobre a tendência, sem habilidade no total do ano | "17,4% do Ceará queimou"; "+0,072"; número de focos previstos |
| VIIRS NDVI | Continuidade do MODIS (r 0,986 no estado); testemunha de fim de safra (AUC ~0,8; abaixo de 90% do normal, 7,5 em 10 quebram); caatinga out/2026 z +1,07, 3º de 15; nov/2026 provisório | "o NDVI decide no portão" |
| Deslocamento do NDVI | +0,03 a +0,05 desde 2020 nos dois sensores com a chuva IMERG; ~0,01 próprio do MODIS; causa aberta | "deriva do Terra" como causa principal |
| Kluger et al. 2025 | "Kluger, Di Tommaso & Lobell (ERL 2025)"; achados qualitativos do resumo | "Stanford showed"; "4,5%" e "3,7×" até conferir na versão publicada |
| São José | "A chuva do dia diz tanto quanto toda a chuva até ali, que é pouco (ρ ≈ +0,3; n = 28)" | "tradition is weak, not wrong" |
| Reprodução | "Recomputado em 4 scripts a partir dos mesmos dados"; o juiz reproduziu do `.nc` cru | "reproduzido de forma independente por 4 scripts" |
| Pontos globais | 40 de 47 pontos terrestres tropicais sem mês de quebra térmica; SMAP L4 cobre 99,6% da terra entre 60°S e 60°N | "86% dos trópicos" |

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
- **ET0:** o ~1.960 mm/ano da síntese é a ET0 do ERA5, e os 2.279 mm/ano do rascunho são a do POWER. Os dois estão certos; a diferença de 15% vem do viés quente da Tmax do POWER.
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

**Cortados de saída do MVP:** M2 e seleção aninhada; trajetórias diárias animadas e barras de ISNA diárias; cartões para 184 municípios e pesos da família; globo, MapLibre, Esri e Nominatim; auditoria gerada em Python (vira `AUDIT.md`); suíte de 30 casos adversariais (vira lista branca); do painel "hoje", a chuva da estação seca, o GWS do CLSM e os açudes do Landsat; pontos globais (vira 1 linha); NLDAS-2, GLDAS Noah e IMERG Early fora do recibo; código de barras ao vivo; áudio e TTS; modo global e SMAP ao vivo; ECOSTRESS, GNN e Prithvi; simulador de WhatsApp; FIRMS NRT, LSPA e CDL; explicador LLM em tempo de execução.

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
   - Rodapé: "Staggered sowing and legume-that-stays: no worst-year number yet; not in the record."
6. **"NASA is the engine, IBGE is the referee. How we used SI, honestly."**
   - *On screen:* IMERG, SMAP L4, VIIRS, GRACE/GRACE-FO, SRTM. *In our analysis (repo):* SMAP L3, GLDAS-2.1/2.2, MODIS, Landsat/HLS, POWER, NEX-GDDP, NLDAS-2. *Roadmap:* ECOSTRESS, NISAR, Prithvi.
   - "Every curve by era: the rule that worked in 1998–2015 failed in 2016–2025, and we show it. Fair baselines: SMAP was compared with the best rain reading, and lost the main-light role."
   - "Random validation lies (**0.49 vs −0.08**)."
   - "What did not work: causal ML on county statistics (a placebo failed); the diversity link is composition, not diversity (rain-fed crops only: **+1.4 points**, not significant)."
   - "Satellites know the bad year, not the bad county (within-year AUC up to ~**0.65**; geography alone 0.61)."
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
| **Best Use of Science** | 1ª | Curvas validadas por ano e por era; linha de base justa (o SMAP perdeu o posto de luz principal para a melhor leitura da chuva); regra de 2027 congelada com hash; IBGE como árbitro; resultados negativos declarados (soma em 2016–2025, Quixadá, SMAP de novembro, IA causal no PAM, média de percentis); recibo A–D com marca ·T; ponte com Kluger et al. 2025. |
| **Best Storytelling** | 2ª | 2016, "a mesma chuva da NASA, lida de dois jeitos"; 2022, o alarme falso que a segunda missão segurou; "duas secas, dois escudos" (1998 e 2016); São José testado com respeito; 2027 ao vivo; Dona Francisca. |
| **Local Impact** | 3ª | Ceará, 184 municípios, técnico no circuito, ações baratas em novembro, decisão do caupi no início de março, maniva e semente; validação com um técnico de ATER (se feita). |
| **Best Use of Data** | 4ª | Duas missões na luz (GPM IMERG e SMAP L4), o L3 como checagem, o VIIRS como continuidade do MODIS e testemunha, a escala útil medida entre sensores, o sentinela de deriva, o relato copiado no PAM. |
| **Galactic Impact** | Indicação | Motor global (o SMAP L4 cobre 99,6% da terra entre 60°S e 60°N; o IMERG é quase global); "40 de 47 pontos terrestres tropicais sem mês de quebra térmica". |
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
- FIRMS NRT, LSPA, CDL e o simulador de WhatsApp foram cortados; o pré-registro só sai com o OK do José; o mapa usa o GeoJSON sem tiles (E).

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
5. Conferir na lei o limiar, a cesta e a área mínima do Garantia-Safra, e a janela do ZARC oficial de Quixadá.
6. Publicar ou não o hash da regra de 2027 (sha256 `41b7c820fe6693dd1ac2336075585a36fc6ec03fd9e1133c4537d8cf984fdb41`) e a leitura VIIRS da safra de 2026.
7. Nome final: QUADRA (recomendado) ou a reserva Field Replay.
8. Gravar ou não 45 s de voz humana em português para o cartão (até sáb 18h).
9. Confirmar se fatos do "Encontro dos Profetas da Chuva" de Quixadá podem ser citados.

---

## Project summary (English)

QUADRA (the sertão's word for the rainy season) lets farmers and extension agents stress-test rotation plans against NASA's record before committing. Kluger, Di Tommaso and Lobell (ERL 2025) showed with satellites and causal machine learning that rotation benefits change with climate, but only in temperate breadbaskets and without water data. QUADRA takes the question to the semi-arid tropics, where a rotation is a policy with checkpoints and what decides is when the water shows up.

QUADRA places the checkpoints where three measured curves cross: what the data already know (validated by leaving whole years out, and always shown for 1998–2015 and 2016–2025 separately), what is still possible (planting deadlines from an FAO-56 water balance driven by IMERG and NASA POWER), and when satellites can see (optical sensors go partly blind at decision time; SMAP's radiometer sees through clouds). The key finding is about how to read NASA water data. Counting IMERG rain from January 1 worked until 2015 and failed in the last decade, because wet Januaries hid dry seasons. The same IMERG rain counted from February 1 holds up in both periods. On March 19, 2016, the last day to switch crops and the closest analog to today's record El Niño, rain counted from January flagged 7 of Ceará's 182 counties; counted from February, all 182; 7 in 10 counties then lost their corn. NASA's SMAP soil moisture is the second mission that confirms. When both agreed on March 19, 5 in 10 counties lost their corn; with rain alone, 2 in 10; with neither, 1 in 10. In 2022, rain flagged 142 counties and SMAP none, and only 3 failed. The light is regional: it tells the year, not the county, and the screen says so. The 2027 rule is frozen with an internal hash; it was chosen after seeing the data, with thresholds fixed beforehand.

For each county, QUADRA compares the current practice with three alternative three-year strategies over every season in the IMERG record. Observed yields from Brazil's IBGE act as referee, and where the record cannot measure a strategy, the card says so. Against today's corn and beans, an equal-thirds corn–beans–cassava portfolio, computed on county yields, had a worst-year-in-ten of 36% of normal versus 26% (a ceiling: part of it is averaging). In county-years when NASA's April light was on, it was 21% versus 13%. Staggered sowing protects against a 2016-type year (early-March cowpea had water in 7 of 10 counties), while cassava planted the year before protects against a 1998-type year (when not even cowpea had water). Every number carries a receipt (NASA source, scale, validation, A–D grade), and an audit file shows where the tool fails, including the county where the soil light never hit. The engine is global; the demo is Ceará. NASA evidence. The farmer decides.

## Use of SI (AI) tools

Inside the product, SI appears in five places:
1. A physics-guided crop-water twin (FAO-56 water balance) whose soil-water state is calibrated against NASA SMAP L4 and validated by leaving whole years out.
2. Checkpoint alerts whose skill is measured without look-ahead and shown separately for 1998–2015 and 2016–2025. The main light (IMERG rain counted from February) was chosen by a declared criterion (the reading whose worst era-and-checkpoint score is highest) after seeing 2016–2025, with thresholds fixed before testing (75% from round 1; 20 in commit 48a3608). SMAP L4 confirms it as a second mission. The 2027 rule was frozen on 14/11/2026 with an internal hash, and an out-of-distribution warning flags this year's record El Niño.
3. An exact search over rotation strategies that ranks them by tail risk (CVaR) against current practice, with a neighbour placebo, a declared floor for years without cassava cuttings, and "no number" where the record cannot measure a strategy.
4. A drift and data-quality sentinel that downgrades evidence automatically. It flagged Terra's documented orbit drift in land surface temperature, a post-2020 greening seen by two sensors, copied year-to-year yield reports, and SMAP's dry-season gaps and duplicated dates.
5. A large language model that only drafts the text on each card. It works offline from the engine's numbers, and a whitelist check blocks any number the engine did not produce.

We also report what did not work: causal machine learning on county statistics could not identify a rotation effect (a placebo test failed), November soil moisture does not predict the rainy season, and SMAP soil moisture alone adds about nothing over the best reading of IMERG rain.

To build QUADRA, the team used Anthropic's Claude (Claude Code) as a coding and analysis assistant. This included a council of AI agents that proposed, debated, re-analysed new NASA data and adversarially reviewed designs over two rounds. Every reported number comes from a script in the project repository that a person can rerun. No model was trained on LLM outputs, and no LLM is called at run time.
