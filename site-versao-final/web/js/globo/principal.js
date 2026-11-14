// Origem: João Pedro (branch estudo-jp, 29f81f6), site-nasa/static/js/principal.js; adaptado para o site final:
// busca local nos 1.794 municípios do Nordeste (busca.js) no lugar de /api/geocode (Nominatim pelo Flask), e o
// clique no globo acha o município na malha local no lugar de /api/reverse; sai unicos() (juntava repetidos do
// Nominatim); nordeste.json por caminho relativo; botão "Montar o plano do meu roçado" no cartão do mapa
// (roca.html#/<cod>/1), visível na chegada até o painel do iframe avisar que desenhou.
// principal.js - liga a interface: busca de lugar, viagem do globo 3D ate o mapa e volta.
import { Espaco, DIST_TROCA } from './espaco.js';
import { Mapa, zoomEquivalente, distEquivalente } from './mapa.js';
import { Painel } from './painel.js';
import { Ovos } from './ovos.js';
import { dentroDoNordeste, passoKonami, KONAMI } from './util.js';
import { procurar, municipioNoPonto, UF_NOME } from './busca.js';

const $ = (id) => document.getElementById(id);
const esperar = (ms) => new Promise((ok) => setTimeout(ok, ms));
const corpo = document.body;

const ui = {
  form: $('busca'),
  campo: $('buscaCampo'),
  botao: $('buscaBotao'),
  lista: $('sugestoes'),
  msg: $('buscaMsg'),
  mira: $('mira'),
  miraTexto: $('miraTexto'),
  telLat: $('telLat'),
  telLon: $('telLon'),
  telAlt: $('telAlt'),
  telUtc: $('telUtc'),
  etapa: $('viagemEtapa'),
  destino: $('viagemDestino'),
  nome: $('localNome'),
  detalhe: $('localDetalhe'),
  coords: $('localCoords'),
  alt: $('localAlt'),
  dicaMapa: $('dicaMapa'),
  voltar: $('voltar'),
  carga: $('cargaBarra'),
  hero: $('hero'),
  mergulho: $('mergulho'),
  plano: $('planoBotao'),
};

// ------------------------------------------------------------------ formatos

function grau(v, pos, neg) {
  return `${Math.abs(v).toFixed(2).replace('.', ',')}° ${v >= 0 ? pos : neg}`;
}
const fmtLat = (lat) => grau(lat, 'N', 'S');
const fmtLon = (lon) => grau(lon, 'L', 'O');
const fmtCoord = (lat, lon) => `${fmtLat(lat)} · ${fmtLon(lon)}`;

// ------------------------------------------------------------------ cena

let estado = 'inicio';   // inicio | viajando | mapa | voltando

const espaco = new Espaco($('espaco'), {
  aoProgresso: (f) => ui.carga.style.setProperty('--p', f),
  aoPairar: (p, x, y) => {
    if (!p) {
      ui.mira.classList.remove('visivel');
      return;
    }
    ui.mira.classList.add('visivel');
    ui.mira.style.transform = `translate(${x + 20}px, ${y + 18}px)`;
    ui.miraTexto.textContent = fmtCoord(p.lat, p.lon);
  },
  aoClicar: (lat, lon) => {
    if (estado !== 'inicio') return;
    if (!noNordeste(lat, lon)) { foraDoNordeste(); return; }
    viajar(pontoNoGlobo(lat, lon));
  },
  // mergulho com a rodinha/pinca: o cartao some aos poucos e a barra mostra quanto falta
  aoAproximar: (a) => {
    if (estado !== 'inicio') return;
    corpo.classList.toggle('mergulhando', a > 0.01);
    if (a <= 0.01) {
      ui.hero.removeAttribute('style');
      return;
    }
    ui.hero.style.opacity = String(Math.max(0, 1 - a * 3));
    ui.hero.style.transform = `scale(${1 - a * 0.08})`;
    ui.hero.style.filter = `blur(${(a * 10).toFixed(1)}px)`;
    ui.hero.style.pointerEvents = a > 0.25 ? 'none' : '';
    ui.mergulho.style.setProperty('--a', a.toFixed(3));
  },
  aoEntrar: (lat, lon) => viajar(pontoNoGlobo(lat, lon), { continuar: true }),
});
const mapa = new Mapa($('mapa'));
const painel = new Painel($('painel'));
// botao do plano no cartao do mapa: entra com o municipio e sai quando o painel do iframe desenha (painel.css)
painel.aoMudar = (cod) => {
  ui.plano.hidden = !cod;
  if (cod) ui.plano.href = `roca.html#/${cod}/1`;
};
// o mapa encolhe para um cartao a esquerda quando o painel abre: o MapLibre precisa saber do novo tamanho
new ResizeObserver(() => mapa.mapa?.resize()).observe($('mapa'));

