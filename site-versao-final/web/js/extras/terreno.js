// QUADRA, extra "terreno": "Seu terreno em metros" (rodada 2, analise/fluxo2/BRIEFING.md, D4; agente C1, 15/11/2026).
// O roçado dele em escala (larg × comp das medidas de Sua roça; sem medidas, o quadrado da área, SUPOSIÇÃO), cada faixa com os
// metros e a cultura do ano, e por parte: carreiras, distância entre linhas e entre covas, sementes por cova e quanto material
// levar para aquela área; e um zoom de 5 × 5 m com as linhas e as covas no espaçamento certo. Geometria: montar() de
// passos/plantio/desenho.js. Espaçamento: dados/agronomia.json (seção 6 do briefing, do A1), com a fonte de cada cultura.
//
// API (as funções exportadas não mexem na página e rodam no node; só render() usa o DOM):
//   default { id: "terreno", render(el, ctx, { plano, ano }) }
//       plano: no formato de r.plano (padrão: ctx.r.plano); ano: índice em plano.anos (0, 1, 2) ou o próprio ano (2027).
//       Pode ser chamado de novo no mesmo el (outro ano ou outro plano): redesenha. Pede o próprio CSS (css/extras/terreno.css).
//   carregarAgronomia() → Promise<json | null>     (uma vez; null se o arquivo não carregar, e tenta de novo na próxima)
//   dadosCultura(agro, nome) → { nome, ...campos da seção 6 } | null    ("Palma" acha "Palma forrageira")
//   contas(lay, k, agro, plano?) → { linhas: [Linha], fontes: [texto] }   lay = montar(plano, ctx.ef); k = índice do ano
//       Linha = { id: "A"|"B"|"C"|"Baixio"|"Bordas", letra, parte, cultura, tipo, pousio, incerto, nFaixas, larguraM,
//                 comprimentoM, perimetroM (só Bordas), ha, itens: [Item] }
//       Item  = { cultura, dados, papel: "principal"|"entrelinhas"|"dentro"|"fora", nota, linhasPorFaixa, linhas,
//                 covasPorLinha, covas, entre_linhas_m, entre_covas_m, por_cova, material, unidade, quantidade }
//       quantidade: kg (unidade "kg") ou número de manivas/mudas/raquetes/estacas; null quando falta o dado (nunca inventa).
//   frases(U, linha) → { titulo, area, medida, leve, itens: [{ espacamento, material, porCova? }] }   (texto puro, sem HTML; leve =
//       o material da linha numa frase só, "≈ 2.110 manivas"; o relatório pode usar titulo + medida + itens)
//   qtdTxt(U, item), metros(U, m), dist(U, m), haTxt(U, ha), curto(cultura): os formatos do bloco ("≈ 2,6 kg", "16,7 m", "60 cm")
//   svgTerreno(U, lay, k, { W, Hmax, zoom, agro, plano }) → <svg> do roçado em escala (zoom = id da linha marcada com o quadrado de 5 m;
//       plano: a leguminosa do revezamento, como em contas)
//   svgZoom(U, linha, { W }) → <svg> do pedaço de 5 × 5 m (ou maior, para caju e banana) com linhas e covas
import { montar } from "../passos/plantio/desenho.js";

// ------------------------------------------------------------------ dados de agronomia (A1)
let AGRO = null;
const baixarAgro = () => fetch(new URL("../../dados/agronomia.json", import.meta.url)).then((r) => (r.ok ? r.json() : null)).catch(() => null);
export function carregarAgronomia() {
  // servidor ocupado: tenta de novo uma vez 400 ms depois (como o ideal.js); se falhar de novo, null e tenta na próxima chamada
  return (AGRO ||= baixarAgro().then((j) => j || new Promise((ok) => setTimeout(ok, 400)).then(baixarAgro))
    .then((j) => { if (!j) AGRO = null; return j; }));
}

const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").trim();
const num = (v) => (Number.isFinite(+v) && +v > 0 ? +v : null);

/** A cultura pelo nome do plano ("Palma" → "Palma forrageira", "gliricídia" → "Gliricídia"). */
export function dadosCultura(agro, nome) {
  const c = agro?.culturas || {}, n = norm(nome);
  if (!n) return null;
  const k = Object.keys(c).find((x) => norm(x) === n) || Object.keys(c).find((x) => norm(x).startsWith(n + " ") || norm(x).startsWith(n + "-"));
  return k ? { nome: k, ...c[k] } : null;
}

// ------------------------------------------------------------------ as contas (sem DOM)
const ehPousio = (c) => /pousio|descanso/i.test(c || "");
const separar = (c) => String(c || "").split(/\s*\+\s*/).filter(Boolean);

/** Um item plantado em nf faixas iguais de w metros (no sentido do comp) por L metros (o comprimento da carreira). Com lpf, o
 *  número de carreiras por faixa vem de fora (entre as carreiras de outra cultura; a cerca viva, 1 linha). */
function item(agro, nome, papel, { w = 0, L, nf = 1, lpf = null, nota = "", ecAqui = null, porCovaAqui = null, g100 = null }) {
  const d = dadosCultura(agro, nome);
  const el = num(d?.entre_linhas_m), ec0 = num(d?.entre_covas_m), ec = ecAqui || ec0;
  const base = { cultura: d?.nome || nome, dados: d, papel, nota, linhasPorFaixa: null, linhas: null, covasPorLinha: null, covas: null,
    entre_linhas_m: el, entre_covas_m: ec, por_cova: porCovaAqui || num(d?.por_cova) || 1, material: d?.material || "",
    unidade: d?.material_unidade || "", quantidade: null };
  // entre_linhas_m null (gliricídia) = uma carreira só, na cerca: com lpf dado (cerca, entre as carreiras) a conta não precisa dele
  if (!ec || (!el && lpf == null)) return base;
  lpf ??= Math.max(1, Math.floor(w / el + 1e-6)); // a 1ª carreira a meia distância da divisa
  const cpl = Math.max(1, Math.floor(L / ec + 1e-6));
  const linhas = nf * lpf, covas = linhas * cpl;
  // caupi no milho em pé: covas × sementes por cova × o peso de uma semente (o peso de 100 sementes da fonte)
  if (porCovaAqui && g100 && base.unidade === "kg") {
    return { ...base, linhasPorFaixa: lpf, linhas, covasPorLinha: cpl, covas, quantidade: (covas * porCovaAqui * g100) / 100 / 1000 };
  }
  return { ...base, linhasPorFaixa: lpf, linhas, covasPorLinha: cpl, covas, ...quanto(base, covas, el, ec0) };
}

