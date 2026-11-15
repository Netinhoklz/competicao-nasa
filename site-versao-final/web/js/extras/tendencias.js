// Extra "Como o seu lugar está mudando" (pontos 1 e 11 do desafio): seis mini-gráficos ano a ano do município, num eixo comum
// 2000–2026, com o valor do ano, a tendência em palavras (só quando é clara) e, quando o ano está do lado ruim do normal, 1 frase
// que liga o número à roça e ao solo. O toque em qualquer gráfico move o cursor em todos ao mesmo tempo (comparar as bases no mesmo ano).
// Dados: web/dados/tendencias/<UF>.json, gerado por ferramentas/preparar_tendencias.py (IMERG, SMAP e MODIS por município;
// NASA POWER em grade de ~55 km; GRACE por mesorregião). Nada é calculado aqui além de escolher o ano.
// Uso: import T from "./extras/tendencias.js"; await T.render(div, ctx, { series: ["c", "s", "t", "e", "v", "a"] }).
import * as U from "../comum.js";
import { termo } from "./glossario.js"; // integração: "o que é?" nas palavras evaporação e verde do satélite

const CACHE = {};
// o servidor às vezes recusa um pedido no meio de uma rajada: tenta de novo uma vez; sem dado, não guarda a falha
const pedir = (url) => fetch(url).then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))));
const carregar = (uf) => {
  const url = new URL(`../../dados/tendencias/${uf}.json`, import.meta.url);
  return (CACHE[uf] ??= pedir(url).catch(() => new Promise((ok) => setTimeout(ok, 400)).then(() => pedir(url)))
    .catch(() => { delete CACHE[uf]; return null; }));
};

const A0 = 2000, A1 = 2026, AGORA = 2027; // AGORA = posição "mais recente" do controle
const sinal = (v, casas = 0) => (v > 0 ? "+" : v < 0 ? "−" : "") + U.num(Math.abs(v), casas);

// ruim: o sentido que pesa contra a roça (+1 = subir é pior, −1 = cair é pior). perto: faixa "perto do normal".
const SERIES = {
  c: { icone: "chuva", rot: "Chuva da estação", ruim: -1, casas: 0, ct: 0, un: " mm",
    val: (v) => `${U.num(v)}<small>mm</small>`, rel: (v, n) => v / n - 1, perto: 0.1,
    sub: (v, n) => `normal ${U.num(n)} mm`,
    frase: "Chuva fraca na estação: roça de sequeiro em risco e chão sem cobertura.",
    sobe: "subindo", desce: "caindo" },
  s: { icone: "solo", rot: "Umidade do solo", ruim: -1, casas: 0, ct: 1, un: " pontos de %",
    val: (v) => `${sinal(v)}<small>%</small>`, rel: (v) => v / 100, perto: 0.05,
    sub: (v) => (Math.abs(v) < 5 ? "perto do normal" : v < 0 ? "mais seco que o normal" : "mais úmido que o normal"),
    frase: "Solo seco na raiz: a planta murcha antes e a vida do solo para.",
    sobe: "mais úmido", desce: "secando" },
  t: { icone: "termo", rot: "Dias mais quentes", ruim: 1, casas: 1, ct: 1, un: " °C",
    val: (v) => `${U.num(v, 1)}<small>°C</small>`, rel: (v, n) => (v - n) / 5, perto: 0.1,
    sub: (v, n) => `normal ${U.num(n, 1)} °C`,
    frase: "Calor acima de 35 °C queima a flor do feijão e do milho.",
    sobe: "esquentando", desce: "esfriando" },
  e: { icone: "sol", rot: "Evaporação", gl: "evapotranspiracao", ruim: 1, casas: 0, ct: 0, un: " mm",
    val: (v) => `${U.num(v)}<small>mm</small>`, rel: (v, n) => v / n - 1, perto: 0.03,
    sub: (v, n) => `normal ${U.num(n)} mm no ano`,
    frase: "Quanto mais o ar puxa, mais rápido a roça e o chão secam.",
    sobe: "subindo", desce: "caindo" },
  v: { icone: "broto", rot: "Verde do satélite", gl: "ndvi", ruim: -1, casas: 0, ct: 1, un: " pontos de %",
    val: (v) => `${sinal(v)}<small>%</small>`, rel: (v) => v / 100, perto: 0.05,
    sub: (v) => (Math.abs(v) < 5 ? "perto do normal" : v < 0 ? "menos verde que o normal" : "mais verde que o normal"),
    frase: "Pouco verde é pasto fraco e chão descoberto, que a chuva forte lava.",
    sobe: "mais verde", desce: "menos verde" },
  a: { icone: "poco", rot: "Água guardada", ruim: -1, casas: 1, ct: 1, un: " cm",
    val: (v) => `${sinal(v, 1)}<small>cm</small>`, rel: (v) => v / 30, perto: 0.1,
    sub: (v) => (v < 0 ? "a menos que em 2004–09" : "a mais que em 2004–09"),
    frase: "Menos água no chão: açude, cacimba e poço secam mais cedo.",
    sobe: "subindo", desce: "caindo" },
};
const ORDEM = ["c", "s", "t", "e", "v", "a"];
// ordem da manchete: o que mais pesa para a roça primeiro
const MANCHETE = [["t", "está esquentando"], ["a", "a água guardada no chão está caindo"], ["c", "a chuva da estação está caindo"],
  ["s", "o solo está secando"], ["v", "o verde está caindo"], ["e", "o ar puxa mais água"]];

