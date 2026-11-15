// QUADRA, site final: bloco extra "Outros jeitos de girar o roçado" (pontos 8 e 9 do desafio Field Shift).
// Monta no navegador, só a partir de ctx.r (cardápio, plano, financeiro), três rotações ligadas às prioridades do agricultor
// ("Guardar água", "Mais renda", "Cuidar do solo") e o plano do QUADRA como referência, e compara os quatro em 7 pontos
// (adubo natural, chão coberto, palhada, quebra de praga, uso de água, comida do gado, renda) com 1 a 3 pontinhos.
// Só entram culturas que o cardápio deixa no município (situação diferente de "fora"); sem maniva, a mandioca sai.
// No passo 4 o bloco é "O que vale mais para você?": as abas (Água · Renda · Solo · Um pouco de cada, que é o plano) são a pergunta da prioridade e gravam
// ctx.ef.prioridade (ctx.set); o jeito aceso é o da prioridade. No celular, a grade e o giro ano a ano ficam em "Ver a comparação".
// Regras de pontuação e evidência no "Ver como pontuamos"; graus e cartões de pesquisa/catalogo_rotacoes.json (ids nos comentários).
// Uso: import cenarios from "./extras/cenarios.js"; await cenarios.render(el, ctx, { painel: true });
import * as U from "../comum.js";

const IDS = ["agua", "renda", "solo", "plano"];
const NOME = { agua: "Guardar água", renda: "Mais renda", solo: "Cuidar do solo", plano: "Plano do QUADRA" };
const CURTO = { agua: "Água", renda: "Renda", solo: "Solo", plano: "Plano" };
// nas abas a pergunta é "O que vale mais para você?": ninguém responde "o plano"; o plano é o equilíbrio
const ABA = { ...CURTO, plano: "Um pouco de cada" };
const ICONE = { agua: "gota", renda: "dinheiro", solo: "broto", plano: "faixas" };
const COR = { agua: "azul", renda: "ambar", solo: "verde", plano: "verde" };
const DA_PRIORIDADE = { garantir: "agua", vender: "renda", equilibrar: "plano", solo: "solo" };
const INV = { agua: "garantir", renda: "vender", solo: "solo", plano: "equilibrar" }; // a aba tocada → a prioridade gravada

// Código de cada parte do roçado num ano:
// L leguminosa de grão · C cereal solteiro (milho ou sorgo de grão) · Z milho com feijão no pé · U milho com mucuna no pé ·
// F forragem anual (sorgo forrageiro, milheto) · M1/M2 mandioca no ano do plantio / da colheita · P1/P palma no 1º ano / já cortável ·
// G1/G leguminosa perene no 1º ano / crescida (gliricídia com palma, ou guandu) · O pousio.
// Nível 0, 1 ou 2 por ponto (SUPOSIÇÃO, regras no "ver mais"); gram = gramínea, hospedeira da lagarta-do-cartucho
// (milho com feijão no pé = meia gramínea: metade das linhas é feijão, como no passo 4).
const NIVEL = {
  L: { adubo: 2, chao: 1, palha: 1, gado: 0, gram: 0 },
  C: { adubo: 0, chao: 1, palha: 2, gado: 1, gram: 1 },
  Z: { adubo: 1, chao: 2, palha: 2, gado: 1, gram: 0.5 },
  U: { adubo: 1, chao: 2, palha: 2, gado: 1, gram: 1 },
  F: { adubo: 0, chao: 2, palha: 1, gado: 2, gram: 1 },
  M1: { adubo: 0, chao: 0, palha: 1, gado: 0, gram: 0 },
  M2: { adubo: 0, chao: 2, palha: 1, gado: 1, gram: 0 },
  P1: { adubo: 0, chao: 1, palha: 0, gado: 0, gram: 0 },
  P: { adubo: 0, chao: 1, palha: 0, gado: 2, gram: 0 },
  G1: { adubo: 1, chao: 1, palha: 0, gado: 0, gram: 0 },
  G: { adubo: 2, chao: 2, palha: 2, gado: 2, gram: 0 },
  O: { adubo: 0, chao: 1, palha: 1, gado: 1, gram: 0 },
};
// Dias de ciclo na chuva (uso de água): caupi 60–75 d e milho ~110 d do calendário do motor; o resto é suposição.
const DIAS_CULT = { "Feijão-caupi": 70, "Feijão comum": 85, Amendoim: 100, Milho: 110, "Sorgo granífero": 110, "Sorgo forrageiro": 105, Milheto: 90 };
const DIAS_COD = { Z: 145, U: 145, M1: 120, M2: 60, P1: 60, P: 60, G1: 60, G: 60, O: 0 };
const ENRAIZADA = new Set(["M2", "P", "G"]); // já no chão desde o ano anterior: conta o risco mais baixo do ZARC (20%)

