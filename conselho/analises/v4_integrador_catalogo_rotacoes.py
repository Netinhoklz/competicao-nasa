"""Integrador (v4): gera pesquisa/catalogo_rotacoes_comprovadas.md e pesquisa/catalogo_rotacoes.json
a partir de v4_integrador_catalogo_dados.py (fonte unica). Nao altera nenhum arquivo existente.
"""
import json
import math
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import v4_integrador_catalogo_dados as D  # noqa: E402

RAIZ = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa")
MD = RAIZ / "pesquisa" / "catalogo_rotacoes_comprovadas.md"
JS = RAIZ / "pesquisa" / "catalogo_rotacoes.json"
MARCA = "v4_integrador_catalogo_dados.py"
for alvo in (MD, JS):
    if alvo.exists() and MARCA not in alvo.read_text(encoding="utf-8")[:2000]:
        raise SystemExit(f"{alvo} existe e nao foi gerado por este script: nao sobrescrever")

HOJE = datetime.now().strftime("%Y-%m-%d %H:%M")


def lnrr(p):
    if p is None:
        return None
    return round(math.log(1 + p / 100.0), 4)


def efeito_json(ef):
    var, c, lo, hi, un, na = ef
    if un == "%":
        return {"variavel": var, "central": lnrr(c), "baixo": lnrr(lo), "alto": lnrr(hi),
                "unidade": "lnRR", "na": na, "pct": [c, lo, hi]}
    return {"variavel": var, "central": c, "baixo": lo, "alto": hi, "unidade": un, "na": na}


def cel(s):
    return str(s).replace("|", "/").replace("\n", " ")


NE_TXT = {"sim": "Sim", "parcial": "Parcial", "nao": "Não"}
TITULOS = {
    1: "Tabela 1 — Rotação e sucessão no tempo",
    2: "Tabela 2 — Plantas de cobertura e adubo verde",
    3: "Tabela 3 — Consórcio no espaço",
    4: "Tabela 4 — Agrofloresta, silvipastoril e ILP",
    5: "Tabela 5 — Quebra de praga",
    6: "Tabela 6 — Moduladores e sínteses (regras do motor, não cartões de par)",
}
CAB = ("| Configuração (base de comparação) | Culturas | Efeito (valor, intervalo; escopo) | Onde e clima | Condições que modulam "
       "| Grau final | Transfere para o semiárido | Transfere global | Referência | DOI e página/tabela |\n"
       "|---|---|---|---|---|---|---|---|---|---|\n")


def tabela(t):
    linhas = [f"\n### {TITULOS[t]}\n\n", CAB]
    for k in [c for c in D.C if c["t"] == t]:
        dois = "; ".join(k["doi"]) if k["doi"] else "DOI não verificado"
        linhas.append("| " + " | ".join(cel(x) for x in [
            f"**{k['nome']}** (base: {k['base']}) `{k['id']}`",
            k["cult"], k["ef_md"], k["onde"], k["mod"],
            f"{k['g']}·{k['T']}",
            f"{NE_TXT[k['ne']]}: {k['ne_md']}",
            k["gl"], k["ref"], f"{dois} — {k['pg']}"]) + " |\n")
    return "".join(linhas)


# ------------------------------------------------------------------ texto
INTRO = f"""# Catálogo de rotações comprovadas (QUADRA)

Gerado em {HOJE} pelo integrador do conselho de 10 agentes (rodada R1 de extração e R2 de votos), a partir de
`conselho/analises/v4_integrador_catalogo_dados.py` (fonte única do .md e do `catalogo_rotacoes.json`).
Entram só configurações com voto majoritário "incluir" ou "incluir_com_ressalva" na R2; duplicatas entre especialistas
foram fundidas num cartão canônico. Onde os especialistas divergiram num número, o integrador conferiu no texto do
artigo, na Source Data ou no XML (`conselho/analises/v4_integrador_catalogo_conferencias.py` e `.saida.txt`).

## Como ler

- **Escopo do efeito.** Toda célula de efeito diz se é na **cultura seguinte** (o ano depois da antecessora), na
  **sequência inteira** (soma dos anos, com o ano da antecessora), no **sistema consorciado** (as duas culturas no mesmo
  espaço e estação), em **solo ou serviço**, ou em **praga**. Cultura seguinte e sequência inteira nunca se somam.
- **Tempo × espaço.** Rotação e sucessão são no tempo (Tabela 1); consórcio é no espaço (Tabela 3). O consórcio
  milho+feijão do sertão (S0) é a base real do Nordeste: os priors de "leguminosa antecessora" foram medidos contra base
  SEM leguminosa e não se aplicam contra a S0 (cartão `ne_s0_para_rotacao_tempo`, grau D).
- **Grau (força da evidência no domínio em que foi medida), escala única adotada pelo conselho:**
  A = meta-análise com IC, ≥ 20 estudos, verificada no texto e replicada em direção por fonte independente;
  B = meta-análise ou subgrupo com IC de um só artigo (10–20 estudos ou n de 25 a 300), desenho causal observacional
  grande, ou rede multi-sítio de longo prazo; C = um sítio ou 1–2 anos (mesmo ensaio longo de um sítio), < 10 estudos,
  valor só de figura, sem IC, citação secundária; D = não significativo vendido como efeito, só resumo, sem estatística,
  simulação, correlação ecológica ou proxy dos nossos dados.
- **Transferência (eixo separado do grau):** T0 = medido no semiárido brasileiro (a condição de água vai no texto);
  T1 = análogo medido no estrato de aridez 0,2–0,5 e MAT ≥ 20 °C com ≥ 5 sítios; T2 = só a direção; T3 = não transfere.
  O motor usa número só com T0 ou T1; com T2, só a direção.
- **Unidade no motor.** Efeitos em % viram lnRR = ln(1 + p/100) no JSON (campo `pct` guarda o original). Converter
  para kg/ha só na tela, sobre a distribuição local dos anos colhidos.
- O CE tem índice de aridez mediano 0,34 (POWER 1991–2020; p10 0,28, p90 0,49): é semiárido quente. O milho do
  semiárido NE rende ~0,55–0,59 t/ha nos anos colhidos (PAM).
- Intervalos em t/ha e LER marcados "aprox." ou "calculado" são ±1,96·EP feitos pelo conselho quando o artigo publica só o EP.

## O que o motor usa no Nordeste (resumo dos cartões decisivos)

| Decisão no talhão | Cartão | Número para o motor | Grau |
|---|---|---|---|
| Caupi (ou outra leguminosa de grão) antes de milho/sorgo **solteiro**, sequeiro, N ≈ 0 | `ne_lg_cereal_sequeiro_quente` | +24% no ano colhido (faixa +2% a +49%); ano seco alarga até 0 | B·T1 |
| Sair do consórcio milho+feijão (S0) para rotação no tempo | `ne_s0_para_rotacao_tempo` | não medido: central 0, sensibilidade 0 a +9% | D·T3 |
| Chance de quebra do milho (o bônus não vale nesse ano) | `parametros_ne.freq_quebra_milho` | CE 18,8%; NE 21,0% (2000–2024) | D (nossos dados) |
| Consórcio milho+caupi (ganho de terra, não de água) | `mudare22_milho_caupi`, `souza11_milho_caupi_laminas` | LER 1,37 com água; 1,15 no cenário seco | B / C |
| Quebra sem leguminosa (estratégia comparável obrigatória) | `mudare_pousio_milho`, `mudare_sorgo_milho` | pousio→milho +31%; sorgo→milho +28% (ano sem grão e veto de praga na sequência) | C·T2 |
| Trocar o sorgo tolerante por milho na sequência | `mudare_neg_sorgo_para_milho_sorgo` | veto (−32% de rendimento na sequência) | B |
| Cobertura antes/depois do milho no sequeiro | `luz_crotalaria_fp_60d_milho`, `pacheco13_milheto_pos_colheita_falha` | sem bônus; pré-milho tira 40% da chuva do milho; pós-colheita vetada; só relay tardio | C |
| Leguminosa antes do algodão | `zhao_leg_algodao_nulo` | sem bônus de N (−1,3%); rotação do algodão vale pelo vazio regional | B |
| Desconto por N (perímetros, MATOPIBA, modo global) | `mod_n_fertilizante` | −6 a −7% por 50 kg N/ha; nulo > 236 kg | A |

## Configurações por tipo
"""

