"""Agronomo do semiarido - 2a analise: "calibrar a pratica do agricultor pelos dados" (modelagem inversa).

Perguntas:
 B1. Com que atraso, em relacao a 1a chuva de plantio (>= 20 mm em 3 dias), o feijao e o milho do PAM se comportam
     como se tivessem sido semeados? (o atraso que maximiza a correlacao ISNA x anomalia de rendimento)
 B2. Que capacidade de agua do solo (CAD) explica melhor a quebra do milho? (sensibilidade do balde)
 B3. O calor na floracao (dias com Tmax acima do p90 local, POWER) explica a quebra que o balde nao ve (ex.: 2012)?
     Teste do modelo hibrido: fisica (ISNA) + calor + correcao por gradient boosting, validacao deixando 1 ano de fora.
 B4. Data-limite de troca de cultura com limiar ISNA 0,6 (o "joelho" da curva do PAM da analise A2).
Reaproveita o clima diario municipal e o balde FAO-56 de agronomo_isna_zarc_sintetico.py (mesmos parametros).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
from comum import *  # noqa

import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
ANOS = np.arange(1998, 2026)
ND = 304

chuva = pd.read_parquet(OUT / "chuva_mun_diaria.parquet")
mun = gpd.read_file(REF / "ceara_municipios.geojson")
mun["pt"] = mun.geometry.representative_point()
cods = [c for c in chuva.columns if c in set(mun.codarea)]
mun = mun.set_index("codarea").loc[cods]
e0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"].load()
tx = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")["T2M_MAX"].load()
et0, tmx = {}, {}
for c in cods:
    p = mun.loc[c, "pt"]
    et0[c] = e0.sel(lat=p.y, lon=p.x, method="nearest").to_series()
    tmx[c] = tx.sel(lat=p.y, lon=p.x, method="nearest").to_series()
et0 = pd.DataFrame(et0); tmx = pd.DataFrame(tmx)
NM = len(cods)
R = np.zeros((NM, len(ANOS), ND), np.float32); E = np.zeros_like(R); T = np.zeros_like(R)
for j, a in enumerate(ANOS):
    idx = pd.date_range(f"{a}-01-01", periods=ND, freq="D")
    R[:, j] = chuva.reindex(idx)[cods].fillna(0).values.T
    E[:, j] = et0.reindex(idx)[cods].interpolate().bfill().values.T
    T[:, j] = tmx.reindex(idx)[cods].interpolate().bfill().values.T
# p90 local da Tmax de fev-mai (por municipio, 1998-2025) -> limiar de calor relativo (evita o vies absoluto do POWER)
p90 = np.quantile(T[:, :, 31:151].reshape(NM, -1), 0.9, axis=1)[:, None, None]
QUENTE = T >= p90

CULT = {"milho": (20, 30, 35, 25, 0.30, 1.20, 0.35, 0.6, 0.55), "caupi": (15, 20, 25, 15, 0.40, 1.05, 0.35, 0.5, 0.45)}


def simular(c, sow, awc=100.0):
    li, ld, lm, ll, ki, km, ke, zr, pp = CULT[c]
    kc = np.concatenate([np.full(li, ki), np.linspace(ki, km, ld), np.full(lm, km), np.linspace(km, ke, ll)]).astype(np.float32)
    mid = np.zeros(len(kc), bool); mid[li + ld:li + ld + lm] = True
    L = len(kc); taw = awc * zr; raw = pp * taw
    Dr = np.full(sow.shape, taw, np.float32)
    eta_m = np.zeros(sow.shape, np.float32); etc_m = np.zeros_like(eta_m); calor = np.zeros_like(eta_m)
    for d in range(ND):
        k = d - sow
        dentro = (k >= 0) & (k < L)
        kci = np.where(dentro, kc[np.clip(k, 0, L - 1)], 0.0)
        ks = np.where(Dr <= raw, 1.0, np.clip((taw - Dr) / (taw - raw), 0, 1))
        etc = kci * E[:, :, d]
        eta = np.where(dentro, ks * etc, 0.3 * np.clip((taw - Dr) / taw, 0, 1) * E[:, :, d])
        Dr = np.clip(Dr - R[:, :, d] + eta, 0, taw)
        ism = dentro & mid[np.clip(k, 0, L - 1)]
        eta_m += np.where(ism, eta, 0); etc_m += np.where(ism, etc, 0); calor += ism & QUENTE[:, :, d]
    return eta_m / np.maximum(etc_m, 1e-6), calor


c3 = np.zeros_like(R); c3[:, :, 2:] = R[:, :, 2:] + R[:, :, 1:-1] + R[:, :, :-2]
ok = c3 >= 20; ok[:, :, :2] = False; ok[:, :, 120:] = False
sow_ag = np.where(ok.any(2), ok.argmax(2), 119)

# rendimentos (mesma deflacao Theil-Sen da analise A1)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.cod_local.str.startswith("23") & pam.ano.between(1998, 2025)]
Y = {}
for prod, nome in {"Milho (em grão)": "milho", "Feijão (em grão)": "feijao"}.items():
    s = pam[pam.produto == prod].copy()
    s["rp"] = np.where(s.area_plantada_ha > 0, s.producao_t * 1000 / s.area_plantada_ha, np.nan)
    M = np.full((NM, len(ANOS)), np.nan)
    for cod, g in s.groupby("cod_local"):
        if cod not in cods or g.area_plantada_ha.mean() < 300:
            continue
        g = g.set_index("ano").sort_index()
        yy = g.rp.where(g.rp > 0).dropna()
        if len(yy) < 15:
            continue
        sl, ic, _, _ = stats.theilslopes(np.log(yy.values), yy.index.values)
        an = g.rp / np.exp(ic + sl * g.index.values) - 1
        i = cods.index(cod)
        for a, v in an.items():
            M[i, a - 1998] = v
    Y[nome] = M
mask = {k: np.isfinite(v) for k, v in Y.items()}


def rho(x, cult):
    m = mask[cult]
    return stats.spearmanr(x[m], Y[cult][m])[0]


def auc(x, cult):
    m = mask[cult]
    return roc_auc_score((Y[cult][m] <= -0.5).astype(int), -x[m])


print("=== B1. Atraso de semeadura que melhor explica o PAM (relativo a 1a chuva >= 20 mm/3 d) ===")
for cult, cc, offs in [("feijao", "caupi", [0, 10, 20, 30, 40, 50, 60]), ("milho", "milho", [0, 10, 20, 30])]:
    linha = []
    for o in offs:
        isna, _ = simular(cc, np.minimum(sow_ag + o, ND - 80))
        linha.append((o, round(rho(isna, cult), 3), round(auc(isna, cult), 3)))
    print(f"  {cult} (balde {cc}): (atraso d, rho, AUC quebra>=50%) = {linha}")
# tambem: caupi semeado em data fixa (decendio) - qual decendio "fixo" melhor explica o feijao?
fix = []
for nome_d, dd in {"21/jan": 20, "01/fev": 31, "11/fev": 41, "21/fev": 51, "01/mar": 59, "11/mar": 69}.items():
    isna, _ = simular("caupi", np.full((NM, len(ANOS)), dd))
    fix.append((nome_d, round(rho(isna, "feijao"), 3)))
print(f"  feijao com semeadura fixa: {fix}")

print("\n=== B2. Sensibilidade a CAD (mm/m) do milho ===")
for awc in [50, 75, 100, 150]:
    isna, _ = simular("milho", sow_ag, awc)
    m = mask["milho"]
    fr12 = (isna[:, 2012 - 1998] < 0.5)[m[:, 2012 - 1998]].mean()
    print(f"  CAD {awc} mm/m (TAW {awc * 0.6:.0f} mm): rho={rho(isna, 'milho'):+.3f} AUC={auc(isna, 'milho'):.3f}  "
          f"frac. mun. ISNA<0,5 em 2012={fr12:.0%}")

print("\n=== B3. Modelo hibrido: ISNA (fisica) + calor na floracao + GBM, deixando 1 ano de fora ===")
isna_m, calor_m = simular("milho", sow_ag, 100)
isna_m2, _ = simular("milho", sow_ag + 20, 100)
fm = R[:, :, 31:151]
P = fm.sum(2)
rows = []
for i in range(NM):
    for j in range(len(ANOS)):
        if mask["milho"][i, j]:
            rows.append({"i": i, "ano": ANOS[j], "y": Y["milho"][i, j], "P_fmam": P[i, j], "isna": isna_m[i, j],
                         "isna_atraso20": isna_m2[i, j], "dias_quentes_flor": calor_m[i, j],
                         "dias_quentes_fmam": QUENTE[i, j, 31:151].sum(), "lat": mun.loc[cods[i], "pt"].y,
                         "lon": mun.loc[cods[i], "pt"].x})
D = pd.DataFrame(rows)
print(f"  rho(dias quentes na floracao, anomalia milho) = {stats.spearmanr(D.dias_quentes_flor, D.y)[0]:+.3f}; "
      f"rho(dias quentes fev-mai, anomalia) = {stats.spearmanr(D.dias_quentes_fmam, D.y)[0]:+.3f}")
# correlacao parcial: calor x anomalia controlando o ISNA (residuo de rank)
rk = D[["y", "isna", "dias_quentes_fmam"]].rank()
ry = rk.y - np.polyval(np.polyfit(rk["isna"], rk.y, 1), rk["isna"])
rc = rk.dias_quentes_fmam - np.polyval(np.polyfit(rk["isna"], rk.dias_quentes_fmam, 1), rk["isna"])
print(f"  correlacao parcial (rank) calor fev-mai x anomalia | ISNA = {np.corrcoef(ry, rc)[0, 1]:+.3f}")
y = D.y.clip(-1, 2).values
for nome_c, cols in {"chuva fev-mai": ["P_fmam"], "ISNA": ["isna"], "ISNA + calor": ["isna", "dias_quentes_flor", "dias_quentes_fmam"],
                     "ISNA + calor + chuva + local": ["isna", "isna_atraso20", "dias_quentes_flor", "dias_quentes_fmam", "P_fmam", "lat", "lon"]}.items():
    X = D[cols].values; pred = np.zeros(len(D))
    for a in ANOS:
        te = (D.ano == a).values
        if te.any():
            pred[te] = HistGradientBoostingRegressor(max_depth=3, max_iter=200, learning_rate=0.05, min_samples_leaf=40,
                                                     random_state=0).fit(X[~te], y[~te]).predict(X[te])
    r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    a12 = (D.ano == 2012).values
    print(f"  {nome_c:30s} R2_LOYO={r2:.3f}  AUC={roc_auc_score((y <= -0.5).astype(int), -pred):.3f}  "
          f"2012: anomalia prevista mediana={np.median(pred[a12]):+.2f} vs real={np.median(y[a12]):+.2f}")

print("\n=== B4. Data-limite (risco <= 30%) com limiar ISNA 0,6 ===")
DEC = {"21/jan": 20, "01/fev": 31, "11/fev": 41, "21/fev": 51, "01/mar": 59, "11/mar": 69, "21/mar": 79, "01/abr": 90, "11/abr": 100}
for cc in CULT:
    pr = {dn: (simular(cc, np.full((NM, len(ANOS)), dd))[0] >= 0.6).mean(1) for dn, dd in DEC.items()}
    PR = pd.DataFrame(pr)
    med = PR.median()
    ult = PR.apply(lambda r: [d for d in DEC if r[d] >= 0.7][-1] if (r >= 0.7).any() else "nenhum", axis=1)
    print(f"  {cc}: mediana estadual P(ISNA>=0,6) por decendio {med.round(2).to_dict()}")
    print(f"        ultimo decendio com risco<=30% (n mun.): {ult.value_counts().to_dict()}")
