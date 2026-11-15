// QUADRA, extra "o que é?" (ponto 2 do desafio): as palavras técnicas em linguagem da roça, com um exemplo do próprio município.
//   termo(chave, texto) → a palavra com sublinhado pontilhado; tocar abre um balão pequeno (Enter/Espaço no teclado; Esc ou tocar fora fecha).
//   instalar(ctx)       → liga os ouvintes uma vez só (delegados) e guarda o ctx do passo para os exemplos; pode ser chamado a cada render.
//   lista(ctx)          → o glossário inteiro, para um verMais.   default.render(el, ctx, opcoes) → a lista dentro de um verMais.
// Números do exemplo: ctx.r (API) e dados/glossario_mun.json (ferramentas/preparar_glossario.py: ET0 do POWER, veranico do IMERG,
// noite mais fria do ERA5, verde do MODIS). O JSON (~90 KB) só é baixado no 1º balão aberto ou quando a lista abre; até lá (ou sem ele),
// os termos que dependem dele mostram só a definição.
import * as U from "../comum.js";

const URL_DADOS = new URL("../../dados/glossario_mun.json", import.meta.url); // vale para roca.html e para as páginas de teste
const MES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
const POWER = "NASA POWER, climatologia do município (célula do ponto interno)";

let dados = null, pedido = null, ctxAtual = null, instalado = false, aberto = null, largura = 0;

/** Busca o JSON dos municípios uma vez (null se faltar). */
export function carregar() {
  return (pedido ||= fetch(URL_DADOS).then((r) => (r.ok ? r.json() : null)).catch(() => null).then((j) => (dados = j)));
}

/** Linha do município no JSON como objeto {campo: valor}. */
function doMunicipio(cod) {
  const v = cod && dados?.m?.[cod];
  return v ? Object.fromEntries(dados.campos.map((c, i) => [c, v[i]])) : {};
}

/** "quase 3 vezes", "mais de 2 vezes"… (frequência sem casas decimais). */
function vezes(x) {
  const n = Math.round(x);
  return `${x < n - 0.05 ? "quase " : x > n + 0.05 ? "mais de " : ""}${n} vezes`;
}

