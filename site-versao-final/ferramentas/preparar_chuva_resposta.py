"""Gera os dados do módulo "E se chover…" (web/js/extras/cenario_chuva.js), pontos 13 e 5 do desafio:

1) web/dados/chuva_resposta.json (pequeno): para cada mesorregião, estado e o Nordeste, e para milho, feijão e mandioca, a relação
   MEDIDA entre a chuva da estação (IMERG, em fração do normal do município) e a colheita (IBGE PAM, rendimento por ha plantado em
   fração da mediana 1998–2025 do município): chance de quebra (colheita < metade do normal, a definição canônica) e colheita típica
   (mediana), numa grade de 50% a 150% da chuva normal. Ajuste: média com peso gaussiano na chuva (h = 0,10), encolhida da
   mesorregião para o estado e do estado para o Nordeste (K = 30 pares equivalentes) e forçada a ser monótona (PAVA: mais chuva
   nunca aumenta a quebra nem diminui a colheita típica). Acerto: teste deixando cada ano de fora (Brier contra o clima).
2) web/dados/chuva_sobreposicao/<UF>.json: por município, as bases no mesmo eixo do tempo, em % do normal:
   chuva da estação (IMERG, 1998–2025), água útil do solo na estação (SMAP L4, 2015–2025), colheita (PAM, 2015–2025), as quebras de
   1998–2025 e, mês a mês de 2015 a 2025, o estado da roça: roça com água, aperto (terra seca com a roça no campo: SMAP) ou chão
   descoberto (sem verde: MODIS NDVI), entressafra.

Lê: E:/campeonato-nasa/dados/analogos_aprofundado/{onset_ne_mun,regime_chuva_ne_mun}.csv (chuva da estação do motor),
    E:/campeonato-nasa/dados/financeiro/painel_mun_cultura_ano.parquet (PAM), dados_resumo/derivados/ibge_ne_mun_smap_mensal.parquet,
    dados_resumo/derivados/ibge_ne_municipios_referencia.parquet, E:/campeonato-nasa/dados/modis/mod13a1_ndvi_nordeste_005deg.nc,
    E:/campeonato-nasa/dados/ibge_nordeste/malha_ne_municipio.geojson, E:/campeonato-nasa/dados/el_nino_2026/eventos.csv.
Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_chuva_resposta.py  (~2,5 min)"""
import datetime
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
T0 = time.time()
RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path("E:/campeonato-nasa/dados")
DERIV = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/dados_resumo/derivados")
SAI_CURVA = RAIZ / "web" / "dados" / "chuva_resposta.json"
SAI_SOBRE = RAIZ / "web" / "dados" / "chuva_sobreposicao"
CULT = ["Milho", "Feijão", "Mandioca"]
ANOS = np.arange(1998, 2026)
SOBRE = np.arange(2015, 2026)  # o SMAP começa em 31/03/2015
G = np.round(np.arange(0.5, 1.501, 0.1), 2)  # grade do controle: 50% a 150% do normal
H, K = 0.10, 30.0
UFS = {"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA"}
MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

EVT = pd.read_csv(DADOS / "el_nino_2026" / "eventos.csv", index_col=0)
FORTES = sorted(int(a) for a in EVT[(EVT.ONI_OND_NDJ >= 1.5) & EVT.quadra_afetada.between(1998, 2025)].quadra_afetada)
assert FORTES == [1998, 2010, 2016, 2024], FORTES
REF = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet").set_index("cod_mun")
REG = pd.read_csv(DADOS / "analogos_aprofundado" / "regime_chuva_ne_mun.csv", dtype={"cod": str}).set_index("cod")

# ---------------------------------------------------------------- chuva da estação (a mesma do motor: _perspectiva_municipal)
ONS = pd.read_csv(DADOS / "analogos_aprofundado" / "onset_ne_mun.csv", dtype={"cod": str})
ONS = ONS[ONS.ano <= 2025].dropna(subset=["chuva_estacao_mm"])  # 2026 é IMERG Late (preliminar)
# normal = mediana dos anos sem El Niño forte, como no passo 1 ("2016: 55% da chuva normal da estação")
NORM_MM = ONS[~ONS.ano.isin(FORTES)].groupby("cod").chuva_estacao_mm.median()
ONS["x"] = ONS.chuva_estacao_mm / ONS.cod.map(NORM_MM)
X = ONS.set_index(["cod", "ano"]).x


