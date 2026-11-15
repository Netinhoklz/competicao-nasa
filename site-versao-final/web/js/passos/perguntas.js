// Passo 2, "Sua roça": uma tela só, com as linhas já marcadas com o comum daqui (o que planta, tamanho, terra, baixio, maniva e o ano
// passado). Cada toque muda só o rascunho da tela: não grava, não chama a API e não avança. O primário da barra ("Ver o meu plano →",
// ou "Voltar a <passo> →" para quem veio de um "mudar") grava uma vez só, e só as linhas tocadas.
// Ordem de serviço: analise/fluxo/00_FLUXO_FINAL.md (seções 3.1 e 7) e, na rodada 2 (15/11), analise/fluxo2/BRIEFING.md (D2):
// a lista completa das culturas ("Ver todas as culturas"), o tamanho em metros à vista (grava ha, area_un, larg e comp), o baixio
// explicado com um desenho, e a maniva e o ano passado, que saíram do Plano.
// A lista das culturas mora em extras/culturas.js; "em tarefas ou passos" abre extras/area.js; o ano passado usa o formato de `antes`
// de extras/historico.js; a terra usa as palavras do Vicente (interface-inicial-vicente). Os modos "pergunta" de hoje_ideal.js e
// historico.js ficam no código (páginas de teste), fora da jornada.
import { olho, OLHOS } from "../extras/voce_decide.js";
import { lerHoje, CULT, igual, mexer, opcoesCultura } from "../extras/hoje_ideal.js";
import { GRUPOS, TODAS, foraDaqui, noCardapio } from "../extras/culturas.js";
import AREA, { tarefaPadrao, haDe, metrosDe, escreverArea } from "../extras/area.js";
import { CULT_H, lerAntes, escreverAntes, ANO_HOJE, icHist } from "../extras/historico.js";

const TERRAS = [["arenosa", "areia", "Seca rápido"], ["mista", "gota", "Segura a umidade"], ["barro", "barro", "Encharca"],
  ["", "interrog", "Não sei"]];
const BAIXIOS = [["nao", 0, "Não tenho"], ["pouco", 0.2, "Pequeno"], ["metade", 0.5, "Grande"], ["", null, "Não sei"]];
const TERCO = ["terco", 1 / 3, "Um terço"]; // só para quem chega por um link antigo (…?baixio=terco)
const MANIVAS = [["tem", "Tenho"], ["plantada", "Já está plantada"], ["nao", "Não tenho"], ["", "Não sei"]];
const HAS = [0.5, 1, 2, 3, 5];
const MAX_M = 5000; // o lado mais comprido que a tela aceita (5 km)
const FONTE_TIPICO = "típico do município no Censo Agropecuário 2017 (IBGE), aplicado ao seu roçado";
const FONTE_ZON = "ZARC/MAPA 2026/27 e FAO GAEZ v4, no cardápio do QUADRA para o município";

// mini-desenho do roçado visto de cima, com o baixio embaixo (fração f; null = tracejado "não sei")
const miniRocado = (f) => `<svg class="mini-rocado" viewBox="0 0 60 60" aria-hidden="true">
  <rect x="2" y="2" width="56" height="56" rx="4" class="mr-terra"/>
  ${f === null ? `<rect x="2" y="38" width="56" height="20" rx="4" class="mr-baixio incerto"/>`
    : f > 0 ? `<rect x="2" y="${58 - 56 * f}" width="56" height="${56 * f}" rx="4" class="mr-baixio"/>` : ""}</svg>`;

