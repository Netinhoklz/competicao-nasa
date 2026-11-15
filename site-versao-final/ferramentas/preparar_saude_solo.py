"""Gera site-versao-final/web/dados/saude_solo.json: os 4 cartões "O que cada planta faz pelo seu solo" (ponto 10 do desafio:
fixadoras de nitrogênio, cobertura/palhada, raiz funda e tolerantes à seca) para o módulo web/js/extras/saude_solo.js.

Lê só pesquisa/catalogo_rotacoes.json (o catálogo do conselho). Cada número da frente sai de um campo do catálogo; quando o
número está só no texto do cartão (ex.: o "~14% (nu)" do Montenegro), o script o procura no texto e para se não achar. Assim,
se o catálogo mudar, o JSON não fica com número velho. As culturas de cada papel e a conta "em 3 anos" saem do plano do
município, no navegador (ctx.r.plano e ctx.r.cardapio da /api/local); o ZARC do cartão da seca também.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_saude_solo.py"""
import datetime
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CAT = RAIZ.parent / "pesquisa" / "catalogo_rotacoes.json"
SAIDA = RAIZ / "web" / "dados" / "saude_solo.json"

cat = json.loads(CAT.read_text(encoding="utf-8"))
C = {c["id"]: c for c in cat["configuracoes"]}


def cartao(cid, grau=None, transf=None):
    c = C[cid]
    if grau:
        assert c["grau"] == grau, (cid, c["grau"])
    if transf:
        assert c["transferencia"] == transf, (cid, c["transferencia"])
    return c


def achar(cid, padrao):
    """Número que só existe no texto do cartão: para se o texto mudou."""
    m = re.search(padrao, C[cid]["efeito_texto"])
    assert m, (cid, padrao)
    return m


def br(v, casas=0):
    s = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def fonte(cid, diz, grau=None):
    """Linha do "De onde vem": o que o artigo mediu, em palavras simples, com o id do cartão para conferir."""
    c = C[cid]
    return {"id": cid, "grau": grau or c["grau"], "transf": c["transferencia"], "onde": c.get("onde") or "",
            "ref": c.get("referencia_texto") or "", "doi": (c.get("referencias") or [None])[0], "diz": diz}


# ------------------------------------------------------------------ fixa nitrogênio
lg = cartao("ne_lg_cereal_sequeiro_quente", "B", "T1")
assert lg["efeito"]["pct"] == [24.0, 2.0, 49.0], lg["efeito"]["pct"]
p_lg, p_lg_b, p_lg_a = (round(x) for x in lg["efeito"]["pct"])
s0 = cartao("ne_s0_para_rotacao_tempo", "D", "T3")
mt = cartao("martins_gliricidia_forrageira", "C", "T0")
n_ponta = mt["efeito"]["central"]  # 39,3 kg N/ha nas pontas (gliricídia + palma)
n_madeira = float(achar("martins_gliricidia_forrageira", r"na madeira 77,21a e (\d+,\d+)a").group(1).replace(",", "."))
ndfa = round(float(achar("martins_gliricidia_forrageira", r"%Ndfa 52,35 \(buffel\) e (\d+,\d+) \(palma\)").group(1).replace(",", ".")))
nem = cartao("nematoides_amendoim_caupi", "C", "T2")

fixa = {
    "id": "fixa",
    "efeitos": [
        {"quando": "leg_grao", "val": f"+{p_lg}%", "un": "",
         "sub": "no milho ou sorgo plantado no ano seguinte, contra cereal depois de cereal.",
         "cartao": lg["id"], "grau": lg["grau"], "transf": lg["transferencia"], "onde": "",
         "selo": "suposicao", "selo_fonte": f"efeito de artigos em clima parecido (cartão {lg['id']}, {lg['grau']}·{lg['transferencia']}); "
                                            "no seu roçado não foi medido"},
        {"quando": "sempre", "val": br(n_ponta), "un": "kg de N/ha",
         "sub": "de nitrogênio nas pontas da gliricídia plantada junto da palma.",
         "cartao": mt["id"], "grau": mt["grau"], "transf": mt["transferencia"], "onde": "Taperoá-PB",
         "selo": "suposicao", "selo_fonte": f"medido em Taperoá-PB (cartão {mt['id']}, {mt['grau']}·{mt['transferencia']}); "
                                            "no seu roçado não foi medido"},
    ],
    "fontes": [
        fonte(lg["id"], f"Cereal plantado depois de feijão, caupi ou amendoim rende +{p_lg}% (de +{p_lg_b}% a +{p_lg_a}%) no ano "
                        "colhido, contra cereal sem leguminosa antes, em lugar quente e seco e com pouco adubo. Número do conselho a "
                        "partir de 3 estudos (Zhao 2022, Mudare 2025, Franke 2018)."),
        fonte(s0["id"], "Contra o consórcio milho + feijão de hoje, esse ganho nunca foi medido."),
        fonte(mt["id"], f"Gliricídia junto da palma: cerca de {ndfa}% do nitrogênio da planta veio do ar; {br(n_ponta)} kg de N/ha "
                        f"nas pontas e {br(n_madeira)} na madeira. Ao lado do milho com caupi, nada."),
        fonte(nem["id"], "Nenhuma leguminosa quebra o nematoide com certeza: amendoim só com análise do solo."),
    ],
    "decide": "Qual leguminosa entra depende da semente que você tem e do seu solo.",
}

