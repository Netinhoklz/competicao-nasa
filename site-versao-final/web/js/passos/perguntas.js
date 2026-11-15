// Passo 2, "Sua roça": uma tela só, com as linhas já marcadas com o comum daqui (o que planta, tamanho, terra, baixio, maniva e o ano
// passado). Cada toque muda só o rascunho da tela: não grava, não chama a API e não avança. O primário da barra ("Ver o meu plano →",
// ou "Voltar a <passo> →" para quem veio de um "mudar") grava uma vez só, e só as linhas tocadas.
// Ordem de serviço: analise/fluxo/00_FLUXO_FINAL.md (seções 3.1 e 7) e, na rodada 2 (15/11), analise/fluxo2/BRIEFING.md (D2):
// a lista completa das culturas ("Ver todas as culturas"), o tamanho em metros à vista (grava ha, area_un, larg e comp), o baixio
// explicado com um desenho, e a maniva e o ano passado, que saíram do Plano.
// A lista das culturas mora em extras/culturas.js; o tamanho é só em ha ou em metros (o "em tarefas ou passos" saiu a pedido do José,
// 15/11; uma resposta antiga em tarefas ainda é lida por extras/area.js); o ano passado usa o formato de `antes`
// de extras/historico.js; a terra usa as palavras do Vicente (interface-inicial-vicente). Os modos "pergunta" de hoje_ideal.js e
// historico.js ficam no código (páginas de teste), fora da jornada.
import { olho, OLHOS } from "../extras/voce_decide.js";
import { lerHoje, CULT, igual, mexer, opcoesCultura } from "../extras/hoje_ideal.js";
import { GRUPOS, TODAS, foraDaqui, noCardapio } from "../extras/culturas.js";
import { tarefaPadrao, haDe, metrosDe, escreverArea } from "../extras/area.js";
import { CULT_H, lerAntes, escreverAntes, ANO_HOJE, icHist } from "../extras/historico.js";

// a terra: o nome (areia / misturada / barro) com o desenho da textura e, embaixo, as palavras do Vicente (o que ela faz na chuva forte)
const TERRAS = [["arenosa", "Areia", "seca rápido"], ["mista", "Misturada", "segura água"], ["barro", "Barro", "encharca"], ["", "Não sei", ""]];
const BAIXIOS = [["nao", 0, "Não tenho"], ["pouco", 0.2, "Pequeno"], ["metade", 0.5, "Grande"], ["", null, "Não sei"]];
const TERCO = ["terco", 1 / 3, "Um terço"]; // só para quem chega por um link antigo (…?baixio=terco)
const MANIVAS = [["tem", "Tenho", "rama"], ["plantada", "Já plantada", "broto"], ["nao", "Não tenho", "semRama"], ["", "Não sei", "interrog"]];
const HAS = [0.5, 1, 2, 3, 5];
const MAX_M = 5000; // o lado mais comprido que a tela aceita (5 km)
const FONTE_TIPICO = "típico do município no Censo Agropecuário 2017 (IBGE), aplicado ao seu roçado";
const FONTE_ZON = "ZARC/MAPA 2026/27 e FAO GAEZ v4, no cardápio do QUADRA para o município";

// ícones que faltavam em comum.js (mesmo traço, 24×24): o terreno com as duas medidas, o baixio de lado e a rama da mandioca
const RAMA = '<path d="M4 19 16 5M8.5 20.5 20 7.5M3 14.5 12.5 3.5"/><path d="M8.6 13.4l1.8 1.6M12.8 15.6l1.8 1.6M6.4 8.4l1.8 1.6M14.2 9.6l1.8 1.6"/>';
const ICL = {
  terreno: '<rect x="7" y="8" width="14" height="13" rx="1.5"/><path d="M7 4h14M7 2.6v2.8M21 2.6v2.8M3 8v13M1.6 21h2.8M1.6 8h2.8"/>',
  baixio: '<path d="M2 7c5 0 7 1.8 9 5.8S15 18 17 18h5"/><path d="M14.5 21h7.5M5 2.5l-.8 2M9 2l-.8 2"/>',
  rama: RAMA,
  semRama: `${RAMA}<path d="M3 3l18 18"/>`,
};
const icl = (U, nome) => (ICL[nome] ? `<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">${ICL[nome]}</svg>` : U.ic(nome));

// a textura de cada terra (48×28): grãos soltos (areia), grãos e torrões (misturada), barro liso com rachas e água em cima (encharca)
const GRAOS = [[6, 6], [13, 10], [20, 5], [27, 9], [34, 5], [41, 10], [9, 15], [16, 19], [23, 14], [30, 18], [37, 14], [44, 19], [5, 23],
  [12, 24], [19, 22], [26, 24], [33, 22], [40, 24]];
