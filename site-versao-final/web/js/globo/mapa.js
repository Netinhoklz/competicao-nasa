// Origem: João Pedro (branch estudo-jp, 29f81f6), site-nasa/static/js/mapa.js; adaptado para o site final: nordeste.json por caminho relativo ao módulo; 'municipio' (lugar da busca local, busca.js) entra em ASSENTAMENTO, para a chegada centrar no ponto do município com o zoom tirado da caixa dele. MapLibre local (vendor/); ladrilhos, relevo e limite do IBGE continuam online. Camadas de dados sobre os 1.794 municípios (camadas.js): ligadas depois do 'load', avisadas do município escolhido e desligadas a cada nova viagem e na subida.
// mapa.js - mapa interativo (MapLibre GL, projecao de globo): imagem Sentinel-2 sem nuvens,
// detalhe Maxar ao aproximar, relevo 3D, rotulos vetoriais em portugues, o Nordeste aceso em
// dourado (contorno, divisas e capitais), o limite do municipio escolhido e o marcador do lugar.

import { Camadas } from './camadas.js';

const S2 = 'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2024_3857/default/g/{z}/{y}/{x}.jpg';
// Detalhe de perto: Esri World Imagery Wayback, versao de 2025-07-31. A versao atual tem nuvem e sombra
// sobre Quixada; esta e a mais recente limpa em Quixada, Petrolina, Araripe e Lencois (conferido)
const WAYBACK = 'https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer';
const WAYBACK_VERSAO = 49999;
const TERRENO = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
const IBGE_MALHA = 'https://servicodados.ibge.gov.br/api/v3/malhas/municipios';
const EXAGERO = 1.5;
const ZOOM_PONTO = 12.3;   // zoom de chegada quando o lugar e um ponto (clique ou coordenada)
const ZOOM_AREA_MAX = 12.5; // teto do zoom de chegada para cidades e regioes (bbox)
const OURO = '#ffcb7d';     // o mesmo dourado do fio do Nordeste no globo 3D

/** Tipos do Nominatim que sao uma sede (cidade, vila, distrito...): a chegada centra no ponto, nao no bbox. */
// (site final: + 'municipio', o tipo dos lugares da busca local em busca.js)
export const ASSENTAMENTO = new Set(['city', 'town', 'village', 'hamlet', 'suburb', 'neighbourhood', 'quarter', 'district', 'municipio']);

// O contorno do Nordeste chega junto com o mapa (o mesmo arquivo que o globo 3D usa; principal.js reaproveita este pedido)
export const NORDESTE = fetch(new URL('../../dados/nordeste.json', import.meta.url)).then((r) => r.json()).catch(() => null);

