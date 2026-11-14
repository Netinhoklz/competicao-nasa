"""Integrador (v4): dados do catalogo de rotacoes comprovadas (fonte unica para o .md e o .json).
Cada configuracao traz o texto da tabela (MD) e os campos do motor (JSON).
Efeitos em % sao convertidos para lnRR = ln(1 + p/100) no JSON.
So entram configuracoes com voto majoritario 'incluir' ou 'incluir_com_ressalva' na R2.
"""

# ---------------- DOIs (todos tirados de artigos/indice.csv ou do texto do proprio artigo) ----------------
ZHAO = "10.1038/s41467-022-32464-0"
ZHAO_DADOS = "10.6084/m9.figshare.20290923"
MUD25 = "10.1038/s41467-025-64567-9"
MUD22 = "10.1007/s13593-022-00816-1"
FRANKE = "10.1016/j.agee.2017.09.029"
RUSI = "10.1007/s13593-011-0040-2"
YANG = "10.1038/s41467-023-44464-9"
BOWLES = "10.1016/j.oneear.2020.02.007"
RENWICK = "10.1088/1748-9326/ac1468"
GAUDIN = "10.1371/journal.pone.0113261"
SMITH = "10.1038/s43247-023-00746-0"
MACLAREN = "10.1038/s41893-022-00911-x"
RASM = "10.1126/science.adj1914"
RAVELO = "10.1038/s41467-025-67757-7"
BEILL = "10.1111/gcb.15747"
KING = "10.1002/eap.1648"
KLUGER = "10.1088/1748-9326/ae0f45"
SEIFERT = "10.2134/agronj2016.03.0134"
BEAL = "10.2134/agronj2019.03.0157"
ZHOU = "10.1111/gcb.17556"
MARINI = "10.1088/1748-9326/abc651"
LUZ = "10.3390/su152015091"
SOUZA24 = "10.3390/stresses4040045"
MELO = "10.1590/s0103-84782013005000108"
NASC = "10.1590/s0100-06832008000200013"
ANDNETO = "10.1590/s1415-43662010000200002"
MIRANDA = "10.15446/agron.colomb.v38n1.78957"
MONTE = "10.5194/adgeo-48-19-2019"
SOUZA11 = "10.1590/s0006-87052011000300030"
SOUZA15 = "10.1590/1983-21252015v28n417rc"
LIMAF = "10.1590/s0100-204x2000000500008"
NEVES = "10.1590/0103-8478cr20131657"
PEREZ = "10.1590/s0100-06832006000300015"
MARTINS = "10.1590/s0100-204x2015000200010"
SACRA = "10.1590/s0100-06832013000300025"
PRIMO = "10.1016/j.jenvman.2023.117594"
DINIZ = "10.1590/s0100-204x2017000900004"
LIMA18A = "10.1590/1983-21252018v31n122rc"
LIMA18B = "10.1590/1807-1929/agriambi.v22n2p113-118"
PINHEIRO = "10.5424/fs/2018271-12267"
MENEZES = "10.1023/a:1021172530939"
PACH11 = "10.1590/s0100-06832011000500033"
PACH13 = "10.1590/brag.2013.041"
PACH17 = "10.1590/1983-21252017v30n102rc"
AZAMB = "10.1590/1808-1657000012013"
MATTOS = "10.5380/dma.v55i0.72576"
FAUST = "10.1590/1519-6984.248154"
KENIS = "10.1127/entomologia/2022/1659"
PEREIRA = "10.3390/insects14070582"
XING = "10.1093/biosci/biaa067"
JIN = "10.3390/agriculture12111759"
SEM_DOI = None  # Andrade 2025, Silva 2022, Jardim 2020, Zonta 2016: fora de artigos/indice.csv (DOI nao verificado)

# cond = (aridez, n_kg_ha, produtividade, duracao)
C = []


def add(**k):
    C.append(k)


# =====================================================================================
# TABELA 1 — ROTACAO / SUCESSAO NO TEMPO
# =====================================================================================
add(id="ne_s0_para_rotacao_tempo", tipo="rotacao", t=1,
    nome="Consórcio milho+feijão (S0, prática atual) → rotação no tempo milho/caupi",
    cult="milho, caupi", ant="consórcio milho+feijão (S0)", suc="milho solteiro após caupi solteiro",
    base="o próprio consórcio S0",
    ef_md="NÃO MEDIDO em nenhum artigo do catálogo. Cartão de sensibilidade: central 0; 0 a +9% (controle diverso não leguminoso, CD2 6–9, N ≤ 50, base aberta de Zhao: +9,4%, IC por sítio 5,0–14,4); até +14% só como teste de sensibilidade. Cultura seguinte.",
    ef=("rendimento do milho (cultura seguinte)", 0.0, 0.0, 9.0, "%", "cultura_seguinte"),
    onde="Semiárido NE (alvo); nenhum sítio medido",
    mod="O controle do Zhao nunca contém leguminosa (Eq. 1, p.6); a decisão S0 × rotação sai da sequência inteira (LER do consórcio ~1,15 no sequeiro contra o rendimento solteiro de cada ano, preço local) e do risco",
    cond=("qualquer", "≈0", "baixa", "não medida"),
    g="D", T="T3", ne="nao", ne_md="NÃO como número: o contraste nunca foi medido; é o ensaio prioritário (faixas que trocam de lugar)",
    gl="Não", ref="Integrador, a partir de Zhao 2022 (Eq. 1) e da base aberta (v4_engenheiro_debate_base_diversa)",
    doi=[ZHAO, ZHAO_DADOS], pg="Zhao p.6 Eq. 1; base aberta, bloco 1 do script do engenheiro")

add(id="ne_lg_cereal_sequeiro_quente", tipo="rotacao", t=1,
    nome="CARTÃO NE: leguminosa de grão → cereal tropical em sequeiro quente-seco, N ≈ 0 (síntese do conselho)",
    cult="caupi, amendoim, feijão → milho, sorgo, milheto", ant="leguminosa de grão (faixa comum, sem ranking de espécie)", suc="milho, sorgo ou milheto solteiro",
    base="cereal solteiro após antecessora não leguminosa ou cereal contínuo",
    ef_md="+24% (central) com faixa +2% a +49%; só no ano colhido. Central = mediana das estimativas dadas pelos votantes; limites = Mudare < 500 mm (IC inferior +2%) e Zhao análogo amplo caupi→cereal (+48,6%). Cultura seguinte.",
    ef=("rendimento do cereal seguinte (ano colhido)", 24.0, 2.0, 49.0, "%", "cultura_seguinte"),
    onde="Estrato AI 0,2–0,5 e MAT ≥ 20 °C (análogo do CE, AI 0,34 pelo POWER)",
    mod="N (descontar −6 a −7% por 50 kg N/ha); ano seco (LGP < 150 d) alarga o IC até 0 sem mexer no centro; irrigado usa a faixa baixa; quebra entra à parte",
    cond=("AI 0,2–0,5; vale também < 500 mm", "0–50 (sem desconto); desconto acima", "baixa (aplicar sobre a mediana dos anos colhidos)", "1º ciclo"),
    g="B", T="T1", ne="parcial", ne_md="Sim contra milho/sorgo solteiro e no ano colhido; NÃO contra o consórcio S0",
    gl="Sim para trópicos secos de baixo insumo", ref="Síntese: Zhao 2022; Mudare 2025 (Source Data); Franke 2018",
    doi=[ZHAO, ZHAO_DADOS, MUD25, FRANKE], pg="Mudare Source Data aba S5-S6 (MAP, Legume < 500); Zhao base aberta (metodólogo A3); Franke Tab. 3")

add(id="zhao_leg_global", tipo="rotacao", t=1,
    nome="Leguminosa antecessora → cultura principal (média global)",
    cult="qualquer leguminosa → qualquer principal (91% cereais)", ant="leguminosa (grão, forragem ou adubo verde)", suc="cultura principal",
    base="antecessora não leguminosa",
    ef_md="+20,4% (IC95 17,7–23,1); mediana +10,2%; 73,6% positivas, 25,7% negativas; base aberta: +18,2% (IC por sítio 14,7–23,0). Cultura seguinte.",
    ef=("rendimento da cultura principal", 20.4, 17.7, 23.1, "%", "cultura_seguinte"),
    onde="Global, 462 estudos, 53 países, 1959–2020",
    mod="N e diversidade do controle (maiores na meta-floresta); aridez pesa pouco; rendimento zero (quebra) EXCLUÍDO",
    cond=("qualquer; análogo AI 0,2–0,5 e MAT ≥ 20 °C dá +23,6% (49 sítios)", "nulo > 236", "baixa amplia", "1º ciclo em diante"),
    g="A", T="T1", ne="parcial", ne_md="Direção e relativo transferem (análogo previsto +23,5% contra +23,6% observado); só contra base sem leguminosa e no ano colhido",
    gl="Sim, como prior ajustado por N, diversidade e cultura", ref="Zhao et al. 2022, Nat Commun 13:4926",
    doi=[ZHAO, ZHAO_DADOS], pg="p.2 Fig. 2a; p.7 (exclusão de zero); base aberta md5 conferido")

add(id="zhao_leg_milho", tipo="rotacao", t=1,
    nome="Leguminosa → milho", cult="leguminosa → milho", ant="leguminosa", suc="milho", base="antecessora não leguminosa",
    ef_md="+28,9% (IC95 25,5–32,2). Base aberta, análogo amplo quente-seco: +39,6% (IC 27,2–53,6; 24 sítios); com N ≤ 50: +59,0% (11 sítios). Cultura seguinte.",
    ef=("rendimento do milho", 28.9, 25.5, 32.2, "%", "cultura_seguinte"),
    onde="Global; análogo sem nenhum sítio no Brasil", mod="N (−7%/50 kg), diversidade do controle (significativa no milho)",
    cond=("qualquer", "0–236", "baixa amplia", "1º ciclo"),
    g="A", T="T1", ne="parcial", ne_md="Contra milho solteiro; milho do semiárido rende ~0,55–0,59 t/ha: aplicar em lnRR",
    gl="Sim", ref="Zhao et al. 2022", doi=[ZHAO], pg="p.5 (texto)")

add(id="zhao_leg_sorgo", tipo="rotacao", t=1,
    nome="Leguminosa → sorgo", cult="leguminosa → sorgo", ant="leguminosa", suc="sorgo", base="antecessora não leguminosa",
    ef_md="+28,4% (IC95 22,8–34,0; 33 estudos). Base aberta quente-seco: +57,2% (IC 30,8–100,5; 8 sítios). Mudare soja→sorgo +18,48% (9,72–27,95; n=106). Cultura seguinte.",
    ef=("rendimento do sorgo", 28.4, 22.8, 34.0, "%", "cultura_seguinte"),
    onde="Global", mod="No sorgo a diversidade do controle não modera (ns, Zhao p.3); o 'ns' do Franke é confundimento com a zona (p=0,435)",
    cond=("qualquer", "0–236", "baixa amplia", "1º ciclo"),
    g="A", T="T1", ne="sim", ne_md="Mesma faixa do milho; atenção ao portão de pragas (sorgo hospeda lagarta e alimenta o bicudo adulto)",
    gl="Sim", ref="Zhao et al. 2022; Mudare et al. 2025", doi=[ZHAO, MUD25], pg="Zhao Supl. Tab. 2 (lida pelo especialista); Mudare Source Data Fig. 2b (conferido)")

add(id="zhao_caupi", tipo="rotacao", t=1,
    nome="Caupi como antecessora (qualquer principal)", cult="caupi → principal", ant="caupi", suc="cultura principal", base="antecessora não leguminosa",
    ef_md="+28,7% (IC95 22,8–34,5; 32 estudos). Base aberta: caupi→milho global +26,6% (14 sítios); caupi→cereal análogo amplo +48,6% (IC 32,4–75,1; 11 sítios). Cultura seguinte.",
    ef=("rendimento da cultura principal", 28.7, 22.8, 34.5, "%", "cultura_seguinte"),
    onde="Global, sobretudo trópicos", mod="Ordem entre espécies instável entre meta-análises (no Franke o caupi tem o menor efeito)",
    cond=("qualquer", "0–236", "baixa amplia", "1º ciclo"),
    g="B", T="T1", ne="sim", ne_md="É a leguminosa do sertão; usar a faixa comum, sem prêmio de espécie",
    gl="Sim, trópicos secos", ref="Zhao et al. 2022", doi=[ZHAO, ZHAO_DADOS], pg="Supl. Tab. 1; base aberta (v4_leguminosas_antecessoras_debate C1; v4_metodologo_debate_checagens C)")

add(id="mudare_caupi_milho", tipo="rotacao", t=1,
    nome="Caupi → milho (contra milho contínuo)", cult="caupi → milho", ant="caupi", suc="milho", base="milho contínuo",
    ef_md="+14,68% (IC95 3,76–26,74; n=81). Cultura seguinte.",
    ef=("rendimento do milho", 14.68, 3.76, 26.74, "%", "cultura_seguinte"),
    onde="Global (par de espécies)", mod="N; sem recorte de clima para o par",
    cond=("qualquer", "não estratificado", "não estratificado", "1º ciclo"),
    g="B", T="T2", ne="sim", ne_md="É o par central do CE; define o limite inferior realista; só contra milho solteiro",
    gl="Sim nos trópicos", ref="Mudare et al. 2025, Nat Commun 16:9552", doi=[MUD25], pg="Supl. Tab. 5 p.23; Source Data Fig. 2b (conferido pelo integrador)")

add(id="franke_caupi_cereal", tipo="rotacao", t=1,
    nome="Caupi → cereal (África Subsaariana)", cult="caupi → milho, sorgo, milheto", ant="caupi", suc="cereal", base="cereal contínuo (consórcio excluído)",
    ef_md="+0,40 t/ha (EP 0,09; p=0,0004); 1,21 → 1,60 t/ha (+33%); IC95 aprox. 0,22–0,58 t/ha (±1,96·EP, calculado); n=91. Cultura seguinte.",
    ef=("rendimento de grão do cereal", 0.40, 0.22, 0.58, "t/ha", "cultura_seguinte"),
    onde="África Subsaariana, todas as AEZ, inclusive a sudano-saheliana",
    mod="Os autores atribuem o efeito menor ao ambiente marginal do caupi, não à espécie; reposição de N 10–80 kg N/ha (Tab. 4)",
    cond=("todas as AEZ", "maioria sem ou com pouco N", "baixa", "1º ciclo = ciclos seguintes"),
    g="B", T="T1", ne="sim", ne_md="Mesma espécie e mesmo tipo de ambiente; usar o relativo (+33%), não as t/ha",
    gl="Sim, trópicos secos", ref="Franke et al. 2018 (online 2017), AGEE 261:172–185", doi=[FRANKE], pg="Tab. 3 linha Cowpea (conferida no XML)")

add(id="mudare_caupi_milheto", tipo="rotacao", t=1,
    nome="Caupi → milheto (contra milheto contínuo)", cult="caupi → milheto", ant="caupi", suc="milheto", base="milheto contínuo",
    ef_md="+29,84% (IC95 3,27–63,24; n=27). Cultura seguinte.",
    ef=("rendimento do milheto", 29.84, 3.27, 63.24, "%", "cultura_seguinte"),
    onde="Global, sobretudo Sahel", mod="IC largo, poucas observações",
    cond=("seco", "não estratificado", "baixa", "1º ciclo"),
    g="C", T="T2", ne="parcial", ne_md="Milheto pesa pouco no CE; análogo forrageiro",
    gl="Sim, Sahel", ref="Mudare et al. 2025", doi=[MUD25], pg="Supl. Tab. 5 p.23; Source Data Fig. 2b (conferido)")

add(id="zhao_amendoim", tipo="rotacao", t=1,
    nome="Amendoim como antecessora (qualquer principal)", cult="amendoim → principal", ant="amendoim", suc="cultura principal", base="antecessora não leguminosa",
    ef_md="+19,2% (IC95 12,0–26,3; 21 estudos). Base aberta, amendoim→cereal no análogo amplo: +35,2% (IC 19,4–54,4; 14 sítios). Cultura seguinte.",
    ef=("rendimento da cultura principal", 19.2, 12.0, 26.3, "%", "cultura_seguinte"),
    onde="Global", mod="Faixa comum; valor próprio está no portão de nematoides (grau C)",
    cond=("qualquer", "0–236", "baixa amplia", "1º ciclo"),
    g="B", T="T1", ne="parcial", ne_md="Amendoim é pouco plantado no CE; sem prêmio de espécie",
    gl="Sim", ref="Zhao et al. 2022", doi=[ZHAO, ZHAO_DADOS], pg="Supl. Tab. 1; base aberta (metodólogo C)")

add(id="franke_amendoim_cereal", tipo="rotacao", t=1,
    nome="Amendoim → cereal (África)", cult="amendoim → cereal", ant="amendoim", suc="cereal", base="cereal contínuo",
    ef_md="+0,62 t/ha (EP 0,11; p<0,0001); 1,22 → 1,84 t/ha (+51%); IC95 aprox. 0,40–0,84; n=35. Cultura seguinte.",
    ef=("rendimento de grão do cereal", 0.62, 0.40, 0.84, "t/ha", "cultura_seguinte"),
    onde="África Subsaariana", mod="Reposição de N 60–67 kg N/ha; a ordem contra o caupi se inverte no Zhao e no Mudare",
    cond=("todas as AEZ", "baixo", "baixa", "1º ciclo"),
    g="B", T="T1", ne="parcial", ne_md="Faixa comum, sem ranking", gl="Sim", ref="Franke et al. 2018", doi=[FRANKE], pg="Tab. 3 linha Groundnut (conferida)")

add(id="mudare_amendoim_milho_ns", tipo="rotacao", t=1,
    nome="Amendoim → milho e → milheto (contra monocultura) — cartão nulo", cult="amendoim → milho, milheto", ant="amendoim", suc="milho; milheto", base="cereal contínuo",
    ef_md="Milho +8,14% (IC95 −5,26 a +23,44; n=34) ns; milheto +17,25% (−10,87 a +54,24; n=12) ns. Cultura seguinte.",
    ef=("rendimento do milho", 8.14, -5.26, 23.44, "%", "cultura_seguinte"),
    onde="Global", mod="Contradiz o Franke (amendoim entre os maiores)",
    cond=("qualquer", "não estratificado", "não estratificado", "1º ciclo"),
    g="D", T="T2", ne="nao", ne_md="Não usar como bônus isolado; só alarga a faixa comum", gl="Incerto", ref="Mudare et al. 2025", doi=[MUD25], pg="Supl. Tab. 5; Source Data Fig. 2b (conferido)")

add(id="zhao_feijao_comum", tipo="rotacao", t=1,
    nome="Feijão-comum como antecessora", cult="Phaseolus vulgaris → principal", ant="feijão-comum", suc="cultura principal", base="antecessora não leguminosa",
    ef_md="+14,5% (IC95 9,5–19,5); menos da metade do guandu. Base aberta: feijão-comum→milho +24,3% (9 sítios, planaltos do leste da África), 1 só sítio quente-seco. Cultura seguinte.",
    ef=("rendimento da cultura principal", 14.5, 9.5, 19.5, "%", "cultura_seguinte"),
    onde="Global", mod="Fixador fraco (N líquido −25 a +2 kg/ha, Franke Tab. 4)",
    cond=("qualquer; 1 sítio no estrato", "0–236", "baixa amplia", "1º ciclo"),
    g="B", T="T2", ne="parcial", ne_md="Feijão-comum→milho no CE é C·T2; no sertão o 'feijão' do PAM é sobretudo caupi",
    gl="Sim", ref="Zhao et al. 2022", doi=[ZHAO], pg="p.5 (conferido)")

add(id="zhao_soja", tipo="rotacao", t=1,
    nome="Soja como antecessora", cult="soja → principal", ant="soja", suc="cultura principal", base="antecessora não leguminosa",
    ef_md="+15,9% (IC95 13,1–18,6; 175 estudos). Base aberta: soja→milho na savana úmida +22,3% (11 sítios). Cultura seguinte.",
    ef=("rendimento da cultura principal", 15.9, 13.1, 18.6, "%", "cultura_seguinte"),
    onde="Global (peso EUA/China)", mod="Alto índice de colheita de N; N líquido −62 a +89 kg/ha",
    cond=("qualquer", "0–236", "—", "1º ciclo"),
    g="A", T="T3", ne="nao", ne_md="Soja quase ausente no sertão; serve ao MATOPIBA (onde o par real é soja→milho safrinha no mesmo ano)",
    gl="Sim", ref="Zhao et al. 2022", doi=[ZHAO], pg="Supl. Tab. 1")

add(id="mudare_soja_milho_sorgo", tipo="rotacao", t=1,
    nome="Soja → milho e soja → sorgo (contra monocultura do cereal)", cult="soja → milho; soja → sorgo", ant="soja", suc="milho; sorgo", base="cereal contínuo",
    ef_md="Soja→milho +18,74% (IC95 12,78–25,01; n=746); soja→sorgo +18,48% (9,72–27,95; n=106). Cultura seguinte.",
    ef=("rendimento do milho", 18.74, 12.78, 25.01, "%", "cultura_seguinte"),
    onde="Global, peso dos EUA", mod="N alto reduz",
    cond=("qualquer", "não estratificado", "alta (EUA)", "1º ciclo"),
    g="A", T="T3", ne="nao", ne_md="Mostra que o sorgo responde como o milho; soja só no MATOPIBA", gl="Sim",
    ref="Mudare et al. 2025", doi=[MUD25], pg="Supl. Tab. 5; Source Data Fig. 2b (conferido)")

