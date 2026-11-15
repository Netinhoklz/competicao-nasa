// Passo 5, "Relatório" (roca.html#/<cod>/5): "O plano do seu roçado", com as datas exatas de quando fazer o quê e como
// (analise/fluxo2/BRIEFING.md, D7; agente C4, 15/11/2026). O plano é o que o Plano mostra (ideal.escolhido: chaves `plano` e
// `prioridade`). De cima para baixo: o cabeçalho (lugar, hoje, tamanho, terra, baixio, plano e prioridade); "O que fazer e quando"
// (uma linha por tarefa, por mês, de hoje a dez/2027; 2028 e 2029 resumidos por ano); o desenho pequeno do roçado e o material
// (extras/terreno.js, do C1); o "como fazer, cultura por cultura" (depois do material: na folha impressa o texto longo, que pode
// partir, fecha a última folha); o fim com o "Imprimir / salvar PDF" e a frase do ponto 16 (na folha impressa). O bloco "Leve para o
// técnico" saiu do Relatório (pedido do José, 15/11): fica só o relatório e a geração dele (PDF e WhatsApp).
// Visual (pedido do José, 15/11): os cartões de Sua roça (ícone grande na cor do assunto + título curto), a ficha numa grade de 3
// colunas (ícone + rótulo | valor | "Mudar") e, no PDF, os mesmos cartões na folha clara, com a faixa do QUADRA no alto.
// Regras: datas SÓ de escolhido().linhas (ideal.agendaDe, as barras de/ate e o rótulo sem corte) e de r.agenda.marcos; o "como"
// SÓ de dados/agronomia.json (A1), por cultura e por operação; nada inventado (sem dado, "com o técnico").
// Verde: "Mandar no WhatsApp" (compartilhar de leve_ao_tecnico.js, com as próximas 5 tarefas); secundário: "Imprimir / salvar PDF"
// (window.print(), folha clara A4 do quadra.css + css/passos/relatorio.css). As funções puras (dados, tarefas, proximas, texto)
// rodam no node: testes/ferramentas/teste_relatorio.mjs confere que toda data do relatório existe na agenda.
import * as U from "../comum.js";
import { escolhido, agronomia, NOME_PRIORIDADE, falaTexto } from "../extras/ideal.js";
import { montar } from "./plantio/desenho.js";
import { carregarAgronomia, contas, dadosCultura, qtdTxt, svgTerreno, dist, haTxt } from "../extras/terreno.js";
import { FRASE, olho, OLHOS } from "../extras/voce_decide.js";

// ------------------------------------------------------------------ vocabulário
const MES_LONGO = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
const FALA = { "Feijão-caupi": "feijão", "Feijão comum": "feijão comum", "Sorgo forrageiro": "sorgo forrageiro", "Sorgo granífero": "sorgo de grão",
  "Palma forrageira": "palma", "Palma + gliricídia": "palma e gliricídia", "Pousio pastejado": "descanso", "Mucuna-preta": "mucuna",
  "Algodão herbáceo": "algodão", "Cana-de-açúcar": "cana" };
const fala = (c) => FALA[c] || String(c || "").toLowerCase();
const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);
const lista = (xs) => (xs.length <= 1 ? xs.join("") : `${xs.slice(0, -1).join(", ")} e ${xs[xs.length - 1]}`);
const uniq = (xs) => [...new Set(xs)];
const ORD_PARTE = ["Parte A", "Parte B", "Parte C", "Baixio", "Bordas"];
const ordParte = (p) => { const i = ORD_PARTE.indexOf(p); return i < 0 ? 9 : i; };
const ORD_TIPO = { hoje: 0, marco: 1, preparo: 2, plantio: 3, colheita: 4, pousio: 5 };
const GRAO = new Set(["Feijão-caupi", "Feijão comum", "Milho", "Amendoim", "Sorgo granífero", "Guandu"]); // guardar semente
const baseCult = (c) => String(c || "").replace(/ no milho em pé$/, "");
const PLURAL = { semente: "sementes", maniva: "manivas", raquete: "raquetes", muda: "mudas", estaca: "estacas" };
// a terra e o baixio com as palavras de Sua roça (perguntas.js): o nome e, embaixo, o que a terra faz na chuva
const TERRA = { nao_sei: ["Não sei", ""], arenosa: ["Areia", "seca rápido"], mista: ["Misturada", "segura água"], barro: ["Barro", "encharca"] };
const BAIXIO = { nao_sei: "Não sei", nao: "Não tenho", pouco: "Pequeno", terco: "Um terço", metade: "Grande" };
// ícones de Sua roça que não estão em comum.js (o mesmo desenho de perguntas.js): o terreno com as duas medidas e o baixio de lado
const ICR = {
  terreno: '<rect x="7" y="8" width="14" height="13" rx="1.5"/><path d="M7 4h14M7 2.6v2.8M21 2.6v2.8M3 8v13M1.6 21h2.8M1.6 8h2.8"/>',
  baixio: '<path d="M2 7c5 0 7 1.8 9 5.8S15 18 17 18h5"/><path d="M14.5 21h7.5M5 2.5l-.8 2M9 2l-.8 2"/>',
};
const icr = (nome) => (ICR[nome] ? `<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">${ICR[nome]}</svg>` : U.ic(nome));
// a prioridade do ideal com o ícone do Plano (plantio.js, PRIO) e a cor do assunto: água azul, renda âmbar, solo cor de barro
const PRIO_COR = { garantir: ["gota", "agua"], vender: ["dinheiro", "tamanho"], solo: ["broto", "terra"], equilibrar: ["faixas", "planta"] };

/** "Parte A", "Partes A e B", "Parte B e baixio", "Bordas". */
export function ondeTxt(partes) {
  const ps = uniq(partes).sort((a, b) => ordParte(a) - ordParte(b));
  const letras = ps.filter((p) => /^Parte /.test(p)).map((p) => p.slice(6));
  const out = letras.length === 1 ? [`Parte ${letras[0]}`] : letras.length ? [`Partes ${lista(letras)}`] : [];
  for (const [p, nome] of [["Baixio", "baixio"], ["Bordas", "bordas"]]) if (ps.includes(p)) out.push(out.length ? nome : cap(nome));
  for (const p of ps) if (!/^Parte /.test(p) && p !== "Baixio" && p !== "Bordas") out.push(p);
  return lista(out);
}

const t = (iso) => Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10));
const dmy = (iso) => U.dataBR(iso); // "2027-03-11" → "11/03/2027"
const mesDe = (iso) => `${MES_LONGO[+iso.slice(5, 7) - 1]} de ${iso.slice(0, 4)}`;
/** "de 15/11/2026 a 30/11/2026" em texto curto: "15/11/2026 a 30/11/2026" ou "até 31/12/2026". */
export const periodo = (x) => (x.ate ? (x.ate === x.de ? dmy(x.de) : `${dmy(x.de)} a ${dmy(x.ate)}`) : `${x.prazo ? "até " : ""}${dmy(x.de)}`);

