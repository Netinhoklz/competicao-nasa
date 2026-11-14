# %% [markdown]
# ## 5. Dados Earthdata baixados: SMAP, GLDAS, NLDAS, VIIRS NDVI e IMERG 2026
#
# Com o login Earthdata ativo, os recortes vieram por duas rotas que **cortam no servidor**:
# - **AppEEARS**, com o polígono do Ceará: SMAP L3 (umidade 0–5 cm, 9 km), SMAP L4 (umidade da superfície e da
#   **zona da raiz** + **percentil**, 9 km, 3 h), VIIRS VNP13A3 (NDVI/EVI mensal, 1 km) e VNP13A1 (500 m, 16 dias)
#   nas AOIs. Há também 40 pontos globais em 2020 para validar a cobertura.
# - **OPeNDAP do GES DISC na nuvem**, com a caixa do Nordeste: GLDAS-2.1 Noah mensal, GLDAS-2.2 CLSM diário (com
#   **água subterrânea**, que assimila o GRACE), IMERG V07 Late/Early de 2026 e o NLDAS-2 numa caixa das planícies
#   dos EUA.
#
# | Base | Variáveis | Resolução | Período baixado | Cobertura (seção 4) |
# |---|---|---|---|---|
# | SMAP L3 (SPL3SMP_E) | umidade 0–5 cm AM/PM + qualidade | 9 km, ~2–3 dias | 2015 → nov/2026 | global (85°S–90°N) |
# | SMAP L4 (SPL4SMGP) | superfície, zona da raiz, percentil | 9 km, 3 h | 2015 → nov/2026 | global |
# | GLDAS-2.1 Noah | umidade 4 camadas, ET, escoamento | 0,25°, mensal | 2000 → 2026 | 60°S–90°N |
# | GLDAS-2.2 CLSM | água subterrânea, TWS, umidade raiz | 0,25°, diário | 2003 → 2026 | 60°S–90°N |
# | NLDAS-2 Noah | umidade, ET, escoamento | 0,125°, mensal | 1979 → 2026 | **só EUA** |
# | VIIRS VNP13A3/A1 | NDVI, EVI, confiabilidade | 1 km mensal / 500 m 16 d | 2012 → 2026 | global |
# | IMERG V07 Late/Early | chuva | 0,1°, diário | ago → nov/2026 | global |

# %%
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymannkendall as mk
import shapely
import xarray as xr
from IPython.display import display
from comum import AOIS, DADOS, DERIV, ceara_gdf, nordeste_gdf

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})
CE, NE = ceara_gdf(), nordeste_gdf()
APP = DADOS / "appeears"


def mascara(ds, gdf, lat="lat", lon="lon"):
    lo, la = np.meshgrid(ds[lon].values, ds[lat].values)
    return xr.DataArray(shapely.contains_xy(gdf.union_all(), lo, la), coords={lat: ds[lat], lon: ds[lon]}, dims=(lat, lon))


def abrir_appeears(tarefa_prefixo, produto):
    arqs = sorted(p for d in APP.glob(tarefa_prefixo + "*") if d.is_dir() for p in d.glob(f"{produto}*.nc"))
    if not arqs:
        return None
    dss = [xr.open_dataset(a) for a in arqs]
    return xr.concat(dss, dim="time").sortby("time") if len(dss) > 1 else dss[0]


def var(ds, *trechos):
    for v in ds.data_vars:
        if all(t.lower() in v.lower() for t in trechos):
            return v
    return None


def serie_regional(da, gdf):
    m = mascara(da.to_dataset(name="x"), gdf)
    s = da.where(m).mean(("lat", "lon")).to_series()
    s.index = pd.to_datetime(s.index)
    return s[~s.index.duplicated(keep="last")]  # o L3 tem dias com dois granulos (reprocessamento)


def tendencia(s, rotulo):
    s = s.dropna()
    if len(s) < 24:
        return None
    # teste sazonal: a inclinação de Sen já sai por ciclo (ano); teste comum em série mensal: por mês (× 12)
    sazonal = len(s) >= 36
    r = mk.seasonal_test(s.values, period=12) if sazonal else mk.original_test(s.values)
    return {"série": rotulo, "n": len(s), "início": f"{s.index.min():%Y-%m}", "fim": f"{s.index.max():%Y-%m}",
            "tendência": r.trend, "p": round(r.p, 4), "Sen por ano": round(r.slope * (1 if sazonal else 12), 5)}


