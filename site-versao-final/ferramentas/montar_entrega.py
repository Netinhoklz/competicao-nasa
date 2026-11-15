"""Monta o pacote de entrega do QUADRA: uma pasta que roda sozinha em outra máquina, sem o E: e sem o resto do repositório.

Uso:  E:/campeonato-nasa/venv/Scripts/python.exe -X utf8 site-versao-final/ferramentas/montar_entrega.py [destino]
      (padrão: E:/campeonato-nasa/entrega/QUADRA; só copia e sobrescreve, não apaga nada)

O que entra (o mínimo para rodar e analisar):
  site-versao-final/           o site, o núcleo, os dados do site, os testes e as análises (sem __pycache__ nem .bak)
  scripts/                     os 3 módulos que o núcleo importa (comum, analogos_climaticos_artigos, gaez_zarc_municipio)
  pesquisa/                    o catálogo de rotações (JSON que o núcleo lê e o .md para quem analisa)
  dados/                       só os arquivos que o núcleo lê ao rodar (~70 MB dos ~11 GB do E:/campeonato-nasa/dados)
  app.py                       a partida (python app.py), cópia do app.py da raiz do repositório
  requirements.txt, README.md  a documentação: como instalar, dar a partida, como funciona e o que fazer se algo falhar

O que não entra e por quê:
  - os rasters do GAEZ (2,3 GB): o cache do GAEZ vai aquecido com o ponto interno dos 1.794 municípios (o site só pede por
    município); fora deles o núcleo responde "sem camada" (motor.aptidao);
  - a série diária do SMAP (584 MB): vai a janela de 30 dias já calculada (motor._prepara_smap usa o cache quando a fonte falta).
O scripts/comum.py acha <pacote>/dados sozinho (a raiz vira o pacote quando a pasta dados/ existe ao lado de scripts/).
"""
import json
import math
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
PROJ = SITE.parent
DEST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("E:/campeonato-nasa/entrega/QUADRA")

sys.path.insert(0, str(SITE / "nucleo"))
import motor  # noqa: E402  (com os dados do E:: é daqui que saem os pontos dos municípios e a amostragem do GAEZ)

DADOS = motor.DADOS
ARQUIVOS = [
    "analogos_artigos/assinaturas.csv",
    "analogos_aprofundado/catalogo_lugares_assinaturas.csv", "analogos_aprofundado/catalogo_cartao_lugar.csv",
    "analogos_aprofundado/ne_mun_assinaturas.csv", "analogos_aprofundado/onset_ne_mun.csv",
    "analogos_aprofundado/regime_chuva_ne_mun.csv",
    f"gaez_zarc/nordeste_{motor.SAFRA}.csv",
    "el_nino_2026/resumo.json", "el_nino_2026/estado_atual_uf.csv", "el_nino_2026/eventos.csv",
    "ibge_nordeste/malha_ne_municipio.geojson", "ibge_nordeste/localidades_municipios_ne.json",
    "referencia/ne_50m_land.zip",
    f"complementares/zarc_ne/tabua_risco_ne_{motor.SAFRA}.csv",
    "complementares/zarc_plurianual_ce/tabua_plurianual_ce.csv", "complementares/zarc_perenes_ne/tabua_perenes_ne.csv",
    "prototipo/smap_janela_30d.nc", "prototipo/cache_power_v2.json",
]
MODULOS = ["comum.py", "analogos_climaticos_artigos.py", "gaez_zarc_municipio.py"]
PESQUISA = ["catalogo_rotacoes.json", "catalogo_rotacoes_comprovadas.md"]

REQUISITOS = """# QUADRA: o que o servidor precisa (testado com Python 3.13 no Windows)
numpy==2.5.4
pandas==3.1.1
geopandas==1.2.0
shapely==2.2.0
pyproj==3.8.0
pyogrio==0.13.0
xarray==2026.9.0
netCDF4
rasterio==1.5.2
requests==2.34.2
"""

