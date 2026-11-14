"""Engenheiro de viabilidade (banca adversaria), rodada 2: o MVP da v2 cabe em ~36 h?

So le arquivos ja salvos (nada e gravado no projeto). Blocos:
 A. Inventario dos insumos do exportador citados na secao 10 da v2: existe? forma? periodo? tempo de leitura?
    Consistencia de codigos de municipio entre GeoJSON, SMAP, chuva, PAM, ZARC sintetico e carteira.
 B. Prototipo cronometrado do "exportador minimo" (copia da receita do arquiteto, nao importa): duas luzes em
    19/mar e 30/abr para 184 municipios x 2016-2025 e luz de chuva 1998-2025. Confere o 9 / 64 / 90 de 127 (2016),
    2021 (81 alertas, 3 quebras), 2025 (1 contra 21 de 45) e o placar de Quixada (19/mar 8 alertas e 2 acertos;
    30/abr 7 e 3). Se bater, o bloco 1 da secao 10 (4,5 h) e quase so serializacao.
 C. Painel "hoje": quais numeros saem em segundos dos arquivos prontos (SMAP 10/11/2026, posto entre novembros,
    VIIRS out/2026, GRACE, CLSM) e quais exigem conta nova (chuva da estacao seca: o cache municipal termina em 14/09).
 D. Tamanho do pacote estatico: GeoJSON e JSON por municipio em 3 desenhos (so portoes; serie diaria do ano; serie
    diaria completa). Decide o que cabe em "Quixada carrega em < 2 s no celular".
 E. Densidade de numeros nos 7 slides (secao 11.1) e no video (11.2): conta tokens numericos por slide.
 F. Orcamento: soma da tabela da secao 10 contra o relogio de parede (agora -> dom 23:59, menos o sono obrigatorio).
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

import json
import re
import time
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
pd.set_option("display.width", 220)

D = "E:/campeonato-nasa/dados/derivados/"
R = "E:/campeonato-nasa/dados/referencia/"
A = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/conselho/analises/"
P = r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/proposta/PROPOSTA_FINAL_v2.md"
QXD = "2311306"

print("=" * 20, "A. Inventario dos insumos do exportador (secao 10 da v2)", "=" * 20)
ins = {
    "agronomo_zarc_sintetico_prob": A + "saidas/agronomo_zarc_sintetico_prob.parquet",
    "agronomo_isna_mun_ano": A + "saidas/agronomo_isna_mun_ano.parquet",
    "hidrologo_fao56_mun_ano": A + "saidas/hidrologo_fao56_mun_ano.parquet",
    "v2_hidrologo_smap_pctl_mun_diario": A + "saidas/v2_hidrologo_smap_pctl_mun_diario.parquet",
    "v2_hidrologo_smap_rz_mun_diario": A + "saidas/v2_hidrologo_smap_rz_mun_diario.parquet",
    "estrategista_cache_chuva_mun_diaria": A + "estrategista_cache_chuva_mun_diaria.parquet",
    "carteira_cvar_municipios": A + "saidas/carteira_cvar_municipios.parquet",
    "ibge_pam_mun_anual": D + "ibge_pam_mun_anual.parquet",
    "viirs_ndvi_ce_mensal": D + "viirs_ndvi_ce_mensal.parquet",
    "v2_ecologo_painel_mun_mes": A + "saidas/v2_ecologo_painel_mun_mes.parquet",
}
T = {}
for k, f in ins.items():
    t0 = time.time()
    if not Path(f).exists():
        print(f"  {k:<38} AUSENTE")
        continue
    x = pd.read_parquet(f)
    T[k] = x
    per = ""
    if isinstance(x.index, pd.DatetimeIndex):
        per = f"{x.index.min():%Y-%m-%d} -> {x.index.max():%Y-%m-%d}"
    elif "ano" in x.columns:
        per = f"anos {x.ano.min()}-{x.ano.max()}"
    elif "data" in x.columns:
        per = f"{pd.to_datetime(x.data).min():%Y-%m} -> {pd.to_datetime(x.data).max():%Y-%m}"
    elif "mes" in x.columns:
        per = f"{pd.to_datetime(x.mes).min():%Y-%m} -> {pd.to_datetime(x.mes).max():%Y-%m}"
    print(f"  {k:<38} {Path(f).stat().st_size / 1e6:6.2f} MB | forma {str(x.shape):<14} | {per:<26} | leitura {time.time() - t0:.2f} s")

geo = json.load(open(R + "ceara_municipios.geojson", encoding="utf-8"))
nomes = json.load(open(R + "ceara_municipios_nomes.json", encoding="utf-8"))
cod_geo = {f["properties"]["codarea"] for f in geo["features"]}
cod_smap = set(T["v2_hidrologo_smap_pctl_mun_diario"].columns.astype(str))
cod_chuva = set(T["estrategista_cache_chuva_mun_diaria"].columns.astype(str))
cod_zarc = set(T["agronomo_zarc_sintetico_prob"].index.astype(str))
cart = T["carteira_cvar_municipios"]
cod_cart = set(cart.cod.astype(str))
print(f"\n  codigos: GeoJSON {len(cod_geo)} | SMAP {len(cod_smap)} | chuva {len(cod_chuva)} | ZARC sintetico {len(cod_zarc)} | "
      f"carteira (CVaR) {len(cod_cart)}")
print(f"  GeoJSON == SMAP: {cod_geo == cod_smap} | GeoJSON == chuva: {cod_geo == cod_chuva} | GeoJSON == ZARC: {cod_geo == cod_zarc}")
print(f"  Quixada ({QXD}) na carteira CVaR: {QXD in cod_cart}; municipios SEM carteira: {len(cod_geo - cod_cart)} de {len(cod_geo)}")
print(f"  colunas da carteira: {list(cart.columns)}")
if QXD in cod_cart:
    print("  Quixada na carteira:\n    " + cart[cart.cod.astype(str) == QXD].round(3).to_string(index=False).replace("\n", "\n    "))
print(f"  tipo do arquivo de nomes: {type(nomes).__name__}, {len(nomes)} itens; exemplo: {str(list(nomes.items())[:1] if isinstance(nomes, dict) else nomes[:1])[:160]}")

print("\n" + "=" * 20, "B. Prototipo cronometrado do exportador minimo (duas luzes)", "=" * 20)
t0 = time.time()
pam = T["ibge_pam_mun_anual"]
p = pam[pam["produto"].str.startswith("Milho (em gr")].copy()
p = p[(p.ano >= 1998) & (p.ano <= 2025) & (p.area_plantada_ha >= 50)]
p = p.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
p["r"] = p.producao_t / p.area_plantada_ha


def med_outros(g):
    v = g["r"].values
    return pd.Series([np.median(np.delete(v, i)) if len(v) > 5 else np.nan for i in range(len(v))], index=g.index)


p["ref"] = p.groupby("cod_local", group_keys=False).apply(med_outros)
p["razao"] = p.r / p.ref
p["quebra"] = (p.razao < 0.5).astype(int)
p["cod"] = p.cod_local.astype(str).str[:7]
base = p.dropna(subset=["razao"])[["cod", "ano", "quebra", "razao"]]
chuva = T["estrategista_cache_chuva_mun_diaria"]
chuva.columns = chuva.columns.astype(str)
ANOS = list(range(1998, 2026))
PC = T["v2_hidrologo_smap_pctl_mun_diario"]
PC.columns = PC.columns.astype(str)


def pct_normal(m, d):
    ac = pd.DataFrame({a: chuva.loc[f"{a}-01-01":f"{a}-{m:02d}-{d:02d}"].sum() for a in ANOS}).T
    out = ac.copy() * np.nan
    for a in ANOS:
        out.loc[a] = ac.loc[a] / ac.drop(index=a).median()
    return out.stack().rename("pct").reset_index().rename(columns={"level_0": "ano", "level_1": "cod"})


saida = {}
for gn, (m, d) in {"19/mar": (3, 19), "30/abr": (4, 30)}.items():
    pl = pct_normal(m, d)
    linhas = []
    for a in range(2016, 2026):
        t = pd.Timestamp(a, m, d)
        linhas.append(pd.DataFrame({"ano": a, "cod": PC.columns, "p_dia": PC.loc[t].values,
                                    "p_7d": PC.loc[t - pd.Timedelta(days=6):t].mean().values}))
    sm = pd.concat(linhas)
    tudo = base.merge(pl, on=["cod", "ano"], how="left").merge(sm, on=["cod", "ano"], how="left")
    saida[gn] = tudo
    df = tudo[tudo.ano.between(2016, 2025)].dropna(subset=["pct", "p_dia", "p_7d"])
    q = df.quebra.astype(bool)
    for a in (2016, 2021, 2025):
        s = df.ano == a
        print(f"  [{gn} {a}] quebras {int(q[s].sum())} | chuva<75% pega {int((q & s & (df.pct < 0.75)).sum())} "
              f"(alertas {int((s & (df.pct < 0.75)).sum())}) | SMAP 7d<20 pega {int((q & s & (df.p_7d < 20)).sum())} "
              f"(alertas {int((s & (df.p_7d < 20)).sum())}) | SMAP dia<20 pega {int((q & s & (df.p_dia < 20)).sum())} "
              f"(alertas {int((s & (df.p_dia < 20)).sum())})")
    qx = tudo[(tudo.cod == QXD) & tudo.pct.notna()]
    al = qx.pct < 0.75
    print(f"  [{gn}] Quixada, luz de chuva 1998-2025: {int(al.sum())} alertas, {int((al & (qx.quebra == 1)).sum())} acertos, "
          f"{int(qx.quebra.sum())} quebras; anos de quebra sem alerta: {qx[(qx.quebra == 1) & ~al].ano.tolist()}")
    qs = qx[qx.ano >= 2016].dropna(subset=["p_7d"])
    print(f"  [{gn}] Quixada, luz SMAP 7d<20 2016-2025: alertas {qs[qs.p_7d < 20].ano.tolist()}, "
          f"acertos {qs[(qs.p_7d < 20) & (qs.quebra == 1)].ano.tolist()}")
dt_b = time.time() - t0
print(f"  tempo total do bloco B (le, calcula quebra, chuva por portao, SMAP 7d, para 184 municipios): {dt_b:.1f} s")

# serializacao: JSON so de portoes por municipio (o que o Relogio e o placar precisam)
t0 = time.time()
pacote = {}
for cod in sorted(cod_geo):
    reg = {"cod": cod, "portoes": {}}
    for gn, tudo in saida.items():
        x = tudo[tudo.cod == cod].sort_values("ano")
        reg["portoes"][gn] = {
            "ano": x.ano.astype(int).tolist(),
            "quebra": x.quebra.astype(int).tolist(),
            "razao": x.razao.round(2).tolist(),
            "chuva_pct": x.pct.round(2).tolist(),
            "smap_7d": [None if pd.isna(v) else round(float(v), 1) for v in x.p_7d],
            "smap_dia": [None if pd.isna(v) else round(float(v), 1) for v in x.p_dia],
        }
    z = T["agronomo_zarc_sintetico_prob"]
    if cod in z.index.astype(str):
        reg["zarc"] = {k: round(float(v), 2) for k, v in z.loc[z.index.astype(str) == cod].iloc[0].items()}
    pacote[cod] = reg
tam = {c: len(json.dumps(v, ensure_ascii=False, separators=(",", ":"))) for c, v in pacote.items()}
print(f"  JSON de portoes + ZARC: {sum(tam.values()) / 1e3:.0f} kB para 184 municipios (Quixada {tam[QXD] / 1e3:.1f} kB); "
      f"montagem {time.time() - t0:.1f} s")

print("\n" + "=" * 20, "C. Painel 'hoje': o que sai pronto dos arquivos", "=" * 20)
RZ = T["v2_hidrologo_smap_rz_mun_diario"]
RZ.columns = RZ.columns.astype(str)
ult = RZ.index.max()
ce = RZ.mean(axis=1)
nov = ce[(ce.index.month == ult.month) & (ce.index.day == ult.day)]
posto = int((nov.rank(method="min")).loc[ult])
print(f"  SMAP zona da raiz: ultimo dia {ult:%Y-%m-%d}; CE {ce.loc[ult]:.3f} m3/m3; Quixada {RZ.loc[ult, QXD]:.3f}; "
      f"posto do CE no mesmo dia entre {len(nov)} anos = {posto}o mais seco")
pc_ult = PC.loc[ult]
print(f"  percentil do PRODUTO no ultimo dia: {pc_ult.notna().mean():.0%} dos municipios com valor (esperado: vazio)")
mes_vazio = PC.groupby(PC.index.month).apply(lambda x: x.notna().values.mean()).round(2)
print(f"  fracao de municipio-dias com percentil do produto, por mes: {mes_vazio.to_dict()}")
vi = T["viirs_ndvi_ce_mensal"].copy()
vi["data"] = pd.to_datetime(vi.data)
vi = vi[vi.variavel == "ndvi"].set_index("data").valor
print(f"  VIIRS NDVI do CE (derivado): ultimo mes {vi.index.max():%Y-%m}; out/2026 = "
      f"{vi.get(pd.Timestamp('2026-10-01'), np.nan):.3f}")
outs = vi[vi.index.month == 10]
if pd.Timestamp("2026-10-01") in outs.index:
    z = (outs.loc["2026-10-01"] - outs.drop(pd.Timestamp("2026-10-01")).mean()) / outs.drop(pd.Timestamp("2026-10-01")).std()
    print(f"  z do out/2026 contra os outros {len(outs) - 1} outubros (media e dp simples do derivado estadual): {z:+.2f}; "
          f"posto {int(outs.rank(ascending=False).loc['2026-10-01'])} de {len(outs)} (1 = mais verde)")
gr = pd.read_parquet(D + "grace_ce_mensal.parquet")
gr["data"] = pd.to_datetime(gr.data)
print(f"  GRACE CE: ultimo mes {gr.data.max():%Y-%m}; CLSM CE mensal: ultimo mes "
      f"{pd.to_datetime(pd.read_parquet(D + 'gldas_clsm_ce_mensal.parquet').data).max():%Y-%m}")
print(f"  chuva municipal diaria (cache): ultimo dia {chuva.index.max():%Y-%m-%d}. A 'estacao seca 01/ago-13/nov' exige o "
      f"IMERG Late/Early recente (nao esta no cache municipal): conta nova no exportador ou numero copiado da saida.")

print("\n" + "=" * 20, "D. Tamanho do pacote estatico", "=" * 20)
gtxt = Path(R + "ceara_municipios.geojson").read_text(encoding="utf-8")
ncoord = len(re.findall(r"\[-?\d+\.\d+,\s*-?\d+\.\d+\]", gtxt))
dec = re.findall(r"-?\d+\.(\d+)", gtxt[:20000])
print(f"  GeoJSON: {len(gtxt) / 1e3:.0f} kB, {len(geo['features'])} feicoes, ~{ncoord} pares de coordenadas, "
      f"~{np.median([len(x) for x in dec]):.0f} casas decimais (mediana)")
n_mun = len(cod_geo)
dias_ano = 365
b_val = 5  # bytes medios por valor serializado com 1 casa e virgula
print(f"  serie SMAP 7d de 1 ano (365 d) x {n_mun} mun.: ~{n_mun * dias_ano * b_val / 1e6:.2f} MB")
print(f"  serie SMAP completa ({len(PC)} d) x {n_mun} mun.: ~{n_mun * len(PC) * b_val / 1e6:.1f} MB")
print(f"  chuva diaria completa ({len(chuva)} d) x {n_mun} mun.: ~{n_mun * len(chuva) * b_val / 1e6:.1f} MB")
print(f"  trajetorias diarias so de 3 municipios x 3 anos x 365 d x 4 series: ~{3 * 3 * 365 * 4 * b_val / 1e3:.0f} kB")

print("\n" + "=" * 20, "E. Densidade de numeros nos slides e no video", "=" * 20)
txt = Path(P).read_text(encoding="utf-8")
s111 = txt.split("### 11.1 Os 7 slides")[1].split("### 11.2")[0]
blocos = re.split(r"\n(?=\d\. \*\*)", s111)
num = re.compile(r"(?<![A-Za-z])[+\-−]?\d+(?:[.,]\d+)?%?")
for b in blocos:
    mm = re.match(r"(\d)\. \*\*(.+?)\*\*", b.strip())
    if not mm:
        continue
    toks = [t for t in num.findall(b) if not re.fullmatch(r"\d", t) or True]
    toks = [t for t in toks if t not in {mm.group(1)}]
    print(f"  slide {mm.group(1)}: {len(toks):3d} tokens numericos | palavras {len(b.split()):4d} | {mm.group(2)[:70]}")
s112 = txt.split("### 11.2 Vídeo de 30 s")[1].split("**Como reproduzir")[0]
loc = re.findall(r"\| *\d+–\d+ s *\|[^|]*\|([^|]*)\|", s112)
pal = sum(len(x.split()) for x in loc)
print(f"  video 30 s: {pal} palavras de locucao (fala em ingles confortavel ~2,3-2,7 palavras/s -> "
      f"{pal / 2.7:.0f}-{pal / 2.3:.0f} s); numeros na locucao: {sorted(set(num.findall(' '.join(loc))))}")

print("\n" + "=" * 20, "F. Orcamento contra o relogio", "=" * 20)
s10 = txt.split("## 10. Plano de MVP")[1].split("**Decisões atrasadas")[0]
horas = []
for lin in s10.splitlines():
    mm = re.match(r"\| *([^|]+?) *\| *([\d,–]+) *\|", lin)
    if mm and mm.group(1) not in ("Tarefa",):
        v = mm.group(2).replace(",", ".")
        lo, hi = (v.split("–") + [v])[:2]
        horas.append((mm.group(1), float(lo), float(hi)))
lo = sum(h[1] for h in horas)
hi = sum(h[2] for h in horas)
agora = datetime.now()
prazo = datetime(2026, 11, 15, 23, 59)
parede = (prazo - agora).total_seconds() / 3600
print(f"  tarefas da tabela: {[h[0] for h in horas]}")
print(f"  soma da tabela: {lo:.1f}-{hi:.1f} h; com 25% de contingencia: {lo * 1.25:.1f}-{hi * 1.25:.1f} h-pessoa")
print(f"  agora {agora:%a %d/%m %H:%M}; prazo dom 15/11 23:59 -> {parede:.1f} h de parede; menos 6 h de sono e 2 h de folga "
      f"de submissao = {parede - 8:.1f} h uteis por pessoa (antes de refeicoes e de pausas)")
print(f"  1 pessoa: oferta ~{parede - 8:.0f} h contra demanda {lo:.0f}-{hi:.0f} h (sem contingencia)")
print(f"  2 pessoas: oferta ~{2 * (parede - 8):.0f} h contra {lo * 1.25:.0f}-{hi * 1.25:.0f} h com contingencia")

print("\n" + "=" * 20, "G. Cartoes S0-S3 por municipio: o que da para calcular", "=" * 20)
# receita copiada de arquiteto_final_carteira_ic.py (definicao canonica b): razao = r / mediana dos outros anos
pam2 = pam[(pam.ano >= 1998) & (pam.ano <= 2025)]


def canonica(pref):
    q = pam2[pam2.produto.str.startswith(pref) & (pam2.area_plantada_ha >= 50)]
    q = q.groupby(["cod_local", "ano"], as_index=False)[["producao_t", "area_plantada_ha"]].sum()
    q["r"] = q.producao_t / q.area_plantada_ha
    out = []
    for cod, g in q.sort_values(["cod_local", "ano"]).groupby("cod_local"):
        r = g.r.values
        med = np.array([np.median(np.delete(r, i)) if len(r) > 1 else np.nan for i in range(len(r))])
        out.append(pd.DataFrame({"cod_local": cod, "ano": g.ano.values, "razao": r / med}))
    return pd.concat(out).set_index(["cod_local", "ano"]).razao


Y = pd.DataFrame({"milho": canonica("Milho (em"), "feijao": canonica("Feij"), "mandioca": canonica("Mandioca")}).reset_index()
Y["cod"] = Y.cod_local.astype(str).str[:7]
n_m = Y.dropna(subset=["milho"]).groupby("cod").size()
n_3 = Y.dropna(subset=["milho", "feijao", "mandioca"]).groupby("cod").size()
print(f"  municipios com >= 20 anos de milho (S0 calculavel no municipio): {(n_m >= 20).sum()} de 184")
print(f"  municipios com >= 20 anos das 3 culturas juntas (S2 calculavel no municipio): {(n_3 >= 20).sum()} de 184; "
      f">= 10 anos: {(n_3 >= 10).sum()}")
qm = Y[(Y.cod == QXD)].dropna(subset=["milho"]).milho
print(f"  Quixada, S0 so milho ({len(qm)} anos): P(<0,5) {(qm < 0.5).mean():.3f} ({int((qm < 0.5).sum())} anos) | "
      f"'pior ano em 10' (media dos <= q10) {qm[qm <= qm.quantile(0.10)].mean():.3f} | mediana {qm.median():.3f}")
q3 = Y[(Y.cod == QXD)].dropna(subset=["milho", "feijao", "mandioca"])
print(f"  Quixada, anos com as 3 culturas: {len(q3)} ({q3.ano.tolist()}); com 10 anos o 'pior ano em 10' e UM ano so")
print("  S1 (escalonar) e S3 (leguminosa): sem metrica observada em nenhum municipio (grau C / faixa da literatura, secao 6.2)")