// o roçado de lado: a chuva cai no alto, a água escorre e para no baixio, que fica úmido
const PERFIL = `<svg class="sr-perfil" viewBox="0 0 320 64" role="img" aria-label="O roçado visto de lado: a água da chuva desce do alto e para no baixio">
  <path class="sp-chuva" d="M34 4l-3 7M52 2l-3 7M70 4l-3 7M88 2l-3 7"/>
  <path class="sp-terra" d="M0 22 C70 20 112 21 142 27 C178 34 196 48 228 50 L320 50 L320 64 L0 64 Z"/>
  <path class="sp-umida" d="M214 48.6 C220 49.5 224 50 228 50 L320 50 L320 64 L204 64 Z"/>
  <path class="sp-poca" d="M232 50 H316"/>
  <path class="sp-agua" d="M118 18 C150 21 172 30 198 42"/><path class="sp-agua" d="M192 35 l7 7.5 -9.5 1.6"/>
  <text class="sp-rot" x="44" y="40">alto</text><text class="sp-rot" x="274" y="44">baixio</text></svg>`;

let rasc = null; // o rascunho da tela: { cult, ha, area_un, larg, comp, ml, mc, terra, baixio, maniva, antes }
let tocado = new Set(); // linhas que a pessoa tocou: só elas vão para a URL
let abertos = new Set(); // "quanto de cada", "ver todas" e "em tarefas ou passos" abertos (sobrevivem ao redesenho)
let areaNova = true; // a 1ª montagem de area.js depois de chegar zera o estado dele

const tipicoHa = (pad) => (pad?.rocado_ha > 0 ? pad.rocado_ha : pad?.rocado_ha_padrao > 0 ? pad.rocado_ha_padrao : null);
const lerHa = (s) => { const v = parseFloat(String(s ?? "").replace(",", ".")); return v > 0 ? v : null; };
const metro = (s) => { const v = Math.round(parseFloat(String(s ?? "").replace(",", "."))); return v > 0 ? Math.min(MAX_M, v) : null; };
const txtHa = (v) => String(Math.max(0.0001, Math.round(v * 1e4) / 1e4)); // 0.4 → "0.4"; 5 × 5 m → "0.0025" (ponto: vai para a URL)
/** A área para ler, como o haTxt de extras/terreno.js (o Plano): abaixo de 0,1 ha em m² (20 × 20 m → "400 m²"), abaixo de 1 ha com 2
 *  casas (30 × 50 m → "0,15 ha"), e o U.ha de sempre a partir de 1 ha. O U.ha sozinho escreve "0 ha" para 20 × 20 m. */
const areaTxt = (U, v) => (v < 0.1 ? `${U.num(v * 1e4 >= 100 ? Math.round(v * 1e3) * 10 : Math.round(v * 1e4))} m²`
  : v < 0.995 ? `${U.num(v, 2).replace(/0$/, "")} ha` : U.ha(v));
const tarefasTxt = (U, n) => (n < 0.1 ? "menos de 0,1 tarefa" : `≈ ${n >= 2 ? Math.round(n) : U.num(n, 1)} tarefa${n >= 1.5 ? "s" : ""}`);
// as setinhas dos lados do roçado: a largura vai de lado; o comprimento vai do alto até embaixo, para onde a água desce (o desenho do Plano)
const SETA_LADO = `<svg class="sr-m-seta" viewBox="0 0 24 12" aria-hidden="true"><path d="M2 6h20M6 2 2 6l4 4M18 2l4 4-4 4"/></svg>`;
const SETA_DESCE = `<svg class="sr-m-seta desce" viewBox="0 0 12 24" aria-hidden="true"><path d="M6 2v20M2 18l4 4 4-4"/></svg>`;
const mesmaDivisao = (a, b) => Object.keys(a).length === Object.keys(b).length && Object.keys(a).every((k) => a[k] === b[k]);
const listaNomes = (ks) => { const n = ks.map((k) => CULT[k].nome); return n.length > 1 ? `${n.slice(0, -1).join(", ")} e ${n.at(-1)}` : n[0]; };
/** O ano que "o ano passado" pergunta: o do jeito de hoje (2026, a safra antes do plano de 2027) menos 1. */
const anoPassado = (r) => (r.plano?.anos?.[0] ? r.plano.anos[0] - 1 : ANO_HOJE) - 1;

