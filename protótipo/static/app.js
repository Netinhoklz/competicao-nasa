// QUADRA protótipo (Nordeste): mapa + painel. Os dados vêm de /api/local (motor.py).
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const num = (v, d = 0) => (v === null || v === undefined ? "—" : Number(v).toLocaleString("pt-BR", { maximumFractionDigits: d, minimumFractionDigits: d }));

const mapa = L.map("mapa", { worldCopyJump: true, preferCanvas: true }).setView([-9.0, -40.5], 6);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · malha municipal IBGE', maxZoom: 18,
}).addTo(mapa);
let camadaMun = null, marcador = null, pedido = 0, ultimo = null, ponto = null;
const solo = { textura: "", ad: "" }; // seletor de solo (revisão A7): "" = não sei (melhor caso entre os solos)
const urlLocal = (lat, lon) => `/api/local?lat=${lat}&lon=${lon}&textura=${solo.textura}&ad=${solo.ad}`;
document.addEventListener("change", async (e) => {
  if (!e.target.matches(".sel-solo") || !ultimo) return;
  solo[e.target.dataset.esquema] = e.target.value;
  document.getElementById("c-plantar").outerHTML = cartaoCardapio(ultimo);
  // o solo muda as janelas do calendário e a data da maniva no plano: pede de novo só isso
  const meu = ++pedido;
  try {
    const r = await (await fetch(urlLocal(ponto.lat, ponto.lon))).json();
    if (meu !== pedido || r.erro || !document.getElementById("c-calendario")) return;
    ultimo = r;
    document.getElementById("c-calendario").outerHTML = cartaoCalendario(r);
    document.getElementById("c-rotacao").outerHTML = cartaoPlano(r);
  } catch (_) { /* o cardápio já foi redesenhado; o calendário fica como estava */ }
});
const municipios = {};
const ESTILO = { color: "#1f6b3a", weight: 0.4, fillOpacity: 0.02 };

fetch("/api/municipios").then((r) => r.json()).then((gj) => {
  camadaMun = L.geoJSON(gj, {
    style: ESTILO,
    onEachFeature: (f, l) => {
      const p = f.properties;
      municipios[`${p.nome} (${p.uf})`] = p;
      l.bindTooltip(`${p.nome} (${p.uf})`, { sticky: true });
    },
  }).addTo(mapa);
  const lista = document.getElementById("lista-mun");
  Object.keys(municipios).sort((a, b) => a.localeCompare(b, "pt-BR")).forEach((n) => {
    const o = document.createElement("option"); o.value = n; lista.appendChild(o);
  });
});

function destacar(cod) {
  if (!camadaMun) return;
  camadaMun.eachLayer((l) => {
    const sel = l.feature.properties.cod === cod;
    l.setStyle(sel ? { color: "#b8730f", weight: 2.5, fillOpacity: 0.15 } : ESTILO);
  });
}

async function consultar(lat, lon) {
  const meu = ++pedido; // só a resposta do pedido mais novo é desenhada (revisão A19)
  if (marcador) marcador.remove();
  marcador = L.circleMarker([lat, lon], { radius: 7, color: "#a8321e", weight: 2, fillOpacity: 0.7 }).addTo(mapa);
  document.getElementById("vazio").classList.add("oculto");
  document.getElementById("carregando").classList.remove("oculto");
  document.getElementById("resultado").innerHTML = "";
  try {
    ponto = { lat, lon };
    const resp = await fetch(urlLocal(lat, lon));
    const r = await resp.json();
    if (meu !== pedido) return;
    if (r.erro) throw new Error(r.erro);
    ultimo = r;
    destacar(r.local.cod);
    const nav = `<nav class="nav-painel"><a href="#c-local">Lugar</a><a href="#c-ano">Este ano</a><a href="#c-plantar">O que plantar</a>
      <a href="#c-calendario" class="destaque">Calendário</a><a href="#c-rotacao" class="destaque">Rotação</a><a href="#c-evidencia">Evidência</a></nav>`;
    document.getElementById("resultado").innerHTML = nav + [cartaoLocal(r), cartaoAno(r), cartaoCardapio(r), cartaoCalendario(r), cartaoPlano(r), cartaoEvidencia(r), cartaoFontes(r)].join("");
  } catch (e) {
    if (meu === pedido) document.getElementById("resultado").innerHTML = `<div class="cartao alerta">Erro na consulta: ${esc(e.message)}</div>`;
  } finally {
    if (meu === pedido) document.getElementById("carregando").classList.add("oculto");
  }
}