let estado = { ano: AGORA }; // fica entre redesenhos do passo

function montar(d, cod) {
  const m = d.mun[cod];
  if (!m) return null;
  const cel = d.cel[m.p], reg = d.reg[m.g], ini = d.meta.ini;
  return {
    c: { ini: ini.c, v: m.c, t: m.tc, prelim: A1 },
    s: { ini: ini.s, v: m.s, t: m.ts },
    t: { ini: ini.t, v: cel?.t || [], t: cel?.tt || [] },
    e: { ini: ini.e, v: cel?.e || [], t: cel?.te || [] },
    v: { ini: ini.v, v: m.v, t: m.tv },
    a: { ini: ini.a, v: reg?.a || [], t: reg?.ta || [], reg: reg?.n },
  };
}

const valor = (s, ano) => s.v[ano - s.ini] ?? null;
function ultimo(s) {
  for (let i = s.v.length - 1; i >= 0; i--) if (s.v[i] != null) return s.ini + i;
  return null;
}
/** o ano a mostrar num cartão: o escolhido ou, na posição "agora", o último com dado */
const anoDe = (s) => (estado.ano === AGORA ? ultimo(s) : estado.ano);

/** sentido do ano frente ao normal: "pior" | "melhor" | "" (perto do normal) */
function lado(def, s, v) {
  const r = def.rel(v, s.t[0]);
  if (!Number.isFinite(r) || Math.abs(r) < def.perto) return "";
  return Math.sign(r) === def.ruim ? "pior" : "melhor";
}

/** O chip da tendência só aparece quando ela é clara (sem ela, o "sobe e desce" fica na tabela do ver mais). */
function chipTendencia(def, s, desde) {
  const [, inc, sig] = s.t;
  if (inc == null || !sig) return "";
  const tit = `${sinal(inc, def.ct)}${def.un} por década (${desde}–2025)`;
  const pior = Math.sign(inc) === def.ruim;
  return `<span class="chip tend-chip ${pior ? "ambar" : "verde"}" title="${U.esc(tit)}"><span class="tend-desde">desde ${desde}: </span>${inc > 0 ? "↑" : "↓"} ${inc > 0 ? def.sobe : def.desce}</span>`;
}

// mini-gráfico: viewBox esticado (preserveAspectRatio none) com traço que não estica; os pontos são traços de comprimento 0
const W = 240, H = 52, P = 5;
const X = (a) => P + ((a - A0) / (A1 - A0)) * (W - 2 * P);
function escala(s) {
  const vs = s.v.filter((v) => v != null).concat(s.t[0] ?? []);
  let lo = Math.min(...vs), hi = Math.max(...vs);
  if (!(hi > lo)) { lo -= 1; hi += 1; }
  return (v) => H - P - ((v - lo) / (hi - lo)) * (H - 2 * P);
}
function grafico(k, s, enso) {
  const Y = escala(s);
  let d = "", caneta = false;
  s.v.forEach((v, i) => {
    const a = s.ini + i;
    if (v == null || a === s.prelim) { caneta = caneta && v != null; return; }
    d += `${caneta ? "L" : "M"}${X(a).toFixed(1)} ${Y(v).toFixed(1)}`;
    caneta = true;
  });
  const vp = s.prelim ? valor(s, s.prelim) : null, va = s.prelim ? valor(s, s.prelim - 1) : null;
  const prelim = vp != null && va != null
    ? `<path class="tend-prelim" d="M${X(s.prelim - 1).toFixed(1)} ${Y(va).toFixed(1)}L${X(s.prelim).toFixed(1)} ${Y(vp).toFixed(1)}"/>` : "";
  const faixas = enso.map((a) => `<rect class="tend-enso" x="${(X(a) - 3).toFixed(1)}" y="0" width="6" height="${H}"/>`).join("");
  const normal = s.t[0] != null ? `<path class="tend-normal" d="M${P} ${Y(s.t[0]).toFixed(1)}H${W - P}"/>` : "";
  return `<svg class="tend-linha" data-k="${k}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img"
    aria-label="${U.esc(SERIES[k].rot)} ano a ano">${faixas}${normal}<path class="tend-serie" d="${d}"/>${prelim}<g class="tend-cursor"></g></svg>`;
}
function cursor(k, s) {
  const ano = anoDe(s), v = ano == null ? null : valor(s, ano);
  if (ano == null) return "";
  const x = X(ano).toFixed(1), def = SERIES[k];
  const ponto = v == null ? "" : `<path class="tend-ponto ${lado(def, s, v)}" d="M${x} ${escala(s)(v).toFixed(1)}h0"/>`;
  return `<path class="tend-cur" d="M${x} 0V${H}"/>${ponto}`;
}

