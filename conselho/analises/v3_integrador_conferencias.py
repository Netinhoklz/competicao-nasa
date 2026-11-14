"""Integrador (v3): confere numeros da verificacao adversaria que nao estao em nenhuma saida.
(1) ZARC oficial x sintetico em Quixada, por solo x ciclo (milho e caupi);
(2) PPM: salto do bovino 2020 -> 2021 por UF;
(3) Censo 2017: rotacao sobre o total de estabelecimentos e sobre os de lavoura temporaria;
(4) FUNCEME: data maxima das linhas contra a da ultima leitura valida.
Somente le arquivos.
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa

import pandas as pd

A = Path(r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises")
DEC = {i: f"{['01', '11', '21'][(i - 1) % 3]}/{['jan', 'fev', 'mar', 'abr', 'mai', 'jun'][(i - 1) // 3]}" for i in range(1, 19)}
CICLO = {"20": "Grupo I", "21": "Grupo II", "22": "Grupo III"}
SOLO = {1: "arenoso", 2: "medio", 3: "argiloso", 11: "AD1", 12: "AD2", 13: "AD3", 14: "AD4", 15: "AD5", 16: "AD6"}
QXD = "2311306"

print("=== 1. ZARC 2026/27, sequeiro, Quixada (2311306): ultimo decendio de jan-jun com risco <= 30 e <= 20 ===")
z = pd.read_csv(DADOS / "complementares" / "zarc" / "tabua_risco_ce_2026-2027.csv", sep=";", dtype=str)
z = z[(z.Nome_Outros_Manejos == "Sequeiro") & (z.geocodigo == QXD)]
dec = [f"dec{i}" for i in range(1, 37)]
z[dec] = z[dec].astype(int)
SINT = pd.read_parquet(A / "saidas" / "agronomo_zarc_sintetico_prob.parquet")
SINT.index = SINT.index.astype(str)
DEC_S = ["01/jan", "11/jan", "21/jan", "01/fev", "11/fev", "21/fev", "01/mar", "11/mar", "21/mar", "01/abr", "11/abr", "21/abr"]
for c, pref in {"milho": "Milho 1", "caupi": "Feij\u00e3o Caupi"}.items():
    v = [SINT.loc[QXD, f"{c}|{d}"] for d in DEC_S]
    ok = [i + 1 for i, p in enumerate(v) if p >= 0.7]
    s_ult = max(ok) if ok else 0
    print(f"\n{c}: sintetico (P>=0,7) ultimo = {DEC.get(s_ult, 'sem janela')}")
    s = z[z.Nome_cultura.str.startswith(pref)]
    n_ok = 0
    for _, r in s.sort_values(["Cod_Ciclo", "Cod_Solo"]).iterrows():
        u30 = [i for i in range(1, 19) if 0 < r[f"dec{i}"] <= 30]
        u20 = [i for i in range(1, 19) if 0 < r[f"dec{i}"] <= 20]
        ult = max(u30) if u30 else 0
        dif = s_ult - ult if ult else None
        n_ok += dif is not None and abs(dif) <= 1
        print(f"  {CICLO[r.Cod_Ciclo]:9s} {SOLO[int(r.Cod_Solo)]:9s} risco<=30 ate {DEC.get(ult, 'sem janela'):10s} "
              f"risco<=20 ate {DEC.get(max(u20), '-') if u20 else 'sem janela':10s} dif sint-oficial {dif if dif is not None else '-'}")
    print(f"  combinacoes com |dif| <= 1 decendio: {n_ok} de {len(s)}")

print("\n=== 2. PPM: bovino 2020 -> 2021 por UF (soma municipal) ===")
p = pd.read_parquet(DADOS / "derivados" / "ibge_ne_ppm_mun_anual.parquet")
b = p[p.ano.isin([2020, 2021])].groupby(["uf", "ano"]).bovino.sum().unstack()
b["var_%"] = (b[2021] / b[2020] - 1) * 100
print(b.round(1).to_string())

print("\n=== 3. Censo 2017: rotacao (soma municipal) ===")
cz = pd.read_parquet(DADOS / "derivados" / "ibge_ne_censo2017_praticas_mun.parquet")
ufcol = "uf" if "uf" in cz.columns else None
if ufcol is None:
    cz["uf"] = cz.iloc[:, 0].astype(str).str[:2].map({"21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB",
                                                      "26": "PE", "27": "AL", "28": "SE", "29": "BA"})
cz["rot_tot"] = cz.pct_rotacao / 100 * cz.n_estab
cz["rot_lt"] = cz.pct_rotacao_lavtemp / 100 * cz.n_estab_lavtemp
for nome, g in [("NE", cz), ("CE", cz[cz.uf == "CE"]), ("RN", cz[cz.uf == "RN"])]:
    gt = g.dropna(subset=["pct_rotacao", "n_estab"])
    gl = g.dropna(subset=["pct_rotacao_lavtemp", "n_estab_lavtemp"])
    print(f"  {nome}: rotacao / total de estab. = {gt.rot_tot.sum() / gt.n_estab.sum():.3%} | "
          f"rotacao / estab. com lavoura temporaria = {gl.rot_lt.sum() / gl.n_estab_lavtemp.sum():.1%}")

print("\n=== 4. FUNCEME: datas ===")
f = pd.read_parquet(DADOS / "complementares" / "funceme" / "funceme_postos_diario.parquet")
print(f"  data maxima das linhas: {f.data.max().date()} | ultima leitura valida (mm nao nulo): {f.loc[f.mm.notna(), 'data'].max().date()}")
apos = f[f.data > "2026-11-13"]
print(f"  linhas depois de 13/11/2026: {len(apos)} (com mm nao nulo: {apos.mm.notna().sum()}; datas: {sorted(apos.data.dt.date.astype(str).unique())[:5]})")