// Os três jeitos (linhas: Parte A, B, C, baixio; colunas: 2027, 2028, 2029). "com" = há mandioca; "sem" = sem mandioca (fora do
// cardápio ou sem maniva). Cada código passa por celula(), que troca o que não serve aqui pelo parecido que serve.
const MODELOS = {
  agua: { com: ["M1 M2 L", "P1 P P", "F M1 M2", "S L S"], sem: ["F L F", "P1 P P", "L S F", "S L S"] },
  renda: { com: ["M1 M2 L", "L M1 M2", "M1 M2 L", "L Z L"], sem: ["L F L", "L S L", "L F L", "L Z L"] },
  solo: { com: ["L S L", "F L S", "G1 G G", "U L U"] },
};

const PONTOS = [
  { id: "adubo", rot: "Adubo natural", ic: "feijao", curto: "adubo", delta: 0.15 },
  { id: "chao", rot: "Chão coberto", ic: "chuva", curto: "chão coberto", delta: 0.15 },
  { id: "palha", rot: "Palhada", ic: "broto", curto: "palhada", delta: 0.15 },
  { id: "praga", rot: "Quebra de praga", ic: "escudo", curto: "praga", delta: 0.05, menor: true },
  { id: "agua", rot: "Pouca água", ic: "gota", curto: "água", delta: 0.06, menor: true },
  { id: "gado", rot: "Comida do gado", ic: "vaca", curto: "gado", delta: 0.15 },
  { id: "renda", rot: "Renda", ic: "dinheiro", curto: "renda", delta: null },
];

// Produtividade das planilhas familiares da CONAB (kg/ha); acima de 2× = lavoura grande na série do IBGE.
// Mesma regra do passo 4 (js/passos/dinheiro/calculo.js, CONAB_FAMILIAR_KG_HA).
const CONAB_FAMILIAR_KG_HA = { Milho: 1800, "Feijão": 800, Mandioca: 17400 };
const SERIE = { "Feijão-caupi": "Feijão", "Feijão comum": "Feijão", Milho: "Milho" };

// ---------------------------------------------------------------- montar os quatro jeitos
function recursos(r, ef) {
  const card = new Map((r.cardapio || []).map((c) => [c.cultura, c]));
  const serve = (n) => { const c = card.get(n); return !!c && c.situacao !== "fora"; };
  const pri = (...ns) => ns.find(serve) || null;
  const legPlano = r.plano?.leguminosa;
  return {
    card,
    leg: legPlano && serve(legPlano) ? legPlano : pri("Feijão-caupi", "Feijão comum", "Amendoim"),
    mand: serve("Mandioca") && ef.maniva !== "nao",
    semManiva: serve("Mandioca") && ef.maniva === "nao",
    forr: pri("Sorgo forrageiro", "Milheto"),
    sorgo: pri("Sorgo granífero"),
    milho: serve("Milho"),
    palma: serve("Palma forrageira"),
    mucuna: serve("Mucuna-preta"),
    perene: serve("Gliricídia") ? "Gliricídia" : pri("Guandu"),
    fora: (r.cardapio || []).filter((c) => c.situacao === "fora").map((c) => c.cultura),
  };
}

/** Código do modelo → célula com uma cultura que serve aqui (ou a parecida que serve). */
function celula(cod, R) {
  switch (cod) {
    case "L": return R.leg ? { k: "L", nome: R.leg } : celula("F", R);
    case "S": return R.sorgo ? { k: "C", nome: R.sorgo } : R.milho ? { k: "C", nome: "Milho" } : R.forr ? { k: "F", nome: R.forr } : { k: "O", nome: "Pousio" };
    case "F": return R.forr ? { k: "F", nome: R.forr } : R.sorgo ? { k: "C", nome: R.sorgo } : { k: "O", nome: "Pousio" };
    case "P1": case "P": return R.palma ? { k: cod, nome: "Palma forrageira" } : celula("F", R);
    case "Z": return R.milho && R.leg ? { k: "Z", nome: "Milho", par: R.leg } : celula("S", R);
    case "U": return R.milho && R.mucuna ? { k: "U", nome: "Milho", par: "Mucuna-preta" } : celula("Z", R);
    case "G1": case "G": // gliricídia junto da palma, longe do grão (cartão martins_gliricidia_forrageira); sem ela, guandu
      return R.perene ? { k: cod, nome: R.perene, par: R.perene === "Gliricídia" && R.palma ? "Palma forrageira" : null } : celula(cod === "G1" ? "L" : "F", R);
    default: return { k: cod, nome: "Mandioca" }; // M1, M2
  }
}

