"""Gera site-versao-final/dados/projecao_mun.json (contrato da seção 7 de analise/projecao.md) e
site-versao-final/dados/projecao_metricas.txt, com o método "C + D + conforme" e a definição ÚNICA de El Niño forte do
motor (decisão 3 do PLANO_INTEGRACAO.md): anos-quadra com ONI de out–dez/nov–jan ≥ 1,5 → 1998, 2010, 2016 e 2024.

Porta de ferramentas/origem_analise/projecao/backtest.py, metricas.py, extra.py e projecao.py. O que mudou:
- a classe "El Niño forte" do método D passa de ONI ago–out ≥ 1,0 (1998, 2016, 2024) para a do motor (4 anos);
- o backtest roda as duas definições, para comparar; só os métodos A, C e D (B, D2 e E foram reprovados e B/E não
  dependem da classe); o F (alargamento conforme) é calculado depois, a partir dos escores do D no walk-forward;
- os fatores do alargamento (P10/P90 e P20/P80, × mediana) são recalibrados no walk-forward 2008–2025 (como extra.py);
- preço de referência e custo vêm de preparar_financeiro_site.py, para as telas de dinheiro e segurança baterem.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_projecao.py"""
import datetime
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preparar_financeiro_site as FIN  # noqa: E402

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
D = FIN.DERIV
SAIDA = RAIZ / "dados" / "projecao_mun.json"
METR = RAIZ / "dados" / "projecao_metricas.txt"
QS = np.array([0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9])
QC = [f"q{int(q * 100)}" for q in QS]
ANOS = np.arange(1998, 2026)
K = 10
CULT = ["Milho", "Feijão", "Mandioca"]
SECA = [2012, 2013, 2014, 2015]
EN = FIN.EN  # [1998, 2010, 2016, 2024], de eventos.csv: ONI_OND_NDJ >= 1,5

I = pd.read_parquet(D / "indices_clima_mensal.parquet")
o = I[I.variavel == "ONI"].set_index("data").valor
ASO = o[o.index.month == 9]
ONI_2026 = float(ASO[ASO.index.year == 2026].iloc[0])
ASO_MAX = ASO[ASO.index.year <= 2025]
ASO_MAX_ANO, ASO_MAX = int(ASO_MAX.idxmax().year), float(ASO_MAX.max())
ASO.index = ASO.index.year + 1  # ano da quadra afetada
CLASSES = {"antes": ("ONI ago–out ≥ 1,0", ASO.reindex(ANOS).values >= 1.0),
           "depois": ("ONI out–dez/nov–jan ≥ 1,5", np.isin(ANOS, EN))}
