// QUADRA, módulo extra "E se chover…" (pontos 13 e 5 do desafio Field Shift).
// 1) cenario: controle da chuva da estação (50% a 150% do normal) → chance de quebra (10 roças) e colheita típica de milho, feijão
//    e mandioca, pela relação MEDIDA na mesorregião (IMERG × IBGE PAM, 1998–2025), com os anos do próprio município na régua;
// 2) sobreposicao: chuva (IMERG), água no solo (SMAP) e colheita (PAM) no mesmo eixo, 2015–2025, em % do normal, com a faixa mês a
//    mês (roça com água, aperto, chão descoberto pelo MODIS) e o resumo do ano típico (quando a roça vai ao campo, quando o chão fica
//    descoberto, quando aperta).
// Dados: web/dados/chuva_resposta.json e web/dados/chuva_sobreposicao/<UF>.json (ferramentas/preparar_chuva_resposta.py).
// Uso: await modulo.render(div, ctx, { partes: ["cenario", "sobreposicao"], agro })  (padrão: as duas, nessa ordem).
// O controle abre na chuva típica dos anos de El Niño forte daqui (a mesma conversa do passo); "normal" fica a um toque.
// agro = true (o IBGE daqui mistura lavoura grande): a colheita sai só em % do normal, sem sacos/ha.
import * as U from "../comum.js";

const CULT = [
  { c: "Milho", ic: "milho", un: "sacos/ha", div: 60, nome: "milho" },
  { c: "Feijão", ic: "feijao", un: "sacos/ha", div: 60, nome: "feijão" },
  { c: "Mandioca", ic: "mandioca", un: "t/ha", div: 1000, nome: "mandioca" },
];
const FORTES = [1998, 2010, 2016, 2024];
const ANO0 = 1998, SOB0 = 2015;
const ESTADO = { r: "roça com água", e: "aperto: terra seca com a roça", d: "chão descoberto", n: "entressafra", "-": "sem dado" };
const cache = {};
const pega = (p) => (cache[p] ??= fetch(new URL(`../../dados/${p}`, import.meta.url)).then((r) => (r.ok ? r.json() : null)).catch(() => null));
const tela = { cod: null, x: null, cultura: "Milho", ano: null }; // estado de tela (não é resposta da roça)
let observador = null;

/** Valor da curva (grade 50, 60 … 150% do normal) em x%. */
const interp = (v, x) => {
  const t = (Math.min(150, Math.max(50, x)) - 50) / 10, i = Math.min(9, Math.floor(t));
  return v[i] + (v[i + 1] - v[i]) * (t - i);
};
const emUn = (k, kg) => (kg == null ? null : kg / k.div);
const fmtUn = (v) => (v == null ? "—" : U.num(v, v > 0 && v < 10 ? 1 : 0));
const dez = (p) => Math.round((p ?? 0) * 10);

/** Chuva típica (mediana, em % do normal, arredondada a 5) dos anos de El Niño forte com dado aqui; null sem nenhum. */
function chuvaElNino(m) {
  const v = FORTES.map((a) => m?.ch?.[a - ANO0]).filter((x) => x != null).sort((a, b) => a - b);
  if (!v.length) return null;
  const med = v.length % 2 ? v[(v.length - 1) / 2] : (v[v.length / 2 - 1] + v[v.length / 2]) / 2;
  return Math.min(150, Math.max(50, Math.round(med / 5) * 5));
}

/** Meses (1–12) → "jul a jan" pela maior sequência circular. */
function faixaMeses(ms) {
  const s = new Set(ms);
  if (!s.size) return null;
  if (s.size === 12) return "o ano todo";
  let melhor = 0, ini = 0;
  for (let i = 1; i <= 12; i++) {
    if (s.has(((i + 10) % 12) + 1)) continue; // começa logo depois de um mês fora
    let n = 0;
    while (n < 12 && s.has(((i - 1 + n) % 12) + 1)) n++;
    if (n > melhor) { melhor = n; ini = i; }
  }
  const fim = ((ini - 1 + melhor - 1) % 12) + 1;
  return melhor === 1 ? MES(ini) : `${MES(ini)} a ${MES(fim)}`;
}
const MES = (m) => U.MESES[m - 1];

