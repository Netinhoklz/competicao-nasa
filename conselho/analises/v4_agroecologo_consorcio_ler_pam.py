"""v4 agroecologo: consorcio milho-caupi.

A. LER derivado das Tabelas 1 e 2 de Souza et al. 2011 (Bragantia 70:715, p. 718) por lamina
   de irrigacao (o artigo NAO calcula LER; calcula so a producao equivalente Ye, Tabela 3).
   Conferencia com Lima Filho 2000 (PAB 35:915, Tabela 1, p. 920): LER 1,13.
B. PAM municipal do CE 1974-2025: milho e feijao quebram juntos? (o consorcio protege da seca?)
   Rendimento por area PLANTADA (inclui perda total), razao a mediana do proprio municipio.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd

print("=" * 100)
print("A. LER por lamina, derivado de Souza 2011 (Tabelas 1 e 2, p. 718). Delineamento de substituicao:")
print("   caupi 80 mil pl/ha solteiro x 40 mil no consorcio; milho 50 mil nos dois (p. 716; Souza 2015 p. 153)")
print("=" * 100)
# lamina: (milho solteiro, caupi solteiro, milho consorcio, caupi consorcio, LI milho sol, LI milho cons)
t = {
    "L125": (3860.0, 1320.7, 3476.7, 622.3, 499.1, 558.3),
    "L100": (3418.3, 1374.7, 2865.8, 556.0, 471.2, 529.8),
    "L75":  (3005.0, 1316.5, 2600.0, 609.0, 443.3, 502.3),
    "L50":  (2433.3, 866.0, 2098.3, 373.7, 415.4, 474.4),
    "L0":   (1655.0, 571.4, 1506.7, 138.3, 359.5, 421.1),
}
linhas = []
for k, (ms, cs, mc, cc, lis, lic) in t.items():
    pm, pc = mc / ms, cc / cs
    linhas.append(dict(lamina=k, LER_parcial_milho=round(pm, 3), LER_parcial_caupi=round(pc, 3),
                       LER=round(pm + pc, 3), agua_extra_consorcio_mm=round(lic - lis, 1)))
d = pd.DataFrame(linhas)
print(d.to_string(index=False))
print(f"  Medias da tabela (ultima linha): milho 2509,5/3179,2 + caupi 459,9/1219,5 = "
      f"{2509.5/3179.2:.3f} + {459.9/1219.5:.3f} = {2509.5/3179.2 + 459.9/1219.5:.3f}")
print("  Lima Filho 2000 (Tabela 1): 1500/2208 + 700/1550 =", round(1500/2208, 3), "+", round(700/1550, 3),
      "=", round(1500/2208 + 700/1550, 3), "(o artigo imprime 0,68 + 0,45 = 1,13)")
print("  Leitura: o LER cai de 1,24-1,37 (com agua) para 1,15 na lamina 0; quem cai e o caupi (0,47 -> 0,24).")
print("  CONFUSAO: o consorcio recebeu 58-62 mm a mais que o milho solteiro em toda lamina (Tabelas 1-2).")
print("  Inconsistencia do artigo: milho solteiro L0 = 1.655,0 (Tab. 1) x 1.663,33 (Tab. 3).")
print("  Unidade: 'EUA (kg m-3)' das Tabelas 1-2 = 10 x kg ha-1 mm-1 (3418,3/471,2 = 7,25 kg/ha/mm; tabela 72,5).")

print()
print("=" * 100)
print("B. PAM CE (pares milho+feijao com area plantada: 1988-2025): o milho e o feijao quebram juntos?")
print("=" * 100)
p = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
p = p[p.produto.str.startswith("Milho") | p.produto.str.startswith("Feij")].copy()
p["cult"] = np.where(p.produto.str.startswith("Milho"), "milho", "feijao")
p = p[p.area_plantada_ha > 0]
p["rend_pl"] = p.producao_t * 1000 / p.area_plantada_ha
w = p.pivot_table(index=["cod_local", "ano"], columns="cult", values="rend_pl").dropna()
a = p.pivot_table(index=["cod_local", "ano"], columns="cult", values="area_plantada_ha").reindex(w.index)
med = w.groupby(level=0).transform("median")
r = (w / med).rename(columns=lambda c: "r_" + c)
r = r.join(a.rename(columns=lambda c: "a_" + c))
r = r.reset_index()
r["era"] = np.where(r.ano <= 1997, f"{r.ano.min()}-1997", "1998-2025")
print(f"  municipio-anos com as duas culturas: {len(r)}; municipios {r.cod_local.nunique()}; "
      f"anos {r.ano.min()}-{r.ano.max()}")
print(f"  razao de area plantada feijao/milho: mediana {np.nanmedian(r.a_feijao / r.a_milho):.2f} "
      f"(p10 {np.nanpercentile(r.a_feijao / r.a_milho, 10):.2f}, p90 {np.nanpercentile(r.a_feijao / r.a_milho, 90):.2f})")


def resumo(g):
    fm, ff = g.r_milho < 0.5, g.r_feijao < 0.5
    rho = g[["r_milho", "r_feijao"]].corr(method="spearman").iloc[0, 1]
    idx = (g.r_milho + g.r_feijao) / 2
    return pd.Series(dict(
        n=len(g), rho_spearman=round(rho, 2),
        p_quebra_milho=round(fm.mean(), 3), p_quebra_feijao=round(ff.mean(), 3),
        p_ambos=round((fm & ff).mean(), 3),
        p_ambos_se_independentes=round(fm.mean() * ff.mean(), 3),
        p_feijao_quebra_dado_milho=round((fm & ff).sum() / max(fm.sum(), 1), 3),
        p_milho_quebra_dado_feijao=round((fm & ff).sum() / max(ff.sum(), 1), 3),
        # dispersao robusta (p90-p10)/mediana: o CV classico explode com area plantada minuscula
        disp_milho=round(np.subtract(*g.r_milho.quantile([.9, .1])) / g.r_milho.median(), 2),
        disp_feijao=round(np.subtract(*g.r_feijao.quantile([.9, .1])) / g.r_feijao.median(), 2),
        disp_media_das_duas=round(np.subtract(*idx.quantile([.9, .1])) / idx.median(), 2),
        p10_milho=round(g.r_milho.quantile(.1), 2), p10_feijao=round(g.r_feijao.quantile(.1), 2),
        p10_media_das_duas=round(idx.quantile(.1), 2),
    ))


print(pd.concat({"tudo": resumo(r), **{e: resumo(g) for e, g in r.groupby("era")}}, axis=1).to_string())

rho_mun = r.groupby("cod_local").apply(
    lambda g: g[["r_milho", "r_feijao"]].corr(method="spearman").iloc[0, 1] if len(g) >= 20 else np.nan)
print(f"\n  rho por municipio (>=20 anos): mediana {rho_mun.median():.2f}, p10 {rho_mun.quantile(.1):.2f}, "
      f"p90 {rho_mun.quantile(.9):.2f}, n={rho_mun.notna().sum()}; municipios com rho < 0,5: "
      f"{(rho_mun < 0.5).sum()}")

# anos de seca estadual: mediana estadual da razao do milho < 0,5
est = r.groupby("ano")[["r_milho", "r_feijao"]].median()
seca = est[est.r_milho < 0.5]
print(f"\n  Anos de seca estadual (mediana da razao do milho < 0,5): {len(seca)}")
print(seca.round(2).T.to_string())
print(f"  Nesses anos: razao mediana milho {seca.r_milho.median():.2f} x feijao {seca.r_feijao.median():.2f}; "
      f"anos em que o feijao ficou >= 0,5: {(seca.r_feijao >= 0.5).sum()} de {len(seca)}")

g = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
gs = g[g.produto.str.startswith("Girassol") & (g.area_plantada_ha > 0)]
print(f"\n  Girassol no PAM do CE (rotacao caupi/girassol de Neves 2015): municipio-anos com area > 0 = {len(gs)}; "
      f"area total {gs.area_plantada_ha.sum():.0f} ha; anos {sorted(gs.ano.unique().tolist())}")
