// QUADRA, ponto 16: "Leve para o técnico". 5 a 7 perguntas e confirmações tiradas das respostas e do plano (solo, baixio,
// faixas, datas, metade guardada e portões, preço da raiz, água, maniva) e dos motivos de confiança do município; a água além da
// chuva (2 chips, gravam `agua`); a linha do Garantia-Safra; dois botões: imprimir (só a lista, numa folha clara; CSS em
// css/extras/voce_decide.css) e copiar o texto. compartilhar(ctx, { plano, tarefas }) é o botão verde "Mandar no WhatsApp" do
// Relatório (passo 5): leva o plano escolhido e as próximas tarefas com as datas (relatorio.js) antes das perguntas.
// As perguntas seguem o plano que o Plano, o Dinheiro e o Relatório mostram (ideal.escolhido; sem o motor, o plano do núcleo).
import * as U from "../comum.js";
import { carregar, confiancaDe } from "./confianca.js";
import { FRASE } from "./voce_decide.js";

const NOME = { "Feijão-caupi": "feijão", "Feijão comum": "feijão comum", "Sorgo forrageiro": "sorgo", "Sorgo granífero": "sorgo de grão", Amendoim: "amendoim" };
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
  agua: { chuva: "roça de chuva", cisterna: "cisterna de beber", barreiro: "barreiro ou açude", irriga: "poço ou irrigação" },
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
function janela(plano, linhas) {
  const ls = (linhas || []).filter((l) => l.estacao === 2027 && l.parte !== "Bordas" && !/em pé/.test(l.cultura));
  const l = ls.find((x) => x.cultura === plano?.leguminosa) || ls.find((x) => x.barras?.length) || ls[0];
  const b = l?.barras.find((x) => x.tipo === "plantio" || x.tipo === "estimado");
  return b ? { cultura: curto(l.cultura), txt: `${U.dataBR(b.de, true)} a ${U.dataBR(b.ate, true)}` } : null;
}

/** O plano escolhido (ideal.escolhido: o mesmo do Plano, do Dinheiro e do Relatório) e as linhas da agenda dele; sem o motor,
 *  null (vale o plano do núcleo, r.plano e r.agenda.linhas). */
async function escolhidoDe(ctx) {
  try {
    const m = await import("./ideal.js");
    const e = m.escolhido(ctx.r, ctx.resp || {}, ctx.ef);
    return e?.plano ? { plano: e.plano, linhas: e.linhas } : null;
  } catch (_) { return null; }
}

/** As perguntas (até 7): {icone, texto}. conf = confiancaDe(...) ou null; base = { plano, linhas } do plano escolhido (padrão:
 *  r.plano e r.agenda.linhas). */
