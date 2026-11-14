"""Cientista do clima - Analise 2: El Nino traz SO seca, ou seca + veranico + calor na floracao (risco composto)?

Perguntas
 (a) ONI (NDJ, conhecido em fev) e dipolo explicam o maior veranico da quadra, o numero de veranicos >= 10 d,
     a anomalia de Tmax e os dias de calor extremo (>= p90 local) na janela de floracao (15/mar-30/abr)?
 (b) Distribuicao condicional por fase do ENSO: El Nino forte (ONI NDJ >= 1,0), neutro, La Nina (<= -0,5).
 (c) Dias "quente-seco" (Tmax >= p90 E dentro de veranico >= 5 d) - o estresse composto que derruba feijao/milho.
Metodo: POWER diario por celula (Ceara, 38 celulas), limiares por percentil da propria celula (1991-2020) para
        contornar o vies de +1,7 C da Tmax do POWER contra o ERA5 (secao 90). Veranico = >= 3 dias com <= 2 mm
        (Rocha et al. 2021, FUNCEME); "veranico longo" = >= 10 dias.
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

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
SAIDA = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas"

ind_anual = pd.read_parquet(DADOS / "power" / "power_ce_indicadores_anuais.parquet")
cel = ind_anual[ind_anual.no_ceara][["lat", "lon"]].drop_duplicates().values
ds = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")
P = ds["PRECTOTCORR"].load()
TX = ds["T2M_MAX"].load()
tempo = pd.DatetimeIndex(P.time.values)

I = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")


def corridas(b):
    """comprimentos das sequencias de True."""
    out, c = [], 0
    for x in b:
        if x:
            c += 1
        else:
            if c:
                out.append(c)
            c = 0
    if c:
        out.append(c)
    return out


def marca_corrida(b, minimo):
    """mascara dos dias que pertencem a corridas de True com comprimento >= minimo."""
    b = np.asarray(b); m = np.zeros_like(b); i = 0
    while i < len(b):
        if b[i]:
            j = i
            while j < len(b) and b[j]:
                j += 1
            if j - i >= minimo:
                m[i:j] = True
            i = j
        else:
            i += 1
    return m


ANOS = range(1982, 2026)
reg = []
clim = (tempo.year >= 1991) & (tempo.year <= 2020)
for la, lo in cel:
    p = P.sel(lat=la, lon=lo).values
    tx = TX.sel(lat=la, lon=lo).values
    fmam_clim = clim & tempo.month.isin([2, 3, 4, 5])
    p90 = np.nanpercentile(tx[fmam_clim], 90)
    txm_clim = np.nanmean(tx[fmam_clim])
    for a in ANOS:
        q = (tempo.year == a) & tempo.month.isin([2, 3, 4, 5])
        fl = (tempo >= pd.Timestamp(a, 3, 15)) & (tempo <= pd.Timestamp(a, 4, 30))
        seco = p[q] <= 2.0
        runs = corridas(seco)
        runs_v = [r for r in runs if r >= 3]
        seco_fl = p[fl] <= 2.0
        quente_fl = tx[fl] >= p90
        em_veranico = marca_corrida(seco_fl, 5)
        reg.append({"ano": a, "lat": la, "lon": lo,
                    "chuva_fmam": np.nansum(p[q]),
                    "maior_veranico": max(runs) if runs else 0,
                    "n_veranicos_3d": len(runs_v),
                    "n_veranicos_10d": sum(r >= 10 for r in runs),
                    "anom_tmax_fmam": np.nanmean(tx[q]) - txm_clim,
                    "dias_quentes_floracao": int(quente_fl.sum()),
                    "dias_quente_seco_floracao": int((quente_fl & em_veranico).sum()),
                    "dias_tmax35_floracao": int((tx[fl] >= 35).sum())})
D = pd.DataFrame(reg)
A = D.groupby("ano").mean(numeric_only=True).drop(columns=["lat", "lon"])
# fracao das celulas com veranico >= 15 d (extensao espacial do evento)
A["frac_celulas_veranico15"] = D.assign(v=D.maior_veranico >= 15).groupby("ano").v.mean()


def mm(s, ano, mes):
    return s.get(pd.Timestamp(ano, mes, 1), np.nan)


A["ONI_NDJ"] = [mm(I["ONI"], a - 1, 12) for a in A.index]
A["ONI_ASO"] = [mm(I["ONI"], a - 1, 9) for a in A.index]
A["DIP_DJ"] = [np.nanmean([mm(I["DIPOLO_TNA_menos_TSA"], a - 1, 12), mm(I["DIPOLO_TNA_menos_TSA"], a, 1)]) for a in A.index]
A["DIP_FMAM"] = [np.nanmean([mm(I["DIPOLO_TNA_menos_TSA"], a, m) for m in (2, 3, 4, 5)]) for a in A.index]

alvos = ["chuva_fmam", "maior_veranico", "n_veranicos_10d", "frac_celulas_veranico15", "anom_tmax_fmam",
         "dias_quentes_floracao", "dias_quente_seco_floracao"]
print("(a) Spearman (1982–2025, média das 38 células do Ceará):")
lin = []
for pr in ["ONI_ASO", "ONI_NDJ", "DIP_DJ", "DIP_FMAM", "chuva_fmam"]:
    for al in alvos:
        if pr == al:
            continue
        r = stats.spearmanr(A[pr], A[al])
        lin.append({"preditor": pr, "alvo": al, "rho": r.statistic, "p": r.pvalue})
L = pd.DataFrame(lin)
print(L.pivot_table(index="preditor", columns="alvo", values="rho").round(2).to_string())
print("p < 0,05:", ", ".join(f"{r.preditor}->{r.alvo} {r.rho:+.2f}" for r in L.itertuples() if r.p < 0.05))

# (b) condicional por fase
A["fase"] = np.where(A.ONI_NDJ >= 1.0, "El Niño forte (≥1,0)", np.where(A.ONI_NDJ <= -0.5, "La Niña (≤−0,5)", "neutro/fraco"))
print("\n(b) Mediana por fase do ENSO (ONI NDJ):")
print(A.groupby("fase")[alvos].median().round(2).to_string())
print("n por fase:", A.fase.value_counts().to_dict())
q1 = A.chuva_fmam.quantile(1 / 3)
for f, g in A.groupby("fase"):
    print(f"  {f}: P(quadra no tercil seco) = {(g.chuva_fmam <= q1).mean():.0%} | P(maior veranico médio ≥ 15 d) = "
          f"{(g.maior_veranico >= 15).mean():.0%} | P(≥ 1 dia quente-seco na floração) = {(g.dias_quente_seco_floracao >= 1).mean():.0%}"
          f" | anos: {list(g.index)}")
# teste de Mann-Whitney El Nino forte vs resto
en = A[A.fase.str.startswith("El")]; ou = A[~A.fase.str.startswith("El")]
for al in alvos:
    u = stats.mannwhitneyu(en[al], ou[al], alternative="two-sided")
    print(f"   Mann-Whitney {al}: El Niño forte mediana {en[al].median():.2f} vs resto {ou[al].median():.2f} (p = {u.pvalue:.3f})")

# (c) parcial: o calor na floracao em El Nino vem so da falta de chuva?
import statsmodels.api as sm  # noqa
X = sm.add_constant(A[["ONI_NDJ", "chuva_fmam"]].assign(chuva_fmam=lambda d: d.chuva_fmam / 100))
for al in ["anom_tmax_fmam", "dias_quentes_floracao"]:
    m = sm.OLS(A[al], X).fit()
    print(f"\n(c) OLS {al} ~ ONI_NDJ + chuva_fmam/100: coef ONI {m.params['ONI_NDJ']:+.3f} (p={m.pvalues['ONI_NDJ']:.3f}); "
          f"coef chuva {m.params['chuva_fmam']:+.3f} (p={m.pvalues['chuva_fmam']:.3f}); R² {m.rsquared:.2f}")

# tendencia dos dias quentes na floracao (o fundo que sobe)
import pymannkendall as mk  # noqa
for al in ["dias_quentes_floracao", "anom_tmax_fmam", "maior_veranico"]:
    t = mk.original_test(A[al].values)
    print(f"Tendência MK {al}: {t.trend} p={t.p:.3f} Sen={t.slope*10:+.2f}/década")
print("\nAnos extremos (dias quente-seco na floração):")
print(A.sort_values("dias_quente_seco_floracao", ascending=False)[["fase", "ONI_NDJ", "DIP_FMAM", "chuva_fmam", "maior_veranico", "dias_quentes_floracao", "dias_quente_seco_floracao"]].head(8).round(2).to_string())
print("\n2024 (exceção pós-El Niño) vs 1998/2016/1983:")
print(A.loc[[1983, 1998, 2016, 2024], ["ONI_NDJ", "DIP_DJ", "DIP_FMAM", "chuva_fmam", "maior_veranico", "dias_quentes_floracao"]].round(2).to_string())
A.to_parquet(SAIDA + "/clima_risco_composto_anual.parquet")
