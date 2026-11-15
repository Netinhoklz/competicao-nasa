"""Acrescenta caju (castanha), banana e cana-de-açúcar a site-versao-final/dados/financeiro_mun.json, por município.

Mesmo método e mesmos campos de site-versao-final/ferramentas/preparar_financeiro_site.py (regras portadas, não importadas:
aquele arquivo está sendo editado por outro agente): IBGE PAM 1998–2025 em R$ de 2025 (IPCA, média anual); série = ≥ 10
anos com ≥ 10 ha; preço de referência = mediana 2016–2025 do preço implícito limpo do município (≥ 3 anos, produção ≥ 1 t,
0,25–4× a mediana da UF no ano), senão a da UF, senão a de toda a base; R = rendimento por ha × preço de referência;
lacuna = mediana do município × razão ao normal da mesorregião no ano (origem "meso"); quebra = rendimento < 0,5 × mediana
dos outros anos; El Niño forte = mediana de R nos anos-quadra com ONI ≥ 1,5 (mínimo 2).

Diferenças das perenes (ditas em cada cultura):
- área = "área destinada à colheita" (caju e banana, lavoura permanente: pomar formado) e "área plantada" (cana);
- caju = só a castanha (o PAM não tem o pedúnculo desde 1988);
- sem custo da CONAB para as três no NE: custo_ha, nao_paga_pct e equilibrio = null;
- ha_mes: uma colheita por ano no pomar/canavial formado (365 dias, suposição); os anos até a 1ª colheita não entram.
Fontes: caju no NE inteiro (dados_resumo/derivados/ibge_ne_pam_mun_anual.parquet, "Castanha de caju"); banana e cana só no
CE (E:/campeonato-nasa/dados/ibge_pam/pam_ce_municipios.parquet). Fora do CE, banana e cana = null com aviso "série só por
estado". Os avisos das perenes vão em "avisos_perenes" (o "avisos" do município, que o passo do dinheiro mostra, não muda).

As culturas que já existem não mudam (conferido no fim contra a cópia de segurança financeiro_mun.json.bak).
Rodar de novo depois de preparar_financeiro_site.py, que regrava o JSON sem as perenes.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 scripts/preparar_perenes_financeiro.py
"""
import datetime
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
DADOS = Path("E:/campeonato-nasa/dados")
DERIV = REPO / "dados_resumo" / "derivados"
SAIDA = REPO / "site-versao-final" / "dados" / "financeiro_mun.json"
BAK = SAIDA.with_name(SAIDA.name + ".bak")
ANOS = list(range(1998, 2026))
AREA_MIN, ANOS_MIN = 10, 10
PRECO_REF = range(2016, 2026)
UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
PERENES = ["Caju", "Banana", "Cana-de-açúcar"]
AVISO = {"Caju": "só a castanha (o pedúnculo não entra); rendimento por ha destinado à colheita (pomar formado); sem custo da CONAB",
         "Banana": "rendimento por ha destinado à colheita (bananal formado); sem custo da CONAB",
         "Cana-de-açúcar": "rendimento por ha plantado; o PAM junta cana para usina e para forragem; sem custo da CONAB"}

EVT = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
EN = sorted(int(a) for a in EVT[(EVT.ONI_OND_NDJ >= 1.5) & EVT.quadra_afetada.between(1998, 2025)].quadra_afetada)
assert EN == [1998, 2010, 2016, 2024], EN
IPA = pd.read_csv(DADOS / "financeiro" / "ipca_anual.csv").set_index("ano").fator_r2025


def serie_caju():
    Q = pd.read_parquet(DERIV / "ibge_ne_pam_mun_anual.parquet")
    Q = Q[(Q.produto == "Castanha de caju") & Q.ano.isin(ANOS)]
    return Q[["cod_mun", "ano", "area_plantada_ha", "area_colhida_ha", "producao_t", "valor_mil_moeda"]].assign(produto="Caju")


def serie_ce(produto_pam, nome):
    P = pd.read_parquet(DADOS / "ibge_pam" / "pam_ce_municipios.parquet")
    P = P[(P["produto"] == produto_pam) & P.ano.isin(ANOS)]
    P = P[(P.variavel != "Valor da produção") | (P.unidade == "Mil Reais")]  # 1998+ já em reais; o filtro só garante
    W = P.pivot_table(index=["cod_local", "ano"], columns="variavel", values="valor", aggfunc="first").reset_index()
    area = "Área destinada à colheita" if "Área destinada à colheita" in W else "Área plantada"
    return pd.DataFrame({"cod_mun": W.cod_local.astype(str), "ano": W.ano.astype(int), "area_plantada_ha": W[area],
                         "area_colhida_ha": W["Área colhida"], "producao_t": W["Quantidade produzida"],
                         "valor_mil_moeda": W["Valor da produção"], "produto": nome})


