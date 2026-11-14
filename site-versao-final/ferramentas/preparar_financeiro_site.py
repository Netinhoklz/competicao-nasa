"""Gera site-versao-final/dados/financeiro_mun.json: o valor da colheita por município (milho, feijão, mandioca), em
R$ de 2025 por ha plantado, para o passo "Quanto rende" refazer o plano nos anos que já aconteceram (decisão 7 do
PLANO_INTEGRACAO.md; contrato na seção 3 de analise/financeiro.md).

Origem das regras (portadas sem mudança de método):
- limpeza do PAM, preço de referência e R = rendimento × preço: notebooks/secoes_financeiro/00_intro.py:191-235;
- custo da CONAB (semente, desembolso, operacional; Crateús-CE no milho; correção Giral→Girau): 05_custo.py:29-66;
- cartões, lacunas pela mesorregião e teste fora da amostra: ferramentas/origem_analise/financeiro/fin.py e fin3.py.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_financeiro_site.py
O módulo também é importado por preparar_projecao.py (preço de referência e custo iguais nas duas telas)."""
import datetime
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path("E:/campeonato-nasa/dados")
DERIV = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados")
F = DADOS / "financeiro"
SAIDA = RAIZ / "dados" / "financeiro_mun.json"
CULT = ["Milho", "Feijão", "Mandioca"]
ANOS = list(range(1998, 2026))
AREA_MIN, ANOS_MIN = 10, 10
PRECO_REF = range(2016, 2026)
UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
# ciclo central e faixa em dias (00_intro.py:100-109), só para o R$ por ha-mês
CICLO = {"Feijão": (70, 60, 75), "Milho": (110, 100, 120), "Mandioca": (456, 365, 548)}

EVT = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
EN = sorted(int(a) for a in EVT[(EVT.ONI_OND_NDJ >= 1.5) & EVT.quadra_afetada.between(1998, 2025)].quadra_afetada)
assert EN == [1998, 2010, 2016, 2024], EN


def painel():
    """B = município-anos com ≥ 10 ha plantados das 3 culturas, com normal, quebra, preço de referência e R."""
    P = pd.read_parquet(F / "painel_mun_cultura_ano.parquet")
    P = P[P.produto.isin(CULT)].copy()
    P["uf"] = P.cod_mun.str[:2].map(UF)
    B = P[P.area_plantada_ha >= AREA_MIN].copy()

    def mediana_outros(s):
        v = s.to_numpy()
        if len(v) < 2:
            return pd.Series(np.nan, index=s.index)
        return pd.Series([np.median(np.delete(v, i)) for i in range(len(v))], index=s.index)

    B["normal_kg_ha"] = B.groupby(["cod_mun", "produto"]).rend_plantado_kg_ha.transform(mediana_outros)
    B["quebra"] = B.rend_plantado_kg_ha / B.normal_kg_ha < 0.5
    B["n_anos"] = B.groupby(["cod_mun", "produto"]).ano.transform("size")
    pr = B.preco_r2025_kg.where(B.producao_t >= 1)
    B["preco"] = pr.where((pr / pr.groupby([B.uf, B.produto, B.ano]).transform("median")).between(0.25, 4))
    return B


def precos_ref(B):
    """Preço de referência (R$ de 2025/kg) = mediana 2016–2025 do preço implícito limpo do município (≥ 3 anos);
    sem isso, a da UF; sem isso, a do NE. Devolve (função cod, produto -> (preço, origem), tabela da UF)."""
    jan = B[B.ano.isin(PRECO_REF)]
    pm = jan.groupby(["cod_mun", "produto"]).preco.agg(["median", "count"])
    pm = pm[pm["count"] >= 3]["median"].to_dict()
    pu = jan.groupby(["uf", "produto"]).preco.median().to_dict()
    pn = jan.groupby("produto").preco.median().to_dict()

    def preco(cod, prod):
        if (cod, prod) in pm:
            return float(pm[(cod, prod)]), "município"
        if (UF[cod[:2]], prod) in pu and not np.isnan(pu[(UF[cod[:2]], prod)]):
            return float(pu[(UF[cod[:2]], prod)]), "UF"
        return float(pn[prod]), "NE"

    return preco, jan


