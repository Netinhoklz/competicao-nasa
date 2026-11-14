# Créditos do globo, do mapa e do painel (site final, `web/`)

Origem: João Pedro, branch `estudo-jp`, commit `29f81f6`, pasta `colegas/joao-pedro/site-nasa/` (Flask). No site final tudo
virou arquivo estático, sem Flask. O José junta esta lista no `CREDITOS.md` geral.

## Páginas, código e estilo

| Arquivo no site final | Origem | O que mudou |
|---|---|---|
| `index.html` | JP `templates/index.html` | Jinja (`url_for`) vira caminho relativo. three.js, MapLibre e fontes vêm de `vendor/` (antes, jsDelivr e Google Fonts). Os atalhos "Lençóis Maranhenses" e "Chapada Diamantina" viram os municípios Barreirinhas (MA) e Lençóis (BA), porque a busca agora só acha município. O cartão do mapa ganha o botão "Montar o plano do meu roçado →" (`roca.html#/<cod>/1`). No rodapé, o crédito "Busca: © OpenStreetMap" vira "Municípios: IBGE". |
| `painel.html` | JP `templates/painel.html` | Rota Flask `/painel/<cod>` vira `painel.html?cod=<IBGE>`; `?embutido=1` é o modo do painel ao lado do mapa. Fontes locais. Entra o botão "Montar o plano do meu roçado →" (`target="_top"`). Sai o SMAP da linha de fontes e entra a definição de El Niño forte. Sai o preload da malha (o modo embutido não usa). |
| `js/globo/espaco.js` | JP `static/js/espaco.js` | Texturas e `nordeste.json` por caminho relativo ao módulo (`import.meta.url`). |
| `js/globo/mapa.js` | JP `static/js/mapa.js` | `nordeste.json` relativo. O tipo `municipio` entra em `ASSENTAMENTO`: na chegada, o mapa centra no ponto do município e tira o zoom da caixa dele, entre 11 e 12,5. |
| `js/globo/principal.js` | JP `static/js/principal.js` | A busca deixa de usar `/api/geocode` (Nominatim pelo Flask) e passa a ser local (`busca.js`). O clique no globo deixa de usar `/api/reverse` e acha o município na malha local. Sai `unicos()`, que juntava os repetidos do Nominatim. Só um nome exato vai direto; os nomes parecidos abrem a lista para escolher. Aparece o botão do plano no cartão do mapa. |
| `js/globo/painel.js` | JP `static/js/painel.js` | O iframe passa a ser `painel.html?cod=<cod>&embutido=1`. A lista vem de `busca_municipios.json`, mais leve que `municipios_ne.json`. Entram o gancho `aoMudar(cod)` (botão do plano) e a classe `body.painel-pronto`, ligada quando o iframe avisa que desenhou (`postMessage`). |
| `js/globo/rocacerta.js` | JP `static/js/rocacerta.js` | Aba Inverno 2027: o El Niño dos 6 anos com ONI ≥ 0,5 dá lugar à definição única do plano (`dados/el_nino_uf.json`: ONI ≥ 1,5, quadras de 1998, 2010, 2016 e 2024). A manchete do estado sai em frequência ("em X de cada 10 municípios… o acaso daria 3 em 10"), com barras por ano forte. Sem o arquivo, a tela mostra "carregando dados". O rótulo do ONI vira "ago–out 2026"; "Normal da estação" vira "Chuva típica da estação · mediana 1998–2025". Sai a aba Alerta (o percentil fixo do SMAP de out/2026). As abas vazias ficam escondidas. Entram o botão do plano e o nome do município acima da manchete. |
| `js/globo/ovos.js` | JP `static/js/ovos.js` | Nenhuma mudança de código. |
| `js/globo/util.js` | JP `static/js/util.js` | Nenhuma mudança de código. |
| `js/globo/busca.js` | novo, a partir do `app.py` do JP | Busca local nos 1.794 municípios, sem acento na comparação e com estado opcional ("Quixadá, CE", "quixada ce", "Quixadá (CE)"), ou por coordenada ("-4.97, -39.01", regra `RE_COORD` do `app.py`). O ponto vira município pela malha do painel, com a projeção de `gerar_municipios.py`; na costa e nas ilhas, vale o município de centro mais próximo. |
| `css/globo/style.css` | JP `static/css/style.css` | Nenhuma mudança. |
| `css/globo/painel.css` | JP `static/css/painel.css` | Entra `.cartao-plano`, o botão do cartão do mapa, que some com `body.painel-pronto`. |
| `css/globo/rocacerta.css` | JP `static/css/rocacerta.css` | Entram `.faixa-texto`, `.faixa-lugar` e `.plano`. |

