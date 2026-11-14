# %% [markdown]
# ## 8. NASA GPM IMERG: quando a estação começa e o El Niño no próprio município
#
# **Ficha técnica**
# - **Fonte:** a mesma chuva diária IMERG V07 da seção 7 (`analogos_aprofundado/onset_ne_mun.csv`).
# - **Regra de início** (agronômica, no espírito de Waha et al. 2012): o 1º dia com ≥ 20 mm em 3 dias **sem** veranico
#   de ≥ 10 dias secos (< 1 mm) nos 30 dias seguintes. A busca depende do regime:
#   - **quadra do norte (jan–abr, fev–mai): de 1/dez a 31/mai, como no CE**; a chuva da estação é a de fev–mai;
#   - outros regimes: de 2 meses antes do 1º mês da estação até o fim do 4º mês; a chuva da estação é a dos 4 meses.
# - **Coluna da chuva:** `chuva_estacao_mm`, que alimenta a perspectiva do El Niño.
# - **Produto:** o IMERG Final V07 termina em 30/09/2025; o arquivo vai até 14/09/2026 com o Late depois disso. **A estação
#   de 2026 é preliminar** em todos os regimes (revisão A16).
# - **El Niño forte:** ONI de OND–NDJ ≥ 1,5 (`el_nino_2026/eventos.csv`; seção 9). Na série IMERG entram 2010, 2016 e
#   2024 e, no litoral leste (estação que começa em mar–abr), também 1998.
#
# **No protótipo:**
# - `motor.inicio_estacao`: o início típico (mediana dos anos **sem** El Niño forte), a faixa p10–p90, a % de anos sem
#   início e, **sem negrito**, a diferença nos anos de El Niño forte, com os anos listados (revisões A17 e M25);
# - `motor._perspectiva_municipal`: nos El Niños fortes da série, em quantos a chuva da estação do município ficou no terço
#   mais seco. Com ONI ≥ 1,5, o alerta acende se isso aconteceu em pelo menos 2 e em ≥ 2/3 dos anos; senão, "sinal fraco".

# %%
FORTES = M.FORTES
O = M.ONS.copy()
O["uf"] = O.cod.map(UFMUN)
O["regime"] = O.mes_inicio_estacao.map(grupo_regime)
O["dia"] = np.nan
for m0, idx in O.groupby("mes_inicio_estacao").groups.items():
    s_ = O.loc[idx, "inicio_chuva"]
    O.loc[idx, "dia"] = pd.Series(np.asarray(M._dia_estacao(s_, m0), dtype=float), index=idx).where(s_.notna())
O["forte"] = O.ano.isin(FORTES)
O25 = O[O.ano <= 2025]  # como o motor: a estação de 2026 (IMERG Late, preliminar) fica fora das estatísticas
print(f"{O.cod.nunique()} municípios × estações; anos por regime:")
display(O.groupby("regime").agg(municipios=("cod", "nunique"), primeiro=("ano", "min"), ultimo=("ano", "max"),
                                anos=("ano", "nunique"), sem_inicio_pct=("inicio_chuva", lambda s: round(s.isna().mean() * 100, 1)),
                                anos_el_nino_forte=("ano", lambda s: ", ".join(map(str, sorted(set(s) & FORTES))))).reindex(REGIMES))


def janela(a, m):
    """Janela de busca da estação 'a' (cópia da regra de scripts/preparar_prototipo_nordeste.py, para datar o produto)."""
    if m <= 2:
        return pd.Timestamp(a - 1, 12, 1), pd.Timestamp(a, 5, 31)
    ano_m0 = a if m <= 6 else a - 1
    return (pd.Timestamp(ano_m0, m, 1) - pd.DateOffset(months=2),
            pd.Timestamp(ano_m0, m, 1) + pd.DateOffset(months=4) - pd.Timedelta(days=1))


FIM_FINAL = pd.Timestamp("2025-09-30")
prod = []
for m0 in sorted(O.mes_inicio_estacao.unique()):
    ult = int(O[O.mes_inicio_estacao == m0].ano.max())
    ini, fim = janela(ult, m0)
    prod.append({"estação": RG7[RG7.mes_inicio_estacao == m0].estacao.iloc[0], "municípios": int((RG7.mes_inicio_estacao == m0).sum()),
                 "última estação": ult, "busca": f"{ini:%d/%m/%Y}–{fim:%d/%m/%Y}",
                 "% dos dias depois do Final (Late, preliminar)": round(100 * max(0, (fim - max(ini - pd.Timedelta(days=1), FIM_FINAL)).days) / ((fim - ini).days + 1))})
