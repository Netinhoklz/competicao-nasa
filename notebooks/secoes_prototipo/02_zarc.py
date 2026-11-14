# %% [markdown]
# ## 2. ZARC (MAPA): quando plantar e com que risco
#
# **Ficha técnica**
# - **O que é:** a tábua de risco do Zoneamento Agrícola de Risco Climático, nos dados abertos do MAPA, filtrada para as 9
#   UFs do Nordeste (`complementares/zarc_ne/tabua_risco_ne_<safra>.csv`, `;` como separador).
#   - 2026/27: **uma portaria por cultura e por estado**, de abril a agosto de 2026 nas 9 culturas do cardápio (contagem abaixo).
#   - 2025/26: usada para comparar.
# - **Unidade:** município × cultura × manejo × solo × ciclo. Para cada um dos 36 decêndios do ano, o valor é o risco de
#   perda (20, 30 ou 40%) ou 0 (não indicado).
#   - Solo: 1 arenoso, 2 médio, 3 argiloso; 11–16 = classes de água disponível AD1–AD6.
#   - Ciclo: Grupos I–IV (Cod_Ciclo 20, 21, 22, 24).
# - **Critério:** a cultura tem água suficiente na fase crítica em pelo menos 80% dos anos (linha de Campos et al. 2010).
#
# **Filtros que o motor aplica** (os mesmos aqui):
# - só sequeiro e só as 9 culturas do cardápio com ZARC;
# - **só os grupos de ciclo com cultivar indicada na portaria** (`gaez_zarc_municipio.CICLOS_COM_CULTIVAR`, revisão C3):
#   caupi e sorgo forrageiro no Grupo I, mamona nos Grupos II–IV. **Isso só foi conferido nas portarias do CE**; nos outros
#   8 estados entram todos os grupos da tábua, e o cartão avisa;
# - **só a mamona tradicional** (`CLIMA_POR_CULTURA`, revisão M5): a de "Clima Semiárido" (baixa produtividade,
#   Port. 143/2026, item 1.13) fica fora.
#
# **ZARC plurianual do CE** (revisão A1): mandioca (Port. 11/2020), milheto (Port. 330/2020) e palma (Port. 284/2019) têm
# portarias sem ano-safra, fora da tábua aberta. O motor lê uma tábua complementar extraída dos PDFs
# (`complementares/zarc_plurianual_ce/`; vigência pela página do MAPA de 05/11/2026, SISZARC não conferido). Nos outros
# 8 estados, essas culturas seguem sem ZARC no protótipo.
#
# **No protótipo:**
# - a janela com risco de 20%, até 30% e até 40% de cada cultura: a união dos solos e ciclos e, desde 14/11, a janela em
#   cada tipo de solo (revisão A7); a janela termina no último dia do decêndio (revisão M4);
# - duas datas (revisão A6): o 1º decêndio com alguma cultura do cardápio zoneada (até 40%) e o 1º com risco de 20%. O
#   motor procura a partir de **3 meses antes do início da estação do município** (seção 7);
# - **onde a cultura tem ZARC no município, o ZARC decide** (seção 3).

# %%
from gaez_zarc_municipio import data_dec

D = GZ.D
MENU_Z = M.ZARC_MENU
SAFRAS = ["2025-2026", "2026-2027"]
Z = {s: pd.read_csv(DADOS / "complementares" / "zarc_ne" / f"tabua_risco_ne_{s}.csv", sep=";") for s in SAFRAS}
Z26 = Z["2026-2027"]
print(f"ZARC 2026/27 (NE): {len(Z26):,} linhas; {Z26.geocodigo.nunique()} municípios; {Z26.Nome_cultura.nunique()} culturas; "
      f"{Z26.Portaria.nunique()} portarias; manejos: {Z26.Nome_Outros_Manejos.value_counts().to_dict()}")
display(Z26.groupby("UF").agg(linhas=("geocodigo", "size"), municipios=("geocodigo", "nunique"), culturas=("Nome_cultura", "nunique"),
                              portarias=("Portaria", "nunique")).reindex(UF_ORDEM).T)
men = Z26[(Z26.Nome_Outros_Manejos == "Sequeiro") & Z26.Nome_cultura.isin(MENU_Z)]
PxU = men.groupby(["Nome_cultura", "UF"]).Portaria.nunique().unstack().reindex(index=MENU_Z, columns=UF_ORDEM)
num = men.groupby(["Nome_cultura", "UF"]).Portaria.first().str.extract(r"Port\.(\d+)_de_(\S+)")
print(f"Cultura do cardápio × UF com exatamente uma portaria: {int((PxU == 1).sum().sum())} de {PxU.size}; "
      f"{men.Portaria.nunique()} portarias distintas para as 9 culturas. Número da portaria (data em cada linha):")
