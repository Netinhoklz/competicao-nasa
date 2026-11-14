"""Arquiteto-chefe, versao final: numeros canonicos que a banca pediu para refazer antes do deck.

A. Curva de habilidade CANONICA por portao (quebra canonica do milho; chuva IMERG acumulada desde 1/jan em % do normal
   do municipio, normal = mediana dos OUTROS anos), com e sem o oceano (ONI ja publicado na data), AUC total,
   AUC dentro do ano e IC90 por bootstrap de anos. Regra unica de alerta: acumulado < 75% do normal.
B. Curva de POSSIBILIDADE: fracao dos 184 municipios em que cada cultura ainda cabe na janela do ZARC sintetico.
C. Replay de Quixada ano a ano (definicao canonica; carteira 1/3; % do normal nos portoes; ISNA do balde).
D. ET0 x chuva por mes (POWER e ERA5, CE, 1991-2020).
E. Pontos globais sem mes de quebra termica: so pontos terrestres.
So le arquivos; nao escreve nada.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
S = A + "saidas/"
rng = np.random.default_rng(0)

# ---------------- quebra canonica (mesma receita do arquiteto / cetico_r3)
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
    return p.dropna(subset=["razao"])


mi = serie("Milho (em gr")
fe = serie("Feij")
ma = serie("Mandioca")

ind = pd.read_parquet(D + "indices_clima_mensal.parquet")
oni = ind[ind.variavel == "ONI"].set_index("data")["valor"]


def oni_em(ano, mes):
    return float(oni.get(pd.Timestamp(ano, mes, 1), np.nan))


chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
anos = list(range(1998, 2026))
# portao: (mes, dia, ONI ja publicado: (desloc_ano, mes central do trimestre))
PORT = {"15/nov (ano-1)": None, "31/jan": (1, 31, (-1, 11)), "28/fev": (2, 28, (-1, 12)), "19/mar": (3, 19, (0, 1)),
        "31/mar": (3, 31, (0, 1)), "30/abr": (4, 30, (0, 2))}


def pct_normal(m, d):
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos}).T  # ano x mun
    out = ac.copy() * np.nan
    for a in anos:
        out.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return out


def auc_ic(df, col, nboot=500):
    auc = roc_auc_score(df.quebra, df[col])
    yrs = df.ano.unique()
    g = {a: df[df.ano == a] for a in yrs}
    bs = []
    for _ in range(nboot):
        bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            bs.append(roc_auc_score(bb.quebra, bb[col]))
    return auc, np.percentile(bs, 5), np.percentile(bs, 95)


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, g[col]); den += w
    return num / den


print("=" * 20, "A. Curva de habilidade canonica (milho, quebra municipal; n por portao abaixo)", "=" * 20)
base = mi[["cod", "ano", "quebra"]]
linhas = []
for nome, spec in PORT.items():
    if spec is None:
        df = base.copy()
        df["oni"] = df.ano.map(lambda a: oni_em(a - 1, 9))  # ASO, publicado ~5/nov
        df = df.dropna()
        a, lo, hi = auc_ic(df, "oni")
        print(f"  {nome:15s} so oceano (ONI ASO): AUC={a:.3f} IC90 [{lo:.2f},{hi:.2f}]  dentro do ano = 0,50 por construcao  n={len(df)}")
        linhas.append({"portao": nome, "chuva": np.nan, "chuva_oceano": a, "lo": lo, "hi": hi, "dentro": 0.5})
        continue
    m, d, (da, mo) = spec
    P = pct_normal(m, d)
    pl = P.stack().rename("pct").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})
    df = base.merge(pl, on=["cod", "ano"])
    df["oni"] = df.ano.map(lambda a: oni_em(a + da, mo))
    df["s_chuva"] = -df.pct.clip(upper=3)
    z = lambda s: (s - s.mean()) / s.std()
    df["s_comb"] = z(df.oni) + z(df.s_chuva)
    # logistica deixando o ano de fora (2 atributos)
    df["s_loyo"] = np.nan
    for a in anos:
        tr, te = df.ano != a, df.ano == a
        if te.sum() == 0:
            continue
        lr = LogisticRegression().fit(df.loc[tr, ["oni", "s_chuva"]], df.loc[tr, "quebra"])
        df.loc[te, "s_loyo"] = lr.predict_proba(df.loc[te, ["oni", "s_chuva"]])[:, 1]
    a1, l1, h1 = auc_ic(df, "s_chuva")
    a2, l2, h2 = auc_ic(df, "s_comb")
    a3 = roc_auc_score(df.quebra, df.s_loyo)
    dw = auc_dentro(df, "s_chuva")
    al = df.pct < 0.75
    q = df.quebra.astype(bool)
    pqa, pqn = q[al].mean(), q[~al].mean()
    print(f"  {nome:15s} chuva: AUC={a1:.3f} [{l1:.2f},{h1:.2f}] | chuva+oceano (soma z): {a2:.3f} [{l2:.2f},{h2:.2f}] | "
          f"logistica LOYO: {a3:.3f} | dentro do ano (chuva): {dw:.3f} | n={len(df)}")
    print(f"  {'':15s} ALERTA <75%: {al.mean():.0%} dos mun-anos acendem; recall {q[al].sum() / q.sum():.0%}; "
          f"precisao {pqa:.0%}; P(quebra|alerta)={pqa:.2f} (n={al.sum()}) vs P(quebra|sem alerta)={pqn:.2f} (n={(~al).sum()}); razao {pqa / pqn:.1f}x")
    for ano in [1998, 2012, 2016, 2024]:
        g = df[df.ano == ano]
        qa = g.quebra.astype(bool)
        aa = g.pct < 0.75
        print(f"      {ano}: quebras {qa.sum():3d} | alertas {aa.sum():3d} | acertos {(qa & aa).sum():3d} | "
              f"recall {((qa & aa).sum() / max(qa.sum(), 1)):.0%}")
    linhas.append({"portao": nome, "chuva": a1, "chuva_oceano": a2, "lo": l2, "hi": h2, "dentro": dw})
print("\nResumo da curva (para o grafico das 3 curvas):")
print(pd.DataFrame(linhas).round(3).to_string(index=False))

# ---------------- B. possibilidade
print("\n" + "=" * 20, "B. Curva de possibilidade (ZARC sintetico, P(ISNA flor >= 0,5) >= 0,7)", "=" * 20)
Z = pd.read_parquet(S + "agronomo_zarc_sintetico_prob.parquet")
DEC = {"01/jan": 1, "11/jan": 11, "21/jan": 21, "01/fev": 32, "11/fev": 42, "21/fev": 52, "01/mar": 60,
       "11/mar": 70, "21/mar": 80, "01/abr": 91, "11/abr": 101, "21/abr": 111}
GATES = {"31/jan": 31, "28/fev": 59, "19/mar": 78, "31/mar": 90, "30/abr": 120}
for cult in ["milho", "sorgo", "caupi"]:
    res = []
    for gn, gd in GATES.items():
        # ainda cabe se algum decendio cujo fim (inicio+9) >= dia do portao tem P >= 0,7
        cols = [f"{cult}|{dn}" for dn, dd in DEC.items() if dd + 9 >= gd]
        ok = (Z[cols] >= 0.7).any(axis=1).mean() if cols else 0.0
        res.append(f"{gn}: {ok:.0%}")
    print(f"  {cult}: " + " | ".join(res))
qx = "2311306"
print("  Quixada, P por decendio:")
print(Z.loc[qx].unstack() if False else Z.loc[[qx]].T.rename(columns={qx: "P"}).T.to_string())

# ---------------- C. Quixada
print("\n" + "=" * 20, "C. Replay de Quixada (2311306), definicao canonica", "=" * 20)
T = pd.DataFrame(index=anos)
for nome, s in [("milho", mi), ("feijao", fe), ("mandioca", ma)]:
    T[nome] = s[s.cod == qx].set_index("ano").razao
T["carteira_1_3"] = T[["milho", "feijao", "mandioca"]].mean(axis=1, skipna=False)
for g, (m, d) in {"19/mar": (3, 19), "31/mar": (3, 31), "30/abr": (4, 30)}.items():
    T[f"pct_{g}"] = pct_normal(m, d)[qx]
T["oni_ndj"] = [oni_em(a - 1, 12) for a in anos]
isna = pd.read_parquet(S + "agronomo_isna_mun_ano.parquet")
isna["cod"] = isna.cod.astype(str)
iq = isna[isna.cod == qx].set_index("ano")
T["isna_flor_milho"] = iq.isna_flor_milho
T["isna_flor_caupi"] = iq.isna_flor_caupi
print(T.round(2).to_string())
print(f"  anos de quebra do milho (razao<0,5): {list(T.index[T.milho < 0.5])}")
print(f"  anos com as 3 culturas: {T.carteira_1_3.notna().sum()}")
cauda = T.milho.nsmallest(3)
print(f"  3 piores anos do milho: {cauda.round(2).to_dict()}")

# ---------------- D. ET0 x chuva por mes
print("\n" + "=" * 20, "D. ET0 x chuva por mes, CE, 1991-2020", "=" * 20)
pw = pd.read_parquet(D + "power_ce_mensal.parquet")
pw = pw[(pw.data.dt.year >= 1991) & (pw.data.dt.year <= 2020)]
dias = lambda s: s.index.days_in_month
pv = pw.pivot_table(index="data", columns="variavel", values="valor")
mm = lambda col: pv[col] * pv.index.days_in_month
P_pw = mm("PRECTOTCORR").groupby(pv.index.month).mean()
E_pw = mm("ET0").groupby(pv.index.month).mean()
e5 = pd.read_parquet(D + "era5_ce_mensal.parquet")
e5 = e5[(e5.data.dt.year >= 1991) & (e5.data.dt.year <= 2020)].pivot_table(index="data", columns="variavel", values="valor")
P_e5 = e5.tp.groupby(e5.index.month).mean()
E_e5 = e5.et0.groupby(e5.index.month).mean()
tab = pd.DataFrame({"P_power": P_pw, "ET0_power": E_pw, "P_era5": P_e5, "ET0_era5": E_e5}).round(0)
print(tab.to_string())
print(f"  anual: P POWER {P_pw.sum():.0f}, ET0 POWER {E_pw.sum():.0f}; P ERA5 {P_e5.sum():.0f}, ET0 ERA5 {E_e5.sum():.0f}; "
      f"razao ET0 ERA5/POWER {E_e5.sum() / E_pw.sum():.3f}")
print(f"  meses com ET0 > chuva: POWER {(E_pw > P_pw).sum()} de 12; ERA5 {(E_e5 > P_e5).sum()} de 12")

# ---------------- E. pontos globais
print("\n" + "=" * 20, "E. Pontos globais sem mes de quebra termica (POWER 2020)", "=" * 20)
g = pd.read_csv(A + "ecologo_grausdia_global_2020.csv")
trop = g[g.lat.abs() <= 23.44]
terra = trop[~trop.ponto.str.startswith("Oceano")]
print(f"  tropicais: {len(trop)}; com 0 meses de quebra: {(trop.meses_quebra == 0).sum()}")
print(f"  tropicais TERRESTRES: {len(terra)}; com 0 meses: {(terra.meses_quebra == 0).sum()} "
      f"({(terra.meses_quebra == 0).mean():.0%}); excecoes: {terra[terra.meses_quebra > 0].ponto.tolist()}")
print(f"  Iowa: {g[g.ponto == 'Iowa'].meses_quebra.iloc[0]} meses de quebra")
