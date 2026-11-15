// QUADRA, site final: a jornada (roca.html#/<cod IBGE>/<passo>?respostas).
// Cada passo é um módulo em js/passos/ com: export default { id, titulo, render(el, ctx) }.
// Contrato do ctx: ver web/js/passos/LEIA-ME.md. Fluxo: analise/fluxo/00_FLUXO_FINAL.md (o globo entra direto em #/<cod>/2).
import * as U from "./comum.js";

// As rotas #/<cod>/1..5 não mudam; a ordem da jornada é ORDEM (Sua roça → O plano → Quanto rende → Se secar → Do espaço).
// titulo = pílula no computador; curto = pílula no celular; primario = rótulo do botão verde; volta = rótulo para quem veio de um "mudar".
// Os passos são carregados só quando abertos: um erro num deles não derruba a jornada inteira.
const PASSOS = [
  { id: "lugar", titulo: "Do espaço", curto: "Espaço", primario: "Ver o meu plano →", volta: "Voltar a Do espaço →" },
  { id: "perguntas", titulo: "Sua roça", curto: "Roça", primario: "Ver o meu plano →" },
  { id: "plantio", titulo: "O plano", curto: "Plano", primario: "Quanto rende →", volta: "Voltar ao plano →" },
  { id: "dinheiro", titulo: "Quanto rende", curto: "Dinheiro", primario: "E se secar? →", volta: "Voltar a Quanto rende →" },
  { id: "seguranca", titulo: "Se secar", curto: "Seca", primario: "Mandar no WhatsApp", volta: "Voltar a Se secar →" },
];
const ORDEM = [2, 3, 4, 5, 1];
const modulos = {};
const espera = (ms) => new Promise((ok) => setTimeout(ok, ms));
// pedido recusado (internet fraca ou servidor ocupado): tenta de novo uma vez, como os extras (comum.js)
const importar = (url) => import(url).catch(() => espera(400).then(() => import(`${url}?de-novo=1`)));
const carregarPasso = (id) => (modulos[id] ||= importar(`./passos/${id}.js`).then((m) => m.default)
  .catch((e) => { delete modulos[id]; throw e; }));
// o jeito de hoje em 1 linha na ficha (o mesmo módulo do passo 2 e do passo 4); se falhar, a ficha só mostra o tamanho
const HI = importar("./extras/hoje_ideal.js").catch(() => null);
// "o que é?": balão das palavras técnicas (ponto 2); se não carregar, a jornada segue sem ele
const GLOSSARIO = importar("./extras/glossario.js").catch(() => null);

// Respostas do agricultor. "" = não sei / não respondeu (vale o padrão). Só o que difere do padrão vai para a URL.
export const PADRAO = { terra: "", ha: "", baixio: "", agua: "", vol: "", maniva: "", criacao: "", prioridade: "", gs: "", raiz: "", custo: "",
  hoje: "", area_un: "", antes: "", exp: "" }; // jeito de hoje, unidade da área, o que plantou antes e a experiência (não vão para a API)
const TERRA = { arenosa: { textura: "1", ad: "12" }, mista: { textura: "2", ad: "13" }, barro: { textura: "3", ad: "15" } };
const BAIXIO_FRAC = { nao: 0, pouco: 0.2, terco: 1 / 3, metade: 0.5, "": 1 / 3 };

const cache = new Map();
let estado = { cod: null, passo: 2, resp: { ...PADRAO } };
let pedido = 0;
// "mudar" (data-editar): o passo de onde a pessoa saiu e a linha de "Sua roça" que ela quer mudar. Vivem só nesta página:
// recarregar cai no padrão ("Ver o meu plano").
let volta = null, foco = null;
let primario = null; // { rotulo, fn } do botão verde da tela que está à vista
let ctxAtual = null;
let deNovo = false; // a API falhou e já foi tentada de novo uma vez (volta a false quando carrega)

