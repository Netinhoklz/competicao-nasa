// rocacerta.js - painel do municipio: abas, faixa de sinal, indicadores, mapa e grafico.
// Pouco texto: cada informacao e um desenho com um numero. Dados (static/data/, gerados por
// ferramentas/gerar_municipios.py): municipios_ne.json (IMERG, SMAP, IBGE, ONI) e malha_ne.json (malha IBGE).

const [D, G] = await Promise.all([
  fetch('/static/data/municipios_ne.json').then((r) => r.json()),
  fetch('/static/data/malha_ne.json').then((r) => r.json()),
]);

// campos de cada municipio (ver D.campos)
const F = { nome: 0, uf: 1, ini: 4, normal: 5, clima: 6, analogos: 7, rho: 8, pct100: 9, solo: 10, soloN: 11, semi: 12, serie: 13 };
const MES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
const UF_NOME = { MA: 'Maranhão', PI: 'Piauí', CE: 'Ceará', RN: 'Rio Grande do Norte', PB: 'Paraíba', PE: 'Pernambuco', AL: 'Alagoas', SE: 'Sergipe', BA: 'Bahia' };
const RHO_FIRME = 0.38;   // Spearman significativo a 5% com ~27 anos
const HOJE = new Date().getMonth();
const fmt = new Intl.NumberFormat('pt-BR');
const $ = (id) => document.getElementById(id);

// escalas (rampas azul e azul/vermelho do guia de visualizacao, seguras para daltonismo)
const DIV = ['#a8322a', '#d96c5a', '#f0b9ad', 'var(--meio)', '#9ec5f4', '#3987e5', '#184f95'];
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
const faixaDe = (v, cortes) => { let k = 0; while (k < cortes.length && v >= cortes[k]) k++; return k; };
const mediana = (xs) => { const s = xs.filter((x) => x != null).sort((a, b) => a - b); if (!s.length) return null; const k = s.length >> 1; return s.length % 2 ? s[k] : (s[k - 1] + s[k]) / 2; };
const janela = (m) => (m[F.ini] == null ? '' : `${MES[m[F.ini] - 1]}–${MES[(m[F.ini] + 2) % 12]}`);
const naEstacao = (m, mes0) => m[F.ini] != null && (mes0 - (m[F.ini] - 1) + 12) % 12 < 4;

// ------------------------------------------------------------------ leituras por municipio

function nino(m) {
  const val = m[F.analogos].filter(Boolean);
  return { n: val.length, secos: val.filter((a) => a[1]).length, pct: mediana(val.map((a) => a[0])) };
}
function solo(m) {
  const p = m[F.solo], n = m[F.soloN];
  if (p == null || !n) return null;
  const k = Math.round((p / 100) * n);   // anos anteriores mais secos que agora
  const palavra = p < 10 ? 'muito seco' : p < 34 ? 'seco' : p < 67 ? 'normal' : 'úmido';
  return { p, n, k, palavra };
}
function ligacao(m) {
  const r = m[F.rho];
  if (r == null) return null;
  const nivel = r >= RHO_FIRME ? 3 : r >= 0.2 ? 2 : 1;
  return { r, nivel, palavra: ['', 'fraca', 'média', 'firme'][nivel] };
}

// ------------------------------------------------------------------ mini-graficos (indicadores)