mapa.on("click", (e) => { const p = e.latlng.wrap(); consultar(+p.lat.toFixed(4), +p.lng.toFixed(4)); });
document.getElementById("busca").addEventListener("change", (e) => {
  const m = municipios[e.target.value];
  if (!m) return;
  mapa.setView([m.lat, m.lon], 9);
  consultar(m.lat, m.lon);
});
document.querySelectorAll(".atalhos button").forEach((b) => b.addEventListener("click", () => {
  const lat = +b.dataset.lat, lon = +b.dataset.lon;
  mapa.setView([lat, lon], Math.abs(lon) > 60 ? 6 : 8);
  consultar(lat, lon);
}));
const _q = new URLSearchParams(location.search);
if (_q.has("lat") && _q.has("lon")) {
  const lat = +_q.get("lat"), lon = +_q.get("lon");
  mapa.setView([lat, lon], 8);
  consultar(lat, lon);
}

// ------------------------------------------------------------------ cartões
function cartaoLocal(r) {
  const l = r.local, c = r.clima, a = r.analogos[0];
  const nome = l.municipio ? `${esc(l.municipio)} <span class="local-sub">· ${esc(l.mesorregiao)} · ${esc(l.uf)}</span>`
    : `${num(l.lat, 2)}, ${num(l.lon, 2)} <span class="local-sub">· fora do Nordeste</span>`;
  const reg = r.este_ano.regime;
  if (!a) return `<div class="cartao" id="c-local"><div class="local-nome">${nome}</div>${reg ? `<p>${esc(reg.texto)}</p>` : ""}
    <p class="aviso">${esc(c.fonte)}.</p></div>`;
  return `<div class="cartao" id="c-local">
    <div class="local-nome">${nome}</div>
    ${reg ? `<p>${esc(reg.texto)}</p>` : ""}
    <div class="chips">
      <span class="chip">chuva ${num(c.chuva_anual_mm)} mm/ano</span>
      <span class="chip">aridez P/ET0 ${num(c.aridez_P_ET0, 2)}</span>
      <span class="chip">${num(c.meses_umidos)} meses úmidos</span>
      <span class="chip">Tmax média na estação úmida ${num(c.tmax_estacao_umida, 1)} °C</span>
    </div>
    <p class="local-sub">${esc(c.fonte)}.</p>
    <h3>Estudo de clima mais parecido (NASA POWER)</h3>
    <div><b>${esc(a.lugar)}</b> — ${esc(a.artigos)}</div>
    <div class="barra"><span style="width:${Math.round(a.w * 100)}%"></span></div>
    <div class="local-sub">Peso de transferência w = ${num(a.w, 2)}: ${esc(r.confianca.texto)}.
      Depois: ${r.analogos.slice(1, 3).map((x) => `${esc(x.lugar)} (${num(x.w, 2)})`).join("; ")}.</div>
  </div>`;
}

