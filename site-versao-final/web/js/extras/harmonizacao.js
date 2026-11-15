// Ponto 7 do desafio (harmonizar bases de resoluções diferentes numa grade comum): "Do satélite ao seu município".
// Desenha o contorno do município (web/dados/malha_ne.json, do João Pedro) com a grade de cada base na resolução nativa, calculada
// aqui a partir do contorno, e marca o que entra no número do município. Dados: web/dados/harmonizacao.json
// (ferramentas/preparar_harmonizacao.py): células do IMERG com centro no município e a chuva média do ano em cada uma, as grades
// do SMAP, POWER e GAEZ e a tabela das bases. Só SVG, sem biblioteca.
import * as U from "../comum.js";

// projeção de malha_ne.json (a mesma de js/globo/busca.js): x = (lon − LON0)·cos(9,5°)·40, y = (LAT0 − lat)·40
const LON0 = -48.9, LAT0 = -0.9, ESC = 40, COS95 = Math.cos((9.5 * Math.PI) / 180);
const KM_LAT = 110.57, KM_LON = 111.32, KM_1KM = 0.9266; // km por grau; lado do pixel "1 km" do MODIS/VIIRS

let pedido = null;
const carregar = () => (pedido ??= Promise.all(["dados/harmonizacao.json", "dados/malha_ne.json"].map((u) =>
  fetch(u).then((r) => (r.ok ? r.json() : null)).catch(() => null))).then((v) => { if (!v[0] && !v[1]) pedido = null; return v; }));

let escolhida = "chuva"; // base escolhida: fica entre os redesenhos do passo

const BASES = [
  { id: "chuva", rot: "Chuva", icone: "chuva" },
  { id: "solo", rot: "Solo", icone: "gota" },
  { id: "clima", rot: "Clima", icone: "sol" },
  { id: "aptidao", rot: "Aptidão", icone: "semente" },
  { id: "verde", rot: "Verde", icone: "broto" },
  { id: "rocado", rot: "Seu roçado", icone: "lupa" },
];

const f = (v) => (Math.round(v * 1000) / 1000).toString();
const mil = (n) => (n >= 1500 ? `${U.num(Math.round(n / 1000))} mil` : U.num(Math.round(n / 10) * 10));

/** Contorno de malha_ne.json → anéis em [lon, lat]. */
function aneis(caminho) {
  return caminho.split("M").filter(Boolean).map((s) => s.replace(/Z/g, "").trim().split("L").map((p) => {
    const [x, y] = p.trim().split(/\s+/).map(Number);
    return [x / (COS95 * ESC) + LON0, LAT0 - y / ESC];
  }));
}

/** Projeção local em km, centrada no município, com a caixa de vista na proporção 5:4. */
function projecao(rs, ponto) {
  const pts = rs.flat().concat(ponto ? [ponto] : []);
  const lons = pts.map((p) => p[0]), lats = pts.map((p) => p[1]);
  const b = [Math.min(...lons), Math.min(...lats), Math.max(...lons), Math.max(...lats)];
  const latc = (b[1] + b[3]) / 2, lonc = (b[0] + b[2]) / 2, kx = KM_LON * Math.cos((latc * Math.PI) / 180);
  const X = (lon) => (lon - lonc) * kx, Y = (lat) => (latc - lat) * KM_LAT;
  let w = X(b[2]) - X(b[0]), h = Y(b[1]) - Y(b[3]);
  const m = Math.max(w, h) * 0.09 + 0.6;
  w += 2 * m; h += 2 * m;
  if (h / w > 0.8) w = h / 0.8; else h = w * 0.8;
  const P = { X, Y, kx, latc, w, h, vb: [-w / 2, -h / 2, w, h] };
  P.lonA = lonc - w / 2 / kx; P.lonB = lonc + w / 2 / kx; P.latA = latc - h / 2 / KM_LAT; P.latB = latc + h / 2 / KM_LAT;
  return P;
}

