// QUADRA, passo 4 "Quanto rende": o retorno do plano de rotação, refeito nos anos que já aconteceram no município.
// Método e textos: analise/financeiro.md (seções 2, 4 e 6), analise/perguntas.md ("Seu bolso"), decisões 7 e 9 do
// PLANO_INTEGRACAO.md. Contas em js/passos/dinheiro/calculo.js; gráficos em js/passos/dinheiro/graficos.js.
import * as C from "./dinheiro/calculo.js";
import * as G from "./dinheiro/graficos.js";

const { rs, faixaRs } = G;
const SEQ = "3.136 sequências (4 El Niños fortes × 28 × 28 anos do IBGE), enumeradas, sem sorteio";
const FONTE_PAM = "IBGE PAM 1998–2025: rendimento por ha plantado × preço de referência do município, em R$ de 2025 (IPCA)";
const FONTE_CONAB = "CONAB, custos de produção do NE (semente e desembolso), R$ de 2025";
const SUP_AREA = "Partes A, B e C do mesmo tamanho; bordas não tiram área; baixio = metade milho + metade caupi por ha; forragem sem R$";

const op = (chave, valor, atual, texto, sub = "") =>
  `<button type="button" class="op${valor === atual ? " on" : ""}" data-set="${chave}=${valor}" aria-pressed="${valor === atual}">` +
  `${texto}${sub ? `<small>${sub}</small>` : ""}</button>`;
const kg = (v) => `${(v >= 1000 ? Math.round(v / 10) * 10 : Math.round(v)).toLocaleString("pt-BR")} kg`;
const vezes = (k, n, unid = "anos") => `${k} de ${n} ${unid}`;
/** Largura útil do cartão (px): os gráficos desenham na escala 1:1 e só rolam de lado quando não cabem (celular). */
const largura = (min) => {
  const w = globalThis.innerWidth || 1000;
  return Math.round(Math.max(min, Math.min(1180, w) - (w <= 760 ? 70 : 80)));
};
const rolar = (svg, w) => `<div class="rola"><div class="rola-dentro" style="min-width:${w}px">${svg}</div></div>`;

export default {
  id: "dinheiro",
  titulo: "Quanto rende",
  render(el, ctx) {
    const { r, ef, util: U } = ctx;
    const fin = r.financeiro, mun = r.local.municipio;
    const m = C.montar(r, ef);
    const pr = fin?.precos_raiz || {};
    const temMand = !!m.usadas?.includes("Mandioca");
    let raiz = ef.raiz, preco = pr[raiz];
    if (!(preco > 0)) { raiz = "municipio"; preco = pr.municipio ?? m.precoRefMand; }
    const mult = m.precoRefMand && preco ? preco / m.precoRefMand : 1;
    const nivel = ef.custo === "desembolso" ? "desembolso" : "semente";
    const SOBRA = nivel === "semente" ? "Sobra depois da semente" : "Sobra depois de máquina e insumos";

    const topo = `<div class="titulo-passo"><h1>Quanto rende</h1><p>O plano do seu roçado refeito nos anos que já aconteceram em
      <b>${U.esc(mun)}</b> (IBGE, 1998–2025, em R$ de 2025), contra o jeito de hoje: milho + feijão na roça toda. Não é previsão
      do ano: é o que teria acontecido aqui, com o mesmo ano para todas as culturas.</p></div>`;
    const bolso = bolsoHtml(ctx, m, pr, raiz, nivel, temMand);

    if (!m.ok) {
      el.innerHTML = topo + bolso + semConta(m, fin, U);
      ligar(el, ctx);
      return;
    }

    const t = C.calcular(m, nivel, mult);
    const tS = nivel === "semente" ? t : C.calcular(m, "semente", mult);
    const tD = nivel === "desembolso" ? t : C.calcular(m, "desembolso", mult);
    const agro = m.agro.length > 0;
    const calib = calibracao(fin, m);

    const avisos = avisosHtml(ctx, m, fin, agro);
    const partes = {
      destaque: destaqueHtml(ctx, m, t, nivel, mult, pr, temMand, agro, SOBRA),
      cartoes: cartoesHtml(ctx, m, t, calib, SOBRA),
      barras: barrasHtml(ctx, t, SOBRA),
      caixa: caixaHtml(ctx, m, t, nivel),
      elnino: elNinoHtml(ctx, m, t, nivel, mult, SOBRA),
      termo: termoHtml(ctx, m, tS, tD),
      replay: replayHtml(ctx, m, nivel, mult, preco, temMand, SOBRA),
      detalhes: detalhesHtml(ctx, m, fin, t, calib, nivel, mult, preco),
    };
    const ordem = ef.prioridade === "garantir"
      ? ["elnino", "cartoes", "barras", "caixa", "termo", "replay"]
      : ["cartoes", "barras", "caixa", "elnino", "termo", "replay"];
    const corpo = ordem.map((k) => partes[k]).join("");
    el.innerHTML = topo + bolso + avisos + partes.destaque + (agro ? `<div class="apagado">${corpo}</div>` : corpo) + partes.detalhes;
    ligar(el, ctx);
    ligarCaixa(el, t);
  },
};