tab = num[0].unstack().reindex(index=MENU_Z, columns=UF_ORDEM)
tab["data"] = num[1].groupby(level=0).agg(lambda s: ", ".join(sorted(set(s)))).reindex(MENU_Z)
display(tab)
est = men.groupby("Nome_cultura").agg(municipios=("geocodigo", "nunique"), linhas=("geocodigo", "size"),
                                      solos=("Cod_Solo", lambda s: ",".join(map(str, sorted(s.unique())))),
                                      ciclos=("Cod_Ciclo", lambda s: ",".join(map(str, sorted(s.unique())))),
                                      climas=("Nome_Clima", lambda s: " | ".join(sorted(s.unique())))).reindex(MENU_Z)
display(est)


# %%
def mascaras(z):
    """Ciclos com cultivar (conferidos só no CE) e mamona tradicional: True = a linha fica."""
    ciclo = pd.Series(True, index=z.index)
    for (uf, cult), ciclos in GZ.CICLOS_COM_CULTIVAR.items():
        s_ = (z.UF == uf) & (z.Nome_cultura == cult)
        ciclo &= ~s_ | z.Cod_Ciclo.isin(ciclos)
    clima = pd.Series(True, index=z.index)
    for cult, cl in GZ.CLIMA_POR_CULTURA.items():
        clima &= (z.Nome_cultura != cult) | (z.Nome_Clima == cl)
    return ciclo, clima


def filtra(z):
    """Os filtros do motor: sequeiro, cultura do cardápio, ciclos com cultivar, mamona tradicional."""
    z = z[(z.Nome_Outros_Manejos == "Sequeiro") & z.Nome_cultura.isin(MENU_Z)]
    ciclo, clima = mascaras(z)
    return z[ciclo & clima]


seq = filtra(Z26)
ciclo, clima = mascaras(men)
print(f"Linhas de sequeiro das 9 culturas: {len(men):,}; depois dos filtros: {len(seq):,}. Saem {int((~ciclo).sum()):,} linhas do CE "
      f"(grupos de ciclo sem cultivar) e {int((~clima).sum()):,} da mamona de clima semiárido "
      f"(em {men[~clima].geocodigo.nunique()} municípios).")
print("Grupos de ciclo na tábua, por cultura, fora do CE (sem conferência de cultivar):")
display(men[men.UF != "CE"].groupby("Nome_cultura").Cod_Ciclo.apply(lambda s: ",".join(map(str, sorted(s.unique())))).reindex(MENU_Z).to_frame("ciclos").T)
q = men[(men.geocodigo == 2311306) & (men.Nome_cultura == "Feijão Caupi")]
qf = seq[(seq.geocodigo == 2311306) & (seq.Nome_cultura == "Feijão Caupi")]
jan = lambda t: GZ.janelas([i + 1 for i, c in enumerate(D) if (t[c] == 20).any()])  # noqa: E731
print(f"Exemplo (caupi em Quixadá, risco de 20%): todos os grupos {jan(q)}; só os grupos com cultivar (Grupo I) {jan(qf)}")
v = seq[D].stack()
print("Distribuição dos valores (linhas filtradas × 36 decêndios):")
display((v.value_counts(normalize=True) * 100).round(1).rename("% das células").to_frame().T)

# %%
# janela por cultura e UF: % dos municípios da UF com risco de 20% em alguma combinação solo × ciclo, em cada decêndio
r20m = (seq[D] == 20).groupby([seq.Nome_cultura, seq.geocodigo.astype(str)]).any()
cods = MUN.cod.values
fig, axs = plt.subplots(3, 3, figsize=(19, 10.5), sharex=True)
for ax, c in zip(axs.ravel(), MENU_Z):
    m_ = r20m.loc[c].reindex(cods, fill_value=False)
    H = m_.groupby(UFMUN.reindex(m_.index).values).mean().reindex(UF_ORDEM) * 100
    im = ax.imshow(H.values, aspect="auto", cmap=SEQ, vmin=0, vmax=100)
    ax.set_yticks(range(9))
    ax.set_yticklabels(UF_ORDEM, fontsize=8)
    ax.set_xticks(range(0, 36, 3))
    ax.set_xticklabels(M.MESES, fontsize=8)
    ax.grid(False)
    ax.set_title(c, fontsize=10)
