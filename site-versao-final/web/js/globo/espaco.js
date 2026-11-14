// Origem: João Pedro (branch estudo-jp, 29f81f6), site-nasa/static/js/espaco.js; adaptado para o site final: texturas e nordeste.json por caminho relativo ao módulo (../../texturas/, ../../dados/), sem /static do Flask; three.js local (vendor/, via importmap do index.html).
// espaco.js - cena 3D do inicio: Terra (dia/noite, oceano, nuvens), atmosfera, ceu estrelado,
// mira do cursor, mergulho com zoom e a viagem ate um lugar. Visual sobrio: a imagem da NASA
// e a protagonista; nada de brilho artificial.
import * as THREE from 'three';

const GRAU = Math.PI / 180;
const DIR_TEX = new URL('../../texturas/', import.meta.url).href;   // relativo ao modulo (site estatico)

export const FOV = 36.87;        // mesmo campo de visao padrao do MapLibre: a troca globo -> mapa casa
export const DIST_TROCA = 2.1;   // distancia camera-centro (em raios) em que o mapa assume

const EIXO = -23.4 * GRAU;       // inclinacao do eixo (o polo norte pende para o centro da tela)
const RAIO_NUVENS = 1.008;
const RAIO_ATMO = 1.16;
const RAIO_MARCAS = 1.012;       // mira e marcador ficam acima das nuvens
// Nordeste: o planeta fica olhando para a regiao (balanca devagar em vez de dar voltas)
const FOCO_NE = { lat: -8.5, lon: -40.5 };
const GIRO_NE = -(FOCO_NE.lon + 90) * GRAU;
// a regiao fica perto da borda de cima do disco: vista de lado, a cortina de luz sobe contra o ceu
const INCL_NE = (FOCO_NE.lat - 34) * GRAU;
const ALTURA_CORTINA = 0.05;     // em raios terrestres (exagerada, como toda a cena)
const CAPITAIS_NE = [
  ['São Luís', -2.53, -44.3], ['Teresina', -5.09, -42.8], ['Fortaleza', -3.73, -38.52],
  ['Natal', -5.79, -35.21], ['João Pessoa', -7.12, -34.86], ['Recife', -8.05, -34.9],
  ['Maceió', -9.67, -35.74], ['Aracaju', -10.91, -37.07], ['Salvador', -12.97, -38.5],
];
const RAIO_LINHAS = 1.0095;      // contorno e capitais ficam acima das nuvens
// Lua ao fundo: textura Solar System Scope (dados LRO/NASA); tamanho e distancia artisticos
// A Lua orbita devagar: uma elipse na tela em volta da Terra que passa exatamente pelo Sol, entao a
// cada volta ha um eclipse. Ela se esconde atras da Terra do lado esquerdo e fica mais perto (maior)
// na parte de baixo da orbita.
const DIST_LUA = 45;
const RAIO_LUA = 1.3;
const PERIODO_LUA = 150;         // s por volta
const PRIMEIRO_ECLIPSE = 32;     // s depois de a pagina abrir
const ORBITA_LUA_RY = { paisagem: 0.42, retrato: 0.3 };   // raio vertical da elipse, em alturas de tela
// Abertura: o sol comeca escondido atras da Terra (eclipse: so as luzes das cidades), rompe pela
// borda e desliza ate o alto a direita da tela, iluminando um crescente da Terra (a direcao
// final e calculada a partir do enquadramento: _solDoEnquadramento). Na viagem ele segue ate
// ficar de frente para o destino, para a troca com o mapa (imagem diurna) casar.
const SOL_NOITE = new THREE.Vector3(-0.2, 0.3, -0.95).normalize();
const SOL_DESTINO = new THREE.Vector3(0.5, 0.32, 0.8).normalize();
const ALVO_SOL = { paisagem: { x: 0.84, y: 0.2 }, retrato: { x: 0.86, y: 0.07 } };   // fracao da tela
const DIST_SOL = 1500;           // o sol e um painel distante sempre de frente para a camera
const MEIO_CAMPO_SOL = 40 * GRAU;
const RAIO_SOL = 0.6 * GRAU;     // raio aparente do disco (artistico; o real e 0,27 grau)
const RAIO_TERRA_KM = 6371;

const EX = new THREE.Vector3(1, 0, 0);
const EY = new THREE.Vector3(0, 1, 0);
const EZ = new THREE.Vector3(0, 0, 1);

const suave = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const saida = (t) => 1 - Math.pow(1 - t, 4);
const lerp = (a, b, t) => a + (b - a) * t;
const limitar = (v, a, b) => Math.min(b, Math.max(a, v));

/** Ponto na esfera unitaria no mesmo sistema de UV da SphereGeometry (u=0 em lon -180). */
export function latLonParaVetor(lat, lon, r = 1) {
  const phi = (lon + 180) * GRAU;
  const theta = (90 - lat) * GRAU;
  return new THREE.Vector3(
    -Math.cos(phi) * Math.sin(theta) * r,
    Math.cos(theta) * r,
    Math.sin(phi) * Math.sin(theta) * r,
  );
}

// ---------------------------------------------------------------- shaders

// base local (normal, leste, norte) em coordenadas de mundo, para o mapa de normais
const TERRA_VERT = /* glsl */ `
varying vec2 vUv;
varying vec3 vMundo;
varying vec3 vN;
varying vec3 vLeste;
varying vec3 vNorte;
void main() {
  vUv = uv;
  vec3 nObj = normalize(position);
  vec3 leste = normalize(cross(vec3(0.0, 1.0, 0.0), nObj) + vec3(0.0, 0.0, 1e-4));
  mat3 rot = mat3(modelMatrix);
  vN = rot * nObj;
  vLeste = rot * leste;
  vNorte = rot * cross(nObj, leste);
  vec4 m = modelMatrix * vec4(position, 1.0);
  vMundo = m.xyz;
  gl_Position = projectionMatrix * viewMatrix * m;
}`;