// ---------- Seu bolso ----------
function bolsoHtml(ctx, m, pr, raiz, nivel, temMand) {
  const { ef, r, util: U } = ctx;
  const ha = U.ha(ef.ha);
  const temB = m.temBaixio ?? ef.tem_baixio !== false, b = m.b ?? ef.baixio_ha;
  const area = temB && b > 0
    ? `${ha}, com ${U.ha(b)} de baixio${ef.tem_baixio === null ? " (se você tiver baixio: não respondido, a conta usa ⅓)" : ""}`
    : `${ha}, sem baixio`;
  const orig = ef.ha_origem === "resposta" ? "" : ` <span class="sub">(${U.esc(ef.ha_origem)})</span>`;
  const oni = r.este_ano?.oni;
  const porque = ef.prioridade_origem === "resposta" ? "" :
    ef.prioridade_origem.includes("alerta")
      ? `Sugerimos <b>garantir</b> porque aqui 2027 é ano de alerta de El Niño${oni ? ` (o Pacífico está +${U.num(oni, 1)} °C acima do normal)` : ""}. Mude se quiser.`
      : `Sugerimos <b>equilibrar</b>: aqui o El Niño dá ${U.esc(r.este_ano?.nivel_alerta || "sinal fraco")}. Mude se quiser.`;
  const ufTxt = r.local.uf;
  const raizOps = temMand ? `
    <div class="pergunta"><span class="q">Por quanto você vende a raiz da mandioca?</span><div class="ops">
      ${pr.municipio > 0 ? op("raiz", "municipio", raiz, `o preço daqui`, `R$ ${U.num(pr.municipio, 2)}/kg${pr.origem_municipio && pr.origem_municipio !== "município" ? ` (da ${pr.origem_municipio})` : ""}`) : ""}
      ${pr.uf_mediana > 0 ? op("raiz", "uf_mediana", raiz, `o preço comum no ${ufTxt}`, `R$ ${U.num(pr.uf_mediana, 2)}/kg`) : ""}
      ${pr.uf_p25 > 0 ? op("raiz", "uf_p25", raiz, `um preço baixo no ${ufTxt}`, `R$ ${U.num(pr.uf_p25, 2)}/kg`) : ""}
    </div><p class="nota">É o número que mais muda a conta. Muita gente plantando mandioca ao mesmo tempo pode baixar o preço.
      ${U.selo("medido", "mediana 2016–2025 do preço implícito do IBGE (município) e mediana e 1º quartil da UF; escolher é suposição")}</p></div>`
    : `<div class="pergunta"><span class="q">Preço da raiz</span><p class="nota">O plano daqui não usa mandioca: o preço da raiz não muda nada.</p></div>`;
  const gs = ef.gs, cabe = ef.ha <= 5;
  const gsTxt = gs === "sim"
    ? `O Garantia-Safra paga quando a perda chega a 40% ou mais. O valor dele não entra nesta conta.`
    : gs === "nao"
      ? (cabe ? `Com ${ha} você cabe no limite de 5 ha. Vale procurar a secretaria de agricultura ou o sindicato para a inscrição. O valor não entra nesta conta.`
        : `Com ${ha} você passa do limite de 5 ha do Garantia-Safra.`)
      : `A regra: até 5 ha plantados e perda de 40% ou mais. Com ${ha} você ${cabe ? "cabe" : "não cabe"} no limite. O valor não entra nesta conta.`;
  return `<section class="cartao bolso" aria-label="Seu bolso">
    <div class="bolso-topo"><h2>Seu bolso</h2><span class="area">Seu roçado: <b>${area}</b>${orig} · <a href="${ctx.link(2)}">mudar</a></span></div>
    <div class="pergunta"><span class="q">O que vale mais para você neste ano?</span><div class="ops">
      ${op("prioridade", "garantir", ef.prioridade, "Garantir a comida e a criação", "mesmo ganhando menos")}
      ${op("prioridade", "equilibrar", ef.prioridade, "Equilibrar")}
      ${op("prioridade", "vender", ef.prioridade, "Vender e ganhar mais", "aceito mais risco")}
    </div>${porque ? `<p class="nota">${porque}</p>` : ""}</div>
    ${raizOps}
    <div class="pergunta"><span class="q">O que você paga para plantar?</span><div class="ops">
      ${op("custo", "semente", nivel, "só a semente", "a mão de obra é da família")}
      ${op("custo", "desembolso", nivel, "pago máquina e insumos", "o desembolso da CONAB")}
    </div><p class="nota">Os dois são réguas da CONAB: "só a semente" é otimista, "máquina e insumos" é pessimista para o roçado.
      ${U.selo("medido", FONTE_CONAB)}</p></div>
    <div class="pergunta"><span class="q">Você está inscrito no Garantia-Safra?</span><div class="ops">
      ${op("gs", "sim", gs, "sim")}${op("gs", "nao", gs, "não")}${op("gs", "nao_sei", gs === "sim" || gs === "nao" ? gs : "nao_sei", "não sei")}
    </div><p class="nota">${gsTxt}</p></div>
  </section>`;
}

function ligar(el, ctx) {
  el.addEventListener("click", (ev) => {
    const b = ev.target.closest("[data-set]");
    if (!b) return;
    const [k, v] = b.dataset.set.split("=");
    ctx.set({ [k]: v });
  });
}