assert list(ANOS[CLASSES["antes"][1]]) == [1998, 2016, 2024]
REF = pd.read_parquet(D / "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
P = pd.read_parquet(FIN.F / "painel_mun_cultura_ano.parquet")


def matriz(cult, n_min):
    v = P[(P.produto == cult) & (P.area_plantada_ha > 0)]
    Y = v.pivot(index="cod_mun", columns="ano", values="rend_plantado_kg_ha").reindex(columns=ANOS)
    return Y[Y.notna().sum(axis=1) >= n_min]


def frac_below(R, thr):
    ok = ~np.isnan(R)
    return np.where(ok.sum(1) > 0, np.nansum(R < thr, 1) / np.maximum(ok.sum(1), 1), np.nan)


def pool_meso(R, meso, qs, mask_cols=None):
    """Quantis e P(R<0,5) do conjunto de razões da mesorregião (todos os municípios e anos do recorte)."""
    qm = np.full((len(qs), R.shape[0]), np.nan)
    pm = np.full(R.shape[0], np.nan)
    Rr = R if mask_cols is None else R[:, mask_cols]
    for m in np.unique(meso):
        ix = meso == m
        z = Rr[ix].ravel()
        z = z[~np.isnan(z)]
        if len(z) < 5:
            continue
        qm[:, ix] = np.quantile(z, qs)[:, None]
        pm[ix] = (z < 0.5).mean()
    return qm, pm


def backtest(forte):
    """LOYO (28 anos) e WF (alvo 2008–2025, só o passado) dos métodos A, C e D (backtest.py, sem B, D2 e E)."""
    linhas = []
    for cult in CULT:
        Yd = matriz(cult, 20)
        Y, mun = Yd.values, Yd.index.values
        meso = REF.loc[mun, "cod_meso"].values
        for modo in ["LOYO", "WF"]:
            for t in (ANOS if modo == "LOYO" else ANOS[ANOS >= 2008]):
                jt = int(np.where(ANOS == t)[0][0])
                tr = (ANOS != t) if modo == "LOYO" else (ANOS < t)
                Ytr = Y[:, tr]
                n = (~np.isnan(Ytr)).sum(1)
                med = np.nanmedian(Ytr, 1)
                y = Y[:, jt]
                ok = (~np.isnan(y)) & (n >= 8) & (med > 0)
                R = Ytr / med[:, None]
                w = n / (n + K)
                res = {"A_mun": (np.nanquantile(Ytr, QS, axis=1), frac_below(R, 0.5))}
                qm, pm = pool_meso(R, meso, QS)
                res["C_hier"] = (med[None, :] * (w * np.nanquantile(R, QS, axis=1) + (1 - w) * qm), w * frac_below(R, 0.5) + (1 - w) * pm)
                cls = forte[tr] == forte[jt]
                qmD, pmD = pool_meso(R, meso, QS, cls)
                Rc = R[:, cls]
                nc = (~np.isnan(Rc)).sum(1)
                wc = nc / (nc + K)
                qmuD = np.where(nc[None, :] > 0, np.nanquantile(np.where(nc[:, None] > 0, Rc, 1.0), QS, axis=1), 1.0)
                res["D_enso"] = (med[None, :] * (wc * qmuD + (1 - wc) * qmD), wc * np.nan_to_num(frac_below(Rc, 0.5)) + (1 - wc) * pmD)
                for nome, (q, pq) in res.items():
                    d = pd.DataFrame({"metodo": nome, "modo": modo, "cultura": cult, "cod_mun": mun[ok], "ano": t,
                                      "y": y[ok], "med": med[ok], "pq": pq[ok]})
                    for k, c in enumerate(QC):
                        d[c] = q[k][ok]
                    linhas.append(d)
    return pd.concat(linhas, ignore_index=True)


def conforme_wf(B):
    """F a partir do D no walk-forward, ano a ano, com os escores só dos anos anteriores (mesma cultura).
    F_conf = como backtest.py (P10, P90 e P20 pelo fator bilateral); F_final = como o JSON (P10/P90 pelo bilateral,
    P20/P80 pelo fator de um lado só, o do piso)."""
    out = []
    S = B[(B.modo == "WF") & (B.metodo == "D_enso")]
    for cult, g in S.groupby("cultura"):
        sb, sp = [], []
        for t in sorted(g.ano.unique()):
            x = g[g.ano == t].copy()
            Qb = Qp = 0.0
            if sb:
                s, u = np.concatenate(sb), np.concatenate(sp)
                Qb = np.quantile(s, min(1, np.ceil((len(s) + 1) * 0.8) / len(s)))
                Qp = np.quantile(u, min(1, np.ceil((len(u) + 1) * 0.8) / len(u)))
            sb.append(np.maximum((x.q10 - x.y) / x.med, (x.y - x.q90) / x.med).values)
            sp.append(((x.q20 - x.y) / x.med).values)
            f = x.copy()
            f["metodo"] = "F_conf"
            f["q10"], f["q90"], f["q20"] = x.q10 - Qb * x.med, x.q90 + Qb * x.med, x.q20 - Qb * x.med
            h = x.copy()
            h["metodo"] = "F_final"
            h["q10"], h["q90"] = x.q10 - Qb * x.med, x.q90 + Qb * x.med
            h["q20"], h["q80"] = x.q20 - Qp * x.med, x.q80 + Qp * x.med
            out += [f, h]
    return pd.concat([B] + out, ignore_index=True)


def fatores(B):
    """extra.py: quantil 80% dos escores do walk-forward 2008–2025 (× mediana), bilateral e só o piso."""
    f = {}
    for m in ["C_hier", "D_enso"]:
        s = B[(B.modo == "WF") & (B.metodo == m)]
        f[m] = (float(np.quantile(np.maximum((s.q10 - s.y) / s.med, (s.y - s.q90) / s.med), 0.8)),
                float(np.quantile((s.q20 - s.y) / s.med, 0.8)))
    return f


def metricas(B, anos_en, fat):
    B = B.copy()
    r = B.y / B.med
    B["quebra"] = (r < 0.5).astype(float)
    B["cov80"] = ((B.y >= B.q10) & (B.y <= B.q90)).astype(float)
    B["piso80"] = (B.y >= B.q20).astype(float)
    B["pq"] = B.pq.clip(0, 1)
    B["brier"] = (B.pq - B.quebra) ** 2
    # D com o alargamento fixo do JSON (fatores do WF), avaliado também no LOYO
    Dl = B[(B.metodo == "D_enso")].copy()
    wb, wp = fat["D_enso"]
    Dl["metodo"] = "D+fixo"
    Dl["cov80"] = ((Dl.y >= Dl.q10 - wb * Dl.med) & (Dl.y <= Dl.q90 + wb * Dl.med)).astype(float)
    Dl["piso80"] = (Dl.y >= Dl.q20 - wp * Dl.med).astype(float)
    B = pd.concat([B, Dl], ignore_index=True)
    B["grupo"] = np.where(B.ano.isin(anos_en), "El Niño forte", np.where(B.ano.isin(SECA), "seca 2012–15", "demais"))
    m = {}
    for modo in ["LOYO", "WF"]:
        S = B[B.modo == modo]
        cy = S.groupby(["metodo", "ano"]).cov80.mean().unstack(0)
        m[modo] = {"geral": S.groupby("metodo").cov80.mean(), "media_anos": cy.mean(), "pior": cy.min(), "lt60": (cy < 0.6).sum(),
                   "milho": S[S.cultura == "Milho"].groupby("metodo").cov80.mean(),
                   "grupo": S.groupby(["grupo", "metodo"]).agg(n=("y", "size"), cov80=("cov80", "mean"), piso80=("piso80", "mean"),
                                                               brier=("brier", "mean"), p_prev=("pq", "mean"), f_obs=("quebra", "mean")),
                   "en_ano": S[S.ano.isin(EN)].groupby(["ano", "metodo"]).agg(cov80=("cov80", "mean"), piso80=("piso80", "mean"),
                                                                             p_prev=("pq", "mean"), f_obs=("quebra", "mean")),
                   "milho_en_ano": S[S.ano.isin(EN) & (S.cultura == "Milho")].groupby(["ano", "metodo"]).agg(
                       p_prev=("pq", "mean"), f_obs=("quebra", "mean"), piso80=("piso80", "mean")),
                   "cy": cy}
    return m


def projetar(fat):
    """projecao.py com os 4 anos fortes e os fatores recalibrados."""
    QP = np.array([0.1, 0.2, 0.5, 0.8, 0.9])
    FORTES = np.isin(ANOS, EN)
    Bf = FIN.painel()
    preco, _ = FIN.precos_ref(Bf)
    CU = FIN.custos()
    (wbD, wpD), (wbC, wpC) = [tuple(round(x, 3) for x in fat[k]) for k in ["D_enso", "C_hier"]]
    base27 = (f"El Niño forte = anos-quadra com ONI out–dez/nov–jan ≥ 1,5 ({', '.join(map(str, EN[:-1]))} e {EN[-1]}); "
              f"o ONI de ago–out/2026 (+{ONI_2026:.2f}) está acima do maior ago–out da série (+{ASO_MAX:.2f}, {ASO_MAX_ANO}): extrapolação"
              ).replace(".", ",")
    base_clima = "só clima: todos os anos 1998–2025 (sem previsão do oceano para tão longe)"
    res = {}
    for cult in CULT:
        Y = matriz(cult, 15)
        mun, A = Y.index.values, Y.values
        med = np.nanmedian(A, 1)
        R = A / med[:, None]
        meso = REF.loc[mun, "cod_meso"].values
        n_all, n_f = (~np.isnan(R)).sum(1), (~np.isnan(R[:, FORTES])).sum(1)
        qm_all, pm_all = pool_meso(R, meso, QP)
        qm_f, pm_f = pool_meso(R, meso, QP, FORTES)
        qmu_all = np.nanquantile(R, QP, axis=1)
        qmu_f = np.nanquantile(np.where(n_f[:, None] > 0, R[:, FORTES], 1.0), QP, axis=1)
        pmu_all = np.nanmean(np.where(np.isnan(R), np.nan, R < 0.5), 1)
        pmu_f = np.nan_to_num(np.nanmean(np.where(np.isnan(R[:, FORTES]), np.nan, R[:, FORTES] < 0.5), 1))
        w_all, w_f = n_all / (n_all + K), n_f / (n_f + K)
        cu = {"semente": CU[cult]["semente"], "desembolso": CU[cult]["desembolso"]}
        for i, c in enumerate(mun):
            pr, origem_pr = preco(c, cult)
            anos = {}
            for ano in ["2027", "2028", "2029"]:
                if ano == "2027":
                    qr = w_f[i] * qmu_f[:, i] + (1 - w_f[i]) * qm_f[:, i]
                    pq = w_f[i] * pmu_f[i] + (1 - w_f[i]) * pm_f[i]
                    wb, wp, base = wbD, wpD, base27
                else:
                    qr = w_all[i] * qmu_all[:, i] + (1 - w_all[i]) * qm_all[:, i]
                    pq = w_all[i] * pmu_all[i] + (1 - w_all[i]) * pm_all[i]
                    wb, wp, base = wbC, wpC, base_clima
                qr = np.maximum.accumulate(qr) + np.array([-wb, -wp, 0, wp, wb])
                kg = med[i] * np.clip(qr, 0, None)
                rec = kg * pr
                a = {"tipo": "projeção", "kg_ha": {f"p{int(q * 100)}": int(round(x)) for q, x in zip(QP, kg)}}
                if cult != "Mandioca":
                    a["sacos60_ha"] = {k: round(v / 60, 1) for k, v in a["kg_ha"].items()}
                a["chance_quebra"] = round(float(pq), 2)
                a["receita_r2025_ha"] = {f"p{int(q * 100)}": int(round(x)) for q, x in zip(QP, rec)}
                for k, val in cu.items():
                    if val > 0:
                        a[f"chance_nao_paga_{k}"] = round(float(np.interp(val, rec, QP, left=0.05, right=0.95)), 2)
                a["base"] = base
                anos[ano] = a
            p3 = [anos[x]["chance_quebra"] for x in ["2027", "2028", "2029"]]
            res.setdefault(c, {"municipio": REF.loc[c, "municipio"], "uf": REF.loc[c, "uf"], "mesorregiao": REF.loc[c, "mesorregiao"]})
            res[c][cult] = {
                "mediana_1998_2025_kg_ha": int(round(med[i])), "n_anos": int(n_all[i]), "n_anos_el_nino_forte": int(n_f[i]),
                "peso_municipio_2027": round(float(w_f[i]), 2), "peso_municipio_clima": round(float(w_all[i]), 2),
                "preco_r2025_kg": round(pr, 2), "origem_preco": origem_pr, "custo_r2025_ha": cu,
                "medido_anos_parecidos_kg_ha": {str(a): int(round(A[i, ANOS == a][0])) for a in EN if not np.isnan(A[i, ANOS == a][0])},
                "anos": anos, "chance_ao_menos_1_quebra_2027_2029": round(1 - float(np.prod([1 - x for x in p3])), 2)}
    out = {"_meta": {
        "descricao": "Projeção do rendimento por ha plantado (kg/ha, sacos de 60 kg/ha e R$ de 2025/ha) por município, cultura e ano; chave = código IBGE.",
        "metodo": (f"C + D + conforme. 2027 (D): quantis da razão ao normal só nos anos de El Niño forte ({', '.join(map(str, EN))}), "
                   f"município encolhido para a mesorregião com peso n/(n+{K}); alargamento P10/P90 ±{wbD:.3f} × mediana e P20/P80 ∓{wpD:.3f} × mediana. "
                   f"2028–2029 (C): todos os anos 1998–2025, mesmo encolhimento; alargamento ±{wbC:.3f} e ∓{wpC:.3f}. Fatores calibrados no "
                   "walk-forward 2008–2025 (projecao_metricas.txt). Corte em zero.").replace("0.", "0,"),
        "tipo": {"medido": "medido_anos_parecidos_kg_ha, mediana_1998_2025_kg_ha, n_anos (IBGE PAM); custo (CONAB); preço de referência",
                 "projeção": "anos.2027/2028/2029: quantis, chance de quebra e chance de não pagar",
                 "suposição": "o futuro se parece com 1998–2025, sem tendência; 2027 se parece com os 4 El Niños fortes; preço = referência 2016–2025"},
        "quebra": "rendimento < 0,5 × mediana 1998–2025 do município",
        "chance_nao_paga": "interpolação do custo nos quantis da receita; 0,05 e 0,95 são o limite da interpolação: ler '≤ 1 em 10' e '≥ 9 em 10'",
        "chance_ao_menos_1_quebra": "1 − Π(1 − p) supondo anos independentes; nos blocos reais de 3 anos as quebras se agrupam (0,50 contra 0,58)",
        "anos_el_nino_forte": EN, "oni_ago_out_2026": ONI_2026, "oni_ago_out_max_serie": {"valor": ASO_MAX, "ano": ASO_MAX_ANO},
        "fatores_conforme": {"2027": {"p10_p90": wbD, "p20_p80": wpD}, "2028_2029": {"p10_p90": wbC, "p20_p80": wpC}},
        "nao_projeta": ["secas de vários anos (2012–15)", "a roça de uma família (o PAM é a média do município)", "a mandioca ano a ano (PAM repetido)",
                        "o efeito da rotação", "preço futuro", "o P90 no cerrado com tendência forte (ex.: Barreiras)"],
        "script": "site-versao-final/ferramentas/preparar_projecao.py", "gerado_em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}}
    for c in REF.index:
        d = res.get(c, {"municipio": REF.loc[c, "municipio"], "uf": REF.loc[c, "uf"], "mesorregiao": REF.loc[c, "mesorregiao"]})
        av = []
        for cult in CULT:
            if cult not in d:
                d[cult] = None
                av.append(f"{cult}: sem projeção (menos de 15 anos com área plantada no PAM 1998–2025)")
        d["avisos"] = av
        out[c] = d
    return out


def tabela(m_a, m_d, linhas):
    return "\n".join(f"{nome:58s} {fa(m_a):>8s} {fa(m_d):>8s}" for nome, fa in linhas)


def main():
    t0 = time.time()
    run = {}
    for k, (rot, forte) in CLASSES.items():
        B = conforme_wf(backtest(forte))
        fat = fatores(B)
        run[k] = {"rot": rot, "anos": [int(a) for a in ANOS[forte]], "fat": fat, "m": metricas(B, [int(a) for a in ANOS[forte]], fat), "n": len(B)}
        print(k, rot, run[k]["anos"], {m: tuple(round(x, 3) for x in v) for m, v in fat.items()}, f"{time.time() - t0:.0f}s", flush=True)
    a, d = run["antes"], run["depois"]
    ma, md = a["m"], d["m"]

    def g(m, modo, grupo, met, col):
        try:
            return m[modo]["grupo"].loc[(grupo, met), col]
        except KeyError:
            return np.nan

    L = [
        ("LOYO, cobertura 80%, média dos anos: C", lambda m: f"{m['LOYO']['media_anos']['C_hier']:.3f}"),
        ("LOYO, cobertura 80%, média dos anos: D", lambda m: f"{m['LOYO']['media_anos']['D_enso']:.3f}"),
        ("LOYO, cobertura 80%, média dos anos: D + alargamento fixo", lambda m: f"{m['LOYO']['media_anos']['D+fixo']:.3f}"),
        ("LOYO, El Niño forte: cobertura 80% do D", lambda m: f"{g(m, 'LOYO', 'El Niño forte', 'D_enso', 'cov80'):.3f}"),
        ("LOYO, El Niño forte: cobertura 80% do D + alargamento fixo", lambda m: f"{g(m, 'LOYO', 'El Niño forte', 'D+fixo', 'cov80'):.3f}"),
        ("LOYO, El Niño forte: piso P20 do C (meta 0,80)", lambda m: f"{g(m, 'LOYO', 'El Niño forte', 'C_hier', 'piso80'):.3f}"),
        ("LOYO, El Niño forte: piso P20 do D", lambda m: f"{g(m, 'LOYO', 'El Niño forte', 'D_enso', 'piso80'):.3f}"),
        ("LOYO, El Niño forte: piso P20 do D + alargamento fixo", lambda m: f"{g(m, 'LOYO', 'El Niño forte', 'D+fixo', 'piso80'):.3f}"),
        ("LOYO, El Niño forte: quebra prevista D / observada", lambda m: f"{g(m, 'LOYO', 'El Niño forte', 'D_enso', 'p_prev'):.2f}/{g(m, 'LOYO', 'El Niño forte', 'D_enso', 'f_obs'):.2f}"),
        ("LOYO, El Niño forte: quebra prevista C / observada", lambda m: f"{g(m, 'LOYO', 'El Niño forte', 'C_hier', 'p_prev'):.2f}/{g(m, 'LOYO', 'El Niño forte', 'C_hier', 'f_obs'):.2f}"),
        ("WF, cobertura 80%, média dos anos: C", lambda m: f"{m['WF']['media_anos']['C_hier']:.3f}"),
        ("WF, cobertura 80%, média dos anos: D", lambda m: f"{m['WF']['media_anos']['D_enso']:.3f}"),
        ("WF, cobertura 80%, média dos anos: F_conf (como backtest.py)", lambda m: f"{m['WF']['media_anos']['F_conf']:.3f}"),
        ("WF, cobertura 80%, média dos anos: F_final (como o JSON)", lambda m: f"{m['WF']['media_anos']['F_final']:.3f}"),
        ("WF, pior ano: F_conf", lambda m: f"{m['WF']['pior']['F_conf']:.3f}"),
        ("WF, anos com cobertura < 0,6: F_conf", lambda m: f"{int(m['WF']['lt60']['F_conf'])}"),
        ("WF, cobertura 80% do milho: F_conf", lambda m: f"{m['WF']['milho']['F_conf']:.3f}"),
        ("WF, El Niño forte: cobertura 80% do F_conf", lambda m: f"{g(m, 'WF', 'El Niño forte', 'F_conf', 'cov80'):.3f}"),
        ("WF, El Niño forte: piso P20 do D", lambda m: f"{g(m, 'WF', 'El Niño forte', 'D_enso', 'piso80'):.3f}"),
        ("WF, El Niño forte: piso P20 do F_conf", lambda m: f"{g(m, 'WF', 'El Niño forte', 'F_conf', 'piso80'):.3f}"),
        ("WF, El Niño forte: piso P20 do F_final", lambda m: f"{g(m, 'WF', 'El Niño forte', 'F_final', 'piso80'):.3f}"),
        ("WF, El Niño forte: quebra prevista D / observada", lambda m: f"{g(m, 'WF', 'El Niño forte', 'D_enso', 'p_prev'):.2f}/{g(m, 'WF', 'El Niño forte', 'D_enso', 'f_obs'):.2f}"),
    ]
    txt = [f"Backtest da projeção por ciclo (método C + D + conforme), gerado por site-versao-final/ferramentas/preparar_projecao.py em "
           f"{datetime.datetime.now():%Y-%m-%d %H:%M}.",
           "PAM municipal 1998–2025, rendimento por ha plantado; municípios com ≥ 20 anos; milho, feijão e mandioca.",
           "LOYO = deixa o ano de fora (28 anos); WF = walk-forward, só o passado, alvo 2008–2025.",
           "C = quantis do município encolhidos para a mesorregião (peso n/(n+10)); D = o mesmo, só com os anos da mesma classe de El Niño;",
           "F_conf = D alargado ano a ano pelo quantil 80% dos escores dos anos anteriores (P10, P90 e P20 pelo fator bilateral, como backtest.py);",
           "F_final = idem, mas P20/P80 pelo fator de um lado só (é o que vai no JSON, com o fator fixo calibrado em todos os anos do WF);",
           "D + alargamento fixo = D com os fatores fixos do JSON (calibrados no WF) aplicados também no LOYO (otimista: mesmos dados).",
           "",
           f"ANTES  = {a['rot']}: {a['anos']} (definição do analista da projeção)",
           f"DEPOIS = {d['rot']}: {d['anos']} (definição única do motor, eventos.csv: ONI_OND_NDJ ≥ 1,5)",
           "Nota: a classe do DEPOIS usa o ONI de out–dez/nov–jan, que só fecha em janeiro; em nov/2026 o ago–out já está em "
           f"+{ONI_2026:.2f}, então a classe de 2027 é certa. 'El Niño forte' em cada coluna = os anos da própria definição.".replace("2.", "2,"),
           "",
           "== Fatores do alargamento conforme (quantil 80% dos escores do WF 2008–2025, × mediana do município) ==",
           f"{'':58s} {'ANTES':>8s} {'DEPOIS':>8s}",
           tabela(a, d, [("D (2027): P10/P90, bilateral", lambda r: f"{r['fat']['D_enso'][0]:.3f}"),
                         ("D (2027): P20/P80, só o piso", lambda r: f"{r['fat']['D_enso'][1]:.3f}"),
                         ("C (2028–29): P10/P90, bilateral", lambda r: f"{r['fat']['C_hier'][0]:.3f}"),
                         ("C (2028–29): P20/P80, só o piso", lambda r: f"{r['fat']['C_hier'][1]:.3f}")]),
           "(o analista registrou 0,155/0,079 para o D e 0,104/0,056 para o C, em analise/projecao.md)",
           "",
           "== Resumo: antes × depois ==",
           f"{'':58s} {'ANTES':>8s} {'DEPOIS':>8s}",
           tabela(ma, md, L),
           ""]
    for k, r in run.items():
        m = r["m"]
        txt += [f"######## {k.upper()}: {r['rot']} {r['anos']}", ""]
        for modo in ["LOYO", "WF"]:
            txt += [f"--- {modo}: cobertura 80% (todas as linhas / média dos anos / pior ano / anos < 0,6 / milho)",
                    pd.DataFrame({"geral": m[modo]["geral"], "media_anos": m[modo]["media_anos"], "pior": m[modo]["pior"],
                                  "anos_lt60": m[modo]["lt60"], "milho": m[modo]["milho"]}).round(3).to_string(), "",
                    f"--- {modo}: por grupo de anos (3 culturas)", m[modo]["grupo"].round(3).to_string(), "",
                    f"--- {modo}: cada El Niño forte da definição única (3 culturas)", m[modo]["en_ano"].round(2).to_string(), "",
                    f"--- {modo}: milho, quebra prevista × observada nos El Niños fortes", m[modo]["milho_en_ano"].round(2).to_string(), "",
                    f"--- {modo}: cobertura 80% por ano", m[modo]["cy"].round(2).to_string(), ""]
    METR.write_text("\n".join(txt), encoding="utf-8")
    print(METR, f"{METR.stat().st_size / 1e3:.0f} kB")
    out = projetar(d["fat"])
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, allow_nan=False, separators=(",", ":")), encoding="utf-8")
    print(f"{sum(1 for c in out if not c.startswith('_') and any(out[c][x] for x in CULT))} municípios com projeção; "
          f"{SAIDA} {SAIDA.stat().st_size / 1e6:.2f} MB; {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
