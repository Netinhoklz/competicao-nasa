"""v3 pedologo/ecologo do fogo -- teste 2: recorrencia do fogo no Ceara com MCD64A1 (NASA), contra
Silva et al. 2023 (Ci. Fl. 33(1) e70195: MCD64A1 2001-2018, bioma Caatinga), Argibay et al. 2020 (Landsat 30 m,
Capivara-Confusoes/PI 1999-2017), Franca Rocha et al. 2024 (Fire 7:437, MapBiomas/Landsat 1985-2023) e o pousio de
10-15 anos de Menezes et al. 2012 (Braz. J. Biol. 72(3) supl.).

Dados: mcd64a1_queimado_anual_nordeste_0005deg.nc (pixel de 500 m reamostrado por vizinho a 0,005 grau; 1 = queimou
no ano), mcd64a1_area_queimada_mensal_uf.parquet (km2 por UF e mes), FIRMS VIIRS (type 0, n/h) para o calendario.
Mascara do CE: centro do pixel dentro do limite IBGE (referencia/ceara_uf.geojson).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *
import numpy as np, pandas as pd, xarray as xr, shapely

ds = xr.open_dataset(DADOS / "modis" / "mcd64a1_queimado_anual_nordeste_0005deg.nc")
q = ds.queimado.sel(lat=slice(-2.5, -8.0), lon=slice(-41.5, -37.0))
LON, LAT = np.meshgrid(q.lon.values, q.lat.values)
ce = ceara_gdf().geometry.union_all()
dentro = shapely.contains_xy(ce, LON, LAT)
npx = int(dentro.sum())
area_px = (0.005 * 111.32) ** 2 * np.cos(np.deg2rad(LAT[dentro]))  # km2
area_ce = area_px.sum()
print(f"Pixels 0,005 grau no CE: {npx} (~{area_ce:,.0f} km2; IBGE ~148.900 km2)")

def resumo(a0, a1):
    Q = q.sel(ano=slice(a0, a1)).values[:, dentro].astype(np.int16)  # (anos, px)
    n = Q.sum(0)
    anos = a1 - a0 + 1
    queim = n >= 1
    print(f"\n--- {a0}-{a1} ({anos} anos) ---")
    print(f"  area queimada ao menos 1 vez: {area_px[queim].sum():,.0f} km2 = {queim.mean():.1%} do CE")
    print(f"  area queimada somada (pixel-ano): {(Q * area_px).sum():,.0f} km2; media anual {(Q * area_px).sum() / anos:,.0f} km2"
          f" ({(Q * area_px).sum() / anos / area_ce:.2%} do CE por ano)")
    vc = pd.Series(n[queim]).value_counts().sort_index()
    print("  numero de anos queimados por pixel (entre os queimados): " +
          ", ".join(f"{k}: {v / queim.sum():.1%}" for k, v in vc.items()))
    print(f"  maximo de anos queimados num pixel: {n.max()} | fracao da area queimada com recorrencia (>= 2 anos): {(n >= 2).sum() / queim.sum():.1%}")
    return Q, n

Q18, n18 = resumo(2001, 2018)   # periodo de Silva et al. 2023
Q25, n25 = resumo(2001, 2025)

# reincidencia dentro de 10 anos (pousio de 10-15 anos, Menezes et al. 2012), com seguimento completo:
Q = q.sel(ano=slice(2001, 2025)).values[:, dentro].astype(bool)
anos = np.arange(2001, 2026)
prim = np.where(Q.any(0), Q.argmax(0), -1)
for janela, ultimo in [(10, 2015), (5, 2020)]:
    sel = (prim >= 0) & (anos[np.clip(prim, 0, None)] <= ultimo)
    re = np.zeros(sel.sum(), bool); gap = np.full(sel.sum(), np.nan)
    Qs, ps = Q[:, sel], prim[sel]
    for k in range(1, janela + 1):
        ii = ps + k
        hit = Qs[ii, np.arange(len(ps))] & ~re
        gap[hit] = k; re |= hit
    print(f"\nPixels com 1a queima em 2001-{ultimo} (seguimento de {janela} anos): {sel.sum()} ; reincidiram em ate {janela} anos: {re.mean():.1%}"
          f" | entre os reincidentes, intervalo mediano {np.nanmedian(gap):.0f} anos; ate 3 anos: {np.mean(gap[re] <= 3):.1%}")
print("  (pixel de 500 m ~ 21-25 ha, nao e talhao: um rocado pequeno nao aparece no MCD64A1; ver texto)")

# --- comparacao entre UFs (Silva: medias de ocorrencias PI > BA > CE; nao e a mesma metrica)
uf = pd.read_parquet(DADOS / "modis" / "mcd64a1_area_queimada_mensal_uf.parquet")
uf["ano"] = pd.to_datetime(uf.data).dt.year; uf["mes"] = pd.to_datetime(uf.data).dt.month
nomes = {21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA"}
u = uf[uf.ano.between(2001, 2018)].groupby("uf").area_queimada_km2.sum() / 18
print("\nArea queimada media anual 2001-2018 por UF (UF inteira, MCD64A1): " +
      ", ".join(f"{nomes[k]} {v:,.0f} km2" for k, v in u.sort_values(ascending=False).items()))

# --- calendario do fogo no CE: area MCD64A1 x focos VIIRS
ce_m = uf[(uf.uf == 23) & uf.ano.between(2001, 2025)].groupby("mes").area_queimada_km2.sum()
ce_m = ce_m / ce_m.sum()
v = pd.read_parquet(DADOS / "viirs" / "firms_viirs_snpp_nordeste.parquet", columns=["acq_date", "type", "uf", "confidence"])
v = v[(v.uf == 23) & (v["type"] == 0) & (v.confidence.astype(str).str.lower().isin(["n", "h"]))]
fm = pd.to_datetime(v.acq_date).dt.month.value_counts(normalize=True).sort_index()
print("\nCalendario no CE, fracao por mes (MCD64A1 area 2001-2025 | VIIRS focos 2012-2025):")
for mth in range(1, 13):
    print(f"  {mth:2d}: area {ce_m.get(mth, 0):5.1%} | focos {fm.get(mth, 0):5.1%}")
cum_a = ce_m.cumsum(); cum_f = fm.cumsum()
print(f"  acumulado ate 30/set: area {cum_a[9]:.0%} | focos {cum_f[9]:.0%}; meses de maior area: {list(ce_m.sort_values(ascending=False).index[:3])}")

# --- anos de pico (Franca Rocha: 2021 = maior area queimada da Caatinga em 1985-2023)
ne = uf[uf.ano.between(2001, 2025)].groupby("ano").area_queimada_km2.sum()
cea = uf[(uf.uf == 23) & uf.ano.between(2001, 2025)].groupby("ano").area_queimada_km2.sum()
print(f"\nPosto de 2021 entre 2001-2025: no CE {int(cea.rank(ascending=False)[2021])}o; no NE (9 UFs) {int(ne.rank(ascending=False)[2021])}o")
print("  maiores anos CE:", list(cea.sort_values(ascending=False).index[:5]), "| maiores anos NE:", list(ne.sort_values(ascending=False).index[:5]))

# --- MCD64A1 x FIRMS: fracao de celulas de 375 m (proposta: 17% do CE em celulas com >= 1 foco 2012-2025)
Q1225 = q.sel(ano=slice(2012, 2025)).values[:, dentro].astype(bool).any(0)
print(f"\nMCD64A1 2012-2025: {Q1225.mean():.1%} do CE queimou ao menos 1 vez (500 m) -- comparar com 17% das celulas VIIRS com foco")
