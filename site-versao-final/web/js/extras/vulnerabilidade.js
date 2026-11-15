// QUADRA, extra do ponto 12 do desafio (vulnerabilidade no nível do campo): "Onde o seu roçado sofre mais".
// O roçado visto de cima (mesma geometria do passo 3: montar() de passos/plantio/desenho.js) com 3 vistas:
//   água e erosão: declive do município (NASADEM: 90 m no CE; 1 km ajustado no resto do NE), faixa do alto e linhas de escorrimento;
//   seca primeiro: o alto e a terra arenosa, longe do baixio; janela de plantar do ZARC na areia × no barro (ctx.r.cardapio);
//   geada: a noite mais fria de 1979–2020 (ERA5) e o que pesa de fato aqui: dias acima de 35 °C na flor (ERA5 + calendário).
//   "E se esquentar?" (ponto 13): +1 °C e +2 °C nos dias acima de 35 °C, com o clima medido deslocado (web/dados/calor_cenario.json,
//   ferramentas/preparar_calor_cenario.py, baixado só no 1º toque).
// Dados: web/dados/declive_mun.json (ferramentas/preparar_declive.py). Uso: render(el, ctx, {vista, painel}).
import * as U from "../comum.js";
import { termo } from "./glossario.js"; // integração: "o que é?" em geada e veranico
import { montar } from "../passos/plantio/desenho.js";

const URL_DADOS = new URL("../../dados/declive_mun.json", import.meta.url);
const URL_CSS = new URL("../../css/extras/vulnerabilidade.css", import.meta.url);
const URL_CEN = new URL("../../dados/calor_cenario.json", import.meta.url);
let cache = null, cacheCen = null;
const cenarios = () => (cacheCen ||= fetch(URL_CEN).then((r) => (r.ok ? r.json() : null)).catch(() => null));
let seq = 0;
const est = { cod: null, vista: "agua", terreno: "tipico", calor: 0 }; // calor: 0 hoje, 1 = +1 °C, 2 = +2 °C

const VISTAS = [
  { id: "agua", icone: "chuva", rot: "Água e erosão" },
  { id: "seca", icone: "sol", rot: "Seca primeiro" },
  { id: "geada", icone: "termo", rot: "Geada e calor" },
];
const DIAS_FLOR = { "Milho": [50, 65], "Feijão-caupi": [35, 50], "Sorgo granífero": [55, 70], "Feijão comum": [30, 45] };
const NOME = { "Milho": "milho", "Feijão-caupi": "caupi", "Sorgo granífero": "sorgo de grão", "Sorgo forrageiro": "sorgo forrageiro",
  "Feijão comum": "feijão", "Mandioca": "mandioca", "Milheto": "milheto", "Amendoim": "amendoim" };
const nome = (c) => NOME[c] || String(c || "").toLowerCase();

function dados() {
  if (!cache) cache = fetch(URL_DADOS).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  return cache;
}
function css() {
  if ([...document.querySelectorAll("link[rel=stylesheet]")].some((l) => /extras\/vulnerabilidade\.css$/.test(l.href))) return;
  const l = document.createElement("link");
  l.rel = "stylesheet"; l.href = URL_CSS.href;
  document.head.appendChild(l);
}

// ------------------------------------------------------------------ contas pequenas
const pctTxt = (v) => (v === null || v === undefined ? "—" : v < 1 ? "< 1" : U.num(v, v < 10 ? 1 : 0).replace(/,0$/, ""));
const nivel = (d) => (d < 3 ? 1 : d < 8 ? 2 : d < 20 ? 3 : 4);
const doy = (dd, mm) => Math.round((Date.UTC(2027, mm - 1, dd) - Date.UTC(2027, 0, 1)) / 864e5);
/** "11/03–20/04; 01/11–31/12" → dias somados (as janelas do ZARC são inclusivas e podem virar o ano). */
function diasJanela(txt) {
  if (!txt || /nenhum/i.test(txt)) return 0;
  return String(txt).split(";").reduce((s, p) => {
    const m = p.match(/(\d{2})\/(\d{2})\s*[–-]\s*(\d{2})\/(\d{2})/);
    if (!m) return s;
    const a = doy(+m[1], +m[2]), b = doy(+m[3], +m[4]);
    return s + (b >= a ? b - a + 1 : 365 - a + b + 1);
  }, 0);
}
const maisDias = (iso, n) => new Date(Date.parse(iso + "T12:00:00Z") + n * 864e5).toISOString().slice(0, 10);