/** Bordas de uma grade regular (origem o, passo s) dentro de [a, b]. */
function bordas(o, s, a, b) {
  const out = [];
  for (let k = Math.ceil((a - o) / s); k <= Math.floor((b - o) / s); k++) out.push(o + k * s);
  return out;
}

/** Linhas da grade (um único <path>): lons e lats das bordas. */
function grade(P, lons, lats, cls = "hz-grade") {
  const [x0, y0, w, h] = P.vb;
  const d = lons.map((lo) => `M${f(P.X(lo))} ${f(y0)}V${f(y0 + h)}`).join("") + lats.map((la) => `M${f(x0)} ${f(P.Y(la))}H${f(x0 + w)}`).join("");
  return d ? `<path class="${cls}" d="${d}"/>` : "";
}

const celula = (P, lonW, latN, lonE, latS, cls) =>
  `<rect class="${cls}" x="${f(P.X(lonW))}" y="${f(P.Y(latN))}" width="${f(P.X(lonE) - P.X(lonW))}" height="${f(P.Y(latS) - P.Y(latN))}"/>`;

function escala(P) {
  const alvo = P.w / 4, k = [1, 2, 5, 10, 20, 50, 100].find((v) => v >= alvo * 0.6) || 100;
  const x = P.vb[0] + P.w * 0.05, y = P.vb[1] + P.h * 0.94, fs = P.w * 0.034;
  return `<g class="hz-escala"><path d="M${f(x)} ${f(y)}h${f(k)}"/><text x="${f(x)}" y="${f(y - fs * 0.6)}" font-size="${f(fs)}">${k} km</text></g>`;
}

/** Área do município em km² (anéis com sinal, regra do par-ímpar). */
function areaKm2(P, rs) {
  return Math.abs(rs.reduce((s, r) => s + r.reduce((a, p, i) => {
    const q = r[(i + 1) % r.length];
    return a + P.X(p[0]) * P.Y(q[1]) - P.X(q[0]) * P.Y(p[1]);
  }, 0) / 2, 0));
}

/** Células do IMERG do município: [{lat, lon, mm}], com a média pela regra do centro e pela área. */
function celulasImerg(H, cod) {
  const v = H?.m?.[cod];
  if (!v) return null;
  const [i0, j0, perto, mmCentro, mmArea] = v, im = H.imerg, cel = [];
  for (let k = 5; k + 2 < v.length; k += 3) {
    cel.push({ lat: im.lat0 + (i0 + v[k]) * im.passo, lon: im.lon0 + (j0 + v[k + 1]) * im.passo, mm: v[k + 2] == null ? null : v[k + 2] * 10 });
  }
  return { cel, perto: !!perto, mmCentro, mmArea };
}

// ---------------------------------------------------------------- uma camada por base
function camadaChuva(P, H, cod) {
  const im = H?.imerg, c = celulasImerg(H, cod);
  if (!im) return { svg: "" };
  const meio = im.passo / 2;
  let svg = grade(P, bordas(im.lon0 - meio, im.passo, P.lonA, P.lonB), bordas(im.lat0 - meio, im.passo, P.latA, P.latB));
  if (!c) return { svg };
  const vals = c.cel.map((x) => x.mm).filter((x) => x != null);
  let lo = Math.min(...vals), hi = Math.max(...vals);
  if (hi - lo < 100) { const m = (lo + hi) / 2; lo = m - 50; hi = m + 50; }
  const op = (mm) => (mm == null ? 0.08 : 0.16 + (0.72 * (mm - lo)) / (hi - lo));
  const r = P.w * 0.008;
  svg = c.cel.map((x) => {
    const x0 = P.X(x.lon - meio), y0 = P.Y(x.lat + meio);
    return `<rect class="hz-cel${c.perto ? " perto" : ""}" x="${f(x0)}" y="${f(y0)}" width="${f(P.X(x.lon + meio) - x0)}" height="${f(P.Y(x.lat - meio) - y0)}"
      fill-opacity="${op(x.mm).toFixed(2)}"><title>${x.mm == null ? "sem dado" : U.num(x.mm) + " mm por ano"}</title></rect>`;
  }).join("") + svg + c.cel.map((x) => `<circle class="hz-centro" cx="${f(P.X(x.lon))}" cy="${f(P.Y(x.lat))}" r="${f(r)}"/>`).join("");
  return { svg, c, min: Math.min(...vals), max: Math.max(...vals) };
}

