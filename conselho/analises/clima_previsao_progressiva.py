"""Cientista do clima - Analise 1: o inicio da estacao preve o RESTO da quadra? A previsao se afina ao longo da estacao?

Perguntas
 (a) O rho = -0,67 (inicio Liebmann-Marengo x total da estacao, secao 02) e informacao util ou e mecanico?
     O inicio de L&M e definido olhando o ano inteiro (minimo do acumulado ate 30/abr) e o "total da estacao" soma
     do inicio ao fim: inicio cedo => estacao mais longa => total maior por construcao. O teste honesto e:
     um indicador conhecivel NA DATA de decisao preve a chuva que AINDA VAI CAIR depois dela?
 (b) Previsao progressiva de tercil (deixando 1 ano de fora), em 4 pontos de decisao:
       t0 = 15/nov (Y-1): ONI ASO + dipolo jul-set                         -> alvo: chuva 01/fev-31/mai
       t1 = 01/fev (Y)  : ONI NDJ + dipolo dez-jan + chuva 01/dez-31/jan   -> alvo: chuva 01/fev-31/mai
       t2 = 16/fev (Y)  : + chuva 01/jan-15/fev + dia da 1a chuva de plantio -> alvo: chuva 16/fev-31/mai
       t3 = 16/mar (Y)  : + chuva 01/jan-15/mar + dipolo fev                 -> alvo: chuva 16/mar-31/mai
Dados: NASA POWER diario (PRECTOTCORR, 0,5 x 0,625 grau, 1981-2026) nas celulas do Ceara;
       IMERG V07 diario (0,1 grau, 1998-2025) para checar robustez; indices ONI/TNA/TSA (NOAA).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, DERIV

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
SAIDA = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas"

# ---------------- chuva diaria media do Ceara ----------------
ind_anual = pd.read_parquet(DADOS / "power" / "power_ce_indicadores_anuais.parquet")
cel = ind_anual[ind_anual.no_ceara][["lat", "lon"]].drop_duplicates()
ds = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")
pr = ds["PRECTOTCORR"].load()
M = xr.zeros_like(pr.isel(time=0), dtype=bool)
for _, r in cel.iterrows():
    M.loc[dict(lat=r.lat, lon=r.lon)] = True
print("células POWER no Ceará:", int(M.sum()))
pr_ce = pr.where(M)
serie = pr_ce.mean(("lat", "lon")).to_series()

# IMERG 0,1 grau (robustez), media espacial em caixa do Ceara sem mascara fina (rapido)
try:
    import geopandas as gpd  # noqa
    import shapely
    ce_geom = ceara_gdf().geometry.union_all()
    arqs = sorted((DADOS / "imerg").glob("imerg_ce_diario_*.nc"))
    im = xr.open_mfdataset(arqs, combine="by_coords")["precip"].load()
    lo, la = np.meshgrid(im.lon.values, im.lat.values)
    MI = xr.DataArray(shapely.contains_xy(ce_geom, lo, la), dims=("lat", "lon"))
    serie_im = im.where(MI).mean(("lat", "lon")).to_series()
except Exception as e:  # noqa
    print("IMERG indisponível:", e)
    serie_im = None

# ---------------- indices ----------------
I = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
ONI, DIP, TNA, TSA = I["ONI"], I["DIPOLO_TNA_menos_TSA"], I["TNA"], I["TSA"]


def mm(s, ano, mes):
    return s.get(pd.Timestamp(ano, mes, 1), np.nan)


def soma(s, a, b):
    x = s[a:b]
    return x.sum() if len(x) >= (pd.Timestamp(b) - pd.Timestamp(a)).days * 0.95 else np.nan


def primeira_chuva_plantio(s, ano, limiar=20.0, janela=3, ate="02-15"):
    """dia (doy) da 1a vez em que a soma movel de 3 dias >= 20 mm a partir de 01/jan; censurado em 'ate'+1."""
    x = s[f"{ano}-01-01":f"{ano}-{ate}"]
    r = x.rolling(janela).sum()
    hit = r[r >= limiar]
    lim = pd.Timestamp(f"{ano}-{ate}").dayofyear + 1
    return float(hit.index[0].dayofyear) if len(hit) else float(lim)


def liebmann_marengo(s, ano):
    """inicio/fim (L&M 2001) no ano hidrologico ago(Y-1)-jul(Y); usa o ano inteiro (retrospectivo)."""
    clim = s.mean()
    x = s[f"{ano-1}-08-01":f"{ano}-07-31"]
    if len(x) < 360:
        return np.nan, np.nan, np.nan
    A = (x - clim).cumsum()
    ini = A[: f"{ano}-04-30"].idxmin()
    fim = A[ini:].idxmax()
    doy = ini.dayofyear if ini.month < 8 else ini.dayofyear - 365
    return float(doy), float(x[ini:fim].sum()), float((fim - ini).days)


def montar(s, anos):
    lin = []
    for a in anos:
        lm_ini, lm_tot, lm_dur = liebmann_marengo(s, a)
        lin.append({
            "ano": a,
            "ONI_ASO": mm(ONI, a - 1, 9), "DIP_JAS": np.nanmean([mm(DIP, a - 1, m) for m in (7, 8, 9)]),
            "ONI_NDJ": mm(ONI, a - 1, 12), "DIP_DJ": np.nanmean([mm(DIP, a - 1, 12), mm(DIP, a, 1)]),
            "TNA_DJ": np.nanmean([mm(TNA, a - 1, 12), mm(TNA, a, 1)]), "TSA_DJ": np.nanmean([mm(TSA, a - 1, 12), mm(TSA, a, 1)]),
            "ONI_DJF": mm(ONI, a, 1), "DIP_FEV": mm(DIP, a, 2),
            "chuva_dez_jan": soma(s, f"{a-1}-12-01", f"{a}-01-31"),
            "chuva_jan_15fev": soma(s, f"{a}-01-01", f"{a}-02-15"),
            "chuva_jan_15mar": soma(s, f"{a}-01-01", f"{a}-03-15"),
            "dia_1a_chuva": primeira_chuva_plantio(s, a),
            "LM_inicio": lm_ini, "LM_total_estacao": lm_tot, "LM_duracao": lm_dur,
            "alvo_FMAM": soma(s, f"{a}-02-01", f"{a}-05-31"),
            "alvo_16fev_mai": soma(s, f"{a}-02-16", f"{a}-05-31"),
            "alvo_16mar_mai": soma(s, f"{a}-03-16", f"{a}-05-31"),
        })
    return pd.DataFrame(lin).set_index("ano")


T = montar(serie, range(1982, 2026))
print(f"\nPOWER: {len(T)} anos ({T.index.min()}–{T.index.max()})")

# ---------------- (a) o rho -0,67 e mecanico? ----------------
print("\n(a) Spearman do INÍCIO (L&M, retrospectivo) e da 1a chuva de plantio (tempo real) com cada alvo:")
linhas = []
for pred in ["LM_inicio", "dia_1a_chuva", "chuva_jan_15fev", "chuva_dez_jan"]:
    for alvo in ["LM_total_estacao", "alvo_FMAM", "alvo_16fev_mai", "alvo_16mar_mai"]:
        d = T[[pred, alvo]].dropna()
        r = stats.spearmanr(d[pred], d[alvo])
        linhas.append({"preditor": pred, "alvo": alvo, "rho": round(r.statistic, 2), "p": round(r.pvalue, 3), "n": len(d)})
tab_a = pd.DataFrame(linhas).pivot_table(index="preditor", columns="alvo", values="rho")
print(tab_a.round(2).to_string())
print(pd.DataFrame(linhas).query("p < 0.05").to_string(index=False))

if serie_im is not None:
    TI = montar(serie_im, range(1999, 2026))
    print(f"\nIMERG (robustez, {len(TI)} anos):")
    li = []
    for pred in ["LM_inicio", "dia_1a_chuva", "chuva_jan_15fev"]:
        for alvo in ["LM_total_estacao", "alvo_FMAM", "alvo_16fev_mai", "alvo_16mar_mai"]:
            d = TI[[pred, alvo]].dropna()
            r = stats.spearmanr(d[pred], d[alvo])
            li.append({"preditor": pred, "alvo": alvo, "rho": round(r.statistic, 2), "p": round(r.pvalue, 3)})
    print(pd.DataFrame(li).pivot_table(index="preditor", columns="alvo", values="rho").round(2).to_string())

# ---------------- (b) previsao progressiva de tercil ----------------
def rps(p, k):
    o = np.eye(3)[k]
    return np.sum((np.cumsum(p) - np.cumsum(o)) ** 2) / 2


def loo_tercil(D, cols, alvo, C=0.5):
    d = D[cols + [alvo]].dropna()
    rm, rc, ac, probs = [], [], [], {}
    for ano in d.index:
        tr = d.drop(ano)
        q1, q2 = tr[alvo].quantile([1 / 3, 2 / 3])
        ytr = np.where(tr[alvo] <= q1, 0, np.where(tr[alvo] >= q2, 2, 1))
        yte = int(0 if d.loc[ano, alvo] <= q1 else (2 if d.loc[ano, alvo] >= q2 else 1))
        sc = StandardScaler().fit(tr[cols])
        m = LogisticRegression(C=C, max_iter=2000).fit(sc.transform(tr[cols]), ytr)
        p = m.predict_proba(sc.transform(d.loc[[ano], cols]))[0]
        rm.append(rps(p, yte)); rc.append(rps(np.full(3, 1 / 3), yte)); ac.append(int(np.argmax(p) == yte))
        probs[ano] = (p[0], yte)
    return 1 - np.mean(rm) / np.mean(rc), np.mean(ac), len(d), probs


etapas = {
    "t0 15/nov ONI_ASO+DIP_JAS -> FMAM": (["ONI_ASO", "DIP_JAS"], "alvo_FMAM"),
    "t1 01/fev ONI_NDJ+DIP_DJ -> FMAM": (["ONI_NDJ", "DIP_DJ"], "alvo_FMAM"),
    "t1 01/fev +chuva dez-jan -> FMAM": (["ONI_NDJ", "DIP_DJ", "chuva_dez_jan"], "alvo_FMAM"),
    "t1 01/fev ONI+TNA+TSA separados -> FMAM": (["ONI_NDJ", "TNA_DJ", "TSA_DJ"], "alvo_FMAM"),
    "t2 16/fev só oceano -> 16fev-mai": (["ONI_NDJ", "DIP_DJ"], "alvo_16fev_mai"),
    "t2 16/fev +chuva jan-15fev -> 16fev-mai": (["ONI_NDJ", "DIP_DJ", "chuva_jan_15fev"], "alvo_16fev_mai"),
    "t2 16/fev +1a chuva -> 16fev-mai": (["ONI_NDJ", "DIP_DJ", "dia_1a_chuva"], "alvo_16fev_mai"),
    "t2 16/fev só chuva jan-15fev -> 16fev-mai": (["chuva_jan_15fev"], "alvo_16fev_mai"),
    "t3 16/mar ONI_DJF+DIP_FEV -> 16mar-mai": (["ONI_DJF", "DIP_FEV"], "alvo_16mar_mai"),
    "t3 16/mar +chuva jan-15mar -> 16mar-mai": (["ONI_DJF", "DIP_FEV", "chuva_jan_15mar"], "alvo_16mar_mai"),
}
print("\n(b) Previsão progressiva de tercil (LOO, logística multinomial L2, POWER 1982–2025):")
res = []
probs_guardadas = {}
for nome, (cols, alvo) in etapas.items():
    rpss, acc, n, probs = loo_tercil(T, cols, alvo)
    res.append({"etapa": nome, "RPSS": round(rpss, 3), "acerto_tercil": round(acc, 3), "n": n})
    probs_guardadas[nome] = probs
R = pd.DataFrame(res)
print(R.to_string(index=False))

# ---------------- previsao 2027 no ponto t0 (hoje) ----------------
cols, alvo = etapas["t0 15/nov ONI_ASO+DIP_JAS -> FMAM"]
T26 = montar(serie, range(1982, 2027))  # inclui a quadra 2026 (ja observada)
d = T26[cols + [alvo]].dropna()
q1, q2 = d[alvo].quantile([1 / 3, 2 / 3])
y = np.where(d[alvo] <= q1, 0, np.where(d[alvo] >= q2, 2, 1))
sc = StandardScaler().fit(d[cols])
m = LogisticRegression(C=0.5, max_iter=2000).fit(sc.transform(d[cols]), y)
x27 = pd.DataFrame({"ONI_ASO": [mm(ONI, 2026, 9)], "DIP_JAS": [np.nanmean([mm(DIP, 2026, k) for k in (7, 8, 9)])]})
p27 = m.predict_proba(sc.transform(x27))[0]
print(f"\nQuadra 2027 (t0, hoje): ONI ASO/2026 = {x27.ONI_ASO[0]:+.2f}, dipolo jul–set/2026 = {x27.DIP_JAS[0]:+.2f}")
print(f"  P(seca, normal, chuvosa) = {p27.round(2)} | limites de tercil FMAM: {q1:.0f} / {q2:.0f} mm")
# sensibilidade ao Atlantico: e se o dipolo de dez-jan virar +0,5 (norte quente) ou -0,5 (sul quente)?
cols1, _ = etapas["t1 01/fev ONI_NDJ+DIP_DJ -> FMAM"]
d1 = T26[cols1 + [alvo]].dropna()
y1 = np.where(d1[alvo] <= q1, 0, np.where(d1[alvo] >= q2, 2, 1))
sc1 = StandardScaler().fit(d1[cols1]); m1 = LogisticRegression(C=0.5, max_iter=2000).fit(sc1.transform(d1[cols1]), y1)
print("  Cenários para 01/fev/2027 (ONI NDJ suposto +2,0):")
for dj in (-0.5, 0.0, 0.5):
    p = m1.predict_proba(sc1.transform(pd.DataFrame({"ONI_NDJ": [2.0], "DIP_DJ": [dj]})))[0]
    print(f"    dipolo dez–jan {dj:+.1f}: P(seca, normal, chuvosa) = {p.round(2)}")

# ONI ASO no registro: 2026 e recorde?
aso = ONI[ONI.index.month == 9].sort_values(ascending=False)
print("\nMaiores ONI ASO desde 1950:", {k.year: round(v, 2) for k, v in aso.head(6).items()})
T26.to_parquet(SAIDA + "/clima_tabela_progressiva.parquet")
pd.to_pickle(probs_guardadas, SAIDA + "/clima_probs_loo.pkl")