/** Geometria do roçado igual à do passo 3; sem plano, um roçado de 6 faixas com ⅓ de baixio. */
function geometria(ctx) {
  try {
    if (ctx.r && ctx.r.plano) {
      const l = montar(ctx.r.plano, ctx.ef);
      return { lado: l.lado, profAlto: l.profAlto, temBaixio: l.temBaixio, incerto: l.incerto, faixas: l.faixas.map((f) => [f.y0, f.y1]) };
    }
  } catch (_) { /* cai no genérico */ }
  const bx = ctx.ef && ctx.ef.tem_baixio !== false, lado = 100, prof = bx ? 100 * (1 - (ctx.ef?.baixio_frac || 1 / 3)) : 100;
  return { lado, profAlto: prof, temBaixio: bx, incerto: ctx.ef?.tem_baixio === null,
    faixas: Array.from({ length: 6 }, (_, i) => [prof * i / 6, prof * (i + 1) / 6]) };
}

/** Cultura do plano com janela de solo no ZARC: areia × barro (risco de 20%). */
function janelaSolo(ctx) {
  const card = ctx.r?.cardapio || [];
  const noPlano = new Set((ctx.r?.plano?.faixas || []).flatMap((f) => f.anos.map((a) => a.cultura)));
  const ordem = ["Feijão-caupi", "Milho", "Sorgo granífero", "Sorgo forrageiro", "Mandioca", "Feijão comum", "Milheto", "Amendoim"];
  const cand = [...ordem.filter((c) => noPlano.has(c)), ...ordem.filter((c) => !noPlano.has(c))];
  for (const nomeTexto of [true, false]) {
    for (const c of cand) {
      const k = card.find((x) => x.cultura === c);
      const ps = k && k.por_solo;
      if (!ps || ps.length < 2) continue;
      const areia = ps.find((s) => s.solo === "arenoso"), barro = ps.find((s) => s.solo === "argiloso");
      if (nomeTexto && !(areia && barro)) continue;
      const a = areia || ps[0], b = barro || ps[ps.length - 1];
      const da = diasJanela(a.risco20), db = diasJanela(b.risco20);
      if (db > 0 && db > da) return { cultura: c, areia: a, barro: b, da, db, todos: ps };
    }
  }
  return null;
}

/** Janela da flor: plantio do calendário + dias típicos até a flor; soma os dias quentes esperados (décimos/mês → por dia). */
function janelaFlor(ctx, geo, quente) {
  const a = ctx.r?.agenda;
  if (!a || !quente) return null;
  const ordem = geo.temBaixio ? ["Milho", "Feijão-caupi", "Sorgo granífero", "Feijão comum"] : ["Feijão-caupi", "Milho", "Sorgo granífero", "Feijão comum"];
  for (const c of ordem) {
    const l = a.linhas.find((x) => x.cultura === c && (geo.temBaixio || x.parte !== "Baixio"));
    const b = l && l.barras.find((x) => x.tipo === "plantio" || x.tipo === "estimado");
    if (!b) continue;
    const de = maisDias(b.de, DIAS_FLOR[c][0]), ate = maisDias(b.ate, DIAS_FLOR[c][1]);
    let soma = 0;
    for (let d = de; d <= ate; d = maisDias(d, 1)) {
      const y = +d.slice(0, 4), m = +d.slice(5, 7);
      soma += quente[m - 1] / 10 / new Date(Date.UTC(y, m, 0)).getUTCDate();
    }
    return { cultura: c, de, ate, soma, plantio: b };
  }
  return null;
}

// ------------------------------------------------------------------ o desenho
const W = 300, X0 = 22, Y0 = 30, S = 256;

function base(geo, id) {
  const s = S / geo.lado;
  let h = `<rect class="vz-cerca" x="${X0 - 9}" y="${Y0 - 9}" width="${S + 18}" height="${S + 18}" rx="7"/>`;
  geo.faixas.forEach(([a, b]) => { h += `<rect class="vz-fx" x="${X0}" y="${(Y0 + a * s).toFixed(1)}" width="${S}" height="${((b - a) * s).toFixed(1)}"/>`; });
  if (geo.temBaixio) {
    const y = Y0 + geo.profAlto * s;
    h += `<rect class="vz-bx${geo.incerto ? " incerto" : ""}" x="${X0}" y="${y.toFixed(1)}" width="${S}" height="${(Y0 + S - y).toFixed(1)}"/>`;
  }
  return h;
}
const rotulo = (x, y, txt, cls = "", ancora = "start") => `<text class="vz-t ${cls}" x="${x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="${ancora}">${U.esc(txt)}</text>`;
const icone = (nomeIc, x, y, esc_, cls) => `<g class="vz-ic ${cls}" transform="translate(${x.toFixed(1)},${y.toFixed(1)}) scale(${esc_})">${U.IC[nomeIc]}</g>`;

