"""v3 Agroecologo - grupo 5 (sistemas de cultivo): checagens rapidas dos artigos com os dados NASA.

Blocos:
  A. Chuva dos ensaios (pluviometro/estacao citada no artigo) x IMERG V07 (0,1 grau) x POWER PRECTOTCORR (0,5 grau)
  B. ET0 FAO-56 da estacao INMET (Diniz 2017, Serra Talhada) x ET0 FAO-56 do POWER; ETP normal de Mossoro (Miranda 2020)
  C. Perez-Marin 2006: 2004 choveu mais que 2003 e o milho rendeu menos -> distribuicao mensal IMERG
  D. NASADEM 30 m: classes de declividade das regras de arranjo (Pinheiro & Nair 2018 / Araujo Filho)
  E. SMAP L4 na bacia do Jatoba (Pesqueira-PE, Montenegro 2019) x capacidade de campo/ponto de murcha do artigo
  F. PAM: o que o IBGE ve (e nao ve) das estrategias do grupo 5
  G. Coeficientes de agua do consorcio palma-sorgo (equacoes de Diniz 2017; WUE de Lima 2018b)
Numeros dos artigos: transcritos do PDF (ver comentario de cada bloco).
"""
import sys, json
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import xarray as xr

IM = DADOS / "imerg"
PW = DADOS / "power"

# ---------------------------------------------------------------- utilitarios
_im_cache = {}


def imerg_serie(lat, lon, ini, fim, viz=0):
    """Chuva diaria IMERG (NE, 0,1 grau) na celula mais proxima (viz=0) ou media 3x3 (viz=1)."""
    anos = range(pd.Timestamp(ini).year, pd.Timestamp(fim).year + 1)
    partes = []
    for a in anos:
        if a not in _im_cache:
            _im_cache[a] = xr.open_dataset(IM / f"imerg_ne_diario_{a}.nc")["precip"]
        da = _im_cache[a]
        i = int(np.abs(da.lat.values - lat).argmin())
        j = int(np.abs(da.lon.values - lon).argmin())
        sub = da.isel(lat=slice(i - viz, i + viz + 1), lon=slice(j - viz, j + viz + 1)).mean(("lat", "lon"))
        partes.append(sub.to_series())
    s = pd.concat(partes)
    return s.loc[ini:fim]


pw_ne = xr.open_dataset(PW / "power_ne_mensal.nc")


def power_mensal(lat, lon, var="PRECTOTCORR"):
    da = pw_ne[var].sel(lat=lat, lon=lon, method="nearest")
    s = da.to_series()
    if var == "PRECTOTCORR":  # mm/dia medio do mes -> mm/mes
        s = s * s.index.days_in_month
    return s


et0 = xr.open_dataset(PW / "power_ce_diario_et0.nc")["ET0"]


def et0_serie(lat, lon, ini, fim):
    return et0.sel(lat=lat, lon=lon, method="nearest").to_series().loc[ini:fim]


# centroides IBGE (malha do NE) para sitios sem coordenada confiavel no texto
loc = json.load(open(DADOS / "ibge_nordeste/localidades_municipios_ne.json", encoding="utf-8"))
malha = json.load(open(DADOS / "ibge_nordeste/malha_ne_municipio.geojson", encoding="utf-8"))
from shapely.geometry import shape


def centroide(nome, uf):
    cod = [m["id"] for m in loc if m["nome"] == nome and m["microrregiao"]["mesorregiao"]["UF"]["sigla"] == uf][0]
    f = [f for f in malha["features"] if f["properties"]["codarea"] == str(cod)][0]
    g = shape(f["geometry"])
    return cod, g


print("=" * 100)
print("A. CHUVA DO ENSAIO (texto do artigo) x IMERG V07 x POWER PRECTOTCORR")
print("=" * 100)
cod_esp, g_esp = centroide("Esperança", "PB")
cod_pes, g_pes = centroide("Pesqueira", "PE")
from shapely.geometry import Point
c_esp, c_pes = g_esp.centroid, g_pes.centroid
print(f"Esperança-PB (IBGE {cod_esp}) centroide {c_esp.y:.3f}, {c_esp.x:.3f}; "
      f"ponto do texto 7°19'S contém? {g_esp.contains(Point(c_esp.x, -7.3167))}; "
      f"lon do texto 33°51'O fica a {(-33.85 - g_esp.bounds[2]):.2f} grau a leste do limite leste do município (no mar)")
