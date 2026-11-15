// Passo 5, "Segurança" (versão 2, pouco texto): o que já se sabe hoje e, para cada cultura do plano, o que a roça do município colheu
// em anos parecidos (2027 com o El Niño medido; 2028–29 só com o clima). Método: analise/projecao.md ("C + D + conforme");
// dados: ctx.r.projecao (dados/projecao_mun.json), ctx.r.financeiro (dados/financeiro_mun.json); acerto: dados/projecao_metricas.txt.
import { leque, legendaLeque, eixoBom, anosParecidos, quadro28 } from "./seguranca/graficos.js";
import { termo } from "../extras/glossario.js";
import { olho, OLHOS } from "../extras/voce_decide.js";
import { ufDe } from "../comum.js";
import { CONAB_FAMILIAR_KG_HA } from "./dinheiro/calculo.js";
// Ordem (analise/fluxo/00_FLUXO_FINAL.md, seção 7, D): abertura → "2027, cada cultura" (1 linha por cultura; régua e cartões no ver mais)
// → "E se chover…" (extra cenario_chuva, abre em 100%) → portões → memória (extra historico) → "Leve para o técnico" → ver mais do fim
// (detalhes de hoje, 28 anos, o que não dá para projetar, quanto já acertou). "Seu olho" (ponto 16) nos portões e na memória; onde o IBGE
// mistura lavoura grande, o mesmo aviso do passo 4 vem no ver mais dos cartões (é lá que aparecem os sacos/ha).

const SERIE = [["Milho", /^milho/i, "cereal"], ["Feijão", /^feij/i, "leguminosa"], ["Mandioca", /^mandioca/i, "tampão"]];
const serieDe = (nome) => (SERIE.find(([, re]) => re.test(nome || "")) || [null])[0];
const UN = { Milho: "sacos/ha", Feijão: "sacos/ha", Mandioca: "t/ha" };
const UN_CURTA = { Milho: "sacos", Feijão: "sacos", Mandioca: "t" };
const emUn = (c, kg) => (kg == null ? null : c === "Mandioca" ? kg / 1000 : kg / 60);
const PISO_KG = { Milho: 30, Feijão: 30, Mandioca: 500 }; // abaixo disso (meio saco; meia tonelada) o piso é "quase nada"

// Backtest novo: dados/projecao_metricas.txt (gerado 14/11/2026 18:24 por ferramentas/preparar_projecao.py), coluna DEPOIS
// (definição única de El Niño forte: 1998, 2010, 2016, 2024). WF = walk-forward 2008–2025, só com o passado.
const CALIB = {
  fonte: "dados/projecao_metricas.txt (gerado 14/11/2026 18:24), bloco 'Resumo: antes × depois', coluna DEPOIS",
  wf_media: 0.793, wf_pior: 0.622, wf_en_cob: 0.675, wf_en_piso: 0.843, wf_en_prev: 0.34, wf_en_obs: 0.25,
  milho: [["2010", 0.57, 0.38], ["2016", 0.42, 0.49], ["2024", 0.48, 0.11]], // WF, milho, quebra prevista × observada
};
// Os 7 jeitos testados (analise/projecao.md, seção 3, linha "WF, todos · média por ano"; milho: linha "WF, milho · cobertura").
const METODOS = [
  ["F", "região + El Niño, alargado pelo teste (o escolhido)", 78], ["C", "município puxado para a região", 69], ["A", "só o município", 67],
  ["D", "só os anos de El Niño", 65], ["B", "tirando a tendência", 61], ["D2", "El Niño + tendência", 60], ["E", "regressão por quantis, tudo junto", 56],
];
// Portões (analise/projecao.md, seção 4 e achados; portoes_precos.py): milho no semiárido de CE, RN, PB, PI e PE, 1998–2025,
// razão ao normal do município por classe da chuva IMERG desde 1/fev (meses inteiros: fev–mar ≈ 19/mar, fev–abr ≈ 30/abr).
const PORTOES = {
  fonte: "chuva GPM IMERG (NASA) × colheita IBGE PAM (analise/projecao.md, seção 4; portoes_precos.py): milho no semiárido de CE, RN, PB, PI e PE, 23.704 município-anos, 1998–2025",
  linhas: [
    { nome: "Chuva fraca", faixa: "menos de ¾ do normal", cor: "alerta", cq: "var(--terra)", p50: 0.33, q_abr: 0.60, q_mar: 0.54 },
    { nome: "Chuva no meio", faixa: "de ¾ ao normal", cor: "destaque", cq: "var(--amber)", p50: 0.72, q_abr: 0.37, q_mar: 0.33 },
    { nome: "Chuva boa", faixa: "o normal ou mais", cor: "verde", cq: "var(--green)", p50: 1.36, q_abr: 0.10, q_mar: 0.13 },
  ],
};
const NAO_PROJETA = [
  ["Secas de vários anos, como a de 2012–15", "vêm sem aviso do oceano; nesses anos o leque acertou só 6 a 7 em 10."],
  ["A roça da sua família", "o IBGE dá a média do município; uma roça sozinha varia mais que a média."],
  ["A mandioca ano a ano", "o IBGE repete o número do ano anterior em muitos municípios; o leque dela parece mais seguro do que é."],
  ["Sorgo, palma, gliricídia, milheto e guandu", "não têm série no município; o caupi entra no \"feijão\" do IBGE, que junta caupi e feijão comum."],
  ["O ganho da rotação", "os +24% do cereal depois da leguminosa vêm de estudos (clima análogo), não estão na série do município."],
  ["O preço futuro", "o valor usa o preço de referência de 2016–2025, em R$ de 2025."],
  ["Irrigação e baixio", "a série do IBGE mistura tudo e é quase toda de sequeiro."],
  ["O litoral leste", "o satélite (IMERG) capta só 39–72% da chuva medida no chão; lá os portões não valem."],
  ["O cerrado com produtividade subindo", "o lado de cima do leque (P90) sai alto demais (ex.: Barreiras)."],
];