/** Linha d'água que desce do alto e se junta num rego (ondula mais quanto mais forte a ladeira). */
function escorre(x, cx, y1, y2, amp, fase) {
  const n = Math.max(8, Math.round((y2 - y1) / 6));
  let d = "";
  for (let k = 0; k <= n; k++) {
    const t = k / n, y = y1 + (y2 - y1) * t;
    const xx = x + (cx - x) * 0.45 * t * t + amp * Math.sin(t * Math.PI * 3 + fase) * (0.4 + 0.6 * t);
    d += `${k ? "L" : "M"}${xx.toFixed(1)} ${y.toFixed(1)}`;
    if (k === n) d += `M${(xx - 4).toFixed(1)} ${(y - 6).toFixed(1)}L${xx.toFixed(1)} ${y.toFixed(1)}L${(xx + 4).toFixed(1)} ${(y - 6).toFixed(1)}`;
  }
  return d;
}

function svgAgua(geo, L, id) {
  const s = S / geo.lado, yFim = Y0 + (geo.temBaixio ? geo.profAlto : geo.lado) * s;
  const nPerde = L >= 3 ? 2 : 1;
  const yPerde = Y0 + geo.faixas[Math.min(nPerde, geo.faixas.length) - 1][1] * s;
  const n = [3, 5, 7, 9][L - 1], amp = [2, 3.5, 5, 6.5][L - 1];
  let h = base(geo, id);
  h += `<rect class="vz-perde n${L}" x="${X0}" y="${Y0}" width="${S}" height="${(yPerde - Y0).toFixed(1)}"/>`;
  geo.faixas.slice(1).forEach(([a]) => { h += `<line class="vz-nivel" x1="${X0}" y1="${(Y0 + a * s).toFixed(1)}" x2="${X0 + S}" y2="${(Y0 + a * s).toFixed(1)}"/>`; });
  const regos = L >= 3 ? [X0 + S * 0.32, X0 + S * 0.7] : [X0 + S * 0.5];
  let p = "";
  for (let i = 0; i < n; i++) {
    const x = X0 + S * (i + 0.5) / n, cx = regos.reduce((m, r) => (Math.abs(r - x) < Math.abs(m - x) ? r : m));
    p += escorre(x, cx, Y0 + 6, yFim - 4, amp, i * 1.7);
  }
  h += `<path class="vz-escorre n${L}" d="${p}"/>`;
  if (geo.temBaixio) {
    h += `<rect class="vz-deposito" x="${X0}" y="${yFim.toFixed(1)}" width="${S}" height="${Math.min(22, Y0 + S - yFim).toFixed(1)}" fill="url(#vz-pontos-${id})"/>`;
    h += rotulo(X0 + 10, Math.min(Y0 + S - 10, yFim + 38), "o baixio recebe a terra", "fundo");
  }
  h += rotulo(X0 + S - 10, Y0 + 20, "perde terra", "terra", "end");
  return h;
}

function svgSeca(geo, terra, id) {
  const s = S / geo.lado, yAlto = Y0 + (geo.temBaixio ? geo.profAlto : geo.lado) * s;
  let h = base(geo, id);
  h += `<rect class="vz-seco" x="${X0}" y="${Y0}" width="${S}" height="${(yAlto - Y0).toFixed(1)}" fill="url(#vz-grad-${id})"/>`;
  const hAlto = yAlto - Y0;
  if (terra === "arenosa") {
    h += `<rect class="vz-areia" x="${X0}" y="${Y0}" width="${S}" height="${hAlto.toFixed(1)}" fill="url(#vz-areia-${id})"/>`;
  } else if (terra !== "barro") {
    h += `<ellipse class="vz-areia" cx="${X0 + S * 0.27}" cy="${(Y0 + hAlto * 0.28).toFixed(1)}" rx="${S * 0.17}" ry="${(hAlto * 0.15).toFixed(1)}" fill="url(#vz-areia-${id})"/>
      <ellipse class="vz-areia" cx="${X0 + S * 0.72}" cy="${(Y0 + hAlto * 0.55).toFixed(1)}" rx="${S * 0.13}" ry="${(hAlto * 0.12).toFixed(1)}" fill="url(#vz-areia-${id})"/>`;
    h += rotulo(X0 + S * 0.27, Y0 + hAlto * 0.28 + 4, "areia?", "forte", "middle");
  }
  h += icone("sol", X0 + S - 34, Y0 + 8, 1.05, "ambar");
  h += rotulo(X0 + 10, Y0 + 20, "seca primeiro", "ambar");
  if (geo.temBaixio) {
    h += icone("gota", X0 + 10, yAlto + 10, 0.9, "azul");
    h += rotulo(X0 + 36, yAlto + 28, "o baixio guarda água", "azul");
  }
  return h;
}

