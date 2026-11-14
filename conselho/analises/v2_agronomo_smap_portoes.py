"""Agronomo (rodada 2) - SMAP L4 zona da raiz na data de plantio e nos portoes x quebra canonica (IBGE PAM).

Perguntas (pre-declaradas antes de rodar):
 P1. Nos portoes 31/jan, 28/fev, 19/mar e 30/abr, o percentil da zona da raiz do SMAP L4 separa a quebra canonica do
     milho, do feijao e da mandioca tao bem quanto a chuva IMERG acumulada desde 1/jan (% do normal, regra canonica)?
     Soma algo a chuva? Validacao: ano inteiro fora (LOYO), IC90 por bootstrap de ANOS, AUC dentro do ano.
 P2. Plantar no perfil seco: no dia de semeadura da regra do agricultor (1o dia com >= 20 mm em 3 dias, IMERG),
     o percentil da zona da raiz muda a chance de quebra do milho?
 P3. Quixada 2016-2025: o SMAP explica 2023, 2024 e 2025 (quebra do milho com chuva 93-105% do normal)?
 P4. Estado atual (ultimo dia do arquivo, 10/11/2026) e se o solo de novembro diz algo da quadra seguinte.

Regras fixadas a priori (nao ajustadas olhando o resultado):
 - alerta SMAP = percentil da zona da raiz < 25 no dia do portao; alerta de chuva = canonico (< 75% do normal,
   normal = mediana dos OUTROS anos 1998-2025 do municipio);
 - quebra canonica = producao/area plantada < 50% da mediana do proprio municipio nos OUTROS anos (1998-2025);
 - anos com SMAP: 2016-2025 (o L4 comeca em 31/03/2015; a quadra de 2015 fica fora).
Dados: dados/smap/smap_l4_diario_ne.nc (so o recorte do CE); conselho/analises/saidas/chuva_mun_diaria.parquet;
       conselho/analises/saidas/agronomo_isna_mun_ano.parquet (dia de semeadura); dados/derivados/ibge_pam_mun_anual.parquet.
Saida: impressa (-> v2_agronomo_smap_portoes.saida.txt) e saidas/v2_agronomo_smap_mun_*.parquet (serie municipal diaria).
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
RNG = np.random.default_rng(0)
ANOS = list(range(2016, 2026))
PORTOES = {"31/jan": "01-31", "28/fev": "02-28", "19/mar": "03-19", "30/abr": "04-30"}

# ------------------------------------------------------------------ 1. SMAP L4 por municipio (media dos pixels)
with Cronometro("smap municipal"):
    ds = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
    s = ds[["sm_rootzone", "sm_rootzone_pctl", "sm_surface"]].sel(lat=slice(-2.6, -8.0), lon=slice(-41.6, -37.1)).load()
    mun = gpd.read_file(REF / "ceara_municipios.geojson")
    mun["cod"] = mun.codarea.astype(str)
    lo, la = np.meshgrid(s.lon.values, s.lat.values)
    P = lo.size
    M = np.zeros((P, len(mun)), np.float32)
    n_viz = 0
    for j, (_, m) in enumerate(mun.iterrows()):
        mk = shapely.contains_xy(m.geometry, lo, la).ravel()
        if mk.sum() == 0:
            pt = m.geometry.representative_point()
            d = (lo.ravel() - pt.x) ** 2 + (la.ravel() - pt.y) ** 2
            d[np.isnan(s.sm_rootzone.isel(time=0).values.ravel())] = np.inf
            mk = np.zeros(P, bool); mk[np.argmin(d)] = True; n_viz += 1
        M[mk, j] = 1.0
    SER = {}
    for v in ["sm_rootzone", "sm_rootzone_pctl", "sm_surface"]:
        X = s[v].values.reshape(len(s.time), P)
        ok = np.isfinite(X)
        num = np.where(ok, X, 0) @ M
        den = ok.astype(np.float32) @ M
        SER[v] = pd.DataFrame(num / np.where(den > 0, den, np.nan), index=pd.DatetimeIndex(s.time.values), columns=mun.cod)
        SER[v].to_parquet(OUT / f"v2_agronomo_smap_mun_{v}.parquet")
print(f"SMAP L4: {len(s.time)} dias ({s.time.values[0]!s:.10} a {s.time.values[-1]!s:.10}); {len(mun)} municipios; "
      f"{n_viz} pequenos usam o pixel mais proximo; pixels por municipio: mediana {np.median(M.sum(0)):.0f}")
RZ, PC = SER["sm_rootzone"], SER["sm_rootzone_pctl"]
falta = RZ.loc["2016-01-01":"2025-12-31"].isna().all(axis=1).mean()
print(f"dias sem dado 2016-2025: {falta:.1%}")

# ------------------------------------------------------------------ 2. quebra canonica (mesma definicao do arquiteto)
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
    p["razao"] = p.r / p.ref
    p["quebra"] = p.razao < 0.5
    p["cod"] = p.cod_local.astype(str)
    return p.dropna(subset=["razao"])[["cod", "ano", "razao", "quebra"]]


Q = {"milho": serie("Milho (em gr"), "feijao": serie("Feij"), "mandioca": serie("Mandioca")}

# ------------------------------------------------------------------ 3. chuva acumulada desde 1/jan, % do normal (canonico)
chuva = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
cods = [c for c in chuva.columns if c in set(mun.cod)]
CH = {}
for g, md in PORTOES.items():
    acc = {a: chuva.loc[f"{a}-01-01":f"{a}-{md}", cods].sum() for a in range(1998, 2026)}
    A = pd.DataFrame(acc).T  # ano x mun
    norm = pd.DataFrame({a: A.drop(index=a).median() for a in A.index}).T
    CH[g] = (A / norm)

# ------------------------------------------------------------------ 4. painel municipio-ano
sem = pd.read_parquet(OUT / "agronomo_isna_mun_ano.parquet")[["cod", "ano", "semeadura_doy"]]
sem["cod"] = sem.cod.astype(str)
linhas = []
for a in ANOS:
    for c in cods:
        r = {"cod": c, "ano": a}
        for g, md in PORTOES.items():
            t = pd.Timestamp(f"{a}-{md}")
            r[f"chuva_{g}"] = CH[g].loc[a, c]
            r[f"pctl_{g}"] = PC.at[t, c] if t in PC.index else np.nan
            r[f"rz_{g}"] = RZ.at[t, c] if t in RZ.index else np.nan
        linhas.append(r)
D = pd.DataFrame(linhas).merge(sem, on=["cod", "ano"], how="left")
# no dia de semeadura do agricultor e na floracao do milho (dia +50 a +85 apos a semeadura)
ps, pf = [], []
for _, r in D.iterrows():
    t0 = pd.Timestamp(f"{int(r.ano)}-01-01") + pd.Timedelta(days=int(r.semeadura_doy) - 1)
    ps.append(PC.at[t0, r.cod] if t0 in PC.index else np.nan)
    pf.append(PC.loc[t0 + pd.Timedelta(days=50):t0 + pd.Timedelta(days=85), r.cod].mean())
D["pctl_semeadura"], D["pctl_flor_milho"] = ps, pf
print(f"painel: {len(D)} municipio-anos ({D.cod.nunique()} municipios x {D.ano.nunique()} anos 2016-2025)")


def auc(y, s):
    y = np.asarray(y, bool)
    return roc_auc_score(y, s) if 0 < y.sum() < len(y) else np.nan


def boot_ano(d, f, B=2000):
    anos = d.ano.unique()
    grp = {a: d[d.ano == a] for a in anos}
    v = []
    for _ in range(B):
        bb = pd.concat([grp[a] for a in RNG.choice(anos, len(anos))])
        v.append(f(bb))
    return np.nanpercentile(v, [5, 95])


def dentro_ano(d, col):
    vals, ws = [], []
    for a, g in d.groupby("ano"):
        if g.quebra.sum() >= 5 and (~g.quebra).sum() >= 5:
            vals.append(auc(g.quebra, -g[col])); ws.append(len(g))
    return (np.average(vals, weights=ws) if vals else np.nan), len(vals)


# ------------------------------------------------------------------ P1. habilidade por portao
print("\n=== P1. Habilidade por portao, quebra canonica, 2016-2025 (AUC: valor baixo -> quebra) ===")
taxa = {}
for cult, q in Q.items():
    d0 = D.merge(q, on=["cod", "ano"])
    taxa[cult] = d0.groupby("ano").quebra.mean()
    print(f"\n{cult}: {len(d0)} municipio-anos; taxa-base {d0.quebra.mean():.1%}; fracao em quebra por ano: "
          + ", ".join(f"{a}: {v:.0%}" for a, v in taxa[cult].items()))
    for g in PORTOES:
        d = d0.dropna(subset=[f"chuva_{g}", f"pctl_{g}"])
        a_c, a_s = auc(d.quebra, -d[f"chuva_{g}"]), auc(d.quebra, -d[f"pctl_{g}"])
        ic_c = boot_ano(d, lambda b: auc(b.quebra, -b[f"chuva_{g}"]), 1000)
        ic_s = boot_ano(d, lambda b: auc(b.quebra, -b[f"pctl_{g}"]), 1000)
        w_c, nw = dentro_ano(d, f"chuva_{g}")
        w_s, _ = dentro_ano(d, f"pctl_{g}")
        # LOYO logistica pareada: chuva | chuva + pctl
        X1 = np.c_[np.log(d[f"chuva_{g}"].clip(0.05))]
        X2 = np.c_[X1, d[f"pctl_{g}"] / 100]
        p1 = np.zeros(len(d)); p2 = np.zeros(len(d))
        for a in ANOS:
            te = (d.ano == a).values
            if te.sum() == 0 or d.quebra[~te].nunique() < 2:
                continue
            p1[te] = LogisticRegression().fit(X1[~te], d.quebra[~te]).predict_proba(X1[te])[:, 1]
            p2[te] = LogisticRegression().fit(X2[~te], d.quebra[~te]).predict_proba(X2[te])[:, 1]
        dd = d.assign(p1=p1, p2=p2)
        dif = boot_ano(dd, lambda b: auc(b.quebra, b.p2) - auc(b.quebra, b.p1), 1000)
        br1, br2 = ((p1 - d.quebra) ** 2).mean(), ((p2 - d.quebra) ** 2).mean()
        print(f"  {g}: chuva AUC {a_c:.2f} (IC90 {ic_c[0]:.2f}-{ic_c[1]:.2f}) | SMAP pctl AUC {a_s:.2f} "
              f"(IC90 {ic_s[0]:.2f}-{ic_s[1]:.2f}) | dentro do ano: chuva {w_c:.2f}, SMAP {w_s:.2f} ({nw} anos com >=5 quebras) | "
              f"LOYO chuva {auc(d.quebra, p1):.2f} -> chuva+SMAP {auc(d.quebra, p2):.2f} (dif IC90 {dif[0]:+.2f} a {dif[1]:+.2f}); "
              f"Brier {br1:.3f} -> {br2:.3f}")

print("\n--- Tabela de alerta em 19/mar e 30/abr (milho): chance de quebra com e sem cada alerta ---")
dm = D.merge(Q["milho"], on=["cod", "ano"])
for g in ["19/mar", "30/abr"]:
    d = dm.dropna(subset=[f"pctl_{g}"])
    ac = d[f"chuva_{g}"] < 0.75
    asm = d[f"pctl_{g}"] < 25
    for nome, m in [("chuva < 75%", ac), ("SMAP pctl < 25", asm), ("os dois", ac & asm), ("so chuva", ac & ~asm),
                    ("so SMAP", ~ac & asm), ("nenhum", ~ac & ~asm)]:
        anos_on = sorted(d[m].ano.unique())
        print(f"  {g} {nome:15s}: n={m.sum():4d}  quebram {d.quebra[m].mean() * 10 if m.sum() else np.nan:4.1f} em 10 "
              f"| anos com o alerta aceso em >=25% dos municipios: "
              f"{[a for a in anos_on if m[d.ano == a].mean() >= 0.25]}")
    print(f"  {g} concordancia dos alertas: {(ac == asm).mean():.0%}; correlacao Spearman chuva x pctl: "
          f"{d[[f'chuva_{g}', f'pctl_{g}']].corr('spearman').iloc[0, 1]:+.2f}")

# ------------------------------------------------------------------ P2. plantar no perfil seco
print("\n=== P2. Percentil da zona da raiz no dia de semeadura do agricultor x quebra do milho (2016-2025) ===")
d = dm.dropna(subset=["pctl_semeadura"]).copy()
d["terco"] = pd.cut(d.pctl_semeadura, [-1, 33.3, 66.6, 101], labels=["seco (<33)", "medio", "umido (>67)"])
for t, g in d.groupby("terco"):
    ic = boot_ano(g, lambda b: b.quebra.mean(), 1000)
    print(f"  {t:12s}: n={len(g):4d}  quebra {g.quebra.mean():.1%} (IC90 por ano {ic[0]:.1%}-{ic[1]:.1%}); "
          f"dia mediano de semeadura {g.semeadura_doy.median():.0f}")
print(f"  AUC (pctl na semeadura): {auc(d.quebra, -d.pctl_semeadura):.2f}; dentro do ano: {dentro_ano(d, 'pctl_semeadura')[0]:.2f}")
# dentro do ano: os municipios que plantaram no perfil mais seco DAQUELE ano quebraram mais?
d["pctl_sem_rel"] = d.pctl_semeadura - d.groupby("ano").pctl_semeadura.transform("median")
d["sem_rel"] = d.semeadura_doy - d.groupby("ano").semeadura_doy.transform("median")
print(f"  dentro do ano: AUC do percentil relativo {auc(d.quebra, -d.pctl_sem_rel):.2f}; "
      f"AUC da semeadura tardia relativa {auc(d.quebra, d.sem_rel):.2f}")
print("  floracao do milho (+50 a +85 d) - diagnostico de fim de safra, NAO e portao:")
d = dm.dropna(subset=["pctl_flor_milho"])
print(f"   AUC pctl na floracao {auc(d.quebra, -d.pctl_flor_milho):.2f} (IC90 "
      f"{'-'.join(f'{x:.2f}' for x in boot_ano(d, lambda b: auc(b.quebra, -b.pctl_flor_milho), 1000))}); "
      f"dentro do ano {dentro_ano(d, 'pctl_flor_milho')[0]:.2f}")

# ------------------------------------------------------------------ P3. Quixada
nomes = {str(x["id"]): x["nome"] for x in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}
QX = [c for c, n in nomes.items() if n == "Quixadá"][0]
print(f"\n=== P3. Quixada ({QX}), ano a ano ===")
qm = Q["milho"][Q["milho"].cod == QX].set_index("ano").razao
qf = Q["feijao"][Q["feijao"].cod == QX].set_index("ano").razao
dq = D[D.cod == QX].set_index("ano")
med_est = D.groupby("ano")[["pctl_19/mar", "pctl_30/abr", "pctl_flor_milho"]].median()
print(" ano | milho razao | feijao razao | chuva%19/mar | pctl 19/mar | chuva%30/abr | pctl 30/abr | semeadura doy | "
      "pctl semeadura | pctl floracao milho | pctl flor. mediana do estado")
for a in ANOS:
    r = dq.loc[a]
    print(f" {a} | {qm.get(a, np.nan):5.2f} {'Q' if qm.get(a, 1) < 0.5 else ' '} | {qf.get(a, np.nan):5.2f} "
          f"{'Q' if qf.get(a, 1) < 0.5 else ' '} | {r['chuva_19/mar']:5.0%} | {r['pctl_19/mar']:5.0f} | "
          f"{r['chuva_30/abr']:5.0%} | {r['pctl_30/abr']:5.0f} | {r.semeadura_doy:4.0f} | {r.pctl_semeadura:5.0f} | "
          f"{r.pctl_flor_milho:5.0f} | {med_est.loc[a, 'pctl_flor_milho']:5.0f}")
# 2026 (sem PAM ainda)
for g, md in PORTOES.items():
    t = pd.Timestamp(f"2026-{md}")
    print(f"  2026 {g}: Quixada pctl {PC.at[t, QX]:.0f}; mediana do CE {PC.loc[t].median():.0f}")

# ------------------------------------------------------------------ P4. hoje e memoria de novembro
ult = PC.index[-1]
print(f"\n=== P4. Ultimo dia do SMAP L4: {ult.date()} ===")
print(f"  pctl zona da raiz: mediana CE {PC.loc[ult].median():.0f} (p10-p90 {PC.loc[ult].quantile(.1):.0f}-"
      f"{PC.loc[ult].quantile(.9):.0f}); Quixada {PC.at[ult, QX]:.0f}; umidade CE mediana {RZ.loc[ult].median():.3f} m3/m3")
nov = {}
for a in range(2015, 2026):
    t = pd.Timestamp(f"{a}-11-10")
    if t in PC.index:
        nov[a] = (PC.loc[t].median(), RZ.loc[t].median())
print("  10/nov de cada ano: pctl mediano (umidade) -> fracao de municipios com quebra do milho na quadra seguinte:")
xs, ys = [], []
for a, (p_, r_) in nov.items():
    fq = taxa["milho"].get(a + 1, np.nan)
    print(f"   {a}: pctl {p_:4.0f} ({r_:.3f} m3/m3) -> quadra {a + 1}: {fq if np.isnan(fq) else round(fq * 100)}%")
    if np.isfinite(fq):
        xs.append(p_); ys.append(fq)
from scipy import stats  # noqa: E402
print(f"  Spearman pctl de 10/nov x quebra da quadra seguinte: rho {stats.spearmanr(xs, ys)[0]:+.2f} (n = {len(xs)} anos)")
