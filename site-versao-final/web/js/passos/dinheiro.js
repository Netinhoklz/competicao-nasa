// QUADRA, passo 4 "Quanto rende": o retorno do plano de rotação, refeito nos anos que já aconteceram no município.
// Visual v2 (LEIA-ME.md, "Visual e texto"): pouco texto na frente; método, fórmulas e ressalvas no "Ver como calculamos".
// Método: analise/financeiro.md (seções 2, 4 e 6); decisões 7 e 9 do PLANO_INTEGRACAO.md.
// Contas em js/passos/dinheiro/calculo.js; gráficos em js/passos/dinheiro/graficos.js.
import * as C from "./dinheiro/calculo.js";
import * as G from "./dinheiro/graficos.js";
import { termo } from "../extras/glossario.js";
import { olho, OLHOS } from "../extras/voce_decide.js";
// "Hoje → melhor → ideal" (extras/hoje_ideal.js): o jeito de hoje informado em "Sua roça" entra no lugar do milho + feijão fixo
import HI, { comHoje, lerHoje } from "../extras/hoje_ideal.js";
// Extra (js/extras/cenarios.js, montado por U.montarExtras): "O que vale mais para você?", as abas dos jeitos de girar o roçado, que
// gravam a prioridade (pontos 8 e 9). Ordem (analise/fluxo/00_FLUXO_FINAL.md, 3.1): título + o que a conta supõe → Hoje, melhor e ideal →
// prioridade → "Ajustar a conta" e os "ver mais" (El Niño, caixa, paga o gasto, como calculamos). Nenhum controle antes do número.
// "Seu olho" (ponto 16): o preço da raiz e a conta da família ficam no "Ajustar a conta"; com lavoura grande no IBGE, à vista.

const { rs, faixaRs } = G;
const SEQ = "3.136 combinações de anos já vistos aqui (2027 entre os 4 El Niños fortes; 2028 e 2029 entre os 28 anos do IBGE), todas contadas";
const FONTE_PAM = "IBGE PAM 1998–2025: rendimento por ha plantado × preço de referência do município, em R$ de 2025 (IPCA)";
const FONTE_CONAB = "CONAB, custos de produção do NE (semente e desembolso), R$ de 2025";
const SUP_AREA = "Partes A, B e C do mesmo tamanho; bordas não tiram área; baixio = metade milho + metade caupi; forragem sem R$";
const CUSTO_TXT = { semente: "só a semente", desembolso: "semente, trator, adubo e diária" };
const raizTxt = (uf) => ({ municipio: "daqui", uf_mediana: `comum no ${uf}`, uf_p25: `baixo no ${uf}` });

const vezes = (k, n, unid = "") => `${k} de ${n}${unid ? " " + unid : ""}`;
/** Largura útil do painel (px): os gráficos desenham 1:1 e só rolam de lado quando não cabem (celular). */
const largura = (min) => {
  const w = globalThis.innerWidth || 1000;
  return Math.round(Math.max(min, Math.min(1120, w) - (w <= 760 ? 66 : 106)));
};
const rolar = (svg, w) => `<div class="rola"><div class="rola-dentro" style="min-width:${w}px">${svg}</div></div>`;
const seg = (chave, atual, ops) => `<div class="seg" role="group">${ops.map(([v, t, s]) =>
  `<button type="button" data-set="${chave}=${v}" class="${v === atual ? "on" : ""}" aria-pressed="${v === atual}">${t}${s ? `<small>${s}</small>` : ""}</button>`).join("")}</div>`;
const rotulo = (U, icone, texto, selo = "") => `<div class="rot-bloco">${U.ic(icone)}<span>${texto} ${selo}</span></div>`;
const chave = (cls) => `<i class="chave m-${cls}"></i>`;

