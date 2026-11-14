"""ZARC do CE em portarias plurianuais (fora da tábua de risco aberta), no formato da tábua aberta.

Culturas: mandioca (Port. SPA/MAPA 11/2020), milheto (Port. 330/2020) e palma forrageira (Port. 284/2019). Revisão
A1/C5 (protótipo/REVISAO_10_AGENTES.md). As três não estão nos dados abertos do ZARC 2026/27, mas estão na página
"Safra vigente — Ceará" do MAPA.

Fontes (TLS verificado, comum.sessao_http):
- PDF do MAPA (link da página "Safra vigente — Ceará"): a fonte principal da tábua. A tabela é lida pela posição do
  texto na página (pypdf), porque as células vazias somem no texto corrido.
- Texto do DOU (in.gov.br, HTML com células explícitas): segunda leitura independente. O script compara as duas, célula
  por célula, e para se houver diferença.

Legenda das tabelas (seções 3 e 5 das portarias):
- "Períodos" 1–36 = decêndios do ano civil (1 = 01–10/jan, 2 = 11–20/jan, 3 = 21–31/jan, ..., 36 = 21–31/dez), como
  dec1..dec36 da tábua aberta. Não há conversão.
- Colunas: SOLO 1, 2 e 3 (tipos 1 arenoso, 2 médio, 3 argiloso; IN nº 2/2008) × RISCO DE 20%, 30% e 40%. As três
  colunas de risco de um solo são disjuntas: cada período aparece numa só, com o seu nível de risco.
- Célula: "a" = intervalo contínuo, com as pontas ("4 a 7" = 4, 5, 6, 7; "34 a 3" vira o ano: 34, 35, 36, 1, 2, 3).
  "+" = união de períodos ou intervalos ("4 + 7" = 4 e 7). Célula vazia = nenhum período com esse risco.
  As portarias não escrevem essa legenda. A leitura vem da tabela de períodos e de três testes feitos aqui: as colunas
  de risco de um solo nunca se sobrepõem; o risco cresce do centro para as pontas da janela; e as janelas são contínuas.
- Milheto: uma tabela por grupo de cultivares, Grupo I (90–110 dias), II (111–135) e III (> 135). Na tábua aberta o
  código é Cod_Ciclo 20, 21 e 22. Mandioca e palma têm grupo único, gravado como Cod_Ciclo 20 (convenção deste
  arquivo, explicada em `observacao`).

Saída: E:/campeonato-nasa/dados/complementares/zarc_plurianual_ce/tabua_plurianual_ce.csv (sep=";"), com as colunas da
tábua aberta + `observacao`, e o MANIFESTO.json. As fontes baixadas ficam em fontes/.
- Uma linha por cultura × município × solo × grupo. Como na tábua aberta, não há linha toda zerada. Quando um solo não
  tem período em nenhum risco, a linha fica de fora, e o MANIFESTO conta esses casos.
- SafraIni/SafraFin ficam vazios: a portaria é plurianual e vale da publicação até ser revogada. Cod_Munic, Cod_Meso,
  Cod_Micro e municipio vêm da tábua aberta 2026/27 do CE, pelo geocódigo.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 scripts/zarc_plurianual_ce.py
"""
import hashlib
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import pandas as pd  # noqa: E402
from pypdf import PdfReader  # noqa: E402

from comum import DADOS, REF, baixar, registrar_manifesto, sessao_http  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = DADOS / "complementares" / "zarc_plurianual_ce"
FONTES = BASE / "fontes"
SAIDA = BASE / "tabua_plurianual_ce.csv"
MAPA = ("https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-"
        "risco-climatico/portarias/safra-vigente/ceara/")
