// testes.js - testes das regras puras do site (static/js/util.js), rodados no Chrome sem janela.
// Resultado: JSON [{nome, ok, erro}] no <pre id="resultado">, lido por site-nasa/testes/test_js.py.
import * as U from '/static/js/util.js';

const resultados = [];
function teste(nome, fn) {
  try { fn(); resultados.push({ nome, ok: true }); } catch (e) { resultados.push({ nome, ok: false, erro: String(e?.message ?? e) }); }
}
function igual(veio, esperado, msg = '') {
  if (JSON.stringify(veio) !== JSON.stringify(esperado)) {
    throw new Error(`${msg} esperado ${JSON.stringify(esperado)}, veio ${JSON.stringify(veio)}`);
  }
}
function verdade(cond, msg) { if (!cond) throw new Error(msg); }

try {
  const [ne, mun] = await Promise.all([
    fetch('/static/data/nordeste.json').then((r) => r.json()),
    fetch('/static/data/municipios_ne.json').then((r) => r.json()),
  ]);

  // ---------------------------------------------------------------- faixas e estatistica
  teste('faixaDe: limites caem na faixa de cima', () => {
    igual(U.faixaDe(10, [20, 40]), 0);
    igual(U.faixaDe(20, [20, 40]), 1);
    igual(U.faixaDe(39.9, [20, 40]), 1);
    igual(U.faixaDe(40, [20, 40]), 2);
    igual(U.faixaDe(-5, []), 0);
  });
  teste('mediana: par, impar, nulos e vazio', () => {
    igual(U.mediana([3, 1, 2]), 2);
    igual(U.mediana([4, 1, 3, 2]), 2.5);
    igual(U.mediana([null, 5, undefined, 1]), 3);
    igual(U.mediana([null, NaN]), null);
    igual(U.mediana([]), null);
  });
  teste('naEstacao: estacao que atravessa a virada do ano (nov-fev)', () => {
    igual([10, 11, 0, 1, 2, 9].map((m) => U.naEstacao(11, m)), [true, true, true, true, false, false]);
    igual([0, 3, 4].map((m) => U.naEstacao(1, m)), [true, true, false]);
    igual(U.naEstacao(null, 0), false);
  });

  // ---------------------------------------------------------------- leituras do painel
  teste('leituraNino: conta anos secos e ignora anos sem dado', () => {
    igual(U.leituraNino([[63, 1], [66, 1], [79, 1], [105, 0]]), { n: 4, secos: 3, pct: 72.5 });
    igual(U.leituraNino([null, [120, 0], [80, 1], null]), { n: 2, secos: 1, pct: 100 });
    igual(U.leituraNino([null, null]), { n: 0, secos: 0, pct: null });
  });
  teste('leituraSolo: palavra e quantos anos foram mais secos', () => {
    igual(U.leituraSolo(null, 11), null);
    igual(U.leituraSolo(50, 0), null);
    igual(U.leituraSolo(5, 11).palavra, 'muito seco');
    igual(U.leituraSolo(20, 10), { p: 20, n: 10, k: 2, palavra: 'seco' });
    igual(U.leituraSolo(50, 12).palavra, 'normal');
    igual(U.leituraSolo(100, 11), { p: 100, n: 11, k: 11, palavra: 'úmido' });
  });

  // ---------------------------------------------------------------- geografia
  const quadrado = [[0, 0], [10, 0], [10, 10], [0, 10]];
  teste('pontoNoAnel: dentro, fora e concavo', () => {
    igual(U.pontoNoAnel(5, 5, quadrado), true);
    igual(U.pontoNoAnel(15, 5, quadrado), false);
    const ele = [[0, 0], [10, 0], [10, 3], [3, 3], [3, 10], [0, 10]];
    igual(U.pontoNoAnel(1, 8, ele), true);
    igual(U.pontoNoAnel(8, 8, ele), false);
  });
  teste('distanciaAoAnel: distancia ate a borda mais proxima', () => {
    verdade(Math.abs(U.distanciaAoAnel(5, -1, quadrado) - 1) < 1e-9, 'abaixo do quadrado');
    verdade(U.distanciaAoAnel(5, 5, quadrado) > 4.9, 'no meio');
  });

  const capitais = { 'São Luís': [-2.53, -44.30], Teresina: [-5.09, -42.80], Fortaleza: [-3.73, -38.52], Natal: [-5.79, -35.21],
    'João Pessoa': [-7.12, -34.86], Recife: [-8.05, -34.88], Maceió: [-9.67, -35.74], Aracaju: [-10.91, -37.07], Salvador: [-12.97, -38.50] };
  for (const [nome, [lat, lon]] of Object.entries(capitais)) {
    teste(`dentroDoNordeste: capital ${nome}`, () => igual(U.dentroDoNordeste(lat, lon, ne.contorno), true));
  }
  const interior = { Quixadá: [-4.97, -39.01], Petrolina: [-9.38, -40.50], 'Alcântara (MA)': [-2.37, -44.40],
    'Chapada Diamantina': [-12.56, -41.39], 'Formosa do Rio Preto': [-11.05, -45.19], Mossoró: [-5.19, -37.34],
    'Fernando de Noronha (PE, ilha)': [-3.85, -32.42] };
  for (const [nome, [lat, lon]] of Object.entries(interior)) {
    teste(`dentroDoNordeste: ${nome}`, () => igual(U.dentroDoNordeste(lat, lon, ne.contorno), true));
  }
  const fora = { Brasília: [-15.79, -47.88], 'São Paulo': [-23.55, -46.63], Belém: [-1.45, -48.50], Palmas: [-10.18, -48.33],
    'Montes Claros (MG)': [-16.73, -43.86], 'Oceano Atlântico': [-6, -30], 'Mar perto de Noronha': [-3.6, -32.1], Paris: [48.86, 2.35] };
  for (const [nome, [lat, lon]] of Object.entries(fora)) {
    teste(`fora do Nordeste: ${nome}`, () => igual(U.dentroDoNordeste(lat, lon, ne.contorno), false));
  }
  teste('dentroDoNordeste: coordenada invalida', () => {
    igual(U.dentroDoNordeste(NaN, -39, ne.contorno), false);
    igual(U.dentroDoNordeste(undefined, undefined, ne.contorno), false);
  });
  teste('todo municipio da base cai dentro do Nordeste', () => {
    const fora = Object.entries(mun.m).filter(([, m]) => m[2] != null && !U.dentroDoNordeste(m[2], m[3], ne.contorno));
    igual(fora.map(([c]) => c), []);
  });

  // ---------------------------------------------------------------- municipio do lugar
  teste('acharMunicipio: codigo IBGE da busca (7 ou 9 digitos)', () => {
    igual(U.acharMunicipio(mun, { ibge: '2311306', lat: 0, lon: 0 }), '2311306');
    igual(U.acharMunicipio(mun, { ibge: '231130605', lat: 0, lon: 0 }), '2311306');   // distrito
  });
  teste('acharMunicipio: sem codigo, o centro de cada municipio acha ele mesmo', () => {
    const cods = Object.keys(mun.m).filter((_, i) => i % 37 === 0);
    const errados = cods.filter((c) => U.acharMunicipio(mun, { lat: mun.m[c][2], lon: mun.m[c][3] }) !== c);
    igual(errados, []);
  });
  teste('acharMunicipio: longe de tudo devolve null', () => {
    igual(U.acharMunicipio(mun, { lat: -23.55, lon: -46.63 }), null);
  });

  // ---------------------------------------------------------------- easter eggs
  teste('passoKonami: sequencia completa, maiuscula e erro no meio', () => {
    let p = 0;
    for (const t of U.KONAMI.slice(0, -2)) p = U.passoKonami(p, t);
    p = U.passoKonami(p, 'B');
    p = U.passoKonami(p, 'A');
    igual(p, U.KONAMI.length);
    igual(U.passoKonami(3, 'x'), 0);
    igual(U.passoKonami(3, 'ArrowUp'), 1);   // errou mas recomecou
  });
  teste('naSombraDaTerra: atras da Terra em relacao ao Sol', () => {
    const sol = { x: 1, y: 0, z: 0 };
    igual(U.naSombraDaTerra({ x: -1.1, y: 0, z: 0 }, sol), true);
    igual(U.naSombraDaTerra({ x: -1.1, y: 0.5, z: 0.5 }, sol), true);
    igual(U.naSombraDaTerra({ x: -1.1, y: 1.2, z: 0 }, sol), false);   // atras mas fora do cilindro
    igual(U.naSombraDaTerra({ x: 1.1, y: 0, z: 0 }, sol), false);      // lado do dia
    igual(U.naSombraDaTerra({ x: 0, y: 0, z: 1.1 }, sol), false);      // terminador
  });
} catch (e) {
  resultados.push({ nome: 'carregar dados de teste', ok: false, erro: String(e?.message ?? e) });
}

document.getElementById('resultado').textContent = JSON.stringify(resultados);