const grao = ([x, y]) => `<circle class="tx-grao" cx="${x}" cy="${y}" r="1.5"/>`;
const TEXTURA = {
  arenosa: `<rect class="tx-fundo areia" x="1" y="1" width="46" height="26" rx="6"/>${GRAOS.map(grao).join("")}`,
  mista: `<rect class="tx-fundo mista" x="1" y="1" width="46" height="26" rx="6"/>${GRAOS.filter((_, i) => i % 2).map(grao).join("")}
    <ellipse class="tx-torrao" cx="13" cy="9" rx="5" ry="3.4"/><ellipse class="tx-torrao" cx="33" cy="12" rx="5.5" ry="3.6"/>
    <ellipse class="tx-torrao" cx="21" cy="21" rx="5" ry="3.2"/>`,
  barro: `<rect class="tx-fundo barro" x="1" y="1" width="46" height="26" rx="6"/><path class="tx-racha" d="M9 27l4-8 7-3 3-6M23 10l8 4 6-5M31 14l2 7 8 3M13 19l-8-3"/>
    <path class="tx-agua" d="M7 5h13M28 5h13"/>`,
};
const textura = (v) => `<svg class="sr-tx" viewBox="0 0 48 28" aria-hidden="true">${TEXTURA[v]}</svg>`;

// o baixio de cada resposta: o roçado de lado (o mesmo desenho do "o que é?"), com a parte baixa e úmida do tamanho da resposta
const perfilMini = (f) => {
  const x = f > 0 ? Math.round(60 - 54 * f) : 60; // onde começa o chão plano do baixio
  const chao = f > 0 ? `M0 7C${x * 0.45} 7 ${x * 0.55} 21 ${x} 21L60 21L60 30L0 30Z` : "M0 7C24 7 34 25 60 25L60 30L0 30Z";
  return `<svg class="sr-pf" viewBox="0 0 60 30" aria-hidden="true"><path class="sp-terra" d="${chao}"/>${f > 0
    ? `<rect class="sp-umida" x="${x - 2}" y="21" width="${62 - x}" height="9"/><path class="sp-poca" d="M${x + 1} 21H58"/>` : ""}</svg>`;
};

// o roçado de lado: a chuva cai no alto, a água escorre e para no baixio, que fica úmido
const PERFIL = `<svg class="sr-perfil" viewBox="0 0 320 64" role="img" aria-label="O roçado visto de lado: a água da chuva desce do alto e para no baixio">
  <path class="sp-chuva" d="M34 4l-3 7M52 2l-3 7M70 4l-3 7M88 2l-3 7"/>
  <path class="sp-terra" d="M0 22 C70 20 112 21 142 27 C178 34 196 48 228 50 L320 50 L320 64 L0 64 Z"/>
  <path class="sp-umida" d="M214 48.6 C220 49.5 224 50 228 50 L320 50 L320 64 L204 64 Z"/>
  <path class="sp-poca" d="M232 50 H316"/>
  <path class="sp-agua" d="M118 18 C150 21 172 30 198 42"/><path class="sp-agua" d="M192 35 l7 7.5 -9.5 1.6"/>
  <text class="sp-rot" x="44" y="40">alto</text><text class="sp-rot" x="274" y="44">baixio</text></svg>`;

let rasc = null; // o rascunho da tela: { cult, ha, area_un, larg, comp, ml, mc, terra, baixio, maniva, antes }
let tocado = new Set(); // linhas que a pessoa tocou: só elas vão para a URL
let abertos = new Set(); // "quanto de cada" e "ver todas" abertos (sobrevivem ao redesenho)

const tipicoHa = (pad) => (pad?.rocado_ha > 0 ? pad.rocado_ha : pad?.rocado_ha_padrao > 0 ? pad.rocado_ha_padrao : null);
const lerHa = (s) => { const v = parseFloat(String(s ?? "").replace(",", ".")); return v > 0 ? v : null; };
const metro = (s) => { const v = Math.round(parseFloat(String(s ?? "").replace(",", "."))); return v > 0 ? Math.min(MAX_M, v) : null; };
const txtHa = (v) => String(Math.max(0.0001, Math.round(v * 1e4) / 1e4)); // 0.4 → "0.4"; 5 × 5 m → "0.0025" (ponto: vai para a URL)
/** A área para ler, como o haTxt de extras/terreno.js (o Plano): abaixo de 0,1 ha em m² (20 × 20 m → "400 m²"), abaixo de 1 ha com 2
 *  casas (30 × 50 m → "0,15 ha"), e o U.ha de sempre a partir de 1 ha. O U.ha sozinho escreve "0 ha" para 20 × 20 m. */
