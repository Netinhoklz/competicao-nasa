"""Curador de bases (v3), teste A: chuva IMERG V07 (via POWER, dia UTC, 0,1 grau) x pluviometros da FUNCEME no Ceara.

Fonte de campo: https://cdn.funceme.br/calendario/postos/postos.zip (link "Dados dos postos do Ceara" do Calendario
de Chuvas, chuvas.funceme.br; baixado em 14/11/2026, Last-Modified 13/11/2026). Um .txt por posto:
Municipios;Postos;Latitude;Longitude;Anos;Meses;Total;Dia1..Dia31, com 999 = sem leitura e 888 = dia inexistente.
A FUNCEME le o pluviometro as 7h (hora local) e atribui ao dia da leitura: o total do dia D cobre ~10 UTC de D-1 a
10 UTC de D. Por isso o teste mede a defasagem que maximiza a correlacao antes de tudo.

Blocos:
 A1. Ponto: cada posto x celula IMERG mais proxima (1998-2025): r diario (defasagem 0 e -1), r mensal, razao de
     volume, POD/FAR de dia chuvoso (>= 1 mm), frequencia de dias >= 1 mm.
 A2. Municipio (a escala do QUADRA): media dos postos do municipio x media IMERG do municipio (cache do estrategista),
     acumulado desde 1/jan ate cada portao em % do normal (mediana dos outros anos), mesma receita canonica.
     Correlacao total e dentro do ano; AUC da quebra canonica do milho com cada fonte nos MESMOS municipio-anos.
 A3. Veranico na quadra (fev-abr): maior sequencia de dias com <= 2 mm e n de dias <= 2 mm, IMERG x postos.
Saidas: E:/campeonato-nasa/dados/complementares/funceme/funceme_postos_diario.parquet (cache) e
        conselho/analises/v3_curador_valida_imerg_funceme.saida.txt (via redirecionamento).
"""
import sys
import warnings
import zipfile
import io

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from sklearn.metrics import roc_auc_score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
BASE = DADOS / "complementares" / "funceme"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
D = "E:/campeonato-nasa/dados/derivados/"
rng = np.random.default_rng(0)

# ---------------- 0) postos FUNCEME -> longo diario
CACHE = BASE / "funceme_postos_diario.parquet"
CACHE_META = BASE / "funceme_postos_meta.parquet"
if CACHE.exists():
    dia = pd.read_parquet(CACHE)
    meta = pd.read_parquet(CACHE_META)
else:
    z = zipfile.ZipFile(BASE / "bruto" / "postos.zip")
    partes, metas = [], []
    for nome in z.namelist():
        if not nome.endswith(".txt"):
            continue
        t = pd.read_csv(io.BytesIO(z.read(nome)), sep=";", encoding="latin1")
        if t.empty:
            continue
        pid = int(nome.split(".")[0])
        metas.append({"posto": pid, "municipio": t.Municipios.iloc[0], "nome": t.Postos.iloc[0],
                      "lat": float(t.Latitude.iloc[0]), "lon": float(t.Longitude.iloc[0])})
        dcols = [f"Dia{i}" for i in range(1, 32)]
        L = t.melt(id_vars=["Anos", "Meses"], value_vars=dcols, var_name="d", value_name="mm")
        L["d"] = L["d"].str[3:].astype(int)
        L = L[L.mm != 888]
        L["mm"] = L.mm.where(L.mm != 999)
        L["data"] = pd.to_datetime(dict(year=L.Anos, month=L.Meses, day=L.d), errors="coerce")
        L = L.dropna(subset=["data"])
        L["posto"] = pid
        partes.append(L[["posto", "data", "mm"]])
    dia = pd.concat(partes, ignore_index=True)
    dia["mm"] = dia.mm.astype("float32")
    meta = pd.DataFrame(metas)
    dia.to_parquet(CACHE, index=False)
    meta.to_parquet(CACHE_META, index=False)
    registrar_manifesto("complementares/funceme", {
        "fonte": "FUNCEME, postos pluviometricos do Ceara (Calendario de Chuvas)",
        "url": "https://cdn.funceme.br/calendario/postos/postos.zip",
        "outros": ["https://cdn.funceme.br/calendario-chuvas/rain-repository-by-mendonca-2020/Original.zip",
                   "https://cdn.funceme.br/calendario-chuvas/rain-repository-by-mendonca-2020/Reconstructed.zip"],
        "convencao": "leitura as 7h local; 999 = sem leitura; 888 = dia inexistente",
        "postos": int(meta.posto.nunique()),
        "periodo": [str(dia.data.min().date()), str(dia.data.max().date())],
        "arquivos": ["bruto/postos.zip", "bruto/Original.zip", "bruto/Reconstructed.zip",
                     "funceme_postos_diario.parquet", "funceme_postos_meta.parquet"],
        "script": "conselho/analises/v3_curador_valida_imerg_funceme.py",
    }, base=BASE)