add(id="franke_soja_cereal", tipo="rotacao", t=1,
    nome="Soja → cereal (África)", cult="soja → cereal", ant="soja", suc="cereal", base="cereal contínuo",
    ef_md="+0,62 t/ha (EP 0,10; p<0,0001); 1,18 → 1,80 t/ha (+53%); n=47. Cultura seguinte.",
    ef=("rendimento de grão do cereal", 0.62, 0.42, 0.82, "t/ha", "cultura_seguinte"),
    onde="África Subsaariana (Guiné, sul e leste)", mod="17–33% do N da palhada recuperado pelo milho (citação secundária)",
    cond=("savanas", "baixo", "baixa", "1º ciclo"),
    g="B", T="T3", ne="nao", ne_md="Cerrado e modo global", gl="Sim", ref="Franke et al. 2018", doi=[FRANKE], pg="Tab. 3 linha Soybean (conferida)")

add(id="zhao_guandu", tipo="rotacao", t=1,
    nome="Guandu como antecessora (ciclo completo)", cult="guandu → principal; guandu → milho", ant="guandu (Cajanus cajan)", suc="cultura principal; milho", base="antecessora não leguminosa / milho contínuo",
    ef_md="Zhao +32,4% (IC95 23,8–41,0; 15 estudos); Mudare guandu→milho +22,66% (3,16–45,84; n=12); base aberta análogo +48,9% (14–100; 4 sítios). Cultura seguinte.",
    ef=("rendimento da cultura principal", 32.4, 23.8, 41.0, "%", "cultura_seguinte"),
    onde="Global, sobretudo trópicos", mod="Só guandu de ciclo completo/semiperene: como cobertura de 60 d não rende (da Luz 2023) e semeado junto com o milho custa grão (Melo 2013)",
    cond=("qualquer; 4 sítios no estrato", "0–236", "baixa amplia", "ocupa a área ≥ 1 safra"),
    g="B", T="T2", ne="parcial", ne_md="Só como fase perene ou faixa; usar o limite inferior; custo da safra ocupada entra na sequência",
    gl="Sim, trópicos", ref="Zhao et al. 2022; Mudare et al. 2025", doi=[ZHAO, MUD25], pg="Zhao p.5 (conferido); Mudare Supl. Tab. 5 (conferido)")

add(id="zhao_leg_algodao_nulo", tipo="rotacao", t=1,
    nome="Leguminosa → algodão (e canola, trigo-sarraceno) — cartão nulo", cult="leguminosa → algodão", ant="leguminosa", suc="algodão", base="antecessora não leguminosa",
    ef_md="Algodão −1,3% (IC95 −12,0 a +9,5); canola +3,9% (0,0–7,8); trigo-sarraceno +5,4% (−3,5 a 14,2). Base aberta análogo: algodão −8,0% (2 sítios). Cultura seguinte.",
    ef=("rendimento do algodão", -1.3, -12.0, 9.5, "%", "cultura_seguinte"),
    onde="Global", mod="Cultura-alvo não cereal",
    cond=("qualquer", "—", "—", "—"),
    g="B", T="T2", ne="sim", ne_md="O motor não dá bônus de N ao algodão; a rotação do algodão vale pela quebra do bicudo",
    gl="Sim", ref="Zhao et al. 2022", doi=[ZHAO], pg="p.5 (conferido)")

add(id="mudare_rotacao_geral", tipo="rotacao", t=1,
    nome="Rotação contra monocultura: geral, leguminosa, não leguminosa e ordem", cult="qualquer antecessora diferente → principal", ant="qualquer; leguminosa; não leguminosa", suc="cultura seguinte",
    base="monocultura contínua da cultura seguinte",
    ef_md="Geral +20% (IC95 16–24; n=3.663, 738 exp.); leguminosa +23% (19–28; n=1.726); não leguminosa +16% (11–21; n=953). Leguminosa de grão→cereal +20,1% (n=1.237) contra cereal→leguminosa de grão +8,9% (n=302). Cultura seguinte.",
    ef=("rendimento da cultura seguinte", 23.0, 19.0, 28.0, "%", "cultura_seguinte"),
    onde="Global, 1980–2024, seis continentes", mod="N e tipo de sequência (top-10 modelos por AIC); o efeito cresce com os anos (Supl. Fig. 1)",
    cond=("qualquer", "cai com N", "—", "cresce com os anos"),
    g="A", T="T2", ne="parcial", ne_md="Base é monocultura, não o consórcio S0; a ordem importa (feijão depois do milho não recebe os 20%)",
    gl="Sim", ref="Mudare et al. 2025", doi=[MUD25], pg="p.2 Fig. 1b–d (conferido); Source Data Fig. 1e e 2a (conferido)")

add(id="mudare_africa_leg_naoleg", tipo="rotacao", t=1,
    nome="Leguminosa contra não leguminosa na África (contra monocultura)", cult="leguminosa / não leguminosa → cultura seguinte", ant="leguminosa; não leguminosa", suc="cultura seguinte", base="monocultura",
    ef_md="Leguminosa lnR 0,2542 (0,126–0,382; n=303) = +29% (13–47); não leguminosa lnR 0,0223 (−0,183 a 0,228; n=36) = +2,3% ns. O '16% (10–22%)' do texto é a leguminosa na AMÉRICA DO NORTE (lnR 0,1492; 0,0971–0,201). Cultura seguinte.",
    ef=("rendimento da cultura seguinte (leguminosa, África)", 29.0, 13.4, 46.5, "%", "cultura_seguinte"),
    onde="África (pouco N)", mod="Pouco N aplicado",
    cond=("mistura zonas úmidas e áridas", "baixo", "baixa", "1º ciclo"),
    g="B", T="T2", ne="parcial", ne_md="Análogo de baixo insumo; usar o estrato de aridez, não o valor do continente",
    gl="Sim para baixo insumo", ref="Mudare et al. 2025 (Source Data)", doi=[MUD25], pg="p.2; Source Data aba Figure 1e (conferida pelo integrador)")

add(id="mudare_classes_chuva", tipo="rotacao", t=1,
    nome="Leguminosa e não leguminosa antecessora por classe de chuva anual", cult="leguminosa / não leguminosa → cultura seguinte", ant="leguminosa; não leguminosa", suc="cultura seguinte", base="monocultura",
    ef_md="Leguminosa: < 500 mm lnR 0,16 (0,02–0,30; n=129) = +17% (2–35); 500–1.000 mm 0,16 (0,06–0,25); > 1.000 mm 0,23 (0,10–0,36); mesma letra 'a'. Não leguminosa: < 500 mm 0,23 (0,15–0,32; n=56) = +26%, letra 'b', contra 0,05 e 0,03. Cultura seguinte.",
    ef=("rendimento da cultura seguinte (leguminosa, < 500 mm)", 17.4, 2.0, 35.0, "%", "cultura_seguinte"),
    onde="Global, por MAP", mod="Valor só na Source Data; classe por chuva anual, não por aridez",
    cond=("< 500 mm (classe de MAP)", "não estratificado", "—", "1º ciclo"),
    g="B", T="T1", ne="sim", ne_md="Mostra que a leguminosa ainda ganha abaixo de 500 mm e que a quebra sem leguminosa rende mais ali",
    gl="Sim para zonas secas", ref="Mudare et al. 2025 (Source Data)", doi=[MUD25], pg="Source Data aba Supplementary Figure S5-S6, linhas MAP (conferida)")

add(id="mudare_moduladores_agua_solo", tipo="rotacao", t=1,
    nome="Moduladores de água e solo da leguminosa antecessora", cult="leguminosa → cultura seguinte", ant="leguminosa", suc="cultura seguinte", base="monocultura",
    ef_md="Sequeiro lnR 0,20 (0,13–0,28; n=396) = +22% contra irrigado 0,09 (−0,07 a 0,25; n=36) = +9%, MESMA letra; arenoso 0,53 (0,32–0,74; n=22) = +70%; areia franca 0,27 (n=81); palhada removida 0,27 (n=56) contra devolvida 0,17 (n=248); plantio direto 0,05 ns (n=51). Cultura seguinte.",
    ef=("rendimento da cultura seguinte (sequeiro)", 22.1, 13.9, 32.3, "%", "cultura_seguinte"),
    onde="Global", mod="Subgrupos pequenos, sem diferença formal: só direção",
    cond=("—", "—", "—", "—"),
    g="C", T="T2", ne="parcial", ne_md="Direção: sequeiro e areia ampliam; irrigado usa a faixa baixa; retirar a palha para o gado não anula o bônus",
    gl="Sim (direção)", ref="Mudare et al. 2025 (Source Data)", doi=[MUD25], pg="Source Data aba Supplementary Figure S5-S6 (Irrigation, Texture, Tillage, Precrop residues; conferida)")

add(id="franke_global", tipo="rotacao", t=1,
    nome="Leguminosa de grão → cereal na África Subsaariana (média)", cult="leguminosa de grão → milho, sorgo, milheto, arroz", ant="leguminosa de grão", suc="cereal", base="cereal contínuo (consórcio excluído)",
    ef_md="+0,49 t/ha (EP 0,09; p<0,0001); 1,20 → 1,69 t/ha (+41%); IC95 aprox. 0,31–0,67 (calculado); 199 obs., 44 publicações. Cultura seguinte.",
    ef=("rendimento de grão do cereal", 0.49, 0.31, 0.67, "t/ha", "cultura_seguinte"),
    onde="África Subsaariana, pequenos produtores, pouco N", mod="Ganho relativo cai com o rendimento do controle; leguminosa × resposta p<0,0001; zona p=0,351; cereal p=0,435",
    cond=("todas as AEZ", "maioria 0–50", "baixa", "1º ciclo = 2º+ (p=0,907)"),
    g="A", T="T1", ne="sim", ne_md="Melhor análogo de sistema; aplicar o %, não as t/ha (controle africano ≈ 2× o milho do sertão)",
    gl="Sim para baixo insumo", ref="Franke et al. 2018", doi=[FRANKE], pg="Tab. 3 linha Overall mean (conferida no XML)")

add(id="franke_sahel", tipo="rotacao", t=1,
    nome="Leguminosa → cereal na zona sudano-saheliana (< 700 mm, < 150 d) — cenário de ano seco", cult="caupi, amendoim → milheto, sorgo", ant="leguminosa de grão", suc="milheto ou sorgo (sem milho)", base="cereal contínuo",
    ef_md="+0,28 t/ha (EP 0,17; p=0,138, ns); 1,16 → 1,44 t/ha (+24% relativo, igual à Guiné); IC95 aprox. −0,05 a +0,61 t/ha (≈ −4% a +53%); n=46, 8 publicações. Cultura seguinte.",
    ef=("rendimento de grão do cereal", 0.28, -0.05, 0.61, "t/ha", "cultura_seguinte"),
    onde="Mali, Níger, Burkina Faso", mod="Zona e cereal confundidos; leguminosa produz pouco na estação curta",
    cond=("< 700 mm e < 150 d", "baixo", "baixa", "1º ciclo"),
    g="C", T="T1", ne="sim", ne_md="Análogo do ano seco: centro relativo NÃO cai; o IC alarga até 0. 589 dos 1.254 municípios do semiárido NE têm < 700 mm (IMERG)",
    gl="Sim, Sahel", ref="Franke et al. 2018", doi=[FRANKE], pg="Tab. 3 linha Sudano-Sahelian zone (conferida); Métodos (AEZ)")

add(id="franke_guine", tipo="rotacao", t=1,
    nome="Leguminosa → cereal na savana da Guiné (700–1.200 mm, 150–250 d) — cenário de ano normal", cult="leguminosa de grão → milho, sorgo, arroz", ant="leguminosa de grão", suc="cereal", base="cereal contínuo",
    ef_md="+0,52 t/ha (EP 0,18; p=0,015); 2,14 → 2,66 t/ha (+24%); n=74. Cultura seguinte.",
    ef=("rendimento de grão do cereal", 0.52, 0.17, 0.87, "t/ha", "cultura_seguinte"),
    onde="Nigéria, Gana, Burkina, Benin", mod="Muito N no cereal (Tab. 2)",
    cond=("700–1.200 mm; 150–250 d", "alto em parte", "média", "1º ciclo"),
    g="B", T="T1", ne="sim", ne_md="157 dos 175 municípios do semiárido do CE caem nesta faixa de chuva média, mas só em parte dos anos pelo LGP",
    gl="Sim", ref="Franke et al. 2018", doi=[FRANKE], pg="Tab. 3 linha Guinea savannah (conferida)")

add(id="franke_austral", tipo="rotacao", t=1,
    nome="Leguminosa → milho nas savanas da África Austral (estação única)", cult="leguminosa de grão → milho", ant="leguminosa de grão", suc="milho", base="milho contínuo",
    ef_md="+0,69 t/ha (EP 0,18; p=0,0005); 1,65 → 2,34 t/ha (+42%); n=27. Cultura seguinte.",
    ef=("rendimento de grão do milho", 0.69, 0.34, 1.04, "t/ha", "cultura_seguinte"),
    onde="Zimbábue, Malawi, Moçambique, Tanzânia; 600–1.200 mm, estação única de 100–250 d", mod="Solos arenosos pobres; outlier de striga excluído",
    cond=("estação única", "baixo", "baixa", "1º ciclo"),
    g="B", T="T1", ne="sim", ne_md="Melhor análogo de estação única com milho e solo arenoso", gl="Sim",
    ref="Franke et al. 2018", doi=[FRANKE], pg="Tab. 3 linha Savannahs of southern Africa (conferida)")

add(id="franke_por_cereal", tipo="rotacao", t=1,
    nome="Resposta por cereal na África (milho, milheto, sorgo) — só prova de confundimento", cult="leguminosa → milho; milheto; sorgo", ant="leguminosa de grão", suc="milho; milheto; sorgo", base="cereal contínuo",
    ef_md="Milho +0,57 t/ha (EP 0,12; n=131); milheto +0,32 (EP 0,21; ns; n=37); sorgo +0,12 (EP 0,26; ns; n=25); cereal × resposta p=0,435. Cultura seguinte.",
    ef=("rendimento de grão do milho", 0.57, 0.33, 0.81, "t/ha", "cultura_seguinte"),
    onde="África Subsaariana", mod="Todo o milheto e o sorgo estão na zona sudano-saheliana",
    cond=("confundido com a zona", "—", "—", "—"),
    g="B", T="T2", ne="parcial", ne_md="NÃO usar para dizer que o sorgo não responde (no Zhao quente-seco o sorgo dá +57%)",
    gl="Sim, com a ressalva", ref="Franke et al. 2018", doi=[FRANKE], pg="Tab. 3 linhas Maize, Millet, Sorghum (conferida)")

add(id="franke_dose_n_ciclo", tipo="rotacao", t=1,
    nome="Efeito da leguminosa por dose de N no cereal e por ciclo (África)", cult="leguminosa de grão → cereal", ant="leguminosa de grão", suc="cereal com 0, 15–50 ou 60–120 kg N", base="cereal contínuo com a mesma dose",
    ef_md="0 N +0,54 t/ha (EP 0,11; 0,97 → 1,51, +56%; n=77); 15–50 N +0,49 (EP 0,15); 60–120 N +0,32 (EP 0,14; p=0,025); N × resposta p=0,204. 1º ciclo +0,48 contra 2º+ +0,49 (p=0,907). Cultura seguinte.",
    ef=("rendimento de grão do cereal (0 N)", 0.54, 0.32, 0.76, "t/ha", "cultura_seguinte"),
    onde="África Subsaariana", mod="Partição N/não-N (~59% não-N) é razão entre subgrupos de estudos diferentes, não decomposição medida",
    cond=("todas", "0 (linha do sertão)", "baixa", "1º ciclo = 2º+"),
    g="B", T="T1", ne="sim", ne_md="Sertão está na classe 0 N; contar o bônus desde o 1º ciclo, sem acúmulo",
    gl="Sim; concorda com Zhao e Mudare", ref="Franke et al. 2018", doi=[FRANKE], pg="Tab. 3 linhas de N e de ciclo (conferida)")

add(id="mudare_pousio_milho", tipo="rotacao", t=1,
    nome="Pousio → milho (quebra sem leguminosa)", cult="pousio → milho; → sorgo; → milheto", ant="pousio", suc="milho; sorgo; milheto", base="cereal contínuo",
    ef_md="Pousio→milho +31,02% (IC95 16,01–47,96; n=31); pousio→sorgo +11,46% ns (n=28); pousio→milheto −4,56% ns (n=12). Cultura seguinte (o ano de pousio não dá grão).",
    ef=("rendimento do milho", 31.02, 16.01, 47.96, "%", "cultura_seguinte"),
    onde="Global", mod="O pousio dos ensaios pode ser pousio limpo de recarga (temperado); o do sertão é pastejado; Mudare excluiu o pousio da sequência inteira (p.8)",
    cond=("vale mais em estação seca (Kluger)", "—", "—", "1 safra sem grão"),
    g="C", T="T2", ne="parcial", ne_md="Entra como estratégia comparável obrigatória, calculada na sequência inteira e com verificação de 'pousio limpo'",
    gl="Sim", ref="Mudare et al. 2025", doi=[MUD25], pg="Supl. Tab. 5 p.24; Source Data Fig. 2b (conferido)")

add(id="mudare_sorgo_milho", tipo="rotacao", t=1,
    nome="Sorgo → milho (quebra sem leguminosa)", cult="sorgo → milho", ant="sorgo", suc="milho", base="milho contínuo",
    ef_md="+27,92% (IC95 7,58–52,12; n=10); milho→sorgo −7,36% (−19,88 a +7,11; n=16) ns. Cultura seguinte.",
    ef=("rendimento do milho", 27.92, 7.58, 52.12, "%", "cultura_seguinte"),
    onde="Global", mod="n pequeno; veto do portão de pragas perto do algodão (sorgo alimenta o bicudo adulto; mantém a lagarta)",
    cond=("seco favorece (não leguminosa < 500 mm +26%)", "—", "—", "1º ciclo"),
    g="C", T="T2", ne="parcial", ne_md="Só longe do algodão e com a sequência inteira calculada (vale o veto 'milho-sorgo no lugar de sorgo contínuo')",
    gl="Sim", ref="Mudare et al. 2025", doi=[MUD25], pg="Supl. Tab. 5; Source Data Fig. 2b (conferido)")

add(id="mudare_algodao_milho", tipo="rotacao", t=1,
    nome="Algodão ↔ milho e sorgo → algodão (quebra sem leguminosa)", cult="milho ↔ algodão; sorgo → algodão", ant="milho; algodão; sorgo", suc="algodão; milho", base="monocultura da cultura seguinte",
    ef_md="Milho→algodão +31,69% (IC95 5,84–63,85; n=13); algodão→milho +19,21% (1,37–40,19; n=44); sorgo→algodão +21,60% (0,03–47,83; n=10). Cultura seguinte.",
    ef=("rendimento do algodão", 31.69, 5.84, 63.85, "%", "cultura_seguinte"),
    onde="Global", mod="Antes do algodão, preferir milho a sorgo (portão do bicudo)",
    cond=("qualquer", "—", "—", "1º ciclo"),
    g="C", T="T2", ne="parcial", ne_md="Só dentro de vazio regional do algodão; o ganho de praga vem do vazio, não do talhão",
    gl="Sim", ref="Mudare et al. 2025", doi=[MUD25], pg="Source Data Fig. 2b (conferida pelo integrador)")

add(id="mudare_sequencia_inteira", tipo="rotacao", t=1,
    nome="Sequência inteira (antecessora + principal) contra monocultura", cult="pares de 2 anos", ant="antecessora", suc="principal (soma dos 2 anos)", base="2 anos da monocultura da principal",
    ef_md="Rendimento total +23% (IC95 16–31); energia +24% (16–32); proteína +14% (8–21); Fe +27%; Mg +17%; Zn +17%; receita bruta +20% (12–29); 609 pares, 114 exp. SEQUÊNCIA INTEIRA.",
    ef=("rendimento total da sequência", 23.0, 16.0, 31.0, "%", "sequencia_inteira"),
    onde="Global", mod="Receita bruta (preço FAOSTAT 2008–2018, sem custo); excluiu misturas, pousio e algodão (p.8)",
    cond=("não estratificado", "—", "—", "2 anos"),
    g="B", T="T2", ne="parcial", ne_md="Só justifica o método; o motor recalcula a sequência com produção e preço locais e nunca soma ao bônus da cultura seguinte",
    gl="Sim, com preços locais", ref="Mudare et al. 2025", doi=[MUD25], pg="p.2–3 Fig. 3a; Supl. Tab. 7")

