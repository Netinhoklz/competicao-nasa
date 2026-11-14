// Passo 1, "O lugar": o que este município permite, sem perguntar nada (núcleo do José: ZARC + GAEZ + NASA POWER/IMERG/SMAP + ONI).
const SIT = {
  "indicada": ["ok", "Indicado", "ZARC 2026/27 com risco de 20% em algum solo e ciclo"],
  "com risco": ["risco", "Com risco", "o ZARC daqui só chega a 30% ou 40% de risco"],
  "só aptidão": ["apto", "Apto, sem ZARC aqui", "sem zoneamento neste município; a aptidão do FAO GAEZ v4 (pouco insumo) passa de 40"],
  "apta (GAEZ)": ["apto", "Apto (GAEZ)", "aptidão do FAO GAEZ v4 acima de 40"],
  "literatura": ["lit", "Só na literatura", "sem camada GAEZ/ZARC; vem de estudos no semiárido"],
};

function doy(ddmm) {
  if (!ddmm) return null;
  const [d, m] = ddmm.split("/").map(Number);
  return (Date.UTC(2026, m - 1, d) - Date.UTC(2026, 0, 1)) / 864e5 + 1;
}

function regua(r, U) {
  const reg = r.este_ano.regime, ini = r.este_ano.inicio;
  if (!reg) return "";
  const m0 = reg.mes_inicio, w = 100 / 365;
  const meses = U.MESES.map((m, i) => `<span style="left:${(Date.UTC(2026, i, 1) - Date.UTC(2026, 0, 1)) / 864e5 * w}%">${m}</span>`).join("");
  const faixa = [];
  for (let k = 0; k < 4; k++) {
    const m = (m0 - 1 + k) % 12;
    const a = (Date.UTC(2026, m, 1) - Date.UTC(2026, 0, 1)) / 864e5, b = (Date.UTC(2026, m + 1, 1) - Date.UTC(2026, 0, 1)) / 864e5;
    faixa.push(`<i class="regua-chuva" style="left:${a * w}%;width:${(b - a) * w}%"></i>`);
  }
  let marcas = "";
  if (ini) {
    const p10 = doy(ini.p10), p90 = doy(ini.p90), med = doy(ini.mediana);
    if (p10 && p90) {
      const seg = p10 <= p90 ? [[p10, p90]] : [[p10, 365], [1, p90]];
      marcas += seg.map(([a, b]) => `<i class="regua-inicio" style="left:${a * w}%;width:${(b - a) * w}%" title="8 em 10 anos a chuva começa entre ${ini.p10} e ${ini.p90}"></i>`).join("");
    }
    if (med) marcas += `<b class="regua-mediana" style="left:${med * w}%" title="Início típico ${ini.mediana}"></b>`;
  }
  const z = r.este_ano.zarc_primeiro;
  return `<div class="cartao"><h3>A estação de chuva aqui ${U.selo("medido", "GPM IMERG via NASA POWER, 1998–2025 (2026 é preliminar e fica fora)")}</h3>
    <div class="regua" role="img" aria-label="Meses da estação chuvosa e do início típico da chuva">${faixa.join("")}${marcas}<div class="regua-meses">${meses}</div></div>
    <p class="regua-legenda"><span class="ch-chuva"></span> estação chuvosa típica: <b>${U.esc(reg.estacao)}</b>
      (${U.num(reg.chuva_mm)} mm, ${U.num(reg.fracao * 100)}% da chuva do ano)
      ${ini ? `<span class="ch-inicio"></span> a chuva começa entre <b>${U.esc(ini.p10)}</b> e <b>${U.esc(ini.p90)}</b> em 8 de 10 anos (típico ${U.esc(ini.mediana)})` : ""}</p>
    ${z && (z.ate40 || z.risco20) ? `<p class="sub pequeno">ZARC 2026/27 ${U.selo("medido", "MAPA, tábua de risco aberta")}: alguma cultura anual do
      cardápio fica zoneada desde ${U.esc(z.ate40 || "—")} (risco até 40%) e com risco de 20% desde ${U.esc(z.risco20 || "nenhum decêndio")}.</p>` : ""}</div>`;
}

