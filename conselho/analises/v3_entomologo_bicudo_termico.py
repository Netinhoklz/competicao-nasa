"""Entomologo (v3), teste 1: relogio termico do bicudo com os parametros PUBLICADOS e o dado NASA.

PRE-REGISTRO (escrito antes de rodar):
- Parametros lidos no texto (nada de memoria):
  * Pereira, Diniz & Parra 2023, Insects 14:582 (doi 10.3390/insects14070582), secao 3.2: Tb = 10,18 C e
    K = 357,84 graus-dia (ovo-adulto, dieta artificial, 7 temperaturas constantes 18-32 C).
    Tabela 3 (R0 e lambda por temperatura) e Tabela 1 (sobrevivencia ovo-adulto).
  * Broglio-Micheletti 1991, citado por Azambuja & Degrande 2014 (Arq. Inst. Biol. 81:377), p. 381:
    "ovo-pupa" Tb = 12,3 C e K = 251,2 graus-dia (sensibilidade).
  * Aproximacao antiga do conselho (ecologo_grausdia_geracoes.py): Tb ~10,5 C, K ~346 (2 pontos; nao do artigo).
- Dado NASA: POWER diario 0,5 grau (T2M, T2M_MAX), celula mais proxima de cada AOI; MODIS MOD11A2 LST diurna (AOI mensal).
- Graus-dia: max(0, T2M - Tb) por dia; sensibilidade com corte horizontal em 32 C (maior temperatura testada; o
  artigo NAO define limiar superior). Geracoes = soma / K. Teto termico: sem pre-oviposicao, sem hospedeiro.
- R0 e lambda mensais: interpolacao linear da Tabela 3 na T2M media do mes (1991-2020), presos nas pontas
  (abaixo de 18 C = valor de 18; acima de 32 C = valor de 32). Fator mensal = lambda^30 (so se houver hospedeiro).
- Checagem de Faustino et al. (Braz. J. Biol. 83:e248154): Barbalha-CE, jul-set/2019, "~7 mm" e "~25 C" (INMET).
- Pergunta: o calor do ar do sertao suprime o bicudo (R0 < 1)? Ou a supressao so vem do solo (dessecacao dos
  botoes caidos) e da falta de hospedeiro (vazio sanitario)?
Somente le arquivos. Saida: v3_entomologo_bicudo_termico.saida.txt
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

OUT = Path(__file__).with_suffix(".saida.txt")
LIN = []


def out(s=""):
    print(s)
    LIN.append(str(s))


PARAMS = {"Pereira 2023 (Tb 10,18; K 357,84)": (10.18, 357.84),
          "Broglio-Micheletti 1991 via Azambuja (Tb 12,3; K 251,2)": (12.3, 251.2),
          "aproximacao antiga do conselho (Tb 10,5; K 346)": (10.5, 346.0)}
T_TAB = np.array([18, 20, 22, 25, 28, 30, 32], float)
R0_TAB = np.array([3.367, 9.932, 28.623, 74.766, 74.722, 11.681, 0.675])
LAM_TAB = np.array([1.016, 1.035, 1.067, 1.111, 1.111, 1.083, 0.979])
RM_TAB = np.array([0.016, 0.034, 0.065, 0.105, 0.105, 0.084, -2.084])  # como impresso na Tabela 3
SURV_TAB = np.array([23.3, 29.2, 49.6, 60.8, 51.6, 37.2, 22.1])

out("== A. Coerencia interna da Tabela 3 de Pereira et al. 2023 ==")
out(f"  R0(25 C)/R0(18 C) = {R0_TAB[3] / R0_TAB[0]:.2f} (o resumo diz 22,25)")
for t, rm, lam in zip(T_TAB, RM_TAB, LAM_TAB):
    flag = "  <- nao bate: ln(lambda) = %.4f" % np.log(lam) if abs(np.log(lam) - rm) > 0.01 else ""
    out(f"  {t:4.0f} C: rm impresso {rm:+.3f} | ln(lambda) {np.log(lam):+.4f}{flag}")
# taxa de desenvolvimento pela Tb/K publicada: dias ovo-adulto = K/(T - Tb)
for t, d_art in [(18, 46.2), (32, 16.1)]:
    out(f"  dias ovo-adulto a {t} C pela Tb/K publicada: {357.84 / (t - 10.18):.1f} d (medido no artigo: {d_art} d)")

d = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")
SITIOS = {k: (v[0], v[1]) for k, v in AOIS.items()}
SITIOS["barbalha_faustino"] = (-39.302, -7.305)  # 7 18'18" S, 39 18'7" W (Faustino et al., secao 2.1)

out("\n== B. Geracoes potenciais por ano (POWER T2M diario, 1981-2025; teto termico com hospedeiro o ano todo) ==")
res_ano = {}
for nome, (lon, lat) in SITIOS.items():
    c = d.sel(lon=lon, lat=lat, method="nearest")
    t = c.T2M.to_series().loc["1981":"2025"]
    out(f"  {nome}: celula POWER ({float(c.lat):.2f}, {float(c.lon):.2f}; elevacao da celula "
        f"{float(c.elevacao_m):.0f} m), T2M media {t.mean():.1f} C")
    for pn, (tb, k) in PARAMS.items():
        for corte in (None, 32.0):
            tt = t.clip(upper=corte) if corte else t
            g = ((tt - tb).clip(lower=0).groupby(tt.index.year).sum() / k)
            slope = np.polyfit(g.index.values, g.values, 1)[0] * 10
            tag = "corte 32 C" if corte else "sem corte"
            res_ano[(nome, pn, tag)] = g
            out(f"     {pn:<55s} {tag:<10s}: {g.mean():5.1f} geracoes/ano (min {g.min():.1f}, max {g.max():.1f}; "
                f"tendencia {slope:+.2f}/decada)")

out("\n== C. Janela de entressafra 1/ago-31/dez (o que uma soqueira nao destruida ou o algodao moco permite) ==")
for nome, (lon, lat) in SITIOS.items():
    t = d.sel(lon=lon, lat=lat, method="nearest").T2M.to_series().loc["1981":"2025"]
    tb, k = PARAMS["Pereira 2023 (Tb 10,18; K 357,84)"]
    m = t[(t.index.month >= 8)]
    g = (m - tb).clip(lower=0).groupby(m.index.year).sum() / k
    out(f"  {nome:<18s}: {g.mean():.1f} geracoes potenciais em ago-dez (min {g.min():.1f}, max {g.max():.1f})")

out("\n== D. R0 e fator mensal (lambda^30) pela T2M media mensal 1991-2020 (Tabela 3 interpolada) ==")
modis = pd.read_parquet(DERIV / "modis_aoi_mensal.parquet")
lst = modis[modis.variavel == "lst_dia"].copy()
lst["mes"] = pd.to_datetime(lst.data).dt.month
for nome, (lon, lat) in SITIOS.items():
    c = d.sel(lon=lon, lat=lat, method="nearest")
    t = c.T2M.to_series().loc["1991":"2020"]
    tx = c.T2M_MAX.to_series().loc["1991":"2020"]
    tm = t.groupby(t.index.month).mean()
    txm = tx.groupby(tx.index.month).mean()
    r0 = np.interp(tm.values, T_TAB, R0_TAB)
    lam30 = np.interp(tm.values, T_TAB, LAM_TAB) ** 30
    sv = np.interp(tm.values, T_TAB, SURV_TAB)
    l_aoi = lst[lst.aoi == nome].groupby("mes").valor.mean() if nome in AOIS else None
    out(f"  {nome}")
    out("     mes  T2M   Tmax   R0   lambda^30  sobrev.ovo-adulto%  LST_dia_MODIS")
    for i, mes in enumerate(tm.index):
        lv = f"{l_aoi.get(mes, np.nan):5.1f}" if l_aoi is not None else "  -  "
        out(f"     {mes:3d} {tm[mes]:5.1f} {txm[mes]:6.1f} {r0[i]:6.1f} {lam30[i]:9.1f} {sv[i]:12.1f} {lv:>18s}")
    out(f"     meses com R0 < 1: {int((r0 < 1).sum())}; R0 minimo {r0.min():.1f} (mes {tm.index[r0.argmin()]}); "
        f"lambda^30 minimo {lam30.min():.1f}")

out("\n== E. Dias muito quentes no ar (POWER T2M diaria >= 30 C e >= 32 C), 1991-2020, % dos dias por mes ==")
for nome, (lon, lat) in SITIOS.items():
    t = d.sel(lon=lon, lat=lat, method="nearest").T2M.to_series().loc["1991":"2020"]
    p30 = (t >= 30).groupby(t.index.month).mean() * 100
    p32 = (t >= 32).groupby(t.index.month).mean() * 100
    out(f"  {nome:<18s} >=30 C: " + " ".join(f"{v:4.0f}" for v in p30.values))
    out(f"  {'':<18s} >=32 C: " + " ".join(f"{v:4.0f}" for v in p32.values))

out("\n== F. Checagem do sitio de Faustino et al. (Barbalha, jul-set/2019) ==")
c = d.sel(lon=-39.302, lat=-7.305, method="nearest")
jj = slice("2019-07-01", "2019-09-30")
out(f"  POWER PRECTOTCORR jul-set/2019: {float(c.PRECTOTCORR.sel(time=jj).sum()):.1f} mm (artigo: ~7 mm, INMET)")
out(f"  POWER IMERG_PRECTOT jul-set/2019: {float(c.IMERG_PRECTOT.sel(time=jj).sum()):.1f} mm")
out(f"  POWER T2M media jul-set/2019: {float(c.T2M.sel(time=jj).mean()):.1f} C (artigo: ~25 C)")
im = pd.read_parquet(DERIV / "imerg_aoi_mensal.parquet")
im = im[(im.aoi == "cariri") & (im.variavel == "precip_total") & (pd.to_datetime(im.data) >= "2019-07-01")
        & (pd.to_datetime(im.data) <= "2019-09-30")]
out(f"  IMERG V07 0,1 grau AOI cariri jul-set/2019 (mm/mes): {im.valor.round(1).tolist()} -> soma {im.valor.sum():.1f} mm")
l = lst[(lst.aoi == "cariri") & (pd.to_datetime(lst.data) >= "2019-07-01") & (pd.to_datetime(lst.data) <= "2019-09-30")]
out(f"  MODIS LST diurna AOI cariri jul-set/2019: {l.valor.round(1).tolist()} C "
    f"(solo medido entre linhas no artigo: 37 C aspersao, 41 C gotejo)")

out("\n== G. Geracoes num ciclo de algodao de sequeiro de 150 dias semeado em 1/fev (Pereira 2023) ==")
out("  [Azambuja & Degrande 2014, p. 382, citando Bianchini 2004: 'sete geracoes' num unico ciclo do algodao]")
for nome, (lon, lat) in SITIOS.items():
    t = d.sel(lon=lon, lat=lat, method="nearest").T2M.to_series().loc["1981":"2025"]
    tb, k = PARAMS["Pereira 2023 (Tb 10,18; K 357,84)"]
    g = []
    for a in range(1981, 2026):
        j = t.loc[pd.Timestamp(a, 2, 1):pd.Timestamp(a, 2, 1) + pd.Timedelta(days=149)]
        g.append(((j - tb).clip(lower=0).sum()) / k)
    out(f"  {nome:<18s}: {np.mean(g):.1f} geracoes (min {np.min(g):.1f}, max {np.max(g):.1f})")

OUT.write_text("\n".join(LIN), encoding="utf-8")
