"""Arquiteto-chefe, rodada 2: arbitragem das divergencias entre especialistas sobre o SMAP L4 nos portoes.

Divergencias a resolver (todas vindas dos .saida.txt da rodada 2):
 1. AUC do SMAP em 19/mar: 0,68 (pesquisador de IA, SR, designer, hidrologo: media dos 7 dias ate o portao)
    contra 0,59 (estrategista, cetico, agronomo: valor do DIA do portao). Em 30/abr todos dao ~0,77.
 2. Quebras de 2016 pegas pelo SMAP < 20 em 30/abr: 90 de 127 (dia) contra 64 de 127 (media de 7 dias).
 3. Memoria da zona da raiz: tau 13 dias (agronomo, anomalia fev-jun) contra 46-58 dias (hidrologo, ano inteiro).
 4. Limiar do alerta SMAP: < 20 (secao 05, hidrologo, estrategista, cetico, designer) contra < 25 (agronomo).
Nada e escolhido aqui olhando o resultado: as duas leituras (dia e 7 dias) e os dois limiares sao reportados lado a lado.
A regra para o deck (fixada ANTES de rodar): quando duas leituras igualmente razoaveis divergem, o slide usa a MENOS
favoravel ao SMAP e o recibo mostra a outra.
Tambem: E. regra canonica de chuva por era (1998-2015 x 2016-2025) e regra "duas luzes" (chuva < 75% OU SMAP < 20).
So le arquivos ja salvos pelos especialistas (series municipais diarias do SMAP do hidrologo, cache de chuva, PAM).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
rng = np.random.default_rng(11)
QXD = "2311306"

# ---------------- quebra canonica do milho (receita do arquiteto, copiada)
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
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
base = p.dropna(subset=["razao"])[["cod", "ano", "quebra", "razao"]]

chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
ANOS = list(range(1998, 2026))


def pct_normal(m, d):
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in ANOS}).T
    out = ac.copy() * np.nan
    for a in ANOS:
        out.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return out.stack().rename("pct").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})


PC = pd.read_parquet(A + "saidas/v2_hidrologo_smap_pctl_mun_diario.parquet")
RZ = pd.read_parquet(A + "saidas/v2_hidrologo_smap_rz_mun_diario.parquet")
PC.columns = PC.columns.astype(str)
RZ.columns = RZ.columns.astype(str)
print(f"SMAP municipal (hidrologo, deduplicado): {PC.shape[0]} dias x {PC.shape[1]} municipios, "
      f"{PC.index.min().date()} a {PC.index.max().date()}; datas repetidas no indice: {int(PC.index.duplicated().sum())}")


def auc_boot(df, cols, nb=1000):
    yrs = df.ano.unique()
    g = {a: df[df.ano == a] for a in yrs}
    pt = {c: roc_auc_score(df.quebra, df[c]) for c in cols}
    bs = []
    for _ in range(nb):
        bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            bs.append([roc_auc_score(bb.quebra, bb[c]) for c in cols])
    return pt, np.array(bs)


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            num += npos * nneg * roc_auc_score(g.quebra, g[col])
            den += npos * nneg
    return num / den


def placar(df, al, nome):
    q = df.quebra.astype(bool)
    pa, ps = q[al].mean(), q[~al].mean()
    rec = (al & q).sum() / q.sum()
    por = {a: f"{int((al & q)[df.ano == a].sum())}/{int(q[df.ano == a].sum())} (alertas {int(al[df.ano == a].sum())})"
           for a in (2016, 2021, 2025)}
    print(f"    {nome:<34} acende {al.mean():5.1%} | P(q|alerta) {pa:.2f} (n {int(al.sum())}) | P(q|sem) {ps:.2f} | "
          f"recall {rec:5.1%} | 2016 {por[2016]} | 2021 {por[2021]} | 2025 {por[2025]}")


print("\n" + "=" * 18, "A-D. SMAP pctl no DIA x MEDIA DE 7 DIAS, limiar 20 x 25 (milho, 2016-2025, pareado)", "=" * 18)
for gn, (m, d) in {"28/fev": (2, 28), "19/mar": (3, 19), "30/abr": (4, 30)}.items():
    pl = pct_normal(m, d)
    linhas = []
    for a in range(2016, 2026):
        t = pd.Timestamp(a, m, d)
        dia = PC.loc[t]
        sete = PC.loc[t - pd.Timedelta(days=6):t].mean()
        linhas.append(pd.DataFrame({"ano": a, "cod": PC.columns, "p_dia": dia.values, "p_7d": sete.values}))
    sm = pd.concat(linhas)
    df = base[base.ano.between(2016, 2025)].merge(pl, on=["cod", "ano"]).merge(sm, on=["cod", "ano"]).dropna()
    df["s_chuva"], df["s_dia"], df["s_7d"] = -df.pct.clip(upper=3), -df.p_dia, -df.p_7d
    pt, bs = auc_boot(df, ["s_chuva", "s_dia", "s_7d"])
    ic = lambda j: f"[{np.percentile(bs[:, j], 5):.2f}; {np.percentile(bs[:, j], 95):.2f}]"
    print(f"\n  [{gn}] n = {len(df)} municipio-anos, {df.ano.nunique()} anos, {int(df.quebra.sum())} quebras")
    print(f"    AUC total: chuva {pt['s_chuva']:.3f} {ic(0)} | SMAP dia {pt['s_dia']:.3f} {ic(1)} | SMAP 7 dias {pt['s_7d']:.3f} {ic(2)}")
    for j, c in [(1, "dia"), (2, "7 dias")]:
        dd = bs[:, j] - bs[:, 0]
        print(f"    dif SMAP {c} - chuva: {pt[['s_chuva','s_dia','s_7d'][j]] - pt['s_chuva']:+.3f} "
              f"(IC90 por ano {np.percentile(dd, 5):+.3f} a {np.percentile(dd, 95):+.3f})")
    print(f"    AUC dentro do ano: chuva {auc_dentro(df, 's_chuva'):.3f} | SMAP dia {auc_dentro(df, 's_dia'):.3f} | "
          f"SMAP 7 dias {auc_dentro(df, 's_7d'):.3f}")
    s16 = df[df.ano != 2016]
    print(f"    sem 2016: chuva {roc_auc_score(s16.quebra, s16.s_chuva):.3f} | SMAP dia {roc_auc_score(s16.quebra, s16.s_dia):.3f}"
          f" | SMAP 7 dias {roc_auc_score(s16.quebra, s16.s_7d):.3f}")
    print(f"    r(SMAP dia, SMAP 7 dias) entre municipio-anos = {df.p_dia.corr(df.p_7d):.3f}")
    placar(df, df.pct < 0.75, "chuva < 75% (canonica)")
    for c in ("dia", "7d"):
        for lim in (20, 25):
            placar(df, df[f"p_{c}"] < lim, f"SMAP {c} < {lim}")
    for c in ("dia", "7d"):
        placar(df, (df.pct < 0.75) | (df[f"p_{c}"] < 20), f"duas luzes: chuva<75% OU SMAP {c}<20")
    qx = df[df.cod == QXD].set_index("ano")[["razao", "quebra", "pct", "p_dia", "p_7d"]].round(2)
    print(f"    Quixada ({gn}):\n" + qx.to_string().replace("\n", "\n      "))

print("\n" + "=" * 18, "E. Regra canonica de chuva por era (milho, quebra canonica)", "=" * 18)
for gn, (m, d) in {"19/mar": (3, 19), "30/abr": (4, 30)}.items():
    df = base.merge(pct_normal(m, d), on=["cod", "ano"]).dropna()
    df["s"] = -df.pct.clip(upper=3)
    for rot, sel in [("1998-2025", df.ano >= 1998), ("1998-2015", df.ano <= 2015), ("2016-2025", df.ano >= 2016)]:
        x = df[sel]
        al, q = x.pct < 0.75, x.quebra.astype(bool)
        print(f"  [{gn} {rot}] AUC {roc_auc_score(x.quebra, x.s):.3f} | dentro do ano {auc_dentro(x, 's'):.3f} | "
              f"P(q|alerta) {q[al].mean():.2f} (n {int(al.sum())}) | P(q|sem) {q[~al].mean():.2f} | "
              f"recall {(al & q).sum() / q.sum():.1%} | taxa-base {q.mean():.3f}")

print("\n" + "=" * 18, "F. Memoria da zona da raiz (e-folding da anomalia; duas definicoes)", "=" * 18)
rz = RZ.loc["2015-04-01":"2025-12-31"]


def anom(s):
    doy = np.clip(np.asarray(s.index.dayofyear), 1, 365)
    clim = s.groupby(doy).mean().reindex(range(1, 366)).interpolate()
    c3 = pd.concat([clim, clim, clim]).rolling(31, center=True).mean().iloc[365:730]
    c3.index = range(1, 366)
    return s - c3.reindex(doy).values


def efold(a, meses=None, maxlag=150):
    v = a.values
    mo = a.index.month.values
    yr = a.index.year.values
    for L in range(1, maxlag):
        x, y = v[:-L], v[L:]
        ok = np.isfinite(x) & np.isfinite(y)
        if meses is not None:
            ok &= np.isin(mo[:-L], meses) & np.isin(mo[L:], meses) & (yr[:-L] == yr[L:])
        if ok.sum() < 30:
            return np.nan
        if np.corrcoef(x[ok], y[ok])[0, 1] < 1 / np.e:
            return L
    return np.nan


ce = anom(rz.mean(axis=1))
print(f"  media do CE: e-folding ano inteiro = {efold(ce)} dias | so pares dentro de fev-jun = {efold(ce, [2, 3, 4, 5, 6])} dias"
      f" | so pares dentro de ago-dez = {efold(ce, [8, 9, 10, 11, 12])} dias")
tm_all, tm_fj = [], []
for c in rz.columns:
    a = anom(rz[c])
    tm_all.append(efold(a))
    tm_fj.append(efold(a, [2, 3, 4, 5, 6]))
print(f"  por municipio (mediana): ano inteiro = {np.nanmedian(tm_all):.0f} dias | fev-jun = {np.nanmedian(tm_fj):.0f} dias")
print("  Nota: aqui a autocorrelacao e AGRUPADA entre anos (inclui a anomalia da estacao inteira). O agronomo (tau 13 d)\n"
      "  correlaciona DENTRO de cada ano, o que tira a anomalia media do ano e mede so a memoria intrassazonal.\n"
      "  As duas medidas estao certas e respondem perguntas diferentes; nenhuma vai ao pitch como 'o solo esquece em X dias'.")
