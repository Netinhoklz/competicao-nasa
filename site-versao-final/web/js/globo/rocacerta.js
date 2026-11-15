// Origem: João Pedro (branch estudo-jp, 29f81f6), site-nasa/static/js/rocacerta.js; adaptado para o site final:
// página estática painel.html?cod=<IBGE>[&embutido=1] (era /painel/<cod> do Flask) e dados por caminho relativo;
// aba Inverno 2027 com a definição única de El Niño do plano (dados/el_nino_uf.json: ONI ≥ 1,5, quadras de 1998,
// 2010, 2016 e 2024; manchete do estado em frequência, barras por ano forte; "carregando dados" se o arquivo
// ainda não existir) no lugar dos 6 anos com ONI ≥ 0,5; sai a aba Alerta (percentil fixo do SMAP de out/2026);
// abas vazias (Veranico, Preparo, Entressafra) escondidas; botão "Montar o plano do meu roçado →" (roca.html#/<cod>/1,
// target=_top); no iframe, avisa a página de cima quando desenhou (postMessage 'painel-pronto').
// rocacerta.js - painel do municipio: abas, faixa de sinal, indicadores, mapa e grafico.
// Pouco texto: cada informacao e um desenho com um numero. Dados (dados/, gerados por
// ferramentas/gerar_municipios.py do JP): municipios_ne.json (IMERG, IBGE, ONI) e malha_ne.json (malha IBGE).

import { faixaDe, naEstacao as estacaoTem } from './util.js';

// ?embutido=1: dentro do painel lateral do globo (o mapa ja esta a esquerda): sem topo, sem mapa, tema escuro
const PARAMS = new URLSearchParams(location.search);
const EMB = PARAMS.has('embutido');
if (EMB) {
  document.documentElement.dataset.theme = 'dark';
  document.body.classList.add('embutido');
}
const dado = (nome) => new URL(`../../dados/${nome}`, import.meta.url);
const [D, G, NINO] = await Promise.all([
  fetch(dado('municipios_ne.json')).then((r) => r.json()),
  EMB ? null : fetch(dado('malha_ne.json')).then((r) => r.json()),
  // El Nino forte por estado (definicao unica do plano); outro passo gera o arquivo: sem ele, "carregando dados"
  fetch(dado('el_nino_uf.json')).then((r) => (r.ok ? r.json() : null)).catch(() => null),
]);

// campos de cada municipio (ver D.campos)
const F = { nome: 0, uf: 1, ini: 4, normal: 5, clima: 6, analogos: 7, rho: 8, pct100: 9, solo: 10, soloN: 11, semi: 12, serie: 13 };
const MES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
const UF_EM = { MA: 'no Maranhão', PI: 'no Piauí', CE: 'no Ceará', RN: 'no Rio Grande do Norte', PB: 'na Paraíba', PE: 'em Pernambuco', AL: 'em Alagoas', SE: 'em Sergipe', BA: 'na Bahia' };
const UF_NOME = { MA: 'Maranhão', PI: 'Piauí', CE: 'Ceará', RN: 'Rio Grande do Norte', PB: 'Paraíba', PE: 'Pernambuco', AL: 'Alagoas', SE: 'Sergipe', BA: 'Bahia' };
const UF_DE = { MA: 'do Maranhão', PI: 'do Piauí', CE: 'do Ceará', RN: 'do Rio Grande do Norte', PB: 'da Paraíba', PE: 'de Pernambuco', AL: 'de Alagoas', SE: 'de Sergipe', BA: 'da Bahia' };
const RHO_FIRME = 0.38;   // Spearman significativo a 5% com ~27 anos
const HOJE = new Date().getMonth();
const fmt = new Intl.NumberFormat('pt-BR');
const $ = (id) => document.getElementById(id);

// escalas (rampas azul e azul/vermelho do guia de visualizacao, seguras para daltonismo)
const SEQ = ['#cde2fb', '#9ec5f4', '#5598e7', '#256abf', '#0d366b'];

