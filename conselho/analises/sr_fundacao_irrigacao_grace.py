"""Conselho - Especialista em sensoriamento remoto e modelos de fundacao.

Pergunta: a "pegada de irrigacao" vista do espaco (verde na seca, Landsat 8/9 a 30 m) acompanha a memoria
hidrica de varios anos (GRACE TWS e chuva acumulada IMERG)? Se sim, a viabilidade de uma rotacao irrigada
no ano que vem pode ser estimada ANTES do plantio com dados NASA, sem cadastro de outorga.

Metodo:
1. Para cada AOI e ano (2013-2026), janela seca ago-dez, pixels com >= 3 observacoes limpas.
   - "verde permanente na seca": mediana do NDVI >= 0,55 (pomar irrigado, mata ciliar perene)
   - "irrigacao ativa": p90 do NDVI >= 0,65 (pelo menos um ciclo verde forte em plena seca)
   Area em km2 (pixel de 30 m) normalizada pela area observada.
2. Correlacao de Spearman da area com: GRACE TWS da AOI (media ago-dez), chuva IMERG acumulada 12/24/36 meses
   ate julho, chuva fev-mai do mesmo ano.
3. Validacao fraca do rotulo: ESA CCI LC 2020 (300 m) - fracao de pixels "irrigacao ativa" em 2020 por classe.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
import warnings

import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Transformer
from scipy import stats

from comum import DADOS, DERIV

warnings.filterwarnings("ignore")

gr = pd.read_parquet(DERIV / "grace_aoi_mensal.parquet")
gr["data"] = pd.to_datetime(gr["data"])
im = pd.read_parquet(DERIV / "imerg_aoi_mensal.parquet")
im["data"] = pd.to_datetime(im["data"])
im = im[im.variavel == "precip_total"]
cci = xr.open_dataset(DADOS / "modis/esa_cci_lc_2020_nordeste_300m.nc").lccs_class

res = []
cci_tab = {}
for aoi in ["apodi_jaguaribe", "cariri", "sertao_central", "ibiapaba"]:
    ds = xr.open_dataset(DADOS / f"landsat/landsat_aoi_{aoi}.nc")
    t = pd.to_datetime(ds.time.values)
    nd = ds.ndvi.values.astype("float32")
    for ano in range(2013, 2027):
        sel = (t >= pd.Timestamp(ano, 8, 1)) & (t <= pd.Timestamp(ano, 12, 31))
        if sel.sum() < 3:
            continue
        cubo = nd[sel]
        nobs = np.isfinite(cubo).sum(0)
        ok = nobs >= 3
        med = np.nanmedian(cubo, 0)
        p90 = np.nanpercentile(cubo, 90, axis=0)
        n_ok = ok.sum()
        perm = (med >= 0.55) & ok
        ativa = (p90 >= 0.65) & ok
        res.append({"aoi": aoi, "ano": ano, "cenas": int(sel.sum()), "frac_pix_obs": n_ok / ok.size,
                    "pct_verde_perm": 100 * perm.sum() / max(n_ok, 1), "pct_irrig_ativa": 100 * ativa.sum() / max(n_ok, 1),
                    "km2_irrig_ativa_obs": ativa.sum() * 900 / 1e6, "ndvi_seca_mediana_aoi": float(np.nanmedian(med[ok]))})
        if ano == 2020:
            tr = Transformer.from_crs(ds.attrs.get("crs", "EPSG:32624"), "EPSG:4326", always_xy=True)
            X, Y = np.meshgrid(ds.x.values, ds.y.values)
            lo, la = tr.transform(X, Y)
            lat_idx = np.searchsorted(-cci.lat.values, -la.ravel())
            lon_idx = np.searchsorted(cci.lon.values, lo.ravel())
            lat_idx = np.clip(lat_idx, 0, cci.lat.size - 1)
            lon_idx = np.clip(lon_idx, 0, cci.lon.size - 1)
            cl = cci.values[lat_idx, lon_idx].reshape(X.shape)
            df = pd.DataFrame({"classe": cl[ok], "ativa": ativa[ok], "perm": perm[ok]})
            cci_tab[aoi] = df.groupby("classe").agg(pixels=("ativa", "size"), pct_irrig_ativa=("ativa", "mean"), pct_verde_perm=("perm", "mean"))
    ds.close()

R = pd.DataFrame(res)
print("== Area 'verde na seca' por AOI e ano (% dos pixels observados) ==")
print(R.pivot(index="ano", columns="aoi", values="pct_irrig_ativa").round(1).to_string())
print("\n(verde permanente, mediana >= 0,55)")
print(R.pivot(index="ano", columns="aoi", values="pct_verde_perm").round(1).to_string())

print("\n== Validacao fraca com ESA CCI 2020 (fracao de pixels por classe CCI) ==")
for aoi, tab in cci_tab.items():
    tab = tab[tab.pixels >= 2000].copy()
    tab["pct_irrig_ativa"] = (100 * tab.pct_irrig_ativa).round(1)
    tab["pct_verde_perm"] = (100 * tab.pct_verde_perm).round(1)
    print(f"-- {aoi}")
    print(tab.to_string())

print("\n== Area irrigada ativa x memoria hidrica (Spearman, anos 2013-2026) ==")
for aoi in ["apodi_jaguaribe", "cariri", "sertao_central", "ibiapaba"]:
    r = R[R.aoi == aoi].set_index("ano")
    g = gr[gr.aoi == aoi]
    g = g[g.data.dt.month.isin([8, 9, 10, 11, 12])].groupby(g.data.dt.year)["valor"].mean()
    c = im[im.aoi == aoi].set_index("data")["valor"].sort_index()
    feats = {"GRACE_TWS_ago_dez": g}
    for w in [12, 24, 36]:
        acc = c.rolling(w).sum()
        feats[f"chuva_acum_{w}m_ate_jul"] = acc[acc.index.month == 7].groupby(acc[acc.index.month == 7].index.year).first()
    q = c[c.index.month.isin([2, 3, 4, 5])]
    feats["chuva_fev_mai"] = q.groupby(q.index.year).sum()
    F = pd.DataFrame(feats)
    J = r[["pct_irrig_ativa", "pct_verde_perm"]].join(F, how="inner").dropna()
    linha = [f"{aoi:16s} n={len(J):2d}"]
    for k in feats:
        rho, p = stats.spearmanr(J.pct_irrig_ativa, J[k])
        linha.append(f"{k}: rho={rho:+.2f} (p={p:.3f})")
    print("  " + " | ".join(linha))
    if aoi == "apodi_jaguaribe":
        print(J.round(2).to_string())
        # janela seca mais critica: 2015-2017 vs 2020-2025
        a = J.loc[J.index.isin([2015, 2016, 2017]), "pct_irrig_ativa"].mean()
        b = J.loc[J.index.isin(range(2020, 2026)), "pct_irrig_ativa"].mean()
        print(f"  Apodi: irrigacao ativa media 2015-17 = {a:.1f}%  vs  2020-25 = {b:.1f}%  (razao {b / a:.2f}x)")
R.to_csv(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/sr_fundacao_irrigacao_anual.csv", index=False)
