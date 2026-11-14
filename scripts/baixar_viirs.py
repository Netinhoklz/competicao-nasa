"""Focos de fogo FIRMS (VIIRS S-NPP 375 m e MODIS 1 km) - arquivos anuais abertos por pais.

Baixa o CSV anual do Brasil, filtra o Nordeste, atribui a UF (IBGE), grava parquet e apaga o CSV bruto.
Tambem registra evidencias de cobertura global (arquivos por pais em varios continentes).
Uso: python -I baixar_viirs.py [--fontes viirs-snpp modis]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa: E402,F401

import geopandas as gpd  # noqa: E402
import pandas as pd  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

BASE = "https://firms.modaps.eosdis.nasa.gov/data/country/{s}/{y}/{s}_{y}_{pais}.csv"
FONTES = {"viirs-snpp": (2012, 2025, pasta("viirs")), "modis": (2000, 2025, pasta("modis"))}
TMPF = RAIZ / "tmp" / "firms"


def log(*a):
    print(datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def processar(fonte, ano, sess, ufs):
    url = BASE.format(s=fonte, y=ano, pais="Brazil")
    csv = TMPF / f"{fonte}_{ano}_Brazil.csv"
    baixar(url, csv, sess)
    df = pd.read_csv(csv, low_memory=False)
    n_br = len(df)
    lon0, lat0, lon1, lat1 = BBOX_NE
    df = df[(df.longitude >= lon0) & (df.longitude <= lon1) & (df.latitude >= lat0) & (df.latitude <= lat1)].copy()
    g = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
    g = gpd.sjoin(g, ufs[["codarea", "geometry"]], how="inner", predicate="within")
    out = pd.DataFrame(g.drop(columns=["geometry", "index_right"])).rename(columns={"codarea": "uf"})
    out["uf"] = out["uf"].astype(int)
    out["acq_date"] = pd.to_datetime(out["acq_date"])
    out["fonte"] = fonte
    tam = csv.stat().st_size
    csv.unlink()
    return out, {"ano": ano, "fonte": fonte, "focos_brasil": n_br, "focos_nordeste": len(out), "csv_bytes": tam}


def validacao(sess):
    paises = ["Brazil", "United_States", "India", "Australia", "Kenya", "Argentina", "Ukraine", "France", "China",
              "Canada", "Indonesia", "Nigeria", "South_Africa", "Mexico", "Kazakhstan", "Russian_Federation", "Russia"]
    res = {}
    for s in ("viirs-snpp", "modis"):
        for p in paises:
            url = BASE.format(s=s, y=2023, pais=p)
            try:
                r = sess.head(url, timeout=60, allow_redirects=True)
                res[f"{s}/{p}"] = {"status": r.status_code, "bytes": int(r.headers.get("Content-Length", 0) or 0)}
            except Exception as e:
                res[f"{s}/{p}"] = {"status": "erro", "erro": repr(e)[:100]}
    for s in ("viirs-noaa20", "viirs-noaa21", "viirs-j1"):
        r = sess.head(BASE.format(s=s, y=2023, pais="Brazil"), timeout=60, allow_redirects=True)
        res[f"{s}/Brazil"] = {"status": r.status_code}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fontes", nargs="+", default=["viirs-snpp", "modis"])
    a = ap.parse_args()
    TMPF.mkdir(parents=True, exist_ok=True)
    sess = sessao_http()
    ufs = nordeste_gdf()
    for fonte in a.fontes:
        y0, y1, dest = FONTES[fonte]
        partes, resumo = [], []
        for ano in range(y0, y1 + 1):
            t0 = time.time()
            try:
                df, r = processar(fonte, ano, sess, ufs)
                partes.append(df)
                resumo.append(r)
                log(fonte, ano, r, f"{time.time() - t0:.0f}s")
            except Exception as e:
                resumo.append({"ano": ano, "fonte": fonte, "erro": repr(e)[:200]})
                log("ERRO", fonte, ano, repr(e)[:200])
        tudo = pd.concat(partes, ignore_index=True)
        nome = "firms_viirs_snpp_nordeste.parquet" if fonte == "viirs-snpp" else "firms_modis_nordeste.parquet"
        tudo.to_parquet(dest / nome, index=False)
        pd.DataFrame(resumo).to_csv(dest / nome.replace(".parquet", "_resumo_anual.csv"), index=False)
        registrar_manifesto(dest.name, {f"firms_{fonte}": {
            "fonte": f"NASA FIRMS {fonte} - arquivos anuais por pais (Brasil), filtrados ao Nordeste por UF IBGE",
            "url_padrao": BASE, "anos": [y0, y1], "linhas": len(tudo), "arquivos": [nome, nome.replace('.parquet', '_resumo_anual.csv')],
            "nota": "ano corrente nao tem arquivo anual (so NRT via API com MAP_KEY)"}})
        log(fonte, "salvo", len(tudo))
    val = validacao(sess)
    (pasta("viirs") / "validacao_global_firms.json").write_text(json.dumps(
        {"gerado_em": datetime.now().isoformat(timespec="seconds"), "head_2023": val}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    registrar_manifesto("viirs", {"vnp13_ndvi": {
        "status": "NAO BAIXADO - exige Earthdata Login (LP DAAC: VNP13A1/VNP13Q1/VJ113A1)",
        "alternativa_aberta": "MODIS MOD13Q1 (mesmo algoritmo de VI) em dados/modis; VIIRS e a continuidade apos o fim do Terra/Aqua"}})
    log("fim")


if __name__ == "__main__":
    main()
