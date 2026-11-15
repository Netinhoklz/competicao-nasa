// Confere o motor do ideal (web/js/extras/ideal.js) no node, com os JSON da API sem respostas salvos em testes/exemplos/api/
// (8 municípios) e uma matriz de respostas. Uso:
//   node testes/ferramentas/teste_ideal.mjs                 todos os municípios, a matriz inteira, resumo no fim
//   node testes/ferramentas/teste_ideal.mjs 2311306 -v      um município, imprimindo os planos e os 8 números
//   API=<pasta> node ...                                     outra pasta de JSON (ex.: respostas reais buscadas com curl)
// Sai com código 1 se alguma conferência falhar. O ef é montado com a mesma lógica de efetivas() de web/js/roca.js (copiada aqui).
import fs from "node:fs";
import { pathToFileURL, fileURLToPath } from "node:url";

const WEB = fileURLToPath(new URL("../../web/js/", import.meta.url));
const imp = (p) => import(pathToFileURL(WEB + p).href);
const I = await imp("extras/ideal.js");
const D = await imp("passos/plantio/desenho.js");
const C = await imp("passos/dinheiro/calculo.js");
const HI = await imp("extras/hoje_ideal.js");
const { CULT } = await imp("extras/culturas.js");

const DIR = process.env.API || fileURLToPath(new URL("../exemplos/api/", import.meta.url)); // respostas reais: API=testes/exemplos/api_respostas/
const args = process.argv.slice(2), verbose = args.includes("-v");
const cods = args.filter((a) => /^\d{7}$/.test(a));
const arquivos = fs.readdirSync(DIR).filter((f) => /^\d{7}(_.*)?\.json$/.test(f) && (!cods.length || cods.some((c) => f.startsWith(c))));

// ---------------------------------------------------------------- efetivas() de roca.js (copiada; não editar roca.js)
const TERRA = { arenosa: 1, mista: 1, barro: 1 };
const BAIXIO_FRAC = { nao: 0, pouco: 0.2, terco: 1 / 3, metade: 0.5, "": 1 / 3 };
function efetivas(resp, r) {
  const pad = r.padroes || {};
  const alerta = r.este_ano?.nivel_alerta === "alerta";
  const haResp = parseFloat(String(resp.ha || "").replace(",", "."));
  const padHa = pad.rocado_ha > 0 ? pad.rocado_ha : (pad.rocado_ha_padrao > 0 ? pad.rocado_ha_padrao : null);
  const area = haResp > 0 ? haResp : (padHa || 1);
  const frac = BAIXIO_FRAC[resp.baixio || ""] ?? 1 / 3;
  return {
    terra: TERRA[resp.terra] ? resp.terra : "nao_sei", ha: Math.round(area * 100) / 100,
    ha_origem: haResp > 0 ? "resposta" : "padrão", baixio: resp.baixio || "nao_sei",
    tem_baixio: resp.baixio === "nao" ? false : (resp.baixio ? true : null), baixio_frac: frac, baixio_ha: Math.round(area * frac * 100) / 100,
    agua: resp.agua || "chuva", maniva: resp.maniva || "tem", criacao: "nao_sei",
    prioridade: resp.prioridade || (alerta ? "garantir" : "equilibrar"), prioridade_origem: resp.prioridade ? "resposta" : "padrão",
    gs: "nao_sei", raiz: resp.raiz || "uf_mediana", custo: resp.custo || "semente",
    larg: +resp.larg || undefined, comp: +resp.comp || undefined,
  };
}

// ---------------------------------------------------------------- a matriz de respostas
const ANTONIO = { hoje: "milho:34,feijao:33,mandioca:33", ha: "3", terra: "barro", baixio: "pouco" };
const MATRIZ = [
  ["padrão", {}],
  ["Seu Antônio", ANTONIO],
  ["só milho", { hoje: "milho:100" }],
  ["milho+feijão", { hoje: "milho:50,feijao:50" }],
  ["com caju", { hoje: "milho:40,feijao:40,caju:20" }],
  ["sem baixio", { ...ANTONIO, baixio: "nao" }],
  ["maniva não", { ...ANTONIO, maniva: "nao" }],
  ["maniva no chão", { ...ANTONIO, maniva: "plantada" }],
  ["antes=milho", { ...ANTONIO, antes: "2025:milho" }],
  ["antes=feijão", { hoje: "feijao:60,mandioca:40", antes: "2025:feijao" }],
  ["antes=descansou", { ...ANTONIO, antes: "2025:pousio" }],
  ["sem baixio, antes=milho", { hoje: "milho:50,feijao:50", baixio: "nao", antes: "2025:milho" }],
  ["só feijão", { hoje: "feijao:100" }],
  ["milho+sorgo", { hoje: "milho:50,sorgo:50" }],
  ["muitas", { hoje: "milho:20,feijao:20,mandioca:20,algodao:10,amendoim:10,palma:10,banana:10" }],
  ["só outra", { hoje: "outra:100" }],
  ["só mandioca", { hoje: "mandioca:100" }],
  ["só mandioca, sem rama", { hoje: "mandioca:100", maniva: "nao" }],
  ["mandioca no chão (tenho)", { hoje: "milho:25,feijao:25,mandioca:25,amendoim:25", ha: "0.4", baixio: "pouco" }],
  ["só palma", { hoje: "palma:100" }],
  ["mandioca + palma", { hoje: "mandioca:50,palma:50", larg: "40", comp: "100", ha: "0.4" }],
  ["areia", { ...ANTONIO, terra: "arenosa" }],
  ["em metros", { ...ANTONIO, ha: "", larg: "120", comp: "250" }],
  ...I.PRIORIDADES.map((p) => [`prioridade ${p}`, { ...ANTONIO, prioridade: p }]),
  ["plano=ideal", { ...ANTONIO, plano: "ideal" }],
];

