"""v4 - Especialista Cerrado/MATOPIBA: le a Figura 3a de Andrade et al. 2025 (Agronomy 15:1083,
doi 10.3390/agronomy15051083, p. 8) em pixels para obter a produtividade da soja por cobertura,
porque o texto (p. 7) da so porcentagens (+19% a +22%) e a Tabela 3 mostra que os autores usam
(T - F)/T em vez de (T - F)/F (ex.: MBN feijao-guandu 2,13 vs pousio 0,23 = "+89%").
Entrada: PDF aberto do repositorio Alice/Embrapa, renderizado com pdftoppm (argumento 1 = PNG da p. 8).
Eixo x da figura: 2500 a 5000 kg/ha. Barras cinza-escuras; ponta direita = media (sem a barra de erro).
"""
import sys
import numpy as np
from PIL import Image

img = np.asarray(Image.open(sys.argv[1]).convert("L")).astype(int)
H, W = img.shape
# regiao do painel (a): metade superior da pagina
top = img[: int(H * 0.30)]
escuro = (top > 70) & (top < 130)          # cinza das barras (nao preto do texto)
linhas = np.where(escuro.sum(axis=1) > W * 0.05)[0]
# agrupa linhas consecutivas em barras
grupos, ini = [], linhas[0]
for a, b in zip(linhas[:-1], linhas[1:]):
    if b != a + 1:
        grupos.append((ini, a)); ini = b
grupos.append((ini, linhas[-1]))
grupos = [g for g in grupos if g[1] - g[0] >= 5]
nomes = ["C. juncea", "Pigeon pea", "Cowpea", "Massai", "Tanzania", "Ruziziensis", "Marandu", "Millet", "Fallow"]
print("barras encontradas:", len(grupos))
# ponta esquerda comum (valor 2500) e ponta direita de cada barra
esq, dirs = [], []
for (a, b) in grupos:
    # linhas proximas da borda da barra (a linha preta da barra de erro corre no centro);
    # ultimo pixel cinza de cada linha = ponta da barra
    ext = []
    for r in list(range(a + 1, a + 4)) + list(range(b - 3, b)):
        xs = np.where(escuro[r])[0]
        ext.append((xs.min(), xs.max()))
    esq.append(int(np.median([e[0] for e in ext]))); dirs.append(int(np.median([e[1] for e in ext])))
x2500 = int(np.median(esq))
# eixo: procurar a linha horizontal preta do eixo x abaixo das barras
abaixo = img[grupos[-1][1] + 5: int(H * 0.32)]
ln = np.argmax((abaixo < 60).sum(axis=1))
xs_eixo = np.where(abaixo[ln] < 60)[0]
x5000 = xs_eixo.max()
print(f"x(2500)={x2500}  x(5000)={x5000}  (largura {x5000 - x2500} px)")
vals = {}
for nome, xr in zip(nomes, dirs):
    v = 2500 + (xr - x2500) / (x5000 - x2500) * 2500
    vals[nome] = v
F = vals["Fallow"]
print(f"{'cobertura':12s} {'kg/ha':>6s} {'(T-F)/F':>8s} {'(T-F)/T':>8s}")
for nome in reversed(nomes):
    v = vals[nome]
    print(f"{nome:12s} {v:6.0f} {100*(v-F)/F:7.1f}% {100*(v-F)/v:7.1f}%")
