"""Curador de bases (v3): converte a rede de umidade do solo do CEMADEN (Zeri et al., Mendeley Data,
doi 10.17632/xrk5rfcpvg.2; ago/2015-abr/2019, 360 PCDs, EC-5 a 10 e 20 cm, horario em UTC) para parquet diario.

Entrada: E:/campeonato-nasa/dados/complementares/cemaden/pcd/*.xlsx (extraidos de bruto/PCDs_.zip)
Saida:   E:/campeonato-nasa/dados/complementares/cemaden/cemaden_diario.parquet
         colunas: estacao, data (dia UTC), us10_media, us20_media, us10_13utc, us20_13utc (media das horas 13 e 14 UTC,
         casando com o granulo SMAP L4 das 13:30 UTC), chuva_mm, n_horas
         E:/campeonato-nasa/dados/complementares/cemaden/cemaden_estacoes.parquet (coordenadas e textura do Info)
"""
import sys
from multiprocessing import Pool

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
from openpyxl import load_workbook

BASE = DADOS / "complementares" / "cemaden"


def ler(caminho):
    wb = load_workbook(caminho, read_only=True, data_only=True)
    ws = wb["Data"]
    linhas = list(ws.iter_rows(values_only=True))
    cab = [str(c) for c in linhas[0]]
    d = pd.DataFrame(linhas[1:], columns=cab)
    info = {}
    for r in wb["Info"].iter_rows(values_only=True):
        if r and r[0] is not None and len(r) > 1:
            info[str(r[0]).strip()] = r[1]
    wb.close()
    est = Path(caminho).stem.split("_")[-1]
    d["Time"] = pd.to_datetime(d["Time"])
    for c in d.columns[1:]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    # fora da faixa fisica do EC-5 vira NaN
    for c in [c for c in d.columns if c.startswith("US")]:
        d.loc[(d[c] <= 0) | (d[c] > 0.6), c] = np.nan
    d["data"] = d["Time"].dt.floor("D")
    h = d["Time"].dt.hour
    g = d.groupby("data")
    out = pd.DataFrame({
        "us10_media": g["US10cm"].mean() if "US10cm" in d else np.nan,
        "us20_media": g["US20cm"].mean() if "US20cm" in d else np.nan,
        "chuva_mm": g["Precip"].sum(min_count=20) if "Precip" in d else np.nan,
        "n_horas": g["US10cm"].count() if "US10cm" in d else 0,
    })
    m = d[h.isin([13, 14])].groupby("data")
    out["us10_13utc"] = m["US10cm"].mean() if "US10cm" in d else np.nan
    out["us20_13utc"] = m["US20cm"].mean() if "US20cm" in d else np.nan
    out = out.reset_index()
    out.insert(0, "estacao", est)
    meta = {"estacao": est, "arquivo": Path(caminho).name, "colunas": ",".join(cab)}
    for k in ["City", "State", "Latitude", "Longitude", "Sand", "Silt", "Clay"]:
        meta[k.lower()] = info.get(k)
    return out, meta


def main():
    fs = sorted((BASE / "pcd").glob("*.xlsx"))
    t0 = time.time()
    with Pool(6) as p:
        res = p.map(ler, fs, chunksize=4)
    dia = pd.concat([r[0] for r in res], ignore_index=True)
    est = pd.DataFrame([r[1] for r in res])
    dia.to_parquet(BASE / "cemaden_diario.parquet", index=False)
    est.to_parquet(BASE / "cemaden_estacoes.parquet", index=False)
    print(len(fs), "arquivos;", len(dia), "estacao-dias;", f"{time.time()-t0:.0f}s")
    print(est.head().to_string())
    registrar_manifesto("complementares/cemaden", {
        "fonte": "CEMADEN, rede de umidade do solo do semiarido (Zeri et al.), Mendeley Data v2",
        "doi": "10.17632/xrk5rfcpvg.2",
        "url": "https://data.mendeley.com/datasets/xrk5rfcpvg/2",
        "periodo": "2015-08 a 2019-05 (horario, UTC)",
        "estacoes": len(est),
        "sensor": "Decagon EC-5, calibracao padrao (+-0,03 m3/m3), 10 e 20 cm; subconjunto com 30 e 40 cm",
        "arquivos": ["bruto/PCDs_.zip (sha256 278bef79...)", "bruto/_Stations.xlsx", "pcd/*.xlsx",
                     "cemaden_diario.parquet", "cemaden_estacoes.parquet"],
        "script": "conselho/analises/v3_curador_converter_cemaden.py",
    }, base=BASE)


if __name__ == "__main__":
    main()