const IC = {
  onda: '<path d="M2 9c2.5-3 5-3 7.5 0s5 3 7.5 0 3.5-2.2 5-2.5M2 16c2.5-3 5-3 7.5 0s5 3 7.5 0 3.5-2.2 5-2.5"/>',
  chuva: '<path d="M7 15a4.5 4.5 0 0 1 .6-8.96A5.5 5.5 0 0 1 18 7.5a3.75 3.75 0 0 1-.5 7.5M8 18l-1 3M12 18l-1 3M16 18l-1 3"/>',
  gota: '<path d="M12 3c3.5 4.2 5.5 7 5.5 10a5.5 5.5 0 0 1-11 0c0-3 2-5.8 5.5-10z"/>',
  milho: '<path d="M12 3c2.6 2 3.8 5 3.8 8.5S14.5 18 12 21c-2.5-3-3.8-6-3.8-9.5S9.4 5 12 3zM5 12c1.5 4 3.8 7 7 9M19 12c-1.5 4-3.8 7-7 9"/>',
  solo: '<path d="M3 9h18M3 9l2 11h14l2-11M12 9V4M9 6l3-2 3 2"/>',
  broto: '<path d="M12 21v-9M12 12c0-4 2.5-6.5 7-7 0 4.5-2.5 7-7 7zM12 15c0-3-2-5-6-5.5 0 3.5 2 5.5 6 5.5z"/>',
  sol: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  fogo: '<path d="M12 21c-4 0-6.5-2.6-6.5-6.2 0-3.4 2.6-5.4 3.8-8.8 2.4 1.6 3.4 3.6 3.4 5.6 1-.8 1.6-2 1.8-3.4 2 1.8 4 4.2 4 6.8 0 3.4-2.5 6-6.5 6z"/>',
  sino: '<path d="M6 17V11a6 6 0 0 1 12 0v6l1.5 2h-15L6 17zM10 21h4"/>',
  celeiro: '<path d="M3 21V10l9-6 9 6v11M3 21h18M9 21v-6h6v6"/>',
  termo: '<path d="M10 14.5V5a2 2 0 0 1 4 0v9.5a4 4 0 1 1-4 0z"/><path d="M12 10v7"/>',
  ok: '<path d="M5 12.5 10 17l9-10"/>',
  alerta: '<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4M12 17v.5"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16v.5"/>',
  mais: '<path d="M12 5v14M5 12h14"/>',
};
const ic = (n) => `<svg viewBox="0 0 24 24" aria-hidden="true">${IC[n]}</svg>`;
const janela = (m) => (m[F.ini] == null ? '' : `${MES[m[F.ini] - 1]}–${MES[(m[F.ini] + 2) % 12]}`);
const naEstacao = (m, mes0) => estacaoTem(m[F.ini], mes0);

// ------------------------------------------------------------------ leituras por municipio (regras em util.js)

// El Nino forte (plano, decisao 3): a manchete e o estado, em frequencia; o municipio e o detalhe (o que aconteceu aqui).
// NINO = dados/el_nino_uf.json: {definicao, anos, acaso_pct, uf: {CE: {pct_terco_seco: {ano: %}, media, n_mun}}}
const enso = (m) => NINO?.uf?.[m[F.uf]] ?? null;
const emDez = (v) => Math.round(v / 10);
const ACASO = NINO?.acaso_pct ?? 33;
const FORTES = NINO?.anos ?? D.analogos;   // os mesmos 4 anos (1998, 2010, 2016, 2024) enquanto o arquivo nao chega
// ONI do JP (municipios_ne.json): o valor de "09/2026" e o trimestre centrado em setembro (ago-out, ASO)
const [ONI_MES, ONI_ANO] = D.oni.mes.split('/').map(Number);
const ONI_TRI = `${MES[(ONI_MES + 10) % 12]}–${MES[ONI_MES % 12]} ${ONI_ANO}`;
function ligacao(m) {
  const r = m[F.rho];
  if (r == null) return null;
  const nivel = r >= RHO_FIRME ? 3 : r >= 0.2 ? 2 : 1;
  return { r, nivel, palavra: ['', 'fraca', 'média', 'firme'][nivel] };
}

// ------------------------------------------------------------------ mini-graficos (indicadores)