/** O plano do motor (ctx.r.plano.faixas, sem as bordas) nos mesmos códigos. */
function linhasDoPlano(r) {
  const leg = r.plano?.leguminosa || "Feijão-caupi";
  return (r.plano?.faixas || []).filter((f) => f.parte !== "Bordas").map((f) => {
    let ant = null;
    const cels = f.anos.map((a) => {
      const c = a.cultura || "", t = a.tipo || "", tx = a.texto || "";
      let cel;
      if (/mandioca/i.test(c)) cel = { k: ant === "M1" ? "M2" : "M1", nome: "Mandioca" };
      else if (/pousio/i.test(c) || t === "pousio") cel = { k: "O", nome: c };
      else if (t === "leguminosa" && !/guandu/i.test(c)) cel = { k: "L", nome: c };
      else if (t === "forragem") cel = { k: "F", nome: c };
      else if (/palma/i.test(c)) cel = { k: ant === "P1" || ant === "P" ? "P" : "P1", nome: "Palma forrageira" };
      else if (t === "perene" || t === "leguminosa") cel = { k: ant === "G1" || ant === "G" ? "G" : "G1", nome: c };
      else if (/mucuna/i.test(tx)) cel = { k: "U", nome: c, par: "Mucuna-preta" };
      else if (/\+/.test(tx) && /feij|caupi|leguminosa/i.test(tx)) cel = { k: "Z", nome: c, par: leg };
      else cel = { k: "C", nome: c };
      ant = cel.k;
      return cel;
    });
    return { parte: f.parte, cels };
  });
}

function montarJeitos(r, ef, R) {
  const plano = linhasDoPlano(r);
  const temBx = plano.some((l) => l.parte === "Baixio");
  const T = ef.ha > 0 ? ef.ha : 1;
  const b = temBx ? Math.min(Math.max(ef.baixio_ha || 0, 0), T) : 0;
  const a = (T - b) / 3;
  const area = (p) => (p === "Baixio" ? b : a);
  const partes = ["Parte A", "Parte B", "Parte C"].concat(temBx ? ["Baixio"] : []);
  const J = { plano: plano.map((l) => ({ ...l, area: area(l.parte) })) };
  for (const id of ["agua", "renda", "solo"]) {
    const m = MODELOS[id][R.mand ? "com" : "sem"] || MODELOS[id].com;
    J[id] = partes.map((p, i) => ({ parte: p, area: area(p), cels: m[i].split(" ").map((c) => celula(c, R)) }));
  }
  return { J, T, a, b, temBx };
}

// ---------------------------------------------------------------- os 7 pontos
const planta = (c) => (c.k === "M1" || c.k === "M2" ? "Mandioca" : c.k === "P1" || c.k === "P" ? "Palma" : c.nome + (c.par ? "+" + c.par : ""));
/** A mesma planta (ou gramínea depois de gramínea) volta ao mesmo lugar no ano seguinte. */
function repete(x, y) {
  if (x.k === "M1" && y.k === "M2") return false; // a mesma mandioca, ainda no chão
  if ((x.k === "P1" || x.k === "P") && y.k === "P") return false; // palma é perene
  if ((x.k === "G1" || x.k === "G") && y.k === "G") return false; // gliricídia e guandu também
  if (x.k === "O" && y.k === "O") return false;
  if (x.k === "Z" && y.k === "Z") return false; // milho com feijão no pé: as linhas trocam de lugar a cada ano (regra do plano)
  if (NIVEL[x.k]?.gram && NIVEL[y.k]?.gram) return true; // a lagarta-do-cartucho come milho, sorgo e milheto
  return planta(x) === planta(y);
}

function riscoDe(R, c) {
  if (ENRAIZADA.has(c.k)) return 20;
  const nome = c.k === "Z" || c.k === "U" ? "Milho" : c.k === "M1" || c.k === "M2" ? "Mandioca" : c.k === "P1" || c.k === "P" ? "Palma forrageira" : c.nome;
  const z = R.card.get(nome);
  const ok = (s) => !!s && s !== "nenhum";
  if (z && ok(z.risco20)) return 20;
  if (z && ok(z.risco30)) return 30;
  if (z && ok(z.risco40)) return 40;
  if (z && [z.risco20, z.risco30, z.risco40].includes("nenhum")) return 50; // tem ZARC, mas nenhuma janela aqui
  return 30; // sem ZARC aqui: risco médio (suposição)
}
const dias = (c) => DIAS_COD[c.k] ?? DIAS_CULT[c.nome] ?? 100;

