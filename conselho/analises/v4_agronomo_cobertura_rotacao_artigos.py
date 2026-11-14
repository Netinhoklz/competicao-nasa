"""Agrônomo de plantas de cobertura — rodada v4 (catálogo de rotações comprovadas).

Três blocos rápidos (< 2 min no total):
  A. Efeitos RECALCULADOS a partir das tabelas dos artigos (números transcritos com página/tabela):
     - Melo et al. 2013, Ciência Rural 43(9):1535-1541, Tabela 2 (p. 1539) e Tabela 1 (p. 1538);
     - Nascimento et al. 2008, RBCS 32:579-587, Quadro 5 (p. 586);
     - Andrade Neto et al. 2010, RBEAA 14(2):124-130, Tabela 2 (p. 128): modelo y = 4an/(1+n)^2, n = exp(-(x-b)/c).
     Pergunta: o "efeito da leguminosa" anunciado no resumo é da leguminosa ou do adubo? E o que as letras das tabelas dizem?
  B. Fotoperíodo nos 184 municípios do Ceará e nas latitudes citadas por Miranda et al. 2020 (Agron. Colomb. 38(1):148-155, p. 150-151).
     Pergunta: o teto de biomassa da crotalária por floração precoce (dia curto) vale para o estado inteiro?
  C. Água nas janelas de cobertura no Ceará (IMERG por município, cache do estrategista; ET0 POWER).
     Pergunta: a chuva da quadra entrega a água que os ensaios deram por irrigação (270-370 mm)?
Saída: v4_agronomo_cobertura_rotacao_artigos.saida.txt (mesma pasta).
"""
import json
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import xarray as xr

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220)
AQUI = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")

