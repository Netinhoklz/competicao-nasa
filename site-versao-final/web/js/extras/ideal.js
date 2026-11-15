// QUADRA, motor do "Seu jeito, melhorado" e do "O ideal" (rodada 2, 15/11/2026; analise/fluxo2/BRIEFING.md, seção 5).
// Sem DOM: roda no navegador e no node (testes/ferramentas/teste_ideal.mjs). Uma fonte só para o Plano (/3), o Dinheiro (/4) e o
// Relatório (/5): os planos saem no formato de ctx.r.plano ({anos, faixas[{parte, por_que, anos[3]: {cultura, tipo, texto}}], notas})
// e desenham em plantio/desenho.js (montar) sem mudança; as datas saem no formato de ctx.r.agenda.linhas.
//   planoMelhor(r, resp, ef)              só as culturas que ele marcou em "O que planta hoje?", no melhor giro A/B/C (+ baixio, bordas)
//   planoIdeal(r, resp, ef, prioridade)   equilibrar = r.plano; garantir/vender/solo = as rotações de extras/cenarios.js
//   beneficios(r, resp, ef, plano, tipo)  os 9 números de "O que você ganha" (tipo: hoje | melhor | ideal), com selo e fonte
//                                          (correção Y, 15/11: comida_kg = só grão e raiz_kg à parte; ano normal = média de 2028 e 2029;
//                                          2027 = o que sobrou em pelo menos 3 dos 4 El Niños fortes; conta parcial sem a série que falta)
//   escolhaPadrao(r, resp, ef)            a prioridade padrão pelos números (nunca uma que perde nos 3 números de R$ e quebra)
//   textoItem(U, item), falaTexto(s)      o formato único dos números e os textos do núcleo com as palavras da roça
//   baseComum(r, resp, ef), itensPlano(r, ef, plano)   a base pareada e os lançamentos (dinheiro/pareado.js usa os mesmos)
//   comparar3(r, resp, ef, prioridade)    { hoje, melhor, ideal }, cada um { plano, beneficios }
//   agendaDe(r, plano, ef)                as linhas do calendário do plano (para r.plano, r.agenda.linhas sem mudar)
//   escolhido(r, resp, ef)                o plano que o Plano, o Dinheiro e o Relatório mostram (chaves `plano` e `prioridade`)
// Regras: nada de número inventado (null = "não medido"); R$ e quebra pela conta de passos/dinheiro/calculo.js (que não muda) e de
// extras/hoje_ideal.js; datas só das janelas do ZARC de r.agenda.culturas e das regras de calendário do núcleo (nucleo/motor.py:
// _linha, _revezamento, _estacao_tipica), copiadas de r.agenda.linhas sempre que a mesma cultura já tem linha lá.
// API exata e números de conferência: analise/fluxo2/implementacao/A2.md.
import * as C from "../passos/dinheiro/calculo.js";
import { montar as montarDesenho, grade, ehGram } from "../passos/plantio/desenho.js";
import { CULT } from "./culturas.js";
import { lerHoje, areasHoje, itensCen, mesesS0, quebra, seriesDe } from "./hoje_ideal.js";
import { calcular as calcCenarios, manchete, troca, NOME as NOME_JEITO, DA_PRIORIDADE, linhasDe, semMono } from "./cenarios.js";

// ------------------------------------------------------------------ coeficientes de agronomia (web/dados/agronomia.json, do A1)
let AGRO = null;
async function carregarAgro() {
  try {
    const url = new URL("../../dados/agronomia.json", import.meta.url);
    if (url.protocol === "file:") { // node (testes): lê do disco
      const fs = await import("node:fs");
      return fs.existsSync(url) ? JSON.parse(fs.readFileSync(url, "utf8")) : null;
    }
    // servidor ocupado recusa pedido: tenta de novo uma vez (como os extras de comum.js)
    const pedir = () => fetch(url).then((x) => (x.ok ? x.json() : Promise.reject(new Error(String(x.status)))));
    return await pedir().catch(() => new Promise((ok) => setTimeout(ok, 400)).then(pedir)).catch(() => null);
  } catch (_) { return null; } // sem o arquivo: N, palhada e forragem ficam "não medido"
}
AGRO = await carregarAgro();
/** Troca os coeficientes (testes, ou a página que já tem o JSON). null = sem coeficientes. Limpa os números guardados. */
export function definirAgronomia(j) { AGRO = j || null; MEMO = new WeakMap(); MEMO_P = new WeakMap(); }
export const agronomia = () => AGRO;

// ------------------------------------------------------------------ vocabulário
export const PRIORIDADES = ["garantir", "vender", "solo", "equilibrar"];
/** O nome de cada prioridade na frente (o mesmo das abas de "O que vale mais para você?"). */
export const NOME_PRIORIDADE = { garantir: "Guardar água", vender: "Mais renda", solo: "Cuidar do solo", equilibrar: "Um pouco de cada" };
// tipo de cada cultura no plano (o mesmo TIPO_ROT de nucleo/motor.py)
const TIPO = { "Feijão-caupi": "leguminosa", "Feijão comum": "leguminosa", Amendoim: "leguminosa", Guandu: "perene", "Mucuna-preta": "leguminosa",
  Milho: "cereal", "Sorgo granífero": "cereal", "Sorgo forrageiro": "forragem", Milheto: "forragem", "Palma forrageira": "perene",
  Gliricídia: "perene", Mandioca: "tampão", "Algodão herbáceo": "renda", Mamona: "renda", Girassol: "renda", Caju: "perene",
  Banana: "perene", "Cana-de-açúcar": "perene", "Pousio pastejado": "pousio" };
// dias do plantio à colheita (mínimo, máximo, fonte): CICLO de nucleo/motor.py, o mesmo das barras de colheita de r.agenda
const CICLO = {
  "Feijão-caupi": [60, 75, "caupi precoce, proposta v3, S2"], "Feijão comum": [75, 90, "suposição"], Amendoim: [90, 120, "suposição"],
  Milho: [100, 120, "~110 dias; intervalo suposto"], "Sorgo granífero": [100, 120, "suposição"], "Sorgo forrageiro": [90, 120, "1º corte; suposição"],
  Milheto: [75, 100, "suposição"], "Algodão herbáceo": [120, 160, "suposição"], Mamona: [150, 240, "suposição"], Girassol: [90, 120, "suposição"],
  Mandioca: [365, 548, "a CONAB usa 18 meses"], "Palma forrageira": [540, 730, "1º corte; suposição"],
  Caju: [730, 1095, "1ª safra do cajueiro-anão no 2º–3º ano; Embrapa: 2º ano no irrigado; sequeiro: suposição"],
  Banana: [365, 450, "1º cacho; Embrapa: 11–13 meses no irrigado; 12–15 no sequeiro: suposição"],
  "Cana-de-açúcar": [365, 540, "1º corte aos 12 (cana de ano) a 18 meses (cana de ano e meio); Embrapa"],
};
const LEG = new Set(["Feijão-caupi", "Feijão comum", "Amendoim", "Mucuna-preta"]); // leguminosas anuais (giram)
const PERENE = new Set(["Palma forrageira", "Gliricídia", "Caju", "Banana", "Cana-de-açúcar", "Guandu"]); // ficam no lugar (bordas)
const CEREAL = new Set(["Milho", "Sorgo granífero"]);
const FIXA_N = new Set([...LEG, "Guandu", "Gliricídia"]);
/** M (mandioca), L (leguminosa que gira), P (perene), O (descanso) ou X (cereal, forragem e renda anuais). */
const papel = (n) => (n === "Mandioca" ? "M" : LEG.has(n) ? "L" : PERENE.has(n) ? "P" : n === "Pousio pastejado" ? "O" : "X");
const rank = (n) => (CEREAL.has(n) ? 0 : ehGram(n) ? 1 : 2);

// palavras da roça para os "por quê"
const FALA = { "Feijão-caupi": "feijão", "Feijão comum": "feijão comum", "Sorgo forrageiro": "sorgo", "Sorgo granífero": "sorgo de grão",
  "Palma forrageira": "palma", "Algodão herbáceo": "algodão", "Mucuna-preta": "mucuna", "Cana-de-açúcar": "cana", "Pousio pastejado": "descanso",
  Gliricídia: "gliricídia" };
const FEM = new Set(["Mandioca", "Palma forrageira", "Mamona", "Banana", "Cana-de-açúcar", "Mucuna-preta", "Gliricídia"]);
const fala = (n) => FALA[n] || String(n || "").toLowerCase();
const com = (n) => `${FEM.has(n) ? "a" : "o"} ${fala(n)}`;
const de_ = (n) => `${FEM.has(n) ? "da" : "do"} ${fala(n)}`;
const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);
const lista = (xs) => (xs.length <= 1 ? xs.join("") : `${xs.slice(0, -1).join(", ")} e ${xs[xs.length - 1]}`);
const nomesDoTexto = (c) => String(c || "").split(/\s*\+\s*/).map((x) => (/^palma$/i.test(x) ? "Palma forrageira" : /^gliric/i.test(x) ? "Gliricídia" : x));

/** Os textos das células, dos "por quê" e das notas (do núcleo e deste motor) com as palavras da roça, só na hora de mostrar (os
 *  textos de máquina não mudam: desenho, agenda e material leem "revezamento", "solteiro"…). Lista das trocas: revisão R1/R3, 15/11. */
const FALA_TEXTO = [
  [/\s*\((?:ZARC|Port\.)[^)]*\)/g, ""],
  [/\(\+24% no ano colhido, contra cereal solteiro\)/g, "(rende uns 24% a mais)"],
  [/Leguminosa antes do cereal: o cereal seguinte rende ~24% a mais no ano colhido, contra cereal solteiro\./g, "Milho depois do feijão rende uns 24% a mais."],
  [/Sem mandioca apta aqui: falta o tampão\./g, "Aqui a mandioca não vai bem."],
  [/Sem leguminosa de grão no cardápio deste lugar: o plano não tem a rotação leguminosa → cereal\./g, "Aqui não há feijão com data segura: o plano não reveza feijão e milho."],
  [/Sem leguminosa no cardápio: sem rotação leguminosa → cereal\./g, "Aqui não há feijão com data segura para revezar."],
  [/sem leguminosa no cardápio: sem revezamento/g, "sem feijão com data segura aqui: fica sozinho"],
  [/sem leguminosa no cardápio/g, "sem feijão com data segura aqui"],
  [/depois da leguminosa/g, "depois do feijão"], [/da leguminosa/g, "do feijão"], [/a leguminosa/g, "o feijão"], [/leguminosas?/g, "feijão"],
  [/\+ feijão-caupi em revezamento/g, "+ feijão no meio do milho"], [/\+ feijão em revezamento/g, "+ feijão no meio do milho"],
  [/\bcereal solteiro\b/g, "milho sozinho"], [/\bsolteiro\b/g, "sozinho"], [/o cereal seguinte/g, "o milho seguinte"], [/\bcereal\b/g, "milho"],
  [/caupi precoce/g, "feijão de ciclo curto"], [/\bprecoce\b/g, "de ciclo curto"],
  [/o tampão/g, "a reserva"], [/tampão/g, "reserva"],
  [/só cabe salvar/g, "salve o que der"], [/fenação do excedente/g, "feno do que sobrar"],
  [/metade guardada até/g, "metade da semente guardada até"], [/\s*→\s*/g, " depois "], [/kg de N\b/g, "kg de adubo (nitrogênio)"],
];
export const falaTexto = (s) => FALA_TEXTO.reduce((a, [re, b]) => a.replace(re, b), String(s || "")).replace(/\s{2,}/g, " ").trim();

/** A mandioca que ele marcou em "O que planta hoje?" já está no chão, qualquer que seja a resposta da maniva (revisão R1, 15/11);
 *  "Já está plantada" também. A maniva decide só a mandioca NOVA: "Não tenho" = não planta mais (a do chão colhe e não replanta). */
const mandNoChao = (h, ef) => (h.informado && (h.cult.mandioca || 0) > 0) || ef?.maniva === "plantada";
/** A parte que recebe a mandioca velha (sem rama para replantar): a última cujo 1º ano repete o de outra parte; senão, a última. */
function parteDaVelha(linhas) {
  for (let i = linhas.length - 1; i >= 0; i--) if (linhas.some((x, j) => j !== i && x[0].cultura === linhas[i][0].cultura)) return i;
  return linhas.length - 1;
}
const celVelha = () => ({ cultura: "Mandioca", tipo: "tampão", ja_no_chao: true, velha: true,
  texto: "já está no chão: colhe em 2027; sem rama, não replanta" });
// solo da resposta de Terra → o código do ZARC (o mesmo de roca.js: arenosa AD2, mista AD3, barro AD5)
const SOLO_RESP = { arenosa: 12, mista: 13, barro: 15 };
/** O risco do ZARC da cultura no solo que ele respondeu (cardapio[].por_solo); null = terra "não sei" ou sem a linha do solo. */
function riscoNoSolo(card, nome, terra) {
  const cod = SOLO_RESP[terra], c = card.get(nome);
  if (!cod || !Array.isArray(c?.por_solo)) return null;
  return c.por_solo.find((s) => +s.cod_solo === cod) || null;
}
const temJanela = (x) => !!x && x !== "nenhum";

// ------------------------------------------------------------------ memória (as telas pedem os mesmos números várias vezes)
let MEMO = new WeakMap(), MEMO_P = new WeakMap();
function memo(r, nome, chave, fn) {
  let m = MEMO.get(r);
  if (!m) MEMO.set(r, (m = new Map()));
  const k = `${nome}|${chave}`;
  if (!m.has(k)) m.set(k, fn());
  return m.get(k);
}
function memoP(plano, chave, fn) {
  let m = MEMO_P.get(plano);
  if (!m) MEMO_P.set(plano, (m = new Map()));
  if (!m.has(chave)) m.set(chave, fn());
  return m.get(chave);
}
const chaveDe = (resp, ef) => JSON.stringify([resp?.hoje || "", resp?.antes || "", resp?.prioridade || "", ef?.ha, ef?.tem_baixio, ef?.baixio_frac,
  ef?.baixio_ha, ef?.maniva, ef?.raiz, ef?.custo, ef?.prioridade, ef?.larg, ef?.comp, ef?.terra]);

// ------------------------------------------------------------------ datas (dia em ms UTC, como o date do Python)
const DIA = 864e5;
const MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
const p2 = (v) => String(v).padStart(2, "0");
const deISO = (s) => { const [a, m, d] = String(s).split("-").map(Number); return Date.UTC(a, m - 1, d); };
const deBR = (s) => { const [d, m, a] = String(s).split("/").map(Number); return Date.UTC(a, m - 1, d); };
const iso = (t) => new Date(t).toISOString().slice(0, 10);
const dmy = (t) => { const x = new Date(t); return `${p2(x.getUTCDate())}/${p2(x.getUTCMonth() + 1)}/${x.getUTCFullYear()}`; };
const dm = (t) => dmy(t).slice(0, 5);
const mesAno = (t) => { const x = new Date(t); return `${MES[x.getUTCMonth()]}/${x.getUTCFullYear()}`; };
const maisAnos = (t, n) => { if (t == null || !n) return t; const x = new Date(t); return Date.UTC(x.getUTCFullYear() + n, x.getUTCMonth(), x.getUTCDate()); };

