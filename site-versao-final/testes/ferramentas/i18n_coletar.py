"""Coleta os textos que o site mostra em português, para traduzir (web/i18n/en.json; guia em testes/i18n/LEIA-ME.md).
Abre o Edge sem janela (a classe do aceite, 390x844) com ?i18n=coletar e percorre: a página inicial (busca e 3 municípios no
mapa, com as camadas e as abas do painel ao lado), a jornada (roca.html) em cada município × passos 2 a 5 × as variantes abaixo,
com todo <details> aberto, o "Outra" do ano passado, os 3 anos e o mês a mês do desenho do Plano, um selo, um termo do glossário
o que só sai na impressão (beforeprint) e o texto do "Mandar no WhatsApp" do Relatório; e o painel.html com todas as abas.
Junta o window.__i18nChaves de cada tela (js/i18n.js: sem nome de lugar, número, sigla nem unidade sozinhos; o nome de lugar
dentro da frase vem como marcador {0}, igual ao número). Grava testes/i18n/pt_textos.json: lista de {chave, contagem, onde}
(onde = até 5 telas), em ordem alfabética, sem duplicatas.
Uso: MSYS_NO_PATHCONV=1 E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 testes/ferramentas/i18n_coletar.py [cod,cod,...]
     (padrão: os 7 municípios do aceite, 224 telas, ~40 min. Um só, ex. 2311306: 38 telas, ~9 min.) Um Edge por vez: não junto
     com o aceite (com dois, o servidor recusa pedidos)."""
import json
import os
import re
import sys
import time
import urllib.parse

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import aceite_fluxo as A  # noqa: E402

SITE = os.path.dirname(os.path.dirname(AQUI))
PASTA = os.path.join(SITE, "testes", "i18n")
ANTONIO = A.ANTONIO
# as variantes da jornada: (sufixo do hash, rótulo); Sua roça (passo 2) não lê o plano nem a prioridade
VARIANTES = [("", "hoje"), ("plano=ideal", "ideal")] + [(f"plano=ideal&prioridade={p}", f"ideal {p}") for p in
                                                        ("garantir", "vender", "solo", "equilibrar")] + [
    (ANTONIO, "Seu Antônio"), ("hoje=milho:100", "só milho"), ("terra=nao_sei", "terra não sei")]
SO_NO_PLANO = ("plano=", "prioridade=")
LUGARES_GLOBO = ["Quixadá, Ceará", "Picos, Piauí", "Petrolina, Pernambuco"]
PAINEL = ["2311306", "2611101", "2903201"]

# ---------------------------------------------------------------- o que se faz em cada tela (tudo acumula no __i18nChaves)
ROCA = r"""(async () => {
  const d = (ms) => new Promise((r) => setTimeout(r, ms));
  const abrir = () => document.querySelectorAll("details").forEach((x) => { x.open = true; });
  abrir(); await d(700); abrir(); await d(400);
  const leque = document.querySelector('[data-leque="antes"][aria-expanded="false"]');  // "Outra" do ano passado (Sua roça)
  if (leque) { leque.click(); await d(600); abrir(); await d(300); }
  for (const k of [1, 2, 0]) { const b = document.querySelector(`#jornada [data-ano="${k}"]`); if (b) { b.click(); await d(450); } }
  for (const b of [...document.querySelectorAll("#jornada [data-mes]")]) { b.click(); await d(110); }  // o mês a mês
  const ano = document.querySelector('#jornada [data-ano="0"]'); if (ano) { ano.click(); await d(300); }
  document.querySelector("#jornada .selo")?.click(); await d(300);      // o balão "de onde vem"
  document.querySelector("#jornada .gl-termo")?.click(); await d(700);  // o balão do glossário
  abrir(); await d(500);
  if (/\/5(\?|$)/.test(location.hash)) {
    window.dispatchEvent(new Event("beforeprint")); await d(800);  // o que só a impressão/PDF do Relatório mostra
    window.dispatchEvent(new Event("afterprint")); await d(300);
    // o texto do "Mandar no WhatsApp" (passa pelo t() do i18n.js)
    Object.defineProperty(navigator, "share", { configurable: true, value: async (o) => { window.__wa = o.text; } });
    document.getElementById("avancar")?.click();
    for (let i = 0; i < 20 && !window.__wa; i++) await d(200);
  }
  return true;
})()"""
INDEX_BUSCA = r"""(async () => {
  const d = (ms) => new Promise((r) => setTimeout(r, ms)), c = document.getElementById("buscaCampo");
  if (!c) return false;
  c.value = "Quixa"; c.dispatchEvent(new Event("input", { bubbles: true })); await d(1500);
  c.value = "zzqqxx"; c.dispatchEvent(new Event("input", { bubbles: true })); await d(800);
  document.getElementById("busca").requestSubmit(); await d(1500);
  c.value = ""; c.dispatchEvent(new Event("input", { bubbles: true }));
  return true;
})()"""
INDEX_MAPA = r"""(async () => {
  const d = (ms) => new Promise((r) => setTimeout(r, ms));
  for (const b of [...document.querySelectorAll('button[role="radio"][data-id]')]) { if (!b.hidden) { b.click(); await d(1000); } }
  for (const b of [...document.querySelectorAll("button[data-camada]")]) { b.click(); await d(600); }
  const f = document.querySelector("#painel iframe"), fd = f && f.contentDocument;
  if (fd) for (const b of [...fd.querySelectorAll("#abas [data-aba]")]) {
    b.click(); await d(2500); fd.querySelectorAll("details").forEach((x) => { x.open = true; }); await d(700);
  }
  return true;
})()"""
PAINEL_ABAS = r"""(async () => {
  const d = (ms) => new Promise((r) => setTimeout(r, ms));
  for (const b of [...document.querySelectorAll("#abas [data-aba]")]) {
    if (!b.offsetParent) continue;
    b.click();
    for (let i = 0; i < 30 && /Buscando/.test(document.querySelector("#faixa")?.textContent || ""); i++) await d(500);
    await d(1500);
    document.querySelectorAll("details").forEach((x) => { x.open = true; }); await d(1200);
  }
  return true;
})()"""
# o que o i18n.js juntou, na página e no painel do iframe (o globo)
JUNTAR = r"""(() => {
  const pega = (w) => { try {
    if (!w || !w.QUADRA_I18N) return null;
    return w.__i18nChaves ? { chaves: [...w.__i18nChaves] } : { vistas: [...w.__i18nVistas], faltas: [...w.__i18nFaltas], lingua: w.QUADRA_I18N.lingua };
  } catch (_) { return null; } };
  const f = document.querySelector("#painel iframe");
  return [pega(window), f ? pega(f.contentWindow) : null].filter(Boolean);
})()"""