def preparar(P):
    """Como painel() e precos_ref() de preparar_financeiro_site.py (e scripts/preparar_financeiro.py:painel)."""
    P = P.copy()
    P["uf"] = P.cod_mun.str[:2].map(UF)
    P["fator_r2025"] = P.ano.map(IPA)
    P["valor_r2025"] = P.valor_mil_moeda * 1000 * P.fator_r2025
    ok = P.area_plantada_ha > 0
    P["rend_plantado_kg_ha"] = np.where(ok, P.producao_t * 1000 / P.area_plantada_ha.where(ok), np.nan)
    P["preco_r2025_kg"] = np.where(P.producao_t > 0, P.valor_r2025 / (P.producao_t * 1000).where(P.producao_t > 0), np.nan)
    B = P[P.area_plantada_ha >= AREA_MIN].dropna(subset=["rend_plantado_kg_ha"]).copy()

    def mediana_outros(s):
        v = s.to_numpy()
        if len(v) < 2:
            return pd.Series(np.nan, index=s.index)
        return pd.Series([np.median(np.delete(v, i)) for i in range(len(v))], index=s.index)

    B["normal_kg_ha"] = B.groupby("cod_mun").rend_plantado_kg_ha.transform(mediana_outros)
    B["quebra"] = B.rend_plantado_kg_ha / B.normal_kg_ha < 0.5
    B["n_anos"] = B.groupby("cod_mun").ano.transform("size")
    pr = B.preco_r2025_kg.where(B.producao_t >= 1)
    B["preco"] = pr.where((pr / pr.groupby([B.uf, B.ano]).transform("median")).between(0.25, 4))
    jan = B[B.ano.isin(PRECO_REF)]
    pm = jan.groupby("cod_mun").preco.agg(["median", "count"])
    pm = pm[pm["count"] >= 3]["median"].to_dict()
    pu = jan.groupby("uf").preco.median().to_dict()
    pn = float(jan.preco.median())
    base_toda = "NE" if B.uf.nunique() > 1 else "CE"

    def preco(cod):
        if cod in pm:
            return float(pm[cod]), "município"
        if UF[cod[:2]] in pu and not np.isnan(pu[UF[cod[:2]]]):
            return float(pu[UF[cod[:2]]]), "UF"
        return pn, base_toda

    B["preco_ref"] = [preco(c)[0] for c in B.cod_mun]
    B["R"] = B.rend_plantado_kg_ha * B.preco_ref
    M = B[B.n_anos >= ANOS_MIN].copy()
    M["R_rel"] = M.R / M.groupby("cod_mun").R.transform("median")
    return M, preco


def r0(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else int(round(float(x)))


def r2(x):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 2)


