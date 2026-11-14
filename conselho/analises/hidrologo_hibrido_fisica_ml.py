"""Hidrólogo — análise 3: o balanço FAO-56 acrescenta habilidade a um modelo de ML só com chuva? (híbrido física + ML)

Alvo: desvio do rendimento municipal (IBGE PAM, por área plantada, sem tendência) de milho e feijão, 1999–2025.
Conjuntos de atributos:
  A = só chuva IMERG (total fev–mai, totais mensais jan–jun, maior veranico de fev–mai, nº de veranicos >= 3 dias com <= 2 mm,
      definição de Rocha et al. 2021);
  B = só estados do balde FAO-56 (ISNA, ISNA na floração, dia do semeio, percolação, escoamento, água que sobra);
  A+B = híbrido.
Modelo: HistGradientBoosting (sklearn), validação deixando UM ANO inteiro de fora (sem vazamento temporal entre municípios).
Métricas: Spearman OOF, AUC para quebra >= 50%, e a mesma coisa por ano (habilidade espacial dentro do ano).
Entrada do balde: saidas/hidrologo_fao56_mun_ano.parquet (análise 1).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import shapely
import xarray as xr
from scipy import stats
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
SAIDA = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")

im = xr.concat([xr.open_dataset(DADOS / "imerg" / f"imerg_ce_diario_{a}.nc")["precip"] for a in range(1998, 2027)], "time")
mun = municipios_ce_gdf(); mun["cod"] = mun.codarea.astype(int)
lo, la = np.meshgrid(im.lon.values, im.lat.values)
W = np.zeros((len(mun), lo.size), dtype=np.float32)
for i, geom in enumerate(mun.geometry):
    m = shapely.contains_xy(geom, lo.ravel(), la.ravel())
    if m.sum() == 0:
        c = geom.centroid; m = np.zeros(lo.size, bool); m[np.argmin((lo.ravel() - c.x) ** 2 + (la.ravel() - c.y) ** 2)] = True
    W[i, m] = 1.0 / m.sum()
P = pd.DataFrame(np.nan_to_num(im.where(im >= 0).values.reshape(im.sizes["time"], -1)) @ W.T, index=pd.DatetimeIndex(im.time.values),
                 columns=mun.cod.values)

feat = []
for ano in range(1999, 2026):
    x = P.loc[str(ano)]
    d = {"ano": ano, "cod": P.columns.values}
    for mes in range(1, 7):
        d[f"chuva_m{mes:02d}"] = x[x.index.month == mes].sum().values
    q = x[x.index.month.isin([2, 3, 4, 5])]
    d["chuva_fmam"] = q.sum().values
    seco = (q <= 2.0).values
    maior = np.zeros(seco.shape[1]); nver = np.zeros(seco.shape[1]); run = np.zeros(seco.shape[1])
    for t in range(seco.shape[0]):
        run = np.where(seco[t], run + 1, 0)
        maior = np.maximum(maior, run)
        nver += (run == 3)  # conta cada veranico uma vez, ao atingir 3 dias
    d["maior_veranico"] = maior; d["n_veranicos"] = nver
    feat.append(pd.DataFrame(d))
F = pd.concat(feat)

R = pd.read_parquet(SAIDA / "hidrologo_fao56_mun_ano.parquet")
R = R[R.regra == "chuva"]
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.produto.isin(["Milho (em grão)", "Feijão (em grão)"])].copy()
pam["cultura"] = pam.produto.map({"Milho (em grão)": "milho", "Feijão (em grão)": "feijao"})
pam = pam[(pam.area_plantada_ha >= 200) & (pam.ano >= 1993)]
pam["rend"] = pam.producao_t * 1000 / pam.area_plantada_ha
pam = pam.sort_values(["cod_local", "cultura", "ano"])
pam["desvio"] = pam.rend / pam.groupby(["cod_local", "cultura"]).rend.transform(lambda s: s.rolling(7, center=True, min_periods=3).median()) - 1
pam["cod"] = pam.cod_local.astype(int)

A = ["chuva_fmam"] + [f"chuva_m{m:02d}" for m in range(1, 7)] + ["maior_veranico", "n_veranicos"]
B = ["isna", "isna_flor", "doy_semeio", "dp_mm", "runoff_mm", "agua_sobra_colheita_mm"]
linhas = []
for cult in ["milho", "feijao"]:
    D = (pam[pam.cultura == cult][["cod", "ano", "desvio"]].merge(F, on=["cod", "ano"])
         .merge(R[R.cultura == cult][["cod", "ano"] + B], on=["cod", "ano"]).dropna(subset=["desvio"]))
    D = D[D.desvio.between(-1, 3)]
    print(f"\n=== {cult}: {len(D)} município-anos, {D.ano.nunique()} anos ===")
    print("Spearman simples com o desvio:", {c: round(stats.spearmanr(D[c], D.desvio).correlation, 3) for c in ["chuva_fmam", "maior_veranico", "n_veranicos", "isna", "isna_flor"]})
    sev = (D.desvio <= -0.5).astype(int)
    for nome, cols in [("A só chuva", A), ("B só balde FAO-56", B), ("A+B híbrido", A + B)]:
        oof = np.full(len(D), np.nan)
        for ano in sorted(D.ano.unique()):
            tr, te = D.ano.values != ano, D.ano.values == ano
            m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=40,
                                              l2_regularization=1.0, random_state=0)
            m.fit(D.loc[tr, cols], D.desvio[tr])
            oof[te] = m.predict(D.loc[te, cols])
        D["oof"] = oof
        rho = stats.spearmanr(oof, D.desvio).correlation
        auc = roc_auc_score(sev, -oof)
        dentro = D.groupby("ano").apply(lambda h: stats.spearmanr(h.oof, h.desvio).correlation).mean()
        mae = np.mean(np.abs(oof - D.desvio))
        # ponderado pela área do estado: o ano como um todo
        linhas.append({"cultura": cult, "atributos": nome, "rho_OOF": rho, "rho_dentro_do_ano": dentro, "AUC_quebra50": auc, "MAE": mae})
        print(f"  {nome:20s} rho OOF {rho:.3f} | rho entre municípios no mesmo ano {dentro:.3f} | AUC quebra>=50% {auc:.3f} | MAE {mae:.3f}")
    # bootstrap por ano do ganho do híbrido sobre "só chuva" (reamostra anos, não linhas)
T = pd.DataFrame(linhas)
T.to_csv(SAIDA / "hidrologo_hibrido_resultados.csv", index=False)

# ---------------------------------------------------------------- variante: ML de baixa capacidade, monotônico (coerente com a física)
print("\n=== Variante monotônica e de baixa capacidade (deixando 1 ano de fora) ===")
from sklearn.isotonic import IsotonicRegression
for cult in ["milho", "feijao"]:
    D = (pam[pam.cultura == cult][["cod", "ano", "desvio"]].merge(F, on=["cod", "ano"])
         .merge(R[R.cultura == cult][["cod", "ano"] + B], on=["cod", "ano"]).dropna(subset=["desvio"]))
    D = D[D.desvio.between(-1, 3)]
    sev = (D.desvio <= -0.5).astype(int)
    variantes = {
        "isotônica(ISNA)": (["isna"], None),
        "isotônica(chuva fmam)": (["chuva_fmam"], None),
        "GBM monotônico ISNA+chuva+veranico": (["isna", "chuva_fmam", "maior_veranico"], [1, 1, -1]),
        "GBM monotônico ISNA+ISNAflor+chuva+veranico": (["isna", "isna_flor", "chuva_fmam", "maior_veranico"], [1, 1, 1, -1]),
    }
    for nome, (cols, mono) in variantes.items():
        oof = np.full(len(D), np.nan)
        for ano in sorted(D.ano.unique()):
            tr, te = D.ano.values != ano, D.ano.values == ano
            if mono is None:
                m = IsotonicRegression(out_of_bounds="clip").fit(D.loc[tr, cols[0]], D.desvio[tr])
                oof[te] = m.predict(D.loc[te, cols[0]])
            else:
                m = HistGradientBoostingRegressor(max_iter=150, learning_rate=0.05, max_depth=2, min_samples_leaf=150,
                                                  monotonic_cst=mono, random_state=0).fit(D.loc[tr, cols], D.desvio[tr])
                oof[te] = m.predict(D.loc[te, cols])
        D["oof"] = oof + 1e-9 * np.random.default_rng(0).standard_normal(len(D))
        rho = stats.spearmanr(D.oof, D.desvio).correlation
        dentro = D.groupby("ano").apply(lambda h: stats.spearmanr(h.oof, h.desvio).correlation).mean()
        print(f"  {cult:7s} {nome:45s} rho OOF {rho:.3f} | dentro do ano {dentro:.3f} | AUC quebra>=50% {roc_auc_score(sev, -D.oof):.3f} | MAE {np.mean(np.abs(D.oof - D.desvio)):.3f}")
