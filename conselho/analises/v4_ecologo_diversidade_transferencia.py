"""v4 - Ecologo de diversidade: testes rapidos de TRANSFERENCIA das regras de Bowles 2020, Smith 2023 e MacLaren 2022
para o semiarido do Nordeste, com os nossos dados (IMERG por municipio, PAM NE, Censo Agro 2017).

  A  gradiente de chuva: Bowles 2020 (Tabela 1, p. 286) so achou ganho de rendimento da rotacao entre 664 e 1.074 mm/ano;
     no sitio mais seco (CO, 406 mm) nao houve ganho e no SD (582 mm) so em anos de seca (p. 289). Onde cai o semiarido?
  B  linha de base: Smith 2023 e MacLaren 2022 medem o ganho CONTRA A MONOCULTURA (Simpson = 1). Quao longe disso ja esta
     a carteira municipal do NE (Simpson inverso e riqueza funcional das 5 lavouras temporarias da PAM)? E o milho e o
     feijao andam juntos (sinal de consorcio)?
  C  contexto de N: MacLaren 2022 e Smith 2023 dizem que o ganho da diversificacao e maior com pouco N. Quanto o
     semiarido aduba (Censo 2017)?
  D  extensao do teste v3 (rotacao declarada x perda de milho/feijao 2012-2016), agora estratificado pela CHUVA MEDIA
     ANUAL (o modulador de Bowles), com controles.
Uso: python -I v4_ecologo_diversidade_transferencia.py
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 200)
REFM = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")

# ---------------------------------------------------------------- chuva media anual (IMERG, anos completos 1998-2025)
im = pd.read_parquet(DERIV / "ibge_ne_mun_imerg_mensal.parquet")
im["ano"] = im.data.dt.year
anual = im[(im.ano >= 1998) & (im.ano <= 2025)].groupby(["cod_mun", "ano"]).precip_mm.agg(["sum", "count"])
anual = anual[anual["count"] == 12]["sum"].unstack()
MAP = anual.mean(axis=1).rename("map_mm")
R = REFM.join(MAP)

print("=== A. Onde o semiarido cai no gradiente de chuva dos 11 experimentos de Bowles 2020 ===")
print("Bowles: CO 406 mm sem ganho; SD 582 mm ganho so em seca; 664-1.074 mm ganho na maioria dos sitios")
faixas = [0, 406, 582, 664, 1074, 1e9]
rot = ["< 406 (abaixo do sitio mais seco)", "406-582 (CO-SD: sem ganho / so na seca)", "582-664",
       "664-1.074 (faixa com ganho)", "> 1.074 (acima do mais umido)"]
for nome, msk in [("Semiarido 2022", R.semiarido_2022), ("Fora do semiarido (NE)", ~R.semiarido_2022),
                  ("Ceara (todos)", R.uf == "CE")]:
    s = R.loc[msk, "map_mm"].dropna()
    c = pd.cut(s, faixas, labels=rot).value_counts(normalize=True).reindex(rot) * 100
    print(f"\n{nome}: n={len(s)} municipios; mediana {s.median():.0f} mm (p10 {s.quantile(.1):.0f}, "
          f"p90 {s.quantile(.9):.0f})")
    for k, v in c.items():
        print(f"   {k:45s} {v:5.1f}%")

# ---------------------------------------------------------------- B. linha de base da carteira municipal
print("\n=== B. Linha de base: diversidade da carteira de lavouras temporarias (PAM NE, media 2015-2024) ===")
pam = pd.read_parquet(DERIV / "ibge_ne_pam_mun_anual.parquet")
tmp = pam[(pam.tipo == "temporaria") & pam.ano.between(2015, 2024)]
a = tmp.groupby(["cod_mun", "produto"]).area_colhida_ha.mean().unstack().fillna(0)
tot = a.sum(axis=1)
a = a[tot >= 500]  # municipio com lavoura de verdade
p = a.div(a.sum(axis=1), axis=0)
simpson_inv = 1 / (p ** 2).sum(axis=1)
grupos = {"cereal": ["Milho", "Sorgo"], "leguminosa": ["Feijão"], "folha_larga": ["Mandioca", "Algodão herbáceo"]}
fr = sum((p[[c for c in cols if c in p]].sum(axis=1) >= 0.05).astype(int) for cols in grupos.values())
B = pd.DataFrame({"simpson_inv": simpson_inv, "riqueza_funcional": fr,
                  "fr_leg": p.get("Feijão", 0), "fr_milho": p.get("Milho", 0)}).join(R[["semiarido_2022", "uf"]])
for nome, msk in [("Semiarido 2022", B.semiarido_2022), ("Fora do semiarido", ~B.semiarido_2022.astype(bool))]:
    q = B[msk]
    print(f"{nome}: n={len(q)}; Simpson inverso mediana {q.simpson_inv.median():.2f} (p10 {q.simpson_inv.quantile(.1):.2f}, "
          f"p90 {q.simpson_inv.quantile(.9):.2f}); % com Simpson < 1,5 = {100 * (q.simpson_inv < 1.5).mean():.0f}%")
    print(f"   riqueza funcional (grupos com >= 5% da area): "
          f"{(q.riqueza_funcional.value_counts(normalize=True).sort_index() * 100).round(1).to_dict()}")
    print(f"   fracao de area do feijao (leguminosa): mediana {100 * q.fr_leg.median():.0f}%; "
          f"do milho: mediana {100 * q.fr_milho.median():.0f}%")
# milho e feijao andam juntos? (area plantada, por municipio-ano, semiarido) -> sinal de consorcio
mf = pam[pam.produto.isin(["Milho", "Feijão"]) & pam.ano.between(1990, 2024)]
mf = mf.pivot_table(index=["cod_mun", "ano"], columns="produto", values="area_plantada_ha").dropna()
mf = mf[(mf.Milho > 50) & (mf["Feijão"] > 50)].join(R[["semiarido_2022"]], on="cod_mun")
sa = mf[mf.semiarido_2022]
r_cross, _ = stats.spearmanr(np.log(sa.Milho), np.log(sa["Feijão"]))
# dentro do municipio: variacao anual de log-area (tira o nivel de cada municipio)
dl = sa.groupby(level=0)[["Milho", "Feijão"]].transform(lambda s: np.log(s).diff()).dropna()
r_within, _ = stats.spearmanr(dl.Milho, dl["Feijão"])
razao = (sa["Feijão"] / sa.Milho)
print(f"Semiarido, municipio-ano 1990-2024 (n={len(sa)}): Spearman log(area milho) x log(area feijao) = {r_cross:+.2f}; "
      f"variacao anual dentro do municipio = {r_within:+.2f}; razao feijao/milho mediana {razao.median():.2f} "
      f"(p25 {razao.quantile(.25):.2f}, p75 {razao.quantile(.75):.2f})")

# ---------------------------------------------------------------- C. contexto de N (Censo 2017)
print("\n=== C. Contexto de N: uso de adubo e rotacao declarada (Censo Agro 2017) ===")
c = pd.read_parquet(DERIV / "ibge_ne_censo2017_praticas_mun.parquet").set_index("cod_mun").join(R[["semiarido_2022", "uf", "map_mm"]])
for nome, msk in [("Semiarido 2022", c.semiarido_2022.astype(bool)), ("Fora do semiarido", ~c.semiarido_2022.astype(bool)),
                  ("Ceara", c.uf == "CE")]:
    q = c[msk]
    w = q.n_estab
    print(f"{nome}: n={len(q)} mun.; % estab. que adubam (media ponderada) {np.average(q.pct_adubacao.fillna(0), weights=w):.1f}%; "
          f"so organica {np.average(q.pct_adubacao_organica_so.fillna(0), weights=w):.1f}%; "
          f"% com rotacao {np.average(q.pct_rotacao.fillna(0), weights=w):.1f}%; "
          f"% rotacao nas lav. temporarias {np.nanmedian(q.pct_rotacao_lavtemp):.1f}% (mediana mun.)")

# ---------------------------------------------------------------- D. v3 estratificado por chuva media anual
print("\n=== D. Rotacao declarada (Censo 2017) x perda na seca 2012-2016, por faixa de chuva media anual ===")
arq = DADOS / "ibge_nordeste" / "teste_rotacao_seca.parquet"  # gerado por v3_ibge_testes_nasa.py rotacao
if not arq.exists():
    print("  (arquivo da v3 ausente: rode v3_ibge_testes_nasa.py rotacao)")
else:
    T = pd.read_parquet(arq).join(MAP)


    def pcorr(df, x, y, ctrl):
        d = df[[x, y] + ctrl].dropna()
        rk = d.rank()
        if ctrl:
            Z = np.column_stack([np.ones(len(rk))] + [rk[k] for k in ctrl])
            rx = rk[x] - Z @ np.linalg.lstsq(Z, rk[x], rcond=None)[0]
            ry = rk[y] - Z @ np.linalg.lstsq(Z, rk[y], rcond=None)[0]
        else:
            rx, ry = rk[x], rk[y]
        r, pv = stats.pearsonr(rx, ry)
        return r, pv, len(d)


    ctrl = ["chuva_2012_16_pct", "pct_irrigacao", "pct_orientacao_tecnica", "pct_familiar", "uf_cod"]
    for cult in ("Milho", "Feijão"):
        col = f"razao_{cult}"
        print(f"-- {cult}")
        for nome, lo, hi in [("< 600 mm", 0, 600), ("600-800 mm", 600, 800), ("800-1.074 mm", 800, 1074),
                             ("> 1.074 mm", 1074, 1e9)]:
            q = T[(T.map_mm >= lo) & (T.map_mm < hi)]
            r, pv, n = pcorr(q, "pct_rotacao", col, ctrl)
            dq = q.dropna(subset=[col, "pct_rotacao"])
            if len(dq) >= 30:
                hi_rot = dq[dq.pct_rotacao >= dq.pct_rotacao.quantile(2 / 3)][col].median()
                lo_rot = dq[dq.pct_rotacao <= dq.pct_rotacao.quantile(1 / 3)][col].median()
                extra = f"; razao mediana tercil alto {hi_rot:.2f} x baixo {lo_rot:.2f}"
            else:
                extra = ""
            print(f"   {nome:14s} n={n:4d}  parcial(% rotacao, razao | {'+'.join(ctrl)}) = {r:+.2f} (p={pv:.2g}){extra}")
