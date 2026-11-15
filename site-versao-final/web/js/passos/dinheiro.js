// QUADRA, passo 4 "Quanto rende": Hoje → Melhorado → Ideal refeitos nos anos que já aconteceram no município.
// Rodada 2 (analise/fluxo2/BRIEFING.md, D5): os números vêm de extras/ideal.js (comparar3 e escolhido), a mesma fonte do "O que você
// ganha" do Plano; o Ideal é o da prioridade escolhida no Plano (uma linha diz qual e leva ao Plano para mudar; as abas saíram daqui).
// O ponto 6 (incerteza), que vinha do "Se secar": "em 8 de 10 anos…" à vista e a grade de 10 roças no "ver mais".
// Os "ver mais" (El Niño, caixa, paga o gasto, os 28 anos, como calculamos) são do plano escolhido no Plano (Seu jeito, melhorado
// ou O ideal) contra o jeito de hoje, na mesma base pareada (dinheiro/pareado.js). Contas: dinheiro/calculo.js (não muda).
// Visual v2 (LEIA-ME.md, "Visual e texto"): pouco texto na frente; método, fórmulas e ressalvas no "Ver como calculamos".
import * as C from "./dinheiro/calculo.js";
import * as G from "./dinheiro/graficos.js";
import { basePareada, montagem } from "./dinheiro/pareado.js";
import { termo } from "../extras/glossario.js";
import { olho, OLHOS } from "../extras/voce_decide.js";
import HI, { lerHoje } from "../extras/hoje_ideal.js";
import { comparar3, escolhido, textoItem } from "../extras/ideal.js";

const { rs, faixaRs } = G;
const SEQ = "3.136 combinações de anos já vistos aqui (2027 entre os 4 El Niños fortes; 2028 e 2029 entre os 28 anos do IBGE), todas contadas";
const FONTE_PAM = "IBGE PAM 1998–2025: rendimento por ha plantado × preço de referência do município, em R$ de 2025 (IPCA)";
const FONTE_CONAB = "CONAB, custos de produção do NE (semente e desembolso), R$ de 2025";
const FONTE_PROJ = "anos parecidos do IBGE (PAM 1998–2025), município + mesorregião, alargado pelo teste com o passado";
const SUP_AREA = "Partes A, B e C do mesmo tamanho; bordas não tiram área; baixio = metade milho + metade feijão; forragem sem R$";
const CUSTO_TXT = { semente: "só a semente", desembolso: "semente, trator, adubo e diária" };
const raizTxt = (uf) => ({ municipio: "daqui", uf_mediana: `comum no ${uf}`, uf_p25: `baixo no ${uf}` });
// o plano escolhido no Plano, nos rótulos dos "ver mais" (a cor dele também: melhorado âmbar, ideal azul, como no gráfico de cima)
const NOME = { melhor: "melhorado", ideal: "ideal" };

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
const temCultura = (p, nome) => (p?.faixas || []).some((f) => f.parte !== "Bordas" && f.anos?.some((c) => c.cultura === nome));

