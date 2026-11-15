// QUADRA, site final: passo 3 "Como plantar" (roca.html#/<cod>/3). Versão 2: pouco texto, no visual da tela inicial.
// Junta a rotação do José (Partes A/B/C, baixio, bordas, calendário: protótipo/, branch estudo-jose, e7a23b5) com a distribuição
// em faixas do Vicente Lima (PercolaCampo, branch estudo-vicente, 18fd0e3). Desenho e algoritmo: analise/distribuicao.md;
// o que do PercolaCampo é defensável: analise/vicente.md. Contrato do ctx e regras de texto: js/passos/LEIA-ME.md.
import { montar, grade, espalhar, ehGram, LIMIAR_SITIO } from "./plantio/desenho.js";
import { linhaDoTempo, calendarioCompleto, ligarCalendario, agora } from "./plantio/calendario.js";
import { olho, OLHOS } from "../extras/voce_decide.js";
import { lerHoje } from "../extras/hoje_ideal.js";
// Ordem (analise/fluxo/00_FLUXO_FINAL.md, seção 3, tela 2): título → "Agora" → roçado → maniva → o que fazer e quando → giro (extra
// historico) → "Por que este plano", com 3 "ver mais": vulnerabilidade, por que em faixas e saude_solo (extras montados ao abrir).
// "Seu olho" (ponto 16) à vista: o da metade guardada (calendário) e o do giro; o das faixas fica no "ver mais" da rotação.

// estado de tela (não é resposta): ano escolhido, vista por ano ou mês a mês, mês, relógios das animações
const est = { cod: null, ano: 0, modo: "ano", mes: null, relogio: null, foco: null, compacto: false };

const CURTO = { "Feijão-caupi": "caupi", "Sorgo forrageiro": "sorgo forrageiro", "Sorgo granífero": "sorgo de grão", "Feijão comum": "feijão",
  "Palma + gliricídia": "palma + gliricídia" };
const curto = (c) => CURTO[c] || String(c || "").toLowerCase();
const ESTADO = { preparo: "preparo sem fogo", risco: "pode plantar, com mais risco", plantar: "plantar", crescendo: "crescendo",
  colher: "colher", descanso: "descanso" };
const ESTADO_CURTO = { ...ESTADO, preparo: "preparo", risco: "plantar c/ risco" };
const PRIOR = { colheita: 6, plantio: 5, estimado: 5, roca: 4, risco: 3, preparo: 2, pousio: 1 };
const DE_BARRA = { colheita: "colher", plantio: "plantar", estimado: "plantar", roca: "crescendo", risco: "risco", preparo: "preparo", pousio: "descanso" };
const SUPOE_LAYOUT = "roçado quadrado com a área da resposta; Partes A, B e C do mesmo tamanho; bordas no perímetro sem tirar área " +
  "(como no estudo financeiro, 10_familia.py); faixas de pelo menos 10 m";

function pararTudo() {
  clearInterval(est.relogio); est.relogio = null;
  clearInterval(est.foco); est.foco = null;
}

/** Meses do calendário (agenda.inicio a agenda.fim). */
function listaMeses(a) {
  const out = [];
  if (!a) return out;
  for (let y = +a.inicio.slice(0, 4), m = +a.inicio.slice(5, 7); `${y}-${String(m).padStart(2, "0")}` <= a.fim.slice(0, 7); m = m % 12 + 1, y += m === 1 ? 1 : 0) {
    const mm = String(m).padStart(2, "0"), dias = new Date(y, m, 0).getDate();
    out.push({ ini: `${y}-${mm}-01`, fim: `${y}-${mm}-${dias}`, m, y, dias });
  }
  return out;
}

/** O que a parte está fazendo no mês, pelas barras da agenda (revez = a linha do caupi no milho em pé do baixio). */
function estadoMes(a, parte, mes, revez = false) {
  const linhas = a.linhas.filter((l) => l.parte === parte && /em pé/.test(l.cultura) === revez);
  let melhor = null;
  for (const l of linhas) for (const b of l.barras) {
    if (b.de <= mes.fim && b.ate >= mes.ini && (!melhor || PRIOR[b.tipo] > PRIOR[melhor.b.tipo])) melhor = { l, b };
  }
  if (melhor) return { estado: DE_BARRA[melhor.b.tipo], cultura: melhor.l.cultura, tipo: melhor.l.tipo, barra: melhor.b, linha: melhor.l };
  if (revez) {
    const l = linhas.find((x) => x.barras.length && x.barras[0].de <= mes.fim && x.barras[x.barras.length - 1].ate >= mes.ini);
    if (l) return { estado: "crescendo", cultura: l.cultura, tipo: l.tipo, linha: l };
    return null;
  }
  const colhida = linhas.flatMap((l) => l.barras.filter((b) => b.tipo === "colheita" && b.ate < mes.ini).map((b) => ({ l, b })))
    .sort((p, q) => (p.b.ate < q.b.ate ? 1 : -1))[0];
  return { estado: "descanso", cultura: colhida ? colhida.l.cultura : null, tipo: "pousio", palhada: !!colhida };
}

const haTxt = (U, v) => (v >= 10 ? U.num(v, 0) : v >= 1 ? U.num(v, 1).replace(/,0$/, "") : U.num(v, 2)) + " ha";
const botoesAno = (p) => `<div class="anos" role="group" aria-label="Ano do plano">${p.anos.map((ano, k) =>
  `<button type="button" class="ano-b" data-ano="${k}">${ano}</button>`).join("")}</div>`;

// ------------------------------------------------------------------ abertura (a ficha da casca mostra o tamanho e o "Mudar")
function abertura() {
  return `<div class="titulo-passo"><p class="kicker">Como plantar</p>
    <h1>Plante em faixas.<span class="eco">Cada ano, cada cultura muda de lugar.</span></h1></div>`;
}

/** A faixa "Agora: …" sob o título (agora() de plantio/calendario.js; a linha do tempo começa depois dela, sem repetir). */
function faixaAgora(ctx) {
  const U = ctx.util, t = agora(ctx);
  return t ? `<div class="plantio-agora">${U.faixa("semente", "verde", `<b>Agora:</b> ${U.esc(t)}`)}</div>` : "";
}

// ------------------------------------------------------------------ o roçado visto de cima (SVG em escala)
function linhasFaixa(x, y, w, h) {
  const n = Math.max(1, Math.floor((h - 6) / 9)), gap = (h - 6) / n;
  let s = `<g class="lin">`;
  for (let j = 0; j < n; j++) { const yy = (y + 3 + gap * (j + 0.5)).toFixed(1); s += `<line x1="${x + 4}" y1="${yy}" x2="${x + w - 4}" y2="${yy}"/>`; }
  return s + "</g>";
}

