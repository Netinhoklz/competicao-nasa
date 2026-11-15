// C3 (rodada 2): confere o passo 4 no node, com os JSON da API salvos (testes/exemplos/api/, 8 municípios).
//  1. dinheiro/pareado.js (a base dos "ver mais") dá os MESMOS números de extras/ideal.js: 3 anos (P10/P50/P90), o jeito de hoje,
//     2027 nos El Niños, os 28 anos e o "8 em 10", para hoje, melhorado e os 4 ideais;
//  2. o modo "comparacao" de extras/hoje_ideal.js (desenhado num el falso) mostra na tabela os valores de ideal.beneficios, o
//     escolhido certo e nenhuma frase banida;
//  3. Quixadá padrão: hoje R$ 2.480, melhorado R$ 2.550, ideal "Um pouco de cada" R$ 4.360, "Guardar água" R$ 3.980.
// Uso: node teste_dinheiro.mjs [WEB=<pasta web/js>] [API=<pasta>]. Sai com 1 se alguma conferência falhar.
import fs from "node:fs";
import { pathToFileURL, fileURLToPath } from "node:url";

const WEB = process.env.WEB || fileURLToPath(new URL("../../web/js/", import.meta.url));
const DIR = process.env.API || fileURLToPath(new URL("../exemplos/api/", import.meta.url));
const imp = (p) => import(pathToFileURL(WEB + p).href);
const I = await imp("extras/ideal.js");
const P = await imp("passos/dinheiro/pareado.js");
const C = await imp("passos/dinheiro/calculo.js");
const HI = (await imp("extras/hoje_ideal.js")).default;
const U = await imp("comum.js");
const { rs } = await imp("passos/dinheiro/graficos.js");
const { PADRAO, efetivas } = await imp("roca.js");

const ANT = { hoje: "milho:34,feijao:33,mandioca:33", ha: "3", terra: "barro", baixio: "pouco" };
const MATRIZ = [
  ["padrão", {}], ["Seu Antônio", ANT], ["só milho", { hoje: "milho:100" }], ["com caju", { hoje: "milho:40,feijao:40,caju:20" }],
  ["sem baixio", { ...ANT, baixio: "nao" }], ["maniva não", { ...ANT, maniva: "nao" }], ["maniva no chão", { ...ANT, maniva: "plantada" }],
  ["antes=milho", { ...ANT, antes: "2025:milho" }], ["só feijão", { hoje: "feijao:100" }], ["milho+sorgo", { hoje: "milho:50,sorgo:50" }],
  ["muitas", { hoje: "milho:20,feijao:20,mandioca:20,algodao:10,amendoim:10,palma:10,banana:10" }], ["só palma", { hoje: "palma:100" }],
  ["só outra", { hoje: "outra:100" }], ["em metros", { ...ANT, ha: "", larg: "120", comp: "250" }],
  ["desembolso", { ...ANT, custo: "desembolso" }], ["raiz baixa", { ...ANT, raiz: "uf_p25" }], ["plano=ideal", { ...ANT, plano: "ideal" }],
];
const BANIDAS = ["5 perguntas", "Só o que muda a conta", "muda o que dá para salvar", "acima do recorde", "qualquer terra", "sem preço aqui",
  "ainda não vende", "à frente de hoje em", "à frente em"];

let oks = 0, falhas = 0;
const erros = [];
const ok = (c, msg) => { if (c) oks++; else { falhas++; if (erros.length < 40) erros.push(msg); } };
const perto = (a, b) => Math.abs(a - b) < 0.01;
const esp = (x) => JSON.stringify(x).replace(/ | /g, " "); // graficos.rs usa espaço duro; hoje_ideal.rs, espaço comum
const SEL = /<span class="hi-tab-val( sel)?" role="cell"[^>]*>([^<]*(?:<span[^>]*>[^<]*<\/span>)?)<\/span>/g;

