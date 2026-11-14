"""Integrador (v4): aplica ao catalogo a conferencia do verificador adversario
(v4_verificador_catalogo_conferencias.py e .saida.txt) e acrescenta ao .md a secao "Verificacao adversaria".

Edita so pesquisa/catalogo_rotacoes_comprovadas.md e pesquisa/catalogo_rotacoes.json.
Roda sobre a saida do gerador (v4_integrador_catalogo_rotacoes.py) e recusa rodar duas vezes.
Cada troca de texto exige que o trecho antigo exista exatamente uma vez; as linhas de cartao do .md sao
re-renderizadas a partir do JSON corrigido, no mesmo formato do gerador (conferido antes de editar).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
PROJ = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa")
MD = PROJ / "pesquisa" / "catalogo_rotacoes_comprovadas.md"
JS = PROJ / "pesquisa" / "catalogo_rotacoes.json"
SECAO = "## Verificação adversária"
SCRIPT = "conselho/analises/v4_integrador_correcao_verificador.py"
HOJE = datetime.now().strftime("%Y-%m-%d %H:%M")

md = MD.read_text(encoding="utf-8")
if SECAO in md:
    raise SystemExit("a verificação adversária já foi aplicada a este .md: nada a fazer")
cat = json.loads(JS.read_text(encoding="utf-8"))
if "verificacao_adversaria" in cat:
    raise SystemExit("a verificação adversária já foi aplicada a este JSON: nada a fazer")
C = {c["id"]: c for c in cat["configuracoes"]}
ANTES = {k: Counter(c[k] for c in cat["configuracoes"]) for k in ("tipo", "grau", "transferencia")}

# ------------------------------------------------------------- formato da linha (igual ao gerador)
NE_TXT = {"sim": "Sim", "parcial": "Parcial", "nao": "Não"}


def cel(s):
    return str(s).replace("|", "/").replace("\n", " ")


def linha(c):
    dois = "; ".join(c["referencias"]) if c["referencias"] else "DOI não verificado"
    g = f"{c['grau']}·{c['transferencia']}"
    if c.get("grau_direcao"):
        g += f" (direção: {c['grau_direcao']})"
    return "| " + " | ".join(cel(x) for x in [
        f"**{c['configuracao']}** (base: {c['base_comparacao']}) `{c['id']}`",
        c["culturas"], c["efeito_texto"], c["onde"], c["moduladores"], g,
        f"{NE_TXT[c['transfere_ne']]}: {c['transfere_ne_motivo']}",
        c["transfere_global"], c["referencia_texto"], f"{dois} — {c['fonte_pagina']}"]) + " |"


LINHAS = md.split("\n")
IDX = {}
for i, l in enumerate(LINHAS):
    if l.startswith("| **"):
        for cid in C:
            if f"`{cid}` |" in l:
                assert cid not in IDX, f"cartão em duas linhas: {cid}"
                IDX[cid] = i
assert set(IDX) == set(C), f"cartões sem linha no .md: {set(C) - set(IDX)}"
ruins = [cid for cid in C if linha(C[cid]) != LINHAS[IDX[cid]]]
assert not ruins, f"o formato re-renderizado não bate com o gerador em {ruins[:5]}"
print(f"conferido: as {len(C)} linhas de cartão do .md batem com o JSON antes da correção")

# ------------------------------------------------------------- utilitários de troca
NOTAS = {}


def troca(cid, campo, velho, novo):
    s = C[cid][campo]
    assert s.count(velho) == 1, (cid, campo, s.count(velho), velho[:70])
    C[cid][campo] = s.replace(velho, novo)


def poe(cid, nota, **campos):
    for k, v in campos.items():
        assert k in C[cid] or k in ("efeitos_adicionais", "ancoras_verificaveis", "grau_direcao"), (cid, k)
        C[cid][k] = v
    NOTAS[cid] = (NOTAS[cid] + " " + nota) if cid in NOTAS else nota


def troca_md(velho, novo):
    global md
    n = md.count(velho)
    assert n == 1, (n, velho[:90])
    md = md.replace(velho, novo)


# ============================================================ A. os 20 números
# Item 3: N (mod_n_fertilizante)
poe("mod_n_fertilizante", "Item 3: −7% vem da p.2/Fig. 2c; 236 kg da p.3/Fig. 3a; −6% e −17 a −19% são análise própria.",
    efeito_texto=("−7% a cada 50 kg N/ha (p.2, Fig. 2c); com diversidade 1 (monocultura) +41,0% sem N, caindo 7,9% por "
                  "50 kg, e com diversidade alta −3,2% por 50 kg (Fig. 3a); nulo > 236 kg N/ha (p.3, do modelo de interação "
                  "N × diversidade da Fig. 3a, 'regardless of crop diversification'; conferido). Análise própria da base "
                  "aberta, não do artigo: −0,061 lnRR/50 kg (EP 0,006), sem interação seco × N (p=0,87); sequeiro com "
                  "N ≤ 50: −17 a −19%/50 kg. Cultura seguinte."),
    fonte_pagina=("Zhao p.2 e Fig. 2c (−7%); p.3 e Fig. 3a (236 kg; −7,9% e −3,2%); análise própria: "
                  "v4_satelite_espaco_tempo_zhao S1–S2"))

# Item 5: produtividade (mod_produtividade)
poe("mod_produtividade", "Item 5: +32% × +7% só no resumo, sem IC; Fig. 4a e p.4 só a direção; número C, direção A.",
    grau="C", grau_direcao="A",
    efeito_texto=("+32% em ambiente de baixa produtividade contra +7% em alta: números só no resumo (p.1), sem IC; a Fig. 4a "
                  "é uma curva loess de lnRR contra o rendimento padronizado, sem 32% nem 7% impressos; o corpo (p.4) dá só "
                  "a direção: acima da média do banco o ganho é 'nearly constant and negligible' e 79% dos ganhos > 20% "
                  "ocorrem abaixo da média. 'Baixa' e 'alta' = abaixo e acima da média do banco inteiro (comparação entre "
                  "estudos, não dentro do talhão). Cultura seguinte."),
    fonte_pagina="resumo p.1 (número); p.4 e Fig. 4a (só direção)")

# Item 9: Mudare por classe de chuva (mudare_classes_chuva)
troca("mudare_classes_chuva", "efeito_texto", "contra 0,05 e 0,03. Cultura seguinte.",
      "contra 0,05 e 0,03. Análogo quente na mesma aba (MAT): leguminosa com MAT > 20 °C lnR 0,20 (0,05–0,34; n=228) = "
      "+22% (+5 a +40), mesma letra 'a' das classes frias. Cultura seguinte.")
poe("mudare_classes_chuva", "Item 9: classe de chuva anual inclui terras secas frias (T1 → T2); 626 de 1.726 obs.; "
    "acrescentado o análogo MAT > 20 °C.",
    transferencia="T2",
    transfere_ne_motivo=("Direção: a leguminosa ainda ganha abaixo de 500 mm e a quebra sem leguminosa rende mais ali; a "
                         "classe é de chuva anual (inclui terras secas frias), por isso T2"),
    moduladores=("Valor só na Source Data; classe por chuva anual, não por aridez (< 500 mm inclui terras secas frias); o "
                 "recorte por MAP usa só 626 das 1.726 observações de leguminosa"),
    fonte_pagina="Source Data aba Supplementary Figure S5-S6, linhas MAP e MAT (conferidas)")

# Item 11: conflito da mucuna -> milho (Zhao +78% x Mudare +37,9%)
troca("mudare_crotalaria_mucuna_milho", "efeito_texto", "mucuna→milho +37,90% (20,55–57,75; n=24);",
      "mucuna→milho +37,90% (20,55–57,75; n=24; conflito: o Zhao, p.5 e Fig. 5, dá mucuna→milho +78%, IC 59,1–99,4, "
      "contra antecessora não leguminosa);")
poe("mudare_crotalaria_mucuna_milho", "Item 11: conflito com o Zhao (mucuna→milho +78%) mostrado.")
troca("zhao_adubo_verde_milho", "efeito_texto", "Mucuna→milho +78% (IC95 59,1–99,4), o maior de 60 sequências;",
      "Mucuna→milho +78% (IC95 59,1–99,4), o maior de 60 sequências (conflito: o Mudare 2025 dá +37,90%, 20,55–57,75, "
      "contra milho contínuo);")
poe("zhao_adubo_verde_milho", "Item 11: conflito com o Mudare (mucuna→milho +37,90%) mostrado.")

# Item 12: Mudare na África
troca("mudare_africa_leg_naoleg", "efeito_texto",
      "= +29% (13–47); não leguminosa lnR 0,0223 (−0,183 a 0,228; n=36) = +2,3% ns.",
      "= +28,9% (+13,4 a +46,5); não leguminosa lnR 0,0223 (−0,183 a 0,228; n=36) = +2,3% (−16,7 a +25,6), ns por "
      "imprecisão (n=36), não prova de efeito nulo.")
poe("mudare_africa_leg_naoleg", "Item 12: o ns da não leguminosa é imprecisão (n=36), não efeito nulo.")

# Item 13: cartões negativos de sequência
poe("mudare_neg_cereal_para_leg_cereal",
    "Item 13: receita −53,1% (soja-milho) e −47,1% (soja-sorgo) da Source Data no lugar do −50% sem IC; 73,8% só no "
    "cenário rendimento-receita-energia; n da aba não serve de peso.",
    efeito={"variavel": "receita bruta da sequência: soja-milho no lugar de milho contínuo", "central": -0.7579,
            "baixo": -0.836, "alto": -0.680, "unidade": "lnRR", "na": "sequencia_inteira", "pct": [-53.1, -56.6, -49.3]},
    efeitos_adicionais=[{"variavel": "receita bruta da sequência: soja-sorgo no lugar de sorgo contínuo",
                         "central": -0.6371, "baixo": -0.772, "alto": -0.503, "unidade": "lnRR",
                         "na": "sequencia_inteira", "pct": [-47.1, -53.8, -39.5]}],
    efeito_texto=("Texto p.4: energia −27%, micronutrientes −53% e receita −50%, juntando as duas trocas. Source Data (aba "
                  "Figure 3e, base da Fig. 3g): soja-milho no lugar de milho contínuo, receita lnR −0,758 (−0,836 a −0,680) "
                  "= −53,1% (−56,6 a −49,3) e energia −31,0% (−36,4 a −25,1); soja-sorgo no lugar de sorgo contínuo, "
                  "receita lnR −0,637 (−0,772 a −0,503) = −47,1% (−53,8 a −39,5) e energia −23,7% (−33,6 a −12,4). As "
                  "colunas n da aba parecem desalinhadas (soja-sorgo e milho-trigo com n=216; a Fig. 2b dá soja→sorgo "
                  "n=106): não usar n como peso. Perde-perde-perde em 73,8% só no cenário rendimento-receita-energia "
                  "(Supl. Tab. 7, p.26); 78,97% em Mg, Fe e Zn; 8,58% na proteína. SEQUÊNCIA INTEIRA."),
    fonte_pagina="p.4 e p.6–7; Fig. 3g; Source Data aba Figure 3e (conferida pelo verificador); Supl. Tab. 7 (p.26) e 8")
poe("mudare_neg_sorgo_para_milho_sorgo",
    "Item 13: n=10 (B → C); IC de energia e receita da Source Data no JSON; 'sorgo tolerante' é leitura do conselho; "
    "veto vira alerta.",
    grau="C",
    efeito={"variavel": ("energia da sequência: milho-sorgo no lugar de sorgo contínuo (o rendimento −32% do texto p.4 "
                         "não tem linha nem IC na Source Data)"),
            "central": -0.3871, "baixo": -0.607, "alto": -0.167, "unidade": "lnRR", "na": "sequencia_inteira",
            "pct": [-32.1, -45.5, -15.4]},
    efeitos_adicionais=[{"variavel": "receita bruta da sequência: milho-sorgo no lugar de sorgo contínuo",
                         "central": -0.3718, "baixo": -0.587, "alto": -0.157, "unidade": "lnRR",
                         "na": "sequencia_inteira", "pct": [-31.1, -44.4, -14.5]}],
    efeito_texto=("Texto p.4: rendimento −32%, nutrição −23% e receita −31% ('subprodução transgressiva'). A Source Data "
                  "(aba Figure 3e) não tem linha de rendimento por sequência; tem energia lnR −0,387 (−0,607 a −0,167) = "
                  "−32,1% (−45,5 a −15,4) e receita lnR −0,372 (−0,587 a −0,157) = −31,1% (−44,4 a −14,5), n=10. "
                  "SEQUÊNCIA INTEIRA."),
    moduladores=("O artigo não estratifica por clima: 'sorgo é o cereal tolerante' é leitura do conselho; n=10; colunas n "
                 "da aba Figure 3e desalinhadas"),
    transfere_ne_motivo=("Alerta de direção, não veto numérico: no sertão seco, não trocar sorgo contínuo por milho-sorgo "
                         "sem calcular a sequência (grau C, n=10)"),
    fonte_pagina="p.4; Fig. 3g; Source Data aba Figure 3e (conferida pelo verificador); Supl. Tab. 8")
C["mudare_neg_sorgo_para_milho_sorgo"]["condicoes"]["aridez"] = (
    "não estratificado por clima no artigo ('sorgo tolerante' é leitura do conselho)")
troca("mudare_sorgo_milho", "transfere_ne_motivo", "(vale o veto 'milho-sorgo no lugar de sorgo contínuo')",
      "(vale o alerta C 'milho-sorgo no lugar de sorgo contínuo')")
poe("mudare_sorgo_milho", "Item 13: o veto de sequência virou alerta C.")
troca("mudare_ganha_ganha", "efeito_texto", "(só na Fig. 3g, sem número no texto);",
      "(só na Fig. 3g, sem número no texto; na Source Data o sorgo-milho tem n=3 e as colunas n da aba parecem "
      "desalinhadas);")
poe("mudare_ganha_ganha", "Item 13: sorgo-milho com n=3.")

# Item 14-16: Franke (confirmados; ressalva do N)
troca("franke_dose_n_ciclo", "efeito_texto", "N × resposta p=0,204.",
      "N × resposta p=0,204 (as classes de N não diferem formalmente).")
poe("franke_dose_n_ciclo", "Itens 14–16: confirmados no XML; classes de N não diferem (p=0,204).")

# Item 17: Mudare 2022 (conferido agora)
poe("mudare22_milho_caupi",
    "Item 17: LER conferido (p.7, Fig. 3a); Tab. 1 é receita; retas da Fig. 5 não verificáveis; 'sequeiro' só do "
    "esquema da Fig. 1; 1,15 de Souza não é sequeiro.",
    efeito_texto=("LER 1,37 ± 0,03 (média ± EP; África; p.7, Fig. 3a); receita bruta 997 → 1.723 US$/ha (+73%; n=88; "
                  "P=0,004; Tab. 1); ganho absoluto só em figura. Sistema consorciado."),
    onde=("África (o 'sequeiro' vem só do esquema da Fig. 1, 'Rely on rainfall'; o artigo não estratifica o LER por "
          "chuva)"),
    moduladores=("O LER cai com o N e o ganho absoluto sobe com o P (direção no texto); as retas 'LER = 1,45 − 0,00126·N' "
                 "e 'efeito líquido = 1,23 + 0,0148·P' estão só na Fig. 5 (p.10): não verificado"),
    transfere_ne_motivo=("Teto; no NE não há LER de sequeiro medido (o 1,15 de Souza 2011 é com déficit após o "
                         "pendoamento, irrigado até 40 DAS); mostra que a S0 já capta ganho de terra"),
    fonte_pagina=("LER: p.7, Fig. 3a; receita: Tab. 1 (conferidos pelo verificador no PDF aberto da Springer, fora de "
                  "artigos/)"))
C["mudare22_milho_caupi"]["condicoes"]["aridez"] = "África; LER não estratificado por chuva"
poe("mudare22_milho_feijao", "Item 17: LER conferido.",
    fonte_pagina="p.7 Fig. 3a/3b (LER conferido pelo verificador); Tab. 1 (receita)")
poe("mudare22_milho_amendoim", "Item 17: LER e contradição 0,61 × 0,70 conferidos.",
    fonte_pagina="p.7 Fig. 3 (LER e contradição 0,61 × 0,70 conferidos pelo verificador); Tab. 1 (receita)")
troca("mudare22_milho_soja", "efeito_texto", "China: LER 1,38,", "China: LER 1,38 ± 0,03,")
poe("mudare22_milho_soja", "Item 17: LER conferido.",
    fonte_pagina="p.7 Fig. 3 (LER conferido pelo verificador); Tab. 1 (receita)")
troca("mudare22_arranjos", "efeito_texto", "efeito líquido = 1,23 + 0,0148·P. Sistema consorciado.",
      "o efeito líquido sobe com o P (a reta 1,23 + 0,0148·P está só na Fig. 5, p.10: não verificada no texto). "
      "Sistema consorciado.")
poe("mudare22_arranjos", "Item 17: arranjos conferidos (p.8); reta do P não verificável no texto.",
    onde="África (sequeiro não estratificado)",
    fonte_pagina="p.5; p.8 Fig. 4 (arranjos conferidos pelo verificador); p.10 Fig. 5")

# Item 18: Souza 2011 (L0 não é sequeiro)
poe("souza11_milho_caupi_laminas",
    "Item 18: L0 irrigada com 100% da ETo até 40 DAS (não é sequeiro); −66% do caupi não se reproduz; LER não cresce "
    "com a água.",
    efeito={"variavel": "LER com déficit após o pendoamento (L0; todas as lâminas irrigadas até 40 DAS)",
            "central": 1.152, "baixo": None, "alto": 1.372, "unidade": "LER", "na": "sistema_consorciado"},
    efeito_texto=("Milho −13% e caupi −66% contra o solteiro (p.719); o −12,7% do milho bate com as tabelas, o −66% do "
                  "caupi não (dá −57,8% pelas linhas ou −62,3% com a média impressa da Tab. 1, cuja linha de médias não "
                  "bate com as linhas). LER calculado por nós (Tab. 1–2, p.718): L125 1,372; L100 1,243; L75 1,328; L50 "
                  "1,294; L0 1,152, sem crescer com a água (L100 < L50); Ye +22% → +7%; EUA menor no consórcio. Sistema "
                  "consorciado."),
    onde=("Petrolina-PE, BSwh', 548,7 mm; 1 safra (2007/08), 3 repetições; todas as parcelas com 100% da ETo por "
          "gotejo até 40 DAS (pendoamento), lâminas diferentes só depois (p.716–717); na L0 o milho consorciado recebeu "
          "421,1 mm e o caupi 383,0 mm"),
    moduladores=("Água (o caupi é quem perde); o consórcio recebeu 58–62 mm a mais; caupi consorciado com metade da "
                 "densidade (40 mil contra 80 mil plantas/ha); 90 kg N/ha no milho"),
    transfere_ne_motivo=("1,15 com déficit após o pendoamento (L0, irrigado até 40 DAS); LER em sequeiro não medido; "
                         "recomendar caupi solteiro ou faixa larga em semeadura tardia"),
    fonte_pagina="Tab. 1–2 (p.718), p.716–717 (irrigação e lâminas), p.719 (conferido), Tab. 3 (p.720)")
C["souza11_milho_caupi_laminas"]["condicoes"]["aridez"] = "semiárido; todas as lâminas irrigadas até 40 DAS"
C["souza11_milho_caupi_laminas"]["condicoes"]["duracao"] = "1 safra (2007/08), 3 repetições"
troca("ne_s0_para_rotacao_tempo", "moduladores",
      "(LER do consórcio ~1,15 no sequeiro contra o rendimento solteiro de cada ano, preço local)",
      "(LER do consórcio contra o rendimento solteiro de cada ano, preço local; o 1,15 de Souza 2011 é com déficit após "
      "o pendoamento, irrigado até 40 DAS: LER em sequeiro não medido)")
poe("ne_s0_para_rotacao_tempo", "Item 18: o 1,15 deixou de ser chamado de sequeiro.")

# Item 19: Diniz 2017
troca("diniz_palma_sorgo_ler", "efeito_texto", "(Tab. 2). Sistema consorciado.",
      "(Tab. 2; a linha do sistema está rotulada 'Single crop', erro de diagramação). Sistema consorciado.")
poe("diniz_palma_sorgo_ler", "Item 19: 1,51 é média de 5 regimes; sem LER por lâmina.",
    moduladores=("O 1,51 é a média de 5 regimes de água (354,7 mm só de chuva a 1.012,2 mm com irrigação salina); os "
                 "autores dizem que a lâmina não afetou o LER (p.730), mas não publicam LER por lâmina; palma não "
                 "responde à água acima de ~355 mm"))

# Item 20: Martins 2015
poe("martins_gliricidia_forrageira", "Item 20: %Ndfa está na Tab. 1 (p.181); a Tab. 2 (p.182) traz o N fixado.",
    efeito_texto=("%Ndfa 52,35 (buffel) e 51,62 (palma), contra 0,0 ao lado do milho+caupi (Tab. 1, p.181); N fixado "
                  "nas pontas 43,2a e 39,3a kg/ha e na madeira 77,21a e 111,75a kg/ha (buffel e palma), contra 0,00b ao "
                  "lado do milho+caupi (Tab. 2, p.182). Serviço."),
    fonte_pagina="Tab. 1 p.181 (%Ndfa); Tab. 2 p.182 (N fixado)")

# ============================================================ B. colaterais
# B1: sorgo do Franke não está todo no Sahel
poe("franke_por_cereal",
    "B1: o sorgo vem sobretudo da Guiné; o sinal fraco é real, não só confundimento.",
    configuracao="Resposta por cereal na África (milho, milheto, sorgo): o sorgo responde pouco",
    moduladores=("Todo o milheto está na zona sudano-saheliana; o sorgo vem de várias zonas, sobretudo da Guiné (Tab. 1: "
                 "1 estudo do sul da África, 3 da Guiné, 3 da sudano-saheliana), e os autores leem o rendimento baixo "
                 "do sorgo como potencial menor (seção 3.1.2)"),
    transfere_ne_motivo=("O sinal fraco do sorgo na África é real, não só confundimento com a zona: no cartão NE o sorgo "
                         "usa a metade inferior da faixa até haver dado local (Zhao global +28,4%; base aberta "
                         "quente-seco +57,2%, 8 sítios, análise própria)"),
    fonte_pagina=("Tab. 3 linhas Maize, Millet, Sorghum (conferida); Tab. 1 e seção 3.1.2 (zonas do sorgo; conferidas "
                  "pelo verificador)"))
troca("franke_por_cereal", "efeito_texto", "sorgo +0,12 (EP 0,26; ns; n=25)",
      "sorgo +0,12 (EP 0,26; 1,06 → 1,18 t/ha, +11%; p=0,647; n=25)")
C["franke_por_cereal"]["condicoes"]["aridez"] = "milheto só na zona sudano-saheliana; sorgo em várias zonas, sobretudo Guiné"
troca("zhao_leg_sorgo", "moduladores", "o 'ns' do Franke é confundimento com a zona (p=0,435)",
      "no Franke o sorgo dá +0,12 t/ha (1,06 → 1,18, +11%, p=0,647, n=25), sobretudo da Guiné: sinal fraco real, não só "
      "confundimento (p=0,435 é a interação cereal × resposta)")
poe("zhao_leg_sorgo", "B1: ressalva do Franke ao sorgo; B3: média global (T1 → T2).",
    transferencia="T2", transfere_ne="parcial",
    transfere_ne_motivo=("Média global (T2: só direção); a resposta do sorgo na África é fraca (Franke +11% ns, n=25), "
                         "então no cartão NE o sorgo usa a metade inferior da faixa até haver dado local; atenção ao "
                         "portão de pragas (sorgo hospeda lagarta e alimenta o bicudo adulto)"))

# B2: cartão decisivo do NE
NE = "ne_lg_cereal_sequeiro_quente"
poe(NE, "B2: central e alto são síntese do conselho; âncoras verificáveis acrescentadas; ressalva do sorgo (B1).",
    efeito_texto=("+24% (central) com faixa +2% a +49%; só no ano colhido. Central e limite alto são SÍNTESE DO "
                  "CONSELHO, não número de artigo: o central é a mediana das estimativas dos votantes; o alto (+48,6%) é "
                  "a estimativa pontual da nossa análise da base aberta do Zhao (caupi→cereal, análogo amplo; IC próprio "
                  "32,4–75,1; 11 sítios); o baixo (+2%) é o limite inferior do IC do Mudare < 500 mm (cartão T2). A faixa "
                  "mistura bases (Zhao: antecessora não leguminosa; Mudare e Franke: monocultura). Âncoras verificáveis: "
                  "Franke Tab. 3, +24% relativo na zona sudano-saheliana (1,16 → 1,44 t/ha, ns) e na Guiné (2,14 → 2,66); "
                  "Mudare Source Data S5-S6, leguminosa < 500 mm +17% (+2 a +35) e leguminosa com MAT > 20 °C +22% (+5 a "
                  "+40; n=228); base aberta do Zhao no estrato AI 0,2–0,5 e MAT ≥ 20 °C +23,6% (49 sítios; análise "
                  "própria). Cultura seguinte."),
    fonte_pagina=("Mudare Source Data aba S5-S6 (MAP, Legume < 500; MAT, Legume > 20); Zhao base aberta (metodólogo A3; "
                  "análise própria); Franke Tab. 3 (Sudano-Sahelian zone e Guinea savannah)"),
    ancoras_verificaveis=[
        {"fonte": "Franke 2018, Tab. 3, Sudano-Sahelian zone", "t_ha": [1.16, 1.44], "pct": 24.1,
         "nota": "ns (p=0,138); base: cereal contínuo", "doi": "10.1016/j.agee.2017.09.029"},
        {"fonte": "Franke 2018, Tab. 3, Guinea savannah", "t_ha": [2.14, 2.66], "pct": 24.3,
         "nota": "p=0,015; base: cereal contínuo", "doi": "10.1016/j.agee.2017.09.029"},
        {"fonte": "Mudare 2025, Source Data aba Supplementary Figure S5-S6, MAP < 500 mm, Legume",
         "lnRR": [0.16, 0.02, 0.30], "pct": [17.4, 2.0, 35.0], "n": 129,
         "nota": "base: monocultura; classe de chuva anual (T2)", "doi": "10.1038/s41467-025-64567-9"},
        {"fonte": "Mudare 2025, Source Data aba Supplementary Figure S5-S6, MAT > 20 °C, Legume",
         "lnRR": [0.20, 0.05, 0.34], "pct": [22.1, 5.1, 40.5], "n": 228,
         "nota": "base: monocultura", "doi": "10.1038/s41467-025-64567-9"},
        {"fonte": "Zhao 2022, base aberta (figshare), estrato AI 0,2–0,5 e MAT ≥ 20 °C", "pct": 23.6, "n_sitios": 49,
         "nota": "análise própria do conselho, não número do artigo; base: antecessora não leguminosa",
         "doi": "10.6084/m9.figshare.20290923"}])
troca(NE, "moduladores", "N (descontar −6 a −7% por 50 kg N/ha);",
      "N (descontar −7% por 50 kg N/ha, Zhao Fig. 2c); sorgo com a ressalva do Franke (+0,12 t/ha, +11%, ns, n=25, "
      "sobretudo Guiné): sem dado local, metade inferior da faixa;")
C[NE]["efeito"]["origem"] = ("síntese do conselho: central = mediana dos votos; alto = estimativa pontual da base aberta do "
                             "Zhao (análise própria); baixo = limite inferior do IC do Mudare < 500 mm")

# B3: T1 não vale para média global ou continental
B3 = {
    "zhao_leg_global": ("Direção transfere; é média global (inclui climas frios e úmidos: T2), e o número do semiárido vem "
                        "do cartão ne_lg_cereal_sequeiro_quente (análogo da base aberta: previsto +23,5% contra +23,6% "
                        "observado); só contra base sem leguminosa e no ano colhido"),
    "franke_global": ("Melhor análogo de sistema, mas é média da África Subsaariana (inclui planaltos frios do leste e "
                      "floresta úmida acima de 1.200 mm: T2); o número por estrato vem das zonas (franke_sahel, "
                      "franke_guine, franke_austral); aplicar o %, não as t/ha (controle africano ≈ 2× o milho do sertão)"),
    "zhao_leg_milho": ("Média global (T2: só direção; o número vem do cartão NE); contra milho solteiro; milho do "
                       "semiárido rende ~0,55–0,59 t/ha: aplicar em lnRR"),
    "zhao_caupi": ("É a leguminosa do sertão; média global (T2), então o número vem do cartão NE; faixa comum, sem prêmio "
                   "de espécie"),
    "zhao_amendoim": "Média global (T2); amendoim é pouco plantado no CE; sem prêmio de espécie",
    "franke_caupi_cereal": ("Mesma espécie, mas média da África Subsaariana inteira (inclui planaltos e zonas úmidas: T2); "
                            "o relativo (+33%) serve de âncora, não as t/ha"),
    "franke_amendoim_cereal": "Média da África Subsaariana (T2); faixa comum, sem ranking",
}
for cid, motivo in B3.items():
    assert C[cid]["transferencia"] == "T1", cid
    nota = ("B3: média global ou continental (T1 → T2)." if cid in ("zhao_leg_global", "franke_global")
            else "B3 (extensão do integrador, mesma definição): média global ou continental (T1 → T2).")
    poe(cid, nota, transferencia="T2", transfere_ne_motivo=motivo)

# B5: composição da mistura
poe("mudare_mistura_forrageira", "B5: composição gramínea + leguminosa não está no texto (Mixture = grupos funcionais "
    "diferentes, p.2).",
    configuracao="Mistura de espécies de grupos funcionais diferentes (e leguminosa forrageira) antes do cereal",
    culturas="mistura de espécies → cereal; leguminosa forrageira → cereal",
    onde="Global (sobretudo trigo; 'ley' não verificado)")
C["mudare_mistura_forrageira"]["efeito_texto"] = (
    "O artigo define 'Mixture' só como 'species belonging to different functional groups' (p.2): a composição gramínea + "
    "leguminosa forrageira NÃO foi verificada. " + C["mudare_mistura_forrageira"]["efeito_texto"])

# ------------------------------------------------------------- notas e re-renderização das linhas
for cid, nota in NOTAS.items():
    C[cid]["verificacao_adversaria"] = nota
    LINHAS[IDX[cid]] = linha(C[cid])
md = "\n".join(LINHAS)

# ============================================================ texto fora das tabelas de cartões
troca_md("artigo, na Source Data ou no XML (`conselho/analises/v4_integrador_catalogo_conferencias.py` e `.saida.txt`).\n",
         "artigo, na Source Data ou no XML (`conselho/analises/v4_integrador_catalogo_conferencias.py` e `.saida.txt`).\n"
         f"Em {HOJE}, o integrador aplicou a conferência do verificador adversário com `{SCRIPT}`\n"
         "(seção \"Verificação adversária\", no fim). Regerar o catálogo pelo script de dados desfaz essas correções; nesse\n"
         "caso, rode o script de correção logo depois.\n")
troca_md("  T1 = análogo medido no estrato de aridez 0,2–0,5 e MAT ≥ 20 °C com ≥ 5 sítios; T2 = só a direção; T3 = não transfere.",
         "  T1 = análogo medido no estrato de aridez 0,2–0,5 e MAT ≥ 20 °C com ≥ 5 sítios (vale para o número do estrato;\n"
         "  média global ou continental é T2); T2 = só a direção; T3 = não transfere.")

# resumo NE
troca_md("| +24% no ano colhido (faixa +2% a +49%); ano seco alarga até 0 | B·T1 |",
         "| +24% no ano colhido (síntese do conselho; faixa +2% a +49%); âncoras de artigo: Franke +24% (Sahel e Guiné), "
         "Mudare MAT > 20 °C +22% (+5 a +40); ano seco alarga até 0 | B·T1 |")
troca_md("| CE 18,8%; NE 21,0% (2000–2024) | D (nossos dados) |",
         "| CE 20,2%; NE 21,0% (2000–2024, mediana municipal da mesma janela; com a mediana de 1988–2025 o CE dá 18,8%) "
         "| D (nossos dados) |")
troca_md("| LER 1,37 com água; 1,15 no cenário seco | B / C |",
         "| LER 1,37 (África, Mudare 2022); 1,15 com déficit após o pendoamento (Souza 2011, L0, irrigado até 40 DAS); "
         "LER em sequeiro não medido | B / C |")
troca_md("| Trocar o sorgo tolerante por milho na sequência | `mudare_neg_sorgo_para_milho_sorgo` | veto (−32% de "
         "rendimento na sequência) | B |",
         "| Trocar sorgo contínuo por milho-sorgo na sequência | `mudare_neg_sorgo_para_milho_sorgo` | alerta de direção, "
         "não veto numérico: −32% de rendimento na sequência (texto p.4, sem IC); Source Data: energia −32,1% (−45,5 a "
         "−15,4), receita −31,1% (−44,4 a −14,5), n=10 | C |")
troca_md("| −6 a −7% por 50 kg N/ha; nulo > 236 kg | A |",
         "| −7% por 50 kg N/ha (Zhao p.2, Fig. 2c; o −6% é análise própria da base aberta); nulo > 236 kg (p.3, Fig. 3a) "
         "| A |")

# regras de generalização
troca_md("em 18,8% dos município-anos de milho no CE e 21,0% no NE (2000–2024); a\n   definição",
         "em 20,2% dos município-anos de milho no CE e 21,0% no NE (2000–2024, mediana da mesma janela; o CE dá\n"
         "   18,8% com a mediana de 1988–2025); a definição")
troca_md("*Evidência:* Zhao Fig. 4a (+32% contra +7%);",
         "*Evidência:* Zhao, resumo p.1 (+32% contra +7%, sem IC; a Fig. 4a e a p.4 dão só a direção);")
troca_md("4. **G04 — Desconto por N.** −6 a −7% por 50 kg N/ha (Zhao Fig. 2c; base aberta −0,061 lnRR, sem interação seco × N,\n"
         "   p=0,87); em sequeiro com N ≤ 50 a inclinação é mais forte (−17 a −19%); nulo acima de 236 kg N/ha (p.3). No sertão",
         "4. **G04 — Desconto por N.** −7% por 50 kg N/ha (Zhao p.2, Fig. 2c; −7,9% com diversidade 1 e −3,2% com diversidade\n"
         "   alta, Fig. 3a); nulo acima de 236 kg N/ha (p.3, modelo N × diversidade da Fig. 3a). Análise própria da base aberta,\n"
         "   não do artigo: −0,061 lnRR (≈ −6%) por 50 kg, sem interação seco × N (p=0,87), e −17 a −19% em sequeiro com\n"
         "   N ≤ 50. No sertão")
troca_md("8. **G08 — Sem ranking de leguminosa de grão; sorgo responde.**",
         "8. **G08 — Sem ranking de leguminosa de grão; sorgo responde, com ressalva.**")
troca_md("sorgo quente-seco +57,2% (8 sítios).",
         "sorgo quente-seco +57,2% (8 sítios). Ressalva\n"
         "   (verificação adversária, B1): no Franke o sorgo dá +11% ns (n=25), sobretudo na Guiné, e isso não é só\n"
         "   confundimento com a zona; sem dado local, o sorgo usa a metade inferior da faixa do cartão NE.")
troca_md("Mudare p.4 (soja-milho no lugar de milho contínuo: receita −50%;\n   milho-sorgo no lugar de sorgo: rendimento −32%)",
         "Mudare (soja-milho no lugar de milho contínuo: receita −53,1%, IC −56,6 a −49,3, Source Data aba\n"
         "   Figure 3e; o −50% do texto p.4 junta soja-milho e soja-sorgo; milho-sorgo no lugar de sorgo: rendimento −32%,\n"
         "   p.4, grau C com n=10)")
troca_md("16. **G16 — LER e Kc por par.** Milho+caupi: LER dependente da água (1,37 → 1,15 da lâmina 125% à 0; prior africano\n"
         "    1,37) e ET maior no consórcio (Souza 2015). Palma+sorgo: LER estável de 355 a 1.012 mm (Diniz p.730) e ET inalterada\n"
         "    (Lima 2018b).",
         "16. **G16 — LER e Kc por par.** Milho+caupi: LER de 1,37 (L125) a 1,15 (L0, déficit só após o pendoamento, irrigado\n"
         "    até 40 DAS), sem tendência com a água (L100 1,24 < L50 1,29); prior africano 1,37; LER em sequeiro não medido; ET\n"
         "    maior no consórcio (Souza 2015). Palma+sorgo: LER 1,51 como média de 355 a 1.012 mm, sem efeito da lâmina segundo\n"
         "    os autores (Diniz p.730; não há LER por lâmina), e ET inalterada (Lima 2018b).")
troca_md("- \"Amendoim > caupi\" e \"o sorgo responde pouco\" (leitura do Franke pelo metodólogo, que a retirou).",
         "- \"Amendoim > caupi\" e \"o sorgo responde pouco\" (leitura do Franke pelo metodólogo, que a retirou). A verificação\n"
         "  adversária (B1) reabriu a parte do sorgo: o sinal fraco do sorgo no Franke não é só confundimento com a zona (G08).")

# conflitos
troca_md("a +49% (Zhao, caupi→cereal no análogo amplo), grau B·T1, só contra cereal solteiro e no ano colhido.",
         "a +49% (estimativa pontual da nossa análise da base aberta do Zhao, caupi→cereal no análogo amplo),\n"
         "   grau B·T1, só contra cereal solteiro e no ano colhido. Central e alto são síntese do conselho; as âncoras de\n"
         "   artigo (Franke +24% no Sahel e na Guiné; Mudare MAT > 20 °C +22%) concordam com o central (verificação\n"
         "   adversária, B2).")
troca_md("5. **O sorgo responde?** Franke (+0,12 t/ha ns) contra Zhao (+28,4%) e base aberta (+57,2%): responde como o milho; no\n"
         "   Franke o cereal está confundido com a zona (p=0,435, conferido).",
         "5. **O sorgo responde?** Franke (+0,12 t/ha ns) contra Zhao (+28,4%) e base aberta (+57,2%). Resolução original:\n"
         "   \"responde como o milho; no Franke o cereal está confundido com a zona\". *Corrigido pela verificação adversária\n"
         "   (B1):* p=0,435 é a interação cereal × resposta, e o sorgo do Franke vem sobretudo da Guiné (+11%, p=0,647, n=25);\n"
         "   o sinal fraco é real. O sorgo fica no cartão NE com a metade inferior da faixa até haver dado local.")
troca_md("13. **LER do consórcio milho+caupi em sequeiro** (teto 1,15 do agroecólogo contra 1,37 do Mudare 2022): prior 1,37\n"
         "    modulado pela água; 1,15 como cenário seco; o agroecólogo retirou o \"teto universal\".",
         "13. **LER do consórcio milho+caupi em sequeiro** (teto 1,15 do agroecólogo contra 1,37 do Mudare 2022): prior 1,37; o\n"
         "    agroecólogo retirou o \"teto universal\". *Corrigido pela verificação adversária (item 18):* o 1,15 é a L0 de\n"
         "    Souza 2011, irrigada com 100% da ETo até 40 DAS (déficit só após o pendoamento), e não um cenário de sequeiro;\n"
         "    LER em sequeiro não medido.")
troca_md("\"rendimento por ha plantado < 0,5 da mediana municipal\": CE 18,8% e NE 21,0% (2000–2024); CE 22,7% (1988–2025).",
         "\"rendimento por ha plantado < 0,5 da mediana municipal\": CE 20,2% e NE 21,0% (2000–2024, mediana da mesma\n"
         "    janela; o CE dá 18,8% com a mediana de 1988–2025); CE 22,7% (1988–2025).")

# dados e lacunas
troca_md("municipal: CE 18,8% (2000–2024) e 22,7% (1988–2025); NE 21,0%.",
         "municipal: CE 20,2% (2000–2024, mediana da mesma janela; 18,8% com a mediana de 1988–2025) e 22,7% (1988–2025);\n"
         "NE 21,0% (2000–2024).")
troca_md("10. **Mudare 2022:** o PDF não está em `artigos/` (ficou num scratchpad que é apagado); os LER não foram reconferidos\n"
         "    nesta rodada.",
         "10. **Mudare 2022:** o PDF não está em `artigos/`. O verificador adversário conferiu os LER no PDF aberto da Springer\n"
         "    (pasta isolada do scratchpad, que é apagado); as retas da Fig. 5 (LER × N, efeito líquido × P) não são\n"
         "    verificáveis no texto, e o artigo não estratifica o LER por chuva.")
troca_md("Souza 2011 (1.655,0 × 1.663,33; unidade da EUA);",
         "Souza 2011 (1.655,0 × 1.663,33; unidade da EUA; caupi −66% do texto × −57,8% das linhas; linha de médias da\n"
         "    Tab. 1 × linhas);")
troca_md("Mudare 2025 (lnCV p.2 × p.9; '16%' da África);",
         "Mudare 2025 (lnCV p.2 × p.9; '16%' da África; colunas n da aba Figure 3e);")

# ============================================================ JSON: topo, convenções, parâmetros e regras
fq = cat["parametros_ne"]["freq_quebra_milho"]
assert fq["CE_2000_2024"] == 0.188
cat["parametros_ne"]["freq_quebra_milho"] = {
    "definicao": fq["definicao"],
    "CE_2000_2024": 0.202,
    "CE_2000_2024_mediana_1988_2025": 0.188,
    "CE_1988_2025": fq["CE_1988_2025"],
    "NE_2000_2024": fq["NE_2000_2024"],
    "janela_da_mediana": ("CE_2000_2024 e NE_2000_2024 usam a mediana municipal de 2000–2024 (mesma janela); o 0,188 usava "
                          "a mediana de 1988–2025 (e punha 'Milho verde', só 2025, na mesma mediana)"),
    "fonte": fq["fonte"] + "; v4_verificador_catalogo_conferencias.saida.txt (bloco C)",
    "grau": fq["grau"],
}
ler = cat["parametros_ne"]["ler_consorcio_milho_caupi"]
assert ler["sequeiro_ano_seco"] == 1.15
cat["parametros_ne"]["ler_consorcio_milho_caupi"] = {
    "deficit_pos_pendoamento_L0": 1.152,
    "sequeiro": None,
    "teto_com_agua": ler["teto_com_agua"],
    "nota": ("Souza 2011: todas as lâminas com 100% da ETo por gotejo até 40 DAS; na L0 o milho consorciado recebeu "
             "421,1 mm e o caupi 383,0 mm; LER em sequeiro não medido. O 1,37 é o Mudare 2022 (África, p.7, Fig. 3a), "
             "sem estratificação por chuva"),
    "fonte": "Souza 2011 (Tab. 1-2, LER calculado; p.716-717); Mudare 2022 (p.7, Fig. 3a)",
}
cat["convencoes"]["transferencia"]["T1"] = ("analogo AI 0,2-0,5 e MAT >= 20 C com >= 5 sitios (so o numero do estrato; "
                                            "media global ou continental = T2)")
REG = {r["id"]: r for r in cat["regras_motor"]}
assert "(18,8% CE, 21,0% NE)" in REG["G01"]["regra"]
REG["G01"]["regra"] = REG["G01"]["regra"].replace("(18,8% CE, 21,0% NE)", "(20,2% CE e 21,0% NE, 2000–2024)")
REG["G04"]["regra"] = ("Descontar N: −7% por 50 kg N/ha (Zhao p.2, Fig. 2c); nulo acima de ~236 kg (p.3, Fig. 3a); o −6% "
                       "e o −17 a −19% do sequeiro com N baixo são análise própria da base aberta; no sertão N ≈ 0.")
assert REG["G08"]["regra"].endswith("o sorgo responde como o milho.")
REG["G08"]["regra"] = REG["G08"]["regra"].replace(
    "o sorgo responde como o milho.",
    "o sorgo responde (Zhao), mas fraco na África (Franke +11% ns, n=25): sem dado local, metade inferior da faixa.")

DEPOIS = {k: Counter(c[k] for c in cat["configuracoes"]) for k in ("tipo", "grau", "transferencia")}
cat_novo = {}
for k, v in cat.items():
    cat_novo[k] = v
    if k == "gerado_em":
        cat_novo["corrigido_em"] = HOJE
        cat_novo["correcao"] = SCRIPT + " (conferência: conselho/analises/v4_verificador_catalogo_conferencias.py)"
cat_novo["versao"] = "v4-integrador + verificacao adversaria"
cat_novo["verificacao_adversaria"] = {
    "placar_20_numeros": {"confirmados_sem_ressalva": 13, "com_correcao": 7, "itens_corrigidos": [3, 5, 9, 13, 17, 18, 20]},
    "colaterais": 6,
    "cartoes_alterados": sorted(NOTAS),
    "T1_para_T2": sorted([cid for cid in B3] + ["zhao_leg_sorgo", "mudare_classes_chuva"]),
    "grau_rebaixado": {"mod_produtividade": "A -> C (direção A)", "mudare_neg_sorgo_para_milho_sorgo": "B -> C"},
    "nao_conferidos": ["painel IBGE x IMERG; espaço x tempo; cobertura tira 40% da chuva do milho (análises próprias)",
                       "números da base aberta do Zhao (+9,4%, +23,6%, +39,6%, +48,6%, +57,2%): análise própria"],
    "contagens_antes": {k: dict(v) for k, v in ANTES.items()},
    "contagens_depois": {k: dict(v) for k, v in DEPOIS.items()},
}

# ============================================================ seção "Verificação adversária"
def cont(c):
    return ", ".join(f"{k} {c[k]}" for k in sorted(c))


TAB = "\n".join(f"| `{cid}` | {cel(NOTAS[cid])} |" for cid in sorted(NOTAS))
SEC = f"""
{SECAO}