// ------------------------------------------------------------------ easter eggs (ovos.js)

const ovo = { caixa: $('ovo'), texto: $('ovoTexto'), tempo: 0 };
function aviso(texto) {
  ovo.texto.textContent = texto;
  ovo.caixa.classList.add('visivel');
  clearTimeout(ovo.tempo);
  ovo.tempo = setTimeout(() => ovo.caixa.classList.remove('visivel'), 6500);
}
const ovos = new Ovos(espaco, { aviso });
function lancarFoguete() {
  if (estado !== 'inicio') return;
  ovos.lancar();
  aviso('3, 2, 1… Decolagem de Alcântara (MA), a base de foguetes do Brasil, a 2° do equador.');
}
// codigo Konami: cima cima baixo baixo esquerda direita esquerda direita B A
let konami = 0;
window.addEventListener('keydown', (e) => {
  konami = passoKonami(konami, e.key);
  if (konami === KONAMI.length) { konami = 0; lancarFoguete(); }
});

// ------------------------------------------------------------------ so o Nordeste

// O QUADRA so desce no Nordeste: busca, coordenada, clique no globo, atalho e mergulho com a rodinha.
// Contorno do IBGE (dados/nordeste.json); se ele nao carregar, a pagina nao trava ninguem.
let contornoNE = null;
fetch(new URL('../../dados/nordeste.json', import.meta.url)).then((r) => r.json()).then((d) => { contornoNE = d.contorno; }).catch(() => {});
const noNordeste = (lat, lon) => !contornoNE || dentroDoNordeste(lat, lon, contornoNE);
let avisoForaEm = 0;
function foraDoNordeste() {
  if (performance.now() - avisoForaEm < 1500) return;   // a rodinha dispara muitas vezes seguidas
  avisoForaEm = performance.now();
  mensagem('Esse lugar fica fora do Nordeste. Por enquanto o QUADRA só desce lá.', true);
  balancar();
}
espaco.podeMergulhar = (lat, lon) => {
  if (noNordeste(lat, lon)) return true;
  foraDoNordeste();
  return false;
};

/** Lugar a partir de um ponto do globo; o municipio chega da malha local enquanto o planeta gira. */
function pontoNoGlobo(lat, lon, origem = 'Ponto escolhido no globo') {
  const lugar = { nome: fmtCoord(lat, lon), detalhe: origem, lat, lon, bbox: null };
  municipioNoPonto(lat, lon)
    .then((m) => {
      if (!m) return;
      lugar.nome = m.nome;
      lugar.detalhe = `${UF_NOME[m.uf]} · IBGE ${m.cod} · ${origem.toLowerCase()}`;
      lugar.ibge = m.cod;
      if (atual === lugar) painel.mostrar(lugar);
      if (estado === 'viajando' || estado === 'mapa') {
        ui.destino.textContent = lugar.nome;
        preencherCartao(lugar);
      }
    })
    .catch(() => {});
  return lugar;
}

// para depurar no console (e nas capturas automaticas)
window.quadra = { espaco, mapa, ovos };

// ------------------------------------------------------------------ telemetria

// ponto sob a camera, altitude e hora UTC, como num painel de orbita
const fmtKm = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });
let ultimaTel = 0;
function telemetria(agora) {
  requestAnimationFrame(telemetria);
  if (agora - ultimaTel < 100 || estado === 'mapa') return;
  ultimaTel = agora;
  const n = espaco.nadir();
  ui.telLat.textContent = fmtLat(n.lat);
  ui.telLon.textContent = fmtLon(n.lon);
  ui.telAlt.textContent = `${fmtKm.format(espaco.altitudeKm())} km`;
}
function relogio() {
  ui.telUtc.textContent = new Date().toISOString().slice(11, 19);
}
relogio();
setInterval(relogio, 1000);