def meses_estacao(cod):
    """Meses da chuva da estação do motor: quadra do norte = fev–mai; senão os 4 meses a partir de mes_inicio_estacao.
    Devolve [(desloc_ano, mes)]: desloc −1 quando o mês cai no ano anterior ao da safra (estações que começam em out–dez)."""
    r = REG.loc[cod]
    if str(r.regra).startswith("quadra"):
        return [(0, m) for m in (2, 3, 4, 5)]
    m0 = int(r.mes_inicio_estacao)
    return [(-1 if m0 >= 10 and (m0 + k - 1) % 12 + 1 >= m0 else 0, (m0 + k - 1) % 12 + 1) for k in range(4)]


def rotulo_estacao(cod):
    ms = meses_estacao(cod)
    return f"{MES[ms[0][1] - 1]}–{MES[ms[-1][1] - 1]}"


# ---------------------------------------------------------------- colheita (PAM): razão à mediana 1998–2025 do município
P = pd.read_parquet(DADOS / "financeiro" / "painel_mun_cultura_ano.parquet")
P = P[P.produto.isin(CULT) & (P.area_plantada_ha > 0) & P.ano.between(1998, 2025)].copy()
P["n"] = P.groupby(["produto", "cod_mun"]).ano.transform("size")
P = P[P.n >= 20]  # mesma regra da projeção (municípios com 20 anos ou mais de série)
P["med"] = P.groupby(["produto", "cod_mun"]).rend_plantado_kg_ha.transform("median")
P = P[P.med > 0]
P["R"] = P.rend_plantado_kg_ha / P.med
P["q"] = (P.R < 0.5).astype(float)
P["x"] = [X.get((c, a), np.nan) for c, a in zip(P.cod_mun, P.ano)]
P["uf"] = P.cod_mun.str[:2].map(UFS)
P["meso"] = P.uf + "|" + REF.loc[P.cod_mun, "mesorregiao"].values
PARES = P.dropna(subset=["x", "R"])
print(f"pares chuva × colheita: {len(PARES):,} município-anos; " + ", ".join(f"{c} {int((PARES.produto == c).sum()):,}" for c in CULT))


# ---------------------------------------------------------------- ajuste monótono
def pava(y, w, crescente=True):
    """Regressão isotônica (pool adjacent violators) com pesos."""
    y = np.asarray(y, float) if crescente else -np.asarray(y, float)
    blocos = [[v, max(p, 1e-9), 1] for v, p in zip(y, w)]
    i = 0
    while i < len(blocos) - 1:
        if blocos[i][0] > blocos[i + 1][0]:
            a, b = blocos[i], blocos[i + 1]
            blocos[i] = [(a[0] * a[1] + b[0] * b[1]) / (a[1] + b[1]), a[1] + b[1], a[2] + b[2]]
            del blocos[i + 1]
            i = max(i - 1, 0)
        else:
            i += 1
    out = np.concatenate([[v] * n for v, _, n in blocos])
    return out if crescente else -out


def curva_bruta(x, R, q):
    """Média de quebra e mediana de R com peso gaussiano na chuva, na grade G; e o n efetivo de cada ponto."""
    W = np.exp(-0.5 * ((x[None, :] - G[:, None]) / H) ** 2)
    sw = W.sum(1)
    neff = sw ** 2 / np.maximum((W ** 2).sum(1), 1e-12)
    p = (W * q[None, :]).sum(1) / np.maximum(sw, 1e-12)
    o = np.argsort(R)
    cw = np.cumsum(W[:, o], 1) / np.maximum(sw[:, None], 1e-12)
    r = np.array([R[o][min(np.searchsorted(cw[i], 0.5), len(R) - 1)] for i in range(len(G))])
    return p, r, neff


def encolhe(filho, pai):
    p, r, n = filho
    pp, rp, _ = pai
    return (n * p + K * pp) / (n + K), (n * r + K * rp) / (n + K), n