const NIVEL = { "alerta": "Alerta", "sinal fraco": "Sinal fraco", "sem alerta": "Sem alerta", "não avaliado": "Não avaliado aqui" };
function cartaoAno(r) {
  const e = r.este_ano, i = e.inicio, z = e.zarc_primeiro;
  let h = `<div class="cartao ${e.alerta ? "alerta" : ""}" id="c-ano"><h2>Este ano (estação 2027) · ${esc(NIVEL[e.nivel_alerta] || e.nivel_alerta)}</h2>
    <p><b>${esc(e.texto_oni)}</b></p>`;
  if (e.perspectiva) h += `<p>${esc(e.perspectiva)}</p>`;
  if (e.chuva_recente) h += `<p class="local-sub">${esc(e.chuva_recente)}</p>`;
  if (e.smap && e.smap.status === "ok") h += `<p>${esc(e.smap.texto)}</p>`;
  else if (e.smap) h += `<p class="local-sub">Solo agora (SMAP): ${esc(e.smap.status)}.</p>`;
  if (i) {
    const anos = Object.entries(i.anos_el_nino_forte).map(([a, d]) => `${a}: ${d}`).join("; ");
    h += `<h3>Quando a chuva começa (IMERG)</h3>
      <p>Início típico ${esc(i.mediana)} (8 em 10 anos entre ${esc(i.p10)} e ${esc(i.p90)}; ${i.n_anos} estações até 2025; a de 2026,
      IMERG Late preliminar, fica fora).
      Nos El Niños fortes da série: ${esc(anos)}. Com 3 ou 4 anos, a diferença para os demais anos não se separa do acaso; a data
      de início sozinha não protege. Quem decide são os portões ao longo da estação (chuva acumulada e solo SMAP).</p>`;
  }
  if (z && (z.ate40 || z.risco20)) h += `<p class="aviso">ZARC 2026/27, culturas anuais do cardápio (tábua aberta): zoneadas (risco até 40%) desde
    <b>${esc(z.ate40 || "—")}</b>; risco de 20% só a partir de <b>${esc(z.risco20 || "nenhum decêndio")}</b>. Plantar antes disso fica fora do zoneamento.</p>`;
  if (e.alerta && e.regime && e.regime.quadra) h += `<p class="aviso">Ano de alerta: plante uma parte e guarde a outra; garanta semente de
    caupi precoce até dezembro e maniva para fevereiro; não queime.</p>`;
  return h + "</div>";
}

const SELO = {
  "indicada": ["s-indicada", "indicada · risco 20%"], "com risco": ["s-risco", "risco 30–40%"], "só aptidão": ["s-aptidao", "apta · sem ZARC"],
  "apta (GAEZ)": ["s-apta", "apta (GAEZ)"], "pouco apta": ["s-fora", "pouco apta"], "fora": ["s-fora", "fora"],
  "literatura": ["s-lit", "só literatura"], "sem dado": ["s-fora", "sem dado"],
};
function janelaTxt(i) {
  const v = (x) => x && x !== "nenhum" && x !== "—";
  let fonte = i, nota = "";
  const ps = i.por_solo || [];
  if (ps.length) {
    const ad = ps[0].cod_solo >= 11;
    const escolha = ad ? solo.ad : solo.textura;
    if (escolha) {
      const s = ps.find((x) => String(x.cod_solo) === escolha);
      if (!s) return `<span class="local-sub">não zoneado neste solo</span>`;
      fonte = s; nota = ` · ${esc(s.solo)}`;
    }
  }
  if (v(fonte.risco20)) return `${esc(fonte.risco20)} <span class="local-sub">(20%${nota})</span>`;
  if (v(fonte.risco30)) return `${esc(fonte.risco30)} <span class="local-sub">(≤ 30%${nota})</span>`;
  if (v(fonte.risco40)) return `${esc(fonte.risco40)} <span class="local-sub">(≤ 40%${nota})</span>`;
  return nota ? `<span class="local-sub">sem janela neste solo</span>` : "—";
}
function seletoresSolo() {
  const op = (lista, sel) => lista.map(([v, t]) => `<option value="${v}" ${v === sel ? "selected" : ""}>${t}</option>`).join("");
  return `<div class="seletores-solo">
    <label>Textura do solo (caupi, sorgo, amendoim, algodão, mamona; no CE, mandioca, milheto e palma):
      <select class="sel-solo" data-esquema="textura">${op([["", "não sei (melhor caso)"], ["1", "arenoso"], ["2", "textura média"], ["3", "argiloso"]], solo.textura)}</select></label>
    <label>Água disponível do solo (milho, feijão comum, girassol):
      <select class="sel-solo" data-esquema="ad">${op([["", "não sei (melhor caso)"], ["11", "AD1 (menos água)"], ["12", "AD2"], ["13", "AD3"], ["14", "AD4"], ["15", "AD5"], ["16", "AD6 (mais água)"]], solo.ad)}</select></label>
  </div>`;
}
function cartaoCardapio(r) {
  const grupos = { alimento: "Alimentos", forragem: "Forragem e cobertura", renda: "Renda" };
  const ok = r.cardapio.filter((i) => ["indicada", "só aptidão", "apta (GAEZ)"].includes(i.situacao)).length;
  let h = `<div class="cartao" id="c-plantar"><h2>O que plantar aqui</h2>
    <p class="local-sub">${ok} de 15 culturas disponíveis. Se a cultura tem ZARC neste município, o ZARC decide e o GAEZ vira rótulo;
    senão, o GAEZ decide (aptidão > 40, pouco insumo). A janela vale para o solo e o ciclo mais favoráveis; a coluna "solo × ciclo"
    diz em quantas combinações há risco de 20%. Escolha o solo para ver a janela dele.</p>
    ${seletoresSolo()}
    <table><tr><th>Cultura</th><th>Papel</th><th>Aptidão GAEZ</th><th>Janela (ZARC)</th><th>Solo × ciclo</th><th>Situação</th></tr>`;
  for (const [g, rot] of Object.entries(grupos)) {
    h += `<tr class="grupo"><td colspan="6">${rot}</td></tr>`;
    for (const i of r.cardapio.filter((x) => x.grupo === g)) {
      const [cls, txt] = SELO[i.situacao] || ["s-fora", i.situacao];
      const apt = i.aptidao === null || i.aptidao === undefined ? esc(i.classe) : `${num(i.aptidao)} · ${esc(i.classe)}`;
      h += `<tr title="${esc(i.base)}"><td><b>${esc(i.cultura)}</b></td><td>${esc(i.papel)}</td><td>${apt}</td><td>${janelaTxt(i)}</td>
        <td class="local-sub">${esc(i.solo_ciclo || "—")}</td><td><span class="selo ${cls}">${txt}</span></td></tr>`;
    }
  }
  return h + `</table><p class="local-sub">Passe o mouse sobre a linha para ver a fonte. No CE, mandioca, milheto e palma usam as
    portarias plurianuais do ZARC (Port. 11/2020, 330/2020 e 284/2019; vigentes pela página do MAPA de 05/11/2026), que não estão na
    tábua aberta. Nos outros estados, essas culturas ainda usam o GAEZ.</p></div>`;
}