// ------------------------------------------------------------------ o "como" (agronomia.json, do A1)
const ops = (agro) => agro?.operacoes || {};
function capina(agro, nome) {
  const c = ops(agro).capina?.como || [];
  const dur = /Mamona|Algodão/.test(nome) ? c.find((s) => /mamona/i.test(s)) : c.find((s) => /começo/i.test(s));
  return [dur, nome === "Mandioca" ? c.find((s) => /mandioca/i.test(s)) : null, c.find((s) => /cobertura/i.test(s))].filter(Boolean);
}
const COLHE = [[/^Amendoim$/, /^amendoim/i], [/^Mamona$/, /^mamona/i], [/^Sorgo forrageiro$/, /^sorgo/i], [/^Palma/, /^palma/i]];
function colheitaEsp(agro, nome) {
  const par = COLHE.find(([re]) => re.test(nome));
  const op = par && (ops(agro).colheita?.como || []).find((s) => par[1].test(s));
  if (op) return { txt: op.replace(/^[^:]+:\s*/, "").replace(/^./, (x) => x.toUpperCase()), fonte: fonteOp(agro, "colheita") };
  const d = dadosCultura(agro, baseCult(nome)), c = (d?.como || []).find((s) => /colh/i.test(s));
  return c ? { txt: c, fonte: d.fonte || "" } : null;
}
const artigo = (c) => (/^(mandioca|palma|mamona|mucuna|gliric|cana|banana)/i.test(fala(c)) ? "a" : "o");
const fonteOp = (agro, id) => ops(agro)[id]?.fonte || "";

/** Espaçamento de um item das contas do C1 ("carreiras a 80 cm · covas a 50 cm · 3 sementes por cova · 3–7 cm de fundo"). */
function espTxt(it) {
  if (!it?.covas) return null;
  const d = it.dados || {};
  if (it.papel === "dentro" || it.papel === "fora") return `${fala(it.cultura)} por ${it.papel}, a cada ${dist(U, it.entre_covas_m)}`;
  if (d.por_cova == null) return null; // algodão: a fonte dá plantas por metro (vai a frase do "como")
  const pc = `${it.por_cova} ${it.por_cova === 1 ? (it.material || "semente") : PLURAL[it.material] || "sementes"} por cova`;
  const prof = /^\d/.test(String(d.profundidade_cm || "")) ? `${d.profundidade_cm} cm de fundo` : "";
  return [`carreiras a ${dist(U, it.entre_linhas_m)}`, `covas a ${dist(U, it.entre_covas_m)}`, pc, prof].filter(Boolean).join(" · ");
}

/** O material de uma lista de itens das contas do C1, somado por cultura: "≈ 2,6 kg de semente", "≈ 560 raquetes e 56 mudas".
 *  Sem kg na fonte (milho), o número de sementes (covas × por cova); sem dado, nada (o texto diz "com o técnico"). */
function somar(itens) {
  const g = new Map();
  for (const it of itens) {
    let q = it.quantidade, un = it.unidade;
    if ((q === null || q === undefined) && it.covas && it.material === "semente" && it.dados?.por_cova) { q = it.covas * it.por_cova; un = "sementes"; }
    if (q === null || q === undefined || !un) continue;
    const k = `${it.cultura}|${un}`;
    const x = g.get(k) || { cultura: it.cultura, unidade: un, quantidade: 0, onde: [] };
    x.quantidade += q;
    g.set(k, x);
  }
  return [...g.values()];
}
const qtd = (x) => `${qtdTxt(U, x)}${x.unidade === "kg" ? " de semente" : ""}`;
const leveTxt = (itens) => somar(itens).map(qtd).join(" e ").replace(/ e ≈ /g, " e ");

// ------------------------------------------------------------------ os dados do relatório (sem DOM)
/** Cerca viva: a gliricídia (entre_linhas_m null no agronomia.json = uma carreira só) vem sem covas das contas do C1; a conta do A1
 *  é o perímetro ÷ a distância entre covas (uma estaca a cada 5 m). Quando o contas() já trouxer as covas, nada muda aqui. */
function cerca(ct) {
  for (const l of ct.linhas) {
    if (l.id !== "Bordas" || !l.perimetroM) continue;
    l.itens = l.itens.map((it) => {
      if (it.covas || !it.entre_covas_m || !it.unidade || it.unidade === "kg") return it;
      const covas = Math.floor(l.perimetroM / it.entre_covas_m + 1e-6);
      return { ...it, linhasPorFaixa: 1, linhas: 1, covasPorLinha: covas, covas, quantidade: covas * it.por_cova };
    });
  }
  return ct;
}

/** Os itens das contas do C1 para uma tarefa de plantio (as partes dela, no ano k). */
function itensDe(cts, x) {
  const ct = cts[x.k];
  if (!ct) return [];
  return x.partes.flatMap((p) => {
    const l = ct.linhas.find((y) => y.parte === p);
    if (!l) return [];
    if (x.relay) return l.itens.filter((i) => i.papel === "entrelinhas");
    if (p === "Bordas") return l.itens;
    return l.itens.filter((i) => i.papel === "principal");
  });
}

/** Material por ano (k), somado por cultura, com onde vai; as partes que não pedem nada (descanso, já no chão, segue do ano
 *  anterior) vão em `nada`. */
export function materiaisDe(plano, cts, k, semData = []) {
  const ct = cts[k];
  if (!ct) return { itens: [], nada: [], semDado: [], semJanela: [] };
  const itens = [], nada = [], semDado = [], semJanela = [];
  const semJ = new Set(semData.map((x) => `${x.parte}|${baseCult(x.cultura)}`));
  for (const l of ct.linhas) {
    if (l.pousio) { nada.push({ parte: l.parte, txt: "descansa" }); continue; }
    if (l.nada) { nada.push({ parte: l.parte, txt: l.nada }); continue; } // a mesma regra do Plano (terreno.nadaDe)
    for (const it of l.itens) {
      // cultura sem data de plantar aqui (fora do zoneamento): sem tarefa de plantio, sem material; só com a data do técnico
      if (semJ.has(`${l.parte}|${it.cultura}`) || semJ.has(`${l.parte}|${l.cultura}`)) { semJanela.push({ parte: l.parte, cultura: it.cultura }); continue; }
      const s = somar([it]);
      if (!s.length) semDado.push({ parte: l.parte, cultura: it.cultura });
      for (const x of s) itens.push({ ...x, onde: [l.parte], se: !!l.incerto }); // baixio "não sei": à parte, "se tiver baixio"
    }
  }
  const g = new Map();
  for (const x of itens) {
    const k2 = `${x.cultura}|${x.unidade}|${x.se}`, y = g.get(k2);
    if (y) { y.quantidade += x.quantidade; y.onde.push(...x.onde); } else g.set(k2, { ...x, onde: [...x.onde] });
  }
  return { itens: [...g.values()], nada, semDado, semJanela };
}

