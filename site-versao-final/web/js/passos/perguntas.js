// Passo 2, "Sua roça": uma pergunta por tela, com botões grandes de ícone (estilo da tela inicial). Toda pergunta tem "não sei"
// (vale o padrão do município). Entram depois das opções e antes do plano (PLANO_INTEGRACAO.md, decisão 4).
// A pergunta da terra usa as palavras do Vicente (interface-inicial-vicente) e alimenta o ZARC por solo do núcleo do José.
// "Seu olho" (ponto 16): nas perguntas da terra e do baixio, no tamanho do roçado e no aviso de irrigação (extras/voce_decide.js).
import { olho, OLHOS } from "../extras/voce_decide.js";
// Antes das 5 perguntas: "Como você planta hoje?" (extras/hoje_ideal.js) e o que já plantou e viveu (extras/historico.js).
// O tamanho do roçado usa extras/area.js (hectares, tarefas ou a medida do terreno).
import HI, { lerHoje, resumoHoje } from "../extras/hoje_ideal.js";
import HIST, { lerHistorico, resumoHistorico, icHist } from "../extras/historico.js";
import AREA from "../extras/area.js";
let fase = "hoje"; // "hoje" → "historico" → "perguntas"
let q = 0; // pergunta atual (0..4; 5 = pronto)
let telaForcada = null; // ao trocar de fase, abre o módulo nesta tela
let antes = null; // janelas antes das respostas, para o resumo "o que mudou"

// mini-desenho do roçado visto de cima, com o baixio embaixo (fração f; null = tracejado "não sei")
const miniRocado = (f) => `<svg class="mini-rocado" viewBox="0 0 60 60" aria-hidden="true">
  <rect x="2" y="2" width="56" height="56" rx="4" class="mr-terra"/>
  ${f === null ? `<rect x="2" y="38" width="56" height="20" rx="4" class="mr-baixio incerto"/>`
    : f > 0 ? `<rect x="2" y="${58 - 56 * f}" width="56" height="${56 * f}" rx="4" class="mr-baixio"/>` : ""}</svg>`;

const PERG = [
  { k: "terra", titulo: "Quando chove forte,", eco: "como fica a sua terra?", muda: "as datas de plantio",
    op: [["arenosa", "areia", "Seca rápido", "a água some"], ["mista", "gota", "Segura a umidade", "não empoça"],
      ["barro", "barro", "Encharca", "gruda no pé"], ["", "interrog", "Não sei", "uso as datas que servem em qualquer terra"]] },
  { k: "ha", titulo: "Qual o tamanho", eco: "do seu roçado?", muda: "o desenho e o dinheiro", tipo: "area" },
  { k: "baixio", titulo: "Tem um baixio?", eco: "A parte baixa que fica úmida.", muda: "onde vai o milho",
    op: [["nao", { mini: 0 }, "Não tenho", ""], ["pouco", { mini: 0.2 }, "Pequeno", ""], ["terco", { mini: 1 / 3 }, "Um terço", ""],
      ["metade", { mini: 0.5 }, "Metade", ""], ["", { mini: null }, "Não sei", ""]] },
  { k: "agua", titulo: "Além da chuva,", eco: "que água você tem?", muda: "o que dá para salvar",
    op: [["", "chuva", "Só a chuva", ""], ["cisterna", "cisterna", "Cisterna de beber", ""], ["barreiro", "gota", "Barreiro ou açude", ""],
      ["irriga", "poco", "Poço ou irrigação", ""]] },
  { k: "maniva", titulo: "E a mandioca?", eco: "Ela é a reserva do ano ruim.", muda: "a reserva para a seca",
    op: [["", "semente", "Consigo maniva", "para plantar"], ["plantada", "mandioca", "Já tenho plantada", ""], ["nao", "alerta", "Não consigo maniva", ""]] },
];

const janelas = (r) => Object.fromEntries((r.agenda?.culturas || []).map((c) => [c.cultura, (c.plantar || "").split(" (")[0].replace(/^de /, "").replace(/\/20\d\d/g, "")]));

