"""Pos-processamento do NASA POWER: ET0 FAO-56, indicadores agronomicos e derivados mensais.

Entradas: dados/power/power_ce_diario.nc, power_ne_mensal.nc
Saidas:
  dados/power/power_ce_diario_et0.nc          ET0 e P-ET0 diarios na grade do Ceara
  dados/power/power_ce_indicadores_anuais.parquet  por pixel e media do Ceara
  derivados/power_ce_mensal.parquet, power_ne_mensal.parquet, power_aoi_mensal.parquet
"""
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import Point

sys.stdout.reconfigure(encoding="utf-8")
P = pasta("power")
FONTE = "NASA POWER (MERRA-2/CERES), API AG"


def es(t):
    return 0.6108 * np.exp(17.27 * t / (t + 237.3))


def et0_fao56(tmax, tmin, tdew, u2, rs, lat_deg, elev, doy):
    """ET0 Penman-Monteith FAO-56 diaria (mm/dia). rs em MJ m-2 dia-1, u2 em m/s, temperaturas em C."""
    tmean = (tmax + tmin) / 2
    e_s = (es(tmax) + es(tmin)) / 2
    e_a = es(tdew)
    delta = 4098 * es(tmean) / (tmean + 237.3) ** 2
    pres = 101.3 * ((293 - 0.0065 * elev) / 293) ** 5.26
    gamma = 0.000665 * pres
    phi = np.deg2rad(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(dec), -1, 1))
    ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(phi) * np.sin(dec) + np.cos(phi) * np.cos(dec) * np.sin(ws))
    rso = (0.75 + 2e-5 * elev) * ra
    rns = 0.77 * rs
    rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * np.sqrt(np.maximum(e_a, 0))) \
        * (1.35 * np.clip(rs / rso, 0.25, 1.0) - 0.35)
    rn = rns - rnl
    num = 0.408 * delta * rn + gamma * 900 / (tmean + 273) * u2 * (e_s - e_a)
    den = delta + gamma * (1 + 0.34 * u2)
    return np.maximum(num / den, 0)


def mascara(ds, gdf):
    lo, la = np.meshgrid(ds.lon.values, ds.lat.values)
    pts = gpd.GeoSeries([Point(x, y) for x, y in zip(lo.ravel(), la.ravel())], crs=4326)
    dentro = pts.within(gdf.union_all()).values.reshape(lo.shape)
    return xr.DataArray(dentro, coords={"lat": ds.lat, "lon": ds.lon}, dims=("lat", "lon"))


def maior_sequencia(bool_arr):
    """Maior sequencia de True ao longo do eixo 0 (dias) para cada pixel."""
    best = np.zeros(bool_arr.shape[1:], dtype=int)
    cur = np.zeros_like(best)
    for d in bool_arr:
        cur = np.where(d, cur + 1, 0)
        best = np.maximum(best, cur)
    return best


def n_sequencias(bool_arr, minimo):
    """Numero de sequencias de True com tamanho >= minimo."""
    cont = np.zeros(bool_arr.shape[1:], dtype=int)
    cur = np.zeros_like(cont)
    for d in np.concatenate([bool_arr, np.zeros((1,) + bool_arr.shape[1:], bool)]):
        fim = (~d) & (cur >= minimo)
        cont += fim
        cur = np.where(d, cur + 1, 0)
    return cont


def inicio_fim_chuvas(pr_ano, datas):
    """Inicio: 1o dia (a partir de 1/jan) com chuva de 3 dias >= 20 mm sem veranico > 10 dias nos 30 seguintes.
    Fim: ultimo dia ate 31/jul com chuva acumulada de 10 dias >= 10 mm. Retorna dia do ano (NaN se nao houver)."""
    n = pr_ano.shape[0]
    doy = np.array([d.day_of_year for d in datas])
    vazio = np.isnan(pr_ano).all(0)
    p = np.nan_to_num(pr_ano)
    seco = p < 1.0
    # comprimento da sequencia seca que termina em cada dia
    run = np.zeros(p.shape, dtype=np.int16)
    for t in range(n):
        run[t] = (run[t - 1] + 1) * seco[t] if t else seco[t]
    sw = np.lib.stride_tricks.sliding_window_view
    acum3 = sw(p, 3, axis=0).sum(-1)                  # [d] = soma de d..d+2
    maxrun30 = sw(run, 30, axis=0).max(-1)            # [k] = maior seq. seca terminando em k..k+29
    nd = min(n - 33, 200)
    cond = (acum3[:nd] >= 20) & (maxrun30[3:3 + nd] <= 10)
    tem = cond.any(0)
    ini = np.where(tem & ~vazio, doy[np.argmax(cond, 0)], np.nan)
    lim = int(np.searchsorted(doy, 212))  # 31/jul
    acum10 = sw(p, 10, axis=0).sum(-1)[:max(lim - 9, 1)] >= 10
    tem_f = acum10.any(0)
    ult = acum10.shape[0] - 1 - np.argmax(acum10[::-1], 0)
    fim = np.where(tem_f & ~vazio, doy[np.minimum(ult + 9, n - 1)], np.nan)
    return ini, fim


