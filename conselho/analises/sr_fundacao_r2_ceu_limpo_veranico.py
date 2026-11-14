"""Conselho - sensoriamento remoto, RODADA 2. Hipotese: na quadra (fev-mai), as vistas opticas limpas caem
justamente nos veranicos. Se for verdade, o optico e cego quando chove (sem estresse) e enxerga quando falta
agua (estresse) - um vies de amostragem que (a) ajuda a detectar estresse e (b) enviesa medias de NDVI para dias secos.

Chuva diaria municipal IMERG (saidas/chuva_mun_diaria.parquet) no municipio da AOI; cenas S2+Landsat (uniao, 2017-2025).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

from comum import DADOS

BASE = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
chuva = pd.read_parquet(BASE + "saidas/chuva_mun_diaria.parquet")
chuva.index = pd.to_datetime(chuva.index)
MUN = {"sertao_central": "2311306", "apodi_jaguaribe": "2307601", "cariri": "2304202", "ibiapaba": "2313401"}

s2 = pd.read_parquet(DADOS / "sentinel2/s2_aoi_cenas.parquet")
ls = pd.read_parquet(DADOS / "landsat/landsat_aoi_cenas_l89.parquet")
C = pd.concat([s2[["aoi", "datetime", "frac_valida"]], ls[["aoi", "datetime", "frac_valida"]]])
C["datetime"] = pd.to_datetime(C["datetime"], utc=True).dt.tz_localize(None)
C["dia"] = C.datetime.dt.normalize()
C["frac_valida"] = C.frac_valida.fillna(0)
C = C[C.dia.dt.month.isin([2, 3, 4, 5]) & (C.dia.dt.year <= 2025)]

linhas = []
for aoi, g in C.groupby("aoi"):
    p = chuva[MUN[aoi]]
    seco = (p <= 2).astype(int)
    # dias consecutivos secos ate o dia (inclusive)
    run = seco.groupby((seco == 0).cumsum()).cumsum()
    for _, r in g.iterrows():
        d = r.dia
        if d not in p.index:
            continue
        linhas.append({"aoi": aoi, "dia": d, "f": r.frac_valida, "chuva_dia": p[d], "chuva_5d": p[d - pd.Timedelta(days=4):d].sum(),
                       "dias_secos_seguidos": run[d]})
D = pd.DataFrame(linhas)
D["limpa"] = D.f >= 0.6
print(f"cenas fev-mai: {len(D)}; limpas (>=60% da AOI): {D.limpa.mean():.0%}")
print("\nRelacao entre ceu limpo e veranico em curso (dias secos seguidos, <= 2 mm/dia):")
for aoi, g in D.groupby("aoi"):
    rho, p = spearmanr(g.f, g.dias_secos_seguidos)
    a, b = g[g.limpa].dias_secos_seguidos, g[~g.limpa].dias_secos_seguidos
    print(f"  {aoi:16s} rho(f, dias secos) {rho:+.2f} (p {p:.1e}) | mediana dias secos: cena limpa {a.median():.0f} x nublada {b.median():.0f}"
          f" | chuva 5 d: limpa {g[g.limpa].chuva_5d.median():.1f} x nublada {g[~g.limpa].chuva_5d.median():.1f} mm")
a, b = D[D.limpa].dias_secos_seguidos, D[~D.limpa].dias_secos_seguidos
print(f"  TODAS: mediana dias secos limpa {a.median():.0f} x nublada {b.median():.0f} (Mann-Whitney p {mannwhitneyu(a, b).pvalue:.1e})")
# P(cena limpa | em veranico >= 5 d) vs fora
v = D.dias_secos_seguidos >= 5
print(f"  P(cena limpa | veranico em curso >= 5 d) = {D[v].limpa.mean():.0%} (n {v.sum()}) ; fora de veranico = {D[~v].limpa.mean():.0%} (n {(~v).sum()})")
# P(haver >= 1 vista limpa durante um veranico de >= 10 dias) - quantos veranicos longos o optico 've'
vis = []
for aoi, g in D.groupby("aoi"):
    p = chuva[MUN[aoi]]
    for ano in range(2017, 2026):
        q = p[(p.index >= pd.Timestamp(ano, 2, 1)) & (p.index <= pd.Timestamp(ano, 5, 31))]
        seco = (q <= 2).values
        i = 0
        while i < len(seco):
            if seco[i]:
                j = i
                while j < len(seco) and seco[j]:
                    j += 1
                if j - i >= 10:
                    ini, fim = q.index[i], q.index[j - 1]
                    w = g[(g.dia >= ini) & (g.dia <= fim)]
                    vis.append({"aoi": aoi, "ano": ano, "dur": j - i, "viu": bool((w.f >= 0.6).any())})
                i = j
            else:
                i += 1
V = pd.DataFrame(vis)
print(f"\nVeranicos >= 10 dias em fev-mai (2017-2025, 4 AOIs): {len(V)}; com >= 1 cena limpa S2/Landsat durante o veranico: {V.viu.mean():.0%}")
