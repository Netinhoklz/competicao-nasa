"""Gera MANIFESTO.json de IMERG e ERA5 a partir do que esta em disco."""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")


def resumo(arqs):
    return [{"arquivo": a.name, "MB": round(a.stat().st_size / 1e6, 2)} for a in arqs]


im = DADOS / "imerg"
ce = sorted(im.glob("imerg_ce_diario_*.nc"))
ne = sorted(im.glob("imerg_ne_diario_*.nc"))
pcn = sorted((im / "pc_nativo").glob("*.nc"))
per = lambda arqs: (str(xr.open_dataset(arqs[0]).time.values[0])[:10], str(xr.open_dataset(arqs[-1]).time.values[-1])[:10]) if arqs else None  # noqa
registrar_manifesto("imerg", {
    "base": "GPM IMERG (NASA/JAXA)",
    "rotas": {
        "diario_V07": "NASA POWER API, parametro IMERG_PRECTOT, time-standard=UTC, resolucao nativa 0,1 grau "
                      "(https://power.larc.nasa.gov/api/temporal/daily/regional)",
        "meia_hora_V06": "Microsoft Planetary Computer, colecao gpm-imerg-hhr (abfs://imerg/gpm-imerg-hhr.zarr), precipitationCal",
        "oficial_nao_usada": "GES DISC GPM_3IMERGDF/DL/DE V07 - exige Earthdata Login (Final ate 2025-09; Early/Late ate D-1)",
    },
    "recortes": {"CE": BBOX_CE, "NE": BBOX_NE},
    "periodo_diario_CE": per(ce), "periodo_diario_NE": per(ne),
    "amostra_meia_hora": [a.name for a in pcn],
    "chunking_pc": "precipitationCal (time=12, lon=3600, lat=1800) ~52 MB/chunk lz4: chunk = globo inteiro 6 h -> so amostra",
    "limites_power": "regional exige caixa >= 2x2 graus; limite de egresso por requisicao; 429 sob carga",
    "tamanho_total_MB": round(tamanho_pasta(im) / 1e6, 1),
    "arquivos": resumo(ce) + resumo(ne) + resumo(pcn) + resumo([im / "validacao_global_power_imerg.csv"]),
    "scripts": ["scripts/baixar_imerg.py", "scripts/derivar_imerg.py"],
    "derivados": ["derivados/imerg_ce_mensal.parquet", "derivados/imerg_ne_mensal.parquet", "derivados/imerg_aoi_mensal.parquet"],
})
e5 = DADOS / "era5"
dd = sorted(e5.glob("era5_ne_diario_*.nc"))
registrar_manifesto("era5", {
    "base": "ERA5 (ECMWF/Copernicus)",
    "rota": "Microsoft Planetary Computer, colecao era5-pds (Zarr mensal por variavel, horario, 0,25 grau), 1979-01 a 2020-12",
    "rota_oficial_nao_usada": "Copernicus CDS (exige chave .cdsapirc) - necessaria para 2021+",
    "chunking": "(time=372, lat=150, lon=150) ~5,5 MB; Nordeste cabe em 1 bloco espacial -> ~11 MB/mes/variavel",
    "recorte": BBOX_NE, "dia": "horario local UTC-3 (soma/media com contagem de horas; dias incompletos descartados)",
    "variaveis_diarias": ["t2m", "tmax", "tmin", "d2m", "tp (mm)", "ssrd (MJ m-2)", "ws10", "ws10_max"],
    "derivadas": ["et0 FAO-56 PM", "vpd", "ur", "gdd10"],
    "periodo": per(dd) if False else (dd[0].stem[-4:], dd[-1].stem[-4:]) if dd else None,
    "tamanho_total_MB": round(tamanho_pasta(e5) / 1e6, 1),
    "arquivos": resumo(dd) + resumo(sorted(e5.glob("era5_global_*.nc"))) + resumo(sorted(e5.glob("era5_ne_*grade*.nc"))) +
    resumo(sorted(e5.glob("era5_ne_derivados*.nc"))),
    "scripts": ["scripts/baixar_era5.py", "scripts/derivar_era5.py"],
    "derivados": ["derivados/era5_ce_mensal.parquet", "derivados/era5_ne_mensal.parquet", "derivados/era5_aoi_mensal.parquet"],
})
print("manifestos gravados")
