"""Hidrólogo, rodada 2, análise A3: o SMAP L4 pode CALIBRAR o balde M1? Teste fora da amostra no tempo.

Desenho pré-registrado (uma família, uma métrica de ajuste, um teste):
  - Grade: TAW (água disponível na zona da raiz) em {50, 100, 150, 200, 300} mm x Kc efetivo em {0,4; 0,6; 0,8; 1,0}.
    O padrão da A1/A2 (TAW 100, Kc 1,0) está na grade. Física do M1: CN 75, p 0,55.
  - Ajuste por município: maximizar o r de Pearson diário entre o balde (fração de água) e o SMAP L4 sm_rootzone
    do município. Alvo do ajuste = SMAP, nunca a safra: não há vazamento de rótulo.
  - (i) Dentro da era SMAP: ajuste deixando o ANO de fora (2016-2025), r no ano deixado de fora: padrão x calibrado.
  - (ii) Memória (e-folding da anomalia) e data do vale: padrão x calibrado x SMAP.
  - (iii) FORA DA AMOSTRA NO TEMPO: parâmetros ajustados com 2015-2026 e aplicados em 1998-2014 (o SMAP nunca viu esses
    anos). Nos portões 19/mar e 30/abr: AUC dentro do ano, rho entre anos e alerta "percentil < 20" contra a quebra
    canônica do milho, pareado com o balde padrão e com a chuva IMERG em % do normal (regra canônica).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 230)
AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
SAI = AN / "saidas"
rng = np.random.default_rng(0)

mun = municipios_ce_gdf()
cod_col = next(c for c in mun.columns if "cod" in c.lower() or c.lower() in ("id", "codarea"))
mun["cod"] = mun[cod_col].astype(str).str[:7]
cods = mun.cod.tolist()
chuva = pd.read_parquet(AN / "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
et0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"]
valida = np.isfinite(et0.values).mean(0) > 0.9
ELO, ELA = np.meshgrid(et0.lon.values, et0.lat.values)
iv = np.flatnonzero(valida.ravel())
E0 = et0.values.reshape(et0.sizes["time"], -1)
idx_e = [iv[np.argmin((ELO.ravel()[iv] - g.centroid.x) ** 2 + (ELA.ravel()[iv] - g.centroid.y) ** 2)] for g in mun.geometry]
E = pd.DataFrame(E0[:, idx_e], index=pd.DatetimeIndex(et0.time.values), columns=cods)
E = E.fillna(E.groupby(E.index.dayofyear).transform("mean"))
T = chuva.index.intersection(E.index)
T = T[T >= "1998-01-01"]  # começa seco em 1/jan/1998 (fim da estação seca)
P = chuva.loc[T, cods].fillna(0).values.astype(np.float32)
EE = E.loc[T, cods].values.astype(np.float32)

TAWS = [50.0, 100.0, 150.0, 200.0, 300.0]
KCS = [0.4, 0.6, 0.8, 1.0]
COMBOS = [(t, k) for t in TAWS for k in KCS]
PADRAO = COMBOS.index((100.0, 1.0))


def balde_grade(P, E, p=0.55, cn=75.0):
    nC, n = len(COMBOS), P.shape[1]
    taw = np.repeat(np.array([c[0] for c in COMBOS], np.float32), n)
    kc = np.repeat(np.array([c[1] for c in COMBOS], np.float32), n)
    s = 25400.0 / cn - 254.0
    raw = p * taw
    Dr = taw.copy()
    out = np.empty((P.shape[0], nC * n), np.float32)
    for j in range(P.shape[0]):
        pj = np.tile(P[j], nC)
        q = np.where(pj > 0.2 * s, (pj - 0.2 * s) ** 2 / (pj + 0.8 * s), 0.0)
        ks = np.where(Dr > raw, np.clip((taw - Dr) / ((1 - p) * taw), 0, 1), 1.0)
        Dr = np.clip(Dr - (pj - q) + ks * kc * np.tile(E[j], nC), 0, taw)
        out[j] = (taw - Dr) / taw
    return out.reshape(P.shape[0], nC, n)


with Cronometro("balde em 20 combinações x 184 municípios, 1998-2026"):
    BG = balde_grade(P, EE)  # (tempo, combo, mun)
print("dias:", len(T), T.min().date(), "->", T.max().date())

smap = pd.read_parquet(SAI / "v2_hidrologo_smap_rz_mun_diario.parquet")[cods]
dias = smap.index.intersection(T)
iT = T.get_indexer(dias)
S = smap.loc[dias].values  # (dias, mun)
Bs = BG[iT]  # (dias, combo, mun)
anos_s = dias.year.values


def corr_por_coluna(x, y):
    xm = x - np.nanmean(x, 0); ym = y - np.nanmean(y, 0)
    return np.nansum(xm * ym, 0) / np.sqrt(np.nansum(xm ** 2, 0) * np.nansum(ym ** 2, 0))


# ------------------------------------------------------------------ (i) ajuste deixando o ano de fora, dentro da era SMAP
print("\n" + "=" * 25, "(i) r com o SMAP no ANO DEIXADO DE FORA (por município, média)", "=" * 25)
rs = []
escolha_loyo = {}
for y in range(2016, 2026):
    tr, te = anos_s != y, anos_s == y
    rtr = np.stack([corr_por_coluna(Bs[tr, c], S[tr]) for c in range(len(COMBOS))])  # combo x mun
    best = np.nanargmax(rtr, 0)
    escolha_loyo[y] = best
    rte = np.stack([corr_por_coluna(Bs[te, c], S[te]) for c in range(len(COMBOS))])
    r_cal = rte[best, np.arange(len(cods))]
    r_pad = rte[PADRAO]
    rs.append({"ano": y, "r padrão": np.nanmean(r_pad), "r calibrado": np.nanmean(r_cal),
               "mun. em que melhora": np.mean(r_cal > r_pad)})
R = pd.DataFrame(rs).set_index("ano")
print(R.round(3).to_string())
print(f"média dos 10 anos: padrão {R['r padrão'].mean():.3f} | calibrado {R['r calibrado'].mean():.3f} | anos em que melhora: {(R['r calibrado'] > R['r padrão']).sum()} de 10")

# ajuste com toda a era SMAP (para a descrição e para o teste fora da amostra em 1998-2014)
rall = np.stack([corr_por_coluna(Bs[:, c], S) for c in range(len(COMBOS))])
best_all = np.nanargmax(rall, 0)
esc = pd.DataFrame([COMBOS[b] for b in best_all], columns=["TAW", "Kc"], index=cods)
print("\nparâmetros escolhidos com 2015-2026 (184 municípios):")
print(esc.value_counts().head(8).to_string())
print(f"TAW mediana {esc.TAW.median():.0f} mm | Kc mediano {esc.Kc.median():.2f} | r médio padrão {np.nanmean(rall[PADRAO]):.3f} -> calibrado {np.nanmean(rall[best_all, np.arange(len(cods))]):.3f}")
estab = np.mean([np.mean(escolha_loyo[y] == best_all) for y in escolha_loyo])
print(f"estabilidade: fração de município-anos LOYO com a mesma escolha do ajuste completo = {estab:.2f}")

# séries calibradas (uma coluna por município)
Bcal = BG[:, best_all, np.arange(len(cods))]  # (tempo, mun)
Bpad = BG[:, PADRAO, :]

# ------------------------------------------------------------------ (ii) memória e vale
print("\n" + "=" * 25, "(ii) Memória e ciclo: média do Ceará", "=" * 25)


def anom(s, base=("2015-04-01", "2025-12-31")):
    b = s[base[0]:base[1]]
    clim = b.groupby(b.index.dayofyear).mean().reindex(range(1, 367)).interpolate(limit_direction="both")
    clim = pd.concat([clim.iloc[-31:], clim, clim.iloc[:31]]).rolling(31, center=True).mean().iloc[31:-31]
    clim.index = range(1, 367)
    return s - clim.reindex(s.index.dayofyear).values, clim


for nome, s in [("SMAP L4", smap.mean(1)), ("balde padrão", pd.Series(Bpad.mean(1), index=T)),
                ("balde calibrado", pd.Series(Bcal.mean(1), index=T))]:
    s = s["2015-03-31":"2026-09-14"]
    a, cl = anom(s)
    ac = [a.autocorr(k) for k in range(0, 400, 2)]
    k = next((2 * i for i, v in enumerate(ac) if v < np.exp(-1)), None)
    vale = int(cl.idxmin())
    print(f"  {nome:16s} e-folding {k} dias | vale climatológico em {(pd.Timestamp('2021-01-01') + pd.Timedelta(days=vale - 1)):%d/%m} | r com SMAP (CE, diário) "
          f"{s.corr(smap.mean(1).reindex(s.index)):.3f}")

# checagem de aquecimento: o balde começa vazio em 1/jan/1998. Nos outros anos, quanto de água resta em 1/jan?
# Se o calibrado (memória longa) guarda água na virada do ano, 1998 sai artificialmente seco nos portões.
for nome, Bx in [("padrão", Bpad), ("calibrado", Bcal)]:
    j1 = pd.Series([float(np.mean(Bx[T.get_loc(pd.Timestamp(a, 1, 1))])) for a in range(1999, 2027)], index=range(1999, 2027))
    print(f"  aquecimento [{nome}]: fração de água média do CE em 1/jan dos anos 1999-2026: mediana {j1.median():.3f}, máx {j1.max():.3f} ({j1.idxmax()})")

# ------------------------------------------------------------------ (iii) fora da amostra no tempo: 1998-2014
print("\n" + "=" * 25, "(iii) Fora da amostra no tempo: 1998-2014 (SMAP nunca viu), quebra canônica do milho", "=" * 25)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha
p["ref"] = p.groupby("cod_local").r.transform(lambda v: pd.Series([np.median(np.delete(v.values, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=v.index))
p = p.dropna(subset=["ref"])
p["quebra"] = (p.r / p.ref < 0.5).astype(int)
p["cod"] = p.cod_local.astype(str).str[:7]
mi = p[["cod", "ano", "quebra"]]
anos_all = list(range(1998, 2026))


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, -g[col]); den += w
    return num / den


def boot_dif(df, c1, c2, nboot=1000):
    yrs = [a for a, g in df.groupby("ano") if g.quebra.sum() >= 3 and (1 - g.quebra).sum() >= 3]
    v = {a: (roc_auc_score(g.quebra, -g[c1]) - roc_auc_score(g.quebra, -g[c2]), g.quebra.sum() * (1 - g.quebra).sum())
         for a, g in df.groupby("ano") if a in yrs}
    bs = []
    for _ in range(nboot):
        s = rng.choice(yrs, len(yrs))
        w = np.array([v[a][1] for a in s])
        bs.append(np.sum(w * np.array([v[a][0] for a in s])) / w.sum())
    return np.percentile(bs, 5), np.percentile(bs, 95), len(yrs)


def boot_auc_total(df, col, nboot=1000):
    yrs = df.ano.unique(); g = {a: df[df.ano == a] for a in yrs}
    bs = []
    for _ in range(nboot):
        bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            bs.append(roc_auc_score(bb.quebra, -bb[col]))
    return np.percentile(bs, 5), np.percentile(bs, 95)


for nome, (m, d) in {"19/mar": (3, 19), "30/abr": (4, 30)}.items():
    t_ano = {a: T.get_loc(pd.Timestamp(a, m, d)) for a in anos_all}
    vc = pd.DataFrame({a: Bcal[t_ano[a]] for a in anos_all}, index=cods).T  # ano x mun
    vp = pd.DataFrame({a: Bpad[t_ano[a]] for a in anos_all}, index=cods).T
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":pd.Timestamp(a, m, d), cods].sum() for a in anos_all}).T
    rows = []
    for a in range(1998, 2015):
        o = [b for b in anos_all if b != a]
        pc_c = (vc.loc[o] < vc.loc[a]).mean() * 100
        pc_p = (vp.loc[o] < vp.loc[a]).mean() * 100
        pr = ac.loc[a] / ac.loc[o].median()
        for c in cods:
            rows.append({"cod": c, "ano": a, "cal_pctl": pc_c[c], "pad_pctl": pc_p[c], "chuva_pct": min(pr[c], 3),
                         "cal_abs": vc.loc[a, c], "pad_abs": vp.loc[a, c]})
    df = mi.merge(pd.DataFrame(rows), on=["cod", "ano"]).dropna()
    print(f"--- portão {nome}: n={len(df)} município-anos, {df.ano.nunique()} anos, taxa de quebra {df.quebra.mean():.2f}")
    d2 = df[df.ano >= 1999]  # sensibilidade: sem 1998 (ano de aquecimento do balde)
    for regra, c, thr in [("chuva < 75%", "chuva_pct", 0.75), ("balde padrão pctl < 20", "pad_pctl", 20), ("balde calibrado pctl < 20", "cal_pctl", 20)]:
        mk2 = d2[c] < thr
        print(f"   [sem 1998] {regra:26s} P(quebra|alerta) {d2.quebra[mk2].mean():.2f} (n={mk2.sum()}) | recall {d2.quebra[mk2].sum() / d2.quebra.sum():.0%}")
    for c, rot in [("chuva_pct", "chuva IMERG % normal"), ("pad_pctl", "balde padrão, percentil"), ("cal_pctl", "balde calibrado SMAP, percentil")]:
        lo, hi = boot_auc_total(df, c)
        ym = df.groupby("ano").agg(x=(c, "mean"), q=("quebra", "mean"))
        print(f"   {rot:32s} AUC total {roc_auc_score(df.quebra, -df[c]):.3f} [{lo:.2f},{hi:.2f}] | dentro do ano {auc_dentro(df, c):.3f} | "
              f"rho entre anos {stats.spearmanr(ym.x, ym.q)[0]:+.2f}")
    for c1, c2 in [("cal_pctl", "pad_pctl"), ("cal_pctl", "chuva_pct"), ("pad_pctl", "chuva_pct")]:
        lo, hi, ny = boot_dif(df, c1, c2)
        print(f"   dentro do ano {c1} − {c2}: {auc_dentro(df, c1) - auc_dentro(df, c2):+.3f} IC90 [{lo:+.3f},{hi:+.3f}] ({ny} anos)")
    for regra, mk_ in [("chuva < 75%", df.chuva_pct < 0.75), ("balde padrão pctl < 20", df.pad_pctl < 20),
                       ("balde calibrado pctl < 20", df.cal_pctl < 20)]:
        g = df[mk_].groupby("ano").quebra.agg(["size", "sum"])
        tot_q = df.groupby("ano").quebra.sum()
        sec = ", ".join(f"{a}:{int(g.loc[a, 'sum']) if a in g.index else 0}/{int(tot_q[a])}" for a in (1998, 2010, 2012, 2013))
        print(f"   alerta {regra:26s} acende {mk_.mean():.0%} | P(quebra|alerta) {df.quebra[mk_].mean():.2f} (n={mk_.sum()}) | "
              f"P(quebra|sem) {df.quebra[~mk_].mean():.2f} | recall {df.quebra[mk_].sum() / df.quebra.sum():.0%} | acertos/quebras em {sec}")