/** Os textos dos marcos da agenda (os portões), sem jargão na frente; o texto do núcleo fica no "como fazer". */
const MARCOS = [
  [/^P1 · até/, "Ter o material garantido", "relogio"],
  [/^P2/, "Plantar uma parte e guardar a outra", "relogio"],
  [/metade guardada/, "Decidir a metade guardada", "relogio"],
  [/^P3/, "Último dia de troca (São José)", "relogio"],
  [/^P4/, "Salvar o que der: forragem e animais", "relogio"],
  [/^P5/, "Palha no chão, sem fogo", "relogio"],
  [/^P1 da estação/, "Recomeça o ciclo", "relogio"],
  [/^Início típico da chuva/, "A chuva costuma começar", "chuva"],
];
const SEM_JARGAO = [[/Palhada em vez de fogo, fenação do excedente, aceiro, perene em nível\./g, "Palha no chão em vez de fogo, feno do que sobrar, aceiro limpo e a palma plantada em nível."],
  [/O solo do SMAP volta a responder/g, "A umidade da terra, vista do satélite, volta a subir"],
  [/; anote a data e confira com o ZARC/g, "; anote a data e confira com o técnico a data do zoneamento"], [/lê a chuva desde/g, "olhe a chuva desde"],
  [/Luz acesa:/g, "Chuva fraca:"], [/Luz verde:/g, "Chuva boa:"], [/Luz vermelha ou amarela:/g, "Chuva fraca:"],
  [/fenação do excedente/g, "feno do que sobrar"], [/o oceano e o banco de água/g, "olhe o mar e a água guardada"], [/caupi precoce/g, "feijão de ciclo curto"]];
const semJargao = (s) => SEM_JARGAO.reduce((a, [re, b]) => a.replace(re, b), String(s || ""));

/**
 * Tudo o que o relatório mostra, sem DOM: { esc, lay, cts, tarefas, semData, avisos, anos, mat, notaPortoes, hoje }.
 * esc = escolhido(r, resp, ef); tarefas em ordem de data, cada uma { tipo: hoje|marco|preparo|plantio|colheita|pousio, de, ate,
 * prazo, partes, culturas, onde, oque, como, mais[], cond[], selos[{tipo, fonte}], icone, cor, aberta } (datas ISO da agenda).
 */
export function dados(r, resp, ef, agro) {
  const esc = escolhido(r, resp, ef);
  const plano = esc.plano, ag = r.agenda || {};
  const hoje = ag.hoje || new Date().toISOString().slice(0, 10), H = t(hoje);
  if (!plano?.faixas?.length) return { esc, plano: null, tarefas: [], semData: [], avisos: [], anos: [], mat: null, hoje };
  let lay = null;
  try { lay = montar(plano, ef); } catch (_) { lay = null; }
  const cts = lay ? (plano.anos || []).map((_, k) => cerca(contas(lay, k, agro, plano))) : [];
  const mapa = new Map(), semData = [];
  const novo = (key, base) => { if (!mapa.has(key)) mapa.set(key, { partes: [], culturas: [], linhas: [], riscos: [], cond: [], selos: [], mais: [], ...base }); return mapa.get(key); };
  const temMetade = esc.linhas.some((l) => (l.marcos || []).some((m) => /metade/.test(m.rotulo || "")));
  for (const l of esc.linhas) {
    const k = Math.max(0, (plano.anos || []).indexOf(l.estacao));
    const f = (plano.faixas || []).find((x) => x.parte === l.parte), cel = f?.anos?.[k];
    const relay = /no milho em pé$/.test(l.cultura), nome = baseCult(l.cultura);
    // o revezamento segue o texto da célula (como o desenho e o material do C1): "solteiro" ou "sem revezamento" não põe a 2ª cultura
    const tc = `${cel?.texto || ""}`;
    if (relay && cel && !cel.mucuna && !(/revezamento/i.test(tc) && !/sem revezamento/i.test(tc))) continue;
    if (!l.barras?.length) { semData.push({ parte: l.parte, cultura: l.cultura, txt: l.plantar || "", estacao: l.estacao }); continue; }
    const vivas = l.barras.filter((b) => t(b.ate) >= H);
    const riscos = l.barras.filter((b) => b.tipo === "risco");
    const temPlantio = vivas.some((b) => b.tipo === "plantio" || b.tipo === "estimado");
    for (const b of vivas) {
      let tipo = b.tipo === "estimado" ? "plantio" : b.tipo;
      if (tipo === "roca") continue; // "na roça, crescendo": vai no "depois de plantar" (capina e cobertura)
      if (tipo === "risco") { if (temPlantio || b !== vivas.find((x) => x.tipo === "risco")) continue; tipo = "plantio"; } // só sobrou o trecho com mais risco
      const key = tipo === "preparo" || tipo === "pousio" ? `${tipo}|${b.de}|${b.ate}` : `${tipo}|${nome}|${relay}|${b.de}|${b.ate}`;
      const x = novo(key, { tipo, de: b.de, ate: b.ate, k, relay, cultura: nome, tipoCult: l.tipo, estimado: b.tipo === "estimado",
        soRisco: b.tipo === "risco", rotulos: [] });
      x.partes.push(l.parte);
      x.culturas.push(nome);
      x.linhas.push(l);
      x.rotulos.push(b.rotulo);
      if (tipo === "plantio") x.riscos.push(...riscos.filter((y) => !x.riscos.some((z) => z.de === y.de && z.ate === y.ate)));
    }
  }
  for (const m of ag.marcos || []) {
    if (!m.data || m.data < hoje) continue;
    if (/janela do ZARC|verde do satélite/i.test(m.rotulo || "")) continue; // do plano do núcleo / sem ação para a família
    if (/metade/i.test(m.rotulo || "") && !temMetade) continue;
    const ehHoje = m.rotulo === "Hoje";
    novo(`marco|${m.data}|${m.rotulo}`, { tipo: ehHoje ? "hoje" : "marco", de: m.data, ate: null, prazo: /\baté\b/.test(m.rotulo || ""), marco: m });
  }
  const tarefas = [...mapa.values()];
  const E0 = (plano.anos || [2027])[0];
  const mat = materiaisDe(plano, cts, 0, semData.filter((x) => x.estacao === E0 && !/já está/.test(x.txt)));
  const bxIncerto = ef.tem_baixio === null;
  for (const x of tarefas) textos(x, { r, agro, cts, mat, hoje, esc, bxIncerto, semData });
  tarefas.sort((a, b) => (Math.max(t(a.de), H) - Math.max(t(b.de), H)) || (ORD_TIPO[a.tipo] - ORD_TIPO[b.tipo])
    || (ordParte(a.partes[0]) - ordParte(b.partes[0])) || String(a.oque).localeCompare(String(b.oque)));
  ajustesDeData(tarefas, ag);
  const avisos = (plano.avisos || []).map((a) => a.txt).filter(Boolean);
  return { esc, plano, lay, cts, tarefas, semData, avisos, anos: anos(plano, esc.linhas, cts), mat, hoje, bxIncerto,
    notaPortoes: ag.portoes === false ? ag.nota_portoes || "" : "" };
}

