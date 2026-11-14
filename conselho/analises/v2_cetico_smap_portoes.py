"""Cetico, rodada 2 do conselho: refaz de forma independente o teste de habilidade do SMAP L4 nos portoes.

Regras (as mesmas da curva canonica, arquiteto_final_curvas_quixada.py):
- alvo: quebra canonica do milho (producao/area plantada < 50% da mediana do municipio nos OUTROS anos), PAM 1998-2025;
- chuva: IMERG acumulado desde 1/jan em % do normal (mediana dos outros anos de 1998-2025), cache municipal do estrategista;
- SMAP L4 (SPL4SMGP v008, 13:30 UTC) no DIA do portao, media dos pixels 9 km dentro do municipio
  (municipio sem pixel: pixel mais proximo do centroide);
- PRE-REGISTRO (antes de olhar o resultado): variavel principal = sm_rootzone_pctl (percentil da NASA, sem ajuste nosso);
  regra de alerta SMAP = pctl < 20 (convencao de seca agricola citada na secao 05); nenhuma outra configuracao vai ao pitch.
  Secundaria (so auditoria): zona da raiz em % da mediana dos outros anos SMAP (mesma logica do normal da chuva).
- comparacao PAREADA: mesmos municipio-anos (2016-2025; 2015 so existe a partir de 31/mar e entra como sensibilidade);
- IC90 por bootstrap de ANOS; AUC dentro do ano; logistica deixando o ANO de fora (chuva x chuva+SMAP).
B. Quanto do SMAP L4 e a propria chuva IMERG: R2 deixando o ano de fora de um filtro linear de chuva acumulada (IMERG)
   sobre a anomalia diaria da zona da raiz (serie do estado e painel municipal; total e dentro do dia).
C. Quixada 2023-2025 (as quebras que a chuva nao explica): o SMAP ve algo?
So le arquivos; nao escreve nada.
"""
import sys
import time
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
import shapely
import xarray as xr
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
t0 = time.time()
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
rng = np.random.default_rng(0)

# ---------------- quebra canonica (receita copiada do arquiteto)
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")


def serie(prefixo):
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        out = np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])
        return pd.Series(out, index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref
    p["quebra"] = (p.razao < 0.5).astype(int)
    p["cod"] = p.cod_local.astype(str).str[:7]
    return p.dropna(subset=["razao"])


mi = serie("Milho (em gr")
base = mi[["cod", "ano", "quebra", "razao"]]

chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
anos_imerg = list(range(1998, 2026))
GATES = {"31/jan": (1, 31), "28/fev": (2, 28), "19/mar": (3, 19), "31/mar": (3, 31), "30/abr": (4, 30)}


def pct_normal(m, d):
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_imerg}).T
    out = ac.copy() * np.nan
    for a in anos_imerg:
        out.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return out


# ---------------- SMAP L4: recorte do Ceara, pesos por municipio
l4 = xr.open_dataset("E:/campeonato-nasa/dados/smap/smap_l4_diario_ne.nc")
l4 = l4.sel(lat=slice(-2.5, -8.1), lon=slice(-41.6, -37.0))
_t = pd.to_datetime(l4.time.values)
print(f"SMAP L4: {int(_t.duplicated().sum())} dias duplicados no consolidado (granulos repetidos): "
      f"{sorted(set(str(x)[:10] for x in _t[_t.duplicated()]))}; fico com o primeiro")
l4 = l4.isel(time=np.flatnonzero(~_t.duplicated()))
lo, la = np.meshgrid(l4.lon.values, l4.lat.values)
mun = municipios_ce_gdf()
mun["cod"] = mun.codarea.astype(str)
W = np.zeros((len(mun), lo.size))
sem_pixel = 0
for i, g in enumerate(mun.geometry):
    m = shapely.contains_xy(g, lo, la).ravel()
    if m.sum() == 0:
        c = g.centroid
        m = np.zeros(lo.size, bool)
        m[np.argmin((lo.ravel() - c.x) ** 2 + (la.ravel() - c.y) ** 2)] = True
        sem_pixel += 1
    W[i, m] = 1.0 / m.sum()
print(f"SMAP L4 recorte CE: {l4.sizes}; municipios sem pixel 9 km dentro (usam o mais proximo): {sem_pixel}")


