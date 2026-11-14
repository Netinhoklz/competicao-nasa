# %% [markdown]
# ## 7. NASA GPM IMERG: o regime de chuva de cada município
#
# **Ficha técnica**
# - **Fonte:** chuva diária IMERG V07 (0,1°), via NASA POWER, de 01/01/1998 a 14/09/2026, recortada no Nordeste e agregada
#   por município (média das células com centro dentro do município; quem não tem centro de célula dentro usa a célula
#   mais próxima do ponto interno). **O IMERG Final V07 termina em 30/09/2025; o que vem depois é o Late (preliminar)**
#   (revisão A16). A climatologia do regime usa só anos completos, 1998–2025.
# - **Regime:** os 4 meses seguidos mais chuvosos da climatologia (`analogos_aprofundado/regime_chuva_ne_mun.csv`). O NE
#   tem três regimes:
#   - **quadra do norte** (jan–abr, fev–mai): a mesma regra do CE;
#   - **litoral leste** (mar–jun, abr–jul): chuva de outono e inverno;
#   - **Cerrado e sul da BA** (out–jan, nov–fev, dez–mar): chuva de primavera e verão.
#
# **No protótipo (`motor.regime`):**
# - "Estação chuvosa típica" do município, com a chuva da estação e a fração do ano;
# - fora da quadra do norte, o aviso de que os portões de 19/mar e 30/abr e as datas do plano foram calibrados no sertão
#   do CE;
# - **na faixa costeira leste** (até ~20 km do mar, do RN ao sul de Calcanhar até o sul da BA), o aviso de que **o IMERG capta só 39–72% da chuva
#   medida** (viabilidade dos artigos, bloco B2) e de que ali as janelas do ZARC guiam as datas;
# - a ordem em que o motor procura o 1º decêndio do ZARC começa 3 meses antes do 1º mês da estação (seção 2).


# %%
def grupo_regime(m0):
    return "quadra do norte" if m0 <= 2 else ("litoral leste" if m0 <= 6 else "Cerrado e sul da BA")


REGIMES = ["quadra do norte", "litoral leste", "Cerrado e sul da BA"]
COR_REG = dict(zip(REGIMES, [CAT[0], CAT[1], CAT[2]]))
RG7 = M.REG.copy()  # regime_chuva_ne_mun.csv, indexado pelo código IBGE
RG7["uf"] = UFMUN.reindex(RG7.index)
RG7["regime"] = RG7.mes_inicio_estacao.map(grupo_regime)
RG7["lon"] = MUN.set_index("cod").lon.reindex(RG7.index)
EST = ["out–jan", "nov–fev", "dez–mar", "jan–abr", "fev–mai", "mar–jun", "abr–jul"]
print(f"{len(RG7)} municípios com regime. Estação típica (4 meses mais chuvosos) por UF:")
display(pd.crosstab(RG7.uf, RG7.estacao).reindex(index=UF_ORDEM, columns=[e for e in EST if e in set(RG7.estacao)], fill_value=0)
        .assign(total=lambda d: d.sum(1)))
display(pd.crosstab(RG7.uf, RG7.regime).reindex(index=UF_ORDEM, columns=REGIMES, fill_value=0).T)
print("Regra do início da chuva por regime (seção 8):")
display(RG7.groupby("regime").regra.first().reindex(REGIMES).to_frame())
print("Chuva da estação (mm, IMERG) e fração da chuva do ano que cai nela, por regime:")
display(RG7.groupby("regime")[["chuva_estacao_media_mm", "fracao_do_ano"]].describe()
        .loc[REGIMES, (slice(None), ["min", "25%", "50%", "75%", "max"])].round(2))

# %%
fig, axs = plt.subplots(1, 3, figsize=(20, 6.5))
mapa_ne(axs[0], RG7.regime, "Regime de chuva (4 meses mais chuvosos, IMERG 1998–2025)", categorias=COR_REG)
mapa_ne(axs[1], RG7.chuva_estacao_media_mm, "Chuva da estação típica", vmin=200, vmax=1200, rotulo="mm")
mapa_ne(axs[2], RG7.fracao_do_ano, "Fração da chuva do ano na estação", vmin=0.4, vmax=0.9, rotulo="fração")
plt.tight_layout()
plt.show()

# %%
# os avisos que o motor dá (motor.regime): fora da quadra do norte e no litoral leste (ponto interno do município)
RG7["fora_da_quadra"] = ~(RG7.mes_inicio_estacao <= 2)
RG7["aviso_imerg_leste"] = RG7.index.isin(M.LESTE)  # até ~20 km (0,2°) da costa leste, do RN ao sul de Calcanhar até a BA (motor._leste_costeiro)
av = pd.DataFrame({"municípios": RG7.uf.value_counts().reindex(UF_ORDEM),
                   "fora da quadra do norte": RG7.groupby("uf").fora_da_quadra.sum().reindex(UF_ORDEM),
                   "aviso do IMERG no litoral leste": RG7.groupby("uf").aviso_imerg_leste.sum().reindex(UF_ORDEM)}).fillna(0).astype(int)
display(av.T.assign(NE=lambda d: d.sum(1)))
print("Aviso do litoral leste × regime do município:")
display(pd.crosstab(RG7.aviso_imerg_leste.map({True: "com aviso", False: "sem aviso"}), RG7.regime).reindex(columns=REGIMES, fill_value=0))
print(f"Exemplo (motor.regime, Quixadá): {M.regime('2311306', 'CE', -39.03)['texto']}")
rec = MUN[MUN.municipio == "Recife"].iloc[0]
print(f"Exemplo (motor.regime, Recife): {M.regime(rec.cod, rec.uf, rec.lon)['texto']}")

# %% [markdown]
# **Leitura:**
# - **O NE tem três regimes de chuva:**
#   - **quadra do norte** (jan–abr ou fev–mai) em 1.056 municípios: o CE inteiro, 193 do MA, 147 da PB, 143 do PI e 111 do
#     RN;
#   - **litoral leste** (mar–jun ou abr–jul) em 312: PE 96, PB 76, AL 64, RN 56 e SE 20;
#   - **Cerrado e sul da BA** (out–jan, nov–fev ou dez–mar) em 426: 320 da BA, 81 do PI, 24 do MA e 1 de PE.
# - **A estação concentra a chuva do ano:** mediana de 72% na quadra, 63% no litoral leste e 65% no Cerrado. A chuva da
#   estação tem mediana de 606 mm na quadra (199 a 1.579), 449 mm no litoral leste e 452 mm no Cerrado.
# - **738 municípios (41%) não estão na quadra do norte.** Neles, a página avisa que os portões de 19/mar e 30/abr e as
#   datas do plano vêm do sertão do CE.
# - **182 municípios recebem o aviso de que o IMERG capta só 39–72% da chuva medida:** os que ficam a até ~20 km da costa
#   leste, do RN (ao sul de Calcanhar) ao sul da BA (RN 26, PB 17, PE 25, AL 30, SE 26 e BA 58). É onde o achado foi
#   medido (estações a menos de 20 km do mar). O aviso vai pela distância à costa, não pelo regime: 115 deles têm regime
#   de litoral leste, 52 de quadra e 15 do Cerrado e sul da BA.
# - **No produto:** a regra do início da chuva e a ordem em que o motor procura a data do ZARC dependem do regime. No
#   litoral leste, o IMERG subestima a chuva, e as datas vêm do ZARC.