fig.colorbar(im, ax=axs, shrink=0.6, label="% dos municípios da UF com risco de 20% no decêndio")
fig.suptitle("ZARC 2026/27, sequeiro: quando cada cultura tem risco de 20%, por UF (decêndios de jan a dez)", y=0.93)
plt.show()

# %%
# comprimento da janela de 20%: união dos solos e ciclos (o que a página mostra) e a melhor combinação solo × ciclo
U = r20m.sum(1).rename("n20_uniao")
B = seq.assign(n20=(seq[D] == 20).sum(1)).groupby([seq.Nome_cultura, seq.geocodigo.astype(str)]).n20.max().rename("n20_melhor")
JJ = pd.concat([U, B], axis=1).reset_index().rename(columns={"level_1": "cod", "geocodigo": "cod"})
JJ["uf"] = JJ.cod.map(UFMUN)
res = JJ.groupby("Nome_cultura").agg(municipios_com_zarc=("cod", "size"), n20_uniao_mediana=("n20_uniao", "median"),
                                     n20_melhor_mediana=("n20_melhor", "median"),
                                     sem_20_pct=("n20_uniao", lambda s: round((s == 0).mean() * 100, 1))).reindex(MENU_Z)
print("Decêndios com risco de 20% por município (só municípios com ZARC da cultura):")
display(res)
print("Mediana de decêndios com risco de 20% (união de solos e ciclos), por cultura e UF:")
display(JJ.pivot_table(index="Nome_cultura", columns="uf", values="n20_uniao", aggfunc="median").reindex(index=MENU_Z, columns=UF_ORDEM))

# %%
# janela por solo (revisão A7): o cartão mostra a janela em cada tipo de solo zoneado (motor.janelas_por_solo)
print(f"Conferência: a tábua filtrada do motor (motor.ZSEQ) tem {len(M.ZSEQ):,} linhas; a desta seção, {len(seq):,}")
ps = seq.assign(cod=seq.geocodigo.astype(str))
n_solo = (ps[D] == 20).groupby([ps.Nome_cultura, ps.cod, ps.Cod_Solo]).any().sum(1)  # decêndios com 20% em cada solo (união dos ciclos)
amp = n_solo.groupby(level=[0, 1]).agg(["min", "max", "size"])
amp["difere"] = amp["max"] > amp["min"]
amp["so_no_melhor"] = (amp["min"] == 0) & (amp["max"] > 0)
print("Por município: decêndios com risco de 20% no solo mais restritivo e no mais permissivo (medianas) e % dos municípios em que o solo muda a janela:")
display(amp.groupby(level=0).agg(solos=("size", "median"), solo_mais_restritivo=("min", "median"), solo_mais_permissivo=("max", "median"),
                                 pct_janela_muda_com_solo=("difere", lambda s: round(s.mean() * 100, 1)),
                                 pct_20_so_em_parte_dos_solos=("so_no_melhor", lambda s: round(s.mean() * 100, 1))).reindex(MENU_Z))
print("Exemplo (motor.janelas_por_solo, milho em Quixadá):")
display(pd.DataFrame(M.janelas_por_solo("2311306", "Milho 1ª Safra")).set_index("solo"))

# %%
# ZARC plurianual do CE (revisão A1): mandioca, milheto e palma têm portaria plurianual, fora da tábua aberta.
# O motor lê uma tábua complementar extraída dos PDFs (motor.PLUR) e a usa no cardápio do CE (motor.zarc_plurianual).
PL = M.PLUR
print(f"Tábua complementar do CE: {len(PL):,} linhas; {PL.geocodigo.nunique()} municípios; manejos {sorted(PL.Nome_Outros_Manejos.unique())}")
plr, H3, SIT_PLUR = [], {}, {}
for nome_m, nome_t in M.PLUR_NOME.items():
    q_ = PL[PL.Nome_cultura == nome_t]
    u_ = (q_[D] == 20).groupby(q_.geocodigo).any()
    H3[nome_m] = u_.reindex(MUN.cod[MUN.uf == "CE"], fill_value=False).mean() * 100
    # a regra de motor.zarc_plurianual: 20% em algum decêndio = indicada; só 30–40% = com risco; sem linha = fora da portaria
    z40_ = (q_[D] > 0).groupby(q_.geocodigo).any().any(axis=1)
    sit_ = pd.Series("fora da portaria", index=MUN.cod[MUN.uf == "CE"].values)
    sit_[z40_.index] = np.where(u_.any(axis=1).reindex(z40_.index), "indicada", np.where(z40_, "com risco", "fora"))
    SIT_PLUR[nome_m] = sit_
    plr.append({"cultura": nome_m, "portaria": q_.Portaria.iloc[0], "municípios na portaria": q_.geocodigo.nunique(),
                "solos": ",".join(map(str, sorted(q_.Cod_Solo.unique()))), "ciclos": ",".join(map(str, sorted(q_.Cod_Ciclo.unique()))),
                "decêndios com 20% (mediana)": u_.sum(1).median()} | sit_.value_counts().to_dict())