function rendaDe(linhas, fin, ef) {
  const cult = fin?.culturas;
  if (!cult) return null;
  const pr = fin.precos_raiz || {};
  const ref = cult.Mandioca?.preco_kg;
  let preco = pr[ef.raiz];
  if (!(preco > 0)) preco = pr.municipio ?? ref;
  const mult = ref > 0 && preco > 0 ? preco / ref : 1;
  const nivel = ef.custo === "desembolso" ? "desembolso" : "semente";
  const val = (s) => cult[s]?.valor_ha?.p50 ?? null;
  const cst = (s) => cult[s]?.custo_ha?.[nivel] ?? 0;
  const falta = new Set();
  const anual = (nome, f) => {
    const s = SERIE[nome];
    if (!s) return 0;
    const v = val(s);
    if (v === null) { falta.add(s); return 0; }
    return f * (v - cst(s));
  };
  let total = 0;
  for (const l of linhas) {
    if (!(l.area > 0)) continue;
    for (const c of l.cels) {
      let v = 0;
      if (c.k === "L" || c.k === "C") v = anual(c.nome, 1);
      else if (c.k === "Z") v = anual("Milho", 0.5) + anual(c.par, 0.5); // baixio: metade milho, metade feijão (como o passo 4)
      else if (c.k === "U") v = anual("Milho", 1);
      else if (c.k === "F") v = -(fin.custo_sorgo_forrageiro_ha?.[nivel] ?? 0); // forragem: custo sem R$ (vai para o gado)
      else if (c.k === "M1") v = -cst("Mandioca");
      else if (c.k === "M2") { const x = val("Mandioca"); if (x === null) falta.add("Mandioca"); else v = x * mult; }
      total += l.area * v;
    }
  }
  const agro = ["Milho", "Feijão", "Mandioca"].filter((s) => cult[s]?.rend_mediano_kg_ha > 2 * CONAB_FAMILIAR_KG_HA[s]);
  return { total, mult, nivel, preco, falta: [...falta], agro };
}

function avaliar(linhas, R, fin, ef) {
  const s = { adubo: 0, chao: 0, palha: 0, gado: 0, gram: 0 };
  let peso = 0, rep = 0, pesoPar = 0, agua = 0;
  for (const l of linhas) {
    const w = l.area;
    if (!(w > 0)) continue;
    l.cels.forEach((c, k) => {
      const n = NIVEL[c.k] || NIVEL.O;
      for (const q in s) s[q] += w * n[q];
      peso += w;
      agua += w * dias(c) * riscoDe(R, c);
      if (k > 0) { pesoPar += w; if (repete(l.cels[k - 1], c)) rep += w; }
    });
  }
  if (!peso) return null;
  const gram = s.gram / peso, repF = pesoPar ? rep / pesoPar : 0;
  const rs = rendaDe(linhas, fin, ef);
  return {
    adubo: s.adubo / peso, chao: s.chao / peso, palha: s.palha / peso, gado: s.gado / peso,
    gram, rep: repF, praga: (gram + repF) / 2,
    agua: agua / (peso * 120 * 20), // 1,0 = uma roça de 120 dias com 20% de risco em toda a área
    renda: rs && !rs.falta.length ? rs.total : null, rs,
  };
}

/** 1 a 3 pontinhos comparando os 4 jeitos entre si; diferença pequena = empate (2 em todos). */
function pontuar(vals, p) {
  const xs = Object.values(vals).filter(Number.isFinite);
  const out = {};
  if (xs.length < Object.keys(vals).length) return Object.fromEntries(Object.keys(vals).map((k) => [k, null])); // sem os 4, não compara
  const lo = Math.min(...xs), hi = Math.max(...xs);
  const d = p.delta ?? Math.max(300, 0.1 * Math.abs(hi));
  for (const [k, v] of Object.entries(vals)) {
    if (!Number.isFinite(v)) { out[k] = null; continue; }
    if (hi - lo < d) { out[k] = 2; continue; }
    const f = (v - lo) / (hi - lo);
    out[k] = 1 + Math.round(2 * (p.menor ? 1 - f : f));
  }
  return out;
}

/** Contas sem DOM (exportada para conferir no node). */
export function calcular(r, ef) {
  if (!r?.plano?.faixas?.length) return null;
  const R = recursos(r, ef);
  const M = montarJeitos(r, ef, R);
  const aval = Object.fromEntries(IDS.map((id) => [id, avaliar(M.J[id], R, r.financeiro, ef)]));
  if (IDS.some((id) => !aval[id])) return null;
  const pts = Object.fromEntries(PONTOS.map((p) => [p.id, pontuar(Object.fromEntries(IDS.map((id) => [id, aval[id][p.id]])), p)]));
  return { R, ...M, aval, pts };
}

// ---------------------------------------------------------------- texto
const PALAVRA_LEG = { "Feijão-caupi": "feijão", "Feijão comum": "feijão", Amendoim: "amendoim" };
const lista = (xs) => (xs.length <= 1 ? xs.join("") : xs.slice(0, -1).join(", ") + " e " + xs[xs.length - 1]);

