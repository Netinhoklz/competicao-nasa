"""Estrategista - Analise 2: curva de antecedencia do alerta de quebra de safra por municipio (IMERG diario + oceano).

Pergunta: em que data da estacao os dados NASA ja separam os municipios-ano que vao perder mais da metade do
milho/feijao? Quanto cada mes de satelite acrescenta (31/jan, 28/fev, 31/mar, 30/abr, 31/mai)?
E, nos municipios-ano alertados em 28/fev, como se sairam milho, feijao e mandioca (a cultura-tampao)?

Dados: E:/campeonato-nasa/dados/imerg/imerg_ce_diario_*.nc (IMERG V07 via POWER, 0,1 grau, 1998-2026),
referencia/ceara_municipios.geojson, derivados/ibge_pam_mun_anual.parquet, derivados/indices_clima_mensal.parquet,
derivados/srtm_municipios_ce.parquet.
Modelo: HistGradientBoosting (e logistica de referencia), validacao deixando 1 ANO inteiro de fora (todos os
municipios daquele ano saem juntos), AUC e Brier skill contra a taxa base.
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from shapely.geometry import Point
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, brier_score_loss
from comum import DADOS, DERIV, REF

pd.set_option("display.width", 220)
AQUI = Path(__file__).parent
CACHE = AQUI / "estrategista_cache_chuva_mun_diaria.parquet"

# ---------------- 1) chuva diaria por municipio
if CACHE.exists():
    chuva = pd.read_parquet(CACHE)
else:
    mun = gpd.read_file(REF / "ceara_municipios.geojson")
    ds0 = xr.open_dataset(DADOS / "imerg" / "imerg_ce_diario_2000.nc")
    lats, lons = ds0.lat.values, ds0.lon.values
    LO, LA = np.meshgrid(lons, lats)
    pts = gpd.GeoDataFrame({"i": np.arange(LO.size)}, geometry=[Point(x, y) for x, y in zip(LO.ravel(), LA.ravel())], crs=mun.crs)
    j = gpd.sjoin(pts, mun[["codarea", "geometry"]], predicate="within")
    membros = j.groupby("codarea")["i"].apply(list).to_dict()
    for _, r in mun.iterrows():  # municipio pequeno sem centro de celula: celula mais proxima do centroide
        if r.codarea not in membros:
            c = r.geometry.centroid
            membros[r.codarea] = [int(np.argmin((LO.ravel() - c.x) ** 2 + (LA.ravel() - c.y) ** 2))]
    print("municipios:", len(membros), " com 1 celula so:", sum(len(v) == 1 for v in membros.values()))
    partes = []
    for f in sorted((DADOS / "imerg").glob("imerg_ce_diario_*.nc")):
        ds = xr.open_dataset(f)
        P = ds["precip"].values.reshape(ds.sizes["time"], -1)
        P = np.where(P < 0, np.nan, P)
        df = pd.DataFrame({cod: np.nanmean(P[:, idx], axis=1) for cod, idx in membros.items()}, index=pd.to_datetime(ds.time.values))
        partes.append(df)
    chuva = pd.concat(partes).sort_index()
    chuva.columns = chuva.columns.astype(str)
    chuva.to_parquet(CACHE)
print("chuva diaria municipal:", chuva.shape, chuva.index.min().date(), chuva.index.max().date())

# ---------------- 2) atributos por municipio-ano e data de corte
CORTES = {"31/jan": (1, 31), "28/fev": (2, 28), "31/mar": (3, 31), "30/abr": (4, 30), "31/mai": (5, 31)}


def maior_seca(x, lim=2.0):
    best = cur = 0
    for v in x:
        cur = cur + 1 if v <= lim else 0
        best = max(best, cur)
    return best


def dias_veranico(x, lim=2.0, minimo=5):
    tot = cur = 0
    for v in x:
        if v <= lim:
            cur += 1
        else:
            if cur >= minimo:
                tot += cur
            cur = 0
    if cur >= minimo:
        tot += cur
    return tot


def inicio(x, limiar=25.0):
    s3 = pd.Series(x).rolling(3).sum().values
    k = np.where(s3 >= limiar)[0]
    return int(k[0]) + 1 if len(k) else len(x) + 1  # dia do ano (censurado no corte)


ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
ind["data"] = pd.to_datetime(ind.data)
I = ind.pivot_table(index="data", columns="variavel", values="valor")


def ondj(col, ano):
    v = I[col].reindex([pd.Timestamp(ano - 1, 10, 1), pd.Timestamp(ano - 1, 11, 1), pd.Timestamp(ano - 1, 12, 1), pd.Timestamp(ano, 1, 1)])
    return v.mean()


anos = [a for a in range(1998, 2026)]
oce = pd.DataFrame({"ONI_ondj": {a: ondj("ONI", a) for a in anos}, "DIP_ondj": {a: ondj("DIPOLO_TNA_menos_TSA", a) for a in anos}})

linhas = []
for a in anos:
    for nome, (mm, dd) in CORTES.items():
        bloco = chuva.loc[f"{a}-01-01":f"{a}-{mm:02d}-{dd:02d}"]
        fev = chuva.loc[f"{a}-02-01":f"{a}-{mm:02d}-{dd:02d}"] if mm >= 2 else bloco
        for cod in chuva.columns:
            x = bloco[cod].values
            xf = fev[cod].values
            linhas.append({"ano": a, "corte": nome, "cod": cod, "P_acum": np.nansum(x), "dias_chuva": int((xf >= 1).sum()),
                           "maior_seca": maior_seca(xf), "dias_veranico5": dias_veranico(xf), "inicio_doy": inicio(x)})
F = pd.DataFrame(linhas)
# anomalia relativa a mediana municipal do mesmo corte (mediana de 28 anos; vazamento desprezivel)
F["P_razao"] = F.P_acum / F.groupby(["corte", "cod"]).P_acum.transform("median").clip(lower=1)
F = F.merge(oce, left_on="ano", right_index=True)
srtm = pd.read_parquet(DERIV / "srtm_municipios_ce.parquet")[["codarea", "elev_media", "decl_media_graus"]]
srtm["cod"] = srtm.codarea.astype(str)
F = F.merge(srtm.drop(columns="codarea"), on="cod", how="left")
clim = chuva[chuva.index.month.isin([2, 3, 4, 5])]
clim = clim.groupby(clim.index.year).sum().loc[1998:2025].mean().rename("fmam_clim").reset_index().rename(columns={"index": "cod"})
F = F.merge(clim, on="cod")

# ---------------- 3) alvos: rendimento municipal / mediana municipal
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[(pam.ano >= 1998) & (pam.ano <= 2025)]
pam["cod"] = pam.cod_local.astype(str)
alvos = {}
for nome, pref in [("milho", "Milho (em"), ("feijao", "Feij"), ("mandioca", "Mandioca")]:
    q = pam[pam.produto.str.startswith(pref) & (pam.area_colhida_ha >= 100) & (pam.rendimento_kg_ha > 0)][["cod", "ano", "rendimento_kg_ha"]]
    q["razao"] = q.rendimento_kg_ha / q.groupby("cod").rendimento_kg_ha.transform("median")
    alvos[nome] = q.set_index(["cod", "ano"]).razao
Y = pd.DataFrame(alvos).reset_index()
print("municipio-ano com milho:", Y.milho.notna().sum(), "| feijao:", Y.feijao.notna().sum(), "| mandioca:", Y.mandioca.notna().sum())
for c in ["milho", "feijao", "mandioca"]:
    print(f"  taxa de quebra (<50% da mediana) {c}: {(Y[c] < 0.5).mean():.1%}")
print("Correlacao entre culturas (razoes municipio-ano, Spearman):")
print(Y[["milho", "feijao", "mandioca"]].corr(method="spearman").round(2).to_string())

FEATS = ["P_acum", "P_razao", "dias_chuva", "maior_seca", "dias_veranico5", "inicio_doy", "ONI_ondj", "DIP_ondj",
         "elev_media", "decl_media_graus", "fmam_clim"]

resultados = []
preds_fev = None
for alvo in ["milho", "feijao"]:
    for corte in CORTES:
        d = F[F.corte == corte].merge(Y[["cod", "ano", alvo]], on=["cod", "ano"]).dropna(subset=[alvo])
        y = (d[alvo] < 0.5).astype(int).values
        p_gb = np.zeros(len(d))
        p_lr = np.zeros(len(d))
        for a in anos:
            te = (d.ano == a).values
            if te.sum() == 0:
                continue
            gb = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_depth=3, l2_regularization=1.0, random_state=0)
            gb.fit(d.loc[~te, FEATS], y[~te])
            p_gb[te] = gb.predict_proba(d.loc[te, FEATS])[:, 1]
            lr = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=2000))
            lr.fit(d.loc[~te, FEATS], y[~te])
            p_lr[te] = lr.predict_proba(d.loc[te, FEATS])[:, 1]
        base = brier_score_loss(y, np.full(len(y), y.mean()))
        resultados.append({"alvo": alvo, "corte": corte, "n": len(d), "taxa_quebra": y.mean(),
                           "AUC_GB": roc_auc_score(y, p_gb), "BSS_GB": 1 - brier_score_loss(y, p_gb) / base,
                           "AUC_logist": roc_auc_score(y, p_lr), "BSS_logist": 1 - brier_score_loss(y, p_lr) / base})
        if alvo == "milho" and corte == "28/fev":
            preds_fev = d.assign(p=p_gb, quebra=y)
R = pd.DataFrame(resultados)
print("\n=== Curva de antecedencia (LOYO por ano; quebra = rendimento < 50% da mediana municipal) ===")
print(R.round(3).to_string(index=False))

# somente oceano (sem satelite) para comparar
for alvo in ["milho"]:
    d = F[F.corte == "31/jan"].merge(Y[["cod", "ano", alvo]], on=["cod", "ano"]).dropna(subset=[alvo])
    y = (d[alvo] < 0.5).astype(int).values
    p = np.zeros(len(d))
    for a in anos:
        te = (d.ano == a).values
        lr = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=2000)).fit(d.loc[~te, ["ONI_ondj", "DIP_ondj"]], y[~te])
        p[te] = lr.predict_proba(d.loc[te, ["ONI_ondj", "DIP_ondj"]])[:, 1]
    print(f"\nSo oceano (ONI+dipolo out-jan), milho: AUC={roc_auc_score(y, p):.3f}")

# ---------------- 4) o que acontece nos alertados de 28/fev
pf = preds_fev.merge(Y[["cod", "ano", "feijao", "mandioca"]], on=["cod", "ano"], how="left")
alerta = pf.p >= 0.5
print(f"\nAlertas em 28/fev (p>=0.5): {alerta.sum()} municipio-ano de {len(pf)}; precisao={pf.quebra[alerta].mean():.0%}; "
      f"recall={pf.quebra[alerta].sum() / pf.quebra.sum():.0%}")
comp = pd.DataFrame({
    "alertados": [pf.loc[alerta, "milho"].median(), pf.loc[alerta, "feijao"].median(), pf.loc[alerta, "mandioca"].median()],
    "nao_alertados": [pf.loc[~alerta, "milho"].median(), pf.loc[~alerta, "feijao"].median(), pf.loc[~alerta, "mandioca"].median()]},
    index=["milho", "feijao", "mandioca"])
print("Rendimento mediano (razao da mediana municipal):")
print(comp.round(2).to_string())
for a in [2012, 2016, 2019, 2024]:
    s = pf[pf.ano == a]
    if len(s):
        print(f"  {a}: municipios={len(s)}, quebras reais={s.quebra.sum()}, alertados={int((s.p >= 0.5).sum())}, "
              f"acertos={int(((s.p >= 0.5) & (s.quebra == 1)).sum())}, p_medio={s.p.mean():.2f}")

# ---------------- 5) 2026 ate onde ha dado diario (IMERG via POWER ate 14/09/2026)
F26 = []
for nome, (mm, dd) in CORTES.items():
    bloco = chuva.loc[f"2026-01-01":f"2026-{mm:02d}-{dd:02d}"]
    F26.append({"corte": nome, "P_acum_CE_media": bloco.sum().mean(), "P_razao_CE": (bloco.sum() / F[(F.corte == nome)].groupby("cod").P_acum.median()).median()})
print("\n2026 (validacao do ano corrente, fora do treino):")
print(pd.DataFrame(F26).round(2).to_string(index=False))
R.to_csv(AQUI / "estrategista_curva_antecedencia.csv", index=False)

# ---------------- 6) o caso 2012 e 2016 por data de corte (logistica, LOYO)
print("\n=== Anos-caso por data de corte (logistica LOYO; alerta = p >= 2x taxa base) ===")
for corte in CORTES:
    d = F[F.corte == corte].merge(Y[["cod", "ano", "milho"]], on=["cod", "ano"]).dropna(subset=["milho"])
    y = (d.milho < 0.5).astype(int).values
    p = np.zeros(len(d))
    for a in anos:
        te = (d.ano == a).values
        lr = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=2000)).fit(d.loc[~te, FEATS], y[~te])
        p[te] = lr.predict_proba(d.loc[te, FEATS])[:, 1]
    lim = 2 * y.mean()
    al = p >= lim
    txt = [f"{corte}: precisao={y[al].mean():.0%} recall={y[al].sum() / y.sum():.0%}"]
    for a in [2012, 2016, 2024]:
        s = d.ano.values == a
        txt.append(f"{a} quebras={y[s].sum()} alertados={al[s].sum()} acertos={(al & (y == 1))[s].sum()}")
    print(" | ".join(txt))