/** kg: o kg/ha da fonte levado a cada cova (kg/ha × área de uma cova da recomendação da fonte); sem kg na fonte (milho, mucuna),
 *  o número de sementes (covas × por cova, como pede o A1); outras unidades: covas × por cova. */
function quanto(it, covas, el, ec) {
  if (it.unidade === "kg") {
    const kg = num(it.dados?.semente_kg_ha);
    if (kg && el && ec) return { quantidade: covas * kg * el * ec / 1e4 };
    return it.material === "semente" && num(it.dados?.por_cova) ? { quantidade: covas * it.por_cova, unidade: "sementes" } : { quantidade: null };
  }
  return { quantidade: it.unidade ? covas * it.por_cova : null };
}

/** O caupi no milho em pé (agronomia.json, Feijão-caupi.consorcio: 500 Perguntas, cap. 12): covas a 25 cm com 2 sementes (8 por
 *  metro, a ponta alta dos 6 a 8 da fonte), não a densidade do caupi sozinho. Sem o campo, a distância do "como" ("a cada 25 cm"). */
function consorcio(agro) {
  const d = dadosCultura(agro, "Feijão-caupi"), c = d?.consorcio;
  if (c && num(c.entre_covas_m)) {
    const g = Array.isArray(c.g_100_sementes) && c.g_100_sementes.length === 2 ? (c.g_100_sementes[0] + c.g_100_sementes[1]) / 2 : null;
    return { ec: +c.entre_covas_m, por_cova: num(c.por_cova) || 2, g100: g };
  }
  const s = (d?.como || []).find((x) => /rua do milho/i.test(x)) || "";
  const m = /a cada (\d+)\s*cm/i.exec(s);
  return m ? { ec: +m[1] / 100, por_cova: null, g100: null } : null;
}

/** As culturas de uma parte (Parte A/B/C ou Baixio) no ano k: a 1ª nas carreiras; a 2ª ("X + Y" ou o revezamento do texto do
 *  motor, "+ feijão-caupi em revezamento (50–85 dias depois)") entre as carreiras da 1ª. */
/** A 2ª planta no milho em pé, pelo texto do motor (a mesma leitura de segundaBaixio em passos/plantio.js): "+ feijão em revezamento"
 *  e "+ feijão-caupi em revezamento" são a leguminosa do plano; "+ mucuna-preta no milho em pé"; nada com "solteiro" ou "sem revezamento". */
