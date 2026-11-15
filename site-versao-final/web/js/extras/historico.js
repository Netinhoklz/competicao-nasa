// QUADRA, módulo extra "historico" (pedido do José, 14/11/2026: "saber o que ele já plantou anteriormente no solo, entender melhor
// o que ele já faz e entender as suas experiências"). Três modos:
//   render(el, ctx, { modo: "pergunta" })  até 3 telas curtas: o que plantou em 2026 e 2025; o que deu bem e o que quebrou (motivo e
//                                          ano); o que já faz. Grava ctx.set({ antes, exp }).
//   render(el, ctx, { modo: "cartao" })    "Por onde começar o seu giro" (rodada 1; na rodada 2 saiu do Plano: o ano passado é pergunta de Sua roça e o efeito vai no "por quê" das partes).
//   render(el, ctx, { modo: "memoria" })   "A sua memória e os dados": cada quebra que ele lembra contra o que o IBGE anotou (era do "Se secar", que saiu da jornada na rodada 2: hoje nenhuma tela usa).
// Conversa com o "Como você planta hoje?" (extras/hoje_ideal.js): 2026 já vem marcado com o jeito de hoje, e "queima" e "semente",
// que o hoje já pergunta, não são perguntados de novo. Formatos de antes/exp e onde encaixar: integracao/area_historico.md.
import { lerHoje } from "./hoje_ideal.js";
import { CULT } from "./culturas.js";
import { olho } from "./voce_decide.js";

// ------------------------------------------------------------------ vocabulário
// Rodada 2 (15/11): as culturas novas de extras/culturas.js também valem em `antes` (Sua roça pergunta "o ano passado" com as
// culturas de hoje); as 8 de antes continuam iguais e na mesma ordem (o texto de `antes` segue a ordem de CULT_H).
const CAPINS = new Set(["sorgog", "milheto"]); // capins: não quebram o ciclo da lagarta (como milho e sorgo)
export const CULT_H = {
  milho: { nome: "Milho", icone: "milho", serie: "Milho", gram: true },
  feijao: { nome: "Feijão", icone: "feijao", serie: "Feijão" },
  mandioca: { nome: "Mandioca", icone: "mandioca", serie: "Mandioca" },
  sorgo: { nome: "Sorgo", icone: "milho", gram: true },
  palma: { nome: "Palma", icone: "palma" },
  algodao: { nome: "Algodão", icone: "algodao" },
  ...Object.fromEntries(Object.keys(CULT).filter((k) => !["milho", "feijao", "mandioca", "sorgo", "palma", "algodao", "outra"].includes(k))
    .map((k) => [k, { nome: CULT[k].nome, icone: CULT[k].icone, ...(CAPINS.has(k) ? { gram: true } : {}) }])),
  pousio: { nome: "Nada", sub: "pousio", icone: "pousio" },
  outra: { nome: "Outra", icone: "broto" },
};
// as telas do modo "pergunta" (páginas de teste, fora da jornada) seguem com as 8 de antes
const BASE_H = ["milho", "feijao", "mandioca", "sorgo", "palma", "algodao", "pousio", "outra"];
/** O ano do jeito de hoje (a safra de 2026, a última antes do plano de 2027); "o ano passado" de Sua roça é ANO_HOJE − 1. */
export const ANO_HOJE = 2026;
export const MOTIVOS = { seca: ["sol", "Seca"], chuva: ["chuva", "Chuva demais"], praga: ["praga", "Praga"], preco: ["dinheiro", "Preço ruim"], outro: ["interrog", "Outro"] };
export const PRATICAS = { naoqueima: ["semfogo", "Não queimo"], palha: ["palha", "Deixo a palhada"], faixas: ["faixas", "Planto em faixas"],
  semente: ["semente", "Guardo semente"], esterco: ["esterco", "Aduba com esterco"] };
export const ROCA = { trator: ["trator", "Trator"], animal: ["vaca", "Animal"], enxada: ["enxada", "Enxada"] };

// ícones que não estão em comum.js (mesmo traço 24×24)
const ICL = {
  algodao: '<path d="M12 21v-5.5"/><path d="M8.3 15.5a3 3 0 0 1-.9-5.8 3.3 3.3 0 0 1 4.6-3.5 3.3 3.3 0 0 1 4.6 3.5 3 3 0 0 1-.9 5.8z"/><path d="M9 18.5l3-2.5 3 2.5"/>',
  pousio: '<path d="M3 18h18M6 21h12"/><path d="M7 18v-3.5M7 14.5 5.4 12.2M7 14.5l1.6-2.3M16.5 18v-2.8M16.5 15.2l-1.3-1.8M16.5 15.2l1.3-1.8"/>',
  praga: '<circle cx="5" cy="15.5" r="2.3"/><circle cx="9.3" cy="14.8" r="2.4"/><circle cx="13.7" cy="14.2" r="2.5"/><circle cx="18.3" cy="12.4" r="2.8"/><path d="M17.6 9.6 16.8 6.5M19.8 9.8l1-3M5 18v2M9.3 17.4v2.4M13.7 16.9v2.6"/>',
  trator: '<circle cx="7.5" cy="16" r="4"/><circle cx="18" cy="17.5" r="2.5"/><path d="M4.5 12.2V6.5h6l1.8 5.5h6.7v3.3M9.5 6.5v5.5M11.5 16h4"/>',
  palha: '<path d="M3 18.5c3-1.6 6-1.6 9 0s6 1.6 9 0"/><path d="M4 15l6-3.5M8.5 15.5l6.5-4.2M13.5 15.5l6-3.6M6 11.5l2.5-5M14 10.5l1.5-4.5"/>',
  esterco: '<path d="M3.5 19.5h17"/><path d="M5.5 19.5c0-3 2.7-4.3 6.5-4.3s6.5 1.3 6.5 4.3M8.5 15.3c.2-2 1.5-3.1 3.5-3.1s3.3 1.1 3.5 3.1M10.5 12.3c0-1.3.6-2.3 1.5-2.8"/>',
  semfogo: '<path d="M12 21c-4 0-6.5-2.6-6.5-6.2 0-3.4 2.6-5.4 3.8-8.8 2.4 1.6 3.4 3.6 3.4 5.6 1-.8 1.6-2 1.8-3.4 2 1.8 4 4.2 4 6.8 0 3.4-2.5 6-6.5 6z"/><path d="M4 4l16 16"/>',
};
const icon = (U, nome, tam = "") => (ICL[nome] ? `<svg class="ic ${tam}" viewBox="0 0 24 24" aria-hidden="true">${ICL[nome]}</svg>` : U.ic(nome, tam));
/** Ícone do histórico (os de comum.js + algodao, pousio, praga, trator, palha, esterco, semfogo): icHist(ctx.util, "palha", "g"). */
export { icon as icHist };

