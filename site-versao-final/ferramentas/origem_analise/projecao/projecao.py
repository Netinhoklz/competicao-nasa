"""Projeção 2027–2029 por município × cultura (milho, feijão, mandioca), método escolhido no backtest:
2027: condicionado ao ONI de ago–out (classe forte, ONI ≥ 1,0: safras 1998, 2016, 2024), encolhido para a mesorregião;
2028 e 2029: climatologia do município encolhida para a mesorregião (todos os anos 1998–2025).
Nível = mediana do município 1998–2025 (rend. por ha plantado). Receita a preço mediano 2016–25 (R$ de 2025/kg).
Saída: projecao_mun.json (todos) e projecao_exemplos.json (5 municípios)."""
import json
import numpy as np, pandas as pd
OUT = "C:/Users/NETINH~1/AppData/Local/Temp/claude/88b277d27b184113/73cd62bd-b6e9-4872-9e4a-a06e5ca404a0/scratchpad/analise10/projecao/"
D = "c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados/"
QS = np.array([0.1, 0.2, 0.5, 0.8, 0.9]); K = 10
ANOS = np.arange(1998, 2026)
FORTES = np.isin(ANOS, [1998, 2016, 2024])
# custos da CONAB, R$ de 2025/ha (notebooks/secoes_financeiro/05_custo.py:210-212)
CUSTO = {"Milho": {"semente": 284, "desembolso": 1136}, "Feijão": {"semente": 142, "desembolso": 1992},
         "Mandioca": {"semente": 0, "desembolso": 4387}}
