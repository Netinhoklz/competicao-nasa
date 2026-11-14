# Diálogo dos agentes: como deixar o mapa o mais bonito possível

Dois agentes conversam em rodadas sobre o mapa do site (a parte que aparece depois que a pessoa
escolhe um lugar e o globo vira mapa):

- **Agente Design**: diretor de arte cartográfico. Olha capturas reais do site, critica e propõe.
- **Agente Engenharia**: engenheiro de mapas. Responde a cada proposta (aceita, ajusta ou recusa,
  com o motivo técnico), implementa o que foi acordado e verifica com capturas.

Regras combinadas com o usuário:

- Visual **sóbrio, estilo NASA**: preto, branco e cinzas, uma só cor de destaque (`#9cc2ff`),
  Inter + IBM Plex Mono. Nada de neon, brilho (glow), partículas, texto em degradê ou fonte larga.
- O mais **intuitivo** possível.
- Só fontes de dados **sem chave de API**.
- Não quebrar: a troca globo 3D -> mapa (mesmo campo de visão, projeção de globo), o mergulho com
  a rodinha, a volta ao espaço afastando o zoom ou com Esc, e o parâmetro `?lugar=`.

---

## Rodada 1 — Agente Design

Fotos em `C:\Users\netinhoklz\AppData\Local\Temp\claude\88b277d27b184113\309288de-0ee5-4c92-a693-998c35e5936d\scratchpad\agentes\`.
Hoje: `design_r1_quixada_30s.png`, `design_r1_base_56s.png` (perto do chão, z13,4/pitch 74), `design_r1_base_76s.png`
(z11/pitch 78), `design_r1_araripe_32s.png`, `design_r1_iowa_42s.png`, `design_r1_troca_base_15.5s.png` (troca globo→mapa).
Protótipos das propostas (injetados por JS na página, sem editar o site): `design_r1_v3_quixada_36s.png`,
`design_r1_v3_quixada_58s.png`, `design_r1_v2_quixada_78s.png`, `design_r1_v3_quixada_80s.png`, `design_r1_v3_iowa_62s.png`,
`design_r1_v3_iowa_84s.png`. O script final está em `...\scratchpad\agentes\js\proposta3.js`.

### O que está feio ou confuso hoje

1. **Costura na imagem (o pior defeito).** O Esri World Imagery troca de fonte entre z11 e z12: até z11 é um mosaico
   verde saturado (Earthstar), de z12 em diante é Maxar (seco, marrom, com nuvens). Cor média dos ladrilhos sobre
   Quixadá: z10–11 = (60, 72, 27); z12–13 = (105, 100, 76). Com a câmera inclinada, perto carrega z12+ e longe z≤11,
   e uma linha reta corta a tela passando pelo marcador (`quixada_30s`, `base_76s`; em Iowa, canto superior esquerdo).
   Parece erro de carregamento.
2. **Nuvens do Maxar** sobre Quixadá viram manchas brancas com sombra preta coladas no relevo 3D (`base_56s`).
3. **Rótulos raster.** Deitam no chão, esticam, ficam espelhados com inclinação (`base_76s`), borram e crescem ao
   longe (`quixada_30s`, "Aratuba"), estão em inglês na troca ("BRAZIL", "Atlantic Ocean" em `troca_base_15.5s`), e os
   limites municipais brancos com contorno preto são o elemento mais forte da tela. O nome do lugar quase não aparece.
4. **Céu.** Abaixo de ~z12 (globo) o fundo é o espaço preto; acima de ~z12 o MapLibre passa a desenhar plano e acende um
   céu azul saturado (#5fa8ff → #071330) com névoa ciano que lava as serras (`base_56s`). Muda de repente ao aproximar
   e fica com cara de videogame.
5. **Câmera de chegada.** Pitch 58 em z11,5: a metade de cima é ladrilho de baixa resolução (e é onde está a costura).
   Araripe chega em z13,5 (o limite do bbox) e mostra só roçado, sem a chapada.
6. **Interface.** O selo "NASA SPACE APPS…" e a marca "QUADRA" ficam sem fundo sobre a imagem e somem em áreas claras.
   As dicas dos botões estão em inglês ("Zoom in", "Enable terrain"). O cartão tem 3 linhas fixas de instrução. O
   marcador parece um adesivo flutuando, não um ponto no chão. Em Iowa o marcador cobre o rótulo "Ames".
7. **Bug:** Esri com `maxzoom: 18`. No Ceará rural o z18 devolve o ladrilho cinza "Map data not yet available" (2,5 kB;
   testei Quixadá, zona rural e Araripe; Ames tem z18). Aproximando muito, aparece uma placa cinza.
8. O hillshade com sombra azulada `rgba(4,8,22,.55)` duplica as sombras que a foto já tem. Em z≥12 só suja.

### Propostas (em ordem de impacto)

**1. Imagem base sem costura e sem nuvens: Sentinel-2 cloudless + Maxar só no detalhe.**
- *Por quê:* some a linha que corta a tela e somem as nuvens. Em zoom baixo o oceano é azul-marinho, como o Blue
  Marble do globo 3D (o Esri é verde-azulado), então a troca globo→mapa fica mais contínua. Compare `quixada_30s`
  com `v3_quixada_36s` (mesma câmera).
- *Como* (URLs testadas: HTTP 200 e CORS `*`):
  ```js
  s2:      { type:'raster', tiles:['https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2024_3857/default/g/{z}/{y}/{x}.jpg'],
             tileSize:256, maxzoom:14, attribution:'Sentinel-2 cloudless 2024 © EOX (dados Copernicus)' },
  detalhe: { type:'raster', tiles:[ESRI_IMAGEM], tileSize:256, minzoom:12, maxzoom:17, attribution:'Detalhe © Esri, Maxar' },
  // camadas, de baixo para cima
  { id:'s2', type:'raster', source:'s2', paint:{ 'raster-fade-duration':250, 'raster-saturation':-0.08,
    'raster-contrast':-0.04, 'raster-brightness-min':0.05 } },
  { id:'detalhe', type:'raster', source:'detalhe', minzoom:13.5, paint:{ 'raster-fade-duration':250,
    'raster-opacity':['interpolate',['linear'],['zoom'],13.5,0,14.5,1] } },
  ```
  `minzoom:12` na fonte do detalhe faz o MapLibre usar só os ladrilhos Maxar, nunca os verdes de z≤11. `maxzoom:17`
  corrige a placa cinza. O Sentinel-2 tem 10 m/px e fica macio a partir de z14, por isso o Maxar assume ali
  (`v3_iowa_84s`: o mosaico de talhões aparece nítido).
- *Riscos que vi:* (a) o servidor da EOX responde em ~0,9 s por ladrilho contra ~0,4 s do Esri. Num teste, ladrilho
  que ainda não tinha chegado deixou um buraco preto com estrelas e um "bloco" de terreno (`troca_v3_17.5s`). Proponho
  uma rede de segurança: uma fonte `s2-base` com o mesmo URL e `maxzoom: 6` (poucos ladrilhos, já carregados na fase do
  globo) por baixo de tudo, e, se der, pré-aquecer a vista final no `preparar()`: `jumpTo(alvo)` escondido, esperar
  `idle` ou 2,5 s, depois `jumpTo(troca)`. (b) A licença do s2cloudless 2024 é CC BY-NC-SA 4.0: uso não comercial,
  serve para o desafio, mas a atribuição tem de ficar. (c) Testei e descartei o Esri "Clarity"
  (`clarity.maptiles.arcgis.com`): não tem nuvens, mas também tem costura (z13→z14) e puxa para o ciano (`prop_58s`).

**2. Rótulos vetoriais nítidos (OpenFreeMap, sem chave) no lugar do raster.**
- *Por quê:* ficam em pé e nítidos em qualquer inclinação, saem em português e dão nome ao que importa no sertão
  (cidades, açudes, serras, as pedras de Quixadá). Ver `v3_quixada_58s` e `v2_quixada_78s`.
- *Como:* remover a fonte e a camada `rotulos`. Adicionar
  `glyphs:'https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf'` e
  `ofm:{type:'vector', url:'https://tiles.openfreemap.org/planet'}`. A letra é Noto Sans (a única servida lá; é neutra e
  próxima da Inter). Use `nome = ['coalesce',['get','name:pt'],['get','name:latin'],['get','name']]` e o halo comum
  `'text-halo-color':'rgba(0,0,0,0.75)', 'text-halo-width':1.2, 'text-halo-blur':0.3`.
  - `cidades`: place, class city/town, minzoom 5, Noto Sans Regular, `#f2f4f7`.
    `text-size: ['interpolate',['linear'],['zoom'],5,['match',['get','class'],'city',13,11.5],12,['match',['get','class'],'city',18,15.5]]`
    (o interpolate tem de ficar por fora do match, senão o MapLibre recusa a camada).
    `text-padding 8`, `symbol-sort-key` city 0 / town 1, e `text-anchor:'top'`, `text-offset:[0,1.1]` para o
    nome ficar abaixo do ponto e não brigar com o marcador (caso de "Ames").
  - `vilas`: class village, minzoom 10.5, 12 px, `rgba(242,244,247,.85)`, `text-padding 10`.
  - `picos`: camada mountain_peak, minzoom 11.5, Noto Sans Italic 11.5, `rgba(242,244,247,.82)`, anchor top,
    offset [0, .4].
  - `aguas`: camada water_name, minzoom 10, Italic 12, `rgba(214,226,242,.92)`.
  - `estados`: class state, zoom 3.5–8.5, maiúsculas 11 px, `text-letter-spacing .2`, `rgba(242,244,247,.6)`.
  - `limites`: camada boundary, filtro `['<=',['coalesce',['get','admin_level'],99],4]` e
    `['!=',['coalesce',['get','maritime'],0],1]` (sem o coalesce o console reclama "found null"). Linha
    `rgba(255,255,255,.45)`, largura interpolada de 0.6 (z3) a 1.1 (z10), `line-dasharray [3,2]`. Sem limites municipais.

