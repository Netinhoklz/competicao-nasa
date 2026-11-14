// QUADRA, site final: a jornada em 5 passos (roca.html#/<cod IBGE>/<passo>?respostas).
// Cada passo é um módulo em js/passos/ com: export default { id, titulo, curto, render(el, ctx) }.
// Contrato do ctx: ver web/js/passos/LEIA-ME.md.
import * as U from "./comum.js";
import lugar from "./passos/lugar.js";
import perguntas from "./passos/perguntas.js";
import plantio from "./passos/plantio.js";
import dinheiro from "./passos/dinheiro.js";
import seguranca from "./passos/seguranca.js";

const PASSOS = [lugar, perguntas, plantio, dinheiro, seguranca];

// Respostas do agricultor. "" = não sei / não respondeu (vale o padrão). Só o que difere do padrão vai para a URL.
export const PADRAO = { terra: "", ha: "", baixio: "", agua: "", vol: "", maniva: "", criacao: "", prioridade: "", gs: "", raiz: "", custo: "" };
const TERRA = { arenosa: { textura: "1", ad: "12" }, mista: { textura: "2", ad: "13" }, barro: { textura: "3", ad: "15" } };
const BAIXIO_FRAC = { nao: 0, pouco: 0.2, terco: 1 / 3, metade: 0.5, "": 1 / 3 };

const cache = new Map();
let estado = { cod: null, passo: 1, resp: { ...PADRAO } };
let pedido = 0;

function lerHash() {
  const h = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  const [caminho, busca = ""] = h.split("?");
  const [cod, passo] = caminho.split("/");
  const q = new URLSearchParams(busca);
  const resp = { ...PADRAO };
  for (const k of Object.keys(PADRAO)) if (q.has(k)) resp[k] = q.get(k);
  return { cod: /^\d{7}$/.test(cod || "") ? cod : null, passo: Math.min(5, Math.max(1, +passo || 1)), resp };
}

function escreverHash(e) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(e.resp)) if (v !== "" && v !== PADRAO[k]) q.set(k, v);
  const s = q.toString();
  return `#/${e.cod}/${e.passo}${s ? "?" + s : ""}`;
}

/** Parâmetros que mudam o núcleo (o resto o navegador calcula). */
function paramsApi(resp) {
  const p = new URLSearchParams();
  if (TERRA[resp.terra]) { p.set("textura", TERRA[resp.terra].textura); p.set("ad", TERRA[resp.terra].ad); }
  if (resp.baixio === "nao") p.set("baixio", "0");
  else if (["pouco", "terco", "metade"].includes(resp.baixio)) p.set("ad_baixio", "15"); // suposição: o baixio guarda mais água (AD5)
  if (["nao", "plantada"].includes(resp.maniva)) p.set("maniva", resp.maniva);
  return p;
}

async function buscar(cod, resp) {
  const p = paramsApi(resp);
  p.set("cod", cod);
  const chave = p.toString();
  if (!cache.has(chave)) {
    cache.set(chave, fetch(`/api/local?${chave}`).then(async (r) => {
      const j = await r.json();
      if (j.erro) throw new Error(j.erro);
      return j;
    }).catch((e) => { cache.delete(chave); throw e; }));
  }
  return cache.get(chave);
}

