"""Tira as imagens do README da raiz (docs/img/), em inglês, com o Edge sem janela, do servidor local (QUADRA_BASE ou :8090).

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -X utf8 site-versao-final/ferramentas/prints_readme.py [nome ...]
     (sem nomes, tira todas; com nomes, só as pedidas, por exemplo: globe step-plan)
O site abre em inglês por padrão (js/i18n.js), então o perfil novo do Edge já sai em inglês.
"""
import base64
import io
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket
from PIL import Image

BASE = os.environ.get("QUADRA_BASE", "http://127.0.0.1:8090")
SAIDA = Path(__file__).resolve().parents[2] / "docs" / "img"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PERFIL = os.environ.get("QUADRA_PERFIS", "E:/campeonato-nasa/tmp/edge_perfis") + f"/readme_{os.getpid()}"
PORTA = 9333
R = "?terra=barro&ha=3&baixio=pouco&maniva=plantada&hoje=milho:34,feijao:33,mandioca:33"  # o Seu Antônio do aceite (F3)
# nome: (arquivo, caminho, largura, altura, escala, celular, espera em s, seletor para rolar até ele)
PRINTS = {
    "globe": ("globe.jpg", "/", 1440, 810, 1, False, 16, None),
    "panel": ("panel.png", "/painel.html?cod=2311306", 1440, 900, 1, False, 9, None),
    "step-field": ("step-field.png", "/roca.html#/2311306/2", 390, 844, 2, True, 7, None),
    "step-plan": ("step-plan.png", f"/roca.html#/2311306/3{R}&plano=ideal", 390, 844, 2, True, 9, "#plantio-rocado"),
    "step-earnings": ("step-earnings.png", f"/roca.html#/2311306/4{R}", 390, 844, 2, True, 7, None),
    "step-report": ("step-report.png", f"/roca.html#/2311306/5{R}", 390, 844, 2, True, 7, None),
}


def main():
    nomes = sys.argv[1:] or list(PRINTS)
    SAIDA.mkdir(parents=True, exist_ok=True)
    os.makedirs(os.path.dirname(PERFIL), exist_ok=True)
    edge = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--remote-debugging-port={PORTA}",
                             f"--user-data-dir={PERFIL}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                alvos = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORTA}/json"))
                pag = next(a for a in alvos if a["type"] == "page")
                break
            except Exception:  # noqa: BLE001  (o Edge ainda está subindo)
                time.sleep(0.5)
        ws = websocket.create_connection(pag["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
        n = [0]

        def cdp(metodo, **params):
            n[0] += 1
            ws.send(json.dumps({"id": n[0], "method": metodo, "params": params}))
            while True:
                r = json.loads(ws.recv())
                if r.get("id") == n[0]:
                    return r.get("result", {})

        cdp("Page.enable")
        for nome in nomes:
            arq, caminho, larg, alt, escala, celular, espera, seletor = PRINTS[nome]
            cdp("Page.navigate", url="about:blank")
            cdp("Emulation.setDeviceMetricsOverride", width=larg, height=alt, deviceScaleFactor=escala, mobile=celular)
            cdp("Page.navigate", url=BASE + caminho)
            time.sleep(espera)
            if seletor:
                cdp("Runtime.evaluate", expression=f"document.querySelector({seletor!r})?.scrollIntoView({{block: 'start'}}); "
                                                   "window.scrollBy(0, -70)")
                time.sleep(1.5)
            png = base64.b64decode(cdp("Page.captureScreenshot", format="png")["data"])
            img = Image.open(io.BytesIO(png))
            if arq.endswith(".jpg"):
                img.convert("RGB").save(SAIDA / arq, quality=88, optimize=True)
            else:
                img.save(SAIDA / arq, optimize=True)
            print(f"{arq}: {img.size[0]} x {img.size[1]}, {(SAIDA / arq).stat().st_size / 1024:.0f} KB")
        ws.close()
    finally:
        edge.terminate()


if __name__ == "__main__":
    main()
