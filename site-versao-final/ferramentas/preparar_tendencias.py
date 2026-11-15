"""Gera site-versao-final/web/dados/tendencias/<UF>.json: "Como o seu lugar está mudando" (pontos 1 e 11 do desafio).

Para cada um dos 1.794 municípios do Nordeste, seis séries anuais curtas (eixo comum 2000–2026), já arredondadas:

  c  chuva da estação (mm)            GPM IMERG V07 por município (onset_ne_mun.csv, a mesma série do motor e do el_nino_uf);
                                      2026 é IMERG Late (preliminar). Normal = média 1998–2025.
  s  umidade do solo na raiz (%)      NASA SMAP L4 por município (ibge_ne_mun_smap_mensal), anomalia de cada mês contra a média
                                      do mesmo mês em 2015–2026, média do ano (anos com ≥ 6 meses de ≥ 20 dias).
  v  verde do satélite (%)            MODIS MOD13A1 NDVI (500 m → 0,05°), média das células com centro no município (o pequeno
                                      sem centro recebe a célula mais próxima). Pico do ano = média dos 3 maiores compostos de
                                      16 dias; anomalia contra a média 2000–2025.
  t  calor (°C)                       NASA POWER (MERRA-2), grade de ~55 km, célula válida mais próxima do município: média dos
                                      12 meses do dia mais quente de cada mês (T2M_MAX mensal = máxima do mês).
  e  evaporação pedida pelo ar (mm)   ET0 FAO-56 Penman-Monteith com as médias mensais do POWER (T2M, T2MDEW, WS2M,
                                      ALLSKY_SFC_SW_DWN), calibrada contra a ET0 diária do POWER no CE (fator e r no "meta").
  a  água guardada no chão (cm)       GRACE/GRACE-FO CSR RL06.3 mascons; resolução efetiva ~300 km, por isso a média da
                                      MESORREGIÃO do IBGE (células de 0,25° com centro nela). Anomalia contra 2004–2009.

Tendência = inclinação de Theil–Sen por década nos anos completos até 2025 (2000–2025; SMAP 2015–2025; GRACE 2002–2025),
com o teste de Mann–Kendall (sig = 1 se p < 0,10). Gravado: [normal, inclinação por década, sig].

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_tendencias.py"""
import datetime
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pymannkendall as mk
import xarray as xr
from scipy.spatial import cKDTree
from scipy.stats import theilslopes

RAIZ = Path(__file__).resolve().parents[1]
PROJ = RAIZ.parent
DADOS = Path("E:/campeonato-nasa/dados")
DER = PROJ / "dados_resumo" / "derivados"
SAIDA = RAIZ / "web" / "dados" / "tendencias"
UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
A0, A1 = 2000, 2026          # eixo comum do site
ULT = 2025                   # último ano completo (tendência e normal)
EXEMPLOS = ["2311306", "2700300", "2903201"]


def tendencia(anos, vals, casas, desde=A0):
    """[inclinação por década, sig] por Theil–Sen + Mann–Kendall (só anos de `desde` a 2025 com valor)."""
    s = pd.Series(vals, index=anos).dropna()
    s = s[(s.index >= desde) & (s.index <= ULT)]
    if len(s) < 8:
        return [None, 0]
    inc = theilslopes(s.values, s.index.values)[0] * 10
    p = mk.original_test(s.values).p
    return [round(float(inc), casas), int(p < 0.10)]


def serie(s, ini, fim, casas):
    """pd.Series indexada por ano → lista ini..fim arredondada (None onde falta)."""
    out = []
    for a in range(ini, fim + 1):
        v = s.get(a, np.nan)
        out.append(None if pd.isna(v) else (int(round(v)) if casas == 0 else round(float(v), casas)))
    return out