/** Janela de plantio do ZARC da cultura (r.agenda.culturas[].plantar), estação 2027: { ini, fim, ext_ini, ext_fim, zarc, fonte }. */
function janela(r, nome) {
  return memo(r, "jan", nome, () => {
    const c = (r.agenda?.culturas || []).find((x) => x.cultura === nome);
    if (!c) return null;
    const m = /de (\d{2}\/\d{2}\/\d{4}) a (\d{2}\/\d{2}\/\d{4})/.exec(c.plantar || "");
    if (!m) return { semData: true, plantar: c.plantar, colher: c.colher, fonte: c.fonte, situacao: c.situacao };
    const ini = deBR(m[1]), fim = deBR(m[2]);
    const par = /\(com mais risco, ([^)]*)\)/.exec(c.plantar)?.[1] || "";
    const de = /desde (\d{2})\/(\d{2})/.exec(par), ate = /até (\d{2})\/(\d{2})/.exec(par);
    let ext_ini = null, ext_fim = null;
    if (de) { const y = new Date(ini).getUTCFullYear(); ext_ini = Date.UTC(y, +de[2] - 1, +de[1]); if (ext_ini > ini) ext_ini = Date.UTC(y - 1, +de[2] - 1, +de[1]); }
    if (ate) { const y = new Date(fim).getUTCFullYear(); ext_fim = Date.UTC(y, +ate[2] - 1, +ate[1]); if (ext_fim < fim) ext_fim = Date.UTC(y + 1, +ate[2] - 1, +ate[1]); }
    return { ini, fim, ext_ini, ext_fim, zarc: !/^estimado/.test(c.fonte || ""), fonte: c.fonte, plantar: c.plantar, colher: c.colher, situacao: c.situacao };
  });
}
const txtPlantio = (r, nome) => {
  const J = janela(r, nome) || janelaEstimada(r, nome);
  return J && !J.semData ? `plantio de ${dm(J.ini)} a ${dm(J.fim)}${J.zarc ? "" : " (estimado)"}` : "sem data segura aqui";
};
const txtManiva = (r) => {
  const J = janela(r, "Mandioca");
  return J && !J.semData ? `maniva de ${dm(J.ini)} a ${dm(J.fim)}${J.zarc ? " (ZARC)" : " (estimado)"}` : "maniva no começo da chuva";
};

// ------------------------------------------------------------------ prioridade e ano passado
const alertaDe = (r) => r?.este_ano?.nivel_alerta === "alerta";
/** A prioridade que vale: a resposta; sem ela, a escolhida pelos números (escolhaPadrao). ef.prioridade só vale quando é resposta
 *  (roca.js põe "garantir" em ano de alerta mesmo sem resposta). */
export function prioridadePadrao(r, resp = {}, ef = {}) {
  if (PRIORIDADES.includes(resp?.prioridade)) return resp.prioridade;
  if (ef?.prioridade_origem === "resposta" && PRIORIDADES.includes(ef?.prioridade)) return ef.prioridade;
  return escolhaPadrao(r, resp, ef).prioridade;
}

/**
 * A prioridade padrão pelos números (revisão R1, 15/11: "validar que já estamos dando o melhor para a pessoa"): nunca abre numa
 * prioridade que perde para outra nos 3 números de R$ e quebra (ano normal, 2027 e anos de quebra). Em ano de alerta de El Niño
 * (2027 é), vale a que mais sobra em 2027 (diferença de até R$ 50 = empate, decide o ano normal); fora dele, "Um pouco de cada"
 * se ninguém a vence, senão a que mais sobra num ano normal. Sem R$ aqui, a regra antiga (alerta → "Guardar água").
 * → { prioridade, motivo: "numeros" | "regra", cand: [{ p, t, e, q }] }
 */
export function escolhaPadrao(r, resp = {}, ef = {}) {
  const base = alertaDe(r) ? "garantir" : "equilibrar";
  if (!r?.plano?.faixas?.length) return { prioridade: base, motivo: "regra", cand: [] };
  return memo(r, "pri", chaveDe({ ...resp, prioridade: "" }, { ...ef, prioridade: "" }), () => {
    const v = (b, id) => b?.itens?.find((i) => i.id === id)?.valor ?? null;
    const cand = PRIORIDADES.map((p) => {
      const pl = planoIdeal(r, resp, ef, p), b = pl ? beneficios(r, resp, ef, pl, "ideal") : null;
      return { p, t: v(b, "rs_tipico"), e: v(b, "rs_el_nino"), q: v(b, "quebra_10") };
    });
    const com = cand.filter((c) => c.t != null && c.e != null);
    if (!com.length) return { prioridade: base, motivo: "regra", cand };
    const qq = (c) => c.q ?? 99;
    const vence = (a, b) => a.t >= b.t && a.e >= b.e && qq(a) <= qq(b) && (a.t > b.t || a.e > b.e || qq(a) < qq(b));
    const livres = com.filter((c) => !com.some((o) => o !== c && vence(o, c)));
    let pick;
    if (alertaDe(r)) {
      const maxE = Math.max(...livres.map((c) => c.e));
      pick = livres.filter((c) => c.e >= maxE - 50).sort((a, b) => b.t - a.t || qq(a) - qq(b) || (a.p === base ? -1 : b.p === base ? 1 : 0))[0];
    } else pick = livres.find((c) => c.p === base) || [...livres].sort((a, b) => b.t - a.t || b.e - a.e)[0];
    return { prioridade: pick.p, motivo: "numeros", cand };
  });
}

/** O chão nos 2 anos antes do plano: o ano do jeito de hoje (2026 = `hoje`, salvo se `antes` escrever 2026) e o ano passado
 *  (`antes` = "2025:milho,feijao", o formato de extras/historico.js). Só a repetição nos 2 anos muda por onde as partes começam:
 *  gramínea 2 anos seguidos (milho, sorgo, milheto) → a parte começa sem gramínea; senão, leguminosa 2 anos → começa sem ela. */
function lerAntes(r, resp) {
  const anos = {};
  for (const parte of String(resp?.antes || "").split("|")) {
    const [a, cs] = parte.split(":");
    if (/^\d{4}$/.test(a || "") && cs) anos[+a] = cs.split(",").map((s) => s.trim()).filter(Boolean);
  }
  const a1 = (r?.plano?.anos?.[0] || 2027) - 1, a2 = a1 - 1;
  if (!anos[a2] && !anos[a1]) return null;
  const nomes = (ks) => [...new Set(ks.map((k) => CULT[k]?.motor).filter(Boolean))];
  const h = lerHoje(resp?.hoje || "", r?.padroes);
  const y1 = anos[a1] ? nomes(anos[a1]) : nomes(Object.keys(h.cult));
  const y2 = anos[a2] ? nomes(anos[a2]) : [];
  const desc = (anos[a2] || []).includes("pousio");
  const gram = y1.find(ehGram) && y2.find(ehGram) ? y1.find(ehGram) : null;
  const leg = !gram && y1.find((n) => LEG.has(n)) && y2.find((n) => LEG.has(n)) ? y1.find((n) => LEG.has(n)) : null;
  const iguais = y1.filter((n) => y2.includes(n) && !ehGram(n) && !LEG.has(n)); // mandioca, algodão… dois anos no mesmo chão
  return { a1, a2, y1, y2, descansou: desc, gram, leg, iguais, repetiu: !!(gram || leg || iguais.length) };
}

/** A cultura do 1º ano repete o chão dos 2 anos anteriores? Devolve a cultura repetida (para o "por quê") ou null. */
function repeteAntes(c, A) {
  if (!A?.repetiu || !c || c.ja_no_chao || c.ja_plantado || c.tipo === "perene" || c.tipo === "pousio") return null;
  if (A.gram && ehGram(c.cultura)) return A.gram;
  if (A.leg && LEG.has(c.cultura)) return A.leg;
  if (A.iguais.includes(c.cultura)) return c.cultura;
  return null;
}
const limpar = (c, r) => {
  const x = { ...c };
  if (x.ja_no_chao) { delete x.ja_no_chao; x.texto = txtManiva(r); }
  x.texto = String(x.texto || "").replace(/; metade guardada até ~10\/mar/, "");
  return x;
};

/** O ano passado decide por onde cada parte começa: na parte cujo 1º ano repetiria o chão, só o 1º ano troca por uma planta do
 *  próprio plano que não repete (depois de gramínea, a leguminosa: "a terra repetiu milho, comece com o feijão nesse lugar"; depois
 *  de leguminosa, o cereal), sem gramínea atrás de gramínea no ano seguinte; o resto do giro fica igual (a mandioca não se perde).
 *  Sem planta que sirva, copia o giro de uma parte que não repete. */
function ajustarAntes(p, A, r) {
  if (!A?.repetiu) return p;
  const partes = p.faixas.filter((f) => /^Parte /.test(f.parte));
  const ruins = partes.filter((f) => repeteAntes(f.anos[0], A)), bons = partes.filter((f) => !repeteAntes(f.anos[0], A));
  if (!ruins.length) return p;
  const pap = (c) => (c.tipo === "tampão" ? "M" : papel(c.cultura));
  const plantas = [...new Set(p.faixas.filter((f) => /^Parte |^Baixio/.test(f.parte)).flatMap((q) => q.anos)
    .filter((c) => c.tipo !== "tampão" && c.tipo !== "perene" && c.tipo !== "pousio" && !repeteAntes(c, A)).map((c) => c.cultura))];
  const nova = new Map();
  for (const f of ruins) {
    const x = repeteAntes(f.anos[0], A), seg = f.anos[1];
    const quer = ehGram(x) ? ["L", "X"] : LEG.has(x) ? ["X", "L"] : ["L", "X"];
    const cand = plantas.filter((n) => n !== seg?.cultura && !(ehGram(n) && ehGram(seg?.cultura)))
      .sort((a, b) => quer.indexOf(papel(a)) - quer.indexOf(papel(b)) || (CEREAL.has(b) - CEREAL.has(a)));
    let anos = null;
    // a mandioca do 1º ano não troca sozinha (o 2º ano é a colheita dela): aí copia o giro de outra parte
    if (cand.length && f.anos[0].tipo !== "tampão") {
      const n0 = cand[0];
      anos = [{ cultura: n0, tipo: TIPO[n0] || "pousio", texto: (LEG.has(x) && CEREAL.has(n0) ? `depois ${de_(x)} rende uns 24% a mais; ` : "") + txtPlantio(r, n0) },
        ...f.anos.slice(1).map((c) => limpar(c, r))];
    } else if (!LEG.has(x)) { // feijão repetido sem outra planta para trocar: fica (não vira mandioca no roçado todo)
      const quer2 = ehGram(x) ? ["L", "M", "X", "P", "O"] : ["X", "M", "L", "P", "O"];
      const outro = [...bons].sort((a, b) => quer2.indexOf(pap(a.anos[0])) - quer2.indexOf(pap(b.anos[0])))[0];
      if (outro) anos = outro.anos.map((c) => limpar(c, r));
    }
    if (anos) nova.set(f.parte, { anos, x });
  }
  if (!nova.size) return p;
  const quando = A.y2.length ? `${A.a2} e ${A.a1}` : "dois anos seguidos";
  const faixas = p.faixas.map((f) => {
    const n = nova.get(f.parte);
    if (!n) return f;
    // no ano passado, outra da mesma família (sorgo ou milheto antes do milho, amendoim antes do feijão): diz cada ano com o seu nome
    const x2 = A.y2.includes(n.x) ? n.x : A.y2.find((m) => (ehGram(n.x) ? ehGram(m) : LEG.has(n.x) && LEG.has(m)));
    const teve = x2 && x2 !== n.x ? `${fala(x2)} em ${A.a2} e ${fala(n.x)} em ${A.a1}` : `${fala(n.x)} em ${quando}`;
    return { ...f, anos: n.anos, antes: n.x,
      por_que: `Começa com ${com(n.anos[0].cultura)}: ali teve ${teve}. ${porQueLinha(n.anos)}` };
  });
  const out = { ...p, faixas, antes_ajuste: [...nova.entries()].map(([parte, n]) => ({ parte, repetiu: n.x, comeca: n.anos[0].cultura })) };
  if (p.por_que_de) out.por_que_de = { ...p.por_que_de, ...Object.fromEntries(faixas.filter((f) => nova.has(f.parte)).map((f) => [f.parte, f.por_que])) };
  return out;
}

/** O que ele planta hoje e fica fora do giro (as perenes já plantadas: caju, banana, cana, palma, gliricídia, guandu): a área delas
 *  não vira roça nova em nenhum plano. A "outra" entra no giro (a lista já tem todas as perenes: "outra" é uma anual que não está nela).
 *  → { fora_do_giro: [{ chave, cultura, ha }], ha_giro } (sem `hoje` informado, nada fica fora). */
function foraDoGiro(r, resp, ef) {
  const h = lerHoje(resp?.hoje || "", r?.padroes), A = areasHoje(h, ef);
  const fora = !h.informado ? [] : Object.entries(A.ha).filter(([k, v]) => v > 0 && PERENE.has(CULT[k]?.motor))
    .map(([k, v]) => ({ chave: k, cultura: CULT[k]?.motor || null, ha: v }));
  return { fora_do_giro: fora, ha_giro: Math.max(0, Math.round((ef.ha - fora.reduce((s, x) => s + x.ha, 0)) * 100) / 100) };
}
/** As respostas efetivas com a área do giro (ha_giro) no lugar do roçado inteiro, para a conta de cada plano. */
const efDoGiro = (ef, plano) => (plano?.ha_giro != null && plano.ha_giro < ef.ha
  ? { ...ef, ha: plano.ha_giro, baixio_ha: Math.min(ef.baixio_ha ?? plano.ha_giro / 3, plano.ha_giro) } : ef);

