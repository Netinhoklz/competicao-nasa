// painel.js - infograficos do municipio escolhido (El Nino, chuva, chuva x milho, solo).
// Quase sem texto: cada bloco e um desenho com um numero. Dados: static/data/municipios_ne.json
// (gerado por ferramentas/gerar_municipios.py a partir de IMERG, SMAP e IBGE PAM).

let DADOS = null;   // baixado na primeira viagem: nao disputa banda com as texturas do globo na abertura
const dados = () => (DADOS ??= fetch('/static/data/municipios_ne.json').then((r) => (r.ok ? r.json() : null)).catch(() => null));
const MES = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];
const MES3 = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
const RHO_FIRME = 0.38;   // Spearman significativo a 5% com ~27 anos
const DIST_MAX = 0.6;     // graus: alem disso o ponto nao e de nenhum municipio do Nordeste
const fmt = new Intl.NumberFormat('pt-BR');

const ICONE = {
  onda: '<path d="M2 9c2.5-3 5-3 7.5 0s5 3 7.5 0 3.5-2.2 5-2.5M2 16c2.5-3 5-3 7.5 0s5 3 7.5 0 3.5-2.2 5-2.5"/>',
  chuva: '<path d="M7 15a4.5 4.5 0 0 1 .6-8.96A5.5 5.5 0 0 1 18 7.5a3.75 3.75 0 0 1-.5 7.5M8 18l-1 3M12 18l-1 3M16 18l-1 3"/>',
  gota: '<path d="M12 3c3.5 4.2 5.5 7 5.5 10a5.5 5.5 0 0 1-11 0c0-3 2-5.8 5.5-10z"/>',
  milho: '<path d="M12 3c2.6 2 3.8 5 3.8 8.5S14.5 18 12 21c-2.5-3-3.8-6-3.8-9.5S9.4 5 12 3zM5 12c1.5 4 3.8 7 7 9M19 12c-1.5 4-3.8 7-7 9"/>',
  solo: '<path d="M3 9h18M3 9l2 11h14l2-11M12 9V4M9 6l3-2 3 2M8 14h.5M12 16h.5M15.5 13.5h.5"/>',
};
const icone = (nome) => `<svg class="pn-icone" viewBox="0 0 24 24" aria-hidden="true">${ICONE[nome]}</svg>`;

/** Municipio do lugar: pelo codigo IBGE quando a busca traz; senao, o de centro mais proximo. */
function achar(dados, lugar) {
  const cod = String(lugar.ibge || '').slice(0, 7);
  if (dados.m[cod]) return [cod, dados.m[cod]];
  const cos = Math.cos((lugar.lat * Math.PI) / 180);
  let melhor = null;
  let dMin = DIST_MAX;
  for (const [c, m] of Object.entries(dados.m)) {
    if (m[2] == null) continue;
    const d = Math.hypot(m[2] - lugar.lat, (m[3] - lugar.lon) * cos);
    if (d < dMin) { dMin = d; melhor = [c, m]; }
  }
  return melhor;
}

// ---------------------------------------------------------------- desenhos (SVG)

/** Quatro tubos: quanto choveu em cada estacao que veio depois de um El Nino forte. */
function tubos(analogos, anos) {
  const W = 284, topo = 16, base = 70, teto = 150, larg = 34;
  const y = (v) => base - (Math.min(v, teto) / teto) * (base - topo);
  const passo = (W - 52) / anos.length;
  let s = '';
  analogos.forEach((a, i) => {
    const x = i * passo + (passo - larg) / 2;
    s += `<rect class="pn-tubo" x="${x}" y="${topo}" width="${larg}" height="${base - topo}" rx="5"/>`;
    if (a) {
      const [pct, seco] = a;
      const h = Math.max(3, base - y(pct));
      s += `<rect class="${seco ? 'pn-seco' : 'pn-cheio'}" x="${x + 2}" y="${base - h + 2}" width="${larg - 4}" height="${h - 4}" rx="3">` +
        `<title>${anos[i]}: ${pct}% da chuva normal${seco ? ' (ano seco)' : ''}</title></rect>` +
        `<text class="pn-valor" x="${x + larg / 2}" y="${topo - 6}" text-anchor="middle">${pct}%</text>`;
    }
    s += `<text x="${x + larg / 2}" y="${base + 15}" text-anchor="middle">${anos[i]}</text>`;
  });
  s += `<line class="pn-normal" x1="0" x2="${W - 48}" y1="${y(100)}" y2="${y(100)}"/>` +
    `<text x="${W - 44}" y="${y(100) + 4}">normal</text>`;
  return `<svg viewBox="0 0 ${W} ${base + 20}" role="img" aria-label="Chuva da estação depois de cada El Niño forte, em porcentagem do normal">${s}</svg>`;
}

