// Extra do ponto 3: "O satélite e o pluviômetro". O que cada um vê, quanto batem aqui (pluviômetro aprovado mais perto, ou a
// faixa de distância do mar se ele estiver longe) e como juntar os dois melhora a conta da chuva.
// Dados: ferramentas/preparar_satelite_chao.py → dados/satelite_chao.json (IMERG × FUNCEME no CE, 1998–2025; × INMET no NE,
// 2016–2025). Uso: render(el, ctx, { painel: false, convite: false }) — os dois são opcionais (padrão: com painel e convite).
import * as U from "../comum.js";

const ARQ = new URL("../../dados/satelite_chao.json", import.meta.url);
let cache = null;
const dados = () => (cache ??= fetch(ARQ).then((r) => (r.ok ? r.json() : null)).catch(() => null));

const IC_SAT = `<svg class="ic g" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7l4-4 2.5 2.5-4 4zM14.5 18.5l4-4L21 17l-4 4z"/>
  <path d="M9.5 12 12 9.5l2.5 2.5-2.5 2.5zM7.5 7.5l3.25 3.25M13.25 13.25l3.25 3.25M4 15a5 5 0 0 0 5 5"/></svg>`;
const IC_PLUV = `<svg class="ic g" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 3.5h14l-4 5H9z"/>
  <path d="M9 8.5v11a1.5 1.5 0 0 0 1.5 1.5h3a1.5 1.5 0 0 0 1.5-1.5v-11M9 12.5h2.5M9 15.5h2.5M9 18.5h2.5"/></svg>`;
const FAIXA = ["perto do mar leste", "perto do mar do norte", "a 20–150 km do mar", "a mais de 150 km do mar"];

const emDez = (p) => `${Math.round(p * 10)} em 10`;
const dec = (v) => U.num(v, 2);

function barras(linhas, un) {
  const max = Math.max(...linhas.map((l) => l.v), 1);
  return `<div class="sc-barras">${linhas.map((l) => `<div class="sc-barra ${l.cls}">
      <span class="sc-b-rot">${l.rot}</span>
      <span class="sc-b-trilho"><i style="width:${Math.max(6, (l.v / max) * 100)}%"></i></span>
      <b>${U.num(l.v)}<small>${un}</small></b></div>`).join("")}</div>`;
}

// "Juntando os dois": onde o satélite erra muito o total (costa leste, serra), corrigir pelo pluviômetro do lugar;
// no resto, juntar o pluviômetro do vizinho ao satélite (medido na rede densa da FUNCEME, chuva até o portão de 19/mar).
function juntos(p, perto, postos, d, nomeMun) {
  if (p && perto && (p.rz < 0.8 || p.rz > 1.25) && p.ec < p.ea) {
    return `<div class="sc-juntos">
      <h4>Corrigir o satélite pelo pluviômetro ${U.selo("medido", `${p.t}: ${p.n}, ${p.a0}–${p.a1}, contra GPM IMERG; correção por trimestre, deixando o ano de fora`)}</h4>
      ${barras([{ rot: "Satélite sozinho", v: p.ea, cls: "sat" }, { rot: "Corrigido pelo pluviômetro", v: p.ec, cls: "jun" }], "mm")}
      <p class="sc-leg">Erro médio do mês de chuva, medido no pluviômetro de ${U.esc(p.n)}.</p></div>`;
  }
  const g = d?.regional?.portao;
  if (!g) return "";
  const e = Object.fromEntries(g.est.map((x) => [x.k, x]));
  const tem = postos > 0 ? ` ${U.esc(nomeMun)} tem ${postos} ${postos > 1 ? "pluviômetros" : "pluviômetro"} da FUNCEME.` : "";
  return `<div class="sc-juntos">
    <h4>Juntar com o pluviômetro do vizinho ${U.selo("medido", `FUNCEME: ${g.postos} pluviômetros do CE, ${g.periodo}; vizinho a ${U.num(g.dist_viz_km, 0)} km (mediana); ${U.num(g.n_anos)} anos de posto`)}</h4>
    ${barras([{ rot: "Satélite sozinho", v: e.s.erro100, cls: "sat" }, { rot: "Vizinho sozinho", v: e.viz.erro100, cls: "plu" },
      { rot: "Os dois juntos", v: e.media.erro100, cls: "jun" }], "mm")}
    <p class="sc-leg">Erro em cada 100 mm de chuva até 19/mar, medido no Ceará.${tem}</p></div>`;
}

