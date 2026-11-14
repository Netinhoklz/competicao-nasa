"""Estrategista - Analise 1: "o que o oceano de HOJE (jul-set) diz sobre a quadra e a safra do ano que vem".

Pergunta: com o que se sabe em novembro (ONI e dipolo do Atlantico de jul-set do ano Y-1), da para dar
probabilidade de quadra seca e de quebra de milho/feijao no ano Y? O que aconteceu nos anos analogos
de El Nino forte? Qual a probabilidade para 2027 com o ONI de jul-set/2026?

Dados: indices_clima_mensal (ONI, TNA-TSA), power_ce_mensal (PRECTOTCORR, 1981+), imerg_ce_mensal (1998+),
ibge_pam_ce_anual (rendimento milho/feijao/mandioca, 1974-2025).
Validacao: deixar 1 ano de fora (LOYO), RPSS para tercis, AUC/Brier para quebra.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from comum import DERIV

pd.set_option("display.width", 200)

ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
ind["data"] = pd.to_datetime(ind.data)
I = ind.pivot_table(index="data", columns="variavel", values="valor")


def media_janela(s, ano, meses_ano_anterior):
    """media de meses do ano anterior (ex.: [7,8,9])."""
    idx = [pd.Timestamp(ano - 1, m, 1) for m in meses_ano_anterior]
    v = s.reindex(idx)
    return v.mean() if v.notna().all() else np.nan


anos = range(1951, 2028)
X = pd.DataFrame({
    "ONI_jas": {a: media_janela(I["ONI"], a, [7, 8, 9]) for a in anos},
    "DIP_jas": {a: media_janela(I["DIPOLO_TNA_menos_TSA"], a, [7, 8, 9]) for a in anos},
    "ONI_ondj": {a: np.nanmean([I["ONI"].get(pd.Timestamp(a - 1, m, 1), np.nan) for m in (10, 11, 12)] + [I["ONI"].get(pd.Timestamp(a, 1, 1), np.nan)]) for a in anos},
})
print("Preditores conhecidos em nov/2026 para a quadra de 2027:")
print(X.loc[2027, ["ONI_jas", "DIP_jas"]].round(2).to_string())

# ---- chuva fev-mai (POWER, mm/dia mensal -> mm/mes)
pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw["data"] = pd.to_datetime(pw.data)
pr = pw[pw.variavel == "PRECTOTCORR"].set_index("data")["valor"]
# valores ja sao totais mensais (mm/mes; media ~69 mm/mes), nao converter
fmam = pr[pr.index.month.isin([2, 3, 4, 5])]
cnt = fmam.groupby(fmam.index.year).count()
fmam = fmam.groupby(fmam.index.year).sum()[cnt == 4]

im = pd.read_parquet(DERIV / "imerg_ce_mensal.parquet")
im["data"] = pd.to_datetime(im.data)
ip = im[im.variavel == "precip_total"].set_index("data")["valor"]
fi = ip[ip.index.month.isin([2, 3, 4, 5])]
ci = fi.groupby(fi.index.year).count()
fmam_imerg = fi.groupby(fi.index.year).sum()[ci == 4]
j = pd.concat([fmam.rename("power"), fmam_imerg.rename("imerg")], axis=1).dropna()
print(f"\nFMAM POWER x IMERG (1998+): r={j.power.corr(j.imerg):.2f}, n={len(j)}")

# ---- rendimento estadual (desvio da mediana movel de 7 anos)
pam = pd.read_parquet(DERIV / "ibge_pam_ce_anual.parquet")
pam["ano"] = pd.to_datetime(pam.data).dt.year
rend = pam[pam.variavel == "rendimento_kg_ha"].pivot_table(index="ano", columns="produto", values="valor")
cult = {c: [k for k in rend.columns if k.startswith(c)][0] for c in ["Milho (em", "Feij", "Mandioca"]}
R = pd.DataFrame({nome.split(" ")[0]: rend[c] for nome, c in cult.items()})
R.columns = ["milho", "feijao", "mandioca"]
razao = R / R.rolling(7, center=True, min_periods=3).median()

D = X.join(fmam.rename("fmam_mm")).join(razao)
D = D.loc[1975:2025]

print("\n=== Correlacoes (ano Y) com preditores de jul-set de Y-1 (conhecidos em novembro) ===")
for alvo in ["fmam_mm", "milho", "feijao", "mandioca"]:
    for p_ in ["ONI_jas", "DIP_jas", "ONI_ondj"]:
        d = D[[p_, alvo]].dropna()
        rs, ps = stats.spearmanr(d[p_], d[alvo])
        print(f"  {alvo:9s} x {p_:9s}: Spearman={rs:+.2f} (p={ps:.3f}, n={len(d)})")

# ---- analogos: El Nino em jul-set do ano anterior
print("\n=== Anos analogos (ONI jul-set do ano anterior) ===")
D["classe"] = pd.cut(D.ONI_jas, [-9, -0.5, 0.5, 1.0, 9], labels=["La Nina", "neutro", "El Nino moderado", "El Nino forte (>=1.0)"])
tab = D.groupby("classe").agg(anos=("milho", "size"), fmam_mm=("fmam_mm", "mean"),
                              milho_razao=("milho", "mean"), feijao_razao=("feijao", "mean"), mandioca_razao=("mandioca", "mean"),
                              p_quebra_milho_lt60=("milho", lambda s: (s < 0.6).mean()))
print(tab.round(2).to_string())
fortes = D[D.ONI_jas >= 1.0][["ONI_jas", "DIP_jas", "fmam_mm", "milho", "feijao", "mandioca"]]
print("\nAnos com ONI jul-set >= 1.0 no ano anterior:")
print(fortes.round(2).to_string())
print("Media milho razao nos fortes:", round(fortes.milho.mean(), 2), " | demais anos:", round(D[D.ONI_jas < 1.0].milho.mean(), 2))
print("Media feijao razao nos fortes:", round(fortes.feijao.mean(), 2), " | demais anos:", round(D[D.ONI_jas < 1.0].feijao.mean(), 2))
print("Media mandioca razao nos fortes:", round(fortes.mandioca.mean(), 2), " | demais anos:", round(D[D.ONI_jas < 1.0].mandioca.mean(), 2))

# ---- modelo de tercil com LOYO e previsao 2027
dd = D[["ONI_jas", "DIP_jas", "fmam_mm"]].dropna()
q1, q2 = dd.fmam_mm.quantile([1 / 3, 2 / 3])
y = np.where(dd.fmam_mm <= q1, 0, np.where(dd.fmam_mm >= q2, 2, 1))
feats = ["ONI_jas", "DIP_jas"]
rps_m, rps_c, hits = [], [], []
for i in range(len(dd)):
    tr = np.ones(len(dd), bool)
    tr[i] = False
    m = LogisticRegression(C=1.0, max_iter=2000).fit(dd[feats].values[tr], y[tr])
    p = m.predict_proba(dd[feats].values[i:i + 1])[0]
    o = np.eye(3)[y[i]]
    rps_m.append(np.sum((np.cumsum(p) - np.cumsum(o)) ** 2) / 2)
    rps_c.append(np.sum((np.cumsum(np.full(3, 1 / 3)) - np.cumsum(o)) ** 2) / 2)
    hits.append(int(np.argmax(p) == y[i]))
print(f"\nTercil FMAM (POWER {dd.index.min()}-{dd.index.max()}, n={len(dd)}) com ONI+dipolo de JUL-SET do ano anterior:")
print(f"  acerto LOYO={np.mean(hits):.0%} (acaso 33%)  RPSS={1 - np.mean(rps_m) / np.mean(rps_c):+.3f}")
m = LogisticRegression(C=1.0, max_iter=2000).fit(dd[feats].values, y)
p27 = m.predict_proba(X.loc[[2027], feats].values)[0]
print(f"  Previsao 2027 (ONI_jas={X.loc[2027, 'ONI_jas']:.2f}, DIP_jas={X.loc[2027, 'DIP_jas']:.2f}): "
      f"P(seco)={p27[0]:.0%} P(normal)={p27[1]:.0%} P(chuvoso)={p27[2]:.0%}")

# ---- quebra de milho (razao < 0.6) com LOYO
de = D[["ONI_jas", "DIP_jas", "milho"]].dropna()
yb = (de.milho < 0.6).astype(int).values
pr_ = []
for i in range(len(de)):
    tr = np.ones(len(de), bool)
    tr[i] = False
    mb = LogisticRegression(C=1.0, max_iter=2000).fit(de[feats].values[tr], yb[tr])
    pr_.append(mb.predict_proba(de[feats].values[i:i + 1])[0, 1])
pr_ = np.array(pr_)
bs = brier_score_loss(yb, pr_)
bsc = brier_score_loss(yb, np.full(len(yb), yb.mean()))
print(f"\nQuebra de milho (rendimento < 60% da mediana movel), {de.index.min()}-{de.index.max()}, taxa base={yb.mean():.0%}:")
print(f"  AUC LOYO={roc_auc_score(yb, pr_):.2f}  BSS={1 - bs / bsc:+.3f}")
mb = LogisticRegression(C=1.0, max_iter=2000).fit(de[feats].values, yb)
print(f"  P(quebra de milho em 2027 | oceano jul-set/2026) = {mb.predict_proba(X.loc[[2027], feats].values)[0, 1]:.0%}")

# ---- robustez: persistencia do ONI (jul-set -> out-jan) e modelos com 1 preditor
d2 = X[["ONI_jas", "ONI_ondj"]].dropna().loc[1951:2026]
print(f"\nPersistencia ONI jul-set(Y-1) -> out-jan: r={d2.ONI_jas.corr(d2.ONI_ondj):.2f} (n={len(d2)})")
fortes_jas = d2[d2.ONI_jas >= 1.5]
print(f"  anos com ONI_jas>=1.5: {len(fortes_jas)}; ONI_ondj minimo nesses anos = {fortes_jas.ONI_ondj.min():.2f}")


def tercil_loyo(cols):
    dd = D[cols + ["fmam_mm"]].dropna()
    q1, q2 = dd.fmam_mm.quantile([1 / 3, 2 / 3])
    y = np.where(dd.fmam_mm <= q1, 0, np.where(dd.fmam_mm >= q2, 2, 1))
    rm, rc, h = [], [], []
    for i in range(len(dd)):
        tr = np.ones(len(dd), bool); tr[i] = False
        m = LogisticRegression(C=0.5, max_iter=2000).fit(dd[cols].values[tr], y[tr])
        p = m.predict_proba(dd[cols].values[i:i + 1])[0]
        o = np.eye(3)[y[i]]
        rm.append(np.sum((np.cumsum(p) - np.cumsum(o)) ** 2) / 2)
        rc.append(np.sum((np.cumsum(np.full(3, 1 / 3)) - np.cumsum(o)) ** 2) / 2)
        h.append(int(np.argmax(p) == y[i]))
    m = LogisticRegression(C=0.5, max_iter=2000).fit(dd[cols].values, y)
    return np.mean(h), 1 - np.mean(rm) / np.mean(rc), m, len(dd)


DIPo = {a: np.nanmean([I["DIPOLO_TNA_menos_TSA"].get(pd.Timestamp(a - 1, m, 1), np.nan) for m in (10, 11, 12)]
                      + [I["DIPOLO_TNA_menos_TSA"].get(pd.Timestamp(a, 1, 1), np.nan)]) for a in anos}
D["DIP_ondj"] = pd.Series(DIPo)
for cols in (["ONI_jas"], ["ONI_jas", "DIP_jas"], ["ONI_ondj"], ["ONI_ondj", "DIP_ondj"]):
    h, rpss, m, n = tercil_loyo(cols)
    extra = ""
    if cols == ["ONI_jas"]:
        p = m.predict_proba(X.loc[[2027], cols].values)[0]
        extra = f" | 2027: P(seco)={p[0]:.0%} P(normal)={p[1]:.0%} P(chuvoso)={p[2]:.0%}"
    if cols == ["ONI_ondj"]:
        for v in (1.5, 2.0, 2.5):
            p = m.predict_proba(np.array([[v]]))[0]
            extra += f" | se ONI_ondj={v}: P(seco)={p[0]:.0%}"
    print(f"Tercil {'+'.join(cols):18s} n={n}: acerto={h:.0%} RPSS={rpss:+.3f}{extra}")

# chuva FMAM nos analogos fortes vs climatologia
clim = D.fmam_mm.dropna()
print(f"\nFMAM medio (POWER) 1981-2025 = {clim.mean():.0f} mm; tercil inferior <= {clim.quantile(1/3):.0f} mm")
print("FMAM nos anos com ONI_jas>=1.0:", D.loc[D.ONI_jas >= 1.0, "fmam_mm"].round(0).to_dict())
