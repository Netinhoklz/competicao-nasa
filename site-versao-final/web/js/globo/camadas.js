// Origem: novo no site final (não existe no site do João Pedro).
// camadas.js - dados sobre os 1.794 municípios no mapa do globo, depois do mergulho. Um controle só (abas no canto de
// baixo à esquerda do mapa) pinta os municípios: quebra do milho em 2027 (projeção), chuva típica da estação (IMERG),
// solo de abr/2015 até agora (SMAP L4, com controle de tempo), calor de 2000 a 2025 (NASA POWER) e água guardada de 2002 a 2026
// (GRACE), os dois também com controle de tempo (web/dados/camadas_tempo.json, ferramentas/preparar_camadas_tempo.py, ~90 KB, baixado só
// quando uma das duas abas abre), e confiança dos dados (web/dados/confianca_mun.json, a aba só aparece se o arquivo existir). Números pré-calculados em ferramentas/preparar_camadas_mapa.py (web/dados/camadas_mun.json,
// ~150 KB); malha de web/dados/malha_ne.json (a mesma do painel e da busca), desprojetada para lon/lat. Tudo é baixado na
// primeira vez que a pessoa encosta no controle. A cor vem de feature-state: trocar de mês não refaz a geometria.
// Perto do chão (zoom > 10) as cores somem e fica a foto; ao escolher uma camada a câmera sobe até ver a região.

import { IC, esc } from '../comum.js';
import { carregar } from './busca.js';

const DADO = (nome) => new URL(`../../dados/${nome}`, import.meta.url);
const OURO = '#ffcb7d';
const ANTES_DE = 'limites';          // as cores ficam embaixo das divisas, dos contornos e dos nomes
const ZOOM_REGIAO = 8.6;             // acima disso, escolher uma camada afasta a câmera até a região
// projeção de malha_ne.json (a de busca.js e de gerar_municipios.py do JP): x, y em px
const LON0 = -48.9, LAT0 = -0.9, ESCALA = 40, COS = Math.cos((9.5 * Math.PI) / 180);
const z = (...p) => ['interpolate', ['linear'], ['zoom'], ...p];

// o estilo do controle vem junto com o módulo (index.html não precisa mudar)
const css = document.createElement('link');
css.rel = 'stylesheet';
css.href = new URL('../../css/globo/camadas.css', import.meta.url);
document.head.appendChild(css);

const ic = (corpo) => `<svg viewBox="0 0 24 24" aria-hidden="true">${corpo}</svg>`;
const IC_FOTO = '<rect x="3.5" y="5" width="17" height="14" rx="2"/><path d="m4 17.5 5-5 4 4 2.5-2.5 4.5 4.5"/><circle cx="15.5" cy="9.5" r="1.6"/>';
const IC_TOCAR = '<path d="M8 5.5v13l10.5-6.5z"/>';
const IC_PARAR = '<path d="M8.5 5.5v13M15.5 5.5v13"/>';
const SELO = { medido: 'MEDIDO', projecao: 'PROJEÇÃO', suposicao: 'SUPOSIÇÃO' };

// ------------------------------------------------------------------ as camadas

// cores validadas (rampas de um tom só, ordem clara → forte); o solo diverge de um "normal" quase transparente: a foto
// aparece onde nada mudou e as cores ficam só onde o ano foi diferente
const SOLO_COR = ['#d4532e', '#eda07a', 'rgba(40, 40, 37, 0.5)', '#86b6ef', '#2f7fe0'];
const SOLO_PALAVRA = ['o mais seco', 'seco', 'normal', 'úmido', 'o mais úmido'];
// calor e água guardada: as mesmas 5 classes em volta de um "normal" quase transparente
const CALOR_COR = ['#2f7fe0', '#86b6ef', 'rgba(40, 40, 37, 0.5)', '#f5ac5f', '#d4532e'];
const AGUA_COR = ['#d4532e', '#eda07a', 'rgba(40, 40, 37, 0.5)', '#86b6ef', '#2f7fe0'];
const num1 = (v) => v.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const sinal1 = (v) => `${v > 0 ? '+' : v < 0 ? '−' : ''}${num1(Math.abs(v))}`;
/** 5 classes por dois cortes simétricos: ≤ −b, ≤ −a, < a, < b, o resto. */
const cinco = (d, a, b) => (d <= -b ? 0 : d <= -a ? 1 : d < a ? 2 : d < b ? 3 : 4);
/** Série anual (calor por célula, água por mesorregião) do município i no ano pos: valor ou null. */
function anual(D, qual, i, pos) {
  const t = D.tempo?.[qual], k = t?.i[i];
  if (k == null || k < 0) return null;
  const v = (qual === 'calor' ? t.cel : t.reg)[k][pos];
  return v == null ? null : v / 10;
}

