# QUADRA, site final (NASA Space Apps 2026, Field Shift)

O site junta as três partes do time num lugar só:
- **globo e mapa:** João Pedro;
- **núcleo de dados e rotação:** José;
- **distribuição em faixas:** Vicente.

A pessoa abre o globo, escolhe o município do Nordeste e segue 5 passos: o que o lugar permite → sua roça (perguntas) → como
plantar e distribuir → quanto rende → segurança por colheita. O desenho e as decisões estão em `PLANO_INTEGRACAO.md`; a análise
dos 10 agentes que levou a ele está em `analise/`.

## Como rodar

```bash
cd site-versao-final
E:/campeonato-nasa/venv/Scripts/python.exe -X utf8 servidor.py      # http://localhost:8090  (sobe em ~10 s)
```

- `http://localhost:8090/` abre o globo; `http://localhost:8090/roca.html#/2311306/1` vai direto a Quixadá.
- O núcleo lê os dados locais em `E:/campeonato-nasa/dados/` (GAEZ, ZARC, IMERG, SMAP etc.) e os JSON pré-calculados de `dados/`.
  Precisa de internet só para as fontes e os ladrilhos do mapa.
- Para regerar os JSON: `ferramentas/preparar_financeiro_site.py`, `preparar_projecao.py`, `preparar_padroes_censo.py` e
  `preparar_el_nino_uf.py` (cada um diz no topo o que lê e o que grava).

## Pacote de entrega (rodar em outra máquina)

Só esta pasta não roda sozinha: o núcleo importa 3 módulos de `scripts/`, lê `pesquisa/catalogo_rotacoes.json` e os dados do `E:`.
O pacote que roda em qualquer máquina é montado por `ferramentas/montar_entrega.py` (da raiz do repositório):

```bash
E:/campeonato-nasa/venv/Scripts/python.exe -X utf8 site-versao-final/ferramentas/montar_entrega.py   # -> E:/campeonato-nasa/entrega/QUADRA
```

A pasta sai com cerca de 120 MB: o site, os 3 módulos, o catálogo, os ~75 MB de dados que o núcleo lê, `requirements.txt`,
o `README.md` de quem recebe e o `app.py` da raiz. Lá, a partida é `pip install -r requirements.txt` e `python app.py`.
No lugar dos rasters do GAEZ (2,3 GB) e da série diária do SMAP (584 MB) vão a aptidão já amostrada nos 1.794 municípios e a
janela de 30 dias já calculada; o núcleo usa esses caches quando a fonte falta.

## Pastas

| Pasta | O que tem |
|---|---|
| `servidor.py` | servidor só com a biblioteca padrão: o site (`web/`) e a API (`/api/local`, `/api/municipios`) |
| `nucleo/motor.py` | o motor do protótipo do José, com as mudanças do site final (cabeçalho do arquivo) |
| `dados/` | financeiro, projeção e padrões do Censo por município (JSON gerado) |
| `ferramentas/` | scripts que geram `dados/`; `origem_analise/` guarda os scripts dos agentes de análise |
| `web/` | o site: `index.html` (globo), `roca.html` (jornada), `js/passos/` (um módulo por passo), `modulos/percolacampo/` |
| `testes/exemplos/` | respostas reais da API (Quixadá, Arapiraca, Barreiras) |
| `analise/` | os 10 relatórios de integração |

## API

`GET /api/local?cod=<IBGE>` (ou `lat=&lon=`), com respostas opcionais: `textura` 1–3, `ad` e `ad_baixio` 11–16,
`maniva` tem/nao/plantada, `baixio` 0/1, `hoje` AAAA-MM-DD. Devolve o cardápio, este ano, o plano, o calendário, a evidência, o
financeiro, a projeção, os padrões do Censo e a manchete de El Niño do estado. O contrato que os passos usam está em
`web/js/passos/LEIA-ME.md`.

## Créditos

Veja `CREDITOS.md`: cada arquivo que veio de um colega, com o branch e o commit de origem e o que mudou.
