// Confere calculo.js com os valores esperados de Quixadá (analise/financeiro.md, seção 3).
import fs from "node:fs";
import { pathToFileURL, fileURLToPath } from "node:url";
const BASE = fileURLToPath(new URL("../../web/js/passos/dinheiro/calculo.js", import.meta.url));
const C = await import(pathToFileURL(BASE).href);
const DIR = fileURLToPath(new URL("../exemplos/", import.meta.url));  // respostas salvas da API
const arq = process.argv[2] || "local_2311306.json";
const r = JSON.parse(fs.readFileSync(DIR + arq, "utf8"));
const ef = { ha: +(process.argv[3] || 3), baixio_ha: +(process.argv[4] ?? 1), tem_baixio: true, maniva: process.argv[5] || "tem" };
const m = C.montar(r, ef);
const f = (x) => Math.round(x);
console.log("ok", m.ok, "falta", m.falta, "semRs", m.semRs, "agro", m.agro, "a", m.a, "b", m.b, "anos", m.anos.length, "EN", m.anosEN);
for (const k of [0, 1, 2]) console.log(2027 + k, m.itens[k].map((i) => `${i.parte}:${i.cultura}:${i.custo ? "custo@" + C.rotMes(i.mes) : "rec@" + i.meses.map(([j]) => C.rotMes(j)).join(",")}`).join(" | "));
console.log("S0 2027", m.s0[0].map((i) => `${i.cultura}:${i.custo ? "custo@" + C.rotMes(i.mes) : "rec@" + C.rotMes(i.meses[0][0])}`).join(" | "));
const pr = r.financeiro.precos_raiz, ref = m.precoRefMand;
for (const [nome, p] of [["municipio", pr.municipio], ["uf_mediana", pr.uf_mediana], ["uf_p25", pr.uf_p25]]) {
  const t = C.calcular(m, "semente", p / ref);
  console.log(`raiz ${nome} ${p}: plano ${f(t.plano.p10)}/${f(t.plano.p50)}/${f(t.plano.p90)} | S0 ${f(t.s0.p10)}/${f(t.s0.p50)}/${f(t.s0.p90)} | ganho ${f(t.ganho.p10)}/${f(t.ganho.p50)}/${f(t.ganho.p90)} | à frente ${(t.aFrente * 100).toFixed(1)}% | N ${t.n}`);
  if (nome === "municipio") {
    console.log("  El Niño 2027:", t.elNino.map((e) => `${e.ano} ${f(e.plano)} x ${f(e.s0)}`).join("; "));
    console.log("  por ano:", t.porAno.map((a) => `${a.ano} plano P50 ${f(a.plano.p50)} S0 ${f(a.s0.p50)} frente ${a.planoFrente}/${a.n} paga ${a.pagaPlano}/${a.n}`).join(" ; "));
    const cx = t.caixaPlano.map((q) => f(q.p50));
    console.log("  caixa P50:", cx.map((v, i) => `${C.rotMes(i)} ${v}`).join(" "));
    const d = C.calcular(m, "desembolso", p / ref);
    console.log(`  desembolso: plano P50 ${f(d.plano.p50)} neg ${(d.planoNeg * 100).toFixed(0)}% | S0 P50 ${f(d.s0.p50)} neg ${(d.s0Neg * 100).toFixed(0)}% | 2027 plano P50 ${f(d.porAno[0].plano.p50)}`);
    const rp = C.replay(m, "semente", p / ref);
    console.log("  replay acima:", rp.filter((x) => x.plano > x.s0).length, "de", rp.length, "pior plano", f(Math.min(...rp.map((x) => x.plano))));
    console.log("  comida 2027:", JSON.stringify(C.comida2027(m).map((x) => [x.ano, f(x.graoPlano), f(x.raizPlano), f(x.graoS0)])));
  }
}
console.log("empate semente", C.precoEmpate(m, "semente"), "desembolso", C.precoEmpate(m, "desembolso"));
// caminho típico (fin2.py): 2027 = mediana por cultura dos EN, 2028–29 = mediana por cultura; preço do município, semente
const med = (a) => { const o = [...a].sort((x, y) => x - y); const n = o.length; return n % 2 ? o[(n - 1) / 2] : (o[n / 2 - 1] + o[n / 2]) / 2; };
const tip = {}, tipEN = {};
for (const s of m.usadas) { tip[s] = med(m.anos.map((y) => m.R[s].get(y))); tipEN[s] = med(m.anosEN.map((y) => m.R[s].get(y))); }
const fl = new Float64Array(C.NMESES);
[0, 1, 2].forEach((k) => {
  for (const it of m.itens[k]) {
    if (it.custo) fl[it.mes] -= m.custoHa(it.custo, "semente") * it.area;
    else { const v = (k === 0 ? tipEN : tip)[it.serie] * it.fator * (it.serie === "Mandioca" ? pr.municipio / ref : 1); for (const [i, w] of it.meses) fl[i] += v * w; }
  }
});
let acc = 0; const cum = [...fl].map((v) => (acc += v));
console.log("caminho típico:", cum.map((v, i) => `${C.rotMes(i)} ${f(v)}`).join(" "));