// ------------------------------------------------------------------ pensamento (canto inferior esquerdo)

const PENSAMENTOS = [
  { texto: 'O sertanejo é, antes de tudo, um forte.', autor: 'Euclides da Cunha', obra: 'Os Sertões' },
  {
    texto: 'O otimista é um tolo. O pessimista, um chato. Bom mesmo é ser um realista esperançoso.',
    autor: 'Ariano Suassuna',
    obra: 'paraibano, dramaturgo',
  },
  { texto: 'O sertão é do tamanho do mundo.', autor: 'João Guimarães Rosa', obra: 'Grande Sertão: Veredas' },
];
const pensamento = { caixa: $('pensamento'), texto: $('pensamentoTexto'), autor: $('pensamentoAutor'), i: 0 };
setInterval(() => {
  if (estado !== 'inicio' || corpo.classList.contains('mergulhando')) return;
  pensamento.caixa.classList.add('trocando');
  setTimeout(() => {
    pensamento.i = (pensamento.i + 1) % PENSAMENTOS.length;
    const p = PENSAMENTOS[pensamento.i];
    pensamento.texto.textContent = p.texto;
    pensamento.autor.textContent = `${p.autor} · `;
    const cite = document.createElement('cite');
    cite.textContent = p.obra;
    pensamento.autor.appendChild(cite);
    pensamento.caixa.classList.remove('trocando');
  }, 1500);
}, 18000);

// atalhos: "/" leva para a busca; no computador o campo ja comeca focado
window.addEventListener('keydown', (e) => {
  if (e.key === '/' && estado === 'inicio' && document.activeElement !== ui.campo) {
    e.preventDefault();
    ui.campo.focus();
  }
});

espaco.pronto.then(async () => {
  corpo.classList.remove('carregando');
  espaco.iniciar();
  requestAnimationFrame(telemetria);
  setTimeout(() => mapa.precarregar(), 1200);
  // o campo so ganha foco depois que o titulo aparece (sem atrapalhar a abertura)
  if (matchMedia('(hover: hover)').matches) setTimeout(() => ui.campo.focus({ preventScroll: true }), 3600);
  const pedido = new URLSearchParams(location.search).get('lugar');
  if (pedido) {
    await esperar(4500);   // deixa a abertura terminar antes de viajar
    ui.campo.value = pedido;
    buscar(pedido, { primeiro: true });
  }
});

// ------------------------------------------------------------------ busca

let resultados = [];
let ativo = -1;

function mensagem(texto, erro = false) {
  ui.msg.textContent = texto;
  ui.msg.classList.toggle('erro', erro);
}

function balancar() {
  ui.form.classList.remove('balanca');
  void ui.form.offsetWidth;
  ui.form.classList.add('balanca');
}

function fecharLista() {
  ui.lista.hidden = true;
  ui.lista.innerHTML = '';
  ui.campo.removeAttribute('aria-activedescendant');
  resultados = [];
  ativo = -1;
}

function marcarAtivo(i) {
  ativo = i;
  [...ui.lista.children].forEach((li, k) => li.setAttribute('aria-selected', String(k === i)));
  if (i >= 0) ui.campo.setAttribute('aria-activedescendant', `sug-${i}`);
}

function mostrarLista(lista) {
  resultados = lista;
  ui.lista.innerHTML = '';
  lista.forEach((l, i) => {
    const li = document.createElement('li');
    li.id = `sug-${i}`;
    li.setAttribute('role', 'option');
    li.innerHTML = '<span class="sug-pino" aria-hidden="true"></span><span class="sug-texto"><b></b><small></small></span><span class="sug-coord"></span>';
    li.querySelector('b').textContent = l.nome;
    li.querySelector('small').textContent = semCep(l.detalhe);
    li.querySelector('.sug-coord').textContent = fmtCoord(l.lat, l.lon);
    li.addEventListener('pointerdown', (e) => { e.preventDefault(); viajar(l); });
    li.addEventListener('pointerenter', () => marcarAtivo(i));
    ui.lista.appendChild(li);
  });
  ui.lista.hidden = false;
  marcarAtivo(0);
  mensagem(`${lista.length} municípios com esse nome. Escolha um.`);
}

