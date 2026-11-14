# %% [markdown]
# ## 16. Percolação de pragas — conectividade do hospedeiro no espaço e "ponte verde" no tempo
#
# **Ideia.** Uma praga especialista só se espalha se encontra hospedeiro (a cultura que ela come) em sequência.
# - **No espaço:** se os talhões da mesma cultura formam um **aglomerado conectado** que atravessa a paisagem, a praga
#   percola. A teoria de percolação por sítio numa grade quadrada dá um limiar de fração de hospedeiro de
#   p_c ≈ 0,593 com 4 vizinhos e ≈ 0,407 com 8 vizinhos. Acima dele surge um aglomerado gigante.
# - **No tempo:** a **ponte verde** é o hospedeiro que está no mesmo lugar em dois anos seguidos. É exatamente o que a
#   rotação quebra: a larva que nasce onde a mãe pôs o ovo no ano anterior não encontra comida se a cultura mudou.
# - **Escala da praga:** a conectividade depende do **raio de dispersão**. Uma larva de solo anda metros; uma mariposa voa
#   quilômetros. Testamos 0 m, 300 m, 1 km e 5 km.
#
# **Dados (30 m):**
# - **EUA:** CDL, por tipo de cultura, 2023–2025, nas 6 janelas de 40 × 40 km (seção 14).
# - **Ceará:** classe "lavoura" do mapa anual Impact Observatory/Esri (10 m, 2017–2023, Planetary Computer, **global**),
#   reamostrada a 30 m em janelas de 40 × 40 km nas 4 AOIs.
#
# Script: `scripts/percolacao.py`. Saídas em `E:/campeonato-nasa/dados/percolacao/`.
#
# **Ressalvas:**
# - Não há dado de ocorrência de praga para validar. Isto mede a **estrutura** da paisagem que favorece ou bloqueia a
#   dispersão, não o dano.
# - No Ceará, a classe "lavoura" do mapa global separa mal os roçados pequenos do sertão. A fração de lavoura no Sertão
#   Central (< 1%) está provavelmente **subestimada**.
#
# Obs.: "percolação" também é o termo hidrológico para a drenagem profunda da água no solo. No produto, ela é o termo
# D do balde FAO-56 (seção 30, módulo M1). Esta seção trata da percolação de **pragas**.

# %%
import sys
import warnings

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from scipy import ndimage as ndi
from comum import DADOS

plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": 0.3})
P = DADOS / "percolacao"
met = pd.read_csv(P / "metricas.csv")
cen = pd.read_csv(P / "cenarios.csv")
masc = np.load(P / "mascaras_90m.npz")
ORDEM_RAIO = ["0 m", "300 m", "1 km", "5 km"]

# %% [markdown]
# ### 16.1 A teoria: limiar de percolação numa paisagem aleatória
# A curva mostra a fração dos pixels de hospedeiro no maior aglomerado (8 vizinhos) numa grade aleatória de 400 × 400.
# Abaixo de ~0,41 o hospedeiro está fragmentado; acima, surge o aglomerado gigante. Os pontos são as nossas janelas reais
# (hospedeiro no ano, raio 0). Paisagens reais têm talhões contíguos, então ficam acima da curva aleatória para o mesmo p.

# %%
rng = np.random.default_rng(1)
ps = np.linspace(0.05, 0.8, 31)
S_teo = []
for p in ps:
    g = rng.random((400, 400)) < p
    lab, _ = ndi.label(g, structure=np.ones((3, 3)))
    t = np.bincount(lab.ravel())[1:]
    S_teo.append(t.max() / g.sum() if g.sum() else 0)
ult = met[(met.camada == "hospedeiro no ano") & (met.raio == "0 m")]
ult = ult[ult.ano == ult.groupby("regiao").ano.transform("max")]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(ps, S_teo, "k-", label="paisagem aleatória (teoria)")
ax.axvline(0.407, color="gray", ls="--", lw=1)
ax.text(0.415, 0.05, "p_c ≈ 0,407 (8 vizinhos)", fontsize=8)
for _, r in ult.iterrows():
    ax.scatter(r.p, r.S, s=50, marker="o" if r.pais == "EUA" else "s")
    ax.annotate(f"{r.regiao} ({r.hospedeiro})", (r.p, r.S), fontsize=7, xytext=(3, 3), textcoords="offset points")