function svgRocado(U, lay, W) {
  const pad = 24, topo = 18, S = W - 2 * pad, s = S / lay.lado, x0 = pad, y0 = pad + topo;
  const H = y0 + S + pad + 16, fs = W < 420 ? 12 : 14, tx = x0 + 12 + fs + 8;
  const rotulos = (y, hh, i) => {
    const dois = hh >= fs * 2.6;
    const yr = dois ? y + hh / 2 - 2 : y + hh / 2 + fs * 0.36, yf = yr - fs * 0.95 - 3;
    return `<rect class="rot-fundo" x="${x0 + 6}" y="${yf.toFixed(1)}" width="0" height="${(fs * 1.35 + 6).toFixed(1)}" rx="7"
        data-h1="${(fs * 1.35 + 6).toFixed(1)}" data-h2="${(y + hh / 2 + fs - 1 + 6 - yf).toFixed(1)}" data-x="${tx - x0 - 6}"/>
      <g class="rot-ic" transform="translate(${x0 + 12},${(yr - fs * 0.95).toFixed(1)}) scale(${((fs + 2) / 24).toFixed(3)})"></g>
      <text class="rot" x="${tx}" y="${yr.toFixed(1)}" style="font-size:${fs}px"></text>
      <text class="rot2" x="${tx}" y="${(y + hh / 2 + fs - 1).toFixed(1)}" style="font-size:${fs - 2}px"${dois ? "" : ' display="none"'}></text>
      <text class="tag" x="${x0 + S - 10}" y="${yr.toFixed(1)}" text-anchor="end" style="font-size:${fs - 2}px" data-tag="${i}"></text>`;
  };
  let h = `<svg class="rocado-svg" viewBox="0 0 ${W} ${H.toFixed(0)}" role="img" aria-label="O roçado visto de cima, em escala">
    <g class="bordas t-perene" data-bordas>
      <rect class="b-fora" x="${x0 - 15}" y="${y0 - 15}" width="${S + 30}" height="${S + 30}" rx="8"/>
      <rect class="b-dentro" x="${x0 - 7}" y="${y0 - 7}" width="${S + 14}" height="${S + 14}" rx="4"/></g>`;
  lay.faixas.forEach((f, i) => {
    const y = y0 + f.y0 * s, hh = (f.y1 - f.y0) * s;
    h += `<g class="fx" data-fx="${i}"><rect class="chao" x="${x0}" y="${y.toFixed(1)}" width="${S}" height="${hh.toFixed(1)}"/>
      ${linhasFaixa(x0, y, S, hh)}${rotulos(y, hh, i)}</g>`;
  });
  if (lay.temBaixio) {
    const y = y0 + lay.profAlto * s, hh = S - lay.profAlto * s;
    h += `<g class="fx bx${lay.incerto ? " incerto" : ""}" data-bx data-y="${y.toFixed(1)}" data-h="${hh.toFixed(1)}" data-x="${x0}" data-w="${S}">
      <rect class="chao" x="${x0}" y="${y.toFixed(1)}" width="${S}" height="${hh.toFixed(1)}"/>
      <g class="lin" data-milho></g><g class="lin caupi t-leguminosa" data-caupi></g>${rotulos(y, hh, "bx")}</g>`;
  }
  // escala: barra de 5/10/20/25/50/100/200 m com pelo menos 50 unidades
  const L = [5, 10, 20, 25, 50, 100, 200, 500].find((m) => m * s >= 50) || 500;
  const yb = y0 + S + 32;
  h += `<text class="eixo" x="${x0 - 15}" y="${y0 - 24}">alto</text>
    <text class="eixo" x="${x0 + S + 15}" y="${y0 - 24}" text-anchor="end">a água desce ↓</text>
    <line class="escala" x1="${x0}" y1="${yb}" x2="${x0 + L * s}" y2="${yb}"/>
    <text class="eixo" x="${x0 + L * s + 8}" y="${yb + 4}">${L} m</text>
    <text class="eixo" x="${x0 + S}" y="${yb + 4}" text-anchor="end">lado ≈ ${U.num(lay.lado, 0)} m</text></svg>`;
  return h;
}

/** Fundo atrás dos rótulos de cada faixa (as linhas de plantio não cortam o texto). Mede o texto quando a página já está na tela. */
function fundosRotulos(raiz) {
  raiz.querySelectorAll(".rocado-svg .fx").forEach((g) => {
    const f = g.querySelector(".rot-fundo");
    if (!f) return;
    const r1 = g.querySelector(".rot"), r2 = g.querySelector(".rot2");
    const usa2 = r2.textContent && r2.getAttribute("display") !== "none";
    let w = 0;
    for (const t of usa2 ? [r1, r2] : [r1]) {
      let l = 0;
      try { l = t.getComputedTextLength(); } catch (_) { /* fora da tela: estima */ }
      w = Math.max(w, l || t.textContent.length * parseFloat(t.style.fontSize) * 0.56);
    }
    f.setAttribute("width", r1.textContent ? (w + +f.dataset.x + 12).toFixed(1) : "0");
    f.setAttribute("height", usa2 ? f.dataset.h2 : f.dataset.h1);
  });
}

function linhasBaixio(g, k, mostrarCaupi) {
  const x = +g.dataset.x, y = +g.dataset.y, w = +g.dataset.w, h = +g.dataset.h;
  const n = Math.max(2, Math.floor((h - 6) / 9)), gap = (h - 6) / n;
  let milho = "", caupi = "";
  for (let j = 0; j < n; j++) {
    const yy = (y + 3 + gap * (j + 0.5)).toFixed(1), ln = `<line x1="${x + 4}" y1="${yy}" x2="${x + w - 4}" y2="${yy}"/>`;
    if ((j + k) % 2 === 0) milho += ln; else caupi += ln; // as linhas trocam de lugar a cada ano (motor: revezamento)
  }
  g.querySelector("[data-milho]").innerHTML = milho;
  g.querySelector("[data-caupi]").innerHTML = mostrarCaupi ? caupi : "";
}

