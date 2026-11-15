"""Gera site-versao-final/web/dados/camadas_mun.json: as camadas do mapa do globo (index.html, js/globo/camadas.js) para os
1.794 municípios do Nordeste, com poucos números por município.

Camadas (a ordem dos municípios é a de web/dados/busca_municipios.json, gravada em "cods"):
  quebra  chance de quebra do milho em 2027, em 10 anos parecidos (0–10): dados/projecao_mun.json, Milho, anos.2027.chance_quebra
          (quebra = colher menos da metade da mediana 1998–2025 do município). PROJEÇÃO. null = município sem série de milho.
  chuva   chuva típica da estação em mm, arredondada a 10 mm: web/dados/municipios_ne.json, campo normal_mm (IMERG V07, chuva
          desde o início da estação, mediana 1998–2025 sem os El Niños fortes): o MESMO número do painel ao lado do mapa. MEDIDO.
  solo    umidade do solo na zona da raiz (SMAP L4), mês a mês de abr/2015 a out/2026 e "agora" (30 dias até a última data do
          arquivo), em 5 classes pela posição entre os anos da mesma época (1 = o mais seco). MEDIDO.
          A regra é a do núcleo (nucleo/motor.py, smap_agora): mesmo pixel de 9 km no ponto interno do município
          (representative_point da malha do motor), posição pelo rank "min", seco = posição ≤ 3, úmido = posição ≥ n − 2.
          Aqui a posição 1 vira "o mais seco" e a posição n "o mais úmido". Meses com menos de 20 dias de dado ficam sem classe.
          Codificação: 6 símbolos por mês (0 o mais seco, 1 seco, 2 normal, 3 úmido, 4 o mais úmido, 5 sem dado), dois meses por
          caractere em base 36 (c = 6·a + b), uma linha por município.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_camadas_mapa.py"""
import datetime
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path("E:/campeonato-nasa/dados")
SAIDA = RAIZ / "web" / "dados" / "camadas_mun.json"
B36 = "0123456789abcdefghijklmnopqrstuvwxyz"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

cods = [m["cod"] for m in json.loads((RAIZ / "web" / "dados" / "busca_municipios.json").read_text(encoding="utf-8"))["municipios"]]
assert len(cods) == 1794 and len(set(cods)) == 1794

# ---------------------------------------------------------------- quebra do milho em 2027 (projeção)
proj = json.loads((RAIZ / "dados" / "projecao_mun.json").read_text(encoding="utf-8"))


def quebra(cod):
    p = ((((proj.get(cod) or {}).get("Milho") or {}).get("anos") or {}).get("2027") or {}).get("chance_quebra")
    return None if p is None else int(round(p * 10))


q = [quebra(c) for c in cods]

# ---------------------------------------------------------------- chuva típica da estação (o número do painel)
mn = json.loads((RAIZ / "web" / "dados" / "municipios_ne.json").read_text(encoding="utf-8"))
i_normal = mn["campos"].index("normal_mm")
chuva = [None if (mn["m"].get(c) or [None] * 20)[i_normal] is None else int(round(mn["m"][c][i_normal] / 10)) for c in cods]

# ---------------------------------------------------------------- solo (SMAP L4) no ponto do núcleo
g = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
g["cod"] = g.codarea.astype(str)
rp = g.geometry.representative_point()
ponto = {c: (round(p.y, 4), round(p.x, 4)) for c, p in zip(g.cod, rp)}  # igual a motor.ponto_do_municipio
lat = np.array([ponto[c][0] for c in cods])
lon = np.array([ponto[c][1] for c in cods])

ds = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
iy = np.abs(ds.lat.values[None, :] - lat[:, None]).argmin(1)   # "nearest", como o .sel(method="nearest") do motor
ix = np.abs(ds.lon.values[None, :] - lon[:, None]).argmin(1)
S = ds.sm_rootzone.values[:, iy, ix].astype("float64")          # (dias, municípios)
t = pd.DatetimeIndex(ds.time.values)
fim = t.max()
dia = pd.DataFrame(S, index=t)

# agora: média dos 30 dias até a última data, em cada ano de 2015 até o ano da última data (como motor._prepara_smap)
agora = []
for ano in range(2015, fim.year + 1):
    f = fim - pd.DateOffset(years=fim.year - ano)
    agora.append(dia.loc[f - pd.Timedelta(days=29):f].mean())
agora = pd.DataFrame(agora, index=range(2015, fim.year + 1))  # (anos, municípios)

