"""Junta notebooks/secoes/*.py (formato percent: '# %%' e '# %% [markdown]') em um .ipynb e, opcionalmente, executa.

Uso:
  python montar_notebook.py --saida notebooks/estudo.ipynb [--secoes 00 01 02 ...] [--executar] [--timeout 900]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import nbformat

PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
SECOES = PROJ / "notebooks" / "secoes"
MARCA = re.compile(r"^# %%(?P<md>\s*\[markdown\])?\s*$")


def ler_secao(p: Path):
    celulas, atual, tipo = [], [], None

    def fechar():
        if tipo is None:
            return
        texto = "\n".join(atual).strip("\n")
        if not texto.strip():
            return
        if tipo == "md":
            linhas = [l[2:] if l.startswith("# ") else ("" if l.strip() == "#" else l) for l in texto.split("\n")]
            celulas.append(nbformat.v4.new_markdown_cell("\n".join(linhas)))
        else:
            celulas.append(nbformat.v4.new_code_cell(texto))

    for linha in p.read_text(encoding="utf-8").splitlines():
        m = MARCA.match(linha)
        if m:
            fechar()
            atual, tipo = [], ("md" if m.group("md") else "code")
        else:
            if tipo is None:  # cabecalho antes da 1a marca vira codigo
                tipo = "code"
            atual.append(linha)
    fechar()
    return celulas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", required=True)
    ap.add_argument("--secoes", nargs="*", help="prefixos (ex.: 00 01 20); padrao = todas")
    ap.add_argument("--executar", action="store_true")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--kernel", default="campeonato-nasa")
    a = ap.parse_args()

    arquivos = sorted(SECOES.glob("*.py"))
    if a.secoes:
        arquivos = [f for f in arquivos if any(f.name.startswith(s) for s in a.secoes)]
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": a.kernel, "display_name": "Python (campeonato-nasa)", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    for f in arquivos:
        cel = ler_secao(f)
        print(f"{f.name}: {len(cel)} celulas")
        nb.cells.extend(cel)

    saida = Path(a.saida)
    if not saida.is_absolute():
        saida = PROJ / saida
    saida.parent.mkdir(parents=True, exist_ok=True)

    if a.executar:
        from nbconvert.preprocessors import ExecutePreprocessor
        ep = ExecutePreprocessor(timeout=a.timeout, kernel_name=a.kernel, allow_errors=True)
        ep.preprocess(nb, {"metadata": {"path": str(PROJ / "notebooks")}})
        erros = [c for c in nb.cells if c.cell_type == "code" and any(o.get("output_type") == "error" for o in c.get("outputs", []))]
        print(f"celulas com erro: {len(erros)}")
        for c in erros[:10]:
            for o in c["outputs"]:
                if o.get("output_type") == "error":
                    print("  ", o.get("ename"), str(o.get("evalue"))[:200])
    nbformat.write(nb, saida)
    print("gravado:", saida, f"{saida.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    sys.exit(main())
