"""v4 - Especialista em leguminosas antecessoras: testes rapidos.

A) Em que faixa de chuva dos artigos cai cada municipio do semiarido NE
   (Franke 2017: <700 / 700-1200 / >1200 mm; Mudare 2025 Source Data: <500 / 500-1000 / >1000 mm),
   com IMERG anual medio 1998-2024 (tabela municipal ibge_ne_mun_imerg_mensal).
B) Nivel de rendimento do milho e do feijao (PAM NE 2000-2024) e fracao de safras perdidas
   por faixa. As meta-analises (Zhao 2022) excluem observacoes com rendimento zero.
C) Source Data do Mudare 2025 (observacao a observacao): leguminosa -> milho/sorgo/milheto
   nos tropicos com pouco N, contra o resto.
D) Censo 2017: quanto da rotacao ja e praticada no semiarido, por faixa de chuva.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I v4_leguminosas_antecessoras_testes.py <source_data_mudare2025.xlsx>
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)
RNG = np.random.default_rng(42)

# ---------------------------------------------------------------- A) chuva
ref = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet")
semi = ref.loc[ref["semiarido_2022"], ["cod_mun", "uf"]].copy()

im = pd.read_parquet(DERIV / "ibge_ne_mun_imerg_mensal.parquet", columns=["data", "cod_mun", "precip_mm"])
im["ano"] = im["data"].dt.year
im = im[(im["ano"] >= 1998) & (im["ano"] <= 2024)]
cont = im.groupby(["cod_mun", "ano"])["precip_mm"].agg(["sum", "count"]).reset_index()
cont = cont[cont["count"] == 12]
pmed = cont.groupby("cod_mun")["sum"].mean().rename("map_mm")
semi = semi.merge(pmed, left_on="cod_mun", right_index=True, how="left")

semi["faixa_franke"] = pd.cut(semi["map_mm"], [0, 700, 1200, 1e5],
                              labels=["<700 (sudano-saheliana)", "700-1200 (savana da Guine)", ">1200 (umida)"])
semi["faixa_mudare"] = pd.cut(semi["map_mm"], [0, 500, 1000, 1e5], labels=["<500", "500-1000", ">1000"])

print("=" * 90)
print("A) Municipios do semiarido NE (delimitacao 2022) por faixa de chuva media IMERG 1998-2024")
print(f"   n municipios = {len(semi)}; chuva media: mediana {semi['map_mm'].median():.0f} mm, "
      f"P10 {semi['map_mm'].quantile(.1):.0f}, P90 {semi['map_mm'].quantile(.9):.0f}")
print(semi["faixa_franke"].value_counts(sort=False).to_string())
print(semi["faixa_mudare"].value_counts(sort=False).to_string())
ce = semi[semi["uf"] == "CE"]
print(f"   so Ceara (semiarido): n={len(ce)}")
print(ce["faixa_franke"].value_counts(sort=False).to_string())

# ---------------------------------------------------------------- B) PAM
pam = pd.read_parquet(DERIV / "ibge_ne_pam_mun_anual.parquet")
pam = pam[(pam["ano"] >= 2000) & (pam["ano"] <= 2024)]
prods = pam["produto"].unique().tolist()
p_milho = [p for p in prods if p.startswith("Milho")]
p_feijao = [p for p in prods if p.startswith("Feij")]
print("\nB) produtos usados:", p_milho, p_feijao)


def resumo(prod_lista, rotulo):
    d = pam[pam["produto"].isin(prod_lista)].copy()
    d = d[d["cod_mun"].isin(semi["cod_mun"])]
    d = d[(d["area_plantada_ha"] > 0)]
    d["perda"] = (d["area_colhida_ha"].fillna(0) / d["area_plantada_ha"] < 0.5) | (d["producao_t"].fillna(0) <= 0)
    d = d.merge(semi[["cod_mun", "faixa_franke"]], on="cod_mun")
    colh = d[~d["perda"] & (d["rendimento_kg_ha"] > 0)]
    out = []
    for f, g in d.groupby("faixa_franke", observed=True):
        gc = colh[colh["faixa_franke"] == f]
        out.append({"faixa": f, "mun_anos": len(g), "pct_safra_perdida": 100 * g["perda"].mean(),
                    "rend_mediano_colhido_kg_ha": gc["rendimento_kg_ha"].median(),
                    "rend_P75": gc["rendimento_kg_ha"].quantile(.75)})
    o = pd.DataFrame(out)
    print(f"\n   {rotulo} - semiarido NE 2000-2024 (perda = colhida/plantada < 0,5 ou producao 0)")
    print(o.round(1).to_string(index=False))
    tot = d["perda"].mean() * 100
    print(f"   total: {len(d)} municipio-anos; {tot:.1f}% com safra perdida; "
          f"rendimento mediano dos anos colhidos {colh['rendimento_kg_ha'].median():.0f} kg/ha")
    return d


dm = resumo(p_milho, "MILHO")
df_ = resumo(p_feijao, "FEIJAO (inclui caupi)")
print("   Referencias do Franke 2017, Tabela 3 (cereal continuo): media geral 1,20 t/ha; milho 1,96; "
      "sudano-saheliana 1,16; milheto 1,11; sorgo 1,06.")

# ---------------------------------------------------------------- C) Source Data Mudare 2025
if len(sys.argv) > 1:
    f = sys.argv[1]
    s2 = pd.read_excel(f, sheet_name="Supplementary Figure S2", header=2)
    f1 = pd.read_excel(f, sheet_name="Figure 1a-d", header=3).iloc[:, :5]
    alinhado = (len(s2) == len(f1)) and (s2["Study"].values == f1["StudyID"].values).all() \
        and (s2["Category"].values == f1["Category"].values).all()
    print("\n" + "=" * 90)
    print(f"C) Mudare 2025 Source Data: {len(s2)} observacoes; abas S2 e Fig.1 alinhadas linha a linha = {alinhado}")
    if alinhado:
        d = pd.concat([s2, f1[["Lat", "Lon"]]], axis=1)
        d["NFR_Main"] = pd.to_numeric(d["NFR_Main"], errors="coerce")
        d["lnR"] = pd.to_numeric(d["Effect size"], errors="coerce")
        d = d.dropna(subset=["lnR"])
        d["tropico"] = d["Lat"].abs() <= 23.5
        cer = d["MainCrop"].isin(["Maize", "Sorghum", "Millet"])

        def boot_estudo(g, nb=2000):
            # media nao ponderada; bootstrap por estudo (aglomerado)
            est = g.groupby("Study")["lnR"].apply(np.array).tolist()
            if len(est) < 3:
                return np.nan, np.nan, np.nan
            m = np.mean(np.concatenate(est))
            bs = []
            for _ in range(nb):
                idx = RNG.integers(0, len(est), len(est))
                bs.append(np.mean(np.concatenate([est[i] for i in idx])))
            lo, hi = np.percentile(bs, [2.5, 97.5])
            return m, lo, hi

        linhas = []
        grupos = {
            "Leguminosa -> milho/sorgo/milheto, tropico, N <= 60": (d["Category"] == "Legume") & cer & d["tropico"] & (d["NFR_Main"] <= 60),
            "Leguminosa -> milho/sorgo/milheto, tropico, N > 60": (d["Category"] == "Legume") & cer & d["tropico"] & (d["NFR_Main"] > 60),
            "Leguminosa -> milho/sorgo/milheto, fora do tropico": (d["Category"] == "Legume") & cer & ~d["tropico"],
            "Nao leguminosa -> milho/sorgo/milheto, tropico": (d["Category"] == "Non-legume") & cer & d["tropico"],
            "Nao leguminosa -> milho/sorgo/milheto, fora do tropico": (d["Category"] == "Non-legume") & cer & ~d["tropico"],
        }
        for nome, msk in grupos.items():
            g = d[msk]
            m, lo, hi = boot_estudo(g)
            linhas.append({"grupo": nome, "obs": len(g), "estudos": g["Study"].nunique(),
                           "efeito_%": 100 * (np.exp(m) - 1), "IC95_lo_%": 100 * (np.exp(lo) - 1),
                           "IC95_hi_%": 100 * (np.exp(hi) - 1)})
        print("   media NAO ponderada de lnR, IC por bootstrap de estudos (2000 reamostras); NAO e o modelo misto do artigo")
        print(pd.DataFrame(linhas).round(1).to_string(index=False))
        print("   categorias de 'Category':", d["Category"].value_counts().to_dict())
        print("   paises/faixas tropicais: lat-lon distintos no grupo 1:",
              d[list(grupos.values())[0]][["Lat", "Lon"]].drop_duplicates().round(1).values.tolist()[:25])

# ---------------------------------------------------------------- D) Censo 2017
cen = pd.read_parquet(DERIV / "ibge_ne_censo2017_praticas_mun.parquet")
cen = cen.merge(semi[["cod_mun", "faixa_franke", "uf"]], on="cod_mun")
print("\n" + "=" * 90)
print("D) Censo 2017, semiarido NE: % dos estabelecimentos com lavoura temporaria que declaram rotacao")
g = cen.groupby("faixa_franke", observed=True)["pct_rotacao_lavtemp"].describe(percentiles=[.25, .5, .75])
print(g[["count", "25%", "50%", "75%"]].round(1).to_string())
w = (cen["pct_rotacao_lavtemp"] * cen["n_estab_lavtemp"]).sum() / cen["n_estab_lavtemp"].sum()
print(f"   ponderado por estabelecimentos: {w:.1f}% declaram rotacao")
cce = cen[cen["uf"] == "CE"]
wce = (cce["pct_rotacao_lavtemp"] * cce["n_estab_lavtemp"]).sum() / cce["n_estab_lavtemp"].sum()
print(f"   so Ceara: {wce:.1f}%  (mediana municipal {cce['pct_rotacao_lavtemp'].median():.1f}%)")

# correlacao ecologica (D): rotacao declarada x rendimento mediano do milho 2015-2019, por faixa
mm = dm[(dm["ano"].between(2015, 2019)) & ~dm["perda"] & (dm["rendimento_kg_ha"] > 0)]
mm = mm.groupby("cod_mun")["rendimento_kg_ha"].median().rename("rend_milho_1519")
cc = cen.merge(mm, left_on="cod_mun", right_index=True).dropna(subset=["pct_rotacao_lavtemp", "rend_milho_1519"])
print("   correlacao de Spearman (ecologica, NAO causal) rotacao declarada x rendimento do milho 2015-2019:")
for f_, gg in cc.groupby("faixa_franke", observed=True):
    if len(gg) > 20:
        r = gg[["pct_rotacao_lavtemp", "rend_milho_1519"]].corr(method="spearman").iloc[0, 1]
        print(f"     {f_}: rho = {r:+.2f} (n = {len(gg)})")

# ---------------------------------------------------------------- E) LGP do GAEZ no Ceara
# Franke 2017 define a zona sudano-saheliana por <700 mm E <150 dias de crescimento.
lgp = pd.read_parquet(DERIV / "gaez_ce_lgp_chuva_anual_1960_2010.parquet")
x, y = lgp["LGP (dias)"], lgp["chuva (mm)"]
print("\n" + "=" * 90)
print("E) GAEZ, media espacial do Ceara, 1960-2010 (criterio de dias de crescimento do Franke)")
print(f"   LGP: mediana {x.median():.0f} dias (P10 {x.quantile(.1):.0f}, P90 {x.quantile(.9):.0f}); "
      f"anos com LGP < 150: {(x < 150).sum()} de {len(x)}")
print(f"   chuva: media {y.mean():.0f} mm; anos < 700 mm: {(y < 700).sum()}; "
      f"anos com 700-1200 mm mas LGP < 150: {((y >= 700) & (y < 1200) & (x < 150)).sum()}")

# ---------------------------------------------------------------- F) sequencia inteira com o PAM
# Mudare 2025 (Fig. 3e, Source Data): soja->milho contra milho continuo perde energia e receita na
# sequencia inteira. Aqui: 2 anos de milho contra 1 ano de feijao + 1 ano de milho com bonus e,
# usando massa e receita por hectare PLANTADO (inclui perdas) do mesmo municipio-ano. Proxy grosseiro:
# PAM nao sabe a sequencia real e o feijao do PAM soma todos os tipos.
print("\n" + "=" * 90)
print("F) Sequencia inteira (2 anos), semiarido NE 2010-2024, por municipio-ano com milho e feijao plantados")
k = ["cod_mun", "ano"]
a = dm[dm["ano"] >= 2010][k + ["area_plantada_ha", "producao_t", "valor_mil_moeda"]].rename(
    columns={"area_plantada_ha": "ap_m", "producao_t": "p_m", "valor_mil_moeda": "v_m"})
b = df_[df_["ano"] >= 2010][k + ["area_plantada_ha", "producao_t", "valor_mil_moeda"]].rename(
    columns={"area_plantada_ha": "ap_f", "producao_t": "p_f", "valor_mil_moeda": "v_f"})
s = a.merge(b, on=k).merge(semi[["cod_mun", "faixa_franke"]], on="cod_mun")
s = s[(s["ap_m"] > 0) & (s["ap_f"] > 0)].copy()
s["kg_m"] = 1000 * s["p_m"].fillna(0) / s["ap_m"]
s["kg_f"] = 1000 * s["p_f"].fillna(0) / s["ap_f"]
s["rs_m"] = 1000 * s["v_m"].fillna(0) / s["ap_m"]
s["rs_f"] = 1000 * s["v_f"].fillna(0) / s["ap_f"]
s = s[(s["rs_m"] > 0)]
print(f"   municipio-anos: {len(s)}; preco implicito mediano feijao/milho (R$/kg): "
      f"{np.nanmedian((s['rs_f'] / s['kg_f'].replace(0, np.nan)) / (s['rs_m'] / s['kg_m'].replace(0, np.nan))):.2f}x")
for e, rot in [(0.0, "sem bonus"), (0.147, "+14,7% (Mudare 2025, caupi->milho)"),
               (0.24, "+24% (Franke 2017, sudano-saheliana, ns)"), (0.287, "+28,7% (Zhao 2022, caupi)")]:
    rm = (s["kg_f"] + s["kg_m"] * (1 + e)) / (2 * s["kg_m"].replace(0, np.nan))
    rr = (s["rs_f"] + s["rs_m"] * (1 + e)) / (2 * s["rs_m"])
    print(f"   bonus {rot:42s}: massa da sequencia/milho-milho mediana {np.nanmedian(rm):.2f}; "
          f"receita mediana {np.nanmedian(rr):.2f}; receita > milho-milho em {100 * np.nanmean(rr > 1):.0f}% dos municipio-anos")
for f_, g in s.groupby("faixa_franke", observed=True):
    rr = (g["rs_f"] + g["rs_m"] * 1.147) / (2 * g["rs_m"])
    print(f"     faixa {f_}: receita mediana (bonus 14,7%) {np.nanmedian(rr):.2f} (n = {len(g)})")