/** Frequência natural: 0,61 → "6 em 10". */
function freq(p) {
  if (p === null || p === undefined) return "—";
  const n = Math.round(p * 10);
  return n === 0 ? "menos de 1 em 10" : n === 10 ? "quase 10 em 10" : `${n} em 10`;
}
/** Idem para "não paga": 0,95 e 0,05 são o limite da interpolação no JSON ("9 ou mais" e "até 1"). */
function freqPaga(p) {
  if (p === null || p === undefined) return "—";
  if (p >= 0.95) return "9 ou mais em 10";
  if (p <= 0.05) return "até 1 em 10";
  return freq(p);
}
/** Frase do dinheiro (vem depois de "2027:"). */
function fraseNaoPaga(p, oque) {
  if (p >= 0.95) return `em 9 ou mais de 10 anos parecidos, a colheita não paga ${oque}.`;
  if (p <= 0.05) return `a colheita paga ${oque} em 9 ou mais de 10 anos parecidos.`;
  const n = Math.round(p * 10);
  return n === 0 ? `a colheita quase sempre paga ${oque}.` : `em ${n} de 10 anos parecidos, a colheita não paga ${oque}.`;
}

/** P(receita < custo) por interpolação nos quantis (mesma regra do preparar_projecao.py: limite 0,05 e 0,95). */
function chanceAbaixo(q, c) {
  const pts = [[0.1, q.p10], [0.2, q.p20], [0.5, q.p50], [0.8, q.p80], [0.9, q.p90]];
  if (c <= pts[0][1]) return 0.05;
  if (c > pts[4][1]) return 0.95;
  for (let i = 1; i < pts.length; i++) {
    const [p0, v0] = pts[i - 1], [p1, v1] = pts[i];
    if (c <= v1) return v1 === v0 ? p1 : p0 + ((p1 - p0) * (c - v0)) / (v1 - v0);
  }
  return 0.95;
}

const fmtUn = (U, v) => (v === null || v === undefined ? "—" : U.num(v, v > 0 && v < 10 ? 1 : 0));

/** Colheita de um ciclo a partir da agenda: "mai–jun/2027". 2028–29 repetem os meses (suposição). */
function colheita(U, linhas, parte, cultura, ano) {
  const l = linhas.find((x) => x.parte === parte && x.cultura === cultura && x.estacao === ano)
    || linhas.find((x) => x.parte === parte && x.cultura === cultura)
    || linhas.find((x) => x.cultura === cultura);
  if (!l || !l.colher) return null;
  const k = ano - (l.estacao || ano);
  const re = /(\d{2})\/(\d{2})\/(\d{4})|([a-zç]{3})\/(\d{4})/g;
  const d = [];
  let m;
  while ((m = re.exec(l.colher)) && d.length < 2) d.push(m[1] ? { m: +m[2] - 1, a: +m[3] + k } : { m: U.MESES.indexOf(m[4]), a: +m[5] + k });
  if (!d.length || d.some((x) => x.m < 0)) return null;
  const [a, b = a] = d;
  const txt = a.a === b.a ? (a.m === b.m ? `${U.MESES[a.m]}/${a.a}` : `${U.MESES[a.m]}–${U.MESES[b.m]}/${a.a}`)
    : `${U.MESES[a.m]}/${a.a}–${U.MESES[b.m]}/${b.a}`;
  return { txt, sup: k !== 0 || /supos/i.test(l.colher), fonte: `${k !== 0 ? `datas de ${ano} iguais às de ${l.estacao}. ` : ""}${l.colher}` };
}

/** Ciclos do plano: um por parte e ano, mais o caupi em revezamento no milho em pé quando o plano diz. */
function ciclos(U, r) {
  const pl = r.plano, lin = r.agenda?.linhas || [];
  if (!pl?.faixas) return [];
  const out = [];
  for (const f of pl.faixas) {
    pl.anos.forEach((ano, i) => {
      const a = f.anos[i];
      if (!a) return;
      out.push({ parte: f.parte, ano, cultura: a.cultura, tipo: a.tipo, colhe: colheita(U, lin, f.parte, a.cultura, ano) });
      if (/revezamento/i.test(a.texto || "")) {
        const rel = lin.find((l) => l.parte === f.parte && l.cultura !== a.cultura && /em pé/i.test(l.cultura));
        if (rel) out.push({ parte: f.parte, ano, cultura: rel.cultura, tipo: rel.tipo, revez: true, colhe: colheita(U, lin, f.parte, rel.cultura, ano) });
      }
    });
  }
  return out;
}

