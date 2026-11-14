"""v4 zootecnista: envelope hidrico dos ensaios de palma-sorgo e ILP contra o clima do Ceara.

Perguntas:
 A. O IMERG reproduz a chuva relatada nos ensaios (Serra Talhada-PE e Lagoa Seca-PB)?
    Em que percentil da climatologia local (1998-2025) caiu cada ensaio?
 B. Que fracao dos municipio-anos do Ceara (e do semiarido NE) tem chuva anual >= a agua
    total de cada nivel dos ensaios (Diniz 2017; Lima 2018a/b)?  (teto de transferencia:
    nos ensaios a agua vinha em parte por gotejo regular; no sequeiro so ha chuva irregular)
 C. Base de adocao de plantio direto/rotacao (Censo 2017) no Ceara e nos municipios dos ensaios.

Numeros dos artigos usados como referencia (todos lidos no texto):
 - Diniz et al. 2017 PAB 52:724-733, Tabela 1 (p.726): chuva 354,7 mm de nov/2014 (15 dias)
   a nov/2015 (9 dias); lâminas + chuva = 354,7 / 563,0 / 724,4 / 867,5 / 1.012,2 mm.
 - Lima et al. 2018a Rev Caatinga 31:191-201 e 2018b RBEAA 22:113-118: chuva 393 mm em 380 dias
   (jun/2012-jun/2013); agua total 976 / 1.048 / 1.096 / 1.152 / 1.202 mm; Tabela 2 (p.198) 2018a.
 - Jardim et al. 2020 RBEAA 24:756-761 (p.758): 997 mm de chuva de 18/03/2017 a 16/06/2018.
 - Zonta et al. 2016, Embrapa Algodao Documentos 266 (p.19): 389 mm (2015) e 184 mm (2016)
   "entre o plantio e a colheita do milho"; semeaduras 05/06/2015 e 19/04/2016 (colheita sem data:
   usamos 120 dias, aproximacao declarada).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403
import numpy as np
import pandas as pd
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
IMERG = DADOS / "imerg"

# ---------------------------------------------------------------- A. sitios dos ensaios
SITIOS = [
    # nome, lat, lon, inicio, fim, chuva relatada (mm), fonte
    ("Diniz 2017 (Serra Talhada, IPA)", -7.983, -38.250, "2014-11-16", "2015-11-09", 354.7, "Tabela 1, p.726"),
    ("Lima 2018a/b (Serra Talhada, IPA)", -7.983, -38.250, "2012-06-01", "2013-06-15", 393.0, "Material e Metodos, p.113/193"),
    ("Jardim 2020 (Serra Talhada, UAST)", -7.939, -38.292, "2017-03-18", "2018-06-16", 997.0, "p.758"),
    ("Zonta 2016 (Lagoa Seca-PB) 2015", -7.17, -35.85, "2015-06-05", "2015-10-02", 389.0, "p.19 (colheita ~120 d, aprox.)"),
    ("Zonta 2016 (Lagoa Seca-PB) 2016", -7.17, -35.85, "2016-04-19", "2016-08-16", 184.0, "p.19 (colheita ~120 d, aprox.)"),
]

anos = range(1998, 2027)
CHAVES = sorted({(round(lat, 3), round(lon, 3)) for _, lat, lon, *_ in SITIOS})  # celula unica por sitio
series = {}
for ano in anos:
    f = IMERG / f"imerg_ne_diario_{ano}.nc"
    if not f.exists():
        continue
    with xr.open_dataset(f) as d:
        for key in CHAVES:
            s = d["precip"].sel(lat=key[0], lon=key[1], method="nearest").to_series()
            series.setdefault(key, []).append(s)
serie = {k: pd.concat(v).sort_index() for k, v in series.items()}

print("=== A. IMERG (0,1 grau, celula mais proxima) nos sitios dos ensaios ===")
print(f"{'ensaio':38s} {'janela':25s} {'relatado':>9s} {'IMERG':>7s} {'IMERG/rel':>9s} {'pct clim':>8s} {'n anos':>6s}")
linhasA = []
for nome, lat, lon, ini, fim, rel, fonte in SITIOS:
    s = serie[(round(lat, 3), round(lon, 3))]
    ini, fim = pd.Timestamp(ini), pd.Timestamp(fim)
    tot = float(s.loc[ini:fim].sum())
    # climatologia: mesma janela deslocada por ano, so janelas completas
    outros = []
    for k in range(-30, 15):
        i2, f2 = ini + pd.DateOffset(years=k), fim + pd.DateOffset(years=k)
        if i2 < s.index.min() or f2 > pd.Timestamp("2025-12-31"):
            continue
        outros.append(float(s.loc[i2:f2].sum()))
    outros = np.array(outros)
    pct = 100.0 * (outros < tot).mean()
    linhasA.append((nome, tot, rel, pct, len(outros), np.median(outros)))
    print(f"{nome:38s} {ini.date()}..{fim.date()} {rel:9.1f} {tot:7.1f} {tot/rel:9.2f} {pct:8.0f} {len(outros):6d}   mediana clim {np.median(outros):.0f} mm  ({fonte})")

st = serie[(-7.983, -38.25)]
anual = st[(st.index.year >= 1998) & (st.index.year <= 2025)].groupby(st.index.year[(st.index.year >= 1998) & (st.index.year <= 2025)]).sum()
print(f"\nSerra Talhada (celula IPA), chuva anual IMERG 1998-2025: media {anual.mean():.0f} mm, mediana {anual.median():.0f} mm, "
      f"p10 {anual.quantile(.1):.0f}, p90 {anual.quantile(.9):.0f}. Diniz 2017 (p.726) cita media historica de 657 mm.")
lg = serie[(-7.17, -35.85)]
anl = lg[(lg.index.year >= 1998) & (lg.index.year <= 2025)].groupby(lg.index.year[(lg.index.year >= 1998) & (lg.index.year <= 2025)]).sum()
print(f"Lagoa Seca-PB (celula), chuva anual IMERG 1998-2025: media {anl.mean():.0f} mm, mediana {anl.median():.0f} mm; 2015 {anl.get(2015, np.nan):.0f}, 2016 {anl.get(2016, np.nan):.0f}")

# ---------------------------------------------------------------- B. envelope hidrico
print("\n=== B. Envelope: municipio-anos com chuva anual (IMERG, ano civil 1998-2025) >= agua total do ensaio ===")
im = pd.read_parquet(DERIV / "ibge_ne_mun_imerg_mensal.parquet", columns=["data", "cod_mun", "precip_mm"])
im = im[(im.data.dt.year >= 1998) & (im.data.dt.year <= 2025)]
ref = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet")
an = im.groupby(["cod_mun", im.data.dt.year.rename("ano")]).precip_mm.agg(["sum", "count"]).reset_index()
an = an[an["count"] == 12].merge(ref[["cod_mun", "uf", "semiarido_2022", "municipio"]], on="cod_mun")
grupos = {
    "Ceara (todos)": an[an.uf == "CE"],
    "Ceara semiarido 2022": an[(an.uf == "CE") & an.semiarido_2022],
    "Semiarido NE 2022": an[an.semiarido_2022],
}
LIMIARES = [
    (355, "Diniz sequeiro (LER 1,51 nao variou com a lamina)"),
    (563, "Diniz 25% ETo"),
    (976, "Lima 'sem irrigacao diferenciada': consorcio 11,5 x 8,7 t MS, NS"),
    (1048, "Lima 1o nivel com consorcio > solteira (15,3 x 9,1 t)"),
    (1202, "Lima maximo: 24,8 x 6,9 t (+258%)"),
]
for g, d in grupos.items():
    print(f"\n{g}: {d.cod_mun.nunique()} municipios, {len(d)} municipio-anos; chuva anual mediana {d['sum'].median():.0f} mm (p10 {d['sum'].quantile(.1):.0f}, p90 {d['sum'].quantile(.9):.0f})")
    for lim, rot in LIMIARES:
        fr = (d["sum"] >= lim).mean()
        # fracao de municipios em que >= metade dos anos passa do limiar
        porm = d.groupby("cod_mun")["sum"].apply(lambda x: (x >= lim).mean())
        print(f"   >= {lim:5d} mm: {100*fr:5.1f}% dos municipio-anos; municipios com >= 50% dos anos acima: {100*(porm >= .5).mean():5.1f}%   [{rot}]")
    # anos secos: 1998, 2012, 2016
    for a in (1998, 2012, 2016):
        da = d[d.ano == a]
        print(f"   ano {a}: mediana {da['sum'].median():.0f} mm; >=355 {100*(da['sum']>=355).mean():.0f}%; >=976 {100*(da['sum']>=976).mean():.0f}%")

# ---------------------------------------------------------------- C. Censo 2017
print("\n=== C. Censo Agro 2017: plantio direto e rotacao (% dos estabelecimentos) ===")
cp = pd.read_parquet(DERIV / "ibge_ne_censo2017_praticas_mun.parquet")
cols = [c for c in cp.columns if c.startswith("pct_") and not c.endswith("_fam")]
print("colunas pct disponiveis:", cols[:20])
use = [c for c in ["pct_rotacao", "pct_plantio_direto", "pct_cultivo_minimo", "pct_pousio", "pct_nenhuma"] if c in cp.columns]
cp = cp.merge(ref[["cod_mun", "uf", "municipio", "semiarido_2022"]], on="cod_mun")
ce = cp[cp.uf == "CE"]
w = ce["n_estab"]
for c in use:
    print(f"   Ceara {c}: media ponderada por estab. {np.average(ce[c].fillna(0), weights=w):.1f}%  (mediana municipal {ce[c].median():.1f}%)")
for nm in ["Serra Talhada", "Lagoa Seca", "Esperança", "Quixadá"]:
    r = cp[cp.municipio == nm]
    if len(r):
        print(f"   {nm} ({r.uf.iloc[0]}): " + ", ".join(f"{c}={r[c].iloc[0]:.1f}" for c in use))
