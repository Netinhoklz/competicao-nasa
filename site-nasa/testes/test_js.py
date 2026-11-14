"""JavaScript no navegador: regras puras (util.js) e o painel Roca Certa de ponta a ponta (Chrome sem janela)."""
from __future__ import annotations

import json
import re

from conftest import texto_de


def test_util_js(servidor, dom):
    pagina = dom(f"{servidor}/_testes/testes.html")
    bruto = texto_de(pagina, "resultado")
    assert bruto and bruto != "rodando", "a pagina de testes nao terminou (erro de import em util.js?)"
    resultados = json.loads(bruto)
    falhas = [f"{r['nome']}: {r.get('erro')}" for r in resultados if not r["ok"]]
    assert not falhas, "\n".join(falhas)
    assert len(resultados) >= 30, f"so {len(resultados)} testes rodaram"


def test_painel_completo_desenha_quixada(servidor, dom):
    pagina = dom(f"{servidor}/painel/2311306")
    assert "<h1>Quixadá: depois de El Niño, seca em 6 de cada 10 municípios no Ceará</h1>" in pagina
    assert pagina.count('<article class="ind') == 4                                 # quatro indicadores
    assert len(re.findall(r'<path data-c="\d{7}"', pagina)) == 1793                # mapa: todos menos Noronha (ilha)
    assert "<svg viewBox=\"0 0 640" in pagina                                       # grafico desenhado


def test_painel_embutido_sem_mapa_e_escuro(servidor, dom):
    pagina = dom(f"{servidor}/painel/2304400?embutido=1")
    assert re.search(r'<html[^>]*data-theme="dark"', pagina)
    assert re.search(r'<body[^>]*class="[^"]*embutido', pagina)
    assert '<path data-c="' not in pagina                                         # nao desenha o mapa (ja esta ao lado)
    assert "Abrir em tela cheia" in pagina
    assert "Fortaleza" in pagina


def test_painel_estado_com_sinal_fraco_nao_assusta(servidor, dom):
    pagina = dom(f"{servidor}/painel/2927408")                                     # Salvador: Bahia, 36% ~ acaso
    assert "El Niño muda pouco a chuva na Bahia" in pagina
    assert "Previsão firma em fevereiro" in pagina