def telas(cods):
    """(rótulo, página com a busca, hash, o que fazer, espera em s) de cada tela do percurso."""
    t = [("index", "index.html?{p}", "", INDEX_BUSCA, 9)]
    for lugar in LUGARES_GLOBO:
        t.append((f"index mapa {lugar.split(',')[0]}", "index.html?lugar=" + urllib.parse.quote(lugar) + "&{p}", "", INDEX_MAPA, 24))
    for cod in cods:
        for passo in (2, 3, 4, 5):
            for suf, rot in VARIANTES:
                if passo == 2 and suf.startswith(SO_NO_PLANO):
                    continue
                t.append((f"roca {cod}/{passo} {rot}", "roca.html?{p}", f"#/{cod}/{passo}" + (f"?{suf}" if suf else ""), ROCA, 0))
    for cod in PAINEL:
        t.append((f"painel {cod}", f"painel.html?cod={cod}&{{p}}", "", PAINEL_ABAS, 5))
    return t


def percorrer(param, cods, cada):
    """Abre cada tela com ?<param> (i18n=coletar ou lang=en), faz o que a tela pede e chama cada(rótulo, juntado, erros)."""
    ed = A.Edge()
    lista = telas(cods)
    t0 = time.time()
    try:
        for i, (rot, pag, hash_, fazer, espera) in enumerate(lista, 1):
            ok = ed.abrir(hash_, pagina=pag.format(p=param))
            if espera:
                ed.dormir(espera)
            r = ed.js(fazer)
            ed.dormir(0.5)
            juntado = ed.js(JUNTAR) or []
            erros = [e for e in ed.erros if "maplibre-gl.js" not in e and "FogMatrix" not in e]  # avisos do MapLibre (globo)
            cada(rot, juntado, erros)
            print(f"[{i}/{len(lista)} {time.time() - t0:5.0f}s] {rot}: {'ok' if ok and r is True else f'pronto={ok} fazer={r}'}"
                  f"{'  ERROS ' + str(erros[:2]) if erros else ''}", flush=True)
    finally:
        ed.fechar()
    return len(lista)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cods = args[0].split(",") if args else list(A.MUNS)
    total, ruins = {}, []

    def cada(rot, juntado, erros):
        if erros:
            ruins.append((rot, erros[:3]))
        for j in juntado:
            for chave, n in j.get("chaves", []):
                e = total.setdefault(chave, {"chave": chave, "contagem": 0, "onde": []})
                e["contagem"] += n
                if rot not in e["onde"] and len(e["onde"]) < 5:
                    e["onde"].append(rot)

    n = percorrer("i18n=coletar", cods, cada)
    os.makedirs(PASTA, exist_ok=True)
    lista = sorted(total.values(), key=lambda e: (e["chave"].casefold(), e["chave"]))
    arq = os.path.join(PASTA, "pt_textos.json")
    json.dump(lista, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    modelos = sum(1 for e in lista if re.search(r"\{\d+\}", e["chave"]))
    print(f"\n{len(lista)} chaves ({modelos} em forma de modelo, com {{0}}) em {n} telas → {arq}")
    print(f"telas com erro no console: {len(ruins)}" + "".join(f"\n  {r}: {e}" for r, e in ruins[:10]))


if __name__ == "__main__":
    main()
