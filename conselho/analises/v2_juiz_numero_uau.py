"""Juiz da NASA Space Apps (banca adversaria, rodada 2): o numero-uau "9 contra 64 de 127" se reproduz, e o que ele mede?

Pre-declarado ANTES de rodar (nada escolhido pelo resultado; todas as linhas sao impressas):
 A. Reproducao independente do 9/64/127 lendo o SMAP L4 .nc cru (so 13-19/mar e 24-30/abr de 2016-2025, recorte do CE),
    com agregacao municipal propria (media das celulas de 9 km com centro no poligono; sem celula, a mais proxima do
    centroide), deduplicando datas repetidas pela media. Luz 2 = percentil da zona da raiz < 20 (dia e media de 7 dias).
    Luz 1 = chuva IMERG desde 1/jan < 75% da mediana dos outros anos 1998-2025 (cache municipal do estrategista).
    Quebra canonica do milho (receita do arquiteto, copiada).
 B. O que o numero mede DENTRO de 2016 e de 2025: acertos esperados se as mesmas N luzes caissem ao acaso
    (N x taxa de quebra do ano), p hipergeometrico (cauda superior) e AUC dentro do ano.
 C. Linha de base so-IMERG, mesma forma da luz 1 (< 75% do normal), so muda a janela: (i) API tau = 13 d (o substituto
    da luz 2 que a proposta ja usa em 1998-2015) e (ii) chuva dos 30 dias ate o portao. Contagens 2016/2021/2025.
 D. Nivel do ano (10 quadras): fracao de municipios com luz x fracao em quebra; Spearman (n = 10).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import warnings

import numpy as np
import pandas as pd
import shapely
import xarray as xr
from scipy import stats
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
ANOS_S = list(range(2016, 2026))
ANOS = list(range(1998, 2026))

# ---------------- quebra canonica (copiada do arquiteto)
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha


def med_outros(g):
    v = g["r"].values
    return pd.Series([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=g.index)


p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
p["razao"] = p.r / p.ref
p["quebra"] = (p.razao < 0.5).astype(int)
p["cod"] = p.cod_local.astype(str).str[:7]
base = p.dropna(subset=["razao"])[["cod", "ano", "quebra"]]

# ---------------- A. SMAP L4 cru, agregacao propria
mun = municipios_ce_gdf()
cod_col = next(c for c in mun.columns if "cod" in c.lower() or c.lower() in ("id", "codarea"))
mun["cod"] = mun[cod_col].astype(str).str[:7]
ds = xr.open_dataset("E:/campeonato-nasa/dados/smap/smap_l4_diario_ne.nc")["sm_rootzone_pctl"]
ds = ds.sel(lat=slice(-2.4, -8.1), lon=slice(-41.6, -36.9))
LO, LA = np.meshgrid(ds.lon.values, ds.lat.values)
masks = {}
for cod, g in zip(mun.cod, mun.geometry):
    m = shapely.contains_xy(g, LO.ravel(), LA.ravel())
    if m.sum() == 0:
        c = g.centroid
        m = np.zeros(LO.size, bool)
        m[np.argmin((LO.ravel() - c.x) ** 2 + (LA.ravel() - c.y) ** 2)] = True
    masks[cod] = m


def smap_janela(a, m, d):
    t1 = pd.Timestamp(a, m, d)
    x = ds.sel(time=slice(t1 - pd.Timedelta(days=6), t1 + pd.Timedelta(hours=23))).load()
    x["time"] = pd.DatetimeIndex(x.time.values).normalize()
    x = x.groupby("time").mean()
    v = x.values.reshape(x.sizes["time"], -1)
    dia = {c: np.nanmean(v[-1, mk]) for c, mk in masks.items()}
    sete = {c: np.nanmean(np.nanmean(v[:, mk], 1)) for c, mk in masks.items()}
    return pd.DataFrame({"cod": list(dia), "ano": a, "p_dia": list(dia.values()), "p_7d": list(sete.values()),
                         "ndias": x.sizes["time"]})


chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
TAU = 13.0


def chuva_ind(m, d):
    acum, api, c30 = {}, {}, {}
    for a in ANOS:
        t = pd.Timestamp(a, m, d)
        x = chuva.loc[f"{a}-01-01":t]
        acum[a] = x.sum()
        w = np.exp(-(len(x) - 1 - np.arange(len(x))) / TAU)[:, None]
        api[a] = pd.Series((x.values * w).sum(0), index=x.columns)
        c30[a] = chuva.loc[t - pd.Timedelta(days=29):t].sum()
    out = []
    for nome, dd in [("acum", acum), ("api", api), ("c30", c30)]:
        T = pd.DataFrame(dd).T
        P = T.copy() * np.nan
        for a in ANOS:
            P.loc[a] = T.loc[a] / T.drop(index=a).median()
        out.append(P.stack().rename(nome))
    r = pd.concat(out, axis=1).reset_index()
    r.columns = ["ano", "cod", "acum", "api", "c30"]
    return r


def hiper(df, al, ano):
    g = df[df.ano == ano]
    a = al[df.ano == ano]
    N, K, n, k = len(g), int(g.quebra.sum()), int(a.sum()), int((a & g.quebra.astype(bool)).sum())
    esp = n * K / N if N else np.nan
    pv = stats.hypergeom.sf(k - 1, N, K, n) if n else np.nan
    fa = int((a & ~g.quebra.astype(bool)).sum())
    return f"{k}/{K} com {n} luzes ({fa} de {N-K} sem quebra) | acaso {esp:.1f} | p {pv:.3f} | taxa luz|quebra {k/K:.0%} x luz|sem {fa/max(N-K,1):.0%}"


for gn, (m, d) in {"19/mar": (3, 19), "30/abr": (4, 30)}.items():
    sm = pd.concat([smap_janela(a, m, d) for a in ANOS_S])
    ci = chuva_ind(m, d)
    df = base[base.ano.between(2016, 2025)].merge(ci, on=["cod", "ano"]).merge(sm, on=["cod", "ano"]).dropna()
    print(f"\n===================== [{gn}] milho 2016-2025: n = {len(df)} municipio-anos, {int(df.quebra.sum())} quebras; "
          f"dias SMAP por janela: {sorted(sm.ndias.unique())}")
    luzes = {"chuva desde 1/jan < 75%": df.acum < 0.75, "SMAP dia < 20": df.p_dia < 20, "SMAP 7d < 20": df.p_7d < 20,
             "IMERG API tau13 < 75%": df.api < 0.75, "IMERG 30 d < 75%": df.c30 < 0.75}
    print("  A/B. contagens e o que elas medem dentro do ano")
    for nome, al in luzes.items():
        q = df.quebra.astype(bool)
        print(f"   {nome:<24} pooled: acende {al.mean():5.1%} | P(q|luz) {q[al].mean():.2f} | P(q|sem) {q[~al].mean():.2f}")
        for ano in (2016, 2021, 2025):
            print(f"      {ano}: {hiper(df, al, ano)}")
    print("  AUC (pooled 2016-2025 | dentro de 2016 | dentro de 2025), escore = -variavel:")
    for nome, col in [("chuva desde 1/jan", "acum"), ("SMAP dia", "p_dia"), ("SMAP 7d", "p_7d"), ("API tau13", "api"),
                      ("IMERG 30 d", "c30")]:
        s = -df[col].clip(upper=3) if col in ("acum", "api", "c30") else -df[col]  # razoes de chuva cortadas em 3x
        a16, a25 = df.ano == 2016, df.ano == 2025
        print(f"   {nome:<18} {roc_auc_score(df.quebra, s):.3f} | {roc_auc_score(df.quebra[a16], s[a16]):.3f} | "
              f"{roc_auc_score(df.quebra[a25], s[a25]):.3f}")
    # E (acrescentado depois de ver A-D, declarado aqui antes de rodar E): mesmo ORCAMENTO DE ALARMES.
    # A chuva desde 1/jan com limiar escolhido para acender na MESMA fracao de municipio-anos (pooled 2016-2025)
    # que a luz SMAP 7d < 20; e, dentro de 2016, as N cidades mais secas pela chuva, com N = luzes SMAP de 2016.
    print("  E. mesmo orcamento de alarmes (chuva desde 1/jan com limiar casado na taxa da luz SMAP 7d < 20)")
    q = df.quebra.astype(bool)
    for ref in ("p_7d", "p_dia"):
        taxa = (df[ref] < 20).mean()
        lim = df.acum.quantile(taxa)
        alc = df.acum <= lim
        print(f"   casado com SMAP {ref[2:]}: chuva <= {lim:.2f} do normal acende {alc.mean():.1%} | P(q|luz) {q[alc].mean():.2f} | "
              f"P(q|sem) {q[~alc].mean():.2f} | recall {(alc & q).sum() / q.sum():.1%} | 2016 {int((alc & q)[df.ano == 2016].sum())}/127 "
              f"(luzes {int(alc[df.ano == 2016].sum())}) | 2021 luzes {int(alc[df.ano == 2021].sum())} | 2025 "
              f"{int((alc & q)[df.ano == 2025].sum())}/45 (luzes {int(alc[df.ano == 2025].sum())})")
    g16 = df[df.ano == 2016]
    for ref in ("p_7d", "p_dia"):
        n = int((g16[ref] < 20).sum())
        top = g16.nsmallest(n, "acum")
        print(f"   dentro de 2016, as {n} cidades com menos chuva desde 1/jan: {int(top.quebra.sum())} quebras "
              f"(SMAP {ref[2:]} com as mesmas {n} luzes: {int(g16.quebra[g16[ref] < 20].sum())})")
    print("  D. nivel do ano: fracao de municipios com luz x fracao em quebra")
    t = df.groupby("ano").apply(lambda g: pd.Series({
        "quebra": g.quebra.mean(), "chuva": (g.acum < 0.75).mean(), "smap7d": (g.p_7d < 20).mean(),
        "smapdia": (g.p_dia < 20).mean(), "api": (g.api < 0.75).mean(), "c30": (g.c30 < 0.75).mean()}))
    print(t.round(2).to_string())
    for c in ["chuva", "smap7d", "smapdia", "api", "c30"]:
        print(f"   Spearman(fracao com luz {c}, fracao em quebra) = {stats.spearmanr(t[c], t.quebra)[0]:+.2f} (n = 10)")