def ajustar(d):
    """Curvas do Nordeste, de cada estado e de cada mesorregião (cada uma encolhida para a de cima e monótona)."""
    out = {}
    for c in CULT:
        dc = d[d.produto == c]
        ne = curva_bruta(dc.x.values, dc.R.values, dc.q.values)
        out[("NE", c)] = ne
        for uf, du in dc.groupby("uf"):
            fu = encolhe(curva_bruta(du.x.values, du.R.values, du.q.values), ne)
            out[(uf, c)] = fu
            for me, dm in du.groupby("meso"):
                out[(me, c)] = encolhe(curva_bruta(dm.x.values, dm.R.values, dm.q.values), fu)
    for k, (p, r, n) in out.items():
        out[k] = (np.clip(pava(p, n, crescente=False), 0, 1), np.maximum(pava(r, n, crescente=True), 0), n)
    return out


def prever(curvas, d):
    """Chance de quebra prevista para cada par (x fora de 50–150% fica na ponta da grade, como no controle)."""
    pr = np.full(len(d), np.nan)
    for i, (me, uf, c, x) in enumerate(zip(d.meso, d.uf, d.produto, d.x)):
        k = (me, c) if (me, c) in curvas else (uf, c) if (uf, c) in curvas else ("NE", c)
        pr[i] = np.interp(np.clip(x, G[0], G[-1]), G, curvas[k][0])
    return pr


def base_clima(d_treino, d_teste):
    """Referência: a taxa de quebra da mesorregião (encolhida para o estado), sem olhar a chuva."""
    t = d_treino.groupby(["meso", "produto"]).q.agg(["sum", "size"])
    u = d_treino.groupby(["uf", "produto"]).q.mean()
    pr = []
    for me, uf, c in zip(d_teste.meso, d_teste.uf, d_teste.produto):
        pu = u.get((uf, c), d_treino.q.mean())
        s, n = t.loc[(me, c)] if (me, c) in t.index else (0, 0)
        pr.append((s + K * pu) / (n + K))
    return np.array(pr)


CURVAS = ajustar(PARES)
print(f"curvas: {len(CURVAS)} ({time.time() - T0:.0f} s)")

# ---------------------------------------------------------------- acerto: deixando cada ano de fora
acerto = {}
linhas = []
for a in ANOS:
    tr, te = PARES[PARES.ano != a], PARES[PARES.ano == a]
    if not len(te):
        continue
    cv = ajustar(tr)
    linhas.append(pd.DataFrame({"produto": te.produto.values, "ano": a, "x": te.x.values, "q": te.q.values,
                                "p_chuva": prever(cv, te), "p_clima": base_clima(tr, te)}))
L = pd.concat(linhas)
print("\nTeste deixando cada ano de fora (1998–2025): Brier da quebra com a chuva da estação × só o clima da mesorregião")
for c in CULT:
    s = L[L.produto == c]
    bc, bm = float(((s.p_clima - s.q) ** 2).mean()), float(((s.p_chuva - s.q) ** 2).mean())
    cls = []
    for nome, lo, hi in [("abaixo de 75%", -1, 0.75), ("75% a 100%", 0.75, 1.0), ("100% ou mais", 1.0, 99)]:
        z = s[(s.x >= lo) & (s.x < hi)]
        cls.append({"classe": nome, "n": int(len(z)), "previsto": round(float(z.p_chuva.mean()), 3), "aconteceu": round(float(z.q.mean()), 3)})
    acerto[c] = {"n": int(len(s)), "brier_clima": round(bc, 4), "brier_chuva": round(bm, 4), "ganho": round(1 - bm / bc, 3),
                 "por_classe": cls}
    print(f"  {c:9s} n={len(s):6d}  Brier clima {bc:.4f}  com a chuva {bm:.4f}  ganho {100 * (1 - bm / bc):.1f}%  "
          + "; ".join(f"{k['classe']}: previu {k['previsto']:.2f}, aconteceu {k['aconteceu']:.2f} (n={k['n']})" for k in cls))

r2 = lambda v: [round(float(t), 2) for t in v]
curvas_json = {}
for (k, c), (p, r, n) in CURVAS.items():
    curvas_json.setdefault(k, {})[c] = {"q": r2(p), "r": r2(r), "n": int(round(float(n[5])))}  # n efetivo em 100%
