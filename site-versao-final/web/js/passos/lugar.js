// Passo "Do espaço" (#/<cod>/1, fora do caminho, pela pílula "Espaço"): o que este município permite, sem perguntar nada. Pouco texto:
// El Niño, 4 indicadores, as tendências e as 6 primeiras culturas como ícones coloridos. O detalhe técnico fica nos "ver mais".
// Dados: núcleo do José (ZARC + GAEZ + NASA POWER/IMERG/SMAP + ONI) e a manchete de El Niño do estado (definição única).
// Extras (js/extras/, montados por U.montarExtras): tendências (visível), confiança dos dados (visível), satélite × pluviômetro e as grades
// de cada satélite (no ver mais "De onde vêm os dados") e o glossário (no fim). "Seu olho" e "o que é?" entram no próprio texto.
import { termo } from "../extras/glossario.js";
import { olho, OLHOS } from "../extras/voce_decide.js";
const SIT = {
  "indicada": ["ok", "Recomendado"],
  "só aptidão": ["apto", "Dá, sem zoneamento"],
  "apta (GAEZ)": ["apto", "Dá, sem zoneamento"],
  "com risco": ["risco", "Com mais risco"],
  "literatura": ["lit", "Só nos estudos"],
};

function doy(ddmm) {
  if (!ddmm) return null;
  const [d, m] = ddmm.split("/").map(Number);
  return (Date.UTC(2026, m - 1, d) - Date.UTC(2026, 0, 1)) / 864e5 + 1;
}

function regua(r, U) {
  const reg = r.este_ano.regime, ini = r.este_ano.inicio;
  if (!reg) return "";
  const m0 = reg.mes_inicio, w = 100 / 365, dia = (m, d = 1) => (Date.UTC(2026, m, d) - Date.UTC(2026, 0, 1)) / 864e5;
  const meses = U.MESES.map((m, i) => `<span style="left:${dia(i) * w}%">${m}</span>`).join("");
  let faixa = "";
  for (let k = 0; k < 4; k++) {
    const m = (m0 - 1 + k) % 12;
    faixa += `<i class="regua-chuva" style="left:${dia(m) * w}%;width:${(dia(m + 1) - dia(m)) * w}%"></i>`;
  }
  let marcas = "";
  if (ini) {
    const p10 = doy(ini.p10), p90 = doy(ini.p90), med = doy(ini.mediana);
    if (p10 && p90) (p10 <= p90 ? [[p10, p90]] : [[p10, 366], [1, p90]]).forEach(([a, b]) => {
      marcas += `<i class="regua-inicio" style="left:${a * w}%;width:${(b - a) * w}%"></i>`;
    });
    if (med) marcas += `<b class="regua-mediana${med * w < 15 ? " esq" : med * w > 85 ? " dir" : ""}" style="left:${med * w}%"><em>chuva chega ~${U.esc(ini.mediana)}</em></b>`;
  }
  const hoje = r.agenda?.hoje ? doy(U.dataBR(r.agenda.hoje, true)) : null;
  if (hoje) marcas += `<b class="regua-hoje${hoje * w < 15 ? " esq" : hoje * w > 85 ? " dir" : ""}" style="left:${hoje * w}%"><em>hoje</em></b>`;
  return U.verMais(`<div class="regua" role="img" aria-label="Meses de chuva e quando ela costuma chegar">${faixa}${marcas}<div class="regua-meses">${meses}</div></div>
    <div class="regua-legenda"><span><i class="ch-chuva"></i>meses de chuva: <b>${U.esc(reg.estacao)}</b></span>
      ${ini ? `<span><i class="ch-inicio"></i>a chuva chega entre ${U.esc(ini.p10)} e ${U.esc(ini.p90)} (8 em 10 anos)</span>` : ""}
      ${U.selo("medido", "GPM IMERG via NASA POWER, 1998–2025")}</div>
    ${/litoral leste/.test(reg.texto || "") ? olho(OLHOS.leste) : ""}`, "O ano da chuva aqui");
}

