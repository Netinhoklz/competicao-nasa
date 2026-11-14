"""GPM IMERG por duas rotas abertas (sem login Earthdata).

1) modo `power`: serie diaria longa na resolucao NATIVA 0,1 grau via NASA POWER (parametro IMERG_PRECTOT,
   time-standard=UTC; fonte declarada no cabecalho = IMERG). Endpoint regional exige caixa >= 2x2 graus e
   tem limite de egresso por requisicao -> ladrilhos de ~2,3 x 2,9 graus por ano.
   Uso: python baixar_imerg.py power CE|NE ANO_INI ANO_FIM [n_threads]
2) modo `pc`: amostra NATIVA meia-hora (V06) do Microsoft Planetary Computer (gpm-imerg-hhr, Zarr).
   Chunk = (12 meias-horas, globo inteiro) ~52 MB -> so amostras curtas. Cada chunk e global, entao a mesma
   leitura serve para validar cobertura global.
   Uso: python baixar_imerg.py pc AAAA-MM-DD AAAA-MM-DD
3) modo `global`: pontos espalhados pelo globo via POWER para checar onde ha IMERG (validacao de cobertura).
   Uso: python baixar_imerg.py global
4) modo `consolidar`: junta os JSON do modo power em NetCDF por ano.
   Uso: python baixar_imerg.py consolidar CE|NE
"""
import sys
sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa
import gzip
import json
import math
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

import numpy as np
import pandas as pd
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
OUT = pasta("imerg")
RAW = OUT / "power_bruto"
RAW.mkdir(exist_ok=True)
URL = "https://power.larc.nasa.gov/api/temporal/daily/regional"
URL_PT = "https://power.larc.nasa.gov/api/temporal/daily/point"


def ladrilhos(bbox):
    """Menores ladrilhos com lado >= 2 graus (minimo do endpoint regional)."""
    x0, y0, x1, y1 = bbox
    nx = max(1, math.floor((x1 - x0) / 2.0))
    ny = max(1, math.floor((y1 - y0) / 2.0))
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    assert dx >= 2 and dy >= 2, (dx, dy)
    return [(round(x0 + i * dx, 3), round(y0 + j * dy, 3), round(x0 + (i + 1) * dx, 3), round(y0 + (j + 1) * dy, 3))
            for i in range(nx) for j in range(ny)]


def pedir(reg, tile, ano, s):
    x0, y0, x1, y1 = tile
    ini = max(date(ano, 1, 1), date(1998, 1, 1))  # IMERG V07 no POWER comeca em 1998-01-01
    fim = min(date(ano, 12, 31), date.today() - timedelta(days=1))
    nome = RAW / f"{reg}_{ano}_{x0}_{y0}.json.gz"
    if nome.exists():
        return nome, "ja existia", 0
    partes = [(ini, fim)]
    for tentativa in range(3):
        feats = []
        ok = True
        for a, b in partes:
            prm = {"parameters": "IMERG_PRECTOT", "community": "AG", "longitude-min": x0, "longitude-max": x1,
                   "latitude-min": y0, "latitude-max": y1, "start": a.strftime("%Y%m%d"), "end": b.strftime("%Y%m%d"),
                   "format": "JSON", "time-standard": "UTC"}
            import requests
            for espera in (0, 60, 120, 240, 480):
                time.sleep(espera)
                try:
                    r = s.get(URL, params=prm, timeout=600)
                    if r.status_code == 429:
                        continue
                    break
                except requests.exceptions.RetryError:
                    continue  # 429 repetido (limite do POWER, compartilhado com outras frentes): espera e tenta
            d = r.json()
            if not d.get("features"):
                msg = str(d.get("messages") or d)[:200]
                if "egress" in msg.lower():
                    ok = False
                    break
                raise RuntimeError(f"sem features {reg} {ano} {tile}: {msg}")
            feats.extend(d["features"])
        if ok:
            with gzip.open(nome, "wt", encoding="utf-8") as f:
                json.dump({"features": feats}, f)
            return nome, f"ok {len(partes)} parte(s)", len(feats)
        # divide o periodo ao meio e tenta de novo
        novas = []
        for a, b in partes:
            m = a + (b - a) / 2
            novas += [(a, m), (m + timedelta(days=1), b)]
        partes = novas
    raise RuntimeError(f"egresso excedido mesmo dividindo {reg} {ano} {tile}")


