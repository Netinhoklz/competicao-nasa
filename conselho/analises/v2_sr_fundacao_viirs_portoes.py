"""Sensoriamento remoto, rodada 2 (dados novos): VIIRS VNP13A3 como continuidade do NDVI e o NDVI relativo nos portoes.

Perguntas (pre-declaradas antes de rodar; nada e escolhido olhando o resultado):
 A. O VIIRS repete o MODIS no NIVEL MUNICIPAL (nao so na media do estado)? Concordancia da anomalia municipal e do
    desvio relativo aos vizinhos (anomalia menos a media do estado no mesmo mes), por mes, 2012-2026.
 B. O "deslocamento nao explicado" do NDVI (+0,053 desde 2020 no MODIS, cetico_deriva_ndvi_modis_landsat.saida.txt)
    aparece no VIIRS? Teste pareado: mesmos anos, mesma chuva IMERG fev-mai, reta ajustada em 2012-2019 para cada
    sensor; residuo medio 2020-2026. E a diferenca VIIRS - MODIS de fev-mai ano a ano.
 C. O NDVI relativo ajuda NOS PORTOES (so com o que ja existe na data)? Hipotese de latencia (a conferir): o composto
    mensal do mes M esta disponivel no portao seguinte ao fim do mes. Portao 19/mar -> NDVI de fevereiro;
    portao 30/abr -> NDVI de marco; fim de safra (M2) -> media mar-mai. Alvo: quebra canonica do milho (razao < 0,5
    da mediana dos outros anos, area >= 50 ha). Metrica: AUC DENTRO DO ANO (ponderada como no arquiteto), que e
    invariante a qualquer deslocamento comum do ano (deriva do sensor). IC90 por bootstrap de ANOS.
    Mesmas linhas para MODIS, VIIRS e chuva IMERG (% do normal no portao). Combinacao sem ajuste: media dos postos
    dentro do ano (nada treinado, nada escolhido). Versao "vizinhos de 50 km" como secundaria, declarada aqui.
 D. Lacuna do Terra (jun-nov/2025): fracao de pixels do CE com valor em cada sensor.
So le arquivos. Saida: v2_sr_fundacao_viirs_portoes.saida.txt (redirecionada pelo chamador).
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
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
D = "E:/campeonato-nasa/dados/derivados/"
rng = np.random.default_rng(0)

# ---------------- NDVI municipal mensal, os dois sensores na mesma grade 0,01 grau
mo = xr.open_dataset(DADOS / "modis/mod13q1_ndvi_mensal_001deg.nc").ndvi
vi = xr.open_dataset(DADOS / "viirs/vnp13a3_ndvi_evi_ceara_001deg.nc").ndvi.isel(lat=slice(None, None, -1))
assert np.allclose(mo.lat.values, vi.lat.values) and np.allclose(mo.lon.values, vi.lon.values)
lat, lon = mo.lat.values, mo.lon.values
res = abs(lon[1] - lon[0])
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["codarea"] = mun["codarea"].astype(str)
tr = from_origin(lon.min() - res / 2, lat.max() + res / 2, res, res)
lab = features.rasterize(((g, i + 1) for i, g in enumerate(mun.geometry)), out_shape=(len(lat), len(lon)),
                         transform=tr, fill=0, dtype="int32")
assert lat[0] > lat[-1]
codes = np.array(["0"] + list(mun.codarea.values))
ok0 = lab > 0


def municipal(da):
    arr = da.values
    out, frac = {}, {}
    for k, t in enumerate(pd.to_datetime(da.time.values)):
        a = arr[k].astype("float64")
        if np.nanmax(a) > 2:
            a = a / 10000.0
        ok = np.isfinite(a) & ok0 & (a > -0.2) & (a <= 1)
        s = np.bincount(lab[ok], weights=a[ok], minlength=len(codes))
        n = np.bincount(lab[ok], minlength=len(codes))
        with np.errstate(invalid="ignore", divide="ignore"):
            out[t] = (s / n)[1:]
        frac[t] = ok.sum() / ok0.sum()
        out[t][n[1:] < 5] = np.nan
    return pd.DataFrame(out, index=codes[1:]).T, pd.Series(frac)


M, fM = municipal(mo)
V, fV = municipal(vi.sel(time=slice("2012-01-01", None)))
print(f"MODIS: {M.shape[0]} meses {M.index.min():%Y-%m}..{M.index.max():%Y-%m}; VIIRS: {V.shape[0]} meses "
      f"{V.index.min():%Y-%m}..{V.index.max():%Y-%m}; municipios {M.shape[1]}")

# ---------------- D. lacuna do Terra
print("\n" + "=" * 30, "D. Lacuna do Terra: fracao de pixels do CE com NDVI valido", "=" * 30)
lac = pd.DataFrame({"MODIS": fM.reindex(pd.date_range("2025-05-01", "2025-12-01", freq="MS")),
                    "VIIRS": fV.reindex(pd.date_range("2025-05-01", "2025-12-01", freq="MS"))}).round(3)
lac.index = lac.index.strftime("%Y-%m")
print(lac.T.to_string())
print(f"VIIRS: meses de 2012-01 a {fV.index.max():%Y-%m} com >= 80% dos pixels validos: "
      f"{(fV >= 0.8).sum()} de {len(fV)}; mediana {fV.median():.3f}")

# ---------------- A. concordancia municipal
print("\n" + "=" * 30, "A. VIIRS x MODIS no nivel municipal (2012-01 a 2026-09)", "=" * 30)
comum_t = M.index.intersection(V.index)
Mc, Vc = M.loc[comum_t], V.loc[comum_t]
clim_m = Mc[Mc.index.year <= 2024].groupby(Mc[Mc.index.year <= 2024].index.month).mean()
clim_v = Vc[Vc.index.year <= 2024].groupby(Vc[Vc.index.year <= 2024].index.month).mean()
aM = Mc - clim_m.loc[Mc.index.month].values
aV = Vc - clim_v.loc[Vc.index.month].values
dM = aM.sub(aM.mean(axis=1), axis=0)  # relativo ao estado no mesmo mes
dV = aV.sub(aV.mean(axis=1), axis=0)
linhas = []
for t in comum_t:
    j = pd.DataFrame({"m": aM.loc[t], "v": aV.loc[t], "dm": dM.loc[t], "dv": dV.loc[t]}).dropna()
    if len(j) < 100:
        continue
    linhas.append({"t": t, "mes": t.month, "r_anom": stats.pearsonr(j.m, j.v).statistic,
                   "rho_rel": stats.spearmanr(j.dm, j.dv).statistic,
                   "rmsd_rel": np.sqrt(((j.dm - j.dv) ** 2).mean()), "sd_rel_m": j.dm.std()})
L = pd.DataFrame(linhas)
L["estacao"] = np.where(L.mes.isin([2, 3, 4, 5]), "fev-mai (quadra)", np.where(L.mes.isin([8, 9, 10, 11]), "ago-nov (seca)", "outros"))
print(L.groupby("estacao")[["r_anom", "rho_rel", "rmsd_rel", "sd_rel_m"]].median().round(3).to_string())
print(f"todos os meses: n={len(L)}; rho do desvio relativo (mediana) {L.rho_rel.median():.3f}; "
      f"meses com rho >= 0,7: {(L.rho_rel >= 0.7).mean():.0%}")
sM = Mc.mean(axis=1); sV = Vc.mean(axis=1)
jj = pd.concat([sM.rename("m"), sV.rename("v")], axis=1).dropna()
print(f"media do estado (municipios iguais): r = {stats.pearsonr(jj.m, jj.v).statistic:.3f}; vies VIIRS-MODIS = "
      f"{(jj.v - jj.m).mean():+.3f}; meses {len(jj)}")
fVm = fV.groupby(fV.index.month).median()
print("VIIRS: mediana da fracao de pixels do CE com NDVI bom/marginal, por mes do ano (visibilidade a 1 km, mensal):")
print("  " + " ".join(f"{m:02d}:{v:.2f}" for m, v in fVm.items()))

# ---------------- B. deslocamento pos-2020
print("\n" + "=" * 30, "B. O deslocamento +0,053 do MODIS aparece no VIIRS?", "=" * 30)
im = pd.read_parquet(D + "imerg_ce_mensal.parquet")
im = im[im.variavel == "precip_total"].set_index("data")["valor"]
im.index = pd.to_datetime(im.index)
chuva_fmam = im[im.index.month.isin([2, 3, 4, 5])].groupby(im[im.index.month.isin([2, 3, 4, 5])].index.year).sum()


def pix_mean(da, t0):
    arr = da.sel(time=slice(t0, None))
    vals = {}
    for k, t in enumerate(pd.to_datetime(arr.time.values)):
        a = arr.isel(time=k).values.astype("float64")
        if np.nanmax(a) > 2:
            a = a / 10000.0
        ok = np.isfinite(a) & ok0 & (a > -0.2) & (a <= 1)
        vals[t] = a[ok].mean()
    return pd.Series(vals)


pm = pix_mean(mo, "2000-01-01"); pv = pix_mean(vi, "2012-01-01")
fm = lambda s: s[s.index.month.isin([2, 3, 4, 5])].groupby(s[s.index.month.isin([2, 3, 4, 5])].index.year).mean()
E = pd.DataFrame({"modis": fm(pm), "viirs": fm(pv), "chuva": chuva_fmam}).loc[2000:2026]
def desloc(col, ini, fim_fit=2019):
    e = E[[col, "chuva"]].dropna().loc[ini:]
    fit = e.loc[:fim_fit]
    b = np.polyfit(fit.chuva, fit[col], 1)
    r = e[col] - np.polyval(b, e.chuva)
    return r, r.loc[:fim_fit].std(), r.loc[2020:].mean()
r0, sd0, d0 = desloc("modis", 2000)
print(f"replica do cetico (MODIS, reta 2000-2019, media de pixels): residuo 2020-26 = {d0:+.3f} (dp 2000-19 {sd0:.3f})")
rm, sdm, dm_ = desloc("modis", 2012)
rv, sdv, dv_ = desloc("viirs", 2012)
print(f"pareado, reta 2012-2019 (8 anos), mesmos anos: MODIS {dm_:+.3f} (dp {sdm:.3f}) | VIIRS {dv_:+.3f} (dp {sdv:.3f})")
E["viirs_menos_modis"] = E.viirs - E.modis
E["res_modis_12"] = rm; E["res_viirs_12"] = rv
print(E.loc[2012:].round(3).to_string())
dif = E.viirs_menos_modis.dropna()
t_ = stats.ttest_ind(dif.loc[2020:], dif.loc[:2019], equal_var=False)
print(f"VIIRS-MODIS fev-mai: 2012-19 {dif.loc[:2019].mean():+.3f} | 2020-26 {dif.loc[2020:].mean():+.3f} | "
      f"mudanca {dif.loc[2020:].mean() - dif.loc[:2019].mean():+.3f} (Welch p={t_.pvalue:.2f}; n=8 e 7 anos)")
# robustez pre-declarada (todas reportadas): (i) chuva do ERA5 em vez do IMERG; (ii) memoria: + chuva de jun(t-1)-jan(t)
# (o derivado do ERA5 so vai ate 2020-12; usamos a chuva do POWER, MERRA-2 corrigida, mm/dia -> mm/mes)
er = pd.read_parquet(D + "power_ce_mensal.parquet")
er = er[er.variavel == "PRECTOTCORR"].set_index("data")["valor"]; er.index = pd.to_datetime(er.index)
er = er * er.index.days_in_month
E["chuva_era5"] = er[er.index.month.isin([2, 3, 4, 5])].groupby(er[er.index.month.isin([2, 3, 4, 5])].index.year).sum(min_count=4)
im_prev = im.copy(); im_prev.index = im_prev.index + pd.DateOffset(months=7)  # jun(t-1)..jan(t) cai em jan..ago de t
E["chuva_mem"] = im_prev[im_prev.index.month.isin(range(1, 9))].groupby(im_prev[im_prev.index.month.isin(range(1, 9))].index.year).sum()
for sens, ini in [("modis", 2000), ("modis", 2012), ("viirs", 2012)]:
    for rot, xs in [("IMERG fev-mai", ["chuva"]), ("POWER fev-mai", ["chuva_era5"]), ("IMERG fev-mai + jun(t-1)-jan(t)", ["chuva", "chuva_mem"])]:
        e = E.loc[ini:2026, [sens] + xs].dropna()
        fit = e.loc[:2019]
        X = np.c_[np.ones(len(fit)), fit[xs].values]
        b = np.linalg.lstsq(X, fit[sens].values, rcond=None)[0]
        r = e[sens] - np.c_[np.ones(len(e)), e[xs].values] @ b
        print(f"  {sens} reta {ini}-2019, {rot:32s}: residuo 2020-26 {r.loc[2020:].mean():+.3f} (dp {r.loc[:2019].std():.3f}; "
              f"anos 2020+ = {len(r.loc[2020:])})")

# ---------------- C. NDVI relativo nos portoes
print("\n" + "=" * 30, "C. NDVI relativo nos portoes (quebra canonica do milho)", "=" * 30)
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha
p["ref"] = p.groupby("cod_local")["r"].transform(
    lambda v: pd.Series([np.median(np.delete(v.values, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=v.index))
p["quebra"] = (p.r / p.ref < 0.5).astype(int)
p["cod"] = p.cod_local.astype(str).str[:7]
p = p.dropna(subset=["ref"])[["cod", "ano", "quebra"]]

chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
anos_ch = list(range(1998, 2026))


def pct_normal(m, d):
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_ch}).T
    out = ac.copy() * np.nan
    for a in anos_ch:
        out.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return out.stack().rename("pct").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})


cent = mun.to_crs(5880).geometry.centroid
xy = np.c_[cent.x.values, cent.y.values]
dist = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1)) / 1000
viz = (dist <= 50) & (dist > 0)
ordem = list(mun.codarea.values)


def ndvi_janela(T, meses, anos):
    sel = T[T.index.month.isin(meses) & T.index.year.isin(anos)]
    g = sel.groupby(sel.index.year).mean()  # ano x mun
    anom = g - (g.sum() - g) / (g.count() - 1)  # anomalia contra a media dos outros anos
    anom = anom[ordem]
    nb = np.where(viz, 1.0, 0.0)
    vals = anom.values
    okv = np.isfinite(vals)
    soma = np.nan_to_num(vals) @ nb.T
    cnt = okv.astype(float) @ nb.T
    with np.errstate(invalid="ignore", divide="ignore"):
        rel_viz = vals - soma / cnt
    a1 = anom.stack().rename("a").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})
    a2 = pd.DataFrame(rel_viz, index=anom.index, columns=ordem).stack().rename("viz").reset_index().rename(
        columns={"level_0": "ano", "level_1": "cod"})
    return a1.merge(a2, on=["ano", "cod"])


def auc_dentro(df, col, anos=None):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        if anos is not None and a not in anos:
            continue
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, g[col]); den += w
    return num / den if den else np.nan


def boot_dentro(df, cols, nboot=1000):
    yrs = [a for a, g in df.groupby("ano") if g.quebra.sum() >= 3 and (1 - g.quebra).sum() >= 3]
    cache = {a: {c: (g.quebra.sum() * (1 - g.quebra).sum(), roc_auc_score(g.quebra, g[c])) for c in cols}
             for a, g in df.groupby("ano") if a in yrs}
    out = {c: [] for c in cols}
    for _ in range(nboot):
        bb = rng.choice(yrs, len(yrs))
        for c in cols:
            w = np.array([cache[a][c][0] for a in bb]); v = np.array([cache[a][c][1] for a in bb])
            out[c].append((w * v).sum() / w.sum())
    return {c: np.array(v) for c, v in out.items()}, yrs


PORT = {"19/mar (NDVI fev)": ((3, 19), [2]), "30/abr (NDVI mar)": ((4, 30), [3]),
        "fim de safra (NDVI mar-mai, M2)": ((5, 31), [3, 4, 5])}
res_tab = []
for periodo, anos_p, sensores in [("2012-2025 pareado", list(range(2012, 2026)), ["MODIS", "VIIRS"]),
                                  ("2000-2025 so MODIS", list(range(2000, 2026)), ["MODIS"])]:
    print(f"\n--- {periodo} ---")
    for nome, ((m, d), meses) in PORT.items():
        df = p[p.ano.isin(anos_p)].merge(pct_normal(m, d), on=["cod", "ano"])
        df["s_chuva"] = -df.pct.clip(upper=3)
        for s in sensores:
            T = M if s == "MODIS" else V
            nd = ndvi_janela(T, meses, anos_p).rename(columns={"a": f"a_{s}", "viz": f"viz_{s}"})
            df = df.merge(nd, on=["cod", "ano"])
            df[f"s_{s}"] = -df[f"a_{s}"]
            df[f"sv_{s}"] = -df[f"viz_{s}"]
        df = df.dropna()
        # combinacao sem ajuste: media dos postos dentro do ano
        for s in sensores:
            df[f"c_{s}"] = df.groupby("ano")["s_chuva"].rank(pct=True) + df.groupby("ano")[f"s_{s}"].rank(pct=True)
        cols = ["s_chuva"] + [f"{k}_{s}" for s in sensores for k in ("s", "sv", "c")]
        bs, yrs = boot_dentro(df, cols)
        lin = {"periodo": periodo, "portao": nome, "n": len(df), "anos": len(yrs), "taxa_quebra": round(df.quebra.mean(), 3)}
        for c in cols:
            lin[c] = f"{auc_dentro(df, c):.3f} [{np.percentile(bs[c], 5):.2f},{np.percentile(bs[c], 95):.2f}]"
        for s in sensores:
            dd = bs[f"s_{s}"] - bs["s_chuva"]
            lin[f"dNDVI-chuva_{s}"] = f"{auc_dentro(df, f's_{s}') - auc_dentro(df, 's_chuva'):+.3f} [{np.percentile(dd, 5):+.2f},{np.percentile(dd, 95):+.2f}]"
            dc = bs[f"c_{s}"] - bs["s_chuva"]
            lin[f"dComb-chuva_{s}"] = f"{auc_dentro(df, f'c_{s}') - auc_dentro(df, 's_chuva'):+.3f} [{np.percentile(dc, 5):+.2f},{np.percentile(dc, 95):+.2f}]"
            lin[f"AUCtotal_{s}"] = round(roc_auc_score(df.quebra, df[f"s_{s}"]), 3)
        if len(sensores) == 2:
            dv = bs["s_VIIRS"] - bs["s_MODIS"]
            lin["dVIIRS-MODIS"] = f"{auc_dentro(df, 's_VIIRS') - auc_dentro(df, 's_MODIS'):+.3f} [{np.percentile(dv, 5):+.2f},{np.percentile(dv, 95):+.2f}]"
            lin["rho_dentro_ano_MODISxVIIRS"] = round(np.nanmean([stats.spearmanr(g.a_MODIS, g.a_VIIRS).statistic
                                                                  for _, g in df.groupby("ano")]), 3)
        lin["AUCtotal_chuva"] = round(roc_auc_score(df.quebra, df.s_chuva), 3)
        res_tab.append(lin)
        for k, v in lin.items():
            print(f"  {k:28s} {v}")
        print()
print("Leitura: s_* = anomalia do NDVI contra os outros anos (AUC dentro do ano = relativo ao estado no mesmo ano);")
print("sv_* = relativo aos vizinhos de 50 km (secundaria); c_* = soma dos postos chuva + NDVI dentro do ano, sem ajuste.")
pd.DataFrame(res_tab).to_csv(A + "saidas/v2_sr_fundacao_viirs_portoes.csv", index=False)
