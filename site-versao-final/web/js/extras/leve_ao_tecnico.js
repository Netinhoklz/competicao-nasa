// QUADRA, ponto 16: "Leve para o técnico". 5 a 7 perguntas e confirmações tiradas das respostas e do plano (solo, baixio,
// faixas, datas, metade guardada e portões, preço da raiz, água, maniva) e dos motivos de confiança do município, com dois
// botões: imprimir (só a lista, numa folha clara; CSS em css/extras/voce_decide.css) e copiar o texto (para o WhatsApp).
import * as U from "../comum.js";
import { carregar, confiancaDe } from "./confianca.js";
import { FRASE } from "./voce_decide.js";

const NOME = { "Feijão-caupi": "caupi", "Feijão comum": "feijão", "Sorgo forrageiro": "sorgo", "Sorgo granífero": "sorgo de grão", Amendoim: "amendoim" };
const curto = (c) => NOME[c] || String(c || "").toLowerCase();
const TERRA = {
  nao_sei: ["solo", "Minha terra é areia, misturada ou barro?"],
  arenosa: ["areia", "Minha terra seca rápido: as datas de plantar servem?"],
  mista: ["gota", "Minha terra segura a umidade: as datas de plantar servem?"],
  barro: ["barro", "Minha terra encharca: as datas de plantar servem?"],
};
const FICHA = {
  terra: { nao_sei: "terra: não sei", arenosa: "terra arenosa", mista: "terra misturada", barro: "terra de barro" },
  baixio: { nao_sei: "baixio: não sei", nao: "sem baixio", pouco: "baixio pequeno", terco: "baixio de ⅓", metade: "baixio de ½" },
  agua: { chuva: "só a chuva", cisterna: "cisterna de beber", barreiro: "barreiro ou açude", irriga: "poço ou irrigação" },
};
// O que a confiança dos dados pede ao técnico (confianca_mun.json, _textos.<chave>.tecnico), dito como pergunta do agricultor.
const PERGUNTA_CONF = {
  leste: "O pluviômetro da comunidade confirma a chuva do satélite?",
  agro: "Quanto a minha família colhe, para refazer a conta?",
  pam_curta: "Quanto a família colhe num ano bom e num ano ruim?",
  mandioca_sem_serie: "Quanto rende a mandioca aqui, para quem já planta?",
  mandioca_repete: "A casa de farinha confirma a colheita da mandioca?",
  estimada: "A data de plantar desta cultura está certa aqui?",
  ciclo: "A minha semente é do ciclo certo?",
  el_nino: "Que chuva olho antes de decidir?",
  smap: "Como confiro a umidade da terra na mão?",
  portoes: "Que datas de troca valem na minha estação?",
  analogos: "Testo a rotação numa parte pequena primeiro?",
};
// órgão estadual de assistência técnica e extensão rural (ATER)
const ATER = { MA: "AGERP", PI: "Emater-PI", CE: "Ematerce", RN: "Emater-RN", PB: "Empaer", PE: "IPA", AL: "Emater-AL", SE: "Emdagro", BA: "Bahiater" };

/** A janela de plantar da leguminosa em 2027 (ou da 1ª cultura anual do plano): "11/02 a 20/03". */
function janela(r) {
  const ls = (r.agenda?.linhas || []).filter((l) => l.estacao === 2027 && l.parte !== "Bordas" && !/em pé/.test(l.cultura));
  const l = ls.find((x) => x.cultura === r.plano?.leguminosa) || ls[0];
  const b = l?.barras.find((x) => x.tipo === "plantio" || x.tipo === "estimado");
  return b ? { cultura: curto(l.cultura), txt: `${U.dataBR(b.de, true)} a ${U.dataBR(b.ate, true)}` } : null;
}

