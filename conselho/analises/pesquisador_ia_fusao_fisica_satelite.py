"""Pesquisador de IA, rodada 2: a fusao 'fisica (ISNA FAO-56) + satelite (NDVI relativo)' soma ou se sobrepoe?

Pergunta: tres especialistas propuseram camadas diferentes para o risco de quebra do milho:
  - agronomo/hidrologo: ISNA do balde FAO-56 (IMERG + ET0 POWER) -> fisica;
  - cetico: NDVI do MODIS como desvio RELATIVO dentro do ano (chao) + chuva para o nivel do ano (ceu);
  - estrategista/designer: chuva acumulada como % do normal.
Aqui testamos se ISNA e NDVI relativo sao complementares (o ganho de juntar), com validacao deixando o ANO de fora
e um walk-forward simples (treina so com anos anteriores). NDVI de mar-mai = nowcast (informacao dentro da safra).

Entradas: cetico_painel_milho.parquet (alvo an_lin: anomalia vs tendencia linear por municipio; chuva fmam/nver/cdd),
          saidas/agronomo_isna_mun_ano.parquet (isna_flor_milho, isna_ciclo_milho, estresse_flor_milho),
          MODIS NDVI mensal 0,01 grau (mesma agregacao municipal do cetico).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, REF

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from rasterio import features
from rasterio.transform import from_origin
from scipy import stats
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

AQUI = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"

# --- NDVI municipal mar-mai (mesmo procedimento do cetico_satelite_vs_chuva_local.py) ---
nd = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi
lat, lon = nd.lat.values, nd.lon.values
res = abs(lon[1] - lon[0])
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["codarea"] = mun["codarea"].astype(int)
tr = from_origin(lon.min() - res / 2, lat.max() + res / 2, res, res)
lab = features.rasterize(((g, i + 1) for i, g in enumerate(mun.geometry)), out_shape=(len(lat), len(lon)), transform=tr,
                         fill=0, dtype="int32")
if lat[0] < lat[-1]:
    lab = lab[::-1]
codes = np.r_[0, mun.codarea.values]
ok0 = lab > 0
reg = []
for ano in range(2000, 2026):
    sel = [t for t in [pd.Timestamp(ano, m, 1) for m in (3, 4, 5)] if t in nd.time.values]
    a = nd.sel(time=sel).mean("time").values
    if np.nanmax(a) > 2:
        a = a / 10000.0
    ok = np.isfinite(a) & ok0
    s = np.bincount(lab[ok], weights=a[ok], minlength=len(codes))
    n = np.bincount(lab[ok], minlength=len(codes))
    with np.errstate(invalid="ignore", divide="ignore"):
        m = s / n
    for k in range(1, len(codes)):
        reg.append({"cod": codes[k], "ano": ano, "ndvi": m[k]})
S = pd.DataFrame(reg)

P = pd.read_parquet(AQUI + "cetico_painel_milho.parquet")
I = pd.read_parquet(AQUI + "saidas/agronomo_isna_mun_ano.parquet")[
    ["cod", "ano", "isna_flor_milho", "isna_ciclo_milho", "estresse_flor_milho"]]
P["cod"] = P["cod"].astype(int); I["cod"] = I["cod"].astype(int); P["ano"] = P["ano"].astype(int); I["ano"] = I["ano"].astype(int)
P = P.merge(I, on=["cod", "ano"]).merge(S, on=["cod", "ano"]).dropna(subset=["an_lin", "ndvi", "isna_flor_milho"])
P = P[(P.ano >= 2000) & (P.ano <= 2025)].reset_index(drop=True)
for v in ["ndvi", "fmam", "nver", "cdd", "isna_flor_milho", "isna_ciclo_milho", "estresse_flor_milho"]:
    g = P.groupby("cod")[v]
    P[v + "_a"] = P[v] - (g.transform("sum") - P[v]) / (g.transform("count") - 1)  # anomalia sem o proprio ano
    P[v + "_dev"] = P[v + "_a"] - P.groupby("ano")[v + "_a"].transform("mean")    # desvio local dentro do ano
    P[v + "_ano"] = P.groupby("ano")[v + "_a"].transform("mean")                   # nivel do ano (estado)
y = P.an_lin.clip(-1, 2).values
anos = P.ano.values
q = y <= -0.5
print(f"painel milho: {len(P)} municipio-anos, {P.cod.nunique()} municipios, {P.ano.min()}-{P.ano.max()}; "
      f"quebra<=-50%: {q.mean():.1%}")

# correlacao dentro do ano entre os desvios locais (sobreposicao de informacao)
rr = [stats.spearmanr(P.ndvi_dev[anos == a], P.isna_flor_milho_dev[anos == a]).statistic for a in np.unique(anos)]
print(f"rho dentro do ano entre desvio de NDVI e desvio de ISNA na floracao: {np.nanmean(rr):+.3f}")

conj = {
    "A chuva (fmam,nver,cdd)": ["fmam_a", "nver_a", "cdd_a"],
    "B ISNA (flor,ciclo,estresse)": ["isna_flor_milho_a", "isna_ciclo_milho_a", "estresse_flor_milho_a"],
    "C NDVI": ["ndvi_a"],
    "D ISNA + NDVI": ["isna_flor_milho_a", "isna_ciclo_milho_a", "estresse_flor_milho_a", "ndvi_a"],
    "E chuva + ISNA + NDVI": ["fmam_a", "nver_a", "cdd_a", "isna_flor_milho_a", "isna_ciclo_milho_a",
                              "estresse_flor_milho_a", "ndvi_a"],
    "F duas escalas: ISNA(ano+local) + NDVI so local": ["isna_flor_milho_ano", "isna_ciclo_milho_ano",
                                                         "isna_flor_milho_dev", "isna_ciclo_milho_dev", "ndvi_dev"],
    "G duas escalas: chuva(ano) + NDVI so local": ["fmam_ano", "nver_ano", "ndvi_dev"],
}


def avalia(pred):
    rho = [stats.spearmanr(pred[anos == a], y[anos == a]).statistic for a in np.unique(anos)]
    E = pd.DataFrame({"a": anos, "y": y, "p": pred}).groupby("a").mean()
    return (round(r2_score(y, pred), 3), round(np.nanmean(rho), 3), int(np.sum(np.array(rho) > 0)),
            round(stats.pearsonr(E.p, E.y).statistic, 2), round(roc_auc_score(q, -pred), 3))


def modelo(tipo, ncol):
    if tipo == "ridge":
        return make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13)))
    return HistGradientBoostingRegressor(max_depth=2, max_iter=200, learning_rate=0.05, min_samples_leaf=80,
                                         random_state=0)


tab = []
for nome, cols in conj.items():
    X = P[cols].values
    for tipo in ["ridge", "hgb"]:
        # (1) deixa o ano de fora
        pred = np.zeros(len(P))
        for a in np.unique(anos):
            te = anos == a
            pred[te] = modelo(tipo, len(cols)).fit(X[~te], y[~te]).predict(X[te])
        r2, rho, npos, rest, auc = avalia(pred)
        # (2) walk-forward: so anos anteriores (t >= 2010)
        pw = np.full(len(P), np.nan)
        for a in range(2010, 2026):
            te, trn = anos == a, anos < a
            if te.any():
                pw[te] = modelo(tipo, len(cols)).fit(X[trn], y[trn]).predict(X[te])
        okw = np.isfinite(pw)
        rho_w = [stats.spearmanr(pw[okw & (anos == a)], y[okw & (anos == a)]).statistic for a in range(2010, 2026)]
        Ew = pd.DataFrame({"a": anos[okw], "y": y[okw], "p": pw[okw]}).groupby("a").mean()
        vies2020 = (Ew.p - Ew.y).loc[2020:2025].mean()
        tab.append({"atributos": nome, "modelo": tipo, "R2_LOYO": r2, "rho_dentro_ano": rho, "anos_rho>0": npos,
                    "r_estado": rest, "AUC_quebra": auc,
                    "WF_rho_dentro": round(np.nanmean(rho_w), 3), "WF_r_estado": round(stats.pearsonr(Ew.p, Ew.y).statistic, 2),
                    "WF_vies_2020_25": round(vies2020, 2)})
T = pd.DataFrame(tab)
pd.set_option("display.width", 250)
print(T.to_string(index=False))
T.to_csv(AQUI + "saidas/pesquisador_ia_fusao_fisica_satelite.csv", index=False)

# conformal robusto ao ano para o melhor conjunto (ridge E), cobertura nos anos de seca
X = P[conj["E chuva + ISNA + NDVI"]].values
pred = np.zeros(len(P))
for a in np.unique(anos):
    te = anos == a
    pred[te] = modelo("ridge", 0).fit(X[~te], y[~te]).predict(X[te])
res_abs = np.abs(y - pred)
q80_ano = pd.Series(res_abs).groupby(anos).quantile(0.8)
larg_pad = np.quantile(res_abs, 0.8)
larg_rob = np.quantile(q80_ano.values, 0.8)
cob_pad = pd.Series(res_abs <= larg_pad).groupby(anos).mean()
cob_rob = pd.Series(res_abs <= larg_rob).groupby(anos).mean()
print(f"\nconformal (E ridge): largura 80% padrao +-{larg_pad:.2f}, robusta ao ano +-{larg_rob:.2f}; "
      f"anos com cobertura>=80%: padrao {(cob_pad >= 0.8).mean():.0%}, robusta {(cob_rob >= 0.8).mean():.0%}; "
      f"2012: {cob_pad.get(2012, np.nan):.0%} vs {cob_rob.get(2012, np.nan):.0%}")