function camadaSolo(P, H, ponto) {
  const s = H?.smap;
  if (!s) return { svg: "" };
  const lat = s.lat, lons = bordas(s.lon0 - s.dlon / 2, s.dlon, P.lonA, P.lonB);
  const meioLat = (i) => (i <= 0 ? lat[0] + (lat[0] - lat[1]) / 2 : i >= lat.length ? lat[lat.length - 1] - (lat[lat.length - 2] - lat[lat.length - 1]) / 2
    : (lat[i - 1] + lat[i]) / 2); // borda entre a linha i−1 e a i (latitudes do norte para o sul)
  const lats = [];
  for (let i = 0; i <= lat.length; i++) { const b = meioLat(i); if (b >= P.latA && b <= P.latB) lats.push(b); }
  let svg = grade(P, lons, lats);
  if (ponto) {
    let i = 0;
    lat.forEach((v, k) => { if (Math.abs(v - ponto[1]) < Math.abs(lat[i] - ponto[1])) i = k; });
    const j = Math.round((ponto[0] - s.lon0) / s.dlon), lonc = s.lon0 + j * s.dlon;
    svg += celula(P, lonc - s.dlon / 2, meioLat(i), lonc + s.dlon / 2, meioLat(i + 1), "hz-usada");
  }
  return { svg };
}

function camadaRegular(P, ponto, dlon, dlat, oLon, oLat, centrada) {
  let svg = grade(P, bordas(oLon, dlon, P.lonA, P.lonB), bordas(oLat, dlat, P.latA, P.latB));
  if (ponto) {
    const [lon, lat] = ponto;
    const w = centrada ? Math.round(lon / dlon) * dlon - dlon / 2 : oLon + Math.floor((lon - oLon) / dlon) * dlon;
    const s = centrada ? Math.round(lat / dlat) * dlat - dlat / 2 : oLat + Math.floor((lat - oLat) / dlat) * dlat;
    svg += celula(P, w, s + dlat, w + dlon, s, "hz-usada");
  }
  return { svg };
}

function camadaVerde(P) {
  const passo = 1 / 120, pxKm = 360 / P.w; // ~px por km a 360 px de largura
  if (pxKm < 1.4) return { svg: `<rect class="hz-nevoa" x="${f(P.vb[0])}" y="${f(P.vb[1])}" width="${f(P.w)}" height="${f(P.h)}"/>`, fino: true };
  return { svg: grade(P, bordas(0, passo, P.lonA, P.lonB), bordas(0, passo, P.latA, P.latB), "hz-grade fina") };
}

function svgMunicipio(P, rs, camada, ponto, rotulo) {
  const d = rs.map((r) => "M" + r.map((p) => `${f(P.X(p[0]))} ${f(P.Y(p[1]))}`).join("L") + "Z").join("");
  const pino = ponto ? `<circle class="hz-ponto" cx="${f(P.X(ponto[0]))}" cy="${f(P.Y(ponto[1]))}" r="${f(P.w * 0.014)}"/>` : "";
  return `<svg class="hz-svg" viewBox="${P.vb.map(f).join(" ")}" role="img" aria-label="${U.esc(rotulo)}">
    <defs><clipPath id="hz-corte"><rect x="${f(P.vb[0])}" y="${f(P.vb[1])}" width="${f(P.w)}" height="${f(P.h)}"/></clipPath></defs>
    <g clip-path="url(#hz-corte)"><path class="hz-fundo" d="${d}" fill-rule="evenodd"/>${camada}</g>
    <path class="hz-contorno" d="${d}" fill-rule="evenodd"/>${pino}${escala(P)}</svg>`;
}