DOU = "https://www.in.gov.br/web/dou/-/"
PORTARIAS = {
    "Mandioca": dict(
        numero=11, assinada="05/02/2020", dou="12/02/2020", pdf=MAPA + "word/PORTN11MANDIOCACE.pdf",
        html=DOU + "portaria-n-11-de-5-de-fevereiro-de-2020-242813305", revoga="Port. 466/2011",
        nota="plantio de mudas (manivas); grupo único de cultivares, gravado como Cod_Ciclo 20"),
    "Milheto": dict(
        numero=330, assinada="20/10/2020", dou="23/10/2020", pdf=MAPA + "word/PORTN330MILHETOCE.pdf",
        html=DOU + "portaria-n-330-de-20-de-outubro-de-2020-284702859", revoga="Port. 268/2012",
        nota="semeadura; Grupo {g} de cultivares ({dias}), Cod_Ciclo {c}"),
    "Palma Forrageira": dict(
        numero=284, assinada="30/09/2019", dou="07/10/2019", pdf=MAPA + "word/PORTN284PALMAFORRAGEIRACE.pdf",
        html=DOU + "portaria-n-284-de-30-de-setembro-de-2019-220202870", revoga="Port. 292/2011 e 7/2019",
        nota="plantio de mudas (raquetes); ciclo simulado de 24 meses; grupo único, gravado como Cod_Ciclo 20"),
}
GRUPOS = {"I": (20, "90–110 dias"), "II": (21, "111–135 dias"), "III": (22, "> 135 dias")}
SOLOS, RISCOS = (1, 2, 3), (20, 30, 40)
D = [f"dec{i}" for i in range(1, 37)]
COLS = ["Nome_cultura", "SafraIni", "SafraFin", "Cod_Cultura", "Cod_Ciclo", "Cod_Solo", "geocodigo", "UF", "municipio",
        "Cod_Clima", "Nome_Clima", "Cod_Outros_Manejos", "Nome_Outros_Manejos", "Produtividade", "Cod_NM", "Cod_Munic",
        "Cod_Meso", "Cod_Micro", "Portaria"] + D + ["observacao"]
CELULA = re.compile(r"^\d{1,2}( a \d{1,2})?( \+ \d{1,2}( a \d{1,2})?)*$")
GRUPO = re.compile(r"GRUPO (III|II|I)\b")
CABECALHO = re.compile(r"^(RISCO|DE|\d0%|SOLO \d|MUNICÍPIOS|PERÍ|5\.|ODOS)")


