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
