"""v3 - Analista IBGE/Nordeste: baixa recortes do IBGE para os 9 estados do Nordeste.

Bases (API SIDRA apisidra.ibge.gov.br, formato /f/c = so codigos; API de localidades e malhas servicodados.ibge.gov.br;
geoftp para a lista oficial do Semiarido):
  - Censo Agropecuario 2017: 6880 (praticas agricolas x tipologia x atividade, n. e area), 6855 (preparo do solo,
    plantio direto, cultivo minimo), 6857 (irrigacao por metodo), 6846 (pratica x orientacao tecnica), 6847 (adubacao),
    6861 (recursos hidricos: pocos, cisternas), 6958 (lavoura temporaria por tipo de semente: guardada x comprada)
  - PAM 1612/1613 (milho, feijao, mandioca, sorgo, algodao herbaceo e arboreo, castanha de caju) 1974-2025; 839 e 1002
    (milho 1a/2a safra, feijao 1a/2a/3a safra) 2003-2025
  - PPM 3939 (bovino, caprino, ovino, suino, galinaceos, equino) 1974-2025
  - LSPA 6588 (estimativa mensal da safra por UF, 2006-09 -> ultimo mes)
  - Municipios do NE com regiao imediata/intermediaria; malhas GeoJSON; Semiarido 2005, 2017, 2021, 2022.
Saida: E:/campeonato-nasa/dados/ibge_nordeste/*.parquet (+ GeoJSON, planilhas), MANIFESTO.json.
O JSON bruto fica em cache_json/ durante o download e e apagado no fim (o parquet guarda tudo).
Codigos SIDRA: "-" = zero absoluto; ".." = nao se aplica; "..." = nao disponivel; "X" = sigilo (vira NaN).
"""
import json
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
OUT = DADOS / "ibge_nordeste"
OUT.mkdir(parents=True, exist_ok=True)
CACHE = OUT / "cache_json"
CACHE.mkdir(exist_ok=True)
S = sessao_http(retries=6)
UFS = [21, 22, 23, 24, 25, 26, 27, 28, 29]
SIDRA = "https://apisidra.ibge.gov.br/values"


def pedir(url, arq):
    if arq.exists():
        return json.loads(arq.read_text(encoding="utf-8"))
    erro = None
    for t in range(8):
        try:
            r = S.get(url, timeout=300)
            if r.status_code == 200:
                arq.write_text(r.text, encoding="utf-8")
                return r.json()
            erro = f"HTTP {r.status_code} {r.text[:200]}"
        except Exception as e:  # conexao interrompida
            erro = repr(e)[:200]
        time.sleep(5 * (t + 1))
    raise RuntimeError(f"{url} -> {erro}")


def para_df(js):
    cab, linhas = js[0], js[1:]
    df = pd.DataFrame(linhas)
    if df.empty:
        return df
    ren = {}
    for k, nome in cab.items():
        n = nome.replace(" (Código)", "")
        ren[k] = {"Valor": "valor_txt", "Nível Territorial": "nivel", "Unidade de Medida": "cod_unidade"}.get(n, n)
    return df.rename(columns=ren)


def consulta(tab, terr, v, p, cls, nome):
    """cls: lista de (cod_classificacao, categorias). terr: trecho territorial (ex. 'n6/in n3 23')."""
    c = "".join(f"/c{k}/{cats}" for k, cats in cls)
    url = f"{SIDRA}/t/{tab}/{terr.replace(' ', '%20')}/v/{v}/p/{p}{c}/f/c/d/m?formato=json"
    df = para_df(pedir(url, CACHE / f"{nome}.json"))
    df["tabela"] = tab
    return df


def valor_num(df):
    df["valor"] = pd.to_numeric(df["valor_txt"].where(df["valor_txt"] != "-", "0"), errors="coerce")
    return df


def rodar(tarefas, n=3):
    with ThreadPoolExecutor(n) as ex:
        dfs = list(ex.map(lambda a: consulta(*a), tarefas))
    return valor_num(pd.concat([d for d in dfs if len(d)], ignore_index=True))


# ---------------- Censo Agropecuario 2017 ----------------
TIP = (829, "46302,46304")  # total e agricultura familiar - sim


