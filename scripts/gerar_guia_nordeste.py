"""Gera pesquisa/artigos_nordeste.md: artigos com base no Nordeste brasileiro, por modulo do produto, com situacao do PDF."""
import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
GRUPOS = {
    "1. Clima, seca e teleconexão — portões de novembro e janeiro, previsão de tercil": {
        "10.1002/qj.49710343505": "Hastenrath et al. 1977: dinâmica dos riscos climáticos no Nordeste (clássico)",
        "10.1175/1520-0469(1981)038<2653:otdodi>2.0.co;2": "Moura et al. 1981: secas e o dipolo do Atlântico",
        "10.1175/1520-0442(1996)009<2464:vosstw>2.0.co;2": "Nobre et al. 1996: TSM e vento do Atlântico × chuva do Nordeste",
        "10.1002/joc.1341": "Andreoli et al. 2006: efeitos do Pacífico e do Atlântico Sul na chuva",
        "10.1029/2005jd006142": "Kayano et al. 2006: anomalias de chuva × ENSO",
        "10.1007/s10584-011-0227-1": "Hastenrath 2011: revisão dos problemas climáticos do Nordeste",
        "10.1007/s00704-016-1840-8": "Marengo et al. 2016: seca no Nordeste, passado, presente e futuro",
        "10.1590/0001-3765201720170206": "Marengo et al. 2017: a seca de 2010–2016",
        "10.1002/joc.5225": "Brito et al. 2017: frequência, duração e severidade das secas",
        "10.1590/0102-77863630041": "Rocha et al. 2021 (FUNCEME): veranicos no Ceará e impactos no sequeiro",
        "10.3390/w13121613": "Júnior et al. 2021: modelo empírico de previsão sazonal para o Nordeste",
        "10.1590/0102-77863630138": "Sparacino et al. 2021: 35 anos de estação chuvosa e seca no semiárido",
        "10.3390/w12030834": "Filho et al. 2020: análise multivariada (cópulas) da seca 2012–2018",
        "10.3354/cr00786": "Alves et al. 2009: oceanos × safra de milho e feijão no Ceará (1952–2000)",
        "10.1175/jcli-3266.1": "Sun et al. 2005: regionalização climática do Nordeste",
    },
    "2. Água no solo e seca agrícola por satélite — SMAP, NDVI, balde FAO-56": {
        "10.1016/j.rse.2015.11.034": "Anderson et al. 2015/2016: índice de estresse evaporativo (ESI) × perdas de safra no Brasil",
        "10.3389/fenvs.2017.00073": "Rossato et al. 2017: umidade do solo × rendimento no semiárido",
        "10.3390/w10101421": "Zeri et al. 2018: como comunicar a seca agrícola com umidade do solo",
        "10.1002/cli2.7": "Zeri et al. 2021: importância da umidade do solo no monitoramento de seca",
        "10.1590/0001-3765201720170209": "Alvalá et al. 2017: monitoramento de seca no semiárido",
        "10.3390/w9060377": "Paredes-Trejo et al. 2017: índice de déficit hídrico do SMOS no Nordeste",
        "10.3390/rs10081314": "Souza et al. 2018: validação do SMOS L3 e seca em Pernambuco",
        "10.1016/j.rsase.2023.101111": "Araújo et al. 2023: umidade do solo por satélite para seca no semiárido",
        "10.3390/w13192714": "Rodrigues et al. 2021: avaliação do IMERG na bacia do São Francisco",
        "10.1016/j.isprsjprs.2018.12.014": "Barbosa et al. 2019: resposta da Caatinga à seca pelo NDVI",
        "10.3390/rs14112637": "Medeiros et al. 2022: fenologia da Caatinga por sensoriamento remoto",
        "10.1007/s00704-023-04664-1": "Vale et al. 2023: balanço hídrico × rendimento de milho, feijão e mandioca (1990–2019)",
    },
    "3. Água subterrânea — GRACE e GLDAS": {
        "10.1016/j.scitotenv.2019.135845": "Gonçalves et al. 2019: depleção de água pelo GRACE no Nordeste",
        "10.1007/s10040-019-02065-1": "Melati et al. 2019: depleção do aquífero na seca extrema (GRACE)",
        "10.1590/s1982-21702020000300013": "Lima et al. 2020: perdas de massa hídrica na região hidrográfica Atlântico NE Oriental",
    },
    "4. Culturas do sertão e água — coeficientes Kc, tolerância, janelas de plantio": {
        "10.1590/s0006-87052011000300030": "Souza et al. 2011: eficiência do uso da água de milho e caupi, solteiro e consorciado (Petrolina)",
        "10.1590/1983-21252015v28n417rc": "Souza et al. 2015: requerimento hídrico e Kc de milho e caupi, solteiro e consorciado",
        "10.1590/s0100-204x2000000500008": "Filho et al. 2000: respostas fisiológicas de milho e caupi em consórcio",
        "10.1590/1983-21252026v3914137rc": "Santos et al. 2026: déficit hídrico × caupi (BRS Inhuma, BRS Olho Negro)",
        "10.1590/s0100-69162014000400008": "Ramos et al. 2014: caupi verde sob regimes hídricos",
        "10.1590/s1415-43662010000400008": "Campos et al. 2010: aquecimento global × caupi na Paraíba",
        "10.1590/0103-8478cr20151035": "Carvalho et al. 2016: mandioca, produtividade e tolerância à seca",
        "10.1111/jac.12539": "Menezes et al. 2021: híbridos de sorgo sob seca no semiárido",
        "10.3390/w13162288": "Carvalho et al. 2021: água e práticas agrícolas para o sorgo no semiárido",
        "10.3389/fpls.2017.02074": "Santos et al. 2017: data ótima de semeadura do milheto no semiárido (simulação)",
        "10.1590/s1677-04202007000400012": "Bezerra et al. 2007: fisiologia do caju sob estresse",
    },
    "5. Sistemas de cultivo — rotação, consórcio, agrofloresta, cobertura (motor de rotação)": {
        "10.1590/0103-8478cr20131657": "Neves et al. 2015: ROTAÇÃO caupi/girassol com água salina",
        "10.4025/actasciagron.v34i2.13143": "Sousa et al. 2012: consórcio milho-caupi-algodão com adubação orgânica",
        "10.1071/sr17336": "Maia et al. 2019: consórcio + cultivo mínimo e carbono do solo",
        "10.1590/s0100-204x2017000900004": "Diniz et al. 2017: consórcio palma-sorgo irrigado (Serra Talhada)",
        "10.1590/1983-21252018v31n122rc": "Lima et al. 2018a: benefício produtivo-econômico do consórcio palma-sorgo",
        "10.1590/1807-1929/agriambi.v22n2p113-118": "Lima et al. 2018b: uso da água no consórcio palma-sorgo",
        "10.1590/s0100-06832006000300015": "Pérez-Marin et al. 2006: gliricídia × solo, microclima e milho em aleias (Agreste PB)",
        "10.1590/s0100-204x2015000200010": "Martins et al. 2015: N fixado por caupi e gliricídia em agrofloresta (PB)",
        "10.3390/agronomy11081558": "Camelo et al. 2021: agrofloresta com palma e leguminosas arbóreas × biologia do solo",
        "10.5424/fs/2018271-12267": "Pinheiro et al. 2018: silvipastoril na Caatinga (revisão)",
        "10.1023/a:1021172530939": "Menezes et al. 2002: microclima e nutrientes em sistema silvipastoril",
        "10.15446/agron.colomb.v38n1.78957": "Miranda et al. 2020: biomassa de crotalária no semiárido",
        "10.1590/s1415-43662010000200002": "Neto et al. 2010: sorgo forrageiro sob adubação verde",
        "10.5194/adgeo-48-19-2019": "Montenegro et al. 2019: cobertura do solo × umidade e escoamento",
        "10.1016/j.jenvman.2023.117594": "Primo et al. 2023: corte e queima × agrofloresta permanente e em rotação (Sobral-CE)",
        "10.3390/land11010083": "Mapa sistemático de serviços ecossistêmicos da agrofloresta ecológica no Brasil (2022)",
    },
    "6. Solo, carbono e corte e queima": {
        "10.1016/s0167-8809(97)00073-x": "Salcedo et al. 1997: nutrientes em cultivo itinerante na Caatinga",
        "10.1016/j.jaridenv.2007.07.014": "Mamede et al. 2007: corte e queima × banco de sementes da Caatinga",
        "10.1590/s0100-06832013000300025": "Sacramento et al. 2013: C e N do solo, tradicional × agroflorestal",
        "10.1002/ldr.2282": "Ferreira et al. 2014: uso da terra (milho/caupi, uva etc.) × carbono e micróbios do solo",
        "10.1590/s1519-69842012000400004": "Menezes et al. 2012: ciclagem biogeoquímica na Caatinga",
        "10.1016/j.scitotenv.2016.07.095": "Ribeiro et al. 2016: mudança de cobertura × gases de efeito estufa na Caatinga",
    },
    "7. Fogo na Caatinga — portão de entressafra": {
        "10.3390/atmos17010046": "Bezerra et al. 2025: fogo × vulnerabilidade da Caatinga a secas e ondas de calor",
        "10.5902/1980509870195": "Silva et al. 2023: ocorrência e recorrência de fogo na Caatinga (Piauí)",
        "10.3390/fire7120437": "Franca-Rocha et al. 2024: área queimada na Caatinga com deep learning",
        "10.1007/s10661-021-09190-z": "Oliveira et al. 2021: áreas queimadas na bacia do Coreaú (CE)",
        "10.1016/j.ecolind.2020.106151": "Argibay et al. 2020: regimes de fogo no ecótono Caatinga–Cerrado",
    },
    "8. Pragas — algodão e bicudo": {
        "10.1590/1808-1657000012013": "Azambuja et al. 2014: 30 anos do bicudo no Brasil",
        "10.5380/dma.v55i0.72576": "Mattos et al. 2020: a saga do algodão no semiárido (histórico e agroecologia)",
        "10.1590/1519-6984.248154": "Faustino et al. 2021: mortalidade do bicudo em algodão irrigado",
        "10.3390/insects14070582": "Pereira et al. 2023: exigências térmicas e zoneamento do bicudo",
    },
    "9. Políticas, decisão e adaptação — quem usa a ferramenta": {
        "10.1023/a:1020785826029": "Lemos et al. 2002: uso da previsão climática em políticas (Nordeste)",
        "10.1023/a:1024893532329": "Lemos 2003: previsão climática e auxílio à seca no Ceará",
        "10.3354/cr019097": "Finan et al. 2001: adaptações públicas e privadas à seca no Ceará",
        "10.1007/s00267-015-0444-x": "Campos 2015: paradigmas e políticas de seca no Nordeste",
        "10.1002/cli2.17": "Marengo et al. 2021: opções de adaptação agrícola e políticas para a segurança alimentar",
        "10.3390/su10030622": "Lindoso et al. 2018: captação de água e convivência com o semiárido",
        "10.1080/17565529.2017.1301862": "Herwehe et al. 2017: pequena irrigação como adaptação",
    },
}