## Dados

| Arquivo | Origem | O que mudou |
|---|---|---|
| `dados/malha_ne.json` | JP `static/data/malha_ne.json` (malha IBGE projetada em SVG) | Cópia sem mudança |
| `dados/municipios_ne.json` | JP `static/data/municipios_ne.json` (IMERG, PAM, ONI) | Cópia sem mudança. O painel não lê mais `solo_pctl`/`solo_n` nem `enso` |
| `dados/nordeste.json` | JP `static/data/nordeste.json` (contorno IBGE) | Cópia sem mudança |
| `dados/busca_municipios.json` | novo, gerado por `ferramentas/gerar_busca_municipios.py` a partir de `municipios_ne.json` e `interface-nordeste-jp/dados/ibge_malha_ne_municipios.json` (JP) | `cod`, `nome`, `uf`, `lat`, `lon` e `bbox` dos 1.794 municípios. O ponto é o polo de inacessibilidade do maior polígono: o "centro" do JP (média dos vértices) cai fora do próprio município em 30 casos |
| `dados/el_nino_uf.json` | outro passo do site final (não é do JP) | Só é lido aqui |

## Imagens e bibliotecas de terceiros

| Arquivo | Origem | Observação |
|---|---|---|
| `texturas/*.webp`, `texturas/nordeste_mascara.png` | JP `static/textures/` (Terra: NASA Blue Marble e VIIRS Black Marble; Lua: Solar System Scope/LRO) | Só os WebP e a máscara do Nordeste, que o `espaco.js` usa. Os `.jpg` (7,7 MB) ficaram de fora porque nenhum código os usa |
| `vendor/three.module.min.js` | three.js 0.160.0 (MIT), copiado de `site-nasa-v2/vendor/` | O JP carregava `three@0.160.0` do jsDelivr. O sha256 é igual ao do jsDelivr |
| `vendor/maplibre-gl.js`, `vendor/maplibre-gl.css` | MapLibre GL JS 5.24.0 (BSD-3), copiado de `site-nasa-v2/vendor/` | Mesma versão do JP. O sha256 é igual ao do jsDelivr |
| `vendor/LICENSE-three.txt`, `vendor/LICENSE-maplibre.txt` | `site-nasa-v2/vendor/` | Licenças |
| `vendor/fontes/*.woff2`, `globo.css`, `painel.css` | Google Fonts, 14/11/2026, só os subconjuntos latin e latin-ext | Inter, IBM Plex Mono e Instrument Serif (globo); Fraunces e Plus Jakarta Sans (painel). OFL 1.1, texto em `vendor/fontes/OFL.txt` |

## Easter eggs mantidos (ovos.js e principal.js do JP)

- **Satélite em órbita baixa:** dá uma volta a cada 60 s no globo. Clicado, mostra um recado sobre GPM, SMAP ou MODIS.
- **Foguete de Alcântara (MA):** decola quando se digita "foguete" na busca ou com o código Konami (↑ ↑ ↓ ↓ ← → ← → B A).
  No console: `quadra.ovos.lancar()`.
- **Citações no canto inferior esquerdo:** Euclides da Cunha, Ariano Suassuna e Guimarães Rosa, trocando a cada 18 s.
- **Lua com eclipse:** a Lua passa atrás da Terra a cada volta.
