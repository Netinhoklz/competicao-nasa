// Origem: João Pedro (branch estudo-jp, 29f81f6), site-nasa/static/js/ovos.js; adaptado para o site final: three.js vem do vendor/ pelo importmap. 15/11 (pedido do José): o satélite único virou uma frota pequena (10% do tamanho antigo) com a ISS e estrelas cadentes ao fundo (os meteorinhos na Lua saíram, também a pedido dele).
// ovos.js - easter eggs do globo: satelites da NASA e a Estacao Espacial em orbita baixa (clique neles), estrelas
// cadentes ao fundo e um foguete que decola de Alcantara (MA) quando a pessoa digita "foguete" na busca ou faz o
// codigo Konami.
// Usa dois ganchos de espaco.js: aoQuadro (a cada quadro) e aoClicarAntes (clique no canvas).
// As regras puras (sombra da Terra) ficam em util.js, onde os testes alcancam.
import * as THREE from 'three';
import { latLonParaVetor } from './espaco.js';
import { naSombraDaTerra } from './util.js';

const GRAU = Math.PI / 180;
const ALCANTARA = { lat: -2.373, lon: -44.396 };   // Centro de Lancamento de Alcantara
const RAIO_CLIQUE = 28;        // px em volta do satelite que contam como clique
const RAIO_CLIQUE_TERRA = 14;  // na frente do globo o raio encolhe: o toque no municipio continua valendo
const TAM_SAT = 0.0196;        // 10% do satelite que havia aqui (0,196 de ponta a ponta das asas, em raios terrestres)
const TAM_LUZ = 0.0065;        // luz de posicao com tamanho fixo na tela (~8 px de brilho num celular)
const EY = new THREE.Vector3(0, 1, 0);
const limitar = (v, a, b) => Math.min(b, Math.max(a, v));

// Frota: r = raio da orbita (1 = raio da Terra; 1,066 ~ 420 km), incl e no = inclinacao e no ascendente em graus (sobre o
// equador da Terra no enquadramento do inicio), T = s por volta, tam = tamanho relativo, atras = rad atras do anterior.
const GRACE = 'GRACE-FO: são dois, um atrás do outro. A distância entre eles mostra a água debaixo do chão.';
const FROTA = [
  { id: 'iss', r: 1.066, incl: 51.6, no: 35, T: 46, tam: 1.6, luz: 'branca',
    recado: 'Estação Espacial Internacional: tem gente morando lá, e ela dá uma volta na Terra a cada 90 minutos.' },
  { id: 'gpm', r: 1.075, incl: 65, no: 150, T: 52, tam: 1.05, luz: 'vermelha', recado: 'GPM: mede a chuva da Terra inteira a cada 30 minutos.' },
  { id: 'grace', r: 1.085, incl: 89, no: 255, T: 58, tam: 0.6, luz: 'verde', recado: GRACE },
  { id: 'grace', r: 1.085, incl: 89, no: 255, T: 58, tam: 0.6, luz: 'verde', recado: GRACE, atras: 0.07 },
  { id: 'smap', r: 1.105, incl: 98.1, no: 85, T: 63, tam: 1.1, luz: 'vermelha', recado: 'SMAP: mede a água da terra até 5 cm, com essa antena redonda que gira.' },
  { id: 'landsat', r: 1.115, incl: 98.2, no: 205, T: 66, tam: 0.95, luz: 'vermelha', recado: 'Landsat: fotografa a Terra desde 1972 e enxerga pedaços de 30 metros.' },
  { id: 'terra', r: 1.125, incl: 98.2, no: 320, T: 69, tam: 1.15, luz: 'vermelha', recado: 'Terra (MODIS): mede o verde das plantas desde 2000, de manhã.' },
  { id: 'aqua', r: 1.135, incl: 98.2, no: 5, T: 72, tam: 1, luz: 'verde', recado: 'Aqua (MODIS): passa de tarde e mede o verde e o calor do chão.' },
];

// ------------------------------------------------------------------ pecas low poly (satelites e ISS)

// cores (sRGB)
const OURO = 0xd9a441, BRANCO = 0xeef1f4, PRATA = 0xc3cad3, CINZA = 0x8a949f, ESCURO = 0x3a4048, PAINEL = 0x2d56a8;
const PAINEL_ISS = 0xd9a24a, MALHA = 0xf0d68a;

const bloco = (w, h, d) => new THREE.BoxGeometry(w, h, d);
const tubo = (r1, r2, h, n = 8, aberto = false, giro = 0) => new THREE.CylinderGeometry(r1, r2, h, n, 1, aberto, giro);
const capsula = (r, h) => new THREE.CapsuleGeometry(r, h, 2, 8);