const areaTxt = (U, v) => (v < 0.1 ? `${U.num(v * 1e4 >= 100 ? Math.round(v * 1e3) * 10 : Math.round(v * 1e4))} m²`
  : v < 0.995 ? `${U.num(v, 2).replace(/0$/, "")} ha` : U.ha(v));
const tarefasTxt = (U, n) => (n < 0.1 ? "menos de 0,1 tarefa" : `≈ ${n >= 2 ? Math.round(n) : U.num(n, 1)} tarefa${n >= 1.5 ? "s" : ""}`);
// as setinhas dos lados do roçado: a largura vai de lado; o comprimento vai do alto até embaixo, para onde a água desce (o desenho do Plano)
const SETA_LADO = `<svg class="sr-m-seta" viewBox="0 0 24 12" aria-hidden="true"><path d="M2 6h20M6 2 2 6l4 4M18 2l4 4-4 4"/></svg>`;
const SETA_DESCE = `<svg class="sr-m-seta desce" viewBox="0 0 12 24" aria-hidden="true"><path d="M6 2v20M2 18l4 4 4-4"/></svg>`;
// o desenho do terreno ao lado dos metros: o roçado visto de cima, a largura (âmbar) em cima e o comprimento (azul) do alto até a água
const TERRENO = `<svg class="sr-terreno" viewBox="0 0 48 62" aria-hidden="true"><rect class="td-rocado" x="11" y="11" width="35" height="49" rx="4"/>
  <path class="td-agua" d="M11 50h35v6a4 4 0 0 1-4 4H15a4 4 0 0 1-4-4z"/>
  <path class="td-l" d="M13 4h31M16 1.5 13 4l3 2.5M41 1.5 44 4l-3 2.5"/><path class="td-c" d="M4 13v44M1.5 54 4 57l2.5-3"/></svg>`;
const mesmaDivisao = (a, b) => Object.keys(a).length === Object.keys(b).length && Object.keys(a).every((k) => a[k] === b[k]);
const listaNomes = (ks) => { const n = ks.map((k) => CULT[k].nome); return n.length > 1 ? `${n.slice(0, -1).join(", ")} e ${n.at(-1)}` : n[0]; };
/** O ano que "o ano passado" pergunta: o do jeito de hoje (2026, a safra antes do plano de 2027) menos 1. */
const anoPassado = (r) => (r.plano?.anos?.[0] ? r.plano.anos[0] - 1 : ANO_HOJE) - 1;

/** Largura × comprimento da resposta (metros inteiros): larg e comp, ou a medida de area_un que ainda bate com o ha gravado. */
function medidaIni(resp, uf) {
  const L = metro(resp.larg), C = metro(resp.comp);
  if (L && C) return { larg: L, comp: C };
  const m = metrosDe(resp.area_un), h = haDe(resp.area_un, uf), ha = lerHa(resp.ha);
  return m && h && ha && Math.abs(h - ha) / ha < 0.02 ? m : null;
}

/** `hoje` com as culturas novas; quem já tinha outras chaves (|cons=…) fica com as dele (o padrão não vira resposta). */
function hojeTxt(cult, antigo) {
  const cs = Object.keys(CULT).filter((k) => cult[k] > 0).map((k) => `${k}:${cult[k]}`).join(",");
  return [cs, ...String(antigo || "").split("|").slice(1).filter(Boolean)].join("|");
}

/** A maniva que a tela mostra e grava: a tocada; senão, marcar a mandioca supõe que ela já está no chão (e desmarcar desfaz). */
function manivaTela(ctx) {
  const resp = ctx.resp;
  if (tocado.has("maniva")) return rasc.maniva;
  const tinha = "mandioca" in lerHoje(resp.hoje || "", ctx.r.padroes).cult, tem = "mandioca" in rasc.cult;
  if (tem && !tinha && !resp.maniva) return "plantada";
  if (!tem && tinha && resp.maniva === "plantada") return "";
  return resp.maniva || "";
}

/** O que vai para a URL: só as linhas tocadas, e só o que mudou de fato. */
function patch(ctx) {
  const resp = ctx.resp, p = {};
  if (tocado.has("hoje") && !mesmaDivisao(lerHoje(resp.hoje || "", ctx.r.padroes).cult, rasc.cult)) p.hoje = hojeTxt(rasc.cult, resp.hoje);
  const mv = manivaTela(ctx);
  if (mv !== (resp.maniva || "")) p.maniva = mv;
  for (const [k, linha] of [["ha", "ha"], ["area_un", "ha"], ["larg", "ha"], ["comp", "ha"], ["terra", "terra"], ["baixio", "baixio"], ["antes", "antes"]]) {
    if (tocado.has(linha) && (rasc[k] || "") !== (resp[k] || "")) p[k] = rasc[k] || "";
  }
  return p;
}

