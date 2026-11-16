"""QUADRA: start the site (inicia o site).

Usage / Uso:   python app.py [port]      ->  http://localhost:8090

The server is site-versao-final/servidor.py (Python standard library + the engine in site-versao-final/nucleo/motor.py).
This file only checks the packages, starts the server in UTF-8 mode and says which address to open.
O servidor é o site-versao-final/servidor.py; este arquivo só confere os pacotes, sobe o servidor em UTF-8 e diz o endereço.

Hosting (Render): the platform gives the port in the PORT variable and reaches the server from outside, so there the server
listens on 0.0.0.0. On your own computer it listens only on localhost.
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SERVIDOR = AQUI / "site-versao-final" / "servidor.py"
PACOTES = ["numpy", "pandas", "geopandas", "xarray", "netCDF4", "rasterio", "requests"]


def main():
    porta = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PORT", "8090")
    if not porta.isdigit():
        sys.exit("Usage: python app.py [port]   (example: python app.py 8090)")
    faltam = [p for p in PACOTES if importlib.util.find_spec(p) is None]
    if faltam:
        sys.exit(f"Missing Python packages: {', '.join(faltam)}.\nInstall them with:  pip install -r requirements.txt")
    ambiente = dict(os.environ)
    if os.environ.get("RENDER"):  # o Render define RENDER=true: lá o servidor precisa atender de fora
        ambiente.setdefault("QUADRA_HOST", "0.0.0.0")
    print(f"Starting QUADRA. Loading the data takes a few seconds; when the line 'QUADRA (site final)' appears, open\n"
          f"  http://localhost:{porta}\nCtrl+C stops the server.", flush=True)
    try:
        return subprocess.call([sys.executable, "-X", "utf8", "-W", "ignore", str(SERVIDOR), porta], cwd=str(AQUI), env=ambiente)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