function curvaDe(cur, uf, meso) {
  const c = cur?.curvas;
  if (!c) return null;
  if (c[`${uf}|${meso}`]) return { d: c[`${uf}|${meso}`], onde: `na mesorregião ${meso}`, curto: "da região" };
  if (c[uf]) return { d: c[uf], onde: `no estado (${uf})`, curto: "do estado" };
  return c.NE ? { d: c.NE, onde: "no Nordeste", curto: "do Nordeste" } : null;
}

// ---------------------------------------------------------------- 1) E se chover…
function blocoCenario(ctx, cur, m, agro) {
  const loc = ctx.r?.local || {};
  const cv = curvaDe(cur, loc.uf, loc.mesorregiao);
  if (!cv) return `<section class="painel cc-cenario"><p class="kicker">E se chover…</p><p class="sub">Sem a relação entre chuva e colheita para este lugar.</p></section>`;
  const normal = (k) => m?.n?.[k.c] ?? ctx.r?.projecao?.[k.c]?.mediana_1998_2025_kg_ha ?? null;
  const culturas = CULT.filter((k) => cv.d[k.c] && normal(k));
  if (!culturas.length) return `<section class="painel cc-cenario"><p class="kicker">E se chover…</p><p class="sub">O IBGE não tem série de milho, feijão ou mandioca deste município.</p></section>`;
  const principal = culturas[0];
  const est = m?.est || ctx.r?.este_ano?.regime?.estacao || "";
  const anos = (m?.ch || []).map((v, i) => ({ ano: ANO0 + i, v, q: m?.q?.[principal.c]?.[i] })).filter((a) => a.v != null);
  // um ponto por ano na régua; pontos com chuva parecida sobem uma fileira para não se cobrirem
  const fileiras = [];
  const pontos = [...anos].sort((p, q) => p.v - q.v).map((a) => {
    const pos = Math.min(100, Math.max(0, a.v - 50));
    let f = fileiras.findIndex((u) => pos - u >= 3.2);
    if (f < 0) f = fileiras.length < 4 ? fileiras.length : fileiras.indexOf(Math.min(...fileiras));
    fileiras[f] = pos;
    const cls = a.q === "1" ? "quebra" : a.q === "0" ? "ok" : "sem";
    const tit = `${a.ano}: ${a.v}% da chuva normal · ${a.q === "1" ? `o ${principal.nome} quebrou` : a.q === "0" ? `o ${principal.nome} não quebrou` : "sem colheita no IBGE"}`;
    return `<i class="cc-ponto ${cls}${FORTES.includes(a.ano) ? " forte" : ""}" data-v="${a.v}" style="left:${pos}%;bottom:${f * 11}px" title="${U.esc(tit)}"></i>`;
  }).join("");
  // lavoura grande no IBGE: sem sacos/ha (não são de roça de família), só a fração do normal
  const linhas = culturas.map((k) => `<div class="cc-cult">
      <div class="cc-cult-nome">${U.ic(k.ic, "g")}<b>${U.esc(k.c)}</b></div>
      <div class="cc-cult-col"><span class="cc-num" data-cc="col-${k.c}">—</span><small>${agro ? "do normal" : k.un}</small>
        ${agro ? "" : `<span class="cc-normal">normal ${fmtUn(emUn(k, normal(k)))}</span>`}</div>
      <div class="cc-cult-q"><span data-cc="dez-${k.c}"></span><span class="cc-q" data-cc="q-${k.c}"></span></div>
    </div>`).join("");
  const a = cur.meta?.acerto_deixando_o_ano_de_fora || {};
  const am = a[principal.c];
  const fonte = `relação medida ${cv.onde}: chuva IMERG da estação × colheita IBGE PAM, 1998–2025`;
  const leste = /litoral leste/i.test(ctx.r?.este_ano?.regime?.texto || "");
  const xEN = chuvaElNino(m);
  const html = `<section class="painel cc-cenario">
    <p class="kicker">E se chover… ${U.selo("projecao", fonte)}</p>
    <div class="cc-topo">
      <div class="cc-valor"><span class="numero-grande" data-cc="pct">100%</span><span class="cc-valor-rot">da chuva normal${est ? ` de ${U.esc(est.replace("–", " a "))}` : ""}</span></div>
      ${m?.mm && !leste ? `<div class="cc-mm">${U.ic("chuva")}<span>cerca de <b data-cc="mm">${U.num(m.mm)} mm</b> pelo satélite</span></div>` : ""}
    </div>
    <div class="cc-regua">
      ${anos.length ? `<div class="cc-pontos" style="height:${Math.max(1, fileiras.length) * 11 + 4}px" aria-hidden="true">${pontos}</div>` : ""}
      <input class="cc-range" type="range" min="50" max="150" step="5" value="${tela.x}" aria-label="Chuva da estação, em % do normal">
      <div class="cc-marcas"><span>pouca</span><span>normal</span><span>muita</span></div>
    </div>
    <div class="cc-atalhos" role="group" aria-label="Atalhos da chuva">
      ${xEN != null ? `<button type="button" class="chip" data-x="${xEN}">${U.ic("onda")}como nos anos de El Niño daqui</button>` : ""}
      <button type="button" class="chip" data-x="100">${U.ic("chuva")}chuva normal</button></div>
    ${anos.length ? `<div class="cc-pontos-leg"><span><i class="cc-ponto quebra"></i>ano daqui em que o ${principal.nome} quebrou</span>
      <span><i class="cc-ponto ok"></i>não quebrou</span><span><i class="cc-ponto ok forte"></i>El Niño forte</span></div>` : ""}
    <div class="cc-culturas">${linhas}</div>
    <p class="cc-frase" data-cc="frase"></p>
    <p class="cc-local sub" data-cc="local"></p>
    ${U.verMais(`<p>Para cada cultura, juntamos todos os anos de 1998 a 2025 dos municípios ${U.esc(cv.onde.replace(/^n/, "d"))}${
        cv.d[principal.c]?.pares ? ` (${U.num(cv.d[principal.c].pares)} pares de chuva e colheita no ${principal.nome})` : ""}: a chuva da estação
      (satélite GPM IMERG da NASA, em % da mediana dos anos sem El Niño forte) e a colheita por hectare plantado (IBGE PAM, em % do normal
      do município). <b>Quebra</b> é colher menos da metade do normal. A curva é uma média ponderada pela chuva, puxada para a do estado
      quando há poucos anos, e forçada a nunca piorar quando chove mais. A colheita típica é a do meio (metade dos anos fica acima).</p>
      ${am ? `<p>Teste deixando cada ano de fora: saber a chuva melhora em ${U.num(am.ganho * 100)}% o acerto da quebra do ${principal.nome}
        (Brier ${U.num(am.brier_clima, 3)} → ${U.num(am.brier_chuva, 3)}). ${am.por_classe.map((c) => `Chuva ${c.classe}: previu ${U.num(c.previsto * 100)}, aconteceu ${U.num(c.aconteceu * 100)} em 100`).join("; ")}.</p>` : ""}
      ${a.Mandioca ? `<p>A mandioca mal responde à chuva do mesmo ano (fica 1 a 2 anos no chão; o IBGE repete o número em muitos anos): ganho de ${U.num(a.Mandioca.ganho * 100)}%.</p>` : ""}
      <p>Não é previsão da chuva de 2027: é "se chover assim". A roça da sua família varia mais que a média do município, e o seu
      pluviômetro e o que você vê na roça valem mais que esta conta.${leste ? " No litoral leste o satélite capta só 39–72% da chuva medida no chão." : ""}</p>
      <p class="pequeno">Fonte: ${U.esc(cur.meta?.script || "ferramentas/preparar_chuva_resposta.py")}, gerado em ${U.esc(cur.meta?.gerado || "—")}.</p>`)}
  </section>`;
  return { html, cv, culturas, principal, normal, m, anos, agro, xEN };
}

