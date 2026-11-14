"""Gera web/dados/busca_municipios.json: a lista dos 1.794 municipios do Nordeste para a busca local do globo.

Origem dos dados: Joao Pedro (branch estudo-jp, 29f81f6)
  - colegas/joao-pedro/site-nasa/static/data/municipios_ne.json  -> codigo IBGE, nome e UF;
  - colegas/joao-pedro/interface-nordeste-jp/dados/ibge_malha_ne_municipios.json (malha IBGE, API de malhas v3,
    qualidade minima) -> ponto e caixa de cada municipio.
O "centro" do municipios_ne.json e a media dos vertices do maior anel, que pode cair fora de municipios recortados;
aqui o ponto e o polo de inacessibilidade (shapely.ops.polylabel) do maior poligono: sempre dentro do municipio.
A caixa [oeste, sul, leste, norte] e a do municipio inteiro (o mapa usa para escolher o zoom da chegada).

Uso (Python do miniconda, que tem shapely):
  C:/Users/netinhoklz/miniconda3/python.exe -I site-versao-final/ferramentas/gerar_busca_municipios.py
"""
from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import shape
from shapely.ops import polylabel

RAIZ = Path(__file__).resolve().parents[2]
JP = RAIZ / "colegas" / "joao-pedro"
MUNICIPIOS = JP / "site-nasa" / "static" / "data" / "municipios_ne.json"
MALHA = JP / "interface-nordeste-jp" / "dados" / "ibge_malha_ne_municipios.json"
DESTINO = RAIZ / "site-versao-final" / "web" / "dados" / "busca_municipios.json"


def main() -> None:
    m = json.loads(MUNICIPIOS.read_text("utf-8"))["m"]
    geo = {f["properties"]["codarea"]: shape(f["geometry"]) for f in json.loads(MALHA.read_text("utf-8"))["features"]}
    lista, fora = [], 0
    for cod, campos in m.items():
        g = geo[cod]
        maior = max(g.geoms, key=lambda p: p.area) if g.geom_type == "MultiPolygon" else g
        p = polylabel(maior, tolerance=0.002)
        lat_jp, lon_jp = campos[2], campos[3]
        if not g.contains(shape({"type": "Point", "coordinates": [lon_jp, lat_jp]})):
            fora += 1
        w, s, e, n = g.bounds
        lista.append({"cod": cod, "nome": campos[0], "uf": campos[1], "lat": round(p.y, 4), "lon": round(p.x, 4),
                      "bbox": [round(w, 3), round(s, 3), round(e, 3), round(n, 3)]})
    lista.sort(key=lambda x: x["cod"])
    saida = {
        "fonte": "IBGE (codigos, nomes e malha de municipios), via dados do Joao Pedro (estudo-jp, 29f81f6)",
        "ponto": "polo de inacessibilidade do maior poligono do municipio (sempre dentro dele)",
        "bbox": "[oeste, sul, leste, norte] do municipio, em graus",
        "n": len(lista),
        "municipios": lista,
    }
    DESTINO.write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{DESTINO.name}: {len(lista)} municipios, {DESTINO.stat().st_size // 1024} KB; "
          f"centro do JP fora do proprio municipio em {fora}")


if __name__ == "__main__":
    main()
