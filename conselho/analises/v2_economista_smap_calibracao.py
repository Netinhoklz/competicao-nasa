"""Economista, rodada 2, analise 3: por que o percentil pronto do SMAP L4 nao dispara em 2016? E com climatologia propria?

Contexto: em v2_economista_gatilho_smap.saida.txt o gatilho pre-registrado (sm_rootzone_pctl <= 20, fev-mai) pagou em
0,5% dos municipio-anos de 2016-2025, e em 2016 (70% dos municipios com perda >= 50% da cesta) pagou em 1%.
Aqui (EXPLORATORIO, pos-hoc; nao substitui o pre-registro):
 1. Diagnostico do percentil: ciclo sazonal da media CE por mes do ano; fracao de pixels terrestres do CE com pctl <= 20
    por mes; distribuicao dos pixels em fev-mai/2016. Testa se o produto usa climatologia sazonal e se o semiarido fica
    "no meio" mesmo em seca.
 2. Climatologia propria: sm_rootzone (m3/m3) fev-mai por municipio, percentil empirico contra os OUTROS anos
    2016-2025 (9 anos) e z-score contra os outros anos. Corte <= 20 (no maximo 1 dos outros 9 anos mais seco).
    Comparado com o IMERG fev-mai < 75% do normal, nos mesmos municipio-anos e com a MESMA frequencia de pagamento
    (corte do IMERG ajustado para pagar na mesma taxa do SMAP), para comparar sinal com sinal.
Somente le arquivos. Saida: v2_economista_smap_calibracao.saida.txt
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import shapely
import xarray as xr
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
A = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
SAIDA = A / "v2_economista_smap_calibracao.saida.txt"
LINHAS = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LINHAS.append(s)


rng = np.random.default_rng(5)
ds = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
t_all = ds.time.to_index()
pos = np.where(~t_all.duplicated() & (t_all >= "2015-04-01") & (t_all <= "2026-10-31"))[0]
sub = ds[["sm_rootzone", "sm_rootzone_pctl"]].sel(lat=slice(-2.5, -8.1), lon=slice(-41.6, -37.0)).isel(time=pos)
# recorte mensal (media mensal por pixel) para o diagnostico: ~139 meses
mens = sub.resample(time="MS").mean().load()
import geopandas as gpd  # noqa: E402

ce = gpd.read_file(REF / "ceara_uf.geojson").geometry.unary_union
lo, la = np.meshgrid(mens.lon.values, mens.lat.values)
dentro = shapely.contains_xy(ce, lo, la) & np.isfinite(mens.sm_rootzone_pctl.isel(time=0).values)
out(f"pixels terrestres do CE na grade de 9 km: {dentro.sum()}")
P = mens.sm_rootzone_pctl.values[:, dentro]  # meses x pixels
W = mens.sm_rootzone.values[:, dentro]
tm = mens.time.to_index()
out(f"fracao de valores NaN no pctl mensal dos pixels do CE: {np.isnan(P).mean():.3f}; na umidade: {np.isnan(W).mean():.3f}")
df = pd.DataFrame({"mes": tm.month, "ano": tm.year, "pctl_medio": np.nanmean(P, 1), "frac_pctl_le20": np.nanmean(np.where(np.isnan(P), np.nan, P <= 20), 1),
                   "sm_rz_medio": np.nanmean(W, 1)})
out("\n1) Ciclo por mes do ano (media 2015-2026): percentil medio, fracao de pixels com pctl <= 20, umidade da raiz")
out(df.groupby("mes")[["pctl_medio", "frac_pctl_le20", "sm_rz_medio"]].mean().round(3).to_string())
out("\n   Por ano, fev-mai: percentil medio do CE, fracao de pixels <= 20 e umidade media da raiz (m3/m3)")
fm = df[df.mes.isin([2, 3, 4, 5])].groupby("ano")[["pctl_medio", "frac_pctl_le20", "sm_rz_medio"]].mean()
out(fm.round(3).to_string())
p16 = np.nanmean(P[(tm.year == 2016) & tm.month.isin([2, 3, 4, 5])], 0)
p16 = p16[np.isfinite(p16)]
out(f"   pixels CE, pctl medio fev-mai/2016: p5 {np.percentile(p16, 5):.1f}, p25 {np.percentile(p16, 25):.1f}, mediana {np.median(p16):.1f}, "
    f"p75 {np.percentile(p16, 75):.1f}; fracao <= 20: {(p16 <= 20).mean():.2f}")
out(f"   menor percentil mensal da media CE em toda a serie: {df.pctl_medio.min():.1f} ({tm[df.pctl_medio.idxmin()].strftime('%Y-%m')}); "
    f"maior: {df.pctl_medio.max():.1f} ({tm[df.pctl_medio.idxmax()].strftime('%Y-%m')})")
r = df[["pctl_medio", "sm_rz_medio"]].corr().iloc[0, 1]
out(f"   correlacao mensal pctl x umidade da raiz (CE): {r:+.2f}")

# ---------------- 2. Climatologia propria por municipio
mun = municipios_ce_gdf()
mun["cod"] = mun.codarea.astype(str)
anos_s = list(range(2016, 2026))
p2 = np.where(~t_all.duplicated() & t_all.year.isin(anos_s) & t_all.month.isin([2, 3, 4, 5]))[0]
x = ds.sm_rootzone.sel(lat=slice(-2.5, -8.1), lon=slice(-41.6, -37.0)).isel(time=p2).load()
valido = np.isfinite(x.isel(time=0).values)
lo, la = np.meshgrid(x.lon.values, x.lat.values)
F = x.values.reshape(x.shape[0], -1)
cols = {}
for _, rr in mun.iterrows():
    m = shapely.contains_xy(rr.geometry, lo, la) & valido
    if m.sum() == 0:
        c = rr.geometry.centroid
        dist = (lo - c.x) ** 2 + (la - c.y) ** 2
        dist[~valido] = np.inf
        m = np.zeros_like(valido); m.flat[np.argmin(dist)] = True
    cols[rr.cod] = np.nanmean(F[:, m.ravel()], axis=1)
S = pd.DataFrame(cols, index=t_all[p2])
Sw = pd.DataFrame({a: S.loc[f"{a}-02-01":f"{a}-05-31"].mean() for a in anos_s}).T.astype(float)
Sp = Sw * np.nan
Sz = Sw * np.nan
for a in anos_s:
    o = Sw.drop(index=a)
    Sp.loc[a] = 100 * o.lt(Sw.loc[a], axis=1).sum() / len(o)
    Sz.loc[a] = (Sw.loc[a] - o.mean()) / o.std()

ch = pd.read_parquet(A / "estrategista_cache_chuva_mun_diaria.parquet")
ch.columns = ch.columns.astype(str)
anos_i = list(range(1998, 2026))
ac = pd.DataFrame({a: ch.loc[f"{a}-02-01":f"{a}-05-31"].sum() for a in anos_i}).T
pn = ac * np.nan
for a in anos_i:
    pn.loc[a] = ac.loc[a] / ac.drop(index=a).median()

pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.ano.between(1998, 2025)].copy()
pam["cod"] = pam.cod_local.astype(str)


def loo_med(v):
    return np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])


CESTA = ["Milho (em", "Feij", "Mandioca", "Arroz (em", "Algodão herbáceo"]
dc = pam[pam.produto.str.startswith(tuple(CESTA))].copy()
rec = dc[dc.ano.between(2019, 2025)]
preco = rec.groupby("produto").valor_mil_moeda.sum() / rec.groupby("produto").producao_t.sum()
dc["v"] = dc.producao_t * dc.produto.map(preco)
V = dc.groupby(["cod", "ano"]).v.sum().reset_index().sort_values(["cod", "ano"])
V = V[V.v > 0]
V["ref"] = V.groupby("cod").v.transform(lambda s: pd.Series(loo_med(s.values), index=s.index))
V["razao"] = V.v / V.ref
L2 = V.dropna(subset=["razao"]).set_index(["cod", "ano"]).razao
q = pam[pam.produto.str.startswith("Milho (em") & (pam.area_plantada_ha >= 50)]
q = q.groupby(["cod", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum().sort_values(["cod", "ano"])
q["r"] = q.producao_t / q.area_plantada_ha
q["ref"] = q.groupby("cod").r.transform(lambda s: pd.Series(loo_med(s.values), index=s.index))
L1 = (q.r / q.ref).set_axis(pd.MultiIndex.from_frame(q[["cod", "ano"]])).dropna()


def longo(df_, nome):
    s = df_.stack()
    s.index.names = ["ano", "cod"]
    return s.swaplevel().rename(nome)


def placar(score, gat, y, rot):
    D = pd.concat([score.rename("s"), gat.rename("g"), y.rename("y")], axis=1).dropna()
    D["g"] = D.g.astype(bool); D["y"] = D.y.astype(bool)
    an = D.index.get_level_values("ano").values
    ua = np.unique(an)
    grp = {a: np.where(an == a)[0] for a in ua}
    yy, gg = D.y.values, D.g.values
    bh, bp = [], []
    for _ in range(1000):
        ix = np.concatenate([grp[a] for a in rng.choice(ua, len(ua))])
        if yy[ix].any(): bh.append(gg[ix][yy[ix]].mean())
        if gg[ix].any(): bp.append(yy[ix][gg[ix]].mean())
    dentro_ = [roc_auc_score(yy[grp[a]], D.s.values[grp[a]]) for a in ua if 0.1 <= yy[grp[a]].mean() <= 0.9]
    out(f"  {rot:46s} paga {100 * gg.mean():4.1f}% | perdas pagas {100 * gg[yy].mean():4.1f}% [{100 * np.percentile(bh, 5):.0f}-{100 * np.percentile(bh, 95):.0f}]"
        f" | pagamentos sem perda {100 * (1 - yy[gg].mean()):4.1f}% [{100 * (1 - np.percentile(bp, 95)):.0f}-{100 * (1 - np.percentile(bp, 5)):.0f}]"
        f" | AUC {roc_auc_score(yy, D.s):.2f} | dentro do ano {np.mean(dentro_):.2f}")
    return D


out("\n2) EXPLORATORIO: SMAP L4 com climatologia propria (2016-2025), fev-mai")
sp, sz = longo(Sp, "sp"), longo(Sz, "sz")
im = longo(pn.loc[anos_s], "pn")
for rot_l, lab, lim in [("L1 quebra canonica do milho", L1, 0.5), ("L2 cesta tipo GS, perda >= 50%", L2, 0.5)]:
    y = lab < lim
    y = y[y.index.get_level_values("ano").isin(anos_s)]
    out(f" -- {rot_l} (perda em {100 * y.mean():.1f}% dos municipio-anos) --")
    Ds = placar(-sp, sp <= 20, y, "SMAP rz, percentil proprio <= 20")
    placar(-sz, sz <= -0.84, y, "SMAP rz, z proprio <= -0,84")
    taxa = Ds.g.mean()
    corte = im.loc[Ds.index].quantile(taxa)
    placar(-im, im <= corte, y, f"IMERG mesma taxa de pagamento (<= {corte:.2f})")
    placar(-im, im < 0.75, y, "IMERG < 75% normal (canonico)")
    if rot_l.startswith("L2"):
        Dx = pd.concat([sp.rename("sp"), im.rename("pn"), y.rename("y")], axis=1).dropna()
        tb = Dx.assign(gs=Dx.sp <= 20, gi=Dx.pn < 0.75).groupby(level="ano")[["y", "gs", "gi"]].mean().round(2)
        tb.columns = ["fracao_em_perda", "SMAP_proprio", "IMERG_canonico"]
        out(tb.to_string())

SAIDA.write_text("\n".join(LINHAS), encoding="utf-8")