function ligarCenario(sec, b) {
  const $ = (k) => sec.querySelector(`[data-cc="${k}"]`);
  const range = sec.querySelector(".cc-range");
  const atualiza = () => {
    const x = +range.value;
    tela.x = x;
    range.style.setProperty("--cc-pos", `${x - 50}%`);
    range.setAttribute("aria-valuetext", `${x}% da chuva normal`);
    $("pct").textContent = `${x}%`;
    if ($("mm")) $("mm").textContent = `${U.num(Math.round((b.m.mm * x) / 100 / 10) * 10)} mm`;
    sec.querySelectorAll("[data-x]").forEach((bt) => bt.classList.toggle("verde", +bt.dataset.x === x));
    for (const k of b.culturas) {
      const d = b.cv.d[k.c], q = interp(d.q, x), r = interp(d.r, x);
      $(`col-${k.c}`).textContent = b.agro ? `${U.num(Math.round(r * 100))}%` : fmtUn(emUn(k, b.normal(k) * r));
      $(`dez-${k.c}`).innerHTML = U.dezRocas(q, "var(--terra)", `roças de ${k.nome} quebram`);
      const n = dez(q);
      $(`q-${k.c}`).innerHTML = n === 0 ? "quase nenhuma quebra" : `<b>${n} em 10</b> quebram`;
    }
    const p = b.principal, n = dez(interp(b.cv.d[p.c].q, x));
    const com = x === b.xEN ? `Com a chuva dos anos de El Niño daqui (${x}%)` : x === 100 ? "Com a chuva normal" : `Com ${x}% da chuva`;
    $("frase").textContent = n === 0 ? `${com}, quase nenhuma roça de ${p.nome} ${b.cv.curto} quebra.`
      : `${com}, ${n} em 10 roças de ${p.nome} ${b.cv.curto} quebram.`;
    const viz = b.anos.filter((a) => Math.abs(a.v - x) <= 10 && (a.q === "0" || a.q === "1"));
    const k = viz.filter((a) => a.q === "1").length;
    $("local").innerHTML = !b.anos.length ? "" : !viz.length ? `Aqui, nenhum ano de 1998 a 2025 teve chuva assim ${U.selo("medido", "IMERG e IBGE PAM do município")}`
      : `Aqui, em ${viz.length} ${viz.length === 1 ? "ano" : "anos"} com chuva assim (${Math.max(0, x - 10)}% a ${x + 10}%), o ${p.nome} quebrou em <b>${k}</b>
        ${U.selo("medido", `anos: ${viz.map((a) => `${a.ano} (${a.v}%)`).join(", ")}`)}`;
    sec.querySelectorAll(".cc-ponto[data-v]").forEach((el) => el.classList.toggle("perto", Math.abs(+el.dataset.v - x) <= 10));
  };
  range.addEventListener("input", atualiza);
  sec.querySelectorAll("[data-x]").forEach((bt) => bt.addEventListener("click", () => { range.value = bt.dataset.x; atualiza(); }));
  atualiza();
}

