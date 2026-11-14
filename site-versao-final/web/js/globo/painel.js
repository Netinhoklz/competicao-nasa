// Origem: João Pedro (branch estudo-jp, 29f81f6), site-nasa/static/js/painel.js; adaptado para o site final: o iframe
// abre painel.html?cod=<IBGE>&embutido=1 (era /painel/<cod> do Flask); a lista vem de dados/busca_municipios.json
// (busca.js, mais leve que municipios_ne.json); aoMudar(cod) avisa a página do município escolhido (botão do plano)
// e a classe body.painel-pronto entra quando o painel do iframe avisa que desenhou (postMessage 'painel-pronto').
// painel.js - painel lateral: depois do zoom o mapa encolhe para um cartao a esquerda (CSS em painel.css,
// classe body.com-lado) e o painel Roca Certa do municipio (num iframe) abre a direita.
// O municipio vem do codigo IBGE da busca ou, sem ele, do municipio de centro mais proximo.

import { acharMunicipio } from './util.js';
import { carregar } from './busca.js';

export class Painel {
  constructor(caixa) {
    this.caixa = caixa;
    this.vez = 0;
    this.cod = null;
    this.aoMudar = null;   // fn(cod | null): municipio do painel (ou nenhum)
    window.addEventListener('message', (e) => {
      if (e.origin === location.origin && e.data?.quadra === 'painel-pronto' && e.data.cod === this.cod) {
        document.body.classList.add('painel-pronto');
      }
    });
  }

  /** Prepara o painel do municipio de `lugar`. Resolve true se o lugar e um municipio do Nordeste. */
  async mostrar(lugar) {
    const vez = ++this.vez;
    const d = await carregar();
    if (vez !== this.vez) return false;
    const cod = d && acharMunicipio(d, lugar);
    if (!cod) { this.esconder(); return false; }
    if (cod !== this.cod) {
      this.cod = cod;
      document.body.classList.remove('painel-pronto');
      this.caixa.innerHTML = `<iframe src="painel.html?cod=${cod}&embutido=1" title="Painel de ${d.m[cod][0]}"></iframe>`;
    }
    this.caixa.hidden = false;
    document.body.classList.add('com-lado');
    this.aoMudar?.(cod);
    return true;
  }

  esconder() {
    this.vez++;
    this.caixa.hidden = true;
    document.body.classList.remove('com-lado');
    this.aoMudar?.(null);
  }
}
