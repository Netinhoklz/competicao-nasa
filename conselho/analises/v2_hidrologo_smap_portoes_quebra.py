"""Hidrólogo, rodada 2, análise A2: o SMAP L4 nos portões da QUADRA discrimina a quebra municipal melhor que a chuva?

Pergunta: no mesmo conjunto de município-anos (pareado), o percentil da zona da raiz do SMAP L4 no dia do portão
ordena a quebra canônica do milho (IBGE PAM, razão < 0,5 contra a mediana dos OUTROS anos, área >= 50 ha) melhor que:
  (a) a regra canônica da QUADRA: chuva IMERG acumulada desde 1/jan em % do normal (mediana dos outros anos);
  (b) o balde M1 em modo contínuo (mesma física da A1: TAW 100 mm, Kc 1,0, CN 75), fração de água no dia do portão.
Métricas: AUC total com IC90 por bootstrap de ANOS; AUC dentro do ano (ponderada, anos com >= 3 quebras e >= 3 não);
rho entre anos (média do ano contra a fração em quebra). Logística deixando o ano de fora (chuva; chuva + SMAP).
Anos: 2016-2025 em todos os portões (o SMAP começa em 31/03/2015); 30/abr também com 2015 como sensibilidade.
Mais o replay de Quixadá (2311306) 2015-2025: o SMAP explica 2023-2025?
Entrada do SMAP municipal: saidas/v2_hidrologo_smap_pctl_mun_diario.parquet (gerado pela A1).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 230)
AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
SAI = AN / "saidas"
rng = np.random.default_rng(0)
QX = "2311306"

# ------------------------------------------------------------------ quebra canônica (mesma receita do arquiteto)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")


def serie(prefixo):
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        return pd.Series([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref
    p["quebra"] = (p.razao < 0.5).astype(int)
    p["cod"] = p.cod_local.astype(str).str[:7]
    return p.dropna(subset=["razao"])


mi = serie("Milho (em gr")
fe = serie("Feij")

# ------------------------------------------------------------------ preditores
chuva = pd.read_parquet(AN / "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
pct = pd.read_parquet(SAI / "v2_hidrologo_smap_pctl_mun_diario.parquet")
rzm = pd.read_parquet(SAI / "v2_hidrologo_smap_rz_mun_diario.parquet")
anos_ch = list(range(1998, 2026))

# balde M1 contínuo (idêntico à A1)
mun = municipios_ce_gdf()
cod_col = next(c for c in mun.columns if "cod" in c.lower() or c.lower() in ("id", "codarea"))
mun["cod"] = mun[cod_col].astype(str).str[:7]
et0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"]
valida = np.isfinite(et0.values).mean(0) > 0.9
ELO, ELA = np.meshgrid(et0.lon.values, et0.lat.values)
iv = np.flatnonzero(valida.ravel())
E0 = et0.values.reshape(et0.sizes["time"], -1)
idx_e = [iv[np.argmin((ELO.ravel()[iv] - g.centroid.x) ** 2 + (ELA.ravel()[iv] - g.centroid.y) ** 2)] for g in mun.geometry]
E = pd.DataFrame(E0[:, idx_e], index=pd.DatetimeIndex(et0.time.values), columns=mun.cod.tolist())
E = E.fillna(E.groupby(E.index.dayofyear).transform("mean"))
T = chuva.index.intersection(E.index)
T = T[T >= "1998-06-01"]  # desde 1998 para ter climatologia do balde por município (percentil contra os outros anos)


def balde(P, Ev, taw=100.0, p=0.55, kc=1.0, cn=75.0):
    s = 25400.0 / cn - 254.0
    raw = p * taw
    Dr = np.full(P.shape[1], taw)
    out = np.empty_like(P, dtype=float)
    for j in range(P.shape[0]):
        pj = P[j]
        q = np.where(pj > 0.2 * s, (pj - 0.2 * s) ** 2 / (pj + 0.8 * s), 0.0)
        ks = np.where(Dr > raw, np.clip((taw - Dr) / ((1 - p) * taw), 0, 1), 1.0)
        Dr = np.clip(Dr - (pj - q) + ks * kc * Ev[j], 0, taw)
        out[j] = (taw - Dr) / taw
    return out


B = pd.DataFrame(balde(chuva.loc[T, mun.cod].fillna(0).values, E.loc[T, mun.cod].values), index=T, columns=mun.cod.tolist())

PORT = {"31/jan": (1, 31), "28/fev": (2, 28), "19/mar": (3, 19), "30/abr": (4, 30)}


def tabela_portao(m, d, anos):
    rows = []
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_ch}).T
    bq = pd.DataFrame({a: B.loc[pd.Timestamp(a, m, d)] for a in range(1999, 2026)}).T  # balde no dia do portão, ano x mun
    for a in anos:
        t = pd.Timestamp(a, m, d)
        if t not in pct.index:
            continue
        norm = ac.drop(index=a).median()
        outros = bq.drop(index=a, errors="ignore")
        bpct = (outros < bq.loc[a]).mean() * 100  # percentil do balde contra os OUTROS anos (1999-2025), por município
        bclim = outros.mean()  # só geografia: o balde médio daquele município naquela data, sem o ano
        # SMAP: média dos 7 dias até o portão (inclusive), pré-registrado para tirar o ruído de um dia
        sp = pct.loc[t - pd.Timedelta(days=6):t].mean()
        sr = rzm.loc[t - pd.Timedelta(days=6):t].mean()
        for cod in pct.columns:
            rows.append({"cod": cod, "ano": a, "imerg_pct": ac.loc[a, cod] / norm[cod], "smap_pctl": sp[cod],
                         "smap_rz_abs": sr[cod], "balde": bq.loc[a, cod], "balde_pctl": bpct[cod], "balde_clim": bclim[cod]})
    return pd.DataFrame(rows)


def auc_ic(df, col, nboot=500):
    auc = roc_auc_score(df.quebra, -df[col])
    yrs = df.ano.unique()
    g = {a: df[df.ano == a] for a in yrs}
    bs = []
    for _ in range(nboot):
        bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            bs.append(roc_auc_score(bb.quebra, -bb[col]))
    return auc, np.percentile(bs, 5), np.percentile(bs, 95)


def auc_dentro(df, col):
    num = den = 0.0
    por_ano = {}
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            v = roc_auc_score(g.quebra, -g[col])
            por_ano[a] = round(v, 2)
            num += w * v; den += w
    return num / den, por_ano


def boot_dif_dentro(df, c1, c2, nboot=500):
    """IC90 da diferença de AUC dentro do ano (c1 − c2), reamostrando anos."""
    yrs = [a for a, g in df.groupby("ano") if g.quebra.sum() >= 3 and (1 - g.quebra).sum() >= 3]
    vals = {a: (roc_auc_score(g.quebra, -g[c1]), roc_auc_score(g.quebra, -g[c2]), g.quebra.sum() * (1 - g.quebra).sum())
            for a, g in df.groupby("ano") if a in yrs}
    bs = []
    for _ in range(nboot):
        s = rng.choice(yrs, len(yrs))
        w = np.array([vals[a][2] for a in s])
        bs.append(np.sum(w * np.array([vals[a][0] - vals[a][1] for a in s])) / w.sum())
    return np.percentile(bs, 5), np.percentile(bs, 95), len(yrs)


def logistica_loyo(df, cols):
    out = pd.Series(np.nan, index=df.index)
    for a in df.ano.unique():
        tr, te = df.ano != a, df.ano == a
        X = df[cols]
        mu, sd = X[tr].mean(), X[tr].std()
        lr = LogisticRegression().fit((X[tr] - mu) / sd, df.loc[tr, "quebra"])
        out[te] = lr.predict_proba((X[te] - mu) / sd)[:, 1]
    return out


for cultura, base in [("milho", mi), ("feijão", fe)]:
    print("=" * 30, f"Quebra canônica do {cultura}", "=" * 30)
    for nome, (m, d) in PORT.items():
        for anos, rot in [(range(2016, 2026), "2016-2025")] + ([(range(2015, 2026), "2015-2025")] if nome == "30/abr" else []):
            X = tabela_portao(m, d, anos)
            df = base[["cod", "ano", "quebra", "razao"]].merge(X, on=["cod", "ano"]).dropna()
            df["imerg_pct"] = df.imerg_pct.clip(upper=3)
            lin = [f"  {nome} [{rot}] n={len(df)} mun-anos, {df.ano.nunique()} anos, taxa de quebra {df.quebra.mean():.2f}"]
            res = {}
            for c, rc in [("imerg_pct", "chuva IMERG % normal"), ("smap_pctl", "SMAP L4 percentil"), ("smap_rz_abs", "SMAP L4 m3/m3 absoluto"),
                          ("balde", "balde M1 absoluto"), ("balde_pctl", "balde M1 percentil"), ("balde_clim", "só geografia (balde clim.)")]:
                a, lo, hi = auc_ic(df, c)
                dw, pa = auc_dentro(df, c)
                ym = df.groupby("ano").agg(x=(c, "mean"), q=("quebra", "mean"))
                rho = stats.spearmanr(ym.x, ym.q)[0]
                res[c] = (a, dw)
                lin.append(f"     {rc:22s} AUC {a:.3f} [{lo:.2f},{hi:.2f}] | dentro do ano {dw:.3f} | rho entre anos {rho:+.2f}")
                if c == "smap_pctl" and cultura == "milho":
                    lin.append(f"        dentro do ano por ano (SMAP): {pa}")
                if c == "imerg_pct" and cultura == "milho":
                    lin.append(f"        dentro do ano por ano (chuva): {pa}")
            lo_, hi_, ny = boot_dif_dentro(df, "smap_pctl", "imerg_pct")
            lin.append(f"     diferença dentro do ano SMAP − chuva = {res['smap_pctl'][1] - res['imerg_pct'][1]:+.3f}, IC90 por ano [{lo_:+.3f},{hi_:+.3f}] ({ny} anos)")
            for c1, c2 in [("smap_pctl", "balde_pctl"), ("balde", "balde_clim"), ("smap_rz_abs", "smap_pctl"), ("balde_pctl", "imerg_pct")]:
                lo_, hi_, ny = boot_dif_dentro(df, c1, c2)
                lin.append(f"     diferença dentro do ano {c1} − {c2} = {res[c1][1] - res[c2][1]:+.3f}, IC90 por ano [{lo_:+.3f},{hi_:+.3f}]")
            if cultura == "milho" and nome in ("19/mar", "30/abr"):
                for regra, mk_ in [("SMAP<20", df.smap_pctl < 20), ("chuva<75%", df.imerg_pct < 0.75), ("balde pctl<20", df.balde_pctl < 20)]:
                    g = df[mk_].groupby("ano").quebra.agg(["size", "sum"])
                    lin.append(f"     {regra} por ano (alertas, acertos): " + ", ".join(f"{a}:{int(r['size'])}/{int(r['sum'])}" for a, r in g.iterrows())
                               + f" | P(quebra|alerta) {df.quebra[mk_].mean():.2f} (n={mk_.sum()}), recall {df.quebra[mk_].sum() / df.quebra.sum():.0%}")
                lin.append(f"     quebras por ano: {df.groupby('ano').quebra.sum().to_dict()}")
            df["s_ch"] = logistica_loyo(df, ["imerg_pct"])
            df["s_chsm"] = logistica_loyo(df, ["imerg_pct", "smap_pctl"])
            df["s_chba"] = logistica_loyo(df, ["imerg_pct", "balde"])
            lin.append(f"     logística ano fora: chuva {roc_auc_score(df.quebra, df.s_ch):.3f} | chuva+SMAP {roc_auc_score(df.quebra, df.s_chsm):.3f}"
                       f" | chuva+balde {roc_auc_score(df.quebra, df.s_chba):.3f}")
            # regra de alerta SMAP pré-registrada: percentil < 20 (seca agrícola usual) contra a regra da chuva < 75%
            for regra, mask in [("chuva < 75%", df.imerg_pct < 0.75), ("SMAP pctl < 20", df.smap_pctl < 20),
                                ("as duas", (df.imerg_pct < 0.75) & (df.smap_pctl < 20))]:
                if mask.sum():
                    lin.append(f"     alerta {regra:15s}: acende {mask.mean():.0%} | P(quebra|alerta) {df.quebra[mask].mean():.2f} (n={mask.sum()})"
                               f" | P(quebra|sem) {df.quebra[~mask].mean():.2f} | recall {df.quebra[mask].sum() / df.quebra.sum():.0%}")
            print("\n".join(lin))

# ------------------------------------------------------------------ o ISNA canônico do M1 (agrônomo) contra a própria geografia
print("\n" + "=" * 30, "ISNA canônico do M1 (fim de safra) × só geografia (média do ISNA do município nos OUTROS anos)", "=" * 30)
isna = pd.read_parquet(SAI / "agronomo_isna_mun_ano.parquet")
isna["cod"] = isna.cod.astype(str)
for col in ["isna_flor_milho", "isna_ciclo_milho"]:
    x = isna[["cod", "ano", col]].copy()
    tot = x.groupby("cod")[col].transform("sum"); n = x.groupby("cod")[col].transform("count")
    x["clim"] = (tot - x[col]) / (n - 1)
    x["anom"] = x[col] - x["clim"]
    for anos, rot in [((1999, 2025), "1999-2025"), ((2016, 2025), "2016-2025")]:
        df = mi[["cod", "ano", "quebra"]].merge(x, on=["cod", "ano"]).dropna()
        df = df[df.ano.between(*anos)]
        r = {c: auc_dentro(df, c)[0] for c in [col, "clim", "anom"]}
        lo_, hi_, ny = boot_dif_dentro(df, col, "clim")
        print(f"  {col} [{rot}] n={len(df)}: dentro do ano ISNA {r[col]:.3f} | só geografia {r['clim']:.3f} | anomalia do ano {r['anom']:.3f}"
              f" | ISNA − geografia {r[col] - r['clim']:+.3f} IC90 [{lo_:+.3f},{hi_:+.3f}] ({ny} anos)")

# ------------------------------------------------------------------ Quixadá
print("\n" + "=" * 30, "Replay de Quixadá 2015-2025 (milho canônico)", "=" * 30)
qrows = []
for a in range(2015, 2026):
    r = {"ano": a}
    for nome, (m, d) in [("19/mar", (3, 19)), ("30/abr", (4, 30))]:
        t = pd.Timestamp(a, m, d)
        if t in pct.index:
            r[f"SMAP pctl {nome}"] = round(pct.loc[t - pd.Timedelta(days=6):t, QX].mean(), 0)
        ac = chuva.loc[f"{a}-01-01":t, QX].sum()
        r[f"chuva % {nome}"] = round(ac / np.median([chuva.loc[f"{b}-01-01":pd.Timestamp(b, m, d), QX].sum() for b in anos_ch if b != a]), 2)
        r[f"balde {nome}"] = round(B.loc[t, QX], 2)
    # mínimo do percentil SMAP em fev-mai (a planta sente o pior momento)
    r["SMAP pctl 31/mai"] = round(pct.loc[pd.Timestamp(a, 5, 25):pd.Timestamp(a, 5, 31), QX].mean(), 0)
    r["SMAP pctl mín fev-mai"] = round(pct.loc[f"{a}-02-01":f"{a}-05-31", QX].rolling(7).mean().min(), 0)
    r["SMAP pctl médio mar-abr"] = round(pct.loc[f"{a}-03-01":f"{a}-04-30", QX].mean(), 0)
    r["chuva fev-mai (mm)"] = round(chuva.loc[f"{a}-02-01":f"{a}-05-31", QX].sum(), 0)
    qm = mi[(mi.cod == QX) & (mi.ano == a)]
    r["razão milho"] = round(float(qm.razao.iloc[0]), 2) if len(qm) else np.nan
    qf = fe[(fe.cod == QX) & (fe.ano == a)]
    r["razão feijão"] = round(float(qf.razao.iloc[0]), 2) if len(qf) else np.nan
    qrows.append(r)
Q = pd.DataFrame(qrows).set_index("ano")
print(Q.to_string())
q = Q.dropna(subset=["razão milho"])
for c in ["SMAP pctl 30/abr", "SMAP pctl mín fev-mai", "SMAP pctl médio mar-abr", "chuva % 30/abr", "balde 30/abr", "chuva fev-mai (mm)"]:
    j = q[[c, "razão milho"]].dropna()
    print(f"  rho({c}, razão milho) em Quixadá = {stats.spearmanr(j[c], j['razão milho'])[0]:+.2f} (n={len(j)})")
print("  chuva mensal de Quixadá (mm), jan-jun, 2019-2025:")
cm = chuva[QX]["2019":"2025"].resample("MS").sum()
cm = cm[cm.index.month <= 6]
print(cm.groupby([cm.index.year, cm.index.month]).sum().unstack().round(0).to_string())
# vizinhança: os municípios ao redor também quebraram em 2023-2025? (separa relato local de clima)
viz = mun.set_index("cod").geometry
gq = viz[QX]
viz_cods = [c for c, g in viz.items() if c != QX and g.distance(gq) < 0.3]
vq = mi[mi.cod.isin(viz_cods) & mi.ano.between(2016, 2025)].groupby("ano").quebra.mean()
print(f"  fração dos {len(viz_cods)} vizinhos (< 0,3° do limite) em quebra do milho: {vq.round(2).to_dict()}")
print(f"  fração do Ceará em quebra do milho: {mi[mi.ano.between(2016, 2025)].groupby('ano').quebra.mean().round(2).to_dict()}")
