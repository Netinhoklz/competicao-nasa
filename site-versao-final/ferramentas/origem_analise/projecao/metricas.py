import numpy as np, pandas as pd
OUT = "C:/Users/NETINH~1/AppData/Local/Temp/claude/88b277d27b184113/73cd62bd-b6e9-4872-9e4a-a06e5ca404a0/scratchpad/analise10/projecao/"
B = pd.read_parquet(OUT + "bt_linhas.parquet")
EN = {1998, 2010, 2016, 2024}; EN_ASO = {1998, 2016, 2024}; SECA = {2012, 2013, 2014, 2015}
B["grupo"] = np.where(B.ano.isin(EN_ASO), "EN_ASO>=1 (98,16,24)", np.where(B.ano == 2010, "EN 2010 (ASO 0,66)",
                      np.where(B.ano.isin(SECA), "seca 2012-15", "demais")))
r = B.y / B.med
B["quebra"] = (r < 0.5).astype(float)
B["cov80"] = ((B.y >= B.q10) & (B.y <= B.q90)).astype(float)
B["piso80"] = (B.y >= B.q20).astype(float)
B["piso90"] = (B.y >= B.q10).astype(float)
B["larg"] = (B.q90 - B.q10) / B.med


def pin(yv, qv, a):
    d = yv - qv
    return np.maximum(a * d, (a - 1) * d)


B["pinball"] = (pin(r, B.q10 / B.med, 0.1) + pin(r, B.q50 / B.med, 0.5) + pin(r, B.q90 / B.med, 0.9)) / 3
B["ae50"] = (r - B.q50 / B.med).abs()
B["brier"] = (B.pq - B.quebra) ** 2
B["pq"] = B.pq.clip(0, 1)
agg = dict(n=("y", "size"), cov80=("cov80", "mean"), piso80=("piso80", "mean"), piso90=("piso90", "mean"), larg=("larg", "median"),
           pinball=("pinball", "mean"), mae50=("ae50", "mean"), brier=("brier", "mean"), p_prev=("pq", "mean"), f_obs=("quebra", "mean"))
pd.set_option("display.width", 250)
for modo in ["LOYO", "WF"]:
    S = B[B.modo == modo]
    print(f"\n######## {modo}: todos os anos, por cultura")
    print(S.groupby(["cultura", "metodo"]).agg(**agg).round(3).to_string())
    print(f"\n######## {modo}: por grupo de anos (3 culturas juntas)")
    print(S.groupby(["grupo", "metodo"]).agg(**agg).round(3).to_string())
    print(f"\n######## {modo}: Milho por grupo")
    print(S[S.cultura == "Milho"].groupby(["grupo", "metodo"]).agg(**agg).round(3).to_string())
    # cobertura por ano: média dos anos e pior ano
    cy = S.groupby(["metodo", "ano"]).cov80.mean().unstack(0)
    print(f"\n######## {modo}: cobertura 80% por ano (todas as culturas)")
    print(cy.round(2).to_string())
    print("média dos anos / pior ano / anos com cobertura < 60%:")
    print(pd.DataFrame({"media_anos": cy.mean(), "pior": cy.min(), "n_anos_lt60": (cy < 0.6).sum()}).round(3).to_string())
# nível do ano: fração de municípios em quebra x probabilidade média prevista (Milho, LOYO)
S = B[(B.modo == "LOYO") & (B.cultura == "Milho")]
ya = S.groupby(["ano", "metodo"]).agg(f_obs=("quebra", "mean"), p_prev=("pq", "mean")).unstack()
print("\nMilho LOYO, por ano: fração observada de municípios em quebra e P média prevista por método")
print(ya.round(2).to_string())
B.to_parquet(OUT + "bt_metricas_linhas.parquet")