// ---------- avisos ----------
function avisosHtml(ctx, m, fin, agro) {
  const { ef, util: U } = ctx;
  const out = [];
  if (agro) {
    const a = m.agro.map((x) => `${x.cultura.toLowerCase()} ${U.num(x.kg)} kg/ha (${U.num(x.kg / x.conab, 1)}× os ${U.num(x.conab)} kg/ha da roça familiar da CONAB)`).join("; ");
    out.push(`<div class="aviso vermelho"><b>Aqui o IBGE mistura lavoura empresarial.</b> Rendimento mediano do município: ${a}.
      Os R$ abaixo não são os de uma roça de família; servem só para comparar o plano com o jeito de hoje.
      ${U.selo("medido", "IBGE PAM 1998–2025 e planilhas da agricultura familiar da CONAB (2015+)")}</div>`);
  }
  if (ef.maniva === "plantada" && m.itens[0].some((i) => i.plantada)) {
    out.push(`<div class="aviso verde">Você já tem mandioca plantada: a Parte A colhe essa raiz em 2027, e a maniva nova sai dela.
      A receita dessa raiz entra já em 2027. ${U.selo("suposicao", "a mandioca de 2026 rende como a do município no ano sorteado para 2027; colhida aos poucos")}</div>`);
  }
  for (const a of m.avisos) out.push(`<div class="aviso">${U.esc(a)}</div>`);
  if (m.semRs.length) {
    out.push(`<div class="aviso">${U.esc(m.semRs.join(", "))}: sem série do IBGE aqui, ${m.semRs.length > 1 ? "ficam" : "fica"} sem R$ e sem custo nesta conta.</div>`);
  }
  return out.join("");
}

// ---------- destaque (muda com a prioridade) ----------
function destaqueHtml(ctx, m, t, nivel, mult, pr, temMand, agro, SOBRA) {
  const { ef, util: U } = ctx;
  if (agro) {
    return `<section class="cartao destaque apagado-destaque"><p>Sem número de destaque aqui: com lavoura empresarial na série, a média do
      município não diz quanto rende uma roça de família. Os gráficos abaixo mostram só a comparação, em tom apagado.</p></section>`;
  }
  const frente = Math.round(t.aFrente * 100);
  if (ef.prioridade === "garantir") {
    const com = C.comida2027(m);
    const g = com.map((x) => x.graoPlano), rz = com.map((x) => x.raizPlano), g0 = com.map((x) => x.graoS0);
    const rng = (a) => `${kg(Math.min(...a))} a ${kg(Math.max(...a))}`;
    const usoParts = [...new Set(m.itens[0].filter((i) => i.uso).map((i) => i.parte))];
    return `<section class="cartao destaque"><span class="rotulo">Para garantir: o caso ruim primeiro</span>
      <p class="frase-grande">Num caso ruim (1 em cada 10 sequências de anos já vistos aqui), o plano termina 2027–2029 com
      <b>${rs(t.plano.p10)}</b>; o jeito de hoje, com <b>${rs(t.s0.p10)}</b>.</p>
      <p>Comida em 2027, se for como os El Niños de antes: o plano colhe de ${rng(g)} de grão (feijão e milho)${Math.max(...rz) > 0 ? ` e de ${rng(rz)} de raiz` : ""};
      o jeito de hoje, de ${rng(g0)} de grão.${usoParts.length ? ` A forragem (${usoParts.join(", ")}) fica para a criação, sem R$.` : ""}
      ${U.selo("medido", "kg por ha plantado do IBGE PAM nos anos de El Niño forte × as áreas do plano")} ${U.selo("suposicao", SUP_AREA)}</p>
      ${t.ganho.p50 < 0 ? motivoPerde(m) : ""}
      <p class="pequeno sub">${SOBRA}, somando os 3 anos. Depois vem o que aconteceu aqui nos ${m.anosEN.length} El Niños fortes.</p></section>`;
  }
  if (ef.prioridade === "vender" && temMand) {
    const ops = [["municipio", "daqui"], ["uf_mediana", `comum no ${ctx.r.local.uf}`], ["uf_p25", `baixo no ${ctx.r.local.uf}`]]
      .filter(([k]) => pr[k] > 0).map(([k, nome]) => ({ k, nome, p: pr[k], tt: C.totais(m, nivel, pr[k] / m.precoRefMand) }));
    const emp = C.precoEmpate(m, nivel);
    const linhas = ops.map((o) => `<tr class="${o.p === pr[ef.raiz] ? "on" : ""}"><td>raiz a R$ ${U.num(o.p, 2)}/kg <span class="sub">(${o.nome})</span></td>
      <td><b>${sinal(o.tt.ganho.p50)}</b> <span class="sub">${faixaSinal(o.tt.ganho.p10, o.tt.ganho.p90)}</span></td>
      <td>${Math.round(o.tt.aFrente * 100)} de 100</td></tr>`).join("");
    return `<section class="cartao destaque"><span class="rotulo">Para vender: o típico e o preço da raiz</span>
      <p class="frase-grande">Típico em 3 anos: o plano ${deixa(t.plano.p50)}, ${sinal(t.ganho.p50)} que o jeito de hoje (${rs(t.s0.p50)}).</p>
      <table class="sens"><thead><tr><th>Se a raiz valer</th><th>plano − hoje, em 3 anos (típico e faixa)</th><th>plano à frente</th></tr></thead><tbody>${linhas}</tbody></table>
      <p>${emp === null ? "" : emp === 0 ? "O plano fica à frente mesmo com a raiz de graça." : `O plano empata com o jeito de hoje (típico) se a raiz valer <b>R$ ${U.num(emp, 2)}/kg</b>.`}
      ${U.selo("projecao", SEQ)}</p><p class="pequeno sub">${SOBRA}. Preço fixo em R$ de 2025: não dá para prever o preço de 2028.</p></section>`;
  }
  return `<section class="cartao destaque"><span class="rotulo">${ef.prioridade === "vender" ? "Para vender" : "Para equilibrar"}: o típico, com a faixa</span>
    <p class="frase-grande">Típico em 3 anos: o plano ${deixa(t.plano.p50)} e o jeito de hoje ${deixa(t.s0.p50)}:
    o plano fica ${t.ganho.p50 >= 0 ? `${rs(t.ganho.p50)} à frente` : `${rs(-t.ganho.p50)} atrás`} (${faixaSinal(t.ganho.p10, t.ganho.p90)}).</p>
    ${t.ganho.p50 < 0 ? motivoPerde(m) : ""}
    <p class="pequeno sub">${SOBRA}, somando 2027, 2028 e 2029. O plano termina à frente em ${frente} de 100 sequências de anos já vistos. ${U.selo("projecao", SEQ)}</p></section>`;
}
/** Partes do roçado que no ano k só têm custo (maniva, forragem): "a maniva (Parte A) e o sorgo forrageiro (Partes B e C)". */
function semVendaEm(m, k) {
  const g = new Map();
  for (const i of m.itens[k]) {
    if (!i.custo || m.itens[k].some((j) => j.serie && j.parte === i.parte)) continue;
    const nome = i.cultura === "Mandioca" ? "a maniva" : `o ${i.cultura.toLowerCase()}`;
    const ps = g.get(nome) || [];
    if (!ps.includes(i.parte)) ps.push(i.parte);
    g.set(nome, ps);
  }
  return [...g].map(([nome, ps]) => `${nome} (${ps.length > 1 ? "Partes " + ps.map((x) => x.replace("Parte ", "")).join(" e ") : ps[0]})`);
}