function hoje(r, U) {
  const e = r.este_ano, a = r.agenda;
  const sabemos = [
    `<b>O oceano:</b> ${U.esc(e.texto_oni)} ${U.selo("medido", "NOAA/CPC ONI")}`,
    e.chuva_recente ? `<b>A chuva recente:</b> ${U.esc(e.chuva_recente)} ${U.selo("medido", "IMERG Late/Early, preliminar")}` : "",
    e.smap?.status === "ok" ? `<b>O solo agora:</b> posição ${e.smap.posto} de ${e.smap.anos} anos (1 = o mais seco), ${U.esc(e.smap.classe)}.
      Fora da estação, isso não prevê a próxima. ${U.selo("medido", "NASA SMAP L4, 30 dias até " + e.smap.fim)}` : "",
  ].filter(Boolean);
  const naoSabemos = ["Como vai estar o Atlântico de fevereiro a abril, que decide boa parte da quadra.",
    "Quanto vai chover em 2027 aqui: o El Niño puxa para menos, mas 2024 foi El Niño forte e a quadra do CE foi normal.",
    "A data exata em que a chuva vai começar."];
  const fazer = (a?.agora || []).slice(0, 4);
  return `<div class="cartao hoje-cartao"><h2>Hoje, ${U.esc(a?.hoje_txt || "")}</h2>
    <div class="grade-3 hoje-grade">
      <div><h3>O que já sabemos</h3><ul>${sabemos.map((s) => `<li>${s}</li>`).join("")}</ul></div>
      <div><h3>O que ainda não sabemos</h3><ul>${naoSabemos.map((s) => `<li>${U.esc(s)}</li>`).join("")}</ul></div>
      <div><h3>O que dá para fazer agora</h3><ul>${fazer.map((s) => `<li>${U.esc(s)}</li>`).join("")}</ul></div>
    </div></div>`;
}

function elNino(r, U) {
  const e = r.este_ano, u = r.el_nino_uf;
  let h = `<div class="cartao ${e.alerta ? "alerta-cartao" : ""}"><h2>El Niño e a estação de 2027</h2>`;
  if (u && u.pct_terco_seco) {
    const anos = (u.anos || Object.keys(u.pct_terco_seco)).map(String);
    const comDado = anos.filter((a) => u.pct_terco_seco[a] != null);
    const acaso = u.acaso_pct ?? 33;
    h += `<div class="enso">
      <div class="enso-num"><span class="numero-grande">${U.num(Math.round((u.media ?? 0) / 10))} em 10</span>
        <p>municípios do ${U.esc(u.uf)} tiveram a estação no <b>terço mais seco</b> nos anos de El Niño forte (${comDado.join(", ")})
        ${U.selo("medido", u.definicao || "")}. Pelo acaso seriam ${U.num(acaso / 10)} em 10. Os anos discordam: veja as barras.</p></div>
      <svg class="enso-barras" viewBox="0 0 220 120" role="img" aria-label="Por ano de El Niño forte">
        <line x1="0" x2="220" y1="${100 - acaso}" y2="${100 - acaso}" class="enso-acaso"/>
        ${anos.map((a, i) => { const v = u.pct_terco_seco[a], x = 12 + i * 52;
          if (v == null) return `<text x="${x + 17}" y="96" text-anchor="middle" class="enso-ano">sem dado</text>
            <text x="${x + 17}" y="114" text-anchor="middle" class="enso-ano">${a}</text>`;
          return `<rect x="${x}" y="${100 - v}" width="34" height="${v}" rx="3" class="enso-barra"><title>${a}: ${v}%</title></rect>
          <text x="${x + 17}" y="${96 - v}" text-anchor="middle" class="enso-val">${v}%</text>
          <text x="${x + 17}" y="114" text-anchor="middle" class="enso-ano">${a}</text>`; }).join("")}
        <text x="218" y="${96 - acaso}" text-anchor="end" class="enso-ano">acaso</text>
      </svg></div>`;
    if (comDado.length < anos.length) h += `<p class="sub pequeno">${U.esc((u.avisos || [])[0] || "Sem a estação de 1998 neste estado (o IMERG começa em jan/1998).")}</p>`;
  } else {
    h += `<p class="sub">A manchete do estado ainda está sendo calculada.</p>`;
  }
  if (e.perspectiva) h += `<p><b>O que aconteceu aqui</b> (não é previsão): ${U.esc(e.perspectiva)}</p>`;
  if (e.alerta) h += `<p class="aviso">Ano de alerta neste município: o plano guarda uma parte da leguminosa e prioriza a reserva (mandioca e forragem).</p>`;
  return h + "</div>";
}

