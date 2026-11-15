// QUADRA, módulo extra "Hoje → melhor → ideal" (pedido do José, 14/11/2026): a pessoa diz como planta hoje e vê
// (1) o jeito dela refeito nos anos que já aconteceram no município, (2) o mesmo jeito com ajustes pequenos e
// (3) o plano completo do QUADRA. Dois modos: render(el, ctx, { modo: "pergunta" }) e render(el, ctx, { modo: "comparacao" }).
// A conta é a do passo 4 (js/passos/dinheiro/calculo.js, importado sem mudar): R$ de 2025, 2027 entre os 4 El Niños fortes,
// 2028 e 2029 entre os 28 anos do IBGE, o mesmo ano para todas as culturas (3.136 combinações). Só milho, feijão e mandioca têm R$.
// Contrato do ctx e regras de visual: js/passos/LEIA-ME.md. Onde encaixar e o formato de ctx.resp.hoje: integracao/hoje_ideal.md.
import * as C from "../passos/dinheiro/calculo.js";

// ------------------------------------------------------------------ o jeito de hoje em texto (ctx.resp.hoje)
// "milho:50,feijao:50|cons=1|1chuva=1|queima=1|sem=1" — culturas:% (soma 100) | chaves 1/0; chave ausente = padrão.
const CULT = {
  milho: { nome: "Milho", serie: "Milho", icone: "milho", t: "cereal" },
  feijao: { nome: "Feijão", serie: "Feijão", icone: "feijao", t: "leguminosa" },
  mandioca: { nome: "Mandioca", serie: "Mandioca", icone: "mandioca", t: "tampao" },
  sorgo: { nome: "Sorgo", icone: "milho", t: "forragem", semRs: true },
  palma: { nome: "Palma", icone: "palma", t: "perene", semRs: true },
  outra: { nome: "Outra", icone: "broto", t: "pousio", semRs: true },
};
const CHAVES = { cons: "cons", mbx: "mbx", "1chuva": "chuva1", queima: "queima", sem: "sem" };

/** Ajusta as porcentagens para somar 100 (inteiros; a sobra vai para a maior). */
function normal(c) {
  const ks = Object.keys(c).filter((k) => c[k] > 0), s = ks.reduce((a, k) => a + c[k], 0);
  if (!ks.length || !(s > 0)) return { milho: 50, feijao: 50 };
  const o = Object.fromEntries(ks.map((k) => [k, Math.round((c[k] / s) * 100)]));
  const maior = ks.reduce((a, k) => (o[k] > o[a] ? k : a), ks[0]);
  o[maior] += 100 - ks.reduce((a, k) => a + o[k], 0);
  return o;
}
const igual = (ks) => Object.fromEntries(ks.map((k, i) => [k, Math.floor(100 / ks.length) + (i < 100 % ks.length ? 1 : 0)]));

/** Lê ctx.resp.hoje. Sem resposta: milho + feijão juntos, na 1ª chuva (o mais comum no semiárido); semente pelo Censo 2017. */
export function lerHoje(txt, padroes) {
  const pm = padroes?.pct_semente_milho;
  const h = { cult: { milho: 50, feijao: 50 }, cons: 1, mbx: null, chuva1: 1, queima: null, sem: pm == null ? null : pm >= 50 ? 1 : 0, informado: false };
  if (!txt) return h;
  const [cs = "", ...kv] = String(txt).split("|");
  const cult = {};
  for (const p of cs.split(",")) { const [k, v] = p.split(":"); if (CULT[k] && +v > 0) cult[k] = +v; }
  if (Object.keys(cult).length) h.cult = normal(cult);
  for (const p of kv) { const [k, v] = p.split("="); if (CHAVES[k]) h[CHAVES[k]] = v === "1" ? 1 : v === "0" ? 0 : null; }
  h.informado = true;
  return h;
}

/** Escreve o texto compacto (a ordem das culturas segue CULT; só grava as chaves respondidas). */
export function escreverHoje(h) {
  const cs = Object.keys(CULT).filter((k) => h.cult[k] > 0).map((k) => `${k}:${Math.round(h.cult[k])}`).join(",");
  const kv = Object.entries(CHAVES).filter(([, c]) => h[c] === 0 || h[c] === 1).map(([k, c]) => `${k}=${h[c]}`);
  return [cs, ...kv].join("|");
}

// ------------------------------------------------------------------ a conta (sem DOM; roda no node)
/** Áreas de hoje (ha) e onde fica o milho: tudo junto → espalhado; em pedaços → proporcional; "milho no baixio" → baixio primeiro. */
export function areasHoje(h, ef) {
  const T = ef.ha, b = ef.tem_baixio === false ? 0 : Math.min(Math.max(ef.baixio_ha || 0, 0), T);
  const ha = Object.fromEntries(Object.entries(h.cult).map(([k, p]) => [k, (p / 100) * T]));
  const mi = ha.milho || 0;
  const noBaixio = h.cons === 0 && h.mbx === 1 ? Math.min(mi, b) : T > 0 ? mi * (b / T) : 0;
  return { T, b, ha, milhoAlta: Math.max(0, mi - noBaixio) };
}

/** Áreas de um ano do cenário. A mandioca fica 2 estações no chão (convenção do passo 4): metade colhe e metade planta por ano.
 *  A reserva nova (P) começa em 2027 com metade plantada, e só colhe em 2028, salvo se a maniva já estiver no chão. */
function anoCen(sc, k, plantada) {
  const f = k === 0 && !plantada ? 0.5 : 1, ha = sc.ha, fo = sc.fonte || {}, M = ha.mandioca || 0, P = sc.P || 0;
  return { Milho: (ha.milho || 0) - (fo.milho || 0) * f, "Feijão": (ha.feijao || 0) - (fo.feijao || 0) * f, sorgo: ha.sorgo || 0,
    mandPlanta: (M + P) / 2, mandColhe: M / 2 + (k === 0 && !plantada ? 0 : P / 2) };
}

/** Meses de plantio e de colheita do milho e do feijão que o montar() do passo 4 já tirou da agenda (S0), por ano. */
function mesesS0(m) {
  return (m?.s0 || []).map((its) => Object.fromEntries(["Milho", "Feijão"].map((s) => {
    const p = its.find((i) => i.cultura === s && i.custo), c = its.find((i) => i.cultura === s && i.serie);
    return [s, p && c ? { pl: p.mes, meses: c.meses } : null];
  })));
}

