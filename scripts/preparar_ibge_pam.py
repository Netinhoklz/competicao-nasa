"""Derivados do IBGE PAM para cruzamento (formato longo, anual).

Saidas:
  derivados/ibge_pam_ce_anual.parquet   soma do Ceara por cultura e ano (rendimento recalculado = producao/area colhida)
  derivados/ibge_pam_mun_anual.parquet  municipio x cultura x ano (largura: area_plantada, area_colhida, producao_t, rendimento_kg_ha, valor)
"""
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
pam = pd.read_parquet(DADOS / "ibge_pam" / "pam_ce_municipios.parquet")
pam = pam[pam.cod_produto != "0"].copy()
mapa = {"Área plantada": "area_plantada_ha", "Área destinada à colheita": "area_plantada_ha", "Área colhida": "area_colhida_ha",
        "Quantidade produzida": "producao_t", "Rendimento médio da produção": "rendimento_kg_ha", "Valor da produção": "valor_mil_moeda"}
pam["v"] = pam.variavel.map(mapa)
larg = pam.pivot_table(index=["cod_local", "local", "produto", "tipo", "ano"], columns="v", values="valor", aggfunc="sum").reset_index()
larg.columns.name = None
larg.to_parquet(DERIV / "ibge_pam_mun_anual.parquet")

ce = larg.groupby(["produto", "tipo", "ano"])[["area_plantada_ha", "area_colhida_ha", "producao_t", "valor_mil_moeda"]].sum(min_count=1).reset_index()
ce["rendimento_kg_ha"] = 1000 * ce.producao_t / ce.area_colhida_ha.replace(0, np.nan)
ce["perda_area_frac"] = 1 - ce.area_colhida_ha / ce.area_plantada_ha.replace(0, np.nan)
longo = ce.melt(id_vars=["produto", "tipo", "ano"], var_name="variavel", value_name="valor")
longo["data"] = pd.to_datetime(longo.ano.astype(str) + "-01-01")
un = {"area_plantada_ha": "ha", "area_colhida_ha": "ha", "producao_t": "t", "valor_mil_moeda": "mil (moeda do ano; R$ desde 1994)",
      "rendimento_kg_ha": "kg/ha", "perda_area_frac": "fração"}
longo["unidade"] = longo.variavel.map(un)
longo["fonte"] = "IBGE PAM (SIDRA 1612/1613), soma dos 184 municípios"
longo[["data", "produto", "tipo", "variavel", "valor", "unidade", "fonte"]].to_parquet(DERIV / "ibge_pam_ce_anual.parquet")
print("municipal:", larg.shape, "| estadual longo:", longo.shape)
registrar_manifesto("ibge_pam", {"derivados": {
    "derivados/ibge_pam_ce_anual.parquet": "Ceará por cultura e ano (formato longo), rendimento e perda de área recalculados",
    "derivados/ibge_pam_mun_anual.parquet": "município × cultura × ano (formato largo)"}})
