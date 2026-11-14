"""Cetico 1: escala (estado x municipio) e vazamento de validacao no elo chuva -> rendimento.

Perguntas:
  (a) Quanto da variacao do rendimento municipal de milho/feijao e choque comum do ano (regional) e quanto e local?
  (b) A chuva municipal do IMERG (0,1 grau) explica a parte local, alem da chuva media do estado?
  (c) Validacao cruzada aleatoria (linhas) infla a habilidade em relacao a deixar o ANO inteiro de fora?
  (d) O rendimento do IBGE (sobre area COLHIDA) esconde a quebra? Comparar com producao / area PLANTADA.

Dados: E:/campeonato-nasa/dados/imerg/imerg_ce_diario_*.nc (IMERG V07 via POWER, 0,1 grau, diario)
       E:/campeonato-nasa/dados/derivados/ibge_pam_mun_anual.parquet (PAM municipal)
       E:/campeonato-nasa/dados/referencia/ceara_municipios.geojson
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, DERIV, REF

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ANOS = range(1998, 2026)

# ---------------- 1. indices de chuva da quadra por pixel ----------------
reg = []
for ano in ANOS:
    ds = xr.open_dataset(DADOS / "imerg" / f"imerg_ce_diario_{ano}.nc")
    q = ds.precip.sel(time=ds.time.dt.month.isin([2, 3, 4, 5])).values  # (t, lat, lon) mm/dia
    lat, lon = ds.lat.values, ds.lon.values
    ds.close()
    tot = np.nansum(q, axis=0)
    seco = q <= 2.0
    run = np.zeros(q.shape[1:])
    nver = np.zeros(q.shape[1:])
    cdd = np.zeros(q.shape[1:])
    for t in range(q.shape[0]):
        run = np.where(seco[t], run + 1, 0)
        nver += (run == 3)  # cada sequencia conta uma vez quando atinge 3 dias (Rocha et al. 2021: >=3 dias <=2 mm)
        cdd = np.maximum(cdd, run)
    reg.append(xr.Dataset({"fmam": (("lat", "lon"), tot), "nver": (("lat", "lon"), nver), "cdd": (("lat", "lon"), cdd)},
                          coords={"lat": lat, "lon": lon}).expand_dims(ano=[ano]))
pix = xr.concat(reg, "ano")

# ---------------- 2. pixel -> municipio ----------------
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["codarea"] = mun["codarea"].astype(int)
LO, LA = np.meshgrid(pix.lon.values, pix.lat.values)
pts = gpd.GeoDataFrame({"ilat": np.repeat(np.arange(len(pix.lat)), len(pix.lon)),
                        "ilon": np.tile(np.arange(len(pix.lon)), len(pix.lat))},
                       geometry=gpd.points_from_xy(LO.ravel(), LA.ravel()), crs=mun.crs)
j = gpd.sjoin(pts, mun[["codarea", "geometry"]], predicate="within")
faltam = set(mun.codarea) - set(j.codarea)
extra = []
for c in faltam:  # municipio menor que o pixel: pixel mais proximo do ponto representativo
    p = mun.loc[mun.codarea == c].geometry.iloc[0].representative_point()
    extra.append({"ilat": int(np.abs(pix.lat.values - p.y).argmin()), "ilon": int(np.abs(pix.lon.values - p.x).argmin()), "codarea": c})
mapa = pd.concat([j[["ilat", "ilon", "codarea"]], pd.DataFrame(extra)], ignore_index=True)
print(f"municipios: {mun.codarea.nunique()} | pixels 0,1 grau mapeados: {len(j)} | municipios sem centro de pixel: {len(faltam)}")
print(f"pixels por municipio: mediana {mapa.groupby('codarea').size().median():.0f}, min {mapa.groupby('codarea').size().min()}")

linhas = []
arr = {v: pix[v].values for v in ["fmam", "nver", "cdd"]}
for c, g in mapa.groupby("codarea"):
    for k, ano in enumerate(pix.ano.values):
        linhas.append({"codarea": c, "ano": int(ano), **{v: float(np.nanmean(arr[v][k, g.ilat, g.ilon])) for v in arr}})
clima = pd.DataFrame(linhas)
estado = clima.groupby("ano")[["fmam", "nver", "cdd"]].mean().add_prefix("ce_")
clima = clima.merge(estado, on="ano")
for v in ["fmam", "nver", "cdd"]:
    clima[f"d_{v}"] = clima[v] - clima[f"ce_{v}"]  # desvio local em relacao ao estado no mesmo ano

# ---------------- 3. rendimento ----------------
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(int)
res_todas = {}
for nome, chave in [("milho", "Milho (em gr"), ("feijao", "Feij")]:
    s = pam[pam.produto.str.startswith(chave) & pam.ano.between(1998, 2025)].copy()
    s = s[s.area_plantada_ha >= 200]
    s["y_plant"] = s.producao_t * 1000 / s.area_plantada_ha   # kg por ha PLANTADO
    s["y_colh"] = s.rendimento_kg_ha                          # kg por ha COLHIDO (oficial)
    s = s.sort_values(["cod", "ano"])
    for y in ["y_plant", "y_colh"]:
        tend = s.groupby("cod")[y].transform(lambda x: x.rolling(7, center=True, min_periods=3).median())
        s[f"an_{y}"] = (s[y] / tend - 1).clip(-1, 2)
    d = s.merge(clima, left_on=["cod", "ano"], right_on=["codarea", "ano"]).dropna(subset=["an_y_plant", "an_y_colh"])
    d = d[np.isfinite(d.an_y_plant)]
    print(f"\n==== {nome}: {len(d)} municipio-anos, {d.cod.nunique()} municipios, {d.ano.min()}-{d.ano.max()}")

    # (d) colhida x plantada: quebra no estado em anos secos
    tot = s.groupby("ano")[["producao_t", "area_plantada_ha", "area_colhida_ha"]].sum()
    tot["kg_ha_plant"] = tot.producao_t * 1000 / tot.area_plantada_ha
    tot["kg_ha_colh"] = tot.producao_t * 1000 / tot.area_colhida_ha
    med = tot[["kg_ha_plant", "kg_ha_colh"]].median()
    for a in [2012, 2016, 2019]:
        if a in tot.index:
            print(f"  {a}: queda vs mediana 1998-2025 | sobre area plantada {tot.loc[a,'kg_ha_plant']/med.kg_ha_plant-1:+.0%} | "
                  f"sobre area colhida (oficial) {tot.loc[a,'kg_ha_colh']/med.kg_ha_colh-1:+.0%} | "
                  f"area perdida {1-tot.loc[a,'area_colhida_ha']/tot.loc[a,'area_plantada_ha']:.0%}")
    # elasticidade: % por +100 mm (chuva do estado) nas duas definicoes, nivel estado
    st = tot.join(estado)
    for col in ["kg_ha_plant", "kg_ha_colh"]:
        t = st[col].rolling(7, center=True, min_periods=3).median()
        dev = (st[col] / t - 1) * 100
        sl, ic, r, p, _ = stats.linregress(st.ce_fmam, dev)
        print(f"  elasticidade estado ({col}): {sl*100:+.1f}% por +100 mm (r={r:.2f}, p={p:.3f}, n={len(st)})")

    # (a) decomposicao da variancia da anomalia (area plantada)
    yv = d.an_y_plant.values
    ano_ef = d.groupby("ano").an_y_plant.transform("mean")
    mun_ef = d.groupby("cod").an_y_plant.transform("mean")
    r2_ano = 1 - ((yv - ano_ef) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
    resid_ano = yv - ano_ef
    print(f"  (a) R2 so do efeito-ano (choque comum): {r2_ano:.2f} | parte local (dentro do ano): {1-r2_ano:.2f}")

    # (b)+(c) modelos x esquema de validacao
    feats = {
        "M1 chuva media do ESTADO (ridge)": ["ce_fmam", "ce_nver", "ce_cdd"],
        "M2 chuva do MUNICIPIO (ridge)": ["fmam", "nver", "cdd"],
        "M3 municipio + estado (ridge)": ["fmam", "nver", "cdd", "ce_fmam", "ce_nver", "ce_cdd"],
        "M4 municipio + estado (boosting)": ["fmam", "nver", "cdd", "ce_fmam", "ce_nver", "ce_cdd"],
    }
    esquemas = {"aleatorio 5-fold (linhas)": (KFold(5, shuffle=True, random_state=0), None),
                "deixa ANO de fora": (GroupKFold(n_splits=d.ano.nunique()), d.ano.values)}
    tab = []
    for mnome, cols in feats.items():
        X = d[cols].values
        for enome, (cv, grp) in esquemas.items():
            pred = np.zeros(len(d))
            for tr, te in cv.split(X, yv, grp):
                if "boosting" in mnome:
                    m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, random_state=0)
                else:
                    m = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13)))
                m.fit(X[tr], yv[tr])
                pred[te] = m.predict(X[te])
            # habilidade dentro do ano: ordena bem os municipios num mesmo ano?
            rho = []
            for a, g in d.assign(p=pred).groupby("ano"):
                if len(g) >= 20:
                    rho.append(stats.spearmanr(g.p, g.an_y_plant).statistic)
            tab.append({"modelo": mnome, "validacao": enome, "R2": round(r2_score(yv, pred), 3),
                        "rho_dentro_do_ano": round(float(np.nanmean(rho)), 3)})
    T = pd.DataFrame(tab)
    print(T.to_string(index=False))
    # (b') desvio local de chuva x residuo local de rendimento (sem modelo)
    rr = stats.spearmanr(d.d_fmam, resid_ano)
    rv = stats.spearmanr(d.d_nver, resid_ano)
    print(f"  (b') desvio local da chuva fev-mai x desvio local do rendimento: rho={rr.statistic:+.3f} (n={len(d)}); "
          f"veranicos: rho={rv.statistic:+.3f}")
    res_todas[nome] = T

    # (e) robustez: tendencia linear por municipio (a mediana movel de 7 anos "come" a seca de 2012-2017)
    d["an_lin"] = np.nan
    for c, g in d.groupby("cod"):
        if len(g) >= 10:
            b = np.polyfit(g.ano, g.y_plant, 1)
            t = np.polyval(b, g.ano)
            d.loc[g.index, "an_lin"] = np.where(t > 0, g.y_plant / np.maximum(t, 1) - 1, np.nan)
    dl = d.dropna(subset=["an_lin"])
    dl = dl.assign(an_lin=dl.an_lin.clip(-1, 2))
    r2a = 1 - ((dl.an_lin - dl.groupby("ano").an_lin.transform("mean")) ** 2).sum() / ((dl.an_lin - dl.an_lin.mean()) ** 2).sum()
    print(f"  (e) com tendencia linear: R2 do efeito-ano = {r2a:.2f}")
    X = dl[["ce_fmam", "ce_nver", "ce_cdd"]].values
    for enome, (cv, grp) in {"aleatorio": (KFold(5, shuffle=True, random_state=0), None),
                             "deixa ANO de fora": (GroupKFold(n_splits=dl.ano.nunique()), dl.ano.values)}.items():
        pred = np.zeros(len(dl))
        for tr, te in cv.split(X, dl.an_lin.values, grp):
            m = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13))).fit(X[tr], dl.an_lin.values[tr])
            pred[te] = m.predict(X[te])
        print(f"      M1 estado, {enome}: R2={r2_score(dl.an_lin, pred):.3f}")
    # efeito de anos extremos: elasticidade no nivel estado sem 2012 e 2016
    st2 = st.drop([a for a in [2012, 2016] if a in st.index])
    t2 = st2.kg_ha_plant.rolling(7, center=True, min_periods=3).median()
    sl2, _, r2_, p2_, _ = stats.linregress(st2.ce_fmam, (st2.kg_ha_plant / t2 - 1) * 100)
    print(f"  (f) elasticidade estado sem 2012 e 2016: {sl2*100:+.1f}% por +100 mm (r={r2_:.2f}, p={p2_:.3f}, n={len(st2)})")

    # (g) a parte local e sinal ou ruido? correlacao espacial e persistencia do residuo dentro do ano
    cent = mun.set_index("codarea").geometry.representative_point()
    cx, cy = cent.x, cent.y
    d["res"] = resid_ano
    viz = []
    for a, g in d.groupby("ano"):
        g = g.set_index("cod")
        xs, ys = cx.reindex(g.index).values, cy.reindex(g.index).values
        D = np.hypot(xs[:, None] - xs[None], ys[:, None] - ys[None])
        np.fill_diagonal(D, np.inf)
        k = np.argsort(D, axis=1)[:, :5]
        viz.append(stats.pearsonr(g.res.values, g.res.values[k].mean(axis=1)).statistic)
    pv = d.sort_values(["cod", "ano"]).groupby("cod").res.apply(lambda x: x.autocorr(1)).dropna()
    fe = d.groupby("cod").res.transform("mean")
    r2_fe = 1 - ((d.res - fe) ** 2).sum() / ((d.res - d.res.mean()) ** 2).sum()
    print(f"  (g) residuo local: r com a media dos 5 vizinhos = {np.mean(viz):+.2f} (media dos anos) | "
          f"autocorrelacao ano a ano no municipio = {pv.median():+.2f} (mediana) | "
          f"fracao do residuo explicada por efeito fixo de municipio = {r2_fe:.2f}")
    d[["cod", "ano", "y_plant", "an_y_plant", "an_lin", "fmam", "nver", "cdd", "ce_fmam", "ce_nver", "ce_cdd",
       "area_plantada_ha"]].to_parquet(
        rf"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/cetico_painel_{nome}.parquet")

print("\nObs.: a tendencia (mediana movel centrada de 7 anos) usa anos vizinhos; serve para explicar o choque do ano,"
      " nao para prever. O rho_dentro_do_ano mede se o modelo ordena os municipios num mesmo ano.")