/** As janelas de plantar de agora ({cod, jan: {cultura: "dd/mm a dd/mm"}}), para o "era dd/mm" do passo 3 (só neste município). */
function guardarAntes(ctx, p) {
  try {
    if (!Object.keys(p).length) return sessionStorage.removeItem("quadra.antes");
    const jan = (ctx.r.agenda?.culturas || []).map((c) => [c.cultura, String(c.plantar || "").split(" (")[0].replace(/^de /, "").replace(/\/20\d\d/g, "")]);
    sessionStorage.setItem("quadra.antes", JSON.stringify({ cod: ctx.cod, jan: Object.fromEntries(jan.filter(([, v]) => v)) }));
  } catch (_) { /* sem sessionStorage: o passo 3 só não mostra o "antes" */ }
}

/** Faixa de 1 linha: El Niño de 2027 e o solo de hoje. */
function faixa(r, U) {
  const e = r.este_ano || {}, sm = e.smap?.status === "ok" ? e.smap : null;
  const nino = e.oni >= 1.5 ? "El Niño forte" : e.oni >= 0.5 ? "El Niño" : "";
  const solo = sm ? String(sm.classe || "").replace(/ para a época$/, "") : "";
  if (!nino && !solo) return "";
  const fonte = [sm && `Solo: NASA SMAP L4, umidade na raiz nos 30 dias até ${U.dataBR(sm.fim)} (posição ${sm.posto} de ${sm.anos} anos; 1 = o mais seco)`,
    nino && `El Niño: índice ONI da NOAA, mar ${U.num(e.oni, 1)} °C acima do normal`].filter(Boolean).join(". ");
  const txt = [nino && `2027: ${nino}`, solo && `solo hoje ${solo}`].filter(Boolean).join(", ");
  return `<p class="sr-faixa ${e.nivel_alerta === "alerta" ? "" : "azul"}">${U.ic("onda")}<span>${U.esc(txt)}</span>${U.selo("medido", fonte)}</p>`;
}

const botao = (attr, marcado, corpo, cls = "") =>
  `<button type="button" class="sr-op ${cls} ${marcado ? "marcada" : ""}" ${attr} aria-pressed="${marcado}">${corpo}</button>`;
const estadoFeito = (U) => `<span class="sr-estado sr-feito" title="Respondido" role="img" aria-label="respondido">${U.ic("ok")}</span>`;