export default {
  id: "dinheiro",
  titulo: "Quanto rende",
  async render(el, ctx) {
    const { r, ef, util: U } = ctx;
    const resp = ctx.resp || {};
    const fin = r.financeiro, mun = r.local.municipio;
    const abertos = abertosAntes(el, ctx);
    // uma fonte só: o plano escolhido no Plano e os três caminhos com os números de "O que você ganha"
    const esc = escolhido(r, resp, ef);
    const c3 = comparar3(r, resp, ef, esc.prioridade);
    const sel = esc.tipo === "ideal" ? "ideal" : "melhor";
    const rsSel = c3[sel]?.beneficios?.rs, rsHoje = c3.hoje?.beneficios?.rs;
    const X = basePareada(r, resp, ef);
    const m = rsSel?.ok ? montagem(X, r, ef, esc.plano) : null; // os lançamentos do escolhido (caixa, El Niño, paga o gasto)
    const { nivel, mult, preco } = X;
    const pr = fin?.precos_raiz || {};
    const raiz = pr[ef.raiz] > 0 ? ef.raiz : "municipio";
    const h = lerHoje(resp.hoje || "", r.padroes);
    // o preço da raiz só pesa quando a mandioca entra num dos três caminhos e tem série aqui
    const raizVis = !!fin && preco > 0 && X.series.has("Mandioca") && ((h.cult.mandioca || 0) > 0 || temCultura(c3.melhor?.plano, "Mandioca") || temCultura(c3.ideal?.plano, "Mandioca"));
    // a linha do que a conta supõe (à vista, sob o título); "ajustar" abre o "Ajustar a conta"
    const supoe = `<span class="conta-com">Conta com: ${CUSTO_TXT[nivel]}${raizVis ? ` · raiz a R$ ${U.num(preco, 2)}/kg (${raizTxt(r.local.uf)[raiz]})` : ""} ·
      <button type="button" class="link-ajustar" data-abrir="ajustar-conta">ajustar</button>
      ${U.selo("suposicao", `o que a conta supõe quando você não diz: custo da CONAB${raizVis ? "; preço da raiz do IBGE (2016–2025)" : ""}`)}</span>`;
    const ajustar = fin ? `<details class="ver-mais" id="ajustar-conta"><summary>Ajustar a conta</summary>${ajustarHtml(ctx, pr, raiz, nivel, raizVis)}</details>` : "";
    const agro = [rsHoje, c3.melhor?.beneficios?.rs, rsSel].some((x) => x?.ok && x.agro?.length);
    const hiOp = { modo: "comparacao", c3, escolhido: esc, linkMudar: ctx.link(2), linkIdeal: ctx.link(3, { plano: "ideal" }),
      ruim: termo("em_dez", "1 em 10"), olhoAgro: OLHOS.agro };

    const sobe = rsSel?.ok && rsHoje?.ok && rsSel.tres_anos.p50 > rsHoje.tres_anos.p50;
    const algumRs = [rsHoje, c3.melhor?.beneficios?.rs, rsSel].some((x) => x?.ok);
    const [h1, eco, apoio] = !fin ? ["Ainda não dá para fazer a conta aqui.", "Falta a série do IBGE.", `O IBGE não tem a série das culturas daqui em ${U.esc(mun)}.`]
      : !algumRs ? ["Hoje, melhorado e ideal.", "Sem R$: falta a série do IBGE.", supoe]
        : [sobe ? "Dá para tirar mais do mesmo roçado." : "O seu jeito, lado a lado com o plano.", "Hoje, melhorado e ideal.", supoe];
    const comVer = m && !m.semHoje; // as comparações com o jeito de hoje só quando hoje também tem conta
    const t = comVer ? C.calcular(m, nivel, mult) : null;
    const tS = !comVer ? null : nivel === "semente" ? t : C.calcular(m, "semente", mult), tD = !comVer ? null : nivel === "desembolso" ? t : C.calcular(m, "desembolso", mult);
    const mais = `<section class="painel mais-conta">${ajustar}
      ${comVer ? U.verMais(ap(agro, elNinoHtml(ctx, m, t, sel, nivel, mult)), "Se 2027 for como os El Niños fortes") : ""}
      ${comVer ? U.verMais(ap(agro, caixaHtml(ctx, t, sel)), "Quando o dinheiro entra") : ""}
      ${comVer ? U.verMais(ap(agro, termoHtml(ctx, tS, tD, sel)), "A colheita paga o gasto?") : ""}
      ${r.plano ? U.verMais(U.extra("cenarios", { leitura: true, painel: false, prioridade: esc.prioridade }), "Os 4 jeitos, lado a lado") : ""}
      ${U.verMais(`${oitoNumeros(ctx, c3, sel)}${comVer ? replayHtml(ctx, m, esc.plano, sel, nivel, mult, preco, raizVis) + detalhesHtml(ctx, m, t, esc.plano, sel, nivel, mult, preco) : semConta(ctx, X, fin)}${metodos(U)}`, "Ver como calculamos")}
    </section>`;
    el.innerHTML = `<div class="d-tela d-sel-${sel}">${abertura(h1, eco, apoio)}<div class="hi-slot"></div>
      ${avisosHtml(ctx, m)}${rsSel?.ok ? oitoHtml(ctx, c3, sel, agro) : agro ? "" : olho(OLHOS.agro)}${mais}</div>`; // sempre 1 "seu olho" à vista
    ligar(el, ctx);
    if (comVer) ligarCaixa(el, t, NOME[sel]);
    await HI.render(el.querySelector(".hi-slot"), ctx, hiOp);
    await U.montarExtras(el, ctx);
    reabrir(el, abertos);
  },
};

const abertura = (h1, eco, apoio) => `<div class="titulo-passo"><p class="kicker">Quanto rende</p>
  <h1>${h1}<span class="eco">${eco}</span></h1><p>${apoio}</p></div>`;
const ap = (agro, html) => (agro ? `<div class="apagado">${html}</div>` : html); // lavoura grande no IBGE: os R$ só comparam

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

// ---------- ponto 6: "em 8 de 10 anos…" e, no ver mais, a grade de 10 roças ----------
/** "Em 8 de 10 anos já vistos aqui, sobra pelo menos R$ X e você colhe pelo menos Y kg": o 2º pior décimo dos 28 anos (o plano
 *  escolhido já rodando, rs.oito_em_dez) e a comida (comida_kg.detalhe.oito_em_dez_kg), com o jeito de hoje embaixo. */
