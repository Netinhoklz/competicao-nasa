"""Integridade dos dados que o site serve (static/data/) e do gerador (ferramentas/gerar_municipios.py)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1]
DADOS = SITE / "static" / "data"
UFS = {"MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"}


@pytest.fixture(scope="module")
def mun():
    return json.loads((DADOS / "municipios_ne.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def malha():
    return json.loads((DADOS / "malha_ne.json").read_text(encoding="utf-8"))


def test_todos_os_municipios_do_nordeste(mun):
    assert len(mun["m"]) == 1794
    assert {m[1] for m in mun["m"].values()} == UFS
    assert all(len(c) == 7 and c[:2] in {str(x) for x in range(21, 30)} for c in mun["m"])


def test_campos_e_tamanhos(mun):
    n = len(mun["campos"])
    anos = mun["anos"]
    assert anos == list(range(1998, anos[-1] + 1))
    assert mun["analogos"] == [1998, 2010, 2016, 2024]
    for cod, m in mun["m"].items():
        assert len(m) == n, cod
        assert m[4] is None or 1 <= m[4] <= 12, cod                       # inicio da estacao
        assert len(m[6]) == 12, cod                                        # chuva de cada mes
        assert len(m[7]) == 4, cod                                         # anos de El Nino
        assert len(m[13]) == len(anos), cod                                # chuva de cada ano


def test_valores_em_faixas_validas(mun):
    for cod, m in mun["m"].items():
        assert m[5] is None or 0 < m[5] < 3000, cod                        # normal da estacao (mm)
        assert all(v is None or v >= 0 for v in m[6]), cod
        for a in m[7]:
            assert a is None or (a[0] >= 0 and a[1] in (0, 1)), cod
        assert m[8] is None or -1 <= m[8] <= 1, cod                        # correlacao
        assert m[10] is None or 0 <= m[10] <= 100, cod                     # percentil do solo
        assert m[12] in (0, 1), cod                                        # Semiarido


def test_oni_e_mes_do_solo(mun):
    assert -4 < mun["oni"]["valor"] < 4
    assert len(mun["oni"]["mes"]) == 7                                     # mm/aaaa
    assert mun["solo_mes"]


def test_quixada_bate_com_a_analise(mun):
    """Referencia da proposta: Quixada tem estacao jan-abr e chuva fraca em 3 dos 4 El Ninos fortes."""
    q = mun["m"]["2311306"]
    assert q[0] == "Quixadá" and q[1] == "CE"
    assert q[4] == 1
    assert sum(a[1] for a in q[7] if a) == 3


NORONHA = "2605459"   # ilha oceanica: fica fora do quadro do mapa (sem desenho), mas tem dados


def test_el_nino_por_estado(mun):
    e = mun["enso"]
    assert e["anos"] == [1998, 2003, 2005, 2010, 2016, 2024]          # ONI jul-set >= 0,5, periodo do IMERG
    assert set(e["uf"]) == {"MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"}
    for u, v in e["uf"].items():
        assert len(v["por_ano"]) == len(e["anos"]), u
        assert all(x is None or 0 <= x <= 100 for x in v["por_ano"]), u
        assert 0 <= v["media"] <= 100, u
    assert e["uf"]["CE"]["media"] == 57 and e["uf"]["CE"]["por_ano"][0] == 100   # 1998: o Ceara inteiro seco


def test_malha_cobre_os_municipios(mun, malha):
    assert set(malha["m"]) == set(mun["m"])
    sem_desenho = [c for c, d in malha["m"].items() if not (d.startswith("M") and d.endswith("Z"))]
    assert sem_desenho == [NORONHA]
    assert set(malha["ufs"]) == UFS
    for uf in malha["ufs"].values():
        x0, y0, x1, y1 = uf["caixa"]
        assert 0 <= x0 < x1 <= malha["vb"][0] and 0 <= y0 < y1 <= malha["vb"][1]


def test_contorno_do_nordeste_fechado():
    ne = json.loads((DADOS / "nordeste.json").read_text(encoding="utf-8"))
    assert ne["contorno"] and all(len(anel) > 100 for anel in ne["contorno"])
    oeste, sul, leste, norte = ne["bbox"]
    assert oeste < -47 and leste > -35 and sul < -18 and norte > -1


# ------------------------------------------------------------------ funcoes do gerador

@pytest.fixture(scope="module")
def gerador():
    sys.path.insert(0, str(SITE / "ferramentas"))
    import gerar_municipios
    return gerar_municipios


def test_caminho_svg_de_um_quadrado(gerador):
    d, caixa = gerador.caminho({"type": "Polygon", "coordinates": [[[-40, -5], [-39, -5], [-39, -6], [-40, -6], [-40, -5]]]})
    assert d.startswith("M") and d.endswith("Z")
    assert caixa[0] < caixa[2] and caixa[1] < caixa[3]


def test_caminho_ignora_ilhas_oceanicas(gerador):
    noronha = [[-32.4, -3.8], [-32.3, -3.8], [-32.3, -3.9], [-32.4, -3.9], [-32.4, -3.8]]
    d, caixa = gerador.caminho({"type": "MultiPolygon", "coordinates": [[noronha]]})
    assert d == "" and caixa == []


def test_caminho_simplifica_vertices_muito_proximos(gerador):
    anel = [[-40 + i * 0.0001, -5] for i in range(50)] + [[-39, -6], [-40, -6], [-40, -5]]
    d, _ = gerador.caminho({"type": "Polygon", "coordinates": [anel]})
    assert d.count("L") < 10


def test_centro_do_maior_anel(gerador):
    lat, lon = gerador.centro({"type": "Polygon", "coordinates": [[[-40, -5], [-38, -5], [-38, -7], [-40, -7]]]})
    assert (lat, lon) == (-6.0, -39.0)


@pytest.mark.parametrize("v, esperado", [(None, None), (float("nan"), None), (2.4, 2), (2.6, 3)])
def test_inteiro(gerador, v, esperado):
    assert gerador.inteiro(v) == esperado
