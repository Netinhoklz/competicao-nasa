"""Aceite do fluxo novo (analise/fluxo/00_FLUXO_FINAL.md, seção 8) no Edge sem janela a 390x844.
Uso: MSYS_NO_PATHCONV=1 python -I -X utf8 aceite_fluxo.py [cod,cod,...] [--so-telas | --so-toques] [--prints]
(--prints: um print inteiro de cada tela em E:/campeonato-nasa/tmp/fluxo_novo/<cod>/<passo>_<tela>.png)

Parte 1 (telas): roda o script da seção 8 em cada passo (2, 3, 4, 5, 1) de cada município, mais as posições dos critérios
1, 9 e 17, o selo "· NASA" à vista (19), a rolagem de lado com todos os "ver mais" abertos (20) e os erros do console (7),
e imprime uma tabela. Parte 2 (toques, Quixadá e Piritiba): critérios 4, 8, 10 a 19 e 21.
Os critérios 2 e 3 (do painel ao plano e o Seu Antônio) ficam em percorrer_fluxo.py.
Roda tudo em série num Edge só: com testes em paralelo o servidor recusa pedidos (ERR_CONNECTION_REFUSED)."""
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

import websocket

BASE = "http://127.0.0.1:8090"
MUNS = {"2311306": "Quixadá", "2304103": "Crateús", "2208007": "Picos", "2402006": "Caicó", "2611101": "Petrolina",
        "2700300": "Arapiraca", "2903201": "Barreiras"}
ORDEM = [2, 3, 4, 5, 1]
NOME = {2: "Sua roça", 3: "Plano", 4: "Dinheiro", 5: "Se secar", 1: "Do espaço"}
TETO = {2: (1000, 100), 3: (2400, 300), 4: (2200, 260), 5: (2400, 300), 1: (2800, 320)}  # altura, palavras (seção 5)
NASA_EM = {2, 5, 1}  # telas que precisam de "NASA" à vista

