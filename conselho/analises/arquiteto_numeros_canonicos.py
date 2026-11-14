"""Arquiteto-chefe: folha de numeros canonicos para a proposta (uma definicao so por numero).

Calcula, com os derivados do projeto:
  A) ONI ASO/2026 e recorde historico de ASO;
  B) chuva e ET0 anuais medias do CE (POWER, 1991-2020);
  C) GRACE CE dessazonalizado em jul, ago e set/2026 (percentil na serie inteira);
  D) quebra canonica de milho e feijao: producao/area plantada < 50% da mediana do
     proprio municipio nos OUTROS anos (1998-2025, sem vazamento), taxa-base, anos-chave,
     El Nino x demais, correlacao milho x feijao e Quixada.
Saida: impressa (redirecionar para saidas/arquiteto_numeros_canonicos.txt).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd

D = "E:/campeonato-nasa/dados/derivados/"

# ---------------- A) ONI ----------------
ind = pd.read_parquet(D + "indices_clima_mensal.parquet")
oni = ind[ind.variavel == "ONI"].set_index("data")["valor"]
aso = oni[oni.index.month == 9]
print("A) ONI rotulado em set (= trimestre ASO):")
print("   2026:", aso.iloc[-1], "| maiores anteriores:", aso[aso.index.year < 2026].sort_values(ascending=False).head(3).round(2).to_dict())
print("   maximo absoluto historico (qualquer trimestre, < 2026):", oni[oni.index.year < 2026].max(), oni[oni.index.year < 2026].idxmax().date())

# ---------------- B) chuva e ET0 ----------------
pw = pd.read_parquet(D + "power_ce_mensal.parquet")
def anual(var):
    # o campo 'valor' ja e o total mensal (mm/mes); so anos com 12 meses validos
    s = pw[pw.variavel == var].dropna(subset=["valor"])
    g = s.groupby(s["data"].dt.year)["valor"].agg(["sum", "count"])
    g = g[g["count"] == 12]
    return g.loc[1991:2020, "sum"].mean()
print(f"B) POWER CE 1991-2020: PRECTOTCORR {anual('PRECTOTCORR'):.0f} mm/ano | IMERG_PRECTOT {anual('IMERG_PRECTOT'):.0f} mm/ano | ET0 {anual('ET0'):.0f} mm/ano")

# ---------------- C) GRACE ----------------
gr = pd.read_parquet(D + "grace_ce_mensal.parquet").sort_values("data")
gr = gr[gr.variavel == gr.variavel.unique()[0]].set_index("data")["valor"]
clim = gr.groupby(gr.index.month).transform("mean")
des = gr - clim
for m in ["2026-07-01", "2026-08-01", "2026-09-01"]:
    t = pd.Timestamp(m)
    if t in des.index:
        v = des.loc[t]
        print(f"C) GRACE CE dessaz. {t.date()}: {v:+.2f} cm | percentil {100*(des < v).mean():.0f}")
m3 = des.loc["2026-07-01":"2026-09-01"].mean()
print(f"   media jul-set/2026: {m3:+.2f} cm | percentil (da media movel de 3 meses) "
      f"{100*(des.rolling(3).mean() < m3).mean():.0f}")

# ---------------- D) quebra canonica ----------------
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
def serie(prefixo):
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha
    # mediana dos OUTROS anos do municipio
    def med_outros(g):
        v = g["r"].values
        out = np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])
        return pd.Series(out, index=g.index)
    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref
    p["quebra"] = p.razao < 0.5
    return p.dropna(subset=["razao"])

mi = serie("Milho (em gr")
fe = serie("Feij")
oni_ndj = oni[oni.index.month == 12]  # rotulo dez = NDJ
oni_ndj.index = oni_ndj.index.year + 1  # NDJ que antecede a quadra do ano seguinte
for nome, p in [("milho", mi), ("feijao", fe)]:
    fr = p.groupby("ano")["quebra"].mean()
    en = [a for a in fr.index if oni_ndj.get(a, 0) >= 1.0]
    print(f"D) {nome}: n={len(p)} municipio-anos; taxa-base de quebra {100*p.quebra.mean():.1f}%")
    print("   fracao de municipios em quebra: " + ", ".join(f"{a}: {100*fr.get(a, np.nan):.0f}%" for a in [1998, 2010, 2012, 2013, 2016, 2024]))
    print(f"   anos El Nino (ONI NDJ anterior >= 1,0): {en} -> {100*p[p.ano.isin(en)].quebra.mean():.1f}% contra {100*p[~p.ano.isin(en)].quebra.mean():.1f}% nos demais")
    print(f"   queda estadual em 2012 (soma producao / soma area plantada vs mediana dos outros anos): ", end="")
    tot = p.groupby("ano")[["producao_t", "area_plantada_ha"]].sum()
    rr = tot.producao_t / tot.area_plantada_ha
    print(f"{100*(rr.loc[2012]/rr.drop(2012).median()-1):.0f}%")

j = mi.merge(fe, on=["cod_local", "ano"], suffixes=("_m", "_f"))
j = j[(j.razao_m > 0) & (j.razao_f > 0)]
cors = j.groupby("cod_local").apply(lambda g: np.corrcoef(np.log(g.razao_m), np.log(g.razao_f))[0, 1] if len(g) >= 10 else np.nan)
print(f"D) correlacao mediana (log-razao) milho x feijao no mesmo municipio: {cors.median():.2f} (n={cors.notna().sum()} municipios)")

QX = 2311306  # Quixada
for nome, p in [("milho", mi), ("feijao", fe)]:
    q = p[p.cod_local.astype(int) == QX].sort_values("ano")
    if len(q):
        pior = q.loc[q.razao.idxmin()]
        print(f"D) Quixada {nome}: {int(q.quebra.sum())} quebras em {len(q)} anos; pior ano {int(pior.ano)} razao {pior.razao:.2f}; 2012 razao {q.set_index('ano').razao.get(2012, np.nan):.2f}")
