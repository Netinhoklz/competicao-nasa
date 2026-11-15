"""Gera site-versao-final/web/dados/confianca_mun.json: "confiança dos dados aqui", por município do Nordeste (ponto 16).

Cada município recebe só critérios objetivos que o núcleo já usa; nada é opinião. Mesmas regras de nucleo/motor.py e de
web/js/passos/dinheiro/calculo.js, recalculadas direto dos dados (sem chamar a API em laço):

  leste       a até ~20 km (0,2°) da costa leste (box -41,0/-18,6/-34,6/-5,1): o IMERG capta só 39–72% da chuva medida
              (motor._leste_costeiro, viabilidade dos artigos, bloco B2)                                            peso 2
  agro        rendimento mediano do PAM acima de 2× o da roça de família da CONAB (milho 1.800, feijão 800, mandioca
              17.400 kg/ha): a série do IBGE mistura lavoura grande (calculo.js, CONAB_FAMILIAR_KG_HA)                peso 2
  pam_curta   milho ou feijão sem série no município (menos de 10 anos com 10 ha ou mais; financeiro_mun.json):
              o passo "Quanto rende" não faz a conta                                                               peso 2
  mandioca_sem_serie  a mandioca entra no plano e não tem série do IBGE aqui                                       peso 1
  mandioca_repete     o IBGE repete o rendimento da mandioca do ano anterior em 30% dos anos ou mais                peso 1
  estimada    uma cultura anual do plano sem ZARC aqui: a data de plantar é estimada pelo início da chuva (IMERG)  peso 1
  ciclo       o ZARC de uma cultura anual do plano junta grupos de ciclo sem conferir a cultivar
              (só caupi, sorgo forrageiro e mamona do CE foram conferidos; gaez_zarc_municipio.CICLOS_COM_CULTIVAR).
              Vale em quase todo o NE (o milho não foi conferido em lugar nenhum): fica na lista, sem baixar o nível  peso 0
  el_nino     nos El Niños fortes da série IMERG (2010, 2016, 2024) a chuva da estação daqui discordou: pelo menos um
              ano com ≤ 75% do normal e outro com ≥ 100% (motor._perspectiva_municipal)                            peso 1
  smap        o SMAP L4 não tem leitura no pixel do município (motor.smap_agora, mesma janela de 30 dias)         peso 1
  portoes     a estação daqui não é a quadra do norte (começa depois de fevereiro): os portões de 19/mar e 30/abr
              não foram medidos aqui (motor.regime)                                                               peso 1
  analogos    nenhum estudo de rotação com clima parecido (w < 0,3 na assinatura do NASA POWER; motor.analogos)   peso 1

O plano usado nos critérios "estimada" e "ciclo" é o plano padrão (sem respostas): leguminosa, mandioca (tampão),
forragem e o cereal do baixio, escolhidos como em motor.plano a partir da situação de cada cultura (gaez_zarc/nordeste,
mesma amostra do GAEZ no ponto interno do município; ZARC plurianual do CE para mandioca e milheto). A palma das bordas
(perene) fica fora. O módulo web/js/extras/confianca.js refina "estimada" com a agenda real da resposta da API.

Nível = soma dos pesos: 0–1 alta, 2–3 média, 4 ou mais baixa. Formato (compacto, para caber em ≤ 300 KB):
  {"_sobre": {...}, "_textos": {chave: {"texto", "tecnico", "peso"}}, "<cod>": {"nivel": "alta|media|baixa", "motivos": [chave, ...]}}
O módulo confianca.js devolve o contrato completo {nivel, motivos: [{chave, texto}], tecnico: [...]} (confiancaDe).

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_confianca.py"""
import datetime
import json
import warnings
from collections import Counter
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import box

warnings.filterwarnings("ignore", message="Geometry is in a geographic CRS")  # 0,2° como no motor
RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path("E:/campeonato-nasa/dados")
SAIDA = RAIZ / "web" / "dados" / "confianca_mun.json"

