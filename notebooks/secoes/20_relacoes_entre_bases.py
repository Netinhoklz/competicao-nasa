# %% [markdown]
# ## 20. Relações entre bases — conectividade e novas ligações
#
# Aqui as bases deixam de ser estudadas isoladamente. Todas as frentes salvaram séries **mensais médias do Ceará** em
# `dados/derivados/*_ce_mensal.parquet`, no mesmo formato (data, variavel, valor). Isso permite cruzar tudo num único
# painel mensal.
#
# **Perguntas que ligam as bases** (as do desafio e outras novas):
# 1. **Chuva:** as fontes concordam (POWER × IMERG × ERA5)? Qual usar no produto?
# 2. **Teleconexão → decisão de plantio:** o Pacífico (ONI) e o Atlântico (TNA−TSA) antecipam a quadra chuvosa?
# 3. **A vegetação responde à chuva com quanto atraso?** (NDVI × chuva)
# 4. **Água armazenada (GRACE) × chuva × umidade do solo:** memória hídrica de anos.
# 5. **Calor × vegetação:** LST/Tmax × NDVI (estresse).
# 6. **Fogo × secura × vegetação:** quando e por que queima.
# 7. **Clima → produção real** (IBGE PAM): quanto a seca derruba o rendimento de cada cultura.
# 8. **Mercado:** preço × produção, e a volatilidade como risco da rotação.

# %%
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from scipy import stats
from comum import DADOS, DERIV

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})

partes = []
for f in sorted(DERIV.glob("*_ce_mensal.parquet")) + [DERIV / "indices_clima_mensal.parquet"]:
    if not f.exists():
        continue
    d = pd.read_parquet(f)
    if not {"data", "variavel", "valor"} <= set(d.columns):
        continue
    fonte = f.stem.replace("_ce_mensal", "").replace("_mensal", "")
    d = d.assign(col=fonte + ":" + d["variavel"].astype(str))
    d["data"] = pd.to_datetime(d["data"]).dt.to_period("M").dt.to_timestamp()
    partes.append(d[["data", "col", "valor"]])
painel = pd.concat(partes).pivot_table(index="data", columns="col", values="valor", aggfunc="mean").sort_index()
print(f"Painel mensal: {painel.shape[0]} meses × {painel.shape[1]} variáveis, {painel.index.min():%Y-%m} a {painel.index.max():%Y-%m}")
cobertura = painel.notna().sum().rename("meses_com_dado").to_frame()
cobertura["início"] = painel.apply(lambda s: s.first_valid_index())
cobertura["fim"] = painel.apply(lambda s: s.last_valid_index())
cobertura


# %%
def achar(*palavras, excluir=()):
    """Primeira coluna do painel cujo nome contém todas as palavras (sem diferenciar maiúsculas)."""
    for c in painel.columns:
        n = c.lower()
        if all(p.lower() in n for p in palavras) and not any(e.lower() in n for e in excluir):
            return c
    return None


def anual_fmam(s):
    """Total de fev–mai por ano (quadra chuvosa)."""
    s = s.dropna()
    q = s[s.index.month.isin([2, 3, 4, 5])]
    cont = q.groupby(q.index.year).count()
    return q.groupby(q.index.year).sum()[cont == 4]


CH = {k: v for k, v in {
    "POWER (MERRA-2 corrigido)": achar("power", "prectotcorr"),
    "POWER IMERG": achar("power", "imerg"),
    "IMERG (GPM)": achar("imerg", "prec", excluir=("power",)) or achar("imerg", "chuva", excluir=("power",)),
    "ERA5": achar("era5", "prec") or achar("era5", "chuva") or achar("era5", ":tp"),
}.items() if v}
print("Séries de chuva encontradas:", CH)

# %% [markdown]
# ### 20.1 Chuva: as fontes concordam?
# A chuva mensal do Ceará é comparada entre as fontes no período comum, com correlação, viés relativo e RMSE.
# Para o produto, a fonte "de referência" deve ser global, longa e atualizada. A fonte observacional por satélite
# (IMERG) é a referência natural, e os modelos (MERRA-2/ERA5) preenchem onde falta.