function elNino(r, U) {
  const e = r.este_ano, u = r.el_nino_uf;
  if (!u || !u.pct_terco_seco) return "";
  const anos = (u.anos || Object.keys(u.pct_terco_seco)).map(String), acaso = u.acaso_pct ?? 33;
  const comDado = anos.filter((a) => u.pct_terco_seco[a] != null);
  const n = Math.round((u.media ?? 0) / 10);
  const barras = `<svg class="enso-barras" viewBox="0 -16 220 138" role="img" aria-label="Por ano de El Niño forte">
    <line x1="0" x2="220" y1="${100 - acaso}" y2="${100 - acaso}" class="enso-acaso"/>
    ${anos.map((a, i) => { const v = u.pct_terco_seco[a], x = 10 + i * 52;
      return v == null ? `<text x="${x + 17}" y="96" text-anchor="middle" class="enso-ano">—</text><text x="${x + 17}" y="116" text-anchor="middle" class="enso-ano">${a}</text>`
        : `<rect x="${x}" y="${100 - v}" width="34" height="${v}" rx="4" class="enso-barra"/><text x="${x + 17}" y="${94 - v}" text-anchor="middle" class="enso-val">${Math.round(v / 10)} em 10</text>
           <text x="${x + 17}" y="116" text-anchor="middle" class="enso-ano">${a}</text>`; }).join("")}
    <text x="218" y="${95 - acaso}" text-anchor="end" class="enso-ano">acaso</text></svg>`;
  // à vista: a manchete e o "seu olho"; as barras de cada El Niño e o texto técnico ficam no "ver mais"
  return `<div class="painel ${e.alerta ? "destaque" : ""} enso-painel">
    <div class="enso">${U.faixa("onda", e.alerta ? "ambar" : "azul", `${termo("el_nino", "El Niño forte")} em 2027: nos anos assim, a chuva veio fraca em ${termo("em_dez", `${n} de 10`)} municípios ${U.esc(U.ufDe(u.uf))}. ${U.selo("medido", u.definicao || "")}`)}
      ${olhoElNino(e.regime, U)}</div>
    ${U.verMais(`<p class="enso-sub">Pelo acaso seriam 3 em 10; 2024 foi forte e choveu bem.</p>${barras}
      <p>${U.esc(e.texto_oni)}</p>${e.perspectiva ? `<p><b>Neste município</b> (não é previsão): ${U.esc(e.perspectiva)}</p>` : ""}
      <p>${U.esc(u.definicao || "")}${comDado.length < anos.length ? " " + U.esc((u.avisos || [])[0] || "") : ""}</p>`, "Ver cada El Niño forte")}
  </div>`;
}

/** "Seu olho" do El Niño com o mês em que a estação daqui começa (fevereiro na quadra do norte). */
function olhoElNino(reg, U) {
  if (!reg || reg.quadra !== false) return olho(OLHOS.el_nino);
  const MES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
  return olho(`Nem todo El Niño seca igual: olhe a chuva de ${MES[(reg.mes_inicio || 2) - 1]}.`);
}

function indicadores(r, U) {
  const e = r.este_ano, reg = e.regime, ini = e.inicio, sm = e.smap;
  const soloTxt = sm?.status === "ok" ? { "seco para a época": "Seco", "úmido para a época": "Úmido", "normal para a época": "Normal" }[sm.classe] || sm.classe : "—";
  // um selo para o bloco (no rótulo), com a fonte de cada número no toque
  const fonte = ["O mar agora: NOAA/CPC ONI, ago–out/2026", ini && "A chuva chega: NASA GPM IMERG, 27 estações até 2025",
    reg && "Meses de chuva: NASA GPM IMERG, os 4 meses mais chuvosos",
    `O solo hoje: NASA SMAP L4${sm?.status === "ok" ? `, 30 dias até ${sm.fim}; posição ${sm.posto} de ${sm.anos} anos` : ""}`].filter(Boolean).join(". ");
  return `<p class="kicker">O tempo daqui ${U.selo("medido", fonte)}</p><div class="grade-4">
    ${U.ind({ icone: "termo", rot: "O mar agora", val: (e.oni > 0 ? "+" : "") + U.num(e.oni, 1), un: "°C", sub: "acima do normal" })}
    ${ini ? U.ind({ icone: "chuva", rot: "A chuva chega", val: U.esc(ini.mediana), sub: `entre ${U.esc(ini.p10)} e ${U.esc(ini.p90)}` }) : ""}
    ${reg ? U.ind({ icone: "sol", rot: "Meses de chuva", val: U.esc(reg.estacao), sub: `${U.num(reg.chuva_mm)} mm num ano típico` }) : ""}
    ${U.ind({ icone: "solo", rot: "O solo hoje", val: U.esc(soloTxt), sub: sm?.status === "ok" ? termo("umidade_solo", "umidade da raiz") : U.esc(sm?.status || "") })}
  </div>`;
}

