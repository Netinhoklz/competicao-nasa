"""Curador de bases (v3), teste H: IBGE Censo Agropecuario 2017 (SIDRA, API servicodados v3) no Ceara.

Tabela 6861: estabelecimentos com recursos hidricos por tipo (inclui "Pocos e/ou cisternas - cisternas").
Tabela 6778: numero total de estabelecimentos. Baixadas por curl em 14/11/2026 para
E:/campeonato-nasa/dados/complementares/ibge_censo_agro/sidra_6861_ce_municipios.json e sidra_6778_ce_municipios.json.
Mede a fracao de estabelecimentos com cisterna por municipio (o M7 pergunta "volume de barreiro ou cisterna";
o Censo da a existencia, nao o volume). Cruza com o risco de base de quebra do milho no PAM (fracao de anos com
razao < 0,5, receita canonica simplificada: mediana dos outros anos).
"""
import sys
import json
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
C = DADOS / "complementares" / "ibge_censo_agro"


def ler(f):
    d = json.load(open(C / f, encoding="utf-8"))
    lin = []
    for var in d:
        for res in var["resultados"]:
            cat = {k: list(v.values())[0] for cl in res["classificacoes"] for k, v in [(cl["nome"], cl["categoria"])]}
            for s in res["series"]:
                v = s["serie"]["2017"]
                lin.append({"cod": s["localidade"]["id"], "nome": s["localidade"]["nome"],
                            "valor": pd.to_numeric(v, errors="coerce"), **cat})
    return pd.DataFrame(lin)


r = ler("sidra_6861_ce_municipios.json")
t = ler("sidra_6778_ce_municipios.json").groupby("cod").valor.sum().rename("estab_total")
tipo = [k for k in r.columns if "recurso" in k.lower()][0]
pv = r.pivot_table(index="cod", columns=tipo, values="valor", aggfunc="sum")
cist = [k for k in pv.columns if k.endswith("cisternas")][0]
X = pv[[cist, "Total"]].join(t)
X["frac_cisterna"] = X[cist] / X.estab_total
X["frac_algum_recurso"] = X["Total"] / X.estab_total
print(f"municipios: {len(X)} | estabelecimentos no CE: {X.estab_total.sum():,.0f} | com cisterna: {X[cist].sum():,.0f}"
      f" ({X[cist].sum() / X.estab_total.sum():.0%})")
print("fracao com cisterna por municipio: p10 {:.0%}, mediana {:.0%}, p90 {:.0%}".format(*X.frac_cisterna.quantile([.1, .5, .9])))
nomes = r.groupby("cod").nome.first()
q = X.loc[[c for c in X.index if nomes[c].startswith("Quixad")]]
print("Quixada:", q[[cist, "estab_total", "frac_cisterna"]].round(3).to_dict("records"))

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
p = pam[pam.produto.str.startswith("Milho (em gr") & pam.ano.between(1998, 2025) & (pam.area_plantada_ha >= 50)].copy()
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha
p["ref"] = p.groupby("cod_local").r.transform("median")
p["quebra"] = (p.r / p.ref < 0.5)
risco = p.groupby(p.cod_local.astype(str).str[:7]).quebra.mean()
X = X.join(risco.rename("risco_quebra_milho"))
print(f"Spearman(fracao com cisterna, risco de quebra do milho 1998-2025) = "
      f"{X.frac_cisterna.corr(X.risco_quebra_milho, method='spearman'):.2f} (n={X.risco_quebra_milho.notna().sum()})")
print("nota: a tabela 6861 tem uma so categoria 'cisternas' (nao separa consumo humano de producao) e da a",
      "existencia, nao o volume. Serve como camada de contexto do M7, nao como dado de agua para salvamento.")