/** Caixa de cantos redondos (superelipsoide low poly, normais exatas): o corpo "almofada", mais fofo que um bloco. */
function almofada(w, h, d) {
  const g = new THREE.SphereGeometry(1, 12, 8);
  const p = g.attributes.position, n = g.attributes.normal;
  const f = (v, k) => Math.sign(v) * Math.abs(v) ** k;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    p.setXYZ(i, (f(x, 0.3) * w) / 2, (f(y, 0.3) * h) / 2, (f(z, 0.3) * d) / 2);
    n.setXYZ(i, f(x, 1.7) / w, f(y, 1.7) / h, f(z, 1.7) / d);
  }
  g.normalizeNormals();
  return g;
}

/** Junta as pecas {geo, cor, p, r, s} numa geometria so, com a cor em cada vertice: 1 draw call por objeto. */
function juntar(pecas) {
  const pos = [], nor = [], cor = [];
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), c = new THREE.Color();
  for (const { geo, cor: hex, p = [0, 0, 0], r = [0, 0, 0], s = [1, 1, 1] } of pecas) {
    const g = geo.index ? geo.toNonIndexed() : geo;
    g.applyMatrix4(m.compose(new THREE.Vector3(...p), q.setFromEuler(new THREE.Euler(...r)), new THREE.Vector3(...s)));
    pos.push(...g.attributes.position.array);
    nor.push(...g.attributes.normal.array);
    c.setHex(hex);
    for (let i = 0; i < g.attributes.position.count; i++) cor.push(c.r, c.g, c.b);
    g.dispose();
    geo.dispose();
  }
  const out = new THREE.BufferGeometry();
  out.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  out.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  out.setAttribute('color', new THREE.Float32BufferAttribute(cor, 3));
  return out;
}

/** Asa de paineis ao longo de Y (lado +1 ou -1): haste curta e n placas azuis. */
function asa(lado, n, larg = 0.026, comp = 0.028, y0 = 0.016) {
  const pecas = [{ geo: tubo(0.0016, 0.0016, 0.014, 5), cor: CINZA, p: [0, lado * (y0 + 0.002), 0] }];
  for (let k = 0; k < n; k++) {
    pecas.push({ geo: bloco(larg, comp, 0.0025), cor: PAINEL, p: [0, lado * (y0 + 0.009 + comp / 2 + k * (comp + 0.003)), 0] });
  }
  return pecas;
}

