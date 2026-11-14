"""Rodada 1 (v4), engenheiro do motor de rotacao: teste de generalizacao com os nossos dados.

Pergunta (fixada antes de rodar): no painel municipio-ano do IBGE PAM, a area de leguminosas de grao no ano t-1
(feijao + fava + amendoim), como fracao da area plantada de lavouras temporarias, se associa ao rendimento do milho no
ano t, controlando a chuva IMERG de fev-mai do ano t e os efeitos fixos de municipio e de ano?

Desenho (pre-declarado):
- Ceara (PAM completo, 184 municipios): fracao = (feijao + fava + amendoim) / total das temporarias, area plantada.
- Nordeste (PAM derivado com 7 produtos): fracao = feijao / (milho + feijao + mandioca + algodao herbaceo + sorgo).
  O bloco 0 confere no CE quanto essa aproximacao cobre.
- t = 1999..2025 (o IMERG comeca em 1998; a chuva de t-1 entra como controle). Milho com >= 50 ha plantados em t;
  total das temporarias >= 100 ha em t-1; municipios com >= 5 anos validos.
- Y principal: ln(rendimento do milho em kg por ha colhido). Alternativa com as perdas totais: razao
  producao/area plantada sobre a mediana do municipio (corte em 3).
- Chuva: soma fev-mai do IMERG (POWER IMERG_PRECTOT agregado ao municipio), em centenas de mm, com termo quadratico.
- Efeitos fixos de municipio e de ano absorvidos por projecoes alternadas. EP agrupado por ANO (CR1, t com G-1 gl);
  para comparar, agrupado por municipio e nos dois sentidos (Cameron-Gelbach-Miller).
- Confundimentos testados: (a) consorcio/persistencia -> fracao em t entra como controle; (b) area total -> ln da
  area total em t-1 e em t; (c) tendencia -> tendencia linear por municipio; (d) retroalimentacao -> placebo com a
  fracao de t+1 (o futuro nao pode causar o milho de t).
- Leitura: efeito em % do rendimento do milho por +10 p.p. de leguminosa em t-1; MDE80 = 2,8 x EP (5%, poder 80%).
- Referencia da literatura (do texto dos artigos, ver catalogo do conselho): Zhao 2022 p.2, leguminosa antecessora
  +20,4% (IC95 17,7-23,1); milho apos leguminosa +28,9% (25,5-32,2) p.5; feijao comum +14,5% (9,5-19,5) p.5;
  Mudare 2025 p.2, leguminosa +23% (19-28). Se TODA a area de leguminosa de t-1 recebesse milho em t, +10 p.p.
  deslocariam o milho do municipio em ~0,1 x ln(1 + efeito). Esse e o teto do que o painel poderia ver.
So le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
from scipy import stats

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 200)
D = "E:/campeonato-nasa/dados/derivados/"
ANOS = range(1999, 2026)


def cab(t):
    print("\n" + "=" * 20 + " " + t + " " + "=" * 20)


# ----------------------------------------------------------------------------- chuva fev-mai IMERG por municipio-ano
im = pd.read_parquet(D + "ibge_ne_mun_imerg_mensal.parquet")
im["ano"] = im.data.dt.year
im["mes"] = im.data.dt.month
q = im[im.mes.between(2, 5)].groupby(["cod_mun", "ano"]).precip_mm.agg(["sum", "count"])
q = q[q["count"] == 4]["sum"].rename("chuva_fm").reset_index().rename(columns={"cod_mun": "cod"})


def grade(df, cols):
    """Reindexa para a grade completa municipio x ano (1997-2025) para que shift(1) seja exatamente o ano anterior."""
    idx = pd.MultiIndex.from_product([sorted(df.cod.unique()), range(1997, 2026)], names=["cod", "ano"])
    return df.set_index(["cod", "ano"])[cols].reindex(idx).reset_index()


def montar(milho, A_leg, A_tot):
    p = pd.concat([milho, A_leg, A_tot], axis=1).reset_index()
    p = p[(p.ano >= 1997) & (p.ano <= 2025)]
    p["A_leg"] = p["A_leg"].fillna(0.0)
    p = grade(p, ["area_plantada_ha", "area_colhida_ha", "producao_t", "A_leg", "A_tot"])
    p = p.merge(q, on=["cod", "ano"], how="left")
    p["share"] = np.where(p.A_tot >= 100, p.A_leg / p.A_tot, np.nan)
    g = p.groupby("cod")
    p["share_l1"] = g.share.shift(1)
    p["share_l2"] = g.share.shift(2)
    p["share_f1"] = g.share.shift(-1)
    p["lnA_tot"] = np.log(p.A_tot.where(p.A_tot >= 100))
    p["lnA_tot_l1"] = g.lnA_tot.shift(1)
    p["chuva"] = p.chuva_fm / 100.0
    p["chuva2"] = p.chuva ** 2
    p["chuva_l1"] = g.chuva.shift(1)
    ok = p.area_plantada_ha >= 50
    rend = p.producao_t * 1000 / p.area_colhida_ha
    p["y_ln"] = np.where(ok & (p.producao_t > 0) & (p.area_colhida_ha > 0), np.log(rend.clip(lower=1)), np.nan)
    r_pl = np.where(ok, p.producao_t * 1000 / p.area_plantada_ha, np.nan)
    p["r_pl"] = r_pl
    med = p.groupby("cod").r_pl.transform("median")
    p["y_razao"] = (p.r_pl / med).clip(upper=3)
    # z da chuva dentro do municipio (para a interacao tipo Kluger: efeito maior com mais chuva?)
    p["chuva_z"] = (p.chuva - p.groupby("cod").chuva.transform("mean")) / p.groupby("cod").chuva.transform("std")
    p["share_l1_x_chz"] = p.share_l1 * p.chuva_z
    p["share_f1_x_chz"] = p.share_f1 * p.chuva_z
    # composicao media do municipio x chuva: absorve a sensibilidade a chuva propria dos municipios de muito feijao
    p["sharebar_x_chz"] = p.groupby("cod").share.transform("mean") * p.chuva_z
    return p[p.ano.isin(ANOS)].copy()


# ----------------------------------------------------------------------------- painel CE (PAM completo)
pam = pd.read_parquet(D + "ibge_pam_mun_anual.parquet")
pam = pam[pam.tipo == "temporaria"].copy()
pam["cod"] = pam.cod_local.astype(str).str[:7]
A_tot_ce = pam.groupby(["cod", "ano"]).area_plantada_ha.sum().rename("A_tot")
eh_leg = pam.produto.str.startswith(("Feijão", "Fava", "Amendoim"))
A_leg_ce = pam[eh_leg].groupby(["cod", "ano"]).area_plantada_ha.sum().rename("A_leg")
mil_ce = pam[pam.produto.str.startswith("Milho (em")].groupby(["cod", "ano"])[
    ["area_plantada_ha", "area_colhida_ha", "producao_t"]].sum()
ce = montar(mil_ce, A_leg_ce, A_tot_ce)

# proxy NE calculada no proprio CE (para o bloco 0)
cinco = ("Milho (em", "Feijão", "Mandioca", "Algodão herbáceo", "Sorgo")
A5_ce = pam[pam.produto.str.startswith(cinco)].groupby(["cod", "ano"]).area_plantada_ha.sum().rename("A_tot")
Af_ce = pam[pam.produto.str.startswith("Feijão")].groupby(["cod", "ano"]).area_plantada_ha.sum().rename("A_leg")
ce_proxy = montar(mil_ce, Af_ce, A5_ce)

# ----------------------------------------------------------------------------- painel NE (PAM derivado, 7 produtos)
ne_raw = pd.read_parquet(D + "ibge_ne_pam_mun_anual.parquet")
ne_raw = ne_raw[ne_raw.tipo == "temporaria"].rename(columns={"cod_mun": "cod"})
ne_raw["cod"] = ne_raw.cod.astype(str).str[:7]
A5_ne = ne_raw[ne_raw.produto.isin(["Milho", "Feijão", "Mandioca", "Algodão herbáceo", "Sorgo"])].groupby(
    ["cod", "ano"]).area_plantada_ha.sum().rename("A_tot")
Af_ne = ne_raw[ne_raw.produto == "Feijão"].groupby(["cod", "ano"]).area_plantada_ha.sum().rename("A_leg")
mil_ne = ne_raw[ne_raw.produto == "Milho"].groupby(["cod", "ano"])[
    ["area_plantada_ha", "area_colhida_ha", "producao_t"]].sum()
ne = montar(mil_ne, Af_ne, A5_ne)
uf_de = ne_raw.drop_duplicates("cod").set_index("cod").uf
ne["uf"] = ne.cod.map(uf_de)
semi = pd.read_parquet("E:/campeonato-nasa/dados/ibge_nordeste/teste_rotacao_seca.parquet")["semiarido_2022"]
semi.index = semi.index.astype(str).str[:7]
ne["semiarido"] = ne.cod.map(semi)


# ----------------------------------------------------------------------------- estimador
def absorver(d, cols, tendencia=False, tol=1e-10, max_iter=1000):
    """Projecoes alternadas: tira EF de municipio (ou municipio + tendencia linear) e EF de ano."""
    X = d[cols].astype(float).copy()
    gm, ga = d.cod.values, d.ano.values
    tt = (d.ano - d.groupby("cod").ano.transform("mean")).astype(float)
    tt2 = (tt ** 2).groupby(gm).transform("sum").replace(0, np.nan)
    for _ in range(max_iter):
        velho = X.values.copy()
        X = X - X.groupby(gm).transform("mean")
        if tendencia:
            incl = X.mul(tt, axis=0).groupby(gm).transform("sum").div(tt2, axis=0).fillna(0.0)
            X = X - incl.mul(tt, axis=0)
        X = X - X.groupby(ga).transform("mean")
        if np.nanmax(np.abs(X.values - velho)) < tol:
            break
    return X


def mqo(dados, y, xs, tendencia=False):
    d = dados.dropna(subset=[y] + xs).copy()
    d = d[d.groupby("cod").ano.transform("size") >= 5]
    Z = absorver(d, [y] + xs, tendencia=tendencia)
    Y, X = Z[y].values, Z[xs].values
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ Y
    u = Y - X @ b
    N, k = X.shape
    nm, na = d.cod.nunique(), d.ano.nunique()
    Xu = X * u[:, None]

    def meio(grupos):
        S = pd.DataFrame(Xu).groupby(grupos).sum().values
        return S.T @ S

    K_ano = k + nm * (2 if tendencia else 1)          # EF de ano aninhado no cluster de ano
    K_mun = k + na - 1                                 # EF de municipio aninhado no cluster de municipio
    V_ano = XtXi @ meio(d.ano.values) @ XtXi * na / (na - 1) * (N - 1) / (N - K_ano)
    V_mun = XtXi @ meio(d.cod.values) @ XtXi * nm / (nm - 1) * (N - 1) / (N - K_mun)
    V_hc = XtXi @ (Xu.T @ Xu) @ XtXi * (N - 1) / (N - K_ano - na)
    V_2 = V_ano + V_mun - V_hc
    se_a, se_m = np.sqrt(np.diag(V_ano)), np.sqrt(np.diag(V_mun))
    se_2 = np.sqrt(np.maximum(np.diag(V_2), np.diag(V_ano)))
    return dict(b=b, se_a=se_a, se_m=se_m, se_2=se_2, N=N, nm=nm, na=na, xs=xs, d=d, Z=Z, y=y, V_a=V_ano)


def contraste(r, nome):
    """Efeito corrigido pelo placebo: coef(t-1) - coef(t+1) no modelo conjunto, EP por ano (com a covariancia)."""
    a, c = r["xs"].index("share_l1"), r["xs"].index("share_f1")
    dlt = r["b"][a] - r["b"][c]
    se = np.sqrt(r["V_a"][a, a] + r["V_a"][c, c] - 2 * r["V_a"][a, c])
    tcrit = stats.t.ppf(0.975, r["na"] - 1)
    p = 2 * stats.t.sf(abs(dlt / se), r["na"] - 1)
    print(f"  {nome:<58s} {10 * dlt:+6.2f}% (aprox.) por +10 p.p. | IC95 ano [{10 * (dlt - tcrit * se):+6.2f},"
          f" {10 * (dlt + tcrit * se):+6.2f}] p={p:.3f} | MDE80 {28 * se:.1f}%")


def linha(r, nome, j=0, escala="log"):
    b, se, se_m, se_2 = r["b"][j], r["se_a"][j], r["se_m"][j], r["se_2"][j]
    tcrit = stats.t.ppf(0.975, r["na"] - 1)
    p = 2 * stats.t.sf(abs(b / se), r["na"] - 1)
    if escala == "log":
        f = lambda v: 100 * (np.exp(0.1 * v) - 1)  # noqa: E731
        un = "% do milho"
    else:
        f = lambda v: 100 * 0.1 * v  # noqa: E731
        un = "p.p. do normal"
    mde = 100 * 0.1 * 2.8 * se
    print(f"  {nome:<58s} {f(b):+6.2f} {un} por +10 p.p. | IC95 ano [{f(b - tcrit * se):+6.2f}, {f(b + tcrit * se):+6.2f}]"
          f" p={p:.3f} | EP ano/mun/2v = {se:.3f}/{se_m:.3f}/{se_2:.3f} | MDE80 {mde:.1f} | n={r['N']}, mun={r['nm']}, anos={r['na']}")


def coef(r, nome):
    j = r["xs"].index(nome)
    return r["b"][j], r["se_a"][j]


# ============================================================================= BLOCO 0: checagens
cab("BLOCO 0: checagens de dados")
print(f"  CE: {ce.cod.nunique()} municipios; anos {ce.ano.min()}-{ce.ano.max()}; municipio-anos com Y e fracao t-1:"
      f" {ce.dropna(subset=['y_ln', 'share_l1', 'chuva']).shape[0]}")
print(f"  NE: {ne.cod.nunique()} municipios; municipio-anos com Y e fracao t-1: "
      f"{ne.dropna(subset=['y_ln', 'share_l1', 'chuva']).shape[0]}")
print(f"  chuva fev-mai IMERG no CE: mediana {100 * ce.chuva.median():.0f} mm (p10 {100 * ce.chuva.quantile(.1):.0f},"
      f" p90 {100 * ce.chuva.quantile(.9):.0f})")
m = ce[["cod", "ano", "share"]].merge(ce_proxy[["cod", "ano", "share"]], on=["cod", "ano"], suffixes=("", "_px")).dropna()
dm = m.groupby("cod")[["share", "share_px"]].transform(lambda s: s - s.mean())
print(f"  CE: fracao completa (feijao+fava+amendoim / todas temporarias) x aproximacao do NE (feijao / 5 culturas):"
      f" r bruto {m.share.corr(m.share_px):.3f}; r dentro do municipio {dm.share.corr(dm.share_px):.3f};"
      f" medias {m.share.mean():.3f} x {m.share_px.mean():.3f}")
print(f"  fracao de leguminosa t-1 no CE: mediana {ce.share_l1.median():.3f}; p10 {ce.share_l1.quantile(.1):.3f};"
      f" p90 {ce.share_l1.quantile(.9):.3f}")

# ============================================================================= BLOCO 1: quanto da variacao sobra (confundimento por persistencia)
cab("BLOCO 1: persistencia da fracao (o consorcio milho+feijao repete no mesmo roçado)")
for nome, P in [("CE", ce), ("NE", ne)]:
    d = P.dropna(subset=["y_ln", "share_l1", "share", "chuva", "lnA_tot", "lnA_tot_l1", "chuva_l1"])
    d = d[d.groupby("cod").ano.transform("size") >= 5]
    Z = absorver(d, ["share_l1", "share", "share_l2", "lnA_tot", "lnA_tot_l1", "chuva", "chuva_l1"])
    sd_bruto = d.share_l1.std()
    sd_fe = Z.share_l1.std()
    X = Z[["share", "lnA_tot", "lnA_tot_l1", "chuva", "chuva_l1"]].values
    bb = np.linalg.lstsq(X, Z.share_l1.values, rcond=None)[0]
    res = Z.share_l1.values - X @ bb
    r2 = 1 - res.var() / Z.share_l1.var()
    print(f"  {nome}: dp da fracao t-1 bruto {sd_bruto:.3f}; depois dos EF {sd_fe:.3f}; "
          f"r(t-1, t) depois dos EF {Z.share_l1.corr(Z.share):+.3f}; r(t-1, t-2) {Z.share_l1.corr(Z.share_l2):+.3f};"
          f" R2 da fracao t-1 pelos controles {r2:.2f}; dp que sobra {res.std():.3f} (= {1000 * res.std():.0f} p.p./10)")

# ============================================================================= BLOCO 2: CE, especificacoes
CH = ["chuva", "chuva2"]
CTR = ["share", "lnA_tot", "lnA_tot_l1", "chuva_l1"]
cab("BLOCO 2: CEARA, ln(rendimento do milho em t) ~ leguminosa em t-1 (EF municipio + ano; EP por ano)")
r1 = mqo(ce, "y_ln", ["share_l1"] + CH)
linha(r1, "A1 base: fracao t-1 + chuva fev-mai (quadratica)")
bch, sch = coef(r1, "chuva")
b2, _ = coef(r1, "chuva2")
c0 = ce.chuva.median()
print(f"     (checagem: efeito marginal da chuva na mediana {100 * c0:.0f} mm = {100 * (bch + 2 * b2 * c0):+.1f}% do"
      f" milho por +100 mm)")
r2 = mqo(ce, "y_ln", ["share_l1"] + CH + CTR)
linha(r2, "A2 + fracao em t (consorcio) + ln area total t e t-1 + chuva t-1")
bt, st = coef(r2, "share")
print(f"     (fracao em t, o consorcio do mesmo ano: {100 * (np.exp(0.1 * bt) - 1):+.2f}% por +10 p.p., EP {st:.3f})")
r3 = mqo(ce, "y_ln", ["share_l1"] + CH + CTR, tendencia=True)
linha(r3, "A3 = A2 + tendencia linear por municipio")
r4 = mqo(ce, "y_ln", ["share_f1"] + CH + CTR)
linha(r4, "A4 PLACEBO: fracao em t+1 no lugar de t-1 (mesmos controles)")
r4b = mqo(ce, "y_ln", ["share_l1", "share_f1"] + CH + CTR)
linha(r4b, "A4b fracao t-1 com t+1 junto: coef. de t-1", 0)
linha(r4b, "A4b fracao t-1 com t+1 junto: coef. de t+1 (placebo)", 1)
r5 = mqo(ce, "y_ln", ["share_l1", "share_l1_x_chz", "chuva_z"] + CH + CTR)
linha(r5, "A5 interacao: fracao t-1 x chuva (z no municipio): principal", 0)
linha(r5, "A5 interacao: muda por +1 dp de chuva", 1)
r5p = mqo(ce, "y_ln", ["share_f1", "share_f1_x_chz", "chuva_z"] + CH + CTR)
linha(r5p, "A5p PLACEBO da interacao: fracao t+1 x chuva", 1)
r5c = mqo(ce, "y_ln", ["share_l1", "share_l1_x_chz", "chuva_z", "sharebar_x_chz"] + CH + CTR)
linha(r5c, "A5c interacao t-1 x chuva, com composicao media x chuva", 1)
r5cp = mqo(ce, "y_ln", ["share_f1", "share_f1_x_chz", "chuva_z", "sharebar_x_chz"] + CH + CTR)
linha(r5cp, "A5cp PLACEBO de A5c: fracao t+1 x chuva", 1)
r5d = mqo(ce_proxy, "y_ln", ["share_l1", "share_l1_x_chz", "chuva_z", "sharebar_x_chz"] + CH + CTR)
linha(r5d, "A5d = A5c com a fracao aproximada do NE (replica no CE?)", 1)
contraste(r4b, "A4c CORRIGIDO PELO PLACEBO: coef(t-1) - coef(t+1)")
r6 = mqo(ce, "y_razao", ["share_l1"] + CH + CTR)
linha(r6, "A6 Y = razao producao/area plantada (com perdas totais)", escala="nivel")
r6p = mqo(ce, "y_razao", ["share_f1"] + CH + CTR)
linha(r6p, "A6 PLACEBO t+1, Y = razao", escala="nivel")
r7 = mqo(ce_proxy, "y_ln", ["share_l1"] + CH + CTR)
linha(r7, "A7 = A2 com a fracao aproximada do NE (feijao / 5 culturas)")

# ============================================================================= BLOCO 3: NE
cab("BLOCO 3: NORDESTE (9 UFs), fracao = feijao / 5 temporarias; EP por ano")
s1 = mqo(ne, "y_ln", ["share_l1"] + CH)
linha(s1, "B1 base")
s2 = mqo(ne, "y_ln", ["share_l1"] + CH + CTR)
linha(s2, "B2 + fracao t + areas + chuva t-1")
s3 = mqo(ne, "y_ln", ["share_l1"] + CH + CTR, tendencia=True)
linha(s3, "B3 = B2 + tendencia por municipio")
s4 = mqo(ne, "y_ln", ["share_f1"] + CH + CTR)
linha(s4, "B4 PLACEBO fracao t+1")
s4b = mqo(ne, "y_ln", ["share_l1", "share_f1"] + CH + CTR)
linha(s4b, "B4b juntos: t-1", 0)
linha(s4b, "B4b juntos: t+1 (placebo)", 1)
s5 = mqo(ne, "y_ln", ["share_l1", "share_l1_x_chz", "chuva_z"] + CH + CTR)
linha(s5, "B5 interacao com chuva: principal", 0)
linha(s5, "B5 interacao: muda por +1 dp de chuva", 1)
s5p = mqo(ne, "y_ln", ["share_f1", "share_f1_x_chz", "chuva_z"] + CH + CTR)
linha(s5p, "B5p PLACEBO da interacao: fracao t+1 x chuva", 1)
s5c = mqo(ne, "y_ln", ["share_l1", "share_l1_x_chz", "chuva_z", "sharebar_x_chz"] + CH + CTR)
linha(s5c, "B5c interacao t-1 x chuva, com composicao media x chuva", 1)
s5cp = mqo(ne, "y_ln", ["share_f1", "share_f1_x_chz", "chuva_z", "sharebar_x_chz"] + CH + CTR)
linha(s5cp, "B5cp PLACEBO de B5c: fracao t+1 x chuva", 1)
s5d = mqo(ne[ne.uf != "CE"], "y_ln", ["share_l1", "share_l1_x_chz", "chuva_z", "sharebar_x_chz"] + CH + CTR)
linha(s5d, "B5d = B5c sem o Ceara (replica fora do CE?)", 1)
contraste(s4b, "B4c CORRIGIDO PELO PLACEBO: coef(t-1) - coef(t+1)")
s4t = mqo(ne, "y_ln", ["share_l1", "share_f1"] + CH + CTR, tendencia=True)
contraste(s4t, "B4d corrigido pelo placebo, com tendencia por municipio")
for flag, rot in [(True, "semiarido 2022"), (False, "fora do semiarido")]:
    sub = ne[ne.semiarido == flag]
    rr = mqo(sub, "y_ln", ["share_l1"] + CH + CTR)
    linha(rr, f"B6 B2 so {rot}")
    rp = mqo(sub, "y_ln", ["share_f1"] + CH + CTR)
    linha(rp, f"B6 placebo t+1, so {rot}")
    contraste(mqo(sub, "y_ln", ["share_l1", "share_f1"] + CH + CTR), f"B6c corrigido pelo placebo, so {rot}")
s7 = mqo(ne, "y_razao", ["share_l1"] + CH + CTR)
linha(s7, "B7 Y = razao com perdas totais", escala="nivel")
s7p = mqo(ne, "y_razao", ["share_f1"] + CH + CTR)
linha(s7p, "B7 placebo t+1, Y = razao", escala="nivel")
for uf in sorted(ne.uf.dropna().unique()):
    rr = mqo(ne[ne.uf == uf], "y_ln", ["share_l1"] + CH + CTR)
    rp = mqo(ne[ne.uf == uf], "y_ln", ["share_f1"] + CH + CTR)
    b_, s_ = rr["b"][0], rr["se_a"][0]
    bp, sp = rp["b"][0], rp["se_a"][0]
    print(f"  B8 {uf}: t-1 {100 * (np.exp(0.1 * b_) - 1):+6.2f}% (EP {100 * 0.1 * s_:.2f}) | placebo t+1"
          f" {100 * (np.exp(0.1 * bp) - 1):+6.2f}% (EP {100 * 0.1 * sp:.2f}) | n={rr['N']}")

# ============================================================================= BLOCO 4: o que a literatura preveria
cab("BLOCO 4: teto que a literatura permitiria ver no painel (+10 p.p. de leguminosa em t-1, toda seguida de milho)")
lit = {
    "Zhao 2022 p.2, leguminosa antecessora (global)": (20.4, 17.7, 23.1),
    "Zhao 2022 p.5, milho apos leguminosa": (28.9, 25.5, 32.2),
    "Zhao 2022 p.5, feijao comum como antecessor": (14.5, 9.5, 19.5),
    "Mudare 2025 p.2, leguminosa antecessora": (23.0, 19.0, 28.0),
}
for k_, (m_, lo, hi) in lit.items():
    f = lambda e: 100 * (np.exp(0.1 * np.log(1 + e / 100)) - 1)  # noqa: E731
    print(f"  {k_:<50s} efeito no talhao {m_:+.1f}% -> no municipio {f(m_):+.2f}% [{f(lo):+.2f}, {f(hi):+.2f}]")
print(f"  MDE80 do desenho A2 (CE): {100 * 0.1 * 2.8 * r2['se_a'][0]:.1f}% ; B2 (NE): {100 * 0.1 * 2.8 * s2['se_a'][0]:.1f}%")
print("  Leitura: se o teto da literatura e menor que o MDE, o painel nao tem poder para ver a rotacao, mesmo que ela exista.")
