"""v3 - Especialista sensoriamento/hidrologia - Teste 2 (balanco hidrico x rendimento: Vale 2023 e Rossato 2017).

 a) Rossato et al. 2017 (Front Environ Sci 5:73), Tabela 1 (coluna CE): desvio % do rendimento em 2012 em relacao a media
    2000-2012: arroz -25, feijao -52, mandioca -50, milho -60. Tabela 2 (CE, medias 2000-2012): arroz 1.787,39;
    feijao 310,96; mandioca 8.758,53; milho 770,62 kg/ha. Reproduzimos com o PAM municipal do IBGE.
 b) Rossato 2017: a chuva correlaciona mais com o rendimento do que a agua no solo em 0-100 cm porque a raiz media fica em
    40 cm. Testamos com IMERG (chuva) e GLDAS Noah 2.1 (camadas 0-10, 10-40 e 40-100 cm), por municipio do CE.
 c) Vale et al. 2023 (Theor Appl Climatol; PDF local = preprint Research Square 2022): balanco sequencial de
    Thornthwaite-Mather com CAD = 100 mm (MERRA-2) e rendimentos municipais; no semiarido o feijao correlaciona com
    P (0,75), armazenamento WSS (0,76), excedente EXC (0,61), ETP (-0,72) e deficit DEF (-0,58). Refazemos com
    IMERG + POWER (ETP de Thornthwaite com T2M do POWER, como no artigo, e ET0 FAO-56 do POWER) por classe de Thornthwaite.
 d) Conferencias de consistencia da Tabela 2 do Vale (fechamento do balanco, radiacao 34-36 MJ/m2/dia).
 e) Anderson et al. 2016 (RSE 174): ESI = anomalia de ET/ETref. Versao simples: MOD16 ET/PET anual x rendimento do CE.
"""
import sys
import time

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import json
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import shape

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
T0 = time.time()


def secao(t):
    print("\n" + "=" * 100 + f"\n{t}  [{time.time()-T0:.0f}s]\n" + "=" * 100)


# ---------------------------------------------------------------- municipios
g = json.load(open(REF / "ceara_municipios.geojson", encoding="utf-8"))
mun = gpd.GeoDataFrame(
    {"cod": [int(f["properties"]["codarea"]) for f in g["features"]]},
    geometry=[shape(f["geometry"]) for f in g["features"]], crs="EPSG:4326")
mun["lon_c"] = mun.geometry.representative_point().x
mun["lat_c"] = mun.geometry.representative_point().y

# ---------------------------------------------------------------- PAM
secao("(a) Rossato 2017 - desvios de 2012 e medias 2000-2012 no CE com o PAM municipal")
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam["cod_local"].astype(int)
CULT = {"Arroz (em casca)": "arroz", "Feijão (em grão)": "feijao", "Mandioca": "mandioca", "Milho (em grão)": "milho"}
pam = pam[pam["produto"].isin(CULT) & pam["cod"].isin(mun["cod"])].copy()
pam["cult"] = pam["produto"].map(CULT)
for c in ["area_colhida_ha", "area_plantada_ha", "producao_t", "rendimento_kg_ha"]:
    pam[c] = pd.to_numeric(pam[c], errors="coerce")
uf = pam.groupby(["cult", "ano"])[["producao_t", "area_colhida_ha", "area_plantada_ha"]].sum()
uf["rend_colh"] = 1000 * uf["producao_t"] / uf["area_colhida_ha"]
uf["rend_plant"] = 1000 * uf["producao_t"] / uf["area_plantada_ha"]
pm = pam[pam["area_colhida_ha"] > 0]
uf["rend_mun_media"] = pm.groupby(["cult", "ano"])["rendimento_kg_ha"].mean()
ART_T1 = {"arroz": {2010: -24, 2012: -25, 2006: 29}, "feijao": {2010: -33, 2012: -52, 2006: 51},
          "mandioca": {2010: -42, 2012: -50, 2006: 21}, "milho": {2010: -55, 2012: -60, 2006: 56}}