/** Área de um ciclo (mesma suposição do passo "Quanto rende": partes iguais; baixio ½ milho + ½ caupi; bordas fora). */
function areaCiclo(ef, c) {
  if (/^bordas/i.test(c.parte)) return 0;
  if (/^baixio/i.test(c.parte)) return (ef.baixio_ha || 0) / 2;
  return Math.max(0, (ef.ha - (ef.baixio_ha || 0)) / 3);
}

/** Dados de uma cultura com série: quantis em unidades, receita (mandioca no preço da raiz escolhido) e chances de não pagar. */
function cultura(r, ef, c) {
  const p = r.projecao?.[c];
  if (!p?.anos) return null;
  const normalKg = p[Object.keys(p).find((k) => /^mediana/.test(k))];
  let fator = 1, precoTxt = null;
  const fin = r.financeiro;
  if (c === "Mandioca" && fin?.precos_raiz && p.preco_r2025_kg > 0) {
    const pr = fin.precos_raiz[ef.raiz] ?? fin.precos_raiz[fin.precos_raiz.padrao];
    if (pr > 0) {
      fator = pr / p.preco_r2025_kg;
      precoTxt = { preco: pr, origem: { municipio: "o preço daqui", uf_mediana: `a mediana ${ufDe(r.local.uf)}`, uf_p25: `o preço baixo ${ufDe(r.local.uf)}` }[ef.raiz] || "a referência" };
    }
  }
  const custo = p.custo_r2025_ha || fin?.culturas?.[c]?.custo_ha || {};
  const anos = {};
  for (const [a, d] of Object.entries(p.anos)) {
    const q = Object.fromEntries(Object.entries(d.kg_ha).map(([k, v]) => [k, emUn(c, v)]));
    const rec = d.receita_r2025_ha ? Object.fromEntries(Object.entries(d.receita_r2025_ha).map(([k, v]) => [k, v * fator])) : null;
    const nps = custo.semente > 0 ? (fator === 1 && d.chance_nao_paga_semente != null ? d.chance_nao_paga_semente : rec ? chanceAbaixo(rec, custo.semente) : null) : null;
    const npd = custo.desembolso > 0 ? (fator === 1 && d.chance_nao_paga_desembolso != null ? d.chance_nao_paga_desembolso : rec ? chanceAbaixo(rec, custo.desembolso) : null) : null;
    anos[a] = { q, kg: d.kg_ha, quebra: d.chance_quebra, rec, nps, npd, base: d.base || "" };
  }
  const medido = Object.entries(p.medido_anos_parecidos_kg_ha || {}).map(([a, v]) => [a, emUn(c, v)]);
  return { c, p, normal: emUn(c, normalKg), normalKg, anos, medido, custo, fator, precoTxt,
    n_en: p.n_anos_el_nino_forte ?? medido.length, tres: p.chance_ao_menos_1_quebra_2027_2029,
    preco: (p.preco_r2025_kg || 0) * fator, artefato: anos["2027"] && anos["2028"] && anos["2027"].q.p90 > 1.3 * anos["2028"].q.p90 };
}

/** Eixo comum de uma cultura (o mesmo nos 3 anos, para os leques serem comparáveis). */
function eixoCultura(d) {
  const p90 = Math.max(...Object.values(d.anos).map((a) => a.q.p90 || 0));
  return eixoBom(Math.max(d.normal * 1.5, Math.min(p90, d.normal * 2.5)));
}

/** "nos 3 El Niños fortes ... (2010: 58%; ...), 2 ficaram no terço mais seco" → {n, secos, anos:[[ano, %]]}. */
function perspectiva(txt) {
  const m = /nos (\d+) El Niños fortes[^(]*\(([^)]*)\)[^,]*, (\d+) ficaram no terço mais seco/.exec(txt || "");
  if (!m) return null;
  return { n: +m[1], secos: +m[3], anos: [...m[2].matchAll(/(\d{4}): (\d+)%/g)].map((x) => [x[1], +x[2]]) };
}

// --------------------------------------------------------------------------------------------------------------------- blocos
function abertura(U, r, dados) {
  const ds = Object.values(dados);
  const q27 = Math.max(0, ...ds.map((d) => d.anos["2027"]?.quebra ?? 0));
  let h = "Aqui o IBGE não tem série.", eco = "Vale o que você vê na roça.";
  if (ds.length) {
    h = q27 >= 0.45 ? "2027 tende a ser apertado." : q27 >= 0.25 ? "2027 pede cuidado." : "2027 tende a ficar perto do normal.";
    eco = q27 >= 0.25 ? "2028 e 2029: normal." : "2028 e 2029 também.";
  }
  // os portões (19/mar e 30/abr) só foram medidos no sertão de CE, RN, PB, PI e PE
  const olhar = r.agenda?.portoes !== false ? "Olhe a terra em 19/mar e 30/abr e decida com o técnico."
    : "Olhe a terra antes de plantar e decida com o técnico.";
  return `<div class="titulo-passo"><p class="kicker">Se secar</p><h1>${h}<span class="eco">${eco}</span></h1>
    <p>${olhar}</p></div>`;
}

