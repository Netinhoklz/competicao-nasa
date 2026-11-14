"""Arquiteto-chefe, versao final: sensibilidade das datas-limite do ZARC sintetico a escala da ET0.

A banca mostrou que a ET0 do POWER (~2.280 mm/ano) fica ~13-16% acima da do ERA5 (~1.970), coerente com o vies quente
da Tmax do POWER. Aqui o MESMO balde FAO-56 do agronomo_isna_zarc_sintetico.py (copiado, nao importado, para nao
sobrescrever as saidas dele) roda com ET0 x 1,00 e ET0 x 0,87 (escala do ERA5). Data-limite = ultimo decendio com
P(ISNA floracao >= 0,5) >= 0,7 (risco <= 30%). So le arquivos; nao escreve nada.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
ANOS = np.arange(1998, 2026)
ND = 304

chuva = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["pt"] = mun.geometry.representative_point()
cods = [c for c in chuva.columns if c in set(mun.codarea)]
mun = mun.set_index("codarea").loc[cods]
e0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"].load()
et0 = pd.DataFrame({c: e0.sel(lat=mun.loc[c, "pt"].y, lon=mun.loc[c, "pt"].x, method="nearest").to_series() for c in cods})
NM = len(cods)
R = np.zeros((NM, len(ANOS), ND), np.float32)
E = np.zeros_like(R)
for j, a in enumerate(ANOS):
    idx = pd.date_range(f"{a}-01-01", periods=ND, freq="D")
    R[:, j, :] = chuva.reindex(idx)[cods].fillna(0).values.T
    E[:, j, :] = et0.reindex(idx)[cods].interpolate().bfill().values.T

CULT = {"milho": (20, 30, 35, 25, 0.30, 1.20, 0.35, 0.6, 0.55),
        "caupi": (15, 20, 25, 15, 0.40, 1.05, 0.35, 0.5, 0.45),
        "sorgo": (20, 30, 40, 25, 0.30, 1.05, 0.55, 0.8, 0.55)}
AWC = 100.0
DEC = {"01/jan": 0, "11/jan": 10, "21/jan": 20, "01/fev": 31, "11/fev": 41, "21/fev": 51, "01/mar": 59,
       "11/mar": 69, "21/mar": 79, "01/abr": 90, "11/abr": 100, "21/abr": 110}
ORD = list(DEC)


def kc_curve(c):
    li, ld, lm, ll, ki, km, ke, _, _ = CULT[c]
    k = np.concatenate([np.full(li, ki), np.linspace(ki, km, ld), np.full(lm, km), np.linspace(km, ke, ll)])
    mid = np.zeros(len(k), bool)
    mid[li + ld:li + ld + lm] = True
    return k.astype(np.float32), mid


def isna_flor(c, sow, Ef):
    kc, mid = kc_curve(c)
    L = len(kc)
    taw = AWC * CULT[c][7]
    raw = CULT[c][8] * taw
    Dr = np.full(sow.shape, taw, np.float32)
    eta_m = np.zeros(sow.shape, np.float32); etc_m = np.zeros_like(eta_m)
    for d in range(ND):
        k = d - sow
        P = R[:, :, d]; e = Ef[:, :, d]
        dentro = (k >= 0) & (k < L)
        kci = np.where(dentro, kc[np.clip(k, 0, L - 1)], 0.0)
        ks = np.where(Dr <= raw, 1.0, np.clip((taw - Dr) / (taw - raw), 0, 1))
        kbare = 0.3 * np.clip((taw - Dr) / taw, 0, 1)
        etc = kci * e
        eta = np.where(dentro, ks * etc, kbare * e)
        Dr = np.clip(Dr - P + eta, 0, taw)
        ism = dentro & mid[np.clip(k, 0, L - 1)]
        eta_m += np.where(ism, eta, 0); etc_m += np.where(ism, etc, 0)
    return eta_m / np.maximum(etc_m, 1e-6)


QX = "2311306"
res = {}
for esc in [1.00, 0.87]:
    Ef = E * esc
    print(f"\nET0 x {esc:.2f}: ET0 media jan-out = {Ef.sum(2).mean():.0f} mm")
    for c in CULT:
        P = np.stack([(isna_flor(c, np.full((NM, len(ANOS)), dd), Ef) >= 0.5).mean(1) for dd in DEC.values()], 1)
        lim = []
        for i in range(NM):
            oks = [j for j in range(len(ORD)) if P[i, j] >= 0.7]
            lim.append(oks[-1] if oks else -1)
        res[(esc, c)] = np.array(lim)
        qi = cods.index(QX)
        print(f"  {c}: Quixada data-limite = {ORD[lim[qi]] if lim[qi] >= 0 else 'nenhum'}; "
              f"mediana estadual do indice do ultimo decendio = {ORD[int(np.median([l for l in lim if l >= 0]))]}")
print("\nDeslocamento da data-limite (ET0 x0,87 menos x1,00), em decendios, nos 184 municipios:")
for c in CULT:
    d = res[(0.87, c)] - res[(1.00, c)]
    v = pd.Series(d).value_counts().sort_index()
    print(f"  {c}: {v.to_dict()}  | fracao que anda >= 1 decendio: {(d >= 1).mean():.0%}; >= 2: {(d >= 2).mean():.0%}")