# %% [markdown]
# ### 5.1 SMAP — umidade do solo
# - **Validação global:** 40 pontos de terra em 6 continentes, em 2020. Contamos a fração de dias com valor válido em
#   cada ponto. O L3 tem buracos por órbita e qualidade; o L4 é um produto modelado contínuo.

# %%
amostra = DADOS / "smap" / "smap_global_amostra_2025-04-15.nc"
pts = sorted((APP / "smap_global_pontos_2020").glob("*results.csv")) if (APP / "smap_global_pontos_2020").exists() else []
if amostra.exists():
    from comum import paises_gdf, terra_gdf
    ga = xr.open_dataset(amostra)
    terra = terra_gdf().union_all()
    eh_terra = shapely.contains_xy(terra, ga.lon.values, ga.lat.values)
    faixa = np.abs(ga.lat.values) <= 60
    linhas = []
    for v, rot in [("l4_sm_rootzone", "L4 zona da raiz"), ("l3_am", "L3 AM (1 passagem)"), ("l3_pm", "L3 PM (1 passagem)")]:
        ok = np.isfinite(ga[v].values)
        linhas.append({"produto": rot, "% das células de terra com valor": round(100 * ok[eh_terra].mean(), 1),
                       "% terra entre 60°S e 60°N": round(100 * ok[eh_terra & faixa].mean(), 1),
                       "% no oceano (deve ser ~0)": round(100 * ok[~eh_terra].mean(), 2)})
    print(f"Amostra global de {ga.attrs.get('dia')} (1 a cada 8 células da grade de 9 km)")
    display(pd.DataFrame(linhas))
    fig, axs = plt.subplots(1, 2, figsize=(15, 3.8))
    for ax, v, rot in [(axs[0], "l4_sm_rootzone", "SMAP L4 zona da raiz"), (axs[1], "l3_am", "SMAP L3 AM — uma passagem")]:
        paises_gdf().boundary.plot(ax=ax, color="lightgray", lw=0.3)
        m = np.isfinite(ga[v].values)
        sc = ax.scatter(ga.lon.values[m], ga.lat.values[m], c=ga[v].values[m], s=0.3, cmap="YlGnBu", vmin=0, vmax=0.5)
        ax.set_title(f"{rot} ({ga.attrs.get('dia')})")
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
    plt.colorbar(sc, ax=axs, label="m³/m³", shrink=0.8)
    plt.show()
    print("Leitura: o L4 (modelo + assimilação) cobre toda a terra sem gelo; o L3 cobre faixas de órbita por passagem e"
          " fecha o globo em ~2–3 dias. Nenhum dos dois põe valor no oceano.")
elif pts:
    P = pd.read_csv(pts[0])
    col_l3 = next((c for c in P.columns if "AM_soil_moisture" in c and "qual" not in c.lower()), None)
    col_l4 = next((c for c in P.columns if "sm_rootzone" in c and "pctl" not in c), None)
    val = {}
    for nome, c in [("L3 (0–5 cm, AM)", col_l3), ("L4 (zona da raiz)", col_l4)]:
        if c:
            x = P[[ "ID", "Latitude", "Longitude", c]].copy()
            x["ok"] = (x[c] > 0) & (x[c] < 1)
            val[nome] = x.groupby(["ID", "Latitude", "Longitude"]).ok.mean()
    V = pd.DataFrame(val).reset_index()
    fig, axs = plt.subplots(1, len(val), figsize=(7 * len(val), 3.6), squeeze=False)
    from comum import paises_gdf
    for ax, nome in zip(axs[0], val):
        paises_gdf().boundary.plot(ax=ax, color="lightgray", lw=0.4)
        sc = ax.scatter(V.Longitude, V.Latitude, c=V[nome], cmap="RdYlGn", vmin=0, vmax=1, s=45, ec="k")
        ax.set_title(f"SMAP {nome}: fração de dias válidos em 2020")
        plt.colorbar(sc, ax=ax)
    plt.tight_layout()
    plt.show()
    display(V.describe().loc[["mean", "min", "max"]].round(2))
