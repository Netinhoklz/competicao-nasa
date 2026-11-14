"""Curador de bases (v3), teste C: umidade do solo da NASA (SMAP L4 v008, SMAP L3 v006, GLDAS CLSM) x rede de
sensores do CEMADEN no semiarido (Zeri et al., Mendeley Data, doi 10.17632/xrk5rfcpvg.2; EC-5 a 10 e 20 cm, horario
UTC, ago/2015-abr/2019, 360 PCDs). Conversao: v3_curador_converter_cemaden.py.

C1. Tempo ("quando"): por estacao, celula mais proxima; r bruto, r da anomalia (tira a climatologia do dia do ano,
    suavizada em 31 dias, da propria serie), ubRMSD e vies. L4 sm_surface (0-5 cm) x 10 cm; L4 sm_rootzone (0-100 cm) e
    CLSM zona da raiz x media 10-20 cm; L3 AM (06h local, qualidade recomendada) x media diaria de 10 cm.
C2. Nivel: media do nivel absoluto por produto x campo (qual nivel da NASA esta mais perto do sensor?).
C3. Espaco ("onde") nos portoes 28/fev, 19/mar e 30/abr de 2016-2019: posto (percentil proprio) da media de 7 dias
    de cada estacao x o mesmo para a celula SMAP; Spearman entre estacoes na mesma data.
C4. Luz do solo: percentil proprio < 20 no 30/abr (7 dias) pelo SMAP L4 x pelo sensor, concordancia.
So le arquivos; imprime na saida padrao.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import numpy as np
import pandas as pd
import xarray as xr

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
C = DADOS / "complementares" / "cemaden"
dia = pd.read_parquet(C / "cemaden_diario.parquet")
est = pd.read_parquet(C / "cemaden_estacoes.parquet").set_index("estacao")
dia["data"] = pd.to_datetime(dia.data)
dia["us1020"] = dia[["us10_13utc", "us20_13utc"]].mean(axis=1, skipna=False)
T0, T1 = "2015-04-01", "2019-05-01"
print(f"CEMADEN: {est.shape[0]} estacoes; {dia.us10_media.notna().sum():,} estacao-dias com 10 cm;"
      f" {dia.data.min().date()} a {dia.data.max().date()}")
print("por UF:", est.state.value_counts().to_dict())
print("textura (g/kg), mediana: areia", est.sand.astype(float).median(), "| argila", est.clay.astype(float).median())


def abre(f, vars_):
    ds = xr.open_dataset(f)[vars_].sel(time=slice(T0, T1))
    _, iu = np.unique(ds.time.values, return_index=True)  # 4 datas repetidas no L4
    return ds.isel(time=np.sort(iu))


L4 = abre(DADOS / "smap" / "smap_l4_diario_ne.nc", ["sm_surface", "sm_rootzone"])
L3 = abre(DADOS / "smap" / "smap_l3_diario_ne.nc", ["sm_am", "qual_am"])
CL = abre(DADOS / "gldas" / "gldas_clsm025_diario_ne.nc", ["SoilMoist_S_tavg", "SoilMoist_RZ_tavg"])


def extrai(ds, var, lats, lons):
    iy = np.abs(ds.lat.values[None, :] - lats[:, None]).argmin(1)
    ix = np.abs(ds.lon.values[None, :] - lons[:, None]).argmin(1)
    v = ds[var].isel(lat=xr.DataArray(iy, dims="e"), lon=xr.DataArray(ix, dims="e")).load().values
    return pd.DataFrame(v, index=pd.to_datetime(ds.time.values).floor("D"))


ids = est.index.values
la, lo = est.latitude.astype(float).values, est.longitude.astype(float).values
S = {"L4_sup": extrai(L4, "sm_surface", la, lo), "L4_rz": extrai(L4, "sm_rootzone", la, lo)}
am = extrai(L3, "sm_am", la, lo); qa = extrai(L3, "qual_am", la, lo)
S["L3_am"] = am.where((qa.values.astype(int) & 1) == 0)
S["CLSM_sup"] = extrai(CL, "SoilMoist_S_tavg", la, lo) / 20.0     # kg/m2 em 0-2 cm -> m3/m3
S["CLSM_rz"] = extrai(CL, "SoilMoist_RZ_tavg", la, lo) / 1000.0   # kg/m2 em 0-100 cm -> m3/m3
for k in S:
    S[k].columns = ids
    S[k] = S[k].where(S[k] > 0)
G = {c: dia.pivot(index="data", columns="estacao", values=c).reindex(columns=ids) for c in
     ["us10_13utc", "us1020", "us10_media"]}


def anom(x):
    clim = x.groupby(x.index.dayofyear).mean()
    clim = pd.concat([clim.iloc[-15:], clim, clim.iloc[:15]]).rolling(31, center=True, min_periods=5).mean().iloc[15:-15]
    return x - clim.reindex(x.index.dayofyear).values


PARES = [("L4_sup", "us10_13utc", "L4 superficie 0-5 cm x 10 cm (13 UTC)"),
         ("L4_rz", "us1020", "L4 zona da raiz x media 10-20 cm (13 UTC)"),
         ("L3_am", "us10_media", "L3 AM (qualidade recomendada) x 10 cm, media diaria"),
         ("CLSM_sup", "us10_media", "GLDAS CLSM superficie x 10 cm, media diaria"),
         ("CLSM_rz", "us1020", "GLDAS CLSM zona da raiz x media 10-20 cm")]
print("\n" + "=" * 20, "C1/C2. Tempo e nivel por estacao (min. 180 dias em comum)", "=" * 20)
res = {}
for ks, kg, rot in PARES:
    lin = []
    for e in ids:
        s, g = S[ks][e], G[kg][e].reindex(S[ks].index)
        m = s.notna() & g.notna()
        if m.sum() < 180:
            continue
        s2, g2 = s[m], g[m]
        sa, ga = anom(s.where(m)), anom(g.where(m))
        ma = sa.notna() & ga.notna()
        lin.append({"est": e, "n": int(m.sum()), "r": np.corrcoef(s2, g2)[0, 1],
                    "r_anom": np.corrcoef(sa[ma], ga[ma])[0, 1] if ma.sum() > 100 else np.nan,
                    "ubrmsd": np.sqrt(np.mean(((s2 - s2.mean()) - (g2 - g2.mean())) ** 2)),
                    "vies": (s2 - g2).mean(), "nivel_nasa": s2.mean(), "nivel_campo": g2.mean()})
    R = pd.DataFrame(lin).set_index("est")
    res[ks] = R
    q = R.median()
    print(f"{rot}\n   estacoes {len(R)} | r mediano {q.r:.2f} (p10 {R.r.quantile(.1):.2f}, p90 {R.r.quantile(.9):.2f})"
          f" | r anomalia {q.r_anom:.2f} | ubRMSD {q.ubrmsd:.3f} | vies {q.vies:+.3f} m3/m3"
          f" | nivel NASA {q.nivel_nasa:.3f} x campo {q.nivel_campo:.3f} | ubRMSD <= 0,04 em {(R.ubrmsd <= 0.04).mean():.0%}")
# r x textura (o sensor EC-5 com calibracao padrao erra mais em solo argiloso?)
R = res["L4_rz"].join(est[["sand", "clay", "state"]].astype({"sand": float, "clay": float}))
print("\nL4 zona da raiz: r por tercil de areia:",
      R.groupby(pd.qcut(R.sand, 3, labels=["menos areia", "meio", "mais areia"]))["r"].median().round(2).to_dict())
print("L4 zona da raiz: r mediano por UF:", R.groupby("state")["r"].median().round(2).to_dict())
print("Ceara (L4 zona da raiz):", R[R.state == "CE"][["r", "r_anom", "ubrmsd", "vies"]].median().round(3).to_dict(),
      "n =", int((R.state == "CE").sum()))

# ---------------- C3. espaco nos portoes
print("\n" + "=" * 20, "C3. 'Onde': ordem entre estacoes na mesma data (percentil proprio, media de 7 dias)", "=" * 20)


def pct_proprio(x):  # posto de cada dia dentro da propria serie da estacao/celula, no periodo comum
    return x.rank(pct=True) * 100


m_ok = G["us1020"].notna() & S["L4_rz"].reindex(G["us1020"].index).notna()
g_p = pct_proprio(G["us1020"].where(m_ok)).rolling(7, min_periods=4).mean()
s_p = pct_proprio(S["L4_rz"].reindex(G["us1020"].index).where(m_ok)).rolling(7, min_periods=4).mean()
g_abs = G["us1020"].where(m_ok).rolling(7, min_periods=4).mean()
s_abs = S["L4_rz"].reindex(G["us1020"].index).where(m_ok).rolling(7, min_periods=4).mean()
lin = []
for a in [2016, 2017, 2018, 2019]:
    for md in ["02-28", "03-19", "04-30"]:
        d = pd.Timestamp(f"{a}-{md}")
        if d not in g_p.index:
            continue
        x, y = g_p.loc[d], s_p.loc[d]
        m = x.notna() & y.notna()
        xa, ya = g_abs.loc[d], s_abs.loc[d]
        lin.append({"data": d.date(), "n_est": int(m.sum()),
                    "rho_percentil": x[m].corr(y[m], method="spearman"),
                    "rho_nivel": xa[m].corr(ya[m], method="spearman"),
                    "luz_campo_%": (x[m] < 20).mean() * 100, "luz_smap_%": (y[m] < 20).mean() * 100,
                    "concorda_luz_%": ((x[m] < 20) == (y[m] < 20)).mean() * 100})
C3 = pd.DataFrame(lin)
print(C3.round(2).to_string(index=False))
print("mediana rho_percentil:", round(C3.rho_percentil.median(), 2), "| rho_nivel:", round(C3.rho_nivel.median(), 2))
print("nota: percentil proprio com ~3,5 anos de serie; 'luz' = percentil < 20 (regra do portao do QUADRA, aqui em",
      "percentil proprio, nao o sm_rootzone_pctl do produto).")