// ---------------------------------------------------------------- conferências
let falhas = 0, oks = 0;
const erros = [];
const ok = (cond, msg) => { if (cond) oks++; else { falhas++; erros.push(msg); } };
const DATA = /^\d{4}-\d{2}-\d{2}$/;
const IDS = ["rs_tipico", "rs_el_nino", "quebra_10", "comida_kg", "raiz_kg", "forragem_t", "n_kg", "meses_coberto", "ponte_lagarta"];
const SELOS = new Set(["medido", "suposicao", "projecao"]);
const BANIDAS = ["5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde", "qualquer terra", "sem preço aqui",
  "ainda não vende", "à frente de hoje em"];

const ehParte = (f) => /^Parte /.test(f.parte);
const nomesPlano = (p) => new Set(p.faixas.filter((f) => ehParte(f) || f.parte === "Baixio").flatMap((f) => f.anos.map((c) => c.cultura)));

function confPlano(tag, p, r, ef) {
  ok(p && Array.isArray(p.faixas) && p.faixas.length >= 1, `${tag}: plano sem faixas`);
  if (!p) return;
  ok(Array.isArray(p.anos) && p.anos.length === 3, `${tag}: anos`);
  for (const f of p.faixas) {
    ok(Array.isArray(f.anos) && f.anos.length === 3 && f.anos.every((c) => c && c.cultura && c.tipo && typeof c.texto === "string"), `${tag}: ${f.parte} com célula incompleta`);
    ok(typeof f.por_que === "string" && f.por_que.length > 0, `${tag}: ${f.parte} sem por_que`);
  }
  ok(p.faixas.filter(ehParte).length === 3, `${tag}: precisa de 3 partes (calculo.js divide por 3)`);
  // desenha em plantio/desenho.js
  try {
    const lay = D.montar(p, ef);
    ok(lay.faixas.length >= 3 && Number.isFinite(lay.lado) && lay.faixas.every((x) => Number.isFinite(x.y0) && Number.isFinite(x.ha)), `${tag}: desenho com NaN`);
    for (let k = 0; k < 3; k++) { const g = D.grade(lay, k, "faixas"); ok(Number.isFinite(g.p), `${tag}: grade ano ${k}`); }
  } catch (e) { ok(false, `${tag}: desenho.montar falhou: ${e.message}`); }
  // a conta de calculo.js aceita o plano
  if (r.financeiro) {
    try { const m = C.montar({ ...r, plano: p }, ef); ok(m.itens.length === 3, `${tag}: calculo.montar`); } catch (e) { ok(false, `${tag}: calculo.montar falhou: ${e.message}`); }
  }
  const txt = JSON.stringify(p);
  for (const b of BANIDAS) ok(!txt.includes(b), `${tag}: frase banida "${b}"`);
}

/** Nada repete no mesmo chão (a mandioca fica 2 anos; perene e descanso ficam), nem gramínea atrás de gramínea, quando há outra planta. */
function confGiro(tag, p, alternativa) {
  if (p.nao_gira) return; // uma cultura só (ex.: só mandioca): ela volta ao mesmo chão, dito na nota
  for (const f of p.faixas.filter(ehParte)) {
    for (let k = 1; k < 3; k++) {
      const a = f.anos[k - 1], b = f.anos[k];
      if (a.tipo === "perene" || b.tipo === "perene" || a.tipo === "pousio") continue;
      if (a.cultura === "Mandioca" && b.cultura === "Mandioca") {
        ok(k < 2 || f.anos[0].cultura !== "Mandioca", `${tag}: ${f.parte} mandioca 3 anos seguidos`);
        continue;
      }
      if (alternativa) {
        ok(a.cultura !== b.cultura, `${tag}: ${f.parte} repete ${a.cultura} em ${p.anos[k]}`);
        ok(!(D.ehGram(a.cultura) && D.ehGram(b.cultura)), `${tag}: ${f.parte} gramínea atrás de gramínea em ${p.anos[k]}`);
      }
    }
  }
}