# meses completos (>= 20 dias com dado) de abr/2015 ao último mês fechado antes da última data
cont = dia.resample("MS").count()
mes = dia.resample("MS").mean().where(cont >= 20)
mes = mes.loc["2015-04-01":(fim.to_period("M") - 1).to_timestamp()]


def classes(tab):
    """tab: (anos, municípios) da mesma época. Classe 0–5 de cada ano pela posição entre os anos (regra do núcleo)."""
    r = tab.rank(method="min")                    # 1 = o mais seco
    n = tab.notna().sum()
    c = pd.DataFrame(2, index=tab.index, columns=tab.columns)
    c[r <= 3] = 1
    c[r == 1] = 0
    c[r.ge(n - 2, axis=1)] = 3
    c[r.eq(n, axis=1)] = 4
    c[tab.isna()] = 5
    c.loc[:, n < 5] = 5                           # como o motor: menos de 5 anos = sem dado
    return c.astype(int), n


cl = pd.DataFrame(5, index=mes.index, columns=mes.columns)
n_pos = []
for k in range(1, 13):
    sel = mes.index.month == k
    c, n = classes(mes[sel])
    cl[sel] = c.values
c_ag, n_ag = classes(agora)
pos = list(mes.index)
tab = np.vstack([cl.values, c_ag.values[-1:]])    # (posições, municípios): os meses e, por último, agora
for p in pos:
    n_pos.append(int(mes[mes.index.month == p.month].notna().sum().max()))
n_pos.append(int(n_ag.max()))

if tab.shape[0] % 2:
    tab = np.vstack([tab, np.full((1, tab.shape[1]), 5)])
linhas = ["".join(B36[6 * tab[i, m] + tab[i + 1, m]] for i in range(0, tab.shape[0], 2)) for m in range(tab.shape[1])]

# conferência com o núcleo (testes/exemplos/local_2311306.json: posição 8 de 12, "normal para a época")
iq = cods.index("2311306")
r_q = agora.iloc[:, iq].rank(method="min")
print("Quixadá agora: posição", int(r_q.iloc[-1]), "de", int(agora.iloc[:, iq].notna().sum()), "classe", int(c_ag.iloc[-1, iq]))

rotulos = [f"{MESES[p.month - 1]}/{p.year}" for p in pos] + ["agora"]
out = {
    "_meta": {
        "descricao": "Camadas do mapa do globo (js/globo/camadas.js), uma posição por município na ordem de 'cods'.",
        "gerado_em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "script": "site-versao-final/ferramentas/preparar_camadas_mapa.py",
        "quebra": ("Chance de quebra do milho em 2027 em 10 anos parecidos (0–10); quebra = rendimento < 0,5 × mediana 1998–2025 "
                   "do município (IBGE PAM). Projeção de dados/projecao_mun.json (quantis do município encolhidos para a "
                   "mesorregião, 2027 entre os 4 El Niños fortes: 1998, 2010, 2016, 2024). null = sem série de milho."),
        "chuva": ("Chuva típica da estação em dezenas de mm: GPM IMERG V07 (NASA POWER, 0,1°), chuva desde o início da estação "
                  "(onset), mediana 1998–2025 sem os El Niños fortes; campo normal_mm de web/dados/municipios_ne.json (o painel)."),
        "solo": ("NASA SMAP L4 SPL4SMGP v008, umidade na zona da raiz (0–100 cm), pixel de 9 km no ponto interno do município (o "
                 "mesmo do núcleo). Cada posição é um mês (média dos dias, mínimo 20) ou 'agora' (30 dias até "
                 f"{fim:%d/%m/%Y}); a classe compara com a mesma época nos outros anos de 2015–2026: 0 o mais seco, 1 seco "
                 "(posição ≤ 3), 2 normal, 3 úmido (posição ≥ n − 2), 4 o mais úmido, 5 sem dado. Mesma regra do núcleo."),
        "codificacao_solo": "dois meses por caractere em base 36: c = 6·a + b (a = classe do mês ímpar da lista, b = a do seguinte)",
    },
    "cods": ",".join(cods),
    "quebra": q,
    "chuva": chuva,
    "solo": {"rotulos": rotulos, "n_anos": n_pos, "fim": f"{fim:%Y-%m-%d}", "s": linhas},
}
SAIDA.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"{SAIDA}: {SAIDA.stat().st_size / 1024:.0f} KB, {len(rotulos)} posições do solo, "
      f"quebra sem dado {sum(v is None for v in q)}, chuva sem dado {sum(v is None for v in chuva)}")
dist = np.bincount(tab[len(rotulos) - 1].ravel(), minlength=6)
print("agora por classe (0 o mais seco … 4 o mais úmido, 5 sem dado):", dist.tolist())
