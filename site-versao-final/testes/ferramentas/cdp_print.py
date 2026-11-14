"""Print de página com largura emulada (o Edge sem janela não desce de ~500 px). Uso:
python cdp_print.py saida.png largura "hash" [espera_s] [tema]"""
import base64
import json
import subprocess
import sys
import time
import urllib.request

import websocket

import tempfile
D = tempfile.gettempdir()  # perfil temporário do Edge
saida, larg, hash_ = sys.argv[1], int(sys.argv[2]), sys.argv[3]
espera = float(sys.argv[4]) if len(sys.argv) > 4 else 8
tema = sys.argv[5] if len(sys.argv) > 5 else None
import os, random
PORTA = random.randint(9400, 9900)
PERFIL = f"{D}/edge_cdp_{os.getpid()}"
edge = subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "--headless=new", "--disable-gpu",
                         f"--remote-debugging-port={PORTA}", f"--user-data-dir={PERFIL}", "about:blank"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try:
            alvos = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORTA}/json"))
            pag = next(a for a in alvos if a["type"] == "page")
            break
        except Exception:
            time.sleep(0.3)
    ws = websocket.create_connection(pag["webSocketDebuggerUrl"], timeout=60)
    n = [0]

    def cmd(metodo, **p):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": metodo, "params": p}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == n[0]:
                return r.get("result", r)

    cmd("Emulation.setDeviceMetricsOverride", width=larg, height=900, deviceScaleFactor=1, mobile=larg < 600)
    if tema:
        cmd("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": tema}])
    cmd("Page.enable")
    cmd("Page.navigate", url=f"http://127.0.0.1:8090/roca.html{hash_}")
    time.sleep(espera)
    print(cmd("Runtime.evaluate", expression="location.href + ' | ' + (document.getElementById('jornada')||{}).innerText?.slice(0,300)", returnByValue=True)["result"].get("value"))
    cmd("Runtime.evaluate", expression="document.querySelectorAll('details').forEach(d=>d.open=true)")
    if len(sys.argv) > 6:
        print("js:", cmd("Runtime.evaluate", expression=sys.argv[6], returnByValue=True)["result"].get("value"))
    m = cmd("Runtime.evaluate", expression="JSON.stringify([document.documentElement.scrollWidth, document.documentElement.scrollHeight, "
            "[...document.querySelectorAll('.passo-dinheiro *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1 && !e.closest('.rola')).length])",
            returnByValue=True)
    sw, sh, fora = json.loads(m["result"]["value"])
    print("scrollWidth", sw, "scrollHeight", sh, "elementos além da largura (fora de .rola):", fora)
    cmd("Emulation.setDeviceMetricsOverride", width=larg, height=min(sh, 16000), deviceScaleFactor=1, mobile=larg < 600)
    time.sleep(1)
    img = cmd("Page.captureScreenshot", format="png", captureBeyondViewport=True)
    open(saida, "wb").write(base64.b64decode(img["data"]))
    print("ok", saida)
finally:
    edge.terminate()
