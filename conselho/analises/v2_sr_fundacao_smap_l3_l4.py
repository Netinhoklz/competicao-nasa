"""Sensoriamento remoto, rodada 2 (dados novos): SMAP L3 (observacao) x SMAP L4 (modelo + assimilacao) e o SMAP nos portoes.

O consolidado do L3 (smap_l3_diario_ne.nc) AINDA NAO EXISTE: o download esta em andamento. Lemos, so para leitura, os
granulos ja baixados em dados/smap/l3_diario (SPL3SMP_E v006, recorte do Nordeste na MESMA grade EASE2 9 km do L4),
pulando os arquivos modificados nos ultimos 3 minutos (podem estar sendo escritos). Periodo comum = o que existir.

Perguntas pre-declaradas:
 A. Visibilidade do micro-ondas: fracao das celulas do CE com retrieval de qualidade recomendada (bit0 = 0) por
    passagem e por mes do ano; dias por mes com >= 1 retrieval recomendado (AM ou PM) por celula. Compara com a
    visibilidade optica (VIIRS 1 km mensal: v2_sr_fundacao_viirs_portoes.saida.txt; HLS/S2/Landsat: rodada 1).
 B. L3 AM/PM (recomendado) x L4 sm_surface do mesmo dia (L4 13:30 UTC): r agrupado, vies, ubRMSD, r temporal por
    celula (bruto e anomalia contra a climatologia mensal da celula), r espacial dentro do dia, r da media do CE.
    CUIDADO: o L4 assimila as temperaturas de brilho do proprio SMAP, entao a concordancia e em parte circular.
 C. SMAP L4 nos portoes (2016-2025, 10 quadras): percentil da zona da raiz (media dos 7 dias ate o portao, por
    municipio) contra a quebra canonica do milho. AUC total e DENTRO DO ANO, nas MESMAS linhas da chuva IMERG
    (% do normal no portao). Combinacao sem ajuste = soma dos postos dentro do ano. IC90 por bootstrap de ANOS.
    Secundaria declarada: anomalia da zona da raiz (m3/m3) contra a media dos outros anos 2016-2025.
So le arquivos.
"""
import glob
import os
import sys
import time
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, REF

import geopandas as gpd
import h5py
import numpy as np
import pandas as pd
import shapely
import xarray as xr
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
t0 = time.time()

l4 = xr.open_dataset(DADOS / "smap/smap_l4_diario_ne.nc")
_t = pd.DatetimeIndex(l4.time.values)
print(f"L4: datas duplicadas no consolidado: {sorted(set(_t[_t.duplicated()].strftime('%Y-%m-%d')))} -> fica a 1a ocorrencia")
l4 = l4.isel(time=np.where(~_t.duplicated())[0])
lat3 = np.load(DADOS / "smap/l3_diario/lat_linhas.npy"); lon3 = np.load(DADOS / "smap/l3_diario/lon_colunas.npy")
assert np.allclose(lat3, l4.lat.values, atol=1e-4) and np.allclose(lon3, l4.lon.values, atol=1e-4), "grades diferentes"
# caixa do Ceara na grade EASE2
ii = np.where((l4.lat.values <= -2.5) & (l4.lat.values >= -8.0))[0]
jj = np.where((l4.lon.values >= -41.5) & (l4.lon.values <= -37.0))[0]
lat, lon = l4.lat.values[ii], l4.lon.values[jj]
CE = gpd.read_file(REF / "ceara_uf.geojson").union_all()
LO, LA = np.meshgrid(lon, lat)
mce = shapely.contains_xy(CE, LO, LA)
print(f"caixa CE na grade 9 km: {len(ii)} x {len(jj)} celulas; {mce.sum()} celulas com centro no Ceara")

# ---------------- L3: granulos ja baixados
arqs = sorted(glob.glob(str(DADOS / "smap/l3_diario/SMAP_L3_SM_P_E_*_recorte.nc4")))
agora = time.time()
arqs = [a for a in arqs if agora - os.path.getmtime(a) > 180]
arqs = list({os.path.basename(a).split("_")[5]: a for a in arqs}.values())  # 1 granulo por dia (a maior versao)
dias, am, qam, pm, qpm = [], [], [], [], []
falhas = 0
for a in arqs:
    try:
        with h5py.File(a, "r") as h:
            s_am = h["Soil_Moisture_Retrieval_Data_AM/soil_moisture"][ii.min():ii.max() + 1, jj.min():jj.max() + 1]
            f_am = h["Soil_Moisture_Retrieval_Data_AM/retrieval_qual_flag"][ii.min():ii.max() + 1, jj.min():jj.max() + 1]
            s_pm = h["Soil_Moisture_Retrieval_Data_PM/soil_moisture_pm"][ii.min():ii.max() + 1, jj.min():jj.max() + 1]
            f_pm = h["Soil_Moisture_Retrieval_Data_PM/retrieval_qual_flag_pm"][ii.min():ii.max() + 1, jj.min():jj.max() + 1]
    except Exception:
        falhas += 1
        continue
    dias.append(pd.Timestamp(os.path.basename(a).split("_")[5]))
    am.append(s_am); qam.append(f_am); pm.append(s_pm); qpm.append(f_pm)
