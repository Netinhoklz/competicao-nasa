"""Aceite da jornada da rodada 2 (analise/fluxo2/00_FLUXO_V2.md, seção 6), no Edge sem janela a 390x844.
Uso: MSYS_NO_PATHCONV=1 python -I -X utf8 aceite_fluxo.py [cod,cod,...] [--so-node | --so-telas | --so-toques | --so-painel | --so-fim]
     [--sem-node] [--sem-fim] [--prints]
(--prints: um print inteiro de cada tela em $QUADRA_PRINTS/<cod>/<passo>_<tela>.png; padrão E:/campeonato-nasa/tmp/fluxo2/final)

Parte 0 (node): teste_calculo.mjs com o calculo.js de agora e o do HEAD (diff vazio), teste_ideal.mjs, teste_dinheiro.mjs e
  teste_relatorio.mjs (sai 1 se uma data do relatório não existir na agenda).
Parte 1 (telas): Sua roça (2), O plano (3, os 2 lados), Quanto rende (4) e Relatório (5) em cada município: tetos de altura e
  palavras (D2, D3, D5), um verde, "seu olho" <= 2, frases banidas (à vista e nos "ver mais"), nada de lado (também com tudo aberto),
  selo >= 11 px, "ver mais" >= 44 px, zero erro no console, e o que cada tela precisa ter.
Parte 2 (toques, Quixadá; Piritiba no aviso da terra): critérios C1 a C13 (seção 6 do 00_FLUXO_V2.md).
Parte 3 (painel): o conteúdo do antigo "Do espaço" nas abas do painel.html e os números do cartão do mapa (camadas.numerosChave).
Parte 4 (fim, cada um com o seu Edge, depois de fechar o do aceite): percorrer_fluxo.py (do globo ao plano em 2 toques, Seu Antônio,
  40 x 100 m até o desenho, o ideal com Água) e o PDF do Relatório (A4, <= 4 páginas) pela linha de comando do Edge.
Roda tudo em série, um Edge por vez: com testes em paralelo o servidor recusa pedidos (ERR_CONNECTION_REFUSED)."""
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(AQUI))  # site-versao-final/
BASE = os.environ.get("QUADRA_BASE", "http://127.0.0.1:8090")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PY = sys.executable
MUNS = {"2311306": "Quixadá", "2304103": "Crateús", "2208007": "Picos", "2402006": "Caicó", "2611101": "Petrolina",
        "2700300": "Arapiraca", "2903201": "Barreiras"}
# as telas: (passo, sufixo do hash, nome); o Plano é medido nos 2 lados
TELAS = [(2, "", "Sua roça"), (3, "", "Plano"), (3, "?plano=ideal", "Plano ideal"), (4, "", "Dinheiro"), (5, "", "Relatório")]
TETO = {2: (1800, 190), 3: (3600, 430), 4: (2600, 300), 5: (None, None)}  # altura, palavras à vista (D2, D3, D5; D7 sem teto)
BANIDAS = ["5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde", "qualquer terra", "sem preço aqui",
           "ainda não vende", "à frente de hoje em"]
PRINTS = os.environ.get("QUADRA_PRINTS", "E:/campeonato-nasa/tmp/fluxo2/final")
ANTONIO = "hoje=milho:34,feijao:33,mandioca:33&maniva=plantada&ha=0.4&larg=40&comp=100&terra=barro&baixio=pouco"

SECAO8 = r"""(() => {
  const j = document.getElementById("jornada");
  const vis = (e) => (e.offsetWidth || e.offsetHeight) && !e.closest("details:not([open])");
  const txt = j.innerText, tudo = j.textContent;
  const ban = %s;
  // as palavras à vista contam o texto corrido, não os rótulos dos desenhos (SVG): o José pediu (15/11) toda faixa do roçado com
  // parte + cultura ("A · feijão"), o que soma dezenas de rótulos ao Plano sem ser texto para ler
  const visSvg = (s) => { const b = s.getBoundingClientRect(); return (b.width || b.height) && !s.closest("details:not([open])"); }; // SVG não tem offsetWidth
  const nSvg = [...j.querySelectorAll("svg")].filter(visSvg).reduce((n, s) => n + ((s.textContent || "").trim() ? s.textContent.trim().split(/\s+/).length : 0), 0);
  return {
    hash: location.hash,
    altura: document.documentElement.scrollHeight,
    palavras: txt.trim().split(/\s+/).length - nSvg,
    primarios: [...document.querySelectorAll(".botao.primario")].filter(vis).length,
    contadores: document.querySelectorAll(".quiz-barra,.hi-barra,.hs-barra").length,
    nDeM: /\b\d+ de \d+\b/i.test(document.querySelector(".kicker")?.innerText || ""),
    lateral: document.documentElement.scrollWidth > innerWidth,
    olhos: [...j.querySelectorAll(".olho")].filter(vis).length,
    proibidas: ban.filter((f) => tudo.includes(f)),
    selosPequenos: [...document.querySelectorAll(".selo")].filter((s) => vis(s) && parseFloat(getComputedStyle(s).fontSize) < 11).length,
    summaryBaixo: [...document.querySelectorAll("summary")].filter((s) => vis(s) && s.getBoundingClientRect().height < 44).length,
  };
})()""" % json.dumps(BANIDAS, ensure_ascii=False)
EXTRA = r"""(() => {
  const vis = (e) => { const b = e.getBoundingClientRect(); return (b.width || b.height) && !e.closest("details:not([open])"); }; // vale para SVG
  const topo = (s) => { const e = [...document.querySelectorAll(s)].find(vis); return e ? Math.round(e.getBoundingClientRect().top + scrollY) : null; };
  const graf = topo(".hi-graf");
  const J = document.getElementById("jornada");
  return {
    erroPasso: !!document.querySelector("#jornada .erro"),
    kicker: document.querySelector(".kicker")?.innerText || "",
    linhas: ["hoje", "ha", "terra", "baixio", "maniva", "antes"].filter((k) => document.getElementById("linha-" + k)),
    todas: /Ver todas as culturas \(\d+\)/.test(J.innerText),
    metros: !!document.querySelector('[data-lado="larg"]') && !!document.querySelector('[data-lado="comp"]'),
    perfilBaixio: !!document.querySelector("#linha-baixio svg") && /mais baixa do roçado/.test(document.getElementById("linha-baixio")?.innerText || ""),
    selosNasa: [...document.querySelectorAll("#jornada .selo")].filter(vis).map((s) => s.innerText).filter((t) => /MEDIDO · NASA/.test(t)).length,
    agoraTopo: topo(".plantio-agora"), desenhoTopo: topo(".rocado-svg"),
    lados: document.querySelectorAll("#jornada .lados [data-lado]").length,
    ladoAceso: document.querySelector('#jornada .lados [aria-pressed="true"]')?.dataset.lado || "",
    prios: document.querySelectorAll("#jornada [data-prio]").length,
    soltos: document.querySelectorAll("#jornada [data-maniva], #jornada .hs-se").length, // maniva e cartão do giro saíram do Plano
    ganha: !!document.querySelector("#jornada .gn-tab"),
    grafTopo: graf,
    controlesAntes: graf === null ? null : [...document.querySelectorAll("#jornada .seg, #jornada [data-set]")]
      .filter((e) => vis(e) && e.getBoundingClientRect().top + scrollY < graf).length,
    hiTab: !!document.querySelector("#jornada .hi-tab"),
    tarefas: document.querySelectorAll(".passo-relatorio .rl-tarefa").length,
    datasRel: (J.innerText.match(/\b\d{2}\/\d{2}\/\d{4}\b/g) || []).length,
    tecnico: !!document.querySelector('#jornada [data-extra="leve_ao_tecnico"]'),
    topoFixo: Math.round(document.querySelector(".topo")?.getBoundingClientRect().height || 0),
    barra: Math.round(document.querySelector(".nav-baixo")?.getBoundingClientRect().height || 0),
    avancar: document.getElementById("avancar")?.innerText || "",
  };
})()"""
PRONTO = r"""(() => { const j = document.getElementById("jornada");
  return !!(j && j.querySelector(".passo-conteudo") && ![...j.querySelectorAll("[data-extra]")].some((e) => !e.children.length && e.isConnected && !e.closest("details:not([open])"))); })()"""
