"""Confere no Crossref os artigos de aptidao de culturas, calendario de plantio e analogos climaticos (sem DOI de memoria)."""
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import sessao_http  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
PROJ = Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa")
BUSCAS = {
    "Zabel 2014 aptidão global": "Global agricultural land resources a high resolution suitability evaluation and its perspectives until 2100 under climate change",
    "Waha 2012 datas de semeadura": "Climate-driven simulation of global crop sowing dates",
    "Sacks 2010 calendário global": "Crop planting dates: an analysis of global patterns",
    "Jägermeyr 2021 GGCMI fase 3": "Climate impacts on global agriculture emerge earlier in new generation of climate and crop models",
    "Portmann 2010 MIRCA2000": "MIRCA2000 Global monthly irrigated and rainfed crop areas around the year 2000",
    "Ramirez-Villegas 2011 EcoCrop": "Empirical approaches for assessing impacts of climate change on agriculture: The EcoCrop model and a case study with grain sorghum",
    "Ramirez-Villegas análogos": "Climate analogues: finding tomorrow's agriculture today",
    "Whitcraft 2015 nuvens e EO agrícola": "Cloud cover throughout the agricultural growing season: Impacts on passive optical earth observations",
    "Iizumi 2020 GDHY": "The global dataset of historical yields for major crops 1981-2016",
    "Yu 2020 SPAM": "A cultivated planet in 2010 Part 2 the global gridded agricultural-production maps",
    "Fischer 2021 GAEZ v4": "Global Agro-Ecological Zones v4 Model documentation",
    "Franch 2022 calendário por satélite": "Global crop calendars of maize and wheat in the framework of the WorldCereal project",
}
s = sessao_http(retries=3)
with open(PROJ / "artigos" / "indice.csv", encoding="utf-8-sig") as f:
    idx = {l["doi"]: l for l in csv.DictReader(f)}
for rot, q in BUSCAS.items():
    time.sleep(0.4)
    r = s.get("https://api.crossref.org/works", params={"query.bibliographic": q, "rows": 2}, timeout=60)
    itens = r.json()["message"]["items"] if r.ok else []
    print(f"\n== {rot}")
    for m in itens:
        doi = m.get("DOI", "").lower()
        aut = m.get("author", [])
        print(f"   {doi} | {(m.get('title') or [''])[0][:110]} | {', '.join(a.get('family', '') for a in aut[:3])}{' et al.' if len(aut) > 3 else ''} | "
              f"{(m.get('container-title') or [''])[0][:40]} | {m.get('published', {}).get('date-parts', [[None]])[0]} | cit {m.get('is-referenced-by-count')} | "
              f"no índice: {idx[doi]['status'][:20] if doi in idx else 'não'}")
