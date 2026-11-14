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

/** Leque de um ciclo: P10–P90 claro, P20–P80 escuro, P50 traço, normal tracejado. q em unidades da cultura. */
export function leque(q, normal, eixo, rotulo) {
  const { max, passo } = eixo;
  const x = (v) => pos(v, max);
  const corta = q.p90 > max;
  const marcas = [];
  for (let v = 0; v <= max + 1e-9; v += passo) marcas.push(`<span style="left:${x(v)}%">${num(v, Math.abs(v % 1) > 1e-9 ? 1 : 0)}</span>`);
  const xn = x(normal);
  return `<div class="seg-leque" role="img" aria-label="${esc(rotulo)}">
    <div class="seg-leque-normal" style="left:${Math.min(92, Math.max(8, xn))}%">normal ${fmt(normal)}</div>
    <svg class="seg-leque-svg" viewBox="0 0 100 20" preserveAspectRatio="none" aria-hidden="true">
      <rect class="lq-fundo" x="0" y="0" width="100" height="20"/>
      <rect class="lq-90" x="${x(q.p10)}" y="2" width="${Math.max(0.6, x(q.p90) - x(q.p10))}" height="16"/>
      <rect class="lq-80" x="${x(q.p20)}" y="2" width="${Math.max(0.6, x(q.p80) - x(q.p20))}" height="16"/>
      <line class="lq-normal" x1="${xn}" x2="${xn}" y1="0" y2="20"/>
      <line class="lq-p50" x1="${x(q.p50)}" x2="${x(q.p50)}" y1="0" y2="20"/>
    </svg>
    ${corta ? `<div class="seg-leque-corta" title="O lado de cima (P90) passa do fim do eixo">até ${fmt(q.p90)} ›</div>` : ""}
    <div class="seg-leque-eixo">${marcas.join("")}</div>
  </div>`;
}

/** Legenda do leque (uma vez por seção). */
export function legendaLeque() {
  return `<div class="seg-legenda" aria-label="Como ler o leque">
    <span><i class="sw sw-90"></i>8 em 10 anos parecidos caem aqui (P10–P90)</span>
    <span><i class="sw sw-80"></i>6 em 10 (P20–P80)</span>
    <span><i class="sw sw-50"></i>o típico (P50: metade acima, metade abaixo)</span>
    <span><i class="sw sw-normal"></i>o normal daqui (mediana 1998–2025)</span>
  </div>`;
}

/** Grade de 10 roças: n pintadas = roças que quebram em 10 anos parecidos. */
export function grade10(p, rotulo) {
  const n = Math.max(0, Math.min(10, Math.round((p ?? 0) * 10)));
  const roca = (i) => {
    const x = (i % 5) * 26, y = Math.floor(i / 5) * 26, q = i < n;
    return `<g transform="translate(${x} ${y})"><rect class="${q ? "rc-quebra" : "rc-ok"}" x="1" y="1" width="22" height="22" rx="4"/>
      <path class="${q ? "rc-linha-q" : "rc-linha"}" d="M6 7h12M6 12h12M6 17h12"/></g>`;
  };
  return `<svg class="seg-grade" viewBox="0 0 130 52" role="img" aria-label="${esc(rotulo)}">${Array.from({ length: 10 }, (_, i) => roca(i)).join("")}</svg>`;
}

/** Barras dos anos parecidos (medido) contra o normal tracejado. vals: [[ano, valor]] em unidades. */
export function anosParecidos(vals, normal, un) {
  const max = eixoBom(Math.max(normal * 1.25, ...vals.map(([, v]) => v ?? 0))).max;
  const h = (v) => pos(v ?? 0, max);
  return `<div class="seg-anos" role="img" aria-label="Colheita medida nos anos parecidos, em ${esc(un)}">
    <div class="seg-anos-area">
      <div class="seg-anos-normal" style="bottom:${h(normal)}%"></div>
      ${vals.map(([a, v]) => `<div class="seg-anos-col"><div class="seg-anos-barra" style="height:${Math.max(1.5, h(v))}%"></div>
        <b style="bottom:${h(v)}%">${v == null ? "—" : fmt(v)}</b></div>`).join("")}
    </div>
    <div class="seg-anos-rot">${vals.map(([a]) => `<span>${esc(a)}</span>`).join("")}</div>
    <div class="seg-anos-leg"><i></i>normal daqui: ${fmt(normal)} ${esc(un)}</div>
  </div>`;
}

/** Quadro dos 28 anos: um quadrado por ano (verde pagou o desembolso, âmbar só a semente, vermelho nem isso). */
export function quadro28(anos, R, origem, custo, fortes) {
  const cel = anos.map((a, i) => {
    const v = R[i];
    const cls = v == null ? "q-sem" : v >= custo.desembolso ? "q-verde" : (v >= custo.semente && v > 0) ? "q-ambar" : "q-vermelho";
    const forte = fortes.includes(a), viz = origem && origem[i] && origem[i] !== "mun";
    const txt = v == null ? "sem dado" : `R$ ${num(v)}/ha`;
    return `<div class="q-cel ${cls}${forte ? " q-forte" : ""}${viz ? " q-viz" : ""}" title="${a}: ${txt}${forte ? " · El Niño forte" : ""}${viz ? " · completado pela mesorregião" : ""}">
      <i></i><span>${String(a).slice(2)}</span></div>`;
  });
  return `<div class="seg-quadro" role="img" aria-label="28 anos medidos, um quadrado por ano">${cel.join("")}</div>`;
}

/** Cenários do portão: P50 do milho como fração do normal (um eixo, 0 a 1,5× o normal). */
export function cenarios(linhas, normal, un) {
  const max = 1.5;
  return `<div class="seg-cen">${linhas.map((l) => `<div class="seg-cen-linha ${l.cls || ""}">
      <div class="seg-cen-rot">${l.rotulo}</div>
      <div class="seg-cen-barra"><i style="width:${pos(l.p50, max)}%"></i><b class="seg-cen-normal" style="left:${pos(1, max)}%"></b></div>
      <div class="seg-cen-num"><b>${normal ? fmt(l.p50 * normal) + " " + esc(un) : num(l.p50 * 100) + "% do normal"}</b> típico</div>
    </div>`).join("")}
    <div class="seg-cen-linha seg-cen-eixo-l"><div></div><div class="seg-cen-eixo"><span style="left:0%">0</span><span style="left:${pos(0.5, max)}%">metade</span><span style="left:${pos(1, max)}%">normal</span><span style="left:100%">1,5×</span></div><div></div></div>
  </div>`;
}
