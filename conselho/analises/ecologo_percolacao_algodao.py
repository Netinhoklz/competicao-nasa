"""Ecologo de pragas - Analise 2: percolacao da paisagem de hospedeiros no Ceara (algodao 1974-2025 e milho/sorgo hoje).

Perguntas:
  (a) A paisagem de algodao do Ceara era "percolada" (um aglomerado gigante de municipios vizinhos com muito hospedeiro)
      antes do bicudo (1983)? Quando se fragmentou?
  (b) A paisagem de hospedeiros da lagarta-do-cartucho (milho + sorgo) hoje esta percolada?
  (c) Os municipios mais "conectados" ao cinturao algodoeiro em 1979-82 perderam mais algodao depois de 1983?
Metodo: grafo de contiguidade (municipios que se tocam, malha IBGE atual, 184 nos). Densidade de hospedeiro =
area colhida / area do municipio (IBGE PAM, tabelas 1612/1613). '...' = municipio inexistente no ano -> imputado pela
media dos vizinhos (sensibilidade: imputado = 0). Aglomerado gigante = maior componente conexo de municipios com
densidade >= limiar, em % da area do estado (estilo Margosian et al. 2009; limiar de conectividade).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

mun = gpd.read_file(DADOS / "referencia" / "ceara_municipios.geojson")
mun["codarea"] = mun.codarea.astype(str)
mun = mun.sort_values("codarea").reset_index(drop=True)
area_km2 = mun.to_crs(5880).area.values / 1e6
n = len(mun)
viz = gpd.sjoin(mun[["codarea", "geometry"]], mun[["codarea", "geometry"]].rename(columns={"codarea": "c2"}),
                predicate="touches")
idx = {c: i for i, c in enumerate(mun.codarea)}
I = viz.codarea.map(idx).values
J = viz.c2.map(idx).values
A = csr_matrix((np.ones(len(I)), (I, J)), shape=(n, n))
A = ((A + A.T) > 0).astype(float)
print(f"Grafo: {n} municipios, {int(A.sum() / 2)} arestas, grau medio {A.sum(1).mean():.1f}")

p = pd.read_parquet(DADOS / "ibge_pam" / "pam_ce_municipios.parquet")
p = p[p.variavel.str.contains("colhida")].copy()
p["cod_local"] = p.cod_local.astype(str)
p["v"] = np.where(p.valor_txt.astype(str).str.strip() == "...", np.nan,
                  np.where(p.valor_txt.astype(str).str.strip() == "-", 0.0, p.valor))


def serie(produtos):
    d = p[p["produto"].isin(produtos)]
    # soma dos produtos; se todos ausentes -> NaN
    t = d.pivot_table(index="ano", columns="cod_local", values="v", aggfunc=lambda s: s.sum(min_count=1))
    return t.reindex(columns=mun.codarea)


ALG = [x for x in p["produto"].unique() if x.startswith("Algod")]
ARB = [x for x in ALG if "arb" in x]
FAW = [x for x in p["produto"].unique() if x.startswith("Milho (em") or x.startswith("Sorgo")]
print("Produtos:", ALG, FAW)
deg = np.asarray(A.sum(1)).ravel()


def imputar(vals):
    v = vals.copy()
    for _ in range(3):
        miss = np.isnan(v)
        if not miss.any():
            break
        soma = A @ np.nan_to_num(v)
        cnt = A @ (~np.isnan(v)).astype(float)
        with np.errstate(invalid="ignore", divide="ignore"):
            m = soma / cnt
        v[miss] = m[miss]
    return np.nan_to_num(v)


def gigante(dens, lim):
    occ = dens >= lim
    if occ.sum() == 0:
        return 0.0, 0
    sub = A[occ][:, occ]
    nc, lab = connected_components(sub, directed=False)
    areas = np.bincount(lab, weights=area_km2[occ])
    return 100 * areas.max() / area_km2.sum(), int(occ.sum())


def tabela(produtos, anos, rotulo):
    s = serie(produtos)
    linhas = []
    for y in anos:
        if y not in s.index:
            continue
        raw = s.loc[y].values.astype(float)
        nmiss = int(np.isnan(raw).sum())
        dens_imp = imputar(raw / 100 / area_km2) * 100  # % da area do municipio
        dens_zero = np.nan_to_num(raw) / 100 / area_km2 * 100
        lin = {"ano": y, "area_total_mil_ha": np.nansum(raw) / 1e3, "mun_ausentes": nmiss}
        for lim in (2, 5, 10):
            gi, occ = gigante(dens_imp, lim)
            gz, _ = gigante(dens_zero, lim)
            lin[f"gig_{lim}%"] = round(gi, 1)
            lin[f"gig_{lim}%_aus0"] = round(gz, 1)
            lin[f"ocup_{lim}%"] = occ
        linhas.append(lin)
    t = pd.DataFrame(linhas)
    print(f"\n{rotulo}: aglomerado gigante (% da area do CE) por limiar de densidade de hospedeiro")
    print(t.round(1).to_string(index=False))
    return s, t


anos = [1974, 1976, 1978, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1988, 1990, 1992, 1995, 2000, 2005, 2010, 2015, 2020, 2024]
s_alg, t_alg = tabela(ALG, anos, "Algodao (arboreo + herbaceo)")
s_arb, _ = tabela(ARB, [1974, 1980, 1982, 1985, 1990, 1995], "So algodao arboreo (perene)")
s_faw, t_faw = tabela(FAW, [1974, 1985, 1995, 2005, 2010, 2015, 2020, 2022, 2023, 2024], "Milho + sorgo (hospedeiros da lagarta-do-cartucho)")

# (c) conectividade 1979-82 x colapso depois de 1983
base = s_alg.loc[1979:1982]
dens_base = np.vstack([imputar(base.loc[y].values.astype(float) / 100 / area_km2) for y in base.index]).mean(0) * 100
area_base = base.mean(0, skipna=True).values
area_pos = s_alg.loc[1986:1990].mean(0, skipna=True).values
viz_dens = (A @ dens_base) / np.maximum(deg, 1)
ok = (area_base >= 500) & np.isfinite(area_pos) & base.notna().all(0).values
razao = np.log((area_pos[ok] + 1) / (area_base[ok] + 1))
rho, pv = stats.spearmanr(viz_dens[ok], razao)
rho2, pv2 = stats.spearmanr(dens_base[ok], razao)
# correlacao parcial (postos): vizinhanca controlando a densidade propria
rk = lambda x: stats.rankdata(x)
X = np.column_stack([np.ones(ok.sum()), rk(dens_base[ok])])
res_y = rk(razao) - X @ np.linalg.lstsq(X, rk(razao), rcond=None)[0]
res_x = rk(viz_dens[ok]) - X @ np.linalg.lstsq(X, rk(viz_dens[ok]), rcond=None)[0]
rp, pp = stats.pearsonr(res_x, res_y)
print(f"\n(c) {ok.sum()} municipios com >= 500 ha de algodao em 1979-82. Variacao = log(area 1986-90 / area 1979-82)")
print(f"  mediana da razao de area = {np.exp(np.median(razao)):.2f}")
print(f"  Spearman densidade dos VIZINHOS x variacao: rho = {rho:+.3f} (p = {pv:.4f})")
print(f"  Spearman densidade PROPRIA x variacao:      rho = {rho2:+.3f} (p = {pv2:.4f})")
print(f"  Parcial (vizinhos | propria): r = {rp:+.3f} (p = {pp:.4f})")

# controle de chuva: anomalia de chuva 1983-90 no municipio (celula POWER mais proxima do centroide)
ds = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")["PRECTOTCORR"].load()
ann = ds.resample(time="YS").sum()
anom = (ann.sel(time=slice("1983", "1990")).mean("time") - ann.sel(time=slice("1981", "2010")).mean("time")) / ann.sel(time=slice("1981", "2010")).mean("time")
cen = mun.to_crs(5880).centroid.to_crs(4326)
ch = np.array([float(anom.sel(lat=la, lon=lo, method="nearest")) for la, lo in zip(cen.y, cen.x)])
X2 = np.column_stack([np.ones(ok.sum()), rk(dens_base[ok]), rk(ch[ok])])
ry = rk(razao) - X2 @ np.linalg.lstsq(X2, rk(razao), rcond=None)[0]
rx = rk(viz_dens[ok]) - X2 @ np.linalg.lstsq(X2, rk(viz_dens[ok]), rcond=None)[0]
rp2, pp2 = stats.pearsonr(rx, ry)
rch, pch = stats.spearmanr(ch[ok], razao)
print(f"  Spearman anomalia de chuva 1983-90 x variacao: rho = {rch:+.3f} (p = {pch:.4f})")
print(f"  Parcial (vizinhos | propria + chuva): r = {rp2:+.3f} (p = {pp2:.4f})")
# teste de permutacao espacialmente ingenuo (embaralha valores entre municipios) para a parcial
rng = np.random.default_rng(0)
nul = [stats.pearsonr(rng.permutation(rx), ry)[0] for _ in range(2000)]
print(f"  p de permutacao (2000) da parcial: {np.mean(np.abs(nul) >= abs(rp2)):.4f}")