const pontos = (an) => `<div class="pontos" aria-hidden="true">${an.map((a) => `<i class="${a == null ? '' : a[1] ? 'seco' : 'normal'}"></i>`).join('')}</div>`;
const meses = (m) => `<div class="meses" aria-hidden="true">${MES.map((x, i) => `<span class="${naEstacao(m, i) ? 'on' : ''} ${i === HOJE ? 'hoje' : ''}">${x[0].toUpperCase()}</span>`).join('')}</div>`;
const degraus = (n) => `<div class="degraus" aria-hidden="true">${[1, 2, 3].map((k) => `<i class="${k <= n ? 'on' : ''}"></i>`).join('')}</div>`;
const fila = (s) => `<div class="fila" aria-hidden="true">${Array.from({ length: s.n + 1 }, (_, i) => `<i class="${i === s.k ? 'on' : ''}"></i>`).join('')}</div><div class="pontas"><span>seco</span><span>úmido</span></div>`;
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
      const e = nino(m);
      if (!e.n) return { tipo: 'idle', titulo: 'Sem série de chuva', pilula: '' };
      const tipo = e.secos >= 3 ? 'bad' : e.secos === 2 ? 'warn' : 'ok';
      return { tipo, icone: tipo === 'ok' ? 'ok' : 'alerta', titulo: `Depois de El Niño forte, chuva fraca em ${e.secos} de ${e.n} anos`, pilula: ['Risco baixo', 'Risco baixo', 'Risco médio', 'Risco alto', 'Risco alto'][e.secos] };
    },
    indicadores(m) {
      const e = nino(m), oni = D.oni;
      return ind('termo', 'El Niño agora', `${oni.valor > 0 ? '+' : ''}${fmt.format(oni.valor)}<small>°C</small>`, `Pacífico, ${oni.mes}`, escalaOni(oni.valor))
        + ind('chuva', 'Anos secos', `${e.secos}<small>de ${e.n}</small>`, D.analogos.join(' · '), pontos(m[F.analogos]))
        + (e.pct == null ? '' : ind('gota', 'Chuva nesses anos', `${fmt.format(Math.round(e.pct))}<small>%</small>`, 'do normal', barraNormal(e.pct)))
        + ind('sol', 'Normal da estação', `${fmt.format(m[F.normal] ?? 0)}<small>mm</small>`, janela(m), meses(m));
    },
    mapa: {
      titulo: 'Chuva depois de El Niño forte', valor: (m) => nino(m).pct, cortes: [60, 80, 95, 105, 120, 140], cores: DIV,
      rotulos: ['< 60%', '60–80', '80–95', 'normal', '105–120', '120–140', '> 140%'], dica: (v) => `${fmt.format(Math.round(v))}% do normal`,
    },
    grafico(m) {
      $('graficoTitulo').textContent = 'Chuva da estação, ano a ano';
      const vals = m[F.serie], an = (i) => D.analogos.includes(D.anos[i]);
      barras({
        vals, rotulos: D.anos.map((a, i) => (an(i) || i === 0 || i === D.anos.length - 1 ? a : '')), linha100: true, teto: 180, eixo: [0, 50, 100, 150],
        destaque: an, cor: (i) => (an(i) ? 'var(--amber)' : 'var(--meio)'),
        dica: (i) => `<b>${D.anos[i]}${an(i) ? ' · El Niño forte' : ''}</b>${vals[i] == null ? 'sem dado' : `${vals[i]}% do normal (${fmt.format(Math.round((vals[i] * (m[F.normal] ?? 0)) / 100))} mm)`}`,
      });
      return [['var(--amber)', 'depois de El Niño forte'], ['var(--meio)', 'outros anos']];
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
  { id: 'veranico', nome: 'Veranico', icone: 'sol', vazia: true },
  { id: 'rocado', nome: 'Roçado', icone: 'fogo', vazia: true },
  {
    id: 'alerta', nome: 'Alerta', icone: 'sino',
    faixa(m) {
      const s = solo(m);
      if (!s) return { tipo: 'idle', icone: 'info', titulo: 'Sem leitura de solo do satélite', pilula: '' };
      const tipo = s.p < 10 ? 'bad' : s.p < 34 ? 'warn' : 'ok';
      return { tipo, icone: tipo === 'ok' ? 'ok' : 'alerta', titulo: `Solo ${s.palavra} para a época (${D.solo_mes})`, pilula: `Solo: ${s.palavra}` };
    },
    indicadores(m) {
      const s = solo(m), e = nino(m);
      return (s ? ind('solo', 'Solo agora', s.palavra, `zona da raiz, ${D.solo_mes}`, fila(s))
        + ind('chuva', 'Anos mais secos que agora', `${s.k}<small>de ${s.n}</small>`, 'mesmo mês, desde 2015', '') : indVazio() + indVazio())
        + ind('onda', 'El Niño: anos secos', `${e.secos}<small>de ${e.n}</small>`, 'veja Inverno 2027', pontos(m[F.analogos]))
        + indVazio();
    },
    mapa: {
      titulo: 'Água no solo agora', valor: (m) => m[F.solo], cortes: [5, 25, 40, 60, 75, 95], cores: DIV,
      rotulos: ['o mais seco', 'bem seco', 'seco', 'normal', 'úmido', 'bem úmido', 'o mais úmido'], dica: (v) => `posição ${fmt.format(Math.round(v))} de 100`,
    },
    grafico(m) {
      $('graficoTitulo').textContent = 'Solo agora entre os anos do satélite';
      const s = solo(m), caixa = $('grafico');
      caixa.onpointermove = null;
      if (!s) { caixa.innerHTML = '<p class="sub">Sem leitura do SMAP para este município.</p>'; return []; }
      const W = 640, H = 170, n = s.n + 1, passo = (W - 40) / n;
      let svg = '';
      for (let i = 0; i < n; i++) {
        const x = 20 + i * passo, on = i === s.k;
        svg += `<rect x="${x + 3}" y="${on ? 30 : 70}" width="${passo - 6}" height="${on ? 90 : 10}" rx="5" fill="${on ? 'var(--ink)' : DIV[Math.min(6, Math.floor((i / (n - 1)) * 7))]}"/>`;
      }
      svg += `<text class="forte" x="${20 + s.k * passo + passo / 2}" y="20" text-anchor="middle">agora</text>
        <text x="20" y="150">mais seco</text><text x="${W - 20}" y="150" text-anchor="end">mais úmido</text>`;
      caixa.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Solo agora na posição ${s.k + 1} de ${n}, do mais seco ao mais úmido">${svg}</svg>`;
      return [['var(--ink)', `${D.solo_mes}`], [DIV[0], 'anos mais secos'], [DIV[6], 'anos mais úmidos']];
    },
  },
  { id: 'entressafra', nome: 'Entressafra', icone: 'celeiro', vazia: true },
];