const FONTE_IBGE = "IBGE, Produção Agrícola Municipal (PAM) 1998–2025: rendimento médio do município (kg/ha); normal = mediana dos anos da série";
const FONTE_REGRA = "regras do plano do QUADRA (ctx.r.plano): leguminosa antes do cereal (+24% no cereal seguinte, contra cereal solteiro; "
  + "síntese Zhao 2022, grau B); milho e sorgo são capins e não quebram o ciclo da lagarta-do-cartucho; contra o consórcio de hoje, não medido";
// lavoura grande no IBGE: o mesmo critério do passo 4 (js/passos/dinheiro/calculo.js, CONAB_FAMILIAR_KG_HA): mediana > 2× a familiar
const FAMILIAR_KG_HA = { Milho: 1800, "Feijão": 800, Mandioca: 17400 };

// ------------------------------------------------------------------ os textos de ctx.resp.antes e ctx.resp.exp
const lista = (s) => String(s || "").split(",").map((x) => x.trim()).filter(Boolean);

/** "2026:milho,feijao|2025:milho" → { 2026: ["milho", "feijao"], 2025: ["milho"] }. Cultura desconhecida é ignorada. */
export function lerAntes(txt) {
  const anos = {};
  for (const parte of String(txt || "").split("|")) {
    const [a, cs] = parte.split(":");
    const ks = lista(cs).filter((k) => CULT_H[k]);
    if (/^\d{4}$/.test(a || "") && ks.length) anos[+a] = ks.includes("pousio") ? ["pousio"] : ks;
  }
  return anos;
}
export function escreverAntes(anos) {
  return Object.keys(anos || {}).map(Number).sort((a, b) => b - a).filter((a) => anos[a]?.length)
    .map((a) => `${a}:${Object.keys(CULT_H).filter((k) => anos[a].includes(k)).join(",")}`).join("|");
}

/** "bem=feijao|quebra=milho:2024:seca,feijao::praga|faz=palha,esterco|roca=enxada" → { bem, quebras, faz, roca }. */
export function lerExp(txt) {
  const e = { bem: [], quebras: [], faz: [], roca: null };
  for (const parte of String(txt || "").split("|")) {
    const i = parte.indexOf("="), k = parte.slice(0, i), v = parte.slice(i + 1);
    if (i < 0) continue;
    if (k === "bem") e.bem = lista(v).filter((c) => CULT_H[c] && c !== "pousio");
    else if (k === "quebra") e.quebras = lista(v).map((q) => { const [c, a, m] = q.split(":"); return { c, ano: /^\d{4}$/.test(a || "") ? +a : null, mot: MOTIVOS[m] ? m : null }; })
      .filter((q) => CULT_H[q.c] && q.c !== "pousio");
    else if (k === "faz") e.faz = lista(v).filter((p) => PRATICAS[p]);
    else if (k === "roca") e.roca = ROCA[v] ? v : null;
  }
  return e;
}
export function escreverExp(e) {
  const p = [];
  if (e.bem?.length) p.push(`bem=${e.bem.join(",")}`);
  if (e.quebras?.length) p.push(`quebra=${e.quebras.map((q) => `${q.c}:${q.ano || ""}:${q.mot || ""}`.replace(/:+$/, "")).join(",")}`);
  if (e.faz?.length) p.push(`faz=${Object.keys(PRATICAS).filter((k) => e.faz.includes(k)).join(",")}`);
  if (e.roca) p.push(`roca=${e.roca}`);
  return p.join("|");
}

/** As chaves que o "Como você planta hoje?" já respondeu (só o que está escrito no texto, sem os padrões). */
function respondidoHoje(txt) {
  const kv = {};
  for (const p of String(txt || "").split("|").slice(1)) { const [k, v] = p.split("="); if (v === "1" || v === "0") kv[k] = +v; }
  return { queima: kv.queima ?? null, sem: kv.sem ?? null };
}

/**
 * Tudo o que o histórico sabe, para este módulo, o hoje_ideal e o plano: lerHistorico(ctx.resp, ctx.r.padroes).
 * { anos: {2026: [...], 2025: [...]}, bem, quebras: [{c, ano, mot}], faz, roca, queima (1/0/null), sem (1/0/null),
 *   origem: { queima: "hoje" | "historico" | null, sem: ..., anoHoje: "hoje" | null }, ultimo, penultimo, repetiu: [culturas nos 2 anos],
 *   capimRepetiu (milho/sorgo nos 2 anos), mandioca (mandioca no último ano), informado }
 * Sua roça (15/11) só pergunta "o ano passado" e grava `antes` = "2025:milho": aí o ano de hoje (a0 = 2026) é o jeito de hoje
 * (`hoje`), e origem.anoHoje = "hoje". Com o ano de hoje escrito em `antes` (formato antigo), vale o escrito.
 */