function culturas(r, U) {
  const jan = Object.fromEntries((r.agenda?.culturas || []).map((c) => [c.cultura, c]));
  const ord = { ok: 0, apto: 1, risco: 2, lit: 3 };
  const servem = r.cardapio.filter((i) => SIT[i.situacao]).sort((a, b) => ord[SIT[a.situacao][0]] - ord[SIT[b.situacao][0]]);
  const fora = r.cardapio.filter((i) => !SIT[i.situacao]);
  const quando = (j) => (j && j.plantar && j.plantar !== "—" ? j.plantar.split(" (")[0].replace(/^de /, "").replace(/\/20\d\d/g, "") : "");
  // à vista, a recomendada fica só com a bolinha verde (sem repetir "Recomendado" em cada cartão); as outras dizem o que são
  const bloco = (i, comData = true) => {
    const [cls, rot] = SIT[i.situacao], q = comData ? quando(jan[i.cultura]) : "";
    return `<div class="cultura c-${cls}" title="${U.esc(i.base)}">${U.ic(U.icCultura(i.cultura), "g")}
      <b>${U.esc(i.cultura)}</b>${comData || cls !== "ok" ? `<span class="c-rot">${U.esc(rot)}</span>` : ""}${q ? `<span class="c-quando">${U.ic("semente")} ${U.esc(q)}</span>` : ""}</div>`;
  };
  const n = servem.filter((i) => ["ok", "apto"].includes(SIT[i.situacao][0])).length;
  // "Ver todas" diz o que soma às n que servem (o número de cima e o de baixo batem)
  const conta = (c) => servem.filter((i) => SIT[i.situacao][0] === c).length;
  const somam = [conta("risco") && `${conta("risco")} com risco`, conta("lit") && `${conta("lit")} só nos estudos`].filter(Boolean).join(" e ");
  // à vista: as 6 primeiras como ícones (as recomendadas vêm antes); no "ver mais", todas com a época de plantar (e o "seu olho" das
  // datas estimadas), a lista das que não servem e a tabela
  const vis = servem.slice(0, 6);
  const tabela = `<p>Onde a cultura tem zoneamento (ZARC 2026/27, MAPA), ele decide; senão, a aptidão do FAO GAEZ v4 com pouco insumo (acima de 40).
      Sem saber a sua terra, as datas são as que servem nos solos onde a cultura tem zoneamento; em Sua roça elas se ajustam à sua.</p>
      <table><tr><th>Cultura</th><th>Aptidão GAEZ</th><th>Risco 20%</th><th>Até 40%</th><th>Solo × ciclo</th><th>Fonte</th></tr>
      ${r.cardapio.map((i) => `<tr><td>${U.esc(i.cultura)}</td><td>${i.aptidao == null ? U.esc(i.classe) : U.num(i.aptidao) + " · " + U.esc(i.classe)}</td>
        <td>${U.esc(i.risco20 || "—")}</td><td>${U.esc(i.risco40 || "—")}</td><td>${U.esc(i.solo_ciclo || "—")}</td><td class="sub pequeno">${U.esc(i.base)}</td></tr>`).join("")}
      </table>`;
  const legenda = `<div class="legenda-cult"><span class="chip verde">● Recomendado</span><span class="chip">● Dá, sem ${termo("zarc", "zoneamento")}</span><span class="chip ambar">● Com mais risco</span></div>`;
  return `<div class="painel"><h3>O que dá para plantar aqui ${U.selo("medido", "ZARC/MAPA 2026/27 e FAO GAEZ v4")}</h3>
    <p class="culturas-manchete"><span class="numero-grande">${n}</span> culturas servem em ${U.esc(r.local.municipio)}.</p>
    <div class="culturas">${vis.map((i) => bloco(i, false)).join("")}</div>
    ${U.verMais(`${legenda}<div class="culturas">${servem.map((i) => bloco(i)).join("")}</div>
      ${servem.some((i) => SIT[i.situacao][0] === "apto") ? olho(OLHOS.sem_zarc) : ""}
      ${fora.length ? `<p class="sub pequeno">Não servem aqui: ${fora.map((i) => U.esc(i.cultura)).join(", ")}.</p>` : ""}
      <h4>Tabela técnica</h4>${tabela}`, servem.length > vis.length ? (somam ? `Ver todas: mais ${somam}` : `Ver todas as ${servem.length}`) : "Ver quando plantar")}</div>`;
}

function origem(r, U, ctx) {
  const c = r.clima, a = r.analogos?.[0];
  const estudos = a ? `<h4>As regras da rotação</h4><p>O clima daqui (chuva ${U.num(c.chuva_anual_mm)} mm/ano, ${U.num(c.meses_umidos)} meses úmidos) é mais
    parecido com <b>${U.esc(a.lugar)}</b> (${U.esc(a.artigos)}), peso ${U.num(a.w, 2)}: ${U.esc(r.confianca.texto)}. As regras da rotação vêm de estudos em
    lugares assim. ${U.selo("medido", c.fonte)}</p>` : "";
  return `<div class="painel painel-fino origem">
    ${regua(r, U)}
    ${U.verMais(`${U.extra("satelite_chao", { painel: false })}${U.extra("harmonizacao", { naTela: ["ndvi", "grace"] })}${estudos}`, "De onde vêm os dados (satélites)")}
    ${U.extra("glossario")}
    <a class="lugar-acerto" href="${ctx.link(5)}" data-acerto>${U.ic("grafico")}<span>Quanto o cálculo já acertou</span><b>Se secar ${U.ic("seta")}</b></a></div>`;
}

export default {
  id: "lugar",
  titulo: "Do espaço",
  curto: "Espaço",
  async render(el, ctx) {
    const { r, util: U } = ctx;
    el.innerHTML = `<div class="titulo-passo"><p class="kicker">Do espaço</p>
      <h1>${U.esc(r.local.municipio)}, ${U.esc(r.local.uf)}.<span class="eco">Veja o que a terra daqui aceita.</span></h1></div>
      ${elNino(r, U)}
      ${indicadores(r, U)}
      ${U.extra("tendencias")}
      ${culturas(r, U)}
      ${U.extra("confianca")}
      ${origem(r, U, ctx)}`;
    await U.montarExtras(el, ctx);
  },
};
