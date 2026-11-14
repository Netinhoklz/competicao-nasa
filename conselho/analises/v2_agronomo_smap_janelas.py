"""Agronomo (rodada 2) - janelas de plantio de milho, caupi, sorgo e mandioca pela zona da raiz do SMAP L4,
comparadas com o balde FAO-56 da rodada 1 nos MESMOS anos, e a agua da entressafra para a S3.

Pre-declarado (nada ajustado olhando o PAM):
 - umidade relativa W = (zona da raiz - p2) / (p98 - p2) do proprio municipio (SMAP L4, 01/04/2015-10/11/2026);
 - sucesso de uma semeadura = W medio na janela sensivel >= 1 - p (p da FAO-56 usado no balde da rodada 1):
     milho floracao +50 a +85 d, p 0,55 -> W >= 0,45; caupi +35 a +60 d, p 0,45 -> W >= 0,55;
     sorgo +50 a +90 d, p 0,55 -> W >= 0,45; mandioca estabelecimento 0 a +60 d, W >= 0,50 (heuristica, grau C);
 - data-limite = ultimo decendio com P(sucesso) >= 0,7 nas quadras 2016-2026 (mesma regra do ZARC sintetico);
 - sensibilidade: limiar de W +-0,1 (mostrada, nao escolhida);
 - balde da rodada 1 (agronomo_isna_zarc_sintetico.py) recalculado SO em 2016-2026 para a comparacao pareada.
Validacao entre municipios (2016-2025): risco de 21/jan de cada metodo x frequencia real de quebra canonica.
S3: dias por ano com W >= 0,5; entressafra (ago-dez) no piso; camada 1-2 m do GLDAS-2.1 Noah (agua abaixo do SMAP).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import json
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import xarray as xr
from scipy import stats

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
QX = "2311306"
nomes = {str(x["id"]): x["nome"] for x in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}
EX = {n: c for c, n in nomes.items() if n in ("Quixadá", "Crato", "Tianguá", "Tauá", "Iguatu", "Sobral", "Itapipoca")}

RZ = pd.read_parquet(OUT / "v2_agronomo_smap_mun_sm_rootzone.parquet")
print(f"datas duplicadas no SMAP L4 (dois granulos no mesmo dia): {RZ.index.duplicated().sum()} -> fica o primeiro")
RZ = RZ[~RZ.index.duplicated()]
cods = list(RZ.columns)
base = RZ.loc["2015-04-01":]
p2, p98 = base.quantile(0.02), base.quantile(0.98)
W = ((RZ - p2) / (p98 - p2)).clip(0, 1)
SEAS = list(range(2016, 2027))
ND = 300
Wa = np.stack([W.reindex(pd.date_range(f"{a}-01-01", periods=ND, freq="D")).values.T for a in SEAS], 1)  # mun x ano x dia
print(f"W: {Wa.shape} (municipios x quadras 2016-2026 x dias desde 1/jan); faltas {np.isnan(Wa).mean():.2%}")

DEC = {"01/jan": 0, "11/jan": 10, "21/jan": 20, "01/fev": 31, "11/fev": 41, "21/fev": 51, "01/mar": 59, "11/mar": 69,
       "21/mar": 79, "01/abr": 90, "11/abr": 100, "21/abr": 110, "01/mai": 120, "11/mai": 130}
CROPS = {"milho": (50, 85, 0.45), "caupi": (35, 60, 0.55), "sorgo": (50, 90, 0.45), "mandioca": (0, 60, 0.50)}


def p_smap(c, d0, dthr=0.0):
    a, b, thr = CROPS[c]
    m = np.nanmean(Wa[:, :, d0 + a:d0 + b + 1], axis=2)
    return (m >= thr + dthr).mean(1)  # por municipio


def data_limite(serie, alvo=0.7):
    oks = [d for d in serie.index if serie[d] >= alvo]
    return oks[-1] if oks else "nenhum"


PS = {s: pd.DataFrame({(c, d): p_smap(c, dd, s) for c in CROPS for d, dd in DEC.items()}, index=cods) for s in (-0.1, 0.0, 0.1)}
DL_S = {s: pd.DataFrame({c: [data_limite(PS[s].loc[m, c]) for m in cods] for c in CROPS}, index=cods) for s in PS}

# ------------------------------------------------------------------ balde FAO-56 da rodada 1, so 2016-2026
chuva = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["pt"] = mun.geometry.representative_point()
mun = mun.set_index("codarea").loc[cods]
e0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"].load()
et0 = pd.DataFrame({c: e0.sel(lat=mun.loc[c, "pt"].y, lon=mun.loc[c, "pt"].x, method="nearest").to_series() for c in cods})
R = np.zeros((len(cods), len(SEAS), ND), np.float32); E = np.zeros_like(R)
for j, a in enumerate(SEAS):
    idx = pd.date_range(f"{a}-01-01", periods=ND, freq="D")
    R[:, j, :] = chuva.reindex(idx)[cods].fillna(0).values.T
    E[:, j, :] = et0.reindex(idx)[cods].interpolate().bfill().values.T
fim_chuva = chuva.index[-1]
print(f"chuva IMERG municipal ate {fim_chuva.date()} (a quadra de 2026 entra completa ate a floracao de 21/abr + 85 d)")
CULT = {"milho": (20, 30, 35, 25, 0.30, 1.20, 0.35, 0.6, 0.55), "caupi": (15, 20, 25, 15, 0.40, 1.05, 0.35, 0.5, 0.45),
        "sorgo": (20, 30, 40, 25, 0.30, 1.05, 0.55, 0.8, 0.55)}
AWC = 100.0


def kc_curve(c):
    li, ld, lm, ll, ki, km, ke, _, _ = CULT[c]
    k = np.concatenate([np.full(li, ki), np.linspace(ki, km, ld), np.full(lm, km), np.linspace(km, ke, ll)])
    mid = np.zeros(len(k), bool); mid[li + ld:li + ld + lm] = True
    return k.astype(np.float32), mid


def simular(c, sow):
    kc, mid = kc_curve(c); L = len(kc); taw = AWC * CULT[c][7]; raw = CULT[c][8] * taw
    Dr = np.full(sow.shape, taw, np.float32); eta_m = np.zeros(sow.shape, np.float32); etc_m = np.zeros_like(eta_m)
    for d in range(ND):
        k = d - sow; P = R[:, :, d]; e = E[:, :, d]
        dentro = (k >= 0) & (k < L)
        kci = np.where(dentro, kc[np.clip(k, 0, L - 1)], 0.0)
        ks = np.where(Dr <= raw, 1.0, np.clip((taw - Dr) / (taw - raw), 0, 1))
        kbare = 0.3 * np.clip((taw - Dr) / taw, 0, 1)
        etc = kci * e; eta = np.where(dentro, ks * etc, kbare * e)
        Dr = np.clip(Dr - P + eta, 0, taw)
        ism = dentro & mid[np.clip(k, 0, L - 1)]
        eta_m += np.where(ism, eta, 0); etc_m += np.where(ism, etc, 0)
    return eta_m / np.maximum(etc_m, 1e-6)


DECB = {k: v for k, v in DEC.items() if v <= 110}
PB = pd.DataFrame({(c, d): (simular(c, np.full((len(cods), len(SEAS)), dd)) >= 0.5).mean(1) for c in CULT for d, dd in DECB.items()},
                  index=cods)
DL_B = pd.DataFrame({c: [data_limite(PB.loc[m, c]) for m in cods] for c in CULT}, index=cods)
PB28 = pd.read_parquet(OUT / "agronomo_zarc_sintetico_prob.parquet")
PB28.columns = pd.MultiIndex.from_tuples([tuple(c.split("|")) for c in PB28.columns])
DL_B28 = pd.DataFrame({c: [data_limite(PB28.loc[m, c]) for m in cods] for c in CULT}, index=cods)

# ------------------------------------------------------------------ comparacao
ordem = list(DEC)
pos = {d: i for i, d in enumerate(ordem)}
print("\n=== A. P(sucesso) mediana estadual por decendio de semeadura (quadras 2016-2026) ===")
T = pd.DataFrame({f"{c} SMAP": PS[0.0][c].median() for c in CROPS})
for c in CULT:
    T[f"{c} balde"] = PB[c].median()
print(T.round(2).to_string())

print("\n=== B. Data-limite (ultimo decendio com P >= 0,7): SMAP x balde nos mesmos anos x balde 1998-2025 ===")
for c in CROPS:
    vs = DL_S[0.0][c].value_counts().reindex(ordem + ["nenhum"]).fillna(0).astype(int)
    print(f"  {c} SMAP: " + ", ".join(f"{k} {v}" for k, v in vs.items() if v))
    if c in CULT:
        vb = DL_B[c].value_counts().reindex(ordem + ["nenhum"]).fillna(0).astype(int)
        print(f"  {c} balde 2016-26: " + ", ".join(f"{k} {v}" for k, v in vb.items() if v))
        ok = (DL_S[0.0][c] != "nenhum") & (DL_B[c] != "nenhum")
        dif = np.array([pos[a] - pos[b] for a, b in zip(DL_S[0.0][c][ok], DL_B[c][ok])])
        print(f"     SMAP - balde (decendios), {ok.sum()} municipios com as duas datas: mediana {np.median(dif):+.0f}; "
              f"|dif| <= 1 em {(np.abs(dif) <= 1).mean():.0%}; SMAP mais tarde em {(dif > 1).mean():.0%}, mais cedo em {(dif < -1).mean():.0%}")
    for s in (-0.1, 0.1):
        vv = DL_S[s][c]
        ok2 = (vv != "nenhum") & (DL_S[0.0][c] != "nenhum")
        dd = np.array([pos[a] - pos[b] for a, b in zip(vv[ok2], DL_S[0.0][c][ok2])])
        print(f"     sensibilidade limiar {s:+.1f}: data-limite anda mediana {np.median(dd) if len(dd) else np.nan:+.0f} decendios; "
              f"'nenhum' em {(vv == 'nenhum').mean():.0%}")
print("\n  Municipios de exemplo (SMAP | balde 2016-26 | balde 1998-2025):")
for n, c in EX.items():
    print(f"   {n:10s}: " + "; ".join(
        f"{cc} {DL_S[0.0].at[c, cc]}" + (f" | {DL_B.at[c, cc]} | {DL_B28.at[c, cc]}" if cc in CULT else "") for cc in CROPS))

# ------------------------------------------------------------------ C. validacao entre municipios
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")


def serie(prefixo):
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        return pd.Series([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref; p["quebra"] = p.razao < 0.5; p["cod"] = p.cod_local.astype(str)
    return p.dropna(subset=["razao"])


print("\n=== C. Os riscos de cada metodo ordenam os municipios como a quebra real de 2016-2025? (Spearman entre municipios) ===")
for cult, cc in [("milho", "milho"), ("feijao", "caupi")]:
    q = serie("Milho (em gr" if cult == "milho" else "Feij")
    G = q[q.ano.between(2016, 2025)].groupby("cod").agg(fq=("quebra", "mean"), n=("quebra", "size"))
    G = G[G.n >= 8]
    for d in ["21/jan", "11/fev"]:
        rs = stats.spearmanr(1 - PS[0.0].loc[G.index, (cc, d)], G.fq)
        rb = stats.spearmanr(1 - PB.loc[G.index, (cc, d)], G.fq)
        rbs = stats.spearmanr(PS[0.0].loc[G.index, (cc, d)], PB.loc[G.index, (cc, d)])
        print(f"  {cult} ({len(G)} mun.), semeadura {d}: rho SMAP {rs[0]:+.2f} (p {rs[1]:.3f}) | rho balde {rb[0]:+.2f} "
              f"(p {rb[1]:.3f}) | SMAP x balde {rbs[0]:+.2f}")
    # o balde de 28 anos (o que a proposta usa) contra a mesma quebra 2016-2025
    rb28 = stats.spearmanr(1 - PB28.loc[G.index, (cc, "21/jan")], G.fq)
    print(f"  {cult}: balde 1998-2025 (o da proposta), 21/jan, contra a quebra 2016-2025: rho {rb28[0]:+.2f} (p {rb28[1]:.3f})")

# ------------------------------------------------------------------ D. agua para a S3 (leguminosa que fica)
print("\n=== D. Agua na zona da raiz ao longo do ano (SMAP L4, quadras 2016-2025) ===")
Wd = W.loc["2016-01-01":"2025-12-31"]
dias_uteis = (Wd >= 0.5).groupby(Wd.index.year).sum()  # ano x mun


def maior_corrida(b):
    mx = run = 0
    for x in b:
        run = run + 1 if x else 0
        mx = max(mx, run)
    return mx


corr = pd.DataFrame({a: [maior_corrida((g[c] >= 0.5).values) for c in cods] for a, g in Wd.groupby(Wd.index.year)}, index=cods).T
ent = Wd[(Wd.index.month >= 8)]
piso = (ent < 0.1).groupby(ent.index.year).mean()
print(f"  dias por ano com W >= 0,5: mediana dos municipios {dias_uteis.median().median():.0f} "
      f"(p10-p90 dos municipio-anos {np.nanpercentile(dias_uteis.values, 10):.0f}-{np.nanpercentile(dias_uteis.values, 90):.0f}); "
      f"Quixada {dias_uteis[QX].median():.0f} ({dias_uteis[QX].min():.0f} a {dias_uteis[QX].max():.0f})")
print(f"  maior corrida continua com W >= 0,5: mediana {corr.median().median():.0f} d; Quixada mediana {corr[QX].median():.0f} d "
      f"(por ano: {dict(zip(corr.index, corr[QX].astype(int)))})")
for cic, nome in [(75, "caupi 75 d"), (110, "milho 110 d"), (60, "estabelecimento da maniva 60 d")]:
    print(f"   fracao de municipio-anos em que a maior corrida umida cobre {nome}: {(corr.values >= cic).mean():.0%}; "
          f"Quixada {(corr[QX] >= cic).mean():.0%}")
print(f"  entressafra (ago-dez): fracao dos dias com W < 0,1 (piso): mediana {piso.median().median():.0%}; Quixada {piso[QX].median():.0%}")
print(f"  dias com W >= 0,5 em ago-dez: mediana {((ent >= 0.5).groupby(ent.index.year).sum()).median().median():.0f} por ano")

g = xr.open_dataset(DADOS / "gldas" / "gldas_noah025_mensal_ne.nc")
g = g[["SoilMoi0_10cm_inst", "SoilMoi10_40cm_inst", "SoilMoi40_100cm_inst", "SoilMoi100_200cm_inst"]].sel(
    lat=slice(-7.9, -2.7), lon=slice(-41.5, -37.2)).load()
ce = gpd.read_file(REF / "ceara_uf.geojson").geometry.union_all()
lo, la = np.meshgrid(g.lon.values, g.lat.values)
mk = xr.DataArray(shapely.contains_xy(ce, lo, la), dims=("lat", "lon"), coords={"lat": g.lat, "lon": g.lon})
gc = g.where(mk).mean(("lat", "lon")).to_dataframe().loc["2000":"2025"]
gc.columns = ["0-10", "10-40", "40-100", "100-200"]
clim = gc.groupby(gc.index.month).mean()
print("\n  GLDAS-2.1 Noah, media do CE 2000-2025 (kg/m2 = mm por camada), climatologia mensal:")
print(clim.round(1).T.to_string())
mn = gc.groupby(gc.index.year).min()
print("  amplitude do ciclo medio (max - min do mes medio): " +
      ", ".join(f"{c} cm {clim[c].max() - clim[c].min():.1f} mm" for c in clim.columns))
print("  agua em dez acima do minimo do registro, por camada (mediana 2000-2025): " +
      ", ".join(f"{c} {(gc[gc.index.month == 12][c] - gc[c].min()).median():.1f} mm" for c in gc.columns))
dz = {"0-10": 100, "10-40": 300, "40-100": 600, "100-200": 1000}
print("  em m3/m3 (camada / espessura): dez mediano " +
      ", ".join(f"{c} {gc[gc.index.month == 12][c].median() / dz[c]:.3f}" for c in gc.columns) +
      " | abr mediano " + ", ".join(f"{c} {gc[gc.index.month == 4][c].median() / dz[c]:.3f}" for c in gc.columns))
r = stats.spearmanr(gc[gc.index.month == 12]["100-200"].values,
                    gc[gc.index.month == 4]["100-200"].values)
print(f"  a camada 1-2 m em dez acompanha a de abr do mesmo ano? rho {r[0]:+.2f} (n {len(gc) // 12} anos)")

# ------------------------------------------------------------------ E. conferencias do bloco B/C
print("\n=== E. Conferencias ===")
wq = W[QX].loc["2016":"2025"]
print("  Quixada, W mediano por mes (2016-2025): " + ", ".join(f"{m}: {v:.2f}" for m, v in wq.groupby(wq.index.month).median().items()))
rq = RZ[QX].loc["2016":"2025"]
print(f"  Quixada, zona da raiz p2 {p2[QX]:.3f} / p98 {p98[QX]:.3f} m3/m3; mediana por mes: " +
      ", ".join(f"{m}: {v:.3f}" for m, v in rq.groupby(rq.index.month).median().items()))
# versao com umidade ABSOLUTA (m3/m3) na floracao do milho semeado em 21/jan (relatada ao lado; nao substitui o bloco C)
Ra = np.stack([RZ.reindex(pd.date_range(f"{a}-01-01", periods=ND, freq="D")).values.T for a in SEAS], 1)
absm = np.nanmean(Ra[:, :10, 20 + 50:20 + 86], axis=(1, 2))  # 2016-2025
q = serie("Milho (em gr")
G = q[q.ano.between(2016, 2025)].groupby("cod").agg(fq=("quebra", "mean"), n=("quebra", "size"))
G = G[G.n >= 8]
s_abs = pd.Series(absm, index=cods).loc[G.index]
r = stats.spearmanr(-s_abs, G.fq)
print(f"  milho: umidade ABSOLUTA media da zona da raiz na floracao (semeadura 21/jan) x quebra 2016-2025: rho {r[0]:+.2f} "
      f"(p {r[1]:.3f}); x risco do balde 28 anos: rho {stats.spearmanr(-s_abs, 1 - PB28.loc[G.index, ('milho', '21/jan')])[0]:+.2f}")

# ------------------------------------------------------------------ F. a troca de Sao Jose nos anos de luz acesa
print("\n=== F. Troca em Sao Jose: fracao de municipios em que a semeadura de 11/mar ou 21/mar teria agua, por quadra ===")
print("    SMAP = W medio na janela sensivel >= limiar; balde = ISNA floracao >= 0,5. Anos de luz acesa em 2016-2025: 2016, 2017, 2021, 2025")
for c, d in [("caupi", "11/mar"), ("caupi", "21/mar"), ("sorgo", "11/mar"), ("milho", "01/mar")]:
    a_, b_, thr = CROPS[c]; d0 = DEC[d]
    ok_s = np.nanmean(Wa[:, :, d0 + a_:d0 + b_ + 1], axis=2) >= thr          # mun x ano
    ok_b = simular(c, np.full((len(cods), len(SEAS)), d0)) >= 0.5
    txt = []
    for a in [2016, 2017, 2021, 2025]:
        j = SEAS.index(a)
        txt.append(f"{a}: SMAP {ok_s[:, j].mean():.0%} / balde {ok_b[:, j].mean():.0%} (Quixada {'sim' if ok_s[cods.index(QX), j] else 'nao'}/"
                   f"{'sim' if ok_b[cods.index(QX), j] else 'nao'})")
    outros = [SEAS.index(a) for a in SEAS if a not in (2016, 2017, 2021, 2025, 2026)]
    txt.append(f"demais 2018-2024: SMAP {ok_s[:, outros].mean():.0%} / balde {ok_b[:, outros].mean():.0%}")
    print(f"  {c} {d}: " + "; ".join(txt))