function opcao(p, [v, icone, rot, sub], atual, U) {
  const vis = typeof icone === "object" ? miniRocado(icone.mini) : U.ic(icone, "gg");
  return `<button type="button" class="opcao ${String(atual) === String(v) ? "marcada" : ""}" data-v="${U.esc(v)}">
    ${vis}<b>${U.esc(rot)}</b>${sub ? `<span>${U.esc(sub)}</span>` : ""}</button>`;
}

function resumo(ctx, U) {
  const ef = ctx.ef, jan = janelas(ctx.r);
  const leg = ctx.r.plano?.leguminosa, chave = [leg, "Mandioca", "Milho"].filter((c) => c && jan[c]);
  const mud = antes ? chave.filter((c) => antes[c] && antes[c] !== jan[c]) : [];
  const fichas = [
    ["solo", { arenosa: "Terra arenosa", mista: "Terra misturada", barro: "Terra de barro", nao_sei: "Terra: não sei" }[ef.terra], 0],
    ["faixas", U.ha(ef.ha), 1],
    ["gota", { nao_sei: "Baixio: não sei", nao: "Sem baixio", pouco: "Baixio pequeno", terco: "Baixio de ⅓", metade: "Baixio de ½" }[ef.baixio], 2],
    ["chuva", { chuva: "Só a chuva", cisterna: "Cisterna de beber", barreiro: "Barreiro ou açude", irriga: "Poço ou irrigação" }[ef.agua], 3],
    ["mandioca", { tem: "Consigo maniva", plantada: "Mandioca já plantada", nao: "Sem maniva" }[ef.maniva], 4],
  ];
  // o jeito de hoje e o histórico: uma ficha de cada (a 1ª linha do resumo deles), que reabre a tela certa
  const fh = resumoHoje(lerHoje(ctx.resp.hoje || "", ctx.r.padroes), U)[0];
  const fx = resumoHistorico(lerHistorico(ctx.resp, ctx.r.padroes), U)[0];
  const extras = [fh && `<button type="button" class="ficha-r" data-fase="hoje" data-t="${fh[2]}">${U.ic(fh[0], "g")}<span>Hoje: ${U.esc(fh[1])}</span><em>mudar</em></button>`,
    fx && `<button type="button" class="ficha-r" data-fase="historico" data-t="${fx[2]}">${icHist(U, fx[0])}<span>${U.esc(fx[1])}</span><em>mudar</em></button>`]
    .filter(Boolean).join("");
  return `<div class="pronto">
    <div class="titulo-passo"><p class="kicker">Passo 2 · sua roça</p><h1>Pronto.<span class="eco">O plano agora é do seu roçado.</span></h1></div>
    <div class="fichas">${extras}${fichas.map(([i, t, n]) => `<button type="button" class="ficha-r" data-q="${n}">${U.ic(i, "g")}<span>${U.esc(t)}</span><em>mudar</em></button>`).join("")}</div>
    ${chave.length ? `<div class="painel verde">${U.faixa("calendario", "verde", "Suas datas de plantar")}
      <div class="datas">${chave.map((c) => `<div class="data">${U.ic(U.icCultura(c), "g")}<b>${U.esc(c)}</b><span>${U.esc(jan[c])}</span>
        ${mud.includes(c) ? `<em>antes: ${U.esc(antes[c])}</em>` : ""}</div>`).join("")}</div></div>` : ""}
    ${ef.agua === "irriga" ? olho(OLHOS.irrigacao) : ""}
    <a class="botao primario cta" href="${ctx.link(3)}"><span>Ver como plantar</span>${U.ic("seta")}</a></div>`;
}