Feita por um verificador independente depois da geração (`conselho/analises/v4_verificador_catalogo_conferencias.py`,
saída `.saida.txt`) e aplicada pelo integrador em {HOJE} com `{SCRIPT}`. Fontes: texto completo dos PDFs de `artigos/`
(pypdf), Source Data e suplemento do Mudare 2025, XML do Franke 2018 e o PDF aberto do Mudare 2022 (Springer, baixado
numa pasta isolada do scratchpad, fora de `artigos/`). Além deste .md e do JSON, nenhum arquivo existente foi alterado.

**Placar.** Dos 20 números que mais pesam no motor, 13 foram confirmados sem ressalva e 7 precisaram de correção
(itens 3, 5, 9, 13, 17, 18 e 20); houve mais 6 correções colaterais (B1 a B6). Nenhum efeito de consórcio estava rotulado
como rotação, e nenhum efeito da cultura seguinte estava rotulado como sequência inteira. O único erro de rotulagem foi
"sequeiro" num tratamento irrigado (item 18).

### Os 20 números

| Item | Resultado | O que mudou no catálogo |
|---|---|---|
| 1. Zhao +20,4% (17,7–23,1) | Confirmado (p.2, Fig. 2a; mediana 10,2%; 11.768 obs., 462 estudos; inclui forrageiras e adubo verde) | Nada no número; T1 → T2 (B3) |
| 2. Exclusão do rendimento zero | Confirmado (p.7) | Nada |
| 3. N: −7% por 50 kg e nulo > 236 kg | Confirmado com ajuste de citação: −7% na p.2/Fig. 2c; 236 kg na p.3, do modelo N × diversidade da Fig. 3a; −7,9% (diversidade 1) e −3,2% (alta) na Fig. 3a | `mod_n_fertilizante`, G04 e resumo NE: o −6% e o −17 a −19% do sequeiro passam a "análise própria da base aberta" |
| 4. Leguminosa → milho +28,9% | Confirmado (p.5) | Nada no número; T1 → T2 (B3) |
| 5. +32% contra +7% | Número só no resumo (p.1), sem IC; Fig. 4a é loess sem esses números; p.4 dá a direção; baixa/alta = abaixo/acima da média do banco (entre estudos) | `mod_produtividade`: A → C no número, direção A; G02 |
| 6. Leguminosa → algodão −1,3% | Confirmado (p.5) | Nada |
| 7. Mudare 2025 leguminosa +23% × não leguminosa +16% | Confirmado (p.2; Source Data Figure 1e: 0,209, n=1.726; 0,148, n=953) | Nada |
| 8. Caupi → milho +14,68% | Confirmado (Supl. Tab. 5, p.23) | Nada |
| 9. Mudare < 500 mm | Números confirmados; classe de chuva anual inclui terras secas frias; 626 de 1.726 obs. de leguminosa | `mudare_classes_chuva` B·T1 → B·T2; acrescentado o análogo quente (leguminosa com MAT > 20 °C +22%, +5 a +40, n=228) |
| 10. Pousio → milho +31,02% | Confirmado (Supl. Tab. 5, p.24); exclusão da sequência inteira (p.8) | Nada |
| 11. Crotalária e mucuna → milho | Confirmados (Supl. Tab. 5, p.23); conflito não registrado: Zhao mucuna → milho +78% (59,1–99,4) | Conflito mostrado em `mudare_crotalaria_mucuna_milho` e `zhao_adubo_verde_milho` |
| 12. Mudare na África | Confirmado; o "16% (10–22%)" é a leguminosa na América do Norte | `mudare_africa_leg_naoleg`: o ns da não leguminosa é imprecisão (n=36, IC −17% a +26%) |
| 13. Cartões negativos de sequência | Receita soja-milho −53,1% (−56,6 a −49,3), não −50%; soja-sorgo −47,1%; 73,8% só no cenário rendimento-receita-energia; milho-sorgo n=10; colunas n da aba Figure 3e desalinhadas | JSON com os dois lnRR e IC; `mudare_neg_sorgo_para_milho_sorgo` B → C com IC de energia e receita; veto vira alerta; G09 e resumo NE |
| 14–16. Franke 2018 | Confirmados no XML (Tab. 3); interação N × resposta p=0,204 | Ressalva em `franke_dose_n_ciclo` |
| 17. Mudare 2022, LER milho/caupi | Conferido agora: 1,37 ± 0,03 (p.7, Fig. 3a); a Tab. 1 é receita (n=88, +73%, P=0,004); demais LER e arranjos confirmados; retas da Fig. 5 não verificáveis no texto; "sequeiro" só do esquema da Fig. 1 | Cartões `mudare22_*` e lacuna 10 |
| 18. Souza 2011 | Texto e LER confirmados; a L0 não é sequeiro (100% da ETo por gotejo até 40 DAS; 421,1 e 383,0 mm; 90 kg N) | "Cenário seco" e "teto do sequeiro" trocados nos 5 lugares (resumo NE, `souza11_milho_caupi_laminas`, `mudare22_milho_caupi`, `ne_s0_para_rotacao_tempo`, JSON `parametros_ne`), em G16 e no conflito 13; −66% do caupi não se reproduz (−57,8% ou −62,3%) |
| 19. Diniz 2017 | Confirmado (Tab. 3, p.731; Tab. 2, p.728) | 1,51 = média de 5 regimes (354,7 a 1.012,2 mm), sem LER por lâmina; linha "Single crop" |
| 20. Martins 2015 | Caupi 36a × 410a confirmado; o %Ndfa está na Tab. 1 (p.181), não na Tab. 2 | `martins_gliricidia_forrageira`: fonte e números do N fixado (Tab. 2, p.182) |

