"""El Niño 2026-27 e o Nordeste: estado atual (NOAA), analogos historicos, condicao de entrada (NASA) e perspectiva para a quadra 2027.

Saidas em E:/campeonato-nasa/dados/el_nino_2026/: indices.csv, eventos.csv, analogos_chuva_uf.csv, analogos_rendimento_ce.csv,
estado_atual_uf.csv, smap_pctl_comparado.csv, perspectiva_uf.csv, resumo.json
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402
import xarray as xr  # noqa: E402

from comum import DADOS, DERIV, nordeste_gdf, pasta, registrar_manifesto  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
OUT = pasta("el_nino_2026")
ATUAL = DADOS / "indices_clima" / "atualizado_2026-11-14"
UF = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
SEAS = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}


def ler_oni():
    linhas = [l.split() for l in (ATUAL / "oni.ascii.txt").read_text().splitlines()[1:] if l.strip()]
    df = pd.DataFrame(linhas, columns=["seas", "ano", "total", "anom"]).astype({"ano": int, "total": float, "anom": float})
    df["mes"] = df.seas.map(SEAS)
    df["data"] = pd.to_datetime(dict(year=df.ano, month=df.mes, day=1))
    return df.set_index("data").anom.rename("ONI")


def ler_psl(nome):
    txt = (ATUAL / f"{nome}.data").read_text().splitlines()
    a0, a1 = map(int, txt[0].split()[:2])
    vals = {}
    for l in txt[1:]:
        p = l.split()
        if len(p) == 13 and re.fullmatch(r"\d{4}", p[0]):
            for m, v in enumerate(p[1:], 1):
                v = float(v)
                if v > -99:
                    vals[pd.Timestamp(int(p[0]), m, 1)] = v
    return pd.Series(vals, name=nome.upper()).sort_index()


oni, tna, tsa = ler_oni(), ler_psl("tna"), ler_psl("tsa")
idx = pd.concat([oni, tna, tsa], axis=1)
idx["DIPOLO"] = idx.TNA - idx.TSA
idx.to_csv(OUT / "indices.csv")
print("ONI mais recente:", oni.index[-1].strftime("%Y-%m"), oni.iloc[-1], "| TNA", tna.index[-1].strftime("%Y-%m"), round(tna.iloc[-1], 2),
      "| TSA", round(tsa.iloc[-1], 2), "| dipolo", round(tna.iloc[-1] - tsa.iloc[-1], 2))

# ---------- eventos de El Niño: pico de ONI em OND/NDJ do ano Y (quadra afetada = Y+1) ----------
pico = oni[oni.index.month.isin([11, 12])].groupby(oni[oni.index.month.isin([11, 12])].index.year).max()
ev = pd.DataFrame({"ONI_OND_NDJ": pico})
ev["quadra_afetada"] = ev.index + 1
ev["categoria"] = pd.cut(ev.ONI_OND_NDJ, [-9, 0.5, 1.0, 1.5, 2.0, 9], labels=["neutro/La Niña", "fraco", "moderado", "forte", "muito forte"])
fma = idx.DIPOLO[idx.index.month.isin([2, 3, 4])]
dip_fma = fma.groupby(fma.index.year).mean()
ev["dipolo_FMA_quadra"] = ev.quadra_afetada.map(dip_fma)
ev.to_csv(OUT / "eventos.csv")
fortes = ev[ev.ONI_OND_NDJ >= 1.5]
print("El Niños fortes/muito fortes (ONI OND-NDJ >= 1,5):", fortes[["ONI_OND_NDJ", "quadra_afetada", "dipolo_FMA_quadra"]].round(2).to_dict("index"))

# ---------- chuva da quadra (fev-mai) por UF: IMERG 1998+; Ceara POWER 1981+ ----------
im = pd.read_parquet(DERIV / "imerg_ne_mensal.parquet")
im = im[im.variavel == "precip_total"].assign(data=lambda d: pd.to_datetime(d.data))
im = im[im.data.dt.month.isin([2, 3, 4, 5])]
cont = im.groupby(["uf", im.data.dt.year]).valor.count()
fmam = im.groupby(["uf", im.data.dt.year]).valor.sum()[cont == 4].unstack(0)
fmam.index.name = "ano"
pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw = pw[pw.variavel == "PRECTOTCORR"].assign(data=lambda d: pd.to_datetime(d.data))
pw["mm"] = pw.valor * pw.data.dt.days_in_month
pw = pw[pw.data.dt.month.isin([2, 3, 4, 5])]
cpw = pw.groupby(pw.data.dt.year).mm.count()
fmam_pw_ce = pw.groupby(pw.data.dt.year).mm.sum()[cpw == 4]
clim = fmam[fmam.index <= 2025]
terc = clim.quantile([1 / 3, 2 / 3])
anal = []
for ano, e in fortes.iterrows():
    q = int(e.quadra_afetada)
    lin = {"evento": f"{ano}/{str(q)[2:]}", "ONI_OND_NDJ": round(e.ONI_OND_NDJ, 2), "dipolo_FMA": round(e.dipolo_FMA_quadra, 2) if pd.notna(e.dipolo_FMA_quadra) else None}
    if q in fmam_pw_ce.index:
        lin["CE_POWER_%normal"] = round(100 * fmam_pw_ce[q] / fmam_pw_ce[(fmam_pw_ce.index <= 2025)].mean(), 0)
    for uf in UF.values():
        if q in fmam.index and uf in fmam:
            lin[f"{uf}_%normal"] = round(100 * fmam.loc[q, uf] / clim[uf].mean(), 0)
            lin[f"{uf}_tercil"] = "abaixo" if fmam.loc[q, uf] <= terc.loc[1 / 3, uf] else ("acima" if fmam.loc[q, uf] >= terc.loc[2 / 3, uf] else "normal")
    anal.append(lin)
A = pd.DataFrame(anal)
A.to_csv(OUT / "analogos_chuva_uf.csv", index=False)
print(A.to_string())

# ---------- rendimento no Ceara nos anos de analogo (PAM; razao para a mediana movel de 7 anos) ----------
pam = pd.read_parquet(DERIV / "ibge_pam_ce_anual.parquet")
pam["ano"] = pd.to_datetime(pam.data).dt.year
rend = pam[pam.variavel == "rendimento_kg_ha"].pivot_table(index="ano", columns="produto", values="valor")
culturas = [c for c in rend.columns if c.startswith(("Milho", "Feijão", "Mandioca"))]
dev = {c: (rend[c] / rend[c].rolling(7, center=True, min_periods=3).median() - 1) * 100 for c in culturas}
dev = pd.DataFrame(dev)
R = dev.reindex(fortes.quadra_afetada.astype(int)).round(0)
R.index.name = "quadra"
R["ONI"] = fortes.set_index(fortes.quadra_afetada.astype(int)).ONI_OND_NDJ.round(2)
R.to_csv(OUT / "analogos_rendimento_ce.csv")
print("\nDesvio de rendimento no Ceará (%), quadras após El Niño forte:\n", R.to_string())
outros = dev[~dev.index.isin(fortes.quadra_afetada)]
print("Média dos outros anos:", outros.mean().round(1).to_dict())

# ---------- estado atual: chuva ago-nov/2026 por UF (IMERG Late+Early) ----------
ne = nordeste_gdf()
late = xr.open_dataset(DADOS / "imerg" / "imerg_v07_late_diario_ne_recente.nc")
early = xr.open_dataset(DADOS / "imerg" / "imerg_v07_early_diario_ne_recente.nc")
ult_late = pd.Timestamp(late.time.values.max())
rec = xr.concat([late.precipitation, early.precipitation.sel(time=slice(ult_late + pd.Timedelta(days=1), None))], dim="time")
lo, la = np.meshgrid(rec.lon.values, rec.lat.values)
imm = pd.read_parquet(DERIV / "imerg_ne_mensal.parquet")
imm = imm[imm.variavel == "precip_total"].assign(data=lambda d: pd.to_datetime(d.data))
atual = []
ini, fim = pd.Timestamp("2026-08-01"), pd.Timestamp(rec.time.values.max())
for _, u in ne.iterrows():
    sig = UF[str(u.codarea)]
    m = xr.DataArray(shapely.contains_xy(u.geometry, lo, la), dims=("lat", "lon"), coords={"lat": rec.lat, "lon": rec.lon})
    tot = float(rec.where(m).mean(("lat", "lon")).sum())
    h = imm[(imm.uf == sig) & (imm.data.dt.year.between(1998, 2025))]
    # climatologia ago->dia final de nov, proporcional nos dias de novembro
    frac_nov = fim.day / 30
    cl = h[h.data.dt.month.isin([8, 9, 10])].groupby(h.data.dt.year).valor.sum() + frac_nov * h[h.data.dt.month == 11].groupby(h.data.dt.year).valor.sum()
    atual.append({"UF": sig, "chuva_ago_nov2026_mm": round(tot, 1), "normal_mm": round(cl.mean(), 1),
                  "%normal": round(100 * tot / cl.mean(), 0), "percentil": round(100 * (cl < tot).mean(), 0)})
AT = pd.DataFrame(atual)
print(f"\nChuva 01/08 a {fim:%d/%m}/2026 por UF (IMERG V07 Late/Early):\n", AT.to_string(index=False))

# ---------- SMAP L4: umidade da zona da raiz nos 30 dias ate a ultima data, comparada entre os 12 anos ----------
# ATENCAO: o percentil pronto (sm_rootzone_pctl) quase nao existe no Nordeste em out-jan (no Ceara, < 0,5% das
# celulas). Por isso usamos a umidade bruta (sm_rootzone, m3/m3) e a posicao de cada ano entre 2015 e 2026.
sm = xr.open_dataset(DADOS / "smap" / "smap_l4_diario_ne.nc")
smt = pd.Timestamp(sm.time.values.max())
lo2, la2 = np.meshgrid(sm.lon.values, sm.lat.values)
linhas = []
for _, u in ne.iterrows():
    sig = UF[str(u.codarea)]
    m = xr.DataArray(shapely.contains_xy(u.geometry, lo2, la2), dims=("lat", "lon"), coords={"lat": sm.lat, "lon": sm.lon})
    for ano in range(2015, 2027):
        f = pd.Timestamp(ano, smt.month, smt.day)
        jan = sm.sm_rootzone.sel(time=slice(f - pd.Timedelta(days=29), f))
        linhas.append({"UF": sig, "ano": ano, "rz": float(jan.where(m).mean())})
SMt = pd.DataFrame(linhas)
SMt["posto"] = SMt.groupby("UF").rz.rank(method="min").astype(int)
n_anos = SMt.ano.nunique()
SM = SMt[SMt.ano.isin([2015, 2023, 2026])].pivot_table(index="UF", columns="ano", values="posto").astype(int)
SM.columns = [f"posto_{c}" for c in SM.columns]
SM["umidade_raiz_2026_m3m3"] = SMt[SMt.ano == 2026].set_index("UF").rz.round(3)
SM = SM.reset_index()
SM.to_csv(OUT / "smap_pctl_comparado.csv", index=False)
print(f"\nSMAP L4: posição da umidade da zona da raiz nos 30 dias até {smt:%d/%m} entre {n_anos} anos (1 = o mais seco):\n", SM.to_string(index=False))

# ---------- GRACE e NDVI VIIRS: 2026 x mesma época de 2015 e 2023 ----------
gr = pd.read_parquet(DERIV / "grace_ce_mensal.parquet").assign(data=lambda d: pd.to_datetime(d.data)).set_index("data").valor
grne = pd.read_parquet(DERIV / "grace_ne_mensal.parquet").assign(data=lambda d: pd.to_datetime(d.data)).set_index("data").valor
g_ult = gr.index.max()
grace = {f"GRACE_CE_{a}": round(float(gr.get(pd.Timestamp(a, g_ult.month, 1), np.nan)), 1) for a in (2015, 2023, 2026)}
grace.update({f"GRACE_NE_{a}": round(float(grne.get(pd.Timestamp(a, g_ult.month, 1), np.nan)), 1) for a in (2015, 2023, 2026)})
vi = pd.read_parquet(DERIV / "viirs_ndvi_ce_mensal.parquet").assign(data=lambda d: pd.to_datetime(d.data)).set_index("data").valor
v_ult = vi.index.max()
clim_v = vi[vi.index.month == v_ult.month]
ndvi = {f"NDVI_CE_{a}": round(float(vi.get(pd.Timestamp(a, v_ult.month, 1), np.nan)), 3) for a in (2015, 2023, 2026)}
ndvi["NDVI_CE_climatologia"] = round(float(clim_v[clim_v.index.year <= 2025].mean()), 3)
print(f"\nGRACE ({g_ult:%m}/AAAA, cm):", grace, f"\nNDVI VIIRS ({v_ult:%m}/AAAA):", ndvi)

# ---------- perspectiva empírica para a quadra 2027 ----------
persp = []
for uf in UF.values():
    if uf not in fmam:
        continue
    q = [int(x) for x in fortes.quadra_afetada if int(x) in fmam.index]
    vals = fmam.loc[q, uf]
    persp.append({"UF": uf, "n_analogos_IMERG": len(q), "anos": ",".join(map(str, q)),
                  "freq_tercil_inferior": f"{int((vals <= terc.loc[1 / 3, uf]).sum())}/{len(q)}",
                  "mediana_%normal": round(100 * vals.median() / clim[uf].mean(), 0)})
if len(fmam_pw_ce):
    q = [int(x) for x in fortes.quadra_afetada if int(x) in fmam_pw_ce.index]
    t1 = fmam_pw_ce[fmam_pw_ce.index <= 2025].quantile(1 / 3)
    persp.append({"UF": "CE (POWER 1981+)", "n_analogos_IMERG": len(q), "anos": ",".join(map(str, q)),
                  "freq_tercil_inferior": f"{int((fmam_pw_ce[q] <= t1).sum())}/{len(q)}",
                  "mediana_%normal": round(100 * fmam_pw_ce[q].median() / fmam_pw_ce[fmam_pw_ce.index <= 2025].mean(), 0)})
PE = pd.DataFrame(persp)
PE.to_csv(OUT / "perspectiva_uf.csv", index=False)
print("\nPerspectiva empírica (análogos de El Niño forte):\n", PE.to_string(index=False))

AT.to_csv(OUT / "estado_atual_uf.csv", index=False)
resumo = {"ONI_ultimo": [oni.index[-1].strftime("%Y-%m"), float(oni.iloc[-1])], "TNA_ultimo": [tna.index[-1].strftime("%Y-%m"), float(tna.iloc[-1])],
          "TSA_ultimo": [tsa.index[-1].strftime("%Y-%m"), float(tsa.iloc[-1])], "eventos_fortes": fortes.round(2).reset_index().to_dict("records"),
          "grace": grace, "ndvi": ndvi, "smap_data_final": str(smt.date()), "imerg_data_final": str(fim.date())}
(OUT / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
registrar_manifesto("el_nino_2026", {"fonte": "NOAA CPC (ONI, Niño semanal, discussão ENSO 12/11/2026), NOAA PSL (TNA/TSA), NASA IMERG/SMAP/GRACE/VIIRS, IBGE PAM",
                                     "saidas": [p.name for p in OUT.glob("*.csv")]})
