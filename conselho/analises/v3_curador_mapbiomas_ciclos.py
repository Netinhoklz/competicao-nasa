"""Curador de bases (v3), teste G: MapBiomas (estatisticas abertas da colecao 11, brasil.mapbiomas.org/estatisticas,
baixadas em 14/11/2026) no Ceara.

G1. Os produtos agricolas finos (numero anual de ciclos a 10 m 2017-2025; uso agricola de 2a safra) cobrem o Ceara?
G2. Cobertura do semiarido cearense (estado): "Outras lavouras temporarias" x "Mosaico de usos" x pastagem, 1985-2024,
    contra a area plantada de lavouras temporarias do IBGE PAM no CE (todos os municipios do CE; o semiarido cobre
    quase todo o estado). Se o MapBiomas pusesse o rocado em "lavoura temporaria", as duas series andariam juntas.
G3. Irrigacao mapeada no CE (colecao 11).
So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
M = DADOS / "complementares" / "mapbiomas"

print("=" * 20, "G1. Produtos agricolas finos do MapBiomas no Ceara", "=" * 20)
c = pd.read_excel(M / "MAPBIOMAS-BRAZIL-ANNUAL-NUMBER-OF-CROP-CYCLES-MUNICIPALITY_10M.xlsx", "ANNUAL_CROP_CYCLES__2017_2025")
s = pd.read_excel(M / "MAPBIOMAS-BRAZIL-AGRICULTURE-USE-SECOND-CROP-MUNICIPALITY.xlsx", "AGRICULTURE_USE_2ND_CROP")
for nome, d in [("ciclos 10 m", c), ("2a safra", s)]:
    ce = d[d.GEOCODE.astype(str).str.startswith("23")]
    ne = d[d.GEOCODE.astype(str).str[:2].isin(["21", "22", "23", "24", "25", "26", "27", "28", "29"])]
    print(f"  {nome}: municipios no Brasil {d.GEOCODE.nunique()} | no NE {ne.GEOCODE.nunique()} | no CE {ce.GEOCODE.nunique()}")

print("\n" + "=" * 20, "G2. Semiarido do CE (colecao 11): classes agricolas x PAM", "=" * 20)
d = pd.read_excel(M / "MAPBIOMAS_BRAZIL-COVERAGE_STATISTIC-COL.11-SEMIARID_STATE_BIOME.xlsx", "COVERAGE_COL11_SEMIARID")
ce = d[d.state.astype(str).str.contains("Cear")]
anos = [f"y{a}" for a in range(1985, 2025)]
cl = ce.groupby("class_level_4")[anos].sum()
sel = [k for k in cl.index if any(t in k for t in ["Temporary", "Mosaic", "Pasture", "Perennial", "Soybean"])]
print((cl.loc[sel, ["y1985", "y2000", "y2010", "y2016", "y2024"]] / 1000).round(0).to_string(), "\n(mil ha)")
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
temp = ["Milho", "Feij", "Mandioca", "Sorgo", "Algod", "Arroz", "Fava", "Amendoim", "Mamona"]
p = pam[pam.produto.str.startswith(tuple(temp))].groupby("ano").area_plantada_ha.sum()
lav = cl.loc[[k for k in cl.index if "Temporary" in k or "Soybean" in k]].sum()
mos = cl.loc[[k for k in cl.index if "Mosaic" in k]].sum()
lav.index = mos.index = [int(a[1:]) for a in anos]
J = pd.DataFrame({"pam_plantada": p, "mb_lav_temp": lav, "mb_mosaico": mos}).dropna()
print(f"anos em comum: {J.index.min()}-{J.index.max()} (n={len(J)})")
print("razao media MapBiomas lavoura temporaria / PAM:", round((J.mb_lav_temp / J.pam_plantada).median(), 2))
print("Pearson das variacoes ano a ano (diferenca primeira): lavoura temp x PAM =",
      round(J.mb_lav_temp.diff().corr(J.pam_plantada.diff()), 2), "| mosaico x PAM =",
      round(J.mb_mosaico.diff().corr(J.pam_plantada.diff()), 2))
print((J.loc[[1985, 1995, 2005, 2012, 2016, 2020, 2024] if 2024 in J.index else J.index[::5]] / 1000).round(0).to_string(), "\n(mil ha)")

print("\n" + "=" * 20, "G3. Irrigacao mapeada (colecao 11), CE", "=" * 20)
ir = pd.read_excel(M / "MAPBIOMAS-BRAZIL-IRRIGATION-SYSTEMS-MUNICIPALITY-COLLECTION_11.xlsx", "IRRIGATION_SYSTEMS")
ir = ir[ir.MUNICIPALITY_GEOCODE.astype(str).str.startswith("23")]
print((ir.groupby(["IRRIGATION_CLASS_NAME", "AGRICULTURE_CLASS_NAME"])[["y2000", "y2010", "y2020", "y2024"]].sum() / 1000).round(1).to_string(), "\n(mil ha)")
print("maiores areas irrigadas 2024 (ha):", ir.groupby("MUNICIPALITY")["y2024"].sum().sort_values(ascending=False).head(6).round(0).to_dict())