n_pares = PARES.groupby(["meso", "produto"]).size()
for (me, c), v in n_pares.items():
    curvas_json[me][c]["pares"] = int(v)
SAI_CURVA.parent.mkdir(parents=True, exist_ok=True)
meta = {
    "gerado": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "script": "ferramentas/preparar_chuva_resposta.py",
    "grade_pct": [int(round(g * 100)) for g in G],
    "chuva": "GPM IMERG V07 (NASA), chuva da estação por município (a mesma do motor: quadra do norte fev–mai; nos outros lugares os "
             "4 meses mais chuvosos), em fração da mediana dos anos sem El Niño forte; 1998–2025",
    "colheita": "IBGE PAM, rendimento por ha plantado em fração da mediana 1998–2025 do município (municípios com 20 anos ou mais)",
    "quebra": "colheita abaixo da metade do normal do município (a mesma definição do passo Segurança)",
    "metodo": f"média com peso gaussiano na chuva (h = {H:.2f}), mesorregião encolhida para o estado e o estado para o Nordeste "
              f"(K = {K:.0f} pares), depois forçada a ser monótona (PAVA)",
    "pares": int(len(PARES)), "acerto_deixando_o_ano_de_fora": acerto,
}
SAI_CURVA.write_text(json.dumps({"meta": meta, "curvas": curvas_json}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"\n{SAI_CURVA.relative_to(RAIZ)}: {SAI_CURVA.stat().st_size / 1024:.0f} KB")

# ---------------------------------------------------------------- SMAP: água útil do solo (zona da raiz) por mês
S = pd.read_parquet(DERIV / "ibge_ne_mun_smap_mensal.parquet")
S = S[(S.dias >= 10) & (S.data.dt.year <= 2025)]
S["ano"], S["mes"] = S.data.dt.year, S.data.dt.month
seco = S.groupby("cod_mun").sm_rootzone.quantile(0.05)
umido = S.groupby("cod_mun").sm_rootzone.quantile(0.95)
S["au"] = ((S.sm_rootzone - S.cod_mun.map(seco)) / (S.cod_mun.map(umido) - S.cod_mun.map(seco))).clip(0, 1)
S["au_norm_mes"] = S.groupby(["cod_mun", "mes"]).au.transform("median")
AU = {(c, int(a), int(m)): (float(u), float(n)) for c, a, m, u, n in zip(S.cod_mun, S.ano, S.mes, S.au, S.au_norm_mes)}
print(f"SMAP pronto ({time.time() - T0:.0f} s)")

# ---------------------------------------------------------------- MODIS NDVI por município e mês (verde da paisagem)
import geopandas as gpd  # noqa: E402
import xarray as xr  # noqa: E402

ds = xr.open_dataset(DADOS / "modis" / "mod13a1_ndvi_nordeste_005deg.nc").sel(time=slice("2015-01-01", "2025-12-31"))
nd = ds.ndvi.values.astype("float32")
nd[ds.frac_boa.values < 0.3] = np.nan
lat, lon = ds.lat.values, ds.lon.values
LO, LA = np.meshgrid(lon, lat)
malha = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
malha["cod"] = malha.codarea.astype(str)
pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(LO.ravel(), LA.ravel()), crs=malha.crs)
j = gpd.sjoin(pts, malha[["cod", "geometry"]], predicate="within", how="inner")
j = j[~j.index.duplicated()]
cods = list(malha.cod)
ix = {c: i for i, c in enumerate(cods)}
idx = np.full(LO.size, -1)
idx[j.index.values] = [ix[c] for c in j.cod]
sem = [c for c in cods if c not in set(j.cod)]
rp = malha.set_index("cod").loc[sem].geometry.representative_point() if sem else []
perto = {c: (int(np.abs(lat - p.y).argmin()), int(np.abs(lon - p.x).argmin())) for c, p in zip(sem, rp)}
tempos = pd.to_datetime(ds.time.values)
med = np.full((len(tempos), len(cods)), np.nan, dtype="float32")
for t in range(len(tempos)):
    v = nd[t].ravel()
    ok = (idx >= 0) & ~np.isnan(v)
    s_, n_ = np.bincount(idx[ok], v[ok], len(cods)), np.bincount(idx[ok], minlength=len(cods))
    med[t] = np.where(n_ > 0, s_ / np.maximum(n_, 1), np.nan)
    for c, (a, b) in perto.items():
        med[t, ix[c]] = nd[t, a, b]