ax.set_xlabel("fração de hospedeiro na janela (p)")
ax.set_ylabel("fração do hospedeiro no maior aglomerado")
ax.set_title("Percolação por sítio: teoria × paisagens reais (raio 0)")
ax.legend()
plt.show()

# %% [markdown]
# ### 16.2 Hospedeiro no ano × ponte verde, por raio de dispersão
# - S(r) = fração do hospedeiro que fica no maior aglomerado quando pixels a até r de distância se conectam.
# - "atravessa" = o aglomerado gigante toca dois lados opostos da janela de 40 km, ou seja, percola de fato.

# %%
def tabela(camada):
    d = met[met.camada == camada]
    d = d[d.ano == d.groupby("regiao").ano.transform("max")]
    t = d.pivot_table(index=["pais", "regiao", "hospedeiro"], columns="raio", values="S")[ORDEM_RAIO].round(2)
    t.insert(0, "p (fração da janela)", d.groupby(["pais", "regiao", "hospedeiro"]).p.first().round(3))
    t["atravessa a 300 m"] = d[d.raio == "300 m"].set_index(["pais", "regiao", "hospedeiro"]).atravessa
    return t


print("HOSPEDEIRO NO ÚLTIMO ANO")
display(tabela("hospedeiro no ano"))
print("PONTE VERDE (hospedeiro no mesmo pixel em dois anos seguidos: 2024→2025 nos EUA, 2022→2023 no Ceará)")
display(tabela("ponte verde (t e t+1)"))

fig, axs = plt.subplots(1, 2, figsize=(14, 4.5), sharey=True)
for ax, cam in zip(axs, ["hospedeiro no ano", "ponte verde (t e t+1)"]):
    d = met[met.camada == cam]
    d = d[d.ano == d.groupby("regiao").ano.transform("max")]
    for reg, g in d.groupby("regiao"):
        g = g.set_index("raio").loc[ORDEM_RAIO]
        ax.plot(ORDEM_RAIO, g.S, marker="o", ls="-" if g.pais.iloc[0] == "EUA" else "--", label=f"{reg} ({g.hospedeiro.iloc[0]})")
    ax.set_title(cam)
    ax.set_xlabel("raio de dispersão da praga")
axs[0].set_ylabel("fração do hospedeiro no maior aglomerado")
axs[1].legend(fontsize=7, loc="lower right")
plt.suptitle("Linha cheia = EUA (CDL, cultura específica); tracejada = Ceará (lavoura, mapa global)")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 16.3 Mapas: onde está a ponte verde
# Hospedeiro no último ano (cinza) e ponte verde (vermelho), reamostrados a 90 m só para visualização.

# %%
pares = [("iowa_story", "iowa_story_2025", "iowa_story_ponte_2024_25", "Iowa — milho"),
         ("texas_lubbock", "texas_lubbock_2025", "texas_lubbock_ponte_2024_25", "Texas — algodão"),
         ("apodi_jaguaribe", "apodi_jaguaribe_2023", "apodi_jaguaribe_ponte_2022_23", "Apodi (CE) — lavoura"),
         ("sertao_central", "sertao_central_2023", "sertao_central_ponte_2022_23", "Sertão Central (CE) — lavoura")]
fig, axs = plt.subplots(1, 4, figsize=(17, 4.5))
for ax, (reg, k_ano, k_ponte, tit) in zip(axs, pares):
    img = np.zeros(masc[k_ano].shape + (3,))
    img[masc[k_ano]] = (0.75, 0.75, 0.75)
    img[masc[k_ponte]] = (0.85, 0.1, 0.1)
    ax.imshow(img)
    ax.set_title(tit, fontsize=9)
    ax.axis("off")
plt.suptitle("Cinza = hospedeiro no último ano; vermelho = ponte verde (mesmo pixel em dois anos seguidos); janelas de 40 km")
plt.tight_layout()
plt.show()

# %% [markdown]
# ### 16.4 Quanto de rotação desfaz o aglomerado gigante da ponte verde?
# Cenário: retirar ao acaso uma fração f dos **talhões** da ponte verde (rotacioná-los para outra cultura) e medir o
# maior aglomerado a 300 m, em % da ponte original. Média de 10 sorteios.

