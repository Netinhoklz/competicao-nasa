// QUADRA, passo "Como plantar": geometria do roçado e conectividade da gramínea, tudo no navegador.
// Desenho (analise/distribuicao.md, seção 2): roçado quadrado com a área da resposta, baixio embaixo, Partes A/B/C em faixas
// em nível (A B C A B C; 3 faixas se cada uma ficar com menos de 10 m), bordas no perímetro sem tirar área (como em
// notebooks/secoes_financeiro/10_familia.py). Ordem das faixas por força bruta nas permutações de A, B e C.
// Conectividade (ideia de Vicente Lima, PercolaCampo; definições p, S e "atravessa" do MANIFESTO de percolação do José):
// grade de ~5 m, vizinhança 4, union-find.
//
// Rodada 2 (15/11, analise/fluxo2/BRIEFING.md, D4): o roçado pode ser um retângulo larg × comp em metros (as medidas de Sua roça,
// ctx.ef.larg e ctx.ef.comp, que roca.js já preenche; ou o 3º argumento de montar). comp = no sentido em que a água desce: as faixas
// ficam em nível, uma embaixo da outra ao longo do comp, cada uma com o comprimento da largura do roçado, e o baixio fica embaixo.
// Sem medidas, nada muda: o quadrado da área (larg = comp = lado), como antes.
// Campos novos de montar() (os antigos continuam, com o mesmo sentido):
//   larg, comp     metros do roçado (com medidas: as da resposta; sem: o lado do quadrado nos dois)
//   medidas        "resposta" (larg × comp vieram da pessoa) | "quadrado" (suposição: quadrado da área)
//   profBaixio     metros do baixio no sentido do comp (0 sem baixio); o alto vai de 0 a profAlto e o baixio de profAlto a comp
//   faixas[i].larguraM, faixas[i].comprimentoM   metros de cada faixa: a largura (no sentido do comp, = larguraFaixa) e o
//                  comprimento (= larg); y0 e y1 seguem em metros a partir do alto
//   lado           mantido para quem desenha o quadrado: = comp (as coordenadas y0/y1 vão de 0 a lado). Para desenhar o retângulo,
//                  use larg na horizontal e comp na vertical (grade() já usa os dois).
// Com medidas, ha = larg × comp / 10.000 (pode diferir em centésimos do ctx.ef.ha arredondado).
// Correção Y (15/11): as perenes que ele já tem (plano.fora_do_giro) ganham um pedaço próprio no alto, em escala (reserva = { ha, y0,
// y1, larguraM, comprimentoM, culturas, porCultura }); as faixas vão de profPer a profAlto e o baixio de profAlto a comp. haGiro =
// ha − reserva (o mesmo ha_giro da conta de R$). Sem perene fora do giro, reserva = null e nada muda.

export const GRAMINEAS = new Set(["Milho", "Sorgo granífero", "Sorgo forrageiro", "Milheto"]);
export const ehGram = (cultura) => GRAMINEAS.has(cultura);
export const LIMIAR_SITIO = 0.5927; // malha quadrada, 4 vizinhos (Alonso-Tlali 2025, Entropy 27:386): só régua de referência

const permutacoes = (v) => (v.length <= 1 ? [v] : v.flatMap((x, i) => permutacoes([...v.slice(0, i), ...v.slice(i + 1)]).map((p) => [x, ...p])));

/** Layout do roçado a partir do plano do motor e das respostas efetivas (ctx.ef). Medidas em metros e hectares.
 *  med = { larg, comp } em metros (opcional; sem ele valem ef.larg e ef.comp; sem os dois, o quadrado da área). */