function heroi(ctx, lay, meses, W) {
  const U = ctx.util, p = ctx.r.plano, a = ctx.r.agenda;
  const chips = meses.map((mes, i) => `<button type="button" class="mes-b" data-mes="${i}" title="${U.MESES[mes.m - 1]}/${mes.y}">
      ${U.MESES[mes.m - 1]}${mes.m === 1 || i === 0 ? `<small>${String(mes.y).slice(2)}</small>` : ""}</button>`).join("");
  const amostra = (e) => `<svg class="amostra" viewBox="0 0 30 16" aria-hidden="true"><g class="fx t-leguminosa e-${e}"><rect class="chao" x="1" y="1" width="28" height="14"/>
    <g class="lin e-${e}"><line x1="4" y1="5.5" x2="26" y2="5.5"/><line x1="4" y1="10.5" x2="26" y2="10.5"/></g></g></svg>`;
  const ordem = `<p>${fraseOrdem(U, lay)}</p>
    <p>O desenho é uma suposição ${U.selo("suposicao", SUPOE_LAYOUT)}: roçado quadrado de ${haTxt(U, lay.ha)} (lado ≈ ${U.num(lay.lado, 0)} m),
    ${lay.nFaixas} faixas em nível de ≈ ${U.num(lay.larguraFaixa, 0)} m e ${haTxt(U, lay.faixas[0].ha)} cada (Partes A, B e C do mesmo tamanho;
    faixa de pelo menos 10 m, senão 3 faixas)${lay.temBaixio ? `, baixio de ${haTxt(U, lay.haBaixio)}${lay.incerto ? ` (você respondeu "não sei": desenhamos ⅓)` : ""}` : ""}.
    As bordas ficam no perímetro e não tiram área, como no estudo financeiro. As linhas de plantio são ilustrativas: o espaçamento, o tamanho
    de cada faixa e o solo do baixio se confirmam com o técnico.</p>
    <p>No mês a mês, cada faixa mostra o que o calendário manda fazer: plantar e "pode plantar, com mais risco" vêm das janelas do ZARC
    ${U.selo("medido", "ZARC 2026/27 e portarias plurianuais do MAPA")}; crescendo e colher vêm da janela mais o ciclo da cultura
    ${U.selo("suposicao", "ciclos da cultura; alguns sem fonte")}. O calendário só vai até dez/2027: 2028 e 2029 aparecem só por ano
    ${U.selo("projecao", "a rotação segue; as datas repetem o ZARC 2026/27")}.</p>`;
  const legenda = `<p class="vista" data-vista></p>
    <ul class="leg-partes" data-lista></ul>
    <div class="leg-estados" data-legenda-mes hidden>${Object.keys(ESTADO).map((e) => `<span>${amostra(e)}${ESTADO[e]}</span>`).join("")}</div>`;
  const cerca = `<p class="leg-extra"><svg class="amostra" viewBox="0 0 30 16" aria-hidden="true"><g class="bordas t-perene"><line class="b-fora" x1="2" y1="4" x2="28" y2="4"/>
    <line class="b-dentro" x1="2" y1="12" x2="28" y2="12"/></g></svg>Cerca viva: palma e gliricídia</p>`;
  const mesCtl = a ? `<div class="mes-controle">
      <button type="button" class="play" data-play aria-label="Passar os meses">${U.ic("tocar")}</button>
      <div class="mes-trilho" role="group" aria-label="Mês a mês em 2027">${chips}</div></div>` : "";
  const anos = `${p.anos[0]}–${p.anos[p.anos.length - 1]}`;
  const rotHtml = `${olho(OLHOS.faixas)}<h4>Por que esta ordem das faixas</h4>${ordem}<h4>Parte por parte</h4>${rotacao(ctx, lay)}`;
  const topo = `<div class="bloco-topo"><h3>Seu roçado visto de cima <span data-selo-heroi></span></h3>${botoesAno(p)}</div>`;
  // no celular o desenho já traz o nome de cada faixa: o mês a mês, a lista das partes e a rotação ficam num "ver mais" só
  // (aberto quando o mês a mês está ligado, para o redesenho não esconder o controle)
  if (est.compacto) {
    return `<section class="painel heroi" id="plantio-rocado">${topo}
      <figure class="rocado-fig">${svgRocado(U, lay, W)}</figure>${cerca}
      <details class="ver-mais mes-a-mes"${est.modo === "mes" ? " open" : ""}><summary>${a ? `Ver mês a mês e a rotação ${anos}` : `Ver as partes e a rotação ${anos}`}</summary>
        ${mesCtl}${legenda}${U.verMais(rotHtml, `A rotação ${anos}, parte por parte`)}</details></section>`;
  }
  const rot = U.verMais(rotHtml, `Ver a rotação ${anos}, parte por parte`);
  return `<section class="painel heroi" id="plantio-rocado">${topo}
    <div class="heroi-grade">
      <figure class="rocado-fig">${svgRocado(U, lay, W)}</figure>
      <div class="heroi-lado">${legenda}${cerca}</div>
    </div>
    ${mesCtl}
    ${rot}
  </section>`;
}

function fraseOrdem(U, lay) {
  const seq = lay.faixas.map((f) => f.letra).join(" ");
  const sel = U.selo("suposicao", "contado sobre o desenho (faixas iguais em nível): faixas vizinhas e a faixa que encosta no baixio, nos 3 anos do plano");
  let s = `De cima para baixo: <b>${seq}</b>${lay.temBaixio ? " e, embaixo, o baixio" : ""}. `;
  if (lay.contatos === 0) {
    s += `Das 6 ordens possíveis, escolhemos uma em que nenhuma gramínea (milho, sorgo, milheto) encosta em outra gramínea nos 3 anos ${sel}`;
    const ult = lay.encostaBaixio;
    if (lay.temBaixio) s += ult.anos.every((c) => !ehGram(c.cultura))
      ? `: a ${U.esc(ult.parte)}, que aqui nunca tem gramínea, fica encostada no milho do baixio.` : ", nem no milho do baixio.";
    else s += ".";
  } else if (lay.todasIguais) {
    s += `Aqui nenhuma ordem evita que gramínea encoste em gramínea: em qualquer uma das 6 ordens são ${lay.contatos} encontros em 3 anos ${sel}.`;
  } else {
    s += `Das 6 ordens possíveis, esta tem menos encontros de gramínea com gramínea nos 3 anos: ${lay.contatos}, contra ${lay.piorContatos} na pior ${sel}.`;
  }
  return s;
}

