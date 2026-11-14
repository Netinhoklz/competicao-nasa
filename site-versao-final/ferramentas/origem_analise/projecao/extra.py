import numpy as np, pandas as pd
OUT = "C:/Users/NETINH~1/AppData/Local/Temp/claude/88b277d27b184113/73cd62bd-b6e9-4872-9e4a-a06e5ca404a0/scratchpad/analise10/projecao/"
B = pd.read_parquet(OUT + "bt_metricas_linhas.parquet")
QC = ["q10", "q20", "q30", "q50", "q70", "q80", "q90"]; QS = np.array([.1, .2, .3, .5, .7, .8, .9])
EN = [1998, 2016, 2024]
# 1) fator conforme (escala relativa à mediana) para C e D, com todos os anos WF e LOYO
for modo in ["WF", "LOYO"]:
    for m in ["C_hier", "D_enso"]:
        s = B[(B.modo == modo) & (B.metodo == m)]
        sc = np.maximum((s.q10 - s.y) / s.med, (s.y - s.q90) / s.med)
        sl = (s.q20 - s.y) / s.med  # só o piso (um lado)
        print(modo, m, "Qhat80 bilateral", round(float(np.quantile(sc, 0.8)), 3), "| Qhat piso80 (um lado)", round(float(np.quantile(sl, 0.8)), 3))
# 2) mistura 50/50 de C e D (CDFs interpoladas) e D com o piso alargado pelo fator do LOYO dos outros anos — LOYO, por grupo
grid = np.linspace(0, 5, 501)
def cdf(s):
    Q = s[QC].values / s.med.values[:, None]
    Q = np.maximum.accumulate(Q, axis=1)
    out = np.empty((len(s), len(grid)))
    for i in range(len(s)):
        out[i] = np.interp(grid, Q[i], QS, left=0.05, right=0.95)
    return out
for modo in ["LOYO", "WF"]:
    sC = B[(B.modo == modo) & (B.metodo == "C_hier")].sort_values(["cultura", "cod_mun", "ano"]).reset_index(drop=True)
    sD = B[(B.modo == modo) & (B.metodo == "D_enso")].sort_values(["cultura", "cod_mun", "ano"]).reset_index(drop=True)
    sC = sC[sC.ano.isin(EN)]; sD = sD.loc[sC.index]
    F = 0.5 * cdf(sC) + 0.5 * cdf(sD)
    inv = lambda p: grid[np.argmax(F >= p, axis=1)]
    r = (sC.y / sC.med).values
    q10, q20, q90 = inv(0.1), inv(0.2), inv(0.9)
    pq = 0.5 * sC.pq.values + 0.5 * sD.pq.values
    print(f"\n{modo} anos EN ASO>=1, mistura 50/50 C+D: cov80={np.mean((r>=q10)&(r<=q90)):.3f} piso80={np.mean(r>=q20):.3f} "
          f"piso90={np.mean(r>=q10):.3f} brier={np.mean((pq-(r<0.5))**2):.3f} p_prev={pq.mean():.3f} f_obs={np.mean(r<0.5):.3f}")
    for a in EN:
        k = (sC.ano == a).values
        print(f"  {a}: cov80={np.mean((r[k]>=q10[k])&(r[k]<=q90[k])):.2f} piso80={np.mean(r[k]>=q20[k]):.2f} p_prev={pq[k].mean():.2f} f_obs={np.mean(r[k]<0.5):.2f}")
    for nome, s in [("C", sC), ("D", sD)]:
        rr = (s.y / s.med).values
        for a in EN:
            k = (s.ano == a).values
            print(f"  {nome} {a}: piso80={np.mean(rr[k] >= (s.q20.values/s.med.values)[k]):.2f} p_prev={s.pq.values[k].mean():.2f}")
# 3) Quixadá e Barreiras nos anos análogos
P = pd.read_parquet("E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet")
for c in ["2311306", "2903201", "2700300"]:
    x = P[(P.cod_mun == c) & P.produto.isin(["Milho", "Feijão", "Mandioca"])]
    t = x.pivot(index="ano", columns="produto", values="rend_plantado_kg_ha")
    print(c, "mediana", t.median().round().to_dict())
    print(t.loc[[1998, 1999, 2010, 2012, 2016, 2017, 2024, 2025]].round().to_string())
