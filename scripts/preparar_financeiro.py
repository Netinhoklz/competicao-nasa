"""Preparação do estudo financeiro do protótipo QUADRA (notebooks/estudo_financeiro.ipynb).

Etapas (rodar todas ou só as nomeadas):
  python -I -X utf8 scripts/preparar_financeiro.py [sidra] [ipca] [conab] [painel]

- sidra  : IBGE PAM municipal (SIDRA, tabela 1612) de amendoim, mamona e girassol nos 1.794 municípios do NE,
           1998–2025; variáveis 109 área plantada, 216 área colhida, 214 produção, 112 rendimento, 215 valor.
           As outras culturas (milho, feijão, mandioca, sorgo, algodão herbáceo) já estão em
           derivados/ibge_ne_pam_mun_anual.parquet.
- ipca   : IPCA mensal do Banco Central (SGS 433) -> índice mensal, média anual e fator para R$ de 2025.
- conab  : séries históricas de custo de produção da CONAB (www.gov.br/conab, TLS verificado) e extração das
           folhas do Nordeste: local, safra, sistema, produtividade, data dos preços, custo variável, operacional e total.
- painel : painel município × cultura × ano (1998–2025) com rendimento por ha plantado e colhido, preço implícito
           (valor ÷ produção) e receita por ha, em R$ de 2025.

Saídas: E:/campeonato-nasa/dados/financeiro/ (MANIFESTO.json via comum.registrar_manifesto).
"""
import json
import re
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from comum import DADOS, DERIV, pasta, registrar_manifesto, sessao_http  # noqa: E402

warnings.filterwarnings("ignore")
OUT = pasta("financeiro")
BRUTOS = OUT / "brutos"
S = sessao_http(retries=6)
UFS = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
ANOS = range(1998, 2026)
# SIDRA 1612, classificação 81 (metadados: servicodados.ibge.gov.br/api/v3/agregados/1612/metadados)
PRODUTOS_NOVOS = {2691: "Amendoim", 2707: "Mamona", 109179: "Girassol"}
VARS = {109: "area_plantada_ha", 216: "area_colhida_ha", 214: "producao_t", 112: "rendimento_kg_ha", 215: "valor_mil_moeda"}
CONAB = "https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/custos-de-producao/arquivos-custo-de-producao/agricolas/"
CONAB_ARQ = {  # arquivo -> cultura (página "Planilhas de custos de produção > Agrícolas", consultada em 14/11/2026)
    "feijao/feijao_1_safra_serie_historica-1998-2026.xls": "Feijão 1ª safra",
    "feijao/feijao_2_e_3_safras_serie_historica_2013-2026.xls": "Feijão 2ª e 3ª safras",
    "milho/milho_1a_safra_serie_historica_1997-2026.xls": "Milho 1ª safra",
    "milho/milho_2a_safra_serie_historica_2005-2026.xls": "Milho 2ª safra",
    "copy2_of_seriehistoricacustosmandioca2003a2026.xls": "Mandioca",
    "serie-historica-custos-amendoim-2005-a-2024.xls": "Amendoim",
    "serie-historica-custos-girassol-1a-e-2a-safras-2013-a-2024.xls": "Girassol",
    "serie-historica-custos-mamona-2008-a-2025.xlsx": "Mamona",
    "seriehistoricacustossorgo2013a2026.xls": "Sorgo",
    "serie-historica-custos-algodao-em-pluma-1998-a-2026.xlsx": "Algodão",
}


def pedir_json(url, arq):
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
        except Exception as e:  # conexão interrompida
            erro = repr(e)[:200]
        time.sleep(5 * (t + 1))
    raise RuntimeError(f"{url} -> {erro}")


