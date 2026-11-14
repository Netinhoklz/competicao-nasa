"""Checa interpretacao do res07 (razao de produtividade) e da serie anual de LGP no Ceara."""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds
from rasterio.features import geometry_mask

sys.stdout.reconfigure(encoding="utf-8")
G = DADOS / "gaez"
sel = pd.read_csv(G / "selecao.csv")
ce = ceara_gdf()


def ler(a, bbox=BBOX_CE):
    with rasterio.open(G / a) as ds:
        w = from_bounds(*bbox, transform=ds.transform).round_offsets().round_lengths()
        x = ds.read(1, window=w).astype("float32"); tr = ds.window_transform(w); nd = ds.nodata
    if nd is not None and not np.isnan(nd):
        x[x == nd] = np.nan
    return x, tr


x, tr = ler(sel[(sel.servico == "res05") & (sel.cultura == "Maize") & (sel.codigo == "si_seq_alto")].arquivo.iloc[0])
M = geometry_mask(list(ce.geometry), out_shape=x.shape, transform=tr, invert=True)
for crop5, crop6 in [("Maize", "Maize"), ("Cotton", "Cotton"), ("Cassava", "Cassava"), ("Sorghum", "Sorghum")]:
    y6, _ = ler(sel[(sel.servico == "res06") & (sel.cultura == crop6) & (sel.variavel == "Yield")].arquivo.iloc[0])
    r7f = sel[(sel.servico == "res07") & (sel.cultura == crop6)]
    r7, _ = ler(r7f.arquivo.iloc[0]) if len(r7f) else (None, None)
    out = {"crop": crop6, "yield real 2010 media (t/ha)": float(np.nanmean(np.where(y6 > 0, y6, np.nan)[M]))}
    for cod in ["yld_seq_alto", "yld_seq_baixo", "yld_lav_seq_alto"]:
        f = sel[(sel.servico == "res05") & (sel.cultura == crop5) & (sel.codigo == cod)]
        if len(f):
            ya, _ = ler(f.arquivo.iloc[0])
            out[cod + " (t/ha)"] = float(np.nanmean(np.where(ya > 0, ya, np.nan)[M]) / 1000)
    if r7 is not None:
        v = r7[M]; v = v[~np.isnan(v)]
        out["res07 codigos"] = pd.Series(v.astype(int)).value_counts().to_dict()
        out["res07 arquivo"] = r7f.arquivo.iloc[0]
    print(out)

# serie LGP anual Ceara
an = sel[sel.codigo == "lgp_anual"].sort_values("ano")
vals = []
for _, r in an.iterrows():
    a, _ = ler(r.arquivo)
    v = a[M]
    vals.append((int(r.ano), float(np.nanmean(v)), float(np.nanmin(v)), float(np.nanpercentile(v, 10))))
print(pd.DataFrame(vals, columns=["ano", "media", "min", "p10"]).set_index("ano").T.round(0).to_string())