print(f"FUNCEME: {meta.posto.nunique()} postos, {dia.mm.notna().sum():,} leituras validas, "
      f"{dia.data.min().date()} a {dia.data.max().date()}")
ok = dia[dia.mm.notna()]
print("postos com leitura em 2025:", ok[ok.data.dt.year == 2025].posto.nunique(),
      "| em 2026:", ok[ok.data.dt.year == 2026].posto.nunique())

# ---------------- 1) IMERG CE diario (ja em memoria, ~100 MB)
im = xr.open_mfdataset(sorted((DADOS / "imerg").glob("imerg_ce_diario_*.nc")), combine="by_coords")["precip"]
im = im.sel(time=slice("1998-01-01", "2025-12-31")).load()
im = im.where(im >= 0)
tim = pd.to_datetime(im.time.values)
lat_g, lon_g = im.lat.values, im.lon.values

# ---------------- A1. ponto
print("\n" + "=" * 20, "A1. Posto x celula IMERG mais proxima (1998-2025)", "=" * 20)
W = ok[(ok.data >= "1998-01-01") & (ok.data <= "2025-12-31")]
cont = W.groupby("posto").size()
sel = cont[cont >= 3650].index  # >= 10 anos de leituras
M = W[W.posto.isin(sel)].pivot(index="data", columns="posto", values="mm").reindex(tim)
mt = meta.set_index("posto").loc[sel]
iy = np.abs(lat_g[None, :] - mt.lat.values[:, None]).argmin(1)
ix = np.abs(lon_g[None, :] - mt.lon.values[:, None]).argmin(1)
I = pd.DataFrame(im.values[:, iy, ix], index=tim, columns=sel)
print(f"postos com >= 10 anos de leitura em 1998-2025: {len(sel)}")


def r_col(a, b):
    m = a.notna() & b.notna()
    return np.corrcoef(a[m], b[m])[0, 1] if m.sum() > 300 else np.nan


lin = []
for p in sel:
    g, s = M[p], I[p]
    r0 = r_col(g, s)
    r1 = r_col(g, s.shift(1))   # IMERG do dia anterior x leitura das 7h
    rm1 = r_col(g, s.shift(-1))  # IMERG do dia seguinte x posto(D)
    lin.append({"posto": p, "r_lag0": r0, "r_lag1": r1, "r_lagm1": rm1})
R = pd.DataFrame(lin).set_index("posto")
print(f"r diario mediano: defasagem 0 = {R.r_lag0.median():.3f}; IMERG(D-1) x posto(D) = {R.r_lag1.median():.3f}; "
      f"IMERG(D+1) x posto(D) = {R.r_lagm1.median():.3f}; lag 1 melhor em {(R.r_lag1 > R.r_lag0).mean():.0%} dos postos")
LAG = 1 if R.r_lag1.median() > R.r_lag0.median() else 0
Ia = I.shift(LAG)  # IMERG alinhado ao dia da leitura
lin = []
for p in sel:
    g, s = M[p], Ia[p]
    m = g.notna() & s.notna()
    g, s = g[m], s[m]
    gm, sm = g.resample("MS").sum(min_count=25), s.resample("MS").sum(min_count=25)
    q = (g.index.month >= 2) & (g.index.month <= 5)
    wet_g, wet_s = g >= 1, s >= 1
    hits = (wet_g & wet_s).sum()
    lin.append({"posto": p, "lat": mt.lat[p], "lon": mt.lon[p], "n_dias": int(m.sum()),
                "r_dia": np.corrcoef(g, s)[0, 1], "r_dia_fev_mai": np.corrcoef(g[q], s[q])[0, 1],
                "r_5d": np.corrcoef(g.rolling(5).sum().dropna(), s.rolling(5).sum().dropna())[0, 1],
                "r_mes": gm.corr(sm), "razao_volume": s.sum() / g.sum(),
                "pod": hits / wet_g.sum(), "far": (wet_s & ~wet_g).sum() / wet_s.sum(),
                "freq_g": wet_g.mean(), "freq_s": wet_s.mean(),
                "p99_g": np.percentile(g[g > 0], 99), "p99_s": np.percentile(s[s > 0.1], 99)})
