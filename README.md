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
| `dados_resumo/manifestos/` | `MANIFESTO.json` de cada base: fonte, URL, recorte, período e arquivos |

## Dados

Os dados brutos (~11 GB, mais 7 GB do CDL) **não estão no repositório** por causa do limite de tamanho do GitHub.
Eles ficam em `E:/campeonato-nasa/dados/<base>/` e podem ser recriados com os scripts `scripts/baixar_*.py`; os
manifestos dizem de onde veio cada arquivo.

- **Rotas abertas:** NASA POWER, Planetary Computer (IMERG V06, ERA5, Landsat, Sentinel-2, HLS, MODIS, NASADEM, CDL),
  GRACE (CSR/UT), FIRMS, GAEZ, FAOSTAT e Banco Mundial.
- **Exigem conta NASA Earthdata:** SMAP e VIIRS NDVI (via AppEEARS), GLDAS, NLDAS e IMERG V07 recente (via GES DISC,
  com o termo de uso aprovado). As credenciais ficam no `_netrc` do usuário e nunca entram no repositório.

O ambiente Python é o venv em `E:/campeonato-nasa/venv` (kernel Jupyter "Python (campeonato-nasa)").
