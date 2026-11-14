"""Executa celulas de codigo selecionadas de uma secao em formato percent (# %%).

Uso: python -I rodar_celulas.py secao.py 0 1 2      (indices das celulas de CODIGO, a partir de 0)
     python -I rodar_celulas.py secao.py todas
Mostra o indice e o tempo de cada celula; para no primeiro erro.
"""
import os
import sys
import time
import traceback

os.environ.setdefault("MPLBACKEND", "Agg")
sys.stdout.reconfigure(encoding="utf-8")


def celulas(caminho):
    txt = open(caminho, encoding="utf-8").read().splitlines()
    cel, atual, tipo = [], [], None
    for ln in txt:
        if ln.startswith("# %%"):
            if atual and tipo == "code":
                cel.append("\n".join(atual))
            atual = []
            tipo = "markdown" if "[markdown]" in ln else "code"
            continue
        atual.append(ln)
    if atual and tipo == "code":
        cel.append("\n".join(atual))
    return cel


if __name__ == "__main__":
    cs = celulas(sys.argv[1])
    sel = range(len(cs)) if sys.argv[2:] == ["todas"] else [int(x) for x in sys.argv[2:]]
    g = {"__name__": "__main__"}
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.show = lambda *a, **k: plt.close("all")
    t_total = time.time()
    for i in sel:
        t0 = time.time()
        print(f"\n===== célula de código {i} =====", flush=True)
        try:
            exec(compile(cs[i], f"celula_{i}", "exec"), g)
        except Exception:
            traceback.print_exc()
            print(f"FALHOU na célula {i}")
            sys.exit(1)
        print(f"[célula {i}: {time.time() - t0:.1f}s]", flush=True)
    print(f"\nTOTAL {time.time() - t_total:.1f}s ({len(cs)} células de código na seção)")
