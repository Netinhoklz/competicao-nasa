"""Climatologista (v3) - checagens rapidas dos artigos do grupo 1 (clima, seca e teleconexao) com POWER, IMERG e ONI/TNA/TSA.

  A) Moura & Shukla 1981 / Hastenrath & Heller 1977: dipolo do Atlantico (TNA quente + TSA fria) -> chuva abaixo do normal "sempre"?
  B) Kayano & Andreoli 2006: "so 36% das vezes uma previsao baseada no ENSO estaria certa" (versao simples com terciis)
  C) Marengo et al. 2017 (AABC 90): ranking de FMAM 1998 e 2012-2016; "16 de 25 anos abaixo do normal"; afirmacoes sobre ENSO
  D) Sparacino et al. 2021: inicio/fim da estacao (Liebmann et al. 2007) e estacao seca no quadrado de 2,5 graus das Serras da
     Capivara e das Confusoes (PI) com IMERG 1998-2025
  E) Nobre & Shukla 1996: norte e sul do Nordeste fora de fase
  F) Rocha Junior et al. 2021: EOF da chuva de fev-abr no Nordeste (IMERG) e ligacao do modo 1 com ENSO e Atlantico
  G) Pontes Filho et al. 2020 / Brito et al. 2018: a seca de 2012-2018 e a maior em duracao e severidade (SPI-12, teoria de corridas)?
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import warnings

warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, DERIV

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
ind.index = pd.DatetimeIndex(ind.index)
ce = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
ce = ce[ce.variavel.isin(["PRECTOTCORR", "IMERG_PRECTOT"])].pivot_table(index="data", columns="variavel", values="valor")
ce.index = pd.DatetimeIndex(ce.index)
# o derivado do CE ja vem em mm/mes (soma dos dias; rotulo "mm/day/mes"); o do NE vem em mm/dia
ne = pd.read_parquet(DERIV / "power_ne_mensal.parquet")
ne = ne[ne.variavel == "PRECTOTCORR"].set_index("data").valor
ne.index = pd.DatetimeIndex(ne.index)
ne = ne * ne.index.days_in_month
print(f"unidade POWER NE mensal: {pd.read_parquet(DERIV / 'power_ne_mensal.parquet').query('variavel==\"PRECTOTCORR\"').unidade.iloc[0]}")


def sazonal(s, a, m0, m1):
    return s.loc[f"{a}-{m0:02d}":f"{a}-{m1:02d}"].sum() if s.loc[f"{a}-{m0:02d}":f"{a}-{m1:02d}"].notna().sum() == m1 - m0 + 1 else np.nan


def mi(serie, a, meses):
    return np.mean([serie.get(pd.Timestamp(a, m, 1), np.nan) for m in meses])


anos = list(range(1981, 2026))
Y = pd.DataFrame(index=anos)
Y["P_CE_POWER"] = [sazonal(ce.PRECTOTCORR, a, 2, 5) for a in anos]
Y["P_CE_IMERG"] = [sazonal(ce.IMERG_PRECTOT, a, 2, 5) if a >= 1998 else np.nan for a in anos]
Y["P_NE_POWER"] = [sazonal(ne, a, 2, 5) for a in anos]
for v, k in [("TNA", "TNA"), ("TSA", "TSA"), ("DIPOLO_TNA_menos_TSA", "DIP")]:
    Y[f"{k}_FMAM"] = [mi(ind[v], a, [2, 3, 4, 5]) for a in anos]
Y["ONI_DJF"] = [ind.ONI.get(pd.Timestamp(a, 1, 1), np.nan) for a in anos]
Y["ONI_FMA"] = [ind.ONI.get(pd.Timestamp(a, 3, 1), np.nan) for a in anos]

print("\n================ A) dipolo do Atlantico x chuva FMAM do Ceara (Moura & Shukla 1981: TNA quente + TSA fria 'sempre' com chuva abaixo)")
for c in ["P_CE_POWER", "P_CE_IMERG"]:
    ok = Y[c].notna()
    rs = {k: stats.pearsonr(Y.loc[ok, k], Y.loc[ok, c])[0] for k in ["TNA_FMAM", "TSA_FMAM", "DIP_FMAM", "ONI_DJF"]}
    print(f"  {c} ({ok.sum()} anos): " + ", ".join(f"r({k}) {v:+.2f}" for k, v in rs.items()))
    med = Y.loc[ok, c].median()
    pat = ok & (Y.TNA_FMAM > 0) & (Y.TSA_FMAM < 0)
    inv = ok & (Y.TNA_FMAM < 0) & (Y.TSA_FMAM > 0)
    print(f"    TNA>0 e TSA<0 (padrao de seca): {pat.sum()} anos, abaixo da mediana em {(Y.loc[pat, c] < med).mean():.0%} "
          f"({', '.join(f'{a}:{Y.loc[a, c] / med:.0%}' for a in Y.index[pat])})")
    print(f"    TNA<0 e TSA>0 (padrao chuvoso): {inv.sum()} anos, acima da mediana em {(Y.loc[inv, c] > med).mean():.0%}")
# controle por ENSO: o dipolo explica alem do ONI?
ok = Y.P_CE_POWER.notna()
Xm = np.column_stack([np.ones(ok.sum()), Y.loc[ok, "ONI_DJF"], Y.loc[ok, "DIP_FMAM"]])
b, res, *_ = np.linalg.lstsq(Xm, Y.loc[ok, "P_CE_POWER"].values, rcond=None)
yh = Xm @ b
r2 = 1 - ((Y.loc[ok, "P_CE_POWER"] - yh) ** 2).sum() / ((Y.loc[ok, "P_CE_POWER"] - Y.loc[ok, "P_CE_POWER"].mean()) ** 2).sum()
r2o = stats.pearsonr(Y.loc[ok, "ONI_DJF"], Y.loc[ok, "P_CE_POWER"])[0] ** 2
print(f"  POWER 1981-2025: R2 so ONI DJF = {r2o:.2f}; ONI DJF + dipolo FMAM (simultaneo) = {r2:.2f}")

print("\n================ B) Kayano & Andreoli 2006: previsao so pelo ENSO (El Nino -> tercil seco, La Nina -> umido, neutro -> normal)")
for c in ["P_CE_POWER", "P_NE_POWER", "P_CE_IMERG"]:
    ok = Y[c].notna()
    v = Y.loc[ok, c]
    t1, t2 = v.quantile([1 / 3, 2 / 3])
    obs = np.where(v < t1, "seco", np.where(v > t2, "umido", "normal"))
    oni = Y.loc[ok, "ONI_DJF"]
    prev = np.where(oni >= 0.5, "seco", np.where(oni <= -0.5, "umido", "normal"))
    hit = (obs == prev).mean()
    en, ln = prev == "seco", prev == "umido"
    print(f"  {c} ({ok.sum()} anos): acerto total {hit:.0%} (ao acaso 33%); P(seco | El Nino DJF) {np.mean(obs[en] == 'seco'):.0%} (n={en.sum()}); "
          f"P(umido | La Nina) {np.mean(obs[ln] == 'umido'):.0%} (n={ln.sum()}); P(seco | El Nino) inclui {', '.join(str(a) for a in v.index[en])}")

print("\n================ C) Marengo et al. 2017 (AABC 90(2) supl. 1)")
for c in ["P_NE_POWER", "P_CE_POWER"]:
    v = Y.loc[1981:2016, c]
    rk = v.rank()
    print(f"  {c}: FMAM 1981-2016, posicao (1 = mais seco de 36): " + ", ".join(f"{a} {int(rk[a])}" for a in [1983, 1993, 1998, 2012, 2013, 2014, 2015, 2016]))
    base = Y.loc[1981:2000, c].mean()
    abaixo = (Y.loc[1992:2016, c] < base).sum()
    abaixo2 = (Y.loc[1991:2015, c] < base).sum()
    print(f"    anos abaixo da media 1981-2000 em 1992-2016: {abaixo} de 25 (artigo: 16 de 25 'desde meados dos anos 1990'); em 1991-2015: {abaixo2} de 25")
    print(f"    2016 mais seco que 2012? {Y.loc[2016, c]:.0f} mm contra {Y.loc[2012, c]:.0f} mm")
print("  ONI (pico de DJF do ano citado) para 'fortes El Ninos em 1998, 2003, 2007, 2011 e 2015' (secao final do artigo):")
for a in [1998, 2003, 2007, 2011, 2015, 2016]:
    pico = ind.ONI.loc[f"{a - 1}-06":f"{a}-05"]
    print(f"    jun/{a - 1}-mai/{a}: max ONI {pico.max():+.1f}, min {pico.min():+.1f}")
for per in ["2011-06:2012-05", "2012-06:2013-05", "2013-06:2014-05"]:
    a0, a1 = per.split(":")
    print(f"    ONI {a0} a {a1}: min {ind.ONI.loc[a0:a1].min():+.1f}, max {ind.ONI.loc[a0:a1].max():+.1f}  (artigo: 'La Nina em 2012-13')")

# ---------------- IMERG NE diario ----------------
print("\n(carregando IMERG NE diario 1998-2025...)")
caixa_pi = dict(lat=slice(-10.25, -7.75), lon=slice(-44.25, -41.75))  # aprox. do quadrado de 2,5 graus do artigo (Fig. 1)
caixa_B = dict(lat=slice(-7.0, -3.0), lon=slice(-41.0, -37.0))      # 'norte do Nordeste' (aprox. da caixa B de Nobre & Shukla)
caixa_C = dict(lat=slice(-15.0, -10.0), lon=slice(-45.0, -40.0))     # 'sul do Nordeste' (aprox. da caixa C)
pi_d, B_m, C_m, FMA = [], [], [], {}
for a in range(1998, 2027):
    ds = xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc").precip
    pi_d.append(ds.sel(**caixa_pi).mean(["lat", "lon"]).to_series())
    B_m.append(ds.sel(**caixa_B).mean(["lat", "lon"]).to_series().resample("MS").sum(min_count=28))
    C_m.append(ds.sel(**caixa_C).mean(["lat", "lon"]).to_series().resample("MS").sum(min_count=28))
    if a <= 2025:
        FMA[a] = ds.sel(time=slice(f"{a}-02-01", f"{a}-04-30")).sum("time").coarsen(lat=5, lon=5, boundary="trim").mean()
    ds.close()
pi_d = pd.concat(pi_d)
B_m, C_m = pd.concat(B_m), pd.concat(C_m)

print("\n================ D) Sparacino et al. 2021 (postos INMET/ANA, jul/1983-jun/2018) x IMERG (jul/1998-jun/2025), quadrado aprox. das Serras (PI)")
print("  artigo: anual 749 +- 140 mm; inicio 11/nov (dp 20 d); fim 11/abr (dp 25 d); estacao 152 +- 26 d; seca 214 +- 34 d; meio da seca 158 +- 31 d;"
      " tendencias: anual -7 +- 2 mm/ano (P=0,0019), taxa de chuva -0,03 +- 0,02 mm/dia/ano (P=0,0648), meio da seca +1,2 +- 0,5 d/ano (P=0,024)")


def maior_corrida(x, lim):
    m = c = 0
    for v in x:
        c = c + 1 if v < lim else 0
        m = max(m, c)
    return m


rows = []
for a in range(1998, 2025):
    x = pi_d.loc[f"{a}-07-01":f"{a + 1}-06-30"]
    if len(x) < 365:
        continue
    A = (x - x.mean()).cumsum()
    on = A.idxmin() + pd.Timedelta(days=1)
    fim = A.idxmax()
    est = x.loc[on:fim]
    rows.append(dict(ano=a, anual=x.sum(), inicio=on, fim=fim, dur=(fim - on).days, taxa=est.mean(), P_est=est.sum(),
                     frac_est=est.sum() / x.sum(), meio_seca=maior_corrida(x.values, 5.0),
                     cdd2=maior_corrida(x.values, 2.0), cdd1=maior_corrida(x.values, 1.0)))
Sp = pd.DataFrame(rows).set_index("ano")


def doy_jul(ts):
    return (ts - pd.Timestamp(ts.year if ts.month >= 7 else ts.year - 1, 7, 1)).days


Sp["d_ini"] = Sp.inicio.map(doy_jul)
Sp["d_fim"] = Sp.fim.map(doy_jul)
Sp["seca"] = (Sp.d_ini.shift(-1) + 365 - Sp.d_fim)  # do fim desta estacao ao inicio da proxima
base = pd.Timestamp(2001, 7, 1)
print(f"  IMERG ({len(Sp)} anos climatologicos): anual {Sp.anual.mean():.0f} +- {Sp.anual.std():.0f} mm; inicio "
      f"{(base + pd.Timedelta(days=Sp.d_ini.mean())):%d/%b} (dp {Sp.d_ini.std():.0f} d); fim {(base + pd.Timedelta(days=Sp.d_fim.mean())):%d/%b} "
      f"(dp {Sp.d_fim.std():.0f} d); estacao {Sp.dur.mean():.0f} +- {Sp.dur.std():.0f} d; seca {Sp.seca.mean():.0f} +- {Sp.seca.std():.0f} d; "
      f"meio da seca (< 5 mm) {Sp.meio_seca.mean():.0f} +- {Sp.meio_seca.std():.0f} d; fracao da chuva dentro da estacao {Sp.frac_est.mean():.0%}")
print(f"  r(chuva da estacao, data de inicio) = {stats.pearsonr(Sp.P_est, Sp.d_ini)[0]:+.2f} (artigo +0,10); r(chuva, fim) = "
      f"{stats.pearsonr(Sp.P_est, Sp.d_fim)[0]:+.2f} (artigo +0,44); r(chuva, duracao) = {stats.pearsonr(Sp.P_est, Sp.dur)[0]:+.2f} (artigo +0,34)")
for col, nome in [("anual", "anual (mm/ano)"), ("taxa", "taxa de chuva (mm/dia/ano)"), ("meio_seca", "meio da seca (d/ano)"), ("cdd2", "CDD < 2 mm (d/ano)")]:
    for a0, a1 in [(1998, 2017), (1998, 2024)]:
        s = Sp.loc[a0:a1, col]
        lr = stats.linregress(s.index, s.values)
        print(f"  tendencia {nome:28s} {a0}-{a1 + 1}: {lr.slope:+.3f} +- {lr.stderr:.3f} (P = {lr.pvalue:.3f}, n = {len(s)})")
ov = Sp.loc[1998:2017]
print("  anos citados no artigo: estacao mais longa 2009-10 (189 d) e 1999-00 (184 d); mais curta 2015-16 (87 d) e 2003-04 (89 d). IMERG: "
      + ", ".join(f"{a}-{str(a + 1)[2:]} {int(Sp.dur[a])} d" for a in [1999, 2003, 2009, 2015]))
print(f"  IMERG: mais longas {', '.join(f'{a}-{str(a + 1)[2:]} ({int(v)} d)' for a, v in ov.dur.nlargest(2).items())}; "
      f"mais curtas {', '.join(f'{a}-{str(a + 1)[2:]} ({int(v)} d)' for a, v in ov.dur.nsmallest(2).items())}")

print("\n================ E) Nobre & Shukla 1996: norte e sul do Nordeste fora de fase (IMERG 1998-2025)")
bf = pd.Series({a: B_m.loc[f"{a}-02":f"{a}-05"].sum() for a in range(1998, 2026)})
cn = pd.Series({a: C_m.loc[f"{a - 1}-11":f"{a}-01"].sum() for a in range(1999, 2026)})
cf = pd.Series({a: C_m.loc[f"{a}-02":f"{a}-05"].sum() for a in range(1998, 2026)})
print(f"  r(sul NDJ anterior, norte FMAM) = {stats.pearsonr(cn, bf.loc[cn.index])[0]:+.2f} (n={len(cn)}); "
      f"r(sul FMAM, norte FMAM) = {stats.pearsonr(cf, bf)[0]:+.2f} (n={len(bf)})")
sec = bf[bf < bf.quantile(1 / 3)].index.intersection(cn.index)
print(f"  anos de seca no norte (tercil inferior FMAM): {list(sec)}; sul NDJ anterior acima da mediana em {(cn.loc[sec] > cn.median()).mean():.0%}")

print("\n================ F) Rocha Junior et al. 2021 (Water 13:1613): EOF da chuva de fev-abr no Nordeste, IMERG 0,5 grau, 1998-2025")
F = xr.concat([FMA[a] for a in sorted(FMA)], dim=pd.Index(sorted(FMA), name="ano"))
Fv = F.values.reshape(len(FMA), -1)
okc = np.isfinite(Fv).all(0)
Z = Fv[:, okc]
Z = (Z - Z.mean(0))
U, s, Vt = np.linalg.svd(Z, full_matrices=False)
var = s ** 2 / (s ** 2).sum()
print(f"  variancia explicada (anomalia em mm, sem padronizar): EOF1 {var[0]:.0%}, EOF2 {var[1]:.0%}, EOF3 {var[2]:.0%}; soma {var[:3].sum():.0%}")
pc = pd.DataFrame(U[:, :3] * s[:3], index=sorted(FMA), columns=["PC1", "PC2", "PC3"])
lat = np.repeat(F.lat.values, len(F.lon))[okc]
for k in range(3):
    load = Vt[k]
    norte = np.abs(load[lat > -9]).mean() / np.abs(load[lat <= -9]).mean()
    rr = {n: stats.pearsonr(pc[f"PC{k + 1}"], [v for v in Y.loc[pc.index, n]])[0] for n in ["ONI_DJF", "ONI_FMA", "DIP_FMAM", "TSA_FMAM", "TNA_FMAM"]}
    print(f"  PC{k + 1}: |carga| norte (lat > -9) / sul = {norte:.1f}; " + ", ".join(f"r({n}) {v:+.2f}" for n, v in rr.items()))

print("\n================ G) seca de 2012-2018: maior em duracao e severidade? SPI-12 do POWER (Ceara e Nordeste), corridas com SPI < 0")


def spi12(m):
    s12 = m.rolling(12).sum().dropna()
    out = pd.Series(index=s12.index, dtype=float)
    for mes in range(1, 13):
        v = s12[s12.index.month == mes]
        a, loc, sc = stats.gamma.fit(v.values, floc=0)
        out[v.index] = stats.norm.ppf(stats.gamma.cdf(v.values, a, loc=loc, scale=sc))
    return out


for nome, m in [("Ceara", ce.PRECTOTCORR.loc[:"2026-10"]), ("Nordeste", ne.loc[:"2026-10"])]:
    sp = spi12(m.dropna())
    ev, cur = [], None
    for t, v in sp.items():
        if v < 0:
            cur = cur or dict(ini=t, dur=0, sev=0.0)
            cur["dur"] += 1; cur["sev"] += -v; cur["fim"] = t
        elif cur:
            ev.append(cur); cur = None
    if cur:
        ev.append(cur)
    E = pd.DataFrame(ev)
    E = E[E.dur >= 3]
    top = E.sort_values("sev", ascending=False).head(4)
    print(f"  {nome}: eventos (SPI-12 < 0, >= 3 meses) por severidade: " + "; ".join(
        f"{r.ini:%m/%Y}-{r.fim:%m/%Y} ({r.dur} meses, severidade {r.sev:.0f})" for r in top.itertuples()))
    print(f"    mais longo: {E.loc[E.dur.idxmax()].ini:%m/%Y}-{E.loc[E.dur.idxmax()].fim:%m/%Y} ({E.dur.max()} meses); SPI-12 atual "
          f"({sp.index[-1]:%m/%Y}) = {sp.iloc[-1]:+.2f}")
