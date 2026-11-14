"""Pesquisador de IA - painel municipal (Ceara) IMERG diario x IBGE PAM.

Constroi, para cada municipio do Ceara e cada ano 1998-2025:
  - chuva diaria media do municipio (celulas IMERG 0,1 grau com centro dentro do poligono; senao a mais proxima);
  - atributos da quadra: P_jan, P_fev..P_mai, P_fmam, maior veranico (dias seguidos < 2 mm) em fev-mai,
    no de veranicos >= 10 d, inicio "retrospectivo" (Liebmann & Marengo, usa o futuro) e inicio "causal"
    (1o dia a partir de 1/jan com >= 20 mm em 3 dias - conhecido no proprio dia);
  - rendimento efetivo por area PLANTADA (inclui perda de area) de milho, feijao, mandioca e fava.
Saida: conselho/analises/saidas/painel_mun_ce.parquet e chuva_mun_diaria.parquet
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from shapely.geometry import Point

OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
OUT.mkdir(parents=True, exist_ok=True)

# 1) chuva diaria municipal
ds = xr.open_mfdataset(sorted(str(p) for p in (DADOS / "imerg").glob("imerg_ce_diario_*.nc")), combine="by_coords")
pr = ds["precip"].load()
lat, lon = pr.lat.values, pr.lon.values
LL = np.array([(a, b) for a in lat for b in lon])
pts = gpd.GeoDataFrame({"i": range(len(LL))}, geometry=[Point(b, a) for a, b in LL], crs="EPSG:4326")
mun = gpd.read_file(REF / "ceara_municipios.geojson").to_crs("EPSG:4326")
j = gpd.sjoin(pts, mun[["codarea", "geometry"]], predicate="within")
arr = pr.values.reshape(pr.shape[0], -1)  # tempo x celula
series = {}
for _, row in mun.iterrows():
    idx = j.loc[j.codarea == row.codarea, "i"].values
    if len(idx) == 0:
        c = row.geometry.representative_point()
        idx = [int(np.argmin((LL[:, 0] - c.y) ** 2 + (LL[:, 1] - c.x) ** 2))]
    series[row.codarea] = np.nanmean(arr[:, idx], axis=1)
chuva = pd.DataFrame(series, index=pd.to_datetime(pr.time.values))
chuva.to_parquet(OUT / "chuva_mun_diaria.parquet")
print("chuva municipal:", chuva.shape, chuva.index.min().date(), chuva.index.max().date())
cent = mun.set_index("codarea").geometry.representative_point()


def maior_seq(b):
    m = c = 0
    for v in b:
        c = c + 1 if v else 0
        m = max(m, c)
    return m


def n_seq(b, minimo):
    n = c = 0
    for v in list(b) + [False]:
        if v:
            c += 1
        else:
            if c >= minimo:
                n += 1
            c = 0
    return n


media_dia = chuva.mean()
linhas = []
for ano in range(1998, 2026):
    for cod in chuva.columns:
        s = chuva[cod]
        q = s[f"{ano}-02-01":f"{ano}-05-31"]
        if len(q) < 118:
            continue
        r = {"cod": cod, "ano": ano}
        for m, nome in [(1, "jan"), (2, "fev"), (3, "mar"), (4, "abr"), (5, "mai")]:
            r[f"P_{nome}"] = float(s[(s.index.year == ano) & (s.index.month == m)].sum())
        r["P_fmam"] = r["P_fev"] + r["P_mar"] + r["P_abr"] + r["P_mai"]
        seco = (q.values < 2.0)
        r["veranico_max_fmam"] = maior_seq(seco)
        r["n_veranico10_fmam"] = n_seq(seco, 10)
        q2 = s[f"{ano}-02-01":f"{ano}-04-30"].values < 2.0
        r["veranico_max_fev_abr"] = maior_seq(q2)
        # inicio retrospectivo (Liebmann & Marengo; usa a serie ate 30/abr -> olha o futuro)
        h = s[f"{ano-1}-08-01":f"{ano}-04-30"]
        if len(h) > 200:
            A = (h - media_dia[cod]).cumsum()
            ini = A.idxmin()
            r["inicio_LM_doy"] = ini.dayofyear if ini.year == ano else ini.dayofyear - 365
        # inicio causal: 1o dia a partir de 1/jan com >= 20 mm acumulados em 3 dias
        z = s[f"{ano}-01-01":f"{ano}-05-31"].rolling(3).sum()
        ok = z[z >= 20]
        r["inicio_causal_doy"] = ok.index[0].dayofyear if len(ok) else 152
        linhas.append(r)
P = pd.DataFrame(linhas)
P["lat"] = P.cod.map(cent.y)
P["lon"] = P.cod.map(cent.x)
srtm = pd.read_parquet(DERIV / "srtm_municipios_ce.parquet").set_index("codarea")
P["elev"] = P.cod.map(srtm.elev_media)

# 2) rendimentos (PAM municipal)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.cod_local.str.startswith("23") & (pam.ano >= 1998)]
mapa = {"milho": "Milho (em gr", "feijao": "Feij", "mandioca": "Mandioca", "fava": "Fava"}  # "Milho" sozinho pegava "Milho verde"
for k, pref in mapa.items():
    x = pam[pam.produto.str.startswith(pref)].copy()
    x["rend_ef"] = np.where(x.area_plantada_ha > 0, x.producao_t * 1000 / x.area_plantada_ha, np.nan)
    x = x.rename(columns={"cod_local": "cod"})[["cod", "ano", "rend_ef", "area_plantada_ha", "area_colhida_ha"]]
    x.columns = ["cod", "ano", f"rend_{k}", f"aplant_{k}", f"acolh_{k}"]
    P = P.merge(x, on=["cod", "ano"], how="left")
P.to_parquet(OUT / "painel_mun_ce.parquet")
print("painel:", P.shape)
print(P.describe().T[["mean", "std", "min", "max"]].round(2).to_string())