ART_T2 = {"arroz": 1787.39, "feijao": 310.96, "mandioca": 8758.53, "milho": 770.62}
print(f"{'cultura':9s} {'base':28s} {'media00-12':>10s} {'art T2':>8s} | desvio% 2006 / 2010 / 2012 (nosso) | artigo T1")
for c in CULT.values():
    for base, rot in [("rend_colh", "UF: prod/area colhida"), ("rend_mun_media", "media simples dos municipios"),
                      ("rend_plant", "UF: prod/area PLANTADA")]:
        s = uf.loc[c, base]
        m = s.loc[2000:2012].mean()
        d = {a: 100 * (s.loc[a] / m - 1) for a in (2006, 2010, 2012)}
        art = ART_T1[c]
        print(f"{c:9s} {rot:28s} {m:10.1f} {ART_T2[c]:8.1f} | {d[2006]:+6.0f} / {d[2010]:+6.0f} / {d[2012]:+6.0f}"
              f"            | {art[2006]:+d} / {art[2010]:+d} / {art[2012]:+d}")
perda = uf.loc[(slice(None), 2012), :]
for c in ["feijao", "milho"]:
    r = uf.loc[(c, 2012)]
    print(f"   {c} 2012: area plantada {r.area_plantada_ha:,.0f} ha, colhida {r.area_colhida_ha:,.0f} ha "
          f"({100*r.area_colhida_ha/r.area_plantada_ha:.0f}% colhida)")

# ---------------------------------------------------------------- chuva IMERG por municipio
secao("Clima por municipio: IMERG 0,1 grau (media das celulas no municipio), POWER e GLDAS (celula mais proxima)")
im = xr.concat([xr.open_dataset(DADOS / "imerg" / f"imerg_ce_diario_{a}.nc")["precip"] for a in range(1998, 2027)], dim="time")
im_m = im.resample(time="MS").sum(min_count=25).load()
lat_i, lon_i = im_m.lat.values, im_m.lon.values
LA, LO = np.meshgrid(lat_i, lon_i, indexing="ij")
pts = gpd.GeoDataFrame({"i": np.repeat(np.arange(len(lat_i)), len(lon_i)), "j": np.tile(np.arange(len(lon_i)), len(lat_i))},
                       geometry=gpd.points_from_xy(LO.ravel(), LA.ravel()), crs="EPSG:4326")
sj = gpd.sjoin(pts, mun[["cod", "geometry"]], predicate="within")
arr = im_m.values  # (t, lat, lon)
P = {}
for _, r in mun.iterrows():
    cel = sj[sj["cod"] == r["cod"]]
    if len(cel) == 0:
        i = int(np.abs(lat_i - r.lat_c).argmin()); j = int(np.abs(lon_i - r.lon_c).argmin())
        P[r["cod"]] = arr[:, i, j]
    else:
        P[r["cod"]] = arr[:, cel["i"].values, cel["j"].values].mean(axis=1)
P = pd.DataFrame(P, index=pd.DatetimeIndex(im_m.time.values)).loc[:"2026-08-01"]
print("municipios:", P.shape[1], "| sem celula 0,1 grau dentro:", int(mun["cod"].isin(sj["cod"]).eq(False).sum()))

pw = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")
pe = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")
t2m = pw["T2M"].resample(time="MS").mean().load()
et0 = pe["ET0"].resample(time="MS").sum().load()
rad = pw["ALLSKY_SFC_SW_DWN"].load()


def nearest_series(da, lat, lon):
    return da.sel(lat=lat, lon=lon, method="nearest").to_series()


def thornthwaite(tm, lat):
    """ETP de Thornthwaite mensal (mm) com correcao de fotoperiodo N/12 e dias/30; T>26,5 C pela formula de Willmott."""
    tm = tm.copy()
    clim = tm.groupby(tm.index.month).mean()
    I = ((clim.clip(lower=0) / 5) ** 1.514).sum()
    a = 6.75e-7 * I**3 - 7.71e-5 * I**2 + 1.792e-2 * I + 0.49239
    etp = np.where(tm < 26.5, 16 * (10 * tm.clip(lower=0) / I) ** a, -415.85 + 32.24 * tm - 0.43 * tm**2)
    doy = tm.index.dayofyear + 14
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(-np.tan(np.radians(lat)) * np.tan(dec))
    N = 24 / np.pi * ws
    nd = tm.index.days_in_month
    return pd.Series(etp * (N / 12) * (nd / 30), index=tm.index)


