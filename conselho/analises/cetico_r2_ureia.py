"""Cetico rodada 2: razao ureia/milho (Pink Sheet) - ultimo mes e pico."""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
from comum import DERIV
import pandas as pd
m = pd.read_parquet(DERIV / "mercado_precos_mensal.parquet")
m["data"] = pd.to_datetime(m["data"])
print([c for c in m.commodity.unique() if any(k in c.lower() for k in ["urea", "maize", "dap", "tsp", "potass"])])
u = m[m.commodity.str.lower().str.startswith("urea")].set_index("data")["preco"]
z = m[m.commodity.str.lower().str.startswith("maize")].set_index("data")["preco"]
r = (u / z).dropna()
print("ultimos:", r.tail(8).round(2).to_dict())
print("max 2026:", r["2026"].idxmax().date(), round(r["2026"].max(), 2))
print("media 2000-2020:", round(r["2000":"2020"].mean(), 2))
