// QUADRA, módulo extra "O que cada planta faz pelo seu solo" (ponto 10 do desafio).
// 4 cartões (fixa nitrogênio · cobre o chão · raiz funda · aguenta a seca): as culturas DO PLANO deste município que fazem aquilo,
// 1 número com o grau da evidência (catálogo do conselho, via ferramentas/preparar_saude_solo.py → dados/saude_solo.json) e,
// no "De onde vem", o id do cartão do catálogo. Embaixo, a conta do plano: "em 3 anos, parte por parte" (leguminosa, palhada, raiz funda).
// Uso: import m from "./extras/saude_solo.js"; await m.render(el, ctx, { titulo: true, longo: true });
import * as U from "../comum.js";

const URL_DADOS = new URL("../../dados/saude_solo.json", import.meta.url); // = dados/saude_solo.json ao lado de roca.html
let cache = null;
const carregar = () => (cache ??= fetch(URL_DADOS).then((r) => (r.ok ? r.json() : null)).catch(() => null)
  .then((d) => { if (!d) cache = null; return d; }));

// o que cada papel é; a evidência de cada um vem do JSON (sem o JSON, o cartão mostra só o papel e as culturas)
const PAPEIS = [
  { id: "fixa", kicker: "Fixa nitrogênio", icone: "feijao", cor: "t-leguminosa", chaves: ["caupi", "feijao", "amendoim", "guandu", "gliricidia", "mucuna"] },
  { id: "cobre", kicker: "Cobre o chão", icone: "chuva", cor: "t-cereal", chaves: ["milho", "sorgo", "milheto", "mucuna"] },
  { id: "raiz", kicker: "Raiz funda", icone: "mandioca", cor: "t-tampao", chaves: ["mandioca", "guandu", "gliricidia"] },
  { id: "seca", kicker: "Aguenta a seca", icone: "sol", cor: "t-forragem", chaves: ["sorgo", "milheto", "mandioca", "palma", "guandu", "gliricidia"] },
];
const COLUNAS = [["fixa", "leguminosa"], ["cobre", "palhada"], ["raiz", "raiz funda"]]; // a conta "em 3 anos"

const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);
const faz = (papel, cultura) => papel.chaves.some((k) => norm(cultura).includes(k));

/** Culturas de uma célula do plano: "Palma + gliricídia" → 2; o feijão que entra no milho do baixio ("+ feijão-caupi em revezamento") conta. */
function culturasCel(c) {
  const out = String(c.cultura || "").split(/\s*\+\s*/).filter(Boolean).map(cap);
  const m = /^\+\s*(.+?)\s+em revezamento/.exec(c.texto || "");
  if (m) out.push(cap(m[1]));
  return out;
}

/** Dias de uma janela do ZARC ("11/03–20/04; 21/11–20/12"); "nenhum" = 0; sem ZARC = null. */
const DIA0 = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
function dias(s) {
  if (s === null || s === undefined || s === "—") return null;
  if (s === "nenhum") return 0;
  let tot = 0;
  for (const tr of String(s).split(";")) {
    const m = /^(\d{2})\/(\d{2})\s*[–-]\s*(\d{2})\/(\d{2})$/.exec(tr.trim());
    if (!m) return null;
    const a = DIA0[+m[2] - 1] + +m[1], b = DIA0[+m[4] - 1] + +m[3];
    tot += (b >= a ? b - a : b + 365 - a) + 1;
  }
  return tot;
}

/** Sorgo ou milheto do plano contra o milho, na janela de risco baixo (20%) do ZARC daqui. Só vale se o tolerante ganhar. */
function zarcSeca(cardapio, culturas) {
  const cd = new Map((cardapio || []).map((c) => [c.cultura, c]));
  const milho = dias(cd.get("Milho")?.risco20);
  let melhor = null;
  for (const nome of ["Sorgo forrageiro", "Sorgo granífero", "Milheto"]) {
    const d = culturas.includes(nome) ? dias(cd.get(nome)?.risco20) : null;
    if (d !== null && (!melhor || d > melhor.d)) melhor = { nome, d };
  }
  if (!melhor || milho === null || melhor.d <= milho) return null;
  return { dias: String(melhor.d), cultura: melhor.nome.toLowerCase(), milho: milho ? `${milho} dias` : "nenhum dia" };
}

const preencher = (s, z) => String(s || "").replace(/\{(\w+)\}/g, (_, k) => (z && z[k] !== undefined ? z[k] : ""));