def balanco(p, etp, cad=100.0):
    s = cad
    out = []
    for pi, ei in zip(p.values, etp.values):
        if pi < ei:
            s1 = s * np.exp((pi - ei) / cad)
            aet = pi + s - s1
            out.append((s1, ei - aet, 0.0))
        else:
            s1 = min(cad, s + pi - ei)
            out.append((s1, 0.0, s + pi - ei - s1))
        s = s1
    o = pd.DataFrame(out, index=p.index, columns=["WSS", "DEF", "EXC"])
    o["P"], o["PET"] = p.values, etp.values
    return o


gl = xr.open_dataset(DADOS / "gldas" / "gldas_noah025_mensal_ne.nc")
gl = gl.sel(lat=slice(-8.0, -2.5), lon=slice(-41.5, -37.0))
anual = {}
mensal_semi = []
for _, r in mun.iterrows():
    cod = r["cod"]
    p = P[cod]
    tm = nearest_series(t2m, r.lat_c, r.lon_c).reindex(p.index)
    e0 = nearest_series(et0, r.lat_c, r.lon_c).reindex(p.index)
    etp_th = thornthwaite(tm, r.lat_c)
    for nome, etp in [("TH", etp_th), ("FAO", e0)]:
        b = balanco(p, etp).loc["1999-01-01":]
        a = b.groupby(b.index.year).sum()
        a.loc[:, "WSS_FMAM"] = b[b.index.month.isin([2, 3, 4, 5])].groupby(b.index[b.index.month.isin([2, 3, 4, 5])].year)["WSS"].mean()
        anual[(cod, nome)] = a.loc[:2025]
        b["cod"] = cod
        b["etp"] = nome
        mensal_semi.append(b)
    gcel = gl.sel(lat=r.lat_c, lon=r.lon_c, method="nearest")
    s010 = gcel["SoilMoi0_10cm_inst"].to_series(); s1040 = gcel["SoilMoi10_40cm_inst"].to_series()
    s40100 = gcel["SoilMoi40_100cm_inst"].to_series()
    gdf = pd.DataFrame({"g0_40": s010 + s1040, "g0_100": s010 + s1040 + s40100, "g40_100": s40100})
    gdf.index = pd.DatetimeIndex(gdf.index)
    ga = gdf.groupby(gdf.index.year).mean()
    gf = gdf[gdf.index.month.isin([2, 3, 4, 5])]
    ga = ga.join(gf.groupby(gf.index.year).mean().add_suffix("_FMAM"))
    pa = p.groupby(p.index.year).sum()
    pf = p[p.index.month.isin([1, 2, 3, 4, 5])]
    ga["P_ano"] = pa
    ga["P_JFMAM"] = pf.groupby(pf.index.year).sum()
    anual[(cod, "GL")] = ga

# classificacao de Thornthwaite por municipio (1999-2025)
secao("(c) Vale 2023 - classes de Thornthwaite no CE (Im = Ih - 0,6 Ia) com IMERG + POWER")
CLS = [(-60, -40, "arido E"), (-40, -20, "semiarido D"), (-20, 0, "subumido seco C1"), (0, 20, "subumido umido C2"),
       (20, 40, "umido B1"), (40, 60, "umido B2"), (60, 999, "umido B3+")]


def classe(im_):
    for lo, hi, n in CLS:
        if lo <= im_ < hi:
            return n
    return "hiperarido" if im_ < -60 else "?"


rows = []
for _, r in mun.iterrows():
    for nome in ["TH", "FAO"]:
        a = anual[(r["cod"], nome)].mean()
        im_ = 100 * a.EXC / a.PET - 60 * a.DEF / a.PET
        rows.append({"cod": r["cod"], "etp": nome, "Im": im_, "classe": classe(im_), "P": a.P, "PET": a.PET,
                     "DEF": a.DEF, "EXC": a.EXC, "WSS": a.WSS})
cl = pd.DataFrame(rows)
for nome in ["TH", "FAO"]:
    c = cl[cl.etp == nome]
    print(f"\n   ETP = {'Thornthwaite (T2M POWER, metodo do artigo)' if nome=='TH' else 'ET0 FAO-56 (POWER)'}:")
    print(c.groupby("classe")[["P", "PET", "WSS", "DEF", "EXC", "Im"]].mean().round(1).assign(
        n=c.groupby("classe").size()).to_string())
