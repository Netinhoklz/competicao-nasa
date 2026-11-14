// mapa.js - mapa interativo (MapLibre GL, projecao de globo): imagem Sentinel-2 sem nuvens,
// detalhe Maxar ao aproximar, relevo 3D, rotulos vetoriais em portugues e o marcador do lugar.

const S2 = 'https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2024_3857/default/g/{z}/{y}/{x}.jpg';
const ESRI_IMAGEM = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
const TERRENO = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
const EXAGERO = 1.5;
const ZOOM_PONTO = 12.3;   // zoom de chegada quando o lugar e um ponto (clique ou coordenada)
const ZOOM_AREA_MAX = 12.5; // teto do zoom de chegada para cidades e regioes (bbox)

const CREDITO_S2 = '<a href="https://s2maps.eu" target="_blank">Sentinel-2 cloudless 2024</a> © EOX IT Services GmbH '
  + '(dados Copernicus Sentinel modificados, '
  + '<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br" target="_blank">CC BY-NC-SA 4.0</a>)';
const CREDITO_OFM = '<a href="https://openfreemap.org" target="_blank">OpenFreeMap</a> '
  + '<a href="https://www.openmaptiles.org/" target="_blank">© OpenMapTiles</a> '
  + '<a href="https://www.openstreetmap.org/copyright" target="_blank">© colaboradores do OpenStreetMap</a>';

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
      // detalhe Maxar so de z12 em diante: abaixo disso o Esri usa outro mosaico (verde) e faz costura;
      // z17 e o ultimo nivel com imagem no sertao (z18 devolve "Map data not yet available")
      detalhe: {
        type: 'raster',
        tiles: [ESRI_IMAGEM],
        tileSize: 256,
        minzoom: 12,
        maxzoom: 17,
        attribution: 'Detalhe: © Esri, Maxar, Earthstar Geographics',
      },
      ofm: { type: 'vector', url: 'https://tiles.openfreemap.org/planet', attribution: CREDITO_OFM },
      terreno: dem,
      sombra: { ...dem },
    },
    layers: [
      { id: 'base', type: 'raster', source: 'base', paint: tomS2 },
      { id: 's2', type: 'raster', source: 's2', paint: { ...tomS2, 'raster-fade-duration': 250 } },
      {
        id: 'detalhe',
        type: 'raster',
        source: 'detalhe',
        minzoom: 13.5,
        paint: {
          'raster-fade-duration': 250,
          'raster-opacity': ['interpolate', ['linear'], ['zoom'], 13.5, 0, 14.5, 1],
        },
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
      {
        id: 'limites',
        type: 'line',
        source: 'ofm',
        'source-layer': 'boundary',
        minzoom: 4.6,
        filter: ['all',
          ['<=', ['coalesce', ['get', 'admin_level'], 99], 4],
          ['!=', ['coalesce', ['get', 'maritime'], 0], 1]],
        paint: {
          'line-color': 'rgba(255, 255, 255, 0.45)',
          'line-width': ['interpolate', ['linear'], ['zoom'], 3, 0.6, 10, 1.1],
          'line-dasharray': [3, 2],
          'line-opacity': surgir,
        },
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
    ],
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

  _criar(centro, zoom) {
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
    this.mapa.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'bottom-right');
    this.mapa.addControl(new maplibregl.TerrainControl({ source: 'terreno', exaggeration: EXAGERO }), 'bottom-right');
    this.mapa.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');
    this.carregado = new Promise((ok) => this.mapa.once('load', ok));
  }

  /** Cria o mapa escondido enquanto a pessoa ainda esta no inicio, para a viagem nao esperar. */
  precarregar() {
    if (!this.mapa) this._criar([-40, -8], 3);
  }

  /**
   * Posiciona o mapa escondido no ponto de troca e espera os ladrilhos (com limite).
   * Depois, enquanto a Terra 3D ainda viaja (`ate`), passa escondido pela vista final da chegada,
   * para os ladrilhos dela ja estarem no cache quando o voo do mapa terminar.
   */
  async preparar(lugar, zoom, { continuar = false, ate = null } = {}) {
    const centro = [lugar.lon, lugar.lat];
    const troca = { center: centro, zoom, pitch: 0, bearing: 0 };
    if (!this.mapa) {
      this._criar(centro, zoom);
    } else {
      this.mapa.stop();
      this.mapa.jumpTo(troca);
    }
    await this.carregado;
    this._marcar(centro);
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

  /** Camera final: o lugar inteiro em resolucao cheia, inclinada o bastante para mostrar o relevo. */
  _alvo(lugar) {
    let alvo = { center: [lugar.lon, lugar.lat], zoom: ZOOM_PONTO };
    if (lugar.bbox) {
      const [w, s, e, n] = lugar.bbox;
      const cam = this.mapa.cameraForBounds([[w, s], [e, n]], { padding: 80 });
      if (cam) alvo = { center: cam.center, zoom: limitar(cam.zoom + 0.5, 3, ZOOM_AREA_MAX) };
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