def main():
    with open(PROJ / "artigos" / "indice.csv", encoding="utf-8-sig") as f:
        idx = {l["doi"]: l for l in csv.DictReader(f)}
    linhas = ["# Artigos com base no Nordeste brasileiro", "",
              "Curadoria em 14/11/2026: os artigos já citados no estudo (varredura de título, resumo e texto completo,"
              " `scripts/artigos_nordeste.py`) mais uma busca dirigida no OpenAlex pelas lacunas (`scripts/buscar_artigos_nordeste.py`,"
              " 357 resultados com o Nordeste no título ou no resumo, dos quais estes foram selecionados).",
              "Os autores e anos vêm do OpenAlex e do Crossref. As descrições resumem o título e o resumo; os números para slides"
              " devem ser conferidos no PDF.",
              "",
              "Situação do PDF: **local** = em `artigos/`; **DOI** = acesso aberto, mas o site bloqueou o download automático"
              " (abrir pelo link); **fechado** = acesso pago.", ""]
    total, locais, faltam = 0, 0, []
    for grupo, itens in GRUPOS.items():
        linhas += [f"## {grupo}", "", "| Referência e o que sustenta | DOI | PDF |", "|---|---|---|"]
        for doi, desc in itens.items():
            l = idx.get(doi)
            if l is None:
                st = "não indexado"
                faltam.append(doi)
            elif l["status"] == "baixado":
                st = f"local ([pdf]({'../artigos/' + l['arquivo']}))"
                locais += 1
            elif "fechado" in l["status"]:
                st = "fechado"
            else:
                st = "DOI"
            total += 1
            linhas.append(f"| {desc} | [{doi}](https://doi.org/{doi}) | {st} |")
        linhas.append("")
    linhas.insert(8, f"**{total} artigos, {locais} com PDF local.**\n")
    (PROJ / "pesquisa" / "artigos_nordeste.md").write_text("\n".join(linhas), encoding="utf-8")
    print(f"{total} artigos; {locais} PDFs locais; não indexados: {faltam}")


if __name__ == "__main__":
    main()
