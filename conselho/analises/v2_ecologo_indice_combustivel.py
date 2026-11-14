"""Ecologo (rodada 2, dados novos) - Analise 1: indice de combustivel e secura (VIIRS NDVI + SMAP L4 + IMERG)
testado contra os focos FIRMS por municipio, com o ANO como unidade independente.

Painel: saidas/v2_ecologo_painel_mun_mes.parquet (v2_ecologo_painel_combustivel.py).

Definicoes PRE-ESPECIFICADAS (escritas antes de ver o resultado):
  combustivel F_t   = NDVI VIIRS medio de fev-jun do ano t no municipio (biomassa fina produzida na quadra), z por municipio;
  combustivel F_t-1 = o mesmo do ano anterior (acumulo de 2 quadras; Argibay et al. 2020);
  secura D          = 50 - percentil climatologico da zona da raiz do SMAP L4 (sm_rootzone_pctl), dividido por 29
                      (dp de uma uniforme 0-100); positivo = mais seco que o normal;
                      >>> o percentil e NaN em 93-100% dos municipio-meses de out-dez (estacao seca); a primeira rodada
                      (argumento 'pctl', saida *_pctl.saida.txt) so teve 96 municipios no T2. Substituto decidido por
                      COBERTURA, nao por resultado: D = -z(sm_rootzone) por municipio x mes-calendario (2015-2025),
                      argumento 'rz' (padrao); 'sfc' usa sm_surface (sensibilidade).
  chuva R           = chuva IMERG dos 60 dias anteriores (z por municipio x mes-calendario), sinal invertido.
  Indice fixo ICS   = (F_t + F_t-1)/2 + D   (pesos fixos, so a escala e ajustada).
Teste T1 (mensal, previsao de 1 mes): alvo log(1+focos) do mes m em jul-dez; preditores do mes m-1 (D, R) e da quadra.
Teste T2 (portao de entressafra, 30/set): alvo log(1+focos de out-dez); preditores F_t, F_t-1, D de setembro, R jul-set.
Linhas de base: B0 = climatologia do municipio (x mes no T1); B1 = B0 + tendencia linear comum (o fogo e o NDVI
sobem juntos em 2012-2025; sem B1 uma tendencia passaria por habilidade).
Validacao: deixa-um-ano-fora (efeitos fixos e coeficientes so com os anos de treino). Habilidade = 1 - EQM/EQM(base).
IC90 por bootstrap dos ANOS de teste. Modelo principal (pre-registrado) = B1 + F_t + F_t-1 + D. Os demais sao
sensibilidade e nao foram escolhidos olhando o teste.
Anos: SMAP comeca em 31/03/2015 e o FIRMS anual termina em 2025 -> 11 temporadas (2015-2025).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
from scipy import stats

AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
P = pd.read_parquet(AN / "saidas" / "v2_ecologo_painel_mun_mes.parquet")
rng = np.random.default_rng(20261114)

# ---------- preditores por municipio-ano ----------
fj = P[P.m.between(2, 6)].groupby(["codarea", "ano"]).ndvi.mean().rename("F").reset_index()
fj["Fz"] = fj.groupby("codarea").F.transform(lambda s: (s - s.loc[fj.loc[s.index, "ano"] <= 2025].mean())
                                                   / s.loc[fj.loc[s.index, "ano"] <= 2025].std())
fj1 = fj[["codarea", "ano", "Fz"]].copy()
fj1["ano"] += 1
fj1 = fj1.rename(columns={"Fz": "F1z"})
P = P.merge(fj[["codarea", "ano", "Fz"]], on=["codarea", "ano"], how="left").merge(fj1, on=["codarea", "ano"], how="left")
MODO_D = sys.argv[1] if len(sys.argv) > 1 else "rz"
# Cobertura do percentil do SMAP L4 por mes (2015-2025): ele e indefinido (NaN) na estacao seca do Ceara.
cob = P[P.ano.between(2015, 2025)].groupby("m").sm_rootzone_pctl.apply(lambda s: s.notna().mean())
print("Fracao de municipio-meses com sm_rootzone_pctl definido (2015-2025), por mes:",
      ", ".join(f"{k}: {v:.2f}" for k, v in cob.items()))
if MODO_D == "pctl":  # versao pre-especificada original (so existe onde o percentil existe)
    P["D"] = (50 - P.sm_rootzone_pctl) / 29.0
else:  # substituto por cobertura: anomalia padronizada da zona da raiz (m3/m3) por municipio x mes, 2015-2025
    var = "sm_rootzone" if MODO_D == "rz" else "sm_surface"
    cz = P[P.ano.between(2015, 2025)].groupby(["codarea", "m"])[var].agg(["mean", "std"])
    P = P.join(cz, on=["codarea", "m"])
    P["D"] = -(P[var] - P["mean"]) / P["std"]
    P = P.drop(columns=["mean", "std"])
print(f"Secura D = {MODO_D}")
cl = P[P.ano <= 2025].groupby(["codarea", "m"]).P_60.agg(["mean", "std"])
P = P.join(cl, on=["codarea", "m"])
P["R"] = -(P.P_60 - P["mean"]) / P["std"]
P = P.drop(columns=["mean", "std"])
P = P.sort_values(["codarea", "mes"])
for c in ("D", "R", "sm_surface"):
    P[c + "_lag"] = P.groupby("codarea")[c].shift(1)
P["ICS_lag"] = (P.Fz + P.F1z) / 2 + P.D_lag
P["y"] = np.log1p(P.focos)


def loyo(df, X, grupo, anos, trend=True):
    """Previsao deixa-um-ano-fora com efeito fixo 'grupo' (media dos anos de treino) e tendencia opcional.
    Retorna o vetor de previsoes alinhado a df (NaN fora dos anos de teste)."""
    hat = pd.Series(np.nan, index=df.index)
    cols = list(X) + (["t"] if trend else [])
    d = df.copy()
    d["t"] = d.ano - 2020.0
    for a in anos:
        tr, te = d[(d.ano != a) & d.ano.isin(anos)], d[d.ano == a]
        my = tr.groupby(grupo).y.mean()
        if cols:
            mx = tr.groupby(grupo)[cols].mean()
            Xtr = tr[cols].values - mx.loc[tr[grupo]].values
            ytr = tr.y.values - my.loc[tr[grupo]].values
            beta = np.linalg.lstsq(Xtr, ytr, rcond=None)[0]
            te = te[te[grupo].isin(my.index)]
            hat.loc[te.index] = my.loc[te[grupo]].values + (te[cols].values - mx.loc[te[grupo]].values) @ beta
        else:
            te = te[te[grupo].isin(my.index)]
            hat.loc[te.index] = my.loc[te[grupo]].values
    return hat


def habilidade(df, h, h0, nboot=2000):
    e, e0 = (df.y - h) ** 2, (df.y - h0) ** 2
    pa = pd.DataFrame({"ano": df.ano, "e": e, "e0": e0}).groupby("ano")[["e", "e0"]].sum()
    sk = 1 - pa.e.sum() / pa.e0.sum()
    bs = []
    for _ in range(nboot):
        s = pa.iloc[rng.integers(0, len(pa), len(pa))]
        bs.append(1 - s.e.sum() / s.e0.sum())
    lo, hi = np.percentile(bs, [5, 95])
    melhora = int((pa.e < pa.e0).sum())
    return sk, lo, hi, melhora, len(pa)


def relatorio(titulo, df, grupo, anos, modelos):
    print(f"\n{titulo}  (n = {len(df)} linhas, {df[grupo].nunique()} grupos, {len(anos)} anos {min(anos)}-{max(anos)})")
    h0 = loyo(df, [], grupo, anos, trend=False)
    h1 = loyo(df, [], grupo, anos, trend=True)
    sk, lo, hi, mel, n = habilidade(df, h1, h0)
    print(f"  B1 (tendencia) contra B0 (climatologia): habilidade {sk:+.3f} (IC90 {lo:+.3f} a {hi:+.3f}; melhora em {mel}/{n} anos)")
    res = {}
    for nome, X in modelos.items():
        h = loyo(df, X, grupo, anos, trend=True)
        sk1, lo1, hi1, mel1, _ = habilidade(df, h, h1)
        sk0, lo0, hi0, mel0, _ = habilidade(df, h, h0)
        # componente entre anos: media estadual prevista x observada; componente dentro do ano: rho entre municipios
        r = pd.DataFrame({"ano": df.ano, "y": df.y, "h": h, "h1": h1})
        ea = r.groupby("ano")[["y", "h", "h1"]].mean()
        rho_ea = stats.spearmanr(ea.y - ea.h1, ea.h - ea.h1)[0]
        rho_d = r.groupby("ano").apply(lambda g: stats.spearmanr(g.y - g.h1, g.h - g.h1)[0], include_groups=False)
        print(f"  {nome:34s} vs B1 {sk1:+.3f} (IC90 {lo1:+.3f} a {hi1:+.3f}; melhora {mel1}/{n} anos) | vs B0 {sk0:+.3f}"
              f" | rho entre anos (resid. de B1, n={len(ea)}) {rho_ea:+.2f} | rho dentro do ano (mediana) {np.nanmedian(rho_d):+.3f}"
              f" [{(rho_d > 0).sum()}/{len(rho_d)} anos > 0]")
        res[nome] = h
    return res, h0, h1


# ================= T1: mensal jul-dez, previsao de 1 mes =================
T1 = P[P.m.between(7, 12) & P.ano.between(2015, 2025)].dropna(subset=["y", "Fz", "F1z", "D_lag", "R_lag"]).copy()
T1["gm"] = T1.codarea + "_" + T1.m.astype(str)
anos1 = sorted(T1.ano.unique())
mods1 = {
    "so combustivel (F_t, F_t-1)": ["Fz", "F1z"],
    "so secura SMAP (D m-1)": ["D_lag"],
    "so chuva IMERG (R m-1)": ["R_lag"],
    "PRINCIPAL F_t+F_t-1+D": ["Fz", "F1z", "D_lag"],
    "F_t+F_t-1+R (sem SMAP)": ["Fz", "F1z", "R_lag"],
    "F_t+F_t-1+D+R": ["Fz", "F1z", "D_lag", "R_lag"],
    "indice fixo ICS (1 coef.)": ["ICS_lag"],
}
res1, h0_1, h1_1 = relatorio("T1 mensal jul-dez (alvo log1p focos do mes; preditores do mes anterior)", T1, "gm", anos1, mods1)
# Spearman bruto do indice fixo com o residuo de B1 (sem ajuste algum de coeficiente)
r = T1.y - h1_1
print(f"  rho(ICS fixo, residuo de B1) pooled = {stats.spearmanr(T1.ICS_lag, r)[0]:+.3f};"
      f" por mes-calendario: " + ", ".join(f"{mm}: {stats.spearmanr(T1.ICS_lag[T1.m == mm], r[T1.m == mm])[0]:+.2f}" for mm in range(7, 13)))

# ================= T2: portao de entressafra (30/set) -> focos out-dez =================
od = P[P.m.isin([10, 11, 12])].groupby(["codarea", "ano"]).focos.sum(min_count=3).rename("focos_od").reset_index()
se = P[P.m == 9][["codarea", "ano", "Fz", "F1z", "D", "sm_surface"]]
js = P[P.m.isin([7, 8, 9])].groupby(["codarea", "ano"]).P_mes.sum(min_count=3).rename("P_jas").reset_index()
T2 = od.merge(se, on=["codarea", "ano"]).merge(js, on=["codarea", "ano"], how="left")
T2["Rjas"] = -T2.groupby("codarea").P_jas.transform(lambda s: (s - s.mean()) / s.std())
T2["y"] = np.log1p(T2.focos_od)
T2["ICS"] = (T2.Fz + T2.F1z) / 2 + T2.D
T2a = T2[T2.ano.between(2015, 2025)].dropna(subset=["y", "Fz", "F1z", "D", "Rjas"]).copy()
mods2 = {
    "so combustivel (F_t, F_t-1)": ["Fz", "F1z"],
    "so secura SMAP set (D)": ["D"],
    "so chuva IMERG jul-set (R)": ["Rjas"],
    "PRINCIPAL F_t+F_t-1+D": ["Fz", "F1z", "D"],
    "F_t+F_t-1+R (sem SMAP)": ["Fz", "F1z", "Rjas"],
    "F_t+F_t-1+D+R": ["Fz", "F1z", "D", "Rjas"],
    "indice fixo ICS (1 coef.)": ["ICS"],
}
res2, h0_2, h1_2 = relatorio("T2 portao 30/set -> focos out-dez por municipio", T2a, "codarea", sorted(T2a.ano.unique()), mods2)
# replica do M7 com VIIRS no lugar do MODIS, mais anos (2013-2025) sem SMAP
T2b = T2[T2.ano.between(2013, 2025)].dropna(subset=["y", "Fz", "F1z"]).copy()
relatorio("T2' replica M7 com VIIRS (so combustivel), 2013-2025", T2b, "codarea", sorted(T2b.ano.unique()),
          {"combustivel F_t, F_t-1": ["Fz", "F1z"], "so F_t-1": ["F1z"]})

# coeficientes do modelo principal em todos os anos (para leitura do sinal)
d = T2a.copy()
d["t"] = d.ano - 2020.0
cols = ["Fz", "F1z", "D", "t"]
Xd = d[cols] - d.groupby("codarea")[cols].transform("mean")
yd = d.y - d.groupby("codarea").y.transform("mean")
import statsmodels.api as sm
m = sm.OLS(yd, Xd).fit(cov_type="cluster", cov_kwds={"groups": d.ano})
print("\nT2 modelo principal, todos os anos, EF de municipio, EP agrupado por ano (11 grupos: p e indicativo):")
print("  " + " | ".join(f"{c} {m.params[c]:+.3f} (EP {m.bse[c]:.3f}, p={m.pvalues[c]:.3f})" for c in cols))

# observado x previsto (estado) por ano no modelo principal
r2 = pd.DataFrame({"ano": T2a.ano, "obs": T2a.focos_od, "y": T2a.y, "h": res2["PRINCIPAL F_t+F_t-1+D"], "h1": h1_2})
ea = r2.groupby("ano").agg(focos=("obs", "sum"), y=("y", "mean"), h=("h", "mean"), h1=("h1", "mean"))
ea["anom_obs"] = ea.y - ea.h1
ea["anom_prev"] = ea.h - ea.h1
print("\nT2 por ano (estado): focos out-dez observados; anomalia media de log1p contra B1, observada e prevista fora do ano")
print(ea.round(3).to_string())

# ================= Previsao pre-registrada out-dez/2026 =================
d = T2[T2.ano.between(2015, 2025)].dropna(subset=["y", "Fz", "F1z", "D"]).copy()
d["t"] = d.ano - 2020.0
mx = d.groupby("codarea")[cols].mean()
my = d.groupby("codarea").y.mean()
beta = np.linalg.lstsq((d[cols] - mx.loc[d.codarea].values).values, (d.y - my.loc[d.codarea].values).values, rcond=None)[0]
z26 = T2[T2.ano == 2026].dropna(subset=["Fz", "F1z", "D"]).copy()
z26["t"] = 6.0
z26["h"] = my.loc[z26.codarea].values + (z26[cols].values - mx.loc[z26.codarea].values) @ beta
z26["h_tend"] = my.loc[z26.codarea].values + (z26[["t"]].values - mx.loc[z26.codarea, ["t"]].values) @ beta[[3]]
print(f"\nPREVISAO PRE-REGISTRADA out-dez/2026 (modelo principal ajustado em 2015-2025; {len(z26)} municipios)")
print(f"  preditores 2026 (medianas entre municipios): F_t {z26.Fz.median():+.2f} dp | F_t-1 {z26.F1z.median():+.2f} dp |"
      f" D set/2026 {z26.D.median():+.2f} ({'pctl mediano %.0f' % (50 - 29 * z26.D.median()) if MODO_D == 'pctl' else 'z de secura, ' + MODO_D})")
print(f"  anomalia prevista sobre a tendencia (media de log1p): {(z26.h - z26.h_tend).mean():+.3f};"
      f" municipios acima da propria tendencia: {(z26.h > z26.h_tend).mean() * 100:.0f}%")
tot = np.expm1(z26.h).sum()
tot_t = np.expm1(z26.h_tend).sum()
print(f"  soma expm1 prevista: ~{tot:,.0f} focos (so tendencia: ~{tot_t:,.0f}); observado 2015-2025 out-dez:"
      f" media {ea.focos.mean():,.0f}, min {ea.focos.min():,.0f}, max {ea.focos.max():,.0f}")
print("  Conferir quando o FIRMS de 2026 sair (arquivo anual ou NRT com MAP_KEY).")