function svgGeada(geo, tmin, id) {
  const s = S / geo.lado;
  let h = base(geo, id) + `<rect class="vz-calor" x="${X0}" y="${Y0}" width="${S}" height="${S}"/>`;
  h += icone("sol", X0 + S / 2 - 20, Y0 + S * 0.22, 1.7, "ambar");
  h += rotulo(X0 + S / 2, Y0 + S * 0.22 + 64, "o calor pega o roçado todo", "forte", "middle");
  if (geo.temBaixio && tmin !== null && tmin < 12) {
    const y = Y0 + geo.profAlto * s;
    h += rotulo(X0 + 10, Math.min(Y0 + S - 10, y + 26), "se gelasse, seria aqui: o ar frio desce", "azul");
  }
  return h;
}

function svg(geo, vista, extra, id) {
  const corpo = vista === "agua" ? svgAgua(geo, extra.L, id) : vista === "seca" ? svgSeca(geo, extra.terra, id) : svgGeada(geo, extra.tmin, id);
  const H = Y0 + S + 18;
  return `<svg class="vz-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${U.esc(extra.aria)}">
    <defs>
      <linearGradient id="vz-grad-${id}" x1="0" y1="0" x2="0" y2="1"><stop class="vz-g0" offset="0"/><stop class="vz-g1" offset="1"/></linearGradient>
      <pattern id="vz-areia-${id}" width="7" height="7" patternUnits="userSpaceOnUse"><circle class="vz-grao" cx="2" cy="2" r="1.1"/><circle class="vz-grao" cx="5.5" cy="5.2" r=".8"/></pattern>
      <pattern id="vz-pontos-${id}" width="6" height="6" patternUnits="userSpaceOnUse"><circle class="vz-terrinha" cx="3" cy="3" r="1.2"/></pattern>
    </defs>
    <text class="vz-eixo" x="${X0 - 9}" y="${Y0 - 16}">alto</text>
    <text class="vz-eixo" x="${X0 + S + 9}" y="${Y0 - 16}" text-anchor="end">a água desce ↓</text>
    ${corpo}</svg>`;
}

// ------------------------------------------------------------------ o lado: número, frase, conferir
const confira = (txt) => `<p class="vz-confira">${U.ic("lupa")}<span><b>Confira no chão:</b> ${txt}</span></p>`;

function ladoAgua(ctx, m) {
  const d50 = m[0], d90 = m[1], medido = m[2] === 1;
  const sel = medido ? U.selo("medido", "NASADEM (NASA, SRTM reprocessado) a 90 m, declive mediano do município")
    : U.selo("suposicao", "estimado: NASADEM a 1 km, ajustado à escala de 90 m pela relação medida nos 184 municípios do CE");
  const val = est.terreno === "plano" ? Math.min(d50, 2.9) : est.terreno === "ladeira" ? d90 : d50;
  const L = nivel(val);
  const frase = ["Quase plano: a água corre devagar, mas a chuva forte leva terra solta.",
    "Ladeira suave: na chuva forte, a água desce e leva a terra do alto.",
    "Ladeira: a água ganha força e abre rego no meio do roçado.",
    "Ladeira forte: plante só em curva de nível e com o chão coberto."][L - 1];
  const rot = est.terreno === "plano" ? "Terreno mais plano" : est.terreno === "ladeira" ? "1 em 10 terrenos daqui" : "Ladeira típica aqui";
  const chip = (k, t) => `<button type="button" class="vz-terreno" data-vz-terreno="${k}" aria-pressed="${est.terreno === k}">${t}</button>`;
  return {
    L,
    html: `${U.ind({ icone: "onda", rot, val: (est.terreno === "plano" ? "até 3" : pctTxt(val)), un: "% de declive", selo: sel,
      sub: est.terreno === "plano" ? "cai menos de 3 m a cada 100 m" : `cai ≈ ${pctTxt(val)} m a cada 100 m` })}
      <p class="vz-frase">${frase}</p>
      <div class="vz-terrenos" role="group" aria-label="O seu terreno"><span class="pequeno sub">O seu é:</span>
        ${chip("plano", "mais plano")}${chip("tipico", "o típico")}${chip("ladeira", "mais inclinado")}</div>
      <div class="vz-segura"><span class="chip verde">${U.ic("faixas")} faixa em nível</span><span class="chip verde">${U.ic("broto")} palhada no chão</span></div>
      ${confira("depois da primeira chuva forte, veja onde abriu rego. É ali.")}`,
    ver: `<p><b>De onde vem.</b> Declive do relevo medido do espaço (NASADEM, o SRTM de 2000 reprocessado pela NASA), em %: metros que a terra
      cai a cada 100 m. Típico = metade do município tem menos que ${pctTxt(d50)} %; 1 em 10 terrenos passa de ${pctTxt(d90)} %.
      ${medido ? "No Ceará, medido a 90 m." : `Fora do Ceará só temos a grade de 1 km, que achata as ladeiras (no CE, a 90 m o declive dá cerca de 3 vezes o
      de 1 km). Ajustamos com a relação medida nos 184 municípios do CE (R² 0,88; erro típico 11 %; 1 em 10 municípios erra mais de 35 %). Aqui é estimativa.`}</p>
      <p>Classes da Embrapa: até 3 % plano, 3–8 % suave, 8–20 % ondulado, acima de 20 % forte. O desenho muda com a classe.</p>
      <p><b>O desenho é suposição.</b> O roçado do plano, alto em cima e faixas em nível. A água desce, junta força e leva a terra fina do alto;
      o baixio recebe terra e água. Faixa em nível, palhada no chão e cerca viva cortam a enxurrada.</p>
      <p><b>O que o dado não vê.</b> O seu roçado pode ser mais plano ou mais inclinado que o típico (por isso a escolha "O seu é"). Serrote e lajedo
      entram no declive do município. A força de cada chuva não está na conta.</p>`,
  };
}