dias = pd.DatetimeIndex(dias)
am, qam, pm, qpm = map(np.array, (am, qam, pm, qpm))
print(f"L3 lidos: {len(dias)} dias, {dias.min():%Y-%m-%d} -> {dias.max():%Y-%m-%d}; falhas de leitura {falhas}; "
      f"({time.time() - t0:.0f} s)")


def limpo(s, q):
    ok = (s >= 0.02) & (s <= 0.5) & (q != 65534)
    rec = ok & ((q.astype(np.int64) & 1) == 0)
    return np.where(ok, s, np.nan), np.where(rec, s, np.nan)


am_all, am_rec = limpo(am, qam)
pm_all, pm_rec = limpo(pm, qpm)

print("\n" + "=" * 25, "A. Visibilidade do micro-ondas (L3, celulas do CE)", "=" * 25)
f = lambda x: np.isfinite(x[:, mce]).mean(axis=1)
V = pd.DataFrame({"AM qualquer": f(am_all), "AM recomendado": f(am_rec), "PM qualquer": f(pm_all), "PM recomendado": f(pm_rec)},
                 index=dias)
print("fracao das celulas do CE com retrieval, media por mes do ano (por passagem diaria):")
print(V.groupby(V.index.month).mean().round(3).T.to_string())
alg = np.isfinite(am_rec[:, mce]) | np.isfinite(pm_rec[:, mce])
Dd = pd.DataFrame(alg, index=dias).groupby([dias.year, dias.month]).sum()  # dias com >= 1 retrieval por celula-mes
ndias = pd.Series(1, index=dias).groupby([dias.year, dias.month]).sum()
Dd = Dd[ndias.values >= 25]
med_mes = Dd.median(axis=1).groupby(level=1).median()
print("dias por mes com >= 1 retrieval recomendado (AM ou PM), mediana por celula, por mes do ano:")
print("  " + " ".join(f"{m:02d}:{v:.0f}" for m, v in med_mes.items()))
fev_mai = Dd[Dd.index.get_level_values(1).isin([2, 3, 4, 5])].values.ravel()
ago_nov = Dd[Dd.index.get_level_values(1).isin([8, 9, 10, 11])].values.ravel()
print(f"celula-meses com >= 4 dias vistos: fev-mai {np.mean(fev_mai >= 4):.1%} | ago-nov {np.mean(ago_nov >= 4):.1%}")
# chance de ao menos 1 retrieval recomendado nos 16 e 30 dias antes de cada portao, por celula-ano
alg_df = pd.DataFrame(alg, index=dias)
for nome, (m, d) in {"28/fev": (2, 28), "19/mar": (3, 19), "31/mar": (3, 31), "30/abr": (4, 30)}.items():
    r16, r30 = [], []
    for y in sorted(set(dias.year)):
        fim = pd.Timestamp(y, m, d)
        for jan, lst in ((16, r16), (30, r30)):
            w = alg_df.loc[fim - pd.Timedelta(days=jan - 1):fim]
            if len(w) >= jan - 2:
                lst.append(w.any(axis=0).mean())
    print(f"  portao {nome}: fracao de celulas com >= 1 vista recomendada em 16 d = {np.mean(r16):.3f}, "
          f"em 30 d = {np.mean(r30):.3f} (anos {len(r30)})")

