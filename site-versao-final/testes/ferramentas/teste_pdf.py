"""PDF do Relatório pelo CDP (Page.printToPDF) e contagem de páginas (C4). O --headless=new desta máquina diz "Printing is not
available"; este script tenta os modos em ordem: --headless=old, --headless (padrão), e a linha de comando --print-to-pdf.
Uso: MSYS_NO_PATHCONV=1 E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 teste_pdf.py [hash] [saida.pdf]"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

import websocket

SAIDA = os.environ.get("QUADRA_SAIDA", "E:/campeonato-nasa/tmp/fluxo2/C4")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ANTONIO = "hoje=milho:34,feijao:33,mandioca:33&maniva=plantada&ha=0.4&larg=40&comp=100&terra=barro&baixio=pouco&plano=ideal&prioridade=garantir"
hash_ = sys.argv[1] if len(sys.argv) > 1 else f"#/2311306/5?{ANTONIO}"
arq = sys.argv[2] if len(sys.argv) > 2 else f"{SAIDA}/relatorio_antonio.pdf"
URL = f"http://127.0.0.1:8090/roca.html{hash_}"


def paginas(b):
    return len(re.findall(rb"/Type\s*/Page[^s]", b))


def por_cdp(modo):
    porta = 9500 + os.getpid() % 150
    perfil = f"{SAIDA}/perfis/pdf-{os.getpid()}"
    edge = subprocess.Popen([EDGE, modo, "--disable-gpu", f"--remote-debugging-port={porta}", f"--user-data-dir={perfil}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                pag = next(a for a in json.load(urllib.request.urlopen(f"http://127.0.0.1:{porta}/json")) if a["type"] == "page")
                break
            except Exception:
                time.sleep(0.3)
        ws = websocket.create_connection(pag["webSocketDebuggerUrl"], timeout=180)
        n = [0]

        def cmd(metodo, **p):
            n[0] += 1
            ws.send(json.dumps({"id": n[0], "method": metodo, "params": p}))
            while True:
                m = json.loads(ws.recv())
                if m.get("id") == n[0]:
                    if "error" in m:
                        raise RuntimeError(m["error"].get("message"))
                    return m.get("result", {})

        def js(e):
            return cmd("Runtime.evaluate", expression=e, returnByValue=True, awaitPromise=True).get("result", {}).get("value")

        cmd("Page.enable")
        cmd("Emulation.setDeviceMetricsOverride", width=800, height=1100, deviceScaleFactor=1, mobile=False)
        cmd("Page.navigate", url=URL)
        fim = time.time() + 40
        while time.time() < fim and not js("!!document.querySelector('#leve-ao-tecnico') && !document.querySelector('#avancar')?.disabled"):
            time.sleep(0.4)
        time.sleep(1.5)
        js("document.querySelectorAll('#jornada details').forEach((d) => { d.open = true; }); true")
        time.sleep(0.5)
        pdf = cmd("Page.printToPDF", printBackground=True, preferCSSPageSize=True)
        return base64.b64decode(pdf["data"])
    finally:
        edge.terminate()
        try:
            edge.wait(timeout=10)
        except Exception:
            pass
        shutil.rmtree(perfil, ignore_errors=True)


dados = None
for modo in ("--headless=old", "--headless"):
    try:
        dados = por_cdp(modo)
        print("ok com", modo)
        break
    except Exception as e:
        print(modo, "falhou:", e)
if dados is None:
    perfil = f"{SAIDA}/perfis/pdfcli-{os.getpid()}"
    subprocess.run([EDGE, "--headless", "--disable-gpu", f"--user-data-dir={perfil}", "--no-pdf-header-footer", "--virtual-time-budget=20000",
                    f"--print-to-pdf={arq}", URL], timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.rmtree(perfil, ignore_errors=True)
    dados = open(arq, "rb").read() if os.path.exists(arq) else None
    print("linha de comando:", "ok" if dados else "falhou")
if dados:
    open(arq, "wb").write(dados)
    print(f"PDF {arq}: {len(dados)} bytes, {paginas(dados)} páginas")
