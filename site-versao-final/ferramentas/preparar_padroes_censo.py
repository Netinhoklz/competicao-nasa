"""Gera site-versao-final/dados/padroes_censo_mun.json: os padrões do Censo Agro 2017 por município para o "não sei"
das perguntas ao agricultor (decisão 4 do PLANO_INTEGRACAO.md; campos pedidos em analise/perguntas.md, seções 2–4;
mesma conta de scratchpad/analise10/perguntas/defaults.py e defaults2.py).

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_padroes_censo.py"""
import datetime
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DERIV = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados")
SAIDA = RAIZ / "dados" / "padroes_censo_mun.json"

c = pd.read_parquet(DERIV / "ibge_ne_censo2017_praticas_mun.parquet").set_index("cod_mun")
REF = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
milho = c.area_colhida_milho_ha_fam / c.n_estab_milho_fam
caupi = c.area_colhida_feijao_fradinho_ha_fam / c.n_estab_feijao_fradinho_fam
c["rocado_ha"] = pd.concat([milho, caupi], axis=1).max(axis=1)
c["milho_ha"], c["caupi_ha"] = milho, caupi
c = c.replace([np.inf, -np.inf], np.nan)
meso_rocado = c.rocado_ha.groupby(REF.cod_meso.reindex(c.index)).median()
CAMPOS = {  # campo do JSON: (coluna, casas)
    "rocado_ha": ("rocado_ha", 2), "milho_ha_estab_fam": ("milho_ha", 2), "caupi_ha_estab_fam": ("caupi_ha", 2),
    "pct_irrig": ("pct_irrigacao_fam", 1), "pct_cisterna": ("pct_cisterna_fam", 1),
    "pct_semente_milho": ("pct_area_semente_guardada_milho", 1), "pct_semente_caupi": ("pct_area_semente_guardada_feijao_fradinho", 1),
    "pct_familiar": ("pct_familiar", 1), "pct_orientacao_tecnica": ("pct_orientacao_tecnica_fam", 1), "n_estab_fam": ("n_estab_fam", 0),
}
out = {"_fonte": {
    "base": "IBGE, Censo Agropecuário 2017 (SIDRA 6880, 6855, 6857, 6846, 6847, 6861, 6958), via dados_resumo/derivados/ibge_ne_censo2017_praticas_mun.parquet",
    "tipo": "medido (IBGE 2017); usar como padrão do 'não sei' é suposição",
    "campos": {
        "rocado_ha": "roçado típico da família: o maior entre a área colhida de milho e a de feijão-fradinho (caupi) por estabelecimento "
                     "familiar que planta cada um (ha). É área COLHIDA no ano agrícola 2016/17, no meio da seca de 2012–17: subestima a plantada",
        "milho_ha_estab_fam": "área colhida de milho ÷ estabelecimentos familiares com milho (ha)",
        "caupi_ha_estab_fam": "área colhida de feijão-fradinho (caupi) ÷ estabelecimentos familiares com caupi (ha)",
        "pct_irrig": "% dos estabelecimentos familiares que usaram irrigação",
        "pct_cisterna": "% dos estabelecimentos familiares com cisterna (quase sempre de beber: não salva a lavoura)",
        "pct_semente_milho": "% da área colhida de milho plantada com semente guardada (todos os estabelecimentos; a coluna só da agricultura "
                             "familiar tem mais sigilo/ausência)",
        "pct_semente_caupi": "% da área colhida de feijão-fradinho plantada com semente guardada (todos os estabelecimentos)",
        "pct_familiar": "% dos estabelecimentos que são da agricultura familiar (Lei 11.326)",
        "pct_orientacao_tecnica": "% dos estabelecimentos familiares com orientação técnica (para saber se a família usa a tela sozinha)",
        "n_estab_fam": "número de estabelecimentos da agricultura familiar",
        "rocado_ha_padrao": "o valor para o 'não sei' do tamanho: rocado_ha do município; se for null, a mediana da mesorregião (origem_rocado)"},
    "nulos": "null = o Censo não publica (sigilo, nenhum estabelecimento com a cultura) ou o município não existe na tabela",
    "sem_coluna": "o parquet não tem rebanho (PPM) nem baixio/água guardada em volume: a pergunta da criação e o tamanho do barreiro ficam sem padrão do Censo",
    "script": "site-versao-final/ferramentas/preparar_padroes_censo.py",
    "gerado_em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}}
for cod in REF.index:
    rm = meso_rocado.get(REF.cod_meso[cod], np.nan)
    reserva = {"rocado_ha_padrao": None if pd.isna(rm) else round(float(rm), 2), "origem_rocado": "mesorregião"}
    if cod not in c.index:
        out[cod] = {k: None for k in CAMPOS} | reserva | {"avisos": ["município fora da tabela do Censo 2017"]}
        continue
    r = c.loc[cod]
    d = {}
    for k, (col, casas) in CAMPOS.items():
        v = r[col]
        d[k] = None if pd.isna(v) else (int(round(v)) if casas == 0 else round(float(v), casas))
    d |= {"rocado_ha_padrao": d["rocado_ha"], "origem_rocado": "município"} if d["rocado_ha"] is not None else reserva
    d["avisos"] = [f"{k}: sem dado no Censo 2017" for k in ["rocado_ha", "pct_irrig", "pct_cisterna", "pct_semente_milho", "pct_semente_caupi"]
                   if d[k] is None]
    out[cod] = d
SAIDA.write_text(json.dumps(out, ensure_ascii=False, allow_nan=False, separators=(",", ":")), encoding="utf-8")
v = pd.DataFrame({k: x for k, x in out.items() if not k.startswith("_")}).T
print("nulos por campo:", v[list(CAMPOS)].isna().sum().to_dict())
print("rocado_ha mediana/P10/P90:", v.rocado_ha.astype(float).quantile([.5, .1, .9]).round(2).tolist())
print("Quixadá:", out["2311306"])
print(SAIDA, f"{SAIDA.stat().st_size / 1e3:.0f} kB")
