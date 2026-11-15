// QUADRA, passo 4 "Quanto rende": gráficos em SVG à mão (um eixo por gráfico; plano em azul, o jeito de hoje em cinza).
import { NMESES, mesDoIdx, rotMes } from "./calculo.js";
import { IC } from "../../comum.js";

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const n0 = (v, c = 0) => Number(v).toLocaleString("pt-BR", { maximumFractionDigits: c, minimumFractionDigits: c });

/** R$ legível: "R$ 11,5 mil" a partir de 10 mil; "R$ 1.090" de mil a 10 mil (arredonda a 10); "−R$ 101". */
export function rs(v) {
  if (v === null || v === undefined || !Number.isFinite(v)) return "—";
  const s = v < 0 ? "−" : "", a = Math.abs(v);
  if (a >= 10000) return `${s}R$ ${n0(a / 1000, 1)} mil`;
  return `${s}R$ ${n0(a >= 1000 ? Math.round(a / 10) * 10 : Math.round(a))}`;
}
/** "de R$ 11,5 mil a R$ 24,1 mil". */
export const faixaRs = (lo, hi) => `de ${rs(lo)} a ${rs(hi)}`;

function ticks(min, max, n = 4) {
  const span = max - min || 1, s0 = span / n, mag = 10 ** Math.floor(Math.log10(s0)), f = s0 / mag;
  const step = (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * mag;
  const t = [];
  for (let v = Math.ceil(min / step) * step; v <= max + step * 1e-6; v += step) t.push(Math.abs(v) < step * 1e-6 ? 0 : v);
  return t;
}
const tickTxt = (v) => (v === 0 ? "0" : Math.abs(v) >= 1000 ? `${v < 0 ? "−" : ""}${n0(Math.abs(v) / 1000, Math.abs(v) % 1000 ? 1 : 0)} mil` : `${v < 0 ? "−" : ""}${n0(Math.abs(v))}`);

function escala(min, max, y0, y1) {
  const lo = Math.min(0, min), hi = Math.max(0, max);
  const pad = (hi - lo) * 0.08 || 1;
  const a = lo < 0 ? lo - pad : lo, b = hi + pad;
  const t = ticks(a, b);
  const A = Math.min(a, t[0]), B = Math.max(b, t[t.length - 1]);
  return { y: (v) => y1 - ((v - A) / (B - A)) * (y1 - y0), t, A, B };
}

/** Coluna com a ponta arredondada (4px) e a base reta, crescendo da linha do zero. */
function coluna(x, w, yBase, yPonta, cls) {
  const h = Math.abs(yBase - yPonta);
  if (h < 0.5) return "";
  const r = Math.min(4, h, w / 2);
  if (yPonta < yBase) {
    return `<path class="${cls}" d="M${x},${yBase} V${yPonta + r} Q${x},${yPonta} ${x + r},${yPonta} H${x + w - r} Q${x + w},${yPonta} ${x + w},${yPonta + r} V${yBase} Z"/>`;
  }
  return `<path class="${cls}" d="M${x},${yBase} V${yPonta - r} Q${x},${yPonta} ${x + r},${yPonta} H${x + w - r} Q${x + w},${yPonta} ${x + w},${yPonta - r} V${yBase} Z"/>`;
}

function eixoY(E, x0, x1, rotulo, rotY = 12) {
  return E.t.map((v) => `<line class="${v === 0 ? "zero" : "grade"}" x1="${x0}" x2="${x1}" y1="${E.y(v)}" y2="${E.y(v)}"/>` +
    `<text class="tick" x="${x0 - 6}" y="${E.y(v) + 4}" text-anchor="end">${tickTxt(v)}</text>`).join("") +
    (rotulo ? `<text class="tick" x="${x0 - 6}" y="${rotY}" text-anchor="end">${esc(rotulo)}</text>` : "");
}

/**
 * Barras por ano: a coluna é o ano típico (mediana), o traço vertical é a faixa (P10–P90; em 2027, do pior ao melhor dos
 * anos de El Niño forte). Plano e hoje lado a lado, mesmo eixo.
 */
export function barrasAno(porAno, W = 640) {
  const H = 260, x0 = W < 500 ? 50 : 64, x1 = W - 12, yT = 30, yB = H - 40;
  const vals = porAno.flatMap((a) => [a.plano, a.s0]).flatMap((f) => [f.p10, f.p90, f.min, f.max, f.p50]);
  const E = escala(Math.min(...vals), Math.max(...vals), yT, yB);
  const gw = (x1 - x0) / porAno.length, bw = 24, sep = Math.max(4, Math.min(22, gw / 2 - bw - 4)), estreito = 2 * sep + bw < 64;
  let s = eixoY(E, x0, x1, "R$", 12);
  porAno.forEach((a, k) => {
    const cx = x0 + gw * (k + 0.5);
    const en = k === 0 && a.n <= 6;
    [["plano", a.plano, cx - bw - sep], ["s0", a.s0, cx + sep]].forEach(([cls, f, x]) => {
      const lo = en ? f.min : f.p10, hi = en ? f.max : f.p90;
      const quem = cls === "plano" ? "Plano" : "Jeito de hoje";
      s += `<g class="alvo"><title>${quem}, ${a.ano}: típico ${rs(f.p50)}; ${en ? `dos ${a.n} El Niños fortes, ` : ""}${faixaRs(lo, hi)}</title>` +
        `<rect x="${x - 6}" y="${yT}" width="${bw + 12}" height="${yB - yT}" fill="transparent"/>` +
        coluna(x, bw, E.y(0), E.y(f.p50), `m-${cls}`) +
        `<line class="bigode" x1="${x + bw / 2}" x2="${x + bw / 2}" y1="${E.y(hi)}" y2="${E.y(lo)}"/>` +
        `<line class="bigode" x1="${x + bw / 2 - 5}" x2="${x + bw / 2 + 5}" y1="${E.y(hi)}" y2="${E.y(hi)}"/>` +
        `<line class="bigode" x1="${x + bw / 2 - 5}" x2="${x + bw / 2 + 5}" y1="${E.y(lo)}" y2="${E.y(lo)}"/></g>`;
      const yv = f.p50 >= 0 ? Math.min(E.y(f.p50), E.y(hi)) - 6 : Math.max(E.y(f.p50), E.y(lo)) + 14;
      if (cls === "plano" || !estreito) s += `<text class="valor" x="${Math.max(x0 + 30, x + bw / 2)}" y="${yv}" text-anchor="middle">${rs(f.p50)}</text>`;
    });
    s += `<text class="rot-x" x="${cx}" y="${H - 16}" text-anchor="middle">${a.ano}</text>` +
      `<text class="tick" x="${cx}" y="${H - 3}" text-anchor="middle">${en ? (estreito ? `${a.n} El Niños` : `como os ${a.n} El Niños fortes`) : (estreito ? `${a.n} anos` : `como os ${a.n} anos`)}</text>`;
  });
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Sobra por ano, plano e jeito de hoje">${s}</svg>`;
}

/**
 * Caixa acumulado mês a mês (nov/2026 a dez/2029): faixa P10–P90 e linha típica (mediana) do plano e do jeito de hoje,
 * com as saídas (▼) e entradas (▲) do plano nos meses da agenda. Devolve o SVG e a geometria para o cursor.
 */
export function caixa(t, W = 760) {
  const H = 322, x0 = 64, x1 = W - 14, yT = 34, yB = H - 74;
  const todos = [...t.caixaPlano, ...t.caixaS0].flatMap((q) => [q.p10, q.p90]);
  const E = escala(Math.min(...todos), Math.max(...todos), yT, yB);
  const x = (i) => x0 + ((x1 - x0) * i) / (NMESES - 1);
  const area = (q) => q.map((v, i) => `${x(i)},${E.y(v.p90)}`).join(" ") + " " + q.map((v, i) => `${x(i)},${E.y(v.p10)}`).reverse().join(" ");
  const linha = (q) => q.map((v, i) => `${x(i)},${E.y(v.p50)}`).join(" ");
  let s = eixoY(E, x0, x1, "R$", 14);
  for (const [i, ano] of [[2, 2027], [14, 2028], [26, 2029]]) {
    s += `<line class="ano-sep" x1="${x(i) - 0.5 * (x(1) - x(0))}" x2="${x(i) - 0.5 * (x(1) - x(0))}" y1="${yT - 14}" y2="${yB}"/>` +
      `<text class="rot-x" x="${x(i) + 2}" y="${yT - 16}">${ano}</text>`;
  }
  for (let i = 0; i < NMESES; i++) {
    const { mes } = mesDoIdx(i);
    if ([1, 4, 7, 10].includes(mes)) s += `<text class="tick" x="${x(i)}" y="${yB + 14}" text-anchor="middle">${rotMes(i).slice(0, 3)}</text>`;
  }
  s += `<polygon class="banda-s0" points="${area(t.caixaS0)}"/><polygon class="banda-plano" points="${area(t.caixaPlano)}"/>` +
    `<polyline class="l-s0" points="${linha(t.caixaS0)}"/><polyline class="l-plano" points="${linha(t.caixaPlano)}"/>`;
  // saídas e entradas do plano por mês
  const saida = new Map(), entra = new Map();
  for (const mk of t.marcas) (mk.v < 0 ? saida : entra).set(mk.i, ((mk.v < 0 ? saida : entra).get(mk.i) || 0) + mk.v);
  const ys = yB + 32, ye = yB + 56;
  for (const [i] of saida) s += `<path class="m-saida" d="M${x(i) - 5},${ys - 5} h10 l-5,8 z"/>`;
  for (const [i] of entra) s += `<path class="m-entra" d="M${x(i) - 5},${ye + 4} h10 l-5,-8 z"/>`;
  const icone = (nome, y, cls) => `<g class="ic-svg ${cls}" transform="translate(${x0 - 26},${y - 9}) scale(0.75)">${IC[nome]}</g>`;
  s += icone("semente", ys, "saida") + icone("dinheiro", ye, "entra");
  s += `<line class="hoje" x1="${x(0)}" x2="${x(0)}" y1="${yT}" y2="${yB}"/><text class="tick" x="${x(0) + 4}" y="${yT + 10}">hoje</text>`;
  const fim = t.caixaPlano[NMESES - 1].p50, fimS = t.caixaS0[NMESES - 1].p50;
  s += `<line class="cursor" x1="0" x2="0" y1="${yT}" y2="${yB}" style="display:none"/>` +
    `<rect class="captura" x="${x0}" y="${yT - 16}" width="${x1 - x0}" height="${yB - yT + 64}" fill="transparent"/>`;
  return {
    svg: `<svg class="graf graf-caixa" viewBox="0 0 ${W} ${H}" role="img" aria-label="Caixa acumulado mês a mês: plano termina típico em ${rs(fim)}, jeito de hoje em ${rs(fimS)}">${s}</svg>`,
    geo: { W, x0, x1, n: NMESES, x, saida, entra },
  };
}

/** Faixa de 28 barras: o plano maduro e o jeito de hoje no mesmo ano histórico. */
export function replay(rows, anosEN, W = 760) {
  const H = 230, x0 = 64, x1 = W - 10, yT = 26, yB = H - 40;
  const vals = rows.flatMap((r) => [r.plano, r.s0]);
  const E = escala(Math.min(...vals), Math.max(...vals), yT, yB);
  const gw = (x1 - x0) / rows.length, bw = Math.min(12, (gw - 5) / 2);
  let s = eixoY(E, x0, x1, "R$", 12);
  rows.forEach((r, i) => {
    const cx = x0 + gw * (i + 0.5);
    s += `<g class="alvo"><title>${r.ano}: plano ${rs(r.plano)}; jeito de hoje ${rs(r.s0)}${r.vizinhos ? " (ano completado pela mesorregião)" : ""}</title>` +
      `<rect x="${cx - gw / 2}" y="${yT}" width="${gw}" height="${yB - yT}" fill="transparent"/>` +
      coluna(cx - bw - 1, bw, E.y(0), E.y(r.plano), "m-plano") + coluna(cx + 1, bw, E.y(0), E.y(r.s0), "m-s0") + `</g>`;
    if (anosEN.includes(r.ano)) s += `<path class="m-en" d="M${cx},${yB + 6} l4,5 l-4,5 l-4,-5 z"/>`;
    if ((r.ano - rows[0].ano) % 3 === 0) s += `<text class="tick" x="${cx}" y="${yB + 30}" text-anchor="middle">${r.ano}</text>`;
  });
  return `<svg class="graf" viewBox="0 0 ${W} ${H}" role="img" aria-label="Sobra do plano maduro e do jeito de hoje em cada ano de 1998 a 2025">${s}</svg>`;
}

/** Mini barras horizontais (plano e hoje) numa escala comum, para os cartões "se 2027 for como...". */
export function mini(plano, s0, lo, hi) {
  const W = 200, H = 46, x0 = 4, x1 = W - 4;
  const a = Math.min(0, lo), b = Math.max(0, hi);
  const X = (v) => x0 + ((v - a) / (b - a || 1)) * (x1 - x0);
  const bar = (v, y, cls) => { const p = X(Math.min(0, v)), q = X(Math.max(0, v)); return `<rect class="${cls}" x="${p}" y="${y}" width="${Math.max(1, q - p)}" height="12" rx="3"/>`; };
  return `<svg class="graf-mini" viewBox="0 0 ${W} ${H}" aria-hidden="true">${bar(plano, 6, "m-plano")}${bar(s0, 26, "m-s0")}` +
    `<line class="zero" x1="${X(0)}" x2="${X(0)}" y1="2" y2="${H - 2}"/></svg>`;
}

/** Herói: barras horizontais do plano e do jeito de hoje (coluna = típico; traço = do caso ruim ao bom), mesmo eixo. */
export function barrasH(linhas, W = 600) {
  const H = 26 * linhas.length + 10, x0 = 6, x1 = W - 6;
  const vals = linhas.flatMap((l) => [l.f.p10, l.f.p90, 0]);
  const a = Math.min(...vals), b = Math.max(...vals);
  const X = (v) => x0 + ((v - a) / (b - a || 1)) * (x1 - x0);
  let s = "";
  linhas.forEach((l, k) => {
    const y = 6 + k * 26, p = X(Math.min(0, l.f.p50)), q = X(Math.max(0, l.f.p50));
    s += `<g><title>${esc(l.rot)}: típico ${rs(l.f.p50)}; caso ruim ${rs(l.f.p10)}; caso bom ${rs(l.f.p90)}</title>` +
      `<rect class="m-${l.cls}" x="${p}" y="${y}" width="${Math.max(2, q - p)}" height="14" rx="4"/>` +
      `<line class="bigode" x1="${X(l.f.p10)}" x2="${X(l.f.p90)}" y1="${y + 7}" y2="${y + 7}"/>` +
      `<line class="bigode" x1="${X(l.f.p10)}" x2="${X(l.f.p10)}" y1="${y + 2}" y2="${y + 12}"/>` +
      `<line class="bigode" x1="${X(l.f.p90)}" x2="${X(l.f.p90)}" y1="${y + 2}" y2="${y + 12}"/></g>`;
  });
  s += `<line class="zero" x1="${X(0)}" x2="${X(0)}" y1="0" y2="${H}"/>`;
  return `<svg class="graf graf-h" viewBox="0 0 ${W} ${H}" role="img" aria-label="Plano e jeito de hoje, típico e faixa">${s}</svg>`;
}