/** "2027, cada cultura": 1 linha por cultura (quebra em X de 10, grade de 10 roças) e, no ver mais, a régua dos anos e os cartões. */
function bloco2027(U, r, dados, lista, cartoes, avisoAgro, quadro, hoje) {
  if (!r.plano) return `<section class="seg-bloco"><p class="sub">Sem plano para este lugar.</p></section>`;
  const caupi = lista.some((c) => serieDe(c.cultura) === "Feijão" && /caupi/i.test(c.cultura));
  let termoFeito = false; // "o que é?" só na 1ª vez
  const linhas = Object.values(dados).filter((d) => d.anos["2027"]).map((d) => {
    const q = d.anos["2027"].quebra, n = Math.round((q ?? 0) * 10);
    const dez = termoFeito ? `${n} de 10` : termo("em_dez", `${n} de 10`);
    if (n > 0 && n < 10) termoFeito = true;
    const txt = n <= 0 ? "quase nunca quebra" : n >= 10 ? "quase sempre quebra" : `quebra em <b>${dez}</b>`;
    return `<div class="seg-27-linha">${U.ic(U.icCultura(d.c), "g")}
      <div class="seg-27-nome"><b>${U.esc(d.c)}${d.c === "Feijão" && caupi ? ' <span class="sub">(caupi)</span>' : ""}</b><span>${txt}</span></div>
      ${U.dezRocas(q, "var(--terra)", `anos parecidos, ${d.c.toLowerCase()} quebra`)}</div>`;
  }).join("");
  return `<section class="seg-bloco seg-27">
    <p class="kicker">2027, cada cultura ${U.selo("projecao", "anos parecidos do IBGE (PAM 1998–2025), município + mesorregião, alargado pelo teste com o passado")}</p>
    ${linhas ? `<div class="seg-27-linhas">${linhas}</div>
      <p class="sub pequeno seg-27-nota">Quebrar = colher menos da metade do normal daqui.</p>`
      : `<p class="sub">O IBGE não tem série suficiente deste município para projetar.</p>`}
    ${cartoes ? U.verMais(`<p>Não é previsão: é o que a roça de ${U.esc(r.local.municipio)} colheu em anos parecidos, desde 1998.</p>
      ${avisoAgro}${reguaAnos(U, r, dados)}${cartoes}${semSerie(U, lista)}${hoje}${quadro}`, "Cada cultura, 2027 a 2029")
      : `${semSerie(U, lista)}${U.verMais(`${hoje}${quadro}`, quadro ? "Ver hoje e os 28 anos" : "Ver o que já se sabe hoje")}`}
  </section>`;
}

/** O que já se sabe hoje (o mar, o estado, o solo): vai inteiro para o ver mais "Ver os detalhes de hoje". */
function blocoHoje(U, r) {
  const e = r.este_ano || {}, u = r.el_nino_uf, pm = perspectiva(e.perspectiva);
  // o mar e o estado já estão no passo 1: aqui fica só o que é deste município
  const aqui = pm ? [`Aqui, <b>${pm.secos} de ${pm.n}</b> anos de mar assim trouxeram estação seca.`, e.perspectiva]
    : e.smap?.status === "ok" ? [`O solo agora está <b>${U.esc(e.smap.classe)}</b>.`, e.smap.texto] : null;
  const reg = e.regime;
  const naoSabe = [reg && reg.quadra === false ? `a chuva da estação (${reg.estacao})` : "o Atlântico de fev–abr", "quanto vai chover em 2027", "o preço da colheita"];
  const ufAnos = u?.pct_terco_seco ? (u.anos || Object.keys(u.pct_terco_seco)).map((a) => {
    const v = u.pct_terco_seco[a];
    return `${a}: ${v == null ? "sem dado (o satélite começa em jan/1998)" : `${U.num(v / 10)} em 10`}`;
  }).join(" · ") : "";
  return `<p class="kicker">O que já se sabe hoje${aqui ? U.selo("medido", aqui[1] || "") : ""}</p>
    ${aqui ? U.faixa("pino", pm && pm.secos * 2 > pm.n ? "ambar" : "azul", aqui[0]) : ""}
    <div class="seg-naosabe"><span class="sub">Ainda não sabemos:</span>${naoSabe.map((t) => `<span class="chip">${U.ic("interrog")}${U.esc(t)}</span>`).join("")}</div>
    <ul class="seg-lista">
      <li><b>O mar:</b> ${U.esc(e.texto_oni || "")}</li>
      ${u ? `<li><b>Nos municípios ${U.esc(ufDe(u.uf))}, por ano:</b> ${U.esc(ufAnos)}. ${U.esc(u.definicao || "")}</li>` : ""}
      ${e.perspectiva ? `<li><b>Aqui:</b> ${U.esc(e.perspectiva)}</li>` : ""}
      ${e.smap?.status === "ok" ? `<li><b>O solo agora:</b> ${U.esc(e.smap.texto)}</li>` : ""}
      ${e.chuva_recente ? `<li><b>A chuva recente:</b> ${U.esc(e.chuva_recente)}</li>` : ""}
    </ul>`;
}