function pintarRocado(el, ctx, lay, meses) {
  const U = ctx.util, esc = U.esc, a = ctx.r.agenda, p = ctx.r.plano;
  const mes = est.modo === "mes" ? meses[est.mes] : null, k = mes ? 0 : est.ano;
  const caixa = el.querySelector("#plantio-rocado");
  caixa.querySelectorAll("[data-ano]").forEach((b) => b.setAttribute("aria-pressed", String(!mes && +b.dataset.ano === k)));
  caixa.querySelectorAll("[data-mes]").forEach((b) => { b.classList.toggle("atual", !!mes && +b.dataset.mes === est.mes); b.classList.toggle("fora", est.ano !== 0 && !mes); });
  caixa.querySelector("[data-selo-heroi]").innerHTML = mes
    ? U.selo("suposicao", "desenho = suposição; datas de plantar do ZARC 2026/27 (medidas); crescendo e colher = janela + ciclo da cultura")
    : k === 0 ? U.selo("suposicao", SUPOE_LAYOUT + "; culturas do plano para 2027")
      : U.selo("projecao", `${p.anos[k]}: a rotação segue o plano; desenho = suposição`);
  caixa.querySelector("[data-vista]").textContent = mes ? `${U.MESES[mes.m - 1]}/${mes.y} · mês a mês` : `${p.anos[k]} · o ano todo`;
  caixa.querySelector("[data-legenda-mes]").hidden = !mes;
  let temReserva = false;
  lay.faixas.forEach((f, i) => {
    const g = caixa.querySelector(`[data-fx="${i}"]`);
    let tipo, estado = "ano", rot, rot2 = "", tag = "", icone;
    if (mes) {
      const e = estadoMes(a, f.parte, mes);
      tipo = e.tipo; estado = e.estado;
      icone = e.estado === "preparo" ? "enxada" : e.estado === "descanso" ? "" : U.icCultura(e.cultura);
      rot = `${f.letra} · ${e.estado === "descanso" ? (e.palhada ? `palhada do ${curto(e.cultura)}` : "descanso") : `${curto(e.cultura)} · ${(est.compacto ? ESTADO_CURTO : ESTADO)[e.estado]}`}`;
    } else {
      const c = f.plano.anos[k];
      tipo = c.tipo;
      icone = U.icCultura(c.cultura);
      rot = `${f.letra} · ${curto(c.cultura)} · ${haTxt(U, f.ha)}`;
      if (k > 0) {
        const antes = f.plano.anos[k - 1].cultura;
        if (antes === c.cultura && c.cultura === "Mandioca") { tag = "reserva"; temReserva = true; }
        const de = antes === c.cultura ? null : lay.partes.find((q) => q.anos[k - 1].cultura === c.cultura);
        rot2 = `antes: ${curto(antes)}${de && !est.compacto ? ` · ${curto(c.cultura)} vem da ${de.parte.replace("Parte ", "")}` : ""}`;
      }
    }
    g.setAttribute("class", `fx ${U.tipoCss(tipo)} e-${estado}`);
    g.querySelector(".lin").setAttribute("class", `lin e-${estado}`);
    g.querySelector(".rot-ic").innerHTML = icone ? U.IC[icone] : "";
    g.querySelector(".rot").textContent = rot;
    g.querySelector(".rot2").textContent = rot2;
    g.querySelector(".tag").textContent = tag;
  });
  // legenda compacta: uma linha por parte (ícone, nome, área ou o que fazer no mês)
  const itens = [];
  for (const q of p.faixas) {
    if (q.parte === "Baixio" && !lay.temBaixio) continue;
    const L = /^Parte/.test(q.parte) ? q.parte.replace("Parte ", "") : "";
    let cultura, tipo, direita, extra = q.parte === "Baixio" ? `<span class="leg-sub">no baixio${lay.incerto ? ", se tiver (tracejado)" : ""}</span>` : "";
    if (mes) {
      const e = estadoMes(a, q.parte, mes);
      cultura = e.estado === "descanso" ? (e.palhada ? `palhada do ${curto(e.cultura)}` : "descanso") : e.cultura;
      tipo = e.tipo;
      direita = "";
      if (e.estado !== "descanso") extra += `<span class="leg-sub leg-faz">${ESTADO[e.estado]}${e.barra && e.estado !== "crescendo" ? ` · ${U.dataBR(e.barra.de, true)} a ${U.dataBR(e.barra.ate, true)}` : ""}</span>`;
      if (q.parte === "Baixio") { const rz = estadoMes(a, "Baixio", mes, true); if (rz) extra += `<span class="leg-sub">caupi no meio do milho: ${ESTADO[rz.estado]}</span>`; }
      if (q.parte === "Bordas") extra += `<span class="leg-sub">na cerca</span>`;
      if (e.linha && e.linha.estacao > 2027) extra += `<span class="leg-sub">já é a safra ${e.linha.estacao}</span>`;
    } else {
      const c = q.anos[k];
      cultura = q.parte === "Baixio" ? `${c.cultura} + caupi` : c.cultura;
      tipo = c.tipo;
      direita = /^Parte/.test(q.parte) ? haTxt(U, lay.haParte) : q.parte === "Baixio" ? haTxt(U, lay.haBaixio) + (lay.incerto ? "?" : "") : "na cerca";
      if (k > 0 && q.anos[k - 1].cultura === c.cultura && c.cultura === "Mandioca") extra += `<span class="chip terra mini-chip">reserva</span>`;
    }
    itens.push(`<li class="${U.tipoCss(tipo)}"><span class="leg-ic">${U.ic(U.icCultura(cultura))}</span><span class="leg-l">${esc(L)}</span>
      <span class="leg-t"><b>${esc(cultura)}</b>${extra}</span><span class="leg-a">${esc(direita)}</span></li>`);
  }
  caixa.querySelector("[data-lista]").innerHTML = itens.join("") + (temReserva && !mes
    ? `<li class="leg-nota">Reserva: a mandioca do ano anterior ainda está no chão.</li>` : "");
  // baixio
  const gb = caixa.querySelector("[data-bx]");
  if (gb) {
    let tipo = lay.bx.anos[k].tipo, estado = "ano", rot, rot2, caupi = true;
    if (mes) {
      const e = estadoMes(a, "Baixio", mes), rz = estadoMes(a, "Baixio", mes, true);
      tipo = e.tipo; estado = e.estado; caupi = !!rz;
      rot = `Baixio · ${e.estado === "descanso" ? (e.palhada ? `palhada do ${curto(e.cultura)}` : "descanso") : `${curto(e.cultura)} · ${ESTADO[e.estado]}`}`;
      rot2 = rz ? `caupi no meio do milho: ${ESTADO[rz.estado]}` : "";
      gb.querySelector("[data-milho]").setAttribute("class", `lin e-${estado}`);
      gb.querySelector("[data-caupi]").setAttribute("class", `lin caupi t-leguminosa e-${rz ? rz.estado : "ano"}`);
      gb.querySelector(".rot-ic").innerHTML = e.estado === "descanso" ? "" : U.IC[e.estado === "preparo" ? "enxada" : U.icCultura(e.cultura)];
    } else {
      rot = `Baixio${lay.incerto ? "?" : ""} · ${curto(lay.bx.anos[k].cultura)} + caupi · ${haTxt(U, lay.haBaixio)}`;
      rot2 = lay.incerto ? "se você tiver baixio" : "linhas de milho e de caupi alternadas";
      gb.querySelector("[data-milho]").setAttribute("class", "lin e-ano");
      gb.querySelector("[data-caupi]").setAttribute("class", "lin caupi t-leguminosa e-ano");
      gb.querySelector(".rot-ic").innerHTML = U.IC[U.icCultura(lay.bx.anos[k].cultura)];
    }
    gb.setAttribute("class", `fx bx ${U.tipoCss(tipo)} e-${estado}${lay.incerto ? " incerto" : ""}`);
    linhasBaixio(gb, k, caupi);
    gb.querySelector(".rot").textContent = rot;
    gb.querySelector(".rot2").textContent = rot2;
  }
  fundosRotulos(caixa);
  const gbord = caixa.querySelector("[data-bordas]");
  if (gbord) {
    const e = mes ? estadoMes(a, "Bordas", mes) : null;
    gbord.setAttribute("class", `bordas t-perene e-${e ? e.estado : "ano"}`);
  }
}

