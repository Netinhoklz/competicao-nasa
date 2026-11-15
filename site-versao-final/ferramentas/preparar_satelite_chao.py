"""Gera site-versao-final/web/dados/satelite_chao.json: o satélite (IMERG) contra o pluviômetro, por município (ponto 3 do
desafio: como o satélite difere da medição em terra e como juntar os dois melhora a precisão).

Fontes (todas locais, já baixadas e validadas pelo curador v3):
 - Pluviômetros da FUNCEME no Ceará (842 postos, leitura às 7h), 1998–2025:
   E:/campeonato-nasa/dados/complementares/funceme/funceme_postos_diario.parquet (+ _meta). Entram os postos com ≥ 10 anos
   de leitura (mesma regra de conselho/analises/v3_curador_valida_imerg_funceme.py).
 - Estações automáticas do INMET no Nordeste (150), dia UTC, 2016–2025:
   E:/campeonato-nasa/dados/complementares/inmet/inmet_diario_ne_v2.parquet (feito por v3_curador_valida_inmet.py).
 - GPM IMERG V07 diário via NASA POWER, grade de 0,1°: E:/campeonato-nasa/dados/imerg/imerg_{ne,ce}_diario_<ano>.nc.

O que mede, por pluviômetro (célula IMERG mais próxima, só dias com os dois):
 - razão de volume (satélite / pluviômetro), r diário e r mensal (meses com ≥ 25 dias válidos);
 - "perto": fração dos meses de chuva (pluviômetro ≥ 30 mm) em que o satélite ficou a até 25% do pluviômetro, cru e
   corrigido por trimestre (fator = soma do pluviômetro / soma do satélite no mesmo trimestre dos OUTROS anos; 0,25–4).
Controle de qualidade: fica fora o pluviômetro com r mensal < 0,6 ou com o satélite acima de 1,6 vez o pluviômetro
(sinal de leitura faltando: nas normais 1991–2020 do INMET o satélite nunca passa de 1,12 vez a estação no NE; em Sobral,
a estação do INMET dá 1,18 e os postos vizinhos cortados, 1,6–1,7). A razão baixa NÃO sai: na serra e na costa leste ela é
real (chuva de encosta e de brisa que o satélite não vê).

Regional, Ceará (FUNCEME, rede densa): chuva de 1/fev até o portão de 19/mar no seu pluviômetro, estimada por
 (a) satélite sozinho, (b) pluviômetro do vizinho mais perto (2–30 km) sozinho, (c) satélite corrigido pelo vizinho
 (fator = soma do vizinho / soma do satélite na célula do vizinho, nos outros anos) e (d) juntos = média de (b) e (c).
 Medida: erro mediano em cada 100 mm e fração dos anos a até 25%. A regra foi fixada antes de olhar o resultado final.

Por município (1.794, ponto de busca_municipios.json): o pluviômetro aprovado mais perto, a distância, se está na
costa leste (mesma regra de nucleo/motor.py: até 0,2° do mar do RN à BA), a faixa de distância do mar (para quem fica a
mais de LONGE km de um pluviômetro aprovado) e, no CE, quantos postos da FUNCEME leram em 2026.

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 site-versao-final/ferramentas/preparar_satelite_chao.py"""
import datetime
import json
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import box

warnings.filterwarnings("ignore", message="Geometry is in a geographic CRS")  # distância em graus, como no motor

RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path("E:/campeonato-nasa/dados")
SAIDA = RAIZ / "web" / "dados" / "satelite_chao.json"
MES_CHUVA, PERTO = 30.0, 0.25
LONGE = 80  # km: acima disso, a tela usa o resultado da faixa de distância do mar, não o pluviômetro distante
TRI = {12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3}


def imerg_nos_pontos(prefixo, anos, lat, lon, nomes):
    """Série diária do IMERG na célula mais próxima de cada ponto (dia × ponto)."""
    partes = []
    for a in anos:
        ds = xr.open_dataset(DADOS / "imerg" / f"imerg_{prefixo}_diario_{a}.nc")["precip"]
        iy = np.abs(ds.lat.values[None, :] - lat[:, None]).argmin(1)
        ix = np.abs(ds.lon.values[None, :] - lon[:, None]).argmin(1)
        v = ds.isel(lat=xr.DataArray(iy, dims="e"), lon=xr.DataArray(ix, dims="e")).load().values
        partes.append(pd.DataFrame(v, index=pd.to_datetime(ds.time.values), columns=nomes))
    return pd.concat(partes).where(lambda x: x >= 0)