# ---------------------------------------------------------------- municípios
MUN = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
MUN["cod"] = MUN.codarea.astype(str)
REF = pd.read_parquet(DER / "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
MUN["meso"] = MUN.cod.map(REF.cod_meso).astype(str)
MUN = MUN.sort_values("cod").reset_index(drop=True)
PT = MUN.geometry.representative_point()
PX, PY = PT.x.values, PT.y.values
print("municípios", len(MUN))


def celulas_no_poligono(lats, lons, geo):
    """índice do polígono (linha de geo) que contém o centro de cada célula; -1 = fora."""
    LON, LAT = np.meshgrid(lons, lats)
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(LON.ravel(), LAT.ravel()), crs=4326)
    j = gpd.sjoin(pts, geo[["geometry"]].reset_index(names="im"), predicate="within", how="left")
    j = j[~j.index.duplicated()]
    return j["im"].fillna(-1).astype(int).to_numpy()


# ---------------------------------------------------------------- c: chuva da estação (IMERG)
ONS = pd.read_csv(DADOS / "analogos_aprofundado" / "onset_ne_mun.csv", dtype={"cod": str})
REG = pd.read_csv(DADOS / "analogos_aprofundado" / "regime_chuva_ne_mun.csv", dtype={"cod": str}).set_index("cod")
CH = {cod: g.set_index("ano").chuva_estacao_mm for cod, g in ONS.groupby("cod")}
print("chuva ok")

# ---------------------------------------------------------------- s: umidade do solo (SMAP)
SM = pd.read_parquet(DER / "ibge_ne_mun_smap_mensal.parquet", columns=["data", "cod_mun", "sm_rootzone", "dias"])
SM = SM[SM.dias >= 20].copy()
SM["mes"] = SM.data.dt.month
SM["ano"] = SM.data.dt.year
clim = SM.groupby(["cod_mun", "mes"]).sm_rootzone.transform("mean")
SM["anom"] = (SM.sm_rootzone / clim - 1) * 100
g = SM.groupby(["cod_mun", "ano"]).anom.agg(["mean", "count"])
g = g[g["count"] >= 6]["mean"]
SO = {cod: s.droplevel(0) for cod, s in g.groupby(level=0)}
print("smap ok", SM.data.min().date(), SM.data.max().date())

# ---------------------------------------------------------------- v: verde do satélite (MODIS NDVI)
nd = xr.open_dataset(DADOS / "modis" / "mod13a1_ndvi_nordeste_005deg.nc")
lats, lons = nd.lat.values, nd.lon.values
idx = celulas_no_poligono(lats, lons, MUN)
n = len(MUN)
cont = np.bincount(idx[idx >= 0], minlength=n)
# município sem nenhum centro de célula: a célula mais próxima do ponto interior
LON, LAT = np.meshgrid(lons, lats)
arv = cKDTree(np.c_[LON.ravel(), LAT.ravel()])
_, mais_prox = arv.query(np.c_[PX, PY])
sem = np.where(cont == 0)[0]
print("NDVI: municípios sem centro de célula", len(sem))
V = nd["ndvi"].values.reshape(nd.sizes["time"], -1)  # (tempo, células)
tempos = pd.to_datetime(nd.time.values)
ok_i = idx >= 0
NDm = np.full((len(tempos), n), np.nan, dtype=np.float32)
for k in range(len(tempos)):
    x = V[k]
    val = ok_i & np.isfinite(x)
    soma = np.bincount(idx[val], weights=x[val], minlength=n)
    c = np.bincount(idx[val], minlength=n)
    with np.errstate(invalid="ignore", divide="ignore"):
        NDm[k] = np.where(c > 0, soma / c, np.nan)
    NDm[k, sem] = x[mais_prox[sem]]
nd.close()
del V
ND = pd.DataFrame(NDm, index=tempos, columns=MUN.cod.values)
ano = ND.index.year
PICO = ND.groupby(ano).apply(lambda d: d.apply(lambda col: col.dropna().nlargest(3).mean() if col.notna().sum() >= 15 else np.nan))
print("ndvi ok", PICO.shape)

# ---------------------------------------------------------------- t, e: calor e evaporação (POWER, grade ~55 km)
pw = xr.open_dataset(DADOS / "power" / "power_ne_mensal.nc").sel(time=slice("1981-01-01", "2025-12-01"))
plat, plon = pw.lat.values, pw.lon.values
PLON, PLAT = np.meshgrid(plon, plat)