# %%
if len(CH) >= 2:
    dfc = pd.DataFrame({k: painel[v] for k, v in CH.items()})
    dfc = dfc.loc[:, dfc.notna().sum() >= 24]
    # unidades: converter mm/dia para mm/mês quando a média for pequena (< 15)
    for c in dfc:
        if dfc[c].mean() < 15:
            dfc[c] = dfc[c] * dfc.index.days_in_month
    ref = "IMERG (GPM)" if "IMERG (GPM)" in dfc else dfc.columns[0]
    linhas = []
    for c in dfc:
        if c == ref:
            continue
        par = dfc[[ref, c]].dropna()  # comparação par a par no período comum
        if len(par) < 24:
            continue
        r, _ = stats.pearsonr(par[ref], par[c])
        linhas.append({"fonte": c, "vs": ref, "r": round(r, 3), "viés %": round((par[c].mean() / par[ref].mean() - 1) * 100, 1),
                       "RMSE mm/mês": round(float(np.sqrt(((par[c] - par[ref]) ** 2).mean())), 1), "meses": len(par),
                       "período": f"{par.index.min():%Y-%m}–{par.index.max():%Y-%m}"})
    fig, ax = plt.subplots(1, 2, figsize=(13, 4))
    dfc.plot(ax=ax[0], lw=0.8)
    ax[0].set_title("Chuva mensal média no Ceará (mm/mês)")
    clim = dfc.groupby(dfc.index.month).mean()
    clim.plot(ax=ax[1], marker="o")
    ax[1].set_title("Climatologia mensal por fonte")
    ax[1].set_xlabel("mês")
    plt.tight_layout()
    plt.show()
    display(pd.DataFrame(linhas))
else:
    print("Menos de duas séries de chuva disponíveis ainda.")

# %% [markdown]
# ### 20.2 Teleconexões → previsão da quadra chuvosa (ligação nova)
# - **Física:** o Ceará chove quando a **Zona de Convergência Intertropical** desce para o sul em fev–mai. Isso é
#   favorecido por **La Niña** (ONI < 0) e por **Atlântico Sul mais quente que o Norte** (TNA−TSA < 0).
# - **Teste:** o índice médio de **out–jan** (antes do plantio) correlaciona com o total de fev–mai?
# - **Modelo:** uma regressão logística de tercis, avaliada deixando um ano de fora, mostra se há **habilidade
#   preditiva** além da climatologia.
#
# É o protótipo da ideia (5) da seção 30.

# %%
chuva_ref = CH.get("IMERG (GPM)") or CH.get("POWER (MERRA-2 corrigido)") or (list(CH.values())[0] if CH else None)
chuva_longa = CH.get("POWER (MERRA-2 corrigido)") or chuva_ref  # POWER tem 1981+
oni, tna, tsa = achar("indices", "oni"), achar("indices", "tna", excluir=("menos",)), achar("indices", "tsa", excluir=("menos",))
dip = achar("indices", "dipolo")
if chuva_longa and oni and dip:
    fmam = anual_fmam(painel[chuva_longa])
    if fmam.mean() < 60:  # mm/dia somado -> converter aproximando 30 dias
        fmam = fmam * 30
    def media_ondj(s):
        s = s.dropna()
        out = {}
        for ano in range(int(s.index.year.min()) + 1, int(s.index.year.max()) + 1):
            jan = pd.Timestamp(ano, 1, 1)
            janela = s[(s.index >= pd.Timestamp(ano - 1, 10, 1)) & (s.index <= jan)]
            if len(janela) == 4:
                out[ano] = janela.mean()
        return pd.Series(out)
    X = pd.DataFrame({"ONI_ondj": media_ondj(painel[oni]), "Dipolo_ondj": media_ondj(painel[dip]), "FMAM_mm": fmam}).dropna()
    print(f"{len(X)} anos ({X.index.min()}–{X.index.max()})")
    for c in ["ONI_ondj", "Dipolo_ondj"]:
        r, p = stats.pearsonr(X[c], X.FMAM_mm)
        rs, ps = stats.spearmanr(X[c], X.FMAM_mm)
        print(f"  {c:12s}  Pearson r={r:+.2f} (p={p:.3f})   Spearman ρ={rs:+.2f} (p={ps:.3f})")
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    for a, c in zip(ax, ["ONI_ondj", "Dipolo_ondj"]):
        a.scatter(X[c], X.FMAM_mm, c=X.index, cmap="viridis")
        for ano in [1983, 1993, 1998, 2012, 2016, 1985, 2009, 2024]:
            if ano in X.index:
                a.annotate(str(ano), (X.loc[ano, c], X.loc[ano, "FMAM_mm"]), fontsize=7)
        a.set_xlabel(c + " (média out–jan)")
        a.set_ylabel("chuva fev–mai (mm)")
    plt.suptitle("Índices oceânicos antes do plantio × quadra chuvosa no Ceará")
    plt.tight_layout()
    plt.show()

    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import LeaveOneOut
    q1, q2 = X.FMAM_mm.quantile([1 / 3, 2 / 3])
    y = np.where(X.FMAM_mm <= q1, 0, np.where(X.FMAM_mm >= q2, 2, 1))
    acertos, rps_m, rps_c = [], [], []
    for tr, te in LeaveOneOut().split(X):
        m = LogisticRegression(max_iter=1000).fit(X[["ONI_ondj", "Dipolo_ondj"]].iloc[tr], y[tr])
        p = m.predict_proba(X[["ONI_ondj", "Dipolo_ondj"]].iloc[te])[0]
        pc = np.full(3, 1 / 3)
        if len(m.classes_) == 3:
            acertos.append(int(np.argmax(p) == y[te][0]))
            o = np.eye(3)[y[te][0]]
            rps_m.append(np.sum((np.cumsum(p) - np.cumsum(o)) ** 2) / 2)
            rps_c.append(np.sum((np.cumsum(pc) - np.cumsum(o)) ** 2) / 2)
    rpss = 1 - np.mean(rps_m) / np.mean(rps_c)
    print(f"Acurácia de tercil (deixando 1 ano de fora): {np.mean(acertos):.0%}  (acaso = 33%)")
    print(f"RPSS vs climatologia: {rpss:+.2f}  (>0 = melhor que a climatologia)")
