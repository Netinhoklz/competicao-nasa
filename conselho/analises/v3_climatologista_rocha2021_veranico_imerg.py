"""Climatologista (v3) - indicador de veranicos (iv) e IDC de Rocha et al. 2021 (RBMet 36(3):579-589, doi 10.1590/0102-77863630041)
aplicados ao IMERG V07 diario por municipio (1998-2025) e ao POWER/MERRA-2 diario (1981-2025), contra o IBGE PAM.

Definicoes conferidas no PDF local (artigos/2021_Rocha_...pdf, secoes 2.4-2.7, Tabelas 1-2, Eq. 1-4):
  veranico = >= 3 dias seguidos com chuva <= 2 mm, em fev-mai; graus 3-5, 6-10, 11-15, 16-20, >20 dias; pesos 1,2,4,8,16
  iv = sum(P_k * G_k) / PT, G_k = numero de eventos do grau k, PT = soma dos pesos (31)
  indice de seca = Nd_chuva * Nd15 * Prec / (Nd * (Nd - Maior_sem_chuva));  IDC = 1000 * indice / chuva media do Ceara no periodo
  perda PR = (Ra - Rmax)/Rmax * 100 (Rmax = maior rendimento da serie do municipio)
Numeros do artigo para comparar: iv medio 0,74 (e 0,76 como "media climatologica" na secao 3.2); IDC medio 370,72;
iv estadual 2018 = 0,62, 1993 = 1,06, 1989 = 0,59; perdas medias feijao 52,34%, milho 58,65% (1980-2018, postos FUNCEME).

Blocos:
  A) calibracao: iv/IDC medios do IMERG e do POWER contra os numeros do artigo (anos 1989, 1993, 2018)
  B) correlacao municipal iv x rendimento (e IDC, chuva FMAM) 1998-2018 e 1998-2025; Limoeiro do Norte
  C) o iv acrescenta algo a chuva total? (parcial por municipio; AUC da quebra canonica)
  D) checagem: milho + feijao = 91,0% da area cultivada no Ceara em 2017 (IBGE), afirmacao do artigo usada na proposta
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
sys.stdout.reconfigure(encoding="utf-8")
import warnings

warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DADOS, DERIV, REF

import numpy as np
import pandas as pd
import xarray as xr

S = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/saidas")
chuva = pd.read_parquet(S / "chuva_mun_diaria.parquet")  # IMERG V07 (via POWER, 0,1 grau) media por municipio
chuva.index = pd.DatetimeIndex(chuva.index)
chuva.columns = chuva.columns.astype(str)
nomes = {str(d["id"]): d["nome"] for d in json.load(open(REF / "ceara_municipios_nomes.json", encoding="utf-8"))}
pam = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
pam["cod"] = pam.cod_local.astype(str)

PESOS = np.array([1, 2, 4, 8, 16])
LIM = [(3, 5), (6, 10), (11, 15), (16, 20), (21, 10 ** 6)]


def corridas(seco):
    """comprimentos das corridas de True"""
    out, c = [], 0
    for v in seco:
        if v:
            c += 1
        elif c:
            out.append(c); c = 0
    if c:
        out.append(c)
    return out


def indicadores(x):
    """x: chuva diaria fev-mai (mm). Retorna iv, IDC parcial (sem a divisao pela media do CE), Prec etc."""
    x = np.asarray(x, float)
    seco = x <= 2.0
    runs = corridas(seco)
    G = np.array([sum(1 for r in runs if lo <= r <= hi) for lo, hi in LIM])
    iv = (PESOS * G).sum() / PESOS.sum()
    nd = len(x)
    nd_chuva = int((x > 2.0).sum())
    maior = max(runs) if runs else 0
    # Nd15: maior trecho sem veranico >= 15 dias (dias fora de corridas secas >= 15)
    em_v15 = np.zeros(nd, bool)
    i = 0
    while i < nd:
        if seco[i]:
            j = i
            while j < nd and seco[j]:
                j += 1
            if j - i >= 15:
                em_v15[i:j] = True
            i = j
        else:
            i += 1
    nd15 = max(corridas(~em_v15) or [0])
    prec = x.sum()
    ind_seca = nd_chuva * nd15 * prec / (nd * (nd - maior)) if nd > maior else 0.0
    return dict(iv=iv, n_eventos=int(G.sum()), G5=int(G[4]), nd_chuva=nd_chuva, maior_seco=maior, nd15=nd15, P=prec, ind_seca=ind_seca)


# ---------------- IMERG por municipio ----------------
rows = []
for a in range(1998, 2026):
    w = chuva.loc[f"{a}-02-01":f"{a}-05-31"]
    for cod in chuva.columns:
        d = indicadores(w[cod].values)
        d.update(cod=cod, ano=a)
        rows.append(d)
I = pd.DataFrame(rows)
pm = I[(I.ano <= 2018)].P.mean()
I["IDC"] = 1000 * I.ind_seca / pm  # media do CE no periodo 1998-2018 (o artigo usa 1980-2018)

# ---------------- POWER (MERRA-2) e IMERG reamostrado no POWER, celulas do Ceara ----------------
import geopandas as gpd
from shapely.geometry import Point

uf = gpd.read_file(REF / "ceara_uf.geojson").geometry.union_all()
ds = xr.open_dataset(DADOS / "power" / "power_ce_diario.nc")[["PRECTOTCORR", "IMERG_PRECTOT"]]
cel = [(la, lo) for la in ds.lat.values for lo in ds.lon.values if uf.contains(Point(lo, la))]
rp = []
for var, a0 in [("PRECTOTCORR", 1981), ("IMERG_PRECTOT", 1998)]:
    da = ds[var].load()
    for a in range(a0, 2026):
        w = da.sel(time=slice(f"{a}-02-01", f"{a}-05-31"))
        for la, lo in cel:
            d = indicadores(w.sel(lat=la, lon=lo).values)
            d.update(var=var, ano=a, cel=f"{la},{lo}")
            rp.append(d)
P = pd.DataFrame(rp)
for var in P["var"].unique():
    s = P["var"] == var
    P.loc[s, "IDC"] = 1000 * P.loc[s, "ind_seca"] / P.loc[s & (P.ano <= 2018), "P"].mean()

print("================ A) calibracao contra os numeros do artigo (postos FUNCEME, Thiessen por municipio, 1980-2018)")
print(f"  artigo: iv medio 0,74 | IDC medio 370,72 | iv 1989 = 0,59 | 1993 = 1,06 | 2018 = 0,62")
e = I[I.ano <= 2018]
print(f"  IMERG 0,1 grau, media por municipio, 1998-2018: iv medio {e.iv.mean():.2f} | IDC medio {e.IDC.mean():.0f} | "
      f"iv 2018 = {I[I.ano == 2018].iv.mean():.2f} | eventos/estacao {e.n_eventos.mean():.1f} | maior seco medio {e.maior_seco.mean():.1f} d | "
      f"dias > 2 mm {e.nd_chuva.mean():.1f}")
for var, nome in [("PRECTOTCORR", "POWER MERRA-2 0,5 grau"), ("IMERG_PRECTOT", "IMERG na grade POWER")]:
    q = P[P["var"] == var]
    e2 = q[q.ano <= 2018]
    f = lambda a: q[q.ano == a].iv.mean() if (q.ano == a).any() else np.nan
    print(f"  {nome:24s} ({len(cel)} celulas no CE), ate 2018: iv medio {e2.iv.mean():.2f} | IDC medio {e2.IDC.mean():.0f} | "
          f"iv 1989 = {f(1989):.2f} | 1993 = {f(1993):.2f} | 2018 = {f(2018):.2f} | eventos/estacao {e2.n_eventos.mean():.1f} | "
          f"dias > 2 mm {e2.nd_chuva.mean():.1f}")
q = P[P["var"] == "PRECTOTCORR"].groupby("ano")[["iv", "P"]].mean()
print(f"  POWER: r(iv estadual, chuva FMAM estadual) 1981-2025 = {np.corrcoef(q.iv, q.P)[0, 1]:+.2f}; anos de maior iv: "
      + ", ".join(f"{a} {v:.2f}" for a, v in q.iv.nlargest(6).items()))
q2 = I.groupby("ano")[["iv", "P"]].mean()
print(f"  IMERG: r(iv estadual, chuva FMAM estadual) 1998-2025 = {np.corrcoef(q2.iv, q2.P)[0, 1]:+.2f}; anos de maior iv: "
      + ", ".join(f"{a} {v:.2f}" for a, v in q2.iv.nlargest(6).items()))


# ---------------- B) correlacoes municipais ----------------
def rend(prefixo):
    p = pam[pam.produto.str.startswith(prefixo) & (pam.ano >= 1998) & (pam.area_plantada_ha >= 50)]
    p = p.groupby(["cod", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    p["r"] = p.producao_t / p.area_plantada_ha
    return p


print("\n================ B) correlacao por municipio (Pearson no tempo). Artigo: 'para a maior parte do estado' mais veranico -> mais perda;"
      " Jaguaribana perto de zero ou inversa (Limoeiro do Norte -0,3 no milho)")
print("  obs.: PR = (Ra - Rmax)/Rmax e linear em Ra dentro do municipio, entao corr(perda, x) = -corr(rendimento, x): a 'perda' nao muda a correlacao.")
lim_cod = [c for c, n in nomes.items() if n == "Limoeiro do Norte"][0]
J = {}
for cult, pref in [("milho", "Milho (em gr"), ("feijao", "Feij")]:
    R = rend(pref).merge(I, on=["cod", "ano"])
    J[cult] = R
    for a1 in (2018, 2025):
        g = R[R.ano <= a1]
        res = {}
        for v in ["iv", "IDC", "P", "maior_seco"]:
            cc = g.groupby("cod").apply(lambda h: np.corrcoef(h[v], h.r)[0, 1] if len(h) >= 12 and h[v].std() > 0 else np.nan).dropna()
            res[v] = cc
        n = len(res["iv"])
        rc = 0.433 if a1 == 2018 else 0.374  # |r| critico bicaudal 5% para n=21 e n=28
        print(f"  {cult:6s} 1998-{a1} ({n} municipios): r(iv, rend) mediana {res['iv'].median():+.2f}, negativa em {(res['iv'] < 0).mean():.0%} "
              f"(signif. 5% em {(res['iv'] < -rc).mean():.0%}) | r(IDC, rend) mediana {res['IDC'].median():+.2f}, positiva em {(res['IDC'] > 0).mean():.0%} | "
              f"r(chuva FMAM, rend) mediana {res['P'].median():+.2f}, positiva em {(res['P'] > 0).mean():.0%} | r(maior seco, rend) {res['maior_seco'].median():+.2f}")
        if a1 == 2018:
            print(f"     Limoeiro do Norte: r(iv, rend) = {res['iv'].get(lim_cod, np.nan):+.2f} (perda: {-res['iv'].get(lim_cod, np.nan):+.2f}); "
                  f"r(IDC, rend) = {res['IDC'].get(lim_cod, np.nan):+.2f} (perda: {-res['IDC'].get(lim_cod, np.nan):+.2f})")
    # perda media no estilo do artigo (1998-2018)
    g = R[R.ano <= 2018].copy()
    g["PR"] = g.groupby("cod").r.transform(lambda s: (s - s.max()) / s.max() * 100)
    print(f"     perda media estilo Rocha (Ra relativo ao maximo do municipio, 1998-2018): {-g.PR.mean():.1f}% (artigo 1980-2018: "
          f"{'58,65' if cult == 'milho' else '52,34'}%)")

# ---------------- C) o iv acrescenta algo a chuva total? ----------------
print("\n================ C) o iv acrescenta algo a chuva total de fev-mai? (1998-2025)")


def auc(score, y):
    y = np.asarray(y, bool); s = np.asarray(score, float)
    ok = np.isfinite(s)
    s, y = s[ok], y[ok]
    rk = pd.Series(s).rank().values
    n1, n0 = y.sum(), (~y).sum()
    return (rk[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


for cult in ["milho", "feijao"]:
    R = J[cult].copy()
    # quebra canonica: rendimento < 50% da mediana dos outros anos do municipio
    R["ref"] = R.groupby("cod").r.transform(lambda s: pd.Series([np.median(np.delete(s.values, i)) if len(s) > 5 else np.nan
                                                                  for i in range(len(s))], index=s.index))
    R = R.dropna(subset=["ref"])
    R["quebra"] = R.r / R.ref < 0.5
    R["pct"] = R.P / R.groupby("cod").P.transform("median")
    # residuo do iv dado log(chuva) (dentro do municipio)
    R["lp"] = np.log(R.P + 1)
    R["iv_res"] = R.groupby("cod", group_keys=False).apply(
        lambda h: h.iv - np.polyval(np.polyfit(h.lp, h.iv, 1), h.lp) if h.lp.std() > 0 else h.iv * np.nan)
    R["lr"] = np.log(R.r / R.ref)
    parc = R.groupby("cod").apply(lambda h: (lambda e1, e2: np.corrcoef(e1, e2)[0, 1])(
        h.lr - np.polyval(np.polyfit(h.lp, h.lr, 1), h.lp), h.iv - np.polyval(np.polyfit(h.lp, h.iv, 1), h.lp)) if len(h) >= 12 else np.nan).dropna()
    rm = np.corrcoef(R.pct, R.iv)[0, 1]
    print(f"  {cult:6s}: n = {len(R)} municipio-anos, taxa de quebra {R.quebra.mean():.1%}; r(iv, % do normal) = {rm:+.2f}")
    print(f"     AUC quebra: chuva (% do normal, menor = risco) {auc(-R.pct, R.quebra):.3f} | iv {auc(R.iv, R.quebra):.3f} | "
          f"maior seco {auc(R.maior_seco, R.quebra):.3f} | IDC (menor = risco) {auc(-R.IDC, R.quebra):.3f} | "
          f"residuo do iv dado a chuva {auc(R.iv_res, R.quebra):.3f}")
    print(f"     parcial r(iv, log-rendimento | log-chuva) por municipio: mediana {parc.median():+.2f}, negativa em {(parc < 0).mean():.0%} ({len(parc)} municipios)")
    # dentro do tercil de chuva normal: o iv separa?
    t = R.pct.quantile([1 / 3, 2 / 3]).values
    mid = R[(R.pct >= t[0]) & (R.pct <= t[1])]
    hi = mid.iv >= mid.iv.median()
    print(f"     so anos de chuva no tercil do meio (n={len(mid)}): quebra com iv acima da mediana {mid.quebra[hi].mean():.1%} contra "
          f"{mid.quebra[~hi].mean():.1%} abaixo (AUC iv {auc(mid.iv, mid.quebra):.3f})")
    # por ano: replay de 2012 e 2016 e 2018
    for a in (2012, 2016, 2018):
        g = R[R.ano == a]
        print(f"     {a}: iv medio {g.iv.mean():.2f}, chuva % normal mediana {g.pct.median():.0%}, quebra {g.quebra.mean():.0%}")

# ---------------- D) 91% da area ----------------
print("\n================ D) 'milho e feijao correspondem a 91,0% das areas cultivadas no estado' (IBGE 2017, citado no artigo e na proposta)")
p17 = pam[pam.ano == 2017]
mf = p17[p17.produto.str.startswith("Milho (em gr") | p17.produto.str.startswith("Feij")].area_plantada_ha.sum()
tot_t = p17[p17.tipo == "temporaria"].area_plantada_ha.sum()
tot_all = p17.area_plantada_ha.sum()
col_all = p17.area_colhida_ha.sum()
mfc = p17[p17.produto.str.startswith("Milho (em gr") | p17.produto.str.startswith("Feij")].area_colhida_ha.sum()
print(f"  PAM 2017: milho+feijao area plantada {mf:,.0f} ha; temporarias {tot_t:,.0f} ha -> {mf / tot_t:.1%}; "
      f"todas as lavouras (temp.+perm.) {tot_all:,.0f} ha -> {mf / tot_all:.1%}; por area colhida {mfc / col_all:.1%}")
for a in (2016, 2018, 2025):
    pa = pam[pam.ano == a]
    m_ = pa[pa.produto.str.startswith("Milho (em gr") | pa.produto.str.startswith("Feij")].area_plantada_ha.sum()
    print(f"  PAM {a}: milho+feijao / todas as lavouras (area plantada) = {m_ / pa.area_plantada_ha.sum():.1%}")
print(f"  tipos no PAM: {pam.tipo.unique().tolist()}")