/** Zoom no roçado: grade de 30 m, de 70 m e as pegadas de 25 m, em metros. Posição ilustrativa. */
function svgRocado(ha) {
  const lado = Math.sqrt(ha * 1e4), W = Math.max(360, Math.ceil((lado * 2.4) / 70) * 70), H = W * 0.8;
  const lin = (s) => bordas(0, s, 0, W).map((x) => `M${f(x)} 0V${f(H)}`).join("") + bordas(0, s, 0, H).map((y) => `M0 ${f(y)}H${f(W)}`).join("");
  const x0 = (W - lado) / 2, y0 = (H - lado) / 2;
  const pegadas = [];
  for (let t = 30; t < W * 1.2; t += 60) { const x = W * 0.42 + t * 0.6, y = H - t * 0.8; if (x < W - 10 && y > 10) pegadas.push([x, y]); }
  const fs = W * 0.034, k = W > 700 ? 200 : 100;
  return `<svg class="hz-svg" viewBox="0 0 ${f(W)} ${f(H)}" role="img" aria-label="Seu roçado visto pelos satélites mais finos">
    <path class="hz-grade l30" d="${lin(30)}"/><path class="hz-grade e70" d="${lin(70)}"/>
    ${pegadas.map(([x, y]) => `<circle class="hz-gedi" cx="${f(x)}" cy="${f(y)}" r="12.5"/>`).join("")}
    <rect class="hz-roca" x="${f(x0)}" y="${f(y0)}" width="${f(lado)}" height="${f(lado)}"/>
    <g class="hz-escala"><path d="M${f(W * 0.05)} ${f(H * 0.94)}h${k}"/><text x="${f(W * 0.05)}" y="${f(H * 0.94 - fs * 0.6)}" font-size="${f(fs)}">${k} m</text></g></svg>`;
}

