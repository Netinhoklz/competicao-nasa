"""Verificador adversario do catalogo v4: recontas dos numeros que pesam no motor.

Fontes: Souza 2011 (Bragantia 70:715-721) Tab. 1-3; Mudare 2025 Source Data
(E:/campeonato-nasa/dados/suplementos_artigos/2025_Mudare_source_data.xlsx);
PAM-CE (ibge_pam_mun_anual.parquet). Nao altera nenhum arquivo.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403
import math
import pandas as pd
import openpyxl

print("===== A. Souza 2011: LER por lamina (Tab. 1 solteiro, Tab. 2 consorcio, p.718) =====")
# (milho solteiro, caupi solteiro, milho consorcio, caupi consorcio)  kg/ha
tab = {"L125": (3860.0, 1320.7, 3476.7, 622.3), "L100": (3418.3, 1374.7, 2865.8, 556.0),
       "L75": (3005.0, 1316.5, 2600.0, 609.0), "L50": (2433.3, 866.0, 2098.3, 373.7),
       "L0": (1655.0, 571.4, 1506.7, 138.3)}
for k, (ms, cs, mc, cc) in tab.items():
    print(f"  {k}: pLER milho {mc/ms:.3f} + caupi {cc/cs:.3f} = LER {mc/ms + cc/cs:.3f}")
ms_m = sum(v[0] for v in tab.values()) / 5
cs_m = sum(v[1] for v in tab.values()) / 5
mc_m = sum(v[2] for v in tab.values()) / 5
cc_m = sum(v[3] for v in tab.values()) / 5
print(f"  medias recalculadas: milho sol {ms_m:.1f} (impresso 3.179,2), caupi sol {cs_m:.1f} (impresso 1.219,5)")
print(f"  queda no consorcio: milho {100*(mc_m/ms_m-1):+.1f}% (texto p.719: -13%), "
      f"caupi {100*(cc_m/cs_m-1):+.1f}% (texto: -66%); caupi c/ media impressa {100*(cc_m/1219.5-1):+.1f}%")
rr = [tab[k][3] / tab[k][1] for k in tab]
print(f"  caupi: media das razoes por lamina {100*(sum(rr)/5-1):+.1f}%")
print("  Ye (Tab. 3, p.720) / milho solteiro: L125 %+.1f%%, L0 %+.1f%%" % (100*(4719.54/3860-1), 100*(1782.93/1663.33-1)))

print("\n===== B. Mudare 2025 Source Data: sequencias (aba Figure 3e) e Africa (Figure 1e) =====")
wb = openpyxl.load_workbook(r"E:/campeonato-nasa/dados/suplementos_artigos/2025_Mudare_source_data.xlsx",
                            read_only=True, data_only=True)
ws = wb["Figure 3e"]
for r in ws.iter_rows(values_only=True):
    if r[0] in ("Energy", "Revenue") and r[1] in ("Maize-sorghum", "Soybean-maize", "Soybean-sorghum", "Sorghum-maize"):
        es, lo, hi, n = r[2], r[6], r[7], r[9]
        f = lambda x: 100 * (math.exp(x) - 1)
        print(f"  {r[0]:8s} {r[1]:16s} lnR {es:+.4f} ({lo:+.3f} a {hi:+.3f}) = {f(es):+.1f}% ({f(lo):+.1f} a {f(hi):+.1f}); n={n}")
ws = wb["Figure 1e"]
for r in ws.iter_rows(values_only=True):
    if r[0] in ("Africa", "North America", "Global") and r[1] in ("Legume", "Non-legume"):
        print(f"  {r[0]:14s} {r[1]:11s} lnR {r[2]:.4f} ({r[3]:.3f} a {r[4]:.3f}) = "
              f"{100*(math.exp(r[2])-1):+.1f}% ({100*(math.exp(r[3])-1):+.1f} a {100*(math.exp(r[4])-1):+.1f}); {r[8]}")

print("\n===== C. Quebra do milho no PAM-CE: sensibilidade da janela da mediana =====")
pam = pd.read_parquet(r"E:/campeonato-nasa/dados/derivados/ibge_pam_mun_anual.parquet")
m = pam[pam["produto"].astype(str).str.lower().str.contains("milho") & (pam.area_plantada_ha > 0)].copy()
print("  produtos com 'milho':", sorted(m.produto.astype(str).unique()))
m["yp"] = m.producao_t * 1000 / m.area_plantada_ha
m["med_tudo"] = m.groupby("cod_local").yp.transform("median")
s = m[(m.ano >= 2000) & (m.ano <= 2024)].copy()
s["med_janela"] = s.groupby("cod_local").yp.transform("median")
print(f"  como no debate (milho grao + milho verde 2025 na mesma mediana), 2000-2024, n={len(s)}: "
      f"mediana de todos os anos -> {100*(s.yp < 0.5*s.med_tudo).mean():.1f}% | "
      f"mediana 2000-2024 -> {100*(s.yp < 0.5*s.med_janela).mean():.1f}%")
print("  anos por produto:", m.groupby("produto").ano.agg(["min", "max", "size"]).to_dict("index"))
g = m[m.produto.astype(str) == "Milho (em grão)"].copy()
g["med_tudo"] = g.groupby("cod_local").yp.transform("median")
s = g[(g.ano >= 2000) & (g.ano <= 2024)].copy()
s["med_janela"] = s.groupby("cod_local").yp.transform("median")
print(f"  so milho grao, 2000-2024, n={len(s)}: mediana 1988-2025 -> {100*(s.yp < 0.5*s.med_tudo).mean():.1f}% | "
      f"mediana 2000-2024 (mesma janela do calculo NE) -> {100*(s.yp < 0.5*s.med_janela).mean():.1f}%")