NDVI = pd.DataFrame(med, columns=cods)
NDVI["ano"], NDVI["mes"] = tempos.year, tempos.month
NDVI = NDVI.groupby(["ano", "mes"]).mean()  # composições de 16 dias → mês
print(f"NDVI pronto: {len(cods)} municípios, {len(sem)} pelo ponto mais perto ({time.time() - T0:.0f} s)")


# ---------------------------------------------------------------- por município
AU_NORM = S.groupby(["cod_mun", "mes"]).au.median()


def janela_campo(cod):
    """Meses de roça no campo, pelo próprio solo (SMAP): a maior sequência de meses (circular) com água útil normal ≥ 0,5,
    mais o mês antes (o plantio vem com as primeiras chuvas, antes de a terra encher). Sem SMAP: estação do motor + 1 mês.
    Assim o agreste e o leste, onde o IMERG põe a estação cedo demais (fev–mai), seguem o inverno que a terra mostra."""
    try:
        v = AU_NORM.loc[cod].reindex(range(1, 13)).values
    except KeyError:
        v = np.full(12, np.nan)
    if np.isnan(v).any() or not (v >= 0.5).any():
        ms = [m for _, m in meses_estacao(cod)]
        return ms + [ms[-1] % 12 + 1]
    if (v >= 0.5).all():
        return list(range(1, 13))
    melhor, ini = 0, 0
    for i in range(12):
        n = 0
        while n < 12 and v[(i + n) % 12] >= 0.5:
            n += 1
        if n > melhor:
            melhor, ini = n, i
    melhor = max(melhor, 3)  # um ciclo de milho/feijão tem 3–4 meses: a roça fica no campo pelo menos 4 meses
    return [(ini - 1) % 12 + 1] + [(ini + k) % 12 + 1 for k in range(melhor)]


def estados(cod, jan):
    """2015-01..2025-12, um caractere por mês: r roça com água, e aperto (terra seca com a roça no campo), d chão descoberto
    (sem verde), n entressafra com verde, - sem dado. Roça no campo = janela_campo()."""
    campo = {(a, m) for a in range(2015, 2026) for m in jan}
    nv = NDVI[cod] if cod in NDVI.columns else None
    limiar = None
    if nv is not None and nv.notna().sum() > 60:
        lo_, hi_ = nv.quantile(0.05), nv.quantile(0.95)
        if hi_ - lo_ >= 0.12:  # sem estação seca visível no verde, não há "chão descoberto" pelo satélite
            limiar = lo_ + (hi_ - lo_) / 3
    out = []
    for a in map(int, SOBRE):
        for m in range(1, 13):
            g = nv.get((a, m), np.nan) if nv is not None else np.nan
            desc = limiar is not None and not np.isnan(g) and g < limiar
            if (a, m) in campo:
                if (cod, a, m) in AU:
                    au, an = AU[(cod, a, m)]
                    out.append("e" if au < max(0.25, 0.6 * an) else "d" if desc else "r")
                else:
                    out.append("d" if desc else "-")
            else:
                out.append("d" if desc else "n" if not np.isnan(g) else "-")
    return "".join(out)


def solo_estacao(cod, jan):
    """Água útil média nos meses de roça no campo, por safra 2015–2025, em % da mediana dessas safras (≥ 2 meses com dado).
    Janela que vira o ano (ex.: out–abr): os meses de out–dez são do ano anterior ao da safra (a colheita do PAM)."""
    vira = jan[-1] < jan[0]
    ms = [(-1 if vira and m >= jan[0] else 0, m) for m in jan]
    v = {}
    for a in SOBRE:
        z = [AU[(cod, int(a) + d, m)][0] for d, m in ms if (cod, int(a) + d, m) in AU]
        v[int(a)] = float(np.mean(z)) if len(z) >= 2 else np.nan
    s = pd.Series(v)
    md = s.median()
    return [None if np.isnan(t) or not md else int(round(100 * t / md)) for t in s.values]