TEXTOS = {  # frente: até 10 palavras; técnico: onde o julgamento humano pesa mais, até 10 palavras
    "leste": ("Perto do mar, o satélite vê menos chuva que a real.", "Comparar com o pluviômetro da comunidade.", 2),
    "agro": ("O IBGE daqui mistura lavoura grande com roça de família.", "Refazer a conta com a colheita da família.", 2),
    "pam_curta": ("O IBGE tem poucos anos de milho ou feijão aqui.", "Estimar a colheita pela experiência da família.", 2),
    "mandioca_sem_serie": ("Sem série de mandioca do IBGE aqui.", "Estimar a colheita da mandioca com quem já planta.", 1),
    "mandioca_repete": ("O IBGE repete a mandioca de um ano para outro.", "Conferir a colheita da mandioca na casa de farinha.", 1),
    "estimada": ("Uma data de plantar foi estimada pela chuva.", "Confirmar a data de plantar desta cultura.", 1),
    "ciclo": ("O zoneamento não conferiu o ciclo da semente.", "Ver se a semente é do ciclo certo.", 0),
    "el_nino": ("Nos anos de El Niño, aqui houve seca e ano bom.", "Ler a chuva de fevereiro antes de decidir.", 1),
    "smap": ("O satélite não lê a umidade do solo aqui.", "Conferir a umidade da terra na mão.", 1),
    "portoes": ("As datas de decisão foram medidas no sertão do Ceará.", "Ajustar as datas de troca à estação daqui.", 1),
    "analogos": ("Os estudos da rotação vêm de clima diferente.", "Testar a rotação numa parte pequena primeiro.", 1),
}
ORDEM = list(TEXTOS)  # mesma ordem de apresentação: peso maior primeiro, depois a ordem acima
NIVEL = lambda s: "alta" if s <= 1 else "media" if s <= 3 else "baixa"  # noqa: E731
CONAB_FAMILIAR_KG_HA = {"Milho": 1800, "Feijão": 800, "Mandioca": 17400}
ZARC_NOME = {"Feijão-caupi": "Feijão Caupi", "Milho": "Milho 1ª Safra", "Feijão comum": "Feijão 2ª Safra", "Amendoim": "Amendoim",
             "Sorgo granífero": "Sorgo Granífero", "Sorgo forrageiro": "Sorgo Forrageiro"}
GAEZ_SEM_ZARC = {"Mandioca": "mandioca", "Milheto": "milheto"}
PLUR_NOME = {"Mandioca": "Mandioca", "Milheto": "Milheto"}
APTA = 40

# ---------------------------------------------------------------- municípios e ponto interno (o mesmo de motor.ponto_do_municipio)
MUN = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
MUN["cod"] = MUN.codarea.astype(str)
RP = MUN.geometry.representative_point()
PONTO = {c: (round(p.y, 4), round(p.x, 4)) for c, p in zip(MUN.cod, RP)}
UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}

# leste (motor._leste_costeiro)
terra = gpd.read_file("zip://" + str(DADOS / "referencia" / "ne_50m_land.zip"))
costa = terra.boundary.union_all().intersection(box(-41.0, -18.6, -34.6, -5.1))
LESTE = set(MUN.cod[MUN.geometry.distance(costa) <= 0.2])

# ---------------------------------------------------------------- situação das culturas (gaez_zarc + plurianual do CE)
GZT = pd.read_csv(DADOS / "gaez_zarc" / "nordeste_2026-2027.csv", dtype={"geocodigo": str})
PLUR = pd.read_csv(DADOS / "complementares" / "zarc_plurianual_ce" / "tabua_plurianual_ce.csv", sep=";", dtype={"geocodigo": str})
DEC = [f"dec{i}" for i in range(1, 37)]


