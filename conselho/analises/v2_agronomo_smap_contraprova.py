"""Agronomo (rodada 2) - contraprova do achado do SMAP nos portoes.

Achado a testar (de v2_agronomo_smap_portoes.saida.txt): em 2016-2025, o percentil da zona da raiz do SMAP L4 em 30/abr
separou a quebra do milho melhor que a chuva IMERG acumulada desde 1/jan (AUC 0,77 contra 0,66), porque o solo
"esquece" o janeiro chuvoso de 2016. Medida contraria: se o ganho e so memoria curta, uma chuva com memoria curta
(indice de chuva antecedente, API, com a constante de tempo tau MEDIDA no proprio SMAP, sem olhar a quebra) deve
fazer o mesmo nos anos que o SMAP NAO viu (1998-2015). Se fizer, a regra canonica do portao fica errada em 28 anos,
nao so em 10.

Pre-declarado: tau = primeiro atraso em que a autocorrelacao da anomalia diaria da zona da raiz (fev-jun) cai abaixo
de 1/e (media dos municipios); API(portao) = soma de chuva x exp(-(portao - dia)/tau), desde 1/jan; % do normal =
razao contra a mediana dos OUTROS anos; alerta = < 75% (mesmo limiar da regra canonica). Nada mais e ajustado.
Tambem: (b) percentil proprio da zona da raiz para a estacao seca (o percentil do L4 nao existe em out-dez no CE);
(c) serie do milho de Quixada e a mediana de referencia (relato redondo 2017-2020).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
RNG = np.random.default_rng(1)
QX = "2311306"
RZ = pd.read_parquet(OUT / "v2_agronomo_smap_mun_sm_rootzone.parquet")
PC = pd.read_parquet(OUT / "v2_agronomo_smap_mun_sm_rootzone_pctl.parquet")

# ------------------------------------------------------------------ tau da memoria da zona da raiz (SMAP)
doy = RZ.index.dayofyear
clim = RZ.groupby(doy).transform("mean")
clim = clim.rolling(31, center=True, min_periods=1).mean()
an = RZ - clim
estacao = an[(an.index.month >= 2) & (an.index.month <= 6)]
acf = []
for lag in range(1, 121):
    v = []
    for a, g in an.groupby(an.index.year):
        g2 = g[(g.index.month >= 2) & (g.index.month <= 6)]
        x = g2.values[:-lag] if lag < len(g2) else None
        if x is None or len(g2) - lag < 30:
            continue
        y = g2.values[lag:]
        v.append(np.nanmean([np.corrcoef(x[:, j], y[:, j])[0, 1] for j in range(x.shape[1])]))
    acf.append(np.nanmean(v))
acf = np.array(acf)
tau = int(np.argmax(acf < 1 / np.e) + 1)
print(f"memoria da zona da raiz (SMAP L4, CE, fev-jun, 2016-2026): autocorrelacao da anomalia em 10 d {acf[9]:.2f}, "
      f"30 d {acf[29]:.2f}, 60 d {acf[59]:.2f}; tau (1/e) = {tau} dias")

# ------------------------------------------------------------------ chuva: desde 1/jan x API(tau)
chuva = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
cods = [c for c in chuva.columns if c in RZ.columns]
PORT = {"19/mar": "03-19", "30/abr": "04-30"}
IND = {}
for g, md in PORT.items():
    acc, api = {}, {}
    for a in range(1998, 2026):
        x = chuva.loc[f"{a}-01-01":f"{a}-{md}", cods]
        w = np.exp(-(len(x) - 1 - np.arange(len(x))) / tau)[:, None]
        acc[a] = x.sum(); api[a] = (x.values * w).sum(0)
    A = pd.DataFrame(acc).T
    B = pd.DataFrame(api, index=cods).T
    for nome, T in [("acum", A), ("api", B)]:
        norm = pd.DataFrame({a: T.drop(index=a).median() for a in T.index}).T
        IND[(g, nome)] = T / norm

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")


def serie(prefixo):
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        return pd.Series([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref
    p["quebra"] = p.razao < 0.5
    p["cod"] = p.cod_local.astype(str)
    return p.dropna(subset=["razao"])


def auc(y, s):
    y = np.asarray(y, bool)
    return roc_auc_score(y, s) if 0 < y.sum() < len(y) else np.nan


def boot(d, f, B=1000):
    anos = d.ano.unique(); grp = {a: d[d.ano == a] for a in anos}
    v = [f(pd.concat([grp[a] for a in RNG.choice(anos, len(anos))])) for _ in range(B)]
    return np.nanpercentile(v, [5, 95])


for cult, pref in [("milho", "Milho (em gr"), ("feijao", "Feij")]:
    q = serie(pref)
    print(f"\n=== {cult}: chuva desde 1/jan (regra canonica) x API com tau = {tau} d (memoria do SMAP) ===")
    for g in PORT:
        L = []
        for nome in ["acum", "api"]:
            T = IND[(g, nome)].stack().rename(nome).reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})
            L.append(T.set_index(["ano", "cod"]))
        d0 = q.merge(pd.concat(L, axis=1).reset_index(), on=["ano", "cod"])
        if cult == "milho" and g == "30/abr":
            dm_sm = d0.copy()
        for per, (a0, a1) in [("1998-2015 (anos que o SMAP nao viu)", (1998, 2015)), ("2016-2025 (era SMAP)", (2016, 2025)),
                              ("1998-2025", (1998, 2025))]:
            d = d0[d0.ano.between(a0, a1)]
            aa, ab = auc(d.quebra, -d.acum), auc(d.quebra, -d.api)
            dif = boot(d, lambda b: auc(b.quebra, -b.api) - auc(b.quebra, -b.acum))
            txt = []
            for nome in ["acum", "api"]:
                al = d[nome] < 0.75
                txt.append(f"{nome} alerta: {d.quebra[al].mean() * 10:.1f} em 10 (n={al.sum()}) x sem {d.quebra[~al].mean() * 10:.1f}")
            print(f"  {g} {per}: AUC acum {aa:.2f} | API {ab:.2f} | dif API-acum IC90 {dif[0]:+.2f} a {dif[1]:+.2f} | " + "; ".join(txt))
        # SMAP no mesmo painel 2016-2025 (para o milho)
        d = d0[d0.ano >= 2016].copy()
        t = pd.to_datetime(d.ano.astype(str) + "-" + PORT[g])
        d["pctl"] = [PC.at[tt, c] for tt, c in zip(t, d.cod)]
        d = d.dropna(subset=["pctl"])
        print(f"  {g} 2016-2025, mesmo painel: AUC SMAP pctl {auc(d.quebra, -d.pctl):.2f}; Spearman API x pctl "
              f"{stats.spearmanr(d.api, d.pctl)[0]:+.2f}; acum x pctl {stats.spearmanr(d.acum, d.pctl)[0]:+.2f}")

# ------------------------------------------------------------------ (b) percentil proprio na estacao seca
print("\n=== (b) Percentil PROPRIO da zona da raiz (posto entre os anos 2015-2026 no mesmo dia, +-15 d) ===")
ult = RZ.index[-1]
jan = [ult - pd.Timedelta(days=15) + pd.Timedelta(days=k) for k in range(31)]
ref = []
for a in range(2015, 2026):
    for t in jan:
        tt = t.replace(year=a)
        if tt in RZ.index:
            ref.append(RZ.loc[tt])
ref = pd.DataFrame(ref)
hoje = RZ.loc[ult]
pp = (ref < hoje).mean() * 100
print(f"  {ult.date()}: percentil proprio mediano no CE {pp.median():.0f} (p10-p90 {pp.quantile(.1):.0f}-{pp.quantile(.9):.0f}); "
      f"Quixada {pp[QX]:.0f}; fracao de municipios abaixo do p33: {(pp < 33.3).mean():.0%}")
print(f"  umidade da zona da raiz em {ult.date()}: CE mediana {hoje.median():.3f} m3/m3; mesma data 2015-2025: "
      + ", ".join(f"{a}: {RZ.loc[ult.replace(year=a)].median():.3f}" for a in range(2015, 2026) if ult.replace(year=a) in RZ.index))
amp = (RZ.loc["2016":"2025"].groupby(RZ.loc["2016":"2025"].index.year).quantile(0.95) -
       RZ.loc["2016":"2025"].groupby(RZ.loc["2016":"2025"].index.year).quantile(0.05)).median()
dp_nov = pd.DataFrame([RZ.loc[ult.replace(year=a)] for a in range(2015, 2026)]).std()
print(f"  amplitude anual tipica (p95-p5) mediana {amp.median():.3f} m3/m3; desvio entre anos em {ult.strftime('%d/%m')}: "
      f"{dp_nov.median():.3f} m3/m3 ({(dp_nov / amp).median():.0%} da amplitude) -> o solo de novembro esta no piso todo ano")

# ------------------------------------------------------------------ (c) Quixada: o milho e a referencia
print("\n=== (c) Quixada, milho: rendimento (produção/area plantada) e a mediana de referencia ===")
q = serie("Milho (em gr")
qq = q[q.cod == QX].set_index("ano")
print("  " + ", ".join(f"{a}: {int(r * 1000)}" for a, r in qq.r.items()) + " kg/ha")
red = pam[(pam.cod_local.astype(str) == QX) & pam.produto.str.startswith("Milho (em gr") & pam.ano.between(1998, 2025)]
redondo = red[(red.producao_t == red.area_plantada_ha) & (red.area_plantada_ha > 0)].ano.tolist()
print(f"  anos com producao (t) = area plantada (ha), isto e, 1.000 kg/ha exatos: {redondo}")
for a in [2023, 2024, 2025]:
    v = qq.r.drop(index=a).values
    v2 = qq.r.drop(index=[a] + redondo).values
    print(f"  {a}: {qq.r[a] * 1000:.0f} kg/ha; referencia canonica {np.median(v) * 1000:.0f} -> razao {qq.r[a] / np.median(v):.2f}; "
          f"sem os anos redondos {np.median(v2) * 1000:.0f} -> razao {qq.r[a] / np.median(v2):.2f}")
# quantos municipios-anos de milho no CE tem producao == area (relato redondo), por periodo
m = pam[pam.cod_local.astype(str).str.startswith("23") & pam.produto.str.startswith("Milho (em gr") & (pam.area_plantada_ha >= 50)]
m = m[m.ano.between(1998, 2025)]
rd = (m.producao_t == m.area_plantada_ha)
print(f"  CE: municipio-anos de milho com rendimento exato de 1.000 kg/ha: {rd.sum()} de {len(m)} ({rd.mean():.1%}); "
      f"2016-2025: {rd[m.ano >= 2016].mean():.1%}; 1998-2015: {rd[m.ano < 2016].mean():.1%}")

# ------------------------------------------------------------------ (d) 2016, o analogo de El Nino de 2027
print("\n=== (d) Quadras de El Nino forte na era SMAP: que fracao das quebras do milho cada alerta pegou (recall) ===")
qm = serie("Milho (em gr")
for a in [2016, 2017, 2025]:
    d = qm[qm.ano == a].copy()
    for g, md in PORT.items():
        t = pd.Timestamp(f"{a}-{md}")
        d["acum"] = [IND[(g, "acum")].at[a, c] for c in d.cod]
        d["pctl"] = [PC.at[t, c] for c in d.cod]
        qb = d[d.quebra]
        print(f"  {a} {g}: {len(qb)} municipios quebraram ({d.quebra.mean():.0%}); com alerta de chuva (<75%): "
              f"{(qb.acum < 0.75).mean():.0%}; com alerta SMAP (pctl<25): {(qb.pctl < 25).mean():.0%}; "
              f"falsos alarmes SMAP (alerta sem quebra): {((d.pctl < 25) & ~d.quebra).sum()} de {(~d.quebra).sum()}; "
              f"chuva mediana desde 1/jan {d.acum.median():.0%} do normal; pctl mediano {d.pctl.median():.0f}")

# ------------------------------------------------------------------ (e) regra "duas luzes" (pre-declarada aqui, sem ajuste)
print("\n=== (e) Duas luzes no portao: acende se chuva desde 1/jan < 75% OU agua recente baixa ===")
print("    agua recente = API(tau) < 75% do normal em 1998-2015 (substituto do SMAP); SMAP pctl < 25 em 2016-2025")
for g, md in PORT.items():
    d0 = qm.copy()
    d0["acum"] = [IND[(g, "acum")].at[a, c] if a in IND[(g, "acum")].index else np.nan for a, c in zip(d0.ano, d0.cod)]
    d0["api"] = [IND[(g, "api")].at[a, c] if a in IND[(g, "api")].index else np.nan for a, c in zip(d0.ano, d0.cod)]
    d0["pctl"] = [PC.at[pd.Timestamp(f"{a}-{md}"), c] if a >= 2016 else np.nan for a, c in zip(d0.ano, d0.cod)]
    for per, (a0, a1), rec in [("1998-2015", (1998, 2015), "api"), ("2016-2025", (2016, 2025), "pctl")]:
        d = d0[d0.ano.between(a0, a1)].dropna(subset=["acum", rec])
        lim = 0.75 if rec == "api" else 25
        A1 = d.acum < 0.75
        A2 = A1 | (d[rec] < lim)
        for nome, m in [("so chuva acumulada", A1), ("duas luzes", A2)]:
            rc = (m & d.quebra).sum() / d.quebra.sum()
            print(f"  {g} {per} {nome:18s}: acende em {m.mean():.0%} dos municipio-anos; com luz quebram {d.quebra[m].mean() * 10:.1f} "
                  f"em 10 (n={m.sum()}), sem luz {d.quebra[~m].mean() * 10:.1f} em 10; pega {rc:.0%} das quebras")