function textoCartao(k, s) {
  const def = SERIES[k], ano = anoDe(s), v = ano == null ? null : valor(s, ano);
  if (v == null) return { val: "—", sub: !ano ? "sem dado" : ano < s.ini ? `o satélite começa em ${s.ini}` : `sem dado em ${ano}` };
  const quando = `${ano}${s.prelim === ano ? " (preliminar)" : ""}`;
  return { val: def.val(v), sub: `${quando} · ${def.sub(v, s.t[0])}`, lado: lado(def, s, v) };
}

function cartao(k, s, d, enso) {
  const def = { ...SERIES[k], k }, tx = textoCartao(k, s);
  const desde = Math.max(s.ini, A0);
  // um selo só, no título do bloco; a fonte de cada série fica no ver mais
  return `<div class="tend-cartao" data-k="${k}">
    <div class="tend-rot">${U.ic(def.icone)}<span>${def.gl ? termo(def.gl, def.rot) : U.esc(def.rot)}${k === "a" ? ` <em>· região</em>` : ""}</span></div>
    <div class="tend-meio">
      <div class="tend-num"><div class="tend-val ${tx.lado || ""}">${tx.val}</div>${chipTendencia(def, s, desde)}</div>
      ${grafico(k, s, enso)}
    </div>
    <div class="tend-sub">${tx.sub}</div>
    <p class="tend-frase"${tx.lado === "pior" ? "" : " hidden"}>${U.esc(def.frase)}</p>
  </div>`;
}

/** No celular, 1 frase só para o bloco: a da 1ª série do lado ruim no ano mostrado (na ordem da manchete). */
function fraseBloco(S, ks) {
  const k = MANCHETE.map(([k]) => k).find((k) => ks.includes(k) && textoCartao(k, S[k]).lado === "pior");
  return k ? `${U.ic(SERIES[k].icone)}<span>${U.esc(SERIES[k].frase)}</span>` : "";
}

function manchete(r, S, ks) {
  const ditos = MANCHETE.filter(([k]) => ks.includes(k) && S[k].t[2] && S[k].t[1] != null && Math.sign(S[k].t[1]) === SERIES[k].ruim)
    .map(([, f]) => f).slice(0, 2);
  const nome = U.esc(r.local.municipio);
  if (!ditos.length) return `Em ${nome}, o tempo sobe e desce, sem piora clara desde 2000.`;
  return `Em ${nome}, ${ditos.join(" e ")}.`;
}