display(pd.DataFrame(plr).set_index("cultura").fillna(0))
H3 = pd.DataFrame(H3).T
fig, ax = plt.subplots(figsize=(13, 2.4))
im = ax.imshow(H3.values, aspect="auto", cmap=SEQ, vmin=0, vmax=100)
ax.set_yticks(range(len(H3)))
ax.set_yticklabels(H3.index, fontsize=8)
ax.set_xticks(range(0, 36, 3))
ax.set_xticklabels(M.MESES, fontsize=8)
ax.grid(False)
plt.colorbar(im, ax=ax, label="% dos municípios do CE", shrink=0.9)
ax.set_title("ZARC plurianual do CE: % dos municípios com risco de 20% em cada decêndio", fontsize=10)
plt.show()
# as duas datas da página (motor.ZPRIM) usam só a tábua aberta: mudariam com as plurianuais?
Zce = pd.concat([M.ZSEQ.reset_index()[lambda d: d.UF == "CE"], PL.assign(geocodigo=PL.geocodigo.astype(str))], ignore_index=True)
z40, z20 = (Zce[D] > 0).groupby(Zce.geocodigo).any(), (Zce[D] == 20).groupby(Zce.geocodigo).any()
muda40 = muda20 = 0
for cod in z40.index:
    ini = ((int(M.REG.mes_inicio_estacao.get(cod, 2)) - 4) % 12) * 3
    ordem = [(ini + k) % 36 for k in range(36)]
    p40 = next((k + 1 for k in ordem if z40.loc[cod].values[k]), None)
    p20 = next((k + 1 for k in ordem if z20.loc[cod].values[k]), None)
    muda40 += (GZ.data_dec(p40) if p40 else None) != M.ZPRIM[cod]["ate40"]
    muda20 += (GZ.data_dec(p20) if p20 else None) != M.ZPRIM[cod]["risco20"]
print(f"Com as plurianuais nas duas datas da página, mudariam no CE: o 1º decêndio zoneado em {muda40} municípios e o 1º com "
      f"20% em {muda20} (de {len(z40)}). Hoje o motor calcula as datas só com a tábua aberta.")

# %%
# 1º decêndio zoneado (até 40%) e 1º com risco de 20%: as datas que o motor mostra (motor.ZPRIM)
def dia_ordem(txt, cod):
    """'dd/mm' -> dia contínuo (negativo = ano anterior à estação), na ordem que o motor usa (3 meses antes da estação)."""
    if not isinstance(txt, str):
        return np.nan
    d_, m_ = map(int, txt.split("/"))
    k0 = (m_ - 1) * 3 + [1, 11, 21].index(d_)
    ini = ((int(M.REG.mes_inicio_estacao.get(cod, 2)) - 4) % 12) * 3
    doy = pd.Timestamp(2026, m_, d_).dayofyear
    return doy - 365 if (ini >= 18 and k0 >= ini) else doy


ZP = pd.DataFrame(M.ZPRIM).T
ZP["d40"] = [dia_ordem(t, c) for t, c in zip(ZP.ate40, ZP.index)]
ZP["d20"] = [dia_ordem(t, c) for t, c in zip(ZP.risco20, ZP.index)]
ZP["uf"] = ZP.index.map(UFMUN)
print(f"Municípios com alguma linha de ZARC do cardápio: {len(ZP)} de {len(MUN)}; sem nada zoneado: {int(ZP.ate40.isna().sum())}; "
      f"sem nenhum decêndio com risco de 20%: {int(ZP.risco20.isna().sum())}")
