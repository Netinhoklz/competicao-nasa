import pandas as pd, json
D = "c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados/"
for f in ["ibge_ne_pam_mun_anual", "ibge_ne_pam_safras_mun_anual", "ibge_ne_mun_imerg_mensal", "ibge_ne_mun_smap_mensal", "ibge_ne_lspa_uf_mensal", "indices_clima_mensal", "ibge_ne_municipios_referencia"]:
    df = pd.read_parquet(D + f + ".parquet")
    print("=====", f, df.shape)
    print(df.dtypes.to_string())
    print(df.head(3).to_string())
    for c in df.columns:
        if df[c].dtype == object and df[c].nunique() < 60:
            print(c, sorted(df[c].dropna().unique().tolist())[:60])
    for c in ["ano", "data", "mes", "periodo"]:
        if c in df.columns:
            print(c, df[c].min(), df[c].max())
df = pd.read_parquet("E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet")
print("===== painel", df.shape); print(df.dtypes.to_string()); print(df.head(3).to_string())
for c in df.columns:
    if df[c].dtype == object and df[c].nunique() < 60:
        print(c, sorted(df[c].dropna().unique().tolist()))
if "ano" in df.columns: print(df.ano.min(), df.ano.max())
for f in ["indices.csv", "eventos.csv", "analogos_rendimento_ce.csv", "perspectiva_uf.csv"]:
    x = pd.read_csv("E:/campeonato-nasa/dados/el_nino_2026/" + f)
    print("=====", f, x.shape); print(x.head(5).to_string()); print(x.tail(3).to_string())
print(open("E:/campeonato-nasa/dados/el_nino_2026/resumo.json", encoding="utf8").read()[:3000])