const CAMADAS = [
  { id: 'foto', nome: 'Foto', icone: IC_FOTO },
  {
    id: 'quebra', nome: 'Milho', icone: IC.milho, selo: 'projecao',
    kicker: 'Quebra do milho · 2027',
    frase: 'Em 10 anos como 2027, em quantos o milho quebra.',
    cores: ['#fde7c8', '#f5ac5f', '#de6524', '#a33a10'],
    rotulos: ['0–2', '3–4', '5–6', '7+'], unidade: 'em 10 anos',
    palavras: ['baixa', 'média', 'alta', 'muito alta'],
    classe: (D, i) => { const v = D.quebra[i]; return v == null ? -1 : v <= 2 ? 0 : v <= 4 ? 1 : v <= 6 ? 2 : 3; },
    valor: (D, i) => (D.quebra[i] == null ? null : `${D.quebra[i]} em 10`),
    vazio: 'sem série de milho',
    fonte: 'Projeção do QUADRA com o IBGE PAM 1998–2025',
    mais: 'Quebra = colher menos da metade do normal do município. A conta usa os anos de El Niño forte (1998, 2010, '
      + '2016 e 2024) do próprio município, puxados para a mesorregião (IBGE PAM, rendimento do milho). É a média do '
      + 'município: não sabe a roça de cada família nem a chuva de fevereiro.',
  },
  {
    id: 'chuva', nome: 'Chuva', icone: IC.chuva, selo: 'medido',
    kicker: 'Chuva do inverno',
    frase: 'Quanto chove na estação, num ano normal.',
    cores: ['#cde2fb', '#86b6ef', '#3987e5', '#1c5cab'],
    rotulos: ['<350', '350–600', '600–900', '900+'], unidade: 'mm',
    palavras: ['pouca', 'média', 'boa', 'muita'],
    classe: (D, i) => { const v = D.chuva[i]; return v == null ? -1 : v < 35 ? 0 : v < 60 ? 1 : v < 90 ? 2 : 3; },
    valor: (D, i) => (D.chuva[i] == null ? null : `${(D.chuva[i] * 10).toLocaleString('pt-BR')} mm`),
    vazio: 'sem dado',
    fonte: 'NASA GPM IMERG V07, 1998–2025',
    mais: 'Chuva desde o início da estação, mediana de 1998 a 2025 sem os El Niños fortes (satélite GPM IMERG, '
      + 'quadrados de 10 km). É o mesmo número do painel ao lado. Perto do mar o satélite vê menos chuva que o pluviômetro.',
  },
  {
    id: 'solo', nome: 'Solo', icone: IC.solo, selo: 'medido', tempo: true,
    serie: (D) => D.solo, marcas: [[0, '2015'], ['2020', '2020'], ['fim', 'agora']], ms: 120, oque: 'Mês do solo',
    resto: (D, i, pos, k) => (k === 0 || k === 4 ? `em ${D.solo.n_anos[pos]} anos` : 'para a época'),
    kicker: 'Solo · 2015 até hoje',
    frase: 'Arraste para ver cada mês desde 2015.',
    cores: SOLO_COR,
    rotulos: ['mais seco', '', 'normal', '', 'mais úmido'],
    palavras: SOLO_PALAVRA,
    classe: (D, i, pos) => {
      const k = parseInt(D.solo.s[i][pos >> 1], 36);
      const c = pos & 1 ? k % 6 : Math.floor(k / 6);
      return c === 5 || Number.isNaN(c) ? -1 : c;
    },
    vazio: 'sem dado',
    fonte: 'NASA SMAP L4 (SPL4SMGP v008), 2015–2026',
    mais: 'Umidade da terra até 1 m de fundura (satélite SMAP L4), no quadrado de 9 km do ponto do município: o mesmo '
      + 'do plano. Cada mês é comparado com o mesmo mês dos outros anos desde 2015; "agora" são os 30 dias até a última '
      + 'data. Na seca do ano a diferença entre os anos é pequena e não prevê a próxima chuva.',
  },
  {
    id: 'calor', nome: 'Calor', icone: IC.termo, selo: 'medido', tempo: true, dado: 'tempo',
    serie: (D) => D.tempo.calor, marcas: [[0, '2000'], ['2010', '2010'], ['fim', '2025']], ms: 450, oque: 'Ano do calor',
    kicker: 'Calor · 2000 a 2025',
    frase: 'Arraste: o dia mais quente de cada ano, contra o normal daqui.',
    cores: CALOR_COR,
    rotulos: ['mais fresco', '', 'normal', '', 'mais quente'],
    palavras: ['bem mais fresco', 'mais fresco', 'normal', 'mais quente', 'bem mais quente'],
    classe: (D, i, pos) => {
      const v = anual(D, 'calor', i, pos);
      return v == null ? -1 : cinco(v - D.tempo.calor.n[D.tempo.calor.i[i]] / 10, 0.4, 1);
    },
    resto: (D, i, pos) => {
      const v = anual(D, 'calor', i, pos), n = D.tempo.calor.n[D.tempo.calor.i[i]] / 10;
      return v == null ? '' : `${num1(v)} °C · ${sinal1(v - n)} °C do normal`;
    },
    vazio: 'sem dado',
    fonte: 'NASA POWER (MERRA-2), grade de ~55 km, 2000–2025',
    mais: 'Média dos 12 meses do dia mais quente de cada mês (NASA POWER, grade de ~55 km, a célula mais perto do município), '
      + 'contra o normal da mesma célula em 2000–2025. Municípios vizinhos dividem a célula: o mapa sai em blocos. Acima de 35 °C '
      + 'na flor, o feijão e o milho perdem grão. Na serra e no baixio a sua roça pode ser mais fresca que o bloco.',
  },
  {
    id: 'agua', nome: 'Água', icone: IC.poco, selo: 'medido', tempo: true, dado: 'tempo',
    serie: (D) => D.tempo.agua, marcas: [[0, '2002'], ['2014', '2014'], ['fim', '2026']], ms: 450, oque: 'Ano da água guardada',
    kicker: 'Água guardada · 2002 a 2026',
    frase: 'Arraste: a água no chão (solo, aquífero, açude) contra 2004–09.',
    cores: AGUA_COR,
    rotulos: ['menos', '', 'como 2004–09', '', 'mais'],
    palavras: ['muito menos água', 'menos água', 'como em 2004–09', 'mais água', 'muito mais água'],
    classe: (D, i, pos) => { const v = anual(D, 'agua', i, pos); return v == null ? -1 : cinco(v, 3, 10); },
    resto: (D, i, pos) => {
      const v = anual(D, 'agua', i, pos);
      return v == null ? '' : `${sinal1(v)} cm · ${D.tempo.agua.nome[D.tempo.agua.i[i]]}`;
    },
    vazio: 'sem dado neste ano',
    fonte: 'NASA GRACE/GRACE-FO (CSR RL06.3 mascons), por mesorregião, 2002–2026',
    mais: 'Os satélites GRACE pesam a água do chão inteiro (solo, aquífero e açudes) pela gravidade. Não enxergam menos que ~300 km: '
      + 'o mapa pinta a mesorregião toda com o mesmo número, em cm de água contra a média de 2004 a 2009. 2017 e 2018 ficam sem dado '
      + '(troca de satélite). Açude, cacimba e poço da sua comunidade dizem mais que esta média.',
  },
  {
    id: 'confianca', nome: 'Confiança', icone: IC.escudo, selo: 'suposicao', opcional: true,
    kicker: 'Confiança dos dados',
    frase: 'Onde é baixa, a palavra do técnico pesa mais.',
    cores: ['#ddd6fb', '#a898f5', '#7259e6'],
    rotulos: ['alta', 'média', 'baixa'], unidade: '',
    palavras: ['alta', 'média', 'baixa'],
    classe: (D, i) => (D.conf ? { alta: 0, media: 1, baixa: 2 }[D.conf[D.cods[i]]?.nivel] ?? -1 : -1),
    valor: () => null,
    vazio: 'sem dado',
    fonte: 'Regra do QUADRA sobre as bases do plano',
    mais: 'Cada motivo de dúvida soma pontos: chuva do satélite perto do mar, IBGE com poucos anos ou misturando lavoura '
      + 'grande e roça de família, data de plantar estimada, El Niño que já deu seca e cheia aqui. 0–1 ponto é alta, '
      + '2–3 média, 4 ou mais baixa. Toque num município para ver o que conferir lá.',
  },
];
const camada = (id) => CAMADAS.find((c) => c.id === id);

