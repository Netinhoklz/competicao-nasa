// QUADRA, passo 4 "Quanto rende": o retorno do plano de rotação, refeito nos anos que já aconteceram no município.
// Visual v2 (LEIA-ME.md, "Visual e texto"): pouco texto na frente; método, fórmulas e ressalvas no "Ver como calculamos".
// Método: analise/financeiro.md (seções 2, 4 e 6); decisões 7 e 9 do PLANO_INTEGRACAO.md.
// Contas em js/passos/dinheiro/calculo.js; gráficos em js/passos/dinheiro/graficos.js.
import * as C from "./dinheiro/calculo.js";
import * as G from "./dinheiro/graficos.js";
import { termo } from "../extras/glossario.js";
import { olho, OLHOS } from "../extras/voce_decide.js";
// "Hoje → melhor → ideal" (extras/hoje_ideal.js): o jeito de hoje informado no passo 2 entra no lugar do milho + feijão fixo
import HI, { comHoje } from "../extras/hoje_ideal.js";
// Extra (js/extras/cenarios.js, montado por U.montarExtras): "Outros jeitos de girar o roçado", que acende o jeito da prioridade escolhida
// no "Seu bolso" (pontos 8 e 9; "Cuidar do solo" acende o jeito do solo). "Seu olho" (ponto 16): o preço da raiz e, sempre, a conta da família
// (com lavoura grande no IBGE, ele vai no aviso).

const { rs, faixaRs } = G;
const SEQ = "3.136 combinações de anos já vistos aqui (2027 entre os 4 El Niños fortes; 2028 e 2029 entre os 28 anos do IBGE), todas contadas";
const FONTE_PAM = "IBGE PAM 1998–2025: rendimento por ha plantado × preço de referência do município, em R$ de 2025 (IPCA)";
const FONTE_CONAB = "CONAB, custos de produção do NE (semente e desembolso), R$ de 2025";
const SUP_AREA = "Partes A, B e C do mesmo tamanho; bordas não tiram área; baixio = metade milho + metade caupi; forragem sem R$";