/** "mais palma e sorgo; menos milho": o que muda contra o plano, em área por ano. */
function oQueMuda(C, id) {
  const conta = (linhas) => {
    const g = {};
    const add = (k, w) => { g[k] = (g[k] || 0) + w; };
    for (const l of linhas) for (const c of l.cels) {
      const w = l.area;
      if (c.k === "P" || c.k === "P1") add("palma", w);
      else if (c.k === "M1" || c.k === "M2") add("mandioca", w);
      else if (c.k === "L") add(PALAVRA_LEG[c.nome] || "feijão", w);
      else if (c.k === "Z") { add("milho", w / 2); add(PALAVRA_LEG[c.par] || "feijão", w / 2); }
      else if (c.k === "U") { add("milho", w / 2); add("mucuna", w / 2); }
      else if (c.k === "G1" || c.k === "G") add(/glir/i.test(c.nome) ? "gliricídia" : "guandu", w);
      else if (c.k === "F" || c.k === "C") add(/milho/i.test(c.nome) ? "milho" : /milheto/i.test(c.nome) ? "milheto" : "sorgo", w);
    }
    return g;
  };
  const a = conta(C.J[id]), b = conta(C.J.plano);
  const tot = C.T * 3, lim = 0.1 * tot;
  const dif = [...new Set([...Object.keys(a), ...Object.keys(b)])].map((k) => [k, (a[k] || 0) - (b[k] || 0)]);
  const mais = dif.filter(([, d]) => d >= lim).sort((x, y) => y[1] - x[1]).slice(0, 3).map(([k]) => k);
  const menos = dif.filter(([, d]) => d <= -lim).sort((x, y) => x[1] - y[1]).slice(0, 2).map(([k]) => k);
  return { mais, menos };
}
// a manchete diz só o que entra (e por quê); o que sai vai para a linha "Comparado ao plano"
const PORQUE = { agua: ["que aguenta a seca", "que aguentam a seca"], renda: ["para vender", "para vender"], solo: ["que alimenta a terra", "que alimentam a terra"] };
function manchete(C, id) {
  if (id === "plano") return "Plano do QUADRA: um pouco de cada.";
  const { mais } = oQueMuda(C, id);
  return mais.length ? `${NOME[id]}: mais ${lista(mais)}, ${PORQUE[id][mais.length > 1 ? 1 : 0]}.` : `${NOME[id]}: parecido com o plano.`;
}

// o que cada jeito promete vem primeiro na frase "ganha em"
const FOCO = { agua: ["agua", "gado"], renda: ["renda"], solo: ["adubo", "chao", "palha"], plano: [] };
function troca(C, id) {
  const P = C.pts, ganha = [], perde = [];
  const ordem = [...PONTOS].sort((x, y) => FOCO[id].includes(y.id) - FOCO[id].includes(x.id));
  for (const p of ordem) {
    const x = P[p.id][id], y = P[p.id].plano;
    if (x === null || x === undefined || y === null || y === undefined) continue;
    if (id === "plano") { if (x === 3) ganha.push(p.curto); else if (x === 1) perde.push(p.curto); }
    else if (x > y) ganha.push(p.curto); else if (x < y) perde.push(p.curto);
  }
  const g = lista(ganha.slice(0, 3)), q = lista(perde.slice(0, id === "plano" ? 3 : 2));
  if (id === "plano") {
    const f = [g && `mais forte em ${g}`, q && `mais fraco em ${q}`].filter(Boolean).join("; ");
    return f ? f[0].toUpperCase() + f.slice(1) + "." : "Empata com os outros jeitos.";
  }
  const { menos } = oQueMuda(C, id);
  const sai = menos.length ? `menos ${lista(menos)}` : "";
  if (!g && !q) return `Comparado ao plano: ${sai ? sai + "; " : ""}empata nos 7 pontos.`;
  return "Comparado ao plano: " + [sai, g && `ganha em ${g}`, q && `perde em ${q}`].filter(Boolean).join("; ") + ".";
}

const CURTO_CULT = { "Feijão-caupi": "caupi", "Feijão comum": "feijão", Amendoim: "amendoim", Milho: "milho", "Sorgo granífero": "sorgo de grão",
  "Sorgo forrageiro": "sorgo", Milheto: "milheto", "Mucuna-preta": "mucuna" };
