# %% [markdown]
# ## 6. Como isso entra no motor da QUADRA: o catálogo de rotações ponderado pelo clima
#
# O catálogo de rotações comprovadas (`pesquisa/catalogo_rotacoes.json`) reúne 147 configurações. Foram debatidas
# por 10 especialistas e passaram por verificação adversária. Cada cartão traz:
# - o **efeito** (cultura seguinte, sequência inteira, consórcio, solo ou praga);
# - o **grau** (A–D);
# - a **transferência** para o semiárido (T0 = medido no semiárido brasileiro; T1 = estrato análogo; T2 = só direção;
#   T3 = não transfere).
#
# Aqui somamos o terceiro eixo, **medido com a NASA:** a semelhança entre o clima do lugar do estudo e o clima de cada
# município, pela assinatura do POWER das seções 1 a 3.
#
# **Recibo de evidência ponderado pelo clima, para cada estratégia e município:**
# 1. **Filtro de aptidão (GAEZ):** a cultura cabe no município (seção 4)?
# 2. **Data de plantio (IMERG):** o início típico e a faixa do município (seção 5), atualizados nos portões.
# 3. **Efeito esperado:** a média dos cartões do catálogo, ponderada por w = exp(−d²/2) entre o município e o lugar de
#    cada estudo. Só os cartões T0 e T1 entram com número; T2 entra só como direção.
# 4. **Confiança:** se o melhor estudo tem w < 0,3, o recibo diz "nenhum estudo de clima parecido" e rebaixa o grau.

# %%
import json
import re
from pathlib import Path