def main():
    antes = SAIDA.read_bytes()
    F = json.loads(antes.decode("utf-8"))
    if "perenes" not in F["_meta"]:  # a cópia de segurança guarda o JSON sem as perenes (rodar de novo não a sobrescreve)
        shutil.copy2(SAIDA, BAK)
    REFM = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
    fontes = {"Caju": serie_caju(), "Banana": serie_ce("Banana (cacho)", "Banana"),
              "Cana-de-açúcar": serie_ce("Cana-de-açúcar", "Cana-de-açúcar")}
    calc, calib, n_ok = {}, {}, {}
    for p, S in fontes.items():
        M, preco = preparar(S)
        M["meso"] = M.cod_mun.map(REFM.cod_meso)
        calc[p] = (M, preco, M.groupby(["meso", "ano"]).R_rel.median().to_dict())
        c1, c2 = [], []
        for _, g in M.groupby("cod_mun"):  # teste fora da amostra: faixa de 1998–2015 contra 2016–2025
            tr, te = g[g.ano <= 2015].R, g[g.ano >= 2016].R
            if len(tr) >= 8 and len(te) >= 5:
                c1.append(((te >= tr.quantile(.1)) & (te <= tr.quantile(.9))).mean())
                c2.append(((te >= tr.min()) & (te <= tr.max())).mean())
        calib[p] = {"p10_p90": round(float(np.mean(c1)), 2) if c1 else None, "min_max": round(float(np.mean(c2)), 2) if c2 else None,
                    "municipios_no_teste": len(c1)}
        n_ok[p] = int(M.cod_mun.nunique())
    print("municípios com série:", n_ok, "| calibração:", calib)

    for cod in REFM.index:
        d = F[cod]
        uf, meso = REFM.uf[cod], REFM.cod_meso[cod]
        avisos = []
        for p in PERENES:
            M, preco, meso_rel = calc[p]
            g = M[M.cod_mun == cod].sort_values("ano")
            if not len(g):
                d["culturas"][p] = None
                d["historico_R_ha"][p] = d["historico_kg_ha"][p] = d["historico_R_ha"]["origem_" + p] = None
                avisos.append(f"{p}: série só por estado (o PAM por município foi baixado só para o CE)" if (p != "Caju" and uf != "CE")
                              else f"{p}: sem série no município (menos de {ANOS_MIN} anos com {AREA_MIN} ha ou mais no PAM 1998–2025)")
                continue
            pr, origem = preco(cod)
            R, base, own = g.R, float(g.R.median()), g.set_index("ano")
            hR, hk, ho = [], [], []
            for a in ANOS:
                if a in own.index:
                    v, o = float(own.R[a]), "mun"
                else:
                    rel = meso_rel.get((meso, a), np.nan)
                    v, o = (base * rel, "meso") if not np.isnan(rel) else (np.nan, None)
                hR.append(r0(v))
                hk.append(r0(v / pr) if not np.isnan(v) else None)
                ho.append(o)
            en_anos = [a for a in EN if a in own.index]
            c = {"tipo": "medido", "anos_serie": int(len(g)), "anos_vizinhos": [a for a, o in zip(ANOS, ho) if o == "meso"],
                 "preco_kg": r2(pr), "origem_preco": origem, "rend_mediano_kg_ha": r0(g.rend_plantado_kg_ha.median()),
                 "valor_ha": {"p10": r0(R.quantile(.1)), "p50": r0(base), "p90": r0(R.quantile(.9)), "min": r0(R.min()), "max": r0(R.max())},
                 "el_nino_forte": r0(own.R[en_anos].median()) if len(en_anos) >= 2 else None, "anos_el_nino_forte_na_serie": en_anos,
                 "ultimos": {str(a): (r0(own.R[a]) if a in own.index else None) for a in range(2021, 2026)},
                 "quebra_pct": r0(g.quebra.mean() * 100), "nao_paga_pct": None, "custo_ha": None, "equilibrio": None,
                 "ha_mes": {"p50": r0(base / 12), "faixa": [r0(base / 12), r0(base / 12)], "ciclo_dias": 365,
                            "tipo": "suposição (ciclo): pomar ou canavial formado, uma colheita por ano; os anos até a 1ª colheita não entram"},
                 "aviso": AVISO[p], "perene": True}
            if origem != "município":
                avisos.append(f"{p}: preço de referência da {origem} (o município tem menos de 3 anos de preço limpo em 2016–2025)")
            if c["anos_vizinhos"]:
                avisos.append(f"{p}: {len(c['anos_vizinhos'])} ano(s) da série completados pela mesorregião (origem 'meso')")
            d["culturas"][p] = c
            d["historico_R_ha"][p], d["historico_kg_ha"][p], d["historico_R_ha"]["origem_" + p] = hR, hk, ho
        d["avisos_perenes"] = avisos

    F["_meta"]["perenes"] = {
        "culturas": PERENES, "script": "scripts/preparar_perenes_financeiro.py",
        "fontes": {"Caju": "IBGE PAM, Castanha de caju, municípios do NE (dados_resumo/derivados/ibge_ne_pam_mun_anual.parquet)",
                   "Banana": "IBGE PAM, Banana (cacho), municípios do CE (E:/campeonato-nasa/dados/ibge_pam/pam_ce_municipios.parquet)",
                   "Cana-de-açúcar": "IBGE PAM, Cana-de-açúcar, municípios do CE (idem)"},
        "regras": "as mesmas das outras culturas (_meta.regras); área destinada à colheita nas permanentes; sem custo da CONAB",
        "fora_do_CE": "banana e cana = null com aviso 'série só por estado' em avisos_perenes",
        "municipios_com_serie": n_ok,
        "calibracao_fora_da_amostra": calib,
        "gerado_em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}

    # as culturas e campos que já existiam não podem mudar
    velho = json.loads(antes.decode("utf-8"))
    novas = set(PERENES) | {"origem_" + p for p in PERENES}
    sub = ("culturas", "historico_R_ha", "historico_kg_ha")
    fora = lambda x: {k: y for k, y in x.items() if k not in sub and k not in ("avisos_perenes", "perenes")}  # noqa: E731
    for cod, v in velho.items():
        assert fora(F[cod]) == fora(v), cod
        for k in sub if cod != "_meta" else ():
            assert {a: b for a, b in F[cod][k].items() if a not in novas} == {a: b for a, b in v[k].items() if a not in novas}, (cod, k)
    tmp = SAIDA.with_suffix(".tmp")
    tmp.write_text(json.dumps(F, ensure_ascii=False, allow_nan=False, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, SAIDA)
    print(f"{SAIDA}: {SAIDA.stat().st_size / 1e6:.2f} MB (antes {len(antes) / 1e6:.2f} MB); cópia em {BAK.name}; "
          f"culturas antigas idênticas em {len(velho) - 1} municípios")


if __name__ == "__main__":
    main()
