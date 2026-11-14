"""Cetico cientifico, banca adversaria rodada 2: o "9 contra 64" do SMAP e uma comparacao justa?

Pergunta: o ganho do SMAP L4 (pctl zona da raiz < 20, media de 7 dias ate 30/abr) e ganho do SATELITE/MODELO ou ganho
de trocar a LEITURA da chuva (soma desde 1/jan, que guarda janeiro) por qualquer leitura de chuva recente do proprio IMERG?
Leituras de chuva IMERG comparadas (TODAS reportadas; nenhuma escolhida pelo resultado; todas com corte fixo 75% do normal,
normal = mediana dos OUTROS anos 1998-2025):
  W1 1/jan->portao (canonica do QUADRA) | W2 1/fev->portao (declarada pelo economista em v2_economista_janela_alerta.py)
  API tau=13 d desde 1/jan (declarada pelo agronomo em v2_agronomo_smap_contraprova.py, tau medido no SMAP sem rotulo)
  R30 ultimos 30 dias (leitura simples, declarada aqui) | R15 ultimos 15 dias (do cetico, v2_cetico_smap_l3_obs_vs_modelo.py)
Tambem: (b) mesma taxa de alerta que o SMAP (limiar da chuva escolhido SEM rotulo, so pela taxa de acendimento);
(c) placar por ano (n = 10 anos, unidade independente); (d) tirando um ano por vez; (e) sensibilidade a data do portao
(30/abr e pre-declarado; as outras datas sao so sensibilidade); (f) era 1998-2015 para as leituras de chuva.
Rotulo: quebra canonica do milho (producao / area plantada < 50% da mediana dos outros anos; area >= 50 ha).
So le arquivos ja salvos (cache de chuva municipal do estrategista, SMAP municipal deduplicado do hidrologo, PAM).
Saida: v2_cetico_r2b_smap_contra_imerg_justo.saida.txt
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
SAIDA = A + "v2_cetico_r2b_smap_contra_imerg_justo.saida.txt"
LIN = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LIN.append(s)


rng = np.random.default_rng(20261114)
ANOS = list(range(1998, 2026))
TAU = 13

# ---------------- quebra canonica do milho (mesma receita de v2_arquiteto_arbitragem_smap.py)
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
base = p.dropna(subset=["razao"])[["cod", "ano", "quebra"]]

chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
PC = pd.read_parquet(A + "saidas/v2_hidrologo_smap_pctl_mun_diario.parquet")
PC.columns = PC.columns.astype(str)
assert not PC.index.duplicated().any()


def leitura(m, d, tipo):
    """valor bruto por ano x municipio de uma leitura de chuva no portao (m, d)."""
    res = {}
    for a in ANOS:
        g = pd.Timestamp(a, m, d)
        if tipo == "W1":
            x = chuva.loc[f"{a}-01-01":g].sum()
        elif tipo == "W2":
            x = chuva.loc[f"{a}-02-01":g].sum()
        elif tipo == "R30":
            x = chuva.loc[g - pd.Timedelta(days=29):g].sum()
        elif tipo == "R15":
            x = chuva.loc[g - pd.Timedelta(days=14):g].sum()
        elif tipo == "API":
            sl = chuva.loc[f"{a}-01-01":g]
            w = np.exp(-(len(sl) - 1 - np.arange(len(sl))) / TAU)[:, None]
            x = pd.Series((sl.values * w).sum(0), index=sl.columns)
        res[a] = x
    ac = pd.DataFrame(res).T
    o = ac * np.nan
    for a in ANOS:
        o.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    s = o.stack().rename(tipo).reset_index()
    s.columns = ["ano", "cod", tipo]
    return s


def smap7(m, d, anos=range(2016, 2026)):
    li = []
    for a in anos:
        t = pd.Timestamp(a, m, d)
        li.append(pd.DataFrame({"ano": a, "cod": PC.columns, "S7": PC.loc[t - pd.Timedelta(days=6):t].mean().values}))
    return pd.concat(li)


CH = ["W1", "W2", "API", "R30", "R15"]


def painel(m, d, com_smap=True):
    df = base.copy()
    for t in CH:
        df = df.merge(leitura(m, d, t), on=["ano", "cod"], how="inner")
    if com_smap:
        df = df[df.ano.between(2016, 2025)].merge(smap7(m, d), on=["ano", "cod"]).dropna()
        df["sS7"] = -df.S7
    for t in CH:
        df["s" + t] = -df[t].clip(upper=3)
    return df.dropna()


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            num += npos * nneg * roc_auc_score(g.quebra, g[col])
            den += npos * nneg
    return num / den


def boot_dif(df, c1, c0, nb=2000):
    yrs = df.ano.unique()
    g = {a: df[df.ano == a] for a in yrs}
    bs = []
    for _ in range(nb):
        bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            bs.append(roc_auc_score(bb.quebra, bb[c1]) - roc_auc_score(bb.quebra, bb[c0]))
    return np.percentile(bs, [5, 95])


def placar(df, al, nome):
    q = df.quebra.astype(bool)
    por = {a: f"{int((al & q)[df.ano == a].sum())}/{int(q[df.ano == a].sum())} (alertas {int(al[df.ano == a].sum())})"
           for a in (2016, 2021, 2025)}
    out(f"    {nome:<40} acende {al.mean():5.1%} | P(q|alerta) {q[al].mean():.2f} | P(q|sem) {q[~al].mean():.2f} | "
        f"recall {(al & q).sum() / q.sum():5.1%} | 2016 {por[2016]} | 2021 {por[2021]} | 2025 {por[2025]}")


# ======================================================================================
out("=" * 20, "A. 30/abr, milho, 2016-2025: SMAP 7 d contra CINCO leituras de chuva IMERG (mesmas linhas)", "=" * 20)
df = painel(4, 30)
out(f"  n = {len(df)} municipio-anos, {df.ano.nunique()} anos, {int(df.quebra.sum())} quebras "
    f"(2016: {int(df[df.ano == 2016].quebra.sum())})")
out(f"  AUC SMAP 7 d = {roc_auc_score(df.quebra, df.sS7):.3f} | dentro do ano {auc_dentro(df, 'sS7'):.3f}")
for t in CH:
    a = roc_auc_score(df.quebra, df["s" + t])
    lo, hi = boot_dif(df, "sS7", "s" + t)
    out(f"  chuva {t:<4} AUC {a:.3f} | dentro do ano {auc_dentro(df, 's' + t):.3f} | SMAP - {t}: "
        f"{roc_auc_score(df.quebra, df.sS7) - a:+.3f} (IC90 por ano {lo:+.3f} a {hi:+.3f}) | "
        f"rho Spearman(S7, {t}) = {stats.spearmanr(df.S7, df[t])[0]:+.2f}")

out("\n  Regras com limiar FIXO (chuva < 75% do normal; SMAP < 20):")
placar(df, df.S7 < 20, "SMAP 7 d < 20 (canonica da v2)")
for t in CH:
    placar(df, df[t] < 0.75, f"chuva {t} < 75%")

taxa = (df.S7 < 20).mean()
out(f"\n  B. Mesma taxa de alerta que o SMAP ({taxa:.1%} dos municipio-anos de 2016-2025; limiar escolhido sem rotulo):")
for t in CH:
    lim = df[t].quantile(taxa)
    placar(df, df[t] <= lim, f"chuva {t} <= {lim:.2f} do normal")

# ======================================================================================
out("\n" + "=" * 20, "C. Placar por ANO (n = 10; a unidade independente)", "=" * 20)
fa = df.groupby("ano").agg(frac_quebra=("quebra", "mean"), S7_med=("S7", "median"),
                           **{f"{t}_med": (t, "median") for t in CH})
fa["al_S7"] = df.assign(x=df.S7 < 20).groupby("ano").x.mean()
for t in CH:
    fa[f"al_{t}"] = df.assign(x=df[t] < 0.75).groupby("ano").x.mean()
out(fa.round(2).to_string())
for c in ["S7_med"] + [f"{t}_med" for t in CH]:
    r, pv = stats.spearmanr(-fa[c], fa.frac_quebra)
    out(f"  Spearman entre anos (-{c}, fracao em quebra) = {r:+.2f} (p {pv:.3f}, n = 10)")
for c in ["al_S7"] + [f"al_{t}" for t in CH]:
    r, pv = stats.spearmanr(fa[c], fa.frac_quebra)
    out(f"  Spearman entre anos ({c} = fracao com alerta, fracao em quebra) = {r:+.2f} (p {pv:.3f})")

# ======================================================================================
out("\n" + "=" * 20, "D. Tirando um ano por vez: dif de AUC SMAP 7 d - chuva", "=" * 20)
for t in ["W1", "W2", "API"]:
    li = []
    for a in range(2016, 2026):
        x = df[df.ano != a]
        li.append(f"{a}: {roc_auc_score(x.quebra, x.sS7) - roc_auc_score(x.quebra, x['s' + t]):+.3f}")
    out(f"  SMAP - {t}: " + " | ".join(li))

# ======================================================================================
out("\n" + "=" * 20, "E. Sensibilidade a data do portao (30/abr e o pre-declarado)", "=" * 20)
for (m, d) in [(4, 15), (4, 22), (4, 30), (5, 7), (5, 15)]:
    x = painel(m, d)
    q = x.quebra.astype(bool)
    s16 = x.ano == 2016
    s21 = x.ano == 2021
    tx = []
    for nome, al in [("SMAP7<20", x.S7 < 20), ("W1<75%", x.W1 < 0.75), ("W2<75%", x.W2 < 0.75), ("API<75%", x.API < 0.75)]:
        tx.append(f"{nome}: AUC {roc_auc_score(x.quebra, {'SMAP7<20': x.sS7, 'W1<75%': x.sW1, 'W2<75%': x.sW2, 'API<75%': x.sAPI}[nome]):.2f}, "
                  f"2016 {int((al & q & s16).sum())}/{int((q & s16).sum())} (al {int((al & s16).sum())}), 2021 al {int((al & s21).sum())}")
    out(f"  {d:02d}/{m:02d}: " + " || ".join(tx))

# ======================================================================================
out("\n" + "=" * 20, "F. Era 1998-2015 (o SMAP nao existia): as leituras alternativas da chuva tambem funcionam?", "=" * 20)
for (m, d, gn) in [(3, 19, "19/mar"), (4, 30, "30/abr")]:
    x = painel(m, d, com_smap=False)
    for rot, sel in [("1998-2015", x.ano <= 2015), ("2016-2025", x.ano >= 2016), ("1998-2025", x.ano >= 1998)]:
        y = x[sel]
        q = y.quebra.astype(bool)
        partes = []
        for t in CH:
            al = y[t] < 0.75
            partes.append(f"{t} AUC {roc_auc_score(y.quebra, y['s' + t]):.2f} P(q|al) {q[al].mean():.2f} rec {(al & q).sum() / q.sum():.0%}")
        out(f"  [{gn} {rot}] " + " | ".join(partes))

# ======================================================================================
out("\n" + "=" * 20, "G. 19/mar, 2016-2025, mesmas comparacoes (o deck usa 0,59 do dia; aqui a media de 7 d)", "=" * 20)
df19 = painel(3, 19)
out(f"  n = {len(df19)}; AUC SMAP 7 d = {roc_auc_score(df19.quebra, df19.sS7):.3f}")
for t in CH:
    a = roc_auc_score(df19.quebra, df19["s" + t])
    lo, hi = boot_dif(df19, "sS7", "s" + t)
    out(f"  chuva {t:<4} AUC {a:.3f} | SMAP - {t}: {roc_auc_score(df19.quebra, df19.sS7) - a:+.3f} (IC90 por ano {lo:+.3f} a {hi:+.3f})")
placar(df19, df19.S7 < 20, "SMAP 7 d < 20")
for t in CH:
    placar(df19, df19[t] < 0.75, f"chuva {t} < 75%")

# ======================================================================================
out("\n" + "=" * 20, "H. A regra 'duas luzes' da v2 (W1 OU SMAP < 20) contra W2 sozinha e W2 combinada (2016-2025)", "=" * 20)
for gn, x in [("19/mar", df19), ("30/abr", df)]:
    out(f"  [{gn}]")
    placar(x, (x.W1 < 0.75) | (x.S7 < 20), "duas luzes v2: W1<75% OU SMAP7<20")
    placar(x, x.W2 < 0.75, "so IMERG W2 < 75%")
    placar(x, (x.W2 < 0.75) | (x.S7 < 20), "W2<75% OU SMAP7<20")
    placar(x, (x.W2 < 0.75) & (x.S7 < 20), "W2<75% E SMAP7<20")

with open(SAIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(LIN) + "\n")
