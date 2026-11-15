// QUADRA, módulo extra "Hoje → melhor → ideal" (pedido do José, 14/11/2026): a pessoa diz como planta hoje e vê
// (1) o jeito dela refeito nos anos que já aconteceram no município, (2) o mesmo jeito com ajustes pequenos e
// (3) o plano completo do QUADRA. Dois modos: render(el, ctx, { modo: "pergunta" }) e render(el, ctx, { modo: "comparacao", c3, escolhido })
// (rodada 2: no passo 4 a comparação desenha os números de extras/ideal.js, comparar3 e escolhido; comparar() abaixo fica para os testes).
// A conta é a do passo 4 (js/passos/dinheiro/calculo.js, importado sem mudar): R$ de 2025, 2027 entre os 4 El Niños fortes,
// 2028 e 2029 entre os 28 anos do IBGE, o mesmo ano para todas as culturas (3.136 combinações). Só milho, feijão e mandioca têm R$.
// Contrato do ctx e regras de visual: js/passos/LEIA-ME.md. Onde encaixar e o formato de ctx.resp.hoje: integracao/hoje_ideal.md.
import * as C from "../passos/dinheiro/calculo.js";
import { CULT, opcoesCultura } from "./culturas.js";

// ------------------------------------------------------------------ o jeito de hoje em texto (ctx.resp.hoje)
// "milho:50,feijao:50|cons=1|1chuva=1|queima=1|sem=1" — culturas:% (soma 100) | chaves 1/0; chave ausente = padrão.
// a lista das culturas mora em extras/culturas.js (15/11)
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
  // "informado" = a pessoa disse o que planta; só o arranjo ("|cons=0") deixa as culturas no comum daqui
  if (Object.keys(cult).length) { h.cult = normal(cult); h.informado = true; }
  for (const p of kv) { const [k, v] = p.split("="); if (CHAVES[k]) h[CHAVES[k]] = v === "1" ? 1 : v === "0" ? 0 : null; }
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

/** Meses de plantio e de colheita do milho e do feijão que o montar() do passo 4 já tirou da agenda (S0), por ano.
 *  (Exportadas a partir daqui, 15/11: extras/ideal.js refaz o "Hoje" com a mesma conta.) */
export function mesesS0(m) {
  return (m?.s0 || []).map((its) => Object.fromEntries(["Milho", "Feijão"].map((s) => {
    const p = its.find((i) => i.cultura === s && i.custo), c = its.find((i) => i.cultura === s && i.serie);
    return [s, p && c ? { pl: p.mes, meses: c.meses } : null];
  })));
}