/** Lançamentos no formato de calculo.js (custo no plantio; receita = série do ano × área). Os meses só servem ao caixa. */
function itensCen(anosPlano, sc, plantada, meses = []) {
  return anosPlano.map((est, k) => {
    const c = anoCen(sc, k, plantada), out = [];
    for (const s of ["Milho", "Feijão"]) if (c[s] > 1e-9) {
      const ms = meses[k]?.[s], pl = ms?.pl ?? C.idxMes(est, 3), mc = ms?.meses ?? [[C.idxMes(est, 6), 1]];
      out.push({ parte: "Hoje", cultura: s, custo: s, area: c[s], mes: pl, rotulo: `semente: ${s.toLowerCase()}`, tipo: "plantio" });
      out.push({ parte: "Hoje", cultura: s, serie: s, fator: c[s], meses: mc, rotulo: `colheita: ${s.toLowerCase()}`, tipo: "colheita" });
    }
    const pl = C.idxMes(est, 3);
    if (c.sorgo > 1e-9) out.push({ parte: "Hoje", cultura: "Sorgo", custo: "Sorgo forrageiro", area: c.sorgo, mes: pl, rotulo: "semente: sorgo (forragem, sem R$)", tipo: "plantio", uso: true });
    if (c.mandPlanta > 1e-9) out.push({ parte: "Hoje", cultura: "Mandioca", custo: "Mandioca", area: c.mandPlanta, mes: pl, rotulo: "maniva", tipo: "plantio" });
    if (c.mandColhe > 1e-9) { // colheita de fev a set (o mesmo padrão do passo 4 sem agenda)
      const i0 = C.idxMes(est, 2), i1 = C.idxMes(est, 9), n = i1 - i0 + 1;
      out.push({ parte: "Hoje", cultura: "Mandioca", serie: "Mandioca", fator: c.mandColhe, meses: Array.from({ length: n }, (_, j) => [i0 + j, 1 / n]),
        rotulo: "colheita da mandioca", tipo: "colheita" });
    }
    return out;
  });
}

const seriesDe = (its) => new Set(its.flat().flatMap((i) => [i.serie, i.custo]).filter((s) => s === "Milho" || s === "Feijão" || s === "Mandioca"));

/** Ajuste "milho só no baixio": o milho da terra alta vira feijão (a conta só vê a troca de cultura). */
function soBaixio(sc, A) {
  if (!(A.b > 0) || !(sc.milhoAlta > 0.02)) return null;
  return { ...sc, ha: { ...sc.ha, milho: sc.ha.milho - sc.milhoAlta, feijao: (sc.ha.feijao || 0) + sc.milhoAlta }, milhoAlta: 0 };
}
/** Ajuste "um pedaço de mandioca de reserva": até ⅓ da terra alta (o tamanho de uma parte do plano), tirado do milho da terra
 *  alta, depois do feijão e da "outra". */
function reserva(sc, A) {
  const alvo = (A.T - A.b) / 3 - (sc.ha.mandioca || 0);
  if (alvo < 0.05) return null;
  const fonte = {};
  let falta = alvo;
  for (const [k, lim] of [["milho", sc.milhoAlta], ["feijao", sc.ha.feijao || 0], ["outra", sc.ha.outra || 0]]) {
    const t = Math.min(falta, lim);
    if (t > 1e-9) { fonte[k] = t; falta -= t; }
  }
  const P = alvo - falta;
  if (P < 0.05) return null;
  return { ...sc, P, fonte, milhoAlta: sc.milhoAlta - (fonte.milho || 0) };
}

/** Parte da colheita (R$, sem custo) em cada um dos 28 anos, no 3º ano (já rodando). Quebra = ano abaixo da metade do típico
 *  do próprio cenário (a mesma régua do IBGE para uma cultura: rendimento < 0,5 × mediana). */
function quebra(base, itK, mult) {
  const rec = base.anos.map((y) => itK.reduce((s, i) => s + (i.serie ? base.R[i.serie].get(y) * i.fator * (i.serie === "Mandioca" ? mult : 1) : 0), 0));
  const med = C.quantil([...rec].sort((a, b) => a - b), 0.5);
  if (!(med > 0)) return null;
  const en = base.anosEN.map((y) => rec[base.anos.indexOf(y)]);
  return { p: rec.filter((v) => v < 0.5 * med).length / rec.length, k: rec.filter((v) => v < 0.5 * med).length, n: rec.length,
    enRel: C.quantil([...en].sort((a, b) => a - b), 0.5) / med, enQ: en.filter((v) => v < 0.5 * med).length, nEN: en.length };
}

/** Janela boa de plantio do ZARC (ctx.r.agenda.culturas): "11/03 a 20/03". */
function janela(r, nome) {
  const c = (r.agenda?.culturas || []).find((x) => x.cultura === nome);
  const d = [...String(c?.plantar || "").matchAll(/(\d{2})\/(\d{2})\/\d{4}/g)];
  return d.length >= 2 ? `${d[0][1]}/${d[0][2]} a ${d[1][1]}/${d[1][2]}` : null;
}

/**
 * Tudo o que a comparação mostra: hoje, melhor (com os ajustes) e ideal (o plano do motor), cada um com a faixa de 3 anos
 * (P10/P50/P90), a quebra nos 28 anos e a chance de ficar à frente de hoje; mais os alertas de hoje e os ajustes.
 */