else:
    print("Pontos globais do SMAP ainda não baixados (AppEEARS em processamento).")

# %% [markdown]
# - **Ceará: SMAP L4.** Umidade da superfície (0–5 cm) e da zona da raiz (0–100 cm), em m³/m³, e o **percentil da
#   zona da raiz**, que é um índice de seca pronto: abaixo de 20 = seco para a época.

# %%
l4_f = DADOS / "smap" / "smap_l4_diario_ne.nc"
l4 = xr.open_dataset(l4_f) if l4_f.exists() else abrir_appeears("smap_l4_ceara", "SPL4SMGP")
if l4 is not None:
    # recorte do Ceará (+0,5°) carregado na memória: o resample diário lendo do disco o NE inteiro (2 GB) leva horas
    x0, y0, x1, y1 = CE.total_bounds
    l4 = l4.sortby("lat").sel(lat=slice(y0 - 0.5, y1 + 0.5), lon=slice(x0 - 0.5, x1 + 0.5)).load()
    vz, vs, vp = var(l4, "sm_rootzone"), var(l4, "sm_surface"), var(l4, "rootzone_pctl")
    if vp and vz == vp:
        vz = next(v for v in l4.data_vars if "sm_rootzone" in v and "pctl" not in v)
    print("variáveis:", vz, vs, vp, "| tempos:", l4.sizes["time"], str(l4.time.values.min())[:10], "→", str(l4.time.values.max())[:10])
    diario = l4[[v for v in (vz, vs, vp) if v]].resample(time="1D").mean()
    s_rz, s_sf = serie_regional(diario[vz], CE), serie_regional(diario[vs], CE)
    s_pc = serie_regional(diario[vp], CE) if vp else None
    q = pd.DataFrame({"superfície": s_sf, "zona da raiz": s_rz})
    display(q.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T.round(3).assign(assimetria=q.skew().round(2), curtose=q.kurt().round(2)))
    fig, ax = plt.subplots(2, 2, figsize=(14, 7.5))
    q.plot(ax=ax[0, 0], lw=0.6)
    ax[0, 0].set_title("SMAP L4 — umidade média no Ceará (m³/m³, diário)")
    q.groupby(q.index.month).mean().plot(ax=ax[0, 1], marker="o")
    ax[0, 1].set_title("Climatologia mensal")
    ax[0, 1].set_xlabel("mês")
    if s_pc is not None:
        s_pc.resample("MS").mean().plot(ax=ax[1, 0], color="tab:brown")
        ax[1, 0].axhline(20, color="r", ls="--", lw=1)
        ax[1, 0].set_title("Percentil da zona da raiz (média CE) — abaixo de 20 = seca agrícola")
    media = diario[vz].mean("time")
    media.plot(ax=ax[1, 1], cmap="YlGnBu")
    CE.boundary.plot(ax=ax[1, 1], color="k", lw=0.8)
    ax[1, 1].set_title("Umidade média da zona da raiz 2015–2026")
    plt.tight_layout()
    plt.show()
    linhas = [tendencia(q["zona da raiz"].resample("MS").mean(), "SMAP L4 zona da raiz (mensal)"),
              tendencia(q["superfície"].resample("MS").mean(), "SMAP L4 superfície (mensal)")]
    display(pd.DataFrame([l for l in linhas if l]))
    if s_pc is not None:
        ult = diario[vp].isel(time=slice(-30, None)).mean("time")
        fig, ax = plt.subplots(figsize=(6, 5))
        ult.plot(ax=ax, cmap="RdYlBu", vmin=0, vmax=100)
        CE.boundary.plot(ax=ax, color="k", lw=0.8)
        ax.set_title(f"Percentil da zona da raiz — últimos 30 dias até {str(l4.time.values.max())[:10]}")
        plt.show()
    pd.DataFrame({"data": s_rz.resample("MS").mean().index, "variavel": "sm_rootzone", "valor": s_rz.resample("MS").mean().values,
                  "unidade": "m3/m3", "fonte": "SMAP L4 SPL4SMGP.008"}).pipe(
        lambda d: pd.concat([d, pd.DataFrame({"data": s_sf.resample("MS").mean().index, "variavel": "sm_surface",
                                              "valor": s_sf.resample("MS").mean().values, "unidade": "m3/m3", "fonte": "SMAP L4 SPL4SMGP.008"})])
    ).to_parquet(DERIV / "smap_ce_mensal.parquet", index=False)
