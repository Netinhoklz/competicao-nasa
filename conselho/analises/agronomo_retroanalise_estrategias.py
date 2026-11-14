"""Agronomo do semiarido - 3a analise: retroanalise (1998-2025) de estrategias de semeadura no Ceara.

Pergunta: uma regra de troca de cultura acionada por dado NASA (data da 1a chuva de plantio no IMERG x data-limite
do "ZARC sintetico" do proprio municipio) reduz a chance de o agricultor familiar PERDER TUDO no ano?
"Perder tudo" = nenhuma cultura da estrategia com ISNA na floracao >= 0,5 (faixa em que o PAM mostra quebra
mediana de -58% a -72% do milho; ver agronomo_isna_zarc_sintetico.py, A2).

Estrategias (todas semeadas pela regra causal: 1o dia com >= 20 mm em 3 dias desde 1/jan; senao 30/abr):
 S0 atual      : milho + feijao-caupi no mesmo dia (consorcio tradicional)
 S1 escalonada : milho na 1a chuva + caupi 20 d depois (atraso que melhor explica o feijao do PAM, analise B1)
 S2 adaptativa : se a 1a chuva vier ate a data-limite do milho no municipio (risco <= 30% com ISNA 0,6) -> S1;
                 senao -> caupi + sorgo (sem milho).  A data-limite e calculada DEIXANDO O ANO DE FORA.
Limites: balde unico por cultura (sem competicao entre consorciadas); sem calor (ver B3); CAD 100 mm/m.
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

CULT = {"milho": (20, 30, 35, 25, 0.30, 1.20, 0.35, 0.6, 0.55), "caupi": (15, 20, 25, 15, 0.40, 1.05, 0.35, 0.5, 0.45),
        "sorgo": (20, 30, 40, 25, 0.30, 1.05, 0.55, 0.8, 0.55)}


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


c3 = np.zeros_like(R); c3[:, :, 2:] = R[:, :, 2:] + R[:, :, 1:-1] + R[:, :, :-2]
ok = c3 >= 20; ok[:, :, :2] = False; ok[:, :, 120:] = False
sow = np.where(ok.any(2), ok.argmax(2), 119)
sow = np.minimum(sow, ND - 140)

# data-limite do milho por municipio, deixando o ano de fora: ultimo decendio (em ordem) com P(ISNA>=0,6) >= 0,7
DEC = np.array([0, 10, 20, 31, 41, 51, 59, 69, 79, 90, 100, 110])
IND = np.stack([(isna_flor("milho", np.full((NM, NA), d)) >= 0.6) for d in DEC])  # (ndec, NM, NA)
soma = IND.sum(2, keepdims=True)
P_loyo = (soma - IND) / (NA - 1)  # (ndec, NM, NA)
okd = P_loyo >= 0.7
# ultimo decendio ok (indice); se nenhum, -1
ult = np.where(okd.any(0), len(DEC) - 1 - np.argmax(okd[::-1], axis=0), -1)
deadline = np.where(ult >= 0, DEC[np.clip(ult, 0, None)] + 9, -1)  # fim do decendio

im0 = isna_flor("milho", sow)
ic0 = isna_flor("caupi", sow)
ic20 = isna_flor("caupi", sow + 20)
is0 = isna_flor("sorgo", sow)
LIM = 0.5
s0 = (im0 >= LIM) | (ic0 >= LIM)
s1 = (im0 >= LIM) | (ic20 >= LIM)
usa_milho = sow <= deadline
s2 = np.where(usa_milho, s1, (ic0 >= LIM) | (is0 >= LIM))
seca = np.isin(ANOS, [2012, 2013, 2014, 2015, 2016])[None, :].repeat(NM, 0)
tarde = ~usa_milho

print(f"1a chuva de plantio apos a data-limite do milho em {tarde.mean():.0%} dos municipio-anos "
      f"({tarde[seca].mean():.0%} em 2012-2016)")
print(f"{'estrategia':14s} P(perder tudo) todos  2012-16  anos de chuva tardia   P(milho ISNA>=0,5 quando plantado)")
for nome, s in [("S0 atual", s0), ("S1 escalonada", s1), ("S2 adaptativa", s2)]:
    print(f"{nome:14s} {1 - s.mean():20.3f} {1 - s[seca].mean():8.3f} {1 - s[tarde].mean():22.3f}")
pm_ok = (im0 >= LIM)
print(f"milho plantado em ano 'cedo' (antes da data-limite): P(ISNA>=0,5)={pm_ok[usa_milho].mean():.2f}; "
      f"em ano 'tarde': {pm_ok[tarde].mean():.2f}  -> a regra evita plantar milho quando ele so da certo "
      f"{pm_ok[tarde].mean():.0%} das vezes")
print(f"caupi+sorgo nos anos 'tarde': P(ao menos um ISNA>=0,5)={((ic0 >= LIM) | (is0 >= LIM))[tarde].mean():.2f}")

# por ano (fracao de municipios que perdem tudo)
T = pd.DataFrame({"S0": 1 - s0.mean(0), "S1": 1 - s1.mean(0), "S2": 1 - s2.mean(0), "frac_tarde": tarde.mean(0)}, index=ANOS)
print("\nfracao de municipios que 'perdem tudo', por ano (anos com S0 >= 10%):")
print(T[T.S0 >= 0.10].round(2).to_string())
nomes = {str(x["id"]): x["nome"] for x in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}
print("\ndata-limite do milho (mediana dos anos, dia do ano) em municipios-exemplo:",
      {nomes[c]: int(np.median(deadline[cods.index(c)])) for c in cods if nomes.get(c) in ("Quixadá", "Tauá", "Crato", "Sobral", "Tianguá", "Iguatu")})
