/* QUADRA, site final: o site em inglês (padrão) ou português (pedido do José, 15/11/2026). Script clássico, o 1º do <head> das
   3 páginas (index, roca e painel). Uma camada de tradução no DOM, sem mexer na lógica dos passos: o site continua escrito em
   português e, em inglês, este arquivo troca o texto mostrado pelo de i18n/en.json:
     {"textos": {"Voltar ao espaço": "Back to space"}, "modelos": {"Sobra R$ {0} por ano": "R$ {0} left per year"}}
   Traduz os nós de texto (também no SVG), os atributos aria-label, title, placeholder, alt e o value de input[type=button|submit],
   e o <title>; pula script, style, code, textarea, noscript e o que tiver translate="no" ou data-i18n="nao". Um MutationObserver
   pega o que o JavaScript desenha depois (os passos, o painel, a busca).
   Língua: ?lang=en|pt na URL (na busca ou no hash, ex.: roca.html#/2311306/3?lang=pt; grava e vence) > a da página de fora (o
   painel no iframe do globo) > localStorage "quadra-lingua" > inglês.
   Nomes de lugar (município, estado, UF) nunca se traduzem (regra do José): i18n/lugares.json; ver "nomes de lugar" abaixo.
   ?i18n=coletar: a página fica em português e guarda em window.__i18nChaves (Map chave → contagem) tudo o que traduziria.
   Em inglês, window.__i18nVistas e window.__i18nFaltas (Set) guardam o que apareceu e o que ficou sem tradução.
   window.QUADRA_I18N = { lingua, coletando, t(texto), mudar(lingua) }. Guia: testes/i18n/LEIA-ME.md. */
