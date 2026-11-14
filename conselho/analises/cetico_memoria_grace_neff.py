"""Cetico 3: a "memoria hidrica de anos" (GRACE x chuva acumulada 36-48 meses, r ~ 0,47-0,49; secao 20.4)
sobrevive a um teste que respeita a autocorrelacao? E quantos eventos de seca independentes temos para validar?

Metodo:
  - mesmas series da secao 20.4: anomalia mensal da chuva POWER PRECTOTCORR (CE) acumulada em w meses x GRACE TWS (CE);
  - n efetivo de Bretherton et al. (1999): n_eff = n (1 - r1 r2) / (1 + r1 r2), com r1, r2 = autocorrelacoes lag-1;
  - teste de superficie aleatoria (surrogate) por randomizacao de fase da chuva mensal (preserva o espectro), 1000x,
    recalculando o acumulado e a correlacao -> p-valor empirico;
  - robustez: correlacao sem 2012-2017 (a seca longa domina);
  - contagem de anos secos (tercil inferior de fev-mai, POWER 1981-2026) e de "episodios" independentes (anos secos
    consecutivos contam como 1).
Dados: E:/campeonato-nasa/dados/derivados/power_ce_mensal.parquet, grace_ce_mensal.parquet
"""
import sys
import warnings

sys.path.insert(0, r"c:/Users/netinhoklz/Projetos pessoais/campeonato-nasa/scripts")
warnings.filterwarnings("ignore")
from comum import *  # noqa: F401,F403
from comum import DERIV

import numpy as np
import pandas as pd

pw = pd.read_parquet(DERIV / "power_ce_mensal.parquet")
pw["data"] = pd.to_datetime(pw.data).dt.to_period("M").dt.to_timestamp()
ch = pw[pw.variavel == "PRECTOTCORR"].set_index("data").valor.sort_index()
ch = ch[ch.index < "2026-11-01"]
if ch.mean() < 15:
    ch = ch * ch.index.days_in_month
gr = pd.read_parquet(DERIV / "grace_ce_mensal.parquet")
gr["data"] = pd.to_datetime(gr.data).dt.to_period("M").dt.to_timestamp()
gr = gr.set_index("data").valor.sort_index()


def anomalia(s):
    return s - s.groupby(s.index.month).transform("mean")


an = anomalia(ch)


def r_acc(anom, w, excluir=None):
    acc = anom.rolling(w).sum()
    j = pd.concat([acc.rename("a"), gr.rename("g")], axis=1).dropna()
    if excluir:
        j = j[(j.index.year < excluir[0]) | (j.index.year > excluir[1])]
    return j.a.corr(j.g), j


def surrogate(x, rng):
    f = np.fft.rfft(x - x.mean())
    fase = rng.uniform(0, 2 * np.pi, len(f))
    fase[0] = 0
    if len(x) % 2 == 0:
        fase[-1] = 0
    return np.fft.irfft(np.abs(f) * np.exp(1j * fase), n=len(x)) + x.mean()


rng = np.random.default_rng(0)
lin = []
for w in [12, 24, 36, 48]:
    r, j = r_acc(an, w)
    r1 = j.a.autocorr(1)
    r2 = j.g.autocorr(1)  # GRACE tem lacunas: autocorr no indice disponivel (aproximacao)
    n = len(j)
    neff = n * (1 - r1 * r2) / (1 + r1 * r2)
    nulos = []
    x = an.values
    for _ in range(1000):
        s = pd.Series(surrogate(x, rng), index=an.index)
        nulos.append(r_acc(s, w)[0])
    nulos = np.array(nulos)
    p_emp = (np.sum(np.abs(nulos) >= abs(r)) + 1) / (len(nulos) + 1)
    r_sem, j_sem = r_acc(an, w, excluir=(2012, 2017))
    lin.append({"janela_meses": w, "r": round(r, 3), "n_meses": n, "n_efetivo": round(neff, 1),
                "p_surrogate": round(p_emp, 3), "r_nulo_p95": round(np.quantile(np.abs(nulos), 0.95), 3),
                "r_sem_2012_2017": round(r_sem, 3), "n_sem": len(j_sem)})
print(pd.DataFrame(lin).to_string(index=False))

# anos secos e episodios independentes
q = ch[ch.index.month.isin([2, 3, 4, 5])]
cont = q.groupby(q.index.year).count()
fmam = q.groupby(q.index.year).sum()[cont == 4]
t1 = fmam.quantile(1 / 3)
secos = sorted(fmam[fmam <= t1].index.tolist())
ep = []
for a in secos:
    if ep and a - ep[-1][-1] == 1:
        ep[-1].append(a)
    else:
        ep.append([a])
print(f"\nPOWER fev-mai {fmam.index.min()}-{fmam.index.max()}: {len(fmam)} anos; tercil seco <= {t1:.0f} mm")
print(f"anos secos ({len(secos)}): {secos}")
print(f"episodios independentes (anos consecutivos = 1): {len(ep)} -> {ep}")
sec98 = [a for a in secos if a >= 1998]
ep98 = [e for e in ep if e[-1] >= 1998]
print(f"desde 1998 (periodo IMERG/PAM do painel): {len(sec98)} anos secos em {len(ep98)} episodios")
# El Nino forte (ONI out-jan >= 1,5) no registro: quantos casos para o alerta de 2027?
ix = pd.read_parquet(DERIV / "indices_clima_mensal.parquet")
ix["data"] = pd.to_datetime(ix.data)
oni = ix[ix.variavel == "ONI"].set_index("data").valor.sort_index()
casos = []
for ano in range(1982, 2027):
    jan = oni[(oni.index >= f"{ano-1}-10-01") & (oni.index <= f"{ano}-01-01")]
    if len(jan) == 4 and jan.mean() >= 1.5:
        casos.append((ano, round(jan.mean(), 2), round(float(fmam.get(ano, np.nan)), 0),
                      "seco" if fmam.get(ano, np.inf) <= t1 else ("chuvoso" if fmam.get(ano, -1) >= fmam.quantile(2 / 3) else "normal")))
print(f"\nanos com ONI out-jan >= 1,5 (El Nino forte) 1982-2026: {len(casos)}")
for c in casos:
    print("  ", c)