print(f"Pesqueira-PE (IBGE {cod_pes}) centroide {c_pes.y:.3f}, {c_pes.x:.3f} (bacia do Jatobá; sem coordenada no texto)")

SITIOS = {
    # nome: (lat, lon, fonte da coordenada)
    "Serra Talhada-PE (IPA)": (-(7 + 59 / 60), -(38 + 15 / 60), "Diniz 2017 / Lima 2018: 7°59'S 38°15'O"),
    "Pentecoste-CE": (-3.75, -39.25, "Neves 2015: 3°45'S 39°15'O"),
    "Taperoá-PB (Vila Maria Rita)": (-(7 + 12 / 60 + 23 / 3600), -(36 + 49 / 60 + 25 / 3600), "Martins 2015 / Sousa 2012"),
    "Esperança-PB (CASM)": (round(c_esp.y, 3), round(c_esp.x, 3), "centroide IBGE (lon do texto errada)"),
    "Pesqueira-PE (Jatobá)": (round(c_pes.y, 3), round(c_pes.x, 3), "centroide IBGE"),
}

linhas = []


def comparar(sitio, rotulo, ini, fim, relatado):
    lat, lon, _ = SITIOS[sitio]
    s0 = imerg_serie(lat, lon, ini, fim, 0).sum()
    s1 = imerg_serie(lat, lon, ini, fim, 1).sum()
    linhas.append(dict(sitio=sitio, periodo=rotulo, relatado_mm=relatado, imerg_cel=round(float(s0), 1),
                       imerg_3x3=round(float(s1), 1), razao_imerg=round(float(s0) / relatado, 2) if relatado else np.nan))


# Diniz 2017 Tabela 1 (pluviometro no ensaio): nov/2014 (15 d) .. nov/2015 (9 d) = 354,7 mm
comparar("Serra Talhada-PE (IPA)", "16/nov/2014-09/nov/2015 (Diniz T1)", "2014-11-16", "2015-11-09", 354.7)
# Lima 2018a/b: 380 dias jun/2012-jun/2013, chuva 393 mm
comparar("Serra Talhada-PE (IPA)", "01/jun/2012-15/jun/2013 (Lima, 380 d)", "2012-06-01", "2013-06-15", 393.0)
# Neves 2015: mar-jun/2012 = 30,4 + 86,8 + 15,6 + 0
comparar("Pentecoste-CE", "mar-jun/2012 (Neves)", "2012-03-01", "2012-06-30", 30.4 + 86.8 + 15.6 + 0)
# Perez-Marin 2006: totais anuais 2003 = 653 e 2004 = 1.000 mm
comparar("Esperança-PB (CASM)", "2003 (Pérez-Marin)", "2003-01-01", "2003-12-31", 653)
comparar("Esperança-PB (CASM)", "2004 (Pérez-Marin)", "2004-01-01", "2004-12-31", 1000)
# Martins 2015: 987, 533, 725, 756 mm (2006-2009)
for a, v in zip(range(2006, 2010), [987, 533, 725, 756]):
    comparar("Taperoá-PB (Vila Maria Rita)", f"{a} (Martins)", f"{a}-01-01", f"{a}-12-31", v)
# Montenegro 2019: 593, 651, 628 mm (2016-2018)
for a, v in zip(range(2016, 2019), [593, 651, 628]):
    comparar("Pesqueira-PE (Jatobá)", f"{a} (Montenegro)", f"{a}-01-01", f"{a}-12-31", v)

tab = pd.DataFrame(linhas)
# POWER PRECTOTCORR anual / periodo (mensal 0,5 grau)
pw_vals = []
for _, r in tab.iterrows():
    lat, lon, _ = SITIOS[r.sitio]
    s = power_mensal(lat, lon)
    if "Diniz" in r.periodo:
        v = s.loc["2014-12":"2015-10"].sum() + s.loc["2014-11"].sum() * 15 / 30 + s.loc["2015-11"].sum() * 9 / 30
    elif "Lima" in r.periodo:
        v = s.loc["2012-06":"2013-05"].sum() + s.loc["2013-06"].sum() * 15 / 30
    elif "Neves" in r.periodo:
        v = s.loc["2012-03":"2012-06"].sum()
    else:
        a = int(r.periodo[:4])
        v = s.loc[str(a)].sum()
    pw_vals.append(round(float(v), 1))