const meses = (m) => `<div class="meses" aria-hidden="true">${MES.map((x, i) => `<span class="${naEstacao(m, i) ? 'on' : ''} ${i === HOJE ? 'hoje' : ''}">${x[0].toUpperCase()}</span>`).join('')}</div>`;
// % dos municipios do estado no terco mais seco, um ano de El Nino forte por barra; tracejado = acaso (33%)
function anosEstado(e) {
  const vals = FORTES.map((a) => e.pct_terco_seco?.[String(a)] ?? null);
  const W = 220, H = 62, base = 46, n = vals.length, passo = W / n, larg = passo * 0.5, y = (v) => base - (v / 100) * (base - 14);
  let s = `<line x1="0" x2="${W}" y1="${y(ACASO)}" y2="${y(ACASO)}" stroke="var(--muted)" stroke-dasharray="3 3"/>`;
  vals.forEach((v, i) => {
    const x = i * passo + (passo - larg) / 2;
    if (v != null) {
      s += `<rect x="${x}" y="${y(v)}" width="${larg}" height="${Math.max(2, base - y(v))}" rx="3" fill="${v >= 50 ? 'var(--amber)' : 'var(--meio)'}"/>`;
      // frequência natural, como no passo 1 ("7 em 10"), e não "71%"
      s += `<text x="${x + larg / 2}" y="${y(v) - 3}" font-size="9.5" font-weight="700" text-anchor="middle" fill="var(--ink)">${emDez(v)} em 10</text>`;
    } else {
      s += `<text x="${x + larg / 2}" y="${base - 1}" font-size="10" text-anchor="middle" fill="var(--muted)">s/ dado</text>`;
    }
    s += `<text x="${x + larg / 2}" y="${H - 2}" font-size="10" text-anchor="middle" fill="var(--muted)">${FORTES[i]}</text>`;
  });
  return `<svg viewBox="0 0 ${W} ${H}" aria-hidden="true">${s}</svg>`;
}
// nov -> abr: a previsao da estacao so firma quando o Atlantico de fev-mai comeca a aparecer
const REGUA = [10, 11, 0, 1, 2, 3];
const regua = () => `<div class="meses" aria-hidden="true">${REGUA.map((i) => `<span class="${i >= 1 && i <= 3 ? 'on' : ''} ${i === HOJE ? 'hoje' : ''}">${MES[i][0].toUpperCase()}</span>`).join('')}</div>`;
const degraus = (n) => `<div class="degraus" aria-hidden="true">${[1, 2, 3].map((k) => `<i class="${k <= n ? 'on' : ''}"></i>`).join('')}</div>`;
function escalaOni(v) {
  const W = 220, x = (t) => ((Math.max(-2, Math.min(3, t)) + 2) / 5) * W;
  return `<svg viewBox="0 0 ${W} 30" aria-hidden="true">
    <rect x="0" y="10" width="${W}" height="8" rx="4" fill="var(--surface-2)"/>
    <rect x="${x(0.5)}" y="10" width="${x(3) - x(0.5)}" height="8" rx="4" fill="var(--amber-soft)"/>
    <rect x="${x(1.5)}" y="10" width="${x(3) - x(1.5)}" height="8" rx="4" fill="var(--amber)"/>
    <circle cx="${x(v)}" cy="14" r="8" fill="var(--ink)" stroke="var(--surface)" stroke-width="3"/>
    <text x="${x(1.5)}" y="30" font-size="10" fill="var(--muted)">forte</text></svg>`;
}
function barraNormal(pct) {
  const W = 220, teto = 150, x = (v) => (Math.min(v, teto) / teto) * W;
  return `<svg viewBox="0 0 ${W} 30" aria-hidden="true">
    <rect x="0" y="8" width="${W}" height="12" rx="6" fill="var(--surface-2)"/>
    <rect x="0" y="8" width="${x(pct)}" height="12" rx="6" fill="${pct < 90 ? 'var(--amber)' : '#3987e5'}"/>
    <line x1="${x(100)}" x2="${x(100)}" y1="3" y2="25" stroke="var(--ink)" stroke-width="2" stroke-dasharray="3 2"/>
    <text x="${x(100) + 5}" y="31" font-size="10" fill="var(--muted)">normal</text></svg>`;
}
function parte(f) {
  const W = 220;
  return `<svg viewBox="0 0 ${W} 22" aria-hidden="true"><rect x="0" y="5" width="${W}" height="12" rx="6" fill="var(--surface-2)"/>
    <rect x="0" y="5" width="${Math.max(12, f * W)}" height="12" rx="6" fill="var(--green)"/></svg>`;
}
const ind = (icone, titulo, valor, sub, mini) =>
  `<article class="ind"><h3>${ic(icone)}${titulo}</h3><p class="valor">${valor}</p>${sub ? `<p class="sub">${sub}</p>` : ''}<div class="mini">${mini || ''}</div></article>`;
const indVazio = () => '<article class="ind vazio">a definir</article>';

