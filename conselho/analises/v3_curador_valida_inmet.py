"""Curador de bases (v3), teste B/D: INMET x NASA no Nordeste.

Fontes de campo (baixadas por v3_curador_baixar_inmet.py e por curl em 14/11/2026):
 - Normais Climatologicas do Brasil 1991-2020 (INMET), planilhas oficiais portal.inmet.gov.br/uploads/normais/
   Normal-Climatologica-PREC.xlsx e Normal-Climatologica-ESTACOES.xlsx (estacoes convencionais, com coordenadas).
 - Dados horarios das estacoes automaticas do NE, 2016-2025 (portal.inmet.gov.br/dadoshistoricos), hora UTC.

B1. Normal 1991-2020 x climatologia IMERG 1998-2025 (via POWER, 0,1 grau), todas as convencionais do NE com os
    12 meses: razao anual na celula mais proxima e na celula vizinha a oeste (terra), por faixa de distancia do mar.
    Mesma comparacao para o POWER PRECTOTCORR mensal (0,5 grau).
B2. Chuva diaria: estacoes automaticas x IMERG (dia UTC nos dois): r diario, r mensal, razao de volume, litoral x interior.
D.  Temperatura maxima e ET0 FAO-56: estacoes automaticas do CE x POWER diario (celula mais proxima; mesma formula de
    scripts/preparar_power.py aplicada aos dois lados). Estacao: vento a 10 m levado a 2 m (fator 4,87/ln(67,8z-5,42)).
Saida: E:/campeonato-nasa/dados/complementares/inmet/inmet_diario_ne.parquet (cache) e o texto na saida padrao.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import numpy as np
import pandas as pd
import xarray as xr
from preparar_power import et0_fao56

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 230)
B = DADOS / "complementares" / "inmet"

# ---------------- 0) automaticas -> diario UTC
CACHE = B / "inmet_diario_ne_v2.parquet"
if CACHE.exists():
    dd = pd.read_parquet(CACHE)
else:
    partes = []
    for f in sorted((B / "horario_ne").glob("*/*.CSV")):
        cab = {}
        with open(f, encoding="latin1") as fh:
            for _ in range(8):
                k, v = fh.readline().strip().split(";")[:2]
                cab[k.strip(": ")] = v
        x = pd.read_csv(f, sep=";", skiprows=8, encoding="latin1", decimal=",", na_values=["-9999", "-9999,0"],
                        low_memory=False)
        x = x.iloc[:, :19]
        x.columns = ["data", "hora", "chuva", "p", "pmax", "pmin", "rad", "t", "td", "tmax_h", "tmin_h", "tdmax",
                     "tdmin", "urmax", "urmin", "ur", "vdir", "vraj", "vvel"]
        x["data"] = pd.to_datetime(x.data.astype(str).str.replace("/", "-"), errors="coerce")
        for c in x.columns[2:]:
            x[c] = pd.to_numeric(x[c], errors="coerce")
        x.loc[(x.chuva < 0) | (x.chuva > 200), "chuva"] = np.nan
        x.loc[x.rad < 0, "rad"] = 0.0
        g = x.groupby("data")
        d = pd.DataFrame({
            "chuva_mm": g.chuva.sum(min_count=22).where(g.chuva.count() >= 22),
            "tmax": g.tmax_h.max().where(g.tmax_h.count() >= 20),
            "tmin": g.tmin_h.min().where(g.tmin_h.count() >= 20),
            "td": g.td.mean().where(g.td.count() >= 20),
            "u10": g.vvel.mean().where(g.vvel.count() >= 20),
        }).reset_index()
        # radiacao: noite vem vazia; soma das horas de luz (09-21 UTC), exige >= 11 das 13 horas
        hh = pd.to_numeric(x.hora.astype(str).str.replace(":", "").str[:2], errors="coerce")
        xr_ = x[(hh >= 9) & (hh <= 21)].groupby("data").rad
        rs = (xr_.sum(min_count=11) / 1000).where(xr_.count() >= 11)
        d["rs_mj"] = d.data.map(rs)
        d["codigo"] = cab.get("CODIGO (WMO)")
        d["nome"] = cab.get("ESTACAO")
        d["uf"] = cab.get("UF")
        d["lat"] = pd.to_numeric(cab.get("LATITUDE", "").replace(",", "."), errors="coerce")
        d["lon"] = pd.to_numeric(cab.get("LONGITUDE", "").replace(",", "."), errors="coerce")
        d["alt"] = pd.to_numeric(cab.get("ALTITUDE", "").replace(",", "."), errors="coerce")
        partes.append(d)
    dd = pd.concat(partes, ignore_index=True)
    for c in ["lat", "lon", "alt"]:  # alguns cabecalhos anuais vem com campo vazio ou trocado
        dd[c] = dd.groupby("codigo")[c].transform("median")
    dd.loc[(dd.rs_mj <= 0) | (dd.rs_mj > 40), "rs_mj"] = np.nan
    dd.to_parquet(CACHE, index=False)
    registrar_manifesto("complementares/inmet", {
        "normais_1991_2020": "normais_1991_2020/*.xlsx (portal.inmet.gov.br/normais)",
        "diario_ne": "inmet_diario_ne_v2.parquet: dia UTC das automaticas do NE (chuva >= 22 h validas; T, Td, vento, Rs)",
    }, base=B)
dd["data"] = pd.to_datetime(dd.data)
print(f"INMET automaticas NE: {dd.codigo.nunique()} estacoes, {dd.chuva_mm.notna().sum():,} dias com chuva valida,"
      f" {dd.data.min().date()} a {dd.data.max().date()}")

# ---------------- IMERG NE climatologia e series
ne = xr.open_mfdataset(sorted((DADOS / "imerg").glob("imerg_ne_diario_*.nc")), combine="by_coords")["precip"]
ne = ne.sel(time=slice("1998-01-01", "2025-12-31"))
ne = ne.where(ne >= 0)
clim_mes = ne.resample(time="MS").sum().groupby("time.month").mean().load()  # mes x lat x lon (1998-2025)
anual = clim_mes.sum("month")
pw = xr.open_dataset(DADOS / "power" / "power_ne_mensal.nc")["PRECTOTCORR"].sel(time=slice("1998", "2025"))
dias = pd.to_datetime(pw.time.values).days_in_month.values
pw_anual = (pw * xr.DataArray(dias, dims="time", coords={"time": pw.time})).groupby("time.month").mean().sum("month")
# mascara de terra aproximada: celula IMERG com chuva no ponto? usa limite das UFs
import geopandas as gpd
from shapely.geometry import Point
ufs = gpd.read_file(REF / "nordeste_ufs.geojson").to_crs(4326)
terra = ufs.union_all()
costa = terra.boundary


def km_mar(lon, lat):
    return Point(lon, lat).distance(costa) * 111.0


# ---------------- B1. normais
print("\n" + "=" * 20, "B1. Normais INMET 1991-2020 x IMERG 1998-2025 (razao anual)", "=" * 20)
N = pd.read_excel(B / "normais_1991_2020" / "Normal-Climatologica-PREC.xlsx", header=None, skiprows=3)
N = N.iloc[:, :16]
N.columns = ["codigo", "nome", "uf"] + list(range(1, 13)) + ["ano"]
E = pd.read_excel(B / "normais_1991_2020" / "Normal-Climatologica-ESTACOES.xlsx", header=None, skiprows=3).iloc[:, 1:7]
E.columns = ["codigo", "nome_e", "uf_e", "lat", "lon", "alt"]
N = N.merge(E, on="codigo")
N = N[N.uf.isin(["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"])]
for m in range(1, 13):
    N[m] = pd.to_numeric(N[m], errors="coerce")
N["soma12"] = N[list(range(1, 13))].sum(axis=1, min_count=12)
N = N.dropna(subset=["soma12"])
N = N[(N.lon >= -48.8) & (N.lat >= -18.4)]
lin = []
for _, r in N.iterrows():
    c = anual.sel(lat=r.lat, lon=r.lon, method="nearest")
    w = anual.sel(lat=r.lat, lon=float(c.lon) - 0.1, method="nearest")  # vizinha a oeste (para dentro do continente)
    pv = pw_anual.where(pw_anual > 0).stack(k=("lat", "lon")).dropna("k")
    kk = int(np.argmin((pv.lat.values - r.lat) ** 2 + (pv.lon.values - r.lon) ** 2))
    pwc = float(pv.values[kk])  # celula POWER valida mais proxima (a grade mensal tem celulas vazias)
    ok_terra = terra.contains(Point(float(c.lon), float(c.lat)))
    mi = clim_mes.sel(lat=r.lat, lon=r.lon, method="nearest").values
    nm = r[list(range(1, 13))].values.astype(float)
    lin.append({"codigo": r.codigo, "estacao": r.nome, "uf": r.uf, "lat": r.lat, "lon": r.lon,
                "km_mar": km_mar(r.lon, r.lat), "normal": r.soma12, "imerg": float(c), "razao": float(c) / r.soma12,
                "razao_oeste": float(w) / r.soma12, "razao_power": pwc / r.soma12, "celula_em_terra": ok_terra,
                "r_ciclo_mensal": np.corrcoef(mi, nm)[0, 1]})
B1 = pd.DataFrame(lin)
B1["faixa"] = pd.cut(B1.km_mar, [-1, 20, 60, 150, 2000], labels=["<20 km", "20-60 km", "60-150 km", ">150 km"])
print(B1.groupby("faixa")[["razao", "razao_oeste", "razao_power", "r_ciclo_mensal"]].median().round(2).assign(
    n=B1.groupby("faixa").size()).to_string())
cap = B1[B1.estacao.str.contains("RECIFE|MACEIO|ARACAJU|JOAO PESSOA|SALVADOR|NATAL|FORTALEZA|QUIXERAMOBIM|PETROLINA|BARBALHA|SOBRAL|IGUATU|TAUA|SAO LUIS", regex=True)]
print(cap[["estacao", "uf", "km_mar", "normal", "imerg", "razao", "razao_oeste", "razao_power", "celula_em_terra"]].round(2).to_string(index=False))
print("costa leste (RN a BA, < 20 km do mar): razao mediana",
      round(B1[(B1.km_mar < 20) & B1.uf.isin(["RN", "PB", "PE", "AL", "SE", "BA"])].razao.median(), 2),
      "| costa norte (MA, PI, CE, < 20 km):", round(B1[(B1.km_mar < 20) & B1.uf.isin(["MA", "PI", "CE"])].razao.median(), 2))
print("nota: periodos diferentes (normal 1991-2020; IMERG 1998-2025). A normal e a media de 30 anos da estacao.")

# ---------------- B2. chuva diaria automaticas x IMERG
print("\n" + "=" * 20, "B2. Chuva diaria: automaticas INMET x IMERG (dia UTC), 2016-2025", "=" * 20)
st = dd.groupby("codigo")[["nome", "uf", "lat", "lon"]].first()
st = st[(st.lon >= -48.8) & (st.lat >= -18.4)]
iy = np.abs(ne.lat.values[None, :] - st.lat.values[:, None]).argmin(1)
ix = np.abs(ne.lon.values[None, :] - st.lon.values[:, None]).argmin(1)
sub = ne.sel(time=slice("2016-01-01", "2025-12-31"))
I = pd.DataFrame(sub.isel(lat=xr.DataArray(iy, dims="e"), lon=xr.DataArray(ix, dims="e")).load().values,
                 index=pd.to_datetime(sub.time.values), columns=st.index)
G = dd.pivot(index="data", columns="codigo", values="chuva_mm").reindex(I.index)
lin = []
for c in st.index:
    g, s = G[c], I[c]
    m = g.notna() & s.notna()
    if m.sum() < 730:
        continue
    g, s = g[m], s[m]
    gm, sm = g.resample("MS").sum(min_count=25), s.resample("MS").sum(min_count=25)
    lin.append({"codigo": c, "nome": st.nome[c], "uf": st.uf[c], "km_mar": km_mar(st.lon[c], st.lat[c]),
                "n": int(m.sum()), "r_dia": np.corrcoef(g, s)[0, 1],
                "r_dia_lag": np.corrcoef(g.values[1:], s.values[:-1])[0, 1], "r_mes": gm.corr(sm),
                "razao_volume": s.sum() / g.sum(), "freq_g": (g >= 1).mean(), "freq_s": (s >= 1).mean()})
B2 = pd.DataFrame(lin)
B2["faixa"] = pd.cut(B2.km_mar, [-1, 20, 60, 150, 2000], labels=["<20 km", "20-60 km", "60-150 km", ">150 km"])
print(B2.groupby("faixa")[["r_dia", "r_dia_lag", "r_mes", "razao_volume", "freq_g", "freq_s"]].median().round(3).assign(
    n=B2.groupby("faixa").size()).to_string())
print(B2[B2.uf == "CE"].sort_values("km_mar")[["nome", "km_mar", "n", "r_dia", "r_mes", "razao_volume"]].round(2).to_string(index=False))
lit = B2[(B2.km_mar < 20) & B2.uf.isin(["RN", "PB", "PE", "AL", "SE", "BA"])]
print("costa leste < 20 km:", lit[["nome", "uf", "r_dia", "r_mes", "razao_volume"]].round(2).to_string(index=False))

# ---------------- D. Tmax e ET0: POWER x estacao (CE)
print("\n" + "=" * 20, "D. Tmax e ET0 FAO-56: POWER (0,5 x 0,625 grau) x automaticas do CE, 2016-2025", "=" * 20)
pwd = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc").sel(time=slice("2016-01-01", "2025-12-31"))
pet = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"].sel(time=slice("2016-01-01", "2025-12-31"))
ce = dd[dd.uf == "CE"].copy()
ce["u2"] = ce.u10 * 4.87 / np.log(67.8 * 10 - 5.42)
ce["et0"] = et0_fao56(ce.tmax, ce.tmin, ce.td, ce.u2, ce.rs_mj, ce.lat, ce.alt, ce.data.dt.dayofyear)
lin = []
for c, g in ce.groupby("codigo"):
    g = g.set_index("data")
    la, lo = g.lat.iloc[0], g.lon.iloc[0]
    P = pwd.sel(lat=la, lon=lo, method="nearest")
    tx = pd.Series(P.T2M_MAX.values, index=pd.to_datetime(P.time.values))
    e0 = pd.Series(pet.sel(lat=la, lon=lo, method="nearest").values, index=pd.to_datetime(pet.time.values))
    rs = pd.Series(P.ALLSKY_SFC_SW_DWN.values, index=pd.to_datetime(P.time.values))
    u2p = pd.Series(P.WS2M.values, index=pd.to_datetime(P.time.values))
    tdp = pd.Series(P.T2MDEW.values, index=pd.to_datetime(P.time.values))
    m1 = g.tmax.notna() & tx.reindex(g.index).notna()
    m2 = g.et0.notna() & e0.reindex(g.index).notna()
    if m1.sum() < 365:
        continue
    lin.append({"estacao": g.nome.dropna().iloc[0], "alt_est": g.alt.iloc[0], "alt_power": float(P.elevacao_m) if "elevacao_m" in P else np.nan,
                "km_mar": km_mar(lo, la), "dias_T": int(m1.sum()),
                "vies_tmax": (tx.reindex(g.index)[m1] - g.tmax[m1]).mean(),
                "vies_tmax_corr_alt": (tx.reindex(g.index)[m1] - g.tmax[m1]).mean()
                - 0.0065 * (g.alt.iloc[0] - float(P.elevacao_m)),
                "r_tmax": np.corrcoef(tx.reindex(g.index)[m1], g.tmax[m1])[0, 1],
                "dias_ET0": int(m2.sum()),
                "et0_est_mm_ano": g.et0[m2].mean() * 365, "et0_power_mm_ano": e0.reindex(g.index)[m2].mean() * 365,
                "razao_et0": e0.reindex(g.index)[m2].mean() / g.et0[m2].mean() if m2.sum() else np.nan,
                "vies_rs": (rs.reindex(g.index)[m2] - g.rs_mj[m2]).mean() if m2.sum() else np.nan,
                "vies_u2": (u2p.reindex(g.index)[m2] - g.u2[m2]).mean() if m2.sum() else np.nan,
                "vies_td": (tdp.reindex(g.index)[m2] - g.td[m2]).mean() if m2.sum() else np.nan})
DD = pd.DataFrame(lin)
print(DD.round(2).to_string(index=False))
print("medianas:", DD[["vies_tmax", "vies_tmax_corr_alt", "r_tmax", "razao_et0", "vies_rs", "vies_u2", "vies_td"]].median().round(3).to_dict())
print("nota: a celula POWER (~55 x 70 km) mistura serra, sertao e litoral; a ET0 da estacao usa Rs medida e vento",
      "de 10 m reduzido a 2 m. A estacao automatica ja e a referencia de campo do INMET; nao foi feito controle de",
      "qualidade alem de faixas fisicas.")

# ET0 normal INMET (planilha "Evapotranspiracao Potencial", metodo nao informado na planilha) x ET0 POWER 1991-2020
print()
print("=" * 20, "D2. ET potencial normal INMET 1991-2020 (convencionais do CE) x ET0 POWER FAO-56 1991-2020", "=" * 20)
EV = pd.read_excel(B / "normais_1991_2020" / "Normal-Climatologica-EVAPOTM.xlsx", header=None, skiprows=3).iloc[:, :16]
EV.columns = ["codigo", "nome", "uf"] + list(range(1, 13)) + ["ano"]
EV = EV[EV.uf == "CE"].merge(E, on="codigo")
e91 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"].sel(time=slice("1991-01-01", "2020-12-31"))
e91 = e91.groupby("time.year").sum().mean("year")
for _, r in EV.iterrows():
    v = pd.to_numeric(pd.Series([r[m] for m in range(1, 13)]), errors="coerce")
    tot = v.sum() if v.notna().all() else np.nan
    pw_ = float(e91.sel(lat=r.lat, lon=r.lon, method="nearest"))
    print(f"  {r.nome:14s} normal INMET {tot:7.1f} mm/ano | POWER FAO-56 {pw_:7.1f} | razao POWER/INMET {pw_ / tot if tot == tot else float('nan'):.2f}")
