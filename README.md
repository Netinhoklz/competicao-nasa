# Field Shift — NASA Space Apps Challenge 2026

Estudo de dados e proposta para o desafio **"Field Shift: Adapting Farms with NASA Data"**: apoio à decisão de rotação de
culturas com dados da NASA. O produto é pensado para funcionar no mundo todo, com demonstração no Ceará e no Nordeste do Brasil.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `notebooks/estudo_estatistico_bases.ipynb` | Notebook executado: estudo estatístico de cada base (cobertura global, qualidade, estatística, sazonalidade, tendências, extremos e insights), relações entre bases, ideias de ML/DL e síntese |
| `notebooks/secoes/` | Fonte do notebook, uma seção por base, em formato percent (`# %%`). Montagem: `python scripts/montar_notebook.py --saida notebooks/estudo_estatistico_bases.ipynb --executar` |
| `scripts/` | Downloads (`baixar_*.py`), preparação (`preparar_*`, `derivar_*`, `consolidar_*`), utilitários (`comum.py`, `edl.py`) |
| `pesquisa/artigos_e_datasets.md` | Revisão de literatura: 73 artigos e 40 datasets |
| `proposta/` | Proposta para a competição (conselho de 10 especialistas): rascunho, versão final e ata |
| `conselho/analises/` | Análises feitas pelos especialistas durante o debate |
| `dados_resumo/derivados/` | Séries mensais tratadas (Ceará, Nordeste, AOIs) usadas para cruzar as bases |
| `interface-nordeste-jp/` | Página do agricultor para o Nordeste (mapa dos 1.794 municípios: El Niño, chuva × safra, solo). Abra `index.html`; regerar com `python conselho/analises/jp_nordeste_municipios.py` e `python interface-nordeste-jp/scripts/montar_pagina.py` |
| `dados_resumo/manifestos/` | `MANIFESTO.json` de cada base: fonte, URL, recorte, período e arquivos |

## MVP "Agro-Stress Test" (condado piloto nos EUA)

Condado piloto: **Saunders County, Nebraska (FIPS 31155)**. Parâmetros em `config/pilot_county.toml`.

| Pasta | Conteúdo |
|---|---|
| `config/` | Condado, grade mestre (EPSG:5070, 30 m), anos do CDL, camadas de solo, fonte dos talhões |
| `src/ingestion/` | ETL offline. `stac_and_soil.py`: talhões (CSB) × SSURGO × CDL 2008–2025 × terreno NASADEM |
| `src/features/`, `src/models/`, `src/api/` | Próximas etapas (estresse silencioso, LightGBM/SHAP, FastAPI) |
| `data/raw`, `data/interim`, `data/processed` | Fora do git; recriados pelo ETL |

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python -m src.ingestion.stac_and_soil              # ~4 min com cache frio + 3,7 GB do CSB
.venv/Scripts/python -m src.ingestion.stac_and_soil --talhoes grade   # sem o CSB (quadrículas de 402 m)
```

## Dados

Os dados brutos (~11 GB, mais 7 GB do CDL) **não estão no repositório** por causa do limite de tamanho do GitHub.
Eles ficam em `E:/campeonato-nasa/dados/<base>/` e podem ser recriados com os scripts `scripts/baixar_*.py`; os
manifestos dizem de onde veio cada arquivo.

- **Rotas abertas:** NASA POWER, Planetary Computer (IMERG V06, ERA5, Landsat, Sentinel-2, HLS, MODIS, NASADEM, CDL),
  GRACE (CSR/UT), FIRMS, GAEZ, FAOSTAT e Banco Mundial.
- **Exigem conta NASA Earthdata:** SMAP e VIIRS NDVI (via AppEEARS), GLDAS, NLDAS e IMERG V07 recente (via GES DISC,
  com o termo de uso aprovado). As credenciais ficam no `_netrc` do usuário e nunca entram no repositório.

O ambiente Python é o venv em `E:/campeonato-nasa/venv` (kernel Jupyter "Python (campeonato-nasa)").