REGRAS = """
## Regras de generalização aprovadas

Cada regra passou na R2 com maioria (as emendas foram feitas pelos próprios votantes) e traz a evidência.

1. **G01 — Ano colhido.** O bônus de rotação vale só no cenário "colheu"; a quebra é modelada à parte com IMERG e SMAP.
   *Evidência:* Zhao 2022 exclui pares com rendimento zero ("crop failure", p.7, conferido). PAM: rendimento por ha
   plantado < 0,5 da mediana municipal em 18,8% dos município-anos de milho no CE e 21,0% no NE (2000–2024); a
   definição por área colhida depende da UF que informa (MA 0,1%, CE 0,7%, RN 30,6%).
2. **G02 — lnRR sobre o rendimento local.** Nunca t/ha das meta-análises; converter pela distribuição local, incluindo
   quase falhas. *Evidência:* Zhao Fig. 4a (+32% contra +7%); Franke Tab. 3 (controle africano de 1,2–2,1 t/ha contra
   ~0,59 t/ha do milho do sertão); no CE os anos acima da mediana somam 76% do rendimento acumulado do milho.
3. **G03 — Base certa ou nada.** Prior de leguminosa só contra base sem leguminosa. Contra o consórcio S0: "não
   medido" (D). *Evidência:* Eq. 1 do Zhao (p.6) só para controle não leguminoso; Franke excluiu o consórcio; na base
   aberta não há nenhum controle com leguminosa; controle diverso não leguminoso (D 6–9, N ≤ 50) ainda dá +9,4%.
4. **G04 — Desconto por N.** −6 a −7% por 50 kg N/ha (Zhao Fig. 2c; base aberta −0,061 lnRR, sem interação seco × N,
   p=0,87); em sequeiro com N ≤ 50 a inclinação é mais forte (−17 a −19%); nulo acima de 236 kg N/ha (p.3). No sertão
   (N ≈ 0) não há desconto. Franke: 0 N +0,54 t/ha contra 60–120 N +0,32 (interação p=0,204).
5. **G05 — A aridez não reduz o efeito relativo.** O que cai é a t/ha e a chance de colher. No ano seco (LGP < 150 d)
   o IC se alarga até 0, sem mudar o centro. *Evidência:* Franke zona × resposta p=0,351 (Sahel +24% = Guiné +24%);
   Mudare Source Data, leguminosa < 500 mm lnR 0,16 = 500–1.000 mm 0,16 (mesma letra); Zhao com efeito fixo de país,
   AI +0,4% por 0,1 (ns); análogo quente-seco +23,6% observado contra +23,5% previsto.
6. **G06 — Estrato por aridez e temperatura; ano pela água da estação.** Classificar o lugar por P/ET0 e MAT, não pela
   chuva anual. O ano entra pela água da estação da cultura seguinte (IMERG/SMAP) para alargar o IC e para a quebra.
   *Evidência:* na base do Zhao, sítios de 700–1.000 mm têm AI 0,81 (MAT < 10 °C) ou 0,42 (MAT ≥ 20 °C); Kluger: 8 de 9
   leguminosas com bP positivo.
7. **G07 — Pares, com contagem de sítios.** Transferir o par antecessora → cultura; T1 exige ≥ 5 sítios no estrato;
   abaixo disso, só direção ou o limite inferior do IC do cartão mais específico (recurso). *Evidência:* Kluger Tab. S9
   (−12,4% a +14,4% por par); Zhao p.5 (guandu 32,4% contra feijão-comum 14,5%; algodão −1,3%).
8. **G08 — Sem ranking de leguminosa de grão; sorgo responde.** *Evidência:* a ordem se inverte entre Zhao (caupi
   28,7% > amendoim 19,2%), Franke (amendoim e soja 0,62 > caupi 0,40 t/ha) e Mudare (amendoim→milho ns); base aberta
   no análogo amplo: caupi +48,6%, amendoim +35,2%, soja +33,2% (IC sobrepostos); sorgo quente-seco +57,2% (8 sítios).
9. **G09 — Cultura seguinte ≠ sequência inteira.** O motor calcula a sequência com produção e preço locais; cartões
   negativos são obrigatórios. *Evidência:* Mudare p.4 (soja-milho no lugar de milho contínuo: receita −50%;
   milho-sorgo no lugar de sorgo: rendimento −32%); PAM (D): feijão vale 3,6× o milho por kg e inverte a receita.
10. **G10 — Multiplicativo, não seguro de cauda.** O bônus vale ~0 kg no ano de quebra; a estabilidade (lnCV 0,21) tem
    sinal contraditório no próprio artigo (p.2 contra p.9 Eq. 6, conferido) e fica em C.
11. **G11 — 1º ciclo no plano de 3 anos.** *Evidência:* Franke 1º ciclo +0,48 = 2º+ +0,49 t/ha (p=0,907); os ganhos que
    crescem por décadas (Smith, Bowles, Raveloaritiana) vão para a etiqueta de 10–20 anos.
12. **G12 — Irrigado ≠ sequeiro.** *Evidência:* Mudare irrigado +9% contra sequeiro +22% (mesma letra); base aberta,
    AI < 0,5: irrigado +13,8% contra sequeiro +21,9%; todo efeito de cobertura na cultura seguinte no NE foi irrigado.
13. **G13 — Espaço ≠ tempo.** *Evidência:* PAM-CE, milho +13,7% por +100 mm dentro do município contra −15,5% entre
    municípios; Kluger (calor reduz o benefício dentro da região) contra Zhao (efeito de MAT entre climas some com
    efeito fixo de país; a África dá +44% nas duas classes de MAT).
14. **G14 — Retornos decrescentes; função > número de espécies; diversidade medida no talhão.** *Evidência:* Kluger
    3,67× (p.13, conferido); Smith (corcova; 2–3 grupos funcionais); Yang (cereal sobre cereal −16%); o Simpson municipal
    (2,04) não é a sequência do talhão.
15. **G15 — Consórcio tem cartão próprio; LER > 1 não autoriza dizer que supera o melhor solteiro.** *Evidência:* Diniz
    Tab. 2 (sistema 12.130 = sorgo solteiro 14.073, mesma letra); Mudare 2022 (LER parecido, ganho absoluto escala com o
    insumo).
16. **G16 — LER e Kc por par.** Milho+caupi: LER dependente da água (1,37 → 1,15 da lâmina 125% à 0; prior africano
    1,37) e ET maior no consórcio (Souza 2015). Palma+sorgo: LER estável de 355 a 1.012 mm (Diniz p.730) e ET inalterada
    (Lima 2018b).
17. **G17 — Cobertura no sequeiro do NE.** Efeito na cultura seguinte só foi medido com irrigação; a cobertura de 60 d
    antes do milho tira 40% da chuva do ciclo do milho (641 → 387 mm); pós-colheita sem água (63 mm medianos em 60 d;
    0 de 9 locais do sertão com ≥ 167 mm em 90 d); em sequeiro só relay tardio (~50–85 DAP) ou faixa perene, sem bônus de
    grão (Melo 2013: ns em 9 anos). Pacheco 2013: milheto pós-colheita igual ao pousio.
18. **G18 — Biomassa não prevê ganho; teto por fotoperíodo.** *Evidência:* Souza 2024 (juncea 6,0 Mg/ha sem ganho);
    Andrade 2025 (caupi 728 kg/ha deu +27%); Miranda 2020 (2–5 t/ha em ~60 d abaixo de ~15° de latitude).
19. **G19 — Custo da semente decide o curto prazo da cobertura.** *Evidência:* da Luz 2023 (feijão-de-porco −118 US$/ha;
    spectabilis +94).
20. **G20 — Preparo do solo:** independente do efeito de ROTAÇÃO (Renwick p=0,737; MacLaren; Mudare plantio direto ns);
    moderador obrigatório do efeito de COBERTURA (Pacheco 2017: +11,8% só em SPD) com o custo dos primeiros anos de SPD.
21. **G21 — Pousio e quebra sem leguminosa sempre comparáveis; não retirar o pousio sem balanço hídrico.** *Evidência:*
    Mudare pousio→milho +31,0% e não leguminosa < 500 mm +26% (letra b); Kluger pousio bP −3,4* (vale mais na seca);
    Bowles/Akron (tirar o pousio anulou o ganho).
22. **G22 — Antecessor que atrasa a semeadura ou gasta água dá perda maior em ano seco.** *Evidência:* Kluger soja→trigo
    de inverno −12,4%*; no sertão, 30 d de atraso tiram quase toda a janela de sobressemeadura (Quixadá 77 → 27 mm).
23. **G23 — Pragas.** A mobilidade define a escala (talhão só para dispersão curta; mariposa voa ~100–250 km); especialista
    móvel (bicudo) só se quebra no tempo e de forma sincronizada na região; consórcio sem mecanismo não quebra (algodão +
    milho nulo); hospedeiro perene ou invisível anula o vazio; escolher o parceiro pelo status de hospedeiro de cada praga;
    praga sem número de meta-análise (Raveloaritiana: controle de pragas ns até 50 anos).
24. **G24 — Aleia de leguminosa arbórea com grão:** não prometer grão nem N; gliricídia só fixa N com forrageira perene
    (Martins 2015: Ndfa 0% junto ao grão contra ~52% com buffel ou palma).
25. **G25 — Carbono:** dado de campo (C) separado de modelo (D); o modulador é o retorno de esterco e resíduo.
26. **G26 — O ano supera o manejo no semiárido:** efeito "comprovado" exige ≥ 3 anos com o ano como fator; 1–2 anos dão C
    no máximo (Sousa 2012: o ano seco mexeu mais nos micorrízicos que qualquer tratamento).
27. **G27 — Auditoria:** número da tabela com as letras do teste, não do resumo; fórmula (T − C)/C; só resumo vira D;
    Source Data antes do texto.
28. **G28 — Régua de chuva:** posicionar o ano de cada ensaio na climatologia IMERG; converter limiares em mm por posto
    (razão IMERG/pluviômetro de 0,12 a 2,18 nos ensaios do NE).
29. **G29 — O IBGE não arbitra a rotação:** o teto da literatura no painel municipal (+1,4% a +2,6% por +10 p.p.) fica
    abaixo do efeito mínimo detectável (MDE80 corrigido 3,7% no NE e 7,1% no CE); validar no talhão.
30. **G30 — Duas escalas:** grau (força no domínio) separado da transferência (T0–T3), para não penalizar duas vezes.

### Regras rejeitadas na R2

- "Reduzir b pela aridez" (PROPOSTA_FINAL_v2.md, linha ~748) e a 1ª metade da R4 do especialista em leguminosas (faixa
  baixa de 0 a +35% como centro na zona seca): o relativo não cai (G05). Fica a 2ª metade (pousio e sorgo comparáveis).
- "Abaixo de ~600 mm não prometer ganho de rendimento" (ecólogo): vem de 2 sítios temperados frios de alto insumo, usa
  chuva anual em vez de aridez e é contrariada pela Source Data do Mudare e pela base aberta do Zhao. Fica só "não retirar
  o pousio sem medir a água".
- "Contra a S0, ≈ 0 a +4%" (engenheiro, reta do Zhao com D = 8): fora do domínio da Eq. 1; o próprio autor retirou.
- "Central = limite inferior do IC global" como regra padrão (engenheiro): vale só como recurso para pares sem estrato.
- "Amendoim > caupi" e "o sorgo responde pouco" (leitura do Franke pelo metodólogo, que a retirou).
- "Classificar a zona do Franke a cada ano e aplicar a faixa sudano-saheliana" (R5 do especialista em leguminosas, como
  escrita): troca espaço por tempo; substituída por G06.
- "Escalar o ganho pelo Simpson municipal" (ecólogo, forma original): falácia ecológica.
- "Risco de reinfestação por gravidade como peso numérico" (entomólogo R9): o teste no PAM deu nulo; fica estrutura (D).
- "O caupi aumenta e o amendoim reduz nematoides" (R11 do especialista em leguminosas, como escrita): o mesmo parágrafo
  do Franke traz Alvey 2001 e Marschner 2004 em sentido contrário; substituída por "nenhuma leguminosa é quebra garantida".
- "Preparo independente" como regra universal (ecólogo) e "LER depende da água" e "consórcio gasta mais água" como regras
  universais (agroecólogo): valem por par (G16, G20).
"""