def medir(g, s):
    """Métricas de um pluviômetro (g) contra o satélite (s), séries diárias alinhadas."""
    m = g.notna() & s.notna()
    if m.sum() < 730:
        return None
    g, s = g.where(m), s.where(m)
    n = m.resample("MS").sum()
    M = pd.DataFrame({"g": g.resample("MS").sum()[n >= 25], "s": s.resample("MS").sum()[n >= 25]})
    M["ano"], M["tri"] = M.index.year, M.index.month.map(TRI)
    c = []
    for _, r in M.iterrows():  # correção por trimestre, deixa o ano de fora
        o = M[(M.ano != r.ano) & (M.tri == r.tri)]
        if o.s.sum() < 30:
            o = M[M.ano != r.ano]
        c.append(r.s * float(np.clip(o.g.sum() / max(o.s.sum(), 1e-9), 0.25, 4)))
    M["c"] = c
    R = M[M.g >= MES_CHUVA]
    anos = M.ano.unique()
    return {"a0": int(anos.min()), "a1": int(anos.max()), "nm": int(len(R)),
            "rz": float(s.sum() / g.sum()), "rd": float(np.corrcoef(g[m], s[m])[0, 1]), "rm": float(M.g.corr(M.s)),
            "p": float((abs(R.s - R.g) <= PERTO * R.g).mean()), "pc": float((abs(R.c - R.g) <= PERTO * R.g).mean()),
            "ea": float((R.s - R.g).abs().mean()), "ec": float((R.c - R.g).abs().mean())}


