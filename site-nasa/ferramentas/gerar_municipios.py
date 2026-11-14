"""Gera os dados do site: static/data/municipios_ne.json (numeros por municipio) e static/data/malha_ne.json
(malha IBGE ja projetada em caminhos SVG, para o mapa do painel Roca Certa).

Entradas (a partir da raiz do repositorio):
  conselho/analises/saidas/jp_nordeste_municipios.parquet e jp_nordeste_municipios_chuva.parquet
    (gerados por conselho/analises/jp_nordeste_municipios.py);
  dados_resumo/derivados/ibge_ne_mun_imerg_mensal.parquet (chuva mensal IMERG por municipio);
  dados_resumo/derivados/indices_clima_mensal.parquet (ONI);
  interface-nordeste-jp/dados/ibge_malha_ne_{municipios,ufs}.json (malha IBGE, API de malhas v3, qualidade minima).
Uso: python site-nasa/ferramentas/gerar_municipios.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import polars as pl

RAIZ = Path(__file__).resolve().parents[2]
SAIDAS = RAIZ / "conselho" / "analises" / "saidas"
DERIV = RAIZ / "dados_resumo" / "derivados"
MALHAS = RAIZ / "interface-nordeste-jp" / "dados"
DESTINO = RAIZ / "site-nasa" / "static" / "data"
ANALOGOS = [1998, 2010, 2016, 2024]

# projecao equirretangular do Nordeste (cos da latitude media), em px por grau
LON0, LAT0, ESCALA = -48.9, -0.9, 40.0
LON_MAX = -34.5            # deixa de fora as ilhas oceanicas (Fernando de Noronha)
COS = math.cos(math.radians(9.5))
PASSO_MIN = 0.7            # px: vertices mais perto que isso do anterior saem (simplifica a malha)


def centro(geom: dict) -> tuple[float, float]:
    """Media dos vertices do maior anel externo: basta para achar o municipio mais perto de um ponto."""
    poligonos = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    anel = max((p[0] for p in poligonos), key=len)
    return (round(sum(y for _, y in anel) / len(anel), 3), round(sum(x for x, _ in anel) / len(anel), 3))


def inteiro(v: float | None) -> int | None:
    return None if v is None or not math.isfinite(v) else round(v)


def caminho(geom: dict) -> tuple[str, list[float]]:
    """Geometria GeoJSON -> (atributo `d` de um <path> SVG, caixa [x0, y0, x1, y1])."""
    poligonos = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    partes, xs, ys = [], [], []
    for pol in poligonos:
        for anel in pol:
            if min(lon for lon, _ in anel) > LON_MAX:
                continue
            pts, ultimo = [], None
            for lon, lat in anel:
                x, y = (lon - LON0) * COS * ESCALA, (LAT0 - lat) * ESCALA
                if ultimo and math.hypot(x - ultimo[0], y - ultimo[1]) < PASSO_MIN:
                    continue
                pts.append((x, y))
                ultimo = (x, y)
            if len(pts) < 3:
                continue
            xs += [p[0] for p in pts]
            ys += [p[1] for p in pts]
            partes.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z")
    caixa = [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)] if xs else []
    return "".join(partes), caixa


def malha() -> dict:
    mun = json.loads((MALHAS / "ibge_malha_ne_municipios.json").read_text("utf-8"))["features"]
    ufs = json.loads((MALHAS / "ibge_malha_ne_ufs.json").read_text("utf-8"))["features"]
    sigla = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
    estados = {}
    for f in ufs:
        d, caixa = caminho(f["geometry"])
        estados[sigla[f["properties"]["codarea"]]] = {"d": d, "caixa": caixa}
    x1 = max(e["caixa"][2] for e in estados.values())
    y1 = max(e["caixa"][3] for e in estados.values())
    return {"fonte": "IBGE, API de malhas v3 (qualidade minima), simplificada",
            "vb": [round(x1 + 4), round(y1 + 4)], "ufs": estados,
            "m": {f["properties"]["codarea"]: caminho(f["geometry"])[0] for f in mun}}


def main() -> None:
    mun = pl.read_parquet(SAIDAS / "jp_nordeste_municipios.parquet")
    chuva = pl.read_parquet(SAIDAS / "jp_nordeste_municipios_chuva.parquet")
    anos = list(range(1998, chuva["ano_est"].max() + 1))
    serie = {cod: dict(zip(g["ano_est"], g["pct"])) for (cod,), g in chuva.group_by("cod_mun")}
    analogo = {cod: dict(zip(g["ano_est"], g["chuva"]))
               for (cod,), g in chuva.filter(pl.col("ano_est").is_in(ANALOGOS)).group_by("cod_mun")}
    imerg = pl.read_parquet(DERIV / "ibge_ne_mun_imerg_mensal.parquet")
    clima = (imerg.filter(pl.col("data").dt.year() <= 2025)
             .group_by("cod_mun", pl.col("data").dt.month().alias("mes")).agg(pl.col("precip_mm").mean())
             .sort("mes").group_by("cod_mun", maintain_order=True).agg(pl.col("precip_mm")))
    clima = dict(zip(clima["cod_mun"], clima["precip_mm"].to_list()))
    oni = (pl.read_parquet(DERIV / "indices_clima_mensal.parquet").filter(pl.col("variavel") == "ONI")
           .sort("data").tail(1).row(0, named=True))
    geo = json.loads((MALHAS / "ibge_malha_ne_municipios.json").read_text("utf-8"))
    centros = {f["properties"]["codarea"]: centro(f["geometry"]) for f in geo["features"]}

    m = {}
    for r in mun.iter_rows(named=True):
        cod, med, t1 = r["cod_mun"], r["mediana"], r["t1"]
        a, s = analogo.get(cod, {}), serie.get(cod, {})
        m[cod] = [
            r["municipio"], r["uf"], *centros.get(cod, (None, None)), r["ini"], inteiro(med),
            [inteiro(v) for v in clima.get(cod, [])],
            # por analogo: % do normal e se ficou no terco mais seco dos anos
            [[inteiro(a[y] / med * 100), int(a[y] <= t1)] if y in a and med else None for y in ANALOGOS],
            None if r["rho_milho"] is None else round(r["rho_milho"], 2), inteiro(r["pct100_milho"]),
            inteiro(r["solo_pctl"]), r["solo_n"],
            int(bool(r["semiarido"])), [inteiro(s.get(y)) for y in anos],
        ]
    dados = {"campos": ["nome", "uf", "lat", "lon", "ini", "normal_mm", "clima_mm", "analogos", "rho_milho",
                        "milho_pct_100mm", "solo_pctl", "solo_n", "semiarido", "serie_pct"],
             "anos": anos, "analogos": ANALOGOS, "solo_mes": "out 2026",
             "oni": {"mes": f"{oni['data']:%m/%Y}", "valor": round(oni["valor"], 2)}, "m": m}
    for nome, conteudo in (("municipios_ne.json", dados), ("malha_ne.json", malha())):
        arq = DESTINO / nome
        arq.write_text(json.dumps(conteudo, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{nome}: {arq.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