LATERAL_ABERTO = r"""new Promise(async (ok) => { for (let i = 0; i < 3; i++) { document.querySelectorAll("details").forEach((d) => (d.open = true));
  await new Promise((r) => setTimeout(r, 1200)); }
  ok({ sw: document.documentElement.scrollWidth, iw: innerWidth,
    fora: [...document.querySelectorAll("#jornada *")].filter((e) => e.getBoundingClientRect().right > innerWidth + 1 && !e.closest(".rola,.hi-rola,.rola-dentro,.seg-tab-wrap,.seg-cols"))
      .map((e) => e.tagName + "." + String(e.className.baseVal ?? e.className).split(" ")[0]).slice(0, 4) }); })"""
# o plano à vista: o desenho do roçado e os números de "O que você ganha" (Plano) / da tabela de R$ (Quanto rende), por rótulo
ASSINATURA = r"""(() => {
  const rot = (e) => { const c = e.cloneNode(true); c.querySelectorAll(".selo").forEach((s) => s.remove()); return c.textContent.replace(/\s+/g, " ").replace(/ por ano\s*$/, "").trim(); };
  const linhas = (sl, sr, sv) => Object.fromEntries([...document.querySelectorAll(sl)].map((l) => [rot(l.querySelector(sr)), [...l.querySelectorAll(sv)].map((v) => v.textContent.replace(/\s+/g, " ").trim())]));
  return { desenho: document.querySelector(".rocado-svg")?.innerHTML || "", desenhoTxt: document.querySelector(".rocado-svg")?.textContent || "",
    plano: linhas("#jornada .gn-it", ".gn-rot", ".gn-v"), dinheiro: linhas("#jornada .hi-tab-lin", ".hi-tab-rot", ".hi-tab-val"),
    lado: document.querySelector('#jornada .lados [aria-pressed="true"]')?.dataset.lado || "",
    prio: document.querySelector('#jornada [data-prio][aria-pressed="true"]')?.dataset.prio || "",
    colSel: document.querySelector("#jornada .hi-tab-col.sel")?.className || "",
    ficha: document.querySelector("#jornada .rl-ficha")?.innerText || "",
    texto: document.getElementById("jornada")?.innerText || "" };
})()"""
# as datas dd/mm/aaaa do Relatório (todo detalhe aberto) contra a agenda do plano escolhido, refeita dentro da página com o motor
DATAS_RELATORIO = r"""(async () => {
  const I = await import('/js/extras/ideal.js'), R = await import('/js/roca.js');
  const [cam, busca = ''] = decodeURIComponent(location.hash.slice(2)).split('?');
  const q = new URLSearchParams(busca), resp = { ...R.PADRAO };
  for (const [k, v] of q) if (k in resp) resp[k] = v;
  const T = { arenosa: ['1', '12'], mista: ['2', '13'], barro: ['3', '15'] }, p = new URLSearchParams();   // = paramsApi de roca.js
  if (T[resp.terra]) { p.set('textura', T[resp.terra][0]); p.set('ad', T[resp.terra][1]); }
  if (resp.baixio === 'nao') p.set('baixio', '0'); else if (['pouco', 'terco', 'metade'].includes(resp.baixio)) p.set('ad_baixio', '15');
  if (['nao', 'plantada'].includes(resp.maniva)) p.set('maniva', resp.maniva);
  p.set('cod', cam.split('/')[0]);
  const r = await (await fetch('/api/local?' + p)).json();
  const ef = R.efetivas(resp, r), e = I.escolhido(r, resp, ef);
  const br = (s) => s.slice(8, 10) + '/' + s.slice(5, 7) + '/' + s.slice(0, 4);
  const ok = new Set([br(r.agenda.hoje), ...(r.agenda.marcos || []).map((m) => br(m.data))]);
  for (const l of [...e.linhas, ...r.agenda.linhas]) {
    for (const b of l.barras || []) { ok.add(br(b.de)); ok.add(br(b.ate)); for (const x of String(b.rotulo).matchAll(/\d{2}\/\d{2}\/\d{4}/g)) ok.add(x[0]); }
    for (const m of l.marcos || []) ok.add(br(m.data));
    for (const t of [l.plantar, l.colher, l.fonte]) for (const x of String(t || '').matchAll(/\d{2}\/\d{2}\/\d{4}/g)) ok.add(x[0]);
  }
  document.querySelectorAll('#jornada details').forEach((d) => { d.open = true; });
  await new Promise((s) => setTimeout(s, 400));
  const ds = [...document.getElementById('jornada').innerText.matchAll(/\d{2}\/\d{2}\/\d{4}/g)].map((x) => x[0]);
  return { nome: e.nome, datas: ds.length, unicas: new Set(ds).size, fora: [...new Set(ds.filter((x) => !ok.has(x)))] };
})()"""