**3. Céu e horizonte sóbrios, contínuos com o espaço (e relevo mais discreto).**
- *Por quê:* o mesmo visual abaixo e acima de z12, sem o céu "acender" ao aproximar. É uma faixa fina cinza-azulada no
  horizonte, como numa foto da ISS, e as estrelas continuam visíveis atrás. Compare `base_56s` com `v2_quixada_78s`.
- *Como:*
  ```js
  sky: { 'sky-color':'rgba(0,0,0,0)', 'horizon-color':'#a9b8ca', 'fog-color':'#a9b8ca',
         'sky-horizon-blend':0.12, 'horizon-fog-blend':0.3, 'fog-ground-blend':0.94,
         'atmosphere-blend':['interpolate',['linear'],['zoom'],0,1,5,1,8,0] }
  ```
  No hillshade: `'hillshade-exaggeration':['interpolate',['linear'],['zoom'],4,0.35,9,0.18,12,0.05]`,
  `'hillshade-shadow-color':'rgba(0,0,0,0.45)'`, `'hillshade-highlight-color':'rgba(255,255,255,0.10)'`.

**4. Câmera de chegada que mostra o lugar inteiro, em resolução cheia.**
- *Por quê:* em z12,3 com pitch 50 a tela toda fica nítida, e a cidade e as serras aparecem juntas (`v3_quixada_58s`).
  No Araripe passa a aparecer a borda da chapada, não só a roça.
- *Como:* `ZOOM_PONTO` 11.5 → 12.3; pitch 58 → 50; bearing −18 → −15. Para bbox:
  `limitar(cam.zoom + 0.5, 3, 12.5)` (hoje é 13.5) e `pitch: zoom > 8 ? 50 : 30`. Opcional: `padding:{top:160}` no
  `flyTo`, para o marcador descer um pouco e sobrar paisagem atrás. O mergulho com a rodinha (`continuar`) fica como está.

**5. Marcador "no chão" e altitude da NASA no cartão.**
- *Por quê:* deitado no terreno, o anel vira uma elipse quando a câmera inclina e se lê como "este ponto do chão". A
  altitude é um dado NASA de verdade e explica o relevo que a pessoa vê.
- *Como:* `new maplibregl.Marker({ element, anchor:'center', pitchAlignment:'map', rotationAlignment:'map' })`, anel
  de 40 px, sem mudar as cores de hoje. No cartão, uma linha nova "Altitude 192 m · NASA SRTM" com
  `Math.round(mapa.queryTerrainElevation([lon, lat]) / EXAGERO)` depois do `idle`. Conferi no código do MapLibre 5.24:
  o valor já vem multiplicado pelo exagero, por isso a divisão. Tirar o parágrafo fixo de instruções do cartão e pôr
  uma linha só, no rodapé central: "Arraste para mover · Botão direito inclina · Esc volta ao espaço". Ela some na
  primeira interação ou depois de 8 s.

**6. Interface legível sobre a imagem e em português.**
- *Por quê:* hoje o topo some sobre áreas claras, e os botões falam inglês.
- *Como:* `body.no-mapa .topo { background: linear-gradient(to bottom, rgba(0,0,0,.55), rgba(0,0,0,0)); padding-bottom: 28px; }`
  (ou esconder o `.selo` no mapa). Opção `locale` do Map:
  `{'NavigationControl.ZoomIn':'Aproximar', 'NavigationControl.ZoomOut':'Afastar',
  'NavigationControl.ResetBearing':'Arraste para girar; clique para apontar o norte',
  'TerrainControl.Enable':'Ligar relevo 3D', 'TerrainControl.Disable':'Desligar relevo 3D',
  'AttributionControl.ToggleAttribution':'Créditos'}`.

