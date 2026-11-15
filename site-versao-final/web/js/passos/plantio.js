// QUADRA, site final: passo 3 "O plano" (roca.html#/<cod>/3). Versão 2: pouco texto, no visual da tela inicial.
// Junta a rotação do José (Partes A/B/C, baixio, bordas, calendário: protótipo/, branch estudo-jose, e7a23b5) com a distribuição
// em faixas do Vicente Lima (PercolaCampo, branch estudo-vicente, 18fd0e3). Desenho e algoritmo: analise/distribuicao.md;
// o que do PercolaCampo é defensável: analise/vicente.md. Contrato do ctx e regras de texto: js/passos/LEIA-ME.md.
// Rodada 2 (analise/fluxo2/BRIEFING.md, D3): abre em "Seu jeito, melhorado" (só as culturas que ele marcou) e um controle de 2 lados
// [Seu jeito, melhorado | O ideal] (grava `plano`: "" | "ideal"); no lado "O ideal", "O que vale mais para você?" (grava `prioridade`).
// Tudo o que a tela mostra sai do plano à vista, escolhido() de extras/ideal.js: o roçado (desenho.js, larg × comp), o "por quê" de
// cada parte (o efeito da maniva e do ano passado), "O que você ganha" (comparar3: Hoje → Melhorado → Ideal), "Seu terreno em
// metros" (extras/terreno.js, do C1), o calendário (as linhas do plano) e os extras de "Por que este plano".
import { montar, grade, espalhar, ehGram, LIMIAR_SITIO } from "./plantio/desenho.js";
import { linhaDoTempo, calendarioCompleto, ligarCalendario, agora, agendaDoPlano } from "./plantio/calendario.js";
import { olho, OLHOS } from "../extras/voce_decide.js";
import { escolhido, comparar3, NOME_PRIORIDADE, textoItem, falaTexto, agronomia } from "../extras/ideal.js";
import { contas as contasTerreno } from "../extras/terreno.js";
import { mancheteIdeal } from "../extras/hoje_ideal.js";
// Ordem (D3): título → "Agora" → o roçado (controle de 2 lados, prioridade no lado ideal, desenho, "por quê" de cada parte, "Seu terreno
// em metros" e o mês a mês nos "ver mais") → "O que você ganha" → o que fazer e quando → "Por que este plano", com 3 "ver mais".
// "Seu olho" (ponto 16) à vista: o da metade guardada (calendário) ou, sem ele, o das faixas (sob o desenho).

// estado de tela (não é resposta): ano escolhido, vista por ano ou mês a mês, mês, relógios das animações, o "ver mais" do terreno
// aberto e o controle tocado (para ele ficar no mesmo lugar da tela depois do redesenho)
const est = { cod: null, ano: 0, modo: "ano", mes: null, relogio: null, foco: null, compacto: false, terreno: false, terrenoTocado: false, ancora: null };

const CURTO = { "Feijão-caupi": "caupi", "Sorgo forrageiro": "sorgo forrageiro", "Sorgo granífero": "sorgo de grão", "Feijão comum": "feijão",
  "Palma + gliricídia": "palma + gliricídia", "Palma forrageira": "palma", "Mucuna-preta": "mucuna", "Algodão herbáceo": "algodão",
  "Cana-de-açúcar": "cana", "Pousio pastejado": "descanso" };
const curto = (c) => { const b = String(c || "").replace(/ no milho em pé$/, ""); return CURTO[b] || b.toLowerCase(); };
const listaE = (v) => (v.length <= 1 ? v.join("") : v.slice(0, -1).join(", ") + " e " + v[v.length - 1]);
const ESTADO = { preparo: "preparo sem fogo", risco: "pode plantar, com mais risco", plantar: "plantar", crescendo: "crescendo",
  colher: "colher", descanso: "descanso" };
const ESTADO_CURTO = { ...ESTADO, preparo: "preparo", risco: "plantar c/ risco" };
const PRIOR = { colheita: 6, plantio: 5, estimado: 5, roca: 4, risco: 3, preparo: 2, pousio: 1 };
const DE_BARRA = { colheita: "colher", plantio: "plantar", estimado: "plantar", roca: "crescendo", risco: "risco", preparo: "preparo", pousio: "descanso" };
// "O que vale mais para você?": a aba tocada → a prioridade gravada (o mapa INV de extras/cenarios.js)
const PRIO = [["agua", "garantir", "Água", "gota"], ["renda", "vender", "Renda", "dinheiro"], ["solo", "solo", "Solo", "broto"],
  ["plano", "equilibrar", "Um pouco de cada", "faixas"]];

/** O que o desenho supõe (selo SUPOSIÇÃO), com as medidas da pessoa quando ela deu. */
const supoe = (U, lay) => (lay.medidas === "resposta"
  ? `roçado de ${U.num(lay.larg)} × ${U.num(lay.comp)} m (as suas medidas), a água descendo no comprimento`
  : "roçado quadrado com a área da resposta (sem as suas medidas)")
  + "; Partes A, B e C do mesmo tamanho; bordas no perímetro sem tirar área (como no estudo financeiro, 10_familia.py); faixas de pelo menos 10 m";

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

/** O que a parte está fazendo no mês, pelas barras da agenda do plano à vista (revez = a linha da leguminosa no milho em pé do baixio). */
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

/** A 2ª planta do baixio no ano (o texto do motor diz): "caupi" no revezamento, "mucuna"; null quando não há (sem revezamento,
 *  milho solteiro, sorgo sem leguminosa no cardápio). */