function segunda(c, plano) {
  const t = String(c.texto || ""), leg = plano?.leguminosa || "Feijão-caupi";
  if (/sem revezamento|sem feijão para revezar|solteiro/i.test(t)) return null;
  if (c.mucuna || /mucuna/i.test(t)) return "Mucuna-preta";
  const m = /\+\s*([^;(]+?)\s+(?:em revezamento|no milho em pé)/i.exec(t);
  if (m) return /^feij[aã]o(-caupi)?$/i.test(m[1].trim()) ? leg : m[1].trim();
  return /revezamento/i.test(t) ? leg : null;
}

function itensDaParte(agro, c, w, L, nf, plano) {
  if (ehPousio(c.cultura)) return [];
  const nomes = separar(c.cultura);
  const t = String(c.texto || "");
  const seg = nomes.length === 1 ? segunda(c, plano) : null, revez = !!seg && !/mucuna/i.test(seg);
  if (seg) nomes.push(seg);
  const pr = item(agro, nomes[0], "principal", { w, L, nf });
  const out = [pr];
  if (nomes[1] && pr.linhasPorFaixa) { // só com as carreiras do principal medidas dá para contar as do meio
    const nota = (/\((\d+\s*[–-]\s*\d+ dias depois)\)/.exec(t) || [])[1] || "";
    const cs = revez && /caupi/i.test(nomes[1]) ? consorcio(agro) : null;
    out.push(item(agro, nomes[1], "entrelinhas", { L, nf, lpf: Math.max(1, pr.linhasPorFaixa - 1), nota, ecAqui: cs?.ec || null,
      porCovaAqui: cs?.por_cova || null, g100: cs?.g100 || null }));
  }
  return out;
}

/** O que não pede material no ano k (uma regra só para o Plano e o Relatório): descanso, o que já está no chão (a mandioca dele, a
 *  perene que ele tem) e a mesma mandioca ou perene do ano anterior. → texto curto ou null (pede material). */
export function nadaDe(f, k) {
  const c = f?.anos?.[k], ant = k > 0 ? f?.anos?.[k - 1] : null;
  if (!c) return null;
  if (ehPousio(c.cultura)) return "descansa";
  if (c.ja_no_chao || c.ja_plantado) return "já está no chão";
  if (c.cultura === "Mandioca") return fasesMandioca(f)[k] === "colhe" ? "mandioca segue no chão" : null;
  if (ant && ant.cultura === c.cultura && /tampão|perene/.test(c.tipo || "")) return `${curto(c.cultura)} ${separar(c.cultura).length > 1 ? "seguem" : "segue"} no chão`;
  return null;
}
/** A fase da mandioca em cada ano da parte: "planta" (pede maniva), "colhe" (a do ano anterior segue no chão) ou "chao" (a que já
 *  está no chão em 2027). A que já está no chão sem m2 nem velha colhe e replanta com a rama dela (o 2º ano é "colhe"). */
export function fasesMandioca(f) {
  const out = [];
  (f?.anos || []).forEach((c, k) => {
    if (c?.cultura !== "Mandioca") { out.push(null); return; }
    if (k === 0 && c.ja_no_chao) { out.push(c.m2 || c.velha ? "chao-fim" : "chao"); return; }
    const p = k ? out[k - 1] : null;
    out.push(p === "planta" || p === "chao" ? "colhe" : "planta");
  });
  return out.map((x) => (x === "chao-fim" ? "chao" : x));
}
const semMaterial = (its) => its.map((i) => ({ ...i, quantidade: null }));

/** As linhas da lista "parte por parte" no ano k. Cada linha traz `nada` (texto) quando não pede material naquele ano; o pedaço
 *  das perenes que ele já tem (lay.reserva) vem primeiro, com id "Perene". */
export function contas(lay, k, agro, plano = null) {
  const linhas = [];
  const rep = lay.partes.length ? lay.nFaixas / lay.partes.length : 0;
  if (lay.reserva) {
    linhas.push({ id: "Perene", letra: "", parte: "Já plantado", cultura: lay.reserva.culturas.join(" + "), tipo: "perene", pousio: false,
      incerto: false, nFaixas: 1, larguraM: lay.reserva.larguraM, comprimentoM: lay.larg, ha: lay.reserva.ha, itens: [], nada: "já está no chão",
      porCultura: lay.reserva.porCultura });
  }
  for (const q of lay.partes) {
    const c = q.anos[k], letra = q.parte.replace("Parte ", ""), nada = nadaDe(q, k);
    const itens = itensDaParte(agro, c, lay.larguraFaixa, lay.larg, rep, plano);
    linhas.push({ id: letra, letra, parte: q.parte, cultura: c.cultura, tipo: c.tipo, pousio: ehPousio(c.cultura), incerto: false,
      nFaixas: rep, larguraM: lay.larguraFaixa, comprimentoM: lay.larg, ha: lay.haParte, nada, itens: nada ? semMaterial(itens) : itens });
  }
  if (lay.temBaixio) {
    const c = lay.bx.anos[k], nada = nadaDe(lay.bx, k);
    const itens = itensDaParte(agro, c, lay.profBaixio, lay.larg, 1, plano);
    linhas.push({ id: "Baixio", letra: "", parte: "Baixio", cultura: c.cultura, tipo: c.tipo, pousio: ehPousio(c.cultura), incerto: lay.incerto,
      nFaixas: 1, larguraM: lay.profBaixio, comprimentoM: lay.larg, ha: lay.haBaixio, nada, itens: nada ? semMaterial(itens) : itens });
  }
  if (lay.bordas) {
    const c = lay.bordas.anos[k], P = 2 * (lay.larg + lay.comp), nada = nadaDe(lay.bordas, k);
    // cerca viva: uma linha de cada em volta do roçado (palma por dentro, gliricídia por fora), como no desenho do passo 3
    const itens = separar(c.cultura).slice(0, 2).map((nome, i) => item(agro, nome, i ? "fora" : "dentro", { L: P, lpf: 1 }));
    linhas.push({ id: "Bordas", letra: "", parte: "Bordas", cultura: c.cultura, tipo: c.tipo, pousio: false, incerto: false,
      nFaixas: 1, larguraM: null, comprimentoM: null, perimetroM: P, ha: null, nada, itens: nada ? semMaterial(itens) : itens });
  }
  const fontes = [...new Set(linhas.flatMap((l) => l.itens.map((i) => i.dados?.fonte).filter(Boolean)))];
  return { linhas, fontes, ano: plano?.anos?.[k] ?? null };
}

// ------------------------------------------------------------------ texto (puro)
const CURTO = { "Feijão-caupi": "caupi", "Sorgo granífero": "sorgo de grão", "Sorgo forrageiro": "sorgo forrageiro", "Palma forrageira": "palma",
  "Pousio pastejado": "descanso", "Palma + gliricídia": "palma e gliricídia" };
export const curto = (c) => CURTO[c] || (ehPousio(c) ? "descanso" : String(c || "").toLowerCase());
export const metros = (U, m) => `${U.num(m, m >= 100 || Math.abs(m - Math.round(m)) < 0.05 ? 0 : 1)} m`; // 16,7 m (6 × 16,7 = 100)
export const dist = (U, m) => (m < 1 ? `${U.num(m * 100, 0)} cm` : `${U.num(m, Math.abs(m - Math.round(m)) < 0.05 ? 0 : 1)} m`);
export const haTxt = (U, v) => (v < 0.1 ? `${U.num(v * 1e4 >= 100 ? Math.round(v * 1e3) * 10 : Math.round(v * 1e4), 0)} m²` // 0,04 ha → "400 m²"
  : `${U.num(v, v >= 10 ? 0 : v >= 1 ? 1 : 2).replace(/,0+$/, "")} ha`);
const plural = (p, n) => (n === 1 ? p : p.replace(/(semente|maniva|muda|raquete|estaca)$/, "$1s"));

/** "≈ 3.720 manivas", "≈ 2,6 kg", "≈ 350 g", "≈ 1,2 t". null → "". */
export function qtdTxt(U, it) {
  const q = it.quantidade;
  if (q === null || q === undefined) return "";
  if (it.unidade === "kg") {
    if (q < 1) return `≈ ${U.num(Math.max(10, Math.round(q * 100) * 10), 0)} g`;
    return q < 10 ? `≈ ${U.num(q, 1)} kg` : q < 1000 ? `≈ ${U.num(q, 0)} kg` : `≈ ${U.num(q / 1000, 1)} t`;
  }
  // semente sem o kg na fonte (milho, mucuna, feijão comum, girassol): em mil, e o milho também em sacos (o saco vem com ~60 mil)
  if (it.unidade === "sementes" && q >= 1000) {
    const mil = q >= 10000 ? Math.round(q / 1000) : Math.round(q / 100) / 10;
    const saco = +(it.dados?.saco_sementes || 0);
    const sc = saco > 0 ? q / saco : 0;
    return `≈ ${U.num(mil, mil < 10 ? 1 : 0).replace(/,0$/, "")} mil sementes${sc ? ` (${sc < 0.95 ? "menos de 1 saco" : `≈ ${U.num(sc, sc < 10 ? 1 : 0).replace(/,0$/, "")} ${sc < 1.95 ? "saco" : "sacos"}`} de 60 mil)` : ""}`;
  }
  const n = q < 100 ? Math.round(q) : Math.round(q / 10) * 10;
  return `≈ ${U.num(n, 0)} ${n === 1 ? String(it.unidade).replace(/s$/, "") : it.unidade}`;
}

const profTxt = (p) => (!p ? "" : /^\d/.test(String(p)) ? `a ${p} cm de fundo` : String(p));

/** As frases de uma linha da lista (texto puro). */
export function frases(U, l) {
  if (l.id === "Perene") { // o pedaço das perenes que ele já tem
    const cs = (l.porCultura || []).map((x) => `${curto(x.cultura)} ${haTxt(U, x.ha)}`);
    return { titulo: `Já plantado · ${lista(separar(l.cultura).map(curto))}`, area: l.ha ? haTxt(U, l.ha) : "",
      medida: `${metros(U, l.larguraM)} × ${metros(U, l.comprimentoM)}, no alto`, leve: l.nada,
      itens: [{ espacamento: `Fica como está, fora do giro${cs.length > 1 ? `: ${lista(cs)}` : ""}.`, material: "" }] };
  }
  const nome = l.id === "Bordas" ? "Cerca viva" : l.id === "Baixio" ? "Baixio" : `${l.letra}`;
  const cult = l.pousio ? "Descanso" : l.id === "Bordas" ? lista(separar(l.cultura).map(curto))
    : l.itens.length > 1 ? `${l.itens[0].cultura} + ${curto(l.itens[1].cultura)}` : (l.itens[0]?.cultura || l.cultura);
  if (l.nada && !l.pousio) {
    return { titulo: `${nome} · ${cult}`, area: l.ha ? haTxt(U, l.ha) : "", medida: medidaDe(U, l), leve: l.nada,
      itens: [{ espacamento: `${cap(l.nada)}: nada a plantar neste ano.`, material: "" }] };
  }
  const medida = medidaDe(U, l);
  const itens = l.pousio ? [{ espacamento: "Descansa: pasto da criação.", material: "" }] : l.itens.map((it) => {
    if (!it.covas) return { espacamento: `${cap(curto(it.cultura || l.cultura))}: espaçamento com o técnico`, material: "" };
    const pc = `${it.por_cova} ${plural(it.material || "semente", it.por_cova)}`;
    if (it.papel === "dentro" || it.papel === "fora") {
      return { espacamento: `${curto(it.cultura)} por ${it.papel}, a cada ${dist(U, it.entre_covas_m)}`.replace(/^./, (x) => x.toUpperCase()),
        material: `leve ${qtdTxt(U, it)}` };
    }
    if (it.papel === "entrelinhas") {
      return { espacamento: `${curto(it.cultura).replace(/^./, (x) => x.toUpperCase())} entre as carreiras${it.nota ? `, ${it.nota}` : ""}: covas a ${dist(U, it.entre_covas_m)}, ${pc}`,
        material: `leve ${qtdTxt(U, it)}` };
    }
    const porFaixa = l.nFaixas > 1 ? " por faixa" : "";
    const car = `${U.num(it.linhasPorFaixa, 0)} ${it.linhasPorFaixa === 1 ? "carreira" : "carreiras"}`;
    // por_cova null (algodão): a fonte dá 1 planta a cada tantos cm, não covas
    if (it.dados?.por_cova == null) {
      return { espacamento: `${car}${porFaixa} · linhas a ${dist(U, it.entre_linhas_m)} · 1 planta a cada ${dist(U, it.entre_covas_m)}`,
        material: `leve ${qtdTxt(U, it)}` };
    }
    return { espacamento: `${car}${porFaixa} · linhas a ${dist(U, it.entre_linhas_m)} · covas a ${dist(U, it.entre_covas_m)}`,
      material: `${pc} por cova · leve ${qtdTxt(U, it)}`, porCova: `${pc} por cova` };
  });
  return { titulo: `${nome} · ${cult}`, area: l.ha ? haTxt(U, l.ha) : "", medida, itens, leve: leve(U, l) };
}

const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);
const lista = (xs) => (xs.length <= 1 ? xs.join("") : `${xs.slice(0, -1).join(", ")} e ${xs[xs.length - 1]}`);
function medidaDe(U, l) {
  return l.id === "Bordas" ? `${metros(U, l.perimetroM)} em volta do roçado`
    : l.id === "Baixio" ? `${metros(U, l.larguraM)} × ${metros(U, l.comprimentoM)}${l.incerto ? ", se tiver baixio" : ""}`
      : `${l.nFaixas === 1 ? "1 faixa" : `${U.num(l.nFaixas, 0)} faixas`} de ${metros(U, l.larguraM)} × ${metros(U, l.comprimentoM)}`;
}

