"""Economista, rodada 2, analise 2: gatilho parametrico tipo Garantia-Safra com o percentil do SMAP L4 contra a quebra do IBGE.

PRE-REGISTRO (escrito antes de rodar; nenhum corte e escolhido olhando o teste):
- Gatilho SMAP: media municipal do sm_rootzone_pctl (percentil climatologico que vem no proprio produto SPL4SMGP v008,
  granulo das 13:30 UTC) <= 20, em duas janelas: 1/fev-30/abr (portao de 30/abr da QUADRA) e 1/fev-31/mai (fim da quadra).
  Anos 2016-2025 (n = 10 anos; 2015 fica fora porque o SMAP comeca em 31/mar/2015).
- Comparacao com o mesmo corte de sempre da chuva: IMERG acumulado < 75% do normal (mediana dos OUTROS anos 1998-2025),
  janelas 1/jan-30/abr (regra canonica da QUADRA) e 1/fev-31/mai. Mesmos municipio-anos.
- Rotulos do IBGE (PAM): (L1) quebra canonica do milho: producao/area plantada < 50% da mediana dos outros anos;
  (L2) perda tipo Garantia-Safra: valor a preco constante (precos medios 2019-2025) da cesta milho+feijao+mandioca+arroz+
  algodao herbaceo < 50% da mediana dos outros anos; sensibilidade com perda >= 40% (razao < 0,6), porque o limiar legal
  nao foi conferido (PROPOSTA_FINAL.md, 9.5 item 9).
- Metricas: taxa de acerto (perdas pagas), falsos positivos (pagamentos sem perda), risco de base nos dois sentidos,
  AUC geral e dentro do ano, IC90 por bootstrap de ANOS. Placar por ano (fracao de municipios em perda x gatilhados).
- Extensao para n maior: GLDAS-2.2 CLSM (o mesmo modelo Catchment que esta por tras do SMAP L4; ASSIMILA o GRACE),
  umidade da zona de raiz 1/fev-31/mai, percentil empirico do municipio contra os OUTROS anos 2003-2025, corte <= 20.
  n = 23 anos. Comparado com a chuva IMERG nos mesmos anos.
O SMAP L3 (retrieval do satelite, sem modelo) ainda nao foi consolidado (smap_l3_diario_ne.nc nao existe); fica para depois.
Somente le arquivos. Saida: v2_economista_gatilho_smap.saida.txt
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
from scipy import stats
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
A = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
SAIDA = A / "v2_economista_gatilho_smap.saida.txt"
LINHAS = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LINHAS.append(s)


rng = np.random.default_rng(11)
mun = municipios_ce_gdf()
mun["cod"] = mun.codarea.astype(str)


def mascaras(lat, lon, valido):
    lo, la = np.meshgrid(lon, lat)
    res = {}
    for _, r in mun.iterrows():
        m = shapely.contains_xy(r.geometry, lo, la) & valido
        if m.sum() == 0:
            c = r.geometry.centroid
            dist = (lo - c.x) ** 2 + (la - c.y) ** 2
            dist[~valido] = np.inf
            m = np.zeros_like(valido)
            m.flat[np.argmin(dist)] = True
        res[r.cod] = m.ravel()
    return res


def media_municipal(arr, masks):
    """arr (T, lat, lon) -> DataFrame T x municipio."""
    F = arr.reshape(arr.shape[0], -1)
    return pd.DataFrame({c: np.nanmean(F[:, m], axis=1) for c, m in masks.items()})


# ---------------- 1. SMAP L4: percentil da zona de raiz por municipio e janela
ds = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
anos_s = list(range(2016, 2026))
t_all = ds.time.to_index()
out(f"SMAP L4: {len(t_all)} granulos, {t_all.duplicated().sum()} datas repetidas (fica o 1o granulo de cada dia)")
pos = np.where((~t_all.duplicated()) & t_all.year.isin(anos_s) & t_all.month.isin([2, 3, 4, 5]))[0]
tsel = t_all[pos]
x = ds.sm_rootzone_pctl.sel(lat=slice(-2.5, -8.1), lon=slice(-41.6, -37.0)).isel(time=pos).load()
mk = mascaras(x.lat.values, x.lon.values, np.isfinite(x.isel(time=0).values))
npix = pd.Series({c: m.sum() for c, m in mk.items()})
out(f"SMAP L4 recorte CE: {x.shape}; pixels de 9 km por municipio: mediana {npix.median():.0f}, minimo {npix.min()}; dias carregados {len(tsel)}")
S = media_municipal(x.values, mk)
S.index = tsel
JAN = {"30abr": ("02-01", "04-30"), "31mai": ("02-01", "05-31")}
smap = {k: pd.DataFrame({a: S.loc[f"{a}-{i}":f"{a}-{f}"].mean() for a in anos_s}).T for k, (i, f) in JAN.items()}  # ano x mun

# ---------------- 2. IMERG: % do normal (mediana dos outros anos 1998-2025)
ch = pd.read_parquet(A / "estrategista_cache_chuva_mun_diaria.parquet")
ch.columns = ch.columns.astype(str)
anos_i = list(range(1998, 2026))


def pct_normal(i, f):
    ac = pd.DataFrame({a: ch.loc[f"{a}-{i}":f"{a}-{f}"].sum() for a in anos_i}).T
    o = ac * np.nan
    for a in anos_i:
        o.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return o


imerg = {"30abr": pct_normal("01-01", "04-30"), "31mai": pct_normal("02-01", "05-31")}

# ---------------- 3. Rotulos do IBGE
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.ano.between(1998, 2025)].copy()
pam["cod"] = pam.cod_local.astype(str)


def loo_med(v):
    return np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])


q = pam[pam.produto.str.startswith("Milho (em") & (pam.area_plantada_ha >= 50)]
q = q.groupby(["cod", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum().sort_values(["cod", "ano"])
q["r"] = q.producao_t / q.area_plantada_ha
q["ref"] = q.groupby("cod").r.transform(lambda s: pd.Series(loo_med(s.values), index=s.index))
q["razao"] = q.r / q.ref
L1 = q.dropna(subset=["razao"]).set_index(["cod", "ano"]).razao

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
out(f"Rotulos: milho canonico {len(L1)} municipio-anos (quebra {100 * (L1 < .5).mean():.1f}%); "
    f"cesta tipo Garantia-Safra {len(L2)} (perda >= 50%: {100 * (L2 < .5).mean():.1f}%; >= 40%: {100 * (L2 < .6).mean():.1f}%)")


def longo(df, nome):
    s = df.stack()
    s.index.names = ["ano", "cod"]
    return s.swaplevel().rename(nome)


def avalia(score, gat, perda, rot, boot=1000):
    """score: maior = pior; gat: bool; perda: bool. Index (cod, ano)."""
    D = pd.concat([score.rename("s"), gat.rename("g"), perda.rename("y")], axis=1).dropna()
    D["g"] = D.g.astype(bool); D["y"] = D.y.astype(bool)
    anos = D.index.get_level_values("ano").values
    y, g, s = D.y.values, D.g.values, D.s.values
    hit = g[y].mean(); prec = y[g].mean() if g.any() else np.nan
    ua = np.unique(anos)
    grp = {a: np.where(anos == a)[0] for a in ua}
    bh, bp = [], []
    for _ in range(boot):
        ix = np.concatenate([grp[a] for a in rng.choice(ua, len(ua))])
        yy, gg = y[ix], g[ix]
        if yy.any():
            bh.append(gg[yy].mean())
        if gg.any():
            bp.append(yy[gg].mean())
    try:
        auc = roc_auc_score(y, s)
    except ValueError:
        auc = np.nan
    dentro = [roc_auc_score(y[grp[a]], s[grp[a]]) for a in ua if 0.1 <= y[grp[a]].mean() <= 0.9]
    out(f"  {rot:44s} n={len(D):4d} ({len(ua)} anos) perda {100 * y.mean():4.1f}% | paga {100 * g.mean():4.1f}% | "
        f"perdas pagas {100 * hit:4.1f}% [{100 * np.percentile(bh, 5):.0f}-{100 * np.percentile(bh, 95):.0f}] | "
        f"pagamentos sem perda {100 * (1 - prec):4.1f}% [{100 * (1 - np.percentile(bp, 95)):.0f}-{100 * (1 - np.percentile(bp, 5)):.0f}] | "
        f"AUC {auc:.2f} | AUC dentro do ano {np.mean(dentro) if dentro else np.nan:.2f} ({len(dentro)} anos)")
    return D


# ---------------- 4. Avaliacao no periodo SMAP (2016-2025)
res = {}
for rot_l, lab, lim in [("L1 quebra canonica do milho", L1, 0.5), ("L2 cesta tipo GS, perda >= 50%", L2, 0.5),
                        ("L2' cesta tipo GS, perda >= 40%", L2, 0.6)]:
    out(f"\n== {rot_l} | 2016-2025 ==")
    y = (lab < lim)
    y = y[y.index.get_level_values("ano").isin(anos_s)]
    for jan in ["30abr", "31mai"]:
        sp = longo(smap[jan], "pctl")
        im = longo(imerg[jan].loc[anos_s], "pn")
        res[(rot_l, "smap", jan)] = avalia(-sp, sp <= 20, y, f"SMAP L4 pctl <= 20, fev-{jan[2:]}")
        res[(rot_l, "imerg", jan)] = avalia(-im, im < 0.75, y, f"IMERG < 75% normal, {'jan' if jan == '30abr' else 'fev'}-{jan[2:]}")

# ---------------- 5. Placar por ano (L2, perda >= 50%; janela 31/mai)
out("\n== Placar por ano: cesta tipo GS (perda >= 50%), janela fev-mai ==")
Ds = res[("L2 cesta tipo GS, perda >= 50%", "smap", "31mai")]
Di = res[("L2 cesta tipo GS, perda >= 50%", "imerg", "31mai")]
tab = pd.DataFrame({"fracao_em_perda": Ds.groupby("ano").y.mean(), "fracao_SMAP": Ds.groupby("ano").g.mean(),
                    "fracao_IMERG": Di.groupby("ano").g.mean(),
                    "fracao_IMERG_jan_abr": res[("L2 cesta tipo GS, perda >= 50%", "imerg", "30abr")].groupby("ano").g.mean(),
                    "pctl_SMAP_mediano": longo(smap["31mai"], "p").groupby("ano").median()})
out(tab.round(2).to_string())
for c in ["fracao_SMAP", "fracao_IMERG"]:
    r = stats.spearmanr(tab[c], tab.fracao_em_perda)
    out(f"  Spearman entre anos ({c} x fracao em perda): rho = {r.correlation:+.2f}, p = {r.pvalue:.3f}, n = {len(tab)} anos")
ruins = tab.fracao_em_perda >= 0.30
for c in ["fracao_SMAP", "fracao_IMERG"]:
    disp = tab[c] >= 0.30
    out(f"  anos ruins (>= 30% dos municipios em perda): {list(tab.index[ruins])}; o gatilho {c[7:]} 'disparou no estado' "
        f"(>= 30% gatilhados) em {list(tab.index[disp])} -> acertou {int((disp & ruins).sum())} de {int(ruins.sum())}, "
        f"alarme falso em {int((disp & ~ruins).sum())} de {int((~ruins).sum())}")

# ---------------- 6. Extensao com o GLDAS-2.2 CLSM (2003-2025, n = 23 anos)
out("\n== Extensao: GLDAS-2.2 CLSM zona de raiz fev-mai, percentil empirico contra os outros anos (2003-2025) ==")
g = xr.open_dataset(DADOS / "gldas" / "gldas_clsm025_diario_ne.nc")
anos_g = list(range(2003, 2026))
tg = g.time.to_index()
tg = tg[tg.year.isin(anos_g) & tg.month.isin([2, 3, 4, 5])]
z = g.SoilMoist_RZ_tavg.sel(lat=slice(-8.1, -2.5), lon=slice(-41.6, -37.0)).sel(time=tg).load()
zv = z.values.astype(float)
zv[zv < -9000] = np.nan
mkg = mascaras(z.lat.values, z.lon.values, np.isfinite(zv[0]))
Z = media_municipal(zv, mkg)
Z.index = tg
Zw = pd.DataFrame({a: Z.loc[f"{a}-02-01":f"{a}-05-31"].mean() for a in anos_g}).T
Zp = Zw * np.nan
for a in anos_g:
    oth = Zw.drop(index=a)
    Zp.loc[a] = 100 * (oth.lt(Zw.loc[a], axis=1)).sum() / len(oth)
# coerencia SMAP x CLSM nos anos comuns
c_ = pd.concat([longo(smap["31mai"], "s"), longo(Zp.loc[anos_s], "g")], axis=1).dropna()
out(f"  SMAP L4 pctl x CLSM pctl empirico (municipio-anos 2016-2025): Spearman {stats.spearmanr(c_.s, c_.g).correlation:+.2f}")
for rot_l, lab, lim in [("L1 quebra canonica do milho", L1, 0.5), ("L2 cesta tipo GS, perda >= 50%", L2, 0.5)]:
    out(f"  -- {rot_l} | 2003-2025 --")
    y = (lab < lim)
    y = y[y.index.get_level_values("ano").isin(anos_g)]
    gp = longo(Zp, "gp")
    im = longo(imerg["31mai"].loc[anos_g], "pn")
    avalia(-gp, gp <= 20, y, "CLSM pctl <= 20, fev-mai")
    avalia(-im, im < 0.75, y, "IMERG < 75% normal, fev-mai")
    # 2 sinais juntos: paga se qualquer um dispara / se os dois disparam
    both = pd.concat([gp, im], axis=1).dropna()
    avalia(-both.gp, (both.gp <= 20) & (both.pn < 0.75), y, "CLSM E IMERG (os dois)")
    avalia(-both.gp, (both.gp <= 20) | (both.pn < 0.75), y, "CLSM OU IMERG (qualquer um)")

SAIDA.write_text("\n".join(LINHAS), encoding="utf-8")
