"""v4 agroecologo: condicao de transferencia da rotacao caupi (seca, agua salina) -> girassol (chuvas).

Neves et al. 2015 (Ciencia Rural 45:814, p. 818): o efeito residual da agua de 5 dS/m continua (T4)
apareceu no girassol porque a chuva de mar-jun/2012 foi baixa (30,4 + 86,8 + 15,6 + 0 = 132,8 mm,
pluviometro do ensaio). Estudos sem efeito residual tiveram chuva "pelo menos tres vezes maior".
Pergunta: com que frequencia a estacao de mar-jun do CE fica no nivel de 2012 (sem lavagem) e no
nivel de 3x 2012 (lavagem)? Tudo na escala IMERG (o v3 mostrou IMERG 289 mm x 132,8 relatado em
Pentecoste: o limiar relatado NAO pode ser usado direto na escala IMERG).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import xarray as xr

anos = range(1998, 2026)
somas = {}
for a in anos:
    f = DADOS / "imerg" / f"imerg_ce_diario_{a}.nc"
    ds = xr.open_dataset(f)
    somas[a] = ds.precip.sel(time=slice(f"{a}-03-01", f"{a}-06-30")).sum("time").load()
    ds.close()
cubo = xr.concat([somas[a] for a in anos], dim=pd.Index(list(anos), name="ano"))

lat, lon = -3.75, -39.25  # Pentecoste (Neves 2015, p. 815: 3o45'S, 39o15'W)
s = cubo.sel(lat=lat, lon=lon, method="nearest").to_series()
print("=" * 100)
print("A. Pentecoste, celula IMERG mais proxima: chuva mar-jun por ano (mm)")
print("=" * 100)
print(s.round(0).astype(int).to_string())
v12 = s.loc[2012]
print(f"  2012 = {v12:.0f} mm (relatado no ensaio 132,8). Posto de 2012 entre 28 anos: "
      f"{int((s <= v12).sum())} de {len(s)} (1 = mais seco)")
print(f"  anos com mar-jun <= 2012: {int((s <= v12).sum())}; anos >= 3x2012 ({3*v12:.0f} mm): {int((s >= 3*v12).sum())}")
print(f"  mediana 1998-2025 = {s.median():.0f} mm = {s.median()/v12:.2f} x 2012")
for e, sl in [("1998-2011", slice(1998, 2011)), ("2012-2025", slice(2012, 2025))]:
    ss = s.loc[sl]
    print(f"  {e}: anos <= 1,2 x 2012: {int((ss <= 1.2*v12).sum())} de {len(ss)}; mediana {ss.median():.0f}")

print()
print("=" * 100)
print("B. Todo o CE (celulas de 0,1 grau no recorte do estado): fracao de anos com mar-jun <= 1,2 x o")
print("   valor de Pentecoste em 2012 (escala IMERG). Condicao 'sem lavagem' da regra de Neves.")
print("=" * 100)
try:
    import geopandas as gpd
    from shapely.geometry import Point
    ce = ceara_gdf().to_crs(4326).union_all() if hasattr(ceara_gdf(), "union_all") else ceara_gdf().unary_union
    lats, lons = cubo.lat.values, cubo.lon.values
    mask = np.array([[ce.contains(Point(x, y)) for x in lons] for y in lats])
except Exception as ex:  # sem geopandas: usa o retangulo
    print("  (mascara do CE indisponivel, usando o recorte inteiro):", ex)
    mask = np.ones((cubo.lat.size, cubo.lon.size), bool)
lim = 1.2 * v12
frac = (cubo <= lim).mean("ano").values[mask]
print(f"  celulas no CE: {mask.sum()}; fracao de anos 'sem lavagem': mediana {np.median(frac):.2f}, "
      f"p10 {np.percentile(frac, 10):.2f}, p90 {np.percentile(frac, 90):.2f}")
for c in (0.1, 0.2, 0.3):
    print(f"  celulas com fracao >= {c:.1f}: {np.mean(frac >= c):.2%}")
med = cubo.median("ano").values[mask]
print(f"  mar-jun mediano no CE: p10 {np.percentile(med,10):.0f}, p50 {np.median(med):.0f}, p90 {np.percentile(med,90):.0f} mm")
anos_secos = (cubo.where(xr.DataArray(mask, dims=("lat", "lon"), coords={"lat": cubo.lat, "lon": cubo.lon}))
              <= lim).mean(("lat", "lon")).to_series()
print("  fracao do CE em condicao 'sem lavagem' por ano (so anos com >= 25% do estado):")
print(anos_secos[anos_secos >= 0.25].round(2).to_string())