// ---------------------------------------------------------------- 2) chuva, solo e colheita no mesmo eixo
function contaMeses(me) {
  const c = Array.from({ length: 12 }, () => ({ r: 0, e: 0, d: 0, n: 0, "-": 0, anos: 0 }));
  for (let i = 0; i < (me || "").length; i++) {
    const s = me[i];
    c[i % 12][s] = (c[i % 12][s] || 0) + 1;
    if (s !== "-") c[i % 12].anos++;
  }
  return c;
}

function tipico(m) {
  const c = contaMeses(m.me);
  const jc = m.jc || [];
  const desc = [];
  c.forEach((x, i) => { if (x.anos && x.d / x.anos >= 0.5) desc.push(i + 1); });
  let ap = null;
  for (const mm of jc) if (c[mm - 1].e >= 2 && (!ap || c[mm - 1].e > c[ap - 1].e)) ap = mm;
  return { campo: faixaMeses(jc), desc: faixaMeses(desc), ap: ap ? { mes: MES(ap), n: c[ap - 1].e, de: c[ap - 1].anos } : null };
}

function grafico(m, k, sel, W) {
  const anos = Array.from({ length: 11 }, (_, i) => SOB0 + i);
  const curto = W < 520;
  const L = 34, R = 6, T = 14, PH = curto ? 140 : 170, F = 16, GAP = 8;
  const band = (W - L - R) / anos.length;
  const y = (v) => T + PH * (1 - Math.min(v, 200) / 200);
  const cx = (i) => L + band * (i + 0.5);
  const ch = (m.ch || []).slice(SOB0 - ANO0, SOB0 - ANO0 + 11);
  const so = m.so || [], co = m.co?.[k.c] || [];
  const linha = (vs) => {
    let d = "", aberto = false;
    vs.forEach((v, i) => { if (v == null) { aberto = false; return; } d += `${aberto ? "L" : "M"}${cx(i).toFixed(1)} ${y(v).toFixed(1)} `; aberto = true; });
    return d;
  };
  const yS = T + PH + GAP, yA = yS + F + 14;
  const iSel = anos.indexOf(sel);
  const cor = { r: "var(--green)", e: "var(--terra)", d: "var(--amber)", n: "var(--surface-3)", "-": "transparent" };
  const celulas = anos.map((a, i) => Array.from({ length: 12 }, (_, j) => {
    const s = (m.me || "")[i * 12 + j] || "-";
    const w = (band - 3) / 12;
    return `<rect x="${(L + band * i + 1.5 + w * j).toFixed(1)}" y="${yS}" width="${Math.max(0.6, w - 0.6).toFixed(1)}" height="${F}" rx="1" fill="${cor[s]}"${s === "r" || s === "d" ? ' opacity=".8"' : ""}><title>${MES(j + 1)}/${a}: ${ESTADO[s]}</title></rect>`;
  }).join("")).join("");
  return `<svg class="cc-svg" viewBox="0 0 ${W} ${yA + 6}" width="${W}" height="${yA + 6}" role="img"
      aria-label="Chuva, água no solo e colheita de ${k.nome}, de 2015 a 2025, em porcentagem do normal">
    ${iSel >= 0 ? `<rect x="${L + band * iSel}" y="${T - 10}" width="${band}" height="${yA - T + 12}" rx="6" fill="var(--surface-2)"/>` : ""}
    ${[0, 100, 200].map((v) => `<text x="${L - 6}" y="${y(v) + 3.5}" text-anchor="end" class="cc-eixo">${v}%</text>`).join("")}
    <line x1="${L}" x2="${W - R}" y1="${y(0)}" y2="${y(0)}" class="cc-base"/>
    ${ch.map((v, i) => (v == null ? "" : `<rect x="${(cx(i) - band * 0.2).toFixed(1)}" y="${y(v).toFixed(1)}" width="${(band * 0.4).toFixed(1)}" height="${(y(0) - y(v)).toFixed(1)}" rx="2" class="cc-barra"/>`)).join("")}
    <line x1="${L}" x2="${W - R}" y1="${y(100)}" y2="${y(100)}" class="cc-normal-linha"/>
    <path d="${linha(so)}" class="cc-solo"/>
    ${so.map((v, i) => (v == null ? "" : `<circle cx="${cx(i).toFixed(1)}" cy="${y(v).toFixed(1)}" r="3" class="cc-solo-p"/>`)).join("")}
    <path d="${linha(co)}" class="cc-col"/>
    ${co.map((v, i) => (v == null ? "" : `<circle cx="${cx(i).toFixed(1)}" cy="${y(v).toFixed(1)}" r="${v < 50 ? 5 : 4}" class="cc-col-p${v < 50 ? " quebra" : ""}"/>${v > 200 ? `<text x="${cx(i).toFixed(1)}" y="${T - 2}" text-anchor="middle" class="cc-eixo">${v}%</text>` : ""}`)).join("")}
    ${celulas}
    ${anos.map((a, i) => `<text x="${cx(i).toFixed(1)}" y="${yA}" text-anchor="middle" class="cc-ano${i === iSel ? " sel" : ""}">${curto ? String(a).slice(2) : a}</text>`).join("")}
    ${anos.map((a, i) => `<rect x="${L + band * i}" y="0" width="${band}" height="${yA + 6}" fill="transparent" class="cc-alvo" data-ano="${a}"><title>${a}</title></rect>`).join("")}
  </svg>`;
}

