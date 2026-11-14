"""v4 - Especialista Cerrado nordestino / MATOPIBA.

Pergunta: a sobressemeadura de cobertura na cultura de verao (Pacheco 2013/2017, Bom Jesus-PI)
e a cobertura de entressafra (Andrade 2025, Brejo-MA) dependem de chuva em janelas precisas.
Essas janelas existem no sertao? A v3 usou datas fixas do Cerrado (15/mar-15/mai) tambem em
Quixada, onde a estacao e fev-mai; aqui as janelas sao ancoradas no INICIO LOCAL das chuvas
de cada ano (semeadura = inicio agronomico), o que torna a comparacao justa.

Regras pre-declaradas (escolhidas antes de rodar):
  inicio agronomico: 1o dia, entre 1/set e 30/abr, com >= 20 mm em 3 dias e sem sequencia de
    >= 10 dias secos (< 1 mm) nos 30 dias seguintes.
  ciclo da cultura de verao: 125 d (Pacheco 2013: soja semeada 12/dez/2010, colhida 14-16/abr/2011).
  R5.5 (sobressemeadura) = semeadura + 95 d; janela de estabelecimento = [S+95, S+124] (30 d).
  pos-colheita = [S+125, S+154] (30 d): onde o milheto semeado apos a colheita FALHOU em 2011.
  ancoras de campo: Bom Jesus 2010/11 (sobressemeadura funcionou; pos-colheita falhou);
    limiar descritivo 50 mm/30 d (o mesmo da v3).
  entressafra util p/ cobertura (Andrade 2025): 90 d apos a colheita; Andrade mediu 353 mm
    (mai-ago/2021) e obteve 0,7-3,1 t/ha de cobertura; Silva 2022 (irrigado, adubado): 167 mm
    -> 6,84 t/ha e 268 mm -> 9,47 t/ha (patamar).
  rebrota pre-semeadura: 45 d antes da proxima semeadura (Pacheco 2013/2017: a braquiaria
    acumulou a maior parte da massa com as chuvas de outubro, antes da dessecacao).
"""
import sys
sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import numpy as np
import pandas as pd
import xarray as xr

PONTOS = {
    # Cerrado / MATOPIBA (onde os artigos mediram)
    "Bom Jesus-PI (Pacheco)": (-44.740, -9.280),
    "Brejo-MA (Andrade)": (-42.929, -3.712),
    "Urucui-PI": (-44.584, -7.407),
    "Balsas-MA": (-46.425, -8.437),
    "LEM-BA": (-46.139, -12.227),
    # sertao / semiarido
    "Quixada-CE": (-38.965, -4.940),
    "Taua-CE": (-40.292, -6.003),
    "Iguatu-CE": (-39.299, -6.359),
    "Crateus-CE": (-40.677, -5.178),
    "Sobral-CE": (-40.350, -3.689),
    "Ouricuri-PE": (-40.082, -7.883),
    "Serra Talhada-PE": (-38.296, -7.986),
    "Juazeiro-BA": (-40.267, -9.444),
    "Irece-BA": (-41.856, -11.304),
}
SERTAO = [k for k in PONTOS if k.split("-")[-1] in ("CE", "PE") or k in ("Juazeiro-BA", "Irece-BA")]

ARQ = DADOS / "imerg"
anos = range(1998, 2027)
lons = xr.DataArray([v[0] for v in PONTOS.values()], dims="p")
lats = xr.DataArray([v[1] for v in PONTOS.values()], dims="p")
pedacos = []
for a in anos:
    f = ARQ / f"imerg_ne_diario_{a}.nc"
    if not f.exists():
        continue
    with xr.open_dataset(f) as d:
        x = d["precip"].sel(lon=lons, lat=lats, method="nearest").load()
    pedacos.append(pd.DataFrame(x.values, index=pd.to_datetime(x["time"].values), columns=list(PONTOS)))
chuva = pd.concat(pedacos).sort_index()
chuva = chuva[~chuva.index.duplicated()].clip(lower=0)
print(f"IMERG NE diario: {chuva.index.min():%Y-%m-%d} a {chuva.index.max():%Y-%m-%d}, {len(chuva)} dias")


def soma(k, ini, fim):
    return float(chuva[k].loc[ini:fim].sum())


