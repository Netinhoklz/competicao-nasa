# Créditos do site final

Cada parte veio de um branch do repositório `Netinhoklz/competicao-nasa`. Os arquivos copiados levam no topo um comentário com a origem.

## João Pedro (JpLimags), branch `estudo-jp`, commit 29f81f6

O globo 3D, o mergulho até o Nordeste, o mapa dos 1.794 municípios e o painel "Roça Certa". A lista arquivo por arquivo e o que mudou
está em `web/CREDITOS_GLOBO.md`. Em resumo:
- os templates do Flask viraram HTML estático (`web/index.html`, `web/painel.html`), com caminhos relativos;
- three.js 0.160.0, MapLibre 5.24.0 e as fontes ficaram em `web/vendor/` (licenças junto);
- a busca virou local nos 1.794 municípios (`web/js/globo/busca.js`, `web/dados/busca_municipios.json`);
- o painel ganhou o botão "Montar o plano do meu roçado" e passou a usar a definição única de El Niño (`web/dados/el_nino_uf.json`);
- a série de chuva do painel foi alinhada com a do núcleo (`ferramentas/alinhar_painel_jp.py`), para as duas telas darem o mesmo número;
- a aba Alerta (percentil fixo do SMAP de out/2026) saiu, e as abas vazias ficaram escondidas;
- os easter eggs ficaram (`web/js/globo/ovos.js`).

## Vicente Lima, branch `estudo-vicente`, commit 18fd0e3

- **A ideia da distribuição em faixas** (PercolaCampo: percolação de pragas e doenças no roçado). No passo "Como plantar", as partes
  A/B/C viram faixas intercaladas, e a conectividade da gramínea é calculada sobre o desenho (`web/js/passos/plantio/desenho.js`).
  O limiar 0,593 entra só como régua. O R_eff, o "% de plantas protegidas" e as constantes do motor dele não entram, porque não estão
  nos artigos da pasta dele (ver `analise/vicente.md`).
- **O simulador PercolaCampo v3**, como modelo teórico ilustrativo, em `web/modulos/percolacampo/index.html` (faixa de aviso no topo;
  o subtítulo "Dados NASA" virou "Modelo teórico", porque o simulador não lê dado da NASA).
- **As palavras da pergunta do solo** ("seca rápido / segura a umidade / encharca"), de `interface-inicial-vicente`.

## José (Netinhoklz), branch `estudo-jose`

- **O núcleo** (`nucleo/motor.py`), cópia de `protótipo/motor.py` (commit e7a23b5) com as mudanças do site final listadas no cabeçalho:
  GAEZ v4 + ZARC 2026/27, NASA POWER e análogos, catálogo de 147 cartões, El Niño por município (IMERG), SMAP L4, plano A/B/C +
  baixio + bordas e calendário de plantio e colheita.
- **O financeiro e a projeção:** saem do notebook `notebooks/estudo_financeiro` (PAM, CONAB, IPCA) e dos scripts em `ferramentas/`.
- **O servidor, a jornada** (`web/roca.html`, `web/js/roca.js`, `web/js/passos/`) **e o estilo** (`web/css/quadra.css`, com os tokens
  do painel do João Pedro).

## Dados

NASA (POWER, GPM IMERG, SMAP L4), NOAA/CPC (ONI), FAO/IIASA GAEZ v4, MAPA ZARC 2026/27, IBGE (PAM, Censo Agro 2017, malha municipal),
CONAB (custos de produção), OpenStreetMap e OpenFreeMap (mapa), EOX Sentinel-2 cloudless e Esri Wayback (imagem do mapa).

## Uso de IA

O código, as análises e os textos foram feitos com ajuda de IA (Claude), como as regras do Space Apps pedem que se declare.
