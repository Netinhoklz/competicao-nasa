"""Gera site-versao-final/web/dados/declive_mun.json: o que o módulo "Onde o seu roçado sofre mais" (web/js/extras/vulnerabilidade.js,
ponto 12 do desafio) precisa por município do Nordeste. Tudo pré-calculado aqui; o navegador só lê números arredondados.

1. Declive (água correndo / erosão), NASADEM (reprocessamento NASA do SRTM 2000), pasta E:/campeonato-nasa/dados/srtm:
   - Ceará: declividade a 90 m (declividade_ceara_90m.tif), mediana e p90 por município = MEDIDO.
   - Resto do NE: só há a grade de 1 km (declividade_nordeste_1km.tif, DEM em média de bloco), que achata as ladeiras.
     Ajustamos para a escala de 90 m com a relação medida nos 184 municípios do CE (regressão em log: log d90m = a + b log d1km),
     e o site rotula esse valor como estimativa (SUPOSIÇÃO). Os coeficientes, o R² e o erro vão no meta do JSON.
   Declive em % (tan do ângulo × 100), como as classes de relevo da Embrapa (0–3 plano, 3–8 suave, 8–20 ondulado, 20–45 forte).
2. Geada e calor, ERA5 diário 1979–2020 (E:/campeonato-nasa/dados/era5/era5_ne_diario_AAAA.nc, 0,25°, dia em UTC-3):
   - tmin: a noite mais fria do período na célula mais fria do município (°C).
   - quente: dias por mês com Tmax ≥ 35 °C, média dos 42 anos (em décimos de dia; média das células do município).
   Células = centros de grade dentro do município; município pequeno sem centro dentro → a célula mais próxima.

Saída (≈ 80–100 KB): {"meta": {...}, "m": {"<cod IBGE>": [d50, d90, origem, tmin, [12 × décimos de dia quentes]]}}
origem: 1 = medido a 90 m (CE); 0 = estimado do 1 km. Valores null quando o município cai fora da grade (Fernando de Noronha).

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_declive.py"""
import datetime
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
import shapely
import xarray as xr
from rasterio.features import rasterize

RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path("E:/campeonato-nasa/dados")
SAIDA = RAIZ / "web" / "dados" / "declive_mun.json"
LIMIAR_QUENTE = 35.0
ANOS = range(1979, 2021)

mun = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
mun["codarea"] = mun["codarea"].astype(str)
assert len(mun) == 1794, len(mun)


def por_rotulo(rot, val, n):
    """Mediana e p90 de val por rótulo 1..n (rot 0 = fora). Devolve dois vetores (n,) com NaN onde não há pixel."""
    ok = (rot > 0) & np.isfinite(val)
    r, v = rot[ok], val[ok]
    ordem = np.lexsort((v, r))
    r, v = r[ordem], v[ordem]
    ini = np.searchsorted(r, np.arange(1, n + 1), "left")
    fim = np.searchsorted(r, np.arange(1, n + 1), "right")
    p50 = np.full(n, np.nan)
    p90 = np.full(n, np.nan)
    npx = fim - ini
    for i in range(n):
        if npx[i]:
            x = v[ini[i]:fim[i]]
            p50[i] = np.percentile(x, 50)
            p90[i] = np.percentile(x, 90)
    return p50, p90, npx


def pct(graus):
    return np.tan(np.deg2rad(graus)) * 100.0


# ------------------------------------------------------------------ 1 km, NE inteiro
with rasterio.open(DADOS / "srtm" / "declividade_nordeste_1km.tif") as src:
    s1 = pct(src.read(1).astype(np.float64))
    t1 = src.transform
    sh1 = src.shape
rot1 = rasterize([(g, i + 1) for i, g in enumerate(mun.geometry)], out_shape=sh1, transform=t1, fill=0, dtype="int32")
a50, a90, n1 = por_rotulo(rot1, s1, len(mun))
# município pequeno sem pixel com centro dentro: pega os pixels que ele toca
for i in np.flatnonzero(n1 < 4):
    g = mun.geometry.iloc[i]
    m = rasterize([(g, 1)], out_shape=sh1, transform=t1, fill=0, dtype="uint8", all_touched=True).astype(bool) & np.isfinite(s1)
    if m.sum():
        a50[i], a90[i], n1[i] = np.percentile(s1[m], 50), np.percentile(s1[m], 90), m.sum()