function reguaAnos(U, r, dados) {
  const d0 = Object.values(dados)[0];
  const base27 = d0?.anos["2027"]?.base || "", base28 = d0?.anos["2028"]?.base || "";
  const n = d0?.n_en ?? r.financeiro?.anos_el_nino_forte?.length;
  const anosEN = (r.financeiro?.anos_el_nino_forte || Object.keys(d0?.p.medido_anos_parecidos_kg_ha || {})).join(", ");
  return `<div class="seg-regua">
    <div class="seg-regua-ano a27"><span class="seg-ano-n">2027</span><div><b>o mar mais quente de ago–out desde 1950</b>
      <span>comparado com ${n || "os"} anos parecidos${anosEN ? ` (${U.esc(anosEN)})` : ""}</span></div>${U.selo("projecao", base27)}</div>
    <div class="seg-regua-ano"><span class="seg-ano-n">2028</span><div><b>sem previsão do mar</b><span>vale o normal daqui (1998–2025)</span></div>${U.selo("projecao", base28)}</div>
    <div class="seg-regua-ano"><span class="seg-ano-n">2029</span><div><b>sem previsão do mar</b><span>igual a 2028</span></div>${U.selo("projecao", base28)}</div>
  </div>`;
}

function colunaAno(U, d, ano, cics) {
  const k = d.c, a = d.anos[String(ano)];
  if (!a) return `<div class="seg-col fora"><div class="seg-col-ano">${ano}</div><p class="sub">sem projeção</p></div>`;
  const noPlano = cics.length > 0;
  const partes = [...new Set(cics.map((c) => c.parte.replace("Parte ", "")))];
  const col = cics.find((c) => c.colhe)?.colhe;
  const onde = noPlano ? `${partes.join(" e ")}${col ? ` · colhe ${col.txt}` : ""}` : `não plantado em ${ano}`;
  const sem = a.kg.p20 < PISO_KG[k];
  const piso = sem
    ? `<div class="seg-piso sem"><span class="seg-piso-rot">&nbsp;</span><span class="seg-piso-val">sem piso</span><span class="seg-piso-sub">em 2 de 10 anos parecidos, quase nada</span></div>`
    : `<div class="seg-piso"><span class="seg-piso-rot">pelo menos</span><span class="seg-piso-val">${fmtUn(U, a.q.p20)}<small>${UN_CURTA[k]}/ha</small></span>
       <span class="seg-piso-sub">em 8 de 10 anos parecidos</span></div>`;
  return `<div class="seg-col${noPlano ? "" : " fora"}">
    <div class="seg-col-ano">${ano}</div>
    <div class="seg-col-onde" title="${U.esc(col?.fonte || "")}">${U.esc(onde)}</div>
    ${piso}
    <div class="seg-col-q">${U.dezRocas(a.quebra, "var(--terra)", "roças quebram")}<span>quebra em <b>${freq(a.quebra).replace(" em ", " de ")}</b></span></div>
    <div class="seg-col-tip">típico ${fmtUn(U, a.q.p50)} · normal ${fmtUn(U, d.normal)}</div>
  </div>`;
}

function detalheCultura(U, r, ef, d, cics, eixo) {
  const k = d.c, un = UN[k];
  const linhas = ["2027", "2028", "2029"].filter((a) => d.anos[a]).map((a) => {
    const x = d.anos[a];
    const area = cics.filter((c) => String(c.ano) === a).reduce((s, c) => s + areaCiclo(ef, c), 0);
    return `<tr><td><b>${a}</b></td><td>${leque(x.q, d.normal, eixo, `${k} ${a}`)}</td>
      <td>${fmtUn(U, x.q.p10)}–${fmtUn(U, x.q.p90)}</td><td>${fmtUn(U, x.q.p50)}</td>
      <td>${x.rec ? U.brl(x.rec.p50) : "—"}${area > 0 && x.rec ? `<br><span class="sub">sua área (${U.ha(Math.round(area * 100) / 100)}): ${U.brl(x.rec.p50 * area)}</span>` : ""}</td>
      <td>${d.custo.semente > 0 ? freqPaga(x.nps) : "maniva sua"}</td><td>${freqPaga(x.npd)}</td></tr>`;
  }).join("");
  const rp = r.financeiro?.culturas?.Mandioca?.repete_ano_anterior_pct;
  return U.verMais(`${legendaLeque()}
    <div class="seg-tab-wrap"><table class="seg-tab"><thead><tr><th>ano</th><th>leque (${U.esc(un)})</th><th>8 em 10 entre</th><th>típico</th>
      <th>valor típico/ha</th><th>não paga a semente</th><th>não paga o custo todo</th></tr></thead><tbody>${linhas}</tbody></table></div>
    <ul class="seg-lista">
      ${d.tres != null ? `<li>Plantando ${U.esc(k.toLowerCase())} nos 3 anos, a chance de pelo menos 1 quebra é de ${freq(d.tres)} (supondo anos independentes; as quebras costumam vir juntas).</li>` : ""}
      <li>Quebra = colher menos da metade do normal (${fmtUn(U, d.normal / 2)} ${U.esc(un)}). "Pelo menos" = o que se colhe em 8 de 10 anos parecidos (P20, já alargado).</li>
      <li>Valor = colheita × R$ ${U.num(d.preco, 2)}/kg (R$ de 2025, vender ou comer)${d.precoTxt ? `, raiz a ${U.esc(d.precoTxt.origem)} como no passo "Quanto rende"` : ""}.
        Semente e custo todo: CONAB (${U.brl(d.custo.semente)} e ${U.brl(d.custo.desembolso)} por ha); o custo todo é de lavoura acima da média.
        A área de cada parte é suposição (partes iguais; baixio metade milho, metade caupi).</li>
      <li>Em 2027 o município pesa ${U.pct(d.p.peso_municipio_2027)} e a mesorregião (${U.esc(r.local.mesorregiao)}) o resto, porque só há ${d.n_en} anos parecidos.</li>
      ${k === "Feijão" ? "<li>O IBGE junta caupi e feijão comum no \"feijão\". Na seca o preço do feijão costuma subir (proteção parcial).</li>" : ""}
      ${k === "Mandioca" ? `<li>O IBGE repete o número do ano anterior em ${rp != null ? `${U.num(rp)}% dos anos aqui e em ` : ""}29% dos anos no Nordeste: o leque da mandioca parece mais seguro do que é. A mandioca plantada num ano é colhida no seguinte; o leque usa o ano do plantio.</li>` : ""}
      ${d.artefato ? `<li><b>Atenção:</b> o lado de cima de 2027 sai acima do de um ano qualquer. Isso é a produtividade subindo com os anos (2024 foi recorde), não o El Niño: não conte com ele.</li>` : ""}
    </ul>`, "Ver o leque e o dinheiro");
}