else:
    print("SMAP L4 ainda não baixado.")

# %% [markdown]
# - **SMAP L3 (observação do radiômetro, 0–5 cm).** Qualidade: fração de pixels com flag "recomendada" (bit 0 = 0).
#   Concordância com o L4, que é modelo + assimilação do L3.

# %%
l3_f = DADOS / "smap" / "smap_l3_diario_ne.nc"
l3 = xr.open_dataset(l3_f) if l3_f.exists() else abrir_appeears("smap_l3_ceara", "SPL3SMP_E")
if l3 is not None:
    x0, y0, x1, y1 = CE.total_bounds  # recorte do Ceará (+0,5°) na memória, como no L4
    l3 = l3.sortby("lat").sel(lat=slice(y0 - 0.5, y1 + 0.5), lon=slice(x0 - 0.5, x1 + 0.5)).load()
    if "sm_am" in l3:
        vam, vqa = "sm_am", "qual_am"
    else:
        vam, vqa = var(l3, "AM_soil_moisture"), var(l3, "AM_retrieval_qual_flag")
        if vam and "qual" in vam.lower():
            vam = next(v for v in l3.data_vars if v.endswith("AM_soil_moisture"))
    sm = l3[vam].where((l3[vam] > 0) & (l3[vam] < 1))
    m = mascara(l3, CE)
    valido = sm.where(m).notnull().sum(("lat", "lon")) / m.sum()
    print(f"SMAP L3: {l3.sizes['time']} dias; fração média de pixels válidos no Ceará por passagem AM: {float(valido.mean()):.1%}")
    if vqa:
        qa = l3[vqa].where(m)
        recomend = ((qa.astype("int64") & 1) == 0).where(qa.notnull()).mean()
        print(f"   pixels com qualidade recomendada (bit 0 = 0): {float(recomend):.1%}")
    s3 = serie_regional(sm, CE)
    if l4 is not None:
        j = pd.concat([s3.rename("L3"), s_sf.rename("L4 superfície")], axis=1).dropna()
        print(f"   L3 × L4 superfície (média CE diária): r = {j.corr().iloc[0, 1]:.2f}, viés L3−L4 = {(j.L3 - j['L4 superfície']).mean():+.3f} m³/m³, n = {len(j)}")
    fig, ax = plt.subplots(1, 2, figsize=(13, 3.8))
    s3.plot(ax=ax[0], lw=0.5, marker=".", ms=2)
    ax[0].set_title("SMAP L3 AM — média do Ceará (m³/m³)")
    valido.to_series().resample("MS").mean().plot(ax=ax[1])
    ax[1].set_title("Fração de pixels válidos por mês")
    plt.tight_layout()
    plt.show()
else:
    print("SMAP L3 ainda não baixado.")

# %% [markdown]
# ### 5.2 GLDAS-2.1 Noah (mensal) — balanço hídrico em camadas
# As umidades vêm em kg/m² (= mm de água na camada). ET e chuva vêm em kg/m²/s (× 86.400 = mm/dia).

