# site-nasa — interface do QUADRA

Site em Flask do QUADRA (NASA Space Apps Challenge 2026, desafio *Field Shift*). A página inicial
mostra a Terra em 3D; a pessoa escolhe um lugar e o planeta gira e desce até lá, virando um mapa
interativo com imagem de satélite e relevo.

## Como rodar

```bash
cd site-nasa
pip install -r requirements.txt   # flask e requests
python app.py                     # abre em http://127.0.0.1:5000
```

Precisa de internet: a busca usa o Nominatim (OpenStreetMap) e o mapa baixa ladrilhos de imagem e
relevo. As texturas do globo 3D ficam em `static/textures/` e funcionam sem rede.

Link direto para um lugar: `http://127.0.0.1:5000/?lugar=Quixadá, Ceará`.

## Painel Roça Certa (`/painel/<código IBGE>`)

Ao chegar a um município do Nordeste, o mapa fica à esquerda e o painel do município abre à direita
(`/painel/<código>?embutido=1` num iframe; o MapLibre ganha folga para o lugar ficar no meio da parte livre).
O mesmo painel abre em tela cheia em `/painel/<código IBGE de 7 dígitos>` (sem código: Quixadá), sem 3D: abas
**Inverno 2027**, **Plantar** e **Alerta** com dado real; **Veranico**, **Preparo da terra** e **Entressafra** são espaços
tracejados com conteúdo a definir. Mapa dos 1.794 municípios (malha IBGE), busca por nome, zoom no estado e
modo claro/escuro.

**Inverno 2027** mostra o sinal do El Niño **por estado**, não por município. Ele traz a % dos municípios do estado com
a estação no terço mais seco, em cada ano de El Niño (ONI de jul–set ≥ 0,5: 1998, 2003, 2005, 2010, 2016, 2024), e
quando a previsão firma (fevereiro).

O motivo: o teste deixando um ano de fora (`conselho/analises/jp_analogos_atlantico.py`) mostrou que contar os "anos
parecidos" do município não acerta mais que o acaso em novembro (AUC ≈ 0,5). O El Niño desloca o ano no estado inteiro.
Embasamento e referências: `pesquisa/embasamento_painel_nordeste.md`.

Regerar os dados: `python conselho/analises/jp_nordeste_municipios.py`, `python conselho/analises/jp_analogos_atlantico.py` (só o teste) e depois
`python site-nasa/ferramentas/gerar_municipios.py` (escreve `static/data/municipios_ne.json` e `malha_ne.json`).

## Easter eggs (`static/js/ovos.js`)

- Um satélite dá a volta na Terra a cada 48 s; clicar nele mostra um recado sobre GPM, SMAP e MODIS.
- Digitar **foguete** na busca (ou o código Konami: ↑ ↑ ↓ ↓ ← → ← → B A) lança um foguete de Alcântara (MA).
- No console: `quadra.ovos.lancar()`.

## Só o Nordeste

O globo só desce em lugares do Nordeste: busca, coordenada, clique no globo, atalho, endereço `?lugar=` e o
mergulho com a rodinha passam por `dentroDoNordeste` (`static/js/util.js`), que usa o contorno do IBGE
(`static/data/nordeste.json`) com folga de 0,12° para cidades da costa e aceita Fernando de Noronha e o Atol das Rocas.

## Testes

```bash
pip install -r requirements-dev.txt
python -m pytest            # na raiz do repositório
```

- `site-nasa/testes/test_app.py`: rotas, validação da busca, compressão e arquivos dos templates;
- `site-nasa/testes/test_dados.py`: integridade de `municipios_ne.json`, `malha_ne.json` e do gerador;
- `site-nasa/testes/test_js.py`: regras de `util.js` e o painel de ponta a ponta no Chrome sem janela
  (pula se não houver Chrome ou Edge; aponte outro com `CHROME=<caminho>`);
- `testes/test_analise_nordeste.py`: funções da análise por estado e por município.

## Otimizações (14/11/2026)

- Globo abre com texturas WebP leves (~1,7 MB, antes ~6,8 MB em JPG 8K); no computador, as 8K e as nuvens 4K
  chegam em segundo plano 5 s depois da abertura (`_melhorarTexturas` em `espaco.js`). As JPG originais continuam
  na pasta.
- Respostas de texto saem com gzip (`app.py`): os dois JSON do painel caem de ~870 KB para ~300 KB.
- Os dados do município só são baixados na primeira viagem, sem disputar banda com as texturas.
- `rascunhos/`: o painel cartográfico de teste (números simulados) e a gaveta de decisão com a rota
  `/api/decisao`, guardados fora do site; os problemas encontrados estão no topo de `rascunhos/decisao_api.py`.

## Como se usa

| Gesto | O que acontece |
|---|---|
| Digitar um lugar ou `lat, lon` e apertar Enter | o planeta gira até lá e vira mapa |
| Arrastar o planeta | gira, com inércia |
| Rolar a rodinha (ou pinça no celular) | aproxima no ponto sob o cursor; ao completar, entra no mapa |
| Clicar no planeta | desce direto naquele ponto |
| `/` | leva o cursor para a busca |
| No mapa: afastar o zoom até ver o planeta, ou `Esc` | volta ao espaço |

## Estrutura

