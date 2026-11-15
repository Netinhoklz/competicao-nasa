"""O que cabe (FAO GAEZ v4) e quando plantar com que risco (ZARC/MAPA), por município.

Uso:
  python -I gaez_zarc_municipio.py [geocodigo IBGE] [safra]   (padrão: 2311306 = Quixadá; 2026-2027) -> tabela do município
  python -I gaez_zarc_municipio.py --ceara [safra]             -> os 184 municípios do CE: CSV + resumo
  (o Nordeste inteiro é gerado por scripts/preparar_prototipo_nordeste.py gaez_zarc, com as mesmas funções)

- GAEZ v4: índice de aptidão 0–100 (uma casa decimal), sequeiro, insumo baixo e alto (clima 1981–2010, grade de 5'), no
  ponto interno do município. Classes da camada oficial de classes do GAEZ v4 (siLr; Fischer et al. 2021, fig. 7-3):
  > 85 muito alta; > 70 alta; > 55 boa; > 40 média; > 25 moderada; > 10 marginal; > 0 muito marginal. Corte "apta" = > 40
  (média ou melhor), decisão do projeto (revisão A3, 14/11; antes usávamos 35 com os limiares do texto do portal).
- ZARC: tábua de risco oficial (sequeiro). Valor do decêndio = risco de perda (20, 30 ou 40%); 0 = não indicado.
  Só entram os grupos de ciclo com cultivar indicada na portaria, quando isso foi conferido (revisão C3; ver
  CICLOS_COM_CULTIVAR). A janela vai do 1º dia do 1º decêndio ao último dia do último decêndio.
- Situação no município (regra decidida em 14/11, no nível do município):
  "indicada" = a cultura tem ZARC neste município e há risco de 20% em alguma combinação solo × ciclo (o GAEZ vira rótulo);
  "com risco" = tem ZARC, mas o melhor é 30% ou 40%;
  "só aptidão" = sem ZARC neste município, e o GAEZ dá aptidão > 40 (a janela vem da NASA: IMERG/SMAP);
  "fora" = o resto.
"""
import calendar
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # a pasta deste arquivo (scripts/), em qualquer máquina
import pandas as pd  # noqa: E402
import rasterio  # noqa: E402

from comum import DADOS, municipios_ce_gdf  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):  # no Jupyter a saída não tem reconfigure
    sys.stdout.reconfigure(encoding="utf-8")
# cultura do GAEZ -> culturas do ZARC (sequeiro) que respondem pela mesma planta
PARES = {
    "milho": ["Milho 1ª Safra", "Milho 1ª Safra consorciado com Braquiária"],
    "feijão-caupi": ["Feijão Caupi"],
    "feijão (Phaseolus)": ["Feijão 2ª Safra"],
    "sorgo": ["Sorgo Granífero", "Sorgo Forrageiro"],
    "algodão": ["Algodão Herbáceo"],
    "amendoim": ["Amendoim"],
    "girassol": ["Girassol"],
    "mandioca": [], "milheto": [], "guandu": [], "soja": [],
    "—": ["Mamona"],
}
SEM_ZARC = "sem ZARC na tábua"
# grupos de ciclo (Cod_Ciclo: 20 = Grupo I, 21 = II, 22 = III, 24 = IV) que têm cultivar indicada na portaria do estado.
# Conferido pelos revisores em 14/11 nas portarias do CE: caupi Port. SPA/MAPA 121/2026 (item 4.1.1: nenhuma cultivar nos
# Grupos II e III); mamona Port. 143/2026 (nenhuma no Grupo I); sorgo forrageiro Port. 297/2026. Outros estados: não
# conferido (usa todos os grupos da tábua e o cartão avisa).
CICLOS_COM_CULTIVAR = {("CE", "Feijão Caupi"): [20], ("CE", "Sorgo Forrageiro"): [20], ("CE", "Mamona"): [21, 22, 24]}
# a tábua traz duas mamonas: a tradicional (Nome_Clima "Não se aplica", cultura ...041) e a de "Clima Semiárido" (...011),
# indicada para baixa produtividade (Port. 143/2026, item 1.13). O cardápio usa a tradicional (revisão M5).
CLIMA_POR_CULTURA = {"Mamona": "Não se aplica"}
D = [f"dec{i}" for i in range(1, 37)]
APTA = 40  # classe "média" ou melhor do GAEZ v4
CLASSES = [(85, "muito alta"), (70, "alta"), (55, "boa"), (40, "média"), (25, "moderada"), (10, "marginal"), (0, "muito marginal")]