EXCLUIDAS = """
## Excluídas e por quê

| Configuração | Quem propôs | Motivo da exclusão (maioria da R2) |
|---|---|---|
| Pastagem → milho e pastagem → soja (Kluger 2025, Canadá) | Satélite | Mede conversão de pasto em lavoura (64% das amostras mudaram uma única vez, p.11) e some com o NIRv (Apêndice C.2); não é rotação nem ILP |
| Rotacionar todo o contínuo até 2051–2070 (Zhou 2024) | Satélite | Projeção de modelo, específica do Corn Belt, lida só no resumo |
| Rotação diversa × resposta à melhora do ambiente (Bowles, Mead) | Ecólogo | Interação crível em só 2 sítios; média global nula; sem uso no motor |
| Coberturas × fontes de P no milho de sequeiro (Barbosa et al. 2026, DOI 10.1016/j.geodrs.2026.e01065) | Agrônomo | Não lido (só o título). O índice lista outro primeiro autor: conferir a autoria. É a 1ª prioridade de leitura |
| Palhada do capim para a safra seguinte (Zonta 2016) | Zootecnista | Efeito afirmado, não medido; vai para as lacunas |
| Consórcio simultâneo milho + U. ruziziensis, produtividade do milho (Pacheco 2013/2017) | Cerrado | Sem milho solteiro de controle |
| Palma com gliricídia ou leucena, biologia do solo (Camelo 2021) | Agroecólogo | Só o resumo, sem número |
| Milho + caupi + algodão com gliricídia ou esterco, micorrizas (Sousa 2012) | Agroecólogo | Indicador biológico sem rendimento e sem contraste consórcio × solteiro; o ano domina o manejo |
| Número do guandu → milho sob striga (+765%, Manica) | Leguminosas | Caso extremo excluído pelos próprios autores; striga não verificada no NE. O princípio ficou (`striga_principio`) |
| Duplicatas | Metodólogo, engenheiro, zootecnista | Fundidas no cartão canônico: leguminosa global, leguminosa→milho, Franke (média, zonas, N), sequência inteira, economia de N, estabilidade, moduladores N e D, aleias de gliricídia (a versão do zootecnista vinha do resumo e foi substituída pela leitura do Quadro 6) |
"""

