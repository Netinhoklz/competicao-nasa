"""Estrategista, RODADA 2 (dados novos), analise 1: o SMAP L4 (zona da raiz) melhora os portoes de 19/mar e 30/abr?

Pergunta: no periodo em que ha SMAP (quadras 2016-2025), o percentil da umidade da zona da raiz do SMAP L4 no dia do
portao separa melhor a quebra canonica do milho do que a regra canonica de chuva (IMERG desde 1/jan < 75% do normal)?
E o SMAP "ve" 2016 (o ano que a regra de chuva perdeu: 7% de recall em 30/abr) e Quixada 2023-2025?

Pre-registrado ANTES de olhar o resultado (nada e escolhido pelo teste):
  - SMAP: sm_rootzone_pctl do granulo das 13:30 UTC do PROPRIO dia do portao, media dos pixels 9 km cujo centro cai
    no municipio (municipio sem pixel -> pixel mais proximo do ponto representativo). Escore = -pctl.
  - Regra SMAP: pctl < 20 ("seco para a epoca", texto da secao 05 escrito antes desta analise).
  - Regra chuva: canonica do deck (IMERG 1/jan..portao < 75% da mediana dos OUTROS anos 1998-2025, mesmo municipio).
  - Regra "dois relogios": alerta se qualquer uma das duas acender (OU). As tres regras sao reportadas; nenhuma e
    escolhida no teste.
  - Alvo: quebra canonica do milho (producao/area plantada < 50% da mediana dos outros anos do municipio; area >= 50 ha).
  - Unidade independente = ANO: AUC dentro do ano (media ponderada), correlacao entre anos (n = 10) e IC90 por
    bootstrap de ANOS da diferenca pareada de AUC (mesmos municipio-anos para as duas fontes).
So le arquivos; nao escreve nada alem do proprio stdout.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, municipios_ce_gdf

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
rng = np.random.default_rng(0)
QUIX = "2311306"

# ---------------- quebra canonica (copia da receita do arquiteto_final_curvas_quixada.py)
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")


def serie(prefixo):
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        out = np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])
        return pd.Series(out, index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref
    p["quebra"] = (p.razao < 0.5).astype(int)
    p["cod"] = p.cod_local.astype(str).str[:7]
    return p.dropna(subset=["razao"])


mi = serie("Milho (em gr")
print("PAM milho: anos", mi.ano.min(), "-", mi.ano.max(), "| mun-anos", len(mi))

# ---------------- chuva canonica (% do normal desde 1/jan; normal = mediana dos OUTROS anos 1998-2025)
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
anos_all = list(range(1998, 2026))


def pct_normal(m, d):
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_all}).T
    out = ac.copy() * np.nan
    for a in anos_all:
        out.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return out


# ---------------- SMAP L4: so o recorte do Ceara e os dias dos portoes
mun = municipios_ce_gdf()
mun["cod"] = mun.codarea.astype(str).str[:7]
ds = xr.open_dataset(DADOS / "smap/smap_l4_diario_ne.nc")
_, iu = np.unique(ds.time.values, return_index=True)  # 4 dias repetidos no consolidado (2023-2025): fica o 1o
ds = ds.isel(time=np.sort(iu))
pc = ds["sm_rootzone_pctl"].sel(lat=slice(-2.3, -8.2), lon=slice(-41.7, -36.8))
LA, LO = np.meshgrid(pc.lat.values, pc.lon.values, indexing="ij")
pts = gpd.GeoDataFrame({"i": np.arange(LA.size)}, geometry=gpd.points_from_xy(LO.ravel(), LA.ravel()), crs="EPSG:4326")
mun = mun.to_crs("EPSG:4326")
j = gpd.sjoin(pts, mun[["cod", "geometry"]], predicate="within", how="inner")
mapa = j.groupby("cod")["i"].apply(list).to_dict()
sem = [c for c in mun.cod if c not in mapa]
for c in sem:  # municipio pequeno: pixel mais proximo do ponto representativo
    rp = mun.loc[mun.cod == c].geometry.iloc[0].representative_point()
    mapa[c] = [int(np.argmin((LA.ravel() - rp.y) ** 2 + (LO.ravel() - rp.x) ** 2))]
print(f"SMAP: {LA.size} pixels no recorte; {len(mun) - len(sem)} municipios com pixel proprio, {len(sem)} pelo vizinho")

PORT = {"19/mar": (3, 19), "30/abr": (4, 30)}
anos = list(range(2016, 2026))
linhas = []
for nome, (m, d) in PORT.items():
    datas = [pd.Timestamp(a, m, d) for a in anos + [2026] if pd.Timestamp(a, m, d) <= pd.Timestamp("2026-11-10")]
    sub = pc.sel(time=datas, method="nearest").values  # (t, lat, lon)
    tt = pc.sel(time=datas, method="nearest").time.values
    assert all(abs(pd.Timestamp(x) - y) < pd.Timedelta("1D") for x, y in zip(tt, datas)), "dia do portao ausente"
    P = pct_normal(m, d)
    for k, dt in enumerate(datas):
        flat = sub[k].ravel()
        for c, idx in mapa.items():
            v = np.nanmean(flat[idx])
            pr = P.loc[dt.year, c] if (dt.year in P.index and c in P.columns) else np.nan
            linhas.append({"portao": nome, "ano": dt.year, "cod": c, "smap_pctl": v, "pct_chuva": pr})
ds.close()
X = pd.DataFrame(linhas)
df_all = X.merge(mi[["cod", "ano", "quebra", "razao"]], on=["cod", "ano"], how="left")


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, g[col]); den += w
    return num / den if den else np.nan


def boot_diff(df, c1, c2, nboot=1000):
    yrs = df.ano.unique()
    g = {a: df[df.ano == a] for a in yrs}
    out = []
    for _ in range(nboot):
        bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            out.append((roc_auc_score(bb.quebra, bb[c1]), roc_auc_score(bb.quebra, bb[c2])))
    out = np.array(out)
    dd = out[:, 0] - out[:, 1]
    return (np.percentile(out[:, 0], [5, 95]), np.percentile(out[:, 1], [5, 95]), np.percentile(dd, [5, 95]),
            (dd > 0).mean())


for nome in PORT:
    df = df_all[(df_all.portao == nome) & df_all.quebra.notna()].dropna(subset=["smap_pctl", "pct_chuva"]).copy()
    df["quebra"] = df.quebra.astype(int)
    df["s_smap"] = -df.smap_pctl
    df["s_chuva"] = -df.pct_chuva.clip(upper=3)
    print("\n" + "=" * 18, f"Portao {nome} | quadras 2016-2025 | n = {len(df)} municipio-anos | taxa de quebra "
          f"{df.quebra.mean():.1%}", "=" * 18)
    a_s, a_c = roc_auc_score(df.quebra, df.s_smap), roc_auc_score(df.quebra, df.s_chuva)
    ics, icc, icd, pmaior = boot_diff(df, "s_smap", "s_chuva")
    print(f"  AUC agrupada  SMAP pctl: {a_s:.3f} IC90 [{ics[0]:.2f},{ics[1]:.2f}] | chuva IMERG %normal: {a_c:.3f} "
          f"IC90 [{icc[0]:.2f},{icc[1]:.2f}]")
    print(f"  diferenca pareada SMAP - chuva: {a_s - a_c:+.3f}  IC90 por ano [{icd[0]:+.3f},{icd[1]:+.3f}]  "
          f"P(SMAP > chuva) no bootstrap = {pmaior:.2f}")
    print(f"  AUC DENTRO do ano  SMAP: {auc_dentro(df, 's_smap'):.3f} | chuva: {auc_dentro(df, 's_chuva'):.3f}")
    an = df.groupby("ano").agg(fq=("quebra", "mean"), smap=("smap_pctl", "mean"), chuva=("pct_chuva", "median"),
                               n=("quebra", "size"))
    r1, p1 = spearmanr(an.smap, an.fq)
    r2, p2 = spearmanr(an.chuva, an.fq)
    print(f"  ENTRE anos (n = {len(an)}): Spearman(fracao em quebra, SMAP medio) = {r1:+.2f} (p {p1:.3f}); "
          f"(fracao em quebra, chuva mediana) = {r2:+.2f} (p {p2:.3f})")
    # regras de alerta pre-declaradas
    df["al_smap"] = df.smap_pctl < 20
    df["al_chuva"] = df.pct_chuva < 0.75
    df["al_ou"] = df.al_smap | df.al_chuva
    print("  Regra             | acende  | P(quebra|alerta) | P(quebra|sem) | recall | 2016 recall | 2025 recall")
    for r, rot in [("al_chuva", "chuva <75%"), ("al_smap", "SMAP pctl <20"), ("al_ou", "dois relogios (OU)")]:
        al = df[r]
        q = df.quebra.astype(bool)
        rec = lambda a: (al & q & (df.ano == a)).sum() / max((q & (df.ano == a)).sum(), 1)
        print(f"  {rot:17s} | {al.mean():6.1%} | {q[al].mean():16.2f} | {q[~al].mean():13.2f} | "
              f"{(al & q).sum() / q.sum():6.1%} | {rec(2016):11.1%} | {rec(2025):11.1%}   (n alerta = {al.sum()})")
    print("  Contagens por ano (quebras | alertas e acertos de cada regra):")
    for a, g in df.groupby("ano"):
        q = g.quebra.astype(bool)
        print(f"    {a}: quebras {q.sum():3d} de {len(g):3d} | chuva: {g.al_chuva.sum():3d} alertas, "
              f"{(g.al_chuva & q).sum():3d} acertos | SMAP: {g.al_smap.sum():3d} alertas, {(g.al_smap & q).sum():3d} acertos")
    print("  Por ano: fracao em quebra | SMAP pctl medio dos municipios | % mun com SMAP<20 | chuva mediana %normal | "
          "% mun com chuva<75%")
    t = df.groupby("ano").agg(fq=("quebra", "mean"), smap=("smap_pctl", "mean"), smap20=("al_smap", "mean"),
                              chuva=("pct_chuva", "median"), ch75=("al_chuva", "mean"))
    print(t.round(2).to_string())
    # DIAGNOSTICOS (nao escolhem nada; respondem a pergunta da banca "e so a chuva recente?" e "e so 2016?")
    sem16 = df[df.ano != 2016]
    print(f"  Diagnostico sem 2016: AUC SMAP {roc_auc_score(sem16.quebra, sem16.s_smap):.3f} | chuva "
          f"{roc_auc_score(sem16.quebra, sem16.s_chuva):.3f}  (n = {len(sem16)})")
    m, d = PORT[nome]
    fim = pd.Timestamp(2000, m, d)
    ini = fim - pd.Timedelta(days=59)
    rec = pd.DataFrame({a: chuva.loc[f"{a}-{ini.month:02d}-{ini.day:02d}":f"{a}-{m:02d}-{d:02d}"].sum()
                        for a in anos_all}).T
    rp = rec.copy() * np.nan
    for a in anos_all:
        rp.loc[a] = rec.loc[a] / rec.drop(index=a).median()
    rr = rp.stack().rename("pct60").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})
    dd = df.merge(rr, on=["ano", "cod"])
    dd["s_60"] = -dd.pct60.clip(upper=3)
    print(f"  Diagnostico chuva IMERG dos ultimos 60 dias (% normal): AUC {roc_auc_score(dd.quebra, dd.s_60):.3f} | "
          f"dentro do ano {auc_dentro(dd, 's_60'):.3f} | 2016: mediana {dd[dd.ano == 2016].pct60.median():.2f}, "
          f"% mun < 75% = {(dd[dd.ano == 2016].pct60 < 0.75).mean():.0%} | Spearman SMAP x chuva60 = "
          f"{spearmanr(dd.smap_pctl, dd.pct60)[0]:+.2f}")
    # placar do alerta em Quixada
    qx = df_all[(df_all.portao == nome) & (df_all.cod == QUIX)][["ano", "smap_pctl", "pct_chuva", "razao", "quebra"]]
    print(f"  Quixada ({QUIX}) no portao {nome}:")
    print(qx.round(2).to_string(index=False))

print("\nLeitura: so 10 quadras (2016-2025) e ~3 anos de seca; toda diferenca entre fontes e exploratoria (grau B/C).")
