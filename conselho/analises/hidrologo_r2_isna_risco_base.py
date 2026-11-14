"""Hidrólogo — rodada 2: o ISNA (FAO-56) reduz o risco de base de um gatilho tipo Garantia-Safra DENTRO do ano?

O economista mostrou que o gatilho por chuva do IMERG separa os anos (AUC 0,83), mas dentro de um mesmo ano a AUC cai
para 0,59–0,63 (choque sistêmico). Na rodada 1 o ISNA ordenou melhor os municípios dentro do ano (ρ 0,136 contra 0,077).
Aqui: AUC por ano (quebra do milho >= 50%, rendimento por área plantada contra mediana móvel de 7 anos; painel do cético)
para ISNA, ISNA na floração e chuva de fev–mai. E um orçamento hídrico da entressafra (ET0 e chuva ago–dez, POWER CE),
para checar se cobertura viva anual na entressafra tem água.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")

pm = pd.read_parquet(AN / "cetico_painel_milho.parquet")[["cod", "ano", "an_y_plant", "fmam", "nver"]]
fa = pd.read_parquet(AN / "saidas" / "hidrologo_fao56_mun_ano.parquet")
fa = fa[(fa.cultura == "milho") & (fa.regra == "chuva")][["cod", "ano", "isna", "isna_flor"]]
pm["cod"] = pm.cod.astype(str)
fa["cod"] = fa.cod.astype(str)
d = pm.merge(fa, on=["cod", "ano"]).dropna()
d["q"] = (d.an_y_plant <= -0.5).astype(int)
print(f"painel: {len(d)} município-anos, {d.ano.nunique()} anos, quebra >= 50% em {d.q.mean():.1%}")
pred = {"isna": 1, "isna_flor": 1, "fmam": 1, "nver": -1}
print("AUC no painel:", {k: round(roc_auc_score(d.q, -s * d[k]), 3) for k, s in pred.items()})
rows = []
for ano, g in d.groupby("ano"):
    if g.q.sum() >= 5 and (1 - g.q).sum() >= 5:
        rows.append({"ano": ano, "n_q": int(g.q.sum()), **{k: roc_auc_score(g.q, -s * g[k]) for k, s in pred.items()}})
r = pd.DataFrame(rows)
print(f"\nAUC dentro do ano ({len(r)} anos com >= 5 quebras e >= 5 não-quebras):")
print(r[list(pred)].agg(["mean", "median"]).round(3).to_string())
print("ISNA > chuva em", int((r["isna"] > r["fmam"]).sum()), "de", len(r), "anos")
print(r.round(2).to_string(index=False))
# combinação simples: posto médio de ISNA e chuva
d["comb"] = d.groupby("ano").isna.rank(pct=True) + d.groupby("ano").fmam.rank(pct=True)
rc = [roc_auc_score(g.q, -g.comb) for a, g in d.groupby("ano") if a in set(r.ano)]
print(f"posto médio ISNA+chuva, AUC dentro do ano: média {np.mean(rc):.3f}")

print("\n=== orçamento hídrico da entressafra (POWER, média CE; valores mensais já em mm/mês) ===")
p = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
p["data"] = pd.to_datetime(p.data)
for v in ("ET0", "PRECTOTCORR"):
    s = p[p.variavel == v].set_index("data").valor
    s = s["1991":"2020"]
    ad = s[s.index.month.isin([8, 9, 10, 11, 12])]
    jj = s[s.index.month.isin([6, 7])]
    print(f"{v}: ago–dez {ad.groupby(ad.index.year).sum().mean():.0f} mm | jun–jul {jj.groupby(jj.index.year).sum().mean():.0f} mm | ano {s.groupby(s.index.year).sum().mean():.0f} mm")