print("\n   Vale Tab.2 (NEB, MERRA-2): semiarido P 695,0 PET 1.641,7 WSS 223,4 DEF 1.004,8 EXC 100,5 (746 mun);"
      " subumido seco P 932,2 PET 1.541,5 WSS 386,3 DEF 757,7 EXC 210,8 (536 mun)")

# correlacoes no estilo do Vale: series medias da classe (1999-2019, periodo comum com o artigo)
secao("(c) Vale 2023 - correlacao de Pearson entre series anuais medias da classe e rendimento medio da classe")
rend = pam[pam["area_colhida_ha"] > 0].pivot_table(index="ano", columns=["cult", "cod"], values="rendimento_kg_ha")
rplant = pam.assign(rp=1000 * pam.producao_t / pam.area_plantada_ha.replace(0, np.nan)).pivot_table(
    index="ano", columns=["cult", "cod"], values="rp")
ART_V = {"semiarido D": {"P": .75, "WSS": .76, "EXC": .61, "PET": -.72, "DEF": -.58},
         "subumido seco C1": {"P": .76, "WSS": .74, "EXC": .69, "PET": -.78, "DEF": -.72}}
for nome in ["TH", "FAO"]:
    c = cl[cl.etp == nome]
    for cls_ in ["semiarido D", "subumido seco C1"]:
        cods = c.loc[c.classe == cls_, "cod"].tolist()
        if len(cods) < 5:
            continue
        clim = pd.concat([anual[(k, nome)][["P", "PET", "WSS", "DEF", "EXC"]] for k in cods]).groupby(level=0).mean()
        for alvo_nome, alvo in [("rend/colhida", rend), ("rend/plantada", rplant)]:
            for cult in ["feijao", "milho", "mandioca"]:
                y = alvo[cult][[k for k in cods if k in alvo[cult].columns]].mean(axis=1)
                for periodo in [(1999, 2019), (1999, 2025)]:
                    j = clim.join(y.rename("y"), how="inner").loc[periodo[0]:periodo[1]]
                    rr = {v: j[v].corr(j["y"]) for v in ["P", "WSS", "EXC", "PET", "DEF"]}
                    art = ART_V.get(cls_, {}) if (cult == "feijao" and periodo == (1999, 2019) and alvo_nome == "rend/colhida") else {}
                    extra = ("  | artigo feijao: " + " ".join(f"{k}={v:+.2f}" for k, v in art.items())) if art else ""
                    print(f"   ETP={nome:3s} {cls_:17s} n_mun={len(cods):3d} {alvo_nome:13s} {cult:8s} {periodo[0]}-{periodo[1]} "
                          + " ".join(f"{k}={v:+.2f}" for k, v in rr.items()) + extra)

# janela de semeadura: balanco climatologico mensal do semiarido CE (ET0 FAO e TH)
secao("(c) Vale 2023 - meses com P > ETP (janela de semeadura do semiarido: jan-abr no artigo)")
bm = pd.concat(mensal_semi)
for nome in ["FAO", "TH"]:
    semi = cl[(cl.etp == nome) & (cl.classe == "semiarido D")]["cod"].tolist()
    bs = bm[bm["cod"].isin(semi) & (bm["etp"] == nome)]
    clim_m = bs.groupby(bs.index.month)[["P", "PET", "WSS", "EXC", "DEF"]].mean().round(1)
    print(f"   semiarido D (ETP={nome}), {len(semi)} municipios, media 1999-2026:")
    print(clim_m.assign(P_menos_PET=(clim_m.P - clim_m.PET).round(1)).to_string())

# ---------------------------------------------------------------- (b) Rossato: chuva x agua no solo por camada
secao("(b) Rossato 2017 - r(rendimento, X) por municipio; mediana entre municipios (rendimento bruto e sem tendencia)")


def detr(s):
    s = s.dropna()
    if len(s) < 6:
        return s
    x = np.arange(len(s))
    return s - np.polyval(np.polyfit(x, s.values, 1), x)


