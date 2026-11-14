"""Arquiteto-chefe, versao final: IC90 por bootstrap de ANOS para a carteira 1/3 (definicao canonica do juiz,
juiz_carteira_definicao_canonica.py, definicao b) e placar do alerta unico em Quixada. So le arquivos."""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import DERIV  # noqa

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
rng = np.random.default_rng(1)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[(pam.ano >= 1998) & (pam.ano <= 2025)]


def canonica(pref, tirar_repetido=False):
    p = pam[pam.produto.str.startswith(pref) & (pam.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha
    p = p.sort_values(["cod_local", "ano"])
    if tirar_repetido:
        p = p[~(p.groupby("cod_local").r.diff().abs() < 1e-9)]
    out = []
    for cod, g in p.groupby("cod_local"):
        r = g.r.values
        med = np.array([np.median(np.delete(r, i)) if len(r) > 1 else np.nan for i in range(len(r))])
        out.append(pd.DataFrame({"cod_local": cod, "ano": g.ano.values, "razao": r / med}))
    return pd.concat(out).set_index(["cod_local", "ano"]).razao


def met(s):
    return s[s <= s.quantile(0.10)].mean(), (s < 0.5).mean()


for rot, tr in [("canonica (b)", False), ("sem anos repetidos da mandioca (c)", True)]:
    Y = pd.DataFrame({"milho": canonica("Milho (em"), "feijao": canonica("Feij"),
                      "mandioca": canonica("Mandioca", tirar_repetido=tr)}).dropna().reset_index()
    Y["mf"] = Y[["milho", "feijao"]].mean(axis=1)
    Y["c13"] = Y[["milho", "feijao", "mandioca"]].mean(axis=1)
    anos = Y.ano.unique()
    G = {a: Y[Y.ano == a] for a in anos}
    bs = {k: [] for k in ["milho", "mf", "c13", "dif"]}
    bp = {k: [] for k in ["milho", "c13"]}
    for _ in range(2000):
        B = pd.concat([G[a] for a in rng.choice(anos, len(anos))])
        for k in ["milho", "mf", "c13"]:
            bs[k].append(met(B[k])[0])
        bs["dif"].append(met(B.c13)[0] - met(B.milho)[0])
        bp["milho"].append(met(B.milho)[1]); bp["c13"].append(met(B.c13)[1])
    print(f"\n{rot}: n={len(Y)} municipio-anos, {Y.cod_local.nunique()} municipios, {len(anos)} anos")
    for k, nome in [("milho", "100% milho"), ("mf", "milho+feijao"), ("c13", "1/3 cada")]:
        c, p = met(Y[k])
        lo, hi = np.percentile(bs[k], [5, 95])
        print(f"  {nome:13s} CVaR10={c:.3f} IC90 ano [{lo:.3f},{hi:.3f}]  P(<0,5)={p:.3f}")
    print(f"  ganho de CVaR10 (1/3 - milho): IC90 [{np.percentile(bs['dif'], 5):+.3f},{np.percentile(bs['dif'], 95):+.3f}]")
    print(f"  P(<0,5) milho IC90 [{np.percentile(bp['milho'], 5):.3f},{np.percentile(bp['milho'], 95):.3f}] | "
          f"1/3 IC90 [{np.percentile(bp['c13'], 5):.3f},{np.percentile(bp['c13'], 95):.3f}]")
    # quais anos formam a cauda do milho (10% piores)
    cauda = Y[Y.milho <= Y.milho.quantile(0.10)]
    print("  anos que formam a cauda de 10% do milho (contagem de municipio-anos):",
          cauda.ano.value_counts().head(8).to_dict())
