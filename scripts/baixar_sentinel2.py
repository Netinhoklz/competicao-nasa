"""Sentinel-2 L2A (Planetary Computer, sentinel-2-l2a; arquivo completo, offset das baselines >= 04.00 tratado) + HLS v2 (Planetary Computer).
Obs.: o Earth Search sentinel-2-c1-l2a foi testado e descartado: arquivo incompleto (2017: 1 cena, 2018: 42, 2022: 13 numa AOI).

Etapas:
  meta   - metadados STAC das cenas que tocam o Ceara (2015-hoje) -> s2_stac_ceara.parquet
  global - amostras STAC globais (2023) -> s2_stac_global.parquet
  aoi    - cubo por AOI a 20 m (NDVI, NDMI; mascara SCL) 2017-hoje -> s2_aoi_<nome>.nc + s2_aoi_cenas.parquet
  hls    - HLS L30/S30 (2020-hoje): estatisticas por cena nas AOIs -> hls_aoi_cenas.parquet
"""
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from frente_c_util import *  # noqa

import numpy as np
import pandas as pd
import pystac_client

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
ES = "https://planetarycomputer.microsoft.com/api/stac/v1"
COL = "sentinel-2-l2a"
import planetary_computer
OUT = pasta("sentinel2")
CRS = "EPSG:32724"
RES = 20.0
SCL_VALIDO = (4, 5, 6)  # vegetacao, solo nao vegetado, agua


def props_linha(it):
    p = it.properties
    return {
        "id": it.id, "datetime": it.datetime, "platform": p.get("platform"),
        "cloud_cover": p.get("eo:cloud_cover"), "mgrs": p.get("s2:mgrs_tile"),
        "baseline": p.get("s2:processing_baseline"), "nodata_pct": p.get("s2:nodata_pixel_percentage"),
        "veg_pct": p.get("s2:vegetation_percentage"), "nao_veg_pct": p.get("s2:not_vegetated_percentage"),
        "agua_pct": p.get("s2:water_percentage"), "sombra_pct": p.get("s2:cloud_shadow_percentage"),
        "nuvem_alta_pct": p.get("s2:high_proba_clouds_percentage"), "cirro_pct": p.get("s2:thin_cirrus_percentage"),
        "sun_elev": 90 - p["s2:mean_solar_zenith"] if p.get("s2:mean_solar_zenith") is not None else None,
    }


def etapa_meta():
    from shapely.geometry import mapping
    ce = ceara_gdf().geometry.iloc[0].simplify(0.02)
    cli = pystac_client.Client.open(ES)
    linhas = []
    for ano in range(2015, 2027):
        for sem in (("01-01", "06-30"), ("07-01", "12-31")):
            t0 = time.time()
            n0 = len(linhas)
            busca = cli.search(collections=[COL], intersects=mapping(ce), datetime=f"{ano}-{sem[0]}/{ano}-{sem[1]}", limit=1000)
            for it in busca.items():
                linhas.append(props_linha(it))
            print(f"meta {ano} {sem[0]}: {len(linhas)-n0} cenas ({time.time()-t0:.0f}s)")
    df = pd.DataFrame(linhas)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df.to_parquet(OUT / "s2_stac_ceara.parquet", index=False)
    print("meta total", len(df))


def etapa_global():
    from baixar_landsat import AMOSTRAS_GLOBAIS
    cli = pystac_client.Client.open(ES)
    linhas = []
    for nome, (lon, lat) in AMOSTRAS_GLOBAIS.items():
        bb = (lon - 0.5, lat - 0.5, lon + 0.5, lat + 0.5)
        t0 = time.time()
        its = list(cli.search(collections=[COL], bbox=bb, datetime="2023-01-01/2023-12-31", limit=1000).items())
        for it in its:
            d = props_linha(it)
            d.update({"amostra": nome, "lon": lon, "lat": lat})
            linhas.append(d)
        if not its:
            linhas.append({"amostra": nome, "lon": lon, "lat": lat, "id": None})
        print(f"global {nome}: {len(its)} ({time.time()-t0:.0f}s)")
    df = pd.DataFrame(linhas)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df.to_parquet(OUT / "s2_stac_global.parquet", index=False)


