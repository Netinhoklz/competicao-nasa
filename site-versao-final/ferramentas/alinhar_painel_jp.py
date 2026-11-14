"""Alinha a série de chuva do painel Roça Certa (João Pedro) com a do núcleo do José, para as duas telas mostrarem o mesmo número.

O painel do JP media a chuva numa janela fixa de 4 meses, e o núcleo usa a estação a partir do início da chuva (IMERG; onset_ne_mun.csv),
em % da mediana dos anos sem El Niño forte, só até 2025 (2026 é IMERG Late, preliminar). Este script reescreve em
web/dados/municipios_ne.json os campos serie_pct (por ano) e normal_mm (a mediana usada), com a mesma conta de motor._perspectiva_municipal.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 ferramentas/alinhar_painel_jp.py
"""
import json
from pathlib import Path

import pandas as pd

DADOS = Path("E:/campeonato-nasa/dados")
ARQ = Path(__file__).resolve().parents[1] / "web" / "dados" / "municipios_ne.json"

evt = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
FORTES = set(evt[evt.ONI_OND_NDJ >= 1.5].quadra_afetada.astype(int))
ons = pd.read_csv(DADOS / "analogos_aprofundado" / "onset_ne_mun.csv", dtype={"cod": str})
ons = ons[ons.ano <= 2025].dropna(subset=["chuva_estacao_mm"])

d = json.loads(ARQ.read_text(encoding="utf-8"))
i_serie, i_normal = d["campos"].index("serie_pct"), d["campos"].index("normal_mm")
anos = d["anos"]
mudou = 0
for cod, g in ons.groupby("cod"):
    if cod not in d["m"]:
        continue
    s = g.set_index("ano").chuva_estacao_mm
    med = s[~s.index.isin(FORTES)].median()
    if not med or pd.isna(med):
        continue
    d["m"][cod][i_serie] = [int(round(100 * s[a] / med)) if a in s.index else None for a in anos]
    d["m"][cod][i_normal] = int(round(med))
    mudou += 1
d["fonte_serie"] = ("Estação de chuva a partir do início da chuva (IMERG via NASA POWER; onset_ne_mun.csv), em % da mediana dos anos sem "
                    "El Niño forte, 1998–2025; 2026 fica de fora (IMERG Late, preliminar). Mesma conta do núcleo (motor._perspectiva_municipal).")
ARQ.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
q = d["m"]["2311306"]
print(f"{mudou} municípios alinhados. Quixadá: normal {q[i_normal]} mm; 2010 {q[i_serie][anos.index(2010)]}%, "
      f"2016 {q[i_serie][anos.index(2016)]}%, 2024 {q[i_serie][anos.index(2024)]}%")