// ------------------------------------------------------------------ dados (baixados uma vez, na primeira vez)

const ok = (r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status))));

/** "x y L x y … Z" em px → anel fechado em [lon, lat]. */
function anel(s) {
  const pts = s.replace('Z', '').split('L').map((p) => {
    const [x, y] = p.trim().split(' ').map(Number);
    return [+(x / (COS * ESCALA) + LON0).toFixed(4), +(LAT0 - y / ESCALA).toFixed(4)];
  });
  pts.push(pts[0]);
  return pts;
}

let _dados = null;
function dados() {
  _dados ??= Promise.all([fetch(DADO('camadas_mun.json')).then(ok), fetch(DADO('malha_ne.json')).then(ok), carregar()])
    .then(([c, g, b]) => {
      const cods = c.cods.split(',');
      return {
        cods,
        idx: Object.fromEntries(cods.map((k, i) => [k, i])),
        quebra: c.quebra,
        chuva: c.chuva,
        solo: c.solo,
        m: b?.m || {},
        // cada anel vira um polígono (os 5 municípios com mais de um anel são ilhas, sem buracos)
        geo: {
          type: 'FeatureCollection',
          features: cods.filter((k) => g.m[k]).map((k) => ({
            type: 'Feature',
            id: Number(k),
            properties: {},
            geometry: { type: 'MultiPolygon', coordinates: g.m[k].split('M').filter(Boolean).map((s) => [anel(s)]) },
          })),
        },
        conf: null,
        confTextos: null,
      };
    })
    .catch(() => { _dados = null; return null; });
  return _dados;
}