// ------------------------------------------------------------------ o "por quê" curto de cada faixa
function porQueLinha(anos) {
  const [a, b] = anos;
  const pa = a.tipo === "tampão" ? "M" : papel(a.cultura), pb = b ? (b.tipo === "tampão" ? "M" : papel(b.cultura)) : null;
  if (a.velha) return `A sua mandioca colhe aqui em 2027; depois, ${b && b.cultura !== "Mandioca" ? com(b.cultura) : "o giro"}.`;
  if (a.ja_no_chao && a.m2) return "A sua mandioca colhe aqui em 2027; a maniva nova entra em 2028.";
  if (a.ja_no_chao) return "A sua mandioca já está aqui: é a reserva de 2027.";
  if (a.ja_plantado) return "Perene: fica no lugar, não entra no giro.";
  if (pa === "M") return "Mandioca de reserva: se o ano seguinte vier ruim, ela ainda está no chão.";
  if (pa === "L" && b && ehGram(b.cultura)) return `${cap(com(a.cultura))} primeiro: deixa adubo para ${com(b.cultura)} do ano seguinte.`;
  if (pa === "L" && pb === "M") return `${cap(com(a.cultura))} agora; depois, a mandioca de reserva.`;
  if (pa === "L") return `${cap(com(a.cultura))} deixa adubo na terra para o ano seguinte.`;
  if (pa === "P") return a.cultura === "Palma forrageira" ? "Palma em nível: comida do gado na seca." : `${cap(fala(a.cultura))}: adubo e comida do gado.`;
  if (pa === "O") return "Descanso: a terra se refaz e o gado pasteja.";
  if (pb === "M") return `${cap(com(a.cultura))} agora; depois, a mandioca de reserva.`;
  if (pb === "L") return `${cap(com(a.cultura))} agora; no ano seguinte, ${com(b.cultura)} no lugar.`;
  if (a.tipo === "forragem") return `${cap(com(a.cultura))} para o gado; palhada sem fogo.`;
  return "Cada ano uma planta diferente neste chão.";
}
function porQueBaixio(anos, leg) {
  const c0 = anos[0].cultura, outros = [...new Set(anos.map((c) => c.cultura).filter((c) => c !== c0))];
  let s = `A parte mais baixa guarda mais água: ${com(c0)} fica aqui`;
  if (outros.length) s += `, com um ano de ${lista(outros.map(fala))} no meio.`;
  else s += ".";
  if (anos.some((c) => c.mucuna)) s += " A mucuna entra no milho em pé e cobre o chão.";
  else if (leg && CEREAL.has(c0) && anos.some((c) => /revezamento/.test(c.texto || ""))) s += ` ${cap(com(leg))} entra no meio, com ${com(c0)} em pé.`;
  else if (CEREAL.has(c0) && !outros.length) s += " Sem feijão para revezar, ele repete aqui.";
  return s;
}

// ------------------------------------------------------------------ "Seu jeito, melhorado"
/**
 * O melhor sistema só com as culturas que ele marcou (CULT[k].motor; "outra" fica de fora): giro A/B/C em que nada repete no mesmo
 * chão (a mandioca fica 2 anos), leguminosa antes do cereal, o cereal no baixio quando houver (com o feijão em revezamento), a
 * mandioca de tampão (sem maniva, sai), as perenes nas bordas; o ano passado decide por onde cada parte começa (ajustarAntes).
 * Mesmo desenho do giro do núcleo: com mandioca, leguminosa e cereal, A: M M L · B: L X M · C: X M M (o X do núcleo é a forragem).
 * Campos além do formato de r.plano: tipo "melhor", culturas, acrescenta (o que o ideal põe a mais), nao_gira, avisos[{id, cultura, txt}].
 */
export function planoMelhor(r, resp = {}, ef = {}) {
  if (!r?.plano?.faixas?.length) return null;
  return memo(r, "melhor", chaveDe(resp, ef), () => fazerMelhor(r, resp, ef));
}

function fazerMelhor(r, resp, ef) {
  const base = r.plano, anosP = base.anos || [2027, 2028, 2029];
  const h = lerHoje(resp?.hoje || "", r.padroes);
  const card = new Map((r.cardapio || []).map((c) => [c.cultura, c]));
  const peso = new Map();
  for (const [k, p] of Object.entries(h.cult)) { const n = CULT[k]?.motor; if (n) peso.set(n, (peso.get(n) || 0) + p); }
  const notas = [], avisos = [];
  const semCultura = !peso.size;
  if (semCultura) { peso.set("Milho", 50); peso.set("Feijão-caupi", 50); notas.push("Sem cultura conhecida no que você marcou: o giro usa milho e feijão, o mais comum daqui."); }
  if (h.cult.outra) notas.push("A \"outra\" cultura fica fora do giro: combine com o técnico onde ela entra.");
  let nomes = [...peso.keys()].sort((a, b) => peso.get(b) - peso.get(a));
  // a mandioca marcada já está no chão; "Não tenho" maniva = não planta mais: a do chão colhe em 2027 numa parte e sai do giro
  const noChao = mandNoChao(h, ef);
  let velha = false;
  if (nomes.includes("Mandioca") && ef.maniva === "nao") {
    nomes = nomes.filter((n) => n !== "Mandioca");
    velha = noChao;
    avisos.push({ id: "maniva", cultura: "Mandioca", txt: noChao ? "Sem maniva para plantar mais: a sua mandioca colhe em 2027 e depois a parte dela entra no giro."
      : "Sem maniva: a mandioca sai do plano até você conseguir rama." });
    if (!nomes.some((x) => papel(x) !== "P")) { // sem outra planta que gire: o comum daqui
      for (const x of ["Milho", "Feijão-caupi"]) { peso.set(x, 50); nomes.push(x); }
      notas.push("Sem rama para plantar mais mandioca: o giro usa milho e feijão, o mais comum daqui.");
    }
  }
  for (const n of nomes) {
    const c = card.get(n);
    if (!c || c.situacao === "fora") avisos.push({ id: "fora", cultura: n, txt: `${cap(com(n))} não tem data segura aqui: mais risco de perder.` });
  }
  const fora = new Set(avisos.filter((a) => a.id === "fora").map((a) => a.cultura));
  // nunca uma cultura sozinha (pedido do José, 15/11): com uma anual só (ou só perene), entra a do lugar que gira com ela: a
  // leguminosa (r.plano.leguminosa ou a 1ª que serve no cardápio) e, se a dele já é feijão (ou só perene), o cereal
  const serve = (x) => { const c = card.get(x); return !!c && c.situacao !== "fora"; };
  const legLugar = [base.leguminosa, "Feijão-caupi", "Feijão comum", "Amendoim"].find((x) => x && x !== "Mucuna-preta" && LEG.has(x) && serve(x)) || null;
  const cerLugar = ["Milho", "Sorgo granífero", "Milheto"].find(serve) || null;
  const entrou = [], anuais0 = nomes.filter((x) => papel(x) !== "P");
  if (anuais0.length <= 1) {
    const temL = anuais0.some((x) => LEG.has(x));
    for (const x of [temL ? null : legLugar, temL || !anuais0.length ? cerLugar : null]) if (x && !nomes.includes(x)) { entrou.push(x); nomes.push(x); peso.set(x, 1); }
  }
  const L = nomes.filter((n) => papel(n) === "L"), P = nomes.filter((n) => papel(n) === "P");
  let X = nomes.filter((n) => papel(n) === "X").sort((a, b) => rank(a) - rank(b) || peso.get(b) - peso.get(a));
  const M = nomes.includes("Mandioca");
  const temBx = ef.tem_baixio !== false && base.faixas.some((f) => f.parte === "Baixio");
  const bxCult = temBx ? ["Milho", "Sorgo granífero", "Sorgo forrageiro", "Milheto"].find((n) => nomes.includes(n)) || null : null;
  // a terra que ele respondeu sem janela de 20% nem de 30% para o milho (ex.: Picos na areia, AD2): o milho só no baixio, como no núcleo
  const rsMilho = riscoNoSolo(card, "Milho", ef.terra);
  const milhoSolo = !!rsMilho && X.includes("Milho") && !temJanela(rsMilho.risco20) && !temJanela(rsMilho.risco30);
  // (só quando a terra alta continua girando sem ele: feijão e mandioca, ou outro cereal; senão o milho fica, com o aviso)
  const milhoSoBaixio = milhoSolo && bxCult === "Milho" && (L.length ? 1 : 0) + (M ? 2 : 0) + (X.length > 1 ? 1 : 0) >= 2;
  if (milhoSoBaixio) X = X.filter((x) => x !== "Milho");
  // milho só no baixio e só a mandioca na terra alta (ex.: milho + mandioca na areia): entra a leguminosa do lugar no giro das
  // partes, para a terra alta não ficar os 3 anos só de mandioca (auditoria a8, 15/11)
  let girarCom = anuais0[0];
  if (milhoSoBaixio && M && !L.length && !X.length && legLugar && !nomes.includes(legLugar)) {
    entrou.push(legLugar); nomes.push(legLugar); peso.set(legLugar, 1); L.push(legLugar); girarCom = "Mandioca";
  }
  const legMain = L.find((n) => n !== "Mucuna-preta") || null;
  // o cereal do baixio sem feijão dele para revezar: entra o feijão do lugar no milho em pé (o baixio não fica 3 anos só no cereal)
  const legBx = legMain || (bxCult && CEREAL.has(bxCult) ? legLugar : null);
  const relay = !!(bxCult && legBx && CEREAL.has(bxCult));
  const anuais = nomes.filter((n) => papel(n) !== "P");
  const naoGira = anuais.length <= 1;

  // o giro da terra alta: [M1 M2] + L + X; cada parte começa num ponto do giro (nunca no 2º ano da mandioca)
  const cyc = [...(M ? ["M1", "M2"] : []), ...(L.length ? ["L"] : []), ...(X.length ? ["X"] : [])];
  if (!cyc.length) cyc.push("P"); // só perenes: não há giro
  const n = cyc.length;
  // só mandioca (M1 M2): as partes desencontram (A e C plantam em 2027, B colhe em 2027 a que já está no chão), para todo ano ter
  // colheita, como o "metade colhe, metade planta" do jeito de hoje; nos outros giros, nenhuma parte começa no 2º ano da mandioca
  const soM = n === 2 && cyc[0] === "M1";
  // mandioca + uma planta, sem cereal no baixio: a C começa colhendo a mandioca do chão, para nenhum ano ser só mandioca
  const tresM = n === 3 && cyc[0] === "M1" && !bxCult;
  const offs = soM ? [0, 1, 0] : tresM ? [0, 2, 1] : ({ 4: [0, 2, 3], 3: [0, 2, 2], 2: [0, 1, 0], 1: [0, 0, 0] }[n]).map((o) => (cyc[o] === "M2" ? 0 : o));
  const conta = { L: 0, X: 0 };
  const escolher = (papelC, lst, nomeAnt, depoisDeL) => {
    const i0 = conta[papelC]++ % lst.length;
    let roda = [...lst.slice(i0), ...lst.slice(0, i0)];
    if (depoisDeL) roda = [...roda.filter((x) => CEREAL.has(x)), ...roda.filter((x) => !CEREAL.has(x))]; // cereal depois da leguminosa
    return roda.find((x) => x !== nomeAnt && !(ehGram(x) && ehGram(nomeAnt))) || roda.find((x) => x !== nomeAnt) || roda[0];
  };
  const milhoRisco = card.get("Milho")?.situacao === "com risco" && !milhoSoBaixio;
  const linhas = offs.map((o) => {
    let pAnt = null, nAnt = null;
    return [0, 1, 2].map((k) => {
      const pc = cyc[(o + k) % n];
      // só mandioca: a parte que começa no 2º ano colhe em 2027 a mandioca do chão (sem ela no chão, descansa em 2027)
      if (k === 0 && pc === "M2") {
        pAnt = pc; nAnt = "Mandioca";
        return noChao ? { cultura: "Mandioca", tipo: "tampão", ja_no_chao: true, m2: true, texto: "já está no chão: colhe em 2027 conforme a necessidade" }
          : { cultura: "Pousio pastejado", tipo: "pousio", texto: "descanso em 2027: a maniva entra em 2028" };
      }
      const nome = pc === "M1" || pc === "M2" ? "Mandioca" : pc === "L" ? escolher("L", L, nAnt, false) : pc === "X" ? escolher("X", X, nAnt, pAnt === "L") : P[0];
      let texto;
      if (pc === "M1") texto = txtManiva(r);
      else if (pc === "M2") texto = "reserva: colhe conforme a necessidade";
      else if (pc === "L") texto = (pAnt === "M2" ? "na terra que foi mandioca; " : "") + txtPlantio(r, nome);
      else if (pc === "X") texto = (pAnt === "L" && CEREAL.has(nome) ? `depois ${de_(nAnt)} rende uns 24% a mais; ` : "") + txtPlantio(r, nome)
        + (nome === "Milho" && milhoRisco ? "; na terra alta, mais risco aqui" : "");
      else texto = k ? "permanece" : "já plantado: fica onde está";
      // cultura fora do zoneamento: r.agenda.culturas não tem a janela dela, e txtPlantio já diz "sem data segura aqui"
      const cel = { cultura: nome, tipo: TIPO[nome] || "pousio", texto, ...(fora.has(nome) ? { fora: true } : {}) };
      if (pc === "P") cel.ja_plantado = true;
      pAnt = pc; nAnt = nome;
      return cel;
    });
  });
  // a mandioca que já está no chão é a da 1ª parte que começa com mandioca (como no núcleo): colhe em 2027 e a rama replanta
  if (M && noChao) {
    const l = linhas.find((x) => x[0].cultura === "Mandioca" && !x[0].ja_no_chao);
    if (l) Object.assign(l[0], { ja_no_chao: true, texto: "já está no chão: colhe em 2027 conforme a necessidade (reserva)" });
  }
  // sem rama para plantar mais: a mandioca do chão colhe em 2027 numa parte e não replanta (a parte segue o giro em 2028)
  if (velha) { const i = parteDaVelha(linhas); linhas[i][0] = celVelha(); }
  // ano de alerta com portões (o núcleo pôs a metade guardada no interruptor): na 1ª parte que começa com a leguminosa
  const metade = /metade/.test(base.interruptor || "") && legMain;
  let parteMetade = null;
  if (metade) {
    const i = linhas.findIndex((x) => x[0].cultura === legMain);
    if (i >= 0) { linhas[i][0].texto += "; metade guardada até ~10/mar"; parteMetade = `Parte ${"ABC"[i]}`; }
  }

  const faixas = linhas.map((anos, i) => ({ parte: `Parte ${"ABC"[i]}`, por_que: porQueLinha(anos), anos }));
  if (bxCult) {
    const texto = relay ? `+ ${fala(legBx)} em revezamento (50–85 dias depois); as linhas trocam de lugar`
      : CEREAL.has(bxCult) ? `${txtPlantio(r, bxCult)}; sem feijão para revezar` : "forragem; palhada sem fogo";
    const anos = [0, 1, 2].map(() => ({ cultura: bxCult, tipo: TIPO[bxCult], texto }));
    // sem revezamento (forragem, ou sem feijão aqui): um ano de outra planta do giro no meio, para o baixio não repetir 3 anos
    const meio = relay ? null : [legMain, ...nomes.filter((x) => !ehGram(x)), ...nomes].find((x) => x && x !== bxCult && x !== "Mandioca" && papel(x) !== "P");
    if (meio) anos[1] = { cultura: meio, tipo: TIPO[meio] || "pousio", texto: txtPlantio(r, meio) };
    faixas.push({ parte: "Baixio", por_que: porQueBaixio(anos, relay ? legBx : null), anos });
  }
  // as perenes que ele já tem ficam no pedaço delas (fora_do_giro, desenhado em escala por desenho.montar), não na cerca; só sem
  // nenhuma anual (o roçado todo é perene) a 1ª vai nas partes e as outras nas bordas
  const perBordas = cyc[0] === "P" ? P.slice(1) : !anuais0.length ? P : []; // só perene: ela fica nas bordas, a anual que entrou gira
  if (perBordas.length) {
    const nome = perBordas.join(" + ");
    faixas.push({ parte: "Bordas", anos: [0, 1, 2].map((k) => ({ cultura: nome, tipo: "perene", texto: k ? "permanece" : "já plantado: fica onde está", ja_plantado: true })),
      por_que: `Perene: fica no lugar, nas bordas${perBordas.some((x) => x === "Banana" || x === "Cana-de-açúcar") && temBx ? "; banana e cana pedem a beira do baixio" : ""}.` });
  }
  const bxEntrou = relay && !legMain ? legBx : null;
  let plano = { anos: anosP, faixas, notas, avisos, principios: base.principios, leguminosa: legBx, modelo_ne: base.modelo_ne,
    interruptor: parteMetade ? `Alerta para 2027: na ${parteMetade}, metade ${de_(legMain)} fica guardada até ~10/mar.`
      : alertaDe(r) ? "Alerta para 2027: plante escalonado, não tudo no mesmo dia." : null,
    tipo: "melhor", nome: "Seu jeito, melhorado", culturas: nomes, entrou: [...entrou, ...(bxEntrou ? [bxEntrou] : [])], nao_gira: naoGira,
    mand_no_chao: noChao, ...foraDoGiro(r, resp, ef) };
  plano = ajustarAntes(plano, lerAntes(r, resp), r);
  // o ano passado pode pôr todas as partes no mesmo giro (milho dois anos em todo o chão, só milho e feijão, sem baixio): a parte
  // trocada ganha a mandioca (sem rama, outra leguminosa), para nenhum ano ficar com uma planta só no roçado
  const umaSo = (fx) => [0, 1, 2].some((k) => new Set(fx.filter((f) => /^Parte |^Baixio/.test(f.parte)).map((f) => f.anos[k]).filter((c) => c.tipo !== "pousio")
    .flatMap((c) => [c.cultura, ...(/revezamento/.test(c.texto || "") ? ["+"] : [])])).size < 2);
  let antesEntrou = null;
  if (plano.antes_ajuste && umaSo(plano.faixas)) {
    // a mandioca primeiro; se ela não resolve (milho + mandioca sem baixio: a mandioca já é a única planta de 2027), a leguminosa
    // (a do lugar quando o plano não tem nenhuma; senão outra), a 1ª que tira o ano de uma planta só (auditoria a8, 15/11)
    const legs = ["Amendoim", "Feijão comum", "Feijão-caupi"], temLeg = nomes.some((y) => LEG.has(y));
    const xs = [ef.maniva !== "nao" && serve("Mandioca") ? "Mandioca" : null,
      ...[...new Set([...(temLeg ? [] : [legLugar]), ...legs])].filter((y) => y && serve(y) && !nomes.includes(y))].filter(Boolean);
    const i = plano.faixas.findIndex((f) => f.parte === plano.antes_ajuste[plano.antes_ajuste.length - 1].parte);
    const outro = plano.faixas.find((f, j) => j !== i && /^Parte /.test(f.parte));
    let achou = null;
    for (const x of i >= 0 && outro ? xs : []) {
      const anos = x === "Mandioca" ? [{ cultura: x, tipo: TIPO[x], texto: txtManiva(r) }, { cultura: x, tipo: TIPO[x], texto: "reserva: colhe conforme a necessidade" }]
        : [{ cultura: x, tipo: TIPO[x], texto: txtPlantio(r, x) }];
      for (let k = anos.length; k < 3; k++) {
        const ant = anos[k - 1].cultura;
        const y = [...nomes, x].find((n) => papel(n) !== "P" && n !== "Mandioca" && n !== ant && n !== outro.anos[k].cultura && !(ehGram(n) && ehGram(ant)));
        if (y) anos.push({ cultura: y, tipo: TIPO[y] || "pousio", texto: txtPlantio(r, y) });
      }
      if (anos.length < 3) continue;
      const faixas = plano.faixas.map((f, j) => (j === i
        ? { ...f, anos, por_que: `Começa com ${com(x)}: ali teve ${fala(f.antes || "milho")} dois anos. ${porQueLinha(anos)}` } : f));
      if (!achou) achou = { x, faixas }; // nenhuma resolve: fica a 1ª que deu um giro inteiro (como antes)
      if (!umaSo(faixas)) { achou = { x, faixas }; break; }
    }
    if (achou) {
      antesEntrou = nomes.includes(achou.x) ? null : achou.x;
      plano = { ...plano, entrou: [...plano.entrou, ...(antesEntrou ? [achou.x] : [])], faixas: achou.faixas };
    }
  }

  // o que o ideal acrescenta (na prioridade que vale) e as notas
  const ideal = planoIdeal(r, resp, ef, prioridadePadrao(r, resp, ef));
  const noIdeal = [...new Set((ideal?.faixas || []).flatMap((f) => f.anos.flatMap((c) => nomesDoTexto(c.cultura))))]
    .filter((x) => x !== "Pousio pastejado" && !nomes.includes(x) && !plano.entrou.includes(x));
  plano.acrescenta = noIdeal;
  const tres3 = noIdeal.slice(0, 3).map(fala), resto = noIdeal.length - tres3.length;
  const mais = noIdeal.length ? ` O ideal acrescenta ${resto > 0 ? `${tres3.join(", ")} e mais ${resto}` : lista(tres3)}.` : "";
  if (naoGira) {
    const so = anuais[0] || P[0];
    const frase = so ? `Só ${fala(so)}: não dá para girar, ${com(so)} volta ao mesmo chão todo ano.${mais}` : `Sem cultura que gire.${mais}`;
    notas.unshift(frase);
    for (const f of plano.faixas) if (/^Parte /.test(f.parte)) f.por_que = frase;
  } else if (!L.length && !M && X.every(ehGram)) {
    notas.unshift(`${cap(lista(X.map(fala)))} são parentes: um depois do outro não quebra a lagarta.${mais}`);
  } else if (mais) notas.push(mais.trim());
  // o que entrou para não ficar uma cultura só vem primeiro (plantio.js e hoje_ideal.js mostram a nota que começa com "Entr")
  if (entrou.length) notas.unshift(anuais0.length ? `Entrou ${lista(entrou.map(com))} para girar com ${com(girarCom)}: a terra não cansa.`
    : `${entrou.length > 1 ? "Entraram" : "Entrou"} ${lista(entrou.map(com))}, girando ao lado ${de_(P[0])}.`);
  if (bxEntrou) notas.unshift(`Entrou ${com(bxEntrou)} no baixio, no meio ${de_(bxCult)}: a terra não cansa.`);
  if (antesEntrou) notas.unshift(`Entrou ${com(antesEntrou)} numa parte: o roçado não fica todo com uma planta só.`);
  if (X.includes("Milho") && milhoRisco) notas.push("Na terra alta, o milho tem mais risco aqui: em ano seco, plante o milho só no baixio.");
  if (milhoSolo) {
    const terra = { arenosa: "areia", mista: "terra misturada", barro: "barro" }[ef.terra];
    const quando = temJanela(rsMilho.risco40) ? `só tem plantio de ${rsMilho.risco40}, com mais risco` : "não tem data segura";
    const txt = `Na ${terra}, o milho ${quando} aqui: ${milhoSoBaixio ? "ele fica só no baixio" : temBx ? "plante o milho no baixio" : "converse com o técnico"}.`;
    avisos.push({ id: "solo", cultura: "Milho", txt }); // vai nas notas logo abaixo, com os outros avisos
  }
  if (temBx && !bxCult) notas.push("Sem milho nem sorgo, o baixio entra no giro das partes.");
  for (const a of avisos) notas.push(a.txt);
  return plano;
}

