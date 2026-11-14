"""Rodada 2, pesquisador de IA. Estado da agua x chuva acumulada, com mais anos.

O teste do SMAP (v2_pesquisador_ia_smap_escore.py) tem so 10 quadras e e dominado por 2016. Aqui:
  (A) 2004-2025 (22 quadras): a zona da raiz do GLDAS-2.2 CLSM diario (G_p) e um indice de chuva antecedente do
      proprio IMERG (API, memoria exponencial de 30 dias, fixada a priori) contra a chuva acumulada desde 1/jan (R);
  (B) 2016-2025, mesmos municipio-anos: SMAP L4 (S_p) contra R, API e G_p.
Pergunta de fundo: se o SMAP ganha da chuva acumulada, o ganho e "satelite de umidade" ou so "estado em vez de soma"?
Se o API do IMERG faz o mesmo, o ganho e do ESTADO; o SMAP so acrescenta se ganhar do API nas mesmas amostras.

Metricas (sem pesos ajustados, porque com poucos anos os pesos LOYO sao instaveis e a probabilidade LOYO sofre o
artefato de intercepto, ver docstring de v2_pesquisador_ia_smap_escore.py):
  * AUC crua de cada variavel (sinal fixado a priori: mais seco = mais risco);
  * combinacao "soma z" com pesos iguais;
  * AUC agregada e AUC dentro do ano; IC90 por bootstrap de ANOS (2000), deltas pareados nas mesmas amostras.
Variaveis: todas no portao (31/jan, 19/mar, 30/abr); G_p e API em percentil entre os OUTROS anos do mesmo municipio
(G_p: 2004-2026; API: 1998-2025); S_p = sm_rootzone_pctl do produto (media dos 7 dias ate o portao).
Atencao: o CLSM ASSIMILA o GRACE e tem forcante de chuva propria (nao e o IMERG).
So le arquivos; grava saidas/v2_pesquisador_ia_gldas_portoes_longo.csv.
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
from scipy.signal import lfilter
from scipy.stats import rankdata, spearmanr

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 230)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
S = A + "saidas/"
rng = np.random.default_rng(2026)
PORT = {"31/jan": (1, 31), "19/mar": (3, 19), "30/abr": (4, 30)}
TAU = 30.0  # dias, memoria do API (fixada a priori)

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
chuva = chuva.asfreq("D")
anos_c = list(range(1998, 2026))
k = np.exp(-1 / TAU)
API = pd.DataFrame(lfilter([1.0], [1.0, -k], chuva.fillna(0).values, axis=0), index=chuva.index, columns=chuva.columns)


def pct_outros(w, anos):
    """percentil (0-100) de cada ano entre os OUTROS anos, por coluna."""
    w = w.astype("float64")
    out = w.copy() * np.nan
    for a in anos:
        o = w.drop(index=a)
        out.loc[a] = (o.lt(w.loc[a], axis=1).sum() + 0.5 * o.eq(w.loc[a], axis=1).sum()) / o.notna().sum() * 100
    return out


def janela(df, a, m, d, n=7):
    fim = pd.Timestamp(a, m, d)
    return df.loc[fim - pd.Timedelta(days=n - 1):fim].mean()


def cel_mun(lat, lon, ok):
    LL, LA = np.meshgrid(lon, lat)
    pts = gpd.GeoDataFrame({"iy": np.repeat(np.arange(len(lat)), len(lon)), "ix": np.tile(np.arange(len(lon)), len(lat))},
                           geometry=gpd.points_from_xy(LL.ravel(), LA.ravel()), crs="EPSG:4326")
    pts = pts[ok[pts.iy, pts.ix]]
    mun = municipios_ce_gdf()[["codarea", "geometry"]]
    mun["cod"] = mun.codarea.astype(str).str[:7]
    jn = gpd.sjoin(pts, mun, predicate="within")
    cel = {c: list(zip(g.iy, g.ix)) for c, g in jn.groupby("cod")}
    oky, okx = np.where(ok)
    sem = [c for c in mun.cod if c not in cel]
    for c in sem:
        rp = mun.loc[mun.cod == c].geometry.iloc[0].representative_point()
        j = int(np.argmin((lat[oky] - rp.y) ** 2 + (lon[okx] - rp.x) ** 2))
        cel[c] = [(oky[j], okx[j])]
    return cel, len(sem)


def serie_mun(v, tt, cel):
    return pd.DataFrame({c: np.nanmean(np.stack([v[:, iy, ix] for iy, ix in cel[c]], 1), 1) for c in sorted(cel)}, index=tt)


with Cronometro("GLDAS CLSM + SMAP L4 recortes CE"):
    g = xr.open_dataset("E:/campeonato-nasa/dados/gldas/gldas_clsm025_diario_ne.nc")["SoilMoist_RZ_tavg"].sel(
        lat=slice(-8.1, -2.4), lon=slice(-41.7, -37.0)).load()
    sm = xr.open_dataset("E:/campeonato-nasa/dados/smap/smap_l4_diario_ne.nc")["sm_rootzone_pctl"].sel(
        lat=slice(-2.4, -8.1), lon=slice(-41.7, -37.0), time=slice("2016-01-01", "2026-05-05")).load()
celg, semg = cel_mun(g.lat.values, g.lon.values, np.isfinite(g.values).mean(0) > 0.9)
cels, sems = cel_mun(sm.lat.values, sm.lon.values, np.isfinite(sm.values).mean(0) > 0.5)
print(f"GLDAS: {184 - semg} municipios com centro de celula, {semg} pela celula mais proxima | SMAP: {184 - sems} e {sems}")
GZ = serie_mun(g.values, pd.DatetimeIndex(g.time.values), celg)
SP = serie_mun(sm.values, pd.DatetimeIndex(sm.time.values), cels)

linhas = []
for gn, (m, d) in PORT.items():
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_c}).T
    R = ac.copy() * np.nan
    for a in anos_c:
        R.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    api = pct_outros(pd.DataFrame({a: API.loc[f"{a}-{m:02d}-{d:02d}"] for a in anos_c}).T, anos_c)
    ag = list(range(2004, 2027))
    gp = pct_outros(pd.DataFrame({a: janela(GZ, a, m, d) for a in ag}).T, ag)
    sp = pd.DataFrame({a: janela(SP, a, m, d) for a in range(2016, 2026)}).T
    for a in range(2004, 2026):
        for c in sorted(celg):
            linhas.append({"portao": gn, "ano": a, "cod": c, "pct": R.loc[a, c], "api_p": api.loc[a, c], "g_p": gp.loc[a, c],
                           "s_p": sp.loc[a, c] if a >= 2016 else np.nan})
X = pd.DataFrame(linhas)
# sinais fixados a priori: maior = mais seco
X["R"] = -X.pct.clip(upper=3)
X["API"] = -X.api_p
X["G"] = -X.g_p
X["S"] = -X.s_p


def auc(y, p):
    npos = y.sum(); nneg = len(y) - npos
    if npos == 0 or nneg == 0:
        return np.nan
    r = rankdata(p)
    return (r[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg)


def por_ano(y, s, ano, anos):
    out = {}
    for a in anos:
        kk = ano == a
        npos = y[kk].sum(); nneg = kk.sum() - npos
        ok = npos >= 3 and nneg >= 3
        out[a] = (auc(y[kk], s[kk]) if ok else np.nan, npos * nneg if ok else 0.0)
    return out


def dentro(st, yrs):
    au = np.array([st[a][0] for a in yrs]); w = np.array([st[a][1] for a in yrs], float)
    return np.nansum(au * w) / w.sum() if w.sum() else np.nan


def zs(df, cols):
    return sum((df[c] - df[c].mean()) / df[c].std() for c in cols).values


def compara(df, sa, sb, anos, nb=2000):
    y, ano = df.quebra.values, df.ano.values
    idx = {a: np.where(ano == a)[0] for a in anos}
    pa, pb = por_ano(y, sa, ano, anos), por_ano(y, sb, ano, anos)
    dA = auc(y, sb) - auc(y, sa); dD = dentro(pb, anos) - dentro(pa, anos)
    b1, b2 = [], []
    for _ in range(nb):
        yrs = rng.choice(anos, len(anos))
        ii = np.concatenate([idx[a] for a in yrs])
        if y[ii].min() == y[ii].max():
            continue
        b1.append(auc(y[ii], sb[ii]) - auc(y[ii], sa[ii])); b2.append(dentro(pb, yrs) - dentro(pa, yrs))
    mel = sum(pb[a][0] > pa[a][0] for a in anos if np.isfinite(pa[a][0]))
    val = sum(np.isfinite(pa[a][0]) for a in anos)
    return dA, np.percentile(b1, [5, 95]), dD, np.nanpercentile(b2, [5, 95]), mel, val


res = []


def bloco(nome, anos, vars_, pares):
    print("\n" + "=" * 20, nome, "=" * 20)
    for cult, Y in CULT.items():
        for gn in PORT:
            df = X[(X.portao == gn) & X.ano.isin(anos)].merge(Y, on=["cod", "ano"]).dropna(subset=vars_).reset_index(drop=True)
            y, ano = df.quebra.values, df.ano.values
            sc = {v: df[v].values for v in vars_}
            for a_, b_ in pares:
                for t in (a_, b_):
                    if t not in sc:
                        sc[t] = zs(df, t.split("+"))
            print(f"\n--- {cult} | {gn} | n = {len(df)} | anos {anos[0]}-{anos[-1]} | taxa {y.mean():.3f}")
            print("    AUC agregada: " + " | ".join(f"{k} {auc(y, v):.3f}" for k, v in sc.items()))
            print("    AUC dentro do ano: " + " | ".join(f"{k} {dentro(por_ano(y, v, ano, anos), anos):.3f}" for k, v in sc.items()))
            for a_, b_ in pares:
                dA, icA, dD, icD, mel, val = compara(df, sc[a_], sc[b_], anos)
                print(f"    {b_:9s} - {a_:7s}: dAUC {dA:+.3f} IC90 [{icA[0]:+.3f},{icA[1]:+.3f}] | d dentro {dD:+.3f} "
                      f"[{icD[0]:+.3f},{icD[1]:+.3f}] | anos com dentro melhor {mel}/{val}")
                res.append({"bloco": nome[:2], "cultura": cult, "portao": gn, "comparacao": f"{b_} vs {a_}", "n": len(df),
                            "auc_a": auc(y, sc[a_]), "auc_b": auc(y, sc[b_]), "dAUC": dA, "lo": icA[0], "hi": icA[1],
                            "d_dentro": dD, "dd_lo": icD[0], "dd_hi": icD[1], "anos_melhor": mel, "anos_validos": val})


bloco("A. 2004-2025 (22 quadras): chuva acumulada x estado (API do IMERG, GLDAS CLSM)", list(range(2004, 2026)),
      ["R", "API", "G"], [("R", "API"), ("R", "G"), ("R", "R+G"), ("API", "API+G")])
bloco("B. 2016-2025 (10 quadras), mesmas amostras: SMAP contra chuva acumulada, API e GLDAS", list(range(2016, 2026)),
      ["R", "API", "G", "S"], [("R", "S"), ("API", "S"), ("G", "S"), ("API", "API+S"), ("R", "R+S")])
pd.DataFrame(res).to_csv(S + "v2_pesquisador_ia_gldas_portoes_longo.csv", index=False)

print("\n" + "=" * 20, "C. Concordancia entre as camadas de estado (Spearman; 2016-2025)", "=" * 20)
for gn in PORT:
    Z = X[(X.portao == gn) & (X.ano >= 2016)].dropna(subset=["S", "G", "API"])
    for a_, b_ in [("S", "API"), ("S", "G"), ("G", "API"), ("S", "R")]:
        rw = np.mean([spearmanr(q[a_], q[b_]).statistic for _, q in Z.groupby("ano")])
        ym = Z.groupby("ano")[[a_, b_]].mean()
        print(f"  {gn} {a_} x {b_}: dentro do ano {rw:+.2f} | entre anos (media estadual, n=10) {spearmanr(ym[a_], ym[b_]).statistic:+.2f}")
