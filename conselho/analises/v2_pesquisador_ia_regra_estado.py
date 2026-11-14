"""Rodada 2, pesquisador de IA. A regra de alerta: "chuva desde 1/jan < 75% do normal" (canonica) contra regras de ESTADO
da agua no mesmo formato simples, todas fixadas a priori (tercil seco = percentil < 33,3, convencao da previsao sazonal):
  * API30: indice de chuva antecedente do IMERG (memoria exponencial de 30 dias) no tercil seco dos outros anos 1998-2025;
  * controle de taxa de alerta: chuva desde 1/jan no tercil seco dos outros anos (mesma taxa do API);
  * SMAP:  sm_rootzone_pctl (media dos 7 dias ate o portao) < 33,3 (so 2016-2025).
Portoes 19/mar e 30/abr; quebra canonica de milho e feijao. Mostra P(quebra | alerta), P(quebra | sem alerta), quantos
acendem, recall em 2016 e 2025, IC90 por bootstrap de anos da razao P(q|alerta)/P(q|sem alerta), e Quixada 2016-2025.
Nao escolhe limiar olhando o teste. So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from scipy.signal import lfilter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 230)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
rng = np.random.default_rng(7)
PORT = {"19/mar": (3, 19), "30/abr": (4, 30)}
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
    return p.dropna(subset=["razao"])[["cod", "ano", "razao", "quebra"]]


CULT = {"milho": serie("Milho (em gr"), "feijao": serie("Feij")}
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
chuva = chuva.asfreq("D")
anos_c = list(range(1998, 2026))
API = pd.DataFrame(lfilter([1.0], [1.0, -np.exp(-1 / 30.0)], chuva.fillna(0).values, axis=0), index=chuva.index, columns=chuva.columns)

ds = xr.open_dataset("E:/campeonato-nasa/dados/smap/smap_l4_diario_ne.nc")["sm_rootzone_pctl"].sel(
    lat=slice(-2.4, -8.1), lon=slice(-41.7, -37.0), time=slice("2016-01-01", "2025-05-05")).load()
lat, lon = ds.lat.values, ds.lon.values
LL, LA = np.meshgrid(lon, lat)
pts = gpd.GeoDataFrame({"iy": np.repeat(np.arange(len(lat)), len(lon)), "ix": np.tile(np.arange(len(lon)), len(lat))},
                       geometry=gpd.points_from_xy(LL.ravel(), LA.ravel()), crs="EPSG:4326")
mun = municipios_ce_gdf()[["codarea", "geometry"]]
mun["cod"] = mun.codarea.astype(str).str[:7]
jn = gpd.sjoin(pts, mun, predicate="within")
cel = {c: list(zip(g.iy, g.ix)) for c, g in jn.groupby("cod")}
for c in [c for c in mun.cod if c not in cel]:
    rp = mun.loc[mun.cod == c].geometry.iloc[0].representative_point()
    cel[c] = [(int(np.abs(lat - rp.y).argmin()), int(np.abs(lon - rp.x).argmin()))]
v = ds.values
SP = pd.DataFrame({c: np.nanmean(np.stack([v[:, iy, ix] for iy, ix in cel[c]], 1), 1) for c in sorted(cel)},
                  index=pd.DatetimeIndex(ds.time.values))

linhas = []
for gn, (m, d) in PORT.items():
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_c}).T
    ap = pd.DataFrame({a: API.loc[f"{a}-{m:02d}-{d:02d}"] for a in anos_c}).T.astype("float64")
    for a in anos_c:
        o = ap.drop(index=a)
        pa = (o.lt(ap.loc[a], axis=1).sum() + 0.5 * o.eq(ap.loc[a], axis=1).sum()) / o.notna().sum() * 100
        pr = ac.loc[a] / ac.drop(index=a).median()
        oc = ac.drop(index=a)
        prp = (oc.lt(ac.loc[a], axis=1).sum() + 0.5 * oc.eq(ac.loc[a], axis=1).sum()) / oc.notna().sum() * 100
        fim = pd.Timestamp(a, m, d)
        sp = SP.loc[fim - pd.Timedelta(days=6):fim].mean() if a >= 2016 else pd.Series(np.nan, index=SP.columns)
        for c in ac.columns:
            linhas.append({"portao": gn, "ano": a, "cod": c, "pct": pr[c], "pct_p": prp[c], "api_p": pa[c], "s_p": sp.get(c, np.nan)})
X = pd.DataFrame(linhas)
X["al_chuva"] = X.pct < 0.75
X["al_api"] = X.api_p < 100 / 3
X["al_chuva_t"] = X.pct_p < 100 / 3  # controle de taxa: chuva acumulada desde 1/jan no tercil seco
X["al_smap"] = X.s_p < 100 / 3


def razao_ic(df, col, nb=2000):
    g = {a: q for a, q in df.groupby("ano")}
    anos = list(g)
    out = []
    for _ in range(nb):
        b = pd.concat([g[a] for a in rng.choice(anos, len(anos))])
        pa, pn = b.loc[b[col], "quebra"].mean(), b.loc[~b[col], "quebra"].mean()
        if b[col].sum() > 0 and pn > 0:
            out.append(pa / pn)
    return np.percentile(out, [5, 95])


def tabela(df, regras, titulo):
    print(f"\n  {titulo}: n = {len(df)} mun-anos, taxa de quebra {df.quebra.mean():.3f}")
    for col in regras:
        al = df[col]
        pa, pn = df.loc[al, "quebra"].mean(), df.loc[~al, "quebra"].mean()
        lo, hi = razao_ic(df, col)
        rec = df.loc[al & (df.quebra == 1)].shape[0] / max(df.quebra.sum(), 1)
        r16 = df[(df.ano == 2016)]
        r25 = df[(df.ano == 2025)]
        f = lambda r: f"{int((r[col] & (r.quebra == 1)).sum())}/{int(r.quebra.sum())}" if len(r) else "-"
        print(f"    {col:9s}: acende {al.mean():.0%} | P(q|alerta) {pa:.2f} (n={int(al.sum())}) | P(q|sem) {pn:.2f} | razao {pa / pn:.1f}x "
              f"IC90 [{lo:.1f},{hi:.1f}] | recall {rec:.0%} | 2016 {f(r16)} | 2025 {f(r25)} | alarmes falsos {1 - pa:.0%}")


for cult, Y in CULT.items():
    for gn in PORT:
        print("\n" + "=" * 12, f"{cult} | {gn}", "=" * 12)
        df = X[X.portao == gn].merge(Y, on=["cod", "ano"]).dropna(subset=["pct", "api_p"])
        tabela(df[(df.ano >= 1998)], ["al_chuva", "al_chuva_t", "al_api"], "1998-2025 (28 quadras)")
        tabela(df[(df.ano >= 2016)].dropna(subset=["s_p"]), ["al_chuva", "al_chuva_t", "al_api", "al_smap"], "2016-2025 (10 quadras, mesmas amostras)")

print("\n" + "=" * 12, "Quixada (2311306): alertas por ano (milho; razao do PAM)", "=" * 12)
qx = "2311306"
Q = X[X.cod == qx].pivot_table(index="ano", columns="portao", values=["pct", "api_p", "s_p"])
Q.columns = [f"{a}_{b}" for a, b in Q.columns]
Q["milho"] = CULT["milho"][CULT["milho"].cod == qx].set_index("ano").razao
Q["feijao"] = CULT["feijao"][CULT["feijao"].cod == qx].set_index("ano").razao
print(Q.loc[2010:].round(2).to_string())
for col, thr, nome in [("pct_30/abr", 0.75, "chuva<75%"), ("api_p_30/abr", 100 / 3, "API tercil seco"), ("s_p_30/abr", 100 / 3, "SMAP tercil seco")]:
    for gn in ["19/mar", "30/abr"]:
        cc = col.replace("30/abr", gn)
        z = Q[[cc, "milho"]].dropna()
        al = z[cc] < thr
        print(f"  Quixada {nome} em {gn}: acendeu {int(al.sum())} vezes em {len(z)} anos; acertou {int((al & (z.milho < 0.5)).sum())}; "
              f"quebras do milho nesses anos: {int((z.milho < 0.5).sum())}")