export function lerHistorico(resp, padroes = null, a0 = ANO_HOJE) {
  const anos = lerAntes(resp?.antes), e = lerExp(resp?.exp), hj = respondidoHoje(resp?.hoje);
  const hoje = lerHoje(resp?.hoje || "", padroes);
  let anoHoje = null;
  if (!anos[a0] && anos[a0 - 1]) {
    const ks = Object.keys(hoje.cult).filter((k) => CULT_H[k]);
    if (ks.length) { anos[a0] = ks; anoHoje = "hoje"; }
  }
  const queima = hj.queima ?? (e.faz.includes("naoqueima") ? 0 : null);
  const sem = hj.sem ?? (e.faz.includes("semente") ? 1 : null);
  const ys = Object.keys(anos).map(Number).sort((a, b) => b - a), ultimo = ys[0] || null, pen = ys[1] || null;
  const A = ultimo ? anos[ultimo] : [], B = pen && ultimo - pen === 1 ? anos[pen] : [];
  return {
    anos, bem: e.bem, quebras: e.quebras, faz: e.faz, roca: e.roca, queima, sem,
    origem: { queima: hj.queima != null ? "hoje" : queima != null ? "historico" : null, sem: hj.sem != null ? "hoje" : sem != null ? "historico" : null,
      anoHoje },
    ultimo, penultimo: pen,
    repetiu: A.filter((k) => B.includes(k) && k !== "pousio" && k !== "outra"),
    capimRepetiu: A.some((k) => CULT_H[k]?.gram) && B.some((k) => CULT_H[k]?.gram),
    mandioca: A.includes("mandioca") || (hoje.informado && (hoje.cult.mandioca || 0) > 0),
    informado: !!(resp?.antes || resp?.exp),
  };
}

// ------------------------------------------------------------------ cartão: "Por onde começar o seu giro" (sem DOM; roda no node)
const partes = (r) => (r?.plano?.faixas || []).filter((f) => /^Parte/.test(f.parte));

/** 1 a 3 recomendações a partir do histórico e do plano: [{ id, icone, cor, frase, sub, acao? }]. */
export function recomendacoes(r, ef, H) {
  const out = [], P = partes(r), plano = r?.plano?.faixas || [];
  const leg = P.find((f) => f.anos?.[0]?.tipo === "leguminosa");
  const mand = P.find((f) => /^Mandioca/.test(f.anos?.[0]?.cultura || ""));
  const baixio = plano.find((f) => f.parte === "Baixio");
  if (H.capimRepetiu) {
    const qual = H.repetiu.includes("milho") ? "milho" : H.repetiu.includes("sorgo") ? "sorgo" : "milho e sorgo";
    const legNome = leg ? leg.anos[0].cultura.toLowerCase() : "feijão";
    out.push({ id: "repetiu", icone: "feijao", cor: "ambar",
      frase: `A terra repetiu ${qual}: comece com o ${legNome} nesse lugar.`,
      sub: `${leg ? `${leg.parte} do plano. ` : ""}${qual === "milho" ? "Milho atrás de milho junta lagarta e cansa a terra."
        : "Sorgo é parente do milho: não quebra a lagarta."}` });
  }
  if (H.mandioca || ef?.maniva === "plantada") {
    if (mand) out.push({ id: "mandioca", icone: "mandioca", cor: "verde", frase: `A ${mand.parte} já começa com a sua mandioca.`,
      sub: "Deixe a maniva onde está: é a reserva do ano ruim.", acao: ef?.maniva !== "plantada" ? { maniva: "plantada" } : null });
    else out.push({ id: "mandioca", icone: "mandioca", cor: "ambar", frase: "O plano daqui não usa mandioca.",
      sub: "A sua segue como reserva: combine com o técnico." });
  }
  if (H.queima === 1) out.push({ id: "palha", icone: "palha", cor: "terra", frase: "Deixe a palhada: nada de fogo.", sub: "A palha segura a umidade e protege a terra." });
  const secaMilho = H.quebras.find((q) => q.c === "milho" && (q.mot === "seca" || !q.mot));
  if (secaMilho && baixio && ef?.tem_baixio !== false) {
    out.push({ id: "baixio", icone: "gota", cor: "azul", frase: `O milho quebrou${secaMilho.mot === "seca" ? " na seca" : ""}: no plano ele fica no baixio.`,
      sub: "A parte baixa guarda mais água." });
  }
  if (H.faz.includes("faixas")) out.push({ id: "faixas", icone: "faixas", cor: "verde", frase: "Você já planta em faixas.", sub: "O plano só dá nome a elas: A, B e C." });
  if (!out.length && Object.keys(H.anos).length) out.push({ id: "ordem", icone: "faixas", cor: "verde", frase: "Nada repetiu: siga a ordem A, B, C do plano.",
    sub: "Cada parte troca de cultura todo ano." });
  return out.slice(0, 3);
}

// ------------------------------------------------------------------ memória: cada quebra contra o IBGE (sem DOM)
/** Unidade da roça: milho e feijão em sacos de 60 kg/ha; mandioca em toneladas/ha. */
const emUn = (serie, kg) => (serie === "Mandioca" ? { v: kg / 1000, un: "t/ha", casas: 1 } : { v: kg / 60, un: "sacos/ha", casas: 1 });

/** Os anos de pior colheita da série (até k), do pior para o menos ruim. */
function piores(fin, serie, k = 3) {
  const H = fin?.historico_kg_ha, vs = H?.[serie];
  if (!vs) return [];
  return H.anos.map((a, i) => ({ ano: a, kg: vs[i] })).filter((x) => Number.isFinite(x.kg)).sort((a, b) => a.kg - b.kg).slice(0, k);
}

/**
 * Para cada quebra que ele contou: o que o IBGE anotou no município naquele ano.
 * [{ q, nome, serie, caso: "dado" | "sem_ano" | "sem_serie" | "ainda_nao" | "antes_da_serie" | "sem_dado_ano", kg, normal, rel,
 *    nivel: "quebra" | "caiu" | "normal", agro (IBGE de lavoura grande),
 *    meso (ano completado pela mesorregião), piores: [{ano, kg}] }]
 */
