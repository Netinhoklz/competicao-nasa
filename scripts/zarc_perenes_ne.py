"""ZARC dos perenes do Nordeste (caju, cana-de-açúcar e banana), no formato da tábua aberta.

Caju (cajueiro-anão): Portarias SPA/MAPA nº 403 a 411, de 16/12/2020 (DOU de 17/12/2020), uma por estado (AL 403, BA 404,
CE 405, MA 406, PB 407, PE 408, PI 409, RN 410, SE 411), vigentes pelas páginas "Safra vigente — <estado>" do MAPA. As antigas
(nº 35–42 de 2011, 143/2011 e 216/2011) foram revogadas pela Port. SPA/MAPA nº 1, de 09/01/2018 (PDF na página do RN).
Cada portaria tem duas tabelas no formato das plurianuais do CE (Solo 1/2/3 × risco 20/30/40%; ver zarc_plurianual_ce.py):
  5.1 ciclo anual de produção: o risco do município para o pomar (ciclo de 300 dias; o município é classificado pelo menor
      risco em algum decêndio, nota técnica da portaria);
  5.2 implantação do pomar: os decêndios para plantar as mudas.
Três leituras independentes, comparadas célula a célula:
  - PDF do MAPA, pela posição do texto (pypdf), como em zarc_plurianual_ce.py;
  - texto do DOU (in.gov.br, HTML com células explícitas): PDF × DOU tem de bater; se não bater (ou o PDF não ler), o
    estado é registrado no MANIFESTO e fica com a tábua aberta (abaixo), marcada na observação;
  - tábua aberta "Perene, Olerícola e Sem Safra" dos dados abertos do MAPA: as diferenças com o PDF vão para o MANIFESTO.
Cana-de-açúcar, sequeiro: Port. SPA/MAPA nº 5 (outros fins: alimentação animal, açúcar mascavo, melado, cachaça) e nº 4
(açúcar e álcool), ambas de 22/01/2026 (DOU de 26/01/2026). Os PDFs não trazem a tabela (o item 5 remete ao SISZARC e ao
Painel do ZARC): a fonte é a tábua aberta perene, sem segunda leitura. Port. 7/2026 (irrigação de salvamento) só no MANIFESTO.
Banana, sequeiro: Port. SPA/MAPA nº 260–268 de 2019 (AL, BA, MA, PB, PE e SE têm sequeiro; CE, PI e RN só irrigada). Fonte:
a tábua aberta perene, sem segunda leitura (os PDFs ficam em fontes/ para conferir depois).

Convenções da saída (tabua_perenes_ne.csv, sep=";", colunas da tábua aberta + observacao):
  - Nome_cultura "Caju" = implantação do pomar (janelas de plantio); "Caju (ciclo de produção)" = tabela 5.1 (risco do
    município). Idem "Banana" e "Banana (ciclo de produção)". "Cana-de-açúcar" = outros fins (Port. 5/2026);
    "Cana-de-açúcar (açúcar e álcool)" = Port. 4/2026, só para referência.
  - Cod_Ciclo: caju 13 e cana 19 (os da tábua aberta); banana 31 = Maçã, 32 = Prata, 33 = Cavendish (convenção deste
    arquivo; na tábua aberta as três vêm com 13 e o grupo está no nome da cultura).
  - Como na tábua aberta anual (e em zarc_plurianual_ce.py), não há linha toda zerada; o MANIFESTO conta as omitidas.
  - SafraIni/SafraFin vazios: portarias plurianuais, valem da publicação até serem revogadas.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 scripts/zarc_perenes_ne.py
"""
import hashlib
import io
import json
import re
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import pandas as pd  # noqa: E402
from pypdf import PdfReader  # noqa: E402

from comum import DADOS, baixar, registrar_manifesto, sessao_http  # noqa: E402
from zarc_plurianual_ce import _Tabelas, contigua, em_vale, norm_cel, norm_nome, periodos  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = DADOS / "complementares" / "zarc_perenes_ne"
FONTES = BASE / "fontes"
SAIDA = BASE / "tabua_perenes_ne.csv"
SV = ("https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-"
      "risco-climatico/portarias/safra-vigente/")