def inicio(k, ano):
    """Inicio agronomico da safra 'ano' (busca 1/set/ano-1 a 30/abr/ano)."""
    s = chuva[k].loc[f"{ano-1}-09-01":f"{ano}-05-31"]
    if len(s) < 200:
        return None
    v = s.values
    for i in range(len(v) - 33):
        if s.index[i] > pd.Timestamp(f"{ano}-04-30"):
            break
        if v[i:i + 3].sum() >= 20:
            seco = 0
            ok = True
            for x in v[i + 1:i + 31]:
                seco = seco + 1 if x < 1 else 0
                if seco >= 10:
                    ok = False
                    break
            if ok:
                return s.index[i]
    return None


# ---------------------------------------------------------------- A. ancoras de campo
print("\n== A. Ancoras dos artigos x IMERG ==")
k = "Brejo-MA (Andrade)"
print(f"  {k}: cobertura mai/2021-05/ago/2021 IMERG = {soma(k, '2021-05-01', '2021-08-05'):.0f} mm"
      f" (Andrade p.3: 353 mm; media historica 514 mm)")
print(f"  {k}: soja jan/2022-mai/2022 IMERG = {soma(k, '2022-01-01', '2022-05-31'):.0f} mm"
      f" (Andrade p.3: 1586 mm; media historica 1312 mm)")
k = "Bom Jesus-PI (Pacheco)"
print(f"  {k}: 30 d antes da colheita (15/mar-14/abr/2011) = {soma(k, '2011-03-15', '2011-04-14'):.0f} mm;"
      f" 30 d depois (16/abr-15/mai/2011) = {soma(k, '2011-04-16', '2011-05-15'):.0f} mm")
s11 = inicio(k, 2011)
print(f"  inicio agronomico IMERG safra 2010/11 em Bom Jesus: {s11:%d/%b/%Y} (soja semeada em 12/dez/2010 no artigo)")

# ---------------------------------------------------------------- B. janelas ancoradas no inicio local
linhas = []
for k in PONTOS:
    for ano in range(1999, 2026):
        S = inicio(k, ano)
        if S is None:
            linhas.append(dict(local=k, safra=ano, inicio=pd.NaT))
            continue
        Sp = inicio(k, ano + 1)
        d = lambda n: S + pd.Timedelta(days=n)  # noqa: E731
        r = dict(local=k, safra=ano, inicio=S,
                 ciclo=soma(k, d(0), d(124)),
                 sobre=soma(k, d(95), d(124)),
                 pos=soma(k, d(125), d(154)),
                 entre90=soma(k, d(125), d(214)))
        if Sp is not None and ano + 1 <= 2026:
            r["rebrota45"] = soma(k, Sp - pd.Timedelta(days=45), Sp - pd.Timedelta(days=1))
            r["entressafra_d"] = (Sp - d(125)).days
        linhas.append(r)
T = pd.DataFrame(linhas)

print("\n== B. Janelas ancoradas no inicio local das chuvas (safras 1999-2025; IMERG) ==")
print("  colunas: dia mediano do inicio | % anos sem inicio | mediana (mm) de: ciclo 125 d,"
      " sobressemeadura [S+95,S+124], pos-colheita [S+125,S+154], 90 d pos-colheita, 45 d pre-semeadura"
      " | % anos com sobre>=50 | % anos com pos>=50 | entressafra (d)")
res = []
for k, g in T.groupby("local", sort=False):
    ok = g.dropna(subset=["inicio"])
    doy = ok["inicio"].apply(lambda t: (t - pd.Timestamp(f"{t.year}-09-01")).days % 365)
    dia_med = (pd.Timestamp("2001-09-01") + pd.Timedelta(days=float(np.median(doy)))).strftime("%d/%b")
    r = dict(local=k, inicio_mediano=dia_med, sem_inicio=100 * g["inicio"].isna().mean(),
             ciclo=ok["ciclo"].median(), sobre=ok["sobre"].median(), pos=ok["pos"].median(),
             entre90=ok["entre90"].median(), rebrota45=ok["rebrota45"].median(),
             p_sobre50=100 * (ok["sobre"] >= 50).mean(), p_pos50=100 * (ok["pos"] >= 50).mean(),
             entressafra_d=ok["entressafra_d"].median(), n=len(ok))
    res.append(r)
    print(f"  {k:24s} {dia_med:>7s} {r['sem_inicio']:4.0f}% | ciclo {r['ciclo']:5.0f} sobre {r['sobre']:4.0f}"
          f" pos {r['pos']:4.0f} 90d {r['entre90']:4.0f} reb45 {r['rebrota45']:4.0f} | sobre>=50 {r['p_sobre50']:3.0f}%"
          f" pos>=50 {r['p_pos50']:3.0f}% | entressafra {r['entressafra_d']:4.0f} d (n={r['n']})")