export function comparar(r, ef, h) {
  const fin = r.financeiro, A = areasHoje(h, ef), anosPlano = r.plano?.anos || [2027, 2028, 2029];
  const plantada = ef.maniva === "plantada";
  const res = { A, h, fin: !!fin, falta: [], agro: [], hoje: null, melhor: null, ideal: null, ajustes: [], alertas: [], semRs: [] };
  res.semRs = Object.keys(h.cult).filter((k) => CULT[k].semRs).map((k) => CULT[k].nome.toLowerCase());
  const H = fin?.historico_R_ha;
  const temSerie = (s) => !!(fin?.culturas?.[s] && H?.[s] && H[s].filter(Number.isFinite).length >= 10);
  const cult = fin?.culturas || {};

  // preço da raiz e custo: os mesmos do passo 4
  const pr = fin?.precos_raiz || {};
  let raiz = ef.raiz, preco = pr[raiz];
  if (!(preco > 0)) { raiz = "municipio"; preco = pr.municipio ?? cult.Mandioca?.preco_kg; }
  const ref = cult.Mandioca?.preco_kg;
  Object.assign(res, { raiz, preco, mult: ref && preco ? preco / ref : 1, nivel: ef.custo === "desembolso" ? "desembolso" : "semente" });

  // cenários
  const cenHoje = { ha: { ...A.ha }, milhoAlta: A.milhoAlta, P: 0, fonte: {} };
  const m = fin ? C.montar(r, ef) : null;
  const meses = mesesS0(m);
  const itensCenM = (sc) => itensCen(anosPlano, sc, plantada, meses);
  const itH = itensCenM(cenHoje);
  const itI = m ? m.itens : null;
  // a reserva de mandioca só onde o motor aceita a mandioca (cardápio fora de "fora": com ZARC ou só aptidão)
  const mandOk = (r.cardapio || []).some((x) => x.cultura === "Mandioca" && x.situacao !== "fora");
  const opA = soBaixio(cenHoje, A), opB = mandOk ? reserva(cenHoje, A) : null;
  let cenM = cenHoje;
  const ops = [];
  if (opA) { ops.push({ id: "baixio", sc: opA }); }
  if (opB) { ops.push({ id: "reserva", sc: opB }); }

  // alertas de hoje que não dependem do R$
  const inicio = r.este_ano?.inicio?.mediana;
  if (h.queima === 1) res.alertas.push({ id: "queima", icone: "fogo", txt: "Queimar tira a palhada: a terra seca mais cedo." });
  if (h.chuva1 === 1 && inicio) res.alertas.push({ id: "chuva", icone: "chuva", txt: `Na 1ª chuva (por volta de ${inicio}), o veranico pega o broto.` });
  res.alertas.push(h.cons === 0 && h.mbx !== 1 ? { id: "arranjo", icone: "faixas", txt: "Em blocos, a praga anda o bloco todo." }
    : h.cons === 0 ? { id: "arranjo", icone: "faixas", txt: "Cada pedaço num lugar só: a praga volta todo ano." }
      : { id: "arranjo", icone: "faixas", txt: "Tudo junto: a lagarta anda de pé em pé." });

  if (!fin) { res.falta.push("sem a série do IBGE (PAM) daqui"); return fechar(res, r, ef, h, A, null); }
  res.agro = m.agro || [];

  // séries disponíveis e cenários que dá para contar
  const precisa = { hoje: seriesDe(itH), ideal: seriesDe(itI) };
  const okH = precisa.hoje.size > 0 && [...precisa.hoje].every(temSerie);
  const okI = itI.flat().length > 0 && [...precisa.ideal].every(temSerie);
  if (!okH) res.falta.push(precisa.hoje.size ? `${[...precisa.hoje].filter((s) => !temSerie(s)).join(" e ").toLowerCase()}: menos de 10 anos no IBGE daqui`
    : "o que você planta hoje não tem preço no IBGE (só milho, feijão e mandioca têm)");
  if (!okI) res.falta.push(`o plano usa ${[...precisa.ideal].filter((s) => !temSerie(s)).join(" e ").toLowerCase()}, sem série aqui`);
  const okOps = ops.filter((o) => [...seriesDe(itensCenM(o.sc))].every(temSerie));
  const series = new Set([...(okH ? precisa.hoje : []), ...(okI ? precisa.ideal : []), ...okOps.flatMap((o) => [...seriesDe(itensCenM(o.sc))])]);
  if (!series.size) return fechar(res, r, ef, h, A, null);

  // a base da conta: as séries do IBGE (R$/ha de 2025), só os anos em que todas as séries usadas têm valor
  const R = Object.fromEntries([...series].map((s) => [s, new Map(H.anos.map((y, i) => [y, H[s][i]]))]));
  const anos = H.anos.filter((y) => [...series].every((s) => Number.isFinite(R[s].get(y))));
  const anosEN = (fin.anos_el_nino_forte || [1998, 2010, 2016, 2024]).filter((y) => anos.includes(y));
  if (anos.length < 10 || !anosEN.length) { res.falta.push("anos suficientes com as culturas no mesmo ano"); return fechar(res, r, ef, h, A, null); }
  const base = { ...m, R, anos, anosEN };
  const vazio = [[], [], []];
  const tot = (it, s0) => C.totais({ ...base, itens: it, s0 }, res.nivel, res.mult);
  res.base = { anos: anos.length, anosEN, n: anosEN.length * anos.length * anos.length, ano0: anos[0], ano1: anos[anos.length - 1] };

  if (okH) {
    res.hoje = { f: tot(itH, vazio).plano, q: quebra(base, itH[2], res.mult), it: itH };
  }
  if (okI) {
    const t = tot(itI, okH ? itH : vazio);
    res.ideal = { f: t.plano, q: quebra(base, itI[2], res.mult), aFrente: okH ? t.aFrente : null, ganho: okH ? t.ganho : null, it: itI };
  }
  // os ajustes com conta, cada um sozinho sobre o jeito de hoje; só entram os que ganham no típico e ficam à frente
  // em 6 de 10 combinações ou mais (abaixo disso é cara ou coroa)
  if (okH) {
    for (const o of okOps) {
      const it = itensCenM(o.sc), t = tot(it, itH);
      if (t.ganho.p50 > 0 && t.aFrente >= 0.6) res.ajustes.push({ id: o.id, conta: true, ganho: t.ganho, aFrente: t.aFrente, sc: o.sc });
    }
    res.ajustes.sort((a, b) => b.ganho.p50 - a.ganho.p50);
    // o melhor: os ajustes com conta juntos (baixio antes da reserva: a reserva sai do feijão quando o milho já desceu)
    const ids = new Set(res.ajustes.map((a) => a.id));
    if (ids.has("baixio")) cenM = soBaixio(cenM, A) || cenM;
    if (ids.has("reserva")) cenM = reserva(cenM, A) || cenM;
    const itM = itensCenM(cenM), t = tot(itM, itH);
    res.melhor = { f: t.plano, q: quebra(base, itM[2], res.mult), aFrente: ids.size ? t.aFrente : null, ganho: t.ganho, sc: cenM, it: itM, igual: !ids.size };
  }

  // alertas medidos (no começo da lista: pesam mais)
  const med = [];
  const qH = res.hoje?.q;
  if (qH && qH.enRel < 0.6 && !(A.ha.mandioca > 0.2 * A.T)) {
    med.push({ id: "reserva", icone: "onda", txt: `Sem reserva: no El Niño forte, a colheita daqui cai ${fracFala(qH.enRel)}.`, medido: true });
  }
  const kMi = Math.round((cult.Milho?.quebra_pct ?? 0) / 10);
  if (A.milhoAlta > 0.02 && kMi >= 2) {
    const k = kMi;
    med.push({ id: "milho", icone: "milho", txt: `${A.b > 0 ? "Milho fora do baixio" : "Milho em terra alta"}: aqui ele quebra em ${k} de 10 anos.`, medido: true });
  }
  res.alertas = [...med, ...res.alertas];
  return fechar(res, r, ef, h, A, cenM);
}

/**
 * Para o passo 4: devolve o m de calculo.montar() com o "jeito de hoje" (m.s0) trocado pelo que a pessoa informou em
 * ctx.resp.hoje, com os mesmos meses da agenda. Uso: const m = comHoje(C.montar(r, ef), r, ef, ctx.resp.hoje).
 * Mantém o S0 fixo (milho + feijão) e marca m.hojeFixo com o motivo quando o informado não tem conta aqui.
 */
export function comHoje(m, r, ef, txt) {
  if (!m?.ok || !txt) return m;
  const h = lerHoje(txt, r.padroes), A = areasHoje(h, ef), fin = r.financeiro, H = fin.historico_R_ha;
  const s0 = itensCen(r.plano?.anos || [2027, 2028, 2029], { ha: { ...A.ha }, milhoAlta: A.milhoAlta, P: 0, fonte: {} }, ef.maniva === "plantada", mesesS0(m));
  const precisa = [...seriesDe(s0)];
  if (!precisa.length) return { ...m, hojeFixo: "o que você planta hoje não tem preço no IBGE" };
  const falta = precisa.filter((s) => !(fin.culturas?.[s] && H?.[s]));
  if (falta.length) return { ...m, hojeFixo: `${falta.join(" e ").toLowerCase()}: sem série aqui` };
  const R = { ...m.R }, KG = { ...m.KG }, K = fin.historico_kg_ha || {};
  for (const s of precisa) if (!R[s]) {
    R[s] = new Map(H.anos.map((y, i) => [y, H[s][i]]));
    KG[s] = new Map((K.anos || []).map((y, i) => [y, K[s]?.[i] ?? null]));
  }
  const usadas = [...new Set([...m.usadas, ...precisa])];
  const anos = m.anos.filter((y) => usadas.every((s) => Number.isFinite(R[s].get(y))));
  const anosEN = m.anosEN.filter((y) => anos.includes(y));
  if (anos.length < 10 || !anosEN.length) return { ...m, hojeFixo: "anos suficientes com as culturas de hoje no mesmo ano" };
  return { ...m, s0, R, KG, usadas, anos, anosEN, origens: { ...m.origens, ...Object.fromEntries(precisa.map((s) => [s, H["origem_" + s] || []])) },
    hoje: h, hojeDesc: descHoje(h) };
}