### Testado e deixado de fora (por enquanto)
- **Vegetação NDVI da NASA** (`MODIS_Terra_L3_NDVI_16Day` no GIBS: responde, 99% de cobertura em z8, última data
  2026-10-16). É útil para agricultura, mas tem 250 m por pixel (cada pixel vira um quadrado de ~9 px em z11,5) e a
  paleta verde-limão do GIBS briga com o visual sóbrio. Proponho discutir na Rodada 2 como alternância opcional.
- **HLS diário** (`HLS_S30/L30` no GIBS): 0% de cobertura em Quixadá nas datas que testei. Não serve como "imagem recente".

### Pedido à Engenharia
Expor a instância em `window.__mapa` (pode ser só em desenvolvimento). Nesta rodada eu a peguei com um gancho em
`maplibregl.Map.prototype._render`. Lembrete: o Chrome headless (SwiftShader) provavelmente não tem filtro anisotrópico (não
confirmei), então o fundo inclinado deve sair mais borrado nas fotos do que numa GPU real.
O que **não** prototipei (só proposto): `name:latin` no coalesce, `text-anchor/offset` das cidades, a fonte `s2-base`,
o pré-aquecimento, o marcador deitado, a altitude, o rodapé de dicas, o degradê do topo e o `locale`.

---

## Rodada 1 — Agente Engenharia

Fotos em `C:\Users\netinhoklz\AppData\Local\Temp\claude\88b277d27b184113\309288de-0ee5-4c92-a693-998c35e5936d\scratchpad\agentes\`
(prefixo `eng_r1_`). Antes de mexer, guardei os originais e fotografei a troca com o código antigo (`eng_r1_antes_congela_24s`).
Para comparar a troca sem depender do relógio do headless, "congelei" o mapa no enquadramento da troca
(`window.quadra.mapa.chegar = () => {}` pelo console) e medi cores por região (mediana) na Terra 3D e no mapa.

Sobre o pedido de expor a instância: já existe, `window.quadra.mapa.mapa` (o `Map` do MapLibre) e `window.quadra.espaco`.
Não precisa de gancho em `_render`.

### Resposta ponto a ponto

**1. Sentinel-2 cloudless + Maxar só no detalhe — aceito com ajustes.**
- Implementado como proposto: `s2` (EOX, z≤14, tom `-0,08` de saturação) por baixo e `detalhe` Esri com fonte `minzoom 12` /
  `maxzoom 17` e camada surgindo entre z13,5 e z14,5. A costura z11/z12 sumiu, e com ela a placa cinza de z18 (conferi:
  em Quixadá e na zona rural, o z18 do Esri devolve 2.521 bytes, que é a placa; o z17 tem imagem).
- **Rede de segurança: `base`, com o mesmo URL do S2 e `maxzoom 4` (você propôs 6).** Medi o motivo. Na volta ao espaço, com
  a base em z6, o afastamento rápido pedia ladrilhos z6 que ninguém tinha carregado, e abriu um anel preto com estrelas
  (`eng_r1_volta_41s`, `eng_r1_volta_sonda_40.6s`; a sonda mostrou a base com só 2 ladrilhos prontos). O zoom da troca vai
  de ~z2,5 a z4,6, conforme a latitude e a altura da tela (em Ames, z3,47 com 900 px). Com `maxzoom 4`, **qualquer** vista a
  partir da troca usa exatamente os ladrilhos z4 que a base já carregou antes de o mapa aparecer. Resultado: nem na chegada
  nem na volta abre buraco (`eng_r1_volta2_40.6s`, `eng_r1_ames_volta_40.8s`: base com tudo pronto enquanto o S2 tinha
  43–57 ladrilhos carregando). O custo é a base ser mais macia, mas ela só aparece onde o S2 ainda não chegou
  (`eng_r1_ames_22s`). Sua foto `design_r1_troca_base_16.5s` (só 496 kB) sugere que o buraco já existia com o Esri.
- **Pré-aquecimento: aceito, com outra ordem.** Primeiro a vista da troca (é ela que tem de casar com a Terra 3D), depois um
  `jumpTo` escondido para a câmera final que dura **só enquanto a Terra 3D ainda viaja** (`Promise.race([idle, 2,5 s, voo])`),
  depois volta para a troca. Na primeira versão (pré-aquecer antes da troca), a troca atrasou 5 s no headless; agora leva
  de 7,3 a 8,0 s do início da viagem até o mapa (captura sozinha no headless), contra 7,2 s no código antigo. Não vale para o mergulho com a rodinha (`continuar`): o alvo ali é
  z6, e lá não há o que aquecer.
- **Oceano na troca: corrigi um ponto da premissa.** Medido no mesmo enquadramento (mediana, ΔE Lab contra a Terra 3D
  (13,57,101)): Esri (4,51,70) ΔE 17,9; S2 com o seu tom (33,43,62) ΔE 17,7. Ou seja, o S2 não estava mais perto; só troca
  o verde-azulado por cinza-marinho. O S2 cru é escuro demais (15,27,51), e o MapLibre não clareia acima do original. Simulei
  o shader de raster do MapLibre (que reproduziu a medida da captura) e escolhi saturação `+0,3` e contraste `-0,1` **só até
  z5**, voltando ao seu tom em z7. O oceano cai para ΔE 11 (medido: 32,47,74), e a terra quase não muda (17,6 → 19,1).
  Comparação lado a lado: `eng_r1_troca_comparacao.png`. O tamanho do globo continua igual (borda direita em ~1530 px nos dois).
- Licença: CC BY-NC-SA 4.0 está no crédito, com link. README atualizado.

**2. Rótulos vetoriais do OpenFreeMap — aceito com ajustes.**
- Tirei a fonte e a camada `rotulos` do Esri. Pus `glyphs` e `ofm` (Noto Sans), `nome = coalesce(name:pt, name:latin, name)`,
  o halo, `cidades` com nome abaixo do ponto (`text-anchor top`, offset 1,1; em Ames o "Ames" fica logo abaixo do marcador, sem
  ser coberto), `vilas`, `picos`, `estados` e `limites` (níveis ≤ 4, sem marítimos, tracejado), com os coalesce contra o
  "found null".
- **Limites e nomes de estado surgem entre z4,6 e z5,6** (opacidade por zoom, e `minzoom 4,6`). No zoom da troca o globo do
  mapa fica limpo como a Terra 3D, e a fonte vetorial nem é baixada ali (`eng_r1_troca_26s`, sem "BRAZIL"/"Atlantic Ocean").
- **Ordem das camadas:** `cidades` ficou por cima de `estados` (a camada de cima ganha a colisão; no seu protótipo os estados
  ganhavam das cidades).
- **Águas:** no OpenFreeMap, os açudes vêm como **LineString** (linha central do lago), não como ponto. Com posicionamento
  `point` o MapLibre 5.24 põe o nome na *primeira ponta* de cada pedaço de linha recortado pelo ladrilho (li o código), o que
  daria nome na ponta do lago e repetido na borda dos ladrilhos. Usei `line-center` com o texto em pé (`viewport`). Limite medido: na
  vista de chegada de Quixadá (z10,5) **nenhum** açude ganha nome. Com sobreposição liberada aparece 1, e com `point`, 0.
  Então é dado, não estilo: no ladrilho z10 o OpenMapTiles só nomeia açudes grandes. Em z11,5 aparece o Banabuiú. Testei
  `text-max-angle 180` e não mudou nada, então tirei.

**3. Céu e horizonte sóbrios, relevo discreto — aceito como proposto.** Céu transparente, faixa `#a9b8ca` fina, estrelas da
cena 3D atrás (`eng_r1_final_quixada_72s`, z11 com pitch 78). Sombreado com a curva por zoom e as cores que você passou.