const kg = (v) => `${(v >= 1000 ? Math.round(v / 10) * 10 : Math.round(v)).toLocaleString("pt-BR")} kg`;
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
    const jeitos = r.plano ? U.extra("cenarios") : "";
    const m = comHoje(C.montar(r, ef), r, ef, ctx.resp.hoje || "");
    const pr = fin?.precos_raiz || {};
    const temMand = !!m.usadas?.includes("Mandioca");
    let raiz = ef.raiz, preco = pr[raiz];
    if (!(preco > 0)) { raiz = "municipio"; preco = pr.municipio ?? m.precoRefMand; }
    const mult = m.precoRefMand && preco ? preco / m.precoRefMand : 1;
    const nivel = ef.custo === "desembolso" ? "desembolso" : "semente";
    const bolso = bolsoHtml(ctx, m, pr, raiz, nivel, temMand);
    const apoio = `O seu roçado de ${U.ha(ef.ha)} refeito nos anos que já aconteceram em ${U.esc(mun)}.`;

    if (!m.ok) {
      el.innerHTML = abertura("Ainda não dá para fazer a conta aqui.", "Falta a série do IBGE.",
        `O IBGE não tem anos suficientes das culturas do plano em ${U.esc(mun)}.`) + `<div class="hi-slot"></div>` + semConta(m, fin, U) + jeitos;
      ligar(el, ctx);
      await HI.render(el.querySelector(".hi-slot"), ctx, { modo: "comparacao", linkMudar: ctx.link(2), semTitulo: true });
      await U.montarExtras(el, ctx);
      return;
    }

    const t = C.calcular(m, nivel, mult);
    const tS = nivel === "semente" ? t : C.calcular(m, "semente", mult);
    const tD = nivel === "desembolso" ? t : C.calcular(m, "desembolso", mult);
    const agro = m.agro.length > 0;
    const ganha = t.ganho.p50 > 0;
    const caro27 = t.porAno[0].plano.p50 < t.porAno[0].s0.p50;
    const [h1, eco] = agro ? ["Aqui o IBGE mistura lavoura grande.", "Os R$ não são de roça de família."]
      : ganha ? ["Em 3 anos, o plano rende mais.", caro27 ? "2027 é o ano mais apertado." : "Já em 2027 ele fica à frente."]
        : ["Em dinheiro, o plano rende menos.", "O ganho dele é comida da criação e solo."];

    const blocos = {
      // os 28 anos refeitos ficam no "ver mais" do herói (repetiam o "plano à frente")
      heroi: heroiHtml(ctx, m, t, nivel, pr, temMand, replayHtml(ctx, m, nivel, mult, preco, temMand)),
      elnino: elNinoHtml(ctx, m, t, nivel, mult),
      caixa: caixaHtml(ctx, m, t),
      termo: termoHtml(ctx, tS, tD),
    };
    const ordem = ef.prioridade === "garantir" ? ["heroi", "elnino", "caixa", "termo"] : ["heroi", "caixa", "elnino", "termo"];
    const corpo = ordem.map((k) => blocos[k]).join("");
    const ag = agro ? [...m.agro].sort((x, y) => y.kg / y.conab - x.kg / x.conab) : [];
    const aviso = agro ? `<section class="painel alerta">${U.faixa("alerta", "terra",
      `${ag[0].cultura} daqui: ${U.num(ag[0].kg)} kg/ha, ${U.num(ag[0].kg / ag[0].conab, 1)}× a roça de família.`)}
      <p class="pequeno sub">${ag.slice(1).map((x) => `${x.cultura}: ${U.num(x.kg / x.conab, 1)}×. `).join("")}Os números abaixo servem só para comparar o plano com o jeito de hoje.
      ${U.selo("medido", "IBGE PAM 1998–2025 e planilhas da agricultura familiar da CONAB (2015+)")}</p>${olho(OLHOS.agro)}</section>` : "";
    el.innerHTML = abertura(h1, eco, apoio) + bolso + `<div class="hi-slot"></div>` + avisosHtml(ctx, m) + aviso + (agro ? `<div class="apagado">${corpo}</div>` : corpo) + jeitos +
      `<section class="painel como">${U.verMais(detalhesHtml(ctx, m, fin, t, nivel, mult, preco), "Ver como calculamos")}</section>`;
    ligar(el, ctx);
    ligarCaixa(el, t);
    await HI.render(el.querySelector(".hi-slot"), ctx, { modo: "comparacao", linkMudar: ctx.link(2), semTitulo: true });
    await U.montarExtras(el, ctx);
  },
};

const abertura = (h1, eco, apoio) => `<div class="titulo-passo"><p class="kicker">Passo 4 · quanto rende</p>
  <h1>${h1}<span class="eco">${eco}</span></h1><p>${apoio}</p></div>`;

function ligar(el, ctx) {
  el.addEventListener("click", (ev) => {
    const b = ev.target.closest("[data-set]");
    if (!b) return;
    const [k, v] = b.dataset.set.split("=");
    ctx.set({ [k]: v });
  });
}