/** O material numa linha só (a linha fechada da lista): "≈ 2.110 manivas", "≈ 2,6 kg de semente", "≈ 560 raquetes de palma e 56
 *  estacas de gliricídia" (cada quantidade com o nome dela); "já está no chão" quando a parte não pede nada no ano. */
function leve(U, l) {
  if (l.pousio) return "nada a plantar";
  if (l.nada) return l.nada;
  const com = l.itens.filter((i) => i.quantidade !== null);
  if (!com.length) return "";
  if (l.id === "Bordas") return lista(com.map((i) => `${qtdTxt(U, i)} ${i.unidade === "kg" ? "de semente de" : "de"} ${curto(i.cultura)}`));
  const pr = com[0], sec = com.find((i) => i.papel === "entrelinhas");
  const de = sec ? ` de ${curto(pr.cultura)}` : pr.unidade === "kg" ? " de semente" : "";
  return `${qtdTxt(U, pr)}${pr.unidade === "kg" || pr.unidade === "sementes" ? de : ""}`;
}

// ------------------------------------------------------------------ desenhos (SVG em texto)
const f1 = (v) => v.toFixed(1);
const larguraTexto = (t, fs) => t.length * fs * 0.52; // Inter 600 a 12 px: ~0,41 em por letra no Edge; 0,52 dá folga