def agrega(da):
    """da (time, lat, lon) -> DataFrame time x municipio (media; ignora NaN renormalizando pesos)."""
    v = da.values.reshape(da.sizes["time"], -1)
    ok = np.isfinite(v)
    num = np.where(ok, v, 0) @ W.T
    den = ok.astype(float) @ W.T
    return pd.DataFrame(num / np.where(den > 0, den, np.nan), index=pd.to_datetime(da.time.values), columns=mun.cod.values)


datas = [pd.Timestamp(a, m, d) for a in range(2015, 2027) for (m, d) in GATES.values()]
datas = [x for x in datas if x >= pd.Timestamp("2015-03-31") and x <= pd.Timestamp(l4.time.values.max())]
sub = l4.sel(time=datas)
PC = agrega(sub.sm_rootzone_pctl.load())
RZg = agrega(sub.sm_rootzone.load())
print(f"[{time.time() - t0:.0f}s] SMAP nos portoes: {len(datas)} datas")

# ---------------- A. teste pareado nos portoes


def auc_boot(df, cols, nboot=1000):
    yrs = df.ano.unique()
    g = {a: df[df.ano == a] for a in yrs}
    pt = {c: roc_auc_score(df.quebra, df[c]) for c in cols}
    bs = []
    for _ in range(nboot):
        bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            bs.append([roc_auc_score(bb.quebra, bb[c]) for c in cols])
    return pt, np.array(bs)


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, g[col])
            den += w
    return num / den if den else np.nan


print("\n" + "=" * 20, "A. SMAP L4 x chuva IMERG nos portoes (pareado, quebra canonica do milho)", "=" * 20)
res = []
for anos_teste, rot in [(range(2016, 2026), "2016-2025"), (range(2015, 2026), "2015-2025 (so portoes >= 31/mar)")]:
    for gn, (m, d) in GATES.items():
        if rot.startswith("2015") and (m, d) < (3, 31):
            continue
        P = pct_normal(m, d)
        pl = P.stack().rename("pct").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})
        sm = []
        rzd = {a: RZg.loc[pd.Timestamp(a, m, d)] for a in anos_teste if pd.Timestamp(a, m, d) in RZg.index}
        rzdf = pd.DataFrame(rzd).T
        for a in rzd:
            rel = rzdf.loc[a] / rzdf.drop(index=a).median()
            sm.append(pd.DataFrame({"ano": a, "cod": PC.columns, "pctl": PC.loc[pd.Timestamp(a, m, d)].values,
                                    "rz_rel": rel.values}))
        sm = pd.concat(sm)
        df = base[base.ano.isin(list(anos_teste))].merge(pl, on=["cod", "ano"]).merge(sm, on=["cod", "ano"]).dropna()
        # escores: maior = mais risco
        df["s_chuva"] = -df.pct.clip(upper=3)
        df["s_smap"] = -df.pctl
        df["s_rzrel"] = -df.rz_rel
        pt, bs = auc_boot(df, ["s_chuva", "s_smap", "s_rzrel"])
        dif = bs[:, 1] - bs[:, 0]
        # logistica deixando o ano de fora: chuva vs chuva + SMAP (pctl)
        df["p_c"] = np.nan
        df["p_cs"] = np.nan
        for a in df.ano.unique():
            tr, te = df.ano != a, df.ano == a
            for cols, alvo in [(["s_chuva"], "p_c"), (["s_chuva", "s_smap"], "p_cs")]:
                lr = LogisticRegression().fit(df.loc[tr, cols], df.loc[tr, "quebra"])
                df.loc[te, alvo] = lr.predict_proba(df.loc[te, cols])[:, 1]
        a_c, a_cs = roc_auc_score(df.quebra, df.p_c), roc_auc_score(df.quebra, df.p_cs)
        al_s, al_c = df.pctl < 20, df.pct < 0.75
        q = df.quebra.astype(bool)
        r_sc = df.groupby("ano")[["pctl", "pct"]].mean().corr(method="spearman").iloc[0, 1]
        s16 = df[df.ano != 2016]
        an = df.groupby("ano").agg(q=("quebra", "mean"), s=("pctl", "median"), c=("pct", "median"))
        print(f"  [{rot} {gn}] sem 2016: AUC chuva {roc_auc_score(s16.quebra, s16.s_chuva):.3f} | SMAP pctl "
              f"{roc_auc_score(s16.quebra, s16.s_smap):.3f} (quebras {int(s16.quebra.sum())}) | rho anual (fracao em quebra x mediana): "
              f"SMAP {an.q.corr(-an.s, method='spearman'):+.2f}, chuva {an.q.corr(-an.c, method='spearman'):+.2f} (n = {len(an)} anos)")
        lin = {"anos": rot, "portao": gn, "n": len(df), "n_anos": df.ano.nunique(), "quebras": int(q.sum()),
               "AUC_chuva": pt["s_chuva"], "AUC_smap_pctl": pt["s_smap"], "AUC_smap_rzrel": pt["s_rzrel"],
               "dif_smap_menos_chuva": pt["s_smap"] - pt["s_chuva"],
               "dif_IC90": f"[{np.percentile(dif, 5):+.2f},{np.percentile(dif, 95):+.2f}]",
               "IC90_smap": f"[{np.percentile(bs[:, 1], 5):.2f},{np.percentile(bs[:, 1], 95):.2f}]",
               "IC90_chuva": f"[{np.percentile(bs[:, 0], 5):.2f},{np.percentile(bs[:, 0], 95):.2f}]",
               "dentro_chuva": auc_dentro(df, "s_chuva"), "dentro_smap": auc_dentro(df, "s_smap"),
               "LOYO_chuva": a_c, "LOYO_chuva+smap": a_cs,
               "alerta_smap_P(q|a)": q[al_s].mean(), "n_alerta_smap": int(al_s.sum()), "P(q|sem)_smap": q[~al_s].mean(),
               "alerta_chuva_P(q|a)": q[al_c].mean(), "n_alerta_chuva": int(al_c.sum()), "P(q|sem)_chuva": q[~al_c].mean(),
               "rho_anual_smap_chuva": r_sc}
        res.append(lin)
        if rot.startswith("2015") and gn == "30/abr":
            pa = df.groupby("ano").apply(lambda g: pd.Series({
                "quebra": g.quebra.mean(), "alertas_smap": int((g.pctl < 20).sum()),
                "acertos_smap": int(((g.pctl < 20) & (g.quebra == 1)).sum()), "alertas_chuva": int((g.pct < 0.75).sum()),
                "acertos_chuva": int(((g.pct < 0.75) & (g.quebra == 1)).sum()), "quebras": int(g.quebra.sum())}))
            print("  Por ano, portao 30/abr (2015-2025): onde caem os alertas SMAP (pctl < 20) e os da chuva (< 75%)")
            print(pa.round(2).to_string())
        if rot == "2016-2025" and gn == "19/mar":
            por_ano =df.groupby("ano").agg(quebra=("quebra", "mean"), pctl_med=("pctl", "median"), pct_chuva_med=("pct", "median"),
                                             alerta_smap=("pctl", lambda s: (s < 20).mean()), alerta_chuva=("pct", lambda s: (s < 0.75).mean()))