// ------------------------------------------------------------------ "O ideal"
/**
 * O plano com tudo o que sabemos (terra, baixio e maniva já vêm do núcleo em r; ano passado; prioridade; cardápio do lugar).
 * equilibrar = r.plano (as mesmas faixas: agendaDe devolve r.agenda.linhas), salvo quando o ano passado repetiu o chão;
 * garantir/vender/solo = as rotações de extras/cenarios.js ("Guardar água", "Mais renda", "Cuidar do solo"), as bordas do núcleo.
 * Campos além do formato de r.plano: tipo "ideal", prioridade, jeito (agua|renda|solo|plano), nome, manchete, troca.
 */
export function planoIdeal(r, resp = {}, ef = {}, prioridade) {
  if (!r?.plano?.faixas?.length) return null;
  const pri = PRIORIDADES.includes(prioridade) ? prioridade : prioridadePadrao(r, resp, ef);
  return memo(r, "ideal:" + pri, chaveDe(resp, ef), () => fazerIdeal(r, resp, ef, pri));
}

function fazerIdeal(r, resp, ef, pri) {
  const id = DA_PRIORIDADE[pri] || "plano";
  let Cn = null;
  try { Cn = calcCenarios(r, ef); } catch (_) { Cn = null; }
  const h = lerHoje(resp?.hoje || "", r.padroes), noChao = mandNoChao(h, ef);
  const meta = { tipo: "ideal", prioridade: pri, jeito: id, nome: NOME_PRIORIDADE[pri],
    manchete: Cn ? manchete(Cn, id) : null, troca: Cn ? troca(Cn, id) : null, mand_no_chao: noChao, ...foraDoGiro(r, resp, ef) };
  // sem as rotações (cenarios.js sem plano aqui), o ideal fica o plano do núcleo e diz isso no nome
  let p = id === "plano" || !Cn ? { ...r.plano, ...meta, jeito: "plano", nome: id === "plano" ? NOME_PRIORIDADE[pri] : NOME_JEITO.plano }
    : deCenario(r, ef, Cn, id, meta);
  // o "por quê" de cada parte com as palavras da roça (o do núcleo tem "tampão", "cereal solteiro"…): as faixas do núcleo não mudam
  if (p.jeito === "plano") p.por_que_de = Object.fromEntries(p.faixas.filter((f) => /^Parte |^Baixio/.test(f.parte))
    .map((f) => [f.parte, f.parte === "Baixio" ? porQueBaixio(f.anos, p.leguminosa) : porQueLinha(f.anos)]));
  // a mandioca que ele já tem no chão e não pode replantar (sem rama): o ideal sem mandioca colhe a velha em 2027 numa parte
  if (noChao && ef.maniva === "nao" && !p.faixas.some((f) => f.anos.some((c) => c.cultura === "Mandioca"))) {
    const partes = p.faixas.filter((f) => /^Parte /.test(f.parte)), i = parteDaVelha(partes.map((f) => f.anos));
    const alvo = partes[i];
    if (alvo) {
      const anos = [celVelha(), ...alvo.anos.slice(1)];
      p = { ...p, faixas: p.faixas.map((f) => (f === alvo ? { ...f, anos, por_que: porQueLinha(anos) } : f)) };
      if (p.por_que_de) p.por_que_de = { ...p.por_que_de, [alvo.parte]: porQueLinha(anos) };
    }
  }
  const A = lerAntes(r, resp);
  p = ajustarAntes(p, A, r);
  return Cn ? semMonoPlano(r, p, Cn, A) : p;
}

/** Sem monocultura (pedido do José, 15/11), no plano final (o do núcleo, as rotações, a mandioca velha e o ano passado já aplicados):
 *  as células que semMono (cenarios.js) troca entram no lugar; o resto fica igual (ex.: baixio só de sorgo nos 3 anos em Caicó vira
 *  sorgo → feijão → sorgo; só feijão e pousio no roçado ganha milho). No 1º ano, nada que repita o chão do ano passado.
 *  sem_mono = as partes que mudaram. */
function semMonoPlano(r, p, Cn, A) {
  const leg = p.leguminosa || Cn.R.leg;
  const fx = p.faixas.filter((f) => /^Parte |^Baixio/.test(f.parte));
  const linhas = linhasDe(fx, leg).map((l) => ({ ...l, area: l.parte === "Baixio" ? Cn.b : Cn.a }));
  const novas = semMono(linhas, Cn.R, (a) => !!repeteAntes({ cultura: a.nome, tipo: TIPO[a.nome] || "cereal" }, A));
  const troca = new Map(novas.filter((l) => l.cels.some((c) => c.mudou)).map((l) => [l.parte, l.cels]));
  if (!troca.size) return p;
  const porQue = (parte, anos) => (parte === "Baixio" ? porQueBaixio(anos, leg) : porQueLinha(anos));
  // com feijão no plano, o "sem leguminosa no cardápio" do núcleo nas outras células também sai (refeita pelo código dela)
  const cod = new Map(novas.map((l) => [l.parte, l.cels]));
  const faixas = p.faixas.map((f) => {
    const cels = cod.get(f.parte);
    const refaz = (c, k) => cels && (cels[k].mudou || /sem leguminosa/.test(c.texto || ""));
    if (!cels || !f.anos.some(refaz)) return f;
    const anos = f.anos.map((c, k) => (refaz(c, k) ? celCenario(r, cels[k], cels[k - 1] || null, f.parte, leg) : c));
    return { ...f, anos, por_que: porQue(f.parte, anos) };
  });
  const out = { ...p, faixas, leguminosa: leg, sem_mono: [...troca.keys()] };
  if (p.por_que_de) out.por_que_de = { ...p.por_que_de, ...Object.fromEntries(faixas.filter((f, i) => f !== p.faixas[i]).map((f) => [f.parte, f.por_que])) };
  return out;
}