### Correções colaterais

- **B1. Sorgo do Franke.** Só o milheto está todo na zona sudano-saheliana; o sorgo vem de várias zonas, sobretudo da
  Guiné (Tab. 1), e dá +0,12 t/ha (1,06 → 1,18, +11%, p=0,647, n=25). O p=0,435 é a interação cereal × resposta. O sinal
  fraco do sorgo na África é real. Decisão do integrador: sem dado local, o sorgo usa a metade inferior da faixa do
  cartão NE (`franke_por_cereal`, `zhao_leg_sorgo`, `ne_lg_cereal_sequeiro_quente`, G08, conflito 5, regras rejeitadas).
- **B2. Cartão decisivo do NE.** O +24% central é a mediana dos votos e o +49% é a estimativa pontual da nossa análise
  da base aberta: os dois agora estão marcados como síntese do conselho. A faixa mistura bases (Zhao contra antecessora
  não leguminosa; Mudare e Franke contra monocultura). As âncoras verificáveis concordam com o central: Franke +24% (Sahel
  e Guiné), Mudare leguminosa < 500 mm +17% (+2 a +35) e com MAT > 20 °C +22% (+5 a +40). O JSON traz essas âncoras em
  `ancoras_verificaveis`.
- **B3. T1 em médias globais.** Pela definição do catálogo, T1 vale para o número do estrato. Passaram para T2 os
  cartões apontados pelo verificador (`zhao_leg_global`, `franke_global`) e, pela mesma definição, outros seis cartões
  de média global ou continental (`zhao_leg_milho`, `zhao_leg_sorgo`, `zhao_caupi`, `zhao_amendoim`,
  `franke_caupi_cereal`, `franke_amendoim_cereal`). Essa extensão foi decisão do integrador. Continuam em T1 os cartões
  de estrato (`ne_lg_cereal_sequeiro_quente`, `franke_sahel`, `franke_guine`, `franke_austral`) e as regras de
  inclinação ou igualdade (`mod_n_fertilizante`, `mod_aridez_relativo`, `franke_dose_n_ciclo`). Com isso, no NE nenhuma
  média global entra como número, só como direção. A convenção T1 foi reescrita em "Como ler" e no JSON.