/** Carreiras de uma faixa, com no mínimo 4 px entre as desenhadas (as que não cabem são puladas: só o sentido das linhas). */
function carreiras(x, w, yTopo, it, s, cls = "") {
  if (!it?.linhasPorFaixa || !it.entre_linhas_m) return "";
  const passo = Math.max(1, Math.ceil(4 / (it.entre_linhas_m * s)));
  let h = `<g class="tr-lin${cls}">`;
  for (let j = 0; j < it.linhasPorFaixa; j += passo) {
    const y = f1(yTopo + (it.entre_linhas_m / 2 + j * it.entre_linhas_m) * s);
    h += `<line x1="${f1(x + 2)}" y1="${y}" x2="${f1(x + w - 2)}" y2="${y}"/>`;
  }
  return h + "</g>";
}

/** O roçado visto de cima, em escala, com as cotas (largura em cima, comprimento à esquerda), as faixas do ano k, o baixio e a
 *  cerca viva. zoom = id da linha ("A", "Baixio"…) onde vai o quadradinho de 5 m do "de perto". */
export function svgTerreno(U, lay, k, { W = 340, Hmax = 360, zoom = null, agro = null, plano = null } = {}) {
  const cerca = lay.bordas ? 9 : 0, ml = 30, mt = 30, mr = 8, mb = 26, fs = 12;
  const aw = W - ml - mr - 2 * cerca;
  const s = Math.min(aw / lay.larg, Hmax / lay.comp);
  const w = lay.larg * s, h = lay.comp * s, x0 = ml + cerca, y0 = mt + cerca;
  const H = Math.ceil(y0 + h + cerca + mb);
  const livre = W - mr - (x0 + w + cerca + 8); // espaço à direita do roçado (roçado estreito: os rótulos vão para lá)
  const ct = contas(lay, k, agro, plano);
  const porId = Object.fromEntries(ct.linhas.map((l) => [l.id, l]));
  // rótulo da faixa ("A mandioca 16,7 m", a letra em negrito e os metros apagados): com os metros ou sem, dentro da faixa ou à
  // direita do roçado (roçado estreito); sem lugar, só a letra
  const rotulo = (cab, nome, med, y, hh) => {
    const yt = f1(y + hh / 2 + fs * 0.36);
    for (const m of [med, ""]) {
      const tw = larguraTexto(`${cab} ${nome}${m ? " " + m : ""}`, fs);
      const t = `<tspan class="tr-l">${U.esc(cab)}</tspan> ${U.esc(nome)}${m ? ` <tspan class="tr-m">${U.esc(m)}</tspan>` : ""}`;
      const fundo = `<rect class="tr-rot-fundo" x="${f1(x0 + 3)}" y="${f1(+yt - fs + 1)}" width="${f1(tw * 0.87 + 7)}" height="${fs + 5}" rx="4"/>`;
      if (hh >= fs + 3 && tw <= w - 12) return `${fundo}<text class="tr-rot" x="${f1(x0 + 6)}" y="${yt}">${t}</text>`;
      if (hh >= fs + 1 && tw <= livre) return `<text class="tr-rot fora" x="${f1(x0 + w + cerca + 8)}" y="${yt}">${t}</text>`;
    }
    if (hh >= 11 && w >= 14) return `<text class="tr-rot" x="${f1(x0 + 4)}" y="${f1(y + hh / 2 + 4)}"><tspan class="tr-l">${U.esc(cab)}</tspan></text>`;
    return "";
  };
  let g = `<svg class="tr-svg" viewBox="0 0 ${W} ${H}" style="max-width:${W}px" role="img"
    aria-label="O seu roçado visto de cima, em escala: ${U.esc(metros(U, lay.larg))} de largura e ${U.esc(metros(U, lay.comp))} de comprimento">`;
  if (lay.bordas) {
    g += `<g class="tr-bordas t-perene"><rect class="b-fora" x="${f1(x0 - cerca + 1)}" y="${f1(y0 - cerca + 1)}" width="${f1(w + 2 * cerca - 2)}" height="${f1(h + 2 * cerca - 2)}" rx="5"/>
      <rect class="b-dentro" x="${f1(x0 - 4)}" y="${f1(y0 - 4)}" width="${f1(w + 8)}" height="${f1(h + 8)}" rx="3"/></g>`;
  }
  let marca = null;
  if (lay.reserva && porId.Perene) { // as perenes que ele já tem: o pedaço delas, no alto, em escala
    const hh = lay.reserva.y1 * s;
    g += `<g class="tr-fx t-perene"><rect class="chao" x="${f1(x0)}" y="${f1(y0)}" width="${f1(w)}" height="${f1(hh)}"/>
      ${rotulo("Já plantado", lista(separar(porId.Perene.cultura).map(curto)), metros(U, lay.reserva.larguraM), y0, hh)}</g>`;
  }
  lay.faixas.forEach((f) => {
    const l = porId[f.letra], y = y0 + f.y0 * s, hh = (f.y1 - f.y0) * s;
    g += `<g class="tr-fx ${U.tipoCss(l.pousio ? "pousio" : l.tipo)}"><rect class="chao" x="${f1(x0)}" y="${f1(y)}" width="${f1(w)}" height="${f1(hh)}"/>
      ${l.pousio ? "" : carreiras(x0, w, y, l.itens[0], s)}
      ${rotulo(f.letra, curto(l.cultura), metros(U, f.larguraM), y, hh)}</g>`;
    if (zoom === f.letra && !marca) marca = { y, hh };
  });
  if (lay.temBaixio) {
    const l = porId.Baixio, y = y0 + lay.profAlto * s, hh = h - lay.profAlto * s;
    const [pr, sec] = l.itens;
    g += `<g class="tr-fx tr-bx ${U.tipoCss(l.pousio ? "pousio" : l.tipo)}${lay.incerto ? " incerto" : ""}">
      <rect class="chao" x="${f1(x0)}" y="${f1(y)}" width="${f1(w)}" height="${f1(hh)}"/>
      ${l.pousio ? "" : carreiras(x0, w, y, pr, s)}
      ${sec && pr?.entre_linhas_m ? `<g class="t-leguminosa">${carreiras(x0, w, y + (pr.entre_linhas_m / 2) * s, { ...sec, entre_linhas_m: pr.entre_linhas_m }, s, " tr-sec")}</g>` : ""}
      ${rotulo(`Baixio${lay.incerto ? "?" : ""}`, `${curto(pr?.cultura || l.cultura)}${sec ? " + " + curto(sec.cultura) : ""}`, metros(U, l.larguraM), y, hh)}</g>`;
    if (zoom === "Baixio") marca = { y, hh };
  }
  if (marca) {
    const l = porId[zoom], ld = ladoZoom(l) * s, zs = Math.max(ld, 7);
    const zx = x0 + w - zs - 4, zy = marca.y + Math.max(0, (marca.hh - zs) / 2);
    g += `<rect class="tr-marca" x="${f1(zx)}" y="${f1(zy)}" width="${f1(zs)}" height="${f1(zs)}"/>`;
  }
  // cotas: largura em cima, comprimento à esquerda
  const yc = mt - 14, xc = ml - 14;
  g += `<g class="tr-cota"><line x1="${f1(x0)}" y1="${yc}" x2="${f1(x0 + w)}" y2="${yc}"/><line x1="${f1(x0)}" y1="${yc - 5}" x2="${f1(x0)}" y2="${yc + 5}"/>
      <line x1="${f1(x0 + w)}" y1="${yc - 5}" x2="${f1(x0 + w)}" y2="${yc + 5}"/>
      <line x1="${xc}" y1="${f1(y0)}" x2="${xc}" y2="${f1(y0 + h)}"/><line x1="${xc - 5}" y1="${f1(y0)}" x2="${xc + 5}" y2="${f1(y0)}"/>
      <line x1="${xc - 5}" y1="${f1(y0 + h)}" x2="${xc + 5}" y2="${f1(y0 + h)}"/></g>
    <text class="tr-cota-t" x="${f1(x0 + w / 2)}" y="${yc - 6}" text-anchor="middle">${U.esc(metros(U, lay.larg))}</text>
    ${h >= 50 ? `<text class="tr-cota-t" transform="translate(${xc - 6},${f1(y0 + h / 2)}) rotate(-90)" text-anchor="middle">${U.esc(metros(U, lay.comp))}</text>`
    : `<text class="tr-cota-t" x="${xc - 5}" y="${f1(y0 + h + cerca + 18)}">↕ ${U.esc(metros(U, lay.comp))}</text>`}
    <text class="tr-eixo" x="${f1(x0 + w + cerca)}" y="${f1(y0 + h + cerca + 18)}" text-anchor="end">a água desce ↓</text>
  </svg>`;
  return g;
}