print("Última estação de cada regime e quanto dela é IMERG Late (preliminar):")
display(pd.DataFrame(prod).set_index("estação"))

# %%
dem = O25[~O25.forte].groupby("cod").dia
PM8 = pd.DataFrame({"mediana": dem.median(), "p10": dem.quantile(0.1), "p90": dem.quantile(0.9),
                    "sem_inicio_pct": O25.groupby("cod").inicio_chuva.apply(lambda s: s.isna().mean() * 100),
                    "dif_el_nino": O25[O25.forte].groupby("cod").dia.median() - dem.median()})
PM8["faixa_p10_p90"] = PM8.p90 - PM8.p10
PM8["uf"], PM8["regime"] = PM8.index.map(UFMUN), RG7.regime.reindex(PM8.index)
# conferência: as mesmas datas que a página mostra (motor.inicio_estacao) nos 1.794 municípios
ok = 0
for cod in PM8.index:
    r = M.inicio_estacao(cod)
    dif = PM8.at[cod, "dif_el_nino"]
    ok += (r["mediana"] == M.data_doy(PM8.at[cod, "mediana"])) and (r["dif_el_nino_dias"] == (None if np.isnan(dif) else int(round(dif))))
print(f"Conferência com motor.inicio_estacao: {ok} de {len(PM8)} municípios com a mesma mediana e a mesma diferença")
display(descreve(PM8[["mediana", "p10", "p90", "faixa_p10_p90", "sem_inicio_pct", "dif_el_nino"]]))
tab8 = PM8.groupby(["regime", "uf"]).agg(municipios=("mediana", "size"), inicio_mediano=("mediana", "median"),
                                         faixa_p10_p90=("faixa_p10_p90", "median"), sem_inicio_pct=("sem_inicio_pct", "median"))
tab8["inicio_mediano"] = tab8.inicio_mediano.map(M.data_doy)
print("Por regime e UF (medianas dos municípios; dia negativo = ano anterior):")
display(tab8.reindex(REGIMES, level=0).round(1))
TK8 = [-92, -61, -31, 1, 32, 60, 91, 121]
fig, axs = plt.subplots(1, 3, figsize=(20, 6.5))
mapa_ne(axs[0], PM8.mediana, "Início típico da chuva (mediana dos anos sem El Niño forte)", vmin=-100, vmax=130, rotulo="data",
        ticks=TK8, rotulos_ticks=["1/out", "1/nov", "1/dez", "1/jan", "1/fev", "1/mar", "1/abr", "1/mai"])
mapa_ne(axs[1], PM8.faixa_p10_p90, "Faixa entre anos (p90 − p10)", vmin=0, vmax=120, rotulo="dias")
mapa_ne(axs[2], PM8.sem_inicio_pct, "% das estações sem início pela regra", vmin=0, vmax=50, rotulo="%")
plt.tight_layout()
plt.show()

# %%
# a janela do ZARC começa perto do início da chuva? (1º decêndio com risco de 20%, seção 2, × início típico do IMERG)
zc = pd.concat([PM8.mediana, ZP.d20.astype(float)], axis=1, keys=["inicio", "zarc20"]).dropna()
rho_z = stats.spearmanr(zc.inicio, zc.zarc20)
gapz = zc.zarc20 - zc.inicio
print(f"Início típico (IMERG) × 1º decêndio com 20% (ZARC), {len(zc)} municípios: Spearman {rho_z[0]:+.2f}; o ZARC começa "
      f"em mediana {gapz.median():+.0f} dias depois do início típico (p10 {gapz.quantile(0.1):+.0f}, p90 {gapz.quantile(0.9):+.0f})")
display(gapz.groupby(PM8.regime.reindex(gapz.index)).describe()[["count", "25%", "50%", "75%"]].reindex(REGIMES).round(0))

