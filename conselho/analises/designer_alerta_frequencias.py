"""Designer (agricultor familiar) - Analise 3: o alerta do meio da quadra, dito em frequencias naturais.

Pergunta: um alerta simples, que cabe num audio de WhatsApp ("choveu menos de 60% do normal ate hoje aqui" ou
"ja passou X dias sem chuva"), emitido em 15/mar, 31/mar ou 30/abr, separa os municipio-anos que quebram o milho/feijao?
Em linguagem de agricultor: "quando o alerta toca, de cada 10 rocados, quantos quebram? e quando nao toca?"
Isso define a mensagem do ponto de conversa de marco/abril (ensilar o milho como forragem, plantar caupi de ciclo curto,
guardar a palha em vez de queimar).

Metodo: chuva acumulada desde 1/jan ate a data, como % da mediana do PROPRIO municipio nessa data nos OUTROS anos
(deixa o ano de fora); maior sequencia de dias < 2 mm desde 1/jan. Alvo: quebra (rend. por area plantada < 50% da
mediana movel de 7 anos), como em designer_calendario_decisao.py. 1998-2025.
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


def alvo(prefixo):
    s = pam[pam.produto.str.startswith(prefixo) & (pam.ano >= 1990)].copy()
    s["rp"] = np.where(s.area_plantada_ha >= 100, s.producao_t * 1000 / s.area_plantada_ha.replace(0, np.nan), np.nan)
    s = s.sort_values(["cod", "ano"])
    s["tend"] = s.groupby("cod")["rp"].transform(lambda v: v.rolling(7, center=True, min_periods=4).median())
    s["quebra"] = (s.rp / s.tend < 0.5).astype(float).where((s.rp / s.tend).notna())
    return s.set_index(["cod", "ano"]).quebra


Q = {"milho": alvo("Milho (em gr"), "feijao": alvo("Feij")}


def maior_seca(x, lim=2.0):
    m = c = 0
    for v in x:
        c = c + 1 if v < lim else 0
        m = max(m, c)
    return m


anos = range(1998, 2026)
for (mes, dia) in [(3, 15), (3, 31), (4, 30)]:
    rows = []
    for a in anos:
        w = chuva.loc[pd.Timestamp(a, 1, 1):pd.Timestamp(a, mes, dia)]
        for cod in chuva.columns:
            rows.append({"cod": cod, "ano": a, "P": w[cod].sum(), "seca": maior_seca(w[cod].values)})
    F = pd.DataFrame(rows)
    # % da mediana do proprio municipio nos outros anos
    piv = F.pivot(index="ano", columns="cod", values="P")
    pct = piv.copy()
    for a in piv.index:
        pct.loc[a] = piv.loc[a] / piv.drop(index=a).median()
    F = F.merge(pct.stack().rename("pct").reset_index(), on=["cod", "ano"])
    print(f"\n=========== data de decisao {dia:02d}/{mes:02d} ===========")
    for cult, q in Q.items():
        G = F.join(q, on=["cod", "ano"]).dropna(subset=["quebra"])
        base = G.quebra.mean()
        for nome, cond in [("chuva < 60% do normal", G.pct < 0.6), ("chuva < 75% do normal", G.pct < 0.75),
                           ("seca >= 20 dias", G.seca >= 20),
                           ("chuva < 75% E seca >= 15 d", (G.pct < 0.75) & (G.seca >= 15))]:
            n_al = int(cond.sum())
            if n_al < 30:
                continue
            p1, p0 = G.quebra[cond].mean(), G.quebra[~cond].mean()
            sens = G.quebra[cond].sum() / G.quebra.sum()
            anos_al = G[cond].groupby("ano").size()
            print(f"[{cult:6s}] {nome:28s}: toca em {cond.mean():5.1%} dos municipio-anos | "
                  f"de 10 rocados com alerta, {10 * p1:.1f} quebram; sem alerta, {10 * p0:.1f} (base {10 * base:.1f}) | "
                  f"razao {p1 / p0:.1f}x | pega {sens:.0%} das quebras | anos com mais alertas: "
                  f"{list(anos_al.sort_values(ascending=False).index[:4])}")
