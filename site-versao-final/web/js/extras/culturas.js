// QUADRA: a lista das culturas que a pessoa diz que planta hoje (linha "O que planta hoje?" de Sua roça, a ficha, o passo 4).
// Saiu de extras/hoje_ideal.js (15/11) para ter um dono só; hoje_ideal.js importa e reexporta CULT e opcoesCultura.
// Chave = o que vai para ctx.resp.hoje ("milho:50,feijao:50"); as chaves que já existem não mudam (links antigos). A ordem de CULT é
// a ordem das culturas no texto de `hoje` (milho, feijão e mandioca primeiro: o cenário "Seu Antônio" dá milho:34,feijao:33,mandioca:33).
// nome: rótulo · sub: o outro nome, só na lista completa · serie: série de R$ do IBGE (calculo.js) · icone: U.ic · t: classe de cor ·
// semRs: fora da conta de R$ · motor: o nome da cultura no cardápio do núcleo (r.cardapio[].cultura e r.agenda.culturas[].cultura);
// null = sem par. Rodada 2 (15/11): as 18 do cardápio do núcleo (as que faltavam entraram antes de "outra").
export const CULT = {
  milho: { nome: "Milho", serie: "Milho", icone: "milho", t: "cereal", motor: "Milho" },
  feijao: { nome: "Feijão", sub: "caupi, de corda", serie: "Feijão", icone: "feijao", t: "leguminosa", motor: "Feijão-caupi" },
  mandioca: { nome: "Mandioca", serie: "Mandioca", icone: "mandioca", t: "tampao", motor: "Mandioca" },
  sorgo: { nome: "Sorgo", sub: "de forragem", icone: "milho", t: "forragem", semRs: true, motor: "Sorgo forrageiro" },
  palma: { nome: "Palma", icone: "palma", t: "perene", semRs: true, motor: "Palma forrageira" },
  feijaoc: { nome: "Feijão comum", sub: "carioca, de arranca", icone: "feijao", t: "leguminosa", semRs: true, motor: "Feijão comum" },
  amendoim: { nome: "Amendoim", icone: "feijao", t: "leguminosa", semRs: true, motor: "Amendoim" },
  sorgog: { nome: "Sorgo de grão", icone: "milho", t: "cereal", semRs: true, motor: "Sorgo granífero" },
  guandu: { nome: "Guandu", sub: "andu", icone: "feijao", t: "leguminosa", semRs: true, motor: "Guandu" },
  milheto: { nome: "Milheto", icone: "milho", t: "forragem", semRs: true, motor: "Milheto" },
  gliricidia: { nome: "Gliricídia", icone: "broto", t: "perene", semRs: true, motor: "Gliricídia" },
  mucuna: { nome: "Mucuna", icone: "feijao", t: "leguminosa", semRs: true, motor: "Mucuna-preta" },
  algodao: { nome: "Algodão", icone: "broto", t: "renda", semRs: true, motor: "Algodão herbáceo" },
  mamona: { nome: "Mamona", icone: "broto", t: "renda", semRs: true, motor: "Mamona" },
  girassol: { nome: "Girassol", icone: "broto", t: "renda", semRs: true, motor: "Girassol" },
  caju: { nome: "Caju", icone: "caju", t: "perene", semRs: true, motor: "Caju" },
  banana: { nome: "Banana", icone: "banana", t: "perene", semRs: true, motor: "Banana" },
  cana: { nome: "Cana", icone: "cana", t: "perene", semRs: true, motor: "Cana-de-açúcar" },
  outra: { nome: "Outra", icone: "broto", t: "pousio", semRs: true, motor: null },
};

/** A lista completa ("Ver todas as culturas"), na ordem dos grupos do cardápio do núcleo (r.cardapio[].grupo); "outra" fica no fim. */
export const GRUPOS = [
  { id: "alimento", nome: "Comida", ks: ["feijao", "milho", "feijaoc", "mandioca", "amendoim", "sorgog", "guandu"] },
  { id: "forragem", nome: "Forragem", ks: ["sorgo", "milheto", "palma", "gliricidia", "mucuna"] },
  { id: "renda", nome: "Renda", ks: ["algodao", "mamona", "girassol"] },
  { id: "perene", nome: "Perenes", ks: ["caju", "banana", "cana"] },
];
export const TODAS = [...GRUPOS.flatMap((g) => g.ks), "outra"];

/** A linha do cardápio do núcleo para a chave (ou undefined: "outra", ou cultura sem linha aqui). */
export const noCardapio = (r, k) => (CULT[k]?.motor ? (r?.cardapio || []).find((c) => c.cultura === CULT[k].motor) : undefined);
/** A cultura está fora do zoneamento daqui (r.cardapio[].situacao === "fora"): pode marcar, com um aviso curto. */
export const foraDaqui = (r, k) => noCardapio(r, k)?.situacao === "fora";

/** As opções à vista na linha "O que planta hoje?" (o resto do cardápio entra pela lista completa). As culturas já marcadas que
 *  vieram da lista completa também ficam à vista (antes de "outra"), para a pessoa ver o que escolheu. */
export function opcoesCultura(r, marcadas = []) {
  const card = r.cardapio || [];
  const serve = (re) => card.some((c) => re.test(c.cultura) && c.situacao !== "fora");
  const base = ["milho", "feijao", "mandioca", ...(serve(/^Sorgo/) ? ["sorgo"] : []), ...(serve(/^Palma/) ? ["palma"] : [])];
  const extras = Object.keys(CULT).filter((k) => k !== "outra" && !base.includes(k) && marcadas.includes(k));
  return [...base, ...extras, "outra"];
}