function lerHash() {
  let h = location.hash.replace(/^#\/?/, "");
  try { h = decodeURIComponent(h); } catch (_) { /* link cortado ou digitado ("%" solto): lê como veio */ }
  const [caminho, busca = ""] = h.split("?");
  const [cod, passo] = caminho.split("/");
  const q = new URLSearchParams(busca);
  const resp = { ...PADRAO };
  for (const k of Object.keys(PADRAO)) if (q.has(k)) resp[k] = q.get(k);
  return { cod: /^\d{7}$/.test(cod || "") ? cod : null, passo: Math.min(5, Math.max(1, +passo || 2)), resp };
}

function escreverHash(e) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(e.resp)) if (v !== "" && v !== PADRAO[k]) q.set(k, v);
  const s = q.toString();
  return `#/${e.cod}/${e.passo}${s ? "?" + s : ""}`;
}

/** Parâmetros que mudam o núcleo (o resto o navegador calcula). */
function paramsApi(resp) {
  const p = new URLSearchParams();
  if (TERRA[resp.terra]) { p.set("textura", TERRA[resp.terra].textura); p.set("ad", TERRA[resp.terra].ad); }
  if (resp.baixio === "nao") p.set("baixio", "0");
  else if (["pouco", "terco", "metade"].includes(resp.baixio)) p.set("ad_baixio", "15"); // suposição: o baixio guarda mais água (AD5)
  if (["nao", "plantada"].includes(resp.maniva)) p.set("maniva", resp.maniva);
  return p;
}

async function buscar(cod, resp) {
  const p = paramsApi(resp);
  p.set("cod", cod);
  const chave = p.toString();
  if (!cache.has(chave)) {
    cache.set(chave, fetch(`/api/local?${chave}`).then(async (r) => {
      const j = await r.json();
      if (j.erro) throw new Error(j.erro);
      return j;
    }).catch((e) => { cache.delete(chave); throw e; }));
  }
  return cache.get(chave);
}

/** Respostas com os padrões aplicados (o que os passos devem usar), com a origem de cada valor. */
function efetivas(resp, r) {
  const pad = r.padroes || {};
  const alerta = r.este_ano?.nivel_alerta === "alerta";
  const haResp = parseFloat(String(resp.ha).replace(",", "."));
  const padHa = pad.rocado_ha > 0 ? pad.rocado_ha : (pad.rocado_ha_padrao > 0 ? pad.rocado_ha_padrao : null);
  const area = haResp > 0 ? haResp : (padHa || 1);
  const frac = BAIXIO_FRAC[resp.baixio] ?? 1 / 3;
  return {
    terra: resp.terra || "nao_sei",
    ha: Math.round(area * 100) / 100,
    ha_origem: haResp > 0 ? "resposta" : (pad.rocado_ha > 0 ? "padrão do município (Censo 2017)"
      : padHa ? "padrão da mesorregião (Censo 2017)" : "exemplo (1 ha)"),
    baixio: resp.baixio || "nao_sei",
    tem_baixio: resp.baixio === "nao" ? false : (resp.baixio ? true : null),
    baixio_frac: frac,
    baixio_ha: Math.round(area * frac * 100) / 100,
    agua: resp.agua || "chuva",
    vol_m3: parseFloat(resp.vol) || null,
    maniva: resp.maniva || "tem",
    criacao: resp.criacao || "nao_sei",
    prioridade: resp.prioridade || (alerta ? "garantir" : "equilibrar"),
    prioridade_origem: resp.prioridade ? "resposta" : (alerta ? "padrão em ano de alerta de El Niño" : "padrão"),
    gs: resp.gs || "nao_sei",
    raiz: resp.raiz || "uf_mediana",
    custo: resp.custo || "semente",
  };
}

/** "milho e feijão", "milho, feijão e mandioca" (o jeito de hoje em poucas palavras, para a ficha). */
function culturasTxt(hi, resp, r) {
  if (!hi?.lerHoje || !hi.CULT) return "";
  const n = Object.keys(hi.lerHoje(resp.hoje || "", r.padroes).cult).map((k) => hi.CULT[k].nome.toLowerCase());
  return n.length > 1 ? `${n.slice(0, -1).join(", ")} e ${n[n.length - 1]}` : n[0] || "";
}