function ladoSeca(ctx, js) {
  const terra = ctx.ef?.terra || "nao_sei";
  const sel = U.selo("medido", "ZARC 2026/27 (MAPA): janela de plantio de risco de 20% por tipo de solo");
  const semBx = ctx.ef?.tem_baixio === false;
  const frase = terra === "barro" ? "Mesmo no barro, o alto seca antes do baixio."
    : semBx ? "O alto e a terra arenosa secam primeiro." : "O alto e a terra arenosa secam primeiro. O baixio guarda água.";
  if (!js) {
    return { html: `${U.faixa("sol", "ambar", frase)}
      ${confira(`no ${termo("veranico", "veranico")}, veja onde a planta murcha primeiro. Ali é o ponto seco.`)}`,
    ver: `<p>Sem janela do ZARC por tipo de solo para as culturas daqui. O alto seca primeiro: a água escorre e se infiltra mais embaixo.</p>` };
  }
  const nA = /arenoso/.test(js.areia.solo) ? "na areia" : `no solo ${js.areia.solo}`, nB = /argiloso/.test(js.barro.solo) ? "no barro" : `no solo ${js.barro.solo}`;
  const dias = (d) => (d === 0 ? "0" : String(d));
  const meu = terra === "barro"
    ? { rot: `No seu barro: janela do ${nome(js.cultura)}`, val: dias(js.db), sub: `${nA}: ${js.da} dias` }
    : { rot: `${terra === "arenosa" ? "Na sua areia" : "Na terra arenosa"}: janela do ${nome(js.cultura)}`, val: dias(js.da), sub: `${nB}: ${js.db} dias` };
  const fraseFinal = js.da === 0 && terra !== "barro" ? `${nA[0].toUpperCase() + nA.slice(1)}, o ${nome(js.cultura)} não tem janela segura aqui.` : frase;
  const linhas = js.todos.map((s) => `<tr><td>${U.esc(s.solo)}</td><td>${U.esc(s.risco20 || "—")}</td><td>${diasJanela(s.risco20)} dias</td></tr>`).join("");
  return {
    html: `${U.ind({ icone: "areia", rot: meu.rot, val: meu.val, un: "dias para plantar", sub: meu.sub, selo: sel })}
      <p class="vz-frase">${fraseFinal}</p>
      ${confira(`no ${termo("veranico", "veranico")}, veja onde a planta murcha primeiro. Ali é o ponto seco.`)}`,
    ver: `<p><b>De onde vem.</b> A janela de plantar de risco 20 % do ZARC 2026/27 (MAPA): as datas em que, em pelo menos 8 de 10 anos, o ${termo("balanco_hidrico", "balanço hídrico")}
      (a água que entra menos a que o sol e a planta tiram) dá para o ${nome(js.cultura)} fechar o ciclo. Terra arenosa segura menos água, por isso a janela encolhe.</p>
      <table><tr><th>Solo</th><th>Janela</th><th>Dias</th></tr>${linhas}</table>
      <p><b>O desenho é suposição.</b> O alto seca primeiro: a água da chuva escorre e se infiltra mais embaixo, e o baixio fica úmido por mais tempo.
      É regra de encosta, não medida do seu roçado: o satélite não vê mancha de areia dentro de 1 ha. ${terra === "nao_sei" || terra === "mista"
        ? "As manchas \"areia?\" marcam onde costuma ter; só você sabe se tem." : ""}</p>`,
  };
}

