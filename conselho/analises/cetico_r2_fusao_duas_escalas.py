"""Cetico, rodada 2: o alerta de 30/abr (designer/estrategista) ganha habilidade LOCAL se somarmos o NDVI relativo?

Checagem A mostrou: a AUC do "% do normal" vem quase toda do nivel do ano (AUC dentro do ano ~0,57).
Aqui: alvo = quebra do milho (rendimento por area plantada < 50% da mediana movel centrada de 7 anos, como o designer).
Atributos no ponto de decisao ~10/mai:
  - nivel do ano: chuva 1/jan-30/abr como % do normal, MEDIA DO ESTADO (igual para todos os municipios no ano);
  - local chuva: % do normal do municipio menos a media do estado no ano;
  - local NDVI: anomalia do NDVI fev-abr do municipio (contra os outros anos) menos a media do estado no ano (MODIS 1 km).
Logistica com validacao deixando o ANO inteiro de fora. Metricas: AUC agrupada e AUC media dentro do ano.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import warnings

warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, DERIV, REF

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from rasterio import features
from rasterio.transform import from_origin
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
OUT = AN / "saidas"

# --- alvo
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(str)
s = pam[pam.produto.str.startswith("Milho (em gr") & (pam.ano >= 1990)].copy()
s = s.groupby(["cod", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
s["rp"] = np.where(s.area_plantada_ha >= 100, s.producao_t * 1000 / s.area_plantada_ha.replace(0, np.nan), np.nan)
s = s.sort_values(["cod", "ano"])
s["tend"] = s.groupby("cod")["rp"].transform(lambda v: v.rolling(7, center=True, min_periods=4).median())
s["quebra"] = ((s.rp / s.tend) < 0.5).astype(float).where((s.rp / s.tend).notna())
q = s.set_index(["cod", "ano"]).quebra

# --- chuva % do normal ate 30/abr
chuva = pd.read_parquet(OUT / "designer_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
ANOS = list(range(2000, 2026))
todos = list(range(1998, 2026))
cube = np.stack([chuva.loc[pd.Timestamp(a, 1, 1):].iloc[:120].values.sum(0) for a in todos])
pct = np.empty_like(cube)
for k in range(len(todos)):
    pct[k] = cube[k] / np.median(np.delete(cube, k, axis=0), axis=0)
C = pd.DataFrame(pct, index=todos, columns=chuva.columns).stack().rename("pct").reset_index()
C.columns = ["ano", "cod", "pct"]

# --- NDVI fev-abr por municipio
nd = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi
lat, lon = nd.lat.values, nd.lon.values
res = abs(lon[1] - lon[0])
mun = gpd.read_file(REF / "ceara_municipios.geojson")
tr = from_origin(lon.min() - res / 2, lat.max() + res / 2, res, res)
lab = features.rasterize(((g, i + 1) for i, g in enumerate(mun.geometry)), out_shape=(len(lat), len(lon)), transform=tr,
                         fill=0, dtype="int32")
if lat[0] < lat[-1]:
    lab = lab[::-1]
codes = np.r_["0", mun["codarea"].astype(str).values] if False else ["0"] + list(mun["codarea"].astype(str).values)
reg = []
for ano in ANOS:
    camp = []
    for m in (2, 3, 4):
        t = pd.Timestamp(ano, m, 1)
        if t in nd.time.values:
            a = nd.sel(time=t).values
            if np.nanmax(a) > 2:
                a = a / 10000.0
            camp.append(a)
    a = np.nanmean(np.stack(camp), 0)
    ok = np.isfinite(a) & (lab > 0)
    sm = np.bincount(lab[ok], weights=a[ok], minlength=len(codes))
    n = np.bincount(lab[ok], minlength=len(codes))
    for k in range(1, len(codes)):
        reg.append({"cod": codes[k], "ano": ano, "ndvi": sm[k] / n[k] if n[k] else np.nan})
N = pd.DataFrame(reg)
N["ndvi_a"] = N.ndvi - N.groupby("cod").ndvi.transform("mean")  # (a media inclui o ano; efeito pequeno, 26 anos)

F = C.merge(N, on=["cod", "ano"]).join(q, on=["cod", "ano"]).dropna()
F["nivel_ano"] = F.groupby("ano").pct.transform("mean")
F["chuva_local"] = F.pct - F.nivel_ano
F["ndvi_local"] = F.ndvi_a - F.groupby("ano").ndvi_a.transform("mean")
print(f"n = {len(F)} municipio-anos, {F.ano.nunique()} anos, taxa de quebra {F.quebra.mean():.1%}")


def loyo(cols):
    p = np.zeros(len(F))
    for a in F.ano.unique():
        tr_, te = F.ano != a, F.ano == a
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(F.loc[tr_, cols], F.loc[tr_, "quebra"])
        p[te.values] = m.predict_proba(F.loc[te, cols])[:, 1]
    F["p"] = p
    dentro = [(roc_auc_score(g.quebra, g.p), len(g)) for _, g in F.groupby("ano") if g.quebra.sum() >= 5 and (1 - g.quebra).sum() >= 5]
    return roc_auc_score(F.quebra, p), np.average([d[0] for d in dentro], weights=[d[1] for d in dentro]), len(dentro)


for nome, cols in [("so nivel do ano (chuva media do estado)", ["nivel_ano"]),
                   ("% do normal do municipio (designer)", ["pct"]),
                   ("nivel do ano + chuva local", ["nivel_ano", "chuva_local"]),
                   ("nivel do ano + NDVI local", ["nivel_ano", "ndvi_local"]),
                   ("nivel do ano + chuva local + NDVI local", ["nivel_ano", "chuva_local", "ndvi_local"])]:
    auc, aucd, nd_ = loyo(cols)
    print(f"  {nome:45s} AUC agrupada {auc:.3f} | AUC dentro do ano {aucd:.3f} ({nd_} anos)")
