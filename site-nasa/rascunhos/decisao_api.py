"""Rota /api/decisao (gaveta de decisao de plantio), guardada fora do app em 14/11/2026.

Nao estava ligada a nenhuma pagina. Problemas encontrados antes de reaproveitar:
- _carregar_municipios indexa o topo de municipios_ne.json ("campos", "m"...), entao todo codigo IBGE da 404;
- float(m[8]) quebra em municipio sem rho; estrelas e riscos por cultura sao regra fixa, nao dado;
- a regra "1a chuva >= 20 mm em 3 dias" e a pratica atual que agronomo_regras_semeadura.py critica.
Precisa de: import csv, json, os; from functools import lru_cache; from flask import jsonify, request; app.
"""

# ── Dados estáticos ────────────────────────────────────────────────────────
_DIR_ANALISES = os.path.join(
    os.path.dirname(__file__),
    "..", "conselho", "analises",
)
_CSV_MILHO = os.path.join(_DIR_ANALISES, "cetico_prereg_2026_milho_ndvi_a.csv")
_CSV_FEIJAO = os.path.join(_DIR_ANALISES, "cetico_prereg_2026_feijao_ndvi_a.csv")
_JSON_MUNICIPIOS = os.path.join(
    os.path.dirname(__file__),
    "static", "data", "municipios_ne.json",
)

_MESES = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}


