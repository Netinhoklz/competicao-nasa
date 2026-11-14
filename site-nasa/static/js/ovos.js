// ovos.js - easter eggs do globo: um satelite em orbita baixa (clique nele) e um foguete que decola
// de Alcantara (MA) quando a pessoa digita "foguete" na busca ou faz o codigo Konami.
// Usa dois ganchos de espaco.js: aoQuadro (a cada quadro) e aoClicarAntes (clique no canvas).
// As regras puras (sombra da Terra) ficam em util.js, onde os testes alcancam.
import * as THREE from 'three';
import { latLonParaVetor } from './espaco.js';
import { naSombraDaTerra } from './util.js';

const GRAU = Math.PI / 180;
const ALCANTARA = { lat: -2.373, lon: -44.396 };   // Centro de Lancamento de Alcantara
const R_ORBITA = 1.1;          // ~640 km na escala da cena (orbita baixa, como GPM e SMAP)
const PERIODO = 60;            // s por volta
const INCL = 65 * GRAU;        // inclinacao do GPM
const RAIO_CLIQUE = 28;        // px em volta do satelite que contam como clique
const EY = new THREE.Vector3(0, 1, 0);

const RECADOS = [
  'Você achou um satélite. São eles que medem a chuva, o solo e o verde do painel.',
  'GPM: mede a chuva da Terra inteira a cada 30 minutos.',
  'SMAP: mede a água no solo, a 5 cm e na zona da raiz.',
  'MODIS: mede o verde das plantas desde 2000.',
];

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

/** Celulas solares: azul escuro com a grade prateada dos contatos. */
const texturaPainel = () => canvasTextura(256, 96, (g, w, h) => {
  g.fillStyle = '#10264a';
  g.fillRect(0, 0, w, h);
  g.strokeStyle = 'rgba(200,210,225,0.55)';
  g.lineWidth = 2;
  for (let x = 0; x <= w; x += w / 8) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); }
  for (let y = 0; y <= h; y += h / 3) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
  g.fillStyle = 'rgba(90,140,220,0.18)';
  g.fillRect(0, 0, w, h / 2);
});

/** Manta termica dourada amassada (MLI). */
const texturaManta = () => canvasTextura(128, 128, (g, w, h) => {
  g.fillStyle = '#b8892c';
  g.fillRect(0, 0, w, h);
  for (let i = 0; i < 70; i++) {
    g.fillStyle = `rgba(${Math.random() < 0.5 ? '255,226,150' : '110,74,20'},${0.15 + Math.random() * 0.25})`;
    g.beginPath();
    g.ellipse(Math.random() * w, Math.random() * h, 4 + Math.random() * 14, 2 + Math.random() * 6, Math.random() * Math.PI, 0, Math.PI * 2);
    g.fill();
  }
});

/** Brilho radial (chama e fumaca). */
const texturaBrilho = (centro, meio, borda) => canvasTextura(64, 64, (g) => {
  const r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  r.addColorStop(0, centro);
  r.addColorStop(0.35, meio);
  r.addColorStop(1, borda);
  g.fillStyle = r;
  g.fillRect(0, 0, 64, 64);
});

const metal = (cor, extra = {}) => new THREE.MeshStandardMaterial({ color: cor, metalness: 0.5, roughness: 0.45, ...extra });
const caixa = (w, h, d, mat) => new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);

export class Ovos {
  /** @param aviso (texto) mostra um recado curto na tela */
  constructor(espaco, { aviso = () => {} } = {}) {
    this.e = espaco;
    this.aviso = aviso;
    this.recado = 0;
    this.foguetes = [];
    this.texChama = texturaBrilho('rgba(255,255,235,1)', 'rgba(255,180,80,0.9)', 'rgba(255,80,20,0)');
    this.texFumaca = texturaBrilho('rgba(235,235,235,0.9)', 'rgba(200,200,200,0.45)', 'rgba(180,180,180,0)');

    // luz do Sol da cena so para os objetos dos easter eggs (os shaders do globo nao usam luzes)
    this.luzSol = new THREE.DirectionalLight(0xffffff, 2.6);
    this.luzAmb = new THREE.AmbientLight(0x9fb4d8, 0.45);   // luz da Terra: na sombra ainda se ve o contorno
    espaco.cena.add(this.luzSol, this.luzSol.target, this.luzAmb);

    // orbita inclinada fixa no espaco (nao gira com a Terra)
    this.u = new THREE.Vector3(1, 0, 0);
    this.v = new THREE.Vector3(0, Math.cos(INCL), Math.sin(INCL));
    this.normalOrbita = new THREE.Vector3().crossVectors(this.u, this.v);
    this.ang = Math.random() * Math.PI * 2;
    this.sombra = 0;
    this.sat = this._satelite();
    espaco.cena.add(this.sat);

    espaco.aoQuadro = (dt, t) => this._quadro(dt, t);
    espaco.aoClicarAntes = (x, y) => this._clique(x, y);
    espaco.canvas.addEventListener('pointermove', (ev) => {
      espaco.canvas.classList.toggle('sobre-satelite', this._sobre(ev.clientX, ev.clientY));
    });
  }

  // ------------------------------------------------------------------ satelite

