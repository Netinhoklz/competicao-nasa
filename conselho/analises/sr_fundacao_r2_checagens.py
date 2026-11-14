"""Conselho - sensoriamento remoto, RODADA 2. Tres checagens para o debate.

A) O ensaio de downscaling (R2 0,44) sobrevive a deriva da LST diurna do MODIS Terra apontada pelo Cetico
   (-4,6 C em 2026)? E o que importa para downscaling e a habilidade ESPACIAL dentro do mes (o nivel do mes
   vem do proprio SMAP), nao a temporal. Testo: R2 por grupo de anos de teste, modelo sem LST diurna, e um
   alvo/atributos com a media do dominio no mes removida (puramente espacial).
B) Os portoes de decisao propostos (28/fev, 31/mar, 30/abr) caem na janela nublada. Qual a chance de haver
   pelo menos uma vista optica limpa do talhao nos 16 e 30 dias antes de cada portao?
C) Relacao ainda nao explorada: a AREA DE AGUA dos acudes medida a 30 m (bit de agua do QA Landsat, 1984-2026)
   como memoria hidrica local. Ela acompanha o GRACE (300 km) e a chuva acumulada de 12-48 meses?
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import GroupKFold

from comum import DADOS

warnings.filterwarnings("ignore")
BASE = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"

# ---------------------------------------------------------------- A) deriva da LST no downscaling
print("=" * 100)
print("A) Downscaling aprendido x deriva da LST diurna do Terra")
P = pd.read_parquet(BASE + "sr_fundacao_painel_celula_mes.parquet")
y = P.a_sm0_10.values
gkf = GroupKFold(n_splits=9)
g_rec = P.ano.values >= 2022


def cv(cols, dfX, yy):
    pred = np.zeros_like(yy)
    for tr, te in gkf.split(dfX, yy, groups=P.ano):
        m = LinearRegression().fit(dfX.iloc[tr][cols], yy[tr])
        pred[te] = m.predict(dfX.iloc[te][cols])
    return pred


var = {
    "4 anomalias (LST dia, NDVI, LST noite, amplitude) [original]": ["a_lst_dia", "a_ndvi", "a_lst_noite", "a_amp_termica"],
    "sem LST diurna (NDVI + LST noite)": ["a_ndvi", "a_lst_noite"],
    "so NDVI": ["a_ndvi"],
}
for nome, cols in var.items():
    pr = cv(cols, P, y)
    print(f"  {nome:62s} R2 total {r2_score(y, pr):.3f} | anos 2000-2021 {r2_score(y[~g_rec], pr[~g_rec]):.3f} | "
          f"2022-2026 {r2_score(y[g_rec], pr[g_rec]):.3f} | vies 2022-26 {np.mean(pr[g_rec] - y[g_rec]):+.4f}")

# versao puramente espacial: remove a media do dominio no mes (de atributos e alvo)
Q = P.copy()
for c in ["a_lst_dia", "a_ndvi", "a_lst_noite", "a_amp_termica", "a_sm0_10"]:
    Q["s_" + c] = Q[c] - Q.groupby("data")[c].transform("mean")
ys = Q.s_a_sm0_10.values
print("  -- habilidade ESPACIAL dentro do mes (media do dominio removida; e o que o downscaling precisa) --")
for nome, cols in var.items():
    cs = ["s_" + c for c in cols]
    pr = cv(cs, Q, ys)
    # rho espacial mediano por mes
    rr = [spearmanr(pr[ix], ys[ix])[0] for _, ix in Q.groupby("data").indices.items() if len(ix) > 30]
    print(f"  {nome:62s} R2 {r2_score(ys, pr):.3f} | 2000-21 {r2_score(ys[~g_rec], pr[~g_rec]):.3f} | "
          f"2022-26 {r2_score(ys[g_rec], pr[g_rec]):.3f} | rho espacial mediano/mes {np.median(rr):+.2f}")

# ---------------------------------------------------------------- B) visibilidade nos portoes
print("=" * 100)
print("B) Chance de pelo menos uma vista optica limpa antes de cada portao (2020-2025, 4 AOIs)")
hls = pd.read_parquet(DADOS / "sentinel2/hls_aoi_cenas.parquet")
s2 = pd.read_parquet(DADOS / "sentinel2/s2_aoi_cenas.parquet")
ls = pd.read_parquet(DADOS / "landsat/landsat_aoi_cenas_l89.parquet")
for d in (hls, s2, ls):
    d["datetime"] = pd.to_datetime(d["datetime"], utc=True).dt.tz_localize(None)
    d["frac_valida"] = d["frac_valida"].fillna(0).clip(0, 1)
uni = pd.concat([s2[["aoi", "datetime", "frac_valida"]], ls[["aoi", "datetime", "frac_valida"]]])
uni["dia"] = uni.datetime.dt.normalize()
uni = uni.sort_values("frac_valida").drop_duplicates(["aoi", "dia"], keep="last")
fontes = {"Landsat 8/9": ls, "Sentinel-2": s2, "HLS": hls, "S2+Landsat (uniao)": uni}
ANOS = range(2020, 2026)
portoes = {"28/fev": (2, 28), "31/mar": (3, 31), "30/abr": (4, 30), "31/ago (seca, controle)": (8, 31)}
linhas = []
for nome, d in fontes.items():
    for pn, (m, dd) in portoes.items():
        for W in (16, 30):
            pind, pemp = [], []
            for aoi, g in d.groupby("aoi"):
                for ano in ANOS:
                    fim = pd.Timestamp(ano, m, dd)
                    w = g[(g.datetime > fim - pd.Timedelta(days=W)) & (g.datetime <= fim)]
                    pind.append(1 - np.prod(1 - w.frac_valida.values))
                    pemp.append(float((w.frac_valida >= 0.6).any()))
            linhas.append({"fonte": nome, "portao": pn, "janela_d": W, "P_vista_indep": np.mean(pind),
                           "frac_anos_com_cena_util": np.mean(pemp)})
V = pd.DataFrame(linhas)
print(V.pivot_table(index=["fonte", "janela_d"], columns="portao", values="frac_anos_com_cena_util").round(2).to_string())
print("  (acima: fracao de AOI-anos com >= 1 cena com >= 60% da AOI limpa na janela antes do portao)")
print(V.pivot_table(index=["fonte", "janela_d"], columns="portao", values="P_vista_indep").round(2).to_string())
print("  (acima: P de um pixel ter >= 1 vista limpa, supondo nuvem independente entre cenas - otimista)")

# ---------------------------------------------------------------- C) area de acude a 30 m como memoria hidrica
print("=" * 100)
print("C) Area de agua (QA Landsat bit 7) por AOI, estacao seca ago-dez, 1984-2026")
lh = pd.read_parquet(DADOS / "landsat/landsat_aoi_cenas_hist.parquet")
L = pd.concat([lh, ls.drop(columns=["erro"], errors="ignore")], ignore_index=True)
L["datetime"] = pd.to_datetime(L["datetime"], utc=True).dt.tz_localize(None)
L = L[(L.frac_valida >= 0.5) & L.frac_agua.notna()]
L["agua_rel"] = L.frac_agua / L.frac_valida  # fracao de agua entre os pixels limpos
L = L[L.datetime.dt.month.isin([8, 9, 10, 11, 12])]
L["ano"] = L.datetime.dt.year
A = L.groupby(["aoi", "ano"]).agg(agua=("agua_rel", "median"), n=("agua_rel", "size")).reset_index()
A = A[A.n >= 2]
print("  cenas por AOI-ano (mediana):", A.n.median(), "| AOI-anos:", len(A))
print(A.groupby("aoi").agua.describe()[["count", "mean", "min", "max"]].mul([1, 100, 100, 100]).round(2).to_string())
print("  (mean/min/max em % da AOI)")

pw = pd.read_parquet(DADOS / "derivados/power_aoi_mensal.parquet")
pw = pw[pw.variavel == "PRECTOTCORR"].copy()
pw["mm"] = pw.valor * pw.data.dt.days_in_month
gr = pd.read_parquet(DADOS / "derivados/grace_aoi_mensal.parquet")
res = []
for aoi in A.aoi.unique():
    a = A[A.aoi == aoi].set_index("ano").agua
    p = pw[pw.aoi == aoi].set_index("data").mm.sort_index()
    g = gr[gr.aoi == aoi].set_index("data").valor.sort_index()
    linha = {"aoi": aoi, "n_anos": len(a)}
    for k in (6, 12, 24, 36, 48):
        acc = p.rolling(k, min_periods=k).sum()
        x = pd.Series({ano: acc.get(pd.Timestamp(ano, 7, 1)) for ano in a.index}).dropna()  # chuva ate jul do ano
        z = a.loc[x.index]
        linha[f"rho_chuva{k}m"] = spearmanr(z, x)[0]
    # chuva da quadra fev-mai do proprio ano
    q = pd.Series({ano: p[(p.index.year == ano) & p.index.month.isin([2, 3, 4, 5])].sum() for ano in a.index})
    linha["rho_quadra_mesmo_ano"] = spearmanr(a, q.loc[a.index])[0]
    gg = pd.Series({ano: g[(g.index.year == ano) & g.index.month.isin([8, 9, 10, 11, 12])].mean() for ano in a.index}).dropna()
    if len(gg) >= 8:
        linha["rho_grace_agodez"] = spearmanr(a.loc[gg.index], gg)[0]
        linha["p_grace"] = spearmanr(a.loc[gg.index], gg)[1]
        linha["n_grace"] = len(gg)
    res.append(linha)
R = pd.DataFrame(res).set_index("aoi")
print(R.round(2).to_string())

# serie do sertao central para a narrativa (secas de 1993, 1998, 2012-17)
sc = A[A.aoi == "sertao_central"].set_index("ano").agua.mul(100).round(2)
print("  Sertao Central, % de agua na AOI (ago-dez):")
print("  ", sc.to_dict())

# relacao com o 'verde na seca' (irrigacao/perene) da rodada 1
ir = pd.read_csv(BASE + "sr_fundacao_irrigacao_anual.csv")
m = ir.merge(A, on=["aoi", "ano"])
for aoi, g in m.groupby("aoi"):
    if len(g) >= 8:
        r, pv = spearmanr(g.agua, g.pct_irrig_ativa)
        print(f"  {aoi:16s} agua x pct_irrig_ativa (2013-26): rho {r:+.2f} (p {pv:.3f}, n {len(g)})")
