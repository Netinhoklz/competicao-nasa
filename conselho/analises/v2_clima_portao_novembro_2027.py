"""Cientista do clima - Rodada 2, analise 3: o portao de novembro para a quadra 2027, com probabilidades honestas.

O que se sabe em 14/11/2026: ONI ASO/2026 = +2,46 (fora da faixa de treino); TNA e TSA ate set/2026; a estacao seca
(analise 1: normal, sem habilidade) e o solo (analise 2: normal, memoria zero ate fevereiro).

A. Tabela de analogos com o limiar FIXADO na rodada 1 (ONI ASO do ano anterior >= 1,3), 1982-2026:
   quadra fev-mai (IMERG % da mediana desde 1998; POWER, que e reanalise, antes), fracao de municipios em quebra
   canonica do milho (1998-2025), Quixada, e o que so se sabe depois (ONI FMA, dipolo fev-mai).
B. Modelo PRE-REGISTRADO, um so: logistica P(quebra municipal do milho) ~ ONI ASO(t-1), 1998-2025, validada deixando
   o ANO inteiro de fora (Brier contra a climatologia do mesmo treino, BSS com IC90 por bootstrap de anos; tambem no
   nivel do ano). Previsao para 2027 em ONI 2,46 (extrapolacao) e em 2,04 (maximo do treino), com IC90 por
   bootstrap de anos (reamostra anos, reajusta).
C. Ano-catastrofe (>= 50% dos municipios em quebra): taxa-base e taxa nos analogos, Clopper-Pearson 90%.
D. Exploratorio (nao vai para o pitch): o Atlantico de jul-set separa 2024 (sem quebra) de 1998/2016? Onde fica 2026?
So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 230)
rng = np.random.default_rng(2)
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
QX = "2311306"

I = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
I.index = pd.DatetimeIndex(I.index)


def ix(v, ano, mes):
    return float(I[v].get(pd.Timestamp(ano, mes, 1), np.nan))


def media3(v, ano, meses):
    return float(np.nanmean([ix(v, ano, m) for m in meses]))


# ---------------- quebra canonica do milho (mesma receita do arquiteto; copiada, nao importada)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha


def med_outros(g):
    v = g["r"].values
    return pd.Series([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=g.index)


p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
p = p.dropna(subset=["ref"])
p["razao"] = p.r / p.ref
p["quebra"] = (p.razao < 0.5).astype(int)
p["cod"] = p.cod_local.astype(str).str[:7]
p["oni"] = p.ano.map(lambda a: ix("ONI", a - 1, 9))
frac = p.groupby("ano").quebra.mean()
qx = p[p.cod == QX].set_index("ano")
print(f"painel: {len(p)} municipio-anos, {p.cod.nunique()} municipios, {p.ano.nunique()} anos; taxa-base {p.quebra.mean():.3f}")

# ---------------- chuva da quadra: IMERG (media dos 184 municipios) 1998-2026; POWER (reanalise) 1982-2026
ch = pd.read_parquet(A + "saidas/chuva_mun_diaria.parquet")
ch.index = pd.DatetimeIndex(ch.index)
chm = ch.mean(axis=1)
im = pd.Series({a: chm.loc[f"{a}-02-01":f"{a}-05-31"].sum() for a in range(1998, 2027)})
im_pct = im / im.loc[:2025].median()
pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw = pw[pw.variavel == "PRECTOTCORR"].copy()
pw["data"] = pd.DatetimeIndex(pw.data)
un = str(pw.unidade.iloc[0])  # rotulo 'mm/day/mes', mas o valor ja e total mensal (mesma nota de unidade da secao 4.4)
pws = pw.set_index("data").valor
print(f"POWER PRECTOTCORR CE: media de abril 1991-2020 = {pws[pws.index.month == 4].loc['1991':'2020'].mean():.0f} (total mensal em mm)")
pwq = pd.Series({a: pws.loc[f"{a}-02-01":f"{a}-05-01"].sum() for a in range(1982, 2027)})
pw_pct = pwq / pwq.loc[1982:2025].median()
terc_pw = pwq.loc[1982:2025].quantile(1 / 3)
print(f"POWER PRECTOTCORR unidade '{un}'; tercil seco fev-mai (1982-2025) < {terc_pw:.0f} mm; corr POWER x IMERG 1998-2025 = {np.corrcoef(pwq.loc[1998:2025], im.loc[1998:2025])[0, 1]:.2f}")

print("\n" + "=" * 25, "A. Analogos (ONI ASO do ano anterior >= 1,3; limiar fixado na rodada 1)", "=" * 25)
lin = []
for t in range(1982, 2028):
    aso = ix("ONI", t - 1, 9)
    if not (aso >= 1.3):
        continue
    lin.append({"quadra": t, "ONI_ASO(t-1)": aso, "ONI_NDJ": ix("ONI", t - 1, 12), "ONI_FMA(t)": ix("ONI", t, 3),
                "TNA_JAS(t-1)": media3("TNA", t - 1, (7, 8, 9)), "TSA_JAS(t-1)": media3("TSA", t - 1, (7, 8, 9)),
                "DIP_JAS(t-1)": media3("DIPOLO_TNA_menos_TSA", t - 1, (7, 8, 9)),
                "DIP_FMAM(t)": media3("DIPOLO_TNA_menos_TSA", t, (2, 3, 4, 5)) if t <= 2026 else np.nan,
                "POWER_%med": pw_pct.get(t, np.nan) * 100, "POWER_tercil_seco": (pwq.get(t, np.nan) < terc_pw) if t <= 2026 else np.nan,
                "IMERG_%med": im_pct.get(t, np.nan) * 100, "frac_quebra": frac.get(t, np.nan),
                "Quixada_razao": qx.razao.get(t, np.nan)})
TA = pd.DataFrame(lin).set_index("quadra")
print(TA.round(2).to_string())
ana = TA.loc[:2026]
ns = int(ana.POWER_tercil_seco.astype(float).sum()); n = len(ana)
lo, hi = stats.beta.ppf(0.05, ns, n - ns + 1), stats.beta.ppf(0.95, ns + 1, n - ns)
print(f"  POWER 1982-2026: quadra no tercil seco em {ns} de {n} analogos (IC90 Clopper-Pearson {lo:.2f}-{hi:.2f}); taxa-base 1/3")
print(f"  ONI ASO 2026 = {ix('ONI', 2026, 9):.2f}; maximo de ASO entre as quadras 1982-2026: {max(ix('ONI', t - 1, 9) for t in range(1982, 2027)):.2f}")

print("\n" + "=" * 25, "B. Logistica pre-registrada P(quebra municipal) ~ ONI ASO(t-1), LOYO por ano", "=" * 25)
anos = sorted(p.ano.unique())
p["p_loyo"] = np.nan
p["p_clim"] = np.nan
for a in anos:
    tr, te = p.ano != a, p.ano == a
    m = LogisticRegression(C=1e6).fit(p.loc[tr, ["oni"]], p.loc[tr, "quebra"])
    p.loc[te, "p_loyo"] = m.predict_proba(p.loc[te, ["oni"]])[:, 1]
    p.loc[te, "p_clim"] = p.loc[tr, "quebra"].mean()


def bss(df):
    return 1 - ((df.p_loyo - df.quebra) ** 2).mean() / ((df.p_clim - df.quebra) ** 2).mean()


g = {a: p[p.ano == a] for a in anos}
bs = [bss(pd.concat([g[a] for a in rng.choice(anos, len(anos))])) for _ in range(1000)]
print(f"  BSS municipal (LOYO) = {bss(p):+.3f}  IC90 por ano [{np.percentile(bs, 5):+.3f}, {np.percentile(bs, 95):+.3f}]")
Y = p.groupby("ano").agg(f=("quebra", "mean"), pl=("p_loyo", "mean"), pc=("p_clim", "mean"), oni=("oni", "first"))
bss_ano = 1 - ((Y.pl - Y.f) ** 2).sum() / ((Y.pc - Y.f) ** 2).sum()
r_s = stats.spearmanr(Y.oni, Y.f)
print(f"  nivel do ano (n=28): 'BSS' da fracao em quebra = {bss_ano:+.3f}; rho(ONI ASO, fracao) = {r_s[0]:+.2f} (p={r_s[1]:.3f})")
print("  confiabilidade nos anos de ONI ASO(t-1) >= 1,0 (previsto LOYO x observado):")
print(Y[Y.oni >= 1.0].round(2).to_string())
mfull = LogisticRegression(C=1e6).fit(p[["oni"]], p.quebra)
pred = lambda m, x: float(m.predict_proba(pd.DataFrame({"oni": [x]}))[:, 1][0])
bsp = {2.46: [], 2.04: [], 1.5: [], 0.0: []}
for _ in range(1000):
    bb = pd.concat([g[a] for a in rng.choice(anos, len(anos))])
    mb = LogisticRegression(C=1e6).fit(bb[["oni"]], bb.quebra)
    for x in bsp:
        bsp[x].append(pred(mb, x))
for x in bsp:
    print(f"  P(quebra municipal | ONI ASO = {x:.2f}) = {pred(mfull, x):.2f}  IC90 por ano [{np.percentile(bsp[x], 5):.2f}, {np.percentile(bsp[x], 95):.2f}]"
          + ("   <- extrapolacao (acima do maximo 2,04)" if x > 2.04 else ""))
print(f"  coeficiente: {mfull.coef_[0][0]:+.2f} por unidade de ONI; taxa-base {p.quebra.mean():.2f}")

print("\n" + "=" * 25, "C. Ano-catastrofe (>= 50% dos municipios em quebra)", "=" * 25)
cat = frac >= 0.5
print(f"  anos-catastrofe 1998-2025: {list(frac.index[cat])} -> {int(cat.sum())} de {len(frac)}")
for lim in [1.0, 1.3, 2.0]:
    sel = [a for a in frac.index if ix("ONI", a - 1, 9) >= lim]
    k = int(cat[sel].sum()); nn = len(sel)
    lo, hi = (stats.beta.ppf(0.05, k, nn - k + 1) if k > 0 else 0.0), (stats.beta.ppf(0.95, k + 1, nn - k) if k < nn else 1.0)
    print(f"  ONI ASO(t-1) >= {lim}: anos {sel} -> catastrofe em {k} de {nn} (IC90 {lo:.2f}-{hi:.2f})")
print(f"  Quixada nos analogos >= 1,3 da era IMERG: " + ", ".join(f"{a}: razao {qx.razao.get(a, np.nan):.2f} quebra {int(qx.quebra.get(a, -1))}" for a in [1998, 2016, 2024]))
print(f"  Quixada, taxa-base: {int(qx.quebra.sum())} quebras em {len(qx)} anos")

print("\n" + "=" * 25, "D. Exploratorio: Atlantico de jul-set (t-1) nos anos de El Nino (ONI ASO >= 1,0), era IMERG", "=" * 25)
lin = []
for t in list(range(1998, 2026)) + [2027]:
    aso = ix("ONI", t - 1, 9)
    if aso >= 1.0:
        lin.append({"quadra": t, "ONI_ASO": aso, "TNA_JAS": media3("TNA", t - 1, (7, 8, 9)), "TSA_JAS": media3("TSA", t - 1, (7, 8, 9)),
                    "DIP_JAS": media3("DIPOLO_TNA_menos_TSA", t - 1, (7, 8, 9)), "frac_quebra": frac.get(t, np.nan), "IMERG_%med": im_pct.get(t, np.nan) * 100})
print(pd.DataFrame(lin).set_index("quadra").round(2).to_string())

print("\n" + "=" * 25, "E. Sensibilidade: tira um analogo por vez e refaz a logistica (P em ONI 2,46 e 2,04)", "=" * 25)
for a in [None, 1998, 2016, 2024]:
    d = p if a is None else p[p.ano != a]
    mj = LogisticRegression(C=1e6).fit(d[["oni"]], d.quebra)
    print(f"  {'todos os anos' if a is None else 'sem ' + str(a):14s}: P(2,46) = {pred(mj, 2.46):.2f} | P(2,04) = {pred(mj, 2.04):.2f} | coef {mj.coef_[0][0]:+.2f}")
viz = Y.assign(d=(Y.oni - 2.46).abs()).sort_values("d")
for k in (2, 3):
    print(f"  {k} anos mais proximos em ONI ASO ({list(viz.index[:k])}): fracao media em quebra {viz.f.iloc[:k].mean():.2f}")

print("\n" + "=" * 25, "F. Rota de fuga: o El Nino decai ate fev-abr (ONI FMA <= 0,5)? 1951-2026", "=" * 25)
dd = pd.DataFrame({t: {"ASO": ix("ONI", t - 1, 9), "FMA": ix("ONI", t, 3)} for t in range(1951, 2027)}).T.dropna()
fo = dd[dd.ASO >= 1.3]
print("  quadras com ONI ASO(t-1) >= 1,3:", {int(t): (round(r.ASO, 2), round(r.FMA, 2)) for t, r in fo.iterrows()})
k = int((fo.FMA <= 0.5).sum()); nn = len(fo)
print(f"  decaiu ate FMA <= 0,5 em {k} de {nn} (IC90 {stats.beta.ppf(0.05, k, nn - k + 1) if k else 0:.2f}-{stats.beta.ppf(0.95, k + 1, nn - k):.2f})")
b = np.polyfit(dd.ASO, dd.FMA, 1); res = dd.FMA - np.polyval(b, dd.ASO)
print(f"  regressao em todos os anos: FMA = {b[0]:.2f}*ASO {b[1]:+.2f} (dp do residuo {res.std():.2f}); para ASO 2,46: FMA previsto {np.polyval(b, 2.46):.2f};"
      f" P(FMA <= 0,5) = {stats.norm.cdf((0.5 - np.polyval(b, 2.46)) / res.std()):.2f} [extrapolacao]")

print("\n" + "=" * 25, "G. Exploratorio com contraprova: o sinal do TSA de jul-set(t-1) nos 7 analogos desde 1966", "=" * 25)
print("  Hipotese formada AGORA nos 5 analogos 1982-2026 (bloco A/D): TSA_JAS(t-1) < 0 -> quadra seca; > 0 -> escapou.")
print("  Contraprova nos 2 analogos que NAO entraram na hipotese (1966 e 1973; desfecho seco/nao seco da rodada 1,")
print("  cetico_r3_refutacoes.saida.txt bloco D: secos 1966, 1983, 1998, 2016; nao secos 1973, 1988, 2024):")
for t in [1966, 1973, 1983, 1988, 1998, 2016, 2024, 2027]:
    print(f"    {t}: ONI ASO {ix('ONI', t - 1, 9):.2f} | TNA_JAS {media3('TNA', t - 1, (7, 8, 9)):+.2f} | TSA_JAS {media3('TSA', t - 1, (7, 8, 9)):+.2f} | DIP_JAS {media3('DIPOLO_TNA_menos_TSA', t - 1, (7, 8, 9)):+.2f}"
          f" | TSA_FMAM(t) {media3('TSA', t, (2, 3, 4, 5)) if t <= 2026 else float('nan'):+.2f}")
ts = pd.Series({t: media3("TSA", t, (7, 8, 9)) for t in range(1950, 2026)})
tf = pd.Series({t + 1: media3("TSA", t + 1, (2, 3, 4, 5)) for t in range(1950, 2026)})
print(f"  persistencia do TSA: corr(TSA jul-set(t-1), TSA fev-mai(t)) = {np.corrcoef(ts.values, tf.reindex(ts.index + 1).values)[0, 1]:+.2f} (1950-2025)")
