"""Curador de bases (v3), testes E e F.

E. Solo: SoilGrids 2.0 (ISRIC, 250 m; leitura por ponto dos COG/VRT em files.isric.org, sem baixar o mapa) x textura
   MEDIDA nas 360 estacoes do CEMADEN (amostra deformada de 1 kg; Info de cada PCD, Zeri et al., Mendeley
   doi 10.17632/xrk5rfcpvg.2). Areia e argila, media de 0-5 e 5-15 cm (g/kg). Amostra salva em
   E:/campeonato-nasa/dados/complementares/soilgrids/soilgrids_pontos_cemaden.parquet.
F. ZARC oficial (Tabua de Risco 2026/2027, MAPA dados abertos, so CE) x ZARC sintetico do agronomo
   (saidas/agronomo_zarc_sintetico_prob.parquet: ultimo decendio com P(ISNA floracao >= 0,5) >= 0,7, isto e,
   risco <= 30%). Oficial: ultimo decendio com risco <= 30% (valores 20 ou 30) em sequeiro, por ciclo e solo.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
A = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")

# ---------------- E. SoilGrids x CEMADEN
print("=" * 20, "E. SoilGrids 2.0 x textura medida (CEMADEN)", "=" * 20)
OUT = DADOS / "complementares" / "soilgrids"
OUT.mkdir(parents=True, exist_ok=True)
CACHE = OUT / "soilgrids_pontos_cemaden.parquet"
est = pd.read_parquet(DADOS / "complementares" / "cemaden" / "cemaden_estacoes.parquet")
est["lat"], est["lon"] = est.latitude.astype(float), est.longitude.astype(float)
if CACHE.exists():
    sg = pd.read_parquet(CACHE)
else:
    sg = est[["estacao", "lat", "lon"]].copy()
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".vrt,.tif",
                      GDAL_HTTP_MAX_RETRY="3", GDAL_HTTP_RETRY_DELAY="2"):
        for prop in ["sand", "clay"]:
            for dep in ["0-5cm", "5-15cm"]:
                t0 = time.time()
                with rasterio.open(f"/vsicurl/https://files.isric.org/soilgrids/latest/data/{prop}/{prop}_{dep}_mean.vrt") as r:
                    xs, ys = transform("EPSG:4326", r.crs, sg.lon.tolist(), sg.lat.tolist())
                    v = np.array([x[0] for x in r.sample(zip(xs, ys))], dtype=float)
                v[v < 0] = np.nan
                sg[f"{prop}_{dep}"] = v  # g/kg
                print(f"  {prop} {dep}: {np.isfinite(v).sum()} pontos, {time.time() - t0:.0f}s", flush=True)
    sg.to_parquet(CACHE, index=False)
    registrar_manifesto("complementares/soilgrids", {
        "fonte": "ISRIC SoilGrids 2.0 (250 m), media prevista",
        "url": "https://files.isric.org/soilgrids/latest/data/",
        "recorte": "so os 360 pontos das estacoes CEMADEN (amostragem por ponto via /vsicurl/)",
        "variaveis": ["sand 0-5cm", "sand 5-15cm", "clay 0-5cm", "clay 5-15cm"],
        "arquivos": ["soilgrids_pontos_cemaden.parquet"],
        "script": "conselho/analises/v3_curador_valida_soilgrids_zarc.py",
    }, base=OUT)
X = est.merge(sg[[c for c in sg.columns if c not in ("lat", "lon")]], on="estacao")
for prop in ["sand", "clay"]:
    X[f"sg_{prop}"] = X[[f"{prop}_0-5cm", f"{prop}_5-15cm"]].mean(axis=1)
    X[f"campo_{prop}"] = pd.to_numeric(X[prop], errors="coerce")
    m = X[f"sg_{prop}"].notna() & X[f"campo_{prop}"].notna()
    d = X.loc[m, f"sg_{prop}"] - X.loc[m, f"campo_{prop}"]
    print(f"  {prop}: n={m.sum()} | campo mediana {X.loc[m, f'campo_{prop}'].median():.0f} g/kg | SoilGrids "
          f"{X.loc[m, f'sg_{prop}'].median():.0f} | vies {d.median():+.0f} | erro abs mediano {d.abs().median():.0f} | "
          f"Spearman {X.loc[m, f'sg_{prop}'].corr(X.loc[m, f'campo_{prop}'], method='spearman'):.2f}")


def classe(areia, argila):  # classe simplificada do ZARC antigo (1 arenoso, 2 medio, 3 argiloso)
    return np.where(argila >= 350, 3, np.where((areia >= 700) & (argila < 150), 1, 2))


m = X.sg_sand.notna() & X.campo_sand.notna()
cs, cc = classe(X.sg_sand[m], X.sg_clay[m]), classe(X.campo_sand[m], X.campo_clay[m])
print(f"  classe textural simplificada (arenoso/medio/argiloso): SoilGrids = campo em {(cs == cc).mean():.0%} das estacoes;"
      f" campo: {dict(zip(*np.unique(cc, return_counts=True)))} | SoilGrids: {dict(zip(*np.unique(cs, return_counts=True)))}")

# ---------------- F. ZARC oficial x sintetico
print("\n" + "=" * 20, "F. ZARC oficial 2026/2027 (CE, sequeiro) x ZARC sintetico (IMERG + POWER)", "=" * 20)
z = pd.read_csv(DADOS / "complementares" / "zarc" / "tabua_risco_ce_2026-2027.csv", sep=";", dtype=str)
z = z[z.Nome_Outros_Manejos == "Sequeiro"]
dec = [f"dec{i}" for i in range(1, 37)]
z[dec] = z[dec].astype(int)
ROT = {}
for i in range(36):
    mes, k = divmod(i, 3)
    ROT[f"dec{i + 1}"] = f"{[1, 11, 21][k]:02d}/{['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'][mes]}"
CULT = {"milho": "Milho 1", "caupi": "Feij\u00e3o Caupi", "sorgo": "Sorgo Gran"}


def ultimo_ok(row, lim=30):
    """ultimo decendio de jan-jun com risco <= lim (20 ou 30); indice 1..18, 0 se nenhum."""
    ok = [i for i in range(1, 19) if 0 < row[f"dec{i}"] <= lim]
    return max(ok) if ok else 0


SINT = pd.read_parquet(A / "saidas" / "agronomo_zarc_sintetico_prob.parquet")
DEC_S = ["01/jan", "11/jan", "21/jan", "01/fev", "11/fev", "21/fev", "01/mar", "11/mar", "21/mar", "01/abr", "11/abr", "21/abr"]


def sint_ultimo(cod, c):
    v = [SINT.loc[cod, f"{c}|{d}"] for d in DEC_S]
    ok = [i + 1 for i, p in enumerate(v) if p >= 0.7]
    return max(ok) if ok else 0


import json
nomes = {str(x["id"]): x["nome"] for x in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}
for c, pref in CULT.items():
    s = z[z.Nome_cultura.str.startswith(pref)].copy()
    if s.empty:
        print(f"  {c}: sem linhas"); continue
    s["ult"] = s.apply(ultimo_ok, axis=1)
    s["ult20"] = s.apply(lambda r: ultimo_ok(r, 20), axis=1)
    g = s.groupby("geocodigo").agg(ult_max=("ult", "max"), ult_med=("ult", "median"), ult20_max=("ult20", "max"),
                                   combos=("ult", "size"))
    g.index = g.index.astype(str)
    g["sint"] = [sint_ultimo(cd, c) if cd in SINT.index.astype(str) else np.nan for cd in g.index]
    g = g.dropna(subset=["sint"])
    from scipy.stats import spearmanr
    rho = spearmanr(g.ult_max, g.sint).correlation
    dif = (g.sint - g.ult_max)
    print(f"  {c}: {len(g)} municipios com ZARC | solos x ciclos por municipio: {int(g.combos.median())} | "
          f"sem janela <= 30% em nenhum solo/ciclo: {(g.ult_max == 0).sum()} | Spearman(oficial mais permissivo, sintetico) = {rho:.2f}")
    print(f"     sintetico - oficial (decendios): mediana {dif.median():+.0f}; |dif| <= 1 em {(dif.abs() <= 1).mean():.0%}; "
          f"sintetico mais tarde em {(dif > 1).mean():.0%}, mais cedo em {(dif < -1).mean():.0%}")
    print(f"     ultimo decendio oficial (mais permissivo): {g.ult_max.map(lambda i: ROT.get(f'dec{int(i)}', 'nenhum')).value_counts().to_dict()}")
    q = s[s.municipio.str.startswith("Quixad")]
    if len(q):
        lin = q[["Cod_Ciclo", "Cod_Solo", "ult", "ult20"]].copy()
        lin["ultimo_risco<=30%"] = lin.ult.map(lambda i: ROT.get(f"dec{int(i)}", "nenhum"))
        lin["ultimo_risco<=20%"] = lin.ult20.map(lambda i: ROT.get(f"dec{int(i)}", "nenhum"))
        cq = q.geocodigo.iloc[0]
        print(f"     Quixada ({cq}, {q.Portaria.iloc[0]}): sintetico = {DEC_S[sint_ultimo(cq, c) - 1] if sint_ultimo(cq, c) else 'nenhum'}")
        print("      ", lin.drop(columns=["ult", "ult20"]).sort_values(["Cod_Ciclo", "Cod_Solo"]).to_string(index=False).replace("\n", "\n       "))
print("  nota: codigos de ciclo 20/21/22 = Grupos I/II/III; solo 1/2/3 = arenoso/medio/argiloso, 11-16 = AD1-AD6",
      "(dicionario de dados da Tabua de Risco 2026). O sintetico usa um solo (CAD 100 mm/m) e um ciclo por cultura.")