// ------------------------------------------------------------------ graficos grandes (SVG)

function barras({ vals, rotulos, cor, destaque, linha100, teto, dica, eixo }) {
  const W = 640, H = 270, esq = 40, dir = 52, topo = 16, base = 226;
  const max = teto ?? Math.max(...vals.filter((v) => v != null), 1) * 1.1;
  const y = (v) => base - (Math.min(v, max) / max) * (base - topo);
  const passo = (W - esq - dir) / vals.length, larg = Math.max(5, passo * 0.72);
  let s = '';
  eixo.filter((t) => t <= max).forEach((t) => {
    s += `<line class="grade" x1="${esq}" x2="${W - dir}" y1="${y(t)}" y2="${y(t)}"/><text x="${esq - 8}" y="${y(t) + 4}" text-anchor="end">${t}${linha100 ? '%' : ''}</text>`;
  });
  vals.forEach((v, i) => {
    const x = esq + i * passo + (passo - larg) / 2;
    if (v != null) {
      const h = Math.max(2, base - y(v)), r = Math.min(4, h / 2);
      s += `<path d="M${x} ${base}v${-(h - r)}q0 ${-r} ${r} ${-r}h${larg - 2 * r}q${r} 0 ${r} ${r}v${h - r}z" fill="${cor(i, v)}"/>`;
    }
    if (rotulos[i]) s += `<text class="${destaque(i) ? 'forte' : ''}" x="${x + larg / 2}" y="${base + 18}" text-anchor="middle">${rotulos[i]}</text>`;
    s += `<rect class="alvo" data-i="${i}" x="${esq + i * passo}" y="${topo}" width="${passo}" height="${base - topo}"/>`;
  });
  if (linha100) s += `<line class="normal" x1="${esq}" x2="${W - dir}" y1="${y(100)}" y2="${y(100)}"/><text class="forte" x="${W - dir + 6}" y="${y(100) + 4}">normal</text>`;
  const caixa = $('grafico');
  caixa.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img">${s}</svg>`;
  caixa.onpointermove = (e) => { const a = e.target.closest('.alvo'); if (a) mostrarDica(dica(+a.dataset.i), e); else esconderDica(); };
  caixa.onpointerleave = esconderDica;
}

// ------------------------------------------------------------------ abas