DOU = "https://www.in.gov.br/web/dou/-/"
TABUA = ("https://dados.agricultura.gov.br/dataset/6d3d141c-885e-41a4-ab7f-dc8ff323b96f/resource/"
         "dae65d31-683f-4ac4-ab90-3abd0c1583ba/download/dados-abertos-tabua-de-risco-safra-perene-olericola-sem-safra.csv")
ESTADO = {"MA": "maranhao", "PI": "piaui", "CE": "ceara", "RN": "rio-grande-do-norte", "PB": "paraiba",
          "PE": "pernambuco", "AL": "alagoas", "SE": "sergipe", "BA": "bahia"}
# UF -> (nº da portaria, PDF relativo à página Safra vigente, final do endereço no DOU)
CAJU = {
    "AL": (403, "alagoas/word/PORTN403CAJUAL.pdf", "portaria-n-403-de-16-de-dezembro-de-2020-294642264"),
    "BA": (404, "bahia/word/PORTN404CAJUBA.pdf", "portaria-n-404-de-16-de-dezembro-de-2020-294651366"),
    "CE": (405, "ceara/word/PORTN405CAJUCE.pdf", "portaria-n-405-de-16-de-dezembro-de-2020-294638585"),
    "MA": (406, "maranhao/arquivos/PORTN406CAJUMA.pdf", "portaria-n-406-de-16-de-dezembro-de-2020-294651440"),
    "PB": (407, "paraiba/arquivos/PORTN407CAJUPB.pdf", "portaria-n-407-de-16-de-dezembro-de-2020-294642338"),
    "PE": (408, "pernambuco/arquivos/PORTN408CAJUPE.pdf", "portaria-n-408-de-16-de-dezembro-de-2020-294651514"),
    "PI": (409, "piaui/arquivos/PORTN409CAJUPI.pdf", "portaria-n-409-de-16-de-dezembro-de-2020-294650710"),
    "RN": (410, "rio-grande-do-norte/arquivos/PORTN410CAJURN.pdf", "portaria-n-410-de-16-de-dezembro-de-2020-294651667"),
    "SE": (411, "sergipe/arquivos/PORTN411CAJUSE.pdf", "portaria-n-411-de-16-de-dezembro-de-2020-294638659"),
}
REVOGACAO_CAJU = "rio-grande-do-norte/word/PORTN1REVOGAODASPORTARIASDECAJU.pdf"
CANA_PDF = {4: "paraiba/PORTN4CANAACARELCOOL.pdf", 5: "paraiba/PORTN5CANAOUTROSFINS.pdf"}
# nome na tábua aberta -> (Nome_cultura da saída, Cod_Ciclo da saída ou None = manter)
MAPA_TABUA = {
    "Caju Anão Implantação": ("Caju", None), "Caju Anão Produção": ("Caju (ciclo de produção)", None),
    "Cana-de-Açúcar (outros fins)": ("Cana-de-açúcar", None),
    "Cana-de-Açúcar (açúcar e álcool)": ("Cana-de-açúcar (açúcar e álcool)", None),
    "Banana Maçã Implantação": ("Banana", 31), "Banana Maçã Produção": ("Banana (ciclo de produção)", 31),
    "Banana Prata Implantação": ("Banana", 32), "Banana Prata Produção": ("Banana (ciclo de produção)", 32),
    "Banana Cavendish Implantação": ("Banana", 33), "Banana Cevendish Produção": ("Banana (ciclo de produção)", 33),
}
VARIEDADE = {31: "Maçã", 32: "Prata", 33: "Cavendish"}
NE = set(ESTADO)
SOLOS, RISCOS = (1, 2, 3), (20, 30, 40)
D = [f"dec{i}" for i in range(1, 37)]
COLS = ["Nome_cultura", "SafraIni", "SafraFin", "Cod_Cultura", "Cod_Ciclo", "Cod_Solo", "geocodigo", "UF", "municipio",
        "Cod_Clima", "Nome_Clima", "Cod_Outros_Manejos", "Nome_Outros_Manejos", "Produtividade", "Cod_NM", "Cod_Munic",
        "Cod_Meso", "Cod_Micro", "Portaria"] + D + ["observacao"]