function prova(e, d) {
  if (!e) return "";
  if (!e.grau) return `<div class="ss-prova">${U.ic("pino")}<span>${U.esc(e.prova || "")}</span></div>`;
  const n = d.graus[e.grau] || 0;
  return `<div class="ss-prova" title="${U.esc(d.grau_txt)}"><span class="ss-grau" aria-hidden="true">${[1, 2, 3, 4]
    .map((i) => `<i${i <= n ? ' class="on"' : ""}></i>`).join("")}</span>
    <span>evidência ${U.esc(e.grau)} · ${U.esc(d.transf[e.transf] || "")}${e.onde ? ", " + U.esc(e.onde) : ""}</span></div>`;
}

function deOndeVem(j, d, extras) {
  const fonte = (f) => `<p class="ss-fonte">${U.esc(f.diz)}<br><span class="pequeno"><code>${U.esc(f.id)}</code>${f.grau
    ? ` · grau ${U.esc(f.grau)}·${U.esc(f.transf)} (${U.esc(d.transf[f.transf] || "")})` : ""}${f.onde ? " · " + U.esc(f.onde) : ""}${f.ref
    ? " · " + U.esc(f.ref) : ""}${f.doi ? ` · <a href="https://doi.org/${U.esc(f.doi)}" target="_blank" rel="noopener">doi</a>` : ""}</span></p>`;
  return (j.fontes || []).map(fonte).join("")
    + (j.nota ? `<p>${U.esc(j.nota)}</p>` : "")
    + (extras.length ? `<p>No cardápio daqui também: ${U.esc(extras.join(", "))}.</p>` : "")
    + (j.decide ? `<p class="ss-decide">${U.ic("enxada")}<span><b>Você decide:</b> ${U.esc(j.decide)}</span></p>` : "");
}

function cartao(papel, j, d, culturas, onde, extras, cond) {
  const e = j ? j.efeitos.find((x) => x.quando === "sempre" || (x.quando === "leg_grao" && cond.legGrao) || (x.quando === "zarc" && cond.zarc)) : null;
  const z = e && e.quando === "zarc" ? cond.zarc : null;
  const chips = culturas.length
    ? culturas.map((c) => `<span class="chip" title="${U.esc(c + ": " + onde.get(c).join(", "))}">${U.ic(U.icCultura(c))}${U.esc(c)}</span>`).join("")
    : `<span class="ss-nada">nenhuma no plano daqui</span>`;
  return `<article class="ss-cartao ${papel.cor}">
    <div class="ss-topo"><span class="ss-bola">${U.ic(papel.icone)}</span><span class="ss-kicker">${U.esc(papel.kicker)}</span>${e ? U.selo(e.selo, e.selo_fonte) : ""}</div>
    ${e ? `<div class="ss-corpo"><div class="ss-val">${U.esc(preencher(e.val, z))}${e.un ? `<small>${U.esc(e.un)}</small>` : ""}</div>
    <p class="ss-sub">${U.esc(preencher(e.sub, z))}</p></div>` : ""}
    <div class="ss-chips"><span class="ss-rot">No seu plano</span>${chips}</div>
    ${prova(e, d)}
    ${j ? U.verMais(deOndeVem(j, d, extras), "De onde vem") : ""}
  </article>`;
}

// ------------------------------------------------------------------ em 3 anos, parte por parte
const anosTxt = (n) => (n === 1 ? "1 ano" : `${n} anos`);
const partesTxt = (ls) => {
  const l = ls.map((x) => x.parte.replace(/^Parte /, ""));
  return l.length === 1 ? `a parte ${l[0]} fica` : `as partes ${l.slice(0, -1).join(", ")} e ${l[l.length - 1]} ficam`;
};

/** Uma frase, só com as partes que giram (A, B, C): "cada parte recebe 1 ano de leguminosa e 2 de palhada" ou onde falta. */
function fraseLongo(rot, conta) {
  const papel = (id, rotulo) => {
    const n = rot.map((l) => conta(l, id));
    if (n.every((x) => x === n[0])) return { igual: true, n: n[0], rotulo };
    const zero = rot.filter((_, i) => n[i] === 0);
    return { txt: zero.length ? `${partesTxt(zero)} sem ${rotulo}` : `toda parte recebe ${rotulo} ao menos 1 ano` };
  };
  const L = papel("fixa", "leguminosa"), P = papel("cobre", "palhada");
  const uma = (x) => (x.txt || (x.n === 0 ? `nenhuma parte recebe ${x.rotulo}` : `cada parte recebe ${anosTxt(x.n)} de ${x.rotulo}`));
  if (L.igual && P.igual && L.n > 0) return `Em 3 anos, cada parte recebe ${anosTxt(L.n)} de leguminosa e ${P.n || "nenhum"} de palhada.`;
  if (L.igual && P.igual && L.n === 0 && P.n === 0) return "Em 3 anos, nenhuma parte recebe leguminosa nem palhada.";
  return `Em 3 anos, ${uma(L)}; ${uma(P)}.`;
}