// O MapLibre (1 MB) e o CSS dele (70 KB) não precisam estar na abertura: chegam na primeira vez que o mapa nasce.
// O CSS entra antes de css/globo/style.css, na mesma ordem de antes (o tema dos controles sobrescreve o do MapLibre).
// Se o index.html já trouxer as duas tags, nada é baixado de novo.
const VENDOR = (arq) => new URL(`../../vendor/${arq}`, import.meta.url).href;
let maplibrePronto = null;
function carregarMaplibre() {
  maplibrePronto ??= new Promise((ok, falhou) => {
    let falta = 2;
    const um = () => { if (--falta === 0) ok(); };
    if (document.querySelector('link[href$="maplibre-gl.css"]')) um();
    else {
      const css = document.createElement('link');
      css.rel = 'stylesheet';
      css.href = VENDOR('maplibre-gl.css');
      css.onload = um;
      css.onerror = um;   // sem o CSS o mapa ainda funciona (só os controles ficam crus)
      document.head.insertBefore(css, document.querySelector('link[href$="css/globo/style.css"]'));
    }
    if (window.maplibregl) um();
    else {
      const js = document.createElement('script');
      js.src = VENDOR('maplibre-gl.js');
      js.onload = um;
      js.onerror = () => { maplibrePronto = null; js.remove(); falhou(new Error('O mapa não carregou. Confira a internet.')); };
      document.head.appendChild(js);
    }
  });
  return maplibrePronto;
}
const MUNDO = [[-180, -85], [180, -85], [180, 85], [-180, 85], [-180, -85]];
const area = (anel) => anel.reduce((s, p, i) => { const q = anel[(i + 1) % anel.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0);
/** Poligono do mundo com os aneis como furos (sentido oposto ao do mundo): a mascara "fora daqui". */
const mundoMenos = (aneis) => ({
  type: 'Feature',
  properties: {},
  geometry: { type: 'Polygon', coordinates: [MUNDO, ...aneis.map((a) => (area(a) > 0 ? a.slice().reverse() : a))] },
});
const VAZIO = { type: 'FeatureCollection', features: [] };
const z = (...p) => ['interpolate', ['linear'], ['zoom'], ...p];
// limites nacionais e estaduais do OpenFreeMap, sem os maritimos
const LIMITES = ['all', ['<=', ['coalesce', ['get', 'admin_level'], 99], 4], ['!=', ['coalesce', ['get', 'maritime'], 0], 1]];

const CREDITO_S2 = '<a href="https://s2maps.eu" target="_blank">Sentinel-2 cloudless 2024</a> © EOX IT Services GmbH '
  + '(dados Copernicus Sentinel modificados, '
  + '<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br" target="_blank">CC BY-NC-SA 4.0</a>)';
const CREDITO_OFM = '<a href="https://openfreemap.org" target="_blank">OpenFreeMap</a> '
  + '<a href="https://www.openmaptiles.org/" target="_blank">© OpenMapTiles</a> '
  + '<a href="https://www.openstreetmap.org/copyright" target="_blank">© colaboradores do OpenStreetMap</a>';
const CREDITO_IBGE = 'Limites: <a href="https://servicodados.ibge.gov.br/api/docs/malhas" target="_blank">IBGE</a>';

// textos dos controles do MapLibre em portugues
const TEXTOS = {
  'Map.Title': 'Mapa',
  'Marker.Title': 'Lugar escolhido',
  'NavigationControl.ZoomIn': 'Aproximar',
  'NavigationControl.ZoomOut': 'Afastar',
  'NavigationControl.ResetBearing': 'Arraste para girar; clique para apontar o norte',
  'TerrainControl.Enable': 'Ligar relevo 3D',
  'TerrainControl.Disable': 'Desligar relevo 3D',
  'AttributionControl.ToggleAttribution': 'Créditos',
};

const esperar = (ms) => new Promise((ok) => setTimeout(ok, ms));
const limitar = (v, a, b) => Math.min(b, Math.max(a, v));

// Onde o Wayback nao tem imagem (mar aberto, e a costa em z17) ele responde 404 SEM cabecalho CORS: o
// navegador acusa erro de CORS e o MapLibre nao reconhece o 404. O "tilemap" do servico (com CORS) diz
// quais ladrilhos existem, em blocos de 32 x 32; so os que existem sao pedidos, os outros viram um 404
// silencioso (o MapLibre segue com o Sentinel-2 por baixo).
const BLOCO = 32;
const blocosWayback = new Map();
function waybackTem(z, y, x) {
  const topo = y - (y % BLOCO);
  const esq = x - (x % BLOCO);
  const chave = `${z}/${topo}/${esq}`;
  if (!blocosWayback.has(chave)) {
    blocosWayback.set(chave, fetch(`${WAYBACK}/tilemap/${WAYBACK_VERSAO}/${chave}/${BLOCO}/${BLOCO}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => d?.data ?? null)
      .catch(() => null));
  }
  return blocosWayback.get(chave).then((d) => d?.[(y - topo) * BLOCO + (x - esq)] === 1);
}
const naoHa = (status = 404) => Object.assign(new Error(`Wayback: sem imagem (${status})`), { status });
function registrarWayback() {
  maplibregl.addProtocol('wayback', async ({ url }, abortController) => {
    const [zl, y, x] = url.slice('wayback://'.length).split('/').map(Number);
    if (!(await waybackTem(zl, y, x))) throw naoHa();
    const r = await fetch(`${WAYBACK}/tile/${WAYBACK_VERSAO}/${zl}/${y}/${x}`, { signal: abortController.signal });
    if (!r.ok) throw naoHa(r.status);
    return { data: await r.arrayBuffer() };
  });
}

/**
 * Zoom do MapLibre em que o globo dele aparece do mesmo tamanho que a Terra 3D vista a
 * `dist` raios do centro. Os dois usam o mesmo campo de visao (36,87 graus), entao a
 * distancia da camera a superficie e 1,5 * altura da tela em pixels nos dois.
 */
export function zoomEquivalente(lat, dist) {
  const f = 1.5 * window.innerHeight;
  const raioPx = f / (dist - 1);
  return Math.log2((2 * Math.PI * raioPx * Math.cos((lat * Math.PI) / 180)) / 512);
}

/** Inverso de zoomEquivalente: distancia da camera 3D que reproduz o globo do mapa nesse zoom. */
export function distEquivalente(lat, zoom) {
  const raioPx = (512 * 2 ** zoom) / (2 * Math.PI * Math.cos((lat * Math.PI) / 180));
  return 1 + (1.5 * window.innerHeight) / raioPx;
}

function estilo() {
  const dem = {
    type: 'raster-dem',
    tiles: [TERRENO],
    tileSize: 256,
    // z14 ja passa da resolucao do SRTM (30 m); acima disso os rotulos (OpenFreeMap vai ate z14)
    // fariam o MapLibre avisar "cannot calculate elevation if elevation maxzoom > source.maxzoom"
    maxzoom: 14,
    encoding: 'terrarium',
    attribution: 'Relevo: AWS Terrain Tiles (NASA SRTM, USGS e outros)',
  };
  const s2 = { type: 'raster', tiles: [S2], tileSize: 256, attribution: CREDITO_S2 };
  // no zoom da troca o oceano do Sentinel-2 fica mais escuro e cinza que o da Terra 3D:
  // um pouco mais de saturacao ate z5 aproxima os dois (dE Lab 17 -> 11); de z7 em diante, tom neutro
  const tom = (troca, perto) => ['interpolate', ['linear'], ['zoom'], 5, troca, 7, perto];
  const tomS2 = { 'raster-saturation': tom(0.3, -0.08), 'raster-contrast': tom(-0.1, -0.04), 'raster-brightness-min': 0.05 };

  const nome = ['coalesce', ['get', 'name:pt'], ['get', 'name:latin'], ['get', 'name']];
  const halo = { 'text-halo-color': 'rgba(0, 0, 0, 0.75)', 'text-halo-width': 1.2, 'text-halo-blur': 0.3 };
  // limites e nomes de estado surgem aos poucos ao descer: no zoom da troca o globo do mapa
  // fica limpo como a Terra 3D (a troca acontece no maximo em z4,6, numa tela alta no equador)
  const surgir = ['interpolate', ['linear'], ['zoom'], 4.6, 0, 5.6, 1];
  const rotulo = (id, camada, minzoom, layout, cor, extra = {}) => ({
    id,
    type: 'symbol',
    source: 'ofm',
    'source-layer': camada,
    minzoom,
    ...extra,
    layout: { 'text-field': nome, 'text-font': ['Noto Sans Regular'], 'text-max-width': 8, ...layout },
    paint: { 'text-color': cor, ...halo, ...(extra.paint || {}) },
  });

  return {
    version: 8,
    projection: { type: 'globe' },
    glyphs: 'https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf',
    sources: {
      // rede de seguranca por baixo de tudo: a mesma imagem so em z4, o nivel que a vista da troca
      // (z2,5 a z4,6, conforme latitude e altura da tela) ja carrega antes de o mapa aparecer. De
      // qualquer zoom acima, a base so pede esses ladrilhos, que ja estao na memoria: nem na chegada
      // nem na volta abre buraco preto enquanto o Sentinel-2 ainda esta chegando
      base: { ...s2, maxzoom: 4 },
      s2: { ...s2, maxzoom: 14 },
      // detalhe so de z14 em diante (abaixo disso o S2 basta e o Esri faz costura entre mosaicos);
      // z17 e o ultimo nivel servido (z18 da 404). Em mar aberto o Wayback responde 404 em qualquer zoom
      detalhe: {
        type: 'raster',
        tiles: ['wayback://{z}/{y}/{x}'],
        tileSize: 256,
        minzoom: 14,
        maxzoom: 17,
        attribution: 'Detalhe: © Esri, Maxar (World Imagery Wayback, 2025-07-31)',
      },
      ofm: { type: 'vector', url: 'https://tiles.openfreemap.org/planet', attribution: CREDITO_OFM },
      terreno: dem,
      sombra: { ...dem },
      // Nordeste (IBGE) e municipio escolhido (IBGE): preenchidos quando os dados chegam
      ne: { type: 'geojson', data: VAZIO, attribution: CREDITO_IBGE },
      'ne-fora': { type: 'geojson', data: VAZIO },
      'ne-capitais': { type: 'geojson', data: VAZIO },
      mun: { type: 'geojson', data: VAZIO, attribution: CREDITO_IBGE },
      'mun-fora': { type: 'geojson', data: VAZIO },
    },
    layers: [
      { id: 'base', type: 'raster', source: 'base', paint: tomS2 },
      { id: 's2', type: 'raster', source: 's2', paint: { ...tomS2, 'raster-fade-duration': 250 } },
      {
        id: 'detalhe',
        type: 'raster',
        source: 'detalhe',
        minzoom: 14,
        paint: { 'raster-fade-duration': 250, 'raster-opacity': z(14, 0, 15, 1) },
      },
      {
        id: 'relevo',
        type: 'hillshade',
        source: 'sombra',
        paint: {
          // a foto ja tem sombra propria: o sombreado so ajuda de longe
          'hillshade-exaggeration': ['interpolate', ['linear'], ['zoom'], 4, 0.35, 9, 0.18, 12, 0.05],
          'hillshade-shadow-color': 'rgba(0, 0, 0, 0.45)',
          'hillshade-highlight-color': 'rgba(255, 255, 255, 0.10)',
          'hillshade-accent-color': 'rgba(0, 0, 0, 0)',
        },
      },
      // o que fica fora da regiao (e, perto do chao, fora do municipio) escurece um pouco: a regiao
      // "acende" sem brilho artificial. Zero no zoom da troca (o globo 3D nao escurece nada)
      {
        id: 'mun-fora',
        type: 'fill',
        source: 'mun-fora',
        minzoom: 8.5,
        paint: { 'fill-color': '#000', 'fill-antialias': false, 'fill-opacity': z(8.5, 0, 10, 0.22, 13, 0.15) },
      },
      {
        id: 'ne-fora',
        type: 'fill',
        source: 'ne-fora',
        minzoom: 4.6,
        maxzoom: 9.5,
        paint: { 'fill-color': '#000', 'fill-antialias': false, 'fill-opacity': z(4.6, 0, 5.8, 0.4, 8, 0.32, 9.5, 0) },
      },
      {
        id: 'limites',
        type: 'line',
        source: 'ofm',
        'source-layer': 'boundary',
        minzoom: 4.6,
        filter: LIMITES,   // dentro do Nordeste, abaixo de z10, valem as divisas douradas (ver _nordeste)
        paint: {
          'line-color': 'rgba(255, 255, 255, 0.45)',
          'line-width': ['interpolate', ['linear'], ['zoom'], 3, 0.6, 10, 1.1],
          'line-dasharray': [3, 2],
          'line-opacity': surgir,
        },
      },
      // Nordeste aceso, estatico: o mesmo fio dourado do globo (1 px na troca), afinando ao descer.
      // O arquivo e simplificado a 0,02 grau (~2 km): bom de longe, impreciso perto do chao, entao
      // contorno e divisas somem ate z10, onde o contorno do municipio (IBGE, mais fino) assume
      {
        id: 'ne-halo',
        type: 'line',
        source: 'ne',
        filter: ['==', ['get', 'k'], 'contorno'],
        maxzoom: 9,
        layout: { 'line-join': 'round' },
        paint: { 'line-color': OURO, 'line-width': z(3, 5, 6, 8, 9, 6), 'line-blur': z(3, 4, 6, 6, 9, 5), 'line-opacity': z(4.6, 0, 5.6, 0.2, 7, 0.16, 9, 0) },
      },
      {
        id: 'ne-divisas',
        type: 'line',
        source: 'ne',
        filter: ['==', ['get', 'k'], 'divisa'],
        maxzoom: 10,
        layout: { 'line-join': 'round' },
        paint: { 'line-color': OURO, 'line-width': 1, 'line-opacity': z(4.6, 0.8, 6, 0.42, 8.5, 0.38, 10, 0) },
      },
      {
        id: 'ne-contorno',
        type: 'line',
        source: 'ne',
        filter: ['==', ['get', 'k'], 'contorno'],
        maxzoom: 10,
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: { 'line-color': OURO, 'line-width': z(4.6, 1, 6, 1.6, 10, 1.4), 'line-opacity': z(3, 1, 8.5, 0.85, 10, 0) },
      },
      // o mesmo gesto uma escala abaixo: o limite oficial do municipio da sede
      {
        id: 'mun-halo',
        type: 'line',
        source: 'mun',
        minzoom: 8.5,
        layout: { 'line-join': 'round' },
        paint: { 'line-color': OURO, 'line-width': 6, 'line-blur': 4, 'line-opacity': z(8.5, 0, 10, 0.18, 13, 0.1) },
      },
      {
        id: 'mun-linha',
        type: 'line',
        source: 'mun',
        minzoom: 8.5,
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: { 'line-color': OURO, 'line-width': z(9, 1.2, 13, 1.8), 'line-opacity': z(8.5, 0, 10, 0.9, 14, 0.7) },
      },
      // de baixo para cima: em caso de colisao, a camada de cima ganha
      rotulo('estados', 'place', 4.6,
        { 'text-field': ['upcase', nome], 'text-size': 11, 'text-letter-spacing': 0.2, 'text-max-width': 10 },
        'rgba(242, 244, 247, 0.6)',
        { maxzoom: 8.5, filter: ['==', ['get', 'class'], 'state'], paint: { 'text-opacity': surgir } }),
      // acudes e lagos vem como linha central do espelho d'agua: um nome no meio dela, em pe
      rotulo('aguas', 'water_name', 10,
        {
          'text-font': ['Noto Sans Italic'],
          'text-size': 12,
          'symbol-placement': 'line-center',
          'text-rotation-alignment': 'viewport',
          'text-pitch-alignment': 'viewport',
        },
        'rgba(214, 226, 242, 0.92)'),
      rotulo('picos', 'mountain_peak', 11.5,
        { 'text-font': ['Noto Sans Italic'], 'text-size': 11.5, 'text-anchor': 'top', 'text-offset': [0, 0.4], 'text-padding': 6 },
        'rgba(242, 244, 247, 0.82)'),
      rotulo('vilas', 'place', 10.5,
        { 'text-size': 12, 'text-padding': 10 },
        'rgba(242, 244, 247, 0.85)',
        { filter: ['==', ['get', 'class'], 'village'] }),
      // o nome fica abaixo do ponto: nao briga com o marcador quando o lugar e a propria cidade
      rotulo('cidades', 'place', 5,
        {
          'text-size': ['interpolate', ['linear'], ['zoom'],
            5, ['match', ['get', 'class'], 'city', 13, 11.5],
            12, ['match', ['get', 'class'], 'city', 18, 15.5]],
          'text-anchor': 'top',
          'text-offset': [0, 1.1],
          'text-padding': 8,
          'symbol-sort-key': ['match', ['get', 'class'], 'city', 0, 1],
        },
        '#f2f4f7',
        { filter: ['in', ['get', 'class'], ['literal', ['city', 'town']]] }),
      // as 9 capitais como pontos de luz com nome em tom quente (a mesma lista do globo). Ficam no topo
      // para o nome ganhar a colisao do nome branco do OpenFreeMap; de z10,5 em diante viram so a cidade
      {
        id: 'ne-cap-halo',
        type: 'circle',
        source: 'ne-capitais',
        maxzoom: 10.5,
        paint: {
          'circle-color': OURO,
          'circle-radius': z(3, 7, 6, 11, 9, 14),
          'circle-blur': 1,
          'circle-opacity': z(4.6, 0.12, 6, 0.5, 9, 0.4, 10.5, 0),
          'circle-pitch-alignment': 'map',
        },
      },
      {
        id: 'ne-cap',
        type: 'circle',
        source: 'ne-capitais',
        maxzoom: 10.5,
        paint: {
          'circle-color': '#fff3dc',
          'circle-radius': z(4.6, 2, 6, 3.4, 9, 4.2),
          'circle-stroke-color': 'rgba(255, 203, 125, 0.85)',
          'circle-stroke-width': z(4.6, 0, 6, 1),
          'circle-opacity': z(9.5, 1, 10.5, 0),
          'circle-stroke-opacity': z(9.5, 1, 10.5, 0),
          'circle-pitch-alignment': 'map',
        },
      },
      {
        id: 'ne-cap-nome',
        type: 'symbol',
        source: 'ne-capitais',
        minzoom: 4.6,
        maxzoom: 10.5,
        layout: {
          'text-field': ['get', 'nome'],
          'text-font': ['Noto Sans Regular'],
          'text-size': z(4.6, 12.5, 9, 15),
          'text-anchor': 'top',
          'text-offset': [0, 0.9],
          'text-letter-spacing': 0.02,
        },
        paint: { 'text-color': '#ffd9a0', ...halo, 'text-halo-color': 'rgba(0, 0, 0, 0.78)', 'text-opacity': z(4.6, 0, 5.2, 1) },
      },
    ],
    // luz so da atmosfera do globo (nao ha fill-extrusion): presa a tela, do mesmo lado do sol da
    // Terra 3D na troca, para a borda clara nao trocar de lado quando o mapa assume
    light: { anchor: 'viewport', position: [1.5, 50, 48] },
    // ceu transparente (as estrelas da cena 3D continuam atras) com uma faixa fina de horizonte
    sky: {
      'sky-color': 'rgba(0, 0, 0, 0)',
      'horizon-color': '#a9b8ca',
      'fog-color': '#a9b8ca',
      'sky-horizon-blend': 0.12,
      'horizon-fog-blend': 0.3,
      'fog-ground-blend': 0.94,
      'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 1, 5, 1, 8, 0],
    },
    terrain: { source: 'terreno', exaggeration: EXAGERO },
  };
}

export class Mapa {
  constructor(container) {
    this.container = container;
    this.mapa = null;
    this.marcador = null;
    this.alvo = null;
  }

  /** Cria o mapa assim que o MapLibre chegar; this.carregado resolve com o estilo e o Nordeste prontos. */
  _criar(centro, zoom) {
    this.carregado = carregarMaplibre().then(() => this._montar(centro, zoom));
    this.carregado.catch(() => { this.carregado = null; });   // a próxima viagem tenta de novo
    return this.carregado;
  }

  _montar(centro, zoom) {
    registrarWayback();
    this.mapa = new maplibregl.Map({
      container: this.container,
      style: estilo(),
      center: centro,
      zoom,
      pitch: 0,
      bearing: 0,
      maxPitch: 78,
      attributionControl: { compact: true },
      locale: TEXTOS,
    });
    // os créditos abertos cobriam a barra "Ver no mapa" e a escala no computador: ficam no botão "i" desde o começo
    this.mapa.once('load', () => this.container.querySelector('.maplibregl-ctrl-attrib')?.classList.remove('maplibregl-compact-show'));
    this.mapa.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'bottom-right');
    this.mapa.addControl(new maplibregl.TerrainControl({ source: 'terreno', exaggeration: EXAGERO }), 'bottom-right');
    const escala = new maplibregl.ScaleControl({ unit: 'metric' });
    this.mapa.addControl(escala, 'bottom-left');
    // com relevo, logo apos um salto de camera o unproject pode dar NaN e a escala fica "NaN m"
    // ate o proximo movimento: quando o mapa assenta, recalcula
    this.mapa.on('idle', () => {
      if (this.container.querySelector('.maplibregl-ctrl-scale')?.textContent.includes('NaN')) escala.setUnit('metric');
    });
    // camadas de dados (camadas.js): a aba Foto volta para a camera da chegada ao municipio
    this.camadas = new Camadas(this.mapa, { perto: () => this._lugar && this._alvo(this._lugar) });
    // so conta como carregado com o Nordeste ja desenhado: a troca precisa do fio no mesmo lugar do globo
    return Promise.all([new Promise((ok) => this.mapa.once('load', ok)), NORDESTE])
      .then(([, d]) => {
        if (d) this._nordeste(d);
        this.camadas.ligar();
      });
  }

  /** Contorno, divisas, mascara e capitais do Nordeste (static/data/nordeste.json, IBGE). */
  _nordeste(d) {
    const linha = (k) => (coordinates) => ({ type: 'Feature', properties: { k }, geometry: { type: 'LineString', coordinates } });
    this.mapa.getSource('ne').setData({
      type: 'FeatureCollection',
      features: [...d.contorno.map(linha('contorno')), ...d.divisas.map(linha('divisa'))],
    });
    this.mapa.getSource('ne-fora').setData(mundoMenos(d.contorno));
    this.mapa.getSource('ne-capitais').setData({
      type: 'FeatureCollection',
      features: (d.capitais || []).map(([nome, lat, lon]) => ({ type: 'Feature', properties: { nome }, geometry: { type: 'Point', coordinates: [lon, lat] } })),
    });
    // dentro da regiao, abaixo de z10, as divisas douradas substituem o tracejado branco
    const regiao = { type: 'Polygon', coordinates: d.contorno };
    this.mapa.setFilter('limites', ['step', ['zoom'], ['all', LIMITES, ['!', ['within', regiao]]], 10, LIMITES]);
  }

  /** Limite oficial do municipio (malha do IBGE), pelo codigo que o Nominatim devolve. */
  async _municipio(lugar) {
    const cod = String(lugar.ibge || '').slice(0, 7);   // distrito tem 9 digitos: os 7 primeiros sao o municipio
    this._codMun = cod;
    this.camadas.municipio(/^\d{7}$/.test(cod) ? cod : null);
    this.mapa.getSource('mun').setData(VAZIO);
    this.mapa.getSource('mun-fora').setData(VAZIO);
    if (!/^\d{7}$/.test(cod)) return;
    try {
      const r = await fetch(`${IBGE_MALHA}/${cod}?formato=application/vnd.geo%2Bjson&qualidade=intermediaria`);
      const g = (await r.json()).features[0].geometry;
      if (this._codMun !== cod) return;   // a pessoa ja foi para outro lugar
      const aneis = g.type === 'Polygon' ? [g.coordinates[0]] : g.coordinates.map((p) => p[0]);
      this.mapa.getSource('mun').setData({ type: 'Feature', properties: {}, geometry: { type: 'MultiLineString', coordinates: aneis } });
      this.mapa.getSource('mun-fora').setData(mundoMenos(aneis));
    } catch {
      // sem a malha o mapa segue normal, so sem o contorno do municipio
    }
  }

  /** Cria o mapa escondido enquanto a pessoa ainda esta no inicio, para a viagem nao esperar. */
  precarregar() {
    if (!this.carregado) this._criar([-40, -8], 3).catch(() => {});
  }

  /**
   * Posiciona o mapa escondido no ponto de troca e espera os ladrilhos (com limite).
   * Depois, enquanto a Terra 3D ainda viaja (`ate`), passa escondido pela vista final da chegada,
   * para os ladrilhos dela ja estarem no cache quando o voo do mapa terminar.
   */
  async preparar(lugar, zoom, { continuar = false, ate = null } = {}) {
    const centro = [lugar.lon, lugar.lat];
    const troca = { center: centro, zoom, pitch: 0, bearing: 0 };
    const naPrecarga = !!this.carregado && !this.mapa;   // a pré-carga ainda espera o MapLibre chegar
    if (!this.carregado) {
      this._criar(centro, zoom);
    } else if (this.mapa) {
      this.mapa.stop();
      this.mapa.jumpTo(troca);
    }
    await this.carregado;
    if (naPrecarga) this.mapa.jumpTo(troca);
    this._lugar = lugar;
    this.camadas.desligar();   // cada viagem chega na foto
    this._marcar(centro);
    this._municipio(lugar);
    await this._ocioso(2000);
    this.alvo = continuar ? null : this._alvo(lugar);
    if (this.alvo && ate) {
      this.mapa.jumpTo(this.alvo);
      await Promise.race([this._ocioso(2500), ate]);
      this.mapa.jumpTo(troca);
      await this._ocioso(1000);
    }
  }

  _ocioso(limite) {
    return Promise.race([new Promise((ok) => this.mapa.once('idle', ok)), esperar(limite)]);
  }

  /**
   * Camera final: o lugar inteiro em resolucao cheia, inclinada o bastante para mostrar o relevo.
   * Numa sede (cidade, distrito...) o bbox costuma ser o do municipio inteiro e a sede pode ficar na
   * ponta dele (Petrolina): centra no ponto da sede e usa o bbox so para o zoom.
   */
  _alvo(lugar) {
    let alvo = { center: [lugar.lon, lugar.lat], zoom: ZOOM_PONTO };
    if (lugar.bbox) {
      const [w, s, e, n] = lugar.bbox;
      const cam = this.mapa.cameraForBounds([[w, s], [e, n]], { padding: 80 });
      if (cam && ASSENTAMENTO.has(lugar.tipo)) alvo.zoom = limitar(cam.zoom + 0.5, 11, ZOOM_AREA_MAX);
      else if (cam) alvo = { center: cam.center, zoom: limitar(cam.zoom + 0.5, 3, ZOOM_AREA_MAX) };
    }
    return { ...alvo, pitch: alvo.zoom > 8 ? 50 : 30, bearing: -15 };
  }

  _marcar(centro) {
    if (!this.marcador) {
      const el = document.createElement('div');
      el.className = 'marcador';
      el.innerHTML = '<i></i><b></b>';
      this.marcador = new maplibregl.Marker({ element: el, anchor: 'center' });
      // "deitado no chao": com a camera inclinada o anel vira elipse, como um ponto do terreno.
      // O anel e simetrico, entao basta achatar a altura; o piso de 45% evita que vire um risco
      // (com pitchAlignment 'map' ele ficaria com 21% da altura em 78 graus)
      const achatar = () => el.style.setProperty('--achatar', Math.max(0.45, Math.cos((this.mapa.getPitch() * Math.PI) / 180)).toFixed(3));
      this.mapa.on('pitch', achatar);
      achatar();
    }
    this.marcador.setLngLat(centro).addTo(this.mapa);
  }

  /**
   * Voo final ate o lugar, inclinando a camera para mostrar o relevo.
   * Com `continuar` (a pessoa entrou girando a rodinha) so segue um pouco o zoom dela.
   */
  chegar(lugar, { continuar = false } = {}) {
    // creditos: recolhidos ao "i" desde o load; se o MapLibre os reabrir sozinho, fecham 10 s depois da
    // chegada, junto com a dica de uso; continuam a um clique
    clearTimeout(this._tCreditos);
    this._tCreditos = setTimeout(() => {
      this.container.querySelector('.maplibregl-ctrl-attrib')?.classList.remove('maplibregl-compact-show');
    }, 10000);
    if (continuar) {
      this.mapa.easeTo({ zoom: this.mapa.getZoom() + 2.2, pitch: 35, duration: 2000, essential: true });
      return;
    }
    this.mapa.flyTo({ ...(this.alvo || this._alvo(lugar)), duration: 5200, curve: 1.25, essential: true });
  }

  /**
   * Altitude do lugar (m) lida no modelo de relevo depois que a camera para.
   * null se o relevo estiver desligado ou a vista ainda estiver longe demais para ser precisa.
   */
  async altitude(lugar) {
    await new Promise((ok) => this.mapa.once('moveend', ok));
    await this._ocioso(4000);
    const terreno = this.mapa.getTerrain();
    if (!terreno || this.mapa.getZoom() < 9) return null;
    const h = this.mapa.queryTerrainElevation([lugar.lon, lugar.lat]);   // ja vem multiplicada pelo exagero
    return h == null ? null : h / terreno.exaggeration;
  }

  /**
   * Sobe ate a vista de globo equivalente a Terra 3D e devolve centro e zoom finais.
   * Se a pessoa ja afastou o zoom alem disso, so endireita a camera (sem voltar a aproximar).
   */
  async subir(zoomDe) {
    const c = this.mapa.getCenter();
    const zoom = Math.min(this.mapa.getZoom(), zoomDe(c.lat));
    this.mapa.stop();
    this.camadas.desligar();   // o globo 3D nao tem as cores: sobe so com a foto
    const longe = this.mapa.getZoom() - zoom > 0.05;
    this.mapa.flyTo({
      center: c, zoom, pitch: 0, bearing: 0, duration: longe ? 1900 : 700, curve: 1.2, essential: true,
    });
    await Promise.race([new Promise((ok) => this.mapa.once('moveend', ok)), esperar(longe ? 2300 : 1000)]);
    return { lat: c.lat, lon: c.lng, zoom };
  }

  /** fn(zoom, foiAPessoa): avisa a cada mudanca de zoom. */
  aoZoom(fn) {
    this.mapa.on('zoom', (e) => fn(this.mapa.getZoom(), !!e.originalEvent));
  }
}