function desenhar(el, ctx) {
  const U = ctx.util, r = ctx.r, pad = r.padroes || {}, uf = r.local?.uf;
  const ks = Object.keys(rasc.cult);
  const tip = tipicoHa(pad), haResp = lerHa(rasc.ha), haV = haResp || tip || 1;
  const deOnde = pad.rocado_ha > 0 ? "típico daqui" : tip ? "típico da região" : "exemplo";
  const baixios = [...BAIXIOS];
  if (rasc.baixio === "terco" || ctx.resp.baixio === "terco") baixios.splice(2, 0, TERCO);
  const det = (k, titulo, corpo, cls = "") => `<details class="ver-mais sr-mais ${cls}" data-k="${k}"${abertos.has(k) ? " open" : ""}><summary>${titulo}</summary>${corpo}</details>`;
  // cada pergunta é um cartão: o número, o ícone e a pergunta curta numa linha (a ajuda curta embaixo dela) e, na borda de cima,
  // ✓ (respondida) ou "comum daqui" (o padrão)
  const resp = ctx.resp, feita = (linha, k = linha) => tocado.has(linha) || !!resp[k];
  const cab = (n, icone, titulo, feito, eco = "", padrao = "comum daqui") => `<div class="sr-cab">
      <span class="sr-n" aria-hidden="true">${n}</span><span class="sr-num" aria-hidden="true">${icl(U, icone)}</span>
      <h2 class="sr-rot">${titulo}${eco ? `<span class="eco">${eco}</span>` : ""}</h2>
      ${feito ? estadoFeito(U) : `<span class="sr-estado sr-padrao">${padrao}</span>`}</div>`;
  const conv = (h, tip) => `<span class="sr-m-conv" aria-live="polite"><b>= ${areaTxt(U, h)}</b><span>${tarefasTxt(U, (h * 10000) / tarefaPadrao(uf))}</span>${tip
    ? U.selo("suposicao", FONTE_TIPICO) : ""}</span>`;
  // a ajuda fecha num "?" no canto do cartão (o desenho e o "seu olho" ficam lá dentro)
  const ajuda = (k, rotulo, corpo) => `<details class="sr-ajuda" data-k="${k}"${abertos.has(k) ? " open" : ""}><summary aria-label="${rotulo}"
      title="${rotulo}"><span aria-hidden="true">?</span></summary><div class="sr-ajuda-corpo">${corpo}</div></details>`;

  // ---- o que planta hoje: as mais comuns à vista + a lista completa; a barra colorida da divisão abre o "quanto de cada"
  const barra = `<span class="hi-divisao sr-divisao" role="img" aria-label="divisão do roçado: ${ks.map((k) => `${CULT[k].nome} ${rasc.cult[k]}%`).join(", ")}">${ks.map((k) =>
    `<i class="t-${CULT[k].t}" style="flex:${rasc.cult[k]}"><span>${ks.length <= 4 ? U.ic(CULT[k].icone) : ""}${ks.length <= 2 && rasc.cult[k] >= 25
      ? `${CULT[k].nome} ` : ""}${rasc.cult[k]}%</span></i>`).join("")}</span>`;
  const opLista = (k) => botao(`data-c="${k}"`, ks.includes(k), `${U.ic(CULT[k].icone)}<span class="sr-l-nome"><b>${CULT[k].nome}</b>${CULT[k].sub
    ? `<small>${CULT[k].sub}</small>` : ""}</span>`, "sr-op-lista");
  const todas = `<div class="sr-todas">${GRUPOS.map((g) => `<div class="sr-grupo"><p class="sr-g-rot">${g.nome}</p>
      <div class="sr-g-ops">${g.ks.map(opLista).join("")}</div></div>`).join("")}
    <div class="sr-grupo"><p class="sr-g-rot">Não achou?</p><div class="sr-g-ops">${opLista("outra")}</div></div></div>`;
  const fora = ks.filter((k) => foraDaqui(r, k));
  // a fonte de cada uma vem antes (o rótulo curto do selo sai da 1ª: ZARC onde há zoneamento, FAO onde só o GAEZ decide)
  const aviso = fora.length ? `<p class="sr-aviso">${U.ic("alerta")}<span>Fora do indicado aqui: ${U.esc(listaNomes(fora).toLowerCase())}.</span>${U.selo("medido",
    `${fora.map((k) => `${CULT[k].motor}: ${noCardapio(r, k)?.base || "fora"}`).join("; ")}. ${FONTE_ZON}`)}</p>` : "";
  const linhaHoje = `<section class="sr-linha" id="linha-hoje">
      ${cab(1, "broto", "O que você planta?", feita("hoje"))}
      <div class="sr-ops n3">${opcoesCultura(r, ks).map((k) => botao(`data-c="${k}"`, ks.includes(k), `${U.ic(CULT[k].icone)}<b>${CULT[k].nome}</b>`)).join("")}</div>
      ${det("todas", `Ver todas as culturas (${TODAS.length})`, todas, "sr-todas-det")}
      ${aviso}
      ${ks.length > 1 ? det("quanto", `${barra}<small>quanto de cada</small>`, `<div class="hi-quanto">${ks.map((k) => `<div class="hi-q-linha">${U.ic(CULT[k].icone)}<b>${CULT[k].nome}</b>
          <button type="button" class="hi-mm" data-m="${k}" data-d="-10" aria-label="menos ${CULT[k].nome}">−</button>
          <span class="hi-q-val">${rasc.cult[k]}%</span>
          <button type="button" class="hi-mm" data-m="${k}" data-d="10" aria-label="mais ${CULT[k].nome}">+</button></div>`).join("")}
          <button type="button" class="chip hi-igual" data-igual="1">dividir igual</button></div>`, "sr-mais-barra") : `<div class="sr-so-barra">${barra}</div>`}
    </section>`;

  // ---- tamanho: chips de ha e, à vista, largura × comprimento em metros (sem resposta: o típico do Censo; o lado do quadrado
  // dele fica de exemplo no campo vazio). Sem resposta, o chip mais perto do típico fica tracejado (só a cara: não grava nada)
  const sug = haResp === null ? HAS.reduce((a, v) => (Math.abs(v - haV) < Math.abs(a - haV) ? v : a)) : null;
  const ladoTip = Math.round(Math.sqrt(haV * 10000));
  // os rótulos dizem qual lado é qual (o comprimento é o do desenho do Plano: do alto até embaixo, para onde a água desce, e as
  // faixas vão atravessadas a ele); no campo vazio, o lado do quadrado típico vem como exemplo ("ex.: 101"), para não parecer valor
  const campo = (k, rot, seta, dica) => `<label class="sr-m-campo" title="${dica}"><span class="sr-m-caixa"><input type="number" inputmode="numeric" min="1"
      max="${MAX_M}" step="1" data-lado="${k}" value="${U.esc(k === "larg" ? rasc.ml : rasc.mc)}" placeholder="ex.: ${ladoTip}"
      aria-label="${dica}, em metros"></span><small>${seta}<span>${rot}</span></small></label>`;
  const linhaHa = `<section class="sr-linha" id="linha-ha">
      ${cab(2, "terreno", "Qual o tamanho?", haResp !== null, conv(haV, haResp === null), deOnde)}
      <div class="sr-ops n5">${HAS.map((v) => botao(`data-ha="${v}"`, haResp !== null && !rasc.larg && Math.abs(haResp - v) < 0.005,
        `<b>${v === 0.5 ? "½" : v}${v === 5 ? " ha" : ""}</b>`, `sr-ha${v === sug && Math.abs(v - haV) < 0.26 ? " sugerida" : ""}`)).join("")}</div>
      <div class="sr-metros">
        <p class="sr-m-rot">ou em metros</p>
        <div class="sr-m-linha">${TERRENO}${campo("larg", "largura", SETA_LADO, "Largura do roçado: de um lado ao outro")}<span class="sr-vezes" aria-hidden="true">×</span>${campo("comp",
          "comprimento, morro abaixo", SETA_DESCE, "Comprimento do roçado: do alto até embaixo, para onde a água da chuva desce")}</div>
      </div>
    </section>`;

  const naoSei = `<span class="sr-img">${U.ic("interrog")}</span>`;
  const linhaTerra = `<section class="sr-linha tem-ajuda" id="linha-terra">
      ${cab(3, "solo", "Como é a terra?", feita("terra"))}
      ${ajuda("ajuda-terra", "Como saber a sua terra?", olho(OLHOS.terra))}
      <div class="sr-ops n4">${TERRAS.map(([v, t, s]) => botao(`data-terra="${v}"`, (rasc.terra || "") === v,
        `${v ? `<span class="sr-img">${textura(v)}</span>` : naoSei}<b>${t}</b>${s ? `<small>${s}</small>` : ""}`, "alto sr-terra")).join("")}</div>
    </section>`;

  const linhaBaixio = `<section class="sr-linha tem-ajuda" id="linha-baixio">
      ${cab(4, "baixio", "Tem baixio?", feita("baixio"), "A parte mais baixa do roçado, onde a água para.")}
      ${ajuda("ajuda-baixio", "O que é baixio?", `${PERFIL}<p>A chuva escorre para lá e a terra fica úmida mais tempo. Beira de riacho, grota, açude.</p>${olho(OLHOS.baixio)}`)}
      <div class="sr-ops n${baixios.length}">${baixios.map(([v, f, t]) => botao(`data-baixio="${v}"`, (rasc.baixio || "") === v,
        `${f === null ? naoSei : `<span class="sr-img">${perfilMini(f)}</span>`}<b>${t}</b>`, "alto")).join("")}</div>
    </section>`;

  // ---- maniva: só quando a mandioca está no jeito dele ou no plano daqui (sem maniva, ela sai do plano). Quem já planta mandioca
  // ouve "para plantar mais?"; quem não planta ouve por que a pergunta está ali (o plano daqui usa mandioca) e não vê "Já está plantada"
  const mv = manivaTela(ctx), planta = ks.includes("mandioca");
  const mandNoPlano = (r.plano?.faixas || []).some((f) => (f.anos || []).some((a) => /^Mandioca/.test(a.cultura || "")));
  const manivas = MANIVAS.filter(([v]) => v !== "plantada" || planta || mv === "plantada");
  const linhaManiva = planta || mandNoPlano || ctx.resp.maniva ? `<section class="sr-linha" id="linha-maniva">
      ${cab(5, "mandioca", "Tem maniva?", feita("maniva"), planta ? "A rama, para plantar mais." : mandNoPlano ? "O plano daqui usa mandioca." : "A rama da mandioca.")}
      <div class="sr-ops n${manivas.length}">${manivas.map(([v, t, i]) => botao(`data-maniva="${v}"`, mv === v,
        `<span class="sr-img">${icl(U, i)}</span><b>${t}</b>`, "alto sr-maniva")).join("")}</div>
    </section>` : "";

  // ---- o ano passado nesse chão (`antes` = "2025:milho,feijao" ou "2025:pousio"): as culturas de hoje e as já marcadas + outra +
  // descansou + não sei. "Outra" abre o leque com a lista completa (os grupos de "Ver todas"); o que marcar lá vira chip aqui
  const ap = anoPassado(r), noAno = lerAntes(rasc.antes)[ap] || [], leque = abertos.has("antes");
  const chipsAntes = [...Object.keys(CULT_H).filter((k) => k !== "pousio" && k !== "outra" && (ks.includes(k) || noAno.includes(k))), "pousio"];
  const chipAntes = (k) => botao(`data-antes="${k}"`, noAno.includes(k),
    `${k === "pousio" ? icHist(U, "pousio") : U.ic(CULT[k]?.icone || "broto")}<b>${k === "pousio" ? "Descansou" : CULT_H[k].nome}</b>`, "sr-chip");
  const opAntes = (k) => botao(`data-antes="${k}"`, noAno.includes(k), `${U.ic(CULT[k].icone)}<span class="sr-l-nome"><b>${CULT_H[k].nome}</b>${CULT[k].sub
    ? `<small>${CULT[k].sub}</small>` : ""}</span>`, "sr-op-lista");
  const lequeAntes = leque ? `<div class="sr-todas sr-leque-antes">${GRUPOS.map((g) => `<div class="sr-grupo"><p class="sr-g-rot">${g.nome}</p>
      <div class="sr-g-ops">${g.ks.map(opAntes).join("")}</div></div>`).join("")}
    <div class="sr-grupo"><p class="sr-g-rot">Não achou?</p><div class="sr-g-ops">${opAntes("outra")}</div></div></div>` : "";
  const linhaAntes = `<section class="sr-linha" id="linha-antes">
      ${cab(6, "relogio", "E no ano passado?", feita("antes"), `Em ${ap}, nesse chão.`)}
      <div class="sr-ops n3 sr-chips">${chipsAntes.slice(0, -1).map(chipAntes).join("")}
        <button type="button" class="sr-op sr-chip ${noAno.includes("outra") ? "marcada" : ""} ${leque ? "aberta" : ""}" data-leque="antes"
          aria-expanded="${leque}">${U.ic("broto")}<b>Outra</b><span class="sr-seta" aria-hidden="true">${leque ? "▴" : "▾"}</span></button>
        ${chipAntes("pousio")}
        ${botao(`data-antes=""`, !noAno.length, `${U.ic("interrog")}<b>Não sei</b>`, "sr-chip")}</div>
      ${lequeAntes}
    </section>`;

  el.innerHTML = `<div class="sua-roca">
    <div class="titulo-passo"><p class="kicker">Sua roça</p><h1>É assim o seu roçado?<span class="eco">Marcamos o comum daqui.</span></h1></div>
    ${faixa(r, U)}${linhaHoje}${linhaHa}${linhaTerra}${linhaBaixio}${linhaManiva}${linhaAntes}</div>`;

  const raiz = el.firstElementChild;
  const mudar = (linha, f) => (ev) => { f(ev.currentTarget); tocado.add(linha); desenhar(el, ctx); };
  raiz.querySelectorAll("[data-c]").forEach((b) => b.addEventListener("click", mudar("hoje", (b) => {
    const k = b.dataset.c, novo = ks.includes(k) ? ks.filter((x) => x !== k) : Object.keys(CULT).filter((x) => ks.includes(x) || x === k);
    if (novo.length) rasc.cult = igual(novo);
  })));
  raiz.querySelectorAll("[data-m]").forEach((b) => b.addEventListener("click", mudar("hoje", (b) => { rasc.cult = mexer(rasc.cult, b.dataset.m, +b.dataset.d); })));
  raiz.querySelector("[data-igual]")?.addEventListener("click", mudar("hoje", () => { rasc.cult = igual(ks); }));
  raiz.querySelectorAll("[data-ha]").forEach((b) => b.addEventListener("click", mudar("ha", (b) => {
    Object.assign(rasc, { ha: b.dataset.ha, area_un: "", larg: "", comp: "", ml: "", mc: "" });
  })));
  raiz.querySelectorAll("[data-terra]").forEach((b) => b.addEventListener("click", mudar("terra", (b) => { rasc.terra = b.dataset.terra; })));
  raiz.querySelectorAll("[data-baixio]").forEach((b) => b.addEventListener("click", mudar("baixio", (b) => { rasc.baixio = b.dataset.baixio; })));
  raiz.querySelectorAll("[data-maniva]").forEach((b) => b.addEventListener("click", mudar("maniva", (b) => { rasc.maniva = b.dataset.maniva; })));
  raiz.querySelectorAll("[data-antes]").forEach((b) => b.addEventListener("click", mudar("antes", (b) => {
    const k = b.dataset.antes, anos = lerAntes(rasc.antes);
    const novo = !k ? [] : k === "pousio" ? (noAno.includes("pousio") ? [] : ["pousio"])
      : noAno.includes(k) ? noAno.filter((x) => x !== k) : [...noAno.filter((x) => x !== "pousio"), k];
    if (novo.length) anos[ap] = novo; else delete anos[ap];
    rasc.antes = escreverAntes(anos);
  })));
  // "Outra" no ano passado: abre (ou fecha) o leque com todas as culturas; abrir não grava nada
  raiz.querySelector("[data-leque]")?.addEventListener("click", () => {
    if (leque) abertos.delete("antes"); else abertos.add("antes");
    desenhar(el, ctx);
    if (!leque) el.querySelector(".sr-leque-antes")?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  });
  // metros: digitando, o "= X ha", as tarefas, o tamanho e os chips acompanham ali mesmo, sem redesenhar (o campo não perde o
  // foco e o toque no outro campo não se perde). Só os dois lados juntos viram resposta.
  raiz.querySelectorAll("[data-lado]").forEach((inp) => inp.addEventListener("input", () => {
    rasc[inp.dataset.lado === "larg" ? "ml" : "mc"] = inp.value;
    const L = metro(rasc.ml), C = metro(rasc.mc);
    tocado.add("ha");
    if (!L || !C) { Object.assign(rasc, { larg: "", comp: "", area_un: "" }); return; }
    const h = (L * C) / 10000;
    Object.assign(rasc, { ha: txtHa(h), area_un: escreverArea({ un: "medida", c: C, l: L, em: "m" }, uf), larg: String(L), comp: String(C) });
    raiz.querySelector(".sr-m-conv").innerHTML = `<b>= ${areaTxt(U, h)}</b><span>${tarefasTxt(U, (h * 10000) / tarefaPadrao(uf))}</span>`;
    const tipico = raiz.querySelector("#linha-ha .sr-padrao"); // "típico daqui" vira ✓: a medida dele é resposta
    if (tipico) tipico.outerHTML = estadoFeito(U);
    raiz.querySelectorAll("[data-ha]").forEach((b) => { b.classList.remove("marcada", "sugerida"); b.setAttribute("aria-pressed", "false"); });
  }));
  raiz.querySelectorAll("details.sr-mais, details.sr-ajuda").forEach((d) => d.addEventListener("toggle", () => {
    if (d.open) abertos.add(d.dataset.k); else abertos.delete(d.dataset.k);
  }));
}

