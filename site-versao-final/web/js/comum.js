// QUADRA, site final: utilidades comuns da jornada (sem dependências).
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

/** Número em pt-BR; "—" para vazio. */
export const num = (v, casas = 0) => (v === null || v === undefined || Number.isNaN(+v) ? "—"
  : Number(v).toLocaleString("pt-BR", { maximumFractionDigits: casas, minimumFractionDigits: casas }));

/** R$ em pt-BR; arredonda a 10 reais acima de 1.000 para não dar falsa precisão. */
export const brl = (v) => {
  if (v === null || v === undefined || Number.isNaN(+v)) return "—";
  const a = Math.abs(v) >= 1000 ? Math.round(v / 10) * 10 : Math.round(v);
  return (a < 0 ? "−R$ " : "R$ ") + Math.abs(a).toLocaleString("pt-BR");
};

/** R$ em mil: "R$ 11,5 mil". */
export const brlMil = (v) => (v === null || v === undefined ? "—" : (v < 0 ? "−" : "") + "R$ " + num(Math.abs(v) / 1000, 1) + " mil");

export const pct = (v, casas = 0) => (v === null || v === undefined ? "—" : num(v * 100, casas) + "%");

/** Frequência natural: 0,68 → "7 em 10". */
export const emDez = (p) => (p === null || p === undefined ? "—" : `${Math.round(p * 10)} em 10`);

/** Selo MEDIDO / SUPOSIÇÃO / PROJEÇÃO com a fonte ao passar o mouse (decisão 9 do plano). */
export const selo = (tipo, fonte = "") => {
  const t = { medido: ["medido", "MEDIDO"], suposicao: ["suposicao", "SUPOSIÇÃO"], projecao: ["projecao", "PROJEÇÃO"] }[tipo] || ["suposicao", tipo];
  return `<span class="selo ${t[0]}" title="${esc(fonte)}">${t[1]}</span>`;
};

const MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
export const MESES = MES;
/** "2027-03-11" → "11/03/2027" (ou "11/03" com curto=true). */
export const dataBR = (iso, curto = false) => { if (!iso) return "—"; const [a, m, d] = iso.split("-"); return curto ? `${d}/${m}` : `${d}/${m}/${a}`; };
/** "2027-03-11" → "mar/2027". */
export const mesAno = (iso) => { if (!iso) return "—"; const [a, m] = iso.split("-"); return `${MES[+m - 1]}/${a}`; };

/** Classe CSS do tipo de cultura do motor ("tampão" → "t-tampao"). */
export const tipoCss = (t) => "t-" + String(t || "pousio").normalize("NFD").replace(/[̀-ͯ]/g, "");

/** Área: 1 → "1 ha"; 0,5 → "0,5 ha". */
export const ha = (v) => `${num(v, v < 10 && v % 1 ? 1 : 0)} ha`;

