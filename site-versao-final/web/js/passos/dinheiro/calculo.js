// QUADRA, passo 4 "Quanto rende": as contas, sem DOM (roda também no node, para conferir).
// Método: analise/financeiro.md, seções 2 e 6; decisão 7 do PLANO_INTEGRACAO.md. Base: notebooks/secoes_financeiro/10_familia.py
// (ano_plano, ano_s0), reescrito para seguir o plano que o motor mostra (ctx.r.plano.faixas) e enumerar as sequências de anos.
// Dados: ctx.r.financeiro (dados/financeiro_mun.json, ferramentas/preparar_financeiro_site.py).

/** Produtividade das planilhas familiares da CONAB (kg/ha, 2015+, sequeiro; milho = Crateús-CE, a mesma folha do custo).
 *  Rendimento mediano do PAM acima de 2× isso = lavoura empresarial misturada na série (oeste da BA, sul do MA e do PI). */
export const CONAB_FAMILIAR_KG_HA = { Milho: 1800, "Feijão": 800, Mandioca: 17400 };
const SERIE = { Milho: "Milho", "Feijão-caupi": "Feijão", "Feijão comum": "Feijão", Mandioca: "Mandioca" };
const FORRAGEM = new Set(["Sorgo forrageiro", "Milheto"]);
const SEM_NADA = new Set(["Pousio pastejado"]);
const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

/** Linha do tempo do caixa: nov/2026 (índice 0) a dez/2029 (índice 37). */
export const NMESES = 38;
export const idxMes = (ano, mes) => (ano - 2026) * 12 + (mes - 11);
export const mesDoIdx = (i) => { const t = 10 + i; return { ano: 2026 + Math.floor(t / 12), mes: (t % 12) + 1 }; };
export const rotMes = (i) => { const { ano, mes } = mesDoIdx(i); return `${MESES[mes - 1]}/${String(ano).slice(2)}`; };
const prender = (i) => Math.min(NMESES - 1, Math.max(0, i));

/** Quantil com interpolação linear (igual ao numpy.percentile); `ord` já ordenado. */
export function quantil(ord, q) {
  if (!ord.length) return null;
  const pos = (ord.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos);
  return ord[lo] + (ord[hi] - ord[lo]) * (pos - lo);
}
const faixa = (vals) => {
  const o = Float64Array.from(vals).sort();
  return { p10: quantil(o, 0.1), p50: quantil(o, 0.5), p90: quantil(o, 0.9), min: o[0], max: o[o.length - 1], n: o.length };
};