@lru_cache(maxsize=1)
def _carregar_previsao() -> dict:
    """Lê os CSVs de previsão e retorna {cod: {milho: {prev, ndvi_a}, feijao: {prev, ndvi_a}}}."""
    dados: dict = {}

    for cultura, caminho in (("milho", _CSV_MILHO), ("feijao", _CSV_FEIJAO)):
        try:
            with open(caminho, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    cod = row["cod"].strip()
                    if cod not in dados:
                        dados[cod] = {}
                    dados[cod][cultura] = {
                        "prev": float(row["prev"]),
                        "ndvi_a": float(row["ndvi_a"]),
                    }
        except FileNotFoundError:
            pass  # Se faltar CSV, retorna disponivel=false para aquela cultura

    return dados


@lru_cache(maxsize=1)
def _carregar_municipios() -> dict:
    """Carrega municipios_ne.json e indexa por código IBGE (string de 7 dígitos)."""
    with open(_JSON_MUNICIPIOS, encoding="utf-8") as f:
        raw = json.load(f)
    # raw pode ser dict {ibge: [...]} ou list de listas
    if isinstance(raw, dict):
        return {str(k): v for k, v in raw.items()}
    # lista de listas onde o próprio índice IBGE não é a chave — tentar por campo embutido
    return {str(item[0]) if isinstance(item, (list, tuple)) else str(item): item for item in raw}


def _nivel_alerta(analogos_secos: int, solo_pctl: float) -> str:
    if analogos_secos >= 3 and solo_pctl < 25:
        return "alto"
    if analogos_secos >= 2 or solo_pctl < 40:
        return "medio"
    return "favoravel"


def _info_alerta(nivel: str) -> dict:
    if nivel == "alto":
        return {
            "nivel": "alto",
            "titulo": "Alto risco climático — plantio com cautela",
            "motivo": "El Niño ativo com solo seco; risco elevado de seca severa",
        }
    if nivel == "medio":
        return {
            "nivel": "medio",
            "titulo": "Risco moderado — atenção ao calendário",
            "motivo": "Possível déficit hídrico; monitore as chuvas antes de plantar",
        }
    return {
        "nivel": "favoravel",
        "titulo": "Condições favoráveis ao plantio",
        "motivo": "Sem El Niño ativo e solo em condições normais",
    }


def _culturas(nivel: str) -> list:
    if nivel == "alto":
        risco_milho = risco_feijao = risco_caupi = "alto"
        risco_palma = "baixo"
    elif nivel == "medio":
        risco_milho = "medio"
        risco_feijao = "medio"
        risco_caupi = "baixo"
        risco_palma = "baixo"
    else:
        risco_milho = risco_feijao = risco_caupi = risco_palma = "baixo"

    _estrelas = {"baixo": 4, "medio": 3, "alto": 2}
    return [
        {
            "nome": "Feijão-caupi",
            "emoji": "🫘",
            "risco": risco_caupi,
            "estrelas": _estrelas[risco_caupi],
            "nota": "Mais resistente à seca que o feijão comum",
        },
        {
            "nome": "Milho",
            "emoji": "🌽",
            "risco": risco_milho,
            "estrelas": _estrelas[risco_milho],
            "nota": "Sensível a veranicos em fevereiro-abril",
        },
        {
            "nome": "Palma forrageira",
            "emoji": "🌵",
            "risco": risco_palma,
            "estrelas": _estrelas[risco_palma],
            "nota": "Excelente para anos secos, colheita longa",
        },
        {
            "nome": "Feijão comum",
            "emoji": "🫘",
            "risco": risco_feijao,
            "estrelas": _estrelas[risco_feijao],
            "nota": "Ciclo curto, bom em anos normais",
        },
    ]


@app.get("/api/decisao")
def decisao():
    ibge = (request.args.get("ibge") or "").strip()
    if not ibge:
        return jsonify(erro="Informe o parâmetro ibge."), 400

    # Carregar dados do município
    municipios = _carregar_municipios()
    m = municipios.get(ibge)
    if m is None:
        return jsonify(erro=f"Município IBGE {ibge!r} não encontrado."), 404

    # Índices do JSON: 0=nome, 1=uf, 2=lat, 3=lon, 4=ini_mes, 5=normal_mm,
    #                  6=clima_mm[12], 7=analogos[[pct,seco]x4],
    #                  8=rho_milho, 9=milho_pct_100mm, 10=solo_pctl, 11=solo_n
    nome       = m[0]
    uf         = m[1]
    ini_mes    = int(m[4])
    normal_mm  = float(m[5])
    analogos   = m[7]        # lista de [pct, seco]
    rho_milho  = float(m[8])
    milho_p100 = float(m[9])
    solo_pctl  = float(m[10])
    solo_n     = int(m[11])

    analogos_secos = sum(1 for a in analogos if a[1])
    analogos_total = len(analogos)

    # Alerta
    nivel = _nivel_alerta(analogos_secos, solo_pctl)
    alerta = _info_alerta(nivel)

    # Previsão dos CSVs
    previsao_csv = _carregar_previsao()
    prev_mun = previsao_csv.get(ibge, {})

    def _prev_cultura(cultura: str, lo: float, hi: float) -> dict:
        if cultura not in prev_mun:
            return {"pct": None, "lo": round(lo * 100, 1), "hi": round(hi * 100, 1),
                    "r": None, "disponivel": False}
        p = prev_mun[cultura]
        return {
            "pct": round(p["prev"] * 100, 1),
            "lo": round(lo * 100, 1),
            "hi": round(hi * 100, 1),
            "r": round(p["ndvi_a"], 2),
            "disponivel": True,
        }

    previsao = {
        "milho":  _prev_cultura("milho",  -0.39, 0.47),
        "feijao": _prev_cultura("feijao", -0.38, 0.38),
    }

    resposta = {
        "municipio": nome,
        "estado": uf,
        "ibge": ibge,
        "alerta": alerta,
        "previsao": previsao,
        "calendario": {
            "ini_mes": ini_mes,
            "ini_nome": _MESES.get(ini_mes, str(ini_mes)),
            "regra": "Plante após a 1ª chuva ≥ 20 mm em 3 dias consecutivos",
        },
        "clima": {
            "normal_mm": normal_mm,
            "solo_pctl": solo_pctl,
            "solo_n": solo_n,
            "analogos_secos": analogos_secos,
            "analogos_total": analogos_total,
            "rho_milho": rho_milho,
            "milho_pct_100mm": milho_p100,
        },
        "culturas": _culturas(nivel),
        "fonte": "MODIS MOD13Q1 2026 · NASA IMERG · NASA SMAP · IBGE PAM 2000–2025",
    }
    return jsonify(resposta)