# ---------------------------------------------------------------- SIDRA
def sidra():
    cache = BRUTOS / "sidra_1612"
    cache.mkdir(parents=True, exist_ok=True)
    anos = ",".join(str(a) for a in ANOS)
    tarefas = [(p, v, uf) for p in PRODUTOS_NOVOS for v in VARS for uf in UFS]  # 3 × 5 × 9 = 135 consultas (≤ 12 mil valores cada)

    def uma(t):
        p, v, uf = t
        url = f"https://apisidra.ibge.gov.br/values/t/1612/n6/in%20n3%20{uf}/v/{v}/p/{anos}/c81/{p}?formato=json"
        js = pedir_json(url, cache / f"p{p}_v{v}_uf{uf}.json")
        df = pd.DataFrame(js[1:]).rename(columns=js[0])
        return df.assign(produto_cod=p, var=v)

    with ThreadPoolExecutor(4) as ex:
        dfs = list(ex.map(uma, tarefas))
    df = pd.concat(dfs, ignore_index=True)
    df = df.rename(columns={"Município (Código)": "cod_mun", "Ano": "ano", "Valor": "valor_txt"})
    # SIDRA: "-" = zero absoluto; ".." não se aplica; "..." não disponível; "X" sigilo
    df["valor"] = pd.to_numeric(df.valor_txt.where(df.valor_txt != "-", "0"), errors="coerce")
    df["ano"] = df.ano.astype(int)
    df["produto"] = df.produto_cod.map(PRODUTOS_NOVOS)
    df["variavel"] = df["var"].map(VARS)
    w = df.pivot_table(index=["cod_mun", "produto", "ano"], columns="variavel", values="valor", aggfunc="first").reset_index()
    w.columns.name = None
    w["uf"] = w.cod_mun.str[:2].map(UFS)
    w["tipo"] = "temporaria"
    w.to_parquet(OUT / "pam_ne_amendoim_mamona_girassol.parquet")
    print("sidra:", len(w), "linhas;", w.cod_mun.nunique(), "municípios;",
          w.groupby("produto").area_plantada_ha.sum().round().to_dict(), flush=True)
    registrar_manifesto("financeiro", {"sidra_1612": {
        "fonte": "IBGE PAM, API SIDRA, tabela 1612 (lavouras temporárias)",
        "url": "https://apisidra.ibge.gov.br/values/t/1612/n6/in n3 {UF}/v/{109,216,214,112,215}/p/1998..2025/c81/{2691,2707,109179}",
        "produtos": {str(k): v for k, v in PRODUTOS_NOVOS.items()}, "variaveis": {str(k): v for k, v in VARS.items()},
        "recorte": "municípios das 9 UFs do Nordeste", "periodo": f"{min(ANOS)}-{max(ANOS)}",
        "unidade_valor": "Mil Reais (1994 a 2025)", "linhas": len(w), "arquivo": "pam_ne_amendoim_mamona_girassol.parquet"}})


# ---------------------------------------------------------------- IPCA
def ipca():
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
    arq = BRUTOS / "bcb_sgs433.json"
    arq.parent.mkdir(parents=True, exist_ok=True)
    if arq.exists():
        arq.unlink()  # sempre a série mais nova
    js = pedir_json(url, arq)
    d = pd.DataFrame(js)
    d["data"] = pd.to_datetime(d.data, format="%d/%m/%Y")
    d["var_pct"] = d.valor.astype(float)
    d = d[d.data >= "1994-07-01"].sort_values("data").reset_index(drop=True)  # Plano Real
    d["indice"] = (1 + d.var_pct / 100).cumprod()
    base = d[d.data.dt.year == 2025].indice.mean()
    d["fator_r2025"] = base / d.indice
    d[["data", "var_pct", "indice", "fator_r2025"]].to_csv(OUT / "ipca_mensal.csv", index=False)
    a = d.groupby(d.data.dt.year).agg(indice_medio=("indice", "mean"), meses=("indice", "size")).reset_index().rename(columns={"data": "ano"})
    a["fator_r2025"] = base / a.indice_medio
    a.to_csv(OUT / "ipca_anual.csv", index=False)
    print("ipca:", d.data.min().date(), "a", d.data.max().date(), "| fator 2010:", round(a.set_index("ano").fator_r2025[2010], 3),
          "| fator 2015:", round(a.set_index("ano").fator_r2025[2015], 3), flush=True)
    registrar_manifesto("financeiro", {"ipca": {
        "fonte": "Banco Central do Brasil, SGS 433 (IPCA, variação mensal %)", "url": url,
        "base": "média dos índices mensais de 2025 = R$ de 2025", "periodo": f"{d.data.min().date()} a {d.data.max().date()}",
        "arquivos": ["ipca_mensal.csv", "ipca_anual.csv"]}})


