"""Motor do protótipo QUADRA (Nordeste): dado um ponto (lat, lon), junta o que os dados dizem sobre o que plantar,
quando e em que ordem.

Camadas (ver proposta/estrutura_gaez_zarc.md e protótipo/REVISAO_10_AGENTES.md):
- O que cabe: FAO GAEZ v4 (aptidão 0–100, sequeiro, insumo baixo; classes oficiais da v4; corte "apta" > 40), no mundo.
- Quando e com que risco: ZARC/MAPA 2026/27 nos 1.794 municípios do Nordeste. Regra decidida em 14/11, no nível do
  município: se a cultura tem ZARC aqui, o ZARC decide e o GAEZ vira rótulo; senão, o GAEZ decide.
- Clima e análogos: assinatura climática do NASA POWER (climatologia + Tmax/Tmin médias diárias 2001–2024) contra os
  lugares dos artigos; peso de transferência w = exp(−d²/2).
- Rotação: catálogo de 147 cartões; número só para cartões T0/T1 (os demais dão só a direção).
- Este ano: ONI (NOAA); perspectiva da estação no próprio município (IMERG, El Niños fortes da série); solo agora (SMAP L4).
"""
import json
import math
import os
import re
import sys
import threading
from pathlib import Path

import numpy as np
import pandas as pd

PROJ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJ / "scripts"))
import analogos_climaticos_artigos as AC  # noqa: E402  (assinatura climática pela API do POWER)
import gaez_zarc_municipio as GZ  # noqa: E402  (amostragem do GAEZ, janelas e regra de situação)
from comum import DADOS  # noqa: E402

VARS = ["chuva_anual_mm", "sazonalidade_walsh", "meses_umidos", "aridez_P_ET0", "tmax_estacao_umida", "tmax_mes_mais_quente"]
SAFRA = "2026-2027"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
CACHE = DADOS / "prototipo"
CACHE.mkdir(exist_ok=True)
D_APR = DADOS / "analogos_aprofundado"
FONTES = {  # data e período de cada base (revisão M29)
    "POWER": "NASA POWER: climatologia (chuva, umidade, vento, radiação) + Tmax/Tmin médias diárias 2001–2024",
    "GAEZ": "FAO/IIASA GAEZ v4: clima 1981–2010, grade de 5'",
    "ZARC": "MAPA ZARC 2026/27 (tábua aberta; uma portaria por cultura e estado)",
    "IMERG": "GPM IMERG V07 diário via NASA POWER, 1998–14/09/2026 (Final até set/2025; depois, Late, preliminar)",
    "SMAP": "NASA SMAP L4 (SPL4SMGP v008), 31/03/2015–10/11/2026",
    "ONI": "NOAA/CPC ONI, 1950–ASO 2026",
}

# cardápio do MVP (proposta/estrutura_gaez_zarc.md, seção 5.1): nome, grupo, camada GAEZ, cultura no ZARC, papel
CARDAPIO = [
    ("Feijão-caupi", "alimento", "feijão-caupi", "Feijão Caupi", "leguminosa principal"),
    ("Milho", "alimento", "milho", "Milho 1ª Safra", "cereal principal"),
    ("Feijão comum", "alimento", "feijão (Phaseolus)", "Feijão 2ª Safra", "leguminosa"),
    ("Mandioca", "alimento", "mandioca", None, "tampão do ano seco"),
    ("Amendoim", "alimento", "amendoim", "Amendoim", "leguminosa (nematoide: só com diagnóstico de solo)"),
    ("Sorgo granífero", "alimento", "sorgo", "Sorgo Granífero", "cereal tolerante à seca"),
    ("Guandu", "alimento", "guandu", None, "leguminosa de ciclo longo (faixa perene)"),
    ("Sorgo forrageiro", "forragem", "sorgo", "Sorgo Forrageiro", "forragem"),
    ("Milheto", "forragem", "milheto", None, "forragem e cobertura"),
    ("Palma forrageira", "forragem", None, None, "forragem perene"),
    ("Gliricídia", "forragem", None, None, "banco de proteína em faixa"),
    ("Mucuna-preta", "forragem", None, None, "cobertura semeada no milho"),
    ("Algodão herbáceo", "renda", "algodão", "Algodão Herbáceo", "renda; só com vazio do bicudo"),
    ("Mamona", "renda", None, "Mamona", "renda"),
    ("Girassol", "renda", "girassol", "Girassol", "renda"),
]
ZARC_MENU = [c[3] for c in CARDAPIO if c[3]]
TIPO_ROT = {"Feijão-caupi": "leguminosa", "Feijão comum": "leguminosa", "Amendoim": "leguminosa", "Guandu": "perene",
            "Mucuna-preta": "leguminosa", "Milho": "cereal", "Sorgo granífero": "cereal", "Sorgo forrageiro": "forragem",
            "Milheto": "forragem", "Palma forrageira": "perene", "Gliricídia": "perene", "Mandioca": "tampão",
            "Algodão herbáceo": "renda", "Mamona": "renda", "Girassol": "renda"}
SO_LITERATURA = {"Palma forrageira": "Diniz 2017; Lima 2018a", "Gliricídia": "Martins 2015; Pérez-Marin 2006",
                 "Mucuna-preta": "Melo 2013"}