// ------------------------------------------------------------------ calendário: de hoje até dez/2027
const tipoCss = (t) => esc(t || "pousio").replace("ã", "a");
const FASES = {
  preparo: "preparo sem fogo", risco: "dá para plantar, com mais risco (até 40%)", plantio: "plantar (janela do ZARC)",
  estimado: "plantar (janela estimada, sem ZARC)", roca: "na roça, crescendo", colheita: "colher", pousio: "pousio pastejado",
};
const MES_ABR = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
function cartaoCalendario(r) {
  const a = r.agenda;
  if (!a) return `<div class="cartao" id="c-calendario"><h2>Calendário: quando plantar e quando colher</h2><p class="local-sub">Sem
    calendário aqui: fora do Nordeste o protótipo não tem o ZARC nem o início da chuva do IMERG por município.</p></div>`;
  const t0 = Date.parse(a.inicio), T = Date.parse(a.fim) + 864e5 - t0;
  const x = (d) => ((Date.parse(d) - t0) / T) * 100;
  const w = (de, ate) => ((Date.parse(ate) + 864e5 - Date.parse(de)) / T) * 100;
  const meses = [];
  for (let y = +a.inicio.slice(0, 4), m = +a.inicio.slice(5, 7); `${y}-${String(m).padStart(2, "0")}` <= a.fim.slice(0, 7); m = m % 12 + 1, y += m === 1 ? 1 : 0)
    meses.push(`${y}-${String(m).padStart(2, "0")}-01`);
  const grade = meses.map((d) => `<span class="g-mes" style="left:${x(d)}%"></span>`).join("") + `<span class="g-hoje" style="left:${x(a.hoje)}%"></span>`;
  const cab = meses.map((d, i) => {
    const fim = i + 1 < meses.length ? x(meses[i + 1]) : 100, m = +d.slice(5, 7);
    return `<span class="g-mes-rot" style="left:${x(d)}%;width:${fim - x(d)}%">${MES_ABR[m - 1]}${m === 1 || i === 0 ? `<small>${d.slice(0, 4)}</small>` : ""}</span>`;
  }).join("");
  const marcos = a.marcos.map((m, i) => `<span class="g-marco ${i % 2 ? "baixo" : "alto"}${m.rotulo === "Hoje" ? " hoje" : ""}" style="left:${x(m.data)}%"
    title="${esc(m.dia)} · ${esc(m.rotulo)}: ${esc(m.texto)}">${i + 1}</span>`).join("");
  const barra = (b) => {
    const larg = w(b.de, b.ate), txt = { plantio: "plantar", estimado: "plantar", colheita: "colher", pousio: "pousio" }[b.tipo];
    return `<span class="g-barra b-${b.tipo} p${b.pista}${b.segue ? " segue" : ""}" style="left:${x(b.de)}%;width:${larg}%"
      title="${esc(b.rotulo)}">${txt && larg > 7 ? txt : ""}</span>`;
  };
  const linha = (l) => `<div class="g-linha"><div class="g-rot t-${tipoCss(l.tipo)}"><b>${esc(l.parte)}${l.estacao > 2027 ? ` <small>· estação ${l.estacao}</small>` : ""}</b>
    <span>${esc(l.cultura)}</span></div><div class="g-trilho">${grade}${l.barras.map(barra).join("")}
    ${l.marcos.map((m) => `<span class="g-decide" style="left:${x(m.data)}%" title="${esc(m.rotulo)}"></span>`).join("")}</div></div>`;
  let h = `<div class="cartao" id="c-calendario"><h2>Calendário: quando plantar e quando colher (hoje até dez/2027)</h2>
    <div class="agora"><h3>O que fazer agora (${esc(a.hoje_txt)})</h3><ul>${a.agora.map((t) => `<li>${esc(t)}</li>`).join("")}</ul></div>
    <p class="local-sub">Cada linha é uma parte do roçado (veja o desenho na Rotação). Barra de cima: <b>quando plantar</b>. Barra de baixo:
    a cultura <b>na roça</b> e a <b>colheita</b>. Linha vermelha: hoje. Círculos: os marcos do ano (passe o mouse). Solo: ${esc(a.solo)};
    escolha o solo no cardápio para ver as janelas dele.</p>
    <div class="g-legenda">${Object.entries(FASES).map(([k, v]) => `<span><i class="b-${k}"></i>${v}</span>`).join("")}
      <span><i class="g-decide-chave"></i>decisão</span></div>
    <div class="gantt-caixa"><div class="gantt">
      <div class="g-linha g-cab"><div class="g-rot"></div><div class="g-trilho">${cab}</div></div>
      <div class="g-linha g-marcos"><div class="g-rot"><b>Marcos</b></div><div class="g-trilho">${grade}${marcos}</div></div>
      ${a.linhas.map(linha).join("")}
    </div></div>`;
  if (a.nota_portoes) h += `<p class="aviso">${esc(a.nota_portoes)}</p>`;
  h += `<h3>Marcos do ano</h3><ol class="marcos">${a.marcos.map((m) => `<li><b>${esc(m.dia)} · ${esc(m.rotulo)}.</b> ${esc(m.texto)}</li>`).join("")}</ol>`;
  h += `<h3>Passo a passo, parte por parte</h3><table class="passos"><tr><th>Parte</th><th>Cultura</th><th>Plantar</th><th>Colher</th><th>De onde vem a data</th></tr>
    ${a.linhas.map((l) => `<tr><td><b>${esc(l.parte)}</b>${l.estacao > 2027 ? `<br><span class="local-sub">estação ${l.estacao}</span>` : ""}</td>
      <td>${esc(l.cultura)}</td><td>${esc(l.plantar)}</td><td>${esc(l.colher)}</td><td class="local-sub">${esc(l.fonte)}</td></tr>`).join("")}</table>`;
  h += `<details><summary>Janela e colheita de cada cultura disponível aqui (também as que ficam fora do giro)</summary>
    <table class="passos"><tr><th>Cultura</th><th>Plantar (estação 2027)</th><th>Colher</th><th>De onde vem a data</th></tr>
    ${a.culturas.map((c) => `<tr><td><b>${esc(c.cultura)}</b></td><td>${esc(c.plantar)}</td><td>${esc(c.colher)}</td><td class="local-sub">${esc(c.fonte)}</td></tr>`).join("")}
    </table></details>`;
  return h + `<p class="local-sub">A colheita vem da janela de plantio mais o ciclo da cultura (dias do plantio à colheita; os ciclos
    sem fonte estão marcados como suposição). Plantou num dia da janela? Some o ciclo àquele dia.</p></div>`;
}