**4. Câmera de chegada — aceito com ajuste.**
- `ZOOM_PONTO` 12,3, pitch 50 (30 se z ≤ 8), bearing −15, teto do bbox 12,5. Araripe chega em z12,34, Ames em z12,37.
- **Recuso o `padding:{top:160}` no `flyTo`:** no MapLibre o padding passado num `flyTo` fica gravado no transform. Depois disso
  o `getCenter()` e o enquadramento do `subir()` deixam de ser o centro da tela, e a volta para a Terra 3D (que assume o globo
  centralizado em `zoomEquivalente`) sai deslocada. Se você quiser o marcador mais baixo, dá para deslocar o *centro*
  geográfico alguns km na direção do bearing, sem padding. Proponha o quanto e eu faço.
- Observação: **Quixadá chega em z10,5**, não 12,3. O geocodificador devolve primeiro o **município** (bbox de ~60 km, centroide
  em −4,916, −39,029, uns 6 km ao norte da sede); a sede é o 2º resultado. Por isso o marcador fica fora da cidade e as
  "Pedras" (picos, `minzoom 11,5`) não aparecem na chegada. Isso é do `app.py`, fora do meu escopo nesta rodada.

**5. Marcador no chão e altitude — aceito com ajustes.**
- **Marcador:** com `pitchAlignment:'map'` o MapLibre aplica `rotateX(pitch)`. Em pitch 78 o anel ficava com 21% da altura e
  virava um risco de 8 px, quase invisível. Como o anel é simétrico, fiz o mesmo efeito achatando só a altura
  (`scaleY(cos pitch)`, com piso de 45%): em 50° fica a elipse do chão, em 78° continua legível. Anel de 40 px, mesmas cores.
- **Altitude:** `queryTerrainElevation / exagero` (conferido no 5.24: o valor já vem multiplicado), lida depois do `moveend`
  + `idle`. Só aparece com o relevo ligado e zoom ≥ 9 (no mergulho com a rodinha, z6, o modelo é grosso demais), e some se
  der negativa (mar). Ajuste na fonte: **nos EUA o AWS Terrain Tiles usa USGS 3DEP, não SRTM**, então o cartão diz
  "NASA SRTM" ou "USGS 3DEP" conforme o lugar. Medidas: Quixadá 185–200 m (varia com o nível do relevo já carregado),
  Araripe 756 m, Ames 281 m.
- **Dica de uso:** saiu o parágrafo do cartão. Entrou um rodapé com o mesmo desenho das dicas do início
  (`Arrastar move o mapa · Botão direito inclina e gira · Esc volta ao espaço`), no lugar do aviso da viagem (9vh). Ele some
  no primeiro toque ou rodinha no mapa, ou depois de 10 s, e fica escondido em tela de toque ou com menos de 640 px.

**6. Interface — aceito.** O degradê do topo o coordenador já fez (`.topo::before`). O `locale` em português ficou com
Aproximar, Afastar, bússola, Ligar/Desligar relevo 3D, Créditos, título do mapa e do marcador (conferido nos `title` dos botões).

### O que mais mudou (achado nos testes)
- **Créditos cobrindo a escala.** Com as fontes novas, a atribuição aberta passava por cima da escala no canto esquerdo (em
  z15,5 quebrava em duas linhas na largura toda). Encurtei os textos (a licença virou link) e pus
  `max-width: calc(100vw - 170px)` na atribuição: agora ela quebra a linha antes de chegar na escala.
- **Aviso novo no console**, em z15,5: "cannot calculate elevation if elevation maxzoom > source.maxzoom". A causa é o
  OpenFreeMap ir só até z14 e o relevo até z15. Baixei o relevo para `maxzoom 14`; não se perde nada, porque o z14 já tem
  ~9,5 m por pixel e o SRTM tem 30 m.
- Crédito do relevo: "AWS Terrain Tiles (NASA SRTM, USGS e outros)".

### Arquivos
- `static/js/mapa.js`: fontes e camadas novas, tom da troca, base de segurança, rótulos, céu, `locale`, `preparar()` com
  pré-aquecimento (`{ continuar, ate }`), `_alvo()`, `altitude()`, marcador achatado. A interface pública continua a mesma
  (`preparar`/`chegar`/`subir`/`aoZoom`, `zoomEquivalente`/`distEquivalente`).
- `static/js/principal.js`: passa `{ continuar, ate: voo }` ao `preparar`, preenche a altitude e liga/desliga a dica.
- `templates/index.html`: linha `#localAlt` no cartão; `#dicaMapa`; tirei `.cartao-dica`.
- `static/css/style.css` (só a parte do mapa): `.cartao-alt`, `.dica-mapa`, marcador de 40 px com `--achatar`, `max-width` da
  atribuição; tirei as regras de `.cartao-dica`.
- `README.md`: estrutura e "Fontes de dados e créditos".

### Verificação (todas sem erro novo no console)
O console só mostra o que já aparecia no código antigo: "calculateFogMatrix is not supported on globe projection" e os
avisos de desempenho do WebGL por software.
- Troca: `eng_r1_troca_12s` (Terra 3D) × `eng_r1_troca_26s` (mapa) × `eng_r1_antes_congela_24s` (Esri) →
  `eng_r1_troca_comparacao.png`.
- Quixadá: `eng_r1_final_quixada_12s`, `_32s`, `_45s`; horizonte em pitch 78: `eng_r1_final_quixada_72s`; base de segurança
  em plena chegada: `eng_r1_quixada_22s`; de perto, z15,5 com Maxar: `eng_r1_perto_70s`.
- Araripe: `eng_r1_final_araripe_22s`, `_32s`, `_45s`. Ames: `eng_r1_ames_22s`, `_32s`, `_45s`.
- Volta ao espaço: `eng_r1_volta_39s`…`_52s` (com o anel preto da base z6, já corrigido), `eng_r1_volta2_40.6s` e
  `eng_r1_ames_volta_40.8s` (sem buraco).
- Mergulho com a rodinha (caminho `continuar`): `eng_r1_rodinha_40s` (z6,1, pitch 35, sem altitude, como esperado).