// ------------------------------------------------------------------ a maniva (sob o desenho): muda o plano no núcleo
function linhaManiva(ctx) {
  const U = ctx.util, p = ctx.r.plano;
  if (ctx.ef.maniva === "nao") {
    return `<div class="plantio-maniva" id="plantio-maniva"><p>${U.ic("mandioca")}<span>Sem maniva: a mandioca saiu do plano.</span></p>
      <div class="maniva-chips"><button type="button" class="chip" data-maniva="">${U.ic("volta")} voltar</button></div></div>`;
  }
  const temM = (f) => f.anos.some((c) => c.cultura === "Mandioca");
  const f = p.faixas.find((x) => /^Parte/.test(x.parte) && x.anos[0].cultura === "Mandioca") || p.faixas.find(temM);
  if (!f) return "";
  const atual = ctx.resp.maniva === "plantada" ? "plantada" : "";
  const ops = [["", "Consigo maniva"], ["plantada", "Já tenho no chão"], ["nao", "Não consigo"]];
  return `<div class="plantio-maniva" id="plantio-maniva"><p>${U.ic("mandioca")}<span><b>Mandioca</b> (${U.esc(f.parte)}): tem maniva?</span></p>
    <div class="maniva-chips" role="group" aria-label="Maniva para a mandioca">${ops.map(([v, t]) => `<button type="button"
      class="chip${atual === v ? " verde" : ""}" data-maniva="${v}" aria-pressed="${atual === v}">${atual === v ? U.ic("ok") : ""}${t}</button>`).join("")}</div></div>`;
}

// ------------------------------------------------------------------ o que fazer e quando
const TERRA_ROT = { nao_sei: "não sei", arenosa: "de areia", mista: "misturada", barro: "de barro" };
const HOJE_ZARC = { milho: "Milho", feijao: "Feijão comum", mandioca: "Mandioca" }; // o jeito de hoje no cardápio do ZARC
const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
const artigo = (c) => (/^(mandioca|palma|mamona|mucuna|gliric)/.test(norm(c)) ? "a" : "o");

/** Terra "não sei": as datas são as que servem nos solos zoneados. Para cada cultura do plano (e do jeito de hoje) sem janela na areia
 *  (cardapio[].por_solo sem o solo 1 ou o AD2, cód. 12), uma linha honesta. Ex.: feijão comum em Quixadá; milho em Piritiba. */
function avisoTerra(ctx) {
  if (ctx.ef.terra !== "nao_sei") return "";
  const U = ctx.util, card = ctx.r.cardapio || [], nomes = new Set();
  for (const f of ctx.r.plano?.faixas || []) for (const c of f.anos) for (const n of String(c.cultura).split(/\s*\+\s*/)) nomes.add(norm(n));
  for (const k of Object.keys(lerHoje(ctx.resp.hoje || "", ctx.r.padroes).cult)) if (HOJE_ZARC[k]) nomes.add(norm(HOJE_ZARC[k]));
  const temAreia = (c) => c.por_solo.some((s) => [1, 12].includes(+s.cod_solo) && [s.risco20, s.risco30, s.risco40].some((x) => x && x !== "nenhum"));
  const sem = card.filter((c) => Array.isArray(c.por_solo) && c.por_solo.length && !temAreia(c)
    && [...nomes].some((n) => norm(c.cultura) === n || norm(c.cultura).startsWith(n + " ")));
  // sem a sigla na frente (o ZARC fica no selo do bloco) e com o que fazer
  return sem.length ? `<ul class="aviso-terra">${sem.map((c) => `<li>${U.ic("areia")}<span>Em terra de areia, ${artigo(c.cultura)} ${U.esc(c.cultura.toLowerCase())}
    não tem data segura aqui: pergunte ao técnico.</span></li>`).join("")}</ul>` : "";
}

const temMetade = (ctx) => !!ctx.r.agenda && /metade/i.test(ctx.r.plano?.interruptor || ""); // o "seu olho" da metade guardada

function blocoTempo(ctx) {
  const U = ctx.util;
  if (!ctx.r.agenda) return "";
  return `<section class="painel" id="plantio-tempo">
    <h3>O que fazer e quando ${U.selo("medido", "datas de plantar da tábua oficial (ZARC 2026/27); os cartões marcados como suposição são estimados")}</h3>
    <a class="chip terra-chip" href="${ctx.link(2)}" data-editar="terra">${U.ic(ctx.ef.terra === "barro" ? "barro" : "areia")}<span>Sua terra:
      ${TERRA_ROT[ctx.ef.terra] || "não sei"} · <u>mudar</u></span></a>
    ${avisoTerra(ctx)}
    ${linhaDoTempo(ctx)}
    <p class="sequeiro">${U.ic("chuva")}<span>Datas para roça de chuva. Molha a roça? Fale com o técnico.</span></p>
    ${temMetade(ctx) ? olho(OLHOS.metade) : ""}
    ${U.verMais(calendarioCompleto(ctx), "Ver o calendário completo")}
  </section>`;
}