def censo():
    t = []
    for uf in UFS:
        t.append((6880, f"n6/in n3 {uf}", "183,184", "2017",
                  [TIP, (12517, "113601,111519"), (12568, "all"), (220, "110085")], f"ca6880_{uf}"))
        t.append((6857, f"n6/in n3 {uf}", "2372,2373", "2017",
                  [TIP, (12604, "all"), (12564, "41145"), (12771, "45951"), (309, "10969")], f"ca6857_{uf}"))
        t.append((6846, f"n6/in n3 {uf}", "183", "2017",
                  [TIP, (12568, "113197,112677,112764,112767"), (12598, "41141"),
                   (12567, "41151,113111,112647,112648,113559"), (220, "110085")], f"ca6846_{uf}"))
        for g, prods in enumerate(["113869,4888,4907", "111677,111676,111675", "4869,4885,4897",
                                   "111672,4909,4910"]):
            t.append((6958, f"n6/in n3 {uf}", "10084,10085,10089", "2017",
                      [TIP, (226, prods), (12550, "all"), (12523, "47127")], f"ca6958_{uf}_{g}"))
    t.append((6855, "n6/in n2 2", "9562,9563,9564,9565,2016,2018", "2017",
              [TIP, (12564, "41145"), (12771, "45951"), (218, "46502")], "ca6855"))
    t.append((6847, "n6/in n2 2", "183", "2017",
              [TIP, (12522, "all"), (12564, "41145"), (12771, "45951"), (800, "41147"), (837, "46544")], "ca6847"))
    t.append((6861, "n6/in n2 2", "2324", "2017",
              [TIP, (12482, "all"), (12517, "113601"), (220, "110085")], "ca6861"))
    df = rodar(t)
    df.to_parquet(OUT / "censo2017_ne_municipios_bruto.parquet")
    print("censo ok", len(df), flush=True)
    return df


# ---------------- PAM ----------------
PAM = {1612: ("109,216,214,112,215", 81, ["2689", "2702", "2708", "2711", "2714"]),
       1613: ("2313,216,214,112,215", 82, ["2725", "2718"])}


def blocos(a0, a1, passo):
    return [f"{a}-{min(a + passo - 1, a1)}" for a in range(a0, a1 + 1, passo)]


def pam():
    t = []
    for tab, (vs, c, prods) in PAM.items():
        for pr in prods:
            for per in blocos(1974, 2025, 5):
                t.append((tab, "n6/in n2 2", vs, per, [(c, pr)], f"pam{tab}_{pr}_{per}"))
    for per in blocos(2003, 2025, 2):
        t.append((839, "n6/in n2 2", "109,216,214,112", per, [(81, "114253,114254")], f"pam839_{per}"))
        t.append((1002, "n6/in n2 2", "109,216,214,112", per, [(81, "117991,117992,117993")], f"pam1002_{per}"))
    df = rodar(t)
    df.to_parquet(OUT / "pam_ne_municipios_bruto.parquet")
    print("pam ok", len(df), flush=True)
    return df


def ppm():
    t = [(3939, "n6/in n2 2", "105", per, [(79, "2670,2681,2677,32794,32796,2672")], f"ppm3939_{per}")
         for per in blocos(1974, 2025, 4)]
    df = rodar(t)
    df.to_parquet(OUT / "ppm_ne_municipios_bruto.parquet")
    print("ppm ok", len(df), flush=True)
    return df


def lspa():
    prods = "39429,39436,39437,39438,39441,39442,39444,39457,39467,0"
    t = []
    for v in ("109", "216", "35", "36"):
        t.append((6588, "n3/in n2 2", v, "all", [(48, prods)], f"lspa_uf_{v}"))
        t.append((6588, "n2/2", v, "all", [(48, prods)], f"lspa_ne_{v}"))
    df = rodar(t)
    df.to_parquet(OUT / "lspa_ne_uf_mensal_bruto.parquet")
    print("lspa ok", len(df), flush=True)
    return df


