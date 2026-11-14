"""Conselho - Especialista em sensoriamento remoto e modelos de fundacao.

Pergunta: na janela que decide a safra (semeadura/emergencia, ~15/jan-15/abr no Ceara), quantas vistas limpas
um pixel de lavoura recebe dos sensores opticos? Quanto o HLS (Landsat+Sentinel-2) melhora sobre o Landsat
sozinho, e quanto ainda falta (o que justifica radar Sentinel-1/NISAR e preenchimento por modelo)?

Metodo (tabelas por cena das 4 AOIs; frac_valida = fracao de pixels limpos da AOI na cena):
- vistas limpas esperadas por pixel por mes = soma de frac_valida das cenas no mes / anos;
- P(um pixel ficar 16 dias sem nenhuma vista limpa) = media sobre janelas de 16 dias de prod(1 - f_s),
  supondo independencia entre cenas (otimista, porque a nuvem e correlacionada);
- maior intervalo (dias) entre cenas "uteis" (f >= 0,6) dentro de 15/jan-15/abr, por ano e AOI.
Periodo comum 2020-2025 (o HLS desta base comeca em 2020).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings

import numpy as np
import pandas as pd

from comum import DADOS

warnings.filterwarnings("ignore")

hls = pd.read_parquet(DADOS / "sentinel2/hls_aoi_cenas.parquet")
s2 = pd.read_parquet(DADOS / "sentinel2/s2_aoi_cenas.parquet")
ls = pd.read_parquet(DADOS / "landsat/landsat_aoi_cenas_l89.parquet")
for d in (hls, s2, ls):
    d["datetime"] = pd.to_datetime(d["datetime"], utc=True).dt.tz_localize(None)
    d["frac_valida"] = d["frac_valida"].fillna(0).clip(0, 1)
fontes = {
    "Landsat 8/9": ls[["aoi", "datetime", "frac_valida"]],
    "Sentinel-2": s2[["aoi", "datetime", "frac_valida"]],
    "HLS L30+S30": hls[["aoi", "datetime", "frac_valida"]],
}
ANOS = range(2020, 2026)

print("== Vistas limpas esperadas por pixel por mes (media 2020-2025, media das 4 AOIs) ==")
tab = {}
for nome, d in fontes.items():
    d = d[d.datetime.dt.year.isin(ANOS)]
    m = d.groupby([d.aoi, d.datetime.dt.month])["frac_valida"].sum() / len(ANOS)
    tab[nome] = m.groupby(level=1).mean()
T = pd.DataFrame(tab).round(1)
T.index.name = "mes"
print(T.to_string())


def p_sem_vista(d, ini_doy, fim_doy, janela=16):
    """Media de prod(1-f) em janelas deslizantes de 16 dias entre os dias-do-ano ini e fim."""
    out = []
    for aoi, g in d.groupby("aoi"):
        for ano in ANOS:
            gg = g[g.datetime.dt.year == ano]
            for s in range(ini_doy, fim_doy - janela + 1, 4):
                a = pd.Timestamp(ano, 1, 1) + pd.Timedelta(days=s - 1)
                w = gg[(gg.datetime >= a) & (gg.datetime < a + pd.Timedelta(days=janela))]
                out.append(np.prod(1 - w.frac_valida.values) if len(w) else 1.0)
    return float(np.mean(out))


print("\n== P(pixel passar 16 dias sem nenhuma vista limpa) - independencia entre cenas (limite otimista) ==")
for nome, d in fontes.items():
    print(f"  {nome:12s}  semeadura 15/jan-15/abr: {p_sem_vista(d, 15, 105):.0%}   seca 01/ago-31/out: {p_sem_vista(d, 213, 304):.0%}")


def maior_gap(d, limiar=0.6):
    linhas = []
    for aoi, g in d.groupby("aoi"):
        for ano in ANOS:
            a, b = pd.Timestamp(ano, 1, 15), pd.Timestamp(ano, 4, 15)
            dt = g[(g.datetime >= a) & (g.datetime <= b) & (g.frac_valida >= limiar)].datetime.sort_values()
            pts = [a] + list(dt) + [b]
            gaps = np.diff(pd.DatetimeIndex(pts)).astype("timedelta64[D]").astype(int)
            linhas.append({"aoi": aoi, "ano": ano, "maior_gap_dias": int(gaps.max()), "cenas_uteis": len(dt)})
    return pd.DataFrame(linhas)


print("\n== Maior intervalo sem cena util (>= 60% da AOI limpa) entre 15/jan e 15/abr ==")
for nome, d in fontes.items():
    G = maior_gap(d)
    print(f"  {nome:12s} mediana {G.maior_gap_dias.median():.0f} d | p90 {G.maior_gap_dias.quantile(.9):.0f} d | "
          f"anos-AOI com gap > 30 d: {(G.maior_gap_dias > 30).mean():.0%} | cenas uteis/estacao (mediana): {G.cenas_uteis.median():.0f}")
    if nome == "HLS L30+S30":
        print(G.pivot(index="ano", columns="aoi", values="maior_gap_dias").to_string())
