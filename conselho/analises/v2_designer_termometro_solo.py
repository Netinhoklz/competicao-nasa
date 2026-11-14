"""Designer, rodada 2 (dados novos). O "termometro do solo": SMAP L4 percentil da zona da raiz por municipio.

Perguntas (pre-registradas antes de rodar; faixas fixadas a priori, sem ajuste):
  Faixas do termometro: VERMELHO pctl < 20 (seco para a epoca), AMARELO 20 a < 40, VERDE >= 40.
  A. O termometro nos portoes 28/fev, 19/mar e 30/abr (media dos 7 dias ate a data) separa a quebra canonica do milho?
     PAREADO com a regra canonica do IMERG (acumulado desde 1/jan < 75% do normal) nos MESMOS municipio-anos.
     AUC total, AUC dentro do ano (ponderada) e associacao entre anos (Spearman da media anual x fracao em quebra).
     Unidade independente = ANO. 2016-2025 (19/mar e 28/fev; o SMAP comeca em 31/03/2015); 2015-2025 em 30/abr.
  B. Frequencias naturais por faixa: "de cada 10 municipio-anos no vermelho, X quebraram", com o numero de ANOS distintos.
  C. Quixada ano a ano (o placar que o tecnico ve) e os anos 2023-2025 sem explicacao pela chuva.
  D. Quando o termometro "dorme": espalhamento entre anos da umidade absoluta (m3/m3) por mes.
  E. Hoje: termometro de 04-10/nov/2026 em Quixada e no CE, contra os mesmos dias de 2015-2025; persistencia nov -> 19/mar.
So le arquivos; nao escreve nada fora do stdout.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import json
import time

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
t0 = time.time()
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"

# ---------------- quebra canonica (mesma receita de arquiteto_final_curvas_quixada.py)
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
nomes = json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))
COD_QXD = str(next(m["id"] for m in nomes if m["nome"].startswith("Quixad")))
print("Quixada cod", COD_QXD)

# ---------------- SMAP L4: recorte CE, todos os dias (so 2 variaveis)
ds = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
ds = ds.sel(lat=slice(-2.5, -8.0), lon=slice(-41.5, -37.0))[["sm_rootzone_pctl", "sm_rootzone"]].load()
print(f"SMAP L4 CE: {ds.sizes}; {str(ds.time.values[0])[:10]} -> {str(ds.time.values[-1])[:10]}; carregado em {time.time()-t0:.0f}s")

# celulas -> municipios (centro da celula dentro do poligono; municipio sem celula -> celula mais proxima do centroide)
gm = municipios_ce_gdf()
gm["cod"] = gm.codarea.astype(str)
LON, LAT = np.meshgrid(ds.lon.values, ds.lat.values)
pts = gpd.GeoDataFrame({"i": np.arange(LON.size)}, geometry=gpd.points_from_xy(LON.ravel(), LAT.ravel()), crs=gm.crs)
sj = gpd.sjoin(pts, gm[["cod", "geometry"]], predicate="within", how="inner")
cel = {c: list(g.i.values) for c, g in sj.groupby("cod")}
sem = 0
for _, r in gm.iterrows():
    if r.cod not in cel:
        c = r.geometry.centroid
        cel[r.cod] = [int(np.argmin((LON.ravel() - c.x) ** 2 + (LAT.ravel() - c.y) ** 2))]
        sem += 1
print(f"municipios: {len(cel)}; sem celula de 9 km dentro (usa a mais proxima): {sem}; Quixada tem {len(cel[COD_QXD])} celulas")

T = ds.sizes["time"]
P = ds.sm_rootzone_pctl.values.reshape(T, -1)
Z = ds.sm_rootzone.values.reshape(T, -1)
datas = pd.to_datetime(ds.time.values)
pct_mun = pd.DataFrame({c: np.nanmean(P[:, ix], axis=1) for c, ix in cel.items()}, index=datas)
rz_mun = pd.DataFrame({c: np.nanmean(Z[:, ix], axis=1) for c, ix in cel.items()}, index=datas)
mce = np.array(sorted(set(sj.i.values)))
ce_pct = pd.Series(np.nanmean(P[:, mce], axis=1), index=datas)
ce_rz = pd.Series(np.nanmean(Z[:, mce], axis=1), index=datas)

print("\n--- Checagem da escala do percentil (o produto traz a climatologia pronta) ---")
vv = pct_mun.values.ravel()
vv = vv[np.isfinite(vv)]
print(f"municipio-dias 2015-2026: fracao < 20 = {np.mean(vv < 20):.1%}; < 40 = {np.mean(vv < 40):.1%}; >= 40 = {np.mean(vv >= 40):.1%}; mediana {np.median(vv):.0f}")
print("  (se a climatologia do produto for de um periodo mais umido que 2015-2026, o vermelho aparece mais que 20% das vezes)")
por_ano = pct_mun.groupby(pct_mun.index.year).apply(lambda d: np.nanmean(d.values < 20))
print("  fracao de municipio-dias no vermelho por ano:", {int(k): round(float(v), 2) for k, v in por_ano.items()})

# ---------------- IMERG % do normal (regra canonica)
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
anos_all = list(range(1998, 2026))


def pct_normal(m, d):
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in anos_all}).T
    out = ac.copy() * np.nan
    for a in anos_all:
        out.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return out


def termo(m, d, anos):
    """media do percentil nos 7 dias ate a data (inclusive), municipio x ano"""
    rows = {}
    for a in anos:
        fim = pd.Timestamp(a, m, d)
        jan = pct_mun.loc[fim - pd.Timedelta(days=6):fim]
        if len(jan) >= 5:
            rows[a] = jan.mean()
    return pd.DataFrame(rows).T


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, g[col]); den += w
    return num / den if den else np.nan


def banda(v):
    return np.where(v < 20, "vermelho", np.where(v < 40, "amarelo", "verde"))


rng = np.random.default_rng(0)


def auc_ic_ano(df, col, nboot=400):
    yrs = df.ano.unique()
    g = {a: df[df.ano == a] for a in yrs}
    bs = []
    for _ in range(nboot):
        bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            bs.append(roc_auc_score(bb.quebra, bb[col]))
    return np.percentile(bs, 5), np.percentile(bs, 95)


print("\n" + "=" * 20, "A/B. Termometro x regra do IMERG, pareado (milho, quebra canonica)", "=" * 20)
PORT = {"28/fev": (2, 28, range(2016, 2026)), "19/mar": (3, 19, range(2016, 2026)), "30/abr": (4, 30, range(2015, 2026))}
guard = {}
for nome, (m, d, anos) in PORT.items():
    S = termo(m, d, anos).stack().rename("smap").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})
    I = pct_normal(m, d).stack().rename("pct").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})
    df = mi[["cod", "ano", "quebra", "razao"]].merge(S, on=["cod", "ano"]).merge(I, on=["cod", "ano"]).dropna()
    df["s_smap"] = -df.smap
    df["s_imerg"] = -df.pct.clip(upper=3)
    guard[nome] = df
    a_s, a_i = roc_auc_score(df.quebra, df.s_smap), roc_auc_score(df.quebra, df.s_imerg)
    ls, hs = auc_ic_ano(df, "s_smap")
    li, hi = auc_ic_ano(df, "s_imerg")
    w_s, w_i = auc_dentro(df, "s_smap"), auc_dentro(df, "s_imerg")
    an = df.groupby("ano").agg(q=("quebra", "mean"), smap=("smap", "mean"), pct=("pct", "mean"))
    rs = spearmanr(-an.smap, an.q).correlation
    ri = spearmanr(-an.pct, an.q).correlation
    print(f"\n[{nome}] n = {len(df)} municipio-anos, {df.ano.nunique()} anos ({df.ano.min()}-{df.ano.max()}), taxa de quebra {df.quebra.mean():.3f}")
    print(f"   AUC total     SMAP {a_s:.3f} [IC90 ano {ls:.2f}-{hs:.2f}] | IMERG {a_i:.3f} [{li:.2f}-{hi:.2f}]")
    print(f"   AUC dentro do ano (entre municipios, mesmo ano): SMAP {w_s:.3f} | IMERG {w_i:.3f}")
    print(f"   entre anos (Spearman media anual x fracao em quebra, n = {len(an)}): SMAP {rs:+.2f} | IMERG {ri:+.2f}")
    print(f"   r(SMAP pctl, IMERG % normal) nos mesmos municipio-anos: {np.corrcoef(df.smap, df.pct.clip(upper=3))[0,1]:+.2f}")
    df["banda"] = banda(df.smap.values)
    tab = df.groupby("banda").agg(n=("quebra", "size"), quebram=("quebra", "sum"), anos=("ano", "nunique"))
    tab["em_10"] = (10 * tab.quebram / tab.n).round(1)
    print("   Frequencias naturais por faixa do termometro:")
    for b in ["vermelho", "amarelo", "verde"]:
        if b in tab.index:
            r = tab.loc[b]
            anos_b = df[df.banda == b].groupby("ano").size()
            top = anos_b.sort_values(ascending=False).head(3)
            print(f"     {b:9s}: {int(r.quebram):4d} de {int(r.n):4d} quebraram = {r.em_10:.1f} em 10 | anos distintos {int(r.anos)}; "
                  f"anos que mais pesam: {dict(top)}")
    al = df.pct < 0.75
    print(f"   Regra IMERG <75%: com alerta {10*df.quebra[al].mean():.1f} em 10 (n={al.sum()}); sem alerta {10*df.quebra[~al].mean():.1f} em 10 (n={(~al).sum()})")
    k = int(al.sum())
    top_s = df.smap.rank(method="first") <= k
    print(f"   Mesma taxa de alerta (os {k} municipio-anos mais secos por cada fonte): SMAP {10*df.quebra[top_s].mean():.1f} em 10 | IMERG {10*df.quebra[al].mean():.1f} em 10")
    vm = df.banda == "vermelho"
    print(f"   Concordancia: vermelho e alerta IMERG {np.mean(vm & al):.1%}; so vermelho {np.mean(vm & ~al):.1%}; so IMERG {np.mean(~vm & al):.1%}")
    for lab, msk in [("vermelho E alerta IMERG", vm & al), ("so vermelho (IMERG ok)", vm & ~al), ("so alerta IMERG (SMAP nao vermelho)", ~vm & al), ("nenhum", ~vm & ~al)]:
        if msk.sum():
            print(f"     {lab:38s}: {10*df.quebra[msk].mean():.1f} em 10 quebraram (n={msk.sum()}, anos {df.ano[msk].nunique()})")

print("\n" + "=" * 20, "C. Quixada ano a ano (o placar do tecnico)", "=" * 20)
rows = []
for a in range(2015, 2026):
    r = {"ano": a}
    for nome, df in guard.items():
        q = df[(df.cod == COD_QXD) & (df.ano == a)]
        r[f"smap_{nome}"] = round(float(q.smap.iloc[0])) if len(q) else np.nan
        r[f"imerg%_{nome}"] = round(100 * float(q.pct.iloc[0])) if len(q) else np.nan
    q = mi[(mi.cod == COD_QXD) & (mi.ano == a)]
    r["razao_milho"] = round(float(q.razao.iloc[0]), 2) if len(q) else np.nan
    r["quebra"] = int(q.quebra.iloc[0]) if len(q) else np.nan
    rows.append(r)
Q = pd.DataFrame(rows).set_index("ano")
print(Q.to_string())
for nome in PORT:
    c = Q[f"smap_{nome}"]
    v = c < 20
    ok = Q.quebra == 1
    print(f"  {nome}: termometro vermelho em {int(v.sum())} anos, com quebra em {int((v & ok).sum())}; quebras sem vermelho: {list(Q.index[ok & ~v & c.notna()])}")
    al = Q[f"imerg%_{nome}"] < 75
    print(f"          IMERG <75% em {int(al.sum())} anos, com quebra em {int((al & ok).sum())} (mesmos anos {Q.index[c.notna()].min()}-{Q.index.max()})")

print("\n" + "=" * 20, "D. Quando o termometro dorme: espalhamento entre anos, por mes (CE)", "=" * 20)
mm = ce_rz.resample("MS").mean()
mp = ce_pct.resample("MS").mean()
tabm = pd.DataFrame({"rz_mediana": mm.groupby(mm.index.month).median(),
                     "rz_p10": mm.groupby(mm.index.month).quantile(0.1), "rz_p90": mm.groupby(mm.index.month).quantile(0.9),
                     "pctl_p10": mp.groupby(mp.index.month).quantile(0.1), "pctl_p90": mp.groupby(mp.index.month).quantile(0.9)})
tabm["rz_amplitude_p90_p10"] = tabm.rz_p90 - tabm.rz_p10
print(tabm.round(3).to_string())
amp = tabm.rz_amplitude_p90_p10
print(f"  amplitude entre anos (p90-p10) em abr = {amp[4]:.3f} m3/m3; em nov = {amp[11]:.3f}; razao abr/nov = {amp[4]/amp[11]:.1f}x")
print(f"  faixa dinamica do ano (mediana de abr - mediana de nov) = {tabm.rz_mediana[4]-tabm.rz_mediana[11]:.3f} m3/m3")

print("\n" + "=" * 20, "D2. O proprio produto desliga o percentil na seca (celulas do CE com percentil, por mes)", "=" * 20)
temp = np.isfinite(P[:, mce])
disp = pd.Series(temp.mean(axis=1), index=datas)
print("  fracao das celulas terrestres do CE COM percentil, media por mes:",
      {int(k): round(float(v), 3) for k, v in disp.groupby(disp.index.month).mean().items()})
dd = disp.groupby(disp.index.dayofyear).agg(["min", "max"])
print(f"  a mascara e a mesma todo ano? maior diferenca entre anos no mesmo dia do ano = {float((dd['max'] - dd['min']).max()):.3f}")
liga = disp.groupby(disp.index.dayofyear).mean()
on = liga[liga >= 0.5]
print(f"  dia do ano em que >= 50% do CE tem percentil: de {on.index.min()} a {on.index.max()} (com eventuais buracos: {len(on)} dias)")
for doy in [1, 15, 32, 46, 60, 78, 121, 152, 182, 213, 244]:
    print(f"    doy {doy:3d} ({(pd.Timestamp(2026,1,1)+pd.Timedelta(days=doy-1)):%d/%m}): {liga.loc[doy]:.0%} das celulas com percentil")

print("\n" + "=" * 20, "E. Hoje (04-10/nov/2026): nivel absoluto, porque o percentil esta desligado", "=" * 20)
fim = pct_mun.index.max()
print("ultimo dia SMAP L4:", fim.date())
hist = []
for a in range(2015, 2027):
    s = pd.Timestamp(a, 11, 4); e = pd.Timestamp(a, 11, 10)
    if e <= fim:
        hist.append({"ano": a, "qxd_rz": float(rz_mun.loc[s:e, COD_QXD].mean()), "ce_rz": float(ce_rz.loc[s:e].mean()),
                     "qxd_pctl_disp": float(np.isfinite(pct_mun.loc[s:e, COD_QXD]).mean())})
H = pd.DataFrame(hist).set_index("ano")
print(H.round(4).to_string())
print(f"  2026: Quixada {H.qxd_rz[2026]:.3f} m3/m3 (faixa 2015-2025: {H.qxd_rz[:2025].min():.3f} a {H.qxd_rz[:2025].max():.3f}); "
      f"posto entre {len(H)} novembros (1 = mais seco): {int(H.qxd_rz.rank().loc[2026])}; CE posto {int(H.ce_rz.rank().loc[2026])}")
# persistencia: nivel de nov do ano t-1 -> termometro de 19/mar e fracao em quebra do ano t
m19 = guard["19/mar"].groupby("ano").agg(smap19=("smap", "mean"), q=("quebra", "mean"))
pers = H[["ce_rz"]].rename(columns={"ce_rz": "nov_anterior_rz"})
pers.index = pers.index + 1
J = m19.join(pers, how="inner")
print(f"  persistencia (CE, n = {len(J)} anos): Spearman nivel nov(t-1) x termometro 19/mar(t) = {spearmanr(J.nov_anterior_rz, J.smap19).correlation:+.2f}; "
      f"nov(t-1) seco x fracao em quebra(t) = {spearmanr(-J.nov_anterior_rz, J.q).correlation:+.2f}")
print(J.round(3).to_string())
print(f"\ntempo total {time.time()-t0:.0f}s")

print("\n" + "=" * 20, "F. Ano a ano no estado: quebras pegas pelo vermelho x pelo alerta IMERG (o caso 2016)", "=" * 20)
for nome in ["19/mar", "30/abr"]:
    df = guard[nome]
    lin = []
    for a, g in df.groupby("ano"):
        q = g[g.quebra == 1]
        lin.append({"ano": a, "quebras": len(q), "frac_quebra": round(g.quebra.mean(), 2),
                    "termometro_medio": round(g.smap.mean()), "imerg_medio_%": round(100 * g.pct.mean()),
                    "pegas_vermelho": int((q.smap < 20).sum()), "pegas_verm_ou_amar": int((q.smap < 40).sum()),
                    "pegas_imerg75": int((q.pct < 0.75).sum()),
                    "alarmes_vermelho_sem_quebra": int(((g.smap < 20) & (g.quebra == 0)).sum())})
    print(f"[{nome}]")
    print(pd.DataFrame(lin).set_index("ano").to_string())

print("\n" + "=" * 20, "G. Robustez: a vantagem do termometro sobre o IMERG depende de um ano so? (jackknife por ano)", "=" * 20)
for nome in ["19/mar", "30/abr"]:
    df = guard[nome]
    difs = {}
    for a in sorted(df.ano.unique()):
        d = df[df.ano != a]
        difs[a] = roc_auc_score(d.quebra, d.s_smap) - roc_auc_score(d.quebra, d.s_imerg)
    d16 = df[df.ano != 2016]
    print(f"[{nome}] diferenca de AUC (SMAP - IMERG) tirando um ano de cada vez: min {min(difs.values()):+.3f} (sem {min(difs, key=difs.get)}), "
          f"max {max(difs.values()):+.3f}; sem 2016: SMAP {roc_auc_score(d16.quebra, d16.s_smap):.3f} x IMERG {roc_auc_score(d16.quebra, d16.s_imerg):.3f}; "
          f"dentro do ano sem 2016: SMAP {auc_dentro(d16, 's_smap'):.3f} x IMERG {auc_dentro(d16, 's_imerg'):.3f}")
    print("   anos em que o termometro (media do estado) ordenou melhor que o IMERG por dentro do ano:",
          sum(1 for a, g in df.groupby("ano") if g.quebra.sum() >= 3 and (1 - g.quebra).sum() >= 3
              and roc_auc_score(g.quebra, g.s_smap) > roc_auc_score(g.quebra, g.s_imerg)),
          "de", sum(1 for a, g in df.groupby("ano") if g.quebra.sum() >= 3 and (1 - g.quebra).sum() >= 3))

print("\n" + "=" * 20, "H. O caso 2016 completo (acertos e alarmes) para o recibo", "=" * 20)
for nome in ["19/mar", "30/abr"]:
    g = guard[nome][guard[nome].ano == 2016]
    q, nq = g[g.quebra == 1], g[g.quebra == 0]
    print(f"[{nome}/2016] municipios {len(g)}; quebraram {len(q)}; vermelho: {int((q.smap<20).sum())} das quebras e {int((nq.smap<20).sum())} dos {len(nq)} sem quebra; "
          f"vermelho ou amarelo: {int((q.smap<40).sum())} e {int((nq.smap<40).sum())}; alerta IMERG: {int((q.pct<0.75).sum())} e {int((nq.pct<0.75).sum())}; "
          f"termometro medio {g.smap.mean():.0f}; IMERG medio {100*g.pct.mean():.0f}%")