/** Largura × comprimento da resposta (metros inteiros): larg e comp, ou a medida de area_un que ainda bate com o ha gravado. */
function medidaIni(resp, uf) {
  const L = metro(resp.larg), C = metro(resp.comp);
  if (L && C) return { larg: L, comp: C };
  const m = metrosDe(resp.area_un), h = haDe(resp.area_un, uf), ha = lerHa(resp.ha);
  return m && h && ha && Math.abs(h - ha) / ha < 0.02 ? m : null;
}

/** `hoje` com as culturas novas; quem já tinha outras chaves (|cons=…) fica com as dele (o padrão não vira resposta). */
function hojeTxt(cult, antigo) {
  const cs = Object.keys(CULT).filter((k) => cult[k] > 0).map((k) => `${k}:${cult[k]}`).join(",");
  return [cs, ...String(antigo || "").split("|").slice(1).filter(Boolean)].join("|");
}

/** A maniva que a tela mostra e grava: a tocada; senão, marcar a mandioca supõe que ela já está no chão (e desmarcar desfaz). */
function manivaTela(ctx) {
  const resp = ctx.resp;
  if (tocado.has("maniva")) return rasc.maniva;
  const tinha = "mandioca" in lerHoje(resp.hoje || "", ctx.r.padroes).cult, tem = "mandioca" in rasc.cult;
  if (tem && !tinha && !resp.maniva) return "plantada";
  if (!tem && tinha && resp.maniva === "plantada") return "";
  return resp.maniva || "";
}

/** O que vai para a URL: só as linhas tocadas, e só o que mudou de fato. */
function patch(ctx) {
  const resp = ctx.resp, p = {};
  if (tocado.has("hoje") && !mesmaDivisao(lerHoje(resp.hoje || "", ctx.r.padroes).cult, rasc.cult)) p.hoje = hojeTxt(rasc.cult, resp.hoje);
  const mv = manivaTela(ctx);
  if (mv !== (resp.maniva || "")) p.maniva = mv;
  for (const [k, linha] of [["ha", "ha"], ["area_un", "ha"], ["larg", "ha"], ["comp", "ha"], ["terra", "terra"], ["baixio", "baixio"], ["antes", "antes"]]) {
    if (tocado.has(linha) && (rasc[k] || "") !== (resp[k] || "")) p[k] = rasc[k] || "";
  }
  return p;
}

/** As janelas de plantar de agora ({cod, jan: {cultura: "dd/mm a dd/mm"}}), para o "era dd/mm" do passo 3 (só neste município). */
function guardarAntes(ctx, p) {
  try {
    if (!Object.keys(p).length) return sessionStorage.removeItem("quadra.antes");
    const jan = (ctx.r.agenda?.culturas || []).map((c) => [c.cultura, String(c.plantar || "").split(" (")[0].replace(/^de /, "").replace(/\/20\d\d/g, "")]);
    sessionStorage.setItem("quadra.antes", JSON.stringify({ cod: ctx.cod, jan: Object.fromEntries(jan.filter(([, v]) => v)) }));
  } catch (_) { /* sem sessionStorage: o passo 3 só não mostra o "antes" */ }
}

/** Faixa de 1 linha: El Niño de 2027 e o solo de hoje. */
function faixa(r, U) {
  const e = r.este_ano || {}, sm = e.smap?.status === "ok" ? e.smap : null;
  const nino = e.oni >= 1.5 ? "El Niño forte" : e.oni >= 0.5 ? "El Niño" : "";
  const solo = sm ? String(sm.classe || "").replace(/ para a época$/, "") : "";
  if (!nino && !solo) return "";
  const fonte = [sm && `Solo: NASA SMAP L4, umidade na raiz nos 30 dias até ${U.dataBR(sm.fim)} (posição ${sm.posto} de ${sm.anos} anos; 1 = o mais seco)`,
    nino && `El Niño: índice ONI da NOAA, mar ${U.num(e.oni, 1)} °C acima do normal`].filter(Boolean).join(". ");
  const txt = [nino && `2027: ${nino}`, solo && `solo hoje ${solo}`].filter(Boolean).join(", ");
  return `<p class="sr-faixa ${e.nivel_alerta === "alerta" ? "" : "azul"}">${U.ic("onda")}<span>${U.esc(txt)}</span>${U.selo("medido", fonte)}</p>`;
}