const ABAS = [
  {
    id: 'inverno', nome: 'Inverno 2027', icone: 'onda',
    faixa(m) {
      const e = enso(m), de = UF_DE[m[F.uf]];
      if (!NINO) return { tipo: 'idle', icone: 'info', titulo: 'El Niño forte no estado: carregando dados…', pilula: '' };
      if (!e) return { tipo: 'idle', icone: 'info', titulo: 'Sem dado de El Niño forte para este estado', pilula: '' };
      const frase = `Em ${emDez(e.media)} de cada 10 municípios ${de}, a estação ficou no terço mais seco nos anos de El Niño forte.`;
      if (e.media < 40) return { tipo: 'info', icone: 'info', titulo: `${frase} É perto do acaso (${emDez(ACASO)} em 10).`, pilula: 'Previsão firma em fevereiro' };
      return { tipo: 'warn', icone: 'alerta', titulo: `${frase} O acaso daria ${emDez(ACASO)} em 10.`, pilula: 'Previsão firma em fevereiro' };
    },
    indicadores(m) {
      const e = enso(m), oni = D.oni, titulo = `Terço mais seco ${UF_EM[m[F.uf]]}`;
      return ind('termo', 'El Niño agora', `${oni.valor > 0 ? '+' : ''}${fmt.format(oni.valor)}<small>°C</small>`, `ONI ${ONI_TRI} · forte a partir de +1,5`, escalaOni(oni.valor))
        + (e ? ind('chuva', titulo, `${emDez(e.media)}<small>em 10</small>`, `municípios, por ano de El Niño forte · acaso: ${emDez(ACASO)}`, anosEstado(e))
          : ind('chuva', titulo, '…', NINO ? 'sem dado para este estado' : 'carregando dados', ''))
        + ind('info', 'Previsão firma', 'fev', 'quando sai o prognóstico oficial', regua())
        + ind('sol', 'Chuva típica da estação', `${fmt.format(m[F.normal] ?? 0)}<small>mm</small>`, `desde o início da chuva · mediana 1998–2025 sem El Niño forte`, meses(m));
    },
    mapa: {
      titulo: 'Terço mais seco nos anos de El Niño forte, por estado', valor: (m) => enso(m)?.media, cortes: [45, 55, 65],
      cores: ['#9ec5f4', '#f0b9ad', '#d96c5a', '#a8322a'], rotulos: ['até 4 em 10 (acaso: 3)', '5 em 10', '6 em 10', '7 ou mais em 10'],
      dica: (v) => `${emDez(v)} em 10 municípios do estado`,
    },
    grafico(m) {
      $('graficoTitulo').textContent = `Chuva da estação em ${m[F.nome]}, ano a ano (desde o início da chuva; IMERG)`;
      const vals = m[F.serie], an = (i) => FORTES.includes(D.anos[i]);
      barras({
        vals, rotulos: D.anos.map((a, i) => (an(i) || i === 0 || i === D.anos.length - 1 ? a : '')), linha100: true, teto: 180, eixo: [0, 50, 100, 150],
        destaque: an, cor: (i) => (an(i) ? 'var(--amber)' : 'var(--meio)'),
        dica: (i) => `<b>${D.anos[i]}${an(i) ? ' · El Niño forte' : ''}</b>${vals[i] == null ? 'sem dado' : `${vals[i]}% do normal (${fmt.format(Math.round((vals[i] * (m[F.normal] ?? 0)) / 100))} mm)`}`,
      });
      return [['var(--amber)', 'El Niño forte'], ['var(--meio)', 'outros anos'], [null, 'o que aconteceu aqui, não é previsão']];
    },
  },
  {
    id: 'plantar', nome: 'Plantar', icone: 'broto',
    faixa(m) {
      const l = ligacao(m);
      return { tipo: 'info', icone: 'broto', titulo: `Estação de chuva: ${janela(m)}`, pilula: l ? `Chuva e milho: ligação ${l.palavra}` : '' };
    },
    indicadores(m) {
      const l = ligacao(m), clima = m[F.clima], ano = clima.reduce((a, b) => a + (b ?? 0), 0);
      const est = clima.reduce((a, v, i) => a + (naEstacao(m, i) ? v ?? 0 : 0), 0);
      return ind('broto', 'Início da estação', MES[(m[F.ini] ?? 1) - 1], '4 meses mais chuvosos', meses(m))
        + ind('chuva', 'Chuva na estação', `${fmt.format(Math.round((est / Math.max(ano, 1)) * 100))}<small>%</small>`, 'da chuva do ano', parte(est / Math.max(ano, 1)))
        + (l ? ind('milho', 'Chuva e milho', `ligação ${l.palavra}`, `${fmt.format(l.r)} de correlação`, degraus(l.nivel)) : indVazio())
        + (l && l.nivel === 3 && m[F.pct100] > 0 && m[F.pct100] < 80
          ? ind('gota', 'A cada 100 mm', `<span class="conta">${ic('gota')}+100<span class="seta"></span>${ic('milho')}+${m[F.pct100]}%</span>`, 'mais chuva, mais milho', '')
          : ind('gota', 'A cada 100 mm', '–', 'ligação fraca demais para medir', ''));
    },
    mapa: {
      titulo: 'Onde a chuva manda no milho', valor: (m) => m[F.rho], cortes: [0.1, 0.25, RHO_FIRME, 0.55], cores: SEQ,
      rotulos: ['quase nada', 'fraca', 'alguma', 'firme', 'muito firme'], dica: (v) => `correlação ${fmt.format(v)}`,
    },
    grafico(m) {
      $('graficoTitulo').textContent = 'Chuva de cada mês';
      const vals = m[F.clima];
      barras({
        vals, rotulos: MES, eixo: [0, 50, 100, 150, 200, 250, 300], destaque: (i) => naEstacao(m, i) || i === HOJE,
        cor: (i) => (naEstacao(m, i) ? 'var(--green)' : 'var(--meio)'),
        dica: (i) => `<b>${MES[i]}${i === HOJE ? ' · agora' : ''}</b>${fmt.format(vals[i] ?? 0)} mm, média 1998–2025`,
      });
      return [['var(--green)', 'estação de chuva'], ['var(--meio)', 'resto do ano']];
    },
  },
  // site final: a aba Alerta (percentil fixo do SMAP de out/2026) saiu; o "agora" do solo vem do motor (roca.html).
  // As abas vazias ficam na lista, mas escondidas (VISIVEIS), ate terem conteudo.
  { id: 'veranico', nome: 'Veranico', icone: 'sol', vazia: true },
  { id: 'preparo', nome: 'Preparo da terra', icone: 'fogo', vazia: true },
  { id: 'entressafra', nome: 'Entressafra', icone: 'celeiro', vazia: true },
];
const VISIVEIS = ABAS.filter((a) => !a.vazia);

