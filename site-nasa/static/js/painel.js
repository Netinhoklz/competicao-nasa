// painel.js - painel lateral: depois do zoom o mapa encolhe para um cartao a esquerda (CSS em painel.css,
// classe body.com-lado) e o painel Roca Certa do municipio (/painel/<cod>?embutido=1, num iframe) abre a direita.
// O municipio vem do codigo IBGE da busca ou, sem ele, do municipio de centro mais proximo.

import { acharMunicipio } from './util.js';

let DADOS = null;         // baixado na primeira viagem: nao disputa banda com as texturas do globo
const dados = () => (DADOS ??= fetch('/static/data/municipios_ne.json').then((r) => (r.ok ? r.json() : null)).catch(() => null));

export class Painel {
  constructor(caixa) {
    this.caixa = caixa;
    this.vez = 0;
    this.cod = null;
  }

  /** Prepara o painel do municipio de `lugar`. Resolve true se o lugar e um municipio do Nordeste. */
  async mostrar(lugar) {
    const vez = ++this.vez;
    const d = await dados();
    if (vez !== this.vez) return false;
    const cod = d && acharMunicipio(d, lugar);
    if (!cod) { this.esconder(); return false; }
    if (cod !== this.cod) {
      this.cod = cod;
      this.caixa.innerHTML = `<iframe src="/painel/${cod}?embutido=1" title="Painel de ${d.m[cod][0]}"></iframe>`;
    }
    this.caixa.hidden = false;
    document.body.classList.add('com-lado');
    return true;
  }

  esconder() {
    this.vez++;
    this.caixa.hidden = true;
    document.body.classList.remove('com-lado');
  }
}
