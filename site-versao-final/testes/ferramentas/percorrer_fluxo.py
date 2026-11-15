"""Percorre a jornada nova num Edge sem janela e salva um print e o texto de cada tela (fluxo: analise/fluxo/00_FLUXO_FINAL.md).
Uso: MSYS_NO_PATHCONV=1 python -I -X utf8 percorrer_fluxo.py pasta_saida [largura] [cod] [nome_no_globo]

1. Do globo ao plano (critério 2): index.html?lugar=<nome> → toque em "Montar o plano do meu roçado" (#planoBotao) → toque no verde
   (#avancar) de Sua roça → tem que dar #/<cod>/3, com 2 toques. Se o globo não abrir no Edge sem janela, usa o painel (painel.html).
2. Percurso padrão: #/<cod>/2 → verde → 3 → verde → 4 → verde → 5 (o verde chama o WhatsApp: só confere o rótulo) → #/<cod>/1.
3. Seu Antônio (critério 3): em Sua roça, mandioca + 3 ha + Encharca + Pequeno + "Ver o meu plano" → o hash tem só
   hoje=milho:34,feijao:33,mandioca:33, maniva=plantada, ha=3, terra=barro e baixio=pouco."""
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import websocket

saida = sys.argv[1]
larg = int(sys.argv[2]) if len(sys.argv) > 2 else 390
cod = sys.argv[3] if len(sys.argv) > 3 else "2311306"
nome_globo = sys.argv[4] if len(sys.argv) > 4 else "Quixadá"
BASE = "http://127.0.0.1:8090"
ALT = 844
os.makedirs(saida, exist_ok=True)
porta = 9300 + os.getpid() % 90
perfil = os.path.join(os.environ.get("QUADRA_PERFIS", "E:/campeonato-nasa/tmp/edge_perfis"), f"quadra-fluxo-{os.getpid()}")
edge = subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                         f"--remote-debugging-port={porta}", f"--user-data-dir={perfil}", "about:blank"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
PRONTO = "!!document.querySelector('#jornada .passo-conteudo') && !document.querySelector('#avancar')?.disabled"
falhas = []
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

    def js(expr):
        return cmd("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True, userGesture=True).get("result", {}).get("value")

    def esperar(expr, teto=20):
        fim = time.time() + teto
        while time.time() < fim:
            if js(expr) is True:
                return True
            time.sleep(0.3)
        return False

    def tocar(sel, espera=2.5):
        ok = js(f"(() => {{ const b = document.querySelector({json.dumps(sel)}); if (!b) return false; b.click(); return true; }})()")
        if not ok:
            falhas.append(f"não achei {sel}")
        time.sleep(espera)
        esperar(PRONTO, 15)
        time.sleep(1)
        return ok

    def hash_():
        return urllib.parse.unquote(js("location.hash") or "")

    num = [0]

    def foto(nome, inteira=True):
        num[0] += 1
        base = os.path.join(saida, f"{num[0]:02d}_{nome}")
        alt = js("document.documentElement.scrollHeight") or ALT
        palavras = js("(() => { const j = document.getElementById('jornada'); return j ? j.innerText.trim().split(/\\s+/).length : 0; })()")
        if inteira:
            cmd("Emulation.setDeviceMetricsOverride", width=larg, height=min(int(alt), 9000), deviceScaleFactor=1, mobile=larg < 600)
            time.sleep(0.8)
        img = cmd("Page.captureScreenshot", format="png", captureBeyondViewport=inteira)
        open(base + ".png", "wb").write(base64.b64decode(img["data"]))
        texto = js("(document.getElementById('jornada')||document.body).innerText") or ""
        open(base + ".txt", "w", encoding="utf-8").write(f"{js('location.href')}\naltura {alt}px · {palavras} palavras\n\n{texto}")
        cmd("Emulation.setDeviceMetricsOverride", width=larg, height=ALT, deviceScaleFactor=1, mobile=larg < 600)
        time.sleep(0.4)
        print(f"ok {base}  altura {alt}  palavras {palavras}", flush=True)

    cmd("Emulation.setDeviceMetricsOverride", width=larg, height=ALT, deviceScaleFactor=1, mobile=larg < 600)
    cmd("Emulation.setTouchEmulationEnabled", enabled=larg < 600)
    cmd("Page.enable")

    # 1. do globo ao plano: 2 toques
    toques = 0
    cmd("Page.navigate", url=f"{BASE}/index.html?lugar={urllib.parse.quote(nome_globo)}")
    # o verde do cartão (#planoBotao) aparece na chegada e cede o lugar ao do painel do iframe (#plano) quando ele desenha
    VERDE = """(() => { const b = document.getElementById('planoBotao');
      if (b && !b.hidden && getComputedStyle(b).display !== 'none') return b;
      const f = document.querySelector('#painel iframe, iframe[src*="painel.html"]');
      const p = f?.contentDocument?.getElementById('plano'); return p && p.offsetWidth ? p : null; })()"""
    globo = esperar(f"(() => {{ const b = {VERDE}; return !!b && /#\\/\\d{{7}}\\/2$/.test(b.href); }})()", 60)
    if globo:
        time.sleep(7)  # o mergulho termina e o painel aparece
        foto("globo_painel", inteira=False)
        print("toque 1:", js(f"(() => {{ const b = {VERDE}; b.click(); return b.id + ' ' + b.getAttribute('href'); }})()"))
    else:  # sem WebGL no Edge sem janela: o painel do globo, sozinho
        print("(o globo não abriu aqui: uso painel.html)")
        cmd("Page.navigate", url=f"{BASE}/painel.html?cod={cod}")
        esperar("(() => { const b = document.getElementById('plano'); return !!b && /#\\/\\d{7}\\/2$/.test(b.href); })()", 30)
        time.sleep(1.5)
        foto("painel", inteira=False)
        js("document.getElementById('plano').target = ''; document.getElementById('plano').click()")
    toques += 1
    time.sleep(2)
    esperar(PRONTO, 25)
    time.sleep(1.5)
    chegou = hash_()
    tocar("#avancar")
    toques += 1
    print(f"critério 2: {toques} toques → {chegou} → {hash_()}", "ok" if chegou.endswith(f"/{cod}/2") and hash_() == f"#/{cod}/3" else "FALHA")
    if hash_() != f"#/{cod}/3":
        falhas.append(f"critério 2: {hash_()}")

    # 2. percurso padrão, um print por tela
    cmd("Page.navigate", url="about:blank")
    time.sleep(0.3)
    cmd("Page.navigate", url=f"{BASE}/roca.html#/{cod}/2")
    esperar(PRONTO, 25)
    time.sleep(2)
    foto("sua_roca")
    for nome, quero in (("plano", 3), ("dinheiro", 4), ("se_secar", 5)):
        tocar("#avancar", 3)
        if hash_() != f"#/{cod}/{quero}":
            falhas.append(f"percurso: esperava #/{cod}/{quero}, deu {hash_()}")
        foto(nome)
    rot = js("document.getElementById('avancar').innerText")
    if rot != "Mandar no WhatsApp":
        falhas.append(f"passo 5: o verde diz '{rot}'")
    tocar('[data-ir="1"]', 3)
    foto("do_espaco")

    # 3. Seu Antônio
    cmd("Page.navigate", url="about:blank")
    time.sleep(0.3)
    cmd("Page.navigate", url=f"{BASE}/roca.html#/{cod}/2")
    esperar(PRONTO, 25)
    time.sleep(2)
    for sel in ('[data-c="mandioca"]', '[data-ha="3"]', '[data-terra="barro"]', '[data-baixio="pouco"]'):
        js(f"document.querySelector({json.dumps(sel)})?.click()")
        time.sleep(0.4)
    if js("location.hash") != f"#/{cod}/2":
        falhas.append("Seu Antônio: o toque mudou a URL antes do verde")
    foto("seu_antonio_marcado")
    tocar("#avancar", 4)
    h = hash_()
    caminho, _, busca = h.partition("?")
    resp = dict(urllib.parse.parse_qsl(busca))
    quero = {"hoje": "milho:34,feijao:33,mandioca:33", "maniva": "plantada", "ha": "3", "terra": "barro", "baixio": "pouco"}
    ok3 = caminho == f"#/{cod}/3" and resp == quero
    print("critério 3:", h, "ok" if ok3 else f"FALHA (esperava {quero})")
    if not ok3:
        falhas.append(f"critério 3: {h}")
    foto("seu_antonio_plano")
    print("FALHAS:", falhas if falhas else "nenhuma")
finally:
    edge.terminate()
    try:
        edge.wait(timeout=10)
    except Exception:
        pass
    shutil.rmtree(perfil, ignore_errors=True)  # o perfil do Edge (~65 MB) não fica para trás
