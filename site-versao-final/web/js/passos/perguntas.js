// Passo 2, "Sua roça": uma tela só, com 4 linhas já marcadas com o comum daqui (o que planta, tamanho, terra e baixio).
// Cada toque muda só o rascunho da tela: não grava, não chama a API e não avança. O primário da barra ("Ver o meu plano →",
// ou "Voltar a <passo> →" para quem veio de um "mudar") grava uma vez só, e só as linhas tocadas.
// Ordem de serviço: analise/fluxo/00_FLUXO_FINAL.md (seções 3.1 e 7, dono A).
// Linha 1 usa CULT, igual, mexer e opcoesCultura de extras/hoje_ideal.js; "+ outra medida" abre extras/area.js; a terra usa as
// palavras do Vicente (interface-inicial-vicente). Os modos "pergunta" de hoje_ideal.js e historico.js ficam no código
// (páginas de teste), fora da jornada.
import { olho, OLHOS } from "../extras/voce_decide.js";
import { lerHoje, CULT, igual, mexer, opcoesCultura } from "../extras/hoje_ideal.js";
import AREA, { tarefaPadrao } from "../extras/area.js";

const TERRAS = [["arenosa", "areia", "Seca rápido"], ["mista", "gota", "Segura a umidade"], ["barro", "barro", "Encharca"],
  ["", "interrog", "Não sei"]];
const BAIXIOS = [["nao", 0, "Não tenho"], ["pouco", 0.2, "Pequeno"], ["metade", 0.5, "Grande"], ["", null, "Não sei"]];
const TERCO = ["terco", 1 / 3, "Um terço"]; // só para quem chega por um link antigo (…?baixio=terco)
const HAS = [0.5, 1, 2, 3, 5];
const FONTE_TIPICO = "típico do município no Censo Agropecuário 2017 (IBGE), aplicado ao seu roçado";

// mini-desenho do roçado visto de cima, com o baixio embaixo (fração f; null = tracejado "não sei")
const miniRocado = (f) => `<svg class="mini-rocado" viewBox="0 0 60 60" aria-hidden="true">
  <rect x="2" y="2" width="56" height="56" rx="4" class="mr-terra"/>
  ${f === null ? `<rect x="2" y="38" width="56" height="20" rx="4" class="mr-baixio incerto"/>`
    : f > 0 ? `<rect x="2" y="${58 - 56 * f}" width="56" height="${56 * f}" rx="4" class="mr-baixio"/>` : ""}</svg>`;

let rasc = null; // o rascunho da tela: { cult, ha, area_un, terra, baixio }
let tocado = new Set(); // linhas que a pessoa tocou: só elas vão para a URL
let abertos = new Set(); // "+ quanto de cada" e "+ outra medida" abertos (sobrevivem ao redesenho)
let areaNova = true; // a 1ª montagem de area.js depois de chegar zera o estado dele

const tipicoHa = (pad) => (pad?.rocado_ha > 0 ? pad.rocado_ha : pad?.rocado_ha_padrao > 0 ? pad.rocado_ha_padrao : null);
const lerHa = (s) => { const v = parseFloat(String(s ?? "").replace(",", ".")); return v > 0 ? v : null; };
const mesmaDivisao = (a, b) => Object.keys(a).length === Object.keys(b).length && Object.keys(a).every((k) => a[k] === b[k]);

/** `hoje` com as culturas novas; quem já tinha outras chaves (|cons=…) fica com as dele (o padrão não vira resposta). */
function hojeTxt(cult, antigo) {
  const cs = Object.keys(CULT).filter((k) => cult[k] > 0).map((k) => `${k}:${cult[k]}`).join(",");
  return [cs, ...String(antigo || "").split("|").slice(1).filter(Boolean)].join("|");
}