# no CE, estas culturas têm ZARC em portaria plurianual que não está na tábua aberta (revisão A1/C5; vigência a conferir)
PLURIANUAL_CE = {"Mandioca": "Port. 11/2020", "Milheto": "Port. 330/2020", "Palma forrageira": "Port. 284/2019"}
# cartões fixos: cartão -> como o motor usa; mostrar_efeito=False quando o número do cartão não é o que a regra diz (C4)
REGRAS = {
    "ne_lg_cereal_sequeiro_quente": ("+24% no ano colhido, contra cereal solteiro, em sequeiro quente-seco com pouco N "
                                     "(síntese do conselho; faixa +2% a +49%).", True),
    "ne_s0_para_rotacao_tempo": ("Não medido: trocar o consórcio milho + feijão de hoje por rotação no tempo é o ensaio que falta "
                                 "(sensibilidade 0 a +9%).", False),
    "mudare_pousio_milho": ("Quebra sem leguminosa: a opção do interruptor em ano seco (só direção).", True),
    "mudare22_milho_caupi": ("Consórcio rende mais terra (LER > 1), não mais água; em sequeiro o LER não foi medido.", True),
    "melo_relay_mucuna": ("A única cobertura que cabe no sequeiro: semeada no milho em pé, ~85 dias depois. Sem bônus de grão "
                          "(diferença não significativa).", False),
    "luz_crotalaria_fp_60d_milho": ("Regra negativa: no balde do QUADRA (simulação, grau C), 60 dias de cobertura antes do milho "
                                    "levam a chance de sucesso de 0,92 a 0,49 no CE; o ensaio de da Luz foi irrigado.", False),
    "pacheco13_milheto_pos_colheita_falha": ("Regra negativa: não semear cobertura depois da colheita (falhou sem chuva).", False),
    "mudare_neg_sorgo_para_milho_sorgo": ("Alerta, não veto: trocar sorgo contínuo por milho-sorgo piorou a sequência (n = 10).", True),
    "zhao_leg_algodao_nulo": ("O algodão não ganha nitrogênio da leguminosa; o que vale é o vazio contra o bicudo.", True),
    "hospedeiro_bicudo_adulto": ("Perto do algodão: caupi ou crotalária, nunca sorgo.", True),
    "martins_gliricidia_forrageira": ("Gliricídia junto da palma ou do buffel, longe do grão.", True),
}

# ---------------------------------------------------------------- dados carregados uma vez
A = pd.read_csv(DADOS / "analogos_artigos" / "assinaturas.csv")
SIT = A[A.grupo != "Ceará (alvo)"].reset_index(drop=True)
MU, SD = A[VARS].mean(), A[VARS].std()
LA = pd.read_csv(D_APR / "catalogo_lugares_assinaturas.csv")
LUG = pd.read_csv(D_APR / "catalogo_cartao_lugar.csv").set_index("id").lugar
CAT = json.loads((PROJ / "pesquisa" / "catalogo_rotacoes.json").read_text(encoding="utf-8"))
CARDS = {c["id"]: c for c in CAT["configuracoes"]}
MUNA = pd.read_csv(D_APR / "ne_mun_assinaturas.csv", dtype={"cod": str}).set_index("cod")
GZT = pd.read_csv(DADOS / "gaez_zarc" / f"nordeste_{SAFRA}.csv", dtype={"geocodigo": str})
ONS = pd.read_csv(D_APR / "onset_ne_mun.csv", dtype={"cod": str}, parse_dates=["inicio_chuva"])
REG = pd.read_csv(D_APR / "regime_chuva_ne_mun.csv", dtype={"cod": str}).set_index("cod")
EN = json.loads((DADOS / "el_nino_2026" / "resumo.json").read_text(encoding="utf-8"))
ATUAL = pd.read_csv(DADOS / "el_nino_2026" / "estado_atual_uf.csv").set_index("UF")
EVT = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
FORTES = set(EVT[EVT.ONI_OND_NDJ >= 1.5].quadra_afetada.astype(int))


def _municipios():
    import geopandas as gpd
    g = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
    g["cod"] = g.codarea.astype(str)
    loc = {str(m["id"]): m for m in json.loads((DADOS / "ibge_nordeste" / "localidades_municipios_ne.json").read_text(encoding="utf-8"))}
    g["municipio"] = g.cod.map(lambda c: loc[c]["nome"])
    g["uf"] = g.cod.str[:2].map(UF)
    g["mesorregiao"] = g.cod.map(lambda c: loc[c]["microrregiao"]["mesorregiao"]["nome"])
    return g


MUN = _municipios()
_SINDEX = MUN.sindex


def _leste_costeiro():
    """Municípios a até ~20 km (0,2°) da costa leste, do RN ao sul de Calcanhar até o sul da BA. É onde o IMERG capta só
    39–72% da chuva medida (viabilidade dos artigos, bloco B2: costa leste < 20 km); a costa norte não tem esse viés."""
    import geopandas as gpd
    from shapely.geometry import box
    terra = gpd.read_file("zip://" + str(DADOS / "referencia" / "ne_50m_land.zip"))
    costa = terra.boundary.union_all().intersection(box(-41.0, -18.6, -34.6, -5.1))
    return set(MUN.cod[MUN.geometry.distance(costa) <= 0.2])


LESTE = _leste_costeiro()


SOLOS = {1: "arenoso", 2: "textura média", 3: "argiloso", 11: "AD1", 12: "AD2", 13: "AD3", 14: "AD4", 15: "AD5", 16: "AD6"}


def _zarc_cardapio():
    """Tábua do ZARC do NE só com o que o cardápio usa: sequeiro, culturas do cardápio, ciclos com cultivar (quando
    conferidos) e a mamona tradicional. Indexada pelo código do município, para a janela por solo (revisão A7)."""
    cols = ["geocodigo", "UF", "Nome_cultura", "Nome_Outros_Manejos", "Nome_Clima", "Cod_Ciclo", "Cod_Solo"] + GZ.D
    Z = pd.read_csv(DADOS / "complementares" / "zarc_ne" / f"tabua_risco_ne_{SAFRA}.csv", sep=";", usecols=cols)
    Z = Z[(Z.Nome_Outros_Manejos == "Sequeiro") & Z.Nome_cultura.isin(ZARC_MENU)]
    manter = pd.Series(True, index=Z.index)
    for (uf, cult), ciclos in GZ.CICLOS_COM_CULTIVAR.items():
        sel = (Z.UF == uf) & (Z.Nome_cultura == cult)
        manter &= ~sel | Z.Cod_Ciclo.isin(ciclos)
    for cult, clima in GZ.CLIMA_POR_CULTURA.items():
        manter &= (Z.Nome_cultura != cult) | (Z.Nome_Clima == clima)
    Z = Z[manter].copy()
    Z["geocodigo"] = Z.geocodigo.astype(str)
    return Z.set_index("geocodigo").sort_index()