const botao = (attr, marcado, corpo, cls = "") =>
  `<button type="button" class="sr-op ${cls} ${marcado ? "marcada" : ""}" ${attr} aria-pressed="${marcado}">${corpo}</button>`;

function desenhar(el, ctx) {
  const U = ctx.util, r = ctx.r, pad = r.padroes || {}, uf = r.local?.uf;
  const ks = Object.keys(rasc.cult);
  const tip = tipicoHa(pad), haResp = lerHa(rasc.ha), haV = haResp || tip || 1;
  const tarefas = tarefasTxt(U, (haV * 10000) / tarefaPadrao(uf));
  const deOnde = pad.rocado_ha > 0 ? "típico daqui" : tip ? "típico da região" : "exemplo";
  const baixios = [...BAIXIOS];
  if (rasc.baixio === "terco" || ctx.resp.baixio === "terco") baixios.splice(2, 0, TERCO);
  const det = (k, titulo, corpo, cls = "") => `<details class="ver-mais sr-mais ${cls}" data-k="${k}"${abertos.has(k) ? " open" : ""}><summary>${titulo}</summary>${corpo}</details>`;

  // ---- o que planta hoje: as mais comuns à vista + a lista completa; a barra colorida da divisão abre o "quanto de cada"
  const barra = `<span class="hi-divisao sr-divisao" role="img" aria-label="divisão do roçado: ${ks.map((k) => `${CULT[k].nome} ${rasc.cult[k]}%`).join(", ")}">${ks.map((k) =>
    `<i class="t-${CULT[k].t}" style="flex:${rasc.cult[k]}"><span>${ks.length <= 4 ? U.ic(CULT[k].icone) : ""}${ks.length <= 2 && rasc.cult[k] >= 25
      ? `${CULT[k].nome} ` : ""}${rasc.cult[k]}%</span></i>`).join("")}</span>`;
  const opLista = (k) => botao(`data-c="${k}"`, ks.includes(k), `${U.ic(CULT[k].icone)}<span class="sr-l-nome"><b>${CULT[k].nome}</b>${CULT[k].sub
    ? `<small>${CULT[k].sub}</small>` : ""}</span>${foraDaqui(r, k) ? `<em class="sr-fora">fora daqui</em>` : ""}`, "sr-op-lista");
  const todas = `<div class="sr-todas">${GRUPOS.map((g) => `<div class="sr-grupo"><p class="sr-g-rot">${g.nome}</p>
      <div class="sr-g-ops">${g.ks.map(opLista).join("")}</div></div>`).join("")}
    <div class="sr-grupo"><p class="sr-g-rot">Não achou?</p><div class="sr-g-ops">${opLista("outra")}</div></div></div>`;
  const fora = ks.filter((k) => foraDaqui(r, k));
  // a fonte de cada uma vem antes (o rótulo curto do selo sai da 1ª: ZARC onde há zoneamento, FAO onde só o GAEZ decide)
  const aviso = fora.length ? `<p class="sr-aviso">${U.ic("alerta")}<span>Fora do indicado aqui: ${U.esc(listaNomes(fora).toLowerCase())}.</span>${U.selo("medido",
    `${fora.map((k) => `${CULT[k].motor}: ${noCardapio(r, k)?.base || "fora"}`).join("; ")}. ${FONTE_ZON}`)}</p>` : "";
  const linhaHoje = `<section class="sr-linha" id="linha-hoje">
      <h2 class="sr-rot">O que planta hoje?</h2>
      <div class="sr-ops n3">${opcoesCultura(r, ks).map((k) => botao(`data-c="${k}"`, ks.includes(k), `${U.ic(CULT[k].icone)}<b>${CULT[k].nome}</b>`)).join("")}</div>
      ${det("todas", `Ver todas as culturas (${TODAS.length})`, todas, "sr-todas-det")}
      ${aviso}
      ${ks.length > 1 ? det("quanto", `${barra}<small>quanto de cada</small>`, `<div class="hi-quanto">${ks.map((k) => `<div class="hi-q-linha">${U.ic(CULT[k].icone)}<b>${CULT[k].nome}</b>
          <button type="button" class="hi-mm" data-m="${k}" data-d="-10" aria-label="menos ${CULT[k].nome}">−</button>
          <span class="hi-q-val">${rasc.cult[k]}%</span>
          <button type="button" class="hi-mm" data-m="${k}" data-d="10" aria-label="mais ${CULT[k].nome}">+</button></div>`).join("")}
          <button type="button" class="chip hi-igual" data-igual="1">dividir igual</button></div>`, "sr-mais-barra") : `<div class="sr-so-barra">${barra}</div>`}
    </section>`;

  // ---- tamanho: chips de ha e, à vista, largura × comprimento em metros (sem resposta: o típico do Censo; o lado do quadrado
  // dele fica de exemplo no campo vazio). Sem resposta, o chip mais perto do típico fica tracejado (só a cara: não grava nada)
  const sug = haResp === null ? HAS.reduce((a, v) => (Math.abs(v - haV) < Math.abs(a - haV) ? v : a)) : null;
  const ladoTip = Math.round(Math.sqrt(haV * 10000));
  // os rótulos dizem qual lado é qual (o comprimento é o do desenho do Plano: do alto até embaixo, para onde a água desce, e as
  // faixas vão atravessadas a ele); no campo vazio, o lado do quadrado típico vem como exemplo ("ex.: 101"), para não parecer valor
  const campo = (k, rot, seta, dica) => `<label class="sr-m-campo" title="${dica}"><span class="sr-m-caixa"><input type="number" inputmode="numeric" min="1"
      max="${MAX_M}" step="1" data-lado="${k}" value="${U.esc(k === "larg" ? rasc.ml : rasc.mc)}" placeholder="ex.: ${ladoTip}"
      aria-label="${dica}, em metros"></span><small>${seta}<span>${rot}</span></small></label>`;
  const linhaHa = `<section class="sr-linha" id="linha-ha">
      <h2 class="sr-rot"><span>Tamanho: <b class="sr-ha-val">${areaTxt(U, haV)}</b>${haResp ? "" : `<span class="sr-ha-tip">, ${deOnde}</span>`}</span>${haResp ? ""
        : `<span class="sr-ha-tip">${U.selo("suposicao", FONTE_TIPICO)}</span>`}</h2>
      <div class="sr-ops n5">${HAS.map((v) => botao(`data-ha="${v}"`, haResp !== null && !rasc.larg && Math.abs(haResp - v) < 0.005,
        `<b>${v === 0.5 ? "½" : v}${v === 5 ? " ha" : ""}</b>`, `sr-ha${v === sug && Math.abs(v - haV) < 0.26 ? " sugerida" : ""}`)).join("")}</div>
      <div class="sr-metros">
        <p class="sr-m-rot">Ou em metros:</p>
        <div class="sr-m-linha">${campo("larg", "largura", SETA_LADO, "Largura do roçado: de um lado ao outro")}<span class="sr-vezes" aria-hidden="true">×</span>${campo("comp",
          "comprimento, morro abaixo", SETA_DESCE, "Comprimento do roçado: do alto até embaixo, para onde a água da chuva desce")}
          <p class="sr-m-conv" aria-live="polite"><b>= ${areaTxt(U, haV)}</b><span>${tarefas}</span></p></div>
      </div>
      ${det("medida", "em tarefas ou passos", `<div class="sr-area"></div>`)}
    </section>`;

  const linhaTerra = `<section class="sr-linha" id="linha-terra">
      <h2 class="sr-rot">Na chuva forte, a sua terra…</h2>
      <div class="sr-ops n4">${TERRAS.map(([v, i, t]) => botao(`data-terra="${v}"`, (rasc.terra || "") === v, `${U.ic(i)}<b>${t}</b>`, "alto")).join("")}</div>
      ${olho(OLHOS.terra)}
    </section>`;

  const linhaBaixio = `<section class="sr-linha" id="linha-baixio">
      <h2 class="sr-rot">Tem baixio?</h2>
      <div class="sr-explica">${PERFIL}<p>É a parte mais baixa do roçado: a chuva escorre para lá e a terra fica úmida mais tempo.
        Beira de riacho, grota, açude.</p></div>
      <div class="sr-ops n${baixios.length}">${baixios.map(([v, f, t]) => botao(`data-baixio="${v}"`, (rasc.baixio || "") === v,
        `${miniRocado(f)}<b>${t}</b>`, "alto")).join("")}</div>
      ${olho(OLHOS.baixio)}
    </section>`;

  // ---- maniva: só quando a mandioca está no jeito dele ou no plano daqui (sem maniva, ela sai do plano). Quem já planta mandioca
  // ouve "para plantar mais?"; quem não planta ouve por que a pergunta está ali (o plano daqui usa mandioca) e não vê "Já está plantada"
  const mv = manivaTela(ctx), planta = ks.includes("mandioca");
  const mandNoPlano = (r.plano?.faixas || []).some((f) => (f.anos || []).some((a) => /^Mandioca/.test(a.cultura || "")));
  const manivas = MANIVAS.filter(([v]) => v !== "plantada" || planta || mv === "plantada");
  const linhaManiva = planta || mandNoPlano || ctx.resp.maniva ? `<section class="sr-linha" id="linha-maniva">
      <h2 class="sr-rot">${planta ? "Tem maniva para plantar mais?" : "Se for plantar mandioca, tem maniva?"} <span class="eco">${planta || !mandNoPlano
        ? "A rama da mandioca." : "O plano daqui usa mandioca."}</span></h2>
      <div class="sr-ops n${manivas.length}">${manivas.map(([v, t]) => botao(`data-maniva="${v}"`, mv === v, `<b>${t}</b>`, "sr-maniva")).join("")}</div>
    </section>` : "";

  // ---- o ano passado nesse chão (`antes` = "2025:milho,feijao" ou "2025:pousio"): as culturas de hoje + outra + descansou + não sei
  const ap = anoPassado(r), noAno = lerAntes(rasc.antes)[ap] || [];
  const chipsAntes = [...Object.keys(CULT_H).filter((k) => k !== "pousio" && (ks.includes(k) || noAno.includes(k) || k === "outra")), "pousio"];
  const linhaAntes = `<section class="sr-linha" id="linha-antes">
      <h2 class="sr-rot">No ano passado, o que plantou nesse chão? <span class="eco">${ap}</span></h2>
      <div class="sr-chips">${chipsAntes.map((k) => botao(`data-antes="${k}"`, noAno.includes(k),
        `${k === "pousio" ? icHist(U, "pousio") : U.ic(CULT[k]?.icone || "broto")}<b>${k === "pousio" ? "Descansou" : CULT_H[k].nome}</b>`, "sr-chip")).join("")}
        ${botao(`data-antes=""`, !noAno.length, `${U.ic("interrog")}<b>Não sei</b>`, "sr-chip")}</div>
    </section>`;

  el.innerHTML = `<div class="sua-roca">
    <div class="titulo-passo"><p class="kicker">Sua roça</p><h1>É assim o seu roçado?<span class="eco">Marcamos o comum daqui.</span></h1></div>
    ${faixa(r, U)}${linhaHoje}${linhaHa}${linhaTerra}${linhaBaixio}${linhaManiva}${linhaAntes}</div>`;

  const raiz = el.firstElementChild;
  const mudar = (linha, f) => (ev) => { f(ev.currentTarget); tocado.add(linha); desenhar(el, ctx); };
  raiz.querySelectorAll("[data-c]").forEach((b) => b.addEventListener("click", mudar("hoje", (b) => {
    const k = b.dataset.c, novo = ks.includes(k) ? ks.filter((x) => x !== k) : Object.keys(CULT).filter((x) => ks.includes(x) || x === k);
    if (novo.length) rasc.cult = igual(novo);
  })));
  raiz.querySelectorAll("[data-m]").forEach((b) => b.addEventListener("click", mudar("hoje", (b) => { rasc.cult = mexer(rasc.cult, b.dataset.m, +b.dataset.d); })));
  raiz.querySelector("[data-igual]")?.addEventListener("click", mudar("hoje", () => { rasc.cult = igual(ks); }));
  raiz.querySelectorAll("[data-ha]").forEach((b) => b.addEventListener("click", mudar("ha", (b) => {
    Object.assign(rasc, { ha: b.dataset.ha, area_un: "", larg: "", comp: "", ml: "", mc: "" });
  })));
  raiz.querySelectorAll("[data-terra]").forEach((b) => b.addEventListener("click", mudar("terra", (b) => { rasc.terra = b.dataset.terra; })));
  raiz.querySelectorAll("[data-baixio]").forEach((b) => b.addEventListener("click", mudar("baixio", (b) => { rasc.baixio = b.dataset.baixio; })));
  raiz.querySelectorAll("[data-maniva]").forEach((b) => b.addEventListener("click", mudar("maniva", (b) => { rasc.maniva = b.dataset.maniva; })));
  raiz.querySelectorAll("[data-antes]").forEach((b) => b.addEventListener("click", mudar("antes", (b) => {
    const k = b.dataset.antes, anos = lerAntes(rasc.antes);
    const novo = !k ? [] : k === "pousio" ? (noAno.includes("pousio") ? [] : ["pousio"])
      : noAno.includes(k) ? noAno.filter((x) => x !== k) : [...noAno.filter((x) => x !== "pousio"), k];
    if (novo.length) anos[ap] = novo; else delete anos[ap];
    rasc.antes = escreverAntes(anos);
  })));
  // metros: digitando, o "= X ha", as tarefas, o tamanho e os chips acompanham ali mesmo, sem redesenhar (o campo não perde o
  // foco e o toque no outro campo não se perde). Só os dois lados juntos viram resposta.
  raiz.querySelectorAll("[data-lado]").forEach((inp) => inp.addEventListener("input", () => {
    rasc[inp.dataset.lado === "larg" ? "ml" : "mc"] = inp.value;
    const L = metro(rasc.ml), C = metro(rasc.mc);
    tocado.add("ha");
    if (!L || !C) { Object.assign(rasc, { larg: "", comp: "", area_un: "" }); return; }
    const h = (L * C) / 10000;
    Object.assign(rasc, { ha: txtHa(h), area_un: escreverArea({ un: "medida", c: C, l: L, em: "m" }, uf), larg: String(L), comp: String(C) });
    raiz.querySelector(".sr-m-conv").innerHTML = `<b>= ${areaTxt(U, h)}</b><span>${tarefasTxt(U, (h * 10000) / tarefaPadrao(uf))}</span>`;
    raiz.querySelector(".sr-ha-val").textContent = areaTxt(U, h);
    raiz.querySelectorAll(".sr-ha-tip").forEach((s) => s.remove());
    raiz.querySelectorAll("[data-ha]").forEach((b) => { b.classList.remove("marcada", "sugerida"); b.setAttribute("aria-pressed", "false"); });
  }));
  raiz.querySelectorAll("details.sr-mais").forEach((d) => d.addEventListener("toggle", () => {
    if (d.open) abertos.add(d.dataset.k); else abertos.delete(d.dataset.k);
    if (d.open && d.dataset.k === "medida") montarArea(raiz, el, ctx, haV);
  }));
  if (abertos.has("medida")) montarArea(raiz, el, ctx, haV);
}

