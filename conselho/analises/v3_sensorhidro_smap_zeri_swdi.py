"""v3 - Especialista sensoriamento/hidrologia - Teste 1 (SMAP L4 x Zeri 2018/2021 e Paredes-Trejo 2017).

Perguntas:
 a) Zeri et al. 2018 (Water 10:1421): SMI = (theta-WP)/(FC-WP); ISA vermelho = SMI<0.4 por 7 dias seguidos,
    laranja = 3 dias. O artigo diz que 20/jan/2016 estava umido e 20/fev/2016 em seca severa (rede Cemaden, 20 cm).
    O SMAP L4 (NASA) reproduz esse contraste no Ceara? WP/FC = percentis 5/95 por pixel (metodo de Paredes-Trejo 2017,
    porque nao temos analise de solo por talhao).
 b) Paredes-Trejo & Barbosa 2017 (Water 9:377): SWDI = 10*(theta-FC)/(FC-WP), FC=p95, WP=p5, semana de seca = SWDI<0,
    POD = 0,986 e r = 0,652 com AWD (P - ETP semanal). Quanto do POD vem da propria construcao do indice?
 c) Zeri et al. 2021 (Clim Resil Sustain e7): defasagem de 1 a 1,5 mes do VHI em relacao a anomalia de umidade (SMA).
    Testamos SMAP L4 (zona de raizes) x VHI aproximado com MODIS NDVI+LST (medias do CE), e SPI-1 do IMERG.
 d) Zeri 2021: chuva nov-jul do semiarido (CHIRPS) media 698 mm; 2011-12 = 400, 2012-13 = 553, 2014-15 = 653.
    Razao com a media pelo IMERG no Ceara.
Rodar: E:/campeonato-nasa/venv/Scripts/python.exe -I <este arquivo>
"""
import sys
import time

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import json

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from shapely.geometry import shape, Point
from shapely.prepared import prep

T0 = time.time()
sys.stdout.reconfigure(encoding="utf-8")


def secao(t):
    print("\n" + "=" * 100 + f"\n{t}  [{time.time()-T0:.0f}s]\n" + "=" * 100)


# ---------------------------------------------------------------- SMAP L4 recorte CE
secao("Carregando SMAP L4 (SPL4SMGP v008) no recorte do Ceara")
ds = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
ds = ds.sel(lat=slice(-2.5, -8.0), lon=slice(-41.5, -37.0))
t = pd.DatetimeIndex(ds.time.values)
keep = ~t.duplicated()
ds = ds.isel(time=np.where(keep)[0])
ds = ds.reindex(time=pd.date_range(ds.time.values[0], ds.time.values[-1], freq="D"))
rz = ds["sm_rootzone"].load()
sf = ds["sm_surface"].load()
print("dias:", rz.sizes["time"], "| grade:", rz.sizes["lat"], "x", rz.sizes["lon"], "| dias com falha:",
      int(np.isnan(rz.mean(("lat", "lon"))).sum()))

uf = json.load(open(REF / "ceara_uf.geojson", encoding="utf-8"))
poly = prep(shape(uf["features"][0]["geometry"]))
LA, LO = np.meshgrid(rz.lat.values, rz.lon.values, indexing="ij")
mask = np.array([[poly.contains(Point(lo, la)) for lo, la in zip(rlo, rla)] for rla, rlo in zip(LA, LO)])
valido = mask & np.isfinite(rz.isel(time=slice(0, 60)).mean("time").values)
print("celulas SMAP dentro do CE com dado:", int(valido.sum()))


def smi(da):
    wp = da.quantile(0.05, dim="time")
    fc = da.quantile(0.95, dim="time")
    return (da - wp) / (fc - wp), wp, fc


# ---------------------------------------------------------------- (a) Zeri 2018 SMI / ISA
secao("(a) Zeri 2018 - SMI e ISA com SMAP L4 no Ceara, verao 2015/2016")
for nome, da in [("superficie 0-5 cm", sf), ("zona de raizes 0-100 cm", rz)]:
    s, wp, fc = smi(da)
    abaixo = (s < 0.4).where(np.isfinite(s))
    run7 = abaixo.rolling(time=7).sum() == 7
    run3 = abaixo.rolling(time=3).sum() == 3
    print(f"\n-- {nome}: WP(p5) mediano {float(wp.where(valido).median()):.3f}, FC(p95) mediano "
          f"{float(fc.where(valido).median()):.3f} m3/m3")
    print(f"   {'data':12s} {'SMI medio':>9s} {'%SMI<0,4':>9s} {'%ISA verm(7d)':>13s} {'%ISA lar(3d)':>12s}")
    for d in ["2016-01-10", "2016-01-20", "2016-01-31", "2016-02-10", "2016-02-20", "2016-02-28", "2016-03-15"]:
        sd = s.sel(time=d).values[valido]
        r7 = run7.sel(time=d).values[valido]
        r3 = run3.sel(time=d).values[valido]
        print(f"   {d:12s} {np.nanmean(sd):9.2f} {100*np.mean(sd<0.4):9.1f} {100*np.mean(r7):13.1f} {100*np.mean(r3 & ~r7):12.1f}")
    if nome.startswith("zona"):
        s_rz = s
