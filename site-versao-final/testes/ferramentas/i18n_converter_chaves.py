"""Converte as chaves do web/i18n/en.json feitas antes da regra dos nomes de lugar (15/11) para a forma nova, sem retraduzir.
Antes, só o número virava {0}: "raiz a R$ {0}/kg (comum no CE) ·". Agora o nome de lugar também vira marcador, na ordem em que
aparece: "raiz a R$ {0}/kg (comum no {1}) ·". A forma nova serve para todos os municípios.
Abre o Edge (classe do aceite) numa página com o js/i18n.js em inglês e monta cada forma com a função do próprio runtime
(QUADRA_I18N._forma), no contexto de cada um dos 7 municípios do aceite. No valor em inglês, troca o nome (que fica igual) e o
número pelo marcador novo. Se não achar o nome ou o número no valor, a chave fica como está.
Só ACRESCENTA em "modelos" as chaves novas que ainda não existem; nada é apagado nem mudado. O runtime aceita as duas formas.
Uso: MSYS_NO_PATHCONV=1 E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 testes/ferramentas/i18n_converter_chaves.py [--seco]"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import aceite_fluxo as A  # noqa: E402

ARQ = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "web", "i18n", "en.json")

CONVERTER = r"""((pares, cods) => {
  const S = (i) => String.fromCharCode(0xE000 + i); // o {i} antigo vira um caractere sem letra nem n\u00FAmero
  const numEn = (n) => { if (n.includes("/")) return n; const s = /^[-−+]/.test(n) ? n[0] : "", c = n.slice(s.length);
    if (/^\d{1,3}(?:\.\d{3})+(?:,\d+)?$/.test(c)) return s + c.replace(/\./g, "_").replace(",", ".").replace(/_/g, ",");
    if (/^\d+,\d+$/.test(c)) return s + c.replace(",", "."); return n; };
  const achar = (v, lit) => { // a 1ª ocorrência inteira (sem letra/número colado) de lit em v
    let i = -1;
    while ((i = v.indexOf(lit, i + 1)) >= 0) {
      const a = v[i - 1] || "", d = v[i + lit.length] || "";
      if (!/[\p{L}\p{N}]/u.test(a) && !/[\p{L}\p{N}]/u.test(d)) return i;
    }
    return -1;
  };
  const novos = {}, sem = [];
  for (const cod of cods) {
    history.replaceState(null, "", `#/${cod}/2?lang=en`);
    for (const [k, v] of pares) {
      const m = QUADRA_I18N._forma(k.replace(/\{(\d+)\}/g, (x, i) => S(+i)));
      if (!m || !m.nums.some((n) => /\p{L}/u.test(n))) continue; // sem nome de lugar: nada muda
      // a ordem nova: cada marcador (o antigo, em sentinela, e o novo {j}) ganha o número da sua posição
      const toks = [...m.forma.matchAll(/\{(\d+)\}|[\uE000-\uF8FF]/g)];
      const idxVelho = {}, idxNovo = {};
      toks.forEach((t, p) => { if (t[1] !== undefined) idxNovo[t[1]] = p; else idxVelho[t[0].charCodeAt(0) - 0xE000] = p; });
      let chave = m.forma.replace(/\{(\d+)\}/g, (x, j) => `\u0001${idxNovo[j]}\u0002`).replace(/[\uE000-\uF8FF]/g, (c) => `\u0001${idxVelho[c.charCodeAt(0) - 0xE000]}\u0002`);
      chave = chave.replace(/\u0001(\d+)\u0002/g, "{$1}");
      // no valor, o marcador provisório não tem algarismo (a busca do número não pode cair dentro dele)
      const mk = (p) => `\u0001${String.fromCharCode(0xF000 + p)}\u0002`;
      let val = v.replace(/\{(\d+)\}/g, (x, i) => (idxVelho[i] === undefined ? x : mk(idxVelho[i]))), ok = true;
      m.nums.forEach((lit, j) => {
        if (!ok) return;
        const cand = /\p{L}/u.test(lit) ? [lit] : [numEn(lit), lit];
        const c = cand.find((x) => achar(val, x) >= 0);
        if (c === undefined) { ok = false; return; }
        const i = achar(val, c);
        val = val.slice(0, i) + mk(idxNovo[j]) + val.slice(i + c.length);
      });
      if (!ok) { sem.push(k); continue; }
      val = val.replace(/\u0001([-])\u0002/g, (x, c) => `{${c.charCodeAt(0) - 0xF000}}`);
      // só lugar e número ("{0}-{1}", "{0} ({1})"): o runtime já deixa como está, não precisa de chave
      if (chave !== k && !(chave in novos) && /\p{L}/u.test(chave.replace(/\{\d+\}/g, ""))) novos[chave] = val;
    }
  }
  return { novos, sem: [...new Set(sem)] };
})"""


def main():
    seco = "--seco" in sys.argv
    d = json.load(open(ARQ, encoding="utf-8"))
    pares = list(d.get("textos", {}).items()) + list(d.get("modelos", {}).items())
    ed = A.Edge()
    try:
        ed.abrir("#/2311306/2?lang=en")
        pronto = ed.esperar("!!(window.QUADRA_I18N && QUADRA_I18N._forma('Ceará'))", 15)
        if not pronto:
            sys.exit("o i18n.js não carregou a lista de lugares")
        r = ed.js(f"({CONVERTER})({json.dumps(pares, ensure_ascii=False)}, {json.dumps(list(A.MUNS))})")
    finally:
        ed.fechar()
    if not isinstance(r, dict) or "novos" not in r:
        sys.exit(f"falhou: {str(r)[:300]}")
    # relê o arquivo agora (outro agente pode ter acrescentado chaves) e só acrescenta o que falta
    mtime = os.path.getmtime(ARQ)
    d = json.load(open(ARQ, encoding="utf-8"))
    todas = set(d["textos"]) | set(d["modelos"])
    novos = {k: v for k, v in r["novos"].items() if k not in todas}
    print(f"{len(pares)} chaves lidas; {len(r['novos'])} formas novas, {len(novos)} ainda não estavam no en.json; "
          f"{len(r['sem'])} com nome de lugar ficaram como estão (o nome ou o número não está igual no inglês)")
    for k in list(novos)[:12]:
        print(f"  + {k[:90]!r} → {novos[k][:90]!r}")
    for k in r["sem"][:8]:
        print(f"  = {k[:110]!r}")
    if seco or not novos:
        return
    if os.path.getmtime(ARQ) != mtime:
        sys.exit("o en.json mudou durante a conversão: rode de novo")
    d["modelos"].update(novos)
    tmp = ARQ + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, ARQ)
    print(f"gravado: {ARQ} (+{len(novos)} modelos)")


if __name__ == "__main__":
    main()