def modo_power(reg, a0, a1, nth):
    bbox = BBOX_CE if reg == "CE" else BBOX_NE
    tiles = ladrilhos(bbox)
    print(reg, "ladrilhos", len(tiles), tiles[:2], flush=True)
    s = sessao_http()
    tarefas = [(t, a) for a in range(a0, a1 + 1) for t in tiles]
    t0 = time.time()
    n = 0
    with ThreadPoolExecutor(nth) as ex:
        fut = {ex.submit(pedir, reg, t, a, s): (t, a) for t, a in tarefas}
        for f in as_completed(fut):
            t, a = fut[f]
            n += 1
            try:
                nome, st, nf = f.result()
                print(f"[{n}/{len(tarefas)}] {a} {t} {st} pts={nf} {time.time()-t0:.0f}s", flush=True)
            except Exception:
                print(f"[{n}/{len(tarefas)}] {a} {t} ERRO {traceback.format_exc()[-400:]}", flush=True)


def consolidar(reg):
    arqs = sorted(RAW.glob(f"{reg}_*.json.gz"))
    anos = sorted({int(a.name.split("_")[1]) for a in arqs})
    bbox = BBOX_CE if reg == "CE" else BBOX_NE
    lons = np.round(np.arange(bbox[0] + 0.05, bbox[2], 0.1), 2)
    lats = np.round(np.arange(bbox[1] + 0.05, bbox[3], 0.1), 2)
    for ano in anos:
        dest = OUT / f"imerg_{reg.lower()}_diario_{ano}.nc"
        regs = {}
        for a in [x for x in arqs if int(x.name.split("_")[1]) == ano]:
            with gzip.open(a, "rt", encoding="utf-8") as f:
                d = json.load(f)
            for ft in d["features"]:
                lo, la = round(ft["geometry"]["coordinates"][0], 2), round(ft["geometry"]["coordinates"][1], 2)
                regs.setdefault((lo, la), {}).update(ft["properties"]["parameter"]["IMERG_PRECTOT"])
        datas = sorted({k for v in regs.values() for k in v})
        idx_d = {k: i for i, k in enumerate(datas)}
        arr = np.full((len(datas), len(lats), len(lons)), np.nan, dtype="float32")
        li = {v: i for i, v in enumerate(lons)}
        la_i = {v: i for i, v in enumerate(lats)}
        fora = 0
        for (lo, la), serie in regs.items():
            if lo not in li or la not in la_i:
                fora += 1
                continue
            vals = np.array([serie.get(k, -999.0) for k in datas], dtype="float32")
            vals[vals <= -998] = np.nan
            arr[:, la_i[la], li[lo]] = vals
        tempo = pd.to_datetime(datas, format="%Y%m%d")
        # o POWER devolve o ano inteiro e preenche com -999 os dias ainda sem dado: descartar dias todo-NaN
        valido = ~np.all(np.isnan(arr), axis=(1, 2))
        arr, tempo = arr[valido], tempo[valido]
        ds = xr.Dataset({"precip": (("time", "lat", "lon"), arr)}, coords={"time": tempo, "lat": lats, "lon": lons})
        ds["precip"].attrs = {"units": "mm/dia", "long_name": "IMERG total diario (dia UTC)"}
        ds.attrs = {"fonte": "GPM IMERG via NASA POWER (IMERG_PRECTOT, time-standard=UTC, resolucao nativa 0,1 grau)",
                    "recorte": str(bbox)}
        ds.to_netcdf(dest, encoding={"precip": {"zlib": True, "complevel": 5}})
        print(reg, ano, ds.sizes, "pontos fora da grade:", fora, "NaN%", float(np.isnan(arr).mean() * 100), flush=True)