export function perguntas(ctx, conf, base = null) {
  const { r, ef } = ctx, p = base?.plano || r.plano || {}, a = r.agenda || {}, linhas = base?.linhas || a.linhas;
  const cand = [];
  const poe = (prio, icone, texto) => cand.push({ prio, icone, texto });
  const [icT, tT] = TERRA[ef.terra] || TERRA.nao_sei;
  poe(1, icT, tT);
  const bx = (p.faixas || []).find((f) => f.parte === "Baixio")?.anos?.[0], cereal = curto(bx?.cultura || "milho");
  // a leguminosa entra no baixio só quando a célula diz revezamento ("solteiro" e "sem revezamento" não põem)
  const revez = !bx || (/revezamento/i.test(bx.texto || "") && !/sem revezamento/i.test(bx.texto || ""));
  if (ef.tem_baixio === null) poe(2, "gota", "Tenho baixio? Que parte do roçado fica úmida?");
  else if (ef.tem_baixio) poe(2, "milho", `O baixio (${U.ha(ef.baixio_ha)}) aguenta ${cereal}${p.leguminosa && revez ? ` com ${curto(p.leguminosa)}` : ""}?`);
  else poe(2, "milho", "Sem baixio, onde o milho tem mais chance?");
  poe(8, "faixas", "As faixas e o espaçamento cabem no meu terreno?");
  const j = janela(p, linhas);
  if (j) poe(3, "calendario", `Plantar ${j.cultura} de ${j.txt} serve à minha semente?`);
  const metade = /metade/i.test(p.interruptor || "");
  if (metade && a.portoes) poe(4, "relogio", "Metade guardada: em 19/mar e 30/abr, decidimos juntos se planto o resto?");
  else if (a.portoes) poe(4, "relogio", "Em 19/mar e 30/abr, olhamos juntos a chuva e a terra?");
  else if (a.portoes === false) poe(4, "relogio", "Que datas de troca valem na minha estação?");
  const temMand = (p.faixas || []).some((f) => f.anos.some((x) => x.cultura === "Mandioca"));
  const pr = r.financeiro?.precos_raiz || {}, kr = pr[ef.raiz] != null ? ef.raiz : "municipio", preco = pr[kr];
  // o rótulo da opção escolhida em "Ajustar a conta" (o padrão é o comum do estado, não o preço daqui)
  const comum = `comum no ${r.local?.uf || "estado"}`;
  const rotRaiz = { municipio: pr.origem_municipio === "UF" ? comum : "daqui", uf_mediana: comum, uf_p25: `baixo no ${r.local?.uf || "estado"}` }[kr];
  if (temMand && preco > 0) poe(5, "mandioca", `A raiz vale R$ ${U.num(preco, 2)}/kg (${rotRaiz}) na casa de farinha?`);
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
const ficha = (ef) => [ef.larg ? `${U.num(ef.larg)} × ${U.num(ef.comp)} m (${U.ha(ef.ha)})` : U.ha(ef.ha), FICHA.terra[ef.terra],
  FICHA.baixio[ef.baixio], FICHA.agua[ef.agua]].filter(Boolean).join(" · ");
const NIV = { alta: "alta", media: "média", baixa: "baixa" };

/** O texto do WhatsApp e do "Copiar o texto". extra = { plano: "Seu jeito, melhorado", partes: "2027: A e C feijão · B milho · …",
 *  material: "caupi ≈ 14 kg, …", tarefas: ["21/02/2027 a 28/02/2027 · Plantar milho (Baixio)", …] } (do Relatório): vão antes das
 *  perguntas. */
function texto(ctx, itens, conf, extra = {}) {
  const l = ctx.r.local, hoje = U.dataBR(ctx.r.respostas_usadas?.hoje || new Date().toISOString().slice(0, 10));
  const link = /^https?:$/.test(location.protocol) && !/^(localhost|127\.)/.test(location.hostname) ? `\nO plano: ${location.href}` : "";
  const plano = extra.plano ? `\nPlano: ${extra.plano}` : "";
  // o que vai em cada parte em 2027 (com a largura das faixas) e o material: o técnico que recebe sabe o que é a Parte A
  const partes = extra.partes ? `\n${extra.partes}` : "", material = extra.material ? `\nMaterial: ${extra.material}` : "";
  const tarefas = extra.tarefas?.length ? `\n\nPróximas tarefas:\n${extra.tarefas.join("\n")}` : "";
  return `QUADRA · ${l.municipio} (${l.uf}) · ${hoje}\nMeu roçado: ${ficha(ctx.ef)}${plano}${partes}${material}${tarefas}\n\nPerguntas para o técnico:\n`
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

/** O aviso do bloco (se ele está na tela) e o rolar até ele, para quem tocou o botão de baixo. */
function avisar(msg) {
  const aviso = document.querySelector("#leve-ao-tecnico .lt-aviso");
  if (!aviso) return;
  aviso.textContent = msg;
  aviso.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/** "Mandar no WhatsApp" (o botão verde do passo 5): o texto do "Copiar o texto" com, à frente, o plano e as próximas tarefas que o
 *  Relatório passa em opcoes ({ plano, tarefas }). Tenta o compartilhar do celular; se não houver, abre o WhatsApp (wa.me); se a
 *  janela for bloqueada, copia. Devolve "share", "cancelou", "wa.me", "copiou" ou "falhou". */
export async function compartilhar(ctx, opcoes = {}) {
  const [dados, base] = await Promise.all([carregar(), escolhidoDe(ctx)]);
  const conf = confiancaDe(dados, ctx.cod || ctx.r.local?.cod, ctx.r);
  const pt = texto(ctx, perguntas(ctx, conf, base), conf, opcoes);
  const t = globalThis.QUADRA_I18N?.t?.(pt) ?? pt; // em inglês, o texto sai traduzido (js/i18n.js; não passa pelo DOM)
  if (navigator.share) {
    try { await navigator.share({ text: t }); return "share"; } catch (e) { if (e?.name === "AbortError") return "cancelou"; } // fechou: não abre outra
  }
  const w = window.open(`https://wa.me/?text=${encodeURIComponent(t)}`, "_blank");
  if (w) { w.opener = null; return "wa.me"; }
  const ok = await copiar(t);
  avisar(ok ? "Copiado. Cole no WhatsApp." : "Não deu para copiar aqui.");
  return ok ? "copiou" : "falhou";
}

// água além da chuva (a cisterna de beber não molha a roça e saiu); tocar de novo no chip aceso volta para "só a chuva"
const AGUA = [["barreiro", "gota", "Barreiro ou açude"], ["irriga", "poco", "Poço ou irrigação"]];

export default {
  id: "leve_ao_tecnico",
  async render(el, ctx, opcoes = {}) {
    const [dados, base] = await Promise.all([opcoes.dados || carregar(), escolhidoDe(ctx)]);
    const conf = confiancaDe(dados, ctx.cod || ctx.r.local?.cod, ctx.r);
    const itens = perguntas(ctx, conf, base);
    const pct = ctx.r.padroes?.pct_orientacao_tecnica, k = pct == null ? null : Math.round(pct);
    const uf = ctx.r.local?.uf;
    const sub = k == null ? "" : k === 0 ? "Aqui, quase nenhuma roça de família recebe orientação técnica."
      : `Aqui, ${k < 30 ? "só " : ""}${k} de 100 roças de família recebem orientação técnica.`;
    // à vista, um "ver mais" com cara de botão e o número no texto; as perguntas e quem confere ficam dentro (imprimir, copiar e o
    // WhatsApp levam todas)
    const li = (x) => `<li><label><input type="checkbox" class="lt-marca">${U.ic(x.icone)}<span>${U.esc(x.texto)}</span></label></li>`;
    el.innerHTML = `<section class="painel lt" id="leve-ao-tecnico" aria-label="Leve para o técnico">
      <p class="kicker">Leve para o técnico</p>
      <details class="ver-mais lt-cab"><summary><b class="lt-tit">${itens.length === 1 ? "Ver a pergunta" : `Ver as perguntas (${itens.length})`}</b></summary>
        <ol class="lt-lista">${itens.map(li).join("")}</ol>
        ${sub ? `<p>${U.esc(sub)} ${U.selo("medido", "IBGE, Censo Agropecuário 2017: % dos estabelecimentos familiares com orientação técnica")}</p>` : ""}
        <p>Quem pode conferir: o técnico do órgão de assistência rural do estado${ATER[uf] ? ` (${ATER[uf]})` : ""}, o sindicato dos
        trabalhadores rurais, a secretaria de agricultura do município, a casa de farinha (preço da raiz) e o vizinho que planta há anos.</p>
        <p>As perguntas saem das suas respostas e do plano. O QUADRA não vê do espaço a sua terra, o seu baixio nem a sua semente.</p></details>
      <div class="lt-agua" role="group" aria-label="Água além da chuva"><span class="lt-agua-rot">Além da chuva, tem:</span>
        ${AGUA.map(([k, ic, rot]) => `<button type="button" class="chip${ctx.ef.agua === k ? " verde" : ""}" data-agua="${k}" aria-pressed="${ctx.ef.agua === k}">${U.ic(ic)}${rot}</button>`).join("")}</div>
      <p class="lt-gs">${U.ic("escudo")}<span><b>Garantia-Safra:</b> paga com perda de 40% ou mais; ${ctx.ef.ha > 5 ? "acima de 5 ha não cabe" : "até 5 ha cabe"};
        renda e adesão do município: confira no sindicato.</span></p>
      <div class="lt-acoes">
        <button type="button" class="botao secundario" data-lt="imprimir">${U.ic("faixas")}Imprimir</button>
        <button type="button" class="botao secundario" data-lt="copiar">${U.ic("seta")}Copiar o texto</button>
        <span class="lt-aviso" role="status" aria-live="polite"></span></div>
    </section>`;
    const aviso = el.querySelector(".lt-aviso");
    el.querySelector('[data-lt="imprimir"]').addEventListener("click", () => imprimir(papel(ctx, itens, conf)));
    el.querySelector('[data-lt="copiar"]').addEventListener("click", async () => {
      aviso.textContent = (await copiar(texto(ctx, itens, conf))) ? "Copiado. Cole no WhatsApp." : "Não deu para copiar aqui.";
    });
    el.querySelectorAll("[data-agua]").forEach((b) => b.addEventListener("click", () => ctx.set({ agua: ctx.ef.agua === b.dataset.agua ? "" : b.dataset.agua })));
  },
  // para o teste (web/teste/voce_decide.html): a folha de impressão e o texto, sem abrir a impressão
  _papel: papel, _texto: texto,
};