tab["power_prectotcorr"] = pw_vals
tab["razao_power"] = (tab.power_prectotcorr / tab.relatado_mm).round(2)
print(tab.to_string(index=False))
rz = tab.razao_imerg.dropna()
print(f"\nIMERG/relatado: mediana {rz.median():.2f}, min {rz.min():.2f}, max {rz.max():.2f}, n={len(rz)}")
print(f"POWER/relatado: mediana {tab.razao_power.median():.2f}, min {tab.razao_power.min():.2f}, max {tab.razao_power.max():.2f}")
print(f"Erro absoluto medio relativo: IMERG {np.mean(np.abs(tab.razao_imerg - 1)):.2f}; POWER {np.mean(np.abs(tab.razao_power - 1)):.2f}")
# ordem entre anos no mesmo sitio (o que o motor usa: o ano bom x o ano ruim)
for sit in ["Taperoá-PB (Vila Maria Rita)", "Pesqueira-PE (Jatobá)", "Esperança-PB (CASM)"]:
    t = tab[tab.sitio == sit]
    from scipy.stats import spearmanr
    if len(t) >= 3:
        rho = spearmanr(t.relatado_mm, t.imerg_cel).correlation
        print(f"  {sit}: ordem dos anos relatado x IMERG (Spearman) = {rho:.2f}; relatado {t.relatado_mm.tolist()} IMERG {t.imerg_cel.tolist()}")
    else:
        print(f"  {sit}: relatado {t.relatado_mm.tolist()} IMERG {t.imerg_cel.tolist()} (mesmo sinal: "
              f"{np.sign(np.diff(t.relatado_mm.values))[0] == np.sign(np.diff(t.imerg_cel.values))[0]})")

# Diniz Tabela 1 mes a mes (chuva e ET0) - mes parcial nas pontas
print("\nDiniz 2017 Tabela 1, mes a mes (Serra Talhada): chuva do pluviometro x IMERG; ET0 INMET (FAO-56) x ET0 POWER (FAO-56)")
T1 = [("2014-11-16", "2014-11-30", 91.1, 172), ("2014-12-01", "2014-12-31", 11.4, 171), ("2015-01-01", "2015-01-31", 45.0, 177),
      ("2015-02-01", "2015-02-28", 63.6, 150), ("2015-03-01", "2015-03-31", 67.0, 156), ("2015-04-01", "2015-04-30", 20.6, 146),
      ("2015-05-01", "2015-05-31", 5.6, 139), ("2015-06-01", "2015-06-30", 47.6, 110), ("2015-07-01", "2015-07-31", 2.8, 116),
      ("2015-08-01", "2015-08-31", 0.0, 157), ("2015-09-01", "2015-09-30", 0.0, 178), ("2015-10-01", "2015-10-31", 0.0, 199),
      ("2015-11-01", "2015-11-09", 0.0, 201)]
lat, lon, _ = SITIOS["Serra Talhada-PE (IPA)"]
rows = []
for ini, fim, p, e in T1:
    rows.append(dict(mes=ini[:7], chuva_ensaio=p, imerg=round(float(imerg_serie(lat, lon, ini, fim).sum()), 1),
                     et0_inmet=e, et0_power=round(float(et0_serie(lat, lon, ini, fim).sum()), 1)))
m = pd.DataFrame(rows)
print(m.to_string(index=False))
print(f"Somas: chuva ensaio {m.chuva_ensaio.sum():.1f} | IMERG {m.imerg.sum():.1f} | ET0 INMET {m.et0_inmet.sum():.0f} | ET0 POWER {m.et0_power.sum():.0f}")
print(f"r mensal chuva (ensaio x IMERG) = {np.corrcoef(m.chuva_ensaio, m.imerg)[0,1]:.2f}; "
      f"r mensal ET0 (INMET x POWER) = {np.corrcoef(m.et0_inmet, m.et0_power)[0,1]:.2f}")
print("  ATENÇÃO: nov/2014 (15 d) e nov/2015 (9 d) têm ET0 de 172 e 201 mm na tabela: são valores de mês inteiro, não dos dias do ensaio "
      "(a soma 2.072 inclui isso). Comparação justa = meses inteiros dez/2014-out/2015:")
mi = m.iloc[1:-1]
print(f"  dez/2014-out/2015: ET0 INMET {mi.et0_inmet.sum():.0f} x POWER {mi.et0_power.sum():.0f} mm "
      f"(razão {mi.et0_power.sum()/mi.et0_inmet.sum():.2f}); chuva ensaio {mi.chuva_ensaio.sum():.1f} x IMERG {mi.imerg.sum():.1f}")
