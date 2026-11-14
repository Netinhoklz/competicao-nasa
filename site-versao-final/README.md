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