class Edge:
    def __init__(self, larg=390, alt=844):
        self.larg, self.alt = larg, alt
        porta = 9100 + os.getpid() % 150
        self.perfil = os.path.join(os.environ.get("QUADRA_PERFIS", "E:/campeonato-nasa/tmp/edge_perfis"), f"quadra-aceite-{os.getpid()}")
        self.proc = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--remote-debugging-port={porta}",
                                      f"--user-data-dir={self.perfil}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                pag = next(a for a in json.load(urllib.request.urlopen(f"http://127.0.0.1:{porta}/json")) if a["type"] == "page")
                break
            except Exception:
                time.sleep(0.3)
        self.ws = websocket.create_connection(pag["webSocketDebuggerUrl"], timeout=60)
        self.n, self.erros = 0, []
        for m in ("Runtime.enable", "Log.enable", "Page.enable"):
            self.cmd(m)
        # o site abre em inglês por padrão (js/i18n.js): os testes rodam em português; ?lang=en na URL abre em inglês
        self.cmd("Page.addScriptToEvaluateOnNewDocument", source="try { if (!/[?&]lang=/.test(location.search + location.hash)) localStorage.setItem('quadra-lingua', 'pt'); } catch (_) {}")
        self.cmd("Emulation.setDeviceMetricsOverride", width=larg, height=alt, deviceScaleFactor=1, mobile=larg < 600)
        self.cmd("Emulation.setTouchEmulationEnabled", enabled=larg < 600)

    def evento(self, ev):
        met = ev.get("method")
        if met == "Runtime.exceptionThrown":
            d = ev["params"]["exceptionDetails"]
            self.erros.append("EXCEÇÃO " + ((d.get("exception") or {}).get("description") or d.get("text", ""))[:200])
        elif met == "Runtime.consoleAPICalled" and ev["params"]["type"] in ("error", "warning"):
            self.erros.append(ev["params"]["type"].upper() + " " + " ".join(str(a.get("value", a.get("description", ""))) for a in ev["params"]["args"])[:200])
        elif met == "Log.entryAdded" and ev["params"]["entry"]["level"] in ("error", "warning"):
            e = ev["params"]["entry"]
            self.erros.append("LOG " + e.get("text", "")[:160] + " " + e.get("url", "").replace(BASE, ""))

    def cmd(self, metodo, **p):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": metodo, "params": p}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n:
                return m.get("result", {})
            self.evento(m)

    def dormir(self, s):
        fim = time.time() + s
        self.ws.settimeout(0.2)
        while time.time() < fim:
            try:
                self.evento(json.loads(self.ws.recv()))
            except Exception:
                pass
        self.ws.settimeout(60)

    def js(self, expr):
        r = self.cmd("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True, userGesture=True)
        if "exceptionDetails" in r:
            return {"erroJs": (r["exceptionDetails"].get("exception") or {}).get("description", "")[:200]}
        return r.get("result", {}).get("value")

    def esperar(self, expr, teto=15):
        fim = time.time() + teto
        while time.time() < fim:
            if self.js(expr) is True:
                return True
            self.dormir(0.3)
        return False

    def abrir(self, hash_, pagina="roca.html"):
        """Carrega a página do zero (about:blank no meio) e espera o passo e os extras à vista."""
        self.cmd("Page.navigate", url="about:blank")
        self.dormir(0.2)
        self.erros = []
        self.cmd("Page.navigate", url=f"{BASE}/{pagina}{hash_}")
        if not pagina.startswith("roca.html"):
            self.dormir(3)
            return True
        ok = self.esperar(PRONTO, 20)
        self.dormir(1.5)  # fontes, extras e o redesenho do glossário
        return ok

    def depois_de(self, expr, espera=2.0):
        """Roda um toque e espera a tela redesenhar."""
        v = self.js(expr)
        self.dormir(espera)
        self.esperar(PRONTO, 10)
        return v

    def print_inteiro(self, arq):
        alt = int(self.js("document.documentElement.scrollHeight") or self.alt)
        self.cmd("Emulation.setDeviceMetricsOverride", width=self.larg, height=min(alt, 12000), deviceScaleFactor=1, mobile=self.larg < 600)
        self.dormir(0.8)
        img = self.cmd("Page.captureScreenshot", format="png", captureBeyondViewport=True)
        os.makedirs(os.path.dirname(arq), exist_ok=True)
        open(arq, "wb").write(base64.b64decode(img["data"]))
        self.cmd("Emulation.setDeviceMetricsOverride", width=self.larg, height=self.alt, deviceScaleFactor=1, mobile=self.larg < 600)
        self.dormir(0.5)

    def fechar(self):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except Exception:
            pass
        shutil.rmtree(self.perfil, ignore_errors=True)  # o perfil do Edge (~65 MB) não fica para trás


recusou = lambda erros: any("ERR_CONNECTION_REFUSED" in e or "Failed to fetch" in e for e in erros)
clicar = lambda sel: f"(() => {{ const b = document.querySelector({json.dumps(sel)}); if (!b) return 'sem ' + {json.dumps(sel)}; b.click(); return 'ok'; }})()"
numeros = lambda v: [re.sub(r"[^\d−-]", "", x) for x in v]  # "R$ 1.850" → "1850", "−R$ 485" → "−485"


# ------------------------------------------------------------------ parte 0: node
def parte_node():
    print("\n== Parte 0: node ==")
    res = {}
    rodar = lambda args, **kw: subprocess.run(["node", *args], cwd=SITE, capture_output=True, text=True, encoding="utf-8", **kw)
    # teste_calculo.mjs com o calculo.js de agora e com o do HEAD, numa árvore temporária com a mesma forma (diff vazio)
    agora = rodar(["testes/ferramentas/teste_calculo.mjs"])
    tmp = tempfile.mkdtemp(prefix="quadra-calc-")
    try:
        for d in ("web/js/passos/dinheiro", "testes/ferramentas"):
            os.makedirs(os.path.join(tmp, d))
        shutil.copytree(os.path.join(SITE, "testes/exemplos"), os.path.join(tmp, "testes/exemplos"))
        shutil.copy(os.path.join(SITE, "testes/ferramentas/teste_calculo.mjs"), os.path.join(tmp, "testes/ferramentas"))
        head = subprocess.run(["git", "show", "HEAD:./web/js/passos/dinheiro/calculo.js"], cwd=SITE, capture_output=True).stdout
        open(os.path.join(tmp, "web/js/passos/dinheiro/calculo.js"), "wb").write(head)
        base = subprocess.run(["node", "testes/ferramentas/teste_calculo.mjs"], cwd=tmp, capture_output=True, text=True, encoding="utf-8")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    mudou = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "web/js/passos/dinheiro/calculo.js"], cwd=SITE).returncode
    res["N1"] = (agora.returncode == 0 and bool(head) and agora.stdout == base.stdout and not mudou,
                 f"teste_calculo: {len(agora.stdout.splitlines())} linhas, iguais ao HEAD: {agora.stdout == base.stdout}; calculo.js mudou: {bool(mudou)}")
    for k, t, padrao in (("N2", "teste_ideal.mjs", r"Conferências: (\d+) ok, (\d+) falha"), ("N3", "teste_dinheiro.mjs", r"(\d+) conferências, (\d+) falhas"),
                         ("N4", "teste_relatorio.mjs", r"conferências (\d+), falhas (\d+)")):
        p = rodar([f"testes/ferramentas/{t}"])
        m = re.search(padrao, p.stdout)
        res[k] = (p.returncode == 0 and bool(m) and m.group(2) == "0", f"{t}: rc {p.returncode}, " + (f"{m.group(1)} conferências, {m.group(2)} falhas" if m else p.stdout[-200:]))
    for k in sorted(res):
        print(f"{k}: {'ok   ' if res[k][0] else 'FALHA'}  {res[k][1]}", flush=True)
    return {k: {"ok": v[0], "detalhe": v[1]} for k, v in res.items()}