// busca local (busca.js): os 1.794 municipios do Nordeste ou uma coordenada; nada sai para a internet
async function buscar(texto, { primeiro = false } = {}) {
  if (!texto) {
    mensagem('Digite um município para começar.', true);
    balancar();
    return;
  }
  ui.form.classList.add('ocupado');
  mensagem('Procurando no Nordeste…');
  try {
    const lista = await procurar(texto);
    if (lista[0]?.tipo === 'coordenada') {
      const c = lista[0];
      if (noNordeste(c.lat, c.lon)) viajar(pontoNoGlobo(c.lat, c.lon, 'Coordenada informada'));
      else { mensagem('Esse lugar fica fora do Nordeste. Por enquanto o QUADRA só desce lá.', true); balancar(); }
      return;
    }
    if (!lista.length) {
      mensagem('Não achei esse município no Nordeste. Tente o nome e o estado (Quixadá, CE) ou coordenadas como -4.97, -39.01.', true);
      balancar();
      return;
    }
    // vai direto so com um nome exato (ou pelo atalho / ?lugar=); parecidos ("São Paulo" -> "São Paulo do Potengi") pedem escolha
    const exatos = lista.filter((l) => l.exato);
    if (primeiro || exatos.length === 1) viajar(exatos[0] || lista[0]);
    else {
      mostrarLista(lista.slice(0, 5));
      if (!exatos.length) mensagem('Nenhum município do Nordeste tem esse nome exato. É algum destes?');
    }
  } catch (err) {
    mensagem(err.message || 'A busca falhou.', true);
    balancar();
  } finally {
    ui.form.classList.remove('ocupado');
  }
}

ui.form.addEventListener('submit', (e) => {
  e.preventDefault();
  if (estado !== 'inicio') return;
  if (ui.campo.value.trim().toLowerCase() === 'foguete') { ui.campo.value = ''; lancarFoguete(); return; }
  if (resultados.length && ativo >= 0) { viajar(resultados[ativo]); return; }
  buscar(ui.campo.value.trim());
});

ui.campo.addEventListener('keydown', (e) => {
  if (!resultados.length) return;
  if (e.key === 'ArrowDown') { e.preventDefault(); marcarAtivo((ativo + 1) % resultados.length); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); marcarAtivo((ativo - 1 + resultados.length) % resultados.length); }
  else if (e.key === 'Escape') { fecharLista(); mensagem(''); }
});
ui.campo.addEventListener('input', () => { if (resultados.length) fecharLista(); mensagem(''); });
ui.campo.addEventListener('blur', () => setTimeout(fecharLista, 150));

document.querySelectorAll('[data-lugar]').forEach((b) => {
  b.addEventListener('click', () => {
    if (estado !== 'inicio') return;
    ui.campo.value = b.dataset.lugar;
    buscar(b.dataset.lugar, { primeiro: true });
  });
});

// ------------------------------------------------------------------ viagem

function etapa(texto) { ui.etapa.textContent = texto; }

// o Nominatim poe o CEP no meio do endereco ("..., 65195-000, Brasil"): no cartao ele so atrapalha
const semCep = (texto) => texto.split(', ').filter((p) => !/^\d{5}(-?\d{3})?$/.test(p)).join(', ');

function preencherCartao(lugar) {
  ui.nome.textContent = lugar.nome;
  ui.detalhe.textContent = semCep(lugar.detalhe);
  ui.coords.textContent = fmtCoord(lugar.lat, lugar.lon);
}

// AWS Terrain Tiles: nos EUA o relevo vem do USGS 3DEP; no resto da faixa 56° S–60° N, do SRTM da NASA
function fonteRelevo({ lat, lon }) {
  if (lat > 24 && lat < 50 && lon > -125 && lon < -66) return 'USGS 3DEP';
  return lat > -56 && lat < 60 ? 'NASA SRTM' : 'AWS Terrain Tiles';
}

