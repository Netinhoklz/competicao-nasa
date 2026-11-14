# %% [markdown]
# ## 10. NASA SMAP L4: o solo agora
#
# **Ficha técnica**
# - **O que é:** umidade da zona da raiz (0–100 cm) do SMAP L4 (SPL4SMGP v008), um modelo que assimila o radiômetro.
#   Grade EASE-Grid 2.0 de 9 km, diária, de 31/03/2015 a 10/11/2026, recorte do Nordeste.
# - **O que o protótipo usa:** a média dos 30 dias até a última data, calculada em cada ano de 2015 a 2026
#   (`E:/campeonato-nasa/dados/prototipo/smap_janela_30d.nc`, gerado pelo motor). No pixel mais próximo do lugar, a
#   posição de 2026 entre os anos (1 = o mais seco): posição ≤ 3 = "seco para a época"; entre as 3 maiores = "úmido para a
#   época"; o resto, "normal" (`motor.smap_agora`).
# - **Por que a posição e não o valor:** contra 303 estações do CEMADEN, o SMAP L4 acompanha bem a variação (r 0,72), mas
#   o nível absoluto é mais alto (0,155 contra 0,080 m³/m³).

# %%
import shapely
import xarray as xr

sm = xr.open_dataset(DADOS / "prototipo" / "smap_janela_30d.nc").load()
rz = sm.rz
ano26 = int(rz.ano.max())
print(f"Janela de 30 dias até {sm.attrs['fim']}; anos {int(rz.ano.min())}–{ano26}; grade {rz.sizes['lat']} × {rz.sizes['lon']}")
ult = rz.sel(ano=ano26)
posto = (rz < ult).sum("ano") + 1  # posição de 2026 entre os anos: 1 = o mais seco (empates ficam com a menor posição)
valido = rz.notnull().all("ano")
posto = posto.where(valido)
lo, la = np.meshgrid(rz.lon.values, rz.lat.values)
UFCOD = dict(zip(M.UF.keys(), M.UF.values()))
linhas = []
for _, u in NE.iterrows():
    m = shapely.contains_xy(u.geometry, lo, la) & valido.values
    p = posto.values[m]
    linhas.append({"UF": UFCOD[str(u.codarea)], "pixels": int(m.sum()), "posição mediana (1 = mais seco)": float(np.median(p)),
                   "% pixels entre os 3 mais secos": round(float((p <= 3).mean() * 100), 1),
                   "% pixels entre os 3 mais úmidos": round(float((p >= rz.sizes['ano'] - 2).mean() * 100), 1),
                   "umidade 2026 (mediana, m³/m³)": round(float(np.median(ult.values[m])), 3),
                   "posição da média da UF": int(pd.Series({int(a): float(np.nanmean(rz.sel(ano=a).values[m])) for a in rz.ano.values}).rank()[ano26])})
display(pd.DataFrame(linhas).set_index("UF").reindex(UF_ORDEM))

# %%
# o que a página mostra no ponto interno de cada município (pixel mais próximo, como motor.smap_agora)
pix = rz.sel(lat=xr.DataArray(MUN.lat.values, dims="m"), lon=xr.DataArray(MUN.lon.values, dims="m"), method="nearest")
V = pd.DataFrame(pix.values.T, index=MUN.cod.values, columns=rz.ano.values)
n_anos = V.notna().sum(1)
pos = V.rank(axis=1, method="min")[ano26]
cls = np.where(pos <= 3, "seco para a época", np.where(pos >= n_anos - 2, "úmido para a época", "normal para a época"))
SM = pd.DataFrame({"posicao": pos, "classe": np.where(V[ano26].isna() | (n_anos < 5), "sem dado no pixel", cls), "uf": MUN.uf.values},
                  index=MUN.cod.values)
for cod in ["2311306", MUN[MUN.municipio == "Recife"].cod.iloc[0], MUN[MUN.municipio == "Barreiras"].cod.iloc[0]]:
    r = M.smap_agora(float(MUN.set_index("cod").at[cod, "lat"]), float(MUN.set_index("cod").at[cod, "lon"]))
    assert r.get("posto") == (None if np.isnan(SM.at[cod, "posicao"]) else int(SM.at[cod, "posicao"])), (cod, r)
print("Conferido com motor.smap_agora em 3 municípios. Classe que a página mostra no ponto interno, por UF:")
display(pd.crosstab(SM.uf, SM.classe, margins=True, margins_name="NE").reindex(UF_ORDEM + ["NE"]))

# %%
fig, axs = plt.subplots(1, 2, figsize=(16, 6.5))
im = axs[0].pcolormesh(rz.lon, rz.lat, posto, cmap=DIV.reversed(), vmin=1, vmax=rz.sizes["ano"], shading="auto")
NE.boundary.plot(ax=axs[0], color="#52514e", lw=0.6)
plt.colorbar(im, ax=axs[0], label=f"posição de 2026 entre {rz.sizes['ano']} anos (1 = mais seco)", shrink=0.8)
axs[0].set_title(f"Solo (zona da raiz) nos 30 dias até {sm.attrs['fim']}: 2026 contra 2015–2026", fontsize=10)
axs[0].set_xlim(*XLIM)
axs[0].set_ylim(*YLIM)
axs[0].set_aspect("equal")
axs[0].set_axis_off()
serie = pd.DataFrame({u: {int(a): float(np.nanmean(rz.sel(ano=a).values[shapely.contains_xy(g_, lo, la) & valido.values])) for a in rz.ano.values}
                      for u, g_ in zip([UFCOD[str(c)] for c in NE.codarea], NE.geometry)})[UF_ORDEM]
rel = (serie / serie.median() * 100).T
im2 = axs[1].imshow(rel.values, cmap=DIV.reversed(), vmin=80, vmax=120, aspect="auto")
for i in range(rel.shape[0]):
    for j in range(rel.shape[1]):
        axs[1].text(j, i, f"{rel.values[i, j]:.0f}", ha="center", va="center", fontsize=7, color="#0b0b0b")
axs[1].set_xticks(range(rel.shape[1]))
axs[1].set_xticklabels(rel.columns, fontsize=8)
axs[1].set_yticks(range(rel.shape[0]))
axs[1].set_yticklabels(rel.index, fontsize=8)
axs[1].grid(False)
plt.colorbar(im2, ax=axs[1], label="umidade média da UF (% da mediana 2015–2026)", shrink=0.8)
axs[1].set_title("Mesma janela de 30 dias, cada ano, por UF (vermelho = mais seco)", fontsize=10)
plt.tight_layout()
plt.show()

# %% [markdown]
# **Leitura:**
# - **O solo do NE está seco para a época, mas não em toda parte.** Na janela de 30 dias até 10/11/2026:
#   - MA, PI, PE, AL e SE têm posição mediana 2 de 12, com 80% a 98% dos pixels entre os 3 anos mais secos;
#   - CE, RN e BA têm posição 5; a PB, 4;
#   - pela média da UF, 2026 é o mais seco dos 12 anos no MA e em SE, o 2º no PI e em PE, e o 5º no CE.
# - **No ponto interno de cada município, a página diz "seco para a época" em 981 municípios**, "normal" em 771 e "úmido"
#   em 41. No PI são 198 de 224 secos; em AL, 97 de 102; em SE, 72 de 75. No CE: 39 secos, 120 normais e 25 úmidos.
#   Fernando de Noronha fica fora do recorte do SMAP.
# - **Em novembro, isso não prevê a estação** (ρ +0,01 entre o solo de novembro e o de fevereiro no CE, na proposta). A
#   página mostra a posição como contexto.