// Modelos: +Z aponta para a Terra (nadir), Y para a normal da orbita. Medidas soltas: a escala sai de TAM_SAT * tam.
// corpo, rotor (gira em Z) e asas (giram em Y para o Sol) dividem o material; luz = onde fica a luz de posicao.
const MODELOS = {
  iss: () => {
    const asas = [];
    for (const y of [0.098, 0.124, -0.098, -0.124]) for (const z of [1, -1]) asas.push({ geo: bloco(0.0018, 0.022, 0.074), cor: PAINEL_ISS, p: [0, y, z * 0.046] });
    return {
      corpo: [
        { geo: bloco(0.014, 0.26, 0.014), cor: PRATA },                                                    // trelica comprida
        { geo: capsula(0.016, 0.12), cor: BRANCO, p: [-0.02, 0, 0.02], r: [0, 0, Math.PI / 2] },          // modulos em fila
        { geo: capsula(0.013, 0.04), cor: BRANCO, p: [0.032, 0, 0.02] },                                   // modulos de lado
        { geo: bloco(0.016, 0.075, 0.0018), cor: PAINEL, p: [-0.09, 0, 0.02] },                            // paineis do lado russo
        { geo: bloco(0.03, 0.016, 0.002), cor: BRANCO, p: [0.022, 0.048, 0] },                             // radiadores
        { geo: bloco(0.03, 0.016, 0.002), cor: BRANCO, p: [0.022, -0.048, 0] },
      ],
      asas,                                                                                                // 4 pares dourados
      luz: [0, 0.132, 0],
    };
  },
  gpm: () => ({
    corpo: [
      { geo: almofada(0.034, 0.034, 0.046), cor: OURO },
      { geo: almofada(0.03, 0.03, 0.008), cor: BRANCO, p: [0, 0, -0.021] },                               // radiador no topo
      { geo: almofada(0.026, 0.026, 0.01), cor: PRATA, p: [0, 0, 0.024] },                                // radar de chuva
      { geo: tubo(0.016, 0.004, 0.007, 10, true), cor: BRANCO, p: [0.004, 0, -0.031], r: [-Math.PI / 2 + 0.3, 0, 0] },   // antena do GMI
      ...asa(1, 2, 0.026, 0.028, 0.017), ...asa(-1, 2, 0.026, 0.028, 0.017),
    ],
    luz: [0.012, 0.012, -0.026],
  }),
  smap: () => ({
    corpo: [
      { geo: almofada(0.028, 0.028, 0.036), cor: OURO },
      { geo: almofada(0.024, 0.024, 0.006), cor: BRANCO, p: [0, 0, -0.017] },
      ...asa(-1, 3, 0.024, 0.026, 0.014),
    ],
    rotor: [                                                                                               // antena de 6 m que gira
      { geo: tubo(0.0018, 0.0018, 0.04, 5), cor: CINZA, p: [0.008, 0, -0.035], r: [Math.PI / 2, 0, 0] },
      { geo: tubo(0.062, 0.012, 0.014, 16, true), cor: MALHA, p: [0.02, 0, -0.062], r: [Math.PI / 2, 0.55, 0, 'YXZ'] },
    ],
    luz: [0.01, 0.01, -0.021],
  }),
  grace: () => ({
    corpo: [
      { geo: tubo(0.011, 0.019, 0.016, 4, false, Math.PI / 4), cor: PRATA, r: [-Math.PI / 2, 0, 0], s: [2.5, 1, 1] },   // prisma de trapezio
      { geo: bloco(0.037, 0.0145, 0.0015), cor: PAINEL, p: [0, 0, -0.0088] },                             // celulas no teto
      { geo: tubo(0.003, 0.003, 0.006, 6), cor: OURO, p: [0.034, 0, 0.002], r: [0, 0, Math.PI / 2] },     // corneta que mede a distancia
    ],
    luz: [-0.02, 0, -0.01],
  }),
  landsat: () => ({
    corpo: [
      { geo: almofada(0.032, 0.032, 0.052), cor: PRATA },
      { geo: almofada(0.034, 0.034, 0.02), cor: OURO, p: [0, 0, -0.008] },                               // cinta dourada
      { geo: almofada(0.022, 0.02, 0.014), cor: ESCURO, p: [0.002, 0, 0.026] },                           // camera virada para a Terra
      ...asa(-1, 3, 0.026, 0.028, 0.016),
    ],
    luz: [0.011, 0.011, -0.027],
  }),
  terra: () => ({
    corpo: [
      { geo: almofada(0.036, 0.036, 0.066), cor: BRANCO },
      { geo: almofada(0.038, 0.038, 0.024), cor: OURO, p: [0, 0, 0.012] },
      { geo: almofada(0.02, 0.02, 0.012), cor: ESCURO, p: [0, 0, 0.034] },                                // MODIS
      ...asa(1, 4, 0.03, 0.026, 0.018),
    ],
    luz: [0.012, -0.012, -0.034],
  }),
  aqua: () => ({
    corpo: [
      { geo: almofada(0.032, 0.032, 0.054), cor: OURO },
      { geo: almofada(0.028, 0.028, 0.006), cor: BRANCO, p: [0, 0, -0.026] },
      { geo: tubo(0.017, 0.005, 0.007, 10, true), cor: BRANCO, p: [0, 0, -0.033], r: [-Math.PI / 2 + 0.35, 0, 0] },   // antena grande do AMSR
      ...asa(-1, 3, 0.028, 0.028, 0.016),
    ],
    luz: [0.011, 0.011, -0.028],
  }),
};

// Luz das pecas: cor por vertice, luz direcional com um brilho, e um resto de luz (da Terra) na sombra
const PECA_VERT = /* glsl */ `
varying vec3 vCor;
varying vec3 vN;
varying vec3 vMundo;
void main() {
  vCor = color;
  vN = normalize(mat3(modelMatrix) * normal);
  vec4 m = modelMatrix * vec4(position, 1.0);
  vMundo = m.xyz;
  gl_Position = projectionMatrix * viewMatrix * m;
}`;

