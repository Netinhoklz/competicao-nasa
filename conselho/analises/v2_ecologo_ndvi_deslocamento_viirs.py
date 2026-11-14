"""Ecologo (rodada 2, dados novos) - Analise 4 (checagem curta): o "deslocamento nao explicado" do NDVI desde 2020
(M6: MODIS fev-mai +0,053 mais verde para a mesma chuva; cetico_deriva_ndvi_modis_landsat.saida.txt) aparece tambem
no VIIRS, que e outro sensor em outra plataforma (S-NPP)? Importa para o indice de combustivel: se o VIIRS tambem
desloca, o combustivel F_t de 2026 (+0,98 dp) carrega esse deslocamento.
Metodo identico nos dois sensores: NDVI estadual fev-mai x chuva IMERG fev-mai (derivados/imerg_ce_mensal), reta
ajustada SO em 2012-2019 (anos em que os dois sensores existem antes do deslocamento), residuo 2020-2026.
Unidade = ano (n pequeno: 8 anos de ajuste). E so checagem, nao vai para o pitch.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd

vi = pd.read_parquet(DERIV / "viirs_ndvi_ce_mensal.parquet")
mo = pd.read_parquet(DERIV / "modis_ce_mensal.parquet")
mo = mo[mo.variavel == "ndvi"]
im = pd.read_parquet(DERIV / "imerg_ce_mensal.parquet")
im = im[im.variavel == "precip_total"]


def fmam(df):
    s = df.set_index(pd.to_datetime(df.data)).valor
    s = s[s.index.month.isin([2, 3, 4, 5])]
    c = s.groupby(s.index.year).count()
    return s.groupby(s.index.year).mean().where(c == 4)


T = pd.DataFrame({"viirs": fmam(vi), "modis": fmam(mo)})
ch = im.set_index(pd.to_datetime(im.data)).valor
ch = ch[ch.index.month.isin([2, 3, 4, 5])]
T["chuva"] = ch.groupby(ch.index.year).sum()
T = T.loc[2012:2026]
for s in ("viirs", "modis"):
    a = T.loc[2012:2019].dropna(subset=[s, "chuva"])
    b = np.polyfit(a.chuva, a[s], 1)
    T[s + "_res"] = T[s] - np.polyval(b, T.chuva)
    r0 = T.loc[2012:2019, s + "_res"]
    r1 = T.loc[2020:2026, s + "_res"]
    print(f"{s}: reta 2012-2019 NDVI = {b[1]:.3f} + {b[0] * 100:.4f} x chuva/100 mm | residuo 2012-2019 dp {r0.std():.3f};"
          f" media 2020-2026 {r1.mean():+.3f} (n={r1.notna().sum()}; z = {r1.mean() / r0.std():+.1f} dp do ajuste)")
T["viirs_menos_modis"] = T.viirs - T.modis
print(T.round(3).to_string())
print(f"VIIRS - MODIS: media 2012-2019 {T.loc[2012:2019, 'viirs_menos_modis'].mean():+.3f};"
      f" 2020-2026 {T.loc[2020:2026, 'viirs_menos_modis'].mean():+.3f}")