export default {
  id: "perguntas",
  titulo: "Sua roça",
  render(el, ctx) {
    if (ctx.entrou || !rasc) {
      const resp = ctx.resp, med = medidaIni(resp, ctx.r.local?.uf);
      rasc = { cult: lerHoje(resp.hoje || "", ctx.r.padroes).cult, ha: resp.ha || "", area_un: resp.area_un || "", terra: resp.terra || "",
        baixio: resp.baixio || "", maniva: resp.maniva || "", antes: resp.antes || "",
        larg: med ? String(med.larg) : "", comp: med ? String(med.comp) : "", ml: med ? String(med.larg) : "", mc: med ? String(med.comp) : "" };
      tocado = new Set();
      abertos = new Set();
    }
    desenhar(el, ctx);
    // o que foi tocado e ainda não foi gravado: o verde grava; a casca (roca.js) também leva junto ao sair por uma pílula ou pelo rodapé
    ctx.pendente = () => { const p = patch(ctx); guardarAntes(ctx, p); return p; };
    // "Ver o meu plano →" (ou "Voltar a …"): grava uma vez só. Antes, troca esta entrada do histórico pela mesma tela com as
    // respostas, para o voltar do celular reabrir "Sua roça" como a pessoa deixou.
    ctx.primario?.(ctx.volta ? undefined : "Ver o meu plano →", () => {
      const p = ctx.pendente();
      if (Object.keys(p).length) location.replace(ctx.link(2, p));
      location.hash = ctx.link(ctx.volta || 3, p);
    });
    if (ctx.entrou && ctx.foco) {
      setTimeout(() => { // depois de o roca.js pôr a tela no lugar e rolar ao topo
        const l = el.querySelector(`#linha-${ctx.foco}`);
        if (!l) return;
        l.scrollIntoView({ block: "start", behavior: "smooth" });
        l.classList.add("em-foco");
        setTimeout(() => l.classList.remove("em-foco"), 2600);
      }, 80);
    }
  },
};
