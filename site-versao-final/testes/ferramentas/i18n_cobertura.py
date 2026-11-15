"""Cobertura da tradução para o inglês (web/i18n/en.json; guia em testes/i18n/LEIA-ME.md): o mesmo percurso do i18n_coletar.py,
com ?lang=en. Junta o window.__i18nVistas e o window.__i18nFaltas de cada tela (js/i18n.js: o que não é neutro, na forma de
modelo quando tem número ou nome de lugar; neutro = só número, nome de lugar, unidade, sigla e letra solta) e grava testes/i18n/faltas.json: lista de {chave, onde} do que ainda
aparece em português, em ordem alfabética. Imprime "cobertura: X de Y textos (Z%)".
Uso: MSYS_NO_PATHCONV=1 E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 testes/ferramentas/i18n_cobertura.py [cod,cod,...]
     (padrão: os 7 municípios do aceite, 224 telas, ~40 min. Um só, ex. 2311306: 38 telas, ~9 min.) Um Edge por vez: não junto
     com o aceite (com dois, o servidor recusa pedidos)."""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import aceite_fluxo as A  # noqa: E402
import i18n_coletar as C  # noqa: E402


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cods = args[0].split(",") if args else list(A.MUNS)
    vistas, faltas, ruins, sem_ingles = set(), {}, [], []

    def cada(rot, juntado, erros):
        if erros:
            ruins.append((rot, erros[:3]))
        for j in juntado:
            if j.get("lingua") != "en":
                sem_ingles.append(rot)
            vistas.update(j.get("vistas", []))
            for c in j.get("faltas", []):
                onde = faltas.setdefault(c, [])
                if rot not in onde and len(onde) < 5:
                    onde.append(rot)

    n = C.percorrer("lang=en", cods, cada)
    os.makedirs(C.PASTA, exist_ok=True)
    lista = [{"chave": c, "onde": faltas[c]} for c in sorted(faltas, key=lambda c: (c.casefold(), c))]
    arq = os.path.join(C.PASTA, "faltas.json")
    json.dump(lista, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    y = len(vistas | set(faltas))
    x = y - len(faltas)
    print(f"\n{len(lista)} textos sem tradução em {n} telas → {arq}")
    print(f"telas com erro no console: {len(ruins)}" + "".join(f"\n  {r}: {e}" for r, e in ruins[:10]))
    if sem_ingles:
        print(f"telas que não abriram em inglês: {len(sem_ingles)} (ex.: {sem_ingles[:3]})")
    print(f"cobertura: {x} de {y} textos ({100 * x / max(y, 1):.1f}%)")


if __name__ == "__main__":
    main()