# cabeçalho da tabela: linhas só em maiúsculas ("PRODUÇÃO" vem sozinho na 2ª linha do título da 5.1) e os rótulos de coluna
CABECALHO = re.compile(r"^(RISCO|DE|\d0%|SOLO \d|MUNICÍPIOS|PERÍ|ODOS)|^[A-ZÀ-Ü :]+$")
SECAO_PDF = re.compile(r"^5\.([12])\b")
SECAO = {"1": "produção", "2": "implantação"}
# no PDF da PB, o começo da 1ª célula às vezes vem no mesmo pedaço de texto do nome ("Sapé1 a" + "36")
NOME_E_CELULA = re.compile(r"^(.*?[^\d\s+])\s*(\d[\d\sa+]*)$")
# nomes das portarias de 2020 -> nome do IBGE (conferidos no localidades_municipios_ne.json)
APELIDO = {"acu": "assu", "augustosevero": "campogrande", "muquemdesaofrancisco": "muquemdosaofrancisco"}
CELULA = re.compile(r"^\d{1,2}( a \d{1,2})?( \+ \d{1,2}( a \d{1,2})?)*$")


def chave_nome(n):
    """Nome sem acento, caixa nem espaços: o PDF às vezes perde o espaço entre pedaços ("Muquémde São Francisco")."""
    n = norm_nome(n).replace(" ", "")
    return APELIDO.get(n, n)


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------- leitura 1: PDF do MAPA (posição do texto)
def ler_pdf_caju(caminho):
    """{(seção, nome): [9 células]} na ordem S1 20/30/40, S2 20/30/40, S3 20/30/40; seção = produção | implantação."""
    ordem, bordas, secao, cur, ult_nome, nome_y, na_tabela, vistas = [], None, None, None, False, None, False, []
    for pg in PdfReader(caminho).pages:
        frag = []

        def vis(t, cm, tm, fd, fs):
            if t.strip():
                frag.append((tm[4] * cm[0] + tm[5] * cm[2] + cm[4], tm[4] * cm[1] + tm[5] * cm[3] + cm[5], t))

        pg.extract_text(visitor_text=vis)
        riscos = [x for x, _, t in frag if t.strip() == "RISCO"]
        if len(riscos) == 9:
            # o texto é centrado na célula: a coluna é a do "RISCO" (centro ≈ x + 12) mais perto do centro do texto
            # (≈ x + 2 por caractere). A borda fixa (RISCO − 3) de zarc_plurianual_ce.py erra no PDF da PB ("1 a 36" de 30%).
            bordas = [x - 3 for x in riscos]
            centros = [x + 12 for x in riscos]
        for x, y, bruto in frag:
            t = " ".join(bruto.split())
            if "RELAÇÃO DOS MUNICÍPIOS" in t:
                na_tabela, ult_nome = True, False
                continue
            if not na_tabela:
                continue
            m = SECAO_PDF.match(t)
            if m:
                secao, ult_nome = SECAO[m.group(1)], False
                vistas.append(secao)
                continue
            if secao is None or bordas is None or CABECALHO.match(t):
                continue
            if x < bordas[0]:  # coluna do município
                if ult_nome:  # mesmo nome: pedaço da mesma linha ("Alcâ" + "ntaras") ou nome quebrado em 2–3 linhas
                    cur[1].append(bruto if abs(y - nome_y) < 1 else " " + bruto)
                else:
                    cur = (secao, [bruto], [[] for _ in range(9)])
                    ordem.append(cur)
                # um pedaço que termina numa célula inteira ("São Vicente do Seridó 1 a 36") fecha o nome
                ult_nome, nome_y = not re.search(r"[^\W\d_].*\d$", t), y
                continue
            col = min(range(9), key=lambda i: abs(x + 2 * len(t) - centros[i]))
            cur[2][col].append(t)
            ult_nome = False
    assert vistas == ["produção", "implantação"], f"seções no PDF: {vistas}"
    out, colados = {}, {}
    for s, nome, cels in ordem:
        txt = " ".join("".join(nome).split())
        chave = (s, txt)
        junto = NOME_E_CELULA.match(txt)
        if junto:  # nome + 1ª célula preenchida no mesmo pedaço de texto (PDF da PB)
            chave = (s, junto.group(1).strip())
            suf = norm_cel(junto.group(2))
            if not CELULA.match(suf):  # célula partida ("1 a" + "36"): junta com a 1ª célula lida à parte
                i = next(k for k, c in enumerate(cels) if c)
                cels[i].insert(0, suf)
            else:  # célula inteira: a coluna fica entre as vazias à esquerda da 1ª lida à parte (resolvida no main)
                colados[chave] = suf
        assert chave not in out, f"município repetido no PDF: {chave}"
        out[chave] = [norm_cel(" ".join(c)) for c in cels]
    return out, colados


