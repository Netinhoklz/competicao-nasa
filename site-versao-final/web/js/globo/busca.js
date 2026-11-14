// Origem: novo no site final (não existe no site do João Pedro). Substitui as rotas /api/geocode e /api/reverse do
// app.py do JP (branch estudo-jp, 29f81f6), que iam ao Nominatim pelo Flask, por uma busca local nos 1.794 municípios
// do Nordeste (dados/busca_municipios.json, gerado por ferramentas/gerar_busca_municipios.py a partir dos dados do JP).
// Reaproveita do JP: a regra de "lat, lon" (RE_COORD do app.py), a comparação sem acento (sem() do rocacerta.js),
// a projeção da malha do painel (gerar_municipios.py) e acharMunicipio() de util.js.

import { acharMunicipio } from './util.js';

const URL_LISTA = new URL('../../dados/busca_municipios.json', import.meta.url);
const URL_MALHA = new URL('../../dados/malha_ne.json', import.meta.url);

export const UF_NOME = {
  MA: 'Maranhão', PI: 'Piauí', CE: 'Ceará', RN: 'Rio Grande do Norte', PB: 'Paraíba',
  PE: 'Pernambuco', AL: 'Alagoas', SE: 'Sergipe', BA: 'Bahia',
};

/** Sem acento, minúsculo, hífen vira espaço, espaços simples: "Olho-d'Água " -> "olho d'agua". */
export const sem = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[-–]/g, ' ').replace(/\s+/g, ' ').trim();
const UF_DE_TEXTO = Object.fromEntries(Object.entries(UF_NOME).flatMap(([s, n]) => [[s.toLowerCase(), s], [sem(n), s]]));

// "-4.97, -39.01" ou "-4.97 -39.01" ou "-4.97; -39.01" (decimal com ponto), como no app.py do JP
const RE_COORD = /^\s*(-?\d{1,2}(?:\.\d+)?)\s*[,;\s]\s*(-?\d{1,3}(?:\.\d+)?)\s*$/;

let lista = null;
/** Lista dos municípios, baixada uma vez: { lista: [{cod, nome, uf, lat, lon, bbox, chave}], m: {cod: [nome, uf, lat, lon]} }. */
export function carregar() {
  lista ??= fetch(URL_LISTA)
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
    .then((d) => ({
      lista: d.municipios.map((x) => ({ ...x, chave: sem(x.nome) })),
      // mesmo formato de municipios_ne.json (nome, uf, lat, lon): util.acharMunicipio funciona sem mudança
      m: Object.fromEntries(d.municipios.map((x) => [x.cod, [x.nome, x.uf, x.lat, x.lon]])),
    }))
    .catch(() => { lista = null; return null; });
  return lista;
}

const lugarDoMunicipio = (x) => ({
  nome: x.nome, detalhe: `${UF_NOME[x.uf]} · IBGE ${x.cod}`, lat: x.lat, lon: x.lon, bbox: x.bbox, tipo: 'municipio', ibge: x.cod,
});
const fmt = (v) => v.toFixed(4).replace('.', ',');

/**
 * Procura um município do Nordeste pelo nome ("Quixadá", "quixada ce", "Quixadá, Ceará", "Quixadá (CE)")
 * ou uma coordenada ("-4.97, -39.01"). Devolve uma lista de lugares (vazia se não achar); lança Error com a
 * mensagem para a pessoa quando a coordenada não existe ou a lista não carregou.
 */
export async function procurar(texto) {
  const c = texto.match(RE_COORD);
  if (c) {
    const lat = Number(c[1]), lon = Number(c[2]);
    if (!(lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180)) {
      throw new Error('Coordenada fora do globo: latitude vai de -90 a 90 e longitude de -180 a 180.');
    }
    return [{ nome: `${fmt(lat)}, ${fmt(lon)}`, detalhe: 'Coordenada informada', lat, lon, bbox: null, tipo: 'coordenada', ibge: null }];
  }
  const d = await carregar();
  if (!d) throw new Error('A lista de municípios não carregou. Recarregue a página.');
  // o estado pode vir depois de vírgula, parêntese ou barra, ou como última palavra ("quixada ce", "Juazeiro - BA")
  const partes = sem(texto).split(/\s*[,()\/]\s*/).filter(Boolean);
  let nome = partes[0] || '';
  let uf = partes.slice(1).map((p) => UF_DE_TEXTO[p]).find(Boolean) || null;
  if (!uf && partes.length === 1) {
    const m = nome.match(/^(.+) (\w\w)$/);
    if (m && UF_DE_TEXTO[m[2]] && d.lista.some((x) => x.chave.startsWith(m[1]))) { nome = m[1]; uf = UF_DE_TEXTO[m[2]]; }
  }
  if (!nome) return [];
  const nota = (x) => (x.chave === nome ? 0 : x.chave.startsWith(nome) ? 1 : x.chave.split(' ').some((p) => p.startsWith(nome)) ? 2 : x.chave.includes(nome) ? 3 : 9);
  return d.lista
    .filter((x) => (!uf || x.uf === uf) && nota(x) < 9)
    .sort((a, b) => nota(a) - nota(b) || a.nome.length - b.nome.length || a.nome.localeCompare(b.nome, 'pt-BR'))
    .slice(0, 6)
    .map((x) => ({ ...lugarDoMunicipio(x), exato: nota(x) === 0 }));
}

// ------------------------------------------------------------------ ponto -> município

// Projeção da malha do painel (malha_ne.json), a mesma de gerar_municipios.py do JP: x, y em px
const LON0 = -48.9, LAT0 = -0.9, ESCALA = 40, COS = Math.cos((9.5 * Math.PI) / 180);
let aneis = null;
/** Anéis de cada município em px, com a caixa de cada um para descartar rápido: [{cod, caixa, aneis}]. */
function malha() {
  aneis ??= fetch(URL_MALHA).then((r) => r.json()).then((g) => Object.entries(g.m).map(([cod, caminho]) => {
    const rs = caminho.split('M').filter(Boolean).map((s) => s.replace('Z', '').split('L').map((p) => p.split(' ').map(Number)));
    const xs = rs.flat().map((p) => p[0]), ys = rs.flat().map((p) => p[1]);
    return { cod, caixa: [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)], aneis: rs };
  })).catch(() => { aneis = null; return null; });
  return aneis;
}
function dentro(x, y, anel) {
  let ok = false;
  for (let i = 0, j = anel.length - 1; i < anel.length; j = i++) {
    const [xi, yi] = anel[i], [xj, yj] = anel[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) ok = !ok;
  }
  return ok;
}

/** Município que contém o ponto (malha simplificada do IBGE); na costa e nas ilhas, o de centro mais próximo. */
export async function municipioNoPonto(lat, lon) {
  const [d, g] = await Promise.all([carregar(), malha()]);
  if (!d) return null;
  const x = (lon - LON0) * COS * ESCALA, y = (LAT0 - lat) * ESCALA;
  const achou = g?.find((m) => x >= m.caixa[0] && x <= m.caixa[2] && y >= m.caixa[1] && y <= m.caixa[3]
    && m.aneis.reduce((n, a) => n + (dentro(x, y, a) ? 1 : 0), 0) % 2 === 1);
  const cod = achou?.cod || acharMunicipio(d, { lat, lon });
  return cod ? d.lista.find((m) => m.cod === cod) : null;
}