function legendaAno(m, k, a) {
  const i = a - SOB0, ch = m.ch?.[a - ANO0], so = m.so?.[i], co = m.co?.[k.c]?.[i];
  const meses = [];
  for (let j = 0; j < 12; j++) if ((m.me || "")[i * 12 + j] === "e") meses.push(MES(j + 1));
  const p = (v) => (v == null ? "—" : `${v}%`);
  return `<b>${a}</b><span>${U.ic("chuva")}chuva ${p(ch)}</span><span>${U.ic("gota")}solo ${p(so)}</span>
    ${m.co?.[k.c] ? `<span>${U.ic(k.ic)}${k.nome} ${p(co)}${co != null && co < 50 ? ' <em class="cc-quebrou">quebrou</em>' : ""}</span>` : ""}
    <span>${U.ic("alerta")}${meses.length ? `aperto em ${meses.join(", ")}` : "sem aperto"}</span>`;
}

function blocoSobre(ctx, cur, m) {
  if (!m) return `<section class="painel cc-sobre"><p class="kicker">O que já aconteceu aqui</p><p class="sub">Sem a série de satélite deste município.</p></section>`;
  const culturas = CULT.filter((k) => (m.co?.[k.c] || []).some((v) => v != null));
  return { culturas, m };
}

function desenhaSobre(sec, b, W) {
  const k = b.culturas.find((x) => x.c === tela.cultura) || b.culturas[0] || CULT[0];
  const co = b.m.co?.[k.c] || [];
  if (tela.ano == null || tela.ano < SOB0 || tela.ano > SOB0 + 10) {
    let pior = null;
    co.forEach((v, i) => { if (v != null && (pior == null || v < co[pior])) pior = i; });
    tela.ano = SOB0 + (pior ?? 1);
  }
  const t = tipico(b.m);
  const chips = b.culturas.length > 1 ? `<div class="cc-chips" role="group" aria-label="Cultura">${b.culturas.map((x) =>
    `<button type="button" class="chip${x.c === k.c ? " verde" : ""}" data-cult="${x.c}" aria-pressed="${x.c === k.c}">${U.ic(x.ic)}${U.esc(x.c)}</button>`).join("")}</div>` : "";
  const fonte = "chuva GPM IMERG; água no solo SMAP L4; colheita IBGE PAM; verde MODIS NDVI (NASA e IBGE), por município";
  const aberto = sec.querySelector("details.ver-mais")?.open; // redesenhar (ano, cultura, largura) não fecha o "ver mais"
  sec.innerHTML =`<p class="kicker">O que já aconteceu aqui · 2015 a 2025 ${U.selo("medido", fonte)}</p>
    ${chips}
    <div class="cc-graf">${grafico(b.m, k, tela.ano, W)}</div>
    <div class="cc-leg">
      <span><i class="cc-sw barra"></i>chuva da estação</span><span><i class="cc-sw solo"></i>água no solo</span>
      ${b.culturas.length ? `<span><i class="cc-sw col"></i>colheita de ${k.nome}</span>` : ""}<span><i class="cc-sw normal"></i>normal</span>
    </div>
    <div class="cc-leg cc-leg-meses">
      <span><i class="cc-mq r"></i>roça com água</span><span><i class="cc-mq e"></i>aperto</span>
      <span><i class="cc-mq d"></i>chão descoberto</span><span><i class="cc-mq n"></i>entressafra</span>
    </div>
    <p class="cc-ano-leg">${legendaAno(b.m, k, tela.ano)}</p>
    <div class="cc-tipico">
      <span class="chip verde">${U.ic("broto")}roça no campo: <b>${U.esc(t.campo || "—")}</b></span>
      ${t.desc ? `<span class="chip ambar">${U.ic("sol")}chão descoberto: <b>${U.esc(t.desc)}</b></span>` : ""}
      <span class="chip terra">${U.ic("alerta")}${t.ap ? `mais aperto: <b>${t.ap.mes}</b> (${t.ap.n} de ${t.ap.de} anos)` : "aperto raro aqui"}</span>
    </div>
    ${U.verMais(`<p>Quatro bases de satélite e de campo, cada uma com a sua grade, trazidas para o mesmo município (média das células
      que caem dentro dele) e para o mesmo eixo do tempo, cada uma em % do próprio normal:</p>
      <ul class="cc-lista">
        <li><b>Chuva</b>: GPM IMERG (NASA, ~11 km), meses ${U.esc(b.m.est || "")} (contados desde o início típico da chuva; o passo "O lugar" mostra os 4 meses mais chuvosos), em % da mediana dos anos sem El Niño forte${b.m.mm ? ` (${U.num(b.m.mm)} mm)` : ""}.</li>
        <li><b>Água no solo</b>: SMAP L4 (NASA, 9 km, zona da raiz), nos meses de roça no campo. É a água útil: 0 é o mais seco e 1 o mais
          úmido já medidos aqui (2015–2025).</li>
        <li><b>Colheita</b>: IBGE PAM, kg por ha plantado, em % da mediana 1998–2025 do município (é a média do município, não de uma roça).
          Ponto vermelho: quebra (menos da metade).</li>
        <li><b>Faixa mês a mês</b>: roça no campo são os meses em que a terra costuma ter metade ou mais da água útil, mais o mês do plantio;
          <b>aperto</b> é a terra abaixo de 1/4 da água útil ou de 60% do normal do mês com a roça no campo; <b>chão descoberto</b> é o verde
          do satélite (MODIS NDVI, ~5 km) no terço mais baixo do ano. O verde é do município todo: mato e roça juntos.</li>
      </ul>
      <p>Toque num ano para ver os números. O SMAP começa em abr/2015; meses sem dado ficam em branco.</p>`)}`;
  if (aberto) sec.querySelector("details.ver-mais").open = true;
  sec.querySelectorAll("[data-cult]").forEach((bt) => bt.addEventListener("click", () => { tela.cultura = bt.dataset.cult; tela.ano = null; desenhaSobre(sec, b, W); }));
  sec.querySelectorAll(".cc-alvo").forEach((r) => r.addEventListener("click", () => { tela.ano = +r.dataset.ano; desenhaSobre(sec, b, largura(sec)); }));
}