/** "cai à metade", "cai a um terço"... (frequência e fração em palavras, sem porcentagem na frente). */
function fracFala(x) {
  if (x < 0.15) return "a quase nada";
  if (x < 0.42) return "a um terço";
  if (x < 0.6) return "à metade";
  return "um pouco";
}

/** Completa os ajustes sem R$ (na ordem do que pesa mais), marca o que depende do olho e corta os alertas em 3. */
function fechar(res, r, ef, h, A, cenM) {
  const leg = r.plano?.leguminosa || "Feijão-caupi";
  const temFeijao = (h.cult.feijao || 0) > 0, temMilho = (h.cult.milho || 0) > 0;
  const semConta = [];
  // metade guardada só quando o motor manda (agenda ou interruptor do plano); senão, escalonar em ano de alerta
  const txtAg = [...(r.agenda?.linhas || []), ...(r.agenda?.culturas || [])].map((x) => x.plantar || "").join(" ");
  const inter = String(r.plano?.interruptor || "");
  const ate = (txtAg.match(/guarde a outra até ([^\s;,)]+)/) || inter.match(/guardada até ([^\s;,)]+?)\.?(?:\s|$)/))?.[1];
  if (ate || /metade/.test(inter)) semConta.push({ id: "metade", icone: "semente", txt: `El Niño: plante metade e guarde metade${ate ? ` até ${ate}` : ""}.` });
  else if (r.este_ano?.nivel_alerta === "alerta" || /escalon/.test(inter)) semConta.push({ id: "metade", icone: "semente", txt: "Escalone: plante em 2 ou 3 vezes, não tudo no mesmo dia." });
  if (h.chuva1 !== 0) {
    const jf = temFeijao ? janela(r, leg) : null, jm = temMilho ? janela(r, "Milho") : null;
    const partes = [jf && `feijão ${jf}`, jm && `milho ${jm}`].filter(Boolean);
    if (partes.length) semConta.push({ id: "janela", icone: "calendario", txt: `Espere a janela boa: ${partes.join(", ")}.`, medido: true });
  }
  semConta.push({ id: "faixas", icone: "faixas", txt: "Plante em faixas, não em blocos: a praga anda menos.", passo: 3 });
  if (h.queima === 1) semConta.push({ id: "fogo", icone: "broto", txt: "Sem fogo: a palhada no chão guarda a umidade." });
  if (h.sem === 0) semConta.push({ id: "semente", icone: "semente", txt: "Garanta a semente até dezembro: o plantio não espera." });
  if (!res.hoje && A.b > 0 && A.milhoAlta > 0.02) {
    semConta.unshift({ id: "baixio", icone: "milho", txt: "Milho só no baixio; em cima, feijão." }); // sem série: o ajuste fica sem R$
  }
  const comConta = res.ajustes.map((a) => ({ ...a, ...TXT_AJ[a.id](a, ef) }));
  res.lista = [...comConta, ...semConta];
  const olhoId = ["metade", "janela", "baixio", "faixas"].find((id) => res.lista.some((a) => a.id === id));
  for (const a of res.lista) a.olho = a.id === olhoId;
  res.olho = res.lista.find((a) => a.olho) || null;
  res.alertas = res.alertas.slice(0, 3);
  res.cenM = cenM;
  return res;
}

const haTxt = (v) => `${(Math.round(v * 10) / 10).toLocaleString("pt-BR")} ha`;
const TXT_AJ = {
  baixio: () => ({ icone: "milho", txt: "Milho só no baixio; em cima, feijão." }),
  reserva: (a, ef) => ({ icone: "mandioca", txt: `Um pedaço de mandioca (${haTxt(a.sc.P)}) de reserva.`, maniva: ef.maniva === "nao" }),
};

// ------------------------------------------------------------------ desenho
const OLHO = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="2.8"/></svg>';
const n0 = (v, c = 0) => Number(v).toLocaleString("pt-BR", { maximumFractionDigits: c, minimumFractionDigits: c });
/** R$ legível (igual ao passo 4): "R$ 11,5 mil" a partir de 10 mil; "R$ 1.090" de mil a 10 mil; "−R$ 101". */
function rs(v) {
  if (v === null || v === undefined || !Number.isFinite(v)) return "—";
  const s = v < 0 ? "−" : "", a = Math.abs(v);
  if (a >= 10000) return `${s}R$ ${n0(a / 1000, 1)} mil`;
  return `${s}R$ ${n0(a >= 1000 ? Math.round(a / 10) * 10 : Math.round(a))}`;
}
const mais = (v) => (v >= 0 ? "+" : "") + rs(v);
const de100 = (p) => { const n = Math.round(p * 100); return n === 100 && p < 1 ? "mais de 99" : n === 0 && p > 0 ? "menos de 1" : String(n); };

let tela = 0; // pergunta atual (0..2; 3 = pronto)
let rascunho = null, visto = ""; // o jeito em edição (só a 1ª tela edita sem gravar a cada toque) e o último texto lido
const zerados = new WeakSet();

export default {
  id: "hoje-ideal",
  titulo: "Hoje, melhor e ideal",
  async render(el, ctx, opcoes = {}) {
    const modo = opcoes.modo === "comparacao" ? "comparacao" : "pergunta";
    if (modo === "comparacao") return desenharComparacao(el, ctx, opcoes);
    if (ctx.entrou && !zerados.has(ctx)) { zerados.add(ctx); tela = Number.isInteger(opcoes.tela) ? opcoes.tela : 0; rascunho = null; }
    return desenharPergunta(el, ctx, opcoes, this);
  },
};

// ------------------------------------------------------------------ modo "pergunta": até 3 toques
const miniRocado = (tipo) => {
  const M = "hi-mr-milho", F = "hi-mr-feijao";
  const corpo = {
    junto: Array.from({ length: 7 }, (_, i) => `<rect x="4" y="${5 + i * 7.4}" width="52" height="4.6" rx="1.5" class="${i % 2 ? F : M}"/>`).join(""),
    pedacos: `<rect x="4" y="4" width="25" height="52" rx="3" class="${M}"/><rect x="31" y="4" width="25" height="52" rx="3" class="${F}"/>`,
    baixio: `<rect x="4" y="4" width="52" height="33" rx="3" class="${F}"/><rect x="4" y="39" width="52" height="17" rx="3" class="${M}"/>`,
    nao: `<text x="30" y="38" text-anchor="middle" class="hi-mr-q">?</text>`,
  }[tipo];
  return `<svg class="hi-mini" viewBox="0 0 60 60" aria-hidden="true"><rect x="1.5" y="1.5" width="57" height="57" rx="6" class="hi-mr-borda${tipo === "nao" ? " incerto" : ""}"/>${corpo}</svg>`;
};

function opcoesCultura(r) {
  const card = r.cardapio || [];
  const serve = (re) => card.some((c) => re.test(c.cultura) && c.situacao !== "fora");
  return ["milho", "feijao", "mandioca", ...(serve(/^Sorgo/) ? ["sorgo"] : []), ...(serve(/^Palma/) ? ["palma"] : []), "outra"];
}

function topo(U, n, titulo, eco) {
  return `<div class="hi-quiz-topo"><p class="kicker">Seu jeito de hoje · ${n + 1} de 3</p>
    <div class="hi-barra">${[0, 1, 2].map((i) => `<i class="${i < n ? "feito" : i === n ? "atual" : ""}"></i>`).join("")}</div></div>
    <h1 class="hi-quiz-titulo">${U.esc(titulo)}<span class="eco">${U.esc(eco)}</span></h1>`;
}

