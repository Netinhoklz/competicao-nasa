"""Pesquisador de IA - analise 3: (a) linha do tempo da informacao com intervalos conformais; (b) diversificacao
e fronteira media x CVaR das misturas de culturas.

(a) Para o milho e o feijao (rendimento efetivo por area plantada, anomalia vs mediana de +-14 anos sem o proprio ano),
    um HistGradientBoosting pooled e treinado com o que se SABE em cada data de decisao:
      T0 1/jan : ONI e dipolo TNA-TSA de out-dez + lat/lon/altitude
      T1 1/mar : T0 + chuva de jan e fev (anomalia padronizada no municipio)
      T2 1/mai : T1 + chuva de mar e abr + maior veranico fev-abr
      T3 1/jun : T2 + chuva de mai + maior veranico fev-mai + no de veranicos >= 10 d
    Validacao deixando um ANO de fora. Intervalo conformal de 80% "cross-conformal por ano": para o ano a, a
    meia-largura e o quantil 80% dos |residuos fora da amostra| dos OUTROS anos. Mede-se a cobertura total e na
    seca de 2012-2016 (cobertura condicional), e a probabilidade de quebra (anomalia < -50%) por Brier skill score.
(b) Correlacao das anomalias entre culturas no mesmo municipio e fronteira media x CVaR20 da renda/ha a precos
    constantes (FAOSTAT Brasil, media 2021-2025, R$/t) com cenarios = anos 1998-2025.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import itertools
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
import warnings
warnings.filterwarnings("ignore")

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
P = pd.read_parquet(OUT / "painel_mun_ce.parquet")
ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
ind["data"] = pd.to_datetime(ind["data"])
piv = ind.pivot_table(index="data", columns="variavel", values="valor")
ond = lambda col, a: piv[col][(piv.index >= f"{a-1}-10-01") & (piv.index <= f"{a-1}-12-31")].mean()
for c in ["P_jan", "P_fev", "P_mar", "P_abr", "P_mai", "veranico_max_fev_abr", "veranico_max_fmam", "n_veranico10_fmam"]:
    g = P.groupby("cod")[c]
    P[c + "_z"] = (P[c] - g.transform("mean")) / g.transform("std")
ESTAT = ["lat", "lon", "elev"]
T = {"T0 1/jan": ["ONI", "DIP"] + ESTAT}
T["T1 1/mar"] = T["T0 1/jan"] + ["P_jan_z", "P_fev_z"]
T["T2 1/mai"] = T["T1 1/mar"] + ["P_mar_z", "P_abr_z", "veranico_max_fev_abr_z"]
T["T3 1/jun"] = T["T2 1/mai"] + ["P_mai_z", "veranico_max_fmam_z", "n_veranico10_fmam_z"]

print("(a) linha do tempo da informacao + conformal 80%")
for cult in ["milho", "feijao"]:
    d = pd.read_parquet(OUT / f"anom_{cult}_j14.parquet").reset_index(drop=True)
    d = d.merge(P[["cod", "ano"] + [c for c in P.columns if c.endswith("_z") and c not in d.columns]], on=["cod", "ano"], how="left")
    d["ONI"] = d.ano.map(lambda a: ond("ONI", a))
    d["DIP"] = d.ano.map(lambda a: ond("DIPOLO_TNA_menos_TSA", a))
    y = d.anom.values
    quebra = (y < -0.5).astype(int)
    seca = d.ano.between(2012, 2016).values
    print(f"\n  {cult}: n={len(d)}; quebra (anom < -50%) em {quebra.mean():.0%} dos municipio-anos "
          f"({quebra[seca].mean():.0%} em 2012-16)")
    for tn, cols in T.items():
        X = d[cols].values
        p = np.zeros(len(d))
        pq = np.zeros(len(d))
        for a in sorted(d.ano.unique()):
            tr, te = (d.ano != a).values, (d.ano == a).values
            m = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=15,
                                              min_samples_leaf=40, random_state=0).fit(X[tr], y[tr])
            p[te] = m.predict(X[te])
            c = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05, max_leaf_nodes=15,
                                               min_samples_leaf=40, random_state=0).fit(X[tr], quebra[tr])
            pq[te] = c.predict_proba(X[te])[:, 1]
        res = np.abs(y - p)
        cob = np.zeros(len(d), bool)
        larg = np.zeros(len(d))
        for a in sorted(d.ano.unique()):
            te = (d.ano == a).values
            outros = res[~te]
            n = len(outros)
            q = np.quantile(outros, min(1, np.ceil((n + 1) * 0.8) / n))
            cob[te] = res[te] <= q
            larg[te] = 2 * q
        mse0 = np.mean(y ** 2)
        msss = 1 - np.mean((y - p) ** 2) / mse0
        bclim = np.mean((quebra.mean() - quebra) ** 2)
        bss = 1 - np.mean((pq - quebra) ** 2) / bclim
        # cobertura por ano: pior ano
        cob_ano = pd.Series(cob).groupby(d.ano.values).mean()
        print(f"   {tn}: MSSS={msss:+.3f} | IC80 largura={np.median(larg)*100:.0f} p.p. | cobertura total={cob.mean():.0%}, "
              f"2012-16={cob[seca].mean():.0%}, pior ano={cob_ano.min():.0%} ({cob_ano.idxmin()}) | BSS quebra={bss:+.3f}")
        # conformal "robusto ao ano": a unidade trocavel e o ANO. Para o ano a, meia-largura = quantil 80% (entre os
        # outros anos) do quantil 80% dos |residuos| de cada ano -> garante >=80% de cobertura em ~80% dos anos.
        qa = pd.Series(res).groupby(d.ano.values).quantile(0.8)
        cob2 = np.zeros(len(d), bool)
        larg2 = np.zeros(len(d))
        for a in sorted(d.ano.unique()):
            te = (d.ano == a).values
            outros = qa.drop(a).values
            k = len(outros)
            q2 = np.quantile(outros, min(1, np.ceil((k + 1) * 0.8) / k))
            cob2[te] = res[te] <= q2
            larg2[te] = 2 * q2
        c2a = pd.Series(cob2).groupby(d.ano.values).mean()
        print(f"      robusto ao ano: largura={np.median(larg2)*100:.0f} p.p. | cobertura total={cob2.mean():.0%}, "
              f"2012-16={cob2[seca].mean():.0%}, anos com cobertura >= 80%: {(c2a >= 0.8).mean():.0%} "
              f"(marginal: {(cob_ano >= 0.8).mean():.0%})")

print("\n(b) diversificacao entre culturas (mesmo municipio)")
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.cod_local.str.startswith("23") & pam.ano.between(1998, 2025)]
CULT = {"milho": "Milho (em gr", "feijao": "Feij", "mandioca": "Mandioca", "caju": "Castanha de caju", "fava": "Fava"}
Y = []
for k, pref in CULT.items():
    x = pam[pam.produto.str.startswith(pref)].copy()
    x["y"] = np.where(x.area_plantada_ha > 0, x.producao_t * 1000 / x.area_plantada_ha, np.nan)
    x["area"] = x.area_plantada_ha
    x["cult"] = k
    Y.append(x[["cod_local", "ano", "cult", "y", "area"]])
Y = pd.concat(Y)
Y = Y[Y.groupby(["cod_local", "cult"]).area.transform("median") >= 100]
Y["anom"] = Y.y / Y.groupby(["cod_local", "cult"]).y.transform("median") - 1
W = Y.pivot_table(index=["cod_local", "ano"], columns="cult", values="anom")
# correlacao dentro do municipio (media das correlacoes municipais) e da media estadual
cors = []
for cod, g in W.groupby(level=0):
    if len(g) >= 20:
        cors.append(g.corr(min_periods=20))
Cmed = pd.concat(cors).groupby(level=0).median()
print("  correlacao mediana das anomalias no mesmo municipio (1998-2025):")
print(Cmed.round(2).to_string())
# queda em 2012 (pior ano) por cultura, mediana dos municipios
print("  anomalia mediana em 2012 e 2012-16 por cultura:",
      W.xs(2012, level=1).median().round(2).to_dict(), "|",
      W[W.index.get_level_values(1).isin(range(2012, 2017))].median().round(2).to_dict())

# Licao da 1a rodada: a renda BRUTA/ha a precos FAOSTAT da "100% mandioca" (sem custo, mao de obra nem limite de
# mercado), o que e absurdo -> otimizador ingenuo engana. Aqui a carteira e NORMALIZADA POR VALOR: cada cultura vale 1
# no seu ano mediano (y / mediana municipal). Isso isola a pergunta de RISCO: que mistura protege na seca?
cols = ["milho", "feijao", "mandioca", "caju"]
Yn = Y[Y.cult.isin(cols)].copy()
Yn["idx"] = Yn.y / Yn.groupby(["cod_local", "cult"]).y.transform("median")
R = Yn.pivot_table(index=["cod_local", "ano"], columns="cult", values="idx")
A = Yn[Yn.ano >= 2015].groupby(["cod_local", "cult"]).area.mean().unstack()
grade = [w for w in itertools.product(np.arange(0, 1.01, 0.1), repeat=3) if sum(w) <= 1.0001]
grade = np.array([list(w) + [1 - sum(w)] for w in grade])
SECA = list(range(2012, 2017))


def cvar(r, a=0.2):
    k = max(1, int(np.ceil(a * len(r))))
    return np.sort(r)[:k].mean()


lin = []
for cod, g in R.groupby(level=0):
    g = g[cols].dropna().droplevel(0)
    if len(g) < 25 or not set(SECA) <= set(g.index):
        continue
    M = g.values
    wa = A.loc[cod, cols].fillna(0).values
    wa = wa / wa.sum()
    cv = np.array([cvar(M @ w) for w in grade])
    w_rob = grade[cv.argmax()]
    # fora da amostra: escolhe a mistura SEM ver 2012-16 e avalia na seca
    fora = ~g.index.isin(SECA)
    cv_f = np.array([cvar(M[fora] @ w) for w in grade])
    w_f = grade[cv_f.argmax()]
    Ms = M[~fora]
    lin.append({"cod": cod,
                **{f"cvar_{c}": cvar(M[:, i]) for i, c in enumerate(cols)},
                "cvar_atual": cvar(M @ wa), "cvar_robusta": cv.max(),
                "seca_atual": (Ms @ wa).mean(), "seca_robusta_oos": (Ms @ w_f).mean(),
                "seca_milho": Ms[:, 0].mean(), "seca_feijao": Ms[:, 1].mean(), "seca_milho_feijao_50": (Ms[:, :2] @ [.5, .5]).mean(),
                **{f"w_atual_{c}": v for c, v in zip(cols, wa)}, **{f"w_oos_{c}": v for c, v in zip(cols, w_f)}})
L = pd.DataFrame(lin)
print(f"  municipios com as 4 culturas, >= 25 anos e 2012-16 completos: {len(L)}")
print("  CVaR20 do indice de valor (1 = ano mediano), mediana dos municipios:")
print("   ", L[[c for c in L.columns if c.startswith("cvar_")]].median().round(2).to_dict())
print("  indice medio na seca 2012-16 (mistura escolhida SEM ver a seca):")
print("   ", L[["seca_atual", "seca_robusta_oos", "seca_milho", "seca_feijao", "seca_milho_feijao_50"]].median().round(2).to_dict())
print("  fracao de municipios em que a mistura fora-da-amostra perdeu menos que a atual na seca:",
      f"{(L.seca_robusta_oos > L.seca_atual).mean():.0%}")
print("  pesos medios atual (area 2015+):", L[[f"w_atual_{c}" for c in cols]].mean().round(2).to_dict())
print("  pesos medios robustos (sem ver a seca):", L[[f"w_oos_{c}" for c in cols]].mean().round(2).to_dict())
L.to_parquet(OUT / "carteira_cvar_municipios.parquet")
