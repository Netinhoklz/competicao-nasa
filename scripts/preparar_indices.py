"""Indices climaticos de teleconexao (ENSO e Atlantico tropical) em formato longo mensal.

ONI (NOAA CPC): media movel de 3 meses da anomalia de TSM no Nino 3.4; atribuida ao mes central.
TNA/TSA (NOAA PSL): anomalia de TSM do Atlantico tropical norte (5.5N-23.5N) e sul (0-20S).
Dipolo (gradiente meridional) = TNA - TSA: positivo = Atlantico norte mais quente = seca no Ceara.
Saida: derivados/indices_clima_mensal.parquet
"""
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
D = pasta("indices_clima")
SEAS = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}


def oni():
    df = pd.read_csv(D / "oni.ascii.txt", sep=r"\s+")
    df["data"] = pd.to_datetime(dict(year=df["YR"], month=df["SEAS"].map(SEAS), day=1))
    return pd.DataFrame({"data": df["data"], "variavel": "ONI", "valor": df["ANOM"], "unidade": "°C",
                         "fonte": "NOAA CPC ONI (ERSSTv5)"})


def psl(nome, rotulo):
    linhas = (D / f"{nome}.data").read_text().splitlines()
    a0, a1 = map(int, linhas[0].split()[:2])
    reg = []
    for ln in linhas[1:]:
        p = ln.split()
        if len(p) == 13 and p[0].isdigit() and a0 <= int(p[0]) <= a1:
            for m, v in enumerate(p[1:], 1):
                v = float(v)
                if v > -99:
                    reg.append((pd.Timestamp(int(p[0]), m, 1), v))
    df = pd.DataFrame(reg, columns=["data", "valor"])
    df["variavel"], df["unidade"], df["fonte"] = rotulo, "°C", f"NOAA PSL {rotulo} (HadISST1.1, clim. 1991-2020)"
    return df


if __name__ == "__main__":
    o, tna, tsa = oni(), psl("tna", "TNA"), psl("tsa", "TSA")
    dip = tna.merge(tsa, on="data", suffixes=("_n", "_s"))
    dip = pd.DataFrame({"data": dip["data"], "variavel": "DIPOLO_TNA_menos_TSA", "valor": dip["valor_n"] - dip["valor_s"],
                        "unidade": "°C", "fonte": "calculado: TNA - TSA"})
    out = pd.concat([o, tna, tsa, dip], ignore_index=True)[["data", "variavel", "valor", "unidade", "fonte"]]
    out.to_parquet(DERIV / "indices_clima_mensal.parquet")
    for v, g in out.groupby("variavel"):
        print(v, g.data.min().date(), "->", g.data.max().date(), len(g), "| ultimo:", round(g.valor.iloc[-1], 2))
    registrar_manifesto("indices_clima", {
        "fonte": "NOAA CPC (ONI) e NOAA PSL (TNA, TSA)",
        "urls": ["https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
                 "https://psl.noaa.gov/data/correlation/tna.data", "https://psl.noaa.gov/data/correlation/tsa.data"],
        "derivado": "derivados/indices_clima_mensal.parquet (ONI no mes central; dipolo = TNA - TSA)",
        "arquivos": {f.name: f.stat().st_size for f in D.glob("*.*") if f.is_file()},
    })