function cartaoCultura(U, r, ef, d, cics) {
  const k = d.c, tipo = SERIE.find(([n]) => n === k)[2];
  const a27 = d.anos["2027"];
  const usaDes = ef.custo === "desembolso" || !(d.custo.semente > 0);
  const pg = usaDes ? a27?.npd : a27?.nps;
  const ondes = [...new Set(cics.map((c) => c.parte))].join(" · ");
  return `<section class="painel seg-cult ${U.tipoCss(tipo)}">
    <div class="seg-cult-cab"><span class="bola">${U.ic(U.icCultura(k), "g")}</span>
      <div><h2>${U.esc(k)}${k === "Feijão" && cics.some((c) => /caupi/i.test(c.cultura)) ? " <span class=\"sub\">(caupi)</span>" : ""}</h2><span class="sub pequeno">${U.esc(ondes)}</span></div>
      ${U.selo("projecao", "anos parecidos do IBGE (PAM 1998–2025), município + mesorregião, alargado pelo teste com o passado")}</div>
    <div class="grade-3 seg-cols">${[2027, 2028, 2029].map((ano) => colunaAno(U, d, ano, cics.filter((c) => c.ano === ano))).join("")}</div>
    <div class="seg-cult-pe">
      <div class="seg-pe-medido"><div class="seg-pe-rot">Aqui, nos anos de mar assim ${U.selo("medido", "IBGE PAM, rendimento por ha plantado nos anos de El Niño forte")}</div>
        ${anosParecidos(d.medido, d.normal, UN[k])}<div class="seg-pe-leg"><i></i>normal ${fmtUn(U, d.normal)} ${U.esc(UN[k])}<b></b>quebra (menos da metade)</div></div>
      ${pg != null ? `<div class="seg-pe-rs" title="${U.esc(`valor = colheita × R$ ${U.num(d.preco, 2)}/kg; custo CONAB`)}">${U.ic("dinheiro", "g")}<p><b>2027:</b> ${fraseNaoPaga(pg, usaDes ? "o custo todo" : "a semente")}</p></div>` : ""}
    </div>
    ${detalheCultura(U, r, ef, d, cics, eixoCultura(d))}
  </section>`;
}

function semSerie(U, lista) {
  const nomes = [...new Set(lista.filter((c) => !serieDe(c.cultura)).map((c) => c.cultura))];
  if (!nomes.length) return "";
  return `<div class="seg-semserie">${nomes.map((n) => `<span class="chip">${U.ic(U.icCultura(n))}${U.esc(n)}</span>`).join("")}
    <span class="sub">sem série no município: sem projeção (valem pelo gado e pela palhada)</span></div>`;
}