def vizinho_valido(var, pontos_x, pontos_y):
    """para cada ponto, (i_lat, i_lon) da célula mais próxima com dado em ≥ 90% dos meses de 1984–2025."""
    a = pw[var].sel(time=slice("1984-01-01", None)).values
    valido = np.isfinite(a).mean(axis=0) >= 0.9
    iy, ix = np.where(valido)
    t = cKDTree(np.c_[plon[ix], plat[iy]])
    _, j = t.query(np.c_[pontos_x, pontos_y])
    return iy[j], ix[j]


def et0_fao56(T, Td, u2, Rs, lat_graus, mes_datas, z=0.0):
    """ET0 FAO-56 (mm/dia) com médias mensais. T, Td °C; u2 m/s; Rs MJ/m²/dia; arrays (tempo,)."""
    lat = np.deg2rad(lat_graus)
    doy = np.asarray(mes_datas.dayofyear) + 14
    dr = 1 + 0.033 * np.cos(2 * np.pi / 365 * doy)
    dec = 0.409 * np.sin(2 * np.pi / 365 * doy - 1.39)
    ws = np.arccos(-np.tan(lat) * np.tan(dec))
    Ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.sin(ws))
    Rso = (0.75 + 2e-5 * z) * Ra
    es = 0.6108 * np.exp(17.27 * T / (T + 237.3))
    ea = 0.6108 * np.exp(17.27 * Td / (Td + 237.3))
    D = 4098 * es / (T + 237.3) ** 2
    gama = 0.000665 * 101.3 * ((293 - 0.0065 * z) / 293) ** 5.26
    Rnl = 4.903e-9 * (T + 273.16) ** 4 * (0.34 - 0.14 * np.sqrt(ea)) * (1.35 * np.clip(Rs / Rso, 0, 1) - 0.35)
    Rn = 0.77 * Rs - Rnl
    return (0.408 * D * Rn + gama * 900 / (T + 273) * u2 * (es - ea)) / (D + gama * (1 + 0.34 * u2))


VARS_ET = ["T2M", "T2MDEW", "WS2M", "ALLSKY_SFC_SW_DWN"]
datas = pd.to_datetime(pw.time.values)
dias_mes = datas.days_in_month.values
ARR = {v: pw[v].values for v in VARS_ET + ["T2M_MAX"]}


def et0_anual(px, py):
    """ET0 anual (mm) sem calibrar nos pontos dados: array (pontos, anos 1981..2025) com NaN onde falta mês."""
    viz = {v: vizinho_valido(v, px, py) for v in VARS_ET}
    out = []
    for k in range(len(px)):
        s = {v: ARR[v][:, viz[v][0][k], viz[v][1][k]] for v in VARS_ET}
        e = et0_fao56(s["T2M"], s["T2MDEW"], s["WS2M"], s["ALLSKY_SFC_SW_DWN"], py[k], datas) * dias_mes
        out.append(pd.Series(e, index=datas.year).groupby(level=0).sum(min_count=12))
    return out, viz


# calibração: a mesma conta nas células do CE contra a ET0 diária FAO-56 do POWER (power_ce_diario_et0.nc)
ce = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"].sel(time=slice("1984-01-01", "2025-12-31"))
CLON, CLAT = np.meshgrid(ce.lon.values, ce.lat.values)
ref = ce.groupby("time.year").sum(min_count=360).values.reshape(len(np.unique(ce.time.dt.year)), -1)
cal, _ = et0_anual(CLON.ravel(), CLAT.ravel())
calm = np.array([c.loc[1984:2025].values for c in cal]).T  # (anos, células)
okc = np.isfinite(calm) & np.isfinite(ref) & (ref > 0)
FATOR = float(ref[okc].mean() / calm[okc].mean())
R_CAL = float(np.corrcoef(calm[okc], ref[okc])[0, 1])
print(f"ET0: fator de calibração {FATOR:.3f}, r anual {R_CAL:.3f}, n {okc.sum()}")
ce.close()

