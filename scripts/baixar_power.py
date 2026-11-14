"""NASA POWER: diario 1981->hoje na grade do Ceara, mensal no Nordeste, amostra global para validar cobertura.

Limites descobertos (sonda_power.py, 13/11/2026): endpoint regional aceita 1 parametro por pedido,
ate 366 dias por pedido e no maximo 10 graus de lado. Ponto aceita varios parametros.
Saida: dados/power/power_ce_diario.nc, power_ne_mensal.nc, power_global_amostra.parquet
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import xarray as xr

sys.stdout.reconfigure(encoding="utf-8")
OUT = pasta("power")
CACHE = OUT / "cache_npz"
CACHE.mkdir(exist_ok=True)
FILL = -999.0
PARAMS = ["T2M", "T2M_MAX", "T2M_MIN", "T2MDEW", "RH2M", "PRECTOTCORR", "WS2M", "ALLSKY_SFC_SW_DWN",
          "EVPTRNS", "GWETTOP", "GWETROOT", "GWETPROF", "IMERG_PRECTOT"]
HOJE = date.today()
S = sessao_http(retries=6)


def regional(param, bbox, start, end, temporal="daily", extra=None):
    q = {"parameters": param, "community": "AG", "longitude-min": bbox[0], "latitude-min": bbox[1],
         "longitude-max": bbox[2], "latitude-max": bbox[3], "start": start, "end": end, "format": "JSON"}
    if extra:
        q.update(extra)
    for tent in range(6):
        r = S.get(f"https://power.larc.nasa.gov/api/temporal/{temporal}/regional", params=q, timeout=600)
        if r.status_code == 200:
            return r.json()
        time.sleep(5 * (tent + 1))
    raise RuntimeError(f"{param} {start}-{end}: HTTP {r.status_code} {r.text[:200]}")


def feats_para_arrays(d, param):
    feats = d["features"]
    lons = np.array([f["geometry"]["coordinates"][0] for f in feats])
    lats = np.array([f["geometry"]["coordinates"][1] for f in feats])
    elev = np.array([f["geometry"]["coordinates"][2] if len(f["geometry"]["coordinates"]) > 2 else np.nan for f in feats])
    chaves = list(feats[0]["properties"]["parameter"][param].keys())
    vals = np.array([[f["properties"]["parameter"][param].get(k, FILL) for k in chaves] for f in feats], dtype="float32")
    return lons, lats, elev, chaves, vals, d.get("header", {}), d.get("parameters", {})


def tarefa_ce(param, ano):
    # IMERG_PRECTOT so vem preenchido com time-standard=UTC (em LST a API devolve -999)
    utc = param == "IMERG_PRECTOT"
    arq = CACHE / (f"ce_{param}_UTC_{ano}.npz" if utc else f"ce_{param}_{ano}.npz")
    if arq.exists():
        return arq
    if utc and ano < 2000:
        raise RuntimeError("IMERG comeca em jun/2000")
    fim = f"{ano}1231" if ano < HOJE.year else HOJE.strftime("%Y%m%d")
    if utc:
        # IMERG vem na grade nativa de 0,1 grau (2475 pontos no CE): pedidos de 1 ano sao lentissimos;
        # em blocos mensais cada pedido leva poucos segundos.
        partes = []
        for mes in range(1, 13):
            ini = pd.Timestamp(ano, mes, 1)
            fm = (ini + pd.offsets.MonthEnd(0))
            if ini.date() > HOJE:
                break
            fm = min(fm.date(), HOJE)
            d = regional(param, BBOX_CE, ini.strftime("%Y%m%d"), fm.strftime("%Y%m%d"), extra={"time-standard": "UTC"})
            partes.append(feats_para_arrays(d, param))
        lons, lats, elev, _, _, header, meta = partes[0]
        chaves = sum((p[3] for p in partes), [])
        vals = np.concatenate([p[4] for p in partes], axis=1)
    else:
        d = regional(param, BBOX_CE, f"{ano}0101", fim)
        lons, lats, elev, chaves, vals, header, meta = feats_para_arrays(d, param)
    np.savez_compressed(arq, lons=lons, lats=lats, elev=elev, chaves=np.array(chaves), vals=vals,
                        meta=json.dumps({"header": header, "parameters": meta}))
    return arq


def carregar_param(arqs, param):
    """Junta os npz de um parametro (cada parametro pode ter grade propria: MERRA-2, CERES 1 grau, IMERG)."""
    series, meta, elev = [], {}, None
    for arq in sorted(arqs):
        z = np.load(arq, allow_pickle=False)
        lons, lats, vals, chaves = z["lons"], z["lats"], z["vals"], z["chaves"]
        lon_u, lat_u = np.unique(lons), np.unique(lats)
        tempo = pd.to_datetime([str(c) for c in chaves], format="%Y%m%d")
        cubo = np.full((len(tempo), len(lat_u), len(lon_u)), np.nan, dtype="float32")
        el = np.full((len(lat_u), len(lon_u)), np.nan, dtype="float32")
        for i, (lo, la) in enumerate(zip(lons, lats)):
            a, b = np.searchsorted(lat_u, la), np.searchsorted(lon_u, lo)
            cubo[:, a, b] = vals[i]
            el[a, b] = z["elev"][i]
        series.append(xr.DataArray(cubo, coords={"time": tempo, "lat": lat_u, "lon": lon_u}, dims=("time", "lat", "lon")))
        elev = el
        meta = json.loads(str(z["meta"])).get("parameters", {}).get(param, meta)
    da = xr.concat(series, "time", join="outer")
    da = da.where(da != FILL)
    da.attrs.update({k: str(v) for k, v in meta.items()})
    return da, elev


def para_grade(da, ref):
    """Leva da para a grade de ref: media por celula se mais fina, vizinho mais proximo se mais grossa."""
    if da.sizes["lat"] == ref.sizes["lat"] and da.sizes["lon"] == ref.sizes["lon"] \
            and np.allclose(da.lat, ref.lat) and np.allclose(da.lon, ref.lon):
        return da
    dlat_r, dlon_r = float(np.diff(ref.lat).min()), float(np.diff(ref.lon).min())
    dlon_s = float(np.diff(da.lon).min()) if da.sizes["lon"] > 1 else 99
    if dlon_s < 0.75 * dlon_r:
        out = np.full((da.sizes["time"], ref.sizes["lat"], ref.sizes["lon"]), np.nan, dtype="float32")
        v = da.values
        for i, la in enumerate(ref.lat.values):
            mi = np.abs(da.lat.values - la) <= dlat_r / 2 + 1e-6
            for j, lo in enumerate(ref.lon.values):
                mj = np.abs(da.lon.values - lo) <= dlon_r / 2 + 1e-6
                if mi.any() and mj.any():
                    out[:, i, j] = np.nanmean(v[:, mi][:, :, mj].reshape(v.shape[0], -1), axis=1)
        res = xr.DataArray(out, coords={"time": da.time, "lat": ref.lat, "lon": ref.lon}, dims=da.dims, attrs=da.attrs)
    else:
        res = da.sel(lat=ref.lat, lon=ref.lon, method="nearest").assign_coords(lat=ref.lat, lon=ref.lon)
    res.attrs["regrade"] = f"de {da.sizes['lat']}x{da.sizes['lon']} para {ref.sizes['lat']}x{ref.sizes['lon']}"
    return res


def montar_grade(arqs_por_param):
    """Dataset (time, lat, lon) na grade MERRA-2 (a do T2M). Parametros com grade nativa diferente
    tambem sao salvos na grade nativa em power_ce_<param>_nativo.nc."""
    cru = {p: carregar_param(a, p) for p, a in arqs_por_param.items()}
    ref, elev = cru["T2M"]
    dvars = {}
    for p, (da, _) in cru.items():
        g = para_grade(da, ref)
        if "regrade" in g.attrs:
            da.to_dataset(name=p).to_netcdf(OUT / f"power_ce_{p}_nativo.nc", encoding={p: {"zlib": True}})
            print(p, "grade nativa", dict(da.sizes), "->", g.attrs["regrade"], flush=True)
        dvars[p] = g.reindex(time=ref.time)
    ds = xr.Dataset(dvars)
    ds["elevacao_m"] = (("lat", "lon"), elev)
    return ds


def baixar_ce_diario():
    anos = list(range(1981, HOJE.year + 1))
    tarefas = [(p, a) for p in PARAMS for a in anos]
    feitos = {p: [] for p in PARAMS}
    t0 = time.time()
    with ThreadPoolExecutor(4) as ex:
        futs = {ex.submit(tarefa_ce, p, a): (p, a) for p, a in tarefas}
        for i, f in enumerate(as_completed(futs), 1):
            p, a = futs[f]
            try:
                feitos[p].append(f.result())
            except Exception as e:
                print("FALHA", p, a, e, flush=True)
            if i % 40 == 0:
                print(f"CE diario {i}/{len(tarefas)} {time.time()-t0:.0f}s", flush=True)
    ds = montar_grade({p: v for p, v in feitos.items() if v})
    ds.attrs.update(fonte="NASA POWER v2 (power.larc.nasa.gov) API regional diaria, comunidade AG",
                    recorte=str(BBOX_CE), baixado_em=str(HOJE))
    enc = {v: {"zlib": True, "complevel": 4} for v in ds.data_vars}
    ds.to_netcdf(OUT / "power_ce_diario.nc", encoding=enc)
    print("salvo power_ce_diario.nc", dict(ds.sizes), flush=True)
    return ds


def baixar_ne_mensal():
    # NE tem ~14 x 17 graus -> blocos de no maximo 10 graus
    lon0, lat0, lon1, lat1 = BBOX_NE
    blocos = []
    for la in np.arange(lat0, lat1, 9.0):
        for lo in np.arange(lon0, lon1, 9.0):
            blocos.append((lo, la, min(lo + 9.0, lon1), min(la + 9.0, lat1)))
    dfs = []
    for param in [p for p in PARAMS if p != "IMERG_PRECTOT"]:
        for b in blocos:
            arq = CACHE / f"ne_m_{param}_{b[0]:.1f}_{b[1]:.1f}.parquet"
            if not arq.exists():
                d = regional(param, b, "1981", str(HOJE.year - 1), temporal="monthly")
                linhas = []
                for f in d["features"]:
                    lo, la = f["geometry"]["coordinates"][:2]
                    for k, v in f["properties"]["parameter"][param].items():
                        if k[-2:] == "13":
                            continue  # media anual
                        linhas.append((lo, la, k, v))
                pd.DataFrame(linhas, columns=["lon", "lat", "yyyymm", "valor"]).assign(param=param).to_parquet(arq)
            dfs.append(pd.read_parquet(arq))
        print("NE mensal", param, "ok", flush=True)
    df = pd.concat(dfs).drop_duplicates(["lon", "lat", "yyyymm", "param"])
    df["valor"] = df["valor"].where(df["valor"] != FILL)
    df["time"] = pd.to_datetime(df["yyyymm"].astype(str), format="%Y%m")
    ds = df.set_index(["param", "time", "lat", "lon"])["valor"].to_xarray().to_dataset("param")
    ds.attrs.update(fonte="NASA POWER API regional mensal, comunidade AG", recorte=str(BBOX_NE))
    ds.to_netcdf(OUT / "power_ne_mensal.nc", encoding={v: {"zlib": True} for v in ds.data_vars})
    print("salvo power_ne_mensal.nc", dict(ds.sizes), flush=True)


PONTOS_GLOBAIS = {
    # nome: (lat, lon, faixa/rotulo)
    "Svalbard": (78.2, 15.6), "Utqiagvik_Alasca": (71.3, -156.8), "Groenlandia_Summit": (72.6, -38.5),
    "Groenlandia_Nuuk": (64.2, -51.7), "Norilsk": (69.3, 88.2), "Yakutsk": (62.0, 129.7),
    "Fairbanks": (64.8, -147.7), "Islandia": (64.1, -21.9), "Finlandia": (64.0, 26.0), "Escandinavia": (63.0, 15.0),
    "Siberia_central": (60.0, 100.0), "Kamchatka": (56.0, 160.0), "Escocia": (57.0, -4.0), "Moscou": (55.7, 37.6),
    "Urais": (56.8, 60.6), "Pradarias_Canada": (52.0, -106.0), "Polonia": (52.0, 19.0), "Cazaquistao": (50.0, 70.0),
    "Ucrania": (49.0, 32.0), "Mongolia": (47.9, 106.9), "Quebec": (47.0, -71.0), "Franca": (47.0, 2.0),
    "Gobi": (43.0, 105.0), "Iowa": (42.0, -93.5), "Espanha": (40.0, -4.0), "Turquia": (39.0, 35.0),
    "Kansas": (38.0, -99.0), "Acores": (38.7, -27.2), "Vale_Central_CA": (36.7, -119.8), "Japao": (36.0, 138.0),
    "Planicie_Norte_China": (36.0, 116.0), "Marrocos": (33.0, -6.0), "Ira": (32.0, 53.0), "Tibete": (31.0, 91.0),
    "Punjab": (30.9, 75.8), "Delta_Nilo": (30.8, 31.0), "Florida": (27.8, -81.7), "Thar": (27.0, 71.0),
    "Saara": (23.0, 10.0), "Bangladesh": (23.7, 90.4), "Arabia_Saudita": (24.7, 46.7), "Cuba": (22.0, -79.5),
    "Myanmar": (21.0, 96.0), "Vietna_norte": (21.0, 105.8), "Bajio_Mexico": (20.5, -101.0), "Havai": (19.7, -155.5),
    "Deccan": (18.0, 77.0), "Tailandia": (15.8, 101.0), "Sudao": (15.5, 32.5), "Iemen": (15.4, 44.2),
    "Cabo_Verde": (15.0, -23.6), "Filipinas": (15.0, 121.0), "Guatemala": (14.6, -90.5), "Sahel_Niger": (13.5, 2.1),
    "Chade": (12.0, 19.0), "Mekong": (10.0, 105.8), "Nigeria": (9.0, 8.0), "Etiopia": (9.0, 38.7),
    "Venezuela": (8.0, -66.0), "Sri_Lanka": (7.8, 80.7), "Colombia": (4.6, -74.0), "Somalia": (2.0, 45.3),
    "Uganda": (1.5, 32.5), "Borneu": (1.0, 114.0), "Congo": (0.0, 23.0), "Sumatra": (0.0, 102.0),
    "Galapagos": (-0.7, -90.3), "Quenia": (-0.5, 36.9), "Equador_Andes": (-1.5, -78.5), "Amazonia": (-3.1, -60.0),
    "Fortaleza_CE": (-3.7, -38.5), "Papua_NG": (-6.0, 145.0), "Tanzania": (-6.2, 35.7), "Java": (-7.5, 110.5),
    "Petrolina_PE": (-9.4, -40.5), "Angola": (-12.5, 18.5), "Mato_Grosso": (-13.0, -56.0), "Andes_Peru": (-13.5, -72.0),
    "Zambia": (-15.4, 28.3), "Fiji": (-17.7, 178.0), "Bolivia": (-17.8, -63.0), "Mocambique": (-18.0, 35.0),
    "Madagascar": (-19.0, 47.0), "Reuniao": (-21.1, 55.5), "Namibia": (-22.5, 17.0), "Kalahari": (-23.0, 22.0),
    "Paraguai": (-23.4, -58.4), "Queensland": (-23.5, 148.0), "Atacama": (-24.0, -69.0), "Outback": (-25.0, 135.0),
    "Africa_do_Sul": (-26.0, 28.0), "Ilha_de_Pascoa": (-27.1, -109.4), "Australia_Ocidental": (-31.9, 116.0),
    "Uruguai": (-32.5, -56.0), "Chile_central": (-34.0, -71.0), "Murray_Darling": (-34.0, 145.0), "Pampa": (-35.0, -61.0),
    "Tasmania": (-42.0, 146.5), "Nova_Zelandia": (-43.5, 172.5), "Patagonia": (-45.0, -70.0), "Kerguelen": (-49.3, 70.2),
    "Peninsula_Antartica": (-64.8, -64.0), "McMurdo": (-77.8, 166.7), "Vostok": (-78.5, 106.8), "Polo_Sul": (-89.9, 0.0),
    "Oceano_Pacifico": (0.0, -140.0), "Oceano_Atlantico_Sul": (-30.0, -15.0),
}
PARAMS_GLOBAL = ["T2M", "T2M_MAX", "T2M_MIN", "RH2M", "PRECTOTCORR", "WS2M", "ALLSKY_SFC_SW_DWN",
                 "EVPTRNS", "GWETTOP", "GWETROOT", "IMERG_PRECTOT"]


def baixar_global():
    arq = OUT / "power_global_amostra.parquet"
    if arq.exists():
        return

    def um(nome, la, lo):
        q = dict(parameters=",".join(PARAMS_GLOBAL), community="AG", longitude=lo, latitude=la,
                 start="20200101", end="20201231", format="JSON")
        r = S.get("https://power.larc.nasa.gov/api/temporal/daily/point", params=q, timeout=300)
        r.raise_for_status()
        d = r.json()
        # IMERG_PRECTOT so vem preenchido em UTC
        q2 = dict(q, parameters="IMERG_PRECTOT", **{"time-standard": "UTC"})
        r2 = S.get("https://power.larc.nasa.gov/api/temporal/daily/point", params=q2, timeout=300)
        if r2.ok:
            d["properties"]["parameter"]["IMERG_PRECTOT"] = r2.json()["properties"]["parameter"]["IMERG_PRECTOT"]
        el = d["geometry"]["coordinates"][2] if len(d["geometry"]["coordinates"]) > 2 else np.nan
        linhas = []
        for p, serie in d["properties"]["parameter"].items():
            for k, v in serie.items():
                linhas.append((nome, la, lo, el, p, k, v))
        return linhas

    linhas = []
    with ThreadPoolExecutor(4) as ex:
        futs = [ex.submit(um, n, la, lo) for n, (la, lo) in PONTOS_GLOBAIS.items()]
        for f in as_completed(futs):
            try:
                linhas += f.result()
            except Exception as e:
                print("global falha", e, flush=True)
    df = pd.DataFrame(linhas, columns=["ponto", "lat", "lon", "elev", "param", "data", "valor"])
    df["data"] = pd.to_datetime(df["data"], format="%Y%m%d")
    df.to_parquet(arq)
    print("salvo amostra global", df["ponto"].nunique(), "pontos", flush=True)


def testar_imerg_utc():
    """IMERG_PRECTOT veio -999 no ponto (LST). Testa regional com time-standard UTC."""
    res = {}
    for ano in (2001, 2015, 2020):
        try:
            d = regional("IMERG_PRECTOT", BBOX_CE, f"{ano}0301", f"{ano}0310", extra={"time-standard": "UTC"})
            v = np.array([list(f["properties"]["parameter"]["IMERG_PRECTOT"].values()) for f in d["features"]])
            res[ano] = float((v != FILL).mean())
        except Exception as e:
            res[ano] = str(e)[:150]
    print("IMERG_PRECTOT UTC fracao valida:", res, flush=True)
    return res


if __name__ == "__main__":
    t0 = time.time()
    imerg = testar_imerg_utc()
    baixar_global()
    ds = baixar_ce_diario()
    baixar_ne_mensal()
    arquivos = {f.name: f.stat().st_size for f in OUT.glob("*.*") if f.is_file()}
    registrar_manifesto("power", {
        "fonte": "NASA POWER (Prediction Of Worldwide Energy Resources), NASA LaRC",
        "url": "https://power.larc.nasa.gov/api/temporal/{daily,monthly}/{regional,point}",
        "comunidade": "AG",
        "limites_api": "regional: 1 parametro/pedido, <=366 dias, <=10 graus; ponto: varios parametros",
        "recortes": {"ce_diario": str(BBOX_CE), "ne_mensal": str(BBOX_NE), "global": f"{len(PONTOS_GLOBAIS)} pontos, 2020 diario"},
        "periodo_ce_diario": f"1981-01-01 a {str(ds.time.values[-1])[:10]}",
        "parametros": PARAMS, "imerg_prectot_utc_teste": imerg,
        "arquivos": arquivos, "minutos": round((time.time() - t0) / 60, 1),
    })
    print("FIM", round((time.time() - t0) / 60, 1), "min", flush=True)