/** O "o quê", o "como" curto, o detalhe e as condições de uma tarefa. */
function textos(x, { r, agro, cts, mat, hoje, esc, bxIncerto }) {
  x.onde = x.partes.length ? ondeTxt(x.partes) : "";
  if (bxIncerto) x.onde = x.onde.replace(/\bbaixio\b/, "baixio (se tiver)").replace(/^Baixio\b/, "Baixio (se tiver)");
  x.cor = x.tipo === "marco" || x.tipo === "hoje" ? "" : x.tipo === "preparo" ? "pousio" : x.tipoCult || "pousio";
  x.aberta = x.de < hoje && x.tipo !== "hoje" && x.tipo !== "marco";
  // "Palma + gliricídia" (a cerca viva) junta o "como" das duas
  const ds = String(x.cultura || "").split(/\s*\+\s*/).map((n) => dadosCultura(agro, n)).filter(Boolean);
  const d = ds.length ? { como: ds.flatMap((y) => y.como || []), fonte: ds.map((y) => y.fonte).filter(Boolean).join("; ") } : null;
  const nomes = lista(uniq(x.culturas.flatMap((c) => String(c).split(/\s*\+\s*/)).map((c) => fala(c.replace(/^Palma$/, "Palma forrageira")))));
  if (x.tipo === "preparo") {
    const c = ops(agro).preparo_sem_fogo?.como || [];
    x.icone = "enxada";
    x.oque = "Preparar a terra sem fogo";
    x.para = nomes;
    x.como = c[0] || "Sem fogo: a palhada fica no chão.";
    x.mais = c.slice(1);
    x.selos = [{ tipo: "suposicao", fonte: "data: os 30 dias antes de abrir a janela de plantar (regra do calendário do QUADRA)" },
      ...(fonteOp(agro, "preparo_sem_fogo") ? [{ tipo: "medido", fonte: fonteOp(agro, "preparo_sem_fogo") }] : [])];
  } else if (x.tipo === "plantio") {
    const l = x.linhas[0], its = itensDe(cts, x);
    x.icone = "semente";
    x.oque = x.relay ? `Plantar ${fala(x.cultura)} no meio do milho` : `Plantar ${fala(x.cultura)}`;
    const esp = x.relay ? null : espTxt(its[0]) && (x.partes.includes("Bordas") ? its.map(espTxt).filter(Boolean).join(" · ") : espTxt(its[0]));
    const frase = x.relay ? (d?.como || []).find((s) => /milho/i.test(s)) || d?.como?.[0] : d?.como?.[0];
    const leve = leveTxt(its);
    x.como = [esp ? cap(esp) : frase || "Espaçamento: com o técnico", leve ? `Leve ${leve}` : ""].filter(Boolean)
      .map((y) => y.replace(/\.+$/, "")).join(". ") + ".";
    x.mais = [...(d?.como || []).filter((s) => s !== x.como && !(esp ? false : s === frase)),
      ...capina(agro, x.cultura).map((s, i) => (i ? s : `Depois de plantar: ${s.replace(/^./, (y) => y.toLowerCase())}`))];
    if (x.riscos.length && !x.soRisco) x.risco = `Também dá, com mais risco (até 4 em 10 anos com perda): ${x.riscos.map(periodo).join(" e ")}.`;
    const antes = x.riscos.filter((y) => y.ate < x.de).sort((a, b) => (a.de < b.de ? -1 : 1))[0];
    if (antes && !x.soRisco) x.cond.push(`Dá para plantar desde ${dmy(antes.de)}, com mais risco.`);
    if (x.soRisco) x.cond.push("Só com mais risco: até 4 em 10 anos com perda.");
    const metade = x.linhas.flatMap((y) => y.marcos || []).find((m) => /metade/.test(m.rotulo || ""));
    // a decisão da metade guardada é uma tarefa do dia; se ela cai antes desta janela, a condição diz isso (não dá para cumprir dentro)
    if (metade) x.cond.push(metade.data < x.de ? `Ano de alerta: plante conforme a decisão de ${dmy(metade.data)} (veja a tarefa do dia).`
      : `Ano de alerta: plante metade e guarde a outra até ${dmy(metade.data)}.`);
    if (x.estimado) x.cond.push("Data estimada: aqui não há zoneamento. Confirme com quem já planta.");
    const fora = /depois de (\d{2}\/\d{2}) fica fora do ZARC/.exec(l.fonte || "");
    if (fora) x.cond.push(`Semeado depois de ${fora[1]}, fica fora da data segura: mais risco.`);
    x.selos = [{ tipo: x.estimado || x.relay ? "suposicao" : /^ZARC/.test(l.fonte || "") ? "medido" : "suposicao", fonte: `data: ${l.fonte || "agenda do QUADRA"}` },
      ...(d?.fonte ? [{ tipo: "medido", fonte: `como: ${d.fonte}` }] : [])];
  } else if (x.tipo === "colheita") {
    const l = x.linhas[0], colher = l.colher || "";
    const dias = (/\((\d+\s*[–-]\s*\d+ (?:dias|meses))/.exec(colher) || [])[1];
    const reserva = x.rotulos.some((s) => /conforme a necessidade/.test(s));
    const ce = reserva ? null : colheitaEsp(agro, x.cultura), esp = ce?.txt || null;
    const guardar = GRAO.has(x.cultura) ? (ops(agro).guardar_semente?.como || []).filter((s) => !/^Amendoim/.test(s) || x.cultura === "Amendoim") : [];
    x.icone = "celeiro";
    x.oque = reserva ? `Colher ${fala(x.cultura)} conforme a necessidade` : /1º corte/.test(colher) ? `Cortar ${fala(x.cultura)}, 1º corte` : `Colher ${fala(x.cultura)}`;
    x.como = reserva ? "É a reserva: colha aos poucos, quando precisar." : esp || (dias ? `Fica pronto com ${dias} de plantado.` : guardar[0] || "");
    x.mais = [esp && dias ? `Fica pronto com ${dias} de plantado.` : "",
      ...guardar.map((s, i) => (i ? s : `Guarde semente: ${s.replace(/^./, (y) => y.toLowerCase())}`)),
      ...(ops(agro).cobertura?.como || []).slice(0, 1)].filter((s) => s && s !== x.como);
    x.selos = [{ tipo: "suposicao", fonte: `data: pelo ciclo da cultura (${colher || "agenda do QUADRA"})` },
      ...(ce?.fonte ? [{ tipo: "medido", fonte: `como: ${ce.fonte}` }] : [])];
  } else if (x.tipo === "pousio") {
    x.icone = "vaca";
    x.oque = "Deixar descansar";
    x.como = "Não planta: o gado pasteja e a terra descansa.";
    x.selos = [{ tipo: "suposicao", fonte: x.linhas[0]?.fonte || "estação típica (IMERG)" }];
  } else if (x.tipo === "hoje") {
    x.icone = "ok";
    x.oque = "Juntar o material para 2027";
    const top = (mat?.itens || []).filter((y) => !y.se).slice(0, 3).map((y) => `${fala(y.cultura)} ${qtdTxt(U, y)}`);
    x.como = `${top.length ? `${cap(top.join(", "))}: ` : ""}a lista completa está no fim.`;
    x.mais = (ops(agro).preparo_sem_fogo?.como || []).slice(0, 1);
  } else {
    const m = x.marco, par = MARCOS.find(([re]) => re.test(m.rotulo || ""));
    x.icone = par?.[2] || "relogio";
    x.oque = par?.[1] || m.rotulo;
    if (/^P1 · até/.test(m.rotulo || "")) {
      const its = (mat?.itens || []).filter((y) => !y.se).map((y) => `${fala(y.cultura)} ${qtdTxt(U, y)}`);
      x.como = `Semente, maniva e mudas da lista no fim${its.length ? ` (${its.slice(0, 3).join(", ")}${its.length > 3 ? "…" : ""})` : ""}. Adesão ao Garantia-Safra, se o município participa. Aceiro.`;
    } else {
      const ini = /(\d+) em 10 anos entre (\S+) e (\S+?)\./.exec(m.texto || "");
      x.como = ini ? `Em ${ini[1]} de 10 anos, começa entre ${ini[2]} e ${ini[3]}.` : semJargao(m.texto);
      x.como = cap(x.como.replace(/^(Último dia de troca\.|Só cabe salvar:|Recomeça o ciclo:)\s*/, "")); // o título já diz
    }
    x.mais = m.texto && x.como !== m.texto ? [`Na agenda: ${m.texto}`] : [];
    x.selos = [{ tipo: /chuva/.test(m.rotulo || "") ? "medido" : "suposicao", fonte: `agenda do QUADRA (${m.rotulo}): ${m.texto || ""}` }];
  }
}

/** 2028 e 2029, por ano: o que vai em cada parte (plano.faixas[].anos[k]), a colheita que cai no ano (r.agenda: colher em mês/ano)
 *  e o material novo daquele ano (contas do C1). */
function anos(plano, linhas, cts) {
  return (plano.anos || []).slice(1).map((ano, i) => {
    const k = i + 1;
    const partes = (plano.faixas || []).slice().sort((a, b) => ordParte(a.parte) - ordParte(b.parte)).map((f) => {
      const c = f.anos?.[k], ant = f.anos?.[k - 1];
      if (!c) return null;
      const segue = ant && ant.cultura === c.cultura && /tampão|perene/.test(c.tipo || "");
      const txt = falaTexto(c.texto);
      return { parte: f.parte, cultura: c.cultura, txt: segue && !txt ? "segue no chão" : txt, cor: c.tipo || "pousio" };
    }).filter(Boolean);
    const colher = [];
    for (const l of linhas.filter((y) => new RegExp(`^de (?:[a-z]{3}|\\d{2}/\\d{2})/${ano}`).test(y.colher || ""))) {
      const c = { partes: [l.parte], cultura: baseCult(l.cultura).replace(/^Palma.*/, "Palma forrageira"), txt: String(l.colher).replace(/;[^)]*\)/, ")") };
      const igual = colher.find((y) => y.cultura === c.cultura && y.txt === c.txt);
      if (igual) igual.partes.push(l.parte); else colher.push(c);
    }
    return { ano, partes, colher, mat: materiaisDe(plano, cts, k) };
  });
}

