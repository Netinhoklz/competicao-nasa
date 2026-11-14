"""Cetico cientifico, banca adversaria rodada 2 (parte 2): o "1% do SMAP" do gatilho e a carteira 1/3 de mandioca.

(1) O slide 6 da v2 diz "NASA's off-the-shelf SMAP drought percentile flagged 1% of counties in 2016". O gatilho do
    economista (v2_economista_gatilho_smap.py, linha 89) usa a MEDIA de fev-abr (ou fev-mai) do percentil diario <= 20.
    Media de percentis diarios nao e percentil: a variancia encolhe para perto de 50. Teste: mesma serie, tres leituras
    (media sazonal do percentil pronto; media de 7 dias em 30/abr, a luz 2 da v2; posto da media sazonal da umidade
    contra os outros anos). Nenhuma escolhida pelo resultado: todas reportadas.
(2) Quixada: as leituras de chuva IMERG alternativas (fev->portao, API tau 13 d, 30 d, 15 d) nos anos de quebra.
(3) Carteira 1/3 (M4, "pior ano em 10" 0,15 -> 0,36): quanto do ganho e so MEDIA de series com ruido de relato
    independente, e nao tolerancia da mandioca? Placebo pre-declarado: o terco de mandioca vira o MILHO (ou o FEIJAO)
    de um dos 5 municipios vizinhos mais proximos no MESMO ano (mesmo clima, outro relato). Media de 200 sorteios.
    Sensibilidade: mandioca do ano seguinte (ciclo de 12-24 meses).
So le arquivos. Saida: v2_cetico_r2b_gatilho_carteira.saida.txt
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import warnings

import geopandas as gpd
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)
D = "E:/campeonato-nasa/dados/derivados/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
SAIDA = A + "v2_cetico_r2b_gatilho_carteira.saida.txt"
LIN = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LIN.append(s)


rng = np.random.default_rng(1511)
QXD = "2311306"
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
pam = pam[(pam.ano >= 1998) & (pam.ano <= 2025)]


def canonica(pref):
    p = pam[pam.produto.str.startswith(pref) & (pam.area_plantada_ha >= 50)]
    p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha
    o = []
    for cod, g in p.groupby("cod_local"):
        r = g.r.values
        med = np.array([np.median(np.delete(r, i)) if len(r) > 5 else np.nan for i in range(len(r))])
        o.append(pd.DataFrame({"cod": str(cod)[:7], "ano": g.ano.values, "razao": r / med}))
    return pd.concat(o).dropna().set_index(["cod", "ano"]).razao


MILHO = canonica("Milho (em")
FEIJ = canonica("Feij")
MAND = canonica("Mandioca")

# ======================================================================================
out("=" * 20, "1. O '1% do SMAP' do gatilho: media sazonal de percentis x leituras de portao (milho, 2016-2025)", "=" * 20)
PC = pd.read_parquet(A + "saidas/v2_hidrologo_smap_pctl_mun_diario.parquet")
RZ = pd.read_parquet(A + "saidas/v2_hidrologo_smap_rz_mun_diario.parquet")
PC.columns = PC.columns.astype(str)
RZ.columns = RZ.columns.astype(str)
li = []
for a in range(2016, 2026):
    t = pd.Timestamp(a, 4, 30)
    li.append(pd.DataFrame({"ano": a, "cod": PC.columns,
                            "media_fev_abr_pctl": PC.loc[f"{a}-02-01":t].mean().values,
                            "pctl_7d_30abr": PC.loc[t - pd.Timedelta(days=6):t].mean().values,
                            "rz_fev_abr": RZ.loc[f"{a}-02-01":t].mean().reindex(PC.columns).values}))
S = pd.concat(li)
S = S.reset_index(drop=True)
pos = []
for c, g in S.groupby("cod"):
    v = g.rz_fev_abr.values
    pos.append(pd.Series([100 * np.mean(np.delete(v, i) < v[i]) for i in range(len(v))], index=g.index))
S["posto_rz_fev_abr"] = pd.concat(pos)
q = MILHO.rename("razao").reset_index()
q = q[q.ano.between(2016, 2025)]
q["quebra"] = q.razao < 0.5
df = q.merge(S, on=["cod", "ano"]).dropna()
out(f"  n = {len(df)} municipio-anos; quebras {int(df.quebra.sum())} (2016: {int(df[df.ano == 2016].quebra.sum())})")
for c in ["media_fev_abr_pctl", "pctl_7d_30abr", "posto_rz_fev_abr"]:
    al = df[c] <= 20
    q16 = df.quebra & (df.ano == 2016)
    out(f"  {c:<22} dp {df[c].std():5.1f} | p10 {df[c].quantile(.1):5.1f} | mediana {df[c].median():5.1f} | acende (<= 20) {al.mean():5.1%} | "
        f"2016: {int((al & q16).sum())}/{int(q16.sum())} quebras (alertas {int((al & (df.ano == 2016)).sum())}) | "
        f"P(q|alerta) {df.quebra[al].mean():.2f}")
out("  Leitura: o '1%' vem de tirar a MEDIA de 89 percentis diarios (que encolhe a variancia), nao do produto da NASA.")

# ======================================================================================
out("\n" + "=" * 20, "2. Quixada: leituras de chuva IMERG alternativas nos anos 2016-2025 (% do normal; < 0,75 acende)", "=" * 20)
chuva = pd.read_parquet(A + "estrategista_cache_chuva_mun_diaria.parquet")
chuva.columns = chuva.columns.astype(str)
ANOS = list(range(1998, 2026))


def ler(m, d, tipo, cod):
    v = {}
    for a in ANOS:
        g = pd.Timestamp(a, m, d)
        x = chuva[cod]
        if tipo == "W1":
            v[a] = x.loc[f"{a}-01-01":g].sum()
        elif tipo == "W2":
            v[a] = x.loc[f"{a}-02-01":g].sum()
        elif tipo == "R30":
            v[a] = x.loc[g - pd.Timedelta(days=29):g].sum()
        elif tipo == "R15":
            v[a] = x.loc[g - pd.Timedelta(days=14):g].sum()
        elif tipo == "API":
            sl = x.loc[f"{a}-01-01":g]
            v[a] = (sl.values * np.exp(-(len(sl) - 1 - np.arange(len(sl))) / 13)).sum()
    s = pd.Series(v)
    return pd.Series({a: s[a] / s.drop(a).median() for a in ANOS})


qx = MILHO.xs(QXD, level="cod")
for (m, d, gn) in [(3, 19, "19/mar"), (4, 30, "30/abr")]:
    tb = pd.DataFrame({t: ler(m, d, t, QXD) for t in ["W1", "W2", "API", "R30", "R15"]}).loc[2016:2025]
    tb.insert(0, "razao_milho", qx.reindex(tb.index))
    out(f"  [{gn}]\n" + tb.round(2).to_string().replace("\n", "\n    "))

# ======================================================================================
out("\n" + "=" * 20, "3. Carteira 1/3: mandioca contra placebo de vizinho (mesmo ano, outro relato)", "=" * 20)
g = gpd.read_file("E:/campeonato-nasa/dados/referencia/ceara_municipios.geojson").to_crs(5880)
g["cod"] = g.codarea.astype(str)
cen = np.c_[g.geometry.centroid.x, g.geometry.centroid.y]
dist = np.sqrt(((cen[:, None, :] - cen[None, :, :]) ** 2).sum(-1))
VIZ = {g.cod.iloc[i]: [g.cod.iloc[j] for j in np.argsort(dist[i])[1:6]] for i in range(len(g))}

Y = pd.DataFrame({"milho": MILHO, "feijao": FEIJ, "mandioca": MAND}).dropna().reset_index()
Y["mand_t1"] = [MAND.get((c, a + 1), np.nan) for c, a in zip(Y.cod, Y.ano)]


def cvar(s):
    s = pd.Series(s).dropna()
    return s[s <= s.quantile(0.10)].mean()


out(f"  n = {len(Y)} municipio-anos com milho, feijao e mandioca (mesma amostra da M4, definicao b)")
out(f"  100% milho CVaR10 {cvar(Y.milho):.3f} | milho+feijao {cvar(Y[['milho', 'feijao']].mean(1)):.3f} | "
    f"1/3 com mandioca {cvar(Y[['milho', 'feijao', 'mandioca']].mean(1)):.3f}")
for nome, serie in [("milho do vizinho", MILHO), ("feijao do vizinho", FEIJ)]:
    vals = []
    for _ in range(200):
        terc = []
        for c, a in zip(Y.cod, Y.ano):
            cand = [v for v in VIZ.get(c, []) if (v, a) in serie.index]
            terc.append(serie[(cand[rng.integers(len(cand))], a)] if cand else np.nan)
        Y["_t"] = terc
        vals.append(cvar(Y[["milho", "feijao", "_t"]].mean(1)))
    out(f"  PLACEBO 1/3 com {nome:<18} CVaR10 {np.mean(vals):.3f} (faixa dos 200 sorteios {np.min(vals):.3f}-{np.max(vals):.3f})")
y1 = Y.dropna(subset=["mand_t1"])
out(f"  Sensibilidade, mandioca do ano SEGUINTE (n = {len(y1)}): 1/3 {cvar(y1[['milho', 'feijao', 'mand_t1']].mean(1)):.3f} | "
    f"mesma amostra com mandioca do ano: {cvar(y1[['milho', 'feijao', 'mandioca']].mean(1)):.3f} | milho {cvar(y1.milho):.3f}")
cauda = Y[Y.milho <= Y.milho.quantile(0.10)]
out(f"  Na cauda do milho (10% piores, n = {len(cauda)}): razao mediana milho {cauda.milho.median():.2f} | feijao "
    f"{cauda.feijao.median():.2f} | mandioca {cauda.mandioca.median():.2f} | mandioca do ano seguinte {cauda.mand_t1.median():.2f}")
rep = pam[pam.produto.str.startswith("Mandioca") & (pam.area_plantada_ha >= 50)].copy()
rep["r"] = rep.producao_t / rep.area_plantada_ha
rep["cod_local"] = rep.cod_local.astype(str).str[:7]
rep = rep.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
rep["r"] = rep.producao_t / rep.area_plantada_ha
rep = rep.sort_values(["cod_local", "ano"])
rep["igual_ano_ant"] = rep.groupby("cod_local").r.diff().abs() < 1e-9
ca = rep.merge(cauda.assign(cod_local=cauda.cod.astype(str))[["cod_local", "ano"]], on=["cod_local", "ano"])
out(f"  Mandioca na cauda do milho com rendimento IDENTICO ao do ano anterior: {ca.igual_ano_ant.mean():.0%} (n = {len(ca)}); "
    f"em todos os anos: {rep.igual_ano_ant.mean():.0%}")

with open(SAIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(LIN) + "\n")