// ------------------------------------------------------------------ por que faixas e não blocos (ideia do Vicente)
function blocoFaixas(ctx, lay) {
  const U = ctx.util, p = ctx.r.plano;
  const fig = (modo, titulo, sub) => `<figure class="mini"><figcaption><b>${titulo}</b> <span>${sub}</span></figcaption>
    <div class="mini-svg" data-mini-svg="${modo}"></div><div class="veredito" data-veredito="${modo}"></div></figure>`;
  const detalhe = `<div data-regua></div>
    <p><b>O limite.</b> As faixas ajudam contra o que anda pelo chão e pela água: fungo e nematoide de raiz, a <i>Phytophthora</i>. Não seguram
    praga que voa longe: a mariposa da lagarta-do-cartucho e o bicudo voam quilômetros. Contra essas, vale a troca de cultura de um ano para o
    outro e o calendário combinado com os vizinhos.</p>
    <div data-tabela-conect></div>
    <ul class="tec">
      <li>O roçado vira uma grade de células de cerca de 5 m (as linhas seguem as divisas das faixas e do baixio; as colunas, os terços). Cada
      célula recebe a cultura do ano. Duas células de gramínea (milho, sorgo, milheto) estão no mesmo bloco se encostam de lado (4 vizinhos;
      union-find). "Desce até o baixio" = algum bloco liga a linha do alto à linha mais baixa. São as definições do estudo de percolação da
      paisagem do José (p, S, "atravessa"), aplicadas dentro do roçado.</li>
      <li>"Em blocos" = as Partes A, B e C lado a lado, cada uma do alto até o baixio. "Em faixas" = a ordem do desenho. As bordas ficam fora da conta.</li>
      <li>A praga que anda no desenho é uma ilustração determinística: começa na primeira célula de gramínea do alto e passa só para a vizinha de
      gramínea. Não prevê perda.</li>
      <li>Referências: Alonso-Tlali et al. 2025, <i>Entropy</i> 27(4):386 (limiar 0,5927; faixas alternadas e xadrez); Ramírez et al. 2018,
      <i>Phys. Rev. E</i> 98:062409 (linhas alternadas); Ramírez et al. 2020, <i>Phys. Rev. E</i> 101:032301 (zoósporos de <i>Phytophthora</i> na
      água do solo).</li>
      <li>O simulador do Vicente calcula outros números (R<sub>eff</sub>, plantas protegidas) com constantes que ainda não têm fonte nos artigos
      da pasta dele (grau D). Eles ficam no simulador, fora do plano, até a calibração.</li>
    </ul>`;
  return `<div class="faixas-bloco" id="plantio-faixas">
    <p class="faixas-frase">Doença de chão e de água passa de planta em planta da mesma família.
      ${U.selo("suposicao", "calculado no navegador sobre o desenho (" + SUPOE_LAYOUT + "); grade de ~5 m, 4 vizinhos")}</p>
    <div class="bloco-topo">${botoesAno(p)}</div>
    <div class="mini-par">${fig("blocos", "Em blocos", "como se faz hoje")}${fig("faixas", "Em faixas", "este plano")}</div>
    <div class="mini-leg"><span><i class="q g1"></i>milho e sorgo</span><span><i class="q g0"></i>outras plantas</span><span><i class="q g2"></i>onde a praga chegou</span></div>
    <div class="foco-linha"><button type="button" class="botao secundario" data-foco>${U.ic("seta")} Ver a praga andar</button>
      <span class="pequeno sub">desenho do mecanismo, não previsão</span></div>
    <div data-aviso-gram></div>
    <p class="rodape-faixas">Não segura praga que voa longe, como a lagarta-do-cartucho. Ideia de Vicente Lima (PercolaCampo) ·
      <a href="modulos/percolacampo/index.html" target="_blank" rel="noopener">simulador do Vicente (modelo teórico)</a></p>
    ${olho(OLHOS.vizinhos)}
    ${U.verMais(detalhe)}
  </div>`;
}

// ------------------------------------------------------------------ por que este plano: 3 "ver mais" com a manchete no título
function porQue(ctx, lay) {
  const U = ctx.util;
  return `<section class="painel plantio-porque" id="plantio-porque"><h3>Por que este plano</h3>
    ${U.verMais(U.extra("vulnerabilidade", { vista: "agua", painel: false }), "Onde o seu roçado sofre mais")}
    ${U.verMais(blocoFaixas(ctx, lay), "Por que em faixas: a praga anda menos")}
    ${U.verMais(U.extra("saude_solo", { titulo: false }), "O que cada planta faz pelo solo")}
  </section>`;
}

function svgMini(U, lay, gr, alcance) {
  const { linhas, nc, largCol, gram } = gr;
  const t = (v) => v.toFixed(2);
  let h = `<svg viewBox="0 0 ${t(lay.lado)} ${t(lay.lado)}" class="mini-grade" role="img" aria-label="Grade do roçado">`;
  linhas.forEach((ln, r) => {
    let c0 = 0;
    const est_ = (c) => (gram[r * nc + c] ? (alcance && alcance.dist[r * nc + c] >= 0 && alcance.dist[r * nc + c] <= alcance.t ? 2 : 1) : 0);
    while (c0 < nc) {
      const e = est_(c0);
      let c1 = c0 + 1;
      while (c1 < nc && est_(c1) === e) c1++;
      h += `<rect class="g${e}" x="${t(c0 * largCol)}" y="${t(ln.y0)}" width="${t((c1 - c0) * largCol + 0.05)}" height="${t(ln.y1 - ln.y0 + 0.05)}"/>`;
      c0 = c1;
    }
  });
  const sw = t(lay.lado / 110);
  if (gr.modo === "faixas") lay.faixas.slice(1).forEach((f) => { h += `<line class="divisa" x1="0" y1="${t(f.y0)}" x2="${t(lay.lado)}" y2="${t(f.y0)}" stroke-width="${sw}"/>`; });
  else for (let j = 1; j < lay.partes.length; j++) { const x = t(lay.lado * j / lay.partes.length); h += `<line class="divisa" x1="${x}" y1="0" x2="${x}" y2="${t(lay.profAlto)}" stroke-width="${sw}"/>`; }
  if (lay.temBaixio) h += `<line class="divisa bx" x1="0" y1="${t(lay.profAlto)}" x2="${t(lay.lado)}" y2="${t(lay.profAlto)}" stroke-width="${t(lay.lado / 70)}"/>`;
  return h + "</svg>";
}

