"""Designer: confere no Crossref os DOIs das referencias de adocao/comunicacao que nao estao na revisao de literatura."""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import sessao_http

DOIS = [
    "10.1126/science.aay3038",        # Fabregas, Kremer, Schilbach 2019
    "10.1093/ej/ueaa084",             # Cole & Fernando 2021
    "10.1073/pnas.0506125102",        # Patt, Suarez, Gwata 2005
    "10.1023/A:1020785826029",        # Lemos et al. 2002
    "10.1175/BAMS-88-7-1033",         # Pennesi 2007
    "10.1037/0033-295X.102.4.684",    # Gigerenzer & Hoffrage 1995
    "10.1287/mnsc.2016.2643",         # Dietvorst, Simmons, Massey 2018
    "10.1016/j.agsy.2016.09.009",     # Rose et al. 2016
    "10.1073/pnas.1231332100",        # Cash et al. 2003
    "10.1111/j.1574-0862.2011.00545.x",  # Aker 2011
    "10.1073/pnas.1813720116",        # van Etten et al. 2019
    "10.1017/S0014479710000876",      # Hansen et al. 2011
    "10.1080/21550085.2012.685603",   # Taddei 2012
    "10.1175/1520-0469(1969)26<636:APARBN>2.0.CO;2",  # Lorenz 1969
    "10.1016/j.gfs.2021.100577",      # Coggins et al. 2022
    "10.1038/s41893-019-0327-4",      # ? Kpadé? (teste)
]
s = sessao_http(retries=2)
s.headers["User-Agent"] = "doi-check/0.1"
for d in DOIS:
    try:
        r = s.get("https://api.crossref.org/works/" + d, timeout=30)
        if r.status_code != 200:
            print(f"{d}: HTTP {r.status_code}")
            continue
        m = r.json()["message"]
        au = m.get("author", [])
        a1 = au[0].get("family", "?") if au else "?"
        ano = (m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0][0]
        print(f"{d}: {a1} et al. ({ano}) | {m.get('title', [''])[0][:110]} | {(m.get('container-title') or [''])[0]} "
              f"{m.get('volume', '')}:{m.get('page', m.get('article-number', ''))}")
    except Exception as e:  # noqa: BLE001
        print(f"{d}: erro {e}")