// ---------------------------------------------------------------- textos (frente) e tabela (ver mais)
function frente(id, ctx, P, cam, area) {
  const { r, ef } = ctx, mun = U.esc(r.local.municipio), lat = r.local.lat ?? -5;
  const kmLon = (g) => Math.round(g * KM_LON * Math.cos((lat * Math.PI) / 180)), kmLat = (g) => Math.round(g * KM_LAT);
  const src = {
    chuva: "GPM IMERG V07 via NASA POWER, 0,1°; chuva média do ano 1998–2025 em cada célula; entra a célula com o centro no município",
    solo: "NASA SMAP L4 (SPL4SMGP v008), EASE-Grid 2.0 de 9 km; o 'solo hoje' usa a célula mais perto do centro do município",
    clima: "NASA POWER, grade de 0,5° × 0,625°; o clima do município é a célula que contém o centro",
    aptidao: "FAO GAEZ v4, grade de 5′ (clima 1981–2010); a aptidão é a célula que contém o centro",
    verde: "MODIS (MOD13Q1 250 m, MOD13A1 500 m) e VIIRS (VNP13A3 1 km); o desenho é uma grade de 30″ ≈ 1 km",
    rocado: "Tamanho do roçado: sua resposta (ou o padrão do Censo 2017). Posição e trilha ilustrativas; tamanhos: Landsat 8/9 30 m, ECOSTRESS 70 m, GEDI 25 m",
  }[id];
  if (id === "chuva") {
    const c = cam.c;
    if (!c) return { val: "11", un: "km de lado", frase: "Cada quadradinho do satélite da chuva tem 11 km de lado.", selo: U.selo("medido", src) };
    const n = c.cel.length, costa = /litoral leste/.test(r.este_ano?.regime?.texto || "");
    // a outra base de chuva do site (NASA POWER, clima do município) discorda em mais de 25%: o pluviômetro desempata
    const power = r.clima?.chuva_anual_mm, difere = power && c.mmCentro && Math.abs(c.mmCentro - power) / power > 0.25;
    const aviso = difere ? `Outra base dá ${U.num(power)} mm. Confira no seu pluviômetro.`
      : costa ? "No litoral, o satélite mede menos chuva que o pluviômetro." : "";
    return {
      val: U.num(n), un: n === 1 ? "quadradinho de 11 km" : "quadradinhos de 11 km",
      frase: c.perto ? `Menor que um quadradinho: usamos o mais perto do centro (${U.num(c.mmCentro)} mm por ano).`
        : `A média deles é a chuva de ${mun}: ${U.num(c.mmCentro)} mm por ano.`,
      legenda: (n > 1 && cam.max > cam.min ? `<span class="hz-rampa"><i></i>de ${U.num(cam.min)} a ${U.num(cam.max)} mm, conforme o quadradinho</span>` : "")
        + (c.perto ? `<span><i class="hz-ch-perto"></i>o mais perto do centro</span>` : `<span><i class="hz-ch-centro"></i>centro dentro: entra na média</span>`)
        + (aviso ? `<span class="hz-aviso">${U.ic("alerta")}${aviso}</span>` : ""),
      selo: U.selo("medido", src),
    };
  }
  if (id === "solo") return { val: "9", un: "km de lado", frase: "O solo de hoje vem do quadradinho do centro, o marcado.",
    legenda: `<span><i class="hz-ch-usada"></i>quadradinho usado</span><span><i class="hz-ch-ponto"></i>centro do município</span>`, selo: U.selo("medido", src) };
  if (id === "clima") return { val: `${kmLat(0.5)} × ${kmLon(0.625)}`, un: "km", frase: "Calor e secura do ar vêm do quadradão que contém o centro.",
    legenda: `<span><i class="hz-ch-usada"></i>quadradão usado</span><span><i class="hz-ch-ponto"></i>centro do município</span>`, selo: U.selo("medido", src) };
  if (id === "aptidao") return { val: "9", un: "km de lado", frase: "O que a terra aceita vem do quadradinho do centro, no mapa da FAO.",
    legenda: `<span><i class="hz-ch-usada"></i>quadradinho usado</span><span><i class="hz-ch-ponto"></i>centro do município</span>`, selo: U.selo("medido", src) };
  if (id === "verde") return { val: "1", un: "km de lado",
    frase: area ? `Grade fina: uns ${mil(area / (KM_1KM * KM_1KM))} quadradinhos cobrem ${mun}.` : "Grade fina: o verde da planta é visto quilômetro a quilômetro.",
    legenda: cam.fino ? `<span>fino demais para desenhar um a um nesta escala</span>` : "", selo: U.selo("medido", src) };
  const ha = Math.max(0.1, +ef?.ha || 1), n30 = Math.max(1, Math.round((ha * 1e4) / 900));
  const haImerg = KM_LAT * 0.1 * KM_LON * 0.1 * Math.cos((lat * Math.PI) / 180) * 100;
  return { val: U.num(n30), un: n30 === 1 ? "pontinho de 30 m" : "pontinhos de 30 m", sub: `no seu roçado de ${U.esc(U.ha(ha))}`,
    frase: `No quadradinho da chuva cabem ${mil(haImerg / ha)} roçados. O seu, só você conhece.`,
    legenda: `<span><i class="hz-ch-roca"></i>seu roçado</span><span><i class="hz-ch-l30"></i>30 m: vê o roçado</span>`
      + `<span><i class="hz-ch-e70"></i>70 m: calor da planta</span><span><i class="hz-ch-gedi"></i>25 m: altura da mata</span>`
      + `<span class="chip">fora do site: passam pouco e pesam muito</span>`,
    selo: U.selo("suposicao", src) };
}

