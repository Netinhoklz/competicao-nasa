"""v4 - Cientista de satelite e inferencia causal: transferencia de efeitos de rotacao entre climas.

Quatro testes rapidos:
 T1. Reanalise da Tabela S9 de Kluger, Di Tommaso & Lobell (2025; arXiv 2506.02384 v2, p. 64):
     confere a mediana de 4,5% (p. 33) e a razao de 3,7x (p. 13) e resume a heterogeneidade
     com chuva e temperatura por categoria de antecessor.
 T2. Suporte climatico: a estacao de cultivo do Ceara cai dentro da faixa de chuva e de aridez
     em que os coeficientes de Kluger/Zhou/Seifert foram estimados? (NLDAS-2 Noah nas celulas
     de milho+soja do CDL 2023 nas Planicies x IMERG municipal + GLDAS-2.1 Noah no Ceara.)
 T3. Memoria de agua no solo entre safras (mecanismo hidrico do antecessor): Planicies x Ceara.
 T4. Espaco por tempo: inclinacao rendimento-chuva ENTRE municipios x DENTRO do municipio
     (PAM Ceara 1998-2025, milho e feijao, por area plantada).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
import xarray as xr

RNG = np.random.default_rng(42)
pd.set_option("display.width", 200)


def q(x, ps=(5, 25, 50, 75, 95)):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return {f"P{p}": round(float(np.percentile(x, p)), 3) for p in ps}


# ---------------------------------------------------------------- T1
print("=" * 100)
print("T1. Tabela S9 de Kluger et al. 2025 (arXiv v2, p. 64), digitada do PDF local")
print("=" * 100)
# pais, trat, ctrl, nT, nC, ef2, efdiv, bP, bT ('*' = significativo a 5%)
S9 = """US S C 811541 432622 2.5* -3.4* 0.6* -1.0*
US WW C 61653 432622 0.9* 0.7* 1.3* -1.6*
Canada S C 21312 16497 1.7* -2.3* 1.3* -0.3
Canada P C 4437 16497 -2.0* 0.2 1.7* -1.4*
Canada WW C 3016 16497 3.7* 5.2* 2.3* -0.9
Canada UW C 2380 16497 3.9* 2.9* 1.2 1.7*
Canada SW C 2015 16497 -0.3 1.3 0.6 2.5*
China S C 28133 111379 -2.4* NA 0.5* -1.5*
France WW C 11415 15327 -0.9* -2.1* -1.5* -5.4*
France WB C 2123 15327 -0.9 -1.9 1.6 -6.0*
US C S 843666 269506 8.5* 0.7* 0.7* 1.4*
US SW S 57524 269506 4.2* -0.0 0.8* 0.2
Canada C S 26706 19068 6.8* 2.7* -0.3 4.0*
Canada SW S 9107 19068 2.6* 3.8* 2.6* 2.1*
Canada R S 8665 19068 2.1* 1.8* 1.7* 2.4*
Canada P S 3412 19068 -2.1* -0.8 0.0 1.4
Canada UW S 2829 19068 4.3* 0.8 -0.3 1.4
China C S 19884 34969 6.2* NA 0.6* -0.6*
US S SW 68494 35515 8.3* 2.9* 1.6* -2.0*
US R SW 18061 35515 7.1* -0.1 2.2* -3.9*
US Su SW 14730 35515 3.9* 1.0 4.5* -1.2*
US DB SW 7624 35515 14.4* 0.6 1.9* -0.7
US C SW 7693 35515 2.1* -0.1 0.8 -0.1
Canada R SW 199115 44809 9.4* 3.0* 1.1* 1.1*
Canada Le SW 33892 44809 10.4* 4.2* 2.7* 0.4
Canada Pe SW 30637 44809 11.3* 4.1* 3.6* -1.1*
Canada S SW 11332 44809 13.7* 3.9* -1.0 -1.7*
Canada F SW 10139 44809 4.7* 5.1* -3.4* -2.5*
US F WW 84845 151613 8.3* 3.0* -0.4 -4.8*
US S WW 35241 151613 -12.4* 6.5* 5.0* -4.6*
US C WW 22417 151613 4.0* 0.8 2.2* 2.9*
France R WW 32045 18119 10.1* -0.9* -1.6* 1.8*
France Si WW 14917 18119 8.3* -0.2 -1.7* 0.1
France C WW 13378 18119 6.7* -0.5 0.3 1.9*
France Ch WW 9720 18119 7.0* -0.2 3.2* 1.7*
France Su WW 8401 18119 6.7* -0.8 1.0 1.9*"""
rows = []
for ln in S9.splitlines():
    pa, tr, ct, nt, nc, *vals = ln.split()
    rec = dict(pais=pa, antecessor=tr, cultura=ct, nT=int(nt), nC=int(nc))
    for nome, v in zip(["ef2", "efdiv", "bP", "bT"], vals):
        rec[nome] = np.nan if v == "NA" else float(v.rstrip("*"))
        rec[nome + "_sig"] = v.endswith("*")
    rows.append(rec)
t = pd.DataFrame(rows)
cat = {"S": "leguminosa", "Pe": "leguminosa", "Le": "leguminosa", "DB": "leguminosa",
       "C": "cereal", "WW": "cereal", "WB": "cereal", "UW": "cereal", "SW": "cereal", "Si": "cereal",
       "R": "folha_larga", "Su": "folha_larga", "Ch": "folha_larga", "P": "pastagem", "F": "pousio"}
t["categoria"] = t.antecessor.map(cat)
print(f"linhas: {len(t)} (o artigo fala em 36 pares rotacao-pais)")
print(f"mediana do efeito do antecessor (2 anos): {t.ef2.median():.2f}%  (texto, p. 33: 4,5%)")
print(f"media do efeito do antecessor: {t.ef2.mean():.2f}%  | media do efeito de diversificar: "
      f"{t.efdiv.mean():.2f}% (n={t.efdiv.notna().sum()})  | razao = {t.ef2.mean() / t.efdiv.mean():.2f}x  (texto, p. 13: ~3,7x)")
m = t.efdiv.notna()
print(f"  razao restrita as {m.sum()} linhas com diversificacao: {t.ef2[m].mean() / t.efdiv[m].mean():.2f}x")
print(f"efeito do antecessor positivo e significativo: {((t.ef2 > 0) & t.ef2_sig).sum()}/36; negativo e significativo: {((t.ef2 < 0) & t.ef2_sig).sum()}/36")
print(f"diversificar: positivo sig {((t.efdiv > 0) & t.efdiv_sig).sum()}, negativo sig {((t.efdiv < 0) & t.efdiv_sig).sum()}, n.s. {(~t.efdiv_sig & m).sum()} (de {m.sum()})")
print("\nPor cultura seguinte (mediana do efeito do antecessor, %):")
print(t.groupby("cultura").ef2.agg(["count", "median", "min", "max"]).round(2).to_string())
print("\nHeterogeneidade com chuva (bP, % por P25->P75 local) e temperatura (bT) por categoria de antecessor:")
g = t.groupby("categoria").agg(n=("bP", "size"),
                               bP_med=("bP", "median"),
                               bP_pos_sig=("bP", lambda s: int(((s > 0) & t.loc[s.index, "bP_sig"]).sum())),
                               bP_neg_sig=("bP", lambda s: int(((s < 0) & t.loc[s.index, "bP_sig"]).sum())),
                               bT_med=("bT", "median"),
                               bT_pos_sig=("bT", lambda s: int(((s > 0) & t.loc[s.index, "bT_sig"]).sum())),
                               bT_neg_sig=("bT", lambda s: int(((s < 0) & t.loc[s.index, "bT_sig"]).sum())))
print(g.round(2).to_string())
print("\nTemperatura quando a cultura seguinte e soja (bT):", t.loc[t.cultura == "S", "bT"].tolist())
leg = t[t.categoria == "leguminosa"]
print("Leguminosa antecessora -> bT:", list(zip(leg.antecessor + "->" + leg.cultura + "(" + leg.pais + ")", leg.bT, leg.bT_sig)))
print(f"\nchuva: {((t.bP > 0) & t.bP_sig).sum()}/36 positivos sig, {((t.bP < 0) & t.bP_sig).sum()}/36 negativos sig")
print(f"razao |bP| mediana / efeito mediano: {t.bP.abs().median():.2f} / {t.ef2.median():.2f} = {t.bP.abs().median() / t.ef2.median():.2f}")
r = np.corrcoef(t.ef2, t.bP)[0, 1]
print(f"correlacao entre o efeito medio e bP entre as 36 linhas: r = {r:.2f}")
# o efeito "em t/ha" para comparacao com o semiarido (Tabela S10, p. 65)
s10 = {("US", "C"): 10.35, ("Canada", "C"): 9.35, ("China", "C"): 6.78, ("France", "C"): 9.01,
       ("US", "S"): 3.17, ("Canada", "S"): 2.78, ("China", "S"): 1.87,
       ("Canada", "SW"): 3.08, ("US", "SW"): 3.16, ("France", "WW"): 7.01, ("US", "WW"): 2.69}
t["ef2_t_ha"] = [r.ef2 / 100 * s10[(r.pais, r.cultura)] for r in t.itertuples()]
print("efeito em t/ha (Tabela S9 x S10), milho como cultura seguinte:",
      t.loc[t.cultura == "C", ["pais", "antecessor", "ef2", "ef2_t_ha"]].round(3).to_dict("records"))

# ---------------------------------------------------------------- T2
print("\n" + "=" * 100)
print("T2. Suporte climatico: Planicies/Corn Belt (NLDAS-2 Noah, celulas de milho+soja do CDL 2023) x Ceara")
print("=" * 100)
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin

ds = xr.open_dataset(DADOS / "nldas/nldas_noah0125_mensal_planicies_eua.nc")
lat = ds.lat.values
lon = ds.lon.values
dst = np.zeros((len(lat), len(lon)), np.float32)
tr_dst = from_origin(lon.min() - 0.0625, lat.max() + 0.0625, 0.125, 0.125)
with rasterio.open(ESTUDO_CDL / "recortes/nacional_2023_960m.tif") as src:
    a = src.read(1)
    mask = np.isin(a, [1, 5]).astype(np.float32)  # CDL: 1 = milho, 5 = soja
    reproject(mask, dst, src_transform=src.transform, src_crs=src.crs, dst_transform=tr_dst,
              dst_crs="EPSG:4326", resampling=Resampling.average)
frac = dst[::-1, :]  # linhas norte->sul viram lat crescente
cel = frac >= 0.25
print(f"celulas NLDAS 0,125 grau com >=25% de milho+soja no CDL 2023: {cel.sum()} de {cel.size}")

mes = ds.time.dt.month.values
ano = ds.time.dt.year.values
dias = ds.time.dt.days_in_month.values
R = ds.Rainf.values  # mm/mes
PET = ds.PotEvap.values / 2.45e6 * 86400 * dias[:, None, None]  # W m-2 -> mm/mes
SM = ds.SoilM_0_100cm.values  # mm


def estacao(arr, meses, anos):
    out = {}
    for y in anos:
        k = (ano == y) & np.isin(mes, meses)
        if k.sum() == len(meses):
            out[y] = arr[k].sum(0)
    return out


anos_kl = range(2008, 2022)  # periodo dos EUA em Kluger (Tabela S1)
Pms = estacao(R, [5, 6, 7, 8, 9], anos_kl)
Ems = estacao(PET, [5, 6, 7, 8, 9], anos_kl)
P_pl = np.stack([Pms[y][cel] for y in Pms])
A_pl = np.stack([Pms[y][cel] / Ems[y][cel] for y in Pms])
cv_pl = np.nanmean(P_pl.std(0) / P_pl.mean(0))
print("Planicies, chuva mai-set (mm), celula-ano 2008-2021:", q(P_pl), f"| CV interanual medio = {cv_pl:.2f}")
print("Planicies, P/PET Noah mai-set:", q(A_pl))

im = pd.read_parquet(DERIV / "ibge_ne_mun_imerg_mensal.parquet")
im = im[im.cod_mun.str.startswith("23")].copy()
im["ano"] = im.data.dt.year
im["mes"] = im.data.dt.month
im = im[(im.ano >= 1998) & (im.ano <= 2025)]
q_fm = im[im.mes.between(2, 5)].groupby(["cod_mun", "ano"]).precip_mm.sum()
q_jj = im[im.mes.between(1, 6)].groupby(["cod_mun", "ano"]).precip_mm.sum()
gl = pd.read_parquet(DERIV / "gldas_ce_mensal.parquet")
gl = gl.pivot_table(index="data", columns="variavel", values="valor")
gl["dias"] = gl.index.days_in_month
gl["PET_mm"] = gl.PotEvap_tavg / 2.45e6 * 86400 * gl.dias
gl["SM100"] = gl.SoilMoi0_10cm_inst + gl.SoilMoi10_40cm_inst + gl.SoilMoi40_100cm_inst
pet_fm = gl[gl.index.month.isin([2, 3, 4, 5])].groupby(gl.index.year[gl.index.month.isin([2, 3, 4, 5])]).PET_mm.sum()
a_fm = (q_fm.reset_index().merge(pet_fm.rename("pet").reset_index().rename(columns={"data": "ano"}), on="ano"))
a_fm["arid"] = a_fm.precip_mm / a_fm.pet
cv_ce = (q_fm.groupby("cod_mun").std() / q_fm.groupby("cod_mun").mean()).mean()
print("Ceara, chuva fev-mai IMERG (mm), municipio-ano 1998-2025:", q(q_fm), f"| CV interanual medio = {cv_ce:.2f}")
print("Ceara, chuva jan-jun IMERG (mm):", q(q_jj))
print("Ceara, P/PET Noah fev-mai (chuva municipal / PET estadual GLDAS):", q(a_fm.arid))
lo, hi = np.percentile(P_pl, [5, 95])
lo25, hi75 = np.percentile(P_pl, [25, 75])
alo, ahi = np.nanpercentile(A_pl, [5, 95])
print(f"fracao dos municipio-anos do CE (fev-mai) dentro de P5-P95 da chuva das Planicies [{lo:.0f}, {hi:.0f}] mm: {((q_fm >= lo) & (q_fm <= hi)).mean():.2%}")
print(f"  ... dentro de P25-P75 [{lo25:.0f}, {hi75:.0f}] mm: {((q_fm >= lo25) & (q_fm <= hi75)).mean():.2%}")
print(f"fracao dentro de P5-P95 da ARIDEZ P/PET das Planicies [{alo:.2f}, {ahi:.2f}]: {((a_fm.arid >= alo) & (a_fm.arid <= ahi)).mean():.2%}")
print(f"  ... abaixo de P5 da aridez das Planicies (mais seco que o mais seco de la): {(a_fm.arid < alo).mean():.2%}")
iqr_pl = np.subtract(*np.percentile(P_pl, [75, 25]))
iqr_ce = np.subtract(*np.percentile(q_fm, [75, 25]))
print(f"IQR da chuva da estacao: Planicies {iqr_pl:.0f} mm; Ceara {iqr_ce:.0f} mm -> razao {iqr_ce / iqr_pl:.2f}")

pw = pd.read_parquet(DADOS / "power/power_global_amostra.parquet")
pw = pw[pw.ponto.isin(["Iowa", "Kansas"]) & pw.param.isin(["T2M_MAX", "T2M_MIN"])].copy()
pw["mes"] = pd.to_datetime(pw.data).dt.month
tg = pw[pw.mes.between(4, 9)].groupby(["ponto", "param"]).valor.mean().unstack()
print("POWER 2020, media de Tmax e Tmin abr-set (definicao de Kluger, p. 29):", ((tg.T2M_MAX + tg.T2M_MIN) / 2).round(1).to_dict())
pc = pd.read_parquet(DERIV / "power_ce_mensal.parquet").pivot_table(index="data", columns="variavel", values="valor")
pcf = pc[pc.index.month.isin([2, 3, 4, 5])]
tce = ((pcf.T2M_MAX + pcf.T2M_MIN) / 2).groupby(pcf.index.year).mean()
print("POWER Ceara (media estadual), media de Tmax e Tmin fev-mai 1981-2025:", q(tce))

# ---------------------------------------------------------------- T3
print("\n" + "=" * 100)
print("T3. Memoria de agua no solo 0-100 cm entre safras (Noah nos dois lados)")
print("=" * 100)
sm_pl = pd.Series(np.nanmean(SM[:, cel], axis=1), index=pd.to_datetime(ds.time.values).to_period("M"))
r_pl = pd.Series(np.nanmean(R[:, cel], axis=1), index=sm_pl.index)
recs = []
for y in range(1979, 2025):
    try:
        recs.append(dict(ano=y, R=r_pl[[pd.Period(f"{y}-{m:02d}", "M") for m in range(5, 10)]].sum(),
                         S_fim=sm_pl[pd.Period(f"{y}-09", "M")], S_pre=sm_pl[pd.Period(f"{y + 1}-04", "M")],
                         R_inv=r_pl[[pd.Period(f"{y}-{m:02d}", "M") for m in (10, 11, 12)] + [pd.Period(f"{y + 1}-{m:02d}", "M") for m in (1, 2, 3)]].sum()))
    except KeyError:
        pass
mp = pd.DataFrame(recs)
print(f"Planicies (n={len(mp)} anos): corr(chuva mai-set_t, SM abr_t+1) = {mp.R.corr(mp.S_pre):.2f}; "
      f"corr(SM set_t, SM abr_t+1) = {mp.S_fim.corr(mp.S_pre):.2f}; corr(chuva out-mar, SM abr) = {mp.R_inv.corr(mp.S_pre):.2f}")
b = np.polyfit(mp.S_fim - mp.S_fim.mean(), mp.S_pre - mp.S_pre.mean(), 1)[0]
print(f"  inclinacao da anomalia SM abr_t+1 sobre SM set_t = {b:.2f} (fracao da anomalia que sobrevive ao inverno)")

imc = pd.read_parquet(DERIV / "imerg_ce_mensal.parquet")
imc = imc[imc.variavel == "precip_total"].set_index("data").valor
recs = []
for y in range(2000, 2026):
    try:
        recs.append(dict(ano=y, R=imc[[pd.Timestamp(f"{y}-{m:02d}-01") for m in range(2, 6)]].sum(),
                         S_fim=gl.loc[pd.Timestamp(f"{y}-06-01"), "SM100"], S_pre=gl.loc[pd.Timestamp(f"{y}-12-01"), "SM100"],
                         S_jan=gl.loc[pd.Timestamp(f"{y + 1}-01-01"), "SM100"] if pd.Timestamp(f"{y + 1}-01-01") in gl.index else np.nan))
    except KeyError:
        pass
mc = pd.DataFrame(recs).dropna(subset=["S_fim", "S_pre"])
print(f"Ceara (n={len(mc)} anos): corr(chuva fev-mai_t, SM dez_t) = {mc.R.corr(mc.S_pre):.2f}; "
      f"corr(SM jun_t, SM dez_t) = {mc.S_fim.corr(mc.S_pre):.2f}; corr(chuva fev-mai_t, SM jan_t+1) = {mc.R.corr(mc.S_jan):.2f}")
b2 = np.polyfit(mc.S_fim - mc.S_fim.mean(), mc.S_pre - mc.S_pre.mean(), 1)[0]
print(f"  inclinacao da anomalia SM dez sobre SM jun = {b2:.2f}")
print(f"  desvio-padrao interanual de SM: jun {mc.S_fim.std():.1f} mm, dez {mc.S_pre.std():.1f} mm; Planicies set {mp.S_fim.std():.1f}, abr {mp.S_pre.std():.1f}")
sm = pd.read_parquet(DERIV / "smap_ce_mensal.parquet")
sm = sm[sm.variavel == "sm_rootzone"].set_index("data").valor
pares = [(sm.get(pd.Timestamp(f"{y}-06-01")), sm.get(pd.Timestamp(f"{y}-12-01"))) for y in range(2015, 2026)]
pares = np.array([p for p in pares if p[0] is not None and p[1] is not None], float)
if len(pares) > 3:
    print(f"  checagem SMAP L4 raiz (CE, n={len(pares)}): corr(jun, dez) = {np.corrcoef(pares[:, 0], pares[:, 1])[0, 1]:.2f}; "
          f"dp jun {pares[:, 0].std():.4f}, dez {pares[:, 1].std():.4f} m3/m3")

# ---------------------------------------------------------------- T4
print("\n" + "=" * 100)
print("T4. Espaco por tempo no PAM Ceara: inclinacao rendimento-chuva ENTRE x DENTRO do municipio")
print("=" * 100)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam = pam[pam.cod_local.str.startswith("23")]


def prep(prefixo):
    d = pam[pam.produto.str.startswith(prefixo) & ~pam.produto.str.contains("verde")].copy()
    d = d[(d.ano >= 1998) & (d.ano <= 2025) & (d.area_plantada_ha >= 50)]
    d["rend"] = d.producao_t * 1000 / d.area_plantada_ha  # kg por ha PLANTADO (inclui perda total)
    d = d.merge(q_fm.rename("chuva").reset_index().rename(columns={"cod_mun": "cod_local"}), on=["cod_local", "ano"])
    n = d.groupby("cod_local").ano.transform("size")
    return d[n >= 15]


def inclinacoes(d):
    ym = d.rend.mean()
    # dentro: efeito fixo de municipio + tendencia linear comum
    dd = d.copy()
    for c in ["rend", "chuva", "ano"]:
        dd[c + "_w"] = dd[c] - dd.groupby("cod_local")[c].transform("mean")
    X = np.c_[dd.chuva_w / 100, dd.ano_w]
    bw = np.linalg.lstsq(X, dd.rend_w, rcond=None)[0][0]
    # entre: medias municipais
    mm = d.groupby("cod_local")[["rend", "chuva"]].mean()
    bb = np.polyfit(mm.chuva / 100, mm.rend, 1)[0]
    return 100 * bw / ym, 100 * bb / ym


for nome, pref in [("milho", "Milho"), ("feijao", "Feij")]:
    d = prep(pref)
    w, bt = inclinacoes(d)
    muns = d.cod_local.unique()
    boot = []
    grp = {k: v for k, v in d.groupby("cod_local")}
    for _ in range(300):
        s = RNG.choice(muns, len(muns), replace=True)
        db = pd.concat([grp[k].assign(cod_local=f"{k}_{i}") for i, k in enumerate(s)])
        boot.append(inclinacoes(db))
    boot = np.array(boot)
    ci = lambda v: f"[{np.percentile(v, 2.5):.1f}; {np.percentile(v, 97.5):.1f}]"
    print(f"{nome}: n={len(d)} municipio-anos, {len(muns)} municipios, rendimento medio {d.rend.mean():.0f} kg/ha plantado")
    print(f"   DENTRO (FE municipio + tendencia): {w:+.1f}% da media por +100 mm fev-mai  IC95 {ci(boot[:, 0])}")
    print(f"   ENTRE municipios (medias 1998-2025): {bt:+.1f}% por +100 mm                IC95 {ci(boot[:, 1])}")
    print(f"   diferenca entre - dentro: {bt - w:+.1f} pp  IC95 {ci(boot[:, 1] - boot[:, 0])}")
    # robustez: rendimento oficial do IBGE (por area colhida, exclui perda total)
    d2 = d[d.rendimento_kg_ha > 0].assign(rend=lambda x: x.rendimento_kg_ha)
    w2, b2_ = inclinacoes(d2)
    print(f"   robustez (rendimento IBGE por area colhida, n={len(d2)}): dentro {w2:+.1f}%  entre {b2_:+.1f}% por +100 mm")
print("\nfim")