const nomeCult = (n) => CURTO_CULT[n] || String(n || "").toLowerCase();
/** [nome, estado] de uma célula para o desenho e a tabela. */
function rotCel(c) {
  switch (c.k) {
    case "Z": case "U": return ["milho", `+ ${nomeCult(c.par)} no pé`];
    case "F": return [nomeCult(c.nome), "p/ o gado"];
    case "M1": return ["mandioca", "planta"];
    case "M2": return ["mandioca", "colhe"];
    case "P1": return ["palma", "planta"];
    case "P": return ["palma", "corta"];
    case "G1": return [nomeCult(c.nome), c.par ? "+ palma, planta" : "planta"];
    case "G": return [nomeCult(c.nome), c.par ? "+ palma, poda" : "poda"];
    case "O": return ["pousio", ""];
    default: return [nomeCult(c.nome), ""];
  }
}
const TIPO = { L: "t-leguminosa", G1: "t-perene", G: "t-perene", C: "t-cereal", Z: "t-cereal", U: "t-cereal", F: "t-forragem", M1: "t-tampao", M2: "t-tampao",
  P1: "t-perene", P: "t-perene", O: "t-pousio" };
const icCel = (c) => (c.k === "F" ? "vaca" : c.k === "P" || c.k === "P1" ? "palma" : c.k === "M1" || c.k === "M2" ? "mandioca" : U.icCultura(c.nome));

// ---------------------------------------------------------------- desenho
const bolinhas = (k) => (k ? `<span class="cen-pts" role="img" aria-label="${k} de 3">${[1, 2, 3].map((i) => `<i class="${i <= k ? "on" : ""}"></i>`).join("")}</span>`
  : `<span class="cen-sem" title="sem dado aqui">—</span>`);

function grade(C, esc, rec) {
  const cab = `<div class="cen-cab"><div class="cen-canto">Compare</div>${IDS.map((id) =>
    `<button type="button" class="cen-jeito${id === esc ? " on" : ""}${id === rec ? " rec" : ""}" data-jeito="${id}" aria-pressed="${id === esc}"
      title="${U.esc(NOME[id])}${id === rec ? " (pela sua prioridade)" : ""}">${U.ic(ICONE[id])}<span>${CURTO[id]}</span></button>`).join("")}</div>`;
  const linhas = PONTOS.map((p) => `<div class="cen-linha"><div class="cen-rot">${U.ic(p.ic)}<span>${p.rot}</span></div>${IDS.map((id) =>
    `<div class="cen-cel${id === esc ? " on" : ""}">${bolinhas(C.pts[p.id][id])}</div>`).join("")}</div>`).join("");
  return `<div class="cen-grade" role="group" aria-label="Os 4 jeitos em 7 pontos">${cab}${linhas}</div>`;
}

function giro(C, r, esc) {
  const anos = r.plano?.anos || [2027, 2028, 2029];
  const bordas = (r.plano?.faixas || []).find((f) => f.parte === "Bordas");
  const cel = (c) => { const [n, e] = rotCel(c); return `<div class="cen-c ${TIPO[c.k] || "t-pousio"}">${U.ic(icCel(c))}<span>${U.esc(n)}${e ? `<small>${U.esc(e)}</small>` : ""}</span></div>`; };
  return `<div class="cen-giro"><p class="cen-giro-tit">${U.esc(NOME[esc])}, ano a ano</p>
    <div class="cen-giro-cab"><span></span>${anos.map((a) => `<span>${a}</span>`).join("")}</div>
    ${C.J[esc].map((l) => `<div class="cen-giro-linha"><span class="cen-parte">${U.esc(l.parte.replace("Parte ", ""))}</span>${l.cels.map(cel).join("")}</div>`).join("")}
    ${bordas ? `<p class="cen-bordas">${U.ic("palma")}<span>Bordas: ${U.esc(String(bordas.anos?.[0]?.cultura || "palma + gliricídia").toLowerCase())}, igual nos 4.</span></p>` : ""}</div>`;
}

const fmt = {
  adubo: (a) => U.num(a.adubo, 1), chao: (a) => U.num(a.chao, 1), palha: (a) => U.num(a.palha, 1), gado: (a) => U.num(a.gado, 1),
  praga: (a) => `${U.pct(a.gram)} · ${U.pct(a.rep)}`, agua: (a) => U.num(a.agua, 2), renda: (a) => (a.renda === null ? "—" : U.num(a.renda / 1000, 1)),
};

