import sys; sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *
import xarray as xr, pandas as pd, json
ds = xr.open_dataset(DADOS/"imerg"/"imerg_ce_diario_2012.nc"); print(ds)
import geopandas as gpd
g = gpd.read_file(REF/"ceara_municipios.geojson"); print(g.columns.tolist(), len(g)); print(g.head(2))
m = pd.read_parquet(DERIV/"ibge_pam_mun_anual.parquet")
print(m[(m.produto.str.startswith("Feij"))&(m.ano==2012)].head())
print(m.ano.min(), m.ano.max())
a = m[m.ano.between(2019,2025)].groupby("produto").area_colhida_ha.sum().sort_values(ascending=False).head(20)/7
print(a)
pr = pd.read_parquet(DERIV/"faostat_precos_produtor.parquet")
b = pr[(pr.Area=="Brazil")&(pr.Months=="Annual value")]
print(b.groupby(["Item","Element"]).Year.agg(["min","max","count"]))