export default {
  id: "dinheiro",
  titulo: "Quanto rende",
  async render(el, ctx) {
    const { r, ef, util: U } = ctx;
    const fin = r.financeiro, mun = r.local.municipio;
    const abertos = abertosAntes(el, ctx);
    const jeitos = r.plano ? U.extra("cenarios") : "";
    const m = comHoje(C.montar(r, ef), r, ef, ctx.resp.hoje || "");
    const pr = fin?.precos_raiz || {};
    const temMand = !!m.usadas?.includes("Mandioca");
    let raiz = ef.raiz, preco = pr[raiz];
    if (!(preco > 0)) { raiz = "municipio"; preco = pr.municipio ?? m.precoRefMand; }
    const mult = m.precoRefMand && preco ? preco / m.precoRefMand : 1;
    const nivel = ef.custo === "desembolso" ? "desembolso" : "semente";
    // a linha do que a conta supõe (à vista, sob o título); "ajustar" abre o "Ajustar a conta"
    const raizVis = temMand && preco > 0 && !m.falta?.includes("Mandioca"); // sem a série da mandioca, o preço da raiz não pesa
    const supoe = `<span class="conta-com">Conta com: ${CUSTO_TXT[nivel]}${raizVis ? ` · raiz a R$ ${U.num(preco, 2)}/kg (${raizTxt(r.local.uf)[raiz]})` : ""} ·
      <button type="button" class="link-ajustar" data-abrir="ajustar-conta">ajustar</button>
      ${U.selo("suposicao", `o que a conta supõe quando você não diz: custo da CONAB${raizVis ? "; preço da raiz do IBGE (2016–2025)" : ""}`)}</span>`;
    const ajustar = `<details class="ver-mais" id="ajustar-conta"><summary>Ajustar a conta</summary>${ajustarHtml(ctx, pr, raiz, nivel, raizVis)}</details>`;
    const hiOp = { modo: "comparacao", linkMudar: ctx.link(2), semTitulo: true, ruim: termo("em_dez", "1 em 10"), olhoAgro: OLHOS.agro };
    const desenharHi = async () => {
      await HI.render(el.querySelector(".hi-slot"), ctx, { ...hiOp, detalhesEm: el.querySelector(".hi-detalhes") });
      await U.montarExtras(el, ctx);
      reabrir(el, abertos);
    };

    // sem a série do plano: o Hoje → melhor → ideal mostra o que dá (com o aviso dele) e o resto vai para o "ver como calculamos"
    if (!m.ok) {
      const [h1, eco, apoio] = fin ? ["Hoje, melhor e ideal.", "Do seu jeito ao plano completo.", supoe]
        : ["Ainda não dá para fazer a conta aqui.", "Falta a série do IBGE.", `O IBGE não tem anos suficientes das culturas do plano em ${U.esc(mun)}.`];
      el.innerHTML = abertura(h1, eco, apoio) + `<div class="hi-slot"></div>` + jeitos +
        `<section class="painel mais-conta">${fin ? ajustar : ""}${U.verMais(`<div class="hi-detalhes hoje-ideal"></div>${semConta(m, fin, U)}`, "Ver como calculamos")}</section>`;
      ligar(el, ctx);
      await desenharHi();
      return;
    }

    const t = C.calcular(m, nivel, mult);
    const tS = nivel === "semente" ? t : C.calcular(m, "semente", mult);
    const tD = nivel === "desembolso" ? t : C.calcular(m, "desembolso", mult);
    const ap = (html) => (m.agro.length ? `<div class="apagado">${html}</div>` : html);
    const mais = `<section class="painel mais-conta">${ajustar}
      ${U.verMais(ap(elNinoHtml(ctx, m, t, nivel, mult)), "Se 2027 for como os El Niños fortes")}
      ${U.verMais(ap(caixaHtml(ctx, m, t)), "Quando o dinheiro entra")}
      ${U.verMais(ap(termoHtml(ctx, tS, tD)), "A colheita paga o gasto?")}
      ${U.verMais(`<div class="hi-detalhes hoje-ideal"></div>${replayHtml(ctx, m, nivel, mult, preco, temMand)}${detalhesHtml(ctx, m, fin, t, nivel, mult, preco)}`, "Ver como calculamos")}
    </section>`;
    el.innerHTML = abertura("Hoje, melhor e ideal.", "Do seu jeito ao plano completo.", supoe) + `<div class="hi-slot"></div>` +
      avisosHtml(ctx, m) + jeitos + mais;
    ligar(el, ctx);
    ligarCaixa(el, t);
    await desenharHi();
  },
};

