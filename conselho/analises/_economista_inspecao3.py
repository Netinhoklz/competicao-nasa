import sys; sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *
import pandas as pd
m = pd.read_parquet(DERIV/"ibge_pam_mun_anual.parquet")
for p in ["Sorgo (em grão)","Gergelim","Amendoim (em casca)","Mamona (baga)","Castanha de caju","Mandioca","Fava (em grão)","Algodão herbáceo (em caroço)","Cana para forragem","Melancia","Batata-doce"]:
    d = m[(m.produto==p)&(m.ano>=2001)&(m.area_colhida_ha>0)]
    print(p, "anos", d.ano.nunique(), "mun-anos", len(d), "mun", d.cod_local.nunique(), "area média/ano", round(d.area_colhida_ha.sum()/25))
ce = pd.read_parquet(DERIV/"ibge_pam_ce_anual.parquet")
print(ce[ce.produto.str.startswith("Sorgo")].pivot_table(index="data",columns="variavel",values="valor").tail(12))
