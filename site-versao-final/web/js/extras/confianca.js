// QUADRA, ponto 16: "Confiança dos dados aqui". Um medidor de 3 barras (como o sinal do celular), até 3 motivos curtos e,
// no "ver mais", todos os motivos, onde o técnico pesa mais e como o nível é calculado.
// Dados: web/dados/confianca_mun.json (ferramentas/preparar_confianca.py): critérios objetivos que o núcleo já usa.
// A agenda da resposta da API (com as respostas do agricultor) refina dois critérios: "estimada" e "portoes".
import * as U from "../comum.js";

const URL_DADOS = new URL("../../dados/confianca_mun.json", import.meta.url); // = dados/confianca_mun.json a partir de roca.html
let promessa = null;

/** Lê o JSON uma vez (null se faltar: o bloco some sem erro). */
export function carregar() {
  promessa ||= fetch(URL_DADOS).then((r) => (r.ok ? r.json() : null)).catch(() => null)
    .then((j) => { if (!j) promessa = null; return j; });
  return promessa;
}

const NOME = { "Feijão-caupi": "caupi", "Feijão comum": "feijão", "Sorgo forrageiro": "sorgo", "Sorgo granífero": "sorgo de grão" };
const lista = (v) => (v.length <= 1 ? v.join("") : v.slice(0, -1).join(", ") + " e " + v[v.length - 1]);

/** Culturas anuais do plano com a data de plantar estimada pela chuva (sem ZARC), pela agenda da API. */
function estimadas(r) {
  const ls = (r?.agenda?.linhas || []).filter((l) => l.parte !== "Bordas" && l.barras.some((b) => b.tipo === "estimado"));
  return [...new Set(ls.map((l) => NOME[l.cultura] || l.cultura.toLowerCase()))];
}

/**
 * Contrato: {nivel: "alta"|"media"|"baixa", motivos: [{chave, texto, peso, tecnico}], tecnico: [texto]} ou null.
 * dados = o JSON (carregar()); r = ctx.r (opcional: refina "estimada" e "portoes" com a agenda das respostas).
 */
export function confiancaDe(dados, cod, r = null) {
  const T = dados?._textos, base = dados?.[cod];
  if (!T || !base) return null;
  const m = new Set(base.motivos);
  const est = r?.agenda ? estimadas(r) : null;
  if (est) est.length ? m.add("estimada") : m.delete("estimada");
  if (r?.agenda?.portoes === false) m.add("portoes");
  else if (r?.agenda?.portoes === true) m.delete("portoes");
  const ordem = Object.keys(T);
  const chaves = [...m].filter((k) => T[k]).sort((a, b) => T[b].peso - T[a].peso || ordem.indexOf(a) - ordem.indexOf(b));
  const soma = chaves.reduce((s, k) => s + T[k].peso, 0);
  const texto = (k) => (k === "estimada" && est?.length ? `Data de plantar ${est.length > 1 ? "de" : "da"} ${lista(est)} estimada pela chuva.` : T[k].texto);
  return {
    nivel: soma <= 1 ? "alta" : soma <= 3 ? "media" : "baixa",
    motivos: chaves.map((k) => ({ chave: k, texto: texto(k), peso: T[k].peso, tecnico: T[k].tecnico })),
    tecnico: [...new Set(chaves.map((k) => T[k].tecnico))],
  };
}

const NIVEL = {
  alta: { rot: "Alta", barras: 3, frase: "Os dados cobrem bem este lugar. Mesmo assim, confira na roça." },
  media: { rot: "Média", barras: 2, frase: "Os dados ajudam, mas aqui alguns pontos pedem o seu olho." },
  baixa: { rot: "Baixa", barras: 1, frase: "Aqui os dados têm buracos. Decida junto com o técnico." },
};