function oitoHtml(ctx, c3, sel, agro) {
  const { util: U } = ctx;
  const b = c3[sel]?.beneficios, x = b?.rs;
  if (!x?.ok) return "";
  const det = (bb) => bb?.itens?.find((i) => i.id === "comida_kg")?.detalhe || {};
  const kgTxt = (q) => `${U.num(Math.round(q / 10) * 10)} kg`;
  // grão e raiz de mandioca em dois números: 1 kg de raiz fresca não é 1 kg de grão
  const colhe = (d0, forte) => { const g = d0.oito_em_dez_kg, r = d0.oito_em_dez_raiz_kg, b2 = (t) => (forte ? `<b>${t}</b>` : t);
    return [g > 0 ? `${b2(kgTxt(g))} de grão` : "", r > 0 ? `${b2(kgTxt(r))} de raiz de mandioca` : ""].filter(Boolean).join(" e "); };
  const v = x.oito_em_dez, k = colhe(det(b), true), hj = c3.hoje?.beneficios, vh = hj?.rs?.ok ? hj.rs.oito_em_dez : null, kh = colhe(det(hj), false);
  const frase = v >= 0 ? `Sobra pelo menos <b>${rs(v)}</b>${k ? ` e colhe pelo menos ${k}` : ""}.`
    : `A perda não passa de <b>${rs(-v)}</b>${k ? `, e colhe pelo menos ${k}` : ""}.`;
  const hojeTxt = vh == null ? "" : `Hoje: ${vh >= 0 ? `sobra ${rs(vh)}` : `perde até ${rs(-vh)}`}${kh ? ` e ${kh}` : ""}.`;
  const fonte = `o ${NOME[sel]} já rodando (como em 2029), refeito em cada um dos ${x.info.anos} anos de ${x.info.ano0} a ${x.info.ano1} (${FONTE_PAM}); 8 em 10 = o 2º pior de cada 10 anos (P20); grão e raiz = rendimento do IBGE (kg/ha) × área; ${FONTE_CONAB}`;
  return `<section class="painel d-oito">
    ${rotulo(U, "escudo", `Em 8 de 10 anos já vistos aqui, por ano`, U.selo("projecao", fonte))}
    ${U.faixa("escudo", v >= 0 ? "verde" : "ambar", frase)}
    ${hojeTxt ? `<p class="frase pequeno">${U.esc(hojeTxt)}</p>` : ""}
    ${agro ? "" : olho(OLHOS.agro)}
    ${U.verMais(dezHtml(ctx, c3, sel), "Ver as 10 roças")}</section>`;
}

/** A grade de 10 roças (como no antigo "Se secar"): de 10 anos, em quantos a colheita quebra, nos três caminhos; e 2027, cada cultura
 *  do plano escolhido, nos anos parecidos (r.projecao). */
function dezHtml(ctx, c3, sel) {
  const { r, util: U } = ctx;
  const ROT = { hoje: "Hoje", melhor: "Melhorado", ideal: "Ideal" };
  const linhas = ["hoje", "melhor", "ideal"].map((t) => {
    const q = c3[t]?.beneficios?.rs?.ok ? c3[t].beneficios.rs.quebra : null;
    if (!q) return `<div class="d10-linha"><b>${ROT[t]}</b><span class="sub">sem conta aqui</span></div>`;
    const k = Math.round(q.p * 10);
    return `<div class="d10-linha${t === sel ? " sel" : ""}"><b>${ROT[t]}</b>${U.dezRocas(q.p, "var(--terra)", "anos de quebra")}
      <span>quebra em <b>${k} de 10</b> anos</span></div>`;
  }).join("");
  // 2027, cada cultura do plano escolhido (as que têm série no IBGE), nos anos de El Niño forte (o que o "Se secar" mostrava)
  const SER = [["Milho", /^milho/i], ["Feijão", /^feij/i], ["Mandioca", /^mandioca/i]];
  const no27 = new Set((c3[sel]?.plano?.faixas || []).filter((f) => f.parte !== "Bordas")
    .map((f) => f.anos?.[0]).filter((c) => c && !(c.cultura === "Mandioca" && !c.ja_no_chao)).map((c) => c.cultura)
    .map((c) => SER.find(([, re]) => re.test(c || ""))?.[0]).filter(Boolean));
  const cult = SER.map(([s]) => s).filter((s) => no27.has(s) && r.projecao?.[s]?.anos?.["2027"]).map((s) => {
    const q = r.projecao[s].anos["2027"].chance_quebra, n = Math.round((q ?? 0) * 10);
    return `<div class="d10-linha"><b>${U.esc(s)}</b>${U.dezRocas(q, "var(--terra)", `anos parecidos, ${s.toLowerCase()} quebra`)}
      <span>${n <= 0 ? "quase nunca quebra" : n >= 10 ? "quase sempre quebra" : `quebra em <b>${n} de 10</b>`}</span></div>`;
  }).join("");
  const qS = c3[sel]?.beneficios?.rs?.quebra;
  return `<p>Cada quadrado é 1 ano de 10. Em vermelho, o ano de quebra: a colheita vale menos da metade do normal dela.
      ${U.selo("projecao", "o roçado já rodando nos 28 anos do IBGE PAM (1998–2025); hoje: medido")}</p>
    <div class="d10">${linhas}</div>
    ${qS ? `<p class="pequeno sub">Nos ${qS.nEN} El Niños fortes da série, o ${NOME[sel]} quebrou em ${qS.enQ}.</p>` : ""}
    ${!cult && (c3[sel]?.plano?.faixas || []).length ? `<p class="pequeno sub">Em 2027 este plano não colhe milho, feijão nem mandioca.</p>` : ""}
    ${cult ? `<h4>2027, cada cultura ${U.selo("projecao", FONTE_PROJ)}</h4><div class="d10">${cult}</div>
      <p class="pequeno sub">Não é previsão: é o que a roça de ${U.esc(r.local.municipio)} colheu em anos de mar quente como o de agora, desde 1998.</p>` : ""}`;
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
    linhas.push(`<div class="ctrl">${rotulo(U, "faixas", "Hoje, como fica no roçado")}
      ${seg("arr", atual, [["junto", "Tudo junto"], ["pedacos", "Em pedaços"], ...(temB ? [["baixio", "Milho no baixio"]] : [])])}</div>`);
  }
  return `<div class="ajustar">${linhas.join("")}${temMand ? "" : olho(OLHOS.agro)}
    <a class="chip aj-mudar" href="${ctx.link(2)}" data-editar="hoje">${U.ic("milho")}Mudar o que planta ou quanto de cada</a></div>`;
}