function segundaBaixio(c, p) {
  const t = String(c?.texto || "");
  if (!c || /sem revezamento|sem feijão para revezar|solteiro/i.test(t)) return null;
  if (c.mucuna || /mucuna/i.test(t)) return "mucuna";
  const m = /\+\s*([^;(]+?)\s+(?:em revezamento|no milho em pé)/i.exec(t);
  if (m) return /^feij[aã]o(-caupi)?$/i.test(m[1].trim()) && p.leguminosa ? curto(p.leguminosa) : m[1].trim().toLowerCase();
  return /revezamento/i.test(t) && p.leguminosa ? curto(p.leguminosa) : null;
}

const haTxt = (U, v) => (v >= 10 ? U.num(v, 0) : v >= 1 ? U.num(v, 1).replace(/,0$/, "") : U.num(v, 2)) + " ha";
const metros = (U, m) => `${U.num(m, m >= 100 || Math.abs(m - Math.round(m)) < 0.05 ? 0 : 1)} m`;
const medidasTxt = (U, lay) => (lay.medidas === "resposta" ? `${U.num(lay.larg)} × ${U.num(lay.comp)} m` : `≈ ${U.num(lay.larg)} × ${U.num(lay.comp)} m`);
const botoesAno = (p) => `<div class="anos" role="group" aria-label="Ano do plano">${p.anos.map((ano, k) =>
  `<button type="button" class="ano-b" data-ano="${k}">${ano}</button>`).join("")}</div>`;

// ------------------------------------------------------------------ abertura (a ficha da casca mostra o tamanho e o "Mudar")
function abertura() {
  return `<div class="titulo-passo"><p class="kicker">O plano</p>
    <h1>Plante em faixas.<span class="eco">Cada ano, outro lugar.</span></h1></div>`;
}

/** A faixa "Agora: …" sob o título (agora() de plantio/calendario.js, com a agenda do plano à vista). */
function faixaAgora(ctx, ag) {
  const U = ctx.util, t = agora(ctx, ag);
  return t ? `<div class="plantio-agora">${U.faixa("semente", "verde", `<b>Agora:</b> ${U.esc(t)}`)}</div>` : "";
}

// ------------------------------------------------------------------ o controle de 2 lados e o "O que vale mais para você?"
function controle(ctx, V) {
  const U = ctx.util, esc = U.esc, ideal = V.E.tipo === "ideal", pm = V.c3?.melhor?.plano || (ideal ? null : V.plano);
  // nomes bem curtos no botão (no máximo 2 linhas): os dois sorgos viram "sorgo"
  const nomes = (ns) => [...new Set(ns.map((n) => curto(n).replace(/^sorgo .*/, "sorgo").replace(/ \+ .*/, "")))];
  const resumo = (ns, n) => { const v = nomes(ns); return listaE([...v.slice(0, n), ...(v.length > n ? [`mais ${v.length - n}`] : [])]); };
  const acr = pm?.acrescenta || [];
  const botao = (lado, titulo, sub) => `<button type="button" class="lado" data-lado="${lado}" aria-pressed="${(lado === "ideal") === ideal}">
      <b>${titulo}</b><small>${esc(sub)}</small></button>`;
  // o seu jeito: rótulo fixo de 1 linha (a ficha da casca, no topo, já lista as culturas); o ideal já diz o que acrescenta (convida a
  // tocar) e, do lado ideal, a prioridade que vale. Os 2 botões ficam com 3 linhas.
  // o ganho de cada lado já no botão (o melhor do produto sem rolar): "+R$ 99 por ano", "+R$ 2.170 por ano, quebra de 2 para 1 em 10"
  const H = V.c3?.hoje?.beneficios, gM = ganhoCurto(U, H, V.c3?.melhor?.beneficios), gI = ganhoCurto(U, H, V.c3?.ideal?.beneficios);
  const subIdeal = ideal ? `${NOME_PRIORIDADE[V.E.prioridade]}${gI ? ` · ${gI}` : ""}` : gI || (acr.length ? `com ${resumo(acr, 2)}` : "tudo o que sabemos");
  let h = `<div class="lados" role="group" aria-label="Qual plano ver">${botao("melhor", "Seu jeito, melhorado", gM || "só o que você planta")}
    ${botao("ideal", "O ideal", subIdeal)}</div>`;
  if (!ideal) return h;
  const pri = V.E.prioridade, origem = V.E.prioridade_origem;
  const bts = PRIO.map(([k, p, nome, icone]) => `<button type="button" class="chip prio-b${p === pri ? " verde" : ""}" data-prio="${k}"
      aria-pressed="${p === pri}">${U.ic(icone)}<span>${nome}</span></button>`).join("");
  // a manchete do ideal comparada ao SEU JEITO (o desenho ao lado), não ao plano do núcleo (extras/hoje_ideal.js, 15/11)
  const manchete = mancheteIdeal(V.plano, pm) || V.plano.manchete || NOME_PRIORIDADE[pri];
  h += `<div class="prio"><p class="prio-q">O que vale mais para você?</p>
    <div class="prio-bs" role="group" aria-label="O que vale mais para você?">${bts}</div>
    <p class="lado-frase">${esc(falaTexto(manchete))}${origem !== "resposta" ? ` <span class="pequeno">(${esc(origem)})</span>` : ""}</p></div>`;
  return h;
}

// ------------------------------------------------------------------ o roçado visto de cima (SVG em escala, larg × comp)
function linhasFaixa(x, y, w, h) {
  const n = Math.max(1, Math.floor((h - 6) / 9)), gap = (h - 6) / n;
  let s = `<g class="lin">`;
  for (let j = 0; j < n; j++) { const yy = (y + 3 + gap * (j + 0.5)).toFixed(1); s += `<line x1="${x + 4}" y1="${yy}" x2="${(x + w - 4).toFixed(1)}" y2="${yy}"/>`; }
  return s + "</g>";
}

/** O roçado em escala: a largura (larg) na horizontal e o comprimento (comp, o sentido em que a água desce) na vertical. Sem as
 *  medidas, o quadrado da área (como antes). Um roçado comprido cresce até 1,5 vez a largura do desenho e fica no meio; num muito
 *  estreito, os nomes das faixas passam da borda (com o fundo escuro atrás). */
function svgRocado(U, lay, W) {
  const pad = 24, topo = 18, Sx = W - 2 * pad, Hmax = Math.max(Sx, Math.min(460, Math.round(Sx * 1.5)));
  const s = Math.min(Sx / lay.larg, Hmax / lay.comp), w = lay.larg * s, hT = lay.comp * s;
  const x0 = pad + (Sx - w) / 2, y0 = pad + topo;
  const H = y0 + hT + pad + 16, fs = W < 420 ? 12 : 14, tx = x0 + 12 + fs + 8;
  const rotulos = (y, hh, i) => {
    const dois = hh >= fs * 2.6;
    const yr = dois ? y + hh / 2 - 2 : y + hh / 2 + fs * 0.36, yf = yr - fs * 0.95 - 3;
    return `<rect class="rot-fundo" x="${(x0 + 6).toFixed(1)}" y="${yf.toFixed(1)}" width="0" height="${(fs * 1.35 + 6).toFixed(1)}" rx="7"
        data-h1="${(fs * 1.35 + 6).toFixed(1)}" data-h2="${(y + hh / 2 + fs - 1 + 6 - yf).toFixed(1)}" data-x="${(tx - x0 - 6).toFixed(1)}"/>
      <g class="rot-ic" transform="translate(${(x0 + 12).toFixed(1)},${(yr - fs * 0.95).toFixed(1)}) scale(${((fs + 2) / 24).toFixed(3)})"></g>
      <text class="rot" x="${tx.toFixed(1)}" y="${yr.toFixed(1)}" style="font-size:${fs}px"></text>
      <text class="rot2" x="${tx.toFixed(1)}" y="${(y + hh / 2 + fs - 1).toFixed(1)}" style="font-size:${fs - 2}px"${dois ? "" : ' display="none"'}></text>
      <text class="tag" x="${(x0 + w - 10).toFixed(1)}" y="${yr.toFixed(1)}" text-anchor="end" style="font-size:${fs - 2}px" data-tag="${i}"></text>`;
  };
  const fino = (hh) => (hh < fs + 4 ? ' data-fino="1"' : ""); // faixa fina demais para o nome: o nome fica na lista
  let h = `<svg class="rocado-svg" viewBox="0 0 ${W} ${H.toFixed(0)}" role="img" aria-label="O roçado visto de cima, em escala: ${U.esc(medidasTxt(U, lay))}">
    <g class="bordas t-perene" data-bordas>
      <rect class="b-fora" x="${(x0 - 15).toFixed(1)}" y="${y0 - 15}" width="${(w + 30).toFixed(1)}" height="${(hT + 30).toFixed(1)}" rx="8"/>
      <rect class="b-dentro" x="${(x0 - 7).toFixed(1)}" y="${y0 - 7}" width="${(w + 14).toFixed(1)}" height="${(hT + 14).toFixed(1)}" rx="4"/></g>`;
  if (lay.reserva) { // as perenes que ele já tem: o pedaço delas, no alto, fora do giro
    const hh = lay.reserva.y1 * s, nomes = listaE(lay.reserva.culturas.map(curto));
    h += `<g class="fx t-perene e-ano per" data-per><rect class="chao" x="${x0.toFixed(1)}" y="${y0.toFixed(1)}" width="${w.toFixed(1)}" height="${hh.toFixed(1)}"/>
      ${hh >= fs + 4 ? `<text class="rot" x="${(x0 + 12).toFixed(1)}" y="${(y0 + hh / 2 + fs * 0.36).toFixed(1)}" style="font-size:${fs}px">Já plantado · ${U.esc(nomes)} · ${U.esc(metros(U, lay.reserva.larguraM))}</text>` : ""}</g>`;
  }
  lay.faixas.forEach((f, i) => {
    const y = y0 + f.y0 * s, hh = (f.y1 - f.y0) * s;
    h += `<g class="fx" data-fx="${i}"${fino(hh)}><rect class="chao" x="${x0.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${hh.toFixed(1)}"/>
      ${linhasFaixa(x0, y, w, hh)}${rotulos(y, hh, i)}</g>`;
  });
  if (lay.temBaixio) {
    const y = y0 + lay.profAlto * s, hh = hT - lay.profAlto * s;
    h += `<g class="fx bx${lay.incerto ? " incerto" : ""}" data-bx data-y="${y.toFixed(1)}" data-h="${hh.toFixed(1)}" data-x="${x0.toFixed(1)}" data-w="${w.toFixed(1)}"${fino(hh)}>
      <rect class="chao" x="${x0.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${hh.toFixed(1)}"/>
      <g class="lin" data-milho></g><g class="lin caupi t-leguminosa" data-caupi></g>${rotulos(y, hh, "bx")}</g>`;
  }
  // escala: barra de 5/10/20/25/50/100/200 m com pelo menos 50 unidades; as medidas do roçado à direita
  const L = [5, 10, 20, 25, 50, 100, 200, 500].find((m) => m * s >= 50) || 500;
  const yb = y0 + hT + 32;
  h += `<text class="eixo" x="${(x0 - 15).toFixed(1)}" y="${y0 - 24}">alto</text>
    <text class="eixo" x="${(x0 + w + 15).toFixed(1)}" y="${y0 - 24}" text-anchor="end">a água desce ↓</text>
    <line class="escala" x1="${x0.toFixed(1)}" y1="${yb.toFixed(1)}" x2="${(x0 + L * s).toFixed(1)}" y2="${yb.toFixed(1)}"/>
    <text class="eixo" x="${(x0 + L * s + 8).toFixed(1)}" y="${(yb + 4).toFixed(1)}">${L} m</text>
    <text class="eixo" x="${Math.max(x0 + w, W - pad).toFixed(1)}" y="${(yb + 4).toFixed(1)}" text-anchor="end">${U.esc(medidasTxt(U, lay))}</text></svg>`;
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

/** As linhas do baixio: com 2 plantas (milho e caupi, milho e mucuna), alternadas e trocando de lugar a cada ano (motor:
 *  revezamento); com 1 planta só (sem revezamento), todas dela. */
function linhasBaixio(g, k, duas) {
  const x = +g.dataset.x, y = +g.dataset.y, w = +g.dataset.w, h = +g.dataset.h;
  const n = Math.max(2, Math.floor((h - 6) / 9)), gap = (h - 6) / n;
  let milho = "", caupi = "";
  for (let j = 0; j < n; j++) {
    const yy = (y + 3 + gap * (j + 0.5)).toFixed(1), ln = `<line x1="${x + 4}" y1="${yy}" x2="${(x + w - 4).toFixed(1)}" y2="${yy}"/>`;
    if (!duas || (j + k) % 2 === 0) milho += ln; else caupi += ln;
  }
  g.querySelector("[data-milho]").innerHTML = milho;
  g.querySelector("[data-caupi]").innerHTML = caupi;
}

/** O "por quê" de cada parte, curto (a 1ª frase do motor, sem os parênteses de fonte): é aqui que aparece o efeito das respostas de
 *  Sua roça ("Começa com o feijão: ali teve milho em 2025 e 2026."; "A sua mandioca já está aqui"). Partes com o mesmo "por quê"
 *  ficam numa linha só ("A e C"). Com uma cultura só, a frase do "não dá para girar" já está sob o controle. */
const curtaPq = (s) => {
  const t = String(s || "").replace(/\s*\([^)]*\)/g, "").replace(/\s+/g, " ").trim();
  const m = /^(.+?[.!?])(\s|$)/.exec(t);
  // o ano de outra planta no meio do baixio já aparece no desenho de cada ano
  return (m ? m[1] : t).replace(/, com um ano de [^.]+ no meio\.$/, ".");
};
/** Sob o desenho, antes do "por quê": no seu jeito, a nota do motor quando não dá para girar (uma cultura só, capins parentes,
 *  nenhuma cultura conhecida; ela já diz o que o ideal acrescenta) e os avisos (sem maniva, cultura sem data aqui, a "outra"). */
function notasDoLado(ctx, V) {
  const U = ctx.util, esc = U.esc, p = V.plano;
  if (V.E.tipo === "ideal") return "";
  const notas = p.notas || [];
  const frase = notas.find((n) => /não dá para girar|não quebra a lagarta|^Sem cultura conhecida/.test(n));
  const avisos = [...(p.avisos || []).map((a) => a.txt), ...notas.filter((n) => /"outra"/.test(n))];
  return (frase ? `<p class="lado-frase">${esc(frase)}</p>` : "")
    + avisos.map((t) => `<p class="lado-aviso">${U.ic("alerta")}<span>${esc(t)}</span></p>`).join("");
}

function porQueLista(ctx, V, lay) {
  const U = ctx.util, p = V.plano, grupos = [];
  for (const f of p.faixas) {
    if (f.parte === "Baixio" && !lay.temBaixio) continue;
    if (f.parte === "Bordas") continue; // a linha da cerca viva, sob o desenho, já diz o que vai nas bordas
    if (p.nao_gira && /^Parte /.test(f.parte)) continue;
    const txt = curtaPq(falaTexto(p.por_que_de?.[f.parte] ?? f.por_que));
    if (!txt) continue;
    const L = /^Parte /.test(f.parte) ? f.parte.replace("Parte ", "") : f.parte;
    const g = grupos.find((x) => x.txt === txt);
    if (g) g.letras.push(L); else grupos.push({ letras: [L], txt, tipo: f.anos[0].tipo });
  }
  if (!grupos.length) return "";
  return `<ul class="pq" aria-label="Por que cada parte">${grupos.map((g) => `<li class="${U.tipoCss(g.tipo)}"><span class="pq-l">${U.esc(listaE(g.letras))}</span>
    <span class="pq-t">${U.esc(g.txt)}</span></li>`).join("")}</ul>`;
}

/** "Seu terreno em metros" (extras/terreno.js, do C1) num "ver mais" logo depois do desenho: só carrega quando abre, e redesenha na
 *  troca de ano. O bloco tem ~145 palavras e ~1.200 px: à vista, sozinho levaria um terço do teto da tela. */
function terrenoVerMais(ctx, lay) {
  const U = ctx.util;
  return `<details class="ver-mais terreno-vm" data-terreno${est.terreno ? " open" : ""}>
    <summary>Seu terreno: metros e distância das covas</summary><div class="terreno-caixa" data-terreno-caixa
      aria-label="${U.esc(medidasTxt(U, lay))}"></div></details>`;
}
function ligarTerreno(el, ctx, V) {
  const det = el.querySelector("[data-terreno]");
  if (!det) return null;
  const caixa = det.querySelector("[data-terreno-caixa]");
  let pedido = 0;
  const desenhar = () => {
    const meu = ++pedido;
    return import("../extras/terreno.js")
      .then((m) => (meu === pedido ? m.default.render(caixa, ctx, { plano: V.plano, ano: est.modo === "mes" ? 0 : est.ano }) : null))
      .catch((e) => { console.error("extra \"terreno\":", e); caixa.innerHTML = `<p class="pequeno">O desenho em metros não carregou agora.</p>`; });
  };
  det.addEventListener("toggle", () => {
    if (det.open !== est.terreno) est.terrenoTocado = true; // a pessoa abriu ou fechou: vale a escolha dela
    if (det.open === est.terreno && caixa.children.length) return; // o "toggle" do details que já nasce aberto
    est.terreno = det.open;
    if (det.open) desenhar();
  });
  V.redesenharTerreno = () => { if (det.open) desenhar(); };
  return det.open ? desenhar() : null;
}

function heroi(ctx, V, lay, meses, W) {
  const U = ctx.util, p = V.plano, a = V.ag;
  const chips = meses.map((mes, i) => `<button type="button" class="mes-b" data-mes="${i}" title="${U.MESES[mes.m - 1]}/${mes.y}">
      ${U.MESES[mes.m - 1]}${mes.m === 1 || i === 0 ? `<small>${String(mes.y).slice(2)}</small>` : ""}</button>`).join("");
  const amostra = (e) => `<svg class="amostra" viewBox="0 0 30 16" aria-hidden="true"><g class="fx t-leguminosa e-${e}"><rect class="chao" x="1" y="1" width="28" height="14"/>
    <g class="lin e-${e}"><line x1="4" y1="5.5" x2="26" y2="5.5"/><line x1="4" y1="10.5" x2="26" y2="10.5"/></g></g></svg>`;
  const ordem = `<p>${fraseOrdem(U, lay)}</p>
    <p>O desenho é uma suposição ${U.selo("suposicao", supoe(U, lay))}: ${lay.medidas === "resposta"
      ? `roçado de ${U.num(lay.larg)} × ${U.num(lay.comp)} m (${haTxt(U, lay.ha)}), as suas medidas, com a água descendo no comprimento`
      : `roçado quadrado de ${haTxt(U, lay.ha)} (lado ≈ ${U.num(lay.lado, 0)} m)`},
    ${lay.nFaixas} faixas em nível de ≈ ${metros(U, lay.larguraFaixa)} e ${haTxt(U, lay.faixas[0].ha)} cada (Partes A, B e C do mesmo tamanho;
    faixa de pelo menos 10 m, senão 3 faixas)${lay.temBaixio ? `, baixio de ${haTxt(U, lay.haBaixio)}${lay.incerto ? ` (você respondeu "não sei": desenhamos ⅓)` : ""}` : ""}.
    As bordas ficam no perímetro e não tiram área, como no estudo financeiro. O espaçamento de cada parte está em "Seu terreno em metros";
    o tamanho de cada faixa e o solo do baixio se confirmam com o técnico.</p>
    <p>No mês a mês, cada faixa mostra o que o calendário manda fazer: plantar e "pode plantar, com mais risco" vêm das janelas do ZARC
    ${U.selo("medido", "ZARC 2026/27 e portarias plurianuais do MAPA")}; crescendo e colher vêm da janela mais o ciclo da cultura
    ${U.selo("suposicao", "ciclos da cultura; alguns sem fonte")}. O calendário só vai até dez/2027: 2028 e 2029 aparecem só por ano
    ${U.selo("projecao", "a rotação segue; as datas repetem o ZARC 2026/27")}.</p>`;
  const legenda = `<p class="vista" data-vista></p>
    <ul class="leg-partes" data-lista></ul>
    <div class="leg-estados" data-legenda-mes hidden>${Object.keys(ESTADO).map((e) => `<span>${amostra(e)}${ESTADO[e]}</span>`).join("")}</div>`;
  // bordas: a cerca viva do núcleo (palma e gliricídia) ou, no seu jeito, as perenes que ele já tem (caju, banana, cana)
  const bordas = p.faixas.find((f) => f.parte === "Bordas");
  const nomeBordas = bordas ? curto(bordas.anos[0].cultura).replace(" + ", " e ") : "";
  const cercaTxt = !bordas ? "" : /palma|gliric/i.test(nomeBordas) ? `Cerca viva: ${nomeBordas}`
    : `Nas bordas: ${nomeBordas}${bordas.anos[0].ja_plantado ? ", já plantado" : ""}`;
  const cerca = bordas ? `<p class="leg-extra"><svg class="amostra" viewBox="0 0 30 16" aria-hidden="true"><g class="bordas t-perene"><line class="b-fora" x1="2" y1="4" x2="28" y2="4"/>
    <line class="b-dentro" x1="2" y1="12" x2="28" y2="12"/></g></svg>${U.esc(cercaTxt)}</p>` : "";
  const mesCtl = a ? `<div class="mes-controle">
      <button type="button" class="play" data-play aria-label="Passar os meses">${U.ic("tocar")}</button>
      <div class="mes-trilho" role="group" aria-label="Mês a mês em 2027">${chips}</div></div>` : "";
  const anos = `${p.anos[0]}–${p.anos[p.anos.length - 1]}`;
  const rotHtml = `${V.olhoFaixas ? "" : olho(OLHOS.faixas)}<h4>Por que esta ordem das faixas</h4>${ordem}<h4>Parte por parte</h4>${rotacao(ctx, V, lay)}`;
  const topo = `<div class="bloco-topo"><h3>Seu roçado visto de cima <span data-selo-heroi></span></h3>${botoesAno(p)}</div>`;
  const depois = `<p class="espaco" data-espaco></p>` + notasDoLado(ctx, V) + porQueLista(ctx, V, lay) + (V.olhoFaixas ? olho(OLHOS.faixas) : "")
    + terrenoVerMais(ctx, lay);
  // no celular o desenho já traz o nome de cada faixa: o mês a mês, a lista das partes e a rotação ficam num "ver mais" só
  // (aberto quando o mês a mês está ligado, para o redesenho não esconder o controle)
  if (est.compacto) {
    return `<section class="painel heroi" id="plantio-rocado">${controle(ctx, V)}${topo}
      <figure class="rocado-fig">${svgRocado(U, lay, W)}</figure>${cerca}${depois}
      <details class="ver-mais mes-a-mes"${est.modo === "mes" ? " open" : ""}><summary>${a ? `Ver mês a mês e a rotação ${anos}` : `Ver as partes e a rotação ${anos}`}</summary>
        ${mesCtl}${legenda}${U.verMais(rotHtml, `A rotação ${anos}, parte por parte`)}</details></section>`;
  }
  const rot = U.verMais(rotHtml, `Ver a rotação ${anos}, parte por parte`);
  return `<section class="painel heroi" id="plantio-rocado">${controle(ctx, V)}${topo}
    <div class="heroi-grade">
      <figure class="rocado-fig">${svgRocado(U, lay, W)}</figure>
      <div class="heroi-lado">${legenda}${cerca}</div>
    </div>
    ${mesCtl}
    ${depois}
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
      ? `: a ${U.esc(ult.parte)}, que aqui nunca tem gramínea, fica encostada no ${U.esc(curto(lay.bx.anos[0].cultura))} do baixio.`
      : `, nem no ${U.esc(curto(lay.bx.anos[0].cultura))} do baixio.`;
    else s += ".";
  } else if (lay.todasIguais) {
    s += `Aqui nenhuma ordem evita que gramínea encoste em gramínea: em qualquer uma das 6 ordens são ${lay.contatos} encontros em 3 anos ${sel}.`;
  } else {
    s += `Das 6 ordens possíveis, esta tem menos encontros de gramínea com gramínea nos 3 anos: ${lay.contatos}, contra ${lay.piorContatos} na pior ${sel}.`;
  }
  return s;
}

function pintarRocado(el, ctx, V, lay, meses) {
  const U = ctx.util, esc = U.esc, a = V.ag, p = V.plano;
  const mes = est.modo === "mes" ? meses[est.mes] : null, k = mes ? 0 : est.ano;
  const caixa = el.querySelector("#plantio-rocado");
  caixa.querySelectorAll("[data-ano]").forEach((b) => b.setAttribute("aria-pressed", String(!mes && +b.dataset.ano === k)));
  caixa.querySelectorAll("[data-mes]").forEach((b) => { b.classList.toggle("atual", !!mes && +b.dataset.mes === est.mes); b.classList.toggle("fora", est.ano !== 0 && !mes); });
  caixa.querySelector("[data-selo-heroi]").innerHTML = mes
    ? U.selo("suposicao", "desenho = suposição; datas de plantar do ZARC 2026/27 (medidas); crescendo e colher = janela + ciclo da cultura")
    : k === 0 ? U.selo("suposicao", supoe(U, lay) + "; culturas do plano para 2027")
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
      rot = `${f.letra} · ${curto(c.cultura)} · ${metros(U, f.larguraM)}`;
      if (k > 0) {
        const antes = f.plano.anos[k - 1].cultura;
        if (antes === c.cultura && c.cultura === "Mandioca") { tag = "reserva"; temReserva = true; }
        const de = antes === c.cultura ? null : lay.partes.find((q) => q.anos[k - 1].cultura === c.cultura);
        rot2 = `antes: ${curto(antes)}${de && !est.compacto ? ` · ${curto(c.cultura)} vem da ${de.parte.replace("Parte ", "")}` : ""}`;
      }
    }
    // A B C A B C: a 2ª faixa de cada parte só leva a letra (a cor e o ícone já dizem a cultura)
    if (lay.faixas.findIndex((x) => x.letra === f.letra) !== i) { rot = f.letra; rot2 = ""; }
    if (g.dataset.fino) { rot = ""; rot2 = ""; tag = ""; icone = ""; }
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
      if (q.parte === "Baixio") { const rz = estadoMes(a, "Baixio", mes, true); if (rz) extra += `<span class="leg-sub">${esc(curto(rz.cultura))} no meio do milho: ${ESTADO[rz.estado]}</span>`; }
      if (q.parte === "Bordas") extra += `<span class="leg-sub">na cerca</span>`;
      if (e.linha && e.linha.estacao > 2027) extra += `<span class="leg-sub">já é a safra ${e.linha.estacao}</span>`;
    } else {
      const c = q.anos[k], seg = q.parte === "Baixio" ? segundaBaixio(c, p) : null;
      cultura = seg ? `${c.cultura} + ${seg}` : c.cultura;
      tipo = c.tipo;
      direita = /^Parte/.test(q.parte) ? haTxt(U, lay.haParte) : q.parte === "Baixio" ? haTxt(U, lay.haBaixio) + (lay.incerto ? "?" : "") : "na cerca";
      if (k > 0 && q.anos[k - 1].cultura === c.cultura && c.cultura === "Mandioca") extra += `<span class="chip terra mini-chip">reserva</span>`;
    }
    itens.push(`<li class="${U.tipoCss(tipo)}"><span class="leg-ic">${U.ic(U.icCultura(cultura))}</span><span class="leg-l">${esc(L)}</span>
      <span class="leg-t"><b>${esc(cultura)}</b>${extra}</span><span class="leg-a">${esc(direita)}</span></li>`);
  }
  if (lay.reserva) itens.unshift(`<li class="t-perene"><span class="leg-ic">${U.ic(U.icCultura(lay.reserva.culturas[0]))}</span><span class="leg-l"></span>
      <span class="leg-t"><b>Já plantado: ${esc(listaE(lay.reserva.culturas.map(curto)))}</b><span class="leg-sub">fica como está, fora do giro</span></span>
      <span class="leg-a">${esc(haTxt(U, lay.reserva.ha))}</span></li>`);
  const ep = caixa.querySelector("[data-espaco]");
  if (ep) ep.innerHTML = espacoHtml(U, lay, k, p);
  caixa.querySelector("[data-lista]").innerHTML = itens.join("") + (temReserva && !mes
    ? `<li class="leg-nota">Reserva: a mandioca do ano anterior ainda está no chão.</li>` : "");
  // baixio: a 2ª planta (caupi, mucuna) só quando o motor põe; sem ela, todas as linhas são da 1ª
  const gb = caixa.querySelector("[data-bx]");
  if (gb) {
    const c = lay.bx.anos[k], seg = segundaBaixio(c, p);
    let tipo = c.tipo, estado = "ano", rot, rot2, duas = !!seg;
    if (mes) {
      const e = estadoMes(a, "Baixio", mes), rz = estadoMes(a, "Baixio", mes, true);
      tipo = e.tipo; estado = e.estado; duas = !!rz;
      rot = `Baixio · ${e.estado === "descanso" ? (e.palhada ? `palhada do ${curto(e.cultura)}` : "descanso") : `${curto(e.cultura)} · ${ESTADO[e.estado]}`}`;
      rot2 = rz ? `${curto(rz.cultura)} no meio do milho: ${ESTADO[rz.estado]}` : "";
      gb.querySelector("[data-milho]").setAttribute("class", `lin e-${estado}`);
      gb.querySelector("[data-caupi]").setAttribute("class", `lin caupi t-leguminosa e-${rz ? rz.estado : "ano"}`);
      gb.querySelector(".rot-ic").innerHTML = e.estado === "descanso" ? "" : U.IC[e.estado === "preparo" ? "enxada" : U.icCultura(e.cultura)];
    } else {
      rot = `Baixio${lay.incerto ? "?" : ""} · ${curto(c.cultura)}${seg ? ` + ${seg}` : ""} · ${metros(U, lay.profBaixio)}`;
      rot2 = lay.incerto ? "se você tiver baixio" : seg ? `linhas de ${curto(c.cultura)} e de ${seg} alternadas` : "";
      gb.querySelector("[data-milho]").setAttribute("class", "lin e-ano");
      gb.querySelector("[data-caupi]").setAttribute("class", "lin caupi t-leguminosa e-ano");
      gb.querySelector(".rot-ic").innerHTML = U.IC[U.icCultura(c.cultura)];
    }
    if (gb.dataset.fino) { rot = ""; rot2 = ""; gb.querySelector(".rot-ic").innerHTML = ""; }
    gb.setAttribute("class", `fx bx ${U.tipoCss(tipo)} e-${estado}${lay.incerto ? " incerto" : ""}`);
    linhasBaixio(gb, k, duas);
    gb.querySelector(".rot").textContent = rot;
    gb.querySelector(".rot2").textContent = rot2;
  }
  fundosRotulos(caixa);
  const gbord = caixa.querySelector("[data-bordas]");
  if (gbord) {
    const e = mes ? estadoMes(a, "Bordas", mes) : null;
    gbord.setAttribute("class", `bordas t-perene e-${e ? e.estado : "ano"}`);
    gbord.style.display = lay.bordas ? "" : "none"; // sem perene nas bordas (seu jeito sem palma): sem cerca no desenho
  }
}

// ------------------------------------------------------------------ "O que você ganha": Hoje → Melhorado → Ideal (extras/ideal.js)
const IDS = ["rs_tipico", "rs_el_nino", "quebra_10", "comida_kg", "raiz_kg", "forragem_t", "n_kg", "meses_coberto", "ponte_lagarta"];
const NOME_MAIS = { comida_kg: "grão", raiz_kg: "raiz", forragem_t: "gado", n_kg: "adubo", meses_coberto: "chão coberto", ponte_lagarta: "lagarta" };
const ROT_POR_ANO = new Set(["comida_kg", "raiz_kg", "forragem_t", "n_kg", "meses_coberto"]);
/** À vista: o dinheiro, a quebra e o adubo; no ideal "Guardar água", a comida do gado no lugar do adubo (é o ganho dele). */
const vistosDe = (pri, ideal) => ["rs_tipico", "rs_el_nino", "quebra_10", ideal && pri === "garantir" ? "forragem_t" : "n_kg"];
const valorTxt = (U, it) => textoItem(U, it); // o mesmo formato do Quanto rende (extras/ideal.js)
const valorDe = (b, id) => b?.itens?.find((i) => i.id === id)?.valor ?? null;
// o nome curto do que ele ganha fora do dinheiro ("ganha em comida do gado e adubo no chão")
const GANHO_NOME = { quebra_10: "menos quebra", forragem_t: "comida do gado", ponte_lagarta: "menos lagarta",
  n_kg: "adubo", comida_kg: "grão", raiz_kg: "raiz", meses_coberto: "chão coberto" };

/** O ganho de um lado numa linha curta, para o botão do controle: "+R$ 99 por ano" ou, sem ganho em R$, "quebra de 2 para 1 em 10". */
function ganhoCurto(U, H, B) {
  const t0 = valorDe(H, "rs_tipico"), t1 = valorDe(B, "rs_tipico"), q0 = valorDe(H, "quebra_10"), q1 = valorDe(B, "quebra_10");
  const out = [];
  if (t0 != null && t1 != null && t1 - t0 >= 50) out.push(`+${U.brl(t1 - t0)} por ano`);
  else if (q0 != null && q1 != null && q1 < q0) out.push(`quebra de ${q0} para ${q1} em 10`);
  return out[0] || ""; // uma linha só: o botão não cresce (o desenho fica no alto da tela)
}

/** Onde ele ganha com o plano à vista, comparado a hoje (até 3, nesta ordem), e onde perde (dito com franqueza, com o porquê). */
function ganhosDe(U, H, B, plano, ideal, M) {
  const d = (id, ref = H) => { const h = valorDe(ref, id), p = valorDe(B, id); return h === null || p === null ? null : { h, p, x: p - h }; };
  const REGRA = [
    ["rs_tipico", (o) => o.x >= 50 && `+${U.brl(o.x)} num ano normal`],
    ["quebra_10", (o) => o.p < o.h && `quebra: de ${o.h} para ${o.p} em 10 anos`],
    ["rs_el_nino", (o) => o.x >= 50 && `+${U.brl(o.x)} em 2027, ano de El Niño`],
    ["forragem_t", (o) => o.x >= 0.1 && `+${U.num(o.x, o.x < 10 ? 1 : 0)} t de comida do gado por ano`],
    ["ponte_lagarta", (o) => o.p > o.h && `caminho da lagarta cortado em ${o.p} de 3 anos`],
    ["n_kg", (o) => o.x >= 1 && `+${U.num(Math.round(o.x))} kg de adubo (nitrogênio) no chão por ano`],
    ["comida_kg", (o) => o.x >= 20 && `+${U.num(Math.round(o.x / 10) * 10)} kg de grão por ano`],
    ["raiz_kg", (o) => o.x >= 50 && `+${U.num(Math.round(o.x / 10) * 10)} kg de raiz de mandioca por ano`],
    ["meses_coberto", (o) => o.x >= 0.3 && `+${U.num(o.x, 1)} meses de chão coberto`],
  ];
  const todos = REGRA.map(([id, f]) => { const o = d(id); const t = o ? f(o) : null; return t ? { id, t } : null; }).filter(Boolean);
  const ganha = todos.slice(0, 3).map((x) => x.t);
  const foraDinheiro = todos.filter((x) => !/^rs_/.test(x.id)).map((x) => GANHO_NOME[x.id]);
  const perde = [], e = d("rs_el_nino"), t = d("rs_tipico");
  if (t && t.x <= -50) perde.push("num ano normal");
  if (e && e.x <= -50) perde.push("em 2027");
  const mandiocaNova = plano.faixas.some((f) => /^Parte /.test(f.parte) && f.anos[0].cultura === "Mandioca" && !f.anos[0].ja_no_chao);
  const fora = B?.itens?.find((i) => i.id === "rs_tipico")?.detalhe?.fora_rs || [];
  // a mandioca nova explica só a perda de 2027 (num ano normal ela já colhe)
  const porque = [perde.includes("em 2027") && !perde.includes("num ano normal") && mandiocaNova ? "a mandioca nova só colhe em 2028" : "",
    fora.length ? `${listaE(fora.map(curto))} ${fora.length > 1 ? "ficam" : "fica"} fora do R$` : ""].filter(Boolean); // o porquê vai no balão do selo
  let perdeTxt = "";
  if (ideal && t && t.x <= -50) { // o ideal daqui não dá mais dinheiro que hoje: dizer em que ele ganha
    // os ganhos fora do dinheiro já estão na lista de cima; sem lista, eles vão aqui
    perdeTxt = `O ideal daqui não dá mais dinheiro${!ganha.length && foraDinheiro.length ? `: ganha em ${listaE(foraDinheiro.slice(0, 3))}` : ""}${porque.length ? `; ${porque.join("; ")}` : ""}.`;
  } else if (perde.length) perdeTxt = `Sobra menos que hoje ${listaE(perde)}${porque.length ? `: ${porque.join("; ")}` : ""}.`;
  // o ideal que perde para o seu jeito melhorado em 2027 (ex.: "Guardar água"): o que ele dá em troca
  let vsM = "";
  if (ideal && M && !perdeTxt) {
    const m = d("rs_el_nino", M), f = d("forragem_t", M);
    if (m && m.x <= -50) vsM = `${U.brl(-m.x)} a menos que o seu jeito melhorado em 2027${f && f.x >= 0.1 ? `, com +${U.num(f.x, f.x < 10 ? 1 : 0)} t de comida do gado por ano` : ""}.`;
  }
  return { ganha, perdeTxt, vsM, t };
}

/** Sob o desenho: a distância das carreiras e das covas de cada parte no ano à vista ("A e C caupi 80 × 50 cm · B milho 100 × 50 cm"),
 *  com o selo do espaçamento recomendado (dados/agronomia.json). Sem os dados, nada. */
function espacoHtml(U, lay, k, p) {
  const agro = agronomia();
  if (!agro) return "";
  let ct;
  try { ct = contasTerreno(lay, k, agro, p); } catch (_) { return ""; }
  const grupos = [], fontes = new Set();
  const med = (el, ec) => (el >= 1 && ec >= 1 ? `${U.num(el, el % 1 ? 1 : 0)} × ${U.num(ec, ec % 1 ? 1 : 0)} m` : `${Math.round(el * 100)} × ${Math.round(ec * 100)} cm`);
  for (const l of ct.linhas) {
    if (l.id === "Perene" || l.id === "Bordas" || l.pousio || l.nada) continue;
    const it = l.itens.find((i) => i.papel === "principal" && i.covas && i.entre_linhas_m && i.entre_covas_m);
    if (!it) continue;
    if (it.dados?.fonte) fontes.add(it.dados.fonte.split(",")[0]);
    const quem = l.id === "Baixio" ? "baixio" : l.letra, txt = `${curto(l.cultura)} ${med(it.entre_linhas_m, it.entre_covas_m)}`;
    const g = grupos.find((x) => x.txt === txt);
    if (g) g.quem.push(quem); else grupos.push({ quem: [quem], txt });
  }
  if (!grupos.length) return "";
  return `<b>Carreira × cova:</b> ${U.esc(grupos.map((g) => `${listaE(g.quem)} ${g.txt}`).join(" · "))} ${U.selo("suposicao",
    `espaçamento recomendado de sequeiro, não medido no seu roçado (dados/agronomia.json: ${[...fontes].join("; ")}); o detalhe, as sementes e o zoom de 5 × 5 m estão em "Seu terreno"`)}`;
}

function blocoGanha(ctx, V) {
  const U = ctx.util, esc = U.esc, c3 = V.c3;
  const H = c3?.hoje?.beneficios, M = c3?.melhor?.beneficios, I = c3?.ideal?.beneficios;
  if (!H || !M) return "";
  const ideal = V.E.tipo === "ideal", B = ideal ? I : M, atual = ideal ? 2 : 1;
  const { ganha, perdeTxt, vsM, t } = B ? ganhosDe(U, H, B, V.plano, ideal, M) : { ganha: [], perdeTxt: "", vsM: "", t: null };
  const rsB = B?.itens?.find((i) => i.id === "rs_tipico");
  const semRs = valorDe(B, "rs_tipico") === null ? rsB?.fonte || "" : "";
  const parcial = rsB?.detalhe?.parcial || [];
  const semGiro = !!B?.rs?.semGiro;
  const informado = c3.hoje.plano?.informado;
  const cols = [H, M, I];
  const linha = (id) => {
    const its = cols.map((b) => b?.itens?.find((i) => i.id === id) || null);
    const ref = its[atual] || its[1] || its[2] || its[0]; // o selo é o da coluna escolhida (projeção); o "medido" do hoje vai no balão
    if (!ref || its.every((i) => i?.valor === 0)) return ""; // zero nas 3 colunas (ex.: comida do gado sem forrageira): nada a comparar
    if (id === "raiz_kg" && its.every((i) => !i?.valor)) return ""; // sem mandioca em nenhum dos 3
    const fonte = ref.fonte + (its[0]?.selo === "medido" && ref !== its[0] ? `. A coluna Hoje é medida: ${its[0].fonte}` : "");
    return `<div class="gn-it" role="row"><span class="gn-rot" role="rowheader">${esc(ref.rotulo)}${ROT_POR_ANO.has(id) ? " por ano" : ""} ${U.selo(ref.selo, fonte)}</span>
      ${its.map((it, j) => {
        const tx = valorTxt(U, it);
        return `<span class="gn-v${j === atual ? " atual" : ""}${tx ? "" : " nm"}" role="cell"${tx ? "" : ` title="${esc(it?.fonte || "não medido")}"`}>${tx ? esc(tx) : "não medido"}</span>`;
      }).join("")}</div>`;
  };
  const nomeIdeal = NOME_PRIORIDADE[c3.prioridade] || "";
  const cab = `<div class="gn-cab" role="row"><span class="gn-c0" role="columnheader"></span><span class="gn-h" role="columnheader">Hoje${informado ? "" : "<small>o comum daqui</small>"}</span>
        <span class="gn-h${atual === 1 ? " atual" : ""}" role="columnheader">Melhorado</span>
        <span class="gn-h${atual === 2 ? " atual" : ""}" role="columnheader">Ideal<small>${esc(nomeIdeal)}</small></span></div>`;
  const tabela = (html) => `<div class="gn-tab" role="table" aria-label="Hoje, seu jeito melhorado e o ideal">${cab}${html}</div>`;
  // à vista: o dinheiro, a quebra e o adubo (ou a comida do gado, no "Guardar água"); os outros num "ver mais" logo abaixo
  const vistosIds = vistosDe(c3.prioridade, ideal);
  const vistos = vistosIds.map(linha).join("");
  const mais = IDS.filter((id) => !vistosIds.includes(id)).map((id) => [id, linha(id)]).filter(([, h]) => h);
  const info = B?.rs?.info || H.rs?.info;
  const comoHoje = informado ? "o que você marcou em Sua roça (a mandioca já no chão, metade colhendo por ano)"
    : "o jeito comum daqui (milho e feijão), porque você não marcou o que planta";
  const agro = (B?.rs?.agro || []).length > 0;
  const detalhe = `<p><b>Hoje</b> = ${comoHoje}. <b>Melhorado</b> = só as suas culturas, em faixas que giram. <b>Ideal</b> = ${esc(nomeIdeal)},
      com tudo o que sabemos do lugar.</p>
    <p>As 3 colunas usam a mesma conta e os mesmos anos${info ? ` do IBGE (${info.ano0}–${info.ano1})` : ""}: a sobra é a colheita a preço da região menos
      a semente; a mão de obra da família não entra. O ano normal é a média de 2028 e 2029 (a mandioca fica 2 anos no chão); 2027 é o que
      sobrou em pelo menos 3 dos 4 El Niños fortes já vistos. A soma de 2027 a 2029 está em Quanto rende.</p>
    <ul class="gn-fontes">${IDS.map((id) => { const it = B?.itens?.find((i) => i.id === id) || H.itens.find((i) => i.id === id);
      return it ? `<li><b>${esc(it.rotulo)}:</b> ${esc(it.fonte)}</li>` : ""; }).join("")}</ul>`;
  // "Quase igual a hoje" só quando não há ganho nem perda e a sobra fica perto (±R$ 50); "o ganho maior vem com o ideal" só quando o
  // ideal de fato passa o hoje e o melhorado em algum número de R$ ou de quebra
  const vI = (id) => valorDe(I, id), vH = (id) => valorDe(H, id), vM = (id) => valorDe(M, id);
  const idealMaior = ["rs_tipico", "rs_el_nino"].some((id) => vI(id) != null && vH(id) != null && vM(id) != null && vI(id) > Math.max(vH(id), vM(id)) + 50)
    || (vI("quebra_10") != null && vH("quebra_10") != null && vM("quebra_10") != null && vI("quebra_10") < Math.min(vH("quebra_10"), vM("quebra_10")));
  const quase = !ganha.length && !perdeTxt && !semGiro && !semRs && (!t || Math.abs(t.x) < 50);
  const frase = ganha.length ? `<ul class="gn-ganhos">${ganha.map((g) => `<li>${U.ic("ok")}<span>${esc(g)}</span></li>`).join("")}</ul>`
    : quase ? `<p class="gn-quase">Quase igual a hoje${!ideal && idealMaior ? ": o ganho maior vem com o ideal." : "."}</p>` : "";
  return `<section class="painel ganha" id="plantio-ganha" data-ganha>
    <h3>O que você ganha</h3>
    <p class="gn-sub">${ideal ? "O ideal" : "Melhorado"}, comparado a hoje:</p>
    ${frase}
    ${perdeTxt ? `<p class="gn-perde">${U.ic("alerta")}<span>${esc(perdeTxt)}</span></p>` : ""}
    ${vsM ? `<p class="gn-perde">${U.ic("info")}<span>${esc(vsM)}</span></p>` : ""}
    ${semRs ? `<p class="gn-perde">${U.ic("info")}<span>${esc(semRs.replace(/^não medido: /, "Sem R$: ").replace(/^./, (x) => x.toUpperCase()))}.</span></p>` : ""}
    ${parcial.length && !semRs ? `<p class="gn-perde">${U.ic("info")}<span>Conta sem ${esc(listaE(parcial.map((x) => (x === "Mandioca" ? "a mandioca" : `o ${x.toLowerCase()}`))))}: o IBGE não tem a série aqui.</span></p>` : ""}
    ${agro ? `<p class="gn-perde">${U.ic("info")}<span>Aqui o IBGE mistura lavoura grande: os R$ só comparam.</span></p>` : ""}
    ${tabela(vistos)}
    ${mais.length ? U.verMais(tabela(mais.map(([, h]) => h).join("")), `Mais ${mais.length}: ${listaE(mais.map(([id]) => NOME_MAIS[id]))}`) : ""}
    ${U.verMais(detalhe)}
  </section>`;
}

// ------------------------------------------------------------------ o que fazer e quando
const TERRA_ROT = { nao_sei: "não sei", arenosa: "de areia", mista: "misturada", barro: "de barro" };
const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
const artigo = (c) => (/^(mandioca|palma|mamona|mucuna|gliric)/.test(norm(c)) ? "a" : "o");

/** Terra "não sei": as datas são as que servem nos solos zoneados. Para cada cultura do plano à vista sem janela na areia
 *  (cardapio[].por_solo sem o solo 1 ou o AD2, cód. 12), uma linha honesta. Ex.: milho em Piritiba. O seu jeito, melhorado, já tem só as
 *  culturas que ele marcou (o "feijão" de Sua roça é o caupi; o feijão comum é outra chave, extras/culturas.js). */
function avisoTerra(ctx, plano) {
  if (ctx.ef.terra !== "nao_sei") return "";
  const U = ctx.util, card = ctx.r.cardapio || [], nomes = new Set();
  for (const f of plano?.faixas || []) for (const c of f.anos) for (const n of String(c.cultura).split(/\s*\+\s*/)) nomes.add(norm(n));
  const temAreia = (c) => c.por_solo.some((s) => [1, 12].includes(+s.cod_solo) && [s.risco20, s.risco30, s.risco40].some((x) => x && x !== "nenhum"));
  const sem = card.filter((c) => Array.isArray(c.por_solo) && c.por_solo.length && !temAreia(c)
    && [...nomes].some((n) => norm(c.cultura) === n || norm(c.cultura).startsWith(n + " ")));
  // sem a sigla na frente (o ZARC fica no selo do bloco), com o que fazer, e numa linha só (Petrolina, ideal: caupi e os 2 sorgos)
  if (!sem.length) return "";
  const nomesSem = sem.map((c) => curto(c.cultura));
  const quem = nomesSem.length === 1 ? `${artigo(sem[0].cultura)} ${nomesSem[0]} não tem` : `${listaE(nomesSem)} não têm`;
  return `<ul class="aviso-terra"><li>${U.ic("areia")}<span>Em terra de areia, ${U.esc(quem)} data segura aqui: pergunte ao técnico.</span></li></ul>`;
}

const temMetade = (V) => !!V.ag && /metade/i.test(V.plano?.interruptor || ""); // o "seu olho" da metade guardada

function blocoTempo(ctx, V) {
  const U = ctx.util;
  if (!V.ag) return "";
  return `<section class="painel" id="plantio-tempo">
    <h3>O que fazer e quando ${U.selo("medido", "datas de plantar da tábua oficial (ZARC 2026/27); os cartões marcados como suposição são estimados")}</h3>
    <a class="chip terra-chip" href="${ctx.link(2)}" data-editar="terra">${U.ic(ctx.ef.terra === "barro" ? "barro" : "areia")}<span>Sua terra:
      ${TERRA_ROT[ctx.ef.terra] || "não sei"} · <u>mudar</u></span></a>
    ${avisoTerra(ctx, V.plano)}
    ${linhaDoTempo(ctx, V.ag)}
    <p class="sequeiro">${U.ic("chuva")}<span>Datas para roça de chuva. Molha a roça? Fale com o técnico.</span></p>
    ${temMetade(V) ? olho(OLHOS.metade) : ""}
    ${U.verMais(calendarioCompleto(ctx, V.ag), "Ver o calendário completo")}
  </section>`;
}

// ------------------------------------------------------------------ por que faixas e não blocos (ideia do Vicente)
function blocoFaixas(ctx, V, lay) {
  const U = ctx.util, p = V.plano;
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
      ${U.selo("suposicao", "calculado no navegador sobre o desenho (" + supoe(U, lay) + "); grade de ~5 m, 4 vizinhos")}</p>
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
function porQue(ctx, V, lay) {
  const U = ctx.util;
  return `<section class="painel plantio-porque" id="plantio-porque"><h3>Por que este plano</h3>
    ${U.verMais(U.extra("vulnerabilidade", { vista: "agua", painel: false }), "Onde o seu roçado sofre mais")}
    ${U.verMais(blocoFaixas(ctx, V, lay), "Por que em faixas: a praga anda menos")}
    ${U.verMais(U.extra("saude_solo", { titulo: false }), "O que cada planta faz pelo solo")}
  </section>`;
}

/** A grade do roçado em escala (larg × comp em metros, como desenho.js): faixas ou blocos, com a gramínea e onde a praga chegou. */
function svgMini(U, lay, gr, alcance) {
  const { linhas, nc, largCol, gram } = gr;
  const t = (v) => v.toFixed(2), L = lay.larg || lay.lado, C = lay.comp || lay.lado, M = Math.max(L, C);
  let h = `<svg viewBox="0 0 ${t(L)} ${t(C)}" class="mini-grade" role="img" aria-label="Grade do roçado">`;
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
  const sw = t(M / 110);
  if (gr.modo === "faixas") lay.faixas.slice(1).forEach((f) => { h += `<line class="divisa" x1="0" y1="${t(f.y0)}" x2="${t(L)}" y2="${t(f.y0)}" stroke-width="${sw}"/>`; });
  else for (let j = 1; j < lay.partes.length; j++) { const x = t(L * j / lay.partes.length); h += `<line class="divisa" x1="${x}" y1="0" x2="${x}" y2="${t(lay.profAlto)}" stroke-width="${sw}"/>`; }
  if (lay.temBaixio) h += `<line class="divisa bx" x1="0" y1="${t(lay.profAlto)}" x2="${t(L)}" y2="${t(lay.profAlto)}" stroke-width="${t(M / 70)}"/>`;
  return h + "</svg>";
}

/** O veredito grande de cada desenho: quantos pedaços de milho e sorgo e se a praga atravessa do alto ao baixo. */
function veredito(U, lay, g) {
  if (g.p === 0) return `<span class="chip">${U.ic("ok")} sem milho nem sorgo</span>`;
  if (g.desce) return `<span class="chip terra">${U.ic("alerta")} ${g.blocos === 1 ? "1 bloco só: a praga atravessa" : "a praga desce até embaixo"}</span>`;
  if (g.blocos > 1) return `<span class="chip verde">${U.ic("escudo")} ${g.blocos} pedaços: a praga para</span>`;
  if (lay.temBaixio && Math.abs(g.maior - lay.frac) < 1e-6) return `<span class="chip">${U.ic("ok")} só o ${U.esc(curto(lay.bx.anos[0].cultura))} do baixio</span>`;
  return `<span class="chip ambar">${U.ic("alerta")} 1 bloco grande: não desce, mas é grande</span>`;
}

function pintarFaixas(el, ctx, V, lay, conect) {
  const U = ctx.util, p = V.plano;
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
function avisoGramineas(ctx, V, lay, conect) {
  const U = ctx.util, p = V.plano;
  const acima = p.anos.filter((_, j) => conect[j].faixas.p > LIMIAR_SITIO);
  const pontes = [];
  for (const q of lay.partes) for (let j = 0; j + 1 < p.anos.length; j++)
    if (ehGram(q.anos[j].cultura) && ehGram(q.anos[j + 1].cultura)) pontes.push(`${q.parte} (${p.anos[j]}→${p.anos[j + 1]})`);
  if (!acima.length && !pontes.length) return "";
  const pMax = Math.max(...p.anos.map((_, j) => conect[j].faixas.p));
  const repete = pontes.length && lay.partes.every((q) => q.anos.every((c) => c.cultura === q.anos[0].cultura));
  const frase = acima.length ? `Aqui milho e sorgo ficam com ${U.emDez(pMax)} partes do roçado.`
    : repete ? "Aqui o mesmo capim volta ao mesmo lugar todo ano." : "Aqui o sorgo repete no mesmo lugar dois anos seguidos.";
  return `<div class="aviso-gram">${U.faixa("alerta", "terra", frase)}
    <p class="pequeno">Fale com o técnico: trocar um ${repete ? "ano de milho" : "sorgo"} por feijão, palma ou descanso.${pontes.length ? ` Repete em: ${pontes.join("; ")}.` : ""}
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
function rotacao(ctx, V, lay) {
  const U = ctx.util, esc = U.esc, p = V.plano;
  const area = (f) => (/^Parte/.test(f.parte) ? `${haTxt(U, lay.haParte)} ${U.selo("suposicao", supoe(U, lay))}`
    : f.parte === "Baixio" ? `${haTxt(U, lay.haBaixio)}${lay.incerto ? " (se tiver)" : ""} ${U.selo("suposicao", "fração do baixio da sua resposta; \"não sei\" = 1/3")}`
      : f.parte === "Bordas" ? "no perímetro, sem tirar área" : "");
  const seloAno = (a, k) => `${a} ${k === 0 ? U.selo("medido", "janelas do ZARC 2026/27 nos textos de cada cultura")
    : U.selo("projecao", "a rotação segue; as datas repetem o ZARC 2026/27")}`;
  const cel = (c) => `<div class="rot-cel ${U.tipoCss(c.tipo)}"><b>${esc(c.cultura)}</b><span>${esc(falaTexto(c.texto))}${/estimad/.test(c.texto)
    ? " " + U.selo("suposicao", "janela estimada pelo início típico da chuva (IMERG); sem ZARC aqui") : ""}</span></div>`;
  let h = `<p>Cada parte recebe uma cultura por ano e, no ano seguinte, a cultura muda de parte. A leguminosa deixa nitrogênio para o cereal que
    vem depois${p.faixas.some((f) => f.anos.some((c) => c.cultura === "Mandioca")) ? ", e fica mandioca no chão como reserva para um ano ruim" : ""}.</p>
    ${p.modelo_ne ? `<p class="aviso">Fora do Nordeste usamos o modelo do sertão: as culturas são do lugar, mas as datas, as bordas e o alerta do ano foram calibrados no NE.</p>` : ""}
    <div class="tab-rot-caixa"><table class="tab-rot"><tr><th>Parte do roçado</th>${p.anos.map((a, k) => `<th>${seloAno(a, k)}</th>`).join("")}</tr>`;
  for (const f of p.faixas) {
    if (f.parte === "Baixio" && !lay.temBaixio) continue;
    h += `<tr><td><b>${esc(f.parte)}</b><br><span class="pequeno">${area(f)}</span></td>${f.anos.map((c, k) => `<td><span class="ano-rot">${seloAno(p.anos[k], k)}</span>${cel(c)}</td>`).join("")}</tr>
      <tr class="porque"><td colspan="${p.anos.length + 1}">Por quê: ${esc(falaTexto(p.por_que_de?.[f.parte] ?? f.por_que))}</td></tr>`;
  }
  h += `</table></div>`;
  if (p.interruptor) h += `<p class="aviso"><b>O alerta do ano:</b> ${esc(falaTexto(p.interruptor))}</p>`;
  h += `<h4>As regras da rotação e a evidência de cada uma</h4>
    ${(p.principios || []).map((c) => `<div class="ev"><div class="ev-regra">${esc(c.regra || c.configuracao)}${c.irrigado ? " (irrigado)" : ""}</div>
      <div class="pequeno">${c.efeito ? `<b>${esc(c.efeito)}</b> · ` : ""}grau ${esc(c.grau)}·${esc(c.transferencia)} ${esc(c.rotulo_transferencia)} · ${esc(c.referencia)}${c.lugar ? " · " + esc(c.lugar) : ""}${c.doi ? ` · <a href="https://doi.org/${esc(c.doi)}" target="_blank" rel="noopener">doi</a>` : ""}</div></div>`).join("")}
    <h4>Notas</h4><ul class="notas">${(p.notas || []).map((n) => `<li>${esc(falaTexto(n))}</li>`).join("")}</ul>`;
  return h;
}

// ------------------------------------------------------------------ passo
export default {
  id: "plantio",
  titulo: "O plano",
  async render(el, ctx) {
    pararTudo();
    const U = ctx.util, r = ctx.r;
    if (est.cod !== ctx.cod) Object.assign(est, { cod: ctx.cod, ano: 0, modo: "ano", mes: null, terreno: false, terrenoTocado: false, ancora: null });
    // com as medidas do terreno respondidas, "Seu terreno" abre sozinho (até a pessoa fechar)
    if (!est.terrenoTocado) est.terreno = !!(ctx.ef.larg && ctx.ef.comp);
    // redesenho por um toque (lado, prioridade): sem a animação de entrada da casca, a tela só troca, sem piscar nem descer 10 px
    el.classList.toggle("sem-entrada", !ctx.entrou);
    const E = r.plano ? escolhido(r, ctx.resp, ctx.ef) : null;
    if (!E?.plano) {
      el.innerHTML = abertura() + `<section class="painel"><p>Sem plano para este ponto (sem dado de terra).</p></section>`;
      return;
    }
    // o plano à vista e a agenda dele; os objetos do motor são guardados por r e respostas: só leitura (ideal.js)
    const plano = E.plano, ag = agendaDoPlano(r.agenda, E.linhas);
    let c3 = null;
    try { c3 = comparar3(r, ctx.resp, ctx.ef, E.prioridade); } catch (e) { console.error("comparar3:", e); }
    const V = { E, plano, ag, c3, olhoFaixas: false, redesenharTerreno: null };
    V.olhoFaixas = !temMetade(V); // 1 "seu olho" à vista sempre: o da metade guardada (calendário) ou o das faixas (sob o desenho)
    const lay = montar(plano, ctx.ef);
    const meses = listaMeses(ag);
    if (est.mes === null || est.mes >= meses.length) {
      const hoje = ag ? ag.hoje : "";
      est.mes = Math.max(0, meses.findIndex((m) => hoje >= m.ini && hoje <= m.fim));
    }
    if (!ag) est.modo = "ano";
    if (est.ano >= plano.anos.length) est.ano = 0;
    const conect = plano.anos.map((_, k) => ({ blocos: { ...grade(lay, k, "blocos"), modo: "blocos" }, faixas: { ...grade(lay, k, "faixas"), modo: "faixas" } }));
    const W = Math.round(Math.min(640, Math.max(300, (window.innerWidth || 800) - 66)));
    est.compacto = W < 420;
    el.innerHTML = abertura() + faixaAgora(ctx, ag) + heroi(ctx, V, lay, meses, W) + blocoGanha(ctx, V) + blocoTempo(ctx, V) + porQue(ctx, V, lay);
    el.querySelector("[data-aviso-gram]").innerHTML = avisoGramineas(ctx, V, lay, conect);

    // o controle de 2 lados (grava `plano`) e "O que vale mais para você?" (grava `prioridade`): sem nova chamada à API
    const ancorar = (b) => { est.ancora = { sel: b.dataset.lado ? `[data-lado="${b.dataset.lado}"]` : `[data-prio="${b.dataset.prio}"]`, top: b.getBoundingClientRect().top }; };
    el.querySelectorAll("[data-lado]").forEach((b) => b.addEventListener("click", () => {
      const v = b.dataset.lado === "ideal" ? "ideal" : "";
      if ((ctx.resp.plano || "") === v) return;
      ancorar(b);
      ctx.set({ plano: v });
    }));
    el.querySelectorAll("[data-prio]").forEach((b) => b.addEventListener("click", () => {
      const p = PRIO.find(([k]) => k === b.dataset.prio)?.[1];
      if (!p || (ctx.resp.prioridade === p && ctx.resp.plano === "ideal")) return;
      ancorar(b);
      ctx.set({ prioridade: p, plano: "ideal" });
    }));

    const pintar = () => { pintarRocado(el, ctx, V, lay, meses); pintarFaixas(el, ctx, V, lay, conect); };
    const play = el.querySelector("[data-play]");
    const parar = () => { clearInterval(est.relogio); est.relogio = null; if (play) { play.innerHTML = U.ic("tocar"); play.classList.remove("tocando"); } };
    el.querySelectorAll("[data-ano]").forEach((b) => b.addEventListener("click", () => {
      parar(); est.ano = +b.dataset.ano; est.modo = "ano"; pintar(); V.redesenharTerreno?.();
    }));
    el.querySelectorAll("[data-mes]").forEach((b) => b.addEventListener("click", () => {
      parar(); const mudouAno = est.ano !== 0; est.ano = 0; est.modo = "mes"; est.mes = +b.dataset.mes; pintar(); if (mudouAno) V.redesenharTerreno?.();
    }));
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
        pintarRocado(el, ctx, V, lay, meses);
      }, 1100);
    });
    el.querySelector("[data-foco]").addEventListener("click", () => animarFoco(el, ctx, lay, conect));
    ligarCalendario(el, ctx, ag);
    pintar();
    // os extras de "Por que este plano" olham o plano à vista (vulnerabilidade e saude_solo leem ctx.r.plano)
    const ctxP = { ...ctx, r: { ...r, plano, agenda: ag } };
    const terreno = ligarTerreno(el, ctx, V);
    await Promise.all([U.montarExtras(el, ctxP), terreno ? Promise.race([terreno, new Promise((ok) => setTimeout(ok, 700))]) : null]);
    // roca.js põe o passo na tela logo depois do render: aí o texto já tem medida, e o controle tocado volta ao mesmo lugar da tela
    requestAnimationFrame(() => {
      fundosRotulos(el);
      const a = est.ancora;
      est.ancora = null;
      const b = a && el.isConnected ? el.querySelector(a.sel) : null;
      if (b) window.scrollBy(0, b.getBoundingClientRect().top - a.top);
    });
  },
};
