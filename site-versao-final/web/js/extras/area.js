// QUADRA, módulo extra "area" (pedido do José, 14/11/2026: "acrescentar opção por hectare ou tamanho do terreno").
// A tela "Qual o tamanho do seu roçado?" em 3 unidades: hectares, tarefas ou a medida do terreno (comprimento × largura, em metros
// ou em passos). Mostra sempre a conversão em hectares e grava ctx.set({ ha, area_un }): `ha` em hectares (texto com ponto, o que o
// roca.js já lê) e `area_un` com o que a pessoa digitou, para reabrir igual. Formato e onde encaixar: integracao/area_historico.md.
//
// A tarefa (IBGE, 1948, "Unidades agrárias não decimais em uso no Brasil", inquérito nas prefeituras): a de 25 × 25 braças
// (0,3025 ha; braça = 2,20 m) é usada em todos os estados do Nordeste (no RN "mil-covas", no MA "linha"); na Bahia predomina a
// "tarefa baiana" de 30 × 30 braças (0,4356 ha), que também aparece no Sertão de PE, em municípios da PB e, no CE, com o nome de
// "cem-passos". Por isso: padrão 3.025 m² (BA: 4.356 m²), a outra à escolha, selo SUPOSIÇÃO e "confirme com o técnico".
import { olho } from "./voce_decide.js";

export const TAREFAS = [
  { m2: 3025, lado: "55 × 55 m", nome: "25 braças" },
  { m2: 4356, lado: "66 × 66 m", nome: "tarefa baiana" },
];
/** Tamanho padrão da tarefa (m²) pelo estado. */
export const tarefaPadrao = (uf) => (uf === "BA" ? 4356 : 3025);
/** Um passo de adulto andando normal (SUPOSIÇÃO; o técnico mede com trena). */
export const PASSO_M = 0.8;

const FONTE_TAREFA = "IBGE (1948), Unidades agrárias não decimais em uso no Brasil: tarefa de 25 × 25 braças (0,3025 ha) em todo o "
  + "Nordeste; na Bahia, a tarefa baiana de 30 × 30 braças (0,4356 ha), no Ceará chamada cem-passos. Braça = 2,20 m. "
  + "Muda de lugar para lugar.";
const FONTE_PASSO = "suposição: 1 passo de adulto ≈ 0,8 m; com trena ou corda medida, o número fica certo";
const FONTE_TIPICO = "típico do município no Censo Agropecuário 2017 (IBGE: área de lavoura do estabelecimento familiar), aplicado ao seu roçado";
const CAMPO_HA = 0.714; // campo oficial de futebol, 105 × 68 m

const REGUA = '<rect x="2.5" y="8" width="19" height="8" rx="1.5"/><path d="M6 8v3M9.5 8v4.5M13 8v3M16.5 8v4.5"/>';
const icRegua = (tam = "") => `<svg class="ic ${tam}" viewBox="0 0 24 24" aria-hidden="true">${REGUA}</svg>`;

const r2 = (v) => Math.round(v * 100) / 100;
const lerNum = (s) => { const v = parseFloat(String(s ?? "").replace(",", ".")); return Number.isFinite(v) && v > 0 ? v : null; };
const txtNum = (v) => String(r2(v)); // 1.21 → "1.21" (ponto: vai para a URL)

// ------------------------------------------------------------------ o texto de area_un
/** Lê area_un: "" ou "ha" (hectares), "tarefa:4" (tarefa do estado) ou "tarefa:4:4356" (m² da tarefa escolhida),
 *  "medida:100x50" (metros) ou "medida:125x60:passos". Texto inválido → null. */
export function lerArea(txt) {
  const [un = "", a, b] = String(txt || "").split(":");
  if (un === "" || un === "ha") return { un: "ha" };
  if (un === "tarefa") { const n = lerNum(a); return n ? { un, n, m2: lerNum(b) } : null; }
  if (un === "medida") {
    const [c, l] = String(a || "").split("x").map(lerNum);
    return c && l ? { un, c, l, em: b === "passos" ? "passos" : "m" } : null;
  }
  return null;
}

