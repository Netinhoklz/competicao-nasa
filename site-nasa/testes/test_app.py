"""Servidor Flask (app.py): paginas, busca de lugares, validacao das entradas e compressao."""
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path

import pytest
import requests

import app as modulo_app


# ------------------------------------------------------------------ paginas

def test_inicio_tem_as_frases_novas(cliente):
    r = cliente.get("/")
    assert r.status_code == 200
    corpo = r.get_data(as_text=True)
    assert "Dá órbita pro campo" in corpo
    assert "Qual é o seu município?" in corpo
    assert "dados de satélite da NASA</p>" not in corpo      # frase antiga do sobretitulo


@pytest.mark.parametrize("url, cod", [
    ("/painel", "2311306"),                 # sem codigo: Quixada
    ("/painel/2304400", "2304400"),         # Fortaleza
    ("/painel/abc", "2311306"),             # codigo invalido volta para Quixada
    ("/painel/123", "2311306"),
])
def test_painel_codigo(cliente, url, cod):
    r = cliente.get(url)
    assert r.status_code == 200
    assert f'data-cod="{cod}"' in r.get_data(as_text=True)


@pytest.mark.parametrize("template", ["index.html", "painel.html"])
def test_templates_apontam_para_arquivos_que_existem(template):
    raiz = Path(modulo_app.app.root_path)
    estaticos = re.findall(r"filename='([^']+)'", (raiz / "templates" / template).read_text(encoding="utf-8"))
    assert estaticos, "o template deveria usar url_for('static', ...)"
    faltando = [arq for arq in estaticos if not (raiz / "static" / arq).exists()]
    assert not faltando


def test_modulos_js_importam_arquivos_que_existem():
    """Todo `import ... from './x.js'` dos scripts do site aponta para um arquivo que existe."""
    pasta = Path(modulo_app.app.root_path) / "static" / "js"
    faltando = [(js.name, alvo) for js in pasta.glob("*.js")
                for alvo in re.findall(r"from '\./([^']+)'", js.read_text(encoding="utf-8"))
                if not (pasta / alvo).exists()]
    assert not faltando


# ------------------------------------------------------------------ /api/geocode

def test_geocode_sem_texto(cliente):
    assert cliente.get("/api/geocode").status_code == 400
    assert cliente.get("/api/geocode?q=%20%20").status_code == 400


def test_geocode_texto_longo(cliente):
    assert cliente.get("/api/geocode?q=" + "a" * 161).status_code == 400


@pytest.mark.parametrize("q, lat, lon", [
    ("-4.97, -39.01", -4.97, -39.01),
    ("-4.97 -39.01", -4.97, -39.01),
    ("-4.97;-39.01", -4.97, -39.01),
    ("12, 45", 12.0, 45.0),
])
def test_geocode_coordenadas(cliente, q, lat, lon):
    r = cliente.get("/api/geocode", query_string={"q": q})
    assert r.status_code == 200
    (lugar,) = r.get_json()["resultados"]
    assert (lugar["lat"], lugar["lon"], lugar["tipo"]) == (lat, lon, "coordenada")


def test_geocode_coordenada_fora_do_globo(cliente):
    assert cliente.get("/api/geocode", query_string={"q": "95, 10"}).status_code == 400


def test_geocode_texto_usa_nominatim(cliente, monkeypatch):
    vistos = []

    def falso(texto):
        vistos.append(texto)
        return ({"nome": "Quixadá", "detalhe": "Ceará", "lat": -4.97, "lon": -39.01, "bbox": None, "tipo": "town", "ibge": "2311306"},)

    monkeypatch.setattr(modulo_app, "_buscar", falso)
    r = cliente.get("/api/geocode", query_string={"q": "QUIXADÁ"})
    assert r.status_code == 200
    assert r.get_json()["resultados"][0]["ibge"] == "2311306"
    assert vistos == ["quixadá"]                              # o cache usa o texto em minusculas


def test_geocode_nominatim_fora_do_ar(cliente, monkeypatch):
    def falha(_):
        raise requests.ConnectionError("sem rede")

    monkeypatch.setattr(modulo_app, "_buscar", falha)
    assert cliente.get("/api/geocode", query_string={"q": "quixada"}).status_code == 502


# ------------------------------------------------------------------ /api/reverse

@pytest.mark.parametrize("qs", [{}, {"lat": "x", "lon": "1"}, {"lat": "1"}])
def test_reverse_parametros_invalidos(cliente, qs):
    assert cliente.get("/api/reverse", query_string=qs).status_code == 400


def test_reverse_fora_do_globo(cliente):
    assert cliente.get("/api/reverse", query_string={"lat": 100, "lon": 0}).status_code == 400


def test_reverse_no_oceano_devolve_a_coordenada(cliente, monkeypatch):
    monkeypatch.setattr(modulo_app, "_reverso", lambda lat, lon: None)
    r = cliente.get("/api/reverse", query_string={"lat": -10, "lon": -30})
    assert r.status_code == 200
    assert r.get_json()["resultado"]["tipo"] == "coordenada"


def test_reverse_sem_rede_nao_quebra(cliente, monkeypatch):
    def falha(lat, lon):
        raise requests.Timeout()

    monkeypatch.setattr(modulo_app, "_reverso", falha)
    assert cliente.get("/api/reverse", query_string={"lat": -5, "lon": -39}).get_json()["resultado"]["tipo"] == "coordenada"


def test_lugar_converte_bbox_e_codigo_ibge():
    item = {"name": "Quixadá", "display_name": "Quixadá, Ceará, Região Nordeste, Brasil", "lat": "-4.97",
            "lon": "-39.01", "boundingbox": ["-5.2", "-4.7", "-39.3", "-38.8"], "addresstype": "town",
            "extratags": {"IBGE:GEOCODIGO": "2311306"}}
    lugar = modulo_app._lugar(item)
    assert lugar["bbox"] == [-39.3, -5.2, -38.8, -4.7]        # [oeste, sul, leste, norte]
    assert lugar["detalhe"] == "Ceará, Região Nordeste, Brasil"
    assert lugar["ibge"] == "2311306"


# ------------------------------------------------------------------ compressao

def test_json_sai_comprimido(cliente):
    r = cliente.get("/static/data/municipios_ne.json", headers={"Accept-Encoding": "gzip, deflate"})
    assert r.headers.get("Content-Encoding") == "gzip"
    assert "Accept-Encoding" in r.headers.get("Vary", "")
    dados = json.loads(gzip.decompress(r.get_data()))
    assert len(dados["m"]) == 1794


def test_sem_pedido_de_gzip_vai_puro(cliente):
    r = cliente.get("/static/data/municipios_ne.json")
    assert "Content-Encoding" not in r.headers
    assert json.loads(r.get_data())["anos"][0] == 1998


def test_imagem_nao_e_recomprimida(cliente):
    r = cliente.get("/static/textures/moon.webp", headers={"Accept-Encoding": "gzip"})
    assert r.status_code == 200
    assert "Content-Encoding" not in r.headers
