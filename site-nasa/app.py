"""Servidor Flask do site do QUADRA (NASA Space Apps 2026, desafio Field Shift).

Rotas:
  /                 pagina inicial (globo 3D + busca + mapa)
  /api/geocode?q=   texto ou "lat, lon" -> lista de lugares reais (Nominatim/OpenStreetMap)
  /api/reverse      lat, lon -> nome do lugar (usado quando a pessoa clica no globo)

Uso: python app.py  (abre em http://127.0.0.1:5000)
"""
from __future__ import annotations

import os
import re
from functools import lru_cache

import requests
from flask import Flask, jsonify, render_template, request

# Mesmo ajuste de certificados dos scripts do projeto (scripts/comum.py): o repositorio
# do Windows nao confia em algumas raizes; o pacote do Git confia.
_CA_GIT = "C:/Program Files/Git/mingw64/etc/ssl/certs/ca-bundle.crt"
if os.path.exists(_CA_GIT):
    os.environ.setdefault("REQUESTS_CA_BUNDLE", _CA_GIT)

app = Flask(__name__)

NOMINATIM = "https://nominatim.openstreetmap.org"
# A politica do Nominatim pede um User-Agent que identifique a aplicacao.
CABECALHOS = {"User-Agent": "QUADRA-FieldShift-site/0.1 (NASA Space Apps 2026 demo)"}
TIMEOUT_S = 8
MAX_TEXTO = 160

# "-4.97, -39.01" ou "-4.97 -39.01" ou "-4.97; -39.01" (decimal com ponto)
RE_COORD = re.compile(r"^\s*(-?\d{1,2}(?:\.\d+)?)\s*[,;\s]\s*(-?\d{1,3}(?:\.\d+)?)\s*$")


def _lugar(item: dict) -> dict:
    """Converte um resultado do Nominatim para o formato usado pelo front-end."""
    partes = [p.strip() for p in item.get("display_name", "").split(",") if p.strip()]
    # boundingbox do Nominatim: [lat_min, lat_max, lon_min, lon_max] (strings)
    bb = item.get("boundingbox")
    bbox = None
    if bb and len(bb) == 4:
        s, n, w, e = (float(v) for v in bb)
        bbox = [w, s, e, n]
    return {
        "nome": item.get("name") or (partes[0] if partes else "Lugar sem nome"),
        "detalhe": ", ".join(partes[1:]) if len(partes) > 1 else "",
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
        "bbox": bbox,
        "tipo": item.get("addresstype") or item.get("type") or "",
    }


@lru_cache(maxsize=512)
def _buscar(texto: str) -> tuple:
    r = requests.get(
        f"{NOMINATIM}/search",
        params={"q": texto, "format": "jsonv2", "limit": 6, "accept-language": "pt-BR,pt,en"},
        headers=CABECALHOS,
        timeout=TIMEOUT_S,
    )
    r.raise_for_status()
    return tuple(_lugar(i) for i in r.json())


@lru_cache(maxsize=512)
def _reverso(lat: float, lon: float) -> dict | None:
    r = requests.get(
        f"{NOMINATIM}/reverse",
        params={"lat": lat, "lon": lon, "zoom": 10, "format": "jsonv2", "accept-language": "pt-BR,pt,en"},
        headers=CABECALHOS,
        timeout=TIMEOUT_S,
    )
    r.raise_for_status()
    dados = r.json()
    return None if "error" in dados else _lugar(dados)


def _coordenada(lat: float, lon: float) -> dict:
    return {"nome": f"{lat:.4f}, {lon:.4f}", "detalhe": "Coordenada informada", "lat": lat, "lon": lon,
            "bbox": None, "tipo": "coordenada"}


@app.get("/")
def inicio():
    return render_template("index.html")


@app.get("/api/geocode")
def geocode():
    texto = (request.args.get("q") or "").strip()
    if not texto:
        return jsonify(erro="Digite um lugar."), 400
    if len(texto) > MAX_TEXTO:
        return jsonify(erro="Texto longo demais."), 400

    m = RE_COORD.match(texto)
    if m:
        lat, lon = float(m.group(1)), float(m.group(2))
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return jsonify(resultados=[_coordenada(lat, lon)])
        return jsonify(erro="Coordenada fora do globo: latitude vai de -90 a 90 e longitude de -180 a 180."), 400

    try:
        resultados = _buscar(texto.lower())
    except requests.RequestException:
        return jsonify(erro="O serviço de busca não respondeu. Tente de novo em instantes."), 502
    return jsonify(resultados=list(resultados))


@app.get("/api/reverse")
def reverse():
    try:
        lat = round(float(request.args["lat"]), 3)
        lon = round(float(request.args["lon"]), 3)
    except (KeyError, ValueError):
        return jsonify(erro="Informe lat e lon."), 400
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return jsonify(erro="Coordenada fora do globo."), 400

    try:
        lugar = _reverso(lat, lon)
    except requests.RequestException:
        lugar = None
    # No oceano o Nominatim nao acha nada: devolve a propria coordenada.
    return jsonify(resultado=lugar or _coordenada(lat, lon))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
