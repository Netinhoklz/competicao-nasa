"""Abre uma página no Edge sem janela e imprime os erros de JS e do console (para achar por que um passo não desenha).
Uso: MSYS_NO_PATHCONV=1 python erros_console.py "http://127.0.0.1:8090/roca.html#/2311306/1" [espera_s]"""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

url = sys.argv[1]
espera = float(sys.argv[2]) if len(sys.argv) > 2 else 8
porta = 9300 + os.getpid() % 500
perfil = os.path.join(tempfile.gettempdir(), f"quadra-erros-{os.getpid()}")
edge = subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "--headless=new", "--disable-gpu",
                         f"--remote-debugging-port={porta}", f"--user-data-dir={perfil}", "about:blank"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try:
            pag = next(a for a in json.load(urllib.request.urlopen(f"http://127.0.0.1:{porta}/json")) if a["type"] == "page")
            break
        except Exception:
            time.sleep(0.3)
    ws = websocket.create_connection(pag["webSocketDebuggerUrl"], timeout=5)
    n = [0]

    def cmd(metodo, **p):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": metodo, "params": p}))
        return n[0]

    for m in ("Runtime.enable", "Log.enable", "Page.enable"):
        cmd(m)
    cmd("Page.navigate", url=url)
    fim = time.time() + espera
    while time.time() < fim:
        try:
            ev = json.loads(ws.recv())
        except Exception:
            continue
        met = ev.get("method")
        if met == "Runtime.exceptionThrown":
            d = ev["params"]["exceptionDetails"]
            print("EXCEÇÃO:", d.get("text"), (d.get("exception") or {}).get("description", "")[:400], d.get("url", ""), d.get("lineNumber"))
        elif met == "Runtime.consoleAPICalled" and ev["params"]["type"] in ("error", "warning"):
            print("CONSOLE", ev["params"]["type"], " ".join(str(a.get("value", a.get("description", ""))) for a in ev["params"]["args"])[:400])
        elif met == "Log.entryAdded" and ev["params"]["entry"]["level"] in ("error", "warning"):
            e = ev["params"]["entry"]
            print("LOG", e["level"], e.get("text", "")[:300], e.get("url", ""))
    cmd("Runtime.evaluate", expression="(document.getElementById('jornada')||{}).innerText?.slice(0,200)", returnByValue=True)
    ws.settimeout(5)
    while True:
        ev = json.loads(ws.recv())
        if "result" in ev and "result" in ev["result"]:
            print("TEXTO:", ev["result"]["result"].get("value"))
            break
finally:
    edge.terminate()
