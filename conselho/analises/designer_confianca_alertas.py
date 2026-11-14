"""Designer - Rodada 2: orcamento de confianca dos alertas (como um agricultor EXPERIMENTA o alerta ao longo dos anos).

Perguntas (adocao, nao so AUC):
 (1) Quando o alerta de 30/abr ("chuva desde 1/jan < 75% do normal do municipio") toca e o milho NAO quebra (< 50%),
     o ano foi normal ou "meio ruim"? Se o falso alarme cai em ano de perda moderada, o agricultor nao o percebe como erro.
 (2) Primeira impressao: para quem comeca a usar em um ano qualquer (1998-2020), o PRIMEIRO alerta que recebe e acerto,
     "quase acerto" (rend. < 75% do normal) ou alarme claro (ano normal)?
 (3) Coerencia da mensagem entre conversas (28/fev -> 31/mar -> 30/abr): quantas vezes o alerta "liga e desliga"?
 (4) Prova social: alertas em anos em que >= 50% dos municipios sao alertados juntos vs alertas isolados - precisao.
Dados: saidas/designer_chuva_mun_diaria.parquet (IMERG V07 diario municipal), ibge_pam_mun_anual.parquet. 1998-2025.
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

s = pam[pam.produto.str.startswith("Milho (em gr") & (pam.ano >= 1990)].copy()
s["rp"] = np.where(s.area_plantada_ha >= 100, s.producao_t * 1000 / s.area_plantada_ha.replace(0, np.nan), np.nan)
s = s.sort_values(["cod", "ano"])
s["tend"] = s.groupby("cod")["rp"].transform(lambda v: v.rolling(7, center=True, min_periods=4).median())
s["razao"] = s.rp / s.tend
R = s.set_index(["cod", "ano"]).razao

anos = list(range(1998, 2026))
cube = np.stack([chuva.loc[pd.Timestamp(a, 1, 1):].iloc[:151].values for a in anos])
datas = {"28/fev": 59, "31/mar": 90, "30/abr": 120}
alerta = {}
for nome, nd in datas.items():
    acc = cube[:, :nd, :].sum(1)
    pct = np.empty_like(acc)
    for k in range(len(anos)):
        pct[k] = acc[k] / np.median(np.delete(acc, k, axis=0), axis=0)
    alerta[nome] = pd.DataFrame(pct < 0.75, index=anos, columns=chuva.columns)

A = pd.concat({k: v.stack() for k, v in alerta.items()}, axis=1)
A.index.names = ["ano", "cod"]
A = A.reset_index().join(R, on=["cod", "ano"]).dropna(subset=["razao"])
A["quebra"] = A.razao < 0.5
A["classe"] = np.select([A.razao < 0.5, A.razao < 0.75], ["quebra(<50%)", "perda moderada(50-75%)"], "ano normal(>=75%)")
print(f"municipio-anos com rendimento: {len(A)}; taxa de quebra {A.quebra.mean():.3f}")

# (1) o que e o falso alarme
for d in datas:
    al = A[A[d]]
    print(f"\n(1) alerta {d}: toca em {A[d].mean():.1%}; entre os alertados -> "
          + ", ".join(f"{k} {v:.0%}" for k, v in al.classe.value_counts(normalize=True).items())
          + f" | razao mediana {al.razao.median():.2f} (nao alertados {A[~A[d]].razao.median():.2f})")
    fa = al[~al.quebra]
    print(f"    falso alarme (sem quebra): razao mediana {fa.razao.median():.2f}; "
          f"{(fa.razao < 0.75).mean():.0%} deles foram perda moderada; {(fa.razao >= 1.0).mean():.0%} acima do normal")

# (2) primeira impressao para quem comeca em cada ano
d = "30/abr"
lin = []
for cod, g in A.sort_values("ano").groupby("cod"):
    for inicio in range(1998, 2021):
        h = g[(g.ano >= inicio) & g[d]]
        if len(h):
            r = h.iloc[0]
            lin.append({"cod": cod, "inicio": inicio, "espera_anos": r.ano - inicio, "classe": r.classe})
P = pd.DataFrame(lin)
print(f"\n(2) primeiro alerta de 30/abr recebido (184 mun x inicios 1998-2020, n={len(P)}):")
print("    " + ", ".join(f"{k} {v:.0%}" for k, v in P.classe.value_counts(normalize=True).items()))
print(f"    espera mediana ate o 1o alerta: {P.espera_anos.median():.0f} anos (p90 {P.espera_anos.quantile(.9):.0f})")
# primeiros 3 anos de uso: P(ao menos um alarme claro em ano normal)
lin = []
for cod, g in A.groupby("cod"):
    g = g.set_index("ano")
    for inicio in range(1998, 2024):
        w = g.loc[inicio:inicio + 2]
        if len(w) == 3:
            lin.append({"alarme_claro": bool((w[d] & (w.razao >= 0.75)).any()),
                        "quebra_perdida": bool((~w[d] & w.quebra).any()),
                        "algum_alerta": bool(w[d].any())})
T3 = pd.DataFrame(lin)
print(f"    em 3 anos de uso: P(>=1 alarme claro em ano normal) {T3.alarme_claro.mean():.0%}; "
      f"P(>=1 quebra sem alerta) {T3.quebra_perdida.mean():.0%}; P(nenhum alerta) {(~T3.algum_alerta).mean():.0%}")

# (3) coerencia entre conversas
seq = A["28/fev"].astype(int).astype(str) + A["31/mar"].astype(int).astype(str) + A["30/abr"].astype(int).astype(str)
vc = seq.value_counts(normalize=True)
liga_desliga = seq.isin(["101", "010", "100", "110"])
print("\n(3) padrao do alerta 28/fev-31/mar-30/abr (1=alerta): " + ", ".join(f"{k} {v:.1%}" for k, v in vc.items()))
print(f"    mensagem que liga e depois desliga (100,110,010,101): {liga_desliga.mean():.1%} dos municipio-anos; "
      f"quebra nesses casos {A.quebra[liga_desliga].mean():.2f} vs {A.quebra[seq == '111'].mean():.2f} em 111 "
      f"e {A.quebra[seq == '000'].mean():.2f} em 000")
for pat in ["111", "011", "001", "100", "110", "000"]:
    m = seq == pat
    if m.sum() > 20:
        print(f"    {pat}: n={m.sum():4d}  P(quebra)={A.quebra[m].mean():.2f}  razao mediana={A.razao[m].median():.2f}")

# (4) prova social
frac = A.groupby("ano")[d].mean()
A["sinc"] = A.ano.map(frac) >= 0.5
for nome, m in [("alerta em ano sincronizado (>=50% mun alertados)", A[d] & A.sinc),
                ("alerta isolado (<50% alertados)", A[d] & ~A.sinc)]:
    print(f"\n(4) {nome}: {m.sum()} casos ({m.sum() / A[d].sum():.0%} dos alertas); P(quebra) {A.quebra[m].mean():.2f}; "
          f"P(razao<0,75) {(A.razao[m] < 0.75).mean():.2f}")
print("    anos sincronizados:", list(frac[frac >= 0.5].index))