/** As perguntas (até 7): {icone, texto}. conf = confiancaDe(...) ou null. */
export function perguntas(ctx, conf) {
  const { r, ef } = ctx, p = r.plano || {}, a = r.agenda || {};
  const cand = [];
  const poe = (prio, icone, texto) => cand.push({ prio, icone, texto });
  const [icT, tT] = TERRA[ef.terra] || TERRA.nao_sei;
  poe(1, icT, tT);
  const cereal = curto((p.faixas || []).find((f) => f.parte === "Baixio")?.anos?.[0]?.cultura || "milho");
  if (ef.tem_baixio === null) poe(2, "gota", "Tenho baixio? Que parte do roçado fica úmida?");
  else if (ef.tem_baixio) poe(2, "milho", `O baixio (${U.ha(ef.baixio_ha)}) aguenta ${cereal}${p.leguminosa ? ` com ${curto(p.leguminosa)}` : ""}?`);
  else poe(2, "milho", "Sem baixio, onde o milho tem mais chance?");
  poe(8, "faixas", "As faixas e o espaçamento cabem no meu terreno?");
  const j = janela(r);
  if (j) poe(3, "calendario", `Plantar ${j.cultura} de ${j.txt} serve à minha semente?`);
  const metade = /metade/i.test(p.interruptor || "");
  if (metade && a.portoes) poe(4, "relogio", "Metade guardada: em 19/mar e 30/abr, decidimos juntos se planto o resto?");
  else if (a.portoes) poe(4, "relogio", "Em 19/mar e 30/abr, olhamos juntos a chuva e a terra?");
  else if (a.portoes === false) poe(4, "relogio", "Que datas de troca valem na minha estação?");
  const temMand = (p.faixas || []).some((f) => f.anos.some((x) => x.cultura === "Mandioca"));
  const pr = r.financeiro?.precos_raiz || {}, preco = pr[ef.raiz] ?? pr.municipio;
  if (temMand && preco > 0) poe(5, "mandioca", `A raiz vale R$ ${U.num(preco, 2)}/kg na casa de farinha daqui?`);
  if (ef.agua === "irriga") poe(6, "poco", "Com poço ou irrigação, que datas e culturas mudam?");
  else if (ef.agua === "barreiro") poe(6, "gota", `O barreiro${ef.vol_m3 ? ` de ${U.num(ef.vol_m3)} m³` : ""} salva o milho na floração?`);
  if (ef.maniva === "nao") poe(7, "semente", "Onde consigo maniva sadia para plantar?");
  // o que a confiança dos dados daqui pede ao técnico (sem repetir a pergunta das datas)
  const deConf = (conf?.motivos || []).filter((m) => m.peso > 0 && !(j && ["estimada", "ciclo"].includes(m.chave))
    && !(a.portoes === false && m.chave === "portoes"));
  const T = conf ? (conf.nivel === "baixa" ? 2 : 1) : 0;
  deConf.slice(0, T).forEach((m, i) => poe(0.5 + i / 10, "lupa", PERGUNTA_CONF[m.chave] || m.tecnico));
  const fica = new Set([...cand].sort((x, y) => x.prio - y.prio).slice(0, 7));
  return cand.filter((x) => fica.has(x));
}

/** Resumo da roça (uma linha), para o técnico saber de que roçado se fala. */
const ficha = (ef) => [U.ha(ef.ha), FICHA.terra[ef.terra], FICHA.baixio[ef.baixio], FICHA.agua[ef.agua]].filter(Boolean).join(" · ");
const NIV = { alta: "alta", media: "média", baixa: "baixa" };

function texto(ctx, itens, conf) {
  const l = ctx.r.local, hoje = U.dataBR(ctx.r.respostas_usadas?.hoje || new Date().toISOString().slice(0, 10));
  const link = /^https?:$/.test(location.protocol) && !/^(localhost|127\.)/.test(location.hostname) ? `\nO plano: ${location.href}` : "";
  return `QUADRA · ${l.municipio} (${l.uf}) · ${hoje}\nMeu roçado: ${ficha(ctx.ef)}\n\nPerguntas para o técnico:\n`
    + itens.map((x, i) => `${i + 1}. ${x.texto}`).join("\n")
    + (conf ? `\n\nConfiança dos dados aqui: ${NIV[conf.nivel]}.` : "") + `\n${FRASE}${link}`;
}

function papel(ctx, itens, conf) {
  const l = ctx.r.local, hoje = U.dataBR(ctx.r.respostas_usadas?.hoje || new Date().toISOString().slice(0, 10));
  return `<p class="lt-papel-marca">QUADRA · ${U.esc(l.municipio)} (${U.esc(l.uf)}) · ${hoje}</p>
    <h1>Perguntas para o técnico</h1><p>Meu roçado: ${U.esc(ficha(ctx.ef))}</p>
    <ol>${itens.map((x) => `<li><span class="lt-caixa"></span>${U.esc(x.texto)}</li>`).join("")}</ol>
    ${conf ? `<p>Confiança dos dados aqui: <b>${NIV[conf.nivel]}</b>${conf.motivos.length ? ` (${U.esc(conf.motivos.slice(0, 3).map((m) => m.texto.replace(/\.$/, "")).join("; "))})` : ""}.</p>` : ""}
    <p class="lt-papel-notas">Anotações:</p><p class="lt-papel-frase">${U.esc(FRASE)}</p>`;
}