/** "deixa R$ 7.740" ou, quando o custo passa a colheita, "fica em −R$ 7.740". */
const deixa = (v) => (v >= 0 ? `deixa <b>${rs(v)}</b>` : `fica em <b>${rs(v)}</b>`);
const sinal = (v) => (v >= 0 ? `${rs(v)} a mais` : `${rs(-v)} a menos`);
const faixaSinal = (lo, hi) => `de ${lo >= 0 ? "+" : ""}${rs(lo)} a ${hi >= 0 ? "+" : ""}${rs(hi)}`;

/** Por que o plano perde em R$ aqui: o que ele planta sem preço e se falta a mandioca. */
function motivoPerde(m) {
  const uso = [...new Set([0, 1, 2].flatMap((k) => m.itens[k].filter((i) => i.uso).map((i) => i.cultura.toLowerCase())))];
  const partes = [];
  if (!m.usadas.includes("Mandioca")) partes.push("o plano daqui não tem mandioca");
  if (uso.length) partes.push(`parte da roça fica com ${uso.join(" e ")} para a criação, que não tem preço no IBGE`);
  if (m.agro.length) partes.push("o milho e o feijão do IBGE daqui são de lavoura empresarial");
  return partes.length ? `<p>Por que o plano perde aqui em dinheiro: ${partes.join("; ")}. O ganho dele (comida da criação, solo, menos praga) fica fora desta conta.</p>` : "";
}

// ---------- cartões ----------
function calibracao(fin, m) {
  const c = fin.calibracao || {};
  const f = c.faixa_p10_p90_cobriu_fora_da_amostra || {}, mm = c.min_max_cobriu_fora_da_amostra || {};
  const v = m.usadas.map((s) => f[s]).filter(Number.isFinite), w = m.usadas.map((s) => mm[s]).filter(Number.isFinite);
  const media = (a) => (a.length ? a.reduce((s, x) => s + x, 0) / a.length : null);
  return { p10p90: media(v), minmax: media(w), por: f };
}

function cartoesHtml(ctx, m, t, calib, SOBRA) {
  const { util: U } = ctx;
  const N = Math.round(t.aFrente * 100);
  const nTxt = N === 100 && t.aFrente < 1 ? "mais de 99" : N === 0 && t.aFrente > 0 ? "menos de 1" : String(N);
  return `<div class="grade-3 cartoes-fin">
    <div class="cartao c-fin"><h3><i class="chave m-plano"></i>O plano, 2027–2029</h3>
      <div class="faixa-grande">${faixaRs(t.plano.p10, t.plano.p90)}</div><div class="tipico">típico ${rs(t.plano.p50)}</div>
      <p class="pequeno sub">${SOBRA}, somando os 3 anos, em ${U.ha(m.T)}</p></div>
    <div class="cartao c-fin"><h3><i class="chave m-s0"></i>Do jeito de hoje</h3>
      <div class="faixa-grande">${faixaRs(t.s0.p10, t.s0.p90)}</div><div class="tipico">típico ${rs(t.s0.p50)}</div>
      <p class="pequeno sub">milho + feijão nos ${U.ha(m.T)}, no mesmo ano</p></div>
    <div class="cartao c-fin"><h3>Quem termina à frente</h3>
      <div class="numero-grande">${nTxt} <small>de 100</small></div>
      <p class="pequeno sub">sequências de anos já vistos aqui terminam 2029 com o plano à frente</p></div>
  </div>
  <p class="calibra">${U.selo("projecao", SEQ)} ${U.selo("suposicao", SUP_AREA)} A faixa vai da sequência ruim (1 em 10) à boa (9 em 10).
    É larga de propósito: num teste fora da amostra, a faixa de um ano acertou ${U.emDez(calib.p10p90)} anos${calib.minmax ? `, e a do pior ao melhor ano já visto, ${U.emDez(calib.minmax)}` : ""}.
    O futuro varia mais que o passado. Nunca é lucro: é o valor da colheita (vender ou comer) menos o custo escolhido.</p>`;
}