/** q = dias quentes por mês (décimos); q0 = os de hoje, em contorno atrás das barras, quando q é um cenário (mesma escala). */
function graficoCalor(q, flor, q0 = null) {
  const w = 264, h = 78, bw = 15, gap = (w - 12 * bw) / 11, max = Math.max(10, ...q.map((v) => v / 10), ...(q0 || []).map((v) => v / 10));
  const x = (i) => i * (bw + gap);
  const xDia = (iso) => { const m = +iso.slice(5, 7) - 1, d = +iso.slice(8, 10); return x(m) + (bw + gap) * (d - 1) / 31; };
  let faixaFlor = "";
  if (flor) {
    const a = xDia(flor.de), b = xDia(flor.ate) + bw * 0.3;
    const caixa = (x1, x2) => `<rect class="vz-flor" x="${x1.toFixed(1)}" y="0" width="${Math.max(3, x2 - x1).toFixed(1)}" height="${h - 16}" rx="4"/>`;
    faixaFlor = flor.ate.slice(0, 4) > flor.de.slice(0, 4) || b < a ? caixa(a, w) + caixa(0, b) : caixa(a, b);
    faixaFlor += `<text class="vz-t verde" x="${Math.min(w - 2, Math.max(2, a + 2)).toFixed(1)}" y="10">flor</text>`;
  }
  const im = q.indexOf(Math.max(...q));
  const fantasma = q0 ? q0.map((v, i) => {
    const hh = (h - 30) * (v / 10) / max;
    return `<rect class="vz-hoje" x="${x(i).toFixed(1)}" y="${(h - 16 - hh).toFixed(1)}" width="${bw}" height="${Math.max(0.8, hh).toFixed(1)}" rx="2"/>`;
  }).join("") : "";
  const barras = q.map((v, i) => {
    const hh = (h - 30) * (v / 10) / max;
    return `<rect class="vz-quente" x="${x(i).toFixed(1)}" y="${(h - 16 - hh).toFixed(1)}" width="${bw}" height="${Math.max(0.8, hh).toFixed(1)}" rx="2"/>
      <text class="vz-mes" x="${(x(i) + bw / 2).toFixed(1)}" y="${h - 3}" text-anchor="middle">${"JFMAMJJASOND"[i]}</text>`;
  }).join("");
  const topo = q[im] > 0 ? `<text class="vz-t terra" x="${(x(im) + bw / 2).toFixed(1)}" y="${(h - 20 - (h - 30) * (q[im] / 10) / max).toFixed(1)}" text-anchor="middle">${Math.round(q[im] / 10)}</text>` : "";
  return `<svg class="vz-graf" viewBox="0 0 ${w} ${h}" role="img" aria-label="Dias acima de 35 °C em cada mês">${faixaFlor}${barras}${fantasma}${topo}</svg>`;
}

const quantos = (soma) => (soma === null ? "" : soma < 0.5 ? "quase nenhum dia" : soma < 1 ? "menos de 1 dia" : `≈ ${Math.round(soma)} dias`);

