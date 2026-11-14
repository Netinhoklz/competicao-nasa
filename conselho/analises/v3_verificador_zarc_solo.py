"""Verificador adversario (v3): o veredito 'milho confere, caupi/sorgo 2-3 decendios mais cedo' do bloco F de
v3_curador_valida_soilgrids_zarc depende de comparar o sintetico com o solo/ciclo MAIS PERMISSIVO do ZARC oficial?
Refaz a comparacao contra: (a) o mais permissivo (como no curador), (b) a mediana dos solos x ciclos,
(c) o solo do meio (tipo 2 / AD3-AD4) em cada ciclo. Somente le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

A = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
z = pd.read_csv(DADOS / "complementares" / "zarc" / "tabua_risco_ce_2026-2027.csv", sep=";", dtype=str)
z = z[z.Nome_Outros_Manejos == "Sequeiro"]
dec = [f"dec{i}" for i in range(1, 37)]
z[dec] = z[dec].astype(int)
CULT = {"milho": "Milho 1", "caupi": "Feij\u00e3o Caupi", "sorgo": "Sorgo Gran"}
SINT = pd.read_parquet(A / "saidas" / "agronomo_zarc_sintetico_prob.parquet")
SINT.index = SINT.index.astype(str)
DEC_S = ["01/jan", "11/jan", "21/jan", "01/fev", "11/fev", "21/fev", "01/mar", "11/mar", "21/mar", "01/abr", "11/abr", "21/abr"]


def ultimo_ok(row, lim=30):
    ok = [i for i in range(1, 19) if 0 < row[f"dec{i}"] <= lim]
    return max(ok) if ok else 0


def sint_ultimo(cod, c):
    v = [SINT.loc[cod, f"{c}|{d}"] for d in DEC_S]
    ok = [i + 1 for i, p in enumerate(v) if p >= 0.7]
    return max(ok) if ok else 0


for c, pref in CULT.items():
    s = z[z.Nome_cultura.str.startswith(pref)].copy()
    s["ult"] = s.apply(ultimo_ok, axis=1)
    s["geocodigo"] = s.geocodigo.astype(str)
    s = s[s.geocodigo.isin(SINT.index)]
    s["sint"] = s.geocodigo.map(lambda cd: sint_ultimo(cd, c))
    solos = sorted(s.Cod_Solo.astype(int).unique())
    print(f"\n{c}: solos {solos}; ciclos {sorted(s.Cod_Ciclo.unique())}; municipios {s.geocodigo.nunique()}")
    g = s.groupby("geocodigo").agg(ult_max=("ult", "max"), ult_med=("ult", "median"), sint=("sint", "first"))
    for nome, col in [("mais permissivo (curador)", "ult_max"), ("mediana solos x ciclos", "ult_med")]:
        d = g.sint - g[col]
        print(f"  {nome:28s} dif mediana {d.median():+.1f} | |dif|<=1 em {(d.abs() <= 1).mean():.0%} | "
              f"Spearman {spearmanr(g[col], g.sint).correlation:.2f}")
    # cada solo, maximo entre ciclos, e cada ciclo x solo
    for so in solos:
        h = s[s.Cod_Solo.astype(int) == so].groupby("geocodigo").agg(u=("ult", "max"), sint=("sint", "first"))
        d = h.sint - h.u
        print(f"  solo {so:>2} (max dos ciclos)        dif mediana {d.median():+.1f} | |dif|<=1 em {(d.abs() <= 1).mean():.0%} | n {len(h)}")
    for ci in sorted(s.Cod_Ciclo.unique()):
        for so in solos:
            h = s[(s.Cod_Ciclo == ci) & (s.Cod_Solo.astype(int) == so)].groupby("geocodigo").agg(u=("ult", "max"), sint=("sint", "first"))
            if len(h) == 0:
                continue
            d = h.sint - h.u
            print(f"    ciclo {ci} solo {so:>2}: dif mediana {d.median():+.1f} | |dif|<=1 em {(d.abs() <= 1).mean():.0%} | "
                  f"oficial sem janela {(h.u == 0).mean():.0%}")