const abertura = (h1, eco, apoio) => `<div class="titulo-passo"><p class="kicker">Quanto rende</p>
  <h1>${h1}<span class="eco">${eco}</span></h1><p>${apoio}</p></div>`;

/** Os "ver mais" que estavam abertos antes de um redesenho por resposta nova (tocar num ajuste não fecha o bloco nem pula a tela). */
function abertosAntes(el, ctx) {
  if (ctx.entrou) return [];
  const velho = [...document.querySelectorAll(".passo-dinheiro")].find((x) => x !== el);
  return velho ? [...velho.querySelectorAll("details[open] > summary")].map((s) => s.textContent) : [];
}
function reabrir(el, titulos) {
  if (!titulos.length) return;
  for (const s of el.querySelectorAll("details > summary")) if (titulos.includes(s.textContent)) s.parentElement.open = true;
}

function ligar(el, ctx) {
  el.addEventListener("click", (ev) => {
    const ab = ev.target.closest("[data-abrir]");
    if (ab) {
      const d = el.querySelector(`#${ab.dataset.abrir}`);
      if (d) { d.open = true; d.scrollIntoView({ behavior: "smooth", block: "start" }); }
      return;
    }
    const b = ev.target.closest("[data-set]");
    if (!b || b.classList.contains("on")) return;
    const [k, v] = b.dataset.set.split("=");
    if (k === "arr") return ctx.set({ hoje: comArranjo(ctx.resp.hoje || "", v) });
    ctx.set({ [k]: v });
  });
}

// ---------- Ajustar a conta (fechado): custo, preço da raiz e como fica no roçado ----------
/** Arranjo de hoje ("junto" | "pedacos" | "baixio") no texto de ctx.resp.hoje. Troca só o arranjo (cons/mbx) e deixa as culturas e
 *  as outras chaves como vieram: sem culturas respondidas, elas continuam "o comum daqui" (o padrão não vira resposta).
 *  "Tudo junto" é o padrão: sem mais nada, a URL volta a ficar limpa. */
function comArranjo(txt, v) {
  const [cs = "", ...kv] = String(txt || "").split("|");
  const resto = kv.filter((p) => p && !/^(cons|mbx)=/.test(p));
  const arr = v === "junto" ? [] : v === "baixio" ? ["cons=0", "mbx=1"] : ["cons=0"];
  const s = [cs, ...arr, ...resto].join("|");
  return /^\|*$/.test(s) ? "" : s;
}

function ajustarHtml(ctx, pr, raiz, nivel, temMand) {
  const { ef, r, util: U } = ctx;
  const uf = r.local.uf, rt = raizTxt(uf);
  const linhas = [`<div class="ctrl">${rotulo(U, "dinheiro", "O que entra na conta", U.selo("medido", FONTE_CONAB))}
    ${seg("custo", nivel, [["semente", "Só a semente"], ["desembolso", "Semente, trator, adubo e diária", "CONAB"]])}</div>`];
  if (temMand) {
    const ops = ["municipio", "uf_mediana", "uf_p25"].filter((v) => pr[v] > 0).map((v) => [v, `R$ ${U.num(pr[v], 2)}`, rt[v]]);
    linhas.push(`<div class="ctrl">${rotulo(U, "mandioca", "Preço da raiz (kg)", U.selo("medido", "mediana 2016–2025 do preço do IBGE no município e na UF; escolher é suposição"))}
      ${seg("raiz", raiz, ops)}${olho(OLHOS.preco_raiz)}</div>`);
  }
  const h = lerHoje(ctx.resp.hoje || "", r.padroes);
  if (Object.keys(h.cult).length > 1) {
    const temB = ef.tem_baixio !== false && (h.cult.milho || 0) > 0;
    const atual = h.cons === 0 && h.mbx === 1 ? "baixio" : h.cons === 0 ? "pedacos" : "junto";
    linhas.push(`<div class="ctrl">${rotulo(U, "faixas", "Como fica no roçado")}
      ${seg("arr", atual, [["junto", "Tudo junto"], ["pedacos", "Em pedaços"], ...(temB ? [["baixio", "Milho no baixio"]] : [])])}</div>`);
  }
  return `<div class="ajustar">${linhas.join("")}${temMand ? "" : olho(OLHOS.agro)}
    <a class="chip aj-mudar" href="${ctx.link(2)}" data-editar="hoje">${U.ic("milho")}Mudar o que planta ou quanto de cada</a></div>`;
}