# %%
# El Niño forte e o início: a diferença do próprio município, os anos e o teste de permutação (revisão A17)
rng = np.random.default_rng(0)
NPERM = 1000
pval = pd.Series(np.nan, index=PM8.index)
for m0, gq in O25.groupby("mes_inicio_estacao"):
    pv = gq.pivot(index="cod", columns="ano", values="dia")
    f_ = np.isin(pv.columns.values, list(FORTES))
    Xv = pv.values
    obs = np.nanmedian(Xv[:, f_], 1) - np.nanmedian(Xv[:, ~f_], 1)
    cont = np.zeros(len(Xv))
    for _ in range(NPERM):
        fp = np.zeros(len(f_), bool)
        fp[rng.choice(len(f_), f_.sum(), replace=False)] = True
        cont += np.abs(np.nanmedian(Xv[:, fp], 1) - np.nanmedian(Xv[:, ~fp], 1)) >= np.abs(obs) - 1e-9
    pval[pv.index] = np.where(np.isnan(obs), np.nan, (cont + 1) / (NPERM + 1))
PM8["p_perm"] = pval
sinal = pd.cut(PM8.dif_el_nino, [-999, -5, 5, 999], labels=["antes (> 5 dias)", "igual (±5 dias)", "depois (> 5 dias)"])
t8 = pd.crosstab(PM8.uf, sinal).reindex(UF_ORDEM)
t8["p < 0,05 (%)"] = (PM8.p_perm < 0.05).groupby(PM8.uf).mean().reindex(UF_ORDEM).mul(100).round(1)
print(f"Início nos El Niños fortes − demais anos, por município ({NPERM} permutações dos anos em cada regime):")
display(t8)
print(f"NE: {int((PM8.p_perm < 0.05).sum())} de {int(PM8.p_perm.notna().sum())} municípios com p < 0,05 "
      f"({(PM8.p_perm < 0.05).mean():.1%}; ao acaso se esperam 5%). Quixadá: {PM8.at['2311306', 'dif_el_nino']:+.0f} dias, "
      f"p = {PM8.at['2311306', 'p_perm']:.2f}; anos {M.inicio_estacao('2311306')['anos_el_nino_forte']}")
anos_f = sorted(set(O25[O25.forte].ano))
an = O25[O25.forte].assign(anom=lambda d: d.dia - d.cod.map(PM8.mediana))
print("Os anos, um a um: início no El Niño forte − início típico do município (mediana dos municípios, dias):")
display(an.pivot_table(index="uf", columns="ano", values="anom", aggfunc="median").reindex(UF_ORDEM).round(0))
fig, axs = plt.subplots(1, 2, figsize=(14, 6.5))
mapa_ne(axs[0], PM8.dif_el_nino.clip(-40, 40), "El Niño forte − demais anos (dias; azul = antes)", cmap=DIV, vmin=-40, vmax=40, rotulo="dias")
mapa_ne(axs[1], PM8.p_perm, "p da permutação (claro = mais perto do acaso)", cmap=SEQ.reversed(), vmin=0, vmax=1, rotulo="p")
plt.tight_layout()
plt.show()

# %%
# El Niño forte e a chuva da estação no próprio município (motor._perspectiva_municipal)
oni_ult = M.EN["ONI_ultimo"][1]
lin = []
for cod in MUN.cod:
    pm = M.PERSP_MUN.get(cod)
    if oni_ult >= 1.5 and pm and pm["anos"]:
        niv = "alerta" if pm["inferior"] >= max(2, math.ceil(len(pm["anos"]) * 2 / 3)) else "sinal fraco"
    else:
        niv = "sem alerta" if pm else "sem dado"
    lin.append({"cod": cod, "nivel": niv, "inferior": pm["inferior"] if pm else np.nan, "n_fortes": len(pm["anos"]) if pm else np.nan})
NV = pd.DataFrame(lin).set_index("cod")
NV["uf"] = UFMUN
print(f"ONI de ago–out/2026 = {oni_ult:+.2f} (≥ 1,5): o motor avalia o alerta em cada município. Nível por UF:")
display(pd.crosstab(NV.uf, NV.nivel, margins=True, margins_name="NE").reindex(UF_ORDEM + ["NE"]))
print("Em quantos El Niños fortes a chuva da estação ficou no terço mais seco do município:")
display(pd.crosstab(NV.n_fortes.astype("Int64").astype(str) + " anos", NV.inferior.astype("Int64")))
acaso = {k: stats.binom.sf(max(2, math.ceil(k * 2 / 3)) - 1, k, 1 / 3) for k in (3, 4)}
print("Chance de acender o alerta só por acaso (anos independentes, terço = 1/3): "
      + "; ".join(f"com {k} anos, {p:.0%}" for k, p in acaso.items()))