function blocoLongo(linhas, anos, d) {
  const papel = Object.fromEntries(PAPEIS.map((p) => [p.id, p]));
  const tem = (a, id) => a.cs.some((c) => faz(papel[id], c));
  const conta = (l, id) => l.anos.filter((a) => tem(a, id)).length;
  const rot = linhas.filter((l) => /^Parte /.test(l.parte));
  const frase = rot.length ? fraseLongo(rot, conta) : "";
  const cab = COLUNAS.map(([id, r]) => `<span class="ss-cab ${papel[id].cor}"><i></i>${r}</span>`).join("");
  const filas = linhas.map((l) => `<span class="ss-parte">${U.esc(l.parte)}</span>` + COLUNAS.map(([id, r]) =>
    `<span class="ss-pips ${papel[id].cor}" role="img" aria-label="${U.esc(`${l.parte}, ${r}: ${conta(l, id)} de ${anos.length} anos`)}">${l.anos
      .map((a) => `<i${tem(a, id) ? ' class="on"' : ""} title="${U.esc(`${a.ano}: ${a.cs.join(" + ")}`)}"></i>`).join("")}</span>`).join("")).join("");
  const mais = d ? U.verMais(`<p>${U.esc(d.longo.regra)}</p>${deOndeVem({ fontes: d.longo.fontes }, d, [])}
    <p class="pequeno">Catálogo: ${U.esc(d.fonte)}. ${U.esc(d.grau_txt)}</p>`, "Como contamos") : "";
  return `<div class="ss-longo">
    <div class="ss-topo">${U.ic("calendario")}<span class="ss-kicker">Em 3 anos, parte por parte</span>${U.selo("projecao",
      `conta os anos do plano ${anos[0]}–${anos[anos.length - 1]}, se o plano for seguido`)}</div>
    ${frase ? `<p class="ss-frase">${U.esc(frase)}</p>` : ""}
    <div class="ss-mat"><span></span>${cab}${filas}</div>
    ${mais}
  </div>`;
}

// ------------------------------------------------------------------ módulo
export default {
  id: "saude_solo",
  /** opcoes: titulo (rótulo do bloco, padrão true) e longo (a conta "em 3 anos", padrão true). */
  async render(el, ctx, opcoes = {}) {
    const { titulo = true, longo = true } = opcoes;
    const r = ctx.r || {}, p = r.plano;
    if (!p || !p.faixas || !p.faixas.length) { el.innerHTML = ""; return; }
    const d = await carregar();

    const faixas = p.faixas.filter((f) => !(f.parte === "Baixio" && ctx.ef && ctx.ef.tem_baixio === false));
    const linhas = faixas.map((f) => ({ parte: f.parte, anos: f.anos.map((c, k) => ({ ano: p.anos[k], cs: culturasCel(c) })) }));
    const onde = new Map(); // cultura → partes onde aparece (na ordem do plano)
    for (const l of linhas) for (const a of l.anos) for (const c of a.cs) {
      if (!onde.has(c)) onde.set(c, []);
      if (!onde.get(c).includes(l.parte)) onde.get(c).push(l.parte);
    }
    const doPlano = [...onde.keys()];
    const cond = {
      legGrao: doPlano.some((c) => /caupi|feijao|amendoim/.test(norm(c))),
      zarc: zarcSeca(r.cardapio, doPlano),
    };
    const noPlano = (c) => doPlano.some((x) => norm(c).includes(norm(x)) || norm(x).includes(norm(c)));
    const cardapio = (r.cardapio || []).filter((c) => ["indicada", "só aptidão", "literatura"].includes(c.situacao) && !noPlano(c.cultura));
    const porId = Object.fromEntries(((d && d.papeis) || []).map((j) => [j.id, j]));

    const cartoes = PAPEIS.map((papel) => cartao(papel, d ? porId[papel.id] : null, d, doPlano.filter((c) => faz(papel, c)), onde,
      cardapio.filter((c) => faz(papel, c.cultura)).map((c) => c.cultura.toLowerCase()), cond)).join("");
    el.innerHTML = `<section class="painel ss">
      ${titulo ? `<h3 class="ss-titulo">O que cada planta faz pelo seu solo</h3>` : ""}
      <div class="ss-cartoes">${cartoes}</div>
      ${longo ? blocoLongo(linhas, p.anos, d) : ""}
    </section>`;
  },
};