# ---------------- Territorio ----------------
def territorio():
    loc = S.get("https://servicodados.ibge.gov.br/api/v1/localidades/regioes/2/municipios", timeout=120).json()
    (OUT / "localidades_municipios_ne.json").write_text(json.dumps(loc, ensure_ascii=False), encoding="utf-8")
    linhas = []
    for m in loc:
        ri = m.get("regiao-imediata") or {}
        rint = ri.get("regiao-intermediaria") or {}
        mi = m.get("microrregiao") or {}
        me = mi.get("mesorregiao") or {}
        uf = (me.get("UF") or rint.get("UF") or {})
        linhas.append({"cod_mun": str(m["id"]), "municipio": m["nome"], "uf": uf.get("sigla"),
                       "cod_uf": str(uf.get("id")), "cod_rgi": str(ri.get("id")), "regiao_imediata": ri.get("nome"),
                       "cod_rgint": str(rint.get("id")), "regiao_intermediaria": rint.get("nome"),
                       "cod_micro": str(mi.get("id")), "microrregiao": mi.get("nome"),
                       "cod_meso": str(me.get("id")), "mesorregiao": me.get("nome")})
    ref = pd.DataFrame(linhas)
    base = "https://servicodados.ibge.gov.br/api/v3/malhas/regioes/2?formato=application/vnd.geo%2Bjson&qualidade="
    # para uma regiao a API so aceita UF/mesorregiao/microrregiao/municipio: as regioes imediatas e
    # intermediarias saem da dissolucao dos municipios pelo codigo da API de localidades
    for intra, q in (("municipio", "intermediaria"), ("UF", "intermediaria")):
        r = S.get(base + q + "&intrarregiao=" + intra, timeout=300)
        r.raise_for_status()
        (OUT / f"malha_ne_{intra}.geojson").write_bytes(r.content)
    import geopandas as gpd
    g = gpd.read_file(OUT / "malha_ne_municipio.geojson").rename(columns={"codarea": "cod_mun"})
    g = g.merge(ref, on="cod_mun", how="left")
    g["geometry"] = g.geometry.make_valid()  # a malha simplificada tem autointersecoes
    for cod, nome, arq in (("cod_rgi", "regiao_imediata", "regiao-imediata"),
                           ("cod_rgint", "regiao_intermediaria", "regiao-intermediaria")):
        g[[cod, nome, "uf", "geometry"]].dissolve(by=[cod, nome, "uf"]).reset_index().to_file(
            OUT / f"malha_ne_{arq}.geojson", driver="GeoJSON")
    geo = "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/semiarido_brasileiro/"
    arqs = {"semiarido_2022.xlsx": "Situacao_2022/lista_municipios_Semiarido_2022.xlsx",
            "semiarido_2021.xls": "Situacao_2021/lista_municipios_Semiarido_2021.xls",
            "semiarido_2017.xlsx": "Situacao_23nov2017/lista_municipios_Semiarido_2017_11_23.xlsx",
            "semiarido_2005.xls": "Situacao_2005a2017/lista_municipios_semiarido.xls",
            "semiarido_resolucao115_2017.pdf": "Situacao_23nov2017/resolucao115_23112017_delimitacaodosemiarido_DOU.pdf"}
    for dest, rel in arqs.items():
        baixar(geo + rel, OUT / "semiarido" / dest, S)
    ref.to_parquet(OUT / "municipios_ne_referencia_sem_semiarido.parquet")
    print("territorio ok", len(ref), flush=True)
    return ref


if __name__ == "__main__":
    t0 = time.time()
    etapas = sys.argv[1:] or ["territorio", "censo", "lspa", "ppm", "pam"]
    for e in etapas:
        globals()[e]()
        print(e, round((time.time() - t0) / 60, 1), "min", flush=True)
    if set(etapas) >= {"territorio", "censo", "lspa", "ppm", "pam"}:
        shutil.rmtree(CACHE, ignore_errors=True)
    registrar_manifesto("ibge_nordeste", {
        "fonte": "IBGE: Censo Agropecuario 2017, PAM, PPM, LSPA (API SIDRA, formato /f/c); localidades e malhas "
                 "(servicodados.ibge.gov.br); lista oficial do Semiarido (geoftp.ibge.gov.br)",
        "script": "conselho/analises/v3_ibge_baixar_nordeste.py",
        "recorte": "1794 municipios do Nordeste (n6 in n2 2) e 9 UFs; Censo pedido por UF",
        "tabelas_sidra": {"censo2017": [6880, 6855, 6857, 6846, 6847, 6861, 6958], "pam": [1612, 1613, 839, 1002],
                          "ppm": [3939], "lspa": [6588]},
        "codigos_sidra": "'-' = zero; '..' nao se aplica; '...' nao disponivel; 'X' sigilo -> NaN",
        "arquivos": {f.name: f.stat().st_size for f in OUT.rglob("*") if f.is_file() and "cache_json" not in str(f)},
    }, base=OUT)
    print("FIM", round((time.time() - t0) / 60, 1), "min", flush=True)
