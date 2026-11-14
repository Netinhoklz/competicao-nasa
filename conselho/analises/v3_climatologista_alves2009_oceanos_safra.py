"""Climatologista (v3) - replicacao de Alves, Servain & Campos 2009 (Clim Res 38:225-236, doi 10.3354/cr00786)
com os nossos dados: IBGE PAM (Ceara, 1974-2025), ONI (NOAA CPC), TNA/TSA (NOAA PSL) e chuva NASA (POWER, IMERG).

O que o artigo diz (conferido no PDF local, artigos/2009_Alves_...pdf):
  - 1952-2000, milho e feijao do Ceara (dado IBGE compilado pelo IPECE).
  - r(chuva FMAM FUNCEME, producao/rendimento): milho +0,52/+0,38; feijao +0,46/+0,22 (secao 3.2).
  - categorias: Nino-3 NDJ +-0,5 C; dipolo (NTA-STA) FMA +-0,2 C (Tabela 1, 9 combinacoes).
  - modelo prognostico: rendimento sem tendencia ~ NI3(NDJ) + NTA, STA, DIP (DJ); calibra nos anos impares,
    valida nos pares: r = +0,36 (feijao) e +0,51 (milho) (secao 4.2, Fig. 9).
Diferencas inevitaveis: ONI (Nino-3.4, ERSSTv5) no lugar do Nino-3 (COADS); TNA/TSA da PSL no lugar das caixas NTA/STA
do artigo (coordenadas nao dadas no texto); PAM municipal somado (184 municipios) no lugar da serie do IPECE.

Blocos:
  A) r(chuva FMAM NASA, producao e rendimento) por era (1981-2000, 2001-2025)
  B) concordancia das categorias Pacifico/Atlantico com a Tabela 1 (1974-2000) e compostos 1974-2025
  C) modelo prognostico: protocolo do artigo (impar/par 1974-2000), fora do tempo (1974-2000 -> 2001-2025) e LOYO
  D) portao de janeiro: o Atlantico de dez-jan acrescenta algo ao ONI de ASO na fracao municipal de quebra (1998-2025)?
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import warnings

warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV

import numpy as np
import pandas as pd

rng = np.random.default_rng(0)

# ---------------- dados ----------------
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
ind.index = pd.DatetimeIndex(ind.index)
pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw = pw[pw.variavel.isin(["PRECTOTCORR", "IMERG_PRECTOT"])].pivot_table(index="data", columns="variavel", values="valor")
pw.index = pd.DatetimeIndex(pw.index)
# o derivado ja vem em mm/mes (soma dos dias; rotulo "mm/day/mes")


def estado(prefixo):
    p = pam[pam.produto.str.startswith(prefixo)].groupby("ano")[["producao_t", "area_plantada_ha", "area_colhida_ha"]].sum()
    p["rend_plant"] = p.producao_t * 1000 / p.area_plantada_ha.where(p.area_plantada_ha > 0)  # PAM so tem area plantada desde 1988
    p["rend_colh"] = p.producao_t * 1000 / p.area_colhida_ha
    return p


M, F = estado("Milho (em gr"), estado("Feij")


def m(serie, ano, meses):
    """media de meses (lista de (dano, mes)) relativos ao ano agricola"""
    v = [serie.get(pd.Timestamp(ano + da, mm, 1), np.nan) for da, mm in meses]
    return np.nanmean(v) if np.isfinite(v).all() else np.nan


anos = range(1974, 2026)
X = pd.DataFrame(index=list(anos))
X["ONI_NDJ"] = [ind.ONI.get(pd.Timestamp(a - 1, 12, 1), np.nan) for a in anos]  # ONI no mes central
X["ONI_ASO"] = [ind.ONI.get(pd.Timestamp(a - 1, 9, 1), np.nan) for a in anos]
for v in ["TNA", "TSA", "DIPOLO_TNA_menos_TSA"]:
    X[v[:3] + "_DJ"] = [m(ind[v], a, [(-1, 12), (0, 1)]) for a in anos]
X["DIP_FMA"] = [m(ind["DIPOLO_TNA_menos_TSA"], a, [(0, 2), (0, 3), (0, 4)]) for a in anos]
X["P_FMAM_POWER"] = [pw.PRECTOTCORR.loc[f"{a}-02":f"{a}-05"].sum(min_count=4) if a >= 1981 else np.nan for a in anos]
# IMERG: o IMERG_PRECTOT do derivado mensal do POWER so comeca em 2000; usa a media dos 184 municipios (IMERG V07 diario, 1998+)
_cm = pd.read_parquet(Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas/chuva_mun_diaria.parquet")).mean(axis=1)
_cm.index = pd.DatetimeIndex(_cm.index)
X["P_FMAM_IMERG"] = [_cm.loc[f"{a}-02-01":f"{a}-05-31"].sum() if a >= 1998 else np.nan for a in anos]
X["DIP_check"] = X.TNA_DJ - X.TSA_DJ - X.DIP_DJ
print(f"checagem: DIP_DJ == TNA_DJ - TSA_DJ (max |dif|) = {X.DIP_check.abs().max():.3f}")


def r_ci(x, y):
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = np.asarray(x)[ok], np.asarray(y)[ok]
    n = len(x)
    r = np.corrcoef(x, y)[0, 1]
    z, se = np.arctanh(r), 1 / np.sqrt(n - 3)
    return r, np.tanh(z - 1.645 * se), np.tanh(z + 1.645 * se), n


def fmt(t):
    r, lo, hi, n = t
    return f"{r:+.2f} (IC90 {lo:+.2f} a {hi:+.2f}; n={n})"


# ---------------- A) chuva FMAM x safra ----------------
print("\n================ A) r(chuva FMAM NASA, producao e rendimento) - artigo: milho +0,52/+0,38, feijao +0,46/+0,22 (1952-2000, FUNCEME)")
for nome, D in [("milho", M), ("feijao", F)]:
    for chuva, ini in [("P_FMAM_POWER", 1981), ("P_FMAM_IMERG", 1998)]:
        for a0, a1 in [(ini, 2000), (2001, 2025), (ini, 2025)]:
            if a1 - a0 < 8:
                continue
            idx = [a for a in range(a0, a1 + 1)]
            x = X.loc[idx, chuva]
            print(f"  {nome:6s} {chuva:13s} {a0}-{a1}: producao {fmt(r_ci(x, D.loc[idx, 'producao_t']))} | "
                  f"rend/area plantada {fmt(r_ci(x, D.loc[idx, 'rend_plant']))} | rend/area colhida {fmt(r_ci(x, D.loc[idx, 'rend_colh']))}")

# ---------------- B) categorias ----------------
print("\n================ B) categorias Pacifico (ONI NDJ +-0,5) x Atlantico (dipolo FMA +-0,2), Tabela 1 do artigo")
tab1 = {"DipNeg/PacNeg": [1957, 1974, 1984, 1985, 1986, 1989, 2000], "DipNeg/PacNeu": [1991, 1994],
        "DipNeg/PacPos": [1973, 1988, 1995], "DipNeu/PacNeg": [1961, 1965, 1967, 1971, 1972, 1975, 1976, 1996, 1999],
        "DipNeu/PacNeu": [1959, 1982, 1990, 1993], "DipNeu/PacPos": [1964, 1977, 1987, 1998],
        "DipPos/PacNeg": [1955, 1956, 1963, 1968, 1997], "DipPos/PacNeu": [1953, 1954, 1960, 1962, 1978, 1979, 1980, 1981],
        "DipPos/PacPos": [1952, 1958, 1966, 1969, 1970, 1983, 1992]}
artigo = {a: k for k, v in tab1.items() for a in v}


def cat(r):
    p = "PacPos" if r.ONI_NDJ > 0.5 else ("PacNeg" if r.ONI_NDJ < -0.5 else "PacNeu")
    d = "DipPos" if r.DIP_FMA > 0.2 else ("DipNeg" if r.DIP_FMA < -0.2 else "DipNeu")
    return f"{d}/{p}"


X["cat"] = X.apply(cat, axis=1)
ov = [a for a in range(1974, 2001)]
conc_p = np.mean([X.loc[a, "cat"].split("/")[1] == artigo[a].split("/")[1] for a in ov])
conc_d = np.mean([X.loc[a, "cat"].split("/")[0] == artigo[a].split("/")[0] for a in ov])
conc = np.mean([X.loc[a, "cat"] == artigo[a] for a in ov])
print(f"  concordancia com a Tabela 1 em 1974-2000 (27 anos): Pacifico {conc_p:.0%}, Atlantico {conc_d:.0%}, categoria inteira {conc:.0%}")
dis = [f"{a}: artigo {artigo[a]} / nosso {X.loc[a, 'cat']} (ONI {X.loc[a, 'ONI_NDJ']:+.1f}, DIP {X.loc[a, 'DIP_FMA']:+.2f})"
       for a in ov if X.loc[a, "cat"] != artigo[a]]
print("  discordancias: " + "; ".join(dis))


# rendimento sem tendencia: razao a mediana movel centrada de 7 anos (canonica do projeto) e residuo do ajuste linear
def anom(s):
    s = s.astype(float)
    med = s.rolling(7, center=True, min_periods=4).median()
    t = np.arange(len(s))
    b = np.polyfit(t, s.values, 1)
    return s / med - 1, s / np.polyval(b, t) - 1


for nome, D in [("milho", M), ("feijao", F)]:
    D["anom_med7"], D["anom_lin"] = anom(D.rend_colh.loc[1974:2025])  # area colhida: unica serie completa 1974-2025
    D["anom_prod_lin"] = anom(D.producao_t.loc[1974:2025])[1]
    b = np.polyfit(np.arange(1974, 2001), D.rend_colh.loc[1974:2000].values, 1)
    print(f"  tendencia linear do rendimento (prod/area colhida) do {nome} 1974-2000: {b[0]:+.1f} kg/ha/ano "
          f"(artigo: tendencia negativa significativa em 1952-2000); 2001-2025: "
          f"{np.polyfit(np.arange(2001, 2026), D.rend_colh.loc[2001:2025].values, 1)[0]:+.1f} kg/ha/ano")
    print(f"    checagem de numeros do artigo ({nome}): producao 2000 = {D.producao_t.get(2000):,.0f} t; 1994 = {D.producao_t.get(1994):,.0f} t; "
          f"menores 1974-2000: {', '.join(f'{a} {v:,.0f} t' for a, v in D.producao_t.loc[1974:2000].nsmallest(4).items())}; "
          f"area colhida 2000 = {D.area_colhida_ha.get(2000):,.0f} ha")

C = X[["cat"]].join(M[["anom_med7", "anom_prod_lin"]].add_prefix("mi_")).join(F[["anom_med7", "anom_prod_lin"]].add_prefix("fe_"))
g = C.groupby("cat").agg(n=("mi_anom_med7", "size"), anos=("mi_anom_med7", lambda s: ",".join(str(a) for a in s.index)),
                         milho_rend=("mi_anom_med7", "mean"), feijao_rend=("fe_anom_med7", "mean"),
                         milho_prod=("mi_anom_prod_lin", "mean"), feijao_prod=("fe_anom_prod_lin", "mean"))
print("  compostos 1974-2025 (anomalia media; rendimento = razao a mediana movel de 7 anos; producao = desvio da reta):")
for k, r in g.iterrows():
    print(f"    {k:14s} n={r.n:2d} | rend milho {r.milho_rend:+5.0%} feijao {r.feijao_rend:+5.0%} | prod milho {r.milho_prod:+5.0%} "
          f"feijao {r.feijao_prod:+5.0%} | {r.anos}")
# afirmacoes qualitativas do artigo
for crit, sel in [("dipolo positivo (qualquer Pacifico)", C.cat.str.startswith("DipPos")),
                  ("dipolo negativo (qualquer Pacifico)", C.cat.str.startswith("DipNeg")),
                  ("Pacifico quente (qualquer dipolo)", C.cat.str.endswith("PacPos")),
                  ("DipPos/PacPos (o pior do artigo)", C.cat == "DipPos/PacPos")]:
    print(f"  {crit:38s}: n={sel.sum():2d}; rend milho {C.mi_anom_med7[sel].mean():+.0%} (resto {C.mi_anom_med7[~sel].mean():+.0%}); "
          f"feijao {C.fe_anom_med7[sel].mean():+.0%} (resto {C.fe_anom_med7[~sel].mean():+.0%})")

# ---------------- C) modelo prognostico ----------------
print("\n================ C) modelo prognostico (so oceano, antes da estacao): artigo r = +0,51 milho, +0,36 feijao (validacao em anos pares 1952-2000)")
Xd = X[["ONI_NDJ", "TNA_DJ", "TSA_DJ", "DIP_DJ"]].values
print(f"  posto da matriz [1, ONI, TNA, TSA, DIP] = {np.linalg.matrix_rank(np.column_stack([np.ones(len(Xd)), Xd]))} de 5 colunas "
      "-> DIP = TNA - TSA e exatamente colinear; a equacao (4)-(5) com os 4 indices nao e identificavel (so 3 graus de liberdade)")


def ajusta(Xa, ya):
    A = np.column_stack([np.ones(len(Xa)), Xa])
    return np.linalg.lstsq(A, ya, rcond=None)[0]


def preve(b, Xa):
    return np.column_stack([np.ones(len(Xa)), Xa]) @ b


def msess(y, yh, clim):
    return 1 - np.mean((y - yh) ** 2) / np.mean((y - clim) ** 2)


preds = {"ONI_NDJ": ["ONI_NDJ"], "TNA_DJ": ["TNA_DJ"], "TSA_DJ": ["TSA_DJ"], "DIP_DJ": ["DIP_DJ"],
         "ONI+TNA+TSA (= artigo)": ["ONI_NDJ", "TNA_DJ", "TSA_DJ"], "ONI_ASO (portao nov)": ["ONI_ASO"],
         "chuva FMAM POWER (teto, nao e previsao)": ["P_FMAM_POWER"]}
for alvo in ["anom_lin", "anom_med7"]:
    print(f"  --- alvo: rendimento (prod/area colhida) {'sem tendencia linear 1974-2025' if alvo == 'anom_lin' else 'razao a mediana movel de 7 anos'}")
    for nome, D in [("milho", M), ("feijao", F)]:
        Y = D[alvo]
        for pn, cols in preds.items():
            ini = 1981 if "POWER" in pn else 1974
            # (1) protocolo do artigo dentro de 1974-2000: calibra impares, valida pares (e o inverso)
            res = []
            for cal_par in (1, 0):
                cal = [a for a in range(ini, 2001) if a % 2 == cal_par]
                val = [a for a in range(ini, 2001) if a % 2 != cal_par]
                b = ajusta(X.loc[cal, cols].values, Y.loc[cal].values)
                res.append(np.corrcoef(preve(b, X.loc[val, cols].values), Y.loc[val].values)[0, 1])
            # (2) fora do tempo: 1974-2000 -> 2001-2025
            cal = list(range(ini, 2001)); val = list(range(2001, 2026))
            b = ajusta(X.loc[cal, cols].values, Y.loc[cal].values)
            yh = preve(b, X.loc[val, cols].values)
            r_out = np.corrcoef(yh, Y.loc[val].values)[0, 1]
            ms_out = msess(Y.loc[val].values, yh, Y.loc[cal].mean())
            # (3) LOYO 1974-2025
            tudo = list(range(ini, 2026))
            yl = np.array([preve(ajusta(X.loc[[x for x in tudo if x != a], cols].values, Y.loc[[x for x in tudo if x != a]].values),
                                 X.loc[[a], cols].values)[0] for a in tudo])
            r_l = np.corrcoef(yl, Y.loc[tudo].values)[0, 1]
            ms_l = msess(Y.loc[tudo].values, yl, np.array([Y.loc[[x for x in tudo if x != a]].mean() for a in tudo]))
            print(f"    {nome:6s} {pn:40s} impar->par r {res[0]:+.2f} | par->impar {res[1]:+.2f} | 1974-2000 -> 2001-2025 r {r_out:+.2f} "
                  f"MSESS {ms_out:+.2f} | LOYO r {r_l:+.2f} MSESS {ms_l:+.2f}")

# ---------------- D) portao de janeiro: Atlantico DJ x ONI ASO na fracao municipal de quebra ----------------
print("\n================ D) portao de janeiro (P2): o Atlantico de dez-jan acrescenta ao ONI de ASO? (quebra canonica, 1998-2025)")


def serie_q(prefixo):
    p = pam[pam.produto.str.startswith(prefixo)]
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        return pd.Series([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["quebra"] = p.r / p.ref < 0.5
    return p.dropna(subset=["ref"]).groupby("ano").quebra.mean()


for nome, pref in [("milho", "Milho (em gr"), ("feijao", "Feij")]:
    fq = serie_q(pref)
    Z = X.loc[fq.index].copy()
    Z["fq"] = fq.values
    lo = np.log((Z.fq + 0.01) / (1.01 - Z.fq))  # logito da fracao
    out = {}
    for pn, cols in [("ONI_ASO", ["ONI_ASO"]), ("ONI_ASO+TNA_DJ+TSA_DJ", ["ONI_ASO", "TNA_DJ", "TSA_DJ"]),
                     ("ONI_ASO+DIP_DJ", ["ONI_ASO", "DIP_DJ"]), ("ONI_NDJ+TNA_DJ+TSA_DJ", ["ONI_NDJ", "TNA_DJ", "TSA_DJ"])]:
        a_ = list(Z.index)
        yl = np.array([preve(ajusta(Z.loc[[x for x in a_ if x != a], cols].values, lo.loc[[x for x in a_ if x != a]].values),
                             Z.loc[[a], cols].values)[0] for a in a_])
        clim = np.array([lo.loc[[x for x in a_ if x != a]].mean() for a in a_])
        out[pn] = (np.corrcoef(yl, lo.values)[0, 1], msess(lo.values, yl, clim))
    rs = {c: r_ci(Z[c], Z.fq)[0] for c in ["ONI_ASO", "ONI_NDJ", "TNA_DJ", "TSA_DJ", "DIP_DJ", "DIP_FMA", "P_FMAM_IMERG"]}
    print(f"  {nome}: r simples com a fracao em quebra (n=28): " + ", ".join(f"{k} {v:+.2f}" for k, v in rs.items()))
    # parcial do Atlantico DJ dado ONI ASO
    for c in ["TNA_DJ", "TSA_DJ", "DIP_DJ"]:
        e1 = Z.fq - np.polyval(np.polyfit(Z.ONI_ASO, Z.fq, 1), Z.ONI_ASO)
        e2 = Z[c] - np.polyval(np.polyfit(Z.ONI_ASO, Z[c], 1), Z.ONI_ASO)
        print(f"    parcial r({c}, fracao | ONI_ASO) = {np.corrcoef(e1, e2)[0, 1]:+.2f}")
    print("    LOYO (logito da fracao): " + " | ".join(f"{k}: r {v[0]:+.2f} MSESS {v[1]:+.2f}" for k, v in out.items()))
    print("    anos mais quebrados: " + ", ".join(f"{a} {Z.fq[a]:.0%} (ONI_ASO {Z.ONI_ASO[a]:+.1f}, TNA_DJ {Z.TNA_DJ[a]:+.2f}, TSA_DJ {Z.TSA_DJ[a]:+.2f})"
                                               for a in Z.fq.sort_values(ascending=False).index[:6]))
print("\n2027 (indices ja publicados): ONI ASO/2026 = "
      f"{ind.ONI.get(pd.Timestamp(2026, 9, 1), np.nan):+.2f}; TNA/TSA de dez/2026-jan/2027 ainda nao existem (portao de janeiro).")
print(f"Ultimos TNA/TSA no arquivo: {ind.TNA.dropna().index.max():%Y-%m} TNA {ind.TNA.dropna().iloc[-1]:+.2f}, TSA {ind.TSA.dropna().iloc[-1]:+.2f}")