function deCenario(r, ef, Cn, id, meta) {
  const leg = Cn.R.leg;
  const faixas = Cn.J[id].map((l) => {
    let ant = null;
    const anos = l.cels.map((c) => { const cel = celCenario(r, c, ant, l.parte, leg); ant = c; return cel; });
    return { parte: l.parte, anos };
  });
  if (meta.mand_no_chao) {
    const f = faixas.find((x) => /^Parte /.test(x.parte) && x.anos[0].cultura === "Mandioca");
    if (f) Object.assign(f.anos[0], { ja_no_chao: true, texto: "já está no chão: colhe em 2027 conforme a necessidade (reserva)" });
  }
  let parteMetade = null;
  if (/metade/.test(r.plano.interruptor || "") && leg) {
    const f = faixas.find((x) => /^Parte /.test(x.parte) && x.anos[0].cultura === leg);
    if (f) { f.anos[0].texto += "; metade guardada até ~10/mar"; parteMetade = f.parte; }
  }
  for (const f of faixas) f.por_que = f.parte === "Baixio" ? porQueBaixio(f.anos, leg) : porQueLinha(f.anos);
  const bordas = r.plano.faixas.filter((f) => f.parte === "Bordas");
  return { anos: r.plano.anos, faixas: [...faixas, ...bordas], principios: r.plano.principios, notas: [meta.manchete, meta.troca].filter(Boolean),
    leguminosa: leg, modelo_ne: r.plano.modelo_ne,
    interruptor: parteMetade ? `Alerta para 2027: na ${parteMetade}, metade ${de_(leg)} fica guardada até ~10/mar.`
      : alertaDe(r) ? "Alerta para 2027: plante escalonado e guarde forragem." : null, ...meta };
}

/** Uma célula das rotações de cenarios.js (códigos L C Z U F M1 M2 P1 P G1 G O) no formato de r.plano. */
function celCenario(r, c, ant, parte, leg) {
  const cel = (cultura, texto, extra = {}) => ({ cultura, tipo: TIPO[cultura] || "pousio", texto, ...extra });
  switch (c.k) {
    case "L": return cel(c.nome, (ant && ant.k === "M2" ? "na terra que foi mandioca; " : "") + txtPlantio(r, c.nome));
    case "C": return cel(c.nome, parte === "Baixio" ? "sozinho no baixio" : (ant?.k === "L" ? `depois ${de_(ant.nome || leg || "Feijão-caupi")} rende uns 24% a mais; ` : "") + txtPlantio(r, c.nome),
      parte === "Baixio" ? { solteiro: true } : {}); // sem a 2ª planta no meio (o flag manda: agendaDe, desenho e material)
    case "Z": return cel("Milho", leg ? `+ ${fala(leg)} em revezamento (50–85 dias depois); as linhas trocam de lugar` : txtPlantio(r, "Milho"));
    case "U": return cel("Milho", "+ mucuna-preta no milho em pé (~85 dias depois): cobre o chão, sem grão", { mucuna: true, solteiro: true });
    case "F": return cel(c.nome, "forragem; palhada sem fogo");
    case "M1": return cel("Mandioca", txtManiva(r));
    case "M2": return cel("Mandioca", "tampão: colhe conforme a necessidade");
    case "P1": return cel("Palma forrageira", "planta em nível: comida do gado na seca");
    case "P": return cel("Palma forrageira", "corta para o gado");
    case "G1": return cel(c.nome, c.par ? "planta junto da palma, longe do grão" : "planta: adubo e comida do gado");
    case "G": return cel(c.nome, c.par ? "com a palma: poda para o gado" : "poda para o gado e para a terra");
    default: return cel("Pousio pastejado", "descanso: o gado pasteja");
  }
}

// ------------------------------------------------------------------ o jeito de hoje (para comparar; não desenha)
/** O jeito de hoje (`hoje`) como "plano" para comparar: { tipo: "hoje", desenhavel: false, areas[{chave, cultura, nome, pct, ha}], arranjo }.
 *  Não tem Parte A/B/C: não passe para desenho.montar nem para agendaDe. */
export function planoHoje(r, resp = {}, ef = {}) {
  return memo(r, "hoje", chaveDe(resp, ef), () => {
    const h = lerHoje(resp?.hoje || "", r?.padroes), A = areasHoje(h, ef);
    return { tipo: "hoje", nome: "Hoje", desenhavel: false, anos: r?.plano?.anos || [2027, 2028, 2029], faixas: [], informado: h.informado,
      arranjo: h.cons === 1 ? "junto" : h.cons === 0 && h.mbx === 1 ? "baixio" : h.cons === 0 ? "pedacos" : null,
      areas: Object.keys(h.cult).map((k) => ({ chave: k, cultura: CULT[k]?.motor || null, nome: CULT[k]?.nome || k, pct: h.cult[k], ha: A.ha[k] })),
      queima: h.queima, chuva1: h.chuva1, sem: h.sem };
  });
}

// ------------------------------------------------------------------ a conta de R$ (calculo.js sem mudar + hoje_ideal.js)
/** Lançamentos de calculo.montar() para um plano qualquer; milho solteiro ou com mucuna no baixio volta a milho inteiro
 *  (montar parte o milho do baixio meio a meio com a leguminosa, a convenção do revezamento). */
export function itensPlano(r, ef, plano) {
  return memoP(plano, "itens|" + chaveDe({}, ef), () => {
    if (!r.financeiro) return { itens: [[], [], []], semRs: [] };
    // a mandioca que ele já tem no chão colhe em 2027 (o "plantada" de calculo.js), qualquer que seja a resposta da maniva
    const efc = plano.mand_no_chao && ef.maniva !== "plantada" ? { ...ef, maniva: "plantada" } : ef;
    const m = C.montar({ ...r, plano }, efDoGiro(efc, plano)); // as perenes que ele já tem guardam a área delas
    const leg = plano.leguminosa, bx = plano.faixas.find((f) => f.parte === "Baixio");
    if (bx && leg) bx.anos.forEach((c, k) => {
      if (c.cultura !== "Milho" || !c.solteiro) return;
      m.itens[k] = m.itens[k].filter((i) => !(i.parte === "Baixio" && i.cultura === leg));
      for (const i of m.itens[k]) if (i.parte === "Baixio" && i.cultura === "Milho") { if (i.custo) i.area *= 2; else i.fator *= 2; }
    });
    fasesMandioca(plano, m);
    return { ...m, itens: m.itens, semRs: m.semRs || [] };
  });
}

/** calculo.montar lê a 1ª mandioca de cada parte como plantio. Duas células do motor fogem disso e são refeitas aqui, com os meses
 *  dos lançamentos de mandioca que o próprio montar já tirou da agenda (±12 meses por ano): a parte que começa no 2º ano (m2: colhe
 *  em 2027 a do chão, planta em 2028, colhe em 2029) e a mandioca velha sem rama (colhe em 2027, não replanta). */
function fasesMandioca(plano, m) {
  const alvo = plano.faixas.filter((f) => f.parte !== "Bordas" && (f.anos[0]?.m2 || (f.anos[0]?.ja_no_chao && f.anos[1]?.cultura !== "Mandioca")));
  if (!alvo.length) return;
  const lancs = m.itens.flatMap((its, k) => its.filter((i) => i.cultura === "Mandioca").map((i) => ({ i, k })));
  const tc = lancs.find((x) => x.i.custo), tr = lancs.find((x) => x.i.serie && !x.i.plantada) || lancs.find((x) => x.i.serie);
  const pr = (i) => Math.min(C.NMESES - 1, Math.max(0, i));
  const mesPl = (k) => (tc ? pr(tc.i.mes + 12 * (k - tc.k)) : pr(C.idxMes(2027 + k, 3)));
  const mesesCo = (k) => (tr ? tr.i.meses.map(([j, w]) => [pr(j + 12 * (k - tr.k)), w]) : [[pr(C.idxMes(2027 + k, 6)), 1]]);
  for (const f of alvo) {
    const area = f.parte === "Baixio" ? m.b : m.a;
    for (let k = 0; k < 3; k++) m.itens[k] = m.itens[k].filter((i) => !(i.parte === f.parte && i.cultura === "Mandioca"));
    if (!(area > 0)) continue;
    let plantou = false;
    f.anos.forEach((c, k) => {
      if (c.cultura !== "Mandioca") { plantou = false; return; }
      if (k === 0 || plantou) { // a do chão (2027) ou a do ano anterior: colhe
        m.itens[k].push({ parte: f.parte, cultura: "Mandioca", serie: "Mandioca", fator: area, meses: mesesCo(k), tipo: "colheita",
          rotulo: k === 0 ? "colheita da mandioca que já está no chão" : "colheita da mandioca", ...(k === 0 ? { plantada: true } : {}) });
        plantou = false;
        return;
      }
      m.itens[k].push({ parte: f.parte, cultura: "Mandioca", custo: "Mandioca", area, mes: mesPl(k), rotulo: "maniva", tipo: "plantio" });
      plantou = true;
    });
  }
}

/** O "hoje" de hoje_ideal.js (áreas informadas; mandioca metade colhe, metade planta) com as culturas novas nos baldes de R$. */
function cenarioHoje(h, A) {
  const ha = { milho: 0, feijao: 0, sorgo: 0, mandioca: 0 };
  for (const [k, v] of Object.entries(A.ha)) {
    const n = CULT[k]?.motor;
    if (n === "Milho") ha.milho += v;
    else if (n === "Feijão-caupi" || n === "Feijão comum") ha.feijao += v; // calculo.js: as duas na série "Feijão" do IBGE
    else if (n === "Sorgo forrageiro" || n === "Milheto") ha.sorgo += v; // forragem: custo da semente, sem R$
    else if (n === "Mandioca") ha.mandioca += v;
  }
  return { ha, milhoAlta: A.milhoAlta, P: 0, fonte: {} };
}

/** A base comum da conta: as mesmas séries e os mesmos anos para hoje, melhor e os 4 ideais (comparação pareada, como no passo 4).
 *  Exportada como baseComum: dinheiro/pareado.js monta os "ver mais" do passo 4 nela (uma conta só). */
export function baseComum(r, resp = {}, ef = {}) { return contexto(r, resp, ef); }
function contexto(r, resp, ef) {
  return memo(r, "ctx", chaveDe(resp, ef), () => {
    const fin = r.financeiro, anosP = r.plano?.anos || [2027, 2028, 2029];
    const h = lerHoje(resp?.hoje || "", r.padroes), A = areasHoje(h, ef);
    const X = { h, A, fin: !!fin, falta: [], base: null, series: new Set(), okH: false, itH: [[], [], []], nivel: "semente", mult: 1, info: null };
    if (!fin) { X.falta.push("o IBGE (PAM) não tem a série deste município"); return X; }
    const m0 = C.montar(r, ef);
    X.itH = itensCen(anosP, cenarioHoje(h, A), ef.maniva === "plantada", mesesS0(m0));
    const cult = fin.culturas || {}, pr = fin.precos_raiz || {};
    let preco = pr[ef.raiz];
    if (!(preco > 0)) preco = pr.municipio ?? cult.Mandioca?.preco_kg;
    const ref = cult.Mandioca?.preco_kg;
    X.mult = ref && preco ? preco / ref : 1;
    X.preco = preco;
    X.nivel = ef.custo === "desembolso" ? "desembolso" : "semente";
    const H = fin.historico_R_ha, K = fin.historico_kg_ha || {};
    const temSerie = (s) => !!(cult[s] && H?.[s] && H[s].filter(Number.isFinite).length >= 10);
    // as séries do melhorado saem das culturas dele (sem montar o plano: a prioridade padrão, que o melhorado usa, lê esta base)
    const planos = PRIORIDADES.map((p) => planoIdeal(r, resp, ef, p)).filter(Boolean);
    const SER = { Milho: "Milho", "Feijão-caupi": "Feijão", "Feijão comum": "Feijão", Mandioca: "Mandioca" };
    const doMelhor = h.informado ? Object.keys(h.cult).map((k) => SER[CULT[k]?.motor]).filter(Boolean) : [];
    const usa = new Set([...seriesDe(X.itH), ...(doMelhor.length ? doMelhor : ["Milho", "Feijão"]),
      ...planos.flatMap((p) => [...seriesDe(itensPlano(r, ef, p).itens)])]);
    const series = [...usa].filter(temSerie);
    X.semSerie = [...usa].filter((s) => !temSerie(s));
    if (!series.length) { X.falta.push("o IBGE não tem série de R$ das culturas daqui"); return X; }
    const R = Object.fromEntries(series.map((s) => [s, new Map(H.anos.map((y, i) => [y, H[s][i]]))]));
    const KG = Object.fromEntries(series.map((s) => [s, new Map((K.anos || []).map((y, i) => [y, K[s]?.[i] ?? null]))]));
    const anos = H.anos.filter((y) => series.every((s) => Number.isFinite(R[s].get(y))));
    const anosEN = (fin.anos_el_nino_forte || [1998, 2010, 2016, 2024]).filter((y) => anos.includes(y));
    if (anos.length < 10 || !anosEN.length) { X.falta.push("anos suficientes com as culturas no mesmo ano"); return X; }
    X.series = new Set(series);
    // usadas e origens das séries da base (C.replay usa; o montar do plano do núcleo só preenche quando todas as dele existem)
    X.base = { ...m0, R, KG, anos, anosEN, usadas: series, origens: Object.fromEntries(series.map((s) => [s, H["origem_" + s] || []])) };
    // o jeito de hoje pareado (s0): sem a série que falta aqui (conta parcial, a mesma regra de contaRs)
    X.itH0 = X.itH.map((its) => its.filter((i) => !(i.serie || i.custo) || X.series.has(i.serie || i.custo) || !["Milho", "Feijão", "Mandioca"].includes(i.serie || i.custo)));
    X.okH = [...seriesDe(X.itH0)].length > 0;
    X.info = { anos: anos.length, ano0: anos[0], ano1: anos[anos.length - 1], anosEN, n: anosEN.length * anos.length * anos.length };
    return X;
  });
}

const tres = (f) => (f ? { p10: f.p10, p50: f.p50, p90: f.p90 } : null);
/** O ano normal, com o plano já rodando: metade de 2028 + metade de 2029 (a mandioca fica 2 anos no chão: num ano uma parte colhe,
 *  no outro, outra). Lançamentos de calculo.js são lineares na área: meia área de cada ano = a média dos dois anos. */