const TIPOS = { leguminosa: "leguminosa", cereal: "cereal", "tampão": "tampão (mandioca)", forragem: "forragem", perene: "perene", pousio: "pousio" };
function celulaRot(c) {
  return `<div class="rot t-${tipoCss(c.tipo)}"><b>${esc(c.cultura)}</b><span>${esc(c.texto)}</span></div>`;
}
function rocado(p) {
  const pt = p.faixas.filter((f) => f.parte.startsWith("Parte")), bx = p.faixas.find((f) => f.parte === "Baixio"),
    bd = p.faixas.find((f) => f.parte === "Bordas");
  const anos = p.anos.map((a, k) => `<figure class="rocado-ano"><figcaption>${a}</figcaption>
    <div class="rocado-terreno">
      <div class="rocado-partes">${pt.map((f) => `<div class="rp f-${tipoCss(f.anos[k].tipo)}"><span class="rp-letra">${esc(f.parte.slice(-1))}</span>
        <span>${esc(f.anos[k].cultura)}</span></div>`).join("")}</div>
      ${bx ? `<div class="rocado-baixio f-${tipoCss(bx.anos[k].tipo)}"><b>Baixio:</b> ${esc(bx.anos[k].cultura)}</div>` : ""}
    </div>${bd ? `<div class="rocado-borda">borda verde = ${esc(bd.anos[k].cultura)}</div>` : ""}</figure>`);
  return `<div class="rocado" role="img" aria-label="O roçado visto de cima, ano a ano">${anos.join('<span class="rocado-seta" aria-hidden="true">→</span>')}</div>`;
}
function linhaEv(c) {
  const doi = c.doi ? ` · <a href="https://doi.org/${esc(c.doi)}" target="_blank" rel="noopener">doi</a>` : "";
  const w = c.w !== null && c.w !== undefined ? ` · w ${num(c.w, 2)}` : "";
  const num_ = c.efeito ? `<b>${esc(c.efeito)}</b> · ` : "";
  return `<div class="ev"><div class="cfg">${esc(c.regra || c.configuracao)}${c.irrigado ? ' <span class="selo s-risco">irrigado</span>' : ""}</div>
    ${c.uso && !c.regra ? `<div>${esc(c.uso)}</div>` : ""}
    <div class="meta">${num_}<span class="grau">${esc(c.grau)}·${esc(c.transferencia)}</span> ${esc(c.rotulo_transferencia)}
    · ${esc(c.referencia)}${c.lugar ? " · " + esc(c.lugar) : ""}${w}${doi}</div></div>`;
}
function cartaoPlano(r) {
  const p = r.plano;
  if (!p) return `<div class="cartao" id="c-rotacao"><h2>Rotação</h2><p>Sem dado de terra neste ponto (mar ou fora da grade do GAEZ): sem plano.</p></div>`;
  let h = `<div class="cartao" id="c-rotacao"><h2>Rotação: como girar as culturas aqui (${p.anos[0]}–${p.anos[2]})</h2>
    <p><b>O que são as partes A, B e C?</b> Divida o roçado em 3 pedaços de tamanho parecido. Cada pedaço recebe uma cultura por
    ano e, no ano seguinte, a cultura muda de pedaço. Assim a leguminosa deixa nitrogênio para o cereal que vem depois, e sempre fica
    mandioca no chão como reserva para um ano ruim. O <b>baixio</b> (a parte mais baixa, que guarda mais água) fica com o cereal todo
    ano. As <b>bordas</b>, plantadas em curva de nível, ficam com palma e gliricídia, que são perenes. Siga a cor de cada cultura de
    um ano para o outro:</p>
    ${rocado(p)}
    <p class="local-sub">Com uma só estação de chuva, a rotação acontece <b>entre os anos</b> (as partes trocam de cultura) e
    <b>dentro da estação</b> (a leguminosa entra no milho em pé). O plano usa só as culturas disponíveis neste lugar. As datas de
    cada parte estão no Calendário.</p>`;
  if (p.modelo_ne) h += `<p class="aviso">Fora do Nordeste o protótipo usa o modelo do sertão: as culturas são do lugar (GAEZ, pouco insumo),
    mas as datas, as bordas e o alerta do ano foram calibrados no NE.</p>`;
  h += `<p class="aviso"><b>Interruptor do ano:</b> ${esc(p.interruptor)}</p>`;
  h += `<div class="legenda-rot">${Object.entries(TIPOS).map(([k, v]) => `<span class="rot-chave t-${k.replace("ã", "a")}">${v}</span>`).join("")}</div>`;
  const SUB = { "Parte A": "1/3 do roçado", "Parte B": "1/3 do roçado", "Parte C": "1/3 do roçado", "Baixio": "parte mais úmida", "Bordas": "em curva de nível" };
  h += `<table class="plano"><tr><th>Parte do roçado</th>${p.anos.map((a) => `<th>${a}</th>`).join("")}<th>Por que gira assim</th></tr>`;
  for (const f of p.faixas) h += `<tr><td>${esc(f.parte)}<br><span class="local-sub">${esc(SUB[f.parte] || "")}</span></td>${f.anos.map((c) => `<td>${celulaRot(c)}</td>`).join("")}<td class="local-sub">${esc(f.por_que)}</td></tr>`;
  h += `</table><h3>As regras da rotação e a evidência de cada uma</h3>${p.principios.map(linhaEv).join("")}`;
  h += `<ul class="notas">${p.notas.map((n) => `<li>${esc(n)}</li>`).join("")}</ul></div>`;
  return h;
}