// ---------- Seu bolso: 3 controles e uma linha de chips ----------
function bolsoHtml(ctx, m, pr, raiz, nivel, temMand) {
  const { ef, r, util: U } = ctx;
  const uf = r.local.uf;
  const temB = m.temBaixio ?? ef.tem_baixio !== false, b = m.b ?? ef.baixio_ha;
  const area = `${U.ha(ef.ha)}${temB && b > 0 ? ` · ${U.ha(b)} de baixio${ef.tem_baixio === null ? "?" : ""}` : " · sem baixio"}`;
  const sug = ef.prioridade_origem === "resposta" ? "" : ef.prioridade_origem.includes("alerta")
    ? `<span class="chip ambar" title="Padrão em ano de alerta de El Niño: mude se quiser">${U.ic("alerta")}sugerido: garantir (El Niño)</span>`
    : `<span class="chip" title="Padrão: mude se quiser">sugerido: equilibrar</span>`;
  const raizOps = [["municipio", pr.municipio, "daqui"], ["uf_mediana", pr.uf_mediana, `comum ${uf}`], ["uf_p25", pr.uf_p25, `baixo ${uf}`]]
    .filter(([, p]) => p > 0).map(([v, p, s]) => [v, `R$ ${U.num(p, 2)}`, s]);
  const gs = ef.gs === "sim" || ef.gs === "nao" ? ef.gs : "nao_sei", cabe = ef.ha <= 5;
  const gsChip = gs === "sim" ? `<span class="chip verde">paga se perder 40% ou mais</span>`
    : cabe ? `<span class="chip verde">${U.ic("ok")}você cabe: até 5 ha</span>` : `<span class="chip terra">acima de 5 ha: não cabe</span>`;
  return `<section class="painel bolso" aria-label="Seu bolso">
    <div class="bolso-linha">
      <div class="ctrl">${rotulo(U, "escudo", "O que vale mais")}${seg("prioridade", ef.prioridade, [["garantir", "Garantir comida"], ["equilibrar", "Equilibrar"], ["vender", "Vender mais"], ["solo", "Cuidar do solo"]])}</div>
      <div class="ctrl">${rotulo(U, "mandioca", "Preço da raiz (kg)", temMand ? U.selo("medido", "mediana 2016–2025 do preço do IBGE no município e na UF; escolher é suposição") : "")}
        ${temMand ? seg("raiz", raiz, raizOps) : `<div class="seg-vazio">o plano daqui não tem mandioca</div>`}</div>
      <div class="ctrl">${rotulo(U, "dinheiro", "O que você paga")}${seg("custo", nivel, [["semente", "Só a semente"], ["desembolso", "Máquina e insumos"]])}</div>
    </div>
    ${temMand ? olho(OLHOS.preco_raiz) : ""}
    <div class="bolso-chips">
      <a class="chip" href="${ctx.link(2)}" title="Mudar no passo 2">${U.ic("faixas")}${area} · mudar</a>${sug}
      <span class="gs" title="Garantia-Safra: o valor do benefício não entra na conta">${U.ic("escudo")}Garantia-Safra
        ${seg("gs", gs, [["sim", "sim"], ["nao", "não"], ["nao_sei", "não sei"]])}${gsChip}</span>
    </div>
  </section>`;
}

function avisosHtml(ctx, m) {
  const { ef, util: U } = ctx;
  const out = [];
  if (ef.maniva === "plantada" && m.itens[0].some((i) => i.plantada)) out.push(`<span class="chip verde">${U.ic("mandioca")}mandioca já plantada: a Parte A colhe em 2027</span>`);
  for (const a of m.avisos) out.push(`<span class="chip ambar">${U.esc(a)}</span>`);
  if (m.semRs.length) out.push(`<span class="chip ambar">${U.esc(m.semRs.join(", "))}: sem preço aqui, fica fora da conta</span>`);
  return out.length ? `<div class="avisos-linha">${out.join("")}</div>` : "";
}