- **B4. Quebra do milho.** Na mesma janela do NE (mediana municipal de 2000–2024), o CE dá 20,2%, contra 21,0% no NE. O
  18,8% usava a mediana de 1988–2025 e punha "Milho verde" (só 2025) na mesma mediana. Corrigido no resumo NE, em G01,
  no conflito 15, no bloco 3 dos dados e no JSON (`parametros_ne.freq_quebra_milho`, regra G01).
- **B5. Mistura do Mudare.** O artigo define "Mixture" só como "species belonging to different functional groups" (p.2).
  A composição gramínea + leguminosa forrageira foi marcada como não verificada.
- **B6. Bowles, Renwick e a Eq. 1 do Zhao.** Confirmados. Nada mudou.

### Cartões alterados ({len(NOTAS)})

| Cartão | Correção |
|---|---|
{TAB}

### Contagens

- Antes: grau {cont(ANTES['grau'])}; transferência {cont(ANTES['transferencia'])}.
- Depois: grau {cont(DEPOIS['grau'])}; transferência {cont(DEPOIS['transferencia'])}.
- Por tipo (sem mudança, {sum(DEPOIS['tipo'].values())} configurações): {cont(DEPOIS['tipo'])}.

### Não conferido nesta verificação

- As análises próprias do painel IBGE × IMERG, de espaço contra tempo e de quanto a cobertura tira da chuva do milho
  (40%) não foram refeitas.