/** O veredito grande de cada desenho: quantos pedaços de milho e sorgo e se a praga atravessa do alto ao baixo. */
function veredito(U, lay, g) {
  if (g.p === 0) return `<span class="chip">${U.ic("ok")} sem milho nem sorgo</span>`;
  if (g.desce) return `<span class="chip terra">${U.ic("alerta")} ${g.blocos === 1 ? "1 bloco só: a praga atravessa" : "a praga desce até embaixo"}</span>`;
  if (g.blocos > 1) return `<span class="chip verde">${U.ic("escudo")} ${g.blocos} pedaços: a praga para</span>`;
  if (lay.temBaixio && Math.abs(g.maior - lay.frac) < 1e-6) return `<span class="chip">${U.ic("ok")} só o milho do baixio</span>`;
  return `<span class="chip ambar">${U.ic("alerta")} 1 bloco grande: não desce, mas é grande</span>`;
}

function pintarFaixas(el, ctx, lay, conect) {
  const U = ctx.util, p = ctx.r.plano;
  const k = est.modo === "mes" ? 0 : est.ano;
  clearInterval(est.foco); est.foco = null;
  const caixa = el.querySelector("#plantio-faixas");
  caixa.querySelectorAll("[data-ano]").forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.ano === k)));
  const baixo = lay.temBaixio ? "até o baixio" : "até a parte mais baixa";
  for (const modo of ["blocos", "faixas"]) {
    const g = conect[k][modo];
    caixa.querySelector(`[data-mini-svg="${modo}"]`).innerHTML = svgMini(U, lay, g, null);
    caixa.querySelector(`[data-veredito="${modo}"]`).innerHTML = veredito(U, lay, g);
  }
  const f = conect[k].faixas;
  caixa.querySelector("[data-foco]").disabled = conect[k].blocos.p === 0;
  caixa.querySelector("[data-regua]").innerHTML = f.p === 0 ? "" : `<p><b>Régua.</b> Numa mistura ao acaso em malha quadrada, acima de
    ${U.num(LIMIAR_SITIO * 100, 1)}% de plantas da mesma família os pedaços tendem a se ligar de ponta a ponta (limiar de percolação 0,593
    ${U.selo("medido", "valor publicado: limiar de percolação de sítio, malha quadrada, 4 vizinhos (Alonso-Tlali et al. 2025, Entropy 27:386)")}).
    Em ${p.anos[k]}, a gramínea ocupa ${U.pct(f.p)} do roçado: ${f.p > LIMIAR_SITIO ? "acima da régua" : "abaixo da régua"}. É só referência: o roçado
    não é mistura ao acaso, por isso contamos os blocos no desenho.</p>`;
  caixa.querySelector("[data-tabela-conect]").innerHTML = `<table class="tab-conect"><tr><th>Ano</th><th>Desenho</th><th>p (gramínea)</th><th>Blocos</th>
    <th>Maior bloco</th><th>Desce ${baixo}?</th></tr>${p.anos.map((ano, j) => ["blocos", "faixas"].map((m) => {
    const g = conect[j][m];
    return `<tr><td>${ano}</td><td>${m === "blocos" ? "em blocos" : "em faixas"}</td><td>${U.num(g.p, 3)}</td><td>${g.blocos}</td><td>${U.num(g.maior, 3)}
      (S = ${U.num(g.S, 2)})</td><td>${g.p === 0 ? "—" : g.desce ? "sim" : "não"}</td></tr>`;
  }).join("")).join("")}</table><p class="pequeno">S = parte da gramínea que está no maior bloco. Números calculados sobre o desenho (suposição).</p>`;
}

/** Aviso quando a gramínea passa da régua ou repete no mesmo lugar (ex.: Arapiraca, sem mandioca apta). Frente curta; detalhe no ver mais. */
function avisoGramineas(ctx, lay, conect) {
  const U = ctx.util, p = ctx.r.plano;
  const acima = p.anos.filter((_, j) => conect[j].faixas.p > LIMIAR_SITIO);
  const pontes = [];
  for (const q of lay.partes) for (let j = 0; j + 1 < p.anos.length; j++)
    if (ehGram(q.anos[j].cultura) && ehGram(q.anos[j + 1].cultura)) pontes.push(`${q.parte} (${p.anos[j]}→${p.anos[j + 1]})`);
  if (!acima.length && !pontes.length) return "";
  const pMax = Math.max(...p.anos.map((_, j) => conect[j].faixas.p));
  const frase = acima.length ? `Aqui milho e sorgo ficam com ${U.emDez(pMax)} partes do roçado.` : "Aqui o sorgo repete no mesmo lugar dois anos seguidos.";
  return `<div class="aviso-gram">${U.faixa("alerta", "terra", frase)}
    <p class="pequeno">Fale com o técnico: trocar um sorgo por feijão, palma ou descanso.${pontes.length ? ` Repete em: ${pontes.join("; ")}.` : ""}
    ${U.selo("suposicao", "calculado sobre o desenho")}</p></div>`;
}

function animarFoco(el, ctx, lay, conect) {
  const U = ctx.util, k = est.modo === "mes" ? 0 : est.ano;
  clearInterval(est.foco);
  const caixa = el.querySelector("#plantio-faixas");
  const al = { blocos: espalhar(conect[k].blocos), faixas: espalhar(conect[k].faixas) };
  const max = Math.max(al.blocos.max, al.faixas.max), passo = Math.max(1, Math.ceil(max / 30));
  let t = 0;
  const quadro = () => {
    if (!caixa.isConnected) { clearInterval(est.foco); est.foco = null; return; }
    for (const modo of ["blocos", "faixas"]) {
      caixa.querySelector(`[data-mini-svg="${modo}"]`).innerHTML = svgMini(U, lay, conect[k][modo], { dist: al[modo].dist, t });
    }
    if (t >= max) { clearInterval(est.foco); est.foco = null; }
    t += passo;
  };
  quadro();
  est.foco = setInterval(quadro, 90);
}

