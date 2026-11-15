"""Percorre a jornada da rodada 2 num Edge sem janela e salva um print e o texto de cada tela (analise/fluxo2/00_FLUXO_V2.md).
Uso: MSYS_NO_PATHCONV=1 python -I -X utf8 percorrer_fluxo.py pasta_saida [largura] [cod] [nome_no_globo]
Cada verificação imprime uma linha "<rótulo>: … ok" (ou FALHA), que o aceite_fluxo.py (parte 4) lê:

1. globo → plano (2 toques): index.html?lugar=<nome> → "Montar o plano do meu roçado" (#planoBotao, ou o #plano do painel no iframe)
   → o verde de Sua roça (#avancar) → #/<cod>/3. Se o globo não abrir no Edge sem janela (sem WebGL), usa o painel (painel.html).
2. percurso 2 → 3 → 4 → 5: #/<cod>/2 → verde → 3 → verde → 4 → verde → 5 (o verde do Relatório é "Mandar no WhatsApp": só o rótulo).
3. Seu Antônio: em Sua roça, mandioca + 3 ha + Encharca + Pequeno + "Ver o meu plano" → o hash tem só hoje=milho:34,feijao:33,
   mandioca:33, maniva=plantada, ha=3, terra=barro e baixio=pouco.
4. 40 × 100 m: largura 40 e comprimento 100 em metros (evento input) + verde → ha=0.4&area_un=medida:100x40&larg=40&comp=100; o
   desenho do Plano diz "40 × 100 m" e "Seu terreno em metros" diz "40 m de largura × 100 m de comprimento"; o Relatório também.
5. ideal + água: no Plano, "O ideal" e "Água" → plano=ideal&prioridade=garantir; Quanto rende marca o ideal como escolhido e o
   Relatório diz "O ideal" e "Guardar água"."""
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
BASE = os.environ.get("QUADRA_BASE", "http://127.0.0.1:8090")
ALT = 844
os.makedirs(saida, exist_ok=True)
porta = 9300 + os.getpid() % 90
perfil = os.path.join(os.environ.get("QUADRA_PERFIS", "E:/campeonato-nasa/tmp/edge_perfis"), f"quadra-fluxo-{os.getpid()}")
edge = subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                         f"--remote-debugging-port={porta}", f"--user-data-dir={perfil}", "about:blank"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
PRONTO = "!!document.querySelector('#jornada .passo-conteudo') && !document.querySelector('#avancar')?.disabled"
falhas = []