// ---------- herói: os dois números ----------
function heroiHtml(ctx, m, t, nivel, pr, temMand, anos28 = "") {
  const { ef, util: U } = ctx;
  const garantir = ef.prioridade === "garantir";
  const num = (f) => (garantir ? f.p10 : f.p50);
  const sub = (f) => (garantir ? `típico ${rs(f.p50)}` : `caso ruim ${rs(f.p10)} · bom ${rs(f.p90)}`);
  const N = Math.round(t.aFrente * 100);
  const frente = t.aFrente >= 0.5
    ? `<span class="chip verde grande">${U.ic("ok")}plano à frente em ${N === 100 && t.aFrente < 1 ? "mais de 99" : N} de 100</span>`
    : `<span class="chip terra grande">${U.ic("alerta")}jeito de hoje à frente em ${100 - N} de 100</span>`;
  let extra = "";
  if (garantir) {
    const com = C.comida2027(m);
    const g = com.map((x) => x.graoPlano), g0 = com.map((x) => x.graoS0), rz = com.map((x) => x.raizPlano);
    const rng = (a) => `${kg(Math.min(...a))} a ${kg(Math.max(...a))}`;
    extra = `<div class="linha-chips"><span class="chip">${U.ic("feijao")}grão em 2027, se for El Niño: plano ${rng(g)} · hoje ${rng(g0)}</span>` +
      (Math.max(...rz) > 0 ? `<span class="chip">${U.ic("mandioca")}raiz em 2027: ${rng(rz)}</span>` : "") + `</div>`;
  } else if (ef.prioridade === "vender" && temMand) {
    const ops = [["municipio", "daqui"], ["uf_mediana", "comum"], ["uf_p25", "baixo"]].filter(([k]) => pr[k] > 0)
      .map(([k]) => ({ k, p: pr[k], g: C.totais(m, nivel, pr[k] / m.precoRefMand).ganho.p50 }));
    const emp = C.precoEmpate(m, nivel);
    extra = `<div class="linha-chips"><span class="rot-mini">${U.ic("mandioca")}se a raiz valer</span>${ops.map((o) =>
      `<span class="chip${o.k === ef.raiz ? " verde" : ""}">R$ ${U.num(o.p, 2)} → ${o.g >= 0 ? "+" : ""}${rs(o.g)}</span>`).join("")}` +
      (emp ? `<span class="chip ambar">empata com a raiz a R$ ${U.num(emp, 2)}</span>` : "") + `</div>`;
  }
  const motivo = ganhaOuMotivo(m, t);
  return `<section class="painel heroi">
    ${rotulo(U, "dinheiro", `${garantir ? `No caso ruim (${termo("em_dez", "1 em cada 10")})` : "Típico"}, em 3 anos · ${nivel === "semente" ? "sobra depois da semente" : "sobra depois de máquina e insumos"}`,
      U.selo("projecao", `${SEQ}. ${FONTE_PAM}. ${FONTE_CONAB}`))}
    <div class="heroi-nums">
      <div class="hn">${chave("plano")}<span class="hn-rot">O plano</span><div class="hn-val">${rs(num(t.plano))}</div><div class="hn-sub">${sub(t.plano)}</div></div>
      <div class="hn">${chave("s0")}<span class="hn-rot">Jeito de hoje <small>${U.esc(m.hojeDesc || "milho + feijão")}</small></span><div class="hn-val cinza">${rs(num(t.s0))}</div><div class="hn-sub">${sub(t.s0)}</div></div>
    </div>
    ${G.barrasH([{ rot: "o plano", cls: "plano", f: t.plano }, { rot: "jeito de hoje", cls: "s0", f: t.s0 }], largura(280))}
    <div class="linha-chips">${frente}${motivo}</div>${extra}
    ${m.agro.length ? "" : olho(OLHOS.agro)}
    ${anos28 ? U.verMais(anos28, "Ver os 28 anos") : ""}
  </section>`;
}

/** Quando o plano perde em R$: o porquê em uma linha. */
function ganhaOuMotivo(m, t) {
  if (t.ganho.p50 > 0) return "";
  const uso = [...new Set([0, 1, 2].flatMap((k) => m.itens[k].filter((i) => i.uso).map((i) => i.cultura.toLowerCase())))];
  const p = [];
  if (!m.usadas.includes("Mandioca")) p.push("sem mandioca");
  if (uso.length) p.push(`${uso.join(" e ")} sem preço`);
  if (m.agro.length) p.push("IBGE de lavoura grande");
  return p.length ? `<span class="chip">por quê: ${p.join(" · ")}</span>` : "";
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
      : `Em ${vezes(atras, n)} o plano fica atrás em 2027${semVenda.length ? `: ${semVenda.join(" e ")} ainda não ${semVenda.length > 1 ? "vendem" : "vende"}` : ""}.`;
  const q = C.ano2027Qualquer(m, nivel, mult);
  return `<section class="painel">
    ${rotulo(U, "onda", "Se 2027 for como…", `<span class="chip terra mini">El Niño muito forte</span>${U.selo("medido", FONTE_PAM + "; anos com ONI ≥ 1,5 em out–dez/nov–jan")}`)}
    <div class="en-grade">${cards}</div>
    <p class="frase">${frase}</p>
    ${U.verMais(`<p>O Pacífico de hoje está como nos ${n} El Niños fortes da série (${m.anosEN.join(", ")}). Cada cartão é o que o plano e o jeito de hoje
      teriam deixado em 2027 aqui, naquele ano. São só ${n} anos: não é previsão.</p>
      <p>Se 2027 for um ano qualquer (os ${q.n} anos): plano típico ${rs(q.plano.p50)}, jeito de hoje ${rs(q.s0.p50)}.</p>`, "Ver mais")}
  </section>`;
}

