"""v3 - Especialista Cerrado/MATOPIBA: checagens dos itens 6-9 do texto recebido.

So leitura de dados ja em disco (nada e gravado em dados/). Saida: .saida.txt ao lado.
Blocos:
  A. IBGE PAM por UF: confere os numeros de area/rendimento citados por Pacheco 2013 e 2017
     (eles citam CONAB; aqui e IBGE, entao a comparacao e de ordem de grandeza) e mede o peso
     do MATOPIBA nordestino (MA, PI, BA) contra o Ceara.
  B. IMERG (NASA, via POWER) em Bom Jesus-PI: chuva nas safras 2010/11 e 2011/12 do experimento
     Pacheco; janela pos-colheita (16/abr-15/mai) contra janela da sobressemeadura (15/mar-14/abr);
     climatologia 1998-2025 da mesma comparacao em 4 pontos do MATOPIBA.
  C. POWER GWETROOT e T2M_MAX mensais em Bom Jesus (entressafra 2011).
  D. SMAP L4 (2015-2025) zona da raiz nos mesmos pontos: queda entre 15/mar e 15/mai.
  E. IMERG contra a chuva medida no campo da Embrapa (Lagoa Seca-PB, Documentos 266):
     389 mm (2015) e 184 mm (2016) "entre o plantio e a colheita" (colheita nao informada).
  F. IMERG em Juazeiro-BA (Pimentel et al. 2011): chuva ago/2006-ago/2007 e normal nov-mar.
Limiar pre-declarado (descritivo, escolhido antes de rodar): janela de 30 dias com < 50 mm = "seca
para estabelecer cobertura semeada a lanco".
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import json
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

SAIDA = Path(__file__).with_suffix(".saida.txt")
_f = open(SAIDA, "w", encoding="utf-8")


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s.encode("ascii", "replace").decode())
    _f.write(s + "\n")


def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


# ---------------------------------------------------------------- pontos (centroide IBGE)
loc = json.load(open(DADOS / "ibge_nordeste/localidades_municipios_ne.json", encoding="utf-8"))
malha = json.load(open(DADOS / "ibge_nordeste/malha_ne_municipio.geojson", encoding="utf-8"))
nome_uf = {m["id"]: (m["nome"], m["microrregiao"]["mesorregiao"]["UF"]["sigla"],
                     m["microrregiao"]["mesorregiao"]["nome"]) for m in loc}


def centroide(geom):
    pts = []
    def rec(c):
        if isinstance(c[0], (int, float)):
            pts.append(c)
        else:
            for x in c:
                rec(x)
    rec(geom["coordinates"])
    a = np.array(pts)
    return float(a[:, 0].mean()), float(a[:, 1].mean())


cent = {}
for ft in malha["features"]:
    cod = int(ft["properties"]["codarea"])
    if cod in nome_uf:
        n, uf, meso = nome_uf[cod]
        cent[(norm(n), uf)] = centroide(ft["geometry"]) + (meso,)

PONTOS = {}
for nome, uf in [("Bom Jesus", "PI"), ("Urucui", "PI"), ("Balsas", "MA"),
                 ("Luis Eduardo Magalhaes", "BA"), ("Lagoa Seca", "PB"), ("Juazeiro", "BA"),
                 ("Quixada", "CE")]:
    lon, lat, meso = cent[(norm(nome), uf)]
    PONTOS[f"{nome}-{uf}"] = (lon, lat, meso)
# coordenadas declaradas nos artigos (9 16'78" e invalido: 78 segundos; lido como 9,28 S)
PONTOS["Bom Jesus exp. Pacheco"] = (-(44 + 44 / 60 + 25 / 3600), -9.28, "texto do artigo")
PONTOS["Juazeiro exp. Pimentel"] = (-(40 + 29 / 60), -(9 + 25 / 60), "texto do artigo (diz 'east')")
p("== Pontos (lon, lat, mesorregiao IBGE) ==")
for k, v in PONTOS.items():
    p(f"  {k:28s} {v[0]:8.3f} {v[1]:7.3f}  {v[2]}")
MATOPIBA = ["Bom Jesus-PI", "Urucui-PI", "Balsas-MA", "Luis Eduardo Magalhaes-BA"]

# ---------------------------------------------------------------- A. IBGE PAM por UF
p("\n== A. IBGE PAM (pam_ne_estados.parquet) ==")
pam = pd.read_parquet(DADOS / "ibge_pam/pam_ne_estados.parquet")
pam["prod_n"] = pam["produto"].map(norm)
pam["var_n"] = pam["variavel"].map(norm)
UF = {"21": "MA", "22": "PI", "23": "CE", "29": "BA", "25": "PB", "26": "PE"}


def serie(uf, prod_prefix, var_prefix):
    m = (pam.cod_local.astype(str) == uf) & pam.prod_n.str.startswith(prod_prefix) & pam.var_n.str.startswith(var_prefix)
    return pam[m].set_index("ano")["valor"].sort_index()


p("Piaui, area plantada (mil ha) - Pacheco 2013 cita Conab 2011/12: soja 438,8; milho 357,3; arroz 141,9")
for prod, nm in [("soja", "soja"), ("milho (em", "milho"), ("arroz", "arroz")]:
    s = serie("22", prod, "area plantada")
    p(f"  {nm:6s}", "  ".join(f"{a}: {s.get(a, np.nan)/1000:6.1f}" for a in range(2010, 2015)))
p("Piaui, rendimento (kg/ha) - Pacheco 2017 cita Conab 2013/14: soja 2.990 (+78,2%), arroz 1.907 (+125,3%), milho 3.189 ('reducao de 138,5%')")
for prod, nm in [("soja", "soja"), ("milho (em", "milho"), ("arroz", "arroz")]:
    s = serie("22", prod, "rendimento")
    txt = "  ".join(f"{a}: {s.get(a, np.nan):6.0f}" for a in range(2011, 2016))
    v13, v14 = s.get(2013, np.nan), s.get(2014, np.nan)
    p(f"  {nm:6s} {txt}   var 2014/2013 = {100*(v14/v13-1):+.1f}%")
p("  Nota: uma reducao percentual nao pode passar de 100%; '138,5%' so faz sentido como (anterior/atual - 1),"
  " i.e. o ano anterior foi 2,385x o atual.")

p("\nSoja: area plantada (mil ha) por UF")
for uf in ["21", "22", "29", "23"]:
    s = serie(uf, "soja", "area plantada")
    p(f"  {UF[uf]}", "  ".join(f"{a}: {s.get(a, np.nan)/1000:7.1f}" for a in [2000, 2010, 2015, 2020, 2024, 2025]))
p("Milho em grao: rendimento medio 2016-2025 (kg/ha) e CV entre anos")
for uf in ["21", "22", "29", "23", "25"]:
    s = serie(uf, "milho (em", "rendimento").loc[2016:2025]
    p(f"  {UF[uf]}  media {s.mean():6.0f}  min {s.min():6.0f}  max {s.max():6.0f}  CV {100*s.std()/s.mean():5.1f}%")
tot = {}
for uf in ["21", "22", "29", "23"]:
    tot[UF[uf]] = sum(serie(uf, pr, "quantidade produzida").get(2024, 0) for pr in ["soja", "milho (em", "algodao herbaceo"])
p("Producao 2024 soja+milho+algodao herbaceo (mil t):", {k: round(v / 1000, 1) for k, v in tot.items()})
gg = pam[pam.prod_n.str.startswith("gergelim") & pam.var_n.str.startswith("area colhida")]
gg = gg.pivot_table(index="ano", columns="cod_local", values="valor", aggfunc="sum").fillna(0)
nz = gg[(gg > 0).any(axis=1)]
p("Gergelim, area colhida (ha) nos anos com algum valor > 0 nas UFs do NE:",
  {int(a): {UF.get(str(c), str(c)): int(v) for c, v in r.items() if v > 0} for a, r in nz.iterrows()})

# ---------------------------------------------------------------- B. IMERG
p("\n== B. IMERG diario 0,1 grau (NASA, via POWER) ==")
anos = range(1998, 2026)
series = {k: [] for k in PONTOS}
for a in anos:
    ds = xr.open_dataset(DADOS / f"imerg/imerg_ne_diario_{a}.nc")
    for k, (lon, lat, _) in PONTOS.items():
        series[k].append(ds["precip"].sel(lon=lon, lat=lat, method="nearest").to_series())
    ds.close()
chuva = {k: pd.concat(v).sort_index() for k, v in series.items()}


def soma(k, ini, fim):
    s = chuva[k].loc[ini:fim]
    return float(s.sum()), len(s)


k = "Bom Jesus exp. Pacheco"
m = chuva[k].loc["2010-10-01":"2012-04-30"].resample("MS").sum()
p("Bom Jesus (ponto do artigo) chuva mensal IMERG out/2010-abr/2012 (mm):")
p("  " + "  ".join(f"{d:%b%y}:{v:.0f}" for d, v in m.items()))
for ini, fim, rot in [("2010-11-01", "2011-04-30", "safra 2010/11 nov-abr"),
                      ("2011-11-01", "2012-04-30", "safra 2011/12 nov-abr"),
                      ("2011-04-16", "2011-10-31", "entressafra 16/abr-31/out/2011"),
                      ("2011-04-16", "2011-05-15", "30 d apos colheita 16/abr/2011 (S2 milheto falhou)"),
                      ("2011-03-15", "2011-04-14", "30 d antes da colheita (~janela R5.5)"),
                      ("2011-11-22", "2011-12-21", "30 d apos dessecacao 22/nov/2011 (decomposicao)")]:
    v, n = soma(k, ini, fim)
    p(f"  {rot:52s} {v:6.0f} mm ({n} d)")

p("\nClimatologia 1998-2025: 30 d antes (15/mar-14/abr) x 30 d depois (16/abr-15/mai) da colheita;"
  " limiar pre-declarado 50 mm")
for k in MATOPIBA + ["Quixada-CE"]:
    pre, pos = [], []
    for a in anos:
        pre.append(soma(k, f"{a}-03-15", f"{a}-04-14")[0])
        pos.append(soma(k, f"{a}-04-16", f"{a}-05-15")[0])
    pre, pos = np.array(pre), np.array(pos)
    p(f"  {k:28s} pre: mediana {np.median(pre):5.0f} mm, anos<50 mm {np.mean(pre<50)*100:4.0f}% | "
      f"pos: mediana {np.median(pos):5.0f} mm, anos<50 mm {np.mean(pos<50)*100:4.0f}% | 2011 pos={pos[2011-1998]:.0f}")

p("\nChuva nov-abr por safra (IMERG, mm) - para cruzar com o IBGE (2013 = safra 2012/13 ruim no PI)")
for k in MATOPIBA:
    p(f"  {k:28s} " + "  ".join(f"{a}/{(a+1)%100:02d}:{soma(k, f'{a}-11-01', f'{a+1}-04-30')[0]:.0f}" for a in range(2009, 2015)))

p("\nClimatologia 1998-2025: chuva nos 30 d apos 22/nov (decomposicao) e total nov-abr")
for k in MATOPIBA + ["Quixada-CE"]:
    d30 = np.array([soma(k, f"{a}-11-22", f"{a}-12-21")[0] for a in range(1998, 2025)])
    sf = np.array([soma(k, f"{a}-11-01", f"{a+1}-04-30")[0] for a in range(1998, 2025)])
    p(f"  {k:28s} 30d pos-22/nov mediana {np.median(d30):5.0f} (p10 {np.percentile(d30,10):4.0f}, p90 {np.percentile(d30,90):4.0f}) | "
      f"nov-abr mediana {np.median(sf):5.0f} (p10 {np.percentile(sf,10):4.0f}) mm")

# ---------------------------------------------------------------- C. POWER mensal
p("\n== C. POWER mensal 0,5 grau em Bom Jesus (GWETROOT, T2M_MAX, PRECTOTCORR) ==")
pw = xr.open_dataset(DADOS / "power/power_ne_mensal.nc")
lon, lat, _ = PONTOS["Bom Jesus exp. Pacheco"]
# a grade lon do arquivo mistura 0,5 e 0,625 grau e ~1/3 das celulas e NaN: usar so colunas validas
valid_lon = [x for x in pw.lon.values if np.isfinite(pw["T2M"].isel(time=0).sel(lon=x).values).any()]
pw = pw.sel(lon=valid_lon)
valid_lat = [y for y in pw.lat.values if np.isfinite(pw["T2M"].isel(time=0).sel(lat=y).values).any()]
pw = pw.sel(lat=valid_lat)
q = pw.sel(lon=lon, lat=lat, method="nearest")
g = q["GWETROOT"].to_series(); tx = q["T2M_MAX"].to_series(); pr = q["PRECTOTCORR"].to_series()
p(f"  celula POWER: lon {float(q.lon):.2f} lat {float(q.lat):.2f}")
p("  2011 GWETROOT: " + "  ".join(f"{d:%b}:{v:.2f}" for d, v in g.loc["2011-03":"2011-12"].items()))
clim = g.groupby(g.index.month).mean()
p("  clim 1981-2025: " + "  ".join(f"{mm}:{clim[mm]:.2f}" for mm in range(3, 13)))
p("  2011 T2M_MAX (C): " + "  ".join(f"{d:%b}:{v:.1f}" for d, v in tx.loc["2011-03":"2011-12"].items()))
txc = tx.groupby(tx.index.month).mean()
p("  T2M_MAX clim 1981-2025: " + "  ".join(f"{mm}:{txc[mm]:.1f}" for mm in range(3, 13)))
pw.close()
gn = xr.open_dataset(DADOS / "gldas/gldas_noah025_mensal_ne.nc")
z = gn["SoilMoi0_10cm_inst"].sel(lon=lon, lat=lat, method="nearest").to_series()
zc = z.groupby(z.index.month).mean()
p("  GLDAS Noah 0-10 cm (kg/m2) 2011: " + "  ".join(f"{d:%b}:{v:.1f}" for d, v in z.loc["2011-03":"2011-11"].items()))
p("  GLDAS Noah 0-10 cm clim 2000-2026: " + "  ".join(f"{mm}:{zc[mm]:.1f}" for mm in range(3, 12)))

# ---------------------------------------------------------------- D. SMAP L4
p("\n== D. SMAP L4 zona da raiz (m3/m3) e percentil, media de 7 d terminando em 15/mar, 15/abr, 15/mai ==")
sm = xr.open_dataset(DADOS / "smap/smap_l4_diario_ne.nc")
for k in MATOPIBA + ["Quixada-CE"]:
    lon, lat, _ = PONTOS[k]
    z = sm[["sm_rootzone", "sm_rootzone_pctl"]].sel(lon=lon, lat=lat, method="nearest").load().to_dataframe()
    linhas = []
    for a in range(2016, 2026):
        r = []
        for md in ["03-15", "04-15", "05-15"]:
            fim = pd.Timestamp(f"{a}-{md}")
            w = z.loc[fim - pd.Timedelta(days=6):fim]
            r.append((w.sm_rootzone.mean(), w.sm_rootzone_pctl.mean()))
        linhas.append((a, r))
    rz = np.array([[x[0] for x in r] for _, r in linhas])
    pc = np.array([[x[1] for x in r] for _, r in linhas])
    p(f"  {k:28s} mediana raiz 15/mar {np.nanmedian(rz[:,0]):.3f} 15/abr {np.nanmedian(rz[:,1]):.3f} 15/mai {np.nanmedian(rz[:,2]):.3f} | "
      f"queda mar->mai {np.nanmedian(rz[:,0]-rz[:,2]):.3f} | pctl disponivel 15/mai em {np.sum(~np.isnan(pc[:,2]))}/10 anos")
    p("     por ano (15/abr raiz, pctl): " + "  ".join(f"{a}:{r[1][0]:.3f}/{r[1][1]:.0f}" for a, r in linhas))
    zz = sm[["sm_rootzone_pctl"]].sel(lon=lon, lat=lat, method="nearest").load().to_dataframe()
    p(f"     sm_rootzone_pctl presente em {100*zz.sm_rootzone_pctl.notna().mean():.0f}% dos dias 2015-2026")

p("\nSMAP L4 superficie (0-5 cm): data de secagem = 1o dia apos 1/mar em que a media movel de 7 d cai abaixo de"
  " (media de mar + media de set)/2 da propria celula (regra pre-declarada); x chuva IMERG 16/abr-15/mai")
for k in MATOPIBA + ["Quixada-CE"]:
    lon, lat, _ = PONTOS[k]
    s = sm["sm_surface"].sel(lon=lon, lat=lat, method="nearest").load().to_series().rolling(7, min_periods=5).mean()
    lim = (s[s.index.month == 3].mean() + s[s.index.month == 9].mean()) / 2
    datas, chuvas = [], []
    for a in range(2016, 2026):
        w = s.loc[f"{a}-03-01":f"{a}-08-31"]
        d = w[w < lim].index.min()
        datas.append(d.day_of_year if pd.notna(d) else np.nan)
        chuvas.append(soma(k, f"{a}-04-16", f"{a}-05-15")[0])
    datas, chuvas = np.array(datas, float), np.array(chuvas)
    ok = np.isfinite(datas)
    rho = pd.Series(datas[ok]).corr(pd.Series(chuvas[ok]), method="spearman")
    def dd(x):
        return (pd.Timestamp("2021-01-01") + pd.Timedelta(days=int(x) - 1)).strftime("%d/%m")
    p(f"  {k:28s} limiar {lim:.3f} | data mediana {dd(np.nanmedian(datas))} (min {dd(np.nanmin(datas))}, max {dd(np.nanmax(datas))}) | "
      f"Spearman com chuva 16/abr-15/mai = {rho:+.2f} (n={ok.sum()})")
    p("     " + "  ".join(f"{a}:{dd(x) if np.isfinite(x) else 'nd'}" for a, x in zip(range(2016, 2026), datas)))
sm.close()

# ---------------------------------------------------------------- E. Lagoa Seca
p("\n== E. Lagoa Seca-PB: IMERG x chuva de campo (Embrapa Documentos 266: 389 mm em 2015, 184 mm em 2016) ==")
k = "Lagoa Seca-PB"
for sem, ref in [("2015-06-05", 389), ("2016-04-19", 184)]:
    t0 = pd.Timestamp(sem)
    txt = []
    for dias in [90, 100, 110, 120, 130, 150]:
        v, _ = soma(k, t0, t0 + pd.Timedelta(days=dias - 1))
        txt.append(f"{dias}d:{v:.0f}")
    p(f"  semeadura {sem} (campo {ref} mm): " + "  ".join(txt))
anual = chuva[k].resample("YS").sum()
p("  IMERG anual Lagoa Seca 2014-2017:", {d.year: round(v) for d, v in anual.loc["2014":"2017"].items()},
  "| mediana 1998-2025:", round(float(anual.loc["1998":"2025"].median())))
p("  IMERG mensal (mm) 2015 abr-out:", {f"{d:%b}": round(v) for d, v in chuva[k].loc["2015-04":"2015-10"].resample("MS").sum().items()},
  "| 2016 mar-set:", {f"{d:%b}": round(v) for d, v in chuva[k].loc["2016-03":"2016-09"].resample("MS").sum().items()})
lon, lat, _ = PONTOS[k]
era = {}
for a in [2015, 2016]:
    e = xr.open_dataset(DADOS / f"era5/era5_ne_diario_{a}.nc")
    era[a] = e["tp"].sel(lon=lon, lat=lat, method="nearest").to_series()
    e.close()
for sem, ref in [("2015-06-05", 389), ("2016-04-19", 184)]:
    t0 = pd.Timestamp(sem); a = t0.year
    txt = "  ".join(f"{d}d:{era[a].loc[t0:t0 + pd.Timedelta(days=d - 1)].sum():.0f}" for d in [90, 120, 150])
    p(f"  ERA5 0,25 grau, semeadura {sem} (campo {ref} mm): {txt}")
gn_r = gn["Rainf_f_tavg"].sel(lon=lon, lat=lat, method="nearest").to_series()
gn_mm = gn_r * 86400 * gn_r.index.days_in_month
p("  GLDAS Noah forcante (mm/mes) 2015 jun-set:", {f"{d:%b}": round(v) for d, v in gn_mm.loc["2015-06":"2015-09"].items()},
  "| 2016 abr-ago:", {f"{d:%b}": round(v) for d, v in gn_mm.loc["2016-04":"2016-08"].items()})
p("  Anual (mm), 2001-2020, mediana: IMERG / ERA5 / GLDAS forcante")
for kk in ["Lagoa Seca-PB", "Bom Jesus-PI", "Balsas-MA", "Juazeiro-BA", "Quixada-CE"]:
    lo, la, _ = PONTOS[kk]
    ei = []
    for a in range(2001, 2021):
        e = xr.open_dataset(DADOS / f"era5/era5_ne_diario_{a}.nc")
        ei.append(float(e["tp"].sel(lon=lo, lat=la, method="nearest").sum()))
        e.close()
    im = chuva[kk].resample("YS").sum().loc["2001":"2020"].values
    gl = gn["Rainf_f_tavg"].sel(lon=lo, lat=la, method="nearest").to_series()
    gl = (gl * 86400 * gl.index.days_in_month).resample("YS").sum().loc["2001":"2020"].values
    p(f"  {kk:16s} {np.median(im):6.0f} / {np.median(ei):6.0f} / {np.median(gl):6.0f}   razao IMERG/ERA5 {np.median(im)/np.median(ei):.2f}")
gn.close()

# ---------------------------------------------------------------- F. Juazeiro
p("\n== F. Juazeiro-BA (Pimentel 2011: 'chuva entre 250 e 500 mm de novembro a marco') ==")
k = "Juazeiro exp. Pimentel"
m = chuva[k].loc["2006-08-01":"2007-08-31"].resample("MS").sum()
p("  IMERG mensal ago/2006-ago/2007: " + "  ".join(f"{d:%b%y}:{v:.0f}" for d, v in m.items()))
nm = np.array([soma(k, f"{a}-11-01", f"{a+1}-03-31")[0] for a in range(1998, 2025)])
an = chuva[k].resample("YS").sum().loc["1998":"2025"]
p(f"  nov-mar 1998/99-2024/25: mediana {np.median(nm):.0f}, p10 {np.percentile(nm,10):.0f}, p90 {np.percentile(nm,90):.0f}, "
  f"fora de 250-500 em {np.mean((nm<250)|(nm>500))*100:.0f}% dos anos | 2006/07 = {nm[2006-1998]:.0f} mm")
p(f"  anual mediana {an.median():.0f} mm; nov-mar / ano (mediana) {np.median(nm)/an.median()*100:.0f}%")

# ---------------------------------------------------------------- G. IMERG veranico x IBGE rendimento UF
p("\n== G. Veranico IMERG (maior sequencia de dias < 2 mm em 1/jan-31/mar) x rendimento IBGE por UF ==")
p("  Regras pre-declaradas: rendimento sem tendencia = razao para a reta OLS 1999-2025; Spearman; ano IBGE t = safra (t-1)/t")


def veranico(k, a):
    s = chuva[k].loc[f"{a}-01-01":f"{a}-03-31"] < 2
    best = run = 0
    for v in s.values:
        run = run + 1 if v else 0
        best = max(best, run)
    return best


for uf, pts in [("22", ["Bom Jesus-PI", "Urucui-PI"]), ("21", ["Balsas-MA"]), ("29", ["Luis Eduardo Magalhaes-BA"])]:
    for prod, nm in [("soja", "soja"), ("milho (em", "milho")]:
        y = serie(uf, prod, "rendimento").loc[1999:2025].dropna()
        y = y[y > 0]
        cf = np.polyfit(y.index.values, y.values, 1)
        ratio = y / np.polyval(cf, y.index.values)
        ver = pd.Series({a: np.mean([veranico(k, a) for k in pts]) for a in y.index if a <= 2025})
        nov_abr = pd.Series({a: np.mean([soma(k, f"{a-1}-11-01", f"{a}-04-30")[0] for k in pts]) for a in y.index})
        r1 = ratio.corr(ver.reindex(ratio.index), method="spearman")
        r2 = ratio.corr(nov_abr.reindex(ratio.index), method="spearman")
        # sensibilidade (adicionada apos ver que a reta linear fica negativa em 1999 no milho do PI):
        # tendencia log-linear, aplicada igual a todas as series
        cl = np.polyfit(y.index.values, np.log(y.values), 1)
        rlog = y / np.exp(np.polyval(cl, y.index.values))
        r3 = rlog.corr(ver.reindex(rlog.index), method="spearman")
        pior = rlog.nsmallest(3)
        p(f"  {UF[uf]} {nm:5s} n={len(ratio)}  rho(veranico) linear={r1:+.2f} log={r3:+.2f}  rho(chuva nov-abr) linear={r2:+.2f}"
          f"  min razao linear={ratio.min():.2f} | 3 piores (log): "
          + ", ".join(f"{a} ({v:.2f}; veranico {ver.get(a, np.nan):.0f} d)" for a, v in pior.items()))

p("\nCobertura do recorte NE (-48,8 a -34,7 lon): Tocantins (MATOPIBA, regiao Norte) fica em boa parte a oeste de -48,8;"
  " o recorte atual cobre MA, PI e BA do MATOPIBA, nao o TO inteiro.")
_f.close()
