"""Fotografa o site em tempo real com o Chrome (ou Edge) headless via DevTools Protocol.

Requer o servidor rodando (python app.py) e o pacote websocket-client.

Exemplos:
    # inicio, fotos aos 4 s e 8 s
    python ferramentas/captura.py saidas/inicio --fotos 4 8

    # viagem automatica ate Quixada (parametro ?lugar=), fotos ao longo da viagem
    python ferramentas/captura.py saidas/quixada --url "http://127.0.0.1:5000/?lugar=Quixadá, Ceará" --fotos 4 7 10 16

    # acao em JS num instante (s:codigo), ex.: clicar no botao de voltar aos 18 s
    python ferramentas/captura.py saidas/volta --url "http://127.0.0.1:5000/?lugar=Fortaleza" \
        --fotos 16 20 24 --acao "17:document.getElementById('voltar').click()"

    # celular
    python ferramentas/captura.py saidas/cel --largura 390 --altura 844 --fotos 5

Cada foto vira <prefixo>_<t>s.png. Mensagens e erros do console saem no terminal.
"""
from __future__ import annotations

import argparse
import base64
import json
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket  # websocket-client

NAVEGADORES = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
]


def porta_livre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Aba:
    def __init__(self, ws_url: str):
        self.ws = websocket.create_connection(ws_url, timeout=30, suppress_origin=True)
        self.ws.settimeout(0.2)
        self.n = 0
        self.respostas: dict[int, dict] = {}
        self.vistas: dict[str, int] = {}

    def avisar(self, texto: str) -> None:
        """Imprime cada mensagem uma vez so (o WebGL repete o mesmo aviso a cada quadro)."""
        self.vistas[texto] = self.vistas.get(texto, 0) + 1
        if self.vistas[texto] == 1:
            print(texto)

    def enviar(self, metodo: str, **params) -> int:
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": metodo, "params": params}))
        return self.n

    def chamar(self, metodo: str, espera: float = 60, **params) -> dict:
        i = self.enviar(metodo, **params)
        fim = time.time() + espera
        while time.time() < fim:
            self.bombear()
            if i in self.respostas:
                r = self.respostas.pop(i)
                if "error" in r:
                    raise RuntimeError(f"{metodo}: {r['error']}")
                return r.get("result", {})
        raise TimeoutError(metodo)

    def bombear(self) -> None:
        try:
            msg = json.loads(self.ws.recv())
        except websocket.WebSocketTimeoutException:
            return
        if "id" in msg:
            self.respostas[msg["id"]] = msg
            return
        metodo = msg.get("method")
        p = msg.get("params", {})
        if metodo == "Runtime.consoleAPICalled":
            texto = " ".join(str(a.get("value", a.get("description", ""))) for a in p.get("args", []))
            self.avisar(f"[console.{p.get('type')}] {texto}")
        elif metodo == "Runtime.exceptionThrown":
            d = p.get("exceptionDetails", {})
            desc = d.get("exception", {}).get("description") or d.get("text")
            self.avisar(f"[ERRO JS] {desc} ({d.get('url', '')}:{d.get('lineNumber')})")
        elif metodo == "Log.entryAdded":
            e = p.get("entry", {})
            if e.get("level") in ("error", "warning"):
                self.avisar(f"[{e.get('level')}] {e.get('text')} {e.get('url', '')}")

    def esperar_ate(self, t_alvo: float) -> None:
        while time.time() < t_alvo:
            self.bombear()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prefixo", help="caminho base das fotos (sem extensao)")
    ap.add_argument("--url", default="http://127.0.0.1:5000/")
    ap.add_argument("--largura", type=int, default=1600)
    ap.add_argument("--altura", type=int, default=900)
    ap.add_argument("--fotos", type=float, nargs="+", default=[5.0], help="instantes (s) das fotos")
    ap.add_argument("--acao", action="append", default=[], help="'s:codigo JS' executado no instante s")
    ap.add_argument("--calmo", action="store_true",
                    help="simula 'reduzir movimento' (o headless ja vem assim; por padrao desligamos)")
    a = ap.parse_args()

    nav = next((n for n in NAVEGADORES if Path(n).exists()), None)
    if nav is None:
        raise SystemExit("Nenhum Chrome/Edge encontrado.")
    prefixo = Path(a.prefixo).resolve()
    prefixo.parent.mkdir(parents=True, exist_ok=True)

    porta = porta_livre()
    perfil = tempfile.mkdtemp(prefix="captura_")
    proc = subprocess.Popen(
        [
            nav, "--headless=new", f"--user-data-dir={perfil}", f"--remote-debugging-port={porta}",
            "--remote-allow-origins=*", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
            "--ignore-gpu-blocklist", "--hide-scrollbars", "--no-first-run", "--mute-audio",
            f"--window-size={a.largura},{a.altura}", "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        alvos = None
        for _ in range(100):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{porta}/json/list", timeout=2) as r:
                    alvos = [t for t in json.load(r) if t.get("type") == "page"]
                if alvos:
                    break
            except OSError:
                pass
            time.sleep(0.2)
        if not alvos:
            raise SystemExit("O navegador nao abriu a porta de depuracao.")

        aba = Aba(alvos[0]["webSocketDebuggerUrl"])
        for m in ("Runtime.enable", "Log.enable", "Page.enable"):
            aba.chamar(m)
        aba.chamar("Emulation.setDeviceMetricsOverride", width=a.largura, height=a.altura,
                   deviceScaleFactor=1, mobile=a.largura < 700)
        aba.chamar("Emulation.setEmulatedMedia", features=[
            {"name": "prefers-reduced-motion", "value": "reduce" if a.calmo else "no-preference"},
        ])
        aba.chamar("Page.navigate", url=a.url)
        t0 = time.time()

        eventos = [(float(s), "foto", None) for s in a.fotos]
        for ac in a.acao:
            s, codigo = ac.split(":", 1)
            eventos.append((float(s), "acao", codigo))
        for instante, tipo, codigo in sorted(eventos, key=lambda e: e[0]):
            aba.esperar_ate(t0 + instante)
            if tipo == "acao":
                r = aba.chamar("Runtime.evaluate", expression=codigo, awaitPromise=False)
                if r.get("exceptionDetails"):
                    print(f"[acao {instante}s falhou] {r['exceptionDetails'].get('text')}")
                continue
            dados = aba.chamar("Page.captureScreenshot", format="png")["data"]
            nome = prefixo.with_name(f"{prefixo.name}_{instante:g}s.png")
            nome.write_bytes(base64.b64decode(dados))
            print(nome)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(perfil, ignore_errors=True)


if __name__ == "__main__":
    main()