rows, com26 = [], {}
for cod, gq in O.dropna(subset=["chuva_estacao_mm"]).groupby("cod"):
    s_ = gq.set_index("ano").chuva_estacao_mm
    t1, med = s_.quantile(1 / 3), s_[~s_.index.isin(FORTES)].median()
    for a in sorted(FORTES & set(s_.index)):
        rows.append({"cod": cod, "uf": UFMUN[cod], "ano": a, "pct": 100 * s_[a] / med, "terco_seco": s_[a] <= t1})
    an1 = sorted(FORTES & set(s_.index))  # sensibilidade: a mesma regra COM a estação de 2026 (o motor a tira)
    com26[cod] = "alerta" if sum(s_[a] <= t1 for a in an1) >= max(2, math.ceil(len(an1) * 2 / 3)) else "sinal fraco"
AN = pd.DataFrame(rows)
com26 = pd.Series(com26)
print(f"Sensibilidade: o motor tira a estação de 2026 (IMERG Late, preliminar) e acende o alerta em {int((NV.nivel == 'alerta').sum())} "
      f"municípios; com ela na série seriam {int((com26 == 'alerta').sum())} ({int((com26 != NV.nivel.reindex(com26.index)).sum())} mudam de nível)")
print("Chuva da estação nos El Niños fortes: % do normal (mediana dos municípios) e % dos municípios no terço mais seco:")
display(pd.concat({"% do normal": AN.pivot_table(index="uf", columns="ano", values="pct", aggfunc="median"),
                   "% no terço seco": AN.pivot_table(index="uf", columns="ano", values="terco_seco", aggfunc="mean") * 100},
                  axis=1).reindex(UF_ORDEM).round(0))
fig, axs = plt.subplots(1, 2, figsize=(16, 6.5), gridspec_kw={"width_ratios": [1, 1.4]})
mapa_ne(axs[0], NV.nivel, "Nível do El Niño na página (ONI +2,46)", categorias={"alerta": "#d03b3b", "sinal fraco": "#86b6ef", "sem dado": CINZA})
O["pct_normal"] = O.chuva_estacao_mm / O.cod.map(O25[~O25.forte].groupby("cod").chuva_estacao_mm.median()) * 100
serie = O.groupby(["regime", "ano"]).pct_normal.median().unstack(0)[REGIMES]
for a in anos_f:
    axs[1].axvspan(a - 0.45, a + 0.45, color="#f0efec", zorder=0)
for r_ in REGIMES:
    s_ = serie[r_].dropna()
    axs[1].plot(s_.index, s_.values, color=COR_REG[r_], marker="o", ms=4, label=r_)
    axs[1].plot([s_.index[-1]], [s_.values[-1]], marker="o", ms=9, mfc="#fcfcfb", mec=COR_REG[r_], ls="none")
axs[1].axhline(100, color="#52514e", lw=0.8)
axs[1].set_ylabel("chuva da estação (% da mediana do município, mediana dos municípios)")
axs[1].set_title("Chuva da estação por regime (faixa cinza = El Niño forte; anel = 2026, preliminar)", fontsize=10)
axs[1].legend(fontsize=8, frameon=False)
plt.tight_layout()
plt.show()
print("Chuva da estação em % da mediana do município (mediana dos municípios), anos de El Niño forte e 2026 (preliminar):")
display(serie.loc[[a for a in serie.index if a in FORTES or a == 2026]].round(0).T)

# %%
okc = O25.dropna(subset=["dia", "chuva_estacao_mm"])
rho_pool = stats.spearmanr(okc.dia, okc.chuva_estacao_mm)
rho_mun = okc.groupby("cod").apply(lambda g: stats.spearmanr(g.dia, g.chuva_estacao_mm)[0] if len(g) >= 10 else np.nan).dropna()
print(f"Início cedo traz estação mais chuvosa? Spearman início × chuva da estação: {rho_pool[0]:+.2f} (todos os município-anos); "
      f"por município, mediana {rho_mun.median():+.2f}, negativo em {(rho_mun < 0).mean():.0%} dos municípios")
display(rho_mun.groupby(RG7.regime.reindex(rho_mun.index)).median().reindex(REGIMES).round(2).to_frame("Spearman mediano").T)
ano_med = O25[O25.regime == "quadra do norte"].groupby("ano").dia.median()
t_mk = stats.kendalltau(ano_med.index, ano_med.values)
print(f"Tendência do início na quadra do norte (mediana dos municípios por ano, {ano_med.index.min()}–{ano_med.index.max()}): "
      f"Kendall τ {t_mk[0]:+.2f}, p = {t_mk[1]:.2f}")

