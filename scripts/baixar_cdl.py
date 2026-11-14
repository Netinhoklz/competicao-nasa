"""Baixa camadas nacionais do USDA Cropland Data Layer (CDL) para estudo (somente EUA).

Confere o tamanho final contra o Content-Length, retoma com Range e tenta de novo.
Uso: python -I baixar_cdl.py Crop_Frequency_2008-2025 2025_30m_cdls ...
"""
import sys
import time

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import ESTUDO_CDL, registrar_manifesto, sessao_http  # noqa: E402

BASE = "https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/Release/datasets"


def tamanho_remoto(s, url):
    r = s.head(url, allow_redirects=True, timeout=60)
    r.raise_for_status()
    return int(r.headers["Content-Length"])


def baixar_retomando(s, url, destino, total, tentativas=20):
    for t in range(tentativas):
        feito = destino.stat().st_size if destino.exists() else 0
        if feito == total:
            return True
        if feito > total:
            destino.unlink()
            feito = 0
        cab = {"Range": f"bytes={feito}-"} if feito else {}
        try:
            with s.get(url, headers=cab, stream=True, timeout=120) as r:
                if feito and r.status_code != 206:
                    destino.unlink()
                    continue
                r.raise_for_status()
                with open(destino, "ab" if feito else "wb") as f:
                    for b in r.iter_content(1 << 20):
                        f.write(b)
        except Exception as e:  # rede instavel: tenta de novo
            print(f"  tentativa {t+1}: {type(e).__name__}: {str(e)[:120]}", flush=True)
            time.sleep(min(60, 5 * (t + 1)))
    return destino.exists() and destino.stat().st_size == total


def main(nomes):
    s = sessao_http()
    ESTUDO_CDL.mkdir(parents=True, exist_ok=True)
    arquivos = {}
    for n in nomes:
        url = f"{BASE}/{n}.zip"
        destino = ESTUDO_CDL / f"{n}.zip"
        total = tamanho_remoto(s, url)
        t0 = time.time()
        ok = baixar_retomando(s, url, destino, total)
        print(f"{n}: ok={ok} {destino.stat().st_size/1e9:.2f}/{total/1e9:.2f} GB em {time.time()-t0:.0f}s", flush=True)
        arquivos[n] = {"url": url, "bytes": destino.stat().st_size, "esperado": total, "ok": ok}
    registrar_manifesto("cdl", {
        "fonte": "USDA NASS Cropland Data Layer (nacional, 30 m)",
        "cobertura": "Estados Unidos contiguos (CONUS) - NAO e global",
        "pagina": "https://www.nass.usda.gov/research-and-science/cropland/release",
        "arquivos_" + "_".join(nomes): arquivos,
    }, base=ESTUDO_CDL)


if __name__ == "__main__":
    main(sys.argv[1:])