# ---------------- B. L3 x L4
print("\n" + "=" * 25, "B. L3 (observacao) x L4 superficie (modelo + assimilacao)", "=" * 25)
l4c = l4[["sm_surface", "sm_rootzone"]].isel(lat=ii, lon=jj).sel(time=slice(dias.min(), dias.max()))
l4t = pd.DatetimeIndex(l4c.time.values).normalize()
comuns = dias.intersection(l4t)
i3 = dias.get_indexer(comuns); i4 = l4t.get_indexer(comuns)
L4s = l4c.sm_surface.values[i4]
print(f"dias comuns: {len(comuns)} ({time.time() - t0:.0f} s)")
for rot, X in [("AM recomendado", am_rec[i3]), ("PM recomendado", pm_rec[i3]), ("AM qualquer", am_all[i3])]:
    x = X[:, mce]; y = L4s[:, mce]
    ok = np.isfinite(x) & np.isfinite(y)
    r_all = stats.pearsonr(x[ok], y[ok]).statistic
    bias = np.mean(x[ok] - y[ok])
    ub = np.sqrt(np.mean(((x[ok] - x[ok].mean()) - (y[ok] - y[ok].mean())) ** 2))
    # temporal por celula: bruto e anomalia contra climatologia mensal da celula
    mes = comuns.month.values
    rt, rta = [], []
    for k in range(x.shape[1]):
        o = ok[:, k]
        if o.sum() < 60:
            continue
        rt.append(stats.pearsonr(x[o, k], y[o, k]).statistic)
        xa = pd.Series(x[o, k]); ya = pd.Series(y[o, k]); mm = mes[o]
        xa = xa - xa.groupby(mm).transform("mean").values; ya = ya - ya.groupby(mm).transform("mean").values
        rta.append(stats.pearsonr(xa, ya).statistic)
    # espacial dentro do dia
    rs = [stats.pearsonr(x[t][ok[t]], y[t][ok[t]]).statistic for t in range(len(comuns)) if ok[t].sum() >= 50]
    # media do CE por dia (so dias com >= 50% das celulas)
    cob = ok.mean(axis=1) >= 0.5
    mx = np.array([np.nanmean(np.where(ok[t], x[t], np.nan)) for t in range(len(comuns))])
    my = np.array([np.nanmean(np.where(ok[t], y[t], np.nan)) for t in range(len(comuns))])
    r_ce = stats.pearsonr(mx[cob], my[cob]).statistic
    print(f"  {rot:15s}: pares {ok.sum():>8d} | r agrupado {r_all:.3f} | vies L3-L4 {bias:+.3f} m3/m3 | ubRMSD {ub:.3f} | "
          f"r temporal/celula mediana {np.median(rt):.3f} (anomalia {np.median(rta):.3f}; celulas {len(rt)}) | "
          f"r espacial no dia mediana {np.median(rs):.3f} | r media CE {r_ce:.3f} (dias {cob.sum()})")

# escala real: concordancia ESPACIAL das anomalias (cada celula menos a sua climatologia mensal; dia menos a media do
# dominio) em blocos de 1, 2, 4 e 8 celulas (9, 18, 36, 72 km). Pre-declarado: escala util = menor bloco com r >= 0,8.
print("\n  escala real (L3 AM recomendado x L4 superficie): r espacial das ANOMALIAS dentro do dia, por tamanho de bloco")
x = am_rec[i3].copy(); y = L4s.copy()
x[:, ~mce] = np.nan; y[:, ~mce] = np.nan
ok = np.isfinite(x) & np.isfinite(y)
x[~ok] = np.nan; y[~ok] = np.nan
mes = comuns.month.values
for k in range(1, 13):
    sel = mes == k
    x[sel] -= np.nanmean(x[sel], axis=0); y[sel] -= np.nanmean(y[sel], axis=0)