CAT = json.loads(Path(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\pesquisa\catalogo_rotacoes.json").read_text(encoding="utf-8"))
C = pd.DataFrame(CAT["configuracoes"]).merge(pd.read_csv(D_APR / "catalogo_cartao_lugar.csv"), on="id")
LA = pd.read_csv(D_APR / "catalogo_lugares_assinaturas.csv")


def pct_relativo(c):
    """Efeito em % do controle: o pct do cartão; em t/ha, divide pelo rendimento do controle impresso no texto."""
    e = c["efeito"] or {}
    if e.get("pct") and e["pct"][0] is not None:
        return pd.Series(e["pct"][:3], dtype=float)
    m = re.search(r"(\d+,\d+) → (\d+,\d+) t/ha", c["efeito_texto"] or "")
    if e.get("unidade") == "t/ha" and m:
        b = float(m.group(1).replace(",", "."))
        return pd.Series([100 * (e.get(k) if e.get(k) is not None else np.nan) / b for k in ("central", "baixo", "alto")], dtype=float)
    return pd.Series([np.nan] * 3)


C[["pct", "pct_baixo", "pct_alto"]] = C.apply(pct_relativo, axis=1)
LA["d_quixada"] = dist(za, z(LA))
LA["w_quixada"] = np.exp(-LA.d_quixada ** 2 / 2)
C = C.merge(LA[["lugar", "d_quixada", "w_quixada"]], on="lugar", how="left")
C["classe_w"] = pd.cut(C.w_quixada, [-0.01, 0.3, 0.6, 1.01], labels=["w < 0,3", "0,3 ≤ w < 0,6", "w ≥ 0,6"]).astype(str)
C.loc[C.lugar.isna(), "classe_w"] = "sem lugar (global ou região)"
print(f"{len(C)} cartões; {C.lugar.notna().sum()} com lugar identificável ({C.lugar.nunique()} lugares)")
display(pd.crosstab(C.tipo, C.transferencia, margins=True, margins_name="total"))

# %%
ordem = ["w ≥ 0,6", "0,3 ≤ w < 0,6", "w < 0,3", "sem lugar (global ou região)"]
cores_w = {"w ≥ 0,6": "#1a7f37", "0,3 ≤ w < 0,6": "#9ac26b", "w < 0,3": "#d9a441", "sem lugar (global ou região)": "#bdbdbd"}
T = pd.crosstab(C.tipo, C.classe_w).reindex(columns=ordem, fill_value=0)
T = T.loc[T.sum(1).sort_values().index]
fig, axs = plt.subplots(1, 2, figsize=(16, 5.5))
T.plot.barh(stacked=True, ax=axs[0], color=[cores_w[c] for c in ordem], width=0.75)
axs[0].set_xlabel("número de cartões")
axs[0].set_title("Catálogo: de que clima vem cada cartão (peso w para Quixadá)")
axs[0].legend(fontsize=8, loc="lower right")
P = C.dropna(subset=["pct", "w_quixada"])
P = P[P.efeito.map(lambda e: (e or {}).get("na") in ("cultura_seguinte", "sequencia_inteira", "sistema_consorciado"))]
marc = {"cultura_seguinte": "o", "sequencia_inteira": "s", "sistema_consorciado": "^"}
for na, g in P.groupby(P.efeito.map(lambda e: e["na"])):
    err = np.vstack([(g.pct - g.pct_baixo).clip(lower=0).fillna(0), (g.pct_alto - g.pct).clip(lower=0).fillna(0)])
    axs[1].errorbar(g.w_quixada, g.pct, yerr=err, fmt=marc[na], ms=6, alpha=0.75, capsize=2, label=na.replace("_", " "))
lg = next(c for c in CAT["configuracoes"] if c["id"] == "ne_lg_cereal_sequeiro_quente")["efeito"]["pct"]
axs[1].axhspan(lg[1], lg[2], color="tab:green", alpha=0.08)
axs[1].axhline(lg[0], color="tab:green", ls="--", lw=1)
axs[1].text(0.99, lg[0] + 2, f"cartão NE (síntese, B·T1): +{lg[0]:.0f}% ({lg[1]:+.0f} a {lg[2]:+.0f})", ha="right", fontsize=8, color="tab:green",
            transform=axs[1].get_yaxis_transform())
for _, r in P[(P.w_quixada > 0.25) | (P.pct.abs() > 60)].iterrows():
    axs[1].annotate(r.id, (r.w_quixada, r.pct), fontsize=6.5, xytext=(3, 3), textcoords="offset points")
axs[1].axhline(0, color="k", lw=0.6)
axs[1].set_xlabel("peso de clima w para Quixadá (POWER)")
axs[1].set_ylabel("efeito (% do controle)")
axs[1].set_title("Efeito de cada cartão com lugar × semelhança de clima")
axs[1].legend(fontsize=8)
plt.tight_layout()
plt.show()

# %%
cols = ["id", "tipo", "configuracao", "pct", "pct_baixo", "pct_alto", "grau", "transferencia", "lugar", "w_quixada"]
print("Cartões com clima parecido com o de Quixadá (w ≥ 0,3), do mais parecido ao menos:")
display(C[C.w_quixada >= 0.3].sort_values("w_quixada", ascending=False)[cols].round(2))
print("Lugares de estudo do catálogo, do mais parecido ao menos parecido com Quixadá:")
display(LA.sort_values("d_quixada")[["lugar", "chuva_anual_mm", "aridez_P_ET0", "meses_umidos", "d_quixada", "w_quixada"]].round(2))

# %% [markdown]
# **Leitura:**
# - **72 dos 147 cartões têm um lugar identificável** (31 lugares). Os outros são médias globais ou de continente, que
#   já entram só como direção (T2/T3).
# - **Lugares mais parecidos com Quixadá:** Bom Jesus-PI (w 0,95), Pentecoste (0,77), Crato (0,75), Mossoró (0,74),
#   Taperoá (0,66), Oeste da Bahia (0,59) e Serra Talhada (0,55).
# - **Os celeiros temperados têm w = 0,00:** Corn Belt, Europa, Ontário e Pradarias. A regra do catálogo ("número só
#   com T0 ou T1") agora tem uma medida da NASA por trás.
# - **21 cartões vêm de clima parecido (w ≥ 0,3), mas nenhum deles é de rotação no tempo medida no semiárido
#   brasileiro.**
#   - Os do Nordeste são de cobertura, consórcio (palma + sorgo), agrofloresta (gliricídia) e praga (bicudo).
#   - **Nenhum número de rotação (T0 ou T1) vem de clima parecido.** O Franke da África Austral (+42%) caiu para
#     w 0,10 e saiu da lista.
#   - O único cartão de rotação com w ≥ 0,3 é o soja → milho de Bom Jesus-PI (−1,6%, nulo, T2, w 0,95). Entra só como
#     direção.
# - **No gráfico de dispersão, os efeitos acima de +100% são biomassa de cobertura, não grão.** É o caso da
#   sobressemeadura de Pacheco 2013 e dos adubos verdes irrigados de Mossoró.

# %% [markdown]
# ### A lacuna, no mapa: onde está o estudo de rotação mais parecido com cada município?
# - **Painel da esquerda:** quantos cartões do catálogo vêm de um clima parecido (w ≥ 0,3) com o de cada município. É a
#   densidade de evidência aplicável.
# - **Painel do meio:** o peso w do **ensaio de rotação no tempo** (cartão do tipo rotação, efeito na cultura seguinte)
#   de clima mais parecido.
# - **Painel da direita:** o lugar desse ensaio.

# %%
zl = z(LA)
WM = np.exp(-np.array([dist(zm.iloc[i], zl) for i in range(len(M))]) ** 2 / 2)  # municípios × lugares
WM = pd.DataFrame(WM, columns=LA.lugar.values, index=M.cod.values)
lug_card = C.dropna(subset=["lugar"])
M["cartoes_w03"] = [(WM.loc[c, lug_card.lugar].values >= 0.3).sum() for c in M.cod]
rot = C[(C.tipo == "rotacao") & C.lugar.notna() & C.efeito.map(lambda e: (e or {}).get("na") == "cultura_seguinte")]
lug_rot = rot.lugar.unique()
M["w_rotacao"] = WM[lug_rot].max(1).values
M["lugar_rotacao"] = WM[lug_rot].idxmax(1).values
geo = municipios_ce_gdf().assign(cod=lambda g: g.codarea.astype(str)).merge(M, on="cod")
fig, axs = plt.subplots(1, 3, figsize=(19, 6.5))
geo.plot(column="cartoes_w03", ax=axs[0], cmap="Greens", legend=True, legend_kwds={"label": "cartões com w ≥ 0,3"})
axs[0].set_title("Evidência do catálogo com clima parecido")
geo.plot(column="w_rotacao", ax=axs[1], cmap="YlGn", vmin=0, vmax=1, legend=True, legend_kwds={"label": "w do ensaio de rotação mais parecido"})
axs[1].set_title("Confiança do número de rotação no tempo")
geo.plot(column="lugar_rotacao", ax=axs[2], categorical=True, legend=True, cmap="Set2",
         legend_kwds={"fontsize": 7, "loc": "lower left", "bbox_to_anchor": (0, -0.4)})
axs[2].set_title("De onde vem esse ensaio")
for a in axs:
    ceara_gdf().boundary.plot(ax=a, color="k", lw=0.8)
    a.set_axis_off()
plt.tight_layout()
plt.show()
print("Cartões de rotação no tempo com lugar:", ", ".join(sorted(rot.id)))
display(M.groupby("mesorregiao").agg(cartoes_w03=("cartoes_w03", "median"), w_rotacao=("w_rotacao", "mean"),
                                    lugar_rotacao=("lugar_rotacao", lambda s: s.value_counts().index[0])).round(2))

# %% [markdown]
# **Leitura:**
# - **O ensaio de rotação no tempo mais parecido com cada município fica fora do Ceará:**
#   - **Centro-Sul, Jaguaribe, Sertões, Sul, Noroeste e Norte:** Bom Jesus-PI, com soja → milho no Cerrado (w médio de
#     0,65 no Noroeste a 0,90 no Centro-Sul). O efeito foi nulo e o cartão é T2.
#   - **Região Metropolitana de Fortaleza:** o Franke da Savana da Guiné (Tamale), w 0,75.
#   - O Franke da África Austral não é mais o ensaio mais parecido de nenhuma mesorregião.
# - **Cada mesorregião tem de 15 a 23 cartões de clima parecido** (mediana por município), quase todos de consórcio,
#   cobertura, agrofloresta e praga.
# - **É a lacuna que mais muda o ranking do motor:** a passagem da prática atual (S0) para a rotação no tempo nunca foi
#   medida (cartão `ne_s0_para_rotacao_tempo`, D·T3, de 0 a +9%). O experimento mais barato que responde a isso é o de
#   faixas que trocam de lugar a cada ano, num município do sertão.

# %% [markdown]
# ### Leguminosa antes do cereal: quanto esperar em cada região do Ceará?
# Os três estratos do Franke (2018), os únicos cartões de leguminosa → cereal com lugar e transferência T1, são
# ponderados pelo peso de clima de cada município. Ficam lado a lado com o cartão-síntese do Nordeste.

# %%
fr = C[C.id.isin(["franke_sahel", "franke_guine", "franke_austral"])].set_index("id")
Wf = WM[fr.lugar.values].values
M["leg_cereal_pct"] = (Wf * fr.pct.values[None, :]).sum(1) / Wf.sum(1)
M["soma_w_franke"] = Wf.sum(1)
display(fr[["configuracao", "pct", "pct_baixo", "pct_alto", "grau", "transferencia", "lugar", "w_quixada"]].round(2))
display(M.groupby("mesorregiao").agg(efeito_ponderado_pct=("leg_cereal_pct", "mean"), soma_dos_pesos=("soma_w_franke", "mean")).round(2))
q = M.loc[M.municipio.str.contains("Quixadá"), ["leg_cereal_pct", "soma_w_franke"]].iloc[0]
print(f"Quixadá: leguminosa → cereal ponderada pelo clima = +{q.leg_cereal_pct:.0f}% (soma dos pesos {q.soma_w_franke:.2f}); "
      f"cartão NE = +{lg[0]:.0f}% ({lg[1]:+.0f} a {lg[2]:+.0f}). Só no ano colhido; contra a S0 (consórcio), não medido.")

# %% [markdown]
# **Leitura:**
# - **Ponderado pelo clima, o efeito da leguminosa antes do cereal em Quixadá fica em cerca de +28%** (soma dos pesos
#   0,46). Entre as mesorregiões, vai de +29% a +31%.
#   - Quem mais pesa é a Savana da Guiné (+24%, w 0,25).
#   - O Sahel (+24%, não significativo) pesa 0,11.
#   - A África Austral (+42%) pesa só 0,10.
# - **Ressalva: o motor fica com o cartão-síntese de +24% (de +2% a +49%) como número central** e usa os +28% só como
#   sensibilidade. O motivo é que nenhum dos três estratos vem de clima parecido com o de Quixadá: todos têm w < 0,3
#   (o maior é 0,25). Pela regra do recibo, isso rebaixa o grau.
# - **Os dois números valem só no ano colhido e só contra milho solteiro:**
#   - o milho quebra em 20,2% dos município-anos do Ceará (2000–2024);
#   - contra a prática atual (milho + feijão consorciados), o efeito não foi medido.

# %% [markdown]
# ### Conclusões deste aprofundamento
# - **A evidência certa para o Ceará vem de climas parecidos, e a NASA permite medir essa semelhança em qualquer lugar.**
#   Os melhores análogos do sertão são o Cerrado piauiense, o semiárido da Índia (Patancheru), Serra Talhada e Sobral,
#   não os celeiros temperados onde a rotação foi medida por satélite (w = 0,00).
# - **A ordem dos análogos é robusta** (seção 1). O Cerrado piauiense fica entre os 3 mais parecidos com o Sertão
#   Central em 100% de 2.000 sorteios de pesos, e o semiárido da Índia em 98,6%. Tirando qualquer variável, a
#   concordância da ordem fica entre 0,85 e 0,92 (tau de Kendall).
# - **Cada município puxa uma literatura diferente** (seção 2), então o recibo do produto é municipal.
# - **O "sertão no mundo"** (seção 3) mostra onde mais a ferramenta funciona do mesmo jeito: Chaco argentino, Oeste da
#   Bahia, norte da Austrália, Burkina Faso, sudoeste de Madagascar e o Deccan na Índia.
# - **Clima parecido também traz culturas parecidas** (seção 4, Spearman −0,76). Os 5 análogos mais próximos têm todos
#   perfil de culturas parecido. Harare, que tem culturas diferentes, deixou de ser análogo. O motor continua exigindo
#   as duas coisas.
# - **Armadilha do El Niño** (seção 5): nos anos de El Niño forte, a chuva "começou" mais cedo (dia 6 contra 18) e a
#   quadra falhou. O início da estação não basta; quem decide são os portões de março e abril (chuva desde 1/fev e SMAP).
# - **O catálogo ponderado pelo clima** (esta seção) chega a três conclusões:
#   - os números que valem no sertão vêm só do próprio Nordeste (consórcio, cobertura, agrofloresta, praga). A
#     leguminosa → cereal do Franke chega a Quixadá com w ≤ 0,25 e fica só como sensibilidade;
#   - nenhum ensaio de rotação no tempo foi feito em clima de sertão. O de clima mais parecido (soja → milho em Bom
#     Jesus-PI, w 0,95) é do Cerrado, deu efeito nulo e é T2;
#   - o ensaio de faixas que trocam de lugar é a medida que falta.