ZSEQ = _zarc_cardapio()

# ZARC plurianual do CE (fora da tábua aberta): mandioca Port. 11/2020, milheto Port. 330/2020, palma Port. 284/2019.
# Vigentes pela página "Safra vigente — Ceará" do MAPA (05/11/2026); SISZARC não conferido (scripts/zarc_plurianual_ce.py).
PLUR = pd.read_csv(DADOS / "complementares" / "zarc_plurianual_ce" / "tabua_plurianual_ce.csv", sep=";")
PLUR["geocodigo"] = PLUR.geocodigo.astype(str)
PLUR_NOME = {"Mandioca": "Mandioca", "Milheto": "Milheto", "Palma forrageira": "Palma Forrageira"}


def janelas_circ(decs):
    """Como GZ.janelas, mas junta o trecho que atravessa a virada do ano (ex.: palma de dez a mar)."""
    decs = sorted(set(decs))
    if not decs:
        return "nenhum"
    if 1 in decs and 36 in decs and len(decs) < 36:
        corte = next(k for k in range(36, 0, -1) if k not in decs)  # último decêndio fora: a janela começa depois dele
        ordem = [((corte + i) % 36) + 1 for i in range(36)]
        seq = [d for d in ordem if d in decs]
        trechos, ini, ant = [], seq[0], seq[0]
        for d in seq[1:] + [None]:
            if d != (ant % 36) + 1:
                trechos.append(f"{GZ.data_dec(ini)}–{GZ.data_dec_fim(ant)}")
                ini = d
            ant = d if d else ant
        return "; ".join(trechos)
    return GZ.janelas(decs)


def zarc_plurianual(cod, nome):
    """Janela e situação de mandioca, milheto ou palma no CE pela portaria plurianual (mesma regra do ZARC)."""
    if nome not in PLUR_NOME:
        return None
    q = PLUR[(PLUR.geocodigo == cod) & (PLUR.Nome_cultura == PLUR_NOME[nome])]
    if not len(q):
        return None
    d = lambda vals, g=q: [i + 1 for i, c in enumerate(GZ.D) if g[c].isin(vals).any()]  # noqa: E731
    n20 = d([20])
    por_solo = [{"cod_solo": int(s), "solo": SOLOS.get(int(s), str(s)), "risco20": janelas_circ(d([20], g)),
                 "risco30": janelas_circ(d([20, 30], g)), "risco40": janelas_circ(d([20, 30, 40], g))} for s, g in q.groupby("Cod_Solo")]
    return {"risco20": janelas_circ(n20), "risco30": janelas_circ(d([20, 30])), "risco40": janelas_circ(d([20, 30, 40])),
            "solo_ciclo": f"{int((q[GZ.D] == 20).any(axis=1).sum())} de {len(q)}", "por_solo": por_solo,
            "situacao": "indicada" if n20 else ("com risco" if d([20, 30, 40]) else "fora"),
            "portaria": q.Portaria.iloc[0].replace("Port.", "Port. ").replace("_de_", " de ").replace("-", "/")}


def janelas_por_solo(cod, cultura_zarc):
    """Para uma cultura do ZARC no município: a janela (risco 20%, ≤ 30%, ≤ 40%) em cada tipo de solo zoneado."""
    if cod not in ZSEQ.index:
        return []
    q = ZSEQ.loc[[cod]]
    q = q[q.Nome_cultura == cultura_zarc]
    out = []
    for solo, g in q.groupby("Cod_Solo"):
        r = lambda vals: [i + 1 for i, c in enumerate(GZ.D) if g[c].isin(vals).any()]  # noqa: E731
        out.append({"cod_solo": int(solo), "solo": SOLOS.get(int(solo), str(solo)), "risco20": GZ.janelas(r([20])),
                    "risco30": GZ.janelas(r([20, 30])), "risco40": GZ.janelas(r([20, 30, 40]))})
    return out


def _zarc_primeiras_datas():
    """Por município: o 1º decêndio da estação com alguma cultura do cardápio zoneada (risco até 40%) e o 1º com risco de
    20% (revisão A6). Só sequeiro e só os ciclos com cultivar, quando conferidos. A ordem começa 3 meses antes da estação."""
    Z = ZSEQ.reset_index()
    zoneado = (Z[GZ.D] > 0).groupby(Z.geocodigo).any()
    r20 = (Z[GZ.D] == 20).groupby(Z.geocodigo).any()
    out = {}
    for cod in zoneado.index:
        m0 = int(REG.mes_inicio_estacao.get(str(cod), 2))
        ini = ((m0 - 4) % 12) * 3  # índice do 1º decêndio do mês 3 meses antes da estação
        ordem = [(ini + k) % 36 for k in range(36)]
        z = zoneado.loc[cod].values
        v = r20.loc[cod].values
        p40 = next((k + 1 for k in ordem if z[k]), None)
        p20 = next((k + 1 for k in ordem if v[k]), None)
        out[str(cod)] = {"ate40": GZ.data_dec(p40) if p40 else None, "risco20": GZ.data_dec(p20) if p20 else None}
    return out


ZPRIM = _zarc_primeiras_datas()


def _perspectiva_municipal():
    """El Niño no próprio município: chuva da estação (IMERG) nos El Niños fortes da série contra os demais anos."""
    out = {}
    o = ONS[ONS.ano <= 2025].dropna(subset=["chuva_estacao_mm"])  # a estação de 2026 é IMERG Late (preliminar) e fica fora
    for cod, g in o.groupby("cod"):
        s = g.set_index("ano").chuva_estacao_mm
        if len(s) < 15:
            continue
        t1, med = s.quantile(1 / 3), s[~s.index.isin(FORTES)].median()
        anos = [int(a) for a in sorted(FORTES) if a in s.index]
        out[cod] = {"anos": anos, "inferior": int(sum(s[a] <= t1 for a in anos)),
                    "pct": [int(round(100 * s[a] / med)) for a in anos], "n_anos": int(len(s))}
    return out