const legenda = (a = "o plano", b = "o jeito de hoje") =>
  `<div class="legenda"><span><i class="chave m-plano"></i>${a}</span><span><i class="chave m-s0"></i>${b}</span></div>`;

// ---------- barras por ano ----------
function barrasHtml(ctx, t, SOBRA) {
  const { util: U } = ctx;
  const [a7, a8, a9] = t.porAno;
  const frase = a7.plano.p50 < a7.s0.p50 && a8.plano.p50 >= a8.s0.p50
    ? "2027 é o ano que custa; 2028 e 2029 pagam."
    : a7.plano.p50 >= a7.s0.p50 && a8.plano.p50 >= a8.s0.p50 && a9.plano.p50 >= a9.s0.p50
      ? "O plano fica à frente no ano típico de cada um dos 3 anos."
      : a8.plano.p50 < a8.s0.p50 && a9.plano.p50 < a9.s0.p50
        ? "No ano típico, o plano deixa menos dinheiro que o jeito de hoje nos 3 anos."
        : "O plano e o jeito de hoje se alternam ano a ano.";
  return `<section class="cartao"><h2>Ano a ano</h2>
    <p class="sub">A coluna é o ano típico; o traço vai do ano ruim ao bom (1 em 10 a 9 em 10). Em 2027, do pior ao melhor dos ${a7.n} El Niños fortes.
      ${U.esc(SOBRA)}. ${U.selo("projecao", SEQ)}</p>
    ${legenda()}${rolar(G.barrasAno(t.porAno, largura(320)), largura(320))}
    <p class="frase">${frase}</p></section>`;
}

// ---------- caixa mês a mês ----------
function caixaHtml(ctx, m, t, nivel) {
  const { util: U } = ctx;
  const { svg } = G.caixa(t, largura(620));
  let iMin = 0;
  t.caixaPlano.forEach((q, i) => { if (q.p50 < t.caixaPlano[iMin].p50) iMin = i; });
  let ultimoAtras = -1;
  t.caixaPlano.forEach((q, i) => { if (q.p50 < t.caixaS0[i].p50 - 0.5) ultimoAtras = i; });
  const volta = ultimoAtras >= 0 && ultimoAtras < C.NMESES - 1 ? C.rotMes(ultimoAtras + 1) : null;
  const fundo = t.caixaPlano[iMin].p50;
  const frase = (fundo < 0 ? `No caminho típico, o ponto mais baixo do plano é <b>${rs(fundo)}</b> em ${C.rotMes(iMin)}. ` : "No caminho típico, o caixa do plano não fica negativo. ") +
    (ultimoAtras === -1 ? "O plano fica à frente do jeito de hoje desde o começo." : volta ? `Ele passa o jeito de hoje em <b>${volta}</b> e não volta mais para trás.` :
      "Ele termina 2029 atrás do jeito de hoje.");
  return `<section class="cartao"><h2>O dinheiro mês a mês</h2>
    <p class="sub">Quanto já saiu e entrou desde hoje, somado. Sai no mês do plantio (${nivel === "semente" ? "semente, maniva" : "semente, máquina e insumos"});
      entra no mês da colheita. Os meses vêm do calendário do passo 3; 2028 e 2029 repetem os meses. A mandioca entra aos poucos, nos meses de colheita.
      ${U.selo("projecao", SEQ)} ${U.selo("suposicao", "custo todo no mês do plantio; receita no meio da colheita; mandioca espalhada nos meses de colheita da agenda")}</p>
    <div class="legenda"><span><i class="chave m-plano"></i>o plano (linha = típico, faixa = 1 em 10 a 9 em 10)</span><span><i class="chave m-s0"></i>o jeito de hoje</span>
      <span><i class="tri saida"></i>sai</span><span><i class="tri entra"></i>entra</span></div>
    <div class="rola"><div class="rola-dentro caixa-wrap" style="min-width:${largura(620)}px">${svg}<div class="dica" hidden></div></div></div>
    <p class="frase">${frase}</p></section>`;
}

function ligarCaixa(el, t) {
  const wrap = el.querySelector(".caixa-wrap");
  if (!wrap) return;
  const svg = wrap.querySelector("svg"), dica = wrap.querySelector(".dica"), cur = svg.querySelector(".cursor");
  const { geo } = G.caixa(t, largura(620));
  const porMes = new Map();
  for (const mk of t.marcas) {
    const k = porMes.get(mk.i) || [];
    k.push(mk);
    porMes.set(mk.i, k);
  }
  const mover = (ev) => {
    const rc = svg.getBoundingClientRect();
    const xv = ((ev.clientX - rc.left) * geo.W) / rc.width;
    const i = Math.max(0, Math.min(geo.n - 1, Math.round(((xv - geo.x0) / (geo.x1 - geo.x0)) * (geo.n - 1))));
    const xi = geo.x(i);
    cur.setAttribute("x1", xi); cur.setAttribute("x2", xi); cur.style.display = "";
    const p = t.caixaPlano[i], s = t.caixaS0[i];
    const mov = (porMes.get(i) || []).map((mk) => `<li>${mk.v < 0 ? "sai" : "entra"} ${rs(Math.abs(mk.v))}: ${mk.rotulo}</li>`).join("");
    dica.innerHTML = `<b>${C.rotMes(i)}</b><div><i class="chave m-plano"></i>plano: típico ${rs(p.p50)} <span>(${faixaRs(p.p10, p.p90)})</span></div>` +
      `<div><i class="chave m-s0"></i>hoje: típico ${rs(s.p50)} <span>(${faixaRs(s.p10, s.p90)})</span></div>${mov ? `<ul>${mov}</ul>` : ""}`;
    dica.hidden = false;
    const px = (xi / geo.W) * rc.width, w = dica.offsetWidth;
    dica.style.left = `${Math.max(0, Math.min(rc.width - w, px + (px > rc.width / 2 ? -w - 12 : 12)))}px`;
  };
  svg.addEventListener("pointermove", mover);
  svg.addEventListener("pointerdown", mover);
  svg.addEventListener("pointerleave", () => { dica.hidden = true; cur.style.display = "none"; });
}