// calor e água guardada: um arquivo só (preparar_camadas_tempo.py), baixado na 1ª vez que uma das duas abas abre
let _tempo = null;
function tempo(D) {
  _tempo ??= fetch(DADO('camadas_tempo.json')).then(ok).then((t) => {
    if (t.n !== D.cods.length) throw new Error('ordem dos municípios diferente');
    const rot = (x) => Array.from({ length: x.fim - x.ini + 1 }, (_, k) => String(x.ini + k));
    D.tempo = { calor: { ...t.calor, rotulos: rot(t.calor) }, agua: { ...t.agua, rotulos: rot(t.agua) } };
    return true;
  }).catch(() => { _tempo = null; return false; });
  return _tempo;
}

// confiança: arquivo de outro passo (preparar_confianca.py); só entra se existir
const URL_CONF = DADO('confianca_mun.json');
let _conf = null;
function confianca(D) {
  _conf ??= fetch(URL_CONF).then(ok).then((c) => { D.conf = c; D.confTextos = c._textos || {}; return true; })
    .catch(() => { _conf = null; return false; });
  return _conf;
}

// ------------------------------------------------------------------ o controle

export class Camadas {
  /**
   * @param mapa  maplibregl.Map (com o estilo de mapa.js)
   * @param perto fn() → câmera da chegada ao município (para a aba Foto voltar até lá)
   */
  constructor(mapa, { perto } = {}) {
    this.mapa = mapa;
    this.perto = perto;
    this.atual = 'foto';
    this.cod = null;      // município escolhido na busca (contorno dourado)
    this.foco = null;     // município da legenda e da faixa do tempo (o escolhido ou o último tocado)
    this.pos = null;      // posição do tempo no solo (null = agora)
    this.D = null;
    this.toca = 0;        // intervalo do "tocar" do tempo

    this.el = document.createElement('div');
    this.el.className = 'maplibregl-ctrl cam';
    this.el.innerHTML = `<div class="cam-legenda" hidden></div>
      <p class="cam-convite">Ver no mapa</p>
      <div class="cam-abas" role="radiogroup" aria-label="Dados no mapa">${CAMADAS.map((c) => `
        <button type="button" role="radio" data-id="${c.id}" aria-checked="${c.id === 'foto'}"${c.opcional ? ' hidden' : ''}
          title="${esc(c.kicker || 'Só a foto do satélite')}">${ic(c.icone)}<span>${esc(c.nome)}</span></button>`).join('')}
      </div>`;
    this.legendaEl = this.el.querySelector('.cam-legenda');
    this.el.querySelector('.cam-abas').addEventListener('click', (e) => {
      const b = e.target.closest('button[data-id]');
      if (b) this.escolher(b.dataset.id);
    });
    // baixa os dados quando a pessoa chega perto do controle: o primeiro toque já sai pronto
    const antes = () => dados();
    this.el.addEventListener('pointerenter', antes, { once: true });
    this.el.addEventListener('focusin', antes, { once: true });
    this.el.addEventListener('touchstart', antes, { once: true, passive: true });

    this.dica = document.createElement('div');
    this.dica.className = 'cam-dica';
    this.dica.hidden = true;
  }