function telaCulturas(ctx, U, h) {
  const ops = opcoesCultura(ctx.r), ks = Object.keys(h.cult);
  const botoes = ops.map((k) => `<button type="button" class="hi-opcao ${ks.includes(k) ? "marcada" : ""}" data-c="${k}" aria-pressed="${ks.includes(k)}">
    ${U.ic(CULT[k].icone, "gg")}<b>${CULT[k].nome}</b>${CULT[k].semRs ? `<span>sem preço aqui</span>` : ""}</button>`).join("");
  const barra = `<div class="hi-divisao" role="img" aria-label="divisão do roçado">${ks.map((k) =>
    `<i class="${"t-" + CULT[k].t}" style="flex:${h.cult[k]}"><span>${h.cult[k] >= 18 ? `${CULT[k].nome} ` : ""}${h.cult[k]}%</span></i>`).join("")}</div>`;
  const linhas = ks.length > 1 ? `<div class="hi-quanto">${ks.map((k) => `<div class="hi-q-linha">${U.ic(CULT[k].icone)}<b>${CULT[k].nome}</b>
      <button type="button" class="hi-mm" data-m="${k}" data-d="-10" aria-label="menos ${CULT[k].nome}">−</button>
      <span class="hi-q-val">${h.cult[k]}%</span>
      <button type="button" class="hi-mm" data-m="${k}" data-d="10" aria-label="mais ${CULT[k].nome}">+</button></div>`).join("")}
      <button type="button" class="chip hi-igual" data-igual="1">dividir igual</button></div>` : "";
  return `${topo(U, 0, "Como você planta hoje?", "Toque no que vai no roçado.")}
    <div class="hi-opcoes">${botoes}</div>
    <div class="hi-quanto-bloco"><p class="hi-rot">${U.ic("faixas")}<span>Quanto de cada, no seu roçado de ${U.ha(ctx.ef.ha)}</span></p>${barra}${linhas}</div>`;
}

function telaArranjo(ctx, U, h) {
  const temB = ctx.ef.tem_baixio !== false && (h.cult.milho || 0) > 0;
  const atual = h.cons === 1 ? "junto" : h.cons === 0 && h.mbx === 1 ? "baixio" : h.cons === 0 ? "pedacos" : "";
  const ops = [["junto", "Tudo junto", "na mesma linha ou cova"], ["pedacos", "Em pedaços", "cada um no seu canto"],
    ...(temB ? [["baixio", "Milho no baixio", "o resto em cima"]] : []), ["nao", "Não sei", "fica o mais comum"]];
  return `${topo(U, 1, "Como fica no roçado?", "Junto ou separado.")}
    <div class="hi-opcoes n${ops.length}">${ops.map(([v, t, s]) => `<button type="button" class="hi-opcao ${atual === v ? "marcada" : ""}" data-arr="${v}">
      ${miniRocado(v)}<b>${t}</b><span>${s}</span></button>`).join("")}</div>`;
}

const PARES = [
  ["chuva1", "Quando planta", [[1, "chuva", "Na 1ª chuva"], [0, "relogio", "Espero a chuva firmar"]]],
  ["queima", "Antes de plantar", [[1, "fogo", "Queimo o roçado"], [0, "broto", "Não queimo"]]],
  ["sem", "A semente", [[1, "semente", "Guardo a minha"], [0, "dinheiro", "Compro ou recebo"]]],
];
function telaManejo(ctx, U, h) {
  return `${topo(U, 2, "E na hora de plantar?", "Só o que muda a conta.")}
    <div class="hi-pares">${PARES.map(([k, rot, ops]) => `<div class="hi-par"><p class="hi-rot">${U.esc(rot)}</p><div class="hi-par-ops">${ops.map(([v, i, t]) =>
      `<button type="button" class="hi-opcao baixa ${h[k] === v ? "marcada" : ""}" data-k="${k}" data-v="${v}" aria-pressed="${h[k] === v}">${U.ic(i, "g")}<b>${t}</b></button>`).join("")}</div></div>`).join("")}</div>`;
}

/** Resumo curto do jeito de hoje (fichas que voltam à pergunta). */
export function resumoHoje(h, U) {
  const cs = Object.keys(h.cult).map((k) => `${CULT[k].nome} ${h.cult[k]}%`).join(" · ");
  const arr = h.cons === 1 ? "Tudo junto" : h.cons === 0 && h.mbx === 1 ? "Milho no baixio" : h.cons === 0 ? "Em pedaços" : "Arranjo: não sei";
  return [["faixas", cs, 0], ["enxada", arr, 1], ["chuva", h.chuva1 === 1 ? "Na 1ª chuva" : h.chuva1 === 0 ? "Espera a chuva firmar" : "Plantio: não sei", 2],
    ["fogo", h.queima === 1 ? "Queima" : h.queima === 0 ? "Não queima" : "Fogo: não sei", 2],
    ["semente", h.sem === 1 ? "Guarda semente" : h.sem === 0 ? "Compra semente" : "Semente: não sei", 2]];
}

function desenharPergunta(el, ctx, opcoes, mod) {
  const U = ctx.util, txt = ctx.resp?.hoje || "";
  if (!rascunho || txt !== visto) { rascunho = lerHoje(txt, ctx.r.padroes); visto = txt; }
  const h = rascunho;
  const gravar = () => { const s = escreverHoje(h); visto = s; ctx.set({ hoje: s }); };
  const redesenhar = () => mod.render(el, ctx, opcoes);
  const ir = (n) => { tela = n; redesenhar(); if (n >= 3) opcoes.aoTerminar?.(h); };

  if (tela >= 3) {
    el.innerHTML = `<div class="hoje-ideal hi-pergunta hi-pronto">
      <div class="titulo-passo"><p class="kicker">Seu jeito de hoje</p><h1>Anotado.<span class="eco">Agora a gente compara.</span></h1></div>
      <div class="hi-fichas">${resumoHoje(h, U).map(([i, t, n]) => `<button type="button" class="hi-ficha" data-q="${n}">${U.ic(i)}<span>${U.esc(t)}</span><em>mudar</em></button>`).join("")}</div>
      ${opcoes.linkComparacao ? `<a class="botao primario cta" href="${opcoes.linkComparacao}"><span>Ver hoje, melhor e ideal</span>${U.ic("seta")}</a>` : ""}</div>`;
    el.querySelectorAll(".hi-ficha").forEach((b) => b.addEventListener("click", () => ir(+b.dataset.q)));
    return;
  }
  const corpo = tela === 0 ? telaCulturas(ctx, U, h) : tela === 1 ? telaArranjo(ctx, U, h) : telaManejo(ctx, U, h);
  el.innerHTML = `<div class="hoje-ideal hi-pergunta">${corpo}
    <div class="hi-nav">
      ${tela === 0 ? `<button type="button" class="botao secundario" id="hi-pular">${U.ic("interrog")} Não sei / pular</button>`
        : `<button type="button" class="botao secundario" id="hi-ant">${U.ic("volta")} Anterior</button>`}
      <button type="button" class="botao ${tela === 1 ? "secundario" : "primario"}" id="hi-prox">${tela === 2 ? `Pronto ${U.ic("ok")}` : tela === 1 ? `Pular ${U.ic("seta")}` : `Próxima ${U.ic("seta")}`}</button>
    </div></div>`;
  const raiz = el.firstElementChild;
  raiz.querySelector("#hi-pular")?.addEventListener("click", () => { rascunho = lerHoje("", ctx.r.padroes); visto = ""; ctx.set({ hoje: "" }); ir(3); });
  raiz.querySelector("#hi-ant")?.addEventListener("click", () => ir(tela - 1));
  raiz.querySelector("#hi-prox").addEventListener("click", () => { if (tela !== 1) gravar(); ir(tela + 1); });
  // 1ª tela: culturas e divisão (edita o rascunho; grava ao avançar)
  raiz.querySelectorAll("[data-c]").forEach((b) => b.addEventListener("click", () => {
    const k = b.dataset.c, ks = Object.keys(h.cult);
    const novo = ks.includes(k) ? ks.filter((x) => x !== k) : Object.keys(CULT).filter((x) => ks.includes(x) || x === k);
    if (!novo.length) return;
    h.cult = igual(novo);
    redesenhar();
  }));
  raiz.querySelectorAll("[data-m]").forEach((b) => b.addEventListener("click", () => { h.cult = mexer(h.cult, b.dataset.m, +b.dataset.d); redesenhar(); }));
  raiz.querySelector("[data-igual]")?.addEventListener("click", () => { h.cult = igual(Object.keys(h.cult)); redesenhar(); });
  // 2ª tela: um toque escolhe e avança
  raiz.querySelectorAll("[data-arr]").forEach((b) => b.addEventListener("click", () => {
    const v = b.dataset.arr;
    h.cons = v === "junto" ? 1 : v === "nao" ? null : 0;
    h.mbx = v === "baixio" ? 1 : null;
    tela = 2;
    gravar();
    redesenhar();
  }));
  // 3ª tela: pares sim/não (tocar de novo desmarca: "não sei")
  raiz.querySelectorAll("[data-k]").forEach((b) => b.addEventListener("click", () => {
    const k = b.dataset.k, v = +b.dataset.v;
    h[k] = h[k] === v ? null : v;
    redesenhar();
  }));
}

