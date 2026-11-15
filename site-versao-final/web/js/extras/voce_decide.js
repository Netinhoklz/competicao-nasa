// QUADRA, ponto 16 ("Você decide"): o QUADRA apoia e não substitui o saber de quem planta.
// - FRASE / moldura(): a frase fixa da moldura (vai na barra de baixo, sempre à vista);
// - olho(texto): "Aqui vale o seu olho", 1 linha nos momentos em que o julgamento humano pesa mais (no máximo 1 por bloco);
// - OLHOS: os textos exatos de cada momento (onde entra cada um: integracao/voce_decide.md).
// Os blocos maiores ficam em confianca.js (confiança dos dados aqui) e leve_ao_tecnico.js (perguntas para o técnico).
import * as U from "../comum.js";

export const FRASE = "O QUADRA ajuda. Quem decide é você, com o técnico.";

const OLHO = '<path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="2.8"/>';
/** Ícone do olho, no mesmo traço dos ícones de comum.js. */
export const icOlho = (tam = "") => `<svg class="ic ${tam}" viewBox="0 0 24 24" aria-hidden="true">${OLHO}</svg>`;

/** "Aqui vale o seu olho": ícone + rótulo curto + 1 linha (até 12 palavras). */
export const olho = (texto) => `<p class="olho" title="Aqui vale o seu olho: isso o satélite não vê.">${icOlho()}
  <span class="olho-rot">seu olho</span><span class="olho-txt">${U.esc(texto)}</span></p>`;

/** A frase fixa da moldura (barra de baixo de roca.html). */
export const moldura = () => `<p class="moldura-decide">${icOlho()}<span>O QUADRA ajuda. <b>Quem decide é você, com o técnico.</b></span></p>`;

/** Os momentos em que o julgamento humano pesa mais (cada texto com até 12 palavras). Condições: integracao/voce_decide.md. */
export const OLHOS = {
  el_nino: "Nem todo El Niño seca igual: olhe a chuva de fevereiro.",
  sem_zarc: "Sem zoneamento, a data é estimada: confirme com quem já planta.",
  leste: "Perto do mar, o pluviômetro da comunidade vale mais que o satélite.",
  terra: "Na dúvida, aperte um torrão molhado: areia esfarela, barro gruda.", // 10 palavras: vai na tela única (Sua roça)
  tarefa: "A tarefa muda de lugar para lugar: confira a medida daqui.",
  baixio: "Ande no roçado depois de uma chuva: onde a água para?",
  irrigacao: "Com irrigação, as datas mudam: combine com o técnico.",
  faixas: "Faixas e espaçamento se acertam no chão, em curva de nível.",
  metade: "Guarde metade da semente; plante quando a terra molhar a mão.",
  vizinhos: "Contra praga que voa, combine o plantio com os vizinhos.",
  preco_raiz: "Pergunte o preço da raiz na casa de farinha daqui.",
  agro: "Faça a conta com o que a sua família colhe.",
  memoria: "Lembra de 2010 e 2016? Compare com a colheita da sua roça.",
  portoes: "19/mar e 30/abr: confira a umidade na mão e com o técnico.",
  portoes_fora: "Aqui as datas de troca são outras: decida com o técnico.",
};

export default {
  id: "voce_decide",
  /** opcoes.olho = chave de OLHOS (ou opcoes.texto) desenha um "seu olho"; sem opções, desenha a frase da moldura. */
  async render(el, ctx, opcoes = {}) {
    const t = opcoes.texto || OLHOS[opcoes.olho];
    el.innerHTML = t ? olho(t) : moldura();
  },
};
