"""Servidor do QUADRA, site final (só a biblioteca padrão do Python + o núcleo em nucleo/motor.py).

Uso:  E:/campeonato-nasa/venv/Scripts/python.exe -X utf8 servidor.py [porta]   ->  http://localhost:8090
Rotas:
  /                       o site (web/): globo do João Pedro em index.html e a jornada em roca.html
  /api/local              ?lat=&lon=  ou  ?cod=<IBGE>; opcionais: textura=1-3, ad=11-16, ad_baixio=11-16,
                          maniva=tem|nao|plantada, baixio=0|1, hoje=AAAA-MM-DD
  /api/municipios         malha dos 1.794 municípios do Nordeste (GeoJSON, a mesma do núcleo)
"""
import json
import math
import sys
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "nucleo"))
import motor  # noqa: E402

WEB = AQUI / "web"
MUN_JSON = motor.municipios_geojson().encode("utf-8")
TIPOS = {".js": "text/javascript; charset=utf-8", ".mjs": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".html": "text/html; charset=utf-8", ".json": "application/json; charset=utf-8", ".geojson": "application/geo+json",
         ".svg": "image/svg+xml", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".woff2": "font/woff2",
         ".woff": "font/woff", ".md": "text/markdown; charset=utf-8", ".pdf": "application/pdf", ".wasm": "application/wasm"}


def _limpa(o):
    """NaN e infinito viram null; tipos do numpy viram tipos do Python (JSON válido)."""
    if isinstance(o, dict):
        return {k: _limpa(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_limpa(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return None if not math.isfinite(float(o)) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def _opcoes(q):
    """Valida as respostas do agricultor que mudam o núcleo; levanta ValueError com mensagem curta."""
    v = lambda k: (q.get(k, [""])[0] or "").strip() or None  # noqa: E731
    textura, ad, ad_b, maniva, baixio, hoje = v("textura"), v("ad"), v("ad_baixio"), v("maniva"), v("baixio"), v("hoje")
    if textura not in (None, "1", "2", "3"):
        raise ValueError("textura deve ser 1, 2 ou 3")
    for nome, x in (("ad", ad), ("ad_baixio", ad_b)):
        if x not in (None, "11", "12", "13", "14", "15", "16"):
            raise ValueError(f"{nome} deve ser de 11 a 16")
    if maniva not in (None, "tem", "nao", "plantada"):
        raise ValueError("maniva deve ser tem, nao ou plantada")
    if baixio not in (None, "0", "1"):
        raise ValueError("baixio deve ser 0 ou 1")
    hoje = date.fromisoformat(hoje) if hoje else None
    return {"textura": textura, "ad": ad, "ad_baixio": ad_b, "maniva": maniva, "baixio": baixio != "0", "hoje": hoje}


class Rotas(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, **TIPOS}

    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(WEB), **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

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
                if q.get("cod"):
                    p = motor.ponto_do_municipio(q["cod"][0])
                    if not p:
                        return self._erro(404, "Município não encontrado no Nordeste.")
                    lat, lon = p
                else:
                    lat, lon = float(q["lat"][0]), float(q["lon"][0])
                op = _opcoes(q)
            except (KeyError, IndexError):
                return self._erro(400, "Informe cod (IBGE) ou lat e lon, por exemplo ?cod=2311306.")
            except ValueError as e:
                return self._erro(400, f"Entrada inválida: {e}.")
            if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90):
                return self._erro(400, "Latitude entre −90 e 90 e longitude finita.")
            try:
                corpo = json.dumps(_limpa(motor.consultar(lat, lon, **op)), ensure_ascii=False, allow_nan=False)
                self._responder(corpo.encode("utf-8"))
            except Exception as e:  # o site mostra o erro na tela em vez de cair
                self._erro(500, f"{type(e).__name__}: {e}")
        elif u.path == "/api/municipios":
            self._responder(MUN_JSON, "application/geo+json; charset=utf-8")
        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        if "/api/" in str(args[0] if args else ""):
            sys.stderr.write("%s\n" % (fmt % args))


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    print(f"QUADRA (site final) em http://localhost:{porta}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", porta), Rotas).serve_forever()