print(f"1 km: {np.isfinite(a50).sum()} de {len(mun)} municípios com declive")
del rot1, s1

# ------------------------------------------------------------------ 90 m, Ceará
ce = mun[mun.codarea.str.startswith("23")]
with rasterio.open(DADOS / "srtm" / "declividade_ceara_90m.tif") as src:
    s9 = pct(src.read(1).astype(np.float32))
    t9 = src.transform
    sh9 = src.shape
rot9 = rasterize([(g, i + 1) for i, g in enumerate(ce.geometry)], out_shape=sh9, transform=t9, fill=0, dtype="int16")
c50, c90, n9 = por_rotulo(rot9, s9, len(ce))
del rot9, s9
print(f"90 m CE: {np.isfinite(c50).sum()} de {len(ce)} municípios")

# ------------------------------------------------------------------ ajuste 1 km → 90 m (só no CE, aplicado ao resto)
idx_ce = mun.index.get_indexer(ce.index)
calib = {}
for nome, x1, x9 in (("p50", a50[idx_ce], c50), ("p90", a90[idx_ce], c90)):
    ok = np.isfinite(x1) & np.isfinite(x9) & (x1 > 0) & (x9 > 0)
    lx, ly = np.log10(x1[ok]), np.log10(x9[ok])
    b, a = np.polyfit(lx, ly, 1)
    pred = a + b * lx
    r2 = 1 - ((ly - pred) ** 2).sum() / ((ly - ly.mean()) ** 2).sum()
    # validação: deixa um de fora (o ajuste de 2 parâmetros é estável, mas medimos para não enganar)
    err = []
    for j in range(ok.sum()):
        mm = np.ones(ok.sum(), bool); mm[j] = False
        bj, aj = np.polyfit(lx[mm], ly[mm], 1)
        err.append(abs(10 ** (aj + bj * lx[j]) / 10 ** ly[j] - 1))
    calib[nome] = {"a": round(float(a), 4), "b": round(float(b), 4), "r2_log": round(float(r2), 3), "n": int(ok.sum()),
                   "erro_mediano_pct": round(float(np.median(err)) * 100, 1), "erro_p90_pct": round(float(np.percentile(err, 90)) * 100, 1),
                   "razao_mediana_90m_sobre_1km": round(float(np.median(10 ** ly / 10 ** lx)), 2)}
print("ajuste:", json.dumps(calib, ensure_ascii=False))

d50 = 10 ** (calib["p50"]["a"] + calib["p50"]["b"] * np.log10(np.maximum(a50, 1e-3)))
d90 = 10 ** (calib["p90"]["a"] + calib["p90"]["b"] * np.log10(np.maximum(a90, 1e-3)))
d50[~np.isfinite(a50)] = np.nan
d90[~np.isfinite(a90)] = np.nan
origem = np.zeros(len(mun), int)
d50[idx_ce], d90[idx_ce], origem[idx_ce] = c50, c90, 1

# ------------------------------------------------------------------ ERA5: noite mais fria e dias quentes por mês
quente = None
tmin_abs = None
n_anos = 0
for ano in ANOS:
    with xr.open_dataset(DADOS / "era5" / f"era5_ne_diario_{ano}.nc") as ds:
        tx = ds["tmax"].values
        tn = ds["tmin"].values
        mes = ds["data"].dt.month.values
        lat = ds["lat"].values.astype(float)
        lon = ds["lon"].values.astype(float)
    if quente is None:
        quente = np.zeros((12, len(lat), len(lon)))
        tmin_abs = np.full((len(lat), len(lon)), np.inf)
    q = tx >= LIMIAR_QUENTE
    for m in range(1, 13):
        quente[m - 1] += q[mes == m].sum(axis=0)
    tmin_abs = np.minimum(tmin_abs, np.nanmin(tn, axis=0))
    n_anos += 1
quente /= n_anos
print(f"ERA5: {n_anos} anos")