/** O que vai em cada parte no 1º ano, numa linha (para o WhatsApp): "2027: A e C caupi · B milho · baixio milho + caupi (faixas de 11 m)". */
export function resumoPartes(d) {
  const p = d.plano, grupos = [];
  for (const f of p.faixas || []) {
    if (f.parte === "Baixio" && !d.lay?.temBaixio) continue;
    const c = f.anos?.[0];
    if (!c) continue;
    const L = /^Parte /.test(f.parte) ? f.parte.slice(6) : f.parte === "Baixio" ? (d.bxIncerto ? "baixio (se tiver)" : "baixio") : "bordas";
    let nome = fala(c.cultura);
    if (f.parte === "Baixio" && c.mucuna) nome += " + mucuna";
    else if (f.parte === "Baixio" && p.leguminosa && !c.solteiro && /revezamento/i.test(c.texto || "") && !/sem revezamento/i.test(c.texto || "")) nome += ` + ${fala(p.leguminosa)}`;
    const g = grupos.find((x) => x.nome === nome && /^[A-C]$/.test(x.L[0]) && /^[A-C]$/.test(L));
    if (g) g.L.push(L); else grupos.push({ L: [L], nome });
  }
  const per = d.lay?.reserva ? ` · já plantado: ${lista(d.lay.reserva.culturas.map(fala))}` : "";
  return `${p.anos?.[0] || 2027}: ${grupos.map((g) => `${lista(g.L)} ${g.nome}`).join(" · ")}${per}${d.lay ? ` (faixas de ${U.num(d.lay.larguraFaixa, 0)} m)` : ""}`;
}
/** O material de 2027 numa linha (para o WhatsApp): "caupi ≈ 14 kg de semente, milho ≈ 33 mil sementes". */
export function materialCurto(d) {
  return (d.mat?.itens || []).map((y) => `${fala(y.cultura)} ${qtd(y)}${y.se ? " (se tiver baixio)" : ""}`).join(", ");
}

/** Depois de pôr em ordem: (1) o P2 ("plante uma parte e guarde a outra") que cai antes do 1º plantio do plano vira "ainda não plante",
 *  com a data do 1º plantio, e a parte/guarde vai para a 1ª tarefa de plantio; (2) o preparo longe do plantio (mais de 7 dias) não diz
 *  "plante logo depois" e diz quando é o plantio daquelas partes. Datas só da agenda (nenhuma muda). */
function ajustesDeData(tarefas, ag) {
  const pls = tarefas.filter((x) => x.tipo === "plantio").sort((a, b) => t(a.de) - t(b.de));
  const pl1 = pls[0];
  for (const x of tarefas) {
    if (x.tipo !== "marco" || !/^P2/.test(x.marco?.rotulo || "") || !pl1 || !(x.de < pl1.de)) continue;
    const quando = (/\(~([^)]+)\)/.exec(x.marco.texto || "") || [])[1];
    x.oque = "A chuva está voltando: ainda não plante";
    x.como = `A umidade da terra, vista do satélite, volta a subir${quando ? ` (~${quando})` : ""}. ${cap(artigo(pl1.cultura))} ${fala(pl1.cultura)} é de ${periodo(pl1)}: espere essa data e confira com o técnico a data do zoneamento.`;
    x.mais = [];
    if (!pl1.cond.some((c) => /Ano de alerta/.test(c))) pl1.cond.push("Ano de alerta: plante uma parte e guarde a outra semente.");
  }
  for (const x of tarefas) {
    if (x.tipo !== "preparo") continue;
    const pl = pls.find((y) => y.de > x.ate && y.partes.some((q) => x.partes.includes(q)));
    if (!pl || t(pl.de) - t(x.ate) <= 7 * 864e5) continue;
    x.mais = x.mais.filter((s) => !/^Plante logo depois/.test(s));
    x.mais.push(`O plantio destas partes é de ${periodo(pl)}.`);
  }
  return ag;
}