/** "em tarefas ou passos": a tela de area.js (só tarefas e passos: os metros já estão à vista) num ctx de rascunho, que só muda
 *  esta tela. Uma medida em passos também vira largura × comprimento em metros. */
function montarArea(raiz, el, ctx, haV) {
  const slot = raiz.querySelector(".sr-area");
  if (!slot) return;
  const cx = { ...ctx, resp: { ...ctx.resp, ha: rasc.ha, area_un: rasc.area_un }, ef: { ...ctx.ef, ha: haV }, entrou: areaNova,
    set: (p) => {
      const m = metrosDe(p.area_un); // em passos, o ha sai dos metros (o mesmo que o Plano desenha)
      Object.assign(rasc, p, { larg: m ? String(m.larg) : "", comp: m ? String(m.comp) : "", ml: m ? String(m.larg) : "", mc: m ? String(m.comp) : "" },
        m ? { ha: txtHa((m.larg * m.comp) / 10000) } : {});
      tocado.add("ha");
      desenhar(el, ctx);
    } };
  areaNova = false;
  AREA.render(slot, cx, { semTitulo: true, abas: ["tarefa", "passos"] });
}

export default {
  id: "perguntas",
  titulo: "Sua roça",
  render(el, ctx) {
    if (ctx.entrou || !rasc) {
      const resp = ctx.resp, med = medidaIni(resp, ctx.r.local?.uf);
      rasc = { cult: lerHoje(resp.hoje || "", ctx.r.padroes).cult, ha: resp.ha || "", area_un: resp.area_un || "", terra: resp.terra || "",
        baixio: resp.baixio || "", maniva: resp.maniva || "", antes: resp.antes || "",
        larg: med ? String(med.larg) : "", comp: med ? String(med.comp) : "", ml: med ? String(med.larg) : "", mc: med ? String(med.comp) : "" };
      tocado = new Set();
      const a = String(resp.area_un || "");
      abertos = new Set(ctx.foco === "ha" && (a.startsWith("tarefa") || a.endsWith(":passos")) ? ["medida"] : []);
      areaNova = true;
    }
    desenhar(el, ctx);
    // o que foi tocado e ainda não foi gravado: o verde grava; a casca (roca.js) também leva junto ao sair por uma pílula ou pelo rodapé
    ctx.pendente = () => { const p = patch(ctx); guardarAntes(ctx, p); return p; };
    // "Ver o meu plano →" (ou "Voltar a …"): grava uma vez só. Antes, troca esta entrada do histórico pela mesma tela com as
    // respostas, para o voltar do celular reabrir "Sua roça" como a pessoa deixou.
    ctx.primario?.(ctx.volta ? undefined : "Ver o meu plano →", () => {
      const p = ctx.pendente();
      if (Object.keys(p).length) location.replace(ctx.link(2, p));
      location.hash = ctx.link(ctx.volta || 3, p);
    });
    if (ctx.entrou && ctx.foco) {
      setTimeout(() => { // depois de o roca.js pôr a tela no lugar e rolar ao topo
        const l = el.querySelector(`#linha-${ctx.foco}`);
        if (!l) return;
        l.scrollIntoView({ block: "start", behavior: "smooth" });
        l.classList.add("em-foco");
        setTimeout(() => l.classList.remove("em-foco"), 2600);
      }, 80);
    }
  },
};