// ---------- 2027: os El Niños fortes ----------
function elNinoHtml(ctx, m, t, nivel, mult, SOBRA) {
  const { r, util: U } = ctx;
  const q = C.ano2027Qualquer(m, nivel, mult);
  const vals = t.elNino.flatMap((e) => [e.plano, e.s0]).concat([q.plano.p50, q.s0.p50]);
  const lo = Math.min(...vals), hi = Math.max(...vals);
  const cards = t.elNino.map((e) => `<div class="en-card"><h4>como ${e.ano}</h4>
      <div class="en-linha"><i class="chave m-plano"></i>plano <b>${rs(e.plano)}</b></div>
      <div class="en-linha"><i class="chave m-s0"></i>hoje <b>${rs(e.s0)}</b></div>${G.mini(e.plano, e.s0, lo, hi)}</div>`).join("") +
    `<div class="en-card qualquer"><h4>um ano qualquer <small>(os ${q.n} anos)</small></h4>
      <div class="en-linha"><i class="chave m-plano"></i>plano <b>${rs(q.plano.p50)}</b> <small>típico</small></div>
      <div class="en-linha"><i class="chave m-s0"></i>hoje <b>${rs(q.s0.p50)}</b> <small>típico</small></div>${G.mini(q.plano.p50, q.s0.p50, lo, hi)}</div>`;
  const n = t.elNino.length, atras = t.elNino.filter((e) => e.plano < e.s0).length;
  const semVenda = semVendaEm(m, 0);
  let iVolta = -1;
  t.caixaPlano.forEach((qq, i) => { if (qq.p50 < t.caixaS0[i].p50 - 0.5) iVolta = i; });
  const volta = iVolta >= 0 && iVolta < C.NMESES - 1 ? C.rotMes(iVolta + 1) : null;
  const depois = t.porAno[1].plano.p50 < t.porAno[1].s0.p50 && t.porAno[2].plano.p50 < t.porAno[2].s0.p50;
  const frase = atras >= Math.ceil(n / 2) && depois
    ? `Em ${vezes(atras, n, "El Niños")} o plano deixa menos que o jeito de hoje em 2027, e no ano típico continua atrás em 2028 e 2029. Aqui o plano não ganha em dinheiro: o ganho dele é a comida da criação e o solo, fora desta conta.`
    : atras >= Math.ceil(n / 2)
    ? `2027 é o ano caro: em ${vezes(atras, n, "El Niños")} o plano deixa menos que o jeito de hoje${semVenda.length ? `, porque ${semVenda.join(" e ")} não ${semVenda.length > 1 ? "vendem" : "vende"} nada no primeiro ano` : ""}.${volta ? ` A volta vem com a colheita: no caminho típico o plano passa o jeito de hoje em ${volta}.` : ""}`
    : `Mesmo em 2027 o plano fica à frente em ${vezes(n - atras, n, "El Niños")}.`;
  const oni = r.este_ano?.oni;
  return `<section class="cartao"><h2>2027 é El Niño muito forte. Se for como…</h2>
    <p class="sub">O Pacífico${oni ? ` hoje (+${U.num(oni, 1)} °C acima do normal)` : ""} está como em ${m.anosEN.slice(0, -1).join(", ")} e ${m.anosEN[m.anosEN.length - 1]}, os ${m.anosEN.length} El Niños fortes da série. O que o plano e o jeito de hoje
      teriam deixado em 2027 aqui, em cada um deles (${U.esc(SOBRA.toLowerCase())}). São só 4 anos: não é previsão.
      ${U.selo("medido", FONTE_PAM + "; anos com ONI ≥ 1,5 em out–dez/nov–jan")} ${U.selo("suposicao", SUP_AREA)}</p>
    <div class="en-grade">${cards}</div>
    <p class="frase">${frase}</p></section>`;
}

