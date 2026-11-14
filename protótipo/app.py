"""Servidor do protótipo QUADRA (só biblioteca padrão do Python).

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -X utf8 app.py [porta]   ->  http://localhost:8765
Rotas:
  /                      página (static/index.html)
  /api/local?lat=&lon=   o que o lugar permite: cardápio, datas, este ano, plano de rotação e evidência
  /api/municipios        malha dos 1.794 municípios do Nordeste (GeoJSON; a mesma que o motor usa)
"""
import json
import math
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np

import motor

STATIC = Path(__file__).resolve().parent / "static"
MUN_JSON = motor.municipios_geojson().encode("utf-8")


def _limpa(o):
    """NaN e infinito viram null; tipos do numpy viram tipos do Python (JSON válido sem trocar texto)."""
    if isinstance(o, dict):
        return {k: _limpa(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_limpa(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return None if not math.isfinite(float(o)) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


class Rotas(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(STATIC), **k)

    def _responder(self, corpo, tipo="application/json; charset=utf-8", status=200):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _erro(self, status, msg):
        self._responder(json.dumps({"erro": msg}, ensure_ascii=False).encode("utf-8"), status=status)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/local":
            q = parse_qs(u.query)
            try:
                lat, lon = float(q["lat"][0]), float(q["lon"][0])
            except (KeyError, ValueError, IndexError):
                return self._erro(400, "Informe lat e lon numéricos, por exemplo ?lat=-4.97&lon=-39.02.")
            if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90):
                return self._erro(400, "Latitude entre −90 e 90 e longitude finita.")
            try:
                corpo = json.dumps(_limpa(motor.consultar(lat, lon)), ensure_ascii=False, allow_nan=False)
                self._responder(corpo.encode("utf-8"))
            except Exception as e:  # o protótipo mostra o erro na tela em vez de cair
                self._erro(500, f"{type(e).__name__}: {e}")
        elif u.path == "/api/municipios":
            self._responder(MUN_JSON, "application/geo+json; charset=utf-8")
        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        if "/api/" in str(args[0] if args else ""):  # args[0] pode ser HTTPStatus (ex.: 404 do favicon)
            sys.stderr.write("%s\n" % (fmt % args))


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"QUADRA protótipo em http://localhost:{porta}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", porta), Rotas).serve_forever()
