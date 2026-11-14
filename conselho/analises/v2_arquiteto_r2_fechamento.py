"""Arquiteto-chefe, fechamento da rodada 2: respostas numericas aos pareceres da banca R2 (juiz, cetico, engenheiro).

PRE-DECLARADO (escrito antes de rodar este script; as AUCs por era das 5 leituras de chuva ja tinham sido impressas pelo
cetico em v2_cetico_r2b_smap_contra_imerg_justo.saida.txt, bloco F, entao a escolha abaixo NAO e cega a esses numeros):
 R1. Luz principal para 2027 = a leitura de chuva IMERG, entre as 5 ja declaradas por outros especialistas
     (W1 1/jan->portao, W2 1/fev->portao, API tau 13 d, R30 ultimos 30 d, R15 ultimos 15 d; corte fixo 75% do normal,
     normal = mediana dos OUTROS anos 1998-2025), com a MAIOR AUC MINIMA nos 4 casos {19/mar, 30/abr} x {1998-2015, 2016-2025}.
     Empate (diferenca < 0,01): a mais simples de explicar, nesta ordem: W1, W2, R30, R15, API. Nenhum limiar novo.
 R2. SMAP L4 (percentil da zona da raiz < 20, media dos 7 dias ate o portao; limiar da secao 05, commit 48a3608) entra como
     leitura da SEGUNDA MISSAO, que confirma ou nao; nao entra em OU com a luz principal.
 R3. Tudo o mais e REPORTADO, nao escolhido: curvas por era nos 5 portoes, ONI por era, nivel do ano em 2016/2021/2025,
     placar de Quixada, contrafactual do caupi (balde da rodada 1) em 1998/2016/2024, carteira condicionada a luz NASA,
     S0 de Quixada, checagem com o SMAP L3 consolidado.
Rotulo: quebra canonica do milho (producao / area plantada < 50% da mediana dos outros anos; area >= 50 ha; 1998-2025).
Unidade independente: o ANO (IC por bootstrap de anos; Spearman entre anos).
So le arquivos ja salvos (PAM, cache de chuva municipal do estrategista, SMAP L4 municipal deduplicado do hidrologo,
ISNA da rodada 1, POWER ET0, SMAP L3 consolidado, ONI). Saida: v2_arquiteto_r2_fechamento.saida.txt
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import hashlib
import json
import time
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import xarray as xr
from scipy import stats
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 230)
t0 = time.time()
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
SAIDA = A + "v2_arquiteto_r2_fechamento.saida.txt"
LIN = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LIN.append(s)


rng = np.random.default_rng(20261114)
ANOS = list(range(1998, 2026))
ERA1, ERA2 = list(range(1998, 2016)), list(range(2016, 2026))
QX = "2311306"
TAU = 13

# ------------------------------------------------------------------ PAM: razoes canonicas
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
pam = pam[(pam.ano >= 1998) & (pam.ano <= 2025)]


def canonica(pref):
    p = pam[pam.produto.str.startswith(pref) & (pam.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha
    o = []
    for cod, g in p.groupby("cod_local"):
        r = g.r.values
        med = np.array([np.median(np.delete(r, i)) if len(r) > 5 else np.nan for i in range(len(r))])
        o.append(pd.DataFrame({"cod": str(cod)[:7], "ano": g.ano.values, "razao": r / med}))
    return pd.concat(o).dropna().set_index(["cod", "ano"]).razao


MILHO = canonica("Milho (em")
FEIJ = canonica("Feij")
MAND = canonica("Mandioca")
base = MILHO.rename("razao").reset_index()
base["quebra"] = (base.razao < 0.5).astype(int)

chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
PC = pd.read_parquet(A + "saidas/v2_hidrologo_smap_pctl_mun_diario.parquet")
PC.columns = PC.columns.astype(str)
assert not PC.index.duplicated().any()

# ONI ASO do ano anterior
oni = pd.read_csv("E:/campeonato-nasa/dados/indices_clima/oni.ascii.txt", sep=r"\s+")
ONI = oni[oni.SEAS == "ASO"].set_index("YR").ANOM
ONI_T = {a: float(ONI.loc[a - 1]) for a in ANOS}


def leitura(m, d, tipo, anos=ANOS):
    """razao ao normal (mediana dos outros anos) por ano x municipio de uma leitura de chuva no portao (m, d)."""
    res = {}
    for a in anos:
        g = pd.Timestamp(a, m, d)
        if tipo == "W1":
            x = chuva.loc[f"{a}-01-01":g].sum()
        elif tipo == "W2":
            x = chuva.loc[f"{a}-02-01":g].sum()
        elif tipo == "R30":
            x = chuva.loc[g - pd.Timedelta(days=29):g].sum()
        elif tipo == "R15":
            x = chuva.loc[g - pd.Timedelta(days=14):g].sum()
        elif tipo == "API":
            sl = chuva.loc[f"{a}-01-01":g]
            w = np.exp(-(len(sl) - 1 - np.arange(len(sl))) / TAU)[:, None]
            x = pd.Series((sl.values * w).sum(0), index=sl.columns)
        res[a] = x
    ac = pd.DataFrame(res).T
    o = ac * np.nan
    for a in anos:
        o.loc[a] = ac.loc[a] / ac.drop(index=a).median().replace(0, np.nan)
    s = o.stack().rename(tipo).reset_index()
    s.columns = ["ano", "cod", tipo]
    return s


def smap7(m, d, anos=ERA2):
    li = []
    for a in anos:
        t = pd.Timestamp(a, m, d)
        li.append(pd.DataFrame({"ano": a, "cod": PC.columns, "S7": PC.loc[t - pd.Timedelta(days=6):t].mean().values}))
    return pd.concat(li)


def auc(y, s):
    return roc_auc_score(y, s) if y.nunique() == 2 else np.nan


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            num += npos * nneg * roc_auc_score(g.quebra, g[col])
            den += npos * nneg
    return num / den if den else np.nan


def ic_auc(df, col, nb=1000):
    yrs = df.ano.unique()
    g = {a: df[df.ano == a] for a in yrs}
    bs = []
    for _ in range(nb):
        bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            bs.append(roc_auc_score(bb.quebra, bb[col]))
    return np.percentile(bs, [5, 95])


def nivel_ano(df, luz):
    t = df.assign(luz=luz.astype(int)).groupby("ano").agg(q=("quebra", "mean"), l=("luz", "mean"))
    r, p = stats.spearmanr(t.l, t.q)
    return r, p, t


GATES = {"31/jan": (1, 31), "28/fev": (2, 28), "19/mar": (3, 19), "31/mar": (3, 31), "30/abr": (4, 30)}
CH = ["W1", "W2", "API", "R30", "R15"]
PAIN = {}
for gn, (m, d) in GATES.items():
    df = base.copy()
    for t in CH:
        if t == "W2" and m == 1:
            continue
        df = df.merge(leitura(m, d, t), on=["ano", "cod"], how="left")
    df["ONI"] = df.ano.map(ONI_T)
    PAIN[gn] = df
out(f"[{time.time() - t0:.0f}s] paineis por portao montados; n municipio-anos de milho = {len(base)} ({base.quebra.sum()} quebras)")

# ================================================================== A
out("\n" + "=" * 22, "A. Curvas por ERA nos 5 portoes (AUC agrupada | Spearman entre anos da fracao com luz x fracao em quebra)", "=" * 22)
out("   score = -leitura (chuva em razao ao normal, cortada em 3); luz = leitura < 0,75; ONI = ONI ASO do ano anterior (score +ONI)")
TAB_A = []
for gn, (m, d) in GATES.items():
    df = PAIN[gn]
    for t in CH + ["ONI"]:
        if t not in df.columns:
            continue
        for era_n, era in [("1998-2015", ERA1), ("2016-2025", ERA2), ("1998-2025", ANOS)]:
            x = df[df.ano.isin(era)].dropna(subset=[t])
            s = x[t] if t == "ONI" else -x[t].clip(upper=3)
            a_ = auc(x.quebra, s)
            if t == "ONI":
                r = np.nan
            else:
                r, _, _ = nivel_ano(x, x[t] < 0.75)
            TAB_A.append((gn, t, era_n, a_, r))
    if m >= 2:
        sm = df[df.ano.isin(ERA2)].merge(smap7(m, d), on=["ano", "cod"]).dropna(subset=["S7"])
        a_ = auc(sm.quebra, -sm.S7)
        r, _, _ = nivel_ano(sm, sm.S7 < 20)
        TAB_A.append((gn, "SMAP7", "2016-2025", a_, r))
TA = pd.DataFrame(TAB_A, columns=["portao", "leitura", "era", "auc", "rho_ano"])
piv = TA.pivot_table(index=["leitura"], columns=["portao", "era"], values="auc").reindex(columns=list(GATES), level=0)
out("  AUC agrupada:")
out(piv.round(2).to_string())
piv2 = TA.pivot_table(index=["leitura"], columns=["portao", "era"], values="rho_ano").reindex(columns=list(GATES), level=0)
out("  Spearman entre anos (fracao de municipios com luz x fracao em quebra):")
out(piv2.round(2).to_string())

out("\n  A2. Fracao de municipios com luz, por ano (chuva < 0,75 do normal; SMAP 7d < 20) e fracao em quebra:")
for gn in ["19/mar", "30/abr"]:
    m, d = GATES[gn]
    df = PAIN[gn].merge(smap7(m, d, ANOS[18:]), on=["ano", "cod"], how="left")
    tb = df.assign(W1l=df.W1 < 0.75, W2l=df.W2 < 0.75, APIl=df.API < 0.75,
                   Sl=np.where(df.S7.notna(), df.S7 < 20, np.nan)).groupby("ano")[["quebra", "W1l", "W2l", "APIl", "Sl"]].mean()
    out(f"   [{gn}]")
    out("    " + tb.round(2).T.to_string().replace("\n", "\n    "))

# ================================================================== B
out("\n" + "=" * 22, "B. Escolha pre-declarada (R1): maior AUC MINIMA em {19/mar, 30/abr} x {1998-2015, 2016-2025}", "=" * 22)
sel = TA[TA.portao.isin(["19/mar", "30/abr"]) & TA.era.isin(["1998-2015", "2016-2025"]) & TA.leitura.isin(CH)]
mm = sel.groupby("leitura").auc.agg(["min", "mean"]).sort_values("min", ascending=False)
out(mm.round(3).to_string())
ordem_simples = ["W1", "W2", "R30", "R15", "API"]
topo = mm["min"].max()
cand = [c for c in ordem_simples if c in mm.index and mm.loc[c, "min"] >= topo - 0.01]
ESC = cand[0]
out(f"  maior minimo = {topo:.3f}; candidatos dentro de 0,01: {cand}; ESCOLHIDA (regra R1): {ESC}")

REGRA = f"""QUADRA - regra de alerta congelada para a quadra de 2027 (fechamento da rodada 2, 14/11/2026)
Luz principal (IMERG, NASA GPM): chuva IMERG V07 de 1/fev ate o portao < 75% do normal do municipio, normal = mediana
  das quadras 1998-2026 (todas menos a do ano). Portoes: 19/mar (Checkpoint Sao Jose, ultima troca) e 30/abr (salvar).
  Leitura descritiva extra so em ano de ONI ASO >= 1,5: 10/mar (decisao do caupi ate ~11/mar), sem habilidade medida.
