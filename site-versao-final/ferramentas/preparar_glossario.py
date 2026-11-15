"""Números do próprio município para os exemplos do glossário "o que é?" (web/js/extras/glossario.js).

Lê (E:/campeonato-nasa/dados/):
  analogos_aprofundado/ne_mun_assinaturas.csv   ponto interno do município e ET0 anual (NASA POWER, FAO-56; a mesma do motor)
  analogos_aprofundado/regime_chuva_ne_mun.csv  mês de início da estação (os 4 meses mais chuvosos, IMERG)
  analogos_aprofundado/onset_ne_mun.csv         dia em que a chuva firmou, por ano (IMERG; definição da proposta v3)
  imerg/imerg_ne_diario_AAAA.nc                 chuva diária GPM IMERG 0,1°, 1998 a 30/09/2025 (só o Final; depois é preliminar)
  era5/era5_ne_diario_AAAA.nc                   mínima diária ERA5 0,25°, 1979–2020
  modis/mod13a1_ndvi_nordeste_005deg.nc         NDVI MODIS MOD13A1 (500 m, 16 dias) em grade de 0,05°, 2001–2025
Grava: web/dados/glossario_mun.json = {fonte, campos, m: {cod: [valores na ordem de campos]}}

Veranico: dentro da estação (do dia em que a chuva firmou ao fim dos 4 meses mais chuvosos), a maior sequência de dias com
menos de 2 mm que termina com a chuva voltando (até 30 dias depois do fim da estação; senão é o fim das águas, não veranico).
Ano com veranico = sequência de 10 dias ou mais. Célula do IMERG no ponto interno do município.
Rodar: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 ferramentas/preparar_glossario.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

D = Path("E:/campeonato-nasa/dados")
SAIDA = Path(__file__).resolve().parents[1] / "web" / "dados" / "glossario_mun.json"
FIM_FINAL = np.datetime64("2025-09-30")
SECO_MM, VERANICO_DIAS, VOLTA_DIAS = 2.0, 10, 30


def mais_proximo(eixo, valores):
    eixo = np.asarray(eixo)
    return np.abs(eixo[None, :] - np.asarray(valores)[:, None]).argmin(axis=1)


def veranicos(A):
    """Por município: anos com veranico de 10+ dias, anos contados, maior sequência e o ano dela."""
    reg = pd.read_csv(D / "analogos_aprofundado/regime_chuva_ne_mun.csv").set_index("cod").mes_inicio_estacao
    ons = pd.read_csv(D / "analogos_aprofundado/onset_ne_mun.csv", parse_dates=["inicio_chuva"])
    blocos, datas = [], []
    for ano in range(1998, 2026):
        ds = xr.open_dataset(D / f"imerg/imerg_ne_diario_{ano}.nc")
        iy, ix = mais_proximo(ds.lat.values, A.lat.values), mais_proximo(ds.lon.values, A.lon.values)
        p = ds.precip.values[:, iy, ix]  # (dias, municípios)
        blocos.append(p)
        datas.append(ds.time.values.astype("datetime64[D]"))
        ds.close()
    P, T = np.concatenate(blocos), np.concatenate(datas)
    ok = T <= FIM_FINAL
    P, T = P[ok], T[ok]
    pos = {c: j for j, c in enumerate(A.cod)}
    out = {}
    for cod, g in ons.groupby("cod"):
        if cod not in pos:
            continue
        j, m0 = pos[cod], int(reg.get(cod, 1))
        k = n = 0
        maior, ano_maior = 0, None
        for r in g.itertuples():
            a0 = r.ano - 1 if m0 >= 9 else r.ano
            ini = np.datetime64(f"{a0}-{m0:02d}-01")
            fim = (pd.Timestamp(ini) + pd.DateOffset(months=4) - pd.Timedelta(days=1)).to_datetime64().astype("datetime64[D]")
            if fim > FIM_FINAL or ini < T[0] or pd.isna(r.inicio_chuva):
                continue
            on = np.datetime64(r.inicio_chuva.date())
            if on > fim:
                continue
            w0 = max(on, ini)
            sel = (T >= w0) & (T <= fim + np.timedelta64(VOLTA_DIAS, "D"))
            seco = P[sel, j] < SECO_MM
            if np.isnan(P[sel, j]).mean() > 0.1:
                continue
            dias = T[sel]
            seq, inicio_seq, melhor = 0, None, 0
            for d, s in zip(dias, seco):
                if s:
                    if seq == 0:
                        inicio_seq = d
                    seq += 1
                else:  # a chuva voltou: conta se a sequência começou dentro da estação
                    if seq and inicio_seq <= fim:
                        melhor = max(melhor, seq)
                    seq = 0
            n += 1
            k += melhor >= VERANICO_DIAS
            if melhor > maior:
                maior, ano_maior = melhor, int(r.ano)
        if n >= 10:
            out[cod] = (k, n, maior, ano_maior)
    return out


def noite_mais_fria(A):
    mn, ano_mn, lat, lon = None, None, None, None
    for ano in range(1979, 2021):
        ds = xr.open_dataset(D / f"era5/era5_ne_diario_{ano}.nc")
        t = ds.tmin.min("data").values
        if mn is None:
            mn, ano_mn, lat, lon = t, np.full(t.shape, ano), ds.lat.values, ds.lon.values
        else:
            novo = t < mn
            mn, ano_mn = np.where(novo, t, mn), np.where(novo, ano, ano_mn)
        ds.close()
    iy, ix = mais_proximo(lat, A.lat.values), mais_proximo(lon, A.lon.values)
    return mn[iy, ix], ano_mn[iy, ix]


def verde(A):
    ds = xr.open_dataset(D / "modis/mod13a1_ndvi_nordeste_005deg.nc")
    t = pd.DatetimeIndex(ds.time.values)
    ok = ds.feito.values & (t.year >= 2001) & (t.year <= 2025)
    v = ds.ndvi.values[ok]  # (compostos, lat, lon)
    meses = t[ok].month.values
    clim = np.stack([np.nanmean(v[meses == m], axis=0) for m in range(1, 13)])  # (12, lat, lon)
    iy, ix = mais_proximo(ds.lat.values, A.lat.values), mais_proximo(ds.lon.values, A.lon.values)
    ny, nx = clim.shape[1:]
    res = []
    for y, x in zip(iy, ix):  # quadrado de 3×3 células (~15 km) em volta do ponto interno
        bloco = clim[:, max(0, y - 1):min(ny, y + 2), max(0, x - 1):min(nx, x + 2)].reshape(12, -1)
        res.append(np.nanmean(bloco, axis=1))
    ds.close()
    return np.array(res)  # (municípios, 12)


def main():
    A = pd.read_csv(D / "analogos_aprofundado/ne_mun_assinaturas.csv")
    print("municípios:", len(A), flush=True)
    vr = veranicos(A)
    print("veranico:", len(vr), "municípios com 10+ anos", flush=True)
    tmin, tano = noite_mais_fria(A)
    print("noite mais fria: mín", float(np.nanmin(tmin)), "máx", float(np.nanmax(tmin)), flush=True)
    nd = verde(A)
    print("NDVI: municípios sem dado", int(np.isnan(nd).all(axis=1).sum()), flush=True)
    m = {}
    for i, r in enumerate(A.itertuples()):
        v = vr.get(r.cod)
        c = nd[i]
        tem_nd = not np.isnan(c).all()
        m[str(r.cod)] = [
            None if pd.isna(r.et0_anual_mm) else int(round(r.et0_anual_mm)),
            *(list(v) if v else [None, None, None, None]),
            None if np.isnan(tmin[i]) else round(float(tmin[i]), 1), int(tano[i]),
            *((int(round(np.nanmax(c) * 100)), int(np.nanargmax(c)) + 1, int(round(np.nanmin(c) * 100)), int(np.nanargmin(c)) + 1)
              if tem_nd else (None, None, None, None)),
        ]
    j = {
        "fonte": {
            "et0": "NASA POWER: evapotranspiração de referência anual (FAO-56 Penman-Monteith, climatologia), ponto interno do município",
            "veranico": f"GPM IMERG V07 diário (célula de 0,1° no ponto interno), estações 1998–2025 (só o Final, até 30/09/2025): do dia em "
                        f"que a chuva firmou ao fim dos 4 meses mais chuvosos, a maior sequência de dias com menos de {SECO_MM:g} mm que "
                        f"termina com a chuva voltando; veranico = {VERANICO_DIAS} dias ou mais. No CE, o satélite conta um pouco menos "
                        "veranico que os pluviômetros (fev–abr: 5 contra 6 em 10 anos; conselho/analises). No leste (estação de "
                        "mar–jun ou abr–jul) o IMERG capta só 39–72% da chuva medida perto da costa: ali o número sai alto",
            "tmin": "ERA5 (ECMWF), reanálise em células de 0,25° (~25 km): a mínima diária mais baixa de 1979–2020. Num baixio ou numa serra, "
                    "a noite pode ser mais fria que a média da célula",
            "ndvi": "NASA MODIS MOD13A1 v061 (500 m, 16 dias), média dos meses de 2001–2025 num quadrado de ~15 km em volta do ponto interno",
        },
        "campos": ["et0_mm", "ver_anos", "ver_n", "ver_maior_dias", "ver_maior_ano", "tmin_c", "tmin_ano",
                   "ndvi_max_x100", "ndvi_max_mes", "ndvi_min_x100", "ndvi_min_mes"],
        "m": m,
    }
    SAIDA.write_text(json.dumps(j, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("gravado", SAIDA, SAIDA.stat().st_size // 1024, "KB", flush=True)
    for cod in ("2311306", "2700300", "2903201"):
        print(cod, A.loc[A.cod == int(cod), "municipio"].iloc[0], m[cod])


if __name__ == "__main__":
    main()