/** Doze meses de chuva; a estacao (4 meses mais chuvosos) fica acesa. */
function meses(clima, ini) {
  const W = 284, base = 52, passo = W / 12, larg = passo - 6;
  const teto = Math.max(...clima, 1);
  let s = '';
  clima.forEach((mm, i) => {
    const naEstacao = (i - (ini - 1) + 12) % 12 < 4;
    const h = Math.max(2, (mm / teto) * (base - 4));
    const x = i * passo + 3;
    s += `<rect class="${naEstacao ? 'pn-cheio' : 'pn-apagado'}" x="${x}" y="${base - h}" width="${larg}" height="${h}" rx="2.5">` +
      `<title>${MES3[i]}: ${fmt.format(mm)} mm</title></rect>` +
      `<text class="${naEstacao ? 'pn-valor' : ''}" x="${x + larg / 2}" y="${base + 14}" text-anchor="middle">${MES[i]}</text>`;
  });
  return `<svg viewBox="0 0 ${W} ${base + 18}" role="img" aria-label="Chuva média de cada mês">${s}</svg>`;
}

/** Tres degraus: quao firme e a ligacao entre chuva e milho. */
function degraus(n) {
  return `<span class="pn-degraus" aria-hidden="true">${[1, 2, 3].map((k) => `<i class="${k <= n ? 'on' : ''}"></i>`).join('')}</span>`;
}

/** Fila de anos do mais seco ao mais umido; o ponto aceso e o mes de agora. */
function fila(pctl, n) {
  const k = Math.round((pctl / 100) * n);   // quantos anos anteriores foram mais secos
  const pontos = Array.from({ length: n + 1 }, (_, i) => `<i class="${i === k ? 'on' : ''}"></i>`).join('');
  return `<div class="pn-fila" role="img" aria-label="${k} de ${n} anos anteriores foram mais secos">${pontos}</div>` +
    '<div class="pn-pontas"><span>seco</span><span>úmido</span></div>';
}

// ---------------------------------------------------------------- blocos

function blocoNino(m, dados) {
  const validos = m[7].filter(Boolean);
  if (!validos.length) return '';
  const secos = validos.filter((a) => a[1]).length;
  return `<section class="pn-bloco">
    <header>${icone('onda')}<h3>Depois de El Niño forte</h3></header>
    <p class="pn-numero"><b class="${secos >= 3 ? 'pn-alerta' : ''}">${secos}<small>/${validos.length}</small></b><span>anos secos</span></p>
    ${tubos(m[7], dados.analogos)}
  </section>`;
}

function blocoChuva(m) {
  if (!m[6].length || m[4] == null) return '';
  const fim = MES3[(m[4] + 2) % 12];
  return `<section class="pn-bloco">
    <header>${icone('chuva')}<h3>Chuva</h3></header>
    <p class="pn-numero"><b>${fmt.format(m[5])}<small> mm</small></b><span>${MES3[m[4] - 1]}–${fim}</span></p>
    ${meses(m[6], m[4])}
  </section>`;
}

function blocoMilho(m) {
  const rho = m[8], pct = m[9];
  if (rho == null) return '';
  const nivel = rho >= RHO_FIRME ? 3 : rho >= 0.2 ? 2 : 1;
  const rotulo = ['', 'ligação fraca', 'alguma ligação', 'ligação firme'][nivel];
  const conta = nivel === 3 && pct > 0 && pct < 80
    ? `<p class="pn-conta">${icone('gota')}<b>+100<small> mm</small></b><span class="pn-seta" aria-hidden="true"></span>${icone('milho')}<b>+${pct}<small>%</small></b></p>`
    : '';
  return `<section class="pn-bloco">
    <header>${icone('milho')}<h3>Chuva e milho</h3></header>
    ${conta}
    <p class="pn-forca">${degraus(nivel)}<span>${rotulo}</span></p>
  </section>`;
}

function blocoSolo(m, dados) {
  const pctl = m[10], n = m[11];
  if (pctl == null || !n) return '';
  const palavra = pctl < 34 ? 'seco' : pctl < 67 ? 'no meio' : 'úmido';
  return `<section class="pn-bloco">
    <header>${icone('solo')}<h3>Solo, ${dados.solo_mes}</h3></header>
    <p class="pn-numero"><b class="${pctl < 10 ? 'pn-alerta' : ''}">${palavra}</b><span>entre ${n + 1} anos</span></p>
    ${fila(pctl, n)}
  </section>`;
}

// ---------------------------------------------------------------- interface publica

export class Painel {
  constructor(caixa) {
    this.caixa = caixa;
    this.vez = 0;
  }

  /** Desenha o painel do municipio de `lugar`; fora do Nordeste o painel fica escondido. */
  async mostrar(lugar) {
    const vez = ++this.vez;
    const d = await dados();
    if (vez !== this.vez) return;
    const achado = d && achar(d, lugar);
    if (!achado) { this.esconder(); return; }
    const [cod, m] = achado;
    this.caixa.innerHTML = `<p class="pn-fonte">${m[0]}, ${m[1]} · NASA IMERG e SMAP · IBGE</p><div class="pn-fileira">` +
      blocoNino(m, d) + blocoChuva(m) + blocoMilho(m) + blocoSolo(m, d) + '</div>' +
      `<a class="pn-abrir" href="/painel/${cod}">Abrir painel de ${m[0]}<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6"/></svg></a>`;
    this.caixa.hidden = false;
  }

  esconder() {
    this.vez++;
    this.caixa.hidden = true;
    this.caixa.innerHTML = '';
  }
}
