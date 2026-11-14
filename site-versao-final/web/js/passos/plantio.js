// QUADRA, site final: passo 3 "Como plantar" (roca.html#/<cod>/3).
// Junta a rotação do José (Partes A/B/C, baixio, bordas, calendário: protótipo/, branch estudo-jose, e7a23b5) com a distribuição
// em faixas do Vicente Lima (PercolaCampo, branch estudo-vicente, 18fd0e3). Desenho e algoritmo: analise/distribuicao.md;
// o que do PercolaCampo é defensável: analise/vicente.md. Contrato do ctx: js/passos/LEIA-ME.md.
import { montar, grade, espalhar, ehGram, LIMIAR_SITIO } from "./plantio/desenho.js";
import { cartaoCalendario, ligarCalendario, seloPlantar } from "./plantio/calendario.js";

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

// ------------------------------------------------------------------ cabeçalho
function cabecalho(ctx) {
  const U = ctx.util, ef = ctx.ef;
  const tam = ef.ha_origem === "resposta" ? `<b>${haTxt(U, ef.ha)}</b>`
    : `<b>${haTxt(U, ef.ha)}</b> (${U.esc(ef.ha_origem.replace(/[()]/g, ""))}; <a href="${ctx.link(2)}">diga o tamanho</a>)`;
  const BX = { pouco: "pequeno (1/5)", terco: "de ⅓", metade: "de metade do roçado" };
  const bx = ef.tem_baixio === false ? "<b>sem baixio</b>"
    : ef.tem_baixio === null ? `<b>baixio: não sei</b> (desenhamos ⅓ tracejado)` : `<b>baixio ${BX[ef.baixio] || ""}</b> (${haTxt(U, ef.baixio_ha)})`;
  const TERRA = { nao_sei: "terra: não sei", arenosa: "terra arenosa", mista: "terra misturada", barro: "terra de barro" };
  const efBx = ef.tem_baixio === false ? "sem baixio, o milho sai do roçado" : "o baixio fica embaixo, com o milho";
  const efTerra = ef.terra === "nao_sei" ? "sem saber a terra, valem as datas do ZARC que servem em todos os solos" : "a terra muda as datas de plantar do ZARC";
  return `<div class="titulo-passo"><h1>Como plantar e distribuir o seu roçado</h1>
    <p>Com as suas respostas, ${tam}, ${bx} e <b>${TERRA[ef.terra] || U.esc(ef.terra)}</b>: o tamanho dá a área de cada faixa; ${efBx};
    ${efTerra}. <a href="${ctx.link(2)}">Mudar as respostas</a>.</p></div>`;
}

// ------------------------------------------------------------------ o roçado visto de cima (SVG em escala)
function linhasFaixa(x, y, w, h) {
  const n = Math.max(1, Math.floor((h - 6) / 9)), gap = (h - 6) / n;
  let s = `<g class="lin">`;
  for (let j = 0; j < n; j++) { const yy = (y + 3 + gap * (j + 0.5)).toFixed(1); s += `<line x1="${x + 4}" y1="${yy}" x2="${x + w - 4}" y2="${yy}"/>`; }
  return s + "</g>";
}

function svgRocado(U, lay, W) {
  const pad = 24, topo = 16, S = W - 2 * pad, s = S / lay.lado, x0 = pad, y0 = pad + topo;
  const H = y0 + S + pad + 14, fs = W < 420 ? 11 : 13;
  const rotulos = (y, hh, i) => {
    const dois = hh >= 34;
    const yr = dois ? y + hh / 2 - 2 : y + hh / 2 + fs * 0.36, yf = yr - fs * 0.92 - 2;
    return `<rect class="rot-fundo" x="${x0 + 5}" y="${yf.toFixed(1)}" width="0" height="${(fs * 1.3 + 4).toFixed(1)}" rx="5"
        data-h1="${(fs * 1.3 + 4).toFixed(1)}" data-h2="${(y + hh / 2 + fs - 1 + 5 - yf).toFixed(1)}"/>
      <text class="rot" x="${x0 + 10}" y="${yr.toFixed(1)}" style="font-size:${fs}px"></text>
      <text class="rot2" x="${x0 + 10}" y="${(y + hh / 2 + fs - 1).toFixed(1)}" style="font-size:${fs - 2}px"${dois ? "" : ' display="none"'}></text>
      <text class="tag" x="${x0 + S - 8}" y="${yr.toFixed(1)}" text-anchor="end" style="font-size:${fs - 2}px" data-tag="${i}"></text>`;
  };
  let h = `<svg class="rocado-svg" viewBox="0 0 ${W} ${H.toFixed(0)}" role="img" aria-label="O roçado visto de cima, em escala">
    <g class="bordas t-perene" data-bordas>
      <rect class="b-fora" x="${x0 - 15}" y="${y0 - 15}" width="${S + 30}" height="${S + 30}" rx="6"/>
      <rect class="b-dentro" x="${x0 - 7}" y="${y0 - 7}" width="${S + 14}" height="${S + 14}" rx="3"/></g>`;
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
  // escala: barra de 5/10/20/25/50/100/200 m com 50–130 unidades
  const L = [5, 10, 20, 25, 50, 100, 200, 500].find((m) => m * s >= 50) || 500;
  const yb = y0 + S + 30;
  h += `<text class="eixo" x="${x0}" y="${y0 - 21}">alto do terreno</text>
    <text class="eixo" x="${x0 + S}" y="${y0 - 21}" text-anchor="end">a água corre ↓${lay.temBaixio ? " para o baixio" : ""}</text>
    <line class="escala" x1="${x0}" y1="${yb}" x2="${x0 + L * s}" y2="${yb}"/>
    <text class="eixo" x="${x0 + L * s + 6}" y="${yb + 4}">${L} m</text>
    <text class="eixo" x="${x0 + S}" y="${yb + 4}" text-anchor="end">cada lado ≈ ${U.num(lay.lado, 0)} m</text></svg>`;
  return h;
}