add(id="mudare_neg_cereal_para_leg_cereal", tipo="rotacao", t=1,
    nome="CARTÃO NEGATIVO: soja-milho no lugar de milho contínuo; soja-sorgo no lugar de sorgo contínuo", cult="soja-milho; soja-sorgo", ant="soja", suc="milho; sorgo", base="cereal contínuo",
    ef_md="Energia −27%, micronutrientes −53%, receita −50% (texto p.4). Soja→milho: energia −31,0% (−36,4 a −25,1), receita −53,1% (n=29); soja→sorgo: receita −47,1% (n=216). Sequências com leguminosa perderam nos três critérios em 73,8% dos casos. SEQUÊNCIA INTEIRA.",
    ef=("receita bruta da sequência", -50.0, None, None, "%", "sequencia_inteira"),
    onde="Global, peso dos EUA (cereal de alto rendimento)", mod="Preço relativo leguminosa/cereal; no NE o feijão vale 3,6× o milho por kg (PAM) e pode inverter a receita (teste D)",
    cond=("—", "—", "alta (cereal)", "2 anos"),
    g="B", T="T2", ne="parcial", ne_md="Transfere em massa e energia; em receita, depende do preço local", gl="Sim, como alerta",
    ref="Mudare et al. 2025", doi=[MUD25], pg="p.4 e p.6–7; Fig. 3g; Source Data aba Figure 3e; Supl. Tab. 7–8")

add(id="mudare_neg_sorgo_para_milho_sorgo", tipo="rotacao", t=1,
    nome="CARTÃO NEGATIVO: milho-sorgo no lugar de sorgo contínuo", cult="milho-sorgo", ant="milho", suc="sorgo", base="sorgo contínuo",
    ef_md="Rendimento −32%, nutrição −23%, receita −31% (sem IC no texto principal; 'subprodução transgressiva'). SEQUÊNCIA INTEIRA.",
    ef=("rendimento total da sequência", -32.0, None, None, "%", "sequencia_inteira"),
    onde="Global", mod="Troca de cultura adaptada por menos adaptada",
    cond=("seco (sorgo é o cereal tolerante)", "—", "—", "2 anos"),
    g="B", T="T2", ne="sim", ne_md="Veto: no sertão seco, não trocar sorgo contínuo por milho em rotação", gl="Sim, como alerta",
    ref="Mudare et al. 2025", doi=[MUD25], pg="p.4; Fig. 3g; Supl. Tab. 8")

add(id="mudare_neg_trigo_europa", tipo="rotacao", t=1,
    nome="CARTÃO NEGATIVO: trigo-cevada → trigo contínuo (Europa)", cult="trigo, cevada", ant="—", suc="trigo contínuo", base="trigo-cevada",
    ef_md="Rendimento −21%, nutrição −25%, receita −15%. SEQUÊNCIA INTEIRA.",
    ef=("rendimento total da sequência", -21.0, None, None, "%", "sequencia_inteira"),
    onde="Europa, temperado", mod="Região", cond=("temperado", "—", "—", "2 anos"),
    g="B", T="T3", ne="nao", ne_md="Só modo global", gl="Sim, Europa", ref="Mudare et al. 2025", doi=[MUD25], pg="p.4; Fig. 4")

add(id="mudare_ganha_ganha", tipo="rotacao", t=1,
    nome="Sequências ganha-ganha (sorgo-milho, milho-soja, sorgo-soja, milho-trigo)", cult="sorgo-milho; milho-soja; sorgo-soja; milho-trigo", ant="vários", suc="vários", base="monocultura comparada",
    ef_md="Melhores em rendimento, nutrição e receita (só na Fig. 3g, sem número no texto); > 80% de ganho onde a monocultura domina (África Ocidental e Austral, América do Sul; Fig. 4). SEQUÊNCIA INTEIRA.",
    ef=("rendimento, nutrição e receita da sequência", None, None, None, "direção", "sequencia_inteira"),
    onde="Global", mod="Onde a leguminosa falha, sorgo-milho é a alternativa (p.6)",
    cond=("—", "—", "—", "2 anos"), g="C", T="T2", ne="parcial", ne_md="Só direção: sorgo-milho plausível no CE quando a leguminosa falha",
    gl="Sim, por região", ref="Mudare et al. 2025", doi=[MUD25], pg="p.4, p.6; Fig. 3g; Fig. 4")

add(id="mudare_economia_n", tipo="rotacao", t=1,
    nome="Economia de N na rotação leguminosa–cereal", cult="leguminosa–milho; leguminosa–trigo", ant="leguminosa", suc="milho; trigo", base="monocultura do cereal",
    ef_md="N mineral do sistema: milho −45,6% (IC95 −52,9 a −37,2; n=95); trigo −41,1% (−51,2 a −30,4; n=51). SEQUÊNCIA INTEIRA (insumo).",
    ef=("N mineral aplicado no sistema", -45.6, -52.9, -37.2, "%", "sequencia_inteira"),
    onde="Global; 20 estudos com N nas duas culturas", mod="Só onde há N aplicado",
    cond=("—", "alto", "—", "—"), g="B", T="T3", ne="nao", ne_md="No sequeiro N ≈ 0; vale para perímetros irrigados e MATOPIBA",
    gl="Sim em sistemas com N alto", ref="Mudare et al. 2025", doi=[MUD25], pg="p.2; Supl. Tab. 2–3")

add(id="mudare_estabilidade_lncv", tipo="rotacao", t=1,
    nome="Estabilidade do rendimento em rotação de longo prazo", cult="rotação × monocultura", ant="—", suc="cultura seguinte", base="monocultura",
    ef_md="lnCV 0,21 (IC95 0,06–0,36; P=0,0059); 1.159 obs., 230 exp. de 9–50 anos. CONTRADIÇÃO INTERNA conferida: p.2 lê 0,21 como rotação mais estável; p.9 (Eq. 6) diz que é mais estável quando lnCV < 0. Cultura seguinte.",
    ef=("lnCV do rendimento", 0.21, 0.06, 0.36, "lnCV", "cultura_seguinte"),
    onde="Global, ensaios longos", mod="Sem quebras totais na amostra", cond=("não relatado", "—", "—", "≥ 9 anos"),
    g="C", T="T3", ne="nao", ne_md="Não usar como seguro de cauda", gl="Com cautela", ref="Mudare et al. 2025", doi=[MUD25], pg="p.2; p.9 Eq. 6 (conferidos)")

add(id="mudare_mistura_forrageira", tipo="rotacao", t=1,
    nome="Mistura gramínea + leguminosa forrageira (e leguminosa forrageira) antes do cereal", cult="mistura forrageira → cereal; leguminosa forrageira → cereal", ant="mistura forrageira; leguminosa forrageira", suc="cereal", base="monocultura",
    ef_md="Mistura→cereal +60,29% (lnR 0,36–0,58; n=79), dos quais mistura→trigo +70,44% (49,12–94,80; n=70); não há par mistura→milho. Leguminosa forrageira→cereal +25,82% (n=393). Cultura seguinte.",
    ef=("rendimento do cereal seguinte", 25.82, 19.7, 32.3, "%", "cultura_seguinte"),
    onde="Global (sistemas com ley, sobretudo trigo)", mod="Cresce com o tempo; custa uma quadra sem grão",
    cond=("—", "—", "—", "≥ 1 safra sem grão"),
    g="B", T="T2", ne="parcial", ne_md="No NE é C·T2 (hipótese para ILP; o valor da forragem não foi medido)",
    gl="Sim (Europa, Oceania)", ref="Mudare et al. 2025", doi=[MUD25], pg="p.2 Fig. 2a; Source Data Fig. 2a e 2b (conferidas)")

add(id="mudare_naoleg_grupos_cereal", tipo="rotacao", t=1,
    nome="Tubérculo, oleaginosa, gramínea forrageira ou fibra → cereal", cult="mandioca etc. → cereal", ant="tubérculo/oleaginosa/gramínea forrageira/fibra", suc="cereal", base="monocultura",
    ef_md="+15% (IC95 4–27). Cultura seguinte.",
    ef=("rendimento do cereal seguinte", 15.0, 4.0, 27.0, "%", "cultura_seguinte"),
    onde="Global", mod="Efeito de quebra; grupo heterogêneo (mandioca não separada)",
    cond=("—", "ganho maior com N alto (MacLaren)", "—", "cresce com os anos"),
    g="B", T="T2", ne="parcial", ne_md="Mandioca→milho: usar o limite inferior (+4%), grau C", gl="Sim",
    ref="Mudare et al. 2025", doi=[MUD25], pg="p.2 Fig. 2a")

add(id="rusinamhodzi_pd_rotacao", tipo="rotacao", t=1,
    nome="Plantio direto + rotação milho–leguminosa contra plantio direto com milho contínuo", cult="milho–soja; milho–caupi", ant="leguminosa", suc="milho", base="plantio direto com milho contínuo",
    ef_md="Diferença média +0,1 t/ha ('mean = 0.1' impresso na Fig. 2), sem IC; 63% dos dados com ganho; 'real yield benefits start after 20 years' (legenda da Fig. 4). Cultura seguinte.",
    ef=("rendimento do milho", 0.1, None, None, "t/ha", "cultura_seguinte"),
    onde="Sequeiro semiárido a subúmido, 26 estudos (EUA, Zimbábue, Nigéria, Índia, México, Brasil)", mod="Chuva intra e entre estações não considerada",
    cond=("semiárido a subúmido", "—", "—", "≥ 5 anos; ganho real após 20"),
    g="C", T="T2", ne="parcial", ne_md="Freia a promessa de ganho rápido sob plantio direto", gl="Sim para agricultura de conservação",
    ref="Rusinamhodzi et al. 2011, Agron Sustain Dev 31:657–673", doi=[RUSI], pg="Fig. 2 (p.661 = PDF p.5, conferido); Fig. 4 (p.662)")

add(id="yang_nao_cereal_trigo_milho", tipo="rotacao", t=1,
    nome="Amendoim, soja ou batata-doce → trigo–milho (Planície do Norte da China)", cult="amendoim; soja; batata-doce → trigo–milho", ant="não cereal", suc="trigo de inverno–milho de verão", base="trigo–milho todo ano",
    ef_md="Grão do trigo-milho seguinte +26–32%; receita +39–46%; sistema amendoim: N2O −30%, C do solo 2,03 t C/ha/ano; soja: N2O −42%. Cultura seguinte e serviços (separar escopos).",
    ef=("grão do trigo-milho seguinte", 29.0, 26.0, 32.0, "%", "cultura_seguinte"),
    onde="Luancheng, Hebei; 472 mm, 14,7 °C, irrigação suplementar; 1 sítio, 2016–2022", mod="Irrigação e N alto no controle",
    cond=("semiúmido irrigado", "alto", "alta", "3 ciclos"),
    g="C", T="T3", ne="nao", ne_md="Irrigado, temperado, cultivo duplo", gl="Sim para cultivo duplo intensivo irrigado",
    ref="Yang et al. 2024, Nat Commun 15:198", doi=[YANG], pg="p.2–5; Fig. 2–4")

add(id="yang_comparador_cereal", tipo="rotacao", t=1,
    nome="Milho de primavera → trigo–milho (só cereais) — comparador", cult="milho → trigo–milho", ant="milho de primavera", suc="trigo–milho", base="trigo–milho todo ano",
    ef_md="Rendimento equivalente −16% e proteína −23%. SEQUÊNCIA INTEIRA.",
    ef=("rendimento equivalente do sistema", -16.0, None, None, "%", "sequencia_inteira"),
    onde="Luancheng, China", mod="Diversificar com outro cereal não dá o bônus", cond=("irrigado", "alto", "alta", "3 ciclos"),
    g="C", T="T2", ne="parcial", ne_md="Só como comparador (função > número de espécies)", gl="Sim", ref="Yang et al. 2024", doi=[YANG], pg="p.3")

add(id="kluger_soja_milho", tipo="rotacao", t=1,
    nome="Soja → milho por satélite (efeito líquido de insumo)", cult="soja → milho", ant="soja", suc="milho", base="milho → milho",
    ef_md="EUA +2,5%* (≈0,26 t/ha); Canadá +1,7%*; China NE −2,4%*; IC só em figura e estreito demais (p.8). Cultura seguinte.",
    ef=("rendimento do milho (GCVI calibrado)", 2.5, None, None, "%", "cultura_seguinte"),
    onde="EUA, Canadá, NE da China; temperado", mod="Efeito líquido da redução de N do agricultor (piso); bT negativo",
    cond=("temperado", "alto", "alta", "2 anos"),
    g="B", T="T3", ne="nao", ne_md="Transfere só o sinal; Ceará fora do suporte térmico", gl="Média: milho de alto insumo",
    ref="Kluger, Di Tommaso & Lobell 2025, ERL", doi=[KLUGER], pg="Tab. S9 (p.64), Tab. S10 (p.65), Fig. 3 (p.8)")

add(id="kluger_milho_soja", tipo="rotacao", t=1,
    nome="Milho → soja por satélite", cult="milho → soja", ant="milho", suc="soja", base="soja → soja",
    ef_md="EUA +8,5%* (≈0,27 t/ha); Canadá +6,8%*; China +6,2%*. Benefício cresce no calor (pragas como hipótese dos autores, p.13). Cultura seguinte.",
    ef=("rendimento da soja", 8.5, None, None, "%", "cultura_seguinte"),
    onde="EUA, Canadá, China; temperado", mod="Mecanismo de praga (atribuído, não medido)",
    cond=("temperado", "—", "—", "2 anos"),
    g="B", T="T2", ne="parcial", ne_md="Análogo indireto de milho → caupi (quebra de praga na leguminosa)", gl="Alta em milho-soja",
    ref="Kluger et al. 2025", doi=[KLUGER], pg="Tab. S9 (p.64); Fig. 3–4; p.13")

add(id="seifert_soja_continua", tipo="rotacao", t=1,
    nome="Soja após milho contra soja contínua (penalidade da soja contínua)", cult="milho → soja", ant="milho", suc="soja", base="soja contínua",
    ef_md="Sequeiro 10,3% (0,32 Mg/ha; IC95 calculado ~8,0–12,6%); irrigado 9,6%; cresce até 5 anos de monocultura. Beal Cohen (só resumo): +10,8% (faixa 4,6–17,6). Cultura seguinte.",
    ef=("rendimento da soja", 10.3, 8.0, 12.6, "%", "cultura_seguinte"),
    onde="IA, IL, IN, MN, NE, SD; 2007–2012; rendimento de seguro (RMA)", mod="Maior em áreas frias e úmidas; atribuída a pragas pelos autores",
    cond=("úmido a subúmido", "—", "—", "cresce até 5 anos de monocultura"),
    g="B", T="T2", ne="parcial", ne_md="Regra de mecanismo (penalidade de praga cresce com os anos de monocultura: caupi contínuo); número não",
    gl="Alta como mecanismo", ref="Seifert, Roberts & Lobell 2017, Agron J 109:541–548", doi=[SEIFERT, BEAL], pg="Resumo p.541; Tab. 3 e Figs. 2–5 (p.543–546)")

add(id="seifert_milho_continuo", tipo="rotacao", t=1,
    nome="Milho rotacionado com soja contra milho contínuo (penalidade do milho contínuo)", cult="soja → milho", ant="soja", suc="milho", base="milho contínuo ≥ 1 ano",
    ef_md="Sequeiro 4,3% (0,42 Mg/ha; IC95 calculado ~2,6–6,0%); irrigado 1,7%; 1,9% → 5,7% de 1 para 2 anos de monocultura e estabiliza. Cultura seguinte.",
    ef=("rendimento do milho", 4.3, 2.6, 6.0, "%", "cultura_seguinte"),
    onde="Corn Belt, 370.420 talhões", mod="Maior nos distritos secos (gradiente espacial confundido com manejo); agricultor põe 32–51 kg N a mais no contínuo",
    cond=("úmido a subúmido", "alto", "alta", "satura em 2 anos"),
    g="B", T="T2", ne="parcial", ne_md="Só a direção (N): é piso, não estimativa", gl="Alta para o mecanismo de N",
    ref="Seifert et al. 2017", doi=[SEIFERT], pg="Resumo; Tab. 3; Figs. 1–5; p.547")

add(id="beal_cohen_milho_satelite", tipo="rotacao", t=1,
    nome="Soja → milho por satélite (Beal Cohen 2019, só resumo)", cult="soja → milho", ant="soja", suc="milho", base="milho contínuo",
    ef_md="+1,0% (faixa −8,9 a +9,7; significado da 'faixa' não verificado); não difere dos 4,3% do talhão. Cultura seguinte.",
    ef=("rendimento do milho", 1.0, -8.9, 9.7, "%", "cultura_seguinte"),
    onde="IN, IA, IL; 2007–2012", mod="Efeito pequeno não se reproduz entre cadeias de satélite",
    cond=("úmido", "alto", "alta", "—"), g="D", T="T3", ne="nao", ne_md="Só aviso metodológico", gl="Média",
    ref="Beal Cohen et al. 2019, Agron J 111:2940–2948", doi=[BEAL], pg="Somente o resumo")

add(id="kluger_leg_trigo_primavera", tipo="rotacao", t=1,
    nome="Leguminosa de grão → trigo de primavera por satélite", cult="feijão seco, lentilha, ervilha, soja → trigo de primavera", ant="leguminosa de grão", suc="trigo de primavera", base="trigo → trigo",
    ef_md="Feijão seco→trigo (EUA) +14,4%* (62% das amostras com propensão < 0,05: grau C); lentilha +10,4%*; ervilha +11,3%*; soja +8,3%* (EUA) e +13,7%* (Canadá). Leguminosas: 8 de 9 bP positivos; 6 de 9 bT negativos. Cultura seguinte.",
    ef=("rendimento do trigo de primavera", 11.3, 8.3, 14.4, "%", "cultura_seguinte"),
    onde="Planícies do norte dos EUA e pradarias do Canadá (frio, sub-úmido a semiárido)", mod="Mais chuva na estação, mais benefício; mais calor, menos (dentro da região)",
    cond=("frio sub-úmido a semiárido", "—", "—", "2 anos"),
    g="B", T="T2", ne="parcial", ne_md="Sinal da leguminosa antecessora; fora do suporte térmico", gl="Média-alta em cereais de sequeiro frio",
    ref="Kluger et al. 2025", doi=[KLUGER], pg="Tab. S9 (p.64); Tab. S7 (p.62); p.12–13")

add(id="kluger_pousio_trigo", tipo="rotacao", t=1,
    nome="Pousio → trigo (armazém de água) por satélite", cult="pousio → trigo de primavera; → trigo de inverno", ant="pousio", suc="trigo", base="trigo → trigo",
    ef_md="Pousio→trigo de primavera (Canadá) +4,7%* com bP −3,4* (vale MAIS em estação seca); pousio→trigo de inverno (EUA) +8,3%*, bT −4,8*. Cultura seguinte.",
    ef=("rendimento do trigo", 4.7, None, None, "%", "cultura_seguinte"),
    onde="Pradarias do Canadá; Planícies dos EUA", mod="Sinal da chuva oposto ao da leguminosa",
    cond=("seco favorece", "—", "—", "1 safra sem grão"),
    g="B", T="T2", ne="parcial", ne_md="Mecanismo hídrico relevante: sustenta o pousio comparável; medir a recarga com SMAP antes de usar número",
    gl="Média em sequeiro de uma safra", ref="Kluger et al. 2025", doi=[KLUGER], pg="Tab. S9 (p.64); Fig. 4 (p.9); p.8")

add(id="kluger_neg_soja_trigo_inverno", tipo="rotacao", t=1,
    nome="CARTÃO NEGATIVO: soja → trigo de inverno (atraso e água)", cult="soja → trigo de inverno", ant="soja", suc="trigo de inverno", base="trigo → trigo",
    ef_md="−12,4%*, o pior da tabela; chuva atenua (bP +5,0*); repete-se na média simples por célula de 1° (Apêndice C.6). Cultura seguinte.",
    ef=("rendimento do trigo de inverno", -12.4, None, None, "%", "cultura_seguinte"),
    onde="EUA, 2008–2021", mod="Colheita tardia atrasa o plantio; a soja seca o solo em ano seco",
    cond=("pior em ano seco", "—", "—", "2 anos"),
    g="B", T="T2", ne="parcial", ne_md="Regra de mecanismo: antecessor que atrasa a semeadura ou gasta água dá perda; vale para a sucessão dentro da quadra",
    gl="Alta como mecanismo", ref="Kluger et al. 2025", doi=[KLUGER], pg="Tab. S9 (p.64); p.11–12; Apêndice C.6 (p.40)")