sazao = np.isin(mes, [2, 3, 4, 5])
for b in (1, 2, 4, 8):
    nl, nc = (x.shape[1] // b) * b, (x.shape[2] // b) * b
    xb = np.nanmean(x[:, :nl, :nc].reshape(len(x), nl // b, b, nc // b, b), axis=(2, 4))
    yb = np.nanmean(y[:, :nl, :nc].reshape(len(y), nl // b, b, nc // b, b), axis=(2, 4))
    cnt = ok[:, :nl, :nc].reshape(len(x), nl // b, b, nc // b, b).sum(axis=(2, 4))
    rr, rq = [], []
    for t in range(len(xb)):
        o = np.isfinite(xb[t]) & np.isfinite(yb[t]) & (cnt[t] >= max(1, b * b // 2))
        if o.sum() >= 12:
            a_, c_ = xb[t][o] - xb[t][o].mean(), yb[t][o] - yb[t][o].mean()
            v = stats.pearsonr(a_, c_).statistic
            (rq if sazao[t] else rr).append(v)
    print(f"    bloco {b} x 9 km = {9 * b:>2d} km: r mediano fev-mai {np.median(rq):.3f} (dias {len(rq)}) | "
          f"outros meses {np.median(rr):.3f} (dias {len(rr)})")

# ---------------- C. SMAP L4 nos portoes
print("\n" + "=" * 25, "C. SMAP L4 nos portoes x quebra canonica do milho (2016-2025)", "=" * 25)
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["codarea"] = mun["codarea"].astype(str)
# celulas de 9 km por municipio (centro dentro; se nenhuma, a mais proxima do centroide)
cel = {}
for _, rw in mun.iterrows():
    dentro = shapely.contains_xy(rw.geometry, LO, LA)
    if dentro.sum() == 0:
        c = rw.geometry.centroid
        k = np.argmin((LO - c.x) ** 2 + (LA - c.y) ** 2)
        dentro = np.zeros_like(dentro); dentro.flat[k] = True
    cel[rw.codarea] = dentro
ncel = pd.Series({k: v.sum() for k, v in cel.items()})
print(f"celulas SMAP 9 km por municipio: mediana {ncel.median():.0f}, min {ncel.min()}, max {ncel.max()}, "
      f"municipios com 1 celula so: {(ncel <= 1).sum()}")

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


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, g[col]); den += w
    return num / den if den else np.nan


def boot(df, cols, nboot=1000):
    yrs = [a for a, g in df.groupby("ano") if g.quebra.sum() >= 3 and (1 - g.quebra).sum() >= 3]
    cache = {a: {c: (g.quebra.sum() * (1 - g.quebra).sum(), roc_auc_score(g.quebra, g[c])) for c in cols}
             for a, g in df.groupby("ano") if a in yrs}
    allg = {a: g for a, g in df.groupby("ano")}
    out = {c: [] for c in cols}; tot = {c: [] for c in cols}
    for _ in range(nboot):
        bb = rng.choice(yrs, len(yrs))
        for c in cols:
            w = np.array([cache[a][c][0] for a in bb]); v = np.array([cache[a][c][1] for a in bb])
            out[c].append((w * v).sum() / w.sum())
        bt = pd.concat([allg[a] for a in rng.choice(sorted(allg), len(allg))])
        for c in cols:
            tot[c].append(roc_auc_score(bt.quebra, bt[c]) if bt.quebra.nunique() == 2 else np.nan)
    return {c: np.array(v) for c, v in out.items()}, {c: np.array(v) for c, v in tot.items()}, yrs


anos_g = list(range(2016, 2026))
PORT = {"28/fev": (2, 28), "19/mar": (3, 19), "30/abr": (4, 30)}
reg = []
for nome, (m, d) in PORT.items():
    for y in anos_g:
        fim = pd.Timestamp(y, m, d)
        sl = l4[["sm_rootzone_pctl", "sm_rootzone"]].isel(lat=ii, lon=jj).sel(time=slice(fim - pd.Timedelta(days=6), fim)).mean("time")
        pc, rz = sl.sm_rootzone_pctl.values, sl.sm_rootzone.values
        for cod, msk in cel.items():
            reg.append({"portao": nome, "ano": y, "cod": cod, "pctl": np.nanmean(pc[msk]), "rz": np.nanmean(rz[msk])})
R = pd.DataFrame(reg)
print(f"L4 nos portoes extraido ({time.time() - t0:.0f} s)")
for nome, (m, d) in PORT.items():
    df = p[p.ano.isin(anos_g)].merge(pct_normal(m, d), on=["cod", "ano"]).merge(R[R.portao == nome], on=["cod", "ano"]).dropna()
    g = df.groupby("cod")["rz"]
    df["rz_a"] = df.rz - (g.transform("sum") - df.rz) / (g.transform("count") - 1)
    df["s_chuva"] = -df.pct.clip(upper=3)
    df["s_pctl"] = -df.pctl
    df["s_rza"] = -df.rz_a
    df["s_comb"] = df.groupby("ano")["s_chuva"].rank(pct=True) + df.groupby("ano")["s_pctl"].rank(pct=True)
    df = df.dropna()
    cols = ["s_chuva", "s_pctl", "s_rza", "s_comb"]
    bd, bt, yrs = boot(df, cols)
    print(f"\n  portao {nome}: n={len(df)} municipio-anos, anos com quebra e nao-quebra = {len(yrs)}, taxa {df.quebra.mean():.3f}")
    print(f"    rho(pctl SMAP, % normal IMERG) agrupado = {stats.spearmanr(df.pctl, df.pct).statistic:+.3f}; "
          f"dentro do ano (media) = {np.nanmean([stats.spearmanr(x.pctl, x.pct).statistic for _, x in df.groupby('ano')]):+.3f}")
    for c in cols:
        print(f"    {c:8s} AUC total {roc_auc_score(df.quebra, df[c]):.3f} [{np.nanpercentile(bt[c], 5):.2f},{np.nanpercentile(bt[c], 95):.2f}]"
              f" | dentro do ano {auc_dentro(df, c):.3f} [{np.percentile(bd[c], 5):.2f},{np.percentile(bd[c], 95):.2f}]")
    for c in ["s_pctl", "s_comb"]:
        dd = bd[c] - bd["s_chuva"]; dt = bt[c] - bt["s_chuva"]
        print(f"    {c} - chuva: dentro {auc_dentro(df, c) - auc_dentro(df, 's_chuva'):+.3f} [{np.percentile(dd, 5):+.2f},{np.percentile(dd, 95):+.2f}]"
              f" | total {roc_auc_score(df.quebra, df[c]) - roc_auc_score(df.quebra, df.s_chuva):+.3f} [{np.nanpercentile(dt, 5):+.2f},{np.nanpercentile(dt, 95):+.2f}]")
    if nome == "19/mar":
        al = df.pctl < 20
        print(f"    regra simples 'pctl < 20' em 19/mar: acende em {al.mean():.1%} dos municipio-anos; quebram {df.quebra[al].mean():.2f} "
              f"com alerta (n={al.sum()}) contra {df.quebra[~al].mean():.2f} sem (n={(~al).sum()})")
        print(f"    alertas 'pctl < 20' por ano: {df[al].groupby('ano').size().to_dict()}; "
              f"quebra com alerta por ano: {df[al].groupby('ano').quebra.mean().round(2).to_dict()}")
    Rq = df[df.cod == "2311306"][["ano", "pct", "pctl", "quebra"]]
    print(f"    Quixada (2311306) em {nome}: " + "; ".join(f"{int(r.ano)}: chuva {r.pct:.2f} do normal, pctl {r.pctl:.0f}, "
                                                        f"quebra {int(r.quebra)}" for r in Rq.itertuples()))

# ---------------- D. o percentil pronto do L4 some na estacao seca; percentil proprio para o portao de novembro
print("\n" + "=" * 25, "D. Disponibilidade do sm_rootzone_pctl e percentil proprio (portao de novembro)", "=" * 25)
pc = l4.sm_rootzone_pctl.isel(lat=ii, lon=jj)
rz = l4.sm_rootzone.isel(lat=ii, lon=jj)
tt = pd.DatetimeIndex(l4.time.values)
amostra = np.arange(0, len(tt), 3)
okp = np.isfinite(pc.isel(time=amostra).values[:, mce]).mean(axis=1)
okr = np.isfinite(rz.isel(time=amostra).values[:, mce]).mean(axis=1)
dd = pd.DataFrame({"pctl": okp, "sm_rootzone": okr}, index=tt[amostra])
print("fracao das celulas do CE com valor, por mes do ano (amostra de 1 dia a cada 3):")
print(dd.groupby(dd.index.month).mean().round(3).T.to_string())
fim = tt.max()
ini = fim - pd.Timedelta(days=6)
atual = rz.sel(time=slice(ini, fim)).mean("time").values
hist = []
for y in range(2015, fim.year):
    w = rz.sel(time=slice(ini.replace(year=y), fim.replace(year=y)))
    if w.sizes["time"] >= 5:
        hist.append(w.mean("time").values)
hist = np.array(hist)
prank = (hist < atual[None]).sum(0) / len(hist) * 100
v = prank[mce & np.isfinite(atual)]
sce = np.nanmean(np.where(mce, atual, np.nan)); hce = [np.nanmean(np.where(mce, h, np.nan)) for h in hist]
print(f"SMAP L4 zona da raiz, {ini:%d/%m} a {fim:%d/%m/%Y}, contra a mesma janela de {len(hist)} anos (2015-{fim.year - 1}):")
print(f"  percentil proprio por celula (CE): mediana {np.median(v):.0f}; celulas abaixo de todos os {len(hist)} anos: "
      f"{np.mean(v == 0):.1%}; media do CE {sce:.4f} m3/m3, posto {1 + sum(h < sce for h in hce)} de {len(hce) + 1} (1 = mais seco)")
print("  medias do CE na janela por ano:", {y: round(float(h), 4) for y, h in zip(range(2015, fim.year), hce)})
print(f"tempo total {time.time() - t0:.0f} s")
