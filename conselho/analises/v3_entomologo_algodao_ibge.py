"""Entomologo (v3), teste 2: o algodao do Ceara e do Nordeste no IBGE (PAM) contra o que os artigos de pragas afirmam.

PRE-REGISTRO (escrito antes de rodar):
- Afirmacoes a conferir (lidas no texto):
  (1) Mattos et al. 2020 (Desenvolv. Meio Ambiente 55:556), secao 2.2: "ate os anos 1970, a area cultivada chegou a ser
      superior a dois milhoes e meio de hectares" (algodao do semiarido nordestino).
  (2) Mattos et al. 2020: o bicudo, "ja em 1983", inicia uma "nova era sem o algodao"; mas a seca de 1980-83 e o mercado
      tambem pesaram ("o bicudo foi apenas uma delas"). Azambuja & Degrande 2014: bicudo no Nordeste em jul/1983 (PB).
  (3) Mattos et al. 2020, secao 3: a Esplar levou o algodao agroecologico de Taua para Choro, Quixada e Massape;
      "apos uma decada" ~200 familias e "area total menor que 200 ha" (Lima et al. 2005).
- Teste de causa (rapido, nao causal): se a seca de 1980-83 explicasse tudo, a area deveria voltar nos anos muito
  chuvosos de 1984-86 (POWER). Se nao voltou, ha outro fator (bicudo, mercado, credito).
- Dados: IBGE PAM (SIDRA 1612/1613) por UF do NE e por municipio do CE, 1974-2025; NASA POWER CE mensal (chuva).
- Algodao arboreo (moco, perene) e herbaceo (anual) separados; area colhida (ha).
Somente le arquivos. Saida: v3_entomologo_algodao_ibge.saida.txt
"""
import sys

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
from comum import *  # noqa: F401,F403

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).with_suffix(".saida.txt")
LIN = []


def out(s=""):
    print(s)
    LIN.append(str(s))


ne = pd.read_parquet(DADOS / "ibge_pam" / "pam_ne_estados.parquet")
ne = ne[ne.produto.str.contains("lgod") & ne.variavel.str.contains("rea colhida")]
ne["tipo_alg"] = np.where(ne.produto.str.contains("arb"), "arboreo", "herbaceo")
tab = ne.pivot_table(index="ano", columns="local", values="valor", aggfunc="sum")
tot = tab.sum(axis=1)
out("== A. Area colhida de algodao (arboreo + herbaceo) no Nordeste, IBGE PAM por UF ==")
out(f"  maximo do NE: {tot.max():,.0f} ha em {tot.idxmax()}; media 1974-1979: {tot.loc[1974:1979].mean():,.0f} ha")
out(f"  NE sem a Bahia, 1974-1979: {tot.loc[1974:1979].mean() - tab.loc[1974:1979].filter(like='Bahia').sum(axis=1).mean():,.0f} ha")
for a in (1974, 1977, 1980, 1982, 1983, 1985, 1987, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025):
    ce = tab.loc[a].filter(like="Cear").sum()
    ba = tab.loc[a].filter(like="Bahia").sum()
    out(f"  {a}: NE {tot.loc[a]:>11,.0f} ha | Ceara {ce:>11,.0f} ({100 * ce / tot.loc[a]:4.1f}%) | Bahia {ba:>11,.0f}")
out("  [Mattos: '> 2,5 milhoes de ha' ate os anos 1970 no semiarido; o PAM so comeca em 1974]")

mun = pd.read_parquet(DERIV / "ibge_pam_mun_anual.parquet")
alg = mun[mun.produto.str.contains("lgod")].copy()
alg["tipo_alg"] = np.where(alg.produto.str.contains("arb"), "arboreo", "herbaceo")
ce = alg.groupby(["ano", "tipo_alg"])[["area_colhida_ha", "producao_t"]].sum().unstack()
area = ce["area_colhida_ha"]
prod = ce["producao_t"]
rend = (prod * 1000 / area.replace(0, np.nan))

pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw = pw[pw.variavel == "PRECTOTCORR"].copy()
pw["data"] = pd.to_datetime(pw.data)
pw["mm"] = pw.valor  # conferido contra o diario: o valor ja e o total do mes (o rotulo 'mm/day/mes' engana)
chuva = pw.groupby(pw.data.dt.year).mm.sum()
fm = pw[pw.data.dt.month.isin([2, 3, 4, 5])].groupby(pw.data.dt.year).mm.sum()
norm_fm = fm.loc[1981:2010].median()