# ------------------------------------------------------------------ cobre o chão (palhada)
mn = cartao("montenegro_palhada_barreira", "C", "T0")
assert mn["efeito"]["pct"][0] == 4.0, mn["efeito"]["pct"]
esc_palha = round(mn["efeito"]["pct"][0])
esc_nu = int(achar("montenegro_palhada_barreira", r"~(\d+)% \(nu\)").group(1))
esc_palma = int(achar("montenegro_palhada_barreira", r"~(\d+)% \(barreira de palma\)").group(1))
achar("montenegro_palhada_barreira", r"perda de solo ~1 → ~0,1")
mf = cartao("melo_fitomassa_leguminosas", "C", "T0")
assert mf["efeito"]["pct"][0] == 36.0, mf["efeito"]["pct"]
mv = cartao("palhada_meia_vida", "C", "T2")
assert (mv["efeito"]["baixo"], mv["efeito"]["alto"]) == (5.4, 15.4), mv["efeito"]
achar("palhada_meia_vida", r"42–177 d")

cobre = {
    "id": "cobre",
    "efeitos": [
        {"quando": "sempre", "val": str(esc_palha), "un": "de 100 litros",
         "sub": f"de chuva escorrem com palhada no chão. No chão nu, {esc_nu}.",
         "cartao": mn["id"], "grau": mn["grau"], "transf": mn["transferencia"], "onde": "Pesqueira-PE",
         "selo": "suposicao", "selo_fonte": f"medido em Pesqueira-PE (cartão {mn['id']}, {mn['grau']}·{mn['transferencia']}); "
                                            "no seu roçado não foi medido"},
    ],
    "fontes": [
        fonte(mn["id"], f"Em encosta do semiárido, sem lavoura, a chuva que escorreu foi ~{esc_nu}% no chão nu, ~{esc_palha}% com palhada e "
                        f"~{esc_palma}% com palma plantada em nível; a terra levada caiu de ~1 para ~0,1 kg por parcela "
                        "(valores lidos de gráfico)."),
        fonte(mf["id"], f"Milho com mucuna no meio deixou {round(mf['efeito']['pct'][0])}% mais palha no chão, sem adubo."),
        fonte(mv["id"], f"No calor do Piauí, metade da palha some em {br(mv['efeito']['baixo'], 1)} a {br(mv['efeito']['alto'], 1)} "
                        "dias (em Goiás, 42 a 177): por isso, sem fogo e sem tirar tudo."),
    ],
    "decide": "Quanto da palha fica no chão e quanto vai para o gado, quem decide é você.",
}

# ------------------------------------------------------------------ raiz funda
pz = cartao("perez_aleia_servicos", "C", "T0")
folha = pz["efeito"]["central"]
folha0 = float(achar("perez_aleia_servicos", r"Folhedo 1\.390 contra (\d+) kg/ha").group(1))
k1, k0 = (float(x) for x in achar("perez_aleia_servicos", r"K (\d+) contra (\d+) mg/kg").groups())
achar("perez_aleia_servicos", r"temperatura máxima do solo −6 °C")
achar("perez_aleia_servicos", r"umidade ~20% MENOR")
achar("perez_aleia_servicos", r"COT sem diferença após 7 anos")
assert k1 / k0 > 2, (k1, k0)
mnl = cartao("mudare_naoleg_grupos_cereal", "B", "T2")
zg = cartao("zhao_guandu", "B", "T2")
mg = cartao("melo_guandu_mesmo_dia", "C", "T0")
assert mg["efeito"]["pct"][0] == -6.4, mg["efeito"]["pct"]

raiz = {
    "id": "raiz",
    "efeitos": [
        {"quando": "sempre", "val": f"{round(folha / folha0)}×", "un": "",
         "sub": "mais folha caindo no chão junto da gliricídia; o potássio do solo mais que dobra.",
         "cartao": pz["id"], "grau": pz["grau"], "transf": pz["transferencia"], "onde": "Esperança-PB",
         "selo": "suposicao", "selo_fonte": f"medido em Esperança-PB (cartão {pz['id']}, {pz['grau']}·{pz['transferencia']}); "
                                            "no seu roçado não foi medido"},
    ],
    "fontes": [
        fonte(pz["id"], f"Junto da fileira de gliricídia, contra 3 m dela: {br(folha)} contra {br(folha0)} kg/ha de folha no chão, "
                        f"potássio {br(k1)} contra {br(k0)} mg/kg e solo até 6 °C mais fresco. Mas a umidade ficou ~20% menor e o "
                        "carbono do solo não mudou em 7 anos."),
        fonte(mnl["id"], "Cereal depois de mandioca tende a render mais que cereal depois de cereal; aqui vale só a direção.", "C"),
        fonte(zg["id"], "Cereal depois de guandu rende mais em estudos do mundo todo; aqui vale só a direção.", ),
        fonte(mg["id"], f"Guandu semeado junto com o milho, no mesmo dia, tirou {br(abs(mg['efeito']['pct'][0]), 1)}% do milho: "
                        "guandu vai em faixa própria."),
    ],
    "nota": "A profundidade da raiz não foi medida nos artigos do catálogo: é o jeito conhecido destas plantas.",
    "decide": "A gliricídia seca o chão perto da fileira: onde pôr a cerca viva, decida com o técnico.",
}