def situacoes(cod, uf, g):
    """{cultura: (situacao, tem_zarc, ciclo_conferido, risco30)} como em motor.cardapio, só para as culturas do plano."""
    out = {}
    for nome, z in ZARC_NOME.items():
        r = g[g.ZARC == z]
        if not len(r):
            continue
        r = r.iloc[0]
        tem = bool(r.zarc_no_municipio)
        out[nome] = (r.situacao, tem, bool(r.ciclos_conferidos), r["risco ≤ 30%"])
    for nome, gz in GAEZ_SEM_ZARC.items():
        if uf == "CE":
            q = PLUR[(PLUR.geocodigo == cod) & (PLUR.Nome_cultura == PLUR_NOME[nome])]
            if len(q):
                n20 = (q[DEC] == 20).any().any()
                n40 = q[DEC].isin([20, 30, 40]).any().any()
                out[nome] = ("indicada" if n20 else "com risco" if n40 else "fora", True, True, None)
                continue
        r = g[(g.GAEZ == gz) & (g.ZARC == "sem ZARC na tábua")]
        si = r["SI baixo"].iloc[0] if len(r) else None
        out[nome] = ("só aptidão" if si is not None and si == si and si > APTA else "fora", False, True, None)
    return out


def culturas_plano(sit):
    """Culturas anuais do plano padrão (motor.plano): leguminosa, mandioca, forragem e o cereal do baixio."""
    ok = {c for c, v in sit.items() if v[0] in ("indicada", "só aptidão")}
    leg = next((c for c in ["Feijão-caupi", "Feijão comum", "Amendoim"] if c in ok), None)
    tampao = "Mandioca" if "Mandioca" in ok else None
    forr = next((c for c in ["Sorgo forrageiro", "Milheto"] if c in ok), None)
    milho = sit.get("Milho", ("fora", False, True, None))
    milho_ok = "Milho" in ok
    milho_30 = milho[0] == "com risco" and milho[3] not in (None, "—", "nenhum")
    cereal = "Milho" if milho_ok else ("Sorgo granífero" if "Sorgo granífero" in ok else None)
    baixio = "Milho" if (milho_ok or milho_30) else cereal
    return [c for c in dict.fromkeys([leg, tampao, forr, baixio]) if c]


# ---------------------------------------------------------------- El Niño no município (motor._perspectiva_municipal)
EVT = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
FORTES = set(EVT[EVT.ONI_OND_NDJ >= 1.5].quadra_afetada.astype(int))
ONS = pd.read_csv(DADOS / "analogos_aprofundado" / "onset_ne_mun.csv", dtype={"cod": str})
PERSP = {}
for cod, g in ONS[ONS.ano <= 2025].dropna(subset=["chuva_estacao_mm"]).groupby("cod"):
    s = g.set_index("ano").chuva_estacao_mm
    if len(s) < 15:
        continue
    med = s[~s.index.isin(FORTES)].median()
    PERSP[cod] = [round(100 * s[a] / med) for a in sorted(FORTES) if a in s.index]
REG = pd.read_csv(DADOS / "analogos_aprofundado" / "regime_chuva_ne_mun.csv", dtype={"cod": str}).set_index("cod")

# ---------------------------------------------------------------- SMAP (motor.smap_agora, sobre o mesmo cache de 30 dias)
SM = xr.open_dataset(DADOS / "prototipo" / "smap_janela_30d.nc").load()
FIM_SM = int(str(SM.attrs["fim"])[:4])


def smap_sem_dado(lat, lon):
    if not (float(SM.lat.min()) - 0.1 <= lat <= float(SM.lat.max()) + 0.1 and float(SM.lon.min()) - 0.1 <= lon <= float(SM.lon.max()) + 0.1):
        return True
    v = SM.rz.sel(lat=lat, lon=lon, method="nearest").to_series().dropna()
    return len(v) < 5 or int(v.index.max()) != FIM_SM


# ---------------------------------------------------------------- análogos (motor.analogos: w do lugar de estudo mais parecido)
VARS = ["chuva_anual_mm", "sazonalidade_walsh", "meses_umidos", "aridez_P_ET0", "tmax_estacao_umida", "tmax_mes_mais_quente"]
A = pd.read_csv(DADOS / "analogos_artigos" / "assinaturas.csv")
SIT = A[A.grupo != "Ceará (alvo)"].reset_index(drop=True)
MU, SD = A[VARS].mean(), A[VARS].std()
ZS = ((SIT[VARS] - MU) / SD).values
MUNA = pd.read_csv(DADOS / "analogos_aprofundado" / "ne_mun_assinaturas.csv", dtype={"cod": str}).set_index("cod")