const PECA_FRAG = /* glsl */ `
uniform vec3 luz;         // direcao da luz: o Sol
uniform float sombra;     // 0..1: dentro da sombra da Terra
varying vec3 vCor;
varying vec3 vN;
varying vec3 vMundo;
void main() {
  vec3 N = normalize(vN) * (gl_FrontFacing ? 1.0 : -1.0);
  vec3 L = normalize(luz);
  vec3 V = normalize(cameraPosition - vMundo);
  float aceso = 1.0 - sombra;
  float dif = max(dot(N, L), 0.0);
  float brilho = pow(max(dot(N, normalize(L + V)), 0.0), 24.0) * 0.45;
  // na sombra fica so a luz fraca que a Terra reflete (o contorno nao some de todo); no Sol ha tambem a luz que
  // sobe do lado de dia da Terra, e contra a luz a peca nao vira so silhueta
  vec3 cor = vCor * (vec3(0.075, 0.085, 0.1) + aceso * (0.38 + 1.35 * dif)) + brilho * aceso;
  gl_FragColor = vec4(cor, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

// Estrela cadente: um risco fino; a ponta corre ao longo dele (uv.x) e a cauda se apaga atras
const METEORO_VERT = /* glsl */ `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}`;

const METEORO_FRAG = /* glsl */ `
uniform float cabeca;   // onde esta a ponta (0..1,45; passando de 1 a cauda vai sumindo)
uniform float brilho;
uniform vec3 cor;
varying vec2 vUv;
void main() {
  float atras = cabeca - vUv.x;
  float cauda = (1.0 - smoothstep(0.0, 0.45, atras)) * step(0.0, atras);
  float fio = 1.0 - smoothstep(0.15, 1.0, abs(vUv.y * 2.0 - 1.0));
  gl_FragColor = vec4(cor * cauda * cauda * fio * brilho, 1.0);
  #include <colorspace_fragment>
}`;

/** Risco de luz da estrela cadente: somado ao fundo e escondido pela Terra e pela Lua. */
const materialRisco = (r, g, b) => new THREE.ShaderMaterial({
  vertexShader: METEORO_VERT,
  fragmentShader: METEORO_FRAG,
  uniforms: { cabeca: { value: 0 }, brilho: { value: 0 }, cor: { value: new THREE.Vector3(r, g, b) } },
  transparent: true,
  depthWrite: false,                 // com o teste de profundidade: a Terra e a Lua ficam sempre na frente
  blending: THREE.AdditiveBlending,
  side: THREE.DoubleSide,
});

/** Quadrilatero do risco: uv.x = 0 na cauda e 1 na ponta. */
function quad() {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(12), 3));
  geo.setAttribute('uv', new THREE.BufferAttribute(new Float32Array([0, 0, 0, 1, 1, 0, 1, 1]), 2));
  geo.setIndex([0, 2, 1, 2, 3, 1]);
  return geo;
}

/** Estica o risco da cauda `a` ate a ponta `b`, com meia largura `lado`. */
function esticar(geo, a, b, lado) {
  const p = geo.attributes.position;
  p.setXYZ(0, a.x - lado.x, a.y - lado.y, a.z - lado.z);
  p.setXYZ(1, a.x + lado.x, a.y + lado.y, a.z + lado.z);
  p.setXYZ(2, b.x - lado.x, b.y - lado.y, b.z - lado.z);
  p.setXYZ(3, b.x + lado.x, b.y + lado.y, b.z + lado.z);
  p.needsUpdate = true;
}

// ------------------------------------------------------------------ texturas desenhadas em canvas

function canvasTextura(w, h, desenhar) {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  desenhar(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Brilho radial (chama, fumaca e luz de posicao). */
const texturaBrilho = (centro, meio, borda) => canvasTextura(64, 64, (g) => {
  const r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  r.addColorStop(0, centro);
  r.addColorStop(0.35, meio);
  r.addColorStop(1, borda);
  g.fillStyle = r;
  g.fillRect(0, 0, 64, 64);
});

const caixa = (w, h, d, mat) => new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);

export class Ovos {
  /** @param aviso (texto) mostra um recado curto na tela */
  constructor(espaco, { aviso = () => {} } = {}) {
    this.e = espaco;
    this.aviso = aviso;
    this.foguetes = [];
    this.texChama = texturaBrilho('rgba(255,255,235,1)', 'rgba(255,180,80,0.9)', 'rgba(255,80,20,0)');
    this.texFumaca = texturaBrilho('rgba(235,235,235,0.9)', 'rgba(200,200,200,0.45)', 'rgba(180,180,180,0)');

    // luz do Sol so para o foguete (os shaders do globo e as pecas daqui calculam a propria luz)
    this.luzSol = new THREE.DirectionalLight(0xffffff, 2.6);
    this.luzAmb = new THREE.AmbientLight(0x9fb4d8, 0.45);   // luz da Terra: na sombra ainda se ve o contorno
    espaco.cena.add(this.luzSol, this.luzSol.target, this.luzAmb);
    this.sombraFoguete = 0;

    // vetores de trabalho (nada de alocar a cada quadro)
    [this._v, this._w, this._a, this._b] = Array.from({ length: 4 }, () => new THREE.Vector3());
    this._q = new THREE.Quaternion();

    this._criarFrota();
    this._criarMeteoro();

    espaco.aoQuadro = (dt, t) => this._quadro(dt, t);
    espaco.aoClicarAntes = (x, y) => this._clique(x, y);
    espaco.canvas.addEventListener('pointermove', (ev) => {
      espaco.canvas.classList.toggle('sobre-satelite', !!this._sobre(ev.clientX, ev.clientY));
    });
  }

  // ------------------------------------------------------------------ satelites e ISS

  /** Material das pecas: um por objeto (cada um tem a sua sombra), todos com o mesmo programa de shader. */
  _material() {
    return new THREE.ShaderMaterial({
      vertexShader: PECA_VERT,
      fragmentShader: PECA_FRAG,
      vertexColors: true,
      side: THREE.DoubleSide,
      uniforms: { luz: { value: this.e.sol }, sombra: { value: 0 } },
    });
  }

  _criarFrota() {
    // orbitas fixas no espaco (nao giram com a Terra), inclinadas sobre o equador do enquadramento do inicio
    const q0 = this.e._qInicio(this.e.giro, this.e.incl);
    this.orbita = new THREE.Group();
    this.e.cena.add(this.orbita);
    const brilho = (meio, borda) => new THREE.SpriteMaterial({
      map: texturaBrilho('rgba(255,255,255,1)', meio, borda),
      blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, sizeAttenuation: false,
    });
    const luzes = {
      vermelha: brilho('rgba(255,90,70,0.9)', 'rgba(255,40,30,0)'),
      verde: brilho('rgba(90,255,140,0.85)', 'rgba(30,255,90,0)'),
      branca: brilho('rgba(220,235,255,0.85)', 'rgba(200,220,255,0)'),
    };
    let anterior = null;
    this.frota = FROTA.map((d) => {
      const modelo = MODELOS[d.id]();
      const mat = this._material();
      const g = new THREE.Group();
      const s = { ...d, g, mat, sombra: 0, fase: Math.random() * 2, pisca: 1.2 + Math.random() * 0.6 };
      g.add(new THREE.Mesh(juntar(modelo.corpo), mat));
      if (modelo.rotor) g.add(s.rotor = new THREE.Mesh(juntar(modelo.rotor), mat));
      if (modelo.asas) g.add(s.asas = new THREE.Mesh(juntar(modelo.asas), mat));
      const medida = new THREE.Box3().setFromObject(g).getSize(this._v);
      const escala = (TAM_SAT * d.tam) / Math.max(medida.x, medida.y, medida.z);
      g.scale.setScalar(escala);
      // luz de posicao piscando: e ela que denuncia o satelite quando ele passa pela sombra da Terra
      s.luz = new THREE.Sprite(luzes[d.luz]);
      s.luz.position.fromArray(modelo.luz);
      s.luz.scale.setScalar(TAM_LUZ / escala);      // o sprite herda a escala do grupo
      g.add(s.luz);
      // orbita: linha dos nos no equador e o plano inclinado, levados para o mundo pela orientacao do inicio
      const no = d.no * GRAU, i = d.incl * GRAU;
      s.u = new THREE.Vector3(Math.cos(no), 0, -Math.sin(no)).applyQuaternion(q0);
      s.v = new THREE.Vector3(-Math.sin(no) * Math.cos(i), Math.sin(i), -Math.cos(no) * Math.cos(i)).applyQuaternion(q0);
      g.up.crossVectors(s.u, s.v);
      s.ang = d.atras && anterior ? anterior.ang - d.atras : Math.random() * Math.PI * 2;
      anterior = s;
      this.orbita.add(g);
      return s;
    });
  }

  _quadro(dt, t) {
    const sol = this.e.sol;
    this.orbita.visible = this.e.pivo.visible;
    for (const s of this.frota) {
      s.ang += (dt * Math.PI * 2) / s.T;
      s.g.position.copy(s.u).multiplyScalar(Math.cos(s.ang) * s.r).addScaledVector(s.v, Math.sin(s.ang) * s.r);
      s.g.lookAt(0, 0, 0);                                                        // instrumentos sempre para baixo (nadir)
      // na sombra da Terra o satelite apaga (so a luz de posicao continua piscando)
      s.sombra += ((naSombraDaTerra(s.g.position, sol) ? 1 : 0) - s.sombra) * Math.min(1, dt * 3);
      s.mat.uniforms.sombra.value = s.sombra;
      s.luz.visible = (t + s.fase) % s.pisca < 0.15;
      if (s.rotor) s.rotor.rotation.z += dt * 1.5;                               // a antena do SMAP gira sem parar
      if (s.asas) {                                                               // as asas da ISS viram para o Sol
        const sl = this._v.copy(sol).applyQuaternion(this._q.copy(s.g.quaternion).invert());
        s.asas.rotation.y = Math.atan2(-sl.z, sl.x);
      }
    }
    this._meteoro(dt);
    // luz do foguete: apaga quando ele esta na sombra da Terra
    const f = this.foguetes[0];
    const noEscuro = f && naSombraDaTerra(f.g.getWorldPosition(this._v), sol) ? 1 : 0;
    this.sombraFoguete += (noEscuro - this.sombraFoguete) * Math.min(1, dt * 3);
    this.luzSol.position.copy(sol).multiplyScalar(5);
    this.luzSol.intensity = 2.6 * (1 - this.sombraFoguete);
    this.foguetes = this.foguetes.filter((f) => this._passoFoguete(f, dt));
  }

  /** O satelite sob o ponteiro (o mais perto, e que a Terra nao esconde), ou null. */
  _sobre(x, y) {
    const e = this.e;
    if (e.modo !== 'livre' || !this.orbita.visible) return null;
    const cam = e.camera.position;
    let achado = null;
    let dMin = Infinity;
    for (const s of this.frota) {
      const p = this._v.copy(s.g.position).project(e.camera);
      if (p.z > 1) continue;
      const d = Math.hypot(((p.x + 1) / 2) * window.innerWidth - x, ((1 - p.y) / 2) * window.innerHeight - y);
      if (d > RAIO_CLIQUE || d >= dMin) continue;
      const ate = this._w.copy(s.g.position).sub(cam);
      const dist = ate.length();
      ate.divideScalar(dist);
      const b = cam.dot(ate);
      const disc = b * b - (cam.lengthSq() - 1);
      if (disc > 0) {
        const tTerra = -b - Math.sqrt(disc);
        if (tTerra > 0 && tTerra < dist) continue;                               // a Terra esta na frente
        if (d > RAIO_CLIQUE_TERRA) continue;                                     // na frente do globo: raio menor
      }
      achado = s;
      dMin = d;
    }
    return achado;
  }

  _clique(x, y) {
    const s = this._sobre(x, y);
    if (!s) return false;
    this.aviso(s.recado);
    return true;
  }

  // ------------------------------------------------------------------ estrelas cadentes

  _criarMeteoro() {
    this.meteoro = new THREE.Mesh(quad(), materialRisco(0.86, 0.91, 1));
    this.meteoro.visible = false;
    this.meteoro.frustumCulled = false;
    this.e.cena.add(this.meteoro);
    this.met = { espera: 3 + Math.random() * 4, idade: 0, dur: 1 };
  }

  _meteoro(dt) {
    const e = this.e;
    const m = this.met;
    if (this.meteoro.visible) {
      m.idade += dt;
      const p = m.idade / m.dur;
      if (p >= 1) { this.meteoro.visible = false; return; }
      const u = this.meteoro.material.uniforms;
      u.cabeca.value = 1.45 * (1 - (1 - p) ** 2);
      u.brilho.value = Math.min(1, p * 8) * (1 - limitar((p - 0.6) / 0.4, 0, 1));
      return;
    }
    if (e.calmo) return;                 // prefers-reduced-motion: sem estrelas cadentes
    m.espera -= dt;
    if (m.espera > 0) return;
    m.espera = 4 + Math.random() * 6;
    if (e.modo === 'livre' && e.pivo.visible) this._lancarMeteoro();
  }

  /** Um risco de 130 a 220 px descendo na diagonal, bem no fundo (700 raios): comeca no ceu, pode passar atras da Terra. */
  _lancarMeteoro() {
    const cam = this.e.camera;
    const c = cam.position;
    const w = window.innerWidth, h = window.innerHeight, D = 700;
    const noCeu = (x, y, out) => out.set(x, y, 0.5).unproject(cam).sub(c).normalize();
    for (let k = 0; k < 8; k++) {
      const x0 = Math.random() * 1.8 - 0.9, y0 = Math.random() * 1.1 - 0.2;
      const a = noCeu(x0, y0, this._a);
      const b = c.dot(a), disc = b * b - (c.lengthSq() - 1.1 * 1.1);
      if (disc > 0 && -b - Math.sqrt(disc) > 0) continue;   // o comeco caiu sobre a Terra: sorteia outro
      const ang = -Math.PI / 2 + (Math.random() < 0.5 ? -1 : 1) * (0.5 + Math.random() * 0.6);
      const comp = 130 + Math.random() * 90;
      const fim = noCeu(x0 + (Math.cos(ang) * comp * 2) / w, y0 + (Math.sin(ang) * comp * 2) / h, this._b).multiplyScalar(D).add(c);
      a.multiplyScalar(D).add(c);
      const meio = (1.3 * D * Math.tan((cam.fov * GRAU) / 2)) / (h / 2);   // meia largura de ~1,3 px
      const lado = this._v.subVectors(fim, a).cross(this._w.subVectors(a, c)).normalize().multiplyScalar(meio);
      esticar(this.meteoro.geometry, a, fim, lado);
      this.met.idade = 0;
      this.met.dur = 0.55 + Math.random() * 0.3;
      this.meteoro.material.uniforms.brilho.value = 0;
      this.meteoro.visible = true;
      return;
    }
  }

  // ------------------------------------------------------------------ foguete

  /**
   * Foguete de dois estagios sobe de Alcantara e faz a curva para leste. Fases: ignicao com nuvem de fumaca,
   * subida, separacao do 1o estagio (cai girando e some), corte do motor e afastamento ate sumir; o rastro
   * se desfaz do mais antigo para o mais novo.
   */
  lancar() {
    if (this.foguetes.length) return;
    const n = latLonParaVetor(ALCANTARA.lat, ALCANTARA.lon, 1).normalize();
    const leste = new THREE.Vector3().crossVectors(EY, n).normalize();
    const branco = () => new THREE.MeshStandardMaterial({ color: 0xf4f6f8, metalness: 0.2, roughness: 0.5, transparent: true });
    const vermelho = () => new THREE.MeshStandardMaterial({ color: 0xd8462b, metalness: 0.2, roughness: 0.5, transparent: true });
    const basico = (m) => { m.emissive = new THREE.Color(0x222222); return m; };   // visivel mesmo no lado da noite

    const g = new THREE.Group();
    const est1 = new THREE.Group();                                               // 1o estagio + aletas
    const c1 = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.007, 0.024, 14), basico(branco()));
    c1.position.y = 0.012;
    est1.add(c1);
    for (let i = 0; i < 4; i++) {
      const aleta = caixa(0.0018, 0.011, 0.009, basico(vermelho()));
      aleta.position.set(Math.cos((i * Math.PI) / 2) * 0.0078, 0.006, Math.sin((i * Math.PI) / 2) * 0.0078);
      aleta.rotation.y = -(i * Math.PI) / 2;
      est1.add(aleta);
    }
    const est2 = new THREE.Group();                                               // 2o estagio + coifa
    const c2 = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.016, 14), basico(branco()));
    c2.position.y = 0.032;
    const bico = new THREE.Mesh(new THREE.ConeGeometry(0.006, 0.014, 14), basico(vermelho()));
    bico.position.y = 0.047;
    est2.add(c2, bico);
    const fogo = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.texChama, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
    fogo.position.y = -0.012;
    g.add(est1, est2, fogo);

    // rastro com transparencia por ponto: some do mais antigo para o mais novo
    const N = 420;
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
    geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(N * 4), 4));
    geo.setDrawRange(0, 0);
    const rastro = new THREE.Line(geo, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, depthWrite: false }));
    this.e.pivo.add(g, rastro);
    this.foguetes.push({
      g, est1, est2, fogo, rastro, n, leste, N, t: 0, k: 0, idade: new Float32Array(N),
      ant: n.clone(), vel: new THREE.Vector3(), separado: null, fumaca: [], corte: false,
    });
  }

  _posicao(f, s) {
    const h = 1.1 * s * s;
    return f.n.clone().multiplyScalar(1 + h * 0.9).addScaledVector(f.leste, 0.55 * h * h);
  }

  _passoFoguete(f, dt) {
    const ESPERA = 1.4, SUBIDA = 7, SEPARA = 0.5, AFASTA = 3.5, VIDA_RASTRO = 5;
    f.t += dt;
    const s = Math.max(0, Math.min(1, (f.t - ESPERA) / SUBIDA));
    const fimSubida = ESPERA + SUBIDA;

    // posicao: na subida segue a curva; depois do corte do motor segue em linha reta (inercia)
    let pos;
    if (f.t <= fimSubida) pos = this._posicao(f, s);
    else pos = f.g.position.clone().addScaledVector(f.vel, dt);
    if (dt > 0) f.vel.copy(pos).sub(f.ant).divideScalar(dt);
    const dir = f.vel.lengthSq() > 1e-12 ? f.vel.clone().normalize() : f.n;
    f.g.quaternion.setFromUnitVectors(EY, dir);
    f.g.position.copy(pos);
    f.ant.copy(pos);

    // chama: cresce na ignicao, encolhe depois da separacao, apaga no corte do motor
    let chama = Math.min(1, f.t / ESPERA) * (f.separado ? 0.6 : 1);
    if (f.t > fimSubida) chama *= Math.max(0, 1 - (f.t - fimSubida) / 0.5);
    f.fogo.visible = chama > 0.01;
    f.fogo.scale.setScalar((0.018 + 0.032 * chama) * (0.85 + Math.random() * 0.3));

    // nuvem de fumaca na base durante a ignicao e o comeco da subida
    if (f.t < ESPERA + 1.6 && Math.random() < 0.5) this._baforada(f, pos, dir);
    f.fumaca = f.fumaca.filter((b) => {
      b.idade += dt;
      const a = b.idade / 3.2;
      b.sp.scale.setScalar(0.02 + a * 0.07);
      b.sp.position.addScaledVector(b.deriva, dt);
      b.sp.material.opacity = 0.55 * Math.max(0, 1 - a);
      if (a < 1) return true;
      this.e.pivo.remove(b.sp);
      b.sp.material.dispose();
      return false;
    });

    // separacao do 1o estagio: solta, perde velocidade, cai para a Terra girando e some
    if (!f.separado && s >= SEPARA) {
      this.e.pivo.attach(f.est1);
      f.fogo.position.y = 0.022;
      f.separado = { vel: f.vel.clone().multiplyScalar(0.55), eixo: new THREE.Vector3(Math.random(), Math.random(), Math.random()).normalize(), idade: 0 };
    }
    if (f.separado && f.est1.parent) {
      const sep = f.separado;
      sep.idade += dt;
      sep.vel.addScaledVector(f.est1.position.clone().normalize(), -0.35 * dt);   // gravidade puxa para o centro
      f.est1.position.addScaledVector(sep.vel, dt);
      f.est1.rotateOnAxis(sep.eixo, dt * 2.2);
      const a = Math.max(0, 1 - sep.idade / 2.8);
      f.est1.traverse((o) => { if (o.material) o.material.opacity = a; });
      if (a <= 0) this._descartar(f.est1);
    }

    // rastro: um ponto por quadro na subida; cada ponto apaga com a idade
    if (f.t > ESPERA && f.t <= fimSubida && f.k < f.N) {
      f.rastro.geometry.attributes.position.setXYZ(f.k, pos.x, pos.y, pos.z);
      f.idade[f.k] = 0;
      f.k++;
      f.rastro.geometry.attributes.position.needsUpdate = true;
      f.rastro.geometry.setDrawRange(0, f.k);
    }
    const cores = f.rastro.geometry.attributes.color;
    let vivo = false;
    for (let i = 0; i < f.k; i++) {
      f.idade[i] += dt;
      const a = 0.65 * Math.max(0, 1 - f.idade[i] / VIDA_RASTRO);
      if (a > 0) vivo = true;
      cores.setXYZW(i, 0.92, 0.93, 0.95, a);
    }
    cores.needsUpdate = true;

    // depois do corte do motor o 2o estagio se afasta e some de vista
    let foguete = 1;
    if (f.t > fimSubida) foguete = Math.max(0, 1 - (f.t - fimSubida) / AFASTA);
    f.g.traverse((o) => { if (o.material && o !== f.fogo) o.material.opacity = foguete; });

    const acabou = f.t > fimSubida && foguete <= 0 && !vivo && !f.fumaca.length && !(f.separado && f.est1.parent);
    if (!acabou) return true;
    this._descartar(f.g);
    this._descartar(f.rastro);
    return false;
  }

  _baforada(f, pos, dir) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.texFumaca, depthWrite: false, transparent: true, opacity: 0.55 }));
    sp.position.copy(pos).addScaledVector(dir, -0.012);
    sp.scale.setScalar(0.02);
    this.e.pivo.add(sp);
    const lado = new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).multiplyScalar(0.02);
    f.fumaca.push({ sp, idade: 0, deriva: lado.addScaledVector(f.n, 0.004) });
  }

  _descartar(obj) {
    obj.parent?.remove(obj);
    obj.traverse((o) => {
      o.geometry?.dispose();
      if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose());
    });
  }
}
