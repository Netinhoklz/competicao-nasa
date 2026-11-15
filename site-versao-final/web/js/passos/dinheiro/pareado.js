// QUADRA, passo 4 "Quanto rende": a conta de calculo.js (sem mudar) para o plano escolhido no Plano, na MESMA base pareada de
// extras/ideal.js (as mesmas séries e os mesmos anos para hoje, o melhorado e os 4 ideais). Os R$ grandes do passo vêm de
// ideal.comparar3 (uma fonte só); daqui saem só os detalhes que precisam dos lançamentos (o caixa mês a mês, "a colheita paga o
// gasto?", os El Niños, os 28 anos). Rodada 2, correção Y (15/11): usa a base (baseComum) e os lançamentos (itensPlano) do próprio
// ideal.js, que agora os exporta, em vez de cópias: a mandioca que já está no chão, as partes desencontradas da mandioca sozinha e a
// conta parcial (uma série faltando, ex.: a mandioca em Caicó) ficam iguais nos dois lugares. teste_dinheiro.mjs (do C3) confere.
import { baseComum, itensPlano } from "../../extras/ideal.js";
import { seriesDe } from "../../extras/hoje_ideal.js";

/** A base comum: { ok, falta, okH, itH, nivel, mult, preco, series, base } (base = m de calculo.montar com as séries e anos comuns). */
export function basePareada(r, resp = {}, ef = {}) {
  const X = baseComum(r, resp, ef);
  return { ...X, ok: !!X.base };
}

/** O m de calculo.js do plano (itens do plano, s0 = o jeito de hoje) na base comum, pronto para C.calcular / C.replay;
 *  T, a e b são as áreas do próprio plano (sem as perenes que ficam fora do giro). null = sem conta (motivo em X.falta).
 *  Série que falta aqui (conta parcial, como em ideal.contaRs): o custo e a colheita dela ficam fora. */
export function montagem(X, r, ef, plano) {
  if (!X?.ok || !plano?.faixas?.length) return null;
  if (plano.ha_giro === 0 && (plano.fora_do_giro || []).length) return null;
  const mp = itensPlano(r, ef, plano);
  const precisa = [...seriesDe(mp.itens)];
  if (!precisa.length) return null;
  const faltam = precisa.filter((s) => !X.series.has(s));
  const itens = faltam.length ? mp.itens.map((its) => its.filter((i) => !faltam.includes(i.serie || i.custo))) : mp.itens;
  if (![...seriesDe(itens)].length) return null;
  return { ...X.base, itens, s0: X.okH ? X.itH0 : [[], [], []], semHoje: !X.okH, parcial: faltam,
    T: mp.T, a: mp.a, b: mp.b, temBaixio: mp.temBaixio, baixioNaoSei: mp.baixioNaoSei, semRs: mp.semRs || [] };
}