PERSP_MUN = _perspectiva_municipal()

# ---------------------------------------------------------------- caches com trava e gravação atômica (revisão C1)
_TRAVA = threading.Lock()
_CACHES = {}


def _cache(nome):
    with _TRAVA:
        if nome not in _CACHES:
            p = CACHE / nome
            try:
                _CACHES[nome] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
            except json.JSONDecodeError:
                _CACHES[nome] = {}
        return _CACHES[nome]


def _grava_cache(nome, chave, valor):
    with _TRAVA:
        _CACHES[nome][chave] = valor
        p = CACHE / nome
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(_CACHES[nome], ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, p)


# ---------------------------------------------------------------- SMAP (solo agora)
_SMAP = {}


def _prepara_smap():
    """Umidade da zona da raiz (SMAP L4) nos 30 dias até a última data, em cada ano de 2015 a 2026 (para o ranking)."""
    import xarray as xr
    fonte = DADOS / "smap" / "smap_l4_diario_ne.nc"
    arq = CACHE / "smap_janela_30d.nc"
    assinatura_fonte = f"{fonte.stat().st_mtime_ns}:{fonte.stat().st_size}"  # revisão M27
    ds = xr.open_dataset(fonte)
    fim = pd.Timestamp(ds.time.values.max())
    if arq.exists():
        try:
            c = xr.open_dataset(arq).load()
            c.close()
            if str(c.attrs.get("fim")) == str(fim.date()) and c.attrs.get("fonte") == assinatura_fonte:
                _SMAP.update(ds=c, fim=fim)
                return
        except (OSError, ValueError):  # cache vazio ou corrompido: recalcula
            pass
    anos = []
    for ano in range(2015, fim.year + 1):
        f = fim - pd.DateOffset(years=fim.year - ano)  # 29/02 vira 28/02 sem erro (revisão M26)
        anos.append(ds.sm_rootzone.sel(time=slice(f - pd.Timedelta(days=29), f)).mean("time").expand_dims(ano=[ano]))
    c = xr.concat(anos, "ano").to_dataset(name="rz").load()
    c.attrs.update(fim=str(fim.date()), fonte=assinatura_fonte)
    tmp = arq.with_name(arq.stem + "_tmp.nc")
    c.to_netcdf(tmp)  # gravação atômica: um processo que cai no meio não deixa arquivo vazio
    os.replace(tmp, arq)
    _SMAP.update(ds=c, fim=fim)


_T_SMAP = threading.Thread(target=_prepara_smap, daemon=True)
_T_SMAP.start()


# ---------------------------------------------------------------- utilidades
def data_doy(d):
    """Dia do ano contínuo (meses do ano anterior negativos) -> 'dd/mm'."""
    if d is None or np.isnan(d):
        return None
    base = pd.Timestamp(2026, 1, 1) + pd.Timedelta(days=int(round(d)) - 1)
    return f"{base.day:02d}/{base.month:02d}"


def _dia_estacao(s, m0):
    """Data -> dia contínuo da estação: dias antes de 1/jan ficam negativos quando a estação começa no fim do ano."""
    d = s.dt.dayofyear.astype(float)
    if m0 <= 2:
        return np.where(s.dt.month == 12, d - 365, d)
    if m0 >= 7:
        return np.where(s.dt.month >= 7, d - 365, d)
    return d


def _br(x, casas=2):
    return f"{x:+.{casas}f}".replace(".", ",")


# ---------------------------------------------------------------- camadas
def localizar(lat, lon):
    """Município do NE que contém o ponto; na costa e nas divisas, o mais próximo até ~2 km (revisão A5/M7)."""
    from shapely.geometry import Point
    p = Point(lon, lat)
    cand = MUN.iloc[list(_SINDEX.query(p))]
    m = cand[cand.contains(p)]
    out = {"lat": round(lat, 4), "lon": round(lon, 4), "uf": None}
    if not len(m):
        perto = MUN.iloc[list(_SINDEX.query(p.buffer(0.02)))]
        if len(perto):
            dist = perto.distance(p)
            m = perto.loc[[dist.idxmin()]] if dist.min() <= 0.02 else perto.iloc[0:0]
    if len(m):
        r = m.iloc[0]
        out.update(cod=r.cod, municipio=r.municipio, mesorregiao=r.mesorregiao, uf=r.uf)
    return out


def _chave_power(lat, lon):
    return f"{round(lat * 2) / 2:.1f},{round(lon / 0.625) * 0.625:.3f}"  # célula nativa do POWER (revisão M13)


def assinatura(lat, lon, cod=None):
    if cod and cod in MUNA.index and not pd.isna(MUNA.loc[cod, "chuva_anual_mm"]):
        r = MUNA.loc[cod]
        return {v: float(r[v]) for v in VARS + ["et0_anual_mm", "altitude_m"]}, "NASA POWER (clima do município: célula do ponto interno)"
    cache = _cache("cache_power_v2.json")
    chave = _chave_power(lat, lon)
    if chave not in cache:
        try:
            _grava_cache("cache_power_v2.json", chave, AC.assinatura(lat, lon))
        except Exception as e:  # API fora do ar ou limite de pedidos (429): a página segue sem os análogos
            return None, f"NASA POWER indisponível agora ({type(e).__name__}); tente de novo em alguns minutos"
    return cache[chave], "NASA POWER (API ao vivo, célula do ponto clicado)"


def aptidao(lat, lon):
    """Aptidão do GAEZ no pixel de 5' do ponto (chave = pixel, revisão A4)."""
    cache = _cache("cache_gaez_v2.json")
    chave = f"{math.floor((90 - lat) * 12)},{math.floor((lon + 180) * 12)}"
    if chave not in cache:
        si = GZ.aptidao([(lon, lat)])
        _grava_cache("cache_gaez_v2.json", chave, {f"{c}|{i}": v[0] for (c, i), v in si.items()})
    return {tuple(k.split("|")): v for k, v in cache[chave].items()}


