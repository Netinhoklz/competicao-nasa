// Passo 2, "Sua roça": as perguntas que mudam o plano. Entram depois das opções e antes do plano (PLANO_INTEGRACAO.md, decisão 4).
// Toda pergunta tem "não sei" (vale o padrão do município) e diz o que muda. A da terra usa as palavras do Vicente
// (interface-inicial-vicente) e alimenta o ZARC por solo do núcleo do José.
let anterior = null; // janelas da resposta anterior, para dizer "o que mudou"

const P = {
  terra: {
    titulo: "Quando chove forte, como fica a terra do seu roçado?",
    muda: "as datas de plantio (o ZARC muda com o solo)",
    opcoes: [["", "Não sei", "mostro as datas que valem em qualquer terra"], ["arenosa", "Seca rápido, a água some", "terra arenosa"],
      ["mista", "Segura a umidade, não empoça", "terra misturada"], ["barro", "Encharca, gruda no pé", "terra de barro"]],
  },
  baixio: {
    titulo: "Tem um baixio, a parte mais baixa que fica úmida depois da chuva?",
    muda: "onde fica o milho; sem baixio, o cereal sai do plano",
    opcoes: [["", "Não sei", "desenho ⅓ tracejado"], ["nao", "Não tenho", ""], ["pouco", "Um pedaço pequeno", "~1/5"],
      ["terco", "Uns ⅓ do roçado", ""], ["metade", "Metade ou mais", ""]],
  },
  agua: {
    titulo: "Além da chuva, que água você tem para a roça?",
    muda: "o que dá para salvar no fim da estação",
    opcoes: [["", "Só a chuva", ""], ["cisterna", "Cisterna de beber", "é água da casa"], ["barreiro", "Barreiro, açude ou calçadão", ""],
      ["irriga", "Poço ou irrigação", ""]],
  },
  maniva: {
    titulo: "Mandioca: como está a sua?",
    muda: "a reserva para o ano ruim (a mandioca fica no chão de um ano para o outro)",
    opcoes: [["", "Consigo maniva para plantar", "padrão"], ["plantada", "Já tenho mandioca plantada", ""], ["nao", "Não consigo maniva", ""]],
  },
  criacao: {
    titulo: "Tem criação?",
    muda: "o peso da forragem no plano (sem preço: é comida dos animais)",
    opcoes: [["", "Não quero dizer", ""], ["nenhuma", "Nenhuma", ""], ["pequenos", "Cabras ou ovelhas", ""], ["gado", "Gado", ""]],
  },
};

function janelas(r) {
  return Object.fromEntries((r.agenda?.culturas || []).map((c) => [c.cultura, (c.plantar || "").split(" (")[0]]));
}

function pergunta(k, ctx, extra = "") {
  const p = P[k], U = ctx.util, atual = ctx.resp[k] || "";
  return `<fieldset class="pergunta"><legend>${U.esc(p.titulo)}</legend>
    <div class="opcoes">${p.opcoes.map(([v, t, s]) => `<button type="button" class="opcao ${v === atual ? "marcada" : ""}" data-k="${k}" data-v="${v}">
      <b>${U.esc(t)}</b>${s ? `<span>${U.esc(s)}</span>` : ""}</button>`).join("")}</div>
    <p class="muda">Muda: ${U.esc(p.muda)}.</p>${extra}</fieldset>`;
}