def offset_baseline(it):
    """A ESA passou a somar 1000 ao DN a partir da baseline 04.00 (25/01/2022)."""
    try:
        return -0.1 if float(it.properties.get("s2:processing_baseline", "0")) >= 4.0 else 0.0
    except ValueError:
        return 0.0


def refl(a, off):
    r = a.astype(np.float32) * 1e-4 + off
    r[a == 0] = np.nan
    return r


def ler_cena(it, nome, transform, w, h):
    it = planetary_computer.sign(it)
    off = offset_baseline(it)
    scl, _, _, _ = ler_na_grade(it.assets["SCL"].href, CRS, transform, w, h, "nearest", nodata=0)
    ok = np.isin(scl, SCL_VALIDO)
    red, _, _, _ = ler_na_grade(it.assets["B04"].href, CRS, transform, w, h, "average", nodata=0)
    nir, _, _, _ = ler_na_grade(it.assets["B08"].href, CRS, transform, w, h, "average", nodata=0)
    sw, _, _, _ = ler_na_grade(it.assets["B11"].href, CRS, transform, w, h, "nearest", nodata=0)
    red, nir, sw = refl(red, off), refl(nir, off), refl(sw, off)
    valido = ok & np.isfinite(red) & np.isfinite(nir) & (nir > 0) & (red > -0.05) & (red < 1) & (nir < 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = (nir - red) / (nir + red)
        ndmi = (nir - sw) / (nir + sw)
    ndvi[~valido] = np.nan
    ndmi[~valido] = np.nan
    p = it.properties
    est = {"aoi": nome, "id": it.id, "datetime": it.datetime, "platform": p.get("platform"),
           "mgrs": p.get("s2:mgrs_tile"), "baseline": p.get("s2:processing_baseline"),
           "cloud_cena": p.get("eo:cloud_cover"), "frac_valida": float(valido.mean()),
           "frac_nuvem_scl": float(np.isin(scl, (8, 9, 10)).mean()), "frac_sombra_scl": float((scl == 3).mean()),
           "frac_agua": float(((scl == 6) & valido).mean())}
    for nv, arr in (("ndvi", ndvi), ("ndmi", ndmi)):
        v = arr[np.isfinite(arr)]
        if v.size >= 100:
            est.update({f"{nv}_media": float(v.mean()), f"{nv}_mediana": float(np.median(v)),
                        f"{nv}_p10": float(np.percentile(v, 10)), f"{nv}_p90": float(np.percentile(v, 90)),
                        f"{nv}_dp": float(v.std())})
    v = ndvi[np.isfinite(ndvi)]
    if v.size >= 100:
        est["frac_solo_exposto"] = float((v < 0.2).mean())
        est["frac_veg_densa"] = float((v > 0.6).mean())
    cubo = None
    if est["frac_valida"] >= 0.02:
        cubo = {"ndvi": ndvi.astype(np.float32), "ndmi": ndmi.astype(np.float32)}
    return est, cubo


def processar_aoi(nome, periodo="2017-01-01/2026-12-31", nthreads=20, max_nuvem=90):
    import xarray as xr
    bb = bbox_aoi(nome)
    transform, w, h = grade_aoi(nome, CRS, RES)
    cli = pystac_client.Client.open(ES)
    its = list(cli.search(collections=[COL], bbox=bb, datetime=periodo, limit=1000).items())
    its = [i for i in its if fracao_cobertura(i.geometry, bb) > 0.5]
    n_total = len(its)
    # duplicatas (tiles vizinhos e reprocessamentos): mesma data+satelite -> maior cobertura, depois maior baseline
    melhor = {}
    for i in its:
        k = (i.datetime.date().isoformat(), str(i.properties.get("platform", "")).lower())
        chave = (round(fracao_cobertura(i.geometry, bb), 3), str(i.properties.get("s2:processing_baseline", "")))
        if k not in melhor or chave > melhor[k][0]:
            melhor[k] = (chave, i)
    its = [v[1] for v in sorted(melhor.values(), key=lambda x: x[1].datetime)]
    n_unicas = len(its)
    pul = [i for i in its if (i.properties.get("eo:cloud_cover") or 0) > max_nuvem]
    its = [i for i in its if (i.properties.get("eo:cloud_cover") or 0) <= max_nuvem]
    print(f"[{nome}] {n_total} itens -> {n_unicas} datas unicas -> {len(its)} com nuvem<={max_nuvem}% ({len(pul)} puladas)", flush=True)
    ests = [{"aoi": nome, "id": i.id, "datetime": i.datetime, "platform": i.properties.get("platform"),
             "cloud_cena": i.properties.get("eo:cloud_cover"), "frac_valida": 0.0, "pulada_nuvem": True} for i in pul]
    cubos = {}
    t0 = time.time()
    with ThreadPoolExecutor(nthreads) as ex:
        fut = {ex.submit(ler_cena, it, nome, transform, w, h): it for it in its}
        for k, f in enumerate(as_completed(fut), 1):
            it = fut[f]
            try:
                e, c = f.result()
                ests.append(e)
                if c is not None:
                    cubos[it.datetime] = (it.id, it.properties.get("platform"), c)
            except Exception as exc:
                ests.append({"aoi": nome, "id": it.id, "datetime": it.datetime, "erro": repr(exc)[:200]})
            if k % 100 == 0:
                print(f"  [{nome}] {k}/{len(its)} ({time.time()-t0:.0f}s)", flush=True)
    if cubos:
        tempos = sorted(cubos)
        xs = transform.c + RES * (np.arange(w) + 0.5)
        ys = transform.f - RES * (np.arange(h) + 0.5)
        ds = xr.Dataset(
            {v: (("time", "y", "x"), np.stack([cubos[t][2][v] for t in tempos]), {"long_name": v.upper()})
             for v in ("ndvi", "ndmi")},
            coords={"time": pd.to_datetime([t.replace(tzinfo=None) for t in tempos]), "x": xs, "y": ys,
                    "scene_id": ("time", [cubos[t][0] for t in tempos]),
                    "platform": ("time", [cubos[t][1] for t in tempos])},
            attrs={"crs": CRS, "res_m": RES, "aoi": nome, "descricao": AOIS[nome][2],
                   "fonte": "Planetary Computer sentinel-2-l2a", "mascara": f"SCL em {SCL_VALIDO}",
                   "transform": list(transform)[:6]})
        enc = {v: {"zlib": True, "complevel": 4, "dtype": "int16", "scale_factor": 1e-4, "_FillValue": -32768,
                   "chunksizes": (1, h, w)} for v in ("ndvi", "ndmi")}
        arq = OUT / f"s2_aoi_{nome}.nc"
        ds.to_netcdf(arq, encoding=enc)
        print(f"  [{nome}] cubo {arq.name} {arq.stat().st_size/1e6:.1f} MB {dict(ds.sizes)}", flush=True)
    return ests


def etapa_aoi():
    todos = []
    for nome in AOIS:
        todos += processar_aoi(nome)
        pd.DataFrame(todos).to_parquet(OUT / "s2_aoi_cenas.parquet", index=False)


# ---------------- HLS (Planetary Computer) -----------------
def ler_hls(it, nome, transform, w, h):
    import planetary_computer
    it = planetary_computer.sign(it)
    nirb = "B05" if it.collection_id == "hls2-l30" else "B8A"
    swb = "B06" if it.collection_id == "hls2-l30" else "B11"
    fm, _, _, _ = ler_na_grade(it.assets["Fmask"].href, "EPSG:32624", transform, w, h, "nearest", nodata=255)
    ok = ((fm & 0b1110) == 0) & (fm != 255)
    arrs = {}
    for b in ("B04", nirb, swb):
        a, _, esc, off = ler_na_grade(it.assets[b].href, "EPSG:32624", transform, w, h, "nearest", nodata=-9999)
        r = a.astype(np.float32) * (esc if esc and esc != 1.0 else 1e-4) + (off or 0.0)
        r[a == -9999] = np.nan
        arrs[b] = r
    red, nir, sw = arrs["B04"], arrs[nirb], arrs[swb]
    valido = ok & np.isfinite(red) & np.isfinite(nir) & (nir > 0) & (red > -0.05) & (red < 1) & (nir < 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = (nir - red) / (nir + red)
        ndmi = (nir - sw) / (nir + sw)
    est = {"aoi": nome, "id": it.id, "colecao": it.collection_id, "datetime": it.datetime,
           "cloud_cena": it.properties.get("eo:cloud_cover"), "frac_valida": float(valido.mean())}
    for nv, arr in (("ndvi", ndvi), ("ndmi", ndmi)):
        v = arr[valido & np.isfinite(arr)]
        if v.size >= 50:
            est.update({f"{nv}_media": float(v.mean()), f"{nv}_mediana": float(np.median(v)),
                        f"{nv}_p10": float(np.percentile(v, 10)), f"{nv}_p90": float(np.percentile(v, 90))})
    return est


def etapa_hls(nthreads=20, max_nuvem=80):
    import planetary_computer
    cli = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
    todos = []
    for nome in AOIS:
        bb = bbox_aoi(nome)
        transform, w, h = grade_aoi(nome, "EPSG:32624", 30.0)
        its = list(cli.search(collections=["hls2-l30", "hls2-s30"], bbox=bb, datetime="2020-01-01/2026-12-31", limit=1000).items())
        its = [i for i in its if fracao_cobertura(i.geometry, bb) > 0.5]
        # duplicatas: mesma data e mesma colecao -> maior cobertura
        melhor = {}
        for i in its:
            k = (i.datetime.date().isoformat(), i.collection_id)
            f = fracao_cobertura(i.geometry, bb)
            if k not in melhor or f > melhor[k][0]:
                melhor[k] = (f, i)
        its = [v[1] for v in melhor.values() if (v[1].properties.get("eo:cloud_cover") or 0) <= max_nuvem]
        print(f"[HLS {nome}] {len(its)} cenas", flush=True)
        t0 = time.time()
        with ThreadPoolExecutor(nthreads) as ex:
            fut = {ex.submit(ler_hls, it, nome, transform, w, h): it for it in its}
            for k, f in enumerate(as_completed(fut), 1):
                try:
                    todos.append(f.result())
                except Exception as exc:
                    it = fut[f]
                    todos.append({"aoi": nome, "id": it.id, "datetime": it.datetime, "erro": repr(exc)[:200]})
                if k % 100 == 0:
                    print(f"  [HLS {nome}] {k}/{len(its)} ({time.time()-t0:.0f}s)", flush=True)
        pd.DataFrame(todos).to_parquet(OUT / "hls_aoi_cenas.parquet", index=False)


if __name__ == "__main__" and len(sys.argv) >= 3 and sys.argv[1] == "aoi_um":
    # uma AOI por processo (paralelismo entre AOIs); depois juntar com s2_aoi_cenas.parquet
    nome = sys.argv[2]
    pd.DataFrame(processar_aoi(nome)).to_parquet(OUT / f"s2_aoi_cenas_{nome}.parquet", index=False)
    print("FIM aoi_um", nome)
    sys.exit(0)

if __name__ == "__main__":
    etapas = sys.argv[1:] or ["meta", "global", "aoi", "hls"]
    t0 = time.time()
    for e in etapas:
        try:
            {"meta": etapa_meta, "global": etapa_global, "aoi": etapa_aoi, "hls": etapa_hls}[e]()
        except Exception:
            traceback.print_exc()
    registrar_manifesto("sentinel2", {
        "fonte": "Microsoft Planetary Computer - sentinel-2-l2a (ESA Copernicus, Sen2Cor); HLS v2 (hls2-l30/hls2-s30). Earth Search C1 descartado por arquivo incompleto",
        "url": ES + "/collections/" + COL,
        "recortes": {"ceara_meta": "cenas que intersectam o Ceara", "aois": {k: bbox_aoi(k) for k in AOIS}},
        "periodos": {"S2 cubos 20 m": "2017-01 a hoje (cenas com nuvem <= 90%)", "HLS": "2020-01 a hoje (nuvem <= 80%)"},
        "grade": f"{CRS} {RES} m (B04/B08 media 10->20 m)", "arquivos": sorted(p.name for p in OUT.iterdir() if p.is_file()),
        "tamanho_bytes": tamanho_pasta(OUT), "duracao_s": round(time.time() - t0),
    })
    print("FIM", round(time.time() - t0), "s")