// ---------------------------------------------------------------- ícones (traço, 24×24)
// Os 16 primeiros vêm do painel Roça Certa do João Pedro (js/globo/rocacerta.js); os outros foram feitos para a jornada.
export const IC = {
  onda: '<path d="M2 9c2.5-3 5-3 7.5 0s5 3 7.5 0 3.5-2.2 5-2.5M2 16c2.5-3 5-3 7.5 0s5 3 7.5 0 3.5-2.2 5-2.5"/>',
  chuva: '<path d="M7 15a4.5 4.5 0 0 1 .6-8.96A5.5 5.5 0 0 1 18 7.5a3.75 3.75 0 0 1-.5 7.5M8 18l-1 3M12 18l-1 3M16 18l-1 3"/>',
  gota: '<path d="M12 3c3.5 4.2 5.5 7 5.5 10a5.5 5.5 0 0 1-11 0c0-3 2-5.8 5.5-10z"/>',
  milho: '<path d="M12 3c2.6 2 3.8 5 3.8 8.5S14.5 18 12 21c-2.5-3-3.8-6-3.8-9.5S9.4 5 12 3zM5 12c1.5 4 3.8 7 7 9M19 12c-1.5 4-3.8 7-7 9"/>',
  solo: '<path d="M3 9h18M3 9l2 11h14l2-11M12 9V4M9 6l3-2 3 2"/>',
  broto: '<path d="M12 21v-9M12 12c0-4 2.5-6.5 7-7 0 4.5-2.5 7-7 7zM12 15c0-3-2-5-6-5.5 0 3.5 2 5.5 6 5.5z"/>',
  sol: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  fogo: '<path d="M12 21c-4 0-6.5-2.6-6.5-6.2 0-3.4 2.6-5.4 3.8-8.8 2.4 1.6 3.4 3.6 3.4 5.6 1-.8 1.6-2 1.8-3.4 2 1.8 4 4.2 4 6.8 0 3.4-2.5 6-6.5 6z"/>',
  sino: '<path d="M6 17V11a6 6 0 0 1 12 0v6l1.5 2h-15L6 17zM10 21h4"/>',
  celeiro: '<path d="M3 21V10l9-6 9 6v11M3 21h18M9 21v-6h6v6"/>',
  termo: '<path d="M10 14.5V5a2 2 0 0 1 4 0v9.5a4 4 0 1 1-4 0z"/><path d="M12 10v7"/>',
  ok: '<path d="M5 12.5 10 17l9-10"/>',
  alerta: '<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4M12 17v.5"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16v.5"/>',
  mais: '<path d="M12 5v14M5 12h14"/>',
  mandioca: '<path d="M14 4c1.5-.5 3-.2 4 1M15 3l1-2M18 5l2-1"/><path d="M15 6c-3 0-6 3-8.5 7.5S3.5 21 5 21.5s4.5-1.5 7.5-4.5S17 10 15 6z"/><path d="M9 14l2 1M8 17l2 .5"/>',
  feijao: '<path d="M5 18c-1.5-3 0-8 4-11s9-3.5 10-2c1 1.5-1 6-5 9s-7.5 5.5-9 4z"/><circle cx="10" cy="13" r="1.3"/><circle cx="13" cy="10.5" r="1.3"/><circle cx="16" cy="8" r="1.3"/>',
  vaca: '<path d="M6 8c-2 0-3-1.5-3-3 1.5 0 3 .5 4 1.5M18 8c2 0 3-1.5 3-3-1.5 0-3 .5-4 1.5"/><path d="M7 7h10l1 6c0 4-2.5 7-6 7s-6-3-6-7l1-6z"/><path d="M9.5 16.5h.01M14.5 16.5h.01M10 11h.01M14 11h.01"/>',
  dinheiro: '<circle cx="12" cy="12" r="9"/><path d="M15 9.2c-.6-1-1.7-1.5-3-1.5-1.7 0-3 .9-3 2.2 0 3 6 1.6 6 4.4 0 1.3-1.3 2.2-3 2.2-1.4 0-2.6-.6-3.1-1.6M12 6v1.7M12 16.5V18"/>',
  calendario: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M7.5 14h2M11 14h2M14.5 14h2M7.5 17.5h2M11 17.5h2"/>',
  escudo: '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
  pino: '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
  enxada: '<path d="M4 20 15 9M13 4l7 7-2.5 2.5-7-7L13 4z"/>',
  poco: '<path d="M5 10h14M6 10v10h12V10M4 6h16l-2 4H6L4 6zM12 6V3M10 14c0 1.1.9 2 2 2s2-.9 2-2-2-3-2-3-2 1.9-2 3z"/>',
  cisterna: '<path d="M4 9c0-1.7 3.6-3 8-3s8 1.3 8 3v9c0 1.7-3.6 3-8 3s-8-1.3-8-3V9z"/><path d="M4 9c0 1.7 3.6 3 8 3s8-1.3 8-3M9 3h6"/>',
  semente: '<path d="M12 21c-4-2-6-5.5-6-9.5C6 7 9 4 12 3c3 1 6 4 6 8.5 0 4-2 7.5-6 9.5z"/><path d="M12 7v11"/>',
  palma: '<ellipse cx="12" cy="16" rx="4" ry="5"/><ellipse cx="8" cy="8" rx="3" ry="4" transform="rotate(-20 8 8)"/><ellipse cx="16" cy="8" rx="3" ry="4" transform="rotate(20 16 8)"/>',
  seta: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  volta: '<path d="M19 12H5M11 6l-6 6 6 6"/>',
  relogio: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  lupa: '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
  grafico: '<path d="M4 20V10M10 20V4M16 20v-8M3 20h18"/>',
  faixas: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9.3h18M3 14.6h18"/>',
  areia: '<path d="M3 17c3-2 6-2 9 0s6 2 9 0M3 12c3-2 6-2 9 0s6 2 9 0"/><circle cx="7" cy="6" r=".6"/><circle cx="12" cy="5" r=".6"/><circle cx="17" cy="6.5" r=".6"/>',
  barro: '<path d="M3 15c2 0 2.5-2 4.5-2s2.5 2 4.5 2 2.5-2 4.5-2 2.5 2 4.5 2"/><path d="M5 19h14M8 9c0-2 2-4 4-6 2 2 4 4 4 6a4 4 0 0 1-8 0z"/>',
  nuvem: '<path d="M7 18a4.5 4.5 0 0 1 .6-8.96A5.5 5.5 0 0 1 18 10.5a3.75 3.75 0 0 1-.5 7.5H7z"/>',
  interrog: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17v.5"/>',
};
/** Ícone em SVG: ic("milho"), ic("gota", "g") (classes: "" 22px, "g" 34px, "gg" 48px). */
export const ic = (nome, tam = "") => `<svg class="ic ${tam}" viewBox="0 0 24 24" aria-hidden="true">${IC[nome] || IC.info}</svg>`;