pct = ds["sm_rootzone_pctl"].sel(time=["2016-01-20", "2016-02-20"]).load()
for d in ["2016-01-20", "2016-02-20"]:
    v = pct.sel(time=d).values[valido]
    print(f"   sm_rootzone_pctl (percentil do proprio L4) {d}: mediana {np.nanmedian(v):.1f} | %<=10: {100*np.nanmean(v<=10):.1f}")

# ---------------------------------------------------------------- (b) Paredes-Trejo 2017 SWDI
secao("(b) Paredes-Trejo 2017 - SWDI com FC=p95 e WP=p5: quanto de 'seca' vem da construcao?")
sem_sf = sf.resample(time="7D").mean()
sem_rz = rz.resample(time="7D").mean()
for nome, d_dia, d_sem in [("superficie", sf, sem_sf), ("raizes", rz, sem_rz)]:
    for base_nome, base in [("p5/p95 da serie diaria", d_dia), ("p5/p95 da serie semanal", d_sem)]:
        wp = base.quantile(0.05, dim="time")
        fc = base.quantile(0.95, dim="time")
        swdi = 10 * (d_sem - fc) / (fc - wp)
        frac = float((swdi < 0).where(np.isfinite(swdi)).mean(("time")).where(valido).mean())
        print(f"   {nome:10s} {base_nome:26s}: fracao de semanas com SWDI<0 = {frac:.3f}")
# media do CE, semanal: SWDI x AWD (IMERG - ET0 POWER)
imerg = xr.concat([xr.open_dataset(DADOS / "imerg" / f"imerg_ce_diario_{a}.nc")["precip"] for a in range(1998, 2027)], dim="time")
LAi, LOi = np.meshgrid(imerg.lat.values, imerg.lon.values, indexing="ij")
mask_i = np.array([[poly.contains(Point(lo, la)) for lo, la in zip(rlo, rla)] for rla, rlo in zip(LAi, LOi)])
p_ce = imerg.where(mask_i).mean(("lat", "lon")).to_series()
et0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"]
et0_ce = et0.mean(("lat", "lon")).to_series()
sf_ce = sf.where(valido).mean(("lat", "lon")).to_series()
rz_ce = rz.where(valido).mean(("lat", "lon")).to_series()
df = pd.concat({"P": p_ce, "ET0": et0_ce, "sf": sf_ce, "rz": rz_ce}, axis=1).loc["2015-04-01":"2026-09-30"].dropna()
w = df.resample("7D").agg({"P": "sum", "ET0": "sum", "sf": "mean", "rz": "mean"})
w["AWD"] = w["P"] - w["ET0"]
for c in ["sf", "rz"]:
    wp, fc = w[c].quantile(0.05), w[c].quantile(0.95)
    w[f"swdi_{c}"] = 10 * (w[c] - fc) / (fc - wp)
seca_ref = w["AWD"] < 0
print(f"\n   media do CE, {len(w)} semanas 2015-2026; semanas com AWD<0 (P<ET0): {100*seca_ref.mean():.1f}%")
for c in ["swdi_sf", "swdi_rz"]:
    prev = w[c] < 0
    pod = (prev & seca_ref).sum() / seca_ref.sum()
    far = (prev & ~seca_ref).sum() / max(prev.sum(), 1)
    r = w[c].corr(w["AWD"])
    rs = stats.spearmanr(w[c], w["AWD"]).statistic
    print(f"   {c}: POD={pod:.3f}  FAR={far:.3f}  r(SWDI,AWD)={r:.3f}  rho={rs:.3f}  | 'sempre seca' daria POD=1,000 e FAR={1-seca_ref.mean():.3f}")
# so estacao de cultivo fev-mai, como o artigo
m = w.index.month.isin([2, 3, 4, 5])
for c in ["swdi_sf", "swdi_rz"]:
    print(f"   fev-mai {c}: r(SWDI,AWD)={w.loc[m, c].corr(w.loc[m, 'AWD']):.3f}  (artigo: r=0,652 em todo o periodo, SMOS L2)")

