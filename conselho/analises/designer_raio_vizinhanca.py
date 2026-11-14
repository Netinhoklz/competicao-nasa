"""Designer (agricultor familiar) - Analise 2: ate que distancia a observacao do VIZINHO vale como evidencia?

Perguntas (desenho da rede de agricultores-sentinela e dos grupos de WhatsApp):
  (a) Chuva diaria e de 5 dias (fev-mai): a correlacao entre municipios cai com a distancia em que escala?
      -> raio em que o pluviometro de um vizinho informa a decisao da semana (veranico, replantio).
  (b) Chuva da quadra (fev-mai, anual) e quebra do milho (razao do rendimento por area plantada): em que escala?
      -> raio em que "o que aconteceu com o vizinho" e evidencia para o meu ano.
  (c) Quantos sentinelas por municipio? (distancia em que r = 0,5, ou seja, r2 = 25% da variancia explicada.)
Metodo: pares de municipios (184 -> 16.836 pares), distancia entre centroides (km), correlacao de Pearson das
series; ajuste r(d) = c0 * exp(-d / L) por minimos quadrados; mediana de r por faixa de 10 km.
Dados: saidas/designer_chuva_mun_diaria.parquet (gerado por designer_calendario_decisao.py a partir do IMERG V07
diario 0,1 grau), ibge_pam_mun_anual.parquet, referencia/ceara_municipios.geojson.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import warnings

warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV, REF

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
chuva = pd.read_parquet(OUT / "designer_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
mun = gpd.read_file(REF / "ceara_municipios.geojson")
cent = mun.to_crs("EPSG:5880").geometry.centroid
XY = pd.DataFrame({"x": cent.x.values / 1000, "y": cent.y.values / 1000}, index=mun.codarea.astype(str)).loc[chuva.columns]
D = np.sqrt((XY.x.values[:, None] - XY.x.values[None]) ** 2 + (XY.y.values[:, None] - XY.y.values[None]) ** 2)
iu = np.triu_indices(len(XY), 1)
d = D[iu]
print(f"{len(XY)} municipios, {len(d)} pares; distancia mediana ao vizinho mais proximo = "
      f"{np.median(np.sort(D, 1)[:, 1]):.1f} km")

c = chuva.loc["1998-01-01":"2025-12-31"]
quadra = c[c.index.month.isin([2, 3, 4, 5])]
series = {
    "chuva diaria (fev-mai)": quadra,
    "chuva de 5 dias (fev-mai)": quadra.groupby([quadra.index.year, (quadra.index.dayofyear - 1) // 5]).sum(),
    "chuva da quadra (total anual fev-mai)": quadra.groupby(quadra.index.year).sum(),
}

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(str)
s = pam[pam.produto.str.startswith("Milho (em gr") & (pam.ano >= 1990)].copy()
s["rp"] = np.where(s.area_plantada_ha >= 100, s.producao_t * 1000 / s.area_plantada_ha.replace(0, np.nan), np.nan)
s = s.sort_values(["cod", "ano"])
s["tend"] = s.groupby("cod")["rp"].transform(lambda v: v.rolling(7, center=True, min_periods=4).median())
s["razao"] = np.log(s.rp / s.tend)
rz = s[s.ano.between(1998, 2025)].pivot_table(index="ano", columns="cod", values="razao").reindex(columns=chuva.columns)
series["quebra do milho (log razao rend./tendencia)"] = rz


def decai(dd, c0, L):
    return c0 * np.exp(-dd / L)


linhas = []
faixas = np.arange(0, 400, 10)
tab_faixa = {}
for nome, S in series.items():
    C = S.corr(min_periods=12).values
    r = C[iu]
    ok = np.isfinite(r)
    (c0, L), _ = curve_fit(decai, d[ok], r[ok], p0=(0.9, 100), maxfev=20000)
    d50 = L * np.log(c0 / 0.5) if c0 > 0.5 else 0.0
    med = pd.Series(r[ok]).groupby(pd.cut(d[ok], faixas)).median()
    tab_faixa[nome] = med
    linhas.append({"serie": nome, "c0 (r a 0 km)": round(c0, 2), "L e-folding (km)": round(L, 0),
                   "d onde r=0,5 (km)": round(d50, 0),
                   "r mediano 0-20 km": round(np.nanmedian(r[ok & (d < 20)]), 2),
                   "r mediano 20-50 km": round(np.nanmedian(r[ok & (d >= 20) & (d < 50)]), 2),
                   "r mediano 100-150 km": round(np.nanmedian(r[ok & (d >= 100) & (d < 150)]), 2),
                   "r mediano 300+ km": round(np.nanmedian(r[ok & (d >= 300)]), 2)})
T = pd.DataFrame(linhas)
print(T.to_string(index=False))
F = pd.DataFrame(tab_faixa)
F.index = [f"{int(i.left)}-{int(i.right)}" for i in F.index]
print("\nr mediano por faixa de distancia (km):")
print(F.iloc[:20].round(2).to_string())

# sentinelas: area de um circulo com raio d50 -> quantos sentinelas para cobrir o Ceara (148.894 km2, IBGE)
AREA_CE = 148894
for _, row in T.iterrows():
    if row["d onde r=0,5 (km)"] > 0:
        n = AREA_CE / (np.pi * row["d onde r=0,5 (km)"] ** 2)
        print(f"{row.serie:45s}: ~{n:,.0f} sentinelas cobrem o CE com r>=0,5 (1 a cada {np.pi * row['d onde r=0,5 (km)'] ** 2:,.0f} km2)")
T.to_csv(OUT / "designer_raio_vizinhanca.csv", index=False)
