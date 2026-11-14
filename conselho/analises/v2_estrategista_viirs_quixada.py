"""Estrategista, RODADA 2, analise 4: o VIIRS (sucessor do MODIS) explica as quebras de Quixada 2023-2025?

A banca deixou "Quixada 2023-2025: tres quebras do PAM com chuva normal; o motor nao explica". A analise 1 mostrou
que o SMAP tambem estava normal em 2023-2024 nos portoes. Se a vegetacao vista pelo VIIRS no pico da quadra tambem
estava normal, a quebra registrada nao parece falta d'agua (praga, relato ou area: vai para a auditoria como
"o satelite discorda do arbitro"). Se estava baixa, ha um sinal que a chuva e o solo nao viram.

Pre-declarado: NDVI VIIRS VNP13A3 medio de mar-abr-mai (meses de pico, conhecidos em junho), media do municipio na grade
0,01 grau; anomalia = valor do ano / mediana dos OUTROS anos 2012-2025 do mesmo municipio. Escore de quebra = -anomalia.
Validacao: AUC agrupada, AUC dentro do ano e Spearman entre anos (n = 14). Tambem a quadra 2026 (sem IBGE ainda).
So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, municipios_ce_gdf

import numpy as np
import pandas as pd
import xarray as xr
from rasterio import features
from rasterio.transform import from_origin
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
QUIX = "2311306"

pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha
p["ref"] = p.groupby("cod_local", group_keys=False).apply(
    lambda g: pd.Series([np.median(np.delete(g.r.values, i)) if len(g) > 5 else np.nan for i in range(len(g))],
                        index=g.index))
p = p.dropna(subset=["ref"])
p["razao"] = p.r / p.ref
p["quebra"] = (p.razao < 0.5).astype(int)
p["cod"] = p.cod_local.astype(str).str[:7]

vi = xr.open_dataset(DADOS / "viirs/vnp13a3_ndvi_evi_ceara_001deg.nc")
lat, lon = vi.lat.values, vi.lon.values
res = abs(lon[1] - lon[0])
mun = municipios_ce_gdf().to_crs("EPSG:4326")
mun["cod"] = mun.codarea.astype(str).str[:7]
tr = from_origin(lon.min() - res / 2, lat.max() + res / 2, res, res)
lab = features.rasterize(((g, i + 1) for i, g in enumerate(mun.geometry)), out_shape=(len(lat), len(lon)), transform=tr,
                         fill=0, dtype="int32")
if lat[0] < lat[-1]:
    lab = lab[::-1]
codes = np.r_[np.array(["0"]), mun.cod.values]
print(f"municipios com pixel VIIRS: {len(np.unique(lab[lab > 0]))} de {len(mun)}")


def media_mun(campo):
    ok = np.isfinite(campo) & (lab > 0)
    s = np.bincount(lab[ok], weights=campo[ok], minlength=len(codes))
    n = np.bincount(lab[ok], minlength=len(codes))
    with np.errstate(invalid="ignore", divide="ignore"):
        return s / n


reg = {}
for a in range(2012, 2027):
    tt = [pd.Timestamp(a, m, 1) for m in (3, 4, 5)]
    x = vi["ndvi"].sel(time=tt).values
    x = np.where((x > -0.2) & (x <= 1), x, np.nan)
    reg[a] = media_mun(np.nanmean(x, axis=0))[1:]
vi.close()
N = pd.DataFrame(reg, index=mun.cod.values).T  # ano x mun
A = N.copy() * np.nan
for a in N.index:
    A.loc[a] = N.loc[a] / N.drop(index=[a, 2026] if a != 2026 else [2026]).median()
lg = A.stack().rename("anom").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})
df = lg.merge(p[["cod", "ano", "quebra", "razao"]], on=["cod", "ano"]).dropna()
df["s"] = -df.anom


def auc_dentro(d, col):
    num = den = 0.0
    for a, g in d.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, g[col]); den += w
    return num / den


print("=" * 18, f"VIIRS NDVI mar-mai x quebra canonica do milho, 2012-2025 (n = {len(df)} municipio-anos)", "=" * 18)
print(f"  AUC agrupada = {roc_auc_score(df.quebra, df.s):.3f} | AUC dentro do ano = {auc_dentro(df, 's'):.3f}")
an = df.groupby("ano").agg(fq=("quebra", "mean"), anom=("anom", "median"))
r, pv = spearmanr(an.anom, an.fq)
print(f"  ENTRE anos (n = {len(an)}): Spearman(NDVI anomalia mediana, fracao em quebra) = {r:+.2f} (p {pv:.3f})")
print(an.round(3).T.to_string())
print("\n  Quixada (2311306): NDVI mar-mai / mediana dos outros anos, e o PAM (razao canonica do milho)")
qx = A[QUIX].rename("ndvi_anom").to_frame().join(p[p.cod == QUIX].set_index("ano")[["razao", "quebra"]])
qx["rank_ndvi_no_ano"] = [(A.loc[a] < A.loc[a, QUIX]).mean() for a in qx.index]  # posicao de Quixada entre os 184
print(qx.round(2).to_string())
print(f"\n  Quadra 2026 (sem IBGE ainda): NDVI mar-mai mediana estadual = {A.loc[2026].median():.3f} do normal; "
      f"{(A.loc[2026] < 0.9).mean():.0%} dos municipios abaixo de 0,90; Quixada = {A.loc[2026, QUIX]:.3f}")
lim = df.groupby(pd.cut(df.anom, [0, 0.85, 0.9, 0.95, 1.0, 1.05, 2])).agg(n=("quebra", "size"), p_quebra=("quebra", "mean"))
print("  P(quebra) por faixa de anomalia de NDVI (2012-2025, todos os municipios):")
print(lim.round(2).to_string())