- Os números da base aberta do Zhao (+9,4%, +23,6%, +39,6%, +48,6% e +57,2%) continuam como análise própria do
  conselho. Não são números do artigo.
"""
md = md.rstrip("\n") + "\n" + SEC

# ============================================================ gravar e conferir
MD.write_text(md, encoding="utf-8")
JS.write_text(json.dumps(cat_novo, ensure_ascii=False, indent=1), encoding="utf-8")
j = json.loads(JS.read_text(encoding="utf-8"))
m = MD.read_text(encoding="utf-8")
assert len(j["configuracoes"]) == len(C)
for c in j["configuracoes"]:
    assert linha(c) in m, f"linha do .md não bate com o JSON: {c['id']}"
corpo = m.split(SECAO)[0].lower()  # a própria seção cita os termos trocados
for velho in ("cenário seco", "teto do sequeiro", "no sequeiro usar 1,15", "~1,15 no sequeiro",
              "todo o milheto e o sorgo", "−6 a −7%", "sequeiro_ano_seco", "só prova de confundimento"):
    assert velho not in corpo, velho
    assert velho not in JS.read_text(encoding="utf-8").lower(), velho
print(f"cartões alterados: {len(NOTAS)}")
for k in ("grau", "transferencia", "tipo"):
    print(f"  {k}: antes {dict(ANTES[k])} | depois {dict(DEPOIS[k])}")
print(f"MD bytes: {MD.stat().st_size} | JSON bytes: {JS.stat().st_size}")