VARS = ["P_ano", "P_JFMAM", "g0_40", "g0_100", "g40_100", "g0_40_FMAM", "g0_100_FMAM", "g40_100_FMAM"]
for periodo in [(2000, 2012), (2000, 2025)]:
    for cult in ["feijao", "milho", "mandioca", "arroz"]:
        for modo in ["bruto", "sem tendencia"]:
            res = {v: [] for v in VARS}
            for k in rend[cult].columns:
                y = rend[cult][k].loc[periodo[0]:periodo[1]]
                if y.notna().sum() < (10 if periodo[1] == 2012 else 18):
                    continue
                X = anual[(k, "GL")].loc[periodo[0]:periodo[1]]
                j = X.join(y.rename("y"), how="inner").dropna()
                if modo != "bruto":
                    j = j.apply(detr)
                for v in VARS:
                    res[v].append(j[v].corr(j["y"]))
            if not res["P_ano"]:
                continue
            print(f"   {periodo[0]}-{periodo[1]} {cult:8s} {modo:13s} n_mun={len(res['P_ano']):3d} | "
                  + " ".join(f"{v}={np.nanmedian(res[v]):+.2f}" for v in VARS))

# ---------------------------------------------------------------- (d) conferencias da Tabela 2 do Vale
secao("(d) Vale 2023 Tabela 2 - fechamento P ~ (PET - DEF) + EXC e radiacao")
V = {"arido": (468.3, 1719.5, 1260.7, 31.0), "semiarido": (695.0, 1641.7, 1004.8, 100.5),
     "subumido seco": (932.2, 1541.5, 757.7, 210.8), "subumido umido": (1187.2, 1460.2, 561.0, 364.2),
     "umido B1": (1532.4, 1608.6, 634.8, 642.0), "umido B2": (2024.0, 1714.5, 608.3, 1007.4)}
for k, (p_, pet, de, ex) in V.items():
    aet = pet - de
    im_ = 100 * ex / pet - 60 * de / pet
    print(f"   {k:15s} P={p_:7.1f}  ETR+EXC={aet+ex:7.1f}  residuo={p_-(aet+ex):+6.1f} mm/ano ({100*(p_-(aet+ex))/p_:+.1f}%)  "
          f"Im das medias={im_:+6.1f} -> {classe(im_)}")
lat_ce = float(rad.lat.mean())
ra = []
for la in [-3.0, -5.0, -7.5, -10.0, -15.0]:
    J = np.arange(1, 366)
    dr = 1 + 0.033 * np.cos(2 * np.pi * J / 365)
    d = 0.409 * np.sin(2 * np.pi * J / 365 - 1.39)
    phi = np.radians(la)
    ws = np.arccos(-np.tan(phi) * np.tan(d))
    Ra = 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(phi) * np.sin(d) + np.cos(phi) * np.cos(d) * np.sin(ws))
    ra.append(f"lat {la:+.1f}: Ra medio {Ra.mean():.1f}")
print("   radiacao no topo da atmosfera (FAO-56 eq. 21), MJ/m2/dia:", "; ".join(ra))
print(f"   POWER ALLSKY_SFC_SW_DWN medio no CE 1981-2025 = {float(rad.sel(time=slice('1981','2025')).mean()):.1f} MJ/m2/dia "
      "(Vale Tab.2: 34,1 a 36,0 MJ/m2/dia na superficie)")

# ---------------------------------------------------------------- (e) Anderson: fRET anual (MOD16) x rendimento UF
secao("(e) Anderson 2016 (versao simples) - anomalia de ET/PET anual (MOD16A3GF, CE) x rendimento do CE")
mod = pd.read_parquet(DERIV / "modis_ce_mensal.parquet")
et = mod[mod.variavel == "et_anual"].set_index("data")["valor"]; pt = mod[mod.variavel == "pet_anual"].set_index("data")["valor"]
fret = (et / pt)
fret.index = pd.to_datetime(fret.index).year
print("   anos MOD16:", fret.index.min(), "-", fret.index.max(), "n=", len(fret))
for cult in ["feijao", "milho", "mandioca"]:
    for base in ["rend_colh", "rend_plant"]:
        y = uf.loc[cult, base]
        j = pd.concat([fret.rename("fRET"), y.rename("y")], axis=1).dropna().loc[2001:2024]
        jd = j.apply(detr)
        print(f"   {cult:8s} {base:10s} n={len(j)}  r bruto={j.fRET.corr(j.y):+.2f}  r sem tendencia={jd.fRET.corr(jd.y):+.2f}")

print(f"\nTempo total: {time.time()-T0:.0f} s")
