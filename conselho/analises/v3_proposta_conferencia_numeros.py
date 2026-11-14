"""Confere os números que a v3 da proposta acrescentou à v2.

Só lê arquivos e imprime na tela (não grava nada).
Para cada linha da v3 que não existe na v2, extrai os números e procura cada um
na v2 e nas fontes da rodada 3. Lista os que não aparecem em nenhuma fonte.
"""
import difflib
import re
from pathlib import Path

RAIZ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
V2 = RAIZ / "proposta" / "PROPOSTA_FINAL_v2.md"
V3 = RAIZ / "proposta" / "PROPOSTA_FINAL_v3.md"
FONTES = [
    V2,
    RAIZ / "pesquisa" / "viabilidade_artigos_nordeste.md",
    RAIZ / "pesquisa" / "catalogo_rotacoes_comprovadas.md",
    RAIZ / "pesquisa" / "el_nino_2026_nordeste.md",
    RAIZ / "proposta" / "estrutura_gaez_zarc.md",
    *sorted((RAIZ / "notebooks" / "secoes_analogos").glob("*.py")),
]

NUM = re.compile(r"(?<![\w/])[−+-]?\d+(?:[.,]\d+)*(?:\s?%)?")


def normaliza(t: str) -> str:
    t = t.replace("−", "-").replace("\u2009", " ").replace("\xa0", " ")
    t = re.sub(r"\s?%", "%", t)
    return t.lstrip("+")


def main() -> None:
    v2 = V2.read_text(encoding="utf-8").splitlines()
    v3 = V3.read_text(encoding="utf-8").splitlines()
    texto_fontes = "\n".join(normaliza(f.read_text(encoding="utf-8")) for f in FONTES)
    novas = [l for l in difflib.ndiff(v2, v3) if l.startswith("+ ")]
    faltam = {}
    total = 0
    for linha in novas:
        for m in NUM.finditer(linha[2:]):
            tok = normaliza(m.group(0)).strip()
            nu = tok.lstrip("-").rstrip("%")
            if len(nu.replace(",", "").replace(".", "")) <= 1:
                continue  # dígitos soltos (1, 2, 3...) são contagem de itens
            total += 1
            if tok in texto_fontes or tok.lstrip("-") in texto_fontes:
                continue
            faltam.setdefault(tok, []).append(linha[2:80])
    print(f"Linhas novas na v3: {len(novas)}; números conferidos: {total}; sem fonte literal: {len(faltam)}")
    for tok, onde in sorted(faltam.items()):
        print(f"  {tok!r}: {onde[0]!r}")


if __name__ == "__main__":
    main()
