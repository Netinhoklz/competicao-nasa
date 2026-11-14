# %% [markdown]
# ## 9. NOAA ONI e a chuva recente: "este ano"
#
# **Ficha técnica**
# - **ONI (Oceanic Niño Index, NOAA/CPC):** anomalia da TSM no Niño-3.4 em médias móveis de 3 meses, de 1950 a 2026
#   (`indices_clima/atualizado_2026-11-14/oni.ascii.txt`, baixado em 14/11/2026).
#   - El Niño forte = ONI de OND–NDJ ≥ 1,5 (eventos e estação afetada em `el_nino_2026/eventos.csv`). São esses anos que
#     a seção 8 usa no próprio município.
# - **Chuva recente** (`el_nino_2026/estado_atual_uf.csv`): IMERG Late/Early de ago a nov/2026, contra uma normal feita
#   com o IMERG Final. A página mostra os mm e o **percentil**, marca como preliminar e diz que a chuva da estação seca não
#   prevê a quadra (revisões A14 e A15).
#
# **No protótipo:** o cartão "Este ano", com o rótulo **"ONI de ago–out/2026 (ASO): +2,46"** e o nível do El Niño no
# próprio município (seção 8). Fora do NE: "não avaliado".

# %%
oni = pd.read_csv(DADOS / "indices_clima" / "atualizado_2026-11-14" / "oni.ascii.txt", sep=r"\s+")
oni["t"] = oni.YR + oni.groupby("YR").cumcount() / 12
ult = oni.iloc[-1]
print(f"ONI: {len(oni)} trimestres, {oni.YR.min()}–{oni.YR.max()}; último {ult.SEAS} {ult.YR} = {ult.ANOM:+.2f}")
display(descreve(oni.ANOM.rename("ONI")))
aso = oni[oni.SEAS == "ASO"].set_index("YR").ANOM
mx = oni.loc[oni.ANOM.idxmax()]
print(f"ASO 2026 = {aso.iloc[-1]:+.2f}: posição {int(aso.rank(ascending=False, method='min')[aso.index[-1]])} de {len(aso)} trimestres ASO "
      f"desde 1950 (o 2º maior ASO é {aso.drop(aso.index[-1]).max():+.2f}, em {aso.drop(aso.index[-1]).idxmax()}); "
      f"maior que {(oni.ANOM < aso.iloc[-1]).mean():.1%} de todos os trimestres. Recorde de qualquer trimestre: {mx.ANOM:+.2f} ({mx.SEAS} {mx.YR})")
oni_m = M.EN["ONI_ultimo"][1]
print("Rótulo da página: " + f"ONI de ago–out/2026 (ASO): {M._br(oni_m)}, {M._rotulo_oni(oni_m)}. É o maior ago–out desde 1950 "
      "(o recorde de qualquer trimestre é +2,59, em 2015/16).")
fig, ax = plt.subplots(figsize=(14, 4))
ax.bar(oni.t, oni.ANOM, width=1 / 12, color=np.where(oni.ANOM >= 0, "#d03b3b", "#3987e5"))
for y in (1.5, -1.5):
    ax.axhline(y, color="#52514e", lw=0.8, ls="--")
ax.set_ylabel("ONI (°C)")
ax.set_title("ONI 1950–2026 (vermelho = quente, azul = frio; tracejado = ±1,5, evento forte)")
plt.show()
print("El Niños fortes (ONI de OND–NDJ ≥ 1,5) e a estação afetada:")
display(M.EVT[M.EVT.ONI_OND_NDJ >= 1.5])

# %%
print("Chuva de ago a nov/2026 por UF, como a página mostra (preliminar: IMERG Late/Early contra normal do IMERG Final):")
display(M.ATUAL.reindex(UF_ORDEM)[["chuva_ago_nov2026_mm", "normal_mm", "percentil"]])

# %% [markdown]
# **Leitura:**
# - **O ONI de ago–out/2026 (ASO) é +2,46, o maior ASO desde 1950** (1º de 77; o 2º é +2,04, em 1997). Ele passa 99,7% de
#   todos os 921 trimestres. O recorde de qualquer trimestre é +2,59 (NDJ de 2015/16). A página diz isso e chama o evento
#   de "El Niño muito forte".
# - **Oito El Niños fortes desde 1957** (ONI de OND–NDJ ≥ 1,5). O de 2009/10 tem ONI de 1,50: o arquivo o chama de
#   "moderado", mas a regra ≥ 1,5 o conta como forte (revisão B13). Na era IMERG entram 1998, 2010, 2016 e 2024.
# - **A chuva de ago a nov/2026 é a da estação seca:** percentil 11 no MA, 25 no PI, 39 no CE, 54 no RN, na PB e em PE, 68
#   na BA, 71 em AL e 79 em SE. É dado preliminar, comparado a uma normal de outro produto, e não prevê a quadra.