def custos():
    """Custo da CONAB em R$ de 2025/ha (05_custo.py:29-66). Sorgo = suposição: lavoura anual manual do NE."""
    C = pd.read_csv(F / "conab_custos_ne.csv", parse_dates=["mes_precos"])
    C["lugar"] = C.folha.str.rsplit("-", n=1).str[0].str.replace("Giral do Ponciano", "Girau do Ponciano")
    C["produto"] = C.cultura_arquivo.map({"Feijão 1ª safra": "Feijão", "Mandioca": "Mandioca", "Mamona": "Mamona", "Milho 1ª safra": "Milho"})
    crateus = (C.cultura_arquivo == "Milho 2ª safra") & C.lugar.str.startswith("Crateús")
    C.loc[crateus, "produto"] = "Milho"
    U = C[C.produto.notna() & ~C.irrigado & (C.familiar | crateus)].sort_values("ano_folha").groupby(["produto", "lugar"]).tail(5)
    loc = U.groupby(["produto", "lugar", "uf"]).agg(
        ate=("ano_folha", "max"), semente=("sementes_r_ha_r2025", "median"), desembolso=("desembolso_r_ha_r2025", "median"),
        custo_operacional=("custo_operacional_r_ha_r2025", "median")).reset_index()

    def central(g):
        rec = g[g.ate >= 2019]
        b = rec if len(rec) else g
        return {"semente": b.semente.median(), "desembolso": b.desembolso.median(), "operacional": b.custo_operacional.median(),
                "faixa_desembolso": [g.desembolso.min(), g.desembolso.max()], "locais": int(len(g))}

    CU = {p: central(g) for p, g in loc.groupby("produto")}
    cr = loc[(loc.produto == "Milho") & loc.lugar.str.startswith("Crateús")].iloc[0]
    CU["Milho"].update(semente=cr.semente, desembolso=cr.desembolso, operacional=cr.custo_operacional)
    CU["Milho"]["origem"] = "CONAB, Crateús-CE (teto: Carira-SE)"
    CU["Feijão"]["origem"] = f"CONAB, feijão da agricultura familiar do NE (mediana de {CU['Feijão']['locais']} locais)"
    CU["Mandioca"]["origem"] = f"CONAB, mandioca da agricultura familiar do NE (mediana de {CU['Mandioca']['locais']} locais)"
    CU["Sorgo forrageiro"] = central(loc[loc.produto.isin(["Feijão", "Mamona"]) | loc.lugar.str.startswith("Crateús")])
    CU["Sorgo forrageiro"]["origem"] = "suposição: lavoura anual manual do NE (CONAB: feijão, mamona e milho de Crateús)"
    out = {}
    for p, v in CU.items():
        if p == "Mamona":
            continue
        out[p] = {"semente": int(round(v["semente"])), "desembolso": int(round(v["desembolso"])), "operacional": int(round(v["operacional"])),
                  "faixa_desembolso": [int(round(x)) for x in v["faixa_desembolso"]], "origem": v["origem"],
                  "tipo": "suposição" if p == "Sorgo forrageiro" else "medido"}
    return out


