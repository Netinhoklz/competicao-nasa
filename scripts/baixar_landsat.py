"""Landsat Collection 2 Level-2 (Planetary Computer, landsat-c2-l2).

Etapas:
  meta   - metadados STAC de todas as cenas que tocam o Ceara (1982-hoje) -> landsat_stac_ceara.parquet
  global - amostras STAC em todos os continentes/faixas de latitude (2023) -> landsat_stac_global.parquet
  aoi    - Landsat 8/9 (2013-hoje): cubo por AOI (red, nir08, swir16 + NDVI/NDMI, mascara QA) em NetCDF
  hist   - Landsat 4/5/7 (1984-2012): so estatisticas por cena nas AOIs (serie longa p/ secas)
Uso: python baixar_landsat.py meta global aoi hist
"""
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from frente_c_util import *  # noqa

import numpy as np
import pandas as pd
import planetary_computer
import pystac_client

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
COL = "landsat-c2-l2"
OUT = pasta("landsat")
CRS = "EPSG:32624"  # Landsat entrega o Ceara na zona UTM 24 (codigo norte, northing negativo)
RES = 30.0


def cliente(assinado=False):
    return pystac_client.Client.open(STAC, modifier=planetary_computer.sign_inplace if assinado else None)


def props_linha(it):
    p = it.properties
    return {
        "id": it.id, "datetime": it.datetime, "platform": p.get("platform"),
        "instrumento": ",".join(p.get("instruments", []) or []),
        "cloud_cover": p.get("eo:cloud_cover"), "cloud_cover_land": p.get("landsat:cloud_cover_land"),
        "path": p.get("landsat:wrs_path"), "row": p.get("landsat:wrs_row"),
        "categoria": p.get("landsat:collection_category"), "sun_elev": p.get("view:sun_elevation"),
        "correcao": p.get("landsat:correction"),
    }


def etapa_meta():
    import json
    from shapely.geometry import mapping
    ce = ceara_gdf().geometry.iloc[0].simplify(0.02)
    cli = cliente()
    linhas = []
    for ano in range(1982, 2027):
        t0 = time.time()
        busca = cli.search(collections=[COL], intersects=mapping(ce), datetime=f"{ano}-01-01/{ano}-12-31", limit=1000)
        n0 = len(linhas)
        for it in busca.items():
            linhas.append(props_linha(it))
        print(f"meta {ano}: {len(linhas)-n0} cenas ({time.time()-t0:.1f}s)")
    df = pd.DataFrame(linhas)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df.to_parquet(OUT / "landsat_stac_ceara.parquet", index=False)
    print("meta total", len(df))


AMOSTRAS_GLOBAIS = {
    # nome: (lon, lat)  caixas de 1 grau
    "Ceara_BR": (-39.0, -5.0), "Amazonia_BR": (-60.0, -3.0), "Pampa_AR": (-61.0, -34.0), "Patagonia_AR": (-70.0, -50.0),
    "TerraDoFogo_AR": (-68.0, -54.5), "Iowa_US": (-93.5, 42.0), "Mexico": (-102.0, 22.0), "Canada_N": (-95.0, 70.0),
    "Groenlandia_N": (-40.0, 81.0), "Sahara_DZ": (5.0, 23.0), "Sahel_NE": (8.0, 14.0), "Etiopia": (39.0, 9.0),
    "Congo": (23.0, -1.0), "AfricaSul": (25.0, -29.0), "Franca": (2.0, 48.5), "Ucrania": (32.0, 49.0),
    "Siberia": (100.0, 62.0), "Svalbard": (16.0, 78.5), "India": (78.0, 22.0), "China_N": (115.0, 37.0),
    "Mongolia": (103.0, 46.0), "Indonesia": (113.0, -1.0), "Japao": (139.0, 36.0), "Australia": (135.0, -25.0),
    "NovaZelandia": (172.0, -43.5), "Antartica_Peninsula": (-60.0, -64.5), "Antartica_interior": (0.0, -80.0),
}


def etapa_global():
    cli = cliente()
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
        print(f"global {nome}: {len(its)} cenas ({time.time()-t0:.1f}s)")
    df = pd.DataFrame(linhas)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df.to_parquet(OUT / "landsat_stac_global.parquet", index=False)


