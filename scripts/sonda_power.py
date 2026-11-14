"""Testes pequenos para descobrir limites do endpoint regional do NASA POWER."""
import sys
import time

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

sys.stdout.reconfigure(encoding="utf-8")
s = sessao_http(retries=1)
URL = "https://power.larc.nasa.gov/api/temporal/daily/regional"


def teste(rotulo, params, bbox=BBOX_CE, start="20240101", end="20240110", temporal="daily"):
    url = f"https://power.larc.nasa.gov/api/temporal/{temporal}/regional"
    q = dict(parameters=params, community="AG", **{"longitude-min": bbox[0], "latitude-min": bbox[1],
             "longitude-max": bbox[2], "latitude-max": bbox[3]}, start=start, end=end, format="JSON")
    t0 = time.time()
    try:
        r = s.get(url, params=q, timeout=300)
        dt = time.time() - t0
        if r.status_code != 200:
            print(f"{rotulo}: HTTP {r.status_code} {dt:.1f}s :: {r.text[:300]}")
            return None
        d = r.json()
        feats = d.get("features", [])
        npar = len(feats[0]["properties"]["parameter"]) if feats else 0
        ndias = len(next(iter(feats[0]["properties"]["parameter"].values()))) if feats else 0
        print(f"{rotulo}: OK {dt:.1f}s pontos={len(feats)} params={npar} passos={ndias} bytes={len(r.content)}")
        return d
    except Exception as e:
        print(f"{rotulo}: ERRO {e}")


teste("1 param 10 dias", "T2M_MAX")
teste("3 params 10 dias", "T2M_MAX,T2M_MIN,PRECTOTCORR")
teste("1 param 1 ano", "T2M_MAX", start="20230101", end="20231231")
teste("1 param 5 anos", "T2M_MAX", start="20190101", end="20231231")
teste("1 param bbox NE", "T2M_MAX", bbox=BBOX_NE)
teste("mensal 1 param bbox CE 1981-2024", "PRECTOTCORR", start="1981", end="2024", temporal="monthly")
teste("mensal 3 params CE", "PRECTOTCORR,T2M,GWETROOT", start="1981", end="2024", temporal="monthly")
# disponibilidade de IMERG_PRECTOT no ponto
for ano in (2000, 2001, 2010, 2020, 2021, 2022, 2023, 2024, 2025):
    r = s.get("https://power.larc.nasa.gov/api/temporal/daily/point", params=dict(
        parameters="IMERG_PRECTOT", community="AG", longitude=-38.5, latitude=-3.7,
        start=f"{ano}0601", end=f"{ano}0603", format="JSON"), timeout=120)
    v = r.json()["properties"]["parameter"]["IMERG_PRECTOT"] if r.ok else r.text[:100]
    print("IMERG", ano, v)
# ultimo dia disponivel
r = s.get("https://power.larc.nasa.gov/api/temporal/daily/point", params=dict(
    parameters="T2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,GWETROOT", community="AG", longitude=-38.5, latitude=-3.7,
    start="20261020", end="20261113", format="JSON"), timeout=120)
print("ultimos:", r.status_code, r.text[:200] if not r.ok else {k: list(v.items())[-6:] for k, v in r.json()["properties"]["parameter"].items()})
