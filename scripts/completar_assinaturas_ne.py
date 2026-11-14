"""Completa as assinaturas climáticas do NE que falharam (limite de pedidos 429 do POWER), uma célula por vez, com pausa.

Uso: python -I completar_assinaturas_ne.py   (atualiza analogos_aprofundado/ne_mun_assinaturas.csv e ceara_mun_assinaturas.csv)
"""
import sys
import time

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import pandas as pd  # noqa: E402

import analogos_climaticos_artigos as AC  # noqa: E402
from comum import DADOS  # noqa: E402

OUT_A = DADOS / "analogos_aprofundado"
A = pd.read_csv(OUT_A / "ne_mun_assinaturas.csv", dtype={"cod": str})
chave = lambda la, lo: (round(la * 2) / 2, round(lo / 0.625) * 0.625)  # noqa: E731
faltam = A[A.chuva_anual_mm.isna()]
celulas = {chave(r.lat, r.lon): (r.lat, r.lon) for r in faltam.itertuples()}
print(f"{len(faltam)} municípios sem assinatura em {len(celulas)} células", flush=True)
feitas = {}
for k, (la, lo) in celulas.items():
    for tentativa in range(6):
        try:
            time.sleep(2)
            feitas[k] = AC.assinatura(la, lo)
            break
        except Exception as e:
            print("  espera", k, type(e).__name__, flush=True)
            time.sleep(20 * (tentativa + 1))
for i, r in faltam.iterrows():
    v = feitas.get(chave(r.lat, r.lon))
    if v:
        for c, x in v.items():
            A.loc[i, c] = x
A.to_csv(OUT_A / "ne_mun_assinaturas.csv", index=False)
A[A.uf == "CE"].drop(columns="uf").to_csv(OUT_A / "ceara_mun_assinaturas.csv", index=False)
print("sem assinatura agora:", int(A.chuva_anual_mm.isna().sum()), flush=True)
