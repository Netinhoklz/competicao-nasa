"""Curador de bases (v3), teste H2: o IBGE ja faz um "previsor por portao" - o LSPA (Levantamento Sistematico da
Producao Agricola, SIDRA tabela 6588, estimativa mensal por UF desde set/2006). Quanto o LSPA de cada mes ja sabe
da safra final do Ceara, e quanto a chuva da NASA (IMERG) acumulada ate o fim do mesmo mes sabe?

Alvo: producao final de milho (1a safra no LSPA; "Milho (em grao)" na PAM municipal somada no estado), 2007-2025.
Escala: log(valor / mediana dos OUTROS anos da producao final). Estatistica: Spearman entre anos (n ~ 19) e
acerto do sinal nos anos de quebra (producao final < 50% da mediana).
Fonte: E:/campeonato-nasa/dados/complementares/ibge_lspa/sidra_6588_lspa_ne5_ufs.json (API servicodados v3, 14/11/2026).
Atencao: o LSPA do mes m sai no inicio do mes m+1, e chuva ate o fim do mes m esta disponivel no mesmo dia (IMERG Late).
"""
import sys
import json
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
L = DADOS / "complementares" / "ibge_lspa"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"

d = json.load(open(L / "sidra_6588_lspa_ne5_ufs.json", encoding="utf-8"))
lin = []
for var in d:
    for res in var["resultados"]:
        prod = list(res["classificacoes"][0]["categoria"].values())[0]
        for s in res["series"]:
            for per, v in s["serie"].items():
                lin.append({"var": var["variavel"], "produto": prod, "uf": s["localidade"]["nome"],
                            "per": per, "valor": pd.to_numeric(v, errors="coerce")})
X = pd.DataFrame(lin)
X["ano_ref"] = X.per.str[:4].astype(int)
X["mes"] = X.per.str[4:].astype(int)
ce = X[(X.uf == "Ceará") & X.produto.str.contains("Milho") & (X["var"] == "Produção")]
print("LSPA CE milho 1a safra, producao: periodos", ce.per.min(), "a", ce.per.max())

# a estimativa do mes m do ANO a refere-se a safra do ano a (o LSPA estima o ano civil corrente)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
fin = pam[pam.produto.str.startswith("Milho (em gr")].groupby("ano").producao_t.sum()
anos = [a for a in range(2007, 2026) if a in fin.index]
ref = {a: np.median([fin[b] for b in anos if b != a]) for a in anos}
y = pd.Series({a: np.log(fin[a] / ref[a]) for a in anos})
queb = [a for a in anos if fin[a] < 0.5 * ref[a]]
print("anos de quebra estadual (producao final < 50% da mediana):", queb)

chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet").mean(axis=1)  # media dos municipios
tab = []
for m in [1, 2, 3, 4, 5, 6]:
    e = ce[ce.mes == m].set_index("ano_ref").valor
    xl = pd.Series({a: np.log(e[a] / ref[a]) for a in anos if a in e.index and e[a] > 0})
    fim = pd.Timestamp(2001, m, 1) + pd.offsets.MonthEnd(0)
    ac = pd.Series({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{fim.day:02d}"].sum() for a in range(1998, 2026)})
    pc = pd.Series({a: np.log(ac[a] / ac.drop(a).median()) for a in anos})
    c = xl.index.intersection(y.index)
    r_l = spearmanr(xl[c], y[c]).correlation
    r_i = spearmanr(pc[anos], y[anos]).correlation
    sin_l = np.mean([xl.get(a, np.nan) < -0.3 for a in queb])
    sin_i = np.mean([pc[a] < np.log(0.75) for a in queb])
    tab.append({"mes_ref": m, "n_anos_lspa": len(c), "rho_LSPA": r_l, "rho_IMERG_acum": r_i,
                "quebras_vistas_LSPA(<-26%)": sin_l, "quebras_vistas_IMERG(<75%)": sin_i})
T = pd.DataFrame(tab)
print(T.round(2).to_string(index=False))
e4 = ce[ce.mes == 4].set_index("ano_ref").valor
print("\nano a ano (LSPA de abril e final, mil t; IMERG ate 30/abr em % da mediana):")
ac4 = pd.Series({a: chuva.loc[f"{a}-01-01":f"{a}-04-30"].sum() for a in range(1998, 2026)})
for a in anos:
    print(f"  {a}: LSPA abr {e4.get(a, np.nan) / 1e3:7.0f} | final PAM {fin[a] / 1e3:7.0f} | mediana {ref[a] / 1e3:6.0f}"
          f" | IMERG 1/jan-30/abr {ac4[a] / ac4.drop(a).median():.0%}")
print("nota: n = 19 anos; Spearman com IC largo. O LSPA e opiniao de campo (GCEA/IBGE) e incorpora a chuva vista.")
