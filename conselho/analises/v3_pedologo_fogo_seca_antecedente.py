"""v3 pedologo/ecologo do fogo -- teste 1: "o deficit de chuva antecede o fogo" (Bezerra et al. 2025/2026)
e "ano umido seguido de ano seco = grande queimada" (Argibay et al. 2020), refeitos no Ceara so com dado NASA.

A. Replica de Bezerra et al. (Atmosphere 2026, 17, 46; Fig. 10): correlacao cruzada mensal entre anomalia de FRP
   (FIRMS VIIRS S-NPP, type 0, confianca n/h, UF 23) e SPI-1/SPI-6 (IMERG V07 via POWER, media do CE) e VPD
   (POWER T2M e T2MDEW, Tetens como no artigo), defasagens -6..+6 meses, 2012-2025.
   Convencao: lag k > 0 = clima k meses ANTES do fogo.
   SPI nao parametrico (posicao de Gringorten por mes-calendario, base 1998-2025 -> quantil normal).
   IC95 por bootstrap em blocos de 12 meses (2000 reps).
B. Replica de Argibay et al. (Ecol. Indic. 113:106151): area queimada anual (MCD64A1, km2, UF 23, 2001-2025) contra
   chuva jan-jun do ano (P_t) e do ano anterior (P_t-1), IMERG.
   B1 estado (n = 25 anos); B2 painel de celulas 0,1 grau do CE (MCD64A1 0,05 grau agregado; IMERG 0,1 grau),
   efeito fixo de celula + tendencia, EP agrupado por ano; habilidade fora do ano (deixa 1 ano fora) contra a
   base "celula + tendencia".
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *
import numpy as np, pandas as pd, xarray as xr, shapely
from scipy import stats
import statsmodels.api as sm

rng = np.random.default_rng(42)
print("=" * 100)
print("A. Bezerra et al.: correlacao cruzada FRP x SPI / VPD, Ceara, mensal 2012-2025")
print("=" * 100)

# ---- FIRMS VIIRS CE
v = pd.read_parquet(DADOS / "viirs" / "firms_viirs_snpp_nordeste.parquet",
                    columns=["acq_date", "frp", "type", "uf", "confidence"])
n0 = (v.uf == 23).sum()
v = v[(v.uf == 23) & (v["type"] == 0) & (v.confidence.astype(str).str.lower().isin(["n", "h"]))]
print(f"FIRMS VIIRS UF 23: {n0} deteccoes, {len(v)} apos type 0 e confianca n/h")
v["mes"] = pd.to_datetime(v.acq_date).dt.to_period("M").dt.to_timestamp()
fm = v.groupby("mes").agg(frp=("frp", "sum"), n=("frp", "size"))
idx = pd.date_range("2012-01-01", "2025-12-01", freq="MS")
fm = fm.reindex(idx, fill_value=0)

# ---- IMERG CE mensal (derivado; media do estado)
im = pd.read_parquet(DERIV / "imerg_ce_mensal.parquet")
p = im[im.variavel == "precip_total"].set_index("data").valor.sort_index()
p = p[(p.index >= "1998-01-01") & (p.index <= "2025-12-01")]


def spi_np(serie, k):
    """SPI nao parametrico: soma movel de k meses, rank de Gringorten por mes-calendario."""
    s = serie.rolling(k).sum()
    out = pd.Series(np.nan, index=s.index)
    for m in range(1, 13):
        sel = s[(s.index.month == m) & s.notna()]
        r = stats.rankdata(sel.values)
        out.loc[sel.index] = stats.norm.ppf((r - 0.44) / (len(sel) + 0.12))
    return out


spi1, spi6 = spi_np(p, 1), spi_np(p, 6)

# ---- VPD POWER (Tetens, igual a Eq. 6-8 do artigo)
pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw = pw.pivot_table(index="data", columns="variavel", values="valor")
es = 6.112 * np.exp(17.67 * pw.T2M / (pw.T2M + 243.5))
ea = 6.112 * np.exp(17.67 * pw.T2MDEW / (pw.T2MDEW + 243.5))
vpd = (es - ea).rename("vpd")

D = pd.DataFrame({"frp": fm.frp, "n": fm.n}).join(spi1.rename("spi1")).join(spi6.rename("spi6")).join(vpd)
D["lfrp"] = np.log1p(D.frp)
D["m"] = D.index.month
D["lfrp_a"] = D.lfrp - D.groupby("m").lfrp.transform("mean")
D["vpd_a"] = D.vpd - D.groupby("m").vpd.transform("mean")
D["p_mm"] = p.reindex(D.index)
print(f"meses: {len(D)} | soma FRP 2012-2025 = {D.frp.sum():,.0f} MW | focos = {int(D.n.sum())}")

clima = {"spi1": spi1, "spi6": spi6, "vpd_bruto": vpd, "vpd_anom": None, "chuva_mm_bruta": p}


def xcorr(y, x, lags=range(-6, 7)):
    out = {}
    for k in lags:
        xs = x.shift(k)  # k>0: clima k meses antes
        ok = y.notna() & xs.notna()
        out[k] = np.corrcoef(y[ok], xs[ok])[0, 1]
    return pd.Series(out)


def boot_ci(y, x, k, reps=2000, bloco=12):
    xs = x.shift(k)
    ok = (y.notna() & xs.notna()).values
    yy, xx = y.values[ok], xs.values[ok]
    n = len(yy); nb = int(np.ceil(n / bloco))
    rs = []
    for _ in range(reps):
        st = rng.integers(0, n - bloco + 1, nb)
        ii = np.concatenate([np.arange(s, s + bloco) for s in st])[:n]
        rs.append(np.corrcoef(yy[ii], xx[ii])[0, 1])
    return np.percentile(rs, [2.5, 97.5])


for alvo, rot in [("lfrp", "log1p(FRP) BRUTO (com ciclo sazonal)"), ("lfrp_a", "ANOMALIA de log1p(FRP) (sem ciclo)")]:
    print(f"\nAlvo: {rot}")
    for nome, x in [("SPI-1", D.spi1), ("SPI-6", D.spi6), ("VPD bruto", D.vpd), ("VPD anomalia", D.vpd_a),
                    ("chuva mm bruta", D.p_mm)]:
        if alvo == "lfrp_a" and nome in ("VPD bruto", "chuva mm bruta"):
            continue
        r = xcorr(D[alvo], x)
        kmin, kmax = r.idxmin(), r.idxmax()
        lo, hi = boot_ci(D[alvo], x, 0)
        lo4, hi4 = boot_ci(D[alvo], x, 4)
        print(f"  {nome:15s} r(lag0) {r[0]:+.2f} [IC95 {lo:+.2f} a {hi:+.2f}] | r(lag+4) {r[4]:+.2f} [IC95 {lo4:+.2f} a {hi4:+.2f}]"
              f" | minimo {r.min():+.2f} em lag {kmin:+d} | maximo {r.max():+.2f} em lag {kmax:+d}")
        print("     lags -6..+6: " + " ".join(f"{r[k]:+.2f}" for k in range(-6, 7)))

# versao anual (n = 12 anos, 2012-2023, como o periodo do artigo) -- o r = -0,69 com p ~ 0,012 do artigo implica n = 12
A = D[(D.index.year <= 2023)].groupby(D.index.year[(D.index.year <= 2023)]).agg(frp=("frp", "sum"), spi6=("spi6", "mean"),
                                                                                  spi1=("spi1", "mean"), vpd=("vpd", "mean"))
for c in ["spi1", "spi6", "vpd"]:
    r, pv = stats.pearsonr(np.log(A.frp), A[c])
    print(f"\nAnual 2012-2023 (n=12): r(log FRP anual, media anual de {c}) = {r:+.2f} (p = {pv:.3f})")
print("Ranking dos anos por FRP anual no CE (2012-2025):",
      ", ".join(f"{a}" for a in D.groupby(D.index.year).frp.sum().sort_values(ascending=False).index[:6]))
print("  Bezerra et al. (bioma Caatinga): maiores intensidades em 2015, 2019, 2021 e 2023")

# atribuicao sazonal: em que mes cai o pico do FRP e o pico do deficit no CE?
cl = D.groupby("m").agg(frp=("frp", "mean"), p=("p_mm", "mean"), vpd=("vpd", "mean"))
print("\nClimatologia CE 2012-2025 (media mensal): FRP pico no mes", cl.frp.idxmax(), "| chuva minima no mes", cl.p.idxmin(),
      "| VPD pico no mes", cl.vpd.idxmax(), "| ultimo mes com chuva media > 100 mm:", cl.index[cl.p > 100].max())

print()
print("=" * 100)
print("B. Argibay et al.: ano umido seguido de ano seco -> grande area queimada? (MCD64A1 x IMERG, Ceara)")
print("=" * 100)
uf = pd.read_parquet(DADOS / "modis" / "mcd64a1_area_queimada_mensal_uf.parquet")
uf["ano"] = pd.to_datetime(uf.data).dt.year
ba = uf[(uf.uf == 23) & uf.ano.between(2001, 2025)].groupby("ano").area_queimada_km2.sum()
pq = p[p.index.month <= 6].groupby(p.index.year[p.index.month <= 6]).sum()  # jan-jun, 1998-2025
B = pd.DataFrame({"ba": ba, "P": pq.reindex(ba.index), "P1": pq.shift(1).reindex(ba.index)})
B["lba"] = np.log(B.ba)
B["t"] = B.index - 2013
print(B.round(1).to_string())
X = B[["P", "P1", "t"]].copy(); X["P"] = (X.P - X.P.mean()) / X.P.std(); X["P1"] = (X.P1 - X.P1.mean()) / X.P1.std()
m = sm.OLS(B.lba, sm.add_constant(X)).fit(cov_type="HC3")
print("\nB1 estado: log(area queimada) ~ z(P_t jan-jun) + z(P_t-1 jan-jun) + tendencia (n = 25, EP HC3)")
for c in ["P", "P1", "t"]:
    lo, hi = m.conf_int().loc[c]
    print(f"  {c:3s} {m.params[c]:+.3f} (IC95 {lo:+.3f} a {hi:+.3f}; p = {m.pvalues[c]:.3f})")
print(f"  R2 = {m.rsquared:.2f}")
res = B.lba - sm.OLS(B.lba, sm.add_constant(B.t)).fit().fittedvalues
med_P, med_P1 = B.P.median(), B.P1.median()
B["umido_seco"] = (B.P1 > med_P1) & (B.P < med_P)
obs = res[B.umido_seco].mean() - res[~B.umido_seco].mean()
perm = []
for _ in range(20000):
    lab = rng.permutation(B.umido_seco.values)
    perm.append(res[lab].mean() - res[~lab].mean())
pperm = (np.sum(np.array(perm) >= obs) + 1) / (len(perm) + 1)
print(f"  Anos 'umido (t-1) e seco (t)' (acima/abaixo da mediana jan-jun): {list(B.index[B.umido_seco])}")
print(f"  anomalia media de log(area) sobre a tendencia: {res[B.umido_seco].mean():+.3f} vs outros {res[~B.umido_seco].mean():+.3f}"
      f" (dif {obs:+.3f}; p permutacao unilateral = {pperm:.3f})")
print("  Anos com maior area queimada no CE:", list(B.ba.sort_values(ascending=False).index[:5]))

# ---- B2 painel 0,1 grau
print("\nB2 painel de celulas 0,1 grau no Ceara (2001-2025)")
fq = xr.open_dataset(DADOS / "modis" / "mcd64a1_frac_queimada_nordeste_005deg.nc").frac_queimada
fq = fq.sel(lat=slice(-2.5, -8.0), lon=slice(-41.5, -37.0), time=slice("2001-01-01", "2025-12-01"))
anual = fq.groupby("time.year").sum("time")  # fracao-ano queimada (soma de meses)
anual = anual.coarsen(lat=2, lon=2, boundary="trim").mean()
im_cells = []
for a in range(2000, 2026):
    ds = xr.open_dataset(DADOS / "imerg" / f"imerg_ce_diario_{a}.nc")
    im_cells.append(ds.precip.sel(time=slice(f"{a}-01-01", f"{a}-06-30")).sum("time").expand_dims(year=[a]))
P = xr.concat(im_cells, "year")
P = P.sel(lat=anual.lat, lon=anual.lon, method="nearest")
P = P.assign_coords(lat=anual.lat, lon=anual.lon)
ce = ceara_gdf().geometry.union_all()
LON, LAT = np.meshgrid(anual.lon.values, anual.lat.values)
dentro = shapely.contains_xy(ce, LON, LAT)
print(f"  celulas dentro do CE: {dentro.sum()} | centros de grade MCD64 {float(anual.lat[0]):.3f}.. ; IMERG casado por vizinho")
rows = []
for a in range(2001, 2026):
    y = anual.sel(year=a).values[dentro]
    pt = P.sel(year=a).values[dentro]; p1 = P.sel(year=a - 1).values[dentro]
    rows.append(pd.DataFrame({"cel": np.arange(dentro.sum()), "ano": a, "ba": y, "P": pt, "P1": p1}))
T = pd.concat(rows, ignore_index=True)
T["y"] = np.log(T.ba + 1e-3)
for c in ["P", "P1"]:
    T[c + "z"] = (T[c] - T.groupby("cel")[c].transform("mean")) / T.groupby("cel")[c].transform("std")
T["Iz"] = T.Pz * (-T.P1z)  # interacao: seco agora x umido antes (positiva quando P1 alto e P baixo)
T["t"] = T.ano - 2013
print(f"  linhas {len(T)}; fracao media queimada por celula-ano {T.ba.mean():.4f}; zeros {np.mean(T.ba == 0):.2%}")


def demean(df, cols):
    return df[cols] - df.groupby("cel")[cols].transform("mean")


for spec in [["P1z", "t"], ["Pz", "t"], ["Pz", "P1z", "t"], ["Pz", "P1z", "Iz", "t"]]:
    Yd = demean(T, ["y"]).y; Xd = demean(T, spec)
    mm = sm.OLS(Yd, Xd).fit(cov_type="cluster", cov_kwds={"groups": T.ano})
    txt = " | ".join(f"{c} {mm.params[c]:+.3f} (IC95 {mm.conf_int().loc[c,0]:+.3f} a {mm.conf_int().loc[c,1]:+.3f})" for c in spec)
    # habilidade fora do ano contra base celula + tendencia
    se_b = se_m = 0.0; melhora = 0
    for a in range(2001, 2026):
        tr, te = T[T.ano != a], T[T.ano == a]
        mu = tr.groupby("cel").y.mean(); xb = tr.groupby("cel")[spec].mean()
        Ytr = tr.y - tr.cel.map(mu); Xtr = tr[spec] - xb.loc[tr.cel].values
        bt = sm.OLS(Ytr, Xtr[["t"]]).fit().params
        bm = sm.OLS(Ytr, Xtr).fit().params
        Xte = te[spec] - xb.loc[te.cel].values
        base = te.cel.map(mu) + Xte[["t"]] @ bt
        mod = te.cel.map(mu) + Xte @ bm
        eb, em = np.mean((te.y - base) ** 2), np.mean((te.y - mod) ** 2)
        se_b += eb; se_m += em; melhora += em < eb
    print(f"  {'+'.join(spec):14s} {txt} | habilidade fora do ano vs celula+tendencia {1 - se_m / se_b:+.3f} (melhora em {melhora}/25 anos)")

# anomalia do ano no estado ja com EF: medias por ano dos residuos da base
Yd = demean(T, ["y"]).y; Xd = demean(T, ["t"])
T["r"] = Yd - sm.OLS(Yd, Xd).fit().fittedvalues
ya = T.groupby("ano").agg(r=("r", "mean"), Pz=("Pz", "mean"), P1z=("P1z", "mean"))
rho1 = stats.spearmanr(ya.r, ya.P1z); rho0 = stats.spearmanr(ya.r, ya.Pz)
print(f"  entre anos (n=25): rho(anomalia de fogo, P_t-1) = {rho1.statistic:+.2f} (p={rho1.pvalue:.2f}); rho(anomalia, P_t) = {rho0.statistic:+.2f} (p={rho0.pvalue:.2f})")

# ---- B3 controle de detectabilidade: o MCD64A1 depende do contraste verde->cicatriz; o foco ativo nao.
print("\nB3 mesmo teste com focos ativos FIRMS MODIS (Terra+Aqua, type 0, confianca >= 30), CE, jul-dez, 2001-2025")
fmod = pd.read_parquet(DADOS / "modis" / "firms_modis_nordeste.parquet", columns=["acq_date", "type", "uf", "confidence"])
fmod = fmod[(fmod.uf == 23) & (fmod["type"] == 0) & (fmod.confidence >= 30)]
dd = pd.to_datetime(fmod.acq_date)
fmod = fmod[dd.dt.month >= 7]
cnt = fmod.groupby(pd.to_datetime(fmod.acq_date).dt.year).size().reindex(range(2001, 2026))
B["lfoc"] = np.log(cnt)
for alvo, rot in [("lba", "log area MCD64A1 (ano todo)"), ("lfoc", "log focos MODIS jul-dez")]:
    r_ = B[alvo] - sm.OLS(B[alvo], sm.add_constant(B.t)).fit().fittedvalues
    s0 = stats.spearmanr(r_, B.P); s1 = stats.spearmanr(r_, B.P1)
    print(f"  {rot:28s}: rho(resid. da tendencia, P_t) = {s0.statistic:+.2f} (p={s0.pvalue:.2f}) | rho(resid., P_t-1) = {s1.statistic:+.2f} (p={s1.pvalue:.2f})")
print(f"  rho(log area MCD64A1, log focos MODIS jul-dez) = {stats.spearmanr(B.lba, B.lfoc).statistic:+.2f}")