// Cada termo: nome, ícone, definição (até 2 frases) e ex(r, d, mun) → [frase, tipo do selo, fonte] ou null.
const TERMOS = {
  el_nino: {
    nome: "El Niño e ONI", icone: "onda",
    def: "Quando o mar do Pacífico esquenta, a chuva do Nordeste costuma vir fraca. O ONI diz quantos graus o mar está acima do normal: +1,5 °C ou mais é El Niño forte.",
    ex: (r, d, mun) => {
      const e = r?.este_ano, u = r?.el_nino_uf;
      if (e?.oni == null) return null;
      const forte = e.oni >= 1.5 ? ": passou de +1,5, é El Niño forte" : "";
      // a perspectiva do município (mesmo texto que o passo 5 lê); sem ela, a do estado
      const p = /nos (\d+) El Niños fortes[^(]*\([^)]*\)[^,]*, (\d+) ficaram no terço mais seco/.exec(e.perspectiva || "");
      const aqui = p ? ` Em ${mun}, ${p[2]} dos ${p[1]} El Niños fortes com dado trouxeram uma estação das mais secas.`
        : u?.media != null ? ` Nos El Niños fortes, a chuva veio fraca em ${Math.round(u.media / 10)} de cada 10 municípios ${U.esc(U.ufDe(u.uf))}.` : "";
      return [`Agora o ONI está em ${e.oni > 0 ? "+" : ""}${U.num(e.oni, 1)} °C${forte}.${aqui}`, "medido",
        `${e.texto_oni || "NOAA/CPC ONI"} ${p ? e.perspectiva : u?.definicao || ""}`];
    },
  },
  em_dez: {
    nome: "“8 em 10”, “1 em cada 10”", icone: "grafico",
    def: "Conta de anos: “8 em 10” quer dizer que, em 10 anos parecidos, aconteceu em 8. Não diz qual ano vai ser.",
    extra: () => U.dezRocas(0.8, "var(--green)", "anos"),
    ex: (r, d, mun) => {
      const i = r?.este_ano?.inicio;
      if (!i?.p10 || !i?.p90) return null;
      return [`Em ${mun}, a chuva chega entre ${U.esc(i.p10)} e ${U.esc(i.p90)} em 8 de cada 10 anos; em 1 vem antes e em 1 depois.`, "medido",
        `GPM IMERG, início da estação por município, ${i.n_anos || ""} anos até 2025`];
    },
  },
  zarc: {
    nome: "Zoneamento (ZARC)", icone: "calendario",
    def: "A tábua oficial do Ministério da Agricultura: em que dias plantar cada cultura e com que risco. Risco de 20% quer dizer que a roça quebra pelo clima em até 2 de cada 10 anos.",
    ex: (r, d, mun) => {
      const z = r?.este_ano?.zarc_primeiro;
      if (!z?.ate40) return null;
      return [`Em ${mun}, a 1ª data liberada é ${U.esc(z.ate40)} (risco até 4 em 10)${z.risco20 ? `; a de menos risco (2 em 10) começa em ${U.esc(z.risco20)}` : ""}.`,
        "medido", "MAPA, ZARC 2026/27: o 1º decêndio da estação com alguma cultura do cardápio zoneada, sequeiro"];
    },
  },
  umidade_solo: {
    nome: "Umidade do solo e anomalia", icone: "solo",
    def: "A água guardada na terra, perto da raiz. Anomalia é o quanto ela está acima ou abaixo do normal para a época.",
    ex: (r, d, mun) => {
      const s = r?.este_ano?.smap;
      if (s?.status !== "ok") return null;
      return [`Até ${U.dataBR(s.fim, true)}, a terra de ${mun} ficou em ${s.posto}º lugar entre ${s.anos} anos (1º = o mais seco): ${U.esc(s.classe)}.`,
        "medido", s.texto || "NASA SMAP L4"];
    },
  },
  evapotranspiracao: {
    nome: "Evapotranspiração", icone: "sol",
    def: "A água que a terra e a planta devolvem ao ar. Sol forte, calor e vento puxam mais.",
    ex: (r, d, mun) => {
      const c = r?.clima, chuva = c?.chuva_anual_mm;
      const et = d.et0_mm ?? (chuva && c?.aridez_P_ET0 ? chuva / c.aridez_P_ET0 : null);
      if (!et || !chuva) return null;
      const x = et / chuva;
      const comp = x >= 1.5 ? ` O ar puxa ${vezes(x)} o que cai.` : x <= 0.9 ? " Aqui chove mais do que o ar puxa." : " É quase o que cai.";
      return [`Em ${mun}, o ar puxaria uns ${U.num(Math.round(et / 10) * 10)} mm por ano, se a terra tivesse água; chove ${U.num(chuva)} mm.${comp}`,
        "medido", `${POWER}: evapotranspiração de referência (FAO-56 Penman-Monteith) e chuva por ano`];
    },
  },
  balanco_hidrico: {
    nome: "Balanço hídrico", icone: "gota",
    def: "A conta da água: a chuva que entra menos a que o sol e a planta tiram. Conta no vermelho é planta com sede.",
    ex: (r, d, mun) => {
      const n = r?.clima?.meses_umidos;
      if (n == null) return null;
      return [`Em ${mun}, ${n <= 8 ? "só " : ""}em ${U.num(n)} meses do ano a chuva cobre pelo menos metade do que o ar puxa: é quando a roça cresce.`,
        "medido", `${POWER}: meses com chuva ≥ metade da evapotranspiração de referência (período de crescimento da FAO)`];
    },
  },
  veranico: {
    nome: "Veranico", icone: "sol",
    def: "Quando a chuva já firmou e para por 10 dias ou mais no meio da estação. Se pega o milho ou o feijão na flor, a perda é grande.",
    ex: (r, d, mun) => {
      // chuva de outono e inverno do leste (estação de mar ou abr): o IMERG capta só 39–72% do medido na costa (proposta v3, B2),
      // e a conta de dias secos sai falsa (Recife daria 52 dias sem chuva). Ali não mostramos o número.
      const reg = r?.este_ano?.regime;
      if ([3, 4].includes(reg?.mes_inicio) || /litoral leste/.test(reg?.texto || "")) {
        return [`No leste, o satélite enxerga menos chuva do que cai (na costa, 4 a 7 de cada 10 mm). Em ${mun}, vale o pluviômetro e quem anota a chuva.`,
          "medido", "Proposta QUADRA v3, B2: IMERG contra 17 estações automáticas do INMET a menos de 20 km da costa leste"];
      }
      if (d.ver_anos == null || !d.ver_n) return null;
      const k = Math.round((d.ver_anos / d.ver_n) * 10);
      const freq = k === 0 ? "em menos de 1 de cada 10 anos" : `em ${k} de cada 10 anos`;
      const maior = d.ver_maior_dias >= 60 ? `Em ${d.ver_maior_ano}, ficou ${d.ver_maior_dias} dias sem voltar: aí já é seca.`
        : `O mais longo: ${d.ver_maior_dias} dias, em ${d.ver_maior_ano}.`;
      return [`Em ${mun}, ${freq} a chuva parou 10 dias ou mais. ${maior}`,
        "medido", `${dados?.fonte?.veranico || "GPM IMERG"}. Aqui: ${d.ver_anos} de ${d.ver_n} estações.`];
    },
  },
  ndvi: {
    nome: "NDVI, o verde do satélite", icone: "broto",
    def: "O verde da planta visto do satélite: vai de 0 (chão nu) a 1 (mata fechada). Quando falta água, o número cai.",
    ex: (r, d, mun) => {
      if (d.ndvi_max_x100 == null) return null;
      return [`Em ${mun}, o verde chega a ${U.num(d.ndvi_max_x100 / 100, 2)} em ${MES[d.ndvi_max_mes - 1]} e cai a ${U.num(d.ndvi_min_x100 / 100, 2)} em ${MES[d.ndvi_min_mes - 1]}.`,
        "medido", dados?.fonte?.ndvi || "NASA MODIS"];
    },
  },
  seu_olho: {
    nome: "Seu olho", icone: "lupa",
    def: "Onde o satélite não vê: vale o que você vê na roça e o que o técnico confere. O QUADRA ajuda; quem decide é você.",
    ex: () => null,
  },
  geada: {
    nome: "Risco de geada", icone: "termo",
    def: "Geada é o gelo das noites abaixo de 0 °C, que queima a folha. No Nordeste quase não há; aqui o risco é calor e veranico.",
    ex: (r, d, mun) => {
      const tq = r?.clima?.tmax_mes_mais_quente;
      if (d.tmin_c == null && tq == null) return null;
      const frio = d.tmin_c != null ? `A noite mais fria de ${mun} de 1979 a 2020: ${U.num(d.tmin_c, 0)} °C, em ${d.tmin_ano}.` : "";
      const serra = d.tmin_c != null && d.tmin_c < 10 ? " Na serra pode esfriar mais: pergunte a quem mora aí." : "";
      const calor = tq != null ? ` No mês mais quente, a tarde fica em ${U.num(tq, 0)} °C, em média.` : "";
      return [`${frio}${serra}${calor}`.trim(), "medido",
        `${dados?.fonte?.tmin || "ERA5"}. Calor: NASA POWER, média da máxima diária do mês mais quente, 2001–2024.`];
    },
  },
};
export const CHAVES = Object.keys(TERMOS);