// ------------------------------------------------------------------ mapa

const svg = $('mapa'), gMun = svg.querySelector('.mun');
const VB_NE = `0 0 ${G.vb[0]} ${G.vb[1]}`;
svg.setAttribute('viewBox', VB_NE);
const cods = Object.keys(G.m).filter((c) => D.m[c]);
gMun.innerHTML = cods.map((c) => `<path data-c="${c}" d="${G.m[c]}"/>`).join('');
svg.querySelector('.ufs').innerHTML = Object.values(G.ufs).map((u) => `<path d="${u.d}"/>`).join('');
const forma = Object.fromEntries([...gMun.children].map((p) => [p.dataset.c, p]));

function pintarMapa(aba) {
  if (aba.vazia) {
    $('mapaTitulo').textContent = 'Escolha o município';
    for (const c of cods) forma[c].style.fill = 'var(--meio)';
    $('legenda').innerHTML = '';
    return;
  }
  const k = aba.mapa;
  $('mapaTitulo').textContent = k.titulo;
  for (const c of cods) {
    const v = k.valor(D.m[c]);
    forma[c].style.fill = v == null ? 'var(--surface-2)' : k.cores[faixaDe(v, k.cortes)];
  }
  $('legenda').innerHTML = k.rotulos.map((r, i) => `<span><i style="background:${k.cores[i]}"></i>${r}</span>`).join('') + '<span><i style="background:var(--surface-2);border:1px solid var(--border)"></i>sem dado</span>';
}

let zoom = 'ne';
function enquadrar() {
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

const estado = { cod: D.m[document.body.dataset.cod] ? document.body.dataset.cod : '2311306', aba: 'inverno' };
try { const a = localStorage.getItem('rc-aba'); if (ABAS.some((x) => x.id === a)) estado.aba = a; } catch (_) { /* sem armazenamento */ }

$('abas').innerHTML = ABAS.map((a) => `<button type="button" data-aba="${a.id}" class="${a.vazia ? 'vazia' : ''}">${ic(a.icone)}${a.nome}</button>`).join('');
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
    faixa.innerHTML = `<span class="sinal">${ic(f.icone || 'info')}</span><h1>${m[F.nome]}: ${f.titulo}</h1>${f.pilula ? `<span class="pilula">${f.pilula}</span>` : ''}`;
    $('indicadores').innerHTML = aba.indicadores(m);
    const leg = aba.grafico(m);
    $('graficoLegenda').innerHTML = leg.map(([c, t]) => `<span><i style="background:${c}"></i>${t}</span>`).join('');
  }
  pintarMapa(aba);
  for (const p of gMun.querySelectorAll('.on')) p.classList.remove('on');
  forma[estado.cod].classList.add('on');
  gMun.appendChild(forma[estado.cod]);
  enquadrar();
  document.title = `${m[F.nome]} · Roça Certa`;
  $('noGlobo').href = `/?lugar=${encodeURIComponent(`${m[F.nome]}, ${UF_NOME[m[F.uf]]}`)}`;
}

function escolher(cod) {
  if (!D.m[cod]) return;
  estado.cod = cod;
  history.replaceState(null, '', `/painel/${cod}`);
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

desenhar();