export function memorias(r, H) {
  const fin = r?.financeiro, KG = fin?.historico_kg_ha, ult = fin?.ultimo_ano_medido || KG?.anos?.at(-1);
  return H.quebras.map((q) => {
    const c = CULT_H[q.c], serie = c.serie, cu = fin?.culturas?.[serie], o = { q, nome: c.nome, serie };
    if (!serie || !(cu?.rend_mediano_kg_ha > 0) || !KG?.[serie]) return { ...o, caso: "sem_serie" };
    const normal = cu.rend_mediano_kg_ha;
    o.normal = normal;
    o.piores = piores(fin, serie);
    o.agro = normal > 2 * (FAMILIAR_KG_HA[serie] || Infinity);
    if (!q.ano) return { ...o, caso: "sem_ano" };
    if (q.ano > ult) return { ...o, caso: "ainda_nao", ult };
    const i = KG.anos.indexOf(q.ano);
    if (i < 0) return { ...o, caso: "antes_da_serie", ano0: KG.anos[0] };
    if (!Number.isFinite(KG[serie][i])) return { ...o, caso: "sem_dado_ano" };
    const kg = KG[serie][i], rel = kg / normal;
    const meso = fin.historico_R_ha?.[`origem_${serie}`]?.[fin.historico_R_ha.anos.indexOf(q.ano)] === "meso";
    return { ...o, caso: "dado", kg, rel, meso, nivel: rel < 0.5 ? "quebra" : rel < 0.8 ? "caiu" : "normal" };
  });
}

// ------------------------------------------------------------------ estado da tela (não é resposta)
let tela = 0; // pergunta atual (0..2; 3 = pronto)
let rasc = null, visto = ""; // o histórico em edição e o texto da última leitura
let deHoje = false; // 2026 veio marcado pelo "Como você planta hoje?"
const zerados = new WeakSet();

export default {
  id: "historico",
  titulo: "O que você já plantou",
  /** opcoes: { modo: "pergunta" | "cartao" | "memoria", tela, aoTerminar(H), aoVoltar(), linkSeguir, olho (cartão: false = sem "seu olho") } */
  async render(el, ctx, opcoes = {}) {
    const modo = ["cartao", "memoria"].includes(opcoes.modo) ? opcoes.modo : "pergunta";
    if (modo === "cartao") return desenharCartao(el, ctx, opcoes);
    if (modo === "memoria") return desenharMemoria(el, ctx);
    if (ctx.entrou && !zerados.has(ctx)) { zerados.add(ctx); tela = Number.isInteger(opcoes.tela) ? opcoes.tela : 0; rasc = null; }
    return desenharPergunta(el, ctx, opcoes, this);
  },
};

// ------------------------------------------------------------------ modo "pergunta"
const anosPergunta = (r) => { const a0 = (r?.plano?.anos?.[0] || 2027) - 1; return [a0, a0 - 1]; }; // 2026 e 2025

function novoRascunho(ctx) {
  const e = lerExp(ctx.resp?.exp), anos = lerAntes(ctx.resp?.antes), [a0] = anosPergunta(ctx.r);
  deHoje = false;
  const h = lerHoje(ctx.resp?.hoje || "", ctx.r?.padroes);
  if (!ctx.resp?.antes && h.informado) { // 2026 = o jeito de hoje (ele confirma ou muda)
    const ks = Object.keys(h.cult).filter((k) => CULT_H[k] && h.cult[k] > 0);
    if (ks.length) { anos[a0] = ks; deHoje = true; }
  }
  return { anos, bem: e.bem, quebras: e.quebras, faz: e.faz, roca: e.roca };
}

function topo(U, n, titulo, eco) {
  return `<div class="hs-topo"><p class="kicker">O que você já fez · ${n + 1} de 3</p>
    <div class="hs-barra">${[0, 1, 2].map((i) => `<i class="${i < n ? "feito" : i === n ? "atual" : ""}"></i>`).join("")}</div></div>
    <h1 class="hs-titulo">${U.esc(titulo)}<span class="eco">${U.esc(eco)}</span></h1>`;
}

const botaoCult = (U, k, marcada, attrs) => `<button type="button" class="hs-op ${marcada ? "marcada" : ""}" ${attrs} aria-pressed="${marcada}">
  ${icon(U, CULT_H[k].icone, "g")}<b>${CULT_H[k].nome}</b>${CULT_H[k].sub ? `<span>${CULT_H[k].sub}</span>` : ""}</button>`;

function telaAnos(ctx, U, h) {
  const [a0, a1] = anosPergunta(ctx.r);
  const bloco = (a) => `<div class="hs-ano">
    <p class="hs-ano-rot"><b>${a}</b>${a === a0 && deHoje ? `<span class="chip">do seu jeito de hoje</span>` : ""}
      ${a === a1 && h.anos[a0]?.length ? `<button type="button" class="chip hs-igual" data-igual="${a}">igual a ${a0}</button>` : ""}</p>
    <div class="hs-ops n8">${BASE_H.map((k) => botaoCult(U, k, (h.anos[a] || []).includes(k), `data-ano="${a}" data-c="${k}"`)).join("")}</div></div>`;
  return `${topo(U, 0, "O que você plantou", "no roçado nos últimos anos?")}
    <p class="hs-dica">Pode marcar mais de um.</p>${bloco(a0)}${bloco(a1)}`;
}