function cartaoRocado(ctx, lay, meses, W) {
  const U = ctx.util, esc = U.esc, p = ctx.r.plano, a = ctx.r.agenda;
  const marcosMes = (mes) => (a ? a.marcos.map((m, i) => ({ ...m, n: i + 1 })).filter((m) => m.data >= mes.ini && m.data <= mes.fim) : []);
  const botoesMes = meses.map((mes, i) => `<button type="button" class="mes-b" data-mes="${i}" title="${U.MESES[mes.m - 1]}/${mes.y}">
      <span>${U.MESES[mes.m - 1]}</span><small>${mes.m === 1 || i === 0 ? mes.y : "&nbsp;"}</small>
      <i class="mes-marcos">${marcosMes(mes).map((m) => `<b class="${m.rotulo === "Hoje" ? "hoje" : ""}" style="left:${((+m.data.slice(8, 10) - 0.5) / mes.dias) * 100}%"
        title="${esc(m.dia)} · ${esc(m.rotulo)}">${m.n}</b>`).join("")}</i></button>`).join("");
  const tipos = [...new Set(p.faixas.filter((f) => f.parte !== "Bordas" && (f.parte !== "Baixio" || lay.temBaixio)).flatMap((f) => f.anos.map((c) => c.tipo)))];
  const NOME_TIPO = { leguminosa: "leguminosa (caupi, feijão)", cereal: "cereal (milho)", "tampão": "mandioca (reserva)", forragem: "forragem (sorgo, milheto)",
    perene: "perene (palma, gliricídia)", renda: "renda", pousio: "descanso" };
  const amostra = (e) => `<svg class="amostra" viewBox="0 0 30 16" aria-hidden="true"><g class="fx t-leguminosa e-${e}"><rect class="chao" x="1" y="1" width="28" height="14"/>
    <g class="lin e-${e}"><line x1="4" y1="5.5" x2="26" y2="5.5"/><line x1="4" y1="10.5" x2="26" y2="10.5"/></g></g></svg>`;
  return `<div class="cartao rocado-cartao" id="plantio-rocado">
    <div class="rocado-topo"><h2>O roçado visto de cima</h2>
      <div class="anos" role="group" aria-label="Ano do plano">${p.anos.map((ano, k) => `<button type="button" class="ano-b" data-ano="${k}">${ano}</button>`).join("")}</div>
      <span class="ano-selo" data-ano-selo></span></div>
    ${a ? `<div class="mes-controle">
      <button type="button" class="play" data-play aria-label="Passar os meses de ${U.mesAno(a.inicio)} a ${U.mesAno(a.fim)}">▶</button>
      <div class="mes-trilho" role="group" aria-label="Mês a mês">${botoesMes}</div>
      <button type="button" class="botao-leve" data-ano-todo>Ano inteiro</button></div>
    <p class="mes-info" data-mes-info></p>` : ""}
    <div class="rocado-grade">
      <figure class="rocado-fig">${svgRocado(U, lay, W)}
        <figcaption class="sub pequeno">Em escala: quadrado de ${haTxt(U, lay.ha)} (lado ≈ ${U.num(lay.lado, 0)} m), ${lay.nFaixas} faixas em nível de
        ≈ ${U.num(lay.larguraFaixa, 0)} m e ${haTxt(U, lay.faixas[0].ha)} cada${lay.temBaixio ? `, baixio de ${haTxt(U, lay.haBaixio)}` : ""}
        ${U.selo("suposicao", SUPOE_LAYOUT + (ctx.ef.ha_origem === "resposta" ? "" : "; tamanho: " + ctx.ef.ha_origem))}.
        O tamanho de cada faixa e o solo do baixio se confirmam com o técnico. As linhas são ilustrativas: o espaçamento é com o técnico.</figcaption></figure>
      <div class="rocado-lado">
        <p class="ordem-frase">${fraseOrdem(U, lay)}</p>
        <ul class="rocado-lista" data-lista></ul>
        <div class="legenda" data-legenda-ano>${tipos.map((t) => `<span class="tipo-chave ${U.tipoCss(t)}">${esc(NOME_TIPO[t] || t)}</span>`).join("")}
          <span class="leg-borda"><svg class="amostra" viewBox="0 0 30 16" aria-hidden="true"><g class="bordas t-perene"><line class="b-fora" x1="2" y1="4" x2="28" y2="4"/>
            <line class="b-dentro" x1="2" y1="12" x2="28" y2="12"/></g></svg><span>borda: gliricídia por fora, palma por dentro. As bordas não tiram área ${U.selo("suposicao", "como no estudo financeiro (10_familia.py): as bordas ficam no perímetro e não entram na área das faixas")}</span></span>
          ${lay.incerto ? `<span class="leg-incerto">tracejado: o baixio, se você tiver (você respondeu "não sei")</span>` : ""}</div>
        <div class="legenda" data-legenda-mes hidden>${Object.keys(ESTADO).map((e) => `<span>${amostra(e)}${ESTADO[e]}</span>`).join("")}
          <span class="sub">a cor é a da cultura do mês</span></div>
        <p class="sub pequeno" data-reserva-nota hidden><span class="tag-reserva">reserva</span> = mandioca do ano anterior ainda no chão: colhe conforme a
        necessidade e segura a família se o ano vier ruim.</p>
      </div>
    </div></div>`;
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
    s += `Aqui nenhuma ordem evita que gramínea encoste em gramínea: em qualquer uma das 6 ordens são ${lay.contatos} encontros em 3 anos ${sel}
      (veja o aviso em "Por que faixas e não blocos").`;
  } else {
    s += `Das 6 ordens possíveis, esta tem menos encontros de gramínea com gramínea nos 3 anos: ${lay.contatos}, contra ${lay.piorContatos} na pior ${sel}.`;
  }
  return s;
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
      w = Math.max(w, l || t.textContent.length * parseFloat(t.style.fontSize) * 0.58);
    }
    f.setAttribute("width", r1.textContent ? (w + 12).toFixed(1) : "0");
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