out("\n== B. Ceara, 1974-1995: algodao no PAM e chuva NASA POWER (media do estado) ==")
out("  ano | arboreo ha | herbaceo ha | total ha | rend. arb kg/ha | rend. herb kg/ha | chuva ano mm | fev-mai % mediana")
for a in range(1974, 1996):
    ch = f"{chuva.get(a, np.nan):7.0f}" if a in chuva.index else "      -"
    fr = f"{100 * fm.get(a, np.nan) / norm_fm:6.0f}" if a in fm.index else "     -"
    out(f"  {a} | {area.loc[a, 'arboreo']:>10,.0f} | {area.loc[a, 'herbaceo']:>11,.0f} | {area.loc[a].sum():>8,.0f} | "
        f"{rend.loc[a, 'arboreo']:>15.0f} | {rend.loc[a, 'herbaceo']:>16.0f} | {ch} | {fr}")
pre = area.loc[1974:1982].sum(axis=1).mean()
for p0, p1 in [(1984, 1986), (1987, 1990), (1991, 2000), (2001, 2010), (2011, 2025)]:
    m = area.loc[p0:p1].sum(axis=1).mean()
    out(f"  media {p0}-{p1}: {m:,.0f} ha = {100 * m / pre:5.1f}% da media 1974-1982 ({pre:,.0f} ha)")
out(f"  rendimento arboreo 1974-1982: {rend.loc[1974:1982, 'arboreo'].mean():.0f} kg/ha; 1984-1990: "
    f"{rend.loc[1984:1990, 'arboreo'].mean():.0f} kg/ha")
out(f"  rendimento herbaceo 1974-1982: {rend.loc[1974:1982, 'herbaceo'].mean():.0f} kg/ha; 1984-1990: "
    f"{rend.loc[1984:1990, 'herbaceo'].mean():.0f} kg/ha")
out(f"  chuva POWER CE: 1981-1983 media {chuva.loc[1981:1983].mean():.0f} mm; 1984-1986 media "
    f"{chuva.loc[1984:1986].mean():.0f} mm; mediana 1981-2010 {chuva.loc[1981:2010].median():.0f} mm")

out("\n== C. Municipios da Esplar (Mattos et al. 2020): area colhida de algodao (arb + herb), ha ==")
alvo = ["Tau", "Chor", "Quixad", "Massap"]
sel = alg[alg.local.str.match(r"^(Tau|Chor[^o]|Quixad|Massap)")]
t = sel.groupby(["ano", "local"]).area_colhida_ha.sum().unstack().fillna(0)
t.columns = [c.split(" - ")[0].encode("ascii", "replace").decode() for c in t.columns]
t["soma"] = t.sum(axis=1)
out(t.loc[1994:2012].round(0).astype(int).to_string())
out(f"  soma 2003-2007 (media): {t.loc[2003:2007, 'soma'].mean():.0f} ha  [Mattos/Lima et al. 2005: Esplar < 200 ha]")

out("\n== D. Hospedeiro visivel hoje: municipios do CE com algodao colhido > 0 ==")
for p0, p1 in [(1974, 1982), (1995, 2000), (2015, 2019), (2020, 2025)]:
    g = alg[(alg.ano >= p0) & (alg.ano <= p1)].groupby("local").area_colhida_ha.sum()
    out(f"  {p0}-{p1}: {(g > 0).sum()} de 184 municipios tiveram algodao em algum ano; "
        f"arboreo (moco) colhido no periodo: {alg[(alg.ano >= p0) & (alg.ano <= p1) & (alg.tipo_alg == 'arboreo')].area_colhida_ha.sum():,.0f} ha")
g = alg[alg.ano >= 2020].groupby("local").area_colhida_ha.mean().sort_values(ascending=False)
out("  maiores areas medias 2020-2025: " + "; ".join(f"{k.split(' - ')[0].encode('ascii', 'replace').decode()} {v:.0f} ha"
                                                    for k, v in g.head(8).items()))
q = alg[(alg.ano >= 2020) & alg.local.str.startswith("Quixad")].groupby("ano").area_colhida_ha.sum()
out(f"  Quixada 2020-2025: {q.to_dict()}")
out("  [o arboreo zera no PAM, mas Mattos et al. descrevem o moco persistindo em capoeiras abandonadas: hospedeiro"
    " invisivel para o IBGE e para mapas de cobertura]")

OUT.write_text("\n".join(LIN), encoding="utf-8")