# ---------------------------------------------------------------- leitura 2: texto do DOU
def ler_dou_caju(caminho):
    p = _Tabelas()
    p.feed(caminho.read_text(encoding="utf-8", errors="replace"))
    out, secao, vistas = {}, None, []
    for lin in p.linhas:
        txt = " ".join(lin).upper()
        if "PERÍODOS INDICADOS PARA MANEJO DURANTE O CICLO ANUAL DE PRODUÇÃO" in txt:
            secao = "produção"
            vistas.append(secao)
            continue
        if "PERÍODOS INDICADOS PARA IMPLANTAÇÃO DO POMAR" in txt:
            secao = "implantação"
            vistas.append(secao)
            continue
        if secao is None or len(lin) != 10 or not lin[0] or lin[0] == "MUNICÍPIOS" or lin[1].startswith("RISCO"):
            continue
        chave = (secao, lin[0])
        assert chave not in out, f"município repetido no DOU: {chave}"
        out[chave] = [norm_cel(c) for c in lin[1:]]
    assert vistas == ["produção", "implantação"], f"seções no DOU: {vistas}"
    return out


# ---------------------------------------------------------------- leitura 3: tábua aberta perene (dados abertos)
def tabua_aberta(s):
    """Linhas do NE de caju, cana e banana da tábua aberta perene (filtro em fluxo; o arquivo nacional não é gravado)."""
    arq = FONTES / "tabua_aberta_perene_ne_caju_cana_banana.csv"
    h = hashlib.sha256()
    r = s.get(TABUA, stream=True, timeout=300)
    r.raise_for_status()
    cab, manter, n, resto = None, [], 0, b""

    def linhas_do_fluxo():
        nonlocal resto
        for bloco in r.iter_content(1 << 20):
            h.update(bloco)  # hash dos bytes crus do arquivo nacional
            partes = (resto + bloco).split(b"\n")
            resto = partes.pop()
            yield from partes
        if resto:
            yield resto

    for b in linhas_do_fluxo():
        t = b.decode("utf-8", errors="replace").rstrip("\r")
        if cab is None:
            cab = t.lstrip("\ufeff")
            cols = cab.split(";")
            iuf, icult = cols.index("UF"), cols.index("Nome_cultura")
            continue
        if not t:
            continue
        n += 1
        p = t.split(";")
        if len(p) > iuf and p[iuf] in NE and p[icult].replace("\xa0", " ").strip() in MAPA_TABUA:
            manter.append(t)
    arq.write_text("\n".join([cab] + manter) + "\n", encoding="utf-8")
    T = pd.read_csv(io.StringIO("\n".join([cab] + manter)), sep=";", dtype=str)
    T["Nome_cultura"] = T.Nome_cultura.str.replace("\xa0", " ").str.strip()
    T[D] = T[D].astype(float).astype(int)
    info = {"url": TABUA, "arquivo_filtrado": f"fontes/{arq.name}", "linhas_brasil": n, "linhas_guardadas": len(T),
            "sha256_do_arquivo_nacional_baixado": h.hexdigest(), "last_modified": r.headers.get("Last-Modified")}
    return T, info


# ---------------------------------------------------------------- páginas de vigência
def vigencia(s):
    out, paginas = {}, {}
    for uf, est in ESTADO.items():
        r = s.get(SV + est, timeout=120)
        r.raise_for_status()
        (FONTES / f"MAPA_safra_vigente_{est}.html").write_bytes(r.content)
        at = re.search(r'documentModified">\s*<span>Atualizado em</span>\s*<span class="value">([^<]+)<', r.text)
        links = {}
        for href, txt in re.findall(r'<a[^>]+href="([^"]+\.pdf)"[^>]*>(.*?)</a>', r.text, flags=re.S | re.I):
            rot = " ".join(re.sub("<[^>]+>", " ", txt).split())
            rel = href.replace(SV, "")
            if re.search(r"CAJU|CANA|BANANA", rel.upper()):
                links[rel] = rot
        paginas[uf] = r.text
        out[uf] = {"pagina": SV + est, "atualizada_em": at.group(1) if at else None,
                   "arquivo": f"fontes/MAPA_safra_vigente_{est}.html", "links_caju_cana_banana": links}
    return out, paginas