### Para a Rodada 2
1. **Nuvens do Maxar a partir de z14,5** sobre Quixadá (`eng_r1_perto_70s`, nuvens e sombra sobre a cidade). O S2 sem
   nuvens fica macio depois de z14. É escolha de vocês: nitidez ou céu limpo.
2. **Geocodificador:** usar a sede (o 2º resultado, ou o `admin_centre`) em vez do centroide do município, e talvez um piso de
   zoom ~11,5 para bbox de município, para as pedras de Quixadá entrarem na chegada.
3. **Atmosfera na troca:** a borda azul da Terra 3D some no mapa (a atmosfera do MapLibre quase não aparece). Dá para alinhar a
   `light` do estilo com o sol da cena 3D; precisa de teste.
4. **Nomes de açude:** se quiserem mais nomes em z10–11, as opções são letra menor ou tirar o prefixo "Açude " quando
   existir (`slice`/`index-of` existem no 5.24). Hoje é limite do dado.
5. O SwiftShader não tem filtro anisotrópico garantido e carrega tudo devagar. Numa GPU real, o fundo inclinado e o tempo de
   chegada devem ser melhores do que nas fotos.

---

## Rodada 2 — Agente Design

Fotos em `C:\Users\netinhoklz\AppData\Local\Temp\claude\88b277d27b184113\309288de-0ee5-4c92-a693-998c35e5936d\scratchpad\agentes\`
(prefixo `design_r2_`). Os protótipos foram injetados por JS em `window.quadra.mapa.mapa`, sem editar o site:
`...\agentes\js\ne2.js` (propostas 1–4 e 6) e `...\agentes\js\municipio_ibge.js` (proposta 5).
Para fotografar a troca sem o voo, congelei o `chegar` como a Engenharia fez na rodada 1.

### O que melhorou
A rodada 1 funcionou. Quixadá chega com a sede no centro, as pedras com nome e a altitude no cartão, sem costura e sem
nuvem (`design_r2_quixada_45s`). Os rótulos estão nítidos e em português, e o céu ficou sóbrio.

### O que ainda está feio ou confuso
1. **O Nordeste some na troca.** No globo 3D a região tem o fio dourado, as divisas e as capitais acesas
   (`design_r2_quixada_9.5s`). Um segundo depois, no mapa, não sobra nada (`design_r2_quixada_11s`): a ideia mais forte do
   início desaparece exatamente quando o mapa aparece.
2. **Contorno duplo durante a troca.** No globo, o fio e a "cortina" ficam a `RAIO_LINHAS` 1,0095, ou seja, ~60 km acima do chão.
   Vista de cima, a cortina vira uma faixa dourada borrada na borda oeste e sul (`design_r2_v2_quixada_20s`). Durante os 0,9 s
   do cruzamento ela aparece deslocada da linha do chão, e o contorno sai duplicado (`design_r2_troca_contorno_lado_a_lado.png`:
   Terra 3D | cruzamento | mapa).
3. **A borda da atmosfera some** (pendência da Engenharia). O mapa usa a `light` padrão `[1.15, 210, 30]`, com o sol embaixo
   à esquerda, enquanto o sol da viagem está em cima à direita (`SOL_DESTINO`). Comparação:
   `design_r2_atmosfera_comparacao.png`.
4. **Petrolina chega errado.** A cidade fica colada na borda de baixo, em z≈9,4, e a tela mostra 80% de caatinga vazia ao
   norte (`design_r2_petrolina_45s`). A causa é que `_alvo()` centraliza o bbox do **município**, e a sede fica na ponta sul,
   na beira do São Francisco. O conserto do geocodificador escolheu o ponto da cidade, mas o bbox continua sendo o do município.
5. **Lençóis Maranhenses** (`design_r2_lencois_45s`):
   - o anel branco do marcador some na areia branca e só sobra o pontinho preto;
   - o detalhe do cartão traz o CEP ("65195-000");
   - aparecem cunhas pretas de borda reta na beira do campo de dunas. Parecem degraus do relevo (SRTM sobre areia, com
     exagero de 1,5). Fica para a Engenharia confirmar desligando o relevo.
6. **Créditos.** Abertos, ocupam ~1.300 px do rodapé por cima da imagem (`design_r2_quixada_45s`).
7. **Escala.** Uma vez a escala mostrou "NaN m" em z15,3 com pitch 55 (`design_r2_v2_quixada_62s`). Vi só depois de um
   `jumpTo` meu; vale conferir.

### Propostas (em ordem de impacto)

Cor única do destaque quente: o mesmo dourado do globo, `#ffcb7d`. O azul `#9cc2ff` continua na interface. Tudo é
**estático** no mapa, sem cintilar e sem pulso: o efeito animado é a assinatura do início, e animar no MapLibre obriga a
redesenhar o relevo a cada quadro, justamente onde a cena 3D já pausa para poupar a GPU.

**1. O Nordeste continua aceso no mapa: contorno com halo, afinando ao descer, e divisas douradas.**
- *Por quê:* dá continuidade ao globo; a pessoa vê que está "dentro" da região. Fotos: `design_r2_v3_46s` (z5,3) e
  `design_r2_ne_viagem_62s` (Ceará, z6,9).
- *Como:* fonte `ne` (GeoJSON montado de `static/data/nordeste.json`: o anel como LineString com `k:'contorno'` e as divisas
  com `k:'divisa'`). Abreviação: `z(...) = ['interpolate',['linear'],['zoom'],...]`.
  - `ne-halo` (line, filtro contorno): `line-color #ffcb7d`, `line-width z(3,5, 6,8, 9,6)`, `line-blur z(3,4, 6,6, 9,5)`,
    `line-opacity z(3,.2, 7,.16, 9.5,0)`. O halo largo e fraco só existe de longe.
  - `ne-contorno` (line): `line-width z(3,1.1, 6,1.6, 10,1.4)`, `line-opacity z(3,1, 9,.85, 13,.5)`, `line-join/cap round`.
    Em z3,4 fica igual ao fio do globo (1 px, opacidade cheia).
  - `ne-divisas` (line, filtro divisa): `line-width z(3,.7, 8,1, 12,1.2)`, `line-opacity z(3,.3, 6,.42, 10,.38, 13,.25)`.
  - No `limites` do OpenFreeMap, acrescentar `['!', ['within', regiaoNE]]` ao filtro: dentro do Nordeste valem as divisas
    douradas, fora continuam as brancas tracejadas. Ponha `ne-halo/ne-contorno/ne-divisas` **acima** de `limites` (antes de
    `estados`), para o dourado cobrir o tracejado branco nas divisas que a região divide com PA, TO, GO e MG. No meu protótipo
    eles ficaram abaixo; corrija isso.

**2. As 9 capitais como pontos de luz com nome.**
- *Por quê:* repete o colar de luzes do litoral que o globo mostra, e o nome em tom quente cria a hierarquia "capital > cidade"
  sem precisar de legenda (`design_r2_v3_46s`; na troca, `design_r2_v2_quixada_38s`). Na 1ª versão os pontos tinham 2 px e
  sumiam (`design_r2_dep_34s`); estes são os valores corrigidos.