function pintarRocado(el, ctx, lay, meses) {
  const U = ctx.util, esc = U.esc, a = ctx.r.agenda, p = ctx.r.plano;
  const mes = est.modo === "mes" ? meses[est.mes] : null, k = mes ? 0 : est.ano;
  el.querySelectorAll("[data-ano]").forEach((b) => b.setAttribute("aria-pressed", String(!mes && +b.dataset.ano === k)));
  el.querySelectorAll("[data-mes]").forEach((b) => { b.classList.toggle("atual", !!mes && +b.dataset.mes === est.mes); b.classList.toggle("fora", est.ano !== 0 && !mes); });
  const seloAno = el.querySelector("[data-ano-selo]");
  seloAno.innerHTML = k === 0 ? U.selo("medido", "culturas do plano para 2027 com as janelas do ZARC 2026/27")
    : U.selo("projecao", `${p.anos[k]}: o plano segue a rotação; as datas repetem o ZARC 2026/27 (o calendário só vai até dez/2027)`);
  const info = el.querySelector("[data-mes-info]");
  if (info) {
    if (mes) {
      const ms = a.marcos.map((m, i) => ({ ...m, n: i + 1 })).filter((m) => m.data >= mes.ini && m.data <= mes.fim);
      info.innerHTML = `<b>${U.MESES[mes.m - 1]}/${mes.y}</b>: cada faixa pintada pelo que o calendário manda fazer no mês.
        ${ms.map((m) => `<span class="marco-n">${m.n}</span> <b>${esc(m.rotulo)}</b> (${esc(m.dia)}): ${esc(m.texto)}`).join(" ")}`;
    } else if (est.ano === 0) info.innerHTML = `Toque num mês (ou em ▶) para ver o roçado mês a mês, de ${U.mesAno(a.inicio)} a ${U.mesAno(a.fim)}.`;
    else info.innerHTML = `O mês a mês só existe para 2027: o calendário do ZARC vai até dez/2027. ${p.anos[k]} aparece só por ano ${U.selo("projecao", "rotação projetada; sem calendário próprio")}.`;
  }
  el.querySelector("[data-legenda-ano]").hidden = !!mes;
  el.querySelector("[data-legenda-mes]").hidden = !mes;
  const itens = [];
  let temReserva = false;
  lay.faixas.forEach((f, i) => {
    const g = el.querySelector(`[data-fx="${i}"]`);
    let tipo, estado = "ano", rot, rot2 = "", tag = "";
    if (mes) {
      const e = estadoMes(a, f.parte, mes);
      tipo = e.tipo; estado = e.estado;
      rot = `${f.letra} · ${e.estado === "descanso" ? (e.palhada ? `palhada do ${curto(e.cultura)}` : "descanso") : `${curto(e.cultura)} · ${(est.compacto ? ESTADO_CURTO : ESTADO)[e.estado]}`}`;
    } else {
      const c = f.plano.anos[k];
      tipo = c.tipo;
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
    g.querySelector(".rot").textContent = rot;
    g.querySelector(".rot2").textContent = rot2;
    g.querySelector(".tag").textContent = tag;
  });
  // lista ao lado: uma linha por parte (não por faixa)
  for (const q of p.faixas) {
    if (q.parte === "Baixio" && !lay.temBaixio) continue;
    if (mes) {
      const e = estadoMes(a, q.parte, mes), rz = q.parte === "Baixio" ? estadoMes(a, "Baixio", mes, true) : null;
      const quando = e.barra ? `${esc(e.barra.rotulo)} ${e.barra.tipo === "colheita" || e.barra.tipo === "roca" ? U.selo("suposicao", "janela de plantio + ciclo da cultura")
        : e.barra.tipo === "preparo" ? U.selo("suposicao", "preparo: o mês antes da janela") : seloPlantar(U, e.linha.fonte)}` : (e.palhada ? `a palhada do ${curto(e.cultura)} fica no chão, sem fogo` : "nada a fazer nesta parte");
      itens.push(`<li class="${U.tipoCss(e.tipo)}"><b>${esc(q.parte)}${e.linha && e.linha.estacao > 2027 ? ` <small>(estação ${e.linha.estacao})</small>` : ""}</b>
        · ${e.cultura && e.estado !== "descanso" ? esc(e.cultura) + ": " : ""}${quando}${rz ? `<br><span class="sub">Caupi no milho em pé: ${ESTADO[rz.estado]}${rz.barra ? ` (${esc(rz.barra.rotulo)})` : ""}</span>` : ""}</li>`);
    } else {
      const c = q.anos[k];
      let txt;
      if (k === 0) txt = `${esc(c.cultura)} <span class="sub">· ${esc(c.texto)}</span>`;
      else {
        const antes = q.anos[k - 1].cultura;
        const de = antes === c.cultura || !/^Parte/.test(q.parte) ? null : lay.partes.find((o) => o.anos[k - 1].cultura === c.cultura);
        txt = antes === c.cultura ? `${esc(c.cultura)} de novo${c.cultura === "Mandioca" ? ` <span class="tag-reserva">reserva</span>` : ""}`
          : `${esc(curto(antes))} → <b>${esc(c.cultura)}</b>${de ? ` <span class="sub">(em ${p.anos[k - 1]} estava na ${esc(de.parte)})</span>` : ""}`;
      }
      const area = /^Parte/.test(q.parte) ? haTxt(U, lay.haParte) + (lay.nFaixas > lay.partes.length ? ` em ${lay.nFaixas / lay.partes.length} faixas` : "") : q.parte === "Baixio" ? haTxt(U, lay.haBaixio) + (lay.incerto ? ", se tiver" : "") : "perímetro";
      itens.push(`<li class="${U.tipoCss(c.tipo)}"><b>${esc(q.parte)}</b> <span class="sub">(${area})</span> · ${txt}</li>`);
    }
  }
  el.querySelector("[data-lista]").innerHTML = itens.join("") + (mes ? "" : `<li class="sem-cor sub pequeno">Área das partes ${U.selo("suposicao", SUPOE_LAYOUT)}</li>`);
  el.querySelector("[data-reserva-nota]").hidden = !temReserva;
  // baixio
  const gb = el.querySelector("[data-bx]");
  if (gb) {
    let tipo = lay.bx.anos[k].tipo, estado = "ano", rot, rot2, caupi = true;
    const ha = haTxt(U, lay.haBaixio);
    if (mes) {
      const e = estadoMes(a, "Baixio", mes), rz = estadoMes(a, "Baixio", mes, true);
      tipo = e.tipo; estado = e.estado; caupi = !!rz;
      rot = `Baixio · ${e.estado === "descanso" ? (e.palhada ? `palhada do ${curto(e.cultura)}` : "descanso") : `${curto(e.cultura)} · ${ESTADO[e.estado]}`}`;
      rot2 = rz ? `caupi no milho em pé: ${ESTADO[rz.estado]}` : "";
      gb.querySelector("[data-milho]").setAttribute("class", `lin e-${estado}`);
      gb.querySelector("[data-caupi]").setAttribute("class", `lin caupi t-leguminosa e-${rz ? rz.estado : "ano"}`);
    } else {
      rot = `Baixio${lay.incerto ? "?" : ""} · ${curto(lay.bx.anos[k].cultura)} + caupi no milho em pé · ${ha}`;
      rot2 = lay.incerto ? "se você tiver baixio: confirme com o técnico" : (k > 0 ? "as linhas de milho e de caupi trocam de lugar" : "linhas de milho e de caupi alternadas");
      gb.querySelector("[data-milho]").setAttribute("class", "lin e-ano");
      gb.querySelector("[data-caupi]").setAttribute("class", "lin caupi t-leguminosa e-ano");
    }
    gb.setAttribute("class", `fx bx ${U.tipoCss(tipo)} e-${estado}${lay.incerto ? " incerto" : ""}`);
    linhasBaixio(gb, k, caupi);
    gb.querySelector(".rot").textContent = rot;
    gb.querySelector(".rot2").textContent = rot2;
  }
  fundosRotulos(el);
  const gbord = el.querySelector("[data-bordas]");
  if (gbord) {
    const e = mes ? estadoMes(a, "Bordas", mes) : null;
    gbord.setAttribute("class", `bordas t-perene e-${e ? e.estado : "ano"}`);
  }
}

// ------------------------------------------------------------------ por que faixas e não blocos (Vicente)
function cartaoFaixas(ctx, lay) {
  const U = ctx.util, p = ctx.r.plano;
  const fig = (modo, titulo) => `<figure class="mini" data-mini="${modo}"><figcaption><b>${titulo}</b></figcaption>
    <div class="mini-svg" data-mini-svg="${modo}"></div><div class="mini-num" data-mini-num="${modo}"></div></figure>`;
  return `<div class="cartao faixas-cartao" id="plantio-faixas">
    <h2>Por que faixas e não blocos</h2>
    <p class="credito">Ideia de distribuição: <b>Vicente Lima</b> (PercolaCampo)</p>
    <p>Quando a mesma família de planta fica toda junta, o que anda pelo chão ou pela água passa de planta em planta pelo bloco inteiro.
    Em faixas, encontra outra família no caminho e para. Aqui contamos isso no desenho do seu roçado, para a <b>gramínea</b>
    (milho, sorgo, milheto), que é a família que o plano mais repete.</p>
    <div class="anos" role="group" aria-label="Ano">${p.anos.map((ano, k) => `<button type="button" class="ano-b" data-ano="${k}">${ano}</button>`).join("")}</div>
    <div class="mini-par">${fig("blocos", "Em blocos lado a lado (como se faz hoje)")}${fig("faixas", "Em faixas (este plano)")}</div>
    <div class="mini-leg"><span><i class="q g1"></i>gramínea</span><span><i class="q g0"></i>outra família (caupi, mandioca, palma)</span>
      <span><i class="q g2"></i>onde o foco chegou</span></div>
    <p class="mini-conclusao" data-mini-conclusao></p>
    <div class="foco-linha"><button type="button" class="botao secundario" data-foco>▶ Ver um foco se espalhar</button>
      <span class="sub pequeno">Ilustra o mecanismo; não prevê perda. O foco começa no alto e passa só para a vizinha da mesma família.</span></div>
    <p class="sub" data-regua></p>
    <div data-aviso-gram></div>
    <p class="limite"><b>O limite:</b> as faixas ajudam contra o que anda pelo chão e pela água (fungo e nematoide de raiz, a
    <i>Phytophthora</i>). Não seguram praga que voa longe: a mariposa da lagarta-do-cartucho e o bicudo voam quilômetros. Contra essas, vale
    a troca de cultura de um ano para o outro e o calendário combinado com os vizinhos.</p>
    <p><a href="modulos/percolacampo/index.html" target="_blank" rel="noopener">Abrir o simulador do Vicente (modelo teórico)</a>
    <span class="sub pequeno">· os números do simulador ainda não têm calibração no semiárido e não entram no plano.</span></p>
    <details><summary>Como a conta é feita (detalhe técnico)</summary>
      <div data-tabela-conect></div>
      <ul class="tec">
        <li>O roçado vira uma grade de células de cerca de 5 m (as linhas seguem as divisas das faixas e do baixio; as colunas, os terços).
        Cada célula recebe a cultura do ano. Duas células de gramínea estão no mesmo bloco se encostam de lado (4 vizinhos; union-find).</li>
        <li><b>p</b> = parte do roçado com gramínea; <b>blocos</b> = pedaços separados; <b>maior bloco</b> = o maior pedaço, em parte do roçado;
        <b>desce até o baixio</b> = algum pedaço liga a linha do alto à linha mais baixa. São as definições do estudo de percolação da paisagem
        do José (p, S, "atravessa"), aplicadas dentro do roçado.</li>
        <li>"Em blocos" = as Partes A, B e C lado a lado, cada uma do alto até o baixio. "Em faixas" = a ordem escolhida acima. As bordas ficam fora da conta.</li>
        <li>Régua: limiar de percolação de sítio 0,5927 na malha quadrada com 4 vizinhos (Alonso-Tlali et al. 2025, <i>Entropy</i> 27(4):386,
        que também compara faixas alternadas e xadrez). Vale para mistura ao acaso; por isso aqui ele é só referência e contamos os blocos de verdade.</li>
        <li>Linhas alternadas contra patógeno: Ramírez et al. 2018 (<i>Phys. Rev. E</i> 98:062409). Zoósporos de <i>Phytophthora</i> que andam
        pela água do solo: Ramírez et al. 2020 (<i>Phys. Rev. E</i> 101:032301).</li>
        <li>O simulador do Vicente calcula outros números (R<sub>eff</sub>, plantas protegidas) com constantes que ainda não têm fonte
        nos artigos da pasta dele. Eles ficam no simulador, fora do plano, até a calibração.</li>
      </ul></details>
  </div>`;
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
  const sw = t(lay.lado / 120);
  if (gr.modo === "faixas") lay.faixas.slice(1).forEach((f) => { h += `<line class="divisa" x1="0" y1="${t(f.y0)}" x2="${t(lay.lado)}" y2="${t(f.y0)}" stroke-width="${sw}"/>`; });
  else for (let j = 1; j < lay.partes.length; j++) { const x = t(lay.lado * j / lay.partes.length); h += `<line class="divisa" x1="${x}" y1="0" x2="${x}" y2="${t(lay.profAlto)}" stroke-width="${sw}"/>`; }
  if (lay.temBaixio) h += `<line class="divisa bx" x1="0" y1="${t(lay.profAlto)}" x2="${t(lay.lado)}" y2="${t(lay.profAlto)}" stroke-width="${t(lay.lado / 70)}"/>`;
  return h + "</svg>";
}

function pintarFaixas(el, ctx, lay, conect) {
  const U = ctx.util, p = ctx.r.plano;
  const k = est.modo === "mes" ? 0 : est.ano;
  clearInterval(est.foco); est.foco = null;
  const caixa = el.querySelector("#plantio-faixas");
  caixa.querySelectorAll("[data-ano]").forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.ano === k)));
  const sel = U.selo("suposicao", "calculado no navegador sobre o desenho (suposição: " + SUPOE_LAYOUT + "); grade de ~5 m, 4 vizinhos");
  const baixo = lay.temBaixio ? "até o baixio" : "até a parte mais baixa";
  for (const modo of ["blocos", "faixas"]) {
    const g = conect[k][modo];
    caixa.querySelector(`[data-mini-svg="${modo}"]`).innerHTML = svgMini(U, lay, g, null);
    caixa.querySelector(`[data-mini-num="${modo}"]`).innerHTML = g.p === 0 ? `<p>Neste ano não há gramínea no roçado.</p>`
      : `<p>A gramínea ocupa <b>${U.pct(g.p)}</b> do roçado em <b>${g.blocos} ${g.blocos === 1 ? "bloco" : "blocos separados"}</b> ${sel}.</p>
        <p>Maior bloco: ${U.pct(g.maior)} do roçado. ${g.desce ? `<b class="ruim">Desce do alto ${baixo}.</b>` : `<b class="bom">Não desce do alto ${baixo}.</b>`}</p>`;
  }
  const b = conect[k].blocos, f = conect[k].faixas;
  caixa.querySelector("[data-mini-conclusao]").innerHTML = b.p === 0 ? ""
    : b.desce && !f.desce && f.blocos > 1 ? `Em ${p.anos[k]}: em blocos, a gramínea forma um caminho só do alto ${baixo}. Em faixas, ela fica em ${f.blocos} pedaços e esse caminho morro abaixo se corta.`
      : b.desce && !f.desce ? `Em ${p.anos[k]}: em faixas, a gramínea ainda fica num bloco só (${U.pct(f.maior)} do roçado); só a faixa de cima, de outra família, fica fora dele. Aqui a ordem das faixas não basta.`
      : !b.desce && !f.desce ? `Em ${p.anos[k]}, a gramínea não desce do alto ${baixo} em nenhum dos dois desenhos${lay.temBaixio ? " (a gramínea do ano é quase só o milho do baixio)" : ""}.`
        : f.desce ? `Em ${p.anos[k]}, a gramínea desce do alto ${baixo} nos dois desenhos.` : "";
  caixa.querySelector("[data-foco]").disabled = b.p === 0;
  const pf = f.p;
  caixa.querySelector("[data-regua]").innerHTML = pf === 0 ? "" : `Régua da teoria: numa mistura ao acaso em malha quadrada, acima de
    ${U.num(LIMIAR_SITIO * 100, 1)}% de plantas da mesma família os pedaços tendem a se ligar de ponta a ponta (limiar 0,593
    ${U.selo("medido", "valor publicado: limiar de percolação de sítio, malha quadrada, 4 vizinhos (Alonso-Tlali et al. 2025, Entropy 27:386)")}).
    Aqui, em ${p.anos[k]}, a gramínea ocupa ${U.pct(pf)}: ${pf > LIMIAR_SITIO ? "<b>acima da régua</b>" : "abaixo da régua"}. É só referência: o roçado
    não é mistura ao acaso, por isso contamos os blocos de verdade no desenho.`;
  // tabela dos 3 anos (detalhe técnico)
  caixa.querySelector("[data-tabela-conect]").innerHTML = `<table class="tab-conect"><tr><th>Ano</th><th>Desenho</th><th>p (gramínea)</th><th>Blocos</th>
    <th>Maior bloco</th><th>Desce ${baixo}?</th></tr>${p.anos.map((ano, j) => ["blocos", "faixas"].map((m) => {
    const g = conect[j][m];
    return `<tr><td>${ano}</td><td>${m === "blocos" ? "em blocos" : "em faixas"}</td><td>${U.num(g.p, 3)}</td><td>${g.blocos}</td><td>${U.num(g.maior, 3)}
      (S = ${U.num(g.S, 2)})</td><td>${g.p === 0 ? "—" : g.desce ? "sim" : "não"}</td></tr>`;
  }).join("")).join("")}</table><p class="sub pequeno">S = parte da gramínea que está no maior bloco. Todos os números ${sel}.</p>`;
}

