"""Economista, rodada 2, analise 4: a regra canonica de alerta (IMERG desde 1/jan < 75% do normal em 30/abr) falhou em 2016-2025?

Motivo: em v2_economista_gatilho_smap.saida.txt a regra canonica disparou em 8% dos municipios em 2016 (70% em perda da
cesta) e em 59% em 2021 (7% em perda). Hipotese: chuva de janeiro (pre-estacao) contamina o acumulado.
Teste (as 3 janelas sao declaradas aqui, todas reportadas, nenhuma escolhida pelo resultado; corte fixo 75% do normal,
normal = mediana dos OUTROS anos 1998-2025):
  W1 1/jan-30/abr (canonica da QUADRA) | W2 1/fev-30/abr (mesmo portao, sem janeiro) | W3 1/fev-31/mai (fim da quadra)
Rotulos: quebra canonica do milho (L1) e cesta tipo Garantia-Safra perda >= 50% (L2). Placar por municipio-ano e por ANO
(ano ruim = >= 30% dos municipios em perda; o alerta "dispara no estado" se >= 30% dos municipios estao abaixo de 75%),
separado em 1998-2015 e 2016-2025. W2 e W3 sao EXPLORATORIAS: a regra canonica continua sendo W1 ate decisao da equipe.
Somente le arquivos. Saida: v2_economista_janela_alerta.saida.txt
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
A = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
SAIDA = A / "v2_economista_janela_alerta.saida.txt"
LINHAS = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LINHAS.append(s)


ch = pd.read_parquet(A / "estrategista_cache_chuva_mun_diaria.parquet")
ch.columns = ch.columns.astype(str)
anos = list(range(1998, 2026))


def pct_normal(i, f):
    ac = pd.DataFrame({a: ch.loc[f"{a}-{i}":f"{a}-{f}"].sum() for a in anos}).T
    o = ac * np.nan
    for a in anos:
        o.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    s = o.stack()
    s.index.names = ["ano", "cod"]
    return s.swaplevel()


JAN = {"W1 jan-abr (canonica)": ("01-01", "04-30"), "W2 fev-abr": ("02-01", "04-30"), "W3 fev-mai": ("02-01", "05-31")}
PN = {k: pct_normal(*v) for k, v in JAN.items()}
jan_share = pd.DataFrame({a: ch.loc[f"{a}-01-01":f"{a}-01-31"].sum() / ch.loc[f"{a}-01-01":f"{a}-05-31"].sum() for a in anos}).T.median(axis=1)
out("Fracao de janeiro na chuva jan-mai (mediana dos municipios), anos selecionados: " +
    ", ".join(f"{a}: {jan_share[a]:.2f}" for a in [1998, 2004, 2012, 2016, 2021, 2024, 2025]) + f" | mediana 1998-2025: {jan_share.median():.2f}")

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.ano.between(1998, 2025)].copy()
pam["cod"] = pam.cod_local.astype(str)


def loo_med(v):
    return np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])


q = pam[pam.produto.str.startswith("Milho (em") & (pam.area_plantada_ha >= 50)]
q = q.groupby(["cod", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum().sort_values(["cod", "ano"])
q["r"] = q.producao_t / q.area_plantada_ha
q["ref"] = q.groupby("cod").r.transform(lambda s: pd.Series(loo_med(s.values), index=s.index))
L1 = (q.r / q.ref).set_axis(pd.MultiIndex.from_frame(q[["cod", "ano"]])).dropna()
CESTA = ["Milho (em", "Feij", "Mandioca", "Arroz (em", "Algodão herbáceo"]
dc = pam[pam.produto.str.startswith(tuple(CESTA))].copy()
rec = dc[dc.ano.between(2019, 2025)]
preco = rec.groupby("produto").valor_mil_moeda.sum() / rec.groupby("produto").producao_t.sum()
dc["v"] = dc.producao_t * dc.produto.map(preco)
V = dc.groupby(["cod", "ano"]).v.sum().reset_index().sort_values(["cod", "ano"])
V = V[V.v > 0]
V["ref"] = V.groupby("cod").v.transform(lambda s: pd.Series(loo_med(s.values), index=s.index))
L2 = (V.v / V.ref).set_axis(pd.MultiIndex.from_frame(V[["cod", "ano"]])).dropna()

for rot_l, lab in [("L1 quebra canonica do milho", L1), ("L2 cesta tipo GS, perda >= 50%", L2)]:
    out(f"\n== {rot_l} ==")
    for per, (a0, a1) in [("1998-2015", (1998, 2015)), ("2016-2025", (2016, 2025)), ("1998-2025", (1998, 2025))]:
        for k, pn in PN.items():
            D = pd.concat([pn.rename("pn"), (lab < 0.5).rename("y")], axis=1).dropna()
            D = D[D.index.get_level_values("ano").to_series().between(a0, a1).values]
            D["y"] = D.y.astype(bool); D["g"] = D.pn < 0.75
            an = D.index.get_level_values("ano")
            fy = D.groupby(an)[["y", "g"]].mean()
            ruim, disp = fy.y >= 0.30, fy.g >= 0.30
            dentro = [roc_auc_score(D.y[an == a], -D.pn[an == a]) for a in fy.index if 0.1 <= fy.y[a] <= 0.9]
            out(f"  {per} {k:22s} paga {100 * D.g.mean():4.1f}% | perdas pagas {100 * D.g[D.y].mean():4.1f}% | "
                f"pagamentos sem perda {100 * (1 - D.y[D.g].mean()):4.1f}% | AUC {roc_auc_score(D.y, -D.pn):.2f} | dentro do ano {np.mean(dentro):.2f} | "
                f"anos ruins {list(fy.index[ruim])}: pegou {int((ruim & disp).sum())} de {int(ruim.sum())}; alarme falso em {int((~ruim & disp).sum())} de {int((~ruim).sum())} "
                f"{list(fy.index[~ruim & disp])}")

SAIDA.write_text("\n".join(LINHAS), encoding="utf-8")