// ---------- datas da agenda ----------
const DATA = /(\d{2})\/(\d{2})\/(\d{4})/g;
const MESANO = /(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\/(\d{4})/g;
function datas(txt) {
  const out = [];
  for (const m of String(txt || "").matchAll(DATA)) out.push({ ano: +m[3], mes: +m[2], dia: +m[1] });
  return out;
}
function mesesAno(txt) {
  const out = [];
  for (const m of String(txt || "").matchAll(MESANO)) out.push({ ano: +m[2], mes: MESES.indexOf(m[1]) + 1, dia: 15 });
  return out;
}
const idx = (d) => idxMes(d.ano, d.mes);

/** Datas de uma linha da agenda: mês do início do plantio e intervalo da colheita (índices da linha do tempo). */
function datasLinha(l) {
  const bp = l.barras.find((b) => b.pista === 1 && (b.tipo === "plantio" || b.tipo === "estimado"));
  const bc = l.barras.find((b) => b.tipo === "colheita");
  const p = (bp && datas(bp.rotulo)[0]) || datas(l.plantar)[0] || null;
  let c = bc ? datas(bc.rotulo) : [];
  if (c.length < 2) c = datas(l.colher);
  if (c.length < 2) c = mesesAno(l.colher);
  return { plantio: p ? idx(p) : null, colheita: c.length >= 2 ? [idx(c[0]), idx(c[1])] : null,
    meio: c.length >= 2 ? Math.floor((idx(c[0]) + c[0].dia / 31 + idx(c[1]) + c[1].dia / 31) / 2) : null };
}

/** Acha a linha da agenda para (parte, cultura, estação); sem ela, a mesma cultura em outra estação ou parte, deslocada
 *  de 12 meses por ano (2028–29 repetem os meses do ZARC 2026/27, suposição da seção 1 de financeiro.md). */
function achar(agenda, parte, teste, estacao) {
  const ls = (agenda?.linhas || []).filter((l) => teste(l.cultura));
  const l = ls.find((x) => x.parte === parte && x.estacao === estacao) || ls.find((x) => x.parte === parte) ||
    ls.find((x) => x.estacao === estacao) || ls[0];
  if (!l) return null;
  const d = datasLinha(l), s = (estacao - l.estacao) * 12;
  return { plantio: d.plantio === null ? null : d.plantio + s, meio: d.meio === null ? null : d.meio + s,
    colheita: d.colheita ? [d.colheita[0] + s, d.colheita[1] + s] : null };
}
const PADRAO_MESES = (est) => ({ plantio: idxMes(est, 3), meio: idxMes(est, 6), colheita: [idxMes(est + 1, 2), idxMes(est + 1, 9)] });

// ---------- o plano em lançamentos ----------
/**
 * Monta a conta do município: áreas, lançamentos (custo fixo num mês; receita = série do ano × fator, espalhada em meses),
 * o que falta e os avisos. Nada aqui depende do ano sorteado.
 */
export function montar(r, ef) {
  const fin = r.financeiro;
  const out = { ok: false, falta: [], semRs: [], avisos: [], agro: [], itens: [[], [], []], s0: [[], [], []] };
  if (!fin) { out.falta.push("a série do IBGE (PAM) deste município ainda não está nos dados"); return out; }
  const cult = fin.culturas || {};
  const anosPlano = r.plano?.anos || [2027, 2028, 2029];
  const faixas = (r.plano?.faixas || []).filter((f) => f.parte !== "Bordas");
  const temBaixio = faixas.some((f) => f.parte === "Baixio");
  const T = ef.ha;
  const b = temBaixio ? Math.min(ef.baixio_ha, T) : 0;
  const a = (T - b) / 3;
  Object.assign(out, { T, a, b, temBaixio, baixioNaoSei: temBaixio && ef.tem_baixio === null });
  const leg = r.plano?.leguminosa || null;
  const agenda = r.agenda;
  const usadas = new Set(["Milho", "Feijão"]); // a S0 sempre usa as duas

  // custo por ha de cada chave (semente e desembolso da CONAB; sorgo = suposição de lavoura anual manual)
  out.custoHa = (chave, nivel) => (chave === "Sorgo forrageiro" ? fin.custo_sorgo_forrageiro_ha?.[nivel] : cult[chave]?.custo_ha?.[nivel]) ?? 0;

  const lanc = (k, it) => out.itens[k].push(it);
  let plantadaUsada = false;
  for (const fx of faixas) {
    const area = fx.parte === "Baixio" ? b : a;
    if (!(area > 0)) continue;
    let plantou = null; // linha da agenda da maniva do ano anterior (para achar os meses da colheita)
    fx.anos.forEach((cel, k) => {
      const est = anosPlano[k], c = cel.cultura;
      if (c === "Mandioca") {
        usadas.add("Mandioca");
        const ag = achar(agenda, fx.parte, (x) => x === "Mandioca", plantou ? plantou.est : est) || PADRAO_MESES(plantou ? plantou.est : est);
        if (plantou) { // ano da colheita: receita do ano k, espalhada nos meses de colheita da agenda (fev–set sem agenda)
          const [i0, i1] = ag.colheita || PADRAO_MESES(plantou.est).colheita;
          lanc(k, { parte: fx.parte, cultura: "Mandioca", serie: "Mandioca", fator: area, meses: faixaMeses(i0, i1), rotulo: "colheita da mandioca", tipo: "colheita" });
          plantou = null;
          return;
        }
        lanc(k, { parte: fx.parte, cultura: "Mandioca", custo: "Mandioca", area, mes: prender(ag.plantio), rotulo: "maniva", tipo: "plantio" });
        plantou = { est };
        if (k === 0 && ef.maniva === "plantada" && !plantadaUsada) { // a mandioca de 2026 já no chão: colhe em 2027 nesta parte
          plantadaUsada = true;
          const [i0, i1] = (ag.colheita || PADRAO_MESES(est).colheita).map((i) => i - 12);
          lanc(0, { parte: fx.parte, cultura: "Mandioca", serie: "Mandioca", fator: area, meses: faixaMeses(i0, i1),
            rotulo: "colheita da mandioca que já está no chão", tipo: "colheita", plantada: true });
        }
        return;
      }
      plantou = null;
      if (fx.parte === "Baixio" && c === "Milho" && leg) { // baixio: ½ milho + ½ leguminosa por ha (convenção do notebook)
        partes(k, fx.parte, "Milho", area / 2, est, (x) => x === "Milho");
        partes(k, fx.parte, leg, area / 2, est, (x) => x.startsWith(leg));
        return;
      }
      partes(k, fx.parte, c, area, est, (x) => x === c);
    });
  }

  function partes(k, parte, c, area, est, teste) {
    const ag = achar(agenda, parte, teste, est) || PADRAO_MESES(est);
    const s = SERIE[c];
    if (s) {
      usadas.add(s);
      lanc(k, { parte, cultura: c, custo: s, area, mes: prender(ag.plantio ?? PADRAO_MESES(est).plantio), rotulo: `semente: ${c.toLowerCase()}`, tipo: "plantio" });
      lanc(k, { parte, cultura: c, serie: s, fator: area, meses: [[prender(ag.meio ?? PADRAO_MESES(est).meio), 1]], rotulo: `colheita: ${c.toLowerCase()}`, tipo: "colheita" });
    } else if (FORRAGEM.has(c)) {
      lanc(k, { parte, cultura: c, custo: "Sorgo forrageiro", area, mes: prender(ag.plantio ?? PADRAO_MESES(est).plantio), rotulo: `semente: ${c.toLowerCase()} (forragem, sem R$)`, tipo: "plantio", uso: true });
    } else if (!SEM_NADA.has(c) && !out.semRs.includes(c)) out.semRs.push(c);
  }

  // o jeito de hoje (S0): milho + feijão em toda a área, mesmo ano; meses do milho do baixio e da leguminosa da agenda
  const tMilho = (x) => x === "Milho", tLeg = (x) => x === leg || /^Feijão/.test(x);
  anosPlano.forEach((est, k) => {
    const agM = achar(agenda, "Baixio", tMilho, est) || achar(agenda, "Parte B", tLeg, est) || PADRAO_MESES(est);
    const agF = achar(agenda, "Parte B", tLeg, est) || agM;
    for (const [s, ag] of [["Milho", agM], ["Feijão", agF]]) {
      out.s0[k].push({ cultura: s, custo: s, area: T / 2, mes: prender(ag.plantio ?? PADRAO_MESES(est).plantio), rotulo: `semente: ${s.toLowerCase()}`, tipo: "plantio" });
      out.s0[k].push({ cultura: s, serie: s, fator: T / 2, meses: [[prender(ag.meio ?? PADRAO_MESES(est).meio), 1]], rotulo: `colheita: ${s.toLowerCase()}`, tipo: "colheita" });
    }
  });

  out.usadas = [...usadas];
  for (const s of out.usadas) if (!cult[s] || !fin.historico_R_ha?.[s]) out.falta.push(s);
  for (const s of ["Milho", "Feijão", "Mandioca"]) {
    const c = cult[s];
    if (c && c.rend_mediano_kg_ha > 2 * CONAB_FAMILIAR_KG_HA[s]) out.agro.push({ cultura: s, kg: c.rend_mediano_kg_ha, conab: CONAB_FAMILIAR_KG_HA[s] });
  }
  if (ef.maniva === "plantada" && !plantadaUsada) out.avisos.push("Você disse que já tem mandioca plantada, mas o plano daqui não usa mandioca: ela não entra na conta.");
  if (out.falta.length) return out;

  // séries: mesmo ano para todas as culturas; só entram os anos em que todas as séries usadas têm valor
  const H = fin.historico_R_ha, K = fin.historico_kg_ha || {};
  out.R = {}; out.KG = {};
  for (const s of out.usadas) {
    out.R[s] = new Map(H.anos.map((y, i) => [y, H[s][i]]));
    out.KG[s] = new Map((K.anos || []).map((y, i) => [y, K[s]?.[i] ?? null]));
  }
  out.anos = H.anos.filter((y) => out.usadas.every((s) => Number.isFinite(out.R[s].get(y))));
  out.anosEN = (fin.anos_el_nino_forte || [1998, 2010, 2016, 2024]).filter((y) => out.anos.includes(y));
  out.precoRefMand = cult.Mandioca?.preco_kg ?? null;
  out.origens = Object.fromEntries(out.usadas.map((s) => [s, H["origem_" + s] || []]));
  out.ok = out.anos.length >= 10 && out.anosEN.length >= 1;
  if (!out.ok) out.falta.push("anos suficientes com as culturas do plano no mesmo ano");
  return out;
}

function faixaMeses(i0, i1) {
  const n = Math.max(1, i1 - i0 + 1), m = [];
  for (let i = i0; i <= i1; i++) m.push([prender(i), 1 / n]);
  return m;
}

// ---------- um ano, todas as sequências ----------
function valorAno(m, lancs, y, nivel, mult) {
  let rec = 0, cst = 0, mand = 0;
  const fluxo = new Float64Array(NMESES);
  for (const it of lancs) {
    if (it.custo) {
      const v = m.custoHa(it.custo, nivel) * it.area;
      cst += v; fluxo[it.mes] -= v;
    } else {
      const base = m.R[it.serie].get(y) * it.fator;
      const v = it.serie === "Mandioca" ? base * mult : base;
      if (it.serie === "Mandioca") mand += base;
      rec += v;
      for (const [i, w] of it.meses) fluxo[i] += v * w;
    }
  }
  for (let i = 1; i < NMESES; i++) fluxo[i] += fluxo[i - 1];
  return { rec, cst, mar: rec - cst, mand, cum: fluxo };
}

/** Margem de cada ano do plano e da S0 em cada ano histórico do sorteio daquele ano. */
function porAno(m, nivel, mult, pool2027) {
  const pools = [pool2027 || m.anosEN, m.anos, m.anos];
  return [0, 1, 2].map((k) => ({
    anos: pools[k],
    plano: pools[k].map((y) => valorAno(m, m.itens[k], y, nivel, mult)),
    s0: pools[k].map((y) => valorAno(m, m.s0[k], y, nivel, mult)),
  }));
}

/** Só os totais de 3 anos (rápido): para a sensibilidade ao preço da raiz e o preço de empate. */
export function totais(m, nivel, mult) {
  const A = porAno(m, nivel, mult);
  const pl = [], s0 = [];
  for (const a of A[0].plano.keys()) for (const b of A[1].plano.keys()) for (const c of A[2].plano.keys()) {
    pl.push(A[0].plano[a].mar + A[1].plano[b].mar + A[2].plano[c].mar);
    s0.push(A[0].s0[a].mar + A[1].s0[b].mar + A[2].s0[c].mar);
  }
  const g = pl.map((v, i) => v - s0[i]);
  return { plano: faixa(pl), s0: faixa(s0), ganho: faixa(g), aFrente: g.filter((v) => v > 0).length / g.length, n: g.length };
}

/** Preço da raiz (R$/kg) em que o ganho típico (P50 de plano − hoje em 3 anos) fica em zero; null se o plano não tem mandioca. */
export function precoEmpate(m, nivel) {
  if (!m.usadas.includes("Mandioca") || !m.precoRefMand) return null;
  const g = (p) => totais(m, nivel, p / m.precoRefMand).ganho.p50;
  if (g(0) >= 0) return 0;
  let lo = 0, hi = 10;
  if (g(hi) < 0) return null;
  for (let i = 0; i < 30; i++) { const md = (lo + hi) / 2; if (g(md) >= 0) hi = md; else lo = md; }
  return hi;
}

/**
 * A conta completa num nível de custo e num preço da raiz: 2027 entre os El Niños fortes, 2028 e 2029 entre os 28 anos,
 * o mesmo ano para todas as culturas e para a S0 (comparação pareada). 4 × 28 × 28 = 3.136 sequências, enumeradas.
 */
export function calcular(m, nivel, mult) {
  const A = porAno(m, nivel, mult);
  const n0 = A[0].anos.length, n1 = A[1].anos.length, n2 = A[2].anos.length, N = n0 * n1 * n2;
  const pl = new Float64Array(N), s0 = new Float64Array(N);
  const cpl = Array.from({ length: NMESES }, () => new Float64Array(N)), cs0 = Array.from({ length: NMESES }, () => new Float64Array(N));
  let n = 0;
  for (let a = 0; a < n0; a++) for (let b = 0; b < n1; b++) for (let c = 0; c < n2; c++, n++) {
    const P = [A[0].plano[a], A[1].plano[b], A[2].plano[c]], S = [A[0].s0[a], A[1].s0[b], A[2].s0[c]];
    pl[n] = P[0].mar + P[1].mar + P[2].mar;
    s0[n] = S[0].mar + S[1].mar + S[2].mar;
    for (let i = 0; i < NMESES; i++) {
      cpl[i][n] = P[0].cum[i] + P[1].cum[i] + P[2].cum[i];
      cs0[i][n] = S[0].cum[i] + S[1].cum[i] + S[2].cum[i];
    }
  }
  const ganho = pl.map((v, i) => v - s0[i]);
  const caixa = (arr) => arr.map((v) => { const o = v.sort(); return { p10: quantil(o, 0.1), p50: quantil(o, 0.5), p90: quantil(o, 0.9) }; });

  // marcas do caixa: saídas (custo fixo) e entradas típicas (mediana do valor no ano) por mês
  const marcas = [];
  [0, 1, 2].forEach((k) => {
    for (const it of m.itens[k]) {
      if (it.custo) {
        const v = m.custoHa(it.custo, nivel) * it.area;
        if (v > 0.5) marcas.push({ i: it.mes, v: -v, rotulo: `${it.rotulo} (${it.parte})` });
      } else {
        const vals = A[k].anos.map((y) => m.R[it.serie].get(y) * it.fator * (it.serie === "Mandioca" ? mult : 1));
        const md = faixa(vals).p50;
        for (const [i, w] of it.meses) marcas.push({ i, v: md * w, rotulo: `${it.rotulo} (${it.parte})` });
      }
    }
  });

  const anoRes = A.map((x, k) => ({
    ano: 2027 + k, anos: x.anos,
    plano: faixa(x.plano.map((v) => v.mar)), s0: faixa(x.s0.map((v) => v.mar)),
    pagaPlano: x.plano.filter((v) => v.mar >= 0).length, pagaS0: x.s0.filter((v) => v.mar >= 0).length, n: x.anos.length,
    planoFrente: x.plano.filter((v, i) => v.mar > x.s0[i].mar).length,
  }));
  return {
    n: N, nEN: n0, nAnos: n1,
    plano: faixa(pl), s0: faixa(s0), ganho: faixa(ganho), aFrente: ganho.filter((v) => v > 0).length / N,
    planoNeg: pl.filter((v) => v < 0).length / N, s0Neg: s0.filter((v) => v < 0).length / N,
    porAno: anoRes,
    elNino: A[0].anos.map((y, i) => ({ ano: y, plano: A[0].plano[i].mar, s0: A[0].s0[i].mar, recPlano: A[0].plano[i].rec, recS0: A[0].s0[i].rec })),
    caixaPlano: caixa(cpl), caixaS0: caixa(cs0), marcas,
  };
}

/** 2027 "um ano qualquer" (os 28 anos, sem condicionar ao El Niño): só o ano de 2027. */
export function ano2027Qualquer(m, nivel, mult) {
  const A = porAno(m, nivel, mult, m.anos)[0];
  return { plano: faixa(A.plano.map((v) => v.mar)), s0: faixa(A.s0.map((v) => v.mar)), n: A.anos.length };
}

/** "Se o plano estivesse no chão desde 1998": o plano maduro (a configuração de 2029: uma parte colhe a mandioca, outra
 *  tem a leguminosa, outra recebe a maniva, mais o baixio) contra a S0, no mesmo ano histórico. */
export function replay(m, nivel, mult) {
  return m.anos.map((y) => ({ ano: y, plano: valorAno(m, m.itens[2], y, nivel, mult).mar, s0: valorAno(m, m.s0[2], y, nivel, mult).mar,
    vizinhos: m.usadas.some((s) => m.origens[s][m.anos.indexOf(y)] === "meso") }));
}

/** Comida em 2027 nos anos de El Niño forte (kg de grão e de raiz), plano × S0. */
export function comida2027(m) {
  const kg = (lancs, y, filtro) => lancs.filter((it) => it.serie && filtro(it.serie))
    .reduce((s, it) => s + (m.KG[it.serie].get(y) ?? 0) * it.fator, 0);
  const grao = (s) => s === "Milho" || s === "Feijão";
  return m.anosEN.map((y) => ({ ano: y, graoPlano: kg(m.itens[0], y, grao), raizPlano: kg(m.itens[0], y, (s) => s === "Mandioca"),
    graoS0: kg(m.s0[0], y, grao) }));
}
