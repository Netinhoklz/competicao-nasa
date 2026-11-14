"""Ecologo de pragas - Analise 1: relogio termico das pragas (graus-dia) no Ceara e no mundo.

Perguntas:
  (a) Quantas geracoes de lagarta-do-cartucho (Spodoptera frugiperda) e de bicudo (Anthonomus grandis) cabem por ano
      e por ciclo de milho no Ceara? Ha tendencia 1981-2025?
  (b) Em que lugares do mundo o inverno faz a "quebra termica" do ciclo, e onde so a rotacao/vazio sanitario pode fazer?

Parametros (literatura da revisao, pesquisa/artigos_e_datasets.md, secao 4):
  - S. frugiperda: limiar inferior ovo-adulto 12,57 C; ovo 35,68 + larva 204,60 + pupa 150,54 = 390,8 graus-dia
    (du Plessis et al. 2020, Insects 11:228). Sem pre-oviposicao -> numero de geracoes e um teto.
  - A. grandis: ciclo de 16,1 d a 32 C e 46,2 d a 18 C (Pereira et al. 2023, Insects 14:582). Ajuste linear da taxa
    de desenvolvimento por esses 2 pontos -> Tb ~ 10,5 C e K ~ 346 graus-dia (aproximacao nossa, nao do artigo).
Metodo de graus-dia: media diaria (Tmax+Tmin)/2 com corte superior horizontal em 32 C (sensibilidade sem corte).
Dados: NASA POWER diario 0,5 grau no Ceara (E:/campeonato-nasa/dados/power/power_ce_diario.nc, 1981-2026) e
amostra global de 107 pontos de 2020 (E:/campeonato-nasa/dados/power/power_global_amostra.parquet).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import numpy as np
import pandas as pd
import pymannkendall as mk
import xarray as xr
from shapely.geometry import Point

FAW_TB, FAW_K = 12.57, 35.68 + 204.60 + 150.54
# bicudo: taxa = a + b*T por dois pontos (18 C, 46,2 d) e (32 C, 16,1 d)
r18, r32 = 1 / 46.2, 1 / 16.1
b = (r32 - r18) / (32 - 18)
BW_TB = 18 - r18 / b
BW_K = 1 / b
TUP = 32.0
print(f"Bicudo (derivado de Pereira 2023): Tb = {BW_TB:.2f} C, K = {BW_K:.0f} graus-dia | Lagarta: Tb = {FAW_TB}, K = {FAW_K:.1f}")


def gd(tmax, tmin, tb, tup=TUP):
    tm = (tmax + tmin) / 2
    if tup is not None:
        tm = np.minimum(tm, tup)
    return np.maximum(tm - tb, 0)


ds = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")[["T2M_MAX", "T2M_MIN"]].load()
uf = gpd.read_file(DADOS / "referencia" / "ceara_uf.geojson").to_crs(4326).union_all()
LA, LO = np.meshgrid(ds.lat.values, ds.lon.values, indexing="ij")
mk_ce = np.array([[uf.buffer(0.15).contains(Point(lo, la)) for lo, la in zip(rlo, rla)] for rlo, rla in zip(LO, LA)])
print("Celulas POWER 0,5 grau dentro do Ceara:", int(mk_ce.sum()))

tx, tn = ds.T2M_MAX, ds.T2M_MIN
res = {}
for nome, tb, k in (("lagarta", FAW_TB, FAW_K), ("bicudo", BW_TB, BW_K)):
    for tup in (TUP, None):
        d = gd(tx, tn, tb, tup)
        g = (d.where(xr.DataArray(mk_ce, dims=("lat", "lon"), coords={"lat": ds.lat, "lon": ds.lon}))
             .mean(("lat", "lon")).to_series())
        ann = g.groupby(g.index.year).sum() / k
        ann = ann.loc[1981:2025]
        res[(nome, "corte32" if tup else "sem_corte")] = ann

print("\n(a) Geracoes por ano no Ceara (media das celulas):")
for (nome, var), ann in res.items():
    t = mk.original_test(ann.values)
    print(f"  {nome:8s} {var:9s}: media 1981-2025 = {ann.mean():.1f} geracoes/ano (min {ann.min():.1f} em {ann.idxmin()}, "
          f"max {ann.max():.1f} em {ann.idxmax()}); Sen = {t.slope * 10:+.2f} geracoes/decada, p = {t.p:.4f}")
faw = res[("lagarta", "corte32")]
print(f"  lagarta: 1981-1990 = {faw.loc[1981:1990].mean():.2f} | 2016-2025 = {faw.loc[2016:2025].mean():.2f} geracoes/ano")

# geracoes dentro de um ciclo de milho de 120 d semeado em 1o de fevereiro (janela tipica da quadra) e no ciclo seco
dfaw = gd(tx, tn, FAW_TB).where(xr.DataArray(mk_ce, dims=("lat", "lon"), coords={"lat": ds.lat, "lon": ds.lon})).mean(("lat", "lon")).to_series()
dbw = gd(tx, tn, BW_TB).where(xr.DataArray(mk_ce, dims=("lat", "lon"), coords={"lat": ds.lat, "lon": ds.lon})).mean(("lat", "lon")).to_series()
ger_ciclo, ger_seco, bw_ciclo = [], [], []
for y in range(1981, 2026):
    ger_ciclo.append(dfaw.loc[f"{y}-02-01":pd.Timestamp(f"{y}-02-01") + pd.Timedelta(days=119)].sum() / FAW_K)
    ger_seco.append(dfaw.loc[f"{y}-08-01":f"{y}-12-31"].sum() / FAW_K)
    bw_ciclo.append(dbw.loc[f"{y}-02-15":pd.Timestamp(f"{y}-02-15") + pd.Timedelta(days=149)].sum() / BW_K)
print(f"  Lagarta: geracoes num milho de 120 d semeado em 1/fev = {np.mean(ger_ciclo):.2f} (faixa {min(ger_ciclo):.2f}-{max(ger_ciclo):.2f})")
print(f"  Lagarta: geracoes possiveis na entressafra ago-dez (se houver hospedeiro verde) = {np.mean(ger_seco):.2f}")
print(f"  Bicudo: geracoes num algodao de 150 d semeado em 15/fev = {np.mean(bw_ciclo):.2f}")

mens = dfaw.groupby(dfaw.index.month).mean()
print("  Graus-dia diarios medios da lagarta por mes (CE):", mens.round(1).to_dict())

# sensibilidade: +1 e +2 C uniforme
for dT in (1, 2):
    g2 = gd(tx + dT, tn + dT, FAW_TB).where(xr.DataArray(mk_ce, dims=("lat", "lon"), coords={"lat": ds.lat, "lon": ds.lon})).mean(("lat", "lon")).to_series()
    a2 = g2.groupby(g2.index.year).sum().loc[1991:2020].mean() / FAW_K
    print(f"  +{dT} C: lagarta {a2:.2f} geracoes/ano (1991-2020 = {faw.loc[1991:2020].mean():.2f})")

# (b) mundo: 107 pontos de 2020
g = pd.read_parquet(DADOS / "power" / "power_global_amostra.parquet")
g = g[g.param.isin(["T2M_MAX", "T2M_MIN"])].pivot_table(index=["ponto", "lat", "lon", "data"], columns="param", values="valor").reset_index()
g = g[(g.T2M_MAX > -90) & (g.T2M_MIN > -90)]
g["gd"] = gd(g.T2M_MAX.values, g.T2M_MIN.values, FAW_TB)
g["mes"] = pd.to_datetime(g.data).dt.month
pm = g.groupby(["ponto", "lat", "lon", "mes"]).gd.mean().reset_index()
# "quebra termica": meses com < 2 graus-dia/dia (uma geracao levaria > 6 meses)
glob = pm.groupby(["ponto", "lat", "lon"]).agg(meses_quebra=("gd", lambda s: int((s < 2).sum()))).reset_index()
glob["geracoes_ano"] = g.groupby(["ponto", "lat", "lon"]).gd.sum().values / FAW_K
glob = glob.sort_values("geracoes_ano", ascending=False)
print("\n(b) Amostra global POWER 2020 (107 pontos): lagarta-do-cartucho")
print(f"  Pontos sem nenhum mes de quebra termica: {(glob.meses_quebra == 0).sum()} de {len(glob)}; "
      f"com >= 4 meses de quebra: {(glob.meses_quebra >= 4).sum()}")
trop = glob[glob.lat.abs() <= 23.5]
print(f"  Entre os tropicos: {(trop.meses_quebra == 0).mean() * 100:.0f}% sem quebra termica (n = {len(trop)})")
sel = ["Fortaleza_CE", "Sahel_Niger", "Etiopia", "Punjab", "Deccan", "Tailandia", "Iowa", "Kansas", "Planicie_Norte_China",
       "Franca", "Ucrania", "Pradarias_Canada", "Delta_Nilo", "Vale_Central_CA", "Uganda", "Nigeria"]
print(glob[glob.ponto.isin(sel)].round(1).to_string(index=False))
out = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/ecologo_grausdia_global_2020.csv")
glob.round(2).to_csv(out, index=False)
print("Tabela global salva em", out)
