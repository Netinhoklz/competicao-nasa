"""Ingestao estatica do condado piloto: talhoes x SSURGO x historico CDL x terreno SRTM (NASADEM).

Etapas (cada uma grava cache em disco e e pulada se o arquivo ja existir, salvo com --forcar):

  limite   limite do condado (Census TIGERweb) ............................ data/raw/limite/
  cdl      historico anual do CDL 30 m (CropScape por FIPS; Planetary Computer como plano B)
           empilhado na grade mestre (EPSG:5070, 30 m) ..................... data/interim/cdl_pilha_30m.tif
  terreno  NASADEM (SRTM reprocessado) via STAC do Planetary Computer -> elevacao, declividade,
           TWI e fator LS (RUSLE), com folga para a area de contribuicao ... data/processed/terreno_30m.tif
  solo     SSURGO via Soil Data Access: poligonos + horizontes + muaggatt,
           agregados por mukey em camadas (0-30, 0-100 cm) ................. data/interim/ssurgo_*.parquet
  talhoes  poligonos USDA Crop Sequence Boundaries (ou quadriculas, plano B) data/processed/talhoes.parquet
  cruzar   CDL, terreno e solo por talhao -> tabelas analiticas ............ data/processed/talhao_*.parquet

Saidas finais (chave id_talhao, periodo = ano-safra do CDL):
  talhoes.parquet              GeoParquet com a geometria (EPSG:5070) - so para mapas e para as proximas extracoes
  talhao_estatico.parquet      uma linha por talhao: solo, terreno e resumo da rotacao baseline
  talhao_periodo_cdl.parquet   uma linha por talhao x ano: cultura dominante e pureza
  talhao_periodo_base.parquet  juncao das duas: semente da tabela analitica que os modulos de sensoriamento completam

Uso:
  python -m src.ingestion.stac_and_soil                       # tudo
  python -m src.ingestion.stac_and_soil --etapas solo cruzar  # so algumas etapas
  python -m src.ingestion.stac_and_soil --talhoes grade       # sem baixar o CSB nacional (3,7 GB)

Regra de desempenho: nada de laco por pixel ou por linha. Rasters sao tratados como arrays (NumPy/numba via pysheds),
estatistica zonal com exactextract (C++), sobreposicao vetorial com GeoPandas (STRtree) e agregacoes com Polars.
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import polars as pl
import pyogrio
import rasterio
import requests
import rioxarray  # noqa: F401  (registra o acessor .rio)
import xarray as xr
from affine import Affine
from exactextract import exact_extract
from rasterio.crs import CRS
from rasterio.enums import Resampling
from requests.adapters import HTTPAdapter
from rioxarray.merge import merge_arrays
from shapely import box
from urllib3.util.retry import Retry

from src.config import carregar_config

log = logging.getLogger("ingestion.stac_and_soil")

CRS_GEO = "EPSG:4326"
ETAPAS = ("limite", "cdl", "terreno", "solo", "talhoes", "cruzar")

# --------------------------------------------------------------------------------------------------------------------
# Legenda do CDL (codigos oficiais do NASS) e agrupamento agronomico usado pelo motor de rotacao
# --------------------------------------------------------------------------------------------------------------------
CDL_CLASSES: dict[int, str] = {
    1: "Corn", 2: "Cotton", 3: "Rice", 4: "Sorghum", 5: "Soybeans", 6: "Sunflower", 10: "Peanuts", 11: "Tobacco",
    12: "Sweet Corn", 13: "Pop or Orn Corn", 14: "Mint", 21: "Barley", 22: "Durum Wheat", 23: "Spring Wheat",
    24: "Winter Wheat", 25: "Other Small Grains", 26: "Dbl Crop WinWht/Soybeans", 27: "Rye", 28: "Oats", 29: "Millet",
    30: "Speltz", 31: "Canola", 32: "Flaxseed", 33: "Safflower", 34: "Rape Seed", 35: "Mustard", 36: "Alfalfa",
    37: "Other Hay/Non Alfalfa", 38: "Camelina", 39: "Buckwheat", 41: "Sugarbeets", 42: "Dry Beans", 43: "Potatoes",
    44: "Other Crops", 47: "Misc Vegs & Fruits", 53: "Peas", 58: "Clover/Wildflowers", 59: "Sod/Grass Seed",
    60: "Switchgrass", 61: "Fallow/Idle Cropland", 63: "Forest", 64: "Shrubland", 65: "Barren", 81: "Clouds/No Data",
    82: "Developed", 83: "Water", 87: "Wetlands", 88: "Nonag/Undefined", 92: "Aquaculture", 111: "Open Water",
    112: "Perennial Ice/Snow", 121: "Developed/Open Space", 122: "Developed/Low Intensity",
    123: "Developed/Med Intensity", 124: "Developed/High Intensity", 131: "Barren", 141: "Deciduous Forest",
    142: "Evergreen Forest", 143: "Mixed Forest", 152: "Shrubland", 176: "Grassland/Pasture", 190: "Woody Wetlands",
    195: "Herbaceous Wetlands", 205: "Triticale", 225: "Dbl Crop WinWht/Corn", 226: "Dbl Crop Oats/Corn",
    228: "Dbl Crop Triticale/Corn", 236: "Dbl Crop WinWht/Sorghum", 237: "Dbl Crop Barley/Corn",
    240: "Dbl Crop Soybeans/Oats", 241: "Dbl Crop Corn/Soybeans", 254: "Dbl Crop Barley/Soybeans",
}
_GRUPOS: dict[str, tuple[int, ...]] = {
    "milho": (1, 12, 13, 225, 226, 228, 237),
    "soja": (5, 26, 240, 254),
    "milho_soja_dupla": (241,),
    "sorgo": (4, 236),
    "cereal_inverno": (21, 22, 23, 24, 25, 27, 28, 29, 30, 205),
    "forrageira": (36, 37, 58, 59, 60),
    "pastagem": (176,),
    "pousio": (61,),
    "outra_lavoura": (2, 3, 6, 10, 11, 14, 31, 32, 33, 34, 35, 38, 39, 41, 42, 43, 44, 47, 53),
}
CDL_GRUPO: dict[int, str] = {c: g for g, cods in _GRUPOS.items() for c in cods}
# Tudo que nao e lavoura, forrageira ou pousio (vegetacao nativa, agua, urbano, nuvem)
CDL_NAO_AGRICOLA: tuple[int, ...] = (63, 64, 65, 81, 82, 83, 87, 88, 92, 111, 112, 121, 122, 123, 124, 131, 141, 142,
                                     143, 152, 190, 195)

# Classes de drenagem do SSURGO em ordem (1 = excessivamente drenado ... 7 = muito mal drenado)
DRENAGEM_ORD = {
    "Excessively drained": 1, "Somewhat excessively drained": 2, "Well drained": 3, "Moderately well drained": 4,
    "Somewhat poorly drained": 5, "Poorly drained": 6, "Very poorly drained": 7,
}
# Variaveis de horizonte agregadas por espessura (coluna SDA -> nome de saida)
HORIZONTE_VARS = {
    "claytotal_r": "argila_pct", "sandtotal_r": "areia_pct", "silttotal_r": "silte_pct", "om_r": "mo_pct",
    "awc_r": "awc_cm_cm", "ksat_r": "ksat_um_s", "dbthirdbar_r": "densidade_g_cm3", "ph1to1h2o_r": "ph",
    "cec7_r": "ctc_cmol_kg", "kwfact": "fator_k",
}


# --------------------------------------------------------------------------------------------------------------------
# Utilitarios
# --------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Grade:
    """Grade raster alinhada (a grade mestre e a do CDL)."""
    crs: str
    transform: Affine
    width: int
    height: int

    @property
    def res(self) -> float:
        return self.transform.a

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        x0, y1 = self.transform.c, self.transform.f
        return x0, y1 - self.height * self.res, x0 + self.width * self.res, y1

    def expandir(self, n_px: int) -> "Grade":
        t = self.transform
        return Grade(self.crs, Affine(t.a, 0, t.c - n_px * t.a, 0, t.e, t.f + n_px * t.a),
                     self.width + 2 * n_px, self.height + 2 * n_px)

    @classmethod
    def de_raster(cls, caminho: Path) -> "Grade":
        with rasterio.open(caminho) as r:
            return cls(r.crs.to_string(), r.transform, r.width, r.height)


def _sessao_http(retries: int = 5) -> requests.Session:
    s = requests.Session()
    r = Retry(total=retries, backoff_factor=1.5, status_forcelist=(429, 500, 502, 503, 504),
              allowed_methods=frozenset({"GET", "HEAD", "POST"}))
    s.mount("https://", HTTPAdapter(max_retries=r, pool_maxsize=16))
    s.headers["User-Agent"] = "agro-stress-test-etl/0.1"
    return s


def _baixar_arquivo(s: requests.Session, url: str, destino: Path, timeout: int = 300) -> Path:
    """Download em streaming para .part e troca atomica no fim."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".part")
    with s.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for bloco in r.iter_content(1 << 20):
                f.write(bloco)
    tmp.replace(destino)
    return destino