# ------------------------------------------------------------------ A. tabelas dos artigos
with Cronometro("A: tabelas dos artigos"):
    print("=== A1. Melo et al. 2013, Tabela 2 (p. 1539): milho, média de 9 anos (2000-2008), Mg/ha; letras de Tukey 1% ===")
    sis = ["SD", "SDM", "SDG", "SDGM", "SDF", "SDFM"]
    nao = dict(zip(sis, [3.447, 3.728, 3.226, 3.425, 3.399, 4.000]))
    let_nao = dict(zip(sis, ["bAB", "bAB", "bB", "bAB", "bB", "bA"]))
    adu = dict(zip(sis, [5.063, 5.047, 4.665, 4.849, 5.074, 4.884]))
    let_adu = dict(zip(sis, ["aAB", "aAB", "aB", "aA", "aA", "aA"]))
    print(f"  {'sistema':6s} {'sem NPK':>8s} {'vs SD':>7s} {'com NPK':>8s} {'vs SD':>7s} {'efeito NPK':>11s}")
    for s in sis:
        print(f"  {s:6s} {nao[s]:8.3f} {100 * (nao[s] / nao['SD'] - 1):+6.1f}% {adu[s]:8.3f} {100 * (adu[s] / adu['SD'] - 1):+6.1f}% "
              f"{100 * (adu[s] / nao[s] - 1):+10.1f}%   letras {let_nao[s]} / {let_adu[s]}")
    ef_npk = [100 * (adu[s] / nao[s] - 1) for s in sis]
    ef_leg_nao = [100 * (nao[s] / nao['SD'] - 1) for s in sis[1:]]
    ef_leg_adu = [100 * (adu[s] / adu['SD'] - 1) for s in sis[1:]]
    print(f"  efeito do NPK dentro de cada sistema: {min(ef_npk):.0f}% a {max(ef_npk):.0f}%  <- é a faixa '22% e 49%' do resumo")
    print(f"  efeito da leguminosa sem NPK (vs SD): {min(ef_leg_nao):+.1f}% a {max(ef_leg_nao):+.1f}% (nenhum difere de SD pela letra maiúscula)")
    print(f"  efeito da leguminosa com NPK (vs SD): {min(ef_leg_adu):+.1f}% a {max(ef_leg_adu):+.1f}%")
    print(f"  ganho do NPK cai com mucuna: SD {adu['SD'] - nao['SD']:.2f} -> SDM {adu['SDM'] - nao['SDM']:.2f}; "
          f"SDF {adu['SDF'] - nao['SDF']:.2f} -> SDFM {adu['SDFM'] - nao['SDFM']:.2f} Mg/ha (artigo: 1,62->1,32 e 1,68->0,88)")
    # equivalência em N: (rend sem NPK com leguminosa - SD sem NPK) / (ganho do NPK no SD) * 90 kg N (aprox.; o NPK também tem P e K)
    for s in ["SDM", "SDFM"]:
        print(f"  'equivalente-NPK' grosseiro de {s}: {(nao[s] - nao['SD']) / (adu['SD'] - nao['SD']) * 100:.0f}% do ganho do NPK completo (90N-60P2O5-45K2O)")

    print("\n=== A2. Melo et al. 2013, Tabela 1 (p. 1538): fitomassa na superfície antes do plantio, Mg/ha (sem teste nas células) ===")
    T1 = {  # ano: (não adubado, adubado) por sistema
        2006: ([3.24, 4.17, 3.45, 3.57, 5.29, 3.44], [5.61, 5.00, 5.72, 4.06, 4.58, 5.66]),
        2007: ([4.45, 5.78, 5.01, 5.55, 6.12, 5.98], [6.60, 9.52, 6.11, 6.64, 8.20, 5.81]),
        2008: ([4.55, 6.74, 5.23, 4.19, 5.70, 6.96], [11.07, 6.19, 7.34, 6.07, 4.97, 7.22]),
    }
    for a, (n_, d_) in T1.items():
        n_ = np.array(n_); d_ = np.array(d_)
        print(f"  {a}: sem NPK leguminosas/SD = {np.round(n_[1:] / n_[0], 2)} | com NPK = {np.round(d_[1:] / d_[0], 2)}")

    print("\n=== A3. Nascimento et al. 2008, Quadro 5 (p. 586): caupi, produtividade acumulada de grãos, kg/ha (Tukey 5%) ===")
    cols = ["Adubo 50N", "BR3301+BR3302", "Nativa", "NFB6156+NFB700"]
    Q5 = pd.DataFrame({"Milheto": [3593, 3191, 2516, 4116], "Mucuna": [4183, 1563, 3956, 3457],
                       "Espontânea": [3324, 3516, 3665, 3111]}, index=cols).T
    L5 = pd.DataFrame({"Milheto": ["aA", "aA", "aA", "aA"], "Mucuna": ["aA", "aB", "aA", "aA"],
                       "Espontânea": ["aA", "aA", "aA", "aA"]}, index=cols).T
    print(Q5.to_string())
    print("  letras:"); print(L5.to_string())
    for c in cols:
        print(f"  {c:15s}: mucuna vs espontânea {100 * (Q5.loc['Mucuna', c] / Q5.loc['Espontânea', c] - 1):+5.0f}% | "
              f"mucuna vs milheto {100 * (Q5.loc['Mucuna', c] / Q5.loc['Milheto', c] - 1):+5.0f}% | "
              f"milheto vs espontânea {100 * (Q5.loc['Milheto', c] / Q5.loc['Espontânea', c] - 1):+5.0f}%")
    print("  -> todas as letras minúsculas na coluna são 'a': a planta de cobertura NÃO mudou a produtividade do caupi a 5%,")
    print("     apesar de o texto (p. 584) dizer que a mucuna deu a maior produtividade. Biomassa da cobertura (p. 582):")
    print("     milheto 3.801, espontânea 1.986, mucuna 1.716 kg/ha MS em 60 d; ensaio IRRIGADO (369,4 mm no caupi).")

    print("\n=== A4. Andrade Neto et al. 2010, Tabela 2 (p. 128): sorgo BR 601 após adubos verdes; modelo da Eq. 1 ===")
    T2 = {  # MSPA (a, b, c) do sorgo, Mg/ha
        "V. espontânea": (5.70, 127.51, 26.39), "Lab-lab": (7.56, 111.70, 22.05), "F. porco": (5.13, 100.69, 20.70),
        "C. juncea": (9.70, 133.18, 26.62), "M. preta": (595.00, 248.68, 27.55), "F. guandu": (7.86, 121.48, 20.58),
        "F. caupi": (6.18, 98.08, 17.74), "C. spectabilis": (7.92, 129.34, 27.53), "Coquetel": (18.20, 178.14, 32.45)}
    T1n = {  # Tabela 1 (p. 126): MSPA do adubo verde (Mg/ha) e N acumulado (kg/ha)
        "V. espontânea": (1.50, 10.65), "Lab-lab": (15.30, 246.40), "F. porco": (3.80, 48.14), "C. juncea": (3.53, 51.78),
        "M. preta": (10.30, 199.78), "F. guandu": (1.90, 33.69), "F. caupi": (1.37, 20.52), "C. spectabilis": (0.90, 12.13),
        "Coquetel": (8.27, 113.16)}

    def mod(x, a, b, c):
        n = np.exp(-(x - b) / c)
        return 4 * a * n / (1 + n) ** 2

    lin = []
    for k, (a, b, c) in T2.items():
        lin.append([k, T1n[k][0], T1n[k][1]] + [mod(x, a, b, c) for x in (60, 80, 100)])
    D = pd.DataFrame(lin, columns=["adubo_verde", "MS_AV", "N_AV", "sorgo60", "sorgo80", "sorgo100"]).set_index("adubo_verde")
    D["rel100_%"] = 100 * (D.sorgo100 / D.loc["V. espontânea", "sorgo100"] - 1)
    print(D.round(2).to_string())
    r = np.corrcoef(D.N_AV, D.sorgo100)[0, 1]
    rs = pd.Series(D.N_AV).rank().corr(pd.Series(D.sorgo100).rank())
    print(f"  correlação N acumulado no adubo verde x MS do sorgo aos 100 DAS: Pearson {r:+.2f} | Spearman {rs:+.2f} (n = 9)")
    print("  sem teste estatístico entre tratamentos para o sorgo (só curvas); ensaio IRRIGADO (aspersão no AV, gotejo no sorgo).")

