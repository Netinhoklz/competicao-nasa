"""Executa uma secao (.py percent) salvando cada figura em PNG (checagem visual).
Uso: python -I salvar_figuras_secao.py <secao.py> <pasta_saida>"""
import sys
import runpy
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

saida = Path(sys.argv[2])
saida.mkdir(parents=True, exist_ok=True)
cont = {"n": 0}


def _show(*a, **k):
    for num in plt.get_fignums():
        cont["n"] += 1
        plt.figure(num).savefig(saida / f"fig_{cont['n']:02d}.png", dpi=70, bbox_inches="tight")
    plt.close("all")


plt.show = _show
runpy.run_path(sys.argv[1], run_name="__main__")
print("figuras:", cont["n"])