/** Lado do pedaço do zoom: 5 m; maior para caju, banana, mamona (pelo menos 2 linhas e 2 covas). */
function ladoZoom(l) {
  const it = l?.itens?.[0];
  const maior = Math.max(it?.entre_linhas_m || 0, it?.entre_covas_m || 0);
  return maior * 2.2 > 5 ? Math.ceil(maior * 2.2) : 5;
}

/** Uma cova: semente = bolinha com os grãos dentro; maniva = risco (a rama deitada); muda, raquete, estaca = bolinha cheia. */
function cova(x, y, r, it) {
  if (it.material === "maniva") {
    const d = r * 0.85;
    return `<line class="tr-maniva" x1="${f1(x - d)}" y1="${f1(y + d * 0.6)}" x2="${f1(x + d)}" y2="${f1(y - d * 0.6)}"/>`;
  }
  if (it.material && it.material !== "semente") return `<circle class="tr-muda" cx="${f1(x)}" cy="${f1(y)}" r="${f1(r * 0.8)}"/>`;
  let h = `<circle class="tr-cova" cx="${f1(x)}" cy="${f1(y)}" r="${f1(r)}"/>`;
  if (r >= 4) {
    const n = Math.min(4, it.por_cova), d = r * 0.4, rg = Math.max(1.1, r * 0.2);
    const pos = n === 1 ? [[0, 0]] : n === 2 ? [[-d, 0], [d, 0]] : n === 3 ? [[0, -d], [-d, d * 0.7], [d, d * 0.7]] : [[-d, -d], [d, -d], [-d, d], [d, d]];
    for (const [dx, dy] of pos) h += `<circle class="tr-grao" cx="${f1(x + dx)}" cy="${f1(y + dy)}" r="${f1(rg)}"/>`;
  }
  return h;
}

/** O pedaço de 5 × 5 m (ou maior, para as perenes de espaçamento largo) de uma linha da lista, em escala: as carreiras, as covas,
 *  e as cotas da distância entre linhas (à esquerda) e entre covas (em cima). */
