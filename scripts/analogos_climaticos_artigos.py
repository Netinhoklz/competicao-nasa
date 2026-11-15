"""Analogos climaticos entre os lugares dos artigos e o Ceara, com a climatologia do NASA POWER (qualquer ponto do planeta).

Assinatura por ponto (climatologia mensal do POWER, comunidade AG):
  chuva anual (mm), indice de sazonalidade de Walsh (0 = uniforme, > 1 = extremamente sazonal), meses com chuva >= ET0/2
  (estacao umida, proxy do periodo de crescimento), aridez anual (P/ET0, FAO-56 Penman-Monteith mensal), Tmax media da estacao
  umida, Tmax do mes mais quente.
Similaridade: distancia euclidiana nas variaveis padronizadas (z). Coordenadas dos sitios dos artigos sao APROXIMADAS (cidade
ou estacao experimental citada no artigo ou zona agroecologica).
Saidas: E:/campeonato-nasa/dados/analogos_artigos/{assinaturas.csv, distancias.csv}
"""
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # a pasta deste arquivo (scripts/), em qualquer máquina
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from comum import pasta, registrar_manifesto, sessao_http  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
OUT = pasta("analogos_artigos")
# (rotulo, lat, lon, grupo, artigos relacionados)
SITIOS = [
    ("Petrolina-PE", -9.39, -40.50, "Nordeste (artigos)", "Souza 2011; Souza 2015 (milho-caupi, Kc)"),
    ("Serra Talhada-PE", -7.99, -38.30, "Nordeste (artigos)", "Diniz 2017; Lima 2018 (palma-sorgo)"),
    ("Esperança-PB (Agreste)", -7.02, -35.86, "Nordeste (artigos)", "Pérez-Marin 2006 (gliricídia)"),
    ("Sobral-CE", -3.69, -40.35, "Nordeste (artigos)", "Sacramento 2013 (carbono do solo medido: agrossilvipastoril × broca e queima)"),
    ("Teresina-PI", -5.09, -42.80, "Nordeste (artigos)", "Santos 2026 (caupi sob déficit)"),
    ("Cerrado piauiense (Bom Jesus-PI, aprox.)", -9.07, -44.36, "Nordeste (artigos)", "Pacheco 2011/2013/2017 (coberturas, MATOPIBA)"),
    ("Zona sudano-saheliana (Niamey, aprox.)", 13.51, 2.11, "África (Franke 2018)", "Franke 2018 (zona sudano-saheliana)"),
    ("Savana da Guiné (Tamale, aprox.)", 9.40, -0.85, "África (Franke 2018)", "Franke 2018 (savana da Guiné)"),
    ("África Austral (Chitedze-Malawi, aprox.)", -13.97, 33.65, "África (Franke 2018)", "Franke 2018 (África Austral); Mudare 2022"),
    ("África Austral (Harare, aprox.)", -17.83, 31.05, "África (Franke 2018)", "Franke 2018 (África Austral)"),
    ("Planalto da África Oriental (Embu, aprox.)", -0.53, 37.45, "África (Franke 2018)", "Franke 2018 (planalto da África Oriental)"),
    ("Floresta úmida da África Ocidental (Ibadan, aprox.)", 7.38, 3.93, "África (Franke 2018)", "Franke 2018 (floresta úmida)"),
    ("Semiárido da Índia (Patancheru, aprox.)", 17.51, 78.27, "Ásia", "referência de semiárido tropical (sorgo, milheto, caupi)"),
    ("Iowa (Ames)", 42.03, -93.62, "EUA/Canadá/Europa/China (Kluger, Bowles)", "Kluger 2025; Bowles 2020; CDL"),
    ("Kansas sudoeste", 37.60, -100.90, "EUA/Canadá/Europa/China (Kluger, Bowles)", "Kluger 2025; CDL (Ogallala)"),
    ("Texas (Lubbock)", 33.60, -101.85, "EUA/Canadá/Europa/China (Kluger, Bowles)", "CDL: algodão contínuo semiárido"),
    ("Ontário (Elora)", 43.64, -80.41, "EUA/Canadá/Europa/China (Kluger, Bowles)", "Renwick 2021 (rotação e seca)"),
    ("França (Beauce, aprox.)", 48.20, 1.80, "EUA/Canadá/Europa/China (Kluger, Bowles)", "Kluger 2025"),
    ("Nordeste da China (Harbin, aprox.)", 45.75, 126.65, "EUA/Canadá/Europa/China (Kluger, Bowles)", "Kluger 2025"),
    ("Planície do Norte da China (aprox.)", 36.20, 116.90, "EUA/Canadá/Europa/China (Kluger, Bowles)", "Yang 2024"),
]
CEARA = [
    ("CE: Quixadá (Sertão Central)", -4.97, -39.02), ("CE: Tauá (Inhamuns)", -6.00, -40.29), ("CE: Crateús", -5.18, -40.67),
    ("CE: Iguatu (Centro-Sul)", -6.36, -39.30), ("CE: Juazeiro do Norte (Cariri)", -7.21, -39.32), ("CE: Limoeiro do Norte (Jaguaribe)", -5.15, -38.10),
    ("CE: Sobral (Norte)", -3.69, -40.35), ("CE: Tianguá (Ibiapaba)", -3.73, -40.99), ("CE: Itapipoca (Litoral Oeste)", -3.49, -39.58),
    ("CE: Fortaleza (Litoral)", -3.73, -38.53), ("CE: Russas (Baixo Jaguaribe)", -4.94, -37.98), ("CE: Baturité (serra úmida)", -4.33, -38.88),
]
PARAMS = "PRECTOTCORR,T2M_MAX,T2M_MIN,T2M,RH2M,WS2M,ALLSKY_SFC_SW_DWN"
MESES = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
DIAS = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
s = sessao_http(retries=4)


