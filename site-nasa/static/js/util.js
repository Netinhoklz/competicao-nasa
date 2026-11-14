// util.js - regras puras do site (sem DOM, sem three.js): usadas pelas paginas e pelos testes
// (site-nasa/testes/js/). Coordenadas em graus; anel = [[lon, lat], ...].

/** Indice da faixa de `v` dados os cortes crescentes (0 = abaixo do primeiro corte). */
export function faixaDe(v, cortes) {
  let k = 0;
  while (k < cortes.length && v >= cortes[k]) k++;
  return k;
}

/** Mediana ignorando nulos; null se nao sobrar nada. */
export function mediana(xs) {
  const s = xs.filter((x) => x != null && Number.isFinite(x)).sort((a, b) => a - b);
  if (!s.length) return null;
  const k = s.length >> 1;
  return s.length % 2 ? s[k] : (s[k - 1] + s[k]) / 2;
}

/** O mes `mes0` (0 = jan) cai na estacao de 4 meses que comeca em `ini` (1 = jan)? Atravessa a virada do ano. */
export function naEstacao(ini, mes0) {
  return ini != null && (mes0 - (ini - 1) + 12) % 12 < 4;
}

/** El Nino forte: analogos = [[pct do normal, seco 0/1] | null, ...] -> anos com dado, anos secos e mediana. */
export function leituraNino(analogos) {
  const val = analogos.filter(Boolean);
  return { n: val.length, secos: val.filter((a) => a[1]).length, pct: mediana(val.map((a) => a[0])) };
}

/** Solo (SMAP): percentil do mes entre `n` anos anteriores -> quantos foram mais secos e uma palavra. */
export function leituraSolo(pctl, n) {
  if (pctl == null || !n) return null;
  const k = Math.round((pctl / 100) * n);
  const palavra = pctl < 10 ? 'muito seco' : pctl < 34 ? 'seco' : pctl < 67 ? 'normal' : 'úmido';
  return { p: pctl, n, k, palavra };
}

// ------------------------------------------------------------------ geografia

/** Ponto dentro do anel (regra par-impar). */
export function pontoNoAnel(lon, lat, anel) {
  let dentro = false;
  for (let i = 0, j = anel.length - 1; i < anel.length; j = i++) {
    const [xi, yi] = anel[i];
    const [xj, yj] = anel[j];
    if ((yi > lat) !== (yj > lat) && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) dentro = !dentro;
  }
  return dentro;
}

/** Menor distancia (graus, longitude corrigida pela latitude) do ponto ate a borda do anel. */
export function distanciaAoAnel(lon, lat, anel) {
  const k = Math.cos((lat * Math.PI) / 180);
  let min = Infinity;
  for (let i = 0, j = anel.length - 1; i < anel.length; j = i++) {
    const ax = anel[j][0] * k, ay = anel[j][1], bx = anel[i][0] * k, by = anel[i][1];
    const px = lon * k, py = lat;
    const dx = bx - ax, dy = by - ay;
    const t = dx || dy ? Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy))) : 0;
    min = Math.min(min, Math.hypot(px - (ax + t * dx), py - (ay + t * dy)));
  }
  return min;
}

/** Ilhas oceanicas do Nordeste que o contorno simplificado deixa de fora: [oeste, sul, leste, norte]. */
export const ILHAS_NE = [
  [-32.50, -3.95, -32.35, -3.80],   // Fernando de Noronha (PE), municipio 2605459
  [-33.85, -3.90, -33.78, -3.84],   // Atol das Rocas (RN)
];

/**
 * O lugar fica no Nordeste? `contorno` = lista de aneis do IBGE simplificados a 0,02 grau; a `folga`
 * (graus) aceita cidades da costa que a simplificacao deixou um pouco para fora (Fortaleza, Recife...).
 */
export function dentroDoNordeste(lat, lon, contorno, folga = 0.12) {
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return false;
  if (ILHAS_NE.some(([o, s, l, n]) => lon >= o && lon <= l && lat >= s && lat <= n)) return true;
  return contorno.some((anel) => pontoNoAnel(lon, lat, anel) || distanciaAoAnel(lon, lat, anel) <= folga);
}

/** Codigo IBGE do municipio do lugar: o da busca, se houver; senao o de centro mais proximo ate `distMax` graus. */
export function acharMunicipio(d, lugar, distMax = 0.6) {
  const cod = String(lugar.ibge || '').slice(0, 7);
  if (d.m[cod]) return cod;
  const cos = Math.cos((lugar.lat * Math.PI) / 180);
  let melhor = null;
  let dMin = distMax;
  for (const [c, m] of Object.entries(d.m)) {
    if (m[2] == null) continue;
    const dist = Math.hypot(m[2] - lugar.lat, (m[3] - lugar.lon) * cos);
    if (dist < dMin) { dMin = dist; melhor = c; }
  }
  return melhor;
}

// ------------------------------------------------------------------ easter eggs

export const KONAMI = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

/** Avanca o codigo Konami: devolve o novo passo (KONAMI.length = completo). */
export function passoKonami(passo, tecla) {
  const t = tecla.length === 1 ? tecla.toLowerCase() : tecla;
  if (t === KONAMI[passo]) return passo + 1;
  return t === KONAMI[0] ? 1 : 0;
}

/**
 * Um ponto em orbita esta na sombra da Terra (raio 1, centro na origem)? `sol` = direcao do Sol (unitaria).
 * Sombra cilindrica: atras da Terra em relacao ao Sol e a menos de 1 raio do eixo Terra-Sol.
 */
export function naSombraDaTerra(pos, sol) {
  const d = pos.x * sol.x + pos.y * sol.y + pos.z * sol.z;
  if (d >= 0) return false;
  const r2 = pos.x * pos.x + pos.y * pos.y + pos.z * pos.z - d * d;
  return r2 < 1;
}