CONFLITOS = """
## Conflitos e como resolvemos

1. **A aridez reduz o efeito relativo?** Proposta e leguminosas R4: sim; ecólogo: sem ganho abaixo de 600 mm; metodólogo,
   satélite e outros: não. *Resolução:* não reduz (G05); o centro relativo fica, o IC alarga no ano seco, a t/ha cai e a
   quebra entra à parte. Conferido: Franke Tab. 3 (Sahel 1,16 → 1,44; Guiné 2,14 → 2,66; AEZ p=0,351) e Mudare S5-S6.
2. **O "16% (10–22%)" do Mudare na África.** Leitura comum na R1/R2: "é a não leguminosa global". *Conferido pelo
   integrador na Source Data (aba Figure 1e):* o intervalo 10–22% casa com a LEGUMINOSA NA AMÉRICA DO NORTE (lnR 0,1492;
   0,0971–0,201 → 16,1%, 10,2–22,3%). A não leguminosa global é 16% com IC 11–21% (0,148; 0,107–0,19). Na África,
   leguminosa +29% (0,2542; 0,126–0,382; n=303) e não leguminosa +2,3% ns (0,0223; −0,183 a 0,228; n=36). O agrônomo
   estava certo; o texto compara África (29%) com América do Norte (16%).
3. **Centro do caupi/leguminosa de grão → cereal no sertão.** Propostas de +14,7% (agroecólogo), +17% (engenheiro),
   ~+24% (satélite, entomólogo, ecólogo) a +25% (metodólogo) e faixa de +15% a +45% (leguminosas). *Resolução:* cartão
   `ne_lg_cereal_sequeiro_quente` com central +24% (mediana dos centros dados pelos votantes), faixa +2% (IC inferior do
   Mudare < 500 mm) a +49% (Zhao, caupi→cereal no análogo amplo), grau B·T1, só contra cereal solteiro e no ano colhido.
4. **Ranking de espécies** (Franke contra Zhao contra Mudare): faixa comum, sem ranking (G08); a espécie se escolhe por
   aptidão, preço e portão de pragas.
5. **O sorgo responde?** Franke (+0,12 t/ha ns) contra Zhao (+28,4%) e base aberta (+57,2%): responde como o milho; no
   Franke o cereal está confundido com a zona (p=0,435, conferido).
6. **Contrafactual S0.** Reta do Zhao (+4%) contra "não medido": não medido, grau D, faixa de sensibilidade 0 a +9%; a
   decisão S0 × rotação sai da sequência inteira (LER contra solteiro de cada ano, preço local) e do risco.
7. **Escalas de grau incompatíveis** (Smith A para o ecólogo e B para outros; Faustino B; resumos como "verificado"):
   escala única com dois eixos (G30). Smith = B; ensaio único = C; só resumo = D (Beal Cohen, Beillouin, Menezes, King &
   Blesh); Zhou ficou C pela maioria, com a marca "só resumo".
8. **Temperatura** (Kluger: calor reduz; Zhao: sítios quentes maiores): espaço ≠ tempo (G13). Sem desconto no prior;
   ano quente de El Niño fica como hipótese C.
9. **Bowles na seca: perda menor ou rendimento maior; 88,9% ou 89,9%?** *Conferido:* o Summary (p.2) escreve "yield
   losses were reduced by 14.0%–89.9%" e o corpo (p.6) "14.0% and 88.9% higher" (Fig. 2B). Citar o corpo; não transfere.
10. **Renwick: 17,1% ou 17,1 p.p.?** *Conferido:* resumo (p.2) "17.1 ± 6.1%"; resultados (p.6) perda de 53% contra 36%.
    São 17,1 p.p. (cerca de um terço a menos em termos relativos).
11. **Aleias de gliricídia: mais grão perto da fileira?** O resumo de Pérez-Marin diz que sim; o Quadro 6 mostra ns em
    2003 e gradiente só em 2004, sem testemunha sem árvore. Vale a tabela. Martins 2015: caupi 36a contra 410a (letras
    iguais; conferido). Não prometer ganho nem perda de grão; a linha 742 da proposta deve virar faixa forrageira afastada.
12. **Preparo do solo** (independente para rotação × obrigatório para cobertura): as duas posições valem para objetos
    diferentes (G20).
13. **LER do consórcio milho+caupi em sequeiro** (teto 1,15 do agroecólogo contra 1,37 do Mudare 2022): prior 1,37
    modulado pela água; 1,15 como cenário seco; o agroecólogo retirou o "teto universal".
14. **LER e ET do palma+sorgo contra milho+caupi:** as regras "LER depende da água" e "consórcio gasta mais água" valem
    para anual+anual; no palma+sorgo o LER foi estável e a ET não mudou (G16).
15. **Frequência de quebra do milho (4,8% / 15,1% / 22,7%):** a definição por área colhida depende da UF; adotada
    "rendimento por ha plantado < 0,5 da mediana municipal": CE 18,8% e NE 21,0% (2000–2024); CE 22,7% (1988–2025).
16. **"Leguminosa forrageira → milho +83%":** não é alfafa nem ervilhaca. *Conferido na Source Data (Fig. 2b):* é
    crotalária juncea → milho +83,43% (47,87–127,53; n=13); alfafa → milho +20,15%; trevo → milho +8,24% ns. A "mistura →
    cereal +60%" é quase toda trigo (mistura → trigo +70,44%, n=70 de 79); não há mistura → milho.
17. **Guandu: prior forte ou cobertura que falha?** Só guandu de ciclo completo ou perene herda o +32,4%; como cobertura de
    60 d e semeado junto com o milho é cartão nulo ou negativo.
18. **Sorgo como escape hídrico × portão de pragas:** entra como estratégia comparável, com veto onde há algodão na
    paisagem (alimenta o bicudo adulto) ou ponte verde de gramínea (lagarta).
19. **Sequência inteira: perde ou ganha receita?** Mudare (preços dos EUA) perde; o PAM do NE (feijão 3,6× o milho) ganha
    (grau D). O motor sempre calcula com o preço local; comparar contra a S0, não contra milho-milho.
20. **Estabilidade (lnCV).** *Conferido:* p.2 lê lnCV 0,21 como rotação mais estável; p.9 (Eq. 6) diz que é mais estável
    quando lnCV < 0. Grau C, nunca seguro de cauda.
21. **Mediana do Kluger:** p.33 diz 4,5% (conferido); a Tab. S9 recalculada dá mediana 4,25% e média 4,52%. Sem efeito na
    decisão; citar 4,25% com a nota.
22. **Rusinamhodzi +0,1 t/ha:** *conferido* "mean = 0.1" impresso na Fig. 2 (p.661); a Tab. 2 só descreve tratamentos.
    Grau C, só direção.
23. **Diniz LER 1,51 contra 1,38:** o desenho é aditivo; o artigo publica 1,51 (Tab. 3, conferido) e a razão das médias
    da Tab. 2 dá 1,38. Citar 1,51 com a nota e usar ATER 1,30 quando a comparação for de área-tempo.
24. **Magnitude soja→milho por satélite** (Kluger 0,26 t/ha, Zhou 0,96 t/ha, Beal Cohen +1,0%): efeito pequeno não se
    reproduz entre cadeias; a magnitude do milho vem das meta-análises.
25. **IMERG como régua dos ensaios** (0,12 em Lagoa Seca, 1,77 em Serra Talhada, 2,18 em Pentecoste, −14% em Brejo-MA):
    não corrigir artigos pelo IMERG; usar anomalia/percentil na própria célula e calibrar limiares por posto (G28).
26. **Rotação leguminosa → cereal e lepidópteros:** o Franke cita a rotação milho-caupi/soja AUMENTANDO o ataque de broca
    (Chabi-Olaye 2005a), com ganho líquido pelo vigor; o consórcio com não hospedeira reduziu. O portão não credita a
    rotação como redução de lepidópteros (G23).
27. **Carbono de agrofloresta** (Primo 2023, modelo: recupera em ~10 anos; Sacramento 2013, campo: o agrossilvipastoril
    perde 5–8 Mg/ha): na tela só o campo (C, ranking); Primo fica D como cenário; nunca misturar os Mg/ha.
"""