/** Partes do roçado que no ano k só têm custo: "a maniva (Parte A) e o sorgo forrageiro (Partes B e C)". */
function semVendaEm(m, k) {
  const g = new Map();
  for (const i of m.itens[k]) {
    if (!i.custo || m.itens[k].some((j) => j.serie && j.parte === i.parte)) continue;
    const nome = i.cultura === "Mandioca" ? "a maniva" : `o ${i.cultura.toLowerCase()}`;
    const ps = g.get(nome) || [];
    if (!ps.includes(i.parte)) ps.push(i.parte);
    g.set(nome, ps);
  }
  return [...g].map(([nome]) => nome);
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
  return `<section class="painel">
    ${rotulo(U, "calendario", "Quando o dinheiro entra", U.selo("projecao", SEQ))}
    <div class="legenda"><span>${chave("plano")}plano</span><span>${chave("s0")}jeito de hoje</span>
      <span>${U.ic("semente")}sai (plantio)</span><span>${U.ic("dinheiro")}entra (colheita)</span></div>
    <div class="rola"><div class="rola-dentro caixa-wrap" style="min-width:${W}px">${svg}<div class="dica" hidden></div></div></div>
    <p class="frase">${partes.join(" ")}</p>
    ${U.verMais(`<p>A linha é o caminho típico; a faixa vai do caso ruim (1 em 10) ao bom (9 em 10). O custo entra no mês do plantio e a colheita
      no meio da colheita, com os meses do calendário do passo 3 (2028 e 2029 repetem os meses). A mandioca entra aos poucos nos meses de colheita.</p>
      <h4>Ano a ano</h4>${rolar(G.barrasAno(t.porAno, largura(320)), largura(320))}
      <p class="pequeno sub">A coluna é o ano típico; o traço vai do ano ruim ao bom. Em 2027, do pior ao melhor dos ${t.porAno[0].n} El Niños fortes.</p>`, "Ver mais")}
  </section>`;
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
  return `<section class="painel">
    ${rotulo(U, "escudo", "A colheita paga o gasto do ano?", U.selo("projecao", `${SEQ}. ${FONTE_CONAB}`))}
    <div class="termo"><div class="termo-linha cab"><span></span><span>só a semente</span><span>máquina e insumos</span></div>${linhas}</div>
    <p class="frase pequeno sub">Barra = plano; risco cinza = jeito de hoje. Em 2027, entre os ${tS.porAno[0].n} El Niños fortes; depois, entre os ${tS.porAno[1].n} anos.</p>
  </section>`;
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
  return `${rotulo(U, "grafico", "Se o plano estivesse no chão desde 1998", U.selo("suposicao", `refeito com as colheitas medidas do ${FONTE_PAM}`))}
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

// ---------- sem série ----------
function semConta(m, fin, U) {
  const falta = !fin ? ["sem dados do IBGE para este município"]
    : m.falta.map((s) => (["Milho", "Feijão", "Mandioca"].includes(s) ? `${s.toLowerCase()}: menos de 10 anos no IBGE` : s));
  return `<section class="painel alerta">${U.faixa("alerta", "terra", "Sem a série do IBGE, não inventamos número.")}
    <div class="linha-chips">${falta.map((f) => `<span class="chip terra">${U.esc(f)}</span>`).join("")}</div>
    ${fin ? U.verMais(`<p>Para comparar o plano com o jeito de hoje no mesmo ano, cada cultura do plano precisa de 10 anos ou mais com 10 ha plantados ou mais
      (IBGE, 1998–2025). Abaixo, só o que existe daqui, por ha plantado.</p>${culturaTabela(fin, U)}`, "Ver o que existe aqui") : ""}</section>`;
}