function confAgenda(tag, r, linhas) {
  ok(Array.isArray(linhas), `${tag}: agenda não é lista`);
  const ini = r.agenda.inicio, fim = r.agenda.fim;
  for (const l of linhas) {
    ok(l.parte && l.cultura && Number.isInteger(l.estacao) && Array.isArray(l.barras) && typeof l.plantar === "string", `${tag}: linha incompleta ${l.parte}/${l.cultura}`);
    for (const b of l.barras) {
      ok(DATA.test(b.de) && DATA.test(b.ate) && b.de <= b.ate && b.de >= ini && b.ate <= fim, `${tag}: barra fora do calendário ${l.parte}/${l.cultura} ${b.de}>${b.ate}`);
      ok(["preparo", "risco", "plantio", "estimado", "roca", "colheita", "pousio"].includes(b.tipo), `${tag}: tipo de barra ${b.tipo}`);
      ok(b.pista === 1 || b.pista === 2, `${tag}: pista`);
    }
  }
}

/** O calendário longo do mês a mês (agendaLonga, até dez do último ano do plano): barras dentro de hoje–dez/2029, todas as estações
 *  do plano e, na emenda (até r.agenda.fim), as mesmas barras do calendário curto que o Plano mostra até dez/2027. */
function confLonga(tag, r, plano, curtas) {
  const longas = I.agendaLonga(r, plano);
  const ini = r.agenda.inicio, fimCurto = r.agenda.fim, fim = `${plano.anos[plano.anos.length - 1]}-12-31`;
  ok(Array.isArray(longas) && longas.length >= curtas.length, `${tag}: calendário longo com menos linhas (${longas.length}) que o curto (${curtas.length})`);
  for (const l of longas) for (const b of l.barras) {
    ok(DATA.test(b.de) && DATA.test(b.ate) && b.de <= b.ate && b.de >= ini && b.ate <= fim, `${tag}: barra fora do calendário longo ${l.parte}/${l.cultura} ${b.de}>${b.ate}`);
  }
  const chave = (l) => `${l.parte}|${l.cultura}|${l.estacao}`, mapa = new Map(longas.map((l) => [chave(l), l]));
  const ate = (l) => l.barras.filter((b) => b.de <= fimCurto).map((b) => `${b.tipo}:${b.de}>${b.ate < fimCurto ? b.ate : fimCurto}`).join(" ");
  for (const l of curtas) {
    const m = mapa.get(chave(l));
    if (!m) { ok(false, `${tag}: o calendário longo não tem ${chave(l)}`); continue; }
    ok(ate(m) === ate(l), `${tag}: emenda diferente em ${chave(l)}\n      curto: ${ate(l)}\n      longo: ${ate(m)}`);
  }
  // depois da emenda, toda parte que gira tem o que fazer em cada ano seguinte; a cultura sem data de plantio aqui (nenhuma barra de
  // plantar dela no calendário) fica de fora, como no núcleo
  const base = (c) => c.replace(/^Palma.*/, "Palma forrageira");
  const comData = new Set(longas.filter((l) => l.barras.some((b) => b.tipo === "plantio" || b.tipo === "estimado")).map((l) => base(l.cultura)));
  for (const f of plano.faixas) for (let k = 1; k < plano.anos.length; k++) {
    const c = f.anos[k], antes = f.anos[k - 1];
    if (!c || c.ja_plantado || c.cultura === "Perene local" || (c.cultura === antes.cultura && (c.tipo === "tampão" || c.tipo === "perene"))) continue;
    if (!comData.has(base(c.cultura)) && c.cultura !== "Pousio pastejado") continue;
    ok(longas.some((l) => l.parte === f.parte && l.estacao === plano.anos[k]), `${tag}: ${f.parte} sem linha de ${c.cultura} em ${plano.anos[k]} no calendário longo`);
  }
}

/** As regras de data do motor (sem copiar nada de r.agenda.linhas) refazem as linhas que o núcleo escreveu para r.plano. */
function confRegrasData(tag, r, ef) {
  const meu = I.agendaDe(r, r.plano, ef, { refazer: true, semCopia: true });
  const deles = r.agenda.linhas;
  const chave = (l) => `${l.parte}|${l.cultura}|${l.estacao}`;
  const mapa = new Map(meu.map((l) => [chave(l), l]));
  let iguais = 0;
  for (const l of deles) {
    const m = mapa.get(chave(l));
    if (!m) { ok(false, `${tag}: regras de data não refazem ${chave(l)}`); continue; }
    const bar = (x) => x.barras.map((b) => `${b.tipo}:${b.de}>${b.ate}:${b.pista}:${b.rotulo}:${b.segue}`).join(" ");
    const igual = bar(m) === bar(l) && m.plantar === l.plantar && m.colher === l.colher && m.fonte === l.fonte
      && JSON.stringify(m.marcos.map((x) => x.data)) === JSON.stringify((l.marcos || []).map((x) => x.data));
    if (igual) iguais++;
    else ok(false, `${tag}: data diferente do núcleo em ${chave(l)}\n      núcleo: ${bar(l)} | ${l.plantar} | ${l.colher}\n      motor:  ${bar(m)} | ${m.plantar} | ${m.colher}`);
  }
  ok(meu.length === deles.length, `${tag}: ${meu.length} linhas refeitas, o núcleo tem ${deles.length}`);
  return { iguais, total: deles.length };
}