R = pd.DataFrame(res)
print(R[["anos", "portao", "n", "n_anos", "quebras", "AUC_chuva", "IC90_chuva", "AUC_smap_pctl", "IC90_smap", "AUC_smap_rzrel",
         "dif_smap_menos_chuva", "dif_IC90"]].round(3).to_string(index=False))
print()
print(R[["anos", "portao", "dentro_chuva", "dentro_smap", "LOYO_chuva", "LOYO_chuva+smap", "rho_anual_smap_chuva"]].round(3).to_string(index=False))
print()
print(R[["anos", "portao", "alerta_chuva_P(q|a)", "n_alerta_chuva", "P(q|sem)_chuva", "alerta_smap_P(q|a)", "n_alerta_smap",
         "P(q|sem)_smap"]].round(3).to_string(index=False))
print("\nPor ano, portao 19/mar (2016-2025): fracao de municipios em quebra, medianas e fracao em alerta")
print(por_ano.round(2).to_string())

# ---------------- B. quanto do L4 e a chuva IMERG
print("\n" + "=" * 20, "B. Quanto da zona da raiz do SMAP L4 e reproduzido so pela chuva IMERG (filtro linear, ano fora)", "=" * 20)
fim = min(pd.Timestamp(l4.time.values.max()), chuva.index.max())
rz = agrega(l4.sm_rootzone.sel(time=slice("2015-03-31", fim)).load())
print(f"[{time.time() - t0:.0f}s] zona da raiz diaria agregada: {rz.shape}")
doy = rz.index.dayofyear
clim = rz.groupby(doy).mean().rolling(31, center=True, min_periods=1).mean()
anom = rz - clim.loc[doy].values
JAN = [10, 30, 60, 90, 180, 365]
cs = chuva.cumsum()
X = {k: (cs - cs.shift(k)).reindex(rz.index) for k in JAN}


