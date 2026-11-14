"""Designer (agricultor familiar) - Analise 3b: "relogio do veranico" a partir do PLANTIO + replay da demo.

Pergunta: contar o veranico a partir da data de plantio (que so o agricultor sabe e pode dizer por audio) separa melhor
a quebra do que contar desde 1/jan? Proxy do plantio: dia seguinte ao 1o acumulado de >= 20 mm em 3 dias desde 1/jan
(inicio "causal", conhecido no proprio dia). Alerta em 31/mar e 30/abr.
Replay: o que o alerta de 30/abr diria em Quixada, Taua, Crateus e Iguatu em 2012 e 2016, e no estado.
Dados: saidas/designer_chuva_mun_diaria.parquet (IMERG V07 diario), ibge_pam_mun_anual.parquet.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import warnings

warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV, REF

import numpy as np
import pandas as pd

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
chuva = pd.read_parquet(OUT / "designer_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
nomes = {str(d["id"]): d["nome"] for d in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(str)
s = pam[pam.produto.str.startswith("Milho (em gr") & (pam.ano >= 1990)].copy()
s["rp"] = np.where(s.area_plantada_ha >= 100, s.producao_t * 1000 / s.area_plantada_ha.replace(0, np.nan), np.nan)
s = s.sort_values(["cod", "ano"])
s["tend"] = s.groupby("cod")["rp"].transform(lambda v: v.rolling(7, center=True, min_periods=4).median())
s["razao"] = s.rp / s.tend
s["quebra"] = (s.razao < 0.5).astype(float).where(s.razao.notna())
Q = s.set_index(["cod", "ano"])[["razao", "quebra"]]


def maior_seca(x, lim=2.0):
    m = c = 0
    for v in x:
        c = c + 1 if v < lim else 0
        m = max(m, c)
    return m


rows = []
for a in range(1998, 2026):
    for (mes, dia) in [(3, 31), (4, 30)]:
        w = chuva.loc[pd.Timestamp(a, 1, 1):pd.Timestamp(a, mes, dia)]
        for cod in chuva.columns:
            x = w[cod].values
            s3 = np.convolve(x, np.ones(3), "valid")
            on = np.where(s3 >= 20)[0]
            plantio = int(on[0]) + 3 if len(on) else None  # dia seguinte ao acumulado
            seca_pos = maior_seca(x[plantio:]) if plantio is not None and plantio < len(x) else len(x)
            rows.append({"cod": cod, "ano": a, "data": f"{dia:02d}/{mes:02d}", "P": x.sum(),
                         "seca_desde_jan": maior_seca(x), "seca_pos_plantio": seca_pos,
                         "plantio_doy": plantio + 1 if plantio is not None else np.nan})
F = pd.DataFrame(rows).join(Q, on=["cod", "ano"])
# % do normal do proprio municipio (mediana dos outros anos, mesma data)
F["pct"] = np.nan
for (cod, dt), g in F.groupby(["cod", "data"]):
    for i, r in g.iterrows():
        F.at[i, "pct"] = r.P / g.loc[g.ano != r.ano, "P"].median()
G = F.dropna(subset=["quebra"])
print(f"plantio proxy (dia do ano), mediana por ano no estado: "
      f"{G[G.data == '30/04'].groupby('ano').plantio_doy.median().round(0).astype('Int64').to_dict()}")
for dt in ["31/03", "30/04"]:
    g = G[G.data == dt]
    print(f"\n=== {dt} (milho, {len(g)} municipio-anos, base {10 * g.quebra.mean():.1f} em 10) ===")
    for nome, cond in [("seca desde 1/jan >= 20 d", g.seca_desde_jan >= 20),
                       ("seca POS-PLANTIO >= 15 d", g.seca_pos_plantio >= 15),
                       ("seca POS-PLANTIO >= 20 d", g.seca_pos_plantio >= 20),
                       ("chuva < 75% do normal", g.pct < 0.75),
                       ("chuva < 75% OU seca pos-plantio >= 20 d", (g.pct < 0.75) | (g.seca_pos_plantio >= 20))]:
        p1, p0 = g.quebra[cond].mean(), g.quebra[~cond].mean()
        print(f"  {nome:40s}: toca {cond.mean():5.1%} | com alerta {10 * p1:.1f}/10 quebram, sem {10 * p0:.1f}/10 "
              f"(razao {p1 / p0:.1f}x) | pega {g.quebra[cond].sum() / g.quebra.sum():.0%} das quebras")

print("\n=== Replay da demo (30/abr) ===")
g = F[F.data == "30/04"]
for a in [2012, 2016]:
    ga = g[g.ano == a]
    al = (ga.pct < 0.75) | (ga.seca_pos_plantio >= 20)
    gq = ga.dropna(subset=["quebra"])
    alq = (gq.pct < 0.75) | (gq.seca_pos_plantio >= 20)
    print(f"{a}: alerta tocaria em {al.mean():.0%} dos municipios; entre os alertados, {gq.quebra[alq].mean():.0%} quebraram; "
          f"entre os nao alertados, {gq.quebra[~alq].mean():.0%}")
    for nm in ["Quixad", "Tau", "Crate", "Iguatu"]:
        c = [k for k, v in nomes.items() if v.startswith(nm)][0]
        r = ga[ga.cod == c].iloc[0]
        print(f"   {nomes[c]:10s}: chuva 1/jan-30/abr = {r.P:4.0f} mm ({r.pct:.0%} do normal), plantio proxy dia {r.plantio_doy:.0f}, "
              f"maior veranico pos-plantio {r.seca_pos_plantio:.0f} d -> alerta={'SIM' if (r.pct < 0.75 or r.seca_pos_plantio >= 20) else 'nao'}"
              f" | real razao={r.razao:.2f}")