Segunda missao (SMAP L4 SPL4SMGP): percentil da zona da raiz < 20, media dos 7 dias ate o portao (percentil do produto;
  se vazio, nao le). Papel: confirma ou nao a luz principal; nunca acende sozinha o vermelho.
Estados: VERMELHO = luz principal E SMAP; AMARELO = so a luz principal; CINZA-AMARELO = so o SMAP ("instrumentos discordam;
  o tecnico decide"); VERDE = nenhuma.
Juiz: quebra canonica do milho no IBGE PAM 2027 (producao / area plantada < 50% da mediana dos outros anos), publicada em 2028.
Placar a publicar: por ano (fracao de municipios com luz x fracao em quebra) e P(quebra | estado), com o n.
Limiares fixados antes dos testes: 75% (rodada 1, regra canonica W1) e 20 (secao 05, commit 48a3608, 14/11 08:34).
A escolha de W2 e do papel do SMAP foi feita DEPOIS de ver 2016-2025 (criterio R1 deste script). Grau B."""
H = hashlib.sha256(REGRA.encode("utf-8")).hexdigest()
out("  Texto congelado da regra de 2027:")
for ln in REGRA.splitlines():
    out("   | " + ln)
out(f"  sha256 (interno; publicar so com o OK do Jose) = {H}")

# ================================================================== C
out("\n" + "=" * 22, "C. 2016 no NIVEL DO ANO, mesmo numero de alarmes, duas missoes (2016-2025)", "=" * 22)
for gn in ["19/mar", "30/abr"]:
    m, d = GATES[gn]
    df = PAIN[gn][PAIN[gn].ano.isin(ERA2)].merge(smap7(m, d), on=["ano", "cod"]).dropna(subset=["W1", "W2", "S7"])
    df["lW1"], df["lW2"], df["lS"] = df.W1 < 0.75, df.W2 < 0.75, df.S7 < 20
    out(f"  [{gn}] n = {len(df)} municipio-anos, {df.quebra.sum()} quebras")
    for a in [2016, 2021, 2022, 2025]:
        g = df[df.ano == a]
        nq, n = g.quebra.sum(), len(g)
        txt = []
        for c, nm in [("lW1", "chuva 1/jan"), ("lW2", "chuva 1/fev"), ("lS", "SMAP 7d")]:
            k = g[c].sum()
            hit = (g[c] & (g.quebra == 1)).sum()
            txt.append(f"{nm}: luz em {k}/{n} ({k / n:.0%}), pega {hit}/{nq}, acaso {k * nq / n:.1f}")
        sc = {"W1": auc(g.quebra, -g.W1.clip(upper=3)), "W2": auc(g.quebra, -g.W2.clip(upper=3)), "S7": auc(g.quebra, -g.S7)}
        out(f"    {a}: quebra {nq}/{n} ({nq / n:.0%}) | " + " | ".join(txt))
        out(f"          AUC dentro do ano: chuva 1/jan {sc['W1']:.3f} | chuva 1/fev {sc['W2']:.3f} | SMAP 7d {sc['S7']:.3f}")
    # mesmo numero de alarmes da luz W2 em 10 quadras: W1 com limiar casado (sem rotulo, so pela taxa)
    taxa = df.lW2.mean()
    lim = df.W1.quantile(taxa)
    lw1c = df.W1 <= lim
    out(f"    mesma taxa de alerta que a chuva 1/fev ({taxa:.1%}): chuva 1/jan <= {lim:.2f} do normal pega em 2016 "
        f"{(lw1c & (df.quebra == 1))[df.ano == 2016].sum()}/127 (alertas {lw1c[df.ano == 2016].sum()}), em 2021 {lw1c[df.ano == 2021].sum()} alertas")
    # duas missoes
    est = np.select([df.lW2 & df.lS, df.lW2 & ~df.lS, ~df.lW2 & df.lS], ["vermelho (W2 e SMAP)", "amarelo (so W2)", "so SMAP"], "verde")
    tb = df.assign(estado=est).groupby("estado").agg(n=("quebra", "size"), quebram=("quebra", "mean"))
    tb["anos_com_estado"] = df.assign(estado=est).groupby("estado").ano.nunique()
    out("    estados de duas missoes:")
    out("      " + tb.round(2).to_string().replace("\n", "\n      "))
    r, p, t = nivel_ano(df, df.lW2 & df.lS)
    r2, p2, _ = nivel_ano(df, df.lW2)
    out(f"    Spearman entre anos: vermelho {r:+.2f} (p {p:.3f}) | luz 1/fev {r2:+.2f} (p {p2:.3f}) (n = 10)")

out("\n  Leitura descritiva de 10/mar (nao e portao validado), fracao de municipios com chuva 1/fev < 75% e quebra observada:")
d10 = base.merge(leitura(3, 10, "W2"), on=["ano", "cod"]).merge(leitura(3, 10, "W1"), on=["ano", "cod"])
t10 = d10.assign(l2=d10.W2 < 0.75, l1=d10.W1 < 0.75).groupby("ano").agg(quebra=("quebra", "mean"), luz_1fev=("l2", "mean"), luz_1jan=("l1", "mean"))
t10["ONI_ASO_ant"] = [ONI_T[a] for a in t10.index]
out("    " + t10.loc[[1998, 2010, 2012, 2016, 2024, 2025]].round(2).to_string().replace("\n", "\n    "))
out(f"    anos com ONI ASO >= 1,5 na era IMERG: {[a for a in ANOS if ONI_T[a] >= 1.5]}")

# ================================================================== D
out("\n" + "=" * 22, "D. Placar de Quixada (milho, quebra canonica)", "=" * 22)
qx = base[base.cod == QX].set_index("ano")
out(f"  quebras de Quixada: {sorted(qx.index[qx.quebra == 1].tolist())} ({qx.quebra.sum()} em {len(qx)})")
for gn in ["19/mar", "30/abr"]:
    df = PAIN[gn][PAIN[gn].cod == QX].set_index("ano")
    for t in ["W1", "W2"]:
        al = df.index[df[t] < 0.75].tolist()
        hit = [a for a in al if df.loc[a, "quebra"] == 1]
        perd = [a for a in df.index if df.loc[a, "quebra"] == 1 and a not in al]
        out(f"  [{gn}] chuva {'1/jan' if t == 'W1' else '1/fev'} < 75% (1998-2025): {len(al)} alertas {al}, {len(hit)} acertos {hit}; quebras sem alerta {perd}")
    out(f"  [{gn}] valores da chuva 1/fev em Quixada: " + ", ".join(f"{a}: {df.loc[a, 'W2']:.3f}" for a in [1998, 2012, 2016, 2018, 2021, 2022, 2023, 2024, 2025] if a in df.index))

# ================================================================== E
out("\n" + "=" * 22, "E. Contrafactual do caupi guardado (balde FAO-56 da rodada 1, copiado de v2_agronomo_smap_janelas.py), grau C", "=" * 22)
cods = list(chuva.columns)
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["codarea"] = mun.codarea.astype(str)
mun["pt"] = mun.geometry.representative_point()
mun = mun.set_index("codarea").loc[cods]
e0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"].load()
et0 = pd.DataFrame({c: e0.sel(lat=mun.loc[c, "pt"].y, lon=mun.loc[c, "pt"].x, method="nearest").to_series() for c in cods})
SEAS = ANOS
ND = 300
chB = pd.read_parquet(A + "saidas/chuva_mun_diaria.parquet")
chB.columns = chB.columns.astype(str)
R = np.zeros((len(cods), len(SEAS), ND), np.float32)
E = np.zeros_like(R)
for j, a in enumerate(SEAS):
    idx = pd.date_range(f"{a}-01-01", periods=ND, freq="D")
    R[:, j, :] = chB.reindex(idx)[cods].fillna(0).values.T
    E[:, j, :] = et0.reindex(idx)[cods].interpolate().bfill().values.T
CULT = {"milho": (20, 30, 35, 25, 0.30, 1.20, 0.35, 0.6, 0.55), "caupi": (15, 20, 25, 15, 0.40, 1.05, 0.35, 0.5, 0.45),
        "sorgo": (20, 30, 40, 25, 0.30, 1.05, 0.55, 0.8, 0.55)}
AWC = 100.0


def kc_curve(c):
    li, ld, lm, ll, ki, km, ke, _, _ = CULT[c]
    k = np.concatenate([np.full(li, ki), np.linspace(ki, km, ld), np.full(lm, km), np.linspace(km, ke, ll)])
    mid = np.zeros(len(k), bool)
    mid[li + ld:li + ld + lm] = True
    return k.astype(np.float32), mid


def simular(c, sow):
    kc, mid = kc_curve(c)
    L = len(kc)
    taw = AWC * CULT[c][7]
    raw = CULT[c][8] * taw
    Dr = np.full(sow.shape, taw, np.float32)
    eta_m = np.zeros(sow.shape, np.float32)
    etc_m = np.zeros_like(eta_m)
    for d in range(ND):
        k = d - sow
        P = R[:, :, d]
        e = E[:, :, d]
        dentro = (k >= 0) & (k < L)
        kci = np.where(dentro, kc[np.clip(k, 0, L - 1)], 0.0)
        ks = np.where(Dr <= raw, 1.0, np.clip((taw - Dr) / (taw - raw), 0, 1))
        kbare = 0.3 * np.clip((taw - Dr) / taw, 0, 1)
        etc = kci * e
        eta = np.where(dentro, ks * etc, kbare * e)
        Dr = np.clip(Dr - P + eta, 0, taw)
        ism = dentro & mid[np.clip(k, 0, L - 1)]
        eta_m += np.where(ism, eta, 0)
        etc_m += np.where(ism, etc, 0)
    return eta_m / np.maximum(etc_m, 1e-6)


DEC = {"01/mar": 59, "11/mar": 69, "21/mar": 79}
OK = {}
for c, dd in [("caupi", "11/mar"), ("caupi", "21/mar"), ("sorgo", "11/mar")]:
    OK[(c, dd)] = simular(c, np.full((len(cods), len(SEAS)), DEC[dd])) >= 0.5
j16 = SEAS.index(2016)
out(f"  conferencia com o agronomo (2016, balde): caupi 11/mar {OK[('caupi', '11/mar')][:, j16].mean():.0%} (agronomo 68%) | "
    f"caupi 21/mar {OK[('caupi', '21/mar')][:, j16].mean():.0%} (33%) | sorgo 11/mar {OK[('sorgo', '11/mar')][:, j16].mean():.0%} (10%)")
isna = pd.read_parquet(A + "saidas/agronomo_isna_mun_ano.parquet")
isna["cod"] = isna.cod.astype(str)
mil1 = isna.pivot(index="cod", columns="ano", values="isna_flor_milho").reindex(index=cods, columns=SEAS)
qtab = base.pivot(index="cod", columns="ano", values="quebra").reindex(index=cods, columns=SEAS)
iq = cods.index(QX)
out("  por quadra: fracao de municipios com agua na floracao (ISNA floracao >= 0,5) e quebra observada do milho (IBGE)")
linhas = []
for j, a in enumerate(SEAS):
    linhas.append({"ano": a, "ONI_ASO_ant": ONI_T[a], "milho_1a_chuva_balde": np.nanmean(mil1[a].values >= 0.5),
                   "milho_nao_quebrou_IBGE": 1 - np.nanmean(qtab[a].values), "caupi_11mar": OK[("caupi", "11/mar")][:, j].mean(),
                   "caupi_21mar": OK[("caupi", "21/mar")][:, j].mean(), "sorgo_11mar": OK[("sorgo", "11/mar")][:, j].mean(),
                   "QX_milho_IBGE": qtab.loc[QX, a], "QX_caupi11": int(OK[("caupi", "11/mar")][iq, j]),
                   "QX_caupi21": int(OK[("caupi", "21/mar")][iq, j])})
TE = pd.DataFrame(linhas).set_index("ano")
out("    " + TE.loc[[1998, 2001, 2010, 2012, 2016, 2024, 2025]].round(2).to_string().replace("\n", "\n    "))
norm = [a for a in SEAS if a not in (1998, 2001, 2010, 2012, 2013, 2015, 2016, 2024, 2025)]
out(f"    demais anos ({len(norm)}): caupi 11/mar {TE.loc[norm, 'caupi_11mar'].mean():.0%} | caupi 21/mar {TE.loc[norm, 'caupi_21mar'].mean():.0%} | "
    f"milho 1a chuva balde {TE.loc[norm, 'milho_1a_chuva_balde'].mean():.0%} | milho nao quebrou (IBGE) {TE.loc[norm, 'milho_nao_quebrou_IBGE'].mean():.0%}")
out("    Leitura: milho_1a_chuva_balde e o ISNA de cultura semeada na 1a chuva (rodada 1), que NAO ve 1998; por isso o observado do IBGE vai ao lado.")

# ================================================================== F
out("\n" + "=" * 22, "F. Carteira 1/3 x pratica atual (milho+feijao) nos anos em que a luz NASA acendeu (1998-2025)", "=" * 22)
Y = pd.DataFrame({"milho": MILHO, "feijao": FEIJ, "mandioca": MAND}).dropna().reset_index()
Y["S0"] = Y[["milho", "feijao"]].mean(1)
Y["S2"] = Y[["milho", "feijao", "mandioca"]].mean(1)


def cvar(s):
    s = pd.Series(s).dropna()
    return s[s <= s.quantile(0.10)].mean()


out(f"  n = {len(Y)} municipio-anos com as 3 culturas | todos: milho {cvar(Y.milho):.3f} | S0 milho+feijao {cvar(Y.S0):.3f} | 1/3 {cvar(Y.S2):.3f}")
for gn in ["19/mar", "30/abr"]:
    m, d = GATES[gn]
    yy = Y.merge(PAIN[gn][["cod", "ano", "W1", "W2"]], on=["cod", "ano"], how="inner").dropna(subset=["W2"])
    for t in ["W2", "W1"]:
        lit = yy[yy[t] < 0.75]
        nl = yy[yy[t] >= 0.75]
        yrs = lit.ano.unique()
        g = {a: lit[lit.ano == a] for a in yrs}
        bs = []
        for _ in range(1000):
            bb = pd.concat([g[a] for a in rng.choice(yrs, len(yrs))])
            bs.append([cvar(bb.S2) - cvar(bb.S0), cvar(bb.S2) - cvar(bb.milho)])
        bs = np.array(bs)
        out(f"  [{gn}] luz chuva {'1/fev' if t == 'W2' else '1/jan'} ACESA (n = {len(lit)}, {len(yrs)} anos): media milho {lit.milho.mean():.2f} | S0 {lit.S0.mean():.2f} | 1/3 {lit.S2.mean():.2f}"
            f" || CVaR10 milho {cvar(lit.milho):.3f} | S0 {cvar(lit.S0):.3f} | 1/3 {cvar(lit.S2):.3f} | 1/3 - S0 IC90 por ano [{np.percentile(bs[:, 0], 5):+.3f}, {np.percentile(bs[:, 0], 95):+.3f}]"
            f" | 1/3 - milho [{np.percentile(bs[:, 1], 5):+.3f}, {np.percentile(bs[:, 1], 95):+.3f}]")
        out(f"           luz APAGADA (n = {len(nl)}): media milho {nl.milho.mean():.2f} | S0 {nl.S0.mean():.2f} | 1/3 {nl.S2.mean():.2f} || CVaR10 milho {cvar(nl.milho):.3f} | S0 {cvar(nl.S0):.3f} | 1/3 {cvar(nl.S2):.3f}")

# ================================================================== G
out("\n" + "=" * 22, "G. Quixada, S0 observado (IBGE, razao canonica)", "=" * 22)
qm = MILHO.xs(QX, level="cod")
qf = FEIJ.xs(QX, level="cod")
s0 = pd.concat([qm, qf], axis=1, keys=["m", "f"]).dropna()
s0v = s0.mean(1)
out(f"  so milho ({len(qm)} anos): P(<0,5) {(qm < 0.5).mean():.3f} ({(qm < 0.5).sum()} anos) | pior ano em 10 {cvar(qm):.3f} | mediana {qm.median():.3f}")
out(f"  S0 milho+feijao ({len(s0v)} anos): P(<0,5) {(s0v < 0.5).mean():.3f} ({(s0v < 0.5).sum()} anos: {sorted(s0v.index[s0v < 0.5].tolist())}) | "
    f"pior ano em 10 {cvar(s0v):.3f} (anos {sorted(s0v.index[s0v <= s0v.quantile(0.1)].tolist())}) | mediana {s0v.median():.3f}")

# ================================================================== H
out("\n" + "=" * 22, "H. SMAP L3 CONSOLIDADO (observacao do radiometro) nos portoes 2016-2025", "=" * 22)
l3 = xr.open_dataset("E:/campeonato-nasa/dados/smap/smap_l3_diario_ne.nc")
tt = pd.to_datetime(l3.time.values)
out(f"  L3: {len(tt)} dias ({tt.min():%Y-%m-%d} -> {tt.max():%Y-%m-%d}); datas duplicadas: {tt.duplicated().sum()} (fica a primeira)")
l3 = l3.isel(time=np.flatnonzero(~tt.duplicated())).sel(lat=slice(-2.5, -8.1), lon=slice(-41.6, -37.0))
lo, la = np.meshgrid(l3.lon.values, l3.lat.values)
mg = municipios_ce_gdf()
mg["cod"] = mg.codarea.astype(str)
Wm = np.zeros((len(mg), lo.size))
for i, gg in enumerate(mg.geometry):
    mk = shapely.contains_xy(gg, lo, la).ravel()
    if mk.sum() == 0:
        c = gg.centroid
        mk = np.zeros(lo.size, bool)
        mk[np.argmin((lo.ravel() - c.x) ** 2 + (la.ravel() - c.y) ** 2)] = True
    Wm[i, mk] = 1.0 / mk.sum()
for gn in ["19/mar", "30/abr"]:
    m, d = GATES[gn]
    datas = [pd.Timestamp(a, m, d) - pd.Timedelta(days=k) for a in ERA2 for k in range(7)]
    _tl = set(pd.to_datetime(l3.time.values))
    datas = sorted(x for x in datas if x in _tl)
    sub = l3.sel(time=datas).load()
    a_, qa_, p_, qp_ = sub.sm_am.values, sub.qual_am.values, sub.sm_pm.values, sub.qual_pm.values
    am = np.where((a_ > 0) & (a_ < 1) & ((qa_ & 1) == 0), a_, np.nan)
    pm = np.where((p_ > 0) & (p_ < 1) & ((qp_ & 1) == 0), p_, np.nan)
    v = np.nanmean(np.stack([am, pm]), axis=0).reshape(len(datas), -1)
    ok = np.isfinite(v)
    agg = (np.where(ok, v, 0) @ Wm.T) / np.where((ok.astype(float) @ Wm.T) > 0, ok.astype(float) @ Wm.T, np.nan)
    L3 = pd.DataFrame(agg, index=pd.DatetimeIndex(datas), columns=mg.cod.values)
    g7 = pd.DataFrame({a: L3.loc[pd.Timestamp(a, m, d) - pd.Timedelta(days=6):pd.Timestamp(a, m, d)].mean() for a in ERA2}).T
    rr = pd.DataFrame({a: g7.loc[a] / g7.drop(index=a).median() for a in ERA2}).T
    s3 = rr.stack().rename("L3").reset_index()
    s3.columns = ["ano", "cod", "L3"]
    df = PAIN[gn][PAIN[gn].ano.isin(ERA2)].merge(smap7(m, d), on=["ano", "cod"]).merge(s3, on=["ano", "cod"]).dropna(subset=["W1", "W2", "S7", "L3"])
    for c in ["W1", "W2"]:
        df["s" + c] = -df[c].clip(upper=3)
    df["sS7"], df["sL3"] = -df.S7, -df.L3
    txt = []
    for c, nm in [("sW1", "chuva 1/jan"), ("sW2", "chuva 1/fev"), ("sS7", "SMAP L4 7d"), ("sL3", "SMAP L3 7d")]:
        lo_, hi_ = ic_auc(df, c, 600)
        yr = df.groupby("ano").agg(q=("quebra", "mean"), v=(c, "median"))
        rho = stats.spearmanr(yr.v, yr.q)[0]
        txt.append(f"{nm} {auc(df.quebra, df[c]):.3f} [{lo_:.2f},{hi_:.2f}] dentro {auc_dentro(df, c):.3f} rho_ano {rho:+.2f}")
    out(f"  [{gn}] n = {len(df)} ({df.quebra.sum()} quebras; dias L3 lidos {len(datas)}): " + " | ".join(txt))
    g16 = df[df.ano == 2016]
    out(f"     2016: L3 7d abaixo de 75% da mediana dos outros anos em {(g16.L3 < 0.75).sum()}/{len(g16)} municipios "
        f"(descritivo; o L3 nao tem limiar de luz); mediana do L3 em 2016 = {g16.L3.median():.2f} do normal")

# ================================================================== I
out("\n" + "=" * 22, "I. Contagem de palavras do roteiro novo do video (secao 11.2 da v2 corrigida)", "=" * 22)
ROT = ["March 19, 2016, the last day to switch crops. NASA rain counted from January looked normal.",
       "Counted from February, it said dry everywhere. By April, NASA soil moisture agreed in half the state.",
       "Seven in ten counties lost their corn. A wet January hid a dry season.",
       "Today: a record El Niño. Buy cowpea seed, keep half the field for an early-March decision, don't burn.",
       "NASA evidence. The farmer decides."]
nw = [len(s.replace("—", " ").split()) for s in ROT]
out(f"  palavras por bloco: {nw}; total {sum(nw)} (teto 70; ~2,3-2,7 palavras/s -> {sum(nw) / 2.7:.0f}-{sum(nw) / 2.3:.0f} s)")

out(f"\n[{time.time() - t0:.0f}s] fim")
Path(SAIDA).write_text("\n".join(LIN), encoding="utf-8")