// ------------------------------------------------------------------ mapa

const svg = $('mapa'), gMun = svg.querySelector('.mun');
const VB_NE = G ? `0 0 ${G.vb[0]} ${G.vb[1]}` : '';
const cods = Object.keys(D.m);
let forma = {};
if (!EMB) {
  svg.setAttribute('viewBox', VB_NE);
  gMun.innerHTML = cods.filter((c) => G.m[c]).map((c) => `<path data-c="${c}" d="${G.m[c]}"/>`).join('');
  svg.querySelector('.ufs').innerHTML = Object.values(G.ufs).map((u) => `<path d="${u.d}"/>`).join('');
  forma = Object.fromEntries([...gMun.children].map((p) => [p.dataset.c, p]));
}

function pintarMapa(aba) {
  if (EMB) return;
  if (aba.vazia) {
    $('mapaTitulo').textContent = 'Escolha o município';
    for (const p of Object.values(forma)) p.style.fill = 'var(--meio)';
    $('legenda').innerHTML = '';
    return;
  }
  const k = aba.mapa;
  $('mapaTitulo').textContent = k.titulo;
  for (const c of cods) {
    const v = k.valor(D.m[c]);
    if (forma[c]) forma[c].style.fill = v == null ? 'var(--surface-2)' : k.cores[faixaDe(v, k.cortes)];
  }
  $('legenda').innerHTML = k.rotulos.map((r, i) => `<span><i style="background:${k.cores[i]}"></i>${r}</span>`).join('') + '<span><i style="background:var(--surface-2);border:1px solid var(--border)"></i>sem dado</span>';
}