/** Escreve area_un (o inverso de lerArea). O m² da tarefa só vai no texto quando difere do padrão do estado. */
export function escreverArea(a, uf) {
  if (!a || a.un === "ha") return "";
  if (a.un === "tarefa") return `tarefa:${txtNum(a.n)}${a.m2 && a.m2 !== tarefaPadrao(uf) ? `:${a.m2}` : ""}`;
  if (a.un === "medida") return `medida:${txtNum(a.c)}x${txtNum(a.l)}${a.em === "passos" ? ":passos" : ""}`;
  return "";
}

/** Hectares do que a pessoa digitou (texto de area_un ou o objeto de lerArea); `uf` decide a tarefa quando o texto não diz.
 *  Devolve null para hectares (o valor já está em ctx.resp.ha) ou para texto inválido. */
export function haDe(area, uf) {
  const a = typeof area === "string" || area == null ? lerArea(area) : area;
  if (!a) return null;
  if (a.un === "tarefa") return (a.n * (a.m2 || tarefaPadrao(uf))) / 10000;
  if (a.un === "medida") { const k = a.em === "passos" ? PASSO_M : 1; return (a.c * k * a.l * k) / 10000; }
  return null;
}

// ------------------------------------------------------------------ estado da tela (não é resposta)
let un = "ha"; // aba aberta: ha | tarefa | medida
let rasc = null; // o que está na tela: { n, m2, c, l, em }
let visto = null; // resp.ha + resp.area_un da última leitura
const zerados = new WeakSet();

/** Hectares em pt-BR com 0, 1 ou 2 casas, conforme precisa: 1 → "1"; 0,5 → "0,5"; 1,21 → "1,21". */
function fmtHa(U, v) {
  const c = Math.abs(v - Math.round(v)) < 0.005 ? 0 : Math.abs(v * 10 - Math.round(v * 10)) < 0.05 ? 1 : 2;
  return U.num(v, v >= 10 ? Math.min(c, 1) : c);
}
const fmtN = (U, v) => U.num(v, Math.abs(v - Math.round(v)) < 0.05 ? 0 : 1);

/** Passo do − e do +: 0,1 ha abaixo de 1 ha, 0,5 ha até 5 ha, 1 ha acima. */
function passoHa(v, d) {
  const s = d > 0 ? (v < 1 ? 0.1 : v < 5 ? 0.5 : 1) : (v <= 1 ? 0.1 : v <= 5 ? 0.5 : 1);
  const n = d > 0 ? Math.floor(v / s + 1e-9) * s + s : Math.ceil(v / s - 1e-9) * s - s;
  return Math.max(0.1, Math.min(100, r2(n)));
}
function passoGrade(v, d, s, min, max) {
  const n = d > 0 ? Math.floor(v / s + 1e-9) * s + s : Math.ceil(v / s - 1e-9) * s - s;
  return Math.max(min, Math.min(max, r2(n)));
}

function campos(v) {
  const c = Math.round((v / CAMPO_HA) * 2) / 2;
  if (c < 0.5) return "menos de meio campo de futebol";
  if (c === 0.5) return "meio campo de futebol";
  const int = Math.floor(c), meio = c % 1 ? "½" : "";
  return `${int}${meio} campo${c > 1 ? "s" : ""} de futebol`;
}

/** Retângulo do terreno visto de cima: muda de forma com comprimento × largura. */
function retangulo(U, c, l, em, haV) {
  const W = 200, H = 112, ox = 46, oy = 18;
  const k = Math.min(W / c, H / l), w = Math.max(10, c * k), h = Math.max(10, l * k);
  const x = ox + (W - w) / 2, y = oy + (H - h) / 2, un = em === "passos" ? "passos" : "m";
  const dentro = w > 70 && h > 30 ? `<text x="${x + w / 2}" y="${y + h / 2 + 6}" class="ar-ret-ha">${fmtHa(U, r2(haV))} ha</text>` : "";
  return `<svg class="ar-ret" viewBox="0 0 292 150" role="img" aria-label="terreno de ${U.esc(c)} por ${U.esc(l)} ${un}">
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="4" class="ar-ret-terra"/>
    <text x="${x + w / 2}" y="${y - 6}" class="ar-ret-rot">${U.num(c, c % 1 ? 1 : 0)} ${un}</text>
    <text x="${x - 8}" y="${y + h / 2}" class="ar-ret-rot" transform="rotate(-90 ${x - 8} ${y + h / 2})">${U.num(l, l % 1 ? 1 : 0)} ${un}</text>
    ${dentro}</svg>`;
}