// ---------- termômetro ----------
function termoHtml(ctx, m, tS, tD) {
  const { util: U } = ctx;
  const cel = (a, rot) => {
    const p = a.pagaPlano / a.n, unid = a.ano === 2027 ? "El Niños" : "anos";
    return `<div class="medidor" title="plano: ${vezes(a.pagaPlano, a.n, unid)}; hoje: ${vezes(a.pagaS0, a.n, unid)}"><span class="rot">${rot}</span>
      <span class="trilho"><span class="cheio" style="width:${(p * 100).toFixed(1)}%"></span><span class="marca-s0" style="left:${((a.pagaS0 / a.n) * 100).toFixed(1)}%"></span></span>
      <b>${vezes(a.pagaPlano, a.n, unid)}</b> <small>hoje: ${a.pagaS0} de ${a.n}</small></div>`;
  };
  const linhas = [0, 1, 2].map((k) => `<div class="termo-linha"><b class="ano">${2027 + k}</b>${cel(tS.porAno[k], "paga a semente")}${cel(tD.porAno[k], "paga máquina e insumos")}</div>`).join("");
  return `<section class="cartao"><h2>A colheita paga o que foi gasto?</h2>
    <p class="sub">Em quantos dos anos já vistos aqui a colheita do ano cobre o custo daquele ano (em 2027, entre os 4 El Niños fortes).
      A barra é o plano; o risquinho cinza, o jeito de hoje. ${U.selo("projecao", SEQ)} ${U.selo("medido", FONTE_CONAB)}</p>
    <div class="termo">${linhas}</div>
  </section>`;
}

// ---------- replay de 28 anos ----------
function replayHtml(ctx, m, nivel, mult, preco, temMand, SOBRA) {
  const { r, util: U } = ctx;
  const rows = C.replay(m, nivel, mult);
  const acima = rows.filter((x) => x.plano > x.s0).length;
  const pior = rows.reduce((a, b) => (b.plano < a.plano ? b : a));
  const desc = r.plano.faixas.filter((f) => f.parte !== "Bordas" && (f.parte !== "Baixio" || m.b > 0)).map((f) => {
    const its = m.itens[2].filter((i) => i.parte === f.parte);
    const c = f.anos[2].cultura;
    const t = its.some((i) => i.serie === "Mandioca") ? "colhe a mandioca" : its.some((i) => i.custo === "Mandioca") ? "recebe a maniva" :
      f.parte === "Baixio" && c === "Milho" && r.plano.leguminosa ? `milho + ${r.plano.leguminosa.toLowerCase()}` : c.toLowerCase();
    return `${f.parte === "Baixio" ? "baixio" : f.parte}: ${t}`;
  }).join("; ");
  return `<section class="cartao"><h2>Se o plano estivesse no chão desde 1998</h2>
    <p class="sub">O plano já rodando (${U.esc(desc)}) contra o jeito de hoje, no mesmo ano, em cada um dos ${rows.length} anos do IBGE.
      ${U.esc(SOBRA)}. ◆ = El Niño forte. ${U.selo("medido", FONTE_PAM)} ${U.selo("suposicao", SUP_AREA)}</p>
    ${legenda("o plano já rodando")}${rolar(G.replay(rows, m.anosEN, largura(600)), largura(600))}
    <p class="frase">O plano ficou acima em <b>${acima} de ${rows.length} anos</b>${temMand ? ` (com a raiz a R$ ${U.num(preco, 2)}/kg)` : ""}. O pior ano do plano foi ${pior.ano}: ${rs(pior.plano)}
      (hoje, nesse ano: ${rs(pior.s0)}).</p></section>`;
}

// ---------- como a conta é feita ----------
function culturaTabela(fin, U) {
  const linhas = ["Milho", "Feijão", "Mandioca"].map((s) => {
    const c = fin.culturas?.[s];
    if (!c) return `<tr><td>${s}</td><td colspan="6" class="sub">sem série no município (menos de 10 anos com 10 ha ou mais no IBGE)</td></tr>`;
    const v = c.valor_ha || {};
    return `<tr><td>${s}${c.aviso ? `<br><small class="sub">${U.esc(c.aviso)}</small>` : ""}</td><td>${rs(v.min)}</td><td>${rs(v.p50)}</td><td>${rs(v.max)}</td>
      <td>${c.el_nino_forte === null ? "—" : rs(c.el_nino_forte)}</td><td>${rs(c.ultimos?.["2025"])}</td>
      <td>R$ ${U.num(c.preco_kg, 2)}/kg${c.origem_preco !== "município" ? ` (${U.esc(c.origem_preco)})` : ""}<br><small class="sub">custo: semente ${rs(c.custo_ha?.semente)}, desembolso ${rs(c.custo_ha?.desembolso)}</small></td></tr>`;
  }).join("");
  return `<div class="rola"><table class="tab-cult"><thead><tr><th>por ha plantado</th><th>pior ano</th><th>típico</th><th>melhor</th><th>El Niño forte</th><th>2025</th><th>preço e custo</th></tr></thead>
    <tbody>${linhas}</tbody></table></div><p class="pequeno sub">${U.selo("medido", FONTE_PAM)} ${U.selo("medido", FONTE_CONAB)} Valor da colheita por ha (vender ou comer, a preço da região), antes do custo.</p>`;
}

