import sys, warnings
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *
from comum import DERIV
import pandas as pd
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 40)
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
S = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas"
I = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
print(I.variavel.unique())
P = I.pivot_table(index="data", columns="variavel", values="valor")
print(P.loc["2026-01-01":].round(2))
G = pd.read_parquet(DERIV / "grace_ce_mensal.parquet")
print(G.variavel.unique(), G.data.max())
g = G.pivot_table(index="data", columns="variavel", values="valor")
print(g.tail(8).round(2))
c = pd.read_parquet(S + "/clima_risco_composto_anual.parquet"); print(c.columns.tolist()); print(c.tail(3))
for f in ["agronomo_isna_mun_ano.parquet", "chuva_mun_diaria.parquet", "painel_mun_ce.parquet"]:
    d = pd.read_parquet(S + "/" + f); print(f, d.shape); print(d.head(3))