function cartaoEvidencia(r) {
  const ev = r.evidencia, lc = ev.leguminosa_cereal;
  const pond = lc.ponderado_pct === null ? `não calculado (soma dos pesos ${num(lc.soma_w, 2)} < 0,3: nenhum estrato do Franke tem clima parecido)`
    : `+${num(lc.ponderado_pct)}% (3 estratos do Franke 2018, soma dos pesos ${num(lc.soma_w, 2)}), só como sensibilidade`;
  return `<div class="cartao" id="c-evidencia"><h2>De onde vem cada regra</h2>
    <p>Leguminosa antes do cereal: o motor usa <b>${esc(lc.central_motor)}</b>. Ponderado pelo clima deste lugar: ${pond}.
    A troca do consórcio milho + feijão por rotação no tempo <b>nunca foi medida</b> no semiárido.</p>
    <h3>Regras do motor</h3>${ev.regras.map(linhaEv).join("")}
    <h3>Estudos de clima parecido com este lugar (w ≥ 0,3)</h3>
    ${ev.perto.length ? ev.perto.map(linhaEv).join("") : `<p class="local-sub">Nenhum estudo do catálogo vem de clima parecido: a evidência vale só como direção.</p>`}
    <p class="local-sub">Número só aparece para cartões T0 (medido no semiárido brasileiro) ou T1 (estrato de clima análogo). T2 = só
    direção; T3 = não transfere. Grau A–D = força da evidência no lugar do estudo.</p></div>`;
}

function cartaoFontes(r) {
  return `<div class="cartao" id="c-fontes"><h2>Fontes e datas</h2><ul class="notas">${Object.values(r.fontes).map((f) => `<li>${esc(f)}</li>`).join("")}
    <li>Catálogo de rotações: 147 cartões (pesquisa/catalogo_rotacoes.json), grau A–D e transferência T0–T3.</li>
    <li>Malha municipal: IBGE. Mapa: OpenStreetMap.</li></ul></div>`;
}