// o detalhe de cada motivo (vai no "ver mais"), com a fonte
const DETALHE = {
  leste: "A até ~20 km da costa leste, o satélite de chuva (GPM IMERG) capta só 39–72% da chuva medida no chão, mais no outono e no inverno. Aqui as datas vêm do zoneamento (ZARC) e o pluviômetro vale mais que o satélite.",
  agro: "O rendimento típico do IBGE (PAM 1998–2025) passa de 2 vezes o da roça de família da CONAB (milho 1.800, feijão 800, mandioca 17.400 kg/ha): a série mistura lavoura grande. Os R$ do passo 4 servem só para comparar.",
  pam_curta: "Milho ou feijão têm menos de 10 anos com 10 ha ou mais no IBGE (PAM 1998–2025): sem série, o passo 4 não faz a conta do dinheiro.",
  mandioca_sem_serie: "A mandioca entra no plano, mas o IBGE não tem série dela aqui: sem projeção nem R$ da mandioca.",
  mandioca_repete: "Em 30% dos anos ou mais, o IBGE repete aqui o rendimento da mandioca do ano anterior: o leque dela parece mais seguro do que é.",
  estimada: "Sem zoneamento (ZARC) desta cultura aqui, a data de plantar vai do início típico da chuva (IMERG, 1998–2025) a 40 dias depois. É suposição.",
  ciclo: "O zoneamento junta grupos de ciclo (precoce, médio, tardio) sem conferir quais sementes existem no estado. Só caupi, sorgo forrageiro e mamona do Ceará foram conferidos; o milho, em lugar nenhum. Por valer em quase todo o Nordeste, não baixa o nível.",
  el_nino: "Nos El Niños fortes com dado do satélite (2010, 2016 e 2024), a chuva da estação daqui teve pelo menos um ano com 75% do normal ou menos e outro com o normal ou mais. O mar sozinho não decide 2027.",
  smap: "O satélite de umidade do solo (NASA SMAP L4) não tem leitura no pixel deste município.",
  portoes: "Os portões de 19/mar e 30/abr foram medidos no sertão do Ceará, onde a chuva é a quadra. Aqui a estação ou as janelas do zoneamento são outras: as datas de troca e de salvar ainda não foram medidas.",
  analogos: "Nenhum lugar dos estudos de rotação tem clima parecido com o daqui (semelhança abaixo de 0,3 no clima do NASA POWER): as regras valem só como direção.",
};
const COMO = "Cada motivo pesa 2 (satélite perto do mar, lavoura grande no IBGE, série curta do IBGE), 1 (os outros) ou 0 (ciclo da semente). "
  + "Soma 0 ou 1: alta; 2 ou 3: média; 4 ou mais: baixa. Os critérios são medidos; os pesos são escolha do QUADRA.";

export default {
  id: "confianca",
  /** Desenha o medidor dentro de el. opcoes.dados: o JSON já carregado (para não buscar de novo). */
  async render(el, ctx, opcoes = {}) {
    const dados = opcoes.dados || await carregar();
    const c = confiancaDe(dados, ctx.cod || ctx.r?.local?.cod, ctx.r);
    if (!c) { el.innerHTML = ""; return; }
    const n = NIVEL[c.nivel];
    const selo = U.selo("suposicao", `nível = regra do QUADRA sobre critérios medidos (${dados._sobre?.script || "preparar_confianca.py"}, ${dados._sobre?.gerado || ""})`);
    const frente = c.motivos.slice(0, 3);
    const persp = ctx.r?.este_ano?.perspectiva;
    const todos = c.motivos.map((m) => `<li><b>${U.esc(m.texto)}</b> ${U.esc(DETALHE[m.chave] || "")}${m.chave === "el_nino" && persp
      ? ` <span class="sub">${U.esc(persp.split(". ")[0].replace(", 1 ficaram", ", 1 ficou"))}.</span>` : ""}</li>`).join("");
    el.innerHTML = `<section class="painel cf cf-${c.nivel}" aria-label="Confiança dos dados aqui">
      <p class="kicker">Confiança dos dados aqui ${selo}</p>
      <div class="cf-grade">
        <div class="cf-linha">
          <span class="cf-sinal" role="img" aria-label="Confiança ${n.rot.toLowerCase()}: ${n.barras} de 3 barras">${[1, 2, 3].map((i) =>
            `<i class="${i <= n.barras ? "on" : ""}"></i>`).join("")}</span>
          <div><b class="cf-nivel">${n.rot}</b><p class="cf-frase">${n.frase}</p></div>
        </div>
        ${frente.length ? `<ul class="cf-motivos">${frente.map((m) => `<li class="p${m.peso}">${U.esc(m.texto)}</li>`).join("")}</ul>`
          : `<p class="cf-motivos-vazio sub">Nenhum aviso nos dados daqui.</p>`}
      </div>
      ${U.verMais(`${todos ? `<ul class="cf-todos">${todos}</ul>` : ""}
        ${c.tecnico.length ? `<h4>Onde o técnico pesa mais aqui</h4><ul>${c.tecnico.map((t) => `<li>${U.esc(t)}</li>`).join("")}</ul>` : ""}
        <h4>Como o nível é calculado</h4><p>${U.esc(COMO)}</p>`, "Ver por quê")}
    </section>`;
  },
};