def km(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


# ---------------------------------------------------------------- costa (mesma regra do motor)
terra = gpd.read_file("zip://" + str(DADOS / "referencia" / "ne_50m_land.zip"))
costa_ne = terra.boundary.union_all().intersection(box(-48.8, -18.6, -34.6, -1.0))
costa_leste = terra.boundary.union_all().intersection(box(-41.0, -18.6, -34.6, -5.1))
MALHA = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
MALHA["cod"] = MALHA.codarea.astype(str)
LESTE = set(MALHA.cod[MALHA.geometry.distance(costa_leste) <= 0.2])

# ---------------------------------------------------------------- INMET
dd = pd.read_parquet(DADOS / "complementares" / "inmet" / "inmet_diario_ne_v2.parquet")
dd["data"] = pd.to_datetime(dd.data)
st = dd.groupby("codigo")[["nome", "uf", "lat", "lon"]].first()
st = st[(st.lon >= -48.8) & (st.lat >= -18.4)]
G = dd.pivot(index="data", columns="codigo", values="chuva_mm")
I = imerg_nos_pontos("ne", range(2016, 2026), st.lat.values, st.lon.values, st.index)
G = G.reindex(I.index)
pluv = []
for c in st.index:
    x = medir(G[c], I[c])
    if x:
        pluv.append(dict(x, id="I" + c, t="INMET", n=str(st.nome[c]).title(), uf=st.uf[c], la=st.lat[c], lo=st.lon[c]))
print(f"INMET: {len(pluv)} estações com ≥ 2 anos de dias em comum")

# ---------------------------------------------------------------- FUNCEME
dia = pd.read_parquet(DADOS / "complementares" / "funceme" / "funceme_postos_diario.parquet")
meta = pd.read_parquet(DADOS / "complementares" / "funceme" / "funceme_postos_meta.parquet").set_index("posto")
meta["municipio"] = meta.municipio.map(lambda s: s.encode("latin1").decode("utf-8") if isinstance(s, str) else s)
ativos26 = set(dia[(dia.data >= "2026-01-01") & dia.mm.notna()].posto.unique())
W = dia[(dia.data >= "1998-01-01") & (dia.data <= "2025-12-31") & dia.mm.notna()]
cont = W.groupby("posto").size()
sel = cont[cont >= 3650].index
F = W[W.posto.isin(sel)].pivot(index="data", columns="posto", values="mm")
mt = meta.loc[sel]
IF = imerg_nos_pontos("ce", range(1998, 2026), mt.lat.values, mt.lon.values, sel)
F = F.reindex(IF.index)
nf = 0
for p in sel:
    x = medir(F[p], IF[p])
    if x:
        nf += 1
        pluv.append(dict(x, id=f"F{p}", t="FUNCEME", n=str(mt.nome[p]).title(), m=mt.municipio[p], uf="CE",
                         la=mt.lat[p], lo=mt.lon[p]))
print(f"FUNCEME: {nf} postos com ≥ 10 anos")

P = pd.DataFrame(pluv)
P["km_mar"] = [costa_ne.distance(gpd.points_from_xy([lo], [la])[0]) * 111 for la, lo in zip(P.la, P.lo)]
P["leste"] = [costa_leste.distance(gpd.points_from_xy([lo], [la])[0]) <= 0.2 for la, lo in zip(P.la, P.lo)]
P["ok"] = (P.rm >= 0.6) & (P.rz <= 1.6)
print("fora pelo controle de qualidade:", (~P.ok).sum(), "de", len(P))
print(P[~P.ok][["id", "n", "uf", "rz", "rm"]].round(2).to_string(index=False))

# ---------------------------------------------------------------- regional: por distância do mar (INMET, NE inteiro)
Q = P[P.ok & (P.t == "INMET")].copy()
Q["faixa"] = np.select([Q.leste & (Q.km_mar < 20), Q.km_mar < 20, Q.km_mar < 150], ["leste", "norte", "meio"], "sertao")
rot = {"leste": "Costa leste (RN à BA), até 20 km do mar", "norte": "Costa norte (MA, PI, CE), até 20 km do mar",
       "meio": "De 20 a 150 km do mar", "sertao": "Mais de 150 km do mar"}
costa_tab = []
for f in ["leste", "norte", "meio", "sertao"]:
    x = Q[Q.faixa == f]
    costa_tab.append({"faixa": rot[f], "n": int(len(x)), "rz": round(float(x.rz.median()), 2), "rm": round(float(x.rm.median()), 2),
                      "p": round(float(x.p.median()), 2), "pc": round(float(x.pc.median()), 2)})
print(pd.DataFrame(costa_tab).to_string(index=False))
# serra: postos da FUNCEME nos maciços de Baturité, Ibiapaba e Meruoca (chuva de encosta)
SERRA = {"Guaramiranga": "Guaramiranga", "Pacoti": "Pacoti", "Palmacia": "Palmácia", "Aratuba": "Aratuba", "Ubajara": "Ubajara",
         "Ibiapina": "Ibiapina", "Sao Benedito": "São Benedito", "Tiangua": "Tianguá", "Meruoca": "Meruoca"}
S_ = P[P.ok & (P.t == "FUNCEME") & P.n.isin(list(SERRA))]
serra = {"postos": sorted(SERRA[n] for n in S_.n.unique()), "n": int(len(S_)), "rz": round(float(S_.rz.median()), 2),
         "rz_min": round(float(S_.rz.min()), 2), "rz_max": round(float(S_.rz.max()), 2)}
print("serra:", serra)

# ---------------------------------------------------------------- regional: portão de 19/mar, Ceará (FUNCEME)
ok_f = [int(i[1:]) for i in P[P.ok & (P.t == "FUNCEME")].id]
mf = meta.loc[ok_f]


def janela(df, minfrac):
    out = {}
    for a in range(1998, 2026):
        w = df.loc[f"{a}-02-01":f"{a}-03-19"]
        out[a] = w.sum(min_count=1).where(w.notna().sum() >= minfrac * len(w))
    return pd.DataFrame(out).T


Gw, Sw = janela(F[ok_f], 0.9), janela(IF[ok_f], 0.99)
D = km(mf.lat.values[:, None], mf.lon.values[:, None], mf.lat.values[None], mf.lon.values[None])
lin = []
for i, p in enumerate(ok_f):
    viz = [ok_f[j] for j in np.argsort(D[i]) if 2 <= D[i, j] <= 30]
    for a in Gw.index:
        g, s = Gw.loc[a, p], Sw.loc[a, p]
        if not (np.isfinite(g) and np.isfinite(s)) or g < 20:
            continue
        for b in viz:
            v = Gw.loc[a, b]
            if np.isfinite(v):
                o = Gw[b].drop(a), Sw[b].drop(a)
                mm = o[0].notna() & o[1].notna()
                f = float(np.clip(o[0][mm].sum() / max(o[1][mm].sum(), 1e-9), 0.25, 4)) if mm.sum() >= 5 else 1.0
                lin.append({"posto": p, "ano": a, "g": g, "s": s, "viz": v, "sc": s * f, "dv": D[i, ok_f.index(b)]})
                break
T = pd.DataFrame(lin)
T["juntos"] = (T.sc + T.viz) / 2
T["media"] = (T.s + T.viz) / 2
est = {"s": "satélite sozinho", "viz": "pluviômetro do vizinho sozinho", "sc": "satélite corrigido pelo vizinho",
       "media": "média simples dos dois", "juntos": "juntos: vizinho + satélite corrigido"}
portao = {"janela": "1/fev a 19/mar", "n_anos": int(len(T)), "postos": int(T.posto.nunique()), "periodo": "1998–2025",
          "dist_viz_km": round(float(T.dv.median()), 1), "est": []}
for k, nome in est.items():
    e = (T[k] - T.g).abs() / T.g
    portao["est"].append({"k": k, "nome": nome, "erro100": int(round(float(e.median()) * 100)),
                          "perto": round(float((e <= PERTO).mean()), 2)})
portao["por_dist"] = []
for lo_, hi in [(2, 10), (10, 20), (20, 30)]:
    x = T[(T.dv >= lo_) & (T.dv < hi)]
    portao["por_dist"].append({"faixa": f"{lo_}–{hi} km", "n": int(len(x)),
                               **{k: int(round(float(((x[k] - x.g).abs() / x.g).median()) * 100)) for k in ["s", "viz", "juntos"]}})
print(json.dumps(portao, ensure_ascii=False, indent=1))

# ---------------------------------------------------------------- por município
B = json.loads((RAIZ / "web" / "dados" / "busca_municipios.json").read_text(encoding="utf-8"))["municipios"]
A = P[P.ok].reset_index(drop=True)
pts = gpd.GeoDataFrame(meta.reset_index(), geometry=gpd.points_from_xy(meta.lon, meta.lat), crs=4326)
ce = gpd.read_file(DADOS / "referencia" / "ceara_municipios.geojson").to_crs(4326)
pj = gpd.sjoin(pts, ce[["codarea", "geometry"]], predicate="within")
n26 = pj[pj.posto.isin(ativos26)].groupby(pj.codarea.astype(str)).size().to_dict()
usados, mun = {}, {}
for m in B:
    d = km(m["lat"], m["lon"], A.la.values, A.lo.values)
    j = int(np.argmin(d))
    usados.setdefault(j, len(usados))
    ponto = gpd.points_from_xy([m["lon"]], [m["lat"]])[0]
    le, kmar = m["cod"] in LESTE, costa_ne.distance(ponto) * 111
    faixa = 0 if le and kmar < 20 else 1 if kmar < 20 else 2 if kmar < 150 else 3  # mesma ordem de costa_tab
    mun[m["cod"]] = ([usados[j], int(round(float(d[j]))), int(le), faixa]
                     + ([int(n26.get(m["cod"], 0))] if m["uf"] == "CE" else []))
NOME = {m["cod"]: m["nome"] for m in B}
gp = gpd.GeoDataFrame(A, geometry=gpd.points_from_xy(A.lo, A.la), crs=4326)
A["cod_mun"] = gpd.sjoin(gp, MALHA[["cod", "geometry"]].to_crs(4326), how="left", predicate="within").groupby(level=0).cod.first()


def sem_acento(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(s).lower()) if unicodedata.category(c) != "Mn")


