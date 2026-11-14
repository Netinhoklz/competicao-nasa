"""Curador de bases (v3), teste A4: a quadra de 2026, fora da amostra do teste A (1998-2025).
Chuva acumulada de 1/jan a 30/abr de 2026 por municipio: IMERG (via POWER, cache municipal do estrategista) x media
dos postos da FUNCEME no municipio (postos.zip de 13/11/2026). Tambem a defasagem do dado de campo: ultimo dia com
leitura e quantos postos leram nos ultimos 7 dias.
So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import numpy as np
import pandas as pd
import geopandas as gpd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
F = DADOS / "complementares" / "funceme"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
dia = pd.read_parquet(F / "funceme_postos_diario.parquet")
meta = pd.read_parquet(F / "funceme_postos_meta.parquet")
ok = dia[dia.mm.notna()]
ult = ok.data.max()
print(f"ultimo dia com leitura FUNCEME no arquivo: {ult.date()} | postos com leitura nos 7 dias ate ele: "
      f"{ok[ok.data > ult - pd.Timedelta(days=7)].posto.nunique()}")
mun = gpd.read_file(REF / "ceara_municipios.geojson")
pts = gpd.GeoDataFrame(meta, geometry=gpd.points_from_xy(meta.lon, meta.lat), crs=mun.crs)
pj = gpd.sjoin(pts, mun[["codarea", "geometry"]], predicate="within")[["posto", "codarea"]]
W = ok[(ok.data >= "2026-01-01") & (ok.data <= "2026-04-30")].merge(pj, on="posto")
cob = W.groupby(["codarea", "data"]).mm.mean().unstack(0)
idx = pd.date_range("2026-01-01", "2026-04-30")
cob = cob.reindex(idx)
cob.columns = cob.columns.astype(str)
g = cob.sum(min_count=1).where(cob.notna().mean() >= 0.9)
ch = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
ch.columns = ch.columns.astype(str)
i = ch.loc["2026-01-01":"2026-04-30"].sum()
X = pd.DataFrame({"posto_mm": g, "imerg_mm": i}).dropna()
print(f"municipios com postos completos (>= 90% dos dias): {len(X)}")
print(f"2026, 1/jan-30/abr: razao IMERG/postos = {X.imerg_mm.sum() / X.posto_mm.sum():.2f}; "
      f"Spearman entre municipios = {X.posto_mm.corr(X.imerg_mm, method='spearman'):.2f}; "
      f"Pearson = {X.posto_mm.corr(X.imerg_mm):.2f}")
print("mediana estadual: postos", round(X.posto_mm.median()), "mm | IMERG", round(X.imerg_mm.median()), "mm")
q = X.loc[[c for c in X.index if c == "2311306"]]
print("Quixada (2311306):", q.round(0).to_dict("records"))