/** O botão verde da barra: o rótulo e o que ele faz (o padrão de cada passo; o passo pode trocar com ctx.primario). */
function primarioPadrao(passo) {
  const p = PASSOS[passo - 1];
  const rotulo = passo === 2 && volta ? PASSOS[volta - 1].volta : p.primario;
  const fn = passo === 2 ? () => { location.hash = escreverHash({ ...estado, passo: volta || 3 }); }
    : passo === 5 ? () => import("./extras/leve_ao_tecnico.js")
      .then((m) => (m.compartilhar ? m.compartilhar(ctxAtual) : rolarAoTecnico()))
    : () => { location.hash = escreverHash({ ...estado, passo: passo === 1 ? 3 : passo + 1 }); };
  return { rotulo, fn };
}
function aplicarPrimario() {
  const a = document.getElementById("avancar");
  a.textContent = primario.rotulo;
  a.disabled = false;
}

function desenharCasca(r, ef, hi) {
  const l = r.local;
  document.getElementById("topo-lugar").innerHTML = `${U.ic("pino")} <b>${U.esc(l.municipio)}</b><span> · ${U.esc(l.uf)}</span>`;
  document.title = `QUADRA · ${l.municipio} (${l.uf})`;
  // as pílulas fazem o papel de abas: sem número; a atual acesa e as anteriores (na ORDEM) com ✓
  const pos = ORDEM.indexOf(estado.passo);
  document.getElementById("passos-nav").innerHTML = ORDEM.map((n, i) => {
    const p = PASSOS[n - 1], cls = i === pos ? "atual" : i < pos ? "feito" : "";
    return `<button class="passo-pilula ${cls}" data-ir="${n}" type="button"${i === pos ? ' aria-current="step"' : ""}>${i < pos ? '<i aria-hidden="true">✓</i>' : ""}<span class="longo">${U.esc(p.titulo)}</span><span class="curto">${U.esc(p.curto)}</span></button>`;
  }).join("");
  // ficha em 1 linha nos passos de resultado: "1,0 ha (típico) · milho e feijão · Mudar"
  const cult = culturasTxt(hi, estado.resp, r);
  document.getElementById("ficha").innerHTML = estado.passo >= 3 ? `<div class="ficha-linha">
    <button type="button" data-editar="ha" title="Mudar o tamanho">${U.esc(U.ha(ef.ha))}${ef.ha_origem === "resposta" ? "" : " (típico)"}</button>
    ${cult ? `<span aria-hidden="true">·</span><button type="button" class="ficha-cult" data-editar="hoje" title="Mudar o que planta">${U.esc(cult)}</button>` : ""}
    <span aria-hidden="true">·</span><button type="button" class="ficha-mudar" data-editar="hoje">Mudar</button></div>` : "";
  // no celular a fileira de pílulas pode rolar: a atual fica no meio
  const nav = document.getElementById("passos-nav"), pil = nav.querySelector(".passo-pilula.atual");
  if (pil && nav.scrollWidth > nav.clientWidth) nav.scrollLeft = pil.offsetLeft - (nav.clientWidth - pil.offsetWidth) / 2;
  // a frase do ponto 16 (barra no computador, rodapé no celular) leva às perguntas para o técnico, no passo 5
  const tecnico = escreverHash({ ...estado, passo: 5 });
  document.getElementById("moldura").href = tecnico;
  document.getElementById("decide-fim").href = tecnico;
  // em Sua roça, "← Mapa"; quem veio de um "mudar" volta ao passo de onde saiu (sem gravar o rascunho)
  const v = document.getElementById("voltar"), mapa = estado.passo === 2 && !volta;
  v.innerHTML = mapa ? "← Mapa" : `← <span class="longo">Voltar</span>`;
  v.setAttribute("aria-label", mapa ? "Voltar ao mapa" : "Voltar");
}