TK = [-92, -61, -31, 1, 32, 60, 91, 121, 152]
TKL = ["1/out", "1/nov", "1/dez", "1/jan", "1/fev", "1/mar", "1/abr", "1/mai", "1/jun"]
fig, axs = plt.subplots(1, 3, figsize=(20, 6.5))
mapa_ne(axs[0], ZP.d40, "1º decêndio com cultura do cardápio zoneada (até 40%)", vmin=-100, vmax=160, rotulo="data", ticks=TK, rotulos_ticks=TKL)
mapa_ne(axs[1], ZP.d20, "1º decêndio com risco de 20% (bege = nenhum)", vmin=-100, vmax=160, rotulo="data", ticks=TK, rotulos_ticks=TKL)
mapa_ne(axs[2], (ZP.d20 - ZP.d40).clip(0, 60), "Dias entre as duas datas", vmin=0, vmax=60, rotulo="dias")
plt.tight_layout()
plt.show()
mes20 = ZP.risco20.dropna().str[3:5].astype(int).map(lambda m: M.MESES[m - 1])
ordem_mes = ["jul", "ago", "set", "out", "nov", "dez", "jan", "fev", "mar", "abr", "mai", "jun"]
print("Municípios pelo mês do 1º decêndio com risco de 20%, por UF:")
display(pd.crosstab(ZP.uf.reindex(mes20.index), mes20).reindex(index=UF_ORDEM, columns=[m for m in ordem_mes if m in set(mes20)], fill_value=0))
gap = (ZP.d20 - ZP.d40).dropna()
print(f"Entre o 1º decêndio zoneado e o 1º com 20%: mesmo decêndio em {(gap == 0).mean():.0%} dos municípios; "
      f"mediana {gap.median():.0f} dias; ≥ 20 dias em {(gap >= 20).mean():.0%}")

# %%
# 2025/26 × 2026/27: o que mudou entre as portarias, comparando só linhas com o mesmo esquema de solo
chave = ["Nome_cultura", "geocodigo", "Cod_Solo", "Cod_Ciclo", "Cod_Clima"]
a, b = filtra(Z["2025-2026"]), filtra(Z["2026-2027"])
mm = a.merge(b, on=chave, how="outer", suffixes=("_25", "_26"), indicator=True)
amb = mm[mm._merge == "both"]
ident = pd.Series((amb[[c + "_25" for c in D]].values == amb[[c + "_26" for c in D]].values).all(1), index=amb.index)
comp = pd.DataFrame({
    "solos 2025/26": a.groupby("Nome_cultura").Cod_Solo.apply(lambda s: ",".join(map(str, sorted(s.unique())))),
    "solos 2026/27": b.groupby("Nome_cultura").Cod_Solo.apply(lambda s: ",".join(map(str, sorted(s.unique())))),
    "linhas 2025/26": a.groupby("Nome_cultura").size(), "linhas 2026/27": b.groupby("Nome_cultura").size(),
    "linhas pareadas": amb.groupby("Nome_cultura").size(),
    "% idênticas (36 decêndios)": (ident.groupby(amb.Nome_cultura).mean() * 100).round(1)}).reindex(MENU_Z)
print("Linhas pareadas por município × cultura × solo × ciclo × clima:")
display(comp.fillna({"linhas pareadas": 0}))
# milho e girassol: o esquema de solo mudou (classes 1–3 -> AD 11–16); a comparação só pode ser do município inteiro
mud = []
for c in ["Milho 1ª Safra", "Girassol"]:
    n = {}
    for s, z in [("2025-2026", a), ("2026-2027", b)]:
        q_ = z[z.Nome_cultura == c]
        n[s] = (q_[D] == 20).groupby(q_.geocodigo).any().sum(1)
    d_ = (n["2026-2027"] - n["2025-2026"]).dropna()
    mud.append({"cultura": c, "municípios nas duas": len(d_), "mediana 2025/26 (solos 1–3)": n["2025-2026"].median(),
                "mediana 2026/27 (AD1–AD6)": n["2026-2027"].median(), "diferença média": round(d_.mean(), 2),
                "% encolheu": round((d_ < 0).mean() * 100, 1), "% cresceu": round((d_ > 0).mean() * 100, 1)})
print("Milho e girassol: decêndios com risco de 20% (união de solos e ciclos) — NÃO comparável célula a célula:")
display(pd.DataFrame(mud).set_index("cultura"))