export function montar(plano, ef, med = null) {
  const partes = plano.faixas.filter((f) => /^Parte /.test(f.parte));
  const bx = plano.faixas.find((f) => f.parte === "Baixio") || null;
  const bordas = plano.faixas.find((f) => f.parte === "Bordas") || null;
  const nAnos = plano.anos.length;
  const temBaixio = ef.tem_baixio !== false && !!bx;
  const incerto = temBaixio && ef.tem_baixio === null; // "não sei": baixio de 1/3, tracejado
  const frac = temBaixio ? (incerto ? 1 / 3 : ef.baixio_frac) : 0;
  const m = med || { larg: ef.larg, comp: ef.comp };
  const medidas = m.larg > 0 && m.comp > 0 ? "resposta" : "quadrado";
  const ha = medidas === "resposta" ? (m.larg * m.comp) / 1e4 : ef.ha;
  const larg = medidas === "resposta" ? +m.larg : Math.sqrt(ha * 1e4);
  const comp = medidas === "resposta" ? +m.comp : larg;
  const lado = comp;
  // as perenes que ele já tem (plano.fora_do_giro de extras/ideal.js: palma, caju, banana…) ficam num pedaço próprio no alto, em
  // escala, fora do giro: a conta de R$ usa só o resto (ha_giro), e o desenho e o material também (correção Y, 15/11)
  const per = (plano.fora_do_giro || []).filter((x) => x.cultura && x.ha > 0);
  const haPer0 = per.reduce((s, x) => s + x.ha, 0);
  const fracPer = ef.ha > 0 && haPer0 > 0 && haPer0 < ef.ha - 1e-9 && partes.length ? haPer0 / ef.ha : 0;
  const haPer = ha * fracPer, haGiro = ha - haPer;
  const haBaixio = Math.min(ha * frac, haGiro); // a mesma regra de calculo.montar: o baixio guarda o tamanho dele, até o giro todo
  const haAlto = haGiro - haBaixio;
  const profPer = comp * fracPer;
  const profAlto = comp * (1 - haBaixio / ha);
  const nFaixas = (profAlto - profPer) / (2 * partes.length) >= 10 ? 2 * partes.length : partes.length;
  const rep = nFaixas / partes.length;

  const g = (f, k) => ehGram(f.anos[k].cultura);
  const custo = (seq) => {
    let contatos = 0, encostaBaixio = 0;
    for (let k = 0; k < nAnos; k++) {
      for (let i = 0; i + 1 < seq.length; i++) if (g(seq[i], k) && g(seq[i + 1], k)) contatos++;
      if (temBaixio && g(seq[seq.length - 1], k)) { encostaBaixio++; if (g(bx, k)) contatos++; }
    }
    return { contatos, encostaBaixio };
  };
  const opcoes = permutacoes(partes.map((_, i) => i)).map((perm) => {
    const seq = Array.from({ length: rep }, () => perm.map((i) => partes[i])).flat();
    return { perm, seq, ...custo(seq) };
  });
  // menos contatos; no empate, menos gramínea encostada no baixio; depois a ordem da lista (A antes de B), determinística
  const melhor = opcoes.reduce((a, b) => (b.contatos < a.contatos || (b.contatos === a.contatos && b.encostaBaixio < a.encostaBaixio) ? b : a));
  const pior = Math.max(...opcoes.map((o) => o.contatos));
  const iguais = opcoes.every((o) => o.contatos === melhor.contatos);

  const alt = (profAlto - profPer) / nFaixas;
  const conta = {};
  const faixas = melhor.seq.map((f, i) => {
    const letra = f.parte.replace("Parte ", "");
    conta[letra] = (conta[letra] || 0) + 1;
    return { id: letra + conta[letra], letra, parte: f.parte, plano: f, y0: profPer + i * alt, y1: profPer + (i + 1) * alt, ha: haAlto / nFaixas,
      larguraM: alt, comprimentoM: larg };
  });
  const reserva = fracPer ? { ha: haPer, y0: 0, y1: profPer, larguraM: profPer, comprimentoM: larg, culturas: per.map((x) => x.cultura),
    porCultura: per.map((x) => ({ cultura: x.cultura, ha: ha * (x.ha / ef.ha) })) } : null;
  return {
    ha, lado, larg, comp, medidas, profBaixio: comp - profAlto, reserva, haGiro, profPer,
    frac: haBaixio / ha, temBaixio, incerto, haBaixio, haAlto, profAlto, larguraFaixa: alt, nFaixas,
    haParte: haAlto / partes.length, partes, bx: temBaixio ? bx : null, bordas, nAnos, faixas,
    ordem: melhor.perm.map((i) => partes[i].parte.replace("Parte ", "")),
    contatos: melhor.contatos, piorContatos: pior, todasIguais: iguais,
    encostaBaixio: melhor.seq[melhor.seq.length - 1],
  };
}

/** Grade de ~5 m com a gramínea do ano k, no desenho "faixas" (o do plano) ou "blocos" (A|B|C lado a lado, como se faz hoje).
 *  As linhas da grade seguem as divisas das faixas e do baixio, e as colunas os terços do roçado: a área de cada célula é exata.
 *  No retângulo, as linhas vão ao longo do comp e as colunas ao longo da larg (largCol em metros da larg). */