- *Como:* fonte `ne-capitais` (os 9 pontos de `CAPITAIS_NE`; vale mover a lista para o `nordeste.json` e as duas cenas
  lerem do mesmo lugar). Três camadas no topo da pilha, para ganharem a colisão do nome branco do OpenFreeMap:
  - `ne-cap-halo` (circle, maxzoom 10.5): `#ffcb7d`, `circle-radius z(3,7, 6,11, 9,14)`, `circle-blur 1`,
    `circle-opacity z(3,.5, 9,.4, 10.5,0)`, `circle-pitch-alignment map`;
  - `ne-cap` (circle): `#fff3dc`, `circle-radius z(3,2.4, 6,3.4, 9,4.2)`, `circle-stroke 1 px rgba(255,203,125,.85)`,
    opacidade 1 até z9,5, depois some até z10,5;
  - `ne-cap-nome` (symbol, z4,6–10,5): Noto Sans Regular, `text-size z(4.6,12.5, 9,15)`, `#ffd9a0`, `text-anchor top`,
    `text-offset [0,.9]`, halo `rgba(0,0,0,.78)` 1,2 px, `text-opacity z(4.6,0, 5.2,1)`.
  - De z10,5 em diante (mais perto), a capital passa a ser só a cidade do OpenFreeMap, sem dourado.

**3. A região acende: escurecer o que está fora do Nordeste em zoom médio.**
- *Por quê:* o Nordeste "acende" sem brilho artificial; só o resto apaga um pouco (`design_r2_v3_46s`: Pará e Tocantins à
  esquerda e o oceano ficam mais escuros). Na troca o efeito fica em 0 (o globo 3D não escurece nada), cresce enquanto o
  mapa desce e some perto do chão.
- *Como:* fonte `ne-fora` = polígono do mundo `[[-180,-85],[180,-85],[180,85],[-180,85]]` com o anel do Nordeste como furo
  (inverter o sentido do anel se a área tiver o mesmo sinal). Camada `ne-fora` (fill, abaixo de `limites`): `fill-color #000`,
  `fill-antialias false`, `fill-opacity z(4.6,0, 5.8,.4, 8,.32, 9.5,0)`.

**4. Troca sem emenda: luz da atmosfera e sem contorno duplo.**
- *Atmosfera:* `light: { anchor:'viewport', position:[1.5, AZ, POL] }` no estilo. No MapLibre a `light` só mexe na
  atmosfera (não há `fill-extrusion`), e o `atmosphere-blend` some até z8.
  - Testei `[1.5,45,60]`: borda clara e larga à direita, como a da Terra 3D, mas leitosa e com uma franja lilás embaixo.
  - Testei `[1.5,57,37]`, que é a direção exata de `SOL_DESTINO`: borda fina e limpa, porém fraca.
  - Proponho `[1.5,50,48]` como meio-termo e aceito que a Engenharia ajuste olhando lado a lado. Minha foto desse valor
    (`design_r2_v3_27s`) caiu no meio do cruzamento e não serve de prova.
- *Contorno duplo:* quem resolve é o `espaco.js`, mas só na descida da viagem; o início não muda.
  - Nos últimos ~35% do `viajar()`, levar a opacidade de `matCortina` a 0: a cortina é um efeito para ser visto de lado e,
    de cima, vira borrão.
  - No instante em que `principal.js` põe `no-mapa`, esconder `grupoNE`.
  - O mapa já entra com o contorno, as divisas e as capitais da proposta 1/2, com a mesma cor e largura. O contorno só
    acompanha o fade de 0,9 s do mapa, sem aparecer duplicado.
  - Alternativa sem o pequeno "piscar": baixar o `grupoNE` para o raio 1,0 ao longo da descida (escala `1/RAIO_LINHAS`).

**5. Chegando numa cidade: sede no centro, contorno do município e marcador legível.**
- *Por quê:* responde "o que mostrar quando a pessoa já está dentro de um município". O limite do município aparece em
  dourado fino e o resto escurece levemente. É o mesmo gesto da região, uma escala abaixo, e mostra a área que o QUADRA
  vai analisar (`design_r2_ne_viagem_78s`, Quixadá em z9,6; `design_r2_v2_petrolina_64s`).
- *Câmera:* em `_alvo()`, quando o tipo é assentamento (city/town/village/district…), usar
  `center: [lugar.lon, lugar.lat]` e `zoom: limitar(cam.zoom + 0.5, 11, 12.5)`. O bbox serve só para o zoom. Parques,
  estados e regiões continuam centrados no bbox (3–12,5). Petrolina passa a chegar com a cidade e o rio no meio.
- *Dado oficial, sem chave:*
  - o Nominatim com `extratags=1` devolve `IBGE:GEOCODIGO` (Quixadá 2311306, Petrolina 2611101; conferi);
  - a malha do município vem de
    `https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{cod}?formato=application/vnd.geo%2Bjson&qualidade=intermediaria`
    (HTTP 200, CORS `*`, 3,6 kB para Quixadá);
  - é a mesma fonte (IBGE) do contorno do Nordeste. Sugiro o `app.py` devolver o `ibge` em `/api/geocode`, aproveitando o
    município que o front hoje descarta ao escolher a sede.
- *Camadas* (abaixo de `limites`), com fonte `mun` (anel como linha) e `mun-fora` (mundo com furo):
  - `mun-fora` (fill): `#000`, `fill-opacity z(8.5,0, 10,.22, 13,.15)`;
  - `mun-halo` (line): `#ffcb7d`, largura 6, blur 4, `line-opacity z(8.5,0, 10,.18, 13,.1)`;
  - `mun-linha` (line): `line-width z(9,1.2, 13,1.8)`, `line-opacity z(8.5,0, 10,.9, 14,.7)`.
  - Em Petrolina a linha ainda ficou fraca em z9,3; se for o caso, comece a rampa em z8.
- *Marcador:* no `.marcador i`, trocar o `box-shadow` por `0 0 0 1.5px rgba(0,0,0,.6), inset 0 0 0 1px rgba(0,0,0,.35)`,
  para o anel aparecer sobre areia, sal e telhado claro.
- *Cartão:* tirar o CEP do `detalhe` (regex `\b\d{5}-\d{3},?\s*`).
- *Opcional:* uma linha "Região imediata de Quixadá · Sertões Cearenses" vinda de
  `servicodados.ibge.gov.br/api/v1/localidades/municipios/{cod}` (testado). Dá contexto agrícola sem inventar nada.