# %% [markdown]
# **Leitura:**
# - **O ZARC do NE 2026/27 tem 240.949 linhas, 17 culturas e 113 portarias.** Nas 9 culturas do cardápio há **exatamente
#   uma portaria por cultura e por estado: 81 portarias**, publicadas de 17/04 (amendoim) a 24/08/2026 (feijão de 2ª
#   safra).
# - **Os filtros do motor tiram 11.581 das 141.858 linhas de sequeiro** (a tábua filtrada tem as mesmas 130.277 linhas da
#   `motor.ZSEQ`):
#   - 3.027 linhas do CE, de grupos de ciclo sem cultivar, e 8.821 da mamona de clima semiárido, em 761 municípios
#     (267 linhas da mamona do CE caem nas duas regras);
#   - **o filtro de ciclos só foi conferido no CE.** Nos outros 8 estados entram todos os grupos da tábua;
#   - em Quixadá, o caupi a 20% vai de 21/02–20/04 (todos os grupos) para 11/03–20/04 (só o Grupo I).
# - **Na maior parte do calendário a cultura não é indicada:** 79,5% das células são 0; 9,9% têm risco de 20%, 5,4% de 30%
#   e 5,2% de 40%.
# - **A janela anda com o regime de chuva** (mapa de calor): começa mais cedo a oeste (MA e PI, de dezembro a março; o
#   milho, o amendoim e o algodão do MA já em novembro e dezembro), passa por fevereiro e março no CE e chega a abril–julho
#   em PE, AL e SE. A BA se espalha pelo ano todo.
# - **Comprimento da janela de 20%** (união de solos e ciclos, mediana dos municípios com ZARC):
#   - sorgo granífero e forrageiro 7 decêndios; amendoim e algodão 6; caupi, milho e mamona 5; girassol 4; feijão de 2ª
#     safra 3;
#   - sem nenhum decêndio a 20%: feijão de 2ª safra em 34,2% dos municípios, girassol em 31,8%, milho em 24,3%;
#   - a UF muda muito: o milho tem mediana de 12 decêndios no MA e 0 no RN; o sorgo granífero, 0 no MA e 12 em SE.
# - **O solo muda a janela em 66% a 87% dos municípios** (revisão A7). No milho, o solo mais restritivo tem mediana de 0
#   decêndio a 20%, e o mais permissivo, 5; em 37,9% dos municípios o milho só chega a 20% em parte dos solos (feijão de 2ª
#   safra: 62,1%). Em Quixadá, nenhum solo dá 20% ao milho, e o risco até 30% só aparece em AD4–AD6.
# - **As duas datas da página quase nunca coincidem:** o 1º decêndio com alguma cultura zoneada e o 1º com risco de 20%
#   caem no mesmo decêndio em só 4% dos municípios; a distância mediana é de 20 dias e chega a 20 dias ou mais em 61%.
#   - O 1º decêndio a 20% vai de novembro–janeiro (MA e PI) a março–abril (PB, PE, AL e SE). No CE, cai em janeiro (54
#     municípios) ou fevereiro (130).
#   - 136 municípios não têm decêndio a 20% em nenhuma cultura do cardápio (o centro da BA, em bege no mapa). Fernando de
#     Noronha não tem nada zoneado.
# - **ZARC plurianual do CE (revisão A1):** a tábua complementar tem 2.757 linhas.
#   - Mandioca (Port. 11/2020) e milheto (Port. 330/2020) cobrem os 184 municípios e são indicados em todos, com mediana
#     de 4 e 9 decêndios a 20%. A palma (Port. 284/2019) cobre 183: indicada em 180 e "com risco" em 3.
#   - **Por desenho, as duas datas da página usam só as culturas anuais da tábua aberta.** Com as plurianuais (a palma
#     começa em dezembro), o 1º decêndio zoneado mudaria em 183 dos 184 municípios do CE, e o aviso perderia o sentido
#     para as culturas anuais. A janela de cada plurianual aparece no cardápio.
# - **2025/26 × 2026/27 (revisão M6):**
#   - nas 7 culturas com o mesmo esquema de solo, as 98.051 linhas pareadas são **idênticas** nos 36 decêndios;
#   - milho e girassol trocaram de esquema (classes de textura 1–3 → AD1–AD6), e nenhuma linha pareia. No município
#     inteiro, a janela de 20% do milho diminuiu em 44,0% e aumentou em 22,6% (média de −0,59 decêndio); a do girassol
#     diminuiu em 46,8% e aumentou em 20,8%;
#   - **isso vem da troca do esquema de solo, não do clima.** A frase antiga "a janela do milho encolheu em 71% dos
#     municípios" não se sustenta.
# - **No produto:** a tábua muda a cada safra, e o cartão precisa do solo. Fora do CE, os grupos de ciclo ainda não foram
#   conferidos nas portarias, e as culturas de portaria plurianual (mandioca, milheto e palma) ficam sem ZARC.