P1 = pd.DataFrame(lin)
q = P1.describe(percentiles=[0.1, 0.5, 0.9]).T[["10%", "50%", "90%"]]
print(q.round(3).to_string())
# geografia do vies: litoral (lon > -38.6 e lat > -4.5, faixa de ~60 km) x serra x sertao
P1["zona"] = np.where((P1.lat > -3.9) | ((P1.lon > -38.4) & (P1.lat > -4.8)), "litoral/norte", "interior")
print(P1.groupby("zona")[["r_dia", "r_mes", "razao_volume", "pod", "far"]].median().round(3).to_string(),
      "\n n:", P1.zona.value_counts().to_dict())

# ---------------- A2. municipio, portoes
print("\n" + "=" * 20, "A2. Municipio: acumulado ate o portao, % do normal, IMERG x postos FUNCEME", "=" * 20)
mun = gpd.read_file(REF / "ceara_municipios.geojson")
pts = gpd.GeoDataFrame(meta, geometry=gpd.points_from_xy(meta.lon, meta.lat), crs=mun.crs)
pj = gpd.sjoin(pts, mun[["codarea", "geometry"]], predicate="within")[["posto", "codarea"]]
W2 = W.merge(pj, on="posto")
cnt = W2.groupby(["codarea", "data"]).mm.count()
gmun = W2.groupby(["codarea", "data"]).mm.mean().unstack(0)  # data x mun
gmun.index = pd.to_datetime(gmun.index)
gmun = gmun.reindex(tim)
gmun.columns = gmun.columns.astype(str)
print("municipios com pelo menos 1 posto (1998-2025):", gmun.notna().any().sum(), "| postos por municipio (mediana):",
      int(pj.groupby("codarea").size().median()))
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
chuva = chuva.reindex(tim).shift(LAG)
comuns = [c for c in gmun.columns if c in chuva.columns]
anos = list(range(1998, 2026))


def serie(prefixo):  # receita canonica (arquiteto_final_curvas_quixada.py)
    pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
    p = pam[pam["produto"].str.startswith(prefixo)].copy()
    p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha

    def med_outros(g):
        v = g["r"].values
        out = np.array([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))])
        return pd.Series(out, index=g.index)

    p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
    p["razao"] = p.r / p.ref
    p["quebra"] = (p.razao < 0.5).astype(int)
    p["cod"] = p.cod_local.astype(str).str[:7]
    return p.dropna(subset=["razao"])


mi = serie("Milho (em gr")[["cod", "ano", "quebra"]]


def acum(df, m, d):
    """acumulado 1/jan -> portao por ano x mun; NaN se faltar > 10% dos dias (so para os postos)."""
    out, cob = {}, {}
    for a in anos:
        x = df.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}", comuns]
        out[a] = x.sum(min_count=1)
        cob[a] = x.notna().mean()
    return pd.DataFrame(out).T, pd.DataFrame(cob).T


def pct(ac):
    o = ac.copy() * np.nan
    for a in anos:
        o.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return o


def auc_dentro(df, col):
    num = den = 0.0
    for a, g in df.groupby("ano"):
        npos, nneg = g.quebra.sum(), (1 - g.quebra).sum()
        if npos >= 3 and nneg >= 3:
            w = npos * nneg
            num += w * roc_auc_score(g.quebra, g[col]); den += w
    return num / den if den else np.nan


PORT = {"31/jan": (1, 31), "28/fev": (2, 28), "19/mar": (3, 19), "30/abr": (4, 30)}
tab = []
for nome, (m, d) in PORT.items():
    ag, cg = acum(gmun, m, d)
    ai, _ = acum(chuva, m, d)
    ag = ag.where(cg >= 0.9)
    ai = ai.where(ag.notna())
    pg, pi = pct(ag), pct(ai)
    L = pd.DataFrame({"pct_posto": pg.stack(), "pct_imerg": pi.stack(),
                      "mm_posto": ag.stack(), "mm_imerg": ai.stack()}).dropna().reset_index()
    L.columns = ["ano", "cod", "pct_posto", "pct_imerg", "mm_posto", "mm_imerg"]
    rr = L[["pct_posto", "pct_imerg"]].corr(method="spearman").iloc[0, 1]
    rd = np.nanmedian([g.pct_posto.corr(g.pct_imerg, method="spearman") for _, g in L.groupby("ano") if len(g) > 20])
    rv = np.nanmedian([g.mm_posto.corr(g.mm_imerg, method="spearman") for _, g in L.groupby("ano") if len(g) > 20])
    X = mi.merge(L, on=["cod", "ano"])
    X["s_posto"], X["s_imerg"] = -X.pct_posto.clip(upper=3), -X.pct_imerg.clip(upper=3)
    tab.append({"portao": nome, "mun_anos": len(L), "rho_pct": rr, "rho_dentro_ano_pct": rd,
                "rho_dentro_ano_mm": rv, "razao_mm_imerg/posto": L.mm_imerg.sum() / L.mm_posto.sum(),
                "n_auc": len(X), "quebras": int(X.quebra.sum()),
                "AUC_posto": roc_auc_score(X.quebra, X.s_posto), "AUC_imerg": roc_auc_score(X.quebra, X.s_imerg),
                "AUCdentro_posto": auc_dentro(X, "s_posto"), "AUCdentro_imerg": auc_dentro(X, "s_imerg")})
    if nome == "30/abr":
        X30 = X.copy()
