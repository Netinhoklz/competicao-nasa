// Passo 2, "Sua roça": uma pergunta por tela, com botões grandes de ícone (estilo da tela inicial). Toda pergunta tem "não sei"
// (vale o padrão do município). Entram depois das opções e antes do plano (PLANO_INTEGRACAO.md, decisão 4).
// A pergunta da terra usa as palavras do Vicente (interface-inicial-vicente) e alimenta o ZARC por solo do núcleo do José.
let q = 0; // pergunta atual (0..4; 5 = pronto)
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

function telaArea(ctx, U) {
  const ef = ctx.ef, pad = ctx.r.padroes || {}, padVal = pad.rocado_ha > 0 ? pad.rocado_ha : pad.rocado_ha_padrao;
  return `<div class="area">
    <button type="button" class="area-mais" data-d="-0.5" aria-label="menos">−</button>
    <div class="area-val"><span class="numero-grande">${U.num(ef.ha, ef.ha % 1 ? 1 : 0)}</span><small>hectares</small></div>
    <button type="button" class="area-mais" data-d="0.5" aria-label="mais">+</button></div>
    <div class="area-rapido">${[0.5, 1, 2, 3, 5].map((v) => `<button type="button" class="chip ${+ctx.resp.ha === v ? "verde" : ""}" data-v="${v}">${U.ha(v)}</button>`).join("")}</div>
    <p class="sub centro">${ef.ha_origem === "resposta" ? "" : `Usando o típico ${pad.rocado_ha > 0 ? "daqui" : "da região"}: ${U.ha(padVal || 1)}. `}1 tarefa ≈ 0,3 ha
      ${U.selo("suposicao", "tarefa cearense de 3.025 m², a conferir; padrão: Censo Agro 2017")}</p>`;
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
  return `<div class="pronto">
    <div class="titulo-passo"><p class="kicker">Passo 2 · sua roça</p><h1>Pronto.<span class="eco">O plano agora é do seu roçado.</span></h1></div>
    <div class="fichas">${fichas.map(([i, t, n]) => `<button type="button" class="ficha-r" data-q="${n}">${U.ic(i, "g")}<span>${U.esc(t)}</span><em>mudar</em></button>`).join("")}</div>
    ${chave.length ? `<div class="painel verde">${U.faixa("calendario", "verde", "Suas datas de plantar")}
      <div class="datas">${chave.map((c) => `<div class="data">${U.ic(U.icCultura(c), "g")}<b>${U.esc(c)}</b><span>${U.esc(jan[c])}</span>
        ${mud.includes(c) ? `<em>antes: ${U.esc(antes[c])}</em>` : ""}</div>`).join("")}</div></div>` : ""}
    ${ef.agua === "irriga" ? `<p class="aviso">Com irrigação, combine as datas com o técnico: o QUADRA mostra o plano de sequeiro.</p>` : ""}
    <a class="botao primario cta" href="${ctx.link(3)}"><span>Ver como plantar</span>${U.ic("seta")}</a></div>`;
}

export default {
  id: "perguntas",
  titulo: "Sua roça",
  render(el, ctx) {
    const U = ctx.util;
    if (ctx.entrou && !ctx.zerou) { q = 0; antes = janelas(ctx.r); ctx.zerou = true; } // só na chegada, não a cada redesenho
    if (q >= PERG.length) {
      el.innerHTML = resumo(ctx, U);
      el.querySelectorAll(".ficha-r").forEach((b) => b.addEventListener("click", () => { q = +b.dataset.q; this.render(el, ctx); }));
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
      ${p.tipo === "area" ? telaArea(ctx, U) : `<div class="opcoes n${p.op.length}">${p.op.map((o) => opcao(p, o, atual, U)).join("")}</div>`}
      ${extraAgua}
      <p class="quiz-muda">${U.ic("info")} muda ${U.esc(p.muda)}</p>
      <div class="quiz-nav">
        <button type="button" class="botao secundario" id="q-ant" ${q === 0 ? "disabled" : ""}>${U.ic("volta")} Anterior</button>
        <button type="button" class="botao secundario" id="q-prox">${q === PERG.length - 1 ? "Terminar" : p.tipo === "area" || p.k === "agua" ? "Próxima" : "Pular"} ${U.ic("seta")}</button>
      </div></div>`;
    const avancar = () => { q += 1; this.render(el, ctx); window.scrollTo({ top: 0, behavior: "smooth" }); };
    el.querySelectorAll(".opcoes .opcao").forEach((b) => b.addEventListener("click", () => {
      const v = b.dataset.v;
      if (p.k === "agua" && v === "barreiro") { ctx.set({ agua: v }); return; } // pede o volume antes de seguir
      q += 1;
      if (String(atual) === v) this.render(el, ctx); else ctx.set({ [p.k]: v });
    }));
    el.querySelectorAll(".area-rapido .chip").forEach((b) => b.addEventListener("click", () => ctx.set({ ha: b.dataset.v })));
    el.querySelectorAll(".area-mais").forEach((b) => b.addEventListener("click", () => {
      const v = Math.max(0.5, Math.min(50, Math.round((ctx.ef.ha + +b.dataset.d) * 2) / 2));
      ctx.set({ ha: String(v) });
    }));
    el.querySelector("#vol")?.addEventListener("change", (e) => ctx.set({ vol: e.target.value }));
    el.querySelector("#q-ant")?.addEventListener("click", () => { q = Math.max(0, q - 1); this.render(el, ctx); });
    el.querySelector("#q-prox").addEventListener("click", avancar);
  },
};
