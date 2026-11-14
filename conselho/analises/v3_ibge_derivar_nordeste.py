"""v3 - Analista IBGE/Nordeste: transforma os brutos de dados/ibge_nordeste em tabelas prontas em dados/derivados.

  ibge_ne_municipios_referencia.parquet   municipio, UF, regiao imediata/intermediaria, Semiarido 2017 e 2022, area
  ibge_ne_censo2017_praticas_mun.parquet  1 linha por municipio: % de estabelecimentos com rotacao, pousio, nenhuma
                                          pratica, plantio direto, cultivo minimo, irrigacao, orientacao tecnica,
                                          adubacao, cisterna, agricultura familiar, semente guardada (milho, feijao...)
  ibge_ne_pam_mun_anual.parquet           municipio x produto x ano (formato largo, igual ao ibge_pam_mun_anual)
  ibge_ne_pam_safras_mun_anual.parquet    milho 1a/2a e feijao 1a/2a/3a safra (2003-2025)
  ibge_ne_ppm_mun_anual.parquet           municipio x ano: cabecas por rebanho
  ibge_ne_lspa_uf_mensal.parquet          data (mes da estimativa), uf, produto, variavel, valor, unidade, fonte
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import geopandas as gpd
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
IB = DADOS / "ibge_nordeste"
UF_SIG = {21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA"}


def referencia():
    ref = pd.read_parquet(IB / "municipios_ne_referencia_sem_semiarido.parquet")
    s22 = pd.read_excel(IB / "semiarido" / "semiarido_2022.xlsx", dtype=str)
    s17 = pd.read_excel(IB / "semiarido" / "semiarido_2017.xlsx", header=1, dtype=str)
    s17 = s17[s17["Código do Município"].fillna("").str.match(r"^\d{7}$")]
    ref["semiarido_2022"] = ref.cod_mun.isin(s22["CD_MUN"].str.strip())
    ref["semiarido_2017"] = ref.cod_mun.isin(s17["Código do Município"].str.strip())
    g = gpd.read_file(IB / "malha_ne_municipio.geojson").rename(columns={"codarea": "cod_mun"})
    g["geometry"] = g.geometry.make_valid()
    # Albers de area igual centrada no NE; a malha e a simplificada ("intermediaria"), entao a area e aproximada
    aea = "+proj=aea +lat_1=-3 +lat_2=-15 +lat_0=-9 +lon_0=-41 +datum=WGS84 +units=m"
    area = g.to_crs(aea).set_index("cod_mun").area / 1e6
    ref["area_km2"] = ref.cod_mun.map(area)
    ref.to_parquet(DERIV / "ibge_ne_municipios_referencia.parquet")
    print("referencia", len(ref), "semiarido 2022 no NE:", int(ref.semiarido_2022.sum()), "de", len(s22),
          "| 2017 no NE:", int(ref.semiarido_2017.sum()), "de", len(s17), flush=True)
    return ref


def censo():
    d = pd.read_parquet(IB / "censo2017_ne_municipios_bruto.parquet")
    d = d.rename(columns={"Município": "cod_mun", "Variável": "v", "Tipologia": "tip"})
    out = {}

    def pega(tab, v, tip="46302", **cls):
        q = d[(d.tabela == tab) & (d.v == v) & (d.tip == tip)]
        for k, c in cls.items():
            q = q[q[k] == c]
        return q.groupby("cod_mun")["valor"].sum(min_count=1)

    P = "Tipo de prática agrícola"
    A = "Grupos de atividade econômica"
    for tip, suf in (("46302", ""), ("46304", "_fam")):
        base = dict(tab=6880, tip=tip)
        kw = {A: "113601", "Grupos de área total": "110085"}
        tot = pega(v="183", **base, **{P: "113197"}, **kw)
        out["n_estab" + suf] = tot
        out["area_estab_ha" + suf] = pega(v="184", **base, **{P: "113197"}, **kw)
        for cod, nome in (("112677", "rotacao"), ("112764", "pousio"), ("112654", "plantio_nivel"),
                          ("112767", "nenhuma_pratica")):
            out[f"pct_{nome}{suf}"] = 100 * pega(v="183", **base, **{P: cod}, **kw) / tot
        out["pct_area_rotacao" + suf] = 100 * pega(v="184", **base, **{P: "112677"}, **kw) / out["area_estab_ha" + suf]
        kwl = {A: "111519", "Grupos de área total": "110085"}
        tl = pega(v="183", **base, **{P: "113197"}, **kwl)
        out["n_estab_lavtemp" + suf] = tl
        out["pct_rotacao_lavtemp" + suf] = 100 * pega(v="183", **base, **{P: "112677"}, **kwl) / tl
        # preparo do solo (6855): denominador = estabelecimentos totais da 6880
        for v, nome in (("9562", "sem_preparo"), ("9564", "convencional"), ("9565", "cultivo_minimo"),
                        ("2016", "plantio_direto")):
            out[f"pct_{nome}{suf}"] = 100 * pega(6855, v, tip) / tot
        out["area_plantio_direto_ha" + suf] = pega(6855, "2018", tip)
        out["pct_irrigacao" + suf] = 100 * pega(6857, "2372", tip, **{"Método utilizado para irrigação": "118477"}) / tot
        out["area_irrigada_ha" + suf] = pega(6857, "2373", tip, **{"Método utilizado para irrigação": "118477"})
        O = "Origem da orientação técnica recebida"
        tot46 = pega(6846, "183", tip, **{P: "113197", O: "41151"})
        out["pct_orientacao_tecnica" + suf] = 100 * pega(6846, "183", tip, **{P: "113197", O: "113111"}) / tot46
        out["pct_orientacao_governo" + suf] = 100 * pega(6846, "183", tip, **{P: "113197", O: "112647"}) / tot46
        com = pega(6846, "183", tip, **{P: "113197", O: "113111"})
        sem = pega(6846, "183", tip, **{P: "113197", O: "113559"})
        out["pct_rotacao_com_orientacao" + suf] = 100 * pega(6846, "183", tip, **{P: "112677", O: "113111"}) / com
        out["pct_rotacao_sem_orientacao" + suf] = 100 * pega(6846, "183", tip, **{P: "112677", O: "113559"}) / sem
        U = "Uso de adubação"
        t47 = pega(6847, "183", tip, **{U: "46545"})
        out["pct_adubacao" + suf] = 100 * pega(6847, "183", tip, **{U: "46546"}) / t47
        out["pct_adubacao_organica_so" + suf] = 100 * pega(6847, "183", tip, **{U: "46548"}) / t47
        R = "Tipo de recurso hídrico"
        out["pct_cisterna" + suf] = 100 * pega(6861, "2324", tip, **{R: "113497"}) / tot
        # semente guardada (6958): % da area colhida com semente comum guardada
        Pr, S_ = "Produtos da lavoura temporária", "Tipo de semente"
        for cod, nome in (("4888", "milho"), ("111677", "feijao_fradinho"), ("111676", "feijao_cor"),
                          ("4897", "sorgo"), ("111672", "algodao")):
            ac = pega(6958, "10089", tip, **{Pr: cod, S_: "47126"})
            out[f"area_colhida_{nome}_ha{suf}"] = ac
            out[f"pct_area_semente_guardada_{nome}{suf}"] = 100 * pega(6958, "10089", tip, **{Pr: cod, S_: "47124"}) / ac
            out[f"n_estab_{nome}{suf}"] = pega(6958, "10084", tip, **{Pr: cod, S_: "47126"})
    w = pd.DataFrame(out)
    w["pct_familiar"] = 100 * w["n_estab_fam"] / w["n_estab"]
    w.index.name = "cod_mun"
    w = w.reset_index()
    w["fonte"] = "IBGE Censo Agropecuario 2017 (SIDRA 6880, 6855, 6857, 6846, 6847, 6861, 6958)"
    w.to_parquet(DERIV / "ibge_ne_censo2017_praticas_mun.parquet")
    print("censo", w.shape, flush=True)
    return w


def pam():
    d = pd.read_parquet(IB / "pam_ne_municipios_bruto.parquet")
    nomes = {"2689": "Algodão herbáceo", "2702": "Feijão", "2708": "Mandioca", "2711": "Milho", "2714": "Sorgo",
             "2725": "Castanha de caju", "2718": "Algodão arbóreo", "114253": "Milho 1ª safra",
             "114254": "Milho 2ª safra", "117991": "Feijão 1ª safra", "117992": "Feijão 2ª safra",
             "117993": "Feijão 3ª safra"}
    col = {"109": "area_plantada_ha", "2313": "area_plantada_ha", "216": "area_colhida_ha", "214": "producao_t",
           "112": "rendimento_kg_ha", "215": "valor_mil_moeda"}
    prod = d["Produto das lavouras temporárias"].fillna(d.get("Produto das lavouras permanentes"))
    d = d.assign(cod_mun=d["Município"], ano=d["Ano"].astype(int), cod_produto=prod,
                 produto=prod.map(nomes), var=d["Variável"].map(col))
    w = d.pivot_table(index=["cod_mun", "produto", "tabela", "ano"], columns="var", values="valor",
                      aggfunc="first").reset_index()
    w.columns.name = None
    w["uf"] = w.cod_mun.str[:2].astype(int).map(UF_SIG)
    w["tipo"] = w.tabela.map({1612: "temporaria", 1613: "permanente", 839: "safra", 1002: "safra"})
    principal = w[w.tabela.isin([1612, 1613])].drop(columns="tabela")
    safras = w[w.tabela.isin([839, 1002])].drop(columns=["tabela", "valor_mil_moeda"], errors="ignore")
    principal.to_parquet(DERIV / "ibge_ne_pam_mun_anual.parquet")
    safras.to_parquet(DERIV / "ibge_ne_pam_safras_mun_anual.parquet")
    print("pam", principal.shape, safras.shape, principal.ano.min(), principal.ano.max(), flush=True)


def ppm():
    d = pd.read_parquet(IB / "ppm_ne_municipios_bruto.parquet")
    nomes = {"2670": "bovino", "2681": "caprino", "2677": "ovino", "32794": "suino", "32796": "galinaceos",
             "2672": "equino"}
    d["reb"] = d["Tipo de rebanho"].map(nomes)
    w = d.pivot_table(index=["Município", "Ano"], columns="reb", values="valor", aggfunc="first").reset_index()
    w.columns.name = None
    w = w.rename(columns={"Município": "cod_mun", "Ano": "ano"})
    w["ano"] = w.ano.astype(int)
    w["uf"] = w.cod_mun.str[:2].astype(int).map(UF_SIG)
    w["fonte"] = "IBGE PPM (SIDRA 3939), cabecas em 31/12"
    w.to_parquet(DERIV / "ibge_ne_ppm_mun_anual.parquet")
    print("ppm", w.shape, w.ano.min(), w.ano.max(), flush=True)


def lspa():
    d = pd.read_parquet(IB / "lspa_ne_uf_mensal_bruto.parquet")
    nomes = {"0": "Total", "39429": "Algodão herbáceo", "39436": "Feijão 1ª safra", "39437": "Feijão 2ª safra",
             "39438": "Feijão 3ª safra", "39441": "Milho 1ª safra", "39442": "Milho 2ª safra", "39444": "Sorgo",
             "39457": "Castanha de caju", "39467": "Mandioca"}
    var = {"109": ("area_plantada", "ha"), "216": ("area_colhida", "ha"), "35": ("producao", "t"),
           "36": ("rendimento", "kg/ha")}
    loc = d["Unidade da Federação"].fillna("NE")
    out = pd.DataFrame({
        "data": pd.to_datetime(d["Mês"], format="%Y%m"),
        "uf": loc.map(lambda x: UF_SIG.get(int(x), x) if x != "NE" else "NE"),
        "produto": d["Produto das lavouras"].map(nomes),
        "variavel": d["Variável"].map(lambda v: var[v][0]),
        "valor": d["valor"],
        "unidade": d["Variável"].map(lambda v: var[v][1]),
    })
    out["fonte"] = "IBGE LSPA (SIDRA 6588): estimativa feita no mes 'data' para a safra do ano civil de 'data'"
    out.to_parquet(DERIV / "ibge_ne_lspa_uf_mensal.parquet")
    print("lspa", out.shape, out.data.min(), out.data.max(), flush=True)


if __name__ == "__main__":
    for e in sys.argv[1:] or ["referencia", "censo", "ppm", "lspa", "pam"]:
        globals()[e]()
