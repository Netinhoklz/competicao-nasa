"""Designer (agricultor familiar) - Analise 1: QUANDO falar com o agricultor e COMO explicar sem perder habilidade.

Perguntas:
  (a) Curva de habilidade ao longo da estacao: com o que se sabe em 30/nov (so oceano), 31/jan, 28/fev, 31/mar e
      30/abr, quanto da para prever a QUEBRA do milho e do feijao NO MUNICIPIO? (define os "pontos de conversa" do
      produto e o custo de esperar).
  (b) Explicacao x habilidade: uma regra falavel (arvore de profundidade 2) e "anos-irmaos" (k vizinhos mais
      proximos entre os anos do proprio municipio, o que o agricultor lembra) perdem quanto para regressao
      logistica e gradient boosting?
  (c) Frequencias naturais: "em 5 anos parecidos com este, em X o milho quebrou" e bem calibrado?

Dados:
  E:/campeonato-nasa/dados/imerg/imerg_ce_diario_*.nc (IMERG V07 via POWER, 0,1 grau, diario 1998-2026-09)
  E:/campeonato-nasa/dados/derivados/ibge_pam_mun_anual.parquet (PAM municipal 1974-2025)
  E:/campeonato-nasa/dados/derivados/indices_clima_mensal.parquet (ONI, TNA-TSA)
  E:/campeonato-nasa/dados/referencia/ceara_municipios.geojson
Alvo: quebra = (producao / area PLANTADA) / mediana movel centrada de 7 anos do municipio < 0,5
      (o limiar de 50% e o mesmo gatilho de perda do Garantia-Safra; a area plantada inclui o rocado perdido).
Validacao: deixar o ANO inteiro de fora (LOYO), 1998-2025; climatologia = taxa de quebra do municipio nos anos de treino.
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import warnings

warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, DERIV, REF

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import Point
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

pd.set_option("display.width", 220)
OUT = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1) chuva diaria municipal (IMERG)
ds = xr.open_mfdataset(sorted(str(p) for p in (DADOS / "imerg").glob("imerg_ce_diario_*.nc")), combine="by_coords")
pr = ds["precip"].load()
lat, lon = pr.lat.values, pr.lon.values
LL = np.array([(a, b) for a in lat for b in lon])
pts = gpd.GeoDataFrame({"i": range(len(LL))}, geometry=[Point(b, a) for a, b in LL], crs="EPSG:4326")
mun = gpd.read_file(REF / "ceara_municipios.geojson").to_crs("EPSG:4326")
jn = gpd.sjoin(pts, mun[["codarea", "geometry"]], predicate="within")
arr = pr.values.reshape(pr.shape[0], -1)
series = {}
for _, row in mun.iterrows():
    idx = jn.loc[jn.codarea == row.codarea, "i"].values
    if len(idx) == 0:
        c = row.geometry.representative_point()
        idx = [int(np.argmin((LL[:, 0] - c.y) ** 2 + (LL[:, 1] - c.x) ** 2))]
    series[row.codarea] = np.nanmean(arr[:, idx], axis=1)
chuva = pd.DataFrame(series, index=pd.to_datetime(pr.time.values))
chuva.to_parquet(OUT / "designer_chuva_mun_diaria.parquet")
print(f"chuva municipal: {chuva.shape}, {chuva.index.min():%Y-%m-%d} a {chuva.index.max():%Y-%m-%d}")

# ---------------------------------------------------------------- 2) indices oceanicos
ind = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
ind["data"] = pd.to_datetime(ind.data)
I = ind.pivot_table(index="data", columns="variavel", values="valor")


def media_meses(var, pares):
    return float(np.mean([I.loc[pd.Timestamp(a, m, 1), var] for a, m in pares]))


# ---------------------------------------------------------------- 3) atributos por data de decisao
DATAS = {  # nome: (mes, dia) no ano da safra; None = 30/nov do ano anterior
    "D0 30/nov (so oceano)": None,
    "D1 31/jan": (1, 31),
    "D2 28/fev": (2, 28),
    "D3 31/mar": (3, 31),
    "D4 30/abr": (4, 30),
}


def maior_seca(x, lim=2.0):
    m = c = 0
    for v in x:
        c = c + 1 if v < lim else 0
        m = max(m, c)
    return m


def atributos(ano, data_dec):
    linhas = []
    if data_dec is None:
        oni = media_meses("ONI", [(ano - 1, 8), (ano - 1, 9), (ano - 1, 10)])
        dip = media_meses("DIPOLO_TNA_menos_TSA", [(ano - 1, 8), (ano - 1, 9), (ano - 1, 10)])
        for cod in chuva.columns:
            linhas.append({"cod": cod, "ano": ano, "ONI": oni, "DIP": dip})
        return linhas
    mes, dia = data_dec
    oni = media_meses("ONI", [(ano - 1, 10), (ano - 1, 11), (ano - 1, 12)])
    meses_dip = [(ano - 1, 12)] + [(ano, m) for m in range(1, mes)] if mes > 1 else [(ano - 1, 10), (ano - 1, 11), (ano - 1, 12)]
    dip = media_meses("DIPOLO_TNA_menos_TSA", meses_dip)
    ini, fim = pd.Timestamp(ano, 1, 1), pd.Timestamp(ano, mes, dia)
    jan = chuva.loc[ini:fim]
    dez = chuva.loc[pd.Timestamp(ano - 1, 12, 1):pd.Timestamp(ano - 1, 12, 31)]
    if len(jan) < (fim - ini).days + 1:
        return []
    for cod in chuva.columns:
        x = jan[cod].values
        s3 = np.convolve(x, np.ones(3), "valid")
        on = np.where(s3 >= 20)[0]
        linhas.append({
            "cod": cod, "ano": ano, "ONI": oni, "DIP": dip,
            "P_dez": float(dez[cod].sum()) if len(dez) == 31 else np.nan,
            "P_acum": float(x.sum()), "dias10": int((x >= 10).sum()),
            "seca_max": maior_seca(x),
            "inicio_doy": int(on[0]) + 1 if len(on) else len(x) + 15,
        })
    return linhas


ANOS = list(range(1998, 2027))
A = {}
for nome, dd in DATAS.items():
    rows = []
    for a in ANOS:
        if dd is None and a < 1998:
            continue
        rows += atributos(a, dd)
    A[nome] = pd.DataFrame(rows)

# ---------------------------------------------------------------- 4) alvo: quebra municipal (PAM)
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(str)
alvos = {}
for cult, nome_pam in [("milho", "Milho (em gr"), ("feijao", "Feij")]:
    s = pam[pam.produto.str.startswith(nome_pam) & (pam.ano >= 1990)].copy()
    s["rp"] = np.where(s.area_plantada_ha >= 100, s.producao_t * 1000 / s.area_plantada_ha.replace(0, np.nan), np.nan)
    s = s.sort_values(["cod", "ano"])
    s["tend"] = s.groupby("cod")["rp"].transform(lambda v: v.rolling(7, center=True, min_periods=4).median())
    s["razao"] = s.rp / s.tend
    s["quebra"] = (s.razao < 0.5).astype(float).where(s.razao.notna())
    alvos[cult] = s[["cod", "ano", "razao", "quebra"]]

srtm = pd.read_parquet(DERIV / "srtm_municipios_ce.parquet").rename(columns={"codarea": "cod"})[["cod", "elev_media", "decl_media_graus"]]
cent = mun.to_crs("EPSG:5880").geometry.centroid.to_crs("EPSG:4326")
geo = pd.DataFrame({"cod": mun.codarea.astype(str), "lat": cent.y.values, "lon": cent.x.values}).merge(srtm, on="cod")

nomes = {str(d["id"]): d["nome"] for d in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}

# sincronia: fracao de municipios com quebra por ano
for cult in alvos:
    t = alvos[cult][alvos[cult].ano.between(1998, 2025)].dropna()
    f = t.groupby("ano").quebra.mean()
    print(f"\n[{cult}] taxa geral de quebra 1998-2025: {t.quebra.mean():.1%} de {len(t)} municipio-anos; "
          f"anos com >50% dos municipios em quebra: {list(f[f > 0.5].index)}")
    print("   fracao de municipios em quebra por ano:", " ".join(f"{a % 100:02d}:{v:.0%}" for a, v in f.items()))


# ---------------------------------------------------------------- 5) validacao LOYO por data e modelo
def avaliar(cult, nome_data, k=5, guardar=False):
    X = A[nome_data].merge(alvos[cult], on=["cod", "ano"], how="left").merge(geo, on="cod", how="left")
    feats = [c for c in ["ONI", "DIP", "P_dez", "P_acum", "dias10", "seca_max", "inicio_doy"] if c in X]
    X = X.dropna(subset=feats)
    lab = X[X.quebra.notna() & X.ano.between(1998, 2025)].copy()
    lab["cod"] = lab.cod.astype(str)
    pred = {m: np.full(len(lab), np.nan) for m in ["clim", "regra_d2", "anos_irmaos_k5", "logistica", "gboost"]}
    anos_ir = [None] * len(lab)
    for a in sorted(lab.ano.unique()):
        tr, te = lab.ano != a, lab.ano == a
        T, E = lab[tr], lab[te]
        # climatologia do municipio (suavizada)
        g = T.groupby("cod").quebra.agg(["sum", "count"])
        pc = ((g["sum"] + 0.5) / (g["count"] + 1)).rename("pc")
        base = T.quebra.mean()
        T_pc = T.cod.map(pc).fillna(base).values
        E_pc = E.cod.map(pc).fillna(base).values
        pred["clim"][te.values] = E_pc
        # regra falavel: arvore de profundidade 2 sobre os atributos de dado
        dt = DecisionTreeClassifier(max_depth=2, min_samples_leaf=150, random_state=0).fit(T[feats], T.quebra)
        pred["regra_d2"][te.values] = dt.predict_proba(E[feats])[:, 1]
        # logistica e gradient boosting (com a climatologia do municipio como atributo)
        sc = StandardScaler().fit(T[feats])
        lg = LogisticRegression(max_iter=2000, C=1.0).fit(np.c_[sc.transform(T[feats]), np.log(T_pc / (1 - T_pc))], T.quebra)
        pred["logistica"][te.values] = lg.predict_proba(np.c_[sc.transform(E[feats]), np.log(E_pc / (1 - E_pc))])[:, 1]
        fx = feats + ["elev_media", "decl_media_graus", "lat", "lon"]
        gb = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=250, min_samples_leaf=40,
                                            l2_regularization=1.0, random_state=0)
        gb.fit(np.c_[T[fx].values, T_pc], T.quebra)
        pred["gboost"][te.values] = gb.predict_proba(np.c_[E[fx].values, E_pc])[:, 1]
        # anos-irmaos: k anos de treino mais parecidos NO PROPRIO municipio
        Zt = pd.DataFrame(sc.transform(T[feats]), index=T.index)
        Ze = pd.DataFrame(sc.transform(E[feats]), index=E.index)
        Tg = {c: idx for c, idx in T.groupby("cod").groups.items()}
        pos = np.where(te.values)[0]
        for p_i, (ix, row) in zip(pos, E.iterrows()):
            idx = Tg.get(row.cod)
            if idx is None or len(idx) < k:
                pred["anos_irmaos_k5"][p_i] = base
                continue
            d = np.sqrt(((Zt.loc[idx].values - Ze.loc[ix].values) ** 2).sum(1))
            o = np.argsort(d)[:k]
            q = T.loc[idx].quebra.values[o]
            pred["anos_irmaos_k5"][p_i] = (q.sum() + pc.get(row.cod, base)) / (k + 1)
            if guardar:
                anos_ir[p_i] = list(zip(T.loc[idx].ano.values[o], q))
    y = lab.quebra.values
    res = {}
    bc = brier_score_loss(y, pred["clim"])
    for m, p in pred.items():
        res[m] = {"AUC": roc_auc_score(y, p), "BSS": 1 - brier_score_loss(y, p) / bc}
    out = pd.DataFrame(res).T
    if guardar:
        lab = lab.assign(**{f"p_{m}": v for m, v in pred.items()}, irmaos=anos_ir)
        return out, lab, feats
    return out


tabelas = []
for cult in ["milho", "feijao"]:
    for nd in DATAS:
        r = avaliar(cult, nd).assign(cultura=cult, data=nd)
        tabelas.append(r)
R = pd.concat(tabelas).reset_index().rename(columns={"index": "modelo"})
print("\n=== Curva de habilidade (LOYO 1998-2025): AUC e BSS vs climatologia do municipio ===")
print(R.pivot_table(index=["cultura", "data"], columns="modelo", values="AUC").round(3).to_string())
print(R.pivot_table(index=["cultura", "data"], columns="modelo", values="BSS").round(3).to_string())
R.to_csv(OUT / "designer_curva_habilidade.csv", index=False)

# ---------------------------------------------------------------- 6) regra falavel e calibracao em 28/fev (milho)
out, lab, feats = avaliar("milho", "D2 28/fev", guardar=True)
X = A["D2 28/fev"].merge(alvos["milho"], on=["cod", "ano"]).dropna(subset=feats + ["quebra"])
X = X[X.ano.between(1998, 2025)]
dt = DecisionTreeClassifier(max_depth=2, min_samples_leaf=150, random_state=0).fit(X[feats], X.quebra)
print("\n=== Regra falavel (arvore de profundidade 2, milho, 28/fev, ajustada em todos os anos) ===")
print(export_text(dt, feature_names=feats, show_weights=True))

print("=== Calibracao das frequencias naturais 'anos-irmaos' (milho, 28/fev, LOYO) ===")
lab["k_quebras"] = lab.irmaos.apply(lambda v: sum(int(q) for _, q in v) if v else np.nan)
cal = lab.dropna(subset=["k_quebras"]).groupby("k_quebras").agg(n=("quebra", "size"), quebra_obs=("quebra", "mean"))
print(cal.round(3).to_string())

# ---------------------------------------------------------------- 7) replay para a demo
print("\n=== Replay para a demo (milho, 28/fev, cada ano fora do treino) ===")
for nome_m in ["Quixad", "Tau", "Crate", "Iguatu"]:
    cods = [c for c, n in nomes.items() if n.startswith(nome_m)]
    if not cods:
        continue
    c = cods[0]
    for a in [2012, 2016, 2019, 2024, 2025]:
        r = lab[(lab.cod == c) & (lab.ano == a)]
        if r.empty:
            continue
        r = r.iloc[0]
        print(f"{nomes[c]:12s} {a}: P_acum={r.P_acum:5.0f} mm seca_max={r.seca_max:2.0f} d ONI={r.ONI:+.1f} | "
              f"p(quebra) clim={r.p_clim:.2f} irmaos={r.p_anos_irmaos_k5:.2f} gb={r.p_gboost:.2f} | "
              f"anos-irmaos={[f'{int(y)}{chr(10007) if q else chr(10003)}' for y, q in r.irmaos]} | "
              f"real: razao={r.razao:.2f} quebra={int(r.quebra)}")
# 2026 (sem PAM ainda): o que o produto teria dito em 28/fev/2026
X26 = A["D2 28/fev"]
X26 = X26[X26.ano == 2026]
print("\n2026 em 28/fev (sem rotulo; estado):", X26[["P_acum", "seca_max", "dias10"]].median().round(1).to_dict(),
      "ONI_OND=%.2f DIP=%.2f" % (X26.ONI.iloc[0], X26.DIP.iloc[0]))