# ------------------------------------------------------------------ parte 1: telas
def medir_tela(ed, cod, passo, suf, nome):
    for tentativa in range(2):
        ok = ed.abrir(f"#/{cod}/{passo}{suf}")
        s8, ex = ed.js(SECAO8), ed.js(EXTRA)
        if ok and not ex.get("erroPasso") and not recusou(ed.erros):
            break
        print(f"  (de novo {cod}/{passo}{suf}: pronto={ok} erros={ed.erros[:2]})", flush=True)
        ed.dormir(3)
    erros = list(ed.erros)
    if "--prints" in sys.argv:
        ed.print_inteiro(f"{PRINTS}/{cod}/{passo}_{nome.replace(' ', '_').lower()}.png")
    lat = ed.js(LATERAL_ABERTO)
    return s8, ex, lat, erros


def falhas_tela(passo, suf, s8, ex, lat, erros):
    f = []
    alt_max, pal_max = TETO[passo]
    if alt_max and s8["altura"] > alt_max:
        f.append(f"altura>{alt_max}")
    if pal_max and s8["palavras"] > pal_max:
        f.append(f"palavras>{pal_max}")
    if s8["primarios"] != 1:
        f.append(f"primarios={s8['primarios']}")
    if s8["contadores"] or s8["nDeM"]:
        f.append("contador")
    if s8["lateral"] or lat["sw"] > lat["iw"]:
        f.append("lateral" + ("(aberto)" if not s8["lateral"] else "") + (f" {lat['fora']}" if lat.get("fora") else ""))
    if s8["olhos"] > 2:
        f.append(f"olhos={s8['olhos']}")
    if s8["proibidas"]:
        f.append("proibidas:" + "/".join(s8["proibidas"]))
    if s8["selosPequenos"]:
        f.append("selo<11px")
    if s8["summaryBaixo"]:
        f.append("summary<44px")
    if ex["erroPasso"]:
        f.append("erro no passo")
    if ex["topoFixo"] > 96 or ex["barra"] > 64:
        f.append(f"topo {ex['topoFixo']} / barra {ex['barra']}")
    if passo == 2:
        if not {"hoje", "ha", "terra", "baixio", "antes"} <= set(ex["linhas"]):
            f.append(f"linhas {ex['linhas']}")
        if not (ex["todas"] and ex["metros"] and ex["perfilBaixio"]):
            f.append(f"todas {ex['todas']} metros {ex['metros']} baixio {ex['perfilBaixio']}")
        if not ex["selosNasa"]:
            f.append("sem 'MEDIDO · NASA' à vista")
    if passo == 3:
        ideal = "plano=ideal" in suf
        if ex["lados"] != 2 or ex["ladoAceso"] != ("ideal" if ideal else "melhor"):
            f.append(f"controle {ex['lados']}/{ex['ladoAceso']}")
        if ideal and ex["prios"] != 4:
            f.append(f"prioridades {ex['prios']}")
        if ex["soltos"]:
            f.append("maniva/giro no meio do Plano")
        if not ex["ganha"]:
            f.append("sem 'O que você ganha'")
        if not ideal and ((ex["agoraTopo"] or 9999) > 400 or (ex["desenhoTopo"] or 9999) > 550):
            f.append(f"Agora {ex['agoraTopo']} desenho {ex['desenhoTopo']}")
    if passo == 4:
        if ex["grafTopo"] is not None and (ex["grafTopo"] > 450 or ex["controlesAntes"]):
            f.append(f"grafico {ex['grafTopo']}/{ex['controlesAntes']}")
        if not ex["hiTab"]:
            f.append("sem tabela Hoje → Melhorado → Ideal")
    if passo == 5:
        # o "Leve para o técnico" saiu do Relatório (pedido do José, 15/11): o bloco não pode aparecer
        if ex["tarefas"] < 1 or ex["datasRel"] < 2 or ex["tecnico"] or ex["avancar"] != "Mandar no WhatsApp":
            f.append(f"relatório: tarefas {ex['tarefas']} datas {ex['datasRel']} bloco do técnico {ex['tecnico']} (deve sumir) verde '{ex['avancar']}'")
    if erros:
        f.append(f"{len(erros)} erro(s) no console")
    return f