# ------------------------------------------------------------------ aguenta a seca
lm = cartao("lima18b_palma_sorgo_eua", "C", "T0")
eua1, eua0 = (float(x.replace(",", ".")) for x in achar("lima18b_palma_sorgo_eua", r"EUA (\d+,\d) ± [\d,]+ contra (\d+,\d)").groups())
dz = cartao("diniz_palma_sorgo_ler", "C", "T0")
assert dz["efeito"]["central"] == 1.51, dz["efeito"]

seca = {
    "id": "seca",
    "efeitos": [
        {"quando": "zarc", "val": "{dias}", "un": "dias",
         "sub": "para plantar o {cultura} com risco baixo aqui. O milho: {milho}.",
         "cartao": None, "grau": None, "transf": None, "onde": "",
         "prova": "medido para este município",
         "selo": "medido", "selo_fonte": "ZARC 2026/27 deste município: dias de plantio em que a perda por falta d'água vem em até "
                                         "2 de 10 anos"},
        {"quando": "sempre", "val": f"{eua1 / eua0:.0f}×".replace(".", ","), "un": "",
         "sub": "mais pasto por milímetro de água com palma e sorgo juntos, contra palma sozinha.",
         "cartao": lm["id"], "grau": lm["grau"], "transf": lm["transferencia"], "onde": "Serra Talhada-PE, com gotejo",
         "selo": "suposicao", "selo_fonte": f"medido em Serra Talhada-PE, com gotejo (cartão {lm['id']}, {lm['grau']}·"
                                            f"{lm['transferencia']}); no seu roçado não foi medido"},
    ],
    "fontes": [
        {"id": "ZARC", "grau": None, "transf": None, "onde": "este município", "ref": "MAPA, ZARC 2026/27 e portarias plurianuais",
         "doi": None, "diz": "Risco baixo = a perda por falta d'água vem em até 2 de 10 anos, na média do município. Contamos os dias "
                             "de plantio com esse risco, do sorgo (ou milheto) do seu plano contra o milho."},
        fonte(lm["id"], f"Palma com sorgo deu {br(eua1, 1)} kg de pasto por ha a cada milímetro de água; a palma sozinha, "
                        f"{br(eua0, 1)}. Foi com gotejo."),
        fonte(dz["id"], f"Palma e sorgo na mesma terra renderam como {br(dz['efeito']['central'], 1)} ha plantados separados "
                        "(com gotejo de água salobra)."),
    ],
    "decide": "O zoneamento é a média do município: a sua terra pode secar antes ou segurar mais.",
}

# ------------------------------------------------------------------ em 3 anos
sc = cartao("sacramento_agrossilvi", "C", "T0")
achar("sacramento_agrossilvi", r"tradicional −58,87")
assert sc["efeito"]["central"] == -5.13, sc["efeito"]
longo = {
    "regra": "Cada bolinha é um ano do plano (2027, 2028, 2029). Leguminosa: caupi, feijão, amendoim, guandu, mucuna ou gliricídia, "
             "inclusive o feijão que entra no milho do baixio. Palhada: milho, sorgo ou milheto, se a palha fica no chão, sem fogo. "
             "Raiz funda: mandioca, guandu ou gliricídia. A conta segue o plano como está: se você mudar o plano, ela muda.",
    "fontes": [
        fonte(sc["id"], "Em Sobral-CE, em 9 anos, a roça de broca e queima perdeu muito mais carbono do solo do que a roça com "
                        "árvores e esterco. Vale a ordem, não o número."),
        fonte(mv["id"], f"Palha some rápido no sertão quente (metade em {br(mv['efeito']['baixo'], 1)} a "
                        f"{br(mv['efeito']['alto'], 1)} dias no Piauí): a palhada conta se ficar no chão."),
    ],
}

out = {
    "fonte": f"pesquisa/catalogo_rotacoes.json ({cat['versao']}; corrigido em {cat.get('corrigido_em') or cat['gerado_em']})",
    "gerado_em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "graus": {"A": 4, "B": 3, "C": 2, "D": 1},
    "grau_txt": "Força da evidência no catálogo do conselho: A é a mais forte; D, a mais fraca.",
    "transf": {"T0": "medido no semiárido", "T1": "clima parecido", "T2": "só a direção", "T3": "não vale aqui"},
    "papeis": [fixa, cobre, raiz, seca],
    "longo": longo,
}
SAIDA.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(SAIDA, SAIDA.stat().st_size, "bytes")