def classe_gaez(si):
    if si is None or si != si:
        return "sem dado"
    return next((nome for lim, nome in CLASSES if si > lim), "não apta")


def data_dec(k):
    """Decêndio 1..36 -> dia/mês de início (1, 11 ou 21)."""
    return f"{[1, 11, 21][(k - 1) % 3]:02d}/{(k - 1) // 3 + 1:02d}"


def data_dec_fim(k):
    """Decêndio 1..36 -> dia/mês do último dia (10, 20 ou o fim do mês)."""
    mes = (k - 1) // 3 + 1
    dia = [10, 20, calendar.monthrange(2027, mes)[1]][(k - 1) % 3]
    return f"{dia:02d}/{mes:02d}"


def janelas(decs):
    """Lista de decêndios -> trechos contínuos 'dd/mm–dd/mm' (1º dia do 1º decêndio ao último dia do último)."""
    decs = sorted(set(decs))
    if not decs:
        return "nenhum"
    trechos, ini, ant = [], decs[0], decs[0]
    for d in decs[1:] + [None]:
        if d != (ant + 1 if ant else None):
            trechos.append(f"{data_dec(ini)}–{data_dec_fim(ant)}")
            ini = d
        ant = d
    return "; ".join(trechos)


def aptidao(pontos):
    """{(cultura, insumo): [aptidão 0–100, uma casa, em cada ponto (lon, lat)]} do GAEZ v4 (toda a terra da célula)."""
    sel = pd.read_csv(DADOS / "gaez" / "selecao.csv")
    sel = sel[(sel.servico == "res05") & sel.variavel.str.startswith("Suitability index") & sel.variavel.str.contains("all land")]
    si = {}
    for _, r in sel.iterrows():
        with rasterio.open(DADOS / "gaez" / r.arquivo) as src:
            si[(r.cultura_pt, r.input_level)] = [None if (src.nodata is not None and v[0] == src.nodata) or v[0] < 0
                                                 else round(float(v[0]) / 100, 1) for v in src.sample(pontos)]
    return si


def tabela(si_mun, Zm):
    """Linhas cultura × (aptidão, janela ZARC) de um município. Zm = linhas de sequeiro do ZARC do município."""
    uf = Zm.UF.iloc[0] if len(Zm) else None
    linhas = []
    for cult_g, culturas_z in PARES.items():
        for cz in culturas_z or [None]:
            q = Zm[Zm.Nome_cultura == cz] if cz else Zm.iloc[0:0]
            ciclos = CICLOS_COM_CULTIVAR.get((uf, cz))
            if ciclos is not None:
                q = q[q.Cod_Ciclo.isin(ciclos)]
            if cz in CLIMA_POR_CULTURA and "Nome_Clima" in q:
                q = q[q.Nome_Clima == CLIMA_POR_CULTURA[cz]]
            r20 = [i + 1 for i, c in enumerate(D) if (q[c] == 20).any()]
            r30 = [i + 1 for i, c in enumerate(D) if q[c].isin([20, 30]).any()]
            r40 = [i + 1 for i, c in enumerate(D) if q[c].isin([20, 30, 40]).any()]
            tem = bool(cz) and len(q) > 0
            linhas.append({"GAEZ": cult_g, "SI baixo": si_mun.get((cult_g, "Low")), "SI alto": si_mun.get((cult_g, "High")),
                           "ZARC": cz or SEM_ZARC, "risco 20%": janelas(r20) if tem else "—",
                           "risco ≤ 30%": janelas(r30) if tem else "—", "risco ≤ 40%": janelas(r40) if tem else "—",
                           "solo×ciclo com 20%": f"{int((q[D] == 20).any(axis=1).sum())} de {len(q)}" if tem else "—",
                           "ciclos_conferidos": ciclos is not None,
                           "_n20": len(r20), "_n30": len(r30), "_n40": len(r40), "_tem_zarc": tem})
    return pd.DataFrame(linhas)