def _baixar_em_blocos(s: requests.Session, url: str, destino: Path, bloco_mb: int = 64, paralelo: int = 8) -> Path:
    """Download grande por HTTP Range em blocos paralelos. Cada bloco vira um arquivo .partNNNN que so e aceito com o
    tamanho exato, entao uma interrupcao retoma de onde parou. (O servidor do NASS responde 500 a um GET completo
    do CSB nacional, mas atende Range.)"""
    total = int(s.head(url, allow_redirects=True, timeout=120).headers["Content-Length"])
    tam = bloco_mb << 20
    faixas = [(i, ini, min(ini + tam, total) - 1) for i, ini in enumerate(range(0, total, tam))]
    destino.parent.mkdir(parents=True, exist_ok=True)

    def baixar(faixa: tuple[int, int, int]) -> Path:
        i, ini, fim = faixa
        p = destino.with_name(f"{destino.name}.part{i:04d}")
        if p.exists() and p.stat().st_size == fim - ini + 1:
            return p
        for tentativa in range(6):
            try:
                r = s.get(url, headers={"Range": f"bytes={ini}-{fim}"}, timeout=600)
                if r.status_code == 206 and len(r.content) == fim - ini + 1:
                    p.write_bytes(r.content)
                    return p
                raise RuntimeError(f"HTTP {r.status_code}, {len(r.content)} bytes")
            except Exception as e:
                log.warning("bloco %d tentativa %d: %s", i, tentativa + 1, e)
                time.sleep(5 * (tentativa + 1))
        raise RuntimeError(f"bloco {i} falhou")

    log.info("Download em %d blocos de %d MB (%.2f GB)", len(faixas), bloco_mb, total / 1e9)
    with ThreadPoolExecutor(paralelo) as ex:
        partes = list(ex.map(baixar, faixas))
    tmp = destino.with_suffix(destino.suffix + ".part")
    with open(tmp, "wb") as f:
        for p in partes:
            with open(p, "rb") as src:
                shutil.copyfileobj(src, f, 16 << 20)
    if tmp.stat().st_size != total:
        raise RuntimeError(f"tamanho final {tmp.stat().st_size} != {total}")
    tmp.replace(destino)
    for p in partes:
        p.unlink()
    return destino