/** O exemplo do município em HTML (ou ""). */
function exemplo(t, ctx) {
  const r = ctx?.r, cod = r?.local?.cod || ctx?.cod;
  let e = null;
  try { e = t.ex(r, doMunicipio(cod), U.esc(r?.local?.municipio || "seu município")); } catch (_) { e = null; }
  return e && e[0] ? `<p class="gl-ex">${U.ic("pino")}<span>${e[0]} ${U.selo(e[1], e[2])}</span></p>` : "";
}

const corpo = (t, ctx) => `<p class="gl-def">${U.esc(t.def)}</p>${t.extra ? t.extra() : ""}${exemplo(t, ctx)}`;

/** A palavra clicável. Chave fora da lista → só o texto. */
export function termo(chave, textoVisivel) {
  const t = TERMOS[chave], txt = U.esc(textoVisivel ?? (t ? t.nome : chave));
  if (!t) return txt;
  instalar();
  return `<span class="gl-termo" role="button" tabindex="0" data-gl="${chave}" aria-expanded="false" aria-controls="gl-balao"
    title="O que é?">${txt}</span>`;
}

/** O glossário inteiro (para um verMais). termos = subconjunto opcional de chaves, na ordem dada. */
export function lista(ctx = ctxAtual, termos = CHAVES) {
  return `<dl class="gl-lista">${termos.filter((k) => TERMOS[k]).map((k) => {
    const t = TERMOS[k];
    return `<div class="gl-item"><dt>${U.ic(t.icone)}<span>${U.esc(t.nome)}</span></dt><dd>${corpo(t, ctx)}</dd></div>`;
  }).join("")}</dl>`;
}

// ------------------------------------------------------------------------------------------------------------------ balão
function vivo() {
  let v = document.getElementById("gl-vivo");
  if (!v) {
    v = document.createElement("div");
    v.id = "gl-vivo";
    v.className = "gl-vivo";
    v.setAttribute("role", "status"); // o leitor de tela lê o balão quando ele entra
    document.body.appendChild(v);
  }
  return v;
}

