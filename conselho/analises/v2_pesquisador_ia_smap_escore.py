"""Rodada 2, pesquisador de IA. TESTE CENTRAL (versao que vale): o SMAP L4 (zona da raiz) acrescenta habilidade alem
da chuva IMERG acumulada para prever a QUEBRA CANONICA municipal de milho e feijao nos portoes 31/jan, 19/mar e 30/abr?

POR QUE ESTA VERSAO EXISTE: em v2_pesquisador_ia_smap_portoes.py e na 1a rodada de v2_pesquisador_ia_gldas_portoes_longo.py,
a AUC AGREGADA das probabilidades da logistica LOYO caiu abaixo de 0,5 (ex.: chuva sozinha 0,33 em 31/jan, quando a AUC
da propria variavel e 0,57). E o artefato do deixa-um-de-fora com poucos anos: quando o ano de teste e de seca, a taxa
de quebra do treino cai, o intercepto cai e o ano inteiro recebe probabilidade menor -> anticorrelacao entre anos.
Com 10 anos isso domina. Correcao (decidida ANTES de ver os deltas desta versao):
  * escore de ORDEM = soma dos coeficientes na escala original vezes as variaveis, SEM intercepto (pesos LOYO);
  * escore SEM AJUSTE = soma de z-escores com pesos iguais (receita "soma z" de arquiteto_final_curvas_quixada.py);
  * AUC de cada variavel crua;
  * a calibracao (Brier da probabilidade LOYO) fica como metrica operacional secundaria.
Resto do protocolo igual: anos 2016-2025, quebra canonica, R = chuva IMERG desde 1/jan em % do normal;
S_p = sm_rootzone_pctl (media dos 7 dias ate o portao); S_a = anomalia da zona da raiz contra a mediana dos outros anos
2016-2026; IC90 por bootstrap de ANOS (2000), comparacao pareada com as mesmas amostras.
So le arquivos; grava saidas/v2_pesquisador_ia_smap_escore.csv.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from scipy.stats import rankdata, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 230)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
S = A + "saidas/"
rng = np.random.default_rng(2026)
ANOS_T = list(range(2016, 2026))
ANOS_SMAP = list(range(2016, 2027))
PORT = {"31/jan": (1, 31), "19/mar": (3, 19), "30/abr": (4, 30)}

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
    p["quebra"] = (p.razao < 0.5).astype(int)
    p["cod"] = p.cod_local.astype(str).str[:7]
    return p.dropna(subset=["razao"])[["cod", "ano", "razao", "quebra"]]


CULT = {"milho": serie("Milho (em gr"), "feijao": serie("Feij")}
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
anos_c = list(range(1998, 2026))


def pct_normal(m, d):
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_c}).T
    out = ac.copy() * np.nan
    for a in anos_c:
        out.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return out


with Cronometro("SMAP L4 recorte CE"):
    ds = xr.open_dataset("E:/campeonato-nasa/dados/smap/smap_l4_diario_ne.nc")
    sub = ds[["sm_rootzone", "sm_rootzone_pctl"]].sel(lat=slice(-2.4, -8.1), lon=slice(-41.7, -37.0),
                                                      time=slice("2015-12-01", "2026-05-05")).load()
lat, lon = sub.lat.values, sub.lon.values
LL, LA = np.meshgrid(lon, lat)
pts = gpd.GeoDataFrame({"iy": np.repeat(np.arange(len(lat)), len(lon)), "ix": np.tile(np.arange(len(lon)), len(lat))},
                       geometry=gpd.points_from_xy(LL.ravel(), LA.ravel()), crs="EPSG:4326")
mun = municipios_ce_gdf()[["codarea", "geometry"]]
mun["cod"] = mun.codarea.astype(str).str[:7]
jn = gpd.sjoin(pts, mun, predicate="within")
cel = {c: list(zip(g.iy, g.ix)) for c, g in jn.groupby("cod")}
sem = [c for c in mun.cod if c not in cel]
for c in sem:
    rp = mun.loc[mun.cod == c].geometry.iloc[0].representative_point()
    cel[c] = [(int(np.abs(lat - rp.y).argmin()), int(np.abs(lon - rp.x).argmin()))]
print(f"municipios: {len(mun)}; com centro de celula SMAP: {len(mun) - len(sem)}; via celula mais proxima: {len(sem)}")
tt = pd.DatetimeIndex(sub.time.values)
rz, pc = sub.sm_rootzone.values, sub.sm_rootzone_pctl.values
cods = sorted(cel)
RZ = pd.DataFrame({c: np.nanmean(np.stack([rz[:, iy, ix] for iy, ix in cel[c]], 1), 1) for c in cods}, index=tt)
PC = pd.DataFrame({c: np.nanmean(np.stack([pc[:, iy, ix] for iy, ix in cel[c]], 1), 1) for c in cods}, index=tt)


def janela(df, a, m, d, n=7):
    fim = pd.Timestamp(a, m, d)
    return df.loc[fim - pd.Timedelta(days=n - 1):fim].mean()


linhas = []
for gn, (m, d) in PORT.items():
    P1 = pct_normal(m, d)
    rzw = pd.DataFrame({a: janela(RZ, a, m, d) for a in ANOS_SMAP}).T.astype("float64")
    pcw = pd.DataFrame({a: janela(PC, a, m, d) for a in ANOS_SMAP}).T.astype("float64")
    anom = rzw.copy() * np.nan
    for a in ANOS_SMAP:
        anom.loc[a] = rzw.loc[a] - rzw.drop(index=a).median()
    for a in ANOS_T:
        for c in cods:
            linhas.append({"portao": gn, "ano": a, "cod": c, "pct": P1.loc[a, c], "smap_pctl": pcw.loc[a, c],
                           "smap_anom": anom.loc[a, c]})
X = pd.DataFrame(linhas)
X["s_chuva"] = -X.pct.clip(upper=3)
X["s_seco_p"] = -X.smap_pctl     # maior = mais seco (sinal fixado a priori)
X["s_seco_a"] = -X.smap_anom


# ---------------- metricas
def auc(y, p):
    npos = y.sum(); nneg = len(y) - npos
    if npos == 0 or nneg == 0:
        return np.nan
    r = rankdata(p)
    return (r[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg)


def loyo(df, cols):
    """devolve (escore de ordem sem intercepto, probabilidade calibrada)."""
    s = np.full(len(df), np.nan); p = np.full(len(df), np.nan)
    for a in ANOS_T:
        tr, te = (df.ano != a).values, (df.ano == a).values
        sc = StandardScaler().fit(df.loc[tr, cols])
        lr = LogisticRegression(C=100, max_iter=2000).fit(sc.transform(df.loc[tr, cols]), df.loc[tr, "quebra"])
        w = lr.coef_[0] / sc.scale_
        s[te] = df.loc[te, cols].values @ w
        p[te] = lr.predict_proba(sc.transform(df.loc[te, cols]))[:, 1]
    return s, p


def zsoma(df, cols):
    return sum((df[c] - df[c].mean()) / df[c].std() for c in cols).values


def por_ano(y, s, ano):
    out = {}
    for a in ANOS_T:
        k = ano == a
        npos = y[k].sum(); nneg = k.sum() - npos
        ok = npos >= 3 and nneg >= 3
        out[a] = (auc(y[k], s[k]) if ok else np.nan, npos * nneg if ok else 0.0)
    return out


def dentro(st, yrs):
    au = np.array([st[a][0] for a in yrs]); w = np.array([st[a][1] for a in yrs], float)
    return np.nansum(au * w) / w.sum() if w.sum() else np.nan


def compara(df, sa, sb, nb=2000):
    y, ano = df.quebra.values, df.ano.values
    idx = {a: np.where(ano == a)[0] for a in ANOS_T}
    pa, pb = por_ano(y, sa, ano), por_ano(y, sb, ano)
    d_auc = auc(y, sb) - auc(y, sa)
    d_den = dentro(pb, ANOS_T) - dentro(pa, ANOS_T)
    b1, b2 = [], []
    for _ in range(nb):
        yrs = rng.choice(ANOS_T, len(ANOS_T))
        ii = np.concatenate([idx[a] for a in yrs])
        if y[ii].min() == y[ii].max():
            continue
        b1.append(auc(y[ii], sb[ii]) - auc(y[ii], sa[ii]))
        b2.append(dentro(pb, yrs) - dentro(pa, yrs))
    melhor = sum((pb[a][0] > pa[a][0]) for a in ANOS_T if np.isfinite(pa[a][0]) and np.isfinite(pb[a][0]))
    validos = sum(np.isfinite(pa[a][0]) for a in ANOS_T)
    return d_auc, np.percentile(b1, [5, 95]), np.mean(np.array(b1) > 0), d_den, np.nanpercentile(b2, [5, 95]), melhor, validos


def brier(y, p):
    return np.mean((p - y) ** 2)


res = []
print("\n" + "=" * 20, "A. TESTE CENTRAL 2016-2025 (10 anos): chuva x chuva + SMAP", "=" * 20)
for cult, Y in CULT.items():
    for gn in PORT:
        df = X[X.portao == gn].merge(Y, on=["cod", "ano"]).dropna(subset=["s_chuva", "smap_pctl", "smap_anom"]).reset_index(drop=True)
        y = df.quebra.values
        qa = df.groupby("ano").quebra.agg(["sum", "count"])
        print(f"\n--- {cult} | {gn} | n = {len(df)} mun-anos, {df.cod.nunique()} municipios | taxa {y.mean():.3f}")
        print("    quebras/ano: " + ", ".join(f"{a}:{int(r['sum'])}/{int(r['count'])}" for a, r in qa.iterrows()))
        cru = {c: auc(y, df[c].values) for c in ["s_chuva", "s_seco_p", "s_seco_a"]}
        print("    AUC crua (sem ajuste): " + " | ".join(f"{k} {v:.3f}" for k, v in cru.items()))
        esc, prob = {}, {}
        for k, cols in {"R": ["s_chuva"], "S_p": ["s_seco_p"], "R+S_p": ["s_chuva", "s_seco_p"], "R+S_a": ["s_chuva", "s_seco_a"]}.items():
            esc[k], prob[k] = loyo(df, cols)
        esc["z:R+S_p"] = zsoma(df, ["s_chuva", "s_seco_p"])
        esc["z:R+S_a"] = zsoma(df, ["s_chuva", "s_seco_a"])
        esc["z:R"] = df.s_chuva.values
        bclim = np.mean([brier(y[df.ano == a], df.loc[df.ano != a, "quebra"].mean()) * (df.ano == a).sum() for a in ANOS_T]) * len(ANOS_T) / len(df)
        print("    escore de ordem LOYO: " + " | ".join(f"{k} AUC {auc(y, v):.3f} dentro {dentro(por_ano(y, v, df.ano.values), ANOS_T):.3f}"
                                                 for k, v in esc.items()))
        print("    probabilidade LOYO (operacional): " + " | ".join(f"{k} BSS {1 - brier(y, v) / bclim:+.3f}" for k, v in prob.items()))
        for a_, b_ in [("R", "R+S_p"), ("R", "R+S_a"), ("z:R", "z:R+S_p"), ("z:R", "z:R+S_a")]:
            dA, icA, pA, dD, icD, mel, val = compara(df, esc[a_], esc[b_])
            print(f"    {b_:8s} - {a_:4s}: dAUC {dA:+.3f} IC90 [{icA[0]:+.3f},{icA[1]:+.3f}] P(>0) {pA:.2f} | d AUC dentro do ano {dD:+.3f} "
                  f"[{icD[0]:+.3f},{icD[1]:+.3f}] | anos com AUC-dentro melhor: {mel}/{val}")
            res.append({"cultura": cult, "portao": gn, "comparacao": f"{b_} vs {a_}", "n": len(df), "auc_base": auc(y, esc[a_]),
                        "auc_novo": auc(y, esc[b_]), "dAUC": dA, "lo": icA[0], "hi": icA[1], "P_maior0": pA,
                        "dentro_base": dentro(por_ano(y, esc[a_], df.ano.values), ANOS_T), "d_dentro": dD,
                        "dd_lo": icD[0], "dd_hi": icD[1], "anos_melhor": mel, "anos_validos": val})
        # brier pareado da probabilidade operacional
        bd = brier(y, prob["R+S_p"]) - brier(y, prob["R"])
        print(f"    dBrier operacional (R+S_p - R): {bd:+.4f}")
R = pd.DataFrame(res)
R.to_csv(S + "v2_pesquisador_ia_smap_escore.csv", index=False)
print("\nResumo (deltas pareados, IC90 por bootstrap de anos; 'z:' = pesos iguais sem ajuste):")
print(R.round(3).to_string(index=False))
print("12 comparacoes primarias (2 culturas x 3 portoes x S_p/S_a, escore LOYO) sem correcao de multiplicidade.")

print("\n" + "=" * 20, "B. Onde esta a informacao: nivel do ano (media estadual, n = 10) e redundancia", "=" * 20)
for cult, Y in CULT.items():
    for gn in PORT:
        df = X[X.portao == gn].merge(Y, on=["cod", "ano"]).dropna(subset=["pct", "smap_pctl"])
        ym = df.groupby("ano").agg(fq=("quebra", "mean"), chuva=("pct", "median"), sp=("smap_pctl", "mean"))
        rw = np.mean([spearmanr(g.pct, g.smap_pctl).statistic for _, g in df.groupby("ano")])
        print(f"  {cult} {gn}: entre anos rho(fracao em quebra, chuva) {spearmanr(ym.fq, ym.chuva).statistic:+.2f}, "
              f"rho(fracao, S_p) {spearmanr(ym.fq, ym.sp).statistic:+.2f}, rho(chuva, S_p) {spearmanr(ym.chuva, ym.sp).statistic:+.2f} | "
              f"dentro do ano rho(chuva, S_p) {rw:+.2f}")
        if cult == "milho":
            print("     " + ", ".join(f"{a}: quebra {r.fq:.0%} chuva {r.chuva:.0%} S_p {r.sp:.0f}" for a, r in ym.iterrows()))

print("\n" + "=" * 20, "C. Quixada (2311306), 2016-2025", "=" * 20)
qx = "2311306"
T = pd.DataFrame(index=ANOS_T)
for cult, Y in CULT.items():
    T[cult] = Y[Y.cod == qx].set_index("ano").razao
for gn in PORT:
    q = X[(X.portao == gn) & (X.cod == qx)].set_index("ano")
    T[f"chuva_{gn}"] = q.pct
    T[f"Sp_{gn}"] = q.smap_pctl
q = X[X.portao == "30/abr"].copy()
T["rank_Sp_30abr"] = q.assign(rk=q.groupby("ano").smap_pctl.rank(pct=True)).query("cod == @qx").set_index("ano").rk
T["rank_chuva_30abr"] = q.assign(rk=q.groupby("ano").pct.rank(pct=True)).query("cod == @qx").set_index("ano").rk
print(T.round(2).to_string())
print("  (rank = posicao de Quixada entre os 184 municipios no mesmo ano; 0 = mais seco)")