**6. Pendências da Engenharia: nuvens de perto e créditos.**
- *Nuvens do Maxar a partir de z14,5:* o "Clarity" que eu tinha descartado na rodada 1 na verdade **redireciona (301) para
  o Esri World Imagery Wayback, versão 23001**. Proponho usar o Wayback direto no `detalhe`, para evitar o salto do redirect:
  - URL `https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/23001/{z}/{y}/{x}`, com
    `minzoom 14`, `maxzoom 17`, camada `minzoom 14`, `raster-opacity z(14,0, 15,1)`;
  - CORS `*` nas duas respostas;
  - de z14 a z17 tem imagem em Quixadá (cidade e zona leste), Petrolina, Araripe e Lençóis; o z18 dá 404, então `maxzoom 17`;
  - sem nuvens nas amostras em que o Maxar atual tem nuvem e sombra (`...\scratchpad\tiles\mont_clarity_perto.png`; no mapa,
    `design_r2_v2_quixada_62s`, Quixadá em z15,3 limpa);
  - a costura e o ciano que vi na rodada 1 eram de z13 para baixo. Usando só de z14 em diante, isso não aparece.
- *Créditos:* manter `compact` e, depois do `load`, tirar o atributo `open` e a classe `maplibregl-compact-show` do
  `.maplibregl-ctrl-attrib`. Fica só o "i" e os créditos continuam a um clique (prática padrão; a CC BY-NC-SA continua citada).

### Testado e deixado de fora
- Cintilar as capitais e o pulso na borda dentro do mapa: obrigaria a redesenhar o relevo a cada quadro. No mapa, a luz é estática.
- Polígono do município pelo Nominatim (`polygon_geojson`): funciona, mas o IBGE é a fonte oficial e a mesma do contorno do
  Nordeste.

---

## Rodada 2 — Agente Engenharia

Fotos em `C:\Users\netinhoklz\AppData\Local\Temp\claude\88b277d27b184113\309288de-0ee5-4c92-a693-998c35e5936d\scratchpad\agentes\`
(prefixo `eng_r2_`). A troca foi fotografada com o `chegar` congelado, como na rodada 1, e medida por pixel.

### Resposta ponto a ponto

**1. Nordeste aceso no mapa (contorno, halo, divisas) — aceito com ajustes.**
- Implementado no estilo, com dados do mesmo `static/data/nordeste.json` do globo 3D. O `carregado` do mapa só resolve
  com o Nordeste já desenhado, então a troca nunca acontece sem o fio. A ordem ficou como você pediu: `ne-fora` abaixo de
  `limites`, e `ne-halo/ne-divisas/ne-contorno` acima, antes de `estados`.
- **Valores na troca, para casar com o globo.**
  - As divisas do globo são fortes. Com 0,3 de opacidade, no mapa elas sumiam na troca. Ficaram 1 px e opacidade 0,8 em
    z4,6, descendo para os seus 0,42/0,38 a partir de z6.
  - O contorno tem 1 px em z4,6. O halo vale 0 na troca e sobe até 0,2 em z5,6.
  - Medido no mesmo enquadramento, a distância entre o dourado do globo e o do mapa tem **mediana de 0 px e p90 ≤ 2 px**
    nos dois sentidos. Não há contorno duplo nem salto (`eng_r2_troca_contorno_sobreposto.png`,
    `eng_r2_troca_lado_a_lado.png`: Terra 3D | cruzamento | mapa).
- **Contorno e divisas somem até z10.** O arquivo é simplificado a 0,02° (~2 km). Perto do chão, o fio passaria a
  quilômetros da divisa real e cortaria cidades no lugar errado. De z10 em diante entra o contorno do município (IBGE, fino).
  Pelo mesmo motivo, o `within` do filtro `limites` só vale abaixo de z10 (`['step', ['zoom'], …, 10, …]`), e acima disso
  voltam os limites do OpenFreeMap, que são precisos.

**2. As 9 capitais com nome — aceito com ajuste.**
- Camadas `ne-cap-halo`, `ne-cap` e `ne-cap-nome` no topo da pilha, com os seus valores. Somem de z10,5 em diante.
- A lista foi para o `nordeste.json` (chave `capitais`, mesma ordem e mesmos valores de `CAPITAIS_NE`). **Coordenador:** o
  `espaco.js` ainda tem a cópia própria; dá para ler do JSON quando você mexer nele.
- Na troca, os pontos têm 2 px sem aro e o halo fica em 0,12, para parecerem com os pontinhos do globo. Os seus valores
  valem a partir de z6.
- Com movimento contínuo, os 9 nomes dourados aparecem (`eng_r2_afastar_comparacao.png`). Numa foto com `jumpTo` de 5
  níveis de zoom, nomes e pontos não foram desenhados, embora o `queryRenderedFeatures` contasse 7 capitais colocadas.
  É coisa do salto de câmera no headless; quem usa o site nunca dá esse salto.

**3. Escurecer fora do Nordeste — aceito como proposto.** `ne-fora` com
`fill-opacity z(4,6, 0, 5,8, 0,4, 8, 0,32, 9,5, 0)`, zero na troca (`eng_r2_quixada_58s`, `eng_r2_lencois_92s`).

**4. Luz da atmosfera — aceito com `[1.5, 50, 48]`, depois de medir as três.**
- Perfil de brilho na borda direita do globo, na mesma linha (`eng_r2_atmosfera_comparacao.png`):
  - Terra 3D: pico de 186, com halo que continua por **60 px fora do disco**;
  - `[57,37]`: só uma faixa de 1 a 2 px (pico de 194) e o resto escuro;
  - `[45,60]`: clareia todo o oceano junto à borda (valores de 125 a 216), leitosa;
  - `[50,48]`: rampa de ~50 px até o pico de 216, a forma mais parecida.
  Ficou `[50,48]`.
- **O que não dá para casar:** a atmosfera do MapLibre só é desenhada **dentro** do disco. Fora dele a tela fica 0 (é onde o
  canvas é transparente para as estrelas). O halo externo da Terra 3D some na troca em qualquer valor de `light`.
- A parte do `espaco.js` (cortina e fio) o coordenador já fez.

**5. Sede no centro, contorno do município, marcador e cartão — aceito com ajustes.**
- **Câmera.** Para os tipos de sede, o centro é o ponto e o bbox só define o zoom, entre 11 e 12,5. Os demais lugares
  continuam centrados no bbox. O conjunto `ASSENTAMENTO` agora é exportado do `mapa.js` e importado pelo `principal.js`,
  uma fonte só. Resultados:
  - Petrolina chega em z11,0, com a cidade, o São Francisco e Juazeiro no meio (`eng_r2_petrolina_40s`);
  - Quixadá chega em z11,65 (`eng_r2_quixada_40s`).
- **`app.py`.** `extratags=1` no `/search` e a chave `ibge` em cada lugar (`None` para coordenada). O `lru_cache`, os erros e
  o resto do formato não mudaram (conferido nas três rotas).
  - No front, a sede escolhida por `unicos` herda o código do município do mesmo grupo.
  - O mapa usa os 7 primeiros dígitos, então um distrito (`231130605`) vira o município (`2311306`).
- **Contorno do município.** Camadas `mun-fora`, `mun-halo` e `mun-linha` com os seus valores.
  - `mun-halo` e `mun-linha` ficaram **acima** de `limites` (você pôs abaixo): onde a divisa do município coincide com a do
    estado, o dourado cobre o tracejado branco, como na proposta 1.
  - Malha `qualidade=intermediaria`, com `MultiPolygon` tratado. Se a pessoa já foi para outro lugar, a resposta atrasada
    é descartada.
  - Quixadá vem com 171 pontos, Petrolina com 191. No Lençóis não há código (é parque) e nada é desenhado.
- **Marcador:** o `box-shadow` duplo, como proposto. O anel aparece sobre a areia (`eng_r2_lencois_40s`).
- **CEP:** em vez da regex no meio do texto, tiro o **segmento** que é só CEP (`split(', ')`). Aplico no cartão e também na
  lista de sugestões. Testado em três endereços.
- *Opcional* "Região imediata…": fica para a rodada 3. É mais uma chamada e mais uma linha no cartão, e o texto precisa
  ser decidido.

**6. Detalhe sem nuvens (Wayback) e créditos — aceito, com duas mudanças e uma correção que não era opcional.**
- **Versão 49999 (2025-07-31) em vez de 23001 (2020-01-08).** Varri as 102 versões desde 2019 nos pontos de teste.
  - A mais recente (2026-10-29) tem nuvem e sombra no centro de Quixadá, a de 2026-06-30 tem nuvem no canto, e a
    **2025-07-31 é a mais recente limpa** em Quixadá, Petrolina, Araripe e Lençóis.
  - A 23001 é 5 anos mais velha e mais lavada (`...\scratchpad\eng\wayback_quixada.png`, `wayback_locais.png`).
  - Quixadá em z15,3 sai limpa (`eng_r2_perto_72s`).
- **Correção: o 404 do Wayback vem sem CORS.**
  - No mar aberto (e na costa em z17) o Wayback responde 404 **sem `Access-Control-Allow-Origin`**. O navegador acusa erro de
    CORS, o MapLibre recebe status 0 em vez de 404 e não silencia.
  - Aproximando ao largo de Fortaleza, o console encheu de erros (52 kB de log). A versão 23001 tem o mesmo problema.
  - Solução: um protocolo `wayback://` no `mapa.js`. Antes de pedir um ladrilho, ele consulta o `tilemap` do próprio serviço
    (tem CORS, um JSON por bloco de 32 × 32, guardado em cache) e só pede o que existe. Conferi o tilemap contra pedidos
    reais em terra, na costa e no mar: bate 100%.
  - Onde não há imagem, o protocolo devolve um erro com `status 404`, que o MapLibre 5.24 silencia (li o código) para seguir
    com o Sentinel-2 por baixo.
  - Resultado: zero erros no mar (`eng_r2_mar_72s`).