function confBeneficios(tag, b) {
  ok(b && Array.isArray(b.itens) && b.itens.length === IDS.length, `${tag}: beneficios precisa de ${IDS.length} itens`);
  if (!b) return;
  ok(JSON.stringify(b.itens.map((x) => x.id)) === JSON.stringify(IDS), `${tag}: ids dos benefícios`);
  for (const x of b.itens) {
    ok(SELOS.has(x.selo), `${tag}: selo ${x.id}`);
    ok(typeof x.fonte === "string" && x.fonte.length > 10, `${tag}: fonte de ${x.id}`);
    ok(x.valor === null || Number.isFinite(x.valor), `${tag}: valor de ${x.id}`);
    ok(x.valor !== null || /não medido/.test(x.fonte), `${tag}: ${x.id} null sem dizer "não medido"`);
    for (const ban of BANIDAS) ok(!x.fonte.includes(ban) && !x.rotulo.includes(ban), `${tag}: frase banida em ${x.id}`);
  }
}

// ---------------------------------------------------------------- melhorado sem monocultura (pedido do José, 15/11)
/** Partes A, B, C e Baixio (as bordas ficam fora): (a) todo ano ≥ 2 culturas plantadas (o feijão em revezamento no milho conta);
 *  (b) nenhuma parte com a mesma anual sozinha nos 3 anos (perene e descanso não contam); (c) nunca uma cultura só no plano. */
function confSemMono(tag, p) {
  const fx = p.faixas.filter((f) => ehParte(f) || f.parte === "Baixio");
  const nomesCel = (c) => [c.cultura, ...(/revezamento/.test(c.texto || "") || c.mucuna ? ["+leg"] : [])];
  for (let k = 0; k < 3; k++) {
    const cs = new Set(fx.map((f) => f.anos[k]).filter((c) => c.tipo !== "pousio").flatMap(nomesCel));
    ok(cs.size >= 2, `${tag}: monocultura em ${p.anos[k]} (só ${[...cs]})`);
  }
  for (const f of fx) {
    const c0 = f.anos[0];
    if (c0.tipo === "perene" || c0.tipo === "pousio") continue;
    ok(!f.anos.every((c) => c.cultura === c0.cultura && nomesCel(c).length < 2), `${tag}: ${f.parte} com ${c0.cultura} sozinho nos 3 anos`);
  }
  ok(new Set(fx.flatMap((f) => f.anos.filter((c) => c.tipo !== "pousio").map((c) => c.cultura))).size >= 2, `${tag}: uma cultura só no plano`);
}

// ---------------------------------------------------------------- ideal sem monocultura (pedido do José, 15/11)
/** Os 4 ideais, nas partes A, B, C e no baixio com área (as bordas ficam fora): (a) todo ano ≥ 2 plantas entre as partes plantadas
 *  (pousio não conta; sorgo de grão e sorgo do gado são a mesma planta; o feijão ou a mucuna no milho contam), o que já tira
 *  (c) uma planta só no plano; (b) nenhuma parte com a mesma anual sozinha nos 3 anos (perene não conta). */
function confIdealSemMono(tag, p, ef) {
  const grupo = (n) => (/^Sorgo/.test(n) ? "Sorgo" : n);
  const plantas = (c) => [grupo(c.cultura), ...(c.mucuna || /mucuna/i.test(c.texto || "") ? ["Mucuna-preta"]
    : !c.solteiro && /^\+ .*(feij|caupi|amendoim)/i.test(c.texto || "") ? [p.leguminosa || "Feijão-caupi"] : [])];
  const viva = (c) => c.tipo !== "pousio" && !/pousio/i.test(c.cultura);
  const fx = p.faixas.filter((f) => ehParte(f) || (f.parte === "Baixio" && ef.baixio_ha > 0));
  for (let k = 0; k < 3; k++) {
    const cs = new Set(fx.map((f) => f.anos[k]).filter(viva).flatMap(plantas));
    ok(cs.size >= 2, `${tag}: monocultura em ${p.anos[k]} (só ${[...cs]})`);
  }
  for (const f of fx) {
    const a = f.anos;
    if (a[0].tipo === "perene" || !viva(a[0])) continue;
    ok(!a.every((c) => c.cultura === a[0].cultura && (c.cultura === "Mandioca" || plantas(c).length < 2)), `${tag}: ${f.parte} com ${a[0].cultura} sozinho nos 3 anos`);
  }
}