function blocoQuadro(U, r, ef, culturas) {
  const f = r.financeiro, h = f?.historico_R_ha;
  if (!h?.anos) return "";
  const fortes = f.anos_el_nino_forte || [];
  const notas = [];
  const linhas = culturas.filter((c) => h[c] && f.culturas?.[c]?.custo_ha).map((c) => {
    const custo = f.culturas[c].custo_ha;
    const fator = c === "Mandioca" && f.precos_raiz ? ((f.precos_raiz[ef.raiz] ?? f.culturas[c].preco_kg) / (f.culturas[c].preco_kg || 1)) : 1;
    const R = h[c].map((v) => (v == null ? null : v * fator));
    const ok = R.filter((v) => v != null);
    const sem = ok.filter((v) => v >= custo.semente && v > 0).length, des = ok.filter((v) => v >= custo.desembolso).length;
    const viz = (h["origem_" + c] || []).filter((o) => o && o !== "mun").length;
    if (viz) notas.push(`${c}: ${viz} ano(s) sem dado do município foram completados pela mesorregião (quadrado apagado).`);
    if (fator !== 1) notas.push(`${c}: raiz ao preço escolhido no passo "Quanto rende".`);
    return `<div class="seg-quadro-linha"><div class="seg-quadro-rot">${U.ic(U.icCultura(c))}<b>${U.esc(c)}</b>
      <span>pagou a semente em <b>${sem} de ${ok.length}</b> · o custo todo em <b>${des}</b></span></div>
      ${quadro28(h.anos, R, h["origem_" + c], custo, fortes)}</div>`;
  });
  if (!linhas.length) return "";
  return `<div class="seg-quadro-cartao">
    <p class="kicker">28 anos que já aconteceram aqui ${U.selo("medido", `${f.base || "IBGE PAM 1998–2025; CONAB"} · ${f.moeda || "R$ de 2025"}`)}</p>
    <div class="seg-legenda-q"><span><i class="q-verde"></i>pagou o custo todo</span><span><i class="q-ambar"></i>só a semente</span>
      <span><i class="q-vermelho"></i>nem a semente</span><span><i class="q-forte-sw"></i>mar quente</span></div>
    ${linhas.join("")}
    <p class="pequeno sub">Valor da colheita de 1 ha (vender ou comer, a preço da região, R$ de 2025) contra o custo da CONAB
      (${U.esc(f.culturas?.Milho?.custo_ha?.origem || "custos do NE")}). Anos de mar quente (El Niño forte): ${fortes.join(", ")}.
      É o que já aconteceu, não uma previsão.</p>${notas.length ? `<ul class="seg-lista">${notas.map((n) => `<li>${U.esc(n)}</li>`).join("")}</ul>` : ""}
  </div>`;
}

/** Os portões (19/mar e 30/abr): as datas já estão na abertura; o método e o "seu olho" vão no ver mais do fim do passo. */
function blocoPortoes(U, r, dados) {
  const ag = r.agenda || {}, m = dados.Milho;
  const vale = ag.portoes !== false; // fora do sertão: em fração do normal, sem virar sacos do município
  const cab = vale
    ? `<h4>O que vamos olhar: 19/mar e 30/abr ${U.selo("medido", PORTOES.fonte)}</h4>`
    : `<h4>O que vamos olhar ${U.selo("suposicao", ag.nota_portoes || "as datas de troca foram medidas só no sertão de CE, RN, PB, PI e PE")}</h4>`;
  return `${cab}${olho(vale ? OLHOS.portoes : OLHOS.portoes_fora)}${vale ? "<p>A chuva que cair desde 1º de fevereiro diz qual ano é este.</p>" : ""}<p>${U.esc(PORTOES.fonte)}. Quebra do milho em 30/abr (chuva de fev a abr): ${PORTOES.linhas.map((l) => `${l.nome.toLowerCase()} ${freq(l.q_abr)}`).join("; ")};
      milho típico: ${PORTOES.linhas.map((l) => `${l.nome.toLowerCase()} ${U.num(l.p50 * 100)}% do normal`).join("; ")}.
      Em 19/mar (chuva de fev a meados de mar) já se separa: ${PORTOES.linhas.map((l) => freq(l.q_mar)).join(", ")}. Hoje, só com o mar,
      ${m ? `a quebra do milho daqui é ${freq(m.anos["2027"]?.quebra)}` : "a conta é a do clima"}. No feijão, a quebra vai de 5 em 10 (chuva fraca) a menos de 1 em 10
      (chuva boa). Os portões são decêndios do ZARC; a conta usa meses inteiros (fev–mar e fev–abr), então é aproximação.
      ${vale ? "No litoral leste o satélite capta pouca chuva: lá a tabela não vale." : U.esc(ag.nota_portoes || "")}</p>`;
}

/** "E se chover…" (os 3 cartões fixos de chuva fraca, no meio e boa viraram este controle, com a mesma quebra) e, no ver mais, cada ano. */
function blocoCenario(U, agro) {
  return `<section class="seg-bloco">
    ${U.extra("cenario_chuva", { partes: ["cenario"], agro })}
  </section>`;
}

/** Os 7 jeitos testados, em barras de "acerto em 100" (ponto 4: comparar abordagens). */
function metodos(U) {
  return `<h4>Testamos 7 jeitos de ler o passado ${U.selo("medido", "analise/projecao.md, seção 3: teste só com o passado (walk-forward 2008–2025), 1.783 municípios; média por ano da cobertura da faixa de 8 em 10")}</h4>
    <p>Ficou o que mais acertou. A regressão por quantis falhou no milho: 26 em 100.</p>
    <div class="seg-metodos" role="list">${METODOS.map(([k, rot, v]) => `<div class="seg-met${k === "F" ? " on" : ""}" role="listitem">
      <span class="seg-met-rot">${U.esc(rot)}</span><span class="seg-met-trilho"><i style="width:${v}%"></i><b class="seg-met-meta" title="meta: 80"></b></span>
      <span class="seg-met-val">${v}</span></div>`).join("")}</div>
    <p class="pequeno sub">Acerto em 100 casos: o ano real caiu dentro da faixa de 8 em 10 (meta: 80, o risco). Nesta 1ª rodada o escolhido deu 78;
      refeito com a definição única de El Niño, deu ${U.num(CALIB.wf_media * 100)}.</p>`;
}