function avisoGramineas(ctx, lay, conect) {
  const U = ctx.util, p = ctx.r.plano;
  const acima = p.anos.filter((_, j) => conect[j].faixas.p > LIMIAR_SITIO);
  const pontes = [];
  for (const q of lay.partes) for (let j = 0; j + 1 < p.anos.length; j++)
    if (ehGram(q.anos[j].cultura) && ehGram(q.anos[j + 1].cultura)) pontes.push(`${q.parte} (${p.anos[j]}→${p.anos[j + 1]})`);
  if (!acima.length && !pontes.length) return "";
  const pMax = Math.max(...p.anos.map((_, j) => conect[j].faixas.p));
  const semMandioca = !lay.partes.some((q) => q.anos.some((c) => c.cultura === "Mandioca"));
  return `<p class="aviso vermelho"><b>Atenção neste lugar:</b> ${semMandioca ? "sem mandioca apta aqui, " : ""}a gramínea fica com até ${U.pct(pMax)}
    do roçado${acima.length ? ` (acima da régua em ${acima.join(", ")})` : ""}${pontes.length ? ` e repete no mesmo lugar em anos seguidos: ${pontes.join("; ")}` : ""}
    ${U.selo("suposicao", "calculado sobre o desenho")}. Nenhuma ordem de faixas resolve isso sozinha. Converse com o técnico sobre trocar um sorgo forrageiro
    por leguminosa, palma ou pousio pastejado.</p>`;
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

// ------------------------------------------------------------------ a rotação 2027–2029 (tabela)
function cartaoRotacao(ctx, lay) {
  const U = ctx.util, esc = U.esc, p = ctx.r.plano;
  const area = (f) => (/^Parte/.test(f.parte) ? `${haTxt(U, lay.haParte)} ${U.selo("suposicao", SUPOE_LAYOUT)}`
    : f.parte === "Baixio" ? (lay.temBaixio ? `${haTxt(U, lay.haBaixio)}${lay.incerto ? " (se tiver)" : ""} ${U.selo("suposicao", "fração do baixio da sua resposta; \"não sei\" = 1/3")}` : "")
      : f.parte === "Bordas" ? "no perímetro: palma por dentro, gliricídia por fora" : "");
  const seloAno = (a, k) => `${a} ${k === 0 ? U.selo("medido", "janelas do ZARC 2026/27 nos textos de cada cultura")
    : U.selo("projecao", "a rotação segue; as datas repetem o ZARC 2026/27")}`;
  const cel = (c) => `<div class="rot-cel ${U.tipoCss(c.tipo)}"><b>${esc(c.cultura)}</b><span>${esc(c.texto)}${/estimad/.test(c.texto)
    ? " " + U.selo("suposicao", "janela estimada pelo início típico da chuva (IMERG); sem ZARC aqui") : ""}</span></div>`;
  let h = `<div class="cartao" id="plantio-rotacao"><h2>A rotação ${p.anos[0]}–${p.anos[p.anos.length - 1]}, parte por parte</h2>
    <p class="sub">Cada parte recebe uma cultura por ano e, no ano seguinte, a cultura muda de parte. A leguminosa deixa nitrogênio para o cereal
    que vem depois, e sempre fica mandioca no chão como reserva para um ano ruim (onde a mandioca cabe).</p>
    ${p.modelo_ne ? `<p class="aviso">Fora do Nordeste usamos o modelo do sertão: as culturas são do lugar, mas as datas, as bordas e o alerta do ano foram calibrados no NE.</p>` : ""}
    <div class="tab-rot-caixa"><table class="tab-rot"><tr><th>Parte do roçado</th>${p.anos.map((a, k) => `<th>${seloAno(a, k)}</th>`).join("")}</tr>`;
  for (const f of p.faixas) {
    if (f.parte === "Baixio" && !lay.temBaixio) continue;
    h += `<tr><td><b>${esc(f.parte)}</b><br><span class="sub pequeno">${area(f)}</span></td>${f.anos.map((c, k) => `<td><span class="ano-rot">${seloAno(p.anos[k], k)}</span>${cel(c)}</td>`).join("")}</tr>
      <tr class="porque"><td colspan="${p.anos.length + 1}">Por quê: ${esc(f.por_que)}</td></tr>`;
  }
  h += `</table></div>`;
  if (p.interruptor) h += `<p class="aviso"><b>Interruptor do ano:</b> ${esc(p.interruptor)}</p>`;
  h += `<details><summary>As regras da rotação, a evidência de cada uma e as notas</summary>
    ${(p.principios || []).map((c) => `<div class="ev"><div class="ev-regra">${esc(c.regra || c.configuracao)}${c.irrigado ? " <span class=\"sub\">(irrigado)</span>" : ""}</div>
      <div class="sub pequeno">${c.efeito ? `<b>${esc(c.efeito)}</b> · ` : ""}grau ${esc(c.grau)}·${esc(c.transferencia)} ${esc(c.rotulo_transferencia)} · ${esc(c.referencia)}${c.lugar ? " · " + esc(c.lugar) : ""}${c.doi ? ` · <a href="https://doi.org/${esc(c.doi)}" target="_blank" rel="noopener">doi</a>` : ""}</div></div>`).join("")}
    <ul class="notas">${(p.notas || []).map((n) => `<li>${esc(n)}</li>`).join("")}</ul></details></div>`;
  return h;
}

// ------------------------------------------------------------------ passo
export default {
  id: "plantio",
  titulo: "Como plantar",
  render(el, ctx) {
    pararTudo();
    const U = ctx.util, r = ctx.r;
    if (est.cod !== ctx.cod) Object.assign(est, { cod: ctx.cod, ano: 0, modo: "ano", mes: null });
    if (!r.plano) {
      el.innerHTML = `<div class="titulo-passo"><h1>Como plantar e distribuir o seu roçado</h1></div>
        <div class="cartao"><p>Sem plano para este ponto (sem dado de terra no GAEZ).</p></div>`;
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
    const W = Math.round(Math.min(600, Math.max(300, (window.innerWidth || 800) - 70)));
    est.compacto = W < 420;
    el.innerHTML = cabecalho(ctx) + cartaoRocado(ctx, lay, meses, W) + cartaoFaixas(ctx, lay) + cartaoCalendario(ctx) + cartaoRotacao(ctx, lay);
    el.querySelector("[data-aviso-gram]").innerHTML = avisoGramineas(ctx, lay, conect);

    const pintar = () => { pintarRocado(el, ctx, lay, meses); pintarFaixas(el, ctx, lay, conect); };
    const parar = () => { clearInterval(est.relogio); est.relogio = null; const b = el.querySelector("[data-play]"); if (b) { b.textContent = "▶"; b.classList.remove("tocando"); } };
    el.querySelectorAll("[data-ano]").forEach((b) => b.addEventListener("click", () => { parar(); est.ano = +b.dataset.ano; est.modo = "ano"; pintar(); }));
    el.querySelectorAll("[data-mes]").forEach((b) => b.addEventListener("click", () => { parar(); est.ano = 0; est.modo = "mes"; est.mes = +b.dataset.mes; pintar(); }));
    el.querySelector("[data-ano-todo]")?.addEventListener("click", () => { parar(); est.modo = "ano"; pintar(); });
    el.querySelector("[data-play]")?.addEventListener("click", (ev) => {
      if (est.relogio) return parar();
      est.ano = 0;
      if (est.modo !== "mes" || est.mes >= meses.length - 1) est.mes = 0;
      est.modo = "mes";
      pintar();
      ev.currentTarget.textContent = "❚❚";
      ev.currentTarget.classList.add("tocando");
      est.relogio = setInterval(() => {
        if (est.mes >= meses.length - 1) return parar();
        est.mes++;
        pintarRocado(el, ctx, lay, meses);
      }, 1100);
    });
    el.querySelector("[data-foco]").addEventListener("click", () => animarFoco(el, ctx, lay, conect));
    ligarCalendario(el, ctx);
    pintar();
    requestAnimationFrame(() => fundosRotulos(el)); // roca.js põe o passo na tela logo depois do render: aí o texto já tem medida
  },
};