/** Respostas com os padrões aplicados (o que os passos devem usar), com a origem de cada valor. */
function efetivas(resp, r) {
  const pad = r.padroes || {};
  const alerta = r.este_ano?.nivel_alerta === "alerta";
  const haResp = parseFloat(String(resp.ha).replace(",", "."));
  const padHa = pad.rocado_ha > 0 ? pad.rocado_ha : (pad.rocado_ha_padrao > 0 ? pad.rocado_ha_padrao : null);
  const area = haResp > 0 ? haResp : (padHa || 1);
  const frac = BAIXIO_FRAC[resp.baixio] ?? 1 / 3;
  return {
    terra: resp.terra || "nao_sei",
    ha: Math.round(area * 100) / 100,
    ha_origem: haResp > 0 ? "resposta" : (pad.rocado_ha > 0 ? "padrão do município (Censo 2017)"
      : padHa ? "padrão da mesorregião (Censo 2017)" : "exemplo (1 ha)"),
    baixio: resp.baixio || "nao_sei",
    tem_baixio: resp.baixio === "nao" ? false : (resp.baixio ? true : null),
    baixio_frac: frac,
    baixio_ha: Math.round(area * frac * 100) / 100,
    agua: resp.agua || "chuva",
    vol_m3: parseFloat(resp.vol) || null,
    maniva: resp.maniva || "tem",
    criacao: resp.criacao || "nao_sei",
    prioridade: resp.prioridade || (alerta ? "garantir" : "equilibrar"),
    prioridade_origem: resp.prioridade ? "resposta" : (alerta ? "padrão em ano de alerta de El Niño" : "padrão"),
    gs: resp.gs || "nao_sei",
    raiz: resp.raiz || "uf_mediana",
    custo: resp.custo || "semente",
  };
}

const ROT = {
  terra: { nao_sei: "terra: não sei", arenosa: "terra arenosa", mista: "terra misturada", barro: "terra de barro" },
  baixio: { nao_sei: "baixio: não sei", nao: "sem baixio", pouco: "baixio pequeno", terco: "baixio ⅓", metade: "baixio ½" },
  agua: { chuva: "só a chuva", cisterna: "cisterna de beber", barreiro: "barreiro/açude", irriga: "poço ou irrigação" },
  maniva: { tem: "consigo maniva", nao: "sem maniva", plantada: "mandioca já plantada" },
};

function desenharCasca(r, ef) {
  const l = r.local;
  document.getElementById("topo-lugar").innerHTML = `<b>${U.esc(l.municipio)}</b> <span>· ${U.esc(l.mesorregiao)} · ${U.esc(l.uf)}</span>`;
  document.title = `QUADRA · ${l.municipio} (${l.uf})`;
  document.getElementById("passos-nav").innerHTML = PASSOS.map((p, i) =>
    `<button class="passo-pilula ${i + 1 === estado.passo ? "atual" : i + 1 < estado.passo ? "feito" : ""}" data-ir="${i + 1}" type="button">
      <i>${i + 1 < estado.passo ? "✓" : i + 1}</i><span>${U.esc(p.titulo)}</span></button>`).join("");
  const ficha = document.getElementById("ficha");
  ficha.innerHTML = estado.passo >= 3 ? `<span>Sua roça:</span>` + [
    ROT.terra[ef.terra], U.ha(ef.ha) + (ef.ha_origem === "resposta" ? "" : " (padrão)"), ROT.baixio[ef.baixio], ROT.agua[ef.agua], ROT.maniva[ef.maniva],
  ].map((t) => `<button type="button" data-ir="2" title="Mudar a resposta">${U.esc(t)} ✎</button>`).join("") : "";
  const v = document.getElementById("voltar"), a = document.getElementById("avancar");
  v.disabled = estado.passo === 1;
  a.textContent = estado.passo < 5 ? `${PASSOS[estado.passo].titulo} →` : "Outro lugar →";
}

async function desenhar() {
  const meu = ++pedido;
  const e = lerHash();
  estado = e;
  const el = document.getElementById("jornada");
  if (!e.cod) return escolherLugar(el);
  if (!el.querySelector(".passo-conteudo")) el.innerHTML = `<div class="carregando">Juntando os dados da NASA, do ZARC e do IBGE para este lugar…</div>`;
  let r;
  try {
    r = await buscar(e.cod, e.resp);
  } catch (err) {
    if (meu === pedido) el.innerHTML = `<div class="erro">Não consegui carregar este lugar: ${U.esc(err.message)}. O servidor está rodando? (python servidor.py)</div>`;
    return;
  }
  if (meu !== pedido) return;
  const ef = efetivas(e.resp, r);
  desenharCasca(r, ef);
  const ctx = {
    r, cod: e.cod, passo: e.passo, resp: e.resp, ef, padroes: r.padroes || null, util: U,
    set: (patch) => { const n = { ...estado, resp: { ...estado.resp, ...patch } }; location.replace(escreverHash(n)); },
    ir: (n) => { location.hash = escreverHash({ ...estado, passo: n }); },
    link: (n, patch = {}) => escreverHash({ ...estado, passo: n, resp: { ...estado.resp, ...patch } }),
  };
  const passo = PASSOS[e.passo - 1];
  const caixa = document.createElement("div");
  caixa.className = `passo-conteudo passo-${passo.id}`;
  try {
    await passo.render(caixa, ctx);
  } catch (err) {
    console.error(err);
    caixa.innerHTML = `<div class="erro">Erro ao desenhar o passo "${U.esc(passo.titulo)}": ${U.esc(err.message)}</div>`;
  }
  if (meu !== pedido) return;
  const mudouPasso = el.dataset.passo !== String(e.passo);
  el.replaceChildren(caixa);
  el.dataset.passo = String(e.passo);
  if (mudouPasso) window.scrollTo({ top: 0, behavior: "instant" });
}