function detalhe(p, linha, d) {
  const R = d.regional || {}, reg = d.regra || {};
  const aqui = p ? `<p><b>Pluviômetro mais perto:</b> ${U.esc(p.n)} (${p.t}${p.m ? `, ${U.esc(p.m)}` : ""}/${p.uf}), a ${linha[1]} km,
      ${p.a0}–${p.a1}, ${p.nm} meses de chuva comparados.${linha[1] > reg.longe_km ? ` Fica a mais de ${reg.longe_km} km: na frente vale a faixa de distância do mar.` : ""}</p>
    <table><tbody>
      <tr><td>No total</td><td>o satélite viu ${U.num(p.rz * 100)} de cada 100 mm</td></tr>
      <tr><td>No mês</td><td>andam juntos (r = ${dec(p.rm)})</td></tr>
      <tr><td>No dia</td><td>batem pouco (r = ${dec(p.rd)}): a chuva de trovoada cai em manchas</td></tr>
      <tr><td>Mês de chuva a até 1/4</td><td>${emDez(p.p)} cru · ${emDez(p.pc)} corrigido por trimestre</td></tr>
      <tr><td>Erro médio do mês</td><td>${p.ea} mm cru · ${p.ec} mm corrigido</td></tr>
    </tbody></table>` : "<p>Sem pluviômetro aprovado para este município.</p>";
  const costa = R.costa ? `<p><b>No Nordeste</b> (estações do INMET, 2016–2025): o satélite erra mais perto do mar leste.</p>
    <table><thead><tr><th>Onde</th><th>Estações</th><th>Viu de 100 mm</th><th>Mês a até 1/4 (cru · corrigido)</th></tr></thead><tbody>
    ${R.costa.map((c) => `<tr><td>${U.esc(c.faixa)}</td><td>${c.n}</td><td>${U.num(c.rz * 100)}</td><td>${emDez(c.p)} · ${emDez(c.pc)}</td></tr>`).join("")}
    </tbody></table>
    ${R.serra?.n ? `<p>Na serra também: em ${R.serra.n} pluviômetros da FUNCEME (${R.serra.postos.map(U.esc).join(", ")}), o satélite viu
      ${U.num(R.serra.rz_min * 100)} a ${U.num(R.serra.rz_max * 100)} de cada 100 mm: a chuva de encosta escapa do quadrado de 11 km.</p>` : ""}
    <p>Corrigir o total ajuda onde o satélite erra muito (costa leste); no sertão, onde ele já acerta o total, a correção não melhora o mês.</p>` : "";
  const g = R.portao;
  const portao = g ? `<p><b>Juntar no portão</b> (chuva de ${U.esc(g.janela)}, ${g.postos} pluviômetros da FUNCEME, ${g.periodo}):</p>
    <table><thead><tr><th>Conta da chuva do seu pluviômetro</th><th>Erro em 100 mm</th><th>Anos a até 1/4</th></tr></thead><tbody>
    ${g.est.map((x) => `<tr><td>${U.esc(x.nome)}</td><td>${x.erro100}</td><td>${emDez(x.perto)}</td></tr>`).join("")}
    </tbody></table>
    <p>Quanto mais perto o vizinho, melhor: ${g.por_dist.map((x) => `${U.esc(x.faixa)}, juntos ${x.juntos} mm (satélite ${x.s})`).join(" · ")}.
      Corrigir o satélite pelo histórico do vizinho não ganhou do satélite cru no CE: o ganho vem de juntar as duas leituras.</p>` : "";
  return U.verMais(`${aqui}${costa}${portao}
    <p><b>Como medimos:</b> chuva diária do GPM IMERG (NASA, quadrados de ~11 km) na célula do pluviômetro, só nos dias com os dois.
      Mês de chuva = pluviômetro com ${reg.mes_chuva_mm ?? 30} mm ou mais. A correção por trimestre usa os outros anos (o ano testado fica de fora).
      Ficaram de fora ${reg.fora_qc} de ${reg.medidos} pluviômetros com sinal de defeito (${U.esc(reg.qc)}).</p>
    <p><b>O pluviômetro também erra:</b> precisa ficar longe de árvore e telhado e ser lido todo dia no mesmo horário.</p>`, "Ver como comparamos");
}

