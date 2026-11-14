"""Monta a pagina do Nordeste (index.html): recorta os dados por municipio, desenha a malha e injeta no modelo.

Entradas:
  conselho/analises/saidas/jp_nordeste_municipios.parquet e jp_nordeste_municipios_chuva.parquet
    (gerados por conselho/analises/jp_nordeste_municipios.py);
  interface-nordeste-jp/dados/ibge_malha_ne_{municipios,ufs}.json (IBGE, API de malhas v3, qualidade minima;
    baixados aqui se nao existirem).
Saidas: interface-nordeste-jp/dados/dados_pagina.json e interface-nordeste-jp/index.html
Uso: python interface-nordeste-jp/scripts/montar_pagina.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import polars as pl
import requests

BASE = Path(__file__).resolve().parent.parent
SAIDAS = BASE.parent / "conselho" / "analises" / "saidas"
MALHA = "https://servicodados.ibge.gov.br/api/v3/malhas/regioes/2?formato=application/vnd.geo%2Bjson&qualidade=minima&intrarregiao={}"
LON0, LAT0, ESCALA = -48.9, -0.9, 40.0     # canto noroeste e pixels por grau
LON_MAX = -34.5                            # deixa de fora as ilhas oceanicas (Fernando de Noronha)
COS = math.cos(math.radians(9.5))
RHO_SIG = 0.38


def malha(nivel: str) -> list[dict]:
    arq = BASE / "dados" / f"ibge_malha_ne_{'municipios' if nivel == 'municipio' else 'ufs'}.json"
    if not arq.exists():
        arq.write_bytes(requests.get(MALHA.format(nivel), timeout=300).content)
    return json.loads(arq.read_text(encoding="utf-8"))["features"]


def caminho(geom: dict) -> str:
    """Geometria GeoJSON -> atributo `d` de um <path> SVG, em projecao equirretangular."""
    poligonos = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    partes = []
    for pol in poligonos:
        for anel in pol:
            if min(lon for lon, _ in anel) > LON_MAX:
                continue
            pts = [f"{(lon - LON0) * COS * ESCALA:.1f} {(LAT0 - lat) * ESCALA:.1f}" for lon, lat in anel]
            partes.append("M" + "L".join(pts) + "Z")
    return "".join(partes)


def arred(v: float | None, casas: int = 2) -> float | None:
    return None if v is None or not math.isfinite(v) else round(v, casas)


def main() -> None:
    mun = pl.read_parquet(SAIDAS / "jp_nordeste_municipios.parquet")
    chuva = pl.read_parquet(SAIDAS / "jp_nordeste_municipios_chuva.parquet")
    anos = list(range(1998, chuva["ano_est"].max() + 1))
    serie = {cod: dict(zip(g["ano_est"], g["pct"])) for (cod,), g in chuva.group_by("cod_mun")}
    desenho = {f["properties"]["codarea"]: caminho(f["geometry"]) for f in malha("municipio")}

    linhas = []
    for r in mun.iter_rows(named=True):
        s = serie.get(r["cod_mun"], {})
        linhas.append([
            r["cod_mun"], r["municipio"], r["uf"], int(bool(r["semiarido"])), r["ini"], arred(r["frac_na_estacao"]),
            arred(r["mediana"], 0), arred(r["rho_milho"]), arred(r["pct100_milho"], 0), arred(r["rho_feijao"]),
            arred(r["rho_dipolo"]), arred(r["analogo_pct"], 0), r["analogo_secos"], r["analogo_n"],
            arred(r["solo_pctl"], 0), desenho.get(r["cod_mun"], ""),
            ",".join("" if s.get(a) is None else str(round(s[a])) for a in anos),
        ])

    def pct_sig(c: str) -> pl.Expr:
        return ((pl.col(c) >= RHO_SIG).mean() * 100).round(0)

    estados = (mun.group_by("uf").agg(
        pl.len().alias("mun"), pl.col("rho_milho").median().round(2), pct_sig("rho_milho").alias("sig_milho"),
        pct_sig("rho_feijao").alias("sig_feijao"),
        ((pl.col("rho_dipolo") <= -RHO_SIG).mean() * 100).round(0).alias("sig_dipolo"),
        pl.col("analogo_pct").median().round(0), pl.col("solo_pctl").median().round(0))
        .sort("sig_milho", descending=True))

    dados = {
        "anos": anos, "analogos": [1998, 2010, 2016, 2024], "smap_mes": "outubro de 2026", "smap_n": mun["solo_n"].max(),
        "vb": [round((LON_MAX - LON0) * COS * ESCALA) + 4, round((LAT0 + 18.5) * ESCALA)],
        "ufs": [caminho(f["geometry"]) for f in malha("UF")],
        "m": linhas, "estados": estados.rows(),
    }
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
    (BASE / "dados" / "dados_pagina.json").write_text(texto, encoding="utf-8")
    modelo = (BASE / "fonte" / "pagina.html").read_text(encoding="utf-8")
    (BASE / "index.html").write_text(modelo.replace("__DATA__", texto), encoding="utf-8")
    print(f"index.html gerado: {len(linhas)} municipios, {len(texto) // 1024} KB de dados")


if __name__ == "__main__":
    main()