add(id="kluger_outros_pares_temperados", tipo="rotacao", t=1,
    nome="Outros pares temperados de cereal/oleaginosa (modo global)", cult="WW, WB, UW, SW, R, Su, C, Si, Ch → milho, soja ou trigo", ant="trigos, cevada, canola, girassol, milho, silagem, beterraba", suc="milho; soja; trigo",
    base="monocultura da cultura seguinte",
    ef_md="De −2,1% a +10,1%: ex. canola→trigo de inverno (França) +10,1%*; trigo de inverno→milho EUA +0,9%*, Canadá +3,7%* (EUA com propensão ruim: C); cevada de inverno→milho −0,9% ns; trigo de primavera→milho −0,3% ns. Mediana dos 36 pares 4,25% (texto p.33: 4,5%). Cultura seguinte.",
    ef=("rendimento da cultura seguinte (mediana dos 36 pares)", 4.25, -12.4, 14.4, "%", "cultura_seguinte"),
    onde="EUA, Canadá, França", mod="Efeito líquido de insumo; ATO só onde há sobreposição",
    cond=("temperado", "alto", "alta", "2 anos"), g="B", T="T3", ne="nao", ne_md="Só modo global", gl="Média, por par",
    ref="Kluger et al. 2025", doi=[KLUGER], pg="Tab. S9 (p.64); p.33 (conferido: '4.5%'); Tab. S7–S8")

add(id="zhou_corn_belt", tipo="rotacao", t=1,
    nome="Milho-soja no Corn Belt e o clima fora da estação (Zhou 2024, só resumo)", cult="soja → milho; milho → soja", ant="soja; milho", suc="milho; soja", base="contínuo",
    ef_md="Milho +0,96 t/ha; soja +0,22 t/ha (1999–2018); até 2051–2070 o benefício do milho cai 6,74–17,18% e o da soja sobe 8,36–13,83%. Cultura seguinte.",
    ef=("rendimento do milho", 0.96, None, None, "t/ha", "cultura_seguinte"),
    onde="Meio-Oeste dos EUA", mod="Calor e chuva fora da estação reduzem o benefício no milho",
    cond=("temperado", "alto", "alta", "—"), g="C", T="T3", ne="nao", ne_md="Só a lição: o clima fora da estação também modula", gl="Corn Belt",
    ref="Zhou et al. 2024, Glob Change Biol 30:e17556", doi=[ZHOU], pg="Somente o resumo (Wiley bloqueado)")

add(id="bowles_media", tipo="rotacao", t=1,
    nome="Rotação diversificada contra simples no milho (média dos sítios com efeito)", cult="rotações de 3–4 culturas com alfafa, aveia, trevo → milho", ant="rotação diversa (RCI máximo)", suc="milho", base="monocultura ou 2 culturas",
    ef_md="+28,1% (de +7,7% a +80,5%), só nos 9 de 11 sítios com efeito crível; média global do RCI com IC −1,93 a +1,97 (inclui zero); Summary: +22,6% em condições favoráveis. Cultura seguinte.",
    ef=("rendimento do milho", 28.1, None, None, "%", "cultura_seguinte"),
    onde="11 ensaios longos EUA/Canadá, 406–1.074 mm, temperado", mod="Seleção a posteriori; sem ganho nos 2 sítios mais secos",
    cond=("temperado", "alto", "alta", "16–58 anos"), g="C", T="T3", ne="nao", ne_md="Base de monocultura, alto insumo, temperado", gl="Temperado úmido, citar sempre o nulo global",
    ref="Bowles et al. 2020, One Earth 2:284–293", doi=[BOWLES], pg="p.2 (Summary) e p.4 (conferidos); Tab. 1; Fig. 1A")

add(id="bowles_seca", tipo="rotacao", t=1,
    nome="Rotação diversa em ano de seca (seca pela indenização do seguro)", cult="rotação diversa → milho", ant="rotação diversa", suc="milho", base="rotação simples",
    ef_md="Rendimento 14,0% a 88,9% MAIOR no ano de seca (corpo p.6, Fig. 2B); o Summary (p.2) escreve 'yield losses reduced by 14.0%–89.9%'; ns em 2 de 9 sítios. Cultura seguinte.",
    ef=("rendimento do milho no ano de seca", None, 14.0, 88.9, "%", "cultura_seguinte"),
    onde="9 sítios dos EUA, temperado", mod="Seca inferida por seguro; sítios áridos sem ganho",
    cond=("temperado", "alto", "alta", "décadas"), g="B", T="T3", ne="nao", ne_md="Seca do ano em lugar úmido ≠ aridez estrutural", gl="Temperado com seca episódica",
    ref="Bowles et al. 2020", doi=[BOWLES], pg="p.6 Fig. 2B e p.2 Summary (conferidos)")

add(id="bowles_akron_pousio", tipo="rotacao", t=1,
    nome="ALERTA: rotação diversa sem pousio no sítio mais seco (Akron, CO)", cult="C-M-Pea-W (sem pousio) contra C-F-W", ant="rotação sem pousio", suc="milho", base="rotação com pousio",
    ef_md="Sem ganho (efeito do RCI não crível); retirar o pousio reduziu a recarga do perfil. Cultura seguinte.",
    ef=("rendimento do milho", 0.0, None, None, "%", "cultura_seguinte"),
    onde="Akron, 406 mm/ano, semiárido frio", mod="Recarga de água pelo pousio",
    cond=("semiárido frio", "—", "—", "longo prazo"), g="B", T="T2", ne="parcial", ne_md="Transfere o mecanismo: não retirar pousio/recarga sem balanço hídrico", gl="Semiáridos de sequeiro",
    ref="Bowles et al. 2020", doi=[BOWLES], pg="p.289 (Variation across Sites); Tab. 1")

add(id="bowles_pior_ambiente", tipo="rotacao", t=1,
    nome="Rotação diversa no pior ambiente do sítio (EI mínimo)", cult="C-O/A-A-A; C-O-P → milho", ant="rotação com fase perene", suc="milho", base="milho contínuo",
    ef_md="ON1 +2.252 kg/ha (IC95 1.488–2.998); OH1 +1.091 kg/ha (739–1.442); maior em 7 de 11 sítios. Cultura seguinte.",
    ef=("rendimento do milho no pior ambiente", 2252.0, 1488.0, 2998.0, "kg/ha", "cultura_seguinte"),
    onde="Ontário e Ohio, temperado úmido", mod="Fase perene forrageira e sem adubo",
    cond=("úmido", "0 a 202", "—", "décadas"), g="B", T="T3", ne="nao", ne_md="O escudo vem da perene; palma/capim como análogo não testados", gl="Sistemas com fase perene",
    ref="Bowles et al. 2020", doi=[BOWLES], pg="p.287 Fig. 1D")

add(id="bowles_tendencia_risco", tipo="rotacao", t=1,
    nome="Rotação diversa: tendência de rendimento e risco de quebra", cult="rotação diversa → milho", ant="rotação diversa", suc="milho", base="simples",
    ef_md="OH1 +12,70 kg/ha/ano por unidade de RCI (3,49–21,51); média global 0,52 (−1,45 a 2,53) ns; menor risco de quebra em 8 de 11 sítios (só figura). Cultura seguinte.",
    ef=("tendência do rendimento do milho", 12.7, 3.49, 21.51, "kg/ha/ano", "cultura_seguinte"),
    onde="11 sítios da América do Norte", mod="Só 6 de 11 sítios; mecanismo especulativo",
    cond=("temperado", "—", "—", "décadas"), g="C", T="T3", ne="nao", ne_md="Etiqueta de horizonte longo", gl="Temperado",
    ref="Bowles et al. 2020", doi=[BOWLES], pg="p.287–288 Fig. 1C; p.288 Fig. 3")

add(id="renwick_seca_imposta", tipo="rotacao", t=1,
    nome="Diversificação com cereais de inverno e trevo sob seca imposta", cult="MMOrcBrc contra MMSS", ant="rotação diversa", suc="milho", base="milho-milho-soja-soja",
    ef_md="Perda pela seca 53% → 36% (17,1 p.p.; o resumo escreve '17,1 ± 6,1%'); rendimento +16% irrigado, +27% chuva, +56% seca; plantio direto sem efeito (p=0,678; interação p=0,737). Cultura seguinte.",
    ef=("perda de rendimento do milho pela seca", -17.1, None, None, "p.p.", "cultura_seguinte"),
    onde="Elora, Ontário; 946 mm; 1 sítio, 1 safra (2016)", mod="N não limitante (161 kg N/ha); MOS associada, mecanismo não resolvido",
    cond=("úmido", "161", "alta", "36 anos de ensaio"), g="C", T="T3", ne="nao", ne_md="1 sítio úmido; seca de 35 dias", gl="Temperado úmido",
    ref="Renwick et al. 2021, ERL 16:084067", doi=[RENWICK], pg="p.2 resumo e p.6 (conferidos); Fig. 1a")

add(id="gaudin_elora", tipo="rotacao", t=1,
    nome="Diversificação em ensaio de 31 anos (alfafa, trigo, trevo) e clima do ano", cult="CCAA, CCSW, CCOrcBrc contra CCSS/CCCC", ant="alfafa; trigo; trevo", suc="milho; soja", base="milho-soja",
    ef_md="Milho com alfafa 8.928,9 contra 8.272,5 kg/ha (+7,9%); P(< p10) 5,7–6,8% contra 15,0%; trigo→soja +13%; anos quentes e secos milho +7%, soja +22%; anos frios e úmidos soja −24%. Cultura seguinte.",
    ef=("rendimento do milho (alfafa)", 7.9, None, None, "%", "cultura_seguinte"),
    onde="Elora, Ontário, continental úmido, 1982–2012", mod="160–180 kg N/ha; sinal muda com o tempo do ano",
    cond=("úmido", "160–180", "alta", "31 anos"), g="C", T="T3", ne="nao", ne_md="Ensaio único temperado; a métrica P(< p10) serve ao cartão", gl="Temperado",
    ref="Gaudin et al. 2015, PLoS ONE 10:e0113261", doi=[GAUDIN], pg="p.4 Tab. 1; p.9 Tab. 2; p.8–10 Figs. 3–4")

add(id="smith_milho_diversidade", tipo="rotacao", t=1,
    nome="Diversidade de espécies na rotação → milho (ensaios longos)", cult="rotações de Simpson até 4,57 → milho", ant="rotação diversa", suc="milho", base="monocultura com N baixo no ano 0",
    ef_md="Ano 5: +2,26 t/ha (IC95 1,81–2,71); ano 35: +4,19 t/ha (3,60–4,78); inclinação no ano 35: 1,00 t/ha por unidade (0,74–1,26) com N baixo contra 0,61 (0,40–0,82) com N alto. Cultura seguinte.",
    ef=("rendimento do milho", 2.26, 1.81, 2.71, "t/ha", "cultura_seguinte"),
    onde="América do Norte, temperado, sequeiro, 10–63 anos", mod="N externo, tempo, grupo funcional (leguminosa e ley); R² baixo ('caso a caso', p.6)",
    cond=("temperado", "baixo amplia", "alta", "5–35 anos"), g="B", T="T2", ne="parcial", ne_md="Só a forma (pouco N, mais ganho; cresce com os anos)", gl="Cereais temperados",
    ref="Smith et al. 2023, Commun Earth Environ 4:89", doi=[SMITH], pg="p.2–4; Fig. 2–3; Supl. Tab. 3")

add(id="smith_graos_pequenos", tipo="rotacao", t=1,
    nome="Diversidade em cereais de grão pequeno (corcova)", cult="rotações → trigo de inverno; cereais de primavera", ant="rotação diversa", suc="cereais de inverno e primavera", base="monocultura",
    ef_md="Inverno: +1,32 t/ha (1,01–1,62) em Simpson 3,91, caindo acima; primavera: +0,94 t/ha (0,74–1,13) em 3,9. Cultura seguinte.",
    ef=("rendimento do cereal de inverno", 1.32, 1.01, 1.62, "t/ha", "cultura_seguinte"),
    onde="Europa, temperado", mod="2–3 grupos funcionais são o ótimo", cond=("temperado", "—", "—", "35 anos"),
    g="B", T="T3", ne="nao", ne_md="Regra de retornos decrescentes, não número", gl="Europa",
    ref="Smith et al. 2023", doi=[SMITH], pg="p.2–3; Fig. 2")

add(id="marini_europa", tipo="rotacao", t=1,
    nome="Rotação diversa contra monocultura de cereais (Europa, só resumo)", cult="rotações → cereais", ant="rotação diversa", suc="cereais", base="monocultura de cereal",
    ef_md="Inverno +860 kg/ha/ano; primavera +390 kg/ha/ano; ganho maior em anos quentes e secos (até ~1.000 kg/ha). Cultura seguinte.",
    ef=("rendimento do cereal de inverno", 860.0, None, None, "kg/ha", "cultura_seguinte"),
    onde="7 ensaios longos na Europa", mod="Tempo do ano", cond=("temperado", "—", "—", "décadas"),
    g="C", T="T3", ne="nao", ne_md="Ano seco temperado ainda tem água", gl="Temperado",
    ref="Marini et al. 2020, ERL", doi=[MARINI], pg="Somente o resumo (PDF está em artigos/, não lido)")

add(id="pacheco17_soja_milho_nulo", tipo="rotacao", t=1,
    nome="Soja (+milheto) → milho + braquiária contra milho + braquiária contínuo — nulo de 1º ano", cult="soja → milho", ant="soja com milheto sobressemeado", suc="milho + U. ruziziensis", base="milho + braquiária → milho + braquiária",
    ef_md="SPD 6.857 contra 6.972 kg/ha (−1,6%, ns); SPC 8.095 contra 8.000 (+1,2%, ns). Cultura seguinte.",
    ef=("rendimento do milho", -1.6, None, None, "%", "cultura_seguinte"),
    onde="Bom Jesus-PI, Aw, Latossolo arenoso, 2011/12", mod="100 kg N/ha; SPD recém-implantado penaliza o milho",
    cond=("Aw", "100", "alta", "1 ano"), g="C", T="T2", ne="parcial", ne_md="Controle negativo: 1 ano com N mineral não mostra ganho", gl="Coerente com o desconto de N",
    ref="Pacheco et al. 2017, Rev Caatinga 30:13–23", doi=[PACH17], pg="Tab. 5 p.22; Tab. 2 p.16")

add(id="neves_sucessao_sal", tipo="sucessao", t=1,
    nome="Sucessão caupi irrigado com água salina (seca) → girassol (chuvas) — manejo do sal", cult="caupi → girassol", ant="caupi com 13 estratégias de água salina", suc="girassol", base="caupi com água boa (T1); sem girassol sem caupi",
    ef_md="Girassol sem diferença do controle em nenhuma estratégia (T1 1.345 'bc'; T4 1.258 'c'); CE do solo 6,18 → ~1,4 dS/m após o girassol; caupi −3% (só na floração) e −17% (cíclica) contra −34% (contínua); economia de 34,1–47,1% de água boa. Cultura seguinte (resíduo de sal).",
    ef=("rendimento do girassol seguinte", None, None, None, "kg/ha", "cultura_seguinte"),
    onde="Pentecoste-CE, BSw'h', 2011/12 (ano seco)", mod="Chuva entre as culturas (lavagem); estratégia de sal na floração ou cíclica",
    cond=("semiárido; mar–jun como 2012 é comum no interior", "—", "—", "1 ciclo"),
    g="C", T="T0", ne="sim", ne_md="Para perímetros com água salobra: regra de manejo do sal; não mede efeito de rotação", gl="Sim para irrigação com água salobra",
    ref="Neves et al. 2015, Ciênc Rural 45:814–820", doi=[NEVES], pg="Tab. 1–3 (p.816–819); p.817")

# =====================================================================================
# TABELA 2 — COBERTURA / ADUBO VERDE
# =====================================================================================
add(id="zhao_adubo_verde_milho", tipo="cobertura", t=2,
    nome="Adubo verde tropical → milho (mucuna, crotalária) — meta-análise", cult="mucuna; crotalária → milho", ant="adubo verde (sem grão)", suc="milho", base="antecessora não leguminosa",
    ef_md="Mucuna→milho +78% (IC95 59,1–99,4), o maior de 60 sequências; mucuna qualquer +58,6% (43,1–74,1); crotalária +60,4% (33,6–87,1). Base aberta (teste ZA): adubo verde→cereal tropical com AI < 0,5 +28,3% (−0,6 a +45,4; 9 sítios), irrigado +4,8%, > 120 kg N +5,8%. Cultura seguinte (a safra de grão perdida não entra).",
    ef=("rendimento do milho", 78.0, 59.1, 99.4, "%", "cultura_seguinte"),
    onde="Trópicos subúmidos (mucuna só com AI ≥ 0,49 e MAP ≥ 750 mm)", mod="Biomassa, N, água; o prêmio sobre a leguminosa de grão some no semiárido e no irrigado tecnificado",
    cond=("subúmido (AI ≥ 0,49)", "baixo (com > 120 kg N cai a +5,8%)", "baixa", "1 safra sem grão"),
    g="C", T="T2", ne="parcial", ne_md="No sequeiro só em revezamento tardio; teto 78%, centro realista 37,9% (Mudare)", gl="Trópicos úmidos onde a terra pode ficar uma safra sem grão",
    ref="Zhao et al. 2022", doi=[ZHAO, ZHAO_DADOS], pg="p.5 Fig. 5 (conferido); Supl. Tab. 1; base aberta (v4_agronomo_cobertura_debate_adubo_verde_zhao)")

add(id="mudare_crotalaria_mucuna_milho", tipo="cobertura", t=2,
    nome="Crotalária juncea, mucuna, alfafa e trevo → milho (pares)", cult="sun hemp; velvet bean; alfafa; trevo → milho", ant="leguminosa forrageira/adubo verde", suc="milho", base="milho contínuo",
    ef_md="Crotalária juncea→milho +83,43% (IC95 47,87–127,53; n=13) = o '83%' do texto; mucuna→milho +37,90% (20,55–57,75; n=24); alfafa→milho +20,15% (4,43–38,23; n=20); trevo→milho +8,24% ns. Cultura seguinte.",
    ef=("rendimento do milho (mucuna, centro realista)", 37.9, 20.55, 57.75, "%", "cultura_seguinte"),
    onde="Global", mod="n pequeno; não é efeito de 'forrageira temperada'",
    cond=("—", "—", "—", "1 safra sem grão"), g="C", T="T2", ne="parcial", ne_md="Crotalária só em perímetro irrigado/vazante; descontar a safra perdida",
    gl="Sim", ref="Mudare et al. 2025", doi=[MUD25], pg="p.2; Supl. Tab. 5 p.23; Source Data Fig. 2b (conferida pelo integrador)")

add(id="luz_crotalaria_fp_60d_milho", tipo="cobertura", t=2,
    nome="Crotalárias e feijão-de-porco por 60 d antes do milho em plantio direto (NE, irrigado no enchimento)", cult="C. juncea, C. spectabilis, feijão-de-porco → milho", ant="cobertura de 60 d", suc="milho BM 990", base="pousio capinado",
    ef_md="7,7 contra 7,1 Mg/ha (+8,5% pela conta; resumo diz +10%), média de 2021–2022; 2022 7,98 contra 6,40; interação cobertura × ano p=0,176. Cultura seguinte.",
    ef=("produtividade do milho", 8.5, None, None, "%", "cultura_seguinte"),
    onde="Arapiraca-AL, As, ~850 mm; milho irrigado 370/322 mm", mod="150 kg N/ha (coerente com adubo verde > 120 kg N +5,8%)",
    cond=("As com irrigação suplementar", "150", "alta", "2 safras"), g="C", T="T0", ne="parcial", ne_md="T0 para área irrigada; NÃO no sequeiro (o milho atrasado 60 d perde 40% da chuva do ciclo)",
    gl="Trópicos baixos com irrigação", ref="da Luz et al. 2023, Sustainability 15:15091", doi=[LUZ], pg="p.1 resumo; p.5–6 Fig. 3A; p.10")

add(id="luz_guandu_lablab_milheto_nulo", tipo="cobertura", t=2,
    nome="Guandu, lablab e milheto por 60 d antes do milho — nulo", cult="guandu, lablab, milheto → milho", ant="cobertura de 60 d", suc="milho", base="pousio capinado",
    ef_md="~7,4 Mg/ha, grupo 'b' com o pousio (7,1); guandu com 1,2 Mg/ha e 37 kg N/ha (não floresce em 60 d). Cultura seguinte.",
    ef=("produtividade do milho", 0.0, None, None, "%", "cultura_seguinte"),
    onde="Arapiraca-AL, irrigado no enchimento", mod="Ciclo da cobertura", cond=("As irrigado", "150", "alta", "2 safras"),
    g="C", T="T0", ne="sim", ne_md="Alerta: guandu de 60 d não serve como cobertura", gl="Latitudes baixas",
    ref="da Luz et al. 2023", doi=[LUZ], pg="p.5–6 Fig. 3A/3B; Fig. 4")

add(id="luz_economia_semente", tipo="cobertura", t=2,
    nome="Retorno de curto prazo da cobertura antes do milho (custo da semente)", cult="coberturas + milho", ant="cobertura", suc="milho", base="pousio + milho",
    ef_md="Retorno líquido contra o pousio: spectabilis +94, lablab +38, milheto +32, juncea −4, feijão-de-porco −118 US$/ha (2 safras). SEQUÊNCIA INTEIRA.",
    ef=("retorno líquido (feijão-de-porco)", -118.0, None, None, "US$/ha", "sequencia_inteira"),
    onde="Arapiraca-AL, milho irrigado tecnificado", mod="Taxa e custo da semente; preço e chuva do ano",
    cond=("irrigado", "150", "alta", "2 safras"), g="C", T="T2", ne="parcial", ne_md="Transfere a regra do custo da semente; os US$ não", gl="Qualitativo",
    ref="da Luz et al. 2023", doi=[LUZ], pg="Seção 2.3 p.5; 3.4 p.9 Fig. 6A")