# ------------------------------------------------------------------ B. fotoperíodo


def dia(lat, J, p=0.8333):
    """Duração do dia (h), modelo CBM (Forsythe et al. 1995); p = 0,8333° inclui refração e meio disco solar."""
    th = 0.2163108 + 2 * np.arctan(0.9671396 * np.tan(0.00860 * (J - 186)))
    ph = np.arcsin(0.39795 * np.cos(th))
    x = (np.sin(np.radians(p)) + np.sin(np.radians(lat)) * np.sin(ph)) / (np.cos(np.radians(lat)) * np.cos(ph))
    return 24 - 24 / np.pi * np.arccos(np.clip(x, -1, 1))


with Cronometro("B: fotoperíodo"):
    J = np.arange(1, 366)
    print("\n=== B. Fotoperíodo (h) — referência de Miranda 2020 (p. 151): Mossoró 11,8 h em junho a 12,4 h em dezembro ===")
    REFS = {"Mossoró-RN (Miranda 2020)": -5.21, "Crato-CE (Nascimento 2008)": -7.23, "Arapiraca-AL (Luz 2023)": -9.70,
            "Goiás 16°43'S (Amabile 2000, cit.)": -16.72, "Seropédica-RJ 22°46'S (Pereira 2005, cit.)": -22.77,
            "SP 24°35'S (Lima 2010, cit.)": -24.58, "RS 29°42'S (Facco 2018, cit.)": -29.70}
    for k, la in REFS.items():
        d = dia(la, J)
        print(f"  {k:42s} min {d.min():5.2f} h | max {d.max():5.2f} h | amplitude {d.max() - d.min():4.2f} h | "
              f"fev-mai {d[31:151].mean():5.2f} h | nov-jan {np.r_[d[304:], d[:31]].mean():5.2f} h")
    mun = municipios_ce_gdf()
    cy = np.array([g.centroid.y for g in mun.geometry])
    dd = np.array([dia(la, J) for la in cy])
    print(f"  Ceará, 184 municípios (lat {cy.min():.2f} a {cy.max():.2f}): máx. anual do dia {dd.max(1).min():.2f}-{dd.max(1).max():.2f} h; "
          f"amplitude anual {np.ptp(dd, 1).min():.2f}-{np.ptp(dd, 1).max():.2f} h")
    for lim in (12.5, 13.0):
        la_lim = next(la for la in np.arange(0, 60, 0.1) if dia(-la, J).max() >= lim)
        print(f"  latitude a partir da qual o dia mais longo do ano passa de {lim} h: ~{la_lim:.1f}°")