/** Lançamentos no formato de calculo.js (custo no plantio; receita = série do ano × área). Os meses só servem ao caixa. */
export function itensCen(anosPlano, sc, plantada, meses = []) {
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

export const seriesDe = (its) => new Set(its.flat().flatMap((i) => [i.serie, i.custo]).filter((s) => s === "Milho" || s === "Feijão" || s === "Mandioca"));

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
export function quebra(base, itK, mult) {
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
  if (ate || /metade/.test(inter)) semConta.push({ id: "metade", icone: "semente", txt: `El Niño: plante metade e guarde metade${ate ? ` até ${ate.replace(/^~/, "por volta de ")}` : ""}.` });
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
    semConta.unshift({ id: "baixio", icone: "milho", txt: TXT_AJ.baixio(null, ef).txt }); // sem série: o ajuste fica sem R$
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
const TXT_BAIXIO = "Em cima, feijão no lugar do milho (o milho fica no baixio).";
const TXT_AJ = {
  // baixio "não sei": a conta supõe o baixio do padrão, e a frase diz que é condicional
  baixio: (a, ef) => ({ icone: "milho", txt: ef?.tem_baixio == null ? "Se tiver baixio: o milho lá embaixo e feijão em cima." : TXT_BAIXIO }),
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

function topo(U, n, titulo, eco) {
  return `<div class="hi-quiz-topo"><p class="kicker">Seu jeito de hoje · ${n + 1} de 3</p>
    <div class="hi-barra">${[0, 1, 2].map((i) => `<i class="${i < n ? "feito" : i === n ? "atual" : ""}"></i>`).join("")}</div></div>
    <h1 class="hi-quiz-titulo">${U.esc(titulo)}<span class="eco">${U.esc(eco)}</span></h1>`;
}

function telaCulturas(ctx, U, h) {
  const ops = opcoesCultura(ctx.r), ks = Object.keys(h.cult);
  const botoes = ops.map((k) => `<button type="button" class="hi-opcao ${ks.includes(k) ? "marcada" : ""}" data-c="${k}" aria-pressed="${ks.includes(k)}">
    ${U.ic(CULT[k].icone, "gg")}<b>${CULT[k].nome}</b>${CULT[k].semRs ? `<span>fora do R$</span>` : ""}</button>`).join("");
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
  return `${topo(U, 2, "E na hora de plantar?", "Toque no que você faz.")}
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

// ------------------------------------------------------------------ modo "comparacao": hoje → melhorado → ideal (passo 4)
// Rodada 2 (15/11): os números vêm de extras/ideal.js (comparar3, a mesma fonte do "O que você ganha" do Plano). O passo passa
// opcoes.c3 = comparar3(...) e opcoes.escolhido = escolhido(...): este módulo não importa ideal.js (ideal.js importa este).
const SERIE_RS = new Set(["Milho", "Feijão-caupi", "Feijão comum", "Mandioca"]); // as que têm R$ (calculo.js)
const CRIACAO = new Set(["Sorgo forrageiro", "Milheto", "Palma forrageira", "Gliricídia"]); // forragem: comida da criação, fora do R$
const CURTO = { "Feijão-caupi": "feijão", "Feijão comum": "feijão comum", "Sorgo forrageiro": "sorgo", "Sorgo granífero": "sorgo de grão",
  "Palma forrageira": "palma", "Algodão herbáceo": "algodão", "Mucuna-preta": "mucuna", "Cana-de-açúcar": "cana", Gliricídia: "gliricídia" };
const curto = (n) => CURTO[n] || String(n || "").toLowerCase();
const listaE = (xs) => (xs.length <= 1 ? xs.join("") : `${xs.slice(0, -1).join(", ")} e ${xs[xs.length - 1]}`);

function largura() {
  const w = globalThis.innerWidth || 1000;
  return Math.round(Math.max(280, Math.min(720, Math.min(1120, w) - (w <= 760 ? 66 : 106))));
}

/** O gráfico: 3 colunas (o típico em 3 anos) com o traço do caso ruim; degraus hoje → melhorado → ideal; o escolhido com fundo. */
function grafico(cols, W) {
  const H = 196, topo0 = 30, base0 = H - 46;
  const vals = cols.flatMap((c) => (c.f ? [c.f.p50, c.f.p10] : [])).concat(0);
  const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
  const y = (v) => topo0 + ((hi - v) / span) * (base0 - topo0);
  const bw = Math.min(96, W / 5.2), gap = W / cols.length;
  let s = `<line class="hi-g-zero" x1="0" x2="${W}" y1="${y(0)}" y2="${y(0)}"/>`;
  cols.forEach((c, i) => {
    const cx = gap * (i + 0.5), x = cx - bw / 2;
    if (c.sel) s += `<rect class="hi-g-sel" x="${cx - gap / 2 + 4}" y="2" width="${gap - 8}" height="${H - 4}" rx="12"/>`;
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
  return `<svg class="hi-graf" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Sobra em 3 anos: hoje, melhorado e ideal, com o caso ruim">${s}</svg>`;
}

/** "milho + feijão, tudo junto" (a % só quando a divisão não é igual): a frase da linha "Hoje". */
function textoHoje(h) {
  const ks = Object.keys(h.cult), iguais = ks.every((k) => Math.abs(h.cult[k] - 100 / ks.length) <= 1);
  const cs = ks.map((k) => CULT[k].nome.toLowerCase() + (iguais ? "" : ` ${h.cult[k]}%`)).join(" + ");
  const arr = ks.length < 2 ? "" : h.cons === 1 ? "tudo junto" : h.cons === 0 && h.mbx === 1 ? "milho no baixio" : h.cons === 0 ? "em pedaços" : "";
  return [cs, arr].filter(Boolean).join(", ");
}

/** "milho 50% + feijão 50% · tudo junto" (para rótulos, como o "Jeito de hoje" do passo 4). */
export function descHoje(h) {
  const cs = Object.keys(h.cult).map((k) => `${CULT[k].nome.toLowerCase()} ${h.cult[k]}%`).join(" + ");
  const arr = h.cons === 1 ? "tudo junto" : h.cons === 0 && h.mbx === 1 ? "milho no baixio" : h.cons === 0 ? "em pedaços" : "";
  return [cs, arr].filter(Boolean).join(" · ");
}

/** Valor de um item de ideal.beneficios na célula da tabela ("R$ 1.010", "2 em 10"; null = "não medido"). */
function valorItem(it) {
  if (!it || it.valor == null) return `<span class="hi-nm">não medido</span>`;
  return it.unidade === "em 10" ? `${n0(it.valor)} em 10` : rs(it.valor);
}

/** O que fica fora do R$ (hoje e os planos à vista): forragem → "comida da criação"; o resto → "o IBGE não tem a série aqui". */
function foraDoRs(h, c3, tipos) {
  const nomes = new Set();
  for (const k of Object.keys(h.cult)) { const n = CULT[k]?.motor; if (k === "outra") nomes.add("outra"); else if (n && !SERIE_RS.has(n)) nomes.add(n); }
  for (const t of tipos) for (const n of c3[t]?.beneficios?.rs?.semRs || []) nomes.add(n);
  for (const t of tipos) for (const f of c3[t]?.plano?.faixas || []) for (const c of f.anos || []) if (CRIACAO.has(c.cultura) && f.parte !== "Bordas") nomes.add(c.cultura);
  const cria = [...nomes].filter((n) => CRIACAO.has(n)), sem = [...nomes].filter((n) => !CRIACAO.has(n) && n !== "outra");
  const out = [];
  if (cria.length) out.push(`${cap(listaE(cria.map(curto)))}: comida da criação, fora do R$.`);
  if (sem.length) out.push(`O IBGE não tem a série de ${listaE(sem.map(curto))} aqui: fora do R$.`);
  if (nomes.has("outra")) out.push("A \"outra\" cultura fica fora do R$.");
  return out;
}
const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);

/** A mandioca nova do plano custa em 2027 e só colhe em 2028 (por isso 2027 sai abaixo de hoje). */
const manivaNova = (p) => (p?.faixas || []).some((f) => /^Parte /.test(f.parte) && f.anos?.[0]?.cultura === "Mandioca" && !f.anos[0].ja_no_chao);

/**
 * Modo "comparacao": o gráfico Hoje → Melhorado → Ideal (sobra em 3 anos), uma linha para cada (o que é, e o "mudar") e as 3 linhas
 * de R$ do "O que você ganha" (ano normal, 2027, anos de quebra). opcoes: c3, escolhido (de extras/ideal.js), linkMudar (Sua roça),
 * linkIdeal (O plano, lado "O ideal", onde a prioridade muda), ruim (HTML do "1 em 10", para o glossário) e olhoAgro (texto do
 * "seu olho" do aviso de lavoura grande).
 */
function desenharComparacao(el, ctx, opcoes) {
  const { r, ef, util: U } = ctx;
  const c3 = opcoes.c3, esc = opcoes.escolhido || {};
  if (!c3) { el.innerHTML = ""; return; }
  const h = lerHoje(ctx.resp?.hoje || "", r.padroes);
  const B = { hoje: c3.hoje?.beneficios, melhor: c3.melhor?.beneficios, ideal: c3.ideal?.beneficios };
  const sel = esc.tipo === "ideal" ? "ideal" : "melhor";
  const pi = c3.ideal?.plano, pm = c3.melhor?.plano;
  const rsOk = ["hoje", "melhor", "ideal"].map((t) => B[t]?.rs).filter((x) => x?.ok);
  const info = rsOk[0]?.info;
  const mun = r.local?.municipio || "aqui";
  const agro = rsOk.some((x) => x.agro?.length);
  const FONTE = `${info ? `${n0(info.n)} combinações de anos já vistos em ${mun} (2027 entre os El Niños fortes ${info.anosEN.join(", ")}; 2028 e 2029 entre os ${info.anos} anos)` : "IBGE PAM"}; IBGE PAM 1998–2025 em R$ de 2025; custo CONAB (${ef.custo === "desembolso" ? "máquina e insumos" : "só a semente"}); a mão de obra da família não entra`;

  // gráfico (os 3 anos: o número do passo 4)
  const COLS = [["hoje", "Hoje"], ["melhor", "Melhorado"], ["ideal", "Ideal"]];
  const cols = COLS.map(([t, rot]) => ({ rot, cls: t, sel: t === sel, f: B[t]?.rs?.ok ? B[t].rs.tres_anos : null }));
  const temNum = cols.some((x) => x.f);

  // avisos de dado: sem a série, uma parte sem conta ou lavoura grande
  const faltas = [...new Set(["hoje", "melhor", "ideal"].flatMap((t) => (B[t]?.rs && !B[t].rs.ok ? B[t].rs.falta || [] : [])))];
  let avTit = "", avCorpo = "";
  if (!r.financeiro || !temNum) {
    avTit = !r.financeiro ? "Sem a série do IBGE daqui, não inventamos R$." : "Aqui a conta de R$ não fecha.";
    avCorpo = `<div class="hi-linha-chips">${faltas.map((f) => `<span class="chip terra">${U.esc(f)}</span>`).join("")}</div>`;
  } else if (faltas.length) {
    avTit = "Uma parte da conta não fecha aqui.";
    avCorpo = `<div class="hi-linha-chips">${faltas.map((f) => `<span class="chip terra">${U.esc(f)}</span>`).join("")}</div>`;
  } else if (agro) {
    const a = rsOk.flatMap((x) => x.agro || []).sort((x, y) => y.kg / y.conab - x.kg / x.conab)[0];
    avTit = "Aqui o IBGE mistura lavoura grande.";
    const selo = U.selo("medido", `IBGE PAM 1998–2025 (${a.cultura.toLowerCase()} ${n0(a.kg)} kg/ha) e planilhas da agricultura familiar da CONAB (${n0(a.conab)} kg/ha)`);
    avCorpo = `<p class="hi-olho-linha">Os R$ só servem para comparar.${opcoes.olhoAgro ? ` ${U.esc(opcoes.olhoAgro)} <em class="hi-tag olho">${OLHO}seu olho</em>` : ""} ${selo}</p>`;
  }
  const aviso = !avTit ? "" : temNum ? `<div class="hi-aviso-linha">${U.ic("alerta")}<div><b>${avTit}</b>${avCorpo}</div></div>`
    : `<section class="painel alerta hi-aviso">${U.faixa("alerta", "terra", avTit)}${avCorpo}</section>`;

  // uma linha para cada caminho
  const tag = (t) => (t === sel ? ` <em class="hi-tag sel" title="o lado escolhido em O plano: o Relatório segue este">escolhido</em>` : "");
  const linha = (t, icone, rot, desc) => `<div class="hi-bloco ${t}"><div class="hi-linha"><div class="hi-l-txt"><p class="hi-l-rot">${U.ic(icone)}${rot}${tag(t)}</p>${desc}</div></div></div>`;
  const linkMudar = opcoes.linkMudar || ctx.link?.(2) || "#";
  const chipHoje = `<a class="hi-mudar" href="${linkMudar}" data-editar="hoje" title="Mudar como você planta hoje">${U.esc(textoHoje(h))}${h.informado ? "" : " (o comum daqui)"} · <u>mudar</u></a>`;
  const entrou = (pm?.notas || []).find((n) => /^Entr(ou|aram) /.test(n)); // a planta que entrou para não ficar uma cultura só
  const descMelhor = pm?.nao_gira ? (pm.notas?.[0] || "Uma cultura só: não dá para girar.") : entrou || "Só o que você planta, girando em faixas.";
  // sem resposta, a prioridade é a padrão pelos números (ideal.escolhaPadrao): "(sugerido: a que mais sobra em 2027)"
  const sugerido = esc.prioridade_origem && esc.prioridade_origem !== "resposta"
    ? (/sobra/.test(esc.prioridade_origem) ? ` (sugerido: ${U.esc(esc.prioridade_origem)})` : /El Niño/.test(esc.prioridade_origem) ? " (sugerido: El Niño)" : " (sugerido)") : "";
  const linkIdeal = opcoes.linkIdeal || ctx.link?.(3) || "#";
  const descIdeal = `<a class="hi-mudar" href="${linkIdeal}" title="Mudar o que vale mais para você, no plano">O que vale mais: <b>${U.esc(pi?.nome || "")}</b>${sugerido} · <u>mudar</u></a>
    ${pi?.manchete && pi.jeito !== "plano" ? `<p class="hi-l-desc">${U.esc((mancheteIdeal(pi, pm) || pi.manchete).replace(/^[^:]+:\s*/, "").replace(/^./, (x) => x.toUpperCase()))}</p>` : ""}`;
  const linhas = linha("hoje", "enxada", "Hoje", chipHoje) + linha("melhor", "ok", "Melhorado", `<p class="hi-l-desc">${U.esc(descMelhor)}</p>`) +
    linha("ideal", "escudo", "Ideal", descIdeal);

  // as 3 linhas de R$ de "O que você ganha" (a mesma fonte: ideal.beneficios)
  const item = (t, id) => B[t]?.itens?.find((x) => x.id === id) || null;
  const tab = !r.financeiro ? "" : `<div class="hi-tab" role="table" aria-label="Sobra e quebra: hoje, melhorado e ideal">
    <div class="hi-tab-cab" role="row"><span></span>${COLS.map(([t, rot]) => `<span class="hi-tab-col ${t}${t === sel ? " sel" : ""}" role="columnheader">${rot}</span>`).join("")}</div>
    ${["rs_tipico", "rs_el_nino", "quebra_10"].map((id) => {
      const ref = item(sel, id) || item("hoje", id);
      return `<div class="hi-tab-lin" role="row"><span class="hi-tab-rot" role="rowheader">${U.esc(ref?.rotulo || id)} ${ref ? U.selo(ref.selo, ref.fonte) : ""}</span>
        ${COLS.map(([t]) => { const it = item(t, id); return `<span class="hi-tab-val${t === sel ? " sel" : ""}" role="cell" title="${U.esc(it?.fonte || "")}">${valorItem(it)}</span>`; }).join("")}</div>`;
    }).join("")}</div>`;
  const notas = foraDoRs(h, c3, ["melhor", "ideal"]);
  const v27 = (t) => item(t, "rs_el_nino")?.valor;
  const caiEm27 = ["melhor", "ideal"].filter((t) => manivaNova(c3[t]?.plano) && v27(t) != null && v27("hoje") != null && v27(t) < v27("hoje"));
  if (caiEm27.length) notas.unshift("Em 2027 a maniva nova só custa: colhe em 2028.");
  const chips = notas.length ? `<ul class="hi-notas">${notas.map((n) => `<li>${U.esc(n)}</li>`).join("")}</ul>` : "";

  const graf = temNum ? `<section class="painel hi-graf-bloco">
      <div class="hi-rot">${U.ic("grafico")}<span>Em 3 anos (2027 a 2029), sobra ${U.selo("projecao", FONTE)}</span></div>
      <div class="${agro ? "hi-apagado" : ""}"><div class="hi-graf-caixa">${grafico(cols, largura())}</div>
      <p class="hi-legenda"><i class="hi-leg-bar"></i>típico <i class="hi-leg-ruim"></i>caso ruim: ${opcoes.ruim || "1 em 10"}</p></div>
      ${linhas}${tab}${chips}${aviso}</section>` : `${aviso}<section class="painel hi-graf-bloco">${linhas}${chips}</section>`;
  el.innerHTML = `<div class="hoje-ideal hi-comparacao${agro ? " agro" : ""}">${graf}</div>`;
}

/** A manchete do ideal comparada ao SEU JEITO (pi = ideal.planoIdeal, pm = ideal.planoMelhor): o que o ideal tem a mais em partes ×
 *  anos, fora das bordas (entra o que ganha 2 ou mais; forragem não é "para vender"). Usada no Plano e em Quanto rende. A manchete
 *  de cenarios.js compara com o plano do núcleo e dizia "Mais renda: mais feijão" com mandioca em 2 das 3 partes (Quixadá, 15/11).
 *  null = sem diferença clara (fica a manchete de pi). Mora aqui porque ideal.js importa este arquivo (sem ciclo). */
const PQ_M = { garantir: ["que aguenta a seca", "que aguentam a seca"], vender: ["para vender", "para vender"],
  solo: ["que cuida da terra", "que cuidam da terra"] };
const NOME_M = { garantir: "Guardar água", vender: "Mais renda", solo: "Cuidar do solo" };
const CURTO_M = { "Feijão-caupi": "feijão", "Feijão comum": "feijão comum", "Sorgo forrageiro": "sorgo forrageiro", "Sorgo granífero": "sorgo de grão",
  "Palma forrageira": "palma", "Mucuna-preta": "mucuna", "Algodão herbáceo": "algodão", "Cana-de-açúcar": "cana", "Pousio pastejado": "descanso" };
const FORRAGEM_M = new Set(["sorgo forrageiro", "palma", "milheto", "gliricídia", "mucuna"]);
export function mancheteIdeal(pi, pm) {
  const pri = pi?.prioridade;
  if (!PQ_M[pri] || !pm) return null;
  const curto = (c) => { const b = String(c || "").replace(/ no milho em pé$/, "").trim(); return CURTO_M[b] || b.toLowerCase(); };
  const conta = (p) => { const g = {}; for (const f of p?.faixas || []) if (f.parte !== "Bordas") for (const a of f.anos || [])
    for (const c of String(a.cultura || "").split(" + ")) { const k = curto(c); g[k] = (g[k] || 0) + 1; } return g; };
  const ci = conta(pi), cm = conta(pm), dif = (k) => ci[k] - (cm[k] || 0);
  const mais = Object.keys(ci).filter((k) => k !== "descanso" && dif(k) >= 2 && !(pri === "vender" && FORRAGEM_M.has(k)))
    .sort((x, y) => dif(y) - dif(x)).slice(0, 2);
  if (!mais.length) return null;
  const lista = mais.length > 1 ? `${mais[0]} e ${mais[1]}` : mais[0];
  return `${NOME_M[pri]}: mais ${lista}, ${PQ_M[pri][mais.length > 1 ? 1 : 0]}.`;
}

// Peças reaproveitadas pela tela única "Sua roça" (passos/perguntas.js).
export { CULT, igual, mexer, opcoesCultura };