| Arquivo | Papel |
|---|---|
| `app.py` | rotas `/`, `/api/geocode?q=` (texto ou coordenadas; devolve também o código IBGE) e `/api/reverse?lat=&lon=` |
| `templates/index.html` | página única |
| `static/css/style.css` | visual (sóbrio: preto, branco e cinzas, Inter + IBM Plex Mono) |
| `static/js/espaco.js` | cena 3D (Three.js): Terra dia/noite, nuvens, atmosfera, estrelas, mergulho e viagem |
| `static/js/mapa.js` | mapa (MapLibre GL, projeção de globo): imagem Sentinel-2 + detalhe Maxar, rótulos vetoriais em português, relevo 3D, céu, marcador, altitude, Nordeste aceso (contorno, divisas, capitais) e limite do município |
| `static/js/principal.js` | liga tudo: busca, viagem globo → mapa e volta |
| `templates/painel.html` + `static/js/rocacerta.js` + `static/css/rocacerta.css` | painel Roça Certa do município (abas, indicadores, mapa IBGE, gráficos) |
| `static/data/malha_ne.json` | malha IBGE dos municípios e estados do Nordeste, já em caminhos SVG simplificados |
| `static/js/painel.js` + `static/css/painel.css` | painel lateral do mapa (iframe do painel Roça Certa) para municípios do Nordeste; estilos dos easter eggs |
| `static/js/ovos.js` | easter eggs: satélite em órbita e foguete de Alcântara |
| `static/data/municipios_ne.json` | números por município (1.794); regerar com `python site-nasa/ferramentas/gerar_municipios.py` depois de `python conselho/analises/jp_nordeste_municipios.py` |
| `static/textures/` | texturas da Terra |
| `ferramentas/captura.py` | fotografa o site em tempo real (Chrome headless via DevTools) e mostra erros do console |
| `docs/dialogo_agentes.md` | conversa entre os dois agentes que refinaram o mapa |

A troca do globo 3D para o mapa é feita no mesmo enquadramento: as duas câmeras usam o mesmo campo
de visão (36,87°) e `zoomEquivalente()` em `mapa.js` converte a distância da câmera 3D no zoom do
MapLibre. Fora do globo o mapa é transparente, então as estrelas continuam aparecendo.

## Fontes de dados e créditos

- Globo 3D: NASA Blue Marble Next Generation e VIIRS Black Marble, baixados do NASA GIBS
  (domínio público; 8K no computador, 4K no celular); máscara de oceano e relevo de
  `mrdoob/three.js` (MIT).
- Nuvens (4K) e Lua: [Solar System Scope](https://www.solarsystemscope.com/textures/), CC BY 4.0
  (feitas a partir de imagens da NASA; a Lua a partir do LRO).
- Contorno do Nordeste e divisas dos estados (fio de luz do globo, `static/data/nordeste.json` e
  `static/textures/nordeste_mascara.png`): IBGE, API de malhas v3, simplificado a 0,02 grau.
- Citações do canto inferior esquerdo: Euclides da Cunha (*Os Sertões*), Ariano Suassuna e
  João Guimarães Rosa (*Grande Sertão: Veredas*).
- Mapa, imagem base (até z14): [Sentinel-2 cloudless 2024](https://s2maps.eu) © EOX IT Services
  GmbH, com dados Copernicus Sentinel modificados. Licença **CC BY-NC-SA 4.0** (uso não comercial,
  serve para o desafio; a atribuição tem de ficar visível).
- Mapa, detalhe ao aproximar (surge entre z14 e z15; ladrilhos z14–z17): Esri World Imagery
  **Wayback**, versão de 2025-07-31 (© Esri, Maxar), com atribuição. A versão atual do World Imagery
  tem nuvem e sombra sobre Quixadá; esta é a mais recente sem nuvem nos lugares de demonstração.
- Mapa, Nordeste e município: malhas do **IBGE** (API de malhas v3, dados abertos). O contorno da
  região, as divisas e as capitais ficam em `static/data/nordeste.json` (o mesmo arquivo do globo 3D);
  o limite do município é baixado na hora pelo código IBGE que o Nominatim devolve.
- Mapa, rótulos e limites: [OpenFreeMap](https://openfreemap.org) (sem chave), esquema
  © OpenMapTiles, dados © colaboradores do OpenStreetMap (ODbL). Fonte das letras: Noto Sans,
  servida pelo próprio OpenFreeMap.
- Relevo 3D e altitude do cartão: AWS Terrain Tiles (Mapzen/Tilezen). No Brasil e na maior parte
  do mundo vem do NASA SRTM; nos EUA, do USGS 3DEP.
- Todos os créditos do mapa aparecem abertos na chegada e, depois de 10 s, ficam no botão de
  créditos (ⓘ) no canto inferior direito; o MapLibre mostra só os das camadas visíveis naquele zoom.
- Busca de lugares: Nominatim / © colaboradores do OpenStreetMap (uso leve, sem autocompletar).

## Ferramenta de captura

```bash
python ferramentas/captura.py saidas/quixada --url "http://127.0.0.1:5000/?lugar=Quixadá" --fotos 5 20
python ferramentas/captura.py saidas/volta --url "http://127.0.0.1:5000/?lugar=Fortaleza" \
    --fotos 20 28 --acao "22:document.getElementById('voltar').click()"
```

Requer `websocket-client`. O WebGL roda por software no modo headless, então tudo fica mais lento
que num navegador comum (o mapa pode levar uns 20 s para carregar).