# ------------------------------------------------------------------ C. água nas janelas
with Cronometro("C: IMERG municipal + ET0"):
    P = pd.read_parquet(AQUI / "estrategista_cache_chuva_mun_diaria.parquet")
    P = P.where(P >= 0)
    et0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"]
    cod_col = next(c for c in mun.columns if "cod" in c.lower() or c.lower() in ("id", "codarea"))
    mun["cod"] = mun[cod_col].astype(str).str[:7]
    cx = np.array([g.centroid.x for g in mun.geometry])
    valida = (np.isfinite(et0.values).mean(0) > 0.9)
    LO, LA = np.meshgrid(et0.lon.values, et0.lat.values)
    iv = np.flatnonzero(valida.ravel())
    E0 = et0.values.reshape(et0.sizes["time"], -1)
    E = pd.DataFrame(np.stack([E0[:, iv[np.argmin((LO.ravel()[iv] - x) ** 2 + (LA.ravel()[iv] - y) ** 2)]] for x, y in zip(cx, cy)], 1),
                     index=pd.DatetimeIndex(et0.time.values), columns=mun.cod.values)
    E = E.fillna(E.groupby(E.index.dayofyear).transform("mean"))
    cods = [c for c in mun.cod.values if c in P.columns]
    P = P[cods]
    E = E[cods].reindex(P.index)
    E = E.fillna(E.groupby(E.index.dayofyear).transform("mean"))
    NOMES = {str(x["id"]): x["nome"] for x in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}

    lin = []
    Pv = P.values; Ev = E.values; t = P.index
    for ano in range(1998, 2026):
        js = t.searchsorted(pd.Timestamp(ano, 1, 1)); je = t.searchsorted(pd.Timestamp(ano, 4, 15))
        r3 = pd.DataFrame(Pv[js:je]).rolling(3, min_periods=3).sum().values
        for k, c in enumerate(cods):
            ok = np.flatnonzero(r3[:, k] >= 20.0)
            if len(ok) == 0:
                lin.append([c, ano, np.nan] + [np.nan] * 6); continue
            j0 = js + ok[0]
            def soma(M, a, b):
                return np.nansum(M[j0 + a: j0 + b, k])
            lin.append([c, ano, t[j0].dayofyear,
                        soma(Pv, 0, 60), soma(Ev, 0, 60),          # cobertura nos 60 d após a 1ª chuva (antes do milho)
                        soma(Pv, 60, 180),                         # milho de 120 d semeado após a cobertura
                        soma(Pv, 0, 120),                          # milho de 120 d semeado na 1ª chuva
                        soma(Pv, 120, 180), soma(Ev, 120, 180)])   # cobertura nos 60 d após a colheita do milho da 1ª chuva
    C = pd.DataFrame(lin, columns=["cod", "ano", "doy1", "P_cob_pre", "E_cob_pre", "P_milho_tardio", "P_milho_cedo",
                                   "P_cob_pos", "E_cob_pos"]).dropna()

print("\n=== C. Água nas janelas de cobertura, Ceará 1998-2025 (IMERG por município; ET0 POWER no centroide) ===")
print(f"  município-anos com 1ª chuva (20 mm/3 d) até 15/abr: {len(C)} de {184 * 28}")
for nome, col, ecol in [("cobertura 60 d ANTES do milho (1ª chuva -> +60 d)", "P_cob_pre", "E_cob_pre"),
                        ("cobertura 60 d APÓS o milho da 1ª chuva (+120 -> +180 d)", "P_cob_pos", "E_cob_pos")]:
    x = C[col]; e = C[ecol]
    dem = 0.8 * e  # demanda aproximada de uma cobertura com Kc médio ~0,8 em 60 d
    print(f"  {nome}:")
    print(f"    chuva mediana {x.median():.0f} mm (p10 {x.quantile(.1):.0f}, p90 {x.quantile(.9):.0f}); ET0 mediana {e.median():.0f} mm; "
          f"P/(0,8·ET0) mediana {(x / dem).median():.2f}")
    for lim in (150, 270, 370):
        print(f"    município-anos com chuva >= {lim} mm: {100 * (x >= lim).mean():.0f}%")
print("  referência de água dos ensaios: Miranda 2020 irrigou a crotalária com 270/310/330 mm (p. 150); Nascimento 2008 deu 369,4 mm ao caupi (p. 581);")
print("  da Luz 2023 deu 370 mm (2021) e 322 mm (2022) ao milho no enchimento (p. 4); Andrade Neto 2010 irrigou adubo verde e sorgo (lâmina não informada).")
x = C.P_milho_tardio; y = C.P_milho_cedo
print(f"  milho de 120 d: chuva mediana no ciclo se semeado na 1ª chuva {y.median():.0f} mm x após 60 d de cobertura {x.median():.0f} mm "
      f"(perda mediana {100 * (1 - (x / y.replace(0, np.nan)).median()):.0f}%)")
C["nome"] = C.cod.map(NOMES)
for nm in ["Crato", "Iguatu", "Quixadá", "Sobral", "Tauá", "Tianguá"]:
    z = C[C.nome == nm]
    print(f"    {nm:8s}: cob. pré P {z.P_cob_pre.median():4.0f} / ET0 {z.E_cob_pre.median():4.0f} mm | cob. pós P {z.P_cob_pos.median():4.0f} / ET0 {z.E_cob_pos.median():4.0f} mm | "
          f"milho cedo {z.P_milho_cedo.median():4.0f} x tardio {z.P_milho_tardio.median():4.0f} mm")