function ladoGeada(ctx, m, geo, cen) {
  const tmin = m[3], q0 = m[4];
  const k = q0 && cen ? est.calor : 0, q = k ? cen[k - 1] : q0; // cenário só quando o arquivo chegou
  const sel = U.selo("medido", "ERA5 (ECMWF/Copernicus) diário 1979–2020, quadrados de ~28 km");
  if (tmin === null) return { html: `<p class="vz-frase">Sem dado de temperatura para este ponto.</p>`, ver: "" };
  const fr = tmin <= 9 ? "Frio raro de serra. Geada pede perto de 0 °C: pergunte a quem mora aí."
    : "Geada pede perto de 0 °C. O perigo aqui é o calor na flor.";
  const flor = janelaFlor(ctx, geo, q), flor0 = k ? janelaFlor(ctx, geo, q0) : null;
  const qtd = quantos(flor ? flor.soma : null);
  const im = q ? q.indexOf(Math.max(...q)) : -1;
  const supoe = k ? `o clima medido (ERA5 1979–2020) com +${k} °C em todos os dias: conta os dias de ${35 - k} °C ou mais; não é projeção de modelo climático. ` : "";
  const linhaFlor = flor ? `<p class="vz-flor-txt"><b>Na flor do ${nome(flor.cultura)}</b> (${U.dataBR(flor.de, true)} a ${U.dataBR(flor.ate, true)}): ${qtd}
      acima de 35 °C${flor0 ? ` <span class="sub">(hoje: ${quantos(flor0.soma)})</span>` : ""} ${U.selo("suposicao", `${supoe}flor ${DIAS_FLOR[flor.cultura][0]}–${DIAS_FLOR[flor.cultura][1]} dias depois de plantar (típico; muda com a variedade), sobre a janela de plantar do calendário`)}</p>` : "";
  // "E se esquentar?": o mesmo clima com +1 °C ou +2 °C (controle de cenário de temperatura)
  const esquenta = q0 ? `<div class="vz-esquenta" role="group" aria-label="E se esquentar?"><span class="vz-graf-rot">E se esquentar?</span>
      ${[0, 1, 2].map((j) => `<button type="button" class="chip${j === est.calor ? " verde" : ""}" data-vz-calor="${j}" aria-pressed="${j === est.calor}">${j ? `+${j} °C` : "hoje"}</button>`).join("")}</div>` : "";
  return {
    html: `${U.ind({ icone: "termo", rot: "Noite mais fria em 42 anos", val: U.num(tmin), un: "°C", selo: sel,
        sub: tmin <= 9 ? `${termo("geada", "geada")}: muito rara, só em serra` : `${termo("geada", "geada")} aqui: quase nunca` })}
      <p class="vz-frase">${fr}</p>
      ${q ? `<div class="vz-calor-caixa">${esquenta}<p class="vz-graf-rot">Dias acima de 35 °C, por mês${k ? ` · com +${k} °C <span class="vz-hoje-leg">(contorno: hoje)</span>` : ""}</p>${graficoCalor(q, flor, k ? q0 : null)}${linhaFlor}
        ${im >= 0 && q[im] >= 50 ? `<p class="pequeno sub">Em ${U.MESES[im]}, são ${Math.round(q[im] / 10)} dias no mês: não deixe a flor cair aí.</p>` : ""}</div>` : ""}
      ${confira("pergunte aos mais velhos em que anos a flor queimou de calor.")}`,
    ver: `<p><b>Geada.</b> A noite mais fria de 1979 a 2020 no quadrado do ERA5 (reanálise europeia, ≈ 28 km) mais frio do município. Em todo o
      Nordeste, a mais fria foi 8 °C, nas serras da Bahia (Chapada Diamantina, Vitória da Conquista). Geada pede perto de 0 °C. A reanálise
      suaviza serra e baixada: numa baixada de serra alta, a noite pode ser alguns graus mais fria. Se gelasse, seria no baixio: o ar frio desce e para lá.</p>
      <p><b>Calor na flor.</b> Barras = dias com máxima de 35 °C ou mais, por mês, na média de 42 anos (ERA5). Acima de ≈ 35 °C o pólen do milho
      perde força (Schoper et al. 1987, <i>Plant Physiology</i> 83:121) e o caupi derruba flor (Hall 2004, <i>European Journal of Agronomy</i> 21:447).
      ${flor ? `A flor do ${nome(flor.cultura)}: ${DIAS_FLOR[flor.cultura][0]} a ${DIAS_FLOR[flor.cultura][1]} dias depois de plantar (típico, muda com a
      variedade), sobre a janela de plantar do calendário (${U.dataBR(flor.plantio.de, true)} a ${U.dataBR(flor.plantio.ate, true)}).` : ""}
      Média de um quadrado de 28 km: no roçado, o termômetro pode marcar mais.</p>
      <p><b>E se esquentar?</b> "+1 °C" e "+2 °C" contam, nos mesmos 42 anos, os dias de 34 °C e de 33 °C ou mais: é o clima medido com todos
      os dias mais quentes por igual (suposição simples, não um modelo do clima futuro). Desde 1981 a máxima daqui já subiu; o painel do município, no mapa (aba Solo e clima), mostra quanto.</p>
      <p><b>Veranico.</b> A falta de chuva no meio da estação é o risco que a janela do ZARC já mede: risco de 20 % = até 2 em 10 anos com perda
      por falta de água.</p>`,
  };
}