# ---------------------------------------------------------------- CONAB
def _num(x):
    try:
        v = float(x)
        return None if np.isnan(v) else v
    except (TypeError, ValueError):
        return None


MESES_PT = {m: i + 1 for i, m in enumerate(["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO",
                                             "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"])}


# componentes do custeio; "mão de obra" inclui a gestão da propriedade familiar (layout antigo) e o administrador (novo)
COMPONENTES = {"mao_de_obra_r_ha": r"M[ÃA]O[- ]DE[- ]OBRA|GEST[ÃA]O DA PROPRIEDADE|ADMINISTRADOR",
               "sementes_r_ha": r"SEMENTE|MANIVA|MUDAS",
               "fertilizantes_r_ha": r"FERTILIZ",
               "agrotoxicos_r_ha": r"AGROT|DEFENSIV",
               "maquinas_animais_r_ha": r"M[ÁA]QUINA|ANIMA|AVI[ÃA]O|TRATOR"}


def _num_br(s):
    """'14850,00' ou '1.500,00' -> float."""
    s = s.strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return float(s)


def _ler_folha(df):
    """Extrai os campos de uma planilha de custo da CONAB. Há dois layouts (antigo: rótulo na 1ª coluna; 'Resumo' novo:
    rótulo em qualquer coluna). Regra: o rótulo é o 1º texto da linha; o R$/ha é o 1º número à direita dele."""
    out, cab = {}, []
    for i in range(len(df)):
        lin = df.iloc[i].tolist()
        textos = [(j, str(x).replace("\n", " ").replace("\t", " ").strip()) for j, x in enumerate(lin) if isinstance(x, str) and str(x).strip()]
        if not textos:
            continue
        j0, rot = textos[0]
        ru = rot.upper()
        junto = " ".join(t for _, t in textos)
        ju = junto.upper()
        val = next((_num(x) for x in lin[j0 + 1:] if _num(x) is not None), None)
        if i < 8:
            cab.append(junto)
        if "PRODUTIVIDADE" in ru and "produtividade_kg_ha" not in out:
            m = re.search(r"(\d[\d\.]*,\d+|\d+(?:\.\d+)?)\s*(kg|t|sc|sacas?)\s*/\s*ha", junto, re.I)
            if m:
                v, u = _num_br(m.group(1)), m.group(2).lower()
            else:
                v, u = val, next((t for _, t in textos[1:] if "/HA" in t.upper()), "kg/ha").split("/")[0].lower()
            out["produtividade_kg_ha"] = None if v is None else v * (1000 if u == "t" else 1)
            out["produtividade_unid_original"] = u
        if "LOCAL:" in ru and "local" not in out:
            out["local"] = rot.split(":", 1)[-1].strip()
        m = re.search(r"SAFRA\s*-\s*(\d{4}/\d{2,4})\s*-\s*(.+)$", junto, re.I)
        if m and "local" not in out:
            out["safra"], out["local"] = m.group(1), m.group(2).strip()
        elif "SAFRA DE" in ju and "safra" not in out:
            m2 = re.search(r"\d{4}/\d{2,4}", junto)
            out["safra"] = m2.group(0) if m2 else None
        m = re.search(r"MÊS/ANO:\s*([A-ZÇ]+)\s*/\s*(\d{4})", ju)
        if m and m.group(1) in MESES_PT and "data_precos" not in out:
            out["data_precos"] = pd.Timestamp(int(m.group(2)), MESES_PT[m.group(1)], 1)
        if "PREÇOS DE" in ju and "data_precos" not in out:
            for x in lin:
                if hasattr(x, "year") and not isinstance(x, str):
                    out["data_precos"] = pd.Timestamp(x)
                    break
        if "TOTAL DAS DESPESAS DE CUSTEIO" in ru:
            out["custeio_r_ha"] = val
        elif ru.startswith("CUSTO VARI"):
            out["custo_variavel_r_ha"] = val
        elif ru.startswith("CUSTO OPERACIONAL"):
            out["custo_operacional_r_ha"] = val
        elif ru.startswith("CUSTO TOTAL"):
            out["custo_total_r_ha"] = val
        elif "custo_variavel_r_ha" not in out:  # componentes, só dentro do custeio (antes do custo variável)
            for chave, padrao in COMPONENTES.items():
                if re.search(padrao, ru):
                    out[chave] = (out.get(chave) or 0) + (val or 0)
                    break
    out["cabecalho"] = " | ".join(cab)
    return out