function tabela(H, ctx, c, naTela) {
  const r = ctx.r, conf = H?.imerg?.conferencia;
  const onde = { tela: ["verde", "Sim"], repo: ["", "Nos estudos"], fora: ["terra", "Não"] };
  const linhas = (H?.bases || []).map((b) => {
    const o = naTela.has(b.id) && b.onde === "repo" ? "tela" : b.onde, [cor, txt] = onde[o] || onde.repo;
    return `<li><div class="hz-b-cab"><b>${U.esc(b.base)}</b><span class="chip ${cor}">${txt}</span></div>
      <div class="hz-b-meta">${U.esc(b.grade)} · ${U.esc(b.periodo)}</div>
      <div>${U.esc(b.municipio)}. <span class="sub">${U.esc(b.porque)}.</span></div></li>`;
  }).join("");
  const aqui = c && c.mmArea ? Math.abs(c.mmCentro - c.mmArea) / c.mmArea * 100 : null;
  const power = r.clima?.chuva_anual_mm;
  return `<p>O município é a grade comum: é nele que estão a colheita (IBGE), o Censo e o zoneamento (ZARC).
      Cada base: grade nativa, período, como vira número do município e se está no site.</p>
    <ul class="hz-tabela">${linhas}</ul>
    <ul class="hz-notas">
      ${conf ? `<li><b>Conferência da chuva.</b> Pesar cada quadradinho pela área dentro do município, em vez de contar só os de centro dentro,
        muda a chuva do ano em ${U.num(conf.mediana_pct, 1)}% no município típico (95% dos ${U.num(conf.n)} abaixo de ${U.num(conf.p95_pct, 1)}%;
        o pior, ${U.num(conf.max_pct, 1)}%)${aqui != null ? `. Aqui: ${U.num(aqui, 1)}% (${U.num(c.mmCentro)} × ${U.num(c.mmArea)} mm)` : ""}.
        ${U.num(conf.sem_centro)} municípios menores que um quadradinho usam o mais perto do centro.</li>` : ""}
      ${power && c ? `<li><b>A mesma chuva em duas grades.</b> IMERG (0,1°, média do município): ${U.num(c.mmCentro)} mm por ano; NASA POWER
        (o quadradão de 0,5°): ${U.num(power)} mm. Por isso cada número diz de que base veio.</li>` : ""}
      <li><b>Até onde o detalhe vale</b> (medido no Ceará: duas fontes independentes concordam com r ≥ 0,8). Solo do SMAP: diz <i>quando</i> a 9 km
        (r 0,89 com o SMAP L3 em cada célula) e <i>onde</i> a partir de 36 km (r 0,82). Verde: 25 km na estação das chuvas (VIIRS × MODIS, r 0,85;
        0,42 a 1 km). Chuva do IMERG contra o solo do SMAP L3: não chega a 0,8 nem a 88 km (0,63), então vale para o ano e a região.</li>
      <li><b>No litoral leste</b> (até ~20 km do mar), o IMERG capta só 39–72% da chuva dos pluviômetros do INMET; ali, as datas vêm do ZARC.</li>
      <li><b>Solo.</b> Não usamos mapa de solo. O ZARC dá o risco por tipo de terra (1 arenoso, 2 médio, 3 argiloso) e, no milho, no feijão comum
        e no girassol, por água disponível (AD1 a AD6). A sua resposta escolhe a classe: arenosa → tipo 1 e AD2; misturada → tipo 2 e AD3;
        barro → tipo 3 e AD5; baixio → AD5 (suposição). "Não sei" = a janela que vale em todas.</li>
      <li><b>As finas ficam fora.</b> Landsat (30 m) vê o roçado, mas a nuvem da estação das chuvas o esconde em boa parte das datas, e o volume
        para 1.794 municípios é grande: usamos só 4 áreas de teste no Ceará. ECOSTRESS (70 m) passa em dias e horas irregulares, porque vai
        na estação espacial. GEDI (25 m) dá tiros soltos em trilhas e mede a altura da mata, não a roça.</li>
    </ul>`;
}

