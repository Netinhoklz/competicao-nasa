// Passo 5, "Segurança": o que já se sabe hoje e, para cada colheita do plano, o leque do que pode vir (2027 com o El Niño medido;
// 2028–29 só com o clima). Método: analise/projecao.md ("C + D + conforme"); dados: ctx.r.projecao (dados/projecao_mun.json),
// ctx.r.financeiro (dados/financeiro_mun.json); calibração: dados/projecao_metricas.txt. Projeção = anos parecidos, nunca previsão.
import { leque, legendaLeque, eixoBom, grade10, anosParecidos, quadro28, cenarios } from "./seguranca/graficos.js";

const SERIE = [["Milho", /^milho/i], ["Feijão", /^feij/i], ["Mandioca", /^mandioca/i]];
const serieDe = (nome) => (SERIE.find(([, re]) => re.test(nome || "")) || [null])[0];
const UN = { Milho: "sacos/ha", Feijão: "sacos/ha", Mandioca: "t/ha" };
const UN_CURTA = { Milho: "sc", Feijão: "sc", Mandioca: "t" };
const emUn = (c, kg) => (kg == null ? null : c === "Mandioca" ? kg / 1000 : kg / 60);
const PISO_KG = { Milho: 30, Feijão: 30, Mandioca: 500 }; // abaixo disso (meio saco; meia tonelada) o "piso" é quase nada

// Backtest novo: dados/projecao_metricas.txt (gerado 2026-11-14 18:24 por ferramentas/preparar_projecao.py), coluna DEPOIS
// (definição única de El Niño forte: 1998, 2010, 2016, 2024). WF = walk-forward 2008–2025, só com o passado.
const CALIB = {
  fonte: "dados/projecao_metricas.txt (gerado 14/11/2026 18:24), bloco 'Resumo: antes × depois', coluna DEPOIS",
  wf_media: 0.793, wf_pior: 0.622, wf_en_cob: 0.675, wf_en_piso: 0.843, wf_en_prev: 0.34, wf_en_obs: 0.25,
  milho: [["2010", 0.57, 0.38], ["2016", 0.42, 0.49], ["2024", 0.48, 0.11]], // WF, milho, quebra prevista × observada (F_final)
};
// Portões (analise/projecao.md, seção 4 e achados; portoes_precos.py): milho no semiárido de CE, RN, PB, PI e PE, 1998–2025,
// razão ao normal do município por classe da chuva IMERG desde 1/fev (meses inteiros: fev–mar ≈ 19/mar, fev–abr ≈ 30/abr).
const PORTOES = {
  fonte: "analise/projecao.md, seção 4 (portoes_precos.py): milho no semiárido de CE, RN, PB, PI e PE, 23.704 município-anos, 1998–2025",
  clima: { p50: 1.0, q: 0.28 },
  linhas: [
    { rotulo: "abaixo de 75% do normal", cls: "c-seco", p50: 0.33, q_abr: 0.60, q_mar: 0.54 },
    { rotulo: "entre 75% e 100%", cls: "c-meio", p50: 0.72, q_abr: 0.37, q_mar: 0.33 },
    { rotulo: "100% ou mais", cls: "c-bom", p50: 1.36, q_abr: 0.10, q_mar: 0.13 },
  ],
};
const NAO_PROJETA = [
  ["Secas de vários anos, como a de 2012–15", "vêm sem aviso do oceano; nesses anos o leque acertou só 6 a 7 em 10."],
  ["A roça da sua família", "o IBGE dá a média do município; uma roça sozinha varia mais que a média."],
  ["A mandioca ano a ano", "o IBGE repete o número do ano anterior em muitos municípios; o leque dela parece mais seguro do que é."],
  ["Sorgo, palma, gliricídia e guandu", "não têm série no município; o caupi entra no \"feijão\" do IBGE, que junta caupi e feijão comum."],
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
/** Frase do dinheiro (vem depois de "2027:"): "em 5 de 10 anos parecidos, a colheita não paga a semente." */
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

const fmtUn = (U, c, v) => (v === null || v === undefined ? "—" : U.num(v, v > 0 && v < 10 ? 1 : 0));

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
  const sup = k !== 0 || /supos/i.test(l.colher);
  const fonte = (k !== 0 ? `datas de ${ano} iguais às de ${l.estacao} (ZARC 2026/27 repetido). ` : "") + `${l.colher}. ${l.fonte || ""}`;
  return { txt, sup, fonte, ano_colhe: b.a };
}