function detalhe(d, S, ks, r) {
  const linhas = ks.map((k) => {
    const s = S[k], def = SERIES[k], [n, inc, sig] = s.t;
    const extra = k === "t" && s.t[3] != null ? `; desde 1981: ${sinal(s.t[3], 2)} °C por década` : "";
    return `<tr><td>${U.esc(def.rot)}</td><td class="sub pequeno">${U.esc(d.meta.fontes[k])}${k === "a" && s.reg ? ` Região: ${U.esc(s.reg)}.` : ""}</td>
      <td>${inc == null ? "—" : `${sinal(inc, def.ct)}${def.un}${sig ? "" : " (sem tendência clara)"}${extra}`}</td></tr>`;
  }).join("");
  const leste = /litoral leste/.test(r?.este_ano?.regime?.texto || "")
    ? `<p><b>Litoral leste:</b> aqui o IMERG capta só 39–72% da chuva medida no pluviômetro; a linha da chuva mostra o sobe e desce, não o total certo.</p>` : "";
  return `<p>Cada base vem numa grade diferente: chuva IMERG ~11 km, umidade SMAP ~9 km, verde MODIS 500 m, calor e evaporação NASA POWER ~55 km,
    água guardada GRACE ~300 km. Aqui todas foram levadas ao município do IBGE (média das células com centro dentro dele, ou a mais próxima);
    o GRACE vai para a mesorregião, porque não enxerga menos que isso.</p>
    <table><tr><th>Série</th><th>Fonte e conta</th><th>Tendência por década</th></tr>${linhas}</table>
    <p>Tendência: inclinação de Theil–Sen nos anos completos (até 2025); "sobe e desce" quando o teste de Mann–Kendall não passa de p &lt; 0,10.
    Faixa âmbar: anos de El Niño forte (2010, 2016, 2024). Linha tracejada: o normal. É o que já aconteceu, não é previsão.</p>${leste}`;
}

export default {
  id: "tendencias",
  async render(el, ctx, opcoes = {}) {
    const r = ctx.r, cod = String(ctx.cod || r?.local?.cod || "");
    const ks = (opcoes.series || ORDEM).filter((k) => SERIES[k]);
    const d = await carregar(r?.local?.uf || "");
    const S = d && montar(d, cod);
    if (!S) {
      el.innerHTML = `<div class="painel tend"><h3>Como o seu lugar está mudando</h3><p class="sub">As séries do satélite deste município não carregaram.</p></div>`;
      return;
    }
    const enso = d.meta.el_nino_forte || [];
    el.innerHTML = `<div class="painel tend">
      <div class="tend-topo">
        <div><h3>Como o seu lugar está mudando ${U.selo("medido", "NASA (IMERG, SMAP, MODIS, POWER, GRACE) por município; fontes no ver mais")}</h3>
          <p class="tend-manchete">${manchete(r, S, ks)}</p></div>
      </div>
      <div class="tend-grade">${ks.map((k) => cartao(k, S[k], d, enso)).join("")}</div>
      <p class="tend-frase-bloco"></p>
      <p class="tend-legenda"><i class="tend-l-normal"></i>normal <i class="tend-l-enso"></i>El Niño forte
        <span>Toque para ver o ano.</span></p>
      <p class="tend-local">${U.ic("info")} O satélite vê a região; a sua roça confirma ou corrige.</p>
      ${U.verMais(detalhe(d, S, ks, r), "Ver de onde vêm as séries")}
    </div>`;

    const grade = el.querySelector(".tend-grade");
    const pintar = () => {
      el.querySelectorAll(".tend-cartao").forEach((c) => {
        const k = c.dataset.k, s = S[k], tx = textoCartao(k, s);
        const val = c.querySelector(".tend-val");
        val.innerHTML = tx.val;
        val.className = `tend-val ${tx.lado || ""}`;
        c.querySelector(".tend-sub").textContent = tx.sub;
        c.querySelector(".tend-frase").hidden = tx.lado !== "pior";
        c.querySelector(".tend-cursor").innerHTML = cursor(k, s);
      });
      const fb = el.querySelector(".tend-frase-bloco");
      fb.innerHTML = fraseBloco(S, ks);
      fb.hidden = !fb.innerHTML;
    };
    const anoDoPonteiro = (ev) => {
      const svg = ev.target.closest?.("svg.tend-linha");
      if (!svg) return null;
      const q = svg.getBoundingClientRect(), x = ((ev.clientX - q.left) / q.width) * W;
      return Math.max(A0, Math.min(A1, Math.round(A0 + ((x - P) / (W - 2 * P)) * (A1 - A0))));
    };
    let fixo = estado.ano;
    const mostrar = (ano) => { estado.ano = ano; pintar(); };
    grade.addEventListener("click", (ev) => { const a = anoDoPonteiro(ev); if (a) { fixo = a; mostrar(a); } });
    grade.addEventListener("pointermove", (ev) => {
      if (ev.pointerType !== "mouse") return;
      const a = anoDoPonteiro(ev);
      if (a && a !== estado.ano) mostrar(a); else if (!a && estado.ano !== fixo) mostrar(fixo);
    });
    grade.addEventListener("pointerleave", () => { if (estado.ano !== fixo) mostrar(fixo); });
    pintar();
  },
};