function avisosHtml(ctx, m) {
  const { ef, util: U } = ctx;
  const out = [];
  if (ef.maniva === "plantada" && m.itens[0].some((i) => i.plantada)) out.push(`<span class="chip verde">${U.ic("mandioca")}mandioca já plantada: a Parte A colhe em 2027</span>`);
  for (const a of m.avisos) out.push(`<span class="chip ambar">${U.esc(a)}</span>`);
  if (m.semRs.length) out.push(`<span class="chip ambar">${U.esc(m.semRs.join(", "))}: comida da criação, fora do R$</span>`);
  return out.length ? `<div class="avisos-linha">${out.join("")}</div>` : "";
}

// ---------- 2027: os El Niños fortes ----------
function elNinoHtml(ctx, m, t, nivel, mult) {
  const { util: U } = ctx;
  const vals = t.elNino.flatMap((e) => [e.plano, e.s0]);
  const lo = Math.min(...vals), hi = Math.max(...vals);
  const cards = t.elNino.map((e) => `<div class="en-card"><div class="en-ano">${e.ano}</div>${G.mini(e.plano, e.s0, lo, hi)}
    <div class="en-val">${chave("plano")}${rs(e.plano)}</div><div class="en-val cinza">${chave("s0")}${rs(e.s0)}</div></div>`).join("");
  const n = t.elNino.length, atras = t.elNino.filter((e) => e.plano < e.s0).length;
  const semVenda = semVendaEm(m, 0);
  const depois = t.porAno[1].plano.p50 < t.porAno[1].s0.p50 && t.porAno[2].plano.p50 < t.porAno[2].s0.p50;
  const frase = atras === 0 ? `Nos ${n}, o plano já fica à frente em 2027.`
    : depois ? `Em ${vezes(atras, n)} o plano fica atrás em 2027, e continua atrás depois.`
      : `Em ${vezes(atras, n)} o plano fica atrás em 2027${semVenda.length ? `: ${semVenda.join("; ")}` : ""}.`;
  const q = C.ano2027Qualquer(m, nivel, mult);
  return `<div class="legenda"><span>${chave("plano")}plano</span><span>${chave("s0")}jeito de hoje</span>
      <span class="chip terra mini">El Niño forte</span>${U.selo("medido", FONTE_PAM + "; anos com ONI ≥ 1,5 em out–dez/nov–jan")}</div>
    <div class="en-grade">${cards}</div>
    <p class="frase">${frase}</p>
    <p class="pequeno sub">O Pacífico de hoje está como nos ${n} El Niños fortes da série (${m.anosEN.join(", ")}). Cada cartão é o que o plano e o jeito de hoje
      teriam deixado em 2027 aqui, naquele ano. São só ${n} anos: não é previsão. Se 2027 for um ano qualquer (os ${q.n} anos): plano típico ${rs(q.plano.p50)},
      jeito de hoje ${rs(q.s0.p50)}.</p>`;
}

/** Partes do roçado que no ano k só têm custo: "a maniva ainda não colhe", "o sorgo vira comida da criação (fora do R$)". */
function semVendaEm(m, k) {
  const g = new Set();
  for (const i of m.itens[k]) {
    if (!i.custo || m.itens[k].some((j) => j.serie && j.parte === i.parte)) continue;
    g.add(i.cultura === "Mandioca" ? "a maniva ainda não colhe"
      : `o ${i.cultura.toLowerCase().replace(" forrageiro", "")} vira comida da criação (fora do R$)`);
  }
  return [...g];
}

