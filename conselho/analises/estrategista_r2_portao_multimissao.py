"""Estrategista, rodada 2: o portão de abril (e de março) melhora ao juntar CHUVA (GPM IMERG) + VEGETAÇÃO (MODIS NDVI)?
Ninguém combinou as duas: o designer/estrategista usaram só chuva (AUC ~0,77-0,80 em 30/abr), o cético só NDVI (0,77 até abr).
Também refaz a minha curva SEM o vazamento que eu mesmo declarei: medianas municipais calculadas sem o ano de teste.

Alvo: milho, rendimento (PAM, área colhida >= 100 ha) / mediana municipal dos OUTROS anos < 0,5. Anos 2000-2025 (MODIS).
Atributos (todos conhecidos na data do portão):
  R   = chuva 1/jan..corte (IMERG, cache municipal) / mediana dos outros anos do município
  N   = NDVI médio fev..mês do corte (MODIS 1 km, média municipal) - média dos outros anos do município
  Nrel= N - média estadual de N no mesmo ano (sinal relativo, imune à deriva comum; ideia do cético)
  ONI = ONI rotulado em dez do ano anterior (NDJ)
Validação: logística, deixa o ANO inteiro de fora. Métrica: AUC e Brier skill contra a taxa-base do treino.
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

AQUI = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
DERIV = r"E:/campeonato-nasa/dados/derivados/"

# ---------- NDVI municipal mensal (mesma rasterização do cético)
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


def media_mun(campo):
    ok = np.isfinite(campo) & (lab > 0)
    s = np.bincount(lab[ok], weights=campo[ok], minlength=len(codes))
    n = np.bincount(lab[ok], minlength=len(codes))
    with np.errstate(invalid="ignore", divide="ignore"):
        return s / n


reg = []
for ano in range(2000, 2026):
    for m in (2, 3, 4):
        t = pd.Timestamp(ano, m, 1)
        if t not in nd.time.values:
            continue
        a = nd.sel(time=t).values
        if np.nanmax(a) > 2:
            a = a / 10000.0
        ma = media_mun(a)
        for k in range(1, len(codes)):
            reg.append({"cod": str(codes[k]), "ano": ano, "mes": m, "ndvi": ma[k]})
S = pd.DataFrame(reg)

# ---------- chuva acumulada
C = pd.read_parquet(AQUI + "estrategista_cache_chuva_mun_diaria.parquet")
C.index = pd.to_datetime(C.index)

# ---------- alvo
pam = pd.read_parquet(DERIV + "ibge_pam_mun_anual.parquet")
pam = pam[(pam.ano >= 1998) & (pam.ano <= 2025)]
pam["cod"] = pam.cod_local.astype(str)
q = pam[pam.produto.str.startswith("Milho (em") & (pam.area_colhida_ha >= 100) & (pam.rendimento_kg_ha > 0)]
q = q.groupby(["cod", "ano"]).rendimento_kg_ha.mean().reset_index()


def mediana_outros(df, col):
    out = np.empty(len(df))
    for cod, idx in df.groupby("cod").groups.items():
        v = df.loc[idx, col].values
        for j, i in enumerate(idx):
            out[df.index.get_loc(i)] = np.nanmedian(np.delete(v, j)) if len(v) > 1 else np.nan
    return out


q = q.reset_index(drop=True)
q["razao"] = q.rendimento_kg_ha / mediana_outros(q, "rendimento_kg_ha")
q["quebra"] = (q.razao < 0.5).astype(int)

ind = pd.read_parquet(DERIV + "indices_clima_mensal.parquet")
oni = ind[ind.variavel == "ONI"].assign(data=lambda d: pd.to_datetime(d.data)).set_index("data").valor
oni_ndj = {a: oni.get(pd.Timestamp(a - 1, 12, 1), np.nan) for a in range(1998, 2027)}

resultados = []
for corte_mes, corte_dia, nome, mes_ndvi in [(3, 31, "31/mar", 3), (4, 30, "30/abr", 4)]:
    linhas = []
    for ano in range(2000, 2026):
        jan1, fim = pd.Timestamp(ano, 1, 1), pd.Timestamp(ano, corte_mes, corte_dia)
        acum = C.loc[jan1:fim].sum()
        for cod, v in acum.items():
            linhas.append({"cod": cod, "ano": ano, "chuva": v})
    R = pd.DataFrame(linhas).reset_index(drop=True)
    R["R"] = R.chuva / mediana_outros(R, "chuva")
    F = S[S.mes.between(2, mes_ndvi)].groupby(["cod", "ano"]).ndvi.mean().reset_index()
    g = F.groupby("cod").ndvi
    F["N"] = F.ndvi - (g.transform("sum") - F.ndvi) / (g.transform("count") - 1)
    F["Nrel"] = F.N - F.groupby("ano").N.transform("mean")
    P = q.merge(R, on=["cod", "ano"]).merge(F, on=["cod", "ano"]).dropna(subset=["razao", "R", "N"])
    P["ONI"] = P.ano.map(oni_ndj)
    P["logR"] = np.log(P.R.clip(0.05, 5))
    y = P.quebra.values
    anos = P.ano.values
    for rot, cols in [("só chuva (R)", ["logR"]), ("só NDVI (N)", ["N"]), ("chuva + NDVI", ["logR", "N"]),
                      ("chuva + NDVI relativo", ["logR", "Nrel"]), ("chuva + NDVI + ONI", ["logR", "N", "ONI"])]:
        p = np.zeros(len(P))
        base = np.zeros(len(P))
        for a in np.unique(anos):
            tr_, te = anos != a, anos == a
            m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(P.loc[tr_, cols].values, y[tr_])
            p[te] = m.predict_proba(P.loc[te, cols].values)[:, 1]
            base[te] = y[tr_].mean()
        bs = np.mean((p - y) ** 2)
        bs0 = np.mean((base - y) ** 2)
        # AUC dentro do ano (média dos anos com as duas classes)
        aucs = [roc_auc_score(y[anos == a], p[anos == a]) for a in np.unique(anos)
                if 0 < y[anos == a].sum() < (anos == a).sum()]
        resultados.append({"portao": nome, "modelo": rot, "n": len(P), "taxa": y.mean(), "AUC": roc_auc_score(y, p),
                           "BSS": 1 - bs / bs0, "AUC_dentro_ano_media": np.mean(aucs)})
        if rot == "chuva + NDVI" and nome == "30/abr":
            P["p"] = p
            casos = P[P.ano.isin([2012, 2016, 2024])].groupby("ano").apply(
                lambda d: pd.Series({"quebras": d.quebra.sum(), "alertas_p>=0.4": (d.p >= 0.4).sum(),
                                     "acertos": ((d.p >= 0.4) & (d.quebra == 1)).sum()}))
            print("\nCasos (chuva+NDVI, 30/abr, alerta p>=0,4):\n", casos)

T = pd.DataFrame(resultados)
pd.set_option("display.width", 160)
print("\nPortão multimissão, milho, quebra < 50% da mediana municipal dos outros anos (LOYO)")
print(T.round(3).to_string(index=False))
T.to_csv(AQUI + "saidas/estrategista_r2_portao_multimissao.csv", index=False)