export function svgZoom(U, l, { W = 300 } = {}) {
  const pr = l.itens.find((i) => i.papel === "principal" && i.covas);
  if (!pr) return "";
  const sec = l.itens.find((i) => i.papel === "entrelinhas" && i.covas);
  const lado = ladoZoom(l), ml = 50, mt = 30, mr = 24, mb = 24;
  const Z = W - ml - mr, z = Z / lado, H = mt + Z + mb;
  const el = pr.entre_linhas_m, ec = pr.entre_covas_m;
  const r = Math.max(2.5, Math.min(10, 0.32 * Math.min(el, ec) * z));
  let g = `<svg class="tr-zoom-svg" viewBox="0 0 ${W} ${H}" style="max-width:${W}px" role="img"
    aria-label="Um pedaço de ${lado} por ${lado} metros: carreiras a ${U.esc(dist(U, el))} e covas a ${U.esc(dist(U, ec))}">
    <g class="${U.tipoCss(l.tipo)}"><rect class="chao" x="${ml}" y="${mt}" width="${Z}" height="${Z}" rx="4"/>`;
  const ys = [];
  for (let y = el / 2; y < lado; y += el) ys.push(y);
  for (const y of ys) {
    const yy = mt + y * z;
    g += `<line class="tr-z-lin" x1="${ml + 3}" y1="${f1(yy)}" x2="${ml + Z - 3}" y2="${f1(yy)}"/>`;
    for (let x = ec / 2; x < lado; x += ec) g += cova(ml + x * z, yy, r, pr);
  }
  g += "</g>";
  if (sec) {
    const r2 = Math.max(2.5, Math.min(10, 0.32 * Math.min(el, sec.entre_covas_m) * z));
    g += `<g class="t-leguminosa">`;
    for (const y of ys) {
      const yy = mt + (y + el / 2) * z;
      if (y + el / 2 >= lado) continue;
      g += `<line class="tr-z-lin tr-sec" x1="${ml + 3}" y1="${f1(yy)}" x2="${ml + Z - 3}" y2="${f1(yy)}"/>`;
      for (let x = sec.entre_covas_m / 2; x < lado; x += sec.entre_covas_m) g += cova(ml + x * z, yy, r2, sec);
    }
    g += "</g>";
  }
  // cotas: entre linhas (à esquerda, entre as 2 primeiras carreiras) e entre covas (em cima, entre as 2 primeiras covas)
  const ya = mt + (el / 2) * z, yb = ya + el * z, xa = ml + (ec / 2) * z, xb = xa + ec * z, xl = ml - 8, yt = mt - 9;
  const tEl = dist(U, el), tEc = dist(U, ec);
  g += `<g class="tr-cota">
      <line x1="${xl}" y1="${f1(ya)}" x2="${xl}" y2="${f1(yb)}"/><line x1="${xl - 4}" y1="${f1(ya)}" x2="${xl + 4}" y2="${f1(ya)}"/><line x1="${xl - 4}" y1="${f1(yb)}" x2="${xl + 4}" y2="${f1(yb)}"/>
      <line x1="${f1(xa)}" y1="${yt}" x2="${f1(xb)}" y2="${yt}"/><line x1="${f1(xa)}" y1="${yt - 4}" x2="${f1(xa)}" y2="${yt + 4}"/><line x1="${f1(xb)}" y1="${yt - 4}" x2="${f1(xb)}" y2="${yt + 4}"/></g>
    <text class="tr-cota-t" x="${xl - 6}" y="${f1((ya + yb) / 2 + 4)}" text-anchor="end">${U.esc(tEl)}</text>
    <text class="tr-cota-t" x="${f1(xb - xa >= larguraTexto(tEc, 12) + 4 ? (xa + xb) / 2 : xb + 4)}" y="${yt - 5}"
      text-anchor="${xb - xa >= larguraTexto(tEc, 12) + 4 ? "middle" : "start"}">${U.esc(tEc)}</text>
    <text class="tr-eixo" x="${f1(ml + Z / 2)}" y="${f1(mt + Z + 17)}" text-anchor="middle">${lado} m</text>
    <text class="tr-eixo" transform="translate(${f1(ml + Z + 15)},${f1(mt + Z / 2)}) rotate(90)" text-anchor="middle">${lado} m</text>
  </svg>`;
  return g;
}

// ------------------------------------------------------------------ o bloco na página
const est = { zoom: null, aberta: null }; // a parte do "de perto" e a parte aberta na lista (estado de tela, não é resposta)

function pedirCss() {
  const href = new URL("../../css/extras/terreno.css", import.meta.url).href;
  return new Promise((ok) => {
    if ([...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === href)) return ok();
    document.head.appendChild(Object.assign(document.createElement("link"), { rel: "stylesheet", href, onload: ok, onerror: ok }));
  });
}

const LAYOUT = "Partes A, B e C do mesmo tamanho, em faixas em nível de pelo menos 10 m (A B C A B C), o baixio embaixo e a cerca viva "
  + "em volta sem tirar área, como no desenho do plano";

function legendaZoom(U, l) {
  const pr = l.itens.find((i) => i.papel === "principal" && i.covas);
  const sec = l.itens.find((i) => i.papel === "entrelinhas" && i.covas);
  const marca = pr.material === "maniva" ? "Cada risco é uma cova" : "Cada bolinha é uma cova";
  const prof = profTxt(pr.dados?.profundidade_cm);
  return `${marca}: ${pr.por_cova} ${plural(pr.material || "semente", pr.por_cova)}${prof ? `, ${U.esc(prof)}` : ""}.`
    + (sec ? ` Linha tracejada: ${U.esc(curto(sec.cultura))} entre as carreiras.` : "");
}