def main():
    ds = xr.open_dataset(P / "power_ce_diario.nc").load()
    print("variaveis:", list(ds.data_vars), dict(ds.sizes))
    for v in ("ALLSKY_SFC_SW_DWN", "PRECTOTCORR", "EVPTRNS"):
        print(v, {k: ds[v].attrs.get(k) for k in ("units", "longname")})
    if "MJ" in str(ds["EVPTRNS"].attrs.get("units", "")):
        # EVPTRNS do POWER e fluxo de energia (MJ m-2 dia-1); em agua: / 2,45 MJ/kg
        at = dict(ds["EVPTRNS"].attrs)
        ds["EVPTRNS"] = (ds["EVPTRNS"] / 2.45).assign_attrs(at, units="mm/day", conversao="MJ/m2/dia / 2,45")
    lat2 = xr.broadcast(ds.lat, ds.lon)[0]
    doy = ds.time.dt.dayofyear
    rs = ds["ALLSKY_SFC_SW_DWN"]
    if "kW" in str(rs.attrs.get("units", "")):
        rs = rs * 3.6  # kWh/m2/dia -> MJ/m2/dia
    et0 = et0_fao56(ds.T2M_MAX, ds.T2M_MIN, ds.T2MDEW, ds.WS2M, rs, lat2, ds.elevacao_m, doy)
    et0 = et0.where(ds.T2M_MAX.notnull() & rs.notnull()).transpose("time", "lat", "lon")
    ds["ET0"] = et0.assign_attrs(units="mm/day", longname="ET0 FAO-56 Penman-Monteith (calculada)")
    ds["P_menos_ET0"] = (ds.PRECTOTCORR - ds.ET0).assign_attrs(units="mm/day")
    ds[["ET0", "P_menos_ET0"]].to_netcdf(P / "power_ce_diario_et0.nc", encoding={"ET0": {"zlib": True}, "P_menos_ET0": {"zlib": True}})

    m_ce = mascara(ds, ceara_gdf())
    print("pontos da grade dentro do Ceara:", int(m_ce.sum()), "de", m_ce.size)
    w = np.cos(np.deg2rad(ds.lat)) * m_ce

    # derivados mensais (media do Ceara)
    unid = {v: ds[v].attrs.get("units", "") for v in ds.data_vars if "time" in ds[v].dims}
    soma = {"PRECTOTCORR", "IMERG_PRECTOT", "EVPTRNS", "ET0", "P_menos_ET0"}
    linhas = []
    for v in unid:
        da = ds[v].where(m_ce)
        mens = (da.resample(time="MS").sum(min_count=20) if v in soma else da.resample(time="MS").mean())
        serie = mens.weighted(w).mean(("lat", "lon"))
        ok = da.resample(time="MS").count().sum(("lat", "lon")) > 0
        serie = serie.where(ok)
        df = serie.to_dataframe(name="valor").reset_index().rename(columns={"time": "data"})
        df["variavel"], df["unidade"], df["fonte"] = v, (unid[v] + "/mes" if v in soma else unid[v]), FONTE
        linhas.append(df[["data", "variavel", "valor", "unidade", "fonte"]])
    pd.concat(linhas, ignore_index=True).to_parquet(DERIV / "power_ce_mensal.parquet")

    # AOIs (ponto de grade mais proximo)
    linhas = []
    for nome, (lo, la, _) in AOIS.items():
        sub = ds.sel(lon=lo, lat=la, method="nearest")
        for v in unid:
            mens = sub[v].resample(time="MS").sum(min_count=20) if v in soma else sub[v].resample(time="MS").mean()
            df = mens.to_dataframe(name="valor").reset_index().rename(columns={"time": "data"})
            df["variavel"], df["unidade"], df["fonte"], df["aoi"] = v, unid[v], FONTE, nome
            linhas.append(df[["data", "aoi", "variavel", "valor", "unidade", "fonte"]])
    pd.concat(linhas, ignore_index=True).to_parquet(DERIV / "power_aoi_mensal.parquet")

    # NE mensal (media do Nordeste)
    ne = xr.open_dataset(P / "power_ne_mensal.nc").load()
    m_ne = mascara(ne, nordeste_gdf().cx[-49:-34.5, :])
    wn = np.cos(np.deg2rad(ne.lat)) * m_ne
    linhas = []
    for v in ne.data_vars:
        serie = ne[v].where(m_ne).weighted(wn).mean(("lat", "lon"))
        df = serie.to_dataframe(name="valor").reset_index().rename(columns={"time": "data"})
        df["variavel"], df["unidade"], df["fonte"] = v, unid.get(v, ""), FONTE + " (mensal regional)"
        linhas.append(df[["data", "variavel", "valor", "unidade", "fonte"]])
    pd.concat(linhas, ignore_index=True).to_parquet(DERIV / "power_ne_mensal.parquet")

    # indicadores anuais por pixel
    reg = []
    anos = sorted(set(ds.time.dt.year.values))
    for ano in anos:
        sub = ds.sel(time=str(ano))
        if sub.sizes["time"] < 360:
            continue
        pr = sub.PRECTOTCORR.values
        q = sub.sel(time=slice(f"{ano}-02-01", f"{ano}-05-31"))
        seco_q = q.PRECTOTCORR.values < 1.0
        ini, fim = inicio_fim_chuvas(pr, pd.DatetimeIndex(sub.time.values))
        ind = {
            "chuva_anual_mm": np.nansum(pr, 0),
            "chuva_fev_mai_mm": np.nansum(q.PRECTOTCORR.values, 0),
            "ET0_anual_mm": np.where(np.isnan(sub.ET0.values).mean(0) > 0.1, np.nan, np.nansum(sub.ET0.values, 0)),
            "dias_tmax_gt35": (sub.T2M_MAX.values > 35).sum(0),
            "dias_tmax_gt38": (sub.T2M_MAX.values > 38).sum(0),
            "dias_chuva_gt50": (pr > 50).sum(0),
            "dias_chuva_gt1": (pr >= 1).sum(0),
            "maior_veranico_fev_mai_d": maior_sequencia(seco_q),
            "n_veranicos_10d_fev_mai": n_sequencias(seco_q, 10),
            "inicio_chuvas_doy": ini,
            "fim_chuvas_doy": fim,
            "GWETROOT_medio": np.nanmean(sub.GWETROOT.values, 0),
        }
        ind["indice_aridez_P_ET0"] = ind["chuva_anual_mm"] / ind["ET0_anual_mm"]
        for i, la in enumerate(ds.lat.values):
            for j, lo in enumerate(ds.lon.values):
                reg.append({"ano": ano, "lat": float(la), "lon": float(lo), "no_ceara": bool(m_ce.values[i, j]),
                            **{k: float(v[i, j]) for k, v in ind.items()}})
    ind = pd.DataFrame(reg)
    ind.to_parquet(P / "power_ce_indicadores_anuais.parquet")
    print("indicadores:", ind.shape, "anos", ind.ano.min(), "-", ind.ano.max())
    registrar_manifesto("power", {"derivados": {
        "power_ce_diario_et0.nc": "ET0 FAO-56 PM e P-ET0 diarios",
        "power_ce_indicadores_anuais.parquet": "indicadores agronomicos anuais por pixel",
        "derivados/power_ce_mensal.parquet": "media do Ceara (mascara IBGE nos centros da grade)",
        "derivados/power_ne_mensal.parquet": "media do Nordeste (API mensal)",
        "derivados/power_aoi_mensal.parquet": "ponto de grade mais proximo de cada AOI"},
        "pontos_grade_no_ceara": int(m_ce.sum())})
    print("FIM preparar_power", flush=True)


if __name__ == "__main__":
    main()