def analogos(sig):
    z = (pd.Series(sig)[VARS] - MU) / SD
    d = np.sqrt((((SIT[VARS] - MU) / SD - z) ** 2).sum(1))
    S = SIT.assign(dist=d.values, w=np.exp(-d.values ** 2 / 2)).sort_values("dist")
    dl = np.sqrt((((LA[VARS] - MU) / SD - z) ** 2).sum(1))
    W = pd.Series(np.exp(-dl.values ** 2 / 2), index=LA.lugar.values)
    return S, W


def cardapio(loc, si):
    cod, uf = loc.get("cod"), loc.get("uf")
    zm = GZT[GZT.geocodigo == cod] if cod else GZT.iloc[0:0]
    linhas = []
    for nome, grupo, g, z, papel in CARDAPIO:
        s_baixo = si.get((g, "Low")) if g else None
        s_alto = si.get((g, "High")) if g else None
        item = {"cultura": nome, "grupo": grupo, "papel": papel, "aptidao": s_baixo, "aptidao_alta": s_alto,
                "classe": GZ.classe_gaez(s_baixo) if g else "sem camada", "risco20": None, "risco30": None, "risco40": None,
                "solo_ciclo": None, "situacao": None, "base": ""}
        r = zm[zm.ZARC == z].iloc[0] if (cod and z and (zm.ZARC == z).any()) else None
        if r is not None and bool(r.get("zarc_no_municipio", False)):
            item.update(risco20=r["risco 20%"], risco30=r["risco ≤ 30%"], risco40=r["risco ≤ 40%"], solo_ciclo=r["solo×ciclo com 20%"],
                        por_solo=janelas_por_solo(cod, z),
                        situacao=r.situacao, base=f"ZARC {SAFRA} ({uf})" + (" + GAEZ" if g else "")
                        + ("" if r.get("ciclos_conferidos", False) else "; grupos de ciclo sem conferência de cultivar"))
        elif uf == "CE" and zarc_plurianual(cod, nome):
            p = zarc_plurianual(cod, nome)
            item.update(risco20=p["risco20"], risco30=p["risco30"], risco40=p["risco40"], solo_ciclo=p["solo_ciclo"],
                        por_solo=p["por_solo"], situacao=p["situacao"],
                        base=(f"ZARC plurianual do CE ({p['portaria']}; vigente pela página do MAPA de 05/11/2026; fora da tábua aberta)"
                              + (" + GAEZ" if g else "") + ("; grupos de ciclo I–III juntos" if nome == "Milheto" else "")))
        elif nome in SO_LITERATURA and not (uf == "CE" and nome in PLURIANUAL_CE):
            item.update(situacao="literatura", base=f"sem camada GAEZ/ZARC; {SO_LITERATURA[nome]} (grau C)")
        elif cod:  # no NE, sem ZARC neste município: o GAEZ decide
            plur = f"; este município não está na portaria plurianual do CE ({PLURIANUAL_CE[nome]})" if (uf == "CE" and nome in PLURIANUAL_CE) else ""
            if g:
                item.update(situacao="só aptidão" if (s_baixo or 0) > GZ.APTA else "fora", base=f"GAEZ (sem ZARC na tábua aqui){plur}")
            else:
                item.update(situacao="literatura" if nome in SO_LITERATURA else "fora", base=f"sem camada GAEZ{plur}")
        else:  # fora do NE: só o GAEZ, com pouco insumo; o insumo alto é só rótulo (revisão M2)
            if g and s_baixo is None and s_alto is None:
                item.update(situacao="sem dado", base="sem dado do GAEZ neste pixel")
            elif g:
                item.update(situacao="apta (GAEZ)" if (s_baixo or 0) > GZ.APTA else "pouco apta",
                            base="GAEZ; ZARC só no Brasil" + (f" (com insumo alto: {s_alto:.0f})" if s_alto and (s_baixo or 0) <= GZ.APTA and s_alto > GZ.APTA else ""))
            else:
                item.update(situacao="literatura" if nome in SO_LITERATURA else "sem dado", base="sem camada GAEZ; ZARC só no Brasil")
        linhas.append(item)
    return linhas


def regime(cod, uf=None, lon=None):
    if cod not in REG.index:
        return None
    r = REG.loc[cod]
    m0 = int(r.mes_inicio_estacao)
    quadra = m0 <= 2
    # no litoral leste (até ~20 km do mar) o IMERG capta só 0,39–0,72 da chuva medida (viabilidade, bloco B2)
    leste = cod in LESTE
    return {"mes_inicio": m0, "estacao": r.estacao, "chuva_mm": float(r.chuva_estacao_media_mm), "fracao": float(r.fracao_do_ano),
            "quadra": quadra,
            "texto": (f"Estação chuvosa típica: {r.estacao} ({r.chuva_estacao_media_mm:.0f} mm, {r.fracao_do_ano * 100:.0f}% do ano; IMERG)."
                      + ("" if quadra else " Não é a quadra do norte: os portões de 19/mar e 30/abr e as datas do plano foram "
                                            "calibrados no sertão do CE e precisam ser ajustados aqui.")
                      + (" Atenção: no litoral leste o IMERG subestima a chuva de outono e inverno (capta 39–72% do medido); "
                         "aqui, as janelas do ZARC são o guia das datas." if leste else ""))}


def inicio_estacao(cod):
    o = ONS[(ONS.cod == cod) & (ONS.ano <= 2025)]  # 2026 é IMERG Late (preliminar): fora das estatísticas
    if not len(o):
        return None
    m0 = int(o.mes_inicio_estacao.iloc[0])
    d = pd.Series(_dia_estacao(o.inicio_chuva, m0), index=o.index).where(o.inicio_chuva.notna())
    forte = o.ano.isin(FORTES)
    demais = d[~forte]
    anos = {int(a): (f"{x:%d/%m}" if pd.notna(x) else "sem início") for a, x in zip(o.ano[forte], o.inicio_chuva[forte])}
    dif = d[forte].median() - demais.median()
    return {"mediana": data_doy(demais.median()), "p10": data_doy(demais.quantile(0.1)), "p90": data_doy(demais.quantile(0.9)),
            "dif_el_nino_dias": None if np.isnan(dif) else int(round(dif)), "anos_el_nino_forte": anos,
            "sem_inicio_pct": round(float(o.inicio_chuva.isna().mean() * 100)),
            "n_anos": int(len(o)), "ultimo_preliminar": int(o.ano.max()) >= 2026}