ET0_M, viz_et = et0_anual(PX, PY)
tmx_iy, tmx_ix = vizinho_valido("T2M_MAX", PX, PY)
# chave da célula = posição do T2M_MAX + das 4 variáveis da ET0 (municípios vizinhos repartem a mesma)
chave = [f"{tmx_iy[k]}_{tmx_ix[k]}_" + "_".join(f"{viz_et[v][0][k]}_{viz_et[v][1][k]}" for v in VARS_ET) for k in range(n)]
CEL = {}
for k in range(n):
    if chave[k] in CEL:
        continue
    tmx = pd.Series(ARR["T2M_MAX"][:, tmx_iy[k], tmx_ix[k]], index=datas.year).groupby(level=0).mean().where(
        pd.Series(ARR["T2M_MAX"][:, tmx_iy[k], tmx_ix[k]], index=datas.year).groupby(level=0).count() == 12)
    et = ET0_M[k] * FATOR
    CEL[chave[k]] = {"t": tmx, "e": et, "lat": float(plat[tmx_iy[k]]), "lon": float(plon[tmx_ix[k]])}
pw.close()
print("power ok, células", len(CEL))

# ---------------------------------------------------------------- a: água guardada (GRACE), por mesorregião
gr = xr.open_dataset(DADOS / "grace" / "grace_ne_mensal.nc")
NOME_MESO = REF.drop_duplicates("cod_meso").set_index("cod_meso").mesorregiao
gm = celulas_no_poligono(gr.lat.values, gr.lon.values, MUN)  # célula → município → mesorregião (sem dissolver a malha)
gmeso = np.where(gm >= 0, MUN.meso.values[np.maximum(gm, 0)], "")
G = gr["lwe_thickness"].values.reshape(gr.sizes["time"], -1)
gt = pd.to_datetime(gr.time.values)
AG = {}
for meso in sorted(MUN.meso.unique()):
    sel = gmeso == meso
    s = pd.Series(np.nanmean(G[:, sel], axis=1), index=gt)
    s = s.groupby(s.index.year).agg(["mean", "count"])
    AG[meso] = {"nome": NOME_MESO[meso], "a": s["mean"].where(s["count"] >= 6), "n_cel": int(sel.sum())}
gr.close()
print("grace ok, mesorregiões", len(AG))