def conab():
    d = BRUTOS / "conab"
    d.mkdir(parents=True, exist_ok=True)
    linhas, baixados = [], {}
    for rel, cultura in CONAB_ARQ.items():
        arq = d / rel.split("/")[-1]
        for t in range(8):  # o gov.br corta conexões longas; tenta de novo
            if arq.exists():
                break
            try:
                r = S.get(CONAB + rel, timeout=300)  # sessão com verificação TLS (comum.CA_BUNDLE)
                r.raise_for_status()
                arq.write_bytes(r.content)
            except Exception as e:
                print("  nova tentativa:", arq.name, repr(e)[:100], flush=True)
                time.sleep(5 * (t + 1))
        baixados[arq.name] = {"url": CONAB + rel, "bytes": arq.stat().st_size}
        x = pd.ExcelFile(arq, engine="xlrd" if arq.suffix == ".xls" else "openpyxl")
        for sh in x.sheet_names:
            m = re.search(r"-(MA|PI|CE|RN|PB|PE|AL|SE|BA)-?(\d{4})?", sh)
            if not m:
                continue
            try:
                info = _ler_folha(x.parse(sh, header=None))
            except Exception as e:  # folha fora do padrão
                info = {"erro": repr(e)[:120]}
            info.update(arquivo=arq.name, cultura_arquivo=cultura, folha=sh, uf=m.group(1),
                        ano_folha=int(m.group(2)) if m.group(2) else None)
            linhas.append(info)
        print("conab:", arq.name, "folhas do NE:", sum(1 for l in linhas if l["arquivo"] == arq.name), flush=True)
    C = pd.DataFrame(linhas)
    cab = C.cabecalho.fillna("").str.upper()
    C["familiar"] = cab.str.contains("FAMILIAR")
    C["irrigado"] = cab.str.contains("IRRIGAD")
    C["sistema"] = np.where(C.familiar, "agricultura familiar", "empresarial") + np.where(C.irrigado, ", irrigado", ", sequeiro")
    # deflator: mês dos preços da planilha; sem data, o mês de abril do ano da folha (aproximação marcada)
    ip = pd.read_csv(OUT / "ipca_mensal.csv", parse_dates=["data"]).set_index("data").fator_r2025
    C["data_precos_aprox"] = C.data_precos.isna()
    dp = C.data_precos.where(C.data_precos.notna(), pd.to_datetime(C.ano_folha.astype("Int64").astype(str) + "-04-01", errors="coerce"))
    C["mes_precos"] = dp.dt.to_period("M").dt.to_timestamp()
    C["fator_r2025"] = C.mes_precos.map(ip)
    for c in ["custeio_r_ha", "custo_variavel_r_ha", "custo_operacional_r_ha", "custo_total_r_ha", *COMPONENTES]:
        C[c + "_r2025"] = C[c] * C.fator_r2025
    # desembolso = custo operacional sem a mão de obra (a família usa a própria) — mesma planilha, sem suposição nova
    C["desembolso_r_ha_r2025"] = C.custo_operacional_r_ha_r2025 - C.mao_de_obra_r_ha_r2025.fillna(0)
    C.to_csv(OUT / "conab_custos_ne.csv", index=False)
    print(C.groupby(["cultura_arquivo", "sistema"]).size().to_string(), flush=True)
    registrar_manifesto("financeiro", {"conab_custos": {
        "fonte": "CONAB, Planilhas de custos de produção, séries históricas (agrícolas)",
        "pagina": "https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/custos-de-producao/planilhas-de-custos-de-producao/copy_of_agricolas",
        "consultado_em": "2026-11-14", "tls": "verificado (sessao_http com CA_BUNDLE)", "arquivos": baixados,
        "extracao": "só folhas com UF do Nordeste no nome; R$/ha da 1ª coluna numérica; deflator = IPCA do mês dos preços da planilha",
        "saida": "conab_custos_ne.csv", "folhas_ne": len(C)}})


