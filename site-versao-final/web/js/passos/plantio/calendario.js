// QUADRA, passo "Como plantar": calendário de plantio e colheita (hoje até dez/2027).
// Porte do cartaoCalendario do protótipo do José (protótipo/static/app.js, branch estudo-jose, e7a23b5) para os tokens de quadra.css,
// com "O que fazer agora" como lista de marcar e o passo a passo num <details>.

const FASES = {
  preparo: "preparo sem fogo", risco: "dá para plantar, com mais risco (até 40%)", plantio: "plantar (janela do ZARC)",
  estimado: "plantar (janela estimada, sem ZARC)", roca: "na roça, crescendo", colheita: "colher", pousio: "pousio pastejado",
};

const chave = (cod) => `quadra-agora-${cod}`;
function lerFeitos(cod) { try { return new Set(JSON.parse(localStorage.getItem(chave(cod)) || "[]")); } catch (_) { return new Set(); } }
function gravarFeitos(cod, s) { try { localStorage.setItem(chave(cod), JSON.stringify([...s])); } catch (_) { /* sem armazenamento: vale só nesta visita */ } }

/** A data de plantar é do ZARC quando a fonte começa por "ZARC"; estimada pela chuva ou pelo revezamento é suposição. */
export const seloPlantar = (U, fonte) => (/^ZARC/.test(fonte || "")
  ? U.selo("medido", fonte) : U.selo("suposicao", fonte || "janela estimada"));

export function cartaoCalendario(ctx) {
  const U = ctx.util, esc = U.esc, a = ctx.r.agenda;
  if (!a) return `<div class="cartao"><h2>Quando plantar e quando colher</h2><p class="sub">Sem calendário para este lugar.</p></div>`;
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
  let h = `<div class="cartao cal" id="plantio-calendario"><h2>Quando plantar e quando colher (hoje até dez/2027)</h2>
    <div class="agora"><h3>O que fazer agora (${esc(a.hoje_txt)})</h3>
      <ul class="agora-lista">${a.agora.map((t, i) => `<li><label><input type="checkbox" data-agora="${i}"${feitos.has(t) ? " checked" : ""}>
        <span>${esc(t)}</span></label></li>`).join("")}</ul>
      <p class="sub pequeno">As datas de plantar vêm do ZARC ${U.selo("medido", "ZARC 2026/27 e portarias plurianuais do MAPA; fonte de cada linha no passo a passo")}.
      Marque o que já fez: fica guardado só neste aparelho.</p></div>
    <p class="sub">Cada linha é uma parte do roçado. Barra de cima: <b>quando plantar</b> ${U.selo("medido", "janela do ZARC (ou estimada pelo início da chuva, onde não há ZARC)")}.
    Barra de baixo: a cultura <b>na roça</b> e a <b>colheita</b> ${U.selo("suposicao", "colheita = janela de plantio + ciclo da cultura; os ciclos sem fonte estão marcados no passo a passo")}.
    Linha vermelha: hoje. Círculos: os marcos do ano (toque ou passe o mouse). Solo: ${esc(a.solo)}.</p>
    <div class="g-legenda">${Object.entries(FASES).map(([k, v]) => `<span><i class="b-${k}"></i>${v}</span>`).join("")}
      <span><i class="g-decide-chave"></i>decisão</span></div>
    <div class="gantt-caixa"><div class="gantt">
      <div class="g-linha g-cab"><div class="g-rot"></div><div class="g-trilho">${cab}</div></div>
      <div class="g-linha g-marcos"><div class="g-rot"><b>Marcos</b></div><div class="g-trilho">${grade}${marcos}</div></div>
      ${a.linhas.map(linha).join("")}
    </div></div>`;
  if (a.nota_portoes) h += `<p class="aviso">${esc(a.nota_portoes)}</p>`;
  h += `<h3>Marcos do ano ${U.selo("suposicao", "portões da proposta QUADRA (calibrados no sertão do CE); as datas de plantar dentro deles vêm do ZARC")}</h3>
    <ol class="marcos">${a.marcos.map((m) => `<li><b>${esc(m.dia)} · ${esc(m.rotulo)}.</b> ${esc(m.texto)}</li>`).join("")}</ol>`;
  h += `<details><summary>Passo a passo, parte por parte (plantar, colher e de onde vem cada data)</summary>
    <ul class="passo-a-passo">${a.linhas.map((l) => `<li class="${U.tipoCss(l.tipo)}"><b>${esc(l.parte)} · ${esc(l.cultura)}</b>${l.estacao > 2027 ? ` <span class="sub">(estação ${l.estacao})</span>` : ""}
      <div><span class="pp-rot">Plantar</span> ${esc(l.plantar)} ${seloPlantar(U, l.fonte)}</div>
      <div><span class="pp-rot">Colher</span> ${esc(l.colher)} ${U.selo("suposicao", "janela de plantio + ciclo da cultura")}</div>
      <div class="sub pequeno">Fonte: ${esc(l.fonte)}</div></li>`).join("")}</ul>
    <p class="sub pequeno">A colheita vem da janela de plantio mais o ciclo da cultura (dias do plantio à colheita). Plantou num dia da
    janela? Some o ciclo àquele dia.</p></details>`;
  return h + `</div>`;
}

/** Liga a lista de marcar (guarda o texto de cada item feito, por município). */
export function ligarCalendario(el, ctx) {
  const a = ctx.r.agenda;
  if (!a) return;
  el.querySelectorAll("[data-agora]").forEach((cx) => cx.addEventListener("change", () => {
    const s = lerFeitos(ctx.cod), t = a.agora[+cx.dataset.agora];
    if (cx.checked) s.add(t); else s.delete(t);
    gravarFeitos(ctx.cod, s);
  }));
}
