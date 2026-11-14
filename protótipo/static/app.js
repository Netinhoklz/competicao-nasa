// QUADRA protótipo (Nordeste): mapa + painel. Os dados vêm de /api/local (motor.py).
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const num = (v, d = 0) => (v === null || v === undefined ? "—" : Number(v).toLocaleString("pt-BR", { maximumFractionDigits: d, minimumFractionDigits: d }));

const mapa = L.map("mapa", { worldCopyJump: true, preferCanvas: true }).setView([-9.0, -40.5], 6);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · malha municipal IBGE', maxZoom: 18,
}).addTo(mapa);
let camadaMun = null, marcador = null, pedido = 0, ultimo = null;
const solo = { textura: "", ad: "" }; // seletor de solo (revisão A7): "" = não sei (melhor caso entre os solos)
document.addEventListener("change", (e) => {
  if (!e.target.matches(".sel-solo") || !ultimo) return;
  solo[e.target.dataset.esquema] = e.target.value;
  document.getElementById("c-plantar").outerHTML = cartaoCardapio(ultimo);
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
    const resp = await fetch(`/api/local?lat=${lat}&lon=${lon}`);
    const r = await resp.json();
    if (meu !== pedido) return;
    if (r.erro) throw new Error(r.erro);
    ultimo = r;
    destacar(r.local.cod);
    const nav = `<nav class="nav-painel"><a href="#c-local">Lugar</a><a href="#c-ano">Este ano</a><a href="#c-plantar">O que plantar</a>
      <a href="#c-rotacao" class="destaque">Rotação</a><a href="#c-evidencia">Evidência</a></nav>`;
    document.getElementById("resultado").innerHTML = nav + [cartaoLocal(r), cartaoAno(r), cartaoCardapio(r), cartaoPlano(r), cartaoEvidencia(r), cartaoFontes(r)].join("");
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

const TIPOS = { leguminosa: "leguminosa", cereal: "cereal", "tampão": "tampão (mandioca)", forragem: "forragem", perene: "perene", pousio: "pousio" };
function celulaRot(c) {
  return `<div class="rot t-${esc(c.tipo).replace("ã", "a")}"><b>${esc(c.cultura)}</b><span>${esc(c.texto)}</span></div>`;
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
    <p>Com uma só estação de chuva, a rotação acontece <b>entre os anos</b> (as faixas trocam de cultura) e <b>dentro da estação</b>
    (a leguminosa entra no milho em pé). O plano usa só as culturas disponíveis neste lugar.</p>`;
  if (p.modelo_ne) h += `<p class="aviso">Fora do Nordeste o protótipo usa o modelo do sertão: as culturas são do lugar (GAEZ, pouco insumo),
    mas as datas, as bordas e o alerta do ano foram calibrados no NE.</p>`;
  h += `<p class="aviso"><b>Interruptor do ano:</b> ${esc(p.interruptor)}</p>`;
  h += `<div class="legenda-rot">${Object.entries(TIPOS).map(([k, v]) => `<span class="rot-chave t-${k.replace("ã", "a")}">${v}</span>`).join("")}</div>`;
  h += `<table class="plano"><tr><th></th>${p.anos.map((a) => `<th>${a}</th>`).join("")}<th>Por que gira assim</th></tr>`;
  for (const f of p.faixas) h += `<tr><td>${esc(f.faixa)}</td>${f.anos.map((c) => `<td>${celulaRot(c)}</td>`).join("")}<td class="local-sub">${esc(f.por_que)}</td></tr>`;
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