def modo_pc(d_ini, d_fim):
    import planetary_computer as pc
    import pystac_client
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
    a = cat.get_collection("gpm-imerg-hhr").assets["zarr-abfs"]
    ds = xr.open_zarr(a.href, storage_options=a.extra_fields["xarray:storage_options"], consolidated=True)
    da = ds["precipitationCal"]
    t0_ref = pd.Timestamp("2000-06-01")
    dias = pd.date_range(d_ini, d_fim, freq="D")
    lon = ds["lon"].values
    lat = ds["lat"].values
    ce_lo = (lon >= BBOX_CE[0]) & (lon <= BBOX_CE[2])
    ce_la = (lat >= BBOX_CE[1]) & (lat <= BBOX_CE[3])
    ne_lo = (lon >= BBOX_NE[0]) & (lon <= BBOX_NE[2])
    ne_la = (lat >= BBOX_NE[1]) & (lat <= BBOX_NE[3])
    dest_dir = OUT / "pc_nativo"
    dest_dir.mkdir(exist_ok=True)
    import dask
    dask.config.set(scheduler="threads", num_workers=8)
    for dia in dias:
        dest = dest_dir / f"imerg_v06_{dia:%Y%m%d}.nc"
        if dest.exists():
            print(dia.date(), "ja existia", flush=True)
            continue
        t0 = time.time()
        i0 = int((dia - t0_ref) / pd.Timedelta("30min"))
        x = da.isel(time=slice(i0, i0 + 48)).values  # (48, lon, lat) mm/h
        tempos = pd.date_range(dia, periods=48, freq="30min")
        ne = x[:, ne_lo][:, :, ne_la]  # (48, lonNE, latNE)
        glob_dia = np.nansum(x, axis=0) * 0.5  # mm/dia
        n_validos = np.isfinite(x).sum(axis=0)
        # grade global 0,5 grau (media de blocos 5x5)
        g = glob_dia.reshape(720, 5, 360, 5).mean(axis=(1, 3))
        nv = n_validos.reshape(720, 5, 360, 5).mean(axis=(1, 3))
        out = xr.Dataset(
            {"precip_ne": (("time", "lon", "lat"), ne.astype("float32"), {"units": "mm/h"}),
             "global_dia_05": (("lon05", "lat05"), g.astype("float32"), {"units": "mm/dia"}),
             "global_nvalidos_05": (("lon05", "lat05"), nv.astype("float32"), {"units": "meias-horas validas (0-48)"})},
            coords={"time": tempos, "lon": lon[ne_lo], "lat": lat[ne_la],
                    "lon05": np.arange(-179.75, 180, 0.5), "lat05": np.arange(-89.75, 90, 0.5)})
        out.attrs = {"fonte": "GPM IMERG V06 Final Run, precipitationCal, via Microsoft Planetary Computer gpm-imerg-hhr",
                     "tempo": "UTC"}
        enc = {v: {"zlib": True, "complevel": 4} for v in out.data_vars}
        out.to_netcdf(dest, encoding=enc)
        print(dia.date(), f"{time.time()-t0:.0f}s", "NE max", float(np.nanmax(ne)), flush=True)


def modo_global():
    """Pontos regulares no globo (terra e oceano) para 3 dias de marco/2019 via POWER IMERG_PRECTOT."""
    s = sessao_http()
    pts = [(lon, lat) for lat in range(-85, 90, 10) for lon in range(-175, 180, 30)]
    linhas = []

    def um(p):
        lon, lat = p
        r = s.get(URL_PT, params={"parameters": "IMERG_PRECTOT", "community": "AG", "longitude": lon, "latitude": lat,
                                  "start": "20190301", "end": "20190310", "format": "JSON", "time-standard": "UTC"},
                  timeout=120)
        d = r.json()
        v = list(d["properties"]["parameter"]["IMERG_PRECTOT"].values())
        return lon, lat, v

    with ThreadPoolExecutor(6) as ex:
        for lon, lat, v in ex.map(um, pts):
            arr = np.array(v, dtype=float)
            linhas.append({"lon": lon, "lat": lat, "n_dias": len(arr), "n_validos": int((arr > -998).sum()),
                           "media_mm": float(arr[arr > -998].mean()) if (arr > -998).any() else np.nan})
    df = pd.DataFrame(linhas)
    df.to_csv(OUT / "validacao_global_power_imerg.csv", index=False)
    print(df.groupby("lat")["n_validos"].mean())


if __name__ == "__main__":
    modo = sys.argv[1]
    if modo == "power":
        modo_power(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 4)
    elif modo == "consolidar":
        consolidar(sys.argv[2])
    elif modo == "pc":
        modo_pc(sys.argv[2], sys.argv[3])
    elif modo == "global":
        modo_global()