por_uf = {}
Pi = P.set_index(["cod_mun", "produto", "ano"]).sort_index()
TEM = set(zip(P.cod_mun, P.produto))
for cod in REF.index:
    if cod not in REG.index:
        continue
    uf = UFS[cod[:2]]
    xs = [X.get((cod, int(a)), np.nan) for a in ANOS]
    d = {"est": rotulo_estacao(cod), "mm": int(round(NORM_MM.get(cod, np.nan))) if cod in NORM_MM.index else None,
         "ch": [None if np.isnan(v) else int(round(100 * v)) for v in xs], "q": {}, "n": {}, "co": {}}
    for c in CULT:
        if (cod, c) not in TEM:
            continue
        sr = Pi.loc[(cod, c)]
        d["n"][c] = int(round(float(sr.med.iloc[0])))
        d["q"][c] = "".join("-" if a not in sr.index else str(int(sr.q.loc[a])) for a in ANOS)
        d["co"][c] = [None if a not in sr.index else int(round(100 * float(sr.R.loc[a]))) for a in SOBRE]
    jan = janela_campo(cod)
    d["jc"] = jan
    d["so"] = solo_estacao(cod, jan)
    d["me"] = estados(cod, jan)
    por_uf.setdefault(uf, {})[cod] = d
print(f"municípios prontos ({time.time() - T0:.0f} s)")

SAI_SOBRE.mkdir(parents=True, exist_ok=True)
meta_s = {
    "gerado": meta["gerado"], "script": meta["script"], "anos_chuva": [int(ANOS[0]), int(ANOS[-1])], "anos_sobre": [int(SOBRE[0]), int(SOBRE[-1])],
    "campos": {"est": "meses da chuva da estação", "mm": "chuva normal da estação (mm, mediana dos anos sem El Niño forte, IMERG)",
               "ch": "chuva da estação em % do normal, 1998–2025", "q": "quebra (1) ou não (0) da colheita, 1998–2025; - sem dado",
               "n": "colheita normal (kg/ha, mediana PAM 1998–2025)", "co": "colheita em % do normal, 2015–2025",
               "jc": "meses de roça no campo (1 = jan)",
               "so": "água útil do solo nos meses de roça no campo (SMAP L4, zona da raiz) em % da mediana 2015–2025",
               "me": "mês a mês de jan/2015 a dez/2025: r roça com água, e aperto, d chão descoberto, n entressafra com verde, - sem dado"},
    "regras": {"roca_no_campo": "a maior sequência de meses com água útil normal (mediana 2015–2025) ≥ 0,5, mais o mês antes (plantio), com no mínimo 4 meses; "
                                "sem SMAP, a estação do motor + 1 mês",
               "agua_util": "SMAP L4 zona da raiz: (umidade − p5) ÷ (p95 − p5) do próprio município, 2015–2025",
               "aperto": "roça no campo e água útil abaixo de 0,25 ou abaixo de 60% do normal daquele mês",
               "chao_descoberto": "MODIS MOD13A1 NDVI do município abaixo de p5 + 1/3 × (p95 − p5); só onde a diferença p95 − p5 é ≥ 0,12",
               "el_nino_forte": FORTES},
}
for uf, dd in sorted(por_uf.items()):
    f = SAI_SOBRE / f"{uf}.json"
    f.write_text(json.dumps({"meta": meta_s, "mun": dd}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  {f.relative_to(RAIZ)}: {len(dd)} municípios, {f.stat().st_size / 1024:.0f} KB")

for cod in ["2311306", "2700300", "2903201"]:
    d = por_uf[UFS[cod[:2]]][cod]
    print(cod, REF.loc[cod, "municipio"], json.dumps({k: d[k] for k in ["est", "mm", "n", "so"]}, ensure_ascii=False))
    print("   chuva", d["ch"])
    print("   milho", d["co"].get("Milho"), d["q"].get("Milho"))
    print("   janela", d["jc"], "solo", d["so"])
    print("   meses", " ".join(d["me"][i:i + 12] for i in range(0, 132, 12)))
    me = REF.loc[cod, "mesorregiao"]
    print("   curva milho", curvas_json[f"{UFS[cod[:2]]}|{me}"]["Milho"])
print(f"fim ({time.time() - T0:.0f} s)")
