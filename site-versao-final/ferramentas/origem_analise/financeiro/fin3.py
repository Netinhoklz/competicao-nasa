"""Calibração da faixa: que par de quantis de 1998–2015 cobre 80% de 2016–2025? E faixa por razão ao normal agrupada."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.argv = [str(Path(__file__))]
exec(open(Path(__file__).parent / "fin.py", encoding="utf8").read().split("# ---------------- custo CONAB")[0])
X = M[M.produto.isin(["Milho", "Feijão", "Mandioca"])]
for lo, hi in [(.1, .9), (.05, .95), (0, 1)]:
    rows = []
    for (p, c), g in X.groupby(["produto", "cod_mun"]):
        tr, te = g[g.ano <= 2015].R, g[g.ano >= 2016].R
        if len(tr) >= 8 and len(te) >= 5:
            rows.append((p, ((te >= tr.quantile(lo)) & (te <= tr.quantile(hi))).mean()))
    print(f"faixa P{lo*100:.0f}–P{hi*100:.0f} de 1998–2015 cobre de 2016–2025:", pd.DataFrame(rows, columns=["p", "c"]).groupby("p").c.mean().round(3).to_dict())
# faixa "agrupada": quantis da razão ao normal da mesorregião (mais anos, mais municípios) x mediana do município
REG = REFM.mesorregiao.to_dict()
X = X.assign(meso=X.cod_mun.map(REG))
T = X[X.ano <= 2015].copy()
T["rel"] = T.R / T.groupby(["produto", "cod_mun"]).R.transform("median")
qlo = T.groupby(["produto", "meso"]).rel.quantile(.1)
qhi = T.groupby(["produto", "meso"]).rel.quantile(.9)
rows = []
for (p, c), g in X.groupby(["produto", "cod_mun"]):
    tr, te = g[g.ano <= 2015], g[g.ano >= 2016]
    if len(tr) >= 8 and len(te) >= 5:
        md, k = tr.R.median(), (p, g.meso.iloc[0])
        lo, hi = md * qlo[k], md * qhi[k]
        rows.append((p, ((te.R >= lo) & (te.R <= hi)).mean()))
print("faixa P10–P90 da razão ao normal da mesorregião × mediana do município:", pd.DataFrame(rows, columns=["p", "c"]).groupby("p").c.mean().round(3).to_dict())