(function () {
  "use strict";
  var CHAVE = "quadra-lingua", raiz = document.documentElement, url = location.search + location.hash;
  var param = function (nome) {
    var m = new RegExp("[?&]" + nome + "=([^&#]*)").exec(url);
    return m ? m[1].toLowerCase() : null;
  };
  var guardar = function (l) {
    try { localStorage.setItem(CHAVE, l); return true; } catch (_) { return false; } // janela privada, dados do site bloqueados
  };
  var fora = null; // a página de fora: o globo, com o painel do município num iframe
  try { if (window.parent !== window && window.parent.QUADRA_I18N) fora = window.parent.QUADRA_I18N; } catch (_) { /* outra origem */ }
  var pedida = param("lang"), lingua = pedida === "en" || pedida === "pt" ? pedida : null;
  var coletar = param("i18n") === "coletar" || !!(fora && fora.coletando);
  if (lingua) guardar(lingua);
  else if (fora) lingua = fora.lingua;
  else { try { lingua = localStorage.getItem(CHAVE); } catch (_) { lingua = null; } }
  if (lingua !== "pt" || coletar) lingua = coletar ? "pt" : "en";
  raiz.lang = lingua === "en" ? "en" : "pt-BR";

  // ------------------------------------------------------------------ chaves e modelos
  var DIC = null, INGLES = new Set(); // DIC: Map chave → inglês (os textos e os modelos juntos; um modelo tem {0}, {1}…)
  var chaves = coletar ? new Map() : null, vistas = new Set(), faltas = new Set();
  var LETRA = /\p{L}/u;
  // um número: 2.480 / 0,5 / -33 / −R$ / 15/11/2026 (a data é um só); "40 × 100" são dois. O colado numa letra fica (SMAP L4).
  var NUM = /(?<![\p{L}\p{N}.,])[-−+]?\d+(?:[.,]\d+)*(?:\/\d+)*/gu;
  var norm = function (s) { return s.replace(/\s+/g, " ").trim(); };

  // ------------------------------------------------------------------ nomes de lugar (regra do José: nunca se traduzem)
  // i18n/lugares.json (ferramentas/preparar_i18n_lugares.py): os 1.794 municípios do Nordeste, os 9 estados e as UFs. Um nome é
  // lugar quando é estado ou UF; é o município da página (roca.html#/<cod>, painel.html?cod=<cod>, o cartão do globo); vem colado
  // numa UF ("Serra Talhada-PE", "Oeiras (INMET/PI)", "Quixadá, CE"); ou é o texto inteiro ("Sobral"). O município que é também
  // palavra do site ("vocab": Barro, Areia, Baixio, Capim…, e as chaves do en.json) só vale como lugar nos 3 primeiros casos.
  // Dentro da frase o lugar vira marcador, como o número ("Em {0}, o milho quebra {1} em {2} anos"), e volta intacto; o texto
  // só de lugar (com número, sigla e unidade) fica como está e não entra na coleta nem na cobertura.
  var COD = new Map(), PRIMEIRA = new Map(), FIXOS = new Set(), VOCAB = new Set(), COLADO = /$^/;
  var PALAVRA = /\p{Lu}[\p{L}'’]*/gu, LETRA_NUM = /[\p{L}\p{N}]/u;
  var carregarLugares = function (j) {
    var por1 = function (nome) { // os nomes pela 1ª palavra, do maior para o menor
      var p = /^[\p{L}'’]+/u.exec(nome), l = p && (PRIMEIRA.get(p[0]) || []);
      if (l && l.indexOf(nome) < 0) { l.push(nome); PRIMEIRA.set(p[0], l); }
    };
    (j.m || []).forEach(function (m) { COD.set(m[0], m); por1(m[1]); });
    var ufs = Object.keys(j.uf || {}), est = ufs.map(function (u) { return j.uf[u]; });
    ufs.concat(est).forEach(function (n) { FIXOS.add(n); por1(n); });
    (j.vocab || []).forEach(function (n) { VOCAB.add(n); });
    PRIMEIRA.forEach(function (l) { l.sort(function (a, b) { return b.length - a.length; }); });
    COLADO = new RegExp("^\\s?[-–,/(·]\\s?(?:[A-Z]+/)?(?:" + ufs.concat(est).join("|") + ")(?![\\p{L}])", "u");
  };
  var contexto = function () { // o município da página
    var s = new Set(), m = /#\/(\d{7})/.exec(location.hash) || /[?&]cod=(\d{7})/.exec(location.search), c = m && COD.get(m[1]);
    var el = document.getElementById("localNome"), q = /[?&]lugar=([^&#]*)/.exec(location.search);
    if (c) s.add(c[1]);
    if (el && el.textContent) s.add(norm(el.textContent));
    if (q) { try { s.add(norm(decodeURIComponent(q[1].replace(/\+/g, " ")).split(",")[0])); } catch (_) { /* lugar mal escrito */ } }
    return s;
  };
  /** Os trechos [início, fim] de ch que são nome de lugar. */
  var lugaresEm = function (ch) {
    var r = [], ctx = null, m;
    if (!PRIMEIRA.size) return r;
    PALAVRA.lastIndex = 0;
    while ((m = PALAVRA.exec(ch))) {
      var i = m.index, l = i > 0 && LETRA_NUM.test(ch.charAt(i - 1)) ? null : PRIMEIRA.get(m[0]);
      for (var k = 0; l && k < l.length; k++) {
        var nome = l[k], fim = i + nome.length;
        if (ch.substr(i, nome.length) !== nome || LETRA_NUM.test(ch.charAt(fim))) continue;
        if (FIXOS.has(nome) || (ctx || (ctx = contexto())).has(nome) || COLADO.test(ch.slice(fim))
            || (fim - i === ch.length && !VOCAB.has(nome) && !(DIC && DIC.has(nome)))) {
          r.push([i, fim]);
          PALAVRA.lastIndex = fim;
        }
        break;
      }
    }
    return r;
  };
  var semLugar = function (ch) {
    var s = "", pos = 0;
    lugaresEm(ch).forEach(function (x) { s += ch.slice(pos, x[0]) + " "; pos = x[1]; });
    return s + ch.slice(pos);
  };
  /** A forma de modelo: cada número e cada nome de lugar vira {0}, {1}… na ordem; nums guarda o original de cada um. */
  var modelo = function (ch) {
    var marcas = lugaresEm(ch), m;
    NUM.lastIndex = 0;
    while ((m = NUM.exec(ch))) marcas.push([m.index, m.index + m[0].length]);
    if (!marcas.length) return null;
    marcas.sort(function (a, b) { return a[0] - b[0]; });
    var forma = "", nums = [], pos = 0;
    marcas.forEach(function (x) {
      if (x[0] < pos) return;
      forma += ch.slice(pos, x[0]) + "{" + nums.length + "}";
      nums.push(ch.slice(x[0], x[1]));
      pos = x[1];
    });
    return { forma: forma + ch.slice(pos), nums: nums };
  };
  // número brasileiro → inglês (2.480 → 2,480; 0,5 → 0.5; 1.234,5 → 1,234.5); data e fração (com /) ficam como estão
  var numEn = function (n) {
    if (n.indexOf("/") >= 0) return n;
    var s = /^[-−+]/.test(n) ? n.charAt(0) : "", c = n.slice(s.length);
    if (/^\d{1,3}(?:\.\d{3})+(?:,\d+)?$/.test(c)) c = c.replace(/\./g, "_").replace(",", ".").replace(/_/g, ",");
    else if (/^\d+,\d+$/.test(c)) c = c.replace(",", ".");
    return s + c;
  };
  // a forma antiga, só com os números como {0}: vale para as chaves do en.json feitas antes da regra dos lugares
  // ("raiz a R$ {0}/kg (comum no CE) ·"); a nova ("… (comum no {1}) ·") serve para todos os municípios e vem primeiro
  var soNumeros = function (ch) {
    var nums = [], forma = ch.replace(NUM, function (n) { nums.push(n); return "{" + (nums.length - 1) + "}"; });
    return nums.length ? { forma: forma, nums: nums } : null;
  };
  var preencher = function (en, nums) { return en.replace(/\{(\d+)\}/g, function (x, i) { return i < nums.length ? numEn(nums[i]) : x; }); };
  var buscar = function (ch) {
    if (DIC.has(ch)) return DIC.get(ch);
    var m = modelo(ch);
    if (m && DIC.has(m.forma)) return preencher(DIC.get(m.forma), m.nums);
    var n = m && soNumeros(ch);
    return n && n.forma !== m.forma && DIC.has(n.forma) ? preencher(DIC.get(n.forma), n.nums) : null;
  };
  var anotar = function (ch) {
    if (!LETRA.test(ch) || neutro(ch)) return; // só número, sigla, unidade e nome de lugar: não se traduz
    var m = modelo(ch);
    if (!lugaresEm(ch).length) chaves.set(ch, (chaves.get(ch) || 0) + 1); // com nome de lugar, só a forma de modelo
    if (m) chaves.set(m.forma, (chaves.get(m.forma) || 0) + 1);
  };
  // um texto "neutro" já vale em inglês: além de número e nome de lugar, só unidade (R$, m, ha, km…), sigla (até 5 maiúsculas
  // sem acento: NASA, SMAP, ZARC, IBGE) e letra solta (as partes A B C, os meses J F M…). MEDIDO, SUPOSIÇÃO, QUADRA e NASADEM não
  // são: vão no dicionário (igual em inglês, se for o caso). Sem tradução, o neutro fica como está, com o número no formato do inglês.
  var UNIDADES = /R\$|°C|m²|m³|\b(?:ha|km|kg|mm|cm|m|g|t|L|x)\b/g, SIGLA = /\b[A-Z][A-Z0-9]{0,4}\b/g;
  var neutro = function (ch) { return !LETRA.test(semLugar(ch).replace(NUM, "").replace(UNIDADES, "").replace(SIGLA, "")); };
  // a cobertura conta a forma de modelo (se tiver número) do que não é neutro
  var contar = function (ch, falta) {
    if (neutro(ch)) return;
    var m = modelo(ch), f = m ? m.forma : ch;
    vistas.add(f);
    if (falta) faltas.add(f);
  };
  var soNumero = function (ch) { var num = ch.replace(NUM, numEn); return num === ch ? null : num; };
  var um = function (ch) { // a tradução de um texto (ou de um pedaço), contando a cobertura; null = fica como está
    // o texto exato do dicionário vence, mesmo com nome de município (Areia, Barro, Baixio são palavras do site); onde a tela
    // mostra o município de verdade, o elemento tem translate="no"
    if (DIC.has(ch)) { contar(ch, false); return DIC.get(ch); }
    if (lugaresEm(ch).length && neutro(ch)) return soNumero(ch); // só lugar ("Quixadá", "Quixadá, CE"): fica como está
    var en = buscar(ch);
    if (en !== null) { contar(ch, false); return en; }
    if (INGLES.has(ch)) return null; // já é uma tradução, lida de volta do DOM pelo JavaScript (o "MEASURED" do selo)
    if (!neutro(ch)) { contar(ch, true); return null; }
    return soNumero(ch);
  };
  /** O texto em inglês com os espaços das pontas, ou null (sem tradução, ou fora do inglês). Um texto que não está inteiro no
   *  dicionário vai pedaço a pedaço pelos separadores, nesta ordem: " · " ("QUADRA · Quixadá (CE)", "medido · de onde vem"),
   *  "; " e ": " (as listas geradas, "(um dos 10 anos): Parte A: feijão-caupi; Baixio: milho", com combinações demais para
   *  ir inteiras no dicionário). Cada pedaço é procurado inteiro (e como modelo) antes de ser partido de novo. */
  var SEPS = [" · ", "; ", ": "];
  var porPedacos = function (ch, i) {
    var s = i;
    while (s < SEPS.length && ch.indexOf(SEPS[s]) <= 0) s++;
    if (s >= SEPS.length) return LETRA.test(ch) ? um(ch) : soNumero(ch);
    if (DIC.has(ch)) { contar(ch, false); return DIC.get(ch); }
    var en = buscar(ch);
    if (en !== null) { contar(ch, false); return en; }
    var mudou = false;
    var r = ch.split(SEPS[s]).map(function (p) {
      var q = porPedacos(p, s + 1);
      if (q !== null && q !== p) mudou = true;
      return q === null ? p : q;
    }).join(SEPS[s]);
    return mudou ? r : null;
  };
  var trocar = function (v) {
    var ch = norm(v);
    if (!ch) return null;
    var partes = ch.indexOf(" · ") > 0 ? ch.split(" · ") : null;
    if (chaves) { anotar(ch); if (partes) partes.forEach(anotar); return null; }
    if (!DIC) return null;
    if (!LETRA.test(ch)) { // só número ou símbolo: em inglês, só o formato do número (+2,46 → +2.46; 1.390 → 1,390)
      var num = /\d/.test(ch) ? v.replace(NUM, numEn) : v;
      return num === v ? null : num;
    }
    var en = porPedacos(ch, 0);
    return en === null ? null : /^\s*/.exec(v)[0] + en + /\s*$/.exec(v)[0];
  };
  /** Uma string solta, que não passa pelo DOM (o texto do WhatsApp): linha a linha. */
  var t = function (s) {
    if (typeof s !== "string" || (!DIC && !chaves)) return s;
    return s.split("\n").map(function (linha) { var r = trocar(linha); return r === null ? linha : r; }).join("\n");
  };

  // ------------------------------------------------------------------ o DOM
  var PULAR = "script,style,code,textarea,noscript,[translate=no],[data-i18n=nao]";
  var ATRIBUTOS = ["aria-label", "title", "placeholder", "alt", "value"];
  var nosFeitos = new WeakMap(), atrFeitos = new WeakMap(); // nó → { pt, en }: o en é o que o nó mostra desde a última passada
  var texto = function (no) {
    var v = no.nodeValue, r = nosFeitos.get(no);
    if (!v || (r && r.en === v) || !/\S/.test(v)) return; // o que nós mesmos escrevemos (ou já vimos) não volta
    var en = trocar(v);
    nosFeitos.set(no, { pt: v, en: en === null ? v : en });
    if (en !== null && en !== v) { no.nodeValue = en; avisar(); }
  };
  // depois de trocar textos, um aviso (1 por quadro): quem mede texto (as caixas atrás dos rótulos do desenho do Plano) mede de novo
  var aviso = 0;
  var avisar = function () {
    if (aviso) return;
    aviso = requestAnimationFrame(function () { aviso = 0; document.dispatchEvent(new CustomEvent("quadra:traduzido")); });
  };
  var atributo = function (el, nome) {
    var v = el.getAttribute(nome);
    if (!v || !/\S/.test(v) || (nome === "value" && !(el.tagName === "INPUT" && /^(button|submit|reset)$/i.test(el.type)))) return;
    var feitos = atrFeitos.get(el);
    if (!feitos) atrFeitos.set(el, (feitos = {}));
    if (feitos[nome] && feitos[nome].en === v) return;
    var en = trocar(v);
    feitos[nome] = { pt: v, en: en === null ? v : en };
    if (en !== null && en !== v) el.setAttribute(nome, en);
  };
  var elemento = function (el) {
    for (var i = 0; i < ATRIBUTOS.length; i++) if (el.hasAttribute(ATRIBUTOS[i])) atributo(el, ATRIBUTOS[i]);
  };
  var filtro = { acceptNode: function (n) { return n.nodeType === 1 && n.matches(PULAR) ? 2 : 1; } }; // REJECT pula o trecho todo
  var varrer = function (no) {
    if (no.nodeType === 3) return texto(no);
    if (no.nodeType !== 1) return;
    elemento(no);
    var w = document.createTreeWalker(no, 5 /* elementos e textos */, filtro), n;
    while ((n = w.nextNode())) { if (n.nodeType === 3) texto(n); else elemento(n); }
  };
  var pulado = function (no) {
    var el = no.nodeType === 1 ? no : no.parentElement;
    return !el || !!el.closest(PULAR);
  };
  var observador = new MutationObserver(function (lista) {
    for (var i = 0; i < lista.length; i++) {
      var m = lista[i];
      if (m.type === "childList") {
        for (var j = 0; j < m.addedNodes.length; j++) if (m.addedNodes[j].isConnected && !pulado(m.addedNodes[j])) varrer(m.addedNodes[j]);
      } else if (m.target.isConnected && !pulado(m.target)) {
        if (m.type === "characterData") texto(m.target); else atributo(m.target, m.attributeName);
      }
    }
  });
  var ligar = function () {
    varrer(raiz);
    observador.observe(raiz, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATRIBUTOS });
  };

  // ------------------------------------------------------------------ trocar de língua (recarrega mantendo o hash, sem o ?lang)
  var semLang = function (s) { return s.replace(/([?&])lang=[^&#]*&?/g, "$1").replace(/[?&]$/, ""); };
  var mudar = function (l) {
    l = l === "pt" ? "pt" : "en";
    var busca = semLang(location.search), hash = semLang(location.hash);
    if (!guardar(l)) busca += (busca ? "&" : "?") + "lang=" + l; // sem localStorage, a escolha vai na URL
    history.replaceState(history.state, "", location.pathname + busca + hash);
    location.reload();
  };
  // o seletor: [data-lingua="en|pt"] (a página inicial) e [data-lingua="trocar"] (o EN/PT do cabeçalho da jornada e do painel)
  var seletor = function () {
    var bs = document.querySelectorAll("[data-lingua]");
    Array.prototype.forEach.call(bs, function (b) {
      var alvo = b.getAttribute("data-lingua");
      if (alvo === "trocar") {
        var rot = lingua === "en" ? "Language: English. Switch to Portuguese" : "Idioma: português. Mudar para inglês";
        b.setAttribute("aria-label", rot);
        b.setAttribute("title", rot);
      } else b.setAttribute("aria-pressed", String(alvo === lingua));
      b.addEventListener("click", function () {
        var l = alvo === "trocar" ? (lingua === "en" ? "pt" : "en") : alvo;
        if (l !== lingua) mudar(l);
      });
    });
  };

  window.__i18nVistas = vistas;
  window.__i18nFaltas = faltas;
  if (chaves) window.__i18nChaves = chaves;
  // _forma: a forma de modelo de um texto, como o runtime a monta (para testes/ferramentas/i18n_converter_chaves.py)
  window.QUADRA_I18N = { lingua: lingua, coletando: coletar, t: t, mudar: mudar, _forma: function (s) { return modelo(norm(s)); } };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", seletor); else seletor();

  if (lingua !== "en" && !coletar) return;
  // inglês: a página fica escondida até o dicionário e os nomes de lugar chegarem (no máximo 1,5 s; depois aparece de qualquer
  // jeito). Na coleta a página fica em português e o dicionário só serve para saber que palavra do site não é lugar.
  var mostrar = function () { raiz.classList.remove("i18n-espera"); };
  if (!coletar) {
    var esconde = document.createElement("style");
    esconde.textContent = "html.i18n-espera,html.i18n-espera *{visibility:hidden!important}";
    (document.head || raiz).appendChild(esconde);
    raiz.classList.add("i18n-espera");
    setTimeout(mostrar, 1500);
  }
  var eu = document.currentScript && document.currentScript.src, base = eu ? eu.replace(/js\/i18n\.js(?:[?#].*)?$/, "") : "";
  var json = function (a, de_novo) { // recusado (internet fraca, servidor ocupado): tenta de novo uma vez, como o roca.js
    return fetch(base + a, { cache: "no-cache" }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () {
      return de_novo ? null : new Promise(function (ok) { setTimeout(ok, 300); }).then(function () { return json(a, true); });
    });
  };
  Promise.all([json("i18n/en.json"), json("i18n/lugares.json")]).then(function (r) {
    if (r[1]) carregarLugares(r[1]);
    if (r[0]) {
      DIC = new Map();
      [r[0].textos, r[0].modelos].forEach(function (o) {
        for (var k in o || {}) if (Object.prototype.hasOwnProperty.call(o, k) && typeof o[k] === "string") { DIC.set(norm(k), o[k]); INGLES.add(norm(o[k])); }
      });
    }
    if (DIC || coletar) ligar(); // sem dicionário: o site fica em português
  }).then(mostrar, mostrar);
})();
