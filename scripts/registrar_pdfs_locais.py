"""Copia PDFs obtidos à mão (abertos, CC-BY) para artigos/ e marca como baixados no índice.

Uso: python -I registrar_pdfs_locais.py <doi> <caminho_pdf> [<doi> <caminho_pdf> ...]
"""
import csv
import shutil
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import baixar_artigos as BA  # noqa: E402

pares = list(zip(sys.argv[1::2], sys.argv[2::2]))
with open(BA.DEST / "indice.csv", encoding="utf-8-sig") as f:
    linhas = list(csv.DictReader(f))
por_doi = {l["doi"].lower(): l for l in linhas}
for doi, caminho in pares:
    l = por_doi[doi.lower()]
    origem = Path(caminho)
    assert origem.read_bytes()[:5] == b"%PDF-", origem
    titulo = "_".join(l["titulo"].replace("-", " ").split()[:7])
    titulo = "".join(c for c in titulo if c.isalnum() or c in "_-")
    nome = f"{l['ano']}_{l['primeiro_autor'].split(' et al.')[0].split()[-1]}_{titulo}.pdf"
    shutil.copy2(origem, BA.DEST / nome)
    l.update(status="baixado", arquivo=nome, fonte_pdf="cópia local (página MDPI bloqueia robô)")
    print(doi, "->", nome)
BA.escrever_indice(linhas)
