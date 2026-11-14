"""Utilitarios da Frente C (Landsat, Sentinel-2, HLS, SRTM): grade alvo por AOI, leitura de janela COG,
Mann-Kendall vetorizado e escolha de item por data."""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import numpy as np

# GDAL afinado para COG remoto
for k, v in {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "GDAL_HTTP_MULTIRANGE": "YES",
    "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.TIF,.tiff",
    "VSI_CACHE": "TRUE",
    "GDAL_CACHEMAX": "512",
    "GDAL_HTTP_MAX_RETRY": "5",
    "GDAL_HTTP_RETRY_DELAY": "2",
    "GDAL_HTTP_TIMEOUT": "60",
}.items():
    os.environ.setdefault(k, v)


def grade_aoi(nome: str, crs: str, res: float, meia: float = AOI_MEIA):
    """Grade alvo (transform, largura, altura) da AOI no CRS dado, alinhada a multiplos de res."""
    from rasterio.transform import from_origin
    from rasterio.warp import transform_bounds

    x0, y0, x1, y1 = transform_bounds("EPSG:4326", crs, *bbox_aoi(nome, meia))
    x0 = math.floor(x0 / res) * res
    y1 = math.ceil(y1 / res) * res
    w = int(math.ceil((x1 - x0) / res))
    h = int(math.ceil((y1 - y0) / res))
    return from_origin(x0, y1, res, res), w, h


def ler_na_grade(href: str, crs: str, transform, w: int, h: int, resampling="nearest", nodata=None):
    """Le um COG remoto reprojetado/reamostrado para a grade alvo (so baixa os blocos necessarios)."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.vrt import WarpedVRT

    rs = getattr(Resampling, resampling)
    with rasterio.open(href) as src:
        nd = src.nodata if nodata is None else nodata
        with WarpedVRT(src, crs=crs, transform=transform, width=w, height=h, resampling=rs,
                       src_nodata=nd, nodata=nd if nd is not None else 0) as vrt:
            a = vrt.read(1)
        escala = (src.scales or [1.0])[0]
        offset = (src.offsets or [0.0])[0]
    return a, nd, escala, offset


def fracao_cobertura(item_geom: dict, bbox) -> float:
    from shapely.geometry import box, shape

    b = box(*bbox)
    try:
        return shape(item_geom).intersection(b).area / b.area
    except Exception:
        return 0.0


def escolher_por_data(itens, bbox, chave_plataforma="platform"):
    """Para cada (data UTC, plataforma) fica o item que mais cobre a AOI (remove duplicatas de tiles/linhas vizinhas)."""
    melhor = {}
    for it in itens:
        k = (it.datetime.date().isoformat(), str(it.properties.get(chave_plataforma, "")).lower())
        f = fracao_cobertura(it.geometry, bbox)
        if k not in melhor or f > melhor[k][0]:
            melhor[k] = (f, it)
    return [v[1] for v in sorted(melhor.values(), key=lambda x: x[1].datetime)]


def mk_sen_vetorizado(y: np.ndarray, x: np.ndarray | None = None):
    """Mann-Kendall (sem correcao de empates) + Sen, vetorizado no ultimo eixo.
    y: (..., n). Retorna (sen_slope, z, p). NaN-tolerante (pares com NaN ignorados)."""
    from scipy.stats import norm

    n = y.shape[-1]
    if x is None:
        x = np.arange(n, dtype=float)
    i, j = np.triu_indices(n, 1)
    d = y[..., j] - y[..., i]
    dx = (x[j] - x[i]).astype(float)
    valido = ~np.isnan(d)
    s = np.nansum(np.sign(d), axis=-1)
    nval = (~np.isnan(y)).sum(axis=-1).astype(float)
    var = nval * (nval - 1) * (2 * nval + 5) / 18.0
    z = np.where(s > 0, (s - 1) / np.sqrt(var), np.where(s < 0, (s + 1) / np.sqrt(var), 0.0))
    z = np.where(nval >= 4, z, np.nan)
    p = 2 * (1 - norm.cdf(np.abs(z)))
    slopes = np.where(valido, d / dx, np.nan)
    sen = np.nanmedian(slopes, axis=-1)
    return sen, z, p