export default {
  id: "perguntas",
  titulo: "Sua roça",
  render(el, ctx) {
    const U = ctx.util;
    if (ctx.entrou && !ctx.zerou) { fase = "hoje"; q = 0; telaForcada = 0; antes = janelas(ctx.r); ctx.zerou = true; } // só na chegada
    const topo = () => window.scrollTo({ top: 0, behavior: "smooth" });
    const abrir = (f, t) => { fase = f; telaForcada = t; this.render(el, ctx); topo(); };
    // ao trocar de fase, o módulo recebe um ctx "recém-chegado" para abrir na tela pedida; depois segue com o ctx de verdade
    const t = telaForcada, cx = t === null ? ctx : { ...ctx, entrou: true };
    telaForcada = null;
    if (fase === "hoje") {
      return HI.render(el, cx, { modo: "pergunta", tela: t ?? undefined, aoTerminar: () => abrir("historico", 0) });
    }
    if (fase === "historico") {
      return HIST.render(el, cx, { modo: "pergunta", tela: t ?? undefined, aoVoltar: () => abrir("hoje", 2),
        aoTerminar: () => { q = 0; abrir("perguntas", null); } });
    }
    if (q >= PERG.length) {
      el.innerHTML = resumo(ctx, U);
      el.querySelectorAll(".ficha-r").forEach((b) => b.addEventListener("click", () => {
        if (b.dataset.fase) return abrir(b.dataset.fase, +b.dataset.t || 0);
        q = +b.dataset.q; this.render(el, ctx);
      }));
      return;
    }
    const p = PERG[q], atual = ctx.resp[p.k] || "";
    const extraAgua = p.k === "agua" && ctx.ef.agua === "barreiro"
      ? `<label class="campo">Cabe uns <input type="number" min="0" step="10" id="vol" value="${U.esc(ctx.resp.vol)}" placeholder="500"> m³
         ${ctx.ef.vol_m3 ? `<span class="chip verde">salva ~${U.num(ctx.ef.vol_m3 / 620, 1)} ha de milho na floração</span>` : ""}</label>` : "";
    el.innerHTML = `<div class="quiz">
      <div class="quiz-topo"><p class="kicker">Passo 2 · sua roça · pergunta ${q + 1} de ${PERG.length}</p>
        <div class="quiz-barra">${PERG.map((_, i) => `<i class="${i < q ? "feito" : i === q ? "atual" : ""}"></i>`).join("")}</div></div>
      <h1 class="quiz-titulo">${U.esc(p.titulo)}<span class="eco">${U.esc(p.eco)}</span></h1>
      ${p.tipo === "area" ? `<div class="area-slot"></div>` : `<div class="opcoes n${p.op.length}">${p.op.map((o) => opcao(p, o, atual, U)).join("")}</div>`}
      ${extraAgua}
      ${OLHOS[p.k] && (p.k === "terra" || p.k === "baixio") ? olho(OLHOS[p.k]) : ""}
      <p class="quiz-muda">${U.ic("info")} muda ${U.esc(p.muda)}</p>
      <div class="quiz-nav">
        <button type="button" class="botao secundario" id="q-ant">${U.ic("volta")} Anterior</button>
        <button type="button" class="botao secundario" id="q-prox">${q === PERG.length - 1 ? "Terminar" : p.tipo === "area" || p.k === "agua" ? "Próxima" : "Pular"} ${U.ic("seta")}</button>
      </div></div>`;
    const avancar = () => { q += 1; this.render(el, ctx); window.scrollTo({ top: 0, behavior: "smooth" }); };
    el.querySelectorAll(".opcoes .opcao").forEach((b) => b.addEventListener("click", () => {
      const v = b.dataset.v;
      if (p.k === "agua" && v === "barreiro") { ctx.set({ agua: v }); return; } // pede o volume antes de seguir
      q += 1;
      if (String(atual) === v) this.render(el, ctx); else ctx.set({ [p.k]: v });
    }));
    const slot = el.querySelector(".area-slot");
    if (slot) AREA.render(slot, ctx, { semTitulo: true });
    el.querySelector("#vol")?.addEventListener("change", (e) => ctx.set({ vol: e.target.value }));
    el.querySelector("#q-ant")?.addEventListener("click", () => {
      if (q === 0) return abrir("historico", 2); // volta à última tela do histórico
      q -= 1; this.render(el, ctx);
    });
    el.querySelector("#q-prox").addEventListener("click", avancar);
  },
};