/** Quadradinhos: um por tarefa (até 60), o último pela metade quando sobra meia. */
function quadrinhos(n) {
  const cheios = Math.floor(n + 1e-9), meio = n - cheios >= 0.25 && n - cheios < 0.75, mais = n - cheios >= 0.75;
  const k = Math.min(60, cheios + (mais ? 1 : 0));
  return `<div class="ar-quad" aria-hidden="true">${"<i></i>".repeat(k)}${meio && k < 60 ? `<i class="meio"></i>` : ""}${cheios > 60 ? `<em>+${cheios - 60}</em>` : ""}</div>`;
}

export default {
  id: "area",
  titulo: "Tamanho do roçado",
  /** opcoes: { semTitulo: true } tira o título, os atalhos ½ · 1 · 2 · 3 · 5 ha e a linha do típico (dentro de Sua roça, que já
   *  tem os três na própria linha do tamanho). */
  async render(el, ctx, opcoes = {}) {
    const U = ctx.util, uf = ctx.r?.local?.uf, pad = ctx.r?.padroes || {};
    const tipico = pad.rocado_ha > 0 ? pad.rocado_ha : pad.rocado_ha_padrao > 0 ? pad.rocado_ha_padrao : null;
    const respHa = lerNum(ctx.resp?.ha);
    const ha = respHa || ctx.ef?.ha || tipico || 1;
    const chave = `${ctx.resp?.ha || ""}|${ctx.resp?.area_un || ""}`;

    // ao chegar, ou quando a resposta mudou: reabre na unidade que a pessoa usou (se ela ainda bate com o ha gravado)
    if ((ctx.entrou && !zerados.has(ctx)) || chave !== visto || !rasc) {
      zerados.add(ctx);
      visto = chave;
      const a = lerArea(ctx.resp?.area_un), hd = haDe(a, uf);
      const bate = a && a.un !== "ha" && hd && respHa && Math.abs(hd - respHa) / respHa < 0.02;
      const m2 = (bate && a.m2) || tarefaPadrao(uf), lado = Math.max(1, Math.round(Math.sqrt(ha * 10000)));
      rasc = { n: r2((ha * 10000) / m2), m2, c: lado, l: lado, em: "m" };
      if (bate) Object.assign(rasc, a, { m2 });
      un = bate ? a.un : "ha";
    }

    const salvar = (haV, area) => ctx.set({ ha: txtNum(Math.max(0.01, haV)), area_un: escreverArea(area, uf) });
    const redesenhar = () => this.render(el, ctx, opcoes);
    const haMedida = () => haDe({ un: "medida", ...rasc }, uf);
    const haTela = un === "ha" ? ha : un === "tarefa" ? haDe({ un: "tarefa", n: rasc.n, m2: rasc.m2 }, uf) : haMedida();

    const abas = [["ha", U.ic("faixas", "g"), "Hectares", ""], ["tarefa", U.ic("enxada", "g"), "Tarefas", ""],
      ["medida", icRegua("g"), "Medida", "do terreno"]];
    const seletor = `<div class="ar-unidades" role="tablist" aria-label="unidade">${abas.map(([v, i, t, s]) =>
      `<button type="button" role="tab" class="ar-un ${un === v ? "marcada" : ""}" data-un="${v}" aria-selected="${un === v}">${i}<b>${t}</b>${s ? `<span>${s}</span>` : ""}</button>`).join("")}</div>`;

    const mm = (alvo, d, rot) => `<button type="button" class="ar-mm" data-alvo="${alvo}" data-d="${d}" aria-label="${rot}">${d > 0 ? "+" : "−"}</button>`;
    let corpo = "", conv = "";
    if (un === "ha") {
      corpo = `<div class="ar-passo">${mm("ha", -1, "menos")}<div class="ar-val"><span class="numero-grande">${fmtHa(U, ha)}</span><small>hectares</small></div>${mm("ha", 1, "mais")}</div>
        ${opcoes.semTitulo ? "" : `<div class="ar-rapido">${[0.5, 1, 2, 3, 5].map((v) => `<button type="button" class="chip ${Math.abs(ha - v) < 0.005 ? "verde" : ""}" data-ha="${v}">${v === 0.5 ? "½" : v} ha</button>`).join("")}</div>`}`;
      const nt = (ha * 10000) / tarefaPadrao(uf);
      conv = `<p class="ar-conv"><span>≈ ${fmtN(U, nt)} tarefa${nt >= 1.05 ? "s" : ""} · ${campos(ha)}</span></p>`;
    } else if (un === "tarefa") {
      const n = rasc.n;
      corpo = `<div class="ar-passo">${mm("n", -1, "menos uma tarefa")}<div class="ar-val"><span class="numero-grande">${fmtN(U, n)}</span><small>tarefa${n >= 1.05 ? "s" : ""}</small></div>${mm("n", 1, "mais uma tarefa")}</div>
        ${quadrinhos(n)}
        <div class="ar-rapido">${[2, 3, 4, 6, 10].map((v) => `<button type="button" class="chip ${Math.abs(n - v) < 0.01 ? "verde" : ""}" data-n="${v}">${v} tarefas</button>`).join("")}</div>
        <div class="ar-tam"><p class="ar-rot">Tamanho da tarefa ${U.selo("suposicao", FONTE_TAREFA)}</p>
          <div class="ar-tam-ops">${TAREFAS.map((t) => `<button type="button" class="ar-tam-op ${rasc.m2 === t.m2 ? "marcada" : ""}" data-m2="${t.m2}" aria-pressed="${rasc.m2 === t.m2}">
            <b>${t.lado}</b><span>${U.num(t.m2)} m² · ${t.nome}</span></button>`).join("")}</div></div>`;
      conv = `<p class="ar-conv"><b>= ${fmtHa(U, r2(haTela))} ha</b></p>`;
    } else {
      const unTxt = rasc.em === "passos" ? "passos" : "metros";
      const lado = (k, rot) => `<div class="ar-lado"><span class="ar-rot">${rot}</span><div class="ar-campo">${mm(k, -1, `menos ${rot.toLowerCase()}`)}
        <input type="number" min="1" step="1" inputmode="decimal" data-lado="${k}" value="${U.esc(r2(rasc[k]))}" aria-label="${rot} em ${unTxt}">${mm(k, 1, `mais ${rot.toLowerCase()}`)}</div>
        <small>${unTxt}</small></div>`;
      corpo = `<div class="ar-em"><button type="button" class="chip ${rasc.em === "m" ? "verde" : ""}" data-em="m">metros</button>
          <button type="button" class="chip ${rasc.em === "passos" ? "verde" : ""}" data-em="passos">passos</button>
          ${rasc.em === "passos" ? `<span class="ar-em-nota">1 passo ≈ 0,8 m ${U.selo("suposicao", FONTE_PASSO)}</span>` : ""}</div>
        <div class="ar-medida">${lado("c", "Comprimento")}<span class="ar-vezes">×</span>${lado("l", "Largura")}</div>
        <div class="ar-prev">${retangulo(U, rasc.c, rasc.l, rasc.em, haTela)}</div>`;
      conv = `<p class="ar-conv"><b>= ${fmtHa(U, r2(haTela))} ha</b></p>`;
    }

    const tip = tipico ? (respHa ? (Math.abs(respHa - tipico) > 0.005
      ? `<button type="button" class="chip ar-usar-tipico" data-tipico="1">Típico daqui: ${fmtHa(U, tipico)} ha · usar</button>` : "")
      : `<span>Usando o típico ${pad.origem_rocado === "município" || pad.rocado_ha > 0 ? "daqui" : "da região"}: ${fmtHa(U, tipico)} ha</span>`) : "";

    el.innerHTML = `<div class="ar">
      ${opcoes.semTitulo ? "" : `<h1 class="ar-titulo">Qual o tamanho<span class="eco">do seu roçado?</span></h1>`}
      ${seletor}
      <div class="ar-corpo">${corpo}</div>
      ${conv}
      ${tip && !opcoes.semTitulo ? `<p class="ar-tipico">${tip} ${U.selo("suposicao", FONTE_TIPICO)}</p>` : ""}
      ${un === "tarefa" ? olho("A tarefa muda de lugar para lugar: confirme com o técnico.") : ""}
    </div>`;

    const raiz = el.firstElementChild;
    raiz.querySelectorAll("[data-un]").forEach((b) => b.addEventListener("click", () => { un = b.dataset.un; redesenhar(); }));
    raiz.querySelectorAll("[data-ha]").forEach((b) => b.addEventListener("click", () => salvar(+b.dataset.ha, { un: "ha" })));
    raiz.querySelector("[data-tipico]")?.addEventListener("click", () => ctx.set({ ha: "", area_un: "" }));
    raiz.querySelectorAll("[data-n]").forEach((b) => b.addEventListener("click", () => {
      rasc.n = +b.dataset.n;
      salvar(haDe({ un: "tarefa", n: rasc.n, m2: rasc.m2 }, uf), { un: "tarefa", n: rasc.n, m2: rasc.m2 });
    }));
    raiz.querySelectorAll("[data-m2]").forEach((b) => b.addEventListener("click", () => {
      rasc.m2 = +b.dataset.m2;
      rasc.n = Math.max(0.5, Math.round(rasc.n * 2) / 2);
      salvar(haDe({ un: "tarefa", n: rasc.n, m2: rasc.m2 }, uf), { un: "tarefa", n: rasc.n, m2: rasc.m2 });
    }));
    raiz.querySelectorAll(".ar-mm").forEach((b) => b.addEventListener("click", () => {
      const alvo = b.dataset.alvo, d = +b.dataset.d;
      if (alvo === "ha") return salvar(passoHa(ha, d), { un: "ha" });
      if (alvo === "n") {
        const s = (d > 0 ? rasc.n < 3 : rasc.n <= 3) ? 0.5 : 1; // meia tarefa até 3; depois, de uma em uma
        rasc.n = passoGrade(rasc.n, d, s, 0.5, 500);
        return salvar(haDe({ un: "tarefa", n: rasc.n, m2: rasc.m2 }, uf), { un: "tarefa", n: rasc.n, m2: rasc.m2 });
      }
      rasc[alvo] = passoGrade(rasc[alvo], d, 5, 1, 5000);
      salvar(haMedida(), { un: "medida", ...rasc });
    }));
    raiz.querySelectorAll("[data-em]").forEach((b) => b.addEventListener("click", () => {
      const em = b.dataset.em;
      if (em === rasc.em) return;
      const k = em === "passos" ? 1 / PASSO_M : PASSO_M; // a mesma terra na outra medida
      rasc.c = Math.max(1, Math.round(rasc.c * k));
      rasc.l = Math.max(1, Math.round(rasc.l * k));
      rasc.em = em;
      salvar(haMedida(), { un: "medida", ...rasc });
    }));
    // digitando: o desenho e o "= X ha" acompanham; grava ao sair do campo (ou Enter)
    raiz.querySelectorAll("[data-lado]").forEach((inp) => {
      inp.addEventListener("input", () => {
        const v = lerNum(inp.value);
        if (!v) return;
        rasc[inp.dataset.lado] = Math.min(5000, v);
        const h = haMedida();
        raiz.querySelector(".ar-prev").innerHTML = retangulo(U, rasc.c, rasc.l, rasc.em, h);
        raiz.querySelector(".ar-conv").innerHTML = `<b>= ${fmtHa(U, r2(h))} ha</b>`;
      });
      inp.addEventListener("change", () => { if (lerNum(inp.value)) salvar(haMedida(), { un: "medida", ...rasc }); });
    });
  },
};
