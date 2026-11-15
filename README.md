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
| `proposta/` | Proposta para a competição (conselho de 10 agentes de IA, ver "AI use"): rascunho, versão final e ata |
| `conselho/analises/` | Análises feitas pelos agentes de IA durante o debate |
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

## AI use (uso de IA)

The NASA Space Apps rules ask each team to say where and how AI tools were used. In this project:

- **Tool.** Claude (Anthropic), mostly through Claude Code, used by the three team members.
- **Code.** The site in `site-versao-final/` (HTML, CSS and JavaScript), the Python engine (`site-versao-final/nucleo/motor.py`),
  the server, the data-preparation scripts (`scripts/`, `site-versao-final/ferramentas/`), the notebooks and the tests were
  written with Claude under the team's direction. The team chose what to build, tested the site and decided what stayed.
- **Data produced with AI.**
  - `site-versao-final/web/i18n/en.json`: the English text of the site, translated from the Portuguese source.
  - `pesquisa/catalogo_rotacoes.json` and `pesquisa/catalogo_rotacoes_comprovadas.md`: the 147 evidence cards were extracted
    from the papers by AI agents, and the numbers were checked against each paper's text or source data (`conselho/analises/`).
  - Both JSON files carry this statement in a metadata field (`_meta.ai_disclosure` and `uso_de_ia`).
- **Text.** The analyses, the proposal and the literature notes in `proposta/`, `conselho/`, `pesquisa/` and
  `site-versao-final/analise/` were drafted with Claude. Where these documents say "council", "specialists" or "agents"
  ("conselho", "especialistas", "agentes"), they mean panels of AI agents, not human experts.
- **Images.** No AI image generator was used. The icons, the drawings of the plot and the satellites on the globe are vector
  and 3D shapes drawn by the site's code. The Earth and Moon textures are real imagery: NASA Blue Marble and VIIRS Black
  Marble (GIBS), and Solar System Scope (CC BY 4.0).
- **Audio and video.** None is AI-generated. The demo was made by the team, without AI.
- **Not AI-generated.** The measured data: NASA (POWER, GPM IMERG, SMAP), NOAA, FAO GAEZ, MAPA ZARC, IBGE and CONAB.
- **NASA branding.** The project uses no NASA logo, flag or mission identifier. NASA is named only as a data source.

In the site, this statement lives in the code, not on screen: each page carries it in a `<meta name="ai-disclosure">` tag,
next to a comment that points to this section.

**Em português:** o código, a tradução para o inglês, os desenhos feitos por código, o resumo dos artigos e os textos de análise
foram feitos com ajuda de IA (Claude, da Anthropic), sob a direção da equipe. Os dados medidos e as imagens de satélite são
reais, não gerados por IA. Nenhuma imagem, áudio ou vídeo foi gerado por IA, e o projeto não usa marca da NASA.