# ---------------------------------------------------------------- painel
def painel():
    base = pd.read_parquet(DERIV / "ibge_ne_pam_mun_anual.parquet")
    base = base[base.produto.isin(["Milho", "Feijão", "Mandioca", "Sorgo", "Algodão herbáceo"])]
    novos = pd.read_parquet(OUT / "pam_ne_amendoim_mamona_girassol.parquet")
    P = pd.concat([base, novos[base.columns]], ignore_index=True)
    P = P[P.ano.isin(ANOS)].copy()
    ipa = pd.read_csv(OUT / "ipca_anual.csv").set_index("ano").fator_r2025
    P["fator_r2025"] = P.ano.map(ipa)
    P["valor_r2025"] = P.valor_mil_moeda * 1000 * P.fator_r2025
    ok_p = P.area_plantada_ha > 0
    ok_c = P.area_colhida_ha > 0
    P["rend_plantado_kg_ha"] = np.where(ok_p, P.producao_t * 1000 / P.area_plantada_ha.where(ok_p), np.nan)
    P["rend_colhido_kg_ha"] = np.where(ok_c, P.producao_t * 1000 / P.area_colhida_ha.where(ok_c), np.nan)
    P["perda_area"] = np.where(ok_p, 1 - P.area_colhida_ha / P.area_plantada_ha.where(ok_p), np.nan)
    P["preco_r2025_kg"] = np.where(P.producao_t > 0, P.valor_r2025 / (P.producao_t * 1000).where(P.producao_t > 0), np.nan)
    P["receita_plantado_r2025_ha"] = np.where(ok_p, P.valor_r2025 / P.area_plantada_ha.where(ok_p), np.nan)
    P["receita_colhido_r2025_ha"] = np.where(ok_c, P.valor_r2025 / P.area_colhida_ha.where(ok_c), np.nan)
    P = P.drop(columns=["valor_mil_moeda", "rendimento_kg_ha"])
    P.to_parquet(OUT / "painel_mun_cultura_ano.parquet")
    print("painel:", len(P), "linhas;", P.cod_mun.nunique(), "municípios;", P.produto.nunique(), "culturas;",
          f"{P.ano.min()}–{P.ano.max()}", flush=True)
    registrar_manifesto("financeiro", {"painel": {
        "arquivo": "painel_mun_cultura_ano.parquet",
        "fontes": ["derivados/ibge_ne_pam_mun_anual.parquet (milho, feijão, mandioca, sorgo, algodão herbáceo)",
                   "pam_ne_amendoim_mamona_girassol.parquet (SIDRA 1612)", "ipca_anual.csv"],
        "periodo": f"{P.ano.min()}-{P.ano.max()}", "moeda": "R$ de 2025 (IPCA, média anual)",
        "colunas": list(P.columns)}})


if __name__ == "__main__":
    etapas = sys.argv[1:] or ["sidra", "ipca", "conab", "painel"]
    for e in etapas:
        t0 = time.time()
        {"sidra": sidra, "ipca": ipca, "conab": conab, "painel": painel}[e]()
        print(f"[{e}] {time.time() - t0:.0f}s", flush=True)