def rotulo(r):
    """Nome para a frente: o município do IBGE (com acento); se o posto tem nome de lugar, 'Lugar (Município)'."""
    mn = NOME.get(r.cod_mun) if isinstance(r.cod_mun, str) else None
    n = " ".join(w if i == 0 or w not in ("Da", "De", "Do", "Das", "Dos", "E") else w.lower() for i, w in enumerate(str(r.n).split()))
    if not mn:
        return n
    return mn if sem_acento(n) == sem_acento(mn) else f"{n} ({mn})"


pl = []
for j, _ in sorted(usados.items(), key=lambda kv: kv[1]):
    r = A.loc[j]
    pl.append({"t": r.t, "n": rotulo(r), **({"m": r.m} if isinstance(r.get("m"), str) else {}), "uf": r.uf,
               "a0": int(r.a0), "a1": int(r.a1), "nm": int(r.nm), "rz": round(float(r.rz), 2), "rd": round(float(r.rd), 2),
               "rm": round(float(r.rm), 2), "p": round(float(r.p), 2), "pc": round(float(r.pc), 2),
               "ea": int(round(float(r.ea))), "ec": int(round(float(r.ec))), "km_mar": int(round(float(r.km_mar)))})

saida = {
    "gerado": datetime.date.today().isoformat(),
    "script": "site-versao-final/ferramentas/preparar_satelite_chao.py",
    "fontes": {"satelite": "GPM IMERG V07 diário via NASA POWER, células de 0,1° (~11 km)",
               "FUNCEME": "postos pluviométricos da FUNCEME (CE), leitura às 7h, 1998–2025, ≥ 10 anos de leitura",
               "INMET": "estações automáticas do INMET no NE, dia UTC, 2016–2025"},
    "regra": {"mes_chuva_mm": MES_CHUVA, "perto": PERTO, "qc": "fora: r mensal < 0,6 ou satélite > 1,6 × pluviômetro",
              "fora_qc": int((~P.ok).sum()), "medidos": int(len(P)), "longe_km": LONGE},
    "campos_mun": ["pluviometro", "km", "costa_leste", "faixa (índice de regional.costa)", "postos_funceme_2026 (só CE)"],
    "pluv": pl, "mun": mun,
    "regional": {"costa": costa_tab, "serra": serra, "portao": portao},
}
SAIDA.write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"gravado {SAIDA} ({SAIDA.stat().st_size / 1024:.0f} KB; {len(pl)} pluviômetros, {len(mun)} municípios)")
for c in ["2311306", "2700300", "2903201", "2611606", "2704302"]:
    i, d, le, *n = mun[c]
    print(c, d, "km", le, n, pl[i])