LEIAME = """# QUADRA: delivery package (pacote de entrega)

NASA Space Apps Challenge 2026, challenge "Field Shift: Adapting Farms with NASA Data".
QUADRA is a partner for the smallholder farmer of Brazil's semi-arid Northeast: it improves what the farmer plants today and
recommends the ideal crop rotation for that land, based on NASA data and on published science.

This folder has only what is needed to run the site and to analyse it. The full repository (studies, notebooks, proposal and
download scripts) is at https://github.com/Netinhoklz/competicao-nasa, branch `estudo-jose`.

## How to start

You need Python 3.13 (the version we tested) and an internet connection for the map tiles. In a terminal opened in this folder:

```
python -m venv venv
venv\\Scripts\\activate            (Windows; on macOS or Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

`app.py` is the start: it checks the packages and starts the server. Loading the data takes a few seconds; when the line
`QUADRA (site final) em http://localhost:8090` appears, open that address in the browser. Ctrl+C stops the server.
To use another port: `python app.py 8091`.

- `http://localhost:8090` is the home page: the globe and the search among the 1,794 municipalities of the Northeast.
- `http://localhost:8090/roca.html#/2311306/2` opens the farmer's journey directly in Quixadá (CE).
- `http://localhost:8090/painel.html?cod=2311306` opens the municipality panel: rain, El Niño, soil and trends.
- The site opens in English. The switch to Portuguese is on the home page and at the top of the other pages.

## How it works

```
browser  (site-versao-final/web: HTML, CSS and JavaScript)
   |  the plan, the income and the report are computed in the browser from the farmer's answers,
   |  which stay in the page address: there is no login and no database
   v
server   (site-versao-final/servidor.py: static files and two routes)
   v
engine   (site-versao-final/nucleo/motor.py)
   reads dados/ (NASA POWER, GPM IMERG, SMAP, ZARC, GAEZ, IBGE) and pesquisa/catalogo_rotacoes.json
```

The journey has four steps after the municipality is chosen: Your field (six questions), The plan (the plot in strips, today's
way against the ideal), Earnings and Report (printable).

The two routes of the server:

| Route | Answer |
|---|---|
| `/api/local?cod=<IBGE code>` | everything the engine knows about the municipality: crops that fit, planting windows, climate, El Niño, soil moisture, rotation plan and evidence. Optional: `textura=1-3`, `ad=11-16`, `ad_baixio=11-16`, `maniva=tem\\|nao\\|plantada`, `baixio=0\\|1`, `hoje=YYYY-MM-DD` |
| `/api/municipios` | the boundaries of the 1,794 municipalities (GeoJSON) |

## If something goes wrong

- **"Missing Python packages":** run `pip install -r requirements.txt` with the virtual environment active.
- **The port is busy:** start on another one, for example `python app.py 8091`.
- **The map is grey:** the map tiles and the satellite image of the map come from the internet.
- **A municipality takes about a second to open:** the engine computes the answer at each request.
- **The tests in `site-versao-final/testes/`** were written for our machine (they need Node.js and Microsoft Edge). They are here to be read.

## What is in this folder

| Folder | Content |
|---|---|
| `app.py` | the start: `python app.py` |
| `site-versao-final/web/` | the site: HTML, CSS and JavaScript, with no framework |
| `site-versao-final/nucleo/motor.py` | the Python engine: crops that fit each municipality, climate, El Niño, soil moisture and rotation rules |
| `site-versao-final/servidor.py` | the server (Python standard library) |
| `site-versao-final/dados/` | income, projection and census data used by the site |
| `site-versao-final/testes/`, `analise/`, `ferramentas/` | the tests, the analyses and the scripts that prepare the data |
| `scripts/` | the three modules the engine imports |
| `pesquisa/` | the catalogue of 147 rotation configurations, with the evidence grade and the source of each one |
| `dados/` | the data files the engine reads when it runs |

Credits and data sources are in `site-versao-final/CREDITOS.md`.

## What is not in this folder

The raw data (about 11 GB) stay out because of their size. Two of them matter when running from this package:

- **FAO GAEZ v4 rasters (2.3 GB).** The package brings the suitability already sampled for the 1,794 municipalities, which is
  all the site asks for.
- **SMAP L4 daily series (584 MB).** The package brings the 30-day window the site shows, already computed.

The scripts that download and prepare everything are in the repository.

## AI use

Claude (Anthropic) helped write the code, translate the site into English, draw the icons in code and summarize the scientific
papers, under the team's direction. The catalogue in `pesquisa/` was extracted from the papers by AI agents and checked against
each paper's text. No image, audio or video is AI-generated, and the project uses no NASA branding. The data and the satellite
imagery are real.

---

## Em português

Esta pasta tem só o necessário para rodar o site e analisá-lo. O repositório completo está em
https://github.com/Netinhoklz/competicao-nasa, branch `estudo-jose`.

**Como dar a partida.** Com o Python 3.13 e internet (para o mapa), abra um terminal nesta pasta e rode os quatro comandos
de "How to start": criar o ambiente, ativar, instalar os pacotes e `python app.py`. O `app.py` é a partida: confere os pacotes
e sobe o servidor. Quando aparecer a linha `QUADRA (site final) em http://localhost:8090`, abra esse endereço no navegador.
Ctrl+C para o servidor; `python app.py 8091` usa outra porta. O site abre em inglês; a troca para português fica na página
inicial e no topo das outras páginas.

**Como funciona.** O navegador monta o plano, a renda e o relatório com as respostas do agricultor, que ficam no endereço da
página (não há cadastro nem banco de dados). O servidor (`site-versao-final/servidor.py`) entrega os arquivos e duas rotas:
`/api/local?cod=<código IBGE>` (tudo o que o motor sabe do município) e `/api/municipios` (a malha). O motor
(`site-versao-final/nucleo/motor.py`) lê `dados/` e o catálogo de `pesquisa/`.

**Se algo der errado.** "Missing Python packages": rode `pip install -r requirements.txt` com o ambiente ativo. Porta ocupada:
`python app.py 8091`. Mapa cinza: falta internet (as imagens do mapa vêm dela).

**O que não veio.** Os dados brutos (cerca de 11 GB). Os rasters do GAEZ (2,3 GB) e a série diária do SMAP (584 MB) foram
trocados pelo que o site usa deles: a aptidão já amostrada nos 1.794 municípios e a janela de 30 dias já calculada.

**Uso de IA.** O Claude (Anthropic) ajudou a escrever o código, traduzir o site para o inglês, desenhar os ícones por código
e resumir os artigos, sob a direção da equipe. Nenhuma imagem, áudio ou vídeo foi gerado por IA, e o projeto não usa marca
da NASA. Os dados e as imagens de satélite são reais.
"""


