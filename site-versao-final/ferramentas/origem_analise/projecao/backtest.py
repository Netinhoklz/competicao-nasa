"""Backtest de métodos de projeção do rendimento por ha plantado (PAM municipal, 1998–2025), NE.
Modos: LOYO (deixa o ano de fora) e WF (walk-forward, só o passado, alvo 2008–2025).
Saída: bt_linhas.parquet (uma linha por método × modo × cultura × município × ano) e métricas impressas."""
import warnings, time
import numpy as np, pandas as pd
import statsmodels.api as sm
warnings.filterwarnings("ignore")
OUT = "C:/Users/NETINH~1/AppData/Local/Temp/claude/88b277d27b184113/73cd62bd-b6e9-4872-9e4a-a06e5ca404a0/scratchpad/analise10/projecao/"
D = "c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados/"
QS = np.array([0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9])
ANOS = np.arange(1998, 2026)
EN_FORTE = {1998, 2010, 2016, 2024}
SECA = {2012, 2013, 2014, 2015}
K = 10  # encolhimento: peso do município = n/(n+K)

I = pd.read_parquet(D + "indices_clima_mensal.parquet")
o = I[I.variavel == "ONI"].set_index("data").valor
ASO = o[o.index.month == 9]; ASO.index = ASO.index.year + 1
ONI = ASO.reindex(ANOS).values
FORTE_ASO = ONI >= 1.0  # o que se sabe em novembro: 1998, 2016, 2024
REF = pd.read_parquet(D + "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
P = pd.read_parquet("E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet")


def matriz(cult):
    v = P[(P.produto == cult) & (P.area_plantada_ha > 0)]
    Y = v.pivot(index="cod_mun", columns="ano", values="rend_plantado_kg_ha").reindex(columns=ANOS)
    Y = Y[Y.notna().sum(axis=1) >= 20]
    return Y


def tendencia(Ytr, cols, t, med):
    """OLS de log(y) contra o ano por município, nos anos de treino; nível previsto em t e razões y/ajuste."""
    L = np.log(np.clip(Ytr, 0.05 * med[:, None], None))
    x = np.where(np.isnan(L), np.nan, cols[None, :].astype(float))
    xm, lm = np.nanmean(x, 1), np.nanmean(L, 1)
    b = np.nansum((x - xm[:, None]) * (L - lm[:, None]), 1) / np.nansum((x - xm[:, None]) ** 2, 1)
    fit = lm[:, None] + b[:, None] * (cols[None, :] - xm[:, None])
    lvl = np.exp(lm + b * (t - xm))
    return lvl, Ytr / np.exp(fit)


def frac_below(R, thr):
    ok = ~np.isnan(R)
    return np.where(ok.sum(1) > 0, np.nansum(R < thr, 1) / np.maximum(ok.sum(1), 1), np.nan)


def pool_meso(R, meso, mask_cols=None):
    """Quantis e P(R<0,5) do conjunto de razões da mesorregião (todos os municípios e anos de treino)."""
    qm = np.full((len(QS), R.shape[0]), np.nan); pm = np.full(R.shape[0], np.nan)
    Rr = R if mask_cols is None else R[:, mask_cols]
    for m in np.unique(meso):
        ix = meso == m
        z = Rr[ix].ravel(); z = z[~np.isnan(z)]
        if len(z) < 5:
            continue
        qm[:, ix] = np.quantile(z, QS)[:, None]; pm[ix] = (z < 0.5).mean()
    return qm, pm


def cdf_from_q(qrel):
    """P(R<0,5) interpolando a CDF pelos quantis previstos (qrel: len(QS) × M, crescente)."""
    out = np.empty(qrel.shape[1])
    for j in range(qrel.shape[1]):
        qq = np.maximum.accumulate(qrel[:, j])
        out[j] = np.interp(0.5, qq, QS, left=QS[0] / 2, right=1 - (1 - QS[-1]) / 2)
    return out


linhas = []
t0 = time.time()
for cult in ["Milho", "Feijão", "Mandioca"]:
    Yd = matriz(cult)
    Y = Yd.values; mun = Yd.index.values
    meso = REF.loc[mun, "cod_meso"].values
    semi = REF.loc[mun, "semiarido_2022"].values.astype(float)
    uf = REF.loc[mun, "uf"].values
    for modo in ["LOYO", "WF"]:
        alvos = ANOS if modo == "LOYO" else ANOS[ANOS >= 2008]
        hist_scores = []  # para o conforme (WF): escores dos anos anteriores
        for t in alvos:
            jt = int(np.where(ANOS == t)[0][0])
            tr = (ANOS != t) if modo == "LOYO" else (ANOS < t)
            cols = ANOS[tr]; Ytr = Y[:, tr]
            n = (~np.isnan(Ytr)).sum(1)
            med = np.nanmedian(Ytr, 1)
            y = Y[:, jt]
            ok = (~np.isnan(y)) & (n >= 8) & (med > 0)
            R = Ytr / med[:, None]
            w = n / (n + K)
            res = {}
            # A: quantis empíricos do município
            res["A_mun"] = (np.nanquantile(Ytr, QS, axis=1), frac_below(R, 0.5))
            # B: tendência removida (nível do ano t × razões ao ajuste)
            lvl, E = tendencia(Ytr, cols, t, med)
            qB = lvl[None, :] * np.nanquantile(E, QS, axis=1)
            pB = frac_below(E * lvl[:, None] / med[:, None], 0.5)
            res["B_tend"] = (qB, pB)
            # C: encolhimento para a mesorregião (média de quantis ponderada por n/(n+K))
            qm, pm = pool_meso(R, meso)
            qmu = np.nanquantile(R, QS, axis=1)
            res["C_hier"] = (med[None, :] * (w * qmu + (1 - w) * qm), w * frac_below(R, 0.5) + (1 - w) * pm)
            # D: condicionado ao ONI de ago–out (classe forte ≥ 1,0 contra o resto), mesorregião + município
            cls = FORTE_ASO[tr] == FORTE_ASO[jt]
            qmD, pmD = pool_meso(R, meso, cls)
            Rc = R[:, cls]; nc = (~np.isnan(Rc)).sum(1); wc = nc / (nc + K)
            qmuD = np.where(nc[None, :] > 0, np.nanquantile(np.where(nc[:, None] > 0, Rc, 1.0), QS, axis=1), 1.0)
            res["D_enso"] = (med[None, :] * (wc * qmuD + (1 - wc) * qmD), wc * np.nan_to_num(frac_below(Rc, 0.5)) + (1 - wc) * pmD)
            # D2: D com o nível pela tendência (lvl no lugar da mediana)
            res["D2_enso_tend"] = (lvl[None, :] * (wc * qmuD + (1 - wc) * qmD),
                                   cdf_from_q((lvl[None, :] * (wc * qmuD + (1 - wc) * qmD)) / med[None, :]))
            # E: regressão quantílica do log da razão, NE inteiro, com ONI, ONI+ (acima de 0,5), semiárido×ONI+ e ano
            rr, cc = np.where(~np.isnan(R))
            lr = np.log(np.clip(R[rr, cc], 0.05, None))
            on = ONI[tr][cc]
            X = np.column_stack([np.ones_like(lr), on, np.clip(on - 0.5, 0, None), semi[rr] * np.clip(on - 0.5, 0, None),
                                 (cols[cc] - 2010) / 10.0])
            xo = ONI[jt]
            Xt = np.column_stack([np.ones(len(mun)), np.full(len(mun), xo), np.full(len(mun), max(xo - 0.5, 0)),
                                  semi * max(xo - 0.5, 0), np.full(len(mun), (t - 2010) / 10.0)])
            qE = np.empty((len(QS), len(mun)))
            for k, q in enumerate(QS):
                b = sm.QuantReg(lr, X).fit(q=q, max_iter=2000).params
                qE[k] = Xt @ b
            qE = np.exp(np.maximum.accumulate(qE, axis=0))
            res["E_qr"] = (med[None, :] * qE, cdf_from_q(qE))
            # F: conforme (só WF): alarga o intervalo 10–90 de D pelo quantil 80% dos escores dos anos anteriores
            if modo == "WF":
                qD = res["D_enso"][0]
                if hist_scores:
                    s = np.concatenate(hist_scores)
                    Qh = np.quantile(s, min(1, np.ceil((len(s) + 1) * 0.8) / len(s)))
                else:
                    Qh = 0.0
                qF = qD.copy(); qF[0] = qD[0] - Qh * med; qF[-1] = qD[-1] + Qh * med
                qF[1] = qD[1] - Qh * med
                res["F_conf"] = (qF, res["D_enso"][1])
                sc = np.maximum((qD[0] - y) / med, (y - qD[-1]) / med)
                hist_scores.append(sc[ok])
            for nome, (q, pq) in res.items():
                d = pd.DataFrame({"metodo": nome, "modo": modo, "cultura": cult, "cod_mun": mun[ok], "uf": uf[ok], "ano": t,
                                  "y": y[ok], "med": med[ok], "pq": pq[ok]})
                for k, qq in enumerate(QS):
                    d[f"q{int(qq*100)}"] = q[k][ok]
                linhas.append(d)
        print(cult, modo, f"{time.time()-t0:.0f}s", flush=True)

B = pd.concat(linhas, ignore_index=True)
B.to_parquet(OUT + "bt_linhas.parquet")
print("linhas", len(B))