  // IControl do MapLibre
  onAdd() { return this.el; }
  onRemove() { this.el.remove(); }

  /** Fontes, camadas e controle: chamar uma vez, depois do 'load' do estilo. */
  ligar() {
    const m = this.mapa;
    m.addSource('cam', {
      type: 'geojson',
      data: { type: 'FeatureCollection', features: [] },
      attribution: 'Camadas: NASA SMAP L4, GPM IMERG, POWER e GRACE, IBGE PAM (QUADRA)',
    });
    const escondida = { visibility: 'none' };
    m.addLayer({
      id: 'cam-cor',
      type: 'fill',
      source: 'cam',
      maxzoom: 11,
      layout: escondida,
      paint: { 'fill-color': 'rgba(0, 0, 0, 0)', 'fill-antialias': false, 'fill-opacity': z(4.5, 0.88, 7.5, 0.84, 9.2, 0.6, 10.6, 0) },
    }, ANTES_DE);
    m.addLayer({
      id: 'cam-borda',
      type: 'line',
      source: 'cam',
      maxzoom: 11,
      layout: escondida,
      paint: { 'line-color': 'rgba(8, 9, 12, 0.6)', 'line-width': z(5, 0.3, 8, 0.9), 'line-opacity': z(4.5, 0.6, 9.2, 0.7, 10.6, 0) },
    }, ANTES_DE);
    m.addLayer({
      id: 'cam-sobre',
      type: 'line',
      source: 'cam',
      maxzoom: 11,
      layout: { ...escondida, 'line-join': 'round' },
      filter: ['==', ['id'], -1],
      paint: { 'line-color': '#fff', 'line-width': 1.6, 'line-opacity': z(9.2, 0.9, 10.6, 0) },
    }, ANTES_DE);
    m.addLayer({
      id: 'cam-sel',
      type: 'line',
      source: 'cam',
      maxzoom: 11,
      layout: { ...escondida, 'line-join': 'round' },
      filter: ['==', ['id'], -1],
      // o contorno oficial do IBGE (mapa.js, 'mun-linha') assume a partir de z9
      paint: { 'line-color': OURO, 'line-width': 2.2, 'line-opacity': z(8.6, 1, 9.8, 0) },
    }, ANTES_DE);
    m.addControl(this, 'bottom-left');
    m.getContainer().appendChild(this.dica);

    m.on('mousemove', 'cam-cor', (e) => this._sobre(e.features[0]?.id, e.point));
    m.on('mouseleave', 'cam-cor', () => this._sobre(null));
    m.on('click', 'cam-cor', (e) => {
      const id = e.features[0]?.id;
      if (id == null) return;
      this._focar(String(id));
      this._sobre(id, e.point);
    });
    m.on('movestart', (e) => { if (e.originalEvent) this._sobre(null); });
    // perto do chão as cores somem (fica a foto): a legenda avisa como trazê-las de volta
    const chao = () => this.el.classList.toggle('cam-chao', m.getZoom() > 10.2);
    m.on('zoomend', chao);
    chao();

    // a aba Confiança só aparece se o arquivo do outro passo existir (HEAD: não baixa o arquivo)
    fetch(URL_CONF, { method: 'HEAD' })
      .then((r) => { if (r.ok) this.el.querySelector('[data-id="confianca"]').hidden = false; })
      .catch(() => {});
  }

  /** Município escolhido na busca (código IBGE) ou null. */
  municipio(cod) {
    this.cod = cod || null;
    this.foco = this.cod;
    if (!this.mapa.getLayer('cam-sel')) return;
    this.mapa.setFilter('cam-sel', ['==', ['id'], this.cod ? Number(this.cod) : -1]);
    if (this.atual !== 'foto') this._atualizar();
  }

  /** Volta para a foto sem mexer na câmera (nova viagem, subida para o espaço). */
  desligar() {
    this._escolhida('foto');
    this._mostrar(false);
  }