const largura = (el) => Math.round(Math.max(300, Math.min(980, (el.querySelector(".cc-graf") || el).clientWidth || el.clientWidth || 640)));

export default {
  id: "cenario_chuva",
  async render(el, ctx, opcoes = {}) {
    const partes = opcoes.partes || ["cenario", "sobreposicao"];
    const loc = ctx.r?.local || {};
    const cod = String(ctx.cod || loc.cod || "");
    if (tela.cod !== cod) Object.assign(tela, { cod, x: null, cultura: "Milho", ano: null });
    el.innerHTML = `<div class="cc-carregando sub">Juntando chuva, solo e colheita…</div>`;
    const [cur, uf] = await Promise.all([pega("chuva_resposta.json"), loc.uf ? pega(`chuva_sobreposicao/${loc.uf}.json`) : null]);
    const m = uf?.mun?.[cod] || null;
    tela.x ??= chuvaElNino(m) ?? 100; // abre na chuva dos anos de El Niño daqui (2027 é um deles)
    el.innerHTML = `<div class="cc">${partes.map((p) => `<div data-parte="${p}"></div>`).join("")}</div>`;
    if (partes.includes("cenario")) {
      const alvo = el.querySelector('[data-parte="cenario"]');
      const b = blocoCenario(ctx, cur, m, !!opcoes.agro);
      if (typeof b === "string") alvo.innerHTML = b;
      else { alvo.innerHTML = b.html; ligarCenario(alvo.firstElementChild, b); }
    }
    if (partes.includes("sobreposicao")) {
      const alvo = el.querySelector('[data-parte="sobreposicao"]');
      const b = blocoSobre(ctx, cur, m);
      if (typeof b === "string") alvo.innerHTML = b;
      else {
        alvo.innerHTML = `<section class="painel cc-sobre"><div class="cc-graf"></div></section>`;
        const sec = alvo.firstElementChild;
        let W = largura(sec);
        desenhaSobre(sec, b, W);
        observador?.disconnect();
        if ("ResizeObserver" in window) {
          observador = new ResizeObserver(() => { const w = largura(sec); if (Math.abs(w - W) > 30) { W = w; desenhaSobre(sec, b, W); } });
          observador.observe(sec);
        }
      }
    }
  },
};