for (const f of fs.readdirSync(DIR).filter((x) => /^\d{7}\.json$/.test(x))) {
  const r = JSON.parse(fs.readFileSync(DIR + f, "utf8"));
  for (const [nome, extra] of MATRIZ) for (const pri of ["", ...I.PRIORIDADES]) {
    const resp = { ...PADRAO, ...extra, ...(pri ? { prioridade: pri } : {}) };
    const ef = efetivas(resp, r), tag = `${f} ${nome} ${pri || "(padrão)"}`;
    const esc = I.escolhido(r, resp, ef), c3 = I.comparar3(r, resp, ef, esc.prioridade);
    ok(c3.ideal.plano === esc.plano || c3.melhor.plano === esc.plano, `${tag}: o escolhido não é um dos dois planos de comparar3`);
    const X = P.basePareada(r, resp, ef);
    for (const t of ["melhor", "ideal"]) {
      const b = c3[t].beneficios;
      if (!b) continue;
      const m = P.montagem(X, r, ef, c3[t].plano);
      ok(!!m === !!b.rs.ok, `${tag} ${t}: montagem ${!!m} × rs.ok ${b.rs.ok}`);
      if (!m || !b.rs.ok) continue;
      const tt = C.calcular(m, X.nivel, X.mult);
      for (const q of ["p10", "p50", "p90"]) ok(perto(tt.plano[q], b.rs.tres_anos[q]), `${tag} ${t}: 3 anos ${q} ${tt.plano[q]} × ${b.rs.tres_anos[q]}`);
      const h = c3.hoje.beneficios.rs;
      if (h.ok) for (const q of ["p10", "p50", "p90"]) ok(perto(tt.s0[q], h.tres_anos[q]), `${tag} ${t}: hoje ${q} ${tt.s0[q]} × ${h.tres_anos[q]}`);
      ok(tt.elNino.every((e, i) => perto(e.plano, b.rs.el_nino.anos[i].sobra)), `${tag} ${t}: El Niño difere`);
      const rp = C.replay(m, X.nivel, X.mult);
      ok(rp.length === b.rs.replay.length && rp.every((x, i) => perto(x.plano, b.rs.replay[i].sobra)), `${tag} ${t}: 28 anos diferem`);
      if (h.ok) ok(rp.every((x, i) => perto(x.s0, h.replay[i].sobra)), `${tag} ${t}: 28 anos de hoje diferem`);
      ok(perto(C.quantil(rp.map((x) => x.plano).sort((a, b2) => a - b2), 0.2), b.rs.oito_em_dez), `${tag} ${t}: 8 em 10 difere`);
    }
    // o desenho da comparação (sem DOM: el falso)
    const el = { innerHTML: "" };
    const ctx = { r, ef, resp, util: U, link: (n, p = {}) => `#/${r.local.cod}/${n}?${new URLSearchParams(p)}` };
    await HI.render(el, ctx, { modo: "comparacao", c3, escolhido: esc, linkIdeal: ctx.link(3, { plano: "ideal" }) });
    const html = el.innerHTML, txt = html.replace(/<[^>]+>/g, " ");
    for (const b of BANIDAS) ok(!txt.includes(b), `${tag}: frase banida "${b}"`);
    const sel = esc.tipo === "ideal" ? "ideal" : "melhor";
    ok(new RegExp(`hi-bloco ${sel}"><div class="hi-linha"><div class="hi-l-txt"><p class="hi-l-rot">[\\s\\S]*?escolhido</em>`).test(html), `${tag}: tag "escolhido" fora do ${sel}`);
    if (r.financeiro && [c3.hoje, c3.melhor, c3.ideal].some((x) => x.beneficios?.rs?.ok)) {
      const cel = [...html.matchAll(SEL)].map((x) => x[2].replace(/<[^>]+>/g, "").trim());
      const quer = ["rs_tipico", "rs_el_nino", "quebra_10"].flatMap((id) => ["hoje", "melhor", "ideal"].map((t) => {
        const it = c3[t].beneficios?.itens?.find((x) => x.id === id);
        return !it || it.valor == null ? "não medido" : id === "quebra_10" ? `${U.num(it.valor)} em 10` : rs(it.valor);
      }));
      ok(esp(cel) === esp(quer), `${tag}: tabela ${JSON.stringify(cel)} × ${JSON.stringify(quer)}`);
      const graf = [...html.matchAll(/class="hi-g-val"[^>]*>([^<]*)</g)].map((x) => x[1]);
      const qg = ["hoje", "melhor", "ideal"].filter((t) => c3[t].beneficios?.rs?.ok).map((t) => rs(c3[t].beneficios.rs.tres_anos.p50));
      ok(esp(graf) === esp(qg), `${tag}: gráfico ${graf} × ${qg}`);
    }
  }
}

// Quixadá padrão (os números do passo 4)
{
  const r = JSON.parse(fs.readFileSync(DIR + "2311306.json", "utf8")), resp = { ...PADRAO }, ef = efetivas(resp, r);
  const v = (pri, t) => rs(I.comparar3(r, resp, ef, pri)[t].beneficios.rs.tres_anos.p50);
  const tab = { hoje: v("garantir", "hoje"), melhor: v("garantir", "melhor"), garantir: v("garantir", "ideal"), equilibrar: v("equilibrar", "ideal") };
  console.log("Quixadá padrão, 3 anos:", JSON.stringify(tab));
  ok(esp(tab) === esp({ hoje: "R$ 2.480", melhor: "R$ 2.550", garantir: "R$ 3.980", equilibrar: "R$ 4.360" }), "Quixadá padrão: números mudaram");
}
console.log(`${oks} conferências, ${falhas} falhas`);
for (const e of erros) console.log("  FALHA", e);
process.exit(falhas ? 1 : 0);
