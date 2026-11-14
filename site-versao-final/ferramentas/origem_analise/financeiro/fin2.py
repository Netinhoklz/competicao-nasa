"""Sensibilidade ao preço da raiz, faixa alargada (janela recente) e caixa mês a mês de Quixadá (plano do motor)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.argv = [str(Path(__file__))]
exec(open(Path(__file__).parent / "fin.py", encoding="utf8").read().split("# ---------------- autocorrelação")[0])
REG = REFM.mesorregiao.to_dict()
M["R_rel"] = M.R / M.groupby(["produto", "cod_mun"]).R.transform("median")
q = M[M.cod_mun == Q]
Mm = M[M.produto.isin(["Milho", "Feijão", "Mandioca"])].copy()
meso_rel = Mm[Mm.cod_mun.map(REG) == REG[Q]].groupby(["produto", "ano"]).R_rel.median()
anos = list(range(1998, 2026))
base = {p: q[q.produto == p].R.median() for p in ["Milho", "Feijão", "Mandioca"]}
rel = pd.DataFrame({p: [q[(q.produto == p) & (q.ano == a)].R_rel.iloc[0] if ((q.produto == p) & (q.ano == a)).any() else meso_rel.get((p, a))
                        for a in anos] for p in base}, index=anos)
ce = B[(B.uf == "23") & (B.produto == "Mandioca") & B.ano.between(2016, 2025)].preco
pq = q[q.produto == "Mandioca"].preco_ref.iloc[0]
precos = {"Quixadá": pq, "mediana CE": ce.median(), "P25 CE": ce.quantile(.25)}
print("preço da raiz (R$/kg):", {k: round(v, 2) for k, v in precos.items()})
AF, AB = 2 / 3, 1.0
KS = {"Milho": CU["Milho"]["semente"], "Feijão": CU["Feijão"]["semente"], "Mandioca": 0.0, "Sorgo": CU["Sorgo"]["semente"]}
rng = np.random.default_rng(1)
N = 20000
y = np.stack([rng.choice(EN, N), rng.choice(anos, N), rng.choice(anos, N)], 1)
R = {p: base[p] * rel[p].reindex(y.ravel()).to_numpy().reshape(N, 3) for p in base}
k_pl = np.array([(KS["Mandioca"] + KS["Feijão"] + KS["Sorgo"]) * AF, (KS["Sorgo"] + KS["Mandioca"]) * AF, (KS["Feijão"] + KS["Mandioca"]) * AF])
k_bx = (KS["Milho"] + KS["Feijão"]) / 2 * AB
for nome, p in precos.items():
    m = R["Mandioca"] * p / pq
    rec_pl = np.stack([R["Feijão"][:, 0] * AF, m[:, 1] * AF, (R["Feijão"][:, 2] + m[:, 2]) * AF], 1) + (R["Milho"] + R["Feijão"]) / 2 * AB
    rec_s0 = (R["Milho"] + R["Feijão"]) / 2 * 3
    mp = (rec_pl - k_pl - k_bx).sum(1)
    ms = (rec_s0 - ((KS["Milho"] + KS["Feijão"]) / 2 * 3)).sum(1)
    print(f"raiz {nome} R$ {p:.2f}: plano 3 anos P10/P50/P90 {np.percentile(mp, [10, 50, 90]).round(-1)} | S0 {np.percentile(ms, [10, 50, 90]).round(-1)} | "
          f"P(plano>S0) {np.mean(mp > ms):.2f} | ganho P10/P50/P90 {np.percentile(mp - ms, [10, 50, 90]).round(-1)}")

# 2027 condicionado x não condicionado (o teste fora da amostra mostrou que 4 El Niños não bastam)
for nome, pool in [("2027 ~ El Niño forte", EN), ("2027 ~ qualquer ano", anos)]:
    yy = rng.choice(pool, N)
    f = base["Feijão"] * rel["Feijão"].reindex(yy).to_numpy()
    mi = base["Milho"] * rel["Milho"].reindex(yy).to_numpy()
    pl = f * AF + (mi + f) / 2 * AB - k_pl[0] - k_bx
    s0 = (mi + f) / 2 * 3 - (KS["Milho"] + KS["Feijão"]) / 2 * 3
    print(f"{nome}: margem semente 2027 plano P10/P50/P90 {np.percentile(pl, [10, 50, 90]).round(-1)}; S0 {np.percentile(s0, [10, 50, 90]).round(-1)}")

# faixa alargada: quantis da janela recente 2011–2025 x 1998–2025
for p in base:
    s = q[q.produto == p].set_index("ano").R
    print(p, "P10/P50/P90 1998–2025:", s.quantile([.1, .5, .9]).round(-1).tolist(), "| 2011–2025:", s[s.index >= 2011].quantile([.1, .5, .9]).round(-1).tolist(),
          "| últimos 5 anos:", s[s.index >= 2021].round(-1).tolist())

# caixa mês a mês (cenário mediano: 2027 = mediana dos EN; 2028–29 = mediana de todos os anos), preço de Quixadá, custo = semente
med = {p: base[p] * rel[p].reindex(EN).median() for p in base}
nor = {p: base[p] for p in base}
mov = []  # (ano, mês, R$, rótulo)
for ano, r in [(2027, med), (2028, nor), (2029, nor)]:
    mov += [(ano, 2, -KS["Milho"] / 2 * AB, "semente do milho (baixio)"), (ano, 4, -KS["Feijão"] / 2 * AB, "semente do caupi (baixio)"),
            (ano, 6, r["Milho"] / 2 * AB, "colheita do milho (baixio)"), (ano, 7, r["Feijão"] / 2 * AB, "colheita do caupi (baixio)")]
    if ano in (2027, 2029):
        mov += [(ano, 3, -KS["Feijão"] * AF, "semente do caupi (parte " + ("B" if ano == 2027 else "A") + ")"),
                (ano, 6, r["Feijão"] * AF, "colheita do caupi")]
    if ano in (2027, 2028):
        mov += [(ano, 3, -KS["Sorgo"] * AF, "semente do sorgo forrageiro")]
    if ano in (2028, 2029):
        mov += [(ano, mm, r["Mandioca"] * AF / 8, "mandioca colhida aos poucos") for mm in range(2, 10)]
cx = pd.DataFrame(mov, columns=["ano", "mes", "rs", "o_que"])
tab = cx.groupby(["ano", "mes"]).rs.sum().reset_index()
tab["acumulado"] = tab.rs.cumsum()
print("\nCAIXA MÊS A MÊS, Quixadá, cenário mediano, custo = semente (R$ 2025, 3 ha):\n", tab.round(0).to_string())