# o script da seção 8, sem mudar nada, mais os campos dos critérios 1, 9, 17 e 19
SECAO8 = r"""(() => {
  const j = document.getElementById("jornada");
  const vis = (e) => (e.offsetWidth || e.offsetHeight) && !e.closest("details:not([open])");
  const txt = j.innerText;
  return {
    hash: location.hash,
    altura: document.documentElement.scrollHeight,
    palavras: txt.trim().split(/\s+/).length,
    primarios: [...document.querySelectorAll(".botao.primario")].filter(vis).length,          // = 1
    contadores: document.querySelectorAll(".quiz-barra,.hi-barra,.hs-barra").length,          // = 0
    nDeM: /\b\d+ de \d+\b/i.test(document.querySelector(".kicker")?.innerText || ""),         // false
    lateral: document.documentElement.scrollWidth > innerWidth,                              // false
    olhos: [...j.querySelectorAll(".olho")].filter(vis).length,                              // <= 2
    nasa: /NASA/.test(txt),                                                                  // true em Sua roça, Se secar e Do espaço
    proibidas: ["5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde",
      "qualquer terra", "sem preço aqui", "ainda não vende", "à frente de hoje em"].filter((f) => txt.includes(f)), // []
    selosPequenos: [...document.querySelectorAll(".selo")].filter((s) => parseFloat(getComputedStyle(s).fontSize) < 11).length, // 0
    summaryBaixo: [...document.querySelectorAll("summary")].filter((s) => vis(s) && s.getBoundingClientRect().height < 44).length, // 0
  };
})()"""
EXTRA = r"""(() => {
  const vis = (e) => { const b = e.getBoundingClientRect(); return (b.width || b.height) && !e.closest("details:not([open])"); }; // vale para SVG
  const topo = (s) => { const e = [...document.querySelectorAll(s)].find(vis); return e ? Math.round(e.getBoundingClientRect().top + scrollY) : null; };
  const fundo = (s) => { const v = [...document.querySelectorAll(s)].filter(vis); return v.length ? Math.round(Math.max(...v.map((e) => e.getBoundingClientRect().bottom)) + scrollY) : null; };
  const graf = topo(".hi-graf");
  return {
    erroPasso: !!document.querySelector("#jornada .erro"),
    kicker: document.querySelector(".kicker")?.innerText || "",
    proxAntigos: document.querySelectorAll("#q-prox,#hi-prox,#hs-prox").length,
    linhas: ["hoje", "ha", "terra", "baixio"].filter((k) => document.getElementById("linha-" + k)).length,
    terraTopo: topo("#linha-terra"),
    agoraTopo: topo(".plantio-agora"), desenhoTopo: topo(".rocado-svg"),
    grafTopo: graf,
    controlesAntes: graf === null ? null : [...document.querySelectorAll("#jornada .seg, #jornada [data-set]")]
      .filter((e) => vis(e) && e.getBoundingClientRect().top + scrollY < graf).length,
    l2027Fundo: fundo(".seg-27-linha"), chuvaTopo: topo(".cc-cenario .kicker"),
    chuvaFrase: document.querySelector('[data-cc="frase"]')?.innerText || "",
    selosNasa: [...document.querySelectorAll("#jornada .selo")].filter(vis).map((s) => s.innerText).filter((t) => /MEDIDO · NASA/.test(t)).length,
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


class Edge:
    def __init__(self, larg=390, alt=844):
        self.larg, self.alt = larg, alt
        porta = 9100 + os.getpid() % 150
        self.perfil = os.path.join(os.environ.get("QUADRA_PERFIS", "E:/campeonato-nasa/tmp/edge_perfis"), f"quadra-aceite-{os.getpid()}")
        self.proc = subprocess.Popen([r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "--headless=new", "--disable-gpu",
                                      "--hide-scrollbars", f"--remote-debugging-port={porta}", f"--user-data-dir={self.perfil}", "about:blank"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        if pagina != "roca.html":
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
        self.cmd("Emulation.setDeviceMetricsOverride", width=self.larg, height=min(alt, 9000), deviceScaleFactor=1, mobile=self.larg < 600)
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


def medir_tela(ed, cod, passo):
    for tentativa in range(2):
        ok = ed.abrir(f"#/{cod}/{passo}")
        s8, ex = ed.js(SECAO8), ed.js(EXTRA)
        recusado = any("ERR_CONNECTION_REFUSED" in e or "Failed to fetch" in e for e in ed.erros)
        if ok and not ex.get("erroPasso") and not recusado:
            break
        print(f"  (de novo {cod}/{passo}: pronto={ok} erros={ed.erros[:2]})", flush=True)
        ed.dormir(2)
    erros = list(ed.erros)
    if "--prints" in sys.argv:
        ed.print_inteiro(f"E:/campeonato-nasa/tmp/fluxo_novo/{cod}/{passo}_{NOME[passo].replace(' ', '_').lower()}.png")
    lat = ed.js(LATERAL_ABERTO)
    return s8, ex, lat, erros


def falhas_tela(passo, s8, ex, lat, erros):
    f = []
    alt_max, pal_max = TETO[passo]
    if s8["altura"] > alt_max:
        f.append(f"altura>{alt_max}")
    if s8["palavras"] > pal_max:
        f.append(f"palavras>{pal_max}")
    if s8["primarios"] != 1:
        f.append(f"primarios={s8['primarios']}")
    if s8["contadores"]:
        f.append("contadores")
    if s8["nDeM"]:
        f.append("n de m")
    if s8["lateral"] or lat["sw"] > lat["iw"]:
        f.append("lateral" + ("(aberto)" if not s8["lateral"] else ""))
    if s8["olhos"] > 2:
        f.append(f"olhos={s8['olhos']}")
    if passo in NASA_EM and not (s8["nasa"] and ex["selosNasa"]):
        f.append("sem 'MEDIDO · NASA' à vista")
    if s8["proibidas"]:
        f.append("proibidas:" + "/".join(s8["proibidas"]))
    if s8["selosPequenos"]:
        f.append("selo<11px")
    if s8["summaryBaixo"]:
        f.append("summary<44px")
    if ex["erroPasso"]:
        f.append("erro no passo")
    if ex["topoFixo"] > 96:
        f.append(f"topo {ex['topoFixo']}px")
    if ex["barra"] > 64:
        f.append(f"barra {ex['barra']}px")
    if passo == 2:
        if ex["proxAntigos"] or ex["linhas"] != 4:
            f.append("crit1")
        if (ex["terraTopo"] or 9999) >= 844:
            f.append("terra abaixo da dobra")
    if passo == 3:
        if (ex["agoraTopo"] or 9999) > 400:
            f.append(f"Agora {ex['agoraTopo']}")
        if (ex["desenhoTopo"] or 9999) > 550:
            f.append(f"desenho {ex['desenhoTopo']}")
    if passo == 4 and ex["grafTopo"] is not None:
        if ex["grafTopo"] > 450 or ex["controlesAntes"]:
            f.append(f"grafico {ex['grafTopo']}/{ex['controlesAntes']}")
    if passo == 5:
        if (ex["l2027Fundo"] or 0) > 900 or (ex["chuvaTopo"] or 9999) > 900:
            f.append(f"2027 {ex['l2027Fundo']} chuva {ex['chuvaTopo']}")
        if "Com a chuva normal" not in ex["chuvaFrase"]:
            f.append("chuva não abre em 100%")
    if erros:
        f.append(f"{len(erros)} erro(s) no console")
    return f


def parte_telas(ed, cods):
    print("\n== Parte 1: as telas (390x844, todo 'ver mais' fechado; lateral também com tudo aberto) ==")
    cab = f"{'município':<10} {'tela':<10} {'altura':>6} {'palav':>5} {'prim':>4} {'olho':>4} {'NASA':>4} {'pos':<16} {'erro':>4}  resultado"
    print(cab)
    print("-" * len(cab))
    linhas, total_falhas = [], 0
    for cod in cods:
        for p in ORDEM:
            s8, ex, lat, erros = medir_tela(ed, cod, p)
            f = falhas_tela(p, s8, ex, lat, erros)
            total_falhas += bool(f)
            pos = {2: f"terra {ex['terraTopo']}", 3: f"agora {ex['agoraTopo']} des {ex['desenhoTopo']}", 4: f"gráfico {ex['grafTopo']}",
                   5: f"2027 {ex['l2027Fundo']} ch {ex['chuvaTopo']}", 1: ""}[p]
            print(f"{MUNS.get(cod, cod):<10} {NOME[p]:<10} {s8['altura']:>6} {s8['palavras']:>5} {s8['primarios']:>4} {s8['olhos']:>4} "
                  f"{ex['selosNasa']:>4} {pos:<16} {len(erros):>4}  {'ok' if not f else 'FALHA: ' + ', '.join(f)}", flush=True)
            for e in erros[:3]:
                print("      ", e)
            linhas.append({"cod": cod, "passo": p, **s8, **{k: v for k, v in ex.items() if k != "chuvaFrase"}, "lateralAberto": lat,
                           "erros": erros, "falhas": f})
    print(f"\ntelas com falha: {total_falhas} de {len(linhas)}")
    return linhas


def parte_toques(ed):
    print("\n== Parte 2: os toques (Quixadá; Piritiba no 13) ==")
    res = {}
    q = "2311306"
    hash_ = lambda: ed.js("decodeURIComponent(location.hash)")
    clicar = lambda sel: f"(() => {{ const b = document.querySelector({json.dumps(sel)}); if (!b) return 'sem ' + {json.dumps(sel)}; b.click(); return 'ok'; }})()"
    texto = lambda: ed.js("document.getElementById('jornada').innerText")

    # 4: só "Ver o meu plano" deixa o hash sem parâmetros; ficha "(típico)"; passo 4 "(o comum daqui)"
    ed.abrir(f"#/{q}/2")
    ed.depois_de(clicar("#avancar"), 2.5)
    h3, ficha = hash_(), ed.js("document.getElementById('ficha').innerText")
    ed.depois_de(clicar("#avancar"), 3)
    res[4] = (h3 == f"#/{q}/3" and "(típico)" in ficha and "(o comum daqui)" in texto(), f"{h3} | ficha '{ficha.strip()}'")

    # 8: os R$ de Quixadá na URL padrão
    ed.abrir(f"#/{q}/4")
    nums = ed.js("[...document.querySelectorAll('.hi-graf .hi-g-val, .hi-graf .hi-g-sub')].map((t) => t.textContent.trim()).filter(Boolean)") or []
    junto = " ".join(nums)
    quero = ["2.480", "4.190", "4.360", "984", "2.490", "2.760"]
    res[8] = (all(v in junto for v in quero), junto)

    # 9: gráfico ≤ 450 px e nenhum controle antes (na parte 1, por município)
    # 10: "Renda" grava prioridade=vender e o número grande não muda
    antes = ed.js("[...document.querySelectorAll('.hi-graf .hi-g-val')].map((t) => t.textContent).join('|')")
    ed.depois_de(clicar(".cen-aba[data-jeito=renda]"), 2.5)
    depois = ed.js("[...document.querySelectorAll('.hi-graf .hi-g-val')].map((t) => t.textContent).join('|')")
    res[10] = ("prioridade=vender" in hash_() and antes == depois and bool(antes), f"{hash_()} | {antes} -> {depois}")

    # 11: voltar do navegador 4 → 3 → 2 → globo (como medir_tela: se o servidor recusou um pedido ou o 1º verde não andou, repete)
    quero11 = [f"#/{q}/4", f"roca.html#/{q}/3", f"roca.html#/{q}/2", "index.html"]
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
        recusado = any("ERR_CONNECTION_REFUSED" in e or "Failed to fetch" in e for e in ed.erros)
        if pilha == quero11:
            break
        print(f"  (critério 11, tentativa {tentativa + 1}: pilha {pilha} | 1º verde andou {andou} | erros {ed.erros[:3]})", flush=True)
        if not (recusado or not andou):
            break
        ed.dormir(2)
    res[11] = (pilha == quero11, " → ".join(map(str, pilha)))

    # 12: "Mudar" da ficha no passo 4 abre Sua roça na linha 1, com "Voltar a Quanto rende →", e volta
    ed.abrir(f"#/{q}/4")
    ed.depois_de(clicar(".ficha-mudar"), 2.5)
    h2 = hash_()
    na_tela = ed.js("(() => { const b = document.getElementById('linha-hoje')?.getBoundingClientRect(); return !!b && b.top >= 0 && b.top < innerHeight - 100; })()")
    rot = ed.js("document.getElementById('avancar').innerText")
    ed.depois_de(clicar("#avancar"), 2.5)
    res[12] = (h2 == f"#/{q}/2" and na_tela and rot == "Voltar a Quanto rende →" and hash_() == f"#/{q}/4", f"{h2} | linha à vista {na_tela} | '{rot}' | {hash_()}")

    # 13: terra "não sei": aviso por cultura; com terra=barro some (o texto perdeu a sigla na frente: "…não tem data segura aqui: pergunte
    # ao técnico."; o ZARC continua no selo do bloco)
    av = {}
    for cod, extra in (("2924801", ""), (q, ""), (q, "?terra=barro")):
        ed.abrir(f"#/{cod}/3{extra}")
        av[cod + extra] = ed.js("[...document.querySelectorAll('.aviso-terra')].map((e) => e.innerText.trim()).join(' / ')")
    res[13] = ("Em terra de areia, o" in av["2924801"] and "não tem data segura aqui" in av[q] and not av[q + "?terra=barro"],
               f"Piritiba: {av['2924801']} | Quixadá: {av[q]} | barro: '{av[q + '?terra=barro']}'")

    # 14: linha da maniva com mandioca no plano; "Não consigo" grava maniva=nao e a mandioca some do desenho
    ed.abrir(f"#/{q}/3")
    tem_linha = ed.js("!!document.querySelector('[data-maniva]')")
    mand0 = ed.js("/mandioca/i.test(document.querySelector('.rocado-svg')?.textContent || '')")
    ed.depois_de(clicar('[data-maniva="nao"]'), 3.5)
    mand1 = ed.js("/mandioca/i.test(document.querySelector('.rocado-svg')?.textContent || '')")
    res[14] = (tem_linha and mand0 and not mand1 and "maniva=nao" in hash_(), f"linha {tem_linha} | mandioca no desenho {mand0} -> {mand1} | {hash_()}")

    # 15: cartão do giro sem `antes`: "Se em 2025…" + SUPOSIÇÃO; "Foi no mesmo lugar" grava o antes
    ed.abrir(f"#/{q}/3")
    giro = ed.js("(() => { const e = document.querySelector('.hs-se')?.closest('[data-extra]'); return e ? e.innerText : ''; })()") or ""
    ed.depois_de(clicar("[data-antes]"), 2.5)
    res[15] = ("Se em 2025" in giro and "SUPOSI" in giro and "antes=2026:milho,feijao|2025:milho,feijao" in hash_(), f"{giro[:60]!r} | {hash_()}")

    # 16: memória no passo 5: "1998" no milho grava exp e mostra "O IBGE anotou…" sem sair do passo
    ed.abrir(f"#/{q}/5")
    ed.depois_de(clicar('[data-quebrou="milho"][data-quebrou-ano="1998"]'), 2.5)
    res[16] = (hash_().startswith(f"#/{q}/5") and "exp=quebra=milho:1998" in hash_() and "O IBGE anotou" in texto(), hash_())

    # 17: "E se chover…" em 100% e as linhas de 2027 acima de 900 px
    ed.abrir(f"#/{q}/5")
    ex = ed.js(EXTRA)
    res[17] = ("Com a chuva normal" in ex["chuvaFrase"] and (ex["l2027Fundo"] or 9999) <= 900 and (ex["chuvaTopo"] or 9999) <= 900,
               f"{ex['chuvaFrase'][:50]!r} | 2027 até {ex['l2027Fundo']} px | título {ex['chuvaTopo']} px")

    # 18: "Mandar no WhatsApp" chama navigator.share (ou wa.me); nenhum verde no bloco do técnico
    ed.js("navigator.share = async (d) => { window.__share = d; }; window.open = (u) => { window.__aberto = u; return {}; }")
    verde = ed.js("document.querySelectorAll('[data-extra=leve_ao_tecnico] .botao.primario').length")
    rot = ed.js("document.getElementById('avancar').innerText")
    ed.depois_de(clicar("#avancar"), 1.5)
    share = ed.js("(window.__share?.text || '').length")
    ed.js("delete navigator.share; Object.defineProperty(navigator, 'share', { value: undefined, configurable: true })")
    ed.dormir(1)  # o botão religa 0,8 s depois quando a tela não muda
    ed.depois_de(clicar("#avancar"), 1.5)
    wa = ed.js("window.__aberto || ''")
    res[18] = (rot == "Mandar no WhatsApp" and share > 100 and wa.startswith("https://wa.me/?text=") and verde == 0,
               f"'{rot}' | share {share} letras | sem share: {wa[:30]} | verdes no técnico {verde}")

    # 19: selo "MEDIDO · NASA …" à vista (parte 1) e o toque mostra a fonte
    ed.abrir(f"#/{q}/2")
    ed.js(clicar("#jornada .selo[data-fonte]"))
    ed.dormir(0.5)
    bal = ed.js("(() => { const b = document.getElementById('selo-balao'); return b && !b.hidden ? b.innerText : ''; })()") or ""
    selo = ed.js("[...document.querySelectorAll('#jornada .selo')].map((s) => s.innerText).find((t) => /NASA/.test(t)) || ''")
    res[19] = ("NASA" in selo and len(bal) > 20, f"'{selo}' | balão: {bal[:60]!r}")

    # 21: links antigos
    ed.abrir(f"#/{q}/1")
    k1, e1 = ed.js("document.querySelector('.kicker')?.innerText"), list(ed.erros)
    ed.abrir(f"#/{q}/3?terra=mista&baixio=terco")
    ok3 = ed.js("!!document.querySelector('.rocado-svg') && !document.querySelector('#jornada .erro')")
    res[21] = ((k1 or "").lower().startswith("do espa") and ok3 and not e1 and not ed.erros, f"passo 1: {k1} | ⅓: desenho {ok3} | erros {len(e1) + len(ed.erros)}")

    for k in sorted(res):
        ok, det = res[k]
        print(f"critério {k:>2}: {'ok   ' if ok else 'FALHA'}  {det}", flush=True)
    return {k: {"ok": v[0], "detalhe": v[1]} for k, v in res.items()}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cods = args[0].split(",") if args else list(MUNS)
    ed = Edge()
    saida = {}
    try:
        if "--so-toques" not in sys.argv:
            saida["telas"] = parte_telas(ed, cods)
        if "--so-telas" not in sys.argv:
            saida["toques"] = parte_toques(ed)
    finally:
        ed.fechar()
    pasta = "E:/campeonato-nasa/tmp/fluxo_novo/final"
    os.makedirs(pasta, exist_ok=True)
    json.dump(saida, open(f"{pasta}/aceite.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nsalvo em {pasta}/aceite.json")
