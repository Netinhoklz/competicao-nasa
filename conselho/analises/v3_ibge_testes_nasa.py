"""v3 - Analista IBGE/Nordeste: testes de ligacao entre as bases IBGE do Nordeste e os dados NASA.

  lspa       LSPA (previsao oficial no ano, por UF) x IMERG: a chuva do satelite ate o mes M antecipa a revisao que a
             LSPA ainda vai fazer ate o PAM final? (portoes 19/mar e 30/abr do M3)
  semiarido  Semiarido oficial 2022 x IMERG (chuva media anual) e SMAP L4 (dias de zona de raiz seca)
  ppm        PPM: rebanho 2011 -> 2016/2017 x deficit de chuva IMERG 2012-2016 (integracao lavoura-pecuaria)
  rotacao    Censo 2017 (% com rotacao) x perda de milho/feijao 2012-2016 (PAM) x anomalia IMERG; e PAM como
             proxy da pratica atual (diversidade de lavouras x rotacao declarada)
  arbitro    PAM NE x IMERG e SMAP: correlacao anual por UF (o IBGE como arbitro nos 9 estados)
Uso: python -I v3_ibge_testes_nasa.py [teste ...]
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 200)
IB = DADOS / "ibge_nordeste"
UF_SIG = {21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA"}
REF = pd.read_parquet(DERIV / "ibge_ne_municipios_referencia.parquet")


def imerg_mun():
    im = pd.read_parquet(DERIV / "ibge_ne_mun_imerg_mensal.parquet")
    im["ano"] = im.data.dt.year
    im["mes"] = im.data.dt.month
    return im


def auc(y, s):
    y, s = np.asarray(y, bool), np.asarray(s, float)
    ok = ~np.isnan(s)
    y, s = y[ok], s[ok]
    return stats.mannwhitneyu(s[y], s[~y]).statistic / (y.sum() * (~y).sum())


def pcorr(df, x, y, ctrl):
    """Correlacao parcial de Spearman de x e y controlando ctrl (residuos de regressao linear nos postos)."""
    d = df[[x, y] + ctrl].dropna()
    R = d.rank()
    Z = np.column_stack([np.ones(len(R))] + [R[c] for c in ctrl])
    rx = R[x] - Z @ np.linalg.lstsq(Z, R[x], rcond=None)[0]
    ry = R[y] - Z @ np.linalg.lstsq(Z, R[y], rcond=None)[0]
    r, p = stats.pearsonr(rx, ry)
    return r, p, len(d)


# ------------------------------------------------------------------ LSPA
def lspa():
    print("\n=== TESTE LSPA x IMERG: a chuva do satelite antecipa a revisao da previsao oficial? ===")
    l = pd.read_parquet(DERIV / "ibge_ne_lspa_uf_mensal.parquet")
    l = l[(l.variavel == "producao") & (l.uf != "NE")]
    l["cultura"] = np.where(l.produto.str.startswith("Milho"), "milho",
                            np.where(l.produto.str.startswith("Feijão"), "feijao", None))
    l = l[l.cultura.notna()]
    l["ano"], l["mes"] = l.data.dt.year, l.data.dt.month
    est = l.groupby(["uf", "cultura", "ano", "mes"]).valor.sum(min_count=1).reset_index(name="lspa_t")
    pam = pd.read_parquet(DADOS / "ibge_pam" / "pam_ne_estados.parquet")
    pam = pam[(pam.variavel == "Quantidade produzida") & pam.produto.isin(["Milho (em grão)", "Feijão (em grão)"])]
    pam = pam.assign(uf=pam.cod_local.astype(int).map(UF_SIG),
                     cultura=pam.produto.map({"Milho (em grão)": "milho", "Feijão (em grão)": "feijao"}))
    pam = pam[["uf", "cultura", "ano", "valor"]].rename(columns={"valor": "pam_t"})
    # chuva IMERG acumulada jan..M por UF (media dos municipios ponderada pela area), % da normal 1998-2025
    im = imerg_mun().merge(REF[["cod_mun", "uf", "area_km2"]], on="cod_mun")
    im["pw"] = im.precip_mm * im.area_km2
    uf_m = im.groupby(["uf", "ano", "mes"]).agg(pw=("pw", "sum"), a=("area_km2", "sum")).reset_index()
    uf_m["p"] = uf_m.pw / uf_m.a
    uf_m = uf_m[uf_m.ano <= 2025]
    linhas = []
    for M in (1, 2, 3, 4, 5, 6):
        acc = uf_m[uf_m.mes <= M].groupby(["uf", "ano"]).p.sum().rename("p_acum").reset_index()
        acc["normal"] = acc.groupby("uf").p_acum.transform(lambda s: (s.sum() - s) / (len(s) - 1))  # sem o proprio ano
        acc["pct_normal"] = 100 * acc.p_acum / acc.normal
        e = est[est.mes == M].merge(pam, on=["uf", "cultura", "ano"]).merge(acc, on=["uf", "ano"])
        e = e[(e.ano >= 2007) & (e.lspa_t > 0) & (e.pam_t > 0)]
        e["revisao_log"] = np.log(e.pam_t / e.lspa_t)
        e["M"] = M
        linhas.append(e)
    E = pd.concat(linhas)
    E.to_parquet(IB / "teste_lspa_imerg.parquet")
    print("revisao_log = ln(PAM final / estimativa LSPA no mes M); >0 = a LSPA subestimou; <0 = superestimou")
    print("chuva = IMERG jan..M do ano, % da normal (sem o proprio ano), media da UF")
    for cult in ("milho", "feijao"):
        print(f"\n-- {cult}: UF x ano 2007-2025, 9 UFs")
        for M in (2, 3, 4, 5, 6):
            q = E[(E.cultura == cult) & (E.M == M)]
            r, p = stats.spearmanr(q.pct_normal, q.revisao_log)
            # dentro da UF (tira a media da UF): sobra so a variacao entre anos
            qd = q.assign(rv=q.revisao_log - q.groupby("uf").revisao_log.transform("mean"),
                          pn=q.pct_normal - q.groupby("uf").pct_normal.transform("mean"))
            rd, pd_ = stats.spearmanr(qd.pn, qd.rv)
            erro = np.median(np.abs(q.revisao_log))
            sup = (q.revisao_log < np.log(0.5)).mean()
            print(f"  M={M}: n={len(q)}  |ln erro| mediano LSPA={erro:.2f}  LSPA >=2x o final em {100*sup:.0f}%  "
                  f"Spearman(chuva, revisao)={r:+.2f} (p={p:.1g})  dentro da UF={rd:+.2f} (p={pd_:.1g})")
        # o caso de 2012 no Ceara
    # SMAP L4 (2016-2025): zona de raiz media jan..M da UF, anomalia contra os outros anos; pareado com IMERG
    sm = pd.read_parquet(DERIV / "ibge_ne_mun_smap_mensal.parquet").merge(REF[["cod_mun", "uf", "area_km2"]],
                                                                         on="cod_mun")
    sm["ano"], sm["mes"] = sm.data.dt.year, sm.data.dt.month
    sm["w"] = sm.sm_rootzone * sm.area_km2
    sm = sm.dropna(subset=["sm_rootzone"])
    su = sm.groupby(["uf", "ano", "mes"]).agg(w=("w", "sum"), a=("area_km2", "sum")).reset_index()
    su["rz"] = su.w / su.a
    print("\n-- pareado 2016-2025 (SMAP L4 existe): Spearman dentro da UF com a revisao")
    for cult in ("milho", "feijao"):
        for M in (3, 4, 5):
            ac = su[(su.mes <= M) & su.ano.between(2016, 2025)].groupby(["uf", "ano"]).rz.mean().rename("rz").reset_index()
            ac["rz_anom"] = ac.rz - ac.groupby("uf").rz.transform(lambda s: (s.sum() - s) / (len(s) - 1))
            q = E[(E.cultura == cult) & (E.M == M)].merge(ac, on=["uf", "ano"])
            dm = lambda c: q[c] - q.groupby("uf")[c].transform("mean")
            ri = stats.spearmanr(dm("pct_normal"), dm("revisao_log"))[0]
            rs = stats.spearmanr(dm("rz_anom"), dm("revisao_log"))[0]
            print(f"  {cult} M={M}: n={len(q)}  IMERG {ri:+.2f}  SMAP zona de raiz {rs:+.2f}")
    c = E[(E.uf == "CE") & (E.ano.isin([2012, 2016])) & (E.cultura == "milho")].sort_values(["ano", "M"])
    print("\nCeara, milho (1a+2a safra LSPA; PAM final):")
    print(c[["ano", "M", "lspa_t", "pam_t", "pct_normal"]].round(0).to_string(index=False))
    # regra simples: se chuva jan..M < 75% da normal, cortar a estimativa LSPA pela metade -- melhora o erro?
    for cult in ("milho", "feijao"):
        for M in (3, 4):
            q = E[(E.cultura == cult) & (E.M == M)].copy()
            seco = q.pct_normal < 75
            # fator de corte aprendido fora do ano (deixa um ano de fora)
            fat = []
            for i, row in q.iterrows():
                o = q[(q.ano != row.ano) & (q.pct_normal < 75)]
                fat.append(np.exp(o.revisao_log.median()) if len(o) else 1.0)
            q["aj"] = np.where(seco, q.lspa_t * np.array(fat), q.lspa_t)
            e0 = np.abs(np.log(q.pam_t / q.lspa_t))[seco]
            e1 = np.abs(np.log(q.pam_t / q.aj))[seco]
            print(f"  {cult} M={M}: anos-UF secos (<75% IMERG) n={seco.sum()}: |ln erro| mediano LSPA {e0.median():.2f}"
                  f" -> com corte IMERG (fator fora do ano) {e1.median():.2f}; melhora em {100*(e1<e0).mean():.0f}% dos casos")


# ------------------------------------------------------------------ Semiarido
def semiarido():
    print("\n=== TESTE Semiarido oficial (SUDENE 2022, lista do IBGE) x IMERG e SMAP L4 ===")
    im = imerg_mun()
    anual = im[(im.ano >= 1998) & (im.ano <= 2025)].groupby(["cod_mun", "ano"]).precip_mm.sum().groupby("cod_mun").mean()
    dd = pd.read_parquet(IB / "smap_l4_rootzone_diario_municipio.parquet")
    dd = dd[(dd.index >= "2015-04-01") & (dd.index < "2026-04-01")]  # 11 anos completos abr-mar
    frac10 = (dd < 0.10).where(dd.notna()).mean()
    frac15 = (dd < 0.15).where(dd.notna()).mean()
    med = dd.median()
    T = REF.set_index("cod_mun").assign(p_anual=anual, smap_frac_lt010=frac10, smap_frac_lt015=frac15,
                                        smap_mediana=med)
    T.to_parquet(IB / "teste_semiarido_nasa.parquet")
    y = T.semiarido_2022.values
    print(f"municipios NE: {len(T)}; no Semiarido 2022: {y.sum()}")
    print(f"municipios sem SMAP (celula mascarada): {int(T.smap_mediana.isna().sum())}")
    for c, sinal in (("p_anual", -1), ("smap_mediana", -1), ("smap_frac_lt015", 1), ("smap_frac_lt010", 1)):
        s = sinal * T[c].fillna(T[c].median()).values
        a = auc(y, sinal * T[c].values)
        # melhor limiar (Youden) e acuracia
        ths = np.unique(np.quantile(s, np.linspace(0.02, 0.98, 97)))
        best = max(ths, key=lambda t: ((s >= t) & y).sum() / y.sum() + ((s < t) & ~y).sum() / (~y).sum())
        acc = ((s >= best) == y).mean()
        print(f"  {c:16s} AUC={a:.3f}  limiar Youden={sinal*best:.3f}  acuracia={100*acc:.1f}%  "
              f"mediana semiarido={T[c][y].median():.3f} x fora={T[c][~y].median():.3f}")
    # combinacao simples: chuva + SMAP (logistica nos postos, validacao cruzada por UF)
    from sklearn.linear_model import LogisticRegression
    X = T[["p_anual", "smap_frac_lt015"]].rank(pct=True).fillna(0.5).values
    ps = np.zeros(len(T))
    for uf in T.uf.unique():
        tr = (T.uf != uf).values
        m = LogisticRegression().fit(X[tr], y[tr])
        ps[~tr] = m.predict_proba(X[~tr])[:, 1]
    print(f"  IMERG + SMAP (logistica, deixa uma UF de fora): AUC={auc(y, ps):.3f}")
    s = -T.p_anual.values
    for lim in (700, 800, 900):
        pred = T.p_anual.values <= lim
        print(f"  regra IMERG chuva media <= {lim} mm: acerto {100*(pred == y).mean():.1f}%  "
              f"(semiarido pego {100*pred[y].mean():.0f}%, fora marcado {100*pred[~y].mean():.0f}%)")
    print("  por UF (% do Semiarido, chuva IMERG mediana dentro/fora):")
    g = T.groupby("uf").agg(n=("municipio", "size"), semi=("semiarido_2022", "mean"))
    g["p_semi"] = T[T.semiarido_2022].groupby("uf").p_anual.median()
    g["p_fora"] = T[~T.semiarido_2022].groupby("uf").p_anual.median()
    print(g.round(2).to_string())


# ------------------------------------------------------------------ PPM
def ppm():
    print("\n=== TESTE PPM (rebanhos) x IMERG: o rebanho caiu onde a chuva faltou em 2012-2016? ===")
    p = pd.read_parquet(DERIV / "ibge_ne_ppm_mun_anual.parquet")
    im = imerg_mun()
    an = im[(im.ano >= 1998) & (im.ano <= 2025)].groupby(["cod_mun", "ano"]).precip_mm.sum().unstack()
    base = an.loc[:, 1998:2011].mean(axis=1)
    def_ = 100 * an.loc[:, 2012:2016].mean(axis=1) / base
    w = p.pivot_table(index="cod_mun", columns="ano", values=["bovino", "caprino", "ovino"])
    T = pd.DataFrame({"chuva_2012_16_pct": def_})
    for r in ("bovino", "caprino", "ovino"):
        a0, a1 = w[(r, 2011)], w[(r, 2016)]
        T[f"{r}_2016_2011"] = np.where((a0 > 50), a1 / a0, np.nan)
    T["ruminantes_2016_2011"] = ((w[("bovino", 2016)] + w[("caprino", 2016)] + w[("ovino", 2016)]) /
                                 (w[("bovino", 2011)] + w[("caprino", 2011)] + w[("ovino", 2011)]))
    T = T.join(REF.set_index("cod_mun")[["uf", "semiarido_2022"]])
    T.to_parquet(IB / "teste_ppm_imerg.parquet")
    tot = p.groupby("ano")[["bovino", "caprino", "ovino"]].sum()
    print("NE total (milhoes de cabecas):")
    print((tot.loc[[2011, 2012, 2013, 2014, 2015, 2016, 2017, 2020, 2025]] / 1e6).round(2).to_string())
    for c in ("bovino_2016_2011", "caprino_2016_2011", "ovino_2016_2011", "ruminantes_2016_2011"):
        q = T[[c, "chuva_2012_16_pct"]].dropna()
        r, pv = stats.spearmanr(q.chuva_2012_16_pct, q[c])
        qs = T[T.semiarido_2022][[c, "chuva_2012_16_pct"]].dropna()
        rs, ps = stats.spearmanr(qs.chuva_2012_16_pct, qs[c])
        print(f"  {c}: mediana {q[c].median():.2f}; Spearman com chuva IMERG 2012-16 (% de 1998-2011) = {r:+.2f} "
              f"(n={len(q)}, p={pv:.1g}); so semiarido {rs:+.2f} (n={len(qs)})")
    # painel anual: variacao do log do rebanho no ano t x anomalia de chuva do ano t (efeito fixo do municipio)
    lg = np.log(w["bovino"].where(w["bovino"] > 0))
    dl = lg.diff(axis=1).loc[:, 1999:2025].stack().rename("dlog")
    an_pct = (an.div(an.mean(axis=1), axis=0)).stack().rename("chuva_rel")
    P = pd.concat([dl, an_pct, an_pct.groupby(level=0).shift(1).rename("chuva_rel_ant")], axis=1).dropna()
    P = P - P.groupby(level=0).transform("mean")
    for c in ("chuva_rel", "chuva_rel_ant"):
        r, pv = stats.spearmanr(P[c], P.dlog)
        print(f"  painel bovino 1999-2025 (efeito fixo do municipio): Spearman(dlog rebanho t, {c}) = {r:+.2f} n={len(P)}")


# ------------------------------------------------------------------ Rotacao (Censo) x seca
def janela_chuvosa(im):
    """4 meses consecutivos mais chuvosos da climatologia 1998-2025 de cada municipio (janela circular)."""
    clim = im[(im.ano >= 1998) & (im.ano <= 2025)].groupby(["cod_mun", "mes"]).precip_mm.mean().unstack()
    v = clim.values
    soma = np.stack([v[:, [(m + k) % 12 for k in range(4)]].sum(1) for m in range(12)], 1)
    ini = soma.argmax(1) + 1  # mes inicial (1-12)
    return pd.Series(ini, index=clim.index, name="mes_ini")


def chuva_estacao(im):
    """Chuva da estacao (4 meses) atribuida ao ano de colheita: a estacao que TERMINA no ano t."""
    ini = janela_chuvosa(im)
    x = im.merge(ini.reset_index(), on="cod_mun")
    rel = (x.mes - x.mes_ini) % 12
    x = x[rel < 4].copy()
    fim = x.mes_ini + 3
    # ano da colheita = ano do ultimo mes da janela
    x["ano_col"] = np.where((x.mes_ini + 3 > 12) & (x.mes >= x.mes_ini), x.ano + 1, x.ano)
    s = x.groupby(["cod_mun", "ano_col"]).agg(p=("precip_mm", "sum"), n=("precip_mm", "count")).reset_index()
    s = s[s.n == 4].rename(columns={"ano_col": "ano"})
    return s[["cod_mun", "ano", "p"]], ini


def rotacao():
    print("\n=== TESTE Censo 2017 (rotacao) x perda na seca 2012-2016 (PAM) x anomalia de chuva IMERG ===")
    c = pd.read_parquet(DERIV / "ibge_ne_censo2017_praticas_mun.parquet")
    pam = pd.read_parquet(DERIV / "ibge_ne_pam_mun_anual.parquet")
    im = imerg_mun()
    est, ini = chuva_estacao(im)
    est = est.pivot(index="cod_mun", columns="ano", values="p")
    chuva = 100 * est.loc[:, 2012:2016].mean(axis=1) / est.loc[:, 1999:2011].mean(axis=1)
    print("janela chuvosa (mes inicial) mais comum por UF:",
          ini.groupby(ini.index.str[:2].astype(int).map(UF_SIG)).agg(lambda s: s.mode()[0]).to_dict())
    linhas = {}
    for cult in ("Milho", "Feijão"):
        q = pam[pam.produto == cult].copy()
        q["y"] = 1000 * q.producao_t / q.area_plantada_ha.where(q.area_plantada_ha > 0)  # kg por ha PLANTADO
        y = q.pivot(index="cod_mun", columns="ano", values="y")
        a = q.pivot(index="cod_mun", columns="ano", values="area_plantada_ha")
        ok = a.loc[:, 2003:2011].median(axis=1) >= 200  # municipio com lavoura de verdade
        base = y.loc[:, 2003:2011].median(axis=1)
        linhas[f"razao_{cult}"] = (y.loc[:, 2012:2016].mean(axis=1) / base).where(ok & (base > 0))
    T = pd.DataFrame(linhas).join(chuva.rename("chuva_2012_16_pct"))
    T = T.join(c.set_index("cod_mun")[["pct_rotacao", "pct_rotacao_lavtemp", "pct_pousio", "pct_nenhuma_pratica",
                                       "pct_irrigacao", "pct_orientacao_tecnica", "pct_familiar",
                                       "pct_cultivo_minimo", "pct_cisterna"]])
    T = T.join(REF.set_index("cod_mun")[["uf", "semiarido_2022"]])
    T["uf_cod"] = T.uf.astype("category").cat.codes
    T.to_parquet(IB / "teste_rotacao_seca.parquet")
    for cult in ("Milho", "Feijão"):
        col = f"razao_{cult}"
        q = T.dropna(subset=[col, "chuva_2012_16_pct", "pct_rotacao"])
        r0, p0 = stats.spearmanr(q.chuva_2012_16_pct, q[col])
        r1, p1 = stats.spearmanr(q.pct_rotacao, q[col])
        print(f"\n-- {cult}: n={len(q)} municipios; razao mediana (rend. 2012-16 / mediana 2003-11) = {q[col].median():.2f}")
        print(f"  Spearman(chuva IMERG 2012-16 %, razao) = {r0:+.2f} (p={p0:.1g})")
        print(f"  Spearman(% rotacao, razao) bruto = {r1:+.2f} (p={p1:.1g})")
        for ctrl in (["chuva_2012_16_pct"], ["chuva_2012_16_pct", "pct_irrigacao", "pct_orientacao_tecnica",
                                              "pct_familiar"],
                     ["chuva_2012_16_pct", "pct_irrigacao", "pct_orientacao_tecnica", "pct_familiar", "uf_cod"]):
            r, p, n = pcorr(T, "pct_rotacao", col, ctrl)
            print(f"  parcial(% rotacao, razao | {'+'.join(ctrl)}) = {r:+.2f} (p={p:.1g}, n={n})")
        # tercis de rotacao dentro de tercis de chuva
        q = q.assign(tc=pd.qcut(q.chuva_2012_16_pct, 3, labels=["seco", "medio", "menos seco"]),
                     tr=pd.qcut(q.pct_rotacao.rank(method="first"), 3, labels=["rot baixa", "rot media", "rot alta"]))
        print("  razao mediana por tercil de chuva (linhas) x tercil de rotacao (colunas):")
        print(q.pivot_table(index="tc", columns="tr", values=col, aggfunc="median", observed=True).round(2).to_string())
    # PAM como proxy da pratica atual: diversidade de lavouras temporarias x rotacao declarada no Censo
    print("\n-- PAM como proxy da pratica atual (M5): diversidade das lavouras x rotacao declarada (Censo 2017)")
    ce = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
    ce = ce[(ce.tipo == "temporaria") & ce.ano.between(2015, 2017)].groupby(["cod_local", "produto"]).area_plantada_ha.mean()
    sh = ce.groupby(level=0).apply(lambda s: float(-(s[s > 0] / s.sum() * np.log(s[s > 0] / s.sum())).sum()))
    nprod = ce.groupby(level=0).apply(lambda s: int((s / s.sum() >= 0.05).sum()))
    D = pd.DataFrame({"shannon": sh, "n_culturas_5pct": nprod}).join(c.set_index("cod_mun")[["pct_rotacao",
                                                                                           "pct_rotacao_lavtemp"]])
    for x in ("shannon", "n_culturas_5pct"):
        r, p = stats.spearmanr(D[x], D.pct_rotacao, nan_policy="omit")
        r2, p2 = stats.spearmanr(D[x], D.pct_rotacao_lavtemp, nan_policy="omit")
        print(f"  Ceara (184 mun., PAM completa): Spearman({x}, % rotacao) = {r:+.2f} (p={p:.1g}); "
              f"com % rotacao nas lavouras temporarias = {r2:+.2f} (p={p2:.1g})")
    w = pam[(pam.tipo == "temporaria") & pam.ano.between(2015, 2017)].groupby(["cod_mun", "produto"]).area_plantada_ha.mean()
    sh = w.groupby(level=0).apply(lambda s: float(-(s[s > 0] / s.sum() * np.log(s[s > 0] / s.sum())).sum())
                                  if s.sum() > 0 else np.nan)
    D = pd.DataFrame({"shannon5": sh}).join(c.set_index("cod_mun")[["pct_rotacao"]])
    r, p = stats.spearmanr(D.shannon5, D.pct_rotacao, nan_policy="omit")
    print(f"  Nordeste (5 lavouras: milho, feijao, mandioca, sorgo, algodao): Spearman(Shannon, % rotacao) = {r:+.2f} "
          f"(p={p:.1g}, n={D.dropna().shape[0]})")


# ------------------------------------------------------------------ Arbitro: PAM NE x IMERG x SMAP
def arbitro():
    print("\n=== TESTE PAM NE (arbitro) x IMERG (1999-2025) e SMAP L4 (2016-2025), por UF ===")
    pam = pd.read_parquet(DERIV / "ibge_ne_pam_mun_anual.parquet")
    im = imerg_mun()
    est, ini = chuva_estacao(im)
    est["chuva_rel"] = est.p / est.groupby("cod_mun").p.transform("mean")
    sm = pd.read_parquet(DERIV / "ibge_ne_mun_smap_mensal.parquet")
    sm["ano"], sm["mes"] = sm.data.dt.year, sm.data.dt.month
    sm = sm.merge(ini.reset_index(), on="cod_mun")
    rel = (sm.mes - sm.mes_ini) % 12
    sm = sm[rel < 4].copy()
    sm["ano_col"] = np.where((sm.mes_ini + 3 > 12) & (sm.mes >= sm.mes_ini), sm.ano + 1, sm.ano)
    sme = sm.groupby(["cod_mun", "ano_col"]).agg(rz=("sm_rootzone", "mean"), n=("sm_rootzone", "count")).reset_index()
    sme = sme[sme.n == 4].rename(columns={"ano_col": "ano"})
    sme["rz_rel"] = sme.rz - sme.groupby("cod_mun").rz.transform("mean")
    res = []
    for cult in ("Milho", "Feijão", "Mandioca"):
        q = pam[pam.produto == cult].copy()
        q["y"] = 1000 * q.producao_t / q.area_plantada_ha.where(q.area_plantada_ha >= 100)
        q["y_rel"] = q.y / q.groupby("cod_mun").y.transform("median")
        q = q.merge(est[["cod_mun", "ano", "chuva_rel"]], on=["cod_mun", "ano"]).merge(
            sme[["cod_mun", "ano", "rz_rel"]], on=["cod_mun", "ano"], how="left")
        q = q.dropna(subset=["y_rel", "chuva_rel"])
        q = q[q.ano.between(1999, 2025)]
        for uf, g in q.groupby("uf"):
            r_im, _ = stats.spearmanr(g.chuva_rel, g.y_rel)
            g2 = g[g.ano >= 2016].dropna(subset=["rz_rel"])
            r_im2 = stats.spearmanr(g2.chuva_rel, g2.y_rel)[0] if len(g2) > 30 else np.nan
            r_sm = stats.spearmanr(g2.rz_rel, g2.y_rel)[0] if len(g2) > 30 else np.nan
            res.append({"cultura": cult, "uf": uf, "n_mun_ano": len(g), "rho_imerg_1999_2025": r_im,
                        "n_2016_2025": len(g2), "rho_imerg_2016_25": r_im2, "rho_smap_2016_25": r_sm})
    R = pd.DataFrame(res)
    R.to_parquet(IB / "teste_arbitro_pam_imerg_smap.parquet")
    print("rho = Spearman entre o rendimento relativo (kg/ha plantado / mediana do municipio) e a chuva da estacao "
          "(IMERG, relativa) ou a zona de raiz (SMAP L4, anomalia) na janela de 4 meses mais chuvosa do municipio")
    print(R.round(2).to_string(index=False))
    print("\nmedia por cultura:")
    print(R.groupby("cultura")[["rho_imerg_1999_2025", "rho_imerg_2016_25", "rho_smap_2016_25"]].mean().round(2).to_string())


if __name__ == "__main__":
    for t in sys.argv[1:] or ["lspa", "semiarido", "ppm", "rotacao", "arbitro"]:
        globals()[t]()