print(f"  r mensal só meses inteiros: ET0 {np.corrcoef(mi.et0_inmet, mi.et0_power)[0,1]:.2f}; chuva {np.corrcoef(mi.chuva_ensaio, mi.imerg)[0,1]:.2f}; "
      f"meses com POWER > INMET: {int((mi.et0_power > mi.et0_inmet).sum())}/{len(mi)}; diferença média {np.mean(mi.et0_power - mi.et0_inmet):.0f} mm/mês")
print("  Registro anterior do conselho: POWER ~13-16% acima do ERA5 (viés quente da Tmax). Contra estação FAO-56 a diferença é maior.")

print("\n" + "=" * 100)
print("B. ETP normal de Mossoró (Miranda 2020, Tabela 1, fonte INMET) x ET0 FAO-56 do POWER, média 1991-2020")
print("=" * 100)
mos = et0.sel(lat=-(5 + 12 / 60), lon=-(37 + 24 / 60), method="nearest").to_series().loc["1991":"2020"]
mm = mos.groupby([mos.index.year, mos.index.month]).sum().groupby(level=1).mean()
nor = {8: 186.1, 9: 202.2, 10: 223.7, 11: 218.2, 12: 234.7}
for k, v in nor.items():
    print(f"  mês {k:2d}: normal INMET {v:6.1f} | POWER ET0 {mm[k]:6.1f} | razão {mm[k]/v:.2f}")
print(f"  soma ago-dez: INMET {sum(nor.values()):.0f} x POWER {sum(mm[k] for k in nor):.0f}")
im_mos = pd.concat([imerg_serie(-(5 + 12 / 60), -(37 + 24 / 60), f"{a}-01-01", f"{a}-12-31") for a in range(1998, 2026)])
imm = im_mos.groupby([im_mos.index.year, im_mos.index.month]).sum().groupby(level=1).mean()
print("  Chuva ago-dez normal INMET (7,2; 1,8; 2,4; 1,7; 14,3) x IMERG 1998-2025: " + "; ".join(f"{imm[k]:.1f}" for k in nor))
print(f"  -> crotalária na seca (ago-out) só com água azul: o ensaio aplicou 270-330 mm; a ETP ago-out normal soma {186.1+202.2+223.7:.0f} mm")

print("\n" + "=" * 100)
print("C. Pérez-Marin 2006: 2004 (1.000 mm) rendeu 34-69% menos milho que 2003 (653 mm). Distribuição mensal IMERG em Esperança-PB")
print("=" * 100)
lat, lon, _ = SITIOS["Esperança-PB (CASM)"]
for a in (2003, 2004):
    s = imerg_serie(lat, lon, f"{a}-01-01", f"{a}-12-31")
    ms = s.groupby(s.index.month).sum()
    jf = ms.loc[[1, 2]].sum(); est = ms.loc[3:8].sum()
    print(f"  {a}: total {ms.sum():6.0f} | jan-fev {jf:5.0f} ({jf/ms.sum():.0%}) | mar-ago (estação de cultivo do artigo) {est:5.0f} | "
          f"meses: " + " ".join(f"{int(v)}" for v in ms.values))
print("  (o artigo diz que a estação chuvosa local é mar-ago e o milho foi semeado nela)")

print("\n" + "=" * 100)
print("D. NASADEM 30 m nas AOIs: classes de declividade das regras de arranjo (Pinheiro & Nair 2018, citando Araújo Filho 2013):")
print("   savana/bosquetes < 10%; aleias (faixas) 10-25%; sem raleamento > 25%")
print("=" * 100)
import rasterio
from rasterio.windows import from_bounds
with rasterio.open(DADOS / "srtm/nasadem_ceara_30m.tif") as src:
    for nome in AOIS:
        b = bbox_aoi(nome)
        w = from_bounds(*b, transform=src.transform)
        z = src.read(1, window=w).astype("float64")
        z[z == src.nodata] = np.nan
        latc = (b[1] + b[3]) / 2
        dy = 30.87 * src.res[1] / (1 / 3600) / 1.0  # ~30,87 m por arco-segundo em lat
        dx = dy * np.cos(np.radians(latc))
        gy, gx = np.gradient(z, dy, dx)
        dec = np.hypot(gx, gy) * 100  # %
        v = dec[np.isfinite(dec)]
        print(f"  {nome:16s}: n={v.size:,} | <3% {np.mean(v<3):.0%} | 3-10% {np.mean((v>=3)&(v<10)):.0%} | "
              f"10-25% (aleia em nível) {np.mean((v>=10)&(v<=25)):.1%} | >25% {np.mean(v>25):.1%} | mediana {np.median(v):.1f}%")