DADOS_TXT = """
## O que os nossos dados mostraram (testes da R1)

**1. Painel IBGE PAM × IMERG (engenheiro; `v4_engenheiro_leguminosa_t1_milho.py`).** ln(rendimento do milho em t) contra
a fração de leguminosas de grão em t−1, com chuva IMERG fev–mai (quadrática), efeitos fixos de município e ano, EP por ano.
- Ceará (184 municípios, 4.901 município-anos, 1999–2025): −3,38% do milho por +10 p.p. de leguminosa em t−1 (IC95 −7,23 a
  +0,64; p=0,095); com tendência por município −3,66%. **Placebo com a fração de t+1: −4,12%**, igual ao "efeito" do
  passado. Corrigido pelo placebo: **+0,18% (−5,01 a +5,37), MDE80 7,1%**. Com zeros (produção/área plantada): −1,58 p.p.
  (placebo −2,87). Checagem do modelo: +100 mm na mediana de 605 mm dão +14,3% de milho.
- Nordeste (1.620 municípios, ~38.500 município-anos): −2,76% (−4,30 a −1,19), placebo −3,25%; corrigido **+0,76%
  (−1,96 a +3,48; MDE80 3,7%)**; semiárido 2022: corrigido +0,24%.
- A fração de leguminosa repete o consórcio do mesmo roçado: r(t−1, t) = +0,60 (CE) e +0,59 (NE) depois dos efeitos fixos.
- Interação com a chuva: +5,8% por +1 dp no CE (placebo +0,5%), mas −0,09% no NE sem o CE: hipótese D, não regra.
- **Leitura:** o painel municipal não identifica o efeito do antecessor; o teto da literatura no município (+1,4% a +2,6%
  por +10 p.p.) está abaixo do MDE80. A validação tem de ir para o talhão (G29).

**2. Espaço contra tempo no PAM-CE (satélite, T4).** Milho: +13,7% da média por +100 mm de chuva fev–mai DENTRO do
município (IC95 12,4–14,9) contra −15,5% ENTRE municípios (−20,4 a −10,5); feijão +8,5% contra −2,7%. Gradiente espacial
não serve como resposta ao clima (G13).

**3. Quebra e domínio das meta-análises (leguminosas, blocos B, C4, C5).** Rendimento por ha plantado < 0,5 da mediana
municipal: CE 18,8% (2000–2024) e 22,7% (1988–2025); NE 21,0%. Por área colhida a medida varia de 0,1% (MA) a 30,6% (RN):
artefato de quem informa. Rendimento mediano dos anos colhidos: milho 590 kg/ha no semiárido NE, abaixo de todo controle
dos artigos.

**4. Zona do Franke pelo IMERG e GAEZ (leguminosas, blocos A e E).** Semiárido NE (1.254 municípios): 589 com < 700 mm,
588 com 700–1.200 mm; pelo Mudare, 244 com < 500 mm. Semiárido do CE: 157 de 175 na faixa da Guiné pela chuva média, mas o
LGP do GAEZ no CE tem mediana 157 d e ficou < 150 d em 19 de 51 anos.

**5. Base aberta do Zhao (metodólogo, satélite, engenheiro, cerrado, agrônomo).** Reproduz o artigo (mediana 10,2%;
73,6/0,7/25,7%). Análogo AI 0,2–0,5 e MAT ≥ 20 °C: +23,6% (49 sítios), previsto +23,5% por moderadores ajustados fora do
análogo. Cereal tropical, N ≤ 50, sequeiro: +45,4% (23 sítios; +43,5% sem o sítio de maior peso, no Mali). Com efeito fixo
de país, AI e MAT não têm efeito; N tem (−6,0% por 50 kg). Controle diverso não leguminoso D 6–9 com N ≤ 50: +9,4%.
Adubo verde com AI < 0,5: +28,3% (−0,6 a +45,4; 9 sítios), igual à leguminosa de grão; irrigado +4,8%. Só 2,2% das
observações têm o AI do CE; os 68 pares brasileiros vêm de AI 0,88–1,30 (nenhum no semiárido).

**6. A base do Nordeste não é monocultura (ecólogo).** Simpson inverso mediano 2,04 no semiárido; 97,9% com 2–3 grupos
funcionais; milho e feijão andam juntos (ρ = +0,78 entre municípios, +0,63 na variação anual). Adubam 28,6% dos
estabelecimentos do semiárido (16,8% no CE); rotação declarada 12,3–13,6% (CE 7,9%, mediana municipal 0,9%). Rotação
declarada contra milho na seca de 2012–2016: nenhuma faixa significativa; Spearman ecológico ρ = +0,15 (< 700 mm), D.

**7. Quebra conjunta milho-feijão (agroecólogo, PAM-CE 1988–2025).** P(ambos quebram) = 0,117 contra 0,035 se
independentes (3,3×); ρ = 0,71; nos 9 anos de seca estadual a razão ao normal foi 0,57 (feijão) e 0,37 (milho). O seguro
vem do ciclo curto, não da mistura.

**8. Janelas de cobertura (agrônomo e cerrado, IMERG 1998–2025).** Pré-milho (1ª chuva → +60 d): 323 mm medianos (≥ 270
mm em 65%), mas o milho atrasado perde 40% da chuva do ciclo (641 → 387 mm; Tauá 475 → 228). Pós-colheita: 63 mm
medianos em 60 d; 0 de 9 locais do sertão chegam a 167 mm em 90 d (Bom Jesus-PI 203; Brejo-MA 476). Sobressemeadura no
fim do enchimento: ≥ 50 mm em 30–85% dos anos no sertão (mediana 63%), só com semeadura na 1ª chuva. Fotoperíodo: dia
mais longo de 12,29 a 12,58 h nos 184 municípios do CE.

**9. Envelope hídrico do palma+sorgo (zootecnista).** Chuva anual ≥ 976 mm (menor nível de Lima 2018a) em 29,1% dos
município-anos do CE e em 0% em 1998, 2012 e 2016; ≥ 355 mm em 99,3%. Os ensaios de Serra Talhada caíram em anos secos
(percentis 0, 22 e 33); IMERG/pluviômetro de 0,89 a 1,77 no Sertão e 0,12–0,62 em Lagoa Seca.

**10. Suporte climático e memória de água (satélite, T2 e T3).** A chuva fev–mai do CE cai 78% dentro do P5–P95 da
estação das Planícies dos EUA; a temperatura (26,2 °C) está fora do suporte (18,8 °C em Iowa). Cerca de 30% da anomalia
de umidade (Noah) sobrevive à entressafra nos dois lugares (CE: corr 0,55, inclinação 0,28).

**11. Pragas no PAM (entomólogo).** O efeito da continuidade do hospedeiro na chegada do bicudo não é identificável no
PAM (ρ +0,150, p=0,109; placebos do mesmo tamanho). Milho ou sorgo existem em 98,3% dos município-anos do CE (1990–2025):
não há quebra regional da lagarta por rotação. Percolação: rotacionar 30–50% dos talhões fragmenta o hospedeiro a 300 m,
mas a 5 km ele segue conectado em todas as janelas.

**12. Sequência inteira com preço do PAM (leguminosas, bloco F; D).** Semiárido NE 2010–2024 (n=16.888): feijão vale
3,61× o milho por kg; feijão→milho dá 0,80–0,94 da massa do milho-milho, mas 1,55–1,69× a receita (acima em 82–90% dos
município-anos). Sem custo, sem mão de obra, comparado com milho-milho (não com a S0).

**13. Manejo do sal (agroecólogo, IMERG).** Um mar–jun como o de 2012 (289 mm na célula de Pentecoste, 2º mais seco em
28 anos) ocorre em ≥ 20% dos anos em 49% das células do CE: a lavagem pela quadra não é garantida.
"""