/** +10/−10 numa cultura: o + tira da maior das outras; o − dá para a menor das outras. Ninguém fica abaixo de 10%. */
function mexer(cult, k, d) {
  const c = { ...cult }, outras = Object.keys(c).filter((x) => x !== k);
  if (!outras.length) return c;
  if (d > 0) {
    const doa = outras.filter((x) => c[x] > 10).sort((a, b) => c[b] - c[a])[0];
    if (!doa) return c;
    const t = Math.min(d, c[doa] - 10);
    c[doa] -= t; c[k] += t;
  } else {
    const t = Math.min(-d, c[k] - 10);
    if (t <= 0) return c;
    const rec = outras.sort((a, b) => c[a] - c[b])[0];
    c[k] -= t; c[rec] += t;
  }
  return c;
}

// ------------------------------------------------------------------ modo "comparacao": hoje → melhor → ideal
function largura() {
  const w = globalThis.innerWidth || 1000;
  return Math.round(Math.max(280, Math.min(720, Math.min(1120, w) - (w <= 760 ? 66 : 106))));
}

/** O gráfico: 3 colunas (o típico em 3 anos) com o traço do caso ruim; degraus hoje → melhor → ideal. */
function grafico(cols, W) {
  const H = 210, topo0 = 30, base0 = H - 46;
  const vals = cols.flatMap((c) => (c.f ? [c.f.p50, c.f.p10] : [])).concat(0);
  const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
  const y = (v) => topo0 + ((hi - v) / span) * (base0 - topo0);
  const bw = Math.min(96, W / 5.2), gap = W / cols.length;
  let s = `<line class="hi-g-zero" x1="0" x2="${W}" y1="${y(0)}" y2="${y(0)}"/>`;
  cols.forEach((c, i) => {
    const cx = gap * (i + 0.5), x = cx - bw / 2;
    if (c.f) {
      const a = y(Math.max(0, c.f.p50)), b = y(Math.min(0, c.f.p50));
      s += `<g><title>${c.rot}: típico ${rs(c.f.p50)}; caso ruim ${rs(c.f.p10)}</title>
        <rect class="hi-g-bar ${c.cls}" x="${x}" y="${a}" width="${bw}" height="${Math.max(2, b - a)}" rx="5"/>
        <line class="hi-g-ruim" x1="${x - 7}" x2="${x + bw + 7}" y1="${y(c.f.p10)}" y2="${y(c.f.p10)}"/>
        <text class="hi-g-val" x="${cx}" y="${Math.min(a, y(c.f.p10)) - 8}" text-anchor="middle">${rs(c.f.p50)}</text></g>`;
    } else {
      s += `<rect class="hi-g-vazio" x="${x}" y="${y(0) - 28}" width="${bw}" height="28" rx="5"/>
        <text class="hi-g-sub" x="${cx}" y="${y(0) - 10}" text-anchor="middle">sem conta</text>`;
    }
    s += `<text class="hi-g-rot" x="${cx}" y="${H - 24}" text-anchor="middle">${c.rot}</text>
      <text class="hi-g-sub" x="${cx}" y="${H - 7}" text-anchor="middle">${c.f ? `ruim ${rs(c.f.p10)}` : ""}</text>`;
    if (i < cols.length - 1) s += `<path class="hi-g-seta" d="M${cx + bw / 2 + 12} ${base0 - 14} l${gap - bw - 30} 0 m-6 -5 l6 5 -6 5"/>`;
  });
  return `<svg class="hi-graf" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Típico em 3 anos: hoje, melhor e ideal, com o caso ruim">${s}</svg>`;
}

function numeros(U, f, garantir) {
  if (!f) return `<div class="hi-num vazio">sem conta</div>`;
  return garantir
    ? `<div class="hi-num">${rs(f.p10)}</div><p class="hi-num-sub">no caso ruim (1 em 10) · típico ${rs(f.p50)}</p>`
    : `<div class="hi-num">${rs(f.p50)}</div><p class="hi-num-sub">típico · caso ruim ${rs(f.p10)}</p>`;
}
function quebraHtml(U, q) {
  if (!q) return "";
  return `<div class="hi-quebra">${U.dezRocas(q.p, "var(--terra)", "anos de quebra")}<span>quebra em <b>${Math.round(q.p * 10)} de 10</b> anos</span></div>`;
}
const frente = (U, p) => (p === null || p === undefined ? ""
  : p >= 0.5 ? `<span class="chip verde">${U.ic("ok")}à frente de hoje em ${de100(p)} de 100</span>`
    : `<span class="chip terra">${U.ic("alerta")}atrás de hoje em ${de100(1 - p)} de 100</span>`);

/** "milho 50% + feijão 50% · tudo junto" (para rótulos, como o "Jeito de hoje" do passo 4). */
export function descHoje(h) {
  const cs = Object.keys(h.cult).map((k) => `${CULT[k].nome.toLowerCase()} ${h.cult[k]}%`).join(" + ");
  const arr = h.cons === 1 ? "tudo junto" : h.cons === 0 && h.mbx === 1 ? "milho no baixio" : h.cons === 0 ? "em pedaços" : "";
  return [cs, arr].filter(Boolean).join(" · ");
}

