"""Juiz (banca adversaria): a vantagem da carteira 1/3 milho, 1/3 feijao, 1/3 mandioca resiste a definicao canonica?

O estrategista_portfolio_rotacao.py e o estrategista_demo_quixada.py usam rendimento por AREA COLHIDA e filtram
area_colhida >= 50 (ou >= 10) e rendimento > 0. Isso descarta os anos de perda total (area colhida = 0), que sao a cauda.
A definicao canonica (arquiteto_numeros_canonicos.py) usa producao / AREA PLANTADA e mediana dos outros anos.
Aqui: (a) definicao original; (b) canonica com perdas totais; (c) canonica sem os anos de mandioca com rendimento repetido.
Tambem: o replay de Quixada em 1998 e 2012 pela definicao canonica.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from comum import DERIV

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[(pam.ano >= 1998) & (pam.ano <= 2025)]
PREF = {"milho": "Milho (em", "feijao": "Feij", "mandioca": "Mandioca"}


def original(pref):
    q = pam[pam.produto.str.startswith(pref) & (pam.area_colhida_ha >= 50) & (pam.rendimento_kg_ha > 0)]
    q = q[["cod_local", "ano", "rendimento_kg_ha"]].copy()
    q["razao"] = q.rendimento_kg_ha / q.groupby("cod_local").rendimento_kg_ha.transform("median")
    return q.set_index(["cod_local", "ano"]).razao


def canonica(pref, tirar_repetido=False):
    p = pam[pam.produto.str.startswith(pref) & (pam.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha
    p = p.sort_values(["cod_local", "ano"])
    if tirar_repetido:
        rep = p.groupby("cod_local").r.diff().abs() < 1e-9
        p = p[~rep]
    out = []
    for cod, g in p.groupby("cod_local"):
        r = g.r.values
        med = np.array([np.median(np.delete(r, i)) if len(r) > 1 else np.nan for i in range(len(r))])
        out.append(pd.DataFrame({"cod_local": cod, "ano": g.ano.values, "razao": r / med}))
    return pd.concat(out).set_index(["cod_local", "ano"]).razao


def resumo(Y, rotulo):
    B = Y.dropna()
    print(f"\n--- {rotulo}: n comum = {len(B)} municipio-anos ---")
    for k, s in {"100% milho": B.milho, "milho+feijao": B[["milho", "feijao"]].mean(axis=1),
                 "1/3 cada": B.mean(axis=1)}.items():
        cvar = s[s <= s.quantile(0.10)].mean()
        print(f"  {k:14s} CVaR10={cvar:.3f}  P(<0.5)={(s < 0.5).mean():.3f}  P10={s.quantile(.1):.3f}")
    # quantos municipio-anos de perda total de milho entram
    print(f"  municipio-anos com milho razao < 0.05 no conjunto comum: {(B.milho < 0.05).sum()}")
    return B


Ya = pd.DataFrame({k: original(v) for k, v in PREF.items()})
Yb = pd.DataFrame({k: canonica(v) for k, v in PREF.items()})
Yc = pd.DataFrame({"milho": canonica(PREF["milho"]), "feijao": canonica(PREF["feijao"]),
                   "mandioca": canonica(PREF["mandioca"], tirar_repetido=True)})
resumo(Ya, "(a) original: area colhida >= 50, rendimento > 0")
Bb = resumo(Yb, "(b) canonica: producao / area plantada >= 50, perdas totais incluidas")
resumo(Yc, "(c) canonica, mandioca sem anos de rendimento repetido")

# quantos municipio-anos de milho em perda total cada definicao deixa de fora
mil_b = Yb.milho.dropna()
mil_a = Ya.milho.dropna()
print(f"\nmilho: municipio-anos canonicos = {len(mil_b)}; com razao < 0.05 = {(mil_b < 0.05).sum()};"
      f" desses, ausentes na definicao original = {(~mil_b[mil_b < 0.05].index.isin(mil_a.index)).sum()}")
# mandioca: os anos secos ficam no conjunto comum?
for ano in [1998, 2012, 2016]:
    na_b = Yb.xs(ano, level="ano") if ano in Yb.index.get_level_values("ano") else None
    if na_b is not None:
        print(f"  {ano}: municipios com milho canonico = {na_b.milho.notna().sum()}, com mandioca canonica = {na_b.mandioca.notna().sum()},"
              f" com as 3 = {na_b.dropna().shape[0]}")

# Quixada
cod = pam[pam.local.str.startswith("Quixad")].cod_local.iloc[0]
print("\nQuixada, definicao canonica (razao da producao/area plantada sobre a mediana dos outros anos):")
Q = Yb.xs(cod, level="cod_local")
print(Q.loc[[a for a in [1998, 2012, 2013, 2016, 2024] if a in Q.index]].round(2).to_string())
q = pam[(pam.cod_local == cod) & pam.ano.isin([1998, 2012, 2016])]
q = q[q.produto.str.startswith(("Milho (em", "Feij", "Mandioca"))]
print(q[["ano", "produto", "area_plantada_ha", "area_colhida_ha", "producao_t"]].sort_values(["ano", "produto"]).to_string(index=False))
QB = Q.dropna()
print(f"Quixada anos com as 3 culturas (canonica): {len(QB)}")
for k, s in {"milho": QB.milho, "milho+feijao": QB[["milho", "feijao"]].mean(axis=1), "1/3 cada": QB.mean(axis=1)}.items():
    print(f"  {k:14s} pior ano={s.min():.2f} ({int(s.idxmin())})  P10={s.quantile(.1):.2f}")
