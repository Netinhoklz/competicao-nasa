"""Monta a página final (index.html) injetando os dados no modelo.

Uso (a partir do root do projeto):
    python interface-inicial-vicente/scripts/montar_pagina.py
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
modelo = (BASE / 'fonte' / 'pagina.html').read_text(encoding='utf-8')
dados = (BASE / 'dados' / 'dados_pagina.json').read_text(encoding='utf-8')
(BASE / 'index.html').write_text(modelo.replace('__DATA__', dados), encoding='utf-8')
print('index.html gerado')