export default {
  id: "perguntas",
  titulo: "Sua roça",
  render(el, ctx) {
    const { r, ef, util: U } = ctx;
    const pad = r.padroes || {};
    const jan = janelas(r);
    // o que mudou desde a última resposta (só as culturas do plano)
    let mudou = "";
    if (anterior && anterior.cod === ctx.cod) {
      const dif = Object.keys(jan).filter((c) => anterior.jan[c] && jan[c] && anterior.jan[c] !== jan[c]).slice(0, 4);
      if (dif.length) mudou = `<div class="aviso verde mudou"><b>O que mudou:</b> ${dif.map((c) => `${U.esc(c)}: ${U.esc(anterior.jan[c])} → <b>${U.esc(jan[c])}</b>`).join("; ")}.</div>`;
    }
    anterior = { cod: ctx.cod, jan };
    const leg = r.plano?.leguminosa, chave = [leg, "Mandioca", "Milho"].filter((c) => c && jan[c]);
    const datas = chave.length ? `<p class="sub pequeno">Com a resposta atual: ${chave.map((c) => `${U.esc(c)} ${U.esc(jan[c])}`).join(" · ")}
      ${U.selo("medido", "ZARC 2026/27 por solo")}</p>` : "";
    const padVal = pad.rocado_ha > 0 ? pad.rocado_ha : pad.rocado_ha_padrao;
    const padHa = padVal > 0 ? `Padrão: ${U.ha(padVal)}, a área típica de milho por família ${pad.rocado_ha > 0 ? "aqui" : "na mesorregião"} (Censo Agro 2017).`
      : "Sem padrão do Censo aqui: usamos 1 ha.";
    const vol = ef.vol_m3 || 0;
    const aguaExtra = ef.agua === "barreiro"
      ? `<label class="campo">Quanto cabe, mais ou menos? <input type="number" min="0" step="10" id="vol" value="${U.esc(ctx.resp.vol)}" placeholder="m³"> m³</label>
         ${vol ? `<p class="aviso">Com ${U.num(vol)} m³ dá para molhar uns <b>${U.num(vol / 620, 2)} ha</b> de milho na floração (62 mm), no fim da estação.
         ${U.selo("suposicao", "62 mm por rega de salvação; volume informado pela família")}</p>` : ""}`
      : ef.agua === "irriga" ? `<p class="aviso">Com irrigação, as datas de sequeiro deixam de ser o limite. O QUADRA mostra o sequeiro; combine o irrigado com o técnico.</p>`
      : ef.agua === "cisterna" ? `<p class="sub pequeno">A cisterna de placa é água de beber: não muda o plano.</p>`
      : (pad.pct_irrig != null ? `<p class="sub pequeno">Em ${U.esc(r.local.municipio)}, ${U.num(pad.pct_irrig, 0)}% dos estabelecimentos irrigam (Censo 2017).</p>` : "");
    const maniExtra = ef.maniva === "plantada" ? `<p class="sub pequeno">Bom: a Parte A já tem reserva em 2027 (entra no dinheiro).</p>`
      : ef.maniva === "nao" ? `<p class="aviso">Sem maniva, o plano gira sem a mandioca: a reserva do ano ruim fica só na forragem.</p>` : "";
    el.innerHTML = `<div class="titulo-passo"><h1>Sua roça</h1>
      <p>Cinco perguntas, um toque cada. "Não sei" sempre vale: usamos o padrão de ${U.esc(r.local.municipio)} e avisamos. Dá para mudar depois.</p></div>
      ${mudou}
      <div class="cartao">${pergunta("terra", ctx, datas)}</div>
      <div class="cartao"><fieldset class="pergunta"><legend>Qual o tamanho do roçado que você planta?</legend>
        <div class="opcoes">${[0.5, 1, 2, 3, 5].map((v) => `<button type="button" class="opcao curta ${+ctx.resp.ha === v ? "marcada" : ""}" data-k="ha" data-v="${v}"><b>${U.ha(v)}</b></button>`).join("")}
          <label class="campo">outro: <input type="number" min="0.1" max="50" step="0.1" id="ha" value="${U.esc(ctx.resp.ha)}" placeholder="${U.num(ef.ha, 1)}"> ha</label></div>
        <p class="muda">Muda: o tamanho de cada parte no desenho e o dinheiro. ${U.esc(padHa)} 1 tarefa ≈ 0,3 ha ${U.selo("suposicao", "tarefa cearense de 3.025 m², a conferir")}.
          ${ef.ha > 5 ? "Acima de 5 ha, fica fora do Garantia-Safra." : ""}</p></fieldset>
        ${pergunta("baixio", ctx)}</div>
      <div class="cartao">${pergunta("agua", ctx, aguaExtra)}</div>
      <div class="cartao">${pergunta("maniva", ctx, maniExtra)}${pergunta("criacao", ctx)}</div>
      <div class="cta-lugar"><a class="botao primario" href="${ctx.link(3)}">Ver como plantar →</a>
        <a class="botao-leve" href="${ctx.link(3)}">Pular: usar os padrões</a></div>`;
    el.querySelectorAll(".opcao").forEach((b) => b.addEventListener("click", () => ctx.set({ [b.dataset.k]: b.dataset.v })));
    el.querySelector("#ha")?.addEventListener("change", (e) => ctx.set({ ha: e.target.value }));
    el.querySelector("#vol")?.addEventListener("change", (e) => ctx.set({ vol: e.target.value }));
  },
};