def parte_telas(ed, cods):
    print("\n== Parte 1: as telas (390x844, todo 'ver mais' fechado; lateral também com tudo aberto) ==")
    cab = f"{'município':<10} {'tela':<12} {'altura':>6} {'palav':>5} {'prim':>4} {'olho':>4} {'pos':<22} {'erro':>4}  resultado"
    print(cab)
    print("-" * len(cab))
    linhas, total = [], 0
    for cod in cods:
        for passo, suf, nome in TELAS:
            s8, ex, lat, erros = medir_tela(ed, cod, passo, suf, nome)
            f = falhas_tela(passo, suf, s8, ex, lat, erros)
            total += bool(f)
            pos = {2: f"linhas {len(ex['linhas'])} NASA {ex['selosNasa']}", 3: f"agora {ex['agoraTopo']} des {ex['desenhoTopo']}",
                   4: f"gráfico {ex['grafTopo']}", 5: f"tarefas {ex['tarefas']} datas {ex['datasRel']}"}[passo]
            print(f"{MUNS.get(cod, cod):<10} {nome:<12} {s8['altura']:>6} {s8['palavras']:>5} {s8['primarios']:>4} {s8['olhos']:>4} "
                  f"{pos:<22} {len(erros):>4}  {'ok' if not f else 'FALHA: ' + ', '.join(f)}", flush=True)
            for e in erros[:3]:
                print("      ", e)
            linhas.append({"cod": cod, "passo": passo, "suf": suf, **s8, **ex, "lateralAberto": lat, "erros": erros, "falhas": f})
    print(f"\ntelas com falha: {total} de {len(linhas)}")
    return linhas