/** Ícone por cultura (para blocos e listas). */
export const icCultura = (c) => {
  const s = String(c || "").toLowerCase();
  if (s.includes("milho") || s.includes("sorgo") || s.includes("milheto")) return "milho";
  if (s.includes("feij") || s.includes("caupi") || s.includes("amendoim") || s.includes("guandu") || s.includes("mucuna")) return "feijao";
  if (s.includes("mandioca")) return "mandioca";
  if (s.includes("palma") || s.includes("glir")) return "palma";
  if (s.includes("pousio")) return "vaca";
  return "broto";
};

/** Indicador no estilo do painel: { icone, rot, val, un, sub, selo } → cartão com número grande. */
export const ind = ({ icone = "info", rot = "", val = "—", un = "", sub = "", selo: s = "" }) =>
  `<div class="ind"><div class="ind-rot">${ic(icone)}<span>${esc(rot)}</span>${s}</div>
    <div class="ind-val">${val}${un ? `<small>${esc(un)}</small>` : ""}</div>${sub ? `<div class="ind-sub">${sub}</div>` : ""}</div>`;

/** Bloco escondido "ver como calculamos" (o detalhe técnico sai da frente). */
export const verMais = (html, titulo = "Ver como calculamos") => `<details class="ver-mais"><summary>${esc(titulo)}</summary>${html}</details>`;

/** Faixa de manchete: bola colorida com ícone + frase forte (como a do painel do JP). cor: verde | ambar | terra | azul. */
export const faixa = (icone, cor, frase) => `<div class="faixa"><span class="bola ${cor}">${ic(icone)}</span><p>${frase}</p></div>`;

/** Grade de 10 roças pintadas: k de 10 em cor (ex.: chance de quebra 0,6 → 6 vermelhas). */
export const dezRocas = (p, cor = "var(--terra)", rotulo = "") => {
  const k = Math.max(0, Math.min(10, Math.round((p ?? 0) * 10)));
  return `<div class="dez-rocas" role="img" aria-label="${k} em 10 ${esc(rotulo)}">${Array.from({ length: 10 }, (_, i) =>
    `<i style="background:${i < k ? cor : "rgba(255,255,255,.08)"}"></i>`).join("")}</div>`;
};