function posicionar(b, alvo) {
  const r = alvo.getBoundingClientRect(), vw = document.documentElement.clientWidth, m = 16;
  const w = Math.min(340, vw - 2 * m);
  b.style.width = `${w}px`;
  const cx = r.left + r.width / 2, left = Math.min(Math.max(m, cx - w / 2), vw - m - w), h = b.offsetHeight;
  const rodape = document.querySelector(".nav-baixo")?.offsetHeight || 0; // barra fixa de baixo da jornada
  const acima = window.innerHeight - rodape - r.bottom < h + 16 && r.top > h + 16;
  b.classList.toggle("acima", acima);
  b.style.left = `${left + window.scrollX}px`;
  b.style.top = `${(acima ? r.top - h - 10 : r.bottom + 10) + window.scrollY}px`;
  b.style.setProperty("--seta", `${Math.min(Math.max(18, cx - left), w - 18)}px`);
}

function abrir(alvo) {
  const t = TERMOS[alvo.dataset.gl];
  if (!t) return;
  fechar(false);
  const v = vivo();
  v.innerHTML = `<div class="gl-balao" id="gl-balao">
    <div class="gl-cab">${U.ic(t.icone)}<b>${U.esc(t.nome)}</b><button type="button" class="gl-fechar" aria-label="Fechar">×</button></div>
    ${corpo(t, ctxAtual)}</div>`;
  const b = v.firstElementChild;
  posicionar(b, alvo);
  alvo.setAttribute("aria-expanded", "true");
  aberto = alvo;
  largura = window.innerWidth;
  if (!dados) carregar().then(() => { if (aberto === alvo && dados) abrir(alvo); }); // o JSON chegou depois: redesenha com o exemplo
}

function fechar(devolverFoco) {
  const v = document.getElementById("gl-vivo");
  if (v) v.innerHTML = "";
  if (!aberto) return;
  aberto.setAttribute("aria-expanded", "false");
  if (devolverFoco && aberto.isConnected) aberto.focus();
  aberto = null;
}

/** Liga os ouvintes (uma vez) e guarda o ctx do passo atual para os exemplos. */
export function instalar(ctx) {
  if (ctx) ctxAtual = ctx;
  if (instalado || typeof document === "undefined") return;
  instalado = true;
  document.addEventListener("click", (ev) => {
    const alvo = ev.target.closest?.(".gl-termo");
    if (alvo) { ev.preventDefault(); return aberto === alvo ? fechar(false) : abrir(alvo); }
    if (ev.target.closest?.(".gl-fechar")) fechar(true);
  });
  document.addEventListener("pointerdown", (ev) => { // tocar fora fecha (pointerdown: no iPhone o click não sobe de um <div> qualquer)
    if (aberto && !ev.target.closest?.(".gl-balao, .gl-termo")) fechar(false);
  });
  document.addEventListener("keydown", (ev) => {
    const alvo = ev.target.closest?.(".gl-termo");
    if (alvo && (ev.key === "Enter" || ev.key === " ")) { ev.preventDefault(); return aberto === alvo ? fechar(false) : abrir(alvo); }
    if (ev.key === "Escape" && aberto) fechar(true);
  });
  document.addEventListener("focusin", (ev) => { // o foco saiu para outro lugar: fecha
    if (aberto && ev.target !== aberto && !ev.target.closest?.(".gl-balao")) fechar(false);
  });
  window.addEventListener("resize", () => { if (aberto && window.innerWidth !== largura) fechar(false); }); // barra do celular não fecha
  window.addEventListener("hashchange", () => fechar(false));
}

export default {
  id: "glossario",
  /** opcoes: { titulo: texto do "ver mais", termos: [chaves] } */
  async render(el, ctx, opcoes = {}) {
    instalar(ctx);
    el.innerHTML = U.verMais('<div class="gl-corpo"></div>', opcoes.titulo || "O que quer dizer cada palavra?");
    const det = el.querySelector("details"), corpo = el.querySelector(".gl-corpo");
    const encher = () => { corpo.innerHTML = lista(ctx, opcoes.termos || CHAVES); };
    det.addEventListener("toggle", () => { // a lista só é feita (e o JSON só é pedido) quando a pessoa abre
      if (!det.open || corpo.childElementCount) return;
      encher();
      if (!dados) carregar().then(() => { if (dados) encher(); });
    });
  },
};