print("\n" + "=" * 100)
print("E. SMAP L4 (9 km) na bacia do Jatobá/Pesqueira x CC 0,16 / PMP 0,05 / porosidade 0,40 (Montenegro 2019)")
print("=" * 100)
sm = xr.open_dataset(DADOS / "smap/smap_l4_diario_ne.nc")
lat, lon, _ = SITIOS["Pesqueira-PE (Jatobá)"]
p = sm[["sm_surface", "sm_rootzone"]].sel(lat=lat, lon=lon, method="nearest").sel(time=slice("2016-01-01", "2018-12-31")).to_dataframe()
for v in ["sm_surface", "sm_rootzone"]:
    x = p[v].dropna()
    print(f"  {v:11s}: n={len(x)} | p5 {x.quantile(.05):.3f} p50 {x.median():.3f} p95 {x.quantile(.95):.3f} max {x.max():.3f} | "
          f"dias > CC 0,16: {np.mean(x>0.16):.0%} | dias < PMP 0,05: {np.mean(x<0.05):.0%}")
for a in (2016, 2017, 2018):
    x = p.loc[str(a), "sm_rootzone"]
    s = imerg_serie(lat, lon, f"{a}-01-01", f"{a}-12-31")
    print(f"  {a}: raiz média {x.mean():.3f}, máx {x.max():.3f} | IMERG {s.sum():.0f} mm | relatado {dict(zip((2016,2017,2018),(593,651,628)))[a]} mm")
print("  Parcela do artigo = 4,5 x 11 m; pixel SMAP L4 = 9 km: a diferença entre solo nu, palma em nível, cobertura morta e caatinga "
      "fica abaixo da resolução. SMAP só dá o estado de fundo.")

print("\n" + "=" * 100)
print("F. PAM (IBGE, municípios do CE): o que existe para validar as estratégias do grupo 5")
print("=" * 100)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
alvo = ["Feijão (em grão)", "Milho (em grão)", "Mandioca", "Sorgo (em grão)", "Girassol (em grão)", "Algodão herbáceo (em caroço)",
        "Gergelim", "Mamona (baga)", "Fava (em grão)", "Amendoim (em casca)", "Cana para forragem"]
q = pam[pam.produto.isin(alvo) & (pam.ano >= 2015)]
r = q[q.area_colhida_ha > 0].groupby(["produto"]).agg(mun_ano=("cod_local", "size"), municipios=("cod_local", "nunique"),
                                                         area_med_ha=("area_colhida_ha", "median"))
print(r.sort_values("mun_ano", ascending=False).to_string())
print("  Ausentes do PAM (não existem como produto): palma forrageira, guandu, gliricídia, leucena, crotalária, mucuna, consórcio.")
pe = pam[pam.local.str.startswith("Pentecoste") & pam.produto.isin(["Feijão (em grão)", "Milho (em grão)"]) & pam.ano.between(2010, 2013)]
print("  Pentecoste (ensaio de Neves, girassol mar-jun/2012):")
print(pe.pivot_table(index="ano", columns="produto", values="rendimento_kg_ha").to_string())

print("\n" + "=" * 100)
print("G. Coeficientes de água do consórcio palma-sorgo (equações do próprio artigo)")
print("=" * 100)
print("  Fig. 2B de Diniz (sorgo, solteiro e consorciado juntos) traz 'DM = 12,473 WD' impresso SEM intercepto: daria "
      f"{12.473*355:.0f} kg em 355 mm, mas o ponto da figura está em ~6.400 (conferido na imagem da p. 729). Equação não usada.")
for wd in (355, 563, 725, 867, 1012):
    cons = -0.0064 * wd ** 2 + 17.2674 * wd + 1642.5849   # Diniz Fig. 3B: consórcio palma-sorgo (bate com os pontos da figura)
    print(f"  água total {wd:5d} mm: consórcio {cons:7.0f} kg MS/ha (Fig. 3B) | palma solteira 4.627 (média; lâmina sem efeito) | "
          f"razão {cons/4627:.2f}")
