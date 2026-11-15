"""Print de qualquer URL com o Edge sem janela, esperando tempo real (serve para páginas com animação).
Uso: MSYS_NO_PATHCONV=1 python print_url.py saida.png largura "http://127.0.0.1:8090/teste/x.html" [espera_s] [js_antes_do_print]"""
import base64
import json
import os
import subprocess
import sys
import shutil
import tempfile
import time
import urllib.request

import websocket

saida, larg, url = sys.argv[1], int(sys.argv[2]), sys.argv[3]
espera = float(sys.argv[4]) if len(sys.argv) > 4 else 6
js = sys.argv[5] if len(sys.argv) > 5 else None
porta = 9800 + os.getpid() % 150
perfil = os.path.join(os.environ.get("QUADRA_PERFIS", "E:/campeonato-nasa/tmp/edge_perfis"), f"quadra-print-{os.getpid()}")
edge = subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                         f"--remote-debugging-port={porta}", f"--user-data-dir={perfil}", "about:blank"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(60):
        try:
            pag = next(a for a in json.load(urllib.request.urlopen(f"http://127.0.0.1:{porta}/json")) if a["type"] == "page")
            break
        except Exception:
            time.sleep(0.3)
    ws = websocket.create_connection(pag["webSocketDebuggerUrl"], timeout=90)
    n = [0]

    def cmd(metodo, **p):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": metodo, "params": p}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == n[0]:
                return m.get("result", {})

    cmd("Emulation.setDeviceMetricsOverride", width=larg, height=900, deviceScaleFactor=1, mobile=larg < 600)
    cmd("Page.enable")
    cmd("Page.navigate", url=url)
    time.sleep(espera)
    if js:
        cmd("Runtime.evaluate", expression=js, awaitPromise=True)
        time.sleep(1.5)
    alt = cmd("Runtime.evaluate", expression="document.documentElement.scrollHeight", returnByValue=True)["result"]["value"]
    cmd("Emulation.setDeviceMetricsOverride", width=larg, height=min(int(alt), 6000), deviceScaleFactor=1, mobile=larg < 600)
    time.sleep(0.8)
    img = cmd("Page.captureScreenshot", format="png", captureBeyondViewport=True)
    open(saida, "wb").write(base64.b64decode(img["data"]))
    print("ok", saida, alt)
finally:
    edge.terminate()
    try:
        edge.wait(timeout=10)
    except Exception:
        pass
    shutil.rmtree(perfil, ignore_errors=True)  # o perfil do Edge (~65 MB) não fica para trás
