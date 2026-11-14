"""Pesquisador de IA - analise 2: resposta do rendimento ao clima por municipio.
Pergunta: o produto deve usar um coeficiente unico (pooled), um por municipio (no pooling) ou um modelo
hierarquico (partial pooling)? E quao longe a "informacao" de um municipio vale para o vizinho?

Alvo: anomalia do rendimento efetivo (producao / area PLANTADA) = rend / mediana(t-3..t-1, t+1..t+3) - 1
Atributos (IMERG diario, por municipio, anomalias padronizadas no proprio municipio):
  P_fmam, veranico_max_fmam (dias seguidos < 2 mm), n_veranico10_fmam, P_jan
Validacao: deixando um ANO inteiro de fora (todos os municipios), 1998-2025.
Modelos: M0 climatologia (0) | M1 pooled linear | M2 um OLS por municipio | M3 hierarquico MAP
(ridge em direcao ao coeficiente pooled = prior gaussiano com variancia tau^2) | M4 HistGradientBoosting pooled
com lat/lon/altitude.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
import warnings
warnings.filterwarnings("ignore")

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
P = pd.read_parquet(OUT / "painel_mun_ce.parquet")
FEAT = ["P_fmam", "veranico_max_fmam", "n_veranico10_fmam", "P_jan"]
for c in FEAT:
    g = P.groupby("cod")[c]
    P[c + "_z"] = (P[c] - g.transform("mean")) / g.transform("std")
FZ = [c + "_z" for c in FEAT]
LIM = {"milho": 6000, "feijao": 2500}
JAN = int(sys.argv[1]) if len(sys.argv) > 1 else 3  # meia-janela da referencia (anos)


def anomalia(df, cult):
    d = df.sort_values(["cod", "ano"]).copy()
    y = d[f"rend_{cult}"].where((d[f"aplant_{cult}"] > 0) & (d[f"rend_{cult}"] <= LIM[cult]))
    d["y"] = y
    ref = []
    for cod, g in d.groupby("cod"):
        s = g.set_index("ano")["y"]
        for a in s.index:
            viz = s[[x for x in range(a - JAN, a + JAN + 1) if x != a and x in s.index]].dropna()
            ref.append((cod, a, viz.median() if len(viz) >= 3 else np.nan))
    R = pd.DataFrame(ref, columns=["cod", "ano", "ref"])
    d = d.merge(R, on=["cod", "ano"])
    d["anom"] = (d.y / d.ref - 1).clip(-1, 2)
    area_med = d.groupby("cod")[f"aplant_{cult}"].transform("median")
    return d[(area_med >= 300) & d.anom.notna() & (d.ref > 0)].copy()


def ajusta_hier(Xtr, ytr, gtr, lam):
    """MAP de beta_m ~ N(beta_pool, tau^2 I): beta_m = (X'X + lam I)^-1 (X'y + lam beta_pool)."""
    Xa = np.c_[np.ones(len(Xtr)), Xtr]
    bpool = np.linalg.lstsq(Xa, ytr, rcond=None)[0]
    coefs = {}
    for g in np.unique(gtr):
        m = gtr == g
        Xg, yg = Xa[m], ytr[m]
        A = Xg.T @ Xg + lam * np.eye(Xa.shape[1])
        coefs[g] = np.linalg.solve(A, Xg.T @ yg + lam * bpool)
    return bpool, coefs


def prevê(X, g, bpool, coefs):
    Xa = np.c_[np.ones(len(X)), X]
    return np.array([Xa[i] @ coefs.get(g[i], bpool) for i in range(len(X))])


resumo = []
for cult in ["milho", "feijao"]:
    d = anomalia(P, cult).reset_index(drop=True)
    X, y, g = d[FZ].values, d.anom.values, d.cod.values
    XS = d[FZ + ["lat", "lon", "elev"]].values
    preds = {k: np.zeros(len(d)) for k in ["M0", "M1", "M2", "M3_l5", "M3_l20", "M3_l80", "M4"]}
    for a in sorted(d.ano.unique()):
        tr, te = (d.ano != a).values, (d.ano == a).values
        bp, _ = ajusta_hier(X[tr], y[tr], g[tr], 1e9)
        preds["M1"][te] = np.c_[np.ones(te.sum()), X[te]] @ bp
        _, c0 = ajusta_hier(X[tr], y[tr], g[tr], 1e-6)
        preds["M2"][te] = prevê(X[te], g[te], bp, c0)
        for lam in [5, 20, 80]:
            _, cl = ajusta_hier(X[tr], y[tr], g[tr], lam)
            preds[f"M3_l{lam}"][te] = prevê(X[te], g[te], bp, cl)
        gb = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=15,
                                           min_samples_leaf=40, random_state=0).fit(XS[tr], y[tr])
        preds["M4"][te] = gb.predict(XS[te])
    mse0 = np.mean(y ** 2)
    print(f"\n== {cult}: {len(d)} municipio-anos, {d.cod.nunique()} municipios, {d.ano.nunique()} anos")
    for k, p in preds.items():
        mse = np.mean((y - p) ** 2)
        print(f"  {k:7s} RMSE={np.sqrt(mse):.3f}  MSSS={1-mse/mse0:+.3f}  r={np.corrcoef(y,p)[0,1] if p.std()>0 else 0:+.2f}")
        resumo.append({"cultura": cult, "modelo": k, "rmse": np.sqrt(mse), "msss": 1 - mse / mse0})
    # heterogeneidade: dispersao dos coeficientes municipais (lam=20, todos os anos) para P_fmam e veranico
    bp, cl = ajusta_hier(X, y, g, 20)
    C = pd.DataFrame(cl, index=["b0"] + FZ).T
    print("  coef. pooled (por 1 dp):", dict(zip(["b0"] + FZ, np.round(bp, 3))))
    print("  dispersao municipal (p10, p50, p90) de P_fmam_z:", np.round(C["P_fmam_z"].quantile([.1, .5, .9]).values, 3),
          "| veranico_max_z:", np.round(C["veranico_max_fmam_z"].quantile([.1, .5, .9]).values, 3))
    # elasticidade em unidades fisicas: % por +100 mm e % por +5 dias de veranico (pooled)
    sdP = P.groupby("cod").P_fmam.std().median()
    sdV = P.groupby("cod").veranico_max_fmam.std().median()
    print(f"  pooled: {bp[1]/sdP*100*100:+.1f}% por +100 mm de fev-mai | {bp[2]/sdV*5*100:+.1f}% por +5 dias no maior veranico")
    d[f"res"] = y - preds["M3_l20"]
    d.to_parquet(OUT / f"anom_{cult}_j{JAN}.parquet")

# Decorrelacao espacial das anomalias de rendimento (milho): correlacao entre pares de municipios x distancia
d = pd.read_parquet(OUT / f"anom_milho_j{JAN}.parquet")
W = d.pivot_table(index="ano", columns="cod", values="anom")
Wr = d.pivot_table(index="ano", columns="cod", values="res")
cods = [c for c in W.columns if W[c].notna().sum() >= 20]
cent = d.groupby("cod")[["lat", "lon"]].first().loc[cods]
la, lo = np.radians(cent.lat.values), np.radians(cent.lon.values)
dist = 6371 * np.arccos(np.clip(np.sin(la[:, None]) * np.sin(la) + np.cos(la[:, None]) * np.cos(la) * np.cos(lo[:, None] - lo), -1, 1))
Cm = W[cods].corr(min_periods=15).values
Cr = Wr[cods].corr(min_periods=15).values
iu = np.triu_indices(len(cods), 1)
T = pd.DataFrame({"dist": dist[iu], "r_anom": Cm[iu], "r_res": Cr[iu]}).dropna()
T["faixa"] = pd.cut(T.dist, [0, 25, 50, 100, 150, 200, 300, 600])
print("\n== correlacao entre municipios (milho) por distancia")
print(T.groupby("faixa", observed=True).agg(pares=("dist", "size"), r_anomalia=("r_anom", "median"), r_residuo=("r_res", "median")).round(2).to_string())
pd.DataFrame(resumo).to_csv(OUT / f"hierarquico_resumo_j{JAN}.csv", index=False)