// o "ver mais" do acerto tem id: o link "Quanto o cálculo já acertou" de Do espaço abre ele e rola até ele (roca.js, data-acerto)
function blocoLimites(U, portoes) {
  return `<section class="seg-bloco seg-limites">
    ${U.verMais(U.extra("cenario_chuva", { partes: ["sobreposicao"] }), "Ver cada ano: chuva, solo e colheita")}
    ${U.verMais(`${portoes}<h4>O que não dá para projetar</h4>
      <ul class="seg-lista">${NAO_PROJETA.map(([t, d]) => `<li><b>${U.esc(t)}</b>: ${U.esc(d)}</li>`).join("")}</ul>
      <h4>Quanto já acertou</h4>
      <p>Num teste feito só com o passado (cada ano de 2008 a 2025 projetado com os anos anteriores; milho, feijão e mandioca; municípios
      com 20 anos ou mais de série):</p>
      <ul class="seg-lista">
        <li>o ano real caiu dentro da faixa de "8 em 10" em <b>${U.num(CALIB.wf_media * 100)} de 100</b> casos (meta 80); no pior ano, ${U.num(CALIB.wf_pior * 100)} de 100;</li>
        <li>o "pelo menos X em 8 de 10" se sustentou em <b>${U.num(CALIB.wf_en_piso * 100)} de 100</b> casos nos El Niños fortes de 2010, 2016 e 2024 (meta 80);</li>
        <li>a faixa inteira acertou ${U.num(CALIB.wf_en_cob * 100)} de 100 nesses anos: o lado de cima erra mais que o de baixo;</li>
        <li>nos El Niños fortes previu quebra em ${U.pct(CALIB.wf_en_prev)} dos casos e aconteceu em ${U.pct(CALIB.wf_en_obs)} (erra para o lado do cuidado);
          mas os anos parecidos discordam: no milho, ${CALIB.milho.map(([a, p, o]) => `${a} previu ${U.pct(p)}, aconteceu ${U.pct(o)}`).join("; ")}.</li>
      </ul>
      <p>Método "C + D + conforme": quantis do município encolhidos para a mesorregião (peso n/(n+10)); 2027 só com os anos de El Niño forte
      (ONI out–dez/nov–jan ≥ 1,5: 1998, 2010, 2016, 2024); depois o leque é alargado pelo que faltou no teste. Os fatores foram calibrados
      nos mesmos dados, então o acerto real tende a ser um pouco menor. Fonte: ${U.esc(CALIB.fonte)}.</p>
      ${metodos(U)}`, "Ver como medimos e quanto já acertou").replace('<details class="ver-mais">', '<details class="ver-mais" id="seg-acerto">')}
  </section>`;
}

export default {
  id: "seguranca",
  titulo: "Se secar",
  async render(el, ctx) {
    const U = ctx.util, r = ctx.r, ef = ctx.ef;
    const lista = ciclos(U, r);
    const nomes = new Set(lista.map((c) => serieDe(c.cultura)).filter(Boolean));
    const ordem = SERIE.map(([k]) => k).filter((k) => nomes.has(k));
    const dados = Object.fromEntries(ordem.map((k) => [k, cultura(r, ef, k)]).filter(([, d]) => d));
    const cartoes = Object.values(dados).map((d) => cartaoCultura(U, r, ef, d, lista.filter((c) => serieDe(c.cultura) === d.c))).join("");
    // lavoura grande no IBGE (mesma regra do passo 4): os sacos/ha não são de roça de família
    const agro = ["Milho", "Feijão", "Mandioca"].filter((c) => r.financeiro?.culturas?.[c]?.rend_mediano_kg_ha > 2 * CONAB_FAMILIAR_KG_HA[c]);
    const avisoAgro = agro.length ? `<div class="painel alerta seg-agro">${U.faixa("alerta", "terra", "Aqui o IBGE mistura lavoura grande: os sacos/ha não são de roça de família.")}
      ${olho(OLHOS.agro)}</div>` : "";
    el.innerHTML = `${abertura(U, r, dados)}
      ${bloco2027(U, r, dados, lista, cartoes, avisoAgro, blocoQuadro(U, r, ef, ordem.length ? ordem : ["Milho", "Feijão", "Mandioca"]), blocoHoje(U, r))}
      ${blocoCenario(U, agro.length > 0)}
      <section class="seg-bloco">${U.extra("historico", { modo: "memoria" })}</section>
      ${U.extra("leve_ao_tecnico")}
      ${blocoLimites(U, blocoPortoes(U, r, dados))}`;
    await U.montarExtras(el, ctx);
  },
};
