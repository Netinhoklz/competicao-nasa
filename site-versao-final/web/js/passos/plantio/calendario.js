// QUADRA, passo "Como plantar": o que fazer e quando (hoje até dez/2027).
// Na frente: a frase do "Agora" (agora(), vai sob o título do passo) e uma linha do tempo de 3 cartões, tiradas de agenda.linhas
// (janelas de plantio e de colheita) e agenda.agora.
// No "ver mais": o Gantt do protótipo do José (cartaoCalendario em protótipo/static/app.js, branch estudo-jose, e7a23b5), a lista
// de marcar, a nota dos portões, os marcos e o passo a passo, com os tokens de quadra.css.
// Rodada 2 (analise/fluxo2/BRIEFING.md, D3): o Plano mostra "Seu jeito, melhorado" ou "O ideal" (extras/ideal.js, escolhido()). Toda
// função daqui aceita a agenda do plano à vista no último argumento (a = agendaDoPlano(r.agenda, escolhido(...).linhas)); sem ele,
// vale ctx.r.agenda, como antes.

const FASES = {
  preparo: "preparo sem fogo", risco: "dá para plantar, com mais risco (até 40%)", plantio: "plantar (janela do ZARC)",
  estimado: "plantar (janela estimada, sem ZARC)", roca: "na roça, crescendo", colheita: "colher", pousio: "pousio pastejado",
};
const NOME = { "Feijão-caupi": "feijão", "Sorgo forrageiro": "sorgo", "Sorgo granífero": "sorgo de grão", "Feijão comum": "feijão comum",
  "Palma + gliricídia": "palma", "Palma forrageira": "palma", "Mucuna-preta": "mucuna", "Algodão herbáceo": "algodão",
  "Cana-de-açúcar": "cana" }; // o "onde" do cartão diz o lugar (bordas, baixio)
const nome = (c) => { const b = String(c || "").replace(/ no milho em pé$/, ""); return NOME[b] || b.toLowerCase(); };
const LUGAR = (p) => (p === "Baixio" ? "baixio" : p === "Bordas" ? "bordas" : p);
const lista = (v) => (v.length <= 1 ? v.join("") : v.slice(0, -1).join(", ") + " e " + v[v.length - 1]);

const chave = (cod) => `quadra-agora-${cod}`;
function lerFeitos(cod) { try { return new Set(JSON.parse(localStorage.getItem(chave(cod)) || "[]")); } catch (_) { return new Set(); } }
function gravarFeitos(cod, s) { try { localStorage.setItem(chave(cod), JSON.stringify([...s])); } catch (_) { /* sem armazenamento: vale só nesta visita */ } }

/** A data de plantar é do ZARC quando a fonte começa por "ZARC"; estimada pela chuva ou pelo revezamento é suposição. */
export const seloPlantar = (U, fonte) => (/^ZARC/.test(fonte || "")
  ? U.selo("medido", fonte) : U.selo("suposicao", fonte || "janela estimada"));

/** Eventos da agenda: começo da janela de plantar, começo da colheita e o primeiro preparo da terra. */
function eventos(a) {
  const hoje = a.hoje, ev = [];
  let preparo = null;
  for (const l of a.linhas) {
    const pl = l.barras.find((b) => b.tipo === "plantio" || b.tipo === "estimado");
    if (pl && pl.ate >= hoje) ev.push({ tipo: "plantar", de: pl.de, ate: pl.ate, nome: nome(l.cultura), cultura: l.cultura, onde: LUGAR(l.parte), suposto: !/^ZARC/.test(l.fonte || "") });
    const co = l.barras.find((b) => b.tipo === "colheita");
    if (co && co.ate >= hoje) ev.push({ tipo: "colher", de: co.de, ate: co.ate, nome: nome(l.cultura), onde: LUGAR(l.parte), suposto: true });
    const pr = l.barras.find((b) => b.tipo === "preparo");
    if (pr && l.parte !== "Bordas" && pr.de > hoje && (!preparo || pr.de < preparo.de)) preparo = { tipo: "preparo", de: pr.de, ate: pr.ate, nome: "", onde: "", suposto: true };
  }
  if (preparo) ev.push(preparo);
  return ev.sort((x, y) => (x.de < y.de ? -1 : x.de > y.de ? 1 : 0));
}

