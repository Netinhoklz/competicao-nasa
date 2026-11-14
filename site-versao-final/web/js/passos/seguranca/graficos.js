// Passo 5, "Segurança": gráficos à mão (SVG e HTML), sem biblioteca. Um eixo por gráfico; texto na cor da tinta.
import { esc, num } from "../../comum.js";

/** Passo "bonito" para o eixo: ~5 marcas entre 0 e max. */
export function eixoBom(max) {
  if (!(max > 0)) return { max: 1, passo: 0.25 };
  const bruto = max / 5, p10 = 10 ** Math.floor(Math.log10(bruto));
  const passo = [1, 2, 2.5, 5, 10].map((k) => k * p10).find((p) => p >= bruto) || 10 * p10;
  return { max: Math.ceil(max / passo - 1e-9) * passo, passo };
}

const pos = (v, max) => Math.max(0, Math.min(100, (v / max) * 100));
const fmt = (v) => num(v, v > 0 && v < 10 && v % 1 ? 1 : 0);

/** Leque de um ano: faixa clara (8 em 10 anos), escura (6 em 10), traço do típico, tracejado do normal. q em unidades da cultura. */
export function leque(q, normal, eixo, rotulo) {
  const { max, passo } = eixo;
  const x = (v) => pos(v, max);
  const marcas = [];
  for (let v = 0; v <= max + 1e-9; v += passo) marcas.push(`<span style="left:${x(v)}%">${num(v, Math.abs(v % 1) > 1e-9 ? 1 : 0)}</span>`);
  const xn = x(normal);
  return `<div class="seg-leque" role="img" aria-label="${esc(rotulo)}">
    <svg class="seg-leque-svg" viewBox="0 0 100 20" preserveAspectRatio="none" aria-hidden="true">
      <rect class="lq-fundo" x="0" y="0" width="100" height="20"/>
      <rect class="lq-90" x="${x(q.p10)}" y="2" width="${Math.max(0.6, x(q.p90) - x(q.p10))}" height="16"/>
      <rect class="lq-80" x="${x(q.p20)}" y="2" width="${Math.max(0.6, x(q.p80) - x(q.p20))}" height="16"/>
      <line class="lq-normal" x1="${xn}" x2="${xn}" y1="0" y2="20"/>
      <line class="lq-p50" x1="${x(q.p50)}" x2="${x(q.p50)}" y1="0" y2="20"/>
    </svg>
    ${q.p90 > max ? `<div class="seg-leque-corta">até ${fmt(q.p90)} ›</div>` : ""}
    <div class="seg-leque-eixo">${marcas.join("")}</div>
  </div>`;
}

/** Legenda do leque. */
export const legendaLeque = () => `<div class="seg-legenda">
    <span><i class="sw sw-90"></i>8 em 10 anos parecidos</span><span><i class="sw sw-80"></i>6 em 10</span>
    <span><i class="sw sw-50"></i>o típico</span><span><i class="sw sw-normal"></i>o normal daqui</span></div>`;

/** Barrinhas dos anos parecidos (medido) contra o normal tracejado. vals: [[ano, valor]] em unidades. */
export function anosParecidos(vals, normal, un) {
  const max = eixoBom(Math.max(normal * 1.25, ...vals.map(([, v]) => v ?? 0))).max;
  const h = (v) => pos(v ?? 0, max);
  return `<div class="seg-anos" role="img" aria-label="Colheita medida nos anos parecidos, em ${esc(un)}; normal ${fmt(normal)}">
    <div class="seg-anos-area">
      <div class="seg-anos-normal" style="bottom:${h(normal)}%"></div>
      ${vals.map(([, v]) => `<div class="seg-anos-col"><div class="seg-anos-barra${v != null && v < normal / 2 ? " quebra" : ""}" style="height:${Math.max(2, h(v))}%"></div>
        <b style="bottom:${h(v)}%">${v == null ? "—" : fmt(v)}</b></div>`).join("")}
    </div>
    <div class="seg-anos-rot">${vals.map(([a]) => `<span>${esc(a)}</span>`).join("")}</div>
  </div>`;
}

/** Quadro dos 28 anos: um quadrado por ano (verde pagou o custo todo, âmbar só a semente, vermelho nem isso). */
export function quadro28(anos, R, origem, custo, fortes) {
  const cel = anos.map((a, i) => {
    const v = R[i];
    const cls = v == null ? "q-sem" : v >= custo.desembolso ? "q-verde" : (v >= custo.semente && v > 0) ? "q-ambar" : "q-vermelho";
    const forte = fortes.includes(a), viz = origem && origem[i] && origem[i] !== "mun";
    return `<div class="q-cel ${cls}${forte ? " q-forte" : ""}${viz ? " q-viz" : ""}" title="${a}: ${v == null ? "sem dado" : `R$ ${num(v)}/ha`}${forte ? " · mar quente (El Niño forte)" : ""}${viz ? " · completado pela região" : ""}">
      <i></i><span>${String(a).slice(2)}</span></div>`;
  });
  return `<div class="seg-quadro" role="img" aria-label="28 anos medidos, um quadrado por ano">${cel.join("")}</div>`;
}