function telaDeu(ctx, U, h) {
  const [a0] = anosPergunta(ctx.r);
  const plantou = new Set(Object.values(h.anos).flat());
  const ks = BASE_H.filter((k) => k !== "pousio").sort((a, b) => plantou.has(b) - plantou.has(a));
  const anosQ = [a0, a0 - 1, a0 - 2, a0 - 3];
  const antigos = Array.from({ length: a0 - 4 - 1990 + 1 }, (_, i) => a0 - 4 - i);
  const detalhe = (q) => `<div class="hs-quebra">
    <p class="hs-q-rot">${icon(U, CULT_H[q.c].icone)}<b>${CULT_H[q.c].nome}</b> quebrou por…</p>
    <div class="hs-motivos">${Object.entries(MOTIVOS).map(([m, [i, t]]) => `<button type="button" class="hs-mot ${q.mot === m ? "marcada" : ""}" data-qc="${q.c}" data-mot="${m}" aria-pressed="${q.mot === m}">
      ${icon(U, i, "g")}<span>${t}</span></button>`).join("")}</div>
    <p class="hs-q-rot pequeno">Em que ano? <span class="sub">se lembrar</span></p>
    <div class="hs-anos">${anosQ.map((a) => `<button type="button" class="chip ${q.ano === a ? "verde" : ""}" data-qc="${q.c}" data-qano="${a}">${a}</button>`).join("")}
      <select class="hs-sel" data-qc="${q.c}" aria-label="ano mais antigo"><option value="">antes</option>${antigos.map((a) => `<option value="${a}" ${q.ano === a ? "selected" : ""}>${a}</option>`).join("")}</select>
      <button type="button" class="chip ${!q.ano ? "verde" : ""}" data-qc="${q.c}" data-qano="">não lembro</button></div></div>`;
  return `${topo(U, 1, "O que deu certo", "e o que deu errado?")}
    <div class="hs-bloco"><p class="hs-rot verde">${U.ic("ok")}<span>Deu bem</span></p>
      <div class="hs-ops n7">${ks.map((k) => botaoCult(U, k, h.bem.includes(k), `data-bem="${k}"`)).join("")}</div></div>
    <div class="hs-bloco"><p class="hs-rot terra">${U.ic("alerta")}<span>Quebrou</span></p>
      <div class="hs-ops n7">${ks.map((k) => botaoCult(U, k, h.quebras.some((q) => q.c === k), `data-quebra="${k}"`)).join("")}</div>
      ${h.quebras.map(detalhe).join("")}</div>`;
}

function telaFaz(ctx, U, h) {
  const hj = respondidoHoje(ctx.resp?.hoje);
  const ja = []; // o que o "Como você planta hoje?" já anotou: não pergunta de novo
  if (hj.queima != null) ja.push(hj.queima ? ["fogo", "Queima o roçado"] : ["semfogo", "Não queima"]);
  if (hj.sem != null) ja.push(hj.sem ? ["semente", "Guarda semente"] : ["dinheiro", "Compra semente"]);
  const ks = Object.keys(PRATICAS).filter((k) => !(k === "naoqueima" && hj.queima != null) && !(k === "semente" && hj.sem != null));
  return `${topo(U, 2, "O que você", "já faz no roçado?")}
    <div class="hs-ops n${ks.length}">${ks.map((k) => { const [i, t] = PRATICAS[k], m = h.faz.includes(k);
      return `<button type="button" class="hs-op ${m ? "marcada" : ""}" data-faz="${k}" aria-pressed="${m}">${icon(U, i, "g")}<b>${t}</b></button>`; }).join("")}</div>
    ${ja.length ? `<p class="hs-ja">${U.ic("ok")}<span>Já anotado no seu jeito de hoje:</span>${ja.map(([i, t]) => `<span class="chip">${icon(U, i)}${t}</span>`).join("")}</p>` : ""}
    <div class="hs-bloco"><p class="hs-rot">${U.ic("enxada")}<span>Como você prepara a terra?</span></p>
      <div class="hs-ops n3">${Object.entries(ROCA).map(([k, [i, t]]) => `<button type="button" class="hs-op ${h.roca === k ? "marcada" : ""}" data-roca="${k}" aria-pressed="${h.roca === k}">
        ${icon(U, i, "g")}<b>${t}</b></button>`).join("")}</div></div>`;
}

/** Fichas do resumo: [ícone, texto, tela]. */
export function resumoHistorico(H, U) {
  const nomes = (ks) => ks.map((k) => (k === "pousio" ? "pousio" : CULT_H[k].nome)).join(", ");
  const fs = Object.keys(H.anos).map(Number).sort((a, b) => b - a).map((a) => [CULT_H[H.anos[a][0]].icone, `${a}: ${nomes(H.anos[a])}`, 0]);
  if (!fs.length) fs.push(["interrog", "Anos: não sei", 0]);
  if (H.bem.length) fs.push(["ok", `Deu bem: ${nomes(H.bem)}`, 1]);
  for (const q of H.quebras) fs.push(["alerta", `Quebrou: ${CULT_H[q.c].nome.toLowerCase()}${q.ano ? ` ${q.ano}` : ""}${q.mot ? ` (${MOTIVOS[q.mot][1].toLowerCase()})` : ""}`, 1]);
  if (H.faz.length) fs.push([PRATICAS[H.faz[0]][0], `Faz: ${H.faz.map((k) => PRATICAS[k][1].toLowerCase()).join(", ")}`, 2]);
  if (H.roca) fs.push([ROCA[H.roca][0], `Prepara a terra: ${ROCA[H.roca][1].toLowerCase()}`, 2]);
  return fs;
}

