"""Engenheiro de viabilidade: checagens pontuais para o MVP (só leitura)."""
import sys, os, glob, json
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import pandas as pd
import numpy as np

S = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises"
D = "E:/campeonato-nasa/dados"

print("## 1. Chuva diária municipal: índice")
c = pd.read_parquet(os.path.join(S, "chuva_mun_diaria.parquet"))
print(" índice:", type(c.index).__name__, c.index.min(), "->", c.index.max(), "| NaN total:", int(c.isna().sum().sum()))
q = "2311306"  # Quixadá (IBGE 2311306)
print(" Quixadá na tabela:", q in c.columns)

print("\n## 2. Balde do hidrólogo: culturas e regras")
h = pd.read_parquet(os.path.join(S, "hidrologo_fao56_mun_ano.parquet"))
print(" culturas:", sorted(h["cultura"].unique()), "| regras:", sorted(h["regra"].unique()))
print(" municípios:", h["cod"].nunique())

print("\n## 3. Carteira CVaR: municípios")
k = pd.read_parquet(os.path.join(S, "carteira_cvar_municipios.parquet"))
print(" linhas:", len(k), "| municípios únicos:", k["cod"].nunique())
print(" fração com seca_robusta_oos < seca_atual:", round(float((k["seca_robusta_oos"] < k["seca_atual"]).mean()), 3))
print(" fração com cvar_robusta > cvar_atual:", round(float((k["cvar_robusta"] > k["cvar_atual"]).mean()), 3))

print("\n## 4. PAM: produtos que o MVP cita, Quixadá, área plantada 2015-2025")
p = pd.read_parquet(os.path.join(D, "derivados", "ibge_pam_mun_anual.parquet"))
pq = p[(p["cod_local"].astype(str) == q) & (p["ano"] >= 2015)]
for prod in ["Milho (em grão)", "Feijão (em grão)", "Mandioca", "Sorgo (em grão)", "Algodão herbáceo (em caroço)"]:
    s = pq[pq["produto"] == prod].set_index("ano")["area_plantada_ha"]
    print(f" {prod}: ", s.to_dict() if len(s) else "ausente")
print(" produtos com 'palma' ou 'forrag' no PAM:", [x for x in p["produto"].unique() if "alma" in x or "orrag" in x])

print("\n## 5. Dados brutos que o rascunho cita como camada")
for base in ["appeears", "gldas", "viirs", "landsat", "nex_gddp", "srtm", "imerg", "power", "earthdata_metadados", "referencia"]:
    pasta = os.path.join(D, base)
    arqs = glob.glob(os.path.join(pasta, "**", "*"), recursive=True)
    arqs = [a for a in arqs if os.path.isfile(a)]
    tam = sum(os.path.getsize(a) for a in arqs) / 1e9
    ext = pd.Series([os.path.splitext(a)[1] for a in arqs]).value_counts().head(5).to_dict()
    print(f" {base}: {len(arqs)} arquivos, {tam:.2f} GB, extensões {ext}")
eco = glob.glob(os.path.join(D, "**", "*ECO*"), recursive=True) + glob.glob(os.path.join(D, "**", "*eco*stress*"), recursive=True)
print(" ECOSTRESS em disco:", len(eco), eco[:3])
smap = [a for a in glob.glob(os.path.join(D, "appeears", "**", "*"), recursive=True) if os.path.isfile(a)]
print(" AppEEARS (SMAP/VIIRS NDVI) em disco:", len(smap), [os.path.basename(a) for a in smap[:6]])
nex = [os.path.basename(a) for a in glob.glob(os.path.join(D, "nex_gddp", "**", "*.nc"), recursive=True)]
mods = sorted(set(n.split("_")[2] if len(n.split("_")) > 2 else n for n in nex))
print(" NEX-GDDP modelos (pelo nome):", mods[:10], "| arquivos .nc:", len(nex))

print("\n## 6. Índices: último ONI")
ix = pd.read_parquet(os.path.join(D, "derivados", "indices_clima_mensal.parquet"))
print(ix[ix["variavel"] == "ONI"].tail(4).to_string())

print("\n## 7. VIIRS: granularidade disponível")
vi = [a for a in glob.glob(os.path.join(D, "viirs", "**", "*"), recursive=True) if os.path.isfile(a)]
print(" arquivos:", [os.path.basename(a) for a in vi[:12]])