# ---------------------------------------------------------------- (c) Zeri 2021: defasagem SMA -> VHI
secao("(c) Zeri 2021 - defasagem SMA (SMAP L4 raizes) -> VHI (MODIS NDVI+LST) e SPI-1 (IMERG)")
mod = pd.read_parquet(DERIV / "modis_ce_mensal.parquet")
ndvi = mod[mod.variavel == "ndvi"].set_index("data")["valor"]
lst = mod[mod.variavel == "lst_dia"].set_index("data")["valor"]
ndvi.index = pd.to_datetime(ndvi.index).to_period("M").to_timestamp()
lst.index = pd.to_datetime(lst.index).to_period("M").to_timestamp()


def por_mes(s, f):
    return s.groupby(s.index.month).transform(f)


vci = (ndvi - por_mes(ndvi, "min")) / (por_mes(ndvi, "max") - por_mes(ndvi, "min"))
tci = (por_mes(lst, "max") - lst) / (por_mes(lst, "max") - por_mes(lst, "min"))
vhi = (50 * vci + 50 * tci).dropna()


def zmes(s):
    return (s - por_mes(s, "mean")) / por_mes(s, "std")


vhia = zmes(vhi)
rz_m = rz_ce.resample("MS").mean()
sma = zmes(rz_m.loc["2015-04-01":"2026-10-01"])
p_m = p_ce.resample("MS").sum().loc["1998-01-01":"2026-08-01"]


def spi1(s):
    out = pd.Series(index=s.index, dtype=float)
    for mm in range(1, 13):
        x = s[s.index.month == mm]
        q0 = (x <= 0.05).mean()
        pos = x[x > 0.05]
        a, loc, sc = stats.gamma.fit(pos, floc=0)
        cdf = q0 + (1 - q0) * stats.gamma.cdf(x.clip(lower=0.05), a, loc=0, scale=sc)
        out[x.index] = stats.norm.ppf(np.clip(cdf, 1e-3, 1 - 1e-3))
    return out


spi = spi1(p_m)
ndvia = zmes(ndvi)
print("   r(indice_t, alvo_t+k) | todos os meses 2015-04..2026-08 | anomalias padronizadas por mes do calendario")
for nome_x, x in [("SMA (SMAP L4 raiz)", sma), ("SPI-1 (IMERG)", spi)]:
    for nome_y, y in [("VHIa", vhia), ("NDVIa", ndvia)]:
        linha = []
        for k in range(0, 4):
            yy = y.shift(-k)
            j = pd.concat([x, yy], axis=1).dropna().loc["2015-04-01":"2026-08-01"]
            linha.append(f"k={k}: {j.iloc[:,0].corr(j.iloc[:,1]):+.2f} (n={len(j)})")
        print(f"   {nome_x:20s} -> {nome_y:5s}  " + "  ".join(linha))
j = pd.concat([sma, spi], axis=1).dropna()
print(f"   r(SMA, SPI-1) mesmo mes = {j.iloc[:,0].corr(j.iloc[:,1]):+.2f}; SMA x SPI-1 do mes anterior = "
      f"{pd.concat([sma, spi.shift(1)], axis=1).dropna().corr().iloc[0,1]:+.2f}")

# ---------------------------------------------------------------- (d) Zeri 2021: chuva nov-jul
secao("(d) Zeri 2021 - chuva nov-jul: razao com a media (CHIRPS semiarido no artigo; IMERG no CE aqui)")
im = pd.read_parquet(DERIV / "imerg_ce_mensal.parquet")
pm = im[im.variavel == "precip_total"].set_index("data")["valor"]
pm.index = pd.to_datetime(pm.index)
safra = {}
for a in range(1999, 2026):
    janela = pm.loc[f"{a-1}-11-01":f"{a}-07-01"]
    if len(janela) == 9:
        safra[a] = janela.sum()
safra = pd.Series(safra)
med = safra.loc[1999:2020].mean()
print(f"   media nov-jul IMERG CE 1998/99-2019/20 = {med:.0f} mm (artigo: 698 mm, CHIRPS, pontos do semiarido 1981-2020)")
for a, art in [(2012, 400), (2013, 553), (2015, 653)]:
    print(f"   {a-1}-{a}: IMERG CE {safra[a]:.0f} mm, razao {safra[a]/med:.2f} | artigo {art} mm, razao {art/698:.2f}")
print(f"   ranking das 5 safras nov-jul mais secas (IMERG CE): {safra.sort_values().head(5).round(0).to_dict()}")

print(f"\nTempo total: {time.time()-T0:.0f} s")