/** O que vai para a URL: só as linhas tocadas, e só o que mudou de fato. */
function patch(ctx) {
  const resp = ctx.resp, p = {};
  if (tocado.has("hoje")) {
    const antes = lerHoje(resp.hoje || "", ctx.r.padroes).cult;
    if (!mesmaDivisao(antes, rasc.cult)) {
      p.hoje = hojeTxt(rasc.cult, resp.hoje);
      const tinha = "mandioca" in antes, tem = "mandioca" in rasc.cult;
      if (tem && !tinha && !resp.maniva) p.maniva = "plantada"; // marcou a mandioca: ela já está no chão (muda na linha da maniva)
      if (!tem && tinha && resp.maniva === "plantada") p.maniva = "";
    }
  }
  for (const [k, linha] of [["ha", "ha"], ["area_un", "ha"], ["terra", "terra"], ["baixio", "baixio"]]) {
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
  const U = ctx.util, r = ctx.r, pad = r.padroes || {};
  const ks = Object.keys(rasc.cult);
  const tip = tipicoHa(pad), haResp = lerHa(rasc.ha), haV = haResp || tip || 1;
  const nt = (haV * 10000) / tarefaPadrao(r.local?.uf);
  const tarefas = `≈ ${nt >= 2 ? Math.round(nt) : U.num(nt, 1)} tarefa${nt >= 1.5 ? "s" : ""}`;
  const deOnde = pad.rocado_ha > 0 ? "típico daqui" : tip ? "típico da região" : "exemplo";
  const baixios = [...BAIXIOS];
  if (rasc.baixio === "terco" || ctx.resp.baixio === "terco") baixios.splice(2, 0, TERCO);
  const det = (k, titulo, corpo, cls = "") => `<details class="ver-mais sr-mais ${cls}" data-k="${k}"${abertos.has(k) ? " open" : ""}><summary>${titulo}</summary>${corpo}</details>`;
  // a barra colorida da divisão fica sempre à vista: é ela que abre o "quanto de cada"
  const barra = `<span class="hi-divisao sr-divisao" role="img" aria-label="divisão do roçado: ${ks.map((k) => `${CULT[k].nome} ${rasc.cult[k]}%`).join(", ")}">${ks.map((k) =>
    `<i class="t-${CULT[k].t}" style="flex:${rasc.cult[k]}"><span>${ks.length <= 4 ? U.ic(CULT[k].icone) : ""}${ks.length <= 2 && rasc.cult[k] >= 25
      ? `${CULT[k].nome} ` : ""}${rasc.cult[k]}%</span></i>`).join("")}</span>`;

  const linhaHoje = `<section class="sr-linha" id="linha-hoje">
      <h2 class="sr-rot">O que planta hoje?</h2>
      <div class="sr-ops n3">${opcoesCultura(r).map((k) => botao(`data-c="${k}"`, ks.includes(k), `${U.ic(CULT[k].icone)}<b>${CULT[k].nome}</b>`)).join("")}</div>
      ${ks.length > 1 ? det("quanto", `${barra}<small>quanto de cada</small>`, `<div class="hi-quanto">${ks.map((k) => `<div class="hi-q-linha">${U.ic(CULT[k].icone)}<b>${CULT[k].nome}</b>
          <button type="button" class="hi-mm" data-m="${k}" data-d="-10" aria-label="menos ${CULT[k].nome}">−</button>
          <span class="hi-q-val">${rasc.cult[k]}%</span>
          <button type="button" class="hi-mm" data-m="${k}" data-d="10" aria-label="mais ${CULT[k].nome}">+</button></div>`).join("")}
          <button type="button" class="chip hi-igual" data-igual="1">dividir igual</button></div>`, "sr-mais-barra") : `<div class="sr-so-barra">${barra}</div>`}
    </section>`;

  // sem resposta, o chip mais perto do típico fica tracejado (só a cara: não grava nada)
  const sug = haResp === null ? HAS.reduce((a, v) => (Math.abs(v - haV) < Math.abs(a - haV) ? v : a)) : null;
  const linhaHa = `<section class="sr-linha" id="linha-ha">
      <h2 class="sr-rot"><span>Tamanho: <b>${U.ha(haV)}</b>${haResp ? "" : `, ${deOnde}`}</span>${haResp ? "" : U.selo("suposicao", FONTE_TIPICO)}</h2>
      <div class="sr-ops n5">${HAS.map((v) => botao(`data-ha="${v}"`, haResp !== null && Math.abs(haResp - v) < 0.005,
        `<b>${v === 0.5 ? "½" : v}${v === 5 ? " ha" : ""}</b>`, `sr-ha${v === sug && Math.abs(v - haV) < 0.26 ? " sugerida" : ""}`)).join("")}</div>
      ${det("medida", `outra medida <span class="sr-lado">(${tarefas})</span>`, `<div class="sr-area"></div>`)}
    </section>`;

  const linhaTerra = `<section class="sr-linha" id="linha-terra">
      <h2 class="sr-rot">Na chuva forte, a sua terra…</h2>
      <div class="sr-ops n4">${TERRAS.map(([v, i, t]) => botao(`data-terra="${v}"`, (rasc.terra || "") === v, `${U.ic(i)}<b>${t}</b>`, "alto")).join("")}</div>
      ${olho(OLHOS.terra)}
    </section>`;

  const linhaBaixio = `<section class="sr-linha" id="linha-baixio">
      <h2 class="sr-rot">Tem baixio? <span class="eco">A parte úmida.</span></h2>
      <div class="sr-ops n${baixios.length}">${baixios.map(([v, f, t]) => botao(`data-baixio="${v}"`, (rasc.baixio || "") === v,
        `${miniRocado(f)}<b>${t}</b>`, "alto")).join("")}</div>
    </section>`;

  el.innerHTML = `<div class="sua-roca">
    <div class="titulo-passo"><p class="kicker">Sua roça</p><h1>É assim o seu roçado?<span class="eco">Marcamos o comum daqui.</span></h1></div>
    ${faixa(r, U)}${linhaHoje}${linhaHa}${linhaTerra}${linhaBaixio}</div>`;

  const raiz = el.firstElementChild;
  const mudar = (linha, f) => (ev) => { f(ev.currentTarget); tocado.add(linha); desenhar(el, ctx); };
  raiz.querySelectorAll("[data-c]").forEach((b) => b.addEventListener("click", mudar("hoje", (b) => {
    const k = b.dataset.c, novo = ks.includes(k) ? ks.filter((x) => x !== k) : Object.keys(CULT).filter((x) => ks.includes(x) || x === k);
    if (novo.length) rasc.cult = igual(novo);
  })));
  raiz.querySelectorAll("[data-m]").forEach((b) => b.addEventListener("click", mudar("hoje", (b) => { rasc.cult = mexer(rasc.cult, b.dataset.m, +b.dataset.d); })));
  raiz.querySelector("[data-igual]")?.addEventListener("click", mudar("hoje", () => { rasc.cult = igual(ks); }));
  raiz.querySelectorAll("[data-ha]").forEach((b) => b.addEventListener("click", mudar("ha", (b) => { rasc.ha = b.dataset.ha; rasc.area_un = ""; })));
  raiz.querySelectorAll("[data-terra]").forEach((b) => b.addEventListener("click", mudar("terra", (b) => { rasc.terra = b.dataset.terra; })));
  raiz.querySelectorAll("[data-baixio]").forEach((b) => b.addEventListener("click", mudar("baixio", (b) => { rasc.baixio = b.dataset.baixio; })));
  raiz.querySelectorAll("details.sr-mais").forEach((d) => d.addEventListener("toggle", () => {
    if (d.open) abertos.add(d.dataset.k); else abertos.delete(d.dataset.k);
    if (d.open && d.dataset.k === "medida") montarArea(raiz, el, ctx, haV);
  }));
  if (abertos.has("medida")) montarArea(raiz, el, ctx, haV);
}

/** "+ outra medida": a tela de area.js (hectares, tarefas ou metros) num ctx de rascunho, que só muda esta tela. */
function montarArea(raiz, el, ctx, haV) {
  const slot = raiz.querySelector(".sr-area");
  if (!slot) return;
  const cx = { ...ctx, resp: { ...ctx.resp, ha: rasc.ha, area_un: rasc.area_un }, ef: { ...ctx.ef, ha: haV }, entrou: areaNova,
    set: (p) => { Object.assign(rasc, p); tocado.add("ha"); desenhar(el, ctx); } };
  areaNova = false;
  AREA.render(slot, cx, { semTitulo: true });
}

export default {
  id: "perguntas",
  titulo: "Sua roça",
  render(el, ctx) {
    if (ctx.entrou || !rasc) {
      const resp = ctx.resp;
      rasc = { cult: lerHoje(resp.hoje || "", ctx.r.padroes).cult, ha: resp.ha || "", area_un: resp.area_un || "", terra: resp.terra || "",
        baixio: resp.baixio || "" };
      tocado = new Set();
      abertos = new Set(ctx.foco === "ha" && resp.area_un ? ["medida"] : []);
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