async function desenhar() {
  const meu = ++pedido;
  const e = lerHash();
  estado = e;
  if (e.passo !== 2) { volta = null; foco = null; }
  const el = document.getElementById("jornada");
  if (!e.cod) return escolherLugar(el);
  document.body.classList.remove("sem-lugar");
  if (!el.querySelector(".passo-conteudo")) el.innerHTML = `<div class="carregando">Olhando o seu lugar lá de cima</div>`;
  let r, hi, gl;
  try {
    [r, hi, gl] = await Promise.all([buscar(e.cod, e.resp), HI, GLOSSARIO]);
  } catch (err) {
    if (meu !== pedido) return;
    // internet fraca ou servidor ocupado: tenta de novo sozinho uma vez; depois, o verde da barra vira "Tentar de novo"
    // (buscar() já tirou do cache o pedido que falhou)
    if (!deNovo) { deNovo = true; setTimeout(() => { if (meu === pedido) desenhar(); }, 1500); return; }
    el.innerHTML = `<div class="erro">Sem sinal para carregar agora. Confira a internet e toque em Tentar de novo.</div>`;
    primario = { rotulo: "Tentar de novo", fn: () => desenhar() };
    aplicarPrimario();
    return;
  }
  deNovo = false;
  if (meu !== pedido) return;
  const ef = efetivas(e.resp, r);
  const prim = primarioPadrao(e.passo);
  const entrou = el.dataset.passo !== String(e.passo) || el.dataset.cod !== e.cod; // chegou agora a este passo (não é só uma resposta nova)
  const ctx = {
    r, cod: e.cod, passo: e.passo, resp: e.resp, ef, padroes: r.padroes || null, util: U, entrou, volta, foco,
    set: (patch) => { const n = { ...estado, resp: { ...estado.resp, ...patch } }; location.replace(escreverHash(n)); },
    ir: (n) => { location.hash = escreverHash({ ...estado, passo: n }); },
    link: (n, patch = {}) => escreverHash({ ...estado, passo: n, resp: { ...estado.resp, ...patch } }),
    /** O botão verde da barra (um por tela): rótulo (sem rótulo, fica o padrão do passo) e o que ele faz. */
    primario: (rotulo, fn) => {
      if (rotulo) prim.rotulo = rotulo;
      if (fn) prim.fn = fn;
      if (primario === prim) aplicarPrimario();
    },
  };
  gl?.instalar(ctx); // os exemplos do balão passam a usar este município
  const passo = PASSOS[e.passo - 1];
  const caixa = document.createElement("div");
  caixa.className = `passo-conteudo passo-${passo.id}`;
  try {
    const mod = await carregarPasso(passo.id);
    if (meu !== pedido) return;
    await mod.render(caixa, ctx);
  } catch (err) {
    console.error(err);
    caixa.innerHTML = `<div class="erro">Erro ao desenhar o passo "${U.esc(passo.titulo)}": ${U.esc(err.message)}</div>`;
  }
  if (meu !== pedido) return;
  desenharCasca(r, ef, hi);
  el.replaceChildren(caixa);
  el.dataset.passo = String(e.passo);
  el.dataset.cod = e.cod;
  ctxAtual = ctx;
  primario = prim;
  aplicarPrimario();
  if (entrou) window.scrollTo({ top: 0, behavior: "instant" });
  explicarOlho(caixa);
  if (rolarTecnico) { rolarTecnico = false; rolarAoTecnico(); }
  if (rolarAcerto) { rolarAcerto = false; abrirAcerto(); }
}

/** "Quanto o cálculo já acertou" (Do espaço): abre o "ver mais" dos 7 jeitos testados no passo 5 e rola até ele. */
let rolarAcerto = false;
function abrirAcerto() {
  const d = document.getElementById("seg-acerto");
  if (!d) return;
  d.open = true;
  window.scrollTo({ top: d.getBoundingClientRect().top + scrollY - 104, behavior: "instant" }); // abaixo do topo fixo
}