const TERRA_FRAG = /* glsl */ `
uniform sampler2D mapaDia;
uniform sampler2D mapaNoite;
uniform sampler2D mapaOceano;
uniform sampler2D mapaNormal;
uniform sampler2D mapaNuvens;
uniform vec3 sol;
uniform float desvioNuvens;
uniform sampler2D mapaNordeste;   // mascara suave da regiao, recortada no retangulo caixaNordeste
uniform vec4 caixaNordeste;       // lonMin, latMin, lonMax, latMax
uniform float destaque;           // 0..1: entra depois da abertura
varying vec2 vUv;
varying vec3 vMundo;
varying vec3 vN;
varying vec3 vLeste;
varying vec3 vNorte;

void main() {
  vec3 N = normalize(vN);
  vec3 tn = texture2D(mapaNormal, vUv).xyz * 2.0 - 1.0;
  vec3 Np = normalize(normalize(vLeste) * tn.x * 0.8 + normalize(vNorte) * tn.y * 0.8 + N * tn.z);
  vec3 V = normalize(cameraPosition - vMundo);
  vec3 L = normalize(sol);

  float oceano = texture2D(mapaOceano, vUv).r;
  vec3 dia = texture2D(mapaDia, vUv).rgb;
  dia = mix(dia, dia * 0.55 + vec3(0.004, 0.03, 0.085), oceano * 0.85);

  float NL = dot(N, L);
  float difusa = max(dot(Np, L), 0.0);
  float diaAmt = smoothstep(-0.10, 0.25, NL);

  float nuvem = smoothstep(0.12, 0.9, texture2D(mapaNuvens, vec2(vUv.x + desvioNuvens, vUv.y)).r);
  vec3 cor = dia * difusa * 1.45 * (1.0 - 0.5 * nuvem);

  // reflexo do sol no mar (discreto)
  vec3 H = normalize(L + V);
  float NH = max(dot(N, H), 0.0);
  cor += vec3(1.0, 0.95, 0.88) * (pow(NH, 300.0) * 0.3 + pow(NH, 30.0) * 0.035) * oceano * (1.0 - nuvem) * diaAmt;

  // luzes das cidades no lado da noite (VIIRS Black Marble)
  vec3 noite = texture2D(mapaNoite, vUv).rgb;
  float luzes = smoothstep(0.05, 0.45, dot(noite, vec3(0.2126, 0.7152, 0.0722)));
  // no Nordeste as luzes ficam mais quentes e mais fortes, com um veu dourado fraco por cima
  vec2 uvNE = vec2(
    (vUv.x * 360.0 - 180.0 - caixaNordeste.x) / (caixaNordeste.z - caixaNordeste.x),
    (vUv.y * 180.0 - 90.0 - caixaNordeste.y) / (caixaNordeste.w - caixaNordeste.y));
  float ne = texture2D(mapaNordeste, clamp(uvNE, 0.0, 1.0)).r * destaque;
  vec3 tomLuz = mix(vec3(1.0, 0.72, 0.42), vec3(1.0, 0.6, 0.26), ne);
  vec3 cidades = tomLuz * luzes * (1.5 + 1.4 * ne) * (1.0 - 0.75 * nuvem);
  cor += (cidades + vec3(0.001, 0.002, 0.005) + vec3(1.0, 0.58, 0.2) * ne * 0.016) * (1.0 - diaAmt);

  // borda azul fina da atmosfera vista por dentro do disco; contra o sol ela acende
  // (espalhamento para a frente, como nas fotos de orbita com o sol atras da Terra)
  float fres = pow(1.0 - max(dot(N, V), 0.0), 3.0);
  float contraLuz = pow(max(dot(-V, L), 0.0), 3.0);
  cor += vec3(0.3, 0.58, 1.0) * fres * (0.04 + 0.7 * smoothstep(-0.3, 0.5, NL) + 0.9 * contraLuz);

  gl_FragColor = vec4(cor, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

const NUVENS_VERT = /* glsl */ `
varying vec2 vUv;
varying vec3 vN;
void main() {
  vUv = uv;
  vN = normalize(mat3(modelMatrix) * normal);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;

const NUVENS_FRAG = /* glsl */ `
uniform sampler2D mapaNuvens;
uniform vec3 sol;
varying vec2 vUv;
varying vec3 vN;
void main() {
  float a = smoothstep(0.12, 0.9, texture2D(mapaNuvens, vUv).r);
  float nl = dot(normalize(vN), normalize(sol));
  float luz = smoothstep(-0.12, 0.35, nl);
  vec3 cor = mix(vec3(0.012, 0.015, 0.025), vec3(0.97), luz);
  // nuvens no terminador pegam a luz rasante do por do sol
  float poente = smoothstep(-0.08, 0.02, nl) * (1.0 - smoothstep(0.02, 0.22, nl));
  cor = mix(cor, vec3(1.0, 0.64, 0.38), poente * 0.35);
  gl_FragColor = vec4(cor, a * mix(0.15, 0.9, luz));
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

// Halo: para cada pixel fora do disco, mede a que altura o raio de visao passa da Terra.
const ATMO_VERT = /* glsl */ `
varying vec3 vMundo;
void main() {
  vec4 m = modelMatrix * vec4(position, 1.0);
  vMundo = m.xyz;
  gl_Position = projectionMatrix * viewMatrix * m;
}`;

const ATMO_FRAG = /* glsl */ `
uniform vec3 sol;
uniform float raioAtmo;
varying vec3 vMundo;
void main() {
  vec3 dir = normalize(vMundo - cameraPosition);
  vec3 p = cameraPosition + dir * dot(-cameraPosition, dir);
  float b = length(p);
  float h = clamp((b - 1.0) / (raioAtmo - 1.0), 0.0, 1.0);
  float dens = exp(-h * 7.0) * (1.0 - h);
  float s = dot(p / max(b, 1e-4), normalize(sol));
  float dia = smoothstep(-0.25, 0.45, s);
  // olhando na direcao do sol a atmosfera acende (espalhamento para a frente)
  float frente = pow(max(dot(dir, normalize(sol)), 0.0), 6.0);
  // onde o dia encontra a noite, rente ao chao, a luz atravessa mais ar e fica laranja (como nas fotos da ISS)
  float ocaso = exp(-pow(s / 0.08, 2.0)) * exp(-h * 9.0);
  vec3 cor = mix(vec3(0.02, 0.05, 0.12), vec3(0.35, 0.62, 1.0), dia);
  cor = mix(cor, vec3(0.75, 0.86, 1.0), frente * 0.6);
  cor = mix(cor, vec3(1.0, 0.45, 0.16), ocaso * 0.7);
  gl_FragColor = vec4(cor * dens * (0.12 + 0.9 * dia + 1.6 * frente + 0.8 * ocaso), 1.0);
  #include <colorspace_fragment>
}`;

const ESTRELAS_VERT = /* glsl */ `
attribute float tamanho;
attribute float fase;
attribute vec3 tom;
uniform float tempo;
uniform float escalaPx;
uniform vec3 sol;
uniform float ofuscamento;   // 0..1: o sol visivel apaga as estrelas em volta dele, como numa camera
varying vec3 vTom;
varying float vPisca;
void main() {
  vec4 mundo = modelMatrix * vec4(position, 1.0);
  float ang = acos(clamp(dot(normalize(mundo.xyz - cameraPosition), normalize(sol)), -1.0, 1.0));
  float apaga = 1.0 - ofuscamento * exp(-pow(ang / 0.33, 2.0));
  vPisca = (0.86 + 0.14 * sin(tempo * (0.4 + fase * 1.2) + fase * 40.0)) * apaga;
  vTom = tom;
  gl_PointSize = tamanho * escalaPx;
  gl_Position = projectionMatrix * viewMatrix * mundo;
}`;

const ESTRELAS_FRAG = /* glsl */ `
varying vec3 vTom;
varying float vPisca;
void main() {
  float d = length(gl_PointCoord - 0.5);
  float a = pow(smoothstep(0.5, 0.0, d), 2.4) * vPisca;
  gl_FragColor = vec4(vTom * a, 1.0);
  #include <colorspace_fragment>
}`;

// Sol: disco recortado pela Terra pixel a pixel (o raio de visao bate na esfera?) e um
// ofuscamento que cai com a distancia angular, como numa camera. Sem reflexos de lente.
const SOL_VERT = /* glsl */ `
varying vec2 vUv;
varying vec3 vMundo;
void main() {
  vUv = uv;
  vec4 m = modelMatrix * vec4(position, 1.0);
  vMundo = m.xyz;
  gl_Position = projectionMatrix * viewMatrix * m;
}`;

const SOL_FRAG = /* glsl */ `
uniform float raioNucleo;   // raio do disco, na escala em que 1 = borda do painel
uniform float visivel;      // fracao do sol fora da Terra e da Lua (o ofuscamento some quando ele se esconde)
uniform vec2 luaUv;         // a Lua tambem recorta o disco (eclipse): centro e raio dela no proprio painel,
uniform float luaRaioUv;    // onde circulo continua circulo (sem a distorcao da perspectiva na borda)
uniform float eclipse;      // 0..1: quanto do disco a Lua cobre (acende a coroa solar)
varying vec2 vUv;
varying vec3 vMundo;
void main() {
  float r = length(vUv - 0.5) * 2.0;
  vec3 dir = normalize(vMundo - cameraPosition);
  float b = dot(cameraPosition, dir);
  float c = dot(cameraPosition, cameraPosition) - 1.0;
  float atras = smoothstep(-0.0006, 0.0006, b * b - c) * step(b, 0.0);
  float dLua = length(vUv - luaUv);
  float naLua = 1.0 - smoothstep(luaRaioUv * 0.985, luaRaioUv * 1.015, dLua);
  float disco = (1.0 - smoothstep(raioNucleo * 0.82, raioNucleo, r)) * (1.0 - atras) * (1.0 - naLua);
  // queda rapida: em espaco linear valores pequenos ainda aparecem depois da conversao para sRGB,
  // entao o brilho precisa sumir em poucos graus para o ceu continuar preto
  float halo = pow(raioNucleo / (r + raioNucleo), 2.3) * (1.0 - smoothstep(0.35, 0.7, r));
  float coroa = pow(raioNucleo / (r + raioNucleo * 0.6), 4.0);   // brilho estourado logo em volta do disco
  // coroa solar do eclipse: anel perolado com raios irregulares em volta da Lua escura
  float giro = atan(vUv.y - luaUv.y, vUv.x - luaUv.x);
  float raios = 0.55 + 0.45 * pow(abs(sin(giro * 3.0 + 1.3) * sin(giro * 7.0 - 0.4)), 0.7);
  float q = luaRaioUv / max(dLua, luaRaioUv);
  float anel = pow(q, 14.0);                  // borda fina e intensa
  float leque = pow(q, 4.5) * raios * 0.35;   // raios longos e fracos
  float coronaSolar = (anel * 0.9 + leque) * eclipse * (1.0 - naLua) * (1.0 - atras);
  vec3 cor = vec3(1.0, 0.99, 0.97) * disco * 6.0
           + vec3(1.0, 0.95, 0.88) * (halo * 2.4 + coroa * 1.6) * visivel * (1.0 - naLua)
           + vec3(0.93, 0.95, 1.0) * coronaSolar * 1.5;
  gl_FragColor = vec4(cor, 1.0);
  #include <colorspace_fragment>
}`;

// Fio de luz do contorno do Nordeste: desenha-se ao longo do comprimento (desenho 0..1) e depois
// um pulso percorre a borda. vProg = posicao ao longo da linha (0..1).
const LINHA_VERT = /* glsl */ `
attribute float progresso;
varying float vProg;
void main() {
  vProg = progresso;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;

const CONTORNO_FRAG = /* glsl */ `
uniform float desenho;
uniform float cabeca;
uniform float opacidade;
uniform vec3 cor;
varying float vProg;
void main() {
  if (vProg > desenho) discard;
  float ponta = exp(-pow((desenho - vProg) * 28.0, 2.0)) * step(desenho, 0.999);
  float pulso = exp(-fract(cabeca - vProg) * 22.0);
  gl_FragColor = vec4(cor * (0.55 + 1.8 * ponta + 1.1 * pulso) * opacidade, 1.0);
  #include <colorspace_fragment>
}`;

const DIVISA_FRAG = /* glsl */ `
uniform float opacidade;
uniform vec3 cor;
varying float vProg;
void main() {
  gl_FragColor = vec4(cor * 0.26 * opacidade, 1.0);
  #include <colorspace_fragment>
}`;

// Cortina de luz que sobe do contorno do Nordeste, como uma aurora: brilho na base que se apaga
// com a altura, estrias que ondulam, o mesmo pulso da borda e filetes de luz subindo.
const CORTINA_VERT = /* glsl */ `
attribute float progresso;
attribute float altura;
varying float vProg;
varying float vAlt;
void main() {
  vProg = progresso;
  vAlt = altura;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;

const CORTINA_FRAG = /* glsl */ `
uniform float tempo;
uniform float cabeca;
uniform float desenho;
uniform float opacidade;
uniform float apagar;       // a cortina some na descida para o mapa
uniform vec3 cor;
varying float vProg;
varying float vAlt;
float sorteio(float n) { return fract(sin(n) * 43758.5453); }
void main() {
  if (vProg > desenho) discard;
  float queda = pow(1.0 - vAlt, 2.4);
  float estria = 0.5 + 0.5 * sin(vProg * 410.0 + tempo * 1.6) * sin(vProg * 127.0 - tempo * 0.8);
  float pulso = exp(-fract(cabeca - vProg) * 18.0);
  float coluna = floor(vProg * 150.0);
  float h1 = sorteio(coluna * 12.9898);
  float h2 = sorteio(coluna * 78.233);
  float y = fract(vAlt * 0.85 - tempo * (0.1 + 0.12 * h1) + h2);
  float filete = exp(-pow((y - 0.5) * 7.0, 2.0)) * step(0.7, h1) * (1.0 - vAlt);
  float a = queda * (0.13 + 0.17 * estria + 0.55 * pulso) + filete * 0.75;
  gl_FragColor = vec4(cor * a * opacidade * (1.0 - apagar), 1.0);
  #include <colorspace_fragment>
}`;

// Capitais: pontos de luz pequenos que cintilam devagar
const CAPITAIS_VERT = /* glsl */ `
attribute float fase;
uniform float tempo;
uniform float escalaPx;
varying float vBrilho;
void main() {
  vBrilho = 0.72 + 0.28 * sin(tempo * 1.2 + fase * 6.2831);
  gl_PointSize = 10.0 * escalaPx;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;

const CAPITAIS_FRAG = /* glsl */ `
uniform float opacidade;
uniform vec3 cor;
varying float vBrilho;
void main() {
  float d = length(gl_PointCoord - 0.5);
  float nucleo = smoothstep(0.16, 0.0, d);
  float halo = pow(smoothstep(0.5, 0.0, d), 2.0) * 0.45;
  gl_FragColor = vec4(cor * (nucleo * 1.6 + halo) * vBrilho * opacidade, 1.0);
  #include <colorspace_fragment>
}`;

// Lua: Lommel-Seeliger (a Lua quase nao escurece na borda) + luz da Terra no lado escuro
const LUA_VERT = /* glsl */ `
varying vec2 vUv;
varying vec3 vN;
varying vec3 vMundo;
void main() {
  vUv = uv;
  vN = normalize(mat3(modelMatrix) * normal);
  vec4 m = modelMatrix * vec4(position, 1.0);
  vMundo = m.xyz;
  gl_Position = projectionMatrix * viewMatrix * m;
}`;

const LUA_FRAG = /* glsl */ `
uniform sampler2D mapa;
uniform vec3 luz;
varying vec2 vUv;
varying vec3 vN;
varying vec3 vMundo;
void main() {
  vec3 N = normalize(vN);
  vec3 V = normalize(cameraPosition - vMundo);
  float mu0 = max(dot(N, normalize(luz)), 0.0);
  float mu = max(dot(N, V), 0.0);
  float ls = mu0 / (mu0 + mu + 1e-4);
  vec3 tex = texture2D(mapa, vUv).rgb;
  vec3 cor = tex * ls * 2.3 + tex * vec3(0.014, 0.018, 0.028);
  gl_FragColor = vec4(cor, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

// ---------------------------------------------------------------- cena

function aleatorio(semente) {
  let s = semente >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export class Espaco {
  constructor(canvas, {
    aoPairar = () => {}, aoClicar = () => {}, aoProgresso = () => {}, aoAproximar = () => {}, aoEntrar = () => {},
  } = {}) {
    this.canvas = canvas;
    this.aoPairar = aoPairar;
    this.aoClicar = aoClicar;
    this.aoAproximar = aoAproximar;   // (0..1) quanto a pessoa ja mergulhou com o zoom
    this.aoEntrar = aoEntrar;         // (lat, lon) o zoom chegou ao fim: hora de virar mapa
    this.calmo = matchMedia('(prefers-reduced-motion: reduce)').matches;

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;

    this.cena = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(FOV, 1, 0.01, 3000);
    this.relogio = new THREE.Clock();
    this.raio = new THREE.Raycaster();

    // estado
    this.modo = 'livre';            // 'livre' (gira e responde ao mouse) | 'viagem' (animacao no controle)
    this.giro = GIRO_NE;            // o enquadramento do inicio olha para o Nordeste
    this.incl = INCL_NE;
    this.velGiro = 0;
    this.velIncl = 0;
    this.desloc = { x: 0, y: 0 };
    this.dist = 6;
    this.parallax = 1;
    this.mouseAlvo = new THREE.Vector2();
    this.mouseSuave = new THREE.Vector2();
    this.ponteiro = null;           // ultima posicao do ponteiro sobre o canvas
    this.arrastando = false;
    this.tweens = [];
    this.ativo = false;
    this.sol = SOL_NOITE.clone();   // direcao da luz, compartilhada por todos os shaders
    this.solInicio = new THREE.Vector3();
    // mergulho com a rodinha/pinca: 0 = enquadramento do inicio, 1 = ponto de troca para o mapa
    this.aprox = 0;
    this.aproxAlvo = 0;
    this.aproxAvisado = 0;
    this.foco = null;               // {lat, lon} para onde o zoom esta indo
    this.toques = new Map();        // ponteiros ativos (pinca no celular)

    const gerente = new THREE.LoadingManager();
    this.pronto = new Promise((ok) => {
      gerente.onLoad = ok;
      gerente.onError = () => {};   // a cena segue mesmo se uma textura falhar
    });
    gerente.onProgress = (_u, feitos, total) => aoProgresso(feitos / total);
    const carregador = new THREE.TextureLoader(gerente);
    const aniso = this.renderer.capabilities.getMaxAnisotropy();
    const carregar = (nome, srgb) => {
      const t = carregador.load(DIR_TEX + nome);
      if (srgb) t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = aniso;
      return t;
    };
    // Abre com texturas leves em WebP (~1,7 MB no total, contra ~6,8 MB das JPG 8K) e, no computador
    // (GPU com folga), troca por 8K e nuvens 4K em segundo plano depois que a abertura termina.
    this.k8 = this.renderer.capabilities.maxTextureSize >= 8192 && Math.min(screen.width, screen.height) >= 700;
    this.tex = {
      dia: carregar('earth_day.webp', true),
      noite: carregar('earth_night.webp', true),
      oceano: carregar('earth_ocean_mask.webp', false),
      normal: carregar('earth_normal.webp', false),
      nuvens: carregar('earth_clouds_2k.webp', false),   // tons de cinza = densidade da nuvem
      nordeste: carregar('nordeste_mascara.png', false),
      lua: carregar('moon.webp', true),
    };
    this.tex.nuvens.wrapS = THREE.RepeatWrapping;
    this.pronto.then(() => setTimeout(() => this._melhorarTexturas(), 5000));

    this._criarCeu();
    this._criarTerra();
    this._criarSol();
    this._criarNordeste();
    this._criarLua();
    this._criarMira();
    this._criarAlvo();

    this.layout = this._layoutInicio();
    this.solInicio.copy(this._solDoEnquadramento());
    this._posicionarLua();

    this._ligarEventos();
    this._redimensionar();
    this._quadro = this._quadro.bind(this);
  }

  /** Troca as texturas leves pelas de alta resolucao sem recriar materiais (mesmo objeto Texture). */
  _melhorarTexturas() {
    if (!this.k8) return;
    const carregador = new THREE.TextureLoader();
    const trocar = (tex, nome) => carregador.load(DIR_TEX + nome, (alta) => {
      tex.dispose();             // a GPU guardou o tamanho antigo: descartar antes de subir a imagem maior
      tex.image = alta.image;
      tex.needsUpdate = true;
    }, undefined, () => {});   // se falhar, fica a textura leve
    trocar(this.tex.dia, 'earth_day_8k.webp');
    trocar(this.tex.noite, 'earth_night_8k.webp');
    trocar(this.tex.nuvens, 'earth_clouds_4k.webp');
  }

  // ------------------------------------------------------------ construcao

  _criarCeu() {
    this.ceu = new THREE.Group();
    this.cena.add(this.ceu);

    const N = 7000;
    const pos = new Float32Array(N * 3);
    const tom = new Float32Array(N * 3);
    const tam = new Float32Array(N);
    const fase = new Float32Array(N);
    const paleta = [[0.82, 0.88, 1.0], [1.0, 1.0, 1.0], [1.0, 0.97, 0.92]];
    const rnd = aleatorio(7);
    const eixoGal = new THREE.Vector3(0.35, 1, -0.4).normalize();
    const v = new THREE.Vector3();
    for (let i = 0; i < N; i++) {
      const naFaixa = i < N * 0.4;
      v.set(rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1);
      if (v.lengthSq() < 1e-4) v.set(1, 0, 0);
      v.normalize();
      if (naFaixa) {
        // aproxima do plano da Via Lactea com espalhamento gaussiano
        const g = (rnd() + rnd() + rnd() - 1.5) * 0.16;
        v.addScaledVector(eixoGal, -v.dot(eixoGal)).normalize().addScaledVector(eixoGal, g).normalize();
      }
      const r = 500 + rnd() * 600;
      pos.set([v.x * r, v.y * r, v.z * r], i * 3);
      const c = paleta[Math.floor(rnd() * paleta.length)];
      const brilho = naFaixa ? 0.45 + rnd() * 0.35 : 0.6 + rnd() * 0.4;
      tom.set([c[0] * brilho, c[1] * brilho, c[2] * brilho], i * 3);
      tam[i] = naFaixa ? 0.9 + Math.pow(rnd(), 4) * 1.0 : 1.1 + Math.pow(rnd(), 8) * 2.2;
      fase[i] = rnd();
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('tom', new THREE.BufferAttribute(tom, 3));
    geo.setAttribute('tamanho', new THREE.BufferAttribute(tam, 1));
    geo.setAttribute('fase', new THREE.BufferAttribute(fase, 1));
    this.matEstrelas = new THREE.ShaderMaterial({
      vertexShader: ESTRELAS_VERT,
      fragmentShader: ESTRELAS_FRAG,
      uniforms: { tempo: { value: 0 }, escalaPx: { value: 1 }, sol: { value: this.sol }, ofuscamento: { value: 0 } },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    this.ceu.add(new THREE.Points(geo, this.matEstrelas));
  }

  _criarTerra() {
    this.pivo = new THREE.Group();
    this.cena.add(this.pivo);

    this.matTerra = new THREE.ShaderMaterial({
      vertexShader: TERRA_VERT,
      fragmentShader: TERRA_FRAG,
      uniforms: {
        mapaDia: { value: this.tex.dia },
        mapaNoite: { value: this.tex.noite },
        mapaOceano: { value: this.tex.oceano },
        mapaNormal: { value: this.tex.normal },
        mapaNuvens: { value: this.tex.nuvens },
        sol: { value: this.sol },
        desvioNuvens: { value: 0 },
        mapaNordeste: { value: this.tex.nordeste },
        caixaNordeste: { value: new THREE.Vector4(0, 0, 1, 1) },
        destaque: { value: 0 },
      },
    });
    this.pivo.add(new THREE.Mesh(new THREE.SphereGeometry(1, 192, 128), this.matTerra));

    this.nuvens = new THREE.Mesh(
      new THREE.SphereGeometry(RAIO_NUVENS, 160, 112),
      new THREE.ShaderMaterial({
        vertexShader: NUVENS_VERT,
        fragmentShader: NUVENS_FRAG,
        uniforms: { mapaNuvens: { value: this.tex.nuvens }, sol: { value: this.sol } },
        transparent: true,
        depthWrite: false,
      }),
    );
    this.pivo.add(this.nuvens);

    this.atmo = new THREE.Mesh(
      new THREE.SphereGeometry(RAIO_ATMO, 128, 96),
      new THREE.ShaderMaterial({
        vertexShader: ATMO_VERT,
        fragmentShader: ATMO_FRAG,
        uniforms: { sol: { value: this.sol }, raioAtmo: { value: RAIO_ATMO } },
        side: THREE.BackSide,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        toneMapped: false,
      }),
    );
    this.cena.add(this.atmo);
  }

  _criarSol() {
    const lado = 2 * DIST_SOL * Math.tan(MEIO_CAMPO_SOL);
    this.matSol = new THREE.ShaderMaterial({
      vertexShader: SOL_VERT,
      fragmentShader: SOL_FRAG,
      uniforms: {
        raioNucleo: { value: Math.tan(RAIO_SOL) / Math.tan(MEIO_CAMPO_SOL) },
        visivel: { value: 0 },
        luaUv: { value: new THREE.Vector2(-10, -10) },
        luaRaioUv: { value: 0 },
        eclipse: { value: 0 },
      },
      transparent: true,
      depthTest: false,               // o ofuscamento passa por cima da borda da Terra, como numa foto
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      toneMapped: false,
    });
    this.solMalha = new THREE.Mesh(new THREE.PlaneGeometry(lado, lado), this.matSol);
    this.solMalha.renderOrder = 10;
    this.solMalha.frustumCulled = false;
    this.cena.add(this.solMalha);
  }

  /** Painel do sol: longe, na direcao da luz, de frente para a camera; mede quanto aparece. */
  _atualizarSol() {
    this.solMalha.position.copy(this.sol).multiplyScalar(DIST_SOL);
    this.solMalha.quaternion.copy(this.camera.quaternion);
    const cam = this.camera.position;
    const theta = this.solMalha.position.clone().sub(cam).angleTo(cam.clone().negate());
    const alfa = Math.asin(Math.min(1, 1 / cam.length()));
    const v = limitar((theta - (alfa - RAIO_SOL)) / (2 * RAIO_SOL), 0, 1);
    const foraDaTerra = v * v * (3 - 2 * v);

    // eclipse, medido no plano do painel do Sol (paralelo a tela: circulo continua circulo).
    // A Lua desenhada e achatada na direcao radial (_atualizarLua) para parecer redonda; aqui ela
    // vira um circulo de raio r' = z * tan(raio angular) / cos(angulo fora do eixo).
    const f = this.camera.getWorldDirection(new THREE.Vector3());
    const paraLua = this.lua.position.clone().sub(cam);
    const dLua = paraLua.clone().normalize();
    const cosT = Math.max(0.2, dLua.dot(f));
    const zPainel = this.solMalha.position.clone().sub(cam).dot(f);
    const noPlano = cam.clone().addScaledVector(dLua, zPainel / cosT).sub(this.solMalha.position);
    const lado = 2 * DIST_SOL * Math.tan(MEIO_CAMPO_SOL);
    const direita = new THREE.Vector3(1, 0, 0).applyQuaternion(this.camera.quaternion);
    const cima = new THREE.Vector3(0, 1, 0).applyQuaternion(this.camera.quaternion);
    const u = this.matSol.uniforms;
    u.luaUv.value.set(0.5 + noPlano.dot(direita) / lado, 0.5 + noPlano.dot(cima) / lado);
    const raioAng = Math.asin(Math.min(1, RAIO_LUA / paraLua.length()));
    u.luaRaioUv.value = this.lua.visible ? (zPainel * Math.tan(raioAng)) / cosT / lado : 0;
    const raioSolUv = u.raioNucleo.value / 2;
    const sep = u.luaUv.value.distanceTo(new THREE.Vector2(0.5, 0.5));
    const cobre = limitar((u.luaRaioUv.value + raioSolUv - sep) / (2 * raioSolUv), 0, 1);
    const eclipse = cobre * cobre * (3 - 2 * cobre);

    u.visivel.value = foraDaTerra * (1 - 0.97 * eclipse);
    u.eclipse.value = eclipse * foraDaTerra;
    // com o Sol a mostra, as estrelas em volta somem; no eclipse elas voltam
    this.matEstrelas.uniforms.ofuscamento.value = this.solMalha.visible ? u.visivel.value : 0;
  }

  /** Direcao do sol que o coloca no alto a direita da tela, no enquadramento do inicio. */
  _solDoEnquadramento() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const alvo = w / h < 0.95 ? ALVO_SOL.retrato : ALVO_SOL.paisagem;
    const cam = new THREE.PerspectiveCamera(FOV, w / h, 0.01, 3000);
    cam.position.set(0, 0, this.layout.dist);
    cam.lookAt(0, 0, 0);
    cam.setViewOffset(w, h, this.layout.x * w, this.layout.y * h, w, h);
    cam.updateMatrixWorld();
    const raio = new THREE.Raycaster();
    raio.setFromCamera(new THREE.Vector2(alvo.x * 2 - 1, -(alvo.y * 2 - 1)), cam);
    return raio.ray.direction.clone().normalize();
  }

  // ------------------------------------------------------------ Nordeste

  /** Contorno (IBGE), divisas dos estados e capitais, presos a superficie. Entram com revelarNordeste(). */
  _criarNordeste() {
    this.grupoNE = new THREE.Group();
    this.pivo.add(this.grupoNE);
    const dourado = new THREE.Color(0xffcb7d);
    const base = { transparent: true, depthWrite: false, blending: THREE.AdditiveBlending };
    this.matContorno = new THREE.ShaderMaterial({
      vertexShader: LINHA_VERT,
      fragmentShader: CONTORNO_FRAG,
      uniforms: { desenho: { value: 0 }, cabeca: { value: 0 }, opacidade: { value: 1 }, cor: { value: dourado } },
      ...base,
    });
    this.matDivisas = new THREE.ShaderMaterial({
      vertexShader: LINHA_VERT,
      fragmentShader: DIVISA_FRAG,
      uniforms: { opacidade: { value: 0 }, cor: { value: dourado } },
      ...base,
    });
    this.matCortina = new THREE.ShaderMaterial({
      vertexShader: CORTINA_VERT,
      fragmentShader: CORTINA_FRAG,
      uniforms: {
        tempo: { value: 0 }, cabeca: { value: 0 }, desenho: { value: 0 }, opacidade: { value: 0 }, apagar: { value: 0 },
        cor: { value: dourado },
      },
      side: THREE.DoubleSide,
      ...base,
    });

    const pos = new Float32Array(CAPITAIS_NE.length * 3);
    const fase = new Float32Array(CAPITAIS_NE.length);
    CAPITAIS_NE.forEach(([, lat, lon], i) => {
      pos.set(latLonParaVetor(lat, lon, RAIO_LINHAS).toArray(), i * 3);
      fase[i] = i / CAPITAIS_NE.length;
    });
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('fase', new THREE.BufferAttribute(fase, 1));
    this.matCapitais = new THREE.ShaderMaterial({
      vertexShader: CAPITAIS_VERT,
      fragmentShader: CAPITAIS_FRAG,
      uniforms: { tempo: { value: 0 }, escalaPx: { value: 1 }, opacidade: { value: 0 }, cor: { value: new THREE.Color(0xffe2b0) } },
      ...base,
    });
    this.grupoNE.add(new THREE.Points(geo, this.matCapitais));

    fetch(new URL('../../dados/nordeste.json', import.meta.url))
      .then((r) => r.json())
      .then((d) => {
        this.matTerra.uniforms.caixaNordeste.value.set(...d.bbox);
        d.contorno.forEach((anel) => {
          this.grupoNE.add(new THREE.Line(this._geoLinha(anel), this.matContorno));
          this.grupoNE.add(new THREE.Mesh(this._geoCortina(anel), this.matCortina));
        });
        d.divisas.forEach((l) => this.grupoNE.add(new THREE.Line(this._geoLinha(l), this.matDivisas)));
      })
      .catch(() => {});
  }

  /** Linha sobre a esfera com o atributo `progresso` (0..1 ao longo do comprimento). */
  _geoLinha(pontos) {
    const vs = pontos.map(([lon, lat]) => latLonParaVetor(lat, lon, RAIO_LINHAS));
    const acum = [0];
    for (let i = 1; i < vs.length; i++) acum.push(acum[i - 1] + vs[i].distanceTo(vs[i - 1]));
    const total = acum[acum.length - 1] || 1;
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(vs.flatMap((v) => v.toArray())), 3));
    geo.setAttribute('progresso', new THREE.BufferAttribute(new Float32Array(acum.map((a) => a / total)), 1));
    return geo;
  }

  /** Faixa vertical sobre o contorno: base na superficie, topo ALTURA_CORTINA acima (atributo altura 0..1). */
  _geoCortina(pontos) {
    const ns = pontos.map(([lon, lat]) => latLonParaVetor(lat, lon, 1));
    const acum = [0];
    for (let i = 1; i < ns.length; i++) acum.push(acum[i - 1] + ns[i].distanceTo(ns[i - 1]));
    const total = acum[acum.length - 1] || 1;
    const pos = [];
    const prog = [];
    const alt = [];
    const idx = [];
    ns.forEach((n, i) => {
      pos.push(...n.clone().multiplyScalar(RAIO_LINHAS).toArray(), ...n.clone().multiplyScalar(RAIO_LINHAS + ALTURA_CORTINA).toArray());
      prog.push(acum[i] / total, acum[i] / total);
      alt.push(0, 1);
      if (i > 0) {
        const a = (i - 1) * 2;
        idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
      }
    });
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute('progresso', new THREE.Float32BufferAttribute(prog, 1));
    geo.setAttribute('altura', new THREE.Float32BufferAttribute(alt, 1));
    geo.setIndex(idx);
    return geo;
  }

  /** O fio de luz contorna o Nordeste; depois acendem as divisas, as capitais e as luzes da regiao. */
  revelarNordeste() {
    const u = this.matTerra.uniforms;
    if (this.calmo) {
      this.matContorno.uniforms.desenho.value = 1;
      this.matCortina.uniforms.desenho.value = 1;
      this.matCortina.uniforms.opacidade.value = 1;
      this.matDivisas.uniforms.opacidade.value = 1;
      this.matCapitais.uniforms.opacidade.value = 1;
      u.destaque.value = 1;
      return Promise.resolve();
    }
    return this._animar(3600, (p) => {
      this.matContorno.uniforms.desenho.value = suave(limitar(p / 0.75, 0, 1));
      this.matCortina.uniforms.desenho.value = this.matContorno.uniforms.desenho.value;
      this.matCortina.uniforms.opacidade.value = suave(limitar((p - 0.1) / 0.6, 0, 1));
      this.matDivisas.uniforms.opacidade.value = limitar((p - 0.55) / 0.45, 0, 1);
      this.matCapitais.uniforms.opacidade.value = limitar((p - 0.65) / 0.35, 0, 1);
      u.destaque.value = suave(limitar((p - 0.2) / 0.8, 0, 1));
    });
  }

  // ------------------------------------------------------------ Lua

  _criarLua() {
    this.matLua = new THREE.ShaderMaterial({
      vertexShader: LUA_VERT,
      fragmentShader: LUA_FRAG,
      uniforms: { mapa: { value: this.tex.lua }, luz: { value: new THREE.Vector3(1, 0, 0) } },
    });
    this.lua = new THREE.Mesh(new THREE.SphereGeometry(RAIO_LUA, 96, 64), this.matLua);
    this.lua.matrixAutoUpdate = false;    // a matriz e montada em _atualizarLua (ha um achatamento)
    this.luaGiro = -Math.PI / 2;          // lado visivel da Lua (longitude 0) virado para a camera
    this.cena.add(this.lua);
  }

  /**
   * Orbita da Lua para o enquadramento atual: elipse na tela centrada na Terra que passa pelo
   * ponto onde o Sol aparece (ali acontece o eclipse). Guarda a camera do inicio para projetar.
   */
  _posicionarLua() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const retrato = w / h < 0.95;
    const cam = new THREE.PerspectiveCamera(FOV, w / h, 0.01, 3000);
    cam.position.set(0, 0, this.layout.dist);
    cam.lookAt(0, 0, 0);
    cam.setViewOffset(w, h, this.layout.x * w, this.layout.y * h, w, h);
    cam.updateMatrixWorld();
    this.camInicio = cam;
    // em unidades de altura de tela (u para a direita, v para baixo)
    const asp = w / h;
    const centro = { u: (0.5 - this.layout.x) * asp, v: 0.5 - this.layout.y };
    const sol = retrato ? ALVO_SOL.retrato : ALVO_SOL.paisagem;
    const du = sol.x * asp - centro.u;
    const dv = sol.y - centro.v;
    const ry = Math.max(retrato ? ORBITA_LUA_RY.retrato : ORBITA_LUA_RY.paisagem, Math.abs(dv) * 1.15);
    const rx = Math.abs(du) / Math.sqrt(1 - (dv / ry) ** 2);
    this.orbitaLua = { centro, rx, ry, asp, thetaSol: Math.atan2(dv / ry, du / rx) };
  }

  /** Move a Lua na orbita, gira devagar e acerta a luz (fase). */
  _atualizarLua(dt) {
    const o = this.orbitaLua;
    const t = this.relogio.elapsedTime;
    // devagar perto do Sol (o eclipse dura alguns segundos), depressa escondida atras da Terra
    const tau = (2 * Math.PI * (t - PRIMEIRO_ECLIPSE)) / PERIODO_LUA;
    const th = o.thetaSol + tau - 0.86 * Math.sin(tau);
    const u = o.centro.u + o.rx * Math.cos(th);
    const v = o.centro.v + o.ry * Math.sin(th);
    const ndc = new THREE.Vector3((u / o.asp) * 2 - 1, -(v * 2 - 1), 0.5).unproject(this.camInicio);
    const dir = ndc.sub(this.camInicio.position).normalize();
    const escala = 1 + 0.22 * Math.sin(th);   // mais perto (maior) embaixo, mais longe em cima
    const pos = this.lua.position.copy(this.camInicio.position).addScaledVector(dir, DIST_LUA / escala);
    this.luaGiro += dt * 0.015;
    // perto da borda do quadro a perspectiva estica a esfera na direcao radial; achata para compensar
    const frente = this.camera.getWorldDirection(new THREE.Vector3());
    const d = pos.clone().sub(this.camera.position).normalize();
    const ka = limitar(d.dot(frente), 0.2, 1) - 1;
    const tr = frente.clone().addScaledVector(d, -d.dot(frente));
    const achata = new THREE.Matrix4();
    if (tr.lengthSq() > 1e-8) {
      const { x, y, z } = tr.normalize();
      achata.set(
        1 + ka * x * x, ka * x * y, ka * x * z, 0,
        ka * y * x, 1 + ka * y * y, ka * y * z, 0,
        ka * z * x, ka * z * y, 1 + ka * z * z, 0,
        0, 0, 0, 1,
      );
    }
    this.lua.matrix.makeTranslation(pos.x, pos.y, pos.z).multiply(achata)
      .multiply(new THREE.Matrix4().makeRotationY(this.luaGiro));
    this.lua.matrixWorldNeedsUpdate = true;

    // Fase: longe do Sol, um crescente gordo (com o Sol no quadro a fase real seria um fio);
    // chegando perto do Sol, a fase real, ate a Lua nova do eclipse. O lado aceso aponta para o Sol.
    const V = this.camera.position.clone().sub(this.lua.position).normalize();
    const real = Math.acos(limitar(V.dot(this.sol), -1, 1));
    const lim = 120 * GRAU;
    const k = limitar((real - 155 * GRAU) / (22 * GRAU), 0, 1);
    const fase = real <= lim ? real : lim + (real - lim) * k * k * (3 - 2 * k);
    const P = this.sol.clone().addScaledVector(V, -this.sol.dot(V));
    if (P.lengthSq() < 1e-6) P.set(1, 0, 0);
    P.normalize();
    this.matLua.uniforms.luz.value.copy(P.multiplyScalar(Math.sin(fase)).addScaledVector(V, Math.cos(fase)));
  }

  _materialTraco(opacidade) {
    return new THREE.MeshBasicMaterial({
      color: 0xffffff, transparent: true, opacity: opacidade, depthWrite: false, side: THREE.DoubleSide,
    });
  }

  _criarMira() {
    // mira de instrumento: anel fino com quatro tracos
    const mat = this._materialTraco(0.85);
    this.mira = new THREE.Group();
    this.mira.add(new THREE.Mesh(new THREE.RingGeometry(0.03, 0.0325, 64), mat));
    for (let k = 0; k < 4; k++) {
      const traco = new THREE.Mesh(new THREE.PlaneGeometry(0.014, 0.0025), mat);
      const a = (k * Math.PI) / 2;
      traco.position.set(Math.cos(a) * 0.045, Math.sin(a) * 0.045, 0);
      traco.rotation.z = a;
      this.mira.add(traco);
    }
    this.mira.visible = false;
    this.cena.add(this.mira);
  }

  _criarAlvo() {
    // destino: ponto branco com anel fino, preso a superficie
    this.alvo = new THREE.Group();
    this.alvo.visible = false;
    const anel = new THREE.Mesh(new THREE.RingGeometry(0.02, 0.023, 64), this._materialTraco(0.95));
    const ponto = new THREE.Mesh(new THREE.CircleGeometry(0.0055, 24), this._materialTraco(1));
    anel.rotation.x = -Math.PI / 2;
    ponto.rotation.x = -Math.PI / 2;
    this.alvo.add(anel, ponto);
    this.pivo.add(this.alvo);
  }

  // ------------------------------------------------------------ eventos

  _ligarEventos() {
    window.addEventListener('resize', () => this._redimensionar());
    window.addEventListener('pointermove', (e) => {
      this.mouseAlvo.set((e.clientX / window.innerWidth) * 2 - 1, -((e.clientY / window.innerHeight) * 2 - 1));
    });

    // rodinha em qualquer lugar da tela (menos na lista de sugestoes) aproxima/afasta o planeta
    window.addEventListener('wheel', (e) => {
      if (this.modo !== 'livre' || e.target.closest?.('.sugestoes')) return;
      e.preventDefault();
      const passo = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
      this._aproximar(-passo * 0.0016, e.clientX, e.clientY);
    }, { passive: false });

    const c = this.canvas;
    c.addEventListener('pointerdown', (e) => {
      this.toques.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (this.toques.size === 2) {           // pinca: o segundo dedo cancela o arrasto
        this.arrastando = false;
        this.pinca = this._distToques();
        return;
      }
      if (this.modo !== 'livre') return;
      this.arrastando = true;
      this.movido = 0;
      this.ultimo = { x: e.clientX, y: e.clientY, t: performance.now() };
      this.velGiro = 0;
      this.velIncl = 0;
      c.setPointerCapture(e.pointerId);
      c.classList.add('arrastando');
    });
    c.addEventListener('pointermove', (e) => {
      this.ponteiro = { x: e.clientX, y: e.clientY };
      if (this.toques.has(e.pointerId)) this.toques.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (this.toques.size === 2 && this.modo === 'livre') {
        const d = this._distToques();
        const [a, b] = [...this.toques.values()];
        this._aproximar((d - this.pinca) * 0.004, (a.x + b.x) / 2, (a.y + b.y) / 2);
        this.pinca = d;
        return;
      }
      if (!this.arrastando) return;
      const agora = performance.now();
      const dx = e.clientX - this.ultimo.x;
      const dy = e.clientY - this.ultimo.y;
      const dt = Math.max(8, agora - this.ultimo.t) / 1000;
      const k = 1 / this._raioPx();
      this.movido += Math.abs(dx) + Math.abs(dy);
      if (this.aprox > 0.02) {                // durante o mergulho o arrasto nao gira o planeta
        this.ultimo = { x: e.clientX, y: e.clientY, t: agora };
        return;
      }
      this.giro += dx * k;
      this.incl = limitar(this.incl + dy * k, -1.0, 1.0);
      this.velGiro = lerp(this.velGiro, (dx * k) / dt, 0.5);
      this.velIncl = lerp(this.velIncl, (dy * k) / dt, 0.5);
      this.ultimo = { x: e.clientX, y: e.clientY, t: agora };
    });
    const soltar = (e) => {
      this.toques.delete(e.pointerId);
      if (!this.arrastando) return;
      this.arrastando = false;
      c.classList.remove('arrastando');
      if (performance.now() - this.ultimo.t > 90) { this.velGiro = 0; this.velIncl = 0; }
      if (this.movido < 6 && e.type === 'pointerup') {
        if (this.aoClicarAntes?.(e.clientX, e.clientY)) return;   // um extra (o satelite) pegou o clique
        const p = this._pontoNaTerra(e.clientX, e.clientY);
        if (p) this.aoClicar(p.lat, p.lon, e.clientX, e.clientY);
      }
    };
    c.addEventListener('pointerup', soltar);
    c.addEventListener('pointercancel', soltar);
    c.addEventListener('pointerleave', () => { this.ponteiro = null; });
  }

  _redimensionar() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.matEstrelas.uniforms.escalaPx.value = this.renderer.getPixelRatio();
    this.matCapitais.uniforms.escalaPx.value = this.renderer.getPixelRatio();
    this.layout = this._layoutInicio();
    this.solInicio.copy(this._solDoEnquadramento());
    this._posicionarLua();
    if (this.modo === 'livre' && !this.tweens.length && !this.foco) {
      this.dist = this.layout.dist;
      if (this.ativo) this.sol.copy(this.solInicio);
    }
  }

  /** Onde a Terra fica no inicio: grande a esquerda no desktop, no alto no celular. */
  _layoutInicio() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const retrato = w / h < 0.95;
    const cx = retrato ? 0.5 : 0.14;
    const cy = retrato ? 0.3 : 0.5;
    const rPx = retrato ? Math.min(0.46 * w, 0.26 * h) : Math.min(0.5 * h, 0.3 * w);
    const ang = Math.atan((rPx / (h / 2)) * Math.tan((FOV * GRAU) / 2));
    return { x: 0.5 - cx, y: 0.5 - cy, dist: 1 / Math.sin(ang) };
  }

  _raioPx() {
    const h = window.innerHeight;
    return ((h / 2) * Math.tan(Math.asin(1 / this.dist))) / Math.tan((FOV * GRAU) / 2);
  }

  _distToques() {
    const [a, b] = [...this.toques.values()];
    return Math.hypot(a.x - b.x, a.y - b.y);
  }

  _pontoNaTerra(x, y) {
    const ndc = new THREE.Vector2((x / window.innerWidth) * 2 - 1, -(y / window.innerHeight) * 2 + 1);
    this.raio.setFromCamera(ndc, this.camera);
    const { origin: o, direction: d } = this.raio.ray;
    const b = o.dot(d);
    const disc = b * b - (o.lengthSq() - 1);
    if (disc < 0) return null;
    const t = -b - Math.sqrt(disc);
    if (t < 0) return null;
    const mundo = o.clone().addScaledVector(d, t);
    const local = mundo.clone().applyQuaternion(this.pivo.quaternion.clone().invert());
    return {
      mundo,
      lat: Math.asin(limitar(local.y, -1, 1)) / GRAU,
      lon: Math.atan2(-local.z, local.x) / GRAU,
    };
  }

  /** Ponto da superficie mais proximo da camera. */
  _pontoDeFrente() {
    const local = this.camera.position.clone().normalize().applyQuaternion(this.pivo.quaternion.clone().invert());
    return { lat: Math.asin(limitar(local.y, -1, 1)) / GRAU, lon: Math.atan2(-local.z, local.x) / GRAU };
  }

  // ------------------------------------------------------------ orientacoes

  _qInicio(giro, incl) {
    return new THREE.Quaternion().setFromAxisAngle(EZ, EIXO)
      .multiply(new THREE.Quaternion().setFromAxisAngle(EX, incl))
      .multiply(new THREE.Quaternion().setFromAxisAngle(EY, giro));
  }

  /** Orientacao que poe (lat, lon) de frente para a camera, com o norte para cima. */
  _qAlvo(lat, lon) {
    return new THREE.Quaternion().setFromAxisAngle(EX, lat * GRAU)
      .multiply(new THREE.Quaternion().setFromAxisAngle(EY, -(lon + 90) * GRAU));
  }

  _posicionarAlvo(lat, lon) {
    const n = latLonParaVetor(lat, lon);
    this.alvo.position.copy(n).multiplyScalar(RAIO_MARCAS);
    this.alvo.quaternion.setFromUnitVectors(EY, n);
    this.alvo.visible = true;
  }

  // ------------------------------------------------------------ mergulho com zoom

  /** Avanca o mergulho. O foco e o ponto sob o cursor (ou o centro visivel do planeta). */
  _aproximar(delta, x, y) {
    if (this.aproxAlvo === 0 && delta <= 0) return;
    if (!this.foco) {
      const p = this._pontoNaTerra(x, y);
      const foco = p ? { lat: p.lat, lon: p.lon } : this._pontoDeFrente();
      if (this.podeMergulhar && !this.podeMergulhar(foco.lat, foco.lon)) return;   // so desce onde a pagina deixa
      this.foco = foco;
      this.qFoco = this._qAlvo(this.foco.lat, this.foco.lon);
      this.velGiro = 0;
      this.velIncl = 0;
      this._posicionarAlvo(this.foco.lat, this.foco.lon);
    }
    this.aproxAlvo = limitar(this.aproxAlvo + delta, 0, 1);
  }

  _zerarMergulho() {
    this.aprox = 0;
    this.aproxAlvo = 0;
    this.foco = null;
    if (this.aproxAvisado !== 0) { this.aproxAvisado = 0; this.aoAproximar(0); }
  }

  // ------------------------------------------------------------ API usada pela pagina

  /**
   * Abertura: a camera comeca perto do lado da noite (so as luzes das cidades), recua ate o
   * enquadramento do inicio e o sol "nasce" pela borda esquerda.
   */
  iniciar() {
    this.ativo = true;
    this.relogio.getDelta();
    requestAnimationFrame(this._quadro);
    const gFinal = this.giro;
    if (this.calmo) {
      this.desloc.x = this.layout.x;
      this.desloc.y = this.layout.y;
      this.dist = this.layout.dist;
      this.sol.copy(this.solInicio);
      this.revelarNordeste();
      return Promise.resolve();
    }
    this.modo = 'viagem';
    this.parallax = 0;
    setTimeout(() => this.revelarNordeste(), 4300);
    return this._animar(5600, (p) => {
      const e = suave(p);
      const sai = saida(p);
      this.dist = lerp(1.7, this.layout.dist, sai);
      this.desloc.x = lerp(0, this.layout.x, e);
      this.desloc.y = lerp(0, this.layout.y, e);
      this.giro = gFinal - 1.1 * (1 - sai);              // gira rapido e desacelera
      this.incl = lerp(0.4, INCL_NE, e);
      this.pivo.quaternion.copy(this._qInicio(this.giro, this.incl));
      this.sol.copy(SOL_NOITE).lerp(this.solInicio, suave(limitar((p - 0.1) / 0.8, 0, 1))).normalize();
      this.parallax = e;
    }, 'abertura').then(() => {
      this.modo = 'livre';   // (se a pessoa viajou durante a abertura, esta promessa nunca resolve)
    });
  }

  /** Altitude da camera sobre a superficie, em km. */
  altitudeKm() {
    return (this.dist - 1) * RAIO_TERRA_KM;
  }

  /** Ponto da superficie bem abaixo da camera (nadir). */
  nadir() {
    return this._pontoDeFrente();
  }

  pausar() { this.ativo = false; }

  retomar() {
    if (this.ativo) return;
    this.ativo = true;
    this.relogio.getDelta();
    requestAnimationFrame(this._quadro);
  }

  mostrarTerra(sim) {
    this.pivo.visible = sim;
    this.atmo.visible = sim;
    this.solMalha.visible = sim;
    this.lua.visible = sim;
    if (!sim) this.mira.visible = false;
  }

  /** Gira o planeta ate o lugar, centraliza e aproxima ate a distancia de troca para o mapa. */
  viajar(lat, lon) {
    // interrompe a abertura se a pessoa ja buscou algo (a revelacao do Nordeste continua)
    this.tweens = this.tweens.filter((tw) => tw.nome !== 'abertura');
    this.modo = 'viagem';
    this.arrastando = false;
    this.mira.visible = false;
    this.aoPairar(null);
    this._posicionarAlvo(lat, lon);
    const q0 = this.pivo.quaternion.clone();
    const q1 = this._qAlvo(lat, lon);
    const x0 = this.desloc.x, y0 = this.desloc.y, d0 = this.dist, p0 = this.parallax;
    const s0 = this.sol.clone();
    // se a pessoa ja mergulhou com o zoom, falta pouco caminho: a viagem encurta
    const falta = limitar((d0 - DIST_TROCA) / Math.max(0.01, this.layout.dist - DIST_TROCA), 0.15, 1);
    const dur = ((this.calmo ? 900 : 1900) + q0.angleTo(q1) * 480) * falta;
    this._zerarMergulho();
    return this._animar(dur, (p) => {
      const e = suave(p);
      this.pivo.quaternion.slerpQuaternions(q0, q1, e);
      this.sol.copy(s0).lerp(SOL_DESTINO, e).normalize();
      this.desloc.x = lerp(x0, 0, e);
      this.desloc.y = lerp(y0, 0, e);
      this.dist = lerp(d0, DIST_TROCA, suave(limitar((p - 0.12) / 0.88, 0, 1)));
      this.parallax = lerp(p0, 0, e);
      this._descerNordeste(suave(limitar((p - 0.3) / 0.7, 0, 1)));
    });
  }

  /**
   * Na descida o fio do Nordeste baixa ate o chao e a cortina se apaga: na troca ele coincide com o
   * contorno desenhado no mapa (sem contorno duplo). e = 0 no alto, 1 na troca.
   */
  _descerNordeste(e) {
    this.grupoNE.scale.setScalar(lerp(1, 1.0006 / RAIO_LINHAS, e));
    this.matCortina.uniforms.apagar.value = limitar((e - 0.25) / 0.5, 0, 1);
  }

  /** Coloca a Terra centralizada no lugar, na distancia do mapa (antes de esconder o mapa). */
  posicionarNoCentro(lat, lon, dist = DIST_TROCA) {
    this.modo = 'viagem';
    this.pivo.quaternion.copy(this._qAlvo(lat, lon));
    this.desloc.x = 0;
    this.desloc.y = 0;
    this.dist = dist;
    this.parallax = 0;
    this.sol.copy(SOL_DESTINO);
    this._descerNordeste(1);
    this.alvo.visible = false;
    this.mostrarTerra(true);
  }

  /** Afasta a camera de volta ao enquadramento do inicio. */
  voltar(lat, lon) {
    const q0 = this.pivo.quaternion.clone();
    this.giro = -(lon + 90) * GRAU;
    this.incl = limitar(lat * GRAU * 0.6, -0.8, 0.8);
    const q1 = this._qInicio(this.giro, this.incl);
    const d0 = this.dist;
    return this._animar(this.calmo ? 900 : 2400, (p) => {
      const e = suave(p);
      this.pivo.quaternion.slerpQuaternions(q0, q1, e);
      this.desloc.x = lerp(0, this.layout.x, e);
      this.desloc.y = lerp(0, this.layout.y, e);
      this.dist = lerp(d0, this.layout.dist, e);
      this.parallax = e;
      this.sol.copy(SOL_DESTINO).lerp(this.solInicio, e).normalize();
      this._descerNordeste(1 - e);
    }).then(() => {
      this.modo = 'livre';
      this.velGiro = 0;
      this.velIncl = 0;
      this._zerarMergulho();
    });
  }

  // ------------------------------------------------------------ animacao

  _animar(dur, passo, nome = '') {
    return new Promise((ok) => this.tweens.push({ t0: performance.now(), dur, passo, ok, nome }));
  }

  _quadro() {
    if (!this.ativo) return;
    requestAnimationFrame(this._quadro);
    const dt = Math.min(this.relogio.getDelta(), 0.05);
    const t = this.relogio.elapsedTime;
    const agora = performance.now();

    this.tweens = this.tweens.filter((tw) => {
      const p = limitar((agora - tw.t0) / tw.dur, 0, 1);
      tw.passo(p);
      if (p >= 1) { tw.ok(); return false; }
      return true;
    });

    this.mouseSuave.lerp(this.mouseAlvo, 1 - Math.exp(-dt * 2));
    if (this.modo === 'livre') this._passoLivre(dt);

    // nuvens andam um pouco mais rapido que o chao
    this.nuvens.rotation.y += dt * 0.005;
    this.matTerra.uniforms.desvioNuvens.value = -this.nuvens.rotation.y / (Math.PI * 2);

    // ceu: rotacao muito lenta
    this.ceu.rotation.y += dt * 0.002;
    this.matEstrelas.uniforms.tempo.value = t;
    this.matCapitais.uniforms.tempo.value = t;
    this.matContorno.uniforms.cabeca.value = (t * 0.045) % 1;   // pulso da borda: uma volta a cada ~22 s
    this.matCortina.uniforms.cabeca.value = this.matContorno.uniforms.cabeca.value;
    this.matCortina.uniforms.tempo.value = t;

    this._aplicarCamera();
    this._atualizarLua(dt);   // antes do Sol: o eclipse depende de onde a Lua esta
    this._atualizarSol();
    this._atualizarMira();
    this.aoQuadro?.(dt, t);   // gancho para quem desenha extras na cena (ovos.js)
    this.renderer.render(this.cena, this.camera);
  }

  /** Modo livre: giro automatico/inercia e, se houver, o mergulho com zoom. */
  _passoLivre(dt) {
    const mergulhando = this.foco !== null;
    if (!this.arrastando && !mergulhando) {
      // inercia do arrasto; depois o planeta volta devagar a olhar para o Nordeste, balancando
      this.giro += this.velGiro * dt;
      this.incl = limitar(this.incl + this.velIncl * dt, -1.0, 1.0);
      this.velGiro *= Math.exp(-dt * 2.2);
      this.velIncl *= Math.exp(-dt * 3.0);
      const t = this.relogio.elapsedTime;
      const balanco = this.calmo ? 0 : 1;
      const giroAlvo = GIRO_NE + balanco * 0.11 * Math.sin(t * 0.07);
      const inclAlvo = INCL_NE + balanco * 0.035 * Math.sin(t * 0.05 + 1.3);
      // volta pelo caminho mais curto (o arrasto pode ter dado varias voltas), so depois da inercia
      const dg = Math.atan2(Math.sin(giroAlvo - this.giro), Math.cos(giroAlvo - this.giro));
      const k = 1 - Math.exp(-dt * 0.3 * Math.max(0, 1 - Math.abs(this.velGiro)));
      this.giro += dg * k;
      this.incl = lerp(this.incl, inclAlvo, k);
    }
    const q = this._qInicio(this.giro, this.incl);
    if (!mergulhando) {
      this.pivo.quaternion.copy(q);
      this.desloc.x = lerp(this.desloc.x, this.layout.x, 1 - Math.exp(-dt * 4));
      this.desloc.y = lerp(this.desloc.y, this.layout.y, 1 - Math.exp(-dt * 4));
      return;
    }

    this.aprox = lerp(this.aprox, this.aproxAlvo, 1 - Math.exp(-dt * 6));
    if (this.aproxAlvo === 0 && this.aprox < 0.003) {   // desistiu do mergulho
      this.alvo.visible = false;
      this.parallax = 1;
      this.sol.copy(this.solInicio);
      this._descerNordeste(0);
      this._zerarMergulho();
      return;
    }
    const w = suave(this.aprox);
    this.pivo.quaternion.copy(q).slerp(this.qFoco, w);
    this.desloc.x = lerp(this.layout.x, 0, w);
    this.desloc.y = lerp(this.layout.y, 0, w);
    this.dist = lerp(this.layout.dist, DIST_TROCA, w);
    this.sol.copy(this.solInicio).lerp(SOL_DESTINO, w).normalize();
    this.parallax = 1 - w;
    this._descerNordeste(w);
    if (Math.abs(this.aprox - this.aproxAvisado) > 0.002) {
      this.aproxAvisado = this.aprox;
      this.aoAproximar(this.aprox);
    }
    if (this.aproxAlvo >= 1 && this.aprox > 0.985) {
      const { lat, lon } = this.foco;
      this.modo = 'viagem';
      this.aoEntrar(lat, lon);
    }
  }

  _aplicarCamera() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const ix = this.mouseSuave.x * 3 * GRAU * this.parallax;
    const iy = this.mouseSuave.y * 2 * GRAU * this.parallax;
    const d = this.dist;
    this.camera.position.set(d * Math.sin(ix) * Math.cos(iy), d * Math.sin(iy), d * Math.cos(ix) * Math.cos(iy));
    this.camera.lookAt(0, 0, 0);
    this.camera.setViewOffset(w, h, this.desloc.x * w, this.desloc.y * h, w, h);
    this.camera.updateMatrixWorld();
  }

  _atualizarMira() {
    const p = this.modo === 'livre' && this.ponteiro && !this.arrastando
      ? this._pontoNaTerra(this.ponteiro.x, this.ponteiro.y)
      : null;
    this.canvas.classList.toggle('sobre-terra', !!p);
    if (!p) {
      if (this.mira.visible) { this.mira.visible = false; this.aoPairar(null); }
      return;
    }
    this.mira.visible = true;
    this.mira.position.copy(p.mundo).multiplyScalar(RAIO_MARCAS);
    this.mira.lookAt(p.mundo.clone().multiplyScalar(2));
    this.aoPairar(p, this.ponteiro.x, this.ponteiro.y);
  }
}