export default {
  id: "harmonizacao",
  async render(el, ctx, opcoes = {}) {
    const { r } = ctx;
    const naTela = new Set(opcoes.naTela || []);
    if (opcoes.base && BASES.some((b) => b.id === opcoes.base) && ctx.entrou) escolhida = opcoes.base;
    el.innerHTML = `<div class="painel hz"><h3>Do satélite ao seu município</h3><p class="sub pequeno">Carregando o mapa…</p></div>`;
    const [H, malha] = await carregar();
    const cod = String(r.local.cod), caminho = malha?.m?.[cod];
    const ponto = Number.isFinite(r.local.lon) && Number.isFinite(r.local.lat) ? [r.local.lon, r.local.lat] : null;
    const rs = caminho ? aneis(caminho) : null;
    const P = rs ? projecao(rs, ponto) : null;
    const area = P ? areaKm2(P, rs) : 0;
    const cImerg = celulasImerg(H, cod);

    const desenhar = () => {
      const id = escolhida;
      let cam = { svg: "" }, mapa;
      if (id === "rocado") mapa = svgRocado(Math.max(0.1, +ctx.ef?.ha || 1));
      else if (P) {
        if (id === "chuva") cam = camadaChuva(P, H, cod);
        else if (id === "solo") cam = camadaSolo(P, H, ponto);
        else if (id === "clima") cam = camadaRegular(P, ponto, H?.power?.dlon ?? 0.625, H?.power?.dlat ?? 0.5, -0.3125, -0.25, true);
        else if (id === "aptidao") cam = camadaRegular(P, ponto, H?.gaez?.passo ?? 1 / 12, H?.gaez?.passo ?? 1 / 12, -180, 90, false);
        else cam = camadaVerde(P);
        mapa = svgMunicipio(P, rs, cam.svg, ponto, `${r.local.municipio} e a grade de ${BASES.find((b) => b.id === id).rot.toLowerCase()}`);
      } else mapa = `<p class="sub pequeno hz-sem">O contorno do município não carregou agora.</p>`;
      const t = frente(id, ctx, P, cam, area);
      return { mapa, t };
    };

    const pintar = () => {
      const { mapa, t } = desenhar();
      el.innerHTML = `<div class="painel hz">
        <h3>Do satélite ao seu município ${t.selo}</h3>
        <div class="hz-corpo">
          <div class="hz-mapa">${mapa}</div>
          <div class="hz-lado">
            <div class="hz-bases" role="group" aria-label="Escolha o que o satélite mede">${BASES.map((b) =>
              `<button type="button" data-base="${b.id}" aria-pressed="${b.id === escolhida}">${U.ic(b.icone)}<span>${b.rot}</span></button>`).join("")}</div>
            <div class="hz-num"><span class="numero-grande">${t.val}<small>${U.esc(t.un)}</small></span>${t.sub ? `<span class="sub">${t.sub}</span>` : ""}</div>
            <p class="hz-frase">${t.frase}</p>
            ${t.legenda ? `<div class="hz-legenda">${t.legenda}</div>` : ""}
          </div>
        </div>
        <p class="hz-junta">${U.ic("faixas")}Cada satélite vê em quadradinhos de um tamanho. Juntamos tudo no seu município.</p>
        ${H ? U.verMais(tabela(H, ctx, cImerg, naTela), "Ver todas as bases e como juntamos") : ""}
      </div>`;
      el.querySelectorAll(".hz-bases button").forEach((b) => b.addEventListener("click", () => {
        escolhida = b.dataset.base;
        const aberto = el.querySelector("details.ver-mais")?.open;
        pintar();
        if (aberto) el.querySelector("details.ver-mais").open = true;
        el.querySelector(`.hz-bases button[data-base="${escolhida}"]`)?.focus();
      }));
    };
    pintar();
  },
};
