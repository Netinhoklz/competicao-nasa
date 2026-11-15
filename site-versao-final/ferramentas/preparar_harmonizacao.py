"""Gera web/dados/harmonizacao.json para o módulo "Do satélite ao seu município" (web/js/extras/harmonizacao.js, ponto 7).

Lê:
  - E:/campeonato-nasa/dados/imerg/imerg_ne_diario_<ano>.nc (GPM IMERG V07 via NASA POWER, 0,1°), anos completos 1998–2025;
  - E:/campeonato-nasa/dados/ibge_nordeste/malha_ne_municipio.geojson (malha do IBGE que o motor usa);
  - E:/campeonato-nasa/dados/prototipo/smap_janela_30d.nc (grade do SMAP L4 que o motor usa no "solo hoje");
  - os MANIFESTO.json das bases, para os períodos da tabela.
Grava: site-versao-final/web/dados/harmonizacao.json (~150 KB).

O que sai, por município (a mesma regra de scripts/preparar_prototipo_nordeste.py, que gera o início e o regime da chuva):
  - as células de 0,1° do IMERG cujo CENTRO cai dentro do município, com a chuva média do ano (1998–2025) em cada uma;
    município sem nenhum centro dentro usa a célula mais próxima do ponto interno (representative_point, o mesmo do motor);
  - a mesma média pesada pela área de cada célula dentro do município, para conferir quanto a regra do centro muda o número.
E, uma vez só: a grade do SMAP (centros), a do POWER e a do GAEZ, e a tabela das bases (resolução, período, o que entra no site).

Uso: E:/campeonato-nasa/venv/Scripts/python.exe -I -X utf8 ferramentas/preparar_harmonizacao.py
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import shapely
import xarray as xr
from shapely.geometry import box

DADOS = Path("E:/campeonato-nasa/dados")
SITE = Path(__file__).resolve().parents[1]
SAIDA = SITE / "web" / "dados" / "harmonizacao.json"
ANOS = range(1998, 2026)  # anos completos (o IMERG via POWER vai até 14/09/2026)


def manifesto(base):
    try:
        return json.loads((DADOS / base / "MANIFESTO.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def municipios():
    g = gpd.read_file(DADOS / "ibge_nordeste" / "malha_ne_municipio.geojson")
    g["cod"] = g.codarea.astype(str)
    rp = g.geometry.representative_point()
    g["lat"], g["lon"] = rp.y, rp.x
    return g


def chuva_anual_por_celula():
    soma, n = None, 0
    for a in ANOS:
        p = xr.open_dataset(DADOS / "imerg" / f"imerg_ne_diario_{a}.nc").precip
        anual = p.sum("time", min_count=330).values  # mm no ano; célula com > 35 dias vazios fica vazia
        soma = anual if soma is None else soma + anual
        n += 1
        lat, lon = p.lat.values, p.lon.values
    return soma / n, lat, lon


def main():
    g = municipios()
    clim, lat, lon = chuva_anual_por_celula()
    lo, la = np.meshgrid(lon, lat)
    idx = np.full(lo.size, -1)
    for j, geom in enumerate(g.geometry):
        idx[shapely.contains_xy(geom, lo, la).ravel()] = j
    plano = clim.ravel()
    lat0, lon0, passo = float(lat[0]), float(lon[0]), 0.1
    m, dif, perto_n = {}, [], 0
    for j, r in enumerate(g.itertuples()):
        cel = list(np.where(idx == j)[0])
        perto = 0
        if not cel:
            cel = [int(np.argmin((la.ravel() - r.lat) ** 2 + (lo.ravel() - r.lon) ** 2))]
            perto, perto_n = 1, perto_n + 1
        ii, jj = np.unravel_index(cel, la.shape)
        vals = plano[cel]
        media_centro = float(np.nanmean(vals))
        # conferência: média pesada pela área de cada célula dentro do município (área em graus² × cos da latitude)
        x0, y0, x1, y1 = r.geometry.bounds
        i_a, i_b = int(np.floor((y0 - lat0) / passo + 0.5)) - 1, int(np.ceil((y1 - lat0) / passo + 0.5)) + 1
        j_a, j_b = int(np.floor((x0 - lon0) / passo + 0.5)) - 1, int(np.ceil((x1 - lon0) / passo + 0.5)) + 1
        geom = shapely.make_valid(r.geometry)
        pesos, vs = [], []
        for i in range(max(i_a, 0), min(i_b, len(lat) - 1) + 1):
            for k in range(max(j_a, 0), min(j_b, len(lon) - 1) + 1):
                v = clim[i, k]
                if np.isnan(v):
                    continue
                cx, cy = lon[k], lat[i]
                a = geom.intersection(box(cx - passo / 2, cy - passo / 2, cx + passo / 2, cy + passo / 2)).area
                if a > 0:
                    pesos.append(a * np.cos(np.radians(cy)))
                    vs.append(v)
        media_area = float(np.average(vs, weights=pesos)) if pesos else media_centro
        dif.append(abs(media_centro - media_area) / media_area * 100)
        i0, j0 = int(ii.min()), int(jj.min())
        lin = [i0, j0, perto, round(media_centro), round(media_area)]
        for a, b, v in zip(ii, jj, vals):
            lin += [int(a - i0), int(b - j0), None if np.isnan(v) else int(round(v / 10))]
        m[r.cod] = lin
    dif = np.array(dif)

    sm = xr.open_dataset(DADOS / "prototipo" / "smap_janela_30d.nc")
    slat, slon = sm.lat.values, sm.lon.values
    dlon = float(np.diff(slon).mean())
    assert np.allclose(np.diff(slon), dlon, atol=1e-4), "a grade do SMAP deveria ter passo fixo em longitude"

    mi, ms, mm, mg, mv = (manifesto(b) for b in ("imerg", "smap", "modis", "grace", "viirs"))
    l4 = ms.get("consolidado_l4", {})
    bases = [
        # id, base, grade nativa, período, como vira número do município, onde está ("tela" | "repo" | "fora"), por quê
        ["imerg", "GPM IMERG V07 (chuva)", "0,1° ≈ 11 km, diária",
         f"{mi.get('periodo_diario_NE', ['1998-01-01', '2026-09-14'])[0][:4]}–{mi.get('periodo_diario_NE', ['', '2026-09-14'])[1][:7]}",
         "Média das células com centro no município, dia a dia e mês a mês (sem centro dentro: a célula mais perto do centro)",
         "tela", "Chuva do ano, quando a chuva chega, El Niño no município, projeção"],
        ["smap", "NASA SMAP L4 (água no solo)", "9 km (EASE-Grid 2.0; aqui ~10 × 8 km, 81 km²), diária",
         f"{l4.get('inicio', '2015-03-31')[:7]}–{l4.get('fim', '2026-11-10')[:7]}",
         "A célula de 9 km mais perto do centro do município; média dos últimos 30 dias, comparada aos mesmos dias de cada ano",
         "tela", "O solo hoje (passo 1)"],
        ["power", "NASA POWER (clima)", "0,5° × 0,625° ≈ 55 × 69 km",
         "climatologia; Tmax/Tmin 2001–2024",
         "A célula que contém o centro do município",
         "tela", "Clima do município: calor, meses úmidos, aridez (base dos estudos parecidos)"],
        ["gaez", "FAO GAEZ v4 (aptidão)", "5′ ≈ 9 km", "clima 1981–2010",
         "A célula que contém o centro do município", "tela", "O que a terra aceita (cardápio)"],
        ["zarc", "ZARC 2026/27 (MAPA)", "já é por município", "safra 2026/27",
         "Tábua por município × tipo de solo × decêndio; o solo entra como classe, não como mapa",
         "tela", "Datas de plantio e risco"],
        ["ibge", "IBGE PAM e Censo Agro 2017", "já é por município", "PAM 1998–2025; Censo 2017",
         "Direto (é a grade comum)", "tela", "Colheita, renda, projeção e respostas padrão"],
        ["ndvi", "MODIS e VIIRS (verde da planta, NDVI)", "250 m a 1 km, a cada 16 dias ou mês",
         f"MODIS {mm.get('mod13a1_nordeste', {}).get('periodo', ['2000'])[0][:4]}–2026; VIIRS "
         f"{mv.get('consolidado_vnp13a3', {}).get('inicio', '2012')[:4]}–2026 (só CE)",
         "Média do município, relativa ao estado no mesmo ano", "repo",
         "Estudos no repositório; o VIIRS a 1 km só foi baixado para o Ceará"],
        ["grace", "GRACE/GRACE-FO (água guardada)", "≈ 300 km (mascons; grade de 0,25°)",
         f"{str(mg.get('periodo', '2002-04 a 2026-09'))[:7]}–{str(mg.get('periodo', '2026-09'))[-10:-3]}",
         "Só a região: um pixel cobre dezenas de municípios", "repo", "Contexto regional; média móvel de 3 meses"],
        ["gldas", "GLDAS 2.1/2.2 e ERA5", "0,25° ≈ 28 km", "GLDAS 2000–2026; ERA5 1979–2020",
         "Checagem da água no solo e da evaporação", "repo", "Conferência; não decide nada na tela"],
        ["landsat", "Landsat 8/9 e HLS", "30 m, a cada 8–16 dias", "2013–2026",
         "Só em 4 áreas de teste no Ceará", "repo",
         "Nuvem na estação das chuvas (visível em só 29–71% das datas de decisão) e volume grande para 1.794 municípios"],
        ["srtm", "NASADEM/SRTM (relevo)", "30 m", "2000 (fixo)", "Relevo do mapa (ladrilhos) e declive nos estudos", "tela",
         "Relevo do mapa; o declive por roçado fica para depois"],
        ["ecostress", "ECOSTRESS (calor da planta)", "70 m", "2018–hoje, em horários variados",
         "Não entra", "fora", "Passa em dias e horas irregulares (órbita da estação espacial) e pesa muito; ficou no roteiro"],
        ["gedi", "GEDI (altura da mata)", "pegadas de 25 m em trilhas", "2019–hoje, com pausa",
         "Não entra", "fora", "São tiros soltos, não uma grade, e medem a mata, não a roça"],
        ["solo", "Solo", "classes do ZARC", "safra 2026/27",
         "Textura (tipos 1–3: arenoso, médio, argiloso) e água disponível AD1–AD6 do ZARC; sua resposta escolhe a classe",
         "tela", "Mapa de solo (SoilGrids 250 m) não entra: só o temos em pontos de teste"],
    ]
    out = {
        "fonte": "GPM IMERG V07 via NASA POWER (0,1°), chuva média do ano 1998–2025; malha IBGE; grades nativas do SMAP L4, "
                 "NASA POWER e FAO GAEZ. Gerado por ferramentas/preparar_harmonizacao.py",
        "imerg": {"lat0": round(lat0, 2), "lon0": round(lon0, 2), "passo": passo, "anos": [ANOS[0], ANOS[-1]],
                  "formato": "m[cod] = [i0, j0, perto, mm_centro, mm_area, (di, dj, mm/10)...]: i = linha (lat0 + i·passo), j = coluna",
                  "conferencia": {"mediana_pct": round(float(np.median(dif)), 1), "p95_pct": round(float(np.percentile(dif, 95)), 1),
                                  "max_pct": round(float(dif.max()), 1), "n": int(len(dif)), "sem_centro": perto_n}},
        "smap": {"lat": [round(float(v), 4) for v in slat], "lon0": round(float(slon[0]), 5), "dlon": round(dlon, 6)},
        "power": {"dlat": 0.5, "dlon": 0.625},
        "gaez": {"x0": -180, "y0": 90, "passo": 1 / 12},
        "bases": [dict(zip(["id", "base", "grade", "periodo", "municipio", "onde", "porque"], b)) for b in bases],
        "m": m,
    }
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"gravado {SAIDA} ({SAIDA.stat().st_size / 1024:.0f} KB); {len(m)} municípios; {perto_n} sem centro de célula")
    print("diferença centro × área (%):", out["imerg"]["conferencia"])
    q = m.get("2311306")
    if q:
        v = [x * 10 for x in q[7::3] if x is not None]
        print("Quixadá:", len(v), "células; média centro", q[3], "área", q[4], "min", min(v), "max", max(v))


if __name__ == "__main__":
    main()