def w_melhor(cod):
    if cod not in MUNA.index or pd.isna(MUNA.loc[cod, "chuva_anual_mm"]):
        return None
    z = ((MUNA.loc[cod, VARS].astype(float) - MU) / SD).values
    d = np.sqrt(((ZS - z) ** 2).sum(1))
    return round(float(np.exp(-d.min() ** 2 / 2)), 2)


# ---------------------------------------------------------------- financeiro (dados/financeiro_mun.json)
FIN = json.loads((RAIZ / "dados" / "financeiro_mun.json").read_text(encoding="utf-8"))

saida = {"_sobre": {
    "gerado": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
    "script": "ferramentas/preparar_confianca.py",
    "nivel": "soma dos pesos dos motivos: 0–1 alta, 2–3 média, 4 ou mais baixa",
    "plano": "critérios 'estimada' e 'ciclo' sobre o plano padrão (sem respostas); o módulo refina 'estimada' com a agenda da API",
}, "_textos": {k: {"texto": t, "tecnico": tec, "peso": p} for k, (t, tec, p) in TEXTOS.items()}}
cont, niveis, detalhe = Counter(), Counter(), {}
for cod, g in GZT.groupby("geocodigo"):
    uf = UF[cod[:2]]
    m = []
    if cod in LESTE:
        m.append("leste")
    f = FIN.get(cod) or {}
    cult = f.get("culturas") or {}
    if any(cult.get(s) and (cult[s].get("rend_mediano_kg_ha") or 0) > 2 * CONAB_FAMILIAR_KG_HA[s] for s in CONAB_FAMILIAR_KG_HA):
        m.append("agro")
    if not f or not cult.get("Milho") or not cult.get("Feijão"):
        m.append("pam_curta")
    sit = situacoes(cod, uf, g)
    plano = culturas_plano(sit)
    if "Mandioca" in plano:
        if not cult.get("Mandioca"):
            m.append("mandioca_sem_serie")
        elif (cult["Mandioca"].get("repete_ano_anterior_pct") or 0) >= 30:
            m.append("mandioca_repete")
    est = [c for c in plano if not sit[c][1]]
    if est:
        m.append("estimada")
    ciclo = [c for c in plano if sit[c][1] and not sit[c][2]]
    if ciclo:
        m.append("ciclo")
    p = PERSP.get(cod) or []
    if p and min(p) <= 75 and max(p) >= 100:
        m.append("el_nino")
    lat, lon = PONTO[cod]
    if smap_sem_dado(lat, lon):
        m.append("smap")
    if cod in REG.index and int(REG.loc[cod, "mes_inicio_estacao"]) > 2:
        m.append("portoes")
    w = w_melhor(cod)
    if w is not None and w < 0.3:
        m.append("analogos")
    m.sort(key=lambda k: (-TEXTOS[k][2], ORDEM.index(k)))
    nivel = NIVEL(sum(TEXTOS[k][2] for k in m))
    saida[cod] = {"nivel": nivel, "motivos": m}
    cont.update(m)
    niveis[nivel] += 1
    detalhe[cod] = (plano, est, ciclo, p, w)

texto = json.dumps(saida, ensure_ascii=False, separators=(",", ":"))
SAIDA.write_text(texto, encoding="utf-8")
print(f"{SAIDA}: {len(saida) - 2} municípios, {len(texto.encode('utf-8')) / 1024:.0f} KB")
print("níveis:", dict(niveis))
print("motivos:", dict(cont.most_common()))
for uf in ["CE", "BA", "PE", "AL", "MA"]:
    c = Counter(v["nivel"] for k, v in saida.items() if k[:2] in [x for x, u in UF.items() if u == uf])
    print(" ", uf, dict(c))
for cod in ["2311306", "2700300", "2903201"]:
    print(cod, saida[cod], detalhe[cod])