add(id="luz_solo_cot_p", tipo="cobertura", t=2,
    nome="Cobertura antes do milho: COT e P disponível (0–10 cm)", cult="juncea, feijão-de-porco, spectabilis", ant="cobertura", suc="—", base="pousio",
    ef_md="COT +8,8% (7,9 contra 7,2 g/kg); P Mehlich +74% em 2021 (spectabilis e feijão-de-porco), +30–39% em 2022. Serviço.",
    ef=("COT 0–10 cm", 8.8, None, None, "%", "solo_ou_servico"),
    onde="Arapiraca-AL, franco-arenoso", mod="P aplicado a lanço", cond=("irrigado", "—", "—", "2 anos"),
    g="C", T="T0", ne="parcial", ne_md="Etiqueta de solo, não ganho de rendimento", gl="Direção", ref="da Luz et al. 2023", doi=[LUZ], pg="Seção 3.3 p.8 Fig. 5")

add(id="souza24_fp_milho_verde", tipo="cobertura", t=2,
    nome="Feijão-de-porco por 60 d antes do milho verde (mesma área de da Luz)", cult="feijão-de-porco → milho verde", ant="feijão-de-porco", suc="milho verde", base="pousio",
    ef_md="15,5 contra 14,3 Mg/ha (+8%; HSD). Outras coberturas sem ganho (juncea 6,0 Mg/ha de MS sem ganho; guandu e milheto −13 a −16% ns). Palhada de crotalária/feijão-de-porco: solo −2 °C. Cultura seguinte.",
    ef=("produtividade de milho verde", 8.0, None, None, "%", "cultura_seguinte"),
    onde="Arapiraca-AL, irrigado, 2023", mod="Não é sítio independente de da Luz 2023",
    cond=("irrigado", "120", "alta", "1 ano"), g="C", T="T0", ne="parcial", ne_md="Só irrigado; biomassa não prevê ganho", gl="Trópicos irrigados",
    ref="Souza et al. 2024, Stresses 4:699–713", doi=[SOUZA24], pg="p.701, p.703–705 Fig. 5")

add(id="nascimento_cobertura_caupi_nulo", tipo="cobertura", t=2,
    nome="Mucuna ou milheto por 60 d antes do caupi — nulo; rizóbio nativo iguala 50 kg N", cult="mucuna; milheto → caupi", ant="cobertura", suc="caupi Patativa", base="vegetação espontânea",
    ef_md="Todas as letras 'a' na coluna (Quadro 5): cobertura não mudou o grão do caupi; mucuna de −56% a +26% conforme a fonte de N; população nativa = 50 kg N/ha. O texto (p.584) contradiz o quadro. Cultura seguinte.",
    ef=("produtividade de grãos do caupi", 0.0, None, None, "%", "cultura_seguinte"),
    onde="Crato-CE, Aw, caupi irrigado (369,4 mm)", mod="Leguminosa antes de leguminosa",
    cond=("Aw irrigado", "0 a 50", "—", "1 ano"), g="C", T="T0", ne="sim", ne_md="Nulo transfere; o caupi não precisa de N mineral nem de cobertura para ter N",
    gl="Sim", ref="Nascimento et al. 2008, R Bras Ci Solo 32:579–587", doi=[NASC], pg="Quadro 3 p.583; Quadro 5 p.586")

add(id="andneto_adubo_verde_sorgo", tipo="cobertura", t=2,
    nome="Adubos verdes por 90 d antes do sorgo forrageiro (irrigado, sem teste)", cult="mucuna, lablab, juncea, caupi, guandu, feijão-de-porco → sorgo", ant="adubo verde 90 d", suc="sorgo BR 601", base="vegetação espontânea",
    ef_md="Sorgo aos 100 DAS pela curva: mucuna 10,69 contra 4,39 Mg/ha (+143%); lablab +60%; juncea +53%; caupi +40%; feijão-de-porco +17%. Sem teste entre tratamentos; r=0,66 com o N do adubo verde (n=9). Cultura seguinte.",
    ef=("MS do sorgo aos 100 DAS", 143.0, None, None, "%", "cultura_seguinte"),
    onde="Mossoró-RN, BSWh', tudo irrigado, 2005–2006", mod="Curva extrapolada (b=248 d); sódio alto no lablab",
    cond=("irrigado", "—", "—", "120 d antes do sorgo"), g="D", T="T0", ne="nao", ne_md="Descritivo; 120 d não cabem na quadra", gl="Irrigado tropical",
    ref="Andrade Neto et al. 2010, RBEAA 14:124–130", doi=[ANDNETO], pg="Tab. 1 p.126; Tab. 2 p.128")

add(id="miranda_fotoperiodo", tipo="cobertura", t=2,
    nome="Crotalária juncea: teto de biomassa por fotoperíodo (latitude baixa)", cult="C. juncea", ant="—", suc="—", base="densidades 10–100 pl/m²",
    ef_md="Floração aos 49–63 DAE; MS de 2,07–4,92 t/ha mesmo irrigada; dia de 11,8–12,4 h. No CE o dia mais longo vai de 12,29 a 12,58 h. Serviço.",
    ef=("MS da parte aérea", 3.39, 2.07, 4.92, "t/ha", "solo_ou_servico"),
    onde="Mossoró-RN (5°12'S), irrigado, 2009–2011", mod="Fotoperíodo; densidade (retorno por kg de semente cai até 90 pl/m²)",
    cond=("< ~15° de latitude", "—", "—", "~60 d"), g="C", T="T0", ne="sim", ne_md="Esperar 2–5 t/ha em ~60 d no CE inteiro; não importar biomassa de latitude alta",
    gl="Sim por latitude", ref="Miranda et al. 2020, Agron Colomb 38:148–155", doi=[MIRANDA], pg="p.149–154; Figs. 1–3")

add(id="montenegro_palhada_barreira", tipo="cobertura", t=2,
    nome="Palhada de braquiária e barreira de palma em nível (encosta, sem cultura)", cult="Brachiaria decumbens (palhada); palma em faixa", ant="—", suc="—", base="solo nu",
    ef_md="Escoamento mediano ~14% (nu) → ~4% (palhada) e ~7% (barreira de palma); perda de solo ~1 → ~0,1 e ~0,4 kg/parcela (box plots, aproximados). Serviço.",
    ef=("escoamento (% da chuva)", 4.0, None, None, "%", "solo_ou_servico"),
    onde="Pesqueira-PE, BSh, 600 mm, 2016–2018", mod="Dose de palha (4 ou 8 t/ha conforme a seção)",
    cond=("semiárido", "—", "—", "3 anos"), g="C", T="T0", ne="sim", ne_md="Serviço de conservação; a palhada precisa vir de algum lugar", gl="Encostas semiáridas",
    ref="Montenegro et al. 2019, Adv Geosci 48:19–30", doi=[MONTE], pg="Fig. 8 p.27; métodos p.23")

add(id="melo_fitomassa_leguminosas", tipo="cobertura", t=2,
    nome="Sistemas com leguminosas intercaladas: fitomassa e cobertura do solo", cult="milho + mucuna/fava/guandu", ant="—", suc="—", base="milho solteiro em plantio direto",
    ef_md="Sem NPK: 4,08 (SD) contra 5,56 (mucuna, +36%) e 5,70 Mg/ha (fava, +40%); com NPK as leguminosas ficaram abaixo do SD; cobertura > 80%. Serviço (sem teste nas células).",
    ef=("fitomassa na superfície", 36.0, None, None, "%", "solo_ou_servico"),
    onde="Alagoinha-PB, sequeiro, 2006–2008", mod="NPK; chuva do ano anterior", cond=("sequeiro", "0", "baixa", "9 anos"),
    g="C", T="T0", ne="sim", ne_md="Leguminosa sustenta palhada sem adubo; o 'até 76%' do resumo não se reproduz", gl="Trópicos quentes",
    ref="Melo et al. 2013, Ciênc Rural 43:1535–1541", doi=[MELO], pg="Tab. 1 p.1538; Fig. 1")

add(id="pacheco17_soja_apos_braquiaria", tipo="cobertura", t=2,
    nome="Soja após U. ruziziensis sobressemeada na soja (R5.5), 2º ano de plantio direto", cult="U. ruziziensis → soja", ant="braquiária em relay", suc="soja", base="soja após pousio",
    ef_md="SPD 3.876 contra 3.468 kg/ha (+11,8%; CV 2,48%, atípico); SPC 4.185 contra 4.076 (ns). Cultura seguinte.",
    ef=("produtividade da soja", 11.8, None, None, "%", "cultura_seguinte"),
    onde="Bom Jesus-PI, Aw, Latossolo arenoso", mod="Só em plantio direto; rebrota com as chuvas de outubro",
    cond=("Aw", "—", "alta", "1 ano"), g="C", T="T3", ne="nao", ne_md="No sertão só o desenho em relay transfere", gl="Savanas Aw (hipótese)",
    ref="Pacheco et al. 2017", doi=[PACH17], pg="Tab. 5 p.22; Tab. 2 p.16")

add(id="pacheco13_sobressemeadura_massa", tipo="cobertura", t=2,
    nome="Sobressemeadura de braquiária ou milheto na soja (R5.5): massa da entressafra", cult="U. ruziziensis; milheto (relay); milho + U. ruziziensis", ant="cobertura em relay", suc="—", base="pousio",
    ef_md="Aos 230 d: 10.842–12.743 contra 4.779 kg/ha (+127% a +167%); N 116–152 contra 40 kg/ha. Aos 160 d (antes das chuvas) só 5,5–5,9 t/ha. Serviço.",
    ef=("fitomassa aos 230 d", 140.0, 127.0, 167.0, "%", "solo_ou_servico"),
    onde="Bom Jesus-PI, Aw, entressafra 2011", mod="A massa vem da rebrota com o retorno das chuvas; mesmo experimento de Pacheco 2017",
    cond=("Aw com retorno de chuva antes da semeadura", "—", "—", "entressafra"), g="C", T="T3", ne="nao", ne_md="No sertão, no máximo o patamar de 160 d, não medido",
    gl="Savanas com retorno gradual da chuva", ref="Pacheco et al. 2013, Bragantia 72:237–246", doi=[PACH13], pg="Tab. 4 p.241; Tab. 5–6")

add(id="pacheco13_milheto_pos_colheita_falha", tipo="cobertura", t=2,
    nome="ALERTA: milheto semeado logo após a colheita da soja — falhou", cult="milheto a lanço pós-colheita", ant="—", suc="—", base="pousio",
    ef_md="4.908 contra 4.779 kg/ha aos 230 d (mesma letra); IMERG: 8 mm nos 30 d após a colheita de 2011. Serviço.",
    ef=("fitomassa aos 230 d", 2.7, None, None, "%", "solo_ou_servico"),
    onde="Bom Jesus-PI, Aw", mod="Chuva após a colheita", cond=("fim de chuva abrupto", "—", "—", "entressafra"),
    g="C", T="T2", ne="sim", ne_md="Mais forte no sertão (5–48 mm nos 30 d pós-colheita): veta cobertura pós-colheita", gl="Regra geral para fim de chuva abrupto",
    ref="Pacheco et al. 2013", doi=[PACH13], pg="Tab. 4 p.241; p.242")

add(id="pacheco13_milheto_pre_safra_nulo", tipo="cobertura", t=2,
    nome="Milheto pré-safra (out) antes da soja — nulo contaminado", cult="milheto → soja", ant="milheto 45 d", suc="soja", base="soja após pousio",
    ef_md="SPD 3.583 contra 3.707 kg/ha (−3,3%, ns); banco de sementes de milheto contaminou todas as parcelas. Cultura seguinte.",
    ef=("produtividade da soja", -3.3, None, None, "%", "cultura_seguinte"),
    onde="Bom Jesus-PI, 2010/11", mod="Tiguera anula o contraste", cond=("Aw", "—", "—", "1 ano"),
    g="C", T="T3", ne="nao", ne_md="Pré-safra consumiria a quadra no sertão", gl="Controle negativo",
    ref="Pacheco et al. 2013", doi=[PACH13], pg="Tab. 7 p.245; p.240")

add(id="pacheco11_milheto_arroz", tipo="cobertura", t=2,
    nome="Soja → milheto safrinha (dessecado na floração) → arroz de terras altas em plantio direto", cult="milheto → arroz; B. ruziziensis (+guandu) → arroz", ant="milheto; braquiária", suc="arroz BRS Sertaneja", base="pousio",
    ef_md="SPD: milheto 3.550 contra 2.423 kg/ha (+46,5%); B. ruziziensis +10% ns; braquiária+guandu +0,8% ns; arroz rendeu mais sobre a palha com MENOS massa. No ciclo seguinte (arroz→coberturas→soja) sem diferença (+7% máx., ns). Cultura seguinte.",
    ef=("produtividade do arroz", 46.5, None, None, "%", "cultura_seguinte"),
    onde="Rio Verde-GO (Cwa) — NÃO é Nordeste", mod="Momento da decomposição e imobilização de N (C/N 34 da braquiária)",
    cond=("Cwa", "60", "alta", "1 ano"), g="C", T="T2", ne="parcial", ne_md="Transfere a regra do momento do N, não o número", gl="Mecanismo geral",
    ref="Pacheco et al. 2011, R Bras Ci Solo 35:1787–1799", doi=[PACH11], pg="Quadro 8 p.1797; Quadros 2–3")

add(id="andrade25_entressafra_soja", tipo="cobertura", t=2,
    nome="Coberturas de entressafra (mai–ago) antes da soja (MATOPIBA)", cult="Tanzânia, Massai, caupi, C. juncea, milheto, Marandu, Ruziziensis, guandu → soja", ant="cobertura de entressafra", suc="soja", base="pousio com soja voluntária",
    ef_md="Contra o pousio (3.474 kg/ha, Fig. 3a lida em pixels): +24% a +29% (grupo a); Urochloa e guandu +10 a +16% (iguais ao pousio). O '+19–22%' do texto usa (T−C)/T. MBN 5,8–9,3× com leguminosas. Cultura seguinte.",
    ef=("produtividade da soja", 26.5, 24.0, 29.0, "%", "cultura_seguinte"),
    onde="Brejo-MA, Aw, ~1.680 mm; entressafra com 353 mm", mod="1 safra acima da média; pousio com soja voluntária (ponte verde)",
    cond=("Aw > 1.300 mm", "—", "—", "1 safra"), g="C", T="T3", ne="nao", ne_md="No sertão a entressafra tem 18–84 mm em 90 d", gl="Savanas úmidas",
    ref="Andrade et al. 2025, Agronomy 15:1083", doi=[], pg="Fig. 3a p.8 (pixels: v4_cerrado_andrade_fig3a_pixels); Tab. 3 p.8–9. DOI não verificado (fora do índice)")

add(id="silva22_laminas_massa", tipo="cobertura", t=2,
    nome="Cobertura de entressafra sob 4 lâminas de água (dose-resposta)", cult="amaranto, quinoa, milheto", ant="—", suc="—", base="lâmina de 432 mm",
    ef_md="Massa 6,84 / 9,47 / 9,94 / 10,04 Mg/ha com 167 / 268 / 381 / 432 mm (−31% com 167 mm; patamar a partir de ~270 mm). Amaranto grão 1.018 → 3.867 kg/ha (167 → 381 mm). Serviço.",
    ef=("massa seca da cobertura", 6.84, None, 10.04, "Mg/ha", "solo_ou_servico"),
    onde="Planaltina-DF, Aw, irrigado, adubado e capinado, 2015", mod="Água; frio impediu grão de milheto",
    cond=("irrigado", "100 + base", "—", "entressafra"), g="C", T="T3", ne="nao", ne_md="Abaixo de 167 mm o cartão diz 'sem número'", gl="Entressafras irrigadas",
    ref="Silva et al. 2022, Atmosphere 13:1617", doi=[], pg="Tab. 2 p.5; Tab. 5 p.7. DOI não verificado (fora do índice)")

add(id="palhada_meia_vida", tipo="cobertura", t=2,
    nome="Persistência da palhada: Cerrado quente (PI) contra ameno (GO)", cult="coberturas", ant="—", suc="—", base="—",
    ef_md="Meia-vida 5,4–15,4 d (Bom Jesus-PI) contra 42–177 d (Rio Verde-GO). Serviço.",
    ef=("meia-vida da palhada", 10.0, 5.4, 15.4, "dias", "solo_ou_servico"),
    onde="PI (Aw) e GO (Cwa)", mod="Temperatura, chuva pós-dessecação, lignina", cond=("quente", "—", "—", "—"),
    g="C", T="T2", ne="sim", ne_md="Direção: no sertão a palha some em dias e o gado a consome", gl="Direção",
    ref="Pacheco et al. 2017; Pacheco et al. 2011", doi=[PACH17, PACH11], pg="Pacheco 2017 Tab. 4 p.18–19; Pacheco 2011 Quadro 3 p.1793")

add(id="gaudin_trevo_revezamento", tipo="cobertura", t=2,
    nome="Trevo-vermelho em revezamento com cereal", cult="trevo semeado no trigo/aveia → milho", ant="trevo em relay", suc="milho", base="sem trevo",
    ef_md="P(milho > p90) 13,2% contra 7,2% com aração; sem ganho com preparo reduzido. Cultura seguinte.",
    ef=("P(rendimento > p90)", None, None, None, "probabilidade", "cultura_seguinte"),
    onde="Elora, Ontário", mod="Preparo", cond=("úmido", "—", "—", "31 anos"),
    g="C", T="T3", ne="nao", ne_md="O nicho do revezamento existe; o número não transfere", gl="Temperado com janela de outono",
    ref="Gaudin et al. 2015", doi=[GAUDIN], pg="p.7; Tab. 2 p.9")

add(id="king_blesh_carbono", tipo="cobertura", t=2,
    nome="Cobertura, perene e leguminosa de grão na rotação: entrada de C e COS (só resumo)", cult="grãos + cobertura; + perene; cereal + leguminosa de grão", ant="—", suc="—", base="só grãos / só cereal",
    ef_md="Cobertura: entrada de C +42%, COS +6,3%; perene: +23%, +12,5%; cereal + leguminosa de grão: entrada de C −16%, COS −5,3%. Serviço.",
    ef=("COS", 6.3, None, None, "%", "solo_ou_servico"),
    onde="27 sítios, 169 sistemas (clima não verificado)", mod="N ≤ 75 kg/ha/ano atenua a queda", cond=("não verificado", "—", "—", "—"),
    g="D", T="T3", ne="nao", ne_md="Alerta: leguminosa de grão não garante carbono", gl="Etiqueta",
    ref="King & Blesh 2018 (online 2017), Ecol Appl 28:249–261", doi=[KING], pg="Somente o resumo")

# =====================================================================================
# TABELA 3 — CONSORCIO NO ESPACO
# =====================================================================================
add(id="mudare22_milho_caupi", tipo="consorcio", t=3,
    nome="Consórcio milho/caupi (África)", cult="milho + caupi", ant="—", suc="milho + caupi na mesma estação", base="solteiros",
    ef_md="LER 1,37 ± 0,03 (média ± EP); receita 997 → 1.723 US$/ha (+73%; n=88); ganho absoluto só em figura. Sistema consorciado.",
    ef=("LER", 1.37, 1.31, 1.43, "LER", "sistema_consorciado"),
    onde="África, maioria em sequeiro", mod="LER = 1,45 − 0,00126·N; P aumenta o ganho absoluto",
    cond=("sequeiro africano", "LER cai com N", "baixa", "1 estação"), g="B", T="T2", ne="parcial", ne_md="Teto; no NE em sequeiro usar 1,15 (lâmina 0) como cenário seco; mostra que a S0 já capta ganho de terra",
    gl="Sim para pequenos produtores", ref="Mudare et al. 2022, Agron Sustain Dev 42:81", doi=[MUD22], pg="p.7 Fig. 3a e Tab. 1 (PDF fora do repositório; não reconferido)")

add(id="mudare22_milho_feijao", tipo="consorcio", t=3,
    nome="Consórcio milho/feijão-comum (África)", cult="milho + feijão-comum", ant="—", suc="consórcio", base="solteiros",
    ef_md="LER 1,34 ± 0,03; efeito líquido 1,89 ± 0,05 t/ha; receita +34% (n=40). Sistema consorciado.",
    ef=("LER", 1.34, 1.28, 1.40, "LER", "sistema_consorciado"),
    onde="África Oriental e Austral", mod="Clima mais fresco favorece o feijão-comum", cond=("fresco", "—", "—", "1 estação"),
    g="B", T="T2", ne="parcial", ne_md="Só serras e brejos", gl="Sim", ref="Mudare et al. 2022", doi=[MUD22], pg="p.7 Fig. 3a/3b, Tab. 1")