# ------------------------------------------------------------------ parte 2: toques
def parte_toques(ed):
    print("\n== Parte 2: os toques (Quixadá; Piritiba e Petrolina no C7) ==")
    res = {}
    q = "2311306"
    hash_ = lambda: ed.js("decodeURIComponent(location.hash)")
    texto = lambda: ed.js("document.getElementById('jornada').innerText") or ""
    assin = lambda: ed.js(ASSINATURA) or {}

    # C1: só "Ver o meu plano" deixa o hash sem parâmetros; ficha "(típico)"; passo 4 "(o comum daqui)"
    ed.abrir(f"#/{q}/2")
    ed.depois_de(clicar("#avancar"), 2.5)
    h3, ficha = hash_(), ed.js("document.getElementById('ficha').innerText")
    ed.depois_de(clicar("#avancar"), 3)
    res["C1"] = (h3 == f"#/{q}/3" and "(típico)" in ficha and "(o comum daqui)" in texto(), f"{h3} | ficha '{ficha.strip()}'")

    # C2: os R$ de Quixadá em 3 anos na URL padrão do passo 4. Desde a correção Y (15/11) o ideal padrão sai dos números
    # (ideal.escolhaPadrao): Hoje 2.480 · Melhorado 2.550 · Ideal Mais renda 5.220; com prioridade=garantir, o Guardar água dá 3.980.
    # O Mais renda era 6.640 até o pedido do José de nunca recomendar monocultura (15/11, tarde): em 2028 as 3 partes eram só
    # mandioca; agora a mandioca gira com outra cultura (extras/cenarios.js) e o ideal cai para 5.220, ainda bem acima de hoje
    ed.abrir(f"#/{q}/4")
    vals = ed.js("[...document.querySelectorAll('.hi-graf .hi-g-val')].map((t) => t.textContent.trim())") or []
    ed.abrir(f"#/{q}/4?prioridade=garantir")
    vals_g = ed.js("[...document.querySelectorAll('.hi-graf .hi-g-val')].map((t) => t.textContent.trim())") or []
    res["C2"] = (all(any(v in x for x in vals) for v in ("2.480", "2.550", "5.220")) and any("3.980" in x for x in vals_g),
                 " | ".join(vals) + " · garantir: " + " | ".join(vals_g))

    # C3: o controle de 2 lados e as 4 prioridades mudam o desenho e os números do Plano; voltar ao seu jeito desenha igual
    ed.abrir(f"#/{q}/3")
    a0 = assin()
    vistos, hashes = [], []
    ed.depois_de(clicar('[data-lado="ideal"]'), 2.5)
    hashes.append(hash_())
    for p in ("agua", "renda", "solo", "plano"):
        ed.depois_de(clicar(f'[data-prio="{p}"]'), 2.5)
        vistos.append(assin())
        hashes.append(hash_())
    ed.depois_de(clicar('[data-lado="melhor"]'), 2.5)
    a1 = assin()
    hashes.append(hash_())
    des = {v["desenho"] for v in vistos}
    num = {json.dumps(v["plano"], ensure_ascii=False) for v in vistos}
    quer = ["plano=ideal", "prioridade=garantir", "prioridade=vender", "prioridade=solo", "prioridade=equilibrar"]
    res["C3"] = (len(des) == 4 and len(num) == 4 and all(k in h for k, h in zip(quer, hashes)) and "plano=" not in hashes[-1]
                 and a1["desenho"] == a0["desenho"] and a0["desenho"] not in des,
                 f"desenhos diferentes {len(des)}/4, números {len(num)}/4, voltar igual {a1['desenho'] == a0['desenho']} | {' → '.join(h.split('?')[-1] for h in hashes)}")

    # C4: o mesmo plano e os mesmos números no Plano, no Dinheiro e no Relatório (Seu Antônio, 40 × 100 m, o ideal com Água)
    hs = f"?{ANTONIO}&plano=ideal&prioridade=garantir"
    ed.abrir(f"#/{q}/3{hs}")
    p3 = assin()
    ed.abrir(f"#/{q}/4{hs}")
    p4 = assin()
    ed.abrir(f"#/{q}/5{hs}")
    p5 = assin()
    comuns = [k for k in p3["plano"] if k in p4["dinheiro"]]
    iguais = [k for k in comuns if numeros(p3["plano"][k]) == numeros(p4["dinheiro"][k])]
    res["C4"] = (p3["lado"] == "ideal" and p3["prio"] == "agua" and "ideal" in p4["colSel"] and "O ideal" in p5["ficha"] and "Guardar água" in p5["ficha"]
                 and "40 × 100 m" in p5["ficha"] and len(comuns) >= 3 and iguais == comuns and "40 × 100 m" in p3["desenhoTxt"],
                 f"Plano {p3['lado']}/{p3['prio']} · Dinheiro coluna '{p4['colSel']}' · Relatório '{' '.join(p5['ficha'].split())[:90]}' · "
                 f"linhas iguais {len(iguais)} de {len(comuns)}: " + "; ".join(f"{k}: {p3['plano'][k]}" for k in comuns))

    # C5: voltar do navegador 4 → 3 → 2 → globo (se o servidor recusou um pedido ou o 1º verde não andou, repete)
    quer5 = [f"#/{q}/4", f"roca.html#/{q}/3", f"roca.html#/{q}/2", "index.html"]
    for tentativa in range(2):
        ed.abrir("", "index.html")
        ed.erros = []
        ed.js(f"location.href = 'roca.html#/{q}/2'")
        ed.dormir(1)
        ed.esperar(PRONTO, 20)
        ed.depois_de(clicar("#avancar"), 2.5)
        andou = hash_() == f"#/{q}/3"
        ed.depois_de(clicar("#avancar"), 2.5)
        pilha = [hash_()]
        for _ in range(3):
            ed.js("history.back()")
            ed.dormir(2.5)
            pilha.append(ed.js("location.pathname.replace('/', '') + location.hash"))
        if pilha == quer5 or not (recusou(ed.erros) or not andou):
            break
        print(f"  (C5, tentativa {tentativa + 1}: pilha {pilha} | 1º verde andou {andou} | erros {ed.erros[:3]})", flush=True)
        ed.dormir(2)
    res["C5"] = (pilha == quer5, " → ".join(map(str, pilha)))

    # C6: "Mudar" volta ao passo de onde saiu: a ficha no passo 4 (linha do que planta) e o baixio no Relatório
    ed.abrir(f"#/{q}/4")
    ed.depois_de(clicar(".ficha-mudar"), 2.5)
    h2 = hash_()
    vis = lambda k: ed.js(f"(() => {{ const b = document.getElementById('linha-{k}')?.getBoundingClientRect(); return !!b && b.top >= 0 && b.top < innerHeight - 100; }})()")
    na4, rot4 = vis("hoje"), ed.js("document.getElementById('avancar').innerText")
    ed.depois_de(clicar("#avancar"), 2.5)
    v4 = hash_()
    ed.abrir(f"#/{q}/5")
    ed.depois_de(clicar('.rl-mudar[data-editar="baixio"]'), 3)
    ed.dormir(1)  # a rolagem suave até a linha
    h5, na5, rot5 = hash_(), vis("baixio"), ed.js("document.getElementById('avancar').innerText")
    ed.depois_de(clicar("#avancar"), 2.5)
    v5 = hash_()
    res["C6"] = (h2 == f"#/{q}/2" and na4 and rot4 == "Voltar a Quanto rende →" and v4 == f"#/{q}/4"
                 and h5 == f"#/{q}/2" and na5 and rot5 == "Voltar ao relatório →" and v5 == f"#/{q}/5",
                 f"4: {h2} linha {na4} '{rot4}' → {v4} | 5: {h5} baixio {na5} '{rot5}' → {v5}")

    # C7: terra "não sei": o aviso da areia olha só as culturas do plano à vista (Piritiba, seu jeito com milho; Petrolina, o ideal
    # com caupi e os 2 sorgos); com terra=barro some. Quixadá (milho e caupi, as 4 prioridades) tem data na areia: lá não aparece.
    av = {}
    pe = "2611101"
    casos7 = (("2924801", ""), (q, ""), (pe, "?plano=ideal"), (pe, "?plano=ideal&terra=barro"))
    for cod, extra in casos7:
        ed.abrir(f"#/{cod}/3{extra}")
        av[cod + extra] = ed.js("[...document.querySelectorAll('.aviso-terra')].map((e) => e.innerText.trim()).join(' / ')") or ""
    res["C7"] = ("Em terra de areia" in av["2924801"] and not av[q] and "data segura aqui" in av[pe + "?plano=ideal"] and not av[pe + "?plano=ideal&terra=barro"],
                 " | ".join(f"{c}{e or ' padrão'}: '{av[c + e][:60]}'" for c, e in casos7))

    # C8: a maniva em Sua roça: com mandioca no jeito de hoje a linha aparece; "Não tenho" grava maniva=nao e a mandioca não é
    # replantada. Desde a correção Y (15/11) a mandioca marcada em "O que planta hoje" já está no chão e colhe em 2027; por isso
    # confere 2028 e 2029 (botões data-ano 1 e 2)
    ed.abrir(f"#/{q}/3?hoje=milho:50,mandioca:50")
    m0 = "mandioca" in (assin().get("desenhoTxt") or "").lower()
    ed.abrir(f"#/{q}/2?hoje=milho:50,mandioca:50")
    linha = ed.js("!!document.getElementById('linha-maniva')")
    ed.js(clicar('[data-maniva="nao"]'))
    ed.dormir(0.6)
    ed.depois_de(clicar("#avancar"), 4)
    a8 = assin()
    m1 = False
    for k in ("1", "2"):
        ed.js(clicar(f'[data-ano="{k}"]'))
        ed.dormir(0.6)
        # o desenho de 2028 escreve "antes: mandioca" (o que esteve ali): só conta a cultura do ano
        m1 = m1 or "mandioca" in re.sub(r"antes: *\S+", "", (assin().get("desenhoTxt") or "").lower())
    res["C8"] = (linha and m0 and not m1 and "maniva=nao" in hash_() and hash_().startswith(f"#/{q}/3") and "maniva" in a8["texto"].lower(),
                 f"linha {linha} | mandioca no desenho {m0} → {m1} | {hash_()}")

    # C9: o ano passado em Sua roça: "Milho" em 2025 grava antes=2025:milho e o Plano diz por quê, na parte que muda
    ed.abrir(f"#/{q}/2?hoje=milho:50,feijao:50")
    ed.js(clicar('[data-antes="milho"]'))
    ed.dormir(0.6)
    ed.depois_de(clicar("#avancar"), 4)
    t9 = texto()
    res["C9"] = ("antes=2025:milho" in hash_() and "ali teve milho em 2025 e 2026" in t9, f"{hash_()} | {'por quê à vista' if 'ali teve milho' in t9 else 'sem o por quê'}")

    # C10: Relatório (Seu Antônio, ideal com Água): toda data dd/mm/aaaa existe na agenda; WhatsApp leva o plano; sem o bloco do técnico
    # (saiu do Relatório) e com o "Imprimir / salvar PDF"
    ed.abrir(f"#/{q}/5{hs}")
    d10 = ed.js(DATAS_RELATORIO) or {}
    ed.js("navigator.share = async (d) => { window.__share = d; }; window.open = (u) => { window.__aberto = u; return {}; }")
    verde = ed.js("document.querySelectorAll('#jornada [data-extra=leve_ao_tecnico], #leve-ao-tecnico').length + (document.querySelector('#jornada [data-rl=imprimir]') ? 0 : 100)")
    rot = ed.js("document.getElementById('avancar').innerText")
    ed.depois_de(clicar("#avancar"), 1.5)
    share = ed.js("window.__share?.text || ''") or ""
    ed.js("delete navigator.share; Object.defineProperty(navigator, 'share', { value: undefined, configurable: true })")
    ed.dormir(1)  # o botão religa 0,8 s depois quando a tela não muda
    ed.depois_de(clicar("#avancar"), 1.5)
    wa = ed.js("window.__aberto || ''") or ""
    res["C10"] = (d10.get("datas", 0) >= 10 and not d10.get("fora") and rot == "Mandar no WhatsApp" and len(share) > 100 and "Próximas tarefas" in share
                  and re.search(r"\d{2}/\d{2}/\d{4}", share) and wa.startswith("https://wa.me/?text=") and verde == 0,
                  f"{d10.get('nome')}: {d10.get('datas')} datas ({d10.get('unicas')} diferentes), fora da agenda {d10.get('fora')} | '{rot}' share {len(share)} letras | wa.me {wa[:22]} | técnico/sem PDF {verde} (deve ser 0)")

    # C11: selo "MEDIDO · NASA …" à vista em Sua roça e o toque mostra a fonte
    ed.abrir(f"#/{q}/2")
    ed.js(clicar("#jornada .selo[data-fonte]"))
    ed.dormir(0.5)
    bal = ed.js("(() => { const b = document.getElementById('selo-balao'); return b && !b.hidden ? b.innerText : ''; })()") or ""
    selo = ed.js("[...document.querySelectorAll('#jornada .selo')].map((s) => s.innerText).find((t) => /NASA/.test(t)) || ''")
    res["C11"] = ("NASA" in selo and len(bal) > 20, f"'{selo}' | balão: {bal[:60]!r}")

    # C12: links antigos: #/<cod>/1 abre Sua roça com as mesmas respostas; /5 abre o Relatório; ⅓ de baixio desenha
    ed.abrir(f"#/{q}/1?ha=2&terra=barro")
    h1, k1, e1 = hash_(), ed.js("document.querySelector('.kicker')?.innerText"), list(ed.erros)
    ed.abrir(f"#/{q}/5?terra=mista")
    k5 = ed.js("document.querySelector('.kicker')?.innerText")
    ed.abrir(f"#/{q}/3?terra=mista&baixio=terco")
    ok3 = ed.js("!!document.querySelector('.rocado-svg') && !document.querySelector('#jornada .erro')")
    res["C12"] = (h1.startswith(f"#/{q}/2?") and "ha=2" in h1 and "terra=barro" in h1 and (k1 or "").lower() == "sua roça" and (k5 or "").lower() == "relatório" and ok3
                  and not e1 and not ed.erros, f"/1 → {h1} ({k1}) | /5: {k5} | ⅓: desenho {ok3} | erros {len(e1) + len(ed.erros)}")

    # C13: a frase do ponto 16 (rodapé) leva ao topo do Relatório: do Plano, abre o passo 5 no topo; já no fim do Relatório, sobe ao topo
    ed.abrir(f"#/{q}/3")
    ed.js(clicar("#decide-fim"))
    ed.dormir(5)
    y1, k13 = ed.js("Math.round(scrollY)"), ed.js("document.querySelector('.kicker')?.innerText || ''")
    ed.js("window.scrollTo(0, document.documentElement.scrollHeight)")
    ed.dormir(0.5)
    ed.js(clicar("#decide-fim"))
    ed.dormir(2)
    y2 = ed.js("Math.round(scrollY)")
    res["C13"] = (hash_().startswith(f"#/{q}/5") and (k13 or "").lower() == "relatório" and y1 is not None and y1 <= 5 and y2 is not None and y2 <= 5,
                  f"{hash_()} | {k13} | do Plano: topo a {y1} px | do fim do Relatório: {y2} px")

    for k in sorted(res, key=lambda x: int(x[1:])):
        ok, det = res[k]
        print(f"{k:>3}: {'ok   ' if ok else 'FALHA'}  {det}", flush=True)
    return {k: {"ok": bool(v[0]), "detalhe": v[1]} for k, v in res.items()}