/** O 1º "seu olho" à vista de cada passo vira "o que é?" (no toque não há title): abre o balão do glossário. */
function explicarOlho(caixa) {
  const rot = [...caixa.querySelectorAll(".olho-rot")].find((e) => !e.closest("details:not([open]), button, a, summary"));
  if (!rot) return;
  rot.classList.add("gl-termo");
  Object.entries({ role: "button", tabindex: "0", "data-gl": "seu_olho", "aria-expanded": "false", "aria-controls": "gl-balao", title: "O que é?" })
    .forEach(([k, v]) => rot.setAttribute(k, v));
}

let rolarTecnico = false;
function rolarAoTecnico() {
  const alvo = document.querySelector('[data-extra="leve_ao_tecnico"]');
  if (alvo) alvo.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function escolherLugar(el) {
  document.body.classList.add("sem-lugar");
  document.getElementById("passos-nav").innerHTML = "";
  document.getElementById("ficha").innerHTML = "";
  document.getElementById("topo-lugar").innerHTML = "";
  const ex = [["2311306", "Quixadá (CE)"], ["2208007", "Picos (PI)"], ["2611101", "Petrolina (PE)"], ["2700300", "Arapiraca (AL)"], ["2903201", "Barreiras (BA)"]];
  el.innerHTML = `<div class="titulo-passo"><p class="kicker">Nordeste do Brasil · da órbita pro campo</p>
    <h1>Qual é o seu município?<span class="eco">A gente olha lá de cima.</span></h1></div>
    <div class="cartao"><input id="busca-mun" list="lista-mun" placeholder="Digite o município…" style="width:100%;max-width:460px;padding:14px 16px;border:1px solid var(--border-2);border-radius:14px;font-size:17px;background:rgba(255,255,255,.04);color:var(--ink)">
    <datalist id="lista-mun"></datalist>
    <p class="sub">Ou toque num exemplo: ${ex.map(([c, n]) => `<a href="#/${c}/2">${n}</a>`).join(" · ")} · <a href="index.html">ver no globo</a></p></div>`;
  let lista = [];
  try {
    const r = await fetch("dados/busca_municipios.json");
    if (!r.ok) throw new Error();
    const j = await r.json();
    lista = (Array.isArray(j) ? j : j.municipios || []).map((m) => ({ nome: `${m.nome} (${m.uf})`, cod: String(m.cod) }));
  } catch (_) {
    const gj = await (await fetch("/api/municipios")).json();
    lista = gj.features.map((f) => ({ nome: `${f.properties.nome} (${f.properties.uf})`, cod: String(f.properties.cod) }));
  }
  lista.sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
  document.getElementById("lista-mun").innerHTML = lista.map((m) => `<option value="${U.esc(m.nome)}"></option>`).join("");
  document.getElementById("busca-mun").addEventListener("change", (ev) => {
    const m = lista.find((x) => x.nome === ev.target.value);
    if (m) location.hash = `#/${m.cod}/2`;
  });
}

// ---------------------------------------------------------------- balão da fonte do selo (no toque não há title)
let balaoTempo = 0;
function mostrarFonte(s) {
  const fonte = s.dataset.fonte || s.getAttribute("title") || "";
  if (!fonte) return;
  let b = document.getElementById("selo-balao");
  if (!b) {
    b = document.createElement("div");
    b.id = "selo-balao";
    b.className = "selo-balao";
    b.setAttribute("role", "status");
    document.body.appendChild(b);
  }
  b.innerHTML = `<b>${U.esc(s.textContent.trim())} · de onde vem</b>${U.esc(fonte)}`;
  b.hidden = false;
  const rs = s.getBoundingClientRect(), w = b.offsetWidth, h = b.offsetHeight;
  const x = Math.max(12, Math.min(innerWidth - w - 12, rs.left + rs.width / 2 - w / 2));
  const y = rs.bottom + 8 + h < innerHeight - 72 ? rs.bottom + 8 : Math.max(8, rs.top - h - 8);
  b.style.left = `${x}px`;
  b.style.top = `${y}px`;
  clearTimeout(balaoTempo);
  balaoTempo = setTimeout(esconderFonte, 5000);
}
function esconderFonte() {
  const b = document.getElementById("selo-balao");
  if (b) b.hidden = true;
}
window.addEventListener("scroll", esconderFonte, { passive: true });
document.addEventListener("keydown", (ev) => {
  const s = ev.target.closest?.(".selo");
  if (s && (ev.key === "Enter" || ev.key === " ")) { ev.preventDefault(); mostrarFonte(s); }
});

document.addEventListener("click", (ev) => {
  const s = ev.target.closest(".selo");
  if (s) {
    if (s.closest("summary")) ev.preventDefault(); // o toque no selo mostra a fonte, não abre o "ver mais"
    return mostrarFonte(s);
  }
  esconderFonte();
  if (!estado.cod) return;
  const ed = ev.target.closest("[data-editar]");
  if (ed) { // "mudar": abre Sua roça na linha certa e guarda a volta
    ev.preventDefault();
    foco = ed.dataset.editar;
    if (estado.passo === 2) return document.getElementById(`linha-${foco}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
    volta = estado.passo;
    location.hash = escreverHash({ ...estado, passo: 2 });
    return;
  }
  const ac = ev.target.closest("[data-acerto]");
  if (ac) { ev.preventDefault(); rolarAcerto = true; location.hash = escreverHash({ ...estado, passo: 5 }); return; }
  const b = ev.target.closest("[data-ir]");
  if (b) { ev.preventDefault(); volta = null; irCom(+b.dataset.ir); return; }
  const m = ev.target.closest("#moldura, #decide-fim");
  if (m) {
    ev.preventDefault();
    if (estado.passo === 5) return rolarAoTecnico();
    rolarTecnico = true;
    irCom(5);
  }
});
/** Vai a outro passo pela pílula ou pelo rodapé. Saindo de Sua roça, leva junto o que foi tocado (ctx.pendente de perguntas.js):
 *  as pílulas fazem o papel de abas, e o rascunho não pode se perder sem aviso. */
function irCom(n) {
  const p = (estado.passo === 2 && ctxAtual?.passo === 2 && ctxAtual.pendente?.()) || {};
  const resp = { ...estado.resp, ...p };
  if (Object.keys(p).length) location.replace(escreverHash({ ...estado, resp })); // o voltar reabre Sua roça como ficou
  location.hash = escreverHash({ ...estado, passo: n, resp });
}
document.getElementById("voltar").addEventListener("click", () => {
  if (estado.cod && estado.passo === 2 && volta) { volta = null; history.back(); return; } // veio de um "mudar": volta sem gravar
  if (!estado.cod || estado.passo === 2) { location.href = "index.html"; return; }
  volta = null;
  location.hash = escreverHash({ ...estado, passo: ORDEM[ORDEM.indexOf(estado.passo) - 1] });
});
// um toque só: o verde se desliga até a tela mudar (se a tela não mudar, como no WhatsApp, volta a ligar). Com a API em cache a
// tela nova chega em 20–60 ms e o verde dela já está ligado: o 2º toque de um toque duplo (até 700 ms) é ignorado.
let ultimoToque = 0;
document.getElementById("avancar").addEventListener("click", (ev) => {
  const a = ev.currentTarget, agora = performance.now();
  if (a.disabled || agora - ultimoToque < 700 || !primario || !estado.cod) return;
  ultimoToque = agora;
  a.disabled = true;
  const antes = location.hash, liga = () => setTimeout(() => { if (location.hash === antes) a.disabled = false; }, 800);
  Promise.resolve().then(primario.fn).catch((err) => console.error(err)).finally(liga);
});
window.addEventListener("hashchange", desenhar);
desenhar();
