"""Gera site-versao-final/web/dados/calor_cenario.json: o controle "E se esquentar?" da aba Calor de "Onde o seu roçado sofre mais"
(web/js/extras/vulnerabilidade.js; ponto 13 do desafio: controle de cenário de temperatura).

Pergunta: se cada dia fosse 1 °C ou 2 °C mais quente, quantos dias por mês passariam de 35 °C na flor? É o mesmo que contar, no
clima medido, os dias com máxima de 34 °C ou mais (+1 °C) e de 33 °C ou mais (+2 °C). Mesma base e mesmas células de
preparar_declive.py (ERA5 diário 1979–2020, 0,25°, dia em UTC-3; média das células com centro dentro do município, ou a mais
próxima), então "hoje" (≥ 35 °C) continua vindo de declive_mun.json e os dois cenários ficam neste arquivo, baixado só quando a
pessoa toca em "+1 °C" ou "+2 °C". É um deslocamento uniforme do clima medido (SUPOSIÇÃO), não uma projeção de modelo climático.

Saída: {"meta": {...}, "m": {"<cod IBGE>": [[12 × décimos de dia ≥ 34 °C], [12 × décimos de dia ≥ 33 °C]]}}

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_calor_cenario.py"""
import datetime
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import shapely
import xarray as xr

RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path("E:/campeonato-nasa/dados")
SAIDA = RAIZ / "web" / "dados" / "calor_cenario.json"
LIMIARES = (34.0, 33.0)  # 35 °C com +1 °C e com +2 °C
ANOS = range(1979, 2021)

mun = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
mun["codarea"] = mun["codarea"].astype(str)
assert len(mun) == 1794, len(mun)

conta, n_anos = None, 0
for ano in ANOS:
    with xr.open_dataset(DADOS / "era5" / f"era5_ne_diario_{ano}.nc") as ds:
        tx = ds["tmax"].values
        mes = ds["data"].dt.month.values
        lat = ds["lat"].values.astype(float)
        lon = ds["lon"].values.astype(float)
    if conta is None:
        conta = np.zeros((len(LIMIARES), 12, len(lat), len(lon)))
    for k, lim in enumerate(LIMIARES):
        q = tx >= lim
        for m in range(1, 13):
            conta[k, m - 1] += q[mes == m].sum(axis=0)
    n_anos += 1
conta /= n_anos
print(f"ERA5: {n_anos} anos")

LON, LAT = np.meshgrid(lon, lat)
dentro_grade = (lon.min() - 0.125, lat.min() - 0.125, lon.max() + 0.125, lat.max() + 0.125)
saida_m = {}
for cod, g in zip(mun.codarea, mun.geometry):
    m = shapely.contains_xy(g, LON, LAT)
    if not m.any():
        p = g.representative_point()
        if not (dentro_grade[0] <= p.x <= dentro_grade[2] and dentro_grade[1] <= p.y <= dentro_grade[3]):
            continue  # Fernando de Noronha: fora da grade
        m = np.zeros_like(m)
        m[np.abs(lat - p.y).argmin(), np.abs(lon - p.x).argmin()] = True
    saida_m[cod] = [[int(round(x * 10)) for x in conta[k][:, m].mean(axis=1)] for k in range(len(LIMIARES))]

meta = {
    "gerado_em": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
    "script": "site-versao-final/ferramentas/preparar_calor_cenario.py",
    "campos": ["dias por mês com Tmax ≥ 34 °C (= ≥ 35 °C com +1 °C), média 1979–2020, em décimos de dia (jan..dez)",
               "dias por mês com Tmax ≥ 33 °C (= ≥ 35 °C com +2 °C), idem"],
    "fonte": "ERA5 (ECMWF/Copernicus) diário 1979–2020, 0,25° (~28 km), dia em UTC-3; mesmas células de preparar_declive.py",
    "regra": "cenário = o clima medido deslocado de +1 °C ou +2 °C em todos os dias (suposição; não é projeção de modelo climático)",
    "n_anos_era5": n_anos, "n_mun": len(saida_m),
}
txt = json.dumps({"meta": meta, "m": saida_m}, ensure_ascii=False, separators=(",", ":"))
SAIDA.write_text(txt, encoding="utf-8")
print(f"gravado {SAIDA} ({len(txt.encode('utf-8')) / 1024:.0f} KB)")
for cod in ("2311306", "2700300", "2903201"):
    print(cod, saida_m.get(cod))