  _satelite() {
    const g = new THREE.Group();
    const manta = metal(0xffffff, { map: texturaManta(), metalness: 0.75, roughness: 0.35 });
    g.add(caixa(0.026, 0.026, 0.04, manta));                                     // corpo
    const radiador = caixa(0.027, 0.002, 0.03, metal(0xe9edf1, { metalness: 0.1, roughness: 0.6 }));
    radiador.position.y = 0.014;
    g.add(radiador);
    const instrumento = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.008, 0.012, 20), metal(0x1a1d22, { roughness: 0.3 }));
    instrumento.rotation.x = Math.PI / 2;
    instrumento.position.z = 0.025;                                               // olha para a Terra (+Z depois do lookAt)
    g.add(instrumento);
    // antena parabolica num mastro
    const perfil = Array.from({ length: 9 }, (_, i) => new THREE.Vector2(0.0015 + (i / 8) * 0.011, ((i / 8) ** 2) * 0.006));
    const prato = new THREE.Mesh(new THREE.LatheGeometry(perfil, 24), metal(0xf2f4f6, { side: THREE.DoubleSide, metalness: 0.2, roughness: 0.5 }));
    prato.position.set(0, -0.026, -0.008);
    prato.rotation.x = Math.PI;
    const mastro = caixa(0.002, 0.012, 0.002, metal(0x9aa3ad));
    mastro.position.set(0, -0.018, -0.008);
    g.add(prato, mastro);
    // duas asas de paineis solares em segmentos, que giram no eixo da haste para seguir o Sol
    const matPainel = metal(0xffffff, { map: texturaPainel(), metalness: 0.35, roughness: 0.3 });
    const matVerso = metal(0x6b7480, { metalness: 0.2, roughness: 0.7 });
    this.asas = [];
    for (const lado of [-1, 1]) {
      const asa = new THREE.Group();
      asa.position.x = lado * 0.016;
      const haste = new THREE.Mesh(new THREE.CylinderGeometry(0.0009, 0.0009, 0.018, 6), metal(0xb7bec7));
      haste.rotation.z = Math.PI / 2;
      haste.position.x = lado * 0.009;
      asa.add(haste);
      for (let k = 0; k < 3; k++) {
        const seg = new THREE.Mesh(new THREE.BoxGeometry(0.026, 0.0012, 0.03), [matVerso, matVerso, matPainel, matVerso, matVerso, matVerso]);
        seg.position.x = lado * (0.031 + k * 0.0275);
        asa.add(seg);
      }
      g.add(asa);
      this.asas.push(asa);
    }
    // luz de posicao piscando: e ela que denuncia o satelite quando ele passa pela sombra da Terra
    this.luz = new THREE.Sprite(new THREE.SpriteMaterial({
      map: texturaBrilho('rgba(255,255,255,1)', 'rgba(255,90,70,0.9)', 'rgba(255,40,30,0)'),
      blending: THREE.AdditiveBlending, depthWrite: false, transparent: true,
    }));
    this.luz.position.set(0.012, 0.015, -0.019);
    this.luz.scale.setScalar(0.022);
    g.add(this.luz);
    g.up.copy(this.normalOrbita);
    g.scale.setScalar(0.85);
    return g;
  }

  _quadro(dt, t) {
    const sol = this.e.sol.clone().normalize();
    this.ang += (dt * Math.PI * 2) / PERIODO;
    const pos = this.sat.position.copy(this.u).multiplyScalar(Math.cos(this.ang) * R_ORBITA)
      .addScaledVector(this.v, Math.sin(this.ang) * R_ORBITA);
    this.sat.lookAt(0, 0, 0);                                                     // instrumento sempre para baixo (nadir)
    // paineis viram para o Sol girando no eixo da haste (X local)
    const solLocal = sol.clone().applyQuaternion(this.sat.quaternion.clone().invert());
    const giro = Math.atan2(solLocal.z, solLocal.y);
    for (const asa of this.asas) asa.rotation.x = -giro;
    // luz do Sol; na sombra da Terra o satelite apaga (so a luz de posicao continua piscando)
    this.sombra += ((naSombraDaTerra(pos, sol) ? 1 : 0) - this.sombra) * Math.min(1, dt * 3);
    this.luzSol.position.copy(pos).addScaledVector(sol, 5);
    this.luzSol.target.position.copy(pos);
    this.luzSol.intensity = 2.6 * (1 - this.sombra);
    this.luz.visible = t % 1.4 < 0.16;
    this.foguetes = this.foguetes.filter((f) => this._passoFoguete(f, dt));
  }

  /** O ponteiro esta sobre o satelite (e o satelite nao esta atras da Terra)? */
  _sobre(x, y) {
    const e = this.e;
    if (e.modo !== 'livre') return false;
    const p = this.sat.position.clone().project(e.camera);
    if (p.z > 1) return false;
    const sx = ((p.x + 1) / 2) * window.innerWidth;
    const sy = ((1 - p.y) / 2) * window.innerHeight;
    if (Math.hypot(sx - x, sy - y) > RAIO_CLIQUE) return false;
    const cam = e.camera.position;
    const ate = this.sat.position.clone().sub(cam);
    const dist = ate.length();
    ate.normalize();
    const b = cam.dot(ate);
    const disc = b * b - (cam.lengthSq() - 1);
    if (disc > 0) {
      const tTerra = -b - Math.sqrt(disc);
      if (tTerra > 0 && tTerra < dist) return false;                             // a Terra esta na frente
    }
    return true;
  }

  _clique(x, y) {
    if (!this._sobre(x, y)) return false;
    this.aviso(RECADOS[this.recado]);
    this.recado = this.recado + 1 < RECADOS.length ? this.recado + 1 : 1;
    return true;
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