/** Monta a folha de impressão (só a lista) e abre a impressão do navegador. */
export function imprimir(html) {
  document.getElementById("lt-impressao")?.remove();
  const d = document.createElement("div");
  d.id = "lt-impressao";
  d.className = "lt-papel";
  d.innerHTML = html;
  document.body.append(d);
  document.body.classList.add("imprime-tecnico");
  window.addEventListener("afterprint", () => { d.remove(); document.body.classList.remove("imprime-tecnico"); }, { once: true });
  window.print();
}

async function copiar(t) {
  try { await navigator.clipboard.writeText(t); return true; } catch (_) { /* sem permissão: tenta o jeito antigo */ }
  const ta = Object.assign(document.createElement("textarea"), { value: t });
  ta.style.cssText = "position:fixed;opacity:0";
  document.body.append(ta);
  ta.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch (_) { ok = false; }
  ta.remove();
  return ok;
}

export default {
  id: "leve_ao_tecnico",
  async render(el, ctx, opcoes = {}) {
    const dados = opcoes.dados || await carregar();
    const conf = confiancaDe(dados, ctx.cod || ctx.r.local?.cod, ctx.r);
    const itens = perguntas(ctx, conf);
    const pct = ctx.r.padroes?.pct_orientacao_tecnica, k = pct == null ? null : Math.round(pct);
    const uf = ctx.r.local?.uf;
    const sub = k == null ? "" : k === 0 ? "Aqui, quase nenhuma roça de família recebe orientação técnica."
      : `Aqui, ${k < 30 ? "só " : ""}${k} de 100 roças de família recebem orientação técnica.`;
    el.innerHTML = `<section class="painel lt" id="leve-ao-tecnico" aria-label="Leve para o técnico">
      <p class="kicker">Leve para o técnico</p>
      <div class="lt-cab"><span class="numero-grande">${itens.length}</span><div><b class="lt-tit">perguntas para a próxima conversa</b>
        ${sub ? `<p class="lt-sub">${U.esc(sub)} ${U.selo("medido", "IBGE, Censo Agropecuário 2017: % dos estabelecimentos familiares com orientação técnica")}</p>` : ""}</div></div>
      <ol class="lt-lista">${itens.map((x) => `<li><label><input type="checkbox" class="lt-marca">${U.ic(x.icone)}<span>${U.esc(x.texto)}</span></label></li>`).join("")}</ol>
      <div class="lt-acoes">
        <button type="button" class="botao secundario" data-lt="imprimir">${U.ic("faixas")}Imprimir</button>
        <button type="button" class="botao primario" data-lt="copiar">${U.ic("seta")}Copiar para o WhatsApp</button>
        <span class="lt-aviso" role="status" aria-live="polite"></span></div>
      ${U.verMais(`<p>Quem pode conferir: o técnico do órgão de assistência rural do estado${ATER[uf] ? ` (${ATER[uf]})` : ""}, o sindicato dos
        trabalhadores rurais, a secretaria de agricultura do município, a casa de farinha (preço da raiz) e o vizinho que planta há anos.</p>
        <p>As perguntas saem das suas respostas e do plano. O QUADRA não vê do espaço a sua terra, o seu baixio nem a sua semente.</p>`, "Onde achar quem confira")}
    </section>`;
    const aviso = el.querySelector(".lt-aviso");
    el.querySelector('[data-lt="imprimir"]').addEventListener("click", () => imprimir(papel(ctx, itens, conf)));
    el.querySelector('[data-lt="copiar"]').addEventListener("click", async () => {
      aviso.textContent = (await copiar(texto(ctx, itens, conf))) ? "Copiado. Cole no WhatsApp." : "Não deu para copiar aqui.";
    });
  },
  // para o teste (web/teste/voce_decide.html): a folha de impressão e o texto, sem abrir a impressão
  _papel: papel, _texto: texto,
};
