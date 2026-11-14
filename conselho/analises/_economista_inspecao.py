import sys; sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *
import pandas as pd
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)
for f in ["ibge_pam_ce_anual","ibge_pam_mun_anual","mercado_precos_mensal","faostat_precos_produtor","power_ce_mensal","indices_clima_mensal","gaez_ranking_culturas_ce_ne","imerg_ce_mensal","faostat_brasil_anual"]:
    d = pd.read_parquet(DERIV / f"{f}.parquet")
    print("=====", f, d.shape); print(d.dtypes.to_dict()); print(d.head(3).to_string())
    for c in ["variavel","produto","commodity","Item","Element"]:
        if c in d.columns: print(c, d[c].nunique(), list(d[c].unique()[:60]))