/** As próximas n tarefas, em texto (para o WhatsApp): "21/02/2027 a 28/02/2027 · Plantar milho (Parte B e baixio)". */
export function proximas(d, n = 5) {
  return d.tarefas.filter((x) => x.tipo !== "hoje").slice(0, n).map((x) => `${periodo(x)} · ${x.oque}${x.onde ? ` (${x.onde})` : ""}`);
}

// ------------------------------------------------------------------ a página
const selos = (ss) => ss.map((s) => U.selo(s.tipo, s.fonte)).join(" ");

function tarefaHtml(x) {
  const data = `<span class="rl-data"><b>${x.prazo ? `<small>até</small> ` : ""}${dmy(x.de)}</b>${x.ate && x.ate !== x.de ? `<span>a ${dmy(x.ate)}</span>` : ""}${x.aberta ? `<em>já aberta</em>` : ""}</span>`;
  const onde = x.onde ? `<span class="rl-onde">${U.esc(x.onde)}</span>` : "";
  const para = x.para ? ` <span class="rl-para">para ${U.esc(x.para)}</span>` : "";
  const cond = x.cond.map((c) => `<span class="rl-cond">${U.ic("alerta")}<span>${U.esc(c)}</span></span>`).join("");
  const mais = x.mais.length || x.selos.length || x.risco ? `<div class="rl-mais">${x.risco ? `<p class="rl-m-risco">${U.esc(x.risco)}</p>` : ""}
      ${x.mais.length ? `<ul>${x.mais.map((s) => `<li>${U.esc(s)}</li>`).join("")}</ul>` : ""}
      ${x.selos.length ? `<p class="rl-fontes">${selos(x.selos)}</p>` : ""}</div>` : "";
  const cls = `rl-tarefa rl-${x.tipo}${x.cor ? ` ${U.tipoCss(x.cor)}` : ""}`;
  const corpo = `${data}<span class="rl-corpo"><span class="rl-oque">${U.ic(x.icone || "calendario")}<b>${U.esc(x.oque)}</b>${onde}${para}</span>
      <span class="rl-como">${U.esc(x.como || "")}</span>${cond}</span>`;
  return mais ? `<li><details class="${cls}"><summary>${corpo}<span class="rl-abre" aria-hidden="true"></span></summary>${mais}</details></li>`
    : `<li><div class="${cls}">${corpo}</div></li>`;
}

function listaHtml(d) {
  const meses = [];
  for (const x of d.tarefas) {
    const m = mesDe(x.de < d.hoje ? d.hoje : x.de);
    if (!meses.length || meses[meses.length - 1].m !== m) meses.push({ m, xs: [] });
    meses[meses.length - 1].xs.push(x);
  }
  return meses.map((g) => `<div class="rl-mes"><h3 class="rl-mes-tit">${U.esc(g.m)}</h3><ol class="rl-lista">${g.xs.map(tarefaHtml).join("")}</ol></div>`).join("");
}

function anosHtml(d) {
  if (!d.anos.length) return "";
  // cada ano num cartão (lado a lado no computador e na folha); a parte numa coluna de largura fixa e o que vai nela ao lado
  return `<div class="rl-depois"><h3 class="rl-mes-tit">Depois: ${d.anos.map((a) => a.ano).join(" e ")}</h3><div class="rl-anos">
    ${d.anos.map((a) => {
      const mat = a.mat.itens.map((y) => `${fala(y.cultura)} ${qtd(y)}${y.se ? " (se tiver baixio)" : ""}`);
      return `<div class="rl-ano"><p class="rl-ano-tit">${a.ano}</p><ul>
        ${a.partes.map((p) => `<li class="${U.tipoCss(p.cor)}"><b>${U.esc(ondeTxt([p.parte]))}</b><span>${U.esc(fala(p.cultura))}${p.txt ? `: ${U.esc(p.txt)}` : ""}</span></li>`).join("")}
        ${a.colher.map((c) => `<li class="rl-ano-colhe">${U.ic("celeiro")}<span>Colher ${U.esc(fala(c.cultura))} (${U.esc(ondeTxt(c.partes))}): ${U.esc(c.txt)}</span></li>`).join("")}</ul>
        ${mat.length ? `<p class="rl-ano-mat">Material novo: ${U.esc(mat.join("; "))}.</p>` : ""}</div>`;
    }).join("")}</div>
    <p class="rl-nota">As datas de ${d.anos.map((a) => a.ano).join(" e ")} repetem as janelas de 2027 (o zoneamento novo ainda não saiu): confira com o técnico no fim de 2027.</p></div>`;
}

/** "Como fazer, cultura por cultura": o "como" do agronomia.json uma vez só (cada cultura do plano e cada operação usada). Na tela
 *  fica fechado (cada tarefa já abre o dela); na folha impressa substitui o detalhe das tarefas, que se repete. */
function guiaHtml(d, agro) {
  const cults = uniq(d.tarefas.filter((x) => x.tipo === "plantio").flatMap((x) => String(x.cultura).split(/\s*\+\s*/)));
  const blocos = uniq(cults.map((c) => dadosCultura(agro, c)?.nome).filter(Boolean)).map((n) => dadosCultura(agro, n))
    .filter((y) => y?.como?.length).map((y) => ({ tit: cap(fala(y.nome)), como: y.como, fonte: y.fonte }));
  const usa = new Set(d.tarefas.map((x) => x.tipo)), nomes = new Set(d.tarefas.map((x) => x.cultura));
  const colheRe = COLHE.filter(([re]) => [...nomes].some((n) => re.test(n))).map(([, re]) => re);
  for (const [id, tit, entra, filtro] of [["preparo_sem_fogo", "Preparo sem fogo", usa.has("preparo")], ["capina", "Capina", usa.has("plantio")],
    ["cobertura", "Palha no chão", usa.has("plantio")], ["colheita", "Colheita", usa.has("colheita"), (s) => colheRe.some((re) => re.test(s))],
    ["guardar_semente", "Guardar semente", d.tarefas.some((x) => x.tipo === "colheita" && GRAO.has(x.cultura))],
    ["adubacao_verde", "Adubação verde", d.tarefas.some((x) => /Mucuna/.test(x.cultura))]]) {
    const como = (ops(agro)[id]?.como || []).filter((s) => !filtro || filtro(s));
    if (entra && como.length) blocos.push({ tit, como, fonte: fonteOp(agro, id) });
  }
  if (!blocos.length) return "";
  // o alto do cartão é o próprio "abrir" (o + à direita, como o das tarefas)
  return `<details class="rl-guia"><summary class="rl-c-cab"><span class="rl-c-ic" aria-hidden="true">${U.ic("enxada")}</span>
    <h2 class="rl-c-tit">Como fazer, cultura por cultura</h2><span class="rl-abre" aria-hidden="true"></span></summary><div class="rl-guia-grade">
    ${blocos.map((b) => `<div class="rl-guia-b"><p class="rl-guia-tit">${U.esc(b.tit)} ${b.fonte ? U.selo("medido", b.fonte) : ""}</p>
      <ul>${b.como.map((s) => `<li>${U.esc(s)}</li>`).join("")}</ul></div>`).join("")}</div></details>`;
}