LON, LAT = np.meshgrid(lon, lat)
tmin_m = np.full(len(mun), np.nan)
quente_m = np.full((len(mun), 12), np.nan)
n_cel = np.zeros(len(mun), int)
dentro_grade = (lon.min() - 0.125, lat.min() - 0.125, lon.max() + 0.125, lat.max() + 0.125)
for i, g in enumerate(mun.geometry):
    m = shapely.contains_xy(g, LON, LAT)
    if not m.any():
        p = g.representative_point()
        if not (dentro_grade[0] <= p.x <= dentro_grade[2] and dentro_grade[1] <= p.y <= dentro_grade[3]):
            continue  # Fernando de Noronha: fora da grade
        m = np.zeros_like(m)
        m[np.abs(lat - p.y).argmin(), np.abs(lon - p.x).argmin()] = True
    n_cel[i] = m.sum()
    tmin_m[i] = tmin_abs[m].min()
    quente_m[i] = quente[:, m].mean(axis=1)


# ------------------------------------------------------------------ JSON
def r1(v):
    return None if not np.isfinite(v) else (round(float(v), 1) if v < 10 else round(float(v)))


saida_m = {}
for i, cod in enumerate(mun.codarea):
    q = None if not np.isfinite(quente_m[i]).all() else [int(round(x * 10)) for x in quente_m[i]]
    saida_m[cod] = [r1(d50[i]), r1(d90[i]), int(origem[i]), None if not np.isfinite(tmin_m[i]) else int(round(tmin_m[i])), q]

ok = np.isfinite(d50)
classe = np.digitize(d50[ok], [3, 8, 20])
meta = {
    "gerado_em": datetime.date.today().isoformat(),
    "script": "site-versao-final/ferramentas/preparar_declive.py",
    "campos": ["d50: declive mediano do município (%)", "d90: 1 em 10 terrenos passa deste declive (%)",
               "origem: 1 = medido a 90 m (Ceará); 0 = estimado da grade de 1 km com o ajuste do CE",
               "tmin: noite mais fria 1979–2020 na célula ERA5 mais fria do município (°C)",
               "quente: dias por mês com Tmax ≥ 35 °C, média 1979–2020, em décimos de dia (jan..dez)"],
    "fonte_declive": ("NASADEM (NASA, reprocessamento do SRTM 2000) via Microsoft Planetary Computer; declividade a 90 m no Ceará e a 1 km "
                      "no Nordeste (DEM em média de bloco), calculada em E:/campeonato-nasa/scripts/baixar_srtm.py; declive em % = tan × 100"),
    "ajuste_1km_90m": calib,
    "fonte_clima": ("ERA5 (ECMWF/Copernicus) diário 1979–2020, 0,25° (~28 km), dia em horário local UTC-3, via Microsoft Planetary Computer; "
                    f"limiar de dia quente: Tmax ≥ {LIMIAR_QUENTE:.0f} °C"),
    "n_anos_era5": n_anos,
    "classes_relevo_embrapa_pct": [3, 8, 20, 45],
    "n_mun": len(mun), "n_medido_90m": int(origem.sum()), "n_com_declive": int(ok.sum()),
    "n_com_clima": int(np.isfinite(tmin_m).sum()),
    "classes_ne": {"plano_lt3": int((classe == 0).sum()), "suave_3a8": int((classe == 1).sum()),
                   "ondulado_8a20": int((classe == 2).sum()), "forte_ge20": int((classe == 3).sum())},
    "tmin_ne": {"min": int(round(np.nanmin(tmin_m))), "n_mun_le_3C": int((np.round(tmin_m) <= 3).sum()),
                "n_mun_le_8C": int((np.round(tmin_m) <= 8).sum()),
                "onde_le_8C": "serras da Bahia: Chapada Diamantina (Piatã, Mucugê, Abaíra, Seabra...) e Vitória da Conquista"},
}
SAIDA.parent.mkdir(parents=True, exist_ok=True)
txt = json.dumps({"meta": meta, "m": saida_m}, ensure_ascii=False, separators=(",", ":"))
SAIDA.write_text(txt, encoding="utf-8")
print(f"gravado {SAIDA} ({len(txt.encode('utf-8')) / 1024:.0f} KB)")
print(json.dumps(meta, ensure_ascii=False, indent=1))
for cod in ("2311306", "2700300", "2903201"):
    print(cod, saida_m[cod])