const meio = (its) => its.map((i) => (i.custo ? { ...i, area: i.area / 2 } : { ...i, fator: i.fator / 2 }));
const anoNormal = (its) => [...meio(its[1]), ...meio(its[2])];
function contaRs(X, it, ehHoje, plano = null) {
  if (!X.base) return { ok: false, falta: X.falta.length ? X.falta : ["sem a série do IBGE daqui"] };
  if (plano && plano.ha_giro === 0 && (plano.fora_do_giro || []).length) {
    return { ok: false, semGiro: true, falta: [`o seu roçado inteiro já é ${lista(plano.fora_do_giro.map((x) => fala(x.cultura)))}: não sobra chão para girar`] };
  }
  let itens = it.itens, parcial = [];
  const precisa = [...seriesDe(itens)];
  if (!precisa.length) return { ok: false, falta: ["o IBGE não tem série de R$ das culturas deste plano (só milho, feijão e mandioca têm)"] };
  // uma série faltando aqui (ex.: a mandioca em Caicó): a conta das outras, dita "sem a mandioca" (custo e colheita dela fora)
  const faltam = precisa.filter((s) => !X.series.has(s));
  if (faltam.length) {
    itens = itens.map((its) => its.filter((i) => !faltam.includes(i.serie || i.custo)));
    if (![...seriesDe(itens)].length) return { ok: false, falta: [`o IBGE não tem a série de ${lista(faltam.map((s) => s.toLowerCase()))} aqui`] };
    parcial = faltam;
  }
  const s0 = X.okH ? X.itH0 : [[], [], []];
  const m = { ...X.base, itens, s0 };
  const t = C.calcular(m, X.nivel, X.mult);
  const rep = C.replay(m, X.nivel, X.mult);
  const ord = rep.map((x) => x.plano).sort((a, b) => a - b);
  // o ano normal (média de 2028 e 2029) e a quebra nele
  const itN = anoNormal(itens), mN = { ...m, itens: [itens[0], itens[1], itN], s0: [s0[0], s0[1], s0[1].length ? anoNormal(s0) : []] };
  // sem nenhuma colheita com R$ no ano normal (só palma, sorgo forrageiro…): não medido, e não R$ 0
  const tN = itN.some((i) => i.serie) ? C.calcular(mN, X.nivel, X.mult).porAno[2] : null;
  return {
    ok: true, parcial,
    tres_anos: tres(t.plano), // 2027–2029 somados: o número do passo 4 (Quixadá padrão: hoje 2.480, ideal "um pouco de cada" 4.360)
    por_ano: t.porAno.map((a) => ({ ano: a.ano, ...tres(a.plano), n: a.n })),
    normal: tN ? { ...tres(tN.plano), n: tN.n } : null,
    el_nino: { p50: t.porAno[0].plano.p50, anos: t.elNino.map((e) => ({ ano: e.ano, sobra: e.plano })) },
    oito_em_dez: C.quantil(ord, 0.2), // num ano do plano já rodando (como 2029): em 8 de 10 anos já vistos, a sobra fica pelo menos nisto
    replay: rep.map((x) => ({ ano: x.ano, sobra: x.plano, vizinhos: x.vizinhos })),
    ganho: X.okH && !ehHoje ? tres(t.ganho) : null, a_frente: X.okH && !ehHoje ? t.aFrente : null,
    quebra: quebra(X.base, itN, X.mult), n: t.n, semRs: it.semRs, info: X.info, agro: X.base.agro || [],
    nivel: X.nivel, preco_raiz: X.preco,
  };
}

/** Comida colhida (kg de grão e de raiz por ano): rendimento do IBGE (kg/ha) × área, mediana dos anos, média dos 3 anos do plano. */
function comidaKg(X, itens) {
  const KG = X.base?.KG;
  if (!KG) return null;
  itens = itens.map((its) => its.filter((i) => !i.serie || X.series.has(i.serie))); // sem a série aqui (conta parcial): fora
  const porAno = [0, 1, 2].map((k) => {
    const vals = { grao: [], raiz: [] };
    for (const y of X.base.anos) {
      let g = 0, rz = 0, ok = true;
      for (const i of itens[k]) {
        if (!i.serie) continue;
        const v = KG[i.serie]?.get(y);
        if (!Number.isFinite(v)) { ok = false; break; }
        if (i.serie === "Mandioca") rz += v * i.fator; else g += v * i.fator;
      }
      if (ok) { vals.grao.push(g); vals.raiz.push(rz); }
    }
    if (!vals.grao.length) return null;
    const q = (a, p) => C.quantil([...a].sort((x, y) => x - y), p);
    return { grao: q(vals.grao, 0.5), raiz: q(vals.raiz, 0.5), p20: q(vals.grao, 0.2), p20r: q(vals.raiz, 0.2) };
  });
  if (porAno.some((x) => !x)) return null;
  const media = (f) => porAno.reduce((s, x) => s + x[f], 0) / 3;
  // grão e raiz não se somam (1 kg de raiz fresca não é 1 kg de grão): dois números
  return { grao: media("grao"), raiz: media("raiz"), p20: media("p20"), p20r: media("p20r") };
}

// ------------------------------------------------------------------ áreas de cada cultura em cada ano (N, forragem, chão coberto)
function celulasPlano(plano, ef) {
  const fx = plano.faixas.filter((f) => /^Parte /.test(f.parte) || f.parte === "Baixio");
  const eg = efDoGiro(ef, plano), T = eg.ha, temBx = fx.some((f) => f.parte === "Baixio"); // a mesma regra de calculo.montar
  const b = temBx ? Math.min(eg.baixio_ha ?? T / 3, T) : 0, nP = fx.filter((f) => /^Parte /.test(f.parte)).length || 1, a = (T - b) / nP;
  const out = [];
  for (const x of plano.fora_do_giro || []) { // as perenes que ele já tem (e a "outra"), no pedaço delas, os 3 anos
    if (!x.cultura || !(x.ha > 0)) continue;
    for (const k of [0, 1, 2]) out.push({ k, parte: "Perene", cultura: x.cultura, tipo: TIPO[x.cultura] || "perene", area: x.ha, c: { cultura: x.cultura, ja_plantado: true }, novo: false, revez: null, mucuna: false });
  }
  for (const f of fx) {
    const area = f.parte === "Baixio" ? b : a;
    if (!(area > 0)) continue;
    f.anos.forEach((c, k) => {
      const ant = k ? f.anos[k - 1] : null, novo = !ant || ant.cultura !== c.cultura;
      const revez = f.parte === "Baixio" && plano.leguminosa && c.cultura === "Milho" && !c.solteiro;
      out.push({ k, parte: f.parte, cultura: c.cultura, tipo: c.tipo, area, c, novo, revez: revez ? plano.leguminosa : null, mucuna: !!c.mucuna });
    });
  }
  return { T: ef.ha, cels: out };
}
function celulasHoje(X, ef) {
  const { h, A } = X, out = [];
  for (const [k, ha] of Object.entries(A.ha)) {
    const n = CULT[k]?.motor;
    if (!n || !(ha > 0)) continue;
    for (const kk of [0, 1, 2]) out.push({ k: kk, parte: "Hoje", cultura: n, tipo: TIPO[n], area: ha, c: { cultura: n }, novo: false, revez: null, mucuna: false });
  }
  return { T: ef.ha, cels: out, junto: h.cons !== 0 };
}

/** Valor central de um coeficiente de agronomia.json: número, [min, max] ou { min, max | valor | central }. */
function coef(tab, nome) {
  const v = tab?.[nome];
  if (v == null) return null;
  if (typeof v === "number") return { v, min: v, max: v };
  if (Array.isArray(v) && v.length >= 2 && v.every(Number.isFinite)) return { v: (v[0] + v[1]) / 2, min: v[0], max: v[1] };
  if (Array.isArray(v) && v.length === 1 && Number.isFinite(v[0])) return { v: v[0], min: v[0], max: v[0] };
  if (typeof v === "object") {
    const c = [v.valor, v.central, v.medio, v.v].find(Number.isFinite);
    const mn = Number.isFinite(v.min) ? v.min : c, mx = Number.isFinite(v.max) ? v.max : c;
    if (Number.isFinite(c)) return { v: c, min: mn ?? c, max: mx ?? c };
    if (Number.isFinite(mn) && Number.isFinite(mx)) return { v: (mn + mx) / 2, min: mn, max: mx };
  }
  return null;
}
const tabela = (...ks) => { const b = AGRO?.beneficios; if (!b) return null; for (const k of ks) if (b[k]) return { tab: b[k], k }; return null; };
const fonteTab = (k) => { const b = AGRO?.beneficios; const f = b?.fonte?.[k] ?? b?.fontes?.[k]; return typeof f === "string" ? f : Array.isArray(f) ? f.join("; ") : ""; };

/** Soma por ano de área × coeficiente das culturas da tabela; null = falta o coeficiente de uma cultura que deveria entrar (o
 *  pedaço medido vai em parcial). A nota do A1 "use a ponta baixa" (fonte_cultura) troca o valor central pelo mínimo. */
function somaCoef(cels, tab, k, entra, fator = () => 1) {
  const falta = new Set(), porAno = [0, 0, 0], min = [0, 0, 0], max = [0, 0, 0];
  const nota = AGRO?.beneficios?.fonte_cultura?.[k] || {};
  for (const x of cels) {
    for (const [nome, f] of entra(x)) {
      const c = coef(tab, nome);
      const w = x.area * f * fator(x, nome);
      if (!c) { if (w > 0) falta.add(nome); continue; }
      const v = /ponta baixa/i.test(nota[nome] || "") ? c.min : c.v;
      porAno[x.k] += w * v; min[x.k] += w * c.min; max[x.k] += w * c.max;
    }
  }
  const m = (a) => a.reduce((s, v) => s + v, 0) / 3;
  if (falta.size) return { valor: null, falta: [...falta], parcial: m(porAno) };
  return { valor: m(porAno), faixa: [m(min), m(max)], por_ano: porAno };
}

/** Meses com planta viva no chão, por ano (dias de ciclo do calendário do núcleo); null = cultura sem ciclo. */
function mesesCel(x, r) {
  const ciclo = (n) => (CICLO[n] ? (CICLO[n][0] + CICLO[n][1]) / 2 : null);
  if (x.tipo === "perene" || PERENE.has(x.cultura) || /^Palma/.test(x.cultura)) return 12;
  if (x.cultura === "Pousio pastejado") return 4; // a estação chuvosa típica (4 meses): o mato rebrota
  if (x.cultura === "Mandioca") return ciclo("Mandioca") / 30 / 2; // ~15 meses no chão, em 2 anos
  if (x.revez) { const cm = ciclo("Milho"), cl = ciclo(x.revez); return cl ? Math.max(cm, 67.5 + cl) / 30 : cm / 30; }
  const c = ciclo(x.cultura);
  return c ? c / 30 : null;
}

// ------------------------------------------------------------------ "O que você ganha": os 8 números
const ROT = {
  rs_tipico: ["Sobra num ano normal", "R$/ano"], rs_el_nino: ["Sobra em 2027, ano de El Niño", "R$"], quebra_10: ["Anos de quebra", "em 10"],
  comida_kg: ["Grão colhido", "kg/ano"], raiz_kg: ["Raiz de mandioca", "kg/ano"], forragem_t: ["Comida do gado", "t/ano"],
  n_kg: ["Adubo que o feijão deixa", "kg de nitrogênio/ano"],
  meses_coberto: ["Chão coberto", "meses/ano"], ponte_lagarta: ["Caminho da lagarta cortado", "anos em 3"],
};
const item = (id, valor, selo, fonte, extra = {}) => ({ id, rotulo: ROT[id][0], valor: valor == null || !Number.isFinite(valor) ? null : valor, unidade: ROT[id][1], selo, fonte, ...extra });

/** O número de um item como as telas escrevem: uma regra só para o Plano ("O que você ganha") e o Quanto rende ("Ver como
 *  calculamos"). U = comum.js (num, brl). null = não medido. */
export function textoItem(U, it) {
  const v = it?.valor;
  if (v === null || v === undefined || !Number.isFinite(v)) return null;
  switch (it.id) {
    case "rs_tipico": case "rs_el_nino": return U.brl(v);
    case "quebra_10": return `${U.num(v)} em 10`;
    case "comida_kg": case "raiz_kg": return `${U.num(v >= 100 ? Math.round(v / 10) * 10 : Math.round(v))} kg`;
    case "forragem_t": return `${U.num(v, v > 0 && v < 10 ? 1 : 0)} t`;
    case "n_kg": return `${U.num(Math.round(v))} kg`;
    case "meses_coberto": return `${U.num(v, 1)} meses`;
    case "ponte_lagarta": return `${U.num(v)} de 3 anos`;
    default: return U.num(v);
  }
}

/**
 * Os 8 números de "O que você ganha" para um plano. tipo: "hoje" (o plano é ignorado: vale `hoje` de Sua roça), "melhor" ou "ideal".
 * → { tipo, itens: [{ id, rotulo, valor, unidade, selo, fonte, faixa?, detalhe? }] (ids: rs_tipico, rs_el_nino, quebra_10, comida_kg,
 *     forragem_t, n_kg, meses_coberto, ponte_lagarta; valor null = não medido, com o motivo na fonte), rs: {...} (contaRs) }.
 */
export function beneficios(r, resp = {}, ef = {}, plano = null, tipo = "ideal") {
  const ehHoje = tipo === "hoje";
  const p = ehHoje ? planoHoje(r, resp, ef) : plano;
  if (!p) return null;
  return memoP(p, `ben|${tipo}|${chaveDe(resp, ef)}`, () => fazerBeneficios(r, resp, ef, p, ehHoje ? "hoje" : tipo));
}