// ---------------------------------------------------------------- roda
const tabela = [];
let regras = { iguais: 0, total: 0 };
const fmt = (v) => (v == null ? "—" : Math.abs(v) >= 100 ? String(Math.round(v)) : String(Math.round(v * 10) / 10));
for (const arq of arquivos) {
  const r = JSON.parse(fs.readFileSync(DIR + arq, "utf8"));
  const cod = arq.slice(0, 7), mun = r.local?.municipio || cod;
  const ef0 = efetivas({}, r);
  // identidade: equilibrar = r.plano (salvo monocultura no núcleo: sem_mono troca só as células dela); agendaDe(r.plano) = r.agenda.linhas
  const eq = I.planoIdeal(r, {}, ef0, "equilibrar");
  ok(!!eq.sem_mono || eq.faixas === r.plano.faixas, `${mun}: ideal equilibrar sem resposta deveria ter as faixas de r.plano`);
  ok(I.agendaDe(r, r.plano, ef0) === r.agenda.linhas, `${mun}: agendaDe(r.plano) deveria devolver r.agenda.linhas`);
  ok(!!eq.sem_mono || I.agendaDe(r, eq, ef0) === r.agenda.linhas, `${mun}: agendaDe(ideal equilibrar) deveria devolver r.agenda.linhas`);
  const rg = confRegrasData(mun, r, ef0);
  regras.iguais += rg.iguais; regras.total += rg.total;
  confLonga(`${mun} · r.plano`, r, r.plano, r.agenda.linhas);

  for (const [nome, resp] of MATRIZ) {
    const tag = `${mun} · ${nome}`;
    const ef = efetivas(resp, r);
    let pm, c3, esc;
    try {
      pm = I.planoMelhor(r, resp, ef);
      confPlano(`${tag} · melhor`, pm, r, ef);
      confSemMono(`${tag} · melhor`, pm);
      const h = HI.lerHoje(resp.hoje || "", r.padroes);
      const dele = new Set(Object.keys(h.cult).map((k) => CULT[k]?.motor).filter(Boolean));
      const mandHoje = h.informado && (h.cult.mandioca || 0) > 0;
      if (!dele.size) { dele.add("Milho"); dele.add("Feijão-caupi"); }
      if (ef.maniva === "nao") dele.delete("Mandioca");
      const PERENES = ["Palma forrageira", "Gliricídia", "Caju", "Banana", "Cana-de-açúcar", "Guandu"];
      if (![...dele].some((n) => !PERENES.includes(n)) && ef.maniva === "nao" && mandHoje) { dele.add("Milho"); dele.add("Feijão-caupi"); }
      // só as culturas dele (a mandioca que já está no chão, sem rama, colhe em 2027 e não replanta)
      const novas = (p) => new Set(p.faixas.filter((f) => ehParte(f) || f.parte === "Baixio").flatMap((f) => f.anos.filter((c) => !c.ja_no_chao).map((c) => c.cultura)));
      // (a leguminosa ou o cereal do lugar entram quando ele planta uma cultura só: pm.entrou, dito na nota "Entrou …")
      for (const n of novas(pm)) ok(dele.has(n) || pm.entrou?.includes(n), `${tag}: melhor tem ${n}, que ele não planta`);
      ok(!pm.entrou?.length || pm.notas.some((x) => /^Entr(ou|aram) /.test(x)), `${tag}: entrou ${pm.entrou} sem a nota`);
      if (ef.maniva === "nao") ok(!novas(pm).has("Mandioca"), `${tag}: maniva não, mas a mandioca nova ficou`);
      // a mandioca que ele marcou está no chão: o melhorado colhe em 2027 (como o hoje), qualquer que seja a resposta da maniva
      if (mandHoje && r.financeiro) ok(I.itensPlano(r, ef, pm).itens[0].some((i) => i.serie === "Mandioca"), `${tag}: a mandioca do chão não colhe em 2027 no melhorado`);
      // todo ano com colheita quando o hoje colhe (ex.: só mandioca não replanta as 3 partes juntas)
      if (r.financeiro) {
        const its = I.itensPlano(r, ef, pm).itens;
        const colheHoje = [...dele].some((n) => ["Milho", "Feijão-caupi", "Feijão comum", "Mandioca"].includes(n));
        for (let k = 0; k < 3; k++) ok(its[k].some((i) => i.serie) || !h.informado || !colheHoje, `${tag}: melhorado sem colheita em ${2027 + k}`);
      }
      const anuais0 = [...dele].filter((n) => !["Palma forrageira", "Gliricídia", "Caju", "Banana", "Cana-de-açúcar", "Guandu"].includes(n));
      const anuais = [...new Set([...anuais0, ...(pm.entrou || []).filter((n) => pm.faixas.some((f) => ehParte(f) && f.anos.some((c) => c.cultura === n)))])];
      const temNaoGram = anuais.some((n) => !D.ehGram(n));
      confGiro(`${tag} · melhor`, pm, anuais.length >= 2 && temNaoGram);
      if (anuais0.length <= 1) ok(!pm.nao_gira && pm.entrou?.length > 0, `${tag}: 1 cultura só e nada entrou para girar com ela`);
      // cereal no baixio quando há baixio e ele planta cereal
      const bx = pm.faixas.find((f) => f.parte === "Baixio");
      // (o JSON buscado com baixio=0 não tem baixio no r.plano: aí o melhor também não tem, mesmo se a matriz responder "pouco")
      const bxNoNucleo = r.plano.faixas.some((f) => f.parte === "Baixio");
      if (ef.tem_baixio !== false && bxNoNucleo && (dele.has("Milho") || dele.has("Sorgo granífero"))) ok(bx && ["Milho", "Sorgo granífero"].includes(bx.anos[0].cultura), `${tag}: cereal fora do baixio`);
      if (ef.tem_baixio === false) ok(!bx, `${tag}: sem baixio, mas o plano tem baixio`);
      // leguminosa antes do cereal, quando ele tem os dois
      if (dele.has("Feijão-caupi") && dele.has("Milho") && !pm.avisos.some((x) => x.id === "solo")) { // milho só no baixio (terra sem janela)
        const parLC = pm.faixas.filter(ehParte).some((f) => f.anos.some((c, k) => k && c.cultura === "Milho" && f.anos[k - 1].tipo === "leguminosa"));
        ok(parLC, `${tag}: nenhuma parte com feijão antes do milho`);
      }
      // o ano passado: gramínea 2 anos seguidos → nenhuma parte começa com gramínea (quando há outra planta)
      if (/milho/.test(resp.antes || "") && /milho/.test(resp.hoje || "milho") && temNaoGram) {
        ok(pm.faixas.filter(ehParte).every((f) => !D.ehGram(f.anos[0].cultura)), `${tag}: antes=milho e ainda começa com gramínea`);
        ok(pm.faixas.some((f) => /ali teve milho/.test(f.por_que)) || pm.faixas.filter(ehParte).every((f) => !D.ehGram(f.anos[0].cultura)), `${tag}: por_que do ano passado`);
      }
      // a mandioca no chão
      if (ef.maniva === "plantada" && dele.has("Mandioca")) ok(pm.faixas.some((f) => f.anos[0].ja_no_chao), `${tag}: maniva no chão sem ja_no_chao`);
      // partes desencontradas: cada papel do giro (leguminosa, outra anual, mandioca) dá um começo; com 3, nenhuma parte repete outra
      const LEGS = ["Feijão-caupi", "Feijão comum", "Amendoim", "Mucuna-preta"], an = [...dele].filter((n) => !PERENES.includes(n));
      const papeis = (an.some((n) => LEGS.includes(n)) ? 1 : 0) + (an.some((n) => !LEGS.includes(n) && n !== "Mandioca") ? 1 : 0)
        + (an.includes("Mandioca") && ef.maniva !== "nao" ? 1 : 0);
      const assin = new Set(pm.faixas.filter(ehParte).map((f) => f.anos.map((c) => c.cultura + (c.ja_no_chao ? "*" : "") + (c.m2 ? "2" : "")).join("|")));
      if (!pm.avisos.some((x) => x.id === "solo")) ok(assin.size >= Math.min(3, papeis), `${tag}: melhorado com partes iguais nos 3 anos`);
      if (h.cult.mandioca === 100) ok(assin.size >= 2, `${tag}: só mandioca com as 3 partes iguais`);
      // cultura fora do zoneamento: aviso
      for (const n of dele) { const c = (r.cardapio || []).find((x) => x.cultura === n); if (!c || c.situacao === "fora") ok(pm.avisos.some((a) => a.cultura === n), `${tag}: ${n} fora sem aviso`); }

      // os 4 ideais
      for (const pri of I.PRIORIDADES) {
        const pi = I.planoIdeal(r, resp, ef, pri);
        confPlano(`${tag} · ideal ${pri}`, pi, r, ef);
        ok(pi.prioridade === pri, `${tag}: prioridade do ideal`);
        const foraCard = new Set((r.cardapio || []).filter((c) => c.situacao === "fora").map((c) => c.cultura));
        for (const n of novas(pi)) ok(!foraCard.has(n), `${tag} · ideal ${pri}: ${n} está fora do cardápio daqui`);
        if (pri !== "equilibrar") confGiro(`${tag} · ideal ${pri}`, pi, false);
        confIdealSemMono(`${tag} · ideal ${pri}`, pi, ef);
        confAgenda(`${tag} · ideal ${pri}`, r, I.agendaDe(r, pi, ef));
        confLonga(`${tag} · ideal ${pri}`, r, pi, I.agendaDe(r, pi, ef));
      }
      confAgenda(`${tag} · melhor`, r, I.agendaDe(r, pm, ef));
      confLonga(`${tag} · melhor`, r, pm, I.agendaDe(r, pm, ef));
      // a revezamento do baixio aparece quando há milho no baixio e leguminosa
      if (bx && bx.anos[0].cultura === "Milho" && pm.leguminosa) {
        const ls = I.agendaDe(r, pm, ef);
        const jm = ls.find((l) => l.parte === "Baixio" && l.cultura === "Milho" && l.estacao === 2027);
        const pl = jm?.barras.find((b) => b.tipo === "plantio");
        if (pl && pl.de <= "2027-10-01") ok(ls.some((l) => /no milho em pé/.test(l.cultura)), `${tag}: baixio com milho e feijão sem a linha do revezamento`);
      }
      c3 = I.comparar3(r, resp, ef);
      for (const t of ["hoje", "melhor", "ideal"]) confBeneficios(`${tag} · ${t}`, c3[t].beneficios);
      esc = I.escolhido(r, resp, ef);
      ok(esc.tipo === (resp.plano === "ideal" ? "ideal" : "melhor"), `${tag}: escolhido.tipo`);
      ok(esc.prioridade === (resp.prioridade || I.prioridadePadrao(r, resp, ef)), `${tag}: escolhido.prioridade`);
      // a prioridade padrão nunca perde para outra nos 3 números (ano normal, 2027, quebra)
      if (!resp.prioridade) {
        const ep = I.escolhaPadrao(r, resp, ef), c = ep.cand.find((x) => x.p === esc.prioridade);
        if (ep.motivo === "numeros") ok(!ep.cand.some((o) => o !== c && o.t != null && o.e != null && o.t >= c.t && o.e >= c.e && (o.q ?? 99) <= (c.q ?? 99)
          && (o.t > c.t || o.e > c.e || (o.q ?? 99) < (c.q ?? 99))), `${tag}: a prioridade padrão ${esc.prioridade} perde para outra nos 3 números`);
      }
      // "comida colhida" é só grão; a raiz vem à parte
      for (const t of ["hoje", "melhor", "ideal"]) {
        const b = c3[t].beneficios, g = b?.itens.find((x) => x.id === "comida_kg"), rz = b?.itens.find((x) => x.id === "raiz_kg");
        if (g?.valor != null) ok(Math.abs(g.valor - g.detalhe.grao_kg) < 1e-6 && Math.abs((rz?.valor ?? 0) - g.detalhe.raiz_kg) < 1e-6, `${tag} · ${t}: grão e raiz somados`);
      }
      ok(Array.isArray(esc.linhas) && (esc.linhas.length > 0 || !r.agenda), `${tag}: escolhido sem linhas`);
    } catch (e) {
      ok(false, `${tag}: exceção ${e.stack}`);
      continue;
    }
    const v = (t, id) => c3[t].beneficios?.itens.find((x) => x.id === id)?.valor;
    // o melhorado tem sobra num ano normal quando o hoje tem (salvo sem rama para a mandioca, que sai do giro depois de 2027)
    if (v("hoje", "rs_tipico") > 0 && ef.maniva !== "nao") ok(v("melhor", "rs_tipico") > 0, `${tag}: melhorado sem sobra num ano normal (hoje ${Math.round(v("hoje", "rs_tipico"))})`);
    const t3 = (t) => c3[t].beneficios?.rs?.ok ? c3[t].beneficios.rs.tres_anos.p50 : null;
    tabela.push({ mun, nome, pri: c3.prioridade, h3: t3("hoje"), m3: t3("melhor"), i3: t3("ideal"),
      hT: v("hoje", "rs_tipico"), mT: v("melhor", "rs_tipico"), iT: v("ideal", "rs_tipico"),
      hE: v("hoje", "rs_el_nino"), mE: v("melhor", "rs_el_nino"), iE: v("ideal", "rs_el_nino"),
      hQ: v("hoje", "quebra_10"), mQ: v("melhor", "quebra_10"), iQ: v("ideal", "quebra_10"),
      hK: v("hoje", "comida_kg"), mK: v("melhor", "comida_kg"), iK: v("ideal", "comida_kg"),
      hF: v("hoje", "forragem_t"), mF: v("melhor", "forragem_t"), iF: v("ideal", "forragem_t"),
      hN: v("hoje", "n_kg"), mN: v("melhor", "n_kg"), iN: v("ideal", "n_kg"),
      hM: v("hoje", "meses_coberto"), mM: v("melhor", "meses_coberto"), iM: v("ideal", "meses_coberto"),
      hP: v("hoje", "ponte_lagarta"), mP: v("melhor", "ponte_lagarta"), iP: v("ideal", "ponte_lagarta"),
      giro: pm.faixas.map((f) => `${f.parte.replace("Parte ", "")}:${f.anos.map((c) => (c.cultura === "Feijão-caupi" ? "F" : c.cultura === "Mandioca" ? "M" : c.cultura === "Milho" ? "Mi" : c.cultura.slice(0, 3))).join("")}`).join(" ") });
    if (verbose) {
      console.log(`\n=== ${tag} (ef.ha ${ef.ha}, baixio ${ef.tem_baixio}, maniva ${ef.maniva}, prioridade ${c3.prioridade})`);
      for (const [rot, p] of [["MELHOR", pm], [`IDEAL ${c3.prioridade}`, c3.ideal.plano]]) {
        console.log(`  ${rot}: ${p.nome}${p.manchete ? " · " + p.manchete : ""}`);
        for (const f of p.faixas) console.log(`    ${f.parte.padEnd(8)} ${f.anos.map((c) => c.cultura + (c.ja_no_chao ? "*" : "")).join(" | ")}\n             ${f.por_que}`);
        if (p.notas?.length) console.log(`    notas: ${p.notas.join(" / ")}`);
      }
      for (const t of ["hoje", "melhor", "ideal"]) console.log(`  ${t.padEnd(6)} ${c3[t].beneficios.itens.map((x) => `${x.id}=${fmt(x.valor)}`).join("  ")}`);
    }
  }
}

