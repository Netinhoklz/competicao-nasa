"""Confere escala da produtividade real (res06, 2010) em regioes de referencia."""
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


def ler(a, bbox):
    with rasterio.open(G / a) as ds:
        w = from_bounds(*bbox, transform=ds.transform).round_offsets().round_lengths()
        x = ds.read(1, window=w).astype("float64"); tr = ds.window_transform(w)
    return x, tr


REG = {"Iowa (EUA)": (-96.6, 40.4, -90.1, 43.5), "Ceará": BBOX_CE, "Índia central": (74, 18, 82, 24),
       "Paraná (BR)": (-54.6, -26.7, -48.0, -22.5), "Mato Grosso (BR)": (-61, -18, -50, -8)}
for crop in ["Maize", "Soybean", "Cotton", "Cassava"]:
    fy = sel[(sel.servico == "res06") & (sel.cultura == crop) & (sel.variavel == "Yield")].arquivo.iloc[0]
    fp = sel[(sel.servico == "res06") & (sel.cultura == crop) & (sel.variavel == "Production")].arquivo.iloc[0]
    for nome, bb in REG.items():
        y, tr = ler(fy, bb)
        p, _ = ler(fp, bb)
        if nome == "Ceará":
            M = geometry_mask(list(ceara_gdf().geometry), out_shape=y.shape, transform=tr, invert=True)
            y = np.where(M, y, 0); p = np.where(M, p, 0)
        ok = (y > 0) & (p > 0)
        area_ha = (p[ok] * 1000 / y[ok]).sum()  # producao 1000 t / (t/ha)
        print(f"{crop:8s} {nome:18s} yield médio simples={y[ok].mean():6.2f} t/ha | produção total={p[ok].sum()/1000:8.3f} Mt | "
              f"área implícita={area_ha/1e6:6.3f} Mha | yield ponderado={p[ok].sum()*1000/area_ha if area_ha else np.nan:5.2f}")