function html(ctx, lay, k, plano, agro, W) {
  const U = ctx.util, ct = contas(lay, k, agro, plano);
  const zoomaveis = ct.linhas.filter((l) => l.id !== "Bordas" && l.itens.some((i) => i.papel === "principal" && i.covas));
  if (!zoomaveis.some((l) => l.id === est.zoom)) est.zoom = zoomaveis[0]?.id || null;
  const zl = zoomaveis.find((l) => l.id === est.zoom);
  const ano = plano.anos[k];
  const sup = lay.medidas !== "resposta";
  const seloDesenho = U.selo("suposicao", (sup ? "quadrado com a área do roçado (você ainda não deu as medidas); " : "as suas medidas; ") + LAYOUT);
  const medidas = sup
    ? `<p class="tr-medidas">Desenhamos um quadrado de <b>${metros(U, lay.larg)} × ${metros(U, lay.comp)}</b>
        (${haTxt(U, lay.ha)}${ctx.ef.ha_origem === "resposta" ? ", o tamanho que você deu" : ", o típico daqui"}).
        <a class="tr-medir" href="${ctx.link ? ctx.link(2) : "#"}" data-editar="ha">Pôr as medidas do seu terreno</a></p>`
    : `<p class="tr-medidas"><b>${metros(U, lay.larg)}</b> de largura × <b>${metros(U, lay.comp)}</b> de comprimento = ${haTxt(U, lay.ha)}</p>`;
  const fonteEsp = ct.fontes.length ? `Espaçamento: ${ct.fontes.join("; ")}. Quantidades contadas sobre o desenho (a 1ª carreira a meia `
    + "distância da divisa), sem sobra para replantio." : "";
  // a lista: uma linha por parte com o material; a parte aberta (a do zoom, ou a tocada) mostra as medidas e o espaçamento
  if (!ct.linhas.some((l) => l.id === est.aberta)) est.aberta = est.zoom || ct.linhas[0]?.id;
  const lista = ct.linhas.map((l) => {
    const fr = frases(U, l), aberta = l.id === est.aberta;
    const det = aberta ? `<span class="tr-p-med">${U.esc(fr.medida)}${fr.area ? ` · ${U.esc(fr.area)}` : ""}</span>
      ${fr.itens.map((i, j) => { // o total da 1ª cultura (e os da cerca) já está na linha de cima: aqui só o que falta
        const mat = i.porCova || (j > 0 && l.id !== "Bordas" ? i.material : "");
        return `<span class="tr-p-esp">${U.esc(i.espacamento)}</span>${mat ? `<span class="tr-p-mat">${U.esc(mat)}</span>` : ""}`;
      }).join("")}` : "";
    const cls = `tr-parte ${U.tipoCss(l.pousio ? "pousio" : l.tipo)}${l.incerto ? " incerto" : ""}`;
    return `<li><button type="button" class="${cls}" data-tr-parte="${U.esc(l.id)}"${zoomaveis.includes(l) ? ' data-zoom="1"' : ""} aria-expanded="${aberta}">
      <span class="tr-p-l1"><b>${U.esc(fr.titulo)}</b><span class="tr-p-leve">${U.esc(fr.leve)}</span></span>${det}</button></li>`;
  }).join("");
  const semDados = !agro ? `<p class="tr-aviso">Espaçamento e sementes: confira com o técnico (os dados não carregaram agora).</p>` : "";
  const zoom = zl ? `<div class="tr-zoom" data-tr-zoom-caixa>
      <p class="tr-zoom-tit">De perto: ${ladoZoom(zl)} × ${ladoZoom(zl)} m ${zl.id === "Baixio" ? "do baixio" : `da Parte ${U.esc(zl.letra)}`}</p>
      ${svgZoom(U, zl, { W: Math.min(W, 330) })}
      <p class="tr-zoom-leg">${legendaZoom(U, zl)}${zoomaveis.length > 1 ? " Toque numa parte para ver." : ""}</p></div>` : "";
  return `<div class="terreno">
    <h3>Seu terreno em metros ${seloDesenho}</h3>
    ${medidas}
    <figure class="tr-fig">${svgTerreno(U, lay, k, { W, zoom: est.zoom, agro, plano })}</figure>
    <h4 class="tr-h4">Parte por parte, em ${ano} ${fonteEsp ? U.selo("suposicao", fonteEsp) : ""}</h4>
    <ul class="tr-partes">${lista}</ul>
    ${semDados}${zoom}
  </div>`;
}

const indiceAno = (plano, ano) => {
  if (ano === undefined || ano === null || ano === "") return 0;
  const i = +ano >= 1000 ? plano.anos.indexOf(+ano) : +ano;
  return i >= 0 && i < plano.anos.length ? i : 0;
};

export default {
  id: "terreno",
  async render(el, ctx, { plano = null, ano = 0 } = {}) {
    const p = plano || ctx.r?.plano;
    if (!p?.faixas?.length) { el.innerHTML = ""; return; }
    const [agro] = await Promise.all([carregarAgronomia(), pedirCss()]);
    const k = indiceAno(p, ano);
    const lay = montar(p, ctx.ef);
    const larg = el.clientWidth || (typeof window !== "undefined" ? (window.innerWidth || 800) - 66 : 340);
    const W = Math.round(Math.min(560, Math.max(300, larg)));
    const pintar = () => {
      el.innerHTML = html(ctx, lay, k, p, agro, W);
      el.querySelectorAll("[data-tr-parte]").forEach((b) => b.addEventListener("click", () => {
        const id = b.dataset.trParte;
        if (est.aberta === id) return;
        est.aberta = id;
        if (b.dataset.zoom) est.zoom = id; // a cerca viva e o descanso só abrem: o "de perto" fica na última parte plantada
        const y = b.getBoundingClientRect().top;
        pintar();
        const nb = el.querySelector(`[data-tr-parte="${CSS.escape(id)}"]`);
        if (nb) window.scrollBy(0, nb.getBoundingClientRect().top - y); // o botão tocado fica no mesmo lugar da tela
      }));
    };
    pintar();
  },
};
