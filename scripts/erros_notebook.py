"""Lista as celulas com erro de um .ipynb executado, com o ultimo titulo markdown antes delas."""
import sys

import nbformat

sys.stdout.reconfigure(encoding="utf-8")
nb = nbformat.read(sys.argv[1], as_version=4)
titulo = ""
for i, c in enumerate(nb.cells):
    if c.cell_type == "markdown":
        for l in c.source.splitlines():
            if l.startswith("#"):
                titulo = l.strip()
                break
    elif c.cell_type == "code":
        for o in c.get("outputs", []):
            if o.get("output_type") == "error":
                print(f"--- celula {i} | secao: {titulo}")
                print("   ", o["ename"], o["evalue"][:300])
                tb = [l for l in o.get("traceback", []) if "line" in l.lower()]
                import re
                limpo = [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in o.get("traceback", [])]
                print("    " + "\n    ".join(limpo[-6:])[:1500])
