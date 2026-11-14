"""Agrônomo de plantas de cobertura — rodada 3: os artigos de cobertura (itens 1–5) contra os dados NASA.

Perguntas (cada bloco < 8 min):
  A. O IMERG reproduz o regime de chuva descrito nos sítios dos ensaios?
     - da Luz et al. 2023 (Arapiraca-AL, 9°42'00"S 36°41'12"W; ~850 mm; chuva abr–set; 2022 "82% acima da normal");
     - Souza et al. 2024 (Arapiraca-AL, 9°46'07"S 36°33'41"W; ~800 mm; chuva mar–ago; ensaio mai–out/2023);
     - Melo et al. 2013 (Alagoinha-PB, EMEPA; ~1.100 mm; 2004 chuvoso; 2007–2008 mais chuva; 2002 e 2007 com
       veranico na floração apesar de > 600 mm; 2008 melhor ano). Coordenada: centroide do município
       (malha IBGE, cód. 2500502), porque o artigo não dá a da estação;
     - Nascimento et al. 2008 (Crato-CE, 7°14'S 39°25'W; 700–1.000 mm; ensaio IRRIGADO, ano não informado).
  B. A "regra" de 60 dias de cobertura antes do milho (da Luz 2023; Souza 2024) cabe na quadra do Ceará?
     Balde FAO-56 por município (mesmos parâmetros de hidrologo_fao56_isna_pam.py: milho 120 d, Kc 0,30/1,20/0,35,
     p 0,55, Zr 0,8 m, AWC 100 mm/m, CN 75, solo seco em 1/nov; sucesso = ISNA da floração >= 0,5).
       S0 milho na 1ª chuva (20 mm em 3 dias a partir de 1/jan, até 15/abr);
       S1 milho 60 dias depois, solo nu no intervalo (só o efeito do calendário);
       S2 cobertura verde por 60 dias (Kc do caupi do mesmo script, 15 d a 0,40 + 20 d até 1,05 + 25 d a 1,05)
          e milho logo após a dessecação (calendário + água gasta pela cobertura).
     Não modela a palhada (redução de evaporação): S1 é o teto otimista para S2.
  C. Calendário de Arapiraca x Ceará: chuva e SMAP L4 (zona da raiz) no ciclo do milho semeado após 60 d de cobertura.
  D. LST do MODIS (MOD11A2, 1 km) consegue ver os ~2 °C de Souza 2024? Ruído espacial e temporal no Cariri.
Saída: v3_agronomo_cobertura_janelas.saida.txt (mesma pasta).
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import shapely
import xarray as xr

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220)

SITIOS = {  # (lat, lon, fonte da coordenada)
    "Arapiraca_Luz2023": (-9.7000, -36.6867, "artigo 9°42'00\"S 36°41'12\"W"),
    "Arapiraca_Souza2024": (-9.7686, -36.5614, "artigo 9°46'07\"S 36°33'41\"W"),
    "Alagoinha_PB_Melo2013": (-6.9618, -35.5222, "centroide IBGE 2500502 (estação não georreferenciada no artigo)"),
    "Crato_Nascimento2008": (-7.2333, -39.4167, "artigo 7°14'S 39°25'W"),
}

# ------------------------------------------------------------------ A. IMERG nos sítios
with Cronometro("A: IMERG nos sítios"):
    ser = {k: [] for k in SITIOS}
    for a in range(1998, 2027):
        d = xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc")["precip"]
        for k, (la, lo, _) in SITIOS.items():
            ser[k].append(d.sel(lat=la, lon=lo, method="nearest").to_series())
    S = pd.DataFrame({k: pd.concat(v) for k, v in ser.items()})
    S = S.where(S >= 0)
    S = S[S.index < "2026-09-15"]

print("=== A. IMERG V07 (via POWER, 0,1°) nos sítios dos ensaios ===")
completo = S[(S.index.year >= 1998) & (S.index.year <= 2025)]
anual = completo.groupby(completo.index.year).sum(min_count=300)
mens = completo.groupby([completo.index.year, completo.index.month]).sum().groupby(level=1).mean()
for k, (la, lo, f) in SITIOS.items():
    print(f"\n{k} ({la}, {lo}; {f})")
    print(f"  chuva anual média 1998–2025: {anual[k].mean():.0f} mm (p10 {anual[k].quantile(.1):.0f}, p90 {anual[k].quantile(.9):.0f})")
    m = mens[k]
    print("  climatologia mensal (mm): " + " ".join(f"{i}:{v:.0f}" for i, v in m.items()))
    tri = {i: m.reindex([(i + j - 1) % 12 + 1 for j in range(6)]).sum() for i in range(1, 13)}
    i6 = max(tri, key=tri.get)
    print(f"  6 meses mais chuvosos começam no mês {i6} ({tri[i6] / m.sum() * 100:.0f}% do total anual)")

# Arapiraca: anomalias das safras do ensaio
for k in ("Arapiraca_Luz2023", "Arapiraca_Souza2024"):
    s = S[k]
    base = s[(s.index.year >= 1998) & (s.index.year <= 2020)]
    print(f"\n{k}: totais das safras do ensaio contra 1998–2020 (IMERG; o artigo usa a normal 1991–2021)")
    for ano in (2021, 2022, 2023):
        for (m0, m1, rot) in ((4, 9, "abr–set"), (4, 10, "abr–out"), (5, 10, "mai–out"), (1, 12, "ano")):
            v = s[(s.index.year == ano) & (s.index.month >= m0) & (s.index.month <= m1)].sum()
            b = base[(base.index.month >= m0) & (base.index.month <= m1)]
            b = b.groupby(b.index.year).sum().mean()
            print(f"  {ano} {rot}: {v:.0f} mm | normal {b:.0f} mm | anomalia {100 * (v / b - 1):+.0f}%")
    # janela do ensaio de da Luz: cobertura 2ª quinzena de abril (usa 20/abr) por 60 d; milho até +120 d
    for ano in (2021, 2022):
        c0 = pd.Timestamp(ano, 4, 20); m0 = c0 + pd.Timedelta(days=60); m1 = m0 + pd.Timedelta(days=120)
        print(f"  {ano}: chuva na cobertura (20/abr +60 d) {s[c0:m0 - pd.Timedelta(days=1)].sum():.0f} mm; "
              f"no milho ({m0:%d/%m}–{m1:%d/%m}) {s[m0:m1].sum():.0f} mm")


def maior_veranico(x, lim=1.0):
    seco = (x < lim).astype(int).values
    best = cur = 0
    for v in seco:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


s = S["Alagoinha_PB_Melo2013"]
print("\nAlagoinha-PB (Melo 2013): o artigo diz 2004 chuvoso; 2007 e 2008 mais chuva; 2002 e 2007 > 600 mm com veranico na floração; 2008 melhor")
lin = []
for ano in range(1998, 2009):
    x = s[s.index.year == ano]
    lin.append(dict(ano=ano, anual=x.sum(), mar_ago=x[(x.index.month >= 3) & (x.index.month <= 8)].sum(),
                    veranico_mai_jul=maior_veranico(x[(x.index.month >= 5) & (x.index.month <= 7)]),
                    veranico_abr_ago=maior_veranico(x[(x.index.month >= 4) & (x.index.month <= 8)]),
                    dias_secos_jun_jul=int((x[(x.index.month >= 6) & (x.index.month <= 7)] < 1).sum())))
L = pd.DataFrame(lin).set_index("ano").round(0)
L["rank_anual"] = L.anual.rank(ascending=False).astype(int)
print(L.to_string())
print(f"  média 1998–2025 no centroide: {anual['Alagoinha_PB_Melo2013'].mean():.0f} mm (artigo: 1.100 mm)")

# ------------------------------------------------------------------ B. 60 dias de cobertura na quadra do Ceará
with Cronometro("B: carregar IMERG CE + ET0 POWER"):
    im = xr.concat([xr.open_dataset(DADOS / "imerg" / f"imerg_ce_diario_{a}.nc")["precip"] for a in range(1998, 2027)], "time")
    im = im.where(im >= 0)
    et0 = xr.open_dataset(DADOS / "power" / "power_ce_diario_et0.nc")["ET0"]
    mun = municipios_ce_gdf()
    cod_col = next(c for c in mun.columns if "cod" in c.lower() or c.lower() in ("id", "codarea"))
    mun["cod"] = mun[cod_col].astype(str).str[:7].astype(int)
    NOMES = {x["id"]: x["nome"] for x in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}
    EX = {c: n for c, n in NOMES.items() if n in ("Crato", "Iguatu", "Quixadá", "Sobral", "Tauá", "Tianguá")}
    COD_QX = next(c for c, n in NOMES.items() if n == "Quixadá")
    lo, la = np.meshgrid(im.lon.values, im.lat.values)
    W = np.zeros((len(mun), lo.size), dtype=np.float32)
    for i, geom in enumerate(mun.geometry):
        m = shapely.contains_xy(geom, lo.ravel(), la.ravel())
        if m.sum() == 0:
            c = geom.centroid
            m = np.zeros(lo.size, bool)
            m[np.argmin((lo.ravel() - c.x) ** 2 + (la.ravel() - c.y) ** 2)] = True
        W[i, m] = 1.0 / m.sum()
    P = np.nan_to_num(im.values.reshape(im.sizes["time"], -1), nan=0.0)
    Pm = P @ W.T
    tP = pd.DatetimeIndex(im.time.values)
    cx = np.array([g.centroid.x for g in mun.geometry]); cy = np.array([g.centroid.y for g in mun.geometry])
    valida = (np.isfinite(et0.values).mean(0) > 0.9)
    LO, LA = np.meshgrid(et0.lon.values, et0.lat.values)
    iv = np.flatnonzero(valida.ravel())
    E0 = et0.values.reshape(et0.sizes["time"], -1)
    E = np.stack([E0[:, iv[np.argmin((LO.ravel()[iv] - x) ** 2 + (LA.ravel()[iv] - y) ** 2)]] for x, y in zip(cx, cy)], 1)
    tE = pd.DatetimeIndex(et0.time.values)
    T = tP.intersection(tE)
    Pm = pd.DataFrame(Pm, index=tP).loc[T].values
    E = pd.DataFrame(E, index=tE).loc[T]
    E = E.fillna(E.groupby(E.index.dayofyear).transform("mean")).values


def curva(L, kc):
    Li, Ld, Lm, Lf = L; ki, km, kf = kc
    k = np.concatenate([np.full(Li, ki), np.linspace(ki, km, Ld + 1)[1:], np.full(Lm, km), np.linspace(km, kf, Lf + 1)[1:]])
    est = np.concatenate([np.zeros(Li), np.ones(Ld), 2 * np.ones(Lm), 3 * np.ones(Lf)]).astype(int)
    return k, est


KC_M, EST_M = curva((20, 35, 40, 25), (0.30, 1.20, 0.35)); L_M = len(KC_M)
KC_C, _ = curva((15, 20, 25, 0), (0.40, 1.05, 1.05)); KC_C = KC_C[:60]  # cobertura verde até 60 d (caupi do script base)
P_M = 0.55; TAW = 100.0 * 0.8; RAW = P_M * TAW


def runoff_cn(p, cn=75.0):
    s_ = 25400.0 / cn - 254.0
    return np.where(p > 0.2 * s_, (p - 0.2 * s_) ** 2 / (p + 0.8 * s_), 0.0)


def simular(ano, cenario, dias=60):
    """Retorna doy da 1ª chuva, doy de semeadura do milho, ISNA total e da floração, chuva no ciclo do milho."""
    i0 = T.searchsorted(pd.Timestamp(ano - 1, 11, 1))
    js = T.searchsorted(pd.Timestamp(ano, 1, 1)); je = T.searchsorted(pd.Timestamp(ano, 4, 15))
    n = Pm.shape[1]
    Dr = np.full(n, TAW)
    onset = np.full(n, -1); sem = np.full(n, -1)
    eta_t = np.zeros(n); etc_t = np.zeros(n); eta_f = np.zeros(n); etc_f = np.zeros(n); chuva = np.zeros(n)
    for j in range(i0, min(je + dias + L_M + 5, len(T))):
        p = Pm[j]; e0 = E[j]; pin = p - runoff_cn(p)
        if js <= j < je:
            g = (onset < 0) & (Pm[max(j - 2, 0): j + 1].sum(0) >= 20.0)
            onset[g] = j
            if cenario == "S0":
                sem[g] = j
        if cenario in ("S1", "S2"):
            sem[(onset >= 0) & (sem < 0) & (j - onset >= dias)] = j
        dia_m = np.where(sem >= 0, j - sem, -1)
        dia_c = np.where(onset >= 0, j - onset, -1)
        ativo_m = (dia_m >= 0) & (dia_m < L_M)
        kc = np.full(n, 0.15)
        if cenario == "S2":
            cob = (dia_c >= 0) & (dia_c < dias) & ~ativo_m
            kc = np.where(cob, KC_C[np.clip(dia_c, 0, dias - 1)], kc)
        kc = np.where(ativo_m, KC_M[np.clip(dia_m, 0, L_M - 1)], kc)
        planta = ativo_m | ((cenario == "S2") & (dia_c >= 0) & (dia_c < dias))
        ks = np.where(Dr > RAW, np.clip((TAW - Dr) / ((1 - P_M) * TAW), 0, 1), 1.0)
        etc = kc * e0
        eta = np.where(planta, ks * etc, etc * np.clip((TAW - Dr) / TAW, 0, 1))
        Dr = np.clip(Dr - pin + eta, 0, TAW)
        eta_t[ativo_m] += eta[ativo_m]; etc_t[ativo_m] += etc[ativo_m]; chuva[ativo_m] += p[ativo_m]
        fl = ativo_m & (EST_M[np.clip(dia_m, 0, L_M - 1)] == 2)
        eta_f[fl] += eta[fl]; etc_f[fl] += etc[fl]
    j1 = T.searchsorted(pd.Timestamp(ano, 1, 1))
    nao = sem < 0
    return pd.DataFrame({"cod": mun.cod.values, "ano": ano, "cen": cenario,
                         "doy_onset": np.where(onset < 0, np.nan, onset - j1 + 1),
                         "doy_milho": np.where(nao, np.nan, sem - j1 + 1),
                         "isna": np.where(nao, 0, eta_t / np.maximum(etc_t, 1e-6)),
                         "isna_flor": np.where(nao, 0, eta_f / np.maximum(etc_f, 1e-6)),
                         "chuva_ciclo": chuva})


with Cronometro("B: simulação 1999–2025 × 3 cenários"):
    R = pd.concat([simular(a, c) for a in range(1999, 2026) for c in ("S0", "S1", "S2")], ignore_index=True)
R["ok"] = (R.isna_flor >= 0.5).astype(float)

print("\n=== B. 60 dias de cobertura antes do milho na quadra do Ceará (balde FAO-56, 184 municípios, 1999–2025) ===")
o = R[R.cen == "S0"]
print(f"  1ª chuva (20 mm/3 d desde 1/jan): mediana doy {o.doy_onset.median():.0f} "
      f"(p10 {o.doy_onset.quantile(.1):.0f}, p90 {o.doy_onset.quantile(.9):.0f}); sem 1ª chuva até 15/abr: {o.doy_onset.isna().mean() * 100:.1f}%")
d0 = pd.Timestamp(2025, 1, 1)
for q in (0.1, 0.5, 0.9):
    v = o.doy_onset.quantile(q)
    print(f"    q{int(q * 100)}: 1ª chuva {(d0 + pd.Timedelta(days=v - 1)):%d/%m} -> milho após 60 d de cobertura {(d0 + pd.Timedelta(days=v + 59)):%d/%m}")
tab = R.groupby("cen").agg(P_sucesso=("ok", "mean"), isna_flor_med=("isna_flor", "median"), isna_med=("isna", "median"),
                           chuva_ciclo_med=("chuva_ciclo", "median"), doy_milho_med=("doy_milho", "median"))
print(tab.round(3).to_string())
pm = R.groupby(["cen", "cod"]).ok.mean().unstack(0)
print(f"  municípios com P(sucesso) >= 0,7: S0 {int((pm.S0 >= .7).sum())} | S1 {int((pm.S1 >= .7).sum())} | S2 {int((pm.S2 >= .7).sum())} de {len(pm)}")
print(f"  P(sucesso) mediana entre municípios: S0 {pm.S0.median():.2f} | S1 {pm.S1.median():.2f} | S2 {pm.S2.median():.2f}")
par = R.pivot_table(index=["cod", "ano"], columns="cen", values="ok")
print(f"  municipio-anos em que S0 dá certo e S2 falha: {((par.S0 == 1) & (par.S2 == 0)).mean() * 100:.1f}% | "
      f"o contrário: {((par.S0 == 0) & (par.S2 == 1)).mean() * 100:.1f}%")
po = R.pivot_table(index=["cod", "ano"], columns="cen", values="doy_milho")
lim = pd.Timestamp(2025, 3, 21).dayofyear
print(f"  milho após 60 d de cobertura semeado depois de 21/mar (data-limite do balde na maior parte do estado): "
      f"{(po.S2 > lim).mean() * 100:.0f}% dos município-anos")
# anos secos e chuvosos pelos tercis da chuva estadual de fev–mai (IMERG, média dos municípios), 1999–2025
fm = pd.Series(Pm.mean(1), index=T)
fm = fm[(fm.index.month >= 2) & (fm.index.month <= 5) & (fm.index.year >= 1999) & (fm.index.year <= 2025)]
fm = fm.groupby(fm.index.year).sum()
secos = tuple(fm[fm <= fm.quantile(1 / 3)].index); chuv = tuple(fm[fm >= fm.quantile(2 / 3)].index)
for anos, rot in ((secos, f"tercil seco de fev–mai {secos}"), (chuv, f"tercil chuvoso de fev–mai {chuv}")):
    x = R[R.ano.isin(anos)].groupby("cen").ok.mean()
    print(f"  {rot}: P(sucesso) S0 {x.S0:.2f} | S1 {x.S1:.2f} | S2 {x.S2:.2f}")
for cod, nm in EX.items():
    if cod in pm.index:
        print(f"    {nm:8s}: P(sucesso) S0 {pm.loc[cod, 'S0']:.2f} | S1 {pm.loc[cod, 'S1']:.2f} | S2 {pm.loc[cod, 'S2']:.2f}")

print("  sensibilidade do comprimento da cobertura verde antes do milho (S2), P(sucesso) estadual:")
for dd in (20, 30, 45, 60):
    x = pd.concat([simular(a, "S2", dd) for a in range(1999, 2026)], ignore_index=True)
    ok = (x.isna_flor >= 0.5)
    pmd = ok.groupby(x.cod).mean()
    print(f"    {dd:2d} d: P(sucesso) {ok.mean():.2f} | municípios com P >= 0,7: {int((pmd >= .7).sum())} de {len(pmd)}")

# ------------------------------------------------------------------ C. SMAP L4: Arapiraca x Ceará no ciclo do milho pós-cobertura
with Cronometro("C: SMAP L4"):
    sm = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
    sm = sm.isel(time=~pd.DatetimeIndex(sm.time.values).duplicated())
    def serie_smap(la, lo_):
        return sm["sm_rootzone_pctl"].sel(lat=la, lon=lo_, method="nearest").to_series()
    ara = serie_smap(-9.7000, -36.6867)
    qx = mun[mun.cod == COD_QX].geometry.iloc[0].centroid
    qxs = serie_smap(qx.y, qx.x)
print("\n=== C. SMAP L4 (percentil da zona da raiz) no ciclo do milho semeado após 60 d de cobertura ===")
qx_on = R[(R.cen == "S2") & (R.cod == COD_QX)].set_index("ano").doy_milho
for ano in range(2016, 2026):
    a0 = pd.Timestamp(ano, 6, 19); a1 = a0 + pd.Timedelta(days=120)
    v_a = ara[a0:a1].mean()
    dq = qx_on.get(ano, np.nan)
    if np.isfinite(dq):
        q0 = pd.Timestamp(ano, 1, 1) + pd.Timedelta(days=int(dq) - 1); q1 = q0 + pd.Timedelta(days=120)
        v_q = qxs[q0:q1].mean(); rq = f"{q0:%d/%m}"
    else:
        v_q = np.nan; rq = "sem semeadura"
    print(f"  {ano}: Arapiraca (milho 19/jun +120 d) pctl {v_a:.2f} | Quixadá (milho {rq} +120 d) pctl {v_q:.2f}")

# ------------------------------------------------------------------ D. LST do MODIS contra os ~2 °C de Souza 2024
with Cronometro("D: LST MOD11A2 no Cariri"):
    lst = xr.open_dataset(DADOS / "modis" / "mod11a2_lst_ceara_001deg.nc")["lst_dia"]
    b = bbox_aoi("cariri")
    x = lst.sel(lon=slice(b[0], b[2]), lat=slice(b[3], b[1]))
    x = x.sel(time=(x.time.dt.year >= 2016) & (x.time.dt.year <= 2025) & (x.time.dt.month >= 8))
    x = x.load()  # o xarray já aplica scale_factor 0,01: valores em °C
    print("\n=== D. MOD11A2 LST diurna (~10:30) no Cariri, ago–dez 2016–2025 ===")
    print(f"  pixels na AOI: {x.sizes['lat'] * x.sizes['lon']} | compostos: {x.sizes['time']} | "
          f"válidos: {float(np.isfinite(x).mean()) * 100:.0f}%")
    dp_esp = x.std(dim=("lat", "lon"))
    anom = x - x.mean(dim=("lat", "lon"))
    dp_tmp = anom.std(dim="time")
    print(f"  desvio-padrão espacial entre pixels de 1 km no mesmo composto: mediana {float(dp_esp.median()):.2f} °C")
    print(f"  desvio-padrão temporal da anomalia de um pixel (relativa à AOI): mediana {float(dp_tmp.median()):.2f} °C")
    print(f"  atributo do produto: {lst.attrs.get('processamento', xr.open_dataset(DADOS / 'modis' / 'mod11a2_lst_ceara_001deg.nc').attrs.get('processamento'))}")
    for area_ha in (0.004, 1, 5, 20):
        print(f"  campo de {area_ha:g} ha num pixel de 100 ha com efeito de 2 °C: sinal de {2 * area_ha / 100:.3f} °C")

# ------------------------------------------------------------------ E. IMERG x pluviômetro INMET A353 (Arapiraca)
with Cronometro("E: INMET A353"):
    base_in = DADOS / "complementares" / "inmet" / "horario_ne"
    partes = []; lat_in = lon_in = None
    for f in sorted(base_in.glob("*/INMET_NE_AL_A353_ARAPIRACA_*.CSV")):
        cab = open(f, encoding="latin-1").read().splitlines()[:8]
        meta = {l.split(";")[0].strip(":"): l.split(";")[1] for l in cab}
        lat_in = float(meta["LATITUDE"].replace(",", ".")); lon_in = float(meta["LONGITUDE"].replace(",", "."))
        d = pd.read_csv(f, sep=";", skiprows=8, encoding="latin-1", decimal=",", usecols=[0, 1, 2])
        d.columns = ["data", "hora", "prec"]
        d["prec"] = pd.to_numeric(d.prec, errors="coerce")
        d.loc[d.prec < 0, "prec"] = np.nan
        partes.append(d)
    H = pd.concat(partes)
    H["data"] = pd.to_datetime(H.data.str.replace("-", "/"), format="%Y/%m/%d")
    g = H.groupby("data").prec
    dia = pd.DataFrame({"mm": g.sum(min_count=1), "n": g.count()})
    dia = dia[dia.n >= 23].mm  # dia válido: >= 23 das 24 horas
    ims = []
    for a in range(2016, 2026):
        ims.append(xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc")["precip"].sel(lat=lat_in, lon=lon_in, method="nearest").to_series())
    imd = pd.concat(ims)
    imd = imd.where(imd >= 0)
    J = pd.DataFrame({"inmet": dia, "imerg": imd}).dropna()
print(f"\n=== E. IMERG (célula de 0,1° da estação) x pluviômetro INMET A353 Arapiraca ({lat_in:.3f}, {lon_in:.3f}), dias válidos nos dois ===")
J["mes"] = J.index.month; J["ano"] = J.index.year
mm = J.groupby(["ano", "mes"]).agg(inmet=("inmet", "sum"), imerg=("imerg", "sum"), n=("inmet", "size"))
mm = mm[mm.n >= 25]
clim = mm.groupby(level=1)[["inmet", "imerg"]].mean()
clim["razao"] = clim.imerg / clim.inmet
print("  média mensal nos meses com >= 25 dias válidos (mm):")
print(clim.round(2).T.to_string())
aa = J.groupby("ano").agg(inmet=("inmet", "sum"), imerg=("imerg", "sum"), dias=("inmet", "size"))
aa["razao"] = aa.imerg / aa.inmet
print(aa.round(2).to_string())
for (m0, m1, rot) in ((1, 3, "jan–mar"), (4, 8, "abr–ago"), (9, 12, "set–dez")):
    x = J[(J.mes >= m0) & (J.mes <= m1)]
    print(f"  {rot}: INMET {x.inmet.sum():.0f} mm, IMERG {x.imerg.sum():.0f} mm (razão {x.imerg.sum() / x.inmet.sum():.2f}); "
          f"r diário {x[['inmet', 'imerg']].corr().iloc[0, 1]:.2f}; dias >= 1 mm: INMET {(x.inmet >= 1).sum()} x IMERG {(x.imerg >= 1).sum()}")
for ano in (2021, 2022, 2023):
    x = J[(J.ano == ano) & (J.mes >= 4) & (J.mes <= 9)]
    print(f"  {ano} abr–set: INMET {x.inmet.sum():.0f} mm ({len(x)} dias válidos) | IMERG {x.imerg.sum():.0f} mm")
print("  meses com >= 25 dias válidos por mês do calendário:", mm.groupby(level=1).size().to_dict())

# ------------------------------------------------------------------ F. IMERG x pluviômetros CEMADEN (rede de umidade do semiárido, 2015-08 a 2019-05)
with Cronometro("F: CEMADEN"):
    est = pd.read_parquet(DADOS / "complementares" / "cemaden" / "cemaden_estacoes.parquet")
    cd = pd.read_parquet(DADOS / "complementares" / "cemaden" / "cemaden_diario.parquet", columns=["estacao", "data", "chuva_mm", "n_horas"])
    cd = cd[(cd.n_horas >= 23) & cd.chuva_mm.notna() & (cd.chuva_mm >= 0)]
    cd["data"] = pd.to_datetime(cd.data)
    ims = xr.concat([xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc")["precip"] for a in range(2015, 2020)], "time")
    ims = ims.where(ims >= 0)
    lat_i = ims.lat.values; lon_i = ims.lon.values
    est["ii"] = [int(np.argmin(np.abs(lat_i - y))) for y in est.latitude]
    est["jj"] = [int(np.argmin(np.abs(lon_i - x))) for x in est.longitude]
    arr = ims.values; tI = pd.DatetimeIndex(ims.time.values)
    pos = pd.Series(np.arange(len(tI)), index=tI)
    cd = cd[cd.data.isin(tI)].merge(est[["estacao", "state", "latitude", "longitude", "ii", "jj"]], on="estacao")
    cd["imerg"] = arr[pos.loc[cd.data].values, cd.ii.values, cd.jj.values]
    cd = cd.dropna(subset=["imerg"])
    cd["mes"] = cd.data.dt.month
print("\n=== F. IMERG (célula de 0,1°) x pluviômetros CEMADEN, dias com >= 23 h válidas, 2015-08 a 2019-05 ===")
cd["leste"] = cd.longitude > -37.5  # faixa oriental (agreste/mata de RN, PB, PE, AL, SE)
for (m0, m1, rot) in ((1, 3, "jan–mar"), (4, 8, "abr–ago"), (9, 12, "set–dez")):
    x = cd[(cd.mes >= m0) & (cd.mes <= m1)]
    g = x.groupby("state").agg(est=("estacao", "nunique"), dias=("chuva_mm", "size"), pluv=("chuva_mm", "sum"), imerg=("imerg", "sum"))
    g["razao"] = g.imerg / g.pluv
    print(f"  {rot}:  " + " | ".join(f"{s} {r.razao:.2f} ({int(r.est)} est.)" for s, r in g.iterrows()))
    gl = x.groupby("leste").agg(pluv=("chuva_mm", "sum"), imerg=("imerg", "sum"), est=("estacao", "nunique"))
    print(f"     a leste de 37,5°W: razão {gl.loc[True, 'imerg'] / gl.loc[True, 'pluv']:.2f} ({int(gl.loc[True, 'est'])} est.) | "
          f"a oeste: {gl.loc[False, 'imerg'] / gl.loc[False, 'pluv']:.2f} ({int(gl.loc[False, 'est'])} est.)")
perto = cd[((cd.latitude + 9.70) ** 2 + (cd.longitude + 36.69) ** 2) ** 0.5 < 0.5]
if len(perto):
    for (m0, m1, rot) in ((1, 3, "jan–mar"), (4, 8, "abr–ago")):
        x = perto[(perto.mes >= m0) & (perto.mes <= m1)]
        print(f"  estações a < 0,5° do ensaio de Arapiraca ({perto.estacao.nunique()}: {', '.join(sorted(perto.drop_duplicates('estacao').apply(lambda r: est.set_index('estacao').loc[r.estacao, 'city'], axis=1)))}), "
              f"{rot}: pluviômetro {x.chuva_mm.sum():.0f} mm x IMERG {x.imerg.sum():.0f} mm (razão {x.imerg.sum() / x.chuva_mm.sum():.2f}) em {len(x)} estação-dias")
ce = cd[cd.state == "CE"]
print(f"  Ceará fev–mai (a quadra): razão {ce[(ce.mes >= 2) & (ce.mes <= 5)].imerg.sum() / ce[(ce.mes >= 2) & (ce.mes <= 5)].chuva_mm.sum():.2f} "
      f"({ce.estacao.nunique()} est.)")

# ------------------------------------------------------------------ G. Desenho de Melo 2013 (leguminosa intercalada) no calendário do Ceará
# guandu semeado no mesmo dia do milho; mucuna 85 dias depois do milho. Janela da mucuna: [milho+85, milho+145].
print("\n=== G. Leguminosa intercalada (desenho de Melo 2013) no Ceará: chuva e ET0 (POWER) nos 60 d após milho+85 d ===")
o = R[R.cen == "S0"][["cod", "ano", "doy_milho"]].dropna()
icod = {c: i for i, c in enumerate(mun.cod.values)}
lin = []
for r in o.itertuples():
    j0 = T.searchsorted(pd.Timestamp(int(r.ano), 1, 1)) + int(r.doy_milho) - 1 + 85
    j1 = j0 + 60
    if j1 >= len(T):
        continue
    i = icod[r.cod]
    lin.append((r.cod, r.ano, Pm[j0:j1, i].sum(), E[j0:j1, i].sum(), (T[j0]).strftime("%d/%m")))
G = pd.DataFrame(lin, columns=["cod", "ano", "P", "ET0", "ini"])
G["razao"] = G.P / G.ET0
print(f"  início da janela (mediana): {pd.Timestamp(2025, 1, 1) + pd.Timedelta(days=int(o.doy_milho.median()) + 84):%d/%m}")
print(f"  chuva mediana {G.P.median():.0f} mm (p10 {G.P.quantile(.1):.0f}, p90 {G.P.quantile(.9):.0f}); ET0 mediana {G.ET0.median():.0f} mm; "
      f"P/ET0 mediana {G.razao.median():.2f}; município-anos com P/ET0 >= 0,5: {(G.razao >= .5).mean() * 100:.0f}%")
for cod, nm in EX.items():
    x = G[G.cod == cod]
    print(f"    {nm:8s}: P {x.P.median():.0f} mm | ET0 {x.ET0.median():.0f} mm | P/ET0 {x.razao.median():.2f}")

# ------------------------------------------------------------------ H. Outra chuva NASA: POWER PRECTOTCORR (MERRA-2 corrigido, 0,5°, mensal) x CEMADEN
print("\n=== H. POWER PRECTOTCORR mensal (mm/dia x dias do mês) x pluviômetros CEMADEN, meses com >= 25 dias válidos ===")
pw = xr.open_dataset(DADOS / "power" / "power_ne_mensal.nc")["PRECTOTCORR"]
cm = cd.assign(ano=cd.data.dt.year).groupby(["estacao", "ano", "mes"]).agg(pluv=("chuva_mm", "sum"), imerg=("imerg", "sum"), n=("chuva_mm", "size"),
                                                                       lat=("latitude", "first"), lon=("longitude", "first"),
                                                                       uf=("state", "first")).reset_index()
cm = cm[cm.n >= 25]
la_p = pw.lat.values; lo_p = pw.lon.values; tp = pd.DatetimeIndex(pw.time.values)
ii = np.array([int(np.argmin(np.abs(la_p - y))) for y in cm.lat]); jj = np.array([int(np.argmin(np.abs(lo_p - x))) for x in cm.lon])
tt = np.array([tp.get_loc(pd.Timestamp(int(a), int(m), 1)) for a, m in zip(cm.ano, cm.mes)])
dias_mes = np.array([pd.Timestamp(int(a), int(m), 1).days_in_month for a, m in zip(cm.ano, cm.mes)])
cm["power"] = pw.values[tt, ii, jj] * dias_mes
cm["perto"] = ((cm.lat + 9.70) ** 2 + (cm.lon + 36.69) ** 2) ** 0.5 < 0.5
for rot, sub in (("AL+SE", cm[cm.uf.isin(["AL", "SE"])]), ("perto de Arapiraca", cm[cm.perto]), ("CE", cm[cm.uf == "CE"])):
    for (m0, m1, r2) in ((1, 3, "jan–mar"), (4, 8, "abr–ago"), (2, 5, "fev–mai")):
        x = sub[(sub.mes >= m0) & (sub.mes <= m1)]
        if len(x) < 5:
            continue
        print(f"  {rot:18s} {r2}: {len(x)} estação-meses | pluviômetro {x.pluv.sum():.0f} | IMERG {x.imerg.sum() / x.pluv.sum():.2f}x "
              f"(r mensal {x[['pluv', 'imerg']].corr().iloc[0, 1]:.2f}) | POWER {x.power.sum() / x.pluv.sum():.2f}x (r mensal {x[['pluv', 'power']].corr().iloc[0, 1]:.2f})")