def situacao(r):
    """Regra decidida em 14/11/2026, no nível do município: se a cultura tem ZARC neste município, o ZARC decide (o GAEZ
    vira rótulo); senão, o GAEZ (> 40, insumo baixo) decide. Mamona sem ZARC no município fica fora (sem camada GAEZ)."""
    if r["_tem_zarc"]:
        return "indicada" if r["_n20"] else ("com risco" if r["_n40"] else "fora")
    if r["GAEZ"] == "—":
        return "fora"
    return "só aptidão" if r["SI baixo"] is not None and r["SI baixo"] > APTA else "fora"


def zarc(safra):
    Z = pd.read_csv(DADOS / "complementares" / "zarc" / f"tabua_risco_ce_{safra}.csv", sep=None, engine="python")
    return Z[Z.Nome_Outros_Manejos == "Sequeiro"]


def um_municipio(geo, safra):
    mun = municipios_ce_gdf()
    pt = mun[mun.codarea.astype(int) == geo].iloc[0].geometry.representative_point()
    si = {k: v[0] for k, v in aptidao([(pt.x, pt.y)]).items()}
    Z = zarc(safra)
    Zm = Z[Z.geocodigo == geo]
    T = tabela(si, Zm).sort_values("SI baixo", ascending=False, na_position="last")
    print(f"{Zm.municipio.iloc[0] if len(Zm) else geo} ({geo}); ponto ({pt.y:.3f}, {pt.x:.3f}); ZARC {safra}, "
          f"{Zm.Portaria.nunique()} portarias (uma por cultura)")
    T = T[[c for c in T.columns if not c.startswith("_")]].astype(object)
    T = T.where(T.notna(), "—")
    print("| " + " | ".join(T.columns) + " |\n|" + "---|" * len(T.columns))
    for _, r in T.iterrows():
        print("| " + " | ".join(str(v) for v in r.values) + " |")


def ceara(safra):
    mun = municipios_ce_gdf()
    nomes = {str(m["id"]): (m["nome"], m["microrregiao"]["mesorregiao"]["nome"])
             for m in json.loads((DADOS / "referencia" / "ceara_municipios_nomes.json").read_text(encoding="utf-8"))}
    pts = [g.representative_point() for g in mun.geometry]
    si = aptidao([(p.x, p.y) for p in pts])
    Z = zarc(safra)
    todas = []
    for i, (_, m) in enumerate(mun.iterrows()):
        geo = int(m.codarea)
        T = tabela({k: v[i] for k, v in si.items()}, Z[Z.geocodigo == geo])
        T["situacao"] = T.apply(situacao, axis=1)
        T["ZARC"] = T.ZARC.where(T.GAEZ != "—", "Mamona")
        T.insert(0, "geocodigo", geo)
        T.insert(1, "municipio", nomes.get(str(geo), ("?", "?"))[0])
        T.insert(2, "mesorregiao", nomes.get(str(geo), ("?", "?"))[1])
        todas.append(T)
    A = pd.concat(todas)
    A["cultura"] = A.ZARC.where(A.ZARC != SEM_ZARC, A.GAEZ)
    saida = DADOS / "gaez_zarc"
    saida.mkdir(exist_ok=True)
    A.drop(columns=[c for c in A.columns if c.startswith("_")]).to_csv(saida / f"ceara_{safra}.csv", index=False)
    print(f"{A.geocodigo.nunique()} municípios; ZARC {safra}; gravado em {saida / f'ceara_{safra}.csv'}\n")
    R = pd.crosstab(A.cultura, A.situacao).reindex(columns=["indicada", "com risco", "só aptidão", "fora"], fill_value=0)
    print("Municípios por cultura e situação (de 184):")
    print(R.sort_values(["indicada", "só aptidão", "com risco"], ascending=False).to_string())
    ok = A[A.situacao.isin(["indicada", "só aptidão"])]
    por_mun = ok.groupby(["mesorregiao", "geocodigo"]).cultura.nunique()
    print("\nCulturas disponíveis por município (indicada + só aptidão + só ZARC), por mesorregião:")
    print(por_mun.groupby("mesorregiao").describe()[["min", "50%", "max"]].to_string())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ceara":
        ceara(sys.argv[2] if len(sys.argv) > 2 else "2026-2027")
    else:
        um_municipio(int(sys.argv[1]) if len(sys.argv) > 1 else 2311306, sys.argv[2] if len(sys.argv) > 2 else "2026-2027")