// ---------------------------------------------------------------- Quixadá padrão: os números do passo 4
const qx = arquivos.find((f) => f.startsWith("2311306"));
if (qx) {
  const r = JSON.parse(fs.readFileSync(DIR + qx, "utf8")), ef = efetivas({}, r);
  const c = HI.comparar(r, ef, HI.lerHoje("", r.padroes));
  const hoje = I.beneficios(r, {}, ef, null, "hoje").rs.tres_anos.p50;
  const eq = I.beneficios(r, {}, ef, I.planoIdeal(r, {}, ef, "equilibrar"), "ideal").rs.tres_anos.p50;
  const mel = I.beneficios(r, {}, ef, I.planoMelhor(r, {}, ef), "melhor").rs.tres_anos.p50;
  const ga = I.beneficios(r, {}, ef, I.planoIdeal(r, {}, ef, "garantir"), "ideal").rs.tres_anos.p50;
  const dez = (v) => Math.round(v / 10) * 10;
  console.log(`\nQuixadá padrão, 3 anos (P50): comparar() do passo 4: hoje ${Math.round(c.hoje.f.p50)} / melhor ${Math.round(c.melhor.f.p50)} / ideal ${Math.round(c.ideal.f.p50)}`);
  console.log(`  ideal.js: hoje ${Math.round(hoje)} · melhorado ${Math.round(mel)} · ideal "um pouco de cada" ${Math.round(eq)} · ideal "guardar água" (padrão em ano de alerta) ${Math.round(ga)}`);
  ok(dez(hoje) === 2480, `Quixadá padrão: hoje deveria dar R$ 2.480 (deu ${dez(hoje)})`);
  ok(dez(eq) === 4360, `Quixadá padrão: ideal "um pouco de cada" deveria dar R$ 4.360 (deu ${dez(eq)})`);
  ok(Math.abs(hoje - c.hoje.f.p50) < 0.5 && Math.abs(eq - c.ideal.f.p50) < 0.5, "Quixadá padrão: ideal.js e comparar() deveriam bater no hoje e no ideal");
}

