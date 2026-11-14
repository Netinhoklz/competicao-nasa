"""Estrategista - Analise 4: a "profecia de Sao Jose" testada com 28 anos de IMERG em 184 municipios.

Crenca sertaneja: "se chover ate o dia de Sao Jose (19/mar), o inverno e bom". Pergunta: a chuva no dia 19/mar
(ou a chuva acumulada ate 19/mar) separa os anos de quebra de milho? Quanto ela vale frente ao modelo de satelite?

Dados: estrategista_cache_chuva_mun_diaria.parquet (gerado por estrategista_alerta_municipal.py a partir de
E:/campeonato-nasa/dados/imerg/imerg_ce_diario_*.nc) e derivados/ibge_pam_mun_anual.parquet.
Unidade independente = ano (os municipios de um mesmo ano sao correlacionados): reporto tambem no nivel estadual.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score
from comum import DERIV

AQUI = Path(__file__).parent
chuva = pd.read_parquet(AQUI / "estrategista_cache_chuva_mun_diaria.parquet")
anos = range(1998, 2026)
lin = []
for a in anos:
    dia = chuva.loc[f"{a}-03-19"]
    jan_ate = chuva.loc[f"{a}-01-01":f"{a}-03-19"].sum()
    janela = chuva.loc[f"{a}-03-18":f"{a}-03-20"].max()
    depois = chuva.loc[f"{a}-03-20":f"{a}-05-31"].sum()
    for cod in chuva.columns:
        lin.append({"ano": a, "cod": cod, "chuva_19mar": dia[cod], "max_18a20mar": janela[cod], "acum_ate_19mar": jan_ate[cod],
                    "chuva_20mar_31mai": depois[cod]})
S = pd.DataFrame(lin)
S["choveu_SJ"] = (S.chuva_19mar >= 1.0).astype(int)
S["acum_razao"] = S.acum_ate_19mar / S.groupby("cod").acum_ate_19mar.transform("median").clip(lower=1)

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[(pam.ano >= 1998) & (pam.ano <= 2025)]
q = pam[pam.produto.str.startswith("Milho (em") & (pam.area_colhida_ha >= 100) & (pam.rendimento_kg_ha > 0)][["cod_local", "ano", "rendimento_kg_ha"]].copy()
q["milho"] = q.rendimento_kg_ha / q.groupby("cod_local").rendimento_kg_ha.transform("median")
q["cod"] = q.cod_local.astype(str)
D = S.merge(q[["cod", "ano", "milho"]], on=["cod", "ano"]).dropna()
D["quebra"] = (D.milho < 0.5).astype(int)
print(f"municipio-ano: {len(D)}; choveu no dia 19/mar (>=1 mm) em {D.choveu_SJ.mean():.0%}")

t = D.groupby("choveu_SJ").agg(n=("quebra", "size"), p_quebra=("quebra", "mean"), milho_mediana=("milho", "median"),
                               chuva_depois_mediana=("chuva_20mar_31mai", "median"))
print("\nPor municipio-ano:")
print(t.round(3).to_string())
print(f"AUC (sinal binario 'choveu no dia', menor risco se choveu): {roc_auc_score(D.quebra, -D.choveu_SJ):.3f}")
print(f"AUC (chuva acumulada 1/jan-19/mar, razao da mediana): {roc_auc_score(D.quebra, -D.acum_razao):.3f}")
print(f"Spearman chuva no dia 19/mar x chuva 20/mar-31/mai: {stats.spearmanr(D.chuva_19mar, D.chuva_20mar_31mai)[0]:+.2f}")
print(f"Spearman acumulado ate 19/mar x chuva 20/mar-31/mai: {stats.spearmanr(D.acum_ate_19mar, D.chuva_20mar_31mai)[0]:+.2f}")

# nivel estadual por ano (unidade independente)
E = D.groupby("ano").agg(frac_mun_choveu_SJ=("choveu_SJ", "mean"), acum_razao=("acum_razao", "median"),
                         frac_quebra=("quebra", "mean"), milho_mediana=("milho", "median"))
r1 = stats.spearmanr(E.frac_mun_choveu_SJ, E.frac_quebra)
r2 = stats.spearmanr(E.acum_razao, E.frac_quebra)
print(f"\nNivel estadual (n={len(E)} anos): Spearman(fracao de municipios com chuva em 19/mar, fracao com quebra) = {r1[0]:+.2f} (p={r1[1]:.3f})")
print(f"Nivel estadual: Spearman(chuva acumulada ate 19/mar, fracao com quebra) = {r2[0]:+.2f} (p={r2[1]:.3f})")
E["SJ_bom"] = E.frac_mun_choveu_SJ >= 0.5
print("Anos com chuva em 19/mar na maioria dos municipios:", list(E.index[E.SJ_bom]))
print(E.groupby("SJ_bom").agg(anos=("frac_quebra", "size"), frac_quebra_media=("frac_quebra", "mean"), milho_mediana=("milho_mediana", "median")).round(2).to_string())
print("\nAnos-caso:")
print(E.loc[[1998, 2012, 2016, 2024]].round(2).to_string())