// ---------- caixa mês a mês ----------
function caixaHtml(ctx, m, t) {
  const { util: U } = ctx;
  const W = largura(620);
  const { svg } = G.caixa(t, W);
  let iMin = 0, ultimoAtras = -1;
  t.caixaPlano.forEach((q, i) => {
    if (q.p50 < t.caixaPlano[iMin].p50) iMin = i;
    if (q.p50 < t.caixaS0[i].p50 - 0.5) ultimoAtras = i;
  });
  const volta = ultimoAtras >= 0 && ultimoAtras < C.NMESES - 1 ? C.rotMes(ultimoAtras + 1) : null;
  const fundo = t.caixaPlano[iMin].p50;
  const partes = [fundo < 0 ? `Mais apertado: <b>${rs(fundo)}</b> em ${C.rotMes(iMin)}.` : "O caixa do plano não fica negativo.",
    ultimoAtras === -1 ? "Fica à frente desde o começo." : volta ? `Passa o jeito de hoje em <b>${volta}</b>.` : "Termina atrás do jeito de hoje."];
  return `<div class="legenda"><span>${chave("plano")}plano</span><span>${chave("s0")}jeito de hoje</span>
      <span>${U.ic("semente")}sai (plantio)</span><span>${U.ic("dinheiro")}entra (colheita)</span>${U.selo("projecao", SEQ)}</div>
    <div class="rola"><div class="rola-dentro caixa-wrap" style="min-width:${W}px">${svg}<div class="dica" hidden></div></div></div>
    <p class="frase">${partes.join(" ")}</p>
    <p class="pequeno sub">A linha é o caminho típico; a faixa vai do caso ruim (1 em 10) ao bom (9 em 10). O custo entra no mês do plantio e a colheita
      no meio da colheita, com os meses do calendário do plano (2028 e 2029 repetem os meses). A mandioca entra aos poucos nos meses de colheita.</p>
    <h4>Ano a ano</h4>${rolar(G.barrasAno(t.porAno, largura(320)), largura(320))}
    <p class="pequeno sub">A coluna é o ano típico; o traço vai do ano ruim ao bom. Em 2027, do pior ao melhor dos ${t.porAno[0].n} El Niños fortes.</p>`;
}

function ligarCaixa(el, t) {
  const wrap = el.querySelector(".caixa-wrap");
  if (!wrap) return;
  const svg = wrap.querySelector("svg"), dica = wrap.querySelector(".dica"), cur = svg.querySelector(".cursor");
  const { geo } = G.caixa(t, largura(620));
  const porMes = new Map();
  for (const mk of t.marcas) porMes.set(mk.i, [...(porMes.get(mk.i) || []), mk]);
  const mover = (ev) => {
    const rc = svg.getBoundingClientRect();
    const xv = ((ev.clientX - rc.left) * geo.W) / rc.width;
    const i = Math.max(0, Math.min(geo.n - 1, Math.round(((xv - geo.x0) / (geo.x1 - geo.x0)) * (geo.n - 1))));
    const xi = geo.x(i);
    cur.setAttribute("x1", xi); cur.setAttribute("x2", xi); cur.style.display = "";
    const p = t.caixaPlano[i], s = t.caixaS0[i];
    const mov = (porMes.get(i) || []).map((mk) => `<li>${mk.v < 0 ? "sai" : "entra"} ${rs(Math.abs(mk.v))}: ${mk.rotulo}</li>`).join("");
    dica.innerHTML = `<b>${C.rotMes(i)}</b><div>${chave("plano")}plano ${rs(p.p50)} <span>(${faixaRs(p.p10, p.p90)})</span></div>` +
      `<div>${chave("s0")}hoje ${rs(s.p50)} <span>(${faixaRs(s.p10, s.p90)})</span></div>${mov ? `<ul>${mov}</ul>` : ""}`;
    dica.hidden = false;
    const px = (xi / geo.W) * rc.width, w = dica.offsetWidth;
    dica.style.left = `${Math.max(0, Math.min(rc.width - w, px + (px > rc.width / 2 ? -w - 12 : 12)))}px`;
  };
  svg.addEventListener("pointermove", mover);
  svg.addEventListener("pointerdown", mover);
  svg.addEventListener("pointerleave", () => { dica.hidden = true; cur.style.display = "none"; });
}

