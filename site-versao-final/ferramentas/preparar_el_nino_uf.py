"""Gera site-versao-final/web/dados/el_nino_uf.json: a manchete de El Niño por estado, com a definição única do motor
(decisão 3 do PLANO_INTEGRACAO.md). Para cada UF e cada El Niño forte (anos-quadra com ONI out–dez/nov–jan ≥ 1,5:
1998, 2010, 2016, 2024), a % dos municípios cuja chuva da estação (IMERG) caiu no terço mais seco do próprio município.

Mesma série e mesma regra de nucleo/motor.py (_perspectiva_municipal): onset_ne_mun.csv, coluna chuva_estacao_mm, só
anos ≤ 2025 (2026 é IMERG Late preliminar), municípios com ≥ 15 estações, terço seco = chuva ≤ quantil 1/3 da série
1998–2025 do município. Substitui o enso.uf do João Pedro (ONI jul–set ≥ 0,5, 6 anos).

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_el_nino_uf.py"""
import datetime
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path("E:/campeonato-nasa/dados")
SAIDA = RAIZ / "web" / "dados" / "el_nino_uf.json"
UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}

EVT = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
EN = sorted(int(a) for a in EVT[(EVT.ONI_OND_NDJ >= 1.5) & EVT.quadra_afetada.between(1998, 2025)].quadra_afetada)
assert EN == [1998, 2010, 2016, 2024], EN

ONS = pd.read_csv(DADOS / "analogos_aprofundado" / "onset_ne_mun.csv", dtype={"cod": str})
o = ONS[ONS.ano <= 2025].dropna(subset=["chuva_estacao_mm"])
linhas = []
for cod, g in o.groupby("cod"):
    s = g.set_index("ano").chuva_estacao_mm
    if len(s) < 15:
        continue
    t1 = s.quantile(1 / 3)
    linhas += [{"uf": UF[cod[:2]], "cod": cod, "ano": a, "seco": bool(s[a] <= t1)} for a in EN if a in s.index]
    linhas.append({"uf": UF[cod[:2]], "cod": cod, "ano": None, "seco": None})  # conta o município na UF
L = pd.DataFrame(linhas)

out = {"definicao": ("Em cada El Niño forte (anos-quadra com ONI de out–dez/nov–jan ≥ 1,5), a % dos municípios do estado cuja chuva da "
                     "estação (IMERG, início da estação pelo onset) caiu no terço mais seco do próprio município (chuva ≤ quantil 1/3 da "
                     "série 1998–2025 do município). Por acaso, seria 33%. 'media' = média simples dos anos com dado. MEDIDO, não é previsão."),
       "anos": EN, "acaso_pct": 33, "uf": {},
       "avisos": [],
       "fonte": "E:/campeonato-nasa/dados/analogos_aprofundado/onset_ne_mun.csv (IMERG Final até 09/2025); ONI: el_nino_2026/eventos.csv",
       "script": "site-versao-final/ferramentas/preparar_el_nino_uf.py",
       "gerado_em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
for uf in ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]:
    g = L[L.uf == uf]
    e = g.dropna(subset=["ano"])
    pct, n = {}, {}
    for a in EN:
        x = e[e.ano == a].seco
        pct[str(a)] = int(round(100 * x.mean())) if len(x) else None
        n[str(a)] = int(len(x))
    v = [p for p in pct.values() if p is not None]
    out["uf"][uf] = {"pct_terco_seco": pct, "media": int(round(sum(v) / len(v))), "n_mun": int(g.cod.nunique()), "n_mun_por_ano": n}
sem98 = [u for u, d in out["uf"].items() if not d["n_mun_por_ano"]["1998"]]
com98 = [f"{u} {d['n_mun_por_ano']['1998']} de {d['n_mun']}" for u, d in out["uf"].items() if d["n_mun_por_ano"]["1998"]]
out["avisos"] = [f"1998: o IMERG mensal começa em jan/1998, então só há estação de 1998 onde a chuva começa em mar–abr ({', '.join(com98)} "
                 f"municípios); em {', '.join(sem98)} a média usa só 2010, 2016 e 2024",
                 "no litoral leste o IMERG capta só 39–72% da chuva do INMET (viabilidade dos artigos, bloco B2)"]
SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(json.dumps(out, ensure_ascii=False, allow_nan=False, indent=1), encoding="utf-8")
for uf, d in out["uf"].items():
    print(uf, d["pct_terco_seco"], "média", d["media"], "n", d["n_mun"], d["n_mun_por_ano"])
print(SAIDA, SAIDA.stat().st_size, "bytes")