function fazerBeneficios(r, resp, ef, plano, tipo) {
  const ehHoje = tipo === "hoje";
  const X = contexto(r, resp, ef);
  const it = ehHoje ? { itens: X.itH, semRs: [] } : itensPlano(r, ef, plano);
  const rs = contaRs(X, it, ehHoje, ehHoje ? null : plano);
  const info = rs.info || X.info;
  const custo = X.nivel === "desembolso" ? "máquina, insumos e serviços (CONAB)" : "a semente (CONAB)";
  const semRsTxt = rs.ok ? "" : `não medido: ${rs.falta.join("; ")}`;
  // o que fica fora do R$: as culturas sem série do IBGE aqui (palma, sorgo de grão…) e a forragem (sorgo, milheto: só o custo)
  const forr = ehHoje ? [] : [...new Set(it.itens.flat().filter((i) => i.uso).map((i) => i.cultura))];
  const foraRs = ehHoje ? [] : [...new Set([...(it.semRs || []), ...forr])];
  const foraTxt = (foraRs.length ? `; fora do R$: ${lista(foraRs.map(fala))} (comida da criação ou sem série do IBGE aqui)` : "")
    + (rs.parcial?.length ? `; sem ${lista(rs.parcial.map((s) => (s === "Mandioca" ? "a mandioca" : `o ${s.toLowerCase()}`)))}: o IBGE não tem a série aqui` : "");
  const FONTE_RS = info ? `colheita a preço da região (IBGE PAM 1998–2025, R$ de 2025) menos ${custo}; a mão de obra da família não entra${foraTxt}` : "";
  const itens = [];
  const extraRs = { fora_rs: foraRs, parcial: rs.parcial || [] };
  // 1-2. R$ (o ano normal = média de 2028 e 2029; 2027 = o que sobrou em pelo menos 3 dos 4 El Niños fortes)
  const semNormal = rs.ok && !rs.normal;
  itens.push(item("rs_tipico", rs.ok && rs.normal ? rs.normal.p50 : null, "projecao", semNormal
    ? `não medido: com o plano já rodando (2028 e 2029), só ficam culturas fora do R$${foraTxt}` : rs.ok
    ? `Sobra num ano com o plano já rodando (a média de 2028 e 2029, porque a mandioca fica 2 anos no chão): mediana dos ${info.anos} anos de ${info.ano0} a ${info.ano1}; ${FONTE_RS}` : semRsTxt,
    rs.ok && rs.normal ? { faixa: [rs.normal.p10, rs.normal.p90], detalhe: { tres_anos: rs.tres_anos, oito_em_dez: rs.oito_em_dez, ...extraRs } } : { detalhe: extraRs }));
  const en = rs.ok ? [...rs.el_nino.anos].sort((a, b) => a.sobra - b.sobra) : [];
  const iEN = Math.max(0, en.length - 3), vEN = en.length ? en[iEN].sobra : null;
  itens.push(item("rs_el_nino", vEN, "projecao", rs.ok
    ? `2027 refeito nos ${en.length} El Niños fortes já vistos: em ${en.length - iEN} de ${en.length} sobrou pelo menos isto (${rs.el_nino.anos.map((e) => `${e.ano}: R$ ${Math.round(e.sobra).toLocaleString("pt-BR")}`).join("; ")}); ${FONTE_RS}` : semRsTxt,
    rs.ok ? { faixa: [en[0].sobra, en[en.length - 1].sobra], detalhe: { anos: rs.el_nino.anos, mediana: rs.el_nino.p50, ...extraRs } } : { detalhe: extraRs }));
  // 3. quebra
  const q = rs.ok ? rs.quebra : null;
  itens.push(item("quebra_10", q ? Math.round(q.p * 10) : null, ehHoje ? "medido" : "projecao", q
    ? `Anos em que a colheita do roçado (já rodando) vale menos da metade do típico dele: ${q.k} de ${q.n} anos do IBGE PAM (1998–2025); nos El Niños fortes, ${q.enQ} de ${q.nEN}${foraTxt}`
    : semRsTxt || "não medido: sem a série do IBGE", q ? { detalhe: { k: q.k, n: q.n, enQ: q.enQ, nEN: q.nEN } } : {}));
  // 4. comida: grão e raiz em dois números (não se somam)
  const cm = rs.ok ? comidaKg(X, it.itens) : null;
  const semGrao = [...new Set((ehHoje ? [] : it.semRs).filter((n) => /Sorgo granífero|Amendoim|Algodão|Mamona|Girassol/.test(n)))];
  const FONTE_KG = "rendimento do IBGE PAM (kg/ha) × área de cada cultura; mediana dos anos já vistos, média dos 3 anos do plano";
  itens.push(item("comida_kg", cm ? cm.grao : null, "projecao", cm
    ? `Grão de milho e feijão: ${FONTE_KG}${semGrao.length ? `; ${lista(semGrao.map(fala))} sem série do IBGE aqui, fora da conta` : ""}`
    : semRsTxt || "não medido: sem a série de kg/ha do IBGE", cm ? { detalhe: { grao_kg: cm.grao, raiz_kg: cm.raiz, oito_em_dez_kg: cm.p20, oito_em_dez_raiz_kg: cm.p20r } } : {}));
  const semRaiz = (rs.parcial || []).includes("Mandioca");
  itens.push(item("raiz_kg", cm && !semRaiz ? cm.raiz : null, "projecao", cm && !semRaiz ? `Raiz de mandioca fresca: ${FONTE_KG}`
    : semRaiz ? "não medido: o IBGE não tem a série da mandioca aqui" : semRsTxt || "não medido: sem a série de kg/ha do IBGE",
    cm && !semRaiz ? { detalhe: { oito_em_dez_kg: cm.p20r } } : {}));
  // 5-6. forragem e N (agronomia.json)
  const cl = ehHoje ? celulasHoje(X, ef) : celulasPlano(plano, ef);
  const tF = tabela("forragem_t_ms_ha", "forragem_t_ha", "forragem");
  if (!AGRO || !tF) itens.push(item("forragem_t", null, "suposicao", "não medido: falta o coeficiente de forragem (dados/agronomia.json)"));
  else {
    const fz = somaCoef(cl.cels, tF.tab, tF.k, (x) => (tF.tab[x.cultura] !== undefined || x.tipo === "forragem" || /^Palma|^Gliric|^Guandu/.test(x.cultura) ? [[x.cultura, 1]] : []),
      (x) => (x.c?.ja_plantado || !x.novo || !PERENE.has(x.cultura) || ehHoje ? 1 : 0)); // perene no 1º ano ainda não corta
    itens.push(item("forragem_t", fz.valor, "suposicao", fz.valor == null
      ? `não medido: a fonte lida não dá a produção de ${lista(fz.falta.map(fala))} (dados/agronomia.json)`
      : `Matéria seca por ano, média dos 3 anos = área de cada forrageira × produção por ha; perene no 1º ano não conta; a palha do milho não entra. ${fonteTab(tF.k) || "dados/agronomia.json"}`,
      fz.valor == null ? { detalhe: { parcial: fz.parcial, falta: fz.falta } } : { faixa: fz.faixa, detalhe: { por_ano: fz.por_ano } }));
  }
  const tN = tabela("n_kg_ha", "n_kg", "nitrogenio_kg_ha");
  if (!AGRO || !tN) itens.push(item("n_kg", null, "suposicao", "não medido: falta o coeficiente de nitrogênio (dados/agronomia.json)"));
  else {
    const nz = somaCoef(cl.cels, tN.tab, tN.k, (x) => (x.revez ? [[x.revez, 0.5]] : x.mucuna ? [["Mucuna-preta", 0.5]] : FIXA_N.has(x.cultura) ? [[x.cultura, 1]] : []));
    itens.push(item("n_kg", nz.valor, "suposicao", nz.valor == null
      ? `não medido: a fonte lida não dá o nitrogênio de ${lista(nz.falta.map(fala))} (dados/agronomia.json)`
      : `kg de N por ano que a leguminosa deixa na terra, média dos 3 anos = área de cada leguminosa × kg de N por ha; o feijão no milho em pé conta meia área. ${fonteTab(tN.k) || "dados/agronomia.json"}`,
      nz.valor == null ? { detalhe: { parcial: nz.parcial, falta: nz.falta } } : { faixa: nz.faixa, detalhe: { por_ano: nz.por_ano } }));
  }
  // 7. chão coberto
  itens.push(mesesItem(cl, ehHoje, r));
  // 8. ponte da lagarta
  itens.push(ponteItem(X, plano, ef, ehHoje));
  return { tipo, itens, rs };
}

function mesesItem(cl, ehHoje, r) {
  const T = cl.T;
  if (!(T > 0)) return item("meses_coberto", null, "suposicao", "não medido: sem a área do roçado");
  let soma = 0, peso = 0;
  const sem = new Set();
  if (ehHoje && cl.junto) { // tudo junto: as anuais dividem o mesmo chão (vale a de ciclo mais longo); mandioca e perenes no pedaço delas
    for (const k of [0, 1, 2]) {
      const cs = cl.cels.filter((x) => x.k === k);
      const anu = cs.filter((x) => x.cultura !== "Mandioca" && !PERENE.has(x.cultura));
      const outras = cs.filter((x) => !anu.includes(x));
      const aA = anu.reduce((s, x) => s + x.area, 0), mA = Math.max(0, ...anu.map((x) => mesesCel(x, r) ?? 0));
      if (aA > 0) { soma += aA * mA; peso += aA; }
      for (const x of outras) { const m = mesesCel(x, r); if (m == null) { sem.add(x.cultura); continue; } soma += x.area * m; peso += x.area; }
    }
  } else {
    for (const x of cl.cels) { const m = mesesCel(x, r); if (m == null) { sem.add(x.cultura); continue; } soma += x.area * m; peso += x.area; }
  }
  if (!peso) return item("meses_coberto", null, "suposicao", "não medido: sem ciclo das culturas");
  return item("meses_coberto", Math.round((soma / peso) * 10) / 10, "suposicao",
    `Meses com planta viva no chão por ano, na média do roçado: dias de ciclo do calendário do núcleo (os mesmos das barras de colheita); mandioca ~15 meses em 2 anos; perene 12; descanso, os 4 meses da chuva${ehHoje && cl.junto ? "; tudo junto conta a cultura de ciclo mais longo" : ""}${sem.size ? `; ${lista([...sem].map(fala))} sem ciclo, fora da média` : ""}; a palhada sem fogo não entra`);
}

function ponteItem(X, plano, ef, ehHoje) {
  const FONTE = "Desenho do roçado em faixas (grade de ~5 m, 4 vizinhos; plantio/desenho.js): anos em que nenhum bloco de milho, sorgo ou milheto liga o alto ao pé do roçado; ideia de Vicente Lima (PercolaCampo). Não segura a mariposa que voa longe";
  if (ehHoje) {
    const { h, A } = X;
    const gram = Object.entries(A.ha).filter(([k, v]) => v > 0 && ehGram(CULT[k]?.motor));
    const soBaixio = h.cons === 0 && h.mbx === 1 && A.milhoAlta <= 0.02 && gram.every(([k]) => k === "milho");
    const v = !gram.length || soBaixio ? 3 : 0;
    return item("ponte_lagarta", v, "suposicao", `${FONTE}. Hoje: ${!gram.length ? "sem milho nem sorgo" : soBaixio ? "o milho só no baixio" : h.cons === 0 ? "cada cultura num pedaço, do alto ao pé" : "tudo junto, o milho forma um bloco só"}`,
      { detalhe: { arranjo: h.cons === 1 ? "junto" : h.cons === 0 ? (h.mbx === 1 ? "baixio" : "pedacos") : null } });
  }
  try {
    const lay = montarDesenho(plano, ef);
    const anos = (plano.anos || [2027, 2028, 2029]).map((ano, k) => {
      const g = grade(lay, k, "faixas"), bl = grade(lay, k, "blocos");
      return { ano, p: g.p, blocos: g.blocos, desce: g.desce, desce_em_blocos: bl.desce, cortada: g.p === 0 || !g.desce };
    });
    return item("ponte_lagarta", anos.filter((a) => a.cortada).length, "suposicao", FONTE, { detalhe: { anos } });
  } catch (e) {
    return item("ponte_lagarta", null, "suposicao", `não medido: o desenho do roçado falhou (${e.message})`);
  }
}

// ------------------------------------------------------------------ os três lado a lado
/** { prioridade, hoje, melhor, ideal }, cada um { plano, beneficios }. Sem prioridade, a que vale (prioridadePadrao). */
export function comparar3(r, resp = {}, ef = {}, prioridade) {
  const pri = PRIORIDADES.includes(prioridade) ? prioridade : prioridadePadrao(r, resp, ef);
  const ph = planoHoje(r, resp, ef), pm = planoMelhor(r, resp, ef), pi = planoIdeal(r, resp, ef, pri);
  return {
    prioridade: pri,
    hoje: { plano: ph, beneficios: beneficios(r, resp, ef, ph, "hoje") },
    melhor: { plano: pm, beneficios: pm ? beneficios(r, resp, ef, pm, "melhor") : null },
    ideal: { plano: pi, beneficios: pi ? beneficios(r, resp, ef, pi, "ideal") : null },
  };
}

// ------------------------------------------------------------------ o calendário do plano (formato de r.agenda.linhas)
const barra = (V, de, ate, tipo, rot) => {
  const de2 = Math.max(de, V.ini), ate2 = Math.min(ate, V.fim);
  if (de2 > ate2) return null;
  return { de: iso(de2), ate: iso(ate2), tipo, rotulo: `${rot}: ${dmy(de)} a ${dmy(ate)}`, segue: ate > V.fim };
};
/** Linha com a janela do ZARC (nucleo/motor.py, _linha): preparo 30 dias antes, mais risco, plantio, crescendo e colheita (CICLO). */
function linhaZarc(V, parte, nome, tipo, J, est) {
  const s = est - 2027, ini = maisAnos(J.ini, s), fim = maisAnos(J.fim, s), ei = maisAnos(J.ext_ini, s), efm = maisAnos(J.ext_fim, s);
  const lin = { parte, cultura: nome, tipo, estacao: est, barras: [], marcos: [], plantar: "—", colher: "—", fonte: "" };
  const p0 = Math.min(ini, ei ?? ini);
  const b = [p0 - DIA >= V.hoje ? barra(V, Math.max(V.hoje, p0 - 30 * DIA), p0 - DIA, "preparo", "preparo sem fogo (palhada no chão, aceiro)") : null];
  if (ei != null && ei < ini) b.push(barra(V, ei, ini - DIA, "risco", "dá para plantar, com mais risco (até 40%)"));
  b.push(barra(V, ini, fim, J.zarc ? "plantio" : "estimado", J.zarc ? "plantio" : "plantio (estimado)"));
  if (efm != null && efm > fim) b.push(barra(V, fim + DIA, efm, "risco", "dá para plantar, com mais risco (até 40%)"));
  for (const x of b) if (x) x.pista = 1;
  const cic = CICLO[nome];
  if (cic) {
    const [cmin, cmax, cf] = cic, c0 = ini + cmin * DIA, c1 = fim + cmax * DIA;
    for (const x of [barra(V, ini, c0 - DIA, "roca", "na roça, crescendo"), barra(V, c0, c1, "colheita", "colheita")]) if (x) { x.pista = 2; b.push(x); }
    lin.colher = cmin >= 300 ? `de ${mesAno(c0)} a ${mesAno(c1)} (${Math.floor(cmin / 30)}–${Math.floor(cmax / 30)} meses depois do plantio; ${cf})`
      : `de ${dmy(c0)} a ${dmy(c1)} (${cmin}–${cmax} dias depois do plantio; ${cf})`;
  }
  lin.barras = b.filter(Boolean);
  const extra = [ei != null && ei < ini ? `desde ${dm(ei)}` : null, efm != null && efm > fim ? `até ${dm(efm)}` : null].filter(Boolean);
  lin.plantar = `de ${dmy(ini)} a ${dmy(fim)}${extra.length ? ` (com mais risco, ${extra.join(" e ")})` : ""}`;
  lin.fonte = J.fonte + (est > 2027 && J.zarc ? "; 2028 repete as datas do ZARC 2026/27 (o de 2027/28 ainda não saiu)" : "");
  return lin;
}
/** Sem ZARC aqui (cultura fora de r.agenda.culturas que o cardápio deixa): a janela estimada do núcleo (nucleo/motor.py, janela()
 *  sem ZARC), do início típico da chuva (IMERG, r.este_ano.inicio.mediana) a 40 dias depois. Cultura "fora" não ganha data. */
