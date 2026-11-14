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
| `app.py` | rotas `/`, `/api/geocode?q=` (texto ou coordenadas) e `/api/reverse?lat=&lon=` |
| `templates/index.html` | página única |
| `static/css/style.css` | visual (sóbrio: preto, branco e cinzas, Inter + IBM Plex Mono) |
| `static/js/espaco.js` | cena 3D (Three.js): Terra dia/noite, nuvens, atmosfera, estrelas, mergulho e viagem |
| `static/js/mapa.js` | mapa (MapLibre GL, projeção de globo): imagem Sentinel-2 + detalhe Maxar, rótulos vetoriais em português, relevo 3D, céu, marcador, altitude |
| `static/js/principal.js` | liga tudo: busca, viagem globo → mapa e volta |
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
- Mapa, detalhe ao aproximar (surge entre z13,5 e z14,5; só ladrilhos z12–z17): Esri World Imagery
  (© Esri, Maxar, Earthstar Geographics), com atribuição.
- Mapa, rótulos e limites: [OpenFreeMap](https://openfreemap.org) (sem chave), esquema
  © OpenMapTiles, dados © colaboradores do OpenStreetMap (ODbL). Fonte das letras: Noto Sans,
  servida pelo próprio OpenFreeMap.
- Relevo 3D e altitude do cartão: AWS Terrain Tiles (Mapzen/Tilezen). No Brasil e na maior parte
  do mundo vem do NASA SRTM; nos EUA, do USGS 3DEP.
- Todos os créditos do mapa aparecem no botão de créditos (ⓘ) no canto inferior direito; o
  MapLibre mostra só os das camadas visíveis naquele zoom.
- Busca de lugares: Nominatim / © colaboradores do OpenStreetMap (uso leve, sem autocompletar).

## Ferramenta de captura

```bash
python ferramentas/captura.py saidas/quixada --url "http://127.0.0.1:5000/?lugar=Quixadá" --fotos 5 20
python ferramentas/captura.py saidas/volta --url "http://127.0.0.1:5000/?lugar=Fortaleza" \
    --fotos 20 28 --acao "22:document.getElementById('voltar').click()"
```

Requer `websocket-client`. O WebGL roda por software no modo headless, então tudo fica mais lento
que num navegador comum (o mapa pode levar uns 20 s para carregar).