// dica de uso do mapa: aparece na chegada e some no primeiro gesto (ou sozinha depois de 10 s)
let dicaTempo = 0;
function dicaMapa(mostrar) {
  clearTimeout(dicaTempo);
  ui.dicaMapa.classList.toggle('visivel', mostrar);
  if (mostrar) dicaTempo = setTimeout(() => dicaMapa(false), 10000);
}
$('mapa').addEventListener('pointerdown', () => dicaMapa(false));
$('mapa').addEventListener('wheel', () => dicaMapa(false), { passive: true });

let atual = null;   // lugar da viagem em curso (a altitude chega depois e precisa conferir)

/** @param continuar a pessoa entrou girando a rodinha: o mapa so segue o zoom dela */
async function viajar(lugar, { continuar = false } = {}) {
  if (estado !== 'inicio') return;
  if (!noNordeste(lugar.lat, lugar.lon)) { foraDoNordeste(); return; }
  estado = 'viajando';
  atual = lugar;
  fecharLista();
  mensagem('');
  ui.campo.blur();
  ui.hero.removeAttribute('style');
  corpo.classList.remove('mergulhando');
  preencherCartao(lugar);
  painel.mostrar(lugar);   // municipio do Nordeste: o mapa encolhe para a esquerda e o painel abre a direita
  ui.alt.hidden = true;
  ui.destino.textContent = lugar.nome;
  etapa(continuar ? 'Entrando no mapa' : 'Alinhando a órbita');
  corpo.classList.add('em-viagem');

  const zoomTroca = zoomEquivalente(lugar.lat, DIST_TROCA);
  const voo = espaco.viajar(lugar.lat, lugar.lon);
  const preparo = mapa.preparar(lugar, zoomTroca, { continuar, ate: voo });
  const t1 = setTimeout(() => etapa('Descendo sobre o destino'), 1300);
  await voo;
  clearTimeout(t1);
  etapa('Sintonizando o satélite');
  await preparo;
  vigiarZoom();

  // troca: o mapa (globo do MapLibre) aparece por cima da Terra 3D no mesmo enquadramento
  corpo.classList.add('no-mapa');
  await esperar(900);
  espaco.mostrarTerra(false);
  mapa.chegar(lugar, { continuar });
  mapa.altitude(lugar).then((m) => {
    if (atual !== lugar || estado !== 'mapa' || m == null || m < 0) return;
    ui.alt.textContent = `Altitude ${fmtKm.format(m)} m · ${fonteRelevo(lugar)}`;
    ui.alt.hidden = false;
  });
  etapa('Chegando');
  await esperar(500);
  corpo.classList.remove('em-viagem');
  estado = 'mapa';
  dicaMapa(true);
}

async function voltar() {
  if (estado !== 'mapa') return;
  estado = 'voltando';
  dicaMapa(false);
  etapa('Subindo para a órbita');
  ui.destino.textContent = '';
  corpo.classList.add('em-viagem');
  if (corpo.classList.contains('com-lado')) await esperar(850);   // o mapa volta a ocupar a tela antes de subir
  espaco.retomar();
  const c = await mapa.subir((lat) => zoomEquivalente(lat, DIST_TROCA));
  espaco.posicionarNoCentro(c.lat, c.lon, distEquivalente(c.lat, c.zoom));
  corpo.classList.remove('no-mapa');
  await esperar(900);
  await espaco.voltar(c.lat, c.lon);
  corpo.classList.remove('em-viagem');
  painel.esconder();
  estado = 'inicio';
}

ui.voltar.addEventListener('click', voltar);
window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && estado === 'mapa') voltar(); });

// Zoom no mapa: perto do chao o ceu fica coberto e a cena 3D pausa (poupa a GPU);
// se a pessoa afastar ate ver o planeta inteiro, volta sozinha para o espaco.
let zoomLigado = false;
function vigiarZoom() {
  if (zoomLigado) return;
  zoomLigado = true;
  mapa.aoZoom((z, foiAPessoa) => {
    if (estado !== 'mapa') return;
    if (z > 5.5) espaco.pausar();
    else espaco.retomar();
    const lat = mapa.mapa.getCenter().lat;
    if (foiAPessoa && z < zoomEquivalente(lat, DIST_TROCA) - 0.35) voltar();
  });
}
