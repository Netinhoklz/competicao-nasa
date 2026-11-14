"""Inspeciona perfil (resolucao, nodata, faixa) das camadas GAEZ baixadas, por grupo."""
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import rasterio

sys.stdout.reconfigure(encoding="utf-8")
P = DADOS / "gaez"
s = pd.read_csv(P / "selecao.csv")
linhas = []
for _, r in s.groupby(["servico", "grupo"]).head(3).iterrows():
    f = P / r["arquivo"]
    if not f.exists():
        linhas.append({"arquivo": r["arquivo"], "status": "FALTA"})
        continue
    with rasterio.open(f) as ds:
        a = ds.read(1, out_shape=(ds.height // 4, ds.width // 4))
        u = np.unique(a)
        linhas.append({"servico": r["servico"], "grupo": r["grupo"], "var": str(r["variavel"])[:45], "un": r["unidade"],
                       "w": ds.width, "h": ds.height, "res": round(ds.res[0], 5), "dtype": ds.dtypes[0],
                       "nodata": ds.nodata, "min": a.min(), "max": a.max(), "n_uniq": len(u),
                       "uniq": u[:10].tolist() if len(u) <= 25 else ""})
pd.set_option("display.width", 260)
pd.set_option("display.max_colwidth", 60)
print(pd.DataFrame(linhas).to_string())
