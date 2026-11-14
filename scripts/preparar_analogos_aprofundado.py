"""Prepara os dados do notebook de aprofundamento (análogos, aptidão e ciclo de plantio).

Saídas em E:/campeonato-nasa/dados/analogos_aprofundado/:
- ceara_mun_assinaturas.csv : assinatura climática (NASA POWER) de cada um dos 184 municípios do Ceará (cache por célula do POWER)
- global_assinaturas.csv     : assinatura em pontos de terra de uma grade global de 6° (onde o clima se parece com o sertão)
- gaez_sitios.csv            : índice de aptidão GAEZ (sequeiro, insumo baixo e alto) de 15 culturas nos sítios dos artigos e no Ceará
- onset_sos_mun.csv          : por município e ano: início da estação pela chuva IMERG (regra agronômica) e início do verde pelo NDVI MODIS
- catalogo_cartao_lugar.csv e catalogo_lugares_assinaturas.csv : lugar de cada cartão de pesquisa/catalogo_rotacoes.json e a
                               assinatura climática (POWER) de cada lugar
Uso: python -I preparar_analogos_aprofundado.py [ceara] [global] [gaez] [ciclo] [catalogo]
"""
import json
import sys
import time

sys.path.insert(0, r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shapely  # noqa: E402
import xarray as xr  # noqa: E402

import analogos_climaticos_artigos as AC  # noqa: E402
from comum import DADOS, municipios_ce_gdf, pasta, registrar_manifesto, terra_gdf  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
OUT = pasta("analogos_aprofundado")


def nomes_mun():
    js = json.loads((DADOS / "referencia" / "ceara_municipios_nomes.json").read_text(encoding="utf-8"))
    return {str(m["id"]): (m["nome"], m["microrregiao"]["mesorregiao"]["nome"]) for m in js}


def ceara():
    mun = municipios_ce_gdf()
    nm = nomes_mun()
    cache, linhas = {}, []
    for _, m in mun.iterrows():
        c = m.geometry.representative_point()
        chave = (round(c.y * 2) / 2, round(c.x / 0.625) * 0.625)  # célula nativa do POWER (0,5° x 0,625°)
        if chave not in cache:
            time.sleep(0.6)
            cache[chave] = AC.assinatura(c.y, c.x)
        nome, meso = nm.get(str(m.codarea), ("?", "?"))
        linhas.append({"cod": str(m.codarea), "municipio": nome, "mesorregiao": meso, "lat": c.y, "lon": c.x, **cache[chave]})
    pd.DataFrame(linhas).to_csv(OUT / "ceara_mun_assinaturas.csv", index=False)
    print("ceara:", len(linhas), "municípios,", len(cache), "células POWER", flush=True)


def global_():
    terra = terra_gdf().union_all()
    pts = [(la, lo) for la in range(-48, 67, 6) for lo in range(-177, 178, 6) if shapely.contains_xy(terra, lo, la)]
    print("global:", len(pts), "pontos de terra", flush=True)
    linhas = []
    for k, (la, lo) in enumerate(pts, 1):
        time.sleep(0.6)
        try:
            linhas.append({"lat": la, "lon": lo, **AC.assinatura(la, lo)})
        except Exception as e:
            print("   falhou", la, lo, type(e).__name__, flush=True)
        if k % 50 == 0:
            print(f"   {k}/{len(pts)}", flush=True)
            pd.DataFrame(linhas).to_csv(OUT / "global_assinaturas.csv", index=False)
    pd.DataFrame(linhas).to_csv(OUT / "global_assinaturas.csv", index=False)


def gaez():
    import rasterio
    sel = pd.read_csv(DADOS / "gaez" / "selecao.csv")
    sel = sel[(sel.servico == "res05") & sel.variavel.str.startswith("Suitability index") & sel.variavel.str.contains("all land")]
    sit = pd.read_csv(DADOS / "analogos_artigos" / "assinaturas.csv")[["ponto", "grupo", "lat", "lon"]]
    linhas = []
    for _, r in sel.iterrows():
        with rasterio.open(DADOS / "gaez" / r.arquivo) as src:
            vals = [v[0] for v in src.sample(list(zip(sit.lon, sit.lat)))]
            nod = src.nodata
        for (_, s), v in zip(sit.iterrows(), vals):
            linhas.append({"ponto": s.ponto, "grupo": s.grupo, "cultura": r.cultura_pt, "insumo": r.input_level,
                           "SI": np.nan if (nod is not None and v == nod) or v < 0 else float(v) / 100})  # 0-100
    pd.DataFrame(linhas).to_csv(OUT / "gaez_sitios.csv", index=False)
    print("gaez:", len(sel), "camadas ×", len(sit), "sítios", flush=True)


def _indice_mun(lat, lon):
    """Para cada célula (lat, lon) da grade, o código do município que a contém (ou '' fora do Ceará)."""
    mun = municipios_ce_gdf()
    lo, la = np.meshgrid(lon, lat)
    idx = np.full(lo.shape, "", dtype=object)
    for _, m in mun.iterrows():
        idx[shapely.contains_xy(m.geometry, lo, la)] = str(m.codarea)
    return idx


def ciclo():
    # --- início da estação pela chuva (IMERG diário 0,1°) ---
    anos = range(1998, 2027)
    ds = xr.open_mfdataset([str(DADOS / "imerg" / f"imerg_ce_diario_{a}.nc") for a in anos], combine="by_coords")
    pr = ds.precip.load()
    idx = _indice_mun(pr.lat.values, pr.lon.values)
    cods = sorted(set(idx.ravel()) - {""})
    serie = {}
    flat = pr.values.reshape(pr.sizes["time"], -1)
    idf = idx.ravel()
    for c in cods:
        sel = idf == c
        if sel.sum() == 0:
            continue
        serie[c] = np.nanmean(flat[:, sel], axis=1)
    S = pd.DataFrame(serie, index=pd.to_datetime(pr.time.values))
    # regra agronômica (tipo Sivakumar): a partir de 1/dez, 1º dia com >= 20 mm em 3 dias e sem veranico de >= 10 dias secos (< 1 mm) nos 30 dias seguintes
    linhas = []
    for c in S.columns:
        x = S[c]
        for a in range(1999, 2027):
            jan = x[(x.index >= pd.Timestamp(a - 1, 12, 1)) & (x.index <= pd.Timestamp(a, 5, 31))]
            on = pd.NaT
            v = jan.values
            for i in range(len(v) - 32):
                if v[i:i + 3].sum() >= 20:
                    seco = v[i + 3:i + 33] < 1
                    corrida, maxc = 0, 0
                    for s_ in seco:
                        corrida = corrida + 1 if s_ else 0
                        maxc = max(maxc, corrida)
                    if maxc < 10:
                        on = jan.index[i]
                        break
            linhas.append({"cod": c, "ano": a, "inicio_chuva": on,
                           "chuva_fev_mai_mm": float(x[(x.index >= pd.Timestamp(a, 2, 1)) & (x.index <= pd.Timestamp(a, 5, 31))].sum())})
    R = pd.DataFrame(linhas)
    # --- início do verde (NDVI MODIS 16 dias, 0,01°) ---
    nd = xr.open_dataset(DADOS / "modis" / "mod13q1_ndvi_evi_ceara_001deg.nc").ndvi
    idx2 = _indice_mun(nd.lat.values, nd.lon.values).ravel()
    tempos = pd.to_datetime(nd.time.values)
    medias = {c: [] for c in R.cod.unique()}
    grupos = {c: np.where(idx2 == c)[0] for c in medias}
    for k in range(nd.sizes["time"]):
        a = nd.isel(time=k).values.ravel()
        for c, ii in grupos.items():
            medias[c].append(np.nanmean(a[ii]) if len(ii) else np.nan)
    N = pd.DataFrame(medias, index=tempos)
    sos = []
    for c in N.columns:
        x = N[c].dropna()
        for a in range(2001, 2027):
            jan = x[(x.index >= pd.Timestamp(a - 1, 10, 1)) & (x.index <= pd.Timestamp(a, 7, 31))]
            if len(jan) < 10:
                continue
            mn = jan[: pd.Timestamp(a, 1, 31)].min()
            mx = jan[pd.Timestamp(a, 2, 1):].max()
            lim = mn + 0.5 * (mx - mn)
            apos = jan[(jan.index >= pd.Timestamp(a - 1, 12, 1)) & (jan > lim)]
            sos.append({"cod": c, "ano": a, "inicio_verde": apos.index[0] if len(apos) else pd.NaT, "ndvi_pico": float(mx), "amplitude": float(mx - mn)})
    R = R.merge(pd.DataFrame(sos), on=["cod", "ano"], how="left")
    R.to_csv(OUT / "onset_sos_mun.csv", index=False)
    print("ciclo:", R.shape, flush=True)


# lugar de cada cartão do catálogo (pela coluna "onde"); a 1ª regra que casar vale. Regiões amplas ("Global", "África
# Subsaariana", "Caatinga", estratos) ficam sem ponto. Pontos marcados "aprox." representam uma região.
LUGARES = [
    (r"Pentecoste", "Pentecoste-CE", -3.79, -39.27), (r"Arapiraca", "Arapiraca-AL", -9.75, -36.66),
    (r"Crato", "Crato-CE", -7.23, -39.41), (r"Barbalha", "Barbalha-CE", -7.31, -39.30),
    (r"Mossoró", "Mossoró-RN", -5.19, -37.34), (r"Pesqueira", "Pesqueira-PE", -8.36, -36.70),
    (r"Alagoinha", "Alagoinha-PB", -6.95, -35.55), (r"Petrolina", "Petrolina-PE", -9.39, -40.50),
    (r"Serra Talhada", "Serra Talhada-PE", -7.99, -38.30), (r"Esperança", "Esperança-PB", -7.02, -35.86),
    (r"Taperoá", "Taperoá-PB", -7.21, -36.83), (r"Sobral", "Sobral-CE", -3.69, -40.35),
    (r"Lagoa Seca", "Lagoa Seca-PB", -7.17, -35.85), (r"Bom Jesus", "Bom Jesus-PI", -9.07, -44.36),
    (r"PI \(Aw\)", "Bom Jesus-PI", -9.07, -44.36), (r"Rio Verde", "Rio Verde-GO", -17.79, -50.92),
    (r"Brejo-MA", "Brejo-MA", -3.68, -42.75), (r"Planaltina", "Planaltina-DF", -15.60, -47.71),
    (r"Oeste da Bahia", "Oeste da Bahia (aprox.)", -12.15, -45.00), (r"^Goiás", "Goiás (aprox.)", -16.68, -49.25),
    (r"Mato Grosso do Sul", "Mato Grosso do Sul (aprox.)", -20.47, -54.62),
    (r"Mali, Níger|Sahel", "Sahel (Niamey, aprox.)", 13.51, 2.11), (r"Nigéria, Gana", "Savana da Guiné (Tamale, aprox.)", 9.40, -0.85),
    (r"Zimbábue", "África Austral (Harare, aprox.)", -17.83, 31.05), (r"Manica", "Manica-Moçambique", -18.94, 32.88),
    (r"África Oriental", "África Oriental seca (Machakos, aprox.)", -1.52, 37.26),
    (r"Luancheng", "Luancheng-China", 37.88, 114.69), (r"Akron", "Akron-EUA", 40.16, -103.21),
    (r"Elora|Ontário", "Elora-Ontário", 43.64, -80.41), (r"Planícies do norte|Pradarias do Canadá", "Pradarias (Regina, aprox.)", 50.45, -104.61),
    (r"IA, IL|IN, IA|Corn Belt|Meio-Oeste|^EUA", "Corn Belt (Ames, aprox.)", 42.03, -93.62),
    (r"Europa", "Europa temperada (Beauce, aprox.)", 48.20, 1.80),
]


def catalogo():
    """Lugar e assinatura climática (POWER) de cada cartão do catálogo de rotações com local identificável."""
    import re
    js =json.loads(open(r"c:\Users\netinhoklz\Projetos pessoais\campeonato-nasa\pesquisa\catalogo_rotacoes.json", encoding="utf-8").read())
    linhas, assin = [], {}
    sem_ponto = r"^Global|estudos \(|ensaios longos:|Oriental e Austral"  # várias regiões num cartão só
    for c in js["configuracoes"]:
        lugar = None if re.search(sem_ponto, c["onde"]) else next(((n, la, lo) for rx, n, la, lo in LUGARES if re.search(rx, c["onde"])), None)
        linhas.append({"id": c["id"], "lugar": lugar[0] if lugar else None})
        if lugar and lugar[0] not in assin:
            assin[lugar[0]] = {"lugar": lugar[0], "lat": lugar[1], "lon": lugar[2], **AC.assinatura(lugar[1], lugar[2])}
            time.sleep(0.5)
    pd.DataFrame(linhas).to_csv(OUT / "catalogo_cartao_lugar.csv", index=False)
    pd.DataFrame(assin.values()).to_csv(OUT / "catalogo_lugares_assinaturas.csv", index=False)
    print("catalogo:", sum(l["lugar"] is not None for l in linhas), "de", len(linhas), "cartões com lugar;", len(assin), "lugares", flush=True)


if __name__ == "__main__":
    tarefas = sys.argv[1:] or ["ceara", "gaez", "ciclo", "global", "catalogo"]
    for t in tarefas:
        {"ceara": ceara, "global": global_, "gaez": gaez, "ciclo": ciclo, "catalogo": catalogo}[t]()
    registrar_manifesto("analogos_aprofundado", {"fonte": "NASA POWER (climatologia), IMERG V07, MODIS MOD13Q1, FAO GAEZ v4, IBGE malhas",
                                                 "tarefas": tarefas, "saidas": [p.name for p in OUT.glob("*.csv")]})
