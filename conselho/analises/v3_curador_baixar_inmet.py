"""Curador de bases (v3): baixa os ZIPs anuais de dados horarios das estacoes automaticas do INMET
(portal.inmet.gov.br/dadoshistoricos), extrai SO as estacoes do Nordeste (nome do CSV traz _NE_) e apaga o ZIP.

Saida: E:/campeonato-nasa/dados/complementares/inmet/horario_ne/<ano>/*.CSV + MANIFESTO.json
Uso: python -I v3_curador_baixar_inmet.py 2016 2025
Obs.: o portal derruba a conexao sem User-Agent de navegador (testado em 14/11/2026).
"""
import sys
import zipfile

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

BASE = DADOS / "complementares" / "inmet"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def main(a0, a1):
    s = sessao_http()
    s.headers["User-Agent"] = UA
    tmp = BASE / "_zips"
    tmp.mkdir(parents=True, exist_ok=True)
    resumo = {}
    for ano in range(a0, a1 + 1):
        dest = BASE / "horario_ne" / str(ano)
        if dest.exists() and any(dest.iterdir()):
            print(ano, "ja extraido", flush=True)
            resumo[ano] = len(list(dest.iterdir()))
            continue
        z = tmp / f"{ano}.zip"
        url = f"https://portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip"
        t0 = time.time()
        with s.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(z, "wb") as f:
                for b in r.iter_content(1 << 20):
                    f.write(b)
        dest.mkdir(parents=True, exist_ok=True)
        n = 0
        with zipfile.ZipFile(z) as zf:
            for nome in zf.namelist():
                base = nome.split("/")[-1]
                if "_NE_" in base.upper() and base.upper().endswith(".CSV"):
                    (dest / base).write_bytes(zf.read(nome))
                    n += 1
        mb = z.stat().st_size / 1e6
        z.unlink()
        resumo[ano] = n
        print(ano, f"{mb:.0f} MB baixados, {n} CSVs do NE extraidos, {time.time()-t0:.0f}s", flush=True)
    tmp.rmdir() if not any(tmp.iterdir()) else None
    registrar_manifesto("complementares/inmet", {
        "fonte": "INMET, dados historicos horarios das estacoes automaticas",
        "url": "https://portal.inmet.gov.br/dadoshistoricos",
        "recorte": "so os CSV com regiao NE no nome; ZIP original apagado apos extracao",
        "anos_csvs": resumo,
        "script": "conselho/analises/v3_curador_baixar_inmet.py",
    }, base=BASE)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
