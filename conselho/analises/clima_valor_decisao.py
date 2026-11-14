"""Cientista do clima - Analise 3: a previsao probabilistica PAGA a troca de rotacao? E quando decidir?

Modelo custo-perda (cost-loss): o agricultor pode "proteger" (trocar milho+feijao pela rotacao tolerante a seca,
custo C em ano normal) ou nao (perda L se vier o evento). Valor economico relativo:
   V = (E_clim - E_prev) / (E_clim - E_perfeito), com E em unidades de L e alfa = C/L.
   V = 1 -> tao bom quanto saber o futuro; V = 0 -> igual a usar so a climatologia; V < 0 -> atrapalha.
Eventos: E1 = quadra no tercil seco (chuva POWER); E2 = quebra do milho (rendimento <= -30% da tendencia, IBGE PAM);
         E3 = quebra do feijao (<= -30%).
Previsoes: probabilidades LOO da analise 1 (clima_probs_loo.pkl) em t0 (15/nov), t1 (01/fev), t2 (16/fev), t3 (16/mar).
Tambem: habilidade condicionada a ENSO forte (|ONI ASO| >= 1) e analogos de ONI ASO extremo (inclui 1960-1980 pela
chuva anual do GAEZ/CRU como proxy).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
SAIDA = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas"
probs = pd.read_pickle(SAIDA + "/clima_probs_loo.pkl")
T = pd.read_parquet(SAIDA + "/clima_tabela_progressiva.parquet")

# ---------------- eventos de quebra (PAM) ----------------
pam = pd.read_parquet(DERIV / "ibge_pam_ce_anual.parquet")
pam["ano"] = pam.data.dt.year
rend = pam[pam.variavel == "rendimento_kg_ha"].pivot_table(index="ano", columns="produto", values="valor")
anom = rend / rend.rolling(9, center=True, min_periods=5).median() - 1
quebra_milho = (anom["Milho (em grão)"] <= -0.30)
quebra_feijao = (anom["Feijão (em grão)"] <= -0.30)


def valor_relativo(p, o, alfas):
    """p: prob prevista do evento; o: 0/1 observado. Envelope sobre limiares de decisao."""
    p, o = np.asarray(p), np.asarray(o).astype(bool)
    s = o.mean()
    out = []
    for a in alfas:
        e_clim = min(a, s)
        e_perf = s * a
        melhor = -np.inf
        for th in np.unique(np.r_[p, 1.01]):
            prot = p >= th
            e = np.mean(np.where(prot, a, np.where(o, 1.0, 0.0)))
            v = (e_clim - e) / (e_clim - e_perf) if e_clim > e_perf else np.nan
            melhor = max(melhor, v)
        out.append(melhor)
    return np.array(out)


def h_f(p, o, th):
    p, o = np.asarray(p), np.asarray(o).astype(bool)
    prot = p >= th
    return prot[o].mean(), prot[~o].mean()


ALFAS = np.array([0.1, 0.2, 0.33, 0.5, 0.67])
mapa_etapa = {
    "t0 15/nov": "t0 15/nov ONI_ASO+DIP_JAS -> FMAM",
    "t1 01/fev": "t1 01/fev ONI_NDJ+DIP_DJ -> FMAM",
    "t2 16/fev": "t2 16/fev +1a chuva -> 16fev-mai",
    "t3 16/mar": "t3 16/mar +chuva jan-15mar -> 16mar-mai",
}
lin = []
rng = np.random.default_rng(42)
for rot, chave in mapa_etapa.items():
    P = probs[chave]
    anos = sorted(P)
    pdry = np.array([P[a][0] for a in anos])
    ev = {"E1 tercil seco": np.array([P[a][1] == 0 for a in anos]),
          "E2 quebra milho": quebra_milho.reindex(anos).fillna(False).values,
          "E3 quebra feijão": quebra_feijao.reindex(anos).fillna(False).values}
    for nome, o in ev.items():
        v = valor_relativo(pdry, o, ALFAS)
        # bootstrap do V em alfa = 0,33
        bs = []
        for _ in range(500):
            i = rng.integers(0, len(anos), len(anos))
            if o[i].sum() in (0, len(i)):
                continue
            bs.append(valor_relativo(pdry[i], o[i], [0.33])[0])
        H, F = h_f(pdry, o, 0.5)
        lin.append({"etapa": rot, "evento": nome, "taxa_base": round(o.mean(), 2),
                    **{f"V(α={a})": round(x, 2) for a, x in zip(ALFAS, v)},
                    "V0.33_IC90": f"[{np.nanpercentile(bs, 5):.2f}, {np.nanpercentile(bs, 95):.2f}]",
                    "acerto(P≥0,5)": round(H, 2), "alarme_falso(P≥0,5)": round(F, 2)})
V = pd.DataFrame(lin)
print("Valor econômico relativo (envelope sobre limiares) — 1982–2025, previsões LOO:")
print(V.to_string(index=False))

# ---------------- habilidade condicionada a ENSO forte (t0) ----------------
P0 = probs[mapa_etapa["t0 15/nov"]]


def rps(p, k):
    o = np.eye(3)[k]
    return np.sum((np.cumsum(p) - np.cumsum(o)) ** 2) / 2


# precisamos das 3 probabilidades: refaz o LOO de t0 guardando o vetor completo
from sklearn.linear_model import LogisticRegression  # noqa
from sklearn.preprocessing import StandardScaler  # noqa
d = T.loc[:2025, ["ONI_ASO", "DIP_JAS", "alvo_FMAM", "ONI_NDJ", "DIP_DJ"]].dropna()


def loo_full(cols):
    out = {}
    for ano in d.index:
        tr = d.drop(ano)
        q1, q2 = tr.alvo_FMAM.quantile([1 / 3, 2 / 3])
        y = np.where(tr.alvo_FMAM <= q1, 0, np.where(tr.alvo_FMAM >= q2, 2, 1))
        k = int(0 if d.loc[ano, "alvo_FMAM"] <= q1 else (2 if d.loc[ano, "alvo_FMAM"] >= q2 else 1))
        sc = StandardScaler().fit(tr[cols])
        m = LogisticRegression(C=0.5, max_iter=2000).fit(sc.transform(tr[cols]), y)
        out[ano] = (m.predict_proba(sc.transform(d.loc[[ano], cols]))[0], k)
    return out


for rot, cols, filtro in [("t0", ["ONI_ASO", "DIP_JAS"], d.ONI_ASO.abs() >= 1.0),
                          ("t1", ["ONI_NDJ", "DIP_DJ"], d.ONI_NDJ.abs() >= 1.0)]:
    F = loo_full(cols)
    for nome, msk in [("|ONI| ≥ 1,0", filtro), ("|ONI| < 1,0", ~filtro)]:
        anos = d.index[msk]
        rm = np.mean([rps(F[a][0], F[a][1]) for a in anos]); rc = np.mean([rps(np.full(3, 1 / 3), F[a][1]) for a in anos])
        print(f"{rot} {nome}: n = {len(anos)}, RPSS = {1 - rm / rc:+.2f}, anos = {list(anos)}")

# ---------------- analogos de ONI ASO extremo, com proxy pre-1981 ----------------
I = pd.read_parquet(DERIV / "indices_clima_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
gz = pd.read_parquet(DERIV / "gaez_ce_lgp_chuva_anual_1960_2010.parquet")["chuva (mm)"]
gz_pct = gz.rank(pct=True)
fm = T.alvo_FMAM.dropna(); fm_pct = fm.rank(pct=True)
aso = I["ONI"][I["ONI"].index.month == 9]
print("\nAnálogos (ONI ASO ≥ 1,3) → quadra seguinte:")
for dt, v in aso[aso >= 1.3].sort_values(ascending=False).items():
    a = dt.year + 1
    dip = np.nanmean([I["DIPOLO_TNA_menos_TSA"].get(pd.Timestamp(a, m, 1), np.nan) for m in (2, 3, 4, 5)])
    txt = f"  ASO {dt.year} = {v:+.2f} → quadra {a}: dipolo fev–mai {dip:+.2f}"
    if a in fm.index:
        txt += f" | FMAM POWER {fm[a]:.0f} mm (percentil {fm_pct[a]:.0%})"
    if a in gz.index:
        txt += f" | chuva anual CRU/GAEZ {gz[a]:.0f} mm (percentil {gz_pct[a]:.0%})"
    if a in quebra_milho.index:
        txt += f" | milho {anom['Milho (em grão)'].get(a, np.nan):+.0%}"
    print(txt)
V.to_csv(SAIDA + "/clima_valor_relativo.csv", index=False)

# ---------------- versao honesta: limiar fixo = alfa (regra de Bayes), sem escolher limiar na amostra ----------------
def v_fixo(p, o, a):
    p, o = np.asarray(p), np.asarray(o).astype(bool)
    s = o.mean(); e_clim = min(a, s); e_perf = s * a
    e = np.mean(np.where(p >= a, a, np.where(o, 1.0, 0.0)))
    return (e_clim - e) / (e_clim - e_perf)


print("\nV com limiar fixo P >= alfa (sem otimizar o limiar):")
lin2 = []
for rot, chave in mapa_etapa.items():
    P = probs[chave]; anos = sorted(P); pdry = np.array([P[a][0] for a in anos])
    for nome, o in {"E1 tercil seco": np.array([P[a][1] == 0 for a in anos]),
                    "E2 quebra milho": quebra_milho.reindex(anos).fillna(False).values}.items():
        lin2.append({"etapa": rot, "evento": nome, **{f"V(α={a})": round(v_fixo(pdry, o, a), 2) for a in ALFAS}})
print(pd.DataFrame(lin2).to_string(index=False))