def et0_pm(tmean, tmax, tmin, rh, u2, rs_mj, z):
    """ET0 FAO-56 Penman-Monteith diaria (mm/dia) com dados medios mensais; Rnl simplificado com Rso ~ 0,75 Ra aprox. por Rs."""
    p = 101.3 * ((293 - 0.0065 * z) / 293) ** 5.26
    gama = 0.000665 * p
    es = lambda t: 0.6108 * math.exp(17.27 * t / (t + 237.3))
    es_m = (es(tmax) + es(tmin)) / 2
    ea = es_m * rh / 100
    delta = 4098 * es(tmean) / (tmean + 237.3) ** 2
    rns = 0.77 * rs_mj
    rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * math.sqrt(max(ea, 0.01))) * (1.35 * 0.75 - 0.35)
    rn = rns - rnl
    return (0.408 * delta * rn + gama * 900 / (tmean + 273) * u2 * (es_m - ea)) / (delta + gama * (1 + 0.34 * u2))


def tmax_tmin_medias(lat, lon, inicio="20010101", fim="20241231"):
    """Médias mensais da máxima e da mínima DIÁRIAS (2001–2024). Na climatologia do POWER, T2M_MAX e T2M_MIN são o
    extremo do mês (recorde), não a média: em Quixadá, janeiro dá 39,3 °C contra 34,9 °C de média (revisão C2, 14/11)."""
    r = s.get("https://power.larc.nasa.gov/api/temporal/daily/point",
              params={"parameters": "T2M_MAX,T2M_MIN", "community": "AG", "longitude": lon, "latitude": lat,
                      "start": inicio, "end": fim, "format": "JSON"}, timeout=180)
    r.raise_for_status()
    par = r.json()["properties"]["parameter"]
    out = {}
    for v in ("T2M_MAX", "T2M_MIN"):
        ser = pd.Series(par[v], dtype=float)
        ser.index = pd.to_datetime(ser.index, format="%Y%m%d")
        ser = ser.where(ser > -900)
        out[v] = ser.groupby(ser.index.month).mean().reindex(range(1, 13)).values
    return out