def smap_agora(lat, lon):
    _T_SMAP.join(timeout=30)
    if "ds" not in _SMAP:
        return {"status": "carregando"}
    c = _SMAP["ds"]
    if not (float(c.lat.min()) - 0.1 <= lat <= float(c.lat.max()) + 0.1 and float(c.lon.min()) - 0.1 <= lon <= float(c.lon.max()) + 0.1):
        return {"status": "fora do recorte do protótipo (o SMAP é global; aqui só baixamos o Nordeste)"}
    v = c.rz.sel(lat=lat, lon=lon, method="nearest").to_series().dropna()
    if len(v) < 5 or v.index.max() != _SMAP["fim"].year:
        return {"status": "sem dado no pixel"}
    posto = int(v.rank(method="min")[v.index.max()])
    classe = "seco para a época" if posto <= 3 else "úmido para a época" if posto >= len(v) - 2 else "normal para a época"
    return {"status": "ok", "fim": str(_SMAP["fim"].date()), "valor": round(float(v.iloc[-1]), 3), "posto": posto, "anos": len(v),
            "classe": classe,
            "texto": (f"Solo (zona da raiz, SMAP L4) nos 30 dias até {_SMAP['fim']:%d/%m/%Y}: posição {posto} de {len(v)} anos "
                      f"(1 = o mais seco), {classe}. Fora da estação, isso não prevê a próxima (ρ +0,01 entre novembro e fevereiro no CE).")}


def _rotulo_oni(oni):
    if oni >= 2:
        return "El Niño muito forte"
    if oni >= 1.5:
        return "El Niño forte"
    if oni >= 1:
        return "El Niño moderado"
    if oni >= 0.5:
        return "El Niño fraco"
    if oni <= -1.5:
        return "La Niña forte"
    if oni <= -0.5:
        return "La Niña"
    return "neutro"


def _efeito(e):
    pct, un, c = e.get("pct"), e.get("unidade"), e.get("central")
    if pct and pct[0] is not None:
        return f"{pct[0]:+.0f}%" + (f" ({pct[1]:+.0f} a {pct[2]:+.0f})" if pct[1] is not None and pct[2] is not None else "")
    if c is None:
        return None
    if un == "LER":
        return f"LER {c:.2f}".replace(".", ",")
    if un in ("t/ha", "kg/ha", "Mg/ha"):
        return f"{c:+.2f} {un}".replace(".", ",")
    return None


def cartao(cid, w=None):
    """Cartão do catálogo. Número só para T0/T1; T2 = só direção; T3 = não transfere (revisão A8)."""
    c = CARDS[cid]
    e = c.get("efeito") or {}
    uso, mostrar = REGRAS.get(cid, (None, True))
    t = c["transferencia"]
    efeito = _efeito(e) if (mostrar and t in ("T0", "T1")) else None
    if efeito and e.get("variavel"):
        efeito += f" ({e['variavel']})"
    texto_onde = f"{c.get('onde', '')} {c.get('efeito_texto', '')}".lower()
    return {"id": cid, "tipo": c["tipo"], "configuracao": c["configuracao"], "grau": c["grau"], "transferencia": t,
            "rotulo_transferencia": {"T0": "medido no semiárido", "T1": "clima análogo", "T2": "só direção", "T3": "não transfere"}[t],
            "uso": uso if w is None else None, "efeito": efeito, "irrigado": "irrig" in texto_onde,
            "referencia": c.get("referencia_texto"), "doi": next((r for r in c.get("referencias") or [] if r.startswith("10.")), None),
            "lugar": LUG.get(cid) if isinstance(LUG.get(cid), str) else None, "w": None if w is None else round(float(w), 2)}


