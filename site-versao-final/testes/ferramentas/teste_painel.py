"""B3 (rodada 2): abre o painel (painel.html) no Edge sem janela, passa por cada aba, mede e tira print.
Uso: python -I -X utf8 teste_painel.py <url> <largura> <prefixo> [abas separadas por vírgula] [--aberto]
Mede por aba: altura da página, rolagem horizontal (scrollWidth > clientWidth), palavras à vista em main.conteudo,
selos e erros de console/exceções. Com --aberto, abre todos os <details> e mede de novo (e tira outro print)."""
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

import websocket

url, larg, prefixo = sys.argv[1], int(sys.argv[2]), sys.argv[3]
abas = sys.argv[4].split(",") if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else ["inverno", "plantar", "clima", "chuva", "dados"]
aberto = "--aberto" in sys.argv
porta = 9100 + os.getpid() % 150
perfil = os.path.join(os.environ.get("QUADRA_PERFIS", "E:/campeonato-nasa/tmp/edge_perfis"), f"quadra-painel-{os.getpid()}")
edge = subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                         f"--remote-debugging-port={porta}", f"--user-data-dir={perfil}", "about:blank"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
erros = []
try:
    for _ in range(60):
        try:
            pag = next(a for a in json.load(urllib.request.urlopen(f"http://127.0.0.1:{porta}/json")) if a["type"] == "page")
            break
        except Exception:
            time.sleep(0.3)
    ws = websocket.create_connection(pag["webSocketDebuggerUrl"], timeout=120)
    n = [0]

    def ouvir(ev):
        met = ev.get("method")
        if met == "Runtime.exceptionThrown":
            d = ev["params"]["exceptionDetails"]
            erros.append(f"EXCEÇÃO {d.get('text')} {(d.get('exception') or {}).get('description', '')[:300]} {d.get('url', '')}:{d.get('lineNumber')}")
        elif met == "Runtime.consoleAPICalled" and ev["params"]["type"] in ("error", "warning"):
            erros.append("CONSOLE " + " ".join(str(a.get("value", a.get("description", ""))) for a in ev["params"]["args"])[:300])
        elif met == "Log.entryAdded" and ev["params"]["entry"]["level"] in ("error", "warning"):
            e = ev["params"]["entry"]
            erros.append(f"LOG {e.get('text', '')[:200]} {e.get('url', '')}")

    def cmd(metodo, **p):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "method": metodo, "params": p}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == n[0]:
                return m.get("result", {})
            ouvir(m)

    def js(expr):
        r = cmd("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            return {"erro": r["exceptionDetails"].get("text")}
        return r.get("result", {}).get("value")

    def esperar(s):
        fim = time.time() + s
        while time.time() < fim:
            js("1")
            time.sleep(0.25)

    for m in ("Runtime.enable", "Log.enable", "Page.enable"):
        cmd(m)
    # o site abre em inglês por padrão (js/i18n.js): o teste roda em português; ?lang=en na URL abre em inglês
    cmd("Page.addScriptToEvaluateOnNewDocument", source="try { if (!/[?&]lang=/.test(location.search + location.hash)) localStorage.setItem('quadra-lingua', 'pt'); } catch (_) {}")
    cmd("Emulation.setDeviceMetricsOverride", width=larg, height=900, deviceScaleFactor=1, mobile=larg < 600)
    cmd("Page.navigate", url=url)
    esperar(5)
    MEDIR = """(() => {
      const de = document.documentElement, c = document.querySelector('main.conteudo');
      const vis = (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
      const largos = [...document.querySelectorAll('main *')].filter((e) => vis(e) && e.getBoundingClientRect().right > de.clientWidth + 1
        && !e.closest('.tend-grade, table, .cc-graf, .hz-mapa, .abas')).slice(0, 5).map((e) => e.className && e.className.baseVal === undefined ? e.className : e.tagName);
      return { altura: de.scrollHeight, rolagem_h: de.scrollWidth - de.clientWidth, palavras: (c.innerText.match(/\\S+/g) || []).length,
        selos: c.querySelectorAll('.selo').length, faixa: document.querySelector('#faixa h1')?.textContent,
        extras: [...document.querySelectorAll('#extras [data-extra]')].map((d) => d.dataset.extra + (d.childElementCount ? '' : '(vazio)')),
        largos };
    })()"""
    for aba in abas:
        js(f"document.querySelector('#abas [data-aba=\"{aba}\"]').click()")
        for _ in range(60):  # a aba da API: espera a faixa sair de "Buscando…"
            if not js("/Buscando/.test(document.querySelector('#faixa').textContent)"):
                break
            esperar(0.5)
        esperar(4)
        med = js(MEDIR)
        print(aba, json.dumps(med, ensure_ascii=False))
        alt = min(int(med["altura"]), 8000)
        cmd("Emulation.setDeviceMetricsOverride", width=larg, height=alt, deviceScaleFactor=1, mobile=larg < 600)
        esperar(1)
        img = cmd("Page.captureScreenshot", format="png", captureBeyondViewport=True)
        open(f"{prefixo}_{aba}.png", "wb").write(base64.b64decode(img["data"]))
        cmd("Emulation.setDeviceMetricsOverride", width=larg, height=900, deviceScaleFactor=1, mobile=larg < 600)
        if aberto:
            js("document.querySelectorAll('main details').forEach((d) => { d.open = true; d.dispatchEvent(new Event('toggle')); })")
            esperar(5)
            js("document.querySelectorAll('main details').forEach((d) => { d.open = true; })")
            esperar(2)
            med = js(MEDIR)
            print(aba, "ABERTO", json.dumps(med, ensure_ascii=False))
            alt = min(int(med["altura"]), 12000)
            cmd("Emulation.setDeviceMetricsOverride", width=larg, height=alt, deviceScaleFactor=1, mobile=larg < 600)
            esperar(1)
            img = cmd("Page.captureScreenshot", format="png", captureBeyondViewport=True)
            open(f"{prefixo}_{aba}_aberto.png", "wb").write(base64.b64decode(img["data"]))
            cmd("Emulation.setDeviceMetricsOverride", width=larg, height=900, deviceScaleFactor=1, mobile=larg < 600)
    print("ERROS:", len(erros))
    for e in erros:
        print(" ", e)
finally:
    edge.terminate()
    try:
        edge.wait(timeout=10)
    except Exception:
        pass
    shutil.rmtree(perfil, ignore_errors=True)