function desenharPergunta(el, ctx, opcoes, mod) {
  const U = ctx.util, txt = `${ctx.resp?.antes || ""}#${ctx.resp?.exp || ""}`;
  if (!rasc || txt !== visto) { rasc = novoRascunho(ctx); visto = txt; }
  const h = rasc;
  const textos = () => ({ antes: escreverAntes(h.anos), exp: escreverExp(h) });
  const gravar = () => { const t = textos(); visto = `${t.antes}#${t.exp}`; ctx.set(t); };
  const redesenhar = () => mod.render(el, ctx, opcoes);
  const ir = (n) => { tela = n; redesenhar(); if (n >= 3) opcoes.aoTerminar?.(lerHistorico({ ...ctx.resp, ...textos() }, ctx.r?.padroes)); };

  if (tela >= 3) {
    const H = lerHistorico({ ...ctx.resp, ...textos() }, ctx.r?.padroes);
    el.innerHTML = `<div class="hs hs-pergunta hs-pronto">
      <div class="titulo-passo"><p class="kicker">O que você já fez</p><h1>Anotado.<span class="eco">A sua experiência entra no plano.</span></h1></div>
      <div class="hs-fichas">${resumoHistorico(H, U).map(([i, t, n]) => `<button type="button" class="hs-ficha" data-q="${n}">${icon(U, i)}<span>${U.esc(t)}</span><em>mudar</em></button>`).join("")}</div>
      ${opcoes.linkSeguir ? `<a class="botao primario cta" href="${opcoes.linkSeguir}"><span>Seguir</span>${U.ic("seta")}</a>` : ""}</div>`;
    el.querySelectorAll(".hs-ficha").forEach((b) => b.addEventListener("click", () => ir(+b.dataset.q)));
    return;
  }
  const corpo = tela === 0 ? telaAnos(ctx, U, h) : tela === 1 ? telaDeu(ctx, U, h) : telaFaz(ctx, U, h);
  el.innerHTML = `<div class="hs hs-pergunta">${corpo}
    <div class="hs-nav">
      <button type="button" class="botao secundario hs-ant" id="hs-ant" ${tela === 0 && !opcoes.aoVoltar ? "disabled" : ""} aria-label="Anterior">${U.ic("volta")}<span>Anterior</span></button>
      <button type="button" class="botao secundario" id="hs-pular">${U.ic("interrog")}<span>Não sei<span class="hs-pular-txt"> / pular</span></span></button>
      <button type="button" class="botao primario" id="hs-prox">${tela === 2 ? `Pronto ${U.ic("ok")}` : `Próxima ${U.ic("seta")}`}</button>
    </div></div>`;
  const raiz = el.firstElementChild;
  raiz.querySelector("#hs-ant").addEventListener("click", () => { gravar(); if (tela === 0) opcoes.aoVoltar?.(); else ir(tela - 1); });
  raiz.querySelector("#hs-prox").addEventListener("click", () => { gravar(); ir(tela + 1); });
  raiz.querySelector("#hs-pular").addEventListener("click", () => { // "não sei": esta tela fica em branco (vale o padrão)
    if (tela === 0) { h.anos = {}; deHoje = false; } else if (tela === 1) { h.bem = []; h.quebras = []; } else { h.faz = []; h.roca = null; }
    gravar();
    ir(tela + 1);
  });
  // tela 1: culturas por ano ("nada/pousio" é sozinho)
  raiz.querySelectorAll("[data-ano][data-c]").forEach((b) => b.addEventListener("click", () => {
    const a = +b.dataset.ano, k = b.dataset.c, cur = h.anos[a] || [];
    h.anos[a] = k === "pousio" ? (cur.includes("pousio") ? [] : ["pousio"]) : cur.includes(k) ? cur.filter((x) => x !== k) : [...cur.filter((x) => x !== "pousio"), k];
    if (!h.anos[a].length) delete h.anos[a];
    redesenhar();
  }));
  raiz.querySelector("[data-igual]")?.addEventListener("click", (ev) => { const [a0] = anosPergunta(ctx.r); h.anos[+ev.currentTarget.dataset.igual] = [...(h.anos[a0] || [])]; redesenhar(); });
  // tela 2: deu bem / quebrou, com o motivo e o ano
  raiz.querySelectorAll("[data-bem]").forEach((b) => b.addEventListener("click", () => {
    const k = b.dataset.bem;
    h.bem = h.bem.includes(k) ? h.bem.filter((x) => x !== k) : [...h.bem, k];
    redesenhar();
  }));
  raiz.querySelectorAll("[data-quebra]").forEach((b) => b.addEventListener("click", () => {
    const k = b.dataset.quebra;
    h.quebras = h.quebras.some((q) => q.c === k) ? h.quebras.filter((q) => q.c !== k) : [...h.quebras, { c: k, ano: null, mot: null }];
    redesenhar();
  }));
  const quebraDe = (c) => h.quebras.find((q) => q.c === c);
  raiz.querySelectorAll("[data-mot]").forEach((b) => b.addEventListener("click", () => { const q = quebraDe(b.dataset.qc); q.mot = q.mot === b.dataset.mot ? null : b.dataset.mot; redesenhar(); }));
  raiz.querySelectorAll("[data-qano]").forEach((b) => b.addEventListener("click", () => { quebraDe(b.dataset.qc).ano = b.dataset.qano ? +b.dataset.qano : null; redesenhar(); }));
  raiz.querySelectorAll(".hs-sel").forEach((s) => s.addEventListener("change", () => { quebraDe(s.dataset.qc).ano = s.value ? +s.value : null; redesenhar(); }));
  // tela 3: o que já faz
  raiz.querySelectorAll("[data-faz]").forEach((b) => b.addEventListener("click", () => {
    const k = b.dataset.faz;
    h.faz = h.faz.includes(k) ? h.faz.filter((x) => x !== k) : [...h.faz, k];
    redesenhar();
  }));
  raiz.querySelectorAll("[data-roca]").forEach((b) => b.addEventListener("click", () => { h.roca = h.roca === b.dataset.roca ? null : b.dataset.roca; redesenhar(); }));
}

