"""Percolacao de pragas na paisagem: conectividade dos hospedeiros no espaco e "ponte verde" no tempo.

Dados (30 m):
- EUA: CDL por tipo de cultura (2023-2025) nas 6 janelas de 40 km (estudo_cdl/recortes).
- Ceara: lavoura (classe 5) do Impact Observatory/Esri LULC anual 10 m (2017-2023, Planetary Computer), reamostrada
  para 30 m em janelas de 40 km nas 4 AOIs.
Metricas por janela e ano:
- p = fracao de hospedeiro; S0 = fracao do hospedeiro no maior aglomerado (8 vizinhos); 'atravessa' = o maior
  aglomerado toca dois lados opostos da janela (percolacao de fato).
- Raio de dispersao r (0, 300 m, 1 km, 5 km): dois pixels de hospedeiro se conectam se estao a <= r; S(r).
- Ponte verde: hospedeiro no ano t E no ano t+1 (o que a rotacao quebra) -> p2, S2(r).
- Cenario de rotacao: retirar ao acaso uma fracao f dos talhoes da ponte verde -> S2(300 m) vs f (media de 10 sorteios).
Saidas: E:/campeonato-nasa/dados/percolacao/{metricas.csv, cenarios.csv, mascaras.npz}
Limiar teorico de percolacao por sitio em rede quadrada: p_c ~ 0,593 (4 vizinhos) e ~0,407 (8 vizinhos).
"""
import sys

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import rasterio  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402

from comum import AOIS, ESTUDO_CDL, pasta, registrar_manifesto  # noqa: E402

OUT = pasta("percolacao")
RES = 30.0
RAIOS = {"0 m": 0, "300 m": 300, "1 km": 1000, "5 km": 5000}
OITO = np.ones((3, 3), bool)
QUATRO = ndi.generate_binary_structure(2, 1)

HOSPEDEIROS_EUA = {  # janela: (nome do hospedeiro, codigos CDL, praga-modelo)
    "iowa_story": ("milho", [1], "larva-alfinete do milho (Diabrotica): ovos no milho, larva morre se o ano seguinte não for milho"),
    "kansas_ogallala": ("milho", [1], "larva-alfinete do milho"),
    "north_dakota_cass": ("milho", [1], "larva-alfinete do milho"),
    "mississippi_delta": ("soja", [5], "pragas e doenças de solo da soja"),
    "texas_lubbock": ("algodão", [2], "bicudo-do-algodoeiro (análogo ao Ceará dos anos 1980)"),
    "california_fresno": ("algodão", [2], "bicudo / pragas do algodão"),
}


def metricas(mask, r_m):
    """Fracao do hospedeiro no maior aglomerado conectado com raio de dispersao r e se ele atravessa a janela."""
    n = int(mask.sum())
    if n == 0:
        return 0.0, False, 0
    if r_m <= 0:
        lab, k = ndi.label(mask, structure=OITO)
    else:
        conect = ndi.distance_transform_edt(~mask) <= (r_m / RES) / 2  # dois pixels a <= r se ligam (cada um "cresce" r/2)
        lab, k = ndi.label(conect, structure=OITO)
        lab = np.where(mask, lab, 0)
    tam = np.bincount(lab.ravel())[1:]
    g = int(np.argmax(tam)) + 1
    gm = lab == g
    atravessa = (gm[0].any() and gm[-1].any()) or (gm[:, 0].any() and gm[:, -1].any())
    return float(tam.max() / n), bool(atravessa), int(k)


def cenario_rotacao(ponte, r_m=300, fracs=(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9), reps=10, semente=7):
    """Retira ao acaso uma fracao f dos talhoes (componentes 4-conexos) da ponte verde e mede S(r)."""
    lab, k = ndi.label(ponte, structure=QUATRO)
    rng = np.random.default_rng(semente)
    linhas = []
    for f in fracs:
        vals = []
        for _ in range(reps if 0 < f < 1 else 1):
            fora = rng.random(k + 1) < f
            fora[0] = True
            m = ~fora[lab] & ponte
            vals.append(metricas(m, r_m)[0] * m.sum() / max(ponte.sum(), 1))  # aglomerado gigante em % da ponte original
        linhas.append({"f_talhoes_rotacionados": f, "gigante_pct_ponte_original": float(np.mean(vals)), "dp": float(np.std(vals))})
    return linhas


def janela_cdl(reg, ano):
    with rasterio.open(ESTUDO_CDL / "recortes" / f"{reg}_{ano}.tif") as r:
        return r.read(1)