# ------------------------------------------------------------------ parte 3: painel e cartão do mapa
def parte_painel(ed, cod="2311306"):
    print("\n== Parte 3: o painel (antigo 'Do espaço') e o cartão do mapa ==")
    res = {}
    quer = {"clima": ["tendencias"], "chuva": ["cenario_chuva"], "dados": ["confianca", "glossario", "satelite_chao", "harmonizacao"]}
    for tent in range(2):
        ed.abrir(f"?cod={cod}", "painel.html")
        vistos, selos, lat, palavras = {}, {}, {}, {}
        for aba, extras in quer.items():
            ed.js(clicar(f'#abas [data-aba="{aba}"]'))
            ed.esperar("!/Buscando/.test(document.querySelector('#faixa')?.textContent || '')", 30)
            ed.dormir(4)
            ed.js("document.querySelectorAll('main details').forEach((d) => { d.open = true; d.dispatchEvent(new Event('toggle')); })")
            ed.dormir(3)
            m = ed.js("""(() => ({ extras: [...document.querySelectorAll('#extras [data-extra]')].filter((d) => d.childElementCount).map((d) => d.dataset.extra),
              selos: document.querySelectorAll('main .selo').length, sw: document.documentElement.scrollWidth, iw: innerWidth,
              palavras: (document.querySelector('main')?.innerText.match(/\\S+/g) || []).length }))()""") or {}
            vistos[aba], selos[aba], lat[aba], palavras[aba] = m.get("extras", []), m.get("selos", 0), m.get("sw", 999) > m.get("iw", 0), m.get("palavras")
        verde = ed.js("document.getElementById('plano')?.getAttribute('href') || ''") or ""
        nc = ed.js(f"import('/js/globo/camadas.js').then((m) => m.numerosChave('{cod}')).then((ns) => (ns || []).map((n) => JSON.stringify(n).slice(0, 120)))") or []
        erros = list(ed.erros)
        if not recusou(erros):
            break
        print(f"  (painel de novo: {erros[:2]})", flush=True)
        ed.dormir(3)
    faltam = {a: [x for x in e if x not in vistos[a]] for a, e in quer.items()}
    res["P1"] = (not any(faltam.values()) and all(selos[a] > 0 for a in quer) and not any(lat.values()) and not erros,
                 f"extras: {vistos} | faltam {faltam} | selos {selos} | palavras {palavras} | lateral {lat} | erros {erros[:2]}")
    res["P2"] = (bool(re.search(rf"roca\.html#/{cod}/2$", verde)) and isinstance(nc, list) and len(nc) >= 3,
                 f"verde → {verde} | cartão do mapa: {len(nc) if isinstance(nc, list) else nc} números {nc if isinstance(nc, list) else ''}")
    for k in sorted(res):
        print(f"{k}: {'ok   ' if res[k][0] else 'FALHA'}  {res[k][1]}", flush=True)
    return {k: {"ok": bool(v[0]), "detalhe": v[1]} for k, v in res.items()}