else:
    print("Faltam séries de chuva ou índices para este teste.")

# %% [markdown]
# ### 20.3 Correlação cruzada com defasagem: quem antecede quem
# Para cada par (chuva → NDVI, chuva → umidade do solo, chuva → GRACE, NDVI → fogo, LST → NDVI), calculamos a
# correlação das **anomalias mensais** (o ciclo sazonal é removido) com defasagens de 0 a 6 meses. O pico diz quanto
# tempo o sistema leva para responder.

# %%
def anomalia(s):
    s = s.dropna()
    return s - s.groupby(s.index.month).transform("mean")


pares = {
    "chuva → NDVI": (chuva_ref, achar("modis", "ndvi")),
    "chuva → umidade raiz (POWER)": (chuva_ref, achar("power", "gwetroot")),
    "chuva → GRACE TWS": (chuva_longa, achar("grace", "tws")),
    "umidade raiz → NDVI": (achar("power", "gwetroot"), achar("modis", "ndvi")),
    "NDVI → fogo (focos)": (achar("modis", "ndvi"), achar("viirs", "foco") or achar("firms") or achar("viirs")),
    "chuva → área queimada": (chuva_ref, achar("queim") or achar("burn") or achar("mcd64")),
    "chuva → focos VIIRS": (chuva_ref, achar("viirs", "foco")),
    "Tmax (ERA5) → NDVI": (achar("era5", "tmax"), achar("modis", "ndvi")),
    "LST → NDVI": (achar("modis", "lst"), achar("modis", "ndvi")),
}
res = {}
for nome, (a, b) in pares.items():
    if not (a and b):
        continue
    xa, xb = anomalia(painel[a]), anomalia(painel[b])
    res[nome] = {lag: xa.shift(lag).corr(xb) for lag in range(0, 7)}
