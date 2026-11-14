"""Fisiologista de culturas do semiarido (v3): parametros do grupo 4 do guia de artigos no balde FAO-56 (M1).

Perguntas:
 P0. Os numeros dos artigos batem com eles mesmos? (contas refeitas a partir das tabelas e figuras impressas)
 P1. A ET0 de estacao medida nos ensaios (Souza 2015 em Petrolina 2007-08; Ramos 2014 em Teresina 2009;
     Santos 2026 em Teresina 2022) bate com a ET0 FAO-56 do NASA POWER e do ERA5 no mesmo lugar e periodo?
     E a chuva do ensaio bate com o IMERG?  (decide se o Kc local pode ser multiplicado pela ET0 do POWER)
 P2. O modelo gaussiano Kc(graus-dia) de Souza 2015 (Tabela 3), com a temperatura de satelite/reanalise,
     reproduz as medias de fase da Tabela 2 do proprio artigo?
 P3. Quixada e Ceara: trocar o Kc FAO generico do M1 pelo Kc medido no semiarido (Souza 2015; Bastos 2008 citado
     por Santos 2026) muda ETc, ISNA, data-limite (criterio do M1 e de Campos 2010) e a associacao com o PAM?
 P4. Campos 2010: quanto do efeito de +3/+6 C vem da ETp de Thornthwaite? (Thornthwaite x Penman-Monteith no POWER)
 P5. Bezerra 2007: "produtividade dos cajueirais < 220 kg/ha" confere com o PAM do Ceara?

Dados: IMERG municipal diario (saidas/chuva_mun_diaria.parquet), POWER CE diario (ET0 FAO-56 e T2M), POWER NE mensal,
ERA5 NE diario (et0, gdd10), IMERG NE diario 0,1 grau, IBGE PAM municipal.  So leitura; nada e gravado em dados/.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
QX = "2311306"  # Quixada
rng = np.random.default_rng(0)


def es(t):
    return 0.6108 * np.exp(17.27 * t / (t + 237.3))


def et0_fao56(tmax, tmin, tdew, u2, rs, lat_deg, elev, doy):
    """Copia de scripts/preparar_power.py (mesma formula usada para gerar power_ce_diario_et0.nc)."""
    tmean = (tmax + tmin) / 2
    e_s = (es(tmax) + es(tmin)) / 2
    e_a = es(tdew)
    delta = 4098 * es(tmean) / (tmean + 237.3) ** 2
    pres = 101.3 * ((293 - 0.0065 * elev) / 293) ** 5.26
    gamma = 0.000665 * pres
    phi = np.deg2rad(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(dec), -1, 1))
    ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(phi) * np.sin(dec) + np.cos(phi) * np.cos(dec) * np.sin(ws))
    rso = (0.75 + 2e-5 * elev) * ra
    rns = 0.77 * rs
    rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * np.sqrt(np.maximum(e_a, 0))) \
        * (1.35 * np.clip(rs / rso, 0.25, 1.0) - 0.35)
    rn = rns - rnl
    num = 0.408 * delta * rn + gamma * 900 / (tmean + 273) * u2 * (e_s - e_a)
    den = delta + gamma * (1 + 0.34 * u2)
    return np.maximum(num / den, 0)


def sec(t):
    print("\n" + "=" * 110 + f"\n{t}\n" + "=" * 110)


# ===================================================================================== P0
sec("P0. Contas refeitas a partir dos numeros impressos nos artigos")
print("Souza et al. 2015 (Rev. Caatinga 28(4)): Kc = ETc/ETo por fase, com as somas da Figura 4")
fig4 = {  # (ETc por fase I..IV, ETo por fase I..IV)
    "milho exclusivo": ([203.0, 75.5, 62.3, 46.3], [236.0, 61.4, 64.2, 88.9]),
    "milho consorciado": ([212.4, 87.8, 75.2, 64.1], [236.0, 61.4, 64.2, 88.9]),
    "caupi exclusivo": ([122.7, 103.6, 61.9, 34.4], [180.5, 101.6, 58.4, 54.6]),
    "caupi consorciado": ([155.2, 126.9, 76.5, 49.7], [180.5, 101.6, 58.4, 54.6]),
}
tab2 = {"milho exclusivo": [0.86, 1.23, 0.97, 0.52], "caupi exclusivo": [0.68, 1.02, 1.06, 0.63],
        "milho consorciado": [0.90, 1.30, 1.20, 0.72], "caupi consorciado": [0.86, 1.30, 1.21, 0.91]}
concl = {"milho exclusivo": [0.86, 1.23, 0.97, 0.52], "caupi exclusivo": [0.68, 1.02, 1.06, 0.63],
         "milho consorciado": [0.90, 1.43, 1.17, 0.72], "caupi consorciado": [0.86, 1.25, 1.31, 0.91]}
for k, (etc, eto) in fig4.items():
    kc = np.round(np.array(etc) / np.array(eto), 2)
    print(f"  {k:18s} Fig.4 ETc/ETo={kc.tolist()}  Tabela 2/resumo={tab2[k]}  Conclusoes={concl[k]}  "
          f"soma ETc={sum(etc):.1f}  soma ETo={sum(eto):.1f}")
print("  -> no consorcio, a Figura 4 e as Conclusoes concordam entre si e divergem da Tabela 2 e do resumo nas fases II e III.")

print("\nSouza et al. 2011 (Bragantia 70(3)): Tabelas 1 e 2 (LI = agua aplicada, mm; PG = graos, kg/ha)")
t1 = pd.DataFrame({"trat": ["125", "100", "75", "50", "0"],
                   "LI_caupi": [476.6, 448.7, 420.8, 392.9, 337.1], "LI_milho": [499.1, 471.2, 443.3, 415.4, 359.5],
                   "PG_caupi": [1320.7, 1374.7, 1316.5, 866.0, 571.4], "PG_milho": [3860.0, 3418.3, 3005.0, 2433.3, 1655.0],
                   "EUA_caupi_impresso": [27.7, 30.6, 31.3, 22.0, 17.0], "EUA_milho_impresso": [77.3, 72.5, 67.8, 58.6, 46.3]})
t1["EUA_caupi_kg_ha_mm"] = (t1.PG_caupi / t1.LI_caupi).round(2)
t1["EUA_milho_kg_ha_mm"] = (t1.PG_milho / t1.LI_milho).round(2)
print(t1.to_string(index=False))
print("  -> a coluna impressa 'EUA (kg m-3)' e 10x a conta em kg ha-1 mm-1 (e 100x em kg m-3); unidade trocada.")
red_mi = (1 - t1.PG_milho / 3860.0) * 100
red_cp = (1 - t1.PG_caupi / 1374.7) * 100
print(f"  reducao do milho exclusivo vs 125% (100,75,50,0): {red_mi.round(0).tolist()[1:]}  (texto: 15, 25, 40, 57 'em ambos')")
print(f"  reducao do caupi exclusivo vs 100% (125,75,50,0): {[round(x) for x in [red_cp[0], red_cp[2], red_cp[3], red_cp[4]]]}"
      "  (texto: 4, 4, 23, 48)")
t2c = np.array([622.3, 556.0, 609.0, 373.7, 138.3]); t2m = np.array([3476.7, 2865.8, 2600.0, 2098.3, 1506.7])
print(f"  consorcio, reducao vs 125%: caupi {np.round((1 - t2c / t2c[0]) * 100)[1:].tolist()} (texto 11, 2, 40, 78); "
      f"milho {np.round((1 - t2m / t2m[0]) * 100)[1:].tolist()}")
b = np.polyfit(t1.LI_milho, t1.PG_milho, 1)
print(f"  reta milho exclusivo refeita: PG = {b[1]:.0f} + {b[0]:.2f} x LI  (Figura 1 impressa: -4.105,67 + 15,95 x LI)")
for cult, li, pg in [("milho", t1.LI_milho, t1.PG_milho), ("caupi", t1.LI_caupi, t1.PG_caupi)]:
    ref = 1 if cult == "caupi" else 0
    ky = (1 - pg.iloc[4] / pg.iloc[ref]) / (1 - li.iloc[4] / li.iloc[ref])
    print(f"  'Ky aparente' {cult} (L0 vs melhor, agua APLICADA, deficit so apos 40 DAS): {ky:.2f}")

print("\nSantos et al. 2026 (Rev. Caatinga 39): reducoes de graos (texto) e um 'Ky aparente' com agua aplicada")
for cv, wmax, r1, r2 in [("BRS Inhuma", 311.00, 62.45, 36.10), ("BRS Olho Negro", 332.08, 62.00, 31.96)]:
    k1 = (r1 / 100) / (1 - 133.80 / wmax); k2 = (r2 / 100) / (1 - 191.70 / wmax)
    print(f"  {cv}: otimo {wmax} mm; Ky(133,8 mm)={k1:.2f}; Ky(191,7 mm)={k2:.2f}")
print("  regime 100% ETc = 249,0 mm com 13,2 mm de chuva -> ETc do ciclo (65 DAS) ~ 235,8 mm")

print("\nLima Filho 2000 (PAB 35(5)): LER = 1500/2208 + 700/1550 = "
      f"{1500 / 2208:.3f} + {700 / 1550:.3f} = {1500 / 2208 + 700 / 1550:.2f}; "
      f"'+18%' e '-5%' sao pontos percentuais acima/abaixo de 0,50 (populacao pela metade): {1500 / 2208 - 0.5:+.3f}, {700 / 1550 - 0.5:+.3f}")

print("\nCampos et al. 2010 (RBEAA 14(4)): Tabela 1 (Sertao, % de baixo risco) x texto")
area_sertao = 11108 / 0.489
print(f"  area do Sertao implicita em '11.108 km2 = 48,9%': {area_sertao:.0f} km2")
print(f"  4.752 km2 = {4752 / area_sertao * 100:.1f}%  e  3.366 km2 = {3366 / area_sertao * 100:.1f}% da mesorregiao")
print("  Tabela 1, linha 11-20/01: BR atual 48,9; +3C 20,9; +6C 14,8  |  linha 21-31/01: 91,1; 48,1; 22,7")
print("  -> os tres numeros do texto sao da linha 11-20/jan, mas o texto diz '21 a 31 de janeiro'.")

print("\nRamos et al. 2014 (Eng. Agric. 34(4)): laminas aplicadas 161-322 mm; maximos estimados em 354 e 423 mm")
print("  -> os dois 'otimos' ficam FORA da faixa testada (extrapolacao da quadratica).")
print(f"  reducao Paraguacu 571,0/2498,04: {(1 - 571.0 / 2498.04) * 100:.2f}%  Guariba 670,6/2936,96: {(1 - 670.6 / 2936.96) * 100:.2f}%")

print("\nSantos et al. 2017 (Front. Plant Sci. 8:2074): media medida de forragem (Tabela 3)")
t3 = [9650, 7650, 11500, 10580, 12050, 9750, 14090, 13180, 12610, 9870, 14110, 14010]
print(f"  media dos 12 valores = {np.mean(t3):.0f} kg/ha (texto: 11,6 Mg/ha); Sao Bento media = {np.mean(t3[8:]):.0f} (texto 12650)")
print("  janelas: resumo 15/abr-15/mai, 12/abr-02/mai, 17/abr-25/mai; Resultados 01/mar-15/abr, 15/fev-15/abr, 15/jan-01/abr")

# ===================================================================================== P1
sec("P1. ET0 de estacao dos ensaios x ET0 FAO-56 do POWER (mensal NE) e do ERA5 (diario); chuva x IMERG")
pm = xr.open_dataset(DADOS / "power" / "power_ne_mensal.nc").load()


def serie_mensal(v, lat, lon):
    a = pm[v]
    ok = (~np.isnan(a.values)).mean(0) > 0.5  # grade mista (MERRA-2 x CERES): celulas com dado na maior parte do tempo
    la, lo = np.meshgrid(a.lat.values, a.lon.values, indexing="ij")
    d = np.where(ok, (la - lat) ** 2 + (lo - lon) ** 2, np.inf)
    i, j = np.unravel_index(np.argmin(d), d.shape)
    return a.isel(lat=i, lon=j).to_series(), (float(a.lat[i]), float(a.lon[j]))


def et0_power_mensal(lat, lon, elev):
    s = {}
    cel = {}
    for v in ["T2M_MAX", "T2M_MIN", "T2MDEW", "WS2M", "ALLSKY_SFC_SW_DWN", "T2M"]:
        s[v], cel[v] = serie_mensal(v, lat, lon)
    df = pd.DataFrame(s)
    doy = (df.index + pd.offsets.Day(14)).dayofyear.values
    df["ET0"] = et0_fao56(df.T2M_MAX.values, df.T2M_MIN.values, df.T2MDEW.values, df.WS2M.values,
                          df.ALLSKY_SFC_SW_DWN.values, lat, elev, doy)
    return df, cel


def diario_de_mensal(m, ini, n):
    idx = pd.date_range(ini, periods=n, freq="D")
    return pd.Series(m.reindex(idx.to_period("M").to_timestamp()).values, index=idx)


# checagem do metodo: PM com medias mensais x media da ET0 diaria do POWER CE (mesma fonte), em Quixada
e0d = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"]
qd = e0d.sel(lat=-4.97, lon=-39.02, method="nearest").to_series()
qm_df, _ = et0_power_mensal(-4.97, -39.02, 200.0)
cmp = pd.DataFrame({"diario": qd.resample("MS").mean(), "mensal": qm_df.ET0}).dropna()
FMET = cmp.mensal.sum() / cmp.diario.sum()
print(f"Metodo (Quixada 1981-2025): PM com medias mensais / media da PM diaria = {FMET:.3f} "
      f"(r mensal = {cmp.corr().iloc[0, 1]:.3f}); as razoes 'POWER/est' abaixo devem ser divididas por esse fator")

era = xr.open_dataset(DADOS / "era5" / "era5_ne_derivados_diario.nc")


def era_serie(v, lat, lon):
    return era[v].sel(lat=lat, lon=lon, method="nearest").to_series()


def imerg_serie(lat, lon, ini, fim):
    out = []
    for a in range(pd.Timestamp(ini).year, pd.Timestamp(fim).year + 1):
        d = xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc")["precip"]
        x = d.sel(lat=slice(lat - 0.15, lat + 0.15), lon=slice(lon - 0.15, lon + 0.15)).mean(["lat", "lon"]).to_series()
        out.append(x)
    s = pd.concat(out)
    return s.loc[ini:fim]


# --- Petrolina, Souza 2015: semeadura 20/12/2007, Campo Exp. Bebedouro (09 09'S, 40 22'W, 365,5 m)
LAT_P, LON_P = -9.15, -40.367
pmP, celP = et0_power_mensal(LAT_P, LON_P, 365.5)
print(f"\nPetrolina: celulas POWER usadas {celP}")
eraP = era_serie("et0", LAT_P, LON_P)
fases = {"milho": [40, 13, 20, 36], "caupi": [30, 21, 12, 16]}
sta = {"milho": [236.0, 61.4, 64.2, 88.9], "caupi": [180.5, 101.6, 58.4, 54.6]}
ini = pd.Timestamp("2007-12-20")
for c, dur in fases.items():
    n = sum(dur)
    pw = diario_de_mensal(pmP.ET0, ini, n)
    er = eraP.reindex(pd.date_range(ini, periods=n, freq="D"))
    lim = np.cumsum([0] + dur)
    rows = []
    for f in range(4):
        a, b_ = lim[f], lim[f + 1]
        rows.append([f"F{f + 1} ({dur[f]} d)", sta[c][f], pw.iloc[a:b_].sum(), er.iloc[a:b_].sum()])
    rows.append(["ciclo", sum(sta[c]), pw.sum(), er.sum()])
    T = pd.DataFrame(rows, columns=["fase", "ETo_estacao", "ET0_POWER", "ET0_ERA5"])
    T["POWER/est"] = T.ET0_POWER / T.ETo_estacao
    T["POWER/est corr"] = T["POWER/est"] / FMET
    T["ERA5/est"] = T.ET0_ERA5 / T.ETo_estacao
    print(f"\n  {c} (Souza 2015, Fig. 4; ciclo {n} d a partir de 20/12/2007):")
    print(T.round(2).to_string(index=False))
rP = imerg_serie(LAT_P, LON_P, "2007-12-20", "2008-04-06")
print(f"  chuva no ciclo do milho: IMERG {rP.sum():.1f} mm (media 3x3 pixels de 0,1 grau) x estacao do ensaio 118,6 mm")
print(f"     IMERG por mes: {rP.resample('MS').sum().round(1).values.tolist()} (dez/07 a abr/08)")
r1 = []
for a in (2007, 2008):
    d_ = xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc")["precip"]
    r1.append(d_.sel(lat=LAT_P, lon=LON_P, method="nearest").to_series())
r1 = pd.concat(r1).loc["2007-12-20":"2008-04-06"]
pr, _ = serie_mensal("PRECTOTCORR", LAT_P, LON_P)
prd = diario_de_mensal(pr, "2007-12-20", 109)
print(f"     IMERG pixel unico: {r1.sum():.1f} mm; POWER PRECTOTCORR (MERRA-2 corrigido, mensal): {prd.sum():.1f} mm")
print("     conta do proprio artigo (Souza 2011/2015): L0 milho = 359,5 mm = irrigacao a 100% ETo ate 40 DAS (ETo F1 = 236,0)"
      f" + chuva 118,6 -> {236.0 + 118.6:.1f}; L100 - L0 = {471.2 - 359.5:.1f} mm irrigados apos 40 DAS contra ETo F2-F4 = "
      f"{61.4 + 64.2 + 88.9:.1f} mm")

# --- Teresina, Ramos 2014: semeadura 10/09/2009, colheita 56-60 DAS, L4 (100% ETo) = 275 mm aplicados, sem chuva
LAT_T, LON_T = -5.083, -42.483
pmT, celT = et0_power_mensal(LAT_T, LON_T, 72.0)
eraT = era_serie("et0", LAT_T, LON_T)
print(f"\nTeresina: celulas POWER usadas {celT}")
for n in (56, 60):
    pw = diario_de_mensal(pmT.ET0, "2009-09-10", n).sum()
    er = eraT.reindex(pd.date_range("2009-09-10", periods=n, freq="D")).sum()
    print(f"  Ramos 2014, {n} d: lamina 100% ETo aplicada = 275 mm | POWER {pw:.0f} mm ({pw / 275:.2f}x) | ERA5 {er:.0f} mm ({er / 275:.2f}x)")
rT = imerg_serie(LAT_T, LON_T, "2009-09-10", "2009-11-08")
print(f"  chuva 10/09-08/11/2009: IMERG {rT.sum():.1f} mm (artigo: 'nao houve precipitacao')")

# --- Teresina, Santos 2026: jul-set 2022, colheita 65 DAS, 100% ETc com Kc de Bastos 2008 = 249,0 - 13,2 = 235,8 mm
kcB = np.r_[np.full(6, 0.3), np.full(23, 0.5), np.full(12, 0.8), np.full(14, 1.2), np.full(11, 0.8)]
for s0 in ("2022-07-01", "2022-07-10", "2022-07-20"):
    pw = diario_de_mensal(pmT.ET0, s0, len(kcB))
    print(f"  Santos 2026, semeadura {s0}: sum(Kc_Bastos x ET0_POWER) = {(kcB * pw.values).sum():.0f} mm "
          f"(ensaio: ~235,8 mm); ET0_POWER do ciclo = {pw.sum():.0f} mm")
r22 = imerg_serie(LAT_T, LON_T, "2022-07-01", "2022-09-30")
print(f"  chuva jul-set/2022: IMERG {r22.sum():.1f} mm (artigo: 13,2 mm no ciclo)")

# ===================================================================================== P2
sec("P2. Gaussiano Kc(GDA) de Souza 2015 (Tabela 3, Tb = 10 C) x medias de fase da Tabela 2")
gauss = {"milho exclusivo": (1.2509, 1179.4972, 526.9940), "caupi exclusivo": (1.0785, 969.1739, 403.4496),
         "milho consorciado": (1.3004, 1172.3778, 576.7093), "caupi consorciado": (1.3123, 995.0474, 452.1302)}
gddP = era_serie("gdd10", LAT_P, LON_P).reindex(pd.date_range(ini, periods=109, freq="D"))
tP = diario_de_mensal(pmP.T2M, ini, 109)
for fonte, g in [("ERA5 gdd10", gddP.values), ("POWER T2M mensal", np.clip(tP.values - 10, 0, None))]:
    gda = np.cumsum(g)
    print(f"\n  GDA com {fonte}: {g.mean():.1f} graus-dia/dia; GDA no fim do milho (109 d) = {gda[-1]:.0f}")
    for k, (a, b_, c_) in gauss.items():
        dur = fases["milho" if "milho" in k else "caupi"]
        n = sum(dur)
        kc = a * np.exp(-0.5 * ((gda[:n] - b_) / c_) ** 2)
        lim = np.cumsum([0] + dur)
        med = [kc[lim[f]:lim[f + 1]].mean() for f in range(4)]
        pico = int(np.argmax(kc))
        print(f"    {k:18s} Gauss por fase={np.round(med, 2).tolist()}  Tabela 2={tab2[k]}  Kc dia 0={kc[0]:.2f}  "
              f"pico no dia {pico} (fase {np.searchsorted(lim, pico, side='right')})")

# ===================================================================================== P3
sec("P3. M1 com Kc medido no semiarido x Kc FAO generico: Quixada e os 184 municipios (IMERG + ET0 POWER), 1998-2025")
chuva = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["pt"] = mun.geometry.representative_point()
cods = [c for c in chuva.columns if c in set(mun.codarea)]
mun = mun.set_index("codarea").loc[cods]
pdia = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")["T2M"].load()
e0 = e0d.load()
ANOS = np.arange(1998, 2026)
ND = 304
NM = len(cods)
R = np.zeros((NM, len(ANOS), ND), np.float32); E = np.zeros_like(R); TT = np.zeros_like(R)
et0m, t2m = {}, {}
for c in cods:
    p = mun.loc[c, "pt"]
    et0m[c] = e0.sel(lat=p.y, lon=p.x, method="nearest").to_series()
    t2m[c] = pdia.sel(lat=p.y, lon=p.x, method="nearest").to_series()
et0m = pd.DataFrame(et0m); t2m = pd.DataFrame(t2m)
for j, a in enumerate(ANOS):
    idx = pd.date_range(f"{a}-01-01", periods=ND, freq="D")
    R[:, j, :] = chuva.reindex(idx)[cods].fillna(0).values.T
    E[:, j, :] = et0m.reindex(idx)[cods].interpolate().bfill().values.T
    TT[:, j, :] = t2m.reindex(idx)[cods].interpolate().bfill().values.T
iq = cods.index(QX)
print(f"clima: {NM} municipios x {len(ANOS)} anos; Quixada: chuva jan-out mediana {np.median(R[iq].sum(1)):.0f} mm, "
      f"ET0 jan-out mediana {np.median(E[iq].sum(1)):.0f} mm, T2M media {TT[iq].mean():.1f} C")


def degraus(dur, kcs):
    return np.concatenate([np.full(d, k) for d, k in zip(dur, kcs)]).astype(np.float32)


def fao(li, ld, lm, ll, ki, km, ke):
    k = np.concatenate([np.full(li, ki), np.linspace(ki, km, ld), np.full(lm, km), np.linspace(km, ke, ll)])
    crit = np.zeros(len(k), bool); crit[li + ld:li + ld + lm] = True
    return k.astype(np.float32), crit


def crit_fases(dur, quais):
    lim = np.cumsum([0] + dur); m = np.zeros(sum(dur), bool)
    for q in quais:
        m[lim[q]:lim[q + 1]] = True
    return m


ZR = {"milho": (0.6, 0.55), "caupi": (0.5, 0.45)}  # Zr (m), p: os mesmos do M1 (agronomo_isna_zarc_sintetico.py)
VAR = {}
k, cr = fao(20, 30, 35, 25, 0.30, 1.20, 0.35); VAR["milho|FAO generico (M1)"] = ("milho", k, cr, None)
d = fases["milho"]
VAR["milho|Souza15 exclusivo"] = ("milho", degraus(d, tab2["milho exclusivo"]), crit_fases(d, [1, 2]), None)
VAR["milho|Souza15 consorcio Tab2"] = ("milho", degraus(d, tab2["milho consorciado"]), crit_fases(d, [1, 2]), None)
VAR["milho|Souza15 consorcio Fig4"] = ("milho", degraus(d, concl["milho consorciado"]), crit_fases(d, [1, 2]), None)
VAR["milho|Souza15 gauss GDA"] = ("milho", np.zeros(109, np.float32), crit_fases(d, [1, 2]), gauss["milho exclusivo"])
k, cr = fao(15, 20, 25, 15, 0.40, 1.05, 0.35); VAR["caupi|FAO generico (M1)"] = ("caupi", k, cr, None)
d = fases["caupi"]
VAR["caupi|Souza15 exclusivo"] = ("caupi", degraus(d, tab2["caupi exclusivo"]), crit_fases(d, [1, 2]), None)
VAR["caupi|Bastos08 (Santos26)"] = ("caupi", kcB.astype(np.float32), crit_fases([6, 23, 12, 14, 11], [3]), None)
VAR["caupi|Souza15 gauss GDA"] = ("caupi", np.zeros(79, np.float32), crit_fases(d, [1, 2]), gauss["caupi exclusivo"])


def simular(nome, sow, taw_fix=None, esc=1.0):
    cult, kc, crit, gp = VAR[nome]
    L = len(kc)
    zr, p = ZR[cult]
    taw = taw_fix if taw_fix is not None else 100.0 * zr
    raw = p * taw
    shp = sow.shape
    Dr = np.full(shp, taw, np.float32)
    gda = np.zeros(shp, np.float32)
    acc = {x: np.zeros(shp, np.float32) for x in ("eta", "etc", "etam", "etcm", "P", "e0")}
    for dd in range(ND):
        kk = dd - sow
        P = R[:, :, dd]; e = E[:, :, dd] * esc
        dentro = (kk >= 0) & (kk < L)
        if gp is None:
            kci = np.where(dentro, kc[np.clip(kk, 0, L - 1)], 0.0)
        else:
            gda = np.where(dentro, gda + np.clip(TT[:, :, dd] - 10, 0, None), 0.0)
            kci = np.where(dentro, gp[0] * np.exp(-0.5 * ((gda - gp[1]) / gp[2]) ** 2), 0.0)
        ks = np.where(Dr <= raw, 1.0, np.clip((taw - Dr) / (taw - raw), 0, 1))
        kbare = 0.3 * np.clip((taw - Dr) / taw, 0, 1)
        etc = kci * e
        eta = np.where(dentro, ks * etc, kbare * e)
        Dr = np.clip(Dr - P + eta, 0, taw)
        ism = dentro & crit[np.clip(kk, 0, L - 1)]
        acc["eta"] += np.where(dentro, eta, 0); acc["etc"] += etc
        acc["etam"] += np.where(ism, eta, 0); acc["etcm"] += np.where(ism, etc, 0)
        acc["P"] += np.where(dentro, P, 0); acc["e0"] += np.where(dentro, e, 0)
    return {"isna": acc["eta"] / np.maximum(acc["etc"], 1e-6), "isna_crit": acc["etam"] / np.maximum(acc["etcm"], 1e-6),
            "etc": acc["etc"], "P": acc["P"], "e0": acc["e0"]}


# regra do agricultor do M1: 1o dia com >= 20 mm em 3 dias a partir de 1/jan; sem isso, 30/abr
c3 = np.zeros_like(R); c3[:, :, 2:] = R[:, :, 2:] + R[:, :, 1:-1] + R[:, :, :-2]
ok = c3 >= 20; ok[:, :, :2] = False; ok[:, :, 120:] = False
sow_ag = np.where(ok.any(2), ok.argmax(2), 119)
print(f"semeadura do agricultor em Quixada (mediana 1998-2025): dia {int(np.median(sow_ag[iq]))} do ano")

RES = {}
for nome in VAR:
    RES[nome] = simular(nome, sow_ag)
print("\nQuixada, semeadura do agricultor, medianas 1998-2025:")
rows = []
for nome, r in RES.items():
    rows.append([nome, np.median(r["e0"][iq]), np.median(r["etc"][iq]), np.median(r["etc"][iq] / r["e0"][iq]),
                 np.median(r["P"][iq]), np.median(r["isna"][iq]), np.median(r["isna_crit"][iq]),
                 (r["isna_crit"][iq] < 0.5).mean()])
Q = pd.DataFrame(rows, columns=["variante", "ET0_ciclo", "ETc_ciclo", "Kc_medio", "chuva_ciclo", "ISNA", "ISNA_crit",
                                "P(ISNA_crit<0,5)"])
print(Q.round(2).to_string(index=False))
print("  referencia medida (Souza 2015, irrigado, Petrolina dez-abr): ETc milho exclusivo 387,0 mm (ETo 450,6); "
      "caupi exclusivo 322,6 mm (ETo 395,9)")

# PAM: rendimento = producao / area plantada (como no M1), anomalia log contra a mediana do municipio
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(str)
MAP = {"milho": "Milho (em grão)", "caupi": "Feijão (em grão)"}
anoms = {}
for cult, prod in MAP.items():
    Y = pam[(pam.produto == prod) & pam.ano.between(1998, 2025) & (pam.area_plantada_ha > 0) & (pam.producao_t > 0)].copy()
    Y["ly"] = np.log(Y.producao_t * 1000 / Y.area_plantada_ha)
    Y["anom"] = Y.ly - Y.groupby("cod").ly.transform("median")
    anoms[cult] = Y.set_index(["cod", "ano"]).anom
print("\nAssociacao com o PAM (184 municipios x 28 anos): Spearman(ISNA, anomalia log do rendimento)")
print("  IC90 por reamostragem de anos inteiros (1000x) da diferenca contra o Kc FAO generico do M1")
base = {"milho": "milho|FAO generico (M1)", "caupi": "caupi|FAO generico (M1)"}
idx = pd.MultiIndex.from_product([cods, ANOS], names=["cod", "ano"])
for cult in ("milho", "caupi"):
    an = anoms[cult].reindex(idx).values.reshape(NM, len(ANOS))
    m = ~np.isnan(an)

    def rho(x, anos_sel):
        xs = x[:, anos_sel]; ys = an[:, anos_sel]; mm = m[:, anos_sel]
        return stats.spearmanr(xs[mm], ys[mm])[0]

    allyr = np.arange(len(ANOS))
    boots = [rng.choice(allyr, len(allyr)) for _ in range(1000)]
    for met in ("isna", "isna_crit"):
        xb = RES[base[cult]][met]
        rb = rho(xb, allyr)
        for nome in [n for n in VAR if n.startswith(cult)]:
            x = RES[nome][met]
            r0 = rho(x, allyr)
            if nome == base[cult]:
                print(f"  {cult:5s} {met:9s} {nome:30s} rho={r0:+.3f}  (n={m.sum()})")
                continue
            dif = [rho(x, bb) - rho(xb, bb) for bb in boots]
            print(f"  {cult:5s} {met:9s} {nome:30s} rho={r0:+.3f}  dif={r0 - rb:+.3f}  IC90 [{np.percentile(dif, 5):+.3f}, "
                  f"{np.percentile(dif, 95):+.3f}]")

# data-limite: criterio do M1 (P(ISNA_crit >= 0,5) >= 0,7) e de Campos 2010 (>= 0,8)
DEC = {"01/jan": 0, "11/jan": 10, "21/jan": 20, "01/fev": 31, "11/fev": 41, "21/fev": 51, "01/mar": 59,
       "11/mar": 69, "21/mar": 79, "01/abr": 90, "11/abr": 100, "21/abr": 110}
print("\nData-limite por decendio fixo (ultimo decendio com P(ISNA_crit >= 0,5) >= alvo), Quixada e mediana estadual")
for taw_fix, rot in [(None, "TAW do M1 (100 mm/m x Zr)"), (40.0, "CAD = 40 mm (Campos 2010)")]:
    print(f"  -- {rot}")
    for nome in VAR:
        P_ = np.zeros((NM, len(DEC)))
        for jd, (dn, dd) in enumerate(DEC.items()):
            r = simular(nome, np.full((NM, len(ANOS)), dd), taw_fix=taw_fix)
            P_[:, jd] = (r["isna_crit"] >= 0.5).mean(1)
        out = []
        for alvo in (0.7, 0.8):
            def dl(row):
                oks = [i for i in range(len(DEC)) if row[i] >= alvo]
                return oks[-1] if oks else -1
            dls = np.array([dl(P_[i]) for i in range(NM)])
            nomes_dec = list(DEC) + ["nenhum"]
            qx_ = nomes_dec[dls[iq]] if dls[iq] >= 0 else "nenhum"
            ok_ = dls[dls >= 0]
            med = nomes_dec[int(np.median(ok_))] if len(ok_) else "nenhum"
            out.append(f"alvo {alvo}: Quixada {qx_:7s} mediana {med:7s} ({(dls < 0).sum():3d} mun. sem data)")
        print(f"   {nome:30s} P Quixada 01/fev..21/mar={np.round(P_[iq, 3:9], 2).tolist()}  " + " | ".join(out))

print("\nSensibilidade a escala da ET0 (P1: estacao/POWER ~ 0,65 em Petrolina 2007-08; ERA5/POWER ~ 0,87):")
print("  data-limite com alvo 0,7 (M1), TAW do M1; Quixada | mediana estadual | ETc mediana do ciclo em Quixada (agricultor)")
for nome in ["milho|FAO generico (M1)", "milho|Souza15 exclusivo", "caupi|FAO generico (M1)", "caupi|Souza15 exclusivo"]:
    linha = []
    for esc in (1.0, 0.87, 0.65):
        P_ = np.zeros((NM, len(DEC)))
        for jd, (dn, dd) in enumerate(DEC.items()):
            P_[:, jd] = (simular(nome, np.full((NM, len(ANOS)), dd), esc=esc)["isna_crit"] >= 0.5).mean(1)
        dls = np.array([max([i for i in range(len(DEC)) if P_[m_, i] >= 0.7], default=-1) for m_ in range(NM)])
        nd = list(DEC)
        etc_q = np.median(simular(nome, sow_ag, esc=esc)["etc"][iq])
        linha.append(f"x{esc:.2f}: {nd[dls[iq]] if dls[iq] >= 0 else 'nenhum'} | "
                     f"{nd[int(np.median(dls[dls >= 0]))]} | ETc {etc_q:.0f} mm")
    print(f"   {nome:26s} " + "   ".join(linha))

# ===================================================================================== P4
sec("P4. Campos 2010: +3 e +6 C na ETp de Thornthwaite x na ET0 FAO-56 (POWER diario, Quixada, 1991-2020)")
pc = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc").sel(lat=-4.97, lon=-39.02, method="nearest").load()
df = pc[["T2M", "T2M_MAX", "T2M_MIN", "T2MDEW", "WS2M", "ALLSKY_SFC_SW_DWN"]].to_dataframe().loc["1991":"2020"]
elev = float(pc["elevacao_m"]) if "elevacao_m" in pc else 200.0
doy = df.index.dayofyear.values
jm = df.index.month <= 5


def pm_dt(dt):
    tx, tn = df.T2M_MAX.values + dt, df.T2M_MIN.values + dt
    es0 = (es(df.T2M_MAX.values) + es(df.T2M_MIN.values)) / 2
    rh = es(df.T2MDEW.values) / es0  # UR media constante
    ea = rh * (es(tx) + es(tn)) / 2
    td = 237.3 * np.log(ea / 0.6108) / (17.27 - np.log(ea / 0.6108))
    return et0_fao56(tx, tn, td, df.WS2M.values, df.ALLSKY_SFC_SW_DWN.values, float(pc.lat), elev, doy)


base_pm = pm_dt(0)[jm].sum() / 30
Tm = df.T2M.resample("MS").mean()
clim = Tm.groupby(Tm.index.month).mean()


def thornthwaite(tmes, I):
    a = 6.75e-7 * I ** 3 - 7.71e-5 * I ** 2 + 1.792e-2 * I + 0.49239
    return 16 * (10 * np.clip(tmes, 0, None) / I) ** a


I0 = ((clim / 5) ** 1.514).sum()
dias = np.array([31, 28.25, 31, 30, 31])
print(f"Elevacao da celula {elev:.0f} m; T media jan-mai {clim.loc[1:5].mean():.1f} C; indice de calor I = {I0:.0f}")
print(f"{'cenario':10s} {'PM jan-mai':>11s} {'dPM':>6s} {'Thorn(I fixo)':>14s} {'dTh':>6s} {'Thorn(I novo)':>14s} {'dTh2':>6s}")
th0 = (thornthwaite(clim.loc[1:5].values, I0) * dias / 30).sum()
for dt in (0, 3, 6):
    p_ = pm_dt(dt)[jm].sum() / 30
    t1_ = (thornthwaite(clim.loc[1:5].values + dt, I0) * dias / 30).sum()
    I1 = (((clim + dt) / 5) ** 1.514).sum()
    t2_ = (thornthwaite(clim.loc[1:5].values + dt, I1) * dias / 30).sum()
    print(f"+{dt} C      {p_:11.0f} {100 * (p_ / base_pm - 1):+5.0f}% {t1_:14.0f} {100 * (t1_ / th0 - 1):+5.0f}% "
          f"{t2_:14.0f} {100 * (t2_ / th0 - 1):+5.0f}%")
print("(Thornthwaite sem correcao de fotoperiodo; o que importa e a variacao relativa)")

# ===================================================================================== P5
sec("P5. Bezerra 2007: 'produtividade dos pomares de caju no Nordeste < 220 kg de castanha/ha' x PAM Ceara")
cj = pam[pam.produto == "Castanha de caju"].groupby("ano")[["producao_t", "area_colhida_ha"]].sum()
cj["kg_ha"] = cj.producao_t * 1000 / cj.area_colhida_ha
s = cj.loc[1990:2025, "kg_ha"]
print(f"PAM Ceara, castanha de caju (soma dos municipios): mediana 1990-2025 {s.median():.0f} kg/ha; "
      f"2000-2007 {cj.loc[2000:2007, 'kg_ha'].median():.0f}; 2016-2025 {cj.loc[2016:2025, 'kg_ha'].median():.0f}; "
      f"anos >= 220: {int((s >= 220).sum())} de {len(s)}")
print(cj.loc[[1995, 2000, 2005, 2010, 2012, 2015, 2020, 2024, 2025], "kg_ha"].round(0).to_string())