export default {
  id: "satelite_chao",
  async render(el, ctx, opcoes = {}) {
    const d = await dados();
    const cod = String(ctx?.r?.local?.cod ?? ctx?.cod ?? "");
    const nomeMun = ctx?.r?.local?.municipio || "O município";
    const linha = d?.mun?.[cod] || null;
    const p = linha ? d.pluv[linha[0]] : null;
    const leste = !!linha?.[2];
    const perto = p && linha[1] <= (d.regra?.longe_km ?? 80);
    const fx = linha && !perto ? d.regional?.costa?.[linha[3]] : null;  // longe de pluviômetro: vale a faixa do mar
    const rz = perto ? p.rz : fx ? fx.rz : null;
    const viu = rz !== null ? Math.round(rz * 100) : null;
    const igual = viu !== null && Math.abs(viu - 100) <= 10;
    const frase = perto
      ? `Para cada 100 mm no pluviômetro de <b>${U.esc(p.n)}</b> (a ${linha[1]} km), o satélite viu ${viu}.`
      : fx ? `Sem pluviômetro testado perto. ${FAIXA[linha[3]][0].toUpperCase() + FAIXA[linha[3]].slice(1)}, para cada 100 mm no pluviômetro, o satélite viu ${viu}.`
      : "Sem pluviômetro testado para este lugar.";
    const fonte = d ? `${d.fontes.satelite}; ${d.fontes.FUNCEME}; ${d.fontes.INMET}` : "GPM IMERG × pluviômetros";
    const portoes = ctx?.r?.agenda?.portoes;
    const html = `
      <h3 class="sc-tit">Satélite × pluviômetro ${U.selo("medido", fonte)}</h3>
      <div class="sc-par">
        <div class="sc-lado sat">
          <div class="sc-rot">${IC_SAT}<b>Satélite</b></div>
          ${viu !== null ? `<div class="sc-num">${viu}<small>mm</small></div>` : ""}
          <p>Vê a área toda, todo dia.</p>
          ${leste ? `<span class="chip terra">Perto do mar, vê menos</span>`
            : viu !== null && viu < 80 ? `<span class="chip terra">Aqui, vê menos chuva</span>`
            : viu !== null && viu > 125 ? `<span class="chip ambar">Aqui, vê chuva a mais</span>`
            : `<span class="sc-fraco">Erra perto do mar e na serra</span>`}
        </div>
        <div class="sc-meio ${viu !== null ? (igual ? "igual" : "dif") : ""}" aria-hidden="true">${viu !== null ? (igual ? "≈" : "≠") : "×"}</div>
        <div class="sc-lado plu">
          <div class="sc-rot">${IC_PLUV}<b>Pluviômetro</b></div>
          ${viu !== null ? `<div class="sc-num">100<small>mm</small></div>` : ""}
          <p>Mede um ponto, exato.</p>
          <span class="sc-fraco">Só vale para ali</span>
        </div>
      </div>
      <p class="sc-frase">${frase}</p>
      ${juntos(p, perto, linha?.[4] ?? 0, d, nomeMun)}
      ${opcoes.convite === false ? "" : `<div class="sc-convite">${U.ic("gota")}<p><b>Tem pluviômetro? Anote a chuva todo dia às 7h.</b>
        <span>Na sua roça, o seu número manda${portoes ? ". Em 19/mar, some desde 1/fev e leve ao técnico" : ""}.</span></p></div>`}
      ${d ? detalhe(p, linha, d) : ""}`;
    el.innerHTML = opcoes.painel === false ? `<div class="ex-satelite-chao">${html}</div>` : `<div class="painel ex-satelite-chao">${html}</div>`;
  },
};