const abertas = (a, ev) => ev.filter((e) => e.tipo === "plantar" && e.de <= a.hoje); // janelas de plantar que já abriram

/** Começo da janela de plantar de cada cultura antes da última resposta em Sua roça (sessionStorage["quadra.antes"] =
 *  {cod, jan: {cultura: "dd/mm a dd/mm"}}, gravado por passos/perguntas.js); {} sem armazenamento ou noutro município. */
function iniciosAntes(cod) {
  try {
    const o = JSON.parse(sessionStorage.getItem("quadra.antes") || "{}") || {};
    if (o.cod !== cod) return {}; // as janelas de antes são de outro município (ou de um formato velho): não compara
    return Object.fromEntries(Object.entries(o.jan || {}).map(([c, v]) => [c, String(v).slice(0, 5)]));
  } catch (_) { return {}; }
}

const dm = (iso) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}`;
const dmy = (iso) => `${dm(iso)}/${iso.slice(0, 4)}`;

/** O "o que fazer agora" de um plano que não é o do núcleo (as linhas de extras/ideal.js agendaDe): os itens do núcleo que citam uma
 *  parte ("Prepare Mandioca (Parte A): …") são refeitos com as linhas do plano, com as mesmas palavras; os outros ficam só quando a
 *  cultura deles está no plano (semente de caupi, maniva, mudas de palma); Garantia-Safra e "nada de fogo" ficam sempre. */
function agoraDoPlano(a, linhas) {
  const hoje = a.hoje, out = [];
  const novas = linhas.filter((l) => !/em pé/.test(l.cultura) && l.tipo !== "pousio" && !/^já /.test(l.plantar || ""));
  const E0 = Math.min(...novas.map((l) => l.estacao).filter(Number.isFinite));
  for (const l of novas.filter((x) => x.estacao === E0)) {
    const p1 = (l.barras || []).filter((b) => b.pista === 1 && ["risco", "plantio", "estimado"].includes(b.tipo));
    const pl = p1.find((b) => b.tipo !== "risco");
    if (!pl || pl.ate < hoje) continue;
    const onde = `${l.cultura} (${l.parte})${pl.tipo === "estimado" ? ", janela estimada" : ""}`, ini = p1[0];
    if (ini.de > hoje) out.push(`Prepare ${onde}: plantar ${String(l.plantar || "").replace(/; ano de alerta.*$/, "")}.`);
    else if (ini.tipo === "risco" && pl.de > hoje) out.push(`Já dá para plantar ${onde}, com mais risco (até 40%); a janela melhor vai de ${dm(pl.de)} a ${dm(pl.ate)}.`);
    else out.push(`Janela aberta agora: ${onde}, até ${dmy(pl.ate)}.`);
  }
  const tem = (re) => novas.some((l) => re.test(l.cultura));
  for (const t of a.agora || []) {
    if (/\((Parte [ABC]|Baixio|Bordas)\)/.test(t)) continue; // por parte: refeito acima com as partes deste plano
    if (/caupi/i.test(t) && !tem(/caupi/i)) continue;
    if (/maniva/i.test(t) && !tem(/^Mandioca/)) continue;
    if (/mudas de palma|gliric/i.test(t) && !tem(/^Palma|^Gliric/)) continue;
    out.push(t);
  }
  return out;
}

/** A agenda do plano à vista: r.agenda com as linhas do plano (extras/ideal.js, agendaDe ou escolhido().linhas) e o "o que fazer
 *  agora" refeito para elas. Para as linhas do núcleo (r.agenda.linhas), devolve r.agenda sem mudar. */
export function agendaDoPlano(a, linhas) {
  if (!a || !Array.isArray(linhas) || linhas === a.linhas) return a;
  return { ...a, linhas, agora: agoraDoPlano(a, linhas) };
}

/** A frase do "Agora", para a faixa sob o título do passo: a janela de plantar que já abriu ou, antes dela, o que juntar
 *  ("junte semente, maniva e mudas; nada de fogo."). Era o 1º cartão da linha do tempo; saiu de lá para não repetir. */
export function agora(ctx, a = ctx.r.agenda) {
  const U = ctx.util;
  if (!a) return "";
  const ab = abertas(a, eventos(a));
  if (ab.length) return `já dá para plantar ${lista([...new Set(ab.map((e) => e.nome))])}, até ${U.dataBR(ab.map((e) => e.ate).sort()[0], true)}.`;
  const junta = [["semente", "semente"], ["maniva", "maniva"], ["mudas", "mudas"]].filter(([k]) => a.agora.some((t) => t.toLowerCase().includes(k))).map(([, v]) => v);
  return `${junta.length ? `junte ${lista(junta)}` : "prepare a semente"}; nada de fogo.`;
}

/** A linha do tempo "o que fazer e quando": 3 cartões depois do "Agora" (2 plantios e 1 colheita). */
export function linhaDoTempo(ctx, a = ctx.r.agenda) {
  const U = ctx.util, esc = U.esc;
  if (!a) return "";
  const ev = eventos(a), abertos = abertas(a, ev);
  const cartoes = [];
  // os próximos, agrupados por mês e por tipo de tarefa (a janela que já abriu está no "Agora")
  const grupos = new Map();
  for (const e of ev) {
    if (abertos.includes(e) || (e.tipo !== "preparo" && e.de <= a.hoje)) continue;
    const k = `${e.de.slice(0, 7)}|${e.tipo}`;
    if (!grupos.has(k)) grupos.set(k, { tipo: e.tipo, de: e.de, cultura: e.cultura, nomes: [], onde: [], suposto: false }); // cultura: a que dá a data
    const g = grupos.get(k);
    if (e.nome && !g.nomes.includes(e.nome)) g.nomes.push(e.nome);
    if (e.onde && !g.onde.includes(e.onde)) g.onde.push(e.onde);
    g.suposto = g.suposto || e.suposto;
  }
  const todos = [...grupos.values()]; // já em ordem de data
  // 3 cartões depois do "Agora": os 2 primeiros plantios do roçado e a 1ª colheita (o preparo e a cerca ficam no calendário completo,
  // e o "Agora" já diz "nada de fogo"); se faltar, completa pela data
  const doRocado = (g) => g.tipo !== "preparo" && g.onde.some((o) => o !== "bordas");
  let escolha = [...todos.filter((g) => g.tipo === "plantar" && doRocado(g)).slice(0, 2), ...todos.filter((g) => g.tipo === "colher" && doRocado(g)).slice(0, 1)];
  for (const g of todos) if (escolha.length < 3 && !escolha.includes(g)) escolha.push(g);
  escolha.sort((x, y) => (x.de < y.de ? -1 : x.de > y.de ? 1 : 0));
  const COR = { plantar: ["semente", "verde"], colher: ["celeiro", "ambar"], preparo: ["enxada", ""] };
  // "era dd/mm" quando a resposta mudou a janela da cultura que dá a data do cartão (as duas pontas tiradas de agenda.culturas)
  const velho = iniciosAntes(ctx.cod), novo = Object.fromEntries((a.culturas || []).map((c) => [c.cultura, String(c.plantar || "").replace(/^de /, "").slice(0, 5)]));
  for (const g of escolha) {
    const [icone, cor] = COR[g.tipo];
    const frase = g.tipo === "preparo" ? "Prepare a terra, sem fogo" : `${g.tipo === "plantar" ? "Plante" : "Colha"} ${lista(g.nomes)}`;
    const antes = g.tipo === "plantar" && velho[g.cultura] && novo[g.cultura] && velho[g.cultura] !== novo[g.cultura] ? velho[g.cultura] : "";
    cartoes.push({ quando: U.MESES[+g.de.slice(5, 7) - 1], data: U.dataBR(g.de, true), icone, cor, frase, antes,
      onde: g.tipo === "preparo" ? ["palhada no chão"] : g.onde, suposto: g.suposto, colheita: g.tipo === "colher" });
  }
  const fonteSelo = "datas de plantar da tábua oficial do Ministério da Agricultura (ZARC 2026/27); as marcadas como suposição são estimadas " +
    "(início da chuva, ciclo da cultura até a colheita, preparo um mês antes)";
  return `<ol class="tempo" style="--n:${cartoes.length}">${cartoes.map((c) => `<li class="tempo-c${c.colheita ? " colhe" : ""}">
      <span class="bola ${c.cor}">${U.ic(c.icone)}</span>
      <div class="tempo-q">${esc(c.quando)} <span>${esc(c.data)}</span>${c.antes ? ` <span class="tempo-antes">· era ${esc(c.antes)}</span>` : ""}${c.suposto ? " " + U.selo("suposicao", fonteSelo) : ""}</div>
      <b>${esc(c.frase)}</b><small>${esc(c.onde.join(" · "))}</small></li>`).join("")}</ol>`;
}

/** O calendário completo (vai dentro do "ver mais"). */
export function calendarioCompleto(ctx, a = ctx.r.agenda) {
  const U = ctx.util, esc = U.esc;
  if (!a) return `<p>Sem calendário para este lugar.</p>`;
  const t0 = Date.parse(a.inicio), T = Date.parse(a.fim) + 864e5 - t0;
  const x = (d) => ((Date.parse(d) - t0) / T) * 100;
  const w = (de, ate) => ((Date.parse(ate) + 864e5 - Date.parse(de)) / T) * 100;
  const meses = [];
  for (let y = +a.inicio.slice(0, 4), m = +a.inicio.slice(5, 7); `${y}-${String(m).padStart(2, "0")}` <= a.fim.slice(0, 7); m = m % 12 + 1, y += m === 1 ? 1 : 0)
    meses.push(`${y}-${String(m).padStart(2, "0")}-01`);
  const grade = meses.map((d) => `<span class="g-mes" style="left:${x(d)}%"></span>`).join("") + `<span class="g-hoje" style="left:${x(a.hoje)}%"></span>`;
  const cab = meses.map((d, i) => {
    const fim = i + 1 < meses.length ? x(meses[i + 1]) : 100, m = +d.slice(5, 7);
    return `<span class="g-mes-rot" style="left:${x(d)}%;width:${fim - x(d)}%">${U.MESES[m - 1]}${m === 1 || i === 0 ? `<small>${d.slice(0, 4)}</small>` : ""}</span>`;
  }).join("");
  const marcos = a.marcos.map((m, i) => `<span class="g-marco ${i % 2 ? "baixo" : "alto"}${m.rotulo === "Hoje" ? " hoje" : ""}" style="left:${x(m.data)}%"
    title="${esc(m.dia)} · ${esc(m.rotulo)}: ${esc(m.texto)}">${i + 1}</span>`).join("");
  const barra = (b) => {
    const larg = w(b.de, b.ate), txt = { plantio: "plantar", estimado: "plantar", colheita: "colher", pousio: "pousio" }[b.tipo];
    return `<span class="g-barra b-${b.tipo} p${b.pista}${b.segue ? " segue" : ""}" style="left:${x(b.de)}%;width:${larg}%"
      title="${esc(b.rotulo)}">${txt && larg > 7 ? txt : ""}</span>`;
  };
  const linha = (l) => `<div class="g-linha"><div class="g-rot ${U.tipoCss(l.tipo)}"><b>${esc(l.parte)}${l.estacao > 2027 ? ` <small>· estação ${l.estacao}</small>` : ""}</b>
    <span>${esc(l.cultura)}</span></div><div class="g-trilho">${grade}${l.barras.map(barra).join("")}
    ${(l.marcos || []).map((m) => `<span class="g-decide" style="left:${x(m.data)}%" title="${esc(m.rotulo)}"></span>`).join("")}</div></div>`;

  const feitos = lerFeitos(ctx.cod);
  let h = `<h4>O que fazer agora (${esc(a.hoje_txt)})</h4>
    <ul class="agora-lista">${a.agora.map((t, i) => `<li><label><input type="checkbox" data-agora="${i}"${feitos.has(t) ? " checked" : ""}>
      <span>${esc(t)}</span></label></li>`).join("")}</ul>
    <p class="pequeno">Marque o que já fez: fica guardado só neste aparelho.</p>
    <h4>Calendário, parte por parte</h4>
    <p>Barra de cima: quando plantar ${U.selo("medido", "janela do ZARC 2026/27 (ou estimada pelo início da chuva no IMERG, onde não há ZARC)")}.
    Barra de baixo: a cultura na roça e a colheita ${U.selo("suposicao", "colheita = janela de plantio + ciclo da cultura; os ciclos sem fonte estão no passo a passo")}.
    Linha vermelha: hoje. Círculos: os marcos. Solo: ${esc(a.solo)}.</p>
    <div class="g-legenda">${Object.entries(FASES).map(([k, v]) => `<span><i class="b-${k}"></i>${v}</span>`).join("")}
      <span><i class="g-decide-chave"></i>decisão</span></div>
    <div class="gantt-caixa"><div class="gantt">
      <div class="g-linha g-cab"><div class="g-rot"></div><div class="g-trilho">${cab}</div></div>
      <div class="g-linha g-marcos"><div class="g-rot"><b>Marcos</b></div><div class="g-trilho">${grade}${marcos}</div></div>
      ${a.linhas.map(linha).join("")}
    </div></div>`;
  if (a.nota_portoes) h += `<p class="aviso">${esc(a.nota_portoes)}</p>`;
  h += `<h4>Marcos do ano ${U.selo("suposicao", "portões da proposta QUADRA (calibrados no sertão do CE); as datas de plantar dentro deles vêm do ZARC")}</h4>
    <ol class="marcos">${a.marcos.map((m) => `<li><b>${esc(m.dia)} · ${esc(m.rotulo)}.</b> ${esc(m.texto)}</li>`).join("")}</ol>
    <h4>Passo a passo (plantar, colher e de onde vem cada data)</h4>
    <ul class="passo-a-passo">${a.linhas.map((l) => `<li class="${U.tipoCss(l.tipo)}"><b>${esc(l.parte)} · ${esc(l.cultura)}</b>${l.estacao > 2027 ? ` (estação ${l.estacao})` : ""}
      <div><span class="pp-rot">Plantar</span> ${esc(l.plantar)} ${seloPlantar(U, l.fonte)}</div>
      <div><span class="pp-rot">Colher</span> ${esc(l.colher)} ${U.selo("suposicao", "janela de plantio + ciclo da cultura")}</div>
      <div class="pequeno">Fonte: ${esc(l.fonte)}</div></li>`).join("")}</ul>
    <p class="pequeno">A colheita vem da janela de plantio mais o ciclo da cultura. Plantou num dia da janela? Some o ciclo àquele dia.</p>`;
  return h;
}

/** Liga a lista de marcar (guarda o texto de cada item feito, por município). */
export function ligarCalendario(el, ctx, a = ctx.r.agenda) {
  if (!a) return;
  el.querySelectorAll("[data-agora]").forEach((cx) => cx.addEventListener("change", () => {
    const s = lerFeitos(ctx.cod), t = a.agora[+cx.dataset.agora];
    if (cx.checked) s.add(t); else s.delete(t);
    gravarFeitos(ctx.cod, s);
  }));
}