def _gravar_tif(caminho: Path, arr: np.ndarray, grade: Grade, nodata, descricoes: list[str] | None = None) -> Path:
    arr = arr if arr.ndim == 3 else arr[None]
    caminho.parent.mkdir(parents=True, exist_ok=True)
    pred = 3 if arr.dtype.kind == "f" else 2
    perfil = dict(driver="GTiff", height=grade.height, width=grade.width, count=arr.shape[0], dtype=arr.dtype,
                  crs=grade.crs, transform=grade.transform, nodata=nodata, compress="deflate", predictor=pred,
                  tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(caminho, "w", **perfil) as d:
        d.write(arr)
        for i, desc in enumerate(descricoes or [], start=1):
            d.set_band_description(i, desc)
    return caminho


def _gravar_manifesto(cfg: dict, etapa: str, info: dict) -> None:
    p = cfg["_caminhos"].processed / "manifesto_stac_and_soil.json"
    atual = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    atual[etapa] = {**info, "gerado_em": datetime.now().isoformat(timespec="seconds")}
    p.write_text(json.dumps(atual, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


class _Cronometro:
    def __init__(self, rotulo: str):
        self.rotulo = rotulo

    def __enter__(self):
        self.t0 = time.perf_counter()
        log.info("[%s] inicio", self.rotulo)
        return self

    def __exit__(self, *exc):
        log.info("[%s] %.1fs", self.rotulo, time.perf_counter() - self.t0)


# --------------------------------------------------------------------------------------------------------------------
# 1. Limite do condado
# --------------------------------------------------------------------------------------------------------------------
TIGERWEB = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query"


def baixar_limite_condado(cfg: dict, s: requests.Session, forcar: bool = False) -> gpd.GeoDataFrame:
    fips = cfg["condado"]["fips"]
    destino = cfg["_caminhos"].raw / "limite" / f"condado_{fips}.geojson"
    if destino.exists() and not forcar:
        return gpd.read_file(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = s.get(TIGERWEB, params={"where": f"GEOID='{fips}'", "outFields": "GEOID,NAME,STATE,COUNTY",
                                    "outSR": 4326, "f": "geojson"}, timeout=120)
        r.raise_for_status()
        gdf = gpd.GeoDataFrame.from_features(r.json()["features"], crs=CRS_GEO)
        if gdf.empty:
            raise ValueError(f"TIGERweb nao achou o FIPS {fips}")
        fonte = "Census TIGERweb State_County/1"
    except Exception as e:  # rede/servico fora: usa a caixa da configuracao
        log.warning("TIGERweb falhou (%s); usando bbox_wgs84 da configuracao", e)
        gdf = gpd.GeoDataFrame({"GEOID": [fips], "NAME": [cfg["condado"]["nome"]]},
                               geometry=[box(*cfg["condado"]["bbox_wgs84"])], crs=CRS_GEO)
        fonte = "bbox_wgs84 (config)"
    gdf.to_file(destino, driver="GeoJSON")
    _gravar_manifesto(cfg, "limite", {"fonte": fonte, "arquivo": destino, "bounds_wgs84": gdf.total_bounds})
    return gdf


# --------------------------------------------------------------------------------------------------------------------
# 2. Historico CDL
# --------------------------------------------------------------------------------------------------------------------
CROPSCAPE = "https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLFile"


def _cdl_cropscape(s: requests.Session, ano: int, fips: str, destino: Path) -> Path:
    """CropScape recorta o CDL pelo FIPS no servidor e devolve a URL do GeoTIFF (EPSG:5070, 30 m)."""
    r = s.get(CROPSCAPE, params={"year": ano, "fips": fips}, timeout=180)
    r.raise_for_status()
    if "<returnURL>" not in r.text:
        raise RuntimeError(f"CropScape sem arquivo para {ano}: {r.text[:200]}")
    url = r.text.split("<returnURL>")[1].split("</returnURL>")[0]
    _baixar_arquivo(s, url, destino)
    with rasterio.open(destino) as t:  # valida o GeoTIFF
        if t.count < 1:
            raise RuntimeError("GeoTIFF vazio")
    return destino


def _cdl_planetary(cfg: dict, ano: int, limite: gpd.GeoDataFrame, destino: Path) -> Path:
    """Plano B: colecao usda-cdl do Planetary Computer (2008-2021), recortada pela caixa do condado."""
    import planetary_computer
    import pystac_client

    cli = pystac_client.Client.open(cfg["terreno"]["stac_url"], modifier=planetary_computer.sign_inplace)
    bbox = limite.to_crs(CRS_GEO).total_bounds.tolist()
    itens = [i for i in cli.search(collections=["usda-cdl"], bbox=bbox, datetime=str(ano)).items()
             if i.properties.get("usda_cdl:type") == "cropland"]
    if not itens:
        raise RuntimeError(f"Planetary Computer sem CDL para {ano}")
    b5070 = limite.to_crs(cfg["grade"]["crs"]).total_bounds
    partes = [rioxarray.open_rasterio(i.assets["cropland"].href, masked=False).rio.clip_box(*b5070) for i in itens]
    da = merge_arrays(partes) if len(partes) > 1 else partes[0]
    da.rio.to_raster(destino, compress="deflate", tiled=True)
    return destino


def baixar_cdl(cfg: dict, limite: gpd.GeoDataFrame, s: requests.Session, forcar: bool = False) -> dict[int, Path]:
    fips = cfg["condado"]["fips"]
    pasta = cfg["_caminhos"].raw / "cdl"
    pasta.mkdir(parents=True, exist_ok=True)

    def um_ano(ano: int) -> tuple[int, Path | None, str]:
        destino = pasta / f"CDL_{ano}_{fips}.tif"
        if destino.exists() and not forcar:
            return ano, destino, "cache"
        for rota in cfg["cdl"]["rotas"]:
            try:
                if rota == "cropscape":
                    return ano, _cdl_cropscape(s, ano, fips, destino), rota
                if rota == "planetary_computer":
                    return ano, _cdl_planetary(cfg, ano, limite, destino), rota
            except Exception as e:
                log.warning("CDL %s via %s falhou: %s", ano, rota, str(e)[:160])
        return ano, None, "falhou"

    with ThreadPoolExecutor(cfg["cdl"]["downloads_paralelos"]) as ex:
        resultado = list(ex.map(um_ano, cfg["cdl"]["anos"]))
    ok = {a: p for a, p, _ in resultado if p is not None}
    for a, _, rota in resultado:
        log.info("CDL %s: %s", a, rota)
    if not ok:
        raise RuntimeError("Nenhum ano do CDL foi obtido")
    _gravar_manifesto(cfg, "cdl_download", {"fips": fips, "rotas": {a: r for a, _, r in resultado}})
    return dict(sorted(ok.items()))


def empilhar_cdl(cfg: dict, arquivos: dict[int, Path], forcar: bool = False) -> tuple[Path, Grade]:
    """Empilha os anos numa unica grade (a do ano mais recente). Anos com grade diferente sao reamostrados
    por vizinho mais proximo (classe categorica nao pode ser interpolada)."""
    destino = cfg["_caminhos"].interim / "cdl_pilha_30m.tif"
    if destino.exists() and not forcar:
        return destino, Grade.de_raster(destino)
    anos = list(arquivos)

    def abrir(p: Path) -> xr.DataArray:
        # O CropScape nao declara nodata, mas 0 = fora do condado. Sem declarar, o GDAL troca 0 por 1 (milho!)
        # ao reamostrar.
        return rioxarray.open_rasterio(p).squeeze("band", drop=True).rio.write_nodata(0)

    ref = abrir(arquivos[anos[-1]])
    if ref.rio.crs != CRS.from_user_input(cfg["grade"]["crs"]):  # comparacao semantica (WKT x EPSG)
        ref = ref.rio.reproject(cfg["grade"]["crs"], resolution=cfg["grade"]["resolucao_m"],
                                resampling=Resampling.nearest, nodata=0)
    camadas, reamostrados = [], []
    for a in anos:
        da = abrir(arquivos[a])
        if da.shape != ref.shape or da.rio.transform() != ref.rio.transform() or da.rio.crs != ref.rio.crs:
            # ex.: 2008-2009 vem deslocados meio pixel (15 m) em relacao aos anos seguintes
            da = da.rio.reproject_match(ref, resampling=Resampling.nearest, nodata=0)
            reamostrados.append(a)
        camadas.append(da.values.astype(np.uint8))
    if reamostrados:
        log.info("CDL reamostrado para a grade de %s: %s", anos[-1], reamostrados)
    pilha = np.stack(camadas)
    grade = Grade(cfg["grade"]["crs"], ref.rio.transform(), ref.rio.width, ref.rio.height)
    _gravar_tif(destino, pilha, grade, nodata=0, descricoes=[str(a) for a in anos])
    _gravar_manifesto(cfg, "cdl", {"arquivo": destino, "anos": anos, "shape": pilha.shape, "crs": grade.crs,
                                   "reamostrados_vizinho_proximo": reamostrados})
    return destino, grade


def anos_da_pilha(caminho: Path) -> list[int]:
    with rasterio.open(caminho) as r:
        return [int(d) for d in r.descriptions]


# --------------------------------------------------------------------------------------------------------------------
# 3. Terreno (NASADEM / SRTM via STAC)
# --------------------------------------------------------------------------------------------------------------------
def baixar_dem(cfg: dict, grade: Grade, forcar: bool = False) -> tuple[Path, Grade, int]:
    """Mosaico NASADEM reprojetado (bilinear) para a grade mestre expandida pela folga."""
    import planetary_computer
    import pystac_client

    folga_px = int(np.ceil(cfg["terreno"]["folga_m"] / grade.res))
    gx = grade.expandir(folga_px)
    destino = cfg["_caminhos"].interim / "dem_nasadem_30m_folga.tif"
    if destino.exists() and not forcar:
        return destino, gx, folga_px
    bbox_geo = gpd.GeoSeries([box(*gx.bounds)], crs=gx.crs).to_crs(CRS_GEO).total_bounds
    bbox_leitura = (bbox_geo[0] - 0.01, bbox_geo[1] - 0.01, bbox_geo[2] + 0.01, bbox_geo[3] + 0.01)
    cli = pystac_client.Client.open(cfg["terreno"]["stac_url"], modifier=planetary_computer.sign_inplace)
    itens = list(cli.search(collections=[cfg["terreno"]["colecao_stac"]], bbox=bbox_leitura).items())
    if not itens:
        raise RuntimeError("Nenhum tile NASADEM para o condado")
    log.info("NASADEM: %d tiles", len(itens))
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MAX_RETRY="5", GDAL_HTTP_RETRY_DELAY="2"):
        partes = [rioxarray.open_rasterio(i.assets["elevation"].href, masked=True).squeeze("band", drop=True)
                  .rio.clip_box(*bbox_leitura) for i in itens]
        mosaico = merge_arrays(partes) if len(partes) > 1 else partes[0]
        dem = mosaico.astype("float32").rio.reproject(gx.crs, shape=(gx.height, gx.width), transform=gx.transform,
                                                      resampling=Resampling.bilinear, nodata=np.nan)
    z = dem.values.astype(np.float32)
    if np.isnan(z).any():
        log.warning("DEM com %.3f%% de lacunas", 100 * np.isnan(z).mean())
    _gravar_tif(destino, z, gx, nodata=np.nan, descricoes=["elev_m"])
    _gravar_manifesto(cfg, "dem", {"colecao": cfg["terreno"]["colecao_stac"], "tiles": [i.id for i in itens],
                                   "arquivo": destino, "folga_px": folga_px})
    return destino, gx, folga_px


def derivar_terreno(cfg: dict, dem_path: Path, gx: Grade, folga_px: int, grade: Grade, forcar: bool = False) -> Path:
    """Declividade (graus), TWI = ln(a / tan b) e fator LS de Moore & Burch (1986), recortados para a grade mestre.

    Hidrologia com pysheds (numba): preenchimento de pits e depressoes, resolucao de planos, D8 e acumulacao.
    a = area especifica de contribuicao (m2 por metro de largura de celula).
    """
    from pysheds.grid import Grid

    destino = cfg["_caminhos"].processed / "terreno_30m.tif"
    if destino.exists() and not forcar:
        return destino
    res = gx.res
    g = Grid.from_raster(str(dem_path))
    dem = g.read_raster(str(dem_path))
    corrigido = g.resolve_flats(g.fill_depressions(g.fill_pits(dem)))
    acc = np.asarray(g.accumulation(g.flowdir(corrigido)), dtype=np.float64)  # em numero de celulas

    z = np.asarray(dem, dtype=np.float64)
    gy, gxx = np.gradient(z, res)  # metros por metro
    tan_b = np.hypot(gxx, gy)
    beta = np.arctan(tan_b)
    a_esp = acc * res  # (celulas * res^2) / res
    twi = np.log(a_esp / np.maximum(tan_b, 1e-3))
    rampa = np.minimum(a_esp, cfg["terreno"]["ls_rampa_max_m"])
    ls = (rampa / 22.13) ** 0.4 * (np.sin(beta) / 0.0896) ** 1.3

    recorte = (slice(folga_px, folga_px + grade.height), slice(folga_px, folga_px + grade.width))
    bandas = np.stack([z, np.degrees(beta), twi, ls])[:, recorte[0], recorte[1]].astype(np.float32)
    bandas[:, np.isnan(bandas[0])] = np.nan
    nomes = ["elev_m", "declividade_graus", "twi", "fator_ls"]
    _gravar_tif(destino, bandas, grade, nodata=np.nan, descricoes=nomes)
    _gravar_manifesto(cfg, "terreno", {"arquivo": destino, "bandas": nomes,
                                       "metodo": "pysheds fill_pits+fill_depressions+resolve_flats, D8; "
                                                 "TWI=ln(a/tan b); LS Moore&Burch 1986"})
    return destino


# --------------------------------------------------------------------------------------------------------------------
# 4. SSURGO (Soil Data Access)
# --------------------------------------------------------------------------------------------------------------------
def _sda(s: requests.Session, url: str, sql: str) -> pl.DataFrame:
    """Executa SQL no SDA. O servico devolve tudo como texto: a tipagem fica para quem chama."""
    r = s.post(url, json={"query": sql, "format": "JSON+COLUMNNAME"}, timeout=600)
    r.raise_for_status()
    tabela = r.json().get("Table", [])
    if not tabela:
        return pl.DataFrame()
    return pl.DataFrame(tabela[1:], schema=tabela[0], orient="row")


def baixar_ssurgo_poligonos(cfg: dict, s: requests.Session, forcar: bool = False) -> gpd.GeoDataFrame:
    area = cfg["condado"]["ssurgo_areasymbol"]
    destino = cfg["_caminhos"].interim / f"ssurgo_{area}_mupolygon.parquet"
    if destino.exists() and not forcar:
        return gpd.read_parquet(destino)
    url, lote = cfg["solo"]["sda_url"], cfg["solo"]["poligonos_por_lote"]
    n = int(_sda(s, url, f"SELECT COUNT(*) AS n FROM mupolygon WHERE areasymbol = '{area}'")["n"][0])
    log.info("SSURGO %s: %d poligonos em lotes de %d", area, n, lote)

    def pagina(ini: int) -> pl.DataFrame:
        return _sda(s, url, f"""SELECT mupolygonkey, mukey, mupolygongeo.STAsText() AS wkt FROM mupolygon
                                WHERE areasymbol = '{area}' ORDER BY mupolygonkey
                                OFFSET {ini} ROWS FETCH NEXT {lote} ROWS ONLY""")

    with ThreadPoolExecutor(cfg["solo"]["consultas_paralelas"]) as ex:
        df = pl.concat(list(ex.map(pagina, range(0, n, lote))))
    if df.height != n:
        raise RuntimeError(f"SSURGO incompleto: {df.height}/{n} poligonos")
    gdf = gpd.GeoDataFrame({"mupolygonkey": df["mupolygonkey"].to_numpy(), "mukey": df["mukey"].to_numpy()},
                           geometry=gpd.GeoSeries.from_wkt(df["wkt"].to_numpy(), crs=CRS_GEO))
    gdf = gdf.to_crs(cfg["grade"]["crs"])
    gdf["geometry"] = gdf.make_valid()
    gdf.to_parquet(destino)
    _gravar_manifesto(cfg, "ssurgo_poligonos", {"areasymbol": area, "n": n, "arquivo": destino})
    return gdf


def agregar_horizontes(h: pl.DataFrame, camadas: list[list[int]]) -> pl.DataFrame:
    """Media ponderada por espessura dentro de cada camada (por componente) e depois pelo % do componente (por mukey).
    Tambem calcula a agua disponivel da camada (cm) = soma(awc * espessura)."""
    partes = []
    for topo, base in camadas:
        sufixo = f"_{topo}_{base}"
        esp = (pl.min_horizontal(pl.col("hzdepb_r"), pl.lit(base)) - pl.max_horizontal(pl.col("hzdept_r"), pl.lit(topo))
               ).clip(lower_bound=0).alias("esp")
        hh = h.with_columns(esp).filter(pl.col("esp") > 0)
        por_comp = hh.group_by(["mukey", "cokey", "comppct_r"]).agg(
            *[((pl.col(v) * pl.col("esp")).sum() / pl.col("esp").filter(pl.col(v).is_not_null()).sum()).alias(nome)
              for v, nome in HORIZONTE_VARS.items()],
            (pl.col("awc_r") * pl.col("esp")).sum().alias("cad_cm"),
        )
        cols = [*HORIZONTE_VARS.values(), "cad_cm"]
        por_mukey = por_comp.group_by("mukey").agg(
            *[((pl.col(c) * pl.col("comppct_r")).sum() / pl.col("comppct_r").filter(pl.col(c).is_not_null()).sum())
              .alias(c + sufixo) for c in cols]
        )
        partes.append(por_mukey.with_columns(pl.selectors.float().fill_nan(None)))  # 0/0 (sem horizonte) -> nulo
    out = partes[0]
    for p in partes[1:]:
        out = out.join(p, on="mukey", how="full", coalesce=True)
    return out


def baixar_ssurgo_atributos(cfg: dict, s: requests.Session, forcar: bool = False) -> pl.DataFrame:
    area = cfg["condado"]["ssurgo_areasymbol"]
    destino = cfg["_caminhos"].interim / f"ssurgo_{area}_mukey.parquet"
    if destino.exists() and not forcar:
        return pl.read_parquet(destino)
    url = cfg["solo"]["sda_url"]
    hvars = ", ".join(f"h.{v}" for v in HORIZONTE_VARS)
    horiz = _sda(s, url, f"""
        SELECT c.mukey, c.cokey, c.comppct_r, c.majcompflag, c.compname, c.hydricrating, c.tfact,
               h.hzdept_r, h.hzdepb_r, {hvars}
        FROM legend l JOIN mapunit mu ON mu.lkey = l.lkey JOIN component c ON c.mukey = mu.mukey
        LEFT JOIN chorizon h ON h.cokey = c.cokey
        WHERE l.areasymbol = '{area}'""")
    agreg = _sda(s, url, f"""
        SELECT ma.mukey, ma.muname, ma.drclassdcd, ma.hydgrpdcd, ma.aws0100wta, ma.aws0150wta, ma.slopegradwta,
               ma.niccdcd, ma.iccdcd, ma.wtdepannmin
        FROM legend l JOIN mapunit mu ON mu.lkey = l.lkey JOIN muaggatt ma ON ma.mukey = mu.mukey
        WHERE l.areasymbol = '{area}'""")
    num = ["comppct_r", "tfact", "hzdept_r", "hzdepb_r", *HORIZONTE_VARS]
    horiz = horiz.with_columns(pl.col(num).cast(pl.Float64, strict=False))
    camadas = agregar_horizontes(horiz, cfg["solo"]["camadas_cm"])

    comp = horiz.unique(["mukey", "cokey"]).with_columns(
        (pl.col("hydricrating") == "Yes").cast(pl.Float64).alias("hidrico"))
    por_comp = comp.group_by("mukey").agg(
        ((pl.col("hidrico") * pl.col("comppct_r")).sum() / pl.col("comppct_r").sum()).alias("frac_hidrico"),
        pl.col("compname").sort_by("comppct_r", descending=True).first().alias("componente_dominante"),
        pl.col("tfact").sort_by("comppct_r", descending=True).first().alias("fator_t"),
    )
    agreg = agreg.with_columns(
        pl.col(["aws0100wta", "aws0150wta", "slopegradwta", "wtdepannmin"]).cast(pl.Float64, strict=False),
        pl.col(["niccdcd", "iccdcd"]).cast(pl.Int8, strict=False),
        pl.col("drclassdcd").replace_strict(DRENAGEM_ORD, default=None, return_dtype=pl.Int8).alias("drenagem_ord"),
        pl.col("hydgrpdcd").str.slice(0, 1).alias("grupo_hidrologico"),
    ).rename({"drclassdcd": "drenagem_classe", "aws0100wta": "cad_0_100_muaggatt_cm",
              "aws0150wta": "cad_0_150_muaggatt_cm", "slopegradwta": "declividade_ssurgo_pct",
              "niccdcd": "capacidade_uso_sequeiro", "iccdcd": "capacidade_uso_irrigado",
              "wtdepannmin": "lencol_min_cm", "hydgrpdcd": "grupo_hidrologico_completo"})
    props = agreg.join(camadas, on="mukey", how="left").join(por_comp, on="mukey", how="left")
    props.write_parquet(destino)
    _gravar_manifesto(cfg, "ssurgo_atributos", {"areasymbol": area, "mukeys": props.height,
                                                "camadas_cm": cfg["solo"]["camadas_cm"], "arquivo": destino})
    return props


# --------------------------------------------------------------------------------------------------------------------
# 5. Talhoes
# --------------------------------------------------------------------------------------------------------------------
def _talhoes_csb(cfg: dict, limite: gpd.GeoDataFrame, s: requests.Session) -> gpd.GeoDataFrame:
    """USDA Crop Sequence Boundaries. O .gdb nacional e um unico .gdbtable de 5,2 GB comprimido por deflate, que nao
    admite leitura aleatoria por HTTP. Por isso: baixa o zip uma vez (retomavel), extrai o .gdb e le so a caixa do
    condado pelo indice espacial. O recorte do condado fica em cache; o .gdb extraido e apagado no fim."""
    zip_local = cfg["talhoes"]["csb_zip_local"]
    zp = Path(zip_local) if zip_local else cfg["_caminhos"].raw / "csb" / cfg["talhoes"]["csb_url"].rsplit("/", 1)[-1]
    if not zipfile.is_zipfile(zp):
        zp.unlink(missing_ok=True)
        log.info("Baixando CSB nacional (~3,7 GB) para %s", zp)
        _baixar_em_blocos(s, cfg["talhoes"]["csb_url"], zp)
    pasta_gdb = cfg["_caminhos"].interim / "csb"
    with zipfile.ZipFile(zp) as z:
        membros = [m for m in z.namelist() if ".gdb/" in m and not m.endswith("/")]
        gdb = pasta_gdb / membros[0].split("/")[0]
        if not gdb.exists():
            log.info("Extraindo %s (%.1f GB)", gdb.name, sum(z.getinfo(m).file_size for m in membros) / 1e9)
            z.extractall(pasta_gdb, members=membros)
    try:
        camada = pyogrio.list_layers(gdb)[0][0]
        crs_csb = pyogrio.read_info(gdb, layer=camada)["crs"]
        caixa = tuple(limite.to_crs(crs_csb).total_bounds)
        gdf = pyogrio.read_dataframe(gdb, layer=camada, bbox=caixa, use_arrow=True)
    finally:
        shutil.rmtree(pasta_gdb, ignore_errors=True)
    gdf = gdf.to_crs(cfg["grade"]["crs"])
    cols = {c.upper(): c for c in gdf.columns}
    gdf = gdf.rename(columns={cols["CSBID"]: "id_talhao"})
    cdl_cols = {c: f"csb_cdl_{c[3:]}" for c in gdf.columns if c.upper().startswith("CDL") and c[3:].isdigit()}
    return gdf.rename(columns=cdl_cols)[["id_talhao", *cdl_cols.values(), "geometry"]]


def _talhoes_grade(cfg: dict, limite: gpd.GeoDataFrame, pilha_cdl: Path) -> gpd.GeoDataFrame:
    """Plano B: quadriculas regulares (padrao 402 m = quarter-quarter section do PLSS) com lavoura suficiente
    no ano mais recente do CDL."""
    lado = cfg["talhoes"]["grade_lado_m"]
    x0, y0, x1, y1 = limite.total_bounds
    xs, ys = np.meshgrid(np.arange(x0, x1, lado), np.arange(y0, y1, lado))
    gdf = gpd.GeoDataFrame(geometry=box(xs.ravel(), ys.ravel(), xs.ravel() + lado, ys.ravel() + lado),
                           crs=limite.crs)
    gdf = gdf.clip(limite).explode(index_parts=False).reset_index(drop=True)
    gdf["id_talhao"] = [f"G{i:06d}" for i in range(len(gdf))]
    with rasterio.open(pilha_cdl) as r:
        ultimo = r.read(r.count)
        perfil = r.profile
    lavoura = (~np.isin(ultimo, CDL_NAO_AGRICOLA) & (ultimo > 0)).astype(np.float32)
    lavoura[ultimo == 0] = np.nan
    mascara = cfg["_caminhos"].interim / "mascara_lavoura.tif"
    perfil.update(count=1, dtype="float32", nodata=np.nan, predictor=3)
    with rasterio.open(mascara, "w", **perfil) as d:
        d.write(lavoura, 1)
    frac = exact_extract(str(mascara), gdf, "mean", include_cols=["id_talhao"], output="pandas")
    gdf = gdf.merge(frac.rename(columns={"mean": "frac_lavoura"}), on="id_talhao")
    return gdf[gdf["frac_lavoura"] >= cfg["talhoes"]["grade_frac_lavoura_min"]].drop(columns="frac_lavoura")


def carregar_talhoes(cfg: dict, limite: gpd.GeoDataFrame, s: requests.Session, pilha_cdl: Path, fonte: str,
                     forcar: bool = False) -> gpd.GeoDataFrame:
    destino = cfg["_caminhos"].processed / "talhoes.parquet"
    if destino.exists() and not forcar:
        return gpd.read_parquet(destino)
    lim = limite.to_crs(cfg["grade"]["crs"])
    gdf = _talhoes_csb(cfg, lim, s) if fonte == "csb" else _talhoes_grade(cfg, lim, pilha_cdl)
    gdf["geometry"] = gdf.make_valid()
    # mantem talhoes cujo ponto interno cai no condado (evita duplicar talhoes de fronteira entre condados)
    dentro = gdf.representative_point().within(lim.union_all())
    gdf = gdf[dentro].copy()
    gdf["area_ha"] = gdf.area / 1e4
    gdf = gdf[gdf["area_ha"] >= cfg["talhoes"]["area_min_ha"]].copy()
    gdf["id_talhao"] = gdf["id_talhao"].astype(str)
    pt = gpd.GeoSeries(gdf.representative_point(), crs=gdf.crs).to_crs(CRS_GEO)
    gdf["lon"], gdf["lat"] = pt.x.to_numpy(), pt.y.to_numpy()
    gdf["fonte_talhao"] = fonte
    gdf = gdf.drop_duplicates("id_talhao").reset_index(drop=True)
    gdf.to_parquet(destino)
    _gravar_manifesto(cfg, "talhoes", {"fonte": fonte, "n": len(gdf), "area_total_ha": float(gdf.area_ha.sum()),
                                       "arquivo": destino})
    return gdf


# --------------------------------------------------------------------------------------------------------------------
# 6. Cruzamentos por talhao
# --------------------------------------------------------------------------------------------------------------------
def cdl_por_talhao(talhoes: gpd.GeoDataFrame, pilha_cdl: Path) -> pl.DataFrame:
    """Classe dominante por talhao e ano (ponderada pela cobertura parcial de cada pixel) e sua pureza."""
    anos = anos_da_pilha(pilha_cdl)
    r = exact_extract(str(pilha_cdl), talhoes[["id_talhao", "geometry"]], ["mode", "frac"],
                      include_cols=["id_talhao"], output="pandas")
    ids = pl.Series("id_talhao", r["id_talhao"].astype(str).to_numpy())
    blocos = []
    for i, ano in enumerate(anos, start=1):
        frac = pl.Series(r[f"band_{i}_frac"].tolist(), dtype=pl.List(pl.Float64))
        blocos.append(pl.DataFrame({
            "id_talhao": ids,
            "periodo": pl.Series(np.full(len(r), ano, dtype=np.int16)),
            "cdl_codigo": pl.Series(r[f"band_{i}_mode"].to_numpy()).cast(pl.Int16, strict=False),
            "cdl_pureza": frac.list.max(),
        }))
    df = pl.concat(blocos)
    return df.with_columns(
        pl.col("cdl_codigo").replace_strict(CDL_CLASSES, default=None, return_dtype=pl.String).alias("cdl_classe"),
        pl.col("cdl_codigo").replace_strict(CDL_GRUPO, default="nao_agricola", return_dtype=pl.String)
        .alias("cdl_grupo"),
        (pl.col("cdl_pureza") >= 0.6).alias("cdl_confiavel"),
    ).sort(["id_talhao", "periodo"])


def resumir_rotacao(hist: pl.DataFrame, ultimos_anos: int = 8) -> pl.DataFrame:
    """Rotacao baseline por talhao: sequencia recente, frequencias por grupo, trocas e padrao dominante."""
    recente = hist.filter(pl.col("periodo") > pl.col("periodo").max() - ultimos_anos)
    troca = (pl.col("cdl_grupo") != pl.col("cdl_grupo").shift(1)).cast(pl.Int8)
    res = recente.sort(["id_talhao", "periodo"]).group_by("id_talhao", maintain_order=True).agg(
        pl.col("cdl_grupo").str.join("-").alias("rotacao_seq"),
        pl.len().alias("rotacao_n_anos"),
        (pl.col("cdl_grupo") == "milho").mean().alias("rotacao_frac_milho"),
        (pl.col("cdl_grupo") == "soja").mean().alias("rotacao_frac_soja"),
        pl.col("cdl_grupo").is_in(["forrageira", "pastagem"]).mean().alias("rotacao_frac_perene"),
        pl.col("cdl_grupo").is_in(["cereal_inverno", "milho_soja_dupla"]).mean().alias("rotacao_frac_inverno_dupla"),
        (pl.col("cdl_grupo") == "pousio").mean().alias("rotacao_frac_pousio"),
        troca.slice(1).sum().alias("rotacao_trocas"),
        pl.col("cdl_grupo").n_unique().alias("rotacao_n_grupos"),
        pl.col("cdl_pureza").mean().alias("rotacao_pureza_media"),
    )
    alterna = pl.col("rotacao_trocas") >= 0.7 * (pl.col("rotacao_n_anos") - 1)
    ms = pl.col("rotacao_frac_milho") + pl.col("rotacao_frac_soja")
    return res.with_columns(
        pl.when((ms >= 0.8) & alterna).then(pl.lit("milho_soja_alternado"))
        .when(pl.col("rotacao_frac_milho") >= 0.8).then(pl.lit("monocultura_milho"))
        .when(pl.col("rotacao_frac_soja") >= 0.8).then(pl.lit("monocultura_soja"))
        .when(pl.col("rotacao_frac_perene") >= 0.5).then(pl.lit("perene_forragem"))
        .when(ms >= 0.8).then(pl.lit("milho_soja_irregular"))
        .otherwise(pl.lit("diversificada")).alias("rotacao_padrao")
    )


def terreno_por_talhao(talhoes: gpd.GeoDataFrame, terreno: Path) -> pl.DataFrame:
    with rasterio.open(terreno) as r:
        nomes = list(r.descriptions)
    ops = ["mean", "stdev", "quantile(q=0.9)"]
    df = pl.from_pandas(exact_extract(str(terreno), talhoes[["id_talhao", "geometry"]], ops,
                                      include_cols=["id_talhao"], output="pandas"))
    ren = {}
    for i, n in enumerate(nomes, start=1):
        ren |= {f"band_{i}_mean": f"{n}_media", f"band_{i}_stdev": f"{n}_dp", f"band_{i}_quantile_90": f"{n}_p90"}
    return df.rename(ren).with_columns(pl.col("id_talhao").cast(pl.String))


def solo_por_talhao(talhoes: gpd.GeoDataFrame, solos: gpd.GeoDataFrame, props: pl.DataFrame) -> pl.DataFrame:
    """Sobreposicao exata talhao x poligono de solo. Numericas: media ponderada pela area de intersecao.
    Categoricas: classe da maior area. Inclui a fracao do talhao coberta por solo mal drenado e a cobertura SSURGO."""
    pedacos = gpd.overlay(talhoes[["id_talhao", "geometry"]], solos[["mukey", "geometry"]], how="intersection",
                          keep_geom_type=True)
    inter = pl.DataFrame({"id_talhao": pedacos["id_talhao"].astype(str).to_numpy(),
                          "mukey": pedacos["mukey"].astype(str).to_numpy(),
                          "a": pedacos.area.to_numpy()})
    inter = inter.group_by(["id_talhao", "mukey"]).agg(pl.col("a").sum()).join(props, on="mukey", how="left")
    categ = ["mukey", "muname", "drenagem_classe", "grupo_hidrologico", "componente_dominante"]
    numer = [c for c, t in props.schema.items() if t.is_numeric() and c not in categ]
    pond = inter.group_by("id_talhao").agg(
        *[((pl.col(c) * pl.col("a")).sum() / pl.col("a").filter(pl.col(c).is_not_null()).sum()).alias(c)
          for c in numer],
        (pl.col("a").filter(pl.col("drenagem_ord") >= 5).sum() / pl.col("a").sum()).alias("frac_mal_drenado"),
        pl.col("mukey").n_unique().alias("n_unidades_solo"),
        pl.col("a").sum().alias("_a_solo"),
    ).with_columns(pl.selectors.float().fill_nan(None))
    dominante = (inter.sort("a", descending=True).group_by("id_talhao", maintain_order=True)
                 .agg(*[pl.col(c).first().alias(f"{c}_dominante" if c == "mukey" else c) for c in categ]))
    area = pl.DataFrame({"id_talhao": talhoes["id_talhao"].astype(str).to_numpy(),
                         "_a_talhao": talhoes.area.to_numpy()})
    return (area.join(pond, on="id_talhao", how="left").join(dominante, on="id_talhao", how="left")
            .with_columns((pl.col("_a_solo") / pl.col("_a_talhao")).clip(upper_bound=1.0).alias("solo_cobertura"))
            .drop("_a_solo", "_a_talhao"))


def cruzar(cfg: dict, talhoes: gpd.GeoDataFrame, pilha_cdl: Path, terreno: Path, solos: gpd.GeoDataFrame,
           props: pl.DataFrame) -> dict[str, Path]:
    proc = cfg["_caminhos"].processed
    with _Cronometro("cruzar: CDL x talhao"):
        hist = cdl_por_talhao(talhoes, pilha_cdl)
    with _Cronometro("cruzar: terreno x talhao"):
        terr = terreno_por_talhao(talhoes, terreno)
    with _Cronometro("cruzar: solo x talhao"):
        solo = solo_por_talhao(talhoes, solos, props)
    rot = resumir_rotacao(hist)

    base_cols = ["id_talhao", "area_ha", "lon", "lat", "fonte_talhao"]
    base = pl.from_pandas(talhoes[base_cols + [c for c in talhoes.columns if c.startswith("csb_cdl_")]])
    estatico = (base.with_columns(pl.col("id_talhao").cast(pl.String))
                .join(solo, on="id_talhao", how="left").join(terr, on="id_talhao", how="left")
                .join(rot, on="id_talhao", how="left"))
    painel = hist.join(estatico, on="id_talhao", how="left").sort(["id_talhao", "periodo"])

    saidas = {"talhao_estatico": proc / "talhao_estatico.parquet",
              "talhao_periodo_cdl": proc / "talhao_periodo_cdl.parquet",
              "talhao_periodo_base": proc / "talhao_periodo_base.parquet"}
    estatico.write_parquet(saidas["talhao_estatico"])
    hist.write_parquet(saidas["talhao_periodo_cdl"])
    painel.write_parquet(saidas["talhao_periodo_base"])
    _gravar_manifesto(cfg, "cruzar", {
        "talhoes": estatico.height, "linhas_painel": painel.height, "anos": hist["periodo"].unique().sort().to_list(),
        "cobertura_solo_media": estatico["solo_cobertura"].mean(),
        "pureza_cdl_media": hist["cdl_pureza"].mean(),
        "padroes_rotacao": dict(estatico["rotacao_padrao"].value_counts().iter_rows()),
        "arquivos": saidas,
    })
    return saidas


# --------------------------------------------------------------------------------------------------------------------
# Orquestracao
# --------------------------------------------------------------------------------------------------------------------
def executar(cfg: dict, etapas: tuple[str, ...] = ETAPAS, forcar: bool = False, fonte_talhoes: str | None = None
             ) -> dict[str, Path]:
    s = _sessao_http()
    f = lambda e: forcar and e in etapas  # noqa: E731  so forca o recalculo das etapas pedidas
    with _Cronometro("limite"):
        limite = baixar_limite_condado(cfg, s, f("limite"))
    with _Cronometro("cdl"):
        pilha, grade = empilhar_cdl(cfg, baixar_cdl(cfg, limite, s, f("cdl")), f("cdl"))
    log.info("Grade mestre: %s %dx%d res=%.0f m", grade.crs, grade.width, grade.height, grade.res)
    with _Cronometro("terreno"):
        dem, gx, folga = baixar_dem(cfg, grade, f("terreno"))
        terreno = derivar_terreno(cfg, dem, gx, folga, grade, f("terreno"))
    with _Cronometro("solo"):
        solos = baixar_ssurgo_poligonos(cfg, s, f("solo"))
        props = baixar_ssurgo_atributos(cfg, s, f("solo"))
    with _Cronometro("talhoes"):
        talhoes = carregar_talhoes(cfg, limite, s, pilha, fonte_talhoes or cfg["talhoes"]["fonte"], f("talhoes"))
    log.info("%d talhoes (%.0f ha)", len(talhoes), talhoes["area_ha"].sum())
    saidas = {"terreno": terreno, "talhoes": cfg["_caminhos"].processed / "talhoes.parquet"}
    if "cruzar" in etapas:
        with _Cronometro("cruzar"):
            saidas |= cruzar(cfg, talhoes, pilha, terreno, solos, props)
    return saidas


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--config", default=None, help="arquivo TOML (padrao: config/pilot_county.toml)")
    ap.add_argument("--etapas", nargs="+", choices=ETAPAS, default=list(ETAPAS),
                    help="etapas a (re)executar; as demais so leem o cache")
    ap.add_argument("--forcar", action="store_true", help="recalcula as etapas pedidas mesmo com cache")
    ap.add_argument("--talhoes", choices=["csb", "grade"], default=None, help="sobrepoe [talhoes].fonte")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    saidas = executar(carregar_config(a.config), tuple(a.etapas), a.forcar, a.talhoes)
    for k, p in saidas.items():
        log.info("%-22s %s", k, p)


if __name__ == "__main__":
    main()
