import pandas as pd, numpy as np
D = "c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados/"
I = pd.read_parquet(D + "indices_clima_mensal.parquet")
o = I[I.variavel == "ONI"].set_index("data").valor
aso = o[o.index.month == 9]
aso.index = aso.index.year + 1  # ano da safra afetada
print(aso.loc[1996:2027].round(2).to_string())
R = pd.read_parquet(D + "ibge_ne_municipios_referencia.parquet")
print(R[R.municipio.isin(["Quixadá", "Barreiras", "Arapiraca", "Petrolina", "Tauá", "Sobral"])][["cod_mun", "municipio", "uf", "mesorregiao", "semiarido_2022"]])
print(R.cod_meso.nunique())
P = pd.read_parquet("E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet")
v = P[(P.area_plantada_ha > 0) & P.produto.isin(["Milho", "Feijão", "Mandioca"])].copy()
# rendimentos repetidos (sinal de estimativa subjetiva)
v = v.sort_values(["produto", "cod_mun", "ano"])
v["rep"] = v.groupby(["produto", "cod_mun"]).rend_plantado_kg_ha.diff().abs() < 1e-6
print("fração de anos com rendimento idêntico ao ano anterior:")
print(v.groupby("produto").rep.mean().round(3).to_string())
print("perda de área (1 - colhida/plantada) média por produto e anos EN:")
v["EN"] = v.ano.isin([1998, 2010, 2016, 2024])
print(v.groupby(["produto", "EN"]).perda_area.mean().unstack().round(3))
print("zeros de produção com área plantada > 0:", v.groupby("produto").apply(lambda g: (g.producao_t == 0).mean()).round(3).to_dict())