- **Créditos.** Ficam abertos na chegada e recolhem para o "i" 10 s depois, junto com a dica de uso. Dá tempo de serem
  vistos na primeira vez, e depois ficam a um clique. Entrou o crédito "Limites: IBGE".

### Bugs que você viu
- **Cunhas pretas nos Lençóis: não é o relevo.** Com `setTerrain(null)` elas continuam iguais (`eng_r2_lencois_58s` ×
  `_40s`), e aparecem nos ladrilhos crus do Sentinel-2 cloudless em z11 (`...\scratchpad\eng\s2_lencois_z11.png`). É do
  mosaico (provável sombra ou emenda de cenas na borda das dunas). Opções para a rodada 3:
  - deixar o Wayback entrar mais cedo só ali (abaixo de z14 ele tem costura);
  - aceitar, porque é a imagem.
- **Escala "NaN m":** não reproduzi em z15,3/pitch 55 (`eng_r2_perto_72s`: 200 m). Pela leitura do código, a escala usa
  `unproject` do centro e só atualiza no `move`. Logo depois de um `jumpTo` com relevo ainda carregando, o resultado pode
  ser NaN e ficar até o próximo movimento. Pus um conserto barato: no `idle`, se o texto tiver NaN, chamo
  `escala.setUnit('metric')`, que recalcula.
- **Um quadro preto (só estrelas) aos 14 s** numa captura, durante "em-viagem", antes da troca (`eng_r2_troca_14s`). Não se
  repetiu em quatro rodadas seguidas e não é o mapa (ainda sem `no-mapa`). Fica como aviso para o coordenador, no
  `espaco.js`.

### Arquivos
- `static/js/mapa.js`: fontes `ne`, `ne-fora`, `ne-capitais`, `mun`, `mun-fora`; dez camadas novas; `light`; detalhe Wayback
  com o protocolo `wayback://`; `_nordeste()`, `_municipio()`, `_alvo()` com a sede, créditos recolhidos e escala sem NaN;
  `ASSENTAMENTO` exportado. A interface pública continua a mesma.
- `static/js/principal.js`: importa `ASSENTAMENTO`; `unicos` herda o código IBGE; `semCep` no cartão e nas sugestões.
- `app.py`: `extratags=1` e a chave `ibge` (+3 linhas, −1).
- `static/data/nordeste.json`: chave `capitais` (o resto do arquivo ficou byte a byte igual).
- `static/css/style.css` (só o marcador): `box-shadow` do anel.
- `README.md`: estrutura e créditos (Wayback 2025-07-31, IBGE no mapa, créditos recolhidos).

### Verificação
Console: só os avisos que já existiam ("calculateFogMatrix…" e os de desempenho do WebGL por software).
- Troca: `eng_r2_troca_lado_a_lado.png`, `eng_r2_troca_contorno_sobreposto.png`, `eng_r2_atmosfera_comparacao.png`.
- Quixadá:
  - chegada: `eng_r2_final_quixada_45s`;
  - Nordeste em z5,6: `eng_r2_quixada_58s`;
  - fora da região, em z8,4: `eng_r2_quixada_76s`;
  - z15,3: `eng_r2_perto_72s`.
- Petrolina: `eng_r2_petrolina_40s`.
- Lençóis: `eng_r2_lencois_40s` (com relevo), `_58s` (sem relevo), `_92s` (região).
- Volta ao espaço: `eng_r2_volta_41s`…`_48s`. Mergulho com a rodinha: `eng_r2_rodinha_40s`. Mar em z14,6: `eng_r2_mar_72s`.
- Capitais com movimento contínuo: `eng_r2_afastar_comparacao.png`.

### Para a Rodada 3
1. Cunhas do Sentinel-2 nos Lençóis (decidir entre Wayback mais cedo só ali ou aceitar).
2. O halo externo da atmosfera some na troca. A troca já é contínua no resto, mas, se incomodar, a saída seria um anel em
   CSS ou canvas por trás do mapa, que some ao descer.
3. "Região imediata · Intermediária" do IBGE no cartão (opcional da proposta 5).
4. O `espaco.js` passar a ler as capitais do `nordeste.json`.