def norm_nome(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(s.replace("-", " ").replace("'", " ").split())


def norm_cel(s):
    return " ".join(s.replace("+", " + ").split())


# ---------------------------------------------------------------- leitura 1: PDF do MAPA, pela posição do texto
def ler_pdf(caminho, com_grupo):
    """{(grupo, nome): [9 células]} na ordem S1 20/30/40, S2 20/30/40, S3 20/30/40."""
    linhas, bordas, grupo, cur, ult_nome = {}, None, None if com_grupo else "único", None, False
    na_tabela, cab, cab_y, grupos_vistos = False, "", None, []
    for pg in PdfReader(caminho).pages:
        frag = []

        def vis(t, cm, tm, fd, fs):
            if t.strip():
                frag.append((tm[4] * cm[0] + tm[5] * cm[2] + cm[4], tm[4] * cm[1] + tm[5] * cm[3] + cm[5], t))

        pg.extract_text(visitor_text=vis)
        riscos = [x for x, _, t in frag if t.strip() == "RISCO"]
        if len(riscos) == 9:
            bordas = [x - 3 for x in riscos]  # borda esquerda de cada coluna de risco (o texto é centrado na célula)
        cab_y = None
        for x, y, bruto in frag:
            t = " ".join(bruto.split())
            if "RELAÇÃO DOS MUNICÍPIOS" in t:
                na_tabela = True
            if not na_tabela:
                continue
            # título do grupo (milheto); o "I" final às vezes vem num pedaço à parte, na mesma linha ("GRUPO I" + "I")
            cont = cab_y is not None and abs(y - cab_y) < 1
            if com_grupo and ("GRUPO" in t or cont):
                cab = cab + t if cont else t
                cab_y, grupo, ult_nome = y, GRUPO.search(cab).group(1), False
                if cont:
                    grupos_vistos[-1] = grupo
                else:
                    grupos_vistos.append(grupo)
                continue
            if CABECALHO.match(t) or bordas is None:
                continue
            if x < bordas[0]:  # coluna do município
                if ult_nome:  # mesmo nome: pedaço da mesma linha ("Alcâ" + "ntaras") ou nome quebrado em 2–3 linhas
                    cur[1].append(bruto if abs(y - nome_y) < 1 else " " + bruto)
                else:
                    cur = (grupo, [bruto], [[] for _ in range(9)])
                    linhas.setdefault("_ordem", []).append(cur)
                ult_nome, nome_y = True, y
                continue
            col = max(i for i, b in enumerate(bordas) if x >= b)
            cur[2][col].append(t)
            ult_nome = False
    if com_grupo:
        assert grupos_vistos == ["I", "II", "III"], f"títulos de grupo no PDF: {grupos_vistos}"
    out = {}
    for g, nome, cels in linhas.pop("_ordem"):
        chave = (g, " ".join("".join(nome).split()))
        assert chave not in out, f"município repetido no PDF: {chave}"
        out[chave] = [norm_cel(" ".join(c)) for c in cels]
    return out


# ---------------------------------------------------------------- leitura 2: texto do DOU (células explícitas)
class _Tabelas(HTMLParser):
    def __init__(self):
        super().__init__()
        self.linhas, self.lin, self.cel = [], None, None

    def handle_starttag(self, tag, a):
        if tag == "tr":
            self.lin = []
        elif tag in ("td", "th"):
            self.cel = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.lin is not None and self.cel is not None:
            self.lin.append(" ".join("".join(self.cel).split()))
            self.cel = None
        elif tag == "tr" and self.lin is not None:
            self.linhas.append(self.lin)
            self.lin = None

    def handle_data(self, d):
        if self.cel is not None:
            self.cel.append(d)


def ler_dou(caminho, com_grupo):
    p = _Tabelas()
    p.feed(caminho.read_text(encoding="utf-8", errors="replace"))
    out, grupo = {}, None if com_grupo else "único"
    for lin in p.linhas:
        txt = " ".join(lin)
        if com_grupo and GRUPO.search(txt):
            grupo = GRUPO.search(txt).group(1)
            continue
        if len(lin) != 10 or not lin[0] or lin[0] == "MUNICÍPIOS" or lin[1].startswith("RISCO"):
            continue
        chave = (grupo, lin[0])
        assert chave not in out, f"município repetido no DOU: {chave}"
        out[chave] = [norm_cel(c) for c in lin[1:]]
    return out


# ---------------------------------------------------------------- célula -> períodos
def periodos(cel):
    if not cel:
        return []
    assert CELULA.match(cel), f"célula fora do padrão: {cel!r}"
    ps = []
    for parte in cel.split(" + "):
        a, _, b = parte.partition(" a ")
        a, b = int(a), int(b or a)
        assert 1 <= a <= 36 and 1 <= b <= 36, cel
        ps += list(range(a, b + 1)) if a <= b else list(range(a, 37)) + list(range(1, b + 1))  # "34 a 3" vira o ano
    return ps


def contigua(ps):
    """A janela (circular, 36 decêndios) é um trecho só?"""
    s = set(ps)
    return len(s) == 36 or sum(1 for p in s if (p % 36) + 1 not in s) == 1


def em_vale(dec):
    """Numa janela contínua, o risco desce até o miolo e sobe para as pontas (não cresce e depois decresce)?"""
    if 0 not in dec:
        return True
    z = dec.index(0)
    seq = [v for v in dec[z:] + dec[:z] if v]  # a janela na ordem do calendário, a partir de um decêndio vazio
    fundo = seq.index(min(seq))
    return all(a >= b for a, b in zip(seq[:fundo], seq[1:fundo + 1])) and all(a <= b for a, b in zip(seq[fundo:], seq[fundo + 1:]))


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    FONTES.mkdir(parents=True, exist_ok=True)
    s = sessao_http()
    ibge = json.loads((REF / "ceara_municipios_nomes.json").read_text(encoding="utf-8"))
    geo_por_nome = {norm_nome(m["nome"]): m["id"] for m in ibge}
    assert len(geo_por_nome) == 184
    aberta = pd.read_csv(DADOS / "complementares" / "zarc" / "tabua_risco_ce_2026-2027.csv", sep=";", dtype=str)
    cod = aberta.drop_duplicates("geocodigo").set_index("geocodigo")[["municipio", "Cod_Munic", "Cod_Meso", "Cod_Micro"]]

    # vigência: a página "Safra vigente — Ceará" do MAPA lista cada PDF? (as revogadas aparecem com "REVOGADA" no rótulo)
    pag = s.get(MAPA.rstrip("/"), timeout=120)
    pag.raise_for_status()
    (FONTES / "MAPA_safra_vigente_ceara.html").write_bytes(pag.content)
    atualizada = re.search(r'documentModified">\s*<span>Atualizado em</span>\s*<span class="value">([^<]+)<', pag.text)
    vig = {"pagina": MAPA.rstrip("/"), "pagina_atualizada_em": atualizada.group(1) if atualizada else None,
           "arquivo": "fontes/MAPA_safra_vigente_ceara.html", "rotulos": {}}
    for cultura, P in PORTARIAS.items():
        m = re.search(re.escape(P["pdf"]) + r'"[^>]*>([^<]*)</a>', pag.text)
        assert m, f"{cultura}: o PDF não está na página Safra vigente — Ceará"
        vig["rotulos"][cultura] = m.group(1).strip()
        assert "REVOGADA" not in m.group(1).upper(), f"{cultura}: marcada como revogada: {m.group(1)}"
    print(f"Página Safra vigente — Ceará (atualizada em {vig['pagina_atualizada_em']}): {vig['rotulos']}")

    linhas, man = [], {}
    for cultura, P in PORTARIAS.items():
        com_grupo = cultura == "Milheto"
        f_pdf = baixar(P["pdf"], FONTES / P["pdf"].rsplit("/", 1)[1], s)
        f_html = FONTES / f"DOU_{P['html'].rsplit('/', 1)[1]}.html"
        r = s.get(P["html"], timeout=120)
        r.raise_for_status()
        f_html.write_bytes(r.content)
        A, B = ler_pdf(f_pdf, com_grupo), ler_dou(f_html, com_grupo)
        # as duas leituras têm de bater célula a célula (nomes comparados sem acento e caixa)
        na = {(g, norm_nome(n)): v for (g, n), v in A.items()}
        nb = {(g, norm_nome(n)): v for (g, n), v in B.items()}
        assert na.keys() == nb.keys(), f"{cultura}: municípios diferentes PDF×DOU: {set(na) ^ set(nb)}"
        dif = [(k, i, na[k][i], nb[k][i]) for k in na for i in range(9) if na[k][i] != nb[k][i]]
        assert not dif, f"{cultura}: {len(dif)} células diferentes PDF×DOU, ex.: {dif[:5]}"

        port = f"Port.{P['numero']}_de_{P['dou'].replace('/', '-')}"
        sem_ibge = [n for (_, n) in A if norm_nome(n) not in geo_por_nome]
        assert not sem_ibge, f"{cultura}: nomes sem geocódigo IBGE: {sem_ibge}"
        conf = {"sobreposicao": 0, "janela_partida": [], "risco_nao_cresce": [], "solos_vazios": []}
        for (g, nome), cels in A.items():
            geo = geo_por_nome[norm_nome(nome)]
            ciclo = GRUPOS[g][0] if com_grupo else 20
            nota = P["nota"].format(g=g, dias=GRUPOS[g][1], c=ciclo) if com_grupo else P["nota"]
            for j, solo in enumerate(SOLOS):
                dec = [0] * 36
                por_risco = {rk: periodos(cels[3 * j + i]) for i, rk in enumerate(RISCOS)}
                for rk, ps in por_risco.items():
                    for p in ps:
                        if dec[p - 1]:
                            conf["sobreposicao"] += 1
                        dec[p - 1] = dec[p - 1] or rk
                todos = [p for ps in por_risco.values() for p in ps]
                if not todos:
                    conf["solos_vazios"].append(f"{nome} G{g} S{solo}")
                    continue
                if not contigua(todos):
                    conf["janela_partida"].append(f"{nome} G{g} S{solo}")
                elif not em_vale(dec):
                    conf["risco_nao_cresce"].append(f"{nome} G{g} S{solo}")
                lin = {c: "" for c in COLS}
                m = cod.loc[str(geo)]
                lin.update(Nome_cultura=cultura, Cod_Ciclo=ciclo, Cod_Solo=solo, geocodigo=geo, UF="CE",
                           municipio=m.municipio, Cod_Clima=0, Nome_Clima="Não se aplica", Cod_Outros_Manejos=1,
                           Nome_Outros_Manejos="Sequeiro", Cod_Munic=m.Cod_Munic, Cod_Meso=m.Cod_Meso,
                           Cod_Micro=m.Cod_Micro, Portaria=port,
                           observacao=(f"Portaria nº {P['numero']} SPA/MAPA, de {P['assinada']} (DOU {P['dou']}), plurianual, "
                                       f"sem ano-safra; {nota}; período = decêndio do ano; tabela da portaria: "
                                       f"'{cels[3 * j]}' | '{cels[3 * j + 1]}' | '{cels[3 * j + 2]}' (20|30|40%)"))
                lin.update({f"dec{k + 1}": v for k, v in enumerate(dec)})
                linhas.append(lin)
        mun = {norm_nome(n) for _, n in A}
        man[cultura] = {
            "portaria": f"Portaria nº {P['numero']} SPA/MAPA, de {P['assinada']}, DOU de {P['dou']} (revoga {P['revoga']}; "
                        f"art. 3º: em vigor na data da publicação, sem prazo de safra)",
            "pdf": {"url": P["pdf"], "arquivo": f"fontes/{f_pdf.name}", "sha256": sha256(f_pdf)},
            "dou": {"url": P["html"], "arquivo": f"fontes/{f_html.name}", "sha256": sha256(f_html)},
            "linhas_da_tabela": len(A), "municipios": len(mun),
            "municipios_fora_da_portaria": sorted(m["nome"] for m in ibge if norm_nome(m["nome"]) not in mun),
            "pdf_x_dou": "0 células diferentes", "periodos_sobrepostos": conf["sobreposicao"],
            "janelas_partidas": conf["janela_partida"], "risco_que_nao_cresce_para_fora": conf["risco_nao_cresce"],
            "solos_sem_periodo (linha omitida)": conf["solos_vazios"],
        }
        print(f"{cultura}: {len(A)} linhas na portaria, {len(mun)} municípios; PDF×DOU idênticos; "
              f"sobreposições {conf['sobreposicao']}; janelas partidas {len(conf['janela_partida'])}; "
              f"risco que não cresce {len(conf['risco_nao_cresce'])}; solos vazios {len(conf['solos_vazios'])}; "
              f"fora: {man[cultura]['municipios_fora_da_portaria']}")

    T = pd.DataFrame(linhas, columns=COLS)
    T.to_csv(SAIDA, sep=";", index=False, encoding="utf-8")
    print(f"{SAIDA}: {len(T)} linhas")
    print(T.groupby(["Nome_cultura", "Cod_Ciclo", "Cod_Solo"]).size().to_string())
    registrar_manifesto("zarc_plurianual_ce", {
        "fonte": "MAPA, ZARC do Ceará em portarias plurianuais (fora dos dados abertos da tábua de risco)",
        "pagina_vigencia": MAPA.rstrip("/"),
        "arquivo": SAIDA.name, "linhas": len(T), "script": "scripts/zarc_plurianual_ce.py",
        "formato": "colunas da tábua aberta (dec1..dec36 = risco 20/30/40; 0 = não indicado) + observacao",
        "legenda": "período = decêndio do ano (1 = 01–10/jan); 'a' = intervalo com as pontas (vira o ano se o início "
                   "for maior); '+' = união; colunas Solo 1/2/3 × risco 20/30/40% disjuntas",
        "convencoes": "Cod_Ciclo 20/21/22 = Grupo I/II/III do milheto; mandioca e palma (grupo único) = 20; "
                      "SafraIni/SafraFin vazios (plurianual); linhas sem nenhum período omitidas, como na tábua aberta",
        "leituras": "PDF do MAPA pela posição do texto (pypdf) e HTML do DOU; comparadas célula a célula",
        "vigencia": vig,
        "culturas": man,
    }, base=BASE)


if __name__ == "__main__":
    main()