# %%
gm_f = DADOS / "gldas" / "gldas_noah025_mensal_ne.nc"
if gm_f.exists():
    gm = xr.open_dataset(gm_f)
    m = mascara(gm, CE)
    cam = {"0–10 cm": "SoilMoi0_10cm_inst", "10–40 cm": "SoilMoi10_40cm_inst", "40–100 cm": "SoilMoi40_100cm_inst",
           "100–200 cm": "SoilMoi100_200cm_inst", "zona da raiz": "RootMoist_inst"}
    S = pd.DataFrame({k: gm[v].where(m).mean(("lat", "lon")).to_series() for k, v in cam.items() if v in gm})
    S["ET mm/dia"] = gm["Evap_tavg"].where(m).mean(("lat", "lon")).to_series() * 86400
    S["chuva mm/dia"] = gm["Rainf_f_tavg"].where(m).mean(("lat", "lon")).to_series() * 86400
    S.index = pd.to_datetime(S.index)
    print(f"GLDAS Noah: {len(S)} meses, {S.index.min():%Y-%m} → {S.index.max():%Y-%m}")
    display(S.describe(percentiles=[0.05, 0.5, 0.95]).T.round(2))
    fig, ax = plt.subplots(1, 2, figsize=(14, 4))
    S[[c for c in cam if c in S]].groupby(S.index.month).mean().plot(ax=ax[0], marker="o")
    ax[0].set_title("Climatologia da umidade por camada (mm)")
    S[["ET mm/dia", "chuva mm/dia"]].groupby(S.index.month).mean().plot.bar(ax=ax[1])
    ax[1].set_title("Chuva × ET (GLDAS) — mm/dia")
    plt.tight_layout()
    plt.show()
    display(pd.DataFrame([tendencia(S[c], f"GLDAS {c}") for c in S.columns]).dropna())
    print("Atenção: tendência de 2000–2026 depende do período (seca de 2012–2017 perto do fim). O POWER, de 1981 a 2026,"
          " não mostra tendência de chuva (seção 1). Leia como 'queda nesta janela', não como mudança de longo prazo.")
    anom = S["zona da raiz"] - S["zona da raiz"].groupby(S.index.month).transform("mean")
    fig, ax = plt.subplots(figsize=(13, 3.5))
    ax.bar(anom.index, anom.values, width=25, color=np.where(anom > 0, "tab:blue", "tab:red"))
    ax.axvspan(pd.Timestamp("2012-01-01"), pd.Timestamp("2017-12-31"), color="orange", alpha=0.12)
    ax.set_title("Anomalia da umidade da zona da raiz (GLDAS, mm) — seca 2012–2017 em destaque")
    plt.show()
else:
    print("GLDAS mensal ainda não consolidado.")

# %% [markdown]
# ### 5.3 GLDAS-2.2 CLSM — água subterrânea × GRACE
# O CLSM assimila o GRACE, então o armazenamento total (TWS) dele deve acompanhar o GRACE. A vantagem é a resolução:
# 0,25° contra ~300 km efetivos, e a separação entre **água subterrânea (GWS)**, umidade do solo e superfície.