T = pd.DataFrame(tab).set_index("portao")
print(T.round(3).to_string())

# bootstrap por ano da diferenca AUC_posto - AUC_imerg no 30/abr e 19/mar
for nome in ["19/mar", "30/abr"]:
    m, d = PORT[nome]
    ag, cg = acum(gmun, m, d); ai, _ = acum(chuva, m, d)
    ag = ag.where(cg >= 0.9); ai = ai.where(ag.notna())
    L = pd.DataFrame({"pct_posto": pct(ag).stack(), "pct_imerg": pct(ai).stack()}).dropna().reset_index()
    L.columns = ["ano", "cod", "pct_posto", "pct_imerg"]
    X = mi.merge(L, on=["cod", "ano"])
    yrs = X.ano.unique(); gg = {a: X[X.ano == a] for a in yrs}; bs = []
    for _ in range(500):
        bb = pd.concat([gg[a] for a in rng.choice(yrs, len(yrs))])
        if bb.quebra.nunique() == 2:
            bs.append(roc_auc_score(bb.quebra, -bb.pct_posto.clip(upper=3)) - roc_auc_score(bb.quebra, -bb.pct_imerg.clip(upper=3)))
    print(f"  {nome}: AUC posto - AUC IMERG = {np.mean(bs):+.3f}, IC90 por ano [{np.percentile(bs, 5):+.3f}, {np.percentile(bs, 95):+.3f}]")

# ---------------- A3. veranico na quadra (fev-abr), municipio
print("\n" + "=" * 20, "A3. Veranico fev-abr por municipio-ano: IMERG x postos", "=" * 20)


def seca_max(x, lim=2.0):
    s = best = 0
    for v in x:
        s = s + 1 if v <= lim else 0
        best = max(best, s)
    return best


lin = []
for a in anos:
    xg = gmun.loc[f"{a}-02-01":f"{a}-04-30", comuns]
    xi = chuva.loc[f"{a}-02-01":f"{a}-04-30", comuns]
    for c in comuns:
        g = xg[c]
        if g.notna().mean() < 0.95:
            continue
        g = g.fillna(0); i = xi[c]
        lin.append({"ano": a, "cod": c, "seca_max_posto": seca_max(g.values), "seca_max_imerg": seca_max(i.values),
                    "dias_le2_posto": int((g <= 2).sum()), "dias_le2_imerg": int((i <= 2).sum()),
                    "dias_ge1_posto": int((g >= 1).sum()), "dias_ge1_imerg": int((i >= 1).sum())})
V = pd.DataFrame(lin)
print(V.drop(columns=["ano", "cod"]).median().to_string())
print("rho(seca_max posto, seca_max IMERG) =", round(V.seca_max_posto.corr(V.seca_max_imerg, method="spearman"), 3),
      "| n =", len(V))
print("veranico >= 10 dias: posto", f"{(V.seca_max_posto >= 10).mean():.0%}", "| IMERG", f"{(V.seca_max_imerg >= 10).mean():.0%}",
      "| concordancia", f"{((V.seca_max_posto >= 10) == (V.seca_max_imerg >= 10)).mean():.0%}")
print("nota: a media municipal de varios postos ja suaviza; o IMERG e media de celulas de 0,1 grau (mais 'chuvisco').")

# limiar do IMERG que iguala a frequencia de dias "secos" do posto (<= 2 mm) na quadra
fg = (V.dias_le2_posto.median())
for lim in [2, 3, 4, 5, 6]:
    dl = []
    for a in anos:
        xi = chuva.loc[f"{a}-02-01":f"{a}-04-30", comuns]
        dl.append((xi <= lim).sum())
    print(f"  IMERG <= {lim} mm: dias secos fev-abr (mediana mun-ano) = {np.median(np.concatenate([d.values for d in dl])):.0f}"
          f"  (posto <= 2 mm: {fg:.0f})")