function cardapio(r, U) {
  const jan = Object.fromEntries((r.agenda?.culturas || []).map((c) => [c.cultura, c]));
  const grupos = { ok: [], risco: [], apto: [], lit: [], fora: [] };
  for (const i of r.cardapio) {
    const s = SIT[i.situacao];
    (s ? grupos[s[0]] : grupos.fora).push(i);
  }
  const bloco = (i) => {
    const s = SIT[i.situacao] || ["fora", i.situacao, ""], j = jan[i.cultura];
    return `<div class="bloco-cultura b-${s[0]}" title="${U.esc(i.base)}">
      <div class="bc-topo"><b>${U.esc(i.cultura)}</b><span class="bc-selo">${U.esc(s[1])}</span></div>
      <div class="bc-papel">${U.esc(i.papel)}</div>
      ${j && j.plantar && j.plantar !== "—" ? `<div class="bc-jan">🌱 plantar ${U.esc(j.plantar.split(" (")[0])}</div>` : ""}
      ${j && j.colher && j.colher !== "—" ? `<div class="bc-jan">🧺 colher ${U.esc(j.colher.split(" (")[0])}</div>` : ""}
    </div>`;
  };
  const sec = (k, titulo, cor) => grupos[k].length ? `<div class="cardapio-grupo"><h3><span class="bolinha ${cor}"></span>${titulo} (${grupos[k].length})</h3>
    <div class="cardapio-blocos">${grupos[k].map(bloco).join("")}</div></div>` : "";
  const ok = grupos.ok.length + grupos.apto.length;
  return `<div class="cartao"><h2>O que dá para plantar aqui</h2>
    <p class="sub">${ok} de ${r.cardapio.length} culturas do cardápio servem neste município. Onde a cultura tem ZARC, o ZARC decide; senão, o
    FAO GAEZ v4. As datas valem para qualquer terra; no passo 2 você diz como é a sua e elas se ajustam.
    ${U.selo("medido", "ZARC/MAPA 2026/27 e FAO GAEZ v4; datas de colheita = plantio + ciclo (suposição)")}</p>
    ${sec("ok", "Indicadas (risco de 20%)", "b-ok")}${sec("apto", "Aptas, sem ZARC aqui", "b-apto")}${sec("risco", "Com mais risco", "b-risco")}
    ${sec("lit", "Só na literatura do semiárido", "b-lit")}
    ${grupos.fora.length ? `<p class="sub pequeno">Não servem aqui: ${grupos.fora.map((i) => U.esc(i.cultura)).join(", ")}.</p>` : ""}
    <details><summary>Tabela técnica (aptidão, risco, solo × ciclo, fonte)</summary>
      <table><tr><th>Cultura</th><th>Aptidão GAEZ</th><th>Risco 20%</th><th>Até 40%</th><th>Solo × ciclo</th><th>Fonte</th></tr>
      ${r.cardapio.map((i) => `<tr><td>${U.esc(i.cultura)}</td><td>${i.aptidao == null ? U.esc(i.classe) : U.num(i.aptidao) + " · " + U.esc(i.classe)}</td>
        <td>${U.esc(i.risco20 || "—")}</td><td>${U.esc(i.risco40 || "—")}</td><td>${U.esc(i.solo_ciclo || "—")}</td><td class="sub pequeno">${U.esc(i.base)}</td></tr>`).join("")}
      </table></details></div>`;
}

function clima(r, U) {
  const c = r.clima, a = r.analogos?.[0];
  if (!a) return "";
  return `<details class="cartao"><summary>De onde vem a evidência das regras (estudos de clima parecido, NASA POWER)</summary>
    <p>O clima daqui (chuva ${U.num(c.chuva_anual_mm)} mm/ano, aridez ${U.num(c.aridez_P_ET0, 2)}, ${U.num(c.meses_umidos)} meses úmidos) é mais
    parecido com <b>${U.esc(a.lugar)}</b> (${U.esc(a.artigos)}): peso de transferência ${U.num(a.w, 2)}, ${U.esc(r.confianca.texto)}.
    ${U.selo("medido", c.fonte)}</p></details>`;
}

export default {
  id: "lugar",
  titulo: "O lugar",
  render(el, ctx) {
    const { r, util: U } = ctx;
    el.innerHTML = `<div class="titulo-passo"><h1>O que ${U.esc(r.local.municipio)} permite</h1>
      <p>Sem perguntar nada ainda: o que os dados da NASA, do zoneamento agrícola (ZARC) e do IBGE dizem sobre este lugar.</p></div>
      ${hoje(r, U)}${elNino(r, U)}${regua(r, U)}${cardapio(r, U)}${clima(r, U)}
      <div class="cta-lugar"><a class="botao primario" href="${ctx.link(2)}">Responder 5 perguntas sobre a sua roça →</a>
      <a class="botao-leve" href="${ctx.link(3)}">Pular e ver o plano com os padrões</a></div>`;
  },
};
