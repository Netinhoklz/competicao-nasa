"""Agronomo do semiarido - 4a analise: QUANDO plantar? regras de semeadura x "falso inicio" (retroanalise 1998-2025).

Motivacao: em agronomo_retroanalise_estrategias.py a 1a chuva de plantio (>= 20 mm em 3 dias) quase nunca vem
"tarde demais" (1% dos municipio-anos); as quebras de 2010/2012/2013/2016 vem do FALSO INICIO (chuva de pre-estacao
seguida de veranico). Entao a decisao certa e "plantar nesta chuva ou esperar o solo encher?".

Regras (todas causais, so usam o passado; fallback 30/abr):
 R1 1a chuva >= 20 mm/3 d (pratica atual; analise B1 mostra que o milho do PAM se comporta assim)
 R2 >= 30 mm/3 d       R3 >= 50 mm em 10 d
 R4 agua armazenada no solo >= 30 mm (balde de solo nu, CAD 60 mm)  <- equivalente a ler SMAP L4 zona da raiz
 R5 agua armazenada >= 45 mm
 R6 R1 mas nao antes de 1/fev     R7 R1 mas nao antes de 15/fev
Saida: P(perder tudo) com milho + caupi no mesmo dia; ISNA do milho; rendimento relativo esperado do milho pela
curva empirica ISNA -> anomalia do PAM (analise A2); CVaR10. Politica aprendida: cada municipio escolhe a regra com
menor P(perder tudo) nos OUTROS anos (deixando o ano de fora) e e avaliado no ano retido.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import json
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

warnings.filterwarnings("ignore")
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
NM, NA = len(cods), len(ANOS)
R = np.zeros((NM, NA, ND), np.float32); E = np.zeros_like(R)
for j, a in enumerate(ANOS):
    idx = pd.date_range(f"{a}-01-01", periods=ND, freq="D")
    R[:, j] = chuva.reindex(idx)[cods].fillna(0).values.T
    E[:, j] = et0.reindex(idx)[cods].interpolate().bfill().values.T

CULT = {"milho": (20, 30, 35, 25, 0.30, 1.20, 0.35, 0.6, 0.55), "caupi": (15, 20, 25, 15, 0.40, 1.05, 0.35, 0.5, 0.45)}


def isna_flor(c, sow):
    li, ld, lm, ll, ki, km, ke, zr, pp = CULT[c]
    kc = np.concatenate([np.full(li, ki), np.linspace(ki, km, ld), np.full(lm, km), np.linspace(km, ke, ll)]).astype(np.float32)
    mid = np.zeros(len(kc), bool); mid[li + ld:li + ld + lm] = True
    L = len(kc); taw = 100.0 * zr; raw = pp * taw
    Dr = np.full(sow.shape, taw, np.float32); a_ = np.zeros(sow.shape, np.float32); b_ = np.zeros_like(a_)
    for d in range(ND):
        k = d - sow; dentro = (k >= 0) & (k < L)
        kci = np.where(dentro, kc[np.clip(k, 0, L - 1)], 0.0)
        ks = np.where(Dr <= raw, 1.0, np.clip((taw - Dr) / (taw - raw), 0, 1))
        etc = kci * E[:, :, d]
        eta = np.where(dentro, ks * etc, 0.3 * np.clip((taw - Dr) / taw, 0, 1) * E[:, :, d])
        Dr = np.clip(Dr - R[:, :, d] + eta, 0, taw)
        ism = dentro & mid[np.clip(k, 0, L - 1)]
        a_ += np.where(ism, eta, 0); b_ += np.where(ism, etc, 0)
    return a_ / np.maximum(b_, 1e-6)


def primeiro(cond, inicio=0, fim=120):
    c = cond.copy(); c[:, :, :inicio] = False; c[:, :, fim:] = False
    return np.where(c.any(2), c.argmax(2), 119)


c3 = np.zeros_like(R); c3[:, :, 2:] = R[:, :, 2:] + R[:, :, 1:-1] + R[:, :, :-2]
c10 = np.cumsum(R, 2); c10[:, :, 10:] = c10[:, :, 10:] - c10[:, :, :-10]
# agua armazenada num perfil de solo nu (CAD 60 mm), evaporacao 0,3*ET0 limitada pela secura
W = np.zeros((NM, NA, ND), np.float32); w = np.zeros((NM, NA), np.float32)
for d in range(ND):
    w = np.clip(w + R[:, :, d] - 0.3 * (w / 60.0) * E[:, :, d], 0, 60); W[:, :, d] = w
REG = {"R1 >=20mm/3d (atual)": primeiro(c3 >= 20, 2), "R2 >=30mm/3d": primeiro(c3 >= 30, 2),
       "R3 >=50mm/10d": primeiro(c10 >= 50, 10), "R4 solo >=30mm (SMAP)": primeiro(W >= 30),
       "R5 solo >=45mm (SMAP)": primeiro(W >= 45), "R6 R1 apos 1/fev": primeiro(c3 >= 20, 31),
       "R7 R1 apos 15/fev": primeiro(c3 >= 20, 45)}
# hibridas: em janeiro so planta com o solo cheio (SMAP); a partir de fevereiro, regra da chuva
REG["R8 fev OU solo>=45mm em jan"] = np.minimum(REG["R6 R1 apos 1/fev"], REG["R5 solo >=45mm (SMAP)"])
REG["R9 fev OU >=50mm/10d em jan"] = np.minimum(REG["R6 R1 apos 1/fev"], REG["R3 >=50mm/10d"])
# curva empirica ISNA floracao do milho -> anomalia mediana do PAM (agronomo_isna_zarc_sintetico.py, A2)
BORDAS = np.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
ANOM = np.array([-0.717, -0.629, -0.580, -0.408, -0.223, -0.025, -0.002, 0.242])
seca = np.isin(ANOS, [2010, 2012, 2013, 2014, 2015, 2016])
res, FALHA = [], {}
for nome, sow in REG.items():
    im = isna_flor("milho", sow); ic = isna_flor("caupi", sow)
    falha = (im < 0.5) & (ic < 0.5); FALHA[nome] = falha
    rel = 1 + ANOM[np.searchsorted(BORDAS, im, side="left")]
    piores = np.sort(rel.ravel())[: int(0.1 * rel.size)]
    res.append({"regra": nome, "semeadura mediana (dia)": int(np.median(sow) + 1),
                "P(perder tudo)": falha.mean(), "P(perder tudo) secas 2010,12-16": falha[:, seca].mean(),
                "P(milho ISNA>=0,6)": (im >= 0.6).mean(), "milho rend. relativo esperado": rel.mean(),
                "CVaR10 milho": piores.mean(), "plantou depois de 31/mar": (sow >= 90).mean()})
print(pd.DataFrame(res).round(3).to_string(index=False))

# politica aprendida (deixando o ano de fora): por municipio, regra com menor P(perder tudo) nos outros anos
nomes_r = list(REG)
Fz = np.stack([FALHA[n] for n in nomes_r])  # (nr, NM, NA)
loyo = (Fz.sum(2, keepdims=True) - Fz) / (NA - 1)
esc = loyo.argmin(0)  # (NM, NA)
pol = np.take_along_axis(Fz, esc[None], 0)[0]
print(f"\npolitica por municipio (LOYO): P(perder tudo)={pol.mean():.3f}; secas={pol[:, seca].mean():.3f}; "
      f"regras escolhidas: { {nomes_r[k]: int(v) for k, v in zip(*np.unique(esc, return_counts=True))} }")
print("\nfracao de municipios que perdem tudo por ano de seca:")
print(pd.DataFrame({n: FALHA[n].mean(0) for n in ["R1 >=20mm/3d (atual)", "R4 solo >=30mm (SMAP)", "R5 solo >=45mm (SMAP)",
                                                   "R6 R1 apos 1/fev", "R8 fev OU solo>=45mm em jan"]} | {"politica LOYO": pol.mean(0)}, index=ANOS)
      .loc[[2001, 2005, 2010, 2012, 2013, 2014, 2015, 2016, 2021]].round(2).to_string())