// ------------------------------------------------------------------ a rotação 2027–2029 (vai no "ver mais" do roçado)
function rotacao(ctx, lay) {
  const U = ctx.util, esc = U.esc, p = ctx.r.plano;
  const area = (f) => (/^Parte/.test(f.parte) ? `${haTxt(U, lay.haParte)} ${U.selo("suposicao", SUPOE_LAYOUT)}`
    : f.parte === "Baixio" ? `${haTxt(U, lay.haBaixio)}${lay.incerto ? " (se tiver)" : ""} ${U.selo("suposicao", "fração do baixio da sua resposta; \"não sei\" = 1/3")}`
      : f.parte === "Bordas" ? "no perímetro: palma por dentro, gliricídia por fora" : "");
  const seloAno = (a, k) => `${a} ${k === 0 ? U.selo("medido", "janelas do ZARC 2026/27 nos textos de cada cultura")
    : U.selo("projecao", "a rotação segue; as datas repetem o ZARC 2026/27")}`;
  const cel = (c) => `<div class="rot-cel ${U.tipoCss(c.tipo)}"><b>${esc(c.cultura)}</b><span>${esc(c.texto)}${/estimad/.test(c.texto)
    ? " " + U.selo("suposicao", "janela estimada pelo início típico da chuva (IMERG); sem ZARC aqui") : ""}</span></div>`;
  let h = `<p>Cada parte recebe uma cultura por ano e, no ano seguinte, a cultura muda de parte. A leguminosa deixa nitrogênio para o cereal que
    vem depois, e fica mandioca no chão como reserva para um ano ruim (onde a mandioca cabe).</p>
    ${p.modelo_ne ? `<p class="aviso">Fora do Nordeste usamos o modelo do sertão: as culturas são do lugar, mas as datas, as bordas e o alerta do ano foram calibrados no NE.</p>` : ""}
    <div class="tab-rot-caixa"><table class="tab-rot"><tr><th>Parte do roçado</th>${p.anos.map((a, k) => `<th>${seloAno(a, k)}</th>`).join("")}</tr>`;
  for (const f of p.faixas) {
    if (f.parte === "Baixio" && !lay.temBaixio) continue;
    h += `<tr><td><b>${esc(f.parte)}</b><br><span class="pequeno">${area(f)}</span></td>${f.anos.map((c, k) => `<td><span class="ano-rot">${seloAno(p.anos[k], k)}</span>${cel(c)}</td>`).join("")}</tr>
      <tr class="porque"><td colspan="${p.anos.length + 1}">Por quê: ${esc(f.por_que)}</td></tr>`;
  }
  h += `</table></div>`;
  if (p.interruptor) h += `<p class="aviso"><b>Interruptor do ano:</b> ${esc(p.interruptor)}</p>`;
  h += `<h4>As regras da rotação e a evidência de cada uma</h4>
    ${(p.principios || []).map((c) => `<div class="ev"><div class="ev-regra">${esc(c.regra || c.configuracao)}${c.irrigado ? " (irrigado)" : ""}</div>
      <div class="pequeno">${c.efeito ? `<b>${esc(c.efeito)}</b> · ` : ""}grau ${esc(c.grau)}·${esc(c.transferencia)} ${esc(c.rotulo_transferencia)} · ${esc(c.referencia)}${c.lugar ? " · " + esc(c.lugar) : ""}${c.doi ? ` · <a href="https://doi.org/${esc(c.doi)}" target="_blank" rel="noopener">doi</a>` : ""}</div></div>`).join("")}
    <h4>Notas</h4><ul class="notas">${(p.notas || []).map((n) => `<li>${esc(n)}</li>`).join("")}</ul>`;
  return h;
}

// ------------------------------------------------------------------ passo
export default {
  id: "plantio",
  titulo: "Como plantar",
  async render(el, ctx) {
    pararTudo();
    const U = ctx.util, r = ctx.r;
    if (est.cod !== ctx.cod) Object.assign(est, { cod: ctx.cod, ano: 0, modo: "ano", mes: null });
    if (!r.plano) {
      el.innerHTML = abertura() + `<section class="painel"><p>Sem plano para este ponto (sem dado de terra).</p></section>`;
      return;
    }
    const lay = montar(r.plano, ctx.ef);
    const meses = listaMeses(r.agenda);
    if (est.mes === null || est.mes >= meses.length) {
      const hoje = r.agenda ? r.agenda.hoje : "";
      est.mes = Math.max(0, meses.findIndex((m) => hoje >= m.ini && hoje <= m.fim));
    }
    if (!r.agenda) est.modo = "ano";
    const conect = r.plano.anos.map((_, k) => ({ blocos: { ...grade(lay, k, "blocos"), modo: "blocos" }, faixas: { ...grade(lay, k, "faixas"), modo: "faixas" } }));
    const W = Math.round(Math.min(640, Math.max(300, (window.innerWidth || 800) - 66)));
    est.compacto = W < 420;
    el.innerHTML = abertura() + faixaAgora(ctx) + heroi(ctx, lay, meses, W) + linhaManiva(ctx) + blocoTempo(ctx)
      + U.extra("historico", { modo: "cartao", olho: !temMetade(ctx) }) // "Por onde começar o seu giro" (2025 com 1 toque); 1 "seu olho" à vista
      + porQue(ctx, lay);
    el.querySelector("[data-aviso-gram]").innerHTML = avisoGramineas(ctx, lay, conect);
    el.querySelectorAll("[data-maniva]").forEach((b) => b.addEventListener("click", () => {
      if ((ctx.resp.maniva || "") !== b.dataset.maniva) ctx.set({ maniva: b.dataset.maniva });
    }));

    const pintar = () => { pintarRocado(el, ctx, lay, meses); pintarFaixas(el, ctx, lay, conect); };
    const play = el.querySelector("[data-play]");
    const parar = () => { clearInterval(est.relogio); est.relogio = null; if (play) { play.innerHTML = U.ic("tocar"); play.classList.remove("tocando"); } };
    el.querySelectorAll("[data-ano]").forEach((b) => b.addEventListener("click", () => { parar(); est.ano = +b.dataset.ano; est.modo = "ano"; pintar(); }));
    el.querySelectorAll("[data-mes]").forEach((b) => b.addEventListener("click", () => { parar(); est.ano = 0; est.modo = "mes"; est.mes = +b.dataset.mes; pintar(); }));
    play?.addEventListener("click", () => {
      if (est.relogio) return parar();
      est.ano = 0;
      if (est.modo !== "mes" || est.mes >= meses.length - 1) est.mes = 0;
      est.modo = "mes";
      pintar();
      play.innerHTML = `<span class="pausa" aria-hidden="true"></span>`;
      play.classList.add("tocando");
      est.relogio = setInterval(() => {
        if (est.mes >= meses.length - 1) return parar();
        est.mes++;
        pintarRocado(el, ctx, lay, meses);
      }, 1100);
    });
    el.querySelector("[data-foco]").addEventListener("click", () => animarFoco(el, ctx, lay, conect));
    ligarCalendario(el, ctx);
    pintar();
    await U.montarExtras(el, ctx);
    requestAnimationFrame(() => fundosRotulos(el)); // roca.js põe o passo na tela logo depois do render: aí o texto já tem medida
  },
};