mc = np.mean([-0.0064 * w ** 2 + 17.2674 * w + 1642.5849 for w in (355, 563, 725, 867, 1012)])
print(f"  Média da curva da Fig. 3B nas 5 lâminas = {mc:.0f} kg MS/ha x Tabela 2 'consórcio' = 12.130 (3.573 palma + 8.557 sorgo): "
      "o artigo não fecha Tabela e Figura (~18% de diferença)")
print("  Médias da Tabela 2 (todas as lâminas): palma solteira 4.627 | sorgo solteiro 14.073 | consórcio 12.130 kg MS/ha;"
      " IPS 6.279 = sorgo convertido em 'equivalente palma' (não é biomassa)")
print(f"  Diniz: 6.279/4.627 = {6279.02/4626.98:.2f}x ; consórcio/sorgo solteiro (biomassa real) = {12130/14073:.2f}x ; consórcio/palma = {12130/4627:.2f}x")
print("  Lima 2018b (mesmo grupo, outro ano): ET/ET0 = 0,50 com ou sem sorgo; WUE consórcio 18,9 x palma solteira 8,4 kg MS/ha/mm de ET")
lat, lon = AOIS["sertao_central"][1], AOIS["sertao_central"][0]
e = et0_serie(lat, lon, "1998-01-01", "2025-12-31")
ea = e.groupby(e.index.year).sum()
pa = pd.Series({a: imerg_serie(lat, lon, f"{a}-01-01", f"{a}-12-31").sum() for a in range(1998, 2026)})
print("  ATENÇÃO para o M1: o Kc 0,50 de Lima 2018b foi medido contra ET0 da estação INMET (300 m). Com ET0 do POWER sem correção "
      "(bloco A: +32% em Serra Talhada) a demanda da palma sai inflada na mesma proporção.")
print(f"  Quixadá (AOI Sertão Central) 1998-2025: ET0 POWER anual mediana {ea.median():.0f} mm -> demanda da palma (0,50 ET0) "
      f"{0.5*ea.median():.0f} mm; IMERG anual mediana {pa.median():.0f} mm; anos com chuva >= 355 mm (lâmina que bastou à palma em Diniz): "
      f"{int((pa>=355).sum())}/{len(pa)}")

print("\n" + "=" * 100)
print("H. Landsat C2 L2 30 m (NASA/USGS), AOI Sertão Central: cobertura no fim da seca (out-dez) x chuva da quadra (IMERG fev-mai)")
print("   Pergunta: o NDVI vê a entressafra coberta? (Montenegro: solo nu escoa mais; Pinheiro: deixar 40% da forragem secar como cobertura)")
print("=" * 100)
ls = xr.open_dataset(DADOS / "landsat/landsat_aoi_sertao_central.nc")
t = pd.to_datetime(ls.time.values)
lat, lon = AOIS["sertao_central"][1], AOIS["sertao_central"][0]
res = []
for a in range(2013, 2026):
    sel = np.where((t.year == a) & (t.month >= 10))[0]
    if len(sel) == 0:
        continue
    nd = ls["ndvi"].isel(time=sel).values
    med = np.nanmedian(nd, axis=0)
    v = med[np.isfinite(med)]
    if v.size < 1000:
        continue
    q = imerg_serie(lat, lon, f"{a}-02-01", f"{a}-05-31").sum()
    res.append(dict(ano=a, cenas=len(sel), frac_valida=round(v.size / med.size, 2), ndvi_mediana=round(float(np.median(v)), 3),
                    frac_ndvi_lt020=round(float(np.mean(v < 0.20)), 3), frac_ndvi_gt040=round(float(np.mean(v > 0.40)), 3),
                    quadra_imerg_mm=round(float(q))))
h = pd.DataFrame(res)
print(h.to_string(index=False))
from scipy.stats import spearmanr
for c in ["ndvi_mediana", "frac_ndvi_lt020", "frac_ndvi_gt040"]:
    print(f"  Spearman quadra x {c}: {spearmanr(h.quadra_imerg_mm, h[c]).correlation:+.2f} (n={len(h)})")
print("  Limites: o cubo Landsat guardado tem red, nir08, swir16; sem swir22 não há NDTI (índice de palhada). NDVI baixo = solo nu OU palhada seca:"
      " não separa as duas. Faixa de gliricídia (1 m a cada 6 m) é subpixel; gliricídia é caducifólia na seca (Pérez-Marin).")