def copiar(origem, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)


def cache_gaez():
    """O cache do GAEZ com o pixel do ponto interno de cada município (a mesma chave e o mesmo ponto do motor.aptidao)."""
    chave = lambda lat, lon: f"{math.floor((90 - lat) * 12)},{math.floor((lon + 180) * 12)}"  # noqa: E731
    cache = dict(motor._cache("cache_gaez_v3.json"))
    pontos = [motor.ponto_do_municipio(c) for c in motor.MUN.cod]
    faltam = {}
    for lat, lon in pontos:
        if chave(lat, lon) not in cache:
            faltam.setdefault(chave(lat, lon), (lon, lat))
    if faltam:
        si = motor.GZ.aptidao(list(faltam.values()))  # uma passada por raster, todos os pontos de uma vez
        for i, k in enumerate(faltam):
            cache[k] = {f"{c}|{ins}": v[i] for (c, ins), v in si.items()}
    sem = [c for c, (lat, lon) in zip(motor.MUN.cod, pontos) if chave(lat, lon) not in cache]
    if sem:
        sys.exit(f"cache do GAEZ sem {len(sem)} municípios: {sem[:5]}")
    return cache, len(faltam)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SITE, DEST / "site-versao-final", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.bak"))
    copiar(PROJ / "app.py", DEST / "app.py")  # a partida: python app.py
    for m in MODULOS:
        copiar(PROJ / "scripts" / m, DEST / "scripts" / m)
    for p in PESQUISA:
        copiar(PROJ / "pesquisa" / p, DEST / "pesquisa" / p)
    for a in ARQUIVOS:
        copiar(DADOS / a, DEST / "dados" / a)
    cache, novos = cache_gaez()
    (DEST / "dados" / "prototipo" / "cache_gaez_v3.json").write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    (DEST / "requirements.txt").write_text(REQUISITOS, encoding="utf-8", newline="\n")
    (DEST / "README.md").write_text(LEIAME, encoding="utf-8", newline="\n")
    tam = sum(f.stat().st_size for f in DEST.rglob("*") if f.is_file())
    print(f"pacote em {DEST}: {sum(1 for f in DEST.rglob('*') if f.is_file())} arquivos, {tam / 1e6:.0f} MB; "
          f"cache do GAEZ com {len(cache)} pixels ({novos} amostrados agora) para {len(motor.MUN)} municípios")


if __name__ == "__main__":
    main()