# %%
piv = cen.pivot_table(index="f_talhoes_rotacionados", columns="regiao", values="gigante_pct_ponte_original")
fig, ax = plt.subplots(figsize=(9, 4.5))
for reg in piv.columns:
    ls = "--" if reg in ("apodi_jaguaribe", "cariri", "ibiapaba", "sertao_central") else "-"
    ax.plot(piv.index * 100, piv[reg] * 100, marker="o", ls=ls, label=reg)
ax.set_xlabel("% dos talhões da ponte verde rotacionados")
ax.set_ylabel("maior aglomerado (raio 300 m), % da ponte original")
ax.legend(fontsize=7)
ax.set_title("Rotação × conectividade da ponte verde")
plt.show()
display((piv * 100).round(0).T)

# %% [markdown]
# ### 16.5 No Ceará, a lavoura volta ao mesmo lugar? (persistência = ponte verde ÷ lavoura do ano)

# %%
ce = met[(met.pais == "Brasil (Ceará)") & (met.raio == "0 m")]
pa = ce[ce.camada == "hospedeiro no ano"].set_index(["regiao", "ano"]).p
pp = ce[ce.camada == "ponte verde (t e t+1)"].set_index(["regiao", "ano"]).p
pers = (pp / pa.reindex(pp.index)).unstack(0)
fig, ax = plt.subplots(figsize=(9, 3.8))
(pers * 100).plot(ax=ax, marker="o")
ax.set_ylabel("% da lavoura que se repete no ano seguinte")
ax.set_title("Persistência da lavoura no mesmo pixel (Impact Observatory 10 m → 30 m)")
plt.show()
display((pers * 100).round(0))

# %% [markdown]
# ### 16.6 Insights para o produto
# - **A rotação quebra a ponte verde para pragas de pouca mobilidade.** No Iowa, o milho do ano forma um aglomerado
#   gigante a 300 m (98%, atravessa a janela). O milho que **persiste** de um ano para o outro, porém, fica fragmentado:
#   só 5% no maior aglomerado. É assim que a rotação milho-soja corta o ciclo de pragas de solo, cuja larva nasce onde
#   estava a cultura no ano anterior.
# - **A monocultura mantém a ponte verde conectada.**
#   - No Texas, o algodão contínuo deixa 65% da ponte verde num único aglomerado que atravessa a janela, o análogo do
#     bicudo no Ceará dos anos 1980.
#   - No cenário, **rotacionar ~30% dos talhões derruba o aglomerado de 65% para ~22%**, e 50% leva a ~9%.
#   - Na soja contínua do Mississippi, é preciso rotacionar mais da metade.
# - **Praga que voa longe não respeita a rotação individual.** Com raio de 5 km, quase todas as janelas, inclusive as do
#   Ceará, ficam conectadas. Para mariposas como a lagarta-do-cartucho, a rotação no talhão não basta: é preciso
#   **coordenação regional**, como o vazio sanitário ou o calendário comum de plantio. O produto deve dizer isso.
# - **No sertão, o roçado já "roda" no espaço.** No Sertão Central, só 28–64% da lavoura (média ~45%, variando com o
#   ano) volta ao mesmo pixel no ano seguinte, por deslocamento e pousio. No Apodi irrigado são 82–91%, no Cariri
#   73–81%. **A ponte verde é um risco das áreas irrigadas e contínuas**, não do sequeiro itinerante.
# - **Leitura do cenário:** no Apodi a curva oscila porque poucos talhões grandes dominam a janela. Com mapa de talhões
#   reais, o cenário fica estável.
# - **Como entra na QUADRA:** um índice de **ponte verde** por célula, com a fração de hospedeiro persistente e o tamanho
#   do aglomerado no raio da praga-alvo. Ele soma risco às estratégias de monocultura (S0) e dá crédito às que quebram a
#   ponte (S1–S3). É um fator **estrutural**, grau C de evidência, até haver dado de ocorrência de praga para validar
#   (ex.: GBIF ou monitoramento de armadilhas).
# - **Funciona no mundo todo:** os EUA usam o CDL (cultura específica); qualquer outro país pode usar o mapa anual global
#   de lavoura, ou um classificador de culturas próprio (seção 30, ideia 1).