# ------------------------------------------------------------------ parte 4: percurso (percorrer_fluxo.py) e PDF, um Edge por vez
def parte_fim():
    print("\n== Parte 4: o percurso (percorrer_fluxo.py) e o PDF do Relatório ==")
    res = {}
    pasta = os.path.join(PRINTS, "percurso")
    p = subprocess.run([PY, "-I", "-X", "utf8", os.path.join(AQUI, "percorrer_fluxo.py"), pasta], capture_output=True, text=True, encoding="utf-8",
                       timeout=900, env={**os.environ, "MSYS_NO_PATHCONV": "1"})
    saida = p.stdout
    open(os.path.join(PRINTS, "percurso.txt"), "w", encoding="utf-8").write(saida + p.stderr)
    for k, rot in (("F1", "globo → plano"), ("F2", "percurso 2 → 3 → 4 → 5"), ("F3", "Seu Antônio"), ("F4", "40 × 100 m"), ("F5", "ideal + água")):
        lin = next((l for l in saida.splitlines() if l.startswith(rot + ":")), "")
        res[k] = (lin.rstrip().endswith(" ok"), lin or f"(sem a linha '{rot}'; rc {p.returncode}) {saida[-300:]}")
    # PDF pela linha de comando do Edge (o Page.printToPDF do CDP não imprime nesta máquina): dispara o beforeprint (detalhe aberto)
    for k, hs in (("F6", f"#/2311306/5?{ANTONIO}&plano=ideal&prioridade=garantir"), ("F7", "#/2311306/5?plano=ideal&prioridade=equilibrar")):
        arq = os.path.join(PRINTS, f"relatorio_{k}.pdf")
        perfil = os.path.join(os.environ.get("QUADRA_PERFIS", "E:/campeonato-nasa/tmp/edge_perfis"), f"quadra-pdf-{os.getpid()}")
        if os.path.exists(arq):
            os.remove(arq)
        subprocess.run([EDGE, "--headless", "--disable-gpu", f"--user-data-dir={perfil}", "--no-pdf-header-footer", "--virtual-time-budget=20000",
                        f"--print-to-pdf={arq}", f"{BASE}/roca.html{hs}&lang=pt"], timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.rmtree(perfil, ignore_errors=True)
        dados = open(arq, "rb").read() if os.path.exists(arq) else b""
        pag = len(re.findall(rb"/Type\s*/Page[^s]", dados))
        tem = b"FontFile" in dados or len(dados) > 30000
        res[k] = (1 <= pag <= 4 and tem, f"{arq}: {len(dados)} bytes, {pag} páginas")
    for k in sorted(res):
        print(f"{k}: {'ok   ' if res[k][0] else 'FALHA'}  {res[k][1]}", flush=True)
    return {k: {"ok": bool(v[0]), "detalhe": v[1]} for k, v in res.items()}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cods = args[0].split(",") if args else list(MUNS)
    so = [a[5:] for a in sys.argv if a.startswith("--so-")]
    quer = lambda parte: parte in so if so else not (parte in ("node", "fim") and f"--sem-{parte}" in sys.argv)
    os.makedirs(PRINTS, exist_ok=True)
    saida = {}
    if quer("node"):
        saida["node"] = parte_node()
    if quer("telas") or quer("toques") or quer("painel"):
        ed = Edge()
        try:
            if quer("telas"):
                saida["telas"] = parte_telas(ed, cods)
            if quer("toques"):
                saida["toques"] = parte_toques(ed)
            if quer("painel"):
                saida["painel"] = parte_painel(ed)
        finally:
            ed.fechar()
    if quer("fim"):
        saida["fim"] = parte_fim()
    json.dump(saida, open(f"{PRINTS}/aceite.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    falhas = [f"{p}:{k}" for p, v in saida.items() if isinstance(v, dict) for k, x in v.items() if not x["ok"]]
    falhas += [f"telas:{t['cod']}/{t['passo']}{t['suf']}" for t in saida.get("telas", []) if t["falhas"]]
    print(f"\nRESUMO: {'tudo ok' if not falhas else 'FALHAS ' + ', '.join(falhas)}\nsalvo em {PRINTS}/aceite.json")
    sys.exit(1 if falhas else 0)