LACUNAS = """
## Lacunas

1. **Nenhum ensaio de rotação do semiárido brasileiro** em Zhao, Franke, Mudare, Smith, MacLaren ou Kluger; os 68 pares
   brasileiros do Zhao vêm de 4 sítios com AI 0,88–1,30.
2. **O contraste que importa não foi medido:** consórcio milho+feijão (S0) contra rotação no tempo milho/caupi (ou faixas
   que trocam de lugar), com rendimento das duas culturas, em sequeiro e ≥ 3 anos. Procurar na Embrapa Semiárido e Meio-Norte.
3. **Efeito em anos de quebra** é desconhecido (as meta-análises excluem o rendimento zero).
4. **LER de vários anos em sequeiro no NE** não existe no lote (os dois ensaios com LER são irrigados, de 1 ano).
5. **Cobertura em sequeiro no NE:** nenhum efeito na cultura seguinte medido; Barbosa 2026 não lido (DOI
   10.1016/j.geodrs.2026.e01065; o índice lista outro primeiro autor).
6. **Custo hídrico da antecessora** (quanto ela gasta da recarga antes do cereal) não foi medido: testar com SMAP L4 por sequência.
7. **Pragas e doenças de solo:** nenhum artigo mede rotação contra Meloidogyne, Pratylenchus, Macrophomina ou Fusarium no
   NE; striga não verificada; status do caupi como hospedeiro da lagarta no CE não verificado; faltam capturas de armadilha
   do bicudo (ADAGRI, Embrapa Algodão) para validar a percolação.
8. **ILP:** efeito da palhada na safra seguinte e produto animal (leite, carne por ha) não medidos; palma+sorgo sem
   tratamento de sequeiro verdadeiro.
9. **Textos não lidos ou só pelo resumo:** Zhou 2024, Beal Cohen 2019, Beillouin 2021, King & Blesh 2018, Camelo 2021,
   Primo 2023, Menezes 2002, Marini 2020 (PDF em `artigos/`, lido só o resumo), Supl. Tab. 2 do Raveloaritiana, Supl.
   Tab. 3–5 do Smith, Parte Suplementar 3 do MacLaren, Midega 2018 (push-pull), Araújo Filho 2002/2013, Ramalho &
   Gonzaga 1989/1990.
10. **Mudare 2022:** o PDF não está em `artigos/` (ficou num scratchpad que é apagado); os LER não foram reconferidos
    nesta rodada.
11. **DOIs fora de `artigos/indice.csv`:** Andrade 2025 (Agronomy 15:1083), Silva 2022 (Atmosphere 13:1617), Jardim 2020
    (RBEAA 24:756–761) e Zonta 2016 (Embrapa Algodão, Documentos 266, sem DOI) ficaram com DOI não verificado.
12. **Inconsistências internas para não propagar:** Mudare 2025 (lnCV p.2 × p.9; '16%' da África); Mudare 2022 (0,61 ×
    0,70 t/ha; texto × Fig. 5 sobre N); Bowles (88,9 × 89,9); Renwick (% × p.p.); Diniz (LER aditivo; Fig. 3B × Tab. 2;
    linha rotulada "Single crop"); Souza 2015 (Kc da Tab. 2 × Conclusões); Souza 2011 (1.655,0 × 1.663,33; unidade da EUA);
    Sacramento 2013 (−8,13 × −5,13; N da caatinga −44%); Martins 2015 (grão a/a × N do grão b/a); Lima Filho 2000 (pontos de
    LER); Neves 2015 (texto × letras da Tab. 3); Pérez-Marin 2006 (476 × 479); Melo 2013 (1.100 mm × IMERG 667 mm; '22–49%'
    é efeito do NPK); Nascimento 2008 (texto × Quadro 5); Andrade 2025 ((T−C)/T); Montenegro 2019 (4 × 8 t/ha); Pacheco
    2013/2017 (mesmo experimento; R5.5 × R5.6); Pacheco 2011 é Rio Verde-GO, não Nordeste; King & Blesh é 2018 com 2 autores.
13. **PAM e mapas:** o PAM não separa consórcio de solteiro nem registra a sequência por talhão; não há mapa anual de
    culturas no CE (o MapBiomas não separa milho de feijão).
14. **Correções sugeridas a documentos existentes (não editados nesta rodada):** PROPOSTA_FINAL_v2.md linha ~748 ("reduzir
    b pela aridez"), ~742 (faixas de gliricídia com caupi → faixa forrageira afastada), ~751 (Primo 2023 de C para D), S2
    (palma+sorgo: 12,1 t contra 14,1 t do sorgo solteiro, ns), Bowles e Renwick (rendimento maior; p.p.);
    pesquisa/meta_analises_globais.md ("+37% a +189%" → +13% → +44% de lucratividade; lista de países do MacLaren está na
    p.8); pesquisa/culturas_eficientes.md ("amendoim e soja > caupi"); pesquisa/artigos_e_datasets.md linha ~886.
"""