/** A ficha do roçado: uma linha por dado, numa grade de 3 colunas (ícone + rótulo | valor | "Mudar"); o "Mudar" vai num <dd> próprio
 *  (a coluna da direita, do mesmo tamanho em todas as linhas; "Hoje" fica com a célula vazia). No computador e na folha, 2 colunas. */
function cabecalho(ctx, d) {
  const { r, ef } = ctx, l = r.local || {}, e = d.esc;
  const tam = ef.larg ? [`${U.num(ef.larg)} × ${U.num(ef.comp)} m`, U.ha(ef.ha)] : [U.ha(ef.ha), ef.ha_origem === "resposta" ? "" : "(o típico daqui)"];
  const selTam = ef.ha_origem === "resposta" ? "" : U.selo("suposicao", `tamanho: ${ef.ha_origem}; ponha as suas medidas em Sua roça`);
  const [terra, terraSub] = TERRA[ef.terra] || TERRA.nao_sei;
  const mudar = (href, campo) => `<a class="rl-mudar" href="${href}"${campo ? ` data-editar="${campo}"` : ""}>Mudar</a>`;
  const link = (n, campo) => mudar(ctx.link ? ctx.link(n) : "#", campo);
  // [cor do assunto, ícone, rótulo, valor, embaixo do valor, "Mudar", selo]; o lugar muda no globo (o "Trocar" do topo)
  const linhas = [
    ["lugar", "pino", "Lugar", `${l.municipio || ""} (${l.uf || ""})`, "", mudar("index.html")],
    ["tempo", "calendario", "Hoje", dmy(d.hoje), "", ""],
    ["tamanho", "terreno", "Tamanho", tam[0], tam[1], link(2, "ha"), selTam],
    ["terra", "solo", "Terra", terra, terraSub, link(2, "terra")],
    ["agua", "baixio", "Baixio", BAIXIO[ef.baixio] || BAIXIO.nao_sei, ef.tem_baixio ? haTxt(U, ef.baixio_ha) : "", link(2, "baixio")],
    ["planta", "faixas", "Plano", e.tipo === "ideal" ? "O ideal" : e.nome, "", link(3)],
  ];
  if (e.tipo === "ideal") {
    const [icone, cor] = PRIO_COR[e.prioridade] || PRIO_COR.equilibrar;
    linhas.push([cor, icone, "Prioridade", NOME_PRIORIDADE[e.prioridade] || e.prioridade,
      `(${e.prioridade_origem === "resposta" ? "você escolheu" : e.prioridade_origem})`, link(3)]);
  }
  const n = Math.ceil(linhas.length / 2); // linhas por coluna no computador (a 2ª coluna começa na linha n)
  return `<dl class="rl-ficha" style="--linhas: ${n}">${linhas.map(([cor, icone, rot, val, sub, acao, selo = ""], i) => `
      <div class="rl-f rl-cor-${cor}${i === n ? " rl-f-col2" : ""}"><dt><span class="rl-f-ic" aria-hidden="true">${icr(icone)}</span><span>${rot}</span></dt>
        <dd class="rl-f-val"><b${cor === "lugar" ? ' translate="no"' : ""}>${U.esc(val)}</b>${sub || selo ? `<small>${U.esc(sub)}${selo ? ` ${selo}` : ""}</small>` : ""}</dd>
        <dd class="rl-f-acao">${acao}</dd></div>`).join("")}
    </dl>`;
}

/** O alto de um cartão, como em Sua roça: o ícone grande na cor do assunto e o título curto (e o selo, quando há). */
const cabCartao = (icone, titulo, selo = "") => `<div class="rl-c-cab"><span class="rl-c-ic" aria-hidden="true">${U.ic(icone)}</span>
    <h2 class="rl-c-tit">${titulo}</h2>${selo}</div>`;

function materialHtml(ctx, d, agro) {
  const its = d.mat?.itens || [];
  const svg = d.lay ? svgTerreno(U, d.lay, 0, { W: 300, Hmax: 220, agro, plano: d.plano }) : "";
  const fontes = d.cts[0]?.fontes || [];
  // o número grande e a unidade embaixo: "≈ 1,6 kg / de semente", "≈ 4.390 / raquetes"
  const q = (y) => (y.unidade === "kg" ? [qtdTxt(U, y), "de semente"] : (/^(.*\d) (\D+)$/.exec(qtdTxt(U, y)) || [0, qtdTxt(U, y), ""]).slice(1));
  const lin = its.map((y) => `<li><span class="rl-mat-q">${U.esc(q(y)[0])}${q(y)[1] ? ` <small>${U.esc(q(y)[1])}</small>` : ""}</span><span class="rl-mat-c"><b>${U.esc(cap(fala(y.cultura)))}</b>
      <small>${U.esc(y.se ? "se tiver baixio" : ondeTxt(y.onde))}</small></span></li>`).join("");
  const semDado = (d.mat?.semDado || []).map((y) => `${fala(y.cultura)} (${ondeTxt([y.parte])})`);
  const semJanela = (d.mat?.semJanela || []).map((y) => `${fala(y.cultura)} (${ondeTxt([y.parte])})`);
  const nada = (d.mat?.nada || []).map((y) => `${ondeTxt([y.parte])}: ${y.txt}`);
  return `<section class="painel rl-cartao rl-cor-planta rl-material" aria-label="O que juntar para ${d.plano.anos?.[0] || 2027}">
    ${cabCartao("semente", `O que juntar para ${d.plano.anos?.[0] || 2027}`, fontes.length ? U.selo("suposicao", `quantidades contadas sobre o desenho do seu roçado${d.lay?.medidas === "resposta" ? " (as suas medidas)" : " (quadrado do tamanho, sem as suas medidas)"}, sem sobra para replantio; espaçamento: ${fontes.join("; ")}`) : "")}
    <div class="rl-mat-grade">
      ${svg ? `<figure class="terreno rl-desenho">${svg}<figcaption>O seu roçado em ${d.plano.anos?.[0] || 2027}${d.lay.medidas === "resposta" ? "" : " (quadrado do tamanho; sem as suas medidas)"}.</figcaption></figure>` : ""}
      <div>${lin ? `<ul class="rl-mat">${lin}</ul>` : `<p class="rl-nota">Material: com o técnico (os dados de espaçamento não carregaram agora).</p>`}
        ${semDado.length ? `<p class="rl-nota">Com o técnico: ${U.esc(lista(semDado))}.</p>` : ""}
        ${semJanela.length ? `<p class="rl-nota">Só se o técnico der a data de plantar: ${U.esc(lista(semJanela))}.</p>` : ""}
        ${nada.length ? `<p class="rl-nota">Nada a levar: ${U.esc(nada.join("; "))}.</p>` : ""}
        <p class="rl-nota">Contado no seu roçado, sem sobra para replantar. Leve um pouco a mais.</p>
        ${olho(OLHOS.faixas)}</div>
    </div></section>`;
}