def main():
    FONTES.mkdir(parents=True, exist_ok=True)
    s = sessao_http()
    vig, paginas = vigencia(s)
    for uf, (num, rel, _) in CAJU.items():
        rot = vig[uf]["links_caju_cana_banana"].get(rel)
        assert rot is not None, f"{uf}: o PDF do caju ({rel}) não está na página Safra vigente"
        assert "REVOGADA" not in rot.upper(), f"{uf}: caju marcado como revogado: {rot}"
        for n, relc in CANA_PDF.items():
            assert any(k.endswith(relc.rsplit("/", 1)[1]) for k in vig[uf]["links_caju_cana_banana"]), f"{uf}: Port. {n}/2026 fora da página"
    print("vigência:", {uf: v["atualizada_em"] for uf, v in vig.items()})

    T, info_tabua = tabua_aberta(s)
    print(f"tábua aberta perene: {info_tabua['linhas_brasil']} linhas no Brasil; {len(T)} guardadas (NE, caju/cana/banana)")
    meta = T.drop_duplicates("geocodigo").set_index("geocodigo")[["municipio", "Cod_Munic", "Cod_Meso", "Cod_Micro"]]
    sigla = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
    ibge = {uf: {} for uf in ESTADO}
    for mu in json.loads((DADOS / "ibge_nordeste" / "localidades_municipios_ne.json").read_text(encoding="utf-8")):
        ibge[sigla[str(mu["id"])[:2]]][chave_nome(mu["nome"])] = str(mu["id"])
    assert sum(len(v) for v in ibge.values()) == 1794

    linhas, man_caju, cajuT = [], {}, T[T.Nome_cultura.str.startswith("Caju")]
    for uf, (num, rel, dou) in CAJU.items():
        port = f"Port.{num}_de_17-12-2020"
        obs0 = f"Portaria nº {num} SPA/MAPA, de 16/12/2020 (DOU 17/12/2020), plurianual; cajueiro-anão"
        m = {"portaria": f"Portaria nº {num} SPA/MAPA, de 16/12/2020, DOU de 17/12/2020 (art. 2º: em vigor na publicação)",
             "rotulo_na_pagina": vig[uf]["links_caju_cana_banana"][rel]}
        Tu = cajuT[cajuT.UF == uf]
        try:
            f_pdf = baixar(SV + rel, FONTES / rel.rsplit("/", 1)[1], s)
            f_html = FONTES / f"DOU_{dou}.html"
            if not f_html.exists():
                r = s.get(DOU + dou, timeout=120)
                r.raise_for_status()
                f_html.write_bytes(r.content)
            m["pdf"] = {"url": SV + rel, "arquivo": f"fontes/{f_pdf.name}", "sha256": sha256(f_pdf)}
            m["dou"] = {"url": DOU + dou, "arquivo": f"fontes/{f_html.name}", "sha256": sha256(f_html)}
            (A, colados), B = ler_pdf_caju(f_pdf), ler_dou_caju(f_html)
            na = {(sc, chave_nome(n)): v for (sc, n), v in A.items()}
            nb = {(sc, chave_nome(n)): v for (sc, n), v in B.items()}
            assert na.keys() == nb.keys(), f"municípios diferentes PDF×DOU: {sorted(set(na) ^ set(nb))[:8]}"
            # célula colada ao nome no PDF: o PDF diz o texto e que a coluna fica à esquerda da 1ª célula lida à parte;
            # o DOU escolhe a coluna só se tiver esse texto numa delas e as outras vazias (senão a comparação abaixo falha)
            m["celulas_coladas_ao_nome_com_coluna_pelo_DOU"] = []
            for (sc, n), suf in colados.items():
                k, cels = (sc, chave_nome(n)), na[(sc, chave_nome(n))]
                lim = next((i for i, c in enumerate(cels) if c), 9)
                cand = [i for i in range(lim) if nb[k][i] == suf]
                if len(cand) == 1 and all(nb[k][i] == "" for i in range(lim) if i != cand[0]):
                    cels[cand[0]] = suf
                    m["celulas_coladas_ao_nome_com_coluna_pelo_DOU"].append(f"{sc} {n}: '{suf}' na coluna {cand[0] + 1}")
                else:
                    cels[0] = norm_cel(f"{suf} {cels[0]}")
            A = {(sc, n): na[(sc, chave_nome(n))] for (sc, n) in A}  # as linhas da saída saem de A, já resolvido
            dif = [(k, i, na[k][i], nb[k][i]) for k in na for i in range(9) if na[k][i] != nb[k][i]]
            assert not dif, f"{len(dif)} células diferentes PDF×DOU, ex.: {dif[:5]}"
            # nome -> geocódigo: 1º o IBGE do estado; depois a grafia da própria tábua aberta do caju (mesma do MAPA)
            geo_nome = {chave_nome(nm): g for g, nm in zip(Tu.geocodigo, Tu.municipio)}
            geo_nome.update(ibge[uf])
            sem_geo = sorted({n for (_, n) in na if n not in geo_nome})
            assert not sem_geo, f"nomes sem geocódigo: {sem_geo}"
            fora_da_tabua = sorted({n for (_, n) in na if geo_nome[n] not in set(Tu.geocodigo)})
            assert not fora_da_tabua, f"geocódigo fora da tábua aberta do estado: {fora_da_tabua}"
        except Exception as e:  # noqa: BLE001  (registra e segue com a tábua aberta, sem inventar)
            m["erro"] = f"{type(e).__name__}: {e}"
            m["fonte_usada"] = "tábua aberta perene (PDF/DOU não conferidos neste estado)"
            print(f"Caju {uf}: FALHOU a leitura dupla ({m['erro'][:200]}); fica a tábua aberta")
            for _, r in Tu[Tu[D].sum(axis=1) > 0].iterrows():
                lin = {c: r.get(c, "") for c in COLS}
                lin.update(Nome_cultura=MAPA_TABUA[r.Nome_cultura][0], SafraIni="", SafraFin="", Portaria=port,
                           observacao=f"{obs0}; fonte: tábua aberta perene do MAPA (PDF×DOU não conferido: {m['erro'][:120]})")
                linhas.append(lin)
            man_caju[uf] = m
            continue

        conf = {"sobreposicao": 0, "janela_partida": [], "risco_nao_cresce": [], "solos_vazios": []}
        dif_tab, n_tab = [], 0
        tab = {(MAPA_TABUA[r.Nome_cultura][0], r.geocodigo, int(r.Cod_Solo)): [int(r[c]) for c in D] for _, r in Tu.iterrows()}
        for (secao, nome), cels in A.items():
            geo = geo_nome[chave_nome(nome)]
            cult = "Caju" if secao == "implantação" else "Caju (ciclo de produção)"
            for j, solo in enumerate(SOLOS):
                dec = [0] * 36
                por_risco = {rk: periodos(cels[3 * j + i]) for i, rk in enumerate(RISCOS)}
                for rk, ps in por_risco.items():
                    for p in ps:
                        if dec[p - 1]:
                            conf["sobreposicao"] += 1
                        dec[p - 1] = dec[p - 1] or rk
                n_tab += 1
                if tab.get((cult, geo, solo), [0] * 36) != dec:
                    dif_tab.append(f"{secao} {nome} S{solo}")
                todos = [p for ps in por_risco.values() for p in ps]
                if not todos:
                    conf["solos_vazios"].append(f"{secao} {nome} S{solo}")
                    continue
                if not contigua(todos):
                    conf["janela_partida"].append(f"{secao} {nome} S{solo}")
                elif not em_vale(dec):
                    conf["risco_nao_cresce"].append(f"{secao} {nome} S{solo}")
                mm = meta.loc[geo]
                lin = {c: "" for c in COLS}
                cod_cult = Tu[Tu.Nome_cultura == ("Caju Anão Implantação" if secao == "implantação" else "Caju Anão Produção")]
                lin.update(Nome_cultura=cult, Cod_Cultura=cod_cult.Cod_Cultura.iloc[0] if len(cod_cult) else "", Cod_Ciclo=13, Cod_Solo=solo, geocodigo=geo,
                           UF=uf, municipio=mm.municipio, Cod_Clima=0, Nome_Clima="Não se aplica", Cod_Outros_Manejos=1,
                           Nome_Outros_Manejos="Sequeiro", Cod_Munic=mm.Cod_Munic, Cod_Meso=mm.Cod_Meso, Cod_Micro=mm.Cod_Micro,
                           Portaria=port,
                           observacao=(f"{obs0}; tabela {'5.2 implantação do pomar (plantio de mudas)' if secao == 'implantação' else '5.1 ciclo anual de produção (risco do município)'}"
                                       f"; período = decêndio do ano; tabela da portaria: '{cels[3 * j]}' | '{cels[3 * j + 1]}' | "
                                       f"'{cels[3 * j + 2]}' (20|30|40%); PDF = DOU" + ("" if (cult, geo, solo) in tab and tab[(cult, geo, solo)] == dec
                                                                                   else "; difere da tábua aberta")))
                lin.update({f"dec{k + 1}": v for k, v in enumerate(dec)})
                linhas.append(lin)
        # municípios com linha não zerada na tábua aberta que o PDF não lista
        geos_pdf = {(sc, geo_nome[n]) for (sc, n) in na}
        so_tabua = sorted({f"{r.Nome_cultura} {r.municipio} S{r.Cod_Solo}" for _, r in Tu[Tu[D].sum(axis=1) > 0].iterrows()
                           if (("implantação" if r.Nome_cultura.endswith("Implantação") else "produção"), r.geocodigo) not in geos_pdf})
        mun = {n for (_, n) in na}
        m.update({"linhas_da_tabela": {"produção": sum(1 for k in A if k[0] == "produção"),
                                       "implantação": sum(1 for k in A if k[0] == "implantação")},
                  "municipios": len(mun), "municipios_do_estado_na_tabua_aberta": int(Tu.geocodigo.nunique()),
                  "pdf_x_dou": "0 células diferentes", "pdf_x_tabua_aberta": f"{len(dif_tab)} de {n_tab} solo×tabela diferentes",
                  "pdf_x_tabua_aberta_exemplos": dif_tab[:10], "so_na_tabua_aberta": so_tabua[:10],
                  "periodos_sobrepostos": conf["sobreposicao"], "janelas_partidas": conf["janela_partida"],
                  "risco_que_nao_cresce_para_fora": conf["risco_nao_cresce"],
                  "solos_sem_periodo (linha omitida)": len(conf["solos_vazios"]), "fonte_usada": "PDF (= DOU)"})
        man_caju[uf] = m
        print(f"Caju {uf} (Port. {num}): {len(mun)} municípios; PDF×DOU idênticos; PDF×tábua: {len(dif_tab)} de {n_tab} diferentes; "
              f"só na tábua: {len(so_tabua)}; partidas {len(conf['janela_partida'])}; não cresce {len(conf['risco_nao_cresce'])}")

    # ---------------------------------------------------------------- cana e banana: tábua aberta (sequeiro)
    man_cana, man_banana = {}, {}
    for n, relc in CANA_PDF.items():
        f = baixar(SV + relc, FONTES / relc.rsplit("/", 1)[1], s)
        texto = " ".join(p.extract_text() for p in PdfReader(f).pages)
        man_cana[f"Port. {n}/2026"] = {"pdf": {"url": SV + relc, "arquivo": f"fontes/{f.name}", "sha256": sha256(f)},
                                       "pdf_remete_ao_SISZARC": "SISZARC" in texto and "Painel de Indicação de Riscos" in texto}
    outros = T[T.Nome_cultura.str.startswith(("Cana", "Banana"))]
    for _, r in outros.iterrows():
        cult, ciclo = MAPA_TABUA[r.Nome_cultura]
        if r.Nome_Outros_Manejos != "Sequeiro" or sum(int(r[c]) for c in D) == 0:
            continue
        lin = {c: r.get(c, "") for c in COLS}
        if cult.startswith("Cana"):
            num = int(re.search(r"Port\.\s*0?(\d+)", r.Portaria).group(1))
            obs = (f"Portaria nº {num} SPA/MAPA, de 22/01/2026 (DOU 26/01/2026), "
                   + ("outros fins (alimentação animal, açúcar mascavo, melado, cachaça)" if num == 5 else "açúcar e álcool")
                   + ", sequeiro; AD1–AD6 (Cod_Solo 11–16); fonte: tábua aberta perene do MAPA (o PDF remete ao SISZARC)")
        else:
            obs = (f"{r.Portaria.replace('_de_', ' de ')}, banana {VARIEDADE[ciclo]}, "
                   + ("implantação" if cult == "Banana" else "ciclo de produção")
                   + f", sequeiro; Cod_Ciclo {ciclo} = {VARIEDADE[ciclo]} (convenção deste arquivo); fonte: tábua aberta perene do MAPA")
        lin.update(Nome_cultura=cult, SafraIni="", SafraFin="", observacao=obs)
        if ciclo:
            lin["Cod_Ciclo"] = ciclo
        linhas.append(lin)
    for (nome_t, manejo), h in outros.groupby(["Nome_cultura", "Nome_Outros_Manejos"]):
        nz = h[h[D].sum(axis=1) > 0]
        (man_cana if nome_t.startswith("Cana") else man_banana)[f"{nome_t} | {manejo}"] = {
            "portarias": sorted(set(h.Portaria)), "linhas_nao_zeradas": int(len(nz)),
            "municipios_por_uf": {k: int(v) for k, v in nz.groupby("UF").geocodigo.nunique().items()},
            "linhas_zeradas_omitidas": int(len(h) - len(nz)), "na_saida": manejo == "Sequeiro"}

    Tout = pd.DataFrame(linhas, columns=COLS)
    Tout.to_csv(SAIDA, sep=";", index=False, encoding="utf-8")
    print(f"{SAIDA}: {len(Tout)} linhas")
    print(Tout.groupby(["Nome_cultura", "UF"]).geocodigo.nunique().unstack(fill_value=0).to_string())
    f_rev = baixar(SV + REVOGACAO_CAJU, FONTES / REVOGACAO_CAJU.rsplit("/", 1)[1], s)
    registrar_manifesto("zarc_perenes_ne", {
        "fonte": "MAPA, ZARC de perenes do Nordeste (caju, cana-de-açúcar, banana) em portarias plurianuais",
        "arquivo": SAIDA.name, "linhas": len(Tout), "script": "scripts/zarc_perenes_ne.py",
        "formato": "colunas da tábua aberta (dec1..dec36 = risco 20/30/40; 0 = não indicado) + observacao",
        "convencoes": ("'Caju'/'Banana' = implantação (janelas de plantio de mudas); '(ciclo de produção)' = risco do município; "
                       "'Cana-de-açúcar' = outros fins (Port. 5/2026), 'Cana-de-açúcar (açúcar e álcool)' = Port. 4/2026 (referência); "
                       "banana Cod_Ciclo 31/32/33 = Maçã/Prata/Cavendish; linhas toda zeradas omitidas; SafraIni/SafraFin vazios"),
        "leituras": {"caju": "PDF do MAPA (posição do texto) × HTML do DOU, célula a célula; terceira leitura: tábua aberta perene",
                     "cana": "só a tábua aberta perene (as portarias de 2026 não trazem tabela: SISZARC/Painel do ZARC)",
                     "banana": "só a tábua aberta perene (PDFs das Port. 260–268/2019 não lidos)"},
        "vigencia": vig,
        "revogacao_caju_antigas": {"portaria": "Port. SPA/MAPA nº 1, de 09/01/2018: revoga as de caju nº 35–39, 41, 42, 143 e 216 de 2011",
                                   "arquivo": f"fontes/{f_rev.name}", "sha256": sha256(f_rev)},
        "tabua_aberta_perene": info_tabua,
        "caju": man_caju,
        "cana": {**man_cana, "irrigacao_de_salvamento": "Port. 7/2026 (Cana-de-Açúcar (açúcar e álcool) | Irrigado): fora da "
                 "saída; o QUADRA é de sequeiro"},
        "banana": {**man_banana, "irrigada": "CE (Port. 262), PI (266) e RN (267) só têm banana irrigada; fora da saída"},
    }, base=BASE)


if __name__ == "__main__":
    main()