def linha(rotulo, ok, det):
    print(f"{rotulo}: {det} {'ok' if ok else 'FALHA'}", flush=True)
    if not ok:
        falhas.append(f"{rotulo}: {det}")


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

    def abrir(h):
        cmd("Page.navigate", url="about:blank")
        time.sleep(0.3)
        cmd("Page.navigate", url=f"{BASE}/roca.html{h}")
        esperar(PRONTO, 25)
        time.sleep(2)

    def hash_():
        return urllib.parse.unquote(js("location.hash") or "")

    def resp():
        caminho, _, busca = hash_().partition("?")
        return caminho, dict(urllib.parse.parse_qsl(busca))

    texto = lambda: js("(document.getElementById('jornada')||document.body).innerText") or ""
    num = [0]

    def foto(nome, inteira=True):
        num[0] += 1
        base = os.path.join(saida, f"{num[0]:02d}_{nome}")
        alt = js("document.documentElement.scrollHeight") or ALT
        palavras = js("(() => { const j = document.getElementById('jornada'); return j ? j.innerText.trim().split(/\\s+/).length : 0; })()")
        if inteira:
            cmd("Emulation.setDeviceMetricsOverride", width=larg, height=min(int(alt), 12000), deviceScaleFactor=1, mobile=larg < 600)
            time.sleep(0.8)
        img = cmd("Page.captureScreenshot", format="png", captureBeyondViewport=inteira)
        open(base + ".png", "wb").write(base64.b64decode(img["data"]))
        open(base + ".txt", "w", encoding="utf-8").write(f"{js('location.href')}\naltura {alt}px · {palavras} palavras\n\n{texto()}")
        cmd("Emulation.setDeviceMetricsOverride", width=larg, height=ALT, deviceScaleFactor=1, mobile=larg < 600)
        time.sleep(0.4)
        print(f"   print {base}.png  altura {alt}  palavras {palavras}", flush=True)

    cmd("Emulation.setDeviceMetricsOverride", width=larg, height=ALT, deviceScaleFactor=1, mobile=larg < 600)
    cmd("Emulation.setTouchEmulationEnabled", enabled=larg < 600)
    cmd("Page.enable")
    # o site abre em inglês por padrão (js/i18n.js): o percurso roda em português; ?lang=en na URL abre em inglês
    cmd("Page.addScriptToEvaluateOnNewDocument", source="try { if (!/[?&]lang=/.test(location.search + location.hash)) localStorage.setItem('quadra-lingua', 'pt'); } catch (_) {}")

    # 1. do globo ao plano: 2 toques
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
        via = js(f"(() => {{ const b = {VERDE}; b.click(); return b.id; }})()")
    else:  # sem WebGL no Edge sem janela: o painel do globo, sozinho
        cmd("Page.navigate", url=f"{BASE}/painel.html?cod={cod}")
        esperar("(() => { const b = document.getElementById('plano'); return !!b && /#\\/\\d{7}\\/2$/.test(b.href); })()", 30)
        time.sleep(1.5)
        foto("painel", inteira=False)
        js("document.getElementById('plano').target = ''; document.getElementById('plano').click()")
        via = "painel.html (sem WebGL)"
    time.sleep(2)
    esperar(PRONTO, 25)
    time.sleep(1.5)
    chegou = hash_()
    tocar("#avancar")
    linha("globo → plano", chegou.endswith(f"/{cod}/2") and hash_() == f"#/{cod}/3", f"2 toques ({via}) → {chegou} → {hash_()}")

    # 2. percurso padrão, um print por tela
    abrir(f"#/{cod}/2")
    foto("sua_roca")
    pilha = [hash_()]
    for nome in ("plano", "dinheiro", "relatorio"):
        tocar("#avancar", 3)
        pilha.append(hash_())
        foto(nome)
    rot = js("document.getElementById('avancar').innerText")
    linha("percurso 2 → 3 → 4 → 5", pilha == [f"#/{cod}/{p}" for p in (2, 3, 4, 5)] and rot == "Mandar no WhatsApp", f"{' → '.join(pilha)} | verde '{rot}'")

    # 3. Seu Antônio
    abrir(f"#/{cod}/2")
    for sel in ('[data-c="mandioca"]', '[data-ha="3"]', '[data-terra="barro"]', '[data-baixio="pouco"]'):
        js(f"document.querySelector({json.dumps(sel)})?.click()")
        time.sleep(0.4)
    parado = js("location.hash") == f"#/{cod}/2"
    foto("seu_antonio_marcado")
    tocar("#avancar", 4)
    caminho, r = resp()
    quero = {"hoje": "milho:34,feijao:33,mandioca:33", "maniva": "plantada", "ha": "3", "terra": "barro", "baixio": "pouco"}
    linha("Seu Antônio", parado and caminho == f"#/{cod}/3" and r == quero, f"{hash_()}{'' if parado else ' (a URL mudou antes do verde)'}")
    foto("seu_antonio_plano")

    # 4. 40 × 100 m: os metros em Sua roça chegam ao desenho do Plano, ao terreno e ao Relatório
    abrir(f"#/{cod}/2")
    for lado, v in (("larg", 40), ("comp", 100)):
        js(f"(() => {{ const i = document.querySelector('[data-lado=\"{lado}\"]'); i.focus(); i.value = '{v}'; i.dispatchEvent(new Event('input', {{ bubbles: true }})); }})()")
        time.sleep(0.5)
    conv = js("document.querySelector('.sr-m-conv')?.innerText || ''") or ""
    foto("metros_40x100")
    tocar("#avancar", 4)
    caminho, r = resp()
    quero4 = {"ha": "0.4", "area_un": "medida:100x40", "larg": "40", "comp": "100"}
    des = js("document.querySelector('.rocado-svg')?.textContent || ''") or ""
    js("(() => { const d = [...document.querySelectorAll('#jornada details')].find((x) => /Seu terreno/.test(x.querySelector('summary')?.textContent || '')); if (d) { d.open = true; d.dispatchEvent(new Event('toggle')); } })()")
    time.sleep(3)
    ter = js("(() => { const d = [...document.querySelectorAll('#jornada details')].find((x) => /Seu terreno/.test(x.querySelector('summary')?.textContent || '')); return d ? d.innerText : ''; })()") or ""
    foto("metros_plano")
    tocar("#avancar", 3)
    tocar("#avancar", 3)
    fic = js("document.querySelector('.rl-ficha')?.innerText || ''") or ""
    ok4 = (caminho == f"#/{cod}/3" and r == quero4 and "0,4 ha" in conv and "40 × 100 m" in des and "40 m de largura × 100 m de comprimento" in " ".join(ter.split())
           and "40 × 100 m" in fic)
    linha("40 × 100 m", ok4, f"{caminho}?{urllib.parse.urlencode(r)} | conversão '{' '.join(conv.split())}' | desenho {'40 × 100 m' in des} | "
          f"terreno {'40 m de largura' in ter} | relatório {'40 × 100 m' in fic}")
    foto("metros_relatorio")

    # 5. o ideal com Água: Plano → Quanto rende → Relatório seguem a escolha
    abrir(f"#/{cod}/3?hoje=milho:50,feijao:50")
    tocar('[data-lado="ideal"]', 3)
    tocar('[data-prio="agua"]', 3)
    caminho, r = resp()
    foto("ideal_agua_plano")
    tocar("#avancar", 3)
    col = js("document.querySelector('#jornada .hi-tab-col.sel')?.className || ''") or ""
    foto("ideal_agua_dinheiro")
    tocar("#avancar", 3)
    fic = " ".join((js("document.querySelector('.rl-ficha')?.innerText || ''") or "").split())
    foto("ideal_agua_relatorio")
    linha("ideal + água", r.get("plano") == "ideal" and r.get("prioridade") == "garantir" and "ideal" in col and "O ideal" in fic and "Guardar água" in fic,
          f"{caminho}?{urllib.parse.urlencode(r)} | Dinheiro '{col}' | Relatório '{fic[:100]}'")
    print("FALHAS:", falhas if falhas else "nenhuma")
finally:
    edge.terminate()
    try:
        edge.wait(timeout=10)
    except Exception:
        pass
    shutil.rmtree(perfil, ignore_errors=True)  # o perfil do Edge (~65 MB) não fica para trás