  async escolher(id) {
    if (id === this.atual) return;
    const tinha = this.atual !== 'foto';
    this._escolhida(id);
    if (id === 'foto') {
      this._mostrar(false);
      const a = this.perto?.();
      if (a && this.mapa.getZoom() < ZOOM_REGIAO) this.mapa.flyTo({ ...a, duration: 2600, curve: 1.3 });
      return;
    }
    this.legendaEl.hidden = false;
    this.legendaEl.innerHTML = '<p class="cam-carregando">Carregando os dados…</p>';
    const D = await dados();
    if (D && id === 'confianca') await confianca(D);
    if (D && camada(id).dado === 'tempo') await tempo(D);
    if (this.atual !== id) return;   // a pessoa já trocou de aba
    if (!D || (id === 'confianca' && !D.conf) || (camada(id).dado === 'tempo' && !D.tempo)) {
      this.legendaEl.innerHTML = '<p class="cam-carregando">Os dados do mapa não carregaram. Tente de novo.</p>';
      this._mostrar(false, true);
      return;
    }
    if (!this.D) {
      this.D = D;
      this.mapa.getSource('cam').setData(D.geo);
    }
    // cada aba com tempo tem a própria régua: ao trocar de aba, o controle volta para o fim dela (o mais recente)
    if (camada(id).tempo) this.pos = camada(id).serie(D).rotulos.length - 1;
    this._legenda();
    this._pintar();
    this._mostrar(true);
    if (!tinha) {
      await this._assentar();
      if (this.atual === id) this._afastar();
    }
  }

  // ---------------------------------------------------------------- por dentro

