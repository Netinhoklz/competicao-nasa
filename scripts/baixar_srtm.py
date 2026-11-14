"""SRTM / NASADEM (Planetary Computer, colecao nasadem; tiles 1x1 grau, 1 arcseg ~30 m).

Etapas:
  ceara    - mosaico 30 m do Ceara (GeoTIFF) + 90 m (declividade, aspecto, TPI) + 270 m (TWI, fator LS RUSLE)
  aoi      - derivados a 30 m nas AOIs (elev, declividade, aspecto, TWI, LS)
  nordeste - Nordeste a ~1 km (media de bloco via overviews) + declividade
  global   - contagem de tiles NASADEM x Copernicus DEM por faixa de latitude vs celulas de terra (Natural Earth)
  munic    - estatisticas zonais por municipio do Ceara (90 m)
"""
import heapq
import math
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from frente_c_util import *  # noqa

import numpy as np
import pandas as pd
import planetary_computer
import pystac_client
import rasterio
from rasterio.transform import from_origin

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
OUT = pasta("srtm")
ND = -32768
ARCSEG = 1 / 3600


def cli(assinado=True):
    return pystac_client.Client.open(STAC, modifier=planetary_computer.sign_inplace if assinado else None)


def salvar_tif(arq, arr, transform, nodata, dtype=None, crs="EPSG:4326"):
    dtype = dtype or arr.dtype
    pred = 3 if np.dtype(dtype).kind == "f" else 2
    with rasterio.open(arq, "w", driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=1, dtype=dtype,
                       crs=crs, transform=transform, nodata=nodata, compress="deflate", predictor=pred,
                       tiled=True, blockxsize=512, blockysize=512, BIGTIFF="IF_SAFER") as dst:
        dst.write(arr.astype(dtype), 1)
    print(f"  salvo {arq.name} {arq.stat().st_size/1e6:.1f} MB {arr.shape}", flush=True)


def ler_tile_janela(href, lon0, lat1, w, h, res):
    """Le a parte do tile que cai na grade alvo (origem lon0, lat1; res graus) -> array (h, w) float32 NaN."""
    from rasterio.enums import Resampling
    from rasterio.windows import from_bounds
    # o tile ja esta em EPSG:4326: le a janela e reamostra com out_shape (GDAL usa as overviews quando res > 1")
    with rasterio.open(href) as src:
        win = from_bounds(lon0, lat1 - h * res, lon0 + w * res, lat1, src.transform)
        a = src.read(1, window=win, out_shape=(h, w), resampling=Resampling.average, masked=True)
        a = a.astype(np.float32).filled(np.nan)
    return a


def mosaico(bbox, res, nthreads=16):
    """Mosaico NASADEM na grade (bbox, res). Le cada tile so na sua janela 1x1 grau (usa overviews quando res>1")."""
    x0, y0, x1, y1 = bbox
    W = int(round((x1 - x0) / res))
    H = int(round((y1 - y0) / res))
    out = np.full((H, W), np.nan, np.float32)
    itens = list(cli().search(collections=["nasadem"], bbox=bbox).items())
    print(f"  {len(itens)} tiles para {bbox} res={res:.6f} -> {H}x{W}", flush=True)

    def tarefa(it):
        tb = it.bbox  # [lon-0.000139, lat-0.000139, lon+1.000139, lat+1.000139]
        lon = round(tb[0]); lat = round(tb[1])
        # interseccao do tile [lon,lon+1]x[lat,lat+1] com a bbox, em pixels da grade alvo
        cx0 = max(lon, x0); cx1 = min(lon + 1, x1); cy0 = max(lat, y0); cy1 = min(lat + 1, y1)
        if cx1 <= cx0 or cy1 <= cy0:
            return None
        c0 = int(round((cx0 - x0) / res)); c1 = int(round((cx1 - x0) / res))
        r0 = int(round((y1 - cy1) / res)); r1 = int(round((y1 - cy0) / res))
        a = ler_tile_janela(it.assets["elevation"].href, x0 + c0 * res, y1 - r0 * res, c1 - c0, r1 - r0, res)
        return r0, r1, c0, c1, a

    t0 = time.time()
    with ThreadPoolExecutor(nthreads) as ex:
        for k, r in enumerate(ex.map(tarefa, itens), 1):
            if r is None:
                continue
            r0, r1, c0, c1, a = r
            bloco = out[r0:r1, c0:c1]
            m = np.isnan(bloco)
            bloco[m] = a[m]
            if k % 20 == 0:
                print(f"    {k}/{len(itens)} tiles ({time.time()-t0:.0f}s)", flush=True)
    return out, from_origin(x0, y1, res, res)


