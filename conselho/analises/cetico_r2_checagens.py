"""Cetico, rodada 2: checagens rapidas de afirmacoes de outros especialistas.

A. Curva de antecedencia (designer/estrategista): IC por bootstrap em BLOCOS DE ANO e AUC DENTRO do ano.
   Pergunta: quanto da AUC 0,65-0,77 e discriminacao entre anos (n efetivo ~28) e quanto e local?
B. Falso inicio (agronomo, portao G2): o efeito sobrevive a efeito fixo de ANO (choque regional)?
C. Adaptacao ja existente: a area plantada de milho/feijao ja responde ao ONI e a chuva de janeiro?
D. Mandioca como "amortecedor": a serie do PAM e suavizada (autocorrelacao) ou defasada (responde a chuva de t-1)?
E. Verde na seca x GRACE no Sertao Central (sr_fundacao): rho sem 2022.
Dados: saidas/designer_chuva_mun_diaria.parquet (IMERG V07 diario por municipio), ibge_pam_mun_anual.parquet,
       indices_clima_mensal.parquet, grace_aoi_mensal.parquet, sr_fundacao_irrigacao_anual.csv.
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
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.metrics import roc_auc_score

AN = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
OUT = AN / "saidas"
rng = np.random.default_rng(42)

chuva = pd.read_parquet(OUT / "designer_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(str)
ANOS = list(range(1998, 2026))


def serie(prefixo, min_area=100):
    s = pam[pam.produto.str.startswith(prefixo) & (pam.ano >= 1990)].copy()
    s = s.groupby(["cod", "ano"], as_index=False)[["producao_t", "area_plantada_ha", "area_colhida_ha"]].sum()
    s["rp"] = np.where(s.area_plantada_ha >= min_area, s.producao_t * 1000 / s.area_plantada_ha.replace(0, np.nan), np.nan)
    s = s.sort_values(["cod", "ano"])
    s["tend"] = s.groupby("cod")["rp"].transform(lambda v: v.rolling(7, center=True, min_periods=4).median())
    s["razao"] = s.rp / s.tend
    s["quebra"] = (s.razao < 0.5).astype(float).where(s.razao.notna())
    return s


milho = serie("Milho (em gr")
feijao = serie("Feij")

# ------------------------------------------------------------------ A
print("=" * 90)
print("A. Curva de antecedencia: AUC agrupada x IC por bootstrap de ANOS x AUC dentro do ano (milho)")
cube = np.stack([chuva.loc[pd.Timestamp(a, 1, 1):].iloc[:151].values for a in ANOS])
q = milho.set_index(["cod", "ano"]).quebra
res = []
for nome, nd in {"28/fev": 59, "31/mar": 90, "30/abr": 120}.items():
    acc = cube[:, :nd, :].sum(1)
    pct = np.empty_like(acc)
    for k in range(len(ANOS)):
        pct[k] = acc[k] / np.median(np.delete(acc, k, axis=0), axis=0)
    F = pd.DataFrame(pct, index=ANOS, columns=chuva.columns).stack().rename("pct").reset_index()
    F.columns = ["ano", "cod", "pct"]
    F = F.join(q, on=["cod", "ano"]).dropna()
    auc = roc_auc_score(F.quebra, -F.pct)
    # bootstrap em blocos de ano
    grupos = {a: g for a, g in F.groupby("ano")}
    bs_auc, bs_rr = [], []
    for _ in range(1000):
        amostra = pd.concat([grupos[a] for a in rng.choice(ANOS, len(ANOS))])
        if amostra.quebra.nunique() < 2:
            continue
        bs_auc.append(roc_auc_score(amostra.quebra, -amostra.pct))
        al = amostra.pct < 0.75
        if al.any() and (~al).any():
            bs_rr.append(amostra.quebra[al].mean() / max(amostra.quebra[~al].mean(), 1e-9))
    # AUC dentro do ano (media ponderada pelos anos com as duas classes)
    dentro = []
    for a, g in F.groupby("ano"):
        if g.quebra.sum() >= 5 and (1 - g.quebra).sum() >= 5:
            dentro.append((roc_auc_score(g.quebra, -g.pct), len(g)))
    auc_dentro = np.average([d[0] for d in dentro], weights=[d[1] for d in dentro])
    # AUC so com o nivel do ano (media estadual do pct atribuida a todos os municipios)
    F["pct_ano"] = F.groupby("ano").pct.transform("mean")
    auc_ano = roc_auc_score(F.quebra, -F.pct_ano)
    al = F.pct < 0.75
    rr = F.quebra[al].mean() / F.quebra[~al].mean()
    res.append(dict(data=nome, AUC=round(auc, 3), IC90_anos=f"{np.percentile(bs_auc,5):.2f}-{np.percentile(bs_auc,95):.2f}",
                    AUC_so_nivel_do_ano=round(auc_ano, 3), AUC_dentro_do_ano=round(auc_dentro, 3), anos_validos_dentro=len(dentro),
                    razao_risco_alerta75=round(rr, 2), IC90_razao=f"{np.percentile(bs_rr,5):.1f}-{np.percentile(bs_rr,95):.1f}"))
print(pd.DataFrame(res).to_string(index=False))

# ------------------------------------------------------------------ B
print("=" * 90)
print("B. Falso inicio apos 1a chuva de plantio (>=20 mm em 3 d desde 1/jan): efeito com e sem efeito fixo de ANO")
linhas = []
for a in ANOS:
    bloco = chuva.loc[pd.Timestamp(a, 1, 1):pd.Timestamp(a, 6, 30)]
    v = bloco.values  # (dias, mun)
    s3 = pd.DataFrame(v).rolling(3).sum().values
    for j, cod in enumerate(chuva.columns):
        idx = np.where(s3[:, j] >= 20)[0]
        if len(idx) == 0 or idx[0] > 120:
            continue
        p = idx[0] + 1
        jan = p <= 31
        prox = v[p:p + 30, j] < 1
        # maior sequencia de dias secos nos 30 dias seguintes
        mx, cur = 0, 0
        for d in prox:
            cur = cur + 1 if d else 0
            mx = max(mx, cur)
        fm = bloco.loc[pd.Timestamp(a, 2, 1):pd.Timestamp(a, 5, 31)].iloc[:, j].sum()
        linhas.append(dict(cod=cod, ano=a, jan=int(jan), fi=int(mx >= 10), chuva_fm=fm / 100))
P = pd.DataFrame(linhas).merge(milho[["cod", "ano", "quebra", "razao"]], on=["cod", "ano"]).dropna()
P["lr"] = np.log(P.razao.clip(0.02, 5))
print(f"n = {len(P)} municipio-anos; falso inicio em {P.fi.mean():.1%}; plantio em janeiro em {P.jan.mean():.1%}")
for rot, f in [("FE municipio + chuva (como o agronomo)", "quebra ~ fi*jan + chuva_fm + C(cod)"),
               ("FE municipio + FE ANO + chuva", "quebra ~ fi*jan + chuva_fm + C(cod) + C(ano)")]:
    m = smf.ols(f, data=P).fit(cov_type="cluster", cov_kwds={"groups": P.ano})
    efeito_jan = m.params["fi"] + m.params["fi:jan"]
    cov = m.cov_params().loc[["fi", "fi:jan"], ["fi", "fi:jan"]].values.sum()
    print(f"  {rot}: efeito de FI apos plantio em JAN na P(quebra) = {efeito_jan:+.3f} (EP cluster-ano {np.sqrt(cov):.3f}); "
          f"apos FEV+ = {m.params['fi']:+.3f} (EP {m.bse['fi']:.3f})")
for rot, f in [("log-razao, FE mun + chuva", "lr ~ fi*jan + chuva_fm + C(cod)"),
               ("log-razao, FE mun + FE ano + chuva", "lr ~ fi*jan + chuva_fm + C(cod) + C(ano)")]:
    m = smf.ols(f, data=P).fit(cov_type="cluster", cov_kwds={"groups": P.ano})
    efeito_jan = m.params["fi"] + m.params["fi:jan"]
    cov = m.cov_params().loc[["fi", "fi:jan"], ["fi", "fi:jan"]].values.sum()
    print(f"  {rot}: FI apos JAN = {efeito_jan:+.3f} log (EP {np.sqrt(cov):.3f}); FI apos FEV+ = {m.params['fi']:+.3f} (EP {m.bse['fi']:.3f})")
fr = P.groupby("ano").agg(fi_jan=("fi", lambda x: (x * P.loc[x.index, "jan"]).mean()), quebra=("quebra", "mean"))
print("  correlacao entre ANOS (fracao com FI apos jan x fracao em quebra):", round(stats.spearmanr(fr.fi_jan, fr.quebra)[0], 2))

# ------------------------------------------------------------------ C
print("=" * 90)
print("C. O agricultor ja adapta? area plantada do estado x ONI (NDJ do ano anterior) e chuva de janeiro")
ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
ind["data"] = pd.to_datetime(ind["data"])
oni = ind[ind.variavel == "ONI"].set_index("data")["valor"]
oni_ndj = {a: oni.get(pd.Timestamp(a - 1, 12, 1), np.nan) for a in ANOS}
chuva_jan = {a: chuva.loc[pd.Timestamp(a, 1, 1):pd.Timestamp(a, 1, 31)].sum().mean() for a in ANOS}
chuva_fm = {a: chuva.loc[pd.Timestamp(a, 2, 1):pd.Timestamp(a, 5, 31)].sum().mean() for a in ANOS}
for nome, s in [("milho", milho), ("feijao", feijao)]:
    tot = s.groupby("ano").area_plantada_ha.sum()
    tot = tot[(tot.index >= 1990)]
    la = np.log(tot)
    tr = la.rolling(5).median().shift(1)  # so o passado
    an = (la - tr).loc[ANOS].dropna()
    o = pd.Series(oni_ndj).loc[an.index]
    cj = pd.Series(chuva_jan).loc[an.index]
    cf = pd.Series(chuva_fm).loc[an.index]
    r1, p1 = stats.spearmanr(an, o)
    r2, p2 = stats.spearmanr(an, cj)
    r3, p3 = stats.spearmanr(an, cf)
    perda = (1 - s.groupby("ano").area_colhida_ha.sum() / s.groupby("ano").area_plantada_ha.sum()).loc[an.index]
    print(f"  {nome}: anomalia da area plantada x ONI NDJ rho={r1:+.2f} (p={p1:.2f}); x chuva jan rho={r2:+.2f} (p={p2:.2f}); "
          f"x chuva fev-mai rho={r3:+.2f} (p={p3:.2f})")
    elnino = o >= 1.0
    print(f"     anos ONI NDJ>=1 {list(an.index[elnino])}: anomalia mediana da area {an[elnino].median():+.1%} x demais {an[~elnino].median():+.1%}; "
          f"perda de area mediana {perda.median():.1%}")

# ------------------------------------------------------------------ D
print("=" * 90)
print("D. Series do PAM por cultura: autocorrelacao do desvio (suavizacao?) e resposta a chuva de t e t-1")
chuva_fm_mun = pd.DataFrame({a: chuva.loc[pd.Timestamp(a, 2, 1):pd.Timestamp(a, 5, 31)].sum() for a in range(1998, 2027)}).T
chuva_fm_mun.index.name = "ano"
cfm = chuva_fm_mun.stack().rename("cfm").reset_index().rename(columns={"level_1": "cod"})
cfm["cod"] = cfm["cod"].astype(str)
cfm["cfm_z"] = cfm.groupby("cod").cfm.transform(lambda v: (v - v.mean()) / v.std())
lag = cfm[["cod", "ano", "cfm_z"]].copy()
lag["ano"] += 1
lag = lag.rename(columns={"cfm_z": "cfm_z_lag"})
for nome, pref in [("milho", "Milho (em gr"), ("feijao", "Feij"), ("mandioca", "Mandioca"), ("castanha de caju", "Castanha de caju")]:
    s = serie(pref, min_area=50)
    s["d"] = np.log(s.razao.clip(0.02, 5))
    s["d_lag"] = s.groupby("cod").d.shift(1)
    ok = s[["d", "d_lag"]].dropna()
    ac = stats.spearmanr(ok.d, ok.d_lag)[0]
    rep = s.groupby("cod").rp.apply(lambda v: (v.diff().abs() < 1e-6).mean())  # fracao de anos com rendimento identico ao anterior
    m = s.merge(cfm[["cod", "ano", "cfm_z"]], on=["cod", "ano"]).merge(lag, on=["cod", "ano"])
    m = m[m.ano.between(1999, 2025)].dropna(subset=["d", "cfm_z", "cfm_z_lag"])
    r_t = stats.spearmanr(m.d, m.cfm_z)[0]
    r_l = stats.spearmanr(m.d, m.cfm_z_lag)[0]
    print(f"  {nome:17s} n={len(m):5d}  autocorr(desvio t,t-1)={ac:+.2f}  rho(desvio, chuva fev-mai t)={r_t:+.2f}  "
          f"rho(desvio, chuva t-1)={r_l:+.2f}  anos c/ rendimento identico ao anterior (mediana mun.)={rep.median():.0%}")

# ------------------------------------------------------------------ E
print("=" * 90)
print("E. Verde na seca x GRACE (Sertao Central): sensibilidade a 2022")
ir = pd.read_csv(AN / "sr_fundacao_irrigacao_anual.csv")
g = pd.read_parquet(DERIV / "grace_aoi_mensal.parquet")
g["data"] = pd.to_datetime(g["data"])
for aoi in ["sertao_central", "cariri", "apodi_jaguaribe"]:
    ga = g[g.aoi == aoi]
    if ga.empty:
        print("  sem GRACE para", aoi)
        continue
    gad = ga[ga.data.dt.month.isin([8, 9, 10, 11, 12])].groupby(ga.data.dt.year).valor.mean()
    x = ir[ir.aoi == aoi].set_index("ano").pct_irrig_ativa
    j = pd.concat([x, gad.rename("grace")], axis=1).dropna()
    r_all = stats.spearmanr(j.pct_irrig_ativa, j.grace)
    s22 = j.drop(2022, errors="ignore")
    r_22 = stats.spearmanr(s22.pct_irrig_ativa, s22.grace)
    sem2 = j.drop([2013, 2022], errors="ignore")
    r_2 = stats.spearmanr(sem2.pct_irrig_ativa, sem2.grace)
    print(f"  {aoi}: n={len(j)} rho={r_all[0]:+.2f} (p={r_all[1]:.3f}); sem 2022 rho={r_22[0]:+.2f} (p={r_22[1]:.3f}); "
          f"sem 2013 e 2022 rho={r_2[0]:+.2f} (p={r_2[1]:.3f})")
