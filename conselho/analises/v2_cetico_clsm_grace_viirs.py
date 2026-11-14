"""Cetico, rodada 2: auditoria de duas concordancias novas (secao 05 do notebook).

A. GLDAS-2.2 CLSM x GRACE (r 0,88 CE / 0,95 NE na secao 05). O CLSM ASSIMILA o GRACE, entao a concordancia e em parte
   circular. Medimos: (1) r bruto com o ciclo sazonal (como na secao 05); (2) r da anomalia sem ciclo sazonal;
   (3) r interanual (medias anuais); e, como referencia NAO circular, o mesmo para o GLDAS-2.1 Noah (que nao assimila o
   GRACE; soma das 4 camadas de solo). A diferenca CLSM - Noah e o teto do que a assimilacao + agua subterranea trazem.
B. VIIRS VNP13A3 x MODIS (r 0,988, vies +0,014 na secao 05). (1) r bruto x r da anomalia sem ciclo sazonal;
   (2) deriva do vies VIIRS - MODIS por ano; (3) o deslocamento "NDVI de fev-mai +0,053 mais verde para a mesma chuva
   desde 2020" (rodada 1, MODIS) aparece tambem no VIIRS, que e outro satelite? Mesmo modelo, mesmos anos (2012-2026).
So le arquivos; nao escreve nada.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
from scipy import stats

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"


def serie(arq, var):
    d = pd.read_parquet(D + arq)
    s = d[d.variavel == var].set_index("data")["valor"].astype(float)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def dessaz(s):
    return s - s.groupby(s.index.month).transform("mean")


def r(a, b):
    j = pd.concat([a, b], axis=1).dropna()
    return j.corr().iloc[0, 1], len(j)


print("=" * 20, "A. GLDAS-2.2 CLSM (assimila GRACE) e GLDAS-2.1 Noah (nao assimila) contra o GRACE", "=" * 20)
for reg in ["ce", "ne"]:
    G = serie(f"grace_{reg}_mensal.parquet", "TWS_anomalia")  # cm
    C = serie(f"gldas_clsm_{reg}_mensal.parquet", "TWS_tavg") / 10  # mm -> cm
    gw = serie(f"gldas_clsm_{reg}_mensal.parquet", "GWS_tavg") / 10
    N = sum(serie(f"gldas_{reg}_mensal.parquet", v) for v in
            ["SoilMoi0_10cm_inst", "SoilMoi10_40cm_inst", "SoilMoi40_100cm_inst", "SoilMoi100_200cm_inst"]) / 10
    comum = G.index.intersection(C.index).intersection(N.index)
    G, C, N, gw = G[comum], C[comum], N[comum], gw[comum]
    lin = []
    for nome, X in [("CLSM TWS (assimila GRACE)", C), ("CLSM so agua subterranea", gw), ("Noah solo 0-200 cm (nao assimila)", N)]:
        rb, n = r(X - X.mean(), G)
        rd, _ = r(dessaz(X), dessaz(G))
        ra, na = r(X.groupby(X.index.year).mean(), G.groupby(G.index.year).mean())
        # variacao mes a mes (so meses consecutivos)
        dx, dg = X.diff(), G.diff()
        cons = pd.Series(comum).diff().dt.days.between(27, 32).values
        rdm, _ = r(dx[cons], dg[cons])
        lin.append({"regiao": reg.upper(), "serie": nome, "r_bruto(c/ sazonal)": rb, "r_anomalia(s/ sazonal)": rd,
                    "r_interanual": ra, "r_variacao_mensal": rdm, "meses": n, "anos": na,
                    "amplitude_sazonal_cm": X.groupby(X.index.month).mean().pipe(lambda m: m.max() - m.min())})
    gamp = G.groupby(G.index.month).mean().pipe(lambda m: m.max() - m.min())
    print(pd.DataFrame(lin).round(3).to_string(index=False))
    print(f"   amplitude sazonal do GRACE {reg.upper()}: {gamp:.1f} cm; meses comuns {len(comum)} "
          f"({comum.min():%Y-%m} -> {comum.max():%Y-%m})")
    # lacuna GRACE -> GRACE-FO (jul/2017-mai/2018): o CLSM continua, sem GRACE para assimilar
    lac = C["2017-07":"2018-05"]
    print(f"   meses do CLSM dentro da lacuna GRACE/GRACE-FO presentes nesta tabela comum: {len(lac)} (a tabela so tem meses com GRACE)")

print("\n" + "=" * 20, "B. VIIRS VNP13A3 x MODIS (NDVI medio do Ceara, mensal)", "=" * 20)
V = serie("viirs_ndvi_ce_mensal.parquet", "ndvi")
M = serie("modis_ce_mensal.parquet", "ndvi")
j = pd.concat([V.rename("v"), M.rename("m")], axis=1).dropna()
print(f"  meses comuns: {len(j)} ({j.index.min():%Y-%m} -> {j.index.max():%Y-%m})")
print(f"  r bruto = {j.corr().iloc[0, 1]:.3f}; vies VIIRS-MODIS = {(j.v - j.m).mean():+.3f}  (reproduz a secao 05)")
jd = pd.concat([dessaz(j.v), dessaz(j.m)], axis=1)
print(f"  r da anomalia sem ciclo sazonal = {jd.corr().iloc[0, 1]:.3f}")
jf = j[j.index.month.isin([2, 3, 4, 5])]
ja = jf.groupby(jf.index.year).mean()
ja = ja[jf.groupby(jf.index.year).size() == 4]
print(f"  r interanual da media fev-mai = {ja.corr().iloc[0, 1]:.3f} (n = {len(ja)} anos)")
b = (j.v - j.m)
ba = b.groupby(b.index.year).mean()
sl = stats.theilslopes(ba.values, ba.index.values)
print(f"  vies anual VIIRS-MODIS: {ba.round(3).to_dict()}")
print(f"  inclinacao de Sen do vies: {sl[0]:+.4f}/ano (IC95 {sl[2]:+.4f} a {sl[3]:+.4f}); "
      f"vies fev-mai 2012-19 = {(ja.v - ja.m).loc[:2019].mean():+.3f}, 2020-26 = {(ja.v - ja.m).loc[2020:].mean():+.3f}")
print(f"  meses da lacuna do Terra (jun-nov/2025) cobertos so pelo VIIRS: {V['2025-06':'2025-11'].notna().sum()} de 6; "
      f"MODIS nesses meses: {M.reindex(pd.date_range('2025-06-01', '2025-11-01', freq='MS')).notna().sum()} de 6")

# deslocamento pos-2020 para a mesma chuva: NDVI fev-mai ~ chuva jan-mai (IMERG CE), ajuste so em 2012-2019
P = serie("imerg_ce_mensal.parquet", "precip_total")
pj_imerg = P[P.index.month <= 5].groupby(P[P.index.month <= 5].index.year).sum()
PW = serie("power_ce_mensal.parquet", "PRECTOTCORR")
PW = PW * PW.index.days_in_month  # mm/dia -> mm/mes
pj_power = PW[PW.index.month <= 5].groupby(PW[PW.index.month <= 5].index.year).sum()
print("\n  Deslocamento pos-2020 (NDVI fev-mai contra chuva jan-mai; ajuste em 2012-2019, residuo medio em 2020-2026):")
for (nome, s), (fonte, pj) in [(x, y) for y in [("IMERG", pj_imerg), ("POWER", pj_power)] for x in [("VIIRS", V), ("MODIS", M)]]:
    sf = s[s.index.month.isin([2, 3, 4, 5])]
    na = sf.groupby(sf.index.year).mean()[sf.groupby(sf.index.year).size() == 4]
    d = pd.concat([na.rename("ndvi"), pj.rename("chuva")], axis=1).dropna().loc[2012:2026]
    tr = d.loc[:2019]
    bb, aa = np.polyfit(np.log(tr.chuva), tr.ndvi, 1)
    res = d.ndvi - (aa + bb * np.log(d.chuva))
    t = stats.ttest_ind(res.loc[2020:], res.loc[:2019])
    print(f"   {nome} x chuva {fonte}: residuo 2020-26 = {res.loc[2020:].mean():+.3f} (anos {list(res.loc[2020:].index)}) vs 2012-19 "
          f"{res.loc[:2019].mean():+.3f}; t = {t.statistic:.2f}, p = {t.pvalue:.3f}; por ano {res.round(3).to_dict()}")