def espacamento(transform, H):
    """Espacamento metrico por linha (dx varia com a latitude)."""
    res = transform.a
    lats = transform.f - res * (np.arange(H) + 0.5)
    dy = res * 110574.0
    dx = res * 111320.0 * np.cos(np.deg2rad(lats))
    return dx.astype(np.float64), dy


def declividade_aspecto(z, transform):
    H, W = z.shape
    dx, dy = espacamento(transform, H)
    zz = z.astype(np.float64)
    gy, gx = np.gradient(zz)  # por pixel
    gx = gx / dx[:, None]
    gy = -gy / dy  # linhas crescem para o sul
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    aspect = (np.degrees(np.arctan2(-gx, -gy)) + 360) % 360  # 0 = norte, sentido horario, direcao da descida
    return slope.astype(np.float32), aspect.astype(np.float32)


def media_bloco(a, f):
    H, W = (a.shape[0] // f) * f, (a.shape[1] // f) * f
    b = a[:H, :W].reshape(H // f, f, W // f, f)
    with np.errstate(invalid="ignore"):
        return np.nanmean(b, axis=(1, 3)).astype(np.float32)


def priority_flood(z, valido, eps=1e-3):
    """Preenche depressoes (Barnes et al. 2014, variante epsilon). Retorna DEM preenchido com descida estrita."""
    from scipy.ndimage import binary_dilation
    H, W = z.shape
    Hp, Wp = H + 2, W + 2
    zp = np.full((Hp, Wp), np.nan); zp[1:-1, 1:-1] = z
    vp = np.zeros((Hp, Wp), bool); vp[1:-1, 1:-1] = valido
    borda = binary_dilation(~vp, np.ones((3, 3), bool)) & vp
    zf = zp.ravel().tolist()
    fechado = (~vp).ravel().tolist()
    heap = []
    for s in np.flatnonzero(borda.ravel()).tolist():
        heap.append((zf[s], s)); fechado[s] = True
    heapq.heapify(heap)
    offs = (-Wp - 1, -Wp, -Wp + 1, -1, 1, Wp - 1, Wp, Wp + 1)
    pop, push = heapq.heappop, heapq.heappush
    while heap:
        zc, c = pop(heap)
        for o in offs:
            n = c + o
            if fechado[n]:
                continue
            fechado[n] = True
            if zf[n] <= zc:
                zf[n] = zc + eps
            push(heap, (zf[n], n))
    return np.array(zf).reshape(Hp, Wp)[1:-1, 1:-1]


def acumulacao_d8(zf, valido, transform):
    """Direcao D8 (maior declive) no DEM preenchido e acumulacao de area (m2) por ordem topologica."""
    H, W = zf.shape
    dx, dy = espacamento(transform, H)
    area = (dx * dy)[:, None] * np.ones((1, W))
    zp = np.pad(np.where(valido, zf, np.nan), 1, constant_values=np.nan)
    melhor = np.zeros((H, W)); rec = np.full((H, W), -1, np.int64)
    idx = np.arange(H * W).reshape(H, W)
    idxp = np.pad(idx, 1, constant_values=-1)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            viz = zp[1 + di:1 + di + H, 1 + dj:1 + dj + W]
            dist = np.sqrt((dx[:, None] * dj) ** 2 + (dy * di) ** 2) * np.ones((1, W))
            with np.errstate(invalid="ignore"):
                queda = (zf - viz) / dist
            queda = np.where(np.isnan(queda), -np.inf, queda)
            m = queda > melhor
            melhor = np.where(m, queda, melhor)
            rec = np.where(m, idxp[1 + di:1 + di + H, 1 + dj:1 + dj + W], rec)
    rec[~valido] = -1
    ordem = np.argsort(-np.where(valido, zf, -np.inf), axis=None)
    ordem = ordem[valido.ravel()[ordem]].tolist()
    acc = np.where(valido, area, 0).ravel().tolist()
    r = rec.ravel().tolist()
    for c in ordem:
        d = r[c]
        if d >= 0:
            acc[d] += acc[c]
    return np.array(acc).reshape(H, W), dx


def twi_ls(acc, slope_deg, dx, valido, cap_as=300.0):
    """TWI = ln(As / tan b);  LS (Moore & Burch 1986) = (As/22.13)^0.4 * (sin b / 0.0896)^1.3, As limitado a cap_as m."""
    As = acc / dx[:, None]
    b = np.deg2rad(np.maximum(slope_deg, 0.0))
    twi = np.log(As / np.maximum(np.tan(b), 0.001))
    ls = (np.minimum(As, cap_as) / 22.13) ** 0.4 * (np.sin(b) / 0.0896) ** 1.3
    twi[~valido] = np.nan; ls[~valido] = np.nan
    return twi.astype(np.float32), ls.astype(np.float32)


def etapa_ceara():
    t0 = time.time()
    z30, t30 = mosaico(BBOX_CE, ARCSEG)
    salvar_tif(OUT / "nasadem_ceara_30m.tif", np.where(np.isnan(z30), ND, np.round(z30)).astype(np.int16), t30, ND)
    print(f"  30 m pronto ({time.time()-t0:.0f}s)")
    z90 = media_bloco(z30, 3); t90 = from_origin(t30.c, t30.f, 3 * ARCSEG, 3 * ARCSEG)
    del z30
    s90, a90 = declividade_aspecto(np.where(np.isnan(z90), np.nanmean(z90), z90), t90)
    s90[np.isnan(z90)] = np.nan; a90[np.isnan(z90)] = np.nan
    from scipy.ndimage import uniform_filter
    zf = np.where(np.isnan(z90), 0, z90); w = (~np.isnan(z90)).astype(np.float32)
    tpi = {}
    for nome, tam in (("1km", 11), ("5km", 55)):
        with np.errstate(invalid="ignore", divide="ignore"):
            med = uniform_filter(zf, tam) / np.maximum(uniform_filter(w, tam), 1e-6)
        tpi[nome] = np.where(np.isnan(z90), np.nan, z90 - med).astype(np.float32)
    salvar_tif(OUT / "nasadem_ceara_90m.tif", z90, t90, np.nan, "float32")
    salvar_tif(OUT / "declividade_ceara_90m.tif", s90, t90, np.nan, "float32")
    salvar_tif(OUT / "aspecto_ceara_90m.tif", a90, t90, np.nan, "float32")
    salvar_tif(OUT / "tpi1km_ceara_90m.tif", tpi["1km"], t90, np.nan, "float32")
    salvar_tif(OUT / "tpi5km_ceara_90m.tif", tpi["5km"], t90, np.nan, "float32")
    # hidrologia a 270 m
    z270 = media_bloco(z90, 3); t270 = from_origin(t90.c, t90.f, 9 * ARCSEG, 9 * ARCSEG)
    val = ~np.isnan(z270) & (z270 > -5)
    print(f"  priority-flood {z270.shape} ...", flush=True)
    t1 = time.time(); zfill = priority_flood(np.where(val, z270, 0), val); print(f"    flood {time.time()-t1:.0f}s", flush=True)
    t1 = time.time(); acc, dx = acumulacao_d8(zfill, val, t270); print(f"    acumulacao {time.time()-t1:.0f}s", flush=True)
    s270, _ = declividade_aspecto(np.where(val, z270, 0), t270); s270[~val] = np.nan
    twi, ls = twi_ls(acc, s270, dx, val)
    import xarray as xr
    H, W = z270.shape
    lons = t270.c + t270.a * (np.arange(W) + 0.5); lats = t270.f - t270.a * (np.arange(H) + 0.5)
    ds = xr.Dataset({"elev": (("lat", "lon"), z270), "elev_preenchida": (("lat", "lon"), np.where(val, zfill, np.nan).astype(np.float32)),
                     "declividade": (("lat", "lon"), s270), "area_contribuicao_m2": (("lat", "lon"), np.where(val, acc, np.nan).astype(np.float32)),
                     "twi": (("lat", "lon"), twi), "ls_rusle": (("lat", "lon"), ls)},
                    coords={"lat": lats, "lon": lons},
                    attrs={"fonte": "NASADEM (PC) media de bloco 9x9 de 1 arcseg", "res_graus": 9 * ARCSEG,
                           "metodos": "priority-flood epsilon (Barnes 2014); D8 maior declive; TWI=ln(As/tan b); LS Moore&Burch 1986 com As<=300 m"})
    ds.to_netcdf(OUT / "ceara_270m_hidrologia.nc", encoding={v: {"zlib": True, "complevel": 4} for v in ds.data_vars})
    print(f"  ceara ok ({time.time()-t0:.0f}s)")


def etapa_aoi():
    import xarray as xr
    linhas = []
    for nome in AOIS:
        bb = bbox_aoi(nome, AOI_MEIA + 0.05)  # folga para a bacia de contribuicao
        z, t = mosaico(bb, ARCSEG, nthreads=4)
        val = ~np.isnan(z)
        s, a = declividade_aspecto(np.where(val, z, np.nanmean(z)), t)
        zf = priority_flood(np.where(val, z, 0), val)
        acc, dx = acumulacao_d8(zf, val, t)
        twi, ls = twi_ls(acc, s, dx, val)
        H, W = z.shape
        lons = t.c + t.a * (np.arange(W) + 0.5); lats = t.f - t.a * (np.arange(H) + 0.5)
        ds = xr.Dataset({"elev": (("lat", "lon"), z), "declividade": (("lat", "lon"), s), "aspecto": (("lat", "lon"), a),
                         "twi": (("lat", "lon"), twi), "ls_rusle": (("lat", "lon"), ls)}, coords={"lat": lats, "lon": lons},
                        attrs={"aoi": nome, "descricao": AOIS[nome][2], "res": "1 arcseg (~30 m)"})
        x0, y0, x1, y1 = bbox_aoi(nome)
        ds = ds.sel(lon=slice(x0, x1), lat=slice(y1, y0))
        ds.to_netcdf(OUT / f"srtm_aoi_{nome}.nc", encoding={v: {"zlib": True, "complevel": 4} for v in ds.data_vars})
        d = {"aoi": nome}
        for v in ("elev", "declividade", "twi", "ls_rusle"):
            x = ds[v].values[np.isfinite(ds[v].values)]
            d.update({f"{v}_media": float(x.mean()), f"{v}_p10": float(np.percentile(x, 10)),
                      f"{v}_p50": float(np.percentile(x, 50)), f"{v}_p90": float(np.percentile(x, 90))})
        sl = ds["declividade"].values; sl = sl[np.isfinite(sl)]
        d["frac_decl_gt8pct"] = float((np.tan(np.deg2rad(sl)) > 0.08).mean())
        d["frac_decl_gt20pct"] = float((np.tan(np.deg2rad(sl)) > 0.20).mean())
        linhas.append(d)
        print(f"  AOI {nome} ok", flush=True)
    df = pd.DataFrame(linhas)
    df.to_parquet(OUT / "srtm_aoi_estatico.parquet", index=False)
    DERIV.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DERIV / "srtm_aoi_estatico.parquet", index=False)


def etapa_nordeste():
    z, t = mosaico(BBOX_NE, 1 / 120)
    salvar_tif(OUT / "nasadem_nordeste_1km.tif", z, t, np.nan, "float32")
    s, _ = declividade_aspecto(np.where(np.isnan(z), np.nanmean(z), z), t)
    s[np.isnan(z)] = np.nan
    salvar_tif(OUT / "declividade_nordeste_1km.tif", s, t, np.nan, "float32")


def etapa_global():
    from shapely.geometry import box
    from shapely.strtree import STRtree
    c = cli(assinado=False)
    reg = {}
    for col in ("nasadem", "cop-dem-glo-30"):
        t0 = time.time()
        cent = set()
        for it in c.search(collections=[col], limit=1000).items():
            b = it.bbox
            cent.add((math.floor((b[0] + b[2]) / 2), math.floor((b[1] + b[3]) / 2)))
        reg[col] = cent
        print(f"  {col}: {len(cent)} tiles ({time.time()-t0:.0f}s)", flush=True)
    terra = terra_gdf().geometry.values
    arv = STRtree(terra)
    linhas = []
    for lat in range(-90, 90):
        for lon in range(-180, 180):
            cel = box(lon, lat, lon + 1, lat + 1)
            tem_terra = len(arv.query(cel, predicate="intersects")) > 0
            linhas.append({"lon": lon, "lat": lat, "terra": tem_terra,
                           "nasadem": (lon, lat) in reg["nasadem"], "copdem": (lon, lat) in reg["cop-dem-glo-30"]})
    df = pd.DataFrame(linhas)
    df.to_parquet(OUT / "srtm_cobertura_global.parquet", index=False)
    print("  global ok", df[["terra", "nasadem", "copdem"]].sum().to_dict())


def etapa_munic():
    from rasterio.features import rasterize
    with rasterio.open(OUT / "nasadem_ceara_90m.tif") as src:
        z = src.read(1); t = src.transform
    with rasterio.open(OUT / "declividade_ceara_90m.tif") as src:
        s = src.read(1)
    mun = municipios_ce_gdf()
    nomes = pd.read_json(REF / "ceara_municipios_nomes.json")
    nomes = dict(zip(nomes["id"].astype(str), nomes["nome"]))
    lab = rasterize([(g, i + 1) for i, g in enumerate(mun.geometry)], out_shape=z.shape, transform=t, fill=0, dtype="int32")
    linhas = []
    tg = np.tan(np.deg2rad(s))
    for i, cod in enumerate(mun["codarea"].astype(str)):
        m = (lab == i + 1) & np.isfinite(z)
        if m.sum() == 0:
            continue
        zz = z[m]; ss = s[m]; tt = tg[m]
        linhas.append({"codarea": cod, "municipio": nomes.get(cod, cod), "n_pix": int(m.sum()),
                       "elev_media": float(zz.mean()), "elev_min": float(zz.min()), "elev_max": float(zz.max()),
                       "elev_p90": float(np.percentile(zz, 90)), "amplitude": float(zz.max() - zz.min()),
                       "decl_media_graus": float(np.nanmean(ss)),
                       "frac_plano_0a3": float((tt <= 0.03).mean()), "frac_suave_3a8": float(((tt > 0.03) & (tt <= 0.08)).mean()),
                       "frac_ondulado_8a20": float(((tt > 0.08) & (tt <= 0.20)).mean()),
                       "frac_forte_20a45": float(((tt > 0.20) & (tt <= 0.45)).mean()), "frac_montanhoso_gt45": float((tt > 0.45).mean())})
    df = pd.DataFrame(linhas)
    df.to_parquet(OUT / "srtm_municipios_ce.parquet", index=False)
    df.to_parquet(DERIV / "srtm_municipios_ce.parquet", index=False)
    print("  munic ok", len(df))


if __name__ == "__main__":
    etapas = sys.argv[1:] or ["ceara", "aoi", "munic", "nordeste", "global"]
    t0 = time.time()
    for e in etapas:
        try:
            print("==", e, flush=True)
            {"ceara": etapa_ceara, "aoi": etapa_aoi, "nordeste": etapa_nordeste, "global": etapa_global, "munic": etapa_munic}[e]()
        except Exception:
            traceback.print_exc()
    registrar_manifesto("srtm", {
        "fonte": "Microsoft Planetary Computer - colecao nasadem (NASADEM_HGT v001, reprocessamento NASA do SRTM 2000); comparacao com cop-dem-glo-30",
        "url": STAC + "/collections/nasadem",
        "recortes": {"ceara_30m": BBOX_CE, "nordeste_1km": BBOX_NE, "aois_30m": {k: bbox_aoi(k) for k in AOIS}},
        "derivados": "declividade, aspecto, TPI 1/5 km (90 m); TWI e LS-RUSLE (270 m estado; 30 m AOIs)",
        "arquivos": sorted(p.name for p in OUT.iterdir() if p.is_file()), "tamanho_bytes": tamanho_pasta(OUT),
        "duracao_s": round(time.time() - t0),
    })
    print("FIM", round(time.time() - t0), "s")