function janelaEstimada(r, nome) {
  const med = r.este_ano?.inicio?.mediana, m0 = +r.este_ano?.regime?.mes_inicio;
  const c = (r.cardapio || []).find((x) => x.cultura === nome);
  if (!med || !m0 || !c || c.situacao === "fora") return null;
  const [d, m] = med.split("/").map(Number), mi = ((((m0 - 4) % 12) + 12) % 12) + 1, y0 = mi >= 7 ? 2026 : 2027;
  const ini = Date.UTC(m >= mi ? y0 : y0 + 1, m - 1, d);
  return { ini, fim: ini + 40 * DIA, ext_ini: null, ext_fim: null, zarc: false,
    fonte: `estimado: do início típico da chuva no IMERG (${med}) a 40 dias depois; sem ZARC aqui (suposição)` };
}
/** Leguminosa semeada no milho em pé, 50–85 dias depois do plantio do milho (nucleo/motor.py, _revezamento). */
function linhaRevez(V, r, jm, leg, est) {
  const s0 = jm.ini + 50 * DIA, s1 = jm.ini + 85 * DIA, [cmin, cmax, cf] = CICLO[leg] || [60, 75, "suposição"];
  const lin = { parte: "Baixio", cultura: `${leg} no milho em pé`, tipo: "leguminosa", estacao: est, marcos: [],
    barras: [barra(V, s0, s1, "plantio", "semeadura no milho em pé"), barra(V, s0 + cmin * DIA, s1 + cmax * DIA, "colheita", "colheita")].filter(Boolean),
    plantar: `de ${dmy(s0)} a ${dmy(s1)} (50–85 dias depois de plantar o milho no começo da janela)`,
    colher: `de ${dmy(s0 + cmin * DIA)} a ${dmy(s1 + cmax * DIA)} (${cmin}–${cmax} dias; ${cf})`,
    fonte: "revezamento no milho em pé (Melo 2013, só direção; sem bônus de grão)" };
  lin.barras.forEach((x, i) => { x.pista = i + 1; });
  const jl = janela(r, leg);
  if (jl && !jl.semData && jl.zarc && s1 > (jl.ext_fim ?? jl.fim)) lin.fonte += `; a semeadura depois de ${dm(jl.ext_fim ?? jl.fim)} fica fora do ZARC do ${leg.toLowerCase()}`;
  return lin;
}
/** Mucuna semeada no milho em pé aos ~85 dias (cartão melo_relay_mucuna do núcleo); não colhe: fica como cobertura. */
function linhaMucuna(V, jm, est) {
  const s0 = jm.ini + 85 * DIA, s1 = jm.fim + 85 * DIA, b = barra(V, s0, s1, "plantio", "semeadura no milho em pé (~85 dias depois do milho)");
  if (!b) return null;
  return { parte: "Baixio", cultura: "Mucuna-preta no milho em pé", tipo: "leguminosa", estacao: est, marcos: [], barras: [{ ...b, pista: 1 }],
    plantar: `de ${dmy(s0)} a ${dmy(s1)} (~85 dias depois de plantar o milho)`, colher: "não colhe: a rama fica no chão como cobertura",
    fonte: "milho + mucuna-preta aos 85 dias, sem adubo (Melo 2013, Alagoinha-PB; só direção, sem bônus de grão)" };
}
/** A estação chuvosa típica (nucleo/motor.py, _estacao_tipica): do 1º dia do mês do início da chuva ao fim do 3º mês seguinte. */
function estacaoTipica(m0, est) {
  const mi = ((((m0 - 4) % 12) + 12) % 12) + 1, ano = (mes) => { const y0 = mi >= 7 ? est - 1 : est; return mes >= mi ? y0 : y0 + 1; };
  const m3 = ((m0 + 2) % 12) + 1, a3 = ano(m3);
  return [Date.UTC(ano(m0), m0 - 1, 1), Date.UTC(a3, m3, 0)];
}
function linhaPousio(V, r, parte, est) {
  const reg = r.este_ano?.regime;
  if (!reg?.mes_inicio) return null;
  const [e0, e1] = estacaoTipica(+reg.mes_inicio, est), x = barra(V, Math.max(e0, V.hoje), e1, "pousio", "pousio pastejado");
  if (!x) return null;
  return { parte, cultura: "Pousio pastejado", tipo: "pousio", estacao: est, barras: [{ ...x, pista: 2 }], marcos: [],
    plantar: "não planta: o gado pasteja e a terra descansa", colher: "—", fonte: `estação típica ${reg.estacao} (IMERG)` };
}
function linhaJaNoChao(V, r, parte, nome, est) {
  const reg = r.este_ano?.regime;
  if (!reg?.mes_inicio) return { parte, cultura: nome, tipo: "tampão", estacao: est, barras: [], marcos: [], plantar: "já está no chão (resposta sua)", colher: "conforme a necessidade", fonte: "resposta da família" };
  const [e0, e1] = estacaoTipica(+reg.mes_inicio, est);
  const bs = [barra(V, Math.max(V.hoje, V.ini), e0 - DIA, "roca", "já na roça"), barra(V, Math.max(e0, V.hoje), e1 + 150 * DIA, "colheita", "colhe conforme a necessidade")]
    .filter(Boolean).map((x) => ({ ...x, pista: 2 }));
  return { parte, cultura: nome, tipo: "tampão", estacao: est, barras: bs, marcos: [], plantar: "já está no chão (resposta sua)",
    colher: `de ${mesAno(Math.max(e0, V.hoje))} a ${mesAno(e1 + 150 * DIA)}, conforme a necessidade`,
    fonte: "resposta da família; colher na estação e na seca seguinte (suposição)" };
}
const semJanela = (parte, nome, tipo, est, J, fora) => ({ parte, cultura: nome, tipo, estacao: est, barras: [], marcos: [],
  plantar: J?.plantar || (fora ? "sem data segura aqui (fora do zoneamento): combine com o técnico" : "sem data aqui: combine com o técnico"),
  colher: J?.colher || "—", fonte: J?.fonte || (fora ? "a cultura não tem ZARC neste município" : "sem ZARC nem ciclo para esta cultura aqui") });

const baseNome = (c) => (/^Palma/.test(c) ? "Palma forrageira" : c);
/** A linha que r.agenda já tem para a mesma cultura e estação (mesma parte; senão o mesmo tipo de chão: baixio ou terra alta). */
function copiaDaAgenda(ag, parte, nome, est) {
  const bx = parte === "Baixio";
  const ls = (ag.linhas || []).filter((l) => baseNome(l.cultura) === nome && l.estacao === est && !/em pé/.test(l.cultura)
    && !/já está no chão/.test(l.plantar || "") && l.tipo !== "pousio");
  const l = ls.find((x) => x.parte === parte) || ls.find((x) => (x.parte === "Baixio") === bx);
  if (!l) return null;
  const c = JSON.parse(JSON.stringify(l));
  c.parte = parte;
  c.marcos = [];
  c.plantar = String(c.plantar || "").replace("; ano de alerta: plante metade e guarde a outra até ~10/mar", "");
  return c;
}
const janelaDaLinha = (lin) => {
  const b = (lin.barras || []).find((x) => x.tipo === "plantio" || x.tipo === "estimado");
  const m = b && /(\d{2}\/\d{2}\/\d{4}) a (\d{2}\/\d{2}\/\d{4})/.exec(b.rotulo);
  return m ? { ini: deBR(m[1]), fim: deBR(m[2]) } : null;
};

/**
 * As linhas do calendário do plano, no formato de r.agenda.linhas ({parte, cultura, tipo, estacao, barras[{de, ate, tipo, rotulo,
 * segue, pista}], marcos, plantar, colher, fonte}), de hoje até r.agenda.fim (dez/2027): a estação 2027 de cada parte e o plantio de
 * 2028 que cai antes do fim. Para r.plano (as mesmas faixas) devolve r.agenda.linhas sem mudar. opcoes.refazer = true monta de novo
 * (testes); opcoes.semCopia = true não copia nada de r.agenda.linhas (testes: confere as regras de data contra o núcleo).
 */
export function agendaDe(r, plano, ef = {}, opcoes = {}) {
  const ag = r?.agenda;
  if (!ag || !plano?.faixas?.length) return [];
  if (!opcoes.refazer && r.plano && plano.faixas === r.plano.faixas) return ag.linhas;
  const fazer = () => fazerAgenda(r, plano, opcoes);
  return opcoes.refazer ? fazer() : memoP(plano, "agenda", fazer);
}

/** O calendário do plano até dezembro do último ano dele (2029), para o mês a mês do Plano: as estações de 2028 e 2029 repetem as
 *  datas do ZARC 2026/27 na rotação do plano (PROJEÇÃO). Sai das regras de data daqui, sem copiar de r.agenda (que para em dez/2027). */
export function agendaLonga(r, plano) {
  if (!r?.agenda || !plano?.faixas?.length) return [];
  return memoP(plano, "agenda-longa", () => fazerAgenda(r, plano, { longa: true }));
}

function fazerAgenda(r, plano, opcoes) {
  const ag = r.agenda, anos = plano.anos || [2027], E0 = anos[0], leg = plano.leguminosa || null;
  // opcoes.longa: todas as estações do plano, até 31/dez do último ano, sem cópia do núcleo (as linhas dele são cortadas em ag.fim)
  const longa = !!opcoes.longa, semCopia = opcoes.semCopia || longa;
  const V = { ini: deISO(ag.inicio), fim: longa ? Math.max(deISO(ag.fim), Date.UTC(anos[anos.length - 1], 11, 31)) : deISO(ag.fim), hoje: deISO(ag.hoje) };
  const card = new Map((r.cardapio || []).map((c) => [c.cultura, c]));
  const marcoMetade = (ag.linhas || []).flatMap((l) => l.marcos || []).find((m) => /metade/.test(m.rotulo || ""));
  const copiar = (parte, nome, est) => (semCopia ? null : copiaDaAgenda(ag, parte, nome, est));
  let metadePosta = false;
  const out = [];
  for (const f of plano.faixas) {
    for (let k = 0; k < (longa ? anos.length : 2); k++) {
      const est = E0 + k, c = f.anos?.[k];
      if (!c) continue;
      const nome = baseNome(c.cultura);
      if (k && c.cultura === f.anos[k - 1].cultura && (c.tipo === "tampão" || c.tipo === "perene")) continue; // a mesma mandioca ou perene
      if (nome === "Perene local") continue;
      if (c.ja_plantado) {
        if (!k) out.push({ parte: f.parte, cultura: c.cultura, tipo: c.tipo || "perene", estacao: est, barras: [], marcos: [],
          plantar: "já está plantado: segue como está", colher: "—", fonte: "resposta sua (o que planta hoje)" });
        continue;
      }
      if (c.ja_no_chao) {
        const l = !semCopia && (ag.linhas || []).find((x) => x.cultura === nome && x.estacao === est && /já está no chão/.test(x.plantar || ""));
        out.push(l ? { ...JSON.parse(JSON.stringify(l)), parte: f.parte } : linhaJaNoChao(V, r, f.parte, nome, est));
        continue;
      }
      if (nome === "Pousio pastejado") {
        const l = !semCopia && (ag.linhas || []).find((x) => x.tipo === "pousio" && x.estacao === est);
        const lin = l ? { ...JSON.parse(JSON.stringify(l)), parte: f.parte } : linhaPousio(V, r, f.parte, est);
        if (lin) out.push(lin);
        continue;
      }
      let lin = copiar(f.parte, nome, est);
      if (!lin) {
        const J = janela(r, nome) || janelaEstimada(r, nome);
        if (!J || J.semData) {
          if (k) continue; // plantio de 2028 sem data: fica fora do calendário (como no núcleo)
          lin = semJanela(f.parte, nome, c.tipo || TIPO[nome] || "pousio", est, J, !card.get(nome) || card.get(nome).situacao === "fora");
        } else {
          if (k && maisAnos(J.ini, est - 2027) > V.fim) continue;
          lin = linhaZarc(V, f.parte, nome, c.tipo || TIPO[nome] || "pousio", J, est);
        }
      }
      // a janela da palma vale para a borda (palma + gliricídia, como no núcleo) e para a palma numa parte do roçado
      const SUF_GLI = "; as mudas de gliricídia vão na mesma época (suposição)";
      if (/^Palma \+/.test(c.cultura)) { lin.cultura = c.cultura; if (!lin.fonte.includes(SUF_GLI)) lin.fonte += SUF_GLI; }
      else { lin.cultura = nome; lin.fonte = String(lin.fonte || "").replace(SUF_GLI, ""); }
      if (marcoMetade && !metadePosta && k === 0 && /^Parte /.test(f.parte) && nome === leg && /metade guardada/.test(c.texto || "")) {
        lin.marcos = [{ ...marcoMetade }];
        lin.plantar += "; ano de alerta: plante metade e guarde a outra até ~10/mar";
        metadePosta = true;
      }
      out.push(lin);
      if (f.parte === "Baixio" && (nome === "Milho" || nome === "Sorgo granífero")) {
        const jm = janelaDaLinha(lin);
        if (jm && c.mucuna) { const lm = linhaMucuna(V, jm, est); if (lm) out.push(lm); }
        // a célula manda: "solteiro" ou "sem revezamento" no texto (ex.: sorgo granífero solteiro no baixio) não ganha a linha
        else if (jm && leg && !c.solteiro && !/solteiro|sem revezamento/.test(c.texto || "") && jm.ini + 50 * DIA <= V.fim - 14 * DIA) {
          const nomeR = `${leg} no milho em pé`;
          const l = !semCopia && (ag.linhas || []).find((x) => x.cultura === nomeR && x.estacao === est);
          out.push(l ? JSON.parse(JSON.stringify(l)) : linhaRevez(V, r, jm, leg, est));
        }
      }
    }
  }
  return out;
}

// ------------------------------------------------------------------ o que as telas mostram
/** O plano escolhido: { tipo: "melhor" | "ideal" (chave `plano`: "" = melhorado, o padrão; "ideal"), prioridade, prioridade_origem,
 *  nome, plano, linhas (agendaDe) }. O Plano, o Dinheiro e o Relatório mostram este. */
export function escolhido(r, resp = {}, ef = {}) {
  const tipo = resp?.plano === "ideal" ? "ideal" : "melhor";
  const prioridade = prioridadePadrao(r, resp, ef);
  const plano = tipo === "ideal" ? planoIdeal(r, resp, ef, prioridade) : planoMelhor(r, resp, ef);
  const resposta = PRIORIDADES.includes(resp?.prioridade) || (ef?.prioridade_origem === "resposta" && PRIORIDADES.includes(ef?.prioridade));
  const ep = resposta ? null : escolhaPadrao(r, resp, ef);
  const origem = resposta ? "resposta" : ep.motivo === "numeros" ? (alertaDe(r) ? "a que mais sobra em 2027" : "a que mais sobra")
    : alertaDe(r) ? "padrão em ano de alerta de El Niño" : "padrão";
  return { tipo, prioridade, prioridade_origem: origem,
    nome: tipo === "ideal" ? `O ideal · ${NOME_PRIORIDADE[prioridade]}` : "Seu jeito, melhorado", plano, linhas: plano ? agendaDe(r, plano, ef) : [] };
}