// ------------------------------------------------------------------ módulo
function desenhar(caixa, ctx, m, geo, js, id, cen = null) {
  const terra = ctx.ef?.terra || "nao_sei";
  let lado, extra;
  if (est.vista === "agua") {
    if (!m || m[0] === null) { lado = { html: `<p class="vz-frase">Sem dado de relevo para este ponto.</p>`, ver: "", L: 2 }; }
    else lado = ladoAgua(ctx, m);
    extra = { L: lado.L || 2, aria: "O roçado visto de cima: a água desce do alto e leva a terra" };
  } else if (est.vista === "seca") {
    lado = ladoSeca(ctx, js);
    extra = { terra, aria: "O roçado visto de cima: o alto e a terra arenosa secam primeiro" };
  } else {
    lado = m ? ladoGeada(ctx, m, geo, cen) : { html: `<p class="vz-frase">Sem dado de temperatura para este ponto.</p>`, ver: "" };
    extra = { tmin: m ? m[3] : null, aria: "O roçado visto de cima: o calor pega o roçado todo" };
  }
  caixa.querySelectorAll("[data-vz-vista]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.vzVista === est.vista)));
  caixa.querySelector("[data-vz-fig]").innerHTML = svg(geo, est.vista, extra, id);
  caixa.querySelector("[data-vz-lado]").innerHTML = lado.html;
  caixa.querySelector("[data-vz-ver]").innerHTML = lado.ver ? U.verMais(lado.ver) : "";
  caixa.querySelectorAll("[data-vz-terreno]").forEach((b) => b.addEventListener("click", () => {
    est.terreno = b.dataset.vzTerreno;
    desenhar(caixa, ctx, m, geo, js, id, cen);
  }));
  caixa.querySelectorAll("[data-vz-calor]").forEach((b) => b.addEventListener("click", async () => {
    est.calor = +b.dataset.vzCalor;
    const todos = est.calor ? await cenarios() : null;
    const meu = todos?.m?.[String(ctx.cod || ctx.r?.local?.cod)] || null;
    if (est.calor && !meu) est.calor = 0; // sem o arquivo (ou sem o município): fica no "hoje"
    desenhar(caixa, ctx, m, geo, js, id, meu);
    caixa.querySelector(`[data-vz-calor="${est.calor}"]`)?.focus();
  }));
}

export default {
  id: "vulnerabilidade",
  async render(el, ctx, opcoes = {}) {
    css();
    const id = ++seq;
    // a vista escolhida sobrevive ao redesenho do passo; volta ao início (opcoes.vista ou "agua") só quando muda o município
    if (est.cod !== ctx.cod) Object.assign(est, { cod: ctx.cod, terreno: "tipico", calor: 0, vista: VISTAS.some((v) => v.id === opcoes.vista) ? opcoes.vista : "agua" });
    const painel = opcoes.painel !== false;
    el.innerHTML = `<section class="${painel ? "painel " : ""}vz" data-vz>
      <div class="vz-topo"><h3>Onde o seu roçado sofre mais</h3>
        <div class="vz-botoes" role="group" aria-label="O que olhar no roçado">${VISTAS.map((v) =>
          `<button type="button" class="vz-b" data-vz-vista="${v.id}" aria-pressed="${v.id === est.vista}">${U.ic(v.icone)}<span>${v.rot}</span></button>`).join("")}</div></div>
      <div class="vz-grade"><figure class="vz-fig" data-vz-fig><div class="vz-carregando"></div></figure><div class="vz-lado" data-vz-lado></div></div>
      <div data-vz-ver></div></section>`;
    const caixa = el.querySelector("[data-vz]");
    const base = await dados();
    if (!el.contains(caixa)) return; // o passo foi redesenhado enquanto os dados chegavam
    const m = base && base.m ? base.m[String(ctx.cod || ctx.r?.local?.cod)] || null : null;
    const geo = geometria(ctx);
    const js = janelaSolo(ctx);
    if (!base) caixa.querySelector("[data-vz-ver]").innerHTML = `<p class="pequeno sub">Os dados de relevo e de temperatura não carregaram.</p>`;
    // com um cenário de calor já escolhido (redesenho do passo), traz o arquivo antes de desenhar
    const meuCen = est.calor ? (await cenarios())?.m?.[String(ctx.cod || ctx.r?.local?.cod)] || null : null;
    if (!meuCen) est.calor = 0;
    caixa.querySelectorAll("[data-vz-vista]").forEach((b) => b.addEventListener("click", () => {
      est.vista = b.dataset.vzVista;
      desenhar(caixa, ctx, m, geo, js, id, meuCen);
    }));
    desenhar(caixa, ctx, m, geo, js, id, meuCen);
  },
};
