// QUADRA, passo "Como plantar": geometria do roçado e conectividade da gramínea, tudo no navegador.
// Desenho (analise/distribuicao.md, seção 2): roçado quadrado com a área da resposta, baixio embaixo, Partes A/B/C em faixas
// em nível (A B C A B C; 3 faixas se cada uma ficar com menos de 10 m), bordas no perímetro sem tirar área (como em
// notebooks/secoes_financeiro/10_familia.py). Ordem das faixas por força bruta nas permutações de A, B e C.
// Conectividade (ideia de Vicente Lima, PercolaCampo; definições p, S e "atravessa" do MANIFESTO de percolação do José):
// grade de ~5 m, vizinhança 4, union-find.

export const GRAMINEAS = new Set(["Milho", "Sorgo granífero", "Sorgo forrageiro", "Milheto"]);
export const ehGram = (cultura) => GRAMINEAS.has(cultura);
export const LIMIAR_SITIO = 0.5927; // malha quadrada, 4 vizinhos (Alonso-Tlali 2025, Entropy 27:386): só régua de referência

const permutacoes = (v) => (v.length <= 1 ? [v] : v.flatMap((x, i) => permutacoes([...v.slice(0, i), ...v.slice(i + 1)]).map((p) => [x, ...p])));

/** Layout do roçado a partir do plano do motor e das respostas efetivas (ctx.ef). Medidas em metros e hectares. */
export function montar(plano, ef) {
  const partes = plano.faixas.filter((f) => /^Parte /.test(f.parte));
  const bx = plano.faixas.find((f) => f.parte === "Baixio") || null;
  const bordas = plano.faixas.find((f) => f.parte === "Bordas") || null;
  const nAnos = plano.anos.length;
  const temBaixio = ef.tem_baixio !== false && !!bx;
  const incerto = temBaixio && ef.tem_baixio === null; // "não sei": baixio de 1/3, tracejado
  const frac = temBaixio ? (incerto ? 1 / 3 : ef.baixio_frac) : 0;
  const ha = ef.ha;
  const lado = Math.sqrt(ha * 1e4);
  const haBaixio = ha * frac;
  const haAlto = ha - haBaixio;
  const profAlto = lado * (1 - frac);
  const nFaixas = profAlto / (2 * partes.length) >= 10 ? 2 * partes.length : partes.length;
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

  const alt = profAlto / nFaixas;
  const conta = {};
  const faixas = melhor.seq.map((f, i) => {
    const letra = f.parte.replace("Parte ", "");
    conta[letra] = (conta[letra] || 0) + 1;
    return { id: letra + conta[letra], letra, parte: f.parte, plano: f, y0: i * alt, y1: (i + 1) * alt, ha: haAlto / nFaixas };
  });
  return {
    ha, lado, frac, temBaixio, incerto, haBaixio, haAlto, profAlto, larguraFaixa: alt, nFaixas,
    haParte: haAlto / partes.length, partes, bx: temBaixio ? bx : null, bordas, nAnos, faixas,
    ordem: melhor.perm.map((i) => partes[i].parte.replace("Parte ", "")),
    contatos: melhor.contatos, piorContatos: pior, todasIguais: iguais,
    encostaBaixio: melhor.seq[melhor.seq.length - 1],
  };
}

/** Grade de ~5 m com a gramínea do ano k, no desenho "faixas" (o do plano) ou "blocos" (A|B|C lado a lado, como se faz hoje).
 *  As linhas da grade seguem as divisas das faixas e do baixio, e as colunas os terços do roçado: a área de cada célula é exata. */
export function grade(lay, k, modo) {
  const linhas = []; // {y0, y1, i: índice da faixa ou -1 no baixio}
  const fatiar = (y0, y1, i) => { const m = Math.max(1, Math.round((y1 - y0) / 5)); for (let j = 0; j < m; j++) linhas.push({ y0: y0 + (y1 - y0) * j / m, y1: y0 + (y1 - y0) * (j + 1) / m, i }); };
  lay.faixas.forEach((f, i) => fatiar(f.y0, f.y1, i));
  if (lay.temBaixio) fatiar(lay.profAlto, lay.lado, -1);
  const nl = linhas.length, np = lay.partes.length;
  const nc = np * Math.max(2, Math.round(lay.lado / 5 / np));
  const largCol = lay.lado / nc;
  const gram = new Uint8Array(nl * nc);
  linhas.forEach((ln, r) => {
    for (let c = 0; c < nc; c++) {
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
  const area = lay.lado * lay.lado;
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
    if (r === 0) o.topo = true;
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