add(id="mudare22_milho_amendoim", tipo="consorcio", t=3,
    nome="Consórcio milho/amendoim (África)", cult="milho + amendoim", ant="—", suc="consórcio", base="solteiros",
    ef_md="LER 1,50 ± 0,05; efeito líquido 0,61 ou 0,70 t/ha (contradição na mesma p.7); receita +93% (n=25). Sistema consorciado.",
    ef=("LER", 1.50, 1.40, 1.60, "LER", "sistema_consorciado"),
    onde="África", mod="—", cond=("—", "—", "—", "1 estação"), g="C", T="T2", ne="parcial", ne_md="Só o LER", gl="Sim",
    ref="Mudare et al. 2022", doi=[MUD22], pg="p.7 Fig. 3, Tab. 1")

add(id="mudare22_milho_soja", tipo="consorcio", t=3,
    nome="Consórcio milho/soja (África e China)", cult="milho + soja", ant="—", suc="consórcio", base="solteiros",
    ef_md="África: LER 1,35 ± 0,02, efeito líquido 0,79 t/ha; China: LER 1,38, efeito líquido 2,43 t/ha. Sistema consorciado.",
    ef=("LER (África)", 1.35, 1.31, 1.39, "LER", "sistema_consorciado"),
    onde="África (baixo insumo) e China (irrigado, alto insumo)", mod="O LER é estável; o ganho absoluto escala com o insumo",
    cond=("—", "—", "—", "1 estação"), g="B", T="T3", ne="parcial", ne_md="A lição transfere; o par não", gl="Sim",
    ref="Mudare et al. 2022", doi=[MUD22], pg="p.7 Fig. 3, Tab. 1")

add(id="mudare22_arranjos", tipo="consorcio", t=3,
    nome="Arranjos do consórcio milho/leguminosa (linhas, faixas, mistura, relay) e P", cult="milho + leguminosa", ant="—", suc="consórcio", base="solteiros",
    ef_md="Linhas alternadas LER 1,37 (efeito líquido 0,90 t/ha); faixas 1,30 (0,56); mistura 1,48 (0,71); relay 1,35 (2,34 ± 0,13 t/ha); efeito líquido = 1,23 + 0,0148·P. Sistema consorciado.",
    ef=("LER (faixas)", 1.30, None, None, "LER", "sistema_consorciado"),
    onde="África, sequeiro", mod="P limita mais que N; texto e Fig. 5 divergem sobre o N",
    cond=("—", "—", "—", "1 estação"), g="B", T="T2", ne="parcial", ne_md="Relay cabe na quadra só com semeadura na 1ª chuva (não testado no semiárido)",
    gl="Sim", ref="Mudare et al. 2022", doi=[MUD22], pg="p.5; p.8 Fig. 4; p.10 Fig. 5")

add(id="souza11_milho_caupi_laminas", tipo="consorcio", t=3,
    nome="Consórcio milho + caupi 1:1 com 5 lâminas (Petrolina)", cult="milho + caupi", ant="—", suc="consórcio 1:1 (substituição)", base="solteiros",
    ef_md="Milho −13% e caupi −66% contra o solteiro (p.719); LER calculado por nós 1,37 (L125) → 1,15 (L0); Ye +22% → +7%; EUA menor no consórcio. Sistema consorciado.",
    ef=("LER (lâmina 0)", 1.15, None, 1.37, "LER", "sistema_consorciado"),
    onde="Petrolina-PE, BSwh', 548,7 mm; 1 ano irrigado", mod="Água (o caupi é quem perde); o consórcio recebeu 58–62 mm a mais",
    cond=("semiárido irrigado", "—", "—", "1 estação"), g="C", T="T0", ne="sim", ne_md="Teto do sequeiro ≈ 1,15; recomendar caupi solteiro ou faixa larga em semeadura tardia",
    gl="Sinal geral", ref="Souza et al. 2011, Bragantia 70:715–721", doi=[SOUZA11], pg="Tab. 1–2 (p.718), p.719 (conferido), Tab. 3 (p.720)")

add(id="souza15_kc_consorcio", tipo="consorcio", t=3,
    nome="Necessidade hídrica e Kc do consórcio milho + caupi", cult="milho + caupi", ant="—", suc="consórcio", base="solteiros",
    ef_md="ETc milho 387,1 → 439,4 mm (+13,5%); caupi 322,6 → 408,4 mm (+26,6%); Kc maior em todas as fases (Tab. 2). Sistema consorciado.",
    ef=("ETc do milho no consórcio", 13.5, None, None, "%", "sistema_consorciado"),
    onde="Petrolina-PE, irrigado", mod="Usar a Tab. 2 (as Conclusões trazem outros Kc)",
    cond=("semiárido", "—", "—", "1 estação"), g="C", T="T0", ne="sim", ne_md="Parâmetro de balanço: consórcio é eficiência de terra, não de água",
    gl="Sinal", ref="Souza et al. 2015, Rev Caatinga 28:151–160", doi=[SOUZA15], pg="Fig. 4 p.157; Tab. 2 p.158")

add(id="limafilho_milho_caupi", tipo="consorcio", t=3,
    nome="Consórcio milho + caupi 1:1, irrigado na seca (Petrolina, 1990)", cult="milho + caupi", ant="—", suc="consórcio", base="solteiros",
    ef_md="LER 1,13 (0,68 + 0,45); o '+18%' do texto são pontos de LER. Fotossíntese do caupi consorciado 11,0 contra 23,0 µmol m-2 s-1. Sistema consorciado.",
    ef=("LER", 1.13, None, None, "LER", "sistema_consorciado"),
    onde="Petrolina-PE, estação seca, 300 mm", mod="Sombreamento", cond=("irrigado", "—", "—", "1 estação"),
    g="C", T="T0", ne="parcial", ne_md="Repete o padrão: milho domina, caupi suprimido", gl="Mecanismo",
    ref="Lima Filho 2000, Pesq Agropec Bras 35:915–921", doi=[LIMAF], pg="Tab. 1 p.920; Figs. 2–4")

add(id="melo_relay_mucuna", tipo="consorcio", t=3,
    nome="Milho + mucuna-preta intercalada aos 85 DAP (relay), sem adubo — único sequeiro longo", cult="milho + mucuna (relay)", ant="—", suc="milho (com mucuna tardia)", base="milho solteiro em plantio direto",
    ef_md="Sem NPK 3.728 contra 3.447 kg/ha (+8,2%; letras bAB e bAB, ns); com NPK 5.047 contra 5.063. Sistema consorciado.",
    ef=("grão de milho, média de 9 anos", 8.2, None, None, "%", "sistema_consorciado"),
    onde="Alagoinha-PB, As', sequeiro, 2000–2008", mod="N (some com 90 kg N); veranico na floração",
    cond=("sequeiro (IMERG 667 mm; o artigo diz 1.100)", "0", "baixa", "9 anos"), g="C", T="T0", ne="sim", ne_md="Transfere o desenho (leguminosa tardia não custou milho), não um ganho",
    gl="Baixo N", ref="Melo et al. 2013", doi=[MELO], pg="Tab. 2 p.1539 (conferida)")

add(id="melo_fava_mucuna", tipo="consorcio", t=3,
    nome="Milho + fava + mucuna intercaladas, sem adubo", cult="milho + fava + mucuna", ant="—", suc="consórcio", base="milho solteiro em plantio direto",
    ef_md="4.000 contra 3.447 kg/ha (+16%; letra A contra AB, NÃO difere do SD). Sistema consorciado.",
    ef=("grão de milho, 9 anos", 16.0, None, None, "%", "sistema_consorciado"),
    onde="Alagoinha-PB, sequeiro", mod="N", cond=("sequeiro", "0", "baixa", "9 anos"),
    g="C", T="T0", ne="parcial", ne_md="Opção de baixo insumo; não citar como ganho", gl="Baixo N", ref="Melo et al. 2013", doi=[MELO], pg="Tab. 2 p.1539 (conferida)")

add(id="melo_guandu_mesmo_dia", tipo="consorcio", t=3,
    nome="ALERTA: milho + guandu semeados no mesmo dia", cult="milho + guandu", ant="—", suc="consórcio", base="milho solteiro em plantio direto",
    ef_md="Sem NPK 3.226 kg/ha (−6,4%; letra B, o mais baixo); com NPK 4.665 (−7,9%, B). Sistema consorciado.",
    ef=("grão de milho, 9 anos", -6.4, None, None, "%", "sistema_consorciado"),
    onde="Alagoinha-PB, sequeiro", mod="Competição na semeadura simultânea", cond=("sequeiro", "0 e 90", "baixa", "9 anos"),
    g="C", T="T0", ne="sim", ne_md="Guandu em faixa ou perene, nunca junto do milho", gl="Coerente", ref="Melo et al. 2013", doi=[MELO], pg="Tab. 2 p.1539 (conferida)")

add(id="diniz_palma_sorgo_ler", tipo="consorcio", t=3,
    nome="Palma OEM + sorgo SF-15: eficiência de uso da terra e MS contra o melhor solteiro", cult="palma forrageira + sorgo", ant="—", suc="consórcio (aditivo)", base="solteiros",
    ef_md="LER 1,51 (LERa 0,87; LERb 0,65; Tab. 3), ATER 1,30; desenho aditivo (pela razão das médias, LER 1,38). MS do sistema 12.130 'A' = sorgo solteiro 14.073 'A' > palma 4.627 'B' (Tab. 2). Sistema consorciado.",
    ef=("LER", 1.51, 1.30, None, "LER", "sistema_consorciado"),
    onde="Serra Talhada-PE, BSwh', 2014–15 (354,7 mm), gotejo salino", mod="LER estável de 355 a 1.012 mm; palma não responde à água acima de ~355 mm",
    cond=("semiárido", "—", "—", "1 ano"), g="C", T="T0", ne="parcial", ne_md="LER relativo transfere; no sequeiro conta 1 corte de sorgo; LER > 1 não supera o sorgo solteiro",
    gl="Plausível onde há Opuntia", ref="Diniz et al. 2017, Pesq Agropec Bras 52:724–733", doi=[DINIZ], pg="Tab. 2 p.728 e Tab. 3 p.731 (conferidas)")

add(id="lima18a_palma_sorgo_aguas", tipo="consorcio", t=3,
    nome="Palma + sorgo IPA-2502 sob 5 águas totais (chuva + gotejo)", cult="palma + sorgo", ant="—", suc="consórcio", base="palma solteira",
    ef_md="976 mm: 11,52 contra 8,71 t MS/ha (+32%, ns); 1.048: +67%; 1.202: +258%. Nenhum tratamento de sequeiro (o nível 0% ETo recebeu 583 mm). Sistema consorciado.",
    ef=("MS do sistema contra palma solteira (976 mm)", 32.0, None, 258.0, "%", "sistema_consorciado"),
    onde="Serra Talhada-PE, 2012–13 (393 mm; a janela mais seca em 27 anos no IMERG)", mod="Água total; só comparado com a palma solteira",
    cond=("irrigado", "—", "—", "1 ano"), g="C", T="T0", ne="parcial", ne_md="Só a ponta baixa; 0% dos municípios do CE chegaram a 976 mm em 1998, 2012 e 2016",
    gl="Não como número", ref="Lima et al. 2018a, Rev Caatinga 31:191–201", doi=[LIMA18A], pg="Tab. 2 p.198")

add(id="lima18a_palma_sorgo_bc", tipo="consorcio", t=3,
    nome="Palma + sorgo irrigado: custo e B/C", cult="palma + sorgo", ant="—", suc="consórcio", base="palma solteira",
    ef_md="Custo +R$ 530/ha (+4,4%) no 1º ano; B/C < 1 no 1º ano como forragem; > 1,1 do 2º ano em diante só por simulação (produtividade constante, água sem custo). SEQUÊNCIA INTEIRA.",
    ef=("custo de implantação", 4.4, None, None, "%", "sequencia_inteira"),
    onde="Serra Talhada-PE, preços de 2013", mod="Destino da palma (forragem ou 'semente'); água não cobrada",
    cond=("irrigado", "—", "—", "1 ano medido; 2–8 simulados"), g="D", T="T0", ne="parcial", ne_md="Portão 'fonte de água'; horizonte de retorno explícito", gl="Não",
    ref="Lima et al. 2018a", doi=[LIMA18A], pg="Tab. 3 p.198; Fig. 5 p.199")

add(id="lima18b_palma_sorgo_eua", tipo="consorcio", t=3,
    nome="Palma + sorgo: eficiência no uso da água e ET", cult="palma + sorgo", ant="—", suc="consórcio", base="palma solteira",
    ef_md="EUA 18,9 ± 7,4 contra 8,4 ± 3,4 kg MS/ha/mm (+125%); ET e ET/ET0 (0,50) não mudaram com o sorgo. Sistema consorciado.",
    ef=("EUA", 125.0, None, None, "%", "sistema_consorciado"),
    onde="Serra Talhada-PE, irrigado", mod="Hipótese CAM noturna + C4 diurna", cond=("irrigado", "—", "—", "1 ano"),
    g="C", T="T0", ne="parcial", ne_md="Direção: o Kc maior do milho+caupi NÃO vale para palma+sorgo", gl="Mecanismo plausível",
    ref="Lima et al. 2018b, RBEAA 22:113–118", doi=[LIMA18B], pg="Fig. 4 p.116–117")

add(id="jardim_clones_palma", tipo="consorcio", t=3,
    nome="Três clones de palma × três sorgos (alerta de clone)", cult="palma (Opuntia, Nopalea) + sorgo", ant="—", suc="consórcio", base="palma solteira",
    ef_md="Sem número de produtividade; biplots não separam solteiro e consórcio; Nopalea acumula menos fitomassa que Opuntia OEM. Sistema consorciado.",
    ef=("fitomassa da palma", None, None, None, "direção", "sistema_consorciado"),
    onde="Serra Talhada-PE, irrigado, 2017–18", mod="Clone e gênero", cond=("irrigado", "—", "—", "15 meses"),
    g="C", T="T0", ne="parcial", ne_md="O resultado depende do clone", gl="Não avaliado",
    ref="Jardim et al. 2020, RBEAA 24:756–761", doi=[], pg="Fig. 2 p.759. DOI não verificado (fora do índice)")

# =====================================================================================
# TABELA 4 — AGROFLORESTA / ILP
# =====================================================================================
add(id="perez_aleia_gliricidia_grao", tipo="agrofloresta", t=4,
    nome="Aleias de gliricídia (6 m) com milho: gradiente de distância", cult="gliricídia + milho", ant="—", suc="milho entre fileiras", base="distância da fileira (sem testemunha sem árvore)",
    ef_md="2003: 479 / 340 / 399 kg/ha a 1 / 2 / 3 m (ns); 2004: 317a / 179b / 122c. Sistema consorciado.",
    ef=("grão de milho a 1 m contra 3 m (2004)", 160.0, None, None, "%", "sistema_consorciado"),
    onde="Esperança-PB, Agreste, 800 mm, solo arenoso", mod="Ano (só no chuvoso); exportação da poda",
    cond=("semiárido-agreste", "0", "baixa", "2 anos"), g="C", T="T0", ne="parcial", ne_md="Não prova ganho de grão da aleia (a frase do resumo vale só para 2004)",
    gl="Fraco", ref="Pérez-Marin et al. 2006, R Bras Ci Solo 30:555–564", doi=[PEREZ], pg="Quadro 6 p.562")

add(id="perez_aleia_servicos", tipo="agrofloresta", t=4,
    nome="Aleias de gliricídia: solo e microclima", cult="gliricídia", ant="—", suc="—", base="0 contra 3 m da fileira",
    ef_md="Folhedo 1.390 contra 270 kg/ha; K 376 contra 162 mg/kg; temperatura máxima do solo −6 °C; umidade ~20% MENOR junto à fileira; COT sem diferença após 7 anos. Serviço.",
    ef=("folhedo", 1390.0, None, None, "kg/ha", "solo_ou_servico"),
    onde="Esperança-PB", mod="Poda; exportação de biomassa", cond=("semiárido-agreste", "—", "—", "7 anos"),
    g="C", T="T0", ne="sim", ne_md="Sombra e ciclagem ao custo de água no solo", gl="Sinal", ref="Pérez-Marin et al. 2006", doi=[PEREZ], pg="Quadros 1–5 (p.559–561)")

add(id="martins_aleia_milho_caupi", tipo="agrofloresta", t=4,
    nome="ALERTA: aleia de gliricídia + Manihot com milho + caupi", cult="gliricídia, Manihot glaziovii + milho + caupi", ant="—", suc="caupi na aleia", base="milho + caupi sem árvores",
    ef_md="Caupi 36a contra 410a kg/ha (letras iguais, ns); N fixado 2,66 contra 29,63 kg/ha; %Ndfa da gliricídia ao lado do grão 0%. Sistema consorciado.",
    ef=("grão do caupi", None, None, None, "kg/ha", "sistema_consorciado"),
    onde="Taperoá-PB, Bsh, 600 mm, 2009", mod="Competição por água; poda exportada",
    cond=("semiárido", "—", "—", "1 ano de amostragem"), g="C", T="T0", ne="sim", ne_md="Não prometer N nem grão ao caupi em aleia; reformular a linha 742 da proposta",
    gl="Alerta geral", ref="Martins et al. 2015, Pesq Agropec Bras 50:178–184", doi=[MARTINS], pg="Tab. 1 p.181 (conferida); Tab. 2 p.182")

add(id="martins_gliricidia_forrageira", tipo="agrofloresta", t=4,
    nome="Gliricídia com forrageira perene (buffel ou palma)", cult="gliricídia + buffel; gliricídia + palma", ant="—", suc="—", base="—",
    ef_md="%Ndfa 52,35 (buffel) e 51,62 (palma); N fixado nas pontas 43,2 e 39,3 kg/ha. Serviço.",
    ef=("N fixado nas pontas (palma)", 39.3, None, 43.2, "kg N/ha", "solo_ou_servico"),
    onde="Taperoá-PB", mod="Cultura associada", cond=("semiárido", "—", "—", "1 amostragem"),
    g="C", T="T0", ne="sim", ne_md="É o arranjo em que a gliricídia entrega N no semiárido", gl="Plausível",
    ref="Martins et al. 2015", doi=[MARTINS], pg="Tab. 2 p.182")

add(id="sacramento_agrossilvi", tipo="agrofloresta", t=4,
    nome="Agrossilvipastoril com esterco devolvido contra broca e queima (13 anos)", cult="leucena + milho + ovinos", ant="—", suc="—", base="broca e queima com pousio",
    ef_md="COT 0–40 cm de 2002 a 2011: agrossilvipastoril −5,13 Mg/ha (impresso −8,13); tradicional −58,87; caatinga +9,6. Serviço (ranking).",
    ef=("variação do COT 0–40 cm", -5.13, None, None, "Mg/ha", "solo_ou_servico"),
    onde="Sobral-CE, 821,6 mm, Luvissolo", mod="Retorno de esterco; uma área por sistema; linha de base de outro estudo",
    cond=("semiárido", "—", "—", "9–13 anos"), g="C", T="T0", ne="sim", ne_md="Vale o ranking (com esterco perde menos), não os Mg/ha", gl="Sinal",
    ref="Sacramento et al. 2013, R Bras Ci Solo 37:784–795", doi=[SACRA], pg="Tab. 2 p.788; Tab. 3 p.790; Tab. 5 p.792")

add(id="sacramento_silvipastoril", tipo="agrofloresta", t=4,
    nome="Silvipastoril por raleamento da caatinga, sem retorno", cult="caatinga raleada + ovinos", ant="—", suc="—", base="2002",
    ef_md="COT −23,87 Mg/ha (121,46 → 97,59); N −5,33 Mg/ha. Serviço.",
    ef=("variação do COT 0–40 cm", -23.87, None, None, "Mg/ha", "solo_ou_servico"),
    onde="Sobral-CE", mod="Sem retorno de resíduo nem esterco", cond=("semiárido", "—", "—", "9 anos"),
    g="C", T="T0", ne="sim", ne_md="Alerta: raleamento sem retorno não sequestra carbono", gl="Plausível",
    ref="Sacramento et al. 2013", doi=[SACRA], pg="Tab. 5 p.792")

add(id="primo_century", tipo="agrofloresta", t=4,
    nome="Agrofloresta permanente ou em rotação de 7 anos (simulação Century, só resumo)", cult="agrossilvipastoril → silvipastoril → caatinga", ant="—", suc="—", base="broca e queima com pousio",
    ef_md="Caatinga ~30,3 Mg/ha; broca e queima −50% em 10 anos; agroflorestas recuperam em ~10 anos (modelo). Serviço.",
    ef=("COS simulado", None, None, None, "Mg/ha", "solo_ou_servico"),
    onde="Semiárido (local não dito no resumo)", mod="Escala incompatível com Sacramento (30 contra 125–135 Mg/ha)",
    cond=("—", "—", "—", "décadas"), g="D", T="T3", ne="nao", ne_md="Só como cenário de modelo; rebaixar a linha 751 da proposta para D", gl="Não",
    ref="Primo et al. 2023, J Environ Manage 336:117594", doi=[PRIMO], pg="Somente o resumo")

