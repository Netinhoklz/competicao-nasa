import sys
from pathlib import Path
sys.argv = [str(Path(__file__))]
exec(open(Path(__file__).parent / "fin.py", encoding="utf8").read().split("# ---------------- autocorrelação")[0])
q = M[M.cod_mun == Q].pivot_table(index="ano", columns="produto", values="R")
k_pl = (0 + 142 + 142) * 2 / 3 + (284 + 142) / 2
k_s0 = (284 + 142) / 2 * 3
for a in EN + [2021, 2022, 2023, 2025]:
    f, mi = q.loc[a, "Feijão"], q.loc[a, "Milho"]
    print(a, "milho", round(mi), "feijao", round(f), "| 2027 plano margem semente", round(f * 2 / 3 + (mi + f) / 2 - k_pl), "S0", round((mi + f) / 2 * 3 - k_s0))
