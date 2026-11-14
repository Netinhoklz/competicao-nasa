"""Agronomo do semiarido - balanco hidrico por cultura (FAO-56) x rendimento real (IBGE PAM), Ceara 1998-2025.

Perguntas:
 A1. A agua que a CULTURA viu (ISNA = ETa/ETc do balanco FAO-56 com IMERG diario + ET0 do POWER, semeadura pela
     regra do agricultor) explica a quebra municipal de milho e feijao melhor que a chuva total de fev-mai e que
     os veranicos? (validacao deixando 1 ano inteiro de fora)
 A2. Existe um limiar de ISNA na floracao, calibrado com o PAM, a partir do qual a safra quebra?
 A3. "ZARC sintetico" global: com so IMERG + POWER, a probabilidade de ISNA ok por decendio de semeadura
     (milho x caupi x sorgo) gera a DATA-LIMITE de troca de cultura? E o risco municipal calculado assim
     ordena os municipios como a frequencia real de quebra no PAM?
 A4. Revezamento (relay): caupi semeado dentro do milho (+50 d) ou em sucessao (apos a colheita) tem agua?

Dados (todos locais):
 - chuva diaria municipal: conselho/analises/saidas/chuva_mun_diaria.parquet (IMERG V07 0,1 grau via POWER,
   media dos pixels com centro no municipio; gerado pelo pesquisador de IA a partir de dados/imerg/*.nc)
 - ET0 FAO-56 diaria: dados/power/power_ce_diario_et0.nc (celula mais proxima do municipio)
 - rendimento: dados/derivados/ibge_pam_mun_anual.parquet (producao / area PLANTADA, inclui perda de area)
Parametros de cultura: FAO-56 (Allen et al. 1998), tabelas 11/12/22, valores aproximados, sem ajuste de clima seco.
CAD do solo = 100 mm/m x profundidade de raiz (suposicao; o produto usaria HWSD/SoilGrids).
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
import xarray as xr
from scipy import stats
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)
OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")

ANOS = np.arange(1998, 2026)
ND = 304  # 1/jan a ~31/out

# ---------------------------------------------------------------- clima diario municipal
chuva = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["pt"] = mun.geometry.representative_point()
cods = [c for c in chuva.columns if c in set(mun.codarea)]
mun = mun.set_index("codarea").loc[cods]
e0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"].load()
et0 = {}
for c in cods:
    p = mun.loc[c, "pt"]
    et0[c] = e0.sel(lat=p.y, lon=p.x, method="nearest").to_series()
et0 = pd.DataFrame(et0)

NM = len(cods)
R = np.zeros((NM, len(ANOS), ND), np.float32)
E = np.zeros_like(R)
for j, a in enumerate(ANOS):
    idx = pd.date_range(f"{a}-01-01", periods=ND, freq="D")
    R[:, j, :] = chuva.reindex(idx)[cods].fillna(0).values.T
    E[:, j, :] = et0.reindex(idx)[cods].interpolate().bfill().values.T
print(f"clima: {NM} municipios x {len(ANOS)} anos x {ND} dias; chuva media jan-out {R.sum(2).mean():.0f} mm, "
      f"ET0 {E.sum(2).mean():.0f} mm")

# ---------------------------------------------------------------- culturas (FAO-56 aprox.)
CULT = {  # L_ini, L_dev, L_mid, L_late, Kc_ini, Kc_mid, Kc_end, Zr (m), p
    "milho": (20, 30, 35, 25, 0.30, 1.20, 0.35, 0.6, 0.55),   # ciclo 110 d
    "caupi": (15, 20, 25, 15, 0.40, 1.05, 0.35, 0.5, 0.45),   # ciclo 75 d (BRS de ciclo curto)
    "sorgo": (20, 30, 40, 25, 0.30, 1.05, 0.55, 0.8, 0.55),   # ciclo 115 d, raiz mais funda
}
AWC = 100.0  # mm/m


def kc_curve(c):
    li, ld, lm, ll, ki, km, ke, _, _ = CULT[c]
    k = np.concatenate([np.full(li, ki), np.linspace(ki, km, ld), np.full(lm, km), np.linspace(km, ke, ll)])
    mid = np.zeros(len(k), bool)
    mid[li + ld:li + ld + lm] = True
    return k.astype(np.float32), mid


def simular(c, sow):
    """sow: (NM, NA) dia de semeadura (indice desde 1/jan). Retorna ISNA ciclo, ISNA floracao, dias Ks<0,5 na floracao."""
    kc, mid = kc_curve(c)
    L = len(kc)
    taw = AWC * CULT[c][7]
    raw = CULT[c][8] * taw
    Dr = np.full(sow.shape, taw, np.float32)  # perfil seco em 1/jan
    eta_c = np.zeros(sow.shape, np.float32); etc_c = np.zeros_like(eta_c)
    eta_m = np.zeros_like(eta_c); etc_m = np.zeros_like(eta_c); st_m = np.zeros_like(eta_c)
    for d in range(ND):
        k = d - sow
        P = R[:, :, d]; e = E[:, :, d]
        dentro = (k >= 0) & (k < L)
        kci = np.where(dentro, kc[np.clip(k, 0, L - 1)], 0.0)
        ks = np.where(Dr <= raw, 1.0, np.clip((taw - Dr) / (taw - raw), 0, 1))
        # antes da semeadura / apos a colheita: evaporacao do solo nu, limitada pela secura
        kbare = 0.3 * np.clip((taw - Dr) / taw, 0, 1)
        etc = kci * e
        eta = np.where(dentro, ks * etc, kbare * e)
        Dr = np.clip(Dr - P + eta, 0, taw)
        eta_c += np.where(dentro, eta, 0); etc_c += etc
        ism = dentro & mid[np.clip(k, 0, L - 1)]
        eta_m += np.where(ism, eta, 0); etc_m += np.where(ism, etc, 0); st_m += (ism & (ks < 0.5))
    return eta_c / np.maximum(etc_c, 1e-6), eta_m / np.maximum(etc_m, 1e-6), st_m


# regra do agricultor (causal): 1o dia com >= 20 mm em 3 dias a partir de 1/jan; se nao vier ate 30/abr, planta em 30/abr
c3 = np.zeros_like(R); c3[:, :, 2:] = R[:, :, 2:] + R[:, :, 1:-1] + R[:, :, :-2]
ok = c3 >= 20
ok[:, :, :2] = False
ok[:, :, 120:] = False
sow_ag = np.where(ok.any(2), ok.argmax(2), 119)

# atributos de chuva (fev-mai = dias 31..150)
fm = R[:, :, 31:151]
P_fmam = fm.sum(2)
seco = fm <= 2.0


def corridas(b):
    """b: (..., T) booleano. Retorna n de corridas >= 3 d, dias nelas, maior corrida."""
    T = b.shape[-1]
    run = np.zeros(b.shape[:-1]); mx = np.zeros_like(run); n3 = np.zeros_like(run); d3 = np.zeros_like(run)
    for t in range(T):
        x = b[..., t]
        fim = (~x) & (run >= 3)
        n3 += fim; d3 += np.where(fim, run, 0)
        run = np.where(x, run + 1, 0)
        mx = np.maximum(mx, run)
    fim = run >= 3
    n3 += fim; d3 += np.where(fim, run, 0)
    return n3, d3, mx


n_ver, d_ver, ver_max = corridas(seco)

feat = []
ISN = {}
for c in CULT:
    ic, im, sm = simular(c, sow_ag)
    ISN[c] = (ic, im, sm)
for i, cod in enumerate(cods):
    for j, a in enumerate(ANOS):
        row = {"cod": cod, "ano": a, "P_fmam": P_fmam[i, j], "n_veranicos3": n_ver[i, j], "dias_veranico": d_ver[i, j],
               "veranico_max": ver_max[i, j], "semeadura_doy": sow_ag[i, j] + 1}
        for c in CULT:
            row[f"isna_ciclo_{c}"] = ISN[c][0][i, j]; row[f"isna_flor_{c}"] = ISN[c][1][i, j]
            row[f"estresse_flor_{c}"] = ISN[c][2][i, j]
        feat.append(row)
F = pd.DataFrame(feat)

# ---------------------------------------------------------------- rendimento PAM sem tendencia tecnologica
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.cod_local.str.startswith("23") & pam.ano.between(1996, 2025)]
PROD = {"Milho (em grão)": "milho", "Feijão (em grão)": "feijao", "Mandioca": "mandioca",
        "Castanha de caju": "caju", "Algodão herbáceo (em caroço)": "algodao"}
print("produtos encontrados:", [p for p in PROD if p in set(pam.produto)])
Y = []
for prod, nome in PROD.items():
    s = pam[pam.produto == prod].copy()
    s["rp"] = np.where(s.area_plantada_ha > 0, s.producao_t * 1000 / s.area_plantada_ha, np.nan)
    for cod, g in s.groupby("cod_local"):
        g = g.set_index("ano").sort_index()
        if g.loc[1998:2025, "area_plantada_ha"].mean() < (300 if nome in ("milho", "feijao") else 100):
            continue
        y = g["rp"].where(g["rp"] > 0)
        yy = y.loc[1998:2025].dropna()
        if len(yy) < 15:
            continue
        sl, ic, _, _ = stats.theilslopes(np.log(yy.values), yy.index.values)
        tend = np.exp(ic + sl * g.index.values)
        # producao zero com area plantada = perda total (anomalia -100%)
        rp0 = g["rp"].fillna(np.nan)
        an = rp0 / tend - 1
        for a, v in an.loc[1996:2025].items():
            if np.isfinite(v):
                Y.append({"cod": cod, "ano": a, "cultura": nome, "anom": v})
Y = pd.DataFrame(Y)
print("municipios por cultura:", Y.groupby("cultura").cod.nunique().to_dict())

# ================================================================ A1: o que explica a quebra?
print("\n=== A1. Quebra municipal x atributos (1998-2025; anomalia = rend/tendencia Theil-Sen - 1) ===")
MAPC = {"milho": "milho", "feijao": "caupi"}
res_a1 = []
for cult, cc in MAPC.items():
    D = Y[(Y.cultura == cult) & Y.ano.between(1998, 2025)].merge(F, on=["cod", "ano"])
    D = D.replace([np.inf, -np.inf], np.nan).dropna()
    print(f"\n{cult}: {len(D)} municipio-anos, {D.cod.nunique()} municipios")
    uni = {}
    for v in ["P_fmam", "n_veranicos3", "dias_veranico", "veranico_max", "semeadura_doy",
              f"isna_ciclo_{cc}", f"isna_flor_{cc}", f"estresse_flor_{cc}"]:
        uni[v] = stats.spearmanr(D[v], D.anom)[0]
    print("  Spearman univariado:", {k: round(v, 3) for k, v in uni.items()})
    conj = {
        "F0 chuva fev-mai": ["P_fmam"],
        "F1 +veranicos+semeadura": ["P_fmam", "n_veranicos3", "dias_veranico", "veranico_max", "semeadura_doy"],
        "F2 so ISNA da cultura": [f"isna_ciclo_{cc}", f"isna_flor_{cc}", f"estresse_flor_{cc}"],
        "F3 F1+ISNA": ["P_fmam", "n_veranicos3", "dias_veranico", "veranico_max", "semeadura_doy",
                       f"isna_ciclo_{cc}", f"isna_flor_{cc}", f"estresse_flor_{cc}"],
    }
    y = D.anom.clip(-1, 2).values
    for nome_c, cols in conj.items():
        X = D[cols].values
        for mod_nome, mk in [("ridge", lambda: make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 3, 20)))),
                             ("hgb", lambda: HistGradientBoostingRegressor(max_depth=3, max_iter=200, learning_rate=0.05,
                                                                            min_samples_leaf=40, random_state=0))]:
            pred = np.zeros(len(D))
            for a in ANOS:
                te = (D.ano == a).values
                if te.sum() == 0:
                    continue
                m = mk().fit(X[~te], y[~te])
                pred[te] = m.predict(X[te])
            r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
            # quebra severa: anomalia <= -50%
            from sklearn.metrics import roc_auc_score
            auc = roc_auc_score((y <= -0.5).astype(int), -pred)
            res_a1.append({"cultura": cult, "conjunto": nome_c, "modelo": mod_nome, "R2_LOYO": round(r2, 3),
                           "rho": round(stats.spearmanr(pred, y)[0], 3), "AUC_quebra50": round(auc, 3)})
A1 = pd.DataFrame(res_a1)
print(A1.to_string(index=False))

# ================================================================ A2: limiar de ISNA na floracao
print("\n=== A2. Rendimento x ISNA na floracao (semeadura do agricultor) ===")
bins = [0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.01]
for cult, cc in MAPC.items():
    D = Y[(Y.cultura == cult)].merge(F, on=["cod", "ano"])
    D["faixa"] = pd.cut(D[f"isna_flor_{cc}"], bins)
    T = D.groupby("faixa").anom.agg(n="size", mediana="median", p_quebra50=lambda s: (s <= -0.5).mean(),
                                    p_quebra30=lambda s: (s <= -0.3).mean())
    print(f"\n{cult} (ISNA floracao de {cc}):")
    print(T.round(3).to_string())

# mandioca e caju: chuva do ano x do ano anterior (memoria)
print("\n=== A2b. Culturas 'tampao': correlacao da anomalia com P_fmam do ano e do ano anterior ===")
Fl = F[["cod", "ano", "P_fmam"]].copy(); Fl["ano"] += 1; Fl = Fl.rename(columns={"P_fmam": "P_fmam_ant"})
for cult in ["milho", "feijao", "mandioca", "caju", "algodao"]:
    D = Y[Y.cultura == cult].merge(F[["cod", "ano", "P_fmam"]], on=["cod", "ano"]).merge(Fl, on=["cod", "ano"]).dropna()
    if len(D) < 50:
        continue
    r0 = stats.spearmanr(D.P_fmam, D.anom)[0]; r1 = stats.spearmanr(D.P_fmam_ant, D.anom)[0]
    seca = D.P_fmam <= D.groupby("cod").P_fmam.transform(lambda s: s.quantile(0.2))
    print(f"  {cult:9s} n={len(D):5d} mun={D.cod.nunique():3d}  rho(ano)={r0:+.2f}  rho(ano ant.)={r1:+.2f}  "
          f"anom. mediana nos 20% anos mais secos do municipio={D.anom[seca].median():+.2f}  "
          f"P(quebra>=50%) seco={(D.anom[seca] <= -0.5).mean():.2f}")

# ================================================================ A3: ZARC sintetico por decendio
print("\n=== A3. 'ZARC sintetico' (IMERG+POWER): P(ISNA floracao >= limiar) por decendio de semeadura ===")
DEC = {"01/jan": 0, "11/jan": 10, "21/jan": 20, "01/fev": 31, "11/fev": 41, "21/fev": 51, "01/mar": 59,
       "11/mar": 69, "21/mar": 79, "01/abr": 90, "11/abr": 100, "21/abr": 110}
LIM = 0.5
prob = {}
for c in CULT:
    for dn, dd in DEC.items():
        _, im, _ = simular(c, np.full((NM, len(ANOS)), dd))
        prob[(c, dn)] = (im >= LIM).mean(1)  # por municipio
PB = pd.DataFrame(prob, index=cods)
est = PB.median().unstack(0)[list(CULT)].loc[list(DEC)]
print(f"mediana estadual de P(ISNA flor >= {LIM}):")
print(est.round(2).to_string())
nomes = {str(x["id"]): x["nome"] for x in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}
EX = {n: c for c, n in nomes.items() if n in ("Quixadá", "Crato", "Tianguá", "Tauá", "Iguatu", "Sobral", "Itapipoca")}
for n, c in EX.items():
    if c in PB.index:
        print(f"\n{n} ({c}):")
        print(PB.loc[c].unstack(0)[list(CULT)].loc[list(DEC)].round(2).T.to_string())


def data_limite(serie, alvo=0.7):
    """ultimo decendio (em sequencia a partir do melhor) com P >= alvo (risco <= 30%)."""
    oks = [d for d in DEC if serie[d] >= alvo]
    return oks[-1] if oks else "nenhum"


DL = pd.DataFrame({c: [data_limite(PB.loc[m].unstack(0)[c]) for m in cods] for c in CULT}, index=cods)
print("\nDistribuicao do ultimo decendio com risco <= 30% (n de municipios):")
for c in CULT:
    print(f"  {c}: {DL[c].value_counts().reindex(list(DEC) + ['nenhum']).fillna(0).astype(int).to_dict()}")
for n, c in EX.items():
    if c in DL.index:
        print(f"  {n}: {DL.loc[c].to_dict()}")

# validacao: risco sintetico do milho (semeadura do agricultor) x frequencia real de quebra no PAM
print("\n=== A3b. Validacao entre municipios: risco sintetico x quebra real (milho e feijao) ===")
for cult, cc in MAPC.items():
    D = Y[(Y.cultura == cult) & Y.ano.between(1998, 2025)].merge(F, on=["cod", "ano"])
    G = D.groupby("cod").agg(risco_sint=(f"isna_flor_{cc}", lambda s: (s < LIM).mean()),
                             quebra_real=("anom", lambda s: (s <= -0.5).mean()), n=("anom", "size"))
    G = G[G.n >= 20]
    r, p = stats.spearmanr(G.risco_sint, G.quebra_real)
    # tambem com o risco por decendio fixo de 21/jan (sem regra do agricultor)
    G["risco_dec"] = 1 - PB.loc[G.index, (cc, "21/jan")]
    r2_, p2_ = stats.spearmanr(G.risco_dec, G.quebra_real)
    print(f"  {cult}: {len(G)} municipios; rho(risco ISNA agricultor, freq. quebra>=50%)={r:+.2f} (p={p:.1e}); "
          f"rho(risco 21/jan, quebra)={r2_:+.2f} (p={p2_:.1e}); quebra real media={G.quebra_real.mean():.2f}, "
          f"risco sintetico medio={G.risco_sint.mean():.2f}")
    # concordancia anual: fracao de municipios com quebra x com ISNA<lim
    A = D.groupby("ano").agg(frac_quebra=("anom", lambda s: (s <= -0.5).mean()),
                             frac_isna=(f"isna_flor_{cc}", lambda s: (s < LIM).mean()))
    print(f"     por ano (estado): r(frac. municipios ISNA<{LIM}, frac. com quebra) = {A.corr().iloc[0, 1]:+.2f}; "
          f"2012: ISNA<lim em {A.loc[2012, 'frac_isna']:.0%} dos mun., quebra em {A.loc[2012, 'frac_quebra']:.0%}")

# ================================================================ A4: revezamento / sucessao do caupi
print("\n=== A4. Segunda cultura na mesma quadra: caupi em revezamento (+50 d no milho) ou sucessao (+110 d) ===")
for nome_s, desl in [("caupi junto (consorcio, dia 0)", 0), ("caupi revezamento (+50 d)", 50), ("caupi sucessao (+110 d)", 110)]:
    s = np.minimum(sow_ag + desl, ND - 80)
    _, im, _ = simular("caupi", s)
    pm = (im >= LIM).mean(1)
    print(f"  {nome_s}: P(ISNA flor >= {LIM}) mediana estadual={np.median(pm):.2f}; "
          f"municipios com P>=0,7: {(pm >= 0.7).sum()} de {NM}; P90 municipal={np.quantile(pm, 0.9):.2f}")
    for n, c in EX.items():
        if c in cods:
            print(f"      {n}: {pm[cods.index(c)]:.2f}", end="")
    print()

F.to_parquet(OUT / "agronomo_isna_mun_ano.parquet")
PB2 = PB.copy(); PB2.columns = [f"{c}|{d}" for c, d in PB.columns]; PB2.index.name = "cod"
PB2.to_parquet(OUT / "agronomo_zarc_sintetico_prob.parquet")
print("\nsalvo: saidas/agronomo_isna_mun_ano.parquet e agronomo_zarc_sintetico_prob.parquet")