// ------------------------------------------------------------------ modo "cartao" (passo 3)
// Sem resposta: supõe 2026 e 2025 iguais ao jeito de hoje e mostra o giro com "Se em 2025 também foi assim"; 2 chips gravam ali mesmo.
function desenharCartao(el, ctx, opcoes) {
  const U = ctx.util, [a0, a1] = anosPergunta(ctx.r);
  const ks = Object.keys(lerHoje(ctx.resp?.hoje || "", ctx.r?.padroes).cult).filter((k) => CULT_H[k]);
  const mesmo = escreverAntes({ [a0]: ks, [a1]: ks }), mudei = escreverAntes({ [a0]: ks });
  const suposto = !ctx.resp?.antes;
  // com a maniva já no chão, a linha da mandioca do plano (logo acima) já diz isso: o cartão não repete
  const H = lerHistorico(suposto ? { ...ctx.resp, antes: mesmo } : ctx.resp, ctx.r?.padroes),
    recs = recomendacoes(ctx.r, ctx.ef, H).filter((x) => !(x.id === "mandioca" && ctx.ef?.maniva === "plantada"));
  const marcado = ctx.resp?.antes === mesmo ? "mesmo" : ctx.resp?.antes === mudei ? "mudei" : "";
  const nomes = ks.map((k) => CULT_H[k].nome.toLowerCase());
  const se = suposto && recs.length ? `<p class="hs-se">Se em ${a1} também foi assim (${U.esc(nomes.length > 1 ? nomes.slice(0, -1).join(", ") + " e " + nomes.at(-1) : nomes[0])}):</p>` : "";
  const lista = recs.length ? `<ul class="hs-recs">${recs.map((x) => `<li><span class="bola ${x.cor}">${icon(U, x.icone)}</span>
      <div><b>${U.esc(x.frase)}</b><span>${U.esc(x.sub)}</span>
      ${x.acao ? `<button type="button" class="chip verde hs-acao" data-acao='${U.esc(JSON.stringify(x.acao))}'>${U.ic("ok")} Já está plantada: avisar o plano</button>` : ""}</div></li>`).join("")}</ul>` : "";
  const chips = ks.length ? `<p class="hs-giro-q">Em ${a1}, plantou no mesmo chão de ${a0}?</p>
    <div class="hs-giro-chips" role="group" aria-label="Onde plantou em ${a1}">${[["mesmo", mesmo, "Sim, no mesmo chão"], ["mudei", mudei, "Não, mudei"]]
    .map(([id, v, t]) => `<button type="button" class="chip${marcado === id ? " verde" : ""}" data-antes="${U.esc(v)}" aria-pressed="${marcado === id}">
      ${marcado === id ? U.ic("ok") : ""}${t}</button>`).join("")}</div>` : "";
  const fonte = FONTE_REGRA + (suposto ? `; ${a0} e ${a1} supostos iguais ao jeito de hoje até você responder` : "");
  el.innerHTML = `<div class="hs hs-cartao painel">
    <p class="hs-rot">${U.ic("faixas")}<span>Por onde começar o seu giro</span>${recs.length ? U.selo("suposicao", fonte) : ""}</p>
    ${se}${lista}${chips}
    ${recs.length && opcoes.olho !== false ? olho("Você conhece a sua terra: se não bater, vale a sua experiência.") : ""}</div>`;
  el.querySelectorAll("[data-acao]").forEach((b) => b.addEventListener("click", () => ctx.set(JSON.parse(b.dataset.acao))));
  el.querySelectorAll("[data-antes]").forEach((b) => b.addEventListener("click", () => {
    if (ctx.resp?.antes !== b.dataset.antes) ctx.set({ antes: b.dataset.antes });
  }));
}

// ------------------------------------------------------------------ modo "memoria" (era do "Se secar"; fora da jornada na rodada 2)
const MEM_CULT = [["milho", "Milho"], ["feijao", "Feijão"]]; // as culturas com chips de ano (série do IBGE)

