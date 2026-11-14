"""Ecologo (rodada 2): perspectiva de fogo out-dez/2026 pelo combustivel visto no NDVI (MODIS fev-jun de 2026 e 2025).
POWER e IMERG discordam na quadra de 2026 (546 contra 733 mm); o NDVI arbitra. Modelo: EF de celula 0,25 grau,
log(1+focos VIIRS out-dez) ~ anomalia de NDVI fev-jun (t, t-1), treinado em 2012-2025.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
sp = pd.read_parquet(AN / "sr_fundacao_painel_celula_mes.parquet")
print("Meses de NDVI em 2026:", sorted(sp[sp.ano == 2026].mes.unique()), "| em 2025:", sorted(sp[sp.ano == 2025].mes.unique()))
q5 = sp[sp.mes.between(2, 6)].groupby(["cel", "ano"]).agg(nd=("a_ndvi", "mean"), lat=("lat", "first"), lon=("lon", "first"))
est_nd = q5.groupby("ano").nd.mean()
print("Anomalia media de NDVI fev-jun por ano:", {int(k): round(v, 3) for k, v in est_nd.loc[2010:].items()})

v = pd.read_parquet(DADOS / "viirs" / "firms_viirs_snpp_nordeste.parquet",
                    columns=["latitude", "longitude", "acq_date", "type", "uf", "confidence"])
v = v[(v.uf == 23) & (v["type"] == 0) & (v.confidence.astype(str).str.lower().isin(["n", "h", "nominal", "high"]))].copy()
v["acq_date"] = pd.to_datetime(v.acq_date)
v = v[v.acq_date.dt.month.isin([10, 11, 12]) & v.acq_date.dt.year.between(2012, 2025)]
v["ano"] = v.acq_date.dt.year
cc = q5.reset_index().groupby("cel")[["lat", "lon"]].first()
d, i = cKDTree(cc.values).query(v[["latitude", "longitude"]].values)
v["cel"] = np.where(d <= 0.18, cc.index.values[i], -1)
f = v[v.cel >= 0].groupby(["cel", "ano"]).size()
rows = []
for c in cc.index:
    for y in range(2012, 2027):
        if (c, y) in q5.index and (c, y - 1) in q5.index:
            rows.append({"cel": c, "ano": y, "nd": q5.loc[(c, y), "nd"], "nd1": q5.loc[(c, y - 1), "nd"],
                         "lf": np.log1p(f.get((c, y), 0)) if y <= 2025 else np.nan})
P = pd.DataFrame(rows)
tr = P[P.ano <= 2025].dropna()
mc = tr.groupby("cel").lf.mean()
mx = tr.groupby("cel")[["nd", "nd1"]].mean()
X = (tr[["nd", "nd1"]] - mx.loc[tr.cel].values).values
beta = np.linalg.lstsq(X, (tr.lf - mc.loc[tr.cel].values).values, rcond=None)[0]
print("Coeficientes (por unidade de anomalia de NDVI):", beta.round(2))
p26 = P[(P.ano == 2026) & P.cel.isin(mc.index)].dropna(subset=["nd", "nd1"])
h = mc.loc[p26.cel].values + (p26[["nd", "nd1"]] - mx.loc[p26.cel].values).values @ beta
tot_obs = tr.groupby("ano").lf.apply(lambda s: np.expm1(s).sum())
# previsao LOYO do total para calibrar a escala
print(f"Celulas com previsao 2026 acima da propria climatologia: {(h > mc.loc[p26.cel].values).mean() * 100:.0f}% (n={len(h)})")
print(f"Total previsto out-dez/2026 (soma expm1, focos type 0 n/h na grade 0,25): ~{np.expm1(h).sum():,.0f}; "
      f"media 2012-2025 na mesma grade: {tot_obs.mean():,.0f}; min {tot_obs.min():,.0f}, max {tot_obs.max():,.0f}")
print("Observado por ano (mesma grade):", {int(k): int(x) for k, x in tot_obs.items()})