/** Ciclos do plano: uma linha por parte e ano, mais o caupi em revezamento no milho em pé quando o plano diz. */
function ciclos(U, r) {
  const pl = r.plano, lin = r.agenda?.linhas || [];
  if (!pl?.faixas) return [];
  const out = [];
  for (const f of pl.faixas) {
    pl.anos.forEach((ano, i) => {
      const a = f.anos[i];
      if (!a) return;
      const perene = a.tipo === "perene" && i > 0;
      out.push({ parte: f.parte, ano, cultura: a.cultura, tipo: a.tipo, texto: a.texto, perene,
        colhe: perene ? null : colheita(U, lin, f.parte, a.cultura, ano) });
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
  const medKey = Object.keys(p).find((k) => /^mediana/.test(k));
  const normalKg = p[medKey];
  let fator = 1, precoTxt = null;
  const fin = r.financeiro;
  if (c === "Mandioca" && fin?.precos_raiz && p.preco_r2025_kg > 0) {
    const pr = fin.precos_raiz[ef.raiz] ?? fin.precos_raiz[fin.precos_raiz.padrao];
    if (pr > 0) {
      fator = pr / p.preco_r2025_kg;
      precoTxt = { preco: pr, origem: { municipio: "o preço daqui", uf_mediana: `a mediana do ${r.local.uf}`, uf_p25: `o preço baixo do ${r.local.uf}` }[ef.raiz] || "a referência" };
    }
  }
  const custo = p.custo_r2025_ha || fin?.culturas?.[c]?.custo_ha || {};
  const anos = {};
  for (const [a, d] of Object.entries(p.anos)) {
    const kg = d.kg_ha;
    const q = Object.fromEntries(Object.entries(kg).map(([k, v]) => [k, emUn(c, v)]));
    const rec = d.receita_r2025_ha ? Object.fromEntries(Object.entries(d.receita_r2025_ha).map(([k, v]) => [k, v * fator])) : null;
    const nps = custo.semente > 0 ? (fator === 1 && d.chance_nao_paga_semente != null ? d.chance_nao_paga_semente : rec ? chanceAbaixo(rec, custo.semente) : null) : null;
    const npd = custo.desembolso > 0 ? (fator === 1 && d.chance_nao_paga_desembolso != null ? d.chance_nao_paga_desembolso : rec ? chanceAbaixo(rec, custo.desembolso) : null) : null;
    anos[a] = { q, kg, quebra: d.chance_quebra, rec, nps, npd, base: d.base || "" };
  }
  const medido = Object.entries(p.medido_anos_parecidos_kg_ha || {}).map(([a, v]) => [a, emUn(c, v)]);
  return { c, p, normal: emUn(c, normalKg), normalKg, anos, medido, custo, fator, precoTxt,
    n_en: p.n_anos_el_nino_forte ?? medido.length, tres: p.chance_ao_menos_1_quebra_2027_2029,
    preco: (p.preco_r2025_kg || 0) * fator, artefato: anos["2027"] && anos["2028"] && anos["2027"].q.p90 > 1.3 * anos["2028"].q.p90 };
}

/** Eixo comum de uma cultura (o mesmo nos 3 anos, para o leque de 2027 e o de 2028 serem comparáveis). */
function eixoCultura(d) {
  const p90 = Math.max(...Object.values(d.anos).map((a) => a.q.p90 || 0));
  return eixoBom(Math.max(d.normal * 1.5, Math.min(p90, d.normal * 2.5)));
}

// ---------------------------------------------------------------------------------------------------------------------------
function blocoHoje(U, r) {
  const e = r.este_ano || {}, u = r.el_nino_uf;
  let estado = "";
  if (u && u.pct_terco_seco && u.media != null) {
    const anos = u.anos || Object.keys(u.pct_terco_seco);
    estado = `<li class="seg-hoje-uf"><span class="seg-n">${U.num(u.media / 10)} em 10</span>
      <div>municípios do ${U.esc(u.uf)} tiveram a estação no <b>terço mais seco</b> nos anos de El Niño forte (média dos anos com dado);
      o acaso daria ${U.num((u.acaso_pct ?? 33) / 10)} em 10. ${U.selo("medido", (u.definicao || "") + (u.n_mun ? ` · ${u.n_mun} municípios` : ""))}
      <div class="seg-uf-anos">${anos.map((a) => { const v = u.pct_terco_seco[a];
        return `<span>${U.esc(a)}: ${v == null ? "sem dado (o satélite começa em jan/1998)" : `<b>${U.num(v / 10)} em 10</b>`}</span>`; }).join("")}</div>
      <span class="sub pequeno">Os anos discordam entre si: por isso é chance, não certeza.</span></div></li>`;
  } else {
    estado = `<li class="sub">A conta do estado (em quantos municípios do ${U.esc(r.local.uf)} a estação ficou no terço mais seco nos El Niños fortes) ainda não foi gerada para este site.</li>`;
  }
  const sabe = [
    `<li class="seg-hoje-oni"><span class="seg-n">${e.oni > 0 ? "+" : ""}${U.num(e.oni, 2)}</span><div><b>O oceano já está quente.</b> ${U.esc(e.texto_oni || "")} ${U.selo("medido", "NOAA/CPC ONI, ago–out/2026")}</div></li>`,
    estado,
    e.perspectiva ? `<li><span class="seg-ico">⌂</span><div><b>Aqui, nos anos fortes</b> (o que aconteceu, não é previsão): ${U.esc(e.perspectiva)} ${U.selo("medido", "GPM IMERG, chuva da estação nos El Niños fortes da série")}</div></li>` : "",
    e.smap?.status === "ok" ? `<li><span class="seg-ico">▤</span><div><b>O solo agora:</b> ${U.esc(e.smap.texto)} ${U.selo("medido", "NASA SMAP L4, 30 dias até " + U.dataBR(e.smap.fim))}</div></li>` : "",
  ].filter(Boolean);
  const reg = e.regime;
  const naoSabe = [
    reg && reg.quadra === false
      ? `<b>Como vai chover na estação daqui</b> (${U.esc(reg.estacao)}): o El Niño é só uma parte da história, e nenhum modelo sabe o resto em novembro.`
      : "<b>O Atlântico de fevereiro a abril</b>, que decide boa parte da quadra. Nenhum modelo sabe isso em novembro.",
    "<b>A chuva de 2027</b> aqui: o El Niño puxa para menos, mas os anos fortes discordam entre si (2024 foi forte e a quadra do CE foi normal).",
    "<b>O clima de 2028 e 2029</b>: o oceano não avisa com tanta antecedência.",
    "<b>O preço</b> que o milho, o feijão e a raiz vão ter.",
  ];
  return `<div class="cartao seg-hoje">
    <div class="seg-hoje-col seg-sabe"><h3>Hoje: o que já se sabe ${U.selo("medido", "dados de hoje: ONI, IMERG, SMAP")}</h3><ul>${sabe.join("")}</ul></div>
    <div class="seg-hoje-col seg-naosabe"><h3>O que ainda não se sabe</h3><ul>${naoSabe.map((s) => `<li><span class="seg-ico">?</span><div>${s}</div></li>`).join("")}</ul></div>
  </div>`;
}

function linhaCiclo(U, r, ef, c, dados, eixos) {
  const tc = U.tipoCss(c.tipo);
  const k = serieDe(c.cultura);
  const d = k ? dados[k] : null;
  const pousio = c.tipo === "pousio" || /pousio/i.test(c.cultura);
  const mes = pousio ? `<span class="seg-mes">a terra descansa: não se colhe</span>`
    : c.perene ? `<span class="seg-mes">${U.esc(c.texto || "segue no chão")}</span>`
    : c.colhe ? `<span class="seg-mes">colhe <b>${U.esc(c.colhe.txt)}</b> ${U.selo(c.colhe.sup ? "suposicao" : "medido", c.colhe.fonte)}</span>`
      : `<span class="seg-mes sub">mês da colheita sem data na agenda</span>`;
  const cab = `<div class="seg-ciclo-cab ${tc}">
      <span class="seg-parte">${U.esc(c.parte.replace("Parte ", ""))}</span>
      <div><b class="seg-cult">${U.esc(c.cultura)}</b>${mes}</div></div>`;
  if (pousio) return `<div class="seg-ciclo sem">${cab}<div class="seg-ciclo-sem">pousio: nada para projetar</div><div></div></div>`;
  if (!d) {
    const motivo = k && !r.projecao ? "sem projeção para este município (série curta no IBGE)" : "sem série no município: sem projeção";
    return `<div class="seg-ciclo sem">${cab}<div class="seg-ciclo-sem">${U.esc(motivo)}${c.tipo === "forragem" || c.tipo === "perene" ? " · vale pelo gado, não pela venda" : ""}</div><div></div></div>`;
  }
  const a = d.anos[String(c.ano)];
  if (!a) return `<div class="seg-ciclo sem">${cab}<div class="seg-ciclo-sem">sem projeção para ${c.ano}</div><div></div></div>`;
  const un = UN[k];
  const area = areaCiclo(ef, c);
  const dinheiro = a.rec && area > 0
    ? `<div class="seg-ciclo-rs">sua parte (${U.ha(Math.round(area * 100) / 100)}): típico <b>${U.brl(a.rec.p50 * area)}</b> ${U.selo("suposicao", `valor da colheita (vender ou comer) = rendimento típico × ${U.num(d.preco, 2)} R$/kg (R$ de 2025) × área; área: partes iguais, baixio metade milho e metade caupi, bordas fora (suposição, como no passo "Quanto rende")`)}</div>` : "";
  const rot = `${c.cultura}, ${c.ano}: P10 ${fmtUn(U, k, a.q.p10)}, P20 ${fmtUn(U, k, a.q.p20)}, típico ${fmtUn(U, k, a.q.p50)}, P80 ${fmtUn(U, k, a.q.p80)}, P90 ${fmtUn(U, k, a.q.p90)} ${un}; normal ${fmtUn(U, k, d.normal)}`;
  return `<div class="seg-ciclo">${cab}
    <div class="seg-ciclo-leque">${leque(a.q, d.normal, eixos[k], rot)}<div class="seg-ciclo-un">${U.esc(un)}</div></div>
    <div class="seg-ciclo-num">
      <div>típico <b>${fmtUn(U, k, a.q.p50)} ${U.esc(un)}</b> ${U.selo("projecao", a.base)}</div>
      <div>quebra: <b>${freq(a.quebra)}</b> anos parecidos</div>
      ${dinheiro}
    </div></div>`;
}

function blocoCiclos(U, r, ef, lista, dados) {
  const eixos = Object.fromEntries(Object.values(dados).map((d) => [d.c, eixoCultura(d)]));
  const anos = r.plano?.anos || [2027, 2028, 2029];
  const base27 = Object.values(dados)[0]?.anos["2027"]?.base || "";
  const recorde = base27.match(/maior ago–out da série \(([+−-]?\d+(?:,\d+)?)/);
  const d0 = Object.values(dados)[0];
  const n = d0?.n_en ?? r.financeiro?.anos_el_nino_forte?.length;
  const oni = r.este_ano?.oni;
  const selos = {
    2027: `<span class="seg-aviso-ano">oceano acima do recorde${oni != null ? ` (+${U.num(oni, 2)}${recorde ? ` contra ${recorde[1]}` : ""})` : ""}: extrapolação${n ? `; ${n} anos parecidos` : ""}</span>`,
    2028: `<span class="seg-aviso-ano clima">só clima, sem previsão do oceano</span>`,
    2029: `<span class="seg-aviso-ano clima">só clima, sem previsão do oceano</span>`,
  };
  const frase = {
    2027: "A estação de 2027 já tem um sinal medido: El Niño muito forte. O leque usa só os anos em que o mar estava assim.",
    2028: "Para 2028 ainda não há sinal nenhum: vale a história inteira de 1998 a 2025. Por isso o leque é mais largo e não muda de lugar.",
    2029: "Igual a 2028: só o clima. O ano depois de um El Niño não tem padrão firme (depois de 2010 veio 2012, o pior ano da série).",
  };
  const blocos = anos.map((ano) => {
    const linhas = lista.filter((c) => c.ano === ano);
    return `<section class="seg-ano seg-ano-${ano}">
      <div class="seg-ano-cab"><span class="seg-ano-n">${ano}</span><div>${selos[ano] || selos[2028]}<p>${U.esc(frase[ano] || frase[2029])}</p></div></div>
      ${linhas.map((c) => linhaCiclo(U, r, ef, c, dados, eixos)).join("")}
    </section>`;
  }).join("");
  const mand = lista.some((c) => serieDe(c.cultura) === "Mandioca" && c.colhe && c.colhe.ano_colhe > c.ano);
  return `<div class="cartao seg-ciclos">
    <h2>Cada colheita do plano</h2>
    <p class="sub">Uma linha por parte do roçado e por ano. O leque mostra o que a roça do município colheu nos anos parecidos; o mesmo eixo vale para os três anos de cada cultura, para dar para comparar.</p>
    ${legendaLeque()}
    ${blocos}
    <details><summary>Como o leque é feito</summary>
      <p>Para cada cultura, a colheita por ha plantado do IBGE (PAM 1998–2025) é dividida pelo normal do município (a mediana). Os quantis dessa razão
      no município são misturados com os da mesorregião (${U.esc(r.local.mesorregiao)}), com peso do município n/(n+10)${d0 ? `: em 2027,
      ${U.pct(d0.p.peso_municipio_2027)} do município (só ${n} anos parecidos); em 2028–29, ${U.pct(d0.p.peso_municipio_clima)}` : ""}.
      Em 2027 entram só os anos de El Niño forte (${U.esc(base27)}). Depois o leque é alargado pelo que o teste com o passado mostrou que faltava
      (alargamento conforme). Quebra = colher menos da metade do normal.</p>
      ${mand ? `<p>A mandioca plantada num ano é colhida no ano seguinte. O leque usa o ano da estação de plantio, que é quando a seca pega a planta pequena.</p>` : ""}
      <p>As datas de 2028 e 2029 repetem os meses de 2027 (o ZARC de 2027/28 ainda não saiu). O dinheiro de cada linha é o valor da colheita (vender ou
      comer, a preço da região), não lucro.</p>
    </details>
  </div>`;
}

function cartaoCultura(U, r, ef, d, ondes) {
  const k = d.c, un = UN[k], a27 = d.anos["2027"], a28 = d.anos["2028"];
  const mun = r.local.municipio, nome = k === "Feijão" ? "o feijão" : k === "Milho" ? "o milho" : "a mandioca";
  const vals = d.medido.map(([, v]) => v).filter((v) => v != null);
  const anosTxt = d.medido.map(([a]) => a);
  const lista = anosTxt.length > 1 ? anosTxt.slice(0, -1).join(", ") + " e " + anosTxt.at(-1) : anosTxt.join("");
  const piso = (a, rotulo) => {
    if (!a) return "";
    const sem = a.kg.p20 < PISO_KG[k];
    return sem ? `<p class="seg-piso sem"><b>${rotulo}: não há piso.</b> Em 2 de 10 anos parecidos não se colhe ${a.kg.p20 > 0 ? "quase " : ""}nada. ${U.selo("projecao", a.base)}</p>`
      : `<p class="seg-piso"><b>${rotulo}:</b> em 8 de 10 anos parecidos, a roça de ${U.esc(mun)} colhe pelo menos <b>${fmtUn(U, k, a.q.p20)} ${un}</b>. ${U.selo("projecao", a.base + " · P20 alargado")}</p>`;
  };
  const npsTxt = (a) => (d.custo.semente > 0 ? freqPaga(a?.nps) : "a maniva é sua");
  const linhaCusto = (rot, val, cls, f27, f28) => `<tr class="${cls}"><td>${rot} <span class="sub">(${val})</span></td><td><b>${f27}</b></td><td><b>${f28}</b></td></tr>`;
  const semente = d.custo.semente > 0 ? U.brl(d.custo.semente) + "/ha" : "R$ 0 na CONAB";
  const alertaMand = k === "Mandioca" ? (() => {
    const rp = r.financeiro?.culturas?.Mandioca?.repete_ano_anterior_pct;
    return `<p class="aviso">Mandioca: o IBGE repete o número do ano anterior em ${rp != null ? `${U.num(rp)}% dos anos aqui e em` : ""} 29% dos anos no Nordeste. O leque dela parece mais estreito (mais "seguro") do que é. ${U.selo("medido", "IBGE PAM; analise/projecao.md")}</p>`;
  })() : "";
  return `<div class="cartao seg-cult-cartao">
    <div class="seg-cult-cab"><h2>${U.esc(k)}</h2><span class="sub">no plano: ${U.esc(ondes.join(" · "))}</span></div>
    <div class="seg-cult-grade">
      <div>
        <h3>1 · O que já aconteceu aqui ${U.selo("medido", "IBGE PAM, rendimento por ha plantado")}</h3>
        <p>Nos ${d.medido.length} anos com o mar assim (${U.esc(lista)}), ${nome} de ${U.esc(mun)} colheu de <b>${fmtUn(U, k, Math.min(...vals))}</b> a
        <b>${fmtUn(U, k, Math.max(...vals))} ${un}</b>. O normal daqui é <b>${fmtUn(U, k, d.normal)}</b>.</p>
        ${anosParecidos(d.medido, d.normal, un)}
      </div>
      <div>
        <h3>2 · Em 10 roças ${U.selo("projecao", (a27?.base || "") + " · quebra = menos da metade do normal")}</h3>
        <div class="seg-grades">
          <figure>${grade10(a27?.quebra, `2027: ${freq(a27?.quebra)} roças quebram`)}<figcaption><b>2027:</b> a roça de ${U.esc(k.toLowerCase())} do município quebra em <b>${freq(a27?.quebra)}</b> anos parecidos</figcaption></figure>
          <figure>${grade10(a28?.quebra, `2028 e 2029: ${freq(a28?.quebra)}`)}<figcaption><b>2028 e 2029:</b> num ano qualquer, quebra em <b>${freq(a28?.quebra)}</b></figcaption></figure>
        </div>
        <p class="sub pequeno">Quebra = colher menos da metade do normal (${fmtUn(U, k, d.normal / 2)} ${un}).</p>
      </div>
      <div>
        <h3>3 · O piso</h3>
        ${piso(a27, "2027")}${piso(a28, "2028 e 2029")}
        ${d.tres != null ? `<p>Se plantar ${nome} nos 3 anos, a chance de pelo menos 1 quebra é de <b>${freq(d.tres)}</b>. ${U.selo("projecao", "1 − Π(1 − p), supondo anos independentes; nos blocos reais de 3 anos as quebras se agrupam (0,50 contra 0,58)")}</p>` : ""}
      </div>
      <div>
        <h3>4 · E o dinheiro ${U.selo("projecao", `valor = rendimento × ${U.num(d.preco, 2)} R$/kg (R$ de 2025); custo: CONAB (medido)`)}</h3>
        ${a27?.rec ? `<p>Valor da colheita por ha em 2027: típico <b>${U.brl(a27.rec.p50)}</b>; ${a27.kg.p20 < PISO_KG[k] ? "em 2 de 10 anos parecidos, quase nada" : `em 8 de 10 anos parecidos, pelo menos <b>${U.brl(a27.rec.p20)}</b>`}.</p>` : ""}
        ${d.custo.semente > 0 && a27?.nps != null ? `<p class="seg-frase-rs">2027: ${fraseNaoPaga(a27.nps, "a semente")}</p>`
          : a27?.npd != null ? `<p class="seg-frase-rs">2027: ${fraseNaoPaga(a27.npd, "o desembolso da CONAB")}</p>` : ""}
        <table class="seg-tab-rs"><thead><tr><th>não paga…</th><th>2027</th><th>2028–29</th></tr></thead><tbody>
          ${linhaCusto("a semente", semente, ef.custo === "semente" ? "atual" : "", npsTxt(a27), npsTxt(a28))}
          ${linhaCusto("o desembolso da CONAB", U.brl(d.custo.desembolso) + "/ha", ef.custo === "desembolso" ? "atual" : "", freqPaga(a27?.npd), freqPaga(a28?.npd))}
        </tbody></table>
        <p class="sub pequeno">${d.precoTxt ? `Raiz a R$ ${U.num(d.precoTxt.preco, 2)}/kg (${U.esc(d.precoTxt.origem)}), como no passo "Quanto rende". ` : ""}
        O desembolso da CONAB é de lavoura acima da média; a semente é a primeira conta que importa. ${k === "Feijão" ? "Na seca o preço do feijão costuma subir (proteção parcial)." : ""}</p>
      </div>
    </div>
    ${alertaMand}
    ${d.artefato ? `<p class="aviso">O lado de cima do leque de 2027 (P90 ${fmtUn(U, k, a27.q.p90)}) sai acima do de um ano qualquer. Isso é a produtividade subindo com os anos (2024 foi recorde), não o El Niño: não conte com ele.</p>` : ""}
  </div>`;
}

function blocoQuadro(U, r, ef, culturas) {
  const f = r.financeiro, h = f?.historico_R_ha;
  if (!h?.anos) return `<div class="cartao"><h2>Os 28 anos que já aconteceram aqui</h2><p class="sub">O IBGE não tem série suficiente deste município (pelo menos 10 anos com 10 ha plantados).</p></div>`;
  const fortes = f.anos_el_nino_forte || [];
  const linhas = culturas.filter((c) => h[c] && f.culturas?.[c]?.custo_ha).map((c) => {
    const custo = f.culturas[c].custo_ha;
    const fator = c === "Mandioca" && f.precos_raiz ? ((f.precos_raiz[ef.raiz] ?? f.culturas[c].preco_kg) / (f.culturas[c].preco_kg || 1)) : 1;
    const R = h[c].map((v) => (v == null ? null : v * fator));
    const ok = R.filter((v) => v != null);
    const des = ok.filter((v) => v >= custo.desembolso).length, sem = ok.filter((v) => v >= custo.semente && v > 0).length;
    const fn = h.anos.map((a, i) => [a, R[i]]).filter(([a, v]) => fortes.includes(a) && v != null);
    const fnSem = fn.filter(([, v]) => v >= custo.semente && v > 0).length;
    const viz = (h["origem_" + c] || []).filter((o) => o && o !== "mun").length;
    return `<div class="seg-quadro-linha">
      <div class="seg-quadro-rot"><b>${U.esc(c)}</b><span>pagou a semente em <b>${sem} de ${ok.length}</b> anos; o desembolso, em <b>${des}</b>.
        Nos ${fn.length} El Niños fortes: a semente em ${fnSem}.</span></div>
      ${quadro28(h.anos, R, h["origem_" + c], custo, fortes)}
      ${viz ? `<p class="sub pequeno">${viz} ano(s) sem dado do município foram completados pela mesorregião (quadrado mais claro).</p>` : ""}
      ${c === "Mandioca" && fator !== 1 ? `<p class="sub pequeno">Raiz ao preço escolhido no passo "Quanto rende".</p>` : ""}
    </div>`;
  });
  return `<div class="cartao seg-quadro-cartao">
    <h2>Os 28 anos que já aconteceram aqui ${U.selo("medido", `${f.base || "IBGE PAM 1998–2025; CONAB"} · ${f.moeda || "R$ de 2025"}`)}</h2>
    <p class="sub">Um quadrado por ano, de 1998 a 2025: o valor da colheita de 1 ha (vender ou comer, a preço da região) contra o custo da CONAB.</p>
    <div class="seg-legenda seg-legenda-q">
      <span><i class="sw q-verde"></i>pagou o desembolso</span><span><i class="sw q-ambar"></i>pagou só a semente</span>
      <span><i class="sw q-vermelho"></i>nem a semente</span><span><i class="sw q-forte-sw"></i>ano de El Niño forte (${fortes.join(", ")})</span>
    </div>
    ${linhas.join("") || `<p class="sub">Nenhuma cultura do plano com série aqui.</p>`}
    <p class="sub pequeno">Medido: é o que já aconteceu, não uma previsão. Custo da CONAB: ${U.esc(f.culturas?.Milho?.custo_ha?.origem || "custos do NE")}.</p>
  </div>`;
}

function blocoPortoes(U, r, dados) {
  const ag = r.agenda || {}, m = dados.Milho;
  const vale = ag.portoes !== false; // fora do sertão a tabela fica em fração do normal, sem virar sacos do município
  const normal = vale ? m?.normal : null, un = "sacos/ha";
  const a27 = m?.anos["2027"];
  const linhas = [
    ...(a27 ? [{ rotulo: "<b>hoje</b>, só com o oceano", cls: "c-hoje", p50: a27.kg.p50 / m.normalKg }] : []),
    ...PORTOES.linhas.map((l) => ({ ...l, rotulo: `em 30/abr, se a chuva desde 1/fev ficar <b>${l.rotulo}</b>` })),
  ];
  const marco = (re) => (ag.marcos || []).find((x) => re.test(x.rotulo || ""));
  const m19 = marco(/19\/mar/), m30 = marco(/30\/abr/);
  return `<div class="cartao seg-portoes">
    <h2>Como o leque de 2027 vai estreitar</h2>
    <p class="sub">Hoje só se sabe o oceano. A partir de fevereiro, a chuva que já caiu (satélite IMERG, da NASA) vai dizendo qual ano é este.
    É o que vamos olhar, e quando.</p>
    ${ag.portoes === false && ag.nota_portoes ? `<p class="aviso">${U.esc(ag.nota_portoes)} A tabela abaixo é do sertão e vale aqui só como ordem de grandeza.</p>` : ""}
    <ol class="seg-linha-tempo">
      <li><b>hoje</b><span>só o oceano: quebra do milho em ${freq(a27?.quebra)} ${U.selo("projecao", a27?.base || "")}</span></li>
      <li><b>19/mar</b><span>${m19 ? U.esc(m19.texto) + " " : ""}Com a chuva de fev a meados de mar, a quebra do milho já se separa:
        ${freq(PORTOES.linhas[0].q_mar)} se a chuva vier fraca, ${freq(PORTOES.linhas[2].q_mar)} se vier boa. ${U.selo("medido", PORTOES.fonte + " · fev–mar")}</span></li>
      <li><b>30/abr</b><span>${m30 ? U.esc(m30.texto) + " " : ""}Com a chuva de fev–abr, quase tudo está decidido. ${U.selo("medido", PORTOES.fonte + " · fev–abr")}</span></li>
    </ol>
    <h3>Milho ${normal ? `de ${U.esc(r.local.municipio)}: típico por cenário` : "do sertão: típico por cenário, em fração do normal"} ${U.selo("projecao", normal ? "razão ao normal do semiárido × normal do município" : PORTOES.fonte)}</h3>
    ${cenarios(linhas, normal, un)}
    <table class="seg-tab-portao"><thead><tr><th>chuva desde 1/fev</th><th>quebra do milho em 30/abr</th><th>em 19/mar</th></tr></thead><tbody>
      ${PORTOES.linhas.map((l) => `<tr class="${l.cls}"><td>${U.esc(l.rotulo)}</td><td><b>${freq(l.q_abr)}</b></td><td>${freq(l.q_mar)}</td></tr>`).join("")}
    </tbody></table>
    <details><summary>De onde vem a tabela</summary>
      <p>${U.esc(PORTOES.fonte)}. Em novembro, só com o clima, o típico é o normal e a quebra é ${freq(PORTOES.clima.q)}. No feijão, a quebra vai
      de 5 em 10 (chuva abaixo de 75%) a menos de 1 em 10 (acima de 100%). Os portões de 19/mar e 30/abr são decêndios do ZARC; aqui a conta usa
      meses inteiros (fev–mar e fev–abr), então é aproximação. ${ag.portoes === false ? "" : "No litoral leste o satélite capta pouca chuva: lá a tabela não vale."}</p>
    </details>
  </div>`;
}

function blocoLimites(U) {
  return `<div class="cartao seg-limites">
    <div class="grade-2">
      <div><h2>O que não dá para projetar</h2>
        <ul class="seg-nao">${NAO_PROJETA.map(([t, d]) => `<li><b>${U.esc(t)}</b>: ${U.esc(d)}</li>`).join("")}</ul></div>
      <div><h2>Quanto este leque já acertou ${U.selo("medido", CALIB.fonte)}</h2>
        <p>Num teste feito só com o passado (cada ano de 2008 a 2025 projetado com os anos anteriores, milho, feijão e mandioca, nos municípios
        com 20 anos ou mais de série):</p>
        <ul class="seg-calib">
          <li><span class="seg-n">${U.num(CALIB.wf_media * 100)} em 100</span><span>vezes o ano real caiu dentro da faixa clara (a meta é 80); no pior ano, ${U.num(CALIB.wf_pior * 100)} em 100.</span></li>
          <li><span class="seg-n">${U.num(CALIB.wf_en_piso * 100)} em 100</span><span>vezes o piso ("pelo menos X em 8 de 10") se sustentou nos El Niños fortes de 2010, 2016 e 2024 (a meta é 80).</span></li>
          <li><span class="seg-n">${U.num(CALIB.wf_en_cob * 100)} em 100</span><span>é o acerto da faixa inteira nesses mesmos anos: o lado de cima erra mais que o de baixo.</span></li>
        </ul>
        <p>Nos El Niños fortes, o método previu quebra em ${U.pct(CALIB.wf_en_prev)} dos casos e aconteceu em ${U.pct(CALIB.wf_en_obs)}: erra para o lado do cuidado.
        Mas os anos parecidos discordam muito entre si; no milho: ${CALIB.milho.map(([a, p, o]) => `${a} previu ${U.pct(p)}, aconteceu ${U.pct(o)}`).join("; ")}.</p>
        <details><summary>Detalhe do teste</summary>
          <p>Walk-forward 2008–2025, método "C + D + conforme" com a definição única de El Niño forte (ONI out–dez/nov–jan ≥ 1,5: 1998, 2010, 2016, 2024).
          Os fatores de alargamento foram calibrados nos mesmos dados, então o acerto real tende a ser um pouco menor. Os erros andam juntos dentro do
          mesmo ano: um ano como 2012 ou 2024 erra em muitos municípios ao mesmo tempo. Fonte: ${U.esc(CALIB.fonte)}.</p>
        </details>
      </div>
    </div>
  </div>`;
}

export default {
  id: "seguranca",
  titulo: "Segurança",
  render(el, ctx) {
    const U = ctx.util, r = ctx.r, ef = ctx.ef;
    const lista = ciclos(U, r);
    const nomes = [...new Set(lista.map((c) => serieDe(c.cultura)).filter(Boolean))];
    const ordem = SERIE.map(([k]) => k).filter((k) => nomes.includes(k));
    const dados = Object.fromEntries(ordem.map((k) => [k, cultura(r, ef, k)]).filter(([, d]) => d));
    const ondes = (k) => [...new Set(lista.filter((c) => serieDe(c.cultura) === k).map((c) => `${c.parte} ${c.ano}`))];
    const semProj = !r.projecao;
    el.innerHTML = `
      <div class="titulo-passo"><h1>Segurança: o que já se sabe e o que pode vir em cada colheita</h1>
        <p>Não é previsão. É o que a roça de ${U.esc(r.local.municipio)} colheu em anos parecidos com este, medido pelo IBGE desde 1998,
        e o quanto isso já acertou. Cada número tem um selo: ${U.selo("medido", "dado medido")} ${U.selo("suposicao", "suposição nossa")} ${U.selo("projecao", "projeção a partir dos anos parecidos")}.</p></div>
      ${blocoHoje(U, r)}
      ${semProj ? `<div class="aviso">A projeção por colheita ainda não está disponível para este município (o IBGE não tem série suficiente ou o dado ainda não foi gerado).</div>` : ""}
      ${r.plano ? blocoCiclos(U, r, ef, lista, dados) : `<div class="cartao"><p class="sub">Sem plano para este lugar: não há colheitas para projetar.</p></div>`}
      ${Object.values(dados).map((d) => cartaoCultura(U, r, ef, d, ondes(d.c))).join("")}
      ${blocoQuadro(U, r, ef, ordem.length ? ordem : ["Milho", "Feijão", "Mandioca"])}
      ${blocoPortoes(U, r, dados)}
      ${blocoLimites(U)}`;
  },
};