CONFERENCIAS = """
## Conferências feitas pelo integrador nesta rodada

Script `conselho/analises/v4_integrador_catalogo_conferencias.py` (saída `.saida.txt`): Source Data do Mudare 2025 (abas
Figure 1e, 2a, 2b, S5-S6), trechos de texto de Zhao 2022, Mudare 2025, Bowles 2020, Renwick 2021, Diniz 2017,
Raveloaritiana 2026, Melo 2013, Kluger 2025, Rusinamhodzi 2011, Martins 2015 e Souza 2011, e a Tabela 3 do Franke 2018
(XML do Europe PMC). Os resultados estão marcados "conferido" na coluna de página/tabela.
"""


def main():
    md = [INTRO]
    for t in range(1, 7):
        md.append(tabela(t))
    md += [REGRAS, EXCLUIDAS, CONFLITOS, DADOS_TXT, LACUNAS, CONFERENCIAS]
    MD.write_text("".join(md), encoding="utf-8")

    confs = []
    for k in D.C:
        confs.append({
            "id": k["id"], "tipo": k["tipo"], "configuracao": k["nome"],
            "antecessora": k["ant"],
            "sucessora_ou_par": (k["cult"] if k["tipo"] in ("consorcio", "agrofloresta", "ilp") and (k["suc"].startswith("consórcio") or k["suc"] == "—") else k["suc"]),
            "base_comparacao": k["base"],
            "culturas": k["cult"], "efeito": efeito_json(k["ef"]),
            "condicoes": dict(zip(["aridez", "n_kg_ha", "produtividade", "duracao"], k["cond"])),
            "grau": k["g"], "transferencia": k["T"], "transfere_ne": k["ne"], "transfere_ne_motivo": k["ne_md"],
            "transfere_global": k["gl"], "onde": k["onde"], "moduladores": k["mod"],
            "referencias": k["doi"], "referencia_texto": k["ref"], "fonte_pagina": k["pg"],
            "efeito_texto": k["ef_md"],
        })
    saida = {
        "versao": "v4-integrador", "gerado_em": HOJE,
        "fonte": "conselho/analises/v4_integrador_catalogo_dados.py",
        "convencoes": {
            "efeito.unidade": "lnRR quando o original e %; pct guarda [central, baixo, alto] em %; null = nao publicado",
            "intervalos_calculados": "em t/ha e LER, baixo/alto = +-1,96*EP calculado pelo conselho quando o artigo publica so o EP; em pares agrupados (Kluger) baixo/alto e a faixa entre pares, nao IC",
            "efeito.na": ["cultura_seguinte", "sequencia_inteira", "sistema_consorciado", "solo_ou_servico", "praga"],
            "grau": "A/B/C/D = forca da evidencia no dominio do estudo (escala unica do conselho)",
            "transferencia": {"T0": "medido no semiarido brasileiro", "T1": "analogo AI 0,2-0,5 e MAT >= 20 C com >= 5 sitios",
                              "T2": "so direcao", "T3": "nao transfere"},
            "uso_no_motor": "numero so com T0 ou T1; T2 so direcao; bonus de rotacao so no cenario 'colheu'; nunca somar cultura_seguinte com sequencia_inteira",
        },
        "parametros_ne": D.PARAMETROS_NE,
        "regras_motor": [{"id": i, "regra": r} for i, r in D.REGRAS_MOTOR],
        "configuracoes": confs,
        "excluidas": [
            {"configuracao": "Pastagem -> milho/soja (Kluger 2025)", "motivo": "conversao de uso da terra, nao rotacao", "referencias": [D.KLUGER]},
            {"configuracao": "Cenario 2051-2070 (Zhou 2024)", "motivo": "projecao de modelo, so resumo", "referencias": [D.ZHOU]},
            {"configuracao": "RCI x indice ambiental (Bowles, Mead)", "motivo": "credivel em 2 sitios", "referencias": [D.BOWLES]},
            {"configuracao": "Coberturas x fontes de P (2026)", "motivo": "nao lido", "referencias": ["10.1016/j.geodrs.2026.e01065"]},
            {"configuracao": "Palhada do capim para a safra seguinte (Zonta 2016)", "motivo": "nao medido", "referencias": []},
            {"configuracao": "Consorcio milho + U. ruziziensis (Pacheco)", "motivo": "sem controle solteiro", "referencias": [D.PACH13, D.PACH17]},
            {"configuracao": "Palma + gliricidia/leucena, biologia do solo (Camelo 2021)", "motivo": "so resumo", "referencias": ["10.3390/agronomy11081558"]},
            {"configuracao": "Micorrizas com gliricidia/esterco (Sousa 2012)", "motivo": "sem rendimento; ano domina", "referencias": ["10.4025/actasciagron.v34i2.13143"]},
            {"configuracao": "Numero do guandu -> milho sob striga (+765%)", "motivo": "outlier excluido pelos autores", "referencias": [D.FRANKE]},
        ],
    }
    JS.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    # checagens
    j = json.loads(JS.read_text(encoding="utf-8"))
    ids = [c["id"] for c in j["configuracoes"]]
    assert len(ids) == len(set(ids)), "ids duplicados"
    obrig = ["id", "tipo", "antecessora", "sucessora_ou_par", "efeito", "condicoes", "grau", "transfere_ne", "referencias"]
    for c in j["configuracoes"]:
        for o in obrig:
            assert o in c, (c["id"], o)
        for o in ["variavel", "central", "baixo", "alto", "unidade", "na"]:
            assert o in c["efeito"], (c["id"], o)
        for o in ["aridez", "n_kg_ha", "produtividade", "duracao"]:
            assert o in c["condicoes"], (c["id"], o)
        assert c["grau"] in "ABCD" and c["transfere_ne"] in ("sim", "parcial", "nao")
    from collections import Counter
    print("configuracoes:", len(ids))
    print("por tipo:", dict(Counter(c["tipo"] for c in j["configuracoes"])))
    print("por grau:", dict(Counter(c["grau"] for c in j["configuracoes"])))
    print("por transferencia:", dict(Counter(c["transferencia"] for c in j["configuracoes"])))
    print("transfere_ne:", dict(Counter(c["transfere_ne"] for c in j["configuracoes"])))
    print("MD bytes:", MD.stat().st_size, "| JSON bytes:", JS.stat().st_size)


if __name__ == "__main__":
    main()