function detalhe(C) {
  const R = C.R, rs = C.aval.plano.rs;
  const tNum = `<table class="cen-tab"><thead><tr><th>Ponto</th>${IDS.map((id) => `<th>${CURTO[id]}</th>`).join("")}</tr></thead>
    <tbody>${PONTOS.map((p) => `<tr><th>${p.rot}${p.id === "praga" ? " <small>(gramínea · repete)</small>" : p.id === "agua" ? " <small>(índice)</small>" : p.id === "renda" ? ` <small>(R$ mil, ${U.ha(C.T)}, 3 anos)</small>` : " <small>(0 a 2)</small>"}</th>${IDS.map((id) =>
      `<td>${fmt[p.id](C.aval[id])}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
  const nivelTxt = rs?.nivel === "desembolso" ? "o desembolso" : "a semente";
  const notas = [];
  if (R.fora.length) notas.push(`Só entram culturas do cardápio daqui. Ficaram de fora: ${U.esc(lista(R.fora.map((c) => c.toLowerCase())))}.`);
  if (R.semManiva) notas.push("Você disse que não consegue maniva: os jeitos giram sem mandioca.");
  if (!rs) notas.push("O IBGE não tem a série daqui: a renda fica sem pontinhos.");
  else {
    const falta = [...new Set(IDS.flatMap((id) => C.aval[id].rs?.falta || []))];
    if (falta.length) notas.push(`Falta a série do IBGE de ${U.esc(lista(falta.map((s) => s.toLowerCase())))}: a renda fica sem pontinhos.`);
  }
  if (rs?.agro?.length) notas.push(`Aqui o IBGE mistura lavoura grande (${U.esc(lista(rs.agro.map((s) => s.toLowerCase())))}): os R$ só servem para comparar os 4.`);
  notas.push("Nenhum dos 4 jeitos foi medido inteiro no semiárido. Trocar o consórcio milho + feijão de hoje por rotação é o ensaio que falta (D·T3).");
  return `<p><b>Como ler.</b> Os pontinhos comparam os 4 jeitos entre si: ●●● é o melhor dos quatro naquele ponto, ●○○ o mais fraco.
    Diferença pequena vira empate (●●○ em todos). Cada parte do roçado, em cada ano, ganha 0, 1 ou 2; a conta pesa pela área
    (Partes A, B e C iguais${C.temBx ? `; baixio de ${U.ha(C.b)}` : ""}, roçado de ${U.ha(C.T)}). Toque numa coluna para ver o jeito ano a ano.
    ${U.selo("suposicao", "regras de pontuação do QUADRA sobre dados medidos (ZARC, IBGE, CONAB)")}</p>
    <ul class="cen-regras">
      <li><b>Adubo natural.</b> Feijão, caupi ou amendoim e gliricídia crescida = 2; milho com feijão ou mucuna no pé e gliricídia do 1º ano = 1;
        o resto = 0. Leguminosa num ano e cereal no seguinte, na mesma parte: o cereal rende ~24% a mais no ano colhido, contra cereal solteiro
        (B·T1; Zhao 2022, Mudare 2025, Franke 2018). Feijão ou mucuna no milho em pé: sem ganho de grão medido (C·T0; Melo 2013, Alagoinha-PB).
        Gliricídia ao lado da palma tira do ar metade do N que usa; ao lado do milho com caupi, não fixou (C·T0; Martins 2015, Taperoá-PB).</li>
      <li><b>Chão coberto.</b> Milho com feijão ou mucuna no pé, forragem fechada, mandioca do 2º ano e gliricídia crescida = 2; feijão, milho ou
        sorgo solteiro, palma em nível e gliricídia nova = 1; mandioca do 1º ano = 0 (cresce devagar e deixa o chão aberto na chuva: suposição).
        Palhada e barreira de palma em nível cortam a enxurrada de ~14% para ~4% e ~7% (C·T0; Montenegro 2019, Pesqueira-PE).</li>
      <li><b>Palhada.</b> Milho ou sorgo de grão sem fogo, milho com feijão ou mucuna e gliricídia (folhas e poda) = 2; feijão (rama fina), forragem
        (o gado leva a massa, fica a soca) e mandioca = 1; palma = 0. Mucuna no milho: +36% de massa (C·T0; Melo 2013). Gliricídia: 1.390 contra
        270 kg/ha de folhas no chão (C·T0; Pérez-Marin 2006, Esperança-PB). Sem fogo e com esterco de volta, o carbono do solo quase não caiu em
        13 anos; com broca e queima, caiu muito (C·T0; Sacramento 2013, Sobral-CE). No calor, a palhada some em 5 a 15 dias (C·T2; Pacheco 2017).</li>
      <li><b>Quebra de praga.</b> Média de duas frações: partes-ano com gramínea (milho, sorgo e milheto: a lagarta-do-cartucho come os três; milho
        com feijão no pé conta meia) e anos em que a mesma planta, ou gramínea depois de gramínea, volta ao mesmo lugar (no milho com feijão do
        baixio, as linhas trocam de lugar a cada ano: não conta). Menos é melhor. Não há número de meta-análise: a quebra vem da biologia da praga
        (regra G17 do catálogo; C–D). Trocar milho por sorgo não quebra a lagarta.</li>
      <li><b>Pouca água.</b> Dias de ciclo na chuva × risco do ZARC daqui (20, 30 ou 40% de perder por falta d'água), pesado pela área; 1,0 = roça de
        120 dias com 20% de risco. Menos é melhor. Caupi 70 dias, milho 110, milho com feijão ou mucuna no pé 145 (com o risco do milho), mandioca
        120 no 1º ano. Planta já enraizada (mandioca no 2º ano, palma e gliricídia depois do 1º) conta 60 dias com o risco mais baixo, 20%. Cultura
        sem ZARC aqui: 30%. Risco do ZARC/MAPA: MEDIDO; dias: suposição.</li>
      <li><b>Comida do gado.</b> Forragem, palma já cortável e gliricídia crescida = 2; palha de milho ou sorgo e rama da mandioca na colheita = 1;
        feijão e planta do 1º ano = 0. Palma com sorgo dá mais por área que cada um sozinho (C·T0; Diniz 2017, Serra Talhada-PE).</li>
      <li><b>Renda.</b> Valor típico por ha (mediana do IBGE PAM 1998–2025, em R$ de 2025) menos ${nivelTxt} (CONAB), somado nos 3 anos. Mandioca
        no preço da raiz que você escolheu${rs?.preco ? ` (R$ ${U.num(rs.preco, 2)}/kg)` : ""}, colhida uma vez a cada 2 anos; milho com feijão no pé =
        metade de cada; forragem, sorgo de grão e palma sem R$ (vão para o gado ou não têm série). A soma das medianas só compara os 4: a conta do
        plano ano a ano, com os anos ruins, está no Hoje, melhor e ideal, acima.</li>
    </ul>
    ${tNum}
    <ul class="cen-regras">${notas.map((n) => `<li>${n}</li>`).join("")}</ul>`;
}

// sem resposta, a prioridade é um padrão: a aba acesa diz "sugerido" (em ano de alerta, pelo El Niño)
function sugerido(ef) {
  const o = ef.prioridade_origem || "resposta";
  if (o === "resposta") return "";
  return `<small class="cen-sug" title="${/alerta|El Niño/i.test(o) ? "sugerido no ano de El Niño: toque em outro se quiser" : "sugerido: toque em outro se quiser"}">sugerido</small>`;
}

function desenhar(el, ctx, opcoes) {
  const { r, ef } = ctx;
  const C = calcular(r, ef);
  const caixa = (html) => (opcoes.painel === false ? `<div class="cen">${html}</div>` : `<section class="painel cen">${html}</section>`);
  const kicker = `<p class="kicker">O que vale mais para você? ${U.selo("suposicao", "regras de pontuação do QUADRA sobre o cardápio (ZARC + GAEZ), o IBGE PAM e a CONAB do município; evidência do catálogo de rotações")}</p>`;
  if (!C) {
    el.innerHTML = caixa(kicker + `<p class="sub">Sem plano para este lugar: não dá para comparar rotações aqui.</p>`);
    return;
  }
  const esc = DA_PRIORIDADE[ef.prioridade] || "plano";
  const abas = `<div class="cen-abas" role="group" aria-label="O que vale mais para você">${IDS.map((id) =>
    `<button type="button" class="cen-aba${id === esc ? " on" : ""}" data-jeito="${id}" aria-pressed="${id === esc}" title="${U.esc(NOME[id])}">
      ${U.ic(ICONE[id])}<span${ABA[id].length > 8 ? ' class="cen-aba-longo"' : ""}>${ABA[id]}</span>${id === esc ? sugerido(ef) : ""}</button>`).join("")}</div>`;
  // a grade de 7 pontos e o giro ano a ano: à vista no computador; no celular passariam de ~700 px, então vão para o "ver mais"
  // (junto com o "como pontuamos", num "ver mais" só)
  const corpo = `<div class="cen-corpo">${grade(C, esc, esc)}${giro(C, r, esc)}</div>`;
  const estreito = (globalThis.innerWidth || 1000) <= 760;
  el.innerHTML = caixa(`${kicker}${abas}
    ${U.faixa(ICONE[esc], COR[esc], U.esc(manchete(C, esc)))}
    <p class="cen-troca"><span>${U.esc(troca(C, esc))}</span></p>
    ${estreito ? U.verMais(`${corpo}<h4 class="cen-giro-tit">Como pontuamos</h4>${detalhe(C)}`, "Ver a comparação")
      : `${corpo}${U.verMais(detalhe(C), "Ver como pontuamos")}`}`);
  // a aba tocada grava a prioridade (o passo redesenha; o número grande do passo 4 não muda)
  el.querySelectorAll("[data-jeito]").forEach((b) => b.addEventListener("click", () => {
    const p = INV[b.dataset.jeito];
    if (p && p !== ctx.resp?.prioridade) ctx.set({ prioridade: p });
  }));
}

export default {
  id: "cenarios",
  /** Desenha o bloco dentro de el. opcoes.painel = false tira a moldura .painel (para pôr dentro de outro painel). */
  async render(el, ctx, opcoes = {}) {
    desenhar(el, ctx, opcoes || {});
  },
};
