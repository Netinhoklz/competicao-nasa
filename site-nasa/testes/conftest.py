"""Fixtures dos testes do site: cliente Flask, servidor ao vivo (para o Chrome) e o Chrome sem janela."""
from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

import pytest
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.serving import make_server

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE))

import app as modulo_app  # noqa: E402  (precisa do caminho acima)

NAVEGADORES = [
    os.environ.get("CHROME", ""),
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


@pytest.fixture(scope="session")
def app():
    modulo_app.app.config.update(TESTING=True)
    return modulo_app.app


@pytest.fixture()
def cliente(app):
    return app.test_client()


@pytest.fixture(scope="session")
def servidor(app):
    """Site real numa porta livre; /_testes/ serve as paginas de teste de JavaScript (testes/js/)."""
    wsgi = SharedDataMiddleware(app, {"/_testes": str(SITE / "testes" / "js")})
    srv = make_server("127.0.0.1", 0, wsgi, threaded=True)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


@pytest.fixture(scope="session")
def chrome():
    for c in NAVEGADORES:
        if c and (Path(c).exists() or shutil.which(c)):
            return c
    pytest.skip("Chrome/Edge nao encontrado: defina CHROME=<caminho> para rodar os testes de JavaScript")


@pytest.fixture(scope="session")
def dom(chrome):
    """dom(url) -> HTML da pagina depois que os scripts rodam (Chrome sem janela, --dump-dom)."""
    perfil = tempfile.mkdtemp(prefix="quadra-testes-")

    def _dom(url: str, espera_ms: int = 8000) -> str:
        r = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
             f"--user-data-dir={perfil}", f"--virtual-time-budget={espera_ms}", "--dump-dom", url],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )
        return r.stdout

    yield _dom
    shutil.rmtree(perfil, ignore_errors=True)


def texto_de(html_pagina: str, ident: str) -> str | None:
    """Conteudo de texto do elemento com id `ident` (sem tags), ou None."""
    m = re.search(rf'id="{ident}"[^>]*>(.*?)</', html_pagina, re.S)
    return html.unescape(m.group(1)) if m else None
