"""Designer - Analise 3d: alerta medido DESDE O PLANTIO (a data que o agricultor informa por audio).

Pergunta: o "% do normal" contado da data de plantio ate 30/abr (mesma janela de calendario nos outros anos do
municipio) separa melhor a quebra do milho do que o acumulado desde 1/jan? Corrige o "falso inicio" de 2016?
Proxy do plantio: dia seguinte ao 1o acumulado >= 20 mm em 3 dias desde 1/jan (ver designer_relogio_veranico.py).
Dados: saidas/designer_chuva_mun_diaria.parquet (IMERG V07 diario), ibge_pam_mun_anual.parquet.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import warnings

warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV

import numpy as np
import pandas as pd

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
chuva = pd.read_parquet(OUT / "designer_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(str)
s = pam[pam.produto.str.startswith("Milho (em gr") & (pam.ano >= 1990)].copy()
s["rp"] = np.where(s.area_plantada_ha >= 100, s.producao_t * 1000 / s.area_plantada_ha.replace(0, np.nan), np.nan)
s = s.sort_values(["cod", "ano"])
s["tend"] = s.groupby("cod")["rp"].transform(lambda v: v.rolling(7, center=True, min_periods=4).median())
s["quebra"] = (s.rp / s.tend < 0.5).astype(float).where((s.rp / s.tend).notna())
Q = s.set_index(["cod", "ano"]).quebra

anos = list(range(1998, 2026))
FIM = (4, 30)
# matriz [ano, dia do ano 0..119, municipio] de jan-abr
dias = 120
cube = np.stack([chuva.loc[pd.Timestamp(a, 1, 1):].iloc[:dias].values for a in anos])  # (anos, dias, mun)
rows = []
for k, a in enumerate(anos):
    for j, cod in enumerate(chuva.columns):
        x = cube[k, :, j]
        s3 = np.convolve(x, np.ones(3), "valid")
        on = np.where(s3 >= 20)[0]
        p = int(on[0]) + 3 if len(on) else None
        if p is None or p >= dias - 10:
            rows.append({"cod": cod, "ano": a, "pct_jan": np.nan, "pct_plantio": np.nan, "plantio": p})
            continue
        outros = np.delete(cube[:, :, j], k, axis=0)
        pct_plantio = x[p:].sum() / np.median(outros[:, p:].sum(1))
        pct_jan = x.sum() / np.median(outros.sum(1))
        rows.append({"cod": cod, "ano": a, "pct_jan": pct_jan, "pct_plantio": pct_plantio, "plantio": p + 1})
F = pd.DataFrame(rows).join(Q, on=["cod", "ano"]).dropna(subset=["quebra", "pct_plantio"])
print(f"{len(F)} municipio-anos com plantio proxy ate ~20/abr; base de quebra {10 * F.quebra.mean():.1f} em 10")
for lim in [0.6, 0.75]:
    for nome, col in [("desde 1/jan", "pct_jan"), ("desde o PLANTIO", "pct_plantio")]:
        cond = F[col] < lim
        p1, p0 = F.quebra[cond].mean(), F.quebra[~cond].mean()
        print(f"  chuva {nome:16s} < {lim:.0%} do normal: toca {cond.mean():5.1%} | com alerta {10 * p1:.1f}/10, "
              f"sem {10 * p0:.1f}/10 (razao {p1 / p0:.1f}x) | pega {F.quebra[cond].sum() / F.quebra.sum():.0%} das quebras")
for a in [2012, 2016]:
    g = F[F.ano == a]
    for nome, col in [("desde 1/jan", "pct_jan"), ("desde o PLANTIO", "pct_plantio")]:
        cond = g[col] < 0.75
        print(f"{a} {nome:16s}: alerta em {cond.mean():.0%} dos municipios; quebraram {g.quebra[cond].mean():.0%} dos alertados "
              f"e {g.quebra[~cond].mean():.0%} dos nao alertados; pega {g.quebra[cond].sum() / max(g.quebra.sum(), 1):.0%} das quebras do ano")
# AUC das duas medidas continuas
from sklearn.metrics import roc_auc_score
print(f"AUC (menos chuva = mais risco): desde 1/jan {roc_auc_score(F.quebra, -F.pct_jan):.3f} | "
      f"desde o plantio {roc_auc_score(F.quebra, -F.pct_plantio):.3f}")