def mascara_qa(qa: np.ndarray) -> np.ndarray:
    """True = pixel limpo: sem fill(0), nuvem dilatada(1), cirro(2), nuvem(3), sombra(4), neve(5)."""
    ruim = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5)
    return (qa & ruim) == 0


def ler_cena(it, nome, transform, w, h, guardar_cubo=True):
    it = planetary_computer.sign(it)
    qa, _, _, _ = ler_na_grade(it.assets["qa_pixel"].href, CRS, transform, w, h, "nearest", nodata=1)
    ok = mascara_qa(qa.astype(np.uint16))
    bandas = {}
    for b in ("red", "nir08", "swir16"):
        a, nd, _, _ = ler_na_grade(it.assets[b].href, CRS, transform, w, h, "nearest", nodata=0)
        refl = a.astype(np.float32) * 0.0000275 - 0.2
        refl[(a == 0)] = np.nan
        bandas[b] = refl
    valido = ok & np.isfinite(bandas["red"]) & np.isfinite(bandas["nir08"])
    valido &= (bandas["red"] > -0.01) & (bandas["nir08"] > 0) & (bandas["red"] < 1.0) & (bandas["nir08"] < 1.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = (bandas["nir08"] - bandas["red"]) / (bandas["nir08"] + bandas["red"])
        ndmi = (bandas["nir08"] - bandas["swir16"]) / (bandas["nir08"] + bandas["swir16"])
    ndvi[~valido] = np.nan
    ndmi[~valido] = np.nan
    agua = ((qa.astype(np.uint16) >> 7) & 1).astype(bool) & valido
    frac = float(valido.mean())
    p = it.properties
    est = {
        "aoi": nome, "id": it.id, "datetime": it.datetime, "platform": p.get("platform"),
        "path": p.get("landsat:wrs_path"), "row": p.get("landsat:wrs_row"), "cloud_cena": p.get("eo:cloud_cover"),
        "frac_valida": frac, "frac_agua": float(agua.mean()),
    }
    for nomev, arr in (("ndvi", ndvi), ("ndmi", ndmi)):
        v = arr[np.isfinite(arr)]
        if v.size >= 50:
            est.update({f"{nomev}_media": float(v.mean()), f"{nomev}_mediana": float(np.median(v)),
                        f"{nomev}_p10": float(np.percentile(v, 10)), f"{nomev}_p90": float(np.percentile(v, 90)),
                        f"{nomev}_dp": float(v.std())})
    # fracao de solo exposto (NDVI<0.2) e vegetacao densa (NDVI>0.6) entre os pixels validos
    v = ndvi[np.isfinite(ndvi)]
    if v.size >= 50:
        est["frac_solo_exposto"] = float((v < 0.2).mean())
        est["frac_veg_densa"] = float((v > 0.6).mean())
    cubo = None
    if guardar_cubo and frac >= 0.02:
        def q(a):
            o = np.where(np.isfinite(a) & valido, np.round(a * 10000), -32768)
            return np.clip(o, -32768, 32767).astype(np.int16)
        cubo = {"red": q(bandas["red"]), "nir08": q(bandas["nir08"]), "swir16": q(bandas["swir16"]),
                "ndvi": q(ndvi), "ndmi": q(ndmi)}
    return est, cubo


def processar_aoi(nome, plataformas, periodo, guardar_cubo, nthreads=20):
    import xarray as xr
    bb = bbox_aoi(nome)
    transform, w, h = grade_aoi(nome, CRS, RES)
    cli = cliente()
    its = list(cli.search(collections=[COL], bbox=bb, datetime=periodo, limit=1000,
                          query={"platform": {"in": plataformas}}).items())
    its = [i for i in its if fracao_cobertura(i.geometry, bb) > 0.5]
    its = escolher_por_data(its, bb)
    print(f"[{nome}] {len(its)} cenas unicas {plataformas} {periodo}", flush=True)
    ests, cubos = [], {}
    t0 = time.time()
    with ThreadPoolExecutor(nthreads) as ex:
        fut = {ex.submit(ler_cena, it, nome, transform, w, h, guardar_cubo): it for it in its}
        for k, f in enumerate(as_completed(fut), 1):
            it = fut[f]
            try:
                e, c = f.result()
                ests.append(e)
                if c is not None:
                    cubos[it.datetime] = (it.id, it.properties.get("platform"), c)
            except Exception as exc:
                ests.append({"aoi": nome, "id": it.id, "datetime": it.datetime, "erro": repr(exc)[:200]})
            if k % 50 == 0:
                print(f"  [{nome}] {k}/{len(its)} ({time.time()-t0:.0f}s)", flush=True)
    if guardar_cubo and cubos:
        tempos = sorted(cubos)
        xs = transform.c + RES * (np.arange(w) + 0.5)
        ys = transform.f - RES * (np.arange(h) + 0.5)
        dv = {}
        for v in ("red", "nir08", "swir16", "ndvi", "ndmi"):
            dv[v] = (("time", "y", "x"), np.stack([cubos[t][2][v] for t in tempos]),
                     {"scale_factor": 1e-4, "_FillValue": -32768,
                      "long_name": {"red": "reflectancia superficie vermelho", "nir08": "reflectancia NIR",
                                    "swir16": "reflectancia SWIR 1.6um", "ndvi": "NDVI", "ndmi": "NDMI (NIR-SWIR1)"}[v]})
        ds = xr.Dataset(
            {k: (d, a) for k, (d, a, _) in dv.items()},
            coords={"time": pd.to_datetime([t.replace(tzinfo=None) for t in tempos]), "x": xs, "y": ys,
                    "scene_id": ("time", [cubos[t][0] for t in tempos]),
                    "platform": ("time", [cubos[t][1] for t in tempos])},
            attrs={"crs": CRS, "res_m": RES, "aoi": nome, "descricao": AOIS[nome][2], "fonte": "Planetary Computer landsat-c2-l2",
                   "mascara": "QA_PIXEL bits 0-5 (fill, nuvem dilatada, cirro, nuvem, sombra, neve)",
                   "transform": list(transform)[:6]},
        )
        enc = {}
        for k, (_, _, at) in dv.items():
            ds[k].encoding = {}
            enc[k] = {"zlib": True, "complevel": 4, "dtype": "int16", "scale_factor": 1e-4, "_FillValue": -32768,
                      "chunksizes": (1, h, w)}
            ds[k].attrs = {"long_name": at["long_name"]}
        # as variaveis estao em inteiros escalados; converte para float para o encoder reaplicar a escala
        for k in dv:
            arr = ds[k].values.astype(np.float32)
            arr[arr == -32768] = np.nan
            ds[k] = (("time", "y", "x"), arr * 1e-4, ds[k].attrs)
        arq = OUT / f"landsat_aoi_{nome}.nc"
        ds.to_netcdf(arq, encoding=enc)
        print(f"  [{nome}] cubo salvo {arq.name} {arq.stat().st_size/1e6:.1f} MB {ds.sizes}", flush=True)
    return ests


def etapa_aoi():
    todos = []
    for nome in AOIS:
        todos += processar_aoi(nome, ["landsat-8", "landsat-9"], "2013-03-01/2026-12-31", True)
        pd.DataFrame(todos).to_parquet(OUT / "landsat_aoi_cenas_l89.parquet", index=False)


def etapa_hist():
    todos = []
    for nome in AOIS:
        todos += processar_aoi(nome, ["landsat-4", "landsat-5", "landsat-7"], "1984-01-01/2012-12-31", False)
        pd.DataFrame(todos).to_parquet(OUT / "landsat_aoi_cenas_hist.parquet", index=False)


if __name__ == "__main__":
    etapas = sys.argv[1:] or ["meta", "global", "aoi", "hist"]
    t0 = time.time()
    for e in etapas:
        try:
            {"meta": etapa_meta, "global": etapa_global, "aoi": etapa_aoi, "hist": etapa_hist}[e]()
        except Exception:
            traceback.print_exc()
    registrar_manifesto("landsat", {
        "fonte": "Microsoft Planetary Computer - colecao landsat-c2-l2 (USGS Landsat Collection 2 Level-2)",
        "url": STAC + "/collections/" + COL,
        "recortes": {"ceara_meta": "todas as cenas que intersectam o Ceara (STAC)", "aois": {k: bbox_aoi(k) for k in AOIS}},
        "periodos": {"L8/L9 cubos": "2013-03 a hoje", "L4/5/7 estatisticas": "1984-2012"},
        "grade": f"{CRS} {RES} m alinhada", "arquivos": sorted(p.name for p in OUT.iterdir() if p.is_file()),
        "tamanho_bytes": tamanho_pasta(OUT), "duracao_s": round(time.time() - t0),
    })
    print("FIM", round(time.time() - t0), "s")
