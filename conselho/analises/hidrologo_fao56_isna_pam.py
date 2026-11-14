"""Hidrólogo — análise 1: balanço hídrico FAO-56 por município × cultura × ano (1998–2025) e validação contra o IBGE PAM.

Perguntas:
  (a) O índice físico de satisfação hídrica (ISNA = ETa/ETc, e o rendimento relativo de Doorenbos-Kassam) explica a
      quebra de safra municipal melhor que a chuva total de fev–mai?
  (b) Semear pela ÁGUA NO SOLO (proxy do SMAP L4: balde com >= 50% da água disponível) reduz falsas partidas e
      perda em relação a semear pela "primeira chuva" (20 mm em 3 dias)?
  (c) Pegada hídrica verde (m³/t) e água que sobra no solo na colheita (o que uma cobertura/forrageira de entressafra
      pode usar), por cultura.
  (d) Probabilidade de quebra em anos de El Niño (ONI out–jan >= +1,0) contra os demais.

Entradas: IMERG V07 diário 0,1° (via POWER, 1998–2026), ET0 FAO-56 PM diário do POWER (0,5°), IBGE PAM municipal,
limites municipais do IBGE, ONI (NOAA).
Parâmetros FAO-56 (Allen et al. 1998, tabelas 11, 12 e 22) com ciclos curtos do sertão (suposição a calibrar com ZARC);
Ky de Doorenbos & Kassam (FAO-33, 1979).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import shapely
import xarray as xr
from scipy import stats
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220)
SAIDA = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
SAIDA.mkdir(exist_ok=True)

# ---------------------------------------------------------------- dados
with Cronometro("carregar"):
    im = xr.concat([xr.open_dataset(DADOS / "imerg" / f"imerg_ce_diario_{a}.nc")["precip"] for a in range(1998, 2027)], "time")
    im = im.where(im >= 0)
    et0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"]
    mun = municipios_ce_gdf()
    cod_col = next(c for c in mun.columns if "cod" in c.lower() or c.lower() in ("id", "codarea"))
    mun["cod"] = mun[cod_col].astype(str).str[:7].astype(int)
    lo, la = np.meshgrid(im.lon.values, im.lat.values)
    W = np.zeros((len(mun), lo.size), dtype=np.float32)
    for i, geom in enumerate(mun.geometry):
        m = shapely.contains_xy(geom, lo.ravel(), la.ravel())
        if m.sum() == 0:
            c = geom.centroid
            m = np.zeros(lo.size, bool)
            m[np.argmin((lo.ravel() - c.x) ** 2 + (la.ravel() - c.y) ** 2)] = True
        W[i, m] = 1.0 / m.sum()
    P = im.values.reshape(im.sizes["time"], -1)
    P = np.nan_to_num(P, nan=0.0)
    Pm = (P @ W.T)  # (tempo, municipio) mm/dia
    tP = pd.DatetimeIndex(im.time.values)
    cx = np.array([g.centroid.x for g in mun.geometry]); cy = np.array([g.centroid.y for g in mun.geometry])
    # célula do POWER válida mais próxima (células de oceano não têm ET0)
    valida = (np.isfinite(et0.values).mean(0) > 0.9)
    LO, LA = np.meshgrid(et0.lon.values, et0.lat.values)
    iv = np.flatnonzero(valida.ravel())
    E0 = et0.values.reshape(et0.sizes["time"], -1)
    E = np.stack([E0[:, iv[np.argmin((LO.ravel()[iv] - x) ** 2 + (LA.ravel()[iv] - y) ** 2)]] for x, y in zip(cx, cy)], 1)
    tE = pd.DatetimeIndex(et0.time.values)
    comum_t = tP.intersection(tE)
    Pm = pd.DataFrame(Pm, index=tP).loc[comum_t].values
    E = pd.DataFrame(E, index=tE).loc[comum_t]
    E = E.fillna(E.groupby(E.index.dayofyear).transform("mean")).values
    print("células POWER válidas:", int(valida.sum()), "| NaN restantes em ET0:", int(np.isnan(E).sum()))
    T = comum_t
print("dias:", len(T), T.min().date(), "->", T.max().date(), "| municípios:", len(mun),
      "| ET0 média anual (mm):", round(float(E.mean() * 365), 0), "| chuva média anual (mm):", round(float(Pm.mean() * 365), 0))

# ---------------------------------------------------------------- culturas (FAO-56)
CULT = {
    #            estágios (ini, des, med, fin) dias | Kc ini, med, fim | p    | Zr m | Ky (FAO-33)
    "milho":    dict(L=(20, 35, 40, 25), kc=(0.30, 1.20, 0.35), p=0.55, zr=0.8, ky=1.25),
    "feijao":   dict(L=(15, 20, 25, 15), kc=(0.40, 1.05, 0.35), p=0.45, zr=0.6, ky=1.15),
    "sorgo":    dict(L=(20, 35, 35, 25), kc=(0.30, 1.00, 0.55), p=0.55, zr=1.0, ky=0.90),
    "mandioca": dict(L=(20, 40, 90, 60), kc=(0.30, 0.80, 0.30), p=0.35, zr=0.8, ky=np.nan),
}
AWC = 100.0  # mm de água disponível por metro (textura média; ZARC usa classes AD1–AD6)


def curva_kc(c):
    Li, Ld, Lm, Lf = c["L"]; ki, km, kf = c["kc"]
    k = np.concatenate([np.full(Li, ki), np.linspace(ki, km, Ld + 1)[1:], np.full(Lm, km), np.linspace(km, kf, Lf + 1)[1:]])
    estagio = np.concatenate([np.zeros(Li), np.ones(Ld), 2 * np.ones(Lm), 3 * np.ones(Lf)]).astype(int)
    return k, estagio


def runoff_cn(p, cn=75.0):
    s = 25400.0 / cn - 254.0
    return np.where(p > 0.2 * s, (p - 0.2 * s) ** 2 / (p + 0.8 * s), 0.0)


def simular(ano, nome, regra="chuva", awc=AWC, irrigar=False, cn=75.0, data_ini=(1, 1), data_fim=(4, 15)):
    """Balde FAO-56 (coeficiente único) para todos os municípios ao mesmo tempo."""
    c = CULT[nome]; kc, est = curva_kc(c); L = len(kc)
    TAW = awc * c["zr"]; RAW = c["p"] * TAW
    t0 = pd.Timestamp(ano - 1, 11, 1)
    i0 = T.searchsorted(t0)
    js = T.searchsorted(pd.Timestamp(ano, *data_ini)); je = T.searchsorted(pd.Timestamp(ano, *data_fim))
    n = Pm.shape[1]
    Dr = np.full(n, TAW)  # fim da estação seca: solo no ponto de murcha
    plantado = np.full(n, -1)
    out = {k: np.zeros(n) for k in ("ETa", "ETc", "ETa_med", "ETc_med", "DP", "Q", "P", "irr", "Dr_colheita", "falsa")}
    ativo = np.zeros(n, bool); dia = np.zeros(n, int); fim = np.zeros(n, bool)
    for j in range(i0, min(je + L + 5, len(T))):
        p = Pm[j]; e0 = E[j]
        q = runoff_cn(p, cn); pin = p - q
        # semeadura
        if js <= j < je:
            if regra == "forcar":
                gatilho = np.ones(n, bool)
            elif regra == "chuva":
                gatilho = Pm[max(j - 2, 0): j + 1].sum(0) >= 20.0
            else:  # água no solo (proxy SMAP L4 zona da raiz): >= 50% da TAW disponível
                gatilho = (TAW - Dr) >= 0.5 * TAW
            novo = (~ativo) & (~fim) & (plantado < 0) & gatilho
            plantado[novo] = j; ativo |= novo
        kc_d = np.where(ativo, kc[np.minimum(dia, L - 1)], 0.15)  # 0,15 = solo nu seco (evaporação)
        ks = np.where(Dr > RAW, np.clip((TAW - Dr) / ((1 - c["p"]) * TAW), 0, 1), 1.0)
        etc = kc_d * e0; eta = np.where(ativo, ks * etc, etc * np.clip((TAW - Dr) / TAW, 0, 1))
        irr = np.zeros(n)
        if irrigar:
            precisa = ativo & (Dr - pin + eta > RAW)
            if irrigar == "flor":  # irrigação de salvamento só no estágio médio (floração/enchimento)
                precisa &= est[np.minimum(dia, L - 1)] == 2
            irr = np.where(precisa, np.maximum(Dr - pin + eta, 0), 0.0)
        Dr_novo = Dr - pin - irr + eta
        dp = np.where(Dr_novo < 0, -Dr_novo, 0.0)
        Dr = np.clip(Dr_novo, 0, TAW)
        a = ativo
        out["ETa"][a] += eta[a]; out["ETc"][a] += etc[a]; out["DP"][a] += dp[a]; out["Q"][a] += q[a]
        out["P"][a] += p[a]; out["irr"][a] += irr[a]
        med = a & (est[np.minimum(dia, L - 1)] == 2)
        out["ETa_med"][med] += eta[med]; out["ETc_med"][med] += etc[med]
        # falsa partida: 15 dias após semear, a cultura já em estresse severo (Ks < 0,3)
        fp = a & (dia == 15) & (ks < 0.3)
        out["falsa"][fp] = 1
        dia = np.where(a, dia + 1, dia)
        colheu = a & (dia >= L)
        out["Dr_colheita"][colheu] = TAW - Dr[colheu]  # água disponível que sobra na colheita (mm)
        fim |= colheu; ativo &= ~colheu
    nao = plantado < 0
    r = pd.DataFrame({"cod": mun.cod.values, "ano": ano, "cultura": nome, "regra": regra,
                      "doy_semeio": np.where(nao, np.nan, (plantado - T.searchsorted(pd.Timestamp(ano, 1, 1)) + 1)),
                      "isna": np.where(nao, 0, out["ETa"] / np.maximum(out["ETc"], 1e-6)),
                      "isna_flor": np.where(nao, 0, out["ETa_med"] / np.maximum(out["ETc_med"], 1e-6)),
                      "eta_mm": out["ETa"], "etc_mm": out["ETc"], "dp_mm": out["DP"], "runoff_mm": out["Q"],
                      "chuva_ciclo_mm": out["P"], "irrig_mm": out["irr"], "agua_sobra_colheita_mm": out["Dr_colheita"],
                      "falsa_partida": out["falsa"], "nao_semeou": nao.astype(int)})
    r["yrel"] = np.clip(1 - c["ky"] * (1 - r["isna"]), 0, 1) if np.isfinite(c["ky"]) else np.nan
    return r


with Cronometro("simulação"):
    res = []
    for ano in range(1999, 2026):
        for nome in CULT:
            res.append(simular(ano, nome, "chuva"))
            res.append(simular(ano, nome, "solo"))
            if nome in ("milho", "feijao"):
                res.append(simular(ano, nome, "chuva", irrigar=True).assign(regra="chuva_irrigado"))
    R = pd.concat(res, ignore_index=True)
R.to_parquet(SAIDA / "hidrologo_fao56_mun_ano.parquet", index=False)

# ---------------------------------------------------------------- PAM: rendimento por área PLANTADA, sem tendência
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.produto.isin(["Milho (em grão)", "Feijão (em grão)", "Mandioca"])].copy()
pam["cultura"] = pam.produto.map({"Milho (em grão)": "milho", "Feijão (em grão)": "feijao", "Mandioca": "mandioca"})
pam = pam[(pam.area_plantada_ha >= 200) & (pam.ano >= 1993)]
pam["rend"] = pam.producao_t * 1000 / pam.area_plantada_ha
pam = pam.sort_values(["cod_local", "cultura", "ano"])
pam["tend"] = pam.groupby(["cod_local", "cultura"]).rend.transform(lambda s: s.rolling(7, center=True, min_periods=3).median())
pam["desvio"] = pam.rend / pam.tend - 1
pam = pam.rename(columns={"cod_local": "cod"})[["cod", "ano", "cultura", "rend", "desvio", "area_plantada_ha"]]
pam["cod"] = pam["cod"].astype(int)

# chuva fev–mai municipal (IMERG)
dfP = pd.DataFrame(Pm, index=T, columns=mun.cod.values)
fmam = dfP[dfP.index.month.isin([2, 3, 4, 5])].groupby(dfP[dfP.index.month.isin([2, 3, 4, 5])].index.year).sum()
fmam = fmam.stack().rename("chuva_fmam").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})

base = R[R.regra == "chuva"].merge(pam, on=["cod", "ano", "cultura"]).merge(fmam, on=["cod", "ano"])
base = base[base.ano.between(1999, 2025)].dropna(subset=["desvio"])
print("\n=== (a) O balanço FAO-56 explica a quebra municipal melhor que a chuva fev–mai? ===")
linhas = []
for cult, g in base.groupby("cultura"):
    sev = (g.desvio <= -0.5).astype(int)
    for x in ["chuva_fmam", "isna", "isna_flor", "yrel"]:
        if g[x].isna().all():
            continue
        rho = stats.spearmanr(g[x], g.desvio).correlation
        # habilidade espacial: correlação entre municípios dentro de cada ano (média)
        dentro_ano = g.groupby("ano").apply(lambda h: stats.spearmanr(h[x], h.desvio).correlation if len(h) > 20 else np.nan).mean()
        # habilidade temporal: dentro de cada município (média)
        dentro_mun = g.groupby("cod").apply(lambda h: stats.spearmanr(h[x], h.desvio).correlation if len(h) > 12 else np.nan).mean()
        auc = roc_auc_score(sev, g[x]) if sev.nunique() == 2 else np.nan
        linhas.append({"cultura": cult, "preditor": x, "n": len(g), "rho_painel": rho, "rho_entre_mun_no_ano": dentro_ano,
                       "rho_no_tempo_por_mun": dentro_mun, "AUC quebra>=50% (1-AUC se neg.)": 1 - auc if auc < 0.5 else auc,
                       "freq_quebra50": sev.mean()})
A = pd.DataFrame(linhas)
print(A.round(3).to_string(index=False))
A.to_csv(SAIDA / "hidrologo_validacao_pam.csv", index=False)

# estado inteiro (ponderado pela área plantada)
print("\n--- Estado (média ponderada pela área plantada), correlação de Spearman com o desvio de rendimento ---")
for cult, g in base.groupby("cultura"):
    w = g.groupby("ano").apply(lambda h: pd.Series({k: np.average(h[k], weights=h.area_plantada_ha) for k in ["desvio", "chuva_fmam", "isna", "isna_flor"]}))
    print(cult, {k: round(stats.spearmanr(w[k], w.desvio).correlation, 2) for k in ["chuva_fmam", "isna", "isna_flor"]}, "| anos", len(w))

# ---------------------------------------------------------------- (b) regra de semeadura
print("\n=== (b) Semear pela água no solo (proxy SMAP L4) × pela primeira chuva ===")
B = R[R.regra.isin(["chuva", "solo"])].groupby(["cultura", "regra"]).agg(
    isna_med=("isna", "median"), isna_p10=("isna", lambda s: s.quantile(0.1)),
    p_isna_lt05=("isna", lambda s: (s < 0.5).mean()), falsa_partida=("falsa_partida", "mean"),
    nao_semeou=("nao_semeou", "mean"), doy_semeio_med=("doy_semeio", "median"), yrel_med=("yrel", "median"),
    yrel_p10=("yrel", lambda s: s.quantile(0.1))).round(3)
print(B.to_string())
# correlação de cada regra com o PAM (qual regra parece mais com o que o agricultor vive?)
for regra in ["chuva", "solo"]:
    g = R[R.regra == regra].merge(pam, on=["cod", "ano", "cultura"]).dropna(subset=["desvio"])
    print(regra, {c: round(stats.spearmanr(h["isna"], h.desvio).correlation, 3) for c, h in g.groupby("cultura")})

# ---------------------------------------------------------------- (c) pegada hídrica e água que sobra
print("\n=== (c) Água por cultura (mediana municipal 1999–2025, regra 'chuva') ===")
C = R[R.regra == "chuva"].merge(pam, on=["cod", "ano", "cultura"], how="left")
C["pegada_verde_m3_t"] = 10 * C.eta_mm / (C.rend / 1000)
tab = C.groupby("cultura").agg(chuva_no_ciclo=("chuva_ciclo_mm", "median"), ETc=("etc_mm", "median"), ETa=("eta_mm", "median"),
                                escoamento=("runoff_mm", "median"), percolacao=("dp_mm", "median"),
                                sobra_na_colheita=("agua_sobra_colheita_mm", "median"),
                                p_sobra_ge_30mm=("agua_sobra_colheita_mm", lambda s: (s >= 30).mean()),
                                pegada_verde_m3_t=("pegada_verde_m3_t", "median"), rend_PAM_kg_ha=("rend", "median")).round(2)
print(tab.to_string())
irr = R[R.regra == "chuva_irrigado"].groupby("cultura").agg(lamina_irrig_mm_med=("irrig_mm", "median"),
                                                            lamina_irrig_mm_p90=("irrig_mm", lambda s: s.quantile(0.9)))
print("Irrigação suplementar para manter Ks=1 na quadra (mm):\n", irr.round(1).to_string())
# safrinha irrigada na seca (semear 1/ago): lâmina total = ETc quase toda
for nome in ["feijao", "milho"]:
    s = pd.concat([simular(a, nome, "forcar", irrigar=True, data_ini=(8, 1), data_fim=(8, 2)) for a in range(2001, 2025)])
    print(f"Safra irrigada semeada em 1/ago ({nome}): lâmina mediana {s.irrig_mm.median():.0f} mm = {10 * s.irrig_mm.median():.0f} m³/ha; ETc {s.etc_mm.median():.0f} mm")

# ---------------------------------------------------------------- (d) El Niño
ix = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
oni = ix[ix.variavel == "ONI"].set_index("data")["valor"]; oni.index = pd.to_datetime(oni.index)
ondj = {a: oni[pd.Timestamp(a - 1, 10, 1): pd.Timestamp(a, 1, 1)].mean() for a in range(1999, 2026)}
R["oni_ondj"] = R.ano.map(ondj)
print("\n=== (d) Probabilidade de ISNA < 0,5 (quebra hídrica) por fase do ENSO (out–jan) ===")
anos_en = sorted(a for a, v in ondj.items() if v >= 1.0)
print("anos El Niño (ONI out–jan >= +1,0):", anos_en)
D = R[R.regra == "chuva"].copy()
D["fase"] = np.where(D.oni_ondj >= 1.0, "El Niño", np.where(D.oni_ondj <= -0.5, "La Niña", "neutro"))
print(D.groupby(["cultura", "fase"]).agg(p_isna_lt05=("isna", lambda s: (s < 0.5).mean()), isna_med=("isna", "median"),
                                         anos=("ano", "nunique")).round(3).unstack("fase").to_string())
DP_ = pam.assign(fase=pam.ano.map(ondj)).dropna(subset=["fase", "desvio"])
DP_["fase"] = np.where(DP_.fase >= 1.0, "El Niño", np.where(DP_.fase <= -0.5, "La Niña", "neutro"))
print("PAM observado: P(quebra >= 50%) e desvio mediano por fase:\n",
      DP_.groupby(["cultura", "fase"]).agg(p_quebra50=("desvio", lambda s: (s <= -0.5).mean()), desvio_med=("desvio", "median"))
      .round(3).unstack("fase").to_string())

# ---------------------------------------------------------------- (e) calibração em amostra dividida (anos ímpares × pares)
print("\n=== (e) Calibração do balde (AWC, CN, início da janela) em anos ímpares, teste em anos pares ===")
pam_i = pam.set_index(["cod", "ano", "cultura"])
cal = []
for nome in ["milho", "feijao"]:
    for awc in (60.0, 100.0, 140.0):
        for cn in (70.0, 80.0, 88.0):
            for ini in ((1, 1), (1, 20), (2, 10)):
                rr = pd.concat([simular(a, nome, "chuva", awc=awc, cn=cn, data_ini=ini, data_fim=(4, 30)) for a in range(1999, 2026)])
                g = rr.join(pam_i, on=["cod", "ano", "cultura"]).dropna(subset=["desvio"])
                imp, par = g[g.ano % 2 == 1], g[g.ano % 2 == 0]
                cal.append({"cultura": nome, "awc": awc, "cn": cn, "ini": f"{ini[1]:02d}/{ini[0]:02d}",
                            "rho_impares": stats.spearmanr(imp["isna"], imp.desvio).correlation,
                            "rho_pares": stats.spearmanr(par["isna"], par.desvio).correlation,
                            "p_isna_lt05": (rr["isna"] < 0.5).mean(), "percol_med": rr.dp_mm.median(), "runoff_med": rr.runoff_mm.median()})
CAL = pd.DataFrame(cal)
CAL.to_csv(SAIDA / "hidrologo_calibracao_balde.csv", index=False)
for nome, g in CAL.groupby("cultura"):
    best = g.loc[g.rho_impares.idxmax()]
    print(nome, "| melhor nos ímpares:", best[["awc", "cn", "ini"]].to_dict(), f"rho ímpares {best.rho_impares:.3f} -> pares {best.rho_pares:.3f}",
          f"| padrão (100, 75, 01/01) ≈ ver tabela; P(ISNA<0,5) {best.p_isna_lt05:.3f}, percolação {best.percol_med:.0f} mm, escoamento {best.runoff_med:.0f} mm")
    fp = fmam.merge(pam, on=["cod", "ano"]); fp = fp[fp.cultura == nome]
    print("    chuva fev–mai, mesmo teste: rho ímpares", round(stats.spearmanr(fp[fp.ano % 2 == 1].chuva_fmam, fp[fp.ano % 2 == 1].desvio).correlation, 3),
          "pares", round(stats.spearmanr(fp[fp.ano % 2 == 0].chuva_fmam, fp[fp.ano % 2 == 0].desvio).correlation, 3))
print(CAL.sort_values(["cultura", "rho_impares"], ascending=[True, False]).groupby("cultura").head(4).round(3).to_string(index=False))

# ---------------------------------------------------------------- (f) irrigação de salvamento na floração × safra irrigada na seca
print("\n=== (f) Água azul: salvamento na floração × irrigação plena na quadra × safra irrigada na seca ===")
for nome in ["milho", "feijao"]:
    seq = R[(R.regra == "chuva") & (R.cultura == nome)].set_index(["cod", "ano"])
    flo = pd.concat([simular(a, nome, "chuva", irrigar="flor") for a in range(1999, 2026)]).set_index(["cod", "ano"])
    ple = R[(R.regra == "chuva_irrigado") & (R.cultura == nome)].set_index(["cod", "ano"])
    ym = {"milho": 3000.0, "feijao": 1200.0}[nome]  # rendimento potencial de sequeiro tecnificado (suposição; ajustar ao GAEZ/Embrapa)
    for rot, x in [("salvamento na floração", flo), ("plena na quadra", ple)]:
        ganho = (x.yrel - seq.yrel).clip(lower=0) * ym  # kg/ha a mais
        m3 = 10 * x.irrig_mm
        efic = (ganho.sum() / m3.sum())
        print(f"  {nome:7s} {rot:24s}: lâmina mediana {x.irrig_mm.median():5.0f} mm (p90 {x.irrig_mm.quantile(.9):5.0f}) | ganho mediano "
              f"{ganho.median():5.0f} kg/ha | {efic:.2f} kg de grão por m³ de água azul | P(ISNA<0,5) {(x['isna'] < 0.5).mean():.3f} vs sequeiro {(seq['isna'] < 0.5).mean():.3f}")
    # anos secos (El Niño e 2012)
    for ano in (2012, 2016):
        print(f"     {ano}: lâmina de salvamento mediana {flo.xs(ano, level='ano').irrig_mm.median():.0f} mm; Yrel sequeiro "
              f"{seq.xs(ano, level='ano').yrel.median():.2f} -> com salvamento {flo.xs(ano, level='ano').yrel.median():.2f}")
# série do estado: ISNA médio por ano e cultura (para o slide "como cada cultura teria se saído")
S = R[R.regra == "chuva"].groupby(["ano", "cultura"])["isna"].median().unstack().round(2)
print("\nISNA mediano dos municípios por ano:\n", S.to_string())
S.to_csv(SAIDA / "hidrologo_isna_ano_cultura.csv")
