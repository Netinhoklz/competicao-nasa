"""Economista agrícola — Análise A3: um gatilho por satélite (IMERG 0,1°) reproduz as quebras tipo Garantia-Safra?

Pergunta: a perda municipal "tipo Garantia-Safra" (>= 50% do valor da produção da cesta milho+feijão+mandioca+arroz+
algodão herbáceo, a preço constante, contra a tendência) é detectável pela chuva do IMERG no próprio município? Qual o
risco de base (perda sem gatilho e gatilho sem perda)? Quanto se ganha com a escala municipal (0,1°) contra a média
estadual? E o ONI antes do plantio antecipa a fração de municípios em perda?

Dados: IMERG V07 diário 0,1° (E:/campeonato-nasa/dados/imerg/imerg_ce_diario_AAAA.nc, via POWER), 1998–2025;
IBGE PAM municipal (ibge_pam_mun_anual); malha municipal IBGE (referencia/ceara_municipios.geojson);
ONI (indices_clima_mensal).
Validação: deixa um ANO inteiro de fora (o choque é espacialmente correlacionado; não vaza entre municípios do mesmo ano).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import xarray as xr
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)

# ---------- 1. Chuva municipal diária
ds = xr.open_mfdataset([str(DADOS / "imerg" / f"imerg_ce_diario_{a}.nc") for a in range(1998, 2026)], combine="by_coords")
pr = ds["precip"].load()  # (time, lat, lon) mm/dia
lon2, lat2 = np.meshgrid(pr.lon.values, pr.lat.values)
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["cod"] = mun.codarea.astype(str)
cols = {}
P = pr.values.reshape(pr.shape[0], -1)
for _, row in mun.iterrows():
    dentro = shapely.contains_xy(row.geometry, lon2.ravel(), lat2.ravel())
    if dentro.sum() == 0:
        c = row.geometry.centroid
        dentro = np.zeros(lon2.size, bool)
        dentro[np.argmin((lon2.ravel() - c.x) ** 2 + (lat2.ravel() - c.y) ** 2)] = True
    cols[row.cod] = np.nanmean(P[:, dentro], axis=1)
chuva = pd.DataFrame(cols, index=pd.to_datetime(pr.time.values))
print("Chuva municipal diária:", chuva.shape)


def maior_seco(x, lim=2.0):
    m = cur = 0
    for v in x:
        cur = cur + 1 if v <= lim else 0
        m = max(m, cur)
    return m


def veranicos(x, lim=2.0, n=3):
    """nº de sequências >= n dias com <= lim mm (definição FUNCEME/Rocha 2021) e dias somados nelas."""
    cont = dias = cur = 0
    for v in list(x) + [lim + 1]:
        if v <= lim:
            cur += 1
        else:
            if cur >= n:
                cont += 1
                dias += cur
            cur = 0
    return cont, dias


feat = []
for ano in range(1998, 2026):
    q = chuva.loc[f"{ano}-02-01":f"{ano}-05-31"]
    jj = chuva.loc[f"{ano}-01-01":f"{ano}-06-30"]
    for c in chuva.columns:
        x = q[c].values
        nv, dv = veranicos(x)
        y = jj[c].values
        s5 = pd.Series(y).rolling(5).sum().values
        ini = int(np.argmax(s5 >= 25)) if (s5 >= 25).any() else 181
        feat.append(dict(cod=c, ano=ano, fmam=x.sum(), jan=chuva.loc[f"{ano}-01-01":f"{ano}-01-31", c].sum(),
                         dias_1mm=(x >= 1).sum(), maior_seco=maior_seco(x), n_veranicos=nv, dias_veranico=dv,
                         inicio=ini, p95=np.percentile(x[x > 0], 95) if (x > 0).any() else 0))
F = pd.DataFrame(feat)
clim = F.groupby("cod")[["fmam", "dias_1mm", "maior_seco", "dias_veranico", "inicio"]].transform("mean")
for v in ["fmam", "dias_1mm", "maior_seco", "dias_veranico", "inicio"]:
    F[v + "_anom"] = F[v] - clim[v]
F["fmam_rel"] = F.fmam / clim.fmam

# ---------- 2. Perda tipo Garantia-Safra (cesta a preço constante vs. tendência)
m = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
CESTA = ["Milho (em grão)", "Feijão (em grão)", "Mandioca", "Arroz (em casca)", "Algodão herbáceo (em caroço)"]
d = m[m.produto.isin(CESTA) & m.ano.between(1998, 2025)]
rec = d[d.ano.between(2019, 2025)]
preco = rec.groupby("produto").valor_mil_moeda.sum() / rec.groupby("produto").producao_t.sum()  # mil R$/t
d = d.assign(v=d.producao_t * d.produto.map(preco))
V = d.groupby(["cod_local", "ano"]).v.sum().rename("valor").reset_index()
perdas = []
for c, g in V.groupby("cod_local"):
    g = g[g.valor > 0]
    if len(g) < 20:
        continue
    t = g.ano.values - 1998
    sl, ic, _, _ = stats.theilslopes(np.log(g.valor.values), t)
    perdas.append(pd.DataFrame({"cod": c, "ano": g.ano.values, "razao": g.valor.values / np.exp(ic + sl * t)}))
L = pd.concat(perdas)
L["perda50"] = (L.razao <= 0.5).astype(int)
D = F.merge(L, on=["cod", "ano"])
print(f"Município-anos: {len(D)} | municípios: {D.cod.nunique()} | frequência de perda >= 50%: {D.perda50.mean():.3f}")
print("Fração de municípios em perda por ano:\n", D.groupby("ano").perda50.mean().round(2).to_string())

# ---------- 3. Modelos de gatilho, deixando um ano de fora
X_cols = ["fmam_rel", "fmam_anom", "dias_1mm_anom", "maior_seco_anom", "dias_veranico_anom", "inicio_anom", "jan", "p95"]
estado = D.groupby("ano")[["fmam"]].mean().rename(columns={"fmam": "fmam_estado"})
D = D.join(estado, on="ano")
D["fmam_estado_rel"] = D.fmam_estado / D.fmam_estado.mean()
y = D.perda50.values
anos = D.ano.values
preds = {k: np.zeros(len(D)) for k in ["limiar chuva FMAM municipal", "limiar chuva FMAM estadual", "logística (8 índices)", "boosting (8 índices)"]}
for a in np.unique(anos):
    tr, te = anos != a, anos == a
    preds["limiar chuva FMAM municipal"][te] = -D.fmam_rel.values[te]
    preds["limiar chuva FMAM estadual"][te] = -D.fmam_estado_rel.values[te]
    lg = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(D.loc[tr, X_cols], y[tr])
    preds["logística (8 índices)"][te] = lg.predict_proba(D.loc[te, X_cols])[:, 1]
    gb = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=300, random_state=0).fit(D.loc[tr, X_cols], y[tr])
    preds["boosting (8 índices)"][te] = gb.predict_proba(D.loc[te, X_cols])[:, 1]

taxa = y.mean()
linhas = []
for nome, s in preds.items():
    auc = roc_auc_score(y, s)
    corte = np.quantile(s, 1 - taxa)  # gatilho que paga na mesma frequência das perdas reais
    g = s >= corte
    linhas.append({"gatilho": nome, "AUC (ano fora)": round(auc, 3),
                   "acerto: perdas pagas": round(g[y == 1].mean(), 3),
                   "perda sem pagamento (risco de base −)": round((~g & (y == 1)).mean(), 3),
                   "pagamento sem perda (risco de base +)": round((g & (y == 0)).mean(), 3),
                   "precisão": round(y[g].mean(), 3)})
print(f"\nGatilhos com a mesma frequência de pagamento das perdas reais ({taxa:.3f}):")
print(pd.DataFrame(linhas).to_string(index=False))

# importância simples: AUC de cada índice isolado
print("\nAUC de cada índice isolado (sinal ajustado):")
for c in X_cols:
    a = roc_auc_score(y, D[c])
    print(f"  {c:20s} {max(a, 1 - a):.3f} ({'maior = perda' if a > 0.5 else 'menor = perda'})")

# ---------- 4. Antes de plantar: o ONI antecipa a fração de municípios em perda?
idx = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
oni = idx["ONI"]
fr = D.groupby("ano").perda50.mean()
oni_aso = pd.Series({a: oni.loc[f"{a - 1}-08-01":f"{a - 1}-10-01"].mean() for a in fr.index})
oni_ondj = pd.Series({a: oni.loc[f"{a - 1}-10-01":f"{a}-01-01"].mean() for a in fr.index})
dip = idx["DIPOLO_TNA_menos_TSA"]
dip_dj = pd.Series({a: dip.loc[f"{a - 1}-12-01":f"{a}-01-01"].mean() for a in fr.index})
for nome, s in [("ONI ago–out (antes)", oni_aso), ("ONI out–jan", oni_ondj), ("Dipolo dez–jan", dip_dj)]:
    rs = stats.spearmanr(s, fr)
    print(f"{nome:22s} × fração de municípios em perda: ρ = {rs.correlation:+.2f} (p = {rs.pvalue:.3f}, n = {len(fr)})")
forte = oni_aso[oni_aso >= 1.0].index
print("Anos com ONI ago–out >= 1,0:", list(forte), "→ fração média em perda", round(fr.loc[forte].mean(), 2),
      "vs. demais", round(fr.drop(forte).mean(), 2))
print("ONI ago–out/2026 (para a quadra de 2027):", round(oni.loc["2026-08-01":"2026-10-01"].mean(), 2),
      "| meses disponíveis:", oni.loc["2026-08-01":].round(2).to_dict())

# ---------- 5. Estado + município: o pixel acrescenta algo ao sinal estadual?
D["desvio_mun_estado"] = D.fmam_rel - D.fmam_estado_rel
X2 = ["fmam_estado_rel", "desvio_mun_estado", "dias_1mm_anom", "dias_veranico_anom"]
p2 = np.zeros(len(D))
for a in np.unique(anos):
    tr, te = anos != a, anos == a
    lg = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(D.loc[tr, X2], y[tr])
    p2[te] = lg.predict_proba(D.loc[te, X2])[:, 1]
preds["logística estado + desvio municipal"] = p2
print("\nAUC dentro do ano (ordena municípios num mesmo ano; anos com 10–90% em perda):")
ruins = [a for a in np.unique(anos) if 0.1 <= y[anos == a].mean() <= 0.9]
for nome, s in preds.items():
    aucs = [roc_auc_score(y[anos == a], s[anos == a]) for a in ruins]
    g = s >= np.quantile(s, 1 - taxa)
    print(f"  {nome:38s} AUC dentro do ano = {np.mean(aucs):.3f} | AUC geral = {roc_auc_score(y, s):.3f} | "
          f"perdas pagas = {g[y == 1].mean():.3f} | precisão = {y[g].mean():.3f}")
print("  anos usados:", ruins)

# ---------- 6. A faixa descoberta: perdas de 25–50% (abaixo do limiar de 50%)
b = pd.cut(D.razao, [0, 0.5, 0.75, 1.0, np.inf], labels=["perda >= 50%", "perda 25–50%", "perda 0–25%", "acima da tendência"])
print("\nDistribuição dos município-anos (cesta a preço constante vs. tendência), 1998–2025:")
print(b.value_counts(normalize=True).round(3).to_string())

# ---------- 7. Limiar novo: a Lei 15.236/2025 baixou a perda mínima do Garantia-Safra de 50% para 40%
y4 = (D.razao <= 0.6).astype(int).values
t4 = y4.mean()
print(f"\nPerda >= 40%: frequência {t4:.3f} (vs {taxa:.3f} com 50%)")
for nome, s in [("limiar chuva FMAM municipal", -D.fmam_rel.values), ("limiar chuva FMAM estadual", -D.fmam_estado_rel.values),
                ("logística (8 índices)", None)]:
    if s is None:
        s = np.zeros(len(D))
        for a in np.unique(anos):
            tr, te = anos != a, anos == a
            lg = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(D.loc[tr, X_cols], y4[tr])
            s[te] = lg.predict_proba(D.loc[te, X_cols])[:, 1]
    g = s >= np.quantile(s, 1 - t4)
    print(f"  {nome:30s} AUC = {roc_auc_score(y4, s):.3f} | perdas pagas = {g[y4 == 1].mean():.3f} | "
          f"perda sem pagamento = {(~g & (y4 == 1)).mean():.3f} | pagamento sem perda = {(g & (y4 == 0)).mean():.3f}")