function avisosHtml(ctx, m) {
  const { ef, util: U } = ctx;
  if (!m) return "";
  const out = [];
  const pl = m.itens[0].find((i) => i.plantada);
  if (ef.maniva === "plantada" && pl) out.push(`<span class="chip verde">${U.ic("mandioca")}mandioca já plantada: a ${U.esc(pl.parte)} colhe em 2027</span>`);
  for (const a of m.avisos || []) out.push(`<span class="chip ambar">${U.esc(a)}</span>`);
  return out.length ? `<div class="avisos-linha">${out.join("")}</div>` : "";
}

// ---------- 2027: os El Niños fortes ----------
function elNinoHtml(ctx, m, t, sel, nivel, mult) {
  const { util: U } = ctx;
  const nm = NOME[sel];
  const vals = t.elNino.flatMap((e) => [e.plano, e.s0]);
  const lo = Math.min(...vals), hi = Math.max(...vals);
  const cards = t.elNino.map((e) => `<div class="en-card"><div class="en-ano">${e.ano}</div>${G.mini(e.plano, e.s0, lo, hi)}
    <div class="en-val">${chave("plano")}${rs(e.plano)}</div><div class="en-val cinza">${chave("s0")}${rs(e.s0)}</div></div>`).join("");
  const n = t.elNino.length, atras = t.elNino.filter((e) => e.plano < e.s0).length;
  const semVenda = semVendaEm(m, 0);
  const depois = t.porAno[1].plano.p50 < t.porAno[1].s0.p50 && t.porAno[2].plano.p50 < t.porAno[2].s0.p50;
  const frase = atras === 0 ? `Nos ${n}, o ${nm} já deixa mais que o jeito de hoje em 2027.`
    : depois ? `Em ${vezes(atras, n)}, o ${nm} deixa menos em 2027, e continua abaixo depois.`
      : `Em ${vezes(atras, n)}, o ${nm} deixa menos em 2027${semVenda.length ? `: ${semVenda.join("; ")}` : ""}.`;
  const q = C.ano2027Qualquer(m, nivel, mult);
  return `<div class="legenda"><span>${chave("plano")}${nm}</span><span>${chave("s0")}jeito de hoje</span>
      <span class="chip terra mini">El Niño forte</span>${U.selo("medido", FONTE_PAM + "; anos com ONI ≥ 1,5 em out–dez/nov–jan")}</div>
    <div class="en-grade">${cards}</div>
    <p class="frase">${frase}</p>
    <p class="pequeno sub">O Pacífico de hoje está como nos ${n} El Niños fortes da série (${m.anosEN.join(", ")}). Cada cartão é o que o ${nm} e o jeito de hoje
      teriam deixado em 2027 aqui, naquele ano. São só ${n} anos: não é previsão. Se 2027 for um ano qualquer (os ${q.n} anos): ${nm} típico ${rs(q.plano.p50)},
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
function caixaHtml(ctx, t, sel) {
  const { util: U } = ctx;
  const nm = NOME[sel];
  const W = largura(620);
  const { svg } = G.caixa(t, W);
  let iMin = 0, ultimoAtras = -1;
  t.caixaPlano.forEach((q, i) => {
    if (q.p50 < t.caixaPlano[iMin].p50) iMin = i;
    if (q.p50 < t.caixaS0[i].p50 - 0.5) ultimoAtras = i;
  });
  const volta = ultimoAtras >= 0 && ultimoAtras < C.NMESES - 1 ? C.rotMes(ultimoAtras + 1) : null;
  const fundo = t.caixaPlano[iMin].p50;
  const partes = [fundo < 0 ? `Mais apertado: <b>${rs(fundo)}</b> em ${C.rotMes(iMin)}.` : `O caixa do ${nm} não fica negativo.`,
    ultimoAtras === -1 ? "Fica acima do jeito de hoje desde o começo." : volta ? `Passa o jeito de hoje em <b>${volta}</b>.` : "Termina abaixo do jeito de hoje."];
  return `<div class="legenda"><span>${chave("plano")}${nm}</span><span>${chave("s0")}jeito de hoje</span>
      <span>${U.ic("semente")}sai (plantio)</span><span>${U.ic("dinheiro")}entra (colheita)</span>${U.selo("projecao", SEQ)}</div>
    <div class="rola"><div class="rola-dentro caixa-wrap" style="min-width:${W}px">${svg}<div class="dica" hidden></div></div></div>
    <p class="frase">${partes.join(" ")}</p>
    <p class="pequeno sub">A linha é o caminho típico; a faixa vai do caso ruim (1 em 10) ao bom (9 em 10). O custo entra no mês do plantio e a colheita
      no meio da colheita, com os meses do calendário do plano (2028 e 2029 repetem os meses). A mandioca entra aos poucos nos meses de colheita.</p>
    <h4>Ano a ano</h4>${rolar(G.barrasAno(t.porAno, largura(320)), largura(320))}
    <p class="pequeno sub">A coluna é o ano típico; o traço vai do ano ruim ao bom. Em 2027, do pior ao melhor dos ${t.porAno[0].n} El Niños fortes.</p>`;
}

function ligarCaixa(el, t, nm) {
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
    dica.innerHTML = `<b>${C.rotMes(i)}</b><div>${chave("plano")}${nm} ${rs(p.p50)} <span>(${faixaRs(p.p10, p.p90)})</span></div>` +
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
function termoHtml(ctx, tS, tD, sel) {
  const { util: U } = ctx;
  const nm = NOME[sel];
  const cel = (a) => `<div class="medidor" title="${nm}: ${a.pagaPlano} de ${a.n}; hoje: ${a.pagaS0} de ${a.n}">
      <span class="trilho"><span class="cheio" style="width:${((a.pagaPlano / a.n) * 100).toFixed(1)}%"></span><span class="marca-s0" style="left:${((a.pagaS0 / a.n) * 100).toFixed(1)}%"></span></span>
      <b>${a.pagaPlano} de ${a.n}</b></div>`;
  const linhas = [0, 1, 2].map((k) => `<div class="termo-linha"><b class="ano">${2027 + k}</b>${cel(tS.porAno[k])}${cel(tD.porAno[k])}</div>`).join("");
  return `<div class="termo"><div class="termo-linha cab"><span></span><span>${CUSTO_TXT.semente}</span><span>${CUSTO_TXT.desembolso}</span></div>${linhas}</div>
    <p class="frase pequeno sub">${U.selo("projecao", `${SEQ}. ${FONTE_CONAB}`)} Barra = ${nm}; risco cinza = jeito de hoje. Em 2027, entre os ${tS.porAno[0].n} El Niños fortes; depois, entre os ${tS.porAno[1].n} anos.</p>`;
}

// ---------- Ver como calculamos ----------
/** Os 8 números de "O que você ganha" (ideal.beneficios), nos três caminhos: a mesma tabela do Plano, para conferir. */
function oitoNumeros(ctx, c3, sel) {
  const { util: U } = ctx;
  const T = ["hoje", "melhor", "ideal"], ROT = { hoje: "Hoje", melhor: "Melhorado", ideal: `Ideal (${c3.ideal?.plano?.nome || ""})` };
  const ref = c3[sel]?.beneficios?.itens || c3.hoje?.beneficios?.itens || [];
  // o mesmo formatador do "O que você ganha" do Plano (extras/ideal.js, textoItem): um número só nos dois lugares
  const fmt = (it) => {
    const tx = textoItem(U, it);
    return tx == null ? `<span class="sub" title="${U.esc(it?.fonte || "")}">não medido</span>` : U.esc(tx);
  };
  const linhas = ref.map((it0) => `<tr><td>${U.esc(it0.rotulo)} <small class="sub">(${U.esc(it0.unidade)})</small> ${U.selo(it0.selo, it0.fonte)}</td>
    ${T.map((t) => `<td${t === sel ? ' class="sel"' : ""}>${fmt(c3[t]?.beneficios?.itens?.find((x) => x.id === it0.id))}</td>`).join("")}</tr>`).join("");
  return `<h4>O que você ganha, nos três caminhos</h4>
    <div class="rola"><table class="tab-oito"><thead><tr><th></th>${T.map((t) => `<th${t === sel ? ' class="sel"' : ""}>${U.esc(ROT[t])}</th>`).join("")}</tr></thead><tbody>${linhas}</tbody></table></div>
    <p class="pequeno sub">Os mesmos números de "O que você ganha", no Plano (uma conta só). "Não medido": falta o dado; toque no selo para ver qual.
      Em 3 anos (2027 a 2029), sobra típica: ${T.map((t) => `${ROT[t].replace(/ \(.*/, "").toLowerCase()} ${c3[t]?.beneficios?.rs?.ok ? rs(c3[t].beneficios.rs.tres_anos.p50) : "sem conta"}`).join("; ")}.</p>`;
}

// ---------- replay de 28 anos ----------
function replayHtml(ctx, m, plano, sel, nivel, mult, preco, temMand) {
  const { util: U } = ctx;
  const rows = C.replay(m, nivel, mult), nm = NOME[sel];
  const acima = rows.filter((x) => x.plano > x.s0).length;
  const tiles = rows.map((x) => `<i class="${x.plano > x.s0 ? "ac" : "ab"}${m.anosEN.includes(x.ano) ? " en" : ""}" title="${x.ano}: ${nm} ${rs(x.plano)} · hoje ${rs(x.s0)}"></i>`).join("");
  const desc = plano.faixas.filter((f) => f.parte !== "Bordas" && (f.parte !== "Baixio" || m.b > 0)).map((f) => {
    const its = m.itens[2].filter((i) => i.parte === f.parte), c = f.anos[2].cultura;
    const tx = its.some((i) => i.serie === "Mandioca") ? "colhe a mandioca" : its.some((i) => i.custo === "Mandioca") ? "recebe a maniva" :
      f.parte === "Baixio" && c === "Milho" && plano.leguminosa && !f.anos[2].solteiro ? `milho + ${plano.leguminosa.toLowerCase()}` : c.toLowerCase();
    return `${f.parte === "Baixio" ? "baixio" : f.parte}: ${tx}`;
  }).join("; ");
  // o plano nunca esteve no chão: a conta é refeita com as colheitas medidas (por isso SUPOSIÇÃO, não MEDIDO)
  return `<h4>Os 28 anos: se o ${nm} estivesse no chão desde 1998 ${U.selo("suposicao", `refeito com as colheitas medidas do ${FONTE_PAM}`)}</h4>
    <div class="faixa28">${tiles}</div>
    <div class="faixa28-eixo"><span>${rows[0].ano}</span><span class="leg"><i class="ac"></i>${nm} acima <i class="ab"></i>abaixo <i class="en-leg"></i>El Niño forte</span><span>${rows[rows.length - 1].ano}</span></div>
    <p class="frase">O ${nm} ficou acima do jeito de hoje em <b>${acima} de ${rows.length} anos</b>.</p>
    <p>O ${nm} já rodando (${U.esc(desc)}) contra o jeito de hoje, no mesmo ano${temMand ? `, com a raiz a R$ ${U.num(preco, 2)}/kg` : ""}.</p>
    ${rolar(G.replay(rows, m.anosEN, largura(600)), largura(600))}`;
}

function culturaTabela(fin, U) {
  const linhas = ["Milho", "Feijão", "Mandioca"].map((s) => {
    const c = fin.culturas?.[s];
    if (!c) return `<tr><td>${s}</td><td colspan="6" class="sub">o IBGE não tem a série de ${s.toLowerCase()} aqui (menos de 10 anos com 10 ha ou mais)</td></tr>`;
    const v = c.valor_ha || {};
    return `<tr><td>${s}${c.aviso ? `<br><small class="sub">${U.esc(c.aviso)}</small>` : ""}</td><td>${rs(v.min)}</td><td>${rs(v.p50)}</td><td>${rs(v.max)}</td>
      <td>${c.el_nino_forte === null ? "—" : rs(c.el_nino_forte)}</td><td>${rs(c.ultimos?.["2025"])}</td>
      <td>R$ ${U.num(c.preco_kg, 2)}/kg${c.origem_preco !== "município" ? ` (${U.esc(c.origem_preco)})` : ""}<br><small class="sub">semente ${rs(c.custo_ha?.semente)} · desembolso ${rs(c.custo_ha?.desembolso)}</small></td></tr>`;
  }).join("");
  return `<div class="rola"><table class="tab-cult"><thead><tr><th>por ha plantado</th><th>pior ano</th><th>típico</th><th>melhor</th><th>El Niño forte</th><th>2025</th><th>preço e custo</th></tr></thead>
    <tbody>${linhas}</tbody></table></div><p class="pequeno sub">${U.selo("medido", FONTE_PAM + "; " + FONTE_CONAB)} Valor da colheita por ha (vender ou comer, a preço da região), antes do custo.</p>`;
}

function detalhesHtml(ctx, m, t, plano, sel, nivel, mult, preco) {
  const { r, util: U } = ctx;
  const fin = r.financeiro, nm = NOME[sel];
  const ha = (v) => U.ha(Math.round(v * 100) / 100);
  const porAno = [0, 1, 2].map((k) => {
    const its = m.itens[k];
    const txt = [...new Set(its.map((i) => {
      if (i.serie === "Mandioca") return `${i.parte}: ${i.plantada ? "colhe a mandioca já plantada" : "colhe a mandioca"}`;
      if (i.custo === "Mandioca") return `${i.parte}: maniva (só custo)`;
      if (i.uso) return `${i.parte}: ${i.cultura.toLowerCase()} (forragem: só custo)`;
      if (i.parte === "Baixio") return `Baixio: ${[...new Set(its.filter((j) => j.parte === "Baixio").map((j) => j.cultura.toLowerCase()))].join(" + ")}`;
      return `${i.parte}: ${i.cultura.toLowerCase()}`;
    }))].join("; ");
    return `<li><b>${2027 + k}</b> (${k === 0 ? `um dos ${t.nEN} El Niños fortes` : `um dos ${t.nAnos} anos`}): ${U.esc(txt)}</li>`;
  }).join("");
  const tab = t.porAno.map((a) => `<tr><td>${a.ano}</td><td>${rs(a.plano.p10)} · <b>${rs(a.plano.p50)}</b> · ${rs(a.plano.p90)}</td>
    <td>${rs(a.s0.p10)} · <b>${rs(a.s0.p50)}</b> · ${rs(a.s0.p90)}</td><td>${a.planoFrente} de ${a.n}</td></tr>`).join("");
  const c = fin.calibracao || {}, cob = c.faixa_p10_p90_cobriu_fora_da_amostra || {}, mm = c.min_max_cobriu_fora_da_amostra || {};
  const avisos = (fin.avisos || []).filter((a) => !/não é lucro|fora da conta/.test(a));
  const fora = (plano.fora_do_giro || []).filter((x) => x.ha > 0);
  return `<h4>O que é cada número</h4>
    <p>"Sobra" = valor da colheita (vender ou comer, a preço da região) menos o custo escolhido. Nunca é lucro: a mão de obra da família não entra.
      ${U.esc(cap(nm))} em 3 anos: típico ${rs(t.plano.p50)}, ${faixaRs(t.plano.p10, t.plano.p90)} (caso ruim = 1 em cada 10; bom = 9 em cada 10).
      Jeito de hoje: típico ${rs(t.s0.p50)}, ${faixaRs(t.s0.p10, t.s0.p90)}. Em ${U.num(t.aFrente * 100)} de 100 combinações, o ${nm} termina com mais que o jeito de hoje.
      ${nivel === "desembolso" ? "Custo: desembolso da CONAB (máquina, insumos e serviços)." : "Custo: só a semente (CONAB)."}</p>
    <h4>Áreas ${U.selo("suposicao", SUP_AREA)}</h4>
    <p>Roçado do giro de ${ha(m.T)}: ${m.b > 0 ? `baixio de ${ha(m.b)}${m.baixioNaoSei ? " (não respondido: ⅓ do roçado)" : ""} e ` : ""}cada parte (A, B e C) com ${ha(m.a)}.
      As bordas não tiram área.${fora.length ? ` ${U.esc(fora.map((x) => `${x.cultura.toLowerCase()} (${ha(x.ha)})`).join(", "))}: já plantado, fica fora do giro em todos os caminhos.` : ""}</p>
    <h4>O que entra em cada ano (${U.esc(nm)})</h4><ul>${porAno}</ul>
    <p>Mandioca: o custo da maniva entra no ano do plantio; a receita, no ano seguinte. Preço da raiz: R$ ${U.num(preco ?? 0, 2)}/kg
      (a série do IBGE usa R$ ${U.num(m.precoRefMand ?? 0, 2)}/kg; a mandioca é multiplicada por ${U.num(mult, 2)}).</p>
    <h4>As combinações de anos ${U.selo("projecao", SEQ)}</h4>
    <p>2027 é um dos El Niños fortes (${m.anosEN.join(", ")}); 2028 e 2029, qualquer um dos ${m.anos.length} anos de 1998 a 2025. O mesmo ano vale para todas as
      culturas e para os três caminhos (a chuva é a mesma no roçado todo). ${t.nEN} × ${t.nAnos} × ${t.nAnos} = ${t.n.toLocaleString("pt-BR")} combinações, todas contadas,
      sem sorteio. Sem tendência nem previsão de série: aqui um ano quase não se parece com o anterior (autocorrelação de 0,2).</p>
    <div class="rola"><table><thead><tr><th>ano</th><th>${U.esc(nm)}: P10 · P50 · P90</th><th>hoje: P10 · P50 · P90</th><th>${U.esc(nm)} com mais</th></tr></thead><tbody>${tab}</tbody></table></div>
    <h4>Calibrador honesto</h4>
    <p>Num teste fora da amostra (faixa de 1998–2015 conferida em 2016–2025), a faixa P10–P90 de um ano acertou
      ${Object.entries(cob).map(([k, v]) => `${k.toLowerCase()} ${U.emDez(v)}`).join(", ")} anos (deveria ser 8 em 10); do pior ao melhor ano já visto,
      ${Object.entries(mm).map(([k, v]) => `${k.toLowerCase()} ${U.emDez(v)}`).join(", ")}. O futuro varia mais que o passado.</p>
    <h4>Por cultura</h4>${culturaTabela(fin, U)}
    <h4>Fora da conta</h4>
    <ul><li>Forragem (sorgo, milheto, palma, gliricídia): comida da criação, fora do R$. Só entra o custo da semente do sorgo e do milheto (${rs(fin.custo_sorgo_forrageiro_ha?.[nivel])}/ha,
      ${U.selo("suposicao", fin.custo_sorgo_forrageiro_ha?.origem || "lavoura anual manual")}).</li>
      <li>Culturas sem série do IBGE no município (amendoim, sorgo de grão, algodão, mamona, girassol, caju, banana, cana…): fora do R$, com a área delas.</li>
      <li>Garantia-Safra (perda de 40% ou mais, até 5 ha; o valor não foi conferido), mão de obra, frete e casa de farinha.</li>
      <li>O ganho de rendimento da rotação contra o consórcio de hoje (não medido) e o preço futuro (fica o de 2016–2025, em R$ de 2025).</li>
      <li>Rendimento acima de 2× o da roça de família da CONAB (milho 1.800, feijão 800, mandioca 17.400 kg/ha) marca lavoura grande na série.</li></ul>
    ${avisos.length ? `<h4>Avisos dos dados</h4><ul>${avisos.map((a) => `<li>${U.esc(a)}</li>`).join("")}</ul>` : ""}`;
}
const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);

// ---------- ponto 4 (comparar abordagens): os 7 jeitos testados para a faixa de "8 em 10" (vinha do "Se secar", que saiu da jornada) ----------
// analise/projecao.md, seção 3, linha "WF, todos · média por ano" (os mesmos números de passos/seguranca.js, METODOS e CALIB)
const METODOS = [
  ["F", "região + El Niño, alargado pelo teste (o escolhido)", 79], ["C", "município puxado para a região", 69], ["A", "só o município", 67],
  ["D", "só os anos de El Niño", 65], ["B", "tirando a tendência", 61], ["D2", "El Niño + tendência", 60], ["E", "regressão por quantis, tudo junto", 56],
];
function metodos(U) {
  return `<h4>Testamos 7 jeitos de ler o passado ${U.selo("medido", "analise/projecao.md, seção 3: teste só com o passado (walk-forward 2008–2025), 1.783 municípios; média por ano da cobertura da faixa de 8 em 10; o escolhido refeito com a definição única de El Niño em dados/projecao_metricas.txt (14/11/2026): 79 (antes, 78)")}</h4>
    <p>Ficou o que mais acertou. A regressão por quantis falhou no milho: 26 em 100.</p>
    <div class="seg-metodos" role="list">${METODOS.map(([k, rot, v]) => `<div class="seg-met${k === "F" ? " on" : ""}" role="listitem">
      <span class="seg-met-rot">${U.esc(rot)}</span><span class="seg-met-trilho"><i style="width:${v}%"></i><b class="seg-met-meta" title="meta: 80"></b></span>
      <span class="seg-met-val">${v}</span></div>`).join("")}</div>
    <p class="pequeno sub">Acerto em 100 casos: o ano real caiu dentro da faixa de 8 em 10 (meta: 80).</p>`;
}

// ---------- sem conta do plano escolhido (vai no "Ver como calculamos": o aviso à vista é o da comparação) ----------
function semConta(ctx, X, fin) {
  const { util: U } = ctx;
  if (!fin) return `<p>Sem dados do IBGE para este município: não inventamos número.</p>`;
  return `<h4>O que falta aqui</h4><p>${X.falta.length ? `${U.esc(X.falta.join("; "))}. ` : ""}Para comparar com o jeito de hoje no mesmo ano, cada cultura
    precisa de 10 anos ou mais com 10 ha plantados ou mais (IBGE, 1998–2025). Abaixo, só o que existe daqui, por ha plantado.</p>${culturaTabela(fin, U)}`;
}
