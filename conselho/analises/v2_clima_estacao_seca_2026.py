"""Cientista do clima - Rodada 2, analise 1: a estacao seca de 2026 (IMERG V07 Late/Early ate 13/11) e o que ela informa.

A. Calibracao: IMERG V07 Late (direto do GES DISC) x IMERG via POWER (IMERG_PRECTOT, base historica) na sobreposicao
   01/ago-14/set/2026, e Late x Early em 01-12/nov/2026. Mesma grade 0,1 graus; media das celulas cujo centro cai no Ceara.
B. A estacao seca 2026 (01/ago-13/nov) contra 1998-2025, no Ceara e em Quixada (2311306): total, % da mediana, posto.
   Contexto: a quadra de 2026 (fev-mai) em % da mediana 1998-2025.
C. Teste PRE-REGISTRADO (uma janela so, a que o produto tem hoje: 01/ago-13/nov do ano t-1):
   a chuva da estacao seca informa a quadra do ano t (chuva fev-mai, % da mediana) ou a fracao de municipios em quebra
   canonica do milho? Unidade = ano; Spearman com IC90 por bootstrap de anos. Ja sabido (rodada 1): ago-out rho -0,06.
So le arquivos; nao escreve nada alem da saida no terminal.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, DERIV, REF

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import shapely
from scipy import stats

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
rng = np.random.default_rng(0)
IM = DADOS / "imerg"
QX = "2311306"

uf = gpd.read_file(REF / "ceara_uf.geojson").geometry.union_all()
mun = gpd.read_file(REF / "ceara_municipios.geojson")
qx_geom = mun[mun.codarea.astype(str) == QX].geometry.iloc[0]


def mascara(lat, lon, geom):
    LO, LA = np.meshgrid(lon, lat)
    return shapely.contains_xy(geom, LO, LA)


def serie_area(da, geom, nome_lat="lat", nome_lon="lon"):
    lat = da[nome_lat].values.astype(float); lon = da[nome_lon].values.astype(float)
    m = mascara(lat, lon, geom)
    if m.sum() == 0:  # municipio menor que a celula: celula mais proxima do centroide
        c = geom.centroid
        m = np.zeros_like(m); m[np.abs(lat - c.y).argmin(), np.abs(lon - c.x).argmin()] = True
    v = da.values[:, m]
    return pd.Series(np.nanmean(v, axis=1), index=pd.DatetimeIndex(da.time.values)), int(m.sum())


# ---------------- historico IMERG via POWER (Ceara), 1998-2026
hist_ce, hist_qx = [], []
for ano in range(1998, 2027):
    ds = xr.open_dataset(IM / f"imerg_ce_diario_{ano}.nc")
    s, n_ce = serie_area(ds["precip"], uf)
    q, n_qx = serie_area(ds["precip"], qx_geom)
    hist_ce.append(s); hist_qx.append(q)
H_ce = pd.concat(hist_ce); H_qx = pd.concat(hist_qx)
print(f"celulas IMERG 0,1 no Ceara: {n_ce}; em Quixada: {n_qx}; historico ate {H_ce.index.max():%Y-%m-%d}")

# ---------------- IMERG V07 Late e Early recentes
L = xr.open_dataset(IM / "imerg_v07_late_diario_ne_recente.nc")["precipitation"]
E = xr.open_dataset(IM / "imerg_v07_early_diario_ne_recente.nc")["precipitation"]
if L.dims[1] != "lat":
    L = L.transpose("time", "lat", "lon"); E = E.transpose("time", "lat", "lon")
L_ce, _ = serie_area(L, uf); L_qx, _ = serie_area(L, qx_geom)
E_ce, _ = serie_area(E, uf); E_qx, _ = serie_area(E, qx_geom)
print(f"Late: {L_ce.index.min():%Y-%m-%d} -> {L_ce.index.max():%Y-%m-%d}; Early: {E_ce.index.min():%Y-%m-%d} -> {E_ce.index.max():%Y-%m-%d}")

print("\n" + "=" * 25, "A. Calibracao entre produtos (Ceara, media de area)", "=" * 25)
sob = slice("2026-08-01", "2026-09-14")
a, b = H_ce.loc[sob], L_ce.loc[sob]
print(f"  01/ago-14/set/2026: POWER-IMERG {a.sum():.1f} mm | Late {b.sum():.1f} mm | razao Late/POWER {b.sum() / a.sum():.2f} | r diario {np.corrcoef(a, b)[0, 1]:.2f} (n={len(a)} dias)")
aq, bq = H_qx.loc[sob], L_qx.loc[sob]
print(f"  Quixada, mesmo periodo: POWER-IMERG {aq.sum():.1f} mm | Late {bq.sum():.1f} mm")
sn = slice("2026-11-01", "2026-11-12")
print(f"  01-12/nov/2026: Late {L_ce.loc[sn].sum():.1f} mm | Early {E_ce.loc[sn].sum():.1f} mm (Ceara); Quixada Late {L_qx.loc[sn].sum():.1f} | Early {E_qx.loc[sn].sum():.1f}")

# serie 2026 da estacao seca: Late ate 12/11 + Early em 13/11
R_ce = pd.concat([L_ce.loc["2026-08-01":"2026-11-12"], E_ce.loc["2026-11-13":"2026-11-13"]])
R_qx = pd.concat([L_qx.loc["2026-08-01":"2026-11-12"], E_qx.loc["2026-11-13":"2026-11-13"]])

print("\n" + "=" * 25, "B. Estacao seca 2026 (01/ago-13/nov) contra 1998-2025", "=" * 25)
JAN = [("ago", "08-01", "08-31"), ("set", "09-01", "09-30"), ("out", "10-01", "10-31"), ("01-13/nov", "11-01", "11-13"),
       ("01/ago-13/nov", "08-01", "11-13")]
for rot, H, R in [("Ceara", H_ce, R_ce), ("Quixada", H_qx, R_qx)]:
    print(f"  {rot}:")
    for nome, i, f in JAN:
        h = pd.Series({a: H.loc[f"{a}-{i}":f"{a}-{f}"].sum() for a in range(1998, 2026)})
        v = R.loc[f"2026-{i}":f"2026-{f}"].sum()
        pos = int((h < v).sum()) + 1
        print(f"    {nome:14s}: 2026 = {v:6.1f} mm | mediana 1998-2025 = {h.median():6.1f} mm ({v / h.median() * 100 if h.median() > 0 else np.nan:5.0f}%)"
              f" | posto {pos} de 29 (1 = mais seco) | min {h.min():.1f} max {h.max():.1f}")
q26 = {}
for rot, H in [("Ceara", H_ce), ("Quixada", H_qx)]:
    h = pd.Series({a: H.loc[f"{a}-02-01":f"{a}-05-31"].sum() for a in range(1998, 2027)})
    q26[rot] = h
    print(f"  quadra (fev-mai) 2026 em {rot}: {h[2026]:.0f} mm = {h[2026] / h.loc[:2025].median() * 100:.0f}% da mediana 1998-2025; posto {int((h.loc[:2025] < h[2026]).sum()) + 1} de 29")

# ---------------- C. teste pre-registrado
print("\n" + "=" * 25, "C. A estacao seca (01/ago-13/nov, ano t-1) informa a quadra do ano t?", "=" * 25)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha


def med_outros(g):
    v = g["r"].values
    out = np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])
    return pd.Series(out, index=g.index)


p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
p["quebra"] = ((p.r / p.ref) < 0.5).astype(int)
p = p.dropna(subset=["ref"])
frac = p.groupby("ano").quebra.mean()
qx_q = p[p.cod_local.astype(str).str[:7] == QX].set_index("ano").quebra

anos = list(range(1999, 2027))
seca = pd.Series({t: H_ce.loc[f"{t - 1}-08-01":f"{t - 1}-11-13"].sum() for t in anos})
quadra = q26["Ceara"] / q26["Ceara"].loc[:2025].median()
seca_qx = pd.Series({t: H_qx.loc[f"{t - 1}-08-01":f"{t - 1}-11-13"].sum() for t in anos})
quadra_qx = q26["Quixada"] / q26["Quixada"].loc[:2025].median()


def sp_boot(x, y, nb=2000):
    d = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    r, pv = stats.spearmanr(d.x, d.y)
    bs = []
    for _ in range(nb):
        i = rng.integers(0, len(d), len(d))
        bs.append(stats.spearmanr(d.x.values[i], d.y.values[i])[0])
    return r, pv, np.nanpercentile(bs, 5), np.nanpercentile(bs, 95), len(d)


for rot, x, y in [("Ceara: seca(t-1) x quadra fev-mai(t) % mediana", seca, quadra),
                  ("Ceara: seca(t-1) x fracao de municipios em quebra do milho(t)", seca, frac),
                  ("Quixada: seca(t-1) x quadra fev-mai(t)", seca_qx, quadra_qx),
                  ("Quixada: seca(t-1) x quebra do milho(t) (0/1)", seca_qx, qx_q)]:
    r, pv, lo, hi, n = sp_boot(x, y)
    print(f"  {rot:65s}: rho={r:+.2f} IC90 [{lo:+.2f},{hi:+.2f}] p={pv:.2f} n={n} anos")
# anos com estacao seca tao seca quanto ou mais que 2026 e o que veio depois
v26 = R_ce.loc["2026-08-01":"2026-11-13"].sum()
sec = seca.loc[:2026]
mais = sec[sec <= v26 * 1.0].index.tolist()
print(f"\n  estacao seca 2026 = {v26:.1f} mm; anos t com estacao seca (t-1) <= 2026: {mais}")
for t in mais:
    print(f"    quadra {t}: {quadra.get(t, np.nan) * 100:.0f}% da mediana; fracao em quebra {frac.get(t, np.nan) if t in frac else float('nan'):.2f}")
qa = quadra.reindex(sec.index)
print(f"\n  quartil seco da estacao seca (t-1) -> quadra mediana {qa[sec <= sec.quantile(0.25)].median() * 100:.0f}% | "
      f"quartil umido -> {qa[sec >= sec.quantile(0.75)].median() * 100:.0f}%  (n={int((sec <= sec.quantile(0.25)).sum())} anos cada)")
fa = frac.reindex(sec.index)
print(f"  fracao media em quebra: quartil seco {fa[sec <= sec.quantile(0.25)].mean():.2f} | quartil umido {fa[sec >= sec.quantile(0.75)].mean():.2f} | todos {fa.mean():.2f}")
n_q = int((fa.loc[mais] >= 0.5).sum()); print(f"  anos 'catastrofe' (>=50% dos municipios em quebra) entre os {len([t for t in mais if t in fa.dropna().index])} anos com estacao seca <= 2026: {n_q}")