# %% [markdown]
# **Leitura:**
# - **Série:** 28 estações na quadra e no Cerrado (1999–2026) e 29 no litoral leste (1998–2026). **A estação de 2026 é
#   IMERG Late em 100% dos dias** em 5 das 7 estações típicas (83% em nov–fev; 67% em out–jan): é preliminar e, como no
#   motor, fica fora das estatísticas abaixo (até 2025: 27 estações na quadra e no Cerrado, 28 no litoral leste).
# - **A página reproduz o notebook:** a mediana e a diferença do El Niño batem com `motor.inicio_estacao` nos 1.794
#   municípios.
# - **O início típico** (mediana dos anos sem El Niño forte; mediana de cada UF e regime) vai de 24/10 (Cerrado do MA)
#   a 17/03 (litoral leste de SE).
#   - Na quadra do norte: 13/12 no MA, 20/12 no PI, 16/01 no CE, 22/01 na PB e 26/01 no RN.
#   - No Cerrado e no sul da BA: 12/11.
# - **Entre anos, o mesmo município varia muito:** mediana de 69 dias entre p10 e p90 (de 11 a 133). É mais estreito na
#   quadra do MA (27 dias) e mais largo na quadra de AL, SE e BA (96 a 105 dias).
# - **Em parte dos anos a regra não acha início:** 5,0% das estações na quadra, 9,8% no litoral leste e 16,2% no Cerrado e
#   sul da BA; até 78% no centro da BA.
# - **O ZARC concorda com o IMERG no tempo:** Spearman +0,83 entre o início típico e o 1º decêndio com 20% (1.658
#   municípios). O ZARC começa, na mediana, 12 dias depois da chuva (p10 −6; p90 +42).
# - **El Niño forte e o início (revisão A17): com 3 anos (4 no litoral leste), a diferença não se separa do acaso.**
#   - 235 de 1.791 municípios (13,1%) têm p < 0,05 na permutação. Ao acaso se esperam 5%, mas municípios vizinhos dividem a
#     mesma chuva e não são testes independentes. No CE, só 0,5%.
#   - O sinal muda de ano para ano. No CE, a chuva começou 12 dias antes do típico em 2010, 11 antes em 2016 e 4 depois em
#     2024; na BA, 20 antes, 40 depois e 56 depois.
#   - Quixadá: +25 dias (2010: 19/03; 2016: 06/01; 2024: 12/02), p = 0,23.
#   - Por isso a página mostra os anos e não diz que o El Niño atrasa ou adianta o início.
# - **El Niño forte e a chuva da estação:** com o ONI em +2,46, o alerta acende em 922 municípios, e o "sinal fraco", em
#   872.
#   - Alerta em 182 do CE, 182 do MA, 152 do PI, 146 do RN e 127 da PB; em 47 de PE e 86 da BA; em nenhum de AL e SE.
#   - Ao acaso (anos independentes, terço de 1/3), o alerta acenderia em 26% dos municípios com 3 anos e em 11% com 4.
#   - 2010 e 2016 foram secos na quadra (CE: 61% do normal nos dois anos, com 100% dos municípios no terço seco). 2024 foi
#     quase normal (CE: 94%; 21% no terço seco).
#   - No litoral leste, 1998 foi o mais seco (PE 19%, AL 23%, PB 28%). Em 2010, AL e SE tiveram chuva acima do normal (151%
#     e 150%).
#   - O motor tira a estação de 2026 (preliminar) da série: 922 alertas. Com ela, seriam 955 (33 mudariam de nível).
# - **A estação de 2026 sai muito acima do normal:** +26% na quadra, +76% no litoral leste e +69% no Cerrado. É IMERG Late.
#   A revisão registra, sem refazer, um Late 2 a 3 vezes acima do Final em ago–set/2025. Esse número precisa ser conferido
#   antes de entrar na normal.
# - **Início cedo vem, em geral, com estação mais chuvosa** (Spearman −0,28 no conjunto; mediana de −0,14 por município,
#   negativa em 73%). O efeito some no Cerrado (−0,01).
# - **Não há tendência no início da quadra em 1999–2025** (Kendall τ −0,08; p = 0,56).
