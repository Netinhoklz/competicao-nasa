"""Gera site-versao-final/web/dados/camadas_tempo.json: as duas camadas do mapa do globo que andam no tempo, ano a ano, além do
solo (js/globo/camadas.js, abas "Calor" e "Água guardada"; ponto 11 do desafio: ondas de calor e queda da água guardada no mapa).

Não lê base nova: reaproveita as séries já levadas ao município em web/dados/tendencias/<UF>.json (ferramentas/preparar_tendencias.py):
  calor  NASA POWER (MERRA-2), grade de ~55 km, célula mais próxima do município: média dos 12 meses do dia mais quente de cada mês,
         2000–2025, e o normal da própria célula (média 2000–2025, campo tt[0]). MEDIDO. Municípios vizinhos dividem a mesma célula.
  agua   NASA GRACE/GRACE-FO CSR RL06.3 mascons: água total no chão (solo, aquífero, açudes) em cm, média da mesorregião, anomalia
         contra 2004–2009, 2002–2026 (2017–2018 sem dado: troca de satélite). MEDIDO. O GRACE não enxerga menos que ~300 km.

Formato (a ordem dos municípios é a de web/dados/busca_municipios.json, a mesma de camadas_mun.json):
  calor: {ini, fim, cel: [[°C×10 por ano]], n: [normal °C×10 por célula], i: [célula de cada município, -1 sem dado]}
  agua:  {ini, fim, reg: [[cm×10 por ano, null sem dado]], nome: [mesorregião], i: [mesorregião de cada município, -1 sem dado]}

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_camadas_tempo.py"""
import datetime
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
WEB = RAIZ / "web" / "dados"
SAIDA = WEB / "camadas_tempo.json"

busca = json.loads((WEB / "busca_municipios.json").read_text(encoding="utf-8"))["municipios"]
cods = [m["cod"] for m in busca]
uf_de = {m["cod"]: m["uf"] for m in busca}
assert len(cods) == 1794 and len(set(cods)) == 1794

T = {uf: json.loads((WEB / "tendencias" / f"{uf}.json").read_text(encoding="utf-8")) for uf in sorted(set(uf_de.values()))}
meta = next(iter(T.values()))["meta"]
ini_t, ini_a, fim = meta["ini"]["t"], meta["ini"]["a"], meta["fim"]
n_t = meta["ultimo_completo"] - ini_t + 1  # calor: só anos completos (2000–2025)
n_a = fim - ini_a + 1                       # água guardada: 2002–2026

cel_id, cel, cel_n = {}, [], []
reg_id, reg, reg_nome = {}, [], []
i_cel, i_reg = [], []
for c in cods:
    d = T[uf_de[c]]
    m = d["mun"].get(c)
    if not m:
        i_cel.append(-1)
        i_reg.append(-1)
        continue
    p = d["cel"].get(m.get("p"))
    if p and p.get("t") and p.get("tt") and p["tt"][0] is not None:
        if m["p"] not in cel_id:
            cel_id[m["p"]] = len(cel)
            serie = (p["t"] + [None] * n_t)[:n_t]
            cel.append([None if v is None else int(round(v * 10)) for v in serie])
            cel_n.append(int(round(p["tt"][0] * 10)))
        i_cel.append(cel_id[m["p"]])
    else:
        i_cel.append(-1)
    g = d["reg"].get(m.get("g"))
    if g and g.get("a"):
        if m["g"] not in reg_id:
            reg_id[m["g"]] = len(reg)
            serie = (g["a"] + [None] * n_a)[:n_a]
            reg.append([None if v is None else int(round(v * 10)) for v in serie])
            reg_nome.append(g.get("n", m["g"]))
        i_reg.append(reg_id[m["g"]])
    else:
        i_reg.append(-1)

# conferência: quantos municípios ficaram sem série e como se espalham as diferenças do calor (para as classes do mapa)
sem_t, sem_a = i_cel.count(-1), i_reg.count(-1)
difs = sorted((v - cel_n[k]) / 10 for k, s in enumerate(cel) for v in s if v is not None)
q = lambda f: difs[int(f * (len(difs) - 1))]
aguas = sorted(v / 10 for s in reg for v in s if v is not None)
qa = lambda f: aguas[int(f * (len(aguas) - 1))]

out = {
    "_sobre": {
        "gerado": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "script": "ferramentas/preparar_camadas_tempo.py",
        "ordem": "municípios na ordem de web/dados/busca_municipios.json (a mesma de camadas_mun.json)",
        "calor": meta["fontes"]["t"], "agua": meta["fontes"]["a"],
    },
    "n": len(cods),
    "calor": {"ini": ini_t, "fim": ini_t + n_t - 1, "cel": cel, "n": cel_n, "i": i_cel},
    "agua": {"ini": ini_a, "fim": fim, "reg": reg, "nome": reg_nome, "i": i_reg},
}
SAIDA.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"{SAIDA.name}: {SAIDA.stat().st_size / 1024:.0f} KB · {len(cel)} células do POWER, {len(reg)} mesorregiões do GRACE")
print(f"sem calor: {sem_t} municípios · sem água guardada: {sem_a}")
print("calor, diferença do normal (°C), quantis 5/20/50/80/95%:", [round(q(f), 2) for f in (0.05, 0.2, 0.5, 0.8, 0.95)])
print("água guardada (cm), quantis 5/20/50/80/95%:", [round(qa(f), 1) for f in (0.05, 0.2, 0.5, 0.8, 0.95)])