def plano(itens, nivel_alerta, reg, no_ne):
    """Plano por faixas 2027–2029 (proposta v3, seção 6.4), com textos que dependem das culturas que existem aqui."""
    ok = {i["cultura"] for i in itens if i["situacao"] in ("indicada", "só aptidão", "apta (GAEZ)")}
    sit = {i["cultura"]: i for i in itens}
    leg = next((c for c in ["Feijão-caupi", "Feijão comum", "Amendoim"] if c in ok), None)
    tampao = "Mandioca" if "Mandioca" in ok else None
    forr = next((c for c in ["Sorgo forrageiro", "Milheto"] if c in ok), None)
    milho_ok = "Milho" in ok
    milho_30 = sit["Milho"]["situacao"] == "com risco" and sit["Milho"]["risco30"] not in (None, "—", "nenhum")
    cereal = "Milho" if milho_ok else ("Sorgo granífero" if "Sorgo granífero" in ok else None)
    cereal_baixio = "Milho" if (milho_ok or milho_30) else cereal  # baixio só com milho até 30% (revisão M3)
    pousio = "Pousio pastejado"
    alerta = nivel_alerta == "alerta"
    quadra = bool(reg and reg["quadra"])
    jm = sit["Mandioca"]
    jan_mand = next((jm[k] for k in ("risco20", "risco30") if jm.get(k) not in (None, "—", "nenhum")), None)
    maniva = (f"maniva na janela ZARC da mandioca ({jan_mand}; Port. 11/2020)" if (jan_mand and "ZARC plurianual" in jm["base"])
              else "maniva de fev até o fim da janela ZARC da mandioca (em geral março)" if quadra
              else "maniva no início da estação chuvosa (confira a portaria da mandioca do estado)")

    def cel(cultura, texto, tipo=None):
        cultura = cultura or pousio
        return {"cultura": cultura, "tipo": tipo or TIPO_ROT.get(cultura, "pousio"), "texto": texto}

    seco = forr or pousio
    ano_bom = ("milho no baixio" if (not milho_ok and milho_30) else (cereal.lower() if cereal else None))
    t_leg = "precoce" if leg else "sem leguminosa no cardápio"
    pos_leg = cel(seco, (f"em ano bom: {ano_bom} depois da leguminosa (+24% no ano colhido, contra cereal solteiro)" if (ano_bom and leg)
                         else "forragem; palhada sem fogo"))
    leg_ano1 = cel(leg, t_leg + ("; metade guardada até ~10/mar" if (alerta and quadra and leg) else ""))
    if tampao:  # giro da 6.4: mandioca → leguminosa → cereal/forragem → mandioca
        f1 = [cel(tampao, maniva), cel(tampao, "tampão: colhe conforme a necessidade"),
              cel(leg, t_leg + (", na terra que foi mandioca" if leg else ""))]
        f2 = [leg_ano1, pos_leg, cel(tampao, maniva)]
        f3 = [cel(seco, "forragem; palhada sem fogo"), cel(tampao, maniva), cel(tampao, "tampão")]
    else:  # sem mandioca apta: giro de 3 fases forragem → leguminosa → cereal (ou forragem em ano seco)
        fases = [lambda: cel(seco, "forragem; palhada sem fogo"), lambda: cel(leg, t_leg), lambda: pos_leg]
        f1 = [fases[(0 + k) % 3]() for k in range(3)]
        f2 = [leg_ano1] + [fases[(1 + k) % 3]() for k in range(1, 3)]
        f3 = [fases[(2 + k) % 3]() for k in range(3)]
    baixio_txt = (f"+ {leg.lower()} em revezamento (50–85 dias depois); as linhas trocam de lugar" if leg
                  else "sem leguminosa no cardápio: sem revezamento")
    faixas = [
        {"faixa": "Faixa 1", "por_que": ("Tampão: se o ano seguinte vier ruim, a mandioca do ano anterior ainda está no chão "
                                         "(Quixadá, 1998: mandioca 50% do normal, milho 0%)." if tampao else "Sem mandioca apta aqui: falta o tampão."),
         "anos": f1},
        {"faixa": "Faixa 2", "por_que": ("Leguminosa antes do cereal: o cereal seguinte rende ~24% a mais no ano colhido, contra "
                                         "cereal solteiro (B·T1). Contra o consórcio de hoje, não medido." if leg else
                                         "Sem leguminosa no cardápio: sem rotação leguminosa → cereal."), "anos": f2},
        {"faixa": "Faixa 3", "por_que": "Forragem e palhada sem fogo; depois, a maniva.", "anos": f3},
        {"faixa": "Baixio", "por_que": "Guarda mais água: é onde fica o cereal. A leguminosa entra no milho em pé, sem bônus de grão.",
         "anos": [cel(cereal_baixio or seco, baixio_txt, "cereal" if cereal_baixio else None)] * 3},
        {"faixa": "Bordas", "por_que": ("Forragem perene e banco de proteína, em nível, longe do grão (só NE)." if no_ne
                                        else "Perene local a definir (palma e gliricídia são do semiárido do NE)."),
         "anos": ([cel("Palma + gliricídia", "em nível, sem fogo", "perene")] + [cel("Palma + gliricídia", "permanecem", "perene")] * 2)
         if no_ne else [cel("Perene local", "a definir", "perene")] * 3},
    ]
    principios = [dict(cartao(cid), regra=txt) for cid, txt in [
        ("ne_lg_cereal_sequeiro_quente", "Na mesma faixa, leguminosa num ano e cereal no seguinte: +24% no ano colhido, contra cereal solteiro."),
        ("mudare_pousio_milho", "Interruptor: em ano seco, sorgo forrageiro ou pousio no lugar do cereal (decidido no plantio)."),
        ("melo_relay_mucuna", "Dentro da quadra, a cobertura entra no milho em pé (revezamento tardio), nunca antes nem depois."),
        ("mudare_neg_sorgo_para_milho_sorgo", "Alerta (só direção, n = 10): não trocar sorgo contínuo por milho-sorgo."),
        ("martins_gliricidia_forrageira", "Gliricídia junto da palma, longe do grão."),
        ("ne_s0_para_rotacao_tempo", "Honestidade: contra o consórcio milho + feijão de hoje, o ganho da rotação não foi medido."),
    ]]
    notas = ["Trocar milho por sorgo não quebra o ciclo da lagarta-do-cartucho (as duas são gramíneas); a quebra exige uma "
             "não-gramínea: caupi, mandioca ou palma.",
             "Nada de cobertura antes do milho nem depois da colheita no sequeiro (da Luz 2023 foi irrigado; Pacheco 2013)."]
    if tampao:
        notas.append("Se não houver mandioca no chão hoje, o tampão só protege a partir de 2028; em 2027 a proteção vem do "
                     "escalonamento e da forragem.")
    if not milho_ok and milho_30:
        notas.append("Milho: o ZARC daqui não chega a risco de 20%; só no baixio (melhor janela até 30%) e escalonado.")
    elif not milho_ok and sit["Milho"]["situacao"] == "com risco":
        notas.append("Milho: aqui o ZARC só chega a risco de 40%; o plano não usa milho.")
    if not leg:
        notas.append("Sem leguminosa de grão no cardápio deste lugar: o plano não tem a rotação leguminosa → cereal.")
    if no_ne and not quadra:
        notas.append("As datas do plano (metade guardada até ~10/mar, maniva em fev–mar) são da quadra do norte; aqui a estação é "
                     f"{reg['estacao'] if reg else 'outra'}: use as janelas do ZARC do cardápio.")
    interruptor = (("Alerta para 2027: na faixa 2, metade da leguminosa fica guardada até ~10/mar. " if (alerta and quadra and leg) else
                    "Alerta para 2027: plante escalonado e guarde forragem. " if (alerta and quadra) else
                    "Alerta para 2027 no próprio município. " if alerta else
                    "Sinal fraco do El Niño aqui: siga o plano, com escalonamento. " if nivel_alerta == "sinal fraco" else
                    "El Niño não avaliado neste lugar. " if nivel_alerta == "não avaliado" else "Sem alerta. ")
                   + "Em 2028, a faixa 2 decide no plantio (com o oceano e a chuva do começo da estação). "
                     "No fim da estação (30/abr no sertão) só cabe salvar.")
    return {"anos": [2027, 2028, 2029], "faixas": faixas, "principios": principios, "interruptor": interruptor, "notas": notas}