R = pd.DataFrame(res).set_index("local")

# ---------------------------------------------------------------- C. leitura pre-declarada
print("\n== C. Leitura: sertao contra as ancoras do Cerrado ==")
bj = R.loc["Bom Jesus-PI (Pacheco)"]
br = R.loc["Brejo-MA (Andrade)"]
ser = R.loc[SERTAO]
print(f"  Bom Jesus: sobre mediana {bj.sobre:.0f} mm, pos {bj.pos:.0f} mm, 90 d pos-colheita {bj.entre90:.0f} mm")
print(f"  Brejo-MA : sobre mediana {br.sobre:.0f} mm, pos {br.pos:.0f} mm, 90 d pos-colheita {br.entre90:.0f} mm")
print(f"  Sertao (mediana das {len(ser)} medianas): ciclo {ser.ciclo.median():.0f} mm, sobre {ser.sobre.median():.0f} mm,"
      f" pos {ser.pos.median():.0f} mm, 90 d pos-colheita {ser.entre90.median():.0f} mm,"
      f" rebrota45 {ser.rebrota45.median():.0f} mm, sem inicio {ser.sem_inicio.median():.0f}% dos anos")
print(f"  Sertao: % anos com sobre>=50 mm (mediana entre locais) {ser.p_sobre50.median():.0f}%"
      f" vs Bom Jesus {bj.p_sobre50:.0f}% e Brejo {br.p_sobre50:.0f}%")
n_90 = (ser.entre90 >= 167).sum()
print(f"  Locais do sertao com 90 d pos-colheita >= 167 mm (menor lamina de Silva 2022): {n_90} de {len(ser)}")
print(f"  Locais do sertao com 90 d pos-colheita >= Andrade 2021 IMERG (ver A): ver tabela B")

# variabilidade: o que importa e o ano ruim
print("\n  p20 (ano ruim, 1 em 5) da janela de sobressemeadura (mm):")
for k in PONTOS:
    g = T[(T.local == k)].dropna(subset=["inicio"])
    print(f"    {k:24s} p20 sobre {np.percentile(g.sobre, 20):4.0f}  p20 ciclo {np.percentile(g.ciclo, 20):5.0f}"
          f"  p20 90d-pos {np.percentile(g.entre90, 20):4.0f}")

# ---------------------------------------------------------------- D. sensibilidade e estacao util
# Bom Jesus 2010/11: inicio IMERG 17/out, semeadura real 12/dez (atraso de 56 d). Fazendas atrasam;
# recalcula as janelas com atraso de 30 e 56 d (pre-declarado) para ver se a leitura muda.
print("\n== D1. Sensibilidade: semeadura = inicio + atraso (mediana mm da janela de sobressemeadura / pos-colheita) ==")
for atraso in (0, 30, 56):
    out = []
    for k in PONTOS:
        v1, v2 = [], []
        for ano in range(1999, 2026):
            S = inicio(k, ano)
            if S is None:
                continue
            S = S + pd.Timedelta(days=atraso)
            v1.append(soma(k, S + pd.Timedelta(days=95), S + pd.Timedelta(days=124)))
            v2.append(soma(k, S + pd.Timedelta(days=125), S + pd.Timedelta(days=154)))
        out.append(f"{k.split(' ')[0][:10]}:{np.median(v1):.0f}/{np.median(v2):.0f}")
    print(f"  atraso {atraso:2d} d -> " + "  ".join(out))

# estacao util: dias entre 10% e 90% da chuva do ano agricola (set-ago), sem calendario
print("\n== D2. Estacao util (dias entre 10% e 90% da chuva do ano agricola set-ago), mediana 1998/99-2024/25 ==")
for k in PONTOS:
    L, tot = [], []
    for ano in range(1999, 2026):
        s = chuva[k].loc[f"{ano-1}-09-01":f"{ano}-08-31"]
        if len(s) < 360 or s.sum() <= 0:
            continue
        c = s.cumsum() / s.sum()
        d10 = c.index[np.argmax(c.values >= 0.10)]
        d90 = c.index[np.argmax(c.values >= 0.90)]
        L.append((d90 - d10).days)
        tot.append(s.sum())
    print(f"  {k:24s} estacao util mediana {np.median(L):4.0f} d (p20 {np.percentile(L, 20):4.0f} d)"
          f" | chuva anual mediana {np.median(tot):5.0f} mm")