let zoom = 'ne';
function enquadrar() {
  if (EMB) return;
  const m = D.m[estado.cod];
  $('zoomUf').textContent = UF_NOME[m[F.uf]];
  document.querySelectorAll('[data-zoom]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.zoom === zoom)));
  if (zoom === 'ne') { svg.setAttribute('viewBox', VB_NE); return; }
  const [x0, y0, x1, y1] = G.ufs[m[F.uf]].caixa, f = 12;
  svg.setAttribute('viewBox', `${x0 - f} ${y0 - f} ${x1 - x0 + 2 * f} ${y1 - y0 + 2 * f}`);
}
document.querySelectorAll('[data-zoom]').forEach((b) => b.addEventListener('click', () => { zoom = b.dataset.zoom; enquadrar(); }));

gMun.addEventListener('pointermove', (e) => {
  const p = e.target.closest('path'); if (!p) return;
  const m = D.m[p.dataset.c], aba = ABAS.find((a) => a.id === estado.aba);
  const v = aba.vazia ? null : aba.mapa.valor(m);
  mostrarDica(`<b>${m[F.nome]} · ${m[F.uf]}</b>${aba.vazia ? '' : v == null ? 'sem dado' : aba.mapa.dica(v)}`, e);
});
gMun.addEventListener('pointerleave', esconderDica);
gMun.addEventListener('click', (e) => { const p = e.target.closest('path'); if (p) escolher(p.dataset.c); });

// ------------------------------------------------------------------ dica (tooltip)

const dica = $('dica');
function mostrarDica(html, e) {
  dica.innerHTML = html; dica.hidden = false;
  const w = dica.offsetWidth;
  dica.style.left = `${Math.max(8, Math.min(e.clientX + 14, innerWidth - w - 8))}px`;
  dica.style.top = `${e.clientY + 16}px`;
}
function esconderDica() { dica.hidden = true; }

// ------------------------------------------------------------------ montar

// sem ?cod= (ou codigo que nao e do Nordeste): Quixada, municipio de referencia da proposta (como no app.py do JP)
const COD = PARAMS.get('cod');
const estado = { cod: D.m[COD] ? COD : '2311306', aba: 'inverno' };
try { const a = localStorage.getItem('rc-aba'); if (VISIVEIS.some((x) => x.id === a)) estado.aba = a; } catch (_) { /* sem armazenamento */ }

$('abas').innerHTML = VISIVEIS.map((a) => `<button type="button" data-aba="${a.id}" class="${a.vazia ? 'vazia' : ''}">${ic(a.icone)}${a.nome}</button>`).join('');
$('abas').addEventListener('click', (e) => {
  const b = e.target.closest('button'); if (!b) return;
  estado.aba = b.dataset.aba;
  try { localStorage.setItem('rc-aba', estado.aba); } catch (_) { /* sem armazenamento */ }
  desenhar();
});

function desenhar() {
  const m = D.m[estado.cod], aba = ABAS.find((a) => a.id === estado.aba);
  document.querySelectorAll('#abas button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.aba === aba.id)));
  const faixa = $('faixa');
  if (aba.vazia) {
    faixa.className = 'faixa vazio';
    faixa.innerHTML = `<h1>${m[F.nome]} · ${aba.nome}: conteúdo a definir</h1>`;
    $('indicadores').innerHTML = indVazio().repeat(4);
    $('graficoTitulo').textContent = '';
    $('grafico').innerHTML = '<div class="vazio" style="min-height:360px;border-radius:12px">gráfico a definir</div>';
    $('grafico').onpointermove = null;
    $('graficoLegenda').innerHTML = '';
  } else {
    const f = aba.faixa(m);
    faixa.className = `faixa t-${f.tipo}`;
    faixa.innerHTML = `<span class="sinal">${ic(f.icone || 'info')}</span><div class="faixa-texto"><p class="faixa-lugar">${m[F.nome]} · ${UF_NOME[m[F.uf]]}</p><h1>${f.titulo}</h1></div>${f.pilula ? `<span class="pilula">${f.pilula}</span>` : ''}`;
    $('indicadores').innerHTML = aba.indicadores(m);
    const leg = aba.grafico(m);
    $('graficoLegenda').innerHTML = leg.map(([c, t]) => `<span>${c ? `<i style="background:${c}"></i>` : ''}${t}</span>`).join('');
  }
  $('plano').href = `roca.html#/${estado.cod}/1`;
  pintarMapa(aba);
  if (forma[estado.cod]) {
    for (const p of gMun.querySelectorAll('.on')) p.classList.remove('on');
    forma[estado.cod].classList.add('on');
    gMun.appendChild(forma[estado.cod]);
  }
  enquadrar();
  document.title = `${m[F.nome]} · Roça Certa`;
  $('noGlobo').href = `index.html?lugar=${encodeURIComponent(`${m[F.nome]}, ${UF_NOME[m[F.uf]]}`)}`;
}

function escolher(cod) {
  if (!D.m[cod]) return;
  estado.cod = cod;
  history.replaceState(null, '', `painel.html?cod=${cod}`);
  $('busca').value = '';
  desenhar();
}

// busca por nome
const sem = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
$('lista').innerHTML = cods.map((c) => `<option value="${D.m[c][F.nome]} (${D.m[c][F.uf]})">`).join('');
$('busca').addEventListener('change', (e) => {
  const t = sem(e.target.value);
  if (!t) return;
  const achou = cods.find((c) => sem(`${D.m[c][F.nome]} (${D.m[c][F.uf]})`) === t)
    || cods.find((c) => sem(D.m[c][F.nome]) === t) || cods.find((c) => sem(D.m[c][F.nome]).startsWith(t));
  if (achou) escolher(achou);
  else { e.target.value = ''; e.target.placeholder = 'Não achei. Tente outro nome'; }
});

// tema claro / escuro
$('tema').addEventListener('click', () => {
  const raiz = document.documentElement;
  const escuro = raiz.dataset.theme ? raiz.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  raiz.dataset.theme = escuro ? 'light' : 'dark';
});

if (NINO) {
  $('fonteNino').textContent = ` (forte: ONI de out–dez/nov–jan ≥ 1,5, quadras de ${FORTES.join(', ')})`;
  $('fonteNino').title = NINO.definicao || '';
}
if (EMB) {
  document.querySelector('.fonte').insertAdjacentHTML('beforebegin',
    `<a class="tela-cheia" href="painel.html?cod=${estado.cod}" target="_top">Abrir em tela cheia</a>`);
}
desenhar();
// no painel lateral do globo: avisa a pagina de cima que desenhou (ela tira o botao do plano do cartao do mapa)
if (EMB && parent !== window) parent.postMessage({ quadra: 'painel-pronto', cod: estado.cod }, location.origin);
