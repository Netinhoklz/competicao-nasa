// Teste do Relatório (C4, rodada 2): para os 8 municípios × respostas, monta os dados e o HTML do passo 5 no node e confere
// 1) toda data dd/mm/aaaa do relatório existe na agenda do plano escolhido (barras de/ate, rótulos, plantar/colher/fonte) ou em
//    r.agenda (hoje, marcos); 2) as tarefas estão em ordem de data, todas com "o quê" e "como"; 3) nada de undefined/NaN/null nem
//    frase banida no texto; 4) o revezamento segue a célula do plano. Sai 1 se algo falhar.
// Uso: node teste_relatorio.mjs [pasta_api]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const W = new URL("../../web/", import.meta.url).href;
const U = await import(W + "js/comum.js");
const { efetivas, PADRAO } = await import(W + "js/roca.js");
const REL = await import(W + "js/passos/relatorio.js");
const agro = JSON.parse(fs.readFileSync(new URL(W + "dados/agronomia.json"), "utf8"));
const PASTA = process.argv[2] || fileURLToPath(new URL("../exemplos/api", import.meta.url));
const A2 = fileURLToPath(new URL("../exemplos/api_respostas", import.meta.url)); // as 4 respostas reais de Quixadá

const RESPS = [
  "",
  "plano=ideal",
  "plano=ideal&prioridade=garantir",
  "plano=ideal&prioridade=vender",
  "plano=ideal&prioridade=solo",
  "plano=ideal&prioridade=equilibrar",
  "hoje=milho:50,feijao:50&larg=40&comp=100&ha=0.4",
  "hoje=milho:34,feijao:33,mandioca:33&larg=40&comp=100&ha=0.4&plano=ideal&prioridade=garantir",
  "hoje=milho:100",
  "hoje=mandioca:50,palma:50",
  "hoje=milho:40,feijao:30,caju:30&antes=2025:milho",
  "hoje=feijao:50,milho:50&antes=2025:milho&plano=ideal",
  "hoje=banana:50,milho:50",
  "hoje=amendoim:50,sorgo_grao:50",
];
const BANIDAS = ["5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde", "qualquer terra", "sem preço aqui",
  "ainda não vende", "à frente de hoje em"];
const tirar = (h) => h.replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'")
  .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\s+/g, " ");
const DATA = /\b(\d{2})\/(\d{2})\/(\d{4})\b/g;
const br = (iso) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}/${iso.slice(0, 4)}`;

let falhas = 0, conf = 0, casos = 0;
const falha = (m) => { falhas++; if (falhas <= 40) console.log("FALHA:", m); };
const tabela = [];

function permitidas(r, d) {
  const s = new Set([br(r.agenda.hoje)]);
  for (const m of r.agenda.marcos || []) s.add(br(m.data));
  const linhas = [...d.esc.linhas, ...(r.agenda.linhas || [])];
  for (const l of linhas) {
    for (const b of l.barras || []) { s.add(br(b.de)); s.add(br(b.ate)); for (const m of String(b.rotulo).matchAll(DATA)) s.add(m[0]); }
    for (const m of l.marcos || []) s.add(br(m.data));
    for (const t of [l.plantar, l.colher, l.fonte]) for (const m of String(t || "").matchAll(DATA)) s.add(m[0]);
  }
  return s;
}

function caso(nome, r, q) {
  casos++;
  const resp = { ...PADRAO };
  for (const [k, v] of new URLSearchParams(q)) resp[k] = v;
  const ef = efetivas(resp, r);
  const d = REL.dados(r, resp, ef, agro);
  const ctx = { r, resp, ef, util: U, link: (n) => `#/x/${n}` };
  const h = REL.default._html(ctx, d, agro);
  const txt = tirar(h);
  const ok = permitidas(r, d);
  for (const m of txt.matchAll(DATA)) { conf++; if (!ok.has(m[0])) falha(`${nome} [${q}]: data ${m[0]} não está na agenda`); }
  // as datas das tarefas (ISO) também
  for (const x of d.tarefas) {
    for (const iso of [x.de, x.ate].filter(Boolean)) { conf++; if (!ok.has(br(iso))) falha(`${nome} [${q}]: tarefa ${x.oque} ${iso} fora da agenda`); }
    conf++; if (!x.oque || !x.como) falha(`${nome} [${q}]: tarefa sem o quê/como: ${JSON.stringify([x.tipo, x.oque, x.como])}`);
    conf++; if (x.ate && x.ate < d.hoje) falha(`${nome} [${q}]: tarefa já passou: ${x.oque} ${x.ate}`);
    conf++; if (x.de > (r.agenda.fim || "2027-12-31")) falha(`${nome} [${q}]: tarefa depois do fim: ${x.oque} ${x.de}`);
  }
  const ord = d.tarefas.map((x) => (x.de < d.hoje ? d.hoje : x.de));
  for (let i = 1; i < ord.length; i++) { conf++; if (ord[i] < ord[i - 1]) falha(`${nome} [${q}]: fora de ordem ${ord[i - 1]} > ${ord[i]}`); }
  for (const b of ["undefined", "NaN", "null", "[object"]) { conf++; if (txt.includes(b)) falha(`${nome} [${q}]: "${b}" no texto: …${txt.slice(Math.max(0, txt.indexOf(b) - 80), txt.indexOf(b) + 40)}…`); }
  for (const b of BANIDAS) { conf++; if (txt.includes(b)) falha(`${nome} [${q}]: frase banida "${b}"`); }
  // revezamento: célula "solteiro"/"sem revezamento" → nenhuma tarefa "no meio do milho" naquele ano
  const bx = d.plano?.faixas?.find((f) => f.parte === "Baixio")?.anos?.[0];
  if (bx) {
    const tc = bx.texto || "", rev = bx.mucuna || (/revezamento/i.test(tc) && !/sem revezamento/i.test(tc));
    conf++;
    if (!rev && d.tarefas.some((x) => x.relay && x.k === 0)) falha(`${nome} [${q}]: revezamento no baixio "${tc}"`);
  }
  // próximas 5 (WhatsApp)
  const p5 = REL.proximas(d, 5);
  conf++; if (d.plano && (!p5.length || p5.some((s) => !/\d{2}\/\d{2}\/\d{4}/.test(s)))) falha(`${nome} [${q}]: próximas 5 sem data: ${JSON.stringify(p5)}`);
  DATA.lastIndex = 0;
  tabela.push({ nome, q, tipo: d.esc.nome, tarefas: d.tarefas.length, meses: new Set(d.tarefas.map((x) => (x.de < d.hoje ? d.hoje : x.de).slice(0, 7))).size,
    datas: [...txt.matchAll(DATA)].length, palavras: txt.split(/\s+/).filter(Boolean).length, mat: d.mat?.itens?.length ?? 0, semData: d.semData.length });
  return { d, txt };
}