# ---------------------------------------------------------------- consulta completa
def consultar(lat, lon):
    lon = ((lon + 180) % 360) - 180  # cópias do mundo no mapa (revisão M9)
    loc = localizar(lat, lon)
    cod, uf = loc.get("cod"), loc.get("uf")
    no_ne = bool(cod)
    sig, fonte_sig = assinatura(lat, lon, cod)
    S, W = analogos(sig) if sig else (None, pd.Series(dtype=float))
    si = aptidao(lat, lon)
    terra = any(v is not None for v in si.values()) or no_ne
    itens = cardapio(loc, si)
    reg = regime(cod, uf, lon) if cod else None
    oni_mes, oni = EN["ONI_ultimo"]
    pm = PERSP_MUN.get(cod) if cod else None
    if not no_ne:
        nivel = "não avaliado"
    elif oni >= 1.5 and pm and pm["anos"]:
        nivel = "alerta" if pm["inferior"] >= max(2, math.ceil(len(pm["anos"]) * 2 / 3)) else "sinal fraco"
    else:
        nivel = "sem alerta"
    este_ano = {"oni": oni, "oni_mes": oni_mes, "nivel_alerta": nivel, "alerta": nivel == "alerta", "nordeste": no_ne,
                "texto_oni": (f"ONI de ago–out/2026 (ASO): {_br(oni)}, {_rotulo_oni(oni)}. É o maior ago–out desde 1950 "
                              "(o recorde de qualquer trimestre é +2,59, em 2015/16).")}
    if not no_ne:
        este_ano["perspectiva"] = ("O efeito do El Niño muda de região para região e não foi avaliado aqui. O produto usaria os "
                                   "portões com a chuva IMERG e o solo SMAP do próprio lugar.")
    elif pm and pm["anos"]:
        anos_txt = "; ".join(f"{a}: {p}%" for a, p in zip(pm["anos"], pm["pct"]))
        este_ano["perspectiva"] = (f"Neste município, nos {len(pm['anos'])} El Niños fortes da série IMERG ({anos_txt} da chuva normal "
                                   f"da estação), {pm['inferior']} ficaram no terço mais seco. São chances, não certeza: 2024 foi "
                                   "El Niño forte e a quadra do CE foi normal. O Atlântico de fevereiro a abril ainda é desconhecido.")
    if uf in ATUAL.index:
        a = ATUAL.loc[uf]
        este_ano["chuva_recente"] = (f"Chuva de ago a nov/2026 em {uf}: {a.chuva_ago_nov2026_mm:.0f} mm, percentil {a.percentil:.0f} "
                                     "(dado preliminar IMERG Late/Early, comparado a uma normal do IMERG Final). É a estação seca: "
                                     "não prevê a quadra.")
    este_ano["smap"] = smap_agora(lat, lon)
    if cod:
        este_ano["regime"] = reg
        este_ano["inicio"] = inicio_estacao(cod)
        este_ano["zarc_primeiro"] = ZPRIM.get(cod)
    perto = [(cid, W.get(l)) for cid, l in LUG.items() if isinstance(l, str) and W.get(l, 0) >= 0.3]
    perto = sorted(perto, key=lambda x: -x[1])[:12]
    fr = [(cid, float(W.get(LUG[cid], 0.0))) for cid in ["franke_sahel", "franke_guine", "franke_austral"]]
    pcts = [CARDS[c]["efeito"]["central"] / float(re.search(r"(\d+,\d+) → ", CARDS[c]["efeito_texto"]).group(1).replace(",", ".")) * 100
            for c, _ in fr]
    ws = [w for _, w in fr]
    leg_pond = sum(p * w for p, w in zip(pcts, ws)) / sum(ws) if sum(ws) >= 0.3 else None  # revisão M19
    w_melhor = round(float(S.iloc[0].w), 2) if S is not None else None  # classificar pelo valor arredondado (revisão M16)
    return {
        "local": loc,
        "terra": terra,
        "fontes": FONTES,
        "clima": {**({k: sig[k] for k in VARS} if sig else {}), "fonte": fonte_sig},
        "analogos": [] if S is None else [{"lugar": r.ponto, "grupo": r.grupo, "artigos": r.artigos, "dist": round(r.dist, 2), "w": round(r.w, 2)}
                                          for r in S.head(5).itertuples()],
        "confianca": {"w": w_melhor, "texto": ("sem o clima do POWER agora: análogos indisponíveis" if w_melhor is None else
                                               "estudos de clima muito parecido" if w_melhor >= 0.6 else "estudos de clima parecido" if w_melhor >= 0.3
                                               else "nenhum estudo de clima parecido: a evidência vale só como direção e os graus valem no lugar do estudo, não aqui")},
        "cardapio": itens,
        "este_ano": este_ano,
        "plano": {**plano(itens, nivel, reg, no_ne), "modelo_ne": not no_ne} if terra else None,
        "evidencia": {"perto": [cartao(c, w) for c, w in perto], "regras": [cartao(c) for c in REGRAS],
                      "leguminosa_cereal": {"ponderado_pct": None if leg_pond is None else round(leg_pond), "soma_w": round(float(sum(ws)), 2),
                                            "central_motor": "+24% (+2 a +49), só no ano colhido e contra cereal solteiro"}},
    }


def municipios_geojson():
    """Malha do NE servida ao mapa: a MESMA que o motor usa (revisão M8), com nome, UF e ponto interno para a busca."""
    g = MUN[["cod", "municipio", "uf", "geometry"]].copy()
    rp = g.geometry.representative_point()
    g["lat"], g["lon"] = rp.y.round(4), rp.x.round(4)
    g = g.rename(columns={"municipio": "nome"})
    return g.to_json()