add(id="pinheiro_manejo_caatinga", tipo="agrofloresta", t=4,
    nome="Manejo silvipastoril da Caatinga (raleamento, rebaixamento, enriquecimento)", cult="caatinga + bovinos, caprinos, ovinos", ant="—", suc="—", base="caatinga sem manejo",
    ef_md="Peso vivo (kg/ha/ano), sem manejo → enriquecimento: bovino 5,6 → 172; caprino 11,9 → 120; ovino 9,7 → 180; ganho diário do bovino na seca −155,7 → +25,0 g. Sistema.",
    ef=("ganho de peso vivo do bovino", 172.0, None, None, "kg/ha/ano", "sistema_consorciado"),
    onde="Caatinga, 260–800 mm (dados secundários de Araújo Filho)", mod="Espécie animal; declive; fosfato no enriquecimento",
    cond=("semiárido", "—", "—", "—"), g="C", T="T0", ne="sim", ne_md="Mostrar ao lado o carbono perdido no raleamento sem retorno (Sacramento)",
    gl="Fraca fora da Caatinga ('mais por intuição', p.12)", ref="Pinheiro & Nair 2018, For Syst 27:eR01S", doi=[PINHEIRO], pg="Tab. 2–5 (p.5–7)")

add(id="pinheiro_cobertura_morta", tipo="agrofloresta", t=4,
    nome="Cobertura morta e vegetação nativa contra perda de água e solo (citação secundária)", cult="—", ant="—", suc="—", base="área desmatada nua",
    ef_md="Redução > 70% (sem intervalo; Albuquerque et al. 2002, original não lido). Serviço.",
    ef=("perda de água e solo", -70.0, None, None, "%", "solo_ou_servico"),
    onde="Caatinga", mod="Não informado", cond=("semiárido", "—", "—", "—"),
    g="D", T="T2", ne="parcial", ne_md="Só direção (Montenegro 2019 cobre o serviço com dado do NE)", gl="Direção",
    ref="Pinheiro & Nair 2018", doi=[PINHEIRO], pg="p.10")

add(id="menezes_arvores_pasto", tipo="agrofloresta", t=4,
    nome="Juazeiro e algaroba em pastagem de buffel (só resumo)", cult="Ziziphus joazeiro; Prosopis juliflora + buffel", ant="—", suc="—", base="capim sem árvore",
    ef_md="Algaroba seca o solo no início da estação; juazeiro não muda a umidade e esfria solo e ar; N mineral maior sob as duas (sem números verificados). Serviço.",
    ef=("umidade do solo", None, None, None, "direção", "solo_ou_servico"),
    onde="Semiárido NE (sítio não informado no resumo)", mod="Espécie da árvore", cond=("semiárido", "—", "—", "—"),
    g="D", T="T0", ne="parcial", ne_md="Só direção, por espécie", gl="Prosopis existe em muitas terras secas",
    ref="Menezes, Salcedo & Elliott 2002, Agrofor Syst 56:27–38", doi=[MENEZES], pg="Somente o resumo")

add(id="zonta_ilp_lanco", tipo="ilp", t=4,
    nome="ILP: milho + braquiária a lanço no dia da semeadura (ano menos seco)", cult="milho + Piatã ou decumbens", ant="—", suc="milho + capim", base="milho solteiro",
    ef_md="2015 (389 mm): grão +2% (Piatã) e +16% (decumbens); silagem +90% e +44%; palhada 6,1 e 4,0 t MS/ha. Sem repetição nem estatística. Sistema consorciado.",
    ef=("silagem total", 90.0, None, None, "%", "sistema_consorciado"),
    onde="Lagoa Seca-PB, Agreste (14,1% de plantio direto)", mod="Espécie, modo de semeadura, chuva",
    cond=("agreste", "alto (MAP 160 + ureia)", "—", "1 ano"), g="D", T="T0", ne="parcial", ne_md="Ganho é silagem e palhada, não grão; sítio atípico", gl="Princípio conhecido",
    ref="Zonta et al. 2016, Embrapa Algodão Documentos 266", doi=[], pg="Tab. 5 p.21. Documento técnico sem DOI")

add(id="zonta_ilp_capins_vigorosos", tipo="ilp", t=4,
    nome="ALERTA ILP: capins vigorosos (Mombaça) competem com o milho", cult="milho + Mombaça, Urocloa a lanço, Andropógon", ant="—", suc="consórcio", base="milho solteiro",
    ef_md="Mombaça −43% (2015) e −38% (2016, mesmo com atrazina + mesotriona) no grão; Urocloa a lanço −23%; Andropógon −17%. Sem estatística. Sistema consorciado.",
    ef=("grão de milho (Mombaça)", -43.0, None, -38.0, "%", "sistema_consorciado"),
    onde="Lagoa Seca-PB, 2015 e 2016", mod="Vigor da espécie; chuva baixa", cond=("agreste", "—", "—", "2 anos"),
    g="D", T="T0", ne="sim", ne_md="Regra de exclusão por precaução (direção repetida em 2 anos)", gl="Plausível",
    ref="Zonta et al. 2016", doi=[], pg="Tab. 5 p.21; Tab. 6 p.22")

add(id="zonta_ilp_entrelinha_seco", tipo="ilp", t=4,
    nome="ILP em ano seco: capim na entrelinha ~20 DAS", cult="milho + Urocloa ou Piatã na entrelinha", ant="—", suc="consórcio", base="milho solteiro",
    ef_md="2016 (184 mm): Urocloa grão 0% e silagem +63%; Piatã +6% e +33%; Piatã a lanço −21%. Sem estatística. Sistema consorciado.",
    ef=("silagem total (Urocloa entrelinha)", 63.0, None, None, "%", "sistema_consorciado"),
    onde="Lagoa Seca-PB, 2016", mod="Chuva do ciclo; semente enterrada", cond=("agreste seco", "—", "—", "1 ano"),
    g="D", T="T0", ne="parcial", ne_md="Regra de manejo condicional à previsão seca; só onde há chuva no ciclo", gl="Não avaliado",
    ref="Zonta et al. 2016", doi=[], pg="Tab. 6 p.22")

add(id="rasmussen_gado", tipo="ilp", t=4,
    nome="Integração com gado em fazendas reais (observacional)", cult="lavoura + mamíferos, aves, abelhas, peixes", ant="—", suc="—", base="fazendas sem a estratégia",
    ef_md="Segurança alimentar +0,23 ± 0,03 DP (> 4× o efeito no rendimento, +0,05 ± 0,03); biodiversidade +0,16; árvores e cercas +0,21 DP com efeito negativo no bem-estar. Sistema (escala z).",
    ef=("segurança alimentar", 0.23, 0.17, 0.29, "DP", "sistema_consorciado"),
    onde="2.655 fazendas, 11 países (5 conjuntos do Brasil)", mod="Tamanho da fazenda; paisagem", cond=("vários", "—", "—", "—"),
    g="C", T="T2", ne="parcial", ne_md="Direção para cabras + palma; não vira número de cartão", gl="Associação",
    ref="Rasmussen et al. 2024, Science 384:87–93", doi=[RASM], pg="PDF p.6; Tab. S12")

# =====================================================================================
# TABELA 5 — QUEBRA DE PRAGA
# =====================================================================================
add(id="vazio_algodao_oeste_ba", tipo="quebra_de_praga", t=5,
    nome="Vazio regional do algodão (≥ 4 meses) + destruição de soqueira + semeadura concentrada", cult="algodão", ant="vazio sem algodão", suc="algodão", base="safra anterior (antes e depois)",
    ef_md="'Efetiva redução populacional' (sem número) e economia de US$ 2 milhões em pulverizações; sem área de controle. Praga.",
    ef=("população do bicudo", None, None, None, "direção", "praga"),
    onde="Oeste da Bahia, Cerrado", mod="Adesão coletiva; pacote de táticas", cond=("—", "—", "—", "≥ 4 meses de vazio"),
    g="C", T="T2", ne="parcial", ne_md="Princípio vale; no sertão o furo é o mocó perene e o algodão irrigado", gl="Cinturões de algodão com bicudo",
    ref="Azambuja & Degrande 2014, Arq Inst Biol 81:377–410 (citando Degrande 2001)", doi=[AZAMB], pg="p.394–395")

add(id="plano_goias_soqueira", tipo="quebra_de_praga", t=5,
    nome="Plano de Goiás: soqueira destruída em até 15 d e semeadura concentrada", cult="algodão", ant="—", suc="algodão", base="safra anterior",
    ef_md="+2,5% a +23% de produção quando adotado na íntegra (antes e depois, sem controle). Cultura seguinte.",
    ef=("produção de algodão", None, 2.5, 23.0, "%", "cultura_seguinte"),
    onde="Goiás, Cerrado", mod="Adoção integral", cond=("—", "—", "—", "1 safra"), g="C", T="T2", ne="parcial", ne_md="Exige coordenação comunitária", gl="Sim",
    ref="Azambuja & Degrande 2014 (citando Degrande 2003)", doi=[AZAMB], pg="p.396")

add(id="destruicao_restos_soqueira_isca", tipo="quebra_de_praga", t=5,
    nome="Destruição imediata dos restos (roçadeira + gradagem) com faixa de soqueira-isca; enterrio de maçãs", cult="algodão", ant="—", suc="—", base="só roçado",
    ef_md="Menor captura de bicudos com roçado + gradeado + faixa-isca (sem número); maçãs enterradas a 5–15 cm: adultos não emergem (qualitativo). Praga.",
    ef=("bicudos capturados", None, None, None, "direção", "praga"),
    onde="Brasil (estudos citados)", mod="Mecanização (limitada na agricultura familiar)", cond=("—", "—", "—", "pós-colheita"),
    g="C", T="T2", ne="parcial", ne_md="É o vazio sanitário do pacote agroecológico", gl="Sim",
    ref="Azambuja & Degrande 2014 (Soares 1993/1994; Ribeiro 2006b)", doi=[AZAMB], pg="p.387 e p.389")

add(id="consorcio_algodao_milho_nulo", tipo="quebra_de_praga", t=5,
    nome="CARTÃO NULO: consórcio algodão + milho contra o bicudo", cult="algodão + milho", ant="—", suc="consórcio", base="algodão solteiro",
    ef_md="'Não afeta a população do bicudo'. Praga.",
    ef=("população do bicudo", 0.0, None, None, "direção", "praga"),
    onde="Não informado (Ramalho & Gonzaga 1989b, 1990, original não lido)", mod="O milho não é hospedeiro nem repelente",
    cond=("—", "—", "—", "—"), g="C", T="T2", ne="sim", ne_md="Consórcio no espaço não quebra o ciclo de especialista móvel", gl="Sim como regra",
    ref="Azambuja & Degrande 2014", doi=[AZAMB], pg="p.395")

add(id="epoca_semeadura_algodao", tipo="quebra_de_praga", t=5,
    nome="Época de semeadura do algodão sob bicudo (calendário único)", cult="algodão", ant="—", suc="—", base="outubro",
    ef_md="12 maçãs/planta (out), 3 (nov), 0 (dez). Praga.",
    ef=("maçãs por planta", 12.0, 0.0, None, "maçãs/planta", "praga"),
    onde="Não informado", mod="Plantio tardio aumenta gerações", cond=("—", "—", "—", "—"),
    g="C", T="T2", ne="parcial", ne_md="No sertão a época é ditada pela chuva: plantio coordenado", gl="Sim",
    ref="Azambuja & Degrande 2014 (Soares & Araújo 1993)", doi=[AZAMB], pg="p.388")

add(id="hospedeiro_bicudo_adulto", tipo="quebra_de_praga", t=5,
    nome="Status de hospedeiro do parceiro de rotação para o bicudo adulto (e crotalária)", cult="sorgo, quiabo, margaridão, caupi, milheto, soja, crotalária", ant="parceiro de rotação/entressafra", suc="algodão", base="botão de algodão",
    ef_md="Só quiabo, sorgo e margaridão mantiveram 50% dos adultos vivos > 7 d; caupi, milheto e soja NÃO mantiveram (o que ≠ 'não alimenta': há pólen de Fabaceae e Poaceae no intestino, Ribeiro 2010); crotalária 7,60 d contra 97,66 d em botão. Praga.",
    ef=("longevidade do adulto (crotalária)", 7.6, None, None, "dias", "praga"),
    onde="Laboratório, Brasil", mod="Malváceas alternativas esticam a vida (Hibiscus tiliaceus 131,6 d)", cond=("—", "—", "—", "—"),
    g="C", T="T2", ne="sim", ne_md="Perto do algodão: caupi ou crotalária, nunca sorgo/quiabo", gl="Sim",
    ref="Azambuja & Degrande 2014 (Vidal 2010; Cunha 2010; Gabriel 1986)", doi=[AZAMB], pg="p.381–382")

add(id="faustino_gotejo_aspersao", tipo="quebra_de_praga", t=5,
    nome="Gotejamento contra aspersão: dessecação do bicudo nos botões caídos", cult="algodão irrigado", ant="—", suc="—", base="microaspersão",
    ef_md="0,00 ± 0,00 contra 0,35 ± 0,11 adulto/gaiola (P<0,01); 0 de 588 contra 6 de 585 botões; solo a 41 °C e 9,7% UR contra 37 °C e 16%. Praga.",
    ef=("adultos emergidos por gaiola", 0.0, None, 0.35, "adultos/gaiola", "praga"),
    onde="Barbalha-CE, jul–set/2019, 16 repetições", mod="1 safra, gaiola sem inimigos naturais, solo arenoso",
    cond=("semiárido irrigado", "—", "—", "1 safra"), g="C", T="T0", ne="sim", ne_md="O solo quente e seco já mata imaturos: o alvo do vazio é o adulto", gl="Climas quentes com gotejo",
    ref="Faustino et al., Braz J Biol 83:e248154", doi=[FAUST], pg="p.3–6; Fig. 1–2; Tab. 1")

add(id="catacao_poda_tubos_isca", tipo="quebra_de_praga", t=5,
    nome="Catação de botões, poda apical e tubos-isca", cult="algodão", ant="—", suc="—", base="sem a tática",
    ef_md="Catação 2,8×, poda apical 2,5× e as duas 4,8× menos bicudos; tubos-isca 1,8 contra 5,4 bicudos/armadilha em 7 semanas. Praga.",
    ef=("redução da população (catação + poda)", 4.8, None, None, "vezes", "praga"),
    onde="Não informado (citações secundárias)", mod="Mão de obra; malation restrito no orgânico", cond=("—", "—", "—", "—"),
    g="C", T="T2", ne="sim", ne_md="Já é prática dos consórcios do semiárido", gl="Sim",
    ref="Azambuja & Degrande 2014 (Neves 2010; Vivan 2009)", doi=[AZAMB], pg="p.387–389")

add(id="mip_rotacao_ms", tipo="quebra_de_praga", t=5,
    nome="MIP com rotação de culturas como um dos componentes (MS)", cult="algodão", ant="pacote", suc="algodão", base="média regional",
    ef_md="6,5 → 4,7 aplicações de inseticida por safra; a parte da rotação não se separa. Praga.",
    ef=("aplicações por safra", -27.7, None, None, "%", "praga"),
    onde="Mato Grosso do Sul", mod="Pacote confundido", cond=("—", "—", "—", "—"),
    g="C", T="T2", ne="parcial", ne_md="Não atribuir o número à rotação (como cartão de rotação é D)", gl="Parcial",
    ref="Azambuja & Degrande 2014 (Degrande 1993)", doi=[AZAMB], pg="p.395")

add(id="mattos_consorcio_algodao_faixas", tipo="quebra_de_praga", t=5,
    nome="Consórcio agroecológico em faixas com algodão em ≤ 50% da área", cult="algodão + milho, feijão, gergelim, amendoim", ant="—", suc="consórcio em faixas com rotação na área", base="convencional da agricultura familiar",
    ef_md="B/C 1,29 (800 kg/ha) contra 0,14 (1.500 kg/ha); exercício econômico do BNB sem ano, preço, chuva nem controle; ganho vem do prêmio de preço (2×). Sequência/sistema.",
    ef=("relação benefício/custo", 1.29, None, None, "B/C", "sistema_consorciado"),
    onde="Semiárido NE, sequeiro, ~1 ha", mod="Prêmio de preço; mão de obra", cond=("semiárido", "—", "—", "—"),
    g="D", T="T0", ne="parcial", ne_md="Comparar com e sem prêmio; não é redução de praga medida", gl="Depende de mercado orgânico",
    ref="Mattos et al. 2020, Desenvolv Meio Ambiente 55:556–580 (citando Araújo Filho 2013)", doi=[MATTOS], pg="Tab. 1 p.576; p.569")

add(id="moco_perene_sem_vazio", tipo="quebra_de_praga", t=5,
    nome="Algodão anual perto de capoeira com mocó perene (hospedeiro sem vazio)", cult="algodão; mocó", ant="—", suc="—", base="—",
    ef_md="'Elevados níveis de infestação, com danos bastante significativos' (qualitativo). Praga.",
    ef=("infestação do bicudo", None, None, None, "direção", "praga"),
    onde="Caatinga", mod="O mocó é invisível no PAM e nos mapas", cond=("semiárido", "—", "—", "—"),
    g="D", T="T0", ne="sim", ne_md="Justifica o mapa de hospedeiro verde na seca no portão", gl="Regra geral",
    ref="Mattos et al. 2020 (citando Lima 2020)", doi=[MATTOS], pg="p.565–566")

add(id="nematoides_amendoim_caupi", tipo="quebra_de_praga", t=5,
    nome="Nematoides: amendoim contra caupi antes de sorgo/milheto (resultados contraditórios)", cult="amendoim; caupi → sorgo; milheto", ant="amendoim; caupi", suc="sorgo; milheto", base="cereal contínuo",
    ef_md="Bado 2011: caupi→sorgo 1,5–2,0× mais nematoides; amendoim→sorgo 17–19× menos. Alvey 2001: milheto após caupi OU amendoim com 60–80× menos. Marschner 2004: amendoim inconsistente. Praga (contagem, não rendimento).",
    ef=("nematoides no cereal (amendoim→sorgo)", None, None, None, "direção", "praga"),
    onde="África Ocidental", mod="Pratylenchus e Meloidogyne têm hospedeiros amplos", cond=("—", "—", "—", "—"),
    g="C", T="T2", ne="parcial", ne_md="Nenhuma leguminosa é quebra garantida; amendoim só com diagnóstico de solo", gl="Regra de hospedeiro",
    ref="Franke et al. 2018 (citando Bado 2011; Alvey 2001; Marschner 2004)", doi=[FRANKE], pg="Seção Pests and diseases (XML)")

add(id="striga_principio", tipo="quebra_de_praga", t=5,
    nome="Leguminosa não hospedeira contra striga (princípio; número excluído)", cult="guandu → milho", ant="guandu", suc="milho", base="milho com striga",
    ef_md="Princípio: a não hospedeira induz germinação suicida e reduz o banco de sementes; o consórcio suprime menos. O caso de +765% (Manica) foi excluído da média pelos próprios autores e NÃO entra como número. Praga.",
    ef=("banco de sementes de striga", None, None, None, "direção", "praga"),
    onde="Manica, Moçambique", mod="Striga não verificada no NE", cond=("—", "—", "—", "—"),
    g="C", T="T3", ne="nao", ne_md="Só princípio no portão de pragas", gl="Onde há Striga (África, Índia)",
    ref="Franke et al. 2018 (citando Rusinamhodzi 2012)", doi=[FRANKE], pg="Tab. 2; seções Overview of responses e Weeds")

add(id="push_pull_lagarta", tipo="quebra_de_praga", t=5,
    nome="Push-pull adaptado ao clima (Desmodium + Brachiaria) contra a lagarta-do-cartucho", cult="milho + Desmodium + borda de Brachiaria", ant="—", suc="consórcio", base="milho solteiro",
    ef_md="Infestação −87% e rendimento 2,7× (citação de Midega 2018, original não lido). Sistema consorciado.",
    ef=("infestação da lagarta", -87.0, None, None, "%", "praga"),
    onde="Áreas secas da África Oriental", mod="Volátil repelente; estabelecimento do Desmodium com 500–800 mm não testado",
    cond=("seco tropical", "—", "—", "—"), g="C", T="T2", ne="parcial", ne_md="Hipótese C·T; consórcio, não rotação", gl="Sim, África Oriental",
    ref="Kenis et al. 2022, Entomol Gen (citando Midega 2018)", doi=[KENIS], pg="p.25")

add(id="abobora_lagarta", tipo="quebra_de_praga", t=5,
    nome="Contraexemplo: milho + abóbora e a lagarta-do-cartucho", cult="milho + abóbora", ant="—", suc="consórcio", base="milho",
    ef_md="Correlacionado com AUMENTO do dano (sem número). Praga.",
    ef=("dano da lagarta", None, None, None, "direção", "praga"),
    onde="Zimbábue (levantamento)", mod="Observacional", cond=("—", "—", "—", "—"),
    g="D", T="T2", ne="parcial", ne_md="Alerta: cucurbitácea é comum no roçado", gl="Contraexemplo",
    ref="Kenis et al. 2022 (citando Baudron 2019)", doi=[KENIS], pg="p.25")