// ---------------------------------------------------------------- resumo
const col = (v) => fmt(v).padStart(6);
console.log(`\n${"município · caso".padEnd(36)} pri        | 3 anos: hoje  melh  ideal | ano típico: hoje  melh  ideal | 2027: hoje melh ideal | quebra/10 | kg/ano: hoje melh ideal | N kg | forr t | meses | ponte | giro do melhor`);
for (const t of tabela) {
  console.log(`${(t.mun + " · " + t.nome).slice(0, 36).padEnd(36)} ${t.pri.padEnd(10)} | ${col(t.h3)}${col(t.m3)}${col(t.i3)} | ${col(t.hT)}${col(t.mT)}${col(t.iT)} | ${col(t.hE)}${col(t.mE)}${col(t.iE)} | ${fmt(t.hQ)} ${fmt(t.mQ)} ${fmt(t.iQ)} | ${col(t.hK)}${col(t.mK)}${col(t.iK)} | ${fmt(t.hN)} ${fmt(t.mN)} ${fmt(t.iN)} | ${fmt(t.hF)} ${fmt(t.mF)} ${fmt(t.iF)} | ${fmt(t.hM)} ${fmt(t.mM)} ${fmt(t.iM)} | ${fmt(t.hP)} ${fmt(t.mP)} ${fmt(t.iP)} | ${t.giro}`);
}
console.log(`\nRegras de data refeitas sem copiar: ${regras.iguais} de ${regras.total} linhas do núcleo iguais (barras, plantar, colher, fonte, marcos).`);
console.log(`agronomia.json: ${I.agronomia() ? "carregado" : "ausente (N e forragem = não medido)"}`);
console.log(`Conferências: ${oks} ok, ${falhas} falha(s).`);
if (falhas) { console.log(erros.slice(0, 60).map((e) => "  FALHA " + e).join("\n")); if (erros.length > 60) console.log(`  … e mais ${erros.length - 60}`); }
process.exit(falhas ? 1 : 0);