def assinatura(lat, lon):
    r = s.get("https://power.larc.nasa.gov/api/temporal/climatology/point",
              params={"parameters": PARAMS, "community": "AG", "longitude": lon, "latitude": lat, "format": "JSON"}, timeout=120)
    r.raise_for_status()
    j = r.json()
    par = j["properties"]["parameter"]
    z = j["geometry"]["coordinates"][2]
    tm = tmax_tmin_medias(lat, lon)  # máxima e mínima médias (não os recordes da climatologia)
    P = np.array([par["PRECTOTCORR"][m] * d for m, d in zip(MESES, DIAS)])
    et0 = np.array([et0_pm(par["T2M"][m], tm["T2M_MAX"][i], tm["T2M_MIN"][i], par["RH2M"][m], par["WS2M"][m],
                           par["ALLSKY_SFC_SW_DWN"][m], z) * d for i, (m, d) in enumerate(zip(MESES, DIAS))])
    tmax = np.asarray(tm["T2M_MAX"])
    umidos = P >= et0 / 2
    walsh = float(np.sum(np.abs(P - P.sum() / 12)) / P.sum()) if P.sum() > 0 else np.nan
    return {"chuva_anual_mm": round(float(P.sum()), 0), "sazonalidade_walsh": round(walsh, 2), "meses_umidos": int(umidos.sum()),
            "aridez_P_ET0": round(float(P.sum() / et0.sum()), 2), "tmax_estacao_umida": round(float(tmax[umidos].mean()) if umidos.any() else float(tmax.max()), 1),
            "tmax_mes_mais_quente": round(float(tmax.max()), 1), "et0_anual_mm": round(float(et0.sum()), 0), "altitude_m": round(z, 0)}


def main():
    linhas = []
    for rot, lat, lon, grupo, arts in SITIOS:
        time.sleep(0.8)
        linhas.append({"ponto": rot, "lat": lat, "lon": lon, "grupo": grupo, "artigos": arts, **assinatura(lat, lon)})
        print(linhas[-1]["ponto"], {k: linhas[-1][k] for k in ("chuva_anual_mm", "aridez_P_ET0", "meses_umidos", "sazonalidade_walsh")}, flush=True)
    for rot, lat, lon in CEARA:
        time.sleep(0.8)
        linhas.append({"ponto": rot, "lat": lat, "lon": lon, "grupo": "Ceará (alvo)", "artigos": "", **assinatura(lat, lon)})
        print(linhas[-1]["ponto"], {k: linhas[-1][k] for k in ("chuva_anual_mm", "aridez_P_ET0", "meses_umidos", "sazonalidade_walsh")}, flush=True)
    A = pd.DataFrame(linhas)
    A.to_csv(OUT / "assinaturas.csv", index=False)
    VARS = ["chuva_anual_mm", "sazonalidade_walsh", "meses_umidos", "aridez_P_ET0", "tmax_estacao_umida", "tmax_mes_mais_quente"]
    Z = (A[VARS] - A[VARS].mean()) / A[VARS].std()
    Z.index = A.ponto
    alvo = A[A.grupo == "Ceará (alvo)"].ponto.tolist()
    fonte = A[A.grupo != "Ceará (alvo)"].ponto.tolist()
    D = pd.DataFrame({c: [float(np.sqrt(((Z.loc[c] - Z.loc[f]) ** 2).sum())) for f in fonte] for c in alvo}, index=fonte).round(2)
    D.to_csv(OUT / "distancias.csv")
    print("\nPara cada ponto do Ceará, os 4 lugares de artigos com clima mais parecido (distância z; menor = mais parecido):")
    for c in alvo:
        top = D[c].sort_values().head(4)
        print(f"  {c:38s} → " + "; ".join(f"{k} ({v})" for k, v in top.items()))
    registrar_manifesto("analogos_artigos", {"fonte": "NASA POWER climatologia (API, comunidade AG)", "metodo": __doc__.strip()[:700],
                                             "variaveis": VARS, "n_sitios_artigos": len(fonte), "n_pontos_ceara": len(alvo)})


if __name__ == "__main__":
    main()
