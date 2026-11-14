"""Entomologo/politicas (v3), teste 3: a tabela de chuva da FUNCEME em Finan & Nelson 2001 contra o NASA POWER e o IMERG.

PRE-REGISTRO (escrito antes de rodar):
- Fonte: Finan & Nelson 2001, Climate Research 19:97-108 (doi 10.3354/cr019097), Tabela 2 (p. 100): chuva anual
  1974-1998 em 6 municipios da pesquisa (484 domicilios, 1998) e no estado; "Source: FUNCEME (unpubl data)".
  Transcrita do PDF local (artigos/2001_FINAN_...pdf) via pypdf; 'na' = sem dado.
- NASA: POWER PRECTOTCORR (0,5 grau; MERRA-2 corrigido) na celula mais proxima do centroide do municipio, 1981-1998;
  media do estado = derivados/power_ce_mensal.parquet (mascara IBGE). IMERG V07 municipal so em 1998 (1 ano).
- Metricas por municipio (1981-1998, n <= 18): Pearson r, Spearman, razao das medias (POWER/FUNCEME), e acerto dos
  anos secos (ano < 75% da media 1981-1998 da propria serie).
- Casos de politica citados no artigo: (i) 1997: previsao 'abaixo da media' lida como seca; "early in the season,
  rains arrived in some areas", e a FUNCEME perdeu credibilidade. (ii) 1998: "adequate rainfall had not arrived by
  St. Joseph's Day (March 19)". Medir com o POWER (estado) jan-mai/1997 e 1/jan-19/mar/1998 contra 1981-2010.
Somente le arquivos. Saida: v3_entomologo_finan_funceme_power.saida.txt
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import io
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

OUT = Path(__file__).with_suffix(".saida.txt")
LIN = []


def out(s=""):
    print(s)
    LIN.append(str(s))


TAB2 = """ano Limoeiro_do_Norte Barbalha Parambu Boa_Viagem Itarema Guaraciaba_do_Norte Ceara
1974 679 1461 na 1068 2362 1598 1579
1975 871 1235 na 992 1051 1605 1141
1976 532 681 na 411 938 973 793
1977 1060 930 na 833 1112 1373 1107
1978 914 1168 266 548 1196 933 854
1979 702 1390 475 460 441 1050 680
1980 824 920 555 350 347 785 785
1981 693 571 554 693 631 978 662
1982 602 564 487 593 969 867 707
1983 321 753 328 262 464 416 433
1984 1289 1092 923 911 1296 1536 1119
1985 1624 2148 2237 1371 2887 2602 1891
1986 1310 1139 1114 973 1861 1961 1317
1987 735 876 514 454 1041 1156 739
1988 849 1321 814 869 1700 1428 1161
1989 990 1567 1379 1122 968 1627 1266
1990 425 791 494 550 689 1000 627
1991 430 926 584 499 1281 1301 776
1992 592 973 428 679 693 1008 694
1993 286 744 490 184 616 484 420
1994 684 1063 1016 761 1714 1780 1167
1995 933 1059 767 751 1548 1462 1083
1996 760 1529 624 668 1491 1422 1067
1997 410 856 644 537 689 1259 709
1998 313 759 344 395 923 714 493"""
f = pd.read_csv(io.StringIO(TAB2), sep=" ", na_values="na").set_index("ano")
# conferencia da transcricao contra as linhas 'Avg.' do artigo (721 1153 532 704 1140 1273 946)
out("== 0. Conferencia da transcricao (medias 1974-1998 da Tabela 2; artigo: 721 1153 532 704 1140 1273 946) ==")
out("  " + " ".join(f"{v:.0f}" for v in f.mean().values))

mun = gpd.read_file(DADOS / "referencia" / "ceara_municipios.geojson")
nomes = pd.DataFrame(json.loads((DADOS / "referencia" / "ceara_municipios_nomes.json").read_text(encoding="utf-8")))
mun["codarea"] = mun.codarea.astype(int)
mun = mun.merge(nomes[["id", "nome"]], left_on="codarea", right_on="id")
cent = mun.to_crs(5880).centroid.to_crs(4326)
mun["lon"], mun["lat"] = cent.x, cent.y

d = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")
imerg = pd.read_parquet(DERIV / "ibge_ne_mun_imerg_mensal.parquet")
imerg["data"] = pd.to_datetime(imerg.data)

out("\n== A. Municipio a municipio, 1981-1998: FUNCEME (Tabela 2) x NASA POWER na celula mais proxima ==")
resumo = []
for col in f.columns[:-1]:
    nome = col.replace("_", " ")
    linha = mun[mun.nome.str.startswith(nome)]
    if len(linha) != 1:
        out(f"  {nome}: municipio nao encontrado de forma unica ({len(linha)})")
        continue
    lon, lat, cod = float(linha.lon.iloc[0]), float(linha.lat.iloc[0]), int(linha.codarea.iloc[0])
    c = d.sel(lon=lon, lat=lat, method="nearest")
    pwa = c.PRECTOTCORR.to_series().loc["1981":"1998"].groupby(lambda x: x.year).sum()
    fu = f.loc[1981:1998, col]
    ok = fu.notna()
    r, _ = stats.pearsonr(fu[ok], pwa[ok])
    rho, _ = stats.spearmanr(fu[ok], pwa[ok])
    seco_f = fu < 0.75 * fu.mean()
    seco_p = pwa < 0.75 * pwa.mean()
    acerto = int((seco_f & seco_p).sum())
    im98 = imerg[(imerg.cod_mun.astype(int) == cod) & (imerg.data.dt.year == 1998)].precip_mm.sum()
    resumo.append(r)
    out(f"  {nome:<20s} centroide ({lat:.2f}, {lon:.2f}) -> celula ({float(c.lat):.2f}, {float(c.lon):.2f}) | "
        f"r {r:+.2f} | rho {rho:+.2f} | POWER/FUNCEME {pwa[ok].mean() / fu[ok].mean():.2f} | anos secos FUNCEME "
        f"{int(seco_f.sum())}, POWER {int(seco_p.sum())}, em comum {acerto} | 1998: FUNCEME {fu.loc[1998]:.0f}, "
        f"POWER {pwa.loc[1998]:.0f}, IMERG {im98:.0f} mm")
out(f"  mediana do r nos 6 municipios: {np.median(resumo):+.2f}")

pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw = pw[pw.variavel == "PRECTOTCORR"].copy()
pw["data"] = pd.to_datetime(pw.data)
anual = pw.groupby(pw.data.dt.year).valor.sum()  # o valor ja e total mensal (conferido no teste 2)
fu = f.loc[1981:1998, "Ceara"]
r, _ = stats.pearsonr(fu, anual.loc[1981:1998])
out("\n== B. Estado do Ceara, 1981-1998: FUNCEME (Tabela 2) x POWER (media do estado) ==")
out(f"  r = {r:+.2f}; media FUNCEME {fu.mean():.0f} mm, POWER {anual.loc[1981:1998].mean():.0f} mm; "
    f"1983: {fu.loc[1983]:.0f} x {anual.loc[1983]:.0f}; 1985: {fu.loc[1985]:.0f} x {anual.loc[1985]:.0f}; "
    f"1997: {fu.loc[1997]:.0f} x {anual.loc[1997]:.0f}; 1998: {fu.loc[1998]:.0f} x {anual.loc[1998]:.0f}")

out("\n== C. 1997 (a previsao 'abaixo da media' que custou a credibilidade): POWER, media do estado ==")
mens = pw.set_index("data").valor
clim = mens.loc["1981":"2010"].groupby(mens.loc["1981":"2010"].index.month).median()
for m in range(1, 7):
    v = mens.loc[f"1997-{m:02d}"].iloc[0]
    out(f"  1997-{m:02d}: {v:6.1f} mm = {100 * v / clim[m]:5.0f}% da mediana 1981-2010 do mes ({clim[m]:.1f} mm)")
fm97 = mens.loc["1997-02":"1997-05"].sum()
fm_clim = mens.loc["1981":"2010"][mens.loc["1981":"2010"].index.month.isin([2, 3, 4, 5])]
fm_clim = fm_clim.groupby(fm_clim.index.year).sum()
out(f"  fev-mai/1997: {fm97:.0f} mm = {100 * fm97 / fm_clim.median():.0f}% da mediana; posto "
    f"{int((fm_clim < fm97).sum()) + 1} de {len(fm_clim)} (1 = mais seco)")
out(f"  ano 1997 na Tabela 2 (estado): {f.loc[1997, 'Ceara']:.0f} mm = {100 * f.loc[1997, 'Ceara'] / f['Ceara'].mean():.0f}% "
    f"da media 1974-1998 do artigo")

out("\n== D. 1998 e o dia de Sao Jose (19/mar): chuva acumulada 1/jan-19/mar, POWER media de celulas no CE ==")
mask = None
s = d.PRECTOTCORR.mean(["lat", "lon"]).to_series()
acc = {a: s.loc[f"{a}-01-01":f"{a}-03-19"].sum() for a in range(1981, 2026)}
acc = pd.Series(acc)
out(f"  1998: {acc[1998]:.0f} mm; mediana 1981-2010 {acc.loc[1981:2010].median():.0f} mm "
    f"({100 * acc[1998] / acc.loc[1981:2010].median():.0f}%); posto {int((acc < acc[1998]).sum()) + 1} de {len(acc)}")
out("  (media simples das 84 celulas do recorte retangular, nao so as do Ceara: serve para comparar anos)")

OUT.write_text("\n".join(LIN), encoding="utf-8")