function detalhesHtml(ctx, m, fin, t, calib, nivel, mult, preco) {
  const { util: U } = ctx;
  const ha = (v) => U.ha(Math.round(v * 100) / 100);
  const porAno = [0, 1, 2].map((k) => {
    const its = m.itens[k];
    const txt = [...new Set(its.map((i) => {
      if (i.serie === "Mandioca") return `${i.parte}: ${i.plantada ? "colhe a mandioca já plantada" : "colhe a mandioca"} (receita)`;
      if (i.custo === "Mandioca") return `${i.parte}: maniva (custo)`;
      if (i.uso) return `${i.parte}: ${i.cultura.toLowerCase()} (forragem: só o custo)`;
      if (i.parte === "Baixio") return `Baixio: ${[...new Set(its.filter((j) => j.parte === "Baixio").map((j) => j.cultura.toLowerCase()))].join(" + ")} (metade da área cada)`;
      return `${i.parte}: ${i.cultura.toLowerCase()}`;
    }))].join("; ");
    return `<li><b>${2027 + k}</b> (${k === 0 ? `um dos ${t.nEN} El Niños fortes` : `um dos ${t.nAnos} anos`}): ${U.esc(txt)}</li>`;
  }).join("");
  const tab = t.porAno.map((a) => `<tr><td>${a.ano}</td><td>${rs(a.plano.p10)} · <b>${rs(a.plano.p50)}</b> · ${rs(a.plano.p90)}</td>
    <td>${rs(a.s0.p10)} · <b>${rs(a.s0.p50)}</b> · ${rs(a.s0.p90)}</td><td>${a.planoFrente} de ${a.n}</td></tr>`).join("");
  const avisos = (fin.avisos || []).filter((a) => !/não é lucro|fora da conta/.test(a));
  return `<details class="cartao como"><summary>Como a conta é feita (e o que fica de fora)</summary>
    <h3>Áreas ${U.selo("suposicao", SUP_AREA)}</h3>
    <p>Roçado de ${ha(m.T)}: ${m.b > 0 ? `baixio de ${ha(m.b)}${m.baixioNaoSei ? " (não respondido: ⅓ do roçado, se você tiver baixio)" : ""} e ` : ""}cada parte (A, B e C) com
      ${ha(m.a)}. As bordas (palma + gliricídia) não tiram área. No baixio, metade da receita e do custo é do milho e metade da leguminosa.</p>
    <h3>O que entra em cada ano</h3><ul>${porAno}</ul>
    <p>Mandioca: o custo da maniva entra no ano do plantio; a receita, no ano seguinte (o IBGE anota a colheita no ano em que ela sai do chão).
      Preço da raiz: R$ ${U.num(preco, 2)}/kg (a série do IBGE usa R$ ${U.num(m.precoRefMand ?? 0, 2)}/kg; a mandioca é multiplicada por ${U.num(mult, 2)}).</p>
    <h3>As sequências ${U.selo("projecao", SEQ)}</h3>
    <p>2027 é um dos El Niños fortes (${m.anosEN.join(", ")}); 2028 e 2029, qualquer um dos ${m.anos.length} anos de 1998 a 2025. O mesmo ano vale para todas as culturas e para o jeito de hoje,
      porque a chuva é a mesma para todo o roçado. ${t.nEN} × ${t.nAnos} × ${t.nAnos} = ${t.n.toLocaleString("pt-BR")} sequências, todas contadas.
      Não usamos tendência nem previsão de série: os anos daqui quase não se parecem com o ano anterior.</p>
    <div class="rola"><table><thead><tr><th>ano</th><th>plano: ruim · típico · bom</th><th>hoje: ruim · típico · bom</th><th>plano à frente</th></tr></thead><tbody>${tab}</tbody></table></div>
    <h3>Calibrador honesto</h3>
    <p>Num teste fora da amostra (faixa montada com 1998–2015, conferida em 2016–2025), a faixa de 1 em 10 a 9 em 10 de um ano acertou
      ${Object.entries(calib.por).map(([k, v]) => `${k.toLowerCase()} ${U.emDez(v)}`).join(", ")} anos (deveria ser 8 em 10). Por isso a faixa daqui é larga e o futuro pode sair dela.</p>
    <h3>Por cultura</h3>${culturaTabela(fin, U)}
    <h3>Fora da conta</h3>
    <ul><li>Forragem: sorgo forrageiro, palma e gliricídia são comida da criação (valor de uso), sem preço no IBGE. Só entra o custo da semente do sorgo
      (${rs(fin.custo_sorgo_forrageiro_ha?.[nivel])}/ha, ${U.selo("suposicao", fin.custo_sorgo_forrageiro_ha?.origem || "lavoura anual manual")}).</li>
      <li>Garantia-Safra, mão de obra da família, frete e casa de farinha.</li>
      <li>O ganho de rendimento da rotação contra o consórcio de hoje (não foi medido) e o preço futuro (fica o de 2016–2025, em R$ de 2025).</li></ul>
    ${avisos.length ? `<h3>Avisos dos dados</h3><ul>${avisos.map((a) => `<li>${U.esc(a)}</li>`).join("")}</ul>` : ""}
  </details>`;
}

// ---------- sem série ----------
function semConta(m, fin, U) {
  const falta = !fin ? ["Não há dados do IBGE (PAM 1998–2025) para este município nesta versão do site."]
    : m.falta.map((s) => (["Milho", "Feijão", "Mandioca"].includes(s)
      ? `${s}: o município tem menos de 10 anos com 10 ha ou mais plantados no IBGE (1998–2025).` : `Falta ${s}.`));
  return `<section class="cartao"><h2>O que falta para fazer a conta aqui</h2>
    <ul>${falta.map((f) => `<li>${U.esc(f)}</li>`).join("")}</ul>
    <p>Sem essa série, não dá para refazer o plano e o jeito de hoje no mesmo ano, e não inventamos número.
      ${fin ? "Abaixo, só o que o IBGE tem daqui, por ha plantado." : ""}</p></section>
    ${fin ? `<section class="cartao"><h2>O que existe aqui</h2>${culturaTabela(fin, U)}</section>` : ""}`;
}
