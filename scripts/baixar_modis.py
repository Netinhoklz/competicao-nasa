"""Download e recorte de produtos MODIS (Planetary Computer) para Ceara / Nordeste.

Uso: python -I baixar_modis.py <ndvi|lst|et|fogo|lc|validacao> [--workers N]

Decisoes:
- Os overviews dos COGs do PC foram gerados por MEDIA (codigos de QA inexistentes aparecem no overview),
  entao toda leitura e feita em resolucao cheia, a mascara de qualidade e aplicada no pixel nativo e so
  depois agregamos (media) para a grade lat/lon.
- Grade do estado: 0.01 grau (~1.1 km) para NDVI/EVI/LST; 0.005 grau (~550 m) para ET.
- AOIs: grade 0.0025 grau (~275 m) por vizinho mais proximo, preservando o pixel de 250 m e o QA bruto.
- Fogo (MCD64A1): fracao queimada mensal numa grade 0.05 grau do Nordeste + mapas anuais 0.005 grau
  + area queimada mensal por UF calculada no pixel nativo (463 m).
- Memmaps em E:/campeonato-nasa/tmp/modis_* permitem retomar se o processo cair.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa: E402,F401

import numpy as np  # noqa: E402
import planetary_computer as pc  # noqa: E402
import pystac_client  # noqa: E402
import rasterio  # noqa: E402
from rasterio.enums import Resampling  # noqa: E402
from rasterio.features import rasterize  # noqa: E402
from rasterio.transform import from_origin  # noqa: E402
from rasterio.warp import reproject, transform_bounds, transform_geom  # noqa: E402
from rasterio.windows import Window, from_bounds  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
OUT = pasta("modis")
TMP = RAIZ / "tmp"
LIMITE = 0      # >0: modo teste (poucas datas, saidas em dados/modis/teste)
SUF = ""
GDAL_ENV = dict(
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    GDAL_HTTP_MAX_RETRY="6",
    GDAL_HTTP_RETRY_DELAY="3",
    GDAL_HTTP_MULTIRANGE="YES",
    GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF",
    VSI_CACHE="TRUE",
    GDAL_CACHEMAX=256,
)

# grades alvo -------------------------------------------------------------
def grade(bbox, res):
    lon0, lat0, lon1, lat1 = bbox
    nx = int(round((lon1 - lon0) / res))
    ny = int(round((lat1 - lat0) / res))
    T = from_origin(lon0, lat1, res, res)
    lons = lon0 + res * (np.arange(nx) + 0.5)
    lats = lat1 - res * (np.arange(ny) + 0.5)
    return T, (ny, nx), lons, lats


T_CE, SH_CE, LON_CE, LAT_CE = grade(BBOX_CE, 0.01)
T_CE5, SH_CE5, LON_CE5, LAT_CE5 = grade(BBOX_CE, 0.005)
T_NE5, SH_NE5, LON_NE5, LAT_NE5 = grade(BBOX_NE, 0.05)
T_NEf, SH_NEf, LON_NEf, LAT_NEf = grade(BBOX_NE, 0.005)
AOI_RES = 0.0025
AOI_G = {n: grade(bbox_aoi(n), AOI_RES) for n in AOIS}


def log(*a):
    print(datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def catalogo():
    return pystac_client.Client.open(STAC)


def buscar(col, bbox, dt, prefixo=None):
    """Itens unicos por (data inicial, tile); prefixo filtra plataforma (MOD/MYD/MCD)."""
    its = catalogo().search(collections=[col], bbox=bbox, datetime=dt).item_collection()
    por = {}
    for it in its:
        if prefixo and not it.id.startswith(prefixo):
            continue
        d = (it.properties.get("start_datetime") or str(it.datetime))[:10]
        k = (d, it.properties["modis:horizontal-tile"], it.properties["modis:vertical-tile"])
        if k not in por or it.id > por[k].id:
            por[k] = it
    datas = {}
    for (d, h, v), it in por.items():
        datas.setdefault(d, []).append(it)
    datas = dict(sorted(datas.items()))
    if LIMITE:
        ks = list(datas)
        sel = ks[:: max(1, len(ks) // LIMITE)][:LIMITE]
        datas = {k: datas[k] for k in sel}
    return datas


def janela(ds, bbox):
    b = transform_bounds("EPSG:4326", ds.crs, *bbox, densify_pts=60)
    w = from_bounds(*b, transform=ds.transform)
    try:
        w = w.intersection(Window(0, 0, ds.width, ds.height))
    except Exception:
        return None
    w = w.round_offsets(op="floor").round_lengths(op="ceil")
    if w.width <= 0 or w.height <= 0:
        return None
    return w


def ler(item, asset, bbox):
    href = pc.sign(item.assets[asset].href)
    for tent in range(6):
        try:
            with rasterio.Env(**GDAL_ENV):
                with rasterio.open(href) as ds:
                    w = janela(ds, bbox)
                    if w is None:
                        return None
                    a = ds.read(1, window=w)
                    return a, ds.window_transform(w), ds.crs
        except Exception as e:  # rede instavel: tenta de novo com token novo
            if tent == 5:
                raise
            time.sleep(3 * (tent + 1))
            href = pc.sign(item.assets[asset].href.split("?")[0])
    return None


def para_grade(arr, T, crs, Tdst, shape, resamp=Resampling.average, nodata=np.nan, dtype="float32"):
    dst = np.full(shape, nodata, dtype=dtype)
    reproject(arr, dst, src_transform=T, src_crs=crs, dst_transform=Tdst, dst_crs="EPSG:4326",
              resampling=resamp, src_nodata=nodata, dst_nodata=nodata, num_threads=1)
    return dst


def combinar(lista):
    """Junta grades de tiles diferentes (nanmean nas bordas)."""
    lista = [x for x in lista if x is not None]
    if not lista:
        return None
    if len(lista) == 1:
        return lista[0]
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return np.nanmean(np.stack(lista), axis=0)


def memmap(nome, shape, dtype, fill):
    p = TMP / f"modis_{nome}{SUF}.npy"
    if p.exists():
        m = np.lib.format.open_memmap(p, mode="r+")
        if m.shape == tuple(shape) and m.dtype == np.dtype(dtype):
            return m
        del m
    m = np.lib.format.open_memmap(p, mode="w+", dtype=dtype, shape=tuple(shape))
    m[:] = fill
    return m


def rodar(datas, funcao, nome, workers):
    chaves = list(datas)
    feito_p = TMP / f"modis_{nome}{SUF}_feito.npy"
    feito = np.load(feito_p) if feito_p.exists() and len(np.load(feito_p)) == len(chaves) else np.zeros(len(chaves), bool)
    pend = [i for i in range(len(chaves)) if not feito[i]]
    log(nome, "datas:", len(chaves), "pendentes:", len(pend))
    lock = threading.Lock()
    n = 0
    erros = []
    with ThreadPoolExecutor(workers) as ex:
        fut = {ex.submit(funcao, i, chaves[i], datas[chaves[i]]): i for i in pend}
        for f in as_completed(fut):
            i = fut[f]
            try:
                f.result()
                with lock:
                    feito[i] = True
                    n += 1
                    if n % 25 == 0:
                        np.save(feito_p, feito)
                        log(nome, f"{n}/{len(pend)}", chaves[i])
            except Exception as e:
                erros.append((chaves[i], repr(e)[:200]))
                log("ERRO", nome, chaves[i], repr(e)[:200])
    np.save(feito_p, feito)
    return feito, erros


# NDVI / EVI ------------------------------------------------------------------
def job_ndvi(workers):
    import xarray as xr
    datas = buscar("modis-13Q1-061", BBOX_CE, "2000-01-01/2026-12-31", prefixo="MOD13Q1")
    N = len(datas)
    ny, nx = SH_CE
    ndvi = memmap("ndvi_ce", (N, ny, nx), "int16", -32768)
    evi = memmap("evi_ce", (N, ny, nx), "int16", -32768)
    boa = memmap("ndvi_boa_ce", (N, ny, nx), "uint8", 255)
    aoi = {}
    for nm, (T, sh, _, _) in AOI_G.items():
        aoi[nm] = (memmap(f"ndvi_aoi_{nm}", (N,) + sh, "int16", -3000),
                   memmap(f"evi_aoi_{nm}", (N,) + sh, "int16", -3000),
                   memmap(f"rel_aoi_{nm}", (N,) + sh, "uint8", 255))

    def f(i, d, itens):
        gn, ge, gb = [], [], []
        a_n = {nm: [] for nm in AOIS}
        for it in itens:
            rn = ler(it, "250m_16_days_NDVI", BBOX_CE)
            if rn is None:
                continue
            rv, T, crs = rn
            re_ = ler(it, "250m_16_days_EVI", BBOX_CE)[0]
            rr = ler(it, "250m_16_days_pixel_reliability", BBOX_CE)[0]
            # arquivos reprocessados (>= jun/2025) vem em int8 com nodata -1; padroniza para uint8/255
            rr16 = rr.astype(np.int16)
            rr = np.where(rr16 < 0, 255, rr16).astype(np.uint8)
            ok = (rr <= 1) & (rv > -3000)
            obs = (rr != 255) & (rv > -3000)
            vn = np.where(ok, rv / 10000.0, np.nan).astype("float32")
            ve = np.where(ok & (re_ > -3000), re_ / 10000.0, np.nan).astype("float32")
            vb = np.where(obs, ok.astype("float32"), np.nan).astype("float32")
            gn.append(para_grade(vn, T, crs, T_CE, SH_CE))
            ge.append(para_grade(ve, T, crs, T_CE, SH_CE))
            gb.append(para_grade(vb, T, crs, T_CE, SH_CE))
            for nm, (Ta, sha, _, _) in AOI_G.items():
                a_n[nm].append((
                    para_grade(rv, T, crs, Ta, sha, Resampling.nearest, -3000, "int16"),
                    para_grade(re_, T, crs, Ta, sha, Resampling.nearest, -3000, "int16"),
                    para_grade(rr, T, crs, Ta, sha, Resampling.nearest, 255, "uint8"),
                ))
        n_, e_, b_ = combinar(gn), combinar(ge), combinar(gb)
        if n_ is None:
            return
        ndvi[i] = np.where(np.isnan(n_), -32768, np.round(n_ * 10000)).astype("int16")
        evi[i] = np.where(np.isnan(e_), -32768, np.round(e_ * 10000)).astype("int16")
        boa[i] = np.where(np.isnan(b_), 255, np.round(b_ * 100)).astype("uint8")
        for nm, lst in a_n.items():
            if not lst:
                continue
            an, ae, ar = lst[0]
            for bn, be, br in lst[1:]:
                m = an == -3000
                an[m], ae[m], ar[m] = bn[m], be[m], br[m]
            aoi[nm][0][i], aoi[nm][1][i], aoi[nm][2][i] = an, ae, ar

    feito, erros = rodar(datas, f, "ndvi", workers)
    tempos = np.array([np.datetime64(d) for d in datas])
    ds = xr.Dataset(
        {"ndvi": (("time", "lat", "lon"), np.asarray(ndvi)),
         "evi": (("time", "lat", "lon"), np.asarray(evi)),
         "frac_boa": (("time", "lat", "lon"), np.asarray(boa))},
        coords={"time": tempos, "lat": LAT_CE, "lon": LON_CE},
        attrs={"fonte": "MOD13Q1 v061 (Terra) via Microsoft Planetary Computer",
               "processamento": "pixel 250 m mascarado por pixel_reliability<=1; media para 0.01 grau",
               "ndvi_escala": 1e-4, "frac_boa": "% de pixels 250 m com reliability<=1 entre os observados (255=sem dado)"})
    for v in ("ndvi", "evi"):
        ds[v].attrs.update(scale_factor=1e-4, _FillValue=-32768, units="1")
    ds["frac_boa"].attrs.update(_FillValue=255, units="%")
    ds["feito"] = ("time", feito)
    enc = {v: {"zlib": True, "complevel": 4, "chunksizes": (min(23, N), ny, nx)} for v in ("ndvi", "evi", "frac_boa")}
    for v in ("ndvi", "evi"):
        ds[v].encoding = {}
    p = OUT / "mod13q1_ndvi_evi_ceara_001deg.nc"
    _salvar_scaled(ds, p, enc)
    # AOIs
    for nm, (T, sh, lons, lats) in AOI_G.items():
        da = xr.Dataset(
            {"ndvi_raw": (("time", "lat", "lon"), np.asarray(aoi[nm][0])),
             "evi_raw": (("time", "lat", "lon"), np.asarray(aoi[nm][1])),
             "pixel_reliability": (("time", "lat", "lon"), np.asarray(aoi[nm][2]))},
            coords={"time": tempos, "lat": lats, "lon": lons},
            attrs={"fonte": "MOD13Q1 v061 (Terra)", "aoi": nm, "descricao": AOIS[nm][2],
                   "nota": "valores brutos (NDVI*1e4, fill -3000; reliability 0 bom,1 marginal,2 neve,3 nuvem,255 sem dado)"})
        da.to_netcdf(OUT / f"mod13q1_aoi_{nm}_250m.nc",
                     encoding={v: {"zlib": True, "complevel": 4} for v in da.data_vars})
    registrar_manifesto("modis", {"mod13q1": {
        "colecao": "modis-13Q1-061 (MOD13Q1, Terra)", "url": STAC, "bbox": BBOX_CE, "n_datas": len(tempos),
        "periodo": [str(tempos[0]), str(tempos[-1])], "datas_ok": int(feito.sum()), "erros": erros[:30],
        "arquivos": [p.name] + [f"mod13q1_aoi_{nm}_250m.nc" for nm in AOIS]}})
    log("ndvi concluido", int(feito.sum()), "de", len(feito))


def _salvar_scaled(ds, p, enc):
    """Grava inteiros ja escalados sem que o xarray reescale (mantem scale_factor como atributo)."""
    import xarray as xr  # noqa
    ds2 = ds.copy()
    for v in ds2.data_vars:
        at = dict(ds2[v].attrs)
        fill = at.pop("_FillValue", None)
        ds2[v].attrs = at
        if v in enc and fill is not None:
            enc[v]["_FillValue"] = fill
    ds2.to_netcdf(p, encoding=enc)


# LST ------------------------------------------------------------------------
def _qc_ok(qc):
    q = qc.astype(np.uint16)
    mand = q & 3
    err = (q >> 6) & 3
    return (mand == 0) | ((mand == 1) & (err <= 1))


def job_lst(workers):
    import xarray as xr
    datas = buscar("modis-11A2-061", BBOX_CE, "2000-01-01/2026-12-31", prefixo="MOD11A2")
    N = len(datas)
    ny, nx = SH_CE
    day = memmap("lstd_ce", (N, ny, nx), "int16", -32768)
    night = memmap("lstn_ce", (N, ny, nx), "int16", -32768)

    def f(i, d, itens):
        gd, gn = [], []
        for it in itens:
            r = ler(it, "LST_Day_1km", BBOX_CE)
            if r is None:
                continue
            ld, T, crs = r
            qd = ler(it, "QC_Day", BBOX_CE)[0]
            ln = ler(it, "LST_Night_1km", BBOX_CE)[0]
            qn = ler(it, "QC_Night", BBOX_CE)[0]
            vd = np.where((ld > 0) & _qc_ok(qd), ld * 0.02 - 273.15, np.nan).astype("float32")
            vn = np.where((ln > 0) & _qc_ok(qn), ln * 0.02 - 273.15, np.nan).astype("float32")
            gd.append(para_grade(vd, T, crs, T_CE, SH_CE))
            gn.append(para_grade(vn, T, crs, T_CE, SH_CE))
        a, b = combinar(gd), combinar(gn)
        if a is None:
            return
        day[i] = np.where(np.isnan(a), -32768, np.round(a * 100)).astype("int16")
        night[i] = np.where(np.isnan(b), -32768, np.round(b * 100)).astype("int16")

    feito, erros = rodar(datas, f, "lst", workers)
    tempos = np.array([np.datetime64(d) for d in datas])
    ds = xr.Dataset({"lst_dia": (("time", "lat", "lon"), np.asarray(day)),
                     "lst_noite": (("time", "lat", "lon"), np.asarray(night))},
                    coords={"time": tempos, "lat": LAT_CE, "lon": LON_CE},
                    attrs={"fonte": "MOD11A2 v061 (Terra, ~10:30/22:30 hora local) via Planetary Computer",
                           "processamento": "QC mandatorio=0 ou (=1 e erro<=2K); media para 0.01 grau",
                           "unidade": "graus Celsius x100"})
    for v in ds.data_vars:
        ds[v].attrs.update(scale_factor=0.01, units="degC", _FillValue=-32768)
    ds["feito"] = ("time", feito)
    enc = {v: {"zlib": True, "complevel": 4, "chunksizes": (min(46, N), ny, nx)} for v in ("lst_dia", "lst_noite")}
    p = OUT / "mod11a2_lst_ceara_001deg.nc"
    _salvar_scaled(ds, p, enc)
    registrar_manifesto("modis", {"mod11a2": {
        "colecao": "modis-11A2-061 (MOD11A2, Terra)", "bbox": BBOX_CE, "n_datas": len(tempos),
        "periodo": [str(tempos[0]), str(tempos[-1])], "datas_ok": int(feito.sum()), "erros": erros[:30],
        "arquivos": [p.name]}})
    log("lst concluido", int(feito.sum()), "de", len(feito))


# ET anual ---------------------------------------------------------------------
def job_et(workers):
    import xarray as xr
    datas = buscar("modis-16A3GF-061", BBOX_CE, "2000-01-01/2026-12-31", prefixo="MOD16A3GF")
    N = len(datas)
    ny, nx = SH_CE5
    et = memmap("et_ce", (N, ny, nx), "float32", np.nan)
    pet = memmap("pet_ce", (N, ny, nx), "float32", np.nan)

    def f(i, d, itens):
        ge, gp = [], []
        for it in itens:
            r = ler(it, "ET_500m", BBOX_CE)
            if r is None:
                continue
            e, T, crs = r
            p_ = ler(it, "PET_500m", BBOX_CE)[0]
            ve = np.where(e < 65500, e * 0.1, np.nan).astype("float32")
            vp = np.where(p_ < 65500, p_ * 0.1, np.nan).astype("float32")
            ge.append(para_grade(ve, T, crs, T_CE5, SH_CE5))
            gp.append(para_grade(vp, T, crs, T_CE5, SH_CE5))
        et[i], pet[i] = combinar(ge), combinar(gp)

    feito, erros = rodar(datas, f, "et", workers)
    tempos = np.array([np.datetime64(d) for d in datas])
    ds = xr.Dataset({"et": (("time", "lat", "lon"), np.asarray(et)),
                     "pet": (("time", "lat", "lon"), np.asarray(pet))},
                    coords={"time": tempos, "lat": LAT_CE5, "lon": LON_CE5},
                    attrs={"fonte": "MOD16A3GF v061 (Terra, anual, gap-filled) via Planetary Computer",
                           "processamento": "valores >=65500 (classes especiais) removidos; media para 0.005 grau",
                           "unidade": "mm/ano"})
    ds["feito"] = ("time", feito)
    p = OUT / "mod16a3gf_et_ceara_0005deg.nc"
    ds.to_netcdf(p, encoding={v: {"zlib": True, "complevel": 4} for v in ("et", "pet")})
    registrar_manifesto("modis", {"mod16a3gf": {
        "colecao": "modis-16A3GF-061", "bbox": BBOX_CE, "n_anos": len(tempos),
        "periodo": [str(tempos[0]), str(tempos[-1])], "erros": erros[:30], "arquivos": [p.name]}})
    log("et concluido")


# Fogo: MCD64A1 --------------------------------------------------------------------
def _mascara_ufs(T, shape, crs):
    g = nordeste_gdf()
    shapes = [(transform_geom("EPSG:4326", crs, geom.__geo_interface__), int(cod))
              for geom, cod in zip(g.geometry, g["codarea"])]
    return rasterize(shapes, out_shape=shape, transform=T, fill=0, dtype="int32")


def job_fogo(workers):
    import pandas as pd
    import xarray as xr
    datas = buscar("modis-64A1-061", BBOX_NE, "2000-01-01/2026-12-31", prefixo="MCD64A1")
    N = len(datas)
    frac = memmap("queim_ne005", (N,) + SH_NE5, "float32", np.nan)
    anos = sorted({int(d[:4]) for d in datas})
    anual = memmap("queim_anual_nef", (len(anos),) + SH_NEf, "uint8", 0)
    cont = memmap("queim_cont_nef", SH_NEf, "int16", 0)
    linhas = []
    lock = threading.Lock()
    masc_cache = {}
    area_px = 463.3127 ** 2 / 1e6  # km2

    def f(i, d, itens):
        gf, gyear = [], []
        reg = {}
        for it in itens:
            r = ler(it, "Burn_Date", BBOX_NE)
            if r is None:
                continue
            bd, T, crs = r
            chave = (it.properties["modis:horizontal-tile"], it.properties["modis:vertical-tile"], bd.shape)
            with lock:
                if chave not in masc_cache:
                    masc_cache[chave] = _mascara_ufs(T, bd.shape, crs)
            uf = masc_cache[chave]
            queim = bd > 0
            terra = bd >= 0
            vf = np.where(terra, queim.astype("float32"), np.nan).astype("float32")
            gf.append(para_grade(vf, T, crs, T_NE5, SH_NE5))
            gyear.append(para_grade(queim.astype("uint8"), T, crs, T_NEf, SH_NEf, Resampling.nearest, 255, "uint8"))
            for cod in np.unique(uf[uf > 0]):
                m = uf == cod
                k = int(cod)
                a = reg.setdefault(k, [0, 0, 0])
                a[0] += int((queim & m).sum())
                a[1] += int((terra & m).sum())
                a[2] += int(((bd == -1) & m).sum())
        fr = combinar(gf)
        if fr is None:
            return
        frac[i] = fr
        y = anos.index(int(d[:4]))
        b = np.zeros(SH_NEf, "uint8")
        for g in gyear:
            b |= (g == 1)
        with lock:
            anual[y] |= b
            cont[:] += b.astype("int16")
            for k, (q, t, u) in reg.items():
                linhas.append({"data": d, "uf": k, "area_queimada_km2": q * area_px,
                               "area_terra_km2": t * area_px, "area_sem_mapeamento_km2": u * area_px})

    # contagem nao e idempotente com retomada: zera se houver retomada parcial
    feito_p = TMP / f"modis_fogo{SUF}_feito.npy"
    if feito_p.exists():
        feito_p.unlink()
    anual[:] = 0
    cont[:] = 0
    feito, erros = rodar(datas, f, "fogo", workers)
    tempos = np.array([np.datetime64(d) for d in datas])
    ds = xr.Dataset({"frac_queimada": (("time", "lat", "lon"), np.asarray(frac))},
                    coords={"time": tempos, "lat": LAT_NE5, "lon": LON_NE5},
                    attrs={"fonte": "MCD64A1 v061 (Terra+Aqua) via Planetary Computer",
                           "processamento": "Burn_Date>0 = queimado; fracao sobre terra mapeada (Burn_Date>=0) numa grade 0.05 grau"})
    ds["feito"] = ("time", feito)
    p1 = OUT / "mcd64a1_frac_queimada_nordeste_005deg.nc"
    ds.to_netcdf(p1, encoding={"frac_queimada": {"zlib": True, "complevel": 4}})
    da = xr.Dataset({"queimado": (("ano", "lat", "lon"), np.asarray(anual)),
                     "n_meses_queimado": (("lat", "lon"), np.asarray(cont))},
                    coords={"ano": anos, "lat": LAT_NEf, "lon": LON_NEf},
                    attrs={"fonte": "MCD64A1 v061", "processamento": "pixel 500 m por vizinho mais proximo em 0.005 grau"})
    p2 = OUT / "mcd64a1_queimado_anual_nordeste_0005deg.nc"
    da.to_netcdf(p2, encoding={v: {"zlib": True, "complevel": 5} for v in da.data_vars})
    df = pd.DataFrame(linhas).sort_values(["data", "uf"])
    p3 = OUT / "mcd64a1_area_queimada_mensal_uf.parquet"
    df.to_parquet(p3, index=False)
    registrar_manifesto("modis", {"mcd64a1": {
        "colecao": "modis-64A1-061 (MCD64A1)", "bbox": BBOX_NE, "n_meses": len(tempos),
        "periodo": [str(tempos[0]), str(tempos[-1])], "erros": erros[:30],
        "arquivos": [p1.name, p2.name, p3.name]}})
    log("fogo concluido")


# Cobertura do solo (para estratificar o fogo) ------------------------------------
def job_lc(workers):
    import xarray as xr
    its = list(catalogo().search(collections=["esa-cci-lc"], bbox=BBOX_NE, datetime="2020-01-01/2020-12-31").items())
    T, sh, lons, lats = grade(BBOX_NE, 1 / 360)  # 300 m nativo
    out = np.zeros(sh, "uint8")
    for it in its:
        href = pc.sign(it.assets["lccs_class"].href)
        with rasterio.Env(**GDAL_ENV), rasterio.open(href) as ds:
            w = janela(ds, BBOX_NE)
            if w is None:
                continue
            a = ds.read(1, window=w)
            g = para_grade(a, ds.window_transform(w), ds.crs, T, sh, Resampling.nearest, 0, "uint8")
            out = np.where(out == 0, g, out)
    ds = xr.Dataset({"lccs_class": (("lat", "lon"), out)}, coords={"lat": lats, "lon": lons},
                    attrs={"fonte": "ESA CCI Land Cover / C3S v2.1.1, ano 2020, 300 m, via Planetary Computer",
                           "classes": "10-30 lavoura (10 sequeiro,11 herbacea,12 arborea,20 irrigada,30 mosaico lavoura>50%), "
                                      "40 mosaico vegetacao natural>50%, 50-62 florestas, 100-153 mosaicos/arbustos/campos, "
                                      "120-122 arbustiva, 130 campo, 160-180 alagados, 190 urbano, 200-202 solo exposto, 210 agua"})
    p = OUT / "esa_cci_lc_2020_nordeste_300m.nc"
    ds.to_netcdf(p, encoding={"lccs_class": {"zlib": True, "complevel": 5}})
    registrar_manifesto("modis", {"esa_cci_lc_auxiliar": {"colecao": "esa-cci-lc 2020", "bbox": BBOX_NE,
                                                           "uso": "estratificar fogo e NDVI por classe", "arquivos": [p.name]}})
    log("lc concluido", np.unique(out, return_counts=True))


# Validacao global ------------------------------------------------------------------
PONTOS = {
    "Ceara_BR": (-39.6, -5.6), "Pampa_AR": (-61.0, -34.5), "Iowa_US": (-93.5, 42.0), "Saskatchewan_CA": (-106.0, 52.0),
    "Franca_FR": (2.0, 48.5), "Ucrania_UA": (32.0, 49.0), "Finlandia_FI": (25.0, 62.5), "Sahara_DZ": (3.0, 27.0),
    "Quenia_KE": (36.1, -0.3), "Punjab_IN": (75.5, 30.8), "Henan_CN": (114.0, 34.0), "NSW_AU": (147.0, -33.0),
    "Java_ID": (110.5, -7.3), "Mato_Grosso_BR": (-55.5, -13.0),
}


def job_validacao(workers):
    cat = catalogo()
    res = {"gerado_em": datetime.now().isoformat(timespec="seconds"), "colecoes": {}, "pontos": {}}
    alvos = {"modis-13Q1-061": ("MOD13Q1", "2024-07-11/2024-07-12", "250m_16_days_NDVI"),
             "modis-11A2-061": ("MOD11A2", "2024-07-11/2024-07-12", "LST_Day_1km"),
             "modis-16A3GF-061": ("MOD16A3GF", "2023-06-01/2023-06-02", "ET_500m"),
             "modis-64A1-061": ("MCD64A1", "2023-07-15/2023-07-16", "Burn_Date")}
    antigo = OUT / "validacao_global.json"
    preservar = {}
    if antigo.exists():
        d0 = json.loads(antigo.read_text(encoding="utf-8"))
        preservar = {k: d0[k] for k in ("tiles_por_periodo", "lacunas_nordeste_mcd64a1") if k in d0}
    R = 6371007.181
    TAM = 1111950.5197665233

    def tile_hv(lon, lat):
        x = R * np.radians(lon) * np.cos(np.radians(lat))
        y = R * np.radians(lat)
        return int((x + 18 * TAM) // TAM), int((9 * TAM - y) // TAM)

    for col, (pref, dt, asset) in alvos.items():
        its = [i for i in cat.search(collections=[col], datetime=dt).items() if i.id.startswith(pref)]
        tiles = sorted({(i.properties["modis:horizontal-tile"], i.properties["modis:vertical-tile"]) for i in its})
        bbs = np.array([i.bbox for i in its]) if its else np.zeros((0, 4))
        info = {"n_itens_um_periodo": len(its), "n_tiles": len(tiles),
                "lat_min": float(bbs[:, 1].min()) if len(bbs) else None, "lat_max": float(bbs[:, 3].max()) if len(bbs) else None,
                "lon_min": float(bbs[:, 0].min()) if len(bbs) else None, "lon_max": float(bbs[:, 2].max()) if len(bbs) else None,
                "tiles": tiles, "extensao_colecao": cat.get_collection(col).extent.to_dict()}
        res["colecoes"][col] = info
        log(col, "tiles num periodo:", len(tiles))
        for nome, (lon, lat) in PONTOS.items():
            h, vv = tile_hv(lon, lat)
            alvo = next((it for it in its if (it.properties["modis:horizontal-tile"], it.properties["modis:vertical-tile"]) == (h, vv)), None)
            v = None
            if alvo is not None:
                try:
                    with rasterio.Env(**GDAL_ENV), rasterio.open(pc.sign(alvo.assets[asset].href)) as ds:
                        from rasterio.warp import transform as tr
                        xs, ys = tr("EPSG:4326", ds.crs, [lon], [lat])
                        v = float(next(ds.sample([(xs[0], ys[0])]))[0])
                except Exception as e:
                    v = "erro " + repr(e)[:80]
            res["pontos"].setdefault(nome, {"lon": lon, "lat": lat})[col] = {"item": alvo.id if alvo else None, "tile": [h, vv], "valor_bruto": v}
    # grade MODIS completa tem 36x18=460 tiles; terra cobre ~317
    res.update(preservar)
    (OUT / "validacao_global.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    log("validacao salva")


# NDVI do Nordeste (MOD13A1 500 m -> 0.05 grau) ---------------------------------------
def job_ndvi_ne(workers):
    import xarray as xr
    datas = buscar("modis-13A1-061", BBOX_NE, "2000-01-01/2026-12-31", prefixo="MOD13A1")
    N = len(datas)
    ndvi = memmap("ndvi_ne005", (N,) + SH_NE5, "float32", np.nan)
    boa = memmap("ndvi_boa_ne005", (N,) + SH_NE5, "float32", np.nan)

    def f(i, d, itens):
        gn, gb = [], []
        for it in itens:
            r = ler(it, "500m_16_days_NDVI", BBOX_NE)
            if r is None:
                continue
            rv, T, crs = r
            rr = ler(it, "500m_16_days_pixel_reliability", BBOX_NE)[0]
            ok = (rr <= 1) & (rv > -3000)
            obs = (rr != 255) & (rv > -3000)
            gn.append(para_grade(np.where(ok, rv / 1e4, np.nan).astype("float32"), T, crs, T_NE5, SH_NE5))
            gb.append(para_grade(np.where(obs, ok.astype("float32"), np.nan).astype("float32"), T, crs, T_NE5, SH_NE5))
        a, b = combinar(gn), combinar(gb)
        if a is not None:
            ndvi[i], boa[i] = a, b

    feito, erros = rodar(datas, f, "ndvi_ne", workers)
    tempos = np.array([np.datetime64(d) for d in datas])
    ds = xr.Dataset({"ndvi": (("time", "lat", "lon"), np.asarray(ndvi)),
                     "frac_boa": (("time", "lat", "lon"), np.asarray(boa))},
                    coords={"time": tempos, "lat": LAT_NE5, "lon": LON_NE5},
                    attrs={"fonte": "MOD13A1 v061 (Terra, 500 m, 16 dias) via Planetary Computer",
                           "processamento": "pixel 500 m mascarado por pixel_reliability<=1; media para 0.05 grau"})
    ds["feito"] = ("time", feito)
    p = OUT / "mod13a1_ndvi_nordeste_005deg.nc"
    ds.to_netcdf(p, encoding={v: {"zlib": True, "complevel": 4} for v in ("ndvi", "frac_boa")})
    registrar_manifesto("modis", {"mod13a1_nordeste": {
        "colecao": "modis-13A1-061 (MOD13A1, Terra)", "bbox": BBOX_NE, "n_datas": len(tempos),
        "periodo": [str(tempos[0]), str(tempos[-1])], "datas_ok": int(feito.sum()), "erros": erros[:30],
        "arquivos": [p.name]}})
    log("ndvi_ne concluido", int(feito.sum()), "de", len(feito))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("tarefa", choices=["ndvi", "lst", "et", "fogo", "lc", "validacao", "ndvi_ne"])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args()
    if a.limite:
        LIMITE = a.limite
        SUF = "_teste"
        OUT = OUT / "teste"
        OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    globals()["job_" + a.tarefa](a.workers)
    log(a.tarefa, f"tempo total {time.time() - t0:.0f}s")
