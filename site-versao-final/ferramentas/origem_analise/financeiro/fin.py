"""Confere o painel financeiro: cobertura por município/cultura, números de Quixadá, replay histórico do plano x S0,
autocorrelação/tendência (para escolher o método de projeção) e teste fora da amostra da faixa P10–P90."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(sys.argv[0]).parent
DADOS = Path("E:/campeonato-nasa/dados")
DERIV = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados")
if not (DERIV / "ibge_ne_municipios_referencia.parquet").exists():
    DERIV = DADOS / "derivados"
F = DADOS / "financeiro"
CULT = ["Milho", "Feijão", "Mandioca", "Sorgo", "Amendoim", "Algodão herbáceo", "Mamona", "Girassol"]
Q = "2311306"
EVT = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
EN = sorted(int(a) for a in EVT[(EVT.ONI_OND_NDJ >= 1.5) & EVT.quadra_afetada.between(1998, 2025)].quadra_afetada)
SECA = list(range(2012, 2017))
REFM = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
print("EN forte:", EN, "| municípios ref:", len(REFM))

P = pd.read_parquet(F / "painel_mun_cultura_ano.parquet")
P = P[P.produto.isin(CULT)].copy()
P["uf"] = P.cod_mun.str[:2]
print("anos no painel:", P.ano.min(), P.ano.max(), "| linhas:", len(P))
print("linhas por ano (últimos):", P.groupby("ano").size().tail(4).to_dict())
B = P[P.area_plantada_ha >= 10].copy()


def med_outros(s):
    v = s.to_numpy()
    if len(v) < 2:
        return pd.Series(np.nan, index=s.index)
    return pd.Series([np.median(np.delete(v, i)) for i in range(len(v))], index=s.index)


B["normal"] = B.groupby(["cod_mun", "produto"]).rend_plantado_kg_ha.transform(med_outros)
B["quebra"] = B.rend_plantado_kg_ha / B.normal < 0.5
B["n_anos"] = B.groupby(["cod_mun", "produto"]).ano.transform("size")
pr = B.preco_r2025_kg.where(B.producao_t >= 1)
B["preco"] = pr.where((pr / pr.groupby([B.uf, B.produto, B.ano]).transform("median")).between(0.25, 4))
jan = B[B.ano.between(2016, 2025)]
pm = jan.groupby(["cod_mun", "produto"]).preco.agg(["median", "count"])
pm = pm[pm["count"] >= 3]["median"]
pu = jan.groupby(["uf", "produto"]).preco.median()
pn = jan.groupby("produto").preco.median()
B["preco_ref"] = pm.reindex(pd.MultiIndex.from_frame(B[["cod_mun", "produto"]])).to_numpy()
B["origem_preco"] = np.where(B.preco_ref.notna(), "município", None)
fu = pu.reindex(pd.MultiIndex.from_frame(B[["uf", "produto"]])).to_numpy()
B["origem_preco"] = np.where(B.preco_ref.isna() & ~np.isnan(fu), "UF", B.origem_preco)
B["preco_ref"] = B.preco_ref.fillna(pd.Series(fu, index=B.index))
B["origem_preco"] = np.where(B.preco_ref.isna(), "NE", B.origem_preco)
B["preco_ref"] = B.preco_ref.fillna(B.produto.map(pn))
B["R"] = B.rend_plantado_kg_ha * B.preco_ref
M = B[B.n_anos >= 10].copy()

# ---------------- cobertura
NMUN = REFM.index.str[:2].isin(["21", "22", "23", "24", "25", "26", "27", "28", "29"]).sum()
cob = pd.DataFrame({
    "mun_algum_ano": B.groupby("produto").cod_mun.nunique(),
    "mun_serie_10": M.groupby("produto").cod_mun.nunique(),
    "mun_serie_com_2021_25": M[M.ano >= 2021].groupby("produto").cod_mun.nunique(),
    "anos_medianos_na_serie": M.groupby(["produto", "cod_mun"]).size().groupby("produto").median(),
    "ultimo_ano_mediano": M.groupby(["produto", "cod_mun"]).ano.max().groupby("produto").median(),
}).reindex(CULT)
cob["%_dos_mun_NE"] = cob.mun_serie_10 / 1794 * 100
print("\nCOBERTURA (série = ≥10 anos com ≥10 ha plantados, 1998–2025); NE = 1794 municípios")
print(cob.round(1).to_string())
s = M.groupby("cod_mun").produto.apply(set)
tres = s.apply(lambda x: {"Milho", "Feijão", "Mandioca"} <= x).sum()
dois = s.apply(lambda x: {"Milho", "Feijão"} <= x).sum()
print(f"mun com milho+feijão: {dois}; com milho+feijão+mandioca: {tres}; com alguma série: {len(s)}; sem nenhuma: {1794 - len(s)}")

# ---------------- custo CONAB (mesma regra da seção 5)
C = pd.read_csv(F / "conab_custos_ne.csv", parse_dates=["mes_precos"])
C["lugar"] = C.folha.str.rsplit("-", n=1).str[0]
C["produto"] = C.cultura_arquivo.map({"Feijão 1ª safra": "Feijão", "Mandioca": "Mandioca", "Mamona": "Mamona", "Milho 1ª safra": "Milho"})
cr = (C.cultura_arquivo == "Milho 2ª safra") & C.lugar.str.startswith("Crateús")
C.loc[cr, "produto"] = "Milho"
U = C[C.produto.notna() & ~C.irrigado & (C.familiar | cr)].sort_values("ano_folha").groupby(["produto", "lugar"]).tail(5)
loc = U.groupby(["produto", "lugar"]).agg(ate=("ano_folha", "max"), semente=("sementes_r_ha_r2025", "median"),
                                          desembolso=("desembolso_r_ha_r2025", "median"), op=("custo_operacional_r_ha_r2025", "median")).reset_index()
CU = {}
for p, g in loc.groupby("produto"):
    r = g[g.ate >= 2019]
    b = r if len(r) else g
    CU[p] = {"semente": b.semente.median(), "desembolso": b.desembolso.median(), "op": b.op.median(),
             "des_min": g.desembolso.min(), "des_max": g.desembolso.max(), "locais": len(g)}
c0 = loc[(loc.produto == "Milho") & loc.lugar.str.startswith("Crateús")].iloc[0]
CU["Milho"].update(semente=c0.semente, desembolso=c0.desembolso, op=c0.op)
an = loc[loc.produto.isin(["Feijão", "Mamona"]) | loc.lugar.str.startswith("Crateús")]
r = an[an.ate >= 2019]
CU["Sorgo"] = {"semente": r.semente.median(), "desembolso": r.desembolso.median(), "op": r.op.median(),
               "des_min": an.desembolso.min(), "des_max": an.desembolso.max(), "locais": 0}
print("\nCUSTO (R$ 2025/ha):", json.dumps({k: {a: round(float(b)) for a, b in v.items()} for k, v in CU.items()}, ensure_ascii=False))

# ---------------- autocorrelação e tendência (escolha do método de projeção)
M["R_rel"] = M.R / M.groupby(["produto", "cod_mun"]).R.transform("median")
ac, tr = [], []
for (p, c), g in M[M.produto.isin(["Milho", "Feijão", "Mandioca"])].groupby(["produto", "cod_mun"]):
    g = g.set_index("ano").R_rel.reindex(range(1998, 2026))
    if g.notna().sum() >= 15:
        ac.append((p, g.autocorr(1)))
        x = g.dropna()
        tr.append((p, pd.Series(x.index).corr(pd.Series(x.values), method="spearman")))
ac = pd.DataFrame(ac, columns=["p", "ac1"]).groupby("p").ac1.describe(percentiles=[.1, .5, .9])
tr = pd.DataFrame(tr, columns=["p", "rho"]).groupby("p").rho.describe(percentiles=[.1, .5, .9])
print("\nAUTOCORRELAÇÃO lag-1 da razão ao normal (por município):\n", ac.round(2).to_string())
print("TENDÊNCIA (Spearman ano × razão):\n", tr.round(2).to_string())

# ---------------- teste fora da amostra: faixa P10–P90 de 1998–2015 cobre quanto de 2016–2025?
rows = []
for (p, c), g in M[M.produto.isin(["Milho", "Feijão", "Mandioca"])].groupby(["produto", "cod_mun"]):
    tr_ = g[g.ano <= 2015].R
    te = g[g.ano >= 2016]
    if len(tr_) >= 8 and len(te) >= 5:
        lo, hi, md = tr_.quantile(.1), tr_.quantile(.9), tr_.median()
        rows.append((p, ((te.R >= lo) & (te.R <= hi)).mean(), (te.R < lo).mean(), (te.R > hi).mean(), te.R.median() / md))
oos = pd.DataFrame(rows, columns=["p", "dentro", "abaixo", "acima", "mediana_teste/treino"]).groupby("p").mean()
print("\nFORA DA AMOSTRA (faixa P10–P90 de 1998–2015 contra 2016–2025, média dos municípios; alvo 0,80):\n", oos.round(3).to_string())
# condicionado: o El Niño forte de 2016 e 2024, previsto pela mediana dos EN de 1998/2010
rows = []
for (p, c), g in M[M.produto.isin(["Milho", "Feijão", "Mandioca"])].groupby(["produto", "cod_mun"]):
    g = g.set_index("ano").R_rel
    base = g.reindex([1998, 2010]).dropna()
    for a in [2016, 2024]:
        if a in g.index and len(base):
            rows.append((p, a, g[a], base.median(), g.drop([1998, 2010, 2016, 2024], errors="ignore").median()))
en = pd.DataFrame(rows, columns=["p", "ano", "obs", "prev_EN", "prev_clima"])
en["erro_EN"] = (en.obs - en.prev_EN).abs()
en["erro_clima"] = (en.obs - en.prev_clima).abs()
print("ERRO ABSOLUTO MEDIANO da razão ao normal em 2016 e 2024: prevendo com os EN de 1998/2010 x com a climatologia\n",
      en.groupby(["p", "ano"])[["obs", "erro_EN", "erro_clima"]].median().round(2).to_string())

# ---------------- Quixadá: números por cultura
REG = REFM.mesorregiao.to_dict()
q = M[M.cod_mun == Q]
print("\nQUIXADÁ: anos por cultura:", q.groupby("produto").ano.agg(["size", "min", "max"]).to_dict("index"))
qm = q[q.produto == "Mandioca"][["ano", "area_plantada_ha", "rend_plantado_kg_ha", "preco_ref", "R"]]
print("mandioca Quixadá (últimos):\n", qm.tail(8).round(2).to_string())
card = {}
for p in ["Milho", "Feijão", "Mandioca", "Algodão herbáceo", "Mamona"]:
    g = q[q.produto == p]
    if not len(g):
        continue
    R = g.R
    cu = CU.get(p, CU["Sorgo"])
    card[p] = {"anos": int(len(g)), "de": int(g.ano.min()), "ate": int(g.ano.max()), "preco_ref_kg": round(float(g.preco_ref.iloc[0]), 2),
               "origem_preco": g.origem_preco.iloc[0], "rend_mediano_kg_ha": round(float(g.rend_plantado_kg_ha.median())),
               "valor_p10": round(float(R.quantile(.1))), "valor_p50": round(float(R.median())), "valor_p90": round(float(R.quantile(.9))),
               "pior_ano_em_10": round(float(R.quantile(.1))),
               "valor_el_nino_forte": round(float(g[g.ano.isin(EN)].R.median())) if g.ano.isin(EN).sum() >= 2 else None,
               "anos_el_nino_forte": int(g.ano.isin(EN).sum()),
               "quebra_pct": round(float(g.quebra.mean() * 100)),
               "nao_paga_semente_pct": round(float((R < cu["semente"]).mean() * 100)),
               "nao_paga_desembolso_pct": round(float((R < cu["desembolso"]).mean() * 100)),
               "custo_semente": round(float(cu["semente"])), "custo_desembolso": round(float(cu["desembolso"]))}
print(json.dumps(card, ensure_ascii=False, indent=1))

# ---------------- replay histórico do plano x S0 em Quixadá (matriz conjunta ano a ano)
# razão ao normal do município; falta -> mediana da mesorregião no ano (mesma regra da seção 10)
Mm = M[M.produto.isin(["Milho", "Feijão", "Mandioca"])].copy()
Mm["meso"] = Mm.cod_mun.map(REG)
meso_rel = Mm[Mm.meso == REG[Q]].groupby(["produto", "ano"]).R_rel.median()
base = {p: q[q.produto == p].R.median() for p in ["Milho", "Feijão", "Mandioca"]}
anos = list(range(1998, 2026))
Rq = pd.DataFrame(index=anos, columns=["Milho", "Feijão", "Mandioca"], dtype=float)
orig = pd.DataFrame(index=anos, columns=Rq.columns, dtype=object)
for p in Rq.columns:
    own = q[q.produto == p].set_index("ano").R_rel
    for a in anos:
        if a in own.index:
            Rq.loc[a, p], orig.loc[a, p] = own[a], "mun"
        else:
            Rq.loc[a, p], orig.loc[a, p] = meso_rel.get((p, a), np.nan), "meso"
Rq = Rq.mul(pd.Series(base))
print("\nanos preenchidos pela mesorregião:", {p: int((orig[p] == "meso").sum()) for p in orig})
# conferir os números da seção 10 (mediana por grupo)
grp = pd.Series(["EN" if a in EN else ("seca" if a in range(2012, 2016) else "normal") for a in anos], index=anos)
print("mediana por grupo (R$/ha):\n", Rq.groupby(grp).median().round(0).to_string())

# plano da família (motor do protótipo, Quixadá): 3 partes de 2/3 ha + baixio 1 ha (milho + caupi em revezamento = ½ + ½)
AF, AB = 2 / 3, 1.0
KS = {p: CU[p]["semente"] for p in ["Milho", "Feijão", "Mandioca"]} | {"Sorgo": CU["Sorgo"]["semente"]}
KD = {p: CU[p]["desembolso"] for p in ["Milho", "Feijão", "Mandioca"]} | {"Sorgo": CU["Sorgo"]["desembolso"]}


def plano_ano(i, r, nivel):
    """i = 0,1,2 (2027..2029); r = receitas/ha do ano; devolve (receita, custo). Sequência do motor:
    A: maniva | mandioca colhe | caupi ; B: caupi | sorgo forr. | maniva ; C: sorgo forr. | maniva | mandioca colhe."""
    K = KS if nivel == "semente" else KD
    bx_r = (r["Milho"] + r["Feijão"]) / 2 * AB
    bx_k = (K["Milho"] + K["Feijão"]) / 2 * AB
    if i == 0:
        rec = r["Feijão"] * AF
        k = (K["Mandioca"] + K["Feijão"] + K["Sorgo"]) * AF
    elif i == 1:
        rec = r["MandiocaColhe"] * AF
        k = (K["Sorgo"] + K["Mandioca"]) * AF
    else:
        rec = (r["Feijão"] + r["MandiocaColhe"]) * AF
        k = (K["Feijão"] + K["Mandioca"]) * AF
    return rec + bx_r, k + bx_k


def s0_ano(r, nivel):
    K = KS if nivel == "semente" else KD
    return (r["Milho"] + r["Feijão"]) / 2 * 3, (K["Milho"] + K["Feijão"]) / 2 * 3


# simulação: 2027 sorteado entre os El Niños fortes (condicionado ao ONI +2,46 de hoje); 2028 e 2029 entre todos os anos.
# a mandioca colhida no ano t cresceu no ano t-1 e t: usamos a razão do ano da colheita (convenção do PAM).
rng = np.random.default_rng(0)
N = 20000
res = {n: {"plano": [], "s0": [], "anos": []} for n in ["semente", "desembolso"]}
y27 = rng.choice(EN, N)
y28 = rng.choice(anos, N)
y29 = rng.choice(anos, N)
for nivel in ["semente", "desembolso"]:
    pl = np.zeros((N, 3))
    s0 = np.zeros((N, 3))
    for j, ys in enumerate([y27, y28, y29]):
        for k, y in enumerate(ys):
            rr = Rq.loc[y].to_dict()
            rr["MandiocaColhe"] = rr["Mandioca"]
            a, b = plano_ano(j, rr, nivel)
            c, d = s0_ano(rr, nivel)
            pl[k, j] = a - b
            s0[k, j] = c - d
    res[nivel] = (pl, s0)
for nivel, (pl, s0) in res.items():
    cp, cs = pl.cumsum(1), s0.cumsum(1)
    print(f"\nSIMULAÇÃO Quixadá, margem sobre {nivel} (R$ 2025, 3 ha; 2027 ~ El Niño forte):")
    for j, ano in enumerate([2027, 2028, 2029]):
        print(f"  {ano}: plano P10/P50/P90 = {np.percentile(pl[:, j], [10, 50, 90]).round(0)} | S0 = {np.percentile(s0[:, j], [10, 50, 90]).round(0)}")
    print(f"  acumulado 2027–29: plano {np.percentile(cp[:, 2], [10, 50, 90]).round(0)} | S0 {np.percentile(cs[:, 2], [10, 50, 90]).round(0)}")
    print(f"  P(plano > S0 em 3 anos) = {(cp[:, 2] > cs[:, 2]).mean():.2f}; P(plano acumulado < 0) = {(cp[:, 2] < 0).mean():.2f}; "
          f"P(S0 acumulado < 0) = {(cs[:, 2] < 0).mean():.2f}; P(plano à frente já em 2027) = {(cp[:, 0] > cs[:, 0]).mean():.2f}; em 2028 = {(cp[:, 1] > cs[:, 1]).mean():.2f}")
    print(f"  pior ano dos 3 (mín. anual) plano P10 = {np.percentile(pl.min(1), 10):.0f}; S0 P10 = {np.percentile(s0.min(1), 10):.0f}")

# replay determinístico de cada ano histórico (mesmo ano para todos os talhões), em regime permanente:
# receita de 1 ano do plano em regime (A colhe mandioca, B caupi, C maniva + baixio) x S0
rp = pd.DataFrame({"plano_regime": Rq.Mandioca * AF + Rq.Feijão * AF + (Rq.Milho + Rq.Feijão) / 2 * AB,
                   "s0": (Rq.Milho + Rq.Feijão) / 2 * 3}).round(0)
rp["plano_menos_s0"] = rp.plano_regime - rp.s0
print("\nREPLAY ano a ano (valor da colheita, 3 ha, regime permanente):\n", rp.to_string())
print("anos em que o plano em regime fica abaixo da S0:", int((rp.plano_menos_s0 < 0).sum()), "de", len(rp))

json.dump({"cobertura": cob.round(1).reset_index().to_dict("records"), "quixada_cartoes": card, "custo": CU,
           "replay": rp.reset_index().rename(columns={"index": "ano"}).to_dict("records")},
          open(OUT / "saida.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=float)