// ---------- termômetro ----------
function termoHtml(ctx, tS, tD) {
  const { util: U } = ctx;
  const cel = (a) => `<div class="medidor" title="plano: ${a.pagaPlano} de ${a.n}; hoje: ${a.pagaS0} de ${a.n}">
      <span class="trilho"><span class="cheio" style="width:${((a.pagaPlano / a.n) * 100).toFixed(1)}%"></span><span class="marca-s0" style="left:${((a.pagaS0 / a.n) * 100).toFixed(1)}%"></span></span>
      <b>${a.pagaPlano} de ${a.n}</b></div>`;
  const linhas = [0, 1, 2].map((k) => `<div class="termo-linha"><b class="ano">${2027 + k}</b>${cel(tS.porAno[k])}${cel(tD.porAno[k])}</div>`).join("");
  return `<div class="termo"><div class="termo-linha cab"><span></span><span>${CUSTO_TXT.semente}</span><span>${CUSTO_TXT.desembolso}</span></div>${linhas}</div>
    <p class="frase pequeno sub">${U.selo("projecao", `${SEQ}. ${FONTE_CONAB}`)} Barra = plano; risco cinza = jeito de hoje. Em 2027, entre os ${tS.porAno[0].n} El Niños fortes; depois, entre os ${tS.porAno[1].n} anos.</p>`;
}

// ---------- replay de 28 anos ----------
function replayHtml(ctx, m, nivel, mult, preco, temMand) {
  const { r, util: U } = ctx;
  const rows = C.replay(m, nivel, mult);
  const acima = rows.filter((x) => x.plano > x.s0).length;
  const tiles = rows.map((x) => `<i class="${x.plano > x.s0 ? "ac" : "ab"}${m.anosEN.includes(x.ano) ? " en" : ""}" title="${x.ano}: plano ${rs(x.plano)} · hoje ${rs(x.s0)}"></i>`).join("");
  const desc = r.plano.faixas.filter((f) => f.parte !== "Bordas" && (f.parte !== "Baixio" || m.b > 0)).map((f) => {
    const its = m.itens[2].filter((i) => i.parte === f.parte), c = f.anos[2].cultura;
    const tx = its.some((i) => i.serie === "Mandioca") ? "colhe a mandioca" : its.some((i) => i.custo === "Mandioca") ? "recebe a maniva" :
      f.parte === "Baixio" && c === "Milho" && r.plano.leguminosa ? `milho + ${r.plano.leguminosa.toLowerCase()}` : c.toLowerCase();
    return `${f.parte === "Baixio" ? "baixio" : f.parte}: ${tx}`;
  }).join("; ");
  // o plano nunca esteve no chão: a conta é refeita com as colheitas medidas (por isso SUPOSIÇÃO, não MEDIDO)
  return `<h4>Os 28 anos: se o plano estivesse no chão desde 1998 ${U.selo("suposicao", `refeito com as colheitas medidas do ${FONTE_PAM}`)}</h4>
    <div class="faixa28">${tiles}</div>
    <div class="faixa28-eixo"><span>${rows[0].ano}</span><span class="leg"><i class="ac"></i>plano acima <i class="ab"></i>abaixo <i class="en-leg"></i>El Niño forte</span><span>${rows[rows.length - 1].ano}</span></div>
    <p class="frase">O plano ficou acima do jeito de hoje em <b>${acima} de ${rows.length} anos</b>.</p>
    <p>O plano já rodando (${U.esc(desc)}) contra o jeito de hoje, no mesmo ano${temMand ? `, com a raiz a R$ ${U.num(preco, 2)}/kg` : ""}.</p>
    ${rolar(G.replay(rows, m.anosEN, largura(600)), largura(600))}`;
}