  _escolhida(id) {
    this.atual = id;
    this._parar();
    this._sobre(null);
    this.el.classList.toggle('cam-ligada', id !== 'foto');
    // no celular o mapa é baixo: com uma camada ligada, o cartão do lugar recolhe (camadas.css) e a legenda diz o nome
    document.body.classList.toggle('cam-ligada', id !== 'foto');
    this.el.querySelectorAll('.cam-abas button').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.id === id)));
  }

  _mostrar(sim, manterLegenda = false) {
    if (!this.mapa.getLayer('cam-cor')) return;
    for (const l of ['cam-cor', 'cam-borda', 'cam-sobre', 'cam-sel']) this.mapa.setLayoutProperty(l, 'visibility', sim ? 'visible' : 'none');
    if (!sim && !manterLegenda) this.legendaEl.hidden = true;
    if (!sim) this._sobre(null);
  }

  /** Espera o mapa parar de mudar de tamanho (no celular ele cresce quando uma camada liga; camadas.css). */
  async _assentar() {
    const caixa = this.mapa.getContainer(), t0 = performance.now();
    let h = -1, iguais = 0;
    while (iguais < 3 && performance.now() - t0 < 1200) {
      await new Promise((ok) => requestAnimationFrame(ok));
      iguais = caixa.clientHeight === h ? iguais + 1 : 0;
      h = caixa.clientHeight;
    }
    this.mapa.resize();
  }

  /**
   * Câmera até a região: o município no meio da parte livre do mapa (acima do controle, à esquerda dos botões),
   * com uns 2 graus de vizinhança em volta; zoom entre 6 (celular) e 7,6 (tela grande).
   */
  _afastar() {
    if (this.mapa.getZoom() <= ZOOM_REGIAO) return;
    const p = this.D.m[this.cod];
    const [lon, lat] = p ? [p[3], p[2]] : this.mapa.getCenter().toArray();
    const caixa = this.mapa.getContainer();
    // no celular a marca e o "Voltar ao espaço" ficam por cima do alto do mapa
    const livre = { top: caixa.clientWidth < 600 ? 104 : 24, bottom: Math.min(this.el.getBoundingClientRect().height + 24, caixa.clientHeight * 0.55), left: 16, right: 56 };
    const larg = Math.max(caixa.clientWidth - livre.left - livre.right, 120);
    const alt = Math.max(caixa.clientHeight - livre.top - livre.bottom, 120);
    const zoom = Math.max(6, Math.min(7.6, Math.log2(Math.min(larg / 4.8, alt / 3.8) * (360 / 512))));
    // sem 'padding' no flyTo (o MapLibre guarda o padding e ele mexeria nas outras viagens): desloca o centro à mão
    const k = 360 / (512 * 2 ** zoom), cos = Math.cos((lat * Math.PI) / 180);
    const dx = (livre.left - livre.right) / 2, dy = (livre.top - livre.bottom) / 2;
    this.mapa.flyTo({ center: [lon - dx * k, lat + dy * k * cos], zoom, pitch: 20, bearing: 0, duration: 2200 });
  }

  _pintar() {
    const L = camada(this.atual), D = this.D, m = this.mapa;
    m.setPaintProperty('cam-cor', 'fill-color',
      ['match', ['coalesce', ['feature-state', 'k'], -1], ...L.cores.flatMap((c, i) => [i, c]), 'rgba(0, 0, 0, 0)']);
    for (let i = 0; i < D.cods.length; i++) m.setFeatureState({ source: 'cam', id: Number(D.cods[i]) }, { k: L.classe(D, i, this.pos) });
  }

  _sobre(id, ponto) {
    if (id == null || this.atual === 'foto' || !this.D) {
      this.dica.hidden = true;
      this.mapa.getLayer('cam-sobre') && this.mapa.setFilter('cam-sobre', ['==', ['id'], -1]);
      return;
    }
    const cod = String(id), i = this.D.idx[cod];
    if (i == null) return;
    this.mapa.setFilter('cam-sobre', ['==', ['id'], Number(id)]);
    const [nome, uf] = this.D.m[cod] || [cod, ''];
    const t = this._texto(i);
    const L = camada(this.atual), extra = L.tempo && L.id !== 'solo' && t.resto ? ` · ${t.resto}` : '';
    this.dica.innerHTML = `<b>${esc(nome)}${uf ? ` · ${uf}` : ''}</b><span>${esc((t.num ? `${t.num} · ${t.palavra}` : t.palavra) + extra)}</span>`
      + (t.nota ? `<small>Confira: ${esc(t.nota)}</small>` : '');
    this.dica.hidden = false;
    const caixa = this.mapa.getContainer(), w = this.dica.offsetWidth, h = this.dica.offsetHeight;
    const x = Math.min(ponto.x + 14, caixa.clientWidth - w - 8), y = ponto.y + h + 22 > caixa.clientHeight ? ponto.y - h - 12 : ponto.y + 16;
    this.dica.style.transform = `translate(${Math.max(8, x)}px, ${Math.max(8, y)}px)`;
  }

  _focar(cod) {
    this.foco = cod;
    this._atualizar();
  }

  /** {num, palavra, resto, nota} do município i na camada atual ("6 em 10" · "alta"; "out/2016" · "seco" · "para a época"). */
  _texto(i) {
    const L = camada(this.atual), D = this.D, k = L.classe(D, i, this.pos);
    if (k < 0) return { num: L.tempo ? L.serie(D).rotulos[this.pos] : '', palavra: L.vazio, resto: '' };
    if (L.tempo) return { num: L.serie(D).rotulos[this.pos], palavra: L.palavras[k], resto: L.resto(D, i, this.pos, k) };
    let nota = '';
    if (L.id === 'confianca' && k > 0) {
      // o motivo de maior peso diz o que conferir no lugar
      const mot = (D.conf[D.cods[i]].motivos || []).map((x) => D.confTextos[x]).filter((x) => x && x.peso > 0)
        .sort((a, b) => b.peso - a.peso)[0];
      nota = mot?.tecnico || '';
    }
    return { num: L.valor(D, i), palavra: L.palavras[k], resto: '', nota };
  }

  _legenda() {
    const L = camada(this.atual), D = this.D;
    const rot = L.tempo ? L.serie(D).rotulos : [], ult = rot.length - 1;
    // marcas da régua: 0, o fim ou um ano ("2020" acha "jan/2020" no solo e "2020" no calor)
    const onde = (m) => (m === 'fim' ? ult : typeof m === 'number' ? m : Math.max(0, rot.findIndex((r) => r === m || r.endsWith(`/${m}`))));
    this.legendaEl.classList.toggle('tempo', !!L.tempo);
    this.legendaEl.innerHTML = `
      <p class="cam-topo"><span class="cam-kicker">${esc(L.kicker)}</span>
        <span class="cam-selo ${L.selo}" title="${esc(L.fonte)}">${SELO[L.selo]}</span></p>
      <p class="cam-valor" aria-live="polite"></p>
      <p class="cam-nota" hidden></p>
      ${L.tempo ? `
        <div class="cam-tempo">
          <button type="button" class="cam-tocar" aria-label="Tocar">${ic(IC_TOCAR)}</button>
          <div class="cam-trilho">
            <svg class="cam-faixa" viewBox="0 0 ${ult + 1} 10" preserveAspectRatio="none" aria-hidden="true"></svg>
            <input type="range" min="0" max="${ult}" step="1" value="${this.pos}" aria-label="${esc(L.oque)}">
            <div class="cam-anos" aria-hidden="true">
              ${L.marcas.map(([m, t]) => `<span style="left:${(onde(m) / ult) * 100}%">${esc(t)}</span>`).join('')}
            </div>
          </div>
        </div>` : ''}
      <p class="cam-frase">${esc(L.frase)}</p>
      <p class="cam-aviso-chao">Afaste o mapa para ver as cores.</p>
      <div class="cam-escala${L.tempo ? ' diverge' : ''}">${L.cores.map((c, i) => `
        <span><i style="background:${c}"></i>${L.rotulos[i] ? `<small>${esc(L.rotulos[i])}</small>` : ''}</span>`).join('')}
        ${L.unidade ? `<em>${esc(L.unidade)}</em>` : ''}</div>
      <details class="cam-mais"><summary>Como lemos</summary><p>${esc(L.mais)}</p><p class="cam-fonte">${esc(L.fonte)}</p></details>`;
    if (L.tempo) {
      const r = this.legendaEl.querySelector('input[type=range]');
      let quadro = 0;
      r.addEventListener('input', () => {
        this._parar();
        this.pos = Number(r.value);
        cancelAnimationFrame(quadro);
        quadro = requestAnimationFrame(() => { this._pintar(); this._atualizar(); });
      });
      this.legendaEl.querySelector('.cam-tocar').addEventListener('click', () => (this.toca ? this._parar() : this._tocar()));
    }
    this._atualizar();
  }

  /** Linha do valor do município em foco, nota e faixa do tempo. */
  _atualizar() {
    const L = camada(this.atual), D = this.D, el = this.legendaEl;
    if (!D || !L.cores) return;
    const valor = el.querySelector('.cam-valor'), nota = el.querySelector('.cam-nota');
    const i = this.foco != null ? D.idx[this.foco] : null;
    if (i == null) {
      valor.innerHTML = '<span class="cam-nome">Toque num município</span>';
      nota.hidden = true;
    } else {
      const t = this._texto(i), nome = (D.m[this.foco] || [this.foco])[0];
      const [grande, pequeno] = L.tempo ? [t.palavra, t.resto] : t.num ? [t.num, t.palavra] : [t.palavra, ''];
      valor.innerHTML = `<span class="cam-nome">${esc(nome)}${L.tempo ? ` · ${esc(t.num)}` : ''}</span>`
        + `<b>${esc(grande)}</b>${pequeno ? `<small>${esc(pequeno)}</small>` : ''}`;
      nota.textContent = t.nota ? `Confira: ${t.nota}` : '';
      nota.hidden = !t.nota;
    }
    if (L.tempo) {
      const svg = el.querySelector('.cam-faixa'), r = el.querySelector('input[type=range]');
      r.value = this.pos;
      if (i == null) { svg.innerHTML = ''; return; }
      if (svg.dataset.i !== String(i)) {
        svg.dataset.i = String(i);
        svg.innerHTML = L.serie(D).rotulos.map((_, p) => {
          const k = L.classe(D, i, p);
          return k < 0 ? '' : `<rect x="${p}" y="0" width="1.02" height="10" fill="${L.cores[k]}"/>`;
        }).join('');
      }
    }
  }

  _tocar() {
    const L = camada(this.atual), ult = L.serie(this.D).rotulos.length - 1;
    if (this.pos >= ult) this.pos = 0;
    this.legendaEl.querySelector('.cam-tocar').innerHTML = ic(IC_PARAR);
    this.legendaEl.querySelector('.cam-tocar').setAttribute('aria-label', 'Parar');
    this.toca = setInterval(() => {
      this.pos = Math.min(this.pos + 1, ult);
      this._pintar();
      this._atualizar();
      if (this.pos >= ult) this._parar();
    }, L.ms || 120);
  }

  _parar() {
    if (!this.toca) return;
    clearInterval(this.toca);
    this.toca = 0;
    const b = this.legendaEl.querySelector('.cam-tocar');
    if (b) { b.innerHTML = ic(IC_TOCAR); b.setAttribute('aria-label', 'Tocar'); }
  }
}