# %%
gc_f = DADOS / "gldas" / "gldas_clsm025_diario_ne.nc"
if gc_f.exists():
    gc = xr.open_dataset(gc_f)
    mens = gc[["GWS_tavg", "TWS_tavg", "SoilMoist_RZ_tavg"]].resample(time="MS").mean()
    regs = {"Ceará": CE, "Nordeste": NE}
    fig, ax = plt.subplots(1, 2, figsize=(14, 4))
    linhas = []
    for a, (nome, g) in zip(ax, regs.items()):
        m = mascara(mens, g)
        gws = mens.GWS_tavg.where(m).mean(("lat", "lon")).to_series()
        tws = mens.TWS_tavg.where(m).mean(("lat", "lon")).to_series()
        ((gws - gws.mean()) / 10).plot(ax=a, label="água subterrânea (anomalia, cm)")
        ((tws - tws.mean()) / 10).plot(ax=a, label="TWS CLSM (anomalia, cm)")
        gr = DERIV / ("grace_ce_mensal.parquet" if nome == "Ceará" else "grace_ne_mensal.parquet")
        if gr.exists():
            G = pd.read_parquet(gr).set_index("data")["valor"]
            G.index = pd.to_datetime(G.index)
            (G - G.mean()).plot(ax=a, label="GRACE TWS (anomalia, cm)", alpha=0.8)
            j = pd.concat([(tws - tws.mean()) / 10, G - G.mean()], axis=1).dropna()
            linhas.append({"região": nome, "r(CLSM TWS, GRACE)": round(j.corr().iloc[0, 1], 3), "meses": len(j)})
        linhas.append(tendencia(gws, f"GWS {nome}"))
        a.axvspan(pd.Timestamp("2012-01-01"), pd.Timestamp("2017-12-31"), color="orange", alpha=0.12)
        a.legend(fontsize=7)
        a.set_title(nome)
    plt.tight_layout()
    plt.show()
    print("Concordância CLSM × GRACE (anomalia de armazenamento total):")
    display(pd.DataFrame([l for l in linhas if l and "região" in l]))
    print("Tendência da água subterrânea (CLSM), teste sazonal de Mann-Kendall:")
    display(pd.DataFrame([l for l in linhas if l and "série" in l]))
    tr = mens.GWS_tavg.groupby("time.year").mean()
    anos = tr.year.values
    incl = xr.apply_ufunc(lambda y: np.polyfit(anos, y, 1)[0] if np.isfinite(y).all() else np.nan, tr,
                          input_core_dims=[["year"]], vectorize=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    incl.plot(ax=ax, cmap="RdBu", center=0, cbar_kwargs={"label": "mm/ano"})
    NE.boundary.plot(ax=ax, color="k", lw=0.5)
    ax.set_title("Tendência linear da água subterrânea (GLDAS CLSM), mm/ano")
    plt.show()
else:
    print("GLDAS CLSM ainda não consolidado.")

# %% [markdown]
# ### 5.4 NLDAS-2 (EUA) — o mesmo balanço onde está o CDL
# A caixa cobre Kansas, Iowa e o Texas semiárido (Lubbock), as janelas do estudo do CDL (seção 14). Serve para
# comparar o regime hídrico das rotações americanas com o do sertão.

# %%
nl_f = DADOS / "nldas" / "nldas_noah0125_mensal_planicies_eua.nc"
if nl_f.exists():
    nl = xr.open_dataset(nl_f)
    pontos = {"Iowa (milho-soja)": (-93.6, 42.0), "Kansas Ogallala": (-100.9, 37.6), "Texas Lubbock (algodão)": (-101.85, 33.6)}
    vsm = "SoilM_0_100cm" if "SoilM_0_100cm" in nl else list(nl.data_vars)[0]
    fig, ax = plt.subplots(1, 2, figsize=(14, 4))
    clim = {}
    for nome, (lo, la) in pontos.items():
        s = nl[vsm].sel(lon=lo, lat=la, method="nearest").to_series()
        s.index = pd.to_datetime(s.index)
        clim[nome] = s.groupby(s.index.month).mean()
        s.rolling(12).mean().plot(ax=ax[0], label=nome)
    ax[0].set_title(f"NLDAS {vsm} (mm) — média móvel 12 meses")
    ax[0].legend(fontsize=8)
    pd.DataFrame(clim).plot(ax=ax[1], marker="o")
    ax[1].set_title("Climatologia mensal (mm)")
    plt.tight_layout()
    plt.show()
    print(f"NLDAS: {nl.sizes['time']} meses, {str(nl.time.values.min())[:7]} → {str(nl.time.values.max())[:7]}; "
          f"caixa lon {float(nl.lon.min()):.2f}..{float(nl.lon.max()):.2f}, lat {float(nl.lat.min()):.2f}..{float(nl.lat.max()):.2f}")
else:
    print("NLDAS ainda não consolidado.")

# %% [markdown]
# ### 5.5 VIIRS NDVI — continuidade do MODIS
# O Terra/MODIS está no fim da vida (lacuna de jun–nov/2025, seção 9). O VIIRS (VNP13A3, 1 km mensal) é o sucessor.
# Comparamos as duas séries do Ceará no período comum para saber se dá para emendar uma na outra.

# %%
vi_f = DADOS / "viirs" / "vnp13a3_ndvi_evi_ceara_001deg.nc"
vi = xr.open_dataset(vi_f) if vi_f.exists() else abrir_appeears("viirs_vnp13a3_ceara", "VNP13A3")
if vi is not None:
    vn = "ndvi" if "ndvi" in vi else var(vi, "NDVI")
    vr = None if "ndvi" in vi else var(vi, "pixel_reliability")  # consolidado já filtrou confiabilidade 0–1
    nd = vi[vn]
    if vr:
        nd = nd.where(vi[vr] <= 1)  # 0 = boa, 1 = marginal
    nd = nd.where((nd > -0.2) & (nd <= 1))
    sv = serie_regional(nd, CE).resample("MS").mean()
    mod = DERIV / "modis_ce_mensal.parquet"
    fig, ax = plt.subplots(figsize=(13, 3.8))
    sv.plot(ax=ax, label="VIIRS VNP13A3 (1 km)")
    if mod.exists():
        M = pd.read_parquet(mod)
        M = M[M.variavel == "ndvi"].set_index("data")["valor"]
        M.index = pd.to_datetime(M.index)
        M.plot(ax=ax, label="MODIS MOD13Q1 (seção 9)", alpha=0.8)
        j = pd.concat([sv.rename("viirs"), M.rename("modis")], axis=1).dropna()
        print(f"VIIRS × MODIS (Ceará, mensal): r = {j.corr().iloc[0, 1]:.3f}, viés VIIRS−MODIS = {(j.viirs - j.modis).mean():+.3f}, "
              f"RMSD = {np.sqrt(((j.viirs - j.modis) ** 2).mean()):.3f}, meses = {len(j)}")
        lac = sv["2025-06":"2025-11"]
        print("NDVI VIIRS nos meses da lacuna do Terra (jun–nov/2025):", lac.round(3).to_dict())
    ax.legend()
    ax.set_title("NDVI médio do Ceará — VIIRS × MODIS")
    plt.show()
    pd.DataFrame({"data": sv.index, "variavel": "ndvi", "valor": sv.values, "unidade": "-", "fonte": "VIIRS VNP13A3.002"}).to_parquet(
        DERIV / "viirs_ndvi_ce_mensal.parquet", index=False)
else:
    print("VIIRS NDVI ainda não baixado.")

# %% [markdown]
# ### 5.6 IMERG V07 2026 — o presente
# A chuva de ago–nov/2026 no Ceará contra a climatologia do IMERG de 1998–2025 (seção 2). Ago–nov é a estação seca;
# o interesse é a anomalia e o alerta de El Niño para a quadra de 2027 (seção 20).

# %%
rec = DERIV / "imerg_late_ce_mensal.parquet"
hist = DERIV / "imerg_ce_mensal.parquet"
if rec.exists() and hist.exists():
    R = pd.read_parquet(rec)
    R = R[R.variavel == "precipitation"].set_index("data")["valor"]
    H = pd.read_parquet(hist)
    H = H[H.variavel == "precip_total"].set_index("data")["valor"]
    H.index, R.index = pd.to_datetime(H.index), pd.to_datetime(R.index)
    clim = H[H.index.year <= 2025].groupby(H[H.index.year <= 2025].index.month).agg(["mean", "std"])
    ultimo_dia = pd.Timestamp(str(xr.open_dataset(DADOS / "imerg" / "imerg_v07_late_diario_ne_recente.nc").time.values.max())[:10])
    T = pd.DataFrame({"IMERG Late 2026 (mm)": R.round(1)})
    frac = [min(1.0, ultimo_dia.day / d.days_in_month) if (d.year, d.month) == (ultimo_dia.year, ultimo_dia.month) else 1.0 for d in T.index]
    T["dias cobertos (fração)"] = np.round(frac, 2)
    T["climatologia proporcional (mm)"] = [round(clim.loc[d.month, "mean"] * f, 1) for d, f in zip(T.index, frac)]
    T["anomalia padronizada"] = [round((r - clim.loc[d.month, "mean"] * f) / (clim.loc[d.month, "std"] * f), 2) for (d, r), f in zip(R.items(), frac)]
    display(T)
    print(f"Último dia do IMERG Late: {ultimo_dia:%Y-%m-%d}. No mês parcial, a climatologia é proporcional aos dias cobertos.")

# %% [markdown]
# ### 5.7 Insights (Earthdata)
# Os números desta seção são calculados acima, a cada execução. Leitura para o produto:
# - **SMAP L4 é a camada de "água no solo" do motor.** É contínuo (sem buracos de órbita), tem a zona da raiz e traz o
#   percentil pronto, que funciona como índice de seca agrícola global e comparável entre lugares.
# - **O SMAP L3** serve para validar e mostrar que há observação de satélite por trás. Tem buracos e ruído a 9 km.
# - **GLDAS** dá o balanço em camadas e, no CLSM, a **água subterrânea a 0,25°**, a ponte entre o GRACE regional e a
#   decisão de irrigação.
# - **NLDAS** só serve nos EUA. No produto mundial, ele é substituído pelo GLDAS.
# - **VIIRS** garante a continuidade do NDVI quando o Terra/MODIS sair de operação. Se o viés contra o MODIS for
#   pequeno, as séries podem ser emendadas; caso contrário, as anomalias são calculadas por sensor.