def r2_loyo(y, Xm, anos):
    pred = np.full(len(y), np.nan)
    for a in np.unique(anos):
        tr, te = anos != a, anos == a
        pred[te] = LinearRegression().fit(Xm[tr], y[tr]).predict(Xm[te])
    return 1 - np.nansum((y - pred) ** 2) / np.nansum((y - y.mean()) ** 2)


# B1: serie do estado
ye = anom.mean(axis=1)
Xe = np.column_stack([X[k].mean(axis=1) for k in JAN])
ok = np.isfinite(Xe).all(1) & np.isfinite(ye.values)
Xd = pd.DataFrame(Xe, index=rz.index)
Xd = Xd - Xd.groupby(Xd.index.dayofyear).transform("mean")  # chuva acumulada tambem dessazonalizada
r2e = r2_loyo(ye.values[ok], Xd.values[ok], rz.index.year.values[ok])
print(f"  B1 serie diaria do estado (anomalia): R2 ano fora = {r2e:.3f} (n dias = {ok.sum()})")
# B2: painel municipal, a cada 5 dias
idx = np.arange(0, len(rz), 5)
ys, xs, ans, dts = [], [], [], []
for i in idx:
    y = anom.iloc[i].values
    xx = np.column_stack([X[k].iloc[i].values for k in JAN])
    ys.append(y); xs.append(xx); ans.append(np.full(len(y), rz.index[i].year)); dts.append(np.full(len(y), i))
y, Xm, ans, dts = np.concatenate(ys), np.vstack(xs), np.concatenate(ans), np.concatenate(dts)
okm = np.isfinite(y) & np.isfinite(Xm).all(1)
y, Xm, ans, dts = y[okm], Xm[okm], ans[okm], dts[okm]
# dessazonaliza a chuva acumulada por municipio-doy seria caro; usa efeito do municipio x mes via regressao com o clima
# medio: aqui a anomalia de chuva = chuva acumulada - media do mesmo doy no municipio (aproximada pela media por doy e mun)
Xa = Xm.copy()
dfx = pd.DataFrame(Xm)
dfx["doy"] = rz.index[dts].dayofyear // 5
dfx["mun"] = np.tile(np.arange(rz.shape[1]), len(idx))[okm]
Xa = (dfx[list(range(len(JAN)))] - dfx.groupby(["mun", "doy"])[list(range(len(JAN)))].transform("mean")).values
r2m = r2_loyo(y, Xa, ans)
# B3: dentro do dia (tira a media do estado no dia de y e de X)
yd = y - pd.Series(y).groupby(dts).transform("mean").values
Xdd = Xa - pd.DataFrame(Xa).groupby(dts).transform("mean").values
r2d = r2_loyo(yd, Xdd, ans)
print(f"  B2 painel municipal (anomalia, 1 dia a cada 5): R2 ano fora = {r2m:.3f} (n = {len(y)})")
print(f"  B3 dentro do dia (ordem entre municipios): R2 ano fora = {r2d:.3f}")
print("  Leitura: R2 alto = a zona da raiz do L4 no Ceara e, em grande parte, a memoria da chuva IMERG que o forca;"
      " o resto mistura fisica do modelo (solo, vegetacao, ET), diferenca de produto de chuva e assimilacao do Tb.")

# ---------------- C. Quixada
print("\n" + "=" * 20, "C. Quixada (2311306): quebras de 2023-2025 com chuva normal; o SMAP ve?", "=" * 20)
qx = "2311306"
T = mi[mi.cod == qx].set_index("ano")[["razao"]].rename(columns={"razao": "milho_razao"})
for gn, (m, d) in [("19/mar", (3, 19)), ("30/abr", (4, 30))]:
    T[f"chuva_{gn}"] = pct_normal(m, d)[qx]
    T[f"smap_pctl_{gn}"] = pd.Series({a: PC.loc[pd.Timestamp(a, m, d), qx] for a in range(2015, 2026)
                                       if pd.Timestamp(a, m, d) in PC.index})
print(T.loc[2015:2025].round(2).to_string())
print(f"\n[{time.time() - t0:.0f}s] fim")