REF = pd.read_parquet(D + "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
P = pd.read_parquet("E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet")
res = {}
for cult in ["Milho", "Feijão", "Mandioca"]:
    v = P[(P.produto == cult) & (P.area_plantada_ha > 0)]
    Y = v.pivot(index="cod_mun", columns="ano", values="rend_plantado_kg_ha").reindex(columns=ANOS)
    Y = Y[Y.notna().sum(axis=1) >= 15]
    pr = v[v.ano >= 2016].groupby("cod_mun").preco_r2025_kg.median()
    pr_uf = v[v.ano >= 2016].groupby("uf").preco_r2025_kg.median()
    mun = Y.index.values; A = Y.values
    med = np.nanmedian(A, 1); R = A / med[:, None]
    meso = REF.loc[mun, "cod_meso"].values
    n_all = (~np.isnan(R)).sum(1); n_f = (~np.isnan(R[:, FORTES])).sum(1)
    def pool(mask):
        q = np.full((len(QS), len(mun)), np.nan); p = np.full(len(mun), np.nan)
        for m in np.unique(meso):
            ix = meso == m; z = R[ix][:, mask].ravel(); z = z[~np.isnan(z)]
            q[:, ix] = np.quantile(z, QS)[:, None]; p[ix] = (z < 0.5).mean()
        return q, p
    qm_all, pm_all = pool(np.ones(len(ANOS), bool)); qm_f, pm_f = pool(FORTES)
    qmu_all = np.nanquantile(R, QS, axis=1)
    qmu_f = np.nanquantile(np.where(n_f[:, None] > 0, R[:, FORTES], 1.0), QS, axis=1)
    pmu_all = np.nanmean(np.where(np.isnan(R), np.nan, R < 0.5), 1)
    pmu_f = np.nan_to_num(np.nanmean(np.where(np.isnan(R[:, FORTES]), np.nan, R[:, FORTES] < 0.5), 1))
    w_all = n_all / (n_all + K); w_f = n_f / (n_f + K)
    for i, c in enumerate(mun):
        preco = pr.get(c, pr_uf.get(REF.loc[c, "uf"], np.nan))
        rec = {}
        for ano in [2027, 2028, 2029]:
            if ano == 2027:
                qr = w_f[i] * qmu_f[:, i] + (1 - w_f[i]) * qm_f[:, i]; pq = w_f[i] * pmu_f[i] + (1 - w_f[i]) * pm_f[i]
                base = "ONI ago–out ≥ 1,0 (safras 1998, 2016, 2024); ONI 2026 = 2,46 fora da série (extrapolação)"
            else:
                qr = w_all[i] * qmu_all[:, i] + (1 - w_all[i]) * qm_all[:, i]; pq = w_all[i] * pmu_all[i] + (1 - w_all[i]) * pm_all[i]
                base = "só clima: todos os anos 1998–2025 (sem previsão do oceano)"
            # alargamento conforme (walk-forward 2008–2025): bilateral no P10/P90, de um lado no P20/P80 (× mediana)
            wb, wp = (0.155, 0.079) if ano == 2027 else (0.104, 0.056)
            qr = np.maximum.accumulate(qr) + np.array([-wb, -wp, 0, wp, wb])
            kg = med[i] * np.clip(qr, 0, None)
            rec[str(ano)] = {"kg_ha": {f"p{int(q*100)}": round(float(x)) for q, x in zip(QS, kg)},
                             "chance_quebra": round(float(pq), 2),
                             "receita_r2025_ha": None if np.isnan(preco) else {f"p{int(q*100)}": round(float(x * preco)) for q, x in zip(QS, kg)},
                             "base": base}
            if cult != "Mandioca":
                rec[str(ano)]["sacos60_ha"] = {k: round(v / 60, 1) for k, v in rec[str(ano)]["kg_ha"].items()}
        res.setdefault(c, {"municipio": REF.loc[c, "municipio"], "uf": REF.loc[c, "uf"], "mesorregiao": REF.loc[c, "mesorregiao"]})
        res[c][cult] = {"mediana_1998_2025_kg_ha": round(float(med[i])), "n_anos": int(n_all[i]), "n_anos_el_nino_forte": int(n_f[i]),
                        "peso_municipio_2027": round(float(w_f[i]), 2), "peso_municipio_clima": round(float(w_all[i]), 2),
                        "preco_r2025_kg": None if np.isnan(preco) else round(float(preco), 2),
                        "custo_r2025_ha": CUSTO[cult], "anos": rec,
                        "medido_anos_parecidos_kg_ha": {str(a): (None if np.isnan(A[i, ANOS == a][0]) else round(float(A[i, ANOS == a][0])))
                                                        for a in [1998, 2016, 2024]}}
        # chance de a receita não pagar a semente / o desembolso (interpolando na distribuição projetada)
        if not np.isnan(preco):
            for ano in ["2027", "2028"]:
                kgq = np.array(list(res[c][cult]["anos"][ano]["kg_ha"].values())) * preco
                for k, val in CUSTO[cult].items():
                    if val > 0:
                        res[c][cult]["anos"][ano][f"chance_nao_paga_{k}"] = round(float(np.interp(val, kgq, QS, left=0.05, right=0.95)), 2)
# 3 anos: chance de >= 1 quebra em 2027–2029 (independente; os blocos reais de 3 anos dão um pouco menos: 0,50 contra 0,58)
for c, d in res.items():
    for cult in ["Milho", "Feijão", "Mandioca"]:
        if cult in d:
            p = [d[cult]["anos"][a]["chance_quebra"] for a in ["2027", "2028", "2029"]]
            d[cult]["chance_ao_menos_1_quebra_2027_2029"] = round(1 - np.prod([1 - x for x in p]), 2)
json.dump(res, open(OUT + "projecao_mun.json", "w", encoding="utf-8"), ensure_ascii=False)
ex = {c: res[c] for c in ["2311306", "2313302", "2903201", "2700300", "2611101"] if c in res}
json.dump(ex, open(OUT + "projecao_exemplos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(res), "municípios")
for c in ["2311306", "2903201"]:
    d = res[c]
    for cult in ["Milho", "Feijão", "Mandioca"]:
        if cult in d:
            a = d[cult]["anos"]
            print(d["municipio"], cult, "mediana", d[cult]["mediana_1998_2025_kg_ha"], "| 2027", a["2027"]["kg_ha"], a["2027"]["chance_quebra"],
                  a["2027"].get("chance_nao_paga_desembolso"), "| 2028", a["2028"]["kg_ha"], a["2028"]["chance_quebra"],
                  "| 3 anos", d[cult]["chance_ao_menos_1_quebra_2027_2029"])