// ---------- Ver como calculamos ----------
function culturaTabela(fin, U) {
  const linhas = ["Milho", "Feijão", "Mandioca"].map((s) => {
    const c = fin.culturas?.[s];
    if (!c) return `<tr><td>${s}</td><td colspan="6" class="sub">sem série no município (menos de 10 anos com 10 ha ou mais no IBGE)</td></tr>`;
    const v = c.valor_ha || {};
    return `<tr><td>${s}${c.aviso ? `<br><small class="sub">${U.esc(c.aviso)}</small>` : ""}</td><td>${rs(v.min)}</td><td>${rs(v.p50)}</td><td>${rs(v.max)}</td>
      <td>${c.el_nino_forte === null ? "—" : rs(c.el_nino_forte)}</td><td>${rs(c.ultimos?.["2025"])}</td>
      <td>R$ ${U.num(c.preco_kg, 2)}/kg${c.origem_preco !== "município" ? ` (${U.esc(c.origem_preco)})` : ""}<br><small class="sub">semente ${rs(c.custo_ha?.semente)} · desembolso ${rs(c.custo_ha?.desembolso)}</small></td></tr>`;
  }).join("");
  return `<div class="rola"><table class="tab-cult"><thead><tr><th>por ha plantado</th><th>pior ano</th><th>típico</th><th>melhor</th><th>El Niño forte</th><th>2025</th><th>preço e custo</th></tr></thead>
    <tbody>${linhas}</tbody></table></div><p class="pequeno sub">${U.selo("medido", FONTE_PAM + "; " + FONTE_CONAB)} Valor da colheita por ha (vender ou comer, a preço da região), antes do custo.</p>`;
}

