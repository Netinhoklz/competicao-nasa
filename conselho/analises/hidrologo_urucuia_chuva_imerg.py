"""Hidrólogo — análise 2b: a queda de chuva do POWER no Oeste da Bahia (Urucuia) aparece também no IMERG (1998–2025)?
Se sim, a perda de água do GRACE no Urucuia é compatível com déficit de chuva, e não só com irrigação."""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np, pandas as pd, xarray as xr, pymannkendall as mk
sys.stdout.reconfigure(encoding="utf-8")
URU = (-46.6, -14.6, -44.0, -10.4)
tot = {}
for a in range(1998, 2026):
    d = xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc")
    v = list(d.data_vars)[0]
    x = d[v].sel(lon=slice(URU[0], URU[2]), lat=slice(URU[1], URU[3]))
    x = x.where(x >= 0)
    tot[a] = float(x.sum("time").mean())
s = pd.Series(tot)
pw = xr.open_dataset(DADOS / "power" / "power_ne_mensal.nc").PRECTOTCORR.sel(lon=slice(URU[0], URU[2]), lat=slice(URU[1], URU[3])).mean(("lat", "lon")).to_series()
pw = (pw * pw.index.days_in_month).groupby(pw.index.year).sum()
j = pd.DataFrame({"imerg": s, "power": pw}).dropna()
print(j.round(0).T.to_string())
for c in j:
    r = mk.original_test(j[c].values); r2 = mk.original_test(j[c].loc[2002:].values)
    print(f"{c}: Sen 1998–2025 {r.slope:+.1f} mm/ano (p={r.p:.3f}) | 2002–2025 {r2.slope:+.1f} (p={r2.p:.3f}) | média {j[c].mean():.0f} mm")
print("r(IMERG, POWER) anual =", round(j.imerg.corr(j.power), 3))
print("média 1998–2011 vs 2012–2025:", {c: (round(j[c].loc[:2011].mean()), round(j[c].loc[2012:].mean())) for c in j})

# atribuição com o IMERG como forçante (reservatório linear, τ = 36 meses; aquecimento 1998–2002)
mens = []
for a in range(1998, 2027):
    d = xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc"); v = list(d.data_vars)[0]
    x = d[v].sel(lon=slice(URU[0], URU[2]), lat=slice(URU[1], URU[3])); x = x.where(x >= 0).mean(("lat", "lon")).to_series()
    mens.append(x.resample("MS").sum())
pm = pd.concat(mens); pm = pm[pm.index < "2026-08-01"]
pa = pm - pm.groupby(pm.index.month).transform("mean")
gr = xr.open_dataset(DADOS / "grace" / "grace_ne_mensal.nc").lwe_thickness.sel(lon=slice(URU[0], URU[2]), lat=slice(URU[1], URU[3])).mean(("lat", "lon")).to_series()
gr.index = pd.to_datetime(gr.index).to_period("M").to_timestamp(); gr = gr.groupby(level=0).mean()
gm = xr.open_dataset(DADOS / "gldas" / "gldas_noah025_mensal_ne.nc")
sm = (gm.SoilMoi0_10cm_inst + gm.SoilMoi10_40cm_inst + gm.SoilMoi40_100cm_inst + gm.SoilMoi100_200cm_inst).sel(lon=slice(URU[0], URU[2]), lat=slice(URU[1], URU[3])).mean(("lat", "lon")).to_series() / 10
sm.index = pd.to_datetime(sm.index)
res = (gr - (sm - sm["2004":"2009"].mean())).dropna()
res = res - res.groupby(res.index.month).transform("mean")
for tau in (24, 36, 48):
    w = np.exp(-np.arange(180) / tau)
    k = pd.Series(np.convolve(pa.values, w)[: len(pa)], index=pa.index).reindex(res.index)
    ok = k.notna() & (res.index >= "2002-06-01")
    a1, b1 = np.polyfit(k[ok], res[ok], 1)
    aj = a1 * k + b1; ne = res - aj
    an = lambda s: s[ok].resample("YE").mean().loc["2003":"2025"]
    t_aj, t_ne, t_res = mk.original_test(an(aj).values), mk.original_test(an(ne).values), mk.original_test(an(res).values)
    print(f"IMERG τ={tau}: r={np.corrcoef(k[ok], res[ok])[0,1]:.3f} | residual {t_res.slope:+.2f} cm/ano | explicado pela chuva {t_aj.slope:+.2f} (p={t_aj.p:.3f}) | não explicado {t_ne.slope:+.2f} (p={t_ne.p:.3f})")