if res:
    R = pd.DataFrame(res).T.dropna(how="all")
    fig, ax = plt.subplots(figsize=(10, 0.5 + 0.45 * len(R)))
    im = ax.imshow(R.values, cmap="RdBu_r", vmin=-0.8, vmax=0.8, aspect="auto")
    ax.set_yticks(range(len(R)))
    ax.set_yticklabels(R.index)
    ax.set_xticks(range(7))
    ax.set_xticklabels([f"{l} m" for l in range(7)])
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            ax.text(j, i, f"{R.values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    plt.colorbar(im, label="correlação das anomalias")
    ax.set_title("Correlação defasada (a causa antecede o efeito em L meses)")
    plt.show()
    R.assign(melhor_defasagem=R.abs().idxmax(axis=1), r_max=R.abs().max(axis=1).round(2))
else:
    print("Pares ainda indisponíveis.")

# %% [markdown]
# ### 20.4 Memória hídrica: GRACE × chuva acumulada
# O armazenamento total de água (GRACE) integra anos de chuva. Comparamos a anomalia do GRACE com a **anomalia
# acumulada da chuva em 12–36 meses**; a janela de melhor ajuste é a "memória" do sistema hídrico do Ceará.
# Para o produto, ela indica se o ano seguinte começa com reserva ou com déficit (açudes, poços, irrigação).

# %%
g = achar("grace", "tws")
if g and chuva_longa:
    an = anomalia(painel[chuva_longa])
    gr = painel[g].dropna()
    linhas = []
    for w in [3, 6, 12, 18, 24, 36, 48]:
        acc = an.rolling(w).sum()
        j = pd.concat([acc, gr], axis=1).dropna()
        linhas.append({"janela_meses": w, "r": round(j.iloc[:, 0].corr(j.iloc[:, 1]), 3), "n": len(j)})
    T = pd.DataFrame(linhas)
    melhor = int(T.loc[T.r.idxmax(), "janela_meses"])
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(gr.index, gr, label="GRACE TWS (cm)", color="tab:blue")
    ax2 = ax.twinx()
    acc = an.rolling(melhor).sum()
    ax2.plot(acc.index, acc, color="tab:orange", alpha=0.7, label=f"chuva acumulada {melhor} m (anomalia)")
    ax.axvspan(pd.Timestamp("2012-01-01"), pd.Timestamp("2017-12-31"), color="red", alpha=0.08, label="seca 2012–2017")
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")
    ax.set_title("Ceará: água total armazenada × chuva acumulada")
    plt.show()
    display(T)

# %% [markdown]
# ### 20.5 Clima → produção agrícola real (IBGE PAM)
# Rendimento anual das culturas no Ceará contra a chuva de fev–mai e o ONI. A **elasticidade** (variação % do
# rendimento por 100 mm de chuva) diz quais culturas são frágeis e quais toleram a seca. Esse é o insumo direto do
# "risco" de cada rotação.

# %%
pam_f = None
for cand in ["ibge_pam_ce_anual.parquet", "pam_ce_anual.parquet", "ibge_pam_anual.parquet"]:
    if (DERIV / cand).exists():
        pam_f = DERIV / cand
        break
if pam_f is None:
    cands = sorted(DERIV.glob("*pam*.parquet")) + sorted((DADOS / "ibge_pam").glob("*.parquet"))
    pam_f = cands[0] if cands else None
print("Arquivo PAM:", pam_f)
if pam_f is not None and chuva_longa:
    pam = pd.read_parquet(pam_f)
    pam["ano"] = pd.to_datetime(pam["data"]).dt.year
    if {"produto", "variavel", "valor"} <= set(pam.columns):
        area = pam[pam.variavel == "area_colhida_ha"].pivot_table(index="ano", columns="produto", values="valor")
        relevantes = area.loc[area.index >= 2000].mean().loc[lambda s: s > 5000].index  # culturas com > 5 mil ha
        rend = pam[pam.variavel == "rendimento_kg_ha"].pivot_table(index="ano", columns="produto", values="valor")
        rend = rend[[c for c in rend.columns if c in relevantes]]
        print("Culturas analisadas (área colhida média > 5 mil ha desde 2000):", list(rend.columns))
        fmam = anual_fmam(painel[chuva_longa])
        if fmam.mean() < 60:
            fmam = fmam * 30
        # culturas permanentes mudaram de unidade no IBGE em 2001 (ex.: banana de mil cachos para toneladas)
        permanentes = set(pam.loc[pam.tipo == "permanente", "produto"])
        linhas = []
        for c in rend.columns:
            s = rend[c]
            if c in permanentes:
                s = s[s.index >= 2001]
            j = pd.concat([s, fmam.rename("fmam")], axis=1).dropna()
            if len(j) < 12 or j[c].mean() <= 0:
                continue
            # rendimento sem tendência tecnológica: razão para a mediana móvel centrada de 7 anos, em %
            tend = j[c].rolling(7, center=True, min_periods=3).median()
            dev = (j[c] / tend - 1) * 100
            sl, ic, r, p, _ = stats.linregress(j.fmam, dev)
            linhas.append({"cultura": c, "anos": len(j), "r(chuva, desvio rend.)": round(r, 2), "p": round(p, 3),
                           "% rendimento por +100 mm": round(sl * 100, 1),
                           "pior ano": int(dev.idxmin()), "quebra no pior ano %": round(dev.min(), 1)})
        E = pd.DataFrame(linhas).sort_values("r(chuva, desvio rend.)", ascending=False)
        display(E)
    else:
        print("Colunas de ano/cultura/rendimento não identificadas; ver seção 13.")

# %% [markdown]
# ### 20.6 Mercado: preço × produção e volatilidade
# Para cada cultura candidata, volatilidade do preço ao produtor (FAOSTAT, Brasil) e do preço internacional
# (Banco Mundial). Na pontuação das rotações, volatilidade alta = risco de renda; cultura com mercado firme = renda
# suplementar.

# %%
mp = DERIV / "mercado_precos_mensal.parquet"
if mp.exists():
    m = pd.read_parquet(mp)
    m["data"] = pd.to_datetime(m["data"])
    rec = m[m.data >= "2000-01-01"]
    vol = (rec.sort_values("data").groupby("commodity")["preco"]
           .apply(lambda s: np.log(s.where(s > 0)).diff().std() * np.sqrt(12)).dropna().sort_values())
    sel = vol[vol.index.str.contains("Maize|Sorghum|Soybean|Cotton|Rice|Wheat|Sugar|Banana|Groundnut|Coffee|Beef|Orange",
                                     case=False, regex=True)]
    if len(sel):
        fig, ax = plt.subplots(figsize=(9, 0.35 * len(sel) + 1))
        sel.plot.barh(ax=ax)
        ax.set_title("Volatilidade anualizada do preço internacional (log-retornos mensais, 2000+)")
        plt.show()
    print(sel.round(3).to_string())

# %% [markdown]
# ### 20.7 Mapa de conectividade das bases
# Como cada base se liga às outras no produto (chave espacial/temporal) e as ligações **novas**, além das sugeridas pelo
# desafio.

# %%
lig = pd.DataFrame([
    ("IMERG/POWER/ERA5 (chuva)", "MODIS/Landsat/S2 (NDVI)", "tempo (defasagem 1–2 meses)", "resposta da vegetação; detecção de estresse"),
    ("ONI + TNA/TSA (oceanos)", "chuva fev–mai", "tempo (out–jan → fev–mai)", "NOVO: previsão de tercil antes do plantio"),
    ("GRACE (TWS)", "chuva acumulada / GLDAS", "tempo (memória de 1–3 anos)", "NOVO: reserva hídrica para irrigação no ano seguinte"),
    ("SRTM (relevo)", "POWER/ERA5 (temperatura, chuva)", "espaço (altitude, orografia)", "microclima de serra × sertão; geada em baixadas"),
    ("SRTM + IMERG (intensidade)", "NDVI (cobertura)", "espaço-tempo", "RUSLE: risco de erosão por rotação"),
    ("FIRMS/MCD64A1 (fogo)", "NDVI + chuva + uso do solo", "espaço-tempo", "NOVO: risco de queimada e manejo de restos culturais"),
    ("GAEZ (aptidão)", "IBGE PAM (produção real)", "espaço (município)", "validar o filtro de culturas candidatas"),
    ("IBGE PAM (rendimento)", "chuva/ONI/GRACE", "tempo (ano)", "NOVO: elasticidade do rendimento à seca por cultura"),
    ("FAOSTAT/Banco Mundial (preço)", "IBGE PAM / GAEZ", "cultura × ano", "renda e risco de mercado da rotação"),
    ("CDL (EUA)", "NDVI/HLS", "pixel × ano", "NOVO: prior de rotação (matriz de transição) e rótulos de treino"),
    ("CDL/MapBiomas (mapa de culturas)", "POWER (graus-dia)", "espaço + tempo", "NOVO: percolação de pragas + nº de gerações"),
    ("NEX-GDDP-CMIP6 (projeções)", "POWER/ERA5 (histórico)", "tempo (2030–2100)", "NOVO: sliders de cenário futuro"),
], columns=["base A", "base B", "chave", "uso no produto"])
lig