function detalhesHtml(ctx, m, fin, t, nivel, mult, preco) {
  const { util: U } = ctx;
  const ha = (v) => U.ha(Math.round(v * 100) / 100);
  const porAno = [0, 1, 2].map((k) => {
    const its = m.itens[k];
    const txt = [...new Set(its.map((i) => {
      if (i.serie === "Mandioca") return `${i.parte}: ${i.plantada ? "colhe a mandioca já plantada" : "colhe a mandioca"}`;
      if (i.custo === "Mandioca") return `${i.parte}: maniva (só custo)`;
      if (i.uso) return `${i.parte}: ${i.cultura.toLowerCase()} (forragem: só custo)`;
      if (i.parte === "Baixio") return `Baixio: ${[...new Set(its.filter((j) => j.parte === "Baixio").map((j) => j.cultura.toLowerCase()))].join(" + ")} (metade da área cada)`;
      return `${i.parte}: ${i.cultura.toLowerCase()}`;
    }))].join("; ");
    return `<li><b>${2027 + k}</b> (${k === 0 ? `um dos ${t.nEN} El Niños fortes` : `um dos ${t.nAnos} anos`}): ${U.esc(txt)}</li>`;
  }).join("");
  const tab = t.porAno.map((a) => `<tr><td>${a.ano}</td><td>${rs(a.plano.p10)} · <b>${rs(a.plano.p50)}</b> · ${rs(a.plano.p90)}</td>
    <td>${rs(a.s0.p10)} · <b>${rs(a.s0.p50)}</b> · ${rs(a.s0.p90)}</td><td>${a.planoFrente} de ${a.n}</td></tr>`).join("");
  const c = fin.calibracao || {}, cob = c.faixa_p10_p90_cobriu_fora_da_amostra || {}, mm = c.min_max_cobriu_fora_da_amostra || {};
  const avisos = (fin.avisos || []).filter((a) => !/não é lucro|fora da conta/.test(a));
  return `<h4>O que é cada número</h4>
    <p>"Sobra" = valor da colheita (vender ou comer, a preço da região) menos o custo escolhido. Nunca é lucro: a mão de obra da família não entra.
      Plano em 3 anos: típico ${rs(t.plano.p50)}, ${faixaRs(t.plano.p10, t.plano.p90)} (caso ruim = 1 em cada 10; bom = 9 em cada 10).
      Jeito de hoje: típico ${rs(t.s0.p50)}, ${faixaRs(t.s0.p10, t.s0.p90)}. O plano termina à frente em ${U.num(t.aFrente * 100, 1)}% das combinações.
      ${nivel === "desembolso" ? "Custo: desembolso da CONAB (máquina, insumos e serviços)." : "Custo: só a semente (CONAB)."}</p>
    <h4>Áreas ${U.selo("suposicao", SUP_AREA)}</h4>
    <p>Roçado de ${ha(m.T)}: ${m.b > 0 ? `baixio de ${ha(m.b)}${m.baixioNaoSei ? " (não respondido: ⅓ do roçado)" : ""} e ` : ""}cada parte (A, B e C) com ${ha(m.a)}.
      As bordas (palma + gliricídia) não tiram área. No baixio, metade é milho e metade a leguminosa.</p>
    <h4>O que entra em cada ano</h4><ul>${porAno}</ul>
    <p>Mandioca: o custo da maniva entra no ano do plantio; a receita, no ano seguinte. Preço da raiz: R$ ${U.num(preco, 2)}/kg
      (a série do IBGE usa R$ ${U.num(m.precoRefMand ?? 0, 2)}/kg; a mandioca é multiplicada por ${U.num(mult, 2)}).</p>
    <h4>As combinações de anos ${U.selo("projecao", SEQ)}</h4>
    <p>2027 é um dos El Niños fortes (${m.anosEN.join(", ")}); 2028 e 2029, qualquer um dos ${m.anos.length} anos de 1998 a 2025. O mesmo ano vale para todas as
      culturas e para o jeito de hoje (a chuva é a mesma no roçado todo). ${t.nEN} × ${t.nAnos} × ${t.nAnos} = ${t.n.toLocaleString("pt-BR")} combinações, todas contadas,
      sem sorteio. Sem tendência nem previsão de série: aqui um ano quase não se parece com o anterior (autocorrelação de 0,2).</p>
    <div class="rola"><table><thead><tr><th>ano</th><th>plano: P10 · P50 · P90</th><th>hoje: P10 · P50 · P90</th><th>plano à frente</th></tr></thead><tbody>${tab}</tbody></table></div>
    <h4>Calibrador honesto</h4>
    <p>Num teste fora da amostra (faixa de 1998–2015 conferida em 2016–2025), a faixa P10–P90 de um ano acertou
      ${Object.entries(cob).map(([k, v]) => `${k.toLowerCase()} ${U.emDez(v)}`).join(", ")} anos (deveria ser 8 em 10); do pior ao melhor ano já visto,
      ${Object.entries(mm).map(([k, v]) => `${k.toLowerCase()} ${U.emDez(v)}`).join(", ")}. O futuro varia mais que o passado.</p>
    <h4>Por cultura</h4>${culturaTabela(fin, U)}
    <h4>Fora da conta</h4>
    <ul><li>Forragem (sorgo, palma, gliricídia): comida da criação, sem preço no IBGE. Só entra o custo da semente do sorgo (${rs(fin.custo_sorgo_forrageiro_ha?.[nivel])}/ha,
      ${U.selo("suposicao", fin.custo_sorgo_forrageiro_ha?.origem || "lavoura anual manual")}).</li>
      <li>Garantia-Safra (perda de 40% ou mais, até 5 ha; o valor não foi conferido), mão de obra, frete e casa de farinha.</li>
      <li>O ganho de rendimento da rotação contra o consórcio de hoje (não medido) e o preço futuro (fica o de 2016–2025, em R$ de 2025).</li>
      <li>Rendimento acima de 2× o da roça de família da CONAB (milho 1.800, feijão 800, mandioca 17.400 kg/ha) marca lavoura grande na série.</li></ul>
    ${avisos.length ? `<h4>Avisos dos dados</h4><ul>${avisos.map((a) => `<li>${U.esc(a)}</li>`).join("")}</ul>` : ""}`;
}

// ---------- sem série (vai no "Ver como calculamos": o aviso à vista é o do Hoje → melhor → ideal) ----------
function semConta(m, fin, U) {
  if (!fin) return `<p>Sem dados do IBGE para este município: não inventamos número.</p>`;
  const falta = m.falta.map((s) => (["Milho", "Feijão", "Mandioca"].includes(s) ? `${s.toLowerCase()}: menos de 10 anos no IBGE` : s));
  return `<h4>O que falta aqui</h4><p>${U.esc(falta.join("; "))}. Para comparar o plano com o jeito de hoje no mesmo ano, cada cultura do plano precisa
    de 10 anos ou mais com 10 ha plantados ou mais (IBGE, 1998–2025). Abaixo, só o que existe daqui, por ha plantado.</p>${culturaTabela(fin, U)}`;
}