def janela_ceara(nome, ano, meia=0.18):
    import planetary_computer
    import pystac_client
    from rasterio.merge import merge
    from rasterio.vrt import WarpedVRT
    lon, lat, _ = AOIS[nome]
    b = (lon - meia, lat - meia, lon + meia, lat + meia)
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace)
    its = [i for i in cat.search(collections=["io-lulc-annual-v02"], bbox=list(b), datetime=f"{ano}-01-01/{ano}-12-31").items()
           if i.id.startswith("24")]
    vrts = [WarpedVRT(rasterio.open(i.assets["data"].href), crs="EPSG:4326", resampling=rasterio.enums.Resampling.nearest) for i in its]
    passo = RES / 111320.0
    arr, _ = merge(vrts, bounds=b, res=(passo, passo), nodata=0, resampling=rasterio.enums.Resampling.nearest)
    for v in vrts:
        v.close()
    return arr[0]


def main():
    linhas, cenarios, guardar = [], [], {}
    # --- EUA ---
    for reg, (host, cods, praga) in HOSPEDEIROS_EUA.items():
        anos = [2023, 2024, 2025]
        m = {a: np.isin(janela_cdl(reg, a), cods) for a in anos}
        for a in anos:
            for rot, r in RAIOS.items():
                s, at, k = metricas(m[a], r)
                linhas.append({"regiao": reg, "pais": "EUA", "hospedeiro": host, "praga_modelo": praga, "camada": "hospedeiro no ano",
                               "ano": a, "raio": rot, "p": float(m[a].mean()), "S": s, "atravessa": at, "n_aglomerados": k})
        for a in anos[:-1]:
            ponte = m[a] & m[a + 1]
            for rot, r in RAIOS.items():
                s, at, k = metricas(ponte, r)
                linhas.append({"regiao": reg, "pais": "EUA", "hospedeiro": host, "praga_modelo": praga, "camada": "ponte verde (t e t+1)",
                               "ano": a, "raio": rot, "p": float(ponte.mean()), "S": s, "atravessa": at, "n_aglomerados": k})
        ponte = m[2024] & m[2025]
        for c in cenario_rotacao(ponte):
            cenarios.append({"regiao": reg, "hospedeiro": host, **c})
        guardar[f"{reg}_2025"] = m[2025][::3, ::3]
        guardar[f"{reg}_ponte_2024_25"] = ponte[::3, ::3]
        print(reg, "ok", flush=True)
    # --- Ceara ---
    for nome in AOIS:
        anos = list(range(2017, 2024))
        m = {}
        for a in anos:
            m[a] = janela_ceara(nome, a) == 5
        for a in anos:
            for rot, r in RAIOS.items():
                s, at, k = metricas(m[a], r)
                linhas.append({"regiao": nome, "pais": "Brasil (Ceará)", "hospedeiro": "lavoura (qualquer)", "praga_modelo": "pragas generalistas de lavoura",
                               "camada": "hospedeiro no ano", "ano": a, "raio": rot, "p": float(m[a].mean()), "S": s, "atravessa": at, "n_aglomerados": k})
        for a in anos[:-1]:
            ponte = m[a] & m[a + 1]
            for rot, r in RAIOS.items():
                s, at, k = metricas(ponte, r)
                linhas.append({"regiao": nome, "pais": "Brasil (Ceará)", "hospedeiro": "lavoura (qualquer)", "praga_modelo": "pragas generalistas de lavoura",
                               "camada": "ponte verde (t e t+1)", "ano": a, "raio": rot, "p": float(ponte.mean()), "S": s, "atravessa": at, "n_aglomerados": k})
        ponte = m[2022] & m[2023]
        for c in cenario_rotacao(ponte):
            cenarios.append({"regiao": nome, "hospedeiro": "lavoura (qualquer)", **c})
        guardar[f"{nome}_2023"] = m[2023][::3, ::3]
        guardar[f"{nome}_ponte_2022_23"] = ponte[::3, ::3]
        print(nome, "ok", flush=True)
    pd.DataFrame(linhas).to_csv(OUT / "metricas.csv", index=False)
    pd.DataFrame(cenarios).to_csv(OUT / "cenarios.csv", index=False)
    np.savez_compressed(OUT / "mascaras_90m.npz", **guardar)
    registrar_manifesto("percolacao", {
        "fonte": "Derivado: USDA CDL 2023-2025 (EUA) e Impact Observatory/Esri LULC anual v02 2017-2023 (Ceará, Planetary Computer)",
        "metodo": __doc__.strip()[:900], "janelas_km": 40, "resolucao_m": RES, "raios": list(RAIOS)})
    print("gravado em", OUT)


if __name__ == "__main__":
    main()