export function grade(lay, k, modo) {
  const L = lay.larg || lay.lado, C = lay.comp || lay.lado;
  const linhas = []; // {y0, y1, i: índice da faixa, -1 no baixio, -2 no pedaço das perenes que ele já tem}
  const fatiar = (y0, y1, i) => { const m = Math.max(1, Math.round((y1 - y0) / 5)); for (let j = 0; j < m; j++) linhas.push({ y0: y0 + (y1 - y0) * j / m, y1: y0 + (y1 - y0) * (j + 1) / m, i }); };
  if (lay.reserva) fatiar(0, lay.reserva.y1, -2);
  lay.faixas.forEach((f, i) => fatiar(f.y0, f.y1, i));
  if (lay.temBaixio) fatiar(lay.profAlto, C, -1);
  const nl = linhas.length, np = lay.partes.length;
  const r0 = Math.max(0, linhas.findIndex((l) => l.i !== -2)); // "o alto" do giro: a 1ª linha depois do pedaço das perenes
  const nc = np * Math.max(2, Math.round(L / 5 / np));
  const largCol = L / nc;
  const gram = new Uint8Array(nl * nc);
  linhas.forEach((ln, r) => {
    for (let c = 0; c < nc; c++) {
      if (ln.i === -2) { gram[r * nc + c] = 0; continue; } // perene: nunca é gramínea
      const cultura = ln.i < 0 ? lay.bx.anos[k].cultura
        : modo === "faixas" ? lay.faixas[ln.i].plano.anos[k].cultura
          : lay.partes[Math.floor(c / (nc / np))].anos[k].cultura;
      gram[r * nc + c] = ehGram(cultura) ? 1 : 0;
    }
  });
  // union-find, vizinhança 4
  const pai = new Int32Array(nl * nc);
  for (let i = 0; i < pai.length; i++) pai[i] = i;
  const raiz = (i) => { while (pai[i] !== i) { pai[i] = pai[pai[i]]; i = pai[i]; } return i; };
  const unir = (a, b) => { a = raiz(a); b = raiz(b); if (a !== b) pai[a] = b; };
  for (let r = 0; r < nl; r++) for (let c = 0; c < nc; c++) {
    const i = r * nc + c;
    if (!gram[i]) continue;
    if (c + 1 < nc && gram[i + 1]) unir(i, i + 1);
    if (r + 1 < nl && gram[i + nc]) unir(i, i + nc);
  }
  const area = L * C;
  const blocos = new Map(); // raiz → {a: área em m², topo, fundo}
  let total = 0;
  for (let r = 0; r < nl; r++) for (let c = 0; c < nc; c++) {
    const i = r * nc + c;
    if (!gram[i]) continue;
    const a = (linhas[r].y1 - linhas[r].y0) * largCol;
    total += a;
    const b = raiz(i);
    if (!blocos.has(b)) blocos.set(b, { a: 0, topo: false, fundo: false });
    const o = blocos.get(b);
    o.a += a;
    if (r === r0) o.topo = true;
    if (r === nl - 1) o.fundo = true;
  }
  const lista = [...blocos.values()];
  const maior = lista.reduce((a, b) => (b.a > a.a ? b : a), { a: 0 });
  return {
    linhas, nl, nc, largCol, gram,
    p: total / area,
    blocos: lista.length,
    maior: maior.a / area,             // fração do roçado no maior bloco
    S: total ? maior.a / total : 0,    // fração da gramínea no maior bloco
    desce: lista.some((b) => b.topo && b.fundo), // um bloco liga a linha do alto à mais baixa (o baixio, se houver)
  };
}

/** Passos (células, vizinhança 4, só por gramínea) de um foco no alto da grade até cada célula; -1 = não alcança. */
export function espalhar(gr) {
  const { nl, nc, gram } = gr;
  const dist = new Int32Array(nl * nc).fill(-1);
  let ini = -1;
  for (let r = 0; r < nl && ini < 0; r++) {
    let melhor = -1;
    for (let c = 0; c < nc; c++) if (gram[r * nc + c] && (melhor < 0 || Math.abs(c + 0.5 - nc / 2) < Math.abs(melhor + 0.5 - nc / 2))) melhor = c;
    if (melhor >= 0) ini = r * nc + melhor;
  }
  if (ini < 0) return { dist, max: 0, ini };
  const fila = [ini];
  dist[ini] = 0;
  let max = 0;
  for (let q = 0; q < fila.length; q++) {
    const i = fila[q], r = Math.floor(i / nc), c = i % nc;
    for (const [rr, cc] of [[r - 1, c], [r + 1, c], [r, c - 1], [r, c + 1]]) {
      if (rr < 0 || cc < 0 || rr >= nl || cc >= nc) continue;
      const j = rr * nc + cc;
      if (gram[j] && dist[j] < 0) { dist[j] = dist[i] + 1; max = Math.max(max, dist[j]); fila.push(j); }
    }
  }
  return { dist, max, ini };
}