const arqs = fs.readdirSync(PASTA).filter((f) => f.endsWith(".json")).sort();
let exemplo = null;
for (const f of arqs) {
  const r = JSON.parse(fs.readFileSync(path.join(PASTA, f), "utf8"));
  for (const q of RESPS) { const x = caso(r.local.municipio, r, q); if (f.startsWith("2311306") && q === RESPS[7]) exemplo = x; }
}
if (fs.existsSync(A2)) {
  for (const f of fs.readdirSync(A2).filter((x) => x.endsWith(".json"))) {
    const r = JSON.parse(fs.readFileSync(path.join(A2, f), "utf8"));
    for (const q of RESPS) caso(`${r.local.municipio}/${f}`, r, q);
  }
}
console.log(`casos ${casos}, conferências ${conf}, falhas ${falhas}`);
const porMun = {};
for (const t of tabela) { const k = t.nome; (porMun[k] ||= []).push(t); }
for (const [k, ts] of Object.entries(porMun)) {
  const mm = (c) => `${Math.min(...ts.map((t) => t[c]))}–${Math.max(...ts.map((t) => t[c]))}`;
  console.log(`${k.padEnd(34)} tarefas ${mm("tarefas")} · meses ${mm("meses")} · datas ${mm("datas")} · palavras ${mm("palavras")} · materiais ${mm("mat")}`);
}
if (exemplo) {
  console.log("\n--- exemplo: Quixadá, Seu Antônio 40 × 100, ideal Guardar água ---");
  for (const x of exemplo.d.tarefas) console.log(`${REL.periodo(x).padEnd(24)} ${x.oque}${x.onde ? ` (${x.onde})` : ""} | ${x.como}${x.cond.length ? ` | ⚑ ${x.cond.join(" ")}` : ""}`);
  console.log("anos:", JSON.stringify(exemplo.d.anos.map((a) => [a.ano, a.partes.map((p) => `${p.parte}: ${p.cultura} ${p.txt}`), a.colher.map((c) => c.txt)]), null, 0));
  console.log("material:", exemplo.d.mat.itens.map((y) => `${y.cultura} ${y.quantidade.toFixed(1)} ${y.unidade} [${y.onde}]`).join("; "), "| nada:", JSON.stringify(exemplo.d.mat.nada));
  console.log("próximas 5:", REL.proximas(exemplo.d, 5));
}
process.exit(falhas ? 1 : 0);