function planoMini(r, U) {
  const fx = (r.plano?.faixas || []).filter((f) => f.parte !== "Bordas" && f.anos?.[0]);
  return `<div class="hi-plano">${fx.map((f) => {
    const c = f.anos[0].cultura;
    return `<span class="hi-parte ${U.tipoCss(f.anos[0].tipo)}" title="${U.esc(f.parte)}, 2027: ${U.esc(c)}">${U.ic(U.icCultura(c))}<small>${U.esc(f.parte.replace("Parte ", ""))}</small></span>`;
  }).join("")}</div>`;
}

function desenharComparacao(el, ctx, opcoes) {
  const { r, ef, util: U } = ctx;
  const h = lerHoje(ctx.resp?.hoje || "", r.padroes);
  const c = comparar(r, ef, h);
  const garantir = ef.prioridade === "garantir", vender = ef.prioridade === "vender";
  const mun = r.local?.municipio || "aqui";
  const agro = c.agro.length > 0;
  const FONTE = `${c.base ? `${n0(c.base.n)} combinações de anos já vistos em ${mun} (2027 entre os El Niños fortes ${c.base.anosEN.join(", ")}; 2028 e 2029 entre os ${c.base.anos} anos)` : "IBGE PAM"}; IBGE PAM 1998–2025 em R$ de 2025; custo CONAB (${c.nivel === "desembolso" ? "máquina e insumos" : "só a semente"})`;
  const linkMudar = opcoes.linkMudar || ctx.link?.(2) || "#";

  // abertura
  const sobe = c.hoje && c.melhor && c.melhor.f.p50 > c.hoje.f.p50;
  const h1 = c.hoje ? (sobe ? "Dá para tirar mais do mesmo roçado." : "O seu jeito, lado a lado com o plano.") : "Do seu jeito ao máximo.";
  const abertura = `<div class="titulo-passo"><p class="kicker">Hoje · melhor · ideal</p>
    <h1>${h1}<span class="eco">Hoje, com ajustes, e o máximo.</span></h1>
    <p>O seu roçado de ${U.ha(ef.ha)} refeito nos anos que já aconteceram em ${U.esc(mun)}.</p></div>`;
  const chipHoje = `<div class="hi-linha-chips"><a class="chip" href="${linkMudar}" title="Mudar como você planta hoje">${U.ic("faixas")}${U.esc(descHoje(h))}${h.informado ? "" : " (o mais comum)"} · mudar</a>
    ${c.semRs.length ? `<span class="chip ambar">${U.esc(c.semRs.join(", "))}: sem preço aqui, fora da conta</span>` : ""}</div>`;

  // avisos de dado
  let aviso = "";
  if (!c.fin || c.falta.length) {
    aviso = `<section class="painel alerta hi-aviso">${U.faixa("alerta", "terra", !c.fin ? "Sem a série do IBGE daqui, não inventamos R$." : "Uma parte da conta não fecha aqui.")}
      <div class="hi-linha-chips">${c.falta.map((f) => `<span class="chip terra">${U.esc(f)}</span>`).join("")}</div>
      <p class="pequeno sub">Mostramos só o que dá: os alertas e os ajustes valem do mesmo jeito.</p></section>`;
  } else if (agro) {
    const a = [...c.agro].sort((x, y) => y.kg / y.conab - x.kg / x.conab)[0];
    aviso = `<section class="painel alerta hi-aviso">${U.faixa("alerta", "terra", `Aqui o IBGE mistura lavoura grande: ${a.cultura.toLowerCase()} ${n0(a.kg)} kg/ha.`)}
      <p class="pequeno sub">Os R$ servem só para comparar os três caminhos ${U.selo("medido", "IBGE PAM 1998–2025 e planilhas da agricultura familiar da CONAB")}</p></section>`;
  }

  // gráfico
  const cols = [{ rot: "Hoje", cls: "hoje", f: c.hoje?.f }, { rot: "Melhor", cls: "melhor", f: c.melhor?.f }, { rot: "Ideal", cls: "ideal", f: c.ideal?.f }];
  const temNum = cols.some((x) => x.f);
  const graf = temNum ? `<section class="painel hi-graf-bloco${agro ? " hi-apagado" : ""}">
      <div class="hi-rot">${U.ic("grafico")}<span>Em 3 anos (2027 a 2029) · sobra depois ${c.nivel === "desembolso" ? "de máquina e insumos" : "da semente"} ${U.selo("projecao", FONTE)}</span></div>
      <div class="hi-graf-caixa">${grafico(cols, largura())}</div>
      <p class="hi-legenda"><i class="hi-leg-bar"></i>típico <i class="hi-leg-ruim"></i>caso ruim (1 em 10)</p></section>` : "";

  // colunas
  const alertas = c.alertas.map((a) => `<li>${U.ic(a.icone)}<span>${U.esc(a.txt)}</span></li>`).join("");
  const colHoje = `<section class="painel hi-col hoje">
    <div class="hi-rot">${U.ic("enxada")}<span>Hoje ${U.selo("projecao", `o seu jeito (${descHoje(h)}) refeito nos anos já vistos; ${FONTE}`)}</span></div>
    <p class="hi-desc">${U.esc(descHoje(h))}</p>
    <div class="${agro ? "hi-apagado" : ""}">${numeros(U, c.hoje?.f, garantir)}${quebraHtml(U, c.hoje?.q)}</div>
    ${alertas ? `<p class="hi-mini-rot">o que pesa</p><ul class="hi-alertas">${alertas}</ul>` : ""}</section>`;

  const frente4 = c.lista.slice(0, 4), resto = c.lista.slice(4);
  const item = (a) => `<li class="${a.olho ? "olho" : ""}">${U.ic(a.icone)}<span>${U.esc(a.txt)}${a.passo && ctx.link ? ` <a href="${ctx.link(a.passo)}">ver</a>` : ""}</span>
    ${a.conta ? `<b class="hi-ganho" title="sozinho, típico em 3 anos; à frente de hoje em ${de100(a.aFrente)} de 100">${mais(a.ganho.p50)}</b>` : ""}
    ${a.maniva ? `<em class="hi-tag">precisa de maniva</em>` : ""}${a.olho ? `<em class="hi-tag olho">${OLHO}seu olho</em>` : ""}</li>`;
  const colMelhor = `<section class="painel hi-col melhor">
    <div class="hi-rot">${U.ic("ok")}<span>Melhor ${U.selo("suposicao", "ajustes sugeridos no seu jeito; as áreas são suposição; os R$ saem da mesma conta (" + FONTE + ")")}</span></div>
    <p class="hi-desc">o seu jeito, com ajustes</p>
    <div class="${agro ? "hi-apagado" : ""}">${numeros(U, c.melhor?.f, garantir)}${c.melhor && !c.melhor.igual ? `<p class="hi-dif">${mais(c.melhor.ganho.p50)} no típico</p>` : c.melhor ? `<p class="hi-dif">mesmo R$: os ajustes protegem</p>` : ""}
    ${quebraHtml(U, c.melhor?.q)}<div class="hi-linha-chips">${frente(U, c.melhor?.aFrente)}</div></div>
    <ol class="hi-ajustes">${frente4.map(item).join("")}</ol>
    ${resto.length ? U.verMais(`<ol class="hi-ajustes">${resto.map(item).join("")}</ol>`, `Mais ${resto.length} ajuste${resto.length > 1 ? "s" : ""}`) : ""}</section>`;

  const forr = (c.ideal?.it || []).flat().some((i) => i.uso);
  const atras = c.ideal && c.hoje && c.ideal.f.p50 < Math.max(c.hoje.f.p50, c.melhor?.f.p50 ?? -Infinity);
  const colIdeal = `<section class="painel hi-col ideal${garantir || vender ? " destaque" : ""}">
    <div class="hi-rot">${U.ic("escudo")}<span>Ideal ${U.selo("projecao", "o plano completo do QUADRA (passo 3) na conta do passo 4; " + FONTE)}</span></div>
    <p class="hi-desc">o plano completo do QUADRA</p>${planoMini(r, U)}
    <div class="${agro ? "hi-apagado" : ""}">${numeros(U, c.ideal?.f, garantir)}${quebraHtml(U, c.ideal?.q)}
    <div class="hi-linha-chips">${frente(U, c.ideal?.aFrente)}${!c.ideal ? "" : garantir ? `<span class="chip">${U.ic("escudo")}garantir: vale o caso ruim</span>` : vender ? `<span class="chip">${U.ic("dinheiro")}vender: vale o típico</span>` : ""}</div>
    ${atras && forr ? `<p class="hi-nota">Em R$ fica atrás: o sorgo vira comida da criação, sem preço aqui.</p>` : ""}</div></section>`;

  // fecho (ponto 16)
  const fecho = `<section class="painel hi-fecho">${U.faixa("enxada", "verde", "Quem decide é você, com o técnico.")}
    ${c.olho ? `<p class="hi-olho">${OLHO}<span>O que mais depende do seu olho: <b>${U.esc(c.olho.txt.replace(/\.$/, ""))}</b></span></p>` : ""}
    ${U.verMais(detalhes(c, r, ef, h, U, FONTE), "Ver como calculamos")}</section>`;

  el.innerHTML = `<div class="hoje-ideal hi-comparacao">${opcoes.semTitulo ? "" : abertura}${chipHoje}${aviso}${graf}<div class="hi-cols">${colHoje}${colMelhor}${colIdeal}</div>${fecho}</div>`;
}