def r0(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else int(round(float(x)))


def r2(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 2)


def main():
    REFM = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
    B = painel()
    preco, jan = precos_ref(B)
    B["preco_ref"] = [preco(c, p)[0] for c, p in zip(B.cod_mun, B.produto)]
    B["R"] = B.rend_plantado_kg_ha * B.preco_ref
    M = B[B.n_anos >= ANOS_MIN].copy()
    M["R_rel"] = M.R / M.groupby(["produto", "cod_mun"]).R.transform("median")
    M["meso"] = M.cod_mun.map(REFM.cod_meso)
    meso_rel = M.groupby(["produto", "meso", "ano"]).R_rel.median().to_dict()
    CU = custos()

    # teste fora da amostra (fin.py e fin3.py): faixa de 1998–2015 contra 2016–2025
    calib = {"p10_p90": {}, "min_max": {}}
    for p in CULT:
        c1, c2 = [], []
        for _, g in M[M.produto == p].groupby("cod_mun"):
            tr, te = g[g.ano <= 2015].R, g[g.ano >= 2016].R
            if len(tr) >= 8 and len(te) >= 5:
                c1.append(((te >= tr.quantile(.1)) & (te <= tr.quantile(.9))).mean())
                c2.append(((te >= tr.min()) & (te <= tr.max())).mean())
        calib["p10_p90"][p], calib["min_max"][p] = round(float(np.mean(c1)), 2), round(float(np.mean(c2)), 2)
    print("calibração fora da amostra:", calib)

    # preço da raiz por UF (fin2.py): mediana e P25 do preço limpo 2016–2025
    raiz_uf = jan[jan.produto == "Mandioca"].groupby("uf").preco.agg(mediana="median", p25=lambda s: s.quantile(.25)).to_dict("index")
    # repetição do rendimento (sinal de estimativa do agente do IBGE) e área recente
    S = B.sort_values(["produto", "cod_mun", "ano"])
    rep = (S.groupby(["produto", "cod_mun"]).rend_plantado_kg_ha.diff().abs() < 1e-6).groupby([S.produto, S.cod_mun]).mean()
    P = pd.read_parquet(F / "painel_mun_cultura_ano.parquet", columns=["cod_mun", "produto", "ano", "area_plantada_ha"])
    area_recente = P[(P.produto == "Mandioca") & (P.ano >= 2018) & (P.area_plantada_ha > 0)].groupby("cod_mun").area_plantada_ha.agg(list).to_dict()

    out = {"_meta": {
        "descricao": "Valor da colheita por município e cultura, R$ de 2025 (IPCA) por ha plantado; chave = código IBGE de 7 dígitos.",
        "tipo": {"medido": "rendimento por ha plantado (IBGE PAM 1998–2025) × preço de referência; custos da CONAB; anos de El Niño forte",
                 "suposição": "custo do sorgo forrageiro; ciclo das culturas (R$ por ha-mês); família padrão de 3 ha; preço da raiz escolhido",
                 "projeção": "nenhuma neste arquivo: o front refaz o plano nos anos já vistos (2027 entre os 4 El Niños fortes, 2028–29 entre os 28 anos)"},
        "regras": {"serie": f"≥ {ANOS_MIN} anos com ≥ {AREA_MIN} ha plantados (1998–2025)",
                   "preco_ref": "mediana 2016–2025 do preço implícito do município (≥ 3 anos, produção ≥ 1 t, 0,25–4× a mediana da UF no ano); sem isso a UF; sem isso o NE",
                   "R": "rendimento por ha plantado × preço de referência; perda total = 0",
                   "lacuna": "ano sem dado do município (ou com < 10 ha): mediana do município × razão ao normal mediana da mesorregião no ano (origem 'meso')",
                   "quebra": "rendimento < 0,5 × mediana dos outros anos do município",
                   "el_nino_forte": "mediana de R nos anos-quadra com ONI out–dez/nov–jan ≥ 1,5 que o município tem na série (mínimo 2)",
                   "equilibrio": "rend_kg_ha = desembolso ÷ preço; preco_kg = desembolso ÷ rendimento mediano"},
        "anos_el_nino_forte": EN,
        "calibracao_fora_da_amostra": {"faixa_p10_p90_cobriu": calib["p10_p90"], "min_max_cobriu": calib["min_max"],
                                       "teste": "faixa de 1998–2015 contra os anos 2016–2025 (meta 0,80)"},
        "sem_valor_rs": {"Sorgo forrageiro": "valor de uso (forragem), sem preço na base", "Palma forrageira": "idem",
                         "Gliricídia": "idem", "Guandu": "sem série municipal no PAM"},
        "fontes": ["IBGE PAM 1998–2025 (E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet)",
                   "CONAB, custos de produção do NE (conab_custos_ne.csv)", "NOAA ONI (el_nino_2026/eventos.csv)"],
        "script": "site-versao-final/ferramentas/preparar_financeiro_site.py",
        "gerado_em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}}

    sem = {p: 0 for p in CULT}
    for cod in REFM.index:
        uf = REFM.uf[cod]
        meso = REFM.cod_meso[cod]
        d = {"cod": cod, "municipio": REFM.municipio[cod], "uf": uf, "mesorregiao": REFM.mesorregiao[cod],
             "moeda": "R$ de 2025 (IPCA)", "base": "IBGE PAM 1998–2025; CONAB custos NE", "ultimo_ano_medido": 2025,
             "anos_el_nino_forte": EN, "culturas": {}, "custo_sorgo_forrageiro_ha": CU["Sorgo forrageiro"],
             "historico_R_ha": {"anos": ANOS}, "historico_kg_ha": {"anos": ANOS}}
        avisos = ["valor da colheita = vender ou comer, a preço da região; não é lucro", "forragem e Garantia-Safra fora da conta"]
        q = M[M.cod_mun == cod]
        for p in CULT:
            g = q[q.produto == p].sort_values("ano")
            if not len(g):
                sem[p] += 1
                d["culturas"][p] = None
                d["historico_R_ha"][p] = d["historico_kg_ha"][p] = d["historico_R_ha"]["origem_" + p] = None
                avisos.append(f"{p}: sem série no município (menos de {ANOS_MIN} anos com {AREA_MIN} ha ou mais no PAM 1998–2025)")
                continue
            pr, origem = preco(cod, p)
            R = g.R
            base = float(R.median())
            own = g.set_index("ano")
            hR, hk, ho = [], [], []
            for a in ANOS:
                if a in own.index:
                    v, o = float(own.R[a]), "mun"
                else:
                    rel = meso_rel.get((p, meso, a), np.nan)
                    v, o = (base * rel, "meso") if not np.isnan(rel) else (np.nan, None)
                hR.append(r0(v))
                hk.append(r0(v / pr) if not np.isnan(v) else None)
                ho.append(o)
            cu = CU[p]
            en_anos = [a for a in EN if a in own.index]
            rend_med = float(g.rend_plantado_kg_ha.median())
            dias, dmin, dmax = CICLO[p]
            c = {"tipo": "medido", "anos_serie": int(len(g)), "anos_vizinhos": [a for a, o in zip(ANOS, ho) if o == "meso"],
                 "preco_kg": r2(pr), "origem_preco": origem, "rend_mediano_kg_ha": r0(rend_med),
                 "valor_ha": {"p10": r0(R.quantile(.1)), "p50": r0(base), "p90": r0(R.quantile(.9)), "min": r0(R.min()), "max": r0(R.max())},
                 "el_nino_forte": r0(own.R[en_anos].median()) if len(en_anos) >= 2 else None, "anos_el_nino_forte_na_serie": en_anos,
                 "ultimos": {str(a): (r0(own.R[a]) if a in own.index else None) for a in range(2021, 2026)},
                 "quebra_pct": r0(g.quebra.mean() * 100),
                 "nao_paga_pct": {"semente": r0((R < cu["semente"]).mean() * 100), "desembolso": r0((R < cu["desembolso"]).mean() * 100)},
                 "custo_ha": cu,
                 "equilibrio": {"rend_kg_ha": r0(cu["desembolso"] / pr), "preco_kg": r2(cu["desembolso"] / rend_med) if rend_med > 0 else None},
                 "ha_mes": {"p50": r0(base / (dias / 30.4)), "faixa": [r0(base / (dmax / 30.4)), r0(base / (dmin / 30.4))], "ciclo_dias": dias,
                            "tipo": "suposição (ciclo)"}}
            if origem != "município":
                avisos.append(f"{p}: preço de referência da {origem} (o município tem menos de 3 anos de preço limpo em 2016–2025)")
            if p == "Feijão":
                c["aviso"] = "o PAM junta caupi e feijão comum"
            if p == "Mandioca":
                pa = area_recente.get(cod, [])
                c["area_plantada_2018_2025_ha"] = [r0(min(pa)), r0(max(pa))] if pa else None
                c["repete_ano_anterior_pct"] = r0(rep.get((p, cod), np.nan) * 100)
                partes = []
                if pa and max(pa) < 100:
                    partes.append(f"preço de pouco volume ({r0(min(pa))}–{r0(max(pa))} ha/ano desde 2018)")
                partes.append(f"{c['repete_ano_anterior_pct']}% dos rendimentos do PAM repetem o ano anterior")
                c["aviso"] = "; ".join(partes)
            if c["anos_vizinhos"]:
                avisos.append(f"{p}: {len(c['anos_vizinhos'])} ano(s) da série completados pela mesorregião (origem 'meso')")
            d["culturas"][p] = c
            d["historico_R_ha"][p], d["historico_kg_ha"][p], d["historico_R_ha"]["origem_" + p] = hR, hk, ho
        pm, om = preco(cod, "Mandioca")
        ru = raiz_uf.get(uf, {})
        d["precos_raiz"] = {"municipio": r2(pm), "origem_municipio": om, "uf_mediana": r2(ru.get("mediana")), "uf_p25": r2(ru.get("p25")),
                            "padrao": "uf_mediana", "tipo": "medido (escolher é suposição)"}
        d["padrao_familia"] = {"T_ha": 3, "baixio_ha": 1, "rotulo": "família da proposta (fictícia); o padrão local do Censo 2017 está em padroes_censo_mun.json",
                               "tipo": "suposição"}
        d["calibracao"] = {"faixa_p10_p90_cobriu_fora_da_amostra": calib["p10_p90"], "min_max_cobriu_fora_da_amostra": calib["min_max"]}
        d["avisos"] = avisos
        out[cod] = d
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, allow_nan=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(out) - 1} municípios; sem série: {sem}; {SAIDA} {SAIDA.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
