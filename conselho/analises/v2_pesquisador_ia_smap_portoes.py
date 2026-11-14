"""SUPERADO por v2_pesquisador_ia_smap_escore.py: a AUC agregada das probabilidades LOYO deste script sofre o artefato
de intercepto do deixa-um-ano-de-fora com 10 anos (AUC < 0,5 para a chuva sozinha). Nao usar os numeros de AUC agregada daqui.
"""
"""Rodada 2, pesquisador de IA. TESTE CENTRAL: o SMAP L4 (zona da raiz) acrescenta habilidade alem da chuva IMERG
acumulada para prever a QUEBRA CANONICA municipal de milho e feijao (IBGE PAM) nos portoes 31/jan, 19/mar e 30/abr?

Protocolo (fixado antes de ver resultado):
- Anos de teste: 2016-2025 (quadras com SMAP L4 e PAM; o SMAP comeca em 31/03/2015; o PAM vai ate 2025). 10 anos.
- Alvo: quebra canonica (producao/area plantada < 50% da mediana dos OUTROS anos do municipio, 1998-2025, area >= 50 ha).
- Linha de base R: chuva IMERG desde 1/jan ate o portao em % do normal (normal = mediana dos outros anos 1998-2025),
  s_chuva = -min(pct, 3) (mesma receita de arquiteto_final_curvas_quixada.py).
- SMAP: media dos 7 dias que terminam no portao, por municipio (media das celulas EASE2 9 km cujo centro cai no
  municipio; municipio sem centro -> celula mais proxima do ponto representativo).
    * S_p  = sm_rootzone_pctl (percentil climatologico do proprio produto, 0-100);
    * S_a  = anomalia de sm_rootzone (m3/m3) = valor - mediana dos OUTROS anos 2016-2026 na mesma janela.
- Modelos: logistica (StandardScaler + LogisticRegression C=100), ajustada deixando o ANO inteiro de fora (LOYO).
  R | S_p | R+S_p | R+S_a. Comparacao pareada R+S contra R com as MESMAS amostras e as MESMAS dobras.
- Metricas: AUC agregada das predicoes fora da dobra; AUC dentro do ano (media ponderada npos*nneg nos anos com >=3
  quebras e >=3 nao quebras); Brier e log-loss; IC90 por bootstrap de ANOS (2000 reamostragens) para os deltas.
- Bloco B (decomposicao, nao selecao): o ganho do SMAP e so chuva antecedente? Linha de base R2 = R + chuva IMERG
  desde 1/out do ano anterior (% do normal). Compara R2+S_p contra R2.
- Bloco C: redundancia SMAP x chuva (Spearman agregado e dentro do ano).
- Bloco D: Quixada 2016-2025 (o motor nao explicava 2023-2025).
So le arquivos; grava apenas o painel em saidas/v2_pesquisador_ia_smap_painel.parquet.
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
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
S = A + "saidas/"
rng = np.random.default_rng(2026)
ANOS_T = list(range(2016, 2026))
ANOS_SMAP = list(range(2016, 2027))
PORT = {"31/jan": (1, 31), "19/mar": (3, 19), "30/abr": (4, 30)}

# ---------------- quebra canonica (receita de arquiteto_final_curvas_quixada.py)
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

# ---------------- chuva IMERG por municipio (cache canonico)
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
anos_c = list(range(1998, 2026))


def pct_normal(ini, m, d):
    """ini(a) -> data inicial do acumulado; normal = mediana dos outros anos 1998-2025."""
    ac = pd.DataFrame({a: chuva.loc[ini(a):f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_c}).T
    out = ac.copy() * np.nan
    for a in anos_c:
        out.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return out


# ---------------- SMAP L4 por municipio
with Cronometro("SMAP L4 recorte CE"):
    ds = xr.open_dataset("E:/campeonato-nasa/dados/smap/smap_l4_diario_ne.nc")
    sub = ds[["sm_rootzone", "sm_rootzone_pctl"]].sel(lat=slice(-2.4, -8.1), lon=slice(-41.7, -37.0),
                                                      time=slice("2015-10-01", "2026-05-05")).load()
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
    iy, ix = int(np.abs(lat - rp.y).argmin()), int(np.abs(lon - rp.x).argmin())
    cel[c] = [(iy, ix)]
print(f"municipios: {len(mun)}; com >=1 centro de celula SMAP: {len(mun) - len(sem)}; via celula mais proxima: {len(sem)}; "
      f"celulas por municipio (mediana): {np.median([len(v) for v in cel.values()]):.0f}")

tt = pd.DatetimeIndex(sub.time.values)
rz = sub.sm_rootzone.values
pc = sub.sm_rootzone_pctl.values
cods = sorted(cel)
RZ = pd.DataFrame({c: np.nanmean(np.stack([rz[:, iy, ix] for iy, ix in cel[c]], 1), 1) for c in cods}, index=tt)
PC = pd.DataFrame({c: np.nanmean(np.stack([pc[:, iy, ix] for iy, ix in cel[c]], 1), 1) for c in cods}, index=tt)
print(f"dias SMAP no recorte: {len(tt)} ({tt.min().date()} a {tt.max().date()}); fracao NaN rootzone mun-dia: {RZ.isna().mean().mean():.3%}")


def janela(df, a, m, d, n=7):
    fim = pd.Timestamp(a, m, d)
    return df.loc[fim - pd.Timedelta(days=n - 1):fim].mean()


# ---------------- painel
linhas = []
for gn, (m, d) in PORT.items():
    P1 = pct_normal(lambda a: f"{a}-01-01", m, d)
    P2 = pct_normal(lambda a: f"{a - 1}-10-01", m, d)
    rzw = pd.DataFrame({a: janela(RZ, a, m, d) for a in ANOS_SMAP}).T
    pcw = pd.DataFrame({a: janela(PC, a, m, d) for a in ANOS_SMAP}).T
    anom = rzw.copy() * np.nan
    for a in ANOS_SMAP:
        anom.loc[a] = rzw.loc[a] - rzw.drop(index=a).median()
    for a in ANOS_T:
        for c in cods:
            linhas.append({"portao": gn, "ano": a, "cod": c, "pct": P1.loc[a, c] if c in P1 else np.nan,
                           "pct_out": P2.loc[a, c] if c in P2 else np.nan, "smap_pctl": pcw.loc[a, c],
                           "smap_anom": anom.loc[a, c], "smap_rz": rzw.loc[a, c]})
X = pd.DataFrame(linhas)
X["s_chuva"] = -X.pct.clip(upper=3)
X["s_chuva_out"] = -X.pct_out.clip(upper=3)
X.to_parquet(S + "v2_pesquisador_ia_smap_painel.parquet", index=False)


def loyo(df, cols):
    p = pd.Series(np.nan, index=df.index)
    for a in ANOS_T:
        tr, te = df.ano != a, df.ano == a
        if te.sum() == 0:
            continue
        mdl = make_pipeline(StandardScaler(), LogisticRegression(C=100, max_iter=2000))
        mdl.fit(df.loc[tr, cols], df.loc[tr, "quebra"])
        p[te] = mdl.predict_proba(df.loc[te, cols])[:, 1]
    return p


def clim(df):
    p = pd.Series(np.nan, index=df.index)
    for a in ANOS_T:
        p[df.ano == a] = df.loc[df.ano != a, "quebra"].mean()
    return p


def auc_dentro(y, p, ano):
    num = den = 0.0
    for a in np.unique(ano):
        k = ano == a
        npos = y[k].sum(); nneg = k.sum() - npos
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(y[k], p[k]); den += w
    return num / den if den else np.nan


def metricas(y, p, ano):
    return {"auc": roc_auc_score(y, p), "dentro": auc_dentro(y, p, ano), "brier": brier_score_loss(y, p),
            "logloss": log_loss(y, np.clip(p, 1e-4, 1 - 1e-4))}


def boot_delta(df, pa, pb, nb=2000):
    """IC90 por bootstrap de ANOS do delta (b - a) com as mesmas amostras."""
    y, ano = df.quebra.values, df.ano.values
    idx = {a: np.where(ano == a)[0] for a in ANOS_T}
    out = {k: [] for k in ["auc", "dentro", "brier", "logloss"]}
    for _ in range(nb):
        yrs = rng.choice(ANOS_T, len(ANOS_T))
        ii = np.concatenate([idx[a] for a in yrs])
        # anos repetidos viram "anos" distintos para a AUC dentro do ano
        ano_b = np.concatenate([np.full(len(idx[a]), j) for j, a in enumerate(yrs)])
        yy = y[ii]
        if yy.min() == yy.max():
            continue
        ma, mb = metricas(yy, pa[ii], ano_b), metricas(yy, pb[ii], ano_b)
        for k in out:
            out[k].append(mb[k] - ma[k])
    return {k: (np.nanpercentile(v, 5), np.nanpercentile(v, 95), np.nanmean(np.array(v) > 0)) for k, v in out.items()}


res = []
print("\n" + "=" * 20, "A. TESTE CENTRAL: R (chuva desde 1/jan) x R + SMAP, LOYO 2016-2025", "=" * 20)
for cult, Y in CULT.items():
    for gn in PORT:
        df = X[X.portao == gn].merge(Y, on=["cod", "ano"]).dropna(
            subset=["s_chuva", "s_chuva_out", "smap_pctl", "smap_anom"]).reset_index(drop=True)
        y, ano = df.quebra.values, df.ano.values
        qa = df.groupby("ano").quebra.agg(["sum", "count"])
        pr = {"clim": clim(df).values, "R": loyo(df, ["s_chuva"]).values, "S_p": loyo(df, ["smap_pctl"]).values,
              "R+S_p": loyo(df, ["s_chuva", "smap_pctl"]).values, "R+S_a": loyo(df, ["s_chuva", "smap_anom"]).values,
              "R2": loyo(df, ["s_chuva", "s_chuva_out"]).values,
              "R2+S_p": loyo(df, ["s_chuva", "s_chuva_out", "smap_pctl"]).values}
        M = {k: metricas(y, v, ano) for k, v in pr.items()}
        print(f"\n--- {cult} | portao {gn} | n = {len(df)} mun-anos | {df.cod.nunique()} municipios | taxa de quebra {y.mean():.3f}")
        print("    quebras por ano: " + ", ".join(f"{a}:{int(r['sum'])}/{int(r['count'])}" for a, r in qa.iterrows()))
        for k, mm in M.items():
            bss = 1 - mm["brier"] / M["clim"]["brier"]
            print(f"    {k:7s} AUC {mm['auc']:.3f} | dentro do ano {mm['dentro']:.3f} | Brier {mm['brier']:.4f} (BSS {bss:+.3f}) | log-loss {mm['logloss']:.4f}")
        for a_, b_ in [("R", "R+S_p"), ("R", "R+S_a"), ("R2", "R2+S_p")]:
            bd = boot_delta(df, pr[a_], pr[b_])
            d = {k: M[b_][k] - M[a_][k] for k in bd}
            # por ano: em quantos anos o log-loss melhora
            ll_a = np.array([log_loss(y[ano == a], np.clip(pr[a_][ano == a], 1e-4, 1 - 1e-4), labels=[0, 1]) for a in ANOS_T])
            ll_b = np.array([log_loss(y[ano == a], np.clip(pr[b_][ano == a], 1e-4, 1 - 1e-4), labels=[0, 1]) for a in ANOS_T])
            melhora = int((ll_b < ll_a).sum())
            print(f"    {b_} - {a_}: dAUC {d['auc']:+.3f} IC90 [{bd['auc'][0]:+.3f},{bd['auc'][1]:+.3f}] P(>0)={bd['auc'][2]:.2f} | "
                  f"d dentro {d['dentro']:+.3f} [{bd['dentro'][0]:+.3f},{bd['dentro'][1]:+.3f}] | "
                  f"dBrier {d['brier']:+.4f} [{bd['brier'][0]:+.4f},{bd['brier'][1]:+.4f}] | "
                  f"dLogLoss {d['logloss']:+.4f} [{bd['logloss'][0]:+.4f},{bd['logloss'][1]:+.4f}] | anos com log-loss melhor: {melhora}/10")
            res.append({"cultura": cult, "portao": gn, "comparacao": f"{b_} vs {a_}", "n": len(df),
                        "auc_base": M[a_]["auc"], "auc_novo": M[b_]["auc"], "dAUC": d["auc"], "dAUC_lo": bd["auc"][0],
                        "dAUC_hi": bd["auc"][1], "d_dentro": d["dentro"], "d_dentro_lo": bd["dentro"][0],
                        "d_dentro_hi": bd["dentro"][1], "dBrier": d["brier"], "dBrier_lo": bd["brier"][0],
                        "dBrier_hi": bd["brier"][1], "anos_melhor_logloss": melhora})
R = pd.DataFrame(res)
R.to_csv(S + "v2_pesquisador_ia_smap_portoes.csv", index=False)
print("\nResumo (deltas pareados; IC90 por bootstrap de anos):")
print(R[["cultura", "portao", "comparacao", "auc_base", "auc_novo", "dAUC", "dAUC_lo", "dAUC_hi", "d_dentro",
         "d_dentro_lo", "d_dentro_hi", "dBrier", "anos_melhor_logloss"]].round(3).to_string(index=False))
print("Nota: 12 comparacoes primarias (2 culturas x 3 portoes x 2 variantes SMAP) sem correcao; ~1 'vitoria' espuria a 90% e esperada.")

print("\n" + "=" * 20, "C. Redundancia SMAP x chuva (Spearman; 184 municipios x 10 anos)", "=" * 20)
for gn in PORT:
    df = X[(X.portao == gn)].dropna(subset=["pct", "smap_pctl", "smap_anom"])
    r_all = spearmanr(df.pct, df.smap_pctl).statistic
    r_out = spearmanr(df.pct_out, df.smap_pctl).statistic
    rw = np.mean([spearmanr(g.pct, g.smap_pctl).statistic for _, g in df.groupby("ano")])
    rw2 = np.mean([spearmanr(g.pct_out, g.smap_pctl).statistic for _, g in df.groupby("ano")])
    ra = np.mean([spearmanr(g.pct, g.smap_anom).statistic for _, g in df.groupby("ano")])
    ym = df.groupby("ano")[["pct", "pct_out", "smap_pctl"]].mean()
    ry = spearmanr(ym.pct, ym.smap_pctl).statistic
    ry2 = spearmanr(ym.pct_out, ym.smap_pctl).statistic
    print(f"  {gn}: rho(chuva 1/jan, S_p) agregado {r_all:+.2f}, dentro do ano {rw:+.2f}; rho(chuva 1/out, S_p) agregado {r_out:+.2f}, "
          f"dentro do ano {rw2:+.2f}; rho(chuva 1/jan, S_a) dentro do ano {ra:+.2f}; ENTRE anos (media estadual, n=10): "
          f"1/jan {ry:+.2f}, 1/out {ry2:+.2f}")
    print("     media estadual por ano: " + ", ".join(f"{a}: chuva {r.pct:.0%} / S_p {r.smap_pctl:.0f}" for a, r in ym.iterrows()))

print("\n" + "=" * 20, "D. Quixada (2311306), 2016-2025: razao do PAM, chuva % normal e percentil SMAP nos portoes", "=" * 20)
qx = "2311306"
T = pd.DataFrame(index=ANOS_T)
for cult, Y in CULT.items():
    T[cult] = Y[Y.cod == qx].set_index("ano").razao
for gn in PORT:
    q = X[(X.portao == gn) & (X.cod == qx)].set_index("ano")
    T[f"chuva_{gn}"] = q.pct
    T[f"Sp_{gn}"] = q.smap_pctl
    T[f"Sa_{gn}"] = q.smap_anom
print(T.round(2).to_string())
print("  percentil do SMAP no proprio municipio-ano em relacao aos 184 municipios (rank dentro do ano, 30/abr):")
q = X[X.portao == "30/abr"].copy()
q["rk"] = q.groupby("ano").smap_pctl.rank(pct=True)
q["rk_chuva"] = q.groupby("ano").pct.rank(pct=True)
print(q[q.cod == qx].set_index("ano")[["rk", "rk_chuva"]].round(2).T.to_string())
