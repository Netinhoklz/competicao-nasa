"""Rodada 2, pesquisador de IA. Prototipo da adaptacao de Kluger, Di Tommaso & Lobell 2025 (ERL 20:114037; floresta
causal do 'precrop payoff') ao IBGE PAM, com o que existe no venv (sem grf/econml: R-learner / DML com
heterogeneidade linear, que e o caso parametrico da floresta causal).

Pergunta: no municipio, ter mais feijao (leguminosa) na safra ANTERIOR muda o rendimento relativo do milho na safra
seguinte, e esse efeito depende da agua da estacao (como Kluger achou para a chuva)?
Desenho (fixado a priori):
- Unidade: municipio-ano, 1999-2025 (precisa de t-1 e t-2). Area de milho e feijao >= 50 ha nos dois anos.
- Y = razao canonica do milho em t (cortada em [0, 3]).
- T = fracao de feijao na area plantada de milho + feijao em t-1 (o 'antecessor' na escala do municipio).
- Modificador X = percentil do API30 do IMERG em 30/abr de t (estado da agua na quadra; 0 = mais seco).
- Confundidores W: T em t-2, fracao media do municipio (todos os anos), razao do milho e do feijao em t-1, API de t-1,
  log da area de milho em t-1, lat/lon do centroide, ano.
- Cross-fitting por ANO (GroupKFold, 5 grupos de anos); nuisances = HistGradientBoosting.
- Estagio final: Y~ = (theta0 + theta1 * (X - 0,5)) * T~, MQO sem intercepto; IC90 por bootstrap de ANOS do estagio final.
- Placebo: T do FUTURO (fracao de feijao em t+1) no lugar de T, com T(t-1) entre os confundidores. Se 'afeta' o milho de t, o desenho capta
  retroalimentacao (o agricultor reage a safra ruim), nao efeito do antecessor.
So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
from scipy.signal import lfilter
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GroupKFold

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
rng = np.random.default_rng(11)
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")


def serie(prefixo):
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        out = np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])
        return pd.Series(out, index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref
    p["cod"] = p.cod_local.astype(str).str[:7]
    return p.dropna(subset=["razao"])[["cod", "ano", "razao", "area_plantada_ha"]]


mi = serie("Milho (em gr").rename(columns={"razao": "r_mi", "area_plantada_ha": "a_mi"})
fe = serie("Feij").rename(columns={"razao": "r_fe", "area_plantada_ha": "a_fe"})
P = mi.merge(fe, on=["cod", "ano"])
P["share"] = P.a_fe / (P.a_fe + P.a_mi)
P = P.set_index(["cod", "ano"]).sort_index()

chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
chuva = chuva.asfreq("D")
API = pd.DataFrame(lfilter([1.0], [1.0, -np.exp(-1 / 30.0)], chuva.fillna(0).values, axis=0), index=chuva.index, columns=chuva.columns)
anos = list(range(1998, 2026))
ap = pd.DataFrame({a: API.loc[f"{a}-04-30"] for a in anos}).T.astype("float64")
apct = ap.copy() * np.nan
for a in anos:
    o = ap.drop(index=a)
    apct.loc[a] = (o.lt(ap.loc[a], axis=1).sum() + 0.5 * o.eq(ap.loc[a], axis=1).sum()) / o.notna().sum()
W_api = apct.stack().rename("api").rename_axis(["ano", "cod"]).reset_index()

mun = municipios_ce_gdf()
mun["cod"] = mun.codarea.astype(str).str[:7]
cent = mun.to_crs(5880).geometry.centroid.to_crs(4326)
geo = pd.DataFrame({"cod": mun.cod, "lon": cent.x.values, "lat": cent.y.values})

rows = []
for (c, a), r in P.iterrows():
    def g(col, aa):
        return P[col].get((c, aa), np.nan)
    rows.append({"cod": c, "ano": a, "Y": min(r.r_mi, 3.0), "T": g("share", a - 1), "T_fut": g("share", a + 1),
                 "T2": g("share", a - 2), "rmi1": g("r_mi", a - 1), "rfe1": g("r_fe", a - 1), "lami1": np.log(g("a_mi", a - 1))})
Z = pd.DataFrame(rows)
Z = Z.merge(W_api, on=["ano", "cod"], how="left").merge(
    W_api.assign(ano=W_api.ano + 1).rename(columns={"api": "api1"}), on=["ano", "cod"], how="left").merge(geo, on="cod")
Z["share_med"] = Z.cod.map(P.share.groupby(level=0).mean())
Z = Z[(Z.ano >= 1999)]
WCOLS = ["T2", "share_med", "rmi1", "rfe1", "api1", "lami1", "lat", "lon", "ano", "api"]


def dml(df, tcol, nome, extra=()):
    W = WCOLS + list(extra)
    df = df.dropna(subset=["Y", tcol] + W).reset_index(drop=True)
    yr, tr = np.zeros(len(df)), np.zeros(len(df))
    for itr, ite in GroupKFold(n_splits=5).split(df, groups=df.ano):
        for alvo, out in (("Y", yr), (tcol, tr)):
            m = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, random_state=0)
            m.fit(df.loc[itr, W], df.loc[itr, alvo])
            out[ite] = df.loc[ite, alvo].values - m.predict(df.loc[ite, W])
    xc = df.api.values - 0.5
    M = np.column_stack([tr, tr * xc])
    th = np.linalg.lstsq(M, yr, rcond=None)[0]
    idx = {a: np.where(df.ano.values == a)[0] for a in df.ano.unique()}
    yrs = list(idx)
    bs = []
    for _ in range(2000):
        ii = np.concatenate([idx[a] for a in rng.choice(yrs, len(yrs))])
        bs.append(np.linalg.lstsq(M[ii], yr[ii], rcond=None)[0])
    bs = np.array(bs)
    lo, hi = np.percentile(bs, 5, 0), np.percentile(bs, 95, 0)
    r2t = 1 - np.var(tr) / np.var(df[tcol])
    print(f"\n  {nome}: n = {len(df)} mun-anos, {df.cod.nunique()} municipios, {len(yrs)} anos | "
          f"fracao da variancia de T explicada pelos confundidores: {r2t:.2f} (sobra {np.std(tr):.3f} de dp em T)")
    for k, nm in enumerate(["theta0 (efeito no ano mediano de agua)", "theta1 (muda do ano mais seco ao mais umido)"]):
        print(f"    {nm}: {th[k] * 0.1:+.4f} na razao do milho por +10 p.p. de feijao | IC90 [{lo[k] * 0.1:+.4f}, {hi[k] * 0.1:+.4f}]")
    for q, xq in [("ano seco (API p10)", 0.1), ("ano mediano", 0.5), ("ano umido (API p90)", 0.9)]:
        e = (th[0] + th[1] * (xq - 0.5)) * 0.1
        eb = (bs[:, 0] + bs[:, 1] * (xq - 0.5)) * 0.1
        print(f"    efeito por +10 p.p. de feijao em t-1, {q}: {e:+.4f} IC90 [{np.percentile(eb, 5):+.4f}, {np.percentile(eb, 95):+.4f}]")
    return th


print("=" * 20, "Precrop payoff municipal (DML/R-learner, cross-fitting por ano)", "=" * 20)
print(f"  fracao de feijao (milho+feijao): mediana {Z['T'].median():.2f}; dp entre anos dentro do municipio "
      f"{Z.groupby('cod')['T'].std().median():.3f}; correlacao T(t-1) x T(t-2) {Z[['T', 'T2']].corr().iloc[0, 1]:.2f}")
dml(Z, "T", "PRINCIPAL: feijao em t-1 -> milho em t")
dml(Z, "T_fut", "PLACEBO: feijao em t+1 -> milho em t (controlando T de t-1)", extra=["T"])