function detalhes(c, r, ef, h, U, FONTE) {
  const lin = (rot, x) => (x ? `<tr><td>${rot}</td><td>${rs(x.f.p10)}</td><td><b>${rs(x.f.p50)}</b></td><td>${rs(x.f.p90)}</td>
    <td>${x.q ? `${x.q.k} de ${x.q.n}` : "—"}</td><td>${x.aFrente == null ? "—" : `${de100(x.aFrente)} de 100`}</td></tr>` : `<tr><td>${rot}</td><td colspan="5">sem conta</td></tr>`);
  const A = c.A, sc = c.cenM;
  const areasTxt = (ha, P = 0, fonte = {}) => Object.keys(CULT).filter((k) => (ha[k] || 0) - (fonte[k] || 0) > 0.005 || (k === "mandioca" && (ha[k] || 0) + P > 0.005))
    .map((k) => `${CULT[k].nome.toLowerCase()} ${haTxt((ha[k] || 0) - (fonte[k] || 0) + (k === "mandioca" ? P : 0))}`).join(", ");
  const ajustes = c.ajustes.map((a) => `<li>${U.esc(TXT_AJ[a.id](a, ef).txt)} Sozinho: típico ${mais(a.ganho.p50)} em 3 anos (caso ruim ${mais(a.ganho.p10)}),
    à frente de hoje em ${de100(a.aFrente)} de 100.</li>`).join("");
  return `<h4>Os três caminhos</h4>
    <div class="hi-rola"><table><thead><tr><th>em 3 anos</th><th>caso ruim</th><th>típico</th><th>caso bom</th><th>anos de quebra</th><th>à frente de hoje</th></tr></thead>
    <tbody>${lin("Hoje", c.hoje)}${lin("Melhor", c.melhor)}${lin("Ideal", c.ideal)}</tbody></table></div>
    <p>"Sobra" = valor da colheita (vender ou comer, a preço da região) menos ${c.nivel === "desembolso" ? "máquina, insumos e serviços (CONAB)" : "a semente (CONAB)"}. Nunca é lucro: a mão de obra da família não entra.
      ${U.selo("projecao", FONTE)} ${c.base ? `${n0(c.base.n)} combinações: 2027 é um dos El Niños fortes (${c.base.anosEN.join(", ")}); 2028 e 2029, qualquer um dos ${c.base.anos} anos de ${c.base.ano0} a ${c.base.ano1}. O mesmo ano vale para todas as culturas e para os três caminhos.` : ""}
      Caso ruim = 1 em cada 10 combinações; caso bom = 9 em 10.</p>
    <h4>As áreas ${U.selo("suposicao", "divisão informada; regras de área do módulo")}</h4>
    <ul><li>Hoje, em ${U.ha(A.T)}${A.b > 0 ? ` (${U.ha(A.b)} de baixio)` : ""}: ${U.esc(areasTxt(A.ha))}. Tudo junto ou em pedaços dá o mesmo R$ por ha: a série do IBGE não separa.
      A mandioca fica duas estações no chão: por ano, metade colhe e metade planta.</li>
      ${sc && c.melhor && !c.melhor.igual ? `<li>Melhor${sc.P > 0 ? ", a partir de 2028" : ""}: ${U.esc(areasTxt(sc.ha, sc.P, sc.fonte))}.${sc.P > 0
        ? ` Em 2027 só metade do pedaço novo de mandioca é plantado, e ele colhe a partir de 2028${ef.maniva === "plantada" ? " (com a maniva já no chão, colhe em 2027)" : ""}.` : ""}</li>` : ""}
      <li>Ideal: o plano do passo 3 (partes A, B e C do mesmo tamanho, baixio = metade milho e metade ${U.esc((r.plano?.leguminosa || "caupi").toLowerCase())}), com a conta do passo 4.</li></ul>
    ${ajustes ? `<h4>Os ajustes que têm conta</h4><ul>${ajustes}</ul>` : ""}
    <p>"Milho só no baixio": a conta só vê a troca de milho por feijão na terra alta; o ganho do baixio úmido não está medido. Janela, metade guardada, faixas, fogo e semente
      não têm R$: o IBGE não separa quem faz e quem não faz. ${U.selo("suposicao", "efeito em R$ não medido; as datas são do ZARC 2026/27")}</p>
    <h4>Quebra</h4>
    <p>Ano em que a colheita do roçado (já rodando, no 3º ano) vale menos da metade do típico dele mesmo, nos ${c.base?.anos ?? 28} anos do IBGE. É a régua do IBGE para uma cultura
      (rendimento abaixo de 0,5 × a mediana). ${c.hoje?.q ? `Hoje: ${c.hoje.q.k} de ${c.hoje.q.n} anos; nos El Niños fortes, ${c.hoje.q.enQ} de ${c.hoje.q.nEN}.` : ""}
      ${U.selo("medido", "IBGE PAM 1998–2025")}</p>
    ${c.mult !== 1 || (h.cult.mandioca || 0) > 0 || c.ajustes.some((a) => a.id === "reserva") ? `<p>Raiz da mandioca a R$ ${n0(c.preco, 2)}/kg (a mesma escolha do passo 4). É o número que mais pesa na conta.</p>` : ""}
    <p>Fora da conta: forragem (sorgo, palma), Garantia-Safra, mão de obra, frete e o ganho da rotação contra o consórcio de hoje (não medido).</p>`;
}