add(id="palhada_paisagem_lagarta", tipo="quebra_de_praga", t=5,
    nome="Cultivo mínimo/palhada e paisagem arborizada contra a lagarta-do-cartucho", cult="milho", ant="—", suc="—", base="preparo convencional; paisagem aberta",
    ef_md="Cultivo mínimo com palhada reduz o dano e aumenta inimigos naturais (sem número; rendimento inconsistente); infestação menor em paisagem com árvores (no prelo). Praga.",
    ef=("dano da lagarta", None, None, None, "direção", "praga"),
    onde="Américas; Zâmbia, Malawi, Brasil", mod="Palha disputa com o gado; fragmentos abrigam desserviços", cond=("—", "—", "—", "—"),
    g="D", T="T2", ne="parcial", ne_md="Só direção", gl="Qualitativo",
    ref="Kenis et al. 2022", doi=[KENIS], pg="p.24–25")

add(id="percolacao_ponte_verde", tipo="quebra_de_praga", t=5,
    nome="Rotação simulada dos talhões da ponte verde (percolação QUADRA)", cult="hospedeiro em t e t+1", ant="rotação de uma fração f dos talhões", suc="—", base="f = 0",
    ef_md="Raio 300 m: Texas algodão 0,65 → 0,22 (f=0,3) → 0,09 (f=0,5); Apodi-CE 0,58 → 0,25 (f=0,5); raio 5 km: conectado em todas as janelas (S 0,961–1,000). Praga (estrutura).",
    ef=("fração da ponte verde no maior aglomerado (300 m, f=0,5)", 0.25, None, None, "fração", "praga"),
    onde="Janelas de 40 km nos EUA (CDL) e no CE (Impact Observatory)", mod="Raio de dispersão da praga; classe 'lavoura' do CE fraca",
    cond=("—", "—", "—", "—"), g="D", T="T0", ne="parcial", ne_md="Filtro de viabilidade: rotação no talhão só fragmenta pragas de dispersão curta", gl="Sim como filtro",
    ref="Análise própria (scripts/percolacao.py)", doi=[], pg="E:/campeonato-nasa/dados/percolacao/cenarios.csv e metricas.csv")

# =====================================================================================
# TABELA 6 — MODULADORES E SINTESES (regras do motor, nao cartoes de par)
# =====================================================================================
add(id="mod_n_fertilizante", tipo="modulador", t=6,
    nome="Modulador N: a vantagem da leguminosa cai com o adubo nitrogenado", cult="leguminosa → qualquer", ant="leguminosa", suc="—", base="antecessora não leguminosa",
    ef_md="−7% a cada 50 kg N/ha (Fig. 2c); nulo > 236 kg N/ha (p.3, conferido); monocultura sem N +41,0% caindo 7,9%/50 kg; base aberta −0,061 lnRR/50 kg (EP 0,006), sem interação seco × N (p=0,87); sequeiro com N ≤ 50: −17 a −19%/50 kg. Cultura seguinte.",
    ef=("inclinação do bônus por 50 kg N/ha", -7.0, None, None, "p.p.", "cultura_seguinte"),
    onde="Global", mod="Interação N × diversidade (P<0,001)", cond=("sem interação com aridez", "0–236", "—", "—"),
    g="A", T="T1", ne="sim", ne_md="No sertão (N ≈ 0) sem desconto; nos perímetros com N alto, a base da curva", gl="Sim, regra principal do modo global",
    ref="Zhao et al. 2022; Franke 2018 Tab. 3; Mudare 2025 Supl. Tab. 2", doi=[ZHAO, ZHAO_DADOS, FRANKE, MUD25], pg="Zhao p.2–3 Fig. 2c, 3a; v4_satelite_espaco_tempo_zhao S1–S2")

add(id="mod_diversidade_controle", tipo="modulador", t=6,
    nome="Modulador diversidade do controle (D = espécies × grupos × espécies/ano; só controle não leguminoso)", cult="leguminosa → qualquer", ant="leguminosa", suc="—", base="controle não leguminoso com diversidade D",
    ef_md="Sem N: +50% em D=1 e −6,6% por unidade; com N: +17% e −2,1%; ns para D > 9. Base aberta, N ≤ 50: D=1 +41,3% (167 sítios); D 2–4 +30,9%; D 6–9 +9,4% (5,0–14,4; 23 sítios). No estrato quente-seco, D > 1 não reduz (+42,6%, 10 sítios). Cultura seguinte.",
    ef=("bônus com controle D 6–9 (N ≤ 50)", 9.4, 5.0, 14.4, "%", "cultura_seguinte"),
    onde="Global", mod="Não se aplica a consórcio com leguminosa (fora do domínio da Eq. 1)", cond=("no quente-seco não reduz", "0–50", "—", "—"),
    g="A", T="T2", ne="parcial", ne_md="Inclinação A; a extrapolação para a S0 (D=8 → +4%) é D e foi rejeitada como número", gl="Sim",
    ref="Zhao et al. 2022", doi=[ZHAO, ZHAO_DADOS], pg="p.2–3 Fig. 2d, 3b; p.6 Eq. 1; v4_engenheiro_debate_base_diversa blocos 1–2")

add(id="mod_produtividade", tipo="modulador", t=6,
    nome="Modulador nível de produtividade da base", cult="leguminosa → qualquer", ant="leguminosa", suc="—", base="controle de baixa × alta produtividade",
    ef_md="+32% em ambiente de baixa produtividade contra +7% em alta (resumo, conferido; Fig. 4a); 79% dos ganhos > 20% vêm de controles abaixo da média. Cultura seguinte.",
    ef=("bônus em ambiente de baixa produtividade", 32.0, None, None, "%", "cultura_seguinte"),
    onde="Global", mod="Baixa produtividade por N/estresse biótico ≠ por água", cond=("—", "baixo", "baixa amplia", "—"),
    g="A", T="T2", ne="parcial", ne_md="Aplicar só no ano colhido e com teto absoluto; não somar ao bônus de N=0", gl="Sim",
    ref="Zhao et al. 2022", doi=[ZHAO], pg="p.1 resumo (conferido); p.4 Fig. 4a")

add(id="mod_regiao", tipo="modulador", t=6,
    nome="Prior por continente", cult="leguminosa → qualquer", ant="leguminosa", suc="—", base="não leguminosa",
    ef_md="África +43%, América do Norte +19%, Ásia +12% (Fig. 4b). Na base aberta, a África dá +44% com MAT < 20 e com MAT ≥ 20 (o prêmio é de sistema/insumo, não de clima). Cultura seguinte.",
    ef=("bônus na África", 43.0, None, None, "%", "cultura_seguinte"),
    onde="Continentes", mod="N e produtividade", cond=("mistura zonas", "—", "—", "—"),
    g="B", T="T2", ne="parcial", ne_md="Não usar 43% no sertão; usar o estrato de aridez", gl="Prior por continente no modo global",
    ref="Zhao et al. 2022", doi=[ZHAO, ZHAO_DADOS], pg="p.4 Fig. 4b; v4_satelite_espaco_tempo_zhao S3")

add(id="mod_aridez_relativo", tipo="modulador", t=6,
    nome="Aridez não reduz o efeito relativo (síntese)", cult="leguminosa → cereal", ant="leguminosa", suc="cereal", base="várias",
    ef_md="Zhao base aberta com EF de país: +0,4% por 0,1 de AI (ns); análogo quente-seco +23,6% contra +23,5% previsto; Mudare: < 500 = 500–1.000 mm (0,16 = 0,16); Franke: zona × resposta p=0,351 (Sahel 24% = Guiné 24%). Base aberta, cereal N ≤ 50 não irrigado: < 500 mm +49% (4 sítios); 500–600 +43% (12); 600–700 +33% (9). Cultura seguinte.",
    ef=("efeito do AI por 0,1 (EF país)", 0.4, None, None, "p.p.", "cultura_seguinte"),
    onde="Global", mod="O que cai é a t/ha e a chance de colher", cond=("todas", "—", "—", "—"),
    g="B", T="T1", ne="sim", ne_md="Centro igual; IC mais largo no ano seco; quebra à parte", gl="Sim",
    ref="Zhao 2022 (base aberta); Mudare 2025; Franke 2018", doi=[ZHAO_DADOS, MUD25, FRANKE], pg="v4_satelite_espaco_tempo_zhao S1; v4_metodologo_debate_checagens; Franke Tab. 3")

add(id="mod_temperatura", tipo="modulador", t=6,
    nome="Temperatura: inclinação dentro da região ≠ contraste entre climas", cult="leguminosa → cereal", ant="leguminosa", suc="—", base="—",
    ef_md="Kluger: leguminosa antecessora com 6 de 9 bT negativos (estação mais quente, menos benefício). Zhao entre climas: MAT +1,9% por 5 °C com EF de país (p=0,11); sequeiro N ≤ 50: −0,2% (p=0,92). Cultura seguinte.",
    ef=("efeito de +5 °C de MAT entre climas (EF país)", 1.9, None, None, "p.p.", "cultura_seguinte"),
    onde="Celeiros temperados; global", mod="Espaço ≠ tempo", cond=("—", "—", "—", "—"),
    g="C", T="T2", ne="parcial", ne_md="Sem desconto no prior; ano quente de El Niño = hipótese C de redução", gl="Só dentro de celeiros",
    ref="Kluger et al. 2025; Zhao 2022 (base aberta)", doi=[KLUGER, ZHAO_DADOS], pg="Kluger Tab. S9, Fig. 4, p.13; v4_satelite_espaco_tempo_zhao S1–S2")

add(id="mod_chuva_estacao", tipo="modulador", t=6,
    nome="Chuva da estação da cultura seguinte (sinal)", cult="antecessora → cultura seguinte", ant="—", suc="—", base="—",
    ef_md="21 de 36 bP positivos e significativos, 4 negativos; leguminosas 8 de 9 positivos; pousio com sinal oposto (bP −3,4*). Mediana |bP| 1,40 p.p. por IQR. Cultura seguinte.",
    ef=("bP mediano (leguminosas)", 1.6, None, None, "p.p. por IQR", "cultura_seguinte"),
    onde="EUA, Canadá, França, China", mod="Moderador no NE = água da estação da cultura seguinte (IMERG/SMAP)", cond=("—", "—", "—", "—"),
    g="B", T="T2", ne="parcial", ne_md="Transfere o sinal, não a magnitude", gl="Sim em direção",
    ref="Kluger et al. 2025", doi=[KLUGER], pg="Tab. S9 (p.64); Fig. 4 (p.9)")

add(id="mod_retornos_decrescentes", tipo="modulador", t=6,
    nome="Retornos decrescentes: sair da monocultura vale mais que diversificar além de 2 culturas", cult="outra → A → B", ant="—", suc="—", base="B → A → B",
    ef_md="Diversificar: média +1,23% (mediana 0,75%; 12 de 34 negativos) contra +4,52% da rotação de 2 anos (3,67×; texto ~3,7×, p.13, conferido). Cultura seguinte.",
    ef=("ganho de diversificar além de 2 culturas", 1.23, None, None, "%", "cultura_seguinte"),
    onde="EUA, Canadá, França", mod="Negativo com soja antes do milho", cond=("—", "—", "—", "3 anos"),
    g="B", T="T2", ne="sim", ne_md="Não prometer ganho de uma 3ª ou 4ª cultura", gl="Sim",
    ref="Kluger et al. 2025; Smith 2023; Zhao 2022", doi=[KLUGER, SMITH, ZHAO], pg="Kluger p.13, Fig. 5, Tab. S9")

add(id="mod_maclaren_n_leguminosa", tipo="modulador", t=6,
    nome="Diversificar com ou sem leguminosa conforme o N; cultura de fertilidade; esterco; resíduos", cult="rotação ou consórcio", ant="—", suc="cultura-teste", base="monocultura",
    ef_md="Com leguminosa: ganho com N ≤ 100 kg/ha e nenhum acima; sem leguminosa: ganho maior com N alto; ley plurianual ajuda mesmo com leguminosa presente; esterco > material vegetal, maior sem leguminosa; manter resíduos: nulo. Números só nas figuras. Cultura seguinte.",
    ef=("razão de rendimento", None, None, None, "direção", "cultura_seguinte"),
    onde="30 ensaios longos: Inglaterra, Quênia, Malawi, Moçambique, Holanda, Nigéria, Escócia, África do Sul, Suécia, Zâmbia, Zimbábue", mod="N; rotação e consórcio no mesmo índice",
    cond=("—", "≤ 100 para leguminosa", "—", "≥ 9 anos"), g="C", T="T2", ne="parcial", ne_md="Direção: com pouco N a leguminosa rende; esterco e leguminosa são substitutos (não somar)",
    gl="Sim como regra qualitativa", ref="MacLaren et al. 2022, Nat Sustain 5:770–779", doi=[MACLAREN], pg="PDF p.5 Fig. 1a–b; p.5–6 Fig. 2 e 4; p.8 (países)")

add(id="mod_raveloaritiana", tipo="modulador", t=6,
    nome="Diversificação de longo prazo: rendimento, lucratividade, pragas e serviços", cult="6 práticas de diversificação", ant="—", suc="—", base="convencional",
    ef_md="Rendimento sem mudança significativa no tempo; lucratividade lnRR 0,1259 (< 3 anos) → 0,3633 (20 anos) = +13% → +44% (o '+189%' é 0,3633/0,1259 − 1; conferido); controle de pragas ns até 50 anos; serviços +37% a +107% (base do % não verificada). SEQUÊNCIA INTEIRA.",
    ef=("lucratividade em 20 anos", 44.0, None, None, "%", "sequencia_inteira"),
    onde="184 meta-análises, 6.741 efeitos; pouco de países de renda baixa", mod="Duração; viés geográfico",
    cond=("—", "—", "—", "20 anos"), g="B", T="T2", ne="parcial", ne_md="Freio de rendimento e de praga; lucro só na etiqueta de 10–20 anos", gl="Sim",
    ref="Raveloaritiana & Wanger 2026, Nat Commun 17:1016", doi=[RAVELO], pg="p.4 (conferido); p.5–8")

add(id="mod_rasmussen_temporal", tipo="modulador", t=6,
    nome="Diversificação temporal e combinação de estratégias em fazendas reais", cult="rotação, cobertura, várias estratégias", ant="—", suc="—", base="fazendas sem a estratégia",
    ef_md="Diversificação temporal: rendimento +0,01 ± 0,02 DP (p=0,74); combinar estratégias: segurança alimentar +0,24, biodiversidade +0,19, rendimento 0,00. SEQUÊNCIA/SISTEMA (escala z).",
    ef=("rendimento (diversificação temporal)", 0.01, -0.03, 0.05, "DP", "sequencia_inteira"),
    onde="2.655 fazendas, 11 países", mod="Observacional", cond=("—", "—", "—", "—"),
    g="C", T="T2", ne="parcial", ne_md="Freia a promessa de rendimento; apoia comparar pacotes", gl="Associação",
    ref="Rasmussen et al. 2024", doi=[RASM], pg="Tab. S12 (PDF p.52–54); PDF p.5–6")

add(id="mod_beillouin", tipo="modulador", t=6,
    nome="Diversificação de culturas em geral (todas as estratégias; só resumo)", cult="agrofloresta, consórcio, cobertura, rotação, mistura de cultivares", ant="—", suc="—", base="simplificado",
    ef_md="Produção mediana +14%; biodiversidade +24%; água +51%; pragas e doenças +63%; solo +11% (medianas de todas as estratégias). Serviço.",
    ef=("produção mediana", 14.0, None, None, "%", "solo_ou_servico"),
    onde="95 meta-análises, 85 países", mod="Estratégia", cond=("—", "—", "—", "—"),
    g="D", T="T3", ne="nao", ne_md="Não atribuir à rotação; só contexto (nem ao portão de pragas)", gl="Panorama",
    ref="Beillouin et al. 2021, Glob Change Biol 27:4697–4710", doi=[BEILL], pg="Somente o resumo")

add(id="mod_rusinamhodzi_ac", tipo="modulador", t=6,
    nome="Agricultura de conservação (direto, rotação, palhada) por chuva, N e textura", cult="milho", ant="—", suc="milho", base="preparo convencional",
    ef_md="< 600 mm: ganho que cresce com o tempo (Fig. 6a); 600–1.000 mm sem tendência; > 1.000 mm perda; mais ganho com N > 100 kg/ha; ganho em franco e arenoso, perda em argiloso. Cultura seguinte.",
    ef=("diferença de rendimento ao longo do tempo", None, None, None, "direção", "cultura_seguinte"),
    onde="Mundo, sequeiro", mod="N, herbicida, palhada (que no sertão vai para o gado)", cond=("< 600 mm favorece", "> 100", "—", "≥ 5 anos"),
    g="C", T="T2", ne="parcial", ne_md="Pacote, não efeito de rotação; exige N e palha", gl="Sim",
    ref="Rusinamhodzi et al. 2011", doi=[RUSI], pg="Resumo; p.663 Fig. 6; p.665–667 Figs. 8–9")


# ---------------- parametros do NE para o motor (dados nossos) ----------------
PARAMETROS_NE = {
    "freq_quebra_milho": {
        "definicao": "rendimento por ha PLANTADO < 0,5 da mediana do proprio municipio (a definicao por area colhida depende da UF que informa)",
        "CE_2000_2024": 0.188, "CE_1988_2025": 0.227, "NE_2000_2024": 0.210,
        "fonte": "conselho/analises/v4_leguminosas_antecessoras_debate.saida.txt (C4, C5)",
        "grau": "D (proxy dos nossos dados)"},
    "quebra_conjunta_milho_feijao_CE": {"p_ambos": 0.117, "p_se_independentes": 0.035, "spearman": 0.71,
                                         "fonte": "v4_agroecologo_consorcio_ler_pam.saida.txt (bloco B)"},
    "preco_feijao_sobre_milho_NE": {"razao_por_kg": 3.61, "fonte": "v4_leguminosas_antecessoras_testes.saida.txt (bloco F)", "grau": "D"},
    "ler_consorcio_milho_caupi": {"sequeiro_ano_seco": 1.15, "teto_com_agua": 1.37,
                                   "fonte": "Souza 2011 (Tab. 1-2, LER calculado); Mudare 2022 (p.7)"},
    "aridez_CE_POWER": {"AI_mediano": 0.34, "p10": 0.28, "p90": 0.49, "fonte": "v4_metodologo_transferencia_moderadores.saida.txt (E1)"},
    "teto_biomassa_cobertura_60d_CE": {"Mg_ha": [2, 5], "fonte": "Miranda 2020; v4_agronomo_cobertura_rotacao_artigos (bloco B)"},
    "custo_hidrico_cobertura_pre_milho": {"chuva_ciclo_milho_mm": [641, 387], "perda": -0.40,
                                          "fonte": "v4_agronomo_cobertura_rotacao_artigos.saida.txt (bloco C)"},
}

REGRAS_MOTOR = [
    ("G01", "Bônus de rotação só no cenário 'colheu'; a quebra (18,8% CE, 21,0% NE) é modelada à parte com IMERG/SMAP."),
    ("G02", "Combinar e aplicar em lnRR sobre o rendimento local; converter para kg/ha pela distribuição local dos anos colhidos."),
    ("G03", "Base certa ou nada: prior de leguminosa só contra base sem leguminosa; contra o consórcio S0 o efeito é 'não medido' (D)."),
    ("G04", "Descontar N: −6 a −7% por 50 kg N/ha (sequeiro com N baixo: até −17 a −19%); nulo acima de ~236 kg; no sertão N ≈ 0."),
    ("G05", "A aridez não muda o centro relativo; no ano seco (LGP < 150 d) só alargar o IC até 0."),
    ("G06", "Escolher o estrato pelo índice de aridez e pela temperatura (não pela chuva anual); o ano entra pela água da estação da cultura seguinte."),
    ("G07", "Transferir pares com ≥ 5 sítios no estrato (T1); sem isso, só direção (T2) ou limite inferior do IC como recurso."),
    ("G08", "Não ranquear caupi, amendoim, feijão e soja pelo bônus; faixa comum; o sorgo responde como o milho."),
    ("G09", "Cultura seguinte e sequência inteira são decisões diferentes; a sequência é calculada com preço local; cartões negativos obrigatórios."),
    ("G10", "Efeito multiplicativo não é seguro de cauda; não subir o pior ano com o bônus."),
    ("G11", "Plano de 3 anos usa o efeito do 1º ciclo; ganhos de décadas vão para a etiqueta de 10–20 anos."),
    ("G12", "Irrigado não é análogo de sequeiro; perímetros usam a faixa baixa."),
    ("G13", "Espaço não é tempo; temperatura dentro da região não explica diferença entre climas."),
    ("G14", "Rotação no tempo e consórcio no espaço têm cartões separados; LER > 1 não autoriza dizer que supera o melhor solteiro."),
    ("G15", "Cobertura em sequeiro no NE só em relay tardio ou faixa perene, sem bônus de grão; pós-colheita vetada."),
    ("G16", "Não retirar o pousio/recarga sem balanço hídrico; pousio e sorgo entram sempre como estratégias comparáveis."),
    ("G17", "Praga sem número de meta-análise; quebra por biologia do hospedeiro e mobilidade; vazio regional sincronizado."),
]