# ---------------------------------------------------------------- monta os JSON por UF
SAIDA.mkdir(parents=True, exist_ok=True)
BR = lambda x: f"{x:.2f}".replace(".", ",")  # noqa: E731  (decimal com vírgula no texto do site)
meta = {
    "gerado": datetime.date.today().isoformat(), "ini": {"c": A0, "s": 2015, "v": A0, "t": A0, "e": A0, "a": 2002}, "fim": A1,
    "ultimo_completo": ULT, "el_nino_forte": [2010, 2016, 2024],
    "tendencia": "Theil–Sen por década nos anos completos até 2025; sig = Mann–Kendall p < 0,10",
    "et0_calibracao": {"fator": round(FATOR, 3), "r_anual": round(R_CAL, 3),
                       "texto": "ET0 FAO-56 com médias mensais do POWER × ET0 diária do POWER em 84 células do CE, 1984–2025"},
    "fontes": {
        "c": "GPM IMERG V07 (NASA POWER, 0,1°) na malha municipal do IBGE; chuva da estação desde o início da chuva (onset); "
             "2026 = IMERG Late, preliminar. Normal = média 1998–2025.",
        "s": "NASA SMAP L4 (SPL4SMGP v008), umidade na zona da raiz (0–100 cm), na malha municipal; anomalia contra a média do "
             "mesmo mês em 2015–2026.",
        "v": "MODIS Terra MOD13A1 v061 NDVI (500 m, 16 dias, agregado a 0,05°), média do município; pico do ano = média dos 3 "
             "maiores compostos; anomalia contra a média 2000–2025.",
        "t": "NASA POWER (MERRA-2), grade de ~55 km, célula mais próxima: média dos 12 meses do dia mais quente de cada mês.",
        "e": "ET0 FAO-56 (Penman-Monteith) calculada com as médias mensais do NASA POWER (temperatura, orvalho, vento, sol), "
             f"calibrada contra a ET0 diária do POWER no CE (fator {BR(FATOR)}, r {BR(R_CAL)}).",
        "a": "GRACE/GRACE-FO CSR RL06.3 mascons: água total no chão (solo, aquífero, açudes), média da mesorregião (resolução "
             "efetiva ~300 km); anomalia contra 2004–2009; 2017–2018 sem dado (troca de satélite).",
    },
}
por_uf = {}
for k in range(n):
    cod = MUN.cod[k]
    uf = UF[cod[:2]]
    d = por_uf.setdefault(uf, {"meta": meta, "mun": {}, "cel": {}, "reg": {}})
    ch = CH.get(cod, pd.Series(dtype=float))
    so = SO.get(cod, pd.Series(dtype=float))
    pk = PICO[cod]
    nv = pk.loc[A0:ULT].mean()
    va = (pk / nv - 1) * 100
    nc = ch.loc[:ULT].mean() if len(ch) else np.nan
    reg = REG.loc[cod] if cod in REG.index else None
    d["mun"][cod] = {
        "c": serie(ch, A0, A1, 0), "s": serie(so, 2015, A1, 0), "v": serie(va, A0, A1, 0),
        "p": chave[k], "g": MUN.meso[k],
        "tc": [None if pd.isna(nc) else int(round(nc))] + tendencia(ch.index, ch.values, 0),
        "ts": [0] + tendencia(so.index, so.values, 1),
        "tv": [0] + tendencia(va.index, va.values, 1),
        "est": None if reg is None else str(reg.estacao),
    }
    if chave[k] not in d["cel"]:
        c = CEL[chave[k]]
        nt, ne = c["t"].loc[A0:ULT].mean(), c["e"].loc[A0:ULT].mean()
        d["cel"][chave[k]] = {
            "t": serie(c["t"], A0, ULT, 1), "e": serie(c["e"], A0, ULT, 0),
            "tt": [round(float(nt), 1)] + tendencia(c["t"].index, c["t"].values, 2)
                  + [tendencia(c["t"].index, c["t"].values, 2, desde=1981)[0]],
            "te": [int(round(ne))] + tendencia(c["e"].index, c["e"].values, 0),
            "ll": [c["lat"], c["lon"]],
        }
    if MUN.meso[k] not in d["reg"]:
        a = AG[MUN.meso[k]]
        d["reg"][MUN.meso[k]] = {"n": a["nome"], "a": serie(a["a"], 2002, A1, 1), "ta": [0] + tendencia(a["a"].index, a["a"].values, 1)}

for uf, d in por_uf.items():
    p = SAIDA / f"{uf}.json"
    p.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(uf, len(d["mun"]), "municípios", len(d["cel"]), "células", f"{p.stat().st_size / 1024:.0f} KB")

for cod in EXEMPLOS:
    uf = UF[cod[:2]]
    m = por_uf[uf]["mun"][cod]
    c = por_uf[uf]["cel"][m["p"]]
    r = por_uf[uf]["reg"][m["g"]]
    print("\n==", cod, MUN.loc[MUN.cod == cod].index[0])
    print(" chuva", m["c"], m["tc"])
    print(" solo ", m["s"], m["ts"])
    print(" verde", m["v"], m["tv"])
    print(" calor", c["t"], c["tt"])
    print(" evap ", c["e"], c["te"])
    print(" água ", r["n"], r["a"], r["ta"])

# resumo: em quantos municípios cada tendência é clara (para o relatório)
print("\ntendência clara (Mann–Kendall p < 0,10), % dos municípios: sobe / desce")
tot = {k: [0, 0] for k in "csvtea"}
for uf, d in por_uf.items():
    for cod, m in d["mun"].items():
        for k, t in (("c", m["tc"]), ("s", m["ts"]), ("v", m["tv"]), ("t", d["cel"][m["p"]]["tt"]), ("e", d["cel"][m["p"]]["te"]),
                     ("a", d["reg"][m["g"]]["ta"])):
            if t[2] and t[1] is not None:
                tot[k][0 if t[1] > 0 else 1] += 1
for k, (a, b) in tot.items():
    print(f"  {k}: {a / n * 100:.0f}% / {b / n * 100:.0f}%")
