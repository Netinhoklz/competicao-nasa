# Interface inicial — Roça Certa (Vicente)

Página web para o pequeno e médio agricultor do Ceará: ele marca a roça no mapa e recebe os avisos em poucos
cartões visuais. As explicações de cada número ficam na página "Como eu funciono".

Abra `index.html` direto no navegador (arquivo único, com os dados embutidos; precisa de internet só para as fontes).

## Telas
- **Mapa**: toque no município (ou digite a cidade) e confirme.
- **Minha roça**: Inverno 2027 (ONI e anos parecidos), Quando plantar?, Seu ano na roça (calendário cultural
  proposto, de nov/2026 a out/2027), O que aguenta seca aqui?, Agora: entressafra, Como foi o inverno aqui.
- **Como eu funciono**: regras, números, fontes e limites de cada cartão.

## Estrutura
| Caminho | Conteúdo |
|---|---|
| `index.html` | Página final, autocontida |
| `fonte/pagina.html` | Modelo da página (HTML/CSS/JS) com o marcador `__DATA__` |
| `dados/dados_pagina.json` | Recorte dos dados dos 184 municípios usado pela página |
| `dados/ibge_malha_ceara_municipios.json` | Malha municipal do IBGE (API de malhas, qualidade mínima) |
| `scripts/extrair_dados.py` | Gera `dados_pagina.json` a partir de `conselho/analises/saidas/` e `dados_resumo/derivados/` |
| `scripts/montar_pagina.py` | Junta modelo + dados em `index.html` |
| `prototipo-celular/` | Primeiro protótipo (app de celular com máquina do tempo e mercado), mantido como referência |

## Regerar
```bash
python interface-inicial-vicente/scripts/extrair_dados.py . interface-inicial-vicente/dados/dados_pagina.json \
       interface-inicial-vicente/dados/ibge_malha_ceara_municipios.json   # precisa de pandas + pyarrow
python interface-inicial-vicente/scripts/montar_pagina.py
```

## Fontes dos dados
Chuva diária GPM IMERG V07 (0,1°) via NASA POWER, por município, 1998–set/2026; ONI (NOAA CPC);
IBGE Produção Agrícola Municipal; relevo NASA SRTM/NASADEM. Números da retroanálise de plantio vêm de
`conselho/analises/agronomo_regras_semeadura.py`.