function html(ctx, d, agro) {
  // a faixa escura do QUADRA no alto da 1ª folha (só na impressão: na tela o topo já tem a marca); o nome do município e a UF
  // não passam pela tradução (translate="no", como na ficha)
  const l = ctx.r.local || {};
  const marca = `<div class="rl-marca"><span class="rl-marca-nome" translate="no"><span class="marca-selo"></span>QUADRA</span>
      <span class="rl-marca-lugar" translate="no">${U.esc(l.municipio || "")} (${U.esc(l.uf || "")}) · ${dmy(d.hoje)}</span></div>`;
  const cab = `${marca}<div class="titulo-passo"><p class="kicker">Relatório</p>
      <h1>O plano do seu roçado<span class="eco">O que fazer e quando.</span></h1></div>`;
  if (!d.plano) return `${cab}<div class="painel"><p>Ainda não há plano para este lugar. Volte ao Plano ou fale com o técnico.</p></div>`;
  const avisos = [...d.avisos, ...d.semData.map((s) => `${cap(fala(s.cultura))} (${ondeTxt([s.parte])}): ${s.txt}`)];
  const guia = guiaHtml(d, agro);
  const pdf = `<button type="button" class="botao secundario rl-pdf" data-rl="imprimir">${U.ic("faixas")}Imprimir / salvar PDF</button>`;
  return `${cab}
    <section class="painel rl-cartao rl-cab" aria-label="O seu roçado">${cabecalho(ctx, d)}
      <div class="rl-acoes">${pdf}</div></section>
    <section class="painel rl-cartao rl-cor-tempo rl-agenda" aria-label="O que fazer e quando">
      ${cabCartao("calendario", "O que fazer e quando")}
      <p class="rl-legenda">Plantar: ${U.selo("medido", "datas de plantar: ZARC (zoneamento agrícola de risco climático do MAPA) para este município, como na agenda do Plano")}
        · Colher: ${U.selo("suposicao", "datas de colher: pela duração do ciclo de cada cultura, contada do plantio")}
<span class="rl-toque"> · Toque numa tarefa para ver como fazer.</span></p>
      <p class="rl-geral">${U.ic("gota")}<span>Plante com a terra úmida, depois que a chuva firmar.</span></p>
      ${d.notaPortoes ? `<p class="rl-geral ambar">${U.ic("alerta")}<span>Aqui as datas de troca e de salvar ainda não foram medidas: combine com o técnico. ${U.selo("suposicao", d.notaPortoes)}</span></p>` : ""}
      ${avisos.length ? `<ul class="rl-avisos">${avisos.map((a) => `<li>${U.ic("alerta")}<span>${U.esc(a)}</span></li>`).join("")}</ul>` : ""}
      ${listaHtml(d)}
      ${anosHtml(d)}
    </section>
    ${materialHtml(ctx, d, agro)}
    ${guia ? `<section class="painel rl-cartao rl-cor-terra rl-guia-sec" aria-label="Como fazer">${guia}</section>` : ""}
    <section class="painel verde rl-fim" aria-label="Guardar o relatório">
      <p class="rl-fim-tit">${U.ic("ok")}<b>Pronto: este é o seu plano.</b></p>
      <p class="rl-fim-sub">Imprima, salve em PDF ou mande no WhatsApp.</p>
      <div class="rl-acoes">${pdf}<span class="rl-aviso" role="status" aria-live="polite"></span></div></section>
    <p class="rl-frase">${U.esc(FRASE)}</p>`;
}

// O CSS do desenho do C1 (css/extras/terreno.css), que o terreno.js só pede quando ele mesmo desenha.
function cssTerreno() {
  const href = new URL("../../css/extras/terreno.css", import.meta.url).href;
  return new Promise((ok) => {
    if ([...document.querySelectorAll("link[rel=stylesheet]")].some((l) => l.href === href)) return ok();
    document.head.appendChild(Object.assign(document.createElement("link"), { rel: "stylesheet", href, onload: ok, onerror: ok }));
  });
}

// Imprimir: abre todos os "ver mais" e as tarefas do relatório antes e fecha depois (também no Ctrl+P).
let fechados = [];
function abrirTudo() {
  if (!document.querySelector(".passo-relatorio") || document.body.classList.contains("imprime-tecnico")) return;
  fechados = [...document.querySelectorAll("#jornada details:not([open])")];
  fechados.forEach((x) => { x.open = true; });
}
function fecharDeNovo() { fechados.forEach((x) => { x.open = false; }); fechados = []; }
let ligado = false;
function ligarImpressao() {
  if (ligado) return;
  ligado = true;
  window.addEventListener("beforeprint", abrirTudo);
  window.addEventListener("afterprint", fecharDeNovo);
}

export default {
  id: "relatorio",
  titulo: "Relatório",
  css: true,
  async render(el, ctx) {
    const agro = agronomia() || await carregarAgronomia();
    const d = dados(ctx.r, ctx.resp, ctx.ef, agro);
    await cssTerreno();
    el.innerHTML = html(ctx, d, agro);
    ligarImpressao();
    el.querySelectorAll('[data-rl="imprimir"]').forEach((b) => b.addEventListener("click", () => { abrirTudo(); window.print(); }));
    // sem o bloco do técnico, o aviso do "copiou" (quando o WhatsApp não abre) fica no fim do relatório
    const avisar = (res) => {
      const a = el.querySelector(".rl-aviso");
      if (!a || (res !== "copiou" && res !== "falhou")) return;
      a.textContent = res === "copiou" ? "Copiado. Cole no WhatsApp." : "Não deu para copiar aqui.";
      a.scrollIntoView({ behavior: "smooth", block: "nearest" });
    };
    ctx.primario("Mandar no WhatsApp", () => import("../extras/leve_ao_tecnico.js")
      .then((m) => m.compartilhar(ctx, { plano: d.plano ? d.esc.nome : "", partes: d.plano ? resumoPartes(d) : "",
        material: d.plano ? materialCurto(d) : "", tarefas: d.plano ? proximas(d, 5) : [] })).then(avisar));
    await U.montarExtras(el, ctx);
  },
  // para o teste no node (testes/ferramentas/teste_relatorio.mjs): o HTML sem a página
  _html: html,
};