function desenharMemoria(el, ctx) {
  const U = ctx.util, r = ctx.r, H = lerHistorico(ctx.resp, r?.padroes), ms = memorias(r, H), fin = r?.financeiro;
  const mun = r?.local?.municipio || "aqui";
  const fmt = (serie, kg) => { const u = emUn(serie, kg); return `${U.num(u.v, u.v < 10 ? u.casas : 0)} ${u.un}`; };
  const fmtV = (serie, kg) => { const u = emUn(serie, kg); return U.num(u.v, u.v < 10 ? u.casas : 0); };
  const pioresTxt = (m) => m.piores.map((p) => `${p.ano} (${fmtV(m.serie, p.kg)})`).join(", ");
  const cores = { quebra: "terra", caiu: "ambar", normal: "azul" };
  const veredito = (m) => {
    if (m.q.mot === "preco") return m.nivel === "normal" ? "A colheita daqui foi normal: o problema foi o preço, como você lembra."
      : "O município também colheu pouco. O preço o IBGE não mostra.";
    return m.nivel === "quebra" ? "Bate: o município todo quebrou nesse ano." : m.nivel === "caiu" ? "Bate em parte: o município caiu, mas menos."
      : "Aqui o dado não mostra quebra: a sua roça pode ser diferente da média. Vale a sua experiência.";
  };
  const item = (m, i) => {
    const q = m.q, mot = q.mot ? ` <span class="hs-mot-tag">${icon(U, MOTIVOS[q.mot][0])}${MOTIVOS[q.mot][1].toLowerCase()}</span>` : "";
    const voce = `<p class="hs-mem-voce">${icon(U, CULT_H[q.c].icone)}<span>Você lembra: <b>${U.esc(m.nome.toLowerCase())} quebrou${q.ano ? ` em ${q.ano}` : ""}</b>${mot}</span>
      <button type="button" class="hs-tirar" data-tirar="${i}">desfazer</button></p>`;
    if (m.caso === "dado") {
      const w = Math.min(100, (m.rel / 1.5) * 100);
      return `<div class="hs-mem ${cores[m.nivel]}">${voce}
        <p class="hs-mem-dado">O IBGE anotou <b>${fmt(m.serie, m.kg)}</b> em ${U.esc(mun)} <span class="sub">(normal ${fmtV(m.serie, m.normal)})</span></p>
        <div class="hs-barra-rel" role="img" aria-label="${Math.round(m.rel * 100)}% do normal"><i style="width:${w}%"></i><em style="left:${100 / 1.5}%"></em></div>
        <p class="hs-mem-rel"><b>${Math.round(m.rel * 100)}%</b> do normal${m.meso ? " · ano completado pela região" : ""}</p>
        <p class="hs-mem-ver">${veredito(m)}</p>
        ${m.agro ? `<p class="hs-mem-nota">Aqui o IBGE mistura lavoura grande: a média fica acima da roça de família.</p>` : ""}</div>`;
    }
    const nota = {
      sem_ano: `Não lembra o ano? Os piores daqui no IBGE: ${m.piores?.length ? pioresTxt(m) : "—"} <span class="sub">(${emUn(m.serie, 1).un})</span>.`,
      sem_serie: `O IBGE daqui não tem a série ${m.nome === "Outra" ? "dessa cultura" : `do ${m.nome.toLowerCase()}`}: vale a sua memória.`,
      ainda_nao: `O IBGE ainda não publicou ${q.ano} (o último é ${m.ult}).`,
      antes_da_serie: `A série do IBGE daqui começa em ${m.ano0}: vale a sua memória.`,
      sem_dado_ano: `O IBGE não anotou ${q.ano} aqui: vale a sua memória.`,
    }[m.caso];
    const escolher = m.caso === "sem_ano" && m.piores?.length ? `<div class="hs-anos">${m.piores.map((p) =>
      `<button type="button" class="chip" data-mem-c="${q.c}" data-mem-ano="${p.ano}">foi em ${p.ano}</button>`).join("")}</div>` : "";
    return `<div class="hs-mem neutro">${voce}<p class="hs-mem-dado">${nota}</p>${escolher}</div>`;
  };
  // por cultura ainda sem quebra contada: os 3 piores anos daqui no IBGE e "outro ano"; o toque grava ali mesmo (sem sair do passo)
  const contadas = new Set(H.quebras.map((q) => q.c));
  const ss = MEM_CULT.filter(([k, s]) => fin?.historico_kg_ha?.[s] && !contadas.has(k));
  const anosSerie = [...(fin?.historico_kg_ha?.anos || [])].reverse();
  const linhaAnos = ([k, s]) => `<div class="hs-mem-linha"><p>${U.ic(CULT_H[k].icone)}<b>${CULT_H[k].nome}</b></p>
    <div class="hs-anos">${piores(fin, s).map((p) => `<button type="button" class="chip" data-quebrou="${k}" data-quebrou-ano="${p.ano}">${p.ano}</button>`).join("")}
      <select class="hs-sel" data-quebrou="${k}" aria-label="Outro ano em que o ${CULT_H[k].nome.toLowerCase()} quebrou"><option value="">outro ano</option></select>
    </div></div>`;
  const pergunta = ss.length ? `<p class="hs-vazio">${U.ic("calendario")}<span>${ms.length ? "Lembra de outro ano ruim?" : "Lembra de um ano que quebrou?"}</span></p>
    <div class="hs-mem-anos">${ss.map(linhaAnos).join("")}</div>` : "";
  let corpo;
  if (ms.length) corpo = `<div class="hs-mems">${ms.map(item).join("")}</div>${pergunta}`;
  else {
    const so = MEM_CULT.map(([, s]) => s).filter((s) => fin?.historico_kg_ha?.[s]);
    corpo = (pergunta || `<p class="sub">Sem série do IBGE para este município.</p>`)
      + (so.some((s) => fin.culturas?.[s]?.rend_mediano_kg_ha > 2 * FAMILIAR_KG_HA[s]) ? `<p class="hs-mem-nota">Aqui o IBGE mistura lavoura grande: a média fica acima da roça de família.</p>` : "");
  }
  const discorda = ms.some((m) => m.caso === "dado" && m.nivel === "normal" && m.q.mot !== "preco");
  el.innerHTML = `<div class="hs hs-memoria painel">
    <p class="hs-rot">${U.ic("calendario")}<span>A sua memória e os dados</span>${fin ? U.selo("medido", FONTE_IBGE) : ""}</p>
    ${corpo}
    ${olho(discorda ? "O roçado da sua família pode ser diferente da média daqui." : "Vale a sua memória: o IBGE só vê a média.")}
    ${U.verMais(`<p>O número do IBGE é a média do município inteiro, de quem planta muito e de quem planta pouco (Produção Agrícola Municipal,
      1998–${fin?.ultimo_ano_medido || 2025}). Milho e feijão em sacos de 60 kg por hectare; mandioca em toneladas por hectare. "Normal" é a
      mediana dos anos da série. Abaixo da metade do normal chamamos de quebra (a mesma régua de Quanto rende); entre metade e 80%, o ano caiu;
      acima disso, foi normal. Lavoura grande: a mediana daqui passa do dobro do rendimento da lavoura familiar da CONAB.
      ${fin?.culturas?.["Feijão"]?.aviso ? `Feijão: ${U.esc(fin.culturas["Feijão"].aviso)}.` : ""} Quando a sua lembrança e o dado discordam,
      vale a sua: a roça de uma família pode quebrar num ano em que o município foi bem.</p>`, "O que o IBGE chama de quebra")}</div>`;
  el.querySelectorAll("[data-mem-ano]").forEach((b) => b.addEventListener("click", () => {
    const e = lerExp(ctx.resp?.exp), q = e.quebras.find((x) => x.c === b.dataset.memC);
    if (q) { q.ano = +b.dataset.memAno; ctx.set({ exp: escreverExp(e) }); }
  }));
  const quebrou = (c, ano) => { const e = lerExp(ctx.resp?.exp); ctx.set({ exp: escreverExp({ ...e, quebras: [...e.quebras, { c, ano }] }) }); };
  el.querySelectorAll("button[data-quebrou-ano]").forEach((b) => b.addEventListener("click", () => quebrou(b.dataset.quebrou, +b.dataset.quebrouAno)));
  el.querySelectorAll("select[data-quebrou]").forEach((s) => {
    // os 28 anos entram só no toque: fora dele não pesam no texto da tela
    const encher = () => { if (s.options.length < 2) s.insertAdjacentHTML("beforeend", anosSerie.map((a) => `<option value="${a}">${a}</option>`).join("")); };
    s.addEventListener("pointerdown", encher);
    s.addEventListener("focus", encher);
    s.addEventListener("change", () => { if (s.value) quebrou(s.dataset.quebrou, +s.value); });
  });
  el.querySelectorAll("[data-tirar]").forEach((b) => b.addEventListener("click", () => {
    const e = lerExp(ctx.resp?.exp);
    e.quebras.splice(+b.dataset.tirar, 1);
    ctx.set({ exp: escreverExp(e) });
  }));
}