async function escolherLugar(el) {
  document.getElementById("passos-nav").innerHTML = "";
  document.getElementById("ficha").innerHTML = "";
  document.getElementById("topo-lugar").innerHTML = "";
  const ex = [["2311306", "Quixadá (CE)"], ["2208007", "Picos (PI)"], ["2611101", "Petrolina (PE)"], ["2700300", "Arapiraca (AL)"], ["2903201", "Barreiras (BA)"]];
  el.innerHTML = `<div class="titulo-passo"><h1>Escolha o seu município</h1><p>O QUADRA cobre os 1.794 municípios do Nordeste. Pelo globo
    (<a href="index.html">voltar ao globo</a>) ou pela busca:</p></div>
    <div class="cartao"><input id="busca-mun" list="lista-mun" placeholder="Digite o município…" style="width:100%;max-width:420px;padding:10px 12px;border:1px solid var(--border);border-radius:10px;font-size:16px;background:var(--surface);color:var(--ink)">
    <datalist id="lista-mun"></datalist>
    <p class="sub">Exemplos: ${ex.map(([c, n]) => `<a href="#/${c}/1">${n}</a>`).join(" · ")}</p></div>`;
  let lista = [];
  try {
    const r = await fetch("dados/busca_municipios.json");
    if (!r.ok) throw new Error();
    const j = await r.json();
    lista = (Array.isArray(j) ? j : j.municipios || []).map((m) => ({ nome: `${m.nome} (${m.uf})`, cod: String(m.cod) }));
  } catch (_) {
    const gj = await (await fetch("/api/municipios")).json();
    lista = gj.features.map((f) => ({ nome: `${f.properties.nome} (${f.properties.uf})`, cod: String(f.properties.cod) }));
  }
  lista.sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
  document.getElementById("lista-mun").innerHTML = lista.map((m) => `<option value="${U.esc(m.nome)}"></option>`).join("");
  document.getElementById("busca-mun").addEventListener("change", (ev) => {
    const m = lista.find((x) => x.nome === ev.target.value);
    if (m) location.hash = `#/${m.cod}/1`;
  });
}

document.addEventListener("click", (ev) => {
  const b = ev.target.closest("[data-ir]");
  if (b && estado.cod) { ev.preventDefault(); location.hash = escreverHash({ ...estado, passo: +b.dataset.ir }); }
});
document.getElementById("voltar").addEventListener("click", () => estado.passo > 1 && (location.hash = escreverHash({ ...estado, passo: estado.passo - 1 })));
document.getElementById("avancar").addEventListener("click", () => {
  if (estado.passo < 5) location.hash = escreverHash({ ...estado, passo: estado.passo + 1 });
  else location.href = "index.html";
});
document.getElementById("tema").addEventListener("click", () => {
  const h = document.documentElement, escuro = h.dataset.theme ? h.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  h.dataset.theme = escuro ? "light" : "dark";
  try { localStorage.setItem("quadra-tema", h.dataset.theme); } catch (_) { /* sem armazenamento: só nesta visita */ }
});
try { const t = localStorage.getItem("quadra-tema"); if (t) document.documentElement.dataset.theme = t; } catch (_) { /* idem */ }
window.addEventListener("hashchange", desenhar);
desenhar();
